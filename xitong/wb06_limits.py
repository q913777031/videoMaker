"""06 增长的极限（白板手绘版）：业绩为什么涨着涨着就不动了？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
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
SQUARE_SHOT = 7

b = Board(size=(3600, 13200))


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


# ---------------------------------------------------------------- 开局：业绩涨不动了（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


CH = (300, 1300, 950, 700)          # 业绩曲线：原点 x、原点 y、宽、高
scene("业绩涨，还要翻倍", "灵魂拷问", (1000, 1000, 0.62))
L(axes(*CH), 0, 0.8, sfx="wood_high")
T("业绩", 420, 560, 56, k0=0.6)
T("时间", 1200, 1370, 50, k0=0.8)
L(fcurve(*CH, logistic, 0, 0.5), 1, 2.2, BLUE, 12, sfx="shaker")
T("月月涨", 620, 820, 66, RED, k0=2.3, k1=2.8)
L(stick(1600, 1320, 0.8, "point", tie=True), 3, 3.6, sfx="wood_high")
L(face(1600, 1320, 0.8, "smile"), 3.6, 3.75)
L(join(rect(1580, 600, 460, 200, 40), P((1540, 700), (1560, 860), (1620, 700))), 4, 4.5, sfx="pop")
T("明年翻倍！", 1580, 600, 72, RED, k0=5, k1=5.8, sfx="kick")

scene("加人加钱，曲线平了", "灵魂拷问", (1000, 1250, 0.62), shake=[5])
L(join(stick(380, 1880, 0.5), stick(520, 1880, 0.5)), 0, 0.6, sfx="pop")
T("加人", 450, 1960, 56, RED, k0=0.6, k1=0.95)
L(join(clock(900, 1740, 100), hands_at(900, 1740, 100, 10, 0)), 1, 1.6, sfx="wood_high")
T("加班", 900, 1960, 56, RED, k0=1.6, k1=1.95)
T("¥", 1350, 1740, 170, GREEN, k0=2, k1=2.3, sfx="pop")
T("加钱", 1350, 1960, 56, RED, k0=2.4, k1=2.75)
L(fcurve(*CH, logistic, 0.5, 1), 3, 4.2, RED, 12, sfx="shaker")
L(ring(1100, 640, 170, 85), 5, 5.4, RED, 8, sfx="rim")
T("？", 1150, 830, 100, RED, k0=5.4, k1=5.8)

scene("越使劲越推不动", "灵魂拷问", (2700, 1250, 0.62), shake=[2], flashes=[4])
L(join(P((2000, 1700), (3420, 1700)), rock(2980, 1450, 240)), 0, 0.9, sfx="wood_low")
L(stick(2560, 1700, 0.85, "point"), 1, 1.6, BLUE, sfx="pop")
T("瓶颈", 2980, 1450, 92, RED, k0=2, k1=2.4, sfx="kick")
L(sweat(2600, 1330), 3, 3.4, BLUE, 6, sfx="shaker")
T("卡在哪了？", 2700, 850, 120, RED, k0=4, k1=5.4, sfx="tom")
H(5, "ding", 0.6)

# ---------------------------------------------------------------- 书中观点（场景 4–9）

scene("书里讲了个油田", "系统之美 · 书中例子", (1000, 3100, 0.74))
L(book(600, 2750, 420, 280), 0, 1.0, sfx="wood_low")
T("系统之美", 600, 2510, 80, GREEN, k0=1, sfx="pop")
T("德内拉 · 梅多斯", 600, 2980, 46, k0=2, k1=3, sfx="pop")
L(derrick(1350, 3250, 560), 3, 4, sfx="wood_low")
T("油田", 1350, 3340, 66, k0=5, sfx="pop")

OIL = (350, 4100, 1100, 550)
scene("油越挖越少", "书中例子 · 油田", (1000, 3380, 0.62), shake=[0], flashes=[0])
L(fcurve(*OIL, bell, 0, 0.5), 0, 1, BLUE, 12, sfx="kick")
L(axes(*OIL), 0, 0.4, BLACK, 8)
T("产量", 470, 3520, 50, k0=1, k1=1.4)
L(fcurve(*OIL, bell, 0.5, 1), 2, 3, RED, 14, sfx="tom")
L(arrow((1560, 3650), (1560, 3980), 0, 50), 3, 3.4, RED, 12, sfx="rim")
T("越挖越少", 1250, 3460, 60, RED, k0=4, k1=4.8, sfx="pop")
L(cross(1350, 2950, 70), 5, 5.3, RED, 10, sfx="rim")

FISH = [(2250, 2810, 1), (2470, 2930, -1), (2700, 2800, 1), (2930, 2940, 1), (3150, 2820, -1), (2580, 3070, 1)]
scene("船越多，鱼越少", "书中例子 · 渔场", (2700, 2700, 0.74))
L(underline(2080, 3320, 2640, 18, 80), 0, 0.8, BLUE, 8, sfx="wood_high")
T("渔场", 2300, 2280, 70, k0=0.8, k1=1.0)
L(boat(2250, 2640, 0.7), 1, 1.5, sfx="pop")
for n, (x, y, d) in enumerate(FISH):
    L(fish(x, y, 0.9, d), 2 + n * 0.2, 2.2 + n * 0.2, BLUE, 7, sfx="pop" if n == 0 else None)
for n, x in enumerate((2550, 2850, 3150)):
    L(boat(x, 2640, 0.7), 3 + n * 0.3, 3.4 + n * 0.3, sfx="wood_high" if n == 0 else None)
for n in range(4):
    x, y, _ = FISH[n + 1]
    L(cross(x, y, 50), 4 + n * 0.2, 4.2 + n * 0.2, RED, 8, sfx="rim" if n == 0 else None)
T("鱼少了", 3100, 2280, 70, RED, k0=5, sfx="pop")

LOOP_Y = 3750
scene("越赚越投，碰上刹车", "书中观点 · 两个回路", (2700, 3750, 0.74), shake=[3])
L(join(node(2300, LOOP_Y, 85), node(2700, LOOP_Y, 85)), 0, 0.6, sfx="pop")
T("赚钱", 2300, LOOP_Y, 50, k0=0.5, k1=0.8)
T("规模", 2700, LOOP_Y, 50, k0=0.7, k1=1.0)
L(arrow((2360, LOOP_Y - 70), (2640, LOOP_Y - 70), -0.35, 34), 1, 1.4, GREEN, 8, sfx="wood_high")
L(arrow((2640, LOOP_Y + 70), (2360, LOOP_Y + 70), -0.35, 34), 1.4, 1.8, GREEN, 8)
T("增强", 2500, LOOP_Y - 200, 56, GREEN, k0=2, sfx="pop")
L(node(3100, LOOP_Y, 85), 3, 3.4, RED, 10, sfx="kick")
T("资源", 3100, LOOP_Y, 50, RED, k0=3.4, k1=3.7)
L(arrow((2760, LOOP_Y - 70), (3040, LOOP_Y - 70), -0.35, 34), 4, 4.4, RED, 8, sfx="rim")
L(arrow((3040, LOOP_Y + 70), (2760, LOOP_Y + 70), -0.35, 34), 4.4, 4.8, RED, 8)
T("刹车", 2900, LOOP_Y - 200, 56, RED, k0=5, sfx="pop")

SC = (650, 5150, 850, 650)
scene("曲线先陡后平", "书中观点 · 先陡后平", (1000, 4800, 0.85))
L(axes(*SC), 0, 0.6, sfx="wood_high")
L(stick(430, 5150, 0.75, "point"), 0.5, 1.0)
L(fcurve(*SC, logistic), 1, 2.4, BLUE, 12, sfx="shaker")
L(P((680, 4480), (1500, 4480)), 3, 3.4, RED, 8, sfx="rim")
T("上限", 1440, 4420, 50, RED, k0=3.4, k1=3.8)
T("增强", 820, 4850, 56, GREEN, k0=4, sfx="pop")
T("刹车", 1400, 4620, 56, RED, k0=5, sfx="pop")

STAVES = [("人手", 2340, 0.8), ("资金", 2580, 0.9), ("客户", 2820, 0.45), ("产能", 3060, 0.68)]
SB, SH = 5150, 750


def top_of(v):
    return SB - SH * v


scene("补上一块，又卡一块", "书中观点 · 限制会转移", (2700, 4800, 0.85))
for n, (w, x, v) in enumerate(STAVES):
    L(rect(x, SB - SH * v / 2, 220, SH * v, 10), n * 0.25, n * 0.25 + 0.25, sfx="wood_high" if n == 0 else None)
for n, (w, x, v) in enumerate(STAVES):
    T(w, x, SB + 60, 50, k0=1 + n * 0.2, k1=1.3 + n * 0.2, sfx="pop" if n == 0 else None)
L(ring(2820, top_of(0.45), 150, 70), 2, 2.4, RED, 8, sfx="rim")
L(rect(2820, (top_of(0.45) + top_of(0.95)) / 2, 220, top_of(0.45) - top_of(0.95), 10), 3, 3.5, BLUE, 10, sfx="kick")
L(ring(3060, top_of(0.68), 150, 70), 4, 4.4, RED, 8, sfx="rim")
T("新卡点", 3060, top_of(0.68) - 130, 60, RED, k0=5, sfx="pop")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

DY = 900                 # 身边的例子整体下移，和上一块拉开距离
CARDS = [(950, 6100 + DY), (2650, 6100 + DY), (950, 7450 + DY), (2650, 7450 + DY)]
STUCK = [(1000, 6440 + DY), (2850, 6180 + DY), (820, 7820 + DY), (3010, 7120 + DY)]       # 各例子“卡在”字样的位置
scene("身边全是这种事", "身边的例子", (1800, 7800, 0.34))
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1450, 900, 40), n * 1.2, n * 1.2 + 0.6, GREEN, 8, sfx=("wood_high", "pop")[n % 2] if n < 3 else None)
T("？", 1800, 7675, 200, RED, k0=4, k1=4.5, sfx="kick")

scene("订单猛增，客服扛不住", "例子 · 订单猛增", (950, 7000, 0.85))
L(stick(560, 7360, 0.8, "hold"), 0, 0.6, sfx="wood_high")
L(face(560, 7360, 0.8, "sad"), 0.6, 0.8)
for n in range(4):
    L(doc(1000 + n * 70, 7100 - n * 50), 1 + n * 0.2, 1.2 + n * 0.2, sfx="pop" if n == 0 else None)
T("订单 ×3", 950, 6670, 70, RED, k0=2, sfx="pop")
L(arrow((1450, 7150), (1450, 6750), 0, 40), 3, 3.4, RED, 10, sfx="wood_high")
T("差评", 1300, 7200, 64, RED, k0=4, sfx="rim")
T("卡在：客服", *STUCK[0], 60, RED, k0=5, k1=5.6, sfx="tom")
L(P((STUCK[0][0] - 150, STUCK[0][1] + 50), (STUCK[0][0] + 150, STUCK[0][1] + 50)), 5.7, 6, RED, 6)

scene("排长队，后厨就俩人", "例子 · 奶茶店", (2650, 7000, 0.85))
L(shop(2350, 7350), 0, 0.9, sfx="wood_high")
T("奶茶", 2350, 6880, 60, k0=1, sfx="pop")
for n in range(5):
    L(stick(2700 + n * 120, 7350, 0.45), 2 + n * 0.25, 2.25 + n * 0.25, BLUE, 8, sfx="pop" if n == 0 else None)
T("后厨 2 人", 2350, 6700, 64, RED, k0=3.3, k1=3.9)
H(3, "shaker")
L(join(clock(2950, 6780, 90), hands_at(2950, 6780, 90, 1, 40)), 4, 4.6, RED, 9, sfx="rim")
T("卡在：人手", *STUCK[1], 56, RED, k0=5, k1=5.7, sfx="tom")

scene("课越报越多，觉不够睡", "例子 · 补课", (950, 8350, 0.85))
L(stick(560, 8630, 0.65), 0, 0.5, sfx="wood_high")
L(face(560, 8630, 0.65, "flat"), 0.5, 0.6)
for n, w in enumerate(("数学", "英语", "作文", "编程")):
    y = 8610 - n * 100
    L(rect(1150, y, 380, 86, 10), 1 + n * 0.5, 1.2 + n * 0.5, sfx="pop" if n % 2 == 0 else None)
    T(w, 1150, y, 50, k0=1.2 + n * 0.5, k1=1.45 + n * 0.5)
L(join(clock(560, 8150, 90), hands_at(560, 8150, 90, 0, 0)), 3, 3.6, RED, 9, sfx="wood_low")
T("分数没涨", 1150, 8050, 56, k0=4, sfx="pop")
T("卡在：睡觉", *STUCK[2], 56, RED, k0=5, k1=5.7, sfx="tom")

MC = (2770, 8580, 480, 380)
scene("天天加练，肌肉不长", "例子 · 健身", (2650, 8350, 0.85))
L(stick(2330, 8730, 0.75, "up"), 0, 0.6, sfx="wood_high")
L(barbell(2330, 8440, 340), 1, 1.4, BLACK, 9, sfx="pop")
T("每天 2 小时", 2420, 8050, 56, k0=2, sfx="pop")
L(sweat(2380, 8500), 3, 3.4, BLUE, 6, sfx="shaker")
L(axes(*MC), 4, 4.4, BLACK, 7, sfx="wood_high")
L(fcurve(*MC, logistic), 4.4, 4.9, RED, 10)
T("卡在：吃和睡", *STUCK[3], 56, RED, k0=5, k1=5.6, sfx="tom")
L(P((STUCK[3][0] - 170, STUCK[3][1] + 48), (STUCK[3][0] + 170, STUCK[3][1] + 48)), 5.7, 6, RED, 6)

scene("都卡在一处，猛加没用", "身边的例子", (1800, 7800, 0.34), shake=[4])
for n, (x, y) in enumerate(STUCK):
    L(ring(x, y, 220, 70), n, n + 0.4, RED, 9, sfx="rim" if n % 2 == 0 else None)
H(1, "wood_high", 0.6)
T("猛加投入", 1800, 8970, 150, RED, k0=4, k1=4.6, sfx="kick")
L(cross(1800, 8970, 150), 5, 5.3, RED, 14, sfx="rim")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

DS = 1600                # 具体做法整体下移
SOL = [(950, 8650 + DS), (2650, 8650 + DS), (950, 9900 + DS), (2650, 9900 + DS)]
GC = (520, 10560, 820, 460)
scene("先画出增长曲线", "第一步 · 画曲线", (950, 10250, 0.85))
L(rect(*SOL[0], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("① 画曲线", 950, 9930, 76, BLUE, k0=1, sfx="pop")
L(axes(*GC), 2, 2.5, BLACK, 8, sfx="wood_high")
T("每月业绩", 640, 10070, 46, k0=2.5, k1=2.9)
L(fcurve(*GC, logistic), 3, 4.2, BLUE, 10, sfx="shaker")
L(ring(1200, 10140, 170, 80), 5, 5.4, RED, 8, sfx="rim")
T("变平了", 1200, 10290, 60, RED, k0=5.4, k1=5.95)

LIST = [("人手", 2300, 10160), ("钱", 2650, 10160), ("客户", 3000, 10160), ("机器", 2470, 10340), ("时间", 2830, 10340)]
scene("列清单，找最先用完的", "第二步 · 列清单", (2650, 10250, 0.85))
L(rect(*SOL[1], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("② 列清单", 2650, 9930, 76, BLUE, k0=1, sfx="pop")
for n, (w, x, y) in enumerate(LIST):
    k = (2, 2.4, 2.8, 3, 3.4)[n]
    T(w, x, y, 60, k0=k, k1=k + 0.35, sfx="pop" if n in (0, 3) else None)
L(ring(2300, 10160, 110, 60), 4, 4.4, RED, 8, sfx="rim")
T("最先用完", 2300, 10530, 64, RED, k0=5, sfx="pop")

scene("钱先补到最缺的", "第三步 · 先补它", (950, 11500, 0.85))
L(rect(*SOL[2], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("③ 先补它", 950, 11180, 76, BLUE, k0=1, sfx="pop")
T("¥", 560, 11430, 160, GREEN, k0=2, k1=2.3, sfx="pop")
L(arrow((680, 11430), (900, 11430), 0, 34), 2.3, 2.6, GREEN, 8)
T("人手", 1050, 11430, 70, RED, k0=3, sfx="pop")
for n in range(3):
    L(stick(1300 + n * 110, 11650, 0.4), 4 + n * 0.25, 4.25 + n * 0.25, BLUE, 8, sfx="pop" if n == 0 else None)
T("客服 +3", 1050, 11670, 56, BLUE, k0=5, k1=5.6, sfx="ding")

scene("补完了，盯下一块", "第四步 · 盯下一块", (2650, 11500, 0.85))
L(rect(*SOL[3], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("④ 盯下一块", 2650, 11180, 76, BLUE, k0=1, sfx="pop")
T("客服", 2300, 11370, 64, k0=2, sfx="pop")
L(check(2420, 11365, 36), 2.4, 2.7, GREEN, 9)
L(arrow((2490, 11370), (2800, 11370), -0.15, 34), 3, 3.4, BLACK, 8, sfx="wood_high")
T("机器？", 2950, 11370, 64, RED, k0=3.4, k1=3.9)
L(calendar(2330, 11690, 200, 170), 4, 4.6, sfx="wood_high")
T("现在卡在哪？", 2860, 11690, 60, RED, k0=5, k1=6, sfx="pop")

# ---------------------------------------------------------------- 收尾（场景 20–21）

scene("找对卡点再使劲", "一句话", (1800, 6500, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 12800, 0.8))
H(0, "cymbal", 0.5)
T("你被哪块卡住过？", 1800, 12720, 80, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：公司冰箱为什么总是乱糟糟？", 1800, 12880, 46, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "limits", "增长的极限", "业绩为什么涨着涨着就不动了？", ACC, b.shots,
                 [f"{BOOK}（转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                 "业绩涨着涨着|就【不动了】", 7,
                 ["书中观点均为转述，不是原话：在有限的环境里，靠增强回路推动的增长迟早会碰上调节回路，曲线由陡变平；"
                  "书中用开采不可再生资源（油田）与捕捞可再生资源（渔场）举例；限制增长的因素不止一个，补上一个，"
                  "下一个就成了新的限制，所以要不断找出当下真正的限制因素。出处：Donella H. Meadows, Thinking in Systems: "
                  "A Primer (2008)，中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                  "木桶短板为示意比喻；各曲线形状、板高、船数、鱼数均为示意。订单猛增客服接不过来、奶茶店后厨人手不够、"
                  "孩子补课越报越多、健身加练不长肌肉均为现实场景示意，不指向任何具体公司或个人；"
                  "四步做法（画曲线、列清单、先补最先用完的、每月盯下一块）为据书中思路整理的建议。"],
                 tags="#增长 #瓶颈 #职场")
    return b.attach(ep)
