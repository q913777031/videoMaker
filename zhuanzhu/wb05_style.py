"""05 选对专注法（白板手绘版）：没有整块时间，还能专注吗？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 E 自测清单，开局让观众打勾）：白板上一张清单、四个空方框 → 四道题逐个打勾（能整周断联吗 / 一年有淡季吗 /
每天有固定空档吗 / 说专注就专注吗）→ drop：四条日历“砰”地拍上白板（全蓝 / 半蓝 / 每天一块 / 碎块）→
亮书：书里给了四种排法（上屏用白话名：断联 / 分段 / 每天定时 / 见缝插针）→ 四种逐个讲（火柴人 + 名牌：高德纳、荣格、
格兰特、艾萨克森；链条法；见缝插针新手别先选），小红点在每种排法里能钻的缝不一样大 →
回到清单对一下（每道题对一条日历）→ 打工人多半适合“每天定时”：小周每天早上一块蓝 → 起步：先连七天 →
拉远看清单和四条日历 → 评论区：你打了几个勾。
出处：卡尔·纽波特《深度工作》准则1“工作要深入”中“选定你的深度哲学”一节（转述）；四道自测题与对应关系、
小周的日程与“先连七天”为据书中思路整理的示意。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, cross, join, rect,
                               stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#2F7F8C"
SQUARE_SHOT = 10                # 场景 11：小周 + 每天一块蓝的课表

b = Board(size=(3600, 8200))
GREY = "#B9BEC6"


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def J():
    return len(b.shots) - 1


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def envelope(x, y, w=180, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 8), P((x - w / 2, y - h / 2), (x, y + 8), (x + w / 2, y - h / 2)))


def tower(x, y, w=180, h=420) -> skia.Path:
    """湖边石塔：(x, y) 为塔底中点；塔身 + 垛口 + 一扇窗 + 几道石缝。"""
    top = y - h
    parts = [P((x - w / 2, y), (x - w / 2, top), (x + w / 2, top), (x + w / 2, y))]
    cren = [(x - w / 2, top)]
    n = 5
    for i in range(n):
        x0 = x - w / 2 + w * i / n
        x1 = x - w / 2 + w * (i + 1) / n
        if i % 2 == 0:
            cren += [(x0, top - 45), (x1, top - 45), (x1, top)]
        else:
            cren += [(x1, top)]
    parts.append(P(*cren))
    parts.append(join(P((x - 22, top + 140), (x - 22, top + 90), (x + 22, top + 90), (x + 22, top + 140)),
                      P((x - 22, top + 140), (x + 22, top + 140))))
    for yy in (top + 210, top + 290):
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
    parts.append(P((x - 30, y), (x - 30, y - 80), (x + 30, y - 80), (x + 30, y)))
    return join(*parts)


def waves(x0, x1, y, amp=12, step=60) -> skia.Path:
    return join(underline(x0, x1, y, amp, step), underline(x0 + 60, x1 - 60, y + 40, amp, step))


def scissors(x, y, s=1.0) -> skia.Path:
    return join(circle(x - 40 * s, y + 40 * s, 22 * s), circle(x + 40 * s, y + 40 * s, 22 * s),
                P((x - 25 * s, y + 25 * s), (x + 30 * s, y - 70 * s)), P((x + 25 * s, y + 25 * s), (x - 30 * s, y - 70 * s)))


def badge_stick(x, y, s=0.85, arms="down") -> skia.Path:
    """小周：火柴人 + 胸前工牌小方块。"""
    hy = y - 290 * s
    return join(stick(x, y, s, arms), rect(x + 24 * s, hy + 130 * s, 34 * s, 44 * s, 4 * s),
                P((x, hy + 60 * s), (x + 24 * s, hy + 108 * s)))


def chain(x0, x1, y, step=120) -> skia.Path:
    """把一排叉连起来的链：一串上下起伏的弧。"""
    p = skia.Path()
    p.moveTo(x0, y)
    x, k = x0, 0
    while x < x1 - 1:
        p.quadTo(x + step / 2, y + (40 if k % 2 == 0 else -40), x + step, y)
        x += step
        k += 1
    return p


def red_dot(pts, num="9", r=55, hop=110):
    """系列角色小红点：红色实心圆 + 白字数字 + 两条小短腿。
    pts = [(拍, x, y), ...]（拍为本镜头内拍号）：第一个拍点弹出，之后在每个拍点前 0.3 秒跳到下一处（带弧线）。"""
    j = J()
    times = [(b.t_of(j, k), x, y) for k, x, y in pts]

    def fn(c, k, t):
        if t >= b.shots[j].t1:           # 只在本场景出现，换场后不留在白板上
            return None
        t0 = times[0][0]
        x, y = times[0][1], times[0][2]
        lift = 0.0
        for (ta, xa, ya), (tb, xb, yb) in zip(times, times[1:]):
            if t >= tb:
                x, y = xb, yb
                continue
            f = clamp01((t - (tb - 0.3)) / 0.3)
            x, y = xa + (xb - xa) * f, ya + (yb - ya) * f
            lift = hop * 4 * f * (1 - f)
            break
        a = clamp01((t - t0) / 0.25)
        sc = ease_out(a) * (1 + 0.25 * math.sin(math.pi * a))
        if sc <= 0:
            return None
        y -= lift
        rr = r * sc
        for d in (-1, 1):
            K.seg(c, x + d * rr * 0.35, y + rr * 0.8, x + d * rr * 0.45, y + rr * 1.45, BLACK, 7)
            K.seg(c, x + d * rr * 0.45, y + rr * 1.45, x + d * rr * 0.75, y + rr * 1.45, BLACK, 7)
        K.dot(c, x, y, rr, RED)
        c.drawCircle(x, y, rr, K.paint("#8E1F18", 1, 5))
        K.text(c, num, x, y + rr * 0.04, rr * (1.0 if len(num) == 1 else 0.62), "black", "#FFFFFF")
        return None

    return fn


# ---------------------------------------------------------------- 清单与四条日历的位置（区块 A）

ROWS = [1010, 1210, 1410, 1610]          # 四道题 / 四条日历 同一行
QX, BX = 840, 1260                        # 题目中心、方框中心
SX0, CW, SH = 1600, 95, 120               # 日历条左端、格宽、条高（每条 7 格）
SCX = SX0 + CW * 3.5                      # 日历条中心
LX = 2520                                 # 四种排法的名字


def strips_fn(c, k, t):
    """四条日历一起从上方拍下来：全蓝 / 半蓝 / 每天一块 / 碎块。"""
    f = ease_out(clamp01(k))
    drop = (1 - f) * 260
    sc = 1 + (1 - f) * 0.25
    for i, y in enumerate(ROWS):
        c.save()
        c.translate(SCX, y - drop)
        c.scale(sc, sc)
        c.translate(-SCX, -y)
        x0, x1, y0 = SX0, SX0 + CW * 7, y - SH / 2
        if i == 0:
            c.drawRect(skia.Rect.MakeXYWH(x0, y0, CW * 7, SH), K.paint(BLUE, 0.85))
        elif i == 1:
            c.drawRect(skia.Rect.MakeXYWH(x0, y0, CW * 3.5, SH), K.paint(BLUE, 0.85))
        elif i == 2:
            for d in range(7):
                c.drawRect(skia.Rect.MakeXYWH(x0 + d * CW + 8, y0 + 8, CW - 16, SH * 0.3), K.paint(BLUE, 0.85))
        else:
            for d, fx, fy in ((0, 0.2, 0.5), (1, 0.55, 0.15), (2, 0.3, 0.6), (4, 0.6, 0.35), (5, 0.15, 0.1),
                              (6, 0.5, 0.6)):
                c.drawRect(skia.Rect.MakeXYWH(x0 + d * CW + fx * (CW - 34), y0 + 10 + fy * (SH - 54), 30, 30),
                           K.paint(BLUE, 0.85))
        c.drawRect(skia.Rect.MakeXYWH(x0, y0, CW * 7, SH), K.paint(BLACK, 1, 7))
        for d in range(1, 7):
            K.seg(c, x0 + d * CW, y0, x0 + d * CW, y0 + SH, BLACK, 5)
        c.restore()
    return None


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 开局：先打个勾（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

scene("先打个勾", "自测 · 先打个勾", (880, 1250, 0.72), bars=2)
L(rect(880, 1250, 1040, 1150, 30), 0, 0.9, BLACK, 10, sfx="wood_high")
L(join(rect(880, 675, 240, 70, 14), circle(880, 640, 18)), 1, 1.6, BLACK, 9, sfx="pop")
L(join(*[rect(BX, y, 80, 80, 8) for y in ROWS]), 2, 2.9, BLACK, 8, sfx="wood_high")
T("先打个勾", 880, 800, 84, RED, k0=3, k1=4, sfx="pop")
C(5, 5.4, red_dot([(5, 1450, 760)], "1"), sfx="ding")

scene("能断联吗", "自测 · 第一、二题", (880, 1200, 0.82))
T("能整周断联吗？", QX, ROWS[0], 60, k0=0, sfx="pop")
L(cross(BX, ROWS[0], 26), 2, 2.6, RED, 9, sfx="rim")
T("一年有淡季吗？", QX, ROWS[1], 60, k0=3, sfx="pop")
L(cross(BX, ROWS[1], 26), 5, 5.6, RED, 9, sfx="rim")
C(6, 6.5, red_dot([(6, 1470, 1010)], "9"), sfx="ding")

scene("有固定空档吗", "自测 · 第三、四题", (880, 1310, 0.82))
T("每天有固定空档吗？", QX, ROWS[2], 60, k0=0, sfx="pop")
L(check(BX, ROWS[2], 34), 3, 3.6, GREEN, 10, sfx="ding")
T("说专注就专注吗？", QX, ROWS[3], 60, k0=4, sfx="pop")
L(cross(BX, ROWS[3], 26), 6, 6.6, RED, 9, sfx="rim")
T("你呢？", 880, 1755, 64, RED, k0=7, sfx="pop")

# ---------------------------------------------------------------- drop：四条日历拍上白板（场景 4）

scene("四种排法", "书中观点 · 四种排法", (2000, 1250, 0.8), shake=[0], flashes=[0])
C(0, 0.7, strips_fn, sfx="kick")
T("四种排法", SCX, 820, 90, k0=2, k1=3, sfx="pop")
C(4, 5.6, red_dot([(4, SX0 + CW * 1.5, ROWS[3] - 120), (5, SX0 + CW * 3.5, ROWS[3] - 120)], "9"), sfx="ding")
H(5, "pop")
T("白格子，它就能钻", SCX, 1770, 64, RED, k0=6, sfx="pop")

# ---------------------------------------------------------------- 亮书：书里给了四种（场景 5）

scene("书里给了四种", "深度工作 · 书中观点", (2180, 1200, 0.62))
L(book(2850, 690, 300, 200), 0, 0.9, BLACK, 9, sfx="wood_low")
T("《深度工作》", 2850, 870, 58, GREEN, k0=1, sfx="pop")
for n, name in enumerate(("断联", "分段", "每天定时", "见缝插针")):
    T(name, LX, ROWS[n], 66, BLUE, k0=3 + n, sfx="pop")
L(underline(2690, 3010, 910, 8, 32), 7, 7.6, GREEN, 6)

# ---------------------------------------------------------------- 四种逐个讲（场景 6–9，区块 C）

scene("杂事全断", "书中观点 · 断联", (950, 4450, 0.85))
T("① 断联", 950, 4020, 80, BLUE, k0=0, sfx="pop")
L(P((1270, 4170), (1270, 4870)), 1, 1.8, BLACK, 16, sfx="wood_low")
L(stick(640, 4770, 0.8, "point"), 2, 2.9, BLACK, 10, sfx="wood_high")
T("高德纳", 640, 4850, 54, k0=3, sfx="pop")
L(envelope(980, 4400), 4, 4.8, BLACK, 9, sfx="pop")
L(cross(980, 4400, 75), 5, 5.6, RED, 11, sfx="rim")
C(6, 7.6, red_dot([(6, 1480, 4530), (7, 1340, 4530), (7.6, 1470, 4550)], "9"), sfx="ding")
H(7, "tom")

scene("一段关门", "书中观点 · 分段", (2650, 4450, 0.85))
T("② 分段", 2650, 4020, 80, BLUE, k0=0, sfx="pop")
L(tower(2330, 4690), 1, 1.9, BLACK, 9, sfx="wood_low")
L(waves(2080, 2580, 4730), 2, 2.8, BLUE, 8, sfx="wood_high")
T("荣格", 2330, 4860, 56, k0=3, sfx="pop")
YB = (2650, 3190, 4380)                 # 一年 12 格：左半照常，右半关门
L(join(rect((YB[0] + YB[1]) / 2, YB[2], YB[1] - YB[0], 90, 6),
       *[P((YB[0] + i * 45, YB[2] - 45), (YB[0] + i * 45, YB[2] + 45)) for i in range(1, 12)]),
  4, 4.9, BLACK, 7, sfx="wood_high")


def _half(c, k, t):
    c.drawRect(skia.Rect.MakeXYWH(YB[0] + 270, YB[2] - 45, 270 * k, 90), K.paint(BLUE, 0.85))
    return None


C(5, 5.6, _half, sfx="pop")
T("格兰特", 2920, 4520, 56, k0=6, sfx="pop")
C(7, 7.5, red_dot([(7, YB[0] + 110, YB[2] - 130)], "9"), sfx="ding")

CAL = (460, 5700, 140)                  # 日历左上角 x、y，格宽（7 列 × 2 行）
scene("别断链", "书中观点 · 每天定时", (950, 5900, 0.85))
T("③ 每天定时", 950, 5470, 80, BLUE, k0=0, sfx="pop")
gx, gy, gw = CAL
L(join(rect(gx + gw * 3.5, gy + gw, gw * 7, gw * 2, 8),
       P((gx, gy + gw), (gx + gw * 7, gy + gw)),
       *[P((gx + gw * i, gy), (gx + gw * i, gy + gw * 2)) for i in range(1, 7)]), 2, 2.9, BLACK, 7, sfx="wood_low")
DAYS = [(gx + gw * (i % 7) + gw / 2, gy + gw * (i // 7) + gw / 2) for i in range(10)]
L(join(*[cross(x, y, 34) for x, y in DAYS]), 3, 5.6, RED, 9, sfx="wood_high")
H(4, "wood_high", 0.6)
H(5, "wood_high", 0.6)
L(join(chain(DAYS[0][0], DAYS[6][0], DAYS[0][1], gw), chain(DAYS[7][0], DAYS[9][0], DAYS[7][1], gw)), 6, 6.8, BLUE, 6,
  sfx="ding")
L(scissors(1260, 6220), 7, 7.8, RED, 8, sfx="rim")
C(7, 7.5, red_dot([(7, 1110, 6200)], "9"))

DB = (2130, 3170, 5700, 130)            # 一天：左右端、中线 y、高
BUSY = [(2130, 2330), (2420, 2700), (2780, 2980), (3060, 3170)]
GAPS = [(2330, 2420), (2700, 2780), (2980, 3060)]
scene("新手别先选", "书中观点 · 见缝插针", (2650, 5900, 0.85))
T("④ 见缝插针", 2650, 5470, 80, BLUE, k0=0, sfx="pop")


def _busy(c, k, t):
    for x0, x1 in BUSY:
        c.drawRect(skia.Rect.MakeLTRB(x0 + 6, DB[2] - DB[3] / 2 + 6, x0 + 6 + (x1 - x0 - 12) * k, DB[2] + DB[3] / 2 - 6),
                   K.paint(GREY, 0.8))
    return None


L(join(rect((DB[0] + DB[1]) / 2, DB[2], DB[1] - DB[0], DB[3], 8),
       *[P((x, DB[2] - DB[3] / 2), (x, DB[2] + DB[3] / 2)) for g in GAPS for x in g]), 1, 1.9, BLACK, 7,
  sfx="wood_high")
C(1.9, 2.3, _busy)


def _gap_fn(x0, x1):
    def fn(c, k, t):
        f = ease_out(k)
        w, h = (x1 - x0 - 16) * f, (DB[3] - 16) * f
        c.drawRect(skia.Rect.MakeXYWH((x0 + x1) / 2 - w / 2, DB[2] - h / 2, w, h), K.paint(BLUE, 0.9))
        return None

    return fn


C(2, 2.4, _gap_fn(*GAPS[0]), sfx="pop")
C(3, 3.4, _gap_fn(*GAPS[1]), sfx="pop")
C(3.5, 3.9, _gap_fn(*GAPS[2]))
C(4, 6.0, red_dot([(4, sum(GAPS[0]) / 2, DB[2] - 140), (5, sum(GAPS[1]) / 2, DB[2] - 140),
                   (6, sum(GAPS[2]) / 2, DB[2] - 140)], "9"), sfx="ding")
L(stick(2320, 6230, 0.65, "shrug"), 5, 5.8, BLACK, 9, sfx="wood_low")
T("艾萨克森", 2320, 6295, 52, k0=5.8, k1=6.8)
T("新手别先选", 2870, 6040, 72, RED, k0=6, sfx="rim")
L(underline(2660, 3080, 6100), 7.3, 7.9, RED, 8)

# ---------------------------------------------------------------- 对一下（场景 10，回到区块 A）

scene("对一下", "自测 · 对一下", (1440, 1250, 0.6))
for n, y in enumerate(ROWS):
    L(arrow((BX + 70, y), (SX0 - 25, y), 0.0, 30), n, n + 0.8, GREEN, 8, sfx="wood_high")
L(oval(SCX, ROWS[2], 780, 200), 4, 4.9, RED, 9, sfx="ding")
T("勾哪条，看哪种", 1440, 1950, 76, k0=6, sfx="pop")

# ---------------------------------------------------------------- 打工人：每天定时（场景 11–12，区块 D）

TT = (760, 130, 2720, 3400)             # 课表：左端、列宽、上、下（5 列）
scene("每天一小块", "做法 · 每天定时", (950, 3000, 0.85))
L(badge_stick(520, 3390, 0.85), 0, 0.9, BLACK, 10, sfx="wood_high")
T("小周", 520, 3465, 54, k0=1, sfx="pop")
tx, tw, ty0, ty1 = TT
L(join(rect(tx + tw * 2.5, (ty0 + ty1) / 2, tw * 5, ty1 - ty0, 10),
       *[P((tx + tw * i, ty0), (tx + tw * i, ty1)) for i in range(1, 5)],
       P((tx, ty0 + 340), (tx + tw * 5, ty0 + 340))), 2, 2.9, BLACK, 7, sfx="wood_low")


def _mornings(c, k, t):
    for d in range(5):
        f = clamp01(k * 5 - d)
        if f <= 0:
            break
        f = ease_out(f)
        c.drawRect(skia.Rect.MakeXYWH(tx + tw * d + 12, ty0 + 14, tw - 24, 150 * f), K.paint(BLUE, 0.88))
    return None


C(3, 4.6, _mornings, sfx="pop")
H(4, "pop")
T("每天9点，先干难活", 1000, 2580, 60, k0=5, sfx="pop")
C(7, 7.5, red_dot([(7, tx + tw * 3, ty0 + 520)], "9"), sfx="ding")

RX0, RW, RY = 2400, 120, 3000           # 一排 7 天
scene("先连七天", "做法 · 先连七天", (2650, 3000, 0.85))
L(badge_stick(2170, 3400, 0.8, "point"), 0, 0.9, BLACK, 10, sfx="wood_high")
L(join(rect(RX0 + RW * 3.5, RY, RW * 7, RW, 8), *[P((RX0 + RW * i, RY - RW / 2), (RX0 + RW * i, RY + RW / 2))
                                                   for i in range(1, 7)]), 1, 1.9, BLACK, 7, sfx="wood_low")
for d in range(7):
    L(cross(RX0 + RW * d + RW / 2, RY, 32), 2 + d * 0.5, 2.4 + d * 0.5, RED, 9,
      sfx="wood_high" if d % 2 == 0 else None)
L(chain(RX0 + RW / 2, RX0 + RW * 6.5, RY + 110, RW), 6, 6.8, BLUE, 7, sfx="ding")
T("先连7天", RX0 + RW * 3.5, 2700, 84, RED, k0=7, sfx="pop")

# ---------------------------------------------------------------- 拉远：清单 + 四条日历（场景 13）

scene("挑一种", "挑一种", (1504, 1250, 0.45))
H(0, "shaker", 0.6)
T("挑一种，先试试", 1500, 2180, 100, RED, k0=1, sfx="pop")
C(3, 3.5, red_dot([(3, 2330, 2170)], "9", r=70), sfx="ding")
L(underline(1150, 1850, 2255), 4, 4.8, RED, 9, sfx="wood_high")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FULL = (1800, 4100, 0.12)
CMT = (1800, 7400, 0.8)
J_END = scene("评论区聊聊", "评论区见", FULL, bars=4)
b.move(J_END, 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你打了几个勾？", 1800, 7320, 80, RED, k0=6, k1=7.75, sfx="pop")
C(8, 8.5, red_dot([(8, 2280, 7300)], "99+", r=60), sfx="ding")
T("下一讲：一坐下就想摸手机，怎么办？", 1800, 7490, 50, k0=9, sfx="wood_high")
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "style", "选对专注法", "没有整块时间，还能专注吗？", ACC, b.shots,
                 [f"{BOOK}准则1“工作要深入”·“选定你的深度哲学”（转述）",
                  "中译本：宋伟译，江西人民出版社 · 后浪 2017；民主与建设出版社 · 后浪 2023"],
                 "没有整块时间|还能【专注】吗", SQUARE_SHOT,
                 ["书中观点均为转述：准则1“工作要深入”的“选定你的深度哲学”一节给出四种安排专注时间的办法——"
                  "禁欲式（几乎断掉浅事，例：计算机科学家高德纳不用电子邮件）、双峰式（一段时间全力专注、其余时间照常，"
                  "例：荣格的湖边石塔、亚当·格兰特把教学集中在一个学期）、节奏式（每天固定时段，例：日历上每天打叉、"
                  "别让链条断的“链条法”）、记者式（一有空档就切进去专注，例：沃尔特·艾萨克森；书里说这种最难，新手别先选）。"
                  "上屏用白话名“断联 / 分段 / 每天定时 / 见缝插针”，书里的原名只写在这里；不是逐字引文。",
                  "四道自测题（能整周断联吗 / 一年有淡季吗 / 每天有固定空档吗 / 说专注就专注吗）及其与四种安排法的对应，"
                  "为据书中思路整理，书里没有这份测验；示例里的勾和叉为示意。",
                  "四条日历条（全蓝 / 半蓝 / 每天一块 / 碎块）、石塔、一年 12 格、日历打叉、碎片空档图均为通俗化示意，"
                  "不是数据；书中人物只画火柴人 + 名牌，不画肖像。",
                  "“打工人多半适合每天定时”、小周每天 9 点先干难活、“先连 7 天”为据书中思路整理的建议与示意，"
                  "时间和天数不是书中数据。"],
                 tags="#时间管理")
    return b.attach(ep)
