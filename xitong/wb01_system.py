"""01 系统是什么（白板手绘版）：换了三份工作，烦心事怎么都一样？

叙事：打工人切身问题开局（换工作、换老板、换同事，加班照旧）→ 书中观点（弹簧演示；要素、连接、目标；
换要素效果最小，改目标全盘变化）→ 身边的例子（客服按单数考核、外卖超时扣钱、末位淘汰、孩子考满分有奖励）→
具体做法（画出来 / 看钱和时间花在哪 / 改规则 / 跳槽前问三句）→ 评论区互动。
书中观点为转述（Meadows, Thinking in Systems, 2008；中译本《系统之美》，邱昭良译，浙江人民出版社 2012）；
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, building, check, circle, clock, cross,
                               doc, face, hands_at, join, light, marker, node, partial, podium_list, rect, scooter,
                               scribble, spring_path, stick, target, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#2F62B8"
SQUARE_SHOT = 16

b = Board(size=(3600, 8600))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


# ---------------------------------------------------------------- 动态元件

def spring_fn(x, top, j_hold, j_release):
    """弹簧：j_hold 镜头逐段画出并被手提着；j_release 镜头第 0 拍松手，衰减振荡。"""

    def fn(c, k, t):
        rel = b.t_of(j_release, 0)
        length = 360
        if t >= rel:
            dt = t - rel
            length = 360 + 200 * math.sin(dt * 9) * math.exp(-dt * 1.5)
            for jj in range(3):
                yy = top + length + 40 + jj * 26
                c.drawPath(P((x - 90 + jj * 20, yy), (x + 90 - jj * 20, yy)), marker(BLUE, 5, 0.6 * math.exp(-dt * 1.5)))
        kk = clamp01((t - b.t_of(j_hold, 0)) / (b.t_of(j_hold, 2.0) - b.t_of(j_hold, 0)))
        part, tip = partial(spring_path(x, top, length), kk)
        c.drawPath(part, marker(BLACK, 9))
        handp = join(P((x - 70, top - 10), (x + 70, top - 10)), circle(x, top - 70, 55))
        if t < rel:
            c.drawPath(partial(handp, clamp01(kk * 3))[0], marker(BLACK, 9))
        else:
            up = ease_out(clamp01((t - rel) / 0.3)) * 200
            c.drawPath(circle(x, top - 70 - up, 55), marker(BLACK, 9, 0.35))
        return tip if kk < 1 else None

    return fn


def fill_red_lamp(x, y):
    def fn(c, k, t):
        K.dot(c, x, y - 65, 28 * k, RED)
        return None

    return fn


# ---------------------------------------------------------------- 开局：打工人的老问题（镜头 1–6）

b.shot("换了三份工作", "灵魂拷问", view=(1000, 820, 0.62))
for n, x in enumerate((450, 1000, 1550)):
    L(building(x, 1000), n, n + 0.8, sfx="wood_high")
    T(("第一家", "第二家", "第三家")[n], x, 1070, 54, k0=n + 0.4)
for a, c_ in ((450, 1000), (1000, 1550)):
    L(arrow((a + 150, 560), (c_ - 150, 560), 0.25), 2.9 if a == 1000 else 1.6, 3.4 if a == 1000 else 2.1, GREEN, 8)

b.shot("烦心事一模一样", "灵魂拷问", view=(1000, 980, 0.62))
for n, x in enumerate((450, 1000, 1550)):
    for m, w in enumerate(("加班", "甩锅", "开会")):
        T(w, x, 1170 + m * 85, 54, RED, k0=n * 1.0 + m * 0.25, k1=n * 1.0 + m * 0.25 + 0.3, sfx="pop" if m == 0 else None)

b.shot("老板换了", "灵魂拷问", view=(2700, 900, 0.8))
L(stick(2350, 1100, 0.85, "point", tie=True), 0, 0.6, sfx="wood_high")
L(face(2350, 1100, 0.85, "flat"), 0.6, 0.75)
L(cross(2350, 900, 110), 1, 1.35, RED, 12, sfx="rim")
L(stick(2600, 1100, 0.85, "down", tie=True), 2, 2.6, BLUE, sfx="pop")
L(face(2600, 1100, 0.85, "smile"), 2.6, 2.75, BLUE)
T("新老板", 2600, 720, 56, BLUE, k0=2.8)

b.shot("同事也换了", "灵魂拷问", view=(2900, 950, 0.8))
for n, x in enumerate((2850, 3030, 3210)):
    L(stick(x, 1100, 0.55), n * 0.25, n * 0.25 + 0.5, sfx="wood_high" if n == 0 else None)
L(scribble(3030, 1000, 500, 220, 9), 1, 1.6, RED, 9, sfx="shaker")
for n, x in enumerate((2850, 3030, 3210)):
    L(stick(x, 1450, 0.55), 2 + n * 0.25, 2.5 + n * 0.25, BLUE, sfx="pop" if n == 0 else None)
T("新同事", 3030, 1520, 50, BLUE, k0=3.1)

b.shot("照样加班到十点", "灵魂拷问", view=(2700, 1550, 0.85))
L(clock(2450, 1650, 180), 0, 0.8, sfx="wood_low")
L(hands_at(2450, 1650, 180, 10, 0), 1, 1.3, RED, 12, sfx="rim")
T("晚上十点", 2900, 1560, 70, RED, k0=1.6)
T("还在工位", 2900, 1700, 70, k0=2.4, sfx=None)
b.hit(len(b.shots) - 1, 2, "pop")

b.shot("毛病出在哪？", "灵魂拷问", view=(1800, 1300, 0.42), flashes=[2])
T("？", 1800, 1900, 420, RED, k0=0, k1=0.6, sfx="kick")
T("毛病出在哪", 1800, 2200, 110, k0=1.0, k1=2.0, sfx="pop")
b.hit(len(b.shots) - 1, 2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书专讲这个", "系统之美", view=(1050, 2700, 0.9))
L(book(750, 2700, 420, 280), 0, 1.0, sfx="wood_low")
T("系统之美", 750, 2460, 80, GREEN, k0=1.0, sfx="pop")
T("德内拉 · 梅多斯", 750, 2930, 46, k0=2.0, sfx="pop")

j_hold = b.shot("作者拿出一根弹簧", "书中例子 · 弹簧玩具", view=(1150, 2650, 0.9))
j_rel = j_hold + 1
b.custom(j_hold, 0, 12, spring_fn(1400, 2450, j_hold, j_rel), sfx="pop")
T("弹簧玩具", 1650, 2420, 56, k0=2.0, sfx="wood_high")

b.shot("手一松，它自己弹", "书中例子 · 弹簧玩具", view=(1250, 2700, 0.9), shake=[0], flashes=[0])
b.hit(j_rel, 0, "kick", 1.0, "松手")
T("自己弹！", 1750, 2800, 80, RED, k0=1.0, sfx="tom")
b.hit(j_rel, 2, "tom", 0.7)

b.shot("怎么弹，弹簧说了算", "书中观点", view=(1050, 3000, 0.85))
T("弹法藏在它的结构里", 1050, 3200, 84, RED, k0=0, k1=1.6, sfx="pop")
L(underline(560, 1540, 3260), 2, 2.6, RED, 8, sfx="ding")

b.shot("公司也是这样", "书中观点 · 系统", view=(2700, 2800, 0.78))
T("公司 = 一个系统", 2700, 2280, 84, k0=0, sfx="pop")
L(rect(2700, 2830, 1150, 1000, 40), 1.6, 2.8, GREEN, 8, sfx="wood_high")
b.hit(len(b.shots) - 1, 2, "wood_high", 0.5)

NODES = [("员工", 2370, 2560), ("主管", 3030, 2560), ("客户", 2370, 3110), ("老板", 3030, 3110)]
b.shot("人是要素", "书中观点 · 要素", view=(2700, 2830, 0.78))
for n, (w, x, y) in enumerate(NODES):
    L(node(x, y, 85), n * 0.7, n * 0.7 + 0.4, sfx="pop" if n < 3 else None)
    T(w, x, y, 50, k0=n * 0.7 + 0.35, k1=n * 0.7 + 0.6)

b.shot("流程和关系是连接", "书中观点 · 连接", view=(2700, 2830, 0.78))
for n, (a, c_) in enumerate(((0, 1), (1, 3), (3, 2), (2, 0))):
    (_, x0, y0), (_, x1, y1) = NODES[a], NODES[c_]
    dx, dy = x1 - x0, y1 - y0
    d = math.hypot(dx, dy)
    L(arrow((x0 + dx / d * 100, y0 + dy / d * 100), (x1 - dx / d * 100, y1 - dy / d * 100), 0.12, 40), n * 0.8,
      n * 0.8 + 0.6, BLACK, 8, sfx="wood_high" if n % 2 == 0 else None)

b.shot("考核是目标", "书中观点 · 目标", view=(2700, 2830, 0.78))
L(target(2700, 2835, 110), 0, 0.8, RED, 10, sfx="kick")
T("考核", 2700, 3010, 60, RED, k0=1.0, sfx="ding")

b.shot("人换得最勤", "书中观点 · 换要素", view=(2700, 2830, 0.78))
for n, (w, x, y) in enumerate(NODES):
    L(scribble(x, y, 170, 170, 7), n * 0.3, n * 0.3 + 0.35, RED, 7, sfx="shaker" if n == 0 else None)
for n, (w, x, y) in enumerate(NODES):
    L(node(x + 150, y - 120, 55), 2 + n * 0.3, 2.3 + n * 0.3, BLUE, 8, sfx="pop" if n == 0 else None)

b.shot("效果却最小", "书中观点 · 换要素", view=(2700, 3050, 0.78))
T("效果：很小", 2700, 3480, 76, k0=0, sfx="pop")
L(P((2420, 3560), (2980, 3560)), 1.2, 1.6, BLACK, 6)
b.hit(len(b.shots) - 1, 2, "wood_low")

b.shot("考核一改，全变了", "书中观点 · 改目标", view=(2700, 2830, 0.78), shake=[1])
L(cross(2700, 3010, 70), 0, 0.4, RED, 12, sfx="rim")
T("交付", 2700, 3150, 72, RED, k0=1.0, k1=1.4, sfx="kick")
for n, (a, c_) in enumerate(((0, 3), (1, 2))):
    (_, x0, y0), (_, x1, y1) = NODES[a], NODES[c_]
    L(arrow((x0, y0), (x1, y1), 0.3, 40), 2 + n * 0.6, 2.6 + n * 0.6, RED, 9, sfx="wood_high" if n == 0 else None)

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 4300), (2650, 4300), (950, 5300), (2650, 5300)]
b.shot("身边就有例子", "身边的例子", view=(1800, 4650, 0.42))
T("身边的例子", 1800, 3720, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("客服只按单数算", "例子 · 只算单数", view=(950, 4300, 0.85))
L(stick(600, 4650, 0.8, "hold"), 0, 0.6, sfx="wood_high")
for n in range(4):
    L(doc(1050 + n * 60, 4300 - n * 40), 0.8 + n * 0.25, 1.05 + n * 0.25)
T("考核：单数", 950, 3970, 70, RED, k0=2.0, sfx="pop")

b.shot("难缠的单没人接", "例子 · 只算单数", view=(950, 4300, 0.85))
L(doc(1350, 4500, 190, 230), 0, 0.5, sfx="wood_high")
T("难", 1350, 4500, 90, RED, k0=0.5, k1=0.8)
L(cross(1350, 4500, 120), 1, 1.35, RED, 12, sfx="rim")
L(stick(600, 4650, 0.8, "shrug"), 2, 2.6, BLUE, sfx="pop")

b.shot("外卖超时就扣钱", "例子 · 超时扣钱", view=(2650, 4300, 0.85))
L(scooter(2600, 4650, 1.1), 0, 0.9, sfx="wood_high")
L(clock(3050, 4050, 110), 1, 1.5, sfx="pop")
L(hands_at(3050, 4050, 110, 12, 10), 1.5, 1.7, RED, 9)
T("超时 扣钱", 2650, 3970, 70, RED, k0=2.0, sfx="rim")

b.shot("骑手只能拼命赶", "例子 · 超时扣钱", view=(2650, 4300, 0.85))
for n in range(4):
    L(P((2250 - n * 30, 4450 + n * 45), (2040 - n * 30, 4450 + n * 45)), n * 0.15, n * 0.15 + 0.3, BLUE, 7,
      sfx="shaker" if n == 0 else None)
L(light(3150, 4420), 1, 1.8, sfx="wood_high")
b.custom(len(b.shots) - 1, 2, 2.4, fill_red_lamp(3150, 4420), sfx="rim")

b.shot("末位淘汰", "例子 · 末位淘汰", view=(950, 5300, 0.85))
L(podium_list(950, 5050, 4), 0, 1.2, sfx="wood_high")
for n in range(4):
    T(("老张", "小李", "阿美", "小王")[n], 950, 5050 + n * 96, 46, k0=0.6 + n * 0.2, k1=0.8 + n * 0.2)
L(cross(950, 5338, 60), 2, 2.3, RED, 10, sfx="rim")

b.shot("同事不再互相帮", "例子 · 末位淘汰", view=(950, 5400, 0.85))
L(stick(650, 5750, 0.65), 0, 0.5, sfx="wood_high")
L(stick(1250, 5750, 0.65), 0.3, 0.8)
L(arrow((760, 5500), (1140, 5500), 0.1, 36), 1, 1.4, GREEN, 8, sfx="pop")
L(cross(950, 5500, 60), 2, 2.3, RED, 10, sfx="rim")

b.shot("考满分给奖励", "例子 · 满分有奖", view=(2650, 5300, 0.85))
L(stick(2300, 5650, 0.6, "up"), 0, 0.5, sfx="wood_high")
T("100分", 2650, 5050, 110, RED, k0=1.0, sfx="pop")
L(join(rect(3050, 5450, 220, 180, 12), P((3050, 5360), (3050, 5540)), P((2940, 5450), (3160, 5450))), 2, 2.6, GREEN,
  sfx="ding")

b.shot("孩子只盯着分数", "例子 · 满分有奖", view=(2650, 5350, 0.85))
for n, w in enumerate(("兴趣", "运动", "朋友")):
    T(w, 2700 + n * 170, 5700, 54, k0=n * 0.3, k1=n * 0.3 + 0.3, sfx="pop" if n == 0 else None)
L(P((2560, 5700), (3170, 5700)), 1.5, 1.9, RED, 8, sfx="rim")
L(arrow((2380, 5300), (2550, 5120), 0.1, 34), 2.6, 3.0, RED, 8)

b.shot("人还是那些人", "身边的例子", view=(1800, 4800, 0.42))
T("人还是那些人", 1800, 5880, 110, k0=0, sfx="pop")
b.hit(len(b.shots) - 1, 2, "wood_low")

b.shot("考核在推着人走", "身边的例子", view=(1800, 4800, 0.42), shake=[0])
T("考核", 1800, 4800, 150, RED, k0=0, k1=0.5, sfx="kick")
for n, (x, y) in enumerate(CARDS):
    L(arrow((1800 + (x - 1800) * 0.12, 4800 + (y - 4800) * 0.2), (1800 + (x - 1800) * 0.55, 4800 + (y - 4800) * 0.55),
            0.1, 40), 1 + n * 0.5, 1.4 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 6750), (2650, 6750), (950, 7650), (2650, 7650)]
b.shot("碰到老问题怎么办", "具体做法", view=(1800, 7100, 0.42))
T("碰到老问题，这样做", 1800, 6230, 110, k0=0, k1=1.6, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1500, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先把它画出来", "第一步 · 画出来", view=(950, 6750, 0.85))
T("① 画出来", 950, 6450, 80, BLUE, k0=0, sfx="pop")
pts = [(700, 6700), (1200, 6700), (950, 6950)]
for n, (x, y) in enumerate(pts):
    L(node(x, y, 55), 1 + n * 0.3, 1.25 + n * 0.3, sfx="wood_high" if n == 0 else None)
L(join(P(pts[0], pts[1]), P(pts[1], pts[2]), P(pts[2], pts[0])), 2.2, 2.9, BLACK, 6, sfx="wood_high")

b.shot("谁拍板，按啥考核", "第一步 · 画出来", view=(950, 6850, 0.85))
for n, w in enumerate(("谁和谁有关", "谁拍板", "按什么考核")):
    T(w, 1250, 6880 + n * 90, 52, RED if n == 2 else BLACK, k0=n * 1.0, sfx="pop")

b.shot("再看钱和时间", "第二步 · 看去向", view=(2650, 6750, 0.85))
T("② 看钱和时间", 2650, 6450, 80, BLUE, k0=0, sfx="pop")
T("¥", 2400, 6720, 160, GREEN, k0=1.0, k1=1.3, sfx="pop")
L(clock(2900, 6720, 100), 2, 2.6, sfx="wood_high")

b.shot("花在哪，就是目标", "第二步 · 看去向", view=(2650, 6850, 0.85))
L(join(arrow((2400, 6830), (2600, 7000), 0.1, 34), arrow((2900, 6840), (2700, 7000), -0.1, 34)), 0, 0.8, BLACK, 8,
  sfx="wood_high")
T("真目标", 2650, 7080, 90, RED, k0=1.0, sfx="pop")
L(underline(2500, 2800, 7140), 2, 2.5, RED, 8, sfx="ding")

b.shot("能改规则就改规则", "第三步 · 改规则", view=(950, 7650, 0.85))
T("③ 改规则", 950, 7350, 80, BLUE, k0=0, sfx="pop")
T("按工时算", 950, 7560, 66, k0=1.0, sfx="pop")
L(P((790, 7560), (1110, 7560)), 2, 2.4, RED, 10, sfx="rim")

b.shot("按工时改成按交付", "第三步 · 改规则", view=(950, 7650, 0.85))
T("按交付算", 950, 7690, 66, RED, k0=0, sfx="pop")
L(check(1230, 7680, 45), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("抢单改成轮值", "第三步 · 改规则", view=(950, 7750, 0.85))
T("抢单", 780, 7880, 62, k0=0, sfx="pop")
L(P((710, 7880), (850, 7880)), 1, 1.3, RED, 10, sfx="rim")
T("→ 轮值", 1080, 7880, 62, RED, k0=2.0, sfx="pop")

b.shot("跳槽前问三句", "第四步 · 跳槽前", view=(2650, 7650, 0.85))
T("④ 跳槽前问三句", 2650, 7350, 76, BLUE, k0=0, k1=1.4, sfx="pop")
L(stick(2250, 7980, 0.6, "point"), 2, 2.6, sfx="wood_high")

for n, w in enumerate(("怎么考核？", "谁定先后？", "出错谁担？")):
    b.shot(w, "第四步 · 跳槽前", view=(2650, 7700, 0.85))
    T(w, 2780, 7520 + n * 150, 70, k0=0, sfx="pop")
    L(check(3130, 7515 + n * 150, 40), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("先看结构，再看人", "一句话", view=(1800, 4600, 0.235))
b.hit(len(b.shots) - 1, 0, "cymbal", 0.5)
b.hit(len(b.shots) - 1, 2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 8350, 0.8))
T("你被哪种考核坑过？", 1800, 8260, 80, RED, k0=0.5, k1=1.8)
T("下一讲：工资涨了，为什么还是存不下钱？", 1800, 8420, 42, k0=2.0, k1=3.2)
b.hit(len(b.shots) - 1, 0, "cymbal", 0.5)
b.hit(len(b.shots) - 1, 1, "pop")
b.hit(len(b.shots) - 1, 2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "system", "系统是什么", "换了三份工作，烦心事怎么都一样？", ACC, b.shots,
                 [f"{BOOK}第一章（转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                 "换了三份工作|烦心事【一模一样】", 16,
                 ["书中观点均为转述：系统由要素、连接、功能或目标组成；开篇弹簧玩具演示行为来自结构；改变要素通常影响最小，"
                  "改变连接与目标影响更大；系统目标要从行为推断。出处：Donella H. Meadows, Thinking in Systems: A Primer "
                  "(2008)，中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                  "客服按单数考核、外卖超时扣钱、末位淘汰、孩子考满分有奖励均为现实场景示意，不指向任何具体公司或个人；"
                  "四步做法为据书中思路整理的建议。"],
                 tags="#打工人")
    return b.attach(ep)
