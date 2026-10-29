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


# ---------------------------------------------------------------- 开局：室友和你（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


scene("室友宅一周，天天乐", "灵魂拷问", (950, 800, 0.85), bars=2)
L(boxes(590, 440, 7, 120, 96), 0, 0.9, BLACK, 8, sfx="wood_high")
L(join(stick(720, 1170, 0.9, "up"), face(720, 1170, 0.9, "smile")), 1, 2, sfx="pop")
T("宅一周", 1200, 880, 76, RED, k0=2, sfx="pop")
for n in range(7):
    L(check(590 + n * 120, 440, 28), 3 + n * 0.14, 3.14 + n * 0.14, GREEN, 7, sfx="shaker" if n == 0 else None)
T("哈哈", 470, 820, 70, BLUE, k0=5, sfx="pop")

scene("你一天就熬不住，差在哪", "灵魂拷问", (2650, 820, 0.85), flashes=[6])
L(join(stick(2380, 1170, 0.9, "down"), face(2380, 1170, 0.9, "sad")), 0, 1, sfx="wood_high")
L(phone(2800, 980, 240, 380), 1, 1.9, BLACK, 9, sfx="pop")
T("小王", 2800, 870, 48, k0=2)
T("阿美", 2800, 950, 48, k0=3)
L(join(P((2700, 870), (2900, 870)), P((2700, 950), (2900, 950))), 4, 4.9, RED, 8, sfx="rim")
T("都在忙", 2800, 1230, 60, RED, k0=5, sfx="pop")
T("差在哪？", 2620, 1440, 110, RED, k0=6, k1=7, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 3–7）

scene("有本书研究过双胞胎", "孤独是可耻的", (2650, 2220, 0.85))
L(book(2650, 2150, 420, 280), 0, 1.2, sfx="wood_low")
T("孤独是可耻的", 2650, 1900, 76, GREEN, k0=2, sfx="pop")
T("卡乔波", 2650, 2400, 56, k0=4, sfx="pop")
T("拿双胞胎做研究", 2650, 2560, 60, RED, k0=5, sfx="pop")

scene("怕被冷落，有天生的", "书中观点 · 天生差别", (2950, 3560, 0.85), shake=[0], flashes=[0])
T("天生", 2950, 3300, 170, RED, k0=0, k1=0.8, sfx="kick")
L(join(stick(2700, 3490, 0.9), face(2700, 3490, 0.9, "smile")), 2, 3, sfx="wood_high")
L(join(stick(3200, 3490, 0.9), face(3200, 3490, 0.9, "smile")), 3, 4, sfx="wood_high")
T("一部分随基因", 2950, 3660, 60, k0=5, sfx="pop")
L(underline(2770, 3130, 3710, 10, 30), 7, 7.6, RED, 7, sfx="ding")

scene("作者比作弹性绳子", "书中比喻 · 弹性的绳子", (1740, 3950, 0.8))
T("弹性的绳子", 1740, 3430, 84, GREEN, k0=0, sfx="pop")
L(node(*ANCH, 120), 2, 2.8, BLACK, 9, sfx="wood_high")
T("身边人", ANCH[0], ANCH[1], 50, k0=2.8)
b.custom(J(), 4, 5.5, rope_fn(True), sfx="pop")
b.custom(J(), 6, 7.5, rope_fn(False), sfx="wood_high")

scene("长绳走远，短绳扯得慌", "书中比喻 · 长绳和短绳", (1740, 3950, 0.8), shake=[6])
T("长绳", 1550, 3600, 60, ORANGE, k0=0, sfx="pop")
WALK["long"] = (J(), 1)
H(1, "shaker")
T("自在", 1950, 3560, 56, BLUE, k0=3, sfx="ding")
T("短绳", 1550, 4400, 60, ORANGE, k0=4, sfx="pop")
WALK["short"] = (J(), 5)
H(5, "shaker")
H(6, "kick", 0.9)
T("扯得慌", 1700, 4260, 60, RED, k0=7, sfx="rim")

scene("长短天生，用法在你", "书中观点 · 一张图", (1700, 4050, 0.62))
L(rect(1740, 3960, 1500, 1250, 40), 0, 1, GREEN, 8, sfx="wood_high")
T("室友", 2230, 3470, 56, BLUE, k0=1, sfx="pop")
T("你", 1780, 4400, 64, BLUE, k0=2, sfx="pop")
T("天生：定长短", 2170, 4000, 60, RED, k0=3, sfx="pop")
T("后天：怎么用", 2170, 4090, 60, BLUE, k0=5, sfx="pop")
T("环境 · 做法", 2170, 4180, 48, k0=6.5, k1=7.9)

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

scene("居家三天就想见人", "例子 · 居家办公", (930, 6200, 0.85))
L(desk(700, 6360, 300), 0, 0.9, sfx="wood_high")
L(join(stick(1010, 6500, 0.85), face(1010, 6500, 0.85, "flat")), 1, 2, sfx="pop")
T("居家第三天", 900, 5910, 64, RED, k0=2, sfx="pop")
L(building(1400, 6460, 180, 300), 4, 4.9, BLACK, 8, sfx="wood_high")
L(arrow((1090, 6280), (1290, 6280), 0.1, 34), 5, 5.8, GREEN, 8, sfx="shaker")
T("想见人", 1150, 6100, 60, RED, k0=6, sfx="pop")

scene("聚会散了，有人发慌", "例子 · 散场回家", (2690, 6200, 0.85))
L(house(2330, 6500, 240, 210), 0, 0.9, sfx="wood_high")
L(join(stick(2680, 6500, 0.75), face(2680, 6500, 0.75, "flat")), 1, 1.9, sfx="wood_high")
L(smiley(3050, 6100, 60, "smile"), 2, 2.8, BLUE, 8, sfx="pop")
T("松口气", 2860, 6100, 50, BLUE, k0=3)
L(smiley(3050, 6400, 60, "sad"), 4, 4.8, RED, 8, sfx="rim")
T("发慌", 2880, 6400, 50, RED, k0=5, sfx="tom")

KX = 1800                                  # 幼儿园一屏居中，下方接三条做法
scene("有的玩开，有的哭一天", "例子 · 上幼儿园", (KX + 40, 7500, 0.85), shake=[6])
L(building(KX, 7450, 300, 330), 0, 0.9, BLACK, 8, sfx="wood_high")
T("幼儿园", KX - 390, 7000, 60, k0=1, sfx="pop")
L(join(stick(KX - 350, 7500, 0.55, "up"), face(KX - 350, 7500, 0.55, "smile")), 2, 2.9, BLUE, 8, sfx="pop")
T("玩开了", KX - 350, 7240, 50, BLUE, k0=3)
L(join(stick(KX + 400, 7500, 0.55), face(KX + 400, 7500, 0.55, "sad"), tears(KX + 400, 7500 - 290 * 0.55)), 4, 4.9,
  BLACK, 8, sfx="rim")
T("哭一天", KX + 400, 7240, 50, RED, k0=5, sfx="tom")
T("绳子长短不一样", KX, 7760, 90, ORANGE, k0=6, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

scene("认清绳长，别骂自己", "第一步 · 认清绳长", (950, 8790, 0.85))
L(rect(950, 8790, 1200, 860, 40), 0, 0.8, GREEN, 8, sfx="wood_low")
T("① 认清绳长", 950, 8470, 76, BLUE, k0=1, sfx="pop")
L(join(P((620, 8620), (1280, 8620)), *[P((620 + i * 110, 8590), (620 + i * 110, 8650)) for i in range(7)]), 3, 3.9,
  ORANGE, 8, sfx="wood_high")
T("我太黏人了", 760, 8810, 56, k0=4, sfx="pop")
L(P((610, 8810), (910, 8810)), 6, 6.5, RED, 10, sfx="rim")
T("正常", 1200, 8810, 64, GREEN, k0=7, k1=7.6, sfx="pop")
L(check(1320, 8805, 34), 7.6, 7.95, GREEN, 9)

scene("多久联系，自己定", "第二步 · 定频率", (2650, 8790, 0.85))
L(rect(2650, 8790, 1200, 860, 40), 0, 0.8, GREEN, 8, sfx="wood_low")
T("② 定联系频率", 2650, 8470, 76, BLUE, k0=1, sfx="pop")
L(phone(2650, 8680, 90, 150), 3, 3.9, BLUE, 8, sfx="wood_high")
T("短绳：每晚视频", 2650, 8890, 54, k0=4, sfx="pop")
T("长绳：每周聊一次", 2650, 9060, 54, k0=6, sfx="pop")

C3 = (1800, 9740)
scene("周末提前约好", "第三步 · 约周末", (1800, 9800, 0.85))
L(rect(*C3, 1200, 860, 40), 0, 0.8, GREEN, 8, sfx="wood_low")
T("③ 提前约周末", 1800, 9420, 76, BLUE, k0=1, sfx="pop")
L(boxes(1440, 9620, 7, 120, 100), 2.75, 3.4, BLACK, 7)
for n, d in enumerate("一二三四五六日"):
    T(d, 1440 + n * 120, 9620, 50, k0=3.4 + n * 0.08, k1=3.55 + n * 0.08)
L(circle(1680, 9620, 70), 4, 4.8, RED, 8, sfx="pop")
L(circle(2040, 9620, 70), 5, 5.8, GREEN, 8, sfx="pop")
T("周三约 → 周六见", 1800, 9810, 58, RED, k0=6, k1=7.9, sfx="pop")

scene("评论区聊聊", "评论区见", (1800, 9700, 0.3))
H(0, "cymbal", 0.5)
H(2, "ding", 0.7)
T("你的绳子长还是短？", 1800, 10500, 160, RED, k0=4, sfx="pop")
T("下一讲：被同事晾在一边，为什么那么难受？", 1800, 10800, 130, k0=8, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


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
