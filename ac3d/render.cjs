#!/usr/bin/env node
/* 逐帧渲染 web/index.html（three.js + DOM 字幕）为无声 MP4，或导出指定时刻的静帧。
 *
 * 用法：
 *   node ac3d/render.cjs --stills <目录> 0.5,17.2,40      导出静帧 PNG
 *   node ac3d/render.cjs --video <输出.mp4> [--workers 4]  完整渲染（H.264 / yuv420p / 30fps，无音轨）
 *   追加 --only 镜头名[,镜头名]  只构建这些镜头（其余为空场景），用于快速检查静帧
 *
 * 依赖：Playwright（使用本机 Chromium，软件 WebGL：SwiftShader）、带 libx264 的 FFmpeg。
 * 页面通过本地静态服务器加载（file:// 下浏览器禁止 ES 模块与 fetch）。
 */
const path = require('path');
const fs = require('fs');
const http = require('http');
const os = require('os');
const { spawn } = require('child_process');

let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const ROOT = path.resolve(__dirname, '..');
const FPS = 30;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.ttf': 'font/ttf',
  '.otf': 'font/otf', '.png': 'image/png' };

function serve() {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
      fs.createReadStream(p).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

let ONLY = '';

async function openPage(browser, port) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('pageerror', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('console', m.text()); });
  await page.goto(`http://127.0.0.1:${port}/ac3d/web/index.html?render=1${ONLY ? '&only=' + ONLY : ''}`);
  await page.waitForFunction(() => window.AC && (window.AC.ready || window.AC.error), null, { timeout: 120000 });
  const err = await page.evaluate(() => window.AC.error);
  if (err) throw new Error(err);
  return page;
}

async function grab(page, t) {
  await page.evaluate(x => window.AC.seek(x), t);
  return page.screenshot({ type: 'png', clip: { x: 0, y: 0, width: 1080, height: 1920 } });
}

async function renderRange(browser, port, from, to, outFile, label) {
  const page = await openPage(browser, port);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', String(FPS), outFile],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg exit ' + c)))));
  for (let f = from; f < to; f++) {
    const buf = await grab(page, f / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - from) % 120 === 0) process.stdout.write(`  [${label}] ${f - from}/${to - from}\n`);
  }
  ff.stdin.end();
  await done;
  await page.close();
}

async function main() {
  const args = process.argv.slice(2);
  const oi = args.indexOf('--only');
  if (oi >= 0) { ONLY = args[oi + 1]; args.splice(oi, 2); }
  const srv = await serve();
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
    '--ignore-gpu-blocklist', '--disable-gpu-vsync', '--font-render-hinting=none'] });
  try {
    if (args[0] === '--stills') {
      const dir = path.resolve(args[1]);
      fs.mkdirSync(dir, { recursive: true });
      const page = await openPage(browser, port);
      for (const s of args[2].split(',')) {
        const t = parseFloat(s);
        const buf = await grab(page, t);
        const f = path.join(dir, `f_${t.toFixed(2).padStart(6, '0')}.png`);
        fs.writeFileSync(f, buf);
        console.log(f);
      }
      return;
    }
    if (args[0] === '--video') {
      const out = path.resolve(args[1]);
      const wi = args.indexOf('--workers');
      const workers = wi > 0 ? parseInt(args[wi + 1], 10) : 4;
      const probe = await openPage(browser, port);
      const info = await probe.evaluate(() => window.AC.info());
      await probe.close();
      const total = Math.round(info.end * FPS);
      const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ac3d-'));
      const n = workers * 3;
      const segs = Array.from({ length: n }, (_, i) => [Math.floor(total * i / n), Math.floor(total * (i + 1) / n),
        path.join(tmp, `seg${String(i).padStart(2, '0')}.mp4`)]);
      let next = 0;
      const t0 = Date.now();
      await Promise.all(Array.from({ length: workers }, async () => {
        while (next < segs.length) {
          const [a, b, f] = segs[next++];
          await renderRange(browser, port, a, b, f, path.basename(f));
        }
      }));
      const list = path.join(tmp, 'list.txt');
      fs.writeFileSync(list, segs.map(s => `file '${s[2]}'`).join('\n'));
      await new Promise((res, rej) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list,
        '-c', 'copy', out], { stdio: 'inherit' }).on('close', c => (c === 0 ? res() : rej(new Error('concat ' + c)))));
      fs.rmSync(tmp, { recursive: true, force: true });
      console.log(`video ${out}: ${total} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      return;
    }
    console.error('usage: --stills <dir> <t,...> | --video <out.mp4> [--workers N]');
    process.exitCode = 2;
  } finally {
    await browser.close();
    srv.close();
  }
}

main().catch(e => { console.error(e); process.exit(1); });
