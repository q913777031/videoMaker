"""08 目标侵蚀（白板手绘版）：标准为什么越来越低？

叙事：打工人切身问题开局（年初定下每天跑一小时，一周后半小时，再后来十分钟，最后“有空再说”）→
书中观点（亮书；系统陷阱之一“目标侵蚀”：标准跟着过去的表现走，坏消息比好消息记得牢；表现变差 → 预期降低 →
标准降低 → 努力减少 → 表现更差，画成一个往下转的回路；每次只降一点，很难察觉）→ 身边的例子（团队季度目标越调越低、
每月存钱变成剩多少存多少、每晚讲故事变成周末讲一个、稿子查三遍变成能交就行；都在跟上一次比）→
具体做法（写下不随心情变的底线 / 跟最好的那次比 / 做到的好事也记下来 / 月底回看，降了就调回去）→ 评论区互动。
书中观点为转述：Meadows, Thinking in Systems: A Primer (2008) 第五章 System Traps 之 Drift to Low Performance；
中译本《系统之美》，邱昭良译，浙江人民出版社 2012。书中给出的出路：保持绝对标准，或让标准参照过去最好的表现。
例子为现实场景示意，做法为据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, clock, cross, doc, face,
                               join, rect, scribble, stick, underline, bubble)
from adler import kit as K

from .common import BOOK, episode

ACC = "#9A5B3C"
SQUARE_SHOT = 15

b = Board(size=(3600, 10000))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def strike(s, x, y, size, k0, sfx="rim"):
    """把已写的一行字划掉。"""
    w = K.text_w(s, size, "hand")
    L(P((x - w / 2 - 14, y + 4), (x + w / 2 + 14, y - 4)), k0, k0 + 0.35, RED, 9, sfx=sfx)


# ---------------------------------------------------------------- 本讲小图元

def sofa(x, y, w=560):
    """沙发（正视）：(x, y) 为坐垫中点。"""
    h = w / 2
    return join(P((x - h + 30, y - 40), (x - h + 30, y - 230), (x + h - 30, y - 230), (x + h - 30, y - 40)),
                rect(x, y, w, 90, 24), rect(x - h, y - 40, 70, 170, 24), rect(x + h, y - 40, 70, 170, 24),
                P((x - h + 30, y + 45), (x - h + 30, y + 110)), P((x + h - 30, y + 45), (x + h - 30, y + 110)))


def sitting(x, y, s=1.0):
    """瘫坐的小人：(x, y) 为臀部。"""
    return join(circle(x, y - 230 * s, 42 * s), P((x, y - 188 * s), (x + 10 * s, y)),
                P((x + 10 * s, y), (x + 150 * s, y + 10 * s), (x + 160 * s, y + 150 * s)),
                P((x + 4 * s, y - 130 * s), (x + 110 * s, y - 70 * s), (x + 170 * s, y - 90 * s)))


def stairs(x0, y0, n, dx, dy):
    pts = [(x0, y0)]
    for i in range(n):
        x, y = pts[-1]
        pts.append((x + dx, y))
        if i < n - 1:
            pts.append((x + dx, y + dy))
    return P(*pts)


def pit(x, y, w=360, d=240):
    """坑：(x, y) 为坑口中点。"""
    p = skia.Path()
    p.moveTo(x - w / 2 - 120, y)
    p.lineTo(x - w / 2, y)
    p.cubicTo(x - w / 2, y + d, x + w / 2, y + d, x + w / 2, y)
    p.lineTo(x + w / 2 + 120, y)
    return p


def oval(x, y, w, h):
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def piggy(x, y):
    """存钱罐：(x, y) 为身体中心。"""
    return join(oval(x, y, 300, 210), rect(x + 165, y, 50, 70, 16), P((x - 40, y - 105), (x + 40, y - 105)),
                P((x - 90, y + 95), (x - 90, y + 150)), P((x + 80, y + 95), (x + 80, y + 150)),
                P((x - 60, y - 95), (x - 85, y - 150), (x - 20, y - 105)))


def bars(x0, base, hs, w=90, gap=60):
    parts = [P((x0 - 60, base), (x0 + len(hs) * (w + gap), base))]
    for i, h in enumerate(hs):
        x = x0 + i * (w + gap)
        parts.append(P((x, base), (x, base - h), (x + w, base - h), (x + w, base)))
    return join(*parts)


def dashed(x0, x1, y, seg=50, gap=30):
    parts, x = [], x0
    while x < x1:
        parts.append(P((x, y), (min(x1, x + seg), y)))
        x += seg + gap
    return join(*parts)


def calendar(x, y, w=300, h=280):
    parts = [rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 60), (x + w / 2, y - h / 2 + 60)),
             P((x - w / 4, y - h / 2 - 25), (x - w / 4, y - h / 2 + 20)),
             P((x + w / 4, y - h / 2 - 25), (x + w / 4, y - h / 2 + 20))]
    for r in range(1, 4):
        yy = y - h / 2 + 60 + r * (h - 60) / 4
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
    for c in range(1, 5):
        xx = x - w / 2 + c * w / 5
        parts.append(P((xx, y - h / 2 + 60), (xx, y + h / 2)))
    return join(*parts)


# ---------------------------------------------------------------- 开局：跑步计划一降再降（镜头 1–6）

b.shot("年初定了个计划", "灵魂拷问", view=(950, 900, 0.85))
L(stick(560, 1250, 0.85, "up"), 0, 0.7, sfx="wood_high")
T("每天跑步", 1120, 620, 80, k0=1, sfx="pop")
T("60分钟", 1120, 780, 100, k0=1.8, k1=2.6)
L(clock(560, 640, 90), 2, 2.6, sfx="wood_low")

b.shot("忙了一周，减半", "灵魂拷问", view=(950, 900, 0.85))
strike("60分钟", 1120, 780, 100, 0)
T("30分钟", 1120, 940, 90, k0=1, sfx="pop")
L(face(560, 1250, 0.85, "flat"), 2, 2.3, sfx="wood_high")

b.shot("又累了，再砍", "灵魂拷问", view=(950, 920, 0.85))
strike("30分钟", 1120, 940, 90, 0)
T("10分钟", 1120, 1100, 80, RED, k0=1, sfx="pop")
T("好累", 380, 870, 56, BLUE, k0=2, sfx="pop")

b.shot("后来干脆不跑了", "灵魂拷问", view=(2650, 900, 0.85))
L(sofa(2600, 1120), 0, 0.9, sfx="wood_high")
L(sitting(2520, 1080), 1, 1.6, BLUE, sfx="pop")
L(bubble(2960, 640, 380, 140, -1), 2, 2.4, sfx="wood_high")
T("有空再说", 2960, 640, 62, k0=2.4)

b.shot("一路往下掉", "灵魂拷问", view=(1800, 1650, 0.85))
L(stairs(1300, 1350, 4, 250, 170), 0, 1.2, sfx="wood_low")
for n, w in enumerate(("60", "30", "10", "0")):
    T(w, 1425 + n * 250, 1290 + n * 170, 66, RED if n == 3 else BLACK, k0=0.3 + n * 0.3, k1=0.5 + n * 0.3)
L(arrow((1250, 1500), (2250, 2020), -0.08, 50), 2, 2.6, RED, 10, sfx="tom")

b.shot("标准去哪了？", "灵魂拷问", view=(1800, 1400, 0.42), flashes=[0])
T("？", 2950, 1650, 300, RED, k0=0, k1=0.5, sfx="kick")
T("标准去哪了", 1800, 2180, 110, k0=1, k1=2, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "系统之美", view=(950, 2700, 0.85))
L(book(700, 2690, 420, 280), 0, 1.0, sfx="wood_low")
T("系统之美", 700, 2440, 80, GREEN, k0=1, sfx="pop")
T("德内拉 · 梅多斯", 700, 2930, 50, k0=2, sfx="pop")

b.shot("书里讲过一种陷阱", "书中观点 · 系统陷阱", view=(950, 2700, 0.85))
T("系统陷阱", 1300, 2440, 70, BLUE, k0=0, sfx="pop")
L(pit(1300, 2640, 300, 220), 1, 1.8, BLACK, 10, sfx="wood_high")
L(scribble(1300, 2720, 200, 80, 6), 2, 2.4, BLACK, 5, sfx="shaker")

b.shot("叫目标侵蚀", "书中观点 · 目标侵蚀", view=(950, 2800, 0.85), shake=[0], flashes=[0])
T("目标侵蚀", 950, 3080, 120, RED, k0=0, k1=0.5, sfx="kick")
L(underline(690, 1210, 3160), 1, 1.5, RED, 8, sfx="ding")
L(arrow((1300, 2500), (1300, 2720), 0.0, 44), 2, 2.4, RED, 10, sfx="tom")

b.shot("标准看过去的成绩", "书中观点 · 目标侵蚀", view=(2650, 2750, 0.85))
L(P((2200, 2350), (2200, 3100), (3170, 3100)), 0, 0.6, BLACK, 9, sfx="wood_high")
ZIG = [(2250 + i * 110, y) for i, y in enumerate((2500, 2600, 2560, 2700, 2660, 2800, 2770, 2920, 2900))]
L(P(*ZIG), 1, 1.8, BLACK, 9, sfx="shaker")
T("表现", 3110, 2990, 54, k0=2, sfx="pop")

b.shot("成绩一差就跟着降", "书中观点 · 目标侵蚀", view=(2650, 2750, 0.85))
L(stairs(2250, 2440, 4, 220, 125), 0, 0.9, BLUE, 9, sfx="pop")
T("标准", 2360, 2380, 54, BLUE, k0=1, sfx="pop")
L(arrow((3100, 2380), (3100, 2660), 0.0, 40), 2, 2.4, RED, 10, sfx="tom")

b.shot("坏消息记得更牢", "书中观点 · 坏消息更重", view=(950, 3850, 0.85))
L(bubble(600, 3620, 300, 140, -1), 0, 0.4, sfx="pop")
T("好消息", 600, 3620, 54, k0=0.4, k1=0.8)
L(bubble(1150, 3900, 600, 320, -1), 1, 1.6, RED, 10, sfx="wood_high")
T("坏消息", 1150, 3900, 110, RED, k0=2, k1=2.6, sfx="pop")

b.shot("好的转眼就忘", "书中观点 · 坏消息更重", view=(950, 3850, 0.85))
L(stick(430, 4250, 0.6, "shrug"), 0, 0.5, sfx="wood_high")
b.erase(len(b.shots) - 1, 1, 1.6, 600, 3640, 380, 250)
H(1, "shaker")
T("忘了", 600, 3630, 60, k0=2, sfx="pop")

LOOP = [("表现变差", 2650, 3500), ("预期降低", 3070, 3850), ("标准降低", 2650, 4200), ("努力减少", 2230, 3850)]
LOOP_ARROWS = [((2790, 3530), (3070, 3790)), ((3070, 3910), (2790, 4180)), ((2510, 4180), (2230, 3910)),
               ((2230, 3790), (2510, 3530))]


def loop_node(n, k0, sfx="pop"):
    w, x, y = LOOP[n]
    L(rect(x, y, 260, 96, 30), k0, k0 + 0.4, BLACK, 7, sfx=sfx)
    T(w, x, y, 54, RED if n == 0 else BLACK, k0=k0 + 0.3, k1=k0 + 0.8)


def loop_arrow(n, k0, sfx=None):
    L(arrow(*LOOP_ARROWS[n], -0.18, 36), k0, k0 + 0.5, GREEN, 8, sfx=sfx)


b.shot("表现差，预期就低", "书中观点 · 往下的回路", view=(2650, 3850, 0.85))
loop_node(0, 0)
loop_arrow(0, 1, "wood_high")
loop_node(1, 2)

b.shot("标准降，劲也松了", "书中观点 · 往下的回路", view=(2650, 3850, 0.85))
loop_arrow(1, 0, "wood_high")
loop_node(2, 1)
loop_arrow(2, 2, "wood_high")
loop_node(3, 3)

b.shot("绕一圈，更差了", "书中观点 · 往下的回路", view=(2650, 3850, 0.85), shake=[1])
loop_arrow(3, 0, "wood_high")
T("越转越低", 2650, 3830, 66, RED, k0=1, k1=1.5, sfx="kick")
L(underline(2520, 2780, 3880, 10, 32), 2, 2.4, RED, 7, sfx="ding")

b.shot("慢得没人察觉", "书中观点 · 很难察觉", view=(1800, 3300, 0.42))
T("每次只降一点点", 1800, 3290, 120, RED, k0=0, k1=1.4, sfx="pop")
H(2, "wood_low")
L(P((1380, 3370), (2220, 3370)), 2, 2.5, BLACK, 6)

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5300), (2650, 5300), (950, 6300), (2650, 6300)]
b.shot("身边就有例子", "身边的例子", view=(1800, 5550, 0.42))
T("身边的例子", 1800, 4720, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("这季没达标", "例子 · 团队目标", view=(950, 5300, 0.85))
L(stick(560, 5700, 0.85, "point", tie=True), 0, 0.6, sfx="wood_high")
L(face(560, 5700, 0.85, "flat"), 0.6, 0.75)
T("目标：100", 1150, 5000, 76, k0=1, sfx="pop")
T("实际：80", 1150, 5140, 76, RED, k0=2, sfx="pop")

b.shot("下季就调低点", "例子 · 团队目标", view=(950, 5300, 0.85))
strike("目标：100", 1150, 5000, 76, 0)
T("下季：80", 1150, 5290, 76, BLUE, k0=1, sfx="pop")
L(arrow((1480, 4980), (1480, 5320), 0.0, 40), 2, 2.4, RED, 10, sfx="tom")

b.shot("说好每月存两千", "例子 · 存钱", view=(2650, 5300, 0.85))
T("每月存 2000", 2830, 5000, 72, k0=0, sfx="pop")
L(piggy(2380, 5420), 1, 1.8, BLACK, 9, sfx="wood_high")
L(join(circle(2380, 5180, 40), arrow((2380, 5230), (2380, 5300), 0.0, 24)), 2, 2.4, GREEN, 8, sfx="ding")

b.shot("后来剩多少存多少", "例子 · 存钱", view=(2650, 5300, 0.85))
strike("每月存 2000", 2830, 5000, 72, 0)
T("剩多少存多少", 2830, 5170, 64, k0=1, sfx="pop")
T("月底：0", 2830, 5340, 80, RED, k0=2, sfx="tom")

b.shot("每晚给娃讲故事", "例子 · 陪孩子", view=(950, 6300, 0.85))
L(stick(560, 6690, 0.8), 0, 0.6, sfx="wood_high")
L(stick(770, 6690, 0.5, "up"), 1, 1.4, BLUE, sfx="pop")
T("每晚讲个故事", 1120, 6000, 66, k0=2, sfx="pop")
L(book(1250, 6340, 230, 150), 2.6, 3.2)

b.shot("累了就改周末", "例子 · 陪孩子", view=(950, 6300, 0.85))
strike("每晚讲个故事", 1120, 6000, 66, 0)
T("周末讲一个", 1120, 6120, 62, RED, k0=1, sfx="pop")
L(bubble(400, 6250, 240, 110, 1), 2, 2.3, sfx="wood_high")
T("明天吧", 400, 6250, 50, k0=2.3, k1=2.7)

b.shot("稿子查三遍才交", "例子 · 交稿", view=(2650, 6300, 0.85))
T("检查 3 遍才交", 2650, 6000, 66, k0=0, sfx="pop")
DOCS = [(2390, 6300), (2610, 6300), (2830, 6300)]
L(join(*[doc(x, y) for x, y in DOCS]), 1, 1.7, BLACK, 8, sfx="wood_high")
L(join(*[check(x + 40, y + 140, 30) for x, y in DOCS]), 2, 2.5, GREEN, 8, sfx="ding")

b.shot("现在能交就行", "例子 · 交稿", view=(2650, 6300, 0.85))
L(join(cross(2610, 6300, 80), cross(2830, 6300, 80)), 0, 0.5, RED, 11, sfx="rim")
T("能交就行", 2650, 6560, 76, RED, k0=1, sfx="pop")
L(stick(3150, 6700, 0.6, "shrug"), 2, 2.5, BLUE, sfx="wood_high")

b.shot("回头一看，差好远", "身边的例子", view=(1800, 5850, 0.42))
T("回头一看：差好远", 1800, 6880, 100, k0=0, k1=1.4, sfx="pop")
H(2, "ding")

b.shot("都在跟上次比", "身边的例子", view=(1800, 5850, 0.42), shake=[0])
T("跟上次比", 1800, 5800, 140, RED, k0=0, k1=0.5, sfx="kick")
for n, (x, y) in enumerate(CARDS):
    L(arrow((1800 + (x - 1800) * 0.2, 5800 + (y - 5800) * 0.25), (1800 + (x - 1800) * 0.55, 5800 + (y - 5800) * 0.55),
            0.1, 40), 1 + n * 0.5, 1.4 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 7800), (2650, 7800), (950, 8750), (2650, 8750)]
b.shot("守住标准这样做", "具体做法", view=(1800, 8150, 0.42))
T("守住标准，这样做", 1800, 7230, 110, k0=0, k1=1.6, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1500, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先把底线写下来", "第一招 · 写下底线", view=(950, 7800, 0.85))
T("① 写下底线", 950, 7500, 80, BLUE, k0=0, sfx="pop")
L(rect(950, 7810, 760, 240, 20), 1, 1.6, BLACK, 8, sfx="wood_high")
T("底线：", 670, 7810, 56, RED, k0=2, sfx="pop")

b.shot("每周至少跑三次", "第一招 · 写下底线", view=(950, 7850, 0.85))
T("每周至少跑 3 次", 1020, 7810, 56, k0=0, k1=1.2, sfx="pop")
L(check(1420, 7800, 40), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("累了就跑慢点", "第一招 · 写下底线", view=(950, 7950, 0.85))
T("累了：跑慢点", 950, 8040, 60, k0=0, sfx="pop")
T("次数不变", 950, 8150, 60, RED, k0=1, sfx="pop")
L(check(1170, 8145, 32), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("跟最好的那次比", "第二招 · 看最好的", view=(2650, 7800, 0.85))
T("② 跟最好的比", 2650, 7500, 80, BLUE, k0=0, sfx="pop")
L(bars(2250, 8050, (200, 280, 380, 250, 220)), 1, 1.8, BLACK, 8, sfx="wood_high")
L(scribble(2595, 7860, 70, 360, 9), 2, 2.4, RED, 6, sfx="ding")

b.shot("最好跑过五公里", "第二招 · 看最好的", view=(2650, 7800, 0.85))
T("最好：5公里", 2595, 7600, 56, RED, k0=0, sfx="pop")
L(underline(2440, 2750, 7640, 8, 30), 2, 2.4, RED, 6, sfx="wood_high")

b.shot("目标就照它来定", "第二招 · 看最好的", view=(2650, 7800, 0.85))
L(dashed(2200, 3000, 7670), 0, 0.6, RED, 7, sfx="rim")
T("目标线", 3120, 7670, 54, RED, k0=1, sfx="pop")
L(arrow((3120, 7960), (3120, 7730), 0.0, 34), 2, 2.4, GREEN, 9, sfx="ding")

b.shot("做到的也记一笔", "第三招 · 好事也记", view=(950, 8750, 0.85))
T("③ 好事也记下", 950, 8450, 80, BLUE, k0=0, sfx="pop")
L(join(rect(950, 8790, 700, 380, 18), *[circle(700 + n * 125, 8600, 16) for n in range(5)]), 1, 1.7, BLACK, 8,
  sfx="wood_high")
T("周五：", 720, 8670, 52, k0=2, sfx="pop")

b.shot("周五写三件好事", "第三招 · 好事也记", view=(950, 8800, 0.85))
for n, w in enumerate(("跑了 3 次", "早睡 2 天", "读完 1 章")):
    T(w, 990, 8750 + n * 85, 52, k0=n, sfx="pop")
    L(check(1210, 8745 + n * 85, 26), n + 0.55, n + 0.8, GREEN, 8)

b.shot("每月翻一次旧账", "第四招 · 月底回看", view=(2650, 8750, 0.85))
T("④ 月底回看", 2650, 8450, 80, BLUE, k0=0, sfx="pop")
L(calendar(2270, 8780), 1, 1.8, BLACK, 7, sfx="wood_high")
L(circle(2360, 8875, 34), 2, 2.4, RED, 8, sfx="ding")

b.shot("拿一月份对一对", "第四招 · 月底回看", view=(2650, 8800, 0.85))
T("1月：每周 4 次", 2890, 8700, 54, k0=0, sfx="pop")
T("10月：每周 2 次", 2890, 8820, 54, RED, k0=1, sfx="pop")
L(underline(2660, 3120, 8865, 8, 30), 2, 2.4, RED, 6, sfx="wood_high")

b.shot("降了就调回去", "第四招 · 月底回看", view=(2650, 8850, 0.85))
L(arrow((3200, 9060), (3200, 8760), 0.0, 40), 0, 0.5, GREEN, 10, sfx="tom")
T("下月调回 4 次", 2890, 8990, 56, GREEN, k0=1, sfx="pop")
L(check(2600, 8985, 30), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("底线定了别往下调", "一句话", view=(1800, 5000, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 9650, 0.8))
T("你哪个标准在悄悄降？", 1800, 9560, 80, RED, k0=0.5, k1=1.8)
T("下一讲：为什么越熬夜越离不开咖啡？", 1800, 9720, 50, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "drift", "目标侵蚀", "标准为什么越来越低？", ACC, b.shots,
                 [f"{BOOK}第五章 · 系统陷阱：目标侵蚀（转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                 "标准一降再降|是个【系统陷阱】", SQUARE_SHOT,
                 ["书中观点均为转述：系统陷阱之一“目标侵蚀”（drift to low performance）——标准受过去表现影响，"
                  "人们对坏消息的感知比好消息更重，于是表现变差 → 预期降低 → 标准降低 → 努力减少 → 表现更差，形成往下走的回路；"
                  "变化缓慢，不易察觉。书中给出的出路：保持绝对标准，或让标准参照过去最好的表现。出处：Donella H. Meadows, "
                  "Thinking in Systems: A Primer (2008) 第五章 System Traps；中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                  "回路节点名称为对书中机制的通俗化转述；跑步计划、团队季度目标、存钱、给孩子讲故事、交稿检查均为现实场景示意，"
                  "图表与数字均为示意，不指向任何具体公司或个人；四招做法为据书中思路整理的建议。"],
                 tags="#目标管理 #自律")
    return b.attach(ep)
