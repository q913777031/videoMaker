import fs from "node:fs";
import { Config } from "@remotion/cli/config";

// 若环境中预装了 Chromium headless shell（如云端容器），直接使用，避免渲染时再下载浏览器；
// 也可用环境变量 REMOTION_BROWSER 指定。都不存在时由 Remotion 自行下载。
const shell = process.env.REMOTION_BROWSER ?? "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell";
if (fs.existsSync(shell)) {
  Config.setBrowserExecutable(shell);
}
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(92);
Config.setCodec("h264");
Config.setCrf(18);
Config.setPixelFormat("yuv420p");
