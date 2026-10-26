"""《系统之美》08–10 讲专用元件：目标线下滑（目标侵蚀）、回路图、双柱对比、咖啡杯、拐杖人、压症状、杠杆撬石、
十二级杠杆阶梯、旋钮。坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from maoxuan.art import DESK, PAPER2, RED  # noqa: F401
from maoxuan.art_d import chips, ink_crowd  # noqa: F401
from scarcity.art import GROUND_Y, ground  # noqa: F401
from zizhi.art import magnifier, thing  # noqa: F401

COFFEE = "#6B4A33"
ROCK = "#8C8A80"


# ---------------------------------------------------------------- 目标侵蚀

def goal_line(c, g, el_t, d):
    """坐标图：灰色“表现”折线从 b0 到 b1 逐段画出；红色“目标”横线按 mode 变化：
    drift = 每次表现跌破目标后，下一拍目标降到表现附近（越降越低）；fixed = 目标固定不动；
    ratchet = 目标只跟着最好表现往上走。"""
    w, h = 860, 520
    mode = d.get("mode", "drift")
    K.card(c, 0, 0, w + 60, h + 90, K.PAPER, 1, r=18)
    K.seg(c, -w / 2, h / 2 - 10, w / 2, h / 2 - 10, K.INK2, 5)
    K.seg(c, -w / 2, h / 2 - 10, -w / 2, -h / 2 + 10, K.INK2, 5)
    if mode == "ratchet":
        pts = [0.25, 0.42, 0.36, 0.55, 0.5, 0.68, 0.62, 0.8]
    else:
        pts = d.get("pts", [0.82, 0.7, 0.74, 0.58, 0.62, 0.45, 0.5, 0.32])
    n = len(pts)
    k = g.span(d.get("b0", 0), d.get("b1", 3), ease=lambda x: x)
    m = k * (n - 1)
    xy = [(-w / 2 + 40 + (w - 80) * i / (n - 1), h / 2 - 30 - (h - 80) * v) for i, v in enumerate(pts)]
    p = skia.Path()
    p.moveTo(*xy[0])
    for i in range(1, n):
        if i <= m:
            p.lineTo(*xy[i])
        elif i - 1 < m:
            f = m - (i - 1)
            p.lineTo(lerp(xy[i - 1][0], xy[i][0], f), lerp(xy[i - 1][1], xy[i][1], f))
    c.drawPath(p, K.paint(K.INK2, 1, 9))
    seen = pts[: int(m) + 1]
    if mode == "drift":
        gv = 0.9
        for v in seen:
            if v < gv:
                gv = v + 0.04
    elif mode == "ratchet":
        gv = max(seen) + 0.05
    else:
        gv = d.get("goal", 0.85)
    gy = h / 2 - 30 - (h - 80) * gv
    K.seg(c, -w / 2 + 20, gy, w / 2 - 20, gy, RED, 7, 0.9)
    K.pill(c, w / 2 - 90, gy - 40, d.get("goal_label", "目标"), 34, RED, K.PAPER)
    K.text(c, d.get("perf_label", "表现"), -w / 2 + 70, -h / 2 + 30, 34, "sans_medium", K.INK2)
    if mode == "drift" and m > 0.5:
        a = clamp01(m - 0.5)
        K.arrow(c, (w / 2 - 60, -h / 2 + 60), (w / 2 - 60, gy - 90), RED, 8, a, a, 0, 28)


def sizes(c, g, el_t, d):
    """好坏记忆不对称：左“做到了”小卡、右“没做到”大卡；b 拍起右卡继续膨胀。even=True 时两张一样大。"""
    k = ease_out(clamp01(g.since(d.get("b", 1)) / 0.5))
    even = d.get("even", False)
    sl = 1.0 if even else 0.7
    sr = 1.0 if even else 1.0 + 0.45 * k
    with K.at(c, -230, 0, -3, sl):
        K.card(c, 0, 0, 340, 220, K.PAPER, 1, r=20)
        K.icon(c, "check", 0, -30, 90, K.GREEN, 1, 0.3)
        K.text(c, "做到了", 0, 60, 46, "serif_black", K.INK)
    with K.at(c, 230, 0, 3, sr):
        K.card(c, 0, 0, 340, 220, K.PAPER, 1, r=20)
        K.icon(c, "cross", 0, -30, 90, K.RED, 1, 0.3)
        K.text(c, "没做到", 0, 60, 46, "serif_black", K.INK)


def frog(c, g, el_t, d):
    """温水青蛙：锅里一只青蛙，火从 b0 起慢慢变大，温度计慢慢上升。"""
    k = g.span(d.get("b0", 0), d.get("b1", 3), ease=lambda x: x)
    K.poly(c, [(-260, -40), (260, -40), (220, 180), (-220, 180)], "#5E6670")
    K.rr(c, 0, -50, 560, 30, 12, "#4A525C")
    c.drawOval(skia.Rect.MakeXYWH(-230, -70, 460, 60), K.paint("#9CC3D6", 0.9))
    with K.at(c, 0, -80):
        c.drawOval(skia.Rect.MakeXYWH(-70, -40, 140, 70), K.paint("#7FA85A"))
        for sx in (-35, 35):
            K.dot(c, sx, -40, 22, "#7FA85A")
            K.dot(c, sx, -42, 10, K.PAPER)
            K.dot(c, sx, -42, 5, K.INK)
    for i in range(5):
        x = -160 + i * 80
        hgt = 40 + 50 * k + 10 * math.sin(g.t * 9 + i)
        p = skia.Path()
        p.moveTo(x - 25, 260)
        p.quadTo(x - 18, 260 - hgt * 0.6, x, 260 - hgt)
        p.quadTo(x + 18, 260 - hgt * 0.6, x + 25, 260)
        p.close()
        c.drawPath(p, K.paint("#E08A3A", 0.85))
    K.rr(c, 380, -40, 40, 320, 20, K.PAPER)
    K.rr_stroke(c, 380, -40, 40, 320, 20, K.INK2, 4)
    th = 60 + 220 * k
    K.rr(c, 380, 110 - th / 2, 22, th, 11, RED)
    K.dot(c, 380, 130, 34, RED)


# ---------------------------------------------------------------- 回路与对比

def loop_diagram(c, g, el_t, d):
    """回路图：names 均匀排在圆上，从 b0 起每 step 拍亮起一个并画出指向下一个的箭头；中心按 loop 标 R（增强）或 B（调节）。"""
    names = d["names"]
    n = len(names)
    r = d.get("r", 260)
    b0, step = d.get("b0", 0), d.get("step", 0.5)
    K.ring(c, 0, 0, r, K.LINE, 10)
    for i, s in enumerate(names):
        a0 = -math.pi / 2 + i * 2 * math.pi / n
        a1 = -math.pi / 2 + (i + 1) * 2 * math.pi / n
        on = g.since(b0 + i * step) >= 0
        if on:
            pa = g.p(b0 + i * step, 0.4)
            path = skia.Path()
            path.addArc(skia.Rect.MakeXYWH(-r, -r, 2 * r, 2 * r), math.degrees(a0) + 14,
                        (math.degrees(a1 - a0) - 28) * pa)
            c.drawPath(path, K.paint(g.acc, 1, 10))
        x, y = math.cos(a0) * r, math.sin(a0) * r
        K.pill(c, x, y, s, 42, g.acc if on else K.INK3, K.PAPER)
    kind = d.get("loop", "R")
    st = fx.word_pop(g.since(b0 + n * step))
    if st:
        a, s_, _ = st
        with K.at(c, 0, 0, 0, s_):
            K.dot(c, 0, 0, 80, K.GOLD if kind == "R" else K.GREEN, a)
            K.text(c, kind, 0, 0, 90, "black", K.PAPER, a)
        if d.get("down"):
            K.arrow(c, (0, 110), (0, 200), RED, 10, a, a, 0, 30)


def twin_bars(c, g, el_t, d):
    """两根柱子：bars [(名称, 起始高, 结束高, 颜色)]，从 b0 到 b1 拍间从起始高变化到结束高。"""
    k = g.span(d.get("b0", 0), d.get("b1", 3))
    bars = d["bars"]
    hmax = 480
    K.seg(c, -360, 280, 360, 280, K.INK2, 6)
    for i, (name, h0, h1, col) in enumerate(bars):
        x = -170 + i * 340
        hh = hmax * lerp(h0, h1, k)
        K.rr(c, x, 280 - hh / 2, 180, max(2.0, hh), 14, col)
        K.text(c, name, x, 340, 46, "serif_black", K.INK)
        if h1 != h0 and k > 0.05:
            up = h1 > h0
            K.arrow(c, (x + 140, 200 if up else 40 - hmax * 0.4), (x + 140, 40 - hmax * 0.4 if up else 200),
                    K.GREEN if up else RED, 9, k, k, 0, 26)


# ---------------------------------------------------------------- 咖啡与拐杖

def cup(c, x, y, s, alpha=1.0, steam_t=0.0):
    """一杯咖啡：杯身 + 把手 + 两缕热气。"""
    K.rr(c, x, y, s, s * 1.1, s * 0.16, K.PAPER, alpha)
    K.rr_stroke(c, x, y, s, s * 1.1, s * 0.16, K.INK2, s * 0.05, alpha)
    K.rr(c, x, y - s * 0.38, s * 0.86, s * 0.16, s * 0.06, COFFEE, alpha)
    K.ring(c, x + s * 0.58, y, s * 0.2, K.INK2, s * 0.06, alpha)
    for j in (-1, 1):
        p = skia.Path()
        p.moveTo(x + j * s * 0.18, y - s * 0.65)
        for q in range(1, 5):
            p.lineTo(x + j * s * 0.18 + math.sin(steam_t * 4 + q + j) * s * 0.08, y - s * (0.65 + q * 0.12))
        c.drawPath(p, K.paint(K.INK3, 0.6 * alpha, s * 0.04))


def cups(c, g, el_t, d):
    """咖啡杯一字排开：第 i 杯在 b0 + i*step 拍落下。"""
    n = d.get("n", 3)
    s = d.get("s", 150)
    gap = d.get("gap", 210)
    for i in range(n):
        st = fx.word_pop(g.since(d.get("b0", 0) + i * d.get("step", 1)))
        if not st:
            continue
        a, s_, _ = st
        with K.at(c, -(n - 1) * gap / 2 + i * gap, 0, (-4, 3, -2, 5)[i % 4], s_):
            cup(c, 0, 0, s, a, g.t)


def crutch_prop(c, h):
    """手持拐杖（从手到地面）。"""
    x, y = h
    K.seg(c, x, y - 10, x + 10, -6, DESK, 12)
    K.seg(c, x - 26, y - 14, x + 22, y - 14, DESK, 12)


def crutch_man(c, g, el_t, d):
    """拄拐杖的人：drop 拍起拐杖抽走（weak=True 时腿软跌坐），否则拄着站。"""
    s = d.get("s", 330)
    drop = d.get("drop")
    if drop is not None and g.since(drop) >= 0:
        k = clamp01(g.since(drop) / 0.35)
        weak = d.get("weak", True)
        pose = K.blend(K.pose("stand"), K.pose("sit_sad" if weak else "cheer"), k)
        K.figure(c, 0, 0, s, pose, None, mood="surprised" if weak else "happy", role=d.get("role", "worker"))
        with K.at(c, 160 + 60 * k, -40, 70 * k):
            K.seg(c, 0, -160, 0, 120, DESK, 12)
    else:
        K.figure(c, 0, 0, s, "give", None, mood=d.get("mood", "calm"), role=d.get("role", "worker"), prop=crutch_prop)


def press(c, g, el_t, d):
    """压症状：弹簧上标“困”的方块，b 拍一只咖啡杯压下去，弹簧压扁；released 拍后杯子移开，方块弹得更高。"""
    b, rel = d.get("b", 1), d.get("rel", 99)
    k = ease_out(clamp01(g.since(b) / 0.3))
    r = ease_out(clamp01(g.since(rel) / 0.35))
    hgt = lerp(220, 90, k) if r <= 0 else lerp(90, 300, r)
    coils = 6
    p = skia.Path()
    p.moveTo(0, 260)
    for i in range(1, coils * 2 + 1):
        p.lineTo((-60 if i % 2 else 60), 260 - hgt * i / (coils * 2))
    c.drawPath(p, K.paint(K.INK2, 1, 8))
    by = 260 - hgt - 70
    K.rr(c, 0, by, 220, 140, 18, RED)
    K.text(c, d.get("label", "困"), 0, by, 80, "serif_black", K.PAPER)
    if k > 0 and r < 1:
        with K.at(c, lerp(0, 320, r), by - 160):
            cup(c, 0, 0, 160, 1 - r, g.t)
    K.seg(c, -200, 262, 200, 262, K.INK2, 6)


# ---------------------------------------------------------------- 杠杆

def lever(c, g, el_t, d):
    """杠杆撬石：长板 + 三角支点 + 右端大石头（label）；push 拍左端被压下，石头被撬起。wrong=True 时反向：石头压回去。"""
    push = d.get("push", 1)
    k = ease_out(clamp01(g.since(push) / 0.5))
    wrong = d.get("wrong", False)
    ang = lerp(-10, 14 if not wrong else -22, k)
    fxp = d.get("fulcrum", 140)
    K.poly(c, [(fxp - 70, 260), (fxp + 70, 260), (fxp, 160)], K.INK2)
    with K.at(c, fxp, 150, ang):
        K.rr(c, -120, 0, 860, 28, 12, DESK)
        with K.at(c, 230, -110, -ang):
            c.drawOval(skia.Rect.MakeXYWH(-130, -90, 260, 190), K.paint(ROCK))
            c.drawOval(skia.Rect.MakeXYWH(-130, -90, 260, 190), K.paint(K.shade(ROCK, 0.3), 1, 6))
            K.text(c, d.get("label", "问题"), 0, 0, 60, "serif_black", K.PAPER)
    rad = math.radians(ang)
    px = fxp + (-520) * math.cos(rad)
    py = 150 + (-520) * math.sin(rad)
    K.figure(c, px - 30, min(262.0, py + 230), 260, "push" if k > 0 else "stand", None, mood="happy" if not wrong else "worried",
             role=d.get("role", "worker"))
    if d.get("label_small"):
        K.pill(c, px, py - 60, d["label_small"], 34, g.acc, K.PAPER)


LEVERS = [
    "超越范式", "范式：底层信念", "系统目标", "自组织：自我演化", "规则：奖励与惩罚", "信息流：谁知道什么",
    "增强回路的强度", "调节回路的强度", "延迟的长短", "存量流量的结构", "缓冲的大小", "常数、参数、数字",
]


def ladder12(c, g, el_t, d):
    """十二级杠杆阶梯：自下而上 12→1，b0 起每 step 拍点亮一级；hi 为高亮的等级（1–12），其它变淡；
    marker 拍时一个小人站上 hi 那一级。"""
    b0, step = d.get("b0", 0), d.get("step", 0.25)
    his = d.get("hi", ())
    if isinstance(his, int):
        his = (his,)
    rh, w0 = 66, 360
    for i in range(12):
        lvl = 12 - i
        y = 380 - i * rh
        w = w0 + i * 26
        x = -160 + i * 26
        on = g.since(b0 + i * step) >= 0
        hi = lvl in his
        if not on:
            continue
        col = g.acc if hi else (K.tint(g.acc, 0.6) if not his else "#DDD2BE")
        K.rr(c, x, y, w, rh - 10, 10, col)
        K.text(c, f"{lvl}", x - w / 2 + 34, y, 34, "black", K.PAPER if (hi or not his) else K.INK3)
        lab = LEVERS[lvl - 1]
        size = min(32.0, 32 * (w - 90) / K.text_w(lab, 32, "serif_black"))
        K.text(c, lab, x - w / 2 + 64, y, size, "serif_black", K.PAPER if (hi or not his) else K.INK3, 1, "left")
    m = d.get("marker")
    if m is not None and his and g.since(m) >= 0:
        i = 12 - his[0]
        y = 380 - i * rh - rh / 2 + 6
        x = -160 + i * 26 - (w0 + i * 26) / 2 - 70
        K.figure(c, x, y + rh / 2 - 6, 150, "cheer" if his[0] <= 3 else "point", None, mood="happy", face=1, role="worker")
    if d.get("arrow"):
        a = clamp01(g.since(d["arrow"]) / 0.4)
        K.arrow(c, (440, 360), (440, -330), K.GOLD, 12, a, a, 0, 34)
        K.text(c, "越有力", 440, -380, 40, "serif_black", K.GOLD, a)


def knob(c, g, el_t, d):
    """调参数旋钮：每拍拧一下（指针来回），旁边“效果”指示灯始终不亮。"""
    t = g.since(d.get("b0", 0))
    ang = 50 * math.sin(max(0.0, t) * 5)
    K.dot(c, -150, 0, 170, K.PAPER)
    K.ring(c, -150, 0, 170, K.INK2, 8)
    for i in range(9):
        a = math.radians(-135 + i * 33.75)
        K.seg(c, -150 + math.sin(a) * 140, -math.cos(a) * 140, -150 + math.sin(a) * 160, -math.cos(a) * 160, K.INK2, 5)
    with K.at(c, -150, 0, ang):
        K.rr(c, 0, -70, 20, 140, 10, RED)
    K.dot(c, -150, 0, 30, K.INK2)
    K.text(c, d.get("label", "参数"), -150, 220, 46, "serif_black", K.INK)
    K.dot(c, 230, 0, 80, "#DDD2BE")
    K.ring(c, 230, 0, 80, K.INK2, 6)
    K.text(c, "效果", 230, 130, 42, "serif_black", K.INK3)
