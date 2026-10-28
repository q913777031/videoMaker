"""皮影戏主题：烛光透亮的幕布底、元素像半透明彩色皮件（镂空花纹、深色描边、贴幕的柔影）、侧身皮影人物带关节铆钉与操纵杆。

install() 只替换当前进程的 kit.paper / kit.figure / core.bg_image / core.draw_frame 与毛笔字体；人物骨架复用水墨人物（maoxuan.ink）。
"""

import functools
import math
from contextlib import contextmanager

import numpy as np
import skia

from adler import core
from adler import kit as K
from engine import gfx
from engine.gfx import clamp01
from maoxuan import ink

LEATHER = "#E9C893"
OUTLINE = "#3A1E10"
ROD = "#2B1A10"


@functools.lru_cache(maxsize=4)
def _filter() -> skia.ImageFilter:
    return skia.ImageFilters.DropShadow(10, 14, 7, 7, skia.Color4f(0.16, 0.06, 0.02, 0.45).toColor())


@contextmanager
def leather_layer(c, alpha: float = 1.0, lift: float = 1.0, bounds: skia.Rect | None = None):
    """皮件图层：整体略透光（alpha 0.9），贴在幕布上的柔和暖色影子。"""
    if alpha <= 0:
        c.save()
        c.clipRect(skia.Rect.MakeWH(0, 0))
        try:
            yield
        finally:
            c.restore()
        return
    p = skia.Paint(Alphaf=clamp01(alpha) * 0.93)
    p.setImageFilter(_filter())
    c.saveLayer(bounds, p)
    try:
        yield
    finally:
        c.restore()


def _wash(c, path, color, alpha=1.0, edge=0.3, line=0.0):
    """皮件上色：饱和的透光色块 + 镂空花点 + 深色刻线描边。"""
    c.drawPath(path, K.paint(color, 0.95 * alpha))
    b = path.getBounds()
    if b.width() > 26 and b.height() > 26:
        c.save()
        c.clipPath(path, doAntiAlias=True)
        hole = skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kClear)
        step = 16.0
        y = b.top() + step
        row = 0
        while y < b.bottom() - 6:
            x = b.left() + step * (0.5 if row % 2 else 1.0)
            while x < b.right() - 6:
                c.drawCircle(x, y, 2.6, hole)
                x += step
            y += step
            row += 1
        c.restore()
    c.drawPath(path, K.paint(OUTLINE, 0.9 * alpha, max(2.5, line * 1.3)))


def _head(c, x, y, r, skin, face, mood, spec, hair_color, tilt, look, blink):
    """侧脸皮影头：额—鼻—唇—下巴一笔轮廓，细长凤眼与一道长眉；帽饰沿用角色发式。"""
    with K.at(c, x, y, tilt * 0.3 * face):
        p = skia.Path()
        f = face
        p.moveTo(-0.9 * r * f, -0.2 * r)
        p.cubicTo(-0.9 * r * f, -1.05 * r, 0.55 * r * f, -1.1 * r, 0.75 * r * f, -0.35 * r)
        p.lineTo(1.08 * r * f, 0.1 * r)
        p.lineTo(0.78 * r * f, 0.22 * r)
        p.lineTo(0.86 * r * f, 0.42 * r)
        p.lineTo(0.72 * r * f, 0.55 * r)
        p.quadTo(0.6 * r * f, 0.95 * r, 0.05 * r * f, 0.9 * r)
        p.quadTo(-0.75 * r * f, 0.8 * r, -0.9 * r * f, -0.2 * r)
        p.close()
        c.drawPath(p, K.paint(LEATHER, 0.96))
        c.drawPath(p, K.paint(OUTLINE, 0.95, r * 0.07))
        ey = -0.08 * r - look * 0.08 * r
        eye = skia.Path()
        eye.moveTo(0.18 * r * f, ey)
        eye.quadTo(0.42 * r * f, ey - 0.14 * r, 0.62 * r * f, ey + 0.02 * r)
        eye.quadTo(0.42 * r * f, ey + 0.06 * r, 0.18 * r * f, ey)
        c.drawPath(eye, K.paint(OUTLINE))
        K.seg(c, 0.1 * r * f, ey - 0.26 * r, 0.7 * r * f, ey - 0.3 * r + (0.08 * r if mood in ("angry",) else 0),
              OUTLINE, r * 0.07)
        mouth = {"smile": 0.06, "happy": 0.08, "sad": -0.06, "worried": -0.04}.get(mood, 0.0) * r
        K.seg(c, 0.55 * r * f, 0.5 * r, 0.75 * r * f, 0.5 * r - mouth, "#8A1E14", r * 0.06)
        c.drawCircle(0.2 * r * f, 0.3 * r, 0.16 * r, K.paint("#C8442E", 0.35))
        ink._hair(c, r, face, spec["hair"], hair_color or OUTLINE)


def piying_figure(c, x, y, s, p="stand", color=K.HERO, head_color=LEATHER, alpha=1.0, face: int = 1, mood="calm",
                  hair=None, hair_color=None, bob: float = 0.0, lift: float = 1.0, look: float = 0.0, blink: bool = False,
                  scarf=None, prop=None, role=None):
    """皮影人物：水墨人物骨架 + 皮件上色与侧脸头；近手与躯干各连一根操纵杆伸出画面下方。"""
    if alpha <= 0 or s <= 0:
        return

    def rod_prop(cc, h):
        _draw_rod(cc, h[0], h[1], h[0] + 30)
        K.dot(cc, h[0], h[1], 6, "#C9A24A")
        if prop:
            prop(cc, h)

    with K.at(c, x, y):
        with leather_layer(c, alpha, lift, skia.Rect.MakeLTRB(-s, -s * 1.4, s, 760)):
            _draw_rod(c, 0, -0.62 * s, -24)
    ink.ink_figure(c, x, y, s, p, color, LEATHER, alpha, face, mood, hair, hair_color, bob, lift, look, blink,
                   scarf, rod_prop, role)


def _draw_rod(c, x0, y0, x1, y_end=230.0):
    """操纵杆：从关节伸到脚下方，末段渐隐（不穿过字幕区）。"""
    pts = 12
    for i in range(pts):
        a, b = i / pts, (i + 1) / pts
        ya, yb = y0 + (y_end - y0) * a, y0 + (y_end - y0) * b
        fade = 1.0 if yb < 40 else max(0.0, 1 - (yb - 40) / (y_end - 40))
        c.drawPath(_rod(x0 + (x1 - x0) * a, ya, x0 + (x1 - x0) * b, yb), K.paint(ROD, 0.9 * fade, 4))


def _rod(x0, y0, x1, y1):
    p = skia.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y1)
    return p


_BG: dict = {}


def bg_image(accent: str) -> skia.Image:
    """幕布：中心烛光暖黄、四周渐暗的赭红；细密布纹；上下两条木框。"""
    if accent in _BG:
        return _BG[accent]
    import cv2

    W, H = core.W, core.H
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W / 2) / (W * 0.62), (yy - H * 0.45) / (H * 0.5))
    k = np.clip(r, 0, 1.4)[..., None]
    c0 = np.array(gfx.rgb("#FBE3B0"), np.float32)
    c1 = np.array(gfx.rgb("#D98B45"), np.float32)
    c2 = np.array(gfx.rgb("#6E2A14"), np.float32)
    img = np.where(k < 0.8, c0 + (c1 - c0) * (k / 0.8), c1 + (c2 - c1) * np.clip((k - 0.8) / 0.6, 0, 1))
    rng = np.random.default_rng(3)
    weave = (np.sin(xx * 1.9) * np.sin(yy * 1.9)) * 3.0
    img += weave[..., None] + rng.normal(0, 2.0, (H, W, 1)).astype(np.float32)
    fib = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 3) * 6
    img += fib[..., None]
    for y0, y1 in ((0, 60), (H - 60, H)):
        img[y0:y1] = np.array(gfx.rgb("#4A2412"), np.float32) + rng.normal(0, 6, (y1 - y0, W, 1)).astype(np.float32)
    rgba = np.dstack([np.clip(img, 0, 255).astype(np.uint8), np.full((H, W), 255, np.uint8)])
    _BG[accent] = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    return _BG[accent]


def install():
    """切换为皮影戏风（只影响当前进程）。"""
    ink.install()
    ink._wash = _wash
    ink._ink_head = _head
    ink.ink_layer = leather_layer
    K.paper = leather_layer
    K.figure = piying_figure
    core.bg_image = bg_image
    orig = core.draw_frame

    def draw_frame(c, ep, T, caption=True, ui=True):
        orig(c, ep, T, caption, ui)
        flick = 0.06 * (math.sin(T * 13.0) * 0.6 + math.sin(T * 7.3 + 1) * 0.4)
        if flick > 0:
            c.drawPaint(K.paint("#FFE2A0", flick))
        else:
            c.drawPaint(K.paint("#3A1408", -flick))

    core.draw_frame = draw_frame
