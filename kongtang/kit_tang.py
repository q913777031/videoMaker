"""控糖系列的专用绘图元件：血糖曲线图、食物图标、餐盘、葡萄糖分子、血管与细胞。

沿用 adler.kit 的纸片风格；曲线图默认是示意（不带具体读数），需要真实数值的镜头在图上另标单位与出处。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

GLU = "#E8A33D"          # 葡萄糖颗粒
SPIKE = "#D9593A"        # 尖峰曲线
FLAT = "#4E9A6E"         # 平稳曲线
VEG = "#5E9A4E"
VEG2 = "#87B865"
BREAD = "#D9A55B"
RICE = "#F4EEDD"
MEAT = "#B8664A"
EGG = "#F6C744"
VESSEL = "#E9B3A8"


# ---------------------------------------------------------------- 血糖曲线

def bump(t: float, peak: float = 1.0, tp: float = 0.22, k: float = 2.2, dip: float = 0.0) -> float:
    """餐后血糖曲线的形状（0–1 横轴）：伽马型隆起，dip>0 时回落后略低于基线（“低谷”）。"""
    if t <= 0:
        return 0.0
    u = t / tp
    v = peak * (u ** k) * math.exp(k * (1 - u))
    if dip:
        v -= dip * math.exp(-((t - tp * 2.6) / (tp * 0.9)) ** 2)
    return v


def chart(c, x, y, w, h, curves, alpha=1.0, band=None, xlabel="饭后时间", ylabel="血糖", grid=True, demo=True):
    """曲线图：(x, y) 为图中心；curves 为 [(fn(t)->0..1, 颜色, 绘制进度 p, 线宽, 标签)]。

    band=(lo, hi) 以 0–1 纵轴比例画一条浅绿色“正常范围”带；demo=True 在右上角标“示意”。
    """
    x0, y0 = x - w / 2, y + h / 2
    with K.fade(c, alpha):
        with K.paper(c, 1, 0.9):
            K.rr(c, x, y, w + 80, h + 120, 26, K.PAPER)
        if band:
            lo, hi = band
            K.rr(c, x, y0 - h * (lo + hi) / 2, w, h * (hi - lo), 6, K.tint(FLAT, 0.75), 0.6)
        if grid:
            for i in range(1, 4):
                K.seg(c, x0, y0 - h * i / 4, x0 + w, y0 - h * i / 4, K.LINE, 2)
        K.seg(c, x0, y0, x0 + w, y0, K.INK3, 4)
        K.seg(c, x0, y0, x0, y0 - h, K.INK3, 4)
        K.text(c, xlabel, x0 + w, y0 + 34, 26, "sans_medium", K.INK3, 1, "right")
        K.text(c, ylabel, x0 + 8, y0 - h - 28, 26, "sans_medium", K.INK3, 1, "left")
        if demo:
            K.text(c, "示意", x0 + w, y0 - h - 28, 24, "sans_medium", K.INK3, 1, "right")
        base = 0.22
        for fn, color, p, width, label in curves:
            p = clamp01(p)
            if p <= 0:
                continue
            path = skia.Path()
            n = max(2, int(120 * p))
            for i in range(n + 1):
                t = p * i / n
                v = base + (1 - base) * 0.92 * fn(t)
                (path.moveTo if i == 0 else path.lineTo)(x0 + t * w, y0 - v * h)
            c.drawPath(path, K.paint(color, 1, width))
            tx = x0 + p * w
            tv = base + (1 - base) * 0.92 * fn(p)
            K.dot(c, tx, y0 - tv * h, width * 0.9, color)
            if label and p > 0.98:
                tm = max((i / 60 for i in range(61)), key=fn)
                vm = base + (1 - base) * 0.92 * fn(tm)
                K.text(c, label, x0 + tm * w + 14, y0 - vm * h - 30, 30, "serif_black", color, 1, "left")


# ---------------------------------------------------------------- 葡萄糖分子

def hexa(c, x, y, r, color=GLU, alpha=1.0, rot=0.0):
    """葡萄糖分子的简化六边形。"""
    if alpha <= 0:
        return
    p = skia.Path()
    for i in range(6):
        a = math.radians(rot + 30 + i * 60)
        (p.moveTo if i == 0 else p.lineTo)(x + r * math.cos(a), y + r * math.sin(a))
    p.close()
    c.drawPath(p, K.paint(color, alpha))
    c.drawPath(p, K.paint(K.shade(color, 0.25), alpha, max(2, r * 0.16)))


def particles(c, x0, y0, x1, y1, t, n=10, r=14, color=GLU, alpha=1.0, speed=0.6, seed=1, wobble=18):
    """一串葡萄糖颗粒沿 (x0,y0)→(x1,y1) 流动。"""
    for i in range(n):
        u = (t * speed + i / n) % 1
        px = lerp(x0, x1, u) + wobble * math.sin(u * 9 + i * seed)
        py = lerp(y0, y1, u) + wobble * math.cos(u * 7 + i * seed * 1.3)
        a = alpha * min(1, u * 6, (1 - u) * 6)
        hexa(c, px, py, r, color, a, u * 120)


def vessel(c, x, y, w, h, alpha=1.0):
    """横向血管剖面：两道血管壁 + 淡红内腔。"""
    with K.fade(c, alpha):
        K.rr(c, x, y, w, h, h / 2, K.tint(VESSEL, 0.45))
        K.rr_stroke(c, x, y, w, h, h / 2, K.shade(VESSEL, 0.15), 10)


def cell(c, x, y, r, open_k=0.0, fill=0.0, alpha=1.0):
    """细胞：圆形，open_k 为门打开程度（胰岛素“钥匙”开门），fill 为细胞内葡萄糖量。"""
    with K.fade(c, alpha):
        with K.paper(c, 1, 0.8):
            K.dot(c, x, y, r, K.mix("#F2D7C9", K.PAPER, 0.2))
        K.ring(c, x, y, r, K.shade("#F2D7C9", 0.3), 8)
        K.dot(c, x + r * 0.25, y - r * 0.2, r * 0.22, K.shade("#F2D7C9", 0.2))
        for i in range(int(6 * clamp01(fill))):
            a = i * 1.1
            hexa(c, x - r * 0.3 + r * 0.35 * math.cos(a), y + r * 0.25 + r * 0.3 * math.sin(a), r * 0.11)
        if open_k > 0:
            gx = x - r
            K.rr(c, gx, y, 28, r * 0.6 * open_k, 8, K.PAPER)


# ---------------------------------------------------------------- 食物图标（s 为整体尺寸，以中心为原点）

def broccoli(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        K.rr(c, x, y + s * 0.22, s * 0.2, s * 0.5, s * 0.06, VEG2)
        for dx, dy, r in ((-0.22, -0.05, 0.2), (0.2, -0.06, 0.2), (0, -0.2, 0.22), (-0.08, 0.04, 0.16),
                          (0.1, 0.05, 0.15)):
            K.dot(c, x + dx * s, y + dy * s, r * s, VEG)
            K.dot(c, x + dx * s - r * s * 0.3, y + dy * s - r * s * 0.3, r * s * 0.35, K.tint(VEG, 0.25))


def salad(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        for i, (dx, col) in enumerate(((-0.25, VEG), (0.0, VEG2), (0.24, VEG), (-0.1, "#D9593A"), (0.15, "#F3C24B"))):
            K.dot(c, x + dx * s, y - s * (0.08 + 0.06 * (i % 2)), s * (0.16 if i < 3 else 0.08), col)
        p = skia.Path()
        p.addArc(skia.Rect.MakeLTRB(x - s * 0.5, y - s * 0.35, x + s * 0.5, y + s * 0.45), 0, 180)
        p.close()
        c.drawPath(p, K.paint("#E7EEF0"))
        c.drawPath(p, K.paint("#9FB6BF", 1, s * 0.03))


def egg(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        p = skia.Path()
        pts = [(-0.45, 0.05), (-0.3, -0.35), (0.1, -0.42), (0.45, -0.15), (0.38, 0.3), (-0.05, 0.42), (-0.4, 0.3)]
        p.moveTo(x + pts[0][0] * s, y + pts[0][1] * s)
        for a, b in zip(pts, pts[1:] + pts[:1]):
            p.quadTo(x + a[0] * s * 1.1, y + a[1] * s * 1.1, x + (a[0] + b[0]) / 2 * s, y + (a[1] + b[1]) / 2 * s)
        p.close()
        c.drawPath(p, K.paint("#FFFDF6"))
        c.drawPath(p, K.paint(K.LINE, 1, s * 0.03))
        K.dot(c, x + s * 0.02, y - s * 0.02, s * 0.18, EGG)
        K.dot(c, x - s * 0.04, y - s * 0.07, s * 0.05, "#FFF3C2")


def drumstick(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        K.rr(c, x + s * 0.22, y + s * 0.22, s * 0.12, s * 0.42, s * 0.05, "#F4EBDD", 1)
        K.dot(c, x + s * 0.3, y + s * 0.42, s * 0.08, "#F4EBDD")
        K.dot(c, x + s * 0.4, y + s * 0.38, s * 0.08, "#F4EBDD")
        c.save()
        c.rotate(-35, x, y)
        K.rr(c, x - s * 0.05, y - s * 0.05, s * 0.5, s * 0.7, s * 0.25, MEAT)
        K.rr(c, x - s * 0.12, y - s * 0.15, s * 0.14, s * 0.3, s * 0.07, K.tint(MEAT, 0.3))
        c.restore()


def bread(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        K.dot(c, x - s * 0.22, y - s * 0.22, s * 0.22, BREAD)
        K.dot(c, x + s * 0.22, y - s * 0.22, s * 0.22, BREAD)
        K.rr(c, x, y + s * 0.05, s * 0.8, s * 0.6, s * 0.1, BREAD)
        K.rr(c, x, y + s * 0.06, s * 0.64, s * 0.46, s * 0.08, "#F6E2B8")
        K.dot(c, x - s * 0.2, y - s * 0.2, s * 0.15, "#F6E2B8")
        K.dot(c, x + s * 0.2, y - s * 0.2, s * 0.15, "#F6E2B8")


def rice(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        K.dot(c, x, y - s * 0.08, s * 0.38, RICE)
        for i in range(9):
            a = i * 0.7
            K.rr(c, x + s * 0.22 * math.cos(a), y - s * 0.12 + s * 0.15 * math.sin(a), s * 0.07, s * 0.04, 4, "#E6DCC3")
        p = skia.Path()
        p.addArc(skia.Rect.MakeLTRB(x - s * 0.48, y - s * 0.3, x + s * 0.48, y + s * 0.42), 0, 180)
        p.close()
        c.drawPath(p, K.paint("#5C8DB8"))
        K.seg(c, x - s * 0.36, y + s * 0.2, x + s * 0.36, y + s * 0.2, "#F2F6FA", s * 0.03)


def cake(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        K.poly(c, [(x - s * 0.45, y + s * 0.35), (x + s * 0.45, y + s * 0.35), (x + s * 0.45, y - s * 0.05),
                   (x - s * 0.45, y + s * 0.12)], "#F3D9B1")
        K.poly(c, [(x - s * 0.45, y + s * 0.12), (x + s * 0.45, y - s * 0.05), (x + s * 0.45, y - s * 0.15),
                   (x - s * 0.45, y + 0.02 * s)], "#F6A6B2")
        K.seg(c, x - s * 0.45, y + s * 0.22, x + s * 0.45, y + s * 0.1, "#F6A6B2", s * 0.05)
        K.dot(c, x + s * 0.22, y - s * 0.2, s * 0.1, "#D9364A")


def cookie(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        K.dot(c, x, y, s * 0.42, "#D1A065")
        for dx, dy in ((-0.15, -0.1), (0.12, -0.18), (0.18, 0.12), (-0.1, 0.18), (0.0, 0.0)):
            K.dot(c, x + dx * s, y + dy * s, s * 0.06, "#5B3A24")


def apple(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        K.dot(c, x - s * 0.15, y + s * 0.05, s * 0.32, "#D84A3A")
        K.dot(c, x + s * 0.15, y + s * 0.05, s * 0.32, "#D84A3A")
        K.dot(c, x - s * 0.2, y - s * 0.05, s * 0.08, "#F08A7A")
        K.seg(c, x, y - s * 0.25, x + s * 0.05, y - s * 0.42, "#6B4A2E", s * 0.05)
        K.poly(c, [(x + s * 0.05, y - s * 0.36), (x + s * 0.28, y - s * 0.45), (x + s * 0.12, y - s * 0.28)], VEG)


def juice(c, x, y, s, alpha=1.0, color="#F29A3A", level=0.75):
    with K.fade(c, alpha):
        K.poly(c, [(x - s * 0.3, y - s * 0.45), (x + s * 0.3, y - s * 0.45), (x + s * 0.24, y + s * 0.45),
                   (x - s * 0.24, y + s * 0.45)], "#EAF2F5")
        top = y + s * 0.45 - s * 0.9 * level
        k = (top - (y - s * 0.45)) / (s * 0.9)
        K.poly(c, [(x - s * (0.3 - 0.06 * k), top), (x + s * (0.3 - 0.06 * k), top), (x + s * 0.24, y + s * 0.45),
                   (x - s * 0.24, y + s * 0.45)], color)
        K.seg(c, x + s * 0.1, y - s * 0.6, x + s * 0.02, y + s * 0.2, "#4E9A6E", s * 0.05)


def honey(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        K.rr(c, x, y + s * 0.05, s * 0.66, s * 0.7, s * 0.14, "#E9A62A")
        K.rr(c, x, y - s * 0.35, s * 0.5, s * 0.14, s * 0.05, "#8A5A2B")
        K.rr(c, x, y + s * 0.08, s * 0.44, s * 0.24, s * 0.05, "#FBF3DF")
        K.text(c, "蜂蜜", x, y + s * 0.09, s * 0.15, "serif_black", "#8A5A2B")


def sugar_cubes(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        for dx, dy in ((-0.2, 0.15), (0.2, 0.15), (0.0, -0.18)):
            K.rr(c, x + dx * s, y + dy * s, s * 0.36, s * 0.36, s * 0.05, "#FFFFFF")
            K.rr_stroke(c, x + dx * s, y + dy * s, s * 0.36, s * 0.36, s * 0.05, K.LINE, s * 0.02)


def vinegar(c, x, y, s, alpha=1.0, label="醋"):
    with K.fade(c, alpha):
        K.rr(c, x, y + s * 0.1, s * 0.42, s * 0.7, s * 0.1, "#6B3A2A")
        K.rr(c, x, y - s * 0.38, s * 0.16, s * 0.3, s * 0.04, "#6B3A2A")
        K.rr(c, x, y - s * 0.55, s * 0.2, s * 0.08, s * 0.03, K.DARK)
        K.rr(c, x, y + s * 0.12, s * 0.32, s * 0.3, s * 0.05, K.PAPER)
        K.text(c, label, x, y + s * 0.13, s * 0.16, "serif_black", "#6B3A2A")


def nuts(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        for dx, dy, r in ((-0.2, 0.08, 0.17), (0.12, 0.1, 0.18), (-0.02, -0.15, 0.17), (0.25, -0.12, 0.14)):
            K.dot(c, x + dx * s, y + dy * s, r * s, "#B9834F")
            K.seg(c, x + dx * s, y + dy * s - r * s * 0.6, x + dx * s, y + dy * s + r * s * 0.6, "#8C5E33", s * 0.02)


def cheese(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        K.poly(c, [(x - s * 0.45, y + s * 0.3), (x + s * 0.45, y + s * 0.3), (x + s * 0.45, y - s * 0.1),
                   (x - s * 0.45, y + s * 0.05)], "#F4C84E")
        for dx, dy, r in ((-0.15, 0.17, 0.07), (0.2, 0.12, 0.09), (0.32, 0.22, 0.04)):
            K.dot(c, x + dx * s, y + dy * s, r * s, "#E0AA2F")


FOODS = {"broccoli": broccoli, "salad": salad, "egg": egg, "drumstick": drumstick, "bread": bread, "rice": rice,
         "cake": cake, "cookie": cookie, "apple": apple, "juice": juice, "honey": honey, "sugar": sugar_cubes,
         "vinegar": vinegar, "nuts": nuts, "cheese": cheese}


def food(c, name, x, y, s, alpha=1.0, rot=0.0, scale=1.0):
    """按名字画食物（带纸片投影）。"""
    if alpha <= 0 or scale <= 0:
        return
    with K.at(c, x, y, rot, scale):
        with K.paper(c, alpha, 0.7, skia.Rect.MakeXYWH(-s, -s, 2 * s, 2 * s)):
            FOODS[name](c, 0, 0, s, 1.0)


def plate(c, x, y, r, alpha=1.0):
    with K.paper(c, alpha, 0.8):
        K.dot(c, x, y, r, "#FFFFFF")
    K.ring(c, x, y, r * 0.78, K.LINE, 4, alpha)


def step_order(c, x, y, items, k_list, s=150, gap=230, alpha=1.0):
    """按顺序排开的食物 + 编号圆点；k_list[i] 为第 i 个的出现进度。"""
    n = len(items)
    for i, (name, label) in enumerate(items):
        k = k_list[i]
        if k <= 0:
            continue
        px = x + (i - (n - 1) / 2) * gap
        food(c, name, px, y, s, alpha * clamp01(k * 3), 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8))
        K.dot(c, px - s * 0.55, y - s * 0.55, 26, K.INK, alpha * clamp01(k * 3))
        K.text(c, str(i + 1), px - s * 0.55, y - s * 0.55, 30, "black", K.PAPER, alpha * clamp01(k * 3))
        if label:
            K.text(c, label, px, y + s * 0.75, 32, "sans_medium", K.INK2, alpha * clamp01(k * 3))
        if i < n - 1 and k >= 1:
            K.arrow(c, (px + s * 0.55, y), (px + gap - s * 0.6, y), K.INK3, 6, alpha, 1, 0, 18)


__all__ = ["GLU", "SPIKE", "FLAT", "bump", "chart", "hexa", "particles", "vessel", "cell", "food", "FOODS", "plate",
           "step_order", "ease_in_out", "ease_out"]
