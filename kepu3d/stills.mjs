// 抽帧检查：只打包一次、只开一个浏览器，按帧号批量输出 PNG。
// 用法：node stills.mjs <props.json> <输出目录> <帧号,帧号,...> [组件 id]
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';

const [propsPath, outDir, frameList, comp = 'Kepu'] = process.argv.slice(2);
const inputProps = JSON.parse(fs.readFileSync(propsPath, 'utf8'));
const browserExecutable = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const chromiumOptions = {gl: 'swangle'};
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public')});
const composition = await selectComposition({serveUrl, id: comp, inputProps, browserExecutable, chromiumOptions});
fs.mkdirSync(outDir, {recursive: true});
for (const f of frameList.split(',').map(Number)) {
  const output = path.join(outDir, `f${String(f).padStart(5, '0')}.png`);
  await renderStill({composition, serveUrl, frame: f, output, inputProps, browserExecutable, chromiumOptions, imageFormat: 'png'});
  console.log(output);
}
