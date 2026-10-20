"""罗杰斯系列的专用元件：面对面的两把椅子、地窖里发芽的土豆、自我与经验的两圆、真实自我与理想自我、
带条件的爱心、耳朵、两双脚印、录音机等。在阿德勒系列的纸片剪影元件（adler.kit）之上组合，坐标以元素中心为原点。"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

SAGE = "#5F8A72"
CLAY = "#B5694A"
DUSK = "#4E6A8F"
WARM = "#E8C9A0"

GROUND_Y = 1130


def ground(g):
    K.ground(g.c, GROUND_Y)


def chair(c, x, y, s, face=1, color=CLAY, alpha=1.0):
    """单人扶手椅（侧面），(x, y) 为椅脚着地中点，face=1 朝右。"""
    with K.at(c, x, y, 0, face, 1):
        K.rr(c, 0, -s * 0.28, s * 0.62, s * 0.16, s * 0.05, color, alpha)
        K.rr(c, -s * 0.28, -s * 0.55, s * 0.14, s * 0.62, s * 0.06, K.mix(color, K.DARK, 0.15), alpha)
        K.rr(c, s * 0.02, -s * 0.4, s * 0.5, s * 0.08, s * 0.04, K.mix(color, K.DARK, 0.25), alpha)
        for dx in (-0.26, 0.26):
            K.seg(c, s * dx, -s * 0.2, s * dx, 0, K.mix(color, K.DARK, 0.5), s * 0.04, alpha)


def two_chairs(c, g, el_t, d):
    """咨询情境：两把椅子面对面，各坐一人；d['lean'] 为咨询师身体前倾的程度。"""
    s = d.get("s", 360)
    gap = d.get("gap", 380)
    chair(c, -gap / 2, 0, s, 1)
    chair(c, gap / 2, 0, s, -1, K.mix(CLAY, K.GOLD, 0.35))
    K.figure(c, -gap / 2 + 20, -s * 0.3, s * 0.82, "sit", d.get("left_color", "#6A5A4A"), K.SKIN, 1, 1,
             d.get("left_mood", "calm"), "short")
    K.figure(c, gap / 2 - 20, -s * 0.3, s * 0.82, d.get("right_pose", "sit"), d.get("right_color", K.HERO), K.SKIN, 1, -1,
             d.get("right_mood", "calm"), d.get("right_hair", "bun"))


def potato(c, x, y, s, sprout=0.0, alpha=1.0, toward=(1.0, -1.0)):
    """地窖里的土豆：sprout 为芽伸长的程度，芽朝 toward 方向（光的方向）弯过去。"""
    path = skia.Path()
    path.addOval(skia.Rect.MakeXYWH(x - s * 0.5, y - s * 0.32, s, s * 0.64))
    c.drawPath(path, K.paint("#B08A5A", alpha))
    c.drawPath(path, K.paint(K.mix("#B08A5A", K.DARK, 0.4), alpha, s * 0.025))
    for dx, dy in ((-0.2, -0.05), (0.15, 0.08), (0.05, -0.15)):
        K.dot(c, x + dx * s, y + dy * s, s * 0.03, K.mix("#B08A5A", K.DARK, 0.5), alpha)
    if sprout > 0:
        p = skia.Path()
        x0, y0 = x + s * 0.2, y - s * 0.25
        tx, ty = toward
        L = s * 2.6 * sprout
        p.moveTo(x0, y0)
        p.quadTo(x0, y0 - L * 0.6, x0 + tx * L * 0.7, y0 + ty * L * 0.75)
        c.drawPath(p, K.paint("#E9E4C8", alpha, s * 0.05))
        K.dot(c, x0 + tx * L * 0.7, y0 + ty * L * 0.75, s * 0.05, "#D8E2A8", alpha)


def basement(c, g, el_t, d):
    """地窖：昏暗的墙、右上角一扇小窗透进一束光、地上一只土豆慢慢发芽。"""
    k = d.get("sprout", 1.0)
    k = k(g, el_t) if callable(k) else k
    K.rr(c, 0, 0, 900, 820, 20, K.mix(K.DARK, K.BG, 0.25))
    K.rr(c, 300, -300, 150, 100, 8, "#F2E6B8")
    K.rr_stroke(c, 300, -300, 150, 100, 8, K.INK, 6)
    K.seg(c, 300, -350, 300, -250, K.INK, 4)
    beam = skia.Path()
    beam.moveTo(230, -250)
    beam.lineTo(370, -250)
    beam.lineTo(-40, 330)
    beam.lineTo(-300, 330)
    beam.close()
    c.drawPath(beam, K.paint("#F2E6B8", 0.22))
    K.rr(c, 0, 360, 900, 100, 0, K.mix("#8A6A4A", K.DARK, 0.3))
    potato(c, -260, 270, 150, k, 1, (1.0, -1.05))


def self_circles(c, x, y, r, overlap=0.3, labels=("自我概念", "真实经验"), alpha=1.0, colors=(DUSK, CLAY), center="一致"):
    """罗杰斯的两圆示意：左圆为自我概念，右圆为真实经验；overlap 0→1 表示一致的程度。"""
    d = lerp(r * 1.9, r * 0.2, overlap)
    for i, sx in enumerate((-1, 1)):
        K.dot(c, x + sx * d / 2, y, r, colors[i], 0.45 * alpha)
        K.ring(c, x + sx * d / 2, y, r, colors[i], 6, alpha)
        if labels:
            K.text(c, labels[i], x + sx * (d / 2 + r * 0.35), y - r - 40, 34, "serif_black", colors[i], alpha)
    if center and overlap > 0.05:
        K.text(c, center, x, y, 36, "serif_black", K.PAPER, alpha * clamp01(overlap * 2))


def circles(c, g, el_t, d):
    """两圆元素：d['ov'] 为 (起, 止)，从 d['b1'] 拍起 1.2 秒内变化。"""
    a, b = d.get("ov", (0.3, 0.3))
    k = ease_in_out(clamp01(g.since(d.get("b1", 0)) / 1.2))
    self_circles(c, 0, 0, d.get("r", 220), lerp(a, b, k), d.get("labels", ("自我概念", "真实经验")), center=d.get("center", "一致"))


def ideal_gap(c, g, el_t, d):
    """真实自我（实线人形）与理想自我（虚线人形），gap 0→1 为距离。"""
    gap = d.get("gap", 1.0)
    gap = gap(g, el_t) if callable(gap) else gap
    s = d.get("s", 340)
    dx = lerp(0, 230, gap)
    K.figure(c, -dx, 0, s, "stand", K.HERO, K.SKIN, 1, 1, d.get("mood", "calm"), "short")
    K.figure(c, dx, 0, s * 1.05, "proud", K.GOLD, K.mix(K.GOLD, K.PAPER, 0.5), 0.45, -1, "smile", "short")
    if d.get("labels", True):
        K.text(c, "真实自我", -dx, -s * 1.24, 32, "serif_black", K.HERO)
        K.text(c, "理想自我", dx, -s * 1.28, 32, "serif_black", K.mix(K.GOLD, K.DARK, 0.3))


def tag_heart(c, x, y, s, cond="考第一", alpha=1.0, swing=0.0):
    """带价签的爱心：条件写在价签上，价签用细线拴在爱心右上角。"""
    K.heart(c, x, y, s, K.RED, alpha)
    ax, ay = x + s * 0.3, y - s * 0.3
    w = K.text_w(cond, 34, "serif_black") + 44
    with K.at(c, ax, ay, -20 + swing):
        K.seg(c, 0, 0, s * 0.35, 0, K.INK2, 3, alpha)
        K.rr(c, s * 0.35 + w / 2, 0, w, 60, 10, K.PAPER, alpha)
        K.rr_stroke(c, s * 0.35 + w / 2, 0, w, 60, 10, K.INK2, 3, alpha)
        K.dot(c, s * 0.35 + 14, 0, 5, K.INK2, alpha)
        K.text(c, cond, s * 0.35 + w / 2 + 6, 0, 34, "serif_black", K.INK, alpha)


def ear(c, x, y, s, color=SAGE, alpha=1.0, waves=0.0, t=0.0):
    """耳朵（倾听），waves>0 时左侧有声波。"""
    with K.at(c, x, y):
        p = skia.Path()
        p.moveTo(-s * 0.15, s * 0.45)
        p.cubicTo(-s * 0.55, s * 0.3, -s * 0.45, -s * 0.55, 0, -s * 0.5)
        p.cubicTo(s * 0.45, -s * 0.45, s * 0.42, 0, s * 0.12, s * 0.1)
        p.cubicTo(-s * 0.05, s * 0.2, s * 0.05, s * 0.45, -s * 0.15, s * 0.45)
        c.drawPath(p, K.paint(K.SKIN, alpha))
        c.drawPath(p, K.paint(color, alpha, s * 0.05))
        q = skia.Path()
        q.moveTo(-s * 0.1, s * 0.15)
        q.cubicTo(-s * 0.25, -s * 0.15, s * 0.15, -s * 0.35, s * 0.15, -s * 0.1)
        c.drawPath(q, K.paint(color, alpha, s * 0.035))
    if waves > 0:
        for i in range(3):
            ph = (t * 1.2 + i / 3) % 1
            K.ring(c, x - s * 0.7, y, s * (0.25 + 0.5 * ph), color, s * 0.025, alpha * waves * (1 - ph), 0.25, 135)


def footprints(c, x, y, s, k=1.0, alpha=1.0, color=K.INK2):
    """一串脚印（“设身处地”），k 为出现进度。"""
    for i in range(6):
        q = clamp01(k * 6 - i)
        if q <= 0:
            continue
        sx = -1 if i % 2 else 1
        with K.at(c, x - s * 1.2 + i * s * 0.48, y + sx * s * 0.14, 90):
            path = skia.Path()
            path.addOval(skia.Rect.MakeXYWH(-s * 0.09, -s * 0.16, s * 0.18, s * 0.3))
            c.drawPath(path, K.paint(color, alpha * q))
            K.dot(c, 0, -s * 0.22, s * 0.05, color, alpha * q)


def recorder(c, x, y, s, t=0.0, run=True, alpha=1.0):
    """开盘式录音机：两只转动的磁带盘。"""
    K.rr(c, x, y, s * 1.4, s * 0.8, s * 0.06, K.mix(K.DARK, K.BG, 0.2), alpha)
    for dx in (-0.35, 0.35):
        cx = x + dx * s
        cy = y - s * 0.08
        K.dot(c, cx, cy, s * 0.26, K.PAPER, alpha)
        K.ring(c, cx, cy, s * 0.26, K.INK, s * 0.03, alpha)
        a0 = t * 3 if run else 0
        for k in range(3):
            a = a0 + k * math.tau / 3
            K.seg(c, cx, cy, cx + math.cos(a) * s * 0.2, cy + math.sin(a) * s * 0.2, K.INK2, s * 0.03, alpha)
        K.dot(c, cx, cy, s * 0.05, K.INK, alpha)
    K.seg(c, x - s * 0.35, y + s * 0.18, x + s * 0.35, y + s * 0.18, K.INK3, s * 0.03, alpha)
    K.dot(c, x + s * 0.55, y + s * 0.28, s * 0.05, K.RED if run else K.INK3, alpha)
