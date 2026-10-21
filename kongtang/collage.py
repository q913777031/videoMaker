"""控糖革命 12 讲合集图（1080×1080）：标题 + 4×3 宫格，每格一张该期的代表插图 + 期号、概念与标题。

用法：python3 -m kongtang.collage [输出路径，默认 out/kongtang/合集_1080.png]
"""

import sys
from pathlib import Path

import skia

from adler import core
from adler import kit as K

from . import build as B
from . import kit_tang as T
from .common import BOOK, DISCLAIMER, TITLES

S = 1080
ACC = "#D9773A"
COLS, ROWS = 4, 3
X0, Y0, GAP = 36, 236, 14
CW = (S - 2 * X0 - (COLS - 1) * GAP) / COLS
CH = 258
IMG_H = 150


def _curve(c, x, y, w, h, fn, color, width=6):
    path = skia.Path()
    for i in range(61):
        u = i / 60
        (path.moveTo if i == 0 else path.lineTo)(x - w / 2 + u * w, y + h / 2 - h * (0.12 + 0.8 * fn(u)))
    c.drawPath(path, K.paint(color, 1, width))


def illustration(c, no, x, y, w, h):
    """每期一张代表插图（以格子图片区中心为原点）。"""
    spike = (lambda u: T.bump(u, 1.0, 0.22, 2.6, 0.15))
    flat = (lambda u: T.bump(u, 0.45, 0.32, 1.6))
    if no == 1:
        for i, (dx, dy) in enumerate(((-60, 10), (0, -20), (60, 10), (-30, 45), (30, 45))):
            T.hexa(c, x + dx, y + dy, 26, T.GLU, 1, i * 20)
    elif no == 2:
        _curve(c, x, y + 8, w * 0.8, h * 0.8, spike, T.SPIKE, 7)
        K.arrow(c, (x - 38, y + 40), (x - 38, y - 42), T.SPIKE, 5, 1, 1, 0, 14)
    elif no == 3:
        for i, name in enumerate(("broccoli", "drumstick", "rice")):
            T.food(c, name, x - 66 + i * 66, y + 4, 54)
            K.dot(c, x - 66 + i * 66 - 22, y - 34, 12, K.INK)
            K.text(c, str(i + 1), x - 66 + i * 66 - 22, y - 33, 15, "black", K.PAPER)
    elif no == 4:
        T.food(c, "salad", x - 30, y + 6, 86)
        T.food(c, "broccoli", x + 52, y - 4, 64)
    elif no == 5:
        K.text(c, "kcal", x, y - 26, 44, "black", K.INK2)
        K.seg(c, x - 60, y - 2, x + 60, y - 2, K.RED, 6)
        T.food(c, "egg", x - 34, y + 36, 50)
        T.food(c, "broccoli", x + 34, y + 36, 46)
    elif no == 6:
        T.food(c, "egg", x - 34, y, 76)
        T.food(c, "cheese", x + 48, y + 12, 56)
    elif no == 7:
        T.food(c, "honey", x - 40, y, 74)
        T.food(c, "sugar", x + 46, y + 14, 60)
        K.text(c, "=", x + 4, y + 6, 40, "black", K.INK2)
    elif no == 8:
        T.food(c, "cake", x + 40, y + 6, 70)
        K.text(c, "饭后", x - 46, y + 2, 30, "serif_black", ACC)
    elif no == 9:
        T.food(c, "vinegar", x - 30, y + 4, 92)
        T.FOODS["juice"](c, x + 46, y + 10, 64, 1.0, "#EADFC4", 0.8)
    elif no == 10:
        K.figure(c, x, y + 64, 120, K.walk(0.6, 1.0), K.HERO, mood="smile", hair="short")
        _curve(c, x + 62, y - 20, 70, 50, flat, T.FLAT, 4)
    elif no == 11:
        T.food(c, "nuts", x - 40, y + 4, 66)
        T.food(c, "cheese", x + 44, y + 8, 60)
    elif no == 12:
        T.food(c, "bread", x - 46, y + 4, 62)
        K.text(c, "+", x + 2, y + 4, 34, "black", K.INK2)
        T.food(c, "egg", x + 50, y + 4, 62)


def main(out: Path):
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(S, S, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    c = surf.getCanvas()
    bg = core.bg_image(ACC)
    c.drawImageRect(bg, skia.Rect.MakeXYWH(0, 0, core.W, core.W), skia.Rect.MakeWH(S, S),
                    skia.SamplingOptions(skia.FilterMode.kLinear))
    K.text(c, "控糖革命", X0, 96, 78, "serif_black", K.INK, 1, "left")
    w = K.text_w("控糖革命", 78, "serif_black")
    K.rr(c, X0 + w + 92, 100, 140, 56, 28, ACC)
    K.text(c, "12 讲", X0 + w + 92, 101, 34, "black", K.PAPER)
    K.text(c, "血糖基础 + 书中 10 个控糖方法，每期 90 秒", X0, 172, 30, "sans_medium", K.INK2, 1, "left")
    for i in range(12):
        no = i + 1
        ep = B.load(f"{no:02d}")
        x = X0 + (i % COLS) * (CW + GAP)
        y = Y0 + (i // COLS) * (CH + GAP)
        cx, cy = x + CW / 2, y + CH / 2
        with K.paper(c, 1, 0.8):
            K.rr(c, cx, cy, CW, CH, 18, K.PAPER)
        dst = skia.Rect.MakeXYWH(x + 7, y + 7, CW - 14, IMG_H)
        K.rr(c, dst.centerX(), dst.centerY(), dst.width(), dst.height(), 12, K.tint(ep.accent, 0.86))
        illustration(c, no, dst.centerX() + 10, dst.centerY() + 6, dst.width(), dst.height())
        K.rr(c, x + 30, y + 30, 46, 30, 15, ep.accent)
        K.text(c, f"{no:02d}", x + 30, y + 31, 20, "black", K.PAPER)
        K.text(c, ep.concept, x + 14, y + IMG_H + 36, 30, "serif_black", ep.accent, 1, "left")
        head, tail = TITLES[no].split("，", 1)
        for j, ln in enumerate((head + "，", tail)):
            K.text(c, ln, x + 14, y + IMG_H + 70 + j * 26, 20, "sans_medium", K.INK2, 1, "left")
    K.text(c, f"依据：{BOOK.split('（')[0]}　·　{DISCLAIMER}", S / 2, S - 26, 17, "sans_medium", K.INK3)
    out.parent.mkdir(parents=True, exist_ok=True)
    surf.makeImageSnapshot().save(str(out), skia.kPNG)
    print(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else B.OUT / "合集_1080.png")
