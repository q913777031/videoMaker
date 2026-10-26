"""经典剧场卡通画风工具：平滑闭合形状、带“沸腾”的墨线、融合轮廓的云团、胶皮管四肢、水粉纸纹。

boil 为线条抖动的帧组号（动画按“一拍二”每 2 帧换一组），同一组号画出完全相同的线条。所有函数是纯函数。
"""

import functools
import math

import numpy as np
import skia

from engine.gfx import H, W, col

INK = "#1E1612"


def _jitter(pts, boil: int, amp: float, seed: int):
    if amp <= 0:
        return pts
    rng = np.random.default_rng((seed * 9973 + boil * 7919) % (2 ** 32))
    return [(x + rng.normal(0, amp), y + rng.normal(0, amp)) for x, y in pts]


def smooth(pts, closed: bool = True, boil: int = 0, amp: float = 0.0, seed: int = 0) -> skia.Path:
    """Catmull-Rom 样条把控制点连成平滑路径；amp>0 时按 boil 组抖动控制点。"""
    p = _jitter(list(pts), boil, amp, seed)
    n = len(p)
    path = skia.Path()
    path.moveTo(*p[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = p[(i - 1) % n] if closed or i > 0 else p[i]
        p1, p2 = p[i], p[(i + 1) % n]
        p3 = p[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        path.cubicTo(*c1, *c2, *p2)
    if closed:
        path.close()
    return path


def ellipse_pts(cx, cy, rx, ry, n: int = 14, rot: float = 0.0, wob: float = 0.0, seed: int = 0):
    rng = np.random.default_rng(seed)
    cr, sr = math.cos(rot), math.sin(rot)
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        f = 1 + wob * rng.uniform(-1, 1)
        x, y = rx * f * math.cos(a), ry * f * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def fill(c: skia.Canvas, path: skia.Path, color, alpha: float = 1.0, shader=None):
    p = skia.Paint(AntiAlias=True, Color=col(color, alpha))
    if shader is not None:
        p.setShader(shader)
    c.drawPath(path, p)


def ink(c: skia.Canvas, path: skia.Path, width: float = 7.0, color=INK, alpha: float = 1.0):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width, Color=col(color, alpha),
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    c.drawPath(path, p)


def shape(c, pts, color, width: float = 7.0, boil: int = 0, amp: float = 1.2, seed: int = 0, shade=None):
    """填色 + 墨线的闭合形状；shade=(色, 偏移 dx, dy) 时在形状内叠一层错位暗部（卡通阴影）。"""
    path = smooth(pts, True, boil, amp, seed)
    fill(c, path, color)
    if shade:
        c.save()
        c.clipPath(path, doAntiAlias=True)
        off = skia.Path(path)
        off.offset(shade[1], shade[2])
        inv = skia.Path()
        inv.addRect(skia.Rect.MakeLTRB(-5000, -5000, 5000, 5000))
        fill(c, skia.Op(inv, off, skia.PathOp.kDifference_PathOp), shade[0], 0.55)
        c.restore()
    ink(c, path, width)
    return path


def cloud(c, circles, color, width: float = 8.0, boil: int = 0, amp: float = 1.0, seed: int = 0, shade=None):
    """多个圆融合成一团（羊毛、烟雾）：先画加粗墨线层，再整体填色盖住内部接缝。"""
    paths = [smooth(ellipse_pts(x, y, r, r * 0.95, 12, wob=0.06, seed=seed + k), True, boil, amp, seed + k)
             for k, (x, y, r) in enumerate(circles)]
    for p in paths:
        ink(c, p, width * 2)
    for p in paths:
        fill(c, p, color)
    if shade:
        for (x, y, r), p in zip(circles, paths):
            c.save()
            c.clipPath(p, doAntiAlias=True)
            fill(c, smooth(ellipse_pts(x + r * 0.35, y + r * 0.45, r * 0.9, r * 0.7, 10)), shade, 0.5)
            c.restore()


def hose(c, pts, width: float, color, boil: int = 0, amp: float = 1.0, seed: int = 0):
    """胶皮管四肢：沿控制点的粗软管，外描墨线。"""
    path = smooth(pts, False, boil, amp, seed)
    ink(c, path, width + 12)
    ink(c, path, width, color)


@functools.lru_cache(maxsize=4)
def paper(seed: int = 5) -> skia.Image:
    """水粉纸纹（乘性）：低频起伏 + 纤维颗粒。"""
    rng = np.random.default_rng(seed)
    lo = rng.normal(0, 1, (H // 64 + 2, W // 64 + 2)).astype(np.float32)
    import cv2
    lo = cv2.resize(lo, (W, H), interpolation=cv2.INTER_CUBIC)
    hi = rng.normal(0, 1, (H, W)).astype(np.float32)
    hi = cv2.GaussianBlur(hi, (0, 0), 0.8)
    v = 1 + 0.035 * lo + 0.045 * hi
    g = np.clip(v * 235, 0, 255).astype(np.uint8)
    rgba = np.dstack([g, g, g, np.full_like(g, 255)])
    return skia.Image.fromarray(rgba, skia.ColorType.kRGBA_8888_ColorType)


def apply_paper(c: skia.Canvas, strength: float = 1.0):
    p = skia.Paint(BlendMode=skia.BlendMode.kMultiply, Alphaf=strength)
    c.drawImage(paper(), 0, 0, skia.SamplingOptions(), p)


def wash(c, rect, top, bottom, seed: int = 0, streaks: int = 18, alpha: float = 1.0):
    """水粉平涂：上下渐变 + 竖向干笔刷痕。rect=(l, t, r, b)。"""
    l, t, r, b = rect
    p = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([(0, t), (0, b)], [col(top, alpha), col(bottom, alpha)]))
    c.drawRect(skia.Rect.MakeLTRB(l, t, r, b), p)
    rng = np.random.default_rng(seed)
    for _ in range(streaks):
        x = rng.uniform(l, r)
        w = rng.uniform(20, 70)
        sp = skia.Paint(AntiAlias=True, Color=col("#FFFFFF" if rng.random() < 0.5 else "#000000", rng.uniform(0.02, 0.05)),
                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8))
        c.drawRect(skia.Rect.MakeLTRB(x, t, x + w, b), sp)


def glow(c, x, y, r, color, alpha: float):
    p = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial((x, y), r, [col(color, alpha), col(color, 0)]))
    c.drawCircle(x, y, r, p)


def burst(c, x, y, r, n: int = 12, color="#FFD84A", boil: int = 0, seed: int = 0, rot: float = 0.0):
    """漫画拟声爆炸框（锯齿星形）。"""
    pts = []
    for k in range(2 * n):
        a = rot + math.pi * k / n
        rr = r * (1.0 if k % 2 == 0 else 0.62)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    path = skia.Path()
    for i, q in enumerate(_jitter(pts, boil, 3, seed)):
        path.lineTo(*q) if i else path.moveTo(*q)
    path.close()
    fill(c, path, color)
    ink(c, path, 7)


def speed_lines(c, x, y, ang: float, n: int, length: float, spread: float, width: float = 6, seed: int = 0, boil: int = 0):
    rng = np.random.default_rng(seed * 31 + boil)
    for k in range(n):
        a = ang + rng.uniform(-spread, spread)
        r0 = rng.uniform(0, 30)
        L = length * rng.uniform(0.6, 1.0)
        p = skia.Path()
        p.moveTo(x + r0 * math.cos(a), y + r0 * math.sin(a))
        p.lineTo(x + (r0 + L) * math.cos(a), y + (r0 + L) * math.sin(a))
        ink(c, p, width)
