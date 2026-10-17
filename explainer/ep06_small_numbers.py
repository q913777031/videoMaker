"""第 06 期：小数定律误区（Belief in the Law of Small Numbers）。

硬币实验室与点图均为教学示意；10 次抛掷"超过七成"的 56/1024 为精确计算（≥8 个正面：45+10+1）。
"""

import math

import numpy as np
import skia

from .engine import (BLUE, CREAM, GOLD, GRAY, INK, KRAFT, LGRAY, PALEBLUE, PALEGOLD, PALERED, PAPER, RED, SKIN,
                     Episode, Shot, arrow, circ, clamp01, col, crect, dline, ease_back, ease_in, ease_io, ease_out,
                     glow, lerp, oval, poly, prog, rect, shape, stroke, text, xf)
from .props import (LIN, big_title, bubble, burst, bulb, card, card_end, check, cross, magnifier, person, pill, sparkle,
                    thought)

COIN_FILL = "#EFC25A"
_RNG = np.random.default_rng(7)
DATA_A = _RNG.binomial(10, 0.5, 40) / 10        # 40 轮"抛 10 次"的正面占比（教学示意）
DATA_B = _RNG.binomial(1000, 0.5, 40) / 1000    # 40 轮"抛 1000 次"的正面占比（教学示意）
_POS = np.random.default_rng(11)
PILE = [(float(a), float(b)) for a, b in _POS.random((1000, 2))]
JITTER = _POS.random((10, 3))
WAFFLE_HI = set(_POS.permutation(1024)[:56].tolist())


# ------------------------------------------------------------------ 元件

def coin(c, x, y, r, face="H", flip=0.0, a=1.0):
    """硬币；flip 为翻转进度（0~1，一圈）。face: H 正面 / T 反面 / None 空白。"""
    k = abs(math.cos(flip * math.pi * 2))
    showing = face if math.cos(flip * math.pi * 2) >= 0 else ("T" if face == "H" else "H")
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    oval(c, x, y, r * max(0.08, k), r, COIN_FILL if showing != "T" else "#E3D2A6", INK, max(3, r * 0.14), rough=False)
    if k > 0.4 and showing:
        text(c, "正" if showing == "H" else "反", x, y + r * 0.34, r * 0.95 * k, INK, "black", "c", k)
    if a < 1:
        c.restore()


def jar(c, cx, cy, w, h, a=1.0):
    """透明玻璃罐，(cx, cy) 为中心。"""
    neck = w * 0.74
    path = skia.Path()
    path.moveTo(cx - neck / 2, cy - h / 2)
    path.lineTo(cx - neck / 2, cy - h / 2 + h * 0.1)
    path.quadTo(cx - w / 2, cy - h / 2 + h * 0.14, cx - w / 2, cy - h / 2 + h * 0.3)
    path.lineTo(cx - w / 2, cy + h / 2 - 40)
    path.quadTo(cx - w / 2, cy + h / 2, cx - w / 2 + 40, cy + h / 2)
    path.lineTo(cx + w / 2 - 40, cy + h / 2)
    path.quadTo(cx + w / 2, cy + h / 2, cx + w / 2, cy + h / 2 - 40)
    path.lineTo(cx + w / 2, cy - h / 2 + h * 0.3)
    path.quadTo(cx + w / 2, cy - h / 2 + h * 0.14, cx + neck / 2, cy - h / 2 + h * 0.1)
    path.lineTo(cx + neck / 2, cy - h / 2)
    shape(c, path, None, None, 0)
    p = skia.Paint(AntiAlias=True, Color=col(PALEBLUE, 0.35 * a))
    c.drawPath(path, p)
    return path


def jar_front(c, path, a=1.0):
    p = skia.Paint(AntiAlias=True, Color=col(INK, a), Style=skia.Paint.kStroke_Style, StrokeWidth=7,
                   StrokeJoin=skia.Paint.kRound_Join, StrokeCap=skia.Paint.kRound_Cap)
    c.drawPath(path, p)


def piles(c, cx, cy, w, h, n, r, a=1.0, hi=None):
    """罐中的一堆硬币点（小圆点代替细节）。"""
    pts = [skia.Point(cx - w / 2 + 14 + x * (w - 28), cy + h / 2 - 16 - y * h * 0.62) for x, y in PILE[:n]]
    p = skia.Paint(AntiAlias=True, Color=col(COIN_FILL, a), StrokeWidth=r * 2, Style=skia.Paint.kStroke_Style,
                   StrokeCap=skia.Paint.kRound_Cap)
    c.drawPoints(skia.Canvas.kPoints_PointMode, pts, p)


def ten_coins(c, cx, cy, w, h, p=1.0, heads=None):
    for i in range(10):
        q = clamp01(p * 10 - i * 0.8)
        if q <= 0:
            continue
        x = cx - w / 2 + 50 + (i % 4) * (w - 100) / 3 + (JITTER[i, 0] - 0.5) * 16
        y = cy + h / 2 - 46 - (i // 4) * 54 + (JITTER[i, 1] - 0.5) * 8 - (1 - q) * 200
        face = "H" if (heads is None or i in heads) else "T"
        coin(c, x, y, 28, face, 0.0, clamp01(q * 2))


def dot_plot(c, data, x0, x1, base, r, bins, hi_color=RED, hi_from=0.7, p=1.0, colr=BLUE, stagger=0.0):
    """按占比分箱堆叠的点图；p 为已落下的点比例。"""
    w = x1 - x0
    counts = {}
    n = len(data)
    show = int(n * clamp01(p))
    for i, v in enumerate(data):
        b = int(round(v * bins))
        k = counts.get(b, 0)
        counts[b] = k + 1
        if i >= show:
            continue
        x = x0 + w * b / bins
        y = base - r - k * (r * 2.05)
        hi = v > hi_from + 1e-9
        circ(c, x, y, r, hi_color if hi else colr, INK, 3, rough=False)


def axis(c, x0, x1, y, labels=((0, "0%"), (0.5, "50%"), (1, "100%")), a=1.0, size=28):
    stroke(c, [(x0, y), (x1, y)], INK, 5, a)
    for v, lab in labels:
        x = lerp(x0, x1, v)
        stroke(c, [(x, y), (x, y + 14)], INK, 4, a)
        text(c, lab, x, y + 48, size, GRAY, "sans", "c", a)


def threshold(c, x, y0, y1, label="70%", p=1.0):
    if p <= 0:
        return
    dline(c, (x, y0), (x, y0 + (y1 - y0) * p), RED, 5, 1.0, (14, 10))
    pill(c, x, y0 - 28, label, 30, PALERED, RED, "sans", 18, clamp01(p * 2), 1.0)


# ------------------------------------------------------------------ 镜头

def s_hook(g):
    c, t = g.c, g.t
    glow(c, 540, 880, 560, GOLD, 0.4)
    big_title(c, ["五次全赢，", "就说明方法有效？"], 340, t, 112)
    # 五个对勾依次盖章
    for i in range(5):
        st = 0.3 + 0.38 * i
        p = g.p(st, 0.35, ease_back)
        if p <= 0:
            continue
        x = 140 + i * 200
        with xf(c, x, 720, sx=max(0.01, p)):
            circ(c, 0, 0, 78, CREAM, INK, 6)
            check(c, 0, 4, 90, clamp01((t - st) * 5), BLUE, 15)
    happy = t > 0.5
    person(c, LIN, 540, 1370, 1.1, face="cheer" if t > 1.9 else "smile", t=t, look=(0, 0),
           armL=(-110, -90) if t > 1.9 else (100, 96), armR=(-70, -90) if t > 1.9 else (80, 84),
           bob=math.sin(t * 6) * 5 if t > 1.9 else 0)
    if t > 2.0:
        for i in range(6):
            a = (t * 1.5 + i * 0.3) % 1.0
            sparkle(c, 250 + i * 115, 940 + 40 * math.sin(i * 2.3), 16 + 10 * math.sin(a * 6.28), GOLD)


def s_lab(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    a = g.pc(0, 0.0, 0.6, ease_out)
    # 甲：小罐 10 枚；乙：大罐 1000 枚
    p1 = jar(c, 270, 980, 360, 520)
    ten_coins(c, 270, 980, 360, 520, g.pc(0, 0.4, 1.2))
    jar_front(c, p1)
    p2 = jar(c, 780, 920, 420, 640)
    piles(c, 780, 920, 420, 640, int(1000 * g.pc(1, 0.0, 1.8, ease_out)), 5.2)
    jar_front(c, p2)
    pill(c, 270, 1290, "甲组 抛10次", 38, PALEGOLD, INK, "sans", 26, clamp01(g.pc(0, 0.6, 0.4) * 2), 1.0)
    pill(c, 780, 1290, "乙组 抛1000次", 38, PALEBLUE, INK, "sans", 26, clamp01(g.pc(1, 0.0, 0.4) * 2), 1.0)
    if g.cue(1) > 1.8:
        pill(c, 540, 500, "各重复很多轮", 40, CREAM, INK, "sans", 28, clamp01((g.cue(1) - 1.8) * 3), 1.0)


def s_question(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.35)
    for i, (x, lab) in enumerate(((290, "甲组"), (790, "乙组"))):
        coin(c, x, 600, 100, "H", (t * 0.9 + i * 0.37) % 1.0)
        pill(c, x, 790, lab, 40, PALEGOLD if i == 0 else PALEBLUE, INK, "sans", 28, 1.0, 1.0)
    with xf(c, 540, 610, rot=math.sin(t * 3) * 6, sx=1.0 + 0.05 * math.sin(t * 5)):
        text(c, "?", 0, 60, 170, RED, "black", "c", 1.0, PAPER, 14)
    p = g.pc(0, 0.6, 0.6, ease_back)
    x0, x1, y = 100, 980, 1090
    rect(c, x0, y - 30, x1 - x0, 60, 20, "#EADFC8", INK, 6, rough=False, a=clamp01(p * 2))
    fill = g.pc(0, 1.0, 1.2, ease_io)
    rect(c, x0, y - 30, (x1 - x0) * 0.7 * fill, 60, 20, PALEGOLD, None, 0, rough=False)
    axis(c, x0, x1, y + 56, a=clamp01(p * 2))
    text(c, "正面占比", 540, y - 130, 40, GRAY, "sans", "c", clamp01(p * 2))
    if fill > 0.99:
        threshold(c, lerp(x0, x1, 0.7), y - 100, y + 56, "超过 70%", g.pc(0, 2.4, 0.5))


def s_numbers(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    # 上：甲组 10 格，≥8 格点亮
    a = g.pc(0, 0.0, 0.5, ease_back)
    pill(c, 270, 500, "甲组：抛 10 次", 38, PALEGOLD, INK, "sans", 24, clamp01(a * 2), max(0.01, a))
    for i in range(10):
        q = g.pc(0, 0.3 + i * 0.08, 0.3)
        on = i < 8
        rect(c, 100 + i * 88, 570, 76, 76, 12, COIN_FILL if on else "#E4DAC3", INK, 5, rough=False, a=clamp01(q * 2))
        if on and q > 0.5:
            text(c, "正", 138 + i * 88, 625, 44, INK, "black", "c", clamp01(q))
    if g.cue(0) > 1.2:
        text(c, "8 个正面 = 80%", 540, 720, 46, RED, "black", "c", clamp01((g.cue(0) - 1.2) * 2), PAPER, 10)
    # 下：乙组 1000，≥701 的长条
    b = g.pc(1, 0.0, 0.5, ease_back)
    pill(c, 300, 850, "乙组：抛 1000 次", 38, PALEBLUE, INK, "sans", 24, clamp01(b * 2), max(0.01, b))
    rect(c, 100, 920, 880, 76, 14, "#E4DAC3", INK, 5, rough=False, a=clamp01(b * 2))
    f = g.pc(1, 0.4, 1.4, ease_io)
    rect(c, 100, 920, 880 * 0.701 * f, 76, 14, COIN_FILL, None, 0, rough=False)
    rect(c, 100, 920, 880, 76, 14, None, INK, 5, rough=False, a=clamp01(b * 2))
    if g.cue(1) > 1.4:
        text(c, "701 个正面 ≈ 70.1%", 540, 1070, 46, RED, "black", "c", clamp01((g.cue(1) - 1.4) * 2), PAPER, 10)
    # 提示：比占比
    d = g.pc(2, 0.0, 0.6, ease_back)
    if d > 0:
        with xf(c, 540, 1230, sx=max(0.01, d)):
            crect(c, 0, 0, 860, 110, 55, CREAM, INK, 5, rough=False)
            text(c, "个数不好比，看占比刻度", 0, 16, 46, INK, "sans", "c")


def s_dots(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.25)
    # 甲：10 次
    pa = g.pc(0, 0.3, 2.0, ease_out)
    pill(c, 230, 480, "甲组 抛10次 × 40轮", 32, PALEGOLD, INK, "sans", 22, clamp01(g.pc(0, 0.0, 0.4) * 2), 1.0)
    dot_plot(c, DATA_A, 100, 980, 900, 17, 10, RED, 0.7, pa, BLUE)
    axis(c, 100, 980, 900, a=clamp01(g.pc(0, 0.0, 0.4) * 2))
    threshold(c, lerp(100, 980, 0.7), 520, 900, "70%", g.pc(0, 1.0, 0.6))
    # 乙：1000 次
    pb = g.pc(1, 0.2, 1.8, ease_out)
    pill(c, 260, 1030, "乙组 抛1000次 × 40轮", 32, PALEBLUE, INK, "sans", 22, clamp01(g.pc(1, 0.0, 0.4) * 2), 1.0)
    dot_plot(c, DATA_B, 100, 980, 1280, 8, 200, RED, 0.7, pb, BLUE)
    axis(c, 100, 980, 1280, a=clamp01(g.pc(1, 0.0, 0.4) * 2))
    threshold(c, lerp(100, 980, 0.7), 1120, 1280, "70%", g.pc(1, 0.8, 0.6))


def s_exact(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    # 甲：1024 种等可能结果中，≥8 个正面的有 56 种
    p = g.pc(0, 0.0, 0.5, ease_back)
    pill(c, 540, 470, "抛10次：1024 种等可能结果", 36, CREAM, INK, "sans", 26, clamp01(p * 2), max(0.01, p))
    cell = 15.5
    gx, gy = 540 - 16 * cell, 520
    show = g.pc(0, 0.3, 1.2, ease_out)
    hi_p = g.pc(0, 1.6, 0.6)
    for i in range(1024):
        if i / 1024 > show:
            break
        r, q = divmod(i, 32)
        hi = i in WAFFLE_HI and hi_p > 0
        rect(c, gx + q * cell, gy + r * cell, cell - 2.5, cell - 2.5, 2.5, RED if hi else "#D9CDB4", None, 0,
             rough=False)
    if hi_p > 0:
        text(c, "其中 56 种有 8 个以上正面", 540, 1065, 38, RED, "sans", "c", hi_p)
        with xf(c, 540, 1160, sx=max(0.01, ease_back(hi_p))):
            text(c, "56 ÷ 1024 ≈ 5.5%", 0, 0, 74, RED, "black", "c", 1.0, PAPER, 12)
    # 乙
    q = g.pc(1, 0.0, 0.6, ease_back)
    if q > 0:
        with xf(c, 540, 1200, sx=1.0):
            pass
        card(c, 540, 1235, 840, 120, PALEBLUE, 0, max(0.01, q), 1.0)
        text(c, "抛1000次、超过七成：几乎不会发生", 0, 16, 42, INK, "sans", "c")
        card_end(c)


def s_term(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.35)
    # 左：小罐，抖动大；右：大罐，稳
    a = g.pc(0, 0.0, 0.6, ease_back)
    if a > 0:
        with xf(c, 270, 700, sx=max(0.01, a) * 1.25):
            wob = math.sin(t * 7) * 0.45 * 12
            for i, v in enumerate((0.2, 0.8, 0.5, 0.9, 0.3)):
                circ(c, -110 + i * 55, 80 - v * 220 + wob * (1 if i % 2 else -1), 16, BLUE, INK, 3, rough=False)
            stroke(c, [(-140, 100), (140, 100)], INK, 5)
            text(c, "小样本：忽高忽低", 0, 170, 36, INK, "sans", "c")
    b = g.pc(0, 0.5, 0.6, ease_back)
    if b > 0:
        with xf(c, 810, 700, sx=max(0.01, b) * 1.25):
            for i, v in enumerate((0.47, 0.52, 0.5, 0.49, 0.53)):
                circ(c, -110 + i * 55, 80 - v * 220, 10, BLUE, INK, 3, rough=False)
            stroke(c, [(-140, 100), (140, 100)], INK, 5)
            text(c, "大样本：围着一半", 0, 170, 36, INK, "sans", "c")
    m = g.pc(1, 0.0, 0.6, ease_back)
    if m > 0:
        with xf(c, 540, 1010, sx=max(0.01, m)):
            text(c, "小数定律误区", 0, 40, 112, RED, "black", "c", 1.0, PAPER, 18)
    s = g.pc(2, 0.0, 0.5, ease_back)
    if s > 0:
        with xf(c, 540, 1130, sx=max(0.01, s)):
            crect(c, 0, 0, 640, 84, 42, CREAM, INK, 5, rough=False)
            text(c, "认知误区", -150, 14, 40, RED, "black", "c")
            text(c, "≠", 0, 14, 44, INK, "black", "c")
            text(c, "统计定理", 150, 14, 40, GRAY, "black", "c")
    y = g.pc(3, 0.0, 0.6, ease_back)
    if y > 0:
        pill(c, 540, 1270, "1971 · 研究背景", 38, PALEGOLD, INK, "sans", 28, clamp01(y * 2), max(0.01, y))


def s_bounds(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    a = g.pc(0, 0.0, 0.6, ease_back)
    if a > 0:
        card(c, 290, 760, 440, 560, CREAM, -2, max(0.01, a), 1.0)
        text(c, "小样本", 0, -190, 56, INK, "black", "c")
        for i in range(3):
            circ(c, -90 + i * 90, -60, 26, BLUE, INK, 4, rough=False)
        text(c, "可以当线索", 0, 70, 44, INK, "sans", "c")
        text(c, "不宜当结论", 0, 140, 44, RED, "sans", "c")
        text(c, "极端 ≠ 作弊", 0, 220, 38, GRAY, "sans", "c")
        card_end(c)
    b = g.pc(1, 0.0, 0.6, ease_back)
    if b > 0:
        card(c, 790, 760, 440, 560, CREAM, 2, max(0.01, b), 1.0)
        text(c, "大样本", 0, -190, 56, INK, "black", "c")
        for r in range(3):
            for q in range(7):
                circ(c, -108 + q * 36, -90 + r * 36, 12, BLUE, INK, 3, rough=False)
        text(c, "更稳定", 0, 70, 44, INK, "sans", "c")
        text(c, "但要抽得公平", 0, 140, 44, RED, "sans", "c")
        text(c, "数量不消除偏差", 0, 220, 38, GRAY, "sans", "c")
        card_end(c)
    if b > 0.5:
        magnifier(c, 960, 520, 54 * b, clamp01(b), -10)


def _crowd(c, x0, y0, cols, rows, dx, dy, r, p, hi=0):
    n = int(cols * rows * clamp01(p))
    for i in range(n):
        x, y = x0 + (i % cols) * dx, y0 + (i // cols) * dy
        colr = [BLUE, RED, GOLD][i % 3] if i < hi else "#B9AE9C"
        circ(c, x, y - r * 1.5, r * 0.7, colr, None, 0, rough=False)
        oval(c, x, y + r * 0.1, r * 0.9, r * 1.0, colr, None, 0, rough=False)


def s_close(g):
    c, t = g.c, g.t
    glow(c, 540, 860, 560, GOLD, 0.3)
    person(c, LIN, 190, 1330, 0.85, face="smile" if g.cue(0) < 1.2 else "think", t=t, look=(5, -4),
           armL=(105, 100), armR=(-30, -100) if g.cue(0) > 1.2 else (80, 84), bob=math.sin(t * 2) * 3)
    if g.cue(0) > 0.6:
        for i in range(5):
            q = g.pc(0, 0.6 + i * 0.12, 0.3, ease_back)
            if q > 0:
                with xf(c, 640 + i * 90, 560, sx=max(0.01, q)):
                    circ(c, 0, 0, 34, CREAM, INK, 4, rough=False)
                    check(c, 0, 2, 36, 1.0, BLUE, 8)
    # 三个人 → 三百人
    if g.cue(1) > 0 and g.cue(2) < 0.4:
        q = g.pc(1, 0.0, 0.5, ease_back)
        fade = 1 - clamp01(g.cue(2) * 2.5) if len(g.shot.cue_t) > 2 else 1.0
        for i in range(3):
            with xf(c, 560 + i * 140, 960, sx=max(0.01, q) * 1.5):
                colr = [BLUE, RED, GOLD][i]
                circ(c, 0, -36, 24, SKIN, INK, 4, a=fade, rough=False)
                oval(c, 0, 18, 36, 44, colr, INK, 4, a=fade, rough=False)
    if g.cue(2) > 0:
        _crowd(c, 392, 720, 20, 15, 31.5, 31, 7.5, g.pc(2, 0.3, 1.6, ease_out))
        q = g.pc(2, 1.4, 0.5, ease_back)
        if q > 0:
            pill(c, 700, 1230, "再看 300 个人，结论一样吗？", 38, PALEGOLD, INK, "sans", 26, clamp01(q * 2), max(0.01, q))


def s_end(g):
    c, t = g.c, g.t
    glow(c, 540, 820, 600, GOLD, 0.45)
    big_title(c, ["五次全赢，", "先别急着说【“稳了”】"], 520, t, 100)
    for i in range(5):
        p = g.p(0.5 + i * 0.15, 0.4, ease_back)
        with xf(c, 140 + i * 200, 960, sx=max(0.01, p)):
            circ(c, 0, 0, 62, CREAM, INK, 5)
            check(c, 0, 3, 70, 1.0, BLUE, 12)
    q = g.p(1.4, 0.5, ease_back)
    if q > 0:
        with xf(c, 540, 1180, sx=max(0.01, q)):
            text(c, "再多看一些，再下结论", 0, 0, 52, GRAY, "sans", "c")


# ------------------------------------------------------------------ 组装

def build() -> Episode:
    shots = [
        Shot(["小林试了个新方法，连赢五次！", "他兴奋地说：|这方法稳了！"], s_hook, tail=0.3, zoom=(1.0, 1.02)),
        Shot(["我们先去一间虚构的硬币实验室，|看看小样本会怎样。", "甲组抛十次，乙组抛一千次，|各重复很多轮。"], s_lab,
             tag="教学设定 · 虚构实验室"),
        Shot(["问题是：哪一组更容易出现|“正面占比超过七成”？"], s_question, tag="教学设定 · 虚构实验室"),
        Shot(["甲组只要八个或更多正面，", "乙组却要七百零一个或更多。", "个数不好比，要看占比。"], s_numbers,
             tag="教学设定 · 虚构实验室"),
        Shot(["把很多轮的结果，|按正面占比摆开。", "甲组的点散得很开，|乙组紧紧挤在一半附近。"], s_dots,
             tag="原理示意 · 非实验记录"),
        Shot(["按公平硬币算，甲组抛十次，|超过七成的可能性约百分之五点五。", "乙组要超过七成，|小到几乎不会发生。"], s_exact,
             tag="按公平硬币精确计算"),
        Shot(["样本越小，波动越大，|极端结果就越容易出现。", "把“小样本能代表整体”当真，|就是【小数定律误区】。",
              "名字像定理，其实是认知误区。", "一九七一年，特沃斯基和卡尼曼|就讨论过人们对小样本的误判。"], s_term,
             tag="本期概念"),
        Shot(["小样本并非没用，|极端结果也不能直接证明作弊。", "大样本也得抽得公平，|数量多不会自动消除偏差。"], s_bounds),
        Shot(["回到小林。连赢五次，|只是一个不错的开始。", "下次听到“我们三个人都这样”，", "再问一句：如果再看三百个人，|结论还会一样吗？"],
             s_close),
        Shot(["五次全赢，先别急着说“稳了”。"], s_end, tail=1.6),
    ]
    return Episode("06_小数定律误区", shots).build()
