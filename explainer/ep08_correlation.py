"""第 08 期：相关不等于因果（Correlation Does Not Imply Causation）。曲线均为教学示意，非真实城市数据。"""

import math

import numpy as np
import skia

from .engine import (BLUE, CREAM, GOLD, GRAY, INK, KRAFT, LGRAY, PALEBLUE, PALEGOLD, PALERED, PAPER, RED, SKIN,
                     Episode, Shot, arrow, circ, clamp01, col, crect, dline, ease_back, ease_in, ease_io, ease_out,
                     glow, lerp, oval, partial_stroke, poly, prog, rect, shape, stroke, text, xf)
from .props import (LIN, OWNER, big_title, bubble, burst, bulb, card, card_end, check, cross, magnifier, person, pill,
                    sparkle, thought)

PINK = "#F2B8C6"


# ------------------------------------------------------------------ 元件

def cone(c, x, y, s=1.0, a=1.0):
    """冰淇淋甜筒，(x, y) 为筒尖。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    poly(c, [(-44, -120), (44, -120), (0, 0)], "#E2B66E", INK, 5, rough=False)
    for i in range(3):
        stroke(c, [(-34 + i * 24, -118), (-8 + i * 12, -34)], "#B9873A", 3)
    circ(c, 0, -150, 52, PINK, INK, 5, rough=False)
    circ(c, 0, -210, 44, CREAM, INK, 5, rough=False)
    circ(c, 4, -262, 12, RED, INK, 4, rough=False)
    if a < 1:
        c.restore()
    c.restore()


def ac_unit(c, cx, cy, s=1.0, wind=0.0, a=1.0):
    """壁挂空调，(cx, cy) 为中心，wind∈[0,1] 控制冷风线。"""
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    rect(c, -130, -48, 260, 96, 22, "#E8EEF2", INK, 6, rough=False)
    rect(c, -108, 14, 216, 18, 8, "#B9C7D1", INK, 4, rough=False)
    circ(c, 96, -18, 6, BLUE, INK, 3, rough=False)
    stroke(c, [(-100, -24), (-30, -24)], LGRAY, 5)
    if wind > 0:
        for i in range(3):
            ph = (wind * 2 + i * 0.33) % 1.0
            x0 = -70 + i * 70
            pts = [(x0, 60 + ph * 20), (x0 - 12, 84 + ph * 20), (x0 + 10, 108 + ph * 20), (x0 - 6, 132 + ph * 20)]
            stroke(c, pts, BLUE, 5, 0.9 * (1 - ph), smooth=True)
    if a < 1:
        c.restore()
    c.restore()


def thermometer(c, cx, cy, h, level, a=1.0, hot=False):
    """温度计，(cx, cy) 为顶端中心，level∈[0,1]。"""
    c.save()
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    rect(c, cx - 32, cy, 64, h, 32, CREAM, INK, 7, rough=False)
    circ(c, cx, cy + h + 26, 56, CREAM, INK, 7, rough=False)
    circ(c, cx, cy + h + 26, 42, RED, None, 0, rough=False)
    top = cy + h - h * 0.86 * level
    rect(c, cx - 14, top, 28, cy + h + 10 - top, 14, RED, None, 0, rough=False)
    for i in range(8):
        y = cy + 40 + i * (h - 70) / 7
        stroke(c, [(cx + 40, y), (cx + 62 - (8 if i % 2 else 0), y)], INK, 4)
    if a < 1:
        c.restore()
    c.restore()


def sun(c, x, y, r, t, a=1.0):
    glow(c, x, y, r * 3.2, GOLD, 0.5 * a)
    for i in range(12):
        ang = math.radians(i * 30 + t * 30)
        stroke(c, [(x + math.cos(ang) * r * 1.25, y + math.sin(ang) * r * 1.25),
                   (x + math.cos(ang) * r * 1.75, y + math.sin(ang) * r * 1.75)], "#E69A2E", 8, a)
    circ(c, x, y, r, "#F5C146", INK, 6, a=a, rough=False)


def shop(c, cx, base, w, h, c1, c2, s=1.0, a=1.0):
    """小店：条纹雨棚 + 立面 + 柜台（中央图标由调用方绘制）。"""
    c.save()
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    rect(c, cx - w / 2, base - h, w, h, 10, CREAM, INK, 6, rough=False)
    rect(c, cx - w / 2 + 24, base - 70, w - 48, 70, 8, KRAFT, INK, 5, rough=False)
    n = 6
    sw = (w + 40) / n
    for i in range(n):
        poly(c, [(cx - w / 2 - 20 + i * sw, base - h - 8), (cx - w / 2 - 20 + (i + 1) * sw, base - h - 8),
                 (cx - w / 2 - 14 + (i + 1) * sw, base - h + 56), (cx - w / 2 - 14 + i * sw, base - h + 56)],
             c1 if i % 2 == 0 else c2, INK, 4, rough=False)
    if a < 1:
        c.restore()
    c.restore()


def bell(x, mu, sd):
    return math.exp(-((x - mu) / sd) ** 2 / 2)


def curve_pts(kind, x0=100, x1=980, ybase=1200, ytop=720, n=48):
    pts = []
    for i in range(n + 1):
        u = i / n
        if kind == 0:   # 冰淇淋
            v = 0.12 + 0.82 * bell(u, 0.55, 0.22) + 0.03 * math.sin(u * 23)
        else:           # 空调：形状相近，略有差异
            v = 0.16 + 0.80 * bell(u, 0.58, 0.20) + 0.035 * math.sin(u * 19 + 1.2)
        pts.append((lerp(x0, x1, u), ybase - (ybase - ytop) * v))
    return pts


# ------------------------------------------------------------------ 镜头

def s_hook(g):
    c, t = g.c, g.t
    glow(c, 540, 900, 560, GOLD, 0.35)
    big_title(c, ["冰淇淋卖得多，", "空调就卖得多？"], 330, t, 108)
    base = 1190
    pl = g.p(0.1, 0.5, ease_back)
    shop(c, 270, base, 380, 420, RED, CREAM, 1.0, clamp01(pl * 2))
    shop(c, 810, base, 380, 420, BLUE, CREAM, 1.0, clamp01(g.p(0.3, 0.5) * 2))
    cone(c, 270, base - 120, 0.75 * max(0.01, pl))
    ac_unit(c, 810, base - 300, 0.95 * max(0.01, g.p(0.3, 0.5, ease_back)), t * 0.8)
    # 销量柱：同步上涨
    for k, (x, colr) in enumerate(((120, "#E0705A"), (660, "#5C8FC4"))):
        for i in range(5):
            q = g.p(0.6 + i * 0.35, 0.4, ease_back)
            if q <= 0:
                continue
            h = 40 + i * 30
            rect(c, x + i * 34, 640 - h * q + 40, 24, h * q, 4, colr, INK, 3, rough=False)
    for x in (270, 810):
        arrow(c, (x - 80, 640), (x + 100, 530), RED, 8, 1.0, 24, g.p(1.2, 0.8))
    if t > 1.6:
        person(c, OWNER, 540, 1300, 0.62 * ease_out(prog(t, 1.6, 0.5)), face="surprise", t=t, armL=(110, 100),
               armR=(-60, -100))


def s_joke(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.35)
    person(c, OWNER, 300, 1320, 1.05, face="happy" if g.cue(0) > 0.4 else "smile", t=t, look=(0, 0),
           armL=(110, 100), armR=(-30, -100), bob=math.sin(t * 2.2) * 3)
    q = g.pc(0, 0.3, 0.6, ease_back)
    if q > 0:
        bubble(c, 540, 560, 840, 124, "我的冰淇淋，带火了空调！", 54, "", CREAM, INK, "black", clamp01(q * 2), max(0.01, q),
               tail_to=(300, 880))
    cone(c, 600, 1150, 0.85 * max(0.01, g.pc(0, 0.6, 0.5, ease_back)))
    ac_unit(c, 900, 960, 0.8 * max(0.01, g.pc(0, 0.9, 0.5, ease_back)), t * 0.8)
    arrow(c, (680, 900), (800, 900), RED, 9, 1.0, 28, g.pc(0, 1.3, 0.8))
    if g.pc(0, 2.0, 0.4) > 0:
        text(c, "？", 740, 860, 90, RED, "black", "c", g.pc(0, 2.0, 0.4), PAPER, 14)


def s_curves(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    x0, x1, yb = 100, 980, 1200
    stroke(c, [(x0 - 20, yb + 10), (x1 + 20, yb + 10)], INK, 5, 1.0)
    stroke(c, [(x0 - 20, yb + 10), (x0 - 20, 690)], INK, 5, 1.0)
    text(c, "时间 →", x1 - 20, yb + 58, 32, GRAY, "sans", "r")
    text(c, "销量 / 订单", x0 - 20, 665, 30, GRAY, "sans", "l")
    p1 = g.pc(0, 0.2, 2.2, ease_io)
    p2 = g.pc(0, 0.4, 2.2, ease_io)
    partial_stroke(c, curve_pts(0), p1, INK, 12, 1.0)
    partial_stroke(c, curve_pts(0), p1, "#E0705A", 7, 1.0)
    partial_stroke(c, curve_pts(1), p2, INK, 12, 1.0)
    partial_stroke(c, curve_pts(1), p2, "#5C8FC4", 7, 1.0)
    a = g.pc(0, 0.3, 0.5, ease_back)
    with xf(c, 280, 560, sx=max(0.01, a)):
        crect(c, 0, 0, 380, 80, 40, PALERED, INK, 5, rough=False)
        text(c, "冰淇淋销量", 24, 14, 36, INK, "sans", "c")
        circ(c, -150, 0, 14, "#E0705A", INK, 3, rough=False)
    with xf(c, 760, 560, sx=max(0.01, a)):
        crect(c, 0, 0, 380, 80, 40, PALEBLUE, INK, 5, rough=False)
        text(c, "空调订单", 24, 14, 36, INK, "sans", "c")
        circ(c, -150, 0, 14, "#5C8FC4", INK, 3, rough=False)
    if g.cue(1) > 0:
        q = g.pc(1, 0.0, 0.5, ease_back)
        with xf(c, 540, 1330, sx=max(0.01, q)):
            text(c, "一起涨 = 一个推动了另一个？", 0, 0, 44, RED, "black", "c", 1.0, PAPER, 10)
    if len(g.shot.cue_t) > 2 and g.cue(2) > 0:
        q = g.pc(2, 0.0, 0.5, ease_back)
        dx = 14 * math.sin(t * 6)
        text(c, "看旁边 →", 860 + dx, 1330, 50, INK, "black", "c", clamp01(q))


def s_reveal(g):
    c, t = g.c, g.t
    glow(c, 540, 820, 560, GOLD, 0.35)
    level = g.pc(0, 0.2, 2.8, ease_io)
    thermometer(c, 540, 470, 360, level)
    sun(c, 850, 560, 62 * (0.7 + 0.3 * level), t, clamp01(level * 2))
    # 冰淇淋和空调
    cone(c, 210, 1130, 0.78)
    ac_unit(c, 860, 1030, 0.9, t * 0.8 * (0.2 + level))
    q1 = g.pc(1, 0.0, 0.8)
    arrow(c, (470, 900), (270, 960), RED, 8, 1.0, 24, q1)
    arrow(c, (610, 900), (800, 940), RED, 8, 1.0, 24, q1)
    if g.cue(1) > 0.2:
        text(c, "想吃冰淇淋", 250, 1230, 38, INK, "sans", "c", clamp01((g.cue(1) - 0.2) * 2))
        text(c, "想买空调", 840, 1230, 38, INK, "sans", "c", clamp01((g.cue(1) - 1.0) * 2))
    sd = g.pc(3, 0.0, 0.5, ease_back) if len(g.shot.cue_t) > 3 else 0.0
    if sd > 0:
        pill(c, 540, 1330, "故事设定，不是现实结论", 36, PALEGOLD, INK, "sans", 26, clamp01(sd * 2), max(0.01, sd))
    st = g.pc(2, 0.0, 0.6, ease_back)
    if st > 0:
        with xf(c, 250, 640, rot=-5, sx=max(0.01, st)):
            crect(c, 0, 0, 440, 100, 24, PALERED, RED, 6, rough=False)
            text(c, "共同原因", 0, 16, 56, RED, "black", "c")


def _node(c, x, y, lab, fill, r=44, a=1.0):
    circ(c, x, y, r, fill, INK, 5, a=a, rough=False)
    text(c, lab, x, y + 14, 40, INK, "black", "c", a)


def s_types(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    # 三种可能：共同原因 / 反向作用 / 巧合
    cx = (190, 540, 890)
    titles = ("共同原因", "反向作用", "纯属巧合")
    for i in range(3):
        k = g.pc(1, 0.0 + 0.5 * i, 0.5, ease_back) if g.cue(1) > -0.5 else 0.0
        if i == 0:
            k = max(k, g.pc(0, 0.5, 0.5, ease_back))
        if k <= 0:
            continue
        with xf(c, cx[i], 820, sx=max(0.01, k)):
            card(c, 0, 0, 300, 470, CREAM, (-2, 1, 2)[i], 1.0, 1.0)
            card_end(c)
            text(c, titles[i], 0, -170, 42, INK, "black", "c")
            if i == 0:
                _node(c, 0, -80, "C", PALEGOLD)
                _node(c, -80, 80, "A", PALERED)
                _node(c, 80, 80, "B", PALEBLUE)
                arrow(c, (-20, -44), (-64, 40), INK, 6, 1.0, 18)
                arrow(c, (20, -44), (64, 40), INK, 6, 1.0, 18)
            elif i == 1:
                _node(c, -80, 20, "A", PALERED)
                _node(c, 80, 20, "B", PALEBLUE)
                arrow(c, (46, 20), (-46, 20), INK, 6, 1.0, 18)
                text(c, "B 推动 A", 0, 130, 34, GRAY, "sans", "c")
            else:
                _node(c, -80, 20, "A", PALERED)
                _node(c, 80, 20, "B", PALEBLUE)
                dline(c, (-36, 20), (36, 20), GRAY, 5, 1.0, (8, 8))
                text(c, "碰巧同步", 0, 130, 34, GRAY, "sans", "c")
    if g.cue(0) > 0.3:
        text(c, "A 与 B 一起变化", 540, 540, 46, RED, "black", "c", clamp01((g.cue(0) - 0.3) * 2), PAPER, 10)


def s_evidence(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    items = ["有没有对照？", "谁先谁后？", "有没有可能的机制？", "其他解释排除了吗？"]
    for i, lab in enumerate(items):
        cue_k = 0 if i < 3 else 1
        off = (0.1 + i * 0.7) if i < 3 else 0.2
        q = g.pc(cue_k, off, 0.5, ease_back)
        if q <= 0:
            continue
        y = 560 + i * 150
        with xf(c, 540, y, sx=max(0.01, q)):
            crect(c, 0, 0, 760, 112, 36, CREAM, INK, 5, rough=False)
            text(c, lab, -40, 16, 46, INK, "sans", "c")
            circ(c, -300, 0, 32, PALEBLUE, INK, 4, rough=False)
        check(c, 240, y + 2, 66, g.pc(cue_k, off + 0.4, 0.4), BLUE, 12) if False else None
        with xf(c, 540, y):
            check(c, -300, 2, 46, g.pc(cue_k, off + 0.35, 0.4), BLUE, 10)
    r = g.pc(2, 0.0, 0.6, ease_back)
    if r > 0:
        with xf(c, 540, 1230, sx=max(0.01, r)):
            crect(c, 0, 0, 900, 120, 50, PALEGOLD, INK, 5, rough=False)
            text(c, "只凭相关，下不了结论", -20, 16, 48, INK, "black", "c")
            magnifier(c, 390, -6, 28)


def s_background(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.35)
    # 三本书：统计推断 / 科学研究 / 因果推断
    names = ("统计推断", "研究方法", "因果推断")
    colors = (PALEBLUE, PALEGOLD, PALERED)
    for i in range(3):
        q = g.pc(0, 0.2 + 0.35 * i, 0.5, ease_back)
        if q <= 0:
            continue
        x = 250 + i * 290
        with xf(c, x, 880, sx=max(0.01, q)):
            rect(c, -90, -230, 180, 460, 12, colors[i], INK, 6, rough=False)
            rect(c, -90, -230, 30, 460, 8, INK, None, 0, rough=False)
            for j, ch in enumerate(names[i]):
                text(c, ch, 12, -130 + j * 72, 54, INK, "black", "c")
    r = g.pc(1, 0.0, 0.6, ease_back)
    if r > 0:
        pill(c, 540, 1230, "科学研究的基本功，不属于某一个人", 38, CREAM, INK, "sans", 28, clamp01(r * 2), max(0.01, r))


def s_reality(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    thermometer(c, 300, 520, 320, 0.75)
    q = g.pc(0, 0.2, 0.6, ease_back)
    if q > 0:
        text(c, "？", 300, 470, 110, RED, "black", "c", clamp01(q), PAPER, 14)
    magnifier(c, 560, 640, 70 * max(0.01, g.pc(0, 0.6, 0.6, ease_back)), 1.0, -10)
    # 证据资料堆
    for i in range(4):
        p = g.pc(2, 0.0 + i * 0.3, 0.5, ease_back)
        if p > 0:
            with xf(c, 760 + (i % 2) * 60, 900 - i * 20, rot=-6 + i * 4, sx=max(0.01, p)):
                card(c, 0, 0, 280, 190, CREAM, 0, 1.0, 1.0)
                for k in range(3):
                    rect(c, -100, -50 + k * 38, 200 - k * 40, 12, 6, LGRAY, None, 0, rough=False)
                card_end(c)
    if g.cue(2) > 0.4:
        pill(c, 540, 1230, "还要另外收集证据", 40, PALEGOLD, INK, "sans", 28, clamp01((g.cue(2) - 0.4) * 2), 1.0)
    if g.cue(1) > 0:
        r = g.pc(1, 0.0, 0.5, ease_back)
        with xf(c, 540, 1100, sx=max(0.01, r)):
            crect(c, 0, 0, 760, 90, 45, PALERED, RED, 5, rough=False)
            text(c, "同步变化 ≠ 都怪温度", 0, 15, 42, RED, "black", "c")


def s_ask(g):
    c, t = g.c, g.t
    glow(c, 540, 850, 560, GOLD, 0.3)
    person(c, LIN, 260, 1330, 0.95, face="think", t=t, look=(5, -4), armL=(105, 100), armR=(-20, -100),
           bob=math.sin(t * 2) * 3, tilt=4)
    # A、B 与神秘的第三件事
    a = g.pc(0, 0.2, 0.6, ease_back)
    if a > 0:
        with xf(c, 0, 0):
            _node(c, 620, 1000, "A", PALERED, 56, clamp01(a * 2))
            _node(c, 880, 1000, "B", PALEBLUE, 56, clamp01(a * 2))
            dline(c, (690, 1000), (810, 1000), INK, 6, a, (12, 9))
            text(c, "一起变化", 750, 1100, 34, GRAY, "sans", "c", clamp01(a * 2))
    b = g.pc(1, 0.3, 0.6, ease_back)
    if b > 0:
        circ(c, 750, 700, 70 * max(0.01, b), PALEGOLD, INK, 6, rough=False)
        text(c, "？", 750, 728, 90 * max(0.01, b), RED, "black", "c")
        arrow(c, (720, 764), (630, 944), RED, 7, 1.0, 22, g.pc(1, 0.8, 0.5))
        arrow(c, (780, 764), (870, 944), RED, 7, 1.0, 22, g.pc(1, 1.0, 0.5))
        pill(c, 750, 580, "第三件事", 36, PALERED, RED, "sans", 24, clamp01(b * 2), 1.0)


def s_end(g):
    c, t = g.c, g.t
    glow(c, 540, 820, 600, GOLD, 0.45)
    big_title(c, ["一起上涨，", "不一定是【谁带火了谁】"], 520, t, 100)
    q = g.p(0.8, 0.6, ease_back)
    cone(c, 260, 1120, 0.7 * max(0.01, q))
    ac_unit(c, 820, 1030, 0.8 * max(0.01, q), t * 0.8)
    thermometer(c, 540, 820, 220, 0.7 * q)


# ------------------------------------------------------------------ 组装

def build() -> Episode:
    shots = [
        Shot(["小镇冰淇淋店的老板，|发现了一件怪事：", "他家销量一涨，|隔壁空调店的订单也跟着涨。"], s_hook, tail=0.3,
             zoom=(1.0, 1.02)),
        Shot(["他半开玩笑：|看来是我的冰淇淋，带火了空调。", "当然，这是个虚构的教学故事。"], s_joke, tag="教学故事 · 虚构小镇"),
        Shot(["把两条曲线放在一起，|形状几乎一模一样。", "一起涨，就能说明|一个推动了另一个吗？", "先别急着下结论，|看看旁边。"], s_curves,
             tag="教学示意 · 非真实城市数据"),
        Shot(["镜头移到旁边：|温度计正在往上爬。", "天气变热，大家想吃冰淇淋，|也想买空调。",
              "在这个故事里，|温度是同时推动两者的共同原因。", "这个原因，是故事里设定好的。"], s_reveal, tag="教学设定 · 虚构小镇"),
        Shot(["只看共同变化，|不足以证明谁导致了谁。", "背后可能是共同原因，|也可能是反向作用，或者只是巧合。"], s_types,
             tag="本期概念"),
        Shot(["要说有因果，还得看对照、|先后顺序、可能的机制，", "再排除其他解释。", "相关不等于没有因果，|只是单凭相关，下不了结论。"],
             s_evidence),
        Shot(["这是统计推断和科学研究的基本功，", "不属于某一个人的“发现”。"], s_background, tag="方法背景"),
        Shot(["现实里，温度这个原因，|也不能凭猜测就定案。", "不是所有同步变化，|都能怪到温度头上。", "还要另外收集证据。"], s_reality),
        Shot(["下次看到两件事同时变化，", "先问一句：|有没有第三件事，同时推动了它们？"], s_ask),
        Shot(["一起上涨，不一定是谁带火了谁。"], s_end, tail=1.6),
    ]
    return Episode("08_相关不等于因果", shots).build()
