"""10 杠杆点（白板手绘版）：想改变，该从哪里下手？（系列最后一讲）

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
叙事：打工人切身问题开局（周一想重新开始：买新本子、下打卡软件、闹钟调早，一个月后照旧）→ 书中观点（撬棍演示
小力气撬大石头；十二个杠杆点画成一架梯子，只点出几级：最下面是数字、往上是信息、规则、目标、心智模式，越往上越有力；
找对了位置也常常推反方向）→ 身边的例子（项目延期只会加班、存钱只少喝奶茶、孩子玩手机只砍时间、业绩差就加指标）→
具体做法（摆到眼前 / 改规则 / 问目标 / 先试一周，推反了就掉头）→ 系列收尾：评论区问题 + 这一季讲完了。
书中观点为转述（Donella H. Meadows, Leverage Points: Places to Intervene in a System, 1999；《系统之美》中亦有收录与展开，
中译本邱昭良译，浙江人民出版社 2012）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, clock, cross, face,
                               hands_at, join, marker, partial, rect, stick, underline)
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#B8322A"
SQUARE_SHOT = 4

b = Board(size=(3600, 10000))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲小画法

def phone(x, y, w=200, h=340):
    return join(rect(x, y, w, h, 30), P((x - 30, y + h / 2 - 30), (x + 30, y + h / 2 - 30)))


def calendar(x, y, w=300, h=280):
    top = y - h / 2 + 70
    parts = [rect(x, y, w, h, 20), P((x - w / 2, top), (x + w / 2, top)),
             P((x - w / 4, y - h / 2 - 25), (x - w / 4, y - h / 2 + 25)),
             P((x + w / 4, y - h / 2 - 25), (x + w / 4, y - h / 2 + 25))]
    for r in range(2):
        for cc in range(3):
            parts.append(circle(x - w / 3 + cc * w / 3, top + 60 + r * 80, 10))
    return join(*parts)


def cup(x, y, w=150, h=220):
    return join(P((x - w / 2, y - h / 2), (x - w * 0.35, y + h / 2), (x + w * 0.35, y + h / 2), (x + w / 2, y - h / 2),
                  close=True),
                P((x - w / 2 - 10, y - h / 2 + 30), (x + w / 2 + 10, y - h / 2 + 30)),
                P((x + 15, y - h / 2), (x + 45, y - h / 2 - 90)),
                circle(x - 20, y + 50, 10), circle(x + 15, y + 70, 10), circle(x - 5, y + 20, 10))


def house(x, y, w=260, h=200):
    return join(P((x - w / 2 - 30, y - h / 2), (x, y - h / 2 - 140), (x + w / 2 + 30, y - h / 2)),
                rect(x, y, w, h, 6), rect(x, y + h / 2 - 55, 60, 110, 4))


def bars(x, y, hs, w=70, gap=40):
    """柱状图：(x, y) 为底边中点，hs 为各柱高度。"""
    n = len(hs)
    x0 = x - (n * w + (n - 1) * gap) / 2
    parts = [P((x0 - 30, y), (x0 + n * w + (n - 1) * gap + 30, y))]
    for i, h in enumerate(hs):
        xl = x0 + i * (w + gap)
        parts.append(P((xl, y), (xl, y - h), (xl + w, y - h), (xl + w, y)))
    return join(*parts)


def knob(x, y, r=55):
    return join(circle(x, y, r), P((x, y), (x, y - r + 12)))


def rock(x, y, r=100):
    pts = [(x + r * (1 + 0.12 * math.sin(i * 2.3)) * math.cos(i * math.pi / 5),
            y + r * 0.85 * (1 + 0.12 * math.sin(i * 2.3)) * math.sin(i * math.pi / 5)) for i in range(10)]
    return P(*pts, close=True)


# ---------------------------------------------------------------- 撬棍（场景 4 画出，场景 5 压下，场景 9 推反）

LV_X, LV_Y, GROUND = 2550, 3110, 3200        # 支点顶端与地面
ARM_L, ARM_R, TH0 = 450, 400, 0.2
PUSHER_X = 2013                              # 压撬棍的小人：右手落在撬棍左端


def lever_fn(j_draw, j_push, j_back):
    def theta(t):
        push = b.t_of(j_push, 0)
        back = b.t_of(j_back, 1)
        th = TH0
        if t >= push:
            th = TH0 - 2 * TH0 * ease_out(clamp01((t - push) / 0.3))
        if t >= back:
            th = -TH0 + 2 * TH0 * ease_out(clamp01((t - back) / 0.35))
        return th

    def fn(c, k, t):
        th = theta(t)
        cs, sn = math.cos(th), math.sin(th)
        left = (LV_X - ARM_L * cs, LV_Y - ARM_L * sn)
        right = (LV_X + ARM_R * cs, LV_Y + ARM_R * sn)
        plank = join(P(left, right), P((left[0], left[1] - 16), (right[0], right[1] - 16)))
        path = join(plank, rock(right[0] + 10, right[1] - 108))
        part, tip = partial(path, k)
        c.drawPath(part, marker(BLACK, 10))
        return tip if k < 1 else None

    return fn


# ---------------------------------------------------------------- 梯子（十二个杠杆点）

R_L, R_R, R_TOP, R_BOT = 1000, 1250, 3800, 4650
LAB_X = 1520


def rung_y(level):
    return R_TOP + (level - 0.5) * (R_BOT - R_TOP) / 12


def level_mark(level, word, k=0):
    """高亮一级：红线描在这一级上（第 k 拍）+ 右侧写出名字（第 k+1 拍）+ 细线连过去。"""
    y = rung_y(level)
    L(P((R_L, y), (R_R, y)), k, k + 0.4, RED, 14, sfx="wood_high")
    w1 = k + 1 + max(0.5, 0.18 * len(word))
    T(word, LAB_X, y + 18, 56, RED, k0=k + 1, k1=w1, sfx="pop")
    L(P((R_R + 30, y), (LAB_X - 28 * len(word) - 30, y)), w1 + 0.05, w1 + 0.35, RED, 5)


# ---------------------------------------------------------------- 开局：想改变，总是没变（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


CLOCK = (1000, 1600)
scene("周一，重新开始", "灵魂拷问", (900, 1270, 0.8))
L(stick(650, 1250, 0.9, "up"), 0, 0.6, sfx="wood_high")
L(face(650, 1250, 0.9, "smile"), 0.6, 0.75)
T("周一", 1100, 820, 80, k0=1, sfx="pop")
T("重新开始！", 1100, 960, 70, RED, k0=2, sfx="pop")
L(clock(*CLOCK, 170), 3, 3.8, sfx="wood_low")
L(hands_at(*CLOCK, 170, 6, 30), 4, 4.3, RED, 12, sfx="rim")
T("早半小时", 520, 1600, 70, RED, k0=5, sfx="pop")

scene("买新本子，下打卡软件", "灵魂拷问", (2600, 1000, 0.85))
L(book(2300, 950, 380, 250), 0, 0.9, sfx="wood_high")
T("新本子", 2300, 1200, 64, k0=1, sfx="pop")
L(underline(2180, 2420, 1250, 10, 30), 1.6, 2.0, GREEN, 6)
L(phone(2900, 950), 2, 2.6, sfx="wood_high")
for n in range(3):
    L(check(2900, 860 + n * 80, 28), 3 + n * 0.25, 3.2 + n * 0.25, GREEN, 7, sfx="pop" if n == 0 else None)
T("打卡软件", 2900, 1200, 60, k0=4, sfx="pop")

scene("照旧了，该从哪下手？", "灵魂拷问", (1800, 1150, 0.42), shake=[4], flashes=[4])
T("一个月后：照旧", 2600, 450, 110, k0=0, k1=1.0, sfx="pop")
for n, (x, y) in enumerate(((2300, 950), (2900, 950), CLOCK)):
    L(cross(x, y, 150), 1 + n, 1.35 + n, RED, 14, sfx="rim")
T("？", 1800, 700, 340, RED, k0=4, k1=4.6, sfx="kick")
T("从哪下手", 1800, 1150, 130, k0=5, k1=5.8, sfx="pop")

# ---------------------------------------------------------------- 书中例子：撬棍（场景 4–5，场景 5 是音乐 drop）

LEVER_VIEW = (2210, 2900, 0.53)
j_draw = scene("小力气，撬大石头", "杠杆点 · 书中例子", LEVER_VIEW)
j_push, j_back = j_draw + 1, j_draw + 5
L(book(1450, 2900, 380, 260), 0, 0.8, sfx="wood_low")
T("杠杆点", 1450, 2680, 80, GREEN, k0=1, sfx="pop")
T("梅多斯 · 1999", 1450, 3110, 46, k0=1.55, k1=1.95)
L(P((1900, GROUND), (3150, GROUND)), 2, 2.4, BLACK, 8, sfx="wood_high")
L(P((LV_X, LV_Y), (LV_X - 70, GROUND), (LV_X + 70, GROUND), close=True), 2.45, 2.85)
b.custom(j_draw, 3, 4.2, lever_fn(j_draw, j_push, j_back), sfx="pop")
L(stick(PUSHER_X, GROUND, 0.8, "point"), 4.3, 4.9)
T("大石头", 2960, 3300, 56, k0=5, sfx="wood_low")

scene("手一压，石头起来", "书中例子 · 撬棍", LEVER_VIEW, shake=[0], flashes=[0])
b.hit(j_push, 0, "kick", 1.0, "压下")
L(arrow((2090, 2780), (2090, 2960), 0, 50), 0, 0.3, BLUE, 12)
T("撬起来！", 2600, 2620, 90, RED, k0=1, sfx="tom")
T("小力气", PUSHER_X, 3300, 56, BLUE, k0=2, sfx="pop")

# ---------------------------------------------------------------- 书中观点：十二个杠杆点（场景 6–9）

LADDER = (1200, 4370, 0.85)
scene("梯子十二级，数字垫底", "书中观点 · 十二个杠杆点", LADDER)
L(join(P((R_L, R_TOP - 10), (R_L, R_BOT + 40)), P((R_R, R_TOP - 10), (R_R, R_BOT + 40))), 0, 0.6, sfx="wood_high")
L(join(*[P((R_L, rung_y(lv)), (R_R, rung_y(lv))) for lv in range(12, 0, -1)]), 1, 2, BLACK, 7, sfx="pop")
T("12", 920, rung_y(12) + 16, 50, k0=2.1, k1=2.4)
T("1", 920, rung_y(1) + 16, 50, k0=2.5, k1=2.8)
L(P((R_L, rung_y(12)), (R_R, rung_y(12))), 3, 3.4, RED, 14, sfx="wood_high")
T("数字", LAB_X, rung_y(12) + 18, 56, RED, k0=4, sfx="pop")
L(P((R_R + 30, rung_y(12)), (LAB_X - 86, rung_y(12))), 4.55, 4.85, RED, 5)
T("最弱", LAB_X + 200, rung_y(12) + 18, 56, RED, k0=5, sfx="rim")
L(underline(LAB_X + 140, LAB_X + 260, rung_y(12) + 55, 8, 24), 5.55, 5.95, RED, 6)

scene("往上：信息和规则", "十二个杠杆点 · 信息与规则", LADDER)
level_mark(6, "信息", 0)
level_mark(5, "规则", 3)

scene("再往上：目标和看法", "十二个杠杆点 · 目标与心智模式", LADDER, flashes=[4])
level_mark(3, "目标", 0)
level_mark(2, "心智模式", 2)
L(arrow((700, R_BOT - 50), (700, R_TOP + 150), 0, 50), 4, 4.6, RED, 12, sfx="ding")
T("越有力", 700, R_TOP + 80, 60, RED, k0=5, sfx="pop")

scene("找对了，却推反了", "书中观点 · 推反方向", LEVER_VIEW, shake=[1])
L(cross(2600, 2600, 90), 0, 0.35, RED, 12, sfx="rim")
b.hit(j_back, 1, "tom", 0.9, "石头落回")
L(arrow((3140, 2900), (3140, 3130), 0, 40), 1, 1.3, RED, 10)
T("推反了", 2600, 2470, 70, RED, k0=2, sfx="pop")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 5600), (2650, 5600), (950, 6600), (2650, 6600)]
WIDE = (1800, 6050, 0.42)
scene("身边就有例子", "身边的例子", WIDE)
T("身边的例子", 1800, 4990, 100, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), 2 + n * 0.5, 2.45 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (0, 2) else None)

scene("项目延期，就加班", "例子 · 项目延期", (900, 5600, 0.85))
L(calendar(700, 5550), 0, 0.9, sfx="wood_high")
T("延期", 1200, 5500, 90, RED, k0=1, sfx="pop")
L(rect(1200, 5470, 220, 130, 16), 2, 2.4, RED, 8, sfx="rim")
for n, x in enumerate((640, 800, 960)):
    L(stick(x, 6000, 0.5, "hold"), 3 + n * 0.25, 3.45 + n * 0.25, sfx="wood_high" if n == 0 else None)
T("每天 +2 小时", 1270, 5760, 60, k0=4, k1=4.8, sfx="pop")
T("第12级", 1300, 5860, 56, RED, k0=5, sfx="rim")

scene("想存钱，只少喝奶茶", "例子 · 存钱", (2700, 5600, 0.85))
L(rect(2400, 5650, 260, 300, 40), 0, 0.6, sfx="wood_high")
T("¥", 2400, 5700, 150, GREEN, k0=1, k1=1.3, sfx="pop")
T("存钱", 2900, 5550, 80, k0=2, sfx="pop")
L(cup(2750, 5800), 3, 3.8, sfx="wood_high")
L(cross(2750, 5800, 110), 4, 4.35, RED, 12, sfx="rim")
T("第12级", 2400, 5880, 56, RED, k0=5, sfx="pop")

scene("玩手机，就砍时间", "例子 · 玩手机", (900, 6700, 0.85))
L(stick(700, 6900, 0.75, "hold"), 0, 0.6, sfx="wood_high")
L(face(700, 6900, 0.75, "smile"), 0.6, 0.75)
L(phone(840, 6720, 110, 180), 1, 1.4, BLUE, 8, sfx="pop")
T("一放学就刷", 1220, 6500, 56, k0=2, sfx="pop")
T("2小时", 1100, 6680, 64, k0=3, sfx="pop")
L(P((1010, 6670), (1190, 6670)), 4, 4.3, RED, 10, sfx="rim")
T("→ 1小时", 1330, 6800, 64, RED, k0=4.4, k1=4.9)
T("第12级", 1330, 6960, 56, RED, k0=5, sfx="pop")

scene("业绩差，再加指标", "例子 · 加指标", (2700, 6720, 0.85))
L(bars(2400, 6750, (260, 190, 120)), 0, 0.9, sfx="wood_high")
T("指标 +30%", 2950, 6500, 64, RED, k0=1, k1=1.9, sfx="pop")
L(arrow((3220, 6570), (3220, 6400), 0, 34), 2, 2.3, RED, 9, sfx="rim")
for n, x in enumerate((2450, 2600, 2750)):
    L(stick(x, 7000, 0.45), 3 + n * 0.25, 3.4 + n * 0.25, sfx="wood_high" if n == 0 else None)
L(join(arrow((2380, 6880), (2180, 6830), 0.15, 30), arrow((2380, 6940), (2180, 6990), -0.15, 30)), 4, 4.5, RED, 8,
  sfx="shaker")
T("推反了", 2950, 6640, 60, RED, k0=5, sfx="rim")

scene("都在拧最下面那级", "身边的例子", WIDE, shake=[4])
for n, (x, y, w) in enumerate(((1300, 5860, 260), (2400, 5880, 260), (1330, 6960, 260), (2950, 6640, 250))):
    L(rect(x, y - 5, w, 100, 40), n, n + 0.4, RED, 8, sfx="rim" if n == 3 else "wood_high")
T("都在拧第12级", 1800, 7150, 90, k0=4, k1=5.2, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 7850), (2650, 7850), (950, 8900), (2650, 8900)]
scene("第一招：摆到眼前", "第一招 · 信息", (900, 7900, 0.85))
L(rect(*SOL[0], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("① 摆到眼前", 950, 7560, 80, BLUE, k0=1, k1=1.9, sfx="pop")
T("第6级 · 信息", 950, 7680, 50, k0=2, k1=2.6)
L(rect(720, 7980, 380, 300, 16), 3, 3.4, sfx="wood_high")
for n, w in enumerate((260, 170, 90)):
    L(P((580, 7900 + n * 80), (580 + w, 7900 + n * 80)), 3.45 + n * 0.25, 3.65 + n * 0.25, GREEN, 22)
L(phone(1250, 7980, 280, 340), 4.2, 4.7)
T("奶茶 -18", 1250, 7940, 46, k0=5, k1=5.45, sfx="pop")
T("本月 -900", 1250, 8040, 46, RED, k0=5.5, k1=6.0)

scene("第二招：改规则", "第二招 · 规则", (2700, 7900, 0.85))
L(rect(*SOL[1], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("② 改规则", 2650, 7560, 80, BLUE, k0=1, k1=1.8, sfx="pop")
T("第5级 · 规则", 2650, 7680, 50, k0=2, k1=2.6)
T("花剩了再存", 2650, 7840, 62, k0=3, sfx="pop")
L(P((2490, 7830), (2810, 7830)), 4, 4.3, RED, 10, sfx="rim")
T("到账先存", 2650, 8000, 76, RED, k0=5, sfx="pop")

scene("第三招：问目标", "第三招 · 目标", (900, 9000, 0.85))
L(rect(*SOL[2], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("③ 问目标", 950, 8610, 80, BLUE, k0=1, k1=1.6, sfx="pop")
T("第3级 · 目标", 950, 8730, 50, k0=1.65, k1=1.95)
L(house(700, 8990), 2, 2.6, sfx="wood_high")
T("首付", 1150, 8950, 80, RED, k0=3, sfx="pop")
T("工时", 750, 9190, 66, k0=3.6, k1=4.0)
L(P((680, 9180), (820, 9180)), 4, 4.3, RED, 10, sfx="rim")
T("交付", 1150, 9190, 66, RED, k0=4.4, k1=4.9)
L(check(1290, 9180, 35), 5, 5.3, GREEN, 9, sfx="ding")

scene("第四招：先试一周", "第四招 · 小步试", (2650, 9000, 0.85))
L(rect(*SOL[3], 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("④ 先试一周", 2650, 8610, 80, BLUE, k0=1, k1=1.6, sfx="pop")
L(calendar(3080, 8650, 180, 170), 2, 2.5, BLACK, 8, sfx="wood_high")
T("推之前看方向", 2650, 8730, 50, k0=2.55, k1=2.95)
L(arrow((2350, 8950), (2900, 8950), 0, 40), 3, 3.4, BLACK, 9, sfx="wood_low")
L(cross(2950, 8950, 50), 4, 4.3, RED, 10, sfx="rim")
L(arrow((2900, 9100), (2350, 9100), 0, 40), 4.4, 4.8, GREEN, 9)
T("换个方向", 2650, 9220, 56, GREEN, k0=5, sfx="pop")

# ---------------------------------------------------------------- 拉远全板 + 评论区（场景 20–21）

scene("先找对那一级", "一句话", (1800, 5100, 0.235))
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 2, "wood_high", 0.6)
b.hit(J(), 4, "ding")

scene("这一季讲完了", "评论区见", (1800, 9650, 0.8))
b.hit(J(), 0, "cymbal", 0.5)
T("你想改的事，卡在哪一级？", 1800, 9560, 70, RED, k0=1, k1=2.6)
b.hit(J(), 1, "pop")
T("这一季讲完了，谢谢你一路看完", 1800, 9720, 52, k0=3, k1=4.5)
b.hit(J(), 3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "leverage", "杠杆点", "想改变，该从哪里下手？", ACC, b.shots,
                 ["Donella H. Meadows (1999), Leverage Points: Places to Intervene in a System（转述）",
                  f"{BOOK}中的杠杆点一节（转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                 "想改变|先找对【那一级】", 7,
                 ["书中观点均为转述：Meadows (1999) 列出十二个杠杆点，由弱到强依次为：12 常数、参数、数字；11 缓冲的大小；"
                  "10 存量流量的结构；9 延迟的长短；8 调节回路的强度；7 增强回路的强度；6 信息流的结构；5 系统的规则；"
                  "4 增加、改变或自组织系统结构的能力；3 系统的目标；2 系统赖以产生的心智模式（范式）；1 超越范式的能力。"
                  "画面只点出其中几级（数字、信息、规则、目标、心智模式），中文标签为缩写意译。“参数最弱”转述自原文"
                  "Parameters are dead last on my list of powerful interventions；“找对了却推反了”转述自文中关于人们常把杠杆"
                  "往错误方向推的论述。撬棍为示意画面。出处：Donella H. Meadows, Leverage Points: Places to Intervene in a "
                  "System (1999)；《系统之美》（Thinking in Systems, 2008；中译本邱昭良译，浙江人民出版社 2012）。",
                  "项目延期只会加班、存钱只少喝奶茶、孩子玩手机只砍时间、业绩差就加指标均为现实场景示意，不指向任何具体公司"
                  "或个人；摆到眼前、改规则、问目标、先试一周四招为据书中思路整理的建议。"],
                 tags="#改变 #方法论")
    return b.attach(ep)
