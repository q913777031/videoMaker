import { cancelRender, continueRender, delayRender, staticFile } from "remotion";

/** 中文字体：渲染前全部加载完成，避免缺字和布局跳变 */
export const FONT_BODY = "NotoSC, sans-serif";
export const FONT_FUN = "Smiley, NotoSC, sans-serif";

const FACES: [string, string, string][] = [
  ["NotoSC", "fonts/NotoSansCJKsc-Bold.otf", "700"],
  ["NotoSC", "fonts/NotoSansCJKsc-Black.otf", "900"],
  ["Smiley", "fonts/SmileySans-Oblique.ttf", "400"],
];

let started = false;
/** 在根组件挂载前调用一次；字体加载失败直接抛错，不静默回退到系统字体 */
export const loadFonts = () => {
  if (started || typeof document === "undefined") return;
  started = true;
  const handle = delayRender("load fonts");
  Promise.all(
    FACES.map(([family, file, weight]) => {
      const face = new FontFace(family, `url('${staticFile(file)}')`, { weight });
      return face.load().then((f) => document.fonts.add(f));
    }),
  )
    .then(() => continueRender(handle))
    .catch((err) => cancelRender(new Error(`font load failed: ${String(err)}`)));
};
