"""07 公地悲剧（白板手绘版）：公司冰箱为什么总是乱糟糟？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。

叙事：打工人切身问题开局（公司冰箱塞满没人认的饭盒，剩菜放了一周，谁都不收拾，自己也放了就走）→ 书中观点（哈丁的
公共草场：每家多放一头牛，多赚的归自己，草被啃秃大家一起摊；画成一张图：好处一个人拿、代价大家摊、草场的状况传不到
放牛的人那里，于是越放越多）→ 身边的例子（会议室开完不收、工作群刷屏、楼道堆杂物、家里水槽堆碗）→ 具体做法（书中三条路：
讲道理、分到个人、一起定规矩并轮流看着；最后回到冰箱）→ 评论区互动。
书中观点为转述（Meadows, Thinking in Systems, 2008；中译本《系统之美》，邱昭良译，浙江人民出版社 2012）；
“公地悲剧”一词与草场放牧的例子出自 Garrett Hardin, The Tragedy of the Commons, Science, 1968；
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, cross,
                               doc, face, join, marker, node, rect, scribble, stick, underline)
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#A0663A"
SQUARE_SHOT = 1

b = Board(size=(3600, 8600))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


FW, FH = 380, 660                                   # 冰箱尺寸（s=1）


def fridge(x, y, s=1.0, open_door=False) -> skia.Path:
    """双门冰箱：(x, y) 为中心；上冷冻、下冷藏两层隔板。"""
    w, h = FW * s, FH * s
    top = y - h / 2
    parts = [rect(x, y, w, h, 30 * s), P((x - w / 2, top + 200 * s), (x + w / 2, top + 200 * s)),
             P((x + w / 2 - 34 * s, top + 60 * s), (x + w / 2 - 34 * s, top + 150 * s))]
    if open_door:
        parts += [P((x - w / 2 + 20 * s, top + 330 * s), (x + w / 2 - 20 * s, top + 330 * s)),
                  P((x - w / 2 + 20 * s, top + 460 * s), (x + w / 2 - 20 * s, top + 460 * s))]
    else:
        parts.append(P((x + w / 2 - 34 * s, top + 240 * s), (x + w / 2 - 34 * s, top + 360 * s)))
    return join(*parts)


def fridge_door(x, y, s=1.0) -> skia.Path:
    """冷藏室门打开（向右斜开）。"""
    w, h = FW * s, FH * s
    top = y - h / 2
    return join(P((x + w / 2, top + 200 * s), (x + w / 2 + 170 * s, top + 160 * s), (x + w / 2 + 170 * s, y + h / 2 + 40 * s),
                  (x + w / 2, y + h / 2)),
                P((x + w / 2 + 40 * s, top + 300 * s), (x + w / 2 + 40 * s, top + 420 * s)))


def shelf_y(y, row, s=1.0):
    """冷藏室三层的放物底线（row 0–2）。"""
    top = y - FH * s / 2
    return top + (330, 460, 640)[row] * s


def box(x, base, w=90, h=66) -> skia.Path:
    """饭盒：底边中点 (x, base)。"""
    return join(rect(x, base - h / 2, w, h, 10), P((x - w / 2 + 6, base - h + 16), (x + w / 2 - 6, base - h + 16)))


def cow(x, y, s=1.0) -> skia.Path:
    """奶牛（侧视，头朝右）：(x, y) 为地面中点。"""
    return join(rect(x, y - 130 * s, 220 * s, 110 * s, 40 * s),
                *[P((x + dx * s, y - 78 * s), (x + dx * s, y)) for dx in (-80, -50, 50, 80)],
                circle(x + 140 * s, y - 175 * s, 42 * s),
                P((x + 118 * s, y - 210 * s), (x + 106 * s, y - 242 * s)),
                P((x + 160 * s, y - 210 * s), (x + 172 * s, y - 242 * s)),
                P((x - 110 * s, y - 165 * s), (x - 150 * s, y - 105 * s)),
                circle(x - 30 * s, y - 135 * s, 22 * s))


def tuft(x, y, h=48) -> skia.Path:
    return P((x - 22, y), (x - 12, y - h * 0.8), (x, y), (x + 10, y - h), (x + 22, y))


def dashed(a, c_, bend=0.2, n=11, head=40) -> skia.Path:
    """虚线箭头（二次曲线取样后隔段描）。"""
    (x0, y0), (x1, y1) = a, c_
    mx, my = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend

    def q(t):
        return ((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1,
                (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1)

    segs = [P(q(i / (2 * n - 1)), q((i + 0.6) / (2 * n - 1))) for i in range(0, 2 * n - 1, 2)]
    ang = math.atan2(y1 - my, x1 - mx)
    for d in (0.45, -0.45):
        segs.append(P((x1, y1), (x1 - head * math.cos(ang + d), y1 - head * math.sin(ang + d))))
    return join(*segs)


def phone(x, y, w=300, h=540) -> skia.Path:
    return join(rect(x, y, w, h, 40), P((x - 40, y - h / 2 + 34), (x + 40, y - h / 2 + 34)),
                circle(x, y + h / 2 - 36, 16))


def bike(x, y, s=1.0) -> skia.Path:
    """自行车（侧视）：(x, y) 为地面中点。"""
    r = 70 * s
    return join(circle(x - 110 * s, y - r, r), circle(x + 110 * s, y - r, r),
                P((x - 110 * s, y - r), (x - 20 * s, y - 170 * s), (x + 80 * s, y - 170 * s), (x + 110 * s, y - r)),
                P((x - 20 * s, y - 170 * s), (x, y - r), (x + 80 * s, y - 170 * s)),
                P((x - 50 * s, y - 190 * s), (x + 10 * s, y - 190 * s)),
                P((x + 80 * s, y - 170 * s), (x + 95 * s, y - 220 * s), (x + 140 * s, y - 220 * s)))


def sink(x, y, w=520) -> skia.Path:
    """水槽：(x, y) 为台面中点。"""
    return join(P((x - w / 2 - 60, y), (x + w / 2 + 60, y)),
                P((x - w / 2, y), (x - w / 2 + 40, y + 150), (x + w / 2 - 40, y + 150), (x + w / 2, y)),
                P((x + w / 2 - 30, y), (x + w / 2 - 30, y - 150), (x + w / 2 - 130, y - 150), (x + w / 2 - 130, y - 115)))


def stink(x, y) -> skia.Path:
    """臭味波浪线三条（自下而上）。"""
    out = []
    for dx in (-40, 0, 40):
        p = skia.Path()
        p.moveTo(x + dx, y)
        for i in range(3):
            p.quadTo(x + dx + (18 if i % 2 == 0 else -18), y - 25 - i * 50, x + dx, y - 50 - i * 50)
        out.append(p)
    return join(*out)


# ---------------------------------------------------------------- 动态元件

GRASS = [(x, y) for y in (3060, 3250, 3575) for x in range(410, 1640, 100)]


def grass_fn(j_dry):
    """草场：画出时逐丛长出；j_dry 场景第 0–2 拍越啃越矮，第 2–4 拍啃光。"""

    def fn(c, k, t):
        h = 1.0 - 0.6 * clamp01((t - b.t_of(j_dry, 0)) / (b.t_of(j_dry, 2) - b.t_of(j_dry, 0)))
        h -= 0.4 * clamp01((t - b.t_of(j_dry, 2)) / (b.t_of(j_dry, 4) - b.t_of(j_dry, 2)))
        n = int(len(GRASS) * k)
        tip = None
        for (x, y) in GRASS[:n]:
            if h > 0.03:
                c.drawPath(tuft(x, y, 48 * h), marker(GREEN, 7))
            else:
                c.drawPath(P((x - 18, y), (x + 18, y)), marker("#9A8A6A", 5))
            tip = (x, y)
        return tip if k < 1 else None

    return fn


# ---------------------------------------------------------------- 开局：公司冰箱（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


FX, FY = 1150, 1150                                  # 冰箱中心
scene("冰箱里全是无主饭盒", "灵魂拷问", (1000, 1100, 0.82), punch=0.02)
L(fridge(FX, FY, 1.0, open_door=True), 0, 1.0, sfx="wood_low")
T("公司冰箱", 620, 880, 64, k0=1.2)
L(fridge_door(FX, FY), 2, 2.5, sfx="wood_high")
BOXES = [(1060, 0), (1220, 0), (1060, 1), (1230, 1)]
for n, (x, row) in enumerate(BOXES):
    L(box(x, shelf_y(FY, row)), 3 + n * 0.25, 3.25 + n * 0.25, sfx="pop" if n == 0 else None)
L(box(1110, shelf_y(FY, 2), 170, 110), 4.1, 4.5)
for n, (x, row) in enumerate(BOXES[:3]):
    T("？", x + 10, shelf_y(FY, row) - 100, 56, RED, k0=5 + n * 0.3, k1=5.2 + n * 0.3, sfx="pop" if n == 0 else None)

scene("你也放了就走", "灵魂拷问", (1000, 1100, 0.82))
T("剩菜", 1110, shelf_y(FY, 2) - 50, 48, k0=0, sfx="pop")
L(stink(1110, shelf_y(FY, 2) - 120), 1, 1.6, GREEN, 6, sfx="shaker")
T("放了7天", 1450, 800, 64, RED, k0=2, sfx="rim")
L(stick(600, 1450, 0.85, "hold"), 3, 3.6, BLUE, sfx="wood_high")
L(face(600, 1450, 0.85, "flat"), 3.6, 3.7, BLUE)
L(box(1230, shelf_y(FY, 2), 100, 80), 4, 4.3, BLUE, sfx="pop")
L(arrow((520, 1250), (370, 1250), 0.1, 34), 5, 5.4, GREEN, 8, sfx="wood_high")

PEOPLE = (2350, 2700, 3050)
scene("冰箱怎么总这样？", "灵魂拷问", (2700, 1250, 0.82), flashes=[4])
for n, x in enumerate(PEOPLE):
    L(stick(x, 1420, 0.85, "shrug"), n * 0.3, n * 0.3 + 0.5, sfx="wood_high" if n == 0 else None)
    L(face(x, 1420, 0.85, "flat"), n * 0.3 + 0.5, n * 0.3 + 0.6)
for n, x in enumerate(PEOPLE):
    T(("谁放的？", "不认识", "不管了")[n], x, 1040, 56, RED if n == 2 else BLACK, k0=1 + n * 0.5,
      k1=1.4 + n * 0.5, sfx="pop" if n in (0, 2) else None)
L(underline(2970, 3130, 1075, 8, 26), 2.5, 2.8, RED, 6)
T("怎么总这样？", 2700, 1680, 100, RED, k0=4, k1=5.2, sfx="kick")
b.hit(J(), 5, "ding", 0.6)

# ---------------------------------------------------------------- 书中观点（场景 4–9）

j_book = scene("书里有片公共草场", "系统之美 · 书中例子", (1000, 3070, 0.64))
L(book(680, 2470, 330, 220), 0, 0.9, sfx="wood_low")
T("系统之美", 1200, 2420, 80, GREEN, k0=1, sfx="pop")
T("德内拉 · 梅多斯", 1200, 2530, 46, k0=1.8, k1=2.6)
L(rect(1000, 3270, 1300, 700, 20), 3, 3.6, BLACK, 8, sfx="wood_high")
b.custom(j_book, 4, 5, grass_fn(j_book + 2), sfx="shaker")
T("公共草场 · 哈丁 1968", 1000, 2972, 44, k0=3.6, k1=4.9)
for n, x in enumerate((600, 1000, 1400)):
    L(cow(x, 3230, 0.8), 5 + n * 0.25, 5.25 + n * 0.25, sfx="wood_high" if n == 0 else None)

REDCOWS = (680, 1080, 1480)
scene("多放一头，钱归自己", "书中例子 · 公共草场", (1000, 3400, 0.8), shake=[0], flashes=[0])
for n, x in enumerate(REDCOWS):
    L(cow(x, 3540, 0.8), 0, 0.45, RED, 10)
b.hit(J(), 0, "kick", 1.0, "红牛砸进草场")
for n, x in enumerate(REDCOWS):
    T("+1", x - 230, 3440, 72, RED, k0=1 + n * 0.5, k1=1.3 + n * 0.5, sfx="tom" if n == 0 else None)
b.hit(J(), 2, "tom", 0.7)
for n, x in enumerate(REDCOWS):
    T("¥", x + 120, 3330, 64, GREEN, k0=3 + n * 0.4, k1=3.3 + n * 0.4, sfx="pop" if n == 0 else None)
T("钱：归自己", 620, 3665, 64, GREEN, k0=5, k1=5.8, sfx="pop")

scene("最后谁都没草吃", "书中例子 · 公共草场", (1000, 3400, 0.8), shake=[4])
b.hit(J(), 0, "shaker", 0.7, "草变矮")
b.hit(J(), 2, "shaker", 0.6, "草啃光")
L(cross(1000, 3270, 300), 4, 4.5, RED, 14, sfx="tom")
T("损失：大家摊", 1080, 3665, 64, RED, k0=5, k1=6, sfx="rim")

RES = (2700, 3070)
ME = (2200, 2870)
NB = [(3200, 2870), (2200, 3290), (3200, 3290)]
VIEW_T = (2700, 3050, 0.8)
scene("书里叫它公地悲剧", "书中观点 · 公地悲剧", VIEW_T)
T("公地悲剧", 2700, 2510, 120, RED, k0=0, k1=0.8, sfx="pop")
L(underline(2450, 2950, 2580), 1, 1.4, RED, 8, sfx="ding")
T("书里的系统陷阱之一", 2700, 2650, 48, k0=1.5, k1=2.7)
L(node(*RES, 115), 3, 3.4, GREEN, 9, sfx="wood_high")
T("草场", RES[0], RES[1] + 18, 56, GREEN, k0=3.4, k1=3.8)
L(node(*ME, 80), 4, 4.4, RED, 9, sfx="pop")
T("我", ME[0], ME[1] + 18, 56, RED, k0=4.4, k1=4.7)
L(arrow((2590, 3010), (2285, 2905), -0.15, 40), 5, 5.3, GREEN, 10, sfx="wood_high")
T("好处全归我", 2470, 2790, 50, GREEN, k0=5.3, k1=6.0)

scene("代价四家一起摊", "书中观点 · 代价", VIEW_T)
for n, (x, y) in enumerate(NB):
    L(node(x, y, 80), n * 0.4, n * 0.4 + 0.3, sfx="pop" if n == 0 else None)
    T("邻居", x, y + 16, 46, k0=n * 0.4 + 0.3, k1=n * 0.4 + 0.5)
for n, (x, y) in enumerate([ME] + NB):
    dx, dy = x - RES[0], y - RES[1]
    d = math.hypot(dx, dy)
    a = (RES[0] + dx / d * 125, RES[1] + dy / d * 125)
    e = (x - dx / d * 90, y - dy / d * 90)
    k = 3 + (n - 1) * 0.3 if n else 4                 # 先画到三家邻居，最后一笔指回“我”（手停在左上，不挡邻居）
    L(arrow(a, e, 0.12 if n else -0.12, 30), k, k + 0.3, RED, 6, sfx={0: "wood_high", 1: "rim"}.get(n))
T("代价：四家分", 2700, 3260, 50, RED, k0=2, k1=2.8, sfx="pop")

scene("没人急，越放越多", "书中观点 · 反馈太弱", VIEW_T, shake=[5])
L(dashed((2600, 3150), (2180, 2960), 0.25), 0, 1.0, BLUE, 5, sfx="wood_low")
T("反馈太弱？", 2330, 3170, 50, BLUE, k0=1, k1=1.9, sfx="pop")
L(arrow((2140, 2760), (2260, 2760), 1.1, 30), 3, 3.6, RED, 8, sfx="wood_high")
T("越放越多", 2700, 2895, 50, RED, k0=3.8, k1=4.6)
L(scribble(RES[0], RES[1], 200, 200, 9), 5, 5.5, RED, 8, sfx="kick")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 4300), (2650, 4300), (950, 5300), (2650, 5300)]
CARD_T = ("会议室", "工作群", "楼道", "家里水槽")
scene("身边到处是公地", "身边的例子", (1800, 4650, 0.42))
T("身边的公地", 1800, 3770, 90, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), 1 + n, 1.45 + n, GREEN, 8, sfx="wood_high")
    T(CARD_T[n], x, y - (330 if n < 2 else 270), 70, k0=1.5 + n, k1=1.5 + n + 0.18 * len(CARD_T[n]) + 0.1)

scene("会议室开完没人收", "例子 · 会议室", (950, 4420, 0.85))
L(oval(950, 4330, 820, 260), 0, 0.5, sfx="wood_low")
for n, x in enumerate((700, 900, 1150)):
    L(join(rect(x, 4300, 50, 64, 8), P((x + 25, 4285), (x + 42, 4285), (x + 42, 4315), (x + 25, 4315))),
      1 + n * 0.2, 1.2 + n * 0.2, sfx="wood_high" if n == 0 else None)
L(doc(1030, 4370, 90, 110, 3), 1.7, 1.9)
L(scribble(950, 4330, 600, 160, 9), 2, 2.6, RED, 6, sfx="shaker")
L(stick(520, 4720, 0.75, "shrug"), 3, 3.6, BLUE, sfx="wood_high")
L(face(520, 4720, 0.75, "sad"), 3.6, 3.7, BLUE)
T("先收10分钟", 1150, 4560, 64, RED, k0=5, k1=5.9, sfx="rim")

scene("要紧通知被刷没了", "例子 · 工作群", (2650, 4330, 0.85))
L(phone(2500, 4360), 0, 0.4, sfx="wood_low")
for n in range(5):
    side = -1 if n % 2 == 0 else 1
    L(rect(2500 + side * 40, 4160 + n * 72, 170, 44, 18), 1 + n * 0.15, 1.15 + n * 0.15, BLACK, 6,
      sfx="shaker" if n == 0 else None)
T("99+", 2770, 4120, 70, RED, k0=2, sfx="pop")
T("通知", 2500, 4530, 50, RED, k0=3, sfx="pop")
L(arrow((2700, 4250), (2700, 4560), 0.0, 36), 3.5, 3.9, RED, 8)
L(stick(3050, 4720, 0.75), 4, 4.5, BLUE, sfx="wood_high")
L(face(3050, 4720, 0.75, "sad"), 4.5, 4.6, BLUE)
T("没看到", 3050, 4400, 56, BLUE, k0=5, sfx="pop")

scene("楼道堆满，出口堵死", "例子 · 楼道", (950, 5380, 0.85))
L(join(P((420, 5080), (420, 5650)), P((420, 5650), (1480, 5650))), 0, 0.4, sfx="wood_low")
for n, (x, y, w, h) in enumerate(((560, 5580, 200, 140), (580, 5440, 160, 140), (780, 5590, 170, 120))):
    L(rect(x, y, w, h, 8), 1 + n * 0.2, 1.2 + n * 0.2, sfx="wood_high" if n == 0 else None)
L(bike(1150, 5650, 0.85), 2, 2.6, sfx="wood_high")
L(rect(1150, 5180, 280, 90, 10), 3, 3.4, GREEN, 7, sfx="pop")
T("安全出口", 1150, 5196, 46, GREEN, k0=3.4, k1=4.1)
L(cross(780, 5520, 180), 5, 5.4, RED, 12, sfx="rim")

FAM = (2200, 2650, 3100)
scene("碗都等别人先洗", "例子 · 家里", (2650, 5350, 0.85))
L(sink(2650, 5300), 0, 0.5, sfx="wood_low")
for n in range(5):
    L(oval(2600 + (n % 2) * 30, 5270 - n * 34, 220, 44), 1 + n * 0.2, 1.2 + n * 0.2, BLACK, 7,
      sfx="wood_high" if n == 0 else None)
L(stink(2410, 5240), 2, 2.5, GREEN, 6, sfx="shaker")
for n, x in enumerate(FAM):
    L(stick(x, 5730, 0.55 if n < 2 else 0.42, "point"), 3 + n * 0.3, 3.4 + n * 0.3, sfx="wood_high" if n == 0 else None)
for n in range(3):
    x0, x1 = FAM[n], FAM[(n + 1) % 3]
    L(arrow((x0 + (70 if x1 > x0 else -70), 5480), (x1 + (-70 if x1 > x0 else 70), 5480), 0.18 if x1 > x0 else -0.12,
            30), 5 + n * 0.3, 5.3 + n * 0.3, RED, 7, sfx="rim" if n == 0 else None)

scene("账落不到个人头上", "身边的例子", (1800, 4800, 0.42), shake=[2])
T("人都没那么坏", 1800, 5880, 110, k0=0, k1=1.2, sfx="pop")
T("没人买单", 1800, 4810, 140, RED, k0=2, k1=2.6, sfx="kick")
for n, (x, y) in enumerate(CARDS):
    L(arrow((1800 + (x - 1800) * 0.2, 4800 + (y - 4800) * 0.25), (1800 + (x - 1800) * 0.55, 4800 + (y - 4800) * 0.55),
            0.1, 40), 3 + n * 0.5, 3.4 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 6750), (2650, 6750), (950, 7650), (2650, 7650)]
scene("书里第一条：讲道理", "第一条 · 讲道理", (950, 6800, 0.85))
L(rect(*SOL[0], 1500, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_low")
T("① 讲道理", 950, 6450, 80, BLUE, k0=1, sfx="pop")
L(stick(520, 7060, 0.8, "point"), 2, 2.5, sfx="wood_high")
L(face(520, 7060, 0.8, "smile"), 2.5, 2.6)
L(rect(1080, 6720, 620, 160, 16), 3, 3.3, ORANGE, 8, sfx="wood_high")
T("过期请带走", 1080, 6730, 56, k0=3.3, k1=4.0)
T("坚持3天", 820, 6970, 60, k0=4, k1=4.7, sfx="pop")
L(arrow((990, 6955), (1140, 6955), 0.0, 30), 4.8, 5.0, BLACK, 7)
T("又乱了", 1290, 6970, 60, RED, k0=5, sfx="rim")

ROWS = (6760, 6900, 7040)                         # 三格的底线
scene("一人一格，各管各的", "第二条 · 分到个人", (2650, 6800, 0.85))
L(rect(*SOL[1], 1500, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_low")
T("② 分到个人", 2650, 6450, 80, BLUE, k0=1, sfx="pop")
L(join(rect(2650, 6830, 800, 420, 16), P((2250, 6760), (3050, 6760)), P((2250, 6900), (3050, 6900))), 2,
  2.6, sfx="wood_high")
for n, w in enumerate(("小王", "小李", "阿美")):
    T(w, 2420, ROWS[n] - 50, 56, k0=3 + n * 0.35, k1=3.3 + n * 0.35, sfx="pop" if n == 0 else None)
for n in range(3):
    L(box(2700, ROWS[n] - 6, 110, 70), 4 + n * 0.3, 4.3 + n * 0.3, sfx="wood_high" if n == 0 else None)
for n in range(3):
    L(check(2930, ROWS[n] - 45, 36), 5 + n * 0.25, 5.2 + n * 0.25, GREEN, 9, sfx="ding" if n == 0 else None)

TB = (700, 7720)
scene("定好规矩轮流看着", "第三条 · 定规矩", (950, 7800, 0.85))
L(rect(*SOL[2], 1500, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_low")
T("③ 一起定规矩", 950, 7340, 76, BLUE, k0=1, k1=1.9, sfx="pop")
for n, x in enumerate((520, 700, 880)):
    L(stick(x, 7720, 0.5), 2 + n * 0.25, 2.3 + n * 0.25, sfx="wood_high" if n == 0 else None)
L(oval(*TB, 520, 90), 2.8, 3.0)
T("没写名字，周五清空", 950, 7870, 58, RED, k0=3, k1=4.2, sfx="pop")
T("值日表", 1330, 7440, 56, k0=4.3, k1=4.8)
for n, w in enumerate(("周一 小王", "周二 小李", "周三 阿美")):
    T(w, 1330, 7530 + n * 75, 48, k0=5 + n * 0.32, k1=5.3 + n * 0.32, sfx="pop" if n == 0 else None)

scene("冰箱清爽多了", "回到冰箱", (2650, 7820, 0.85))
L(rect(*SOL[3], 1500, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_low")
L(fridge(2400, 7680, 0.8, open_door=True), 1, 1.8, sfx="wood_high")
for n, w in enumerate(("小王", "小李", "阿美")):
    T(w, 2400, shelf_y(7680, n, 0.8) - 26, 46, k0=2 + n * 0.25, k1=2.2 + n * 0.25, sfx="pop" if n == 0 else None)
T("清爽！", 2930, 7560, 90, GREEN, k0=3, sfx="ding")
L(check(2930, 7700, 60), 4, 4.3, GREEN, 10, sfx="wood_high")

scene("公共的也得有人管", "一句话", (1800, 4600, 0.235))
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 2, "wood_high", 0.6)
b.hit(J(), 4, "ding")

scene("评论区聊聊", "评论区见", (1800, 8350, 0.8))
b.hit(J(), 0, "cymbal", 0.5)
T("你们公司的公地在哪？", 1800, 8250, 76, RED, k0=1, k1=2.6)
b.hit(J(), 1, "pop")
T("下一讲：标准为什么越来越低？", 1800, 8420, 48, k0=3, k1=4.5)
b.hit(J(), 3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "commons", "公地悲剧", "公司冰箱为什么总是乱糟糟？", ACC, b.shots,
                 [f"{BOOK}（Thinking in Systems: A Primer, 2008；转述）", "中译本：邱昭良译，浙江人民出版社 2012",
                  "Garrett Hardin, The Tragedy of the Commons, Science, 1968"],
                 "好处归自己|代价【大家摊】", 4,
                 ["书中观点均为转述：公地悲剧是书中列出的系统陷阱之一——每个使用者独享使用共享资源的好处，代价由所有人分摊，"
                  "资源状况反馈到使用者（决策者）那里太弱，资源被过度使用直至衰败；书中给出的出路有三条：教育与劝导、"
                  "把公地分给个人、共同商定规则并监督执行。出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)，"
                  "中译本《系统之美》（邱昭良译，浙江人民出版社 2012）；原书中文全文未逐字核对。",
                  "“公地悲剧”一词出自 Garrett Hardin 1968 年发表于 Science 的同名文章，公共草场放牧为其经典例子；"
                  "草场牛数、草变秃的过程为示意。",
                  "公司冰箱、会议室、工作群、楼道杂物、家里水槽均为现实场景示意，不指向任何具体公司或个人；"
                  "贴纸条、分格写名字、周五清空、值日表等做法为据书中三条出路整理的建议。"],
                 tags="#公地悲剧 #团队管理 #职场")
    return b.attach(ep)
