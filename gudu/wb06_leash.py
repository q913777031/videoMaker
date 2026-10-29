"""06 弹性的绳子（白板手绘版）：有人独处挺好，有人一天都熬不住？

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

from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, building, check, circle, clock,
                               cross, desk, face, hands_at, join, marker, node, partial, rect, scribble, stick,
                               underline)
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#B5654A"
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

ANCH = (1150, 3950)                       # 绳子另一头：身边人
WALK = {}                                 # 'long' / 'short' -> 走动的镜头序号


def rope_fn(long: bool):
    """一个人 + 拴在“身边人”上的绳子。长绳：走远了绳子还松着；短绳：走几步就绷直、被扯回来。"""
    ax, ay = (1250, 3870) if long else (1250, 4030)
    fy = 3800 if long else 4420
    Lr = 1500 if long else 720
    x_home = 1650
    dy = (fy - 140) - ay
    reach = ax + math.sqrt(Lr * Lr - dy * dy) + 10 - 1       # 短绳绷直时人的位置

    def where(t):
        jw = WALK.get("long" if long else "short")
        if jw is None:
            return x_home, 0.0, None
        t0 = b.t_of(jw, 0)
        if long:
            e = ease_io((t - t0) / (b.t_of(jw, 1.6) - t0))
            bob = 12 * abs(math.sin(e * math.pi * 4)) if 0 < e < 1 else 0.0
            return x_home + 600 * e, bob, None
        tt = b.t_of(jw, 1)
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


# ---------------------------------------------------------------- 开局：室友和你（镜头 1–6）

b.shot("室友宅了一周", "灵魂拷问", view=(950, 850, 0.85))
L(boxes(590, 520, 7, 120, 96), 0, 0.8, BLACK, 8, sfx="wood_high")
L(stick(720, 1250, 0.9, "up"), 1, 1.6, sfx="pop")
L(face(720, 1250, 0.9, "smile"), 1.6, 1.75)
T("室友", 720, 890, 56, k0=1.75, k1=2.0)
T("宅一周", 1200, 960, 76, RED, k0=2, sfx="pop")
for n in range(7):
    L(check(590 + n * 120, 520, 28), 3 + n * 0.1, 3.1 + n * 0.1, GREEN, 7, sfx="shaker" if n == 0 else None)

b.shot("他天天乐呵呵", "灵魂拷问", view=(950, 900, 0.85))
T("追剧", 1200, 1110, 64, k0=0, sfx="pop")
T("外卖", 1200, 1220, 64, k0=1, sfx="pop")
T("哈哈", 470, 900, 70, BLUE, k0=2, sfx="ding")
L(underline(1090, 1310, 1270, 10, 30), 3, 3.4, GREEN, 7, sfx="wood_high")

b.shot("你一个周末就难受", "灵魂拷问", view=(2650, 850, 0.85))
L(stick(2420, 1250, 0.9, "down"), 0, 0.6, sfx="wood_high")
L(face(2420, 1250, 0.9, "sad"), 0.6, 0.75)
T("你", 2420, 890, 64, BLUE, k0=1, sfx="pop")
L(clock(2930, 650, 110), 2, 2.6, sfx="wood_high")
L(hands_at(2930, 650, 110, 3, 0), 2.6, 2.8, RED, 10)
T("周六下午", 2930, 830, 60, RED, k0=3, sfx="pop")

b.shot("周日翻遍通讯录", "灵魂拷问", view=(2650, 900, 0.85))
L(phone(2930, 1060, 240, 380), 0, 0.6, BLACK, 9, sfx="pop")
for n, w in enumerate(("小王", "阿美", "老同学")):
    T(w, 2930, 950 + n * 80, 48, k0=1 + n * 0.2, k1=1.2 + n * 0.2, sfx="wood_high" if n == 0 else None)
for n in range(3):
    L(P((2830, 950 + n * 80), (3030, 950 + n * 80)), 2 + n * 0.15, 2.15 + n * 0.15, RED, 8,
      sfx="rim" if n == 0 else None)
T("都在忙", 2930, 1310, 60, RED, k0=3, sfx="pop")

b.shot("一天都熬不住", "灵魂拷问", view=(950, 1750, 0.85))
L(window(620, 1580, 260), 0, 0.7, BLACK, 9, sfx="wood_high")
L(stick(1080, 2100, 0.9, "down"), 1, 1.6, sfx="pop")
L(face(1080, 2100, 0.9, "sad"), 1.6, 1.75)
L(scribble(1080, 1560, 260, 110, 7), 2, 2.5, RED, 7, sfx="shaker")
T("心里空落落", 950, 2240, 64, RED, k0=3, sfx="pop")

b.shot("差别咋这么大？", "灵魂拷问", view=(1800, 1350, 0.355), flashes=[0])
T("？", 2650, 1800, 380, RED, k0=0, k1=0.6, sfx="kick")
L(arrow((1300, 700), (2300, 700), 0.12, 50), 1, 1.6, GREEN, 9, sfx="wood_high")
T("差在哪", 2650, 2180, 110, k0=2, k1=2.8, sfx="pop")
H(3, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "孤独是可耻的", view=(950, 2950, 0.85))
L(book(950, 2950, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 950, 2720, 76, GREEN, k0=1, sfx="pop")
T("卡乔波", 950, 3200, 56, k0=2, sfx="pop")

b.shot("拿双胞胎做研究", "书中研究 · 双胞胎", view=(2650, 2950, 0.85))
T("双胞胎研究", 2650, 2540, 70, k0=0, sfx="pop")
L(stick(2400, 3250, 0.9), 1, 1.6, sfx="wood_high")
L(face(2400, 3250, 0.9, "smile"), 1.6, 1.75)
L(stick(2900, 3250, 0.9), 2, 2.6, sfx="wood_high")
L(face(2900, 3250, 0.9, "smile"), 2.6, 2.75)

b.shot("怕被冷落，有天生的", "书中观点 · 天生差别", view=(2650, 3000, 0.85), shake=[0], flashes=[0])
T("天生", 2650, 3060, 170, RED, k0=0, k1=0.5, sfx="kick")
T("一部分随基因", 2650, 3420, 60, k0=2, sfx="pop")
L(underline(2470, 2830, 3470, 10, 30), 3, 3.4, RED, 7, sfx="ding")

b.shot("作者打了个比方", "书中比喻 · 弹性的绳子", view=(1700, 3950, 0.8))
T("弹性的绳子", 1700, 3430, 84, GREEN, k0=0, sfx="pop")
L(node(*ANCH, 120), 1, 1.5, BLACK, 9, sfx="wood_high")
T("身边人", ANCH[0], ANCH[1], 50, k0=2, sfx="pop")

b.shot("一根有弹性的绳", "书中比喻 · 弹性的绳子", view=(1700, 3950, 0.8))
b.custom(J(), 0, 1.4, rope_fn(True), sfx="pop")
b.custom(J(), 2, 3.4, rope_fn(False), sfx="wood_high")

b.shot("绳长天生不一样", "书中观点 · 绳子长短", view=(1700, 3950, 0.8))
T("长绳", 1450, 3600, 60, ORANGE, k0=0, sfx="pop")
T("短绳", 1450, 4400, 60, ORANGE, k0=1, sfx="pop")
T("天生：定长短", 2150, 4000, 60, RED, k0=2, sfx="pop")
H(3, "ding", 0.6)

WALK["long"] = b.shot("绳长，走远也自在", "书中比喻 · 长绳", view=(1700, 3950, 0.8))
H(0, "shaker")
T("自在", 2000, 3560, 56, BLUE, k0=2, sfx="pop")
H(3, "ding", 0.6)

WALK["short"] = b.shot("绳短，一走就扯", "书中比喻 · 短绳", view=(1700, 3950, 0.8), shake=[1])
H(0, "shaker")
H(1, "kick", 0.9)
T("扯得慌", 2170, 4330, 60, RED, k0=2, sfx="rim")

b.shot("怎么用，看后天", "书中观点 · 怎么用", view=(1700, 3950, 0.8))
T("后天：怎么用", 2150, 4090, 60, BLUE, k0=0, sfx="pop")
T("环境 · 做法", 2150, 4180, 48, k0=2, sfx="pop")

b.shot("长短天生，用法在你", "书中观点 · 一张图", view=(1700, 3960, 0.62))
L(rect(1700, 3960, 1550, 1250, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
L(underline(1500, 1900, 3490, 10, 30), 2, 2.4, RED, 7, sfx="ding")

b.shot("室友绳长，你绳短", "书中观点 · 对上号", view=(1700, 3950, 0.8))
T("室友", 2250, 3470, 56, BLUE, k0=0, sfx="pop")
T("你", 1780, 4400, 64, BLUE, k0=1, sfx="pop")
H(2, "ding", 0.6)

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5400), (2650, 5400), (950, 6350), (2650, 6350)]
b.shot("身边也常见", "身边的例子", view=(1800, 5880, 0.355))
T("身边的例子", 1800, 4820, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("居家办公一整周", "例子 · 居家办公", view=(950, 5400, 0.85))
L(desk(700, 5560, 300), 0, 0.7, sfx="wood_high")
L(stick(1010, 5700, 0.85), 1, 1.6, sfx="pop")
L(face(1010, 5700, 0.85, "flat"), 1.6, 1.75)
T("周一 → 周五", 900, 5110, 64, k0=2, sfx="pop")

b.shot("第三天就想去公司", "例子 · 居家办公", view=(950, 5450, 0.85))
T("第三天", 560, 5300, 60, RED, k0=0, sfx="pop")
L(building(1400, 5660, 180, 300), 1, 1.6, BLACK, 8, sfx="wood_high")
L(arrow((1080, 5400), (1290, 5330), 0.12, 34), 1.6, 1.9, GREEN, 8)
T("想见人", 1010, 5800, 60, RED, k0=2, sfx="pop")

b.shot("聚会散了回家", "例子 · 散场回家", view=(2650, 5400, 0.85))
L(house(2330, 5700, 240, 210), 0, 0.8, sfx="wood_high")
L(moon(2700, 5110, 80), 1, 1.5, BLACK, 8, sfx="pop")
L(stick(2680, 5700, 0.75), 2, 2.5, sfx="wood_high")
L(face(2680, 5700, 0.75, "flat"), 2.5, 2.65)
T("散场", 2330, 5080, 60, k0=3, sfx="pop")

b.shot("有人松口气，有人慌", "例子 · 散场回家", view=(2650, 5450, 0.85))
L(smiley(3050, 5300, 60, "smile"), 0, 0.5, BLUE, 8, sfx="pop")
T("松口气", 3050, 5430, 50, BLUE, k0=0.5, k1=0.9)
L(smiley(3050, 5600, 60, "sad"), 2, 2.5, RED, 8, sfx="rim")
T("发慌", 3050, 5730, 50, RED, k0=2.5, k1=2.8)

b.shot("周末他想宅家", "例子 · 夫妻周末", view=(950, 6350, 0.85))
L(stick(650, 6700, 0.85), 0, 0.6, sfx="wood_high")
L(face(650, 6700, 0.85, "smile"), 0.6, 0.75)
T("宅", 650, 6230, 110, BLACK, k0=1, k1=1.3, sfx="pop")
T("在家躺", 650, 6800, 54, k0=2, sfx="pop")

b.shot("她想约朋友出门", "例子 · 夫妻周末", view=(950, 6350, 0.85))
L(stick(1250, 6700, 0.85, "point"), 0, 0.6, BLUE, sfx="wood_high")
L(face(1250, 6700, 0.85, "smile"), 0.6, 0.75, BLUE)
T("出门！", 1250, 6210, 64, RED, k0=1, sfx="pop")
L(scribble(950, 6400, 120, 120, 6), 2, 2.4, RED, 7, sfx="rim")

b.shot("孩子刚上幼儿园", "例子 · 上幼儿园", view=(2650, 6350, 0.85))
L(building(2650, 6650, 300, 330), 0, 0.8, BLACK, 8, sfx="wood_high")
T("幼儿园", 2260, 6200, 60, k0=1, sfx="pop")
L(join(P((2650, 6320), (2650, 6200)), P((2650, 6200), (2740, 6230), (2650, 6260))), 2, 2.4, RED, 8, sfx="pop")

b.shot("有的玩开，有的哭", "例子 · 上幼儿园", view=(2650, 6400, 0.85))
L(stick(2300, 6700, 0.55, "up"), 0, 0.5, BLUE, 8, sfx="pop")
L(face(2300, 6700, 0.55, "smile"), 0.5, 0.6, BLUE)
T("玩开了", 2300, 6440, 50, BLUE, k0=1, sfx="pop")
L(stick(3050, 6700, 0.55), 2, 2.5, BLACK, 8, sfx="rim")
L(join(face(3050, 6700, 0.55, "sad"), tears(3050, 6700 - 290 * 0.55)), 2.5, 2.7, BLUE, 6)
T("哭一天", 3050, 6440, 50, RED, k0=3, sfx="pop")

b.shot("绳子长短不一样", "身边的例子", view=(1800, 5880, 0.355))
for n, ((x, y), w) in enumerate(zip(CARDS, ("短绳", "有长有短", "一长一短", "有长有短"))):
    T(w, x + 330 if n else x + 380, y - 330, 80, ORANGE, k0=n, sfx="pop")

b.shot("长短都正常", "身边的例子", view=(1800, 5880, 0.355), shake=[0])
T("长短都正常", 1800, 6970, 125, GREEN, k0=0, k1=0.8, sfx="kick")
L(check(2290, 6960, 60), 2, 2.3, GREEN, 12, sfx="ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 7850), (2650, 7850), (950, 8800), (2650, 8800)]
b.shot("照着绳长来安排", "具体做法", view=(1800, 8330, 0.355))
T("按你的绳长来", 1800, 7250, 130, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 860, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先认清你的绳长", "第一步 · 认清绳长", view=(950, 7850, 0.85))
T("① 认清绳长", 950, 7530, 76, BLUE, k0=0, sfx="pop")
L(join(P((620, 7680), (1280, 7680)), *[P((620 + i * 110, 7650), (620 + i * 110, 7710)) for i in range(7)]), 1, 1.6,
  ORANGE, 8, sfx="wood_high")
T("我的绳：短", 950, 7800, 60, k0=2, sfx="pop")

b.shot("熬不住，别骂自己", "第一步 · 认清绳长", view=(950, 7850, 0.85))
T("我太黏人了", 760, 7940, 56, k0=0, sfx="pop")
L(P((610, 7940), (910, 7940)), 1, 1.3, RED, 10, sfx="rim")
T("正常", 1200, 7940, 64, GREEN, k0=2, sfx="pop")
L(check(1320, 7935, 34), 3, 3.3, GREEN, 9, sfx="ding")

b.shot("记下啥时最难受", "第一步 · 认清绳长", view=(950, 7900, 0.85))
L(clock(560, 8120, 70), 0, 0.6, sfx="wood_high")
L(hands_at(560, 8120, 70, 4, 0), 0.6, 0.8, RED, 8)
T("周日下午", 820, 8130, 52, k0=1, sfx="pop")
T("下班到家", 1180, 8130, 52, k0=2, sfx="pop")

b.shot("多久联系，自己定", "第二步 · 定频率", view=(2650, 7850, 0.85))
T("② 定联系频率", 2650, 7530, 76, BLUE, k0=0, sfx="pop")
L(phone(2380, 7740, 90, 150), 1, 1.4, BLUE, 8, sfx="wood_high")
T("按自己的需要", 2780, 7740, 58, k0=2, sfx="pop")

b.shot("绳短就每晚通话", "第二步 · 定频率", view=(2650, 7900, 0.85))
T("短绳：每晚视频 10 分钟", 2600, 7950, 54, k0=0, k1=1.4, sfx="pop")
L(check(3020, 7945, 34), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("绳长的一周一次", "第二步 · 定频率", view=(2650, 7950, 0.85))
T("长绳：每周一条消息", 2600, 8120, 54, k0=0, k1=1.4, sfx="pop")
L(check(2960, 8115, 34), 2, 2.3, GREEN, 9, sfx="ding")

DAYS = "一二三四五六日"
b.shot("周末提前约好", "第三步 · 约周末", view=(950, 8800, 0.85))
T("③ 提前约周末", 950, 8480, 76, BLUE, k0=0, sfx="pop")
L(boxes(590, 8680, 7, 120, 100), 1, 1.6, BLACK, 7, sfx="wood_high")
for n, d in enumerate(DAYS):
    T(d, 590 + n * 120, 8680, 50, k0=1.6 + n * 0.05, k1=1.75 + n * 0.05)
L(circle(830, 8680, 70), 2, 2.4, RED, 8, sfx="pop")

b.shot("周三就把人约好", "第三步 · 约周末", view=(950, 8850, 0.85))
L(circle(1190, 8680, 70), 0, 0.4, GREEN, 8, sfx="pop")
L(arrow((860, 8600), (1160, 8600), 0.25, 30), 1, 1.4, RED, 7, sfx="wood_high")
T("周三约 → 周六见", 950, 8870, 58, RED, k0=2, sfx="pop")

b.shot("约不到就报个班", "第三步 · 约周末", view=(950, 8900, 0.85))
T("羽毛球 · 读书会", 950, 9040, 56, k0=0, sfx="pop")
L(check(1290, 9035, 34), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("绳长的也留根线", "第四步 · 留根线", view=(2650, 8800, 0.85))
T("④ 绳长也留根线", 2650, 8480, 76, BLUE, k0=0, sfx="pop")
L(stick(2350, 8900, 0.7), 1, 1.5, sfx="wood_high")
L(face(2350, 8900, 0.7, "smile"), 1.5, 1.6)
L(node(3000, 8720, 75), 2, 2.3, BLACK, 8, sfx="pop")
T("老友", 3000, 8720, 46, k0=2.3, k1=2.6)
L(P((2400, 8760), (2925, 8730)), 3, 3.4, ORANGE, 6, sfx="wood_high")

b.shot("常给老友发消息", "第四步 · 留根线", view=(2650, 8850, 0.85))
L(rect(2900, 8960, 300, 110, 40), 0, 0.5, BLACK, 7, sfx="wood_high")
T("最近咋样？", 2900, 8960, 48, k0=1, sfx="pop")
L(check(3110, 9080, 34), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("知道绳长，用好它", "一句话", view=(1800, 6000, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 9620, 0.8))
T("你的绳子长还是短？", 1800, 9540, 80, RED, k0=0.5, k1=1.8)
T("下一讲：被同事晾在一边，为什么那么难受？", 1800, 9700, 48, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(J(), 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "leash", "弹性的绳子", "有人独处挺好，有人一天都熬不住？", ACC, b.shots,
                 [f"{BOOK}（转述）：对被冷落的敏感度天生有差别、双生子研究、“弹性的绳子”比喻",
                  "中译本：《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009"],
                 "有人独处挺好|有人一天【熬不住】", 15,
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
