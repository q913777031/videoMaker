"""04 增强回路（白板手绘版）：为什么有人越学越快？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
叙事：打工人切身问题开局（同一年入职，三年后她当上组长、你还在原地，脑子差不多，差距哪来的）→
书中观点（亮书；书中例子银行存款：钱越多利息越多、利息再生利息；这就是增强回路；先慢后快的曲线，很多人在平的那段放弃；
它也能往坏处转：越累越想刷手机；好坏都会越滚越大）→ 身边的例子（职场：会做表的人活越多越熟练；生活：跑步越跑越想跑；
家庭：拌嘴越吵越凶；钱：信用卡只还最低，欠款利滚利；小差别越滚越大）→
具体做法（挑一件能滚的事 / 每天做一点 / 收益投回去 / 掐断坏回路）→ 评论区互动。
书中观点为转述（Meadows, Thinking in Systems, 2008；中译本《系统之美》，邱昭良译，浙江人民出版社 2012）；
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               desk, doc, face, hands_at, join, marker, rect, scribble, stick, underline)
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#C0702A"
SQUARE_SHOT = 7

b = Board(size=(3600, 11800))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲小图元

def exp_curve(x0, y0, x1, y1, rate=4.0, u0=0.0, u1=1.0, n=48):
    """指数曲线（先平后陡）：从 (x0, y0) 到 (x1, y1)，取参数段 [u0, u1]。"""
    pts = []
    for i in range(n + 1):
        u = u0 + (u1 - u0) * i / n
        f = (math.exp(rate * u) - 1) / (math.exp(rate) - 1)
        pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * f))
    return P(*pts)


def axes(ox, oy, w, h):
    return join(P((ox, oy - h), (ox, oy), (ox + w, oy)), P((ox - 18, oy - h + 30), (ox, oy - h), (ox + 18, oy - h + 30)),
                P((ox + w - 30, oy - 18), (ox + w, oy), (ox + w - 30, oy + 18)))


def loop_icon(x, y, r, head=None):
    """转圈箭头：顺时针约 300°，尾端带箭头。"""
    head = head or r * 0.45
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -60, 300)
    a = math.radians(240)
    ex, ey = x + r * math.cos(a), y + r * math.sin(a)
    dx, dy = -math.sin(a), math.cos(a)
    for d in (0.5, -0.5):
        c_, s_ = math.cos(math.pi + d), math.sin(math.pi + d)
        p.moveTo(ex, ey)
        p.lineTo(ex + head * (dx * c_ - dy * s_), ey + head * (dx * s_ + dy * c_))
    return p


def loop_pair(xl, xr, y, r=110):
    """两个节点之间的双向回路箭头（上弧左到右，下弧右到左）。"""
    return join(arrow((xl + r * 0.8, y - r * 0.7), (xr - r * 0.8, y - r * 0.7), -0.3, 46),
                arrow((xr - r * 0.8, y + r * 0.7), (xl + r * 0.8, y + r * 0.7), -0.3, 46))


def bank(x, y, w=380):
    """银行：(x, y) 为台阶底边中点。"""
    parts = [P((x - w / 2 - 20, y - 320), (x, y - 430), (x + w / 2 + 20, y - 320), close=True),
             P((x - w / 2, y - 20), (x + w / 2, y - 20)), P((x - w / 2 - 20, y), (x + w / 2 + 20, y))]
    for i in range(4):
        cx = x - w / 2 + 50 + i * (w - 100) / 3
        parts.append(P((cx, y - 300), (cx, y - 30)))
    return join(*parts)


def coins(x, y, n, w=110, h=26):
    return join(*[rect(x, y - i * (h + 2), w, h, h / 2) for i in range(n)])


def runner(x, y, s=1.0):
    """跑步的小人：(x, y) 为后脚着地点附近。"""
    return join(circle(x + 25 * s, y - 290 * s, 45 * s), P((x + 20 * s, y - 245 * s), (x, y - 120 * s)),
                P((x - 90 * s, y), (x - 50 * s, y - 60 * s), (x, y - 120 * s), (x + 60 * s, y - 60 * s),
                  (x + 100 * s, y - 20 * s)),
                P((x - 60 * s, y - 175 * s), (x + 12 * s, y - 210 * s), (x + 70 * s, y - 150 * s)))


def credit_card(x, y, w=340, h=210):
    return join(rect(x, y, w, h, 24), P((x - w / 2, y - h / 2 + 50), (x + w / 2, y - h / 2 + 50)),
                rect(x - w / 2 + 70, y + 10, 70, 50, 8))


def door(x, y, w=160, h=260):
    return join(rect(x, y, w, h, 6), circle(x + w / 2 - 30, y + 10, 10))


def phone(x, y, w=70, h=120):
    return join(rect(x, y, w, h, 14), circle(x, y + h / 2 - 18, 7))


def grid_cells(x, y, cols=7, rows=3, s=100):
    out = []
    for r in range(rows):
        for c_ in range(cols):
            out.append((x + (c_ - (cols - 1) / 2) * s, y + r * s))
    return out


def fill_checks(cells, r=26):
    """格子里逐个打钩（每天一点）。"""

    def fn(c, k, t):
        n = len(cells) * k
        tip = None
        for i, (x, y) in enumerate(cells):
            if i >= n:
                break
            q = clamp01(n - i)
            from whiteboard.engine import partial
            part, p = partial(check(x, y, r), q)
            c.drawPath(part, marker(GREEN, 8))
            tip = p or tip
        return tip if k < 1 else None

    return fn


# ---------------------------------------------------------------- 开局：同一年入职（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("同一年进的公司", "灵魂拷问", (950, 1000, 0.8))
L(P((440, 1470), (1460, 1470)), 0, 0.6, BLACK, 6, sfx="wood_high")
L(rect(950, 760, 300, 120, 16), 1, 1.4, sfx="pop")
T("2021 入职", 950, 760, 58, k0=1.4, k1=2.0)
L(stick(650, 1460, 0.8), 2, 2.5, BLUE, sfx="pop")
T("你", 650, 1540, 56, BLUE, k0=2.5, k1=2.8)
L(stick(1250, 1460, 0.8, hair=True), 3, 3.5, RED, sfx="pop")
T("她", 1250, 1540, 56, RED, k0=3.5, k1=3.8)
T("起点一样", 950, 560, 70, k0=5, k1=5.7, sfx="ding")

scene("三年后差好多", "灵魂拷问", (2650, 1000, 0.8))
L(axes(2100, 1450, 1180, 950), 0, 0.7, BLACK, 8, sfx="wood_high")
T("2021", 2120, 1520, 48, k0=0.5, k1=0.8)
T("2024", 3180, 1520, 48, k0=0.7, k1=1.0)
L(P((2120, 1400), (3180, 1300)), 1, 1.6, BLUE, 10, sfx="pop")
T("你", 3240, 1250, 56, BLUE, k0=1.6, k1=1.8)
L(exp_curve(2120, 1400, 3180, 580, 3.5), 2, 2.9, RED, 11, sfx="shaker")
T("她", 3000, 600, 60, RED, k0=2.9, k1=3.1)
L(P((3110, 1280), (3110, 700)), 3.3, 3.6, RED, 6)
T("当上组长", 2600, 640, 64, RED, k0=4, k1=4.7, sfx="pop")
L(underline(2470, 2730, 700), 5, 5.5, RED, 7, sfx="rim")

scene("脑子差不多，差在哪", "灵魂拷问", (1800, 2900, 0.7), shake=[4], flashes=[4])
L(join(circle(1450, 2650, 110), face(1450, 2650 + 290 * 2.44, 2.44, "smile")), 0, 0.6, RED, 9, sfx="pop")
L(join(circle(2150, 2650, 110), face(2150, 2650 + 290 * 2.44, 2.44, "flat")), 1, 1.6, BLUE, 9, sfx="pop")
T("=", 1800, 2650, 150, k0=2, k1=2.3, sfx="ding")
T("脑子差不多", 1800, 2900, 66, k0=2.6, k1=3.5)
T("？", 1800, 3170, 260, RED, k0=4, k1=4.5, sfx="kick")
T("差距哪来的", 1800, 3420, 90, k0=5, k1=5.6, sfx="pop")
L(underline(1600, 2000, 3490), 5.6, 6.0, RED, 7)

# ---------------------------------------------------------------- 书中观点（场景 4–9）

R1, R2 = 4250, 5250         # 两排区块中心
BX = (950, 2650)            # 两列区块中心

scene("有本书讲过存钱", "系统之美 · 书中例子", (950, R1, 0.85))
L(book(650, R1, 400, 270), 0, 1.0, sfx="wood_low")
T("系统之美", 650, R1 - 240, 80, GREEN, k0=1, sfx="pop")
T("德内拉 · 梅多斯", 650, R1 + 230, 50, k0=2, k1=3)
L(bank(1260, R1 + 120, 340), 3, 3.9, sfx="wood_high")
T("¥", 1260, R1 - 160, 80, GREEN, k0=4, k1=4.3, sfx="pop")
T("存款 ¥10000", 1260, R1 + 220, 54, k0=5, k1=5.9, sfx="pop")

NL, NR = BX[1] - 380, BX[1] + 380
scene("钱越多，利息越多", "书中观点 · 越多越多", (BX[1], R1 + 40, 0.85), shake=[0], flashes=[0])
L(loop_pair(NL, NR, R1), 0, 0.4, RED, 14)
b.hit(J(), 0, "kick", 1.0, "drop：回路砸出")
L(circle(NL, R1, 110), 1, 1.3, BLACK, 9)
T("存款", NL, R1, 66, k0=1, sfx="pop")
L(circle(NR, R1, 110), 2, 2.3, BLACK, 9)
T("利息", NR, R1, 66, k0=2, sfx="pop")
T("+", BX[1], R1, 150, RED, k0=3, k1=3.3, sfx="ding")
for n, (x, m) in enumerate(((2250, 1), (2520, 2), (2790, 4), (3060, 7))):
    L(coins(x, R1 + 380, m), 4 + n * 0.5, 4.4 + n * 0.5, GREEN, 7, sfx="pop" if n % 2 == 0 else None)

scene("这叫增强回路", "书中观点 · 增强回路", (BX[1], R1, 0.85))
T("增强回路", BX[1], R1 - 360, 90, RED, k0=0, sfx="pop")
L(underline(BX[1] - 200, BX[1] + 200, R1 - 295), 2, 2.5, RED, 8, sfx="ding")
L(loop_icon(BX[1] + 330, R1 - 360, 45), 3, 3.5, RED, 8, sfx="wood_high")
b.hit(J(), 5, "pop", 0.6)

OX, OY = 420, R2 + 300       # 曲线坐标轴原点
CX0, CY0, CX1, CY1 = OX + 20, OY - 40, OX + 1060, OY - 700
scene("先慢，后面越来越快", "书中观点 · 先慢后快", (BX[0], R2, 0.85))
L(axes(OX, OY, 1120, 780), 0, 0.7, BLACK, 8, sfx="wood_high")
T("存款", OX + 110, OY - 745, 50, k0=0.5, k1=0.8)
T("时间", OX + 1000, OY - 70, 50, k0=0.7, k1=1.0)
L(exp_curve(CX0, CY0, CX1, CY1, 4.0, 0, 0.6), 1, 2.2, BLACK, 11, sfx="wood_low")
T("平平的", 900, OY - 260, 60, k0=2.3, k1=2.9)
L(exp_curve(CX0, CY0, CX1, CY1, 4.0, 0.6, 1.0), 3, 3.8, RED, 12, sfx="wood_high")
T("越来越快", 1030, OY - 640, 60, RED, k0=4, sfx="pop")
L(arrow((1250, OY - 450), (1330, OY - 640), 0.1, 34), 5, 5.4, RED, 8, sfx="ding")

scene("平的那段最想放弃", "书中观点 · 先慢后快", (BX[0], R2, 0.85))
L(stick(640, OY - 50, 0.45, "shrug"), 0, 0.6, BLUE, 8, sfx="pop")
L(face(640, OY - 50, 0.45, "sad"), 0.6, 0.8, BLUE, 6)
T("太慢了", 560, OY - 330, 54, BLUE, k0=2, sfx="pop")
L(cross(640, OY - 120, 80), 3, 3.35, RED, 11, sfx="rim")
b.hit(J(), 5, "tom", 0.6)

scene("越累越想刷手机", "书中观点 · 恶性循环", (BX[1], R2 + 180, 0.85))
L(loop_pair(NL, NR, R2 - 50, 110), 0, 0.8, BLACK, 10, sfx="wood_high")
L(circle(NL, R2 - 50, 110), 1, 1.3, RED, 9)
T("刷手机", NL, R2 - 50, 54, RED, k0=1, sfx="pop")
L(circle(NR, R2 - 50, 110), 2, 2.3, RED, 9)
T("没精力", NR, R2 - 50, 54, RED, k0=2, sfx="pop")
T("越刷越累，越累越刷", BX[1], R2 + 300, 62, RED, k0=3.5, k1=5.0)
b.hit(J(), 4, "rim", 0.7)

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 6450), (2650, 6450), (950, 7700), (2650, 7700)]
scene("身边到处都是", "身边的例子", (1800, 7075, 0.4))
T("身边的例子", 1800, 5930, 90, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), 1.5 + n * 0.8, 2.0 + n * 0.8, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

cx, cy = CARDS[0]
scene("越会做表，活越多", "例子 · 会做表的人", (cx, cy, 0.85))
L(stick(620, 6820, 0.8, "hold", hair=True), 0, 0.6, RED, sfx="wood_high")
L(join(rect(930, 6560, 220, 170, 10), P((870, 6620), (870, 6580)), P((930, 6620), (930, 6540)),
       P((990, 6620), (990, 6510))), 1, 1.5, BLACK, 8, sfx="pop")
L(bubble(1270, 6170, 330, 110, -1), 2, 2.4, BLACK, 7, sfx="pop")
T("帮我做个表", 1270, 6170, 50, k0=2.4, k1=3.0)
L(bubble(1300, 6380, 330, 110, -1), 3, 3.4, BLACK, 7, sfx="pop")
T("这个也帮下", 1300, 6380, 50, k0=3.4, k1=3.9)
for n, (w, x) in enumerate((("做得多 →", 820), ("更熟练 →", 1080), ("找的更多", 1350))):
    T(w, x, 6760, 50, RED if n == 2 else BLACK, k0=4.5 + n * 0.5, k1=4.9 + n * 0.5, sfx="pop" if n == 1 else None)
L(arrow((1400, 6810), (760, 6810), -0.08, 34), 4, 4.4, RED, 7, sfx="ding")

cx, cy = CARDS[1]
scene("越跑越想跑", "例子 · 跑步", (cx, cy, 0.85))
L(runner(2400, 6800, 0.9), 0, 0.7, BLUE, sfx="wood_high")
for n in range(3):
    L(P((2230, 6560 + n * 60), (2060, 6560 + n * 60)), 1 + n * 0.15, 1.3 + n * 0.15, BLUE, 7,
      sfx="shaker" if n == 0 else None)
T("每天一公里", 2950, 6150, 64, k0=2, sfx="pop")
for n, (x, h, w) in enumerate(((2780, 90, "1"), (2950, 220, "3"), (3120, 360, "5"))):
    L(rect(x, 6800 - h / 2, 110, h, 8), 3 + n * 0.6, 3.4 + n * 0.6, GREEN, 8, sfx="pop" if n == 0 else None)
    T(w, x, 6855, 48, k0=3.4 + n * 0.6, k1=3.6 + n * 0.6)
T("越跑越想跑", 2450, 6160, 60, RED, k0=5, k1=5.9, sfx="ding")

cx, cy = CARDS[2]
scene("越吵越凶", "例子 · 拌嘴", (cx, cy, 0.85), shake=[3])
L(join(stick(600, 8070, 0.75), stick(1300, 8070, 0.75, hair=True)), 0, 0.8, BLACK, 9, sfx="wood_high")
L(bubble(700, 7580, 260, 100, -1), 1, 1.3, BLACK, 7, sfx="pop")
T("你又忘了", 700, 7580, 48, k0=1.3, k1=1.7)
L(bubble(1200, 7580, 260, 100, 1), 2, 2.3, BLACK, 7, sfx="pop")
T("你才是", 1200, 7580, 48, k0=2.3, k1=2.7)
L(join(bubble(620, 7380, 380, 130, -1), scribble(620, 7380, 280, 70, 7)), 3, 3.5, RED, 8, sfx="rim")
L(join(bubble(1280, 7380, 380, 130, 1), scribble(1280, 7380, 280, 70, 7)), 4, 4.5, RED, 8, sfx="rim")
T("越吵越凶", 950, 7730, 70, RED, k0=5, k1=5.7, sfx="kick")

cx, cy = CARDS[3]
scene("欠款利滚利", "例子 · 只还最低", (cx, cy, 0.85))
L(credit_card(2380, 7550), 0, 0.8, BLACK, 9, sfx="wood_high")
T("最低还款", 2960, 7480, 60, k0=1, sfx="pop")
T("欠 ¥5000", 2960, 7630, 60, RED, k0=2, sfx="pop")
L(exp_curve(2250, 8070, 3250, 7720, 3.5), 3, 4.0, RED, 11, sfx="wood_high")
T("利滚利", 2520, 7910, 66, RED, k0=5, k1=5.6, sfx="rim")

scene("都在自己转圈", "身边的例子", (1800, 7075, 0.4), shake=[0])
for n, (x, y) in enumerate(CARDS):
    L(loop_icon(x + (560 if x < 1800 else -560), y - 330, 60), n, n + 0.5, GREEN if n < 2 else RED, 10,
      sfx=("kick", "wood_high", "wood_high", "wood_high")[n])
T("小差别，越滚越大", 1800, 8230, 110, k0=4, k1=5.4, sfx="pop")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 9400), (2650, 9400), (950, 10500), (2650, 10500)]

cx, cy = SOL[0]
scene("挑一件能滚的事", "第一步 · 挑能滚的", (cx, cy + 50, 0.85))
L(rect(cx, cy, 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("① 挑能滚的事", cx, 9110, 76, BLUE, k0=1, sfx="pop")
L(P((450, 9270), (1450, 9510)), 2, 2.4, BLACK, 7, sfx="wood_high")
for n, (x, r) in enumerate(((620, 32), (900, 55), (1240, 85))):
    y = 9270 + (x - 450) * 0.24 - r - 6
    L(circle(x, y, r), 2.4 + n * 0.2, 2.6 + n * 0.2, BLUE, 8)
for n, (w, x) in enumerate((("写作", 580), ("英语", 900))):
    T(w, x, 9670, 64, k0=3 + n, k1=3.4 + n, sfx="pop")
    L(check(x + 105, 9665, 30), 3.4 + n, 3.6 + n, GREEN, 8)
T("刷剧", 1260, 9670, 64, k0=5, k1=5.4, sfx="pop")
L(P((1180, 9670), (1340, 9670)), 5.5, 5.8, RED, 10)

cx, cy = SOL[1]
CELLS = grid_cells(cx, 9280)
scene("每天只做一点", "第二步 · 每天一点", (cx, cy + 40, 0.85))
L(rect(cx, cy, 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("② 每天一点", cx, 9110, 76, BLUE, k0=1, sfx="pop")
L(join(*[rect(x, y, 90, 90, 8) for x, y in CELLS]), 2, 2.9, BLACK, 6, sfx="wood_high")
T("一天读十页", cx, 9670, 64, RED, k0=3, k1=3.9, sfx="pop")
b.custom(J(), 4, 7.4, fill_checks(CELLS), sfx="shaker")
b.hit(J(), 6, "ding", 0.6)

cx, cy = SOL[2]
scene("收益投回去", "第三步 · 投回去", (cx, cy + 50, 0.85))
L(rect(cx, cy, 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("③ 收益投回去", cx, 10210, 76, BLUE, k0=1, sfx="pop")
T("奖金", 650, 10410, 64, k0=2, k1=2.4, sfx="pop")
L(arrow((740, 10410), (1150, 10410), 0, 34), 2.5, 2.9, BLACK, 8)
T("报课", 1250, 10410, 64, k0=3, k1=3.4, sfx="pop")
L(arrow((1230, 10460), (1030, 10620), -0.1, 30), 3.5, 3.9, BLACK, 8)
T("涨薪", 950, 10650, 64, GREEN, k0=4, k1=4.4, sfx="pop")
L(arrow((870, 10620), (670, 10460), -0.1, 30), 4.5, 4.9, BLACK, 8)
T("+", 950, 10500, 70, RED, k0=5, k1=5.3, sfx="ding")

cx, cy = SOL[3]
scene("坏回路早点掐断", "第四步 · 掐断坏回路", (cx, cy + 50, 0.85))
L(rect(cx, cy, 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("④ 掐断坏回路", cx, 10210, 76, BLUE, k0=1, sfx="pop")
L(loop_icon(2230, 10440, 60), 2, 2.4, RED, 9, sfx="wood_high")
T("刷手机", 2440, 10440, 54, RED, k0=2.4, k1=2.8)
L(P((2140, 10540), (2330, 10340)), 3, 3.3, BLACK, 12, sfx="rim")
L(door(2900, 10710), 4, 4.6, BLACK, 9, sfx="wood_high")
L(phone(3090, 10780), 5, 5.4, RED, 8, sfx="pop")
T("放门外", 3090, 10630, 52, RED, k0=5.4, k1=5.9)

scene("熬过平的那一段", "一句话", (1800, 8250, 0.235))
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 2, "wood_high", 0.6)
b.hit(J(), 4, "ding")

scene("评论区聊聊", "评论区见", (1800, 11400, 0.8))
b.hit(J(), 0, "cymbal", 0.5)
T("你想让哪件事滚起来？", 1800, 11320, 80, RED, k0=1, k1=2.6)
b.hit(J(), 1, "pop")
T("下一讲：为什么越着急，越容易出乱子？", 1800, 11480, 50, k0=3, k1=4.5)
b.hit(J(), 3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "reinforcing", "增强回路", "为什么有人越学越快？", ACC, b.shots,
                 [f"{BOOK}：增强回路（自我强化）、银行存款利息（转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                 "越学越快|靠的是【增强回路】", 7,
                 ["书中观点均为转述：增强回路（正反馈、自我强化回路）是“越多越多”的结构，存量越大带来的增长越多，增长又让存量更大；"
                  "书中例子为银行账户的利息，钱越多利息越多；增强回路可以形成良性循环，也可以形成恶性循环；"
                  "指数式增长早期不明显，后期越来越快。出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)，"
                  "中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                  "同事升组长、会做表的人活越多、跑步、拌嘴、信用卡只还最低还款均为现实场景示意，不指向任何具体公司或个人；"
                  "曲线、硬币、柱子均为示意，不是书中数据；四步做法为据书中思路整理的建议。"],
                 tags="#学习 #成长")
    return b.attach(ep)
