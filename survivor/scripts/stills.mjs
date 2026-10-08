// 批量导出关键帧预览：只打包一次，按“名称:帧号”逐张渲染
// 用法：node scripts/stills.mjs <输出目录> hook:45 setup:247 ...
import fs from "node:fs";
import path from "node:path";
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";

const [outDir, ...specs] = process.argv.slice(2);
const shell = process.env.REMOTION_BROWSER ?? "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell";
const browserExecutable = fs.existsSync(shell) ? shell : null;
fs.mkdirSync(outDir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
for (const spec of specs) {
  const [name, frame, compId = "SurvivorBias"] = spec.split(":");
  const composition = await selectComposition({ serveUrl, id: compId, browserExecutable });
  await renderStill({ composition, serveUrl, output: path.join(outDir, `${name}.png`), frame: Number(frame), browserExecutable });
  console.log(`${name} -> frame ${frame}`);
}
