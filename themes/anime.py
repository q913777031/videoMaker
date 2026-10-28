"""日漫赛璐珞主题：粉彩天空底 + 网点、元素统一黑色描边与平涂、大眼睛人物、切镜集中线与重拍冲击帧、斜体粗标题字。

install() 只替换当前进程的绘制函数；人物骨架复用水墨人物（maoxuan.ink），换掉上色、头部与图层效果。
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

LINE = "#1E1A22"
HAIR = {"worker": "#2E2630", "worker_f": "#6B3A2A", "boss": "#3A3A44"}


@functools.lru_cache(maxsize=4)
def _filter(r: float) -> skia.ImageFilter:
    black = skia.ColorFilters.Matrix([0, 0, 0, 0, 0.118, 0, 0, 0, 0, 0.1, 0, 0, 0, 0, 0.133, 0, 0, 0, 1, 0])
    outline = skia.ImageFilters.ColorFilter(black, skia.ImageFilters.Dilate(r, r))
    return skia.ImageFilters.Merge([outline, skia.ImageFilters.Offset(0, 0)])


@contextmanager
def cel_layer(c, alpha: float = 1.0, lift: float = 1.0, bounds: skia.Rect | None = None):
    """赛璐珞图层：整体外描一圈黑边，不要投影。"""
    if alpha <= 0:
        c.save()
        c.clipRect(skia.Rect.MakeWH(0, 0))
        try:
            yield
        finally:
            c.restore()
        return
    p = skia.Paint(Alphaf=clamp01(alpha))
    p.setImageFilter(_filter(3.5))
    c.saveLayer(bounds, p)
    try:
        yield
    finally:
        c.restore()


def _wash(c, path, color, alpha=1.0, edge=0.3, line=0.0):
    """平涂 + 一侧硬阴影（赛璐珞两色）+ 细描边。"""
    c.drawPath(path, K.paint(K.tint(color, 0.08), alpha))
    b = path.getBounds()
    c.save()
    c.clipPath(path, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(b.centerX() + b.width() * 0.12, b.top(), b.right() + 4, b.bottom() + 4),
               K.paint(K.shade(color, 0.22), alpha))
    c.restore()
    c.drawPath(path, K.paint(LINE, alpha, max(2.5, line)))


def _head(c, x, y, r, skin, face, mood, spec, hair_color, tilt, look, blink):
    """日漫头：尖下巴脸、大眼（高光两点）、刺状刘海；帽饰类角色沿用原发式。"""
    r *= 1.55
    f = face
    style = spec["hair"]
    hc = hair_color or HAIR.get("worker_f" if style in ("long", "bun_modern") else "worker")
    with K.at(c, x, y - r * 0.38, tilt * 0.3 * f):
        if style in ("long", "bun_modern"):
            back = skia.Path()
            back.addRoundRect(skia.Rect.MakeXYWH(-r * 1.15 - f * r * 0.15, -r * 1.05, r * 2.3, r * 2.4), r, r)
            c.drawPath(back, K.paint(hc))
            c.drawPath(back, K.paint(LINE, 1, r * 0.06))
        p = skia.Path()
        p.moveTo(-r, -0.2 * r)
        p.cubicTo(-r, -1.15 * r, r, -1.15 * r, r, -0.2 * r)
        p.cubicTo(r, 0.45 * r, 0.45 * r * f + 0.2 * r, 0.95 * r, 0.25 * r * f, 1.05 * r)
        p.cubicTo(-0.25 * r + 0.25 * r * f, 0.95 * r, -r, 0.45 * r, -r, -0.2 * r)
        p.close()
        c.drawPath(p, K.paint("#FBE1CB"))
        c.drawPath(p, K.paint(LINE, 1, r * 0.06))
        ex0 = f * r * 0.28
        gap = r * 0.56
        ey = r * 0.12 - look * r * 0.1
        for k, sx in enumerate((ex0 - gap / 2, ex0 + gap / 2)):
            w = r * (0.26 if (k == 1) == (f > 0) else 0.22)
            if blink or mood == "happy":
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(sx - w, ey - w * 0.6, 2 * w, w * 1.2), 200, 140)
                c.drawPath(arc, K.paint(LINE, 1, r * 0.08))
                continue
            h = r * 0.36
            c.drawOval(skia.Rect.MakeXYWH(sx - w * 0.9, ey - h / 2, w * 1.8, h), K.paint("#FFFFFF"))
            ir = w * (0.55 if mood == "surprised" else 0.75)
            c.drawOval(skia.Rect.MakeXYWH(sx - ir, ey - h * 0.42, 2 * ir, h * 0.9), K.paint("#3E6E9E"))
            c.drawOval(skia.Rect.MakeXYWH(sx - ir * 0.5, ey - h * 0.2, ir, h * 0.5), K.paint("#16202C"))
            K.dot(c, sx - ir * 0.35, ey - h * 0.22, ir * 0.32, "#FFFFFF")
            K.dot(c, sx + ir * 0.35, ey + h * 0.15, ir * 0.15, "#FFFFFF")
            K.seg(c, sx - w * 0.95, ey - h * 0.5, sx + w * 0.95, ey - h * 0.55, LINE, r * 0.09)
            tilt_b = {"angry": 0.12, "worried": -0.1, "sad": -0.1}.get(mood, 0.0) * r * (1 if k == 0 else -1)
            K.seg(c, sx - w * 0.8, ey - h * 0.95 + tilt_b, sx + w * 0.8, ey - h * 0.95 - tilt_b, hc, r * 0.07)
        mx, my = ex0, r * 0.68
        if mood in ("smile", "happy"):
            m = skia.Path()
            m.moveTo(mx - r * 0.14, my)
            m.quadTo(mx, my + r * 0.18, mx + r * 0.14, my)
            m.close()
            c.drawPath(m, K.paint("#C2454A"))
        elif mood in ("open", "surprised", "angry"):
            c.drawOval(skia.Rect.MakeXYWH(mx - r * 0.08, my - r * 0.06, r * 0.16, r * 0.16), K.paint("#7A2430"))
        else:
            K.seg(c, mx - r * 0.08, my, mx + r * 0.08, my, LINE, r * 0.05)
        for sx in (ex0 - gap * 0.75, ex0 + gap * 0.75):
            for j in range(3):
                K.seg(c, sx - r * 0.1 + j * r * 0.08, r * 0.45, sx - r * 0.14 + j * r * 0.08, r * 0.55, "#E26A6A", r * 0.03)
        if style in ("short", "long", "bun", "bun_modern", None):
            bang = skia.Path()
            bang.moveTo(-r * 1.08, 0.05 * r)
            bang.cubicTo(-r * 1.15, -1.3 * r, r * 1.15, -1.3 * r, r * 1.08, 0.0)
            spikes = [(0.8, -0.15), (0.55, -0.45), (0.3, -0.05), (0.05, -0.5), (-0.25, -0.1), (-0.5, -0.45),
                      (-0.75, -0.05)]
            for sx_, sy_ in spikes:
                bang.lineTo(sx_ * r * f, sy_ * r)
            bang.close()
            c.drawPath(bang, K.paint(hc))
            c.drawPath(bang, K.paint(LINE, 1, r * 0.06))
            K.seg(c, -r * 0.3 * f, -0.85 * r, r * 0.2 * f, -0.95 * r, "#FFFFFF", r * 0.06, 0.6)
            if style == "bun_modern":
                c.drawCircle(-f * r * 0.6, -r * 1.05, r * 0.35, K.paint(hc))
        else:
            ink._hair(c, r, face, style, hc)


_BG: dict = {}


def bg_image(accent: str) -> skia.Image:
    """粉彩天空：上暖下蓝的渐变、两朵大云、四角网点。"""
    if accent in _BG:
        return _BG[accent]
    import cv2

    W, H = core.W, core.H
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (yy / H)[..., None]
    img = np.array(gfx.rgb("#FFF4E4"), np.float32) * (1 - t) + np.array(gfx.rgb("#D6E8F8"), np.float32) * t
    cloud = np.zeros((H, W), np.float32)
    for cx, cy, s in ((180, 420, 1.0), (900, 1180, 1.3)):
        for dx, dy, rr in ((0, 0, 90), (80, -30, 70), (-80, 10, 60), (150, 15, 55)):
            cloud = np.maximum(cloud, ((xx - cx - dx * s) ** 2 + (yy - cy - dy * s) ** 2 < (rr * s) ** 2).astype(np.float32))
    cloud = cv2.GaussianBlur(cloud, (0, 0), 2)
    img = img * (1 - 0.55 * cloud[..., None]) + 255 * 0.55 * cloud[..., None]
    corner = np.clip(0.75 - np.hypot((xx - W) / W, yy / H) * 1.6, 0, 1) + np.clip(0.75 - np.hypot(xx / W, (yy - H) / H) * 1.6, 0, 1)
    dots = ((np.mod(xx, 22) - 11) ** 2 + (np.mod(yy, 22) - 11) ** 2) < (corner * 7.5) ** 2
    img = np.where(dots[..., None], img * 0.85 + np.array(gfx.rgb(accent), np.float32) * 0.15, img)
    rgba = np.dstack([np.clip(img, 0, 255).astype(np.uint8), np.full((H, W), 255, np.uint8)])
    _BG[accent] = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    return _BG[accent]


def _speed_lines(c, k: float, seed: int, cx=540, cy=780, inner=430):
    """集中线：从画面四周射向中心的黑色细尖三角，k 为强度（0–1）。"""
    if k <= 0:
        return
    rng = np.random.default_rng(seed)
    p = skia.Path()
    for i in range(70):
        a = i / 70 * 2 * math.pi + rng.random() * 0.05
        r0 = inner + rng.random() * 160
        w = 0.008 + rng.random() * 0.012
        p.moveTo(cx + math.cos(a) * r0, cy + math.sin(a) * r0)
        p.lineTo(cx + math.cos(a - w) * 1600, cy + math.sin(a - w) * 1600)
        p.lineTo(cx + math.cos(a + w) * 1600, cy + math.sin(a + w) * 1600)
        p.close()
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 320, core.W, 1280))
    c.drawPath(p, K.paint(LINE, 0.85 * k))
    c.restore()


def install():
    """切换为日漫赛璐珞风（只影响当前进程）。"""
    ink.install()
    ink._wash = _wash
    ink._ink_head = _head
    ink.ink_layer = cel_layer
    K.paper = cel_layer
    K.figure = ink.ink_figure
    core.bg_image = bg_image
    gfx.FONT_FILES["serif_black"] = "SmileySans-Oblique.ttf"
    orig = core.draw_frame

    def draw_frame(c, ep, T, caption=True, ui=True):
        orig(c, ep, T, caption, ui)
        k = ep.shot_at(T)
        s = ep.shots[k]
        t = T - s.t0
        strength = math.exp(-t * 9) if k > 0 else 0.0
        for it in s.flashes:
            kb = it[0] if isinstance(it, tuple) else it
            dt = T - core.bt(s.b0 + kb)
            if 0 <= dt < 0.45:
                strength = max(strength, math.exp(-dt * 6))
                if dt < 1 / 30 + 1e-6:
                    c.save()
                    c.clipRect(skia.Rect.MakeLTRB(0, 320, core.W, 1280))
                    c.drawPaint(skia.Paint(Color=skia.ColorWHITE, BlendMode=skia.BlendMode.kDifference))
                    c.restore()
        _speed_lines(c, strength * 0.9, int(T * 30) // 2)

    core.draw_frame = draw_frame
