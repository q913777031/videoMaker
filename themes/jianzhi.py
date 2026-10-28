"""红纸剪窗花主题：米金色宣纸底、四角窗花纹样；所有元素都变成深浅两层红纸（按明暗映射）、带镂空花点与纸张投影。"""

import math

import numpy as np
import skia

from adler import core
from engine import gfx
from themes import layer as L
from themes.piying import _wash as cut_wash

RED_MAP = L.matrix([(0.093, 0.183, 0.034, 0, 0.64), (0.189, 0.372, 0.069, 0, 0.09), (0.162, 0.319, 0.059, 0, 0.12),
                    (0, 0, 0, 1, 0)])


def _filter():
    red = skia.ImageFilters.ColorFilter(RED_MAP)
    shadow = skia.ImageFilters.DropShadow(5, 7, 3, 3, skia.Color4f(0.35, 0.1, 0.05, 0.35).toColor(), red)
    return shadow


@L.cache_bg
def bg(accent):
    import cv2

    yy, xx = L.grid()
    W, H = core.W, core.H
    img = np.ones((H, W, 3), np.float32) * np.array(gfx.rgb("#F6E7C8"), np.float32)
    rng = np.random.default_rng(4)
    img += cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 2)[..., None] * 5
    red = np.array(gfx.rgb("#C8323A"), np.float32)
    for cx, cy in ((0, H), (W, H)):
        r = np.hypot(xx - cx, yy - cy)
        ang = np.arctan2(yy - cy, xx - cx)
        petal = (np.abs(np.sin(ang * 6)) * 60 + 220 > r) & (r > 60)
        ring = (np.abs(r - 300) < 10) | (np.abs(r - 330) < 4)
        holes = (np.sin(r / 9) > 0.6) & (np.sin(ang * 24) > 0.5) & (r < 260)
        mask = (petal & ~holes) | ring
        img[mask] = img[mask] * 0.3 + red * 0.7
    return img


def install():
    """元件按剪纸图层绘制；整帧再把舞台区所有内容（含大字、弹字）映射成红纸色，页眉与字幕保持墨色清晰。"""
    import cv2

    from themes import post as P

    L.install(L.make_layer(_filter()), bg, wash=cut_wash)

    def draw_frame(c, ep, T, caption=True, ui=True):
        rgb, a, g, s = P.render_layers(ep, T, False, False)
        lum = (rgb * np.array([0.3, 0.59, 0.11], np.float32)).sum(-1, keepdims=True) / 255
        red = np.concatenate([0.64 + 0.31 * lum, 0.09 + 0.63 * lum, 0.12 + 0.54 * lum], -1) * 255
        base = np.array(bg(ep.accent).toarray()[..., :3], np.float32)
        sh = cv2.GaussianBlur(np.roll(np.roll(a, 7, 0), 5, 1), (0, 0), 3)[..., None] * 0.3
        out = base * (1 - sh) + base * 0.55 * sh
        out = out * (1 - a[..., None]) + red * a[..., None]
        out += P.flash_level(s, g) * 90
        P.put(c, out)
        if caption:
            core.draw_caption(c, ep, s, g)
        if ui:
            core.draw_header(c, ep, s, T, g)
            core.draw_progress(c, ep, T)
        f = P.fade_level(T)
        if f > 0:
            c.drawPaint(skia.Paint(Color=skia.Color4f(0.96, 0.9, 0.78, f)))

    core.draw_frame = draw_frame
