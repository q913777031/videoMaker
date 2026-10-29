"""07 公地悲剧（白板手绘版）：公司冰箱为什么总是乱糟糟？

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
SQUARE_SHOT = 4

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


def grass_fn(j_dry, j_gone):
    """草场：画出时逐丛长出；j_dry 镜头里越啃越矮，j_gone 镜头前两拍啃光。"""

    def fn(c, k, t):
        h = 1.0 - 0.6 * clamp01((t - b.t_of(j_dry, 0)) / (b.t_of(j_dry, 4) - b.t_of(j_dry, 0)))
        h -= 0.4 * clamp01((t - b.t_of(j_gone, 0)) / (b.t_of(j_gone, 2) - b.t_of(j_gone, 0)))
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


# ---------------------------------------------------------------- 开局：公司冰箱（镜头 1–6）

FX, FY = 1150, 1150                                  # 冰箱中心
b.shot("打开公司冰箱", "灵魂拷问", view=(1000, 1100, 0.82), punch=0.02)
L(fridge(FX, FY, 1.0, open_door=True), 0, 1.0, sfx="wood_low")
T("公司冰箱", 620, 880, 64, k0=1.2)
L(fridge_door(FX, FY), 2, 2.5, sfx="wood_high")

b.shot("全是没人认的", "灵魂拷问", view=(1000, 1100, 0.82))
BOXES = [(1060, 0), (1220, 0), (1060, 1), (1230, 1)]
for n, (x, row) in enumerate(BOXES):
    L(box(x, shelf_y(FY, row)), n * 0.25, n * 0.25 + 0.25, sfx="pop" if n == 0 else None)
L(box(1110, shelf_y(FY, 2), 170, 110), 1.1, 1.5)
for n, (x, row) in enumerate(BOXES[:3]):
    T("？", x + 10, shelf_y(FY, row) - 100, 56, RED, k0=2 + n * 0.3, k1=2.2 + n * 0.3, sfx="pop" if n == 0 else None)

b.shot("上周的剩菜还在", "灵魂拷问", view=(1000, 1100, 0.82))
T("剩菜", 1110, shelf_y(FY, 2) - 50, 48, k0=0, sfx="pop")
L(stink(1110, shelf_y(FY, 2) - 120), 1, 1.6, GREEN, 6, sfx="shaker")
T("放了7天", 1450, 800, 64, RED, k0=2, sfx="rim")

PEOPLE = (2350, 2700, 3050)
b.shot("谁都不想收拾", "灵魂拷问", view=(2700, 1100, 0.82))
for n, x in enumerate(PEOPLE):
    L(stick(x, 1420, 0.85, "shrug"), n * 0.3, n * 0.3 + 0.5, sfx="wood_high" if n == 0 else None)
    L(face(x, 1420, 0.85, "flat"), n * 0.3 + 0.5, n * 0.3 + 0.6)
for n, x in enumerate(PEOPLE):
    T(("谁放的？", "不认识", "不管了")[n], x, 1040, 56, RED if n == 2 else BLACK, k0=1.6 + n * 0.5,
      k1=2.0 + n * 0.5, sfx="pop" if n in (0, 2) else None)
L(underline(2970, 3130, 1075, 8, 26), 3.3, 3.6, RED, 6)

b.shot("你也放了就走", "灵魂拷问", view=(1000, 1100, 0.82))
L(stick(600, 1450, 0.85, "hold"), 0, 0.6, BLUE, sfx="wood_high")
L(face(600, 1450, 0.85, "flat"), 0.6, 0.7, BLUE)
L(box(1230, shelf_y(FY, 2), 100, 80), 1, 1.3, BLUE, sfx="pop")
L(arrow((520, 1250), (370, 1250), 0.1, 34), 2, 2.4, GREEN, 8, sfx="wood_high")

b.shot("冰箱怎么总这样？", "灵魂拷问", view=(1800, 1350, 0.42), flashes=[2])
T("？", 1800, 1640, 400, RED, k0=0, k1=0.6, sfx="kick")
T("怎么总这样", 1800, 1960, 110, k0=1.0, k1=2.0, sfx="pop")
b.hit(J(), 2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "系统之美", view=(880, 2390, 0.9))
L(book(750, 2380, 420, 280), 0, 1.0, sfx="wood_low")
T("系统之美", 750, 2160, 80, GREEN, k0=1.0, sfx="pop")
T("德内拉 · 梅多斯", 750, 2610, 46, k0=2.0, sfx="pop")

j_field = b.shot("一片公共草场", "书中例子 · 公共草场", view=(1000, 3330, 0.8))
j_dry, j_gone = j_field + 3, j_field + 4
L(rect(1000, 3270, 1300, 700, 20), 0, 0.8, BLACK, 8, sfx="wood_high")
b.custom(j_field, 1, 2.2, grass_fn(j_dry, j_gone), sfx="shaker")
T("公共草场", 680, 2850, 64, k0=2.2)
T("哈丁 · 1968", 1330, 2850, 50, k0=2.6)
for n, x in enumerate((600, 1000, 1400)):
    L(cow(x, 3230, 0.8), 3 + n * 0.25, 3.25 + n * 0.25, sfx="wood_high" if n == 0 else None)

REDCOWS = (680, 1080, 1480)
b.shot("每家都多放一头", "书中例子 · 公共草场", view=(1000, 3330, 0.8), shake=[0], flashes=[0])
for n, x in enumerate(REDCOWS):
    L(cow(x, 3540, 0.8), 0, 0.45, RED, 10)
b.hit(J(), 0, "kick", 1.0, "红牛砸进草场")
for n, x in enumerate(REDCOWS):
    T("+1", x - 230, 3440, 72, RED, k0=1 + n * 0.5, k1=1.3 + n * 0.5, sfx="tom" if n == 0 else None)
b.hit(J(), 2, "tom", 0.7)

b.shot("多赚的归自己", "书中例子 · 公共草场", view=(1000, 3330, 0.8))
for n, x in enumerate(REDCOWS):
    T("¥", x + 120, 3330, 64, GREEN, k0=n * 0.4, k1=n * 0.4 + 0.3, sfx="pop" if n == 0 else None)
T("钱：归自己", 620, 3700, 64, GREEN, k0=2, sfx="pop")

b.shot("草被啃得越来越秃", "书中例子 · 公共草场", view=(1000, 3330, 0.8))
b.hit(J(), 0, "shaker", 0.7, "草变矮")
T("损失：大家摊", 1250, 3700, 64, RED, k0=2, sfx="rim")

b.shot("最后谁都没草吃", "书中例子 · 公共草场", view=(1000, 3330, 0.8), shake=[2])
b.hit(J(), 0, "shaker", 0.6, "草啃光")
L(cross(1000, 3270, 300), 2, 2.5, RED, 14, sfx="tom")

b.shot("书里叫公地悲剧", "书中观点", view=(2700, 2720, 0.82))
T("公地悲剧", 2700, 2510, 120, RED, k0=0, k1=1.0, sfx="pop")
T("书里的系统陷阱之一", 2700, 2650, 48, k0=1.2)
L(underline(2450, 2950, 2580), 2, 2.5, RED, 8, sfx="ding")

RES = (2700, 3070)
ME = (2200, 2870)
NB = [(3200, 2870), (2200, 3340), (3200, 3340)]
b.shot("好处一个人拿", "书中观点 · 好处", view=(2700, 3090, 0.8))
L(node(*RES, 115), 0, 0.5, GREEN, 9, sfx="wood_high")
T("草场", RES[0], RES[1] + 18, 56, GREEN, k0=0.5)
L(node(*ME, 80), 1, 1.4, RED, 9, sfx="pop")
T("我", ME[0], ME[1] + 18, 56, RED, k0=1.4)
L(arrow((2590, 3010), (2285, 2905), -0.15, 40), 2, 2.5, GREEN, 10, sfx="wood_high")
T("好处全归我", 2470, 2790, 50, GREEN, k0=2.6)

b.shot("代价大家一起摊", "书中观点 · 代价", view=(2700, 3090, 0.8))
for n, (x, y) in enumerate(NB):
    L(node(x, y, 80), n * 0.3, n * 0.3 + 0.3, sfx="pop" if n == 0 else None)
    T("邻居", x, y + 16, 46, k0=n * 0.3 + 0.3, k1=n * 0.3 + 0.5)
for n, (x, y) in enumerate([ME] + NB):
    dx, dy = x - RES[0], y - RES[1]
    d = math.hypot(dx, dy)
    a = (RES[0] + dx / d * 125, RES[1] + dy / d * 125)
    e = (x - dx / d * 90, y - dy / d * 90)
    L(arrow(a, e, 0.12 if n else -0.12, 30), 2 + n * 0.2, 2.3 + n * 0.2, RED, 6, sfx="rim" if n == 0 else None)
T("代价：四家分", 2700, 3290, 50, RED, k0=3.0, k1=3.6)

b.shot("草少了没人急", "书中观点 · 反馈太弱", view=(2700, 3090, 0.8))
L(dashed((2600, 3150), (2180, 2960), 0.25), 0, 1.0, BLUE, 5, sfx="wood_low")
T("反馈太弱", 2330, 3170, 50, BLUE, k0=1.2)
T("？", 2110, 3010, 64, BLUE, k0=2, k1=2.3, sfx="pop")

b.shot("于是越放越多", "书中观点 · 用到衰败", view=(2700, 3090, 0.8), shake=[2])
L(arrow((2140, 2760), (2260, 2760), 1.1, 30), 0, 0.6, RED, 8, sfx="wood_high")
T("越放越多", 2700, 2895, 50, RED, k0=0.8)
L(scribble(RES[0], RES[1], 200, 200, 9), 2, 2.5, RED, 8, sfx="kick")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 4300), (2650, 4300), (950, 5300), (2650, 5300)]
b.shot("身边到处是公地", "身边的例子", view=(1800, 4650, 0.42))
T("身边的公地", 1800, 3760, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("会议室开完不收", "例子 · 会议室", view=(950, 4300, 0.85))
T("会议室", 950, 3970, 70, k0=0, sfx="pop")
L(oval(950, 4330, 820, 260), 0.6, 1.1)
for n, x in enumerate((700, 900, 1150)):
    L(join(rect(x, 4300, 50, 64, 8), P((x + 25, 4285), (x + 42, 4285), (x + 42, 4315), (x + 25, 4315))),
      1 + n * 0.2, 1.2 + n * 0.2, sfx="wood_high" if n == 0 else None)
L(doc(1030, 4370, 90, 110, 3), 1.7, 1.9)
L(scribble(950, 4330, 600, 160, 9), 2, 2.6, RED, 6, sfx="shaker")

b.shot("下一拨人来收拾", "例子 · 会议室", view=(950, 4350, 0.85))
L(stick(520, 4720, 0.75, "shrug"), 0, 0.6, BLUE, sfx="wood_high")
L(face(520, 4720, 0.75, "sad"), 0.6, 0.7, BLUE)
T("先收10分钟", 1100, 4620, 64, RED, k0=2, sfx="rim")

b.shot("工作群天天刷屏", "例子 · 工作群", view=(2650, 4300, 0.85))
T("工作群", 2650, 3970, 70, k0=0, sfx="pop")
L(phone(2500, 4360), 0.6, 1.0)
for n in range(5):
    side = -1 if n % 2 == 0 else 1
    L(rect(2500 + side * 40, 4160 + n * 72, 170, 44, 18), 1 + n * 0.15, 1.15 + n * 0.15, BLACK, 6,
      sfx="shaker" if n == 0 else None)
T("99+", 2770, 4120, 70, RED, k0=2, sfx="pop")

b.shot("要紧通知沉底了", "例子 · 工作群", view=(2650, 4350, 0.85))
T("通知", 2500, 4530, 50, RED, k0=0, sfx="pop")
L(arrow((2700, 4250), (2700, 4560), 0.0, 36), 0.5, 0.9, RED, 8)
L(stick(3050, 4720, 0.75), 1, 1.5, BLUE, sfx="wood_high")
L(face(3050, 4720, 0.75, "sad"), 1.5, 1.6, BLUE)
T("没看到", 3050, 4400, 56, BLUE, k0=2, sfx="pop")

b.shot("楼道堆满杂物", "例子 · 楼道", view=(950, 5300, 0.85))
T("楼道", 950, 4970, 70, k0=0, sfx="pop")
L(join(P((420, 5080), (420, 5650)), P((420, 5650), (1480, 5650))), 0.5, 0.9)
for n, (x, y, w, h) in enumerate(((560, 5580, 200, 140), (580, 5440, 160, 140), (780, 5590, 170, 120))):
    L(rect(x, y, w, h, 8), 1 + n * 0.2, 1.2 + n * 0.2, sfx="wood_high" if n == 0 else None)
L(bike(1150, 5650, 0.85), 2, 2.6, sfx="wood_high")

b.shot("消防通道被堵死", "例子 · 楼道", view=(950, 5300, 0.85))
L(rect(1150, 5180, 280, 90, 10), 0, 0.4, GREEN, 7, sfx="pop")
T("安全出口", 1150, 5196, 46, GREEN, k0=0.4)
L(cross(780, 5520, 180), 2, 2.4, RED, 12, sfx="rim")

b.shot("水槽里堆满碗", "例子 · 家里", view=(2650, 5300, 0.85))
T("家里水槽", 2650, 4970, 70, k0=0, sfx="pop")
L(sink(2650, 5300), 0.6, 1.1)
for n in range(5):
    L(oval(2600 + (n % 2) * 30, 5270 - n * 34, 220, 44), 1 + n * 0.2, 1.2 + n * 0.2, BLACK, 7,
      sfx="wood_high" if n == 0 else None)
L(stink(2600, 5080), 2, 2.5, GREEN, 6, sfx="shaker")

FAM = (2200, 2650, 3100)
b.shot("都等别人先洗", "例子 · 家里", view=(2650, 5400, 0.85))
for n, x in enumerate(FAM):
    L(stick(x, 5730, 0.55 if n < 2 else 0.42, "point"), n * 0.3, n * 0.3 + 0.4, sfx="wood_high" if n == 0 else None)
for n in range(3):
    x0, x1 = FAM[n], FAM[(n + 1) % 3]
    L(arrow((x0 + (70 if x1 > x0 else -70), 5480), (x1 + (-70 if x1 > x0 else 70), 5480), 0.18 if x1 > x0 else -0.12,
            30), 2 + n * 0.3, 2.3 + n * 0.3, RED, 7, sfx="rim" if n == 0 else None)

b.shot("人都没那么坏", "身边的例子", view=(1800, 4800, 0.42))
T("人都没那么坏", 1800, 5880, 110, k0=0, sfx="pop")
b.hit(J(), 2, "wood_low")

b.shot("账落不到个人头上", "身边的例子", view=(1800, 4800, 0.42), shake=[0])
T("没人买单", 1800, 4810, 140, RED, k0=0, k1=0.6, sfx="kick")
for n, (x, y) in enumerate(CARDS):
    L(arrow((1800 + (x - 1800) * 0.2, 4800 + (y - 4800) * 0.25), (1800 + (x - 1800) * 0.55, 4800 + (y - 4800) * 0.55),
            0.1, 40), 1 + n * 0.5, 1.4 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 6750), (2650, 6750), (950, 7650), (2650, 7650)]
b.shot("书里给了三条路", "具体做法", view=(1800, 7100, 0.42))
T("书中三条路", 1800, 6230, 110, k0=0, k1=1.2, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1500, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("第一条：讲道理", "第一条 · 讲道理", view=(950, 6750, 0.85))
T("① 讲道理", 950, 6450, 80, BLUE, k0=0, sfx="pop")
L(stick(520, 7060, 0.8, "point"), 2, 2.6, sfx="wood_high")
L(face(520, 7060, 0.8, "smile"), 2.6, 2.7)

b.shot("冰箱门上贴张条", "第一条 · 讲道理", view=(950, 6750, 0.85))
L(rect(1080, 6780, 620, 250, 16), 0, 0.6, ORANGE, 8, sfx="wood_high")
T("过期饭菜会招虫", 1080, 6750, 54, k0=1, sfx="pop")
T("请带回家", 1080, 6850, 54, RED, k0=2, sfx="pop")

b.shot("光靠自觉管不久", "第一条 · 讲道理", view=(950, 6800, 0.85))
T("坚持3天", 820, 7060, 60, k0=0, sfx="pop")
L(arrow((990, 7045), (1140, 7045), 0.0, 30), 1, 1.3, BLACK, 7, sfx="wood_high")
T("又乱了", 1290, 7060, 60, RED, k0=2, sfx="rim")

b.shot("第二条：分到个人", "第二条 · 分到个人", view=(2650, 6750, 0.85))
T("② 分到个人", 2650, 6450, 80, BLUE, k0=0, sfx="pop")
L(join(rect(2650, 6830, 800, 420, 16), P((2250, 6760), (3050, 6760)), P((2250, 6900), (3050, 6900))), 2,
  2.7, sfx="wood_high")
ROWS = (6760, 6900, 7040)                         # 三格的底线

b.shot("一人一格写名字", "第二条 · 分到个人", view=(2650, 6800, 0.85))
for n, w in enumerate(("小王", "小李", "阿美")):
    T(w, 2420, ROWS[n] - 50, 56, k0=n * 1.0, k1=n * 1.0 + 0.4, sfx="pop")

b.shot("自己那格自己管", "第二条 · 分到个人", view=(2650, 6800, 0.85))
for n in range(3):
    L(box(2700, ROWS[n] - 6, 110, 70), n * 0.3, n * 0.3 + 0.3, sfx="wood_high" if n == 0 else None)
for n in range(3):
    L(check(2930, ROWS[n] - 45, 36), 2 + n * 0.3, 2.2 + n * 0.3, GREEN, 9, sfx="ding" if n == 0 else None)

TB = (700, 7720)
b.shot("第三条：定规矩", "第三条 · 定规矩", view=(950, 7650, 0.85))
T("③ 一起定规矩", 950, 7340, 76, BLUE, k0=0, k1=1.2, sfx="pop")
for n, x in enumerate((520, 700, 880)):
    L(stick(x, 7720, 0.5), 2 + n * 0.25, 2.3 + n * 0.25, sfx="wood_high" if n == 0 else None)
L(oval(*TB, 520, 90), 3, 3.4)

b.shot("坐下来一起商量", "第三条 · 定规矩", view=(950, 7650, 0.85))
for n, x in enumerate((520, 700, 880)):
    L(bubble(x, 7460, 120, 64, -1 if n < 2 else 1), n, n + 0.3, BLACK, 6, sfx="pop")

b.shot("没写名字周五清", "第三条 · 定规矩", view=(950, 7700, 0.85))
T("没写名字，周五清空", 950, 7870, 58, RED, k0=0, k1=1.4, sfx="pop")
L(underline(690, 1210, 7915), 2, 2.5, RED, 7, sfx="ding")

b.shot("轮流值日看一眼", "第三条 · 定规矩", view=(950, 7650, 0.85))
T("值日表", 1330, 7440, 56, k0=0, sfx="pop")
for n, w in enumerate(("周一 小王", "周二 小李", "周三 阿美")):
    T(w, 1330, 7530 + n * 75, 48, k0=1 + n * 0.5, k1=1.4 + n * 0.5, sfx="pop" if n in (0, 2) else None)

b.shot("冰箱清爽多了", "回到冰箱", view=(2650, 7650, 0.85))
L(fridge(2400, 7680, 0.8, open_door=True), 0, 0.8, sfx="wood_low")
for n, w in enumerate(("小王", "小李", "阿美")):
    T(w, 2400, shelf_y(7680, n, 0.8) - 26, 46, k0=1 + n * 0.25, k1=1.2 + n * 0.25, sfx="pop" if n == 0 else None)
T("清爽！", 2930, 7560, 90, GREEN, k0=2, sfx="ding")
L(check(2930, 7700, 60), 2.8, 3.1, GREEN, 10)

b.shot("公共的也得有人管", "一句话", view=(1800, 4600, 0.235))
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 8350, 0.8))
T("你们公司的公地在哪？", 1800, 8250, 76, RED, k0=0.5, k1=1.8)
T("下一讲：标准为什么越来越低？", 1800, 8420, 48, k0=2.0, k1=3.2)
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 1, "pop")
b.hit(J(), 2, "wood_high", 0.7)
b.hit(J(), 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "commons", "公地悲剧", "公司冰箱为什么总是乱糟糟？", ACC, b.shots,
                 [f"{BOOK}（Thinking in Systems: A Primer, 2008；转述）", "中译本：邱昭良译，浙江人民出版社 2012",
                  "Garrett Hardin, The Tragedy of the Commons, Science, 1968"],
                 "好处归自己|代价【大家摊】", 10,
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
