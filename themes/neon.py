"""霓虹赛博主题：近黑紫底 + 透视网格地面；所有元素只留发光的霓虹轮廓（内部淡填充），墨色变青、浅色变暗紫；
扫描线；切镜开头与重拍时 RGB 错位 + 横向撕裂（故障效果）。"""

import functools
import math

import numpy as np

from adler import core
from maoxuan import ink
from themes import post as P

CYAN = np.array([90, 240, 255], np.float32)
PINK = np.array([255, 70, 200], np.float32)


@functools.lru_cache(maxsize=1)
def _bg() -> np.ndarray:
    import cv2

    W, H = core.W, core.H
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.array([12, 6, 24], np.float32) + (yy / H)[..., None] * np.array([20, 4, 30], np.float32)
    hz = 1290.0
    grid = np.zeros((H, W), np.float32)
    below = yy > hz
    depth = np.maximum(yy - hz, 1)
    z = 4000 / depth
    grid[below] = ((np.mod(z[below], 18) < 1.2).astype(np.float32) +
                   (np.mod((xx[below] - W / 2) / depth[below] * 60, 40) < 1.5).astype(np.float32))
    grid = np.clip(grid, 0, 1) * np.clip((yy - hz) / 500, 0, 1)
    glow = cv2.GaussianBlur(grid, (0, 0), 3)
    img += (grid[..., None] * 0.8 + glow[..., None] * 1.5) * PINK * 0.5
    sun = np.exp(-(((xx - W / 2) / 260) ** 2 + ((yy - hz) / 60) ** 2))
    img += sun[..., None] * np.array([255, 90, 160], np.float32) * 0.6
    return img


def _process(rgb, a):
    import cv2

    mx = rgb.max(-1, keepdims=True)
    mn = rgb.min(-1, keepdims=True)
    sat = (mx - mn) / np.maximum(mx, 1)
    v = mx / 255.0
    col = rgb / np.maximum(mx, 1) * 255
    gray = CYAN * (1 - v) + np.array([60, 40, 110], np.float32) * v
    k = np.clip((sat - 0.12) / 0.2, 0, 1)
    neon = col * k + gray * (1 - k)
    edge = cv2.morphologyEx(a, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    lum = rgb.mean(-1) / 255.0 * a
    edge = np.maximum(edge, cv2.morphologyEx(lum, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) * 1.5)
    edge = np.clip(edge, 0, 1)[..., None]
    dark_ink = (a * (1 - v[..., 0]) * (1 - k[..., 0]))[..., None]
    fill = a[..., None] * 0.22 + dark_ink * 0.85
    core_ = neon * np.clip(fill + edge, 0, 1)
    glow = cv2.GaussianBlur(core_, (0, 0), 8) * 1.3
    return core_, glow


def install():
    ink.install()

    def draw_frame(c, ep, T, caption=True, ui=True):
        rgb, a, g, s = P.render_layers(ep, T, caption, ui)
        core_, glow = _process(rgb, a)
        out = _bg() + glow + core_
        out[::3] *= 0.86
        t = T - s.t0
        gl = max(math.exp(-t * 14) if ep.shots.index(s) > 0 else 0.0, P.hit_level(s, T))
        if gl > 0.05:
            sh = int(14 * gl)
            out[..., 0] = np.roll(out[..., 0], sh, axis=1)
            out[..., 2] = np.roll(out[..., 2], -sh, axis=1)
            rng = np.random.default_rng(int(T * 30))
            for _ in range(int(6 * gl) + 1):
                y0 = int(rng.integers(320, 1280))
                h = int(rng.integers(8, 40))
                out[y0:y0 + h] = np.roll(out[y0:y0 + h], int(rng.integers(-60, 60) * gl), axis=1)
        out += P.flash_level(s, g) * np.array([200, 120, 255], np.float32) * 0.5
        out *= 1 - P.fade_level(T)
        P.put(c, out)

    core.draw_frame = draw_frame
