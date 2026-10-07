"""《洞穴寓言》底稿绘制：通用形状工具、人物（侧脸 / 正脸 / 背影 / 坐姿）与 12 个镜头的场景。

所有函数在成片坐标（1080×1920）下作画，画布由 engine.paint.Under 缩放到底稿分辨率。
场景函数签名：draw(c, t, d)，t 为镜头内时间，d 为镜头时长；返回 (流场, 流场权重, 细节图或 None)。
"""

import functools
import math

import cv2
import numpy as np
import skia

from engine import paint as pt
from engine.gfx import clamp01, ease_in_out, ease_out, lerp, mix, rgb

W, H = pt.W, pt.H

# 梵高常用色
PRUSSIAN = "#14304d"
ULTRA = "#22398f"
NIGHT = "#0b1530"
VIOLET = "#3b2b5c"
COBALT = "#2f5fae"
CHROME = "#f4c431"
ORANGE = "#ec8a22"
VERMILION = "#d4462a"
OCHRE = "#c58f2c"
LEAD = "#f4ecd2"
VIRIDIAN = "#2f7d5c"
EMERALD = "#4fa36a"
SKIN = "#d6a27c"
LINEN = "#a88c5a"


# ---------------------------------------------------------------- 基础工具

def C(c, a: float = 1.0) -> int:
    r, g, b = rgb(c) if not isinstance(c, tuple) else c[:3]
    return skia.Color(int(r), int(g), int(b), int(255 * clamp01(a)))


def paint_of(color=None, alpha=1.0, shader=None, blur=0.0, blend=None, stroke=0.0) -> skia.Paint:
    p = skia.Paint(AntiAlias=True)
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(clamp01(alpha))
    else:
        p.setColor(C(color, alpha))
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None:
        p.setBlendMode(blend)
    if stroke > 0:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def radial(x, y, r, colors, pos=None) -> skia.Shader:
    return skia.GradientShader.MakeRadial((x, y), max(r, 1.0), [C(*k) if isinstance(k, tuple) and len(k) == 2
                                                                  and isinstance(k[1], float) else C(k)
                                                                  for k in colors], pos)


def linear(p0, p1, colors, pos=None) -> skia.Shader:
    return skia.GradientShader.MakeLinear([p0, p1], [C(*k) if isinstance(k, tuple) and len(k) == 2
                                                     and isinstance(k[1], float) else C(k) for k in colors], pos)


def smooth(pts, closed=True) -> skia.Path:
    """Catmull-Rom 平滑折线 → 三次贝塞尔路径。"""
    n = len(pts)
    path = skia.Path()
    path.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        path.cubicTo(c1, c2, p2)
    if closed:
        path.close()
    return path


def xf(pts, x, y, s, rot=0.0, sx=1.0):
    """局部坐标点列 → 成片坐标（缩放、水平压缩、旋转、平移）。"""
    cr, sr = math.cos(rot), math.sin(rot)
    return [(x + s * (px * sx * cr - py * sr), y + s * (px * sx * sr + py * cr)) for px, py in pts]


def ellipse(cx, cy, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def glow(c, x, y, r, color, alpha=1.0, blend=skia.BlendMode.kScreen):
    c.drawCircle(x, y, r, paint_of(shader=radial(x, y, r, [(color, alpha), (color, 0.0)]), blend=blend))


def lit(c, path, shadow, light, p0, p1, alpha=1.0):
    """用从 p0（受光色）到 p1（背光色）的线性渐变填充路径。"""
    c.drawPath(path, paint_of(shader=linear(p0, p1, [light, shadow]), alpha=alpha))


@functools.lru_cache(maxsize=32)
def noise_img(seed: int, scale: int, c1: str, c2: str, c3: str, w: int = pt.UW, h: int = pt.UH) -> skia.Image:
    """三色噪声材质（岩壁、草地、水面），底稿分辨率。"""
    rng = np.random.default_rng(seed)

    def layer(s):
        g = rng.random((h // s + 3, w // s + 3)).astype(np.float32)
        return cv2.resize(g, (w + 3 * s, h + 3 * s), interpolation=cv2.INTER_CUBIC)[:h, :w]

    a = 0.6 * layer(scale) + 0.4 * layer(max(2, scale // 3))
    b = 0.6 * layer(scale) + 0.4 * layer(max(2, scale // 4))
    a = (a - a.min()) / (np.ptp(a) + 1e-6)
    b = (b - b.min()) / (np.ptp(b) + 1e-6)
    k1, k2, k3 = (np.array(rgb(k), np.float32) for k in (c1, c2, c3))
    col = k1 * (1 - a[..., None]) + k2 * a[..., None]
    col = col * (1 - 0.6 * b[..., None]) + k3 * 0.6 * b[..., None]
    out = np.empty((h, w, 4), np.uint8)
    out[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    out[..., 3] = 255
    return skia.Image.fromarray(out, skia.ColorType.kRGBA_8888_ColorType)


def texture(c, img: skia.Image, rect=None, alpha=1.0, blend=None, dx=0.0, dy=0.0):
    """把底稿分辨率材质铺满 rect（成片坐标）；rect 超出材质尺寸时按比例拉伸。"""
    rect = rect or skia.Rect.MakeWH(W, H)
    p = paint_of("#FFFFFF", alpha, blend=blend)
    sw = min(rect.width() / pt.US, img.width())
    sh = min(rect.height() / pt.US, img.height())
    src = skia.Rect.MakeXYWH(min(dx / pt.US, img.width() - sw), min(dy / pt.US, img.height() - sh), sw, sh)
    c.drawImageRect(img, src, rect, skia.SamplingOptions(skia.FilterMode.kLinear), p)


def darken(c, amount, color="#000000"):
    if amount > 0:
        c.drawPaint(paint_of(color, amount))


def shade_rect(c, shader, blend=skia.BlendMode.kMultiply, rect=None):
    c.drawRect(rect or skia.Rect.MakeWH(W, H), paint_of(shader=shader, blend=blend))


# ---------------------------------------------------------------- 火

def fire(c, x, y, s, t, grow=1.0, alpha=1.0):
    """火堆：柴堆 + 多层摆动的火舌 + 光晕；grow 0..1 控制火势。"""
    if grow <= 0:
        return
    for i in range(5):
        a = -0.9 + i * 0.45
        lx, ly = x + math.cos(a) * 70 * s, y + 12 * s
        c.drawLine(x - math.cos(a) * 80 * s, ly + 10 * s, lx, ly - 18 * s,
                   paint_of("#3a2416", alpha, stroke=20 * s))
    glow(c, x, y - 60 * s, 520 * s * grow, ORANGE, 0.55 * alpha * grow)
    glow(c, x, y - 40 * s, 240 * s * grow, CHROME, 0.6 * alpha * grow)
    layers = [(VERMILION, 1.0, 0.95), (ORANGE, 0.78, 1.0), (CHROME, 0.55, 1.0), (LEAD, 0.28, 0.95)]
    for k, (colr, size, a_) in enumerate(layers):
        for j in range(5):
            ph = j * 1.7 + k * 0.9
            hgt = (150 + 60 * math.sin(t * 5.3 + ph)) * s * size * grow
            wid = (34 + 10 * math.sin(t * 3.1 + ph * 2)) * s * size * (0.6 + 0.4 * grow)
            bx = x + (j - 2) * 26 * s * size
            sway = 22 * s * math.sin(t * 4.2 + ph) * size
            pts = [(bx - wid, y), (bx - wid * 0.6, y - hgt * 0.4), (bx + sway, y - hgt),
                   (bx + wid * 0.6, y - hgt * 0.45), (bx + wid, y)]
            c.drawPath(smooth(pts), paint_of(colr, a_ * alpha))


def flicker(t, seed=0.0):
    return 0.88 + 0.07 * math.sin(t * 9.1 + seed) + 0.05 * math.sin(t * 23.7 + seed * 2)


# ---------------------------------------------------------------- 人物

# 侧脸轮廓（朝右，头高约 1 = 440px；原点在头部中心）
PROFILE = [(-0.02, -0.52), (0.14, -0.46), (0.22, -0.32), (0.25, -0.16), (0.22, -0.09), (0.25, -0.02),
           (0.33, 0.09), (0.26, 0.14), (0.27, 0.19), (0.24, 0.22), (0.26, 0.27), (0.22, 0.31),
           (0.23, 0.39), (0.15, 0.45), (0.0, 0.43), (-0.08, 0.36), (-0.06, 0.62), (0.16, 0.62),
           (0.13, 0.42), (-0.12, 0.3), (-0.28, 0.06), (-0.3, -0.2), (-0.2, -0.44)]


def head_profile(c, x, y, s, rot=0.0, light=("#f0c08a", SKIN), shadow="#5a3a3a", hair="#1c1712",
                 brow=0.0, eye=1.0, beard=0.3, style="short", light_dir=1.0, facing=1, alpha=1.0):
    """侧脸：皮肤（受光渐变）、头发、耳朵、眉、眼、嘴、胡茬。facing=1 朝右，-1 朝左；light_dir 光从脸前(1)或脑后(-1)。

    brow：0 平静，1 紧皱；eye：1 睁开，0 闭/眯；style：short / bun / old。
    """
    sx = facing

    def P(pts):
        return xf([(px * sx, py) for px, py in pts], x, y, s, rot)

    skin = smooth(P(PROFILE))
    fx, fy = P([(0.3 * light_dir, 0.0)])[0]
    bx, by = P([(-0.3 * light_dir, 0.1)])[0]
    c.save()
    if alpha < 1:
        c.saveLayerAlpha(None, int(255 * alpha))
    lit(c, skin, shadow, light[0], (fx, fy), (bx, by))
    # 胡茬 / 胡子
    if beard > 0:
        jaw = smooth(P([(0.26, 0.24), (0.24, 0.4), (0.12, 0.47), (-0.06, 0.4), (-0.12, 0.28), (0.05, 0.3)]))
        c.drawPath(jaw, paint_of("#3a3446" if style != "old" else "#d8d4cc", beard))
    # 耳朵
    ex, ey = P([(-0.1, 0.02)])[0]
    c.drawPath(ellipse(ex, ey, 0.06 * s, 0.1 * s), paint_of(mix(light[1], VERMILION, 0.25), 0.9))
    # 头发
    if style == "bun":
        hp = [(0.02, -0.5), (0.16, -0.44), (0.12, -0.3), (-0.02, -0.25), (-0.18, -0.08), (-0.2, 0.18),
              (-0.32, 0.12), (-0.36, -0.12), (-0.28, -0.42)]
        bun = P([(-0.4, -0.18)])[0]
        c.drawPath(ellipse(bun[0], bun[1], 0.13 * s, 0.13 * s), paint_of(hair))
    elif style == "old":
        hp = [(-0.05, -0.38), (-0.16, -0.4), (-0.28, -0.26), (-0.32, 0.0), (-0.22, 0.2), (-0.18, -0.05),
              (-0.12, -0.22)]
    else:
        hp = [(0.0, -0.56), (0.12, -0.54), (0.2, -0.44), (0.17, -0.36), (0.08, -0.38), (-0.02, -0.3),
              (-0.08, -0.12), (-0.16, 0.06), (-0.16, 0.22), (-0.28, 0.2), (-0.34, -0.02), (-0.34, -0.3),
              (-0.22, -0.5)]
    c.drawPath(smooth(P(hp)), paint_of(hair))
    hx, hy = P([(0.05, -0.5)])[0]
    hx2, hy2 = P([(-0.2, -0.2)])[0]
    c.drawPath(smooth(P(hp)), paint_of(shader=linear((hx, hy), (hx2, hy2), [(light[0], 0.35), (hair, 0.0)])))
    # 眉、眼、嘴
    b0 = P([(0.11, -0.2 + 0.03 * brow), (0.2, -0.205 + 0.045 * brow)])
    c.drawLine(*b0[0], *b0[1], paint_of("#2a1e1a", 0.95, stroke=0.025 * s))
    e = P([(0.15, -0.12), (0.205, -0.12 + 0.008 * (1 - eye))])
    c.drawLine(*e[0], *e[1], paint_of("#1d1620", 0.95, stroke=(0.012 + 0.02 * eye) * s))
    m = P([(0.24, 0.25), (0.18, 0.255 + 0.005 * brow)])
    c.drawLine(*m[0], *m[1], paint_of("#6a2a2a", 0.85, stroke=0.016 * s))
    if style == "old":
        wr = P([(0.12, -0.27), (0.2, -0.27)])
        c.drawLine(*wr[0], *wr[1], paint_of("#6a4a40", 0.5, stroke=0.01 * s))
    if alpha < 1:
        c.restore()
    c.restore()
    return skin


def head_front(c, x, y, s, rot=0.0, warm=("#ffd08a", "#e2a070"), shadow="#6a3e3a", brow=0.0, eye=1.0,
               squint=0.0, alpha=1.0, sx=1.0, light_x=0.0):
    """正脸：脸型、头发、耳、眉眼鼻嘴、胡茬。light_x 为受光方向（-1 左, 0 正面, 1 右）。"""
    def P(pts):
        return xf(pts, x, y, s, rot, sx)

    c.save()
    if alpha < 1:
        c.saveLayerAlpha(None, int(255 * alpha))
    # 脖子
    neck = smooth(P([(-0.13, 0.3), (0.13, 0.3), (0.15, 0.62), (-0.15, 0.62)]))
    c.drawPath(neck, paint_of(shadow))
    face = smooth(P([(0.0, -0.5), (0.24, -0.42), (0.3, -0.18), (0.28, 0.08), (0.2, 0.32), (0.08, 0.44),
                     (0.0, 0.46), (-0.08, 0.44), (-0.2, 0.32), (-0.28, 0.08), (-0.3, -0.18), (-0.24, -0.42)]))
    lx, ly = P([(light_x * 0.35, -0.1)])[0]
    c.drawPath(face, paint_of(shader=radial(lx, ly, 0.75 * s, [warm[0], warm[1], shadow], [0, 0.5, 1])))
    # 耳
    for side in (-1, 1):
        ex, ey = P([(0.31 * side, 0.0)])[0]
        c.drawPath(ellipse(ex, ey, 0.05 * s * sx, 0.1 * s), paint_of(mix(warm[1], VERMILION, 0.3), 0.85))
    # 胡茬
    c.drawPath(smooth(P([(-0.24, 0.12), (-0.12, 0.38), (0.0, 0.46), (0.12, 0.38), (0.24, 0.12), (0.14, 0.26),
                         (0.0, 0.3), (-0.14, 0.26)])), paint_of("#3a3446", 0.35))
    # 头发（凌乱微卷）
    hp = [(-0.34, -0.06), (-0.36, -0.34), (-0.24, -0.56), (-0.06, -0.64), (0.12, -0.62), (0.3, -0.52),
          (0.37, -0.3), (0.33, -0.08), (0.27, -0.3), (0.16, -0.38), (0.04, -0.34), (-0.08, -0.4),
          (-0.2, -0.32), (-0.28, -0.24)]
    c.drawPath(smooth(P(hp)), paint_of("#1c1712"))
    hx, hy = P([(light_x * 0.3, -0.55)])[0]
    c.drawPath(smooth(P(hp)), paint_of(shader=radial(hx, hy, 0.45 * s, [(warm[0], 0.4), (warm[0], 0.0)])))
    # 眉
    for side in (-1, 1):
        b = P([(0.06 * side, -0.17 + 0.03 * brow), (0.22 * side, -0.2 - 0.01 * brow)])
        c.drawLine(*b[0], *b[1], paint_of("#2a1e1a", 0.95, stroke=0.03 * s))
    # 眼
    for side in (-1, 1):
        ex, ey = P([(0.14 * side, -0.08)])[0]
        open_ = eye * (1 - squint)
        if open_ > 0.15:
            c.drawPath(ellipse(ex, ey, 0.065 * s * sx, 0.03 * s * open_), paint_of("#efe4d0", 0.9))
            c.drawCircle(ex, ey, 0.024 * s * min(1, open_ + 0.3), paint_of("#2a1c18"))
        e = P([(0.07 * side, -0.08 - 0.01 * squint), (0.21 * side, -0.075 + 0.012 * squint)])
        c.drawLine(*e[0], *e[1], paint_of("#2a1e22", 0.9, stroke=0.016 * s))
        if squint > 0.3:
            w1 = P([(0.2 * side, -0.06), (0.25 * side, -0.03)])
            c.drawLine(*w1[0], *w1[1], paint_of("#7a4a40", squint * 0.7, stroke=0.01 * s))
    # 鼻
    n = P([(0.02, -0.06), (0.05, 0.12), (0.0, 0.16), (-0.06, 0.14)])
    c.drawPath(smooth(n, closed=False), paint_of(shadow, 0.65, stroke=0.02 * s))
    # 嘴
    m = P([(-0.09, 0.27 - 0.01 * squint), (0.0, 0.26), (0.09, 0.27 - 0.01 * squint)])
    c.drawPath(smooth(m, closed=False), paint_of("#7a2e2a", 0.85, stroke=0.02 * s))
    if alpha < 1:
        c.restore()
    c.restore()


def head_back(c, x, y, s, rot=0.0, rim=ORANGE, rim_a=0.7, sx=1.0, hair="#1c1712", alpha=1.0, bald=False):
    """后脑勺：头发轮廓 + 脖子 + 暖色轮廓光。"""
    def P(pts):
        return xf(pts, x, y, s, rot, sx)

    c.save()
    if alpha < 1:
        c.saveLayerAlpha(None, int(255 * alpha))
    neck = smooth(P([(-0.14, 0.2), (0.14, 0.2), (0.16, 0.6), (-0.16, 0.6)]))
    c.drawPath(neck, paint_of("#6a4436"))
    head = smooth(P([(0.0, -0.52), (0.26, -0.44), (0.33, -0.16), (0.3, 0.1), (0.2, 0.32), (0.0, 0.38),
                     (-0.2, 0.32), (-0.3, 0.1), (-0.33, -0.16), (-0.26, -0.44)]))
    c.drawPath(head, paint_of("#8a6a5a" if bald else hair))
    for side in (-1, 1):
        ex, ey = P([(0.31 * side, 0.02)])[0]
        c.drawPath(ellipse(ex, ey, 0.05 * s * sx, 0.09 * s), paint_of("#7a4a3a"))
    hx, hy = P([(0.0, 0.45)])[0]
    c.drawPath(head, paint_of(shader=radial(hx, hy, 0.75 * s, [(rim, 0.0), (rim, 0.0), (rim, rim_a)],
                                           [0, 0.6, 1])))
    c.drawPath(head, paint_of(PRUSSIAN, 0.85, stroke=0.035 * s))
    if alpha < 1:
        c.restore()
    c.restore()


def torso_back(c, x, y, s, cloth=LINEN, rim=ORANGE, rim_a=0.5, sx=1.0, alpha=1.0):
    """坐姿背影的肩背（粗麻衣），(x, y) 为脖根。"""
    pts = xf([(-0.16, 0.0), (0.16, 0.0), (0.42, 0.1), (0.52, 0.4), (0.54, 1.3), (0.56, 2.4), (-0.56, 2.4), (-0.54, 1.3), (-0.52, 0.4),
              (-0.42, 0.1)], x, y, s, 0, sx)
    path = smooth(pts)
    c.drawPath(path, paint_of(shader=linear((x, y - 0.1 * s), (x, y + 1.2 * s),
                                            [mix(cloth, rim, 0.35 * rim_a), mix(cloth, PRUSSIAN, 0.45),
                                             mix(cloth, NIGHT, 0.75)]), alpha=alpha))
    c.drawPath(path, paint_of(PRUSSIAN, 0.9 * alpha, stroke=0.035 * s))
    return path


def collar_chain(c, x, y, s, to, alpha=1.0, color="#4a4a58", hi="#c79a5a"):
    """颈部铁环与垂下的链条：从 (x, y) 垂到 to。"""
    c.drawPath(ellipse(x, y, 0.2 * s, 0.06 * s), paint_of(color, alpha, stroke=0.05 * s))
    c.drawPath(ellipse(x, y - 0.01 * s, 0.2 * s, 0.06 * s), paint_of(hi, alpha * 0.5, stroke=0.015 * s))
    n = 14
    for i in range(n):
        k = i / (n - 1)
        px = lerp(x + 0.15 * s, to[0], k)
        py = lerp(y, to[1], k) + math.sin(k * math.pi) * 0.25 * s
        c.drawPath(ellipse(px, py, 0.035 * s, 0.025 * s), paint_of(color, alpha, stroke=0.018 * s))


def seated_back(c, x, y, s, t=0.0, rim=ORANGE, rim_a=0.6, hair="#1c1712", bald=False, chain=True, sway=0.0):
    """坐着的囚徒背影；(x, y) 为脖根。"""
    torso_back(c, x, y, s, rim=rim, rim_a=rim_a * 0.8)
    if chain:
        collar_chain(c, x, y + 0.03 * s, s, (x + 0.6 * s, y + 1.3 * s))
    head_back(c, x + sway * s, y - 0.32 * s, 0.82 * s, rot=sway * 0.3, rim=rim, rim_a=rim_a, hair=hair,
              bald=bald)


# ---------------------------------------------------------------- 场景通用

def dist_weight(cx, cy, r):
    """以 (cx, cy) 为中心、半径 r 的高斯权重图（底稿分辨率）。"""
    y, x = np.mgrid[0:pt.UH, 0:pt.UW].astype(np.float32)
    return np.exp(-(((x - cx / pt.US) ** 2 + (y - cy / pt.US) ** 2) / (2 * (r / pt.US) ** 2)))


def warm_cool(c, cool, warm, light_xy, light_r, strength=1.0, rect=None, dy=0.0):
    """冷色材质铺底，暖色材质按光源径向衰减叠在上面（保持两者饱和度，避免混成灰粉色）。"""
    rect = rect or skia.Rect.MakeWH(W, H)
    texture(c, cool, rect=rect, dy=dy)
    lx, ly = light_xy
    c.saveLayer(rect, None)
    texture(c, warm, rect=rect, dy=dy)
    c.drawRect(rect, paint_of(shader=radial(lx, ly, max(light_r, 1), [("#000000", clamp01(strength)),
                                                                      ("#000000", 0.75 * clamp01(strength)),
                                                                      ("#000000", 0.0)], [0, 0.45, 1]),
                              blend=skia.BlendMode.kDstIn))
    c.restore()


def cave_wall(c, light_xy, light_r, light_col=ORANGE, strength=1.0, seed=11, dy=0.0, base=None, warm=None):
    """岩壁：冷色噪声材质（普鲁士蓝 / 紫 / 群青）+ 以光源为中心的暖色材质（赭 / 橙 / 铬黄）。"""
    cool = noise_img(seed, 36, *(base or (NIGHT, VIOLET, COBALT)))
    hot = noise_img(seed + 100, 30, *(warm or (OCHRE, ORANGE, VERMILION)))
    warm_cool(c, cool, hot, light_xy, light_r, strength, dy=dy)


def floor(c, y0, light_xy, light_r, strength=1.0, seed=12):
    r = skia.Rect.MakeLTRB(0, y0, W, H)
    c.saveLayer(r, None)
    warm_cool(c, noise_img(seed, 24, "#141026", "#22204a", "#2a1a30"),
              noise_img(seed + 100, 20, "#6a4420", OCHRE, "#8a3a20"), light_xy, light_r, strength, rect=r)
    c.drawRect(r, paint_of(shader=linear((0, y0), (0, y0 + 160), [("#000000", 0.0), ("#000000", 1.0)]),
                           blend=skia.BlendMode.kDstIn))
    c.restore()


def object_shadows(c, t, x0, y0, speed, alpha=0.85, scale=1.0, color="#1a1020"):
    """石壁上被举着走过的器物影子：人形雕像、马、罐；x0 为起点，随时间向右移动。"""
    items = [
        ("man", 0.0, 0.0), ("horse", 330.0, 40.0), ("jar", 640.0, 30.0), ("man", 900.0, -10.0),
    ]
    blur = 10 * scale
    for kind, off, yoff in items:
        x = x0 + off * scale + speed * t
        y = y0 + yoff * scale + 6 * math.sin(t * 2.4 + off)
        s = scale
        p = paint_of(color, alpha, blur=blur)
        if kind == "man":
            c.drawCircle(x, y - 150 * s, 34 * s, p)
            c.drawPath(smooth([(x - 40 * s, y - 110 * s), (x + 40 * s, y - 110 * s), (x + 55 * s, y - 20 * s),
                               (x + 30 * s, y + 60 * s), (x - 30 * s, y + 60 * s), (x - 55 * s, y - 20 * s)]), p)
            c.drawLine(x - 50 * s, y - 90 * s, x - 90 * s, y - 10 * s, paint_of(color, alpha, stroke=20 * s, blur=blur))
        elif kind == "horse":
            pts = [(-120, -40), (-60, -70), (40, -70), (80, -110), (130, -150), (150, -120), (110, -70),
                   (100, -10), (90, 80), (70, 80), (60, 0), (-60, 0), (-80, 80), (-100, 80), (-110, -10),
                   (-150, 20)]
            c.drawPath(smooth([(x + px * s, y + py * s) for px, py in pts]), p)
        else:
            c.drawPath(smooth([(x - 30 * s, y - 120 * s), (x + 30 * s, y - 120 * s), (x + 20 * s, y - 95 * s),
                               (x + 70 * s, y - 40 * s), (x + 40 * s, y + 50 * s), (x - 40 * s, y + 50 * s),
                               (x - 70 * s, y - 40 * s), (x - 20 * s, y - 95 * s)]), p)
        # 举着器物的手和木杆
        c.drawLine(x, y + 60 * s, x - 10 * s, y + 260 * s, paint_of(color, alpha * 0.8, stroke=14 * s, blur=blur))


def low_wall(c, y, light=0.6):
    """囚徒身后的矮墙（只在需要时出现）。"""
    r = skia.Rect.MakeLTRB(-20, y, W + 20, y + 120)
    texture(c, noise_img(21, 16, "#2a1e22", "#4a3426", "#1a1420"), rect=r)
    c.drawRect(skia.Rect.MakeLTRB(-20, y - 6, W + 20, y + 10), paint_of(ORANGE, light * 0.6, blur=6))


# ---------------------------------------------------------------- 镜头 2：火燃起

def s2_fire(c, t, d):
    grow = ease_out(clamp01((t - 0.15) / 1.8))
    fx, fy = 540, 1380
    r = lerp(120, 1250, grow) * flicker(t)
    cave_wall(c, (fx, fy - 200), r, strength=0.4 + 0.6 * grow)
    floor(c, 1330, (fx, fy), r * 0.9, strength=grow)
    # 洞顶与两侧更暗的岩体（拱形洞腔）
    rock = paint_of(NIGHT, 0.85, blur=38)
    c.drawPath(smooth([(-80, -80), (1160, -80), (1160, 420), (1010, 260), (930, 380), (820, 230), (700, 300),
                       (560, 210), (420, 330), (300, 230), (160, 400), (60, 300), (-80, 470)]), rock)
    c.drawPath(smooth([(-80, 380), (110, 560), (170, 900), (120, 1250), (230, 1500), (140, 1800), (-80, 2000)]),
               rock)
    c.drawPath(smooth([(1160, 380), (980, 600), (920, 950), (990, 1250), (880, 1520), (960, 1800), (1160, 2000)]),
               rock)
    for x, l in [(330, 150), (520, 110), (760, 170), (880, 90)]:
        c.drawPath(smooth([(x - 30, 200), (x + 30, 200), (x + 6, 200 + l), (x - 6, 200 + l)]), rock)
    fire(c, fx, fy, 1.5, t, grow)
    f = pt.blend_fields((pt.swirl_field(t, 3), 1.0), (pt.concentric_field(fx, fy - 120),
                                                      2.5 * dist_weight(fx, fy - 120, 420 * (0.3 + grow))),
                        (pt.flame_field(t), 3.0 * dist_weight(fx, fy - 80, 140)))
    return f, 0.75, None


# ---------------------------------------------------------------- 镜头 3：囚徒背影

PRISONERS = [(150, 1330, 300, "#1c1712", False), (360, 1300, 320, "#2a1a10", False),
             (580, 1320, 330, "#1c1712", False), (790, 1300, 315, "#3a3a3a", True),
             (990, 1340, 300, "#241a14", False)]


def prisoners_row(c, t, wall_light=1.0, empty=None, zoom=1.0, cx=540, cy=1500):
    """囚徒并排背坐、面向石壁；empty 为空出的位置序号；墙上投着他们的头影与器物影。"""
    fl = flicker(t)
    c.save()
    c.translate(cx, cy)
    c.scale(zoom, zoom)
    c.translate(-cx, -cy)
    cave_wall(c, (540, 1700), 1500 * fl, strength=wall_light)
    # 墙面受光区（火在背后低处）
    c.drawRect(skia.Rect.MakeLTRB(-100, 150, W + 100, 1150),
               paint_of(shader=radial(540, 900, 800 * fl, [(OCHRE, 0.55), (VERMILION, 0.2), (VERMILION, 0.0)]),
                        blend=skia.BlendMode.kScreen))
    object_shadows(c, t, -260, 640, 26, alpha=0.75)
    for i, (x, y, s, hair, bald) in enumerate(PRISONERS):
        if i == empty:
            continue
        c.drawCircle(x + 20, y - 520, 120, paint_of("#120c18", 0.55, blur=30))  # 头影
    floor(c, 1250, (540, 1950), 900 * fl, strength=wall_light * 0.9)
    for i, (x, y, s, hair, bald) in enumerate(PRISONERS):
        if i == empty:
            continue
        seated_back(c, x, y, s, t, rim_a=0.55 * wall_light, hair=hair, bald=bald,
                    sway=0.01 * math.sin(t * 0.8 + i))
    if empty is not None:
        x, y, s, _, _ = PRISONERS[empty]
        for k in range(12):
            px = x - 120 + k * 22
            py = y + 330 + 14 * math.sin(k * 0.9)
            c.drawPath(ellipse(px, py, 12, 8), paint_of("#4a4a58", 0.95, stroke=6))
            c.drawPath(ellipse(px, py - 2, 12, 8), paint_of(OCHRE, 0.5, stroke=2))
    c.restore()


def s3_backs(c, t, d):
    zoom = 1.0 + 0.04 * t / d
    prisoners_row(c, t, zoom=zoom)
    return pt.swirl_field(t, 5), 0.55, None


# ---------------------------------------------------------------- 镜头 4：墙上的影子

def s4_shadows(c, t, d):
    fl = flicker(t, 1.0)
    cave_wall(c, (540, 1500), 1300 * fl, light_col=OCHRE, strength=1.0, seed=31,
              base=("#3a2a3a", "#5a4030", "#2a2440"))
    c.drawPaint(paint_of(shader=radial(560, 900, 900 * fl, [(CHROME, 0.35), (ORANGE, 0.2), (ORANGE, 0.0)]),
                         blend=skia.BlendMode.kScreen))
    object_shadows(c, t, -330, 980, 62, alpha=0.85, scale=1.6)
    # 前景囚徒头部剪影
    for x, y, s in [(170, 1830, 520), (560, 1880, 560), (930, 1840, 500)]:
        head_back(c, x, y, s, rim_a=0.45)
        c.drawPath(smooth([(x - 0.5 * s, y + 0.3 * s), (x + 0.5 * s, y + 0.3 * s), (x + 0.6 * s, y + 0.8 * s),
                           (x - 0.6 * s, y + 0.8 * s)]), paint_of("#1a1418"))
    return pt.swirl_field(t, 7, scale=70), 0.5, None


# ---------------------------------------------------------------- 人物补充

def torso_front(c, x, y, s, cloth=LINEN, light=ORANGE, light_a=0.5, sx=1.0, alpha=1.0, hood=False):
    """正面肩胸（粗麻衣 V 领 / 卫衣），(x, y) 为脖根。"""
    pts = xf([(-0.16, 0.0), (0.16, 0.0), (0.5, 0.14), (0.64, 0.42), (0.68, 1.3), (0.7, 2.4), (-0.7, 2.4),
              (-0.68, 1.3), (-0.64, 0.42), (-0.5, 0.14)], x, y, s, 0, sx)
    path = smooth(pts)
    c.drawPath(path, paint_of(shader=linear((x, y), (x, y + 1.3 * s), [mix(cloth, light, 0.4 * light_a),
                                                                      mix(cloth, PRUSSIAN, 0.5)]), alpha=alpha))
    if hood:
        c.drawPath(smooth(xf([(-0.3, -0.02), (0.3, -0.02), (0.22, 0.12), (-0.22, 0.12)], x, y, s, 0, sx)),
                   paint_of(mix(cloth, NIGHT, 0.4), alpha))
    else:
        v = xf([(-0.14, 0.0), (0.0, 0.26), (0.14, 0.0)], x, y, s, 0, sx)
        c.drawPath(smooth(v, closed=False), paint_of("#5a3a30", alpha * 0.9, stroke=0.03 * s))
    c.drawPath(path, paint_of(PRUSSIAN, 0.85 * alpha, stroke=0.03 * s))


def walker(c, x, y, s, color="#1a1430", alpha=1.0, arm=1.0, step=0.0):
    """逆光中向上走的背影剪影（一只手臂挡在眼前）。"""
    p = paint_of(color, alpha, blur=0.03 * s)
    c.drawCircle(x, y - 0.82 * s, 0.11 * s, p)
    c.drawPath(smooth([(x - 0.17 * s, y - 0.66 * s), (x + 0.17 * s, y - 0.66 * s), (x + 0.2 * s, y - 0.1 * s),
                       (x + 0.12 * s, y + 0.05 * s), (x - 0.12 * s, y + 0.05 * s), (x - 0.2 * s, y - 0.1 * s)]), p)
    for side, ph in ((-1, 0.0), (1, math.pi)):
        sw = 0.08 * s * math.sin(step + ph)
        c.drawLine(x + side * 0.08 * s, y, x + side * 0.1 * s + sw, y + 0.42 * s,
                   paint_of(color, alpha, stroke=0.1 * s, blur=0.02 * s))
    c.drawLine(x + 0.15 * s, y - 0.6 * s, x + lerp(0.3, 0.05, arm) * s, y - lerp(0.25, 0.85, arm) * s,
               paint_of(color, alpha, stroke=0.08 * s, blur=0.02 * s))


# ---------------------------------------------------------------- 镜头 1：深夜，手机光

def s1_phone(c, t, d):
    zoom = 1 + 0.07 * ease_in_out(t / d)
    c.save()
    c.translate(560, 950)
    c.scale(zoom, zoom)
    c.translate(-560, -950)
    texture(c, noise_img(41, 40, NIGHT, ULTRA, PRUSSIAN))
    # 窗与星夜
    win = skia.Rect.MakeLTRB(70, 160, 430, 700)
    texture(c, noise_img(42, 30, "#0d1d5a", COBALT, "#1a2a70"), rect=win)
    for sx_, sy_, r in [(160, 280, 26), (330, 230, 20), (260, 450, 30), (380, 560, 16), (120, 600, 14)]:
        glow(c, sx_, sy_, r * 3.2, CHROME, 0.55)
        c.drawCircle(sx_, sy_, r * 0.7, paint_of(LEAD, 0.95))
    glow(c, 360, 380, 120, "#f0e080", 0.5)
    c.drawCircle(360, 380, 34, paint_of("#f6e27a"))
    c.drawRect(win, paint_of("#2a2030", 0.95, stroke=26))
    c.drawLine(250, 160, 250, 700, paint_of("#2a2030", 0.95, stroke=18))
    # 手机冷光
    px, py = 780, 1230
    glow(c, px, py, 760, "#bfe6d0", 0.5)
    # 身体（卫衣）
    hood = smooth([(300, 1120), (560, 1060), (690, 1160), (820, 1420), (880, 1980), (120, 1980), (160, 1500),
                   (230, 1260)])
    c.drawPath(hood, paint_of(shader=linear((820, 1300), (200, 1500), ["#5a7a8a", "#283048", "#141a30"])))
    c.drawPath(hood, paint_of(PRUSSIAN, 0.9, stroke=12))
    c.drawPath(smooth([(250, 1150), (420, 1060), (520, 1130), (420, 1250), (300, 1260)]),
               paint_of("#1e2440"))
    # 头（侧脸朝右，低头看手机）
    brow = ease_in_out(clamp01((t - 1.6) / 2.6))
    head_profile(c, 540, 860, 560, rot=0.22, light=("#b8e2cc", "#88a8a0"), shadow="#2e2a50", brow=brow,
                 eye=0.8, beard=0.35)
    # 手与手机
    c.save()
    c.translate(px, py)
    c.rotate(-18)
    c.drawRoundRect(skia.Rect.MakeLTRB(-22, -110, 22, 110), 14, 14, paint_of("#101018"))
    c.drawRoundRect(skia.Rect.MakeLTRB(-30, -116, -18, 116), 6, 6, paint_of("#e8fff4", 0.9, blur=6))
    c.restore()
    c.drawPath(smooth([(690, 1270), (800, 1250), (860, 1330), (780, 1400), (680, 1360)]),
               paint_of(shader=linear((700, 1250), (800, 1400), ["#c8dcd0", "#5a5a70"])))
    c.restore()
    f = pt.blend_fields((pt.swirl_field(t, 9), 1.0), (pt.concentric_field(360 * zoom, 380), 2.0 * dist_weight(300, 420, 220)),
                        (pt.concentric_field(px, py), 1.2 * dist_weight(px, py, 300)))
    return f, 0.6, dist_weight(600, 860, 300)


# ---------------------------------------------------------------- 镜头 5：转身

def s5_turn(c, t, d):
    fl = flicker(t, 2.0)
    cave_wall(c, (540, 1700), 1700 * fl, strength=0.9, seed=51)
    c.drawPaint(paint_of(shader=radial(540, 1100, 900, [(ORANGE, 0.4), (VERMILION, 0.0)]),
                         blend=skia.BlendMode.kScreen))
    object_shadows(c, t, -300, 520, 30, alpha=0.6, scale=1.0)
    r = ease_in_out(clamp01((t - 0.35) / 2.0))
    sq = 1 - 0.3 * math.sin(math.pi * r)
    x, y, s = 540, 820, 620
    if r < 1:
        torso_back(c, x, y + 0.32 * s, s, sx=sq, rim_a=0.7, alpha=1 - r)
        head_back(c, x, y, 0.95 * s, sx=sq, rim_a=0.7, alpha=1 - r)
    if r > 0:
        torso_front(c, x, y + 0.32 * s, s, sx=sq, light_a=0.9, alpha=r)
        head_front(c, x, y, 0.95 * s, sx=sq, alpha=r, eye=1.0, squint=0.25 * r, brow=0.4 * r)
    return pt.swirl_field(t, 13), 0.5, dist_weight(x, y, 260)


# ---------------------------------------------------------------- 镜头 6：火光刺眼

def s6_glare(c, t, d):
    fl = flicker(t, 3.0)
    gx, gy = 1180, 640
    cave_wall(c, (gx, gy), 1500 * fl, strength=1.0, seed=61, warm=(ORANGE, CHROME, VERMILION))
    glow(c, gx, gy, 900 * fl, LEAD, 0.75)
    glow(c, gx, gy, 380, "#fff6d8", 0.9)
    tilt = -0.14 * ease_out(clamp01((t - 0.3) / 1.4))
    x, y, s = 470, 900, 980
    torso_front(c, x + 30, y + 0.34 * s, s * 0.95, light_a=1.0)
    head_front(c, x, y, s, rot=tilt, warm=("#fff0b8", "#f0b070"), shadow="#7a3a3a", brow=1.0, eye=1.0,
               squint=1.0, light_x=0.9)
    # 手臂抬起挡光：前臂从画面右下伸到额前，手掌横在眉骨上方
    k = ease_out(clamp01((t - 0.15) / 1.1))
    hand = (lerp(1050, 600, k), lerp(1950, 760, k))
    elbow = (lerp(1150, 980, k), lerp(2100, 1300, k))
    pth = skia.Path()
    pth.moveTo(1200, 2100)
    pth.quadTo(*elbow, hand[0] + 150, hand[1] + 40)
    c.drawPath(pth, paint_of(PRUSSIAN, 0.8, stroke=214))
    c.drawPath(pth, paint_of(shader=linear(elbow, hand, ["#7a3e34", "#e8b080"]), stroke=200))
    palm = smooth([(hand[0] + 200, hand[1] - 40), (hand[0] + 40, hand[1] - 95), (hand[0] - 180, hand[1] - 80),
                   (hand[0] - 260, hand[1] - 30), (hand[0] - 190, hand[1] + 10), (hand[0] + 20, hand[1] + 60),
                   (hand[0] + 190, hand[1] + 70)])
    c.drawPath(palm, paint_of(shader=linear((hand[0] + 200, hand[1]), (hand[0] - 250, hand[1]),
                                            ["#f6d0a0", "#e0a070", "#b8704e"])))
    c.drawPath(palm, paint_of("#6a3028", 0.8, stroke=12))
    for i in range(3):
        fy_ = hand[1] - 45 + i * 30
        c.drawLine(hand[0] - 220 + i * 20, fy_, hand[0] - 40, fy_ + 8, paint_of("#8a4a3a", 0.6, stroke=7))
    f = pt.blend_fields((pt.concentric_field(gx, gy), 2.0), (pt.radial_field(gx, gy), 0.6),
                        (pt.swirl_field(t, 17), 0.5))
    return f, 0.7, dist_weight(x, y - 60, 330)


# ---------------------------------------------------------------- 镜头 7：被拉出洞口

def s7_exit(c, t, d):
    mx, my = 560, 360
    k = clamp01(t / d)
    cave_wall(c, (mx, my), 1700, light_col=CHROME, strength=1.0, seed=71,
              base=(NIGHT, PRUSSIAN, VIOLET), warm=(CHROME, LEAD, OCHRE))
    # 两侧岩壁向洞口收拢
    rock = paint_of(NIGHT, 0.88, blur=30)
    c.drawPath(smooth([(-80, -80), (380, -80), (420, 300), (330, 700), (220, 1200), (160, 1980), (-80, 1980)]), rock)
    c.drawPath(smooth([(1160, -80), (740, -80), (700, 320), (800, 760), (900, 1250), (980, 1980), (1160, 1980)]), rock)
    # 坡道
    c.drawPath(smooth([(470, 520), (650, 520), (900, 1980), (180, 1980)]),
               paint_of(shader=linear((0, 500), (0, 1980), [mix(OCHRE, LEAD, 0.4), "#3a2a30", "#141020"])))
    glow(c, mx, my, 520 + 200 * k, LEAD, 0.95)
    glow(c, mx, my, 250, "#ffffff", 1.0)
    e = ease_in_out(k)
    walker(c, lerp(520, 560, e), lerp(1250, 600, e), lerp(820, 300, e), alpha=lerp(1.0, 0.5, e),
           step=t * 5.0, arm=1.0)
    darken(c, 0.85 * ease_in_out(clamp01((t - d * 0.45) / (d * 0.55))), "#fffbea")
    f = pt.blend_fields((pt.radial_field(mx, my), 1.0), (pt.concentric_field(mx, my), 1.5 * dist_weight(mx, my, 400)))
    return f, 0.7, None


# ---------------------------------------------------------------- 镜头 8：水中倒影 → 抬头看光

def _meadow(c, t, oy):
    """晨光草地世界（高 2H）：天空与太阳光晕、远山、草地、溪流与倒影。"""
    c.save()
    c.translate(0, -oy)
    sky = skia.Rect.MakeLTRB(0, 0, W, 1000)
    texture(c, noise_img(81, 34, "#7fb0d8", "#b8d4e0", "#e6dc9a"), rect=sky)
    glow(c, 980, 160, 900, "#fff2b0", 0.85)
    glow(c, 980, 160, 260, "#fffbe6", 1.0)
    c.drawPath(smooth([(-50, 960), (200, 860), (420, 920), (640, 840), (900, 900), (1130, 860), (1130, 1060),
                       (-50, 1060)]), paint_of("#6a78b0", 0.95))
    texture(c, noise_img(82, 22, EMERALD, "#b8b048", VIRIDIAN), rect=skia.Rect.MakeLTRB(0, 1000, W, 1800))
    # 溪流（世界 y 1700–3840）
    water = skia.Rect.MakeLTRB(0, 1700, W, 2 * H)
    texture(c, noise_img(83, 26, "#2a5a7a", "#4a8aa0", "#2f6a5a"), rect=water, dy=0)
    c.drawRect(water, paint_of(shader=linear((0, 1700), (0, 2 * H), [("#f0e0a0", 0.45), ("#f0e0a0", 0.0)]),
                               blend=skia.BlendMode.kScreen))
    c.drawPath(smooth([(-50, 1690), (300, 1740), (700, 1700), (1130, 1750), (1130, 1800), (-50, 1800)]),
               paint_of("#4a5a2a"))
    c.restore()


def s8_reflect(c, t, d):
    e = ease_in_out(clamp01((t - 0.4) / (d * 0.7)))
    oy = H * (1 - e)
    _meadow(c, t, oy)
    lift = ease_in_out(clamp01((t - d * 0.45) / (d * 0.45)))
    rot = lerp(0.45, -0.12, lift)
    hx, hy, s = 470, 980, 560
    # 倒影（世界坐标，翻转、半透明、波纹）
    c.save()
    c.translate(0, -oy)
    ry = 2 * 1760 - hy
    c.save()
    c.translate(0, ry)
    c.scale(1, -1)
    c.translate(0, -hy)
    head_profile(c, hx + 40, hy + 260, s * 0.9, rot=0.45, light=("#e8c890", "#a88a6a"), shadow="#3a4a5a",
                 alpha=0.6)
    c.restore()
    for k in range(9):
        yy = 2300 + k * 120 + 10 * math.sin(t * 2 + k)
        c.drawLine(80 + 40 * k % 200, yy, 980 - 30 * k % 160, yy, paint_of("#e8f0e0", 0.25, stroke=6))
    c.restore()
    # 人物（跪在溪边，侧脸朝右）
    c.save()
    c.translate(0, -oy)
    body = smooth([(330, 1200), (560, 1190), (640, 1330), (720, 1560), (800, 1720), (620, 1770), (240, 1770),
                   (220, 1550), (260, 1350)])
    c.drawPath(body, paint_of(shader=linear((640, 1200), (240, 1600), ["#e8d098", LINEN, "#4a4a5a"])))
    c.drawPath(body, paint_of(PRUSSIAN, 0.85, stroke=12))
    head_profile(c, hx, hy, s, rot=rot, light=("#ffe2a8", "#e0a878"), shadow="#5a4a5a", brow=0.5 * (1 - lift),
                 eye=lerp(0.3, 0.6, lift), beard=0.35)
    c.restore()
    darken(c, 0.75 * (1 - ease_out(clamp01(t / 2.2))), "#fffbea")
    y_sun = 160 - oy
    sky_w = np.zeros((pt.UH, pt.UW), np.float32)
    top = int(clamp01((1000 - oy) / H) * pt.UH)
    sky_w[:top] = 1
    wat = int(clamp01((1700 - oy) / H) * pt.UH)
    water_w = np.zeros_like(sky_w)
    water_w[wat:] = 1
    f = pt.blend_fields((pt.concentric_field(980, y_sun), 1.5 * sky_w + 0.01), (pt.flame_field(t, 0.25), 1.0 - sky_w),
                        (pt.const_field(0.0), 3.0 * water_w))
    return f, 0.7, dist_weight(hx, hy - oy, 300)


# ---------------------------------------------------------------- 镜头 9：从黑暗升向洞口

def s9_passage(c, t, d):
    e = ease_in_out(clamp01(t / d))
    world = 1.6 * H
    oy = (world - H) * (1 - e)
    c.save()
    c.translate(0, -oy)
    mx, my = 540, 260
    texture(c, noise_img(91, 36, NIGHT, VIOLET, PRUSSIAN), rect=skia.Rect.MakeLTRB(0, 0, W, world))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, world),
               paint_of(shader=radial(mx, my, 1500, [mix(CHROME, LEAD, 0.4), OCHRE, ("#000000", 0.0)], [0, 0.35, 1]),
                        blend=skia.BlendMode.kScreen))
    c.drawPath(smooth([(470, 380), (620, 380), (840, world + 50), (240, world + 50)]),
               paint_of(shader=linear((0, 380), (0, world), [mix(OCHRE, LEAD, 0.3), "#3a2a40", "#0a0a18"])))
    # 光柱
    beam = smooth([(470, 260), (640, 260), (900, 1500), (520, 1600)])
    c.drawPath(beam, paint_of(shader=linear((560, 260), (700, 1600), [("#fff4c8", 0.55), ("#fff4c8", 0.0)]),
                              blend=skia.BlendMode.kScreen))
    glow(c, mx, my, 360, "#fffbe6", 1.0)
    # 底部火堆余烬
    glow(c, 520, world - 120, 260, VERMILION, 0.45)
    # 尘埃
    rng = np.random.default_rng(9)
    for x0, y0, ph in rng.random((40, 3)):
        x = 520 + (x0 - 0.3) * 380 + 20 * math.sin(t * 0.7 + ph * 6)
        y = 400 + y0 * 1100 - t * 12
        c.drawCircle(x, y, 7, paint_of("#fff6d0", 0.8 * (0.5 + 0.5 * math.sin(t * 2 + ph * 9))))
    c.restore()
    f = pt.blend_fields((pt.concentric_field(mx, my - oy), 2.0 * dist_weight(mx, my - oy, 500) + 0.01),
                        (pt.swirl_field(t, 19), 1.0), (pt.radial_field(mx, my - oy), 0.5))
    return f, 0.7, None


# ---------------------------------------------------------------- 镜头 10：其他囚徒的侧脸

def s10_faces(c, t, d):
    fl = flicker(t, 4.0)
    dx = lerp(70, -70, ease_in_out(t / d))
    cave_wall(c, (-100, 1400), 1300 * fl, strength=0.95, seed=101)
    c.save()
    c.translate(dx, 0)
    people = [(300, 760, 430, "bun", "#2a1a14", 0.0), (620, 1080, 470, "short", "#1c1712", 0.25),
              (880, 1420, 440, "old", "#d8d0c8", 0.0)]
    for x, y, s, style, hair, beard in people:
        sh = smooth([(x - 0.55 * s, y + 0.6 * s), (x + 0.2 * s, y + 0.5 * s), (x + 0.5 * s, y + 0.75 * s),
                     (x + 0.6 * s, y + 1.4 * s), (x - 0.7 * s, y + 1.4 * s)])
        c.drawPath(sh, paint_of(shader=linear((x - 0.6 * s, y), (x + 0.6 * s, y), [mix(LINEN, ORANGE, 0.5),
                                                                                  mix(LINEN, PRUSSIAN, 0.6)])))
        c.drawPath(sh, paint_of(PRUSSIAN, 0.85, stroke=10))
        head_profile(c, x, y, s, rot=0.04, light=("#f8b868", "#c87a50"), shadow="#3a2a48", hair=hair,
                     beard=beard if style != "old" else 0.8, style=style, light_dir=-1, eye=0.9)
        collar_chain(c, x - 0.02 * s, y + 0.55 * s, s * 0.9, (x - 0.5 * s, y + 1.4 * s))
    c.restore()
    return pt.swirl_field(t, 23), 0.5, np.maximum(dist_weight(300 + dx, 760, 200), np.maximum(
        dist_weight(620 + dx, 1080, 220), dist_weight(880 + dx, 1420, 210)))


# ---------------------------------------------------------------- 镜头 11：黎明的卧室

def s11_dawn(c, t, d):
    zoom = 1 + 0.05 * ease_in_out(t / d)
    c.save()
    c.translate(540, 1100)
    c.scale(zoom, zoom)
    c.translate(-540, -1100)
    texture(c, noise_img(111, 36, "#5a6aa8", "#7a88b8", "#4a5a90"))
    # 地板
    c.drawPath(smooth([(-50, 1500), (1130, 1440), (1130, 1980), (-50, 1980)]), paint_of("#8a8a5a"))
    for k in range(9):
        c.drawLine(-60 + k * 160, 1980, 140 + k * 120, 1480, paint_of("#5a6a4a", 0.7, stroke=8))
    # 窗与晨光
    win = skia.Rect.MakeLTRB(60, 300, 330, 900)
    texture(c, noise_img(112, 24, "#a8c0d8", "#d8e4e8", "#c8d0e0"), rect=win)
    c.drawRect(win, paint_of("#4a3a3a", 0.95, stroke=24))
    c.drawLine(195, 300, 195, 900, paint_of("#4a3a3a", 0.95, stroke=14))
    band = smooth([(330, 360), (330, 880), (1130, 1500), (1130, 1180)])
    c.drawPath(band, paint_of(shader=linear((330, 600), (1100, 1300), [("#e8ecf0", 0.55), ("#f0d8a0", 0.15)]),
                              blend=skia.BlendMode.kScreen))
    # 床（木框 + 被子）
    c.drawPath(smooth([(560, 1180), (1130, 1150), (1130, 1560), (600, 1560)]), paint_of(OCHRE))
    c.drawPath(smooth([(560, 1120), (1130, 1080), (1130, 1300), (580, 1330)]), paint_of("#b8584a"))
    c.drawPath(smooth([(560, 1120), (1130, 1080), (1130, 1300), (580, 1330)]), paint_of(PRUSSIAN, 0.8, stroke=10))
    c.drawRoundRect(skia.Rect.MakeLTRB(700, 1150, 820, 1200), 10, 10, paint_of("#1a1a24"))
    # 人：坐在床沿，身体朝左，头转向右下看床上的手机
    leg = "#2a3046"
    c.drawLine(560, 1270, 340, 1290, paint_of(leg, stroke=120))
    c.drawLine(330, 1290, 320, 1560, paint_of(leg, stroke=95))
    c.drawPath(smooth([(250, 1540), (360, 1530), (370, 1590), (240, 1595)]), paint_of("#1a1a24"))
    body = smooth([(450, 940), (600, 950), (650, 1150), (640, 1300), (450, 1310), (420, 1120)])
    c.drawPath(body, paint_of(shader=linear((330, 1000), (650, 1200), ["#9aa8c8", "#3a4258"])))
    c.drawPath(body, paint_of(PRUSSIAN, 0.9, stroke=10))
    c.drawLine(470, 1010, 400, 1230, paint_of("#4a5270", stroke=70))
    c.drawPath(ellipse(390, 1250, 48, 36), paint_of("#c8a088"))
    head_profile(c, 545, 830, 300, rot=0.42, light=("#e0e4ea", "#b89a88"), shadow="#4a4a68", facing=1,
                 beard=0.3, eye=0.6, light_dir=-1)
    c.restore()
    return pt.swirl_field(t, 29, scale=110), 0.5, dist_weight(500, 830, 180)


# ---------------------------------------------------------------- 镜头 12：空出的位置

def s12_empty(c, t, d):
    prisoners_row(c, t + 5.0, empty=2, zoom=1.03)
    darken(c, ease_in_out(clamp01((t - (d - 1.4)) / 1.3)) * 0.92)
    return pt.swirl_field(t, 5), 0.55, None


SCENES = [s1_phone, s2_fire, s3_backs, s4_shadows, s5_turn, s6_glare, s7_exit, s8_reflect, s9_passage,
          s10_faces, s11_dawn, s12_empty]
