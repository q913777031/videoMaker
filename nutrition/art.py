"""《动物为什么吃不胖》系列的专用元件：营养几何图（坐标轴、目标点、食物轨道、沿轨道吃进去的点）、
原创动物剪影（蝗虫、黏菌、猫、狒狒、大猩猩、小鼠、摩门蟋蟀）、餐盘、营养条、零食袋、杠杆。
在阿德勒系列的纸片剪影元件（adler.kit）之上组合，坐标以元素中心为原点。"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

PROTEIN = "#C0504D"   # 蛋白质：红
CARB = "#E3A33B"      # 碳水：金
FAT = "#5E8FA8"       # 脂肪：蓝
SALT = "#9AA3AE"
CALCIUM = "#E9E4D6"
LEAF = "#5E8C3A"

GROUND_Y = 1130


def ground(g):
    K.ground(g.c, GROUND_Y)


# ---------------------------------------------------------------- 营养几何图

def geo(c, g, el_t, d):
    """营养几何图：横轴碳水、纵轴蛋白质（0–1 单位），原点在左下。
    d 可含：size 轴长；target (x, y) 与 t_at 目标点出现的拍；rails [(斜率, 颜色, 名称, 出现拍)]；
    dots [(轨道序号, 起拍, 终点 x, 用几拍走完)]；gaps [(点 x, 点 y, 出现拍)] 画出点到目标的虚线差距；
    zig 混合两条轨道走向目标的折线 (起拍, 段数)。"""
    S = d.get("size", 620)
    ox, oy = -S / 2, S / 2

    def P(x, y):
        return ox + x * S, oy - y * S

    k = ease_out(clamp01(el_t / 0.6))
    K.seg(c, ox, oy, ox + S * k, oy, K.INK, 6)
    K.seg(c, ox, oy, ox, oy - S * k, K.INK, 6)
    K.poly(c, [(ox + S + 4, oy), (ox + S - 22, oy - 12), (ox + S - 22, oy + 12)], K.INK, k)
    K.poly(c, [(ox, oy - S - 4), (ox - 12, oy - S + 22), (ox + 12, oy - S + 22)], K.INK, k)
    K.text(c, "碳水 →", ox + S - 40, oy + 50, 34, "serif_black", CARB, k)
    K.text(c, "↑ 蛋白质", ox + 60, oy - S - 40, 34, "serif_black", PROTEIN, k)
    for i, (slope, col, name, at) in enumerate(d.get("rails", ())):
        q = ease_out(clamp01(g.since(at) / 0.8))
        if q <= 0:
            continue
        x1 = min(1.0, 1.0 / slope) if slope > 0 else 1.0
        y1 = slope * x1
        ax, ay = P(0, 0)
        bx, by = P(x1 * q, y1 * q)
        K.seg(c, ax, ay, bx, by, col, 10, 0.85)
        lx, ly = P(x1 * 0.92, y1 * 0.92)
        K.text(c, name, lx + 40, ly - 24, 30, "sans_medium", col, q)
    t = d.get("target")
    if t is not None and g.since(d.get("t_at", 0)) >= 0:
        q = ease_out(clamp01(g.since(d.get("t_at", 0)) / 0.5))
        tx, ty = P(*t)
        K.spotlight(c, tx, ty, 70, K.GOLD, 0.45 * q)
        K.star(c, tx, ty, 30 * q, K.GOLD, 1, 5, 0.45)
        K.ring(c, tx, ty, 44 * q, K.INK, 4, q)
        if d.get("t_label", True):
            K.text(c, "目标", tx + 62, ty - 40, 32, "serif_black", K.INK, q)
    rails = d.get("rails", ())
    for ri, b0, xend, nb in d.get("dots", ()):
        if g.since(b0) < 0:
            continue
        slope, col = rails[ri][0], rails[ri][1]
        p = ease_in_out(clamp01((g.t - g.b(b0)) / max(0.1, g.b(b0 + nb) - g.b(b0))))
        x = xend * p
        px, py = P(x, slope * x)
        K.dot(c, px, py, 18, col)
        K.ring(c, px, py, 18, K.INK, 4)
    for gx, gy, at in d.get("gaps", ()):
        q = clamp01(g.since(at) / 0.4)
        if q <= 0 or t is None:
            continue
        ax, ay = P(gx, gy)
        bx, by = P(*t)
        c.save()
        p = K.paint(K.RED, q, 5)
        p.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
        c.drawLine(ax, ay, bx, by, p)
        c.restore()
    if d.get("zig") and t is not None:
        b0, n = d["zig"]
        p = clamp01((g.t - g.b(b0)) / max(0.1, g.b(b0 + 6) - g.b(b0)))
        pts = [(0.0, 0.0)]
        for i in range(n):
            x0, y0 = pts[-1]
            frac = (i + 1) / n
            tx_, ty_ = t[0] * frac, t[1] * frac
            pts.append((tx_ + (0.06 if i % 2 == 0 else -0.06), ty_ + (-0.06 if i % 2 == 0 else 0.06)) if i < n - 1 else (tx_, ty_))
        m = p * (len(pts) - 1)
        for i in range(int(m)):
            a, b = P(*pts[i]), P(*pts[i + 1])
            K.seg(c, a[0], a[1], b[0], b[1], K.GREEN, 7)
        if m < len(pts) - 1:
            i = int(m)
            a, b = P(*pts[i]), P(*pts[i + 1])
            fr = m - i
            K.seg(c, a[0], a[1], lerp(a[0], b[0], fr), lerp(a[1], b[1], fr), K.GREEN, 7)


# ---------------------------------------------------------------- 动物（原创剪影）

def locust(c, x, y, s, t=0.0, alpha=1.0, color=LEAF, face=1):
    """蝗虫：长身、大后腿、两根触角；(x, y) 为身体中心，s 为体长。"""
    with K.at(c, x, y, 0, face, 1):
        kick = math.sin(t * 6) * 0.04
        K.seg(c, -s * 0.05, s * 0.02, -s * 0.32, -s * 0.22, K.mix(color, K.DARK, 0.3), s * 0.06, alpha)
        K.seg(c, -s * 0.32, -s * 0.22, -s * 0.5, s * (0.16 + kick), K.mix(color, K.DARK, 0.3), s * 0.04, alpha)
        path = skia.Path()
        path.addOval(skia.Rect.MakeXYWH(-s * 0.45, -s * 0.12, s * 0.8, s * 0.24))
        c.drawPath(path, K.paint(color, alpha))
        K.dot(c, s * 0.38, -s * 0.04, s * 0.11, K.mix(color, K.DARK, 0.15), alpha)
        K.dot(c, s * 0.42, -s * 0.07, s * 0.035, K.INK, alpha)
        for dx in (0.1, 0.22):
            K.seg(c, s * dx, s * 0.08, s * (dx + 0.06), s * 0.24, K.mix(color, K.DARK, 0.3), s * 0.025, alpha)
        K.seg(c, s * 0.44, -s * 0.12, s * 0.62, -s * 0.42, K.INK2, s * 0.018, alpha)
        K.seg(c, s * 0.4, -s * 0.13, s * 0.52, -s * 0.46, K.INK2, s * 0.018, alpha)
        K.poly(c, [(-s * 0.2, -s * 0.1), (s * 0.2, -s * 0.13), (-s * 0.35, -s * 0.02)], K.mix(color, K.PAPER, 0.35), alpha * 0.9)


def cricket(c, x, y, s, t=0.0, alpha=1.0, face=1):
    """摩门蟋蟀：短胖、深褐、长触角。"""
    col = "#6B4A33"
    with K.at(c, x, y + math.sin(t * 8) * s * 0.02, 0, face, 1):
        path = skia.Path()
        path.addOval(skia.Rect.MakeXYWH(-s * 0.4, -s * 0.18, s * 0.75, s * 0.36))
        c.drawPath(path, K.paint(col, alpha))
        K.dot(c, s * 0.35, -s * 0.05, s * 0.14, K.mix(col, K.DARK, 0.2), alpha)
        K.dot(c, s * 0.4, -s * 0.09, s * 0.035, K.PAPER, alpha)
        K.seg(c, s * 0.42, -s * 0.15, s * 0.9, -s * 0.55, K.INK2, s * 0.015, alpha)
        K.seg(c, s * 0.38, -s * 0.16, s * 0.75, -s * 0.62, K.INK2, s * 0.015, alpha)
        for dx in (-0.25, -0.05, 0.15):
            K.seg(c, s * dx, s * 0.12, s * (dx - 0.08), s * 0.3, K.mix(col, K.DARK, 0.3), s * 0.03, alpha)


def slime(c, x, y, s, p=1.0, t=0.0, alpha=1.0, toward=None):
    """黏菌：黄色网状菌体，p 为扩展进度；toward=(dx, dy) 时主脉伸向该方向。"""
    col = "#E8C547"
    K.dot(c, x, y, s * 0.22 * (0.6 + 0.4 * p), col, alpha)
    n = 9
    for i in range(n):
        a = i / n * math.tau + 0.3
        L = s * (0.35 + 0.25 * math.sin(i * 1.7)) * p
        if toward is not None:
            ta = math.atan2(toward[1], toward[0])
            boost = max(0.0, math.cos(a - ta))
            L *= 0.6 + 1.6 * boost
        ex, ey = x + math.cos(a) * L, y + math.sin(a) * L
        K.seg(c, x, y, ex, ey, col, s * 0.05, alpha)
        K.seg(c, ex, ey, ex + math.cos(a + 0.6) * L * 0.35, ey + math.sin(a + 0.6) * L * 0.35, col, s * 0.03, alpha)
        K.dot(c, ex, ey, s * 0.04, col, alpha)


def cat(c, x, y, s, alpha=1.0, color="#D98C4A", face=1, t=0.0):
    """坐着的猫：(x, y) 为脚底中点，s 为高度。"""
    with K.at(c, x, y, 0, face, 1):
        tail = math.sin(t * 2.5) * 0.08
        K.seg(c, -s * 0.22, -s * 0.08, -s * (0.48 + tail), -s * 0.4, color, s * 0.07, alpha)
        path = skia.Path()
        path.addOval(skia.Rect.MakeXYWH(-s * 0.3, -s * 0.62, s * 0.56, s * 0.62))
        c.drawPath(path, K.paint(color, alpha))
        K.dot(c, s * 0.04, -s * 0.74, s * 0.2, color, alpha)
        K.poly(c, [(-s * 0.12, -s * 0.86), (-s * 0.06, -s * 1.02), (s * 0.02, -s * 0.9)], color, alpha)
        K.poly(c, [(s * 0.08, -s * 0.9), (s * 0.16, -s * 1.02), (s * 0.2, -s * 0.84)], color, alpha)
        K.dot(c, s * 0.0, -s * 0.76, s * 0.025, K.INK, alpha)
        K.dot(c, s * 0.12, -s * 0.76, s * 0.025, K.INK, alpha)
        K.dot(c, s * 0.06, -s * 0.7, s * 0.02, "#B5534E", alpha)
        for dx in (-0.12, 0.1):
            K.rr(c, s * dx, -s * 0.03, s * 0.09, s * 0.06, s * 0.03, K.mix(color, K.PAPER, 0.4), alpha)


def baboon(c, x, y, s, alpha=1.0, face=1, t=0.0):
    """狒狒：四足侧影，长口鼻，尾巴上翘；(x, y) 为脚底中点，s 为身长。"""
    col = "#8A7A5E"
    with K.at(c, x, y, 0, face, 1):
        K.rr(c, 0, -s * 0.42, s * 0.75, s * 0.32, s * 0.15, col, alpha)
        for dx in (-0.3, -0.18, 0.2, 0.3):
            K.seg(c, s * dx, -s * 0.3, s * dx, 0, K.mix(col, K.DARK, 0.25), s * 0.06, alpha)
        K.seg(c, -s * 0.36, -s * 0.5, -s * 0.55, -s * (0.72 + math.sin(t * 2) * 0.03), col, s * 0.05, alpha)
        K.dot(c, s * 0.42, -s * 0.58, s * 0.15, col, alpha)
        K.rr(c, s * 0.58, -s * 0.54, s * 0.18, s * 0.11, s * 0.05, "#C9B39A", alpha)
        K.dot(c, s * 0.44, -s * 0.64, s * 0.025, K.INK, alpha)


def gorilla(c, x, y, s, alpha=1.0, face=1):
    """大猩猩：宽肩、驼背、指关节着地；(x, y) 为脚底中点，s 为高度。"""
    col = "#3E3A3C"
    with K.at(c, x, y, 0, face, 1):
        K.poly(c, [(-s * 0.4, 0), (-s * 0.45, -s * 0.55), (-s * 0.1, -s * 0.85), (s * 0.35, -s * 0.7), (s * 0.45, -s * 0.2), (s * 0.4, 0)], col, alpha)
        K.dot(c, s * 0.3, -s * 0.82, s * 0.17, col, alpha)
        K.rr(c, s * 0.38, -s * 0.78, s * 0.16, s * 0.14, s * 0.05, "#5E5658", alpha)
        K.dot(c, s * 0.34, -s * 0.86, s * 0.025, K.PAPER, alpha)
        K.seg(c, s * 0.38, -s * 0.5, s * 0.55, 0, col, s * 0.12, alpha)
        K.seg(c, -s * 0.3, -s * 0.3, -s * 0.32, 0, col, s * 0.14, alpha)


def mouse(c, x, y, s, alpha=1.0, color="#B8B2AA", face=1, t=0.0):
    """小鼠：圆身、大圆耳、细长尾；(x, y) 为脚底中点，s 为身长。"""
    with K.at(c, x, y, 0, face, 1):
        p = skia.Path()
        p.moveTo(-s * 0.35, -s * 0.12)
        p.quadTo(-s * 0.7, -s * 0.05 + math.sin(t * 3) * s * 0.05, -s * 0.85, -s * 0.25)
        c.drawPath(p, K.paint("#D9A3A0", alpha, s * 0.03))
        path = skia.Path()
        path.addOval(skia.Rect.MakeXYWH(-s * 0.4, -s * 0.42, s * 0.75, s * 0.42))
        c.drawPath(path, K.paint(color, alpha))
        K.dot(c, s * 0.28, -s * 0.3, s * 0.17, color, alpha)
        K.dot(c, s * 0.18, -s * 0.48, s * 0.12, K.mix(color, "#E9B5B0", 0.5), alpha)
        K.dot(c, s * 0.38, -s * 0.32, s * 0.03, K.INK, alpha)
        K.dot(c, s * 0.46, -s * 0.26, s * 0.025, "#D9736E", alpha)


# ---------------------------------------------------------------- 餐盘、营养条、零食、杠杆

def plate(c, x, y, r, parts=(0.2, 0.5, 0.3), alpha=1.0, p=1.0):
    """餐盘饼图：parts 为（蛋白质、碳水、脂肪）占比，p 为画出进度。"""
    K.dot(c, x, y, r * 1.18, K.PAPER, alpha)
    K.ring(c, x, y, r * 1.18, K.LINE, 6, alpha)
    a0 = -90.0
    rect = skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r)
    for v, col in zip(parts, (PROTEIN, CARB, FAT)):
        sweep = 360 * v * p
        path = skia.Path()
        path.moveTo(x, y)
        path.arcTo(rect, a0, sweep, False)
        path.close()
        c.drawPath(path, K.paint(col, alpha))
        a0 += sweep


def nbar(c, x, y, w, h, v, color, label=None, alpha=1.0, target=None):
    """横向营养条：v 为 0–1，target 处画一条目标刻度。"""
    K.rr(c, x, y, w, h, h / 2, K.LINE, alpha)
    if v > 0:
        K.rr(c, x - w / 2 + w * min(v, 1) / 2, y, w * min(v, 1), h, h / 2, color, alpha)
    if target is not None:
        tx = x - w / 2 + w * target
        K.seg(c, tx, y - h * 0.9, tx, y + h * 0.9, K.INK, 5, alpha)
    if label:
        K.text(c, label, x - w / 2 - 24, y, 34, "serif_black", K.INK, alpha, align="right")


def chips(c, x, y, s, alpha=1.0, color="#D9593A"):
    """零食袋：锯齿封口的长方袋子 + 一圈薯片。"""
    K.rr(c, x, y, s * 0.7, s, s * 0.06, color, alpha)
    for i in range(7):
        xx = x - s * 0.35 + i * s * 0.1
        K.poly(c, [(xx, y - s * 0.5), (xx + s * 0.05, y - s * 0.56), (xx + s * 0.1, y - s * 0.5)], color, alpha)
    K.dot(c, x, y + s * 0.05, s * 0.2, CARB, alpha)
    K.rr(c, x, y - s * 0.28, s * 0.5, s * 0.1, s * 0.03, K.PAPER, alpha * 0.85)


def soda(c, x, y, s, alpha=1.0, color="#3B6E8C"):
    """易拉罐。"""
    K.rr(c, x, y, s * 0.45, s, s * 0.08, color, alpha)
    K.rr(c, x, y - s * 0.52, s * 0.36, s * 0.06, s * 0.02, "#B9C2CC", alpha)
    K.rr(c, x, y, s * 0.45, s * 0.18, 0, K.PAPER, alpha * 0.8)


def lever(c, x, y, w, tilt=0.0, alpha=1.0, small=PROTEIN, big=CARB):
    """杠杆：支点靠近一端，短臂上一小块蛋白质、长臂上一大块碳水 / 脂肪；tilt 为倾斜角（度）。"""
    K.poly(c, [(x - 40, y + 80), (x + 40, y + 80), (x, y)], K.INK2, alpha)
    with K.at(c, x, y, tilt):
        K.rr(c, w * 0.2, 0, w * 1.3, 14, 7, K.mix(K.GOLD, K.DARK, 0.4), alpha)
        K.rr(c, -w * 0.38, -40, 60, 60, 10, small, alpha)
        K.text(c, "蛋白质", -w * 0.38, -110, 32, "serif_black", small, alpha)
        K.rr(c, w * 0.7, -70, 170, 120, 14, big, alpha)
        K.text(c, "碳水 + 脂肪", w * 0.7, -170, 32, "serif_black", K.mix(big, K.DARK, 0.3), alpha)


def gauge_row(c, g, el_t, d):
    """五种食欲：五根竖条依次出现，d['vals'] 为当前满足度，d['hi'] 高亮一根。"""
    names = ("蛋白质", "碳水", "脂肪", "钠", "钙")
    cols = (PROTEIN, CARB, FAT, SALT, "#C9BFA8")
    vals = d.get("vals", (0.6, 0.8, 0.7, 0.4, 0.5))
    for i in range(5):
        k = ease_out(clamp01(g.since(d.get("b0", 0) + i * 0.5) / 0.5))
        if k <= 0:
            continue
        x = -360 + i * 180
        h = 360
        K.rr(c, x, 0, 70, h, 20, K.LINE, k)
        v = vals[i] * k
        K.rr(c, x, h / 2 - h * v / 2, 70, h * v, 20, cols[i], k)
        if d.get("hi") == i:
            K.rr_stroke(c, x, 0, 92, h + 22, 26, K.GOLD, 7, k)
        K.text(c, names[i], x, h / 2 + 50, 34, "serif_black", K.INK, k)
