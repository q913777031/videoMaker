"""封面（1080×1920）：宣纸远山、逐笔书法大标题、朱砂印、竹下静坐的人影。"""

import numpy as np
import skia

from engine import gfx

from . import art, hanzi, ink


def cover(lines: tuple[str, str], seal: str, ep_label: str) -> np.ndarray:
    """lines = (上行大字, 下行朱砂大字)；返回 RGBA 数组。缺笔画数据的字会抛 KeyError。"""
    hanzi.prepare("".join(lines))
    arr = np.zeros((gfx.H, gfx.W, 4), np.uint8)
    surf = skia.Surface(arr)
    c = surf.getCanvas()
    ink.draw_paper(c)
    ink.mountains(c, 980, 420, 3, alpha=0.3, blur=6, shift=120)
    ink.mist(c, 2.0, 1260, 0.55, seed=1)
    ink.mountains(c, 1140, 440, 5, alpha=0.5, shift=60)
    ink.mist(c, 5.0, 1420, 0.5, seed=2)
    for k in range(6):
        art.bamboo(c, 760 + k * 52 + (k % 2) * 14, 1640 + (k % 3) * 10, 620 - (k % 3) * 70, 6 + k, 1.0,
                   0.85 * (0.6 + 0.4 * (k % 2)), width=18 + (k % 2) * 6)
    art.scholar_seated(c, 400, 1640, 1.0, 0.9)
    ink.lamp(c, 590, 1600, 0.6, 0.9)
    ink.label(c, "传习录", 540, 230, 64, tone=ink.CINNABAR)
    ink.label(c, ep_label, 540, 310, 38, tone=ink.OCHRE, name="serif_medium")
    top, bottom = lines
    size = min(200, 900 / max(1, len(top)))
    hanzi.write(c, top, 540, 560, size, 1.0)
    size2 = min(210, 900 / max(1, len(bottom)))
    hanzi.write(c, bottom, 540, 820, size2, 1.0, color=ink.CINNABAR)
    ink.seal(c, seal, 900, 1010, 170, 1.0)
    return arr
