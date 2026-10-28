"""浮世绘版画主题：米黄和纸底、底部青海波纹与远方红日、顶部云带；元素平涂、靛蓝粗描边、套色略偏暖、木纹颗粒。"""

import numpy as np
import skia

from adler import core
from engine import gfx
from themes import layer as L

INDIGO = "#1F2E4A"
WARM = L.matrix([(0.86, 0.1, 0.04, 0, 0.03), (0.06, 0.84, 0.06, 0, 0.02), (0.04, 0.12, 0.74, 0, 0.0), (0, 0, 0, 1, 0)])


def _filter():
    src = skia.ImageFilters.ColorFilter(WARM)
    return skia.ImageFilters.Merge([L.outline(INDIGO, 3.0), src])


@L.cache_bg
def bg(accent):
    import cv2

    yy, xx = L.grid()
    W, H = core.W, core.H
    rng = np.random.default_rng(8)
    img = np.ones((H, W, 3), np.float32) * np.array(gfx.rgb("#EFE2C2"), np.float32)
    img += cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), sigmaX=8, sigmaY=1)[..., None] * 7
    # 远方红日
    sun = np.hypot(xx - 830, yy - 470) < 120
    img[sun] = img[sun] * 0.25 + np.array(gfx.rgb("#D2483A"), np.float32) * 0.75
    # 顶部云带
    band = (yy > 150) & (yy < 175) | (yy > 195) & (yy < 205)
    img[band] = img[band] * 0.7 + np.array(gfx.rgb("#C9A86A"), np.float32) * 0.3
    # 底部青海波
    blue = np.array(gfx.rgb("#2E5E8C"), np.float32)
    y0 = 1500
    r = 60
    ry = np.mod(yy - y0, r)
    row = np.floor((yy - y0) / r)
    cx = np.mod(xx + (row % 2) * r, 2 * r) - r
    d = np.hypot(cx, ry)
    arcs = (np.mod(d, 14) < 4) & (d < r) & (yy > y0)
    img[arcs] = img[arcs] * 0.35 + blue * 0.65
    deep = (yy > y0) & ~arcs
    img[deep] = img[deep] * 0.82 + blue * 0.18
    return img


def install():
    L.install(L.make_layer(_filter(), L.grain(11, 18, 10, 2.0), 0.35), bg, wash=L.flat_wash(INDIGO, 0.18))
