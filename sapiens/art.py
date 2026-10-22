"""《人类简史》系列的专用元件：麦田、货币（贝壳、金币、纸币、手机余额）、石碑与宣言、新旧世界地图、泡沫、
时间轴、两条上升曲线、人群。上班族日常元件（账单、清单、手机聊天、日历等）复用 scarcity.art。
坐标以元素中心为原点。"""

import math

import numpy as np
import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_out, lerp
from scarcity.art import GROUND_Y, badge, bill, calendar, checklist, cycle, ground, laptop, phone_chat  # noqa: F401

WHEAT = "#D9A93A"


def crowd(c, g, el_t, d):
    """一群人（呼吸起伏）。"""
    K.crowd(c, 0, 0, d.get("n", 7), d.get("s", 220), g.t, spread=d.get("spread", 760), rows=d.get("rows", 2))


def wheat(c, x, y, s, t=0.0, alpha=1.0, color=WHEAT):
    """一株麦子：茎 + 7 粒麦穗，随时间轻摆。"""
    sway = 4 * math.sin(t * 1.8 + x * 0.02)
    with K.at(c, x, y, sway):
        K.seg(c, 0, 0, 0, -s, K.shade(color, 0.25), s * 0.035, alpha)
        for i in range(7):
            yy = -s * (0.62 + i * 0.055)
            for side in (-1, 1):
                with K.at(c, side * s * 0.05, yy, side * 28):
                    K.rr(c, 0, 0, s * 0.07, s * 0.12, s * 0.035, color, alpha)
        K.rr(c, 0, -s * 1.02, s * 0.06, s * 0.1, s * 0.03, color, alpha)


def field(c, g, el_t, d):
    """麦田：n 株麦子按行列排开，p 为生长进度（从 0 长到满高）。"""
    n, w = d.get("n", 9), d.get("w", 820)
    p = ease_out(clamp01(el_t / d.get("grow", 1.2)))
    for r in range(2):
        for i in range(n):
            x = -w / 2 + w * (i + 0.5 * r) / (n - 0.5)
            wheat(c, x, r * 40, d.get("s", 220) * (0.6 + 0.4 * p) * (1 - 0.12 * r), g.t + i, p)


def coin(c, x, y, r, alpha=1.0, label="¥"):
    K.dot(c, x, y, r, K.GOLD, alpha)
    K.ring(c, x, y, r * 0.78, K.shade(K.GOLD, 0.2), r * 0.08, alpha)
    K.text(c, label, x, y, r * 1.0, "black", K.shade(K.GOLD, 0.35), alpha)


def shell(c, x, y, s, alpha=1.0):
    """贝壳（海贝币）。"""
    K.poly(c, [(x, y - s * 0.5), (x + s * 0.45, y + s * 0.3), (x - s * 0.45, y + s * 0.3)], "#E9D7C0", alpha)
    for i in range(-2, 3):
        K.seg(c, x, y - s * 0.45, x + i * s * 0.17, y + s * 0.28, "#C9A988", s * 0.04, alpha)


def banknote(c, x, y, w, alpha=1.0, color="#6FA58A", rot=0.0, label="100"):
    with K.at(c, x, y, rot):
        K.card(c, 0, 0, w, w * 0.5, color, alpha, r=w * 0.05)
        K.ring(c, 0, 0, w * 0.13, K.tint(color, 0.5), w * 0.02, alpha)
        K.text(c, label, -w * 0.32, -w * 0.12, w * 0.12, "black", K.PAPER, alpha)
        K.text(c, label, w * 0.32, w * 0.12, w * 0.12, "black", K.PAPER, alpha)


def money_steps(c, g, el_t, d):
    """货币演变：贝壳 → 金币 → 纸币 → 手机余额，第 i 个在 b0 + i*step 拍弹出，之间以箭头相连。"""
    b0, step = d.get("b0", 0), d.get("step", 2)
    xs = [-330, -110, 110, 330]
    names = ["贝壳", "金币", "纸币", "数字"]
    for i, x in enumerate(xs):
        st = fx.word_pop(g.since(b0 + i * step))
        if st is None:
            continue
        a, s_, _ = st
        with K.at(c, x, 0, 0, s_):
            if i == 0:
                shell(c, 0, 0, 120, a)
            elif i == 1:
                coin(c, 0, 0, 60, a)
            elif i == 2:
                banknote(c, 0, 0, 170, a)
            else:
                K.icon(c, "phone", 0, 0, 140, g.acc, a, 0.6, 0, 1, 1, g.acc2)
        K.text(c, names[i], x, 120, 40, "serif_black", K.INK, a)
        if i:
            K.arrow(c, (xs[i - 1] + 70, 0), (x - 75, 0), K.INK3, 6, a, clamp01(g.since(b0 + i * step) / 0.3), 0, 18)


def balance(c, g, el_t, d):
    """手机余额页：余额数字从 v0 滚到 v1（b0→b1 拍），下方一个“扫码付款”按钮。"""
    w, h = d.get("w", 460), d.get("h", 800)
    K.card(c, 0, 0, w, h, K.DARK, 1, r=52)
    K.rr(c, 0, 0, w - 30, h - 30, 40, K.PAPER)
    K.text(c, d.get("title", "我的余额"), 0, -h / 2 + 90, 40, "sans_medium", K.INK2)
    v = lerp(d.get("v0", 0), d.get("v1", 8888), g.span(d.get("b0", 0), d.get("b1", 4)))
    K.text(c, f"¥{v:,.2f}", 0, -h / 2 + 200, 72, "black", K.INK)
    K.rr(c, 0, h / 2 - 140, w - 120, 96, 48, g.acc)
    K.text(c, d.get("button", "扫码付款"), 0, h / 2 - 140, 42, "sans_medium", K.PAPER)
    for i in range(3):
        K.rr(c, 0, -h / 2 + 330 + i * 90, w - 120, 60, 16, "#EEE8DE")


def tablet(c, x, y, s, alpha=1.0, title="汉谟拉比法典", sub="约前1776年"):
    """石碑：圆顶石板 + 楔形文字刻痕。"""
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - s * 0.36, y - s * 0.5, s * 0.72, s), s * 0.3, s * 0.3))
    with K.paper(c, alpha, 1.0, skia.Rect.MakeXYWH(x - s, y - s, 2 * s, 2 * s)):
        c.drawPath(p, K.paint("#8C8A84"))
        rng = np.random.default_rng(3)
        for r in range(9):
            for k in range(5):
                xx = x - s * 0.24 + k * s * 0.12 + rng.uniform(-4, 4)
                yy = y - s * 0.18 + r * s * 0.07
                K.poly(c, [(xx, yy), (xx + s * 0.05, yy - s * 0.015), (xx + s * 0.05, yy + s * 0.015)], "#5F5D58")
    K.text(c, title, x, y - s * 0.62 - 10, 40, "serif_black", K.INK, alpha)
    K.text(c, sub, x, y + s * 0.62, 32, "sans_medium", K.INK2, alpha)


def scroll(c, x, y, s, alpha=1.0, title="独立宣言", sub="1776年"):
    """羊皮纸卷：一张纸 + 上下卷轴 + 横线。"""
    K.card(c, x, y, s * 0.66, s * 0.9, "#F1E3C4", alpha, r=10)
    for yy in (-s * 0.45, s * 0.45):
        K.rr(c, x, y + yy, s * 0.76, s * 0.08, s * 0.04, "#C9A46A", alpha)
    for r in range(7):
        K.seg(c, x - s * 0.24, y - s * 0.28 + r * s * 0.08, x + s * 0.24 - (r % 3) * 10, y - s * 0.28 + r * s * 0.08,
              "#A08A62", 5, alpha)
    K.text(c, title, x, y - s * 0.62 - 10, 40, "serif_black", K.INK, alpha)
    K.text(c, sub, x, y + s * 0.62, 32, "sans_medium", K.INK2, alpha)


def world_map(c, x, y, w, alpha=1.0, blank=False, label=""):
    """示意世界地图：blank=False 时陆地画满（含想象出来的岛屿与怪兽点缀），True 时只画已知海岸、其余留白。"""
    h = w * 0.62
    K.card(c, x, y, w, h, "#EFE4CC", alpha, r=12)
    known = [(-0.28, -0.05, 0.22, 0.3), (-0.05, -0.12, 0.12, 0.18), (0.05, 0.15, 0.1, 0.2)]
    guess = [(0.3, -0.1, 0.18, 0.28), (-0.38, 0.25, 0.14, 0.14), (0.25, 0.28, 0.16, 0.12), (0.4, 0.3, 0.06, 0.06)]
    for cx, cy, rx, ry in known + ([] if blank else guess):
        c.drawOval(skia.Rect.MakeXYWH(x + (cx - rx) * w, y + (cy - ry) * h, 2 * rx * w, 2 * ry * h), K.paint("#9DB07A", alpha))
    if blank:
        K.rr_stroke(c, x + 0.3 * w, y + 0.05 * h, 0.34 * w, 0.6 * h, 16, K.INK3, 4, alpha, dash=(14, 10))
        K.text(c, "？", x + 0.3 * w, y + 0.05 * h, w * 0.12, "black", K.INK3, alpha)
    else:
        K.dot(c, x + 0.3 * w, y - 0.32 * h, w * 0.03, K.RED, alpha)
        K.text(c, "龙", x + 0.18 * w, y + 0.32 * h, w * 0.07, "serif_black", K.RED, alpha)
    if label:
        K.text(c, label, x, y + h / 2 + 46, 38, "serif_black", K.INK, alpha)


def bubble_pop(c, g, el_t, d):
    """泡沫：从 b0 拍起越吹越大并发光，在 pop 拍破裂成星光与碎点。"""
    b0, pop = d.get("b0", 0), d.get("pop", 8)
    r0, r1 = d.get("r0", 60), d.get("r1", 300)
    if g.since(pop) < 0:
        k = g.span(b0, pop)
        r = lerp(r0, r1, k)
        wob = 1 + 0.02 * math.sin(g.t * 9)
        fx.glow(c, 0, 0, r * 1.5, g.acc2, 0.25 + 0.2 * k)
        c.drawCircle(0, 0, r * wob, K.paint(K.tint(g.acc, 0.7), 0.35))
        c.drawCircle(0, 0, r * wob, K.paint(g.acc, 0.9, stroke=6))
        c.drawOval(skia.Rect.MakeXYWH(-r * 0.55, -r * 0.6, r * 0.4, r * 0.22), K.paint(K.PAPER, 0.8))
        if d.get("label"):
            K.text(c, d["label"], 0, 0, max(30, r * 0.28), "serif_black", g.acc)
    else:
        dt = g.since(pop)
        fx.sparks(c, 0, 0, dt, [g.acc, g.acc2, K.PAPER], 22, 4, r1 * 1.3, 26)
        K.ripple(c, 0, 0, dt, g.acc, r1 * 1.4, 8)


def timeline(c, g, el_t, d):
    """时间轴：points [(标签, 说明)] 自左向右在 b0 + i*step 拍点亮。"""
    pts = d["points"]
    b0, step = d.get("b0", 0), d.get("step", 2)
    w = d.get("w", 860)
    n = len(pts)
    xs = [-w / 2 + w * i / (n - 1) for i in range(n)]
    K.seg(c, xs[0], 0, xs[-1], 0, K.LINE, 10)
    lit = clamp01(g.span(b0, b0 + (n - 1) * step, ease_out))
    K.seg(c, xs[0], 0, lerp(xs[0], xs[-1], lit), 0, g.acc, 10)
    for i, (lab, sub) in enumerate(pts):
        st = fx.word_pop(g.since(b0 + i * step))
        on = st is not None
        a, s_, _ = st if on else (1, 1, 0)
        K.dot(c, xs[i], 0, 22 * (s_ if on else 1), g.acc if on else K.LINE)
        if on:
            K.text(c, lab, xs[i], -70, 44, "black", g.acc, a)
            K.text(c, sub, xs[i], 72, 40, "serif_black", K.INK, a)


def two_lines(c, g, el_t, d):
    """两条一起上升的曲线（示意）：“条件”与“期望”，差距（=幸福感）始终不大。"""
    w, h = d.get("w", 760), d.get("h", 460)
    k = g.span(d.get("b0", 0), d.get("b1", 8))
    K.seg(c, -w / 2, h / 2, w / 2, h / 2, K.INK, 6)
    K.seg(c, -w / 2, h / 2, -w / 2, -h / 2, K.INK, 6)
    for name, col, off in (("生活条件", g.acc, 0.0), ("期望", K.RED, 0.12)):
        p = skia.Path()
        steps = max(2, int(40 * k))
        for i in range(steps + 1):
            u = k * i / steps
            xx = -w / 2 + u * w
            yy = h / 2 - (0.12 + off + 0.7 * u ** 1.3) * h
            (p.moveTo if i == 0 else p.lineTo)(xx, yy)
        c.drawPath(p, K.paint(col, 1, stroke=10))
        if k > 0.05:
            K.text(c, name, -w / 2 + k * w - 10, h / 2 - (0.12 + off + 0.7 * k ** 1.3) * h - 46, 38, "serif_black", col,
                   1, "right")


# ---------------------------------------------------------------- 重做版：互动小游戏元件

from scarcity.art import choice, countdown, memo, toasts  # noqa: E402,F401


def pick_cards(c, g, el_t, d):
    """选卡片：cards [(图标, 文字, 是否正确)] 两行排开，b0 起每半拍弹出一张；reveal 拍起正确的发光打勾，其余变暗。"""
    cards = d["cards"]
    cols = d.get("cols", 3)
    w, h, gx, gy = 280, 250, 30, 40
    rows = (len(cards) + cols - 1) // cols
    rev = g.since(d.get("reveal", 99))
    for i, (ic, txt, ok) in enumerate(cards):
        r, j = divmod(i, cols)
        x = (j - (cols - 1) / 2) * (w + gx)
        y = (r - (rows - 1) / 2) * (h + gy)
        st = fx.word_pop(g.since(d.get("b0", 0) + i * 0.5))
        if st is None:
            continue
        a, s_, _ = st
        if rev >= 0:
            k = clamp01(rev / 0.3)
            if ok:
                fx.glow(c, x, y, 220, K.GOLD, 0.35 * k + 0.15 * g.pulse(5))
                s_ *= 1 + 0.08 * k
            else:
                a *= 1 - 0.6 * k
        with K.at(c, x, y, 0, s_):
            K.card(c, 0, 0, w, h, K.PAPER, a, r=26)
            K.icon(c, ic, 0, -30, 110, g.acc if ok else K.INK2, a, 0.5, 0, 1, 1, K.GOLD)
            K.text(c, txt, 0, 80, 44, "serif_black", K.INK, a)
        if rev >= 0 and ok:
            k = clamp01(rev / 0.3)
            with K.at(c, x + w / 2 - 30, y - h / 2 + 30, 0, 0.5 + 0.5 * ease_out(k)):
                K.icon(c, "check", 0, 0, 80, K.GREEN, k, 0.5)


def day_clock(c, g, el_t, d):
    """把人类史压缩成一天：表盘 0–24 时；marks [(时刻小时, 标签, 出现拍)] 依次在表盘上点亮并标注，指针扫到最新标记。"""
    R = d.get("R", 300)
    K.dot(c, 0, 0, R, K.PAPER)
    K.ring(c, 0, 0, R, K.INK, 10)
    for hh in range(24):
        ang = math.radians(hh / 24 * 360 - 90)
        r0 = R * (0.86 if hh % 6 else 0.78)
        K.seg(c, r0 * math.cos(ang), r0 * math.sin(ang), R * 0.95 * math.cos(ang), R * 0.95 * math.sin(ang), K.INK2,
              4 if hh % 6 else 8)
    for hh, lab in ((0, "0点"), (6, "6点"), (12, "12点"), (18, "18点")):
        ang = math.radians(hh / 24 * 360 - 90)
        K.text(c, lab, R * 0.62 * math.cos(ang), R * 0.62 * math.sin(ang), 34, "sans_medium", K.INK3)
    hand = 0.0
    for hh, lab, b in d.get("marks", []):
        k = clamp01(g.since(b) / 0.5)
        if k <= 0:
            continue
        hand = hh * ease_out(k) if hand == 0 else hand + (hh - hand) * ease_out(k)
        ang = math.radians(hh / 24 * 360 - 90)
        x, y = R * math.cos(ang), R * math.sin(ang)
        K.dot(c, x, y, 18, K.RED)
        lx, ly = (R + 120) * math.cos(ang), (R + 70) * math.sin(ang)
        with K.at(c, lx, ly, 0, 0.6 + 0.4 * ease_out(k)):
            K.pill(c, 0, 0, lab, 36, g.acc, K.PAPER, k)
    ang = math.radians(hand / 24 * 360 - 90)
    K.seg(c, 0, 0, R * 0.8 * math.cos(ang), R * 0.8 * math.sin(ang), K.RED, 12)
    K.dot(c, 0, 0, 20, K.RED)
