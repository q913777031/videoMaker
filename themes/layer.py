"""图层类主题的共用构造：给每个元素图层套一个 ImageFilter（描边 / 调色 / 投影），可选颜料纹理，人物复用水墨骨架。"""

import functools
from contextlib import contextmanager

import numpy as np
import skia

from adler import core
from adler import kit as K
from engine import gfx
from engine.gfx import clamp01
from maoxuan import ink


def matrix(rows) -> skia.ColorFilter:
    return skia.ColorFilters.Matrix([v for r in rows for v in r])


def outline(color: str, r: float) -> skia.ImageFilter:
    rr, gg, bb = (v / 255 for v in gfx.rgb(color))
    m = matrix([(0, 0, 0, 0, rr), (0, 0, 0, 0, gg), (0, 0, 0, 0, bb), (0, 0, 0, 1, 0)])
    return skia.ImageFilters.ColorFilter(m, skia.ImageFilters.Dilate(r, r))


@functools.lru_cache(maxsize=8)
def grain(seed: int, dark: float, light: float, sigma: float = 6.0) -> skia.Image:
    """斑驳纹理（透明度编码），用 SrcATop 叠在元素上。"""
    import cv2

    rng = np.random.default_rng(seed)
    v = cv2.GaussianBlur(rng.normal(0, 1, (768, 768)).astype(np.float32), (0, 0), sigma)
    v = v / (v.std() + 1e-6) + 0.4 * rng.normal(0, 1, (768, 768)).astype(np.float32)
    a = np.clip(np.where(v > 0, v * dark, -v * light), 0, 160)
    lum = np.where(v > 0, 30, 245).astype(np.float32)
    rgba = np.dstack([lum, lum, lum, a]).astype(np.uint8)
    return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)


def make_layer(image_filter: skia.ImageFilter, tex: skia.Image | None = None, tex_alpha: float = 0.3,
               opacity: float = 1.0):
    @contextmanager
    def layer(c, alpha: float = 1.0, lift: float = 1.0, bounds: skia.Rect | None = None):
        if alpha <= 0:
            c.save()
            c.clipRect(skia.Rect.MakeWH(0, 0))
            try:
                yield
            finally:
                c.restore()
            return
        p = skia.Paint(Alphaf=clamp01(alpha) * opacity)
        p.setImageFilter(image_filter)
        c.saveLayer(bounds, p)
        try:
            yield
            if tex is not None:
                c.drawImageRect(tex, skia.Rect.MakeXYWH(-1300, -1300, 2600, 2600), skia.SamplingOptions(skia.FilterMode.kLinear),
                                skia.Paint(Alphaf=tex_alpha, BlendMode=skia.BlendMode.kSrcATop))
        finally:
            c.restore()

    return layer


def install(layer, bg, wash=None, head=None, font: str | None = "MaShanZheng-Regular.ttf"):
    """套用图层主题：元素图层、背景、人物上色与头部（可选）、大字字体。"""
    ink.install()
    ink.ink_layer = layer
    if wash:
        ink._wash = wash
    if head:
        ink._ink_head = head
    K.paper = layer
    K.figure = ink.ink_figure
    core.bg_image = bg
    if font:
        gfx.FONT_FILES["serif_black"] = font


def flat_wash(line_color: str, shade: float = 0.0):
    """平涂上色（可带一侧硬阴影）+ 指定颜色细描边。"""

    def wash(c, path, color, alpha=1.0, edge=0.3, line=0.0):
        c.drawPath(path, K.paint(color, alpha))
        if shade:
            b = path.getBounds()
            c.save()
            c.clipPath(path, doAntiAlias=True)
            c.drawRect(skia.Rect.MakeLTRB(b.centerX() + b.width() * 0.15, b.top(), b.right() + 4, b.bottom() + 4),
                       K.paint(K.shade(color, shade), alpha))
            c.restore()
        c.drawPath(path, K.paint(line_color, alpha, max(2.5, line)))

    return wash


def cache_bg(fn):
    store = {}

    def bg(accent):
        if accent not in store:
            img = np.clip(fn(accent), 0, 255).astype(np.uint8)
            rgba = np.dstack([img, np.full(img.shape[:2], 255, np.uint8)])
            store[accent] = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
        return store[accent]

    return bg


def grid():
    yy, xx = np.mgrid[0:core.H, 0:core.W].astype(np.float32)
    return yy, xx
