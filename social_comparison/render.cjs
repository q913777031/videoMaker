#!/usr/bin/env node
/* 逐帧导出 index.html 为无声 MP4（H.264 / yuv420p / 30fps / 无音频轨）。
 *
 * 用法：
 *   node render.cjs out.mp4                 完整 90 秒，4 进程并行
 *   node render.cjs --stills dir 0,3.9,...  只导出若干时间点的 PNG，用于检查画面
 *   node render.cjs --audit                 打印阅读时长、字数与安全区校验
 *
 * 依赖：Playwright（使用已安装的 Chromium）、带 libx264 的 FFmpeg。
 */
const path = require('path');
const fs = require('fs');
const { spawn, execFileSync } = require('child_process');

let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const PAGE = 'file://' + path.join(__dirname, 'index.html') + '?render=1';
const FPS = 30, DUR = 90, TOTAL = FPS * DUR;

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1200, height: 2100 } });
  await page.goto(PAGE);
  await page.waitForFunction(() => window.SCV && document.fonts.status === 'loaded');
  return page;
}

async function renderRange(browser, from, to, outFile) {
  const page = await openPage(browser);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-tune', 'animation', '-g', '60',
    '-pix_fmt', 'yuv420p', '-r', String(FPS), outFile], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  for (let f = from; f < to; f++) {
    const url = await page.evaluate(i => window.SCV.frame(i), f);
    const buf = Buffer.from(url.slice(url.indexOf(',') + 1), 'base64');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - from) % 150 === 0) process.stdout.write(`  [${path.basename(outFile)}] ${f}/${to}\n`);
  }
  ff.stdin.end();
  await done;
  await page.close();
}

async function main() {
  const args = process.argv.slice(2);
  const browser = await chromium.launch();
  try {
    if (args[0] === '--audit') {
      const page = await openPage(browser);
      console.log(JSON.stringify(await page.evaluate(() => window.SCV.audit()), null, 1));
      return;
    }
    if (args[0] === '--stills') {
      const dir = args[1]; fs.mkdirSync(dir, { recursive: true });
      const page = await openPage(browser);
      for (const s of args[2].split(',')) {
        const t = parseFloat(s);
        const url = await page.evaluate(f => window.SCV.frame(f), Math.round(t * FPS));
        fs.writeFileSync(path.join(dir, `t${t.toFixed(2).padStart(5, '0')}.png`), Buffer.from(url.split(',')[1], 'base64'));
      }
      return;
    }
    const out = path.resolve(args[0] || 'social_comparison.mp4');
    const workers = 4, tmp = out + '.parts';
    fs.mkdirSync(tmp, { recursive: true });
    const per = Math.ceil(TOTAL / workers), parts = [];
    const jobs = [];
    for (let w = 0; w < workers; w++) {
      const from = w * per, to = Math.min(TOTAL, from + per), file = path.join(tmp, `part${w}.mp4`);
      parts.push(file); jobs.push(renderRange(browser, from, to, file));
    }
    await Promise.all(jobs);
    const list = path.join(tmp, 'list.txt');
    fs.writeFileSync(list, parts.map(p => `file '${p}'`).join('\n'));
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-an', '-c', 'copy', '-movflags', '+faststart', out], { stdio: 'inherit' });
    fs.rmSync(tmp, { recursive: true, force: true });
    console.log('done:', out);
  } finally { await browser.close(); }
}
main().catch(e => { console.error(e); process.exit(1); });
