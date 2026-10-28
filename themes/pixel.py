"""像素风主题：浅米色纯色底；舞台内容按 8px 像素块降采样、8 级减色、放大保持硬边，带 1 像素块深色外描边；
页眉与字幕保持清晰；整帧叠一层淡扫描线。"""

import numpy as np
import skia

from adler import core
from themes import paper
from themes import post as P

BLOCK = 8
TOP, BOTTOM = 320, 1280
BG = np.array([244, 236, 222], np.float32)


def install():
    import cv2

    paper.install()

    def draw_frame(c, ep, T, caption=True, ui=True):
        rgb, a, g, s = P.render_layers(ep, T, False, False)
        out = np.ones((core.H, core.W, 3), np.float32) * BG
        out[(np.arange(core.H)[:, None] // BLOCK + np.arange(core.W)[None, :] // BLOCK) % 2 == 0] *= 0.985
        w, h = core.W // BLOCK, (BOTTOM - TOP) // BLOCK
        sa = cv2.resize(a[TOP:BOTTOM], (w, h), interpolation=cv2.INTER_AREA)
        sc = cv2.resize(rgb[TOP:BOTTOM] * a[TOP:BOTTOM, :, None], (w, h), interpolation=cv2.INTER_AREA)
        sc = sc / np.maximum(sa, 1e-3)[..., None]
        sc = np.round(sc / 255 * 7) / 7 * 255
        on = (sa > 0.45).astype(np.uint8)
        ring = cv2.dilate(on, np.ones((3, 3), np.uint8)) - on
        small = np.zeros((h, w, 3), np.float32)
        small[on > 0] = sc[on > 0]
        small[ring > 0] = np.array([40, 34, 52], np.float32)
        mask = ((on + ring) > 0).astype(np.float32)
        big = cv2.resize(small, (core.W, BOTTOM - TOP), interpolation=cv2.INTER_NEAREST)
        bm = cv2.resize(mask, (core.W, BOTTOM - TOP), interpolation=cv2.INTER_NEAREST)[..., None]
        out[TOP:BOTTOM] = out[TOP:BOTTOM] * (1 - bm) + big * bm
        out[::4] *= 0.95
        out += P.flash_level(s, g) * 120
        P.put(c, out)
        if caption:
            core.draw_caption(c, ep, s, g)
        if ui:
            core.draw_header(c, ep, s, T, g)
            core.draw_progress(c, ep, T)
        f = P.fade_level(T)
        if f > 0:
            c.drawPaint(skia.Paint(Color=skia.Color4f(0.96, 0.93, 0.87, f)))

    core.draw_frame = draw_frame
