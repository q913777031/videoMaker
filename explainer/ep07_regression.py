"""第 07 期：均值回归（Regression to the Mean）。飞镖成绩为教学示意数据，并非真实比赛记录。"""

import math

import numpy as np
import skia

from .engine import (BLUE, CREAM, GOLD, GRAY, INK, KRAFT, LGRAY, PALEBLUE, PALEGOLD, PALERED, PAPER, RED, SKIN,
                     Episode, Shot, arrow, circ, clamp01, col, crect, dline, ease_back, ease_in, ease_io, ease_out,
                     glow, lerp, oval, partial_stroke, poly, prog, rect, shape, stroke, text, xf)
from .props import (COACH, GALTON, LIN, PLAYER, big_title, bubble, burst, card, card_end, check, cross, magnifier, motion_lines, person,
                    pill, sparkle, thought)

# 30 轮示意成绩（挑选过的教学数据）：最差的 3 轮之后变好，最好的 3 轮之后变差
SCORES = [76, 61, 56, 44, 67, 81, 70, 75, 79, 62, 94, 62, 73, 95, 69, 71, 65, 73, 51, 64, 85, 72, 68, 73, 74, 71,
          75, 55, 75, 64]
LOWS = (3, 18, 27)
HIGHS = (13, 10, 20)

_R = np.random.default_rng(1886)
PARENT = _R.standard_normal(70)
CHILD = 0.6 * PARENT + 0.8 * _R.standard_normal(70)
DARK_GREEN = "#4C7A5A"


# ------------------------------------------------------------------ 元件

def dartboard(c, cx, cy, r, a=1.0):
    circ(c, cx, cy, r + 14, "#5B4636", INK, 6, a=a, rough=False)
    rings = [(r, INK), (r * 0.9, CREAM), (r * 0.72, RED), (r * 0.58, CREAM), (r * 0.38, BLUE), (r * 0.22, CREAM),
             (r * 0.1, RED)]
    for rr, colr in rings:
        circ(c, cx, cy, rr, colr, INK, 3, a=a, rough=False)
    for i in range(12):
        ang = math.radians(i * 30)
        stroke(c, [(cx + math.cos(ang) * r * 0.1, cy + math.sin(ang) * r * 0.1),
                   (cx + math.cos(ang) * r * 0.9, cy + math.sin(ang) * r * 0.9)], INK, 2.5, a * 0.5)


def dart(c, x, y, ang=200.0, s=1.0):
    """飞镖，(x, y) 为镖尖，ang 为镖身相对镖尖的方向（度）。"""
    with xf(c, x, y, rot=ang, sx=s):
        stroke(c, [(0, 0), (86, 0)], INK, 9)
        stroke(c, [(0, 0), (86, 0)], "#C9D4DC", 5)
        poly(c, [(0, 0), (22, -7), (22, 7)], "#8C7F73", INK, 3, rough=False)
        poly(c, [(86, 0), (118, -22), (130, -22), (112, 0), (130, 22), (118, 22)], RED, INK, 3, rough=False)


def thumbs(c, x, y, s=1.0, color=GOLD):
    """表扬用的星章。"""
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = 34 if i % 2 == 0 else 15
        pts.append((x + s * r * math.cos(ang), y + s * r * math.sin(ang)))
    poly(c, pts, color, INK, 4, rough=False)


CH_X0, CH_DX = 92, 31


def cx_(i):
    return CH_X0 + i * CH_DX


def cy_(v, y0=1240, k=9.2):
    return y0 - (v - 40) * k


def chart_base(c, a=1.0, label=True):
    """成绩图：平常水平带 + 基线。"""
    y_hi, y_lo = cy_(79), cy_(61)
    rect(c, 60, y_hi, 960, y_lo - y_hi, 14, PALEBLUE, None, 0, a=0.55 * a, rough=False)
    dline(c, (60, cy_(70)), (1020, cy_(70)), BLUE, 4, a, (20, 12))
    stroke(c, [(60, cy_(40) + 20), (1020, cy_(40) + 20)], INK, 5, a)
    if label:
        text(c, "平常水平", 80, y_hi - 14, 32, BLUE, "sans", "l", a)


def chart_line(c, reveal, hi_lows=0.0, hi_highs=0.0, nexts=0.0, color=INK, dim=1.0):
    n = len(SCORES)
    show = reveal * (n - 1)
    pts = [(cx_(i), cy_(v)) for i, v in enumerate(SCORES)]
    k = int(show)
    seg = pts[:k + 1]
    if k < n - 1:
        f = show - k
        seg = seg + [(lerp(pts[k][0], pts[k + 1][0], f), lerp(pts[k][1], pts[k + 1][1], f))]
    if len(seg) > 1:
        stroke(c, seg, color, 4, 0.55 * dim)
    for i in range(min(n, k + 1)):
        circ(c, pts[i][0], pts[i][1], 8, "#8C7F73", INK, 3, a=dim, rough=False)
    return pts


# ------------------------------------------------------------------ 镜头

def s_hook(g):
    c, t = g.c, g.t
    glow(c, 540, 900, 560, GOLD, 0.35)
    big_title(c, ["挨了一顿骂，", "成绩就会提高？"], 330, t, 112)
    bx, by, br = 540, 735, 160
    rect(c, bx - 250, by - 215, 500, 430, 30, "#DCC9A4", INK, 6, rough=False)
    dartboard(c, bx, by, br)
    # 第一镖：脱靶；第二镖（下一轮）：靠近靶心
    p1 = prog(t, 0.35, 0.5)
    if p1 > 0:
        tx, ty = bx - 120, by + 140
        x = lerp(330, tx, ease_out(p1))
        y = lerp(1000, ty, ease_out(p1)) - math.sin(p1 * math.pi) * 90
        dart(c, x, y, 210 - 20 * p1, 0.9)
        if p1 >= 1:
            text(c, "脱靶！", 215, 690, 48, RED, "black", "c", clamp01((t - 0.85) * 4), PAPER, 10)
    p2 = prog(g.cue(1), 0.3, 0.5) if len(g.shot.cue_t) > 1 else 0.0
    if p2 > 0:
        tx, ty = bx + 18, by + 10
        x = lerp(330, tx, ease_out(p2))
        y = lerp(1000, ty, ease_out(p2)) - math.sin(p2 * math.pi) * 90
        dart(c, x, y, 210 - 20 * p2, 0.9)
    yelling = 1.0 < t < g.cue(1) + t - 0.0 if False else (t > 1.0 and g.cue(1) < 0.2)
    ps_face = "sad" if (t > 0.95 and g.cue(1) < 0.8) else ("cheer" if g.cue(1) >= 0.8 else "smile")
    person(c, PLAYER, 250, 1310, 0.95, face=ps_face, t=t, look=(5, -5),
           armL=(105, 100), armR=(-40, -60) if t < 0.9 else (70, 75),
           tilt=-5 if ps_face == "sad" else 0, bob=math.sin(t * 2) * 3)
    person(c, COACH, 840, 1310, 0.95, face="angry" if yelling else "smile", t=t, flip=True,
           talk=0.5 + 0.5 * math.sin(t * 14) if yelling else 0.0, armL=(110, 100), armR=(-20, -50) if yelling else (80, 84),
           tilt=3 * math.sin(t * 10) if yelling else 0.0, bob=math.sin(t * 2) * 3)
    if yelling:
        for i in range(5):
            a = math.radians(160 + i * 10)
            r0 = 110 + 12 * math.sin(t * 16 + i)
            stroke(c, [(740 + math.cos(a) * r0, 1060 + math.sin(a) * r0),
                       (740 + math.cos(a) * (r0 + 56), 1060 + math.sin(a) * (r0 + 56))], RED, 8)
        text(c, "！！！", 560, 1080, 86, RED, "black", "c", 1.0, PAPER, 14)


def _equation(c, y, p):
    items = [("稳定水平", PALEBLUE, BLUE, 130), ("＋", None, GRAY, 40), ("本轮运气", PALEGOLD, "#B9741A", 130),
             ("＝", None, GRAY, 40), ("本轮成绩", CREAM, INK, 130)]
    total = sum(w for *_, w in items) + 4 * 60
    x = 540 - total / 2
    for i, (lab, fill, colr, w) in enumerate(items):
        q = clamp01(p * 5 - i)
        cxx = x + (w + 60) / 2 * (1 if fill else 0.55) if False else x + w / 2
        if fill:
            with xf(c, cxx + 0, y, sx=max(0.01, ease_back(q))):
                crect(c, 0, 0, w * 1.55, 100, 28, fill, INK, 5, rough=False)
                text(c, lab, 0, 14, 38, colr, "black", "c")
        else:
            text(c, lab, cxx, y + 22, 64, colr, "black", "c", q)
        x += w + 60 if fill else w + 10


def s_model(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    p = g.pc(0, 0.2, 1.4, ease_out)
    # 三个块的公式
    for i, (lab, fill, colr) in enumerate((("稳定水平", PALEBLUE, BLUE), ("本轮运气", PALEGOLD, "#B9741A"),
                                           ("本轮成绩", CREAM, INK))):
        q = clamp01(g.cue(0) * 1.2 - i * 0.7)
        if i == 2:
            q = clamp01(g.cue(1) * 1.2)
        x = (200, 540, 880)[i]
        with xf(c, x, 600, sx=max(0.01, ease_back(q))):
            crect(c, 0, 0, 270, 110, 30, fill, INK, 5, rough=False)
            text(c, lab, 0, 16, 42, colr, "black", "c")
    text(c, "＋", 370, 622, 70, GRAY, "black", "c", clamp01(g.cue(0) * 1.2 - 0.3))
    text(c, "＝", 710, 622, 70, GRAY, "black", "c", clamp01(g.cue(1) * 1.2))
    # 下方：同一水平，成绩被运气推着上下摆
    chart_base(c, clamp01(g.cue(0) * 1.5), label=False)
    if g.cue(1) > 0.3:
        reveal = g.pc(1, 0.3, 3.0, ease_out)
        chart_line(c, reveal, dim=1.0)
    q = g.pc(0, 0.6, 0.6)
    text(c, "水平不变", 540, 790, 42, BLUE, "sans", "c", clamp01(q * 2))


def s_rule(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    chart_base(c, 1.0)
    reveal = g.pc(0, 0.0, 2.4, ease_io)
    pts = chart_line(c, reveal)
    # 特别差：批评
    for i in LOWS:
        q = clamp01((reveal * 29 - i) * 1.0) * g.pc(0, 1.6 + 0.35 * LOWS.index(i), 0.4, ease_back)
        if q > 0.01:
            circ(c, pts[i][0], pts[i][1], 16 * q, None, RED, 6, rough=False)
            with xf(c, pts[i][0], pts[i][1] + 62, sx=q):
                pill(c, 0, 0, "批评", 28, PALERED, RED, "sans", 12)
    # 特别好：表扬
    for k, i in enumerate(HIGHS):
        q = g.pc(1, 0.2 + 0.35 * k, 0.4, ease_back)
        if q > 0.01:
            circ(c, pts[i][0], pts[i][1], 16 * q, None, GOLD, 6, rough=False)
            with xf(c, pts[i][0], pts[i][1] - 56, sx=q):
                pill(c, 0, 0, "表扬", 28, PALEGOLD, "#B9741A", "sans", 12)
    person(c, COACH, 190, 1500, 0.0, face="smile")


def s_belief(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    chart_base(c, 1.0)
    pts = chart_line(c, 1.0, dim=0.9)
    # 批评后变好、表扬后变差
    for k, i in enumerate(LOWS):
        q = g.pc(0, 0.2 + 0.4 * k, 0.5)
        circ(c, pts[i][0], pts[i][1], 17, None, RED, 6, rough=False)
        if q > 0:
            arrow(c, (pts[i][0] + 6, pts[i][1] - 14), (pts[i + 1][0], pts[i + 1][1] + 6), RED, 6, 1.0, 20, q)
    for k, i in enumerate(HIGHS):
        q = g.pc(0, 1.2 + 0.4 * k, 0.5)
        circ(c, pts[i][0], pts[i][1], 17, None, GOLD, 6, rough=False)
        if q > 0:
            arrow(c, (pts[i][0] + 6, pts[i][1] + 14), (pts[i + 1][0], pts[i + 1][1] - 6), "#B9741A", 6, 1.0, 20, q)
    if g.cue(0) > 0.5:
        text(c, "批评后 ↑ 变好", 280, 640, 40, RED, "black", "c", clamp01((g.cue(0) - 0.5) * 2), PAPER, 10)
    if g.cue(0) > 1.5:
        text(c, "表扬后 ↓ 变差", 780, 640, 40, "#B9741A", "black", "c", clamp01((g.cue(0) - 1.5) * 2), PAPER, 10)
    b = g.pc(1, 0.0, 0.5, ease_back)
    person(c, COACH, 230, 1500, 0.0, face="smile")
    if b > 0:
        bubble(c, 540, 500, 560, 112, "骂人才有用！", 54, "", CREAM, RED, "black", clamp01(b * 2), max(0.01, b))


def s_twist(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    chart_base(c, 1.0)
    pts = chart_line(c, 1.0, dim=0.85)
    # 没有教练：划掉
    q0 = g.pc(0, 0.0, 0.5, ease_back)
    if q0 > 0:
        with xf(c, 540, 540, sx=max(0.01, q0)):
            crect(c, 0, 0, 560, 100, 50, CREAM, INK, 5, rough=False)
            text(c, "没有批评，也没有表扬", 0, 15, 40, INK, "sans", "c")
    # 最差的轮 → 下一轮
    q1 = g.pc(1, 0.0, 1.2)
    for k, i in enumerate(LOWS):
        circ(c, pts[i][0], pts[i][1], 17, None, RED, 6, rough=False, a=clamp01(q1 * 2))
        qq = clamp01(q1 * 3 - k)
        if qq > 0:
            circ(c, pts[i + 1][0], pts[i + 1][1], 14, BLUE, INK, 4, a=1.0, rough=False)
            arrow(c, (pts[i][0] + 8, pts[i][1] - 12), (pts[i + 1][0] - 2, pts[i + 1][1] + 12), BLUE, 6, 1.0, 18, qq)
    q2 = g.pc(2, 0.0, 0.6, ease_back)
    if q2 > 0:
        with xf(c, 540, 1360, sx=max(0.01, q2)):
            crect(c, 0, 0, 800, 100, 50, PALEBLUE, INK, 5, rough=False)
            text(c, "下一轮：平均更靠近平常水平", 0, 15, 42, INK, "sans", "c")


def s_galton(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.35)
    a = g.pc(0, 0.0, 0.6, ease_back)
    if a > 0:
        person(c, GALTON, 190, 790, 0.62 * max(0.01, a), face="open", t=t, talk=0.4 + 0.4 * math.sin(t * 8),
               armL=(110, 100), armR=(40, 20))
    pill(c, 700, 520, "高尔顿 · 1886", 40, PALEGOLD, INK, "sans", 28, clamp01(a * 2), max(0.01, a))
    # 散点图
    x0, x1, y0, y1 = 360, 980, 1250, 620
    sx = lambda v: lerp(x0, x1, (v + 2.6) / 5.2)
    sy = lambda v: lerp(y0, y1, (v + 2.6) / 5.2)
    pa = g.pc(0, 0.4, 0.5)
    stroke(c, [(x0, y0), (x1, y0)], INK, 5, pa)
    stroke(c, [(x0, y0), (x0, y1)], INK, 5, pa)
    text(c, "父母身高 →", (x0 + x1) / 2, y0 + 56, 32, GRAY, "sans", "c", pa)
    text(c, "子女", x0 - 8, y1 - 22, 32, GRAY, "sans", "c", pa)
    show = int(70 * g.pc(0, 0.6, 1.8, ease_out))
    for i in range(show):
        tall = PARENT[i] > 1.1
        circ(c, sx(PARENT[i]), sy(CHILD[i]), 8, RED if tall else "#B9AE9C", INK, 2.5, rough=False)
    if g.cue(1) > 0:
        # 父母极高的一组：子女平均线
        mp = float(np.mean(PARENT[PARENT > 1.1]))
        mc = float(np.mean(CHILD[PARENT > 1.1]))
        q = g.pc(1, 0.0, 0.8, ease_out)
        dline(c, (sx(mp), y0), (sx(mp), sy(mp)), GRAY, 4, q, (10, 8))
        circ(c, sx(mp), sy(mp), 11 * q, None, GRAY, 5, rough=False)
        stroke(c, [(x0, sy(mc)), (x0 + (x1 - x0) * q, sy(mc))], RED, 6, q)
        text(c, "子女平均", x1 - 100, sy(mc) + 42, 32, RED, "sans", "c", q)
        text(c, "与父母一样高", sx(mp) - 30, sy(mp) - 24, 30, GRAY, "sans", "c", q)
    if g.cue(2) > 0:
        r = g.pc(2, 0.0, 0.6, ease_back)
        with xf(c, 540, 1380, sx=max(0.01, r)):
            text(c, "均值回归", 0, 0, 100, RED, "black", "c", 1.0, PAPER, 16)


def s_notfate(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    a = g.pc(0, 0.0, 0.6, ease_back)
    if a > 0:
        card(c, 290, 760, 440, 480, CREAM, -2, max(0.01, a), 1.0)
        text(c, "命运补偿", 0, -170, 50, INK, "black", "c")
        stroke(c, [(-100, -40), (100, 60)], GRAY, 6)
        circ(c, 0, 10, 50, "#EEE", INK, 4, rough=False)
        card_end(c)
        cross(c, 290, 760, 190, g.pc(0, 0.8, 0.5))
    b = g.pc(0, 0.5, 0.6, ease_back)
    if b > 0:
        card(c, 790, 760, 440, 480, CREAM, 2, max(0.01, b), 1.0)
        text(c, "必然反转", 0, -170, 50, INK, "black", "c")
        stroke(c, [(-110, 40), (-40, -60), (30, 40), (110, -60)], GRAY, 6)
        card_end(c)
        cross(c, 790, 760, 190, g.pc(0, 1.3, 0.5))
    c2 = g.pc(1, 0.0, 0.6, ease_back)
    if c2 > 0:
        with xf(c, 540, 1170, sx=max(0.01, c2)):
            coin_x = -300
            circ(c, coin_x, 0, 52, "#EFC25A", INK, 5, rough=False)
            text(c, "正", coin_x, 18, 52, INK, "black", "c")
            text(c, "→", -190, 16, 60, GRAY, "black", "c")
            circ(c, -80, 0, 52, "#EFC25A", INK, 5, rough=False)
            text(c, "？", -80, 18, 52, INK, "black", "c")
            text(c, "下一次照旧", 150, 14, 46, INK, "sans", "c")
    d = g.pc(2, 0.0, 0.6, ease_back)
    if d > 0:
        pill(c, 540, 1290, "先挑出极端的一轮，再看下一轮", 38, PALEGOLD, INK, "sans", 28, clamp01(d * 2), max(0.01, d))


def s_control(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    p = g.pc(0, 0.0, 0.6, ease_back)
    if p > 0:
        with xf(c, 270, 760, sx=max(0.01, p)):
            card(c, 0, 0, 390, 460, CREAM, -2, 1.0, 1.0)
            card_end(c)
            text(c, "批评组", 0, -150, 50, RED, "black", "c")
            for i in range(3):
                circ(c, -100 + i * 100, -30, 30, SKIN, INK, 4, rough=False)
                oval(c, -100 + i * 100, 50, 36, 40, PALERED, INK, 4, rough=False)
    q = g.pc(0, 0.6, 0.6, ease_back)
    if q > 0:
        with xf(c, 810, 760, sx=max(0.01, q)):
            card(c, 0, 0, 390, 460, CREAM, 2, 1.0, 1.0)
            card_end(c)
            text(c, "对照组", 0, -150, 50, BLUE, "black", "c")
            for i in range(3):
                circ(c, -100 + i * 100, -30, 30, SKIN, INK, 4, rough=False)
                oval(c, -100 + i * 100, 50, 36, 40, PALEBLUE, INK, 4, rough=False)
            text(c, "什么都不做", 0, 150, 38, GRAY, "sans", "c")
    if g.cue(0) > 1.2:
        text(c, "VS", 540, 775, 44, GRAY, "black", "c", clamp01((g.cue(0) - 1.2) * 2))
    r = g.pc(1, 0.0, 0.6, ease_back)
    if r > 0:
        with xf(c, 540, 1150, sx=max(0.01, r)):
            crect(c, 0, 0, 860, 170, 40, CREAM, INK, 5, rough=False)
            text(c, "批评有没有用？", -170, -8, 44, INK, "sans", "c")
            text(c, "靠对照来回答", 190, -8, 44, RED, "black", "c")
            text(c, "单靠这个故事，不能证明批评无效，也不能证明表扬有效", 0, 54, 28, GRAY, "sans", "c")


def s_close(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    person(c, LIN, 200, 1330, 0.9, face="think", t=t, look=(5, -4), armL=(105, 100), armR=(-20, -100),
           bob=math.sin(t * 2) * 3, tilt=4)
    # 一次干预后变好：虚线 = 不干预也会回落
    q = g.pc(0, 0.0, 1.2, ease_out)
    pts = [(520, 760), (620, 880), (720, 640), (820, 720), (920, 700)]
    stroke(c, pts[:2], INK, 5, 0.9 * q)
    circ(c, 520, 760, 12, "#8C7F73", INK, 3, a=q, rough=False)
    circ(c, 620, 880, 15, None, RED, 6, a=q, rough=False)
    dline(c, (480, 720), (1000, 720), BLUE, 4, q, (18, 12))
    text(c, "平常水平", 900, 690, 30, BLUE, "sans", "c", q)
    p2 = g.pc(0, 1.0, 0.6)
    if p2 > 0:
        arrow(c, (640, 868), (730, 735), RED, 7, 1.0, 22, p2)
        circ(c, 735, 730, 13, BLUE, INK, 3, a=clamp01(p2 * 2), rough=False)
        pill(c, 800, 960, "做了一次干预", 34, PALERED, RED, "sans", 22, clamp01(p2 * 2), 1.0)
    r = g.pc(1, 0.2, 0.6, ease_back)
    if r > 0:
        thought(c, 730, 1175, 600, 170, "", 40, CREAM, clamp01(r * 2), max(0.01, r), dots_to=(430, 1260))
        text(c, "什么都不做，", 730, 1160, 44, INK, "sans", "c", clamp01(r * 2))
        text(c, "也会向平常水平回落吗？", 730, 1215, 40, RED, "black", "c", clamp01(r * 2))


def s_end(g):
    c, t = g.c, g.t
    glow(c, 540, 820, 600, GOLD, 0.45)
    big_title(c, ["骂完就变好，", "不一定是【骂的功劳】"], 520, t, 100)
    q = g.p(0.8, 0.8, ease_out)
    chart_base(c, q, False)
    pts = [(120 + i * 74, [1040, 1130, 1010, 1060, 1000, 1070, 1030, 1050, 1020, 1040, 1035, 1045, 1040][i % 13]) for i in range(13)]
    stroke(c, pts[:int(2 + 11 * q)], INK, 5, 0.6 * q, smooth=True)


# ------------------------------------------------------------------ 组装

def build() -> Episode:
    shots = [
        Shot(["飞镖选手这一轮脱了靶，|教练大吼了一顿。", "下一轮，他的成绩居然好了！"], s_hook, tail=0.3, zoom=(1.0, 1.02)),
        Shot(["这是个教学故事。选手的水平相对稳定，", "但每一轮的成绩，|还会被运气上下推一把。"], s_model,
             tag="教学故事 · 飞镖选手"),
        Shot(["教练的习惯是：|特别差的一轮后批评，", "特别好的一轮后表扬。"], s_rule, tag="教学示意 · 非真实比赛数据"),
        Shot(["几周后他发现：|批评完常常变好，表扬完常常变差。", "于是他得出结论：骂人才有用。"], s_belief,
             tag="教学示意 · 非真实比赛数据"),
        Shot(["但如果没有任何奖惩呢？", "把稳定选手最差的几轮挑出来，|再看它们的下一轮——",
              "平均来说，会更靠近他平常的水平。"], s_twist, tag="原理示意 · 非真实比赛数据"),
        Shot(["一八八六年，高尔顿研究亲子身高，|也发现了类似现象：", "极端高个子的父母，|子女平均身高往往没那么极端。",
              "后来，这被称为【均值回归】。"], s_galton, tag="历史案例 · 1886"),
        Shot(["它不是命运在补偿，|下一次也不一定反转。", "公平硬币的下一次，|不会补偿上一次。", "这里讲的是：先挑出极端，再看下一次。"],
             s_notfate, tag="本期概念"),
        Shot(["批评到底有没有用，|要靠合适的对照才知道。", "这个故事，不能证明批评无效，|也不能证明表扬有效。"], s_control),
        Shot(["下次看到一次干预之后变好了，", "先问一句：如果什么都没做，|它会不会也向平常水平回落？"], s_close),
        Shot(["骂完变好，不一定是骂的功劳。"], s_end, tail=1.6),
    ]
    return Episode("07_均值回归", shots).build()
