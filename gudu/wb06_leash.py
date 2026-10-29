"""06 弹性的绳子（白板手绘版）：有人独处挺好，有人一天都熬不住？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
叙事：打工人切身问题开局（合租室友一个人宅一周天天乐呵呵；你一个周末就难受，翻遍通讯录都在忙，一天都熬不住）→
书中观点（亮书《孤独是可耻的》、卡乔波；双生子研究：对被冷落的敏感程度天生有差别，相当一部分随遗传；作者的比喻
“弹性的绳子”：一头拴着身边人，基因定绳子长短，环境和做法决定怎么用；动态画面：长绳的人走远也自在，短绳的人
一走就扯；画成一张图，对上室友和你）→ 身边的例子（居家办公一周、聚会散场回家、周末夫妻一个想宅一个想出门、
孩子刚上幼儿园；最后拉远：绳子长短不一样，长短都正常）→ 具体做法（认清绳长别自责 / 按需要定联系频率 /
提前约好周末 / 绳长的也留根线）→ 评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, 2008；中译本
《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, building, check, circle, desk,
                               face, join, marker, node, partial, rect, scribble, stick, underline)
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#B5654A"
SQUARE_SHOT = 8

b = Board(size=(3600, 11600))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def ease_io(x):
    return 0.5 - 0.5 * math.cos(math.pi * clamp01(x))


def moon(x, y, r=80) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 14), P((x - w * 0.18, y + h / 2 - 20), (x + w * 0.18, y + h / 2 - 20)))


def house(x, y, w=260, h=220) -> skia.Path:
    """小房子：(x, y) 为底边中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 30, y - h), (x, y - h - 140), (x + w / 2 + 30, y - h)),
                P((x - 35, y), (x - 35, y - 110), (x + 35, y - 110), (x + 35, y)), rect(x + 75, y - 140, 50, 50, 4))


def window(x, y, s=260) -> skia.Path:
    return join(rect(x, y, s, s, 10), P((x, y - s / 2), (x, y + s / 2)), P((x - s / 2, y), (x + s / 2, y)))


def smiley(x, y, r=60, mood="smile") -> skia.Path:
    """圆脸表情：(x, y) 为脸中心。"""
    p = circle(x, y, r)
    p.addCircle(x - r * 0.33, y - r * 0.2, r * 0.07)
    p.addCircle(x + r * 0.33, y - r * 0.2, r * 0.07)
    if mood == "smile":
        p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.1, r * 0.9, r * 0.6), 20, 140)
    else:
        p.addArc(skia.Rect.MakeXYWH(x - r * 0.4, y + r * 0.25, r * 0.8, r * 0.5), 200, 140)
    return p


def tears(x, y) -> skia.Path:
    """两行眼泪：(x, y) 为头部中心。"""
    return join(P((x - 14, y + 6), (x - 20, y + 40)), P((x + 14, y + 6), (x + 20, y + 40)))


def boxes(x0, y, n=7, step=120, s=100) -> skia.Path:
    return join(*[rect(x0 + i * step, y, s, s, 10) for i in range(n)])


# ---------------------------------------------------------------- 动态元件：弹性的绳子

ANCH = (1270, 3950)                       # 绳子另一头：身边人
WALK = {}                                 # 'long' / 'short' -> (走动的场景序号, 起步拍)


def rope_fn(long: bool):
    """一个人 + 拴在“身边人”上的绳子。长绳：走远了绳子还松着；短绳：走几步就绷直、被扯回来。"""
    ax, ay = (1370, 3870) if long else (1370, 4030)
    fy = 3800 if long else 4420
    Lr = 1500 if long else 600
    x_home = 1720
    dy = (fy - 140) - ay
    reach = ax + math.sqrt(Lr * Lr - dy * dy) + 10 - 1       # 短绳绷直时人的位置

    def where(t):
        w = WALK.get("long" if long else "short")
        if w is None:
            return x_home, 0.0, None
        jw, kw = w
        t0 = b.t_of(jw, kw)
        if long:
            e = ease_io((t - t0) / (b.t_of(jw, kw + 1.6) - t0))
            bob = 12 * abs(math.sin(e * math.pi * 4)) if 0 < e < 1 else 0.0
            return x_home + 510 * e, bob, None
        tt = b.t_of(jw, kw + 1)
        if t < tt:
            e = clamp01((t - t0) / (tt - t0)) ** 1.6
            bob = 12 * abs(math.sin(e * math.pi * 3)) if 0 < e < 1 else 0.0
            return x_home + (reach - x_home) * e, bob, None
        dt = t - tt
        return reach - 30 * math.exp(-dt * 5) * abs(math.sin(dt * 12)), 0.0, dt

    def fn(c, k, t):
        x, bob, taut = where(t)
        y = fy - bob
        mood = "smile" if (long or taut is None) else "sad"
        person = join(stick(x, y, 0.8), face(x, y, 0.8, mood))
        px, py = x - 10, y - 140
        d = math.hypot(px - ax, py - ay)
        mx, my = (ax + px) / 2, (ay + py) / 2
        rope = skia.Path()
        rope.moveTo(ax, ay)
        if taut is None and d < Lr - 1:
            sag = min(150.0, 0.35 * math.sqrt(Lr * Lr - d * d))
            rope.quadTo(mx, my + 2 * sag, px, py)
        else:
            dt = taut or 0.0
            ux, uy = -(py - ay) / d, (px - ax) / d
            off = 2 * 22 * math.sin(dt * 30) * math.exp(-dt * 4)
            rope.quadTo(mx + ux * off, my + uy * off, px, py)
        kk = clamp01(k)
        part_p, tip_p = partial(person, clamp01(kk * 1.6))
        c.drawPath(part_p, marker(BLACK, 9))
        part_r, tip_r = partial(rope, clamp01(kk * 2.5 - 1.5))
        c.drawPath(part_r, marker(ORANGE, 10))
        if taut is not None:
            a = 0.6 + 0.4 * math.exp(-taut * 3)
            for n in range(3):
                ox = px + 30 + n * 26
                c.drawPath(P((ox, py - 60 + n * 8), (ox + 26, py - 90 + n * 8)), marker(RED, 6, a))
            c.drawPath(P((ax + 120, ay - 40), (ax + 150, ay - 75)), marker(RED, 6, a))
        if kk < 1:
            return tip_r if kk * 2.5 - 1.5 > 0 else tip_p
        return None

    return fn


# ---------------------------------------------------------------- 开局：室友和你（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("室友宅一周，天天乐", "灵魂拷问", (950, 800, 0.85))
L(boxes(590, 440, 7, 120, 96), 0, 0.8, BLACK, 8, sfx="wood_high")
L(stick(720, 1170, 0.9, "up"), 1, 1.6, sfx="pop")
L(face(720, 1170, 0.9, "smile"), 1.6, 1.75)
T("室友", 720, 810, 56, k0=1.75, k1=2.0)
T("宅一周", 1200, 880, 76, RED, k0=2, sfx="pop")
for n in range(7):
    L(check(590 + n * 120, 440, 28), 3 + n * 0.1, 3.1 + n * 0.1, GREEN, 7, sfx="shaker" if n == 0 else None)
T("哈哈", 470, 820, 70, BLUE, k0=3.7, k1=4.0)
T("追剧", 1100, 1030, 64, k0=4, k1=4.4, sfx="pop")
T("外卖", 1100, 1140, 64, k0=4.5, k1=4.9)
L(P((1170, 1195), (1030, 1195)), 5, 5.4, GREEN, 8, sfx="ding")

scene("你周末翻遍通讯录", "灵魂拷问", (2650, 820, 0.85))
L(stick(2380, 1170, 0.9, "down"), 0, 0.6, sfx="wood_high")
L(face(2380, 1170, 0.9, "sad"), 0.6, 0.75)
T("你", 2380, 810, 64, BLUE, k0=1, sfx="pop")
L(phone(2800, 980, 240, 380), 2, 2.6, BLACK, 9, sfx="pop")
for n, w in enumerate(("小王", "阿美", "老同学")):
    T(w, 2800, 870 + n * 80, 48, k0=2.7 + n * 0.2, k1=2.9 + n * 0.2)
for n in range(3):
    L(P((2700, 870 + n * 80), (2900, 870 + n * 80)), 4 + n * 0.15, 4.15 + n * 0.15, RED, 8,
      sfx="rim" if n == 0 else None)
T("都在忙", 2800, 1230, 60, RED, k0=5, sfx="pop")
L(P((2890, 1275), (2710, 1275)), 5.6, 5.9, RED, 7)

scene("一天都熬不住，差在哪", "灵魂拷问", (950, 2120, 0.85), flashes=[4])
L(window(620, 1760, 260), 0, 0.7, BLACK, 9, sfx="wood_high")
L(stick(1080, 2250, 0.9, "down"), 1, 1.6, sfx="pop")
L(face(1080, 2250, 0.9, "sad"), 1.6, 1.75)
T("心里空落落", 950, 2390, 64, RED, k0=2, sfx="pop")
L(scribble(1080, 1760, 260, 110, 7), 3, 3.5, RED, 7, sfx="shaker")
T("？", 1420, 2050, 220, RED, k0=4, k1=4.5, sfx="kick")
T("差在哪", 950, 2560, 90, k0=5, k1=5.8, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

scene("有本书研究过双胞胎", "孤独是可耻的", (2650, 2220, 0.85))
L(book(2650, 2150, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 2650, 1900, 76, GREEN, k0=1, sfx="pop")
T("卡乔波", 2650, 2400, 56, k0=2, sfx="pop")
T("拿双胞胎做研究", 2650, 2560, 60, RED, k0=4, sfx="pop")

scene("怕被冷落，有天生的", "书中观点 · 天生差别", (2950, 3560, 0.85), shake=[0], flashes=[0])
T("天生", 2950, 3300, 170, RED, k0=0, k1=0.5, sfx="kick")
L(join(stick(2700, 3490, 0.9), face(2700, 3490, 0.9, "smile")), 2, 2.7, sfx="wood_high")
L(join(stick(3200, 3490, 0.9), face(3200, 3490, 0.9, "smile")), 3, 3.7, sfx="wood_high")
T("一部分随基因", 2950, 3660, 60, k0=4, sfx="pop")
L(underline(2770, 3130, 3710, 10, 30), 5, 5.4, RED, 7, sfx="ding")

scene("作者比作弹性绳子", "书中比喻 · 弹性的绳子", (1740, 3950, 0.8))
T("弹性的绳子", 1740, 3430, 84, GREEN, k0=0, sfx="pop")
L(node(*ANCH, 120), 1, 1.5, BLACK, 9, sfx="wood_high")
T("身边人", ANCH[0], ANCH[1], 50, k0=1.5, k1=2.0)
b.custom(J(), 3, 4.4, rope_fn(True), sfx="pop")
b.custom(J(), 5, 6.4, rope_fn(False), sfx="wood_high")

scene("长绳走远也自在", "书中比喻 · 长绳", (1740, 3950, 0.8))
T("长绳", 1550, 3600, 60, ORANGE, k0=0, sfx="pop")
T("短绳", 1550, 4400, 60, ORANGE, k0=1, sfx="pop")
T("天生：定长短", 2170, 4000, 60, RED, k0=2, sfx="pop")
WALK["long"] = (J(), 3)
H(3, "shaker")
T("自在", 1950, 3560, 56, BLUE, k0=5, sfx="ding")

WALK["short"] = (scene("短绳一走就扯", "书中比喻 · 短绳", (1740, 3950, 0.8), shake=[1]), 0)
H(0, "shaker")
H(1, "kick", 0.9)
T("扯得慌", 1700, 4260, 60, RED, k0=2, sfx="rim")
L(P((1790, 4305), (1610, 4305)), 3, 3.3, RED, 7, sfx="tom")

scene("长短天生，用法在你", "书中观点 · 一张图", (1700, 4050, 0.62))
L(rect(1740, 3960, 1500, 1250, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("室友", 2230, 3470, 56, BLUE, k0=1, sfx="pop")
T("你", 1780, 4400, 64, BLUE, k0=2, sfx="pop")
T("后天：怎么用", 2170, 4090, 60, BLUE, k0=3, sfx="pop")
T("环境 · 做法", 2170, 4180, 48, k0=4, sfx="pop")
L(underline(2000, 2340, 4125, 10, 30), 5, 5.4, RED, 7, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 6200), (2650, 6200), (950, 7150), (2650, 7150)]
OVER = (1800, 6870, 0.355)
scene("身边也常见", "身边的例子", OVER)
T("身边的例子", 1800, 5620, 100, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

scene("居家一周就想见人", "例子 · 居家办公", (930, 6200, 0.85))
L(desk(700, 6360, 300), 0, 0.7, sfx="wood_high")
L(stick(1010, 6500, 0.85), 1, 1.6, sfx="pop")
L(face(1010, 6500, 0.85, "flat"), 1.6, 1.75)
T("周一 → 周五", 900, 5910, 64, k0=2, sfx="pop")
T("第三天", 560, 6100, 60, RED, k0=3, sfx="pop")
L(building(1400, 6460, 180, 300), 4, 4.6, BLACK, 8, sfx="wood_high")
L(arrow((1090, 6280), (1290, 6280), 0.1, 34), 4.6, 4.9, GREEN, 8)
T("想见人", 1150, 6100, 60, RED, k0=5, sfx="pop")

scene("聚会散了，有人发慌", "例子 · 散场回家", (2690, 6200, 0.85))
L(house(2330, 6500, 240, 210), 0, 0.8, sfx="wood_high")
L(join(stick(2680, 6500, 0.75), face(2680, 6500, 0.75, "flat")), 1, 1.7, sfx="wood_high")
L(smiley(3050, 6100, 60, "smile"), 2, 2.5, BLUE, 8, sfx="pop")
T("松口气", 2880, 6100, 50, BLUE, k0=2.5, k1=2.9)
L(smiley(3050, 6400, 60, "sad"), 3, 3.5, RED, 8, sfx="rim")
T("发慌", 2900, 6400, 50, RED, k0=3.5, k1=3.8)
T("散场", 2330, 5880, 60, k0=4, sfx="pop")
L(moon(2600, 5930, 80), 5, 5.5, BLACK, 8)

scene("他想宅，她想出门", "例子 · 夫妻周末", (930, 7150, 0.85))
L(join(stick(650, 7500, 0.85), face(650, 7500, 0.85, "smile")), 0, 0.75, sfx="wood_high")
T("宅", 650, 7030, 110, BLACK, k0=1, k1=1.3, sfx="pop")
T("在家躺", 880, 7360, 54, k0=1.5, k1=2.0)
L(join(stick(1250, 7500, 0.85, "point"), face(1250, 7500, 0.85, "smile")), 2, 2.75, BLUE, sfx="wood_high")
L(scribble(950, 7200, 120, 120, 6), 3, 3.4, RED, 7, sfx="rim")
T("出门！", 1250, 7010, 64, RED, k0=4, sfx="pop")

scene("有的玩开，有的哭", "例子 · 上幼儿园", (2690, 7500, 0.85))
L(building(2650, 7450, 300, 330), 0, 0.8, BLACK, 8, sfx="wood_high")
T("幼儿园", 2260, 7000, 60, k0=0.8, k1=1.3)
L(join(P((2650, 7120), (2650, 7000)), P((2650, 7000), (2740, 7030), (2650, 7060))), 1.3, 1.6, RED, 8)
L(join(stick(2300, 7500, 0.55, "up"), face(2300, 7500, 0.55, "smile")), 2, 2.6, BLUE, 8, sfx="pop")
T("玩开了", 2300, 7240, 50, BLUE, k0=2.6, k1=3.0)
L(stick(3050, 7500, 0.55), 3, 3.5, BLACK, 8, sfx="rim")
L(join(face(3050, 7500, 0.55, "sad"), tears(3050, 7500 - 290 * 0.55)), 3.5, 3.7, BLUE, 6)
T("哭一天", 3050, 7240, 50, RED, k0=4, k1=4.5, sfx="tom")

scene("绳子有长短，都正常", "身边的例子", OVER, shake=[4])
for n, ((x, y), w) in enumerate(zip(CARDS, ("短绳", "有长有短", "一长一短", "有长有短"))):
    T(w, x + 330 if n else x + 380, y - 330, 110, ORANGE, k0=n * 0.8, k1=n * 0.8 + 0.7, sfx="pop" if n % 2 == 0 else None)
T("长短都正常", 1800, 7770, 140, GREEN, k0=4, k1=4.8, sfx="kick")
L(check(2220, 7760, 60), 5, 5.3, GREEN, 12, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 8790), (2650, 8790), (950, 9740), (2650, 9940)]
scene("认清绳长，别骂自己", "第一步 · 认清绳长", (950, 8790, 0.85))
L(rect(950, 8790, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("① 认清绳长", 950, 8470, 76, BLUE, k0=0.5, sfx="pop")
L(join(P((620, 8620), (1280, 8620)), *[P((620 + i * 110, 8590), (620 + i * 110, 8650)) for i in range(7)]), 1, 1.6,
  ORANGE, 8, sfx="wood_high")
T("我的绳：短", 950, 8740, 60, k0=2, sfx="pop")
T("我太黏人了", 760, 8880, 56, k0=3, sfx="pop")
L(P((610, 8880), (910, 8880)), 4, 4.3, RED, 10, sfx="rim")
T("正常", 1200, 8880, 64, GREEN, k0=5, k1=5.4, sfx="pop")
L(check(1320, 8875, 34), 5.5, 5.8, GREEN, 9)

scene("多久联系，自己定", "第二步 · 定频率", (2650, 8790, 0.85))
L(rect(2650, 8790, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("② 定联系频率", 2650, 8470, 76, BLUE, k0=0.5, sfx="pop")
L(phone(2650, 8680, 90, 150), 1, 1.4, BLUE, 8, sfx="wood_high")
T("短绳：每晚视频 10 分钟", 2600, 8890, 54, k0=2, k1=3.4, sfx="pop")
L(check(3020, 8885, 34), 3.5, 3.8, GREEN, 9)
T("长绳：每周一条消息", 2600, 9060, 54, k0=4, k1=5.4, sfx="pop")
L(check(2960, 9055, 34), 5.5, 5.8, GREEN, 9)

scene("周末提前约好", "第三步 · 约周末", (950, 9860, 0.85))
L(rect(950, 9740, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("③ 提前约周末", 950, 9420, 76, BLUE, k0=0.5, sfx="pop")
L(boxes(590, 9620, 7, 120, 100), 1, 1.6, BLACK, 7, sfx="wood_high")
for n, d in enumerate("一二三四五六日"):
    T(d, 590 + n * 120, 9620, 50, k0=1.6 + n * 0.05, k1=1.75 + n * 0.05)
L(circle(830, 9620, 70), 2, 2.4, RED, 8, sfx="pop")
L(circle(1190, 9620, 70), 3, 3.4, GREEN, 8, sfx="pop")
L(arrow((860, 9540), (1160, 9540), 0.25, 30), 3.4, 3.8, RED, 7)
T("周三约 → 周六见", 950, 9810, 58, RED, k0=4, k1=4.9, sfx="pop")
T("羽毛球 · 读书会", 950, 9980, 56, k0=5, k1=6, sfx="wood_high")

scene("绳长也常找老友", "第四步 · 留根线", (2650, 10050, 0.85))
L(rect(2650, 9940, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("④ 绳长也留根线", 2650, 9620, 76, BLUE, k0=0.5, sfx="pop")
L(join(stick(2350, 10040, 0.7), face(2350, 10040, 0.7, "smile")), 1, 1.6, sfx="wood_high")
L(node(3000, 9860, 75), 2, 2.3, BLACK, 8, sfx="pop")
T("老友", 3000, 9860, 46, k0=2.3, k1=2.6)
L(P((2400, 9900), (2925, 9870)), 3, 3.4, ORANGE, 6, sfx="wood_high")
L(rect(2900, 10100, 300, 110, 40), 4, 4.5, BLACK, 7)
T("最近咋样？", 2900, 10100, 48, k0=4.5, k1=5.4)
L(check(3110, 10220, 34), 5.5, 5.8, GREEN, 9)
H(4, "pop", 0.6)
H(5, "ding", 0.6)

scene("知道绳长，用好它", "一句话", (1800, 6200, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 11020, 0.8))
T("你的绳子长还是短？", 1800, 10940, 80, RED, k0=1, k1=2.6)
T("下一讲：被同事晾在一边，为什么那么难受？", 1800, 11100, 48, k0=3, k1=4.5)
H(0, "cymbal", 0.5)
H(1, "pop")
H(3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")

def build():
    ep = episode(6, "leash", "弹性的绳子", "有人独处挺好，有人一天都熬不住？", ACC, b.shots,
                 [f"{BOOK}（转述）：对被冷落的敏感度天生有差别、双生子研究、“弹性的绳子”比喻",
                  "中译本：《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009"],
                 "有人独处挺好|有人一天【熬不住】", 8,
                 ["书中观点均为转述：人对被冷落、被孤立的敏感程度天生有差别，作者引用的双生子研究显示孤独感有相当一部分"
                  "受遗传影响；作者把它比作一根“弹性的绳子”——基因决定绳子多长，环境和你的做法决定怎么用它。出处："
                  "John T. Cacioppo & William Patrick, Loneliness: Human Nature and the Need for Social Connection "
                  "(W. W. Norton, 2008)，中译本《孤独是可耻的》（约翰·卡乔波、威廉·帕特里克著，焦梦津译，中国人民大学"
                  "出版社 2009），第一部分相关章节。上屏均为转述，不是逐字引文；绳子的动态画面为对比喻的示意。",
                  "合租室友宅一周、周末翻通讯录、居家办公、聚会散场回家、夫妻周末一个想宅一个想出门、孩子刚上幼儿园均为"
                  "现实场景示意，不指向任何具体个人；时间、次数（如每晚视频 10 分钟、每周一条消息）为示意，不是数据。",
                  "四步做法（认清绳长不自责、按自己的需要定联系频率、提前约好周末、绳长的也留根线）为据书中思路整理的建议。"],
                 tags="#性格 #独处")
    return b.attach(ep)
