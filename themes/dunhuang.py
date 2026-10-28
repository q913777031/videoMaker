"""敦煌壁画主题：赭黄土墙底（斑驳、裂纹、石青石绿的残色）、上下卷草边饰；元素套矿物色（降饱和偏暖）、赭褐描边、颜料剥落的斑点。"""

import numpy as np
import skia

from adler import core
from engine import gfx
from themes import layer as L

BROWN = "#5A2E1A"
MINERAL = L.matrix([(0.62, 0.3, 0.08, 0, 0.05), (0.18, 0.66, 0.12, 0, 0.03), (0.14, 0.26, 0.5, 0, 0.02), (0, 0, 0, 1, 0)])


def _filter():
    src = skia.ImageFilters.ColorFilter(MINERAL)
    return skia.ImageFilters.Merge([L.outline(BROWN, 2.5), src])


@L.cache_bg
def bg(accent):
    import cv2

    yy, xx = L.grid()
    W, H = core.W, core.H
    rng = np.random.default_rng(12)
    img = np.ones((H, W, 3), np.float32) * np.array(gfx.rgb("#D9B47E"), np.float32)
    low = cv2.resize(rng.normal(0, 1, (20, 12)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img += low[..., None] * np.array([14, 11, 8], np.float32)
    img += cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.5)[..., None] * 9
    for col, cx, cy, r in (("#4E8C82", 180, 1500, 260), ("#3E6E9E", 960, 300, 220), ("#A0473A", 900, 1700, 180)):
        m = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)) * (low > -0.2)
        img = img * (1 - 0.28 * m[..., None]) + np.array(gfx.rgb(col), np.float32) * 0.28 * m[..., None]
    crack = np.zeros((H, W), np.uint8)
    for _ in range(6):
        x, y = rng.integers(0, W), rng.integers(0, H)
        dx, dy = rng.normal(0, 1, 2)
        for _ in range(18):
            nx_, ny_ = x + dx * 30 + rng.integers(-12, 13), y + dy * 30 + rng.integers(-12, 13)
            cv2.line(crack, (int(x), int(y)), (int(nx_), int(ny_)), 255, 1)
            x, y = nx_, ny_
    img[cv2.GaussianBlur(crack, (0, 0), 0.8) > 60] *= 0.8
    for y0 in (40, H - 90):
        band = (yy > y0) & (yy < y0 + 50)
        img[band] = img[band] * 0.4 + np.array(gfx.rgb("#7A3B22"), np.float32) * 0.6
        sc = band & (np.hypot(np.mod(xx, 70) - 35, yy - y0 - 25) < 18) & (np.hypot(np.mod(xx, 70) - 35, yy - y0 - 25) > 11)
        img[sc] = np.array(gfx.rgb("#4E8C82"), np.float32)
    return img


def install():
    L.install(L.make_layer(_filter(), L.grain(21, 10, 45, 3.0), 0.5), bg, wash=L.flat_wash(BROWN))
