"""《稀缺》系列的专用元件：带宽条、隧道视野、循环箭头、行李箱、果篮、账单。
在阿德勒系列的纸片剪影元件（adler.kit）与光效层（adler.fx）之上组合，坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

GROUND_Y = 1130


def ground(g):
    K.ground(g.c, GROUND_Y)


def meter(c, g, el_t, d):
    """带宽条：整条为心智容量；eat [(拍, 比例, 名称)] 依次从右往左被占用，剩余部分随节拍轻微发光。"""
    w, h = d.get("w", 760), d.get("h", 120)
    K.card(c, 0, 0, w + 36, h + 36, K.PAPER, 1, r=30)
    x0 = -w / 2
    used = 0.0
    blocks = []
    for b, frac, name in d.get("eat", []):
        k = ease_out(clamp01(g.since(b) / 0.35))
        if k <= 0:
            continue
        blocks.append((used, frac * k, name, k))
        used += frac * k
    free = 1 - used
    col = g.acc if free > 0.45 else K.RED
    fx.glow(c, x0 + w * free / 2, 0, w * 0.45, col, 0.18 + 0.12 * g.pulse(5))
    K.rr(c, x0 + w * free / 2, 0, max(1.0, w * free), h, 20, col)
    x = x0 + w
    for u, f, name, k in blocks:
        bw = w * f
        K.rr(c, x - bw / 2, 0, max(1.0, bw - 6), h, 20, K.DARK, k)
        if bw > 120:
            K.text(c, name, x - bw / 2, 0, 38, "sans_medium", K.PAPER, k)
        x -= bw
    label = d.get("label", "带宽")
    K.text(c, label, 0, -h / 2 - 70, 46, "serif_black", K.INK)
    if d.get("pct", True):
        K.text(c, f"剩余 {round(free * 100):d}%", 0, h / 2 + 70, 40, "sans_medium", col)


def tunnel(c, g, el_t, d):
    """隧道视野：舞台区（不压字幕与页眉）四周压暗，中间留一个圆洞；r 为洞的半径，随进度从大收到小。
    box 为压暗区域 (左, 上, 右, 下)，以元素中心为原点。"""
    r = lerp(d.get("r0", 900), d.get("r", 300), ease_in_out(clamp01(el_t / d.get("close", 1.2))))
    cx, cy = d.get("cx", 0), d.get("cy", 0)
    p = skia.Path()
    l, t, r_, b = d.get("box", (-500, -440, 500, 460))
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(l, t, r_, b), 40, 40))
    p.addCircle(cx, cy, r)
    p.setFillType(skia.PathFillType.kEvenOdd)
    paint = K.paint(K.INK, d.get("dark", 0.78), blur=18)
    c.drawPath(p, paint)
    K.ring(c, cx, cy, r, g.acc2, 6, 0.6 + 0.4 * g.pulse(6))


def cycle(c, g, el_t, d):
    """循环箭头图：labels 均匀排在圆上，第 i 段箭头在 b0 + i*step 拍画出，节点为纸片标签。"""
    labels = d["labels"]
    R = d.get("R", 280)
    n = len(labels)
    b0, step = d.get("b0", 0), d.get("step", 2)
    pts = [(R * math.cos(-math.pi / 2 + i * math.tau / n), R * math.sin(-math.pi / 2 + i * math.tau / n)) for i in range(n)]
    for i in range(n):
        k = clamp01(g.since(b0 + i * step + 1) / 0.5)
        if k <= 0:
            continue
        a0 = -90 + i * 360 / n + 22
        sweep = 360 / n - 44
        rect = skia.Rect.MakeXYWH(-R, -R, 2 * R, 2 * R)
        path = skia.Path()
        path.addArc(rect, a0, sweep * ease_out(k))
        c.drawPath(path, K.paint(g.acc, 1, stroke=12))
        if k >= 1:
            ang = math.radians(a0 + sweep)
            hx, hy = R * math.cos(ang), R * math.sin(ang)
            tang = ang + math.pi / 2
            K.poly(c, [(hx + 26 * math.cos(tang), hy + 26 * math.sin(tang)),
                       (hx + 14 * math.cos(tang + 2.3), hy + 14 * math.sin(tang + 2.3)),
                       (hx + 14 * math.cos(tang - 2.3), hy + 14 * math.sin(tang - 2.3))], g.acc)
    spin = d.get("spin_at")
    rot = 0.0 if spin is None or g.since(spin) < 0 else g.since(spin) * 50
    for i, (x, y) in enumerate(pts):
        st = fx.word_pop(g.since(b0 + i * step))
        if st is None:
            continue
        a, s_, r_ = st
        hi = i == d.get("hi", -1)
        with K.at(c, x, y, r_ * 0.6, s_):
            fx.draw_word(c, labels[i], 0, 0, 52, "serif_black", K.INK, g.acc if hi else K.DARK, K.PAPER, a, True)
    if spin is not None and g.since(spin) >= 0:
        fx.rays(c, 0, 0, R * 0.7, g.acc2, g.t, 10, 0.25, 40)
        with K.at(c, 0, 0, rot):
            K.ring(c, 0, 0, R * 0.32, g.acc2, 8, 0.8, 0.75)


def suitcase(c, x, y, w, h, color, items, alpha=1.0, p=1.0):
    """行李箱：items [(相对 x, 相对 y, 尺寸, 颜色)] 为装进去的物品（p 为装入进度）。"""
    K.card(c, x, y, w, h, color, alpha, r=26)
    K.rr_stroke(c, x, y - h / 2 - 22, w * 0.3, 44, 18, K.shade(color, 0.3), 12, alpha)
    for i, (ix, iy, s, col) in enumerate(items):
        k = clamp01(p * len(items) - i)
        if k <= 0:
            continue
        K.rr(c, x + ix * w / 2, y + iy * h / 2 - (1 - ease_out(k)) * 80, s, s * 0.7, 10, col, alpha * k)


def basket(c, x, y, s, alpha=1.0, n=7):
    """果篮：编织纹篮子 + 一堆圆形水果。"""
    cols = ["#D9593A", "#E3A33B", "#7FA34A", "#C0504D", "#E8B84A", "#6F9E3F", "#D9703A"]
    for i in range(n):
        a = i / max(1, n - 1)
        K.dot(c, x + (a - 0.5) * s * 0.9, y - s * 0.28 - math.sin(a * math.pi) * s * 0.18, s * 0.17, cols[i % len(cols)], alpha)
    K.poly(c, [(x - s * 0.62, y - s * 0.25), (x + s * 0.62, y - s * 0.25), (x + s * 0.45, y + s * 0.3),
               (x - s * 0.45, y + s * 0.3)], "#B98A55", alpha)
    for j in range(3):
        yy = y - s * 0.1 + j * s * 0.13
        K.seg(c, x - s * 0.55 + j * 0.06 * s, yy, x + s * 0.55 - j * 0.06 * s, yy, "#94693C", 6, alpha)


def bill(c, g, el_t, d):
    """账单纸：标题 + 几行横线 + 红色金额条。"""
    w, h = d.get("w", 260), d.get("h", 320)
    K.card(c, 0, 0, w, h, K.PAPER, 1, r=14)
    K.text(c, d.get("title", "账单"), 0, -h / 2 + 50, 40, "serif_black", K.INK)
    for i in range(3):
        K.seg(c, -w / 2 + 34, -h / 2 + 110 + i * 46, w / 2 - 34 - (i % 2) * 50, -h / 2 + 110 + i * 46, K.LINE, 8)
    K.rr(c, 0, h / 2 - 54, w - 70, 46, 12, K.RED)
    K.text(c, d.get("amount", "待付"), 0, h / 2 - 54, 30, "sans_medium", K.PAPER)
