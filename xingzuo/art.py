"""《十二星座》系列的专用元件：火苗、星座符号（♈ 等字体里没有，自己画）、小羊头像、白羊座星群。
上班族日常元件（手机聊天、地面）复用 scarcity.art。坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_out
from scarcity.art import GROUND_Y, ground, phone_chat  # noqa: F401

FIRE = ("#E04A2A", "#F2A33A", "#FFE08A")
HORN = "#D9924A"
FACE = "#F3E2CB"
WOOL = "#FBF7F0"


# ---------------------------------------------------------------- 火苗

def flame_path(w: float, h: float, lean: float = 0.0) -> skia.Path:
    """一片火苗：尖端在 (lean, -h)，底部圆弧最低点约在 +0.54h。"""
    p = skia.Path()
    p.moveTo(lean, -h)
    p.cubicTo(w * 0.25, -h * 0.55, w, -h * 0.05, w * 0.7, h * 0.3)
    p.cubicTo(w * 0.45, h * 0.62, -w * 0.45, h * 0.62, -w * 0.7, h * 0.3)
    p.cubicTo(-w, -h * 0.05, -w * 0.25, -h * 0.55, lean, -h)
    p.close()
    return p


def fire(c, x, y, s, t, alpha=1.0, glow=True, pulse=0.0):
    """三层叠色火苗，随时间摇曳；s 为整体高度，(x, y) 为视觉中心。"""
    if alpha <= 0:
        return
    h, w = s * 0.5, s * 0.34
    with K.at(c, x, y + h * 0.23):
        if glow:
            fx.glow(c, 0, -h * 0.1, s * 1.1, FIRE[1], (0.28 + 0.14 * pulse) * alpha)
        for i, (k, col) in enumerate(zip((1.0, 0.64, 0.34), FIRE)):
            lean = math.sin(t * 8.5 + i * 1.4) * w * 0.35 * k
            hk = h * k * (1 + 0.08 * math.sin(t * 12.5 + i * 0.9))
            path = flame_path(w * k, hk, lean)
            path.offset(0, 0.54 * h * (1 - k))
            c.drawPath(path, K.paint(col, alpha))


def flame(c, g, el_t, d):
    """火苗元素：s 为高度。"""
    fire(c, 0, 0, d.get("s", 150), g.t, 1.0, d.get("glow", True), g.pulse(5))


# ---------------------------------------------------------------- 星座符号

def glyph_path(sign: str, s: float) -> skia.Path:
    """星座符号的描边路径（以中心为原点，高约 s）。目前实现：白羊座 ♈、金牛座 ♉。"""
    p = skia.Path()
    if sign == "aries":
        for side in (-1, 1):
            p.moveTo(0, s * 0.5)
            p.cubicTo(0, -s * 0.05, side * s * 0.08, -s * 0.48, side * s * 0.34, -s * 0.5)
            p.cubicTo(side * s * 0.56, -s * 0.5, side * s * 0.62, -s * 0.2, side * s * 0.5, -s * 0.04)
    elif sign == "taurus":
        p.addCircle(0, s * 0.18, s * 0.3)
        p.moveTo(-s * 0.42, -s * 0.5)
        p.cubicTo(-s * 0.42, -s * 0.2, -s * 0.2, -s * 0.12, 0, -s * 0.12)
        p.cubicTo(s * 0.2, -s * 0.12, s * 0.42, -s * 0.2, s * 0.42, -s * 0.5)
    return p


def glyph(c, g, el_t, d):
    """星座符号元素：sign 为英文键，s 为高度，color 默认强调色。"""
    s = d.get("s", 120)
    col = d.get("color") or g.acc
    with K.paper(c, 1.0, 0.8, skia.Rect.MakeLTRB(-s, -s, s, s)):
        c.drawPath(glyph_path(d.get("sign", "aries"), s), K.paint(col, 1.0, stroke=s * d.get("width", 0.14)))


# ---------------------------------------------------------------- 小羊头像

def ram_head(c, x, y, s, alpha=1.0, mood="happy", t=0.0, horn=HORN, face=FACE, wool=WOOL):
    """小羊头像：卷角 + 绒毛 + 圆脸；s 为脸的直径，(x, y) 为脸心。"""
    if alpha <= 0:
        return
    r = s / 2
    with K.at(c, x, y + 0.02 * r * math.sin(t * 2.4)):
        with K.paper(c, alpha, 0.8, skia.Rect.MakeLTRB(-s * 1.3, -s * 1.3, s * 1.3, s * 1.3)):
            for side in (-1, 1):
                p = skia.Path()
                cx, cy = side * r * 0.92, -r * 0.28
                for i in range(49):
                    k = i / 48
                    th = math.radians(-115 + 250 * k)
                    rad = r * (0.52 - 0.36 * k)
                    px, py = cx + side * rad * math.cos(th), cy + rad * math.sin(th)
                    (p.moveTo if i == 0 else p.lineTo)(px, py)
                c.drawPath(p, K.paint(horn, 1, stroke=r * 0.26))
                c.drawPath(p, K.paint(K.shade(horn, 0.3), 1, stroke=r * 0.07))
            for i in range(9):
                a = math.radians(-165 + 150 * i / 8)
                K.dot(c, r * 0.86 * math.cos(a), r * 0.86 * math.sin(a) - r * 0.1, r * 0.3, wool)
            for side in (-1, 1):
                with K.at(c, side * r * 1.0, r * 0.08, side * 28):
                    c.drawOval(skia.Rect.MakeXYWH(-r * 0.32, -r * 0.16, r * 0.64, r * 0.32), K.paint(K.shade(face, 0.1)))
            K.dot(c, 0, 0, r, face)
            for sx in (-r * 0.36, r * 0.36):
                if mood == "happy":
                    path = skia.Path()
                    path.addArc(skia.Rect.MakeXYWH(sx - r * 0.13, -r * 0.2, r * 0.26, r * 0.22), 200, 140)
                    c.drawPath(path, K.paint(K.INK, 1, r * 0.07))
                else:
                    K.dot(c, sx, -r * 0.1, r * 0.09, K.INK)
            K.dot(c, -r * 0.6, r * 0.14, r * 0.11, K.RED, 0.25)
            K.dot(c, r * 0.6, r * 0.14, r * 0.11, K.RED, 0.25)
            K.poly(c, [(-r * 0.1, r * 0.3), (r * 0.1, r * 0.3), (0, r * 0.42)], K.shade(face, 0.35))
            path = skia.Path()
            path.addArc(skia.Rect.MakeXYWH(-r * 0.22, r * 0.34, r * 0.44, r * 0.26), 20, 140)
            c.drawPath(path, K.paint(K.INK, 1, r * 0.06))


def ram(c, g, el_t, d):
    """小羊头像元素：s 为脸的直径，glow=True 时带随拍呼吸的背光。"""
    s = d.get("s", 160)
    if d.get("glow"):
        fx.glow(c, 0, 0, s * 1.4, g.acc2, 0.3 + 0.15 * g.pulse(5))
    ram_head(c, 0, 0, s, 1.0, d.get("mood", "happy"), g.t)


# ---------------------------------------------------------------- 白羊座星群

# 41 Ari、娄宿三（Hamal, α）、娄宿一（Sheratan, β）、娄宿二（Mesarthim, γ）：按天球位置示意（东在左），亮度为示意
ARIES_STARS = [(-300, -130, 0.72), (-70, -20, 1.0), (150, 85, 0.85), (195, 140, 0.62)]


def constellation(c, g, el_t, d):
    """白羊座星群：第 i 颗星在 b0 + i*step 拍亮起（星光 + 光晕），星与星之间依次连线。"""
    b0, step, sc = d.get("b0", 0), d.get("step", 1), d.get("scale", 1.0)
    pts = [(x * sc, y * sc) for x, y, _ in ARIES_STARS]
    col = d.get("color") or g.acc2
    for i in range(1, len(pts)):
        k = ease_out(clamp01(g.since(b0 + i * step) / 0.35))
        K.seg(c, *pts[i - 1], *pts[i], col, 4, 0.75, k)
    for i, (x, y) in enumerate(pts):
        dt = g.since(b0 + i * step)
        if dt < 0:
            continue
        mag = ARIES_STARS[i][2]
        pop = 1 + 0.7 * math.exp(-dt * 5)
        fx.glow(c, x, y, 80 * mag * sc, col, 0.32)
        fx.sparkle(c, x, y, 24 * mag * sc * pop * (1 + 0.12 * math.sin(g.t * 6 + i)), col, 1.0, g.t * 20 + i * 30)
        K.dot(c, x, y, 7 * mag * sc, K.PAPER)
