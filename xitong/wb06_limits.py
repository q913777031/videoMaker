"""06 增长的极限（白板手绘版）：业绩为什么涨着涨着就不动了？

叙事：打工人切身问题开局（业绩一路涨、领导喊明年翻倍、加人加班加钱，曲线还是平了）→ 书中观点（油田越挖越难、
渔场船多鱼少；赚了钱再投进去的增强回路，碰上资源变少的调节回路，曲线先陡后平；卡点不止一个，补上一块下一块又卡）→
身边的例子（订单猛增客服接不过来、奶茶店后厨人手不够、孩子补课越报越多觉不够睡、健身天天加练肌肉不长）→
具体做法（画出增长曲线 / 列清单找最先用完的 / 钱先补那一块 / 补完盯下一块，每月问一句）→ 评论区互动。
书中观点为转述（Meadows, Thinking in Systems, 2008；中译本《系统之美》，邱昭良译，浙江人民出版社 2012）：
有限环境里靠增强回路推动的增长迟早碰上调节回路，曲线由陡变平；书中用开采不可再生资源（油田）与捕捞可再生资源（渔场）
举例；限制增长的因素不止一个，补上一个，下一个就成了新的限制，要不断找出当下真正的限制因素。
木桶短板为示意比喻；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, clock, cross, doc, face,
                               hands_at, join, node, rect, scribble, stick, underline)

from .common import BOOK, episode

ACC = "#5E8A4A"
SQUARE_SHOT = 14

b = Board(size=(3600, 10900))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


# ---------------------------------------------------------------- 本讲画法

def ring(x, y, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry))
    return p


def axes(x0, y0, w, h) -> skia.Path:
    """坐标轴：(x0, y0) 为原点，向右 w、向上 h。"""
    return join(arrow((x0, y0), (x0, y0 - h), 0, 30), arrow((x0, y0), (x0 + w, y0), 0, 30))


def logistic(u):
    lo, hi = 1 / (1 + math.exp(5)), 1 / (1 + math.exp(-5))
    return (1 / (1 + math.exp(-10 * (u - 0.5))) - lo) / (hi - lo)


def bell(u):
    return math.sin(math.pi * u) ** 1.6


def fcurve(x0, y0, w, h, f, u0=0.0, u1=1.0, n=60) -> skia.Path:
    pts = [(x0 + w * (u0 + (u1 - u0) * i / n), y0 - h * f(u0 + (u1 - u0) * i / n)) for i in range(n + 1)]
    return P(*pts)


def rock(x, y, r) -> skia.Path:
    """大石头：(x, y) 为中心。"""
    pts = []
    for i in range(11):
        a = i / 11 * 2 * math.pi
        rr = r * (1 + 0.12 * math.sin(i * 2.3))
        pts.append((x + math.cos(a) * rr * 1.15, y + math.sin(a) * rr * 0.9))
    return P(*pts, close=True)


def derrick(x, y, h=560) -> skia.Path:
    """油井架：(x, y) 为底边中点。"""
    w = h * 0.55
    parts = [P((x - w / 2, y), (x, y - h), (x + w / 2, y))]
    for f in (0.3, 0.55, 0.78):
        yy = y - h * (1 - f)
        parts.append(P((x - w / 2 * f, yy), (x + w / 2 * f, yy)))
    parts.append(P((x - w / 2 * 0.3, y - h * 0.7), (x + w / 2 * 0.55, y - h * 0.45)))
    parts.append(P((x - w / 2 * 0.55, y - h * 0.45), (x + w / 2 * 0.78, y - h * 0.22)))
    parts.append(P((x - w * 0.9, y), (x + w * 0.9, y)))
    return join(*parts)


def fish(x, y, s=1.0, d=1) -> skia.Path:
    p = ring(x, y, 55 * s, 28 * s)
    p.addPath(P((x - d * 50 * s, y), (x - d * 90 * s, y - 28 * s), (x - d * 90 * s, y + 28 * s), close=True))
    p.addCircle(x + d * 28 * s, y - 6 * s, 5 * s)
    return p


def boat(x, y, s=1.0) -> skia.Path:
    """小渔船：(x, y) 为吃水线中点。"""
    return join(P((x - 130 * s, y - 50 * s), (x + 130 * s, y - 50 * s), (x + 85 * s, y + 10 * s),
                  (x - 85 * s, y + 10 * s), close=True),
                P((x, y - 50 * s), (x, y - 230 * s)), P((x, y - 220 * s), (x + 90 * s, y - 90 * s), (x, y - 90 * s)))


def shop(x, y, w=440, h=400) -> skia.Path:
    """小店门面：(x, y) 为底边中点，带遮阳棚。"""
    top = y - h
    parts = [P((x - w / 2, y), (x - w / 2, top), (x + w / 2, top), (x + w / 2, y)),
             P((x - w / 2 - 30, top), (x + w / 2 + 30, top))]
    aw = skia.Path()
    aw.moveTo(x - w / 2 - 30, top)
    n = 6
    for i in range(n):
        x0 = x - w / 2 - 30 + (w + 60) * i / n
        aw.quadTo(x0 + (w + 60) / n / 2, top + 70, x0 + (w + 60) / n, top)
    parts.append(aw)
    parts.append(rect(x - w / 4, y - h * 0.45, w * 0.32, h * 0.32, 8))
    parts.append(P((x + w / 8, y), (x + w / 8, y - h * 0.55), (x + w * 0.38, y - h * 0.55), (x + w * 0.38, y)))
    return join(*parts)


def barbell(x, y, w=300) -> skia.Path:
    return join(P((x - w / 2, y), (x + w / 2, y)), rect(x - w / 2 + 20, y, 34, 120, 8), rect(x + w / 2 - 20, y, 34, 120, 8))


def calendar(x, y, w=240, h=210) -> skia.Path:
    parts = [rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 55), (x + w / 2, y - h / 2 + 55)),
             P((x - w / 4, y - h / 2 - 20), (x - w / 4, y - h / 2 + 20)),
             P((x + w / 4, y - h / 2 - 20), (x + w / 4, y - h / 2 + 20))]
    for r in range(2):
        for cc in range(4):
            parts.append(rect(x - w / 2 + 35 + cc * (w - 70) / 3, y - h / 2 + 95 + r * 60, 22, 22, 4))
    return join(*parts)


def sweat(x, y) -> skia.Path:
    return join(P((x, y), (x + 30, y - 40)), P((x + 25, y + 25), (x + 65, y - 5)), P((x + 35, y + 60), (x + 80, y + 45)))


# ---------------------------------------------------------------- 开局：业绩涨不动了（镜头 1–6）

CH = (500, 1300, 1000, 700)          # 业绩曲线：原点 x、原点 y、宽、高
b.shot("业绩一路往上涨", "灵魂拷问", view=(1000, 900, 0.85))
L(axes(*CH), 0, 0.8, sfx="wood_high")
T("业绩", 600, 560, 56, k0=0.6)
T("时间", 1430, 1370, 50, k0=0.8)
L(fcurve(*CH, logistic, 0, 0.5), 1, 2.6, BLUE, 12, sfx="shaker")
T("月月涨", 820, 820, 70, RED, k0=3, sfx="pop")

b.shot("领导说明年翻倍", "灵魂拷问", view=(2700, 820, 0.85))
L(stick(2400, 1200, 0.9, "point", tie=True), 0, 0.6, sfx="wood_high")
L(face(2400, 1200, 0.9, "smile"), 0.6, 0.75)
L(join(rect(2880, 640, 560, 250, 40), P((2700, 765), (2600, 850), (2780, 765))), 1, 1.6, sfx="pop")
T("明年翻倍！", 2880, 640, 84, RED, k0=2, k1=2.6, sfx="kick")
b.shots[-1].shake.append(2)

b.shot("加人加班加预算", "灵魂拷问", view=(2700, 1560, 0.85))
L(join(stick(2220, 1720, 0.5), stick(2360, 1720, 0.5)), 0, 0.6, sfx="pop")
L(join(clock(2720, 1580, 110), hands_at(2720, 1580, 110, 10, 0)), 1, 1.6, sfx="pop")
T("¥", 3140, 1580, 190, GREEN, k0=2, k1=2.3, sfx="pop")
for n, (w, x) in enumerate((("加人", 2290), ("加班", 2720), ("加钱", 3140))):
    T(w, x, 1830, 60, RED, k0=n + 0.5, k1=n + 0.9)
H(3, "wood_high")

b.shot("曲线却变平了", "灵魂拷问", view=(1000, 900, 0.85))
L(fcurve(*CH, logistic, 0.5, 1), 0, 1.4, RED, 12, sfx="shaker")
L(ring(1360, 640, 190, 90), 2, 2.4, RED, 8, sfx="rim")
T("？", 1360, 470, 110, RED, k0=3, sfx="pop")

b.shot("越使劲越推不动", "灵魂拷问", view=(1000, 1880, 0.85))
L(join(P((420, 2160), (1580, 2160)), rock(1220, 1900, 250)), 0, 0.9, sfx="wood_low")
L(stick(860, 2160, 0.85, "point"), 1, 1.6, BLUE, sfx="pop")
T("瓶颈", 1220, 1900, 96, RED, k0=2, k1=2.4, sfx="kick")
L(sweat(900, 1790), 3, 3.4, BLUE, 6, sfx="shaker")
b.shots[-1].shake.append(2)

b.shot("卡在哪了？", "灵魂拷问", view=(1800, 1320, 0.42), flashes=[0])
T("？", 1800, 1330, 320, RED, k0=0, k1=0.5, sfx="kick")
T("卡在哪了", 1800, 2350, 120, k0=1, k1=1.8, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "系统之美", view=(1000, 2850, 0.9))
L(book(700, 2850, 420, 280), 0, 1.0, sfx="wood_low")
T("系统之美", 700, 2610, 80, GREEN, k0=1, sfx="pop")
T("德内拉 · 梅多斯", 700, 3080, 50, k0=2, sfx="pop")
T("增长的极限", 1300, 2850, 70, RED, k0=3, k1=3.7, sfx="pop")

OIL = (950, 4050, 600, 520)
b.shot("书里讲了油田", "书中例子 · 油田", view=(1000, 3660, 0.85))
L(derrick(560, 4050, 560), 0, 1.0, sfx="wood_low")
T("油田", 560, 3380, 70, k0=1, sfx="pop")
L(axes(*OIL), 2, 2.5, BLACK, 8, sfx="wood_high")
T("产量", 1040, 3500, 50, k0=2.4)
L(fcurve(*OIL, bell, 0, 0.5), 3, 3.9, BLUE, 12, sfx="shaker")

b.shot("油越挖越难挖", "书中例子 · 油田", view=(1000, 3660, 0.85), shake=[0], flashes=[0])
L(fcurve(*OIL, bell, 0.5, 1), 0, 0.5, RED, 14, sfx="kick")
L(arrow((1420, 3600), (1420, 3960), 0, 50), 0.3, 0.6, RED, 12)
T("越挖越少", 1250, 4140, 64, RED, k0=1, sfx="tom")
L(cross(560, 3700, 70), 2, 2.3, RED, 10, sfx="rim")
H(3, "tom", 0.6)

FISH = [(2250, 2960, 1), (2470, 3080, -1), (2700, 2950, 1), (2930, 3090, 1), (3150, 2970, -1), (2580, 3220, 1)]
b.shot("还有个渔场", "书中例子 · 渔场", view=(2700, 2880, 0.85))
L(underline(2080, 3320, 2790, 18, 80), 0, 0.8, BLUE, 8, sfx="wood_high")
T("渔场", 2700, 2420, 70, k0=1, sfx="pop")
L(boat(2350, 2790, 0.8), 1.2, 1.8)
for n, (x, y, d) in enumerate(FISH):
    L(fish(x, y, 0.9, d), 2 + n * 0.25, 2.25 + n * 0.25, BLUE, 7, sfx="pop" if n == 0 else None)
H(3, "shaker")

b.shot("船越来越多", "书中例子 · 渔场", view=(2700, 2880, 0.85))
for n, x in enumerate((2650, 2900, 3150)):
    L(boat(x, 2790, 0.8), n, n + 0.6, sfx="pop")
H(3, "wood_high")

b.shot("鱼越捞越少", "书中例子 · 渔场", view=(2700, 2880, 0.85))
for n in range(3):
    for m in range(2):
        x, y, _ = FISH[n * 2 + m]
        L(cross(x, y, 50), n + m * 0.3, n + m * 0.3 + 0.25, RED, 8, sfx="rim" if m == 0 else None)
T("鱼少了", 3150, 3230, 64, RED, k0=3, sfx="pop")

LOOP_Y = 3700
b.shot("赚了钱再投进去", "书中观点 · 增强回路", view=(2700, 3780, 0.85))
L(join(node(2300, LOOP_Y, 85), node(2700, LOOP_Y, 85)), 0, 0.6, sfx="pop")
T("赚钱", 2300, LOOP_Y, 50, k0=0.5, k1=0.8)
T("规模", 2700, LOOP_Y, 50, k0=0.7, k1=1.0)
L(arrow((2360, LOOP_Y - 70), (2640, LOOP_Y - 70), -0.35, 34), 1, 1.5, GREEN, 8, sfx="wood_high")
L(arrow((2640, LOOP_Y + 70), (2360, LOOP_Y + 70), -0.35, 34), 2, 2.5, GREEN, 8, sfx="wood_high")
T("增强", 2500, LOOP_Y, 46, GREEN, k0=3, sfx="pop")
T("越转越快", 2420, 3970, 56, GREEN, k0=3.2, k1=3.8)

b.shot("资源少了就刹车", "书中观点 · 调节回路", view=(2700, 3780, 0.85), shake=[0])
L(node(3100, LOOP_Y, 85), 0, 0.4, RED, 10, sfx="kick")
T("资源", 3100, LOOP_Y, 50, RED, k0=0.4, k1=0.7)
L(arrow((2760, LOOP_Y - 70), (3040, LOOP_Y - 70), -0.35, 34), 1, 1.5, RED, 8, sfx="rim")
L(arrow((3040, LOOP_Y + 70), (2760, LOOP_Y + 70), -0.35, 34), 2, 2.5, RED, 8, sfx="rim")
T("刹车", 2900, LOOP_Y, 46, RED, k0=3, sfx="pop")
T("越踩越紧", 2980, 3970, 56, RED, k0=3.2, k1=3.8)

SC = (650, 5150, 850, 650)
b.shot("曲线先陡后平", "书中观点 · 先陡后平", view=(1000, 4800, 0.85))
L(axes(*SC), 0, 0.6, sfx="wood_high")
L(stick(430, 5150, 0.75, "point"), 0.5, 1.0)
L(fcurve(*SC, logistic), 1, 2.4, BLUE, 12, sfx="shaker")
L(P((680, 4480), (1500, 4480)), 2, 2.4, RED, 8, sfx="rim")
T("上限", 1440, 4420, 50, RED, k0=2.4)
T("增强", 820, 4850, 56, GREEN, k0=3, sfx="pop")
T("刹车", 1400, 4620, 56, RED, k0=3.2, k1=3.6)

STAVES = [("人手", 2340, 0.8), ("资金", 2580, 0.9), ("客户", 2820, 0.45), ("产能", 3060, 0.68)]
SB, SH = 5150, 750


def top_of(v):
    return SB - SH * v


b.shot("卡点不止一个", "书中观点 · 限制因素", view=(2700, 4800, 0.85))
for n, (w, x, v) in enumerate(STAVES):
    L(rect(x, SB - SH * v / 2, 220, SH * v, 10), n * 0.3, n * 0.3 + 0.3, sfx="wood_high" if n == 0 else None)
L(P((2210, SB - 120), (3190, SB - 120)), 1.3, 1.6, BLACK, 7)
H(1, "wood_high", 0.5)
for n, (w, x, v) in enumerate(STAVES):
    T(w, x, SB + 60, 50, k0=2 + n * 0.2, k1=2.3 + n * 0.2, sfx="pop" if n == 0 else None)
L(underline(2230, 3170, top_of(0.45) + 20, 12, 60), 3, 3.5, BLUE, 8, sfx="shaker")

b.shot("补上又卡下一块", "书中观点 · 限制会转移", view=(2700, 4800, 0.85))
L(rect(2820, (top_of(0.45) + top_of(0.95)) / 2, 220, top_of(0.45) - top_of(0.95), 10), 0, 0.5, BLUE, 10, sfx="kick")
L(underline(2230, 3170, top_of(0.68) + 20, 12, 60), 1, 1.5, BLUE, 8, sfx="ding")
L(ring(3060, top_of(0.68), 150, 70), 2, 2.4, RED, 8, sfx="rim")
T("新卡点", 3060, top_of(0.68) - 130, 60, RED, k0=3, sfx="pop")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 6100), (2650, 6100), (950, 7100), (2650, 7100)]
STUCK = [(1250, 6440), (2850, 6180), (820, 7470), (2880, 7470)]       # 各例子“卡在”字样的位置
b.shot("身边全是这种事", "身边的例子", view=(1800, 6560, 0.42))
T("身边的例子", 1800, 5530, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("新品订单猛增", "例子 · 订单猛增", view=(950, 6100, 0.85))
L(stick(560, 6460, 0.8, "hold"), 0, 0.6, sfx="wood_high")
for n in range(4):
    L(doc(1000 + n * 70, 6200 - n * 50), 1 + n * 0.2, 1.2 + n * 0.2, sfx="pop" if n == 0 else None)
T("订单 ×3", 950, 5770, 70, RED, k0=2, sfx="pop")
L(arrow((1450, 6250), (1450, 5850), 0, 40), 3, 3.4, RED, 10, sfx="wood_high")

b.shot("客服接不过来", "例子 · 订单猛增", view=(950, 6100, 0.85))
L(scribble(1150, 6050, 380, 300, 9), 0, 0.6, BLACK, 6, sfx="shaker")
L(face(560, 6460, 0.8, "sad"), 0.6, 0.8)
T("差评", 1250, 6300, 64, RED, k0=1, sfx="rim")
T("卡在：客服", *STUCK[0], 60, RED, k0=2, k1=2.7, sfx="tom")

b.shot("奶茶店排长队", "例子 · 奶茶店", view=(2650, 6100, 0.85))
L(shop(2350, 6450), 0, 0.9, sfx="wood_high")
T("奶茶", 2350, 5980, 60, k0=1, sfx="pop")
for n in range(5):
    L(stick(2700 + n * 120, 6450, 0.45), 2 + n * 0.25, 2.25 + n * 0.25, BLUE, 8, sfx="pop" if n == 0 else None)
H(3, "shaker")

b.shot("后厨就两个人", "例子 · 奶茶店", view=(2650, 6100, 0.85))
T("后厨 2 人", 2350, 5800, 64, RED, k0=0, sfx="pop")
L(clock(2950, 5880, 90), 1, 1.5, sfx="wood_low")
L(hands_at(2950, 5880, 90, 1, 40), 2, 2.2, RED, 9, sfx="rim")
T("等 40 分钟", 2950, 6050, 50, RED, k0=2.3)
T("卡在：人手", *STUCK[1], 56, RED, k0=3, k1=3.7, sfx="tom")

b.shot("孩子补课越报越多", "例子 · 补课", view=(950, 7100, 0.85))
L(stick(560, 7380, 0.65), 0, 0.5, sfx="wood_high")
L(face(560, 7380, 0.65, "flat"), 0.5, 0.6)
for n, w in enumerate(("数学", "英语", "作文", "编程")):
    y = 7360 - n * 100
    L(rect(1150, y, 380, 86, 10), 1 + n * 0.5, 1.2 + n * 0.5, sfx="pop" if n % 2 == 0 else None)
    T(w, 1150, y, 50, k0=1.2 + n * 0.5, k1=1.45 + n * 0.5)

b.shot("觉都睡不够了", "例子 · 补课", view=(950, 7100, 0.85))
L(clock(560, 6900, 90), 0, 0.5, sfx="wood_low")
L(hands_at(560, 6900, 90, 0, 0), 1, 1.2, RED, 9, sfx="rim")
T("分数没涨", 1150, 6800, 56, k0=2, sfx="pop")
T("卡在：睡觉", *STUCK[2], 56, RED, k0=3, k1=3.7, sfx="tom")

b.shot("健身天天加练", "例子 · 健身", view=(2650, 7100, 0.85))
L(stick(2330, 7480, 0.75, "up"), 0, 0.6, sfx="wood_high")
L(barbell(2330, 7190, 340), 1, 1.4, BLACK, 9, sfx="pop")
T("每天 2 小时", 2420, 6800, 56, k0=2, sfx="pop")
L(sweat(2380, 7250), 3, 3.4, BLUE, 6, sfx="shaker")

MC = (2770, 7330, 480, 380)
b.shot("练多了反而不长", "例子 · 健身", view=(2650, 7100, 0.85))
L(axes(*MC), 0, 0.5, BLACK, 7, sfx="wood_high")
L(fcurve(*MC, logistic), 0.5, 1.4, RED, 10)
T("肌肉", 2860, 6990, 46, k0=1, sfx="pop")
T("卡在：吃和睡", *STUCK[3], 56, RED, k0=2, k1=2.8, sfx="tom")
H(3, "rim", 0.6)

b.shot("每个都卡在一处", "身边的例子", view=(1800, 6560, 0.42))
for n, (x, y) in enumerate(STUCK):
    L(ring(x, y, 220, 70), n * 0.8, n * 0.8 + 0.4, RED, 9, sfx="rim" if n % 2 == 0 else None)
H(3, "ding")

b.shot("光踩油门没用", "身边的例子", view=(1800, 6800, 0.42), shake=[0])
T("猛加投入", 1800, 7720, 160, RED, k0=0, k1=0.6, sfx="kick")
L(cross(1800, 7720, 150), 1, 1.3, RED, 14, sfx="rim")
H(2, "wood_low")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 8650), (2650, 8650), (950, 9550), (2650, 9550)]
b.shot("涨不动了这样做", "具体做法", view=(1800, 9100, 0.42))
T("涨不动了，这样做", 1800, 8100, 110, k0=0, k1=1.6, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1500, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)
H(3, "wood_high", 0.5)

GC = (520, 8960, 820, 460)
b.shot("先画出增长曲线", "第一步 · 画曲线", view=(950, 8650, 0.85))
T("① 画曲线", 950, 8330, 76, BLUE, k0=0, sfx="pop")
L(axes(*GC), 1, 1.5, BLACK, 8, sfx="wood_high")
T("每月业绩", 640, 8470, 46, k0=1.4)
L(fcurve(*GC, logistic), 2, 3.4, BLUE, 10, sfx="shaker")

b.shot("看它变没变平", "第一步 · 画曲线", view=(950, 8650, 0.85))
L(ring(1200, 8540, 170, 80), 0, 0.4, RED, 8, sfx="rim")
T("变平了", 1200, 8690, 60, RED, k0=1, sfx="pop")
L(underline(1100, 1300, 8740), 2, 2.4, RED, 7, sfx="ding")

LIST = [("人手", 2300, 8560), ("钱", 2650, 8560), ("客户", 3000, 8560), ("机器", 2470, 8740), ("时间", 2830, 8740)]
b.shot("列出要用的东西", "第二步 · 列清单", view=(2650, 8650, 0.85))
T("② 列清单", 2650, 8330, 76, BLUE, k0=0, sfx="pop")
for n, (w, x, y) in enumerate(LIST):
    k = 1 + n * 0.45
    T(w, x, y, 60, k0=round(k) if n in (0, 3) else k, k1=(round(k) if n in (0, 3) else k) + 0.35,
      sfx="pop" if n in (0, 3) else None)
H(3, "wood_high", 0.5)

b.shot("哪样最先用完", "第二步 · 列清单", view=(2650, 8650, 0.85))
L(ring(2300, 8560, 110, 60), 0, 0.4, RED, 8, sfx="rim")
T("最先用完", 2300, 8930, 64, RED, k0=1, sfx="pop")
L(arrow((2190, 8870), (2220, 8630), 0, 30), 2, 2.4, RED, 7, sfx="ding")

b.shot("钱先花在这块", "第三步 · 先补它", view=(950, 9550, 0.85))
T("③ 先补它", 950, 9230, 76, BLUE, k0=0, sfx="pop")
T("¥", 560, 9520, 160, GREEN, k0=1, k1=1.3, sfx="pop")
L(arrow((680, 9520), (900, 9520), 0, 34), 1.5, 1.8, GREEN, 8)
T("人手", 1050, 9520, 70, RED, k0=2, sfx="pop")
H(3, "ding", 0.6)

b.shot("先加客服再拉客", "第三步 · 先补它", view=(950, 9550, 0.85))
for n in range(3):
    L(stick(1300 + n * 110, 9700, 0.4), n * 0.3, n * 0.3 + 0.3, BLUE, 8, sfx="pop" if n == 0 else None)
T("客服 +3", 1350, 9380, 56, BLUE, k0=1, sfx="pop")
L(check(1510, 9380, 36), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("广告先停一停", "第三步 · 先补它", view=(950, 9550, 0.85))
T("广告", 620, 9760, 64, k0=0, sfx="pop")
L(P((540, 9760), (700, 9760)), 1, 1.3, RED, 10, sfx="rim")
T("先停", 860, 9760, 64, RED, k0=2, sfx="pop")

b.shot("补完再找下一块", "第四步 · 盯下一块", view=(2650, 9550, 0.85))
T("④ 盯下一块", 2650, 9230, 76, BLUE, k0=0, sfx="pop")
T("客服", 2300, 9420, 64, k0=1, sfx="pop")
L(check(2420, 9415, 36), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("下一块是机器", "第四步 · 盯下一块", view=(2650, 9550, 0.85))
L(arrow((2490, 9420), (2800, 9420), -0.15, 34), 0, 0.5, BLACK, 8, sfx="wood_high")
T("机器？", 2950, 9420, 64, RED, k0=1, sfx="pop")
L(ring(2950, 9420, 130, 60), 2, 2.4, RED, 7, sfx="rim")

b.shot("每月问一句", "第四步 · 盯下一块", view=(2650, 9600, 0.85))
L(calendar(2330, 9740, 220, 190), 0, 0.8, sfx="wood_high")
T("现在卡在哪？", 2860, 9740, 60, RED, k0=1, sfx="pop")
L(underline(2680, 3050, 9800), 2, 2.5, RED, 7, sfx="ding")

b.shot("一次只补一块", "一句话", view=(1800, 10150, 0.62))
T("一次只补一块", 1800, 10130, 100, RED, k0=0, k1=1.2, sfx="pop")
L(underline(1500, 2100, 10210), 2, 2.5, RED, 8, sfx="ding")

b.shot("找对卡点再使劲", "一句话", view=(1800, 5600, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 10550, 0.8))
T("你被哪块卡住过？", 1800, 10470, 80, RED, k0=0.5, k1=1.8)
T("下一讲：公司冰箱为什么总是乱糟糟？", 1800, 10630, 50, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "limits", "增长的极限", "业绩为什么涨着涨着就不动了？", ACC, b.shots,
                 [f"{BOOK}（转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                 "业绩涨着涨着|就【不动了】", 14,
                 ["书中观点均为转述，不是原话：在有限的环境里，靠增强回路推动的增长迟早会碰上调节回路，曲线由陡变平；"
                  "书中用开采不可再生资源（油田）与捕捞可再生资源（渔场）举例；限制增长的因素不止一个，补上一个，"
                  "下一个就成了新的限制，所以要不断找出当下真正的限制因素。出处：Donella H. Meadows, Thinking in Systems: "
                  "A Primer (2008)，中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                  "木桶短板为示意比喻；各曲线形状、板高、船数、鱼数均为示意。订单猛增客服接不过来、奶茶店后厨人手不够、"
                  "孩子补课越报越多、健身加练不长肌肉均为现实场景示意，不指向任何具体公司或个人；"
                  "四步做法（画曲线、列清单、先补最先用完的、每月盯下一块）为据书中思路整理的建议。"],
                 tags="#增长 #瓶颈 #职场")
    return b.attach(ep)
