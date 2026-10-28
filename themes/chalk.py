"""黑板粉笔主题：墨绿黑板底（擦痕、粉尘）、上下木框；所有元素变成粉笔画——墨色变粉笔白、彩色变粉彩，
笔画带粉笔的干涩颗粒，浅色色块只留淡淡一层。字幕与页眉同样是粉笔字。"""

import functools

import numpy as np

from adler import core
from maoxuan import ink
from themes import post as P


@functools.lru_cache(maxsize=1)
def _bg() -> np.ndarray:
    import cv2

    W, H = core.W, core.H
    rng = np.random.default_rng(31)
    img = np.ones((H, W, 3), np.float32) * np.array([38, 62, 50], np.float32)
    low = cv2.resize(rng.normal(0, 1, (16, 9)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img += low[..., None] * np.array([6, 8, 7], np.float32)
    smear = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), sigmaX=40, sigmaY=6)
    img += np.clip(smear, 0, None)[..., None] * 60
    img += rng.normal(0, 3, (H, W, 1)).astype(np.float32)
    wood = np.array([120, 82, 50], np.float32)
    img[:34] = wood + rng.normal(0, 8, (34, W, 1)).astype(np.float32)
    img[-34:] = wood + rng.normal(0, 8, (34, W, 1)).astype(np.float32)
    return img


@functools.lru_cache(maxsize=1)
def _grain() -> np.ndarray:
    import cv2

    rng = np.random.default_rng(5)
    g = rng.random((core.H, core.W)).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 0.7)
    streak = cv2.GaussianBlur(rng.normal(0, 1, (core.H, core.W)).astype(np.float32), (0, 0), sigmaX=6, sigmaY=0.6)
    return np.clip(0.62 + g * 0.5 + streak * 0.2, 0.3, 1.0)


def _process(rgb, a):
    import cv2

    mx = rgb.max(-1, keepdims=True)
    mn = rgb.min(-1, keepdims=True)
    sat = (mx - mn) / np.maximum(mx, 1)
    v = mx / 255.0
    k = np.clip((sat - 0.12) / 0.2, 0, 1)
    pastel = rgb / np.maximum(mx, 1) * 255 * 0.55 + 255 * 0.45
    white = np.array([242, 242, 232], np.float32)
    col = pastel * k + white * (1 - k)
    strength = np.where(k > 0.5, 0.85, np.clip(1.25 - v * 1.1, 0.15, 1.0))
    edge = cv2.morphologyEx(a, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))[..., None]
    m = np.clip(a[..., None] * strength + edge * 0.9, 0, 1) * _grain()[..., None]
    return col, m


def install():
    ink.install()

    def draw_frame(c, ep, T, caption=True, ui=True):
        rgb, a, g, s = P.render_layers(ep, T, caption, ui)
        col, m = _process(rgb, a)
        out = _bg() * (1 - m) + col * m
        out += P.flash_level(s, g) * 120
        out *= 1 - P.fade_level(T)
        P.put(c, out)

    core.draw_frame = draw_frame
