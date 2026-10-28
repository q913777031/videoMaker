"""整帧后期类主题的共用工具：在透明底上画出整帧（不含闪白与首尾淡入淡出），交给主题逐像素处理，再补上闪白与淡入淡出。"""

import math

import numpy as np
import skia

from adler import core
from adler import fx

_CLEAR = {}


def _clear():
    if "img" not in _CLEAR:
        _CLEAR["img"] = skia.Image.fromarray(np.zeros((core.H, core.W, 4), np.uint8), colorType=skia.kRGBA_8888_ColorType)
    return _CLEAR["img"]


def render_layers(ep, T, caption=True, ui=True):
    """返回（去预乘 RGB float32，alpha 0–1，镜头 G，镜头 Shot）。"""
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    c = surf.getCanvas()
    k = ep.shot_at(T)
    s = ep.shots[k]
    saved = core.bg_image
    core.bg_image = lambda accent: _clear()
    try:
        g = core._draw_shot(c, ep, k, T - s.t0)
        if caption:
            core.draw_caption(c, ep, s, g)
        if ui:
            core.draw_header(c, ep, s, T, g)
            core.draw_progress(c, ep, T)
    finally:
        core.bg_image = saved
    arr = surf.makeImageSnapshot().toarray().astype(np.float32)
    a = arr[..., 3] / 255.0
    return arr[..., :3] / np.maximum(a, 1e-3)[..., None], a, g, s


def flash_level(s, g) -> float:
    fl = 0.0
    for it in s.flashes:
        kb, pk = it if isinstance(it, tuple) else (it, 0.55)
        fl = max(fl, fx.flash_alpha(g.since(kb), pk))
    return fl


def hit_level(s, T) -> float:
    """最近一个重拍（镜头 shake 拍）后的冲击强度 0–1。"""
    v = 0.0
    for it in s.shake:
        kb = it[0] if isinstance(it, tuple) else it
        dt = T - core.bt(s.b0 + kb)
        if 0 <= dt < 0.6:
            v = max(v, math.exp(-dt * 8))
    return v


def fade_level(T) -> float:
    return max(1 - min(1.0, T / 0.4), min(1.0, max(0.0, (T - (core.END - 1.2)) / 1.1)))


def put(c, rgb):
    rgba = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), np.full((core.H, core.W), 255, np.uint8)])
    c.drawImage(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType), 0, 0)
