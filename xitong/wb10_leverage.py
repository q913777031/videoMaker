"""10 杠杆点（白板手绘版）：想改变，该从哪里下手？（系列最后一讲）

叙事：打工人切身问题开局（周一想重新开始：买新本子、下打卡软件、闹钟调早，一个月后照旧）→ 书中观点（撬棍演示
小力气撬大石头；十二个杠杆点画成一架梯子，只点出几级：最下面是数字、往上是信息、规则、目标、心智模式，越往上越有力；
找对了位置也常常推反方向）→ 身边的例子（项目延期只会加班、存钱只少喝奶茶、孩子玩手机只砍时间、业绩差就加指标）→
具体做法（摆到眼前 / 改规则 / 问目标 / 先试一周，推反了就掉头）→ 系列收尾：评论区问题 + 这一季讲完了。
书中观点为转述（Donella H. Meadows, Leverage Points: Places to Intervene in a System, 1999；《系统之美》中亦有收录与展开，
中译本邱昭良译，浙江人民出版社 2012）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, clock, cross, doc, face,
                               hands_at, join, marker, node, partial, rect, scribble, stick, target, underline)
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#B8322A"
SQUARE_SHOT = 15

b = Board(size=(3600, 9800))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    if k1 is None:
        k1 = k0 + max(0.5, 0.18 * len(s))
        if k0 < 2.6:
            k1 = min(k1, 3.1)          # 联系表取景（约第 3.25 拍）前写完
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


# ---------------------------------------------------------------- 撬棍（镜头 8 画出，镜头 9 压下，镜头 17 推反）

LV_X, LV_Y, GROUND = 2550, 3110, 3200        # 支点顶端与地面
ARM_L, ARM_R, TH0 = 450, 400, 0.2


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


def level_mark(level, word, extra=None):
    """高亮一级：红线描在这一级上（第 0 拍）+ 右侧写出名字（第 1 拍）。"""
    y = rung_y(level)
    L(P((R_L, y), (R_R, y)), 0, 0.4, RED, 14, sfx="wood_high")
    T(word, LAB_X, y + 18, 56, RED, k0=1, sfx="pop")
    L(P((R_R + 30, y), (LAB_X - 28 * len(word) - 30, y)), 1.8, 2.1, RED, 5)


# ---------------------------------------------------------------- 开局：想改变，总是没变（镜头 1–6）

b.shot("周一，重新开始", "灵魂拷问", view=(1000, 1000, 0.85))
L(stick(750, 1250, 0.9, "up"), 0, 0.6, sfx="wood_high")
L(face(750, 1250, 0.9, "smile"), 0.6, 0.75)
T("周一", 1200, 820, 80, k0=1, sfx="pop")
T("重新开始！", 1200, 960, 70, RED, k0=2, sfx="pop")

b.shot("先买个新本子", "灵魂拷问", view=(2600, 1000, 0.85))
L(book(2300, 950, 380, 250), 0, 0.9, sfx="wood_high")
T("新本子", 2300, 1200, 64, k0=1.2)
b.hit(J(), 2, "ding")
L(underline(2180, 2420, 1250, 10, 30), 2, 2.4, GREEN, 6)

b.shot("又下了打卡软件", "灵魂拷问", view=(2600, 1000, 0.85))
L(phone(2900, 950), 0, 0.6, sfx="wood_high")
for n in range(3):
    L(check(2900, 860 + n * 80, 28), 1 + n * 0.25, 1.2 + n * 0.25, GREEN, 7, sfx="pop" if n == 0 else None)
T("打卡软件", 2900, 1200, 60, k0=2, sfx="pop")

b.shot("闹钟调早半小时", "灵魂拷问", view=(1000, 1700, 0.85))
L(clock(800, 1700, 170), 0, 0.8, sfx="wood_low")
L(hands_at(800, 1700, 170, 6, 30), 1, 1.3, RED, 12, sfx="rim")
T("早半小时", 1300, 1680, 70, RED, k0=2, sfx="pop")

b.shot("一个月后，照旧", "灵魂拷问", view=(1800, 1350, 0.42), shake=[3])
T("一个月后：照旧", 2600, 1700, 110, k0=0, k1=1.0, sfx="pop")
for n, (x, y) in enumerate(((2300, 950), (2900, 950), (800, 1700))):
    L(cross(x, y, 150), 1 + n, 1.35 + n, RED, 14, sfx="rim")

b.shot("该从哪下手？", "灵魂拷问", view=(1800, 1550, 0.42), flashes=[0])
T("？", 1800, 2250, 420, RED, k0=0, k1=0.6, sfx="kick")
T("从哪下手", 1800, 2520, 130, k0=1.0, k1=1.8, sfx="pop")
b.hit(J(), 2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有篇文章专讲这个", "杠杆点 · 梅多斯", view=(1000, 2900, 0.85))
L(book(800, 2900, 420, 280), 0, 1.0, sfx="wood_low")
T("杠杆点", 800, 2660, 80, GREEN, k0=1.0, sfx="pop")
T("梅多斯 · 1999", 800, 3130, 52, k0=2.0, sfx="pop")
T("系统之美也收了", 800, 3230, 46, k0=2.6, k1=3.4)

j_draw = b.shot("小力气，撬大石头", "书中例子 · 撬棍", view=(2600, 2950, 0.85))
j_push, j_back = j_draw + 1, j_draw + 9
L(P((2050, GROUND), (3150, GROUND)), 0, 0.5, BLACK, 8, sfx="wood_high")
L(P((LV_X, LV_Y), (LV_X - 70, GROUND), (LV_X + 70, GROUND), close=True), 0.5, 0.9)
b.custom(j_draw, 1, 2.2, lever_fn(j_draw, j_push, j_back), sfx="pop")
T("小力气", 2150, 3300, 56, BLUE, k0=2.2)
b.hit(J(), 3, "wood_low")
T("大石头", 2960, 3300, 56, k0=2.5)

b.shot("手一压，石头起来", "书中例子 · 撬棍", view=(2550, 2900, 0.85), shake=[0], flashes=[0])
b.hit(j_push, 0, "kick", 1.0, "压下")
L(arrow((2090, 2780), (2090, 2960), 0, 50), 0, 0.3, BLUE, 12)
T("撬起来！", 2600, 2620, 90, RED, k0=1.0, sfx="tom")
b.hit(j_push, 2, "ding", 0.8)

b.shot("她列了十二个位置", "书中观点 · 十二个杠杆点", view=(1200, 4330, 0.85))
L(join(P((R_L, R_TOP - 60), (R_L, R_BOT + 40)), P((R_R, R_TOP - 60), (R_R, R_BOT + 40))), 0, 0.6, sfx="wood_high")
L(join(*[P((R_L, rung_y(lv)), (R_R, rung_y(lv))) for lv in range(12, 0, -1)]), 1, 2.4, BLACK, 7, sfx="pop")
T("12", 920, rung_y(12) + 16, 50, k0=2.5)
T("1", 920, rung_y(1) + 16, 50, k0=3, sfx="pop")

b.shot("最下面：拧数字", "十二个杠杆点 · 第十二", view=(1200, 4330, 0.85))
level_mark(12, "数字")
L(knob(1710, rung_y(12), 45), 2, 2.5, BLACK, 8, sfx="shaker")

b.shot("排最后，效果最小", "十二个杠杆点 · 第十二", view=(1200, 4330, 0.85))
T("最弱", LAB_X, rung_y(12) + 130, 60, RED, k0=0, sfx="rim")
L(underline(LAB_X - 70, LAB_X + 70, rung_y(12) + 160, 8, 24), 2, 2.4, RED, 6, sfx="wood_low")

b.shot("往上：谁看得到啥", "十二个杠杆点 · 第六", view=(1200, 4330, 0.85))
level_mark(6, "信息")

b.shot("再往上：定规则", "十二个杠杆点 · 第五", view=(1200, 4330, 0.85))
level_mark(5, "规则")

b.shot("更上面：目标", "十二个杠杆点 · 第三", view=(1200, 4330, 0.85))
level_mark(3, "目标")
L(target(1710, rung_y(3), 40), 2, 2.5, RED, 7, sfx="ding")

b.shot("最强：心里的看法", "十二个杠杆点 · 第二", view=(1200, 4330, 0.85), flashes=[2])
level_mark(2, "心智模式")
L(arrow((700, R_BOT - 50), (700, R_TOP + 60), 0, 50), 2, 2.6, RED, 12, sfx="ding")
T("越有力", 700, R_TOP - 70, 60, RED, k0=3, sfx="pop")

b.shot("找对了，却推反了", "书中观点 · 推反方向", view=(2500, 2950, 0.85), shake=[1])
L(arrow((1990, GROUND - 20), (1990, 2930), 0, 50), 0, 0.4, RED, 12, sfx="wood_high")
b.hit(j_back, 1, "tom", 0.9, "石头落回")
L(cross(2600, 2600, 90), 2, 2.35, RED, 12, sfx="rim")
T("推反了", 2600, 2470, 70, RED, k0=2.6)

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5600), (2650, 5600), (950, 6600), (2650, 6600)]
b.shot("身边就有例子", "身边的例子", view=(1800, 6050, 0.42))
T("身边的例子", 1800, 5060, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("项目又延期了", "例子 · 项目延期", view=(950, 5600, 0.85))
L(calendar(700, 5550), 0, 0.9, sfx="wood_high")
T("延期", 1200, 5500, 90, RED, k0=1, sfx="pop")
L(rect(1200, 5470, 220, 130, 16), 2, 2.4, RED, 8, sfx="rim")

b.shot("只会让大家加班", "例子 · 项目延期", view=(950, 5650, 0.85))
for n, x in enumerate((640, 800, 960)):
    L(stick(x, 6000, 0.5, "hold"), n * 0.25, n * 0.25 + 0.45, sfx="wood_high" if n == 0 else None)
T("每天 +2 小时", 1150, 5800, 60, k0=1, sfx="pop")
T("第12级", 1300, 5950, 56, RED, k0=2, sfx="rim")

b.shot("想多存点钱", "例子 · 存钱", view=(2650, 5600, 0.85))
L(rect(2400, 5650, 260, 300, 40), 0, 0.6, sfx="wood_high")
T("¥", 2400, 5700, 150, GREEN, k0=1, k1=1.3, sfx="pop")
T("存钱", 2900, 5550, 80, k0=2, sfx="pop")

b.shot("只少喝杯奶茶", "例子 · 存钱", view=(2650, 5650, 0.85))
L(cup(2900, 5780), 0, 0.8, sfx="wood_high")
L(cross(2900, 5780, 110), 1, 1.35, RED, 12, sfx="rim")
T("第12级", 2400, 5950, 56, RED, k0=2, sfx="pop")

b.shot("孩子总抱着手机", "例子 · 玩手机", view=(950, 6600, 0.85))
L(stick(700, 6900, 0.75, "hold"), 0, 0.6, sfx="wood_high")
L(face(700, 6900, 0.75, "smile"), 0.6, 0.75)
L(phone(840, 6720, 110, 180), 1, 1.4, BLUE, 8, sfx="pop")
T("一放学就刷", 1220, 6500, 56, k0=2, sfx="pop")

b.shot("只把时间砍一半", "例子 · 玩手机", view=(950, 6650, 0.85))
T("2小时", 1100, 6680, 64, k0=0, sfx="pop")
L(P((1010, 6670), (1190, 6670)), 1, 1.3, RED, 10, sfx="rim")
T("→ 1小时", 1330, 6800, 64, RED, k0=1.6)
T("第12级", 1200, 6950, 56, RED, k0=2.6, sfx=None)
b.hit(J(), 3, "pop")

b.shot("业绩差，再加指标", "例子 · 加指标", view=(2650, 6600, 0.85))
L(bars(2450, 6850, (300, 220, 140)), 0, 0.9, sfx="wood_high")
T("指标 +30%", 2950, 6550, 64, RED, k0=1, sfx="pop")
L(arrow((2950, 6620), (2950, 6450), 0, 34), 2, 2.3, RED, 9, sfx="rim")

b.shot("越压，人走得越多", "例子 · 加指标", view=(2650, 6650, 0.85))
for n, x in enumerate((2750, 2900, 3050)):
    L(stick(x, 7000, 0.45), n * 0.25, n * 0.25 + 0.4, sfx="wood_high" if n == 0 else None)
L(join(arrow((2930, 6830), (3180, 6760), -0.15, 30), arrow((3080, 6830), (3260, 6900), 0.15, 30)), 1, 1.5, RED, 8,
  sfx="shaker")
T("推反了", 2950, 6680, 60, RED, k0=2, sfx="rim")

b.shot("都在拧最下面那级", "身边的例子", view=(1800, 6200, 0.42))
T("都在拧数字", 1800, 7160, 110, k0=0, sfx="pop")
b.hit(J(), 2, "wood_low")

b.shot("力气用在最弱处", "身边的例子", view=(1800, 6150, 0.42), shake=[0])
T("第12级", 1800, 6150, 140, RED, k0=0, k1=0.5, sfx="kick")
for n, (x, y) in enumerate(CARDS):
    L(arrow((1800 + (x - 1800) * 0.75, 6100 + (y - 6100) * 0.75),
            (1800 + (x - 1800) * 0.3, 6100 + (y - 6100) * 0.45), 0.1, 40),
      1 + n * 0.5, 1.4 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 7850), (2650, 7850), (950, 8750), (2650, 8750)]
b.shot("想改变，这样下手", "具体做法", view=(1800, 8300, 0.42))
T("往上多找一级", 1800, 7330, 110, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1500, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("第一招：摆到眼前", "第一招 · 信息", view=(950, 7850, 0.85))
T("① 摆到眼前", 950, 7560, 80, BLUE, k0=0, sfx="pop")
T("第6级 · 信息", 950, 7680, 50, k0=2, sfx="pop")

b.shot("进度贴在墙上", "第一招 · 信息", view=(950, 7900, 0.85))
L(rect(720, 7980, 380, 300, 16), 0, 0.5, sfx="wood_high")
for n, w in enumerate((260, 170, 90)):
    L(P((580, 7900 + n * 80), (580 + w, 7900 + n * 80)), 1 + n * 0.25, 1.2 + n * 0.25, GREEN, 22,
      sfx="pop" if n == 0 else None)
L(check(940, 7900, 30), 2, 2.3, GREEN, 8, sfx="ding")

b.shot("每笔花销都推送", "第一招 · 信息", view=(950, 7900, 0.85))
L(phone(1250, 7980, 220, 340), 0, 0.5, sfx="wood_high")
T("奶茶", 1250, 7930, 46, k0=1, sfx="pop")
T("-18", 1250, 8010, 50, RED, k0=1.5)
T("本月 -900", 1250, 8090, 46, RED, k0=2, sfx="pop")

b.shot("第二招：改规则", "第二招 · 规则", view=(2650, 7850, 0.85))
T("② 改规则", 2650, 7560, 80, BLUE, k0=0, sfx="pop")
T("第5级 · 规则", 2650, 7680, 50, k0=2, sfx="pop")

b.shot("工资先存再花", "第二招 · 规则", view=(2650, 7900, 0.85))
T("花剩了再存", 2650, 7820, 62, k0=0, sfx="pop")
L(P((2490, 7810), (2810, 7810)), 1, 1.3, RED, 10, sfx="rim")
T("到账先存", 2650, 7950, 70, RED, k0=2, sfx="pop")

b.shot("作业写完再玩", "第二招 · 规则", view=(2650, 7950, 0.85))
L(doc(2400, 8130, 130, 170), 0, 0.5, sfx="wood_high")
L(arrow((2500, 8130), (2780, 8130), 0.1, 34), 1, 1.4, BLACK, 8, sfx="pop")
L(phone(2880, 8130, 110, 170), 1.5, 1.9, BLUE, 8)
L(check(3050, 8060, 35), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("第三招：问目标", "第三招 · 目标", view=(950, 8750, 0.85))
T("③ 问目标", 950, 8460, 80, BLUE, k0=0, sfx="pop")
T("第3级 · 目标", 950, 8580, 50, k0=2, sfx="pop")

b.shot("存钱是为了啥", "第三招 · 目标", view=(950, 8800, 0.85))
L(house(700, 8840), 0, 0.8, sfx="wood_high")
T("首付", 1150, 8800, 80, RED, k0=1, sfx="pop")
L(underline(1050, 1250, 8850, 10, 28), 2, 2.4, RED, 7, sfx="ding")

b.shot("项目要的是交付", "第三招 · 目标", view=(950, 8850, 0.85))
T("工时", 750, 9040, 66, k0=0, sfx="pop")
L(P((680, 9030), (820, 9030)), 1, 1.3, RED, 10, sfx="rim")
T("交付", 1150, 9040, 66, RED, k0=1.6)
L(check(1290, 9030, 35), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("第四招：先试一周", "第四招 · 小步试", view=(2650, 8750, 0.85))
T("④ 先试一周", 2650, 8460, 80, BLUE, k0=0, sfx="pop")
L(calendar(3080, 8500, 180, 170), 1, 1.6, BLACK, 8, sfx="wood_high")
T("推之前看方向", 2650, 8580, 50, k0=2, sfx="pop")

b.shot("推反了就掉头", "第四招 · 小步试", view=(2650, 8850, 0.85))
L(arrow((2350, 8800), (2900, 8800), 0, 40), 0, 0.5, BLACK, 9, sfx="wood_high")
L(cross(2950, 8800, 50), 1, 1.3, RED, 10, sfx="rim")
L(arrow((2900, 8950), (2350, 8950), 0, 40), 2, 2.5, GREEN, 9, sfx="pop")
T("换个方向", 2650, 9070, 56, GREEN, k0=2.6)

b.shot("先找对那一级", "一句话", view=(1800, 5100, 0.235))
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 2, "ding")

b.shot("这一季讲完了", "评论区见", view=(1800, 9450, 0.8))
T("你想改的事，卡在哪一级？", 1800, 9360, 70, RED, k0=0.5, k1=1.8)
T("这一季讲完了，谢谢你一路看完", 1800, 9520, 52, k0=2.0, k1=3.2)
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 1, "pop")
b.hit(J(), 2, "wood_high", 0.7)
b.hit(J(), 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "leverage", "杠杆点", "想改变，该从哪里下手？", ACC, b.shots,
                 ["Donella H. Meadows (1999), Leverage Points: Places to Intervene in a System（转述）",
                  f"{BOOK}中的杠杆点一节（转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                 "想改变|先找对【那一级】", 15,
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
