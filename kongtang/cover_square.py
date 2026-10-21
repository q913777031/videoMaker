"""控糖革命单期方图封面（1080×1080）：系列标、两行大标题、本期主视觉、底部副标题。

用法：python3 -m kongtang.cover_square 01 [输出路径，默认 out/kongtang/epXX/cover_1080.png]
第 01 期主视觉为“尖峰 vs 平稳”两条血糖曲线；其他期用合集图里的代表插图放大。
"""

import sys
from pathlib import Path

import skia

from adler import core
from adler import kit as K
from engine import gfx

from . import build as B
from . import kit_tang as T
from .collage import illustration

S = 1080


def visual_01(c, ep):
    T.chart(c, 560, 680, 760, 380, [(lambda u: T.bump(u, 1.0, 0.2, 2.6, 0.18), T.SPIKE, 1, 10, "尖峰"),
                                     (lambda u: T.bump(u, 0.42, 0.32, 1.6), T.FLAT, 1, 10, "")])
    K.text(c, "平稳", 760, 660, 34, "serif_black", T.FLAT)
    for i, (x, y, r) in enumerate(((120, 560, 34), (80, 700, 24), (140, 820, 28), (1000, 470, 22))):
        T.hexa(c, x, y, r, T.GLU, 0.9, i * 25)


def main(no: int, out: Path):
    ep = B.load(f"{no:02d}")
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(S, S, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    c = surf.getCanvas()
    c.drawImageRect(core.bg_image(ep.accent), skia.Rect.MakeXYWH(0, 0, core.W, core.W), skia.Rect.MakeWH(S, S),
                    skia.SamplingOptions(skia.FilterMode.kLinear))
    K.rr(c, 72 + 60, 92, 120, 60, 30, ep.accent)
    K.text(c, f"{no:02d}", 72 + 60, 93, 38, "black", K.PAPER)
    K.text(c, ep.series, 72 + 140, 93, 36, "sans_medium", K.INK2, 1, "left")
    lines = ep.cover_title.split("|")
    widest = max(K.text_w(gfx.plain(ln), 84, "serif_black") for ln in lines)
    size = min(84.0, 84 * 940 / widest)
    for i, ln in enumerate(lines):
        gfx.draw_rich(c, ln, 72, 215 + i * size * 1.3, size, "serif_black", K.INK, ep.accent, 1.0, "left")
    if no == 1:
        visual_01(c, ep)
    elif no == 2:
        T.chart(c, 560, 680, 760, 380, [(lambda u: T.bump(u, 1.0, 0.2, 2.6, 0.18), T.SPIKE, 1, 10, "尖峰")],
                1, (0.0, 0.55))
        K.text(c, "正常起伏范围", 900, 840, 28, "sans_medium", T.FLAT, 1, "right")
    else:
        with K.paper(c, 1, 0.9):
            K.rr(c, 540, 690, 900, 500, 36, K.tint(ep.accent, 0.84))
        c.save()
        c.translate(530, 690)
        c.scale(3.2, 3.2)
        illustration(c, no, 0, 0, 220, 150)
        c.restore()
    K.seg(c, 72, 990, 200, 990, ep.accent, 6)
    K.text(c, f"{ep.cover_sub}　·　{ep.title}", 220, 990, 30, "sans_medium", K.INK2, 1, "left")
    out.parent.mkdir(parents=True, exist_ok=True)
    surf.makeImageSnapshot().save(str(out), skia.kPNG)
    print(out)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    main(n, Path(sys.argv[2]) if len(sys.argv) > 2 else B.OUT / f"ep{n:02d}" / "cover_1080.png")
