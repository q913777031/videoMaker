"""第 04 期：可得性偏差（Availability Heuristic / Availability Bias）。"""

import math

from .engine import (BLUE, CREAM, GOLD, GRAY, INK, KRAFT, LGRAY, PALEBLUE, PALEGOLD, PALERED, PAPER, RED, SKIN,
                     Episode, Shot, arrow, circ, clamp01, crect, ease_back, ease_in, ease_io, ease_out, glow, lerp,
                     oval, poly, prog, rect, shadow, stroke, text, xf)
from .props import (HOST, LIN, big_title, bubble, burst, bulb, card, card_end, check, doodle, magnifier, person,
                    phone, pill, sparkle, squiggle, thought)

KINDS = ["star", "cat", "bolt", "flower", "fish", "balloon", "heart", "key"]
TINTS = [PALEGOLD, PALEBLUE, PALERED, "#D9E7C8", PALEGOLD, PALEBLUE, PALERED, "#D9E7C8"]


# ------------------------------------------------------------------ 通用部件

def vivid_card(c, cx, cy, w, h, kind, tint, rot=0.0, scale=1.0, a=1.0):
    card(c, cx, cy, w, h, tint, rot, scale, a)
    doodle(c, kind, 0, -h * 0.08, w / 150)
    rect(c, -w * 0.3, h * 0.28, w * 0.6, 12, 6, INK, None, 0, rough=False)
    card_end(c, a)


def plain_card(c, cx, cy, w, h, rot=0.0, scale=1.0, a=1.0):
    card(c, cx, cy, w, h, "#EFE6D2", rot, scale, a, lw=4)
    for i in range(3):
        rect(c, -w * 0.32, -h * 0.22 + i * h * 0.2, w * (0.64 if i < 2 else 0.4), 10, 5, LGRAY, None, 0, rough=False)
    card_end(c, a)


def sheet(g, cx, cy, w, h, title, vivid, start=0.0, scale=1.0, shown=6, halo=0.0):
    """名单纸：vivid 为真时每行带小插图与故事线。"""
    c = g.c
    if halo > 0:
        glow(c, cx, cy, w * 0.95, GOLD, 0.5 * halo)
    with xf(c, cx, cy, sx=scale):
        card(c, 0, 0, w, h, CREAM, 0, 1.0, 1.0)
        card_end(c)
        text(c, title, 0, -h / 2 + 62, 46, INK, "black", "c")
        rect(c, -w / 2 + 36, -h / 2 + 84, w - 72, 4, 2, INK, None, 0, rough=False)
        top = -h / 2 + 116
        step = (h - 160) / shown
        for i in range(shown):
            p = g.p(start + 0.3 + i * 0.2, 0.35)
            if p <= 0:
                continue
            y = top + i * step + step / 2
            a = p
            x0 = -w / 2 + 52
            if vivid:
                doodle(c, KINDS[i % 8], x0 + 28, y, 0.5, a)
                rect(c, x0 + 80, y - 20, 130, 14, 7, GRAY, None, 0, a=a, rough=False)
                squiggle(c, x0 + 80, x0 + 80 + 190, y + 14, 4, 5, RED if i % 2 else BLUE, 5, a)
            else:
                rect(c, x0 + 6, y - 7, 150 + (i * 37) % 70, 14, 7, LGRAY, None, 0, a=a, rough=False)
        dp = clamp01(g.t - start - 1.8)
        for k in range(3):
            circ(c, -22 + k * 22, h / 2 - 30, 5, GRAY, None, 0, a=dp)


def count_badge(c, cx, cy, p):
    if p <= 0:
        return
    with xf(c, cx, cy, sx=ease_back(p)):
        crect(c, 0, 0, 190, 78, 39, PALEGOLD, INK, 5, rough=False)
        text(c, "共20人", 0, 14, 42, INK, "black", "c")


def news_card(c, x, y, w=250, h=118, a=1.0):
    rect(c, x - w / 2, y - h / 2, w, h, 16, CREAM, INK, 4, a=a, rough=False)
    doodle(c, "warn", x - w / 2 + 52, y, 0.62, a)
    rect(c, x - 10, y - 26, 110, 12, 6, GRAY, None, 0, a=a, rough=False)
    rect(c, x - 10, y - 2, 130, 10, 5, LGRAY, None, 0, a=a, rough=False)
    rect(c, x - 10, y + 20, 90, 10, 5, LGRAY, None, 0, a=a, rough=False)


# ------------------------------------------------------------------ 镜头

def s_hook(g):
    c, t = g.c, g.t
    glow(c, 540, 930, 560, GOLD, 0.4)
    big_title(c, ["越容易想起来，", "就越常见吗？"], 340, t, 118)
    # 甲：鲜活卡片逐张扑到镜头前
    for i in range(7):
        p = g.p(0.2 + 0.17 * i, 0.5, ease_back)
        if p <= 0:
            continue
        ang = -26 + i * 8.6
        vivid_card(c, 290 + (i - 3) * 26, 990 - abs(i - 3) * 7 - (1 - p) * 560, 240, 322, KINDS[i], TINTS[i],
                   ang, lerp(2.3, 1.0, ease_out(p)), clamp01(p * 2))
    # 乙：平淡卡片整齐叠放
    for i in range(7):
        p = g.p(0.55 + 0.12 * i, 0.4)
        if p > 0:
            plain_card(c, 790 + i * 3, 990 + i * 5 - (1 - p) * 300, 224, 300, 0, 1.0, clamp01(p * 2))
    for lab, x in (("甲", 285), ("乙", 795)):
        p = g.p(1.5, 0.4, ease_back)
        pill(c, x, 1250, lab + "名单", 42, CREAM, INK, "sans", 30, clamp01(p * 2), max(0.01, p))
    q = g.p(1.9, 0.5, ease_back)
    if q > 0:
        with xf(c, 540, 700, rot=math.sin(t * 3) * 6, sx=q):
            text(c, "?", 0, 60, 190, RED, "black", "c", 1.0, PAPER, 18)


def s_sheet_a(g):
    c = g.c
    glow(c, 540, 880, 560, GOLD, 0.3)
    sheet(g, 330, 880, 560, 760, "甲名单", True, 0.1, 1.0)
    # 故事小插图：倒立走路的人 / 会开门的猫
    p1 = g.pc(1, 0.2, 0.5, ease_back)
    if p1 > 0:
        card(c, 830, 690, 250, 270, PALEBLUE, 7, max(0.01, p1), 1.0)
        circ(c, 0, 48, 24, SKIN, INK, 5, rough=False)
        stroke(c, [(0, 24), (0, -38)], INK, 9)
        stroke(c, [(0, -38), (-30, -88)], INK, 9)
        stroke(c, [(0, -38), (30, -88)], INK, 9)
        stroke(c, [(0, 8), (-34, 4)], INK, 8)
        stroke(c, [(0, 8), (34, 4)], INK, 8)
        stroke(c, [(-70, 76), (70, 76)], GRAY, 5)
        card_end(c)
    p2 = g.pc(1, 1.3, 0.5, ease_back)
    if p2 > 0:
        card(c, 830, 1040, 250, 270, PALEGOLD, -6, max(0.01, p2), 1.0)
        rect(c, -56, -90, 112, 164, 6, KRAFT, INK, 5, rough=False)
        circ(c, 36, 6, 8, GOLD, INK, 3, rough=False)
        doodle(c, "cat", -8, -10, 0.95)
        card_end(c)


def s_sheet_b(g):
    c = g.c
    glow(c, 540, 860, 520, GOLD, 0.25)
    sheet(g, 285, 860, 470, 680, "甲名单", True, -5, 0.96)
    sheet(g, 795, 860, 470, 680, "乙名单", False, 0.1, 0.96)
    with xf(c, 540, 860):
        text(c, "VS", 0, 20, 56, GRAY, "black", "c")
    count_badge(c, 285, 1250, g.pc(1, 0.1, 0.5, ease_out))
    count_badge(c, 795, 1250, g.pc(1, 0.5, 0.5, ease_out))
    p = g.pc(1, 1.0, 0.5, ease_back)
    if p > 0:
        with xf(c, 540, 1250, sx=p):
            text(c, "=", 0, 30, 100, RED, "black", "c", 1.0, PAPER, 12)


def s_feel(g):
    c = g.c
    inflate = g.p(0.2, 0.9, ease_back)
    glow(c, 330, 800, 560, GOLD, 0.45 * inflate)
    sheet(g, 320, 800, 470, 680, "甲名单", True, -5, lerp(0.96, 1.1, inflate), halo=inflate)
    sheet(g, 810, 830, 470, 680, "乙名单", False, -5, lerp(0.96, 0.78, inflate))
    for i in range(5):
        a = (g.t * 1.4 + i * 0.37) % 1.0
        sparkle(c, 130 + i * 95, 400 + 26 * math.sin(i * 2.1), 18 + 10 * math.sin(a * 6.28), GOLD, inflate)
    th = g.pc(0, 0.6, 0.6, ease_back)
    thought(c, 560, 1270, 600, 130, "好像甲更多？", 50, CREAM, clamp01(th * 2), max(0.01, th), dots_to=(380, 1160))


def s_phone(g):
    c, t = g.c, g.t
    glow(c, 700, 860, 480, GOLD, 0.3)
    scr = phone(c, 730, 830, 340, 660)
    sx, sy, sw, sh = scr
    c.save()
    c.clipRRect(__import__("skia").RRect.MakeRectXY(__import__("skia").Rect.MakeXYWH(sx, sy, sw, sh), 30, 30), True)
    off = (t * 150) % 150
    for i in range(-1, 6):
        news_card(c, sx + sw / 2, sy + 90 + i * 150 + off, sw - 36, 118)
    c.restore()
    person(c, LIN, 290, 1290, 0.95, face="worry", t=t, look=(6, 0), armL=(110, 100), armR=(30, -20),
           bob=math.sin(t * 2) * 3)
    for i in range(3):
        p = g.pc(0, 0.3 + i * 0.5, 0.4, ease_back)
        if p > 0:
            doodle(c, "warn", 330 + i * 110, 520 + (i % 2) * 40, 0.6 * p, clamp01(p * 2))
    ex = g.pc(0, 2.4, 0.4, ease_back)
    if ex > 0:
        text(c, "好几条！", 330, 460, 54, RED, "black", "l", 1.0, PAPER, 12)


def s_replay(g):
    c, t = g.c, g.t
    glow(c, 540, 800, 520, GOLD, 0.3)
    person(c, LIN, 330, 1330, 1.05, face="worry", t=t, look=(4, -6), armL=(100, 95), armR=(-60, -120),
           bob=math.sin(t * 2) * 3)
    th = g.p(0.1, 0.6, ease_back)
    thought(c, 650, 760, 600, 460, "", 40, CREAM, clamp01(th * 2), max(0.01, th), dots_to=(420, 980))
    # 回放：三张鲜明画面轮流闪回
    k = int(t * 2.2) % 3
    for i in range(3):
        on = 1.0 if i == k else 0.35
        p = g.p(0.5 + i * 0.12, 0.4, ease_back)
        if p > 0:
            card(c, 520 + i * 130, 720 + (i % 2) * 70, 190, 240, [PALERED, PALEGOLD, PALERED][i], -8 + i * 8,
                 max(0.01, p) * (1.08 if i == k else 0.94), on)
            doodle(c, "warn", 0, -10, 1.0)
            card_end(c, on)
    pill(c, 650, 560, "回放中…", 34, PALEGOLD, INK, "sans", 24, clamp01(th * 2))
    # 结论：到处都是
    p = g.pc(1, 0.1, 0.5, ease_back)
    if p > 0:
        burst(c, 770, 1130, 190 * p, PALERED, 1.0, 12, t * 20)
        text(c, "到处都是！", 770, 1148, 62, RED, "black", "c")


def s_zoom(g):
    c, t = g.c, g.t
    cols, rows = 10, 9
    cw, ch = 94, 92
    gx0, gy0 = 540 - cols * cw / 2, 880 - rows * ch / 2
    hot = {(3, 3), (4, 4), (6, 3), (5, 5)}
    z = lerp(5.2, 1.0, ease_io(prog(g.cue(1), -0.2, 2.6)))
    fx, fy = 540 + (4.5 - 4.5) * cw, 880 + 0.0
    glow(c, 540, 880, 560, GOLD, 0.25)
    with xf(c, 540, 880, sx=z):
        c.translate(-540 + 0.0, -880 + 0.0)
        for r in range(rows):
            for q in range(cols):
                x = gx0 + q * cw + cw / 2
                y = gy0 + r * ch + ch / 2
                if (q, r) in hot:
                    continue
                with xf(c, x, y):
                    rect(c, -38, -42, 76, 84, 10, "#EFE6D2", INK, 3, rough=False)
                    rect(c, -22, -16, 44, 7, 3, LGRAY, None, 0, rough=False)
                    rect(c, -22, 4, 30, 7, 3, LGRAY, None, 0, rough=False)
        for (q, r) in hot:
            x = gx0 + q * cw + cw / 2
            y = gy0 + r * ch + ch / 2
            pulse = 1 + 0.06 * math.sin(t * 5 + q)
            card(c, x, y, 82, 92, PALERED, 0, pulse, 1.0, lw=4)
            doodle(c, "warn", 0, -4, 0.5)
            card_end(c)
    lab = g.pc(1, 2.2, 0.5, ease_back)
    if lab > 0:
        pill(c, 540, 392, "大小只是印象，格子才是总体", 36, CREAM, INK, "sans", 26, clamp01(lab * 2), max(0.01, lab))


def s_term(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.4)
    # 第一句：印象大 ≠ 数量多
    p0 = g.pc(0, 0.1, 0.6, ease_back)
    if p0 > 0:
        with xf(c, 250, 660, sx=max(0.01, p0)):
            card(c, 0, 0, 230, 300, PALERED, -4, 1.0, 1.0, lw=6)
            doodle(c, "warn", 0, -10, 1.7)
            card_end(c)
        text(c, "印象很大", 250, 860, 40, RED, "sans", "c", clamp01(p0 * 2))
        with xf(c, 540, 660, sx=max(0.01, p0)):
            text(c, "≠", 0, 34, 110, INK, "black", "c")
        for r in range(4):
            for q in range(6):
                rect(c, 650 + q * 62, 540 + r * 66, 48, 54, 8, "#EFE6D2", INK, 3, a=clamp01(p0 * 2), rough=False)
        text(c, "数量很多", 820, 860, 40, GRAY, "sans", "c", clamp01(p0 * 2))
    # 第二句：容易想起来 → 觉得很常见
    a = g.pc(1, 0.0, 0.5, ease_back)
    if a > 0:
        with xf(c, 250, 1010, sx=max(0.01, a)):
            crect(c, 0, 0, 340, 130, 28, PALEGOLD, INK, 6)
            text(c, "容易想起来", 0, 17, 48, INK, "black", "c")
    b = g.pc(1, 1.0, 0.5, ease_back)
    if b > 0:
        with xf(c, 830, 1010, sx=max(0.01, b)):
            crect(c, 0, 0, 340, 130, 28, PALERED, INK, 6)
            text(c, "觉得很常见", 0, 17, 48, INK, "black", "c")
    arrow(c, (440, 1010), (650, 1010), INK, 9, 1.0, 28, g.pc(1, 0.6, 0.5))
    # 第三句：名称
    m = g.pc(2, 0.0, 0.6, ease_back)
    if m > 0:
        with xf(c, 540, 1210, sx=max(0.01, m)):
            text(c, "可得性偏差", 0, 40, 112, RED, "black", "c", 1.0, PAPER, 18)
        for i in range(4):
            a2 = (t * 1.3 + i * 0.4) % 1.0
            sparkle(c, 130 + i * 270, 1130 + 20 * math.sin(i * 2), 16 + 10 * math.sin(a2 * 6.28), GOLD, clamp01(m))
        text(c, "也叫“可得性启发式”", 540, 1285, 38, GRAY, "sans", "c", clamp01(g.pc(2, 0.5, 0.5)))


def s_research(g):
    c, t = g.c, g.t
    glow(c, 540, 840, 560, GOLD, 0.35)
    p = g.p(0.1, 0.7, ease_back)
    with xf(c, 540, 760, rot=-4, sx=max(0.01, p)):
        card(c, 0, 0, 640, 380, "#EBDDB9", 0, 1.0, 1.0, lw=6)
        card_end(c)
        for i in range(4):
            rect(c, -250, -150 + i * 0, 0, 0, 0, None, None, 0)
        text(c, "1973", 0, 60, 190, RED, "black", "c")
        rect(c, -250, 100, 500, 8, 4, INK, None, 0, rough=False)
        rect(c, -250, 130, 360, 8, 4, GRAY, None, 0, rough=False)
        rect(c, -250, 160, 430, 8, 4, GRAY, None, 0, rough=False)
    # 机制链：容易回忆的例子 → 估计一类事物有多大
    q = g.pc(1, 0.0, 0.5, ease_back)
    if q > 0:
        bulb(c, 260, 1100, 46 * max(0.01, q), 1.0)
        text(c, "容易回忆的例子", 260, 1210, 34, INK, "sans", "c", clamp01(q))
    arrow(c, (350, 1100), (690, 1100), INK, 9, 1.0, 28, g.pc(1, 0.6, 0.6))
    r = g.pc(1, 1.2, 0.5, ease_back)
    if r > 0:
        with xf(c, 800, 1100, sx=max(0.01, r)):
            for i, hh in enumerate((50, 90, 130, 70)):
                rect(c, -78 + i * 42, 60 - hh, 30, hh, 4, [PALEBLUE, BLUE, PALEBLUE, PALEBLUE][i], INK, 4, rough=False)
            text(c, "?", 70, -40, 70, RED, "black", "c", 1.0, PAPER, 8)
        text(c, "估计类别大小", 800, 1210, 34, INK, "sans", "c", clamp01(r))


def s_signal(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    # 一张醒目的卡片 + 放大镜 + 新证据
    p = g.p(0.1, 0.6, ease_back)
    pulse = 1 + 0.04 * math.sin(t * 5)
    card(c, 540, 800, 380, 500, PALERED, -3, max(0.01, p) * pulse, 1.0, lw=6)
    doodle(c, "warn", 0, -50, 2.2)
    rect(c, -110, 150, 220, 16, 8, INK, None, 0, rough=False)
    rect(c, -80, 184, 160, 12, 6, GRAY, None, 0, rough=False)
    card_end(c)
    m = g.pc(0, 0.8, 0.6, ease_back)
    if m > 0:
        magnifier(c, 720 + math.sin(t * 2) * 10, 640, 78 * max(0.01, m), clamp01(m * 2), -10)
    n = g.pc(1, 0.0, 0.5, ease_back)
    if n > 0:
        pill(c, 540, 1200, "也可能是重要的新证据", 42, PALEGOLD, INK, "sans", 30, clamp01(n * 2), max(0.01, n))
        check(c, 860, 1030, 120 * max(0.01, n), g.pc(1, 0.4, 0.5))


def s_ask(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    person(c, LIN, 200, 1330, 0.92, face="think", t=t, look=(5, -4), armL=(105, 100), armR=(-20, -100),
           bob=math.sin(t * 2) * 3, tilt=4)
    p = g.p(0.2, 0.6, ease_back)
    thought(c, 640, 700, 640, 140, "到处都是？", 56, CREAM, clamp01(p * 2), max(0.01, p), dots_to=(330, 980))
    # 两个选项：完整统计 vs 几个鲜明例子
    a = g.pc(1, 0.0, 0.6, ease_back)
    if a > 0:
        with xf(c, 450, 1060, sx=max(0.01, a)):
            card(c, 0, 0, 240, 290, CREAM, -3, 1.0, 1.0)
            for r in range(4):
                for q in range(4):
                    rect(c, -62 + q * 32, -88 + r * 36, 24, 26, 4, LGRAY, INK, 2, rough=False)
            card_end(c)
        with xf(c, 800, 1060, sx=max(0.01, a)):
            card(c, 0, 0, 240, 290, CREAM, 3, 1.0, 1.0)
            doodle(c, "warn", -36, -32, 0.7)
            doodle(c, "star", 50, 52, 0.7)
            doodle(c, "heart", 54, -62, 0.5)
            card_end(c)
        pill(c, 450, 1260, "完整统计", 36, PALEBLUE, INK, "sans", 24, clamp01(a * 2))
        pill(c, 800, 1260, "几个鲜明例子", 36, PALERED, INK, "sans", 24, clamp01(a * 2))
        text(c, "还是", 625, 1085, 46, RED, "black", "c", clamp01(a * 2), PAPER, 10)


def s_end(g):
    c, t = g.c, g.t
    glow(c, 540, 820, 600, GOLD, 0.45)
    big_title(c, ["越容易想起来，", "【不一定】越常见"], 560, t, 100)
    for i in range(6):
        a = (t * 1.2 + i * 0.31) % 1.0
        sparkle(c, 150 + i * 160, 420 + 40 * math.sin(i * 1.7), 14 + 14 * math.sin(a * 3.14), GOLD, g.p(0.8, 0.5))
    for i in range(5):
        p = g.p(0.6 + i * 0.15, 0.5, ease_back)
        if p > 0:
            vivid_card(c, 190 + i * 175, 1010 + math.sin(i) * 10, 150, 200, KINDS[i], TINTS[i], -12 + i * 6, p, clamp01(p * 2))


# ------------------------------------------------------------------ 组装

def build() -> Episode:
    shots = [
        Shot(["先做个小测试。", "我念两份名单，|你凭感觉猜：哪份人更多？"], s_hook, tail=0.3, zoom=(1.0, 1.02)),
        Shot(["甲名单里，每个人都带着一个小故事：", "有人会倒立走路，|有人养了一只会开门的猫。"], s_sheet_a,
             tag="教学改编 · 虚构名单"),
        Shot(["乙名单里，|名字只是平平淡淡地读过。", "两份名单其实一样长，各二十个人。"], s_sheet_b,
             tag="教学改编 · 虚构名单"),
        Shot(["可读完以后，|甲名单的人可能会让你觉得更多。", "它们更鲜活，也更容易想起来。"], s_feel,
             tag="教学改编 · 虚构名单"),
        Shot(["换到生活里：小林这周刷手机，|连着刷到好几条事故新闻。"], s_phone, tag="教学故事 · 小林"),
        Shot(["那些画面，他一闭眼就能回放。", "于是心里冒出一句：|最近，到处都是事故。"], s_replay,
             tag="教学故事 · 小林"),
        Shot(["我们把镜头拉远。", "那几条鲜明的画面，|只是众多事件里的几个格子。"], s_zoom, tag="教学示意 · 非真实统计",
             zoom=(1.0, 1.0)),
        Shot(["所以，印象很大，数量不一定多。", "用“想起来有多容易”|去判断“有多常见”，",
              "这种倾向就叫【可得性偏差】。"], s_term, tag="本期概念"),
        Shot(["一九七三年，|特沃斯基和卡尼曼研究过它：", "人们常凭容易回忆起的例子，|去估计一类事物有多大。"], s_research,
             tag="研究背景"),
        Shot(["当然，醒目的事件，|也可能带来重要的新信息。", "真实的风险，|并不会因为这个概念就消失。"], s_signal),
        Shot(["所以下次心里冒出“到处都是”，|先问自己一句：", "我看到的是完整统计，|还是只想起了几个特别鲜明的例子？"], s_ask),
        Shot(["越容易想起来，不一定越常见。"], s_end, tail=1.6),
    ]
    return Episode("04_可得性偏差", shots).build()
