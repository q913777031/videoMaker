"""05 先动起来（白板手绘版）：拖了一周的事，怎么开头？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 I · 数字/曲线故事）：整讲围绕两组数字——“做之前预想的难度 / 满足”和“做完后真实的难度 / 满足”，
再加一条“劲头跟着行动往上走”的曲线。
开局（待办“写周报”拖了七天，日历七格都写着“明天”；小周坐等“想干了再干”，灯泡一直不亮）→
书中观点（亮书：顺序反了，先动，后有劲）→ ★drop：两根柱子，预想难度拔高、真做起来的那根砸下来矮一截 →
书里的反拖延表（做前预想、做完真实各填一遍；把写周报拆成三小步，逐格填数）→ 曲线：做着做着来劲了 →
身边的例子（健身卡办了没去：先换上鞋；简历一直没改：只改一行；两个例子连到同一个“先动”）→
具体做法（今晚给明天排三个小时的事 / 第一步拆到很小）→ 拉远看全板 → 评论区互动。
书中观点为转述：先行动、后有动力；反拖延表（事前预估难度和满足感、事后填真实值）；把大任务拆成小步；
每日活动计划（伯恩斯《伯恩斯新情绪疗法》第 5 章“战胜无为主义”，李亚萍译）。
表里与柱子上的数字均为示意，不是书中数据；例子为现实场景示意，做法据第 5 章思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, circle, doc, desk, face,
                               join, rect, stick)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out

from .common import BOOK, episode

ACC = "#D08A1E"
SQUARE_SHOT = 3                 # 场景 4：两根柱子 + 小周

b = Board(size=(3600, 11400))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def J():
    return len(b.shots) - 1


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """小周：简笔小人 + 挂绳工牌。(x, y) 为脚底。"""
    hy = y - 290 * s
    badge = join(P((x - 14 * s, hy + 48 * s), (x + 20 * s, hy + 104 * s), (x + 40 * s, hy + 48 * s)),
                 rect(x + 20 * s, hy + 124 * s, 34 * s, 40 * s, 5 * s))
    return join(stick(x, y, s, arms), badge)


def cloud(x, y, w, h, bumps=9) -> skia.Path:
    """念头云：一圈鼓包的云朵外轮廓。"""
    p = skia.Path()
    n = 180
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        r = 0.86 + 0.14 * abs(math.sin(a * bumps / 2))
        q = (x + w / 2 * r * math.cos(a), y + h / 2 * r * math.sin(a))
        p.moveTo(*q) if i == 0 else p.lineTo(*q)
    return p


def cloud_edge(x, y, w, h) -> skia.Path:
    """乌云的涂黑边：沿云轮廓来回的锯齿。"""
    p = skia.Path()
    n = 90
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        r = 0.86 + 0.14 * abs(math.sin(a * 9 / 2))
        r *= 1.0 if i % 2 == 0 else 1.1
        q = (x + w / 2 * r * math.cos(a), y + h / 2 * r * math.sin(a))
        p.moveTo(*q) if i == 0 else p.lineTo(*q)
    return p


def bulb(x, y, s=1.0) -> skia.Path:
    """吊着的灯泡：(x, y) 为玻璃泡中心。"""
    return join(P((x, y - 260 * s), (x, y - 110 * s)), rect(x, y - 92 * s, 60 * s, 40 * s, 6 * s),
                circle(x, y, 75 * s), P((x - 22 * s, y + 10 * s), (x - 8 * s, y - 20 * s), (x + 8 * s, y + 10 * s),
                                        (x + 22 * s, y - 20 * s)))


def calendar(x, y, n=7, cw=160, ch=230) -> skia.Path:
    """一排日历格：(x, y) 为整排中心，每格顶部一道装订线。"""
    parts = []
    for i in range(n):
        cx = x + (i - (n - 1) / 2) * cw
        parts += [rect(cx, y, cw - 14, ch, 10), P((cx - cw / 2 + 7, y - ch / 2 + 40), (cx + cw / 2 - 7, y - ch / 2 + 40))]
    return join(*parts)


def cell_x(x, i, n=7, cw=160):
    return x + (i - (n - 1) / 2) * cw


def bar_fn(x, base, w, h, color, overshoot=0.0):
    """柱子从底线升起（可带回弹）。"""

    def fn(c, k, t):
        e = ease_in_out(k)
        f = e + overshoot * math.sin(math.pi * k) if k < 1 else 1.0
        hh = h * f
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2, base - hh, x + w / 2, base), K.paint(color, 0.28))
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2, base - hh, x + w / 2, base), K.paint(color, 1, 9))
        return (x + w / 2, base - hh) if k < 1 else None

    return fn


def drop_fn(x, base, w, h, color, fall=900):
    """一块柱子从上方砸下来，k=1 时落地。"""

    def fn(c, k, t):
        off = fall * (1 - k * k)
        top = base - h - off
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2, top, x + w / 2, top + h), K.paint(color, 0.28))
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2, top, x + w / 2, top + h), K.paint(color, 1, 9))
        if k < 1:
            for dx in (-w / 3, 0, w / 3):
                c.drawLine(x + dx, top - 40, x + dx, top - 140, K.paint(color, 0.5, 6))
        return None

    return fn


def dot_fn(x, y, r, color):
    def fn(c, k, t):
        K.dot(c, x, y, r * min(1.0, k * 1.3), color)
        return None

    return fn


def bar_box(x, base, w, h) -> skia.Path:
    return P((x - w / 2, base), (x - w / 2, base - h), (x + w / 2, base - h), (x + w / 2, base))


def shoe(x, y, s=1.0) -> skia.Path:
    """运动鞋（侧视）：(x, y) 为鞋底中点。"""
    return join(P((x - 110 * s, y), (x - 110 * s, y - 70 * s), (x - 40 * s, y - 90 * s), (x - 10 * s, y - 50 * s),
                  (x + 70 * s, y - 35 * s), (x + 110 * s, y - 10 * s), (x + 110 * s, y), close=True),
                P((x - 110 * s, y - 18 * s), (x + 110 * s, y - 18 * s)),
                P((x - 45 * s, y - 70 * s), (x - 25 * s, y - 55 * s)), P((x - 30 * s, y - 80 * s), (x - 10 * s, y - 62 * s)))


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def rock(x, y, r=200) -> skia.Path:
    pts = [(x + r * f * math.cos(a), y + r * 0.72 * f * math.sin(a))
           for a, f in zip([i / 9 * 2 * math.pi for i in range(9)], (1.0, 0.92, 1.05, 0.9, 1.0, 0.95, 1.08, 0.9, 0.97))]
    return P(*pts, close=True)


def pebbles(x, y, gap=95) -> skia.Path:
    return join(*(oval(x + (i - 1) * gap, y + (i % 2) * 10, 62, 46) for i in range(3)))


def grid(x0, x1, ys, xs) -> skia.Path:
    """表格：横线 ys（自上而下）、竖线 xs，外框 x0–x1。"""
    parts = [P((x0, ys[0]), (x1, ys[0]), (x1, ys[-1]), (x0, ys[-1]), close=True)]
    parts += [P((x0, yy), (x1, yy)) for yy in ys[1:-1]]
    parts += [P((xx, ys[0] if top else ys[1]), (xx, ys[-1])) for xx, top in xs]
    return join(*parts)


# ---------------------------------------------------------------- 开局：拖了一周（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

CAL = (950, 860)
scene("又拖了一周", "灵魂拷问", (950, 760, 0.85), bars=2)
T("待办：写周报", 950, 520, 80, k0=0, k1=1, sfx="pop")
L(calendar(*CAL), 1, 2, BLACK, 8, sfx="wood_high")
for i in range(7):
    T("明天", cell_x(CAL[0], i), CAL[1] + 25, 56, RED if i == 6 else BLACK, k0=2.5 + 0.5 * i, k1=3.0 + 0.5 * i,
      sfx="pop" if i in (1, 3, 5) else None)

scene("等着想干那股劲", "灵魂拷问", (2650, 850, 0.85))
L(desk(2500, 1060, 440), 0, 0.9, sfx="wood_high")
L(zhou(2200, 1250, 0.8, "down"), 1, 1.8, BLACK, 9, sfx="pop")
L(face(2200, 1250, 0.8, "flat"), 1.8, 2.0)
L(bulb(2980, 560, 1.0), 2, 2.9, BLACK, 9, sfx="wood_low")
L(cloud(2330, 520, 440, 190), 3, 3.8, BLACK, 8, sfx="wood_high")
L(cloud_edge(2330, 520, 440, 190), 3.8, 4.6, BLACK, 5)
T("想干了再干", 2330, 520, 54, RED, k0=5, sfx="pop")
T("灯一直不亮", 2980, 760, 54, k0=7, k1=8, sfx="rim")

# ---------------------------------------------------------------- 书中观点（场景 3–4）

scene("书里说顺序反了", "伯恩斯新情绪疗法 · 书中观点", (950, 2300, 0.85))
L(book(950, 2080, 380, 240), 0, 0.9, sfx="wood_low")
T("伯恩斯新情绪疗法", 950, 1840, 62, GREEN, k0=1, k1=3, sfx="pop")
L(rect(640, 2520, 320, 160, 18), 3, 3.8, BLUE, 9, sfx="wood_high")
T("先动", 640, 2520, 76, BLUE, k0=3.8, k1=4.6)
L(arrow((820, 2520), (1060, 2520), 0.0, 40), 5, 5.8, BLACK, 9, sfx="wood_high")
L(rect(1250, 2520, 320, 160, 18), 6, 6.8, GREEN, 9, sfx="pop")
T("后有劲", 1250, 2520, 70, GREEN, k0=6.8, k1=7.7)

BASE = 2700
LX, RX, BW = 2380, 2780, 230
scene("真做没那么难", "书中观点 · 预想和真实", (2650, 2300, 0.8), shake=[0, (4, 18.0)], flashes=[0])
L(P((2180, BASE), (3000, BASE)), 0, 0.5, BLACK, 10, sfx="kick")
b.custom(J(), 0, 1, bar_fn(LX, BASE, BW, 800, RED, overshoot=0.08))
T("九十", LX, BASE - 860, 84, RED, k0=1, k1=1.8, sfx="pop")
T("预想难度", LX, BASE + 75, 58, RED, k0=2, k1=3, sfx="pop")
b.custom(J(), 3.55, 4, drop_fn(RX, BASE, BW, 270, BLUE))
H(4, "kick")
T("三十", RX, BASE - 330, 84, BLUE, k0=5, k1=5.8, sfx="pop")
T("真做起来", RX, BASE + 75, 58, BLUE, k0=6, k1=7, sfx="pop")
L(zhou(3160, BASE, 0.6, "point"), 7, 7.8, BLACK, 8, sfx="wood_high")
L(face(3160, BASE, 0.6, "smile"), 7.8, 8.0)

# ---------------------------------------------------------------- 书里的反拖延表（场景 5–8）

TX0, TX1 = 1230, 2370
COLS = [1400, 1670, 1870, 2070, 2270]
YS = [3490, 3580, 3670, 3790, 3910, 4030]
ROWY = [3730, 3850, 3970]
VT = (1800, 4000, 0.7)

scene("做前做后各填一遍", "书中方法 · 反拖延表", VT)
T("反拖延表", 1800, 3410, 70, ACC, k0=0, k1=1, sfx="pop")
L(grid(TX0, TX1, YS, [(1570, True), (1770, False), (1970, True), (2170, False)]), 1, 2, BLACK, 7, sfx="wood_high")
T("做前预想", 1770, 3535, 58, BLUE, k0=2, k1=3, sfx="pop")
T("做完真实", 2170, 3535, 58, GREEN, k0=3, k1=4, sfx="pop")
T("步骤", COLS[0], 3625, 56, k0=4, k1=4.8, sfx="pop")
T("难度", COLS[1], 3625, 56, BLUE, k0=5, k1=5.5, sfx="pop")
T("满足", COLS[2], 3625, 56, BLUE, k0=5.5, k1=6)
T("难度", COLS[3], 3625, 56, GREEN, k0=6, k1=6.5, sfx="pop")
T("满足", COLS[4], 3625, 56, GREEN, k0=6.5, k1=7)

scene("把写周报拆成三步", "书中方法 · 拆小步", VT)
L(doc(1250, 4320, 150, 190), 0, 0.9, BLACK, 8, sfx="wood_high")
T("写周报", 1250, 4500, 58, k0=1, k1=1.8, sfx="pop")
L(arrow((1380, 4320), (1620, 4320), 0.0, 36), 2, 2.8, BLACK, 8, sfx="wood_high")
T("拆成三小步", 1950, 4320, 66, RED, k0=3, k1=4.25, sfx="pop")
for n, s in enumerate(("打开文档", "列三条", "补数据")):
    T(s, COLS[0], ROWY[n], 56, k0=5 + n, k1=5.8 + n, sfx="pop")

scene("做之前都觉得难", "书中方法 · 做前预想", VT)
for n, s in enumerate(("八十", "七十", "九十")):
    T(s, COLS[1], ROWY[n], 60, RED, k0=n, sfx="pop")
for n, s in enumerate(("二十", "三十", "十")):
    T(s, COLS[2], ROWY[n], 60, BLUE, k0=3 + n, sfx="pop")
L(oval(COLS[1], 3850, 200, 400), 6, 6.9, RED, 7, sfx="ding")

scene("做完再填真实的", "书中方法 · 做完真实", VT)
for n, s in enumerate(("三十", "二十", "四十")):
    T(s, COLS[3], ROWY[n], 60, GREEN, k0=n, sfx="pop")
for n, s in enumerate(("六十", "七十", "五十")):
    T(s, COLS[4], ROWY[n], 60, GREEN, k0=3 + n, sfx="pop")
L(zhou(2380, 4600, 0.5, "up"), 6, 6.8, BLACK, 8, sfx="wood_high")
L(face(2380, 4600, 0.5, "smile"), 6.8, 7.0)

# ---------------------------------------------------------------- 曲线：劲头跟着行动涨（场景 9）

OX, OY0 = 800, 5900
CURVE = [(800, 5890), (1150, 5860), (1450, 5600), (1750, 5250)]


def curve_at(u):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = CURVE
    v = 1 - u
    return (v ** 3 * x0 + 3 * v * v * u * x1 + 3 * v * u * u * x2 + u ** 3 * x3,
            v ** 3 * y0 + 3 * v * v * u * y1 + 3 * v * u * u * y2 + u ** 3 * y3)


cv = skia.Path()
cv.moveTo(*CURVE[0])
cv.cubicTo(*CURVE[1], *CURVE[2], *CURVE[3])
scene("做着做着来劲了", "书中观点 · 先动后有劲", (1300, 5600, 0.85))
L(join(P((OX, 5180), (OX, OY0), (1820, OY0)), P((OX - 25, 5215), (OX, 5180), (OX + 25, 5215)),
       P((1785, OY0 - 25), (1820, OY0), (1785, OY0 + 25))), 0, 0.9, BLACK, 9, sfx="wood_high")
T("劲头", OX + 110, 5180, 58, k0=1, k1=1.8, sfx="pop")
T("开始做", OX, 5975, 58, k0=2, k1=2.8, sfx="pop")
L(cv, 3, 4, ACC, 13, sfx="wood_low")
for n, u in enumerate((0.45, 0.7, 0.95)):
    b.custom(J(), 4 + n, 4.4 + n, dot_fn(*curve_at(u), 16, ACC), sfx="tom")
T("想接着做", 1560, 5160, 60, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–11）

EB = 8000
scene("健身卡办了没去", "例子 · 健身卡", (1200, 7550, 0.85))
L(rect(950, 7150, 260, 160, 16), 0, 0.9, BLACK, 9, sfx="wood_high")
T("健身卡", 950, 7150, 56, k0=1, k1=1.8, sfx="pop")
L(join(P((850, EB), (1560, EB)), bar_box(1000, EB, 180, 600)), 2, 2.9, RED, 9, sfx="wood_low")
T("练一小时", 1000, EB + 70, 54, RED, k0=3, k1=4, sfx="pop")
L(bar_box(1380, EB, 180, 150), 4, 4.8, BLUE, 9, sfx="wood_high")
T("先换鞋", 1380, EB + 70, 54, BLUE, k0=5, k1=5.8, sfx="pop")
L(shoe(1380, EB - 190, 0.8), 6, 6.8, BLUE, 8, sfx="pop")
T("没去过", 1280, 7150, 56, RED, k0=7, k1=7.8, sfx="rim")

ZOOM = (1785, 7600, 0.52)
scene("简历一直没改", "例子 · 简历", (2400, 7550, 0.85))
L(doc(2200, 7150, 150, 190), 0, 0.9, BLACK, 8, sfx="wood_high")
T("简历", 2400, 7150, 60, k0=1, k1=1.8, sfx="pop")
L(join(P((2050, EB), (2760, EB)), bar_box(2200, EB, 180, 600)), 2, 2.9, RED, 9, sfx="wood_low")
T("改完整份", 2200, EB + 70, 54, RED, k0=3, k1=4, sfx="pop")
L(bar_box(2580, EB, 180, 150), 4, 4.8, BLUE, 9, sfx="wood_high")
T("改一行", 2580, EB + 70, 54, BLUE, k0=5, k1=5.8, sfx="pop")
b.move(J(), 5.8, ZOOM, dur=1.1)
L(join(arrow((1400, EB + 130), (1690, 8300), -0.15, 40), arrow((2560, EB + 130), (1910, 8300), 0.15, 40)), 6, 6.8,
  BLUE, 9, sfx="wood_high")
T("先动", 1800, 8350, 130, RED, k0=7, k1=7.8, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 12–13）

scene("把明天排出来", "做法一 · 排好明天", (1200, 9380, 0.85))
T("今晚排好明天", 1200, 8980, 76, BLUE, k0=0, k1=1, sfx="pop")
GY = [9090, 9270, 9450, 9630]
L(grid(750, 1650, GY, [(1050, True)]), 1, 2, BLACK, 8, sfx="wood_high")
for n, (tm, task) in enumerate((("九点", "打开文档"), ("十点", "列三条"), ("十一点", "补数据"))):
    yy = (GY[n] + GY[n + 1]) / 2
    T(tm, 900, yy, 58, k0=2 + 2 * n, k1=2.8 + 2 * n, sfx="pop")
    T(task, 1350, yy, 58, k0=3 + 2 * n, k1=3.9 + 2 * n, sfx="wood_high")

scene("拆到很小", "做法二 · 第一步拆小", (2650, 9450, 0.85))
L(rock(2340, 9150, 210), 0, 0.9, BLACK, 10, sfx="wood_low")
T("写周报", 2340, 9150, 60, k0=1, k1=1.8, sfx="pop")
L(arrow((2590, 9150), (2810, 9150), 0.0, 36), 2, 2.8, BLACK, 9, sfx="wood_high")
L(pebbles(3030, 9150), 3, 3.8, BLACK, 8, sfx="pop")
T("开个文档", 3030, 9290, 56, BLUE, k0=4, k1=5, sfx="pop")
L(zhou(2400, 9950, 0.6, "up"), 5, 5.8, BLACK, 8, sfx="wood_high")
L(face(2400, 9950, 0.6, "smile"), 5.8, 6.0)
L(cloud(2800, 9640, 420, 170), 6, 6.8, BLUE, 8, sfx="pop")
T("这个我能做", 2800, 9640, 52, BLUE, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5700, 0.17)
END = (1500, 10650, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
H(0, "cymbal", 0.5)
H(2, "ding")
b.move(J(), 4, END, dur=1.1)
H(4, "wood_high", 0.6)
T("你拖最久的一件事是什么？", 1500, 10270, 70, RED, k0=6, k1=8.75, sfx="pop")
L(cloud(1850, 10750, 520, 170), 9, 9.8, BLUE, 8, sfx="pop")
T("今天换掉一朵乌云", 1850, 10750, 50, BLUE, k0=9.8, k1=11.8)
T("下一讲：被领导当众批评，怎么接？", 1500, 10470, 52, k0=12, k1=15, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "action", "先动起来", "拖了一周的事，怎么开头？", ACC, b.shots,
                 [f"{BOOK}第 5 章 战胜无为主义（转述）",
                  "中译本：李亚萍译，中国城市出版社 2011；科学技术文献出版社 2014"],
                 "拖了一周的事|怎么【开头】", SQUARE_SHOT,
                 ["书中观点均为转述：第 5 章“战胜无为主义”讲拖延，书中观点是先有行动、后有动力，等“想做了再做”只会越等越不想做；"
                  "书中给的工具包括反拖延表（做之前预估难度和满足感，做完再填真实的）、把大任务拆成小步、每日活动计划。"
                  "“反拖延表”“每日活动计划”为通行译法，李亚萍译本的原用词未核实；上屏均为转述，不是逐字引文。",
                  "两根柱子、反拖延表里的数字（八十、七十、九十，二十、三十、十，三十、二十、四十，六十、七十、五十）"
                  "和“劲头曲线”均为示意，不是书中数据，也不是实验结果。",
                  "拖了一周的周报、健身卡办了没去、简历一直没改均为现实场景示意，不指向任何具体公司或个人；"
                  "“写周报”拆成打开文档、列三条、补数据三步，以及“今晚给明天排三个小时”“第一步拆到很小”，为据书中思路整理的做法。",
                  "本片为读书分享，不能替代诊断和治疗；情绪持续低落或有轻生念头，请尽快联系医生、心理咨询师或当地心理援助热线。"],
                 tags="#拖延")
    return b.attach(ep)
