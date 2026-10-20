"""马斯洛系列的专用元件：需求层次（台阶 / 金字塔两种画法）、满足度条、高峰、鲸鱼（约拿）、饭碗、成长的芽等。
在阿德勒系列的纸片剪影元件（adler.kit）之上组合，坐标以元素中心为原点。"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

LEVELS = (("生理", "#C8873A"), ("安全", "#5E8C61"), ("归属与爱", "#C25B6A"), ("尊重", "#5B6FA8"), ("自我实现", "#8A5BA8"))
SKY = "#BFD6E3"
SEA = "#4F7FA0"

GROUND_Y = 1130


def ground(g):
    K.ground(g.c, GROUND_Y)


def hierarchy(c, x, y, w=720, lh=110, p=1.0, hi=None, fill=None, shape="steps", labels=True, alpha=1.0, dim=0.35):
    """需求层次：自下而上五层。p 为逐层出现的进度（0→1）；hi 为高亮层序号（其余变淡）；
    fill 为各层“相对满足度”0–1 列表，画成层内的满足条；shape 为 steps（等宽台阶，马斯洛原意的相对层级）或 pyramid（流行的金字塔）。"""
    n = len(LEVELS)
    for i, (name, col) in enumerate(LEVELS):
        k = ease_out(clamp01(p * n - i))
        if k <= 0:
            continue
        cy = y + (n / 2 - i - 0.5) * lh
        if shape == "pyramid":
            top = w * (n - i - 1) / n
            bot = w * (n - i) / n
            pts = [(x - bot / 2, cy + lh / 2), (x + bot / 2, cy + lh / 2), (x + top / 2, cy - lh / 2), (x - top / 2, cy - lh / 2)]
            if i == n - 1:
                pts = [(x - bot / 2, cy + lh / 2), (x + bot / 2, cy + lh / 2), (x, cy - lh / 2)]
            a = alpha * k * (1 if hi is None or hi == i else dim)
            K.poly(c, pts, col, a)
            if labels:
                fs = 34 if i < n - 1 else min(28, bot * 0.55 / 4)
                K.text(c, name, x, cy + (lh * 0.3 if i == n - 1 else 0), fs, "serif_black", K.PAPER, a)
            continue
        ww = w - i * 40
        a = alpha * k * (1 if hi is None or hi == i else dim)
        with K.at(c, x, cy + (1 - k) * 40):
            K.rr(c, 0, 0, ww, lh - 12, 16, K.mix(col, K.BG, 0.72), a)
            if fill is not None:
                v = clamp01(fill[i]) * k
                K.rr(c, -ww / 2 + ww * v / 2, 0, ww * v, lh - 12, 16, col, a)
            else:
                K.rr(c, 0, 0, ww, lh - 12, 16, col, a)
            if labels:
                K.text(c, name, 0, 0, 40, "serif_black", K.PAPER if fill is None else K.INK, a)
            if hi == i:
                K.rr_stroke(c, 0, 0, ww + 14, lh + 2, 20, K.GOLD, 6, alpha * k)


def meter(c, x, y, w, h, v, color, label=None, alpha=1.0):
    """横向满足度条；label 写在左侧。"""
    K.rr(c, x, y, w, h, h / 2, K.LINE, alpha)
    if v > 0:
        K.rr(c, x - w / 2 + w * v / 2, y, w * v, h, h / 2, color, alpha)
    if label:
        K.text(c, label, x - w / 2 - 20, y, 34, "serif_black", K.INK, alpha, align="right")


def bowl(c, x, y, s, full=1.0, alpha=1.0):
    """饭碗：full 为饭的多少。"""
    if full > 0:
        K.dot(c, x, y - s * 0.12, s * 0.42 * full, K.PAPER, alpha)
        K.ring(c, x, y - s * 0.12, s * 0.42 * full, K.INK3, 3, alpha)
    K.poly(c, [(x - s * 0.55, y - s * 0.1), (x + s * 0.55, y - s * 0.1), (x + s * 0.35, y + s * 0.38), (x - s * 0.35, y + s * 0.38)],
           "#C8873A", alpha)
    K.rr(c, x, y + s * 0.42, s * 0.4, s * 0.1, 4, K.mix("#C8873A", K.DARK, 0.3), alpha)


def peak(c, x, y, s, glow=0.0, t=0.0, alpha=1.0, color="#8A5BA8"):
    """山峰：山顶的光晕 glow 0→1。"""
    if glow > 0:
        K.spotlight(c, x, y - s * 0.55, s * 0.55 * (1 + 0.05 * math.sin(t * 3)), K.GOLD, 0.55 * glow * alpha)
    K.poly(c, [(x - s * 0.9, y + s * 0.4), (x, y - s * 0.55), (x + s * 0.9, y + s * 0.4)], K.mix(color, K.BG, 0.35), alpha)
    K.poly(c, [(x - s * 0.2, y - s * 0.33), (x, y - s * 0.55), (x + s * 0.2, y - s * 0.33), (x + s * 0.07, y - s * 0.38),
               (x - s * 0.06, y - s * 0.3)], K.PAPER, alpha)
    K.poly(c, [(x + s * 0.1, y + s * 0.4), (x + s * 0.55, y - s * 0.1), (x + s * 1.1, y + s * 0.4)], K.mix(color, K.BG, 0.55), alpha)


def whale(c, x, y, s, mouth=0.0, t=0.0, alpha=1.0):
    """鲸鱼（约拿的故事）：mouth 为张嘴程度。"""
    col = SEA
    with K.at(c, x, y + math.sin(t * 2) * s * 0.03):
        path = skia.Path()
        path.addOval(skia.Rect.MakeXYWH(-s * 0.7, -s * 0.32, s * 1.3, s * 0.64))
        c.drawPath(path, K.paint(col, alpha))
        K.poly(c, [(s * 0.5, 0), (s * 0.95, -s * 0.3), (s * 0.85, 0), (s * 0.95, s * 0.28)], col, alpha)
        K.poly(c, [(-s * 0.55, s * 0.05), (-s * 0.05, s * 0.05), (-s * 0.25, s * 0.3)], K.mix(col, K.PAPER, 0.5), alpha)
        if mouth > 0:
            K.poly(c, [(-s * 0.72, -s * 0.02), (-s * 0.25, s * 0.02 + s * 0.06 * mouth), (-s * 0.72, s * 0.04 + s * 0.22 * mouth)],
                   K.DARK, alpha)
        K.dot(c, -s * 0.38, -s * 0.12, s * 0.035, K.INK, alpha)
        for i in range(3):
            K.seg(c, -s * 0.2 + i * s * 0.05, -s * 0.34, -s * 0.28 + i * s * 0.1, -s * 0.5, K.mix(col, K.PAPER, 0.6), s * 0.025,
                  alpha)


def sprout_grow(c, x, y, s, k=1.0, alpha=1.0):
    """从土里长出的芽：k 为生长进度。"""
    K.rr(c, x, y + s * 0.08, s * 0.9, s * 0.16, s * 0.08, K.mix("#8A6A4A", K.BG, 0.2), alpha)
    h = s * 0.7 * ease_out(clamp01(k))
    K.seg(c, x, y, x, y - h, K.GREEN, s * 0.05, alpha)
    q = clamp01(k * 1.6 - 0.5)
    if q > 0:
        for sx in (-1, 1):
            with K.at(c, x + sx * s * 0.12 * q, y - h * 0.75, sx * 30):
                path = skia.Path()
                path.addOval(skia.Rect.MakeXYWH(-s * 0.16 * q, -s * 0.07 * q, s * 0.32 * q, s * 0.14 * q))
                c.drawPath(path, K.paint(K.GREEN, alpha))


def ladder_up(c, g, el_t, d):
    """台阶示意：小人沿五层台阶往上走；d['to'] 为目标层。"""
    to = d.get("to", 4)
    hierarchy(c, 0, 0, 640, 100, 1, labels=True, alpha=0.9)
    k = ease_in_out(clamp01(el_t / d.get("dur", 3.0)))
    lv = k * to
    i = int(lv)
    f = lv - i
    y = (5 / 2 - 0.5) * 100 - lv * 100 - 60
    K.figure(c, 330 - 20 * lv + 30 * math.sin(f * math.pi), y + 50, 120, K.walk(el_t * 3) if k < 1 else "cheer", K.HERO, K.SKIN, 1,
             -1, "happy", "short")


def gauge_set(c, g, el_t, d):
    """一个人同时“部分满足”五种需要：五根进度条。"""
    vals = d.get("vals", (0.85, 0.7, 0.5, 0.4, 0.1))
    for i, (name, col) in enumerate(reversed(LEVELS)):
        j = len(LEVELS) - 1 - i
        k = ease_out(clamp01(g.since(d.get("b0", 0) + i * 0.5) / 0.6))
        meter(c, 120, -240 + i * 120, 520, 56, vals[j] * k, col, name)
        if d.get("pct") and k > 0:
            K.text(c, f"{round(vals[j] * 100)}%", 420, -240 + i * 120, 34, "sans_medium", K.INK2, k, align="left")


def levels(c, g, el_t, d):
    """需求层次元素：d 可含 seq=[(拍, 高亮层)]、hi、fill、shape、w、lh、grow（入场后逐层长出的秒数）。"""
    hi = d.get("hi")
    for k, i in d.get("seq", ()):
        if g.since(k) >= 0:
            hi = i
    grow = d.get("grow")
    p = clamp01(el_t / grow) if grow else 1.0
    fill = d.get("fill")
    if fill is not None and d.get("fill_at") is not None:
        q = ease_out(clamp01(g.since(d["fill_at"]) / 0.8))
        fill = [v * q for v in fill]
    hierarchy(c, 0, 0, d.get("w", 720), d.get("lh", 110), p, hi, fill, d.get("shape", "steps"), d.get("labels", True))
