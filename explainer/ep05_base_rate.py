"""第 05 期：基率忽视（Base-Rate Neglect）。全部工厂数字均为教学设定。"""

import math

from .engine import (BLUE, CREAM, GOLD, GRAY, INK, KRAFT, LGRAY, PALEBLUE, PALEGOLD, PALERED, PAPER, RED, SKIN,
                     Episode, Shot, arrow, circ, clamp01, crect, ease_back, ease_in, ease_io, ease_out, glow, lerp,
                     oval, poly, prog, rect, shape, stroke, text, xf)
from .factory import (DEFECT_IDX, basket, belt, crate, detector, dot_grid, lamp, pie, scale)
from .props import (LIN, big_title, bubble, burst, bulb, card, card_end, check, cross, doodle, magnifier, person, pill,
                    sparkle, thought)


def s_hook(g):
    c, t = g.c, g.t
    glow(c, 640, 900, 520, GOLD, 0.35)
    big_title(c, ["识别这么准，", "报警却大多错了？"], 330, t, 108)
    belt_y = 1150
    lin_face = "worry" if t > 1.0 else "smile"
    person(c, LIN, 215, belt_y + 20, 1.12, face=lin_face, t=t, look=(5, 2), armL=(110, 100), armR=(60, 50),
           bob=math.sin(t * 2) * 3)
    # 检测门与传送带
    flagged = (346 + 420 * t) % 1520 - 150
    near = abs(flagged - 700) < 120 and t < 3.0
    on = (1.0 if int(t * 8) % 2 == 0 else 0.6) if near else 0.0
    detector(c, 700, belt_y, 1.25, on, t, label=False)
    belt(c, -30, 1110, belt_y, t, 420)
    for k in range(4):
        x = (346 + 420 * t + 380 * k) % 1520 - 150
        fl = 1.0 if (k == 0 and x > 700 and t < 4.0) else 0.0
        crate(c, x, belt_y + 2, 1.25, False, fl)
    if on > 0:
        for i in range(3):
            stroke(c, [(880 + i * 24, 690 - i * 14), (940 + i * 24, 655 - i * 14)], RED, 7, 0.7 * on)
    b = g.pc(1, 0.2, 0.5, ease_back)
    if b > 0:
        bubble(c, 380, 700, 500, 124, "九成是坏的！", 56, "", CREAM, RED, "black", clamp01(b * 2), max(0.01, b),
               tail_to=(240, 820))


def s_setup(g):
    c, t = g.c, g.t
    glow(c, 540, 850, 560, GOLD, 0.3)
    reveal = g.pc(0, 0.3, 2.2, ease_io)
    p = g.pc(0, 0.0, 0.5, ease_back)
    pill(c, 540, 470, "每天检查 10000 件产品", 42, CREAM, INK, "sans", 30, clamp01(p * 2), max(0.01, p))
    dot_grid(c, 540, 850, 660, reveal if g.cue(1) < 0 else 1.0, mark_defect=g.pc(1, 0.2, 0.6, ease_out))
    # 外框
    rect(c, 540 - 346, 850 - 346, 692, 692, 14, None, INK, 5, rough=False, a=clamp01(reveal * 3))
    b1 = g.pc(1, 0.1, 0.5, ease_back)
    if b1 > 0:
        pill(c, 300, 1250, "有缺陷 100件", 40, PALERED, RED, "sans", 28, clamp01(b1 * 2), max(0.01, b1))
    b2 = g.pc(1, 1.2, 0.5, ease_back)
    if b2 > 0:
        pill(c, 780, 1250, "合格 9900件", 40, "#E2D9C6", INK, "sans", 28, clamp01(b2 * 2), max(0.01, b2))
    if b1 > 0:
        pulse = 0.5 + 0.5 * math.sin(t * 6)
        circ(c, 540 + 330, 850 - 330, 0, None)  # 占位避免空分支


def _crate_row(c, x0, y, n, step, flagged, bad, s, p, flag_p):
    for i in range(n):
        q = clamp01((p * n - i) / 1.0)
        if q <= 0:
            continue
        crate(c, x0 + i * step, y - (1 - q) * 40, s, bad, flag_p if i in flagged else 0.0, clamp01(q * 2))


def s_stats(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    # 检出率：10 个缺陷箱，9 个报警
    pa = g.pc(0, 0.0, 0.5, ease_out)
    pill(c, 330, 520, "检出率 90%", 44, PALERED, RED, "sans", 30, clamp01(pa * 2), 1.0)
    _crate_row(c, 140, 700, 10, 88, set(range(9)), True, 0.95, g.pc(0, 0.4, 1.4), g.pc(0, 1.8, 0.6))
    # 误报率：20 个合格箱，1 个误报
    pb = g.pc(0, 2.4, 0.5, ease_out)
    pill(c, 330, 820, "误报率 5%", 44, "#E2D9C6", INK, "sans", 30, clamp01(pb * 2), 1.0)
    _crate_row(c, 140, 970, 10, 88, set(), False, 0.95, g.pc(0, 2.7, 1.0), 0.0)
    _crate_row(c, 140, 1080, 10, 88, {4}, False, 0.95, g.pc(0, 3.2, 1.0), g.pc(0, 4.4, 0.6))
    if g.cue(0) > 4.2:
        text(c, "20 个里有 1 个", 760, 825, 36, GRAY, "sans", "c", clamp01((g.cue(0) - 4.2) * 2))
    if g.cue(0) > 1.0:
        text(c, "10 个里有 9 个", 760, 525, 36, GRAY, "sans", "c", clamp01((g.cue(0) - 1.0) * 2))
    # 名称辨析
    q = g.pc(1, 0.2, 0.5, ease_back)
    if q > 0:
        with xf(c, 540, 1250, sx=max(0.01, q)):
            crect(c, 0, 0, 800, 110, 55, CREAM, INK, 5, rough=False)
            text(c, "检出率 ≠ 误报率 ≠ “准确率”", 0, 16, 42, INK, "sans", "c")
        cross(c, 880, 1250, 56, g.pc(1, 0.9, 0.5))


def _lane(c, y, t, flow, p_flag, bad):
    belt(c, 40, 600, y, t, 160, 30)
    for k in range(4):
        x = (t * 160 + 160 * k) % 640 + 10
        if flow > 0:
            crate(c, x, y + 2, 0.7, bad, 0.0, clamp01(flow))
    detector(c, 620, y, 0.72, p_flag, t, label=False)


def s_split(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.25)
    blink = 1.0 if int(t * 5) % 2 == 0 else 0.5
    # 上路：缺陷 100 → 检出 90
    pill(c, 210, 470, "有缺陷 100件", 36, PALERED, RED, "sans", 24, clamp01(g.p(0.1, 0.4)), 1.0)
    _lane(c, 760, t, g.p(0.2, 0.4), blink * clamp01(g.cue(0) / 0.8), True)
    basket(c, 880, 770, 220, 170)
    n1 = int(90 * g.pc(0, 0.6, 1.6, ease_out))
    for i in range(min(n1, 90)):
        circ(c, 880 - 95 + (i % 15) * 13.5, 770 - 16 - (i // 15) * 15, 5.6, RED, None, 0, rough=False)
    pop1 = g.pc(0, 0.4, 0.5, ease_back)
    if pop1 > 0:
        text(c, f"检出 {n1} 件", 880, 545, 46, RED, "black", "c", clamp01(pop1 * 2), PAPER, 10)
    if g.cue(0) > 0.3:
        text(c, "检出率 90%", 620, 835, 34, GRAY, "sans", "c", clamp01(g.cue(0) * 2))
    if g.cue(0) > 1.5:
        text(c, "100 × 90% = 90", 300, 835, 40, INK, "sans", "c", clamp01((g.cue(0) - 1.5) * 2))
    # 下路：合格 9900 → 误报 495
    p2 = g.pc(1, -0.2, 0.5, ease_out)
    pill(c, 235, 960, "合格 9900件", 36, "#E2D9C6", INK, "sans", 24, clamp01(p2), 1.0)
    on2 = blink * clamp01(g.cue(1) / 0.8) if g.cue(1) > 0 else 0.0
    _lane(c, 1210, t, clamp01(p2), on2, False)
    basket(c, 880, 1225, 260, 210)
    n2 = int(495 * g.pc(1, 0.6, 1.8, ease_out))
    for i in range(min(n2, 495)):
        circ(c, 880 - 112 + (i % 25) * 9.0, 1225 - 14 - (i // 25) * 9.4, 3.8, GOLD, None, 0, rough=False)
    pop2 = g.pc(1, 0.4, 0.5, ease_back)
    if pop2 > 0:
        text(c, f"误报 {n2} 件", 880, 985, 46, "#B9741A", "black", "c", clamp01(pop2 * 2), PAPER, 10)
    if g.cue(1) > 0.3:
        text(c, "误报率 5%", 620, 1285, 34, GRAY, "sans", "c", clamp01(g.cue(1) * 2))
    if g.cue(1) > 1.4:
        text(c, "9900 × 5% = 495", 300, 1285, 40, INK, "sans", "c", clamp01((g.cue(1) - 1.4) * 2))


def s_merge(g):
    c, t = g.c, g.t
    glow(c, 540, 820, 560, GOLD, 0.35)
    # 585 个报警点：45 列 × 13 行，前 90 个是真缺陷
    p0 = g.pc(0, 0.0, 1.4, ease_out)
    n = int(585 * p0)
    for i in range(n):
        x = 540 - 22 * 20 + (i % 45) * 20
        y = 560 + (i // 45) * 24
        circ(c, x, y, 7.5, RED if i < 90 else GOLD, None, 0, rough=False)
    pill(c, 540, 460, "红灯共 585 次", 46, CREAM, INK, "sans", 32, clamp01(g.pc(0, 0.0, 0.4) * 2), 1.0)
    if g.cue(1) > 0:
        # 公式：585 = 90 + 495
        q = g.pc(1, 0.0, 0.5, ease_back)
        with xf(c, 540, 960, sx=max(0.01, q)):
            text(c, "585", -320, 0, 84, INK, "black", "c")
            text(c, "=", -200, 0, 84, GRAY, "black", "c")
            text(c, "90", -70, 0, 84, RED, "black", "c")
            text(c, "+", 40, 0, 84, GRAY, "black", "c")
            text(c, "495", 190, 0, 84, "#B9741A", "black", "c")
            text(c, "真缺陷", -70, 56, 32, RED, "sans", "c")
            text(c, "误报", 190, 56, 32, "#B9741A", "sans", "c")
    if g.cue(2) > 0:
        r = g.pc(2, 0.0, 0.5, ease_back)
        with xf(c, 540, 1150, sx=max(0.01, r)):
            text(c, "90 ÷ 585 ≈", -150, 0, 62, INK, "black", "c")
            text(c, "15.4%", 230, 6, 100, RED, "black", "c", 1.0, PAPER, 14)
        bw = 760
        rect(c, 540 - bw / 2, 1230, bw, 46, 12, GOLD, INK, 5, rough=False, a=clamp01(r * 2))
        rect(c, 540 - bw / 2, 1230, bw * 90 / 585 * g.pc(2, 0.3, 0.8), 46, 12, RED, INK, 5, rough=False,
             a=clamp01(r * 2))


def s_contrast(g):
    c, t = g.c, g.t
    glow(c, 540, 840, 560, GOLD, 0.3)
    person(c, LIN, 250, 1290, 1.0, face="surprise" if g.cue(0) > 0.5 else "worry", t=t, look=(4, -4),
           armL=(110, 100), armR=(-70, -110), bob=math.sin(t * 2) * 3)
    q = g.pc(0, 0.0, 0.5, ease_back)
    bubble(c, 330, 640, 460, 118, "我以为：九成", 50, "", CREAM, INK, "black", clamp01(q * 2), max(0.01, q),
           tail_to=(260, 880))
    cross(c, 590, 640, 76, g.pc(0, 1.2, 0.5))
    # 饼图
    p = g.pc(0, 0.8, 1.2, ease_io)
    with xf(c, 700, 960):
        pie(c, 0, 0, 200, 90 / 585, p)
    if p > 0.95:
        text(c, "真缺陷 90件 ≈15.4%", 700, 1250, 38, RED, "sans", "c", clamp01((g.cue(0) - 2.0) * 2))
    if g.cue(1) > 0:
        r = g.pc(1, 0.0, 0.5, ease_back)
        text(c, "误报 495件 ≈84.6%", 700, 1300, 38, "#B9741A", "sans", "c", clamp01(r * 2))
        with xf(c, 800, 725, sx=max(0.01, r)):
            text(c, "15.4%", 0, 0, 92, RED, "black", "c", 1.0, PAPER, 14)


def s_why(g):
    c, t = g.c, g.t
    glow(c, 540, 840, 560, GOLD, 0.3)
    p = g.pc(1, 0.0, 1.0, ease_back)
    tilt = lerp(0, 8, p)
    lp, rp = scale(c, 540, 720, tilt, 0.95)
    for i in range(90):
        circ(c, lp[0] - 84 + (i % 15) * 12, lp[1] - 10 - (i // 15) * 12, 5.2, RED, None, 0, rough=False)
    for i in range(495):
        circ(c, rp[0] - 112 + (i % 33) * 6.9, rp[1] - 10 - (i // 33) * 7.2, 3.1, GOLD, None, 0, rough=False)
    a = g.pc(0, 0.0, 0.5, ease_back)
    text(c, "100 × 90% = 90", lp[0], lp[1] + 120, 36, RED, "sans", "c", clamp01(a * 2))
    b = g.pc(1, 0.4, 0.5)
    text(c, "9900 × 5% = 495", rp[0], rp[1] + 120, 36, "#B9741A", "sans", "c", clamp01(b * 2))
    pill(c, 220, 470, "缺陷品少", 40, PALERED, RED, "sans", 26, clamp01(a * 2), 1.0)
    pill(c, 860, 470, "合格品多", 40, "#E2D9C6", INK, "sans", 26, clamp01(b * 2), 1.0)


def s_term(g):
    c, t = g.c, g.t
    glow(c, 540, 850, 560, GOLD, 0.4)
    # 左：测得有多准（灯） 右：原本有多常见（点阵）
    a = g.pc(0, 0.0, 0.5, ease_back)
    if a > 0:
        with xf(c, 290, 760, sx=max(0.01, a)):
            card(c, 0, 0, 400, 360, CREAM, -2, 1.0, 1.0)
            card_end(c)
            lamp(c, 0, -30, 1.0, 50, t)
            text(c, "测得有多准", 0, 130, 44, INK, "black", "c")
    b = g.pc(1, 0.0, 0.5, ease_back)
    if b > 0:
        with xf(c, 790, 760, sx=max(0.01, b)):
            card(c, 0, 0, 400, 360, CREAM, 2, 1.0, 1.0)
            card_end(c)
            for r in range(8):
                for q in range(12):
                    circ(c, -110 + q * 20, -110 + r * 20, 6, RED if (r, q) == (2, 7) else "#B9AE9C", None, 0, rough=False)
            text(c, "原本有多常见", 0, 150, 44, INK, "black", "c")
    m = g.pc(1, 0.8, 0.6, ease_back)
    if m > 0:
        with xf(c, 540, 1120, sx=max(0.01, m)):
            text(c, "基率忽视", 0, 40, 124, RED, "black", "c", 1.0, PAPER, 20)
        for i in range(4):
            a2 = (t * 1.3 + i * 0.4) % 1.0
            sparkle(c, 130 + i * 270, 1000 + 20 * math.sin(i * 2), 16 + 10 * math.sin(a2 * 6.28), GOLD, clamp01(m))
    s = g.pc(2, 0.0, 0.5, ease_back)
    if s > 0:
        pill(c, 540, 1260, "20世纪70年代 · 判断与决策研究", 34, PALEGOLD, INK, "sans", 26, clamp01(s * 2), max(0.01, s))


def s_recheck(g):
    c, t = g.c, g.t
    glow(c, 540, 840, 560, GOLD, 0.3)
    # 红灯 → 复检 → 结果
    a = g.pc(1, 0.0, 0.5, ease_back)
    lamp(c, 190, 610, 1.0 if int(t * 4) % 2 == 0 else 0.6, 44, t)
    arrow(c, (270, 610), (420, 610), INK, 9, 1.0, 26, g.pc(1, 0.0, 0.5))
    if a > 0:
        with xf(c, 540, 610, sx=max(0.01, a)):
            magnifier(c, 0, -20, 56)
        text(c, "复检", 540, 730, 40, INK, "black", "c", clamp01(a * 2))
    arrow(c, (660, 610), (810, 610), INK, 9, 1.0, 26, g.pc(1, 0.6, 0.5))
    r = g.pc(1, 1.0, 0.5, ease_back)
    if r > 0:
        crate(c, 880, 650, 1.1 * max(0.01, r), False)
        check(c, 880, 560, 70 * max(0.01, r), g.pc(1, 1.4, 0.4))
    text(c, "按代价安排复检", 540, 800, 40, GRAY, "sans", "c", clamp01(a * 2))
    # 缺陷率变化：两根条
    q = g.pc(2, 0.0, 0.5, ease_back)
    if q > 0:
        pill(c, 540, 930, "缺陷率变了，红灯的含金量也会变", 36, CREAM, INK, "sans", 26, clamp01(q * 2), max(0.01, q))
        for i, (lab, frac, txt) in enumerate((("缺陷率 1%", 90 / 585, "15.4%"), ("缺陷率 10%", 900 / 1350, "约66.7%"))):
            y = 1050 + i * 130
            w = 560
            text(c, lab, 130, y + 16, 34, INK, "sans", "l", clamp01(q * 2))
            rect(c, 340, y - 24, w, 56, 14, "#E9DFC9", INK, 5, rough=False, a=clamp01(q * 2))
            rect(c, 340, y - 24, w * frac * g.pc(2, 0.3 + i * 0.5, 0.9, ease_out), 56, 14, RED, INK, 5, rough=False,
                 a=clamp01(q * 2))
            text(c, txt, 940, y + 16, 40, RED, "black", "r", clamp01((g.cue(2) - 1.0 - i * 0.5) * 2))


def s_ask(g):
    c, t = g.c, g.t
    glow(c, 540, 850, 560, GOLD, 0.3)
    person(c, LIN, 300, 1330, 0.95, face="think", t=t, look=(5, -4), armL=(105, 100), armR=(-20, -100),
           bob=math.sin(t * 2) * 3, tilt=4)
    a = g.pc(0, 0.0, 0.6, ease_back)
    thought(c, 700, 640, 560, 130, "测得多准？", 52, CREAM, clamp01(a * 2), max(0.01, a), dots_to=(400, 960))
    b = g.pc(1, 0.2, 0.6, ease_back)
    if b > 0:
        thought(c, 700, 820, 640, 140, "原本有多常见？", 56, PALEGOLD, clamp01(b * 2), max(0.01, b), dots_to=(420, 980))
        bulb(c, 960, 1020, 38 * max(0.01, b), 1.0)


def s_end(g):
    c, t = g.c, g.t
    glow(c, 540, 820, 600, GOLD, 0.45)
    big_title(c, ["识别很准，", "报警也可能【大多是错的】"], 520, t, 92)
    p = g.p(0.7, 0.6, ease_back)
    with xf(c, 540, 1010, sx=max(0.01, p)):
        for i in range(10):
            crate(c, -400 + i * 88, 40, 0.95, i < 1, 1.0 if i < 1 else 0.0)
    lamp(c, 540, 840, 1.0 if int(t * 4) % 2 == 0 else 0.6, 40, t)


# ------------------------------------------------------------------ 组装

def build() -> Episode:
    shots = [
        Shot(["检测器亮了红灯。", "小林心想：这台机器这么准，|这件九成是坏的。"], s_hook, tail=0.3, zoom=(1.0, 1.02)),
        Shot(["设定：一座虚构的工厂，|每天检查一万件产品。", "其中一百件有缺陷，|九千九百件合格。"], s_setup,
             tag="教学设定 · 虚构工厂"),
        Shot(["检测器能发现九成缺陷品，|也会把百分之五的合格品误报。", "这是检出率和误报率，|可不能统称“准确率”。"],
             s_stats, tag="教学设定 · 虚构数字"),
        Shot(["把产品分成两路。|有缺陷的一百件，检出九十件。", "合格的九千九百件，|百分之五被误报，是四百九十五件。"], s_split,
             tag="教学设定 · 虚构数字"),
        Shot(["红灯一共响了五百八十五次。", "其中真有缺陷的，|只有九十件。", "九十除以五百八十五，|大约百分之十五点四。"], s_merge,
             tag="教学设定 · 虚构数字"),
        Shot(["在这个设定里，红灯亮了，|真有缺陷的只占一成半。", "小林以为的九成，|其实约是百分之十五点四。"], s_contrast,
             tag="教学设定 · 虚构数字"),
        Shot(["原因在于合格品的基数太大。", "哪怕误报率不高，|误报的绝对数量也会很多。"], s_why, tag="教学设定 · 虚构数字"),
        Shot(["只盯着“测得有多准”，", "却忽略这件事原本占多少，|这就是【基率忽视】。",
              "二十世纪七十年代，研究就关注过：|人们怎样忽略原本的比例。"], s_term, tag="本期概念"),
        Shot(["但这不等于可以无视警报。", "红灯要认真对待，|更合理的是按代价安排复检。",
              "缺陷率变了，结果也会跟着变。"], s_recheck, tag="教学设定 · 虚构数字"),
        Shot(["以后听到“测得很准”，|除了问测得多准，", "也问一句：|这件事原本有多常见？"], s_ask),
        Shot(["识别很准，报警也可能大多是错的。"], s_end, tail=1.6),
    ]
    return Episode("05_基率忽视", shots).build()
