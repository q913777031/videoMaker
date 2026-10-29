"""05 延迟（白板手绘版）：为什么越着急，越容易出乱子？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
叙事：打工人切身问题开局（项目告急，领导喊加人，一个月后人到了活儿早干完，又要裁人）→ 书中观点（先亮书；
调水温忽冷忽热作生活类比；书中汽车经销商库存的例子：看销量、下订单、等到货都要时间，货到时车已堆满又砍单，
库存来回振荡；反应越快振荡越凶，慢慢调、看平均趋势反而稳，画成一张库存曲线图）→ 身边的例子（数据一跌就改方案、
健身几天没瘦就饿肚子、孩子一次没考好就报班、开车前车一刹后车越踩越狠）→ 具体做法（先问要等多久 / 看一周平均 /
每次只拧一点 / 留点余量）→ 评论区互动。
书中观点为转述（Meadows, Thinking in Systems, 2008；中译本《系统之美》，邱昭良译，浙江人民出版社 2012）；
调水温为生活类比，例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, building, check, circle, clock, cross,
                               doc, face, hands_at, join, marker, node, rect, scribble, stick, underline)
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#3E6A8A"
SQUARE_SHOT = 8

b = Board(size=(3600, 12100))


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

def calendar(x, y, w=240, h=200, rows=0, cols=0) -> skia.Path:
    parts = [rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 50), (x + w / 2, y - h / 2 + 50)),
             P((x - w / 4, y - h / 2 - 20), (x - w / 4, y - h / 2 + 20)),
             P((x + w / 4, y - h / 2 - 20), (x + w / 4, y - h / 2 + 20))]
    for r in range(1, rows):
        yy = y - h / 2 + 50 + (h - 50) * r / rows
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
    for c_ in range(1, cols):
        xx = x - w / 2 + w * c_ / cols
        parts.append(P((xx, y - h / 2 + 50), (xx, y + h / 2)))
    return join(*parts)


def phone(x, y, w=120, h=200) -> skia.Path:
    return join(rect(x, y, w, h, 18), P((x - 20, y + h / 2 - 25), (x + 20, y + h / 2 - 25)))


def car(x, y, s=1.0) -> skia.Path:
    """小汽车（侧视，车头朝右）：(x, y) 为地面中点，宽约 220·s。"""
    body = P((x - 110 * s, y - 35 * s), (x + 110 * s, y - 35 * s), (x + 110 * s, y - 85 * s), (x + 60 * s, y - 90 * s),
             (x + 30 * s, y - 135 * s), (x - 60 * s, y - 135 * s), (x - 90 * s, y - 88 * s), (x - 110 * s, y - 85 * s),
             close=True)
    return join(body, circle(x - 60 * s, y - 25 * s, 25 * s), circle(x + 60 * s, y - 25 * s, 25 * s))


def bowl(x, y, r=90) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 0, 180)
    return join(P((x - r - 15, y), (x + r + 15, y)), p)


def scale_box(x, y) -> skia.Path:
    """体重秤：(x, y) 为秤面中点。"""
    return join(rect(x, y, 320, 120, 24), circle(x, y - 5, 32), P((x, y - 5), (x + 18, y - 28)))


def dashed(x0, x1, y, dash=40, gap=26) -> skia.Path:
    parts, x = [], x0
    while x < x1:
        parts.append(P((x, y), (min(x1, x + dash), y)))
        x += dash + gap
    return join(*parts)


def axes(x0, y0, x1, y1) -> skia.Path:
    """坐标轴：原点 (x0, y0)，纵轴到 y1，横轴到 x1，带箭头。"""
    return join(P((x0, y1), (x0, y0), (x1, y0)), P((x0 - 18, y1 + 30), (x0, y1), (x0 + 18, y1 + 30)),
                P((x1 - 30, y0 - 18), (x1, y0), (x1 - 30, y0 + 18)))


def curve(fn, x0, x1, n=90) -> skia.Path:
    """按 y = fn(u)（u 从 0 到 1）采样一条曲线。"""
    return P(*[(x0 + (x1 - x0) * i / n, fn(i / n)) for i in range(n + 1)])


def knob_fn(x, y, r, keys):
    """水龙头旋钮的指针：keys = [(镜头, 拍, 角度)]，角度 0 朝上、负值偏冷（左）；到点后 0.3 秒转过去。"""

    def fn(c, k, t):
        ang = keys[0][2]
        for jj, kb, a in keys[1:]:
            t0 = b.t_of(jj, kb)
            if t >= t0:
                ang = ang + (a - ang) * ease_out(clamp01((t - t0) / 0.3))
        rad = math.radians(ang)
        c.drawPath(P((x, y), (x + math.sin(rad) * r * 0.85, y - math.cos(rad) * r * 0.85)), marker(RED, 12))
        return None

    return fn


# ---------------------------------------------------------------- 开局：项目告急（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("项目告急，领导喊加人", "灵魂拷问", (950, 900, 0.85), shake=[5])
L(calendar(600, 650), 0, 0.6, sfx="wood_high")
T("周一", 600, 690, 60, k0=0.6, k1=0.9)
L(stick(600, 1300, 0.8, "shrug"), 1, 1.6, sfx="wood_high")
L(face(600, 1300, 0.8, "sad"), 1.6, 1.75)
L(phone(900, 700), 2, 2.4, sfx="pop")
T("急！", 900, 530, 80, RED, k0=3, k1=3.4, sfx="rim")
L(stick(1250, 1300, 0.85, "point", tie=True), 4, 4.5, sfx="wood_high")
L(face(1250, 1300, 0.85, "flat"), 4.5, 4.6)
L(join(rect(1180, 870, 380, 150, 40), P((1270, 945), (1320, 1010), (1220, 945))), 4.6, 4.95)
T("赶紧加人！", 1180, 885, 56, RED, k0=5, k1=5.7, sfx="kick")

scene("人到了，活儿早干完", "灵魂拷问", (2650, 900, 0.85))
for n in range(4):
    L(calendar(2230 + n * 30, 640 + n * 22, 200, 170), n * 0.22, n * 0.22 + 0.22, sfx="shaker" if n == 0 else None)
T("一个月后", 2290, 470, 56, k0=1, k1=1.6, sfx="pop")
for n, x in enumerate((2500, 2700, 2900)):
    L(stick(x, 1300, 0.65), 2 + n * 0.3, 2.3 + n * 0.3, BLUE, sfx="wood_high" if n == 0 else None)
T("新人到岗", 2700, 940, 54, BLUE, k0=3, k1=3.6, sfx="pop")
L(doc(3100, 650, 200, 260), 4, 4.4, sfx="wood_high")
for n in range(4):
    L(check(3170, 570 + n * 63, 24), 4.4 + n * 0.12, 4.52 + n * 0.12, GREEN, 8)
T("早干完了", 3080, 440, 56, RED, k0=5, k1=5.7, sfx="rim")

scene("刚招来，又要裁", "灵魂拷问", (2650, 900, 0.85), shake=[1, 4], flashes=[4])
T("人闲着", 2290, 950, 56, k0=0, k1=0.6, sfx="pop")
L(cross(2700, 1170, 150), 1, 1.4, RED, 14, sfx="kick")
T("又要裁", 2290, 1090, 60, RED, k0=2, k1=2.6, sfx="rim")
T("？", 3200, 1150, 200, RED, k0=4, k1=4.4, sfx="kick")
T("越急越乱", 2650, 1415, 90, k0=5, k1=5.8, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

DX, DY = 2650, 2850
CARS = [(DX - 190, DY + 340), (DX + 30, DY + 340)]
MORE = [(DX + 250, DY + 340), (DX - 190, DY + 200), (DX + 30, DY + 200), (DX + 250, DY + 200), (DX - 190, DY + 60),
        (DX + 30, DY + 60)]
scene("书里有个车行", "系统之美 · 书中例子", (1950, 2950, 0.62))
L(book(1350, 2900, 380, 260), 0, 0.9, sfx="wood_low")
T("系统之美", 1350, 2680, 84, GREEN, k0=1, k1=1.6, sfx="pop")
T("德内拉 · 梅多斯", 1350, 3120, 52, k0=1.8, k1=2.4)
T("这一讲：延迟", 1350, 3240, 64, RED, k0=2.4, k1=2.95)
L(building(DX - 450, DY + 340, 240, 300), 3, 3.5, sfx="wood_high")
T("车行", DX - 450, DY - 20, 64, k0=3.5, k1=3.85)
for n, (x, y) in enumerate(CARS):
    L(car(x, y, 0.75), 4 + n * 0.4, 4.35 + n * 0.4, sfx="pop" if n == 0 else None)
T("库存", DX + 30, DY + 440, 60, GREEN, k0=5, k1=5.5, sfx="pop")

scene("猛订一批，慢慢才到", "书中例子 · 汽车经销商", (DX, 2950, 0.85), shake=[0], flashes=[0])
b.hit(J(), 0, "kick", 1.0, "猛订")
for n, (x, y) in enumerate(CARS):
    L(arrow((x + 40, y - 150), (x + 40, y - 300), 0.1, 30), n * 0.3, n * 0.3 + 0.3, GREEN, 8)
T("卖得快", DX - 80, DY - 20, 50, GREEN, k0=0.6, k1=0.9)
L(doc(DX + 500, DY + 150, 140, 180), 1, 1.35, sfx="pop")
L(doc(DX + 530, DY + 180, 140, 180), 1.35, 1.7)
T("猛订", DX + 510, DY + 10, 60, RED, k0=2, k1=2.5, sfx="rim")
for n, w in enumerate(("看销量", "下订单", "等到货")):
    x = DX - 350 + n * 350
    L(clock(x, DY - 290, 60), 3 + n, 3.5 + n, sfx="wood_high" if n != 1 else "pop")
    L(hands_at(x, DY - 290, 60, 3 + n * 3, 0), 3.5 + n, 3.6 + n, RED, 7)
    T(w, x, DY - 175, 46, k0=3.6 + n, k1=3.9 + n)

scene("车堆满，又砍单", "书中例子 · 汽车经销商", (DX, 2950, 0.85), shake=[3])
b.erase(J(), 0, 0.6, DX - 80, 2930, 420, 270)
b.hit(J(), 0, "shaker", 0.7, "擦掉")
for n, (x, y) in enumerate(MORE):
    L(car(x, y, 0.75), 1 + n * 0.22, 1.3 + n * 0.22, RED, 8, sfx="pop" if n == 0 else None)
L(cross(DX + 515, DY + 165, 90), 3, 3.3, RED, 14, sfx="kick")
T("砍单", DX + 515, DY + 330, 60, RED, k0=4, k1=4.4, sfx="rim")

CX2, CY2 = 2650, 4270
U0, U1, MID = CX2 - 550, CX2 + 500, CY2 - 75
scene("订得越急，晃得越凶", "书中观点 · 来回振荡", (CX2, CY2, 0.85), shake=[2])
L(axes(CX2 - 570, CY2 + 300, CX2 + 590, CY2 - 450), 0, 0.5, BLACK, 8, sfx="wood_high")
T("库存", CX2 - 470, CY2 - 490, 50, k0=0.5, k1=0.8)
T("时间", CX2 + 520, CY2 + 360, 46, k0=0.8, k1=1.0)
L(dashed(U0, U1 + 60, MID), 1, 1.2, GREEN, 6, sfx="pop")
T("刚好", CX2 + 555, MID + 45, 46, GREEN, k0=1.2, k1=1.45)
L(curve(lambda u: MID - 320 * math.sin(2 * math.pi * 3.5 * u), U0, U1, 140), 2, 3.6, RED, 11, sfx="kick")
T("反应快：大起大落", CX2, CY2 + 400, 52, RED, k0=4, k1=4.9, sfx="rim")

scene("慢慢调，反而稳", "书中观点 · 看平均趋势", (CX2, CY2, 0.85))
L(curve(lambda u: MID - 150 * math.exp(-4 * u) * math.sin(2 * math.pi * 1.2 * u), U0, U1), 0, 1.4, GREEN, 14,
  sfx="wood_high")
T("慢慢调：稳住了", CX2, CY2 + 500, 52, GREEN, k0=2, k1=2.9, sfx="ding")
L(underline(CX2 - 190, CX2 + 190, CY2 + 550), 3, 3.5, GREEN, 7, sfx="pop")

SX, SY = 980, 4270
KX, KY = SX - 320, SY + 170
PIPE = P((KX, KY - 45), (KX, SY - 320), (SX - 490, SY - 320))


def _hot(u):
    return SY + 250 - 480 * math.sin(u * math.pi / 2)


def _cold(u):
    if u < 0.65:
        return SY - 230 + 560 * (1 - math.cos(u / 0.65 * math.pi)) / 2
    return SY + 330


scene("调水温也是这样", "生活类比 · 调水温", (SX, SY, 0.85))
L(stick(SX - 530, SY + 400, 0.8, "point"), 0, 0.5, sfx="wood_high")
L(join(PIPE, P((SX - 600, SY - 320), (SX - 460, SY - 320), (SX - 490, SY - 260), (SX - 570, SY - 260), close=True)),
  0.5, 0.85)
L(join(*[P((SX - 565 + i * 35, SY - 235), (SX - 575 + i * 35, SY - 185)) for i in range(4)]), 0.85, 0.95, BLUE, 6)
L(circle(KX, KY, 45), 1, 1.2, sfx="pop")
b.custom(J(), 1.2, 20, knob_fn(KX, KY, 45, [(J(), 0, -60), (J(), 2, 90), (J(), 3.4, -90)]))
L(axes(SX - 130, SY + 380, SX + 560, SY - 300), 1.3, 1.7, BLACK, 8)
T("水温", SX - 40, SY - 330, 50, k0=1.7, k1=1.95)
L(curve(_hot, SX - 110, SX + 250), 2, 2.9, RED, 10, sfx="tom")
T("烫！", SX + 380, SY - 200, 100, RED, k0=3, k1=3.35, sfx="tom")
L(curve(_cold, SX + 250, SX + 530), 3.4, 3.95, BLUE, 10)
T("冰！", SX + 420, SY + 470, 90, BLUE, k0=4, k1=4.35, sfx="rim")
L(PIPE, 5, 5.4, RED, 14, sfx="wood_high")
T("要走一会儿", SX - 390, SY - 390, 50, RED, k0=5.4, k1=5.95)

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 5900), (2650, 5900), (950, 7100), (2650, 7100)]
OV = (1800, 6650, 0.36)
scene("身边全是这种事", "身边的例子", OV)
for n, ((x, y), w) in enumerate(zip(CARDS, ("改方案", "减肥", "孩子成绩", "开车"))):
    L(rect(x, y, 1500, 900, 40), n, n + 0.6, GREEN, 8, sfx="wood_high" if n % 2 == 0 else "pop")
    T(w, x - 400, y - 360, 84, BLUE, k0=n + 0.6, k1=n + 1.0)

x, y = CARDS[0]
scene("数据一跌，就改方案", "例子 · 改方案", (x, y, 0.85))
L(axes(x - 520, y + 150, x - 60, y - 300), 0, 0.4, BLACK, 7, sfx="wood_high")
L(P((x - 500, y - 200), (x - 400, y - 160), (x - 300, y - 190), (x - 200, y - 60), (x - 110, y + 60)), 0.4, 0.9, BLACK, 8)
L(arrow((x - 170, y - 250), (x - 110, y - 20), -0.1, 34), 1, 1.3, RED, 9, sfx="rim")
for n, w in enumerate(("一版", "二版", "三版")):
    L(doc(x + 170 + n * 170, y - 60, 150, 200, 0), 2 + n * 0.7, 2.3 + n * 0.7, sfx="pop" if n in (0, 2) else None)
    T(w, x + 170 + n * 170, y - 50, 50, k0=2.3 + n * 0.7, k1=2.6 + n * 0.7)
L(cross(x + 340, y - 60, 240), 5, 5.3, RED, 12, sfx="rim")
T("越改越乱", x - 250, y + 320, 64, RED, k0=5.3, k1=5.95)

x, y = CARDS[1]
scene("没瘦就饿，饿完暴吃", "例子 · 健身", (x, y, 0.85))
L(stick(x - 380, y + 330, 0.8, "up"), 0, 0.6, sfx="wood_high")
for n in range(3):
    L(P((x - 480, y + 120 + n * 60), (x - 580, y + 120 + n * 60)), 0.6 + n * 0.1, 0.7 + n * 0.1, BLUE, 6)
L(scale_box(x + 250, y + 230), 1, 1.5, sfx="pop")
T("还是 60kg", x + 250, y + 90, 64, RED, k0=2, k1=2.6, sfx="rim")
L(bowl(x - 200, y - 200, 90), 3, 3.3, sfx="wood_high")
L(cross(x - 200, y - 230, 80), 3.3, 3.6, RED, 10)
T("饿", x - 340, y - 160, 60, k0=3.6, k1=3.8)
for n in range(3):
    L(bowl(x + 330, y - 120 - n * 60, 90 - n * 12), 4 + n * 0.25, 4.25 + n * 0.25, RED, 9,
      sfx="pop" if n == 0 else None)
T("又胖回来", x + 330, y - 300, 54, RED, k0=5, k1=5.6, sfx="rim")

x, y = CARDS[2]
scene("没考好，马上报班", "例子 · 家里", (x, y + 80, 0.85))
L(stick(x - 420, y + 330, 0.6, "down"), 0, 0.5, sfx="wood_high")
L(face(x - 420, y + 330, 0.6, "sad"), 0.5, 0.6)
L(doc(x - 50, y - 30, 260, 320, 0), 1, 1.4, sfx="pop")
T("72", x - 50, y - 10, 120, RED, k0=2, k1=2.4, sfx="rim")
for n, w in enumerate(("数学班", "英语班", "作文班")):
    L(rect(x + 400, y - 260 + n * 150, 240, 110, 16), 3 + n * 0.6, 3.3 + n * 0.6, sfx="pop" if n == 0 else None)
    T(w, x + 400, y - 250 + n * 150, 50, k0=3.3 + n * 0.6, k1=3.55 + n * 0.6)
T("累", x - 420, y + 40, 70, RED, k0=5, k1=5.3, sfx="rim")
L(arrow((x + 280, y + 210), (x - 320, y + 210), 0, 34), 5.3, 5.8, RED, 8)

x, y = CARDS[3]
TRAFFIC = [x - 480, x - 200, x + 80, x + 360]
scene("前车一刹，后车更猛", "例子 · 开车", (x, y + 80, 0.85), shake=[5])
L(P((x - 620, y + 260), (x + 620, y + 260)), 0, 0.3, BLACK, 7, sfx="wood_high")
for n, cx in enumerate(TRAFFIC):
    L(car(cx, y + 250, 0.8), 0.3 + n * 0.15, 0.6 + n * 0.15)
L(circle(x + 360 - 82, y + 250 - 62, 14), 2, 2.2, RED, 10, sfx="rim")
T("刹", x + 360, y + 60, 70, RED, k0=2.2, k1=2.5)
for n, (cx, sz, k) in enumerate(((x + 80, 70, 3), (x - 200, 100, 3.5), (x - 480, 140, 4))):
    T("！", cx, y + 90 - sz * 0.3, sz, RED, k0=k, k1=k + 0.3, sfx=("pop", None, "rim")[n])
T("堵死了", x, y - 180, 70, RED, k0=5, k1=5.55, sfx="kick")

scene("没等结果，又动手", "身边的例子", OV, shake=[4])
for n, (cx, cy) in enumerate(CARDS):
    L(clock(cx + 600, cy - 360, 70), n, n + 0.4, BLUE, 8, sfx=("wood_high", "pop")[n % 2])
    L(hands_at(cx + 600, cy - 360, 70, 4, 50), n + 0.4, n + 0.5, BLUE, 6)
T("没等结果，又动手", 1800, 7720, 110, RED, k0=4, k1=5.3, sfx="kick")
L(underline(1350, 2250, 7800), 5.4, 5.9, RED, 9)

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 8780), (2650, 8780), (950, 10100), (2650, 10100)]

x, y = SOL[0]
scene("先问：要等多久", "第一步 · 算延迟", (x, y, 0.85))
L(rect(x, y, 1500, 820, 40), 0, 0.6, GREEN, 8)
T("① 要等多久？", x, y - 290, 80, BLUE, k0=1, k1=1.9, sfx="pop")
L(clock(x - 400, y + 120, 130), 2, 2.5, sfx="wood_high")
L(hands_at(x - 400, y + 120, 130, 2, 0), 2.5, 2.7, RED, 10)
L(calendar(x + 180, y + 140, 420, 260, 3, 5), 3, 3.5, sfx="wood_high")
T("新方案 → 看两周", x + 180, y - 140, 60, k0=3.6, k1=4.6)
L(circle(x + 180 + 126, y + 140 + 82, 48), 5, 5.3, RED, 9, sfx="rim")
T("到这天再评", x - 400, y + 320, 54, RED, k0=5.3, k1=5.95)

x, y = SOL[1]
DAILY = [0, 90, -60, 120, -100, 40, 150, -30, 70, -120, 60, 130, -40, 100, 20]
scene("看平均，别看一天", "第二步 · 看平均", (x, y, 0.85))
L(rect(x, y, 1500, 820, 40), 0, 0.6, GREEN, 8)
T("② 看一周平均", x, y - 290, 80, BLUE, k0=1, k1=1.9, sfx="pop")
L(P(*[(x - 520 + i * 74, y + 120 - d - i * 8) for i, d in enumerate(DAILY)]), 2, 3.4, BLACK, 7, sfx="shaker")
L(P((x - 520, y + 125), (x + 516, y + 5)), 4, 4.7, RED, 12, sfx="wood_high")
T("平均", x + 430, y - 90, 60, RED, k0=5, k1=5.4, sfx="ding")

x, y = SOL[2]
scene("每次只拧一点", "第三步 · 动作放小", (x, y, 0.85))
L(rect(x, y, 1500, 820, 40), 0, 0.6, GREEN, 8)
T("③ 每次拧一点", x, y - 290, 80, BLUE, k0=1, k1=1.9, sfx="pop")
L(circle(x - 380, y + 100, 110), 2, 2.4, sfx="wood_high")
b.custom(J(), 2.4, 20, knob_fn(x - 380, y + 100, 110, [(J(), 0, 0), (J(), 3, 25)]))
b.hit(J(), 3, "pop")
L(arrow((x - 300, y - 40), (x - 230, y + 10), -0.2, 26), 3, 3.3, RED, 7)
T("加人：先加一个", x + 220, y - 110, 58, k0=4, k1=4.9, sfx="pop")
L(stick(x + 220, y + 340, 0.55), 5, 5.4, BLUE, sfx="wood_high")
L(face(x + 220, y + 340, 0.55, "smile"), 5.4, 5.5, BLUE)

x, y = SOL[3]
scene("给自己留点余量", "第四步 · 留余量", (x, y, 0.85))
L(rect(x, y, 1500, 820, 40), 0, 0.6, GREEN, 8)
T("④ 留点余量", x, y - 290, 80, BLUE, k0=1, k1=1.8, sfx="pop")
for n in range(3):
    L(rect(x - 400, y + 280 - n * 110, 220, 100, 10), 2 + n * 0.3, 2.3 + n * 0.3, BLACK, 8,
      sfx="wood_high" if n == 0 else None)
T("备用", x - 400, y - 80, 56, GREEN, k0=3, k1=3.4, sfx="pop")
T("工期 +1 周", x + 200, y - 100, 64, k0=4, k1=4.7, sfx="pop")
L(check(x + 440, y - 110, 40), 4.75, 4.95, GREEN, 9)
T("急单来了也不慌", x + 200, y + 130, 60, GREEN, k0=5, k1=5.9, sfx="ding")

scene("急的时候，先等等", "一句话", (1800, 6200, 0.235))
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 2, "wood_high", 0.6)
b.hit(J(), 4, "ding")

scene("评论区聊聊", "评论区见", (1800, 11460, 0.8))
b.hit(J(), 0, "cymbal", 0.5)
T("你被哪次着急坑过？", 1800, 11380, 80, RED, k0=1, k1=2.6)
b.hit(J(), 1, "pop")
T("下一讲：业绩为什么涨着涨着就不动了？", 1800, 11540, 50, k0=3, k1=4.5)
b.hit(J(), 3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "delay", "延迟", "为什么越着急，越容易出乱子？", ACC, b.shots,
                 [f"{BOOK}（转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                 "越着急|越容易【出乱子】", 8,
                 ["书中观点均为转述：反馈回路里有延迟时，系统容易来回振荡；书中以汽车经销商的库存为例——感知销量变化、"
                  "做出订货决定、工厂交货都需要时间，订单到货时库存已经过量，于是又砍订单，库存上下摆动；在这个模型里，"
                  "经销商反应得越快振荡越厉害，放慢反应、看平均趋势反而更稳。出处：Donella H. Meadows, Thinking in Systems: "
                  "A Primer (2008)，中译本《系统之美》（邱昭良译，浙江人民出版社 2012）；原书中文未逐字核对。",
                  "调水温忽冷忽热为生活类比，不是书中例子；车行车辆数与各条曲线形状均为示意。",
                  "改方案、健身、孩子报班、开车跟车均为现实场景示意，不指向任何具体公司或个人；四步做法（先问要等多久、"
                  "看一周平均、每次只拧一点、留余量）为据书中思路整理的建议。"],
                 tags="#延迟 #职场")
    return b.attach(ep)
