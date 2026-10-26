"""《系统之美》02–04 讲的专用元件：浴缸（存量与流量）、恒温器、变凉的咖啡、体重曲线（设定点）、
滚雪球、复利柱、回路图（带中心符号）、存钱罐、学习曲线对比。坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_out, lerp
from scarcity.art import GROUND_Y, ground  # noqa: F401
from scarcity.art import cycle  # noqa: F401
from zizhi.art import thing  # noqa: F401

WATER = "#6FA3C8"
TUB = "#E9E4DA"
STEEL = "#8C96A0"
WARM = "#D9593A"
COOL = "#5B8DB8"


# ---------------------------------------------------------------- 浴缸：存量与流量

def bathtub(c, g, el_t, d):
    """浴缸：水位从 l0 在 b0→b1 拍间变到 l1（0..1）；inflow/outflow 为进出水粗细（0 不流）；
    in_label / out_label / label 为水龙头、排水口、存量的文字；pulse=True 时进水忽大忽小（缓冲）。"""
    w, h = d.get("w", 640), d.get("h", 330)
    lvl = lerp(d.get("l0", 0.3), d.get("l1", 0.3), g.span(d.get("b0", 0), d.get("b1", 3)))
    top, bot = -h / 2, h / 2
    inflow, outflow = d.get("inflow", 0.6), d.get("outflow", 0.6)
    if d.get("pulse"):
        inflow *= 0.35 + 0.65 * abs(math.sin(g.t * 2.2))
    # 水龙头与进水
    K.rr(c, -w / 2 + 40, top - 150, 30, 120, 10, STEEL)
    K.rr(c, -w / 2 + 90, top - 205, 130, 30, 12, STEEL)
    K.dot(c, -w / 2 + 40, top - 215, 26, K.RED if inflow > 0 else STEEL)
    wy = bot - 16 - (h - 40) * lvl
    if inflow > 0.01:
        sw = 10 + 34 * inflow
        K.rr(c, -w / 2 + 40, (top - 90 + wy) / 2, sw, wy - (top - 90), sw / 2, WATER, 0.85)
        for i in range(3):
            yy = top - 90 + ((g.t * 260 + i * 70) % max(1.0, wy - top + 90))
            K.dot(c, -w / 2 + 40, yy, sw * 0.3, K.PAPER, 0.6)
    # 浴缸身
    p = skia.Path()
    p.moveTo(-w / 2, top)
    p.lineTo(w / 2, top)
    p.lineTo(w / 2 - 30, bot)
    p.lineTo(-w / 2 + 30, bot)
    p.close()
    c.drawPath(p, K.paint(TUB))
    # 水
    c.save()
    c.clipPath(p, doAntiAlias=True)
    wp = skia.Path()
    wp.moveTo(-w / 2, bot + 10)
    for i in range(41):
        x = -w / 2 + w * i / 40
        wp.lineTo(x, wy + 6 * math.sin(i * 0.7 + g.t * 3))
    wp.lineTo(w / 2, bot + 10)
    wp.close()
    c.drawPath(wp, K.paint(WATER, 0.9))
    c.restore()
    c.drawPath(p, K.paint(K.shade(TUB, 0.35), 1, 8))
    K.rr(c, -w / 2 + 60, bot + 40, 24, 80, 8, K.shade(TUB, 0.3))
    K.rr(c, w / 2 - 60, bot + 40, 24, 80, 8, K.shade(TUB, 0.3))
    # 排水
    if outflow > 0.01:
        sw = 10 + 34 * outflow
        K.rr(c, w / 2 - 110, bot + 70, sw, 120, sw / 2, WATER, 0.8)
        for i in range(2):
            yy = bot + 20 + ((g.t * 220 + i * 60) % 110)
            K.dot(c, w / 2 - 110, yy, sw * 0.3, K.PAPER, 0.6)
    K.ring(c, w / 2 - 110, bot - 8, 16, STEEL, 6)
    if d.get("in_label"):
        K.pill(c, -w / 2 + 170, top - 270, d["in_label"], 42, K.GREEN, K.PAPER)
    if d.get("out_label"):
        K.pill(c, w / 2 - 110, bot + 175, d["out_label"], 42, K.RED, K.PAPER)
    if d.get("label"):
        K.pill(c, 60, max(wy, top + 40) + 70 if lvl < 0.55 else wy + 70, d["label"], 46, g.acc, K.PAPER)


# ---------------------------------------------------------------- 恒温器

def thermostat(c, g, el_t, d):
    """恒温器：温度计读数从 t0 在 b0→b1 拍间趋近设定值 target；低于设定值时暖气片发红，达到后熄灭。"""
    t0, tgt = d.get("t0", 12), d.get("target", 22)
    k = g.span(d.get("b0", 0), d.get("b1", 3))
    temp = lerp(t0, tgt, 1 - (1 - k) ** 2)
    on = abs(tgt - temp) > 0.6
    # 设定面板
    K.card(c, -200, -60, 300, 380, K.PAPER, 1, r=30, accent=g.acc)
    K.text(c, "设定", -200, -200, 40, "sans_medium", K.INK2)
    K.text(c, f"{tgt:.0f}°", -200, -110, 110, "black", g.acc)
    K.text(c, "当前", -200, 10, 38, "sans_medium", K.INK2)
    K.text(c, f"{temp:.0f}°", -200, 80, 76, "black", WARM if temp < tgt - 0.6 else (COOL if temp > tgt + 0.6 else K.GREEN))
    # 温度计
    K.rr(c, 90, -60, 60, 400, 30, K.PAPER)
    K.rr_stroke(c, 90, -60, 60, 400, 30, K.INK2, 5)
    hh = 330 * clamp01((temp - 0) / 35)
    K.rr(c, 90, 120 - hh / 2, 30, hh, 15, WARM)
    K.dot(c, 90, 150, 44, WARM)
    ty = 120 - 330 * tgt / 35
    K.seg(c, 50, ty, 130, ty, g.acc, 6)
    # 暖气片
    for i in range(5):
        x = 260 + i * 46
        K.rr(c, x, 40, 34, 260, 14, WARM if on else STEEL)
        if on:
            for j in range(2):
                yy = -120 - ((g.t * 90 + j * 50 + i * 17) % 100)
                K.seg(c, x - 6, yy, x + 6, yy - 30, WARM, 5, 0.4)


# ---------------------------------------------------------------- 一杯变凉的咖啡

def coffee(c, g, el_t, d):
    """咖啡：温度从 hot 在 b0→b1 拍间降到室温 room（先快后慢），热气随温度减少；右侧温度条。"""
    hot, room = d.get("hot", 80), d.get("room", 22)
    k = g.span(d.get("b0", 0), d.get("b1", 3), ease=lambda x: x)
    temp = room + (hot - room) * math.exp(-3.2 * k)
    heat = (temp - room) / (hot - room)
    K.rr(c, -80, 120, 300, 260, 40, K.PAPER)
    K.rr_stroke(c, -80, 120, 300, 260, 40, K.INK2, 6)
    K.ring(c, 90, 110, 60, K.INK2, 18)
    K.rr(c, -80, 20, 260, 50, 20, "#6B4A33")
    K.rr(c, -80, 270, 360, 30, 14, K.LINE)
    for i in range(3):
        a = heat * (0.5 + 0.5 * math.sin(g.t * 3 + i))
        p = skia.Path()
        x0 = -150 + i * 70
        p.moveTo(x0, -20)
        p.cubicTo(x0 - 30, -80, x0 + 30, -120, x0, -190)
        c.drawPath(p, K.paint(K.INK3, a, 10))
    K.rr(c, 300, 60, 50, 340, 25, K.PAPER)
    K.rr_stroke(c, 300, 60, 50, 340, 25, K.INK2, 5)
    hh = 300 * heat
    K.rr(c, 300, 220 - hh / 2, 26, max(1.0, hh), 13, WARM if heat > 0.3 else COOL)
    K.text(c, f"{temp:.0f}°", 300, -160, 60, "black", WARM if heat > 0.3 else COOL)
    if d.get("room_label", True):
        K.pill(c, 300, 270, "室温", 34, K.INK2, K.PAPER)


# ---------------------------------------------------------------- 体重曲线：被拉回设定点

def rebound(c, g, el_t, d):
    """体重曲线（示意）：先降、再被拉回虚线“设定点”；b0→b1 拍间画出；drop_at 拍标出最低点。"""
    w, h = 820, 460
    K.seg(c, -w / 2, h / 2, w / 2, h / 2, K.INK2, 6)
    K.seg(c, -w / 2, h / 2, -w / 2, -h / 2, K.INK2, 6)
    sp = -h * 0.2
    for i in range(14):
        x = -w / 2 + 20 + i * 60
        K.seg(c, x, sp, x + 30, sp, g.acc, 5, 0.8)
    K.pill(c, w / 2 - 90, sp - 50, d.get("set_label", "设定点"), 36, g.acc, K.PAPER)

    def f(u):
        if u < 0.4:
            return sp + 220 * math.sin(u / 0.4 * math.pi / 2)
        return sp + 220 * math.exp(-(u - 0.4) * 6) * math.cos((u - 0.4) * 3)

    k = g.span(d.get("b0", 0), d.get("b1", 3), ease=lambda x: x)
    p = skia.Path()
    n = max(1, int(80 * k))
    for i in range(n + 1):
        u = k * i / n
        (p.moveTo if i == 0 else p.lineTo)(-w / 2 + u * w, f(u))
    c.drawPath(p, K.paint(WARM, 1, 12))
    x, y = -w / 2 + k * w, f(k)
    K.dot(c, x, y, 20, WARM)
    K.text(c, d.get("y_label", "体重"), -w / 2 + 70, -h / 2 + 20, 38, "sans_medium", K.INK2)
    st = fx.word_pop(g.since(d.get("drop_at", 99)))
    if st:
        a, s_, _ = st
        with K.at(c, -w / 2 + 0.4 * w, sp + 290, 0, s_):
            K.pill(c, 0, 0, d.get("low_label", "瘦下来了"), 38, K.GREEN, K.PAPER, a)


# ---------------------------------------------------------------- 回路图（带中心符号）

def loop_sign(c, g, el_t, d):
    """回路中心徽记：圆圈里一个字（调 / 增），sign 拍弹出并随拍轻转。"""
    st = fx.word_pop(g.since(d.get("at_b", 0)))
    if not st:
        return
    a, s_, _ = st
    col = d.get("color", g.acc)
    with K.at(c, 0, 0, 8 * math.sin(g.t * 2), s_):
        K.dot(c, 0, 0, 90, K.PAPER, a)
        K.ring(c, 0, 0, 90, col, 10, a)
        K.text(c, d.get("text", "调"), 0, 0, 90, "serif_black", col, a)


# ---------------------------------------------------------------- 滚雪球

def snowball(c, g, el_t, d):
    """雪坡：雪球在 b0→b1 拍间从坡顶滚下并越滚越大（示意）。"""
    K.poly(c, [(-460, -260), (460, 300), (-460, 300)], "#EEF2F4")
    K.seg(c, -460, -260, 460, 300, K.shade("#EEF2F4", 0.25), 6)
    k = g.span(d.get("b0", 0), d.get("b1", 3), ease=lambda x: x * x)
    r = 26 + 150 * k
    x = lerp(-400, 300, k)
    y = lerp(-260, 300, (x + 460) / 920) * 1.0 - r * 1.05
    y = -260 + (x + 460) / 920 * 560 - r * 1.1
    with K.at(c, x, y, g.t * 260 * (0.3 + k)):
        K.dot(c, 0, 0, r, "#FBFDFE")
        K.ring(c, 0, 0, r, K.shade("#EEF2F4", 0.35), 6)
        K.seg(c, -r * 0.5, -r * 0.2, r * 0.3, r * 0.4, K.shade("#EEF2F4", 0.3), 5)
    if d.get("label"):
        K.pill(c, x, y - r - 50, d["label"], 40, g.acc, K.PAPER)


# ---------------------------------------------------------------- 复利柱（示意）

def growth_bars(c, g, el_t, d):
    """一排柱子，第 i 根高度 ∝ rate^i（示意），从 b0 起每 step 拍长出一根；linear=True 时为直线增长对照。"""
    n = d.get("n", 8)
    rate = d.get("rate", 1.45)
    w = 760
    bw = w / n * 0.7
    vals = [(i + 1) if d.get("linear") else rate ** i for i in range(n)]
    vmax = max(vals) if not d.get("vmax") else d["vmax"]
    K.seg(c, -w / 2 - 20, 240, w / 2 + 20, 240, K.INK2, 6)
    for i, v in enumerate(vals):
        k = ease_out(clamp01(g.since(d.get("b0", 0) + i * d.get("step", 0.4)) / 0.3))
        if k <= 0:
            continue
        hh = 440 * v / vmax * k
        x = -w / 2 + w / n * (i + 0.5)
        K.rr(c, x, 240 - hh / 2, bw, max(1.0, hh), 8, d.get("color", g.acc))
    if d.get("label"):
        K.pill(c, -w / 2 + 120, -200, d["label"], 40, d.get("color", g.acc), K.PAPER)


# ---------------------------------------------------------------- 两条学习曲线

def two_curves(c, g, el_t, d):
    """两条曲线（示意）：直线慢慢涨（“线性”）与先慢后快的指数曲线（“增强回路”），b0→b1 拍间画出。"""
    w, h = 820, 480
    K.seg(c, -w / 2, h / 2, w / 2, h / 2, K.INK2, 6)
    K.seg(c, -w / 2, h / 2, -w / 2, -h / 2, K.INK2, 6)
    k = g.span(d.get("b0", 0), d.get("b1", 3), ease=lambda x: x)
    for kind, col, lab in (("lin", K.INK3, d.get("lin_label", "原地努力")), ("exp", g.acc, d.get("exp_label", "越学越快"))):
        p = skia.Path()
        n = max(1, int(60 * k))
        for i in range(n + 1):
            u = k * i / n
            v = 0.45 * u if kind == "lin" else (math.exp(2.6 * u) - 1) / (math.exp(2.6) - 1)
            (p.moveTo if i == 0 else p.lineTo)(-w / 2 + u * w, h / 2 - v * h * 0.95)
        c.drawPath(p, K.paint(col, 1, 12))
        if k > 0.95:
            v = 0.45 if kind == "lin" else 1.0
            K.pill(c, w / 2 - 120, h / 2 - v * h * 0.95 - 50, lab, 38, col, K.PAPER)


# ---------------------------------------------------------------- 存钱罐 / 账户

def jar(c, g, el_t, d):
    """透明罐子：罐中硬币层从 l0 在 b0→b1 拍间变到 l1；label 在罐身。"""
    lvl = lerp(d.get("l0", 0.2), d.get("l1", 0.2), g.span(d.get("b0", 0), d.get("b1", 3)))
    K.rr(c, 0, 0, 340, 420, 60, "#F4F8FA")
    hh = 380 * lvl
    K.rr(c, 0, 190 - hh / 2, 300, max(1.0, hh), 40, K.GOLD)
    for i in range(int(lvl * 8)):
        K.seg(c, -120, 190 - (i + 1) * 380 / 8 * 0.95, 120, 190 - (i + 1) * 380 / 8 * 0.95, K.shade(K.GOLD, 0.2), 4)
    K.rr_stroke(c, 0, 0, 340, 420, 60, K.INK2, 6)
    K.rr(c, 0, -230, 220, 50, 16, K.shade(K.GOLD, 0.25))
    if d.get("label"):
        K.pill(c, 0, -300, d["label"], 42, g.acc, K.PAPER)
