"""08 目标侵蚀（白板手绘版）：标准为什么越来越低？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
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
SQUARE_SHOT = 0

b = Board(size=(3600, 12300))


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


# ---------------------------------------------------------------- 开局：跑步计划一降再降（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("跑步计划一砍再砍", "灵魂拷问", (950, 900, 0.85))
L(stick(560, 1250, 0.85, "up"), 0, 0.6, sfx="wood_high")
L(clock(560, 640, 90), 0.6, 1.0)
T("每天跑步", 1120, 620, 80, k0=1, sfx="pop")
T("60分钟", 1120, 780, 100, k0=1.8, k1=2.5)
strike("60分钟", 1120, 780, 100, 3)
T("30分钟", 1120, 940, 90, k0=3.4, k1=3.9)
strike("30分钟", 1120, 940, 90, 4)
T("10分钟", 1120, 1100, 80, RED, k0=4.4, k1=4.9)
L(face(560, 1250, 0.85, "flat"), 5, 5.3, sfx="wood_high")
T("好累", 820, 1120, 56, BLUE, k0=5.3, k1=5.8)

scene("后来干脆不跑了", "灵魂拷问", (2750, 950, 0.85))
L(sofa(2750, 1120), 0, 0.9, sfx="wood_high")
L(sitting(2670, 1080), 1, 1.6, BLUE, sfx="pop")
L(bubble(3100, 640, 380, 140, -1), 3, 3.4, sfx="wood_high")
T("有空再说", 3100, 640, 62, k0=3.4, k1=4.1)
T("跑鞋吃灰", 2750, 1420, 60, k0=5, k1=5.7, sfx="pop")

scene("标准去哪了？", "灵魂拷问", (1835, 1550, 0.34), shake=[4], flashes=[4])
STEPS = [(1415, 1340), (1745, 1540), (2075, 1740), (2405, 1940)]
L(stairs(1250, 1400, 4, 330, 200), 0, 1.2, BLACK, 10, sfx="wood_low")
for n, w in enumerate(("60", "30", "10", "0")):
    T(w, *STEPS[n], 90, RED if n == 3 else BLACK, k0=0.4 + n * 0.3, k1=0.6 + n * 0.3)
L(arrow((1250, 1560), (2400, 2140), -0.08, 50), 2, 2.6, RED, 10, sfx="tom")
T("？", 2950, 1750, 260, RED, k0=4, k1=4.4, sfx="kick")
T("标准去哪了", 900, 1900, 110, k0=4.6, k1=5.8)

# ---------------------------------------------------------------- 书中观点（场景 4–9）

scene("书里说这是个陷阱", "系统之美 · 系统陷阱", (1000, 2900, 0.85))
L(book(700, 2690, 420, 280), 0, 1.0, sfx="wood_low")
T("系统之美", 700, 2440, 80, GREEN, k0=1, sfx="pop")
T("德内拉 · 梅多斯", 700, 2930, 50, k0=1.8, k1=2.8)
T("系统陷阱", 1300, 2440, 70, BLUE, k0=3, sfx="pop")
L(pit(1300, 2640, 300, 220), 4, 4.8, BLACK, 10, sfx="wood_high")
L(scribble(1300, 2720, 200, 80, 6), 5, 5.4, BLACK, 5, sfx="shaker")

scene("这叫目标侵蚀", "书中观点 · 目标侵蚀", (1000, 2950, 0.85), shake=[0], flashes=[0])
T("目标侵蚀", 950, 3080, 120, RED, k0=0, k1=0.5, sfx="kick")
L(underline(690, 1210, 3160), 1, 1.5, RED, 8, sfx="ding")
L(arrow((1300, 2500), (1300, 2720), 0.0, 44), 2, 2.4, RED, 10, sfx="tom")
T("标准", 1150, 2565, 50, RED, k0=3, k1=3.5, sfx="pop")

scene("标准跟着成绩往下走", "书中观点 · 目标侵蚀", (2680, 3060, 0.85))
L(P((2200, 2600), (2200, 3350), (3170, 3350)), 0, 0.6, BLACK, 9, sfx="wood_high")
ZIG = [(2250 + i * 110, y + 250) for i, y in enumerate((2500, 2600, 2560, 2700, 2660, 2800, 2770, 2920, 2900))]
L(P(*ZIG), 1, 1.8, BLACK, 9, sfx="shaker")
T("表现", 3110, 3240, 54, k0=2, sfx="pop")
L(stairs(2250, 2690, 4, 220, 125), 3, 3.9, BLUE, 9, sfx="wood_high")
T("标准", 2360, 2630, 54, BLUE, k0=4, sfx="pop")
L(arrow((3100, 2630), (3100, 2910), 0.0, 40), 5, 5.4, RED, 10, sfx="tom")

scene("坏的记牢，好的忘了", "书中观点 · 坏消息更重", (950, 4060, 0.85))
L(bubble(600, 3620, 300, 140, -1), 0, 0.4, sfx="pop")
T("好消息", 600, 3620, 54, k0=0.4, k1=0.8)
L(bubble(1150, 3900, 600, 320, -1), 1, 1.6, RED, 10, sfx="wood_high")
T("坏消息", 1150, 3900, 110, RED, k0=2, k1=2.6, sfx="pop")
L(stick(430, 4250, 0.6, "shrug"), 3, 3.5, sfx="wood_high")
b.erase(len(b.shots) - 1, 4, 4.6, 600, 3640, 380, 250)
H(4, "shaker")
T("忘了", 600, 3630, 60, k0=5, k1=5.5, sfx="pop")

LOOP = [("表现变差", 2650, 3800), ("预期降低", 3070, 4150), ("标准降低", 2650, 4500), ("努力减少", 2230, 4150)]
LOOP_ARROWS = [((2790, 3830), (3070, 4090)), ((3070, 4210), (2790, 4480)), ((2510, 4480), (2230, 4210)),
               ((2230, 4090), (2510, 3830))]


def loop_node(n, k0, sfx=None):
    w, x, y = LOOP[n]
    L(rect(x, y, 260, 96, 30), k0, k0 + 0.3, BLACK, 7, sfx=sfx)
    T(w, x, y, 54, RED if n == 0 else BLACK, k0=k0 + 0.3, k1=k0 + 0.7)


def loop_arrow(n, k0, sfx=None):
    L(arrow(*LOOP_ARROWS[n], -0.18, 36), k0, k0 + 0.4, GREEN, 8, sfx=sfx)


scene("一圈圈往下转", "书中观点 · 往下的回路", (2650, 4250, 0.85), shake=[5])
loop_node(0, 0, "pop")
loop_arrow(0, 1, "wood_high")
loop_node(1, 1.5)
loop_arrow(1, 2.2)
loop_node(2, 2.6)
loop_arrow(2, 3, "wood_high")
loop_node(3, 3.5)
loop_arrow(3, 4.2)
T("越转越低", 2650, 4130, 66, RED, k0=5, k1=5.5, sfx="kick")
L(underline(2520, 2780, 4180, 10, 32), 5.5, 5.9, RED, 7)

scene("每次只降一点点", "书中观点 · 很难察觉", (2650, 4250, 0.85))
T("每次只降一点点", 2750, 4700, 80, RED, k0=0, k1=1.3, sfx="pop")
L(P((2480, 4750), (3020, 4750)), 2, 2.5, BLACK, 6, sfx="wood_low")
L(join(circle(2290, 4690, 50), P((2325, 4725), (2375, 4775))), 4, 4.5, BLUE, 8, sfx="ding")
T("？", 2290, 4690, 56, BLUE, k0=4.5, k1=4.8)

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 6600), (2650, 6600), (950, 7800), (2650, 7800)]
scene("身边就有例子", "身边的例子", (1800, 7200, 0.34))
T("身边的例子", 1800, 6020, 110, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1400, 900, 40), 2 + n * 0.8, 2.6 + n * 0.8, GREEN, 8, sfx="wood_high" if n in (0, 2) else None)

scene("没达标，下季就调低", "例子 · 团队目标", (870, 6700, 0.85))
L(stick(560, 7000, 0.85, "point", tie=True), 0, 0.6, sfx="wood_high")
L(face(560, 7000, 0.85, "flat"), 0.6, 0.75)
T("目标：100", 1150, 6300, 76, k0=1, sfx="pop")
T("实际：80", 1150, 6440, 76, RED, k0=2, sfx="pop")
strike("目标：100", 1150, 6300, 76, 3)
T("下季：80", 1150, 6590, 76, BLUE, k0=4, sfx="pop")
L(arrow((1480, 6280), (1480, 6620), 0.0, 40), 5, 5.4, RED, 10, sfx="tom")

scene("存钱变成剩多少存多少", "例子 · 存钱", (2710, 6700, 0.85))
T("每月存 2000", 2830, 6300, 72, k0=0, sfx="pop")
L(piggy(2380, 6720), 1, 1.8, BLACK, 9, sfx="wood_high")
L(join(circle(2380, 6480, 40), arrow((2380, 6530), (2380, 6600), 0.0, 24)), 2, 2.4, GREEN, 8, sfx="ding")
strike("每月存 2000", 2830, 6300, 72, 3)
T("剩多少存多少", 2830, 6470, 64, k0=4, sfx="pop")
T("月底：0", 2830, 6640, 80, RED, k0=5, k1=5.6, sfx="tom")

scene("讲故事改成周末讲", "例子 · 陪孩子", (950, 7940, 0.85))
L(stick(560, 8190, 0.8), 0, 0.6, sfx="wood_high")
L(stick(770, 8190, 0.5, "up"), 0.6, 1.0, BLUE)
T("每晚讲个故事", 1120, 7500, 66, k0=1, sfx="pop")
L(book(1250, 7840, 230, 150), 2, 2.6, sfx="wood_high")
strike("每晚讲个故事", 1120, 7500, 66, 3)
T("周末讲一个", 1120, 7620, 62, RED, k0=3.4, k1=4.3)
L(bubble(430, 7750, 240, 110, 1), 5, 5.3, sfx="wood_high")
T("明天吧", 430, 7750, 50, k0=5.3, k1=5.8)

scene("查三遍变成能交就行", "例子 · 交稿", (2650, 7940, 0.85))
T("检查 3 遍才交", 2650, 7500, 66, k0=0, sfx="pop")
DOCS = [(2390, 7800), (2610, 7800), (2830, 7800)]
L(join(*[doc(x, y) for x, y in DOCS]), 1, 1.7, BLACK, 8, sfx="wood_high")
L(join(*[check(x + 40, y + 140, 30) for x, y in DOCS]), 2, 2.5, GREEN, 8, sfx="ding")
L(join(cross(2610, 7800, 80), cross(2830, 7800, 80)), 3, 3.5, RED, 11, sfx="rim")
T("能交就行", 2650, 8060, 76, RED, k0=4, sfx="pop")
L(stick(3150, 8200, 0.6, "shrug"), 5, 5.5, BLUE, sfx="wood_high")

scene("都在跟上次比", "身边的例子", (1800, 7200, 0.34), shake=[2])
T("回头一看：差好远", 1800, 8380, 100, k0=0, k1=1.4, sfx="pop")
T("跟上次比", 1800, 7200, 140, RED, k0=2, k1=2.5, sfx="kick")
for n, (x, y) in enumerate(CARDS):
    L(arrow((1800 + (x - 1800) * 0.2, 7200 + (y - 7200) * 0.25), (1800 + (x - 1800) * 0.55, 7200 + (y - 7200) * 0.55),
            0.1, 40), 3 + n * 0.6, 3.4 + n * 0.6, RED, 9, sfx="wood_high" if n % 2 == 0 else None)

# ---------------------------------------------------------------- 具体做法（场景 16–19）

Y1, Y2 = 9250, 10430          # 两排做法卡的中心高度
SOL = [(950, Y1), (2650, Y1), (950, Y2), (2650, Y2)]
scene("先把底线写下来", "第一招 · 写下底线", (950, Y1 + 110, 0.85))
L(rect(*SOL[0], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("① 写下底线", 950, Y1 - 300, 80, BLUE, k0=1, sfx="pop")
L(rect(950, Y1 + 10, 760, 240, 20), 2, 2.5, BLACK, 8, sfx="wood_high")
T("底线：", 670, Y1 + 10, 56, RED, k0=2.6, k1=3.0)
T("每周至少跑 3 次", 1020, Y1 + 10, 56, k0=3, k1=4.0, sfx="pop")
L(check(1420, Y1, 40), 4, 4.3, GREEN, 10, sfx="ding")
T("累了跑慢点，次数不变", 950, Y1 + 260, 58, k0=4.6, k1=5.9)

scene("跟最好的那次比", "第二招 · 看最好的", (2650, Y1 + 110, 0.85))
L(rect(*SOL[1], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("② 跟最好的比", 2650, Y1 - 300, 80, BLUE, k0=1, sfx="pop")
L(bars(2250, Y1 + 250, (200, 280, 380, 250, 220)), 2, 2.8, BLACK, 8, sfx="wood_high")
L(scribble(2595, Y1 + 60, 70, 360, 9), 3, 3.4, RED, 6, sfx="ding")
T("最好：5公里", 2595, Y1 - 200, 56, RED, k0=3.4, k1=4.0)
L(dashed(2200, 3000, Y1 - 130), 4, 4.6, RED, 7, sfx="rim")
T("目标线", 3120, Y1 - 130, 54, RED, k0=5, k1=5.5, sfx="pop")

scene("做到的也记一笔", "第三招 · 好事也记", (950, Y2 + 110, 0.85))
L(rect(*SOL[2], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("③ 好事也记下", 950, Y2 - 300, 80, BLUE, k0=1, sfx="pop")
L(join(rect(950, Y2 + 40, 700, 380, 18), *[circle(700 + n * 125, Y2 - 150, 16) for n in range(5)]), 2, 2.6, BLACK, 8,
  sfx="wood_high")
T("周五：", 720, Y2 - 80, 52, k0=2.6, k1=3.0)
for n, w in enumerate(("跑了 3 次", "早睡 2 天", "读完 1 章")):
    T(w, 990, Y2 + n * 85, 52, k0=3 + n, k1=3.6 + n, sfx="pop")
    L(check(1210, Y2 - 5 + n * 85, 26), 3.65 + n, 3.9 + n, GREEN, 8)

scene("月底回看，降了就调回", "第四招 · 月底回看", (2650, Y2 + 110, 0.85))
L(rect(*SOL[3], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("④ 月底回看", 2650, Y2 - 300, 80, BLUE, k0=1, sfx="pop")
L(calendar(2270, Y2 + 30), 2, 2.6, BLACK, 7, sfx="wood_high")
L(circle(2360, Y2 + 125, 34), 2.6, 2.9, RED, 8)
T("1月：每周 4 次", 2890, Y2 - 50, 54, k0=3, k1=3.8, sfx="pop")
T("10月：每周 2 次", 2890, Y2 + 70, 54, RED, k0=4, k1=4.8, sfx="pop")
L(arrow((3200, Y2 + 310), (3200, Y2 + 10), 0.0, 40), 5, 5.4, GREEN, 10, sfx="tom")
T("下月调回 4 次", 2890, Y2 + 240, 56, GREEN, k0=5.4, k1=6.0)

scene("底线定了别往下调", "一句话", (1800, 6000, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 11850, 0.8))
H(0, "cymbal", 0.5)
T("你哪个标准在悄悄降？", 1800, 11760, 80, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：为什么越熬夜越离不开咖啡？", 1800, 11920, 50, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")


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
