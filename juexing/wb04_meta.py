"""04 元认知（白板手绘版）：被说一句就上头，怎么刹住？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 juexing/build.py）。
叙事（形式 F 两人对比，开局“同一句话，两个人”）：白板上方中线一分为二，领导站在中线顶上说“这方案太粗了”，
左边阿杰、右边小林同时听到 → 左边当场拍桌回嘴 → 右边也上火，脑袋剖面里老二跳起来 →
drop：右边时间定格，宝宝从脑袋里飞出来，俯看底下攥拳的自己 → 亮书（书旁画舵，写“04”）→
后半讲拆右边那几秒（书中观点：元认知是看见自己正在想什么，能跳出来从旁边看自己；面对选择先停一下，
理智脑才赶得上；做自己思维的舵手）→ 示意：三句自问、换一句话说、一周后两人的结局 →
做法（下班前写一行：今天哪一下上头了）→ 拉回上方两栏看两条路 → 评论区。
系列角色：小林头上的脑袋剖面里住着老大（拄拐）、老二（戴耳机，RED）、宝宝（BLUE）；宝宝握舵，本讲添第 4 道握痕。
书中观点为转述（周岭《认知觉醒》第三章第一节“元认知”、第二节“自控力”）；两位同事、会议、三句自问、
一周后的结局、会后写一行均为示意或据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import ease_out, lerp
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, clock, cross, face,
                               hands_at, join, marker, rect, stick, underline)

from .common import BOOK, episode

ACC = "#5B4BA8"
SQUARE_SHOT = 3                 # 场景 4：宝宝飞到头顶俯看攥拳的自己，左边阿杰在拍桌

b = Board(size=(3600, 9900))
LX, RX, MID = 1250, 2350, 1800  # 上方两栏：左阿杰、右小林，领导站在中线顶上
FOOT = 2300                     # 两位同事的脚底
S0 = 0.85                       # 两位同事的身形
HY = FOOT - 290 * S0            # 两位同事的头部中心
BRAIN = (RX, 1680, 240)         # 小林头上的脑袋剖面
R1, R2, R3, R4 = 3400, 4900, 6400, 7900   # 下方各行的中心（行距 1500，上一行的字不漏进下一屏顶端）
CL, CR = 1000, 2600             # 下方左右两列


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def arc(x, y, r, a0, sweep) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), a0, sweep)
    return p


def baby(x, y, s=1.0, hands=None) -> skia.Path:
    """系列角色宝宝（理智脑）：大头、短身子、围嘴、头顶一撮毛。(x, y) 为脚底，身高约 255·s。"""
    r = 55 * s
    hy = y - 200 * s
    sh = (x, hy + r + 25 * s)
    hands = hands or [(x - 60 * s, y - 95 * s), (x + 60 * s, y - 95 * s)]
    tuft = skia.Path()
    tuft.moveTo(x, hy - r)
    tuft.quadTo(x + 22 * s, hy - r - 30 * s, x + 6 * s, hy - r - 38 * s)
    bib = skia.Path()
    bib.addArc(skia.Rect.MakeXYWH(x - 28 * s, hy + r - 14 * s, 56 * s, 40 * s), 0, 180)
    return join(circle(x, hy, r), tuft, circle(x - 18 * s, hy - 4 * s, 3.5 * s), circle(x + 18 * s, hy - 4 * s, 3.5 * s),
                bib, P((x, hy + r), (x, y - 75 * s)), P(hands[0], sh, hands[1]),
                P((x - 40 * s, y), (x, y - 75 * s), (x + 40 * s, y)))


def wings(x, y, s=1.0) -> skia.Path:
    """宝宝背后的一对小翅膀（“飞”起来看自己）。(x, y) 为宝宝脚底。"""
    parts = []
    for d in (-1, 1):
        w = skia.Path()
        w.moveTo(x + d * 12 * s, y - 120 * s)
        w.quadTo(x + d * 120 * s, y - 220 * s, x + d * 135 * s, y - 115 * s)
        w.quadTo(x + d * 80 * s, y - 125 * s, x + d * 12 * s, y - 100 * s)
        parts.append(w)
    return join(*parts)


def elder(x, y, s=1.0) -> skia.Path:
    """老大（本能脑）：拄拐的老爷爷。"""
    hy = y - 290 * s
    cane = join(P((x + 70 * s, hy + 150 * s), (x + 78 * s, y)), arc(x + 55 * s, hy + 150 * s, 15 * s, 180, 180))
    return join(stick(x, y, s, "down"), cane, P((x - 25 * s, hy + 20 * s), (x, hy + 45 * s), (x + 25 * s, hy + 20 * s)))


def uncle(x, y, s=1.0) -> skia.Path:
    """老二（情绪脑）：戴耳机的大叔，两手举起往上蹦。"""
    hy = y - 290 * s
    return join(stick(x, y, s, "up"), arc(x, hy, 58 * s, 180, 180), rect(x - 56 * s, hy, 18 * s, 36 * s, 6 * s),
                rect(x + 56 * s, hy, 18 * s, 36 * s, 6 * s))


def jump_lines(x, y, s=1.0) -> skia.Path:
    return join(*[P((x + dx * s, y + 18 * s), (x + dx * s, y + 55 * s)) for dx in (-40, 0, 40)])


def angry(x, y, s=1.0) -> skia.Path:
    """生气的脸：下撇的嘴 + 两道往里压的眉毛。(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(face(x, y, s, "sad"), P((x - 32 * s, hy - 30 * s), (x - 8 * s, hy - 18 * s)),
                P((x + 32 * s, hy - 30 * s), (x + 8 * s, hy - 18 * s)))


def fists(x, y, s=1.0) -> skia.Path:
    """攥紧的两个拳头 + 几道发抖的短线。(x, y) 为小人脚底（arms="down" 的手的位置）。"""
    hy = y - 290 * s
    parts = []
    for d in (-1, 1):
        hx, hh = x + d * 70 * s, hy + 170 * s
        parts += [circle(hx, hh, 20 * s), P((hx + d * 30 * s, hh - 25 * s), (hx + d * 48 * s, hh - 38 * s)),
                  P((hx + d * 32 * s, hh + 5 * s), (hx + d * 54 * s, hh + 5 * s))]
    return join(*parts)


def flame(x, y, s=1.0) -> skia.Path:
    """头顶冒的火：(x, y) 为火苗底部中点。"""
    fl = skia.Path()
    fl.moveTo(x, y - 170 * s)
    fl.quadTo(x + 85 * s, y - 70 * s, x + 35 * s, y)
    fl.lineTo(x - 35 * s, y)
    fl.quadTo(x - 85 * s, y - 70 * s, x, y - 170 * s)
    inner = skia.Path()
    inner.moveTo(x, y - 90 * s)
    inner.quadTo(x + 35 * s, y - 40 * s, x, y - 5 * s)
    inner.quadTo(x - 35 * s, y - 40 * s, x, y - 90 * s)
    return join(fl, inner)


def rays(x, y, r0=30, r1=75, angles=(-160, -125, -90, -55, -20)) -> skia.Path:
    return join(*[P((x + math.cos(math.radians(a)) * r0, y + math.sin(math.radians(a)) * r0),
                    (x + math.cos(math.radians(a)) * r1, y + math.sin(math.radians(a)) * r1)) for a in angles])


def wheel(x, y, r=150) -> skia.Path:
    """船舵：双圈轮缘 + 轮毂 + 八根伸出轮缘的把手。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.86), circle(x, y, r * 0.18)]
    for i in range(8):
        a = i / 8 * 2 * math.pi + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        parts += [P((x + ca * r * 0.18, y + sa * r * 0.18), (x + ca * r * 1.22, y + sa * r * 1.22)),
                  circle(x + ca * r * 1.28, y + sa * r * 1.28, r * 0.06)]
    return join(*parts)


def grips(x, y, r, angles) -> skia.Path:
    """舵上的握痕：横跨轮缘的粗短线。angles 为角度（0 为正右，顺时针）。"""
    return join(*[P((x + math.cos(math.radians(a)) * r * 0.78, y + math.sin(math.radians(a)) * r * 0.78),
                    (x + math.cos(math.radians(a)) * r * 1.08, y + math.sin(math.radians(a)) * r * 1.08))
                  for a in angles])


def stopwatch(x, y, r=100) -> skia.Path:
    """秒表：表盘 + 顶上的按钮 + 停住的指针。"""
    return join(clock(x, y, r), P((x, y - r), (x, y - r - 18)), rect(x, y - r - 34, 56, 30, 8),
                P((x + r * 0.72, y - r * 0.72), (x + r * 0.86, y - r * 0.86)), hands_at(x, y, r, 1, 10))


def bolt(x, y, s=1.0) -> skia.Path:
    return P((x + 25 * s, y - 80 * s), (x - 30 * s, y + 5 * s), (x + 12 * s, y + 5 * s), (x - 22 * s, y + 80 * s))


def eye(x, y, w=380, h=190) -> skia.Path:
    """杏仁形的眼睛（不含瞳孔）：w 为宽，h 为高。"""
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.quadTo(x, y - h, x + w / 2, y)
    p.quadTo(x, y + h, x - w / 2, y)
    return join(p, P((x - w / 2 - 30, y - 10), (x - w / 2, y)), P((x + w / 2 + 30, y - 10), (x + w / 2, y)))


def dashed(a, c, n=7) -> skia.Path:
    (x0, y0), (x1, y1) = a, c
    parts = []
    for i in range(n):
        t0, t1 = i / n, (i + 0.55) / n
        parts.append(P((lerp(x0, x1, t0), lerp(y0, y1, t0)), (lerp(x0, x1, t1), lerp(y0, y1, t1))))
    return join(*parts)


def oval(x, y, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    return p


def folder(x, y, w=150, h=110) -> skia.Path:
    return join(rect(x, y, w, h, 8), P((x - w / 2, y - h / 2 + 4), (x - w / 2, y - h / 2 - 22),
                                       (x - w / 2 + 55, y - h / 2 - 22), (x - w / 2 + 70, y - h / 2)))


def calendar(x, y, w=220, h=190, ticks=0) -> skia.Path:
    """台历：外框 + 顶栏 + 两个环；ticks 为格子里打的勾数（最多 3）。"""
    parts = [rect(x, y, w, h, 12), P((x - w / 2, y - h / 2 + 50), (x + w / 2, y - h / 2 + 50))]
    for dx in (-w / 4, w / 4):
        parts.append(P((x + dx, y - h / 2 - 22), (x + dx, y - h / 2 + 14)))
    for i in range(ticks):
        cx = x - w / 3 + i * w / 3
        parts.append(check(cx, y + 30, 26))
    return join(*parts)


def nod(x, hy, r=75) -> skia.Path:
    """点头：头两侧上下的两道弧线 + 小箭头。"""
    return join(arc(x, hy, r, 200, 40), arc(x, hy, r, 300, 40),
                P((x - r * 0.94 - 14, hy - r * 0.34 + 18), (x - r * 0.94, hy - r * 0.34), (x - r * 0.94 + 18, hy - r * 0.34 + 8)))


def table(x0, x1, y, h=100) -> skia.Path:
    return join(P((x0, y), (x1, y)), P((x0 + 40, y), (x0 + 40, y + h)), P((x1 - 40, y), (x1 - 40, y + h)))


BABY0 = (2480, 1800, 0.4)       # 宝宝在脑袋剖面里的位置（脚底 x, y, 身形）
BABY1 = (2700, 1500, 0.75)      # 宝宝飞出去后停的位置


def fly_fn(c, k, t):
    """宝宝从脑袋里飞出：沿弧线升到小林右上方，身子变大，长出小翅膀；路上拖几道速度线。"""
    e = ease_out(k)
    x = lerp(BABY0[0], BABY1[0], e) + 60 * math.sin(math.pi * e)
    y = lerp(BABY0[1], BABY1[1], e)
    s = lerp(BABY0[2], BABY1[2], e)
    if k < 1:
        for i, dx in enumerate((-30, 0, 30)):
            c.drawPath(P((x + dx * s, y + 30 + i * 4), (x + dx * s - 10, y + 90 + i * 8)), K.paint(BLUE, 0.4, 6))
    c.drawPath(join(baby(x, y, s, [(x - 70 * s, y - 230 * s), (x + 70 * s, y - 230 * s)]), wings(x, y, s)),
               marker(BLUE, 8))
    return None


def gap_fn(x0, x1, y, h, color=BLUE, alpha=0.3):
    """时间线上插进的一段空白：从左往右涂浅色。"""

    def fn(c, k, t):
        w = (x1 - x0) * ease_out(k)
        c.drawRect(skia.Rect.MakeXYWH(x0, y - h / 2, w, h), K.paint(color, alpha))
        return None

    return fn


# ---------------------------------------------------------------- 开局：同一句话，两个人（场景 1–4，上方两栏）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("同一句话", "会上 · 同一句话", (MID, 1320, 0.48), bars=2)
L(P((MID, 950), (MID, 2450)), 0, 0.8, BLACK, 7, sfx="wood_low")
L(stick(MID, 760, 0.75, "point", tie=True), 1, 1.8, BLACK, 10, sfx="wood_high")
L(join(rect(2330, 430, 640, 170, 40), P((2170, 515), (2060, 590), (2250, 515))), 2, 2.8, BLACK, 9, sfx="pop")
T("这方案太粗了", 2330, 430, 90, RED, k0=2.8, k1=4.0)
L(stick(LX, FOOT, S0), 4, 4.8, BLACK, 10, sfx="wood_high")
L(stick(RX, FOOT, S0), 5, 5.8, BLACK, 10, sfx="wood_high")

scene("左边当场回嘴", "左边 · 阿杰", (LX, 1950, 0.85))
L(table(1300, 1720, 2200), 0, 0.9, BLACK, 9, sfx="wood_low")
L(rays(1310, 2195), 1, 1.5, RED, 8, sfx="kick")
T("啪！", 1560, 2080, 100, RED, k0=1.5, k1=2.0)
L(angry(LX, FOOT, S0), 2, 2.8, BLACK, 8, sfx="wood_high")
L(flame(LX, 2005, 0.55), 3, 3.9, RED, 9, sfx="rim")
L(join(rect(1530, 1640, 380, 130, 40), P((1440, 1705), (1400, 1770), (1500, 1705))), 4, 4.6, BLACK, 8, sfx="pop")
T("那你来写", 1530, 1640, 64, RED, k0=4.6, k1=5.6)
T("阿杰", LX, 2400, 60, k0=6, k1=6.8, sfx="pop")

BX, BY, BR = BRAIN
scene("右边也上火了", "右边 · 小林", (RX, 1950, 0.85))
L(join(circle(BX, BY, BR), circle(BX - 8, 1950, 12), circle(BX + 4, 1985, 8)), 0, 0.9, BLACK, 8, sfx="wood_low")
L(join(elder(2230, 1800, 0.5), baby(*BABY0)), 1, 1.9, BLACK, 7, sfx="wood_high")
L(uncle(2360, 1780, 0.5), 2, 2.8, RED, 8, sfx="tom")
L(jump_lines(2360, 1780, 0.5), 3, 3.5, RED, 6, sfx="shaker")
T("情绪脑", 2360, 1530, 46, RED, k0=4, k1=4.8, sfx="pop")
L(join(fists(RX, FOOT, S0), angry(RX, FOOT, S0)), 5, 5.9, BLACK, 8, sfx="wood_high")
T("小林", RX, 2400, 60, k0=6, k1=6.8, sfx="pop")

scene("他先飞起来", "右边 · 时间定格", (2050, 2000, 0.6), shake=[0], flashes=[0])
L(stopwatch(1990, 1420, 100), 0, 0.9, RED, 9, sfx="kick")
T("定格", 1990, 1600, 80, RED, k0=1, k1=1.8, sfx="pop")
b.erase(J(), 2, 2.3, BABY0[0], 1740, 90, 150)
b.custom(J(), 2, 3.6, fly_fn, sfx="shaker")
L(join(dashed((2670, 1520), (2400, 1990)), dashed((2730, 1520), (2470, 2000))), 4, 4.9, BLUE, 7, sfx="wood_high")
T("看见自己", 2720, 2250, 80, BLUE, k0=6, k1=7.0, sfx="ding")

# ---------------------------------------------------------------- 亮书 + 书中观点（场景 5–7）

scene("有本书讲过", "有本书讲过 · 认知觉醒", (CR, R1, 0.85))
L(book(2400, R1 + 20, 420, 280), 0, 0.9, BLACK, 9, sfx="wood_low")
T("《认知觉醒》", 2400, R1 - 250, 64, GREEN, k0=1, k1=2.5, sfx="pop")
T("周岭", 2400, R1 + 280, 56, k0=3, k1=3.8, sfx="pop")
L(wheel(2980, R1 - 20, 150), 4, 4.9, GREEN, 8, sfx="wood_high")
T("04", 2980, R1 + 250, 80, RED, k0=6, k1=6.8, sfx="ding")

scene("看见自己在想啥", "书中观点 · 元认知", (CL, R1, 0.85))
L(stick(CL, R1 + 500, 0.8), 0, 0.9, BLACK, 10, sfx="wood_high")
L(eye(CL, R1 - 170), 1, 1.9, BLUE, 9, sfx="pop")
L(join(circle(CL, R1 - 170, 62), stick(CL, R1 - 125, 0.2)), 2, 2.8, BLUE, 6, sfx="ding")
L(join(dashed((CL - 35, R1 - 70), (CL - 60, R1 + 220), 6), dashed((CL + 35, R1 - 70), (CL + 60, R1 + 220), 6)),
  3, 3.8, BLUE, 6, sfx="wood_low")
T("元认知", 1470, R1 - 170, 80, RED, k0=4, k1=4.8, sfx="pop")
T("跳出来看自己", CL, R1 - 420, 60, BLUE, k0=6, k1=7.5, sfx="pop")

TL = R2 + 50                    # 时间线的高度
scene("先停几秒", "书中观点 · 先停一下", (CL, R2 + 60, 0.85))
L(arrow((420, TL), (1590, TL), 0, 36), 0, 0.9, BLACK, 9, sfx="wood_low")
L(bolt(500, R2 - 110, 0.9), 1, 1.6, RED, 10, sfx="rim")
T("被说", 500, R2 + 170, 60, RED, k0=1.6, k1=2.4)
L(rect(1450, R2 - 110, 220, 110, 20), 3, 3.6, BLACK, 8, sfx="wood_high")
T("回应", 1450, R2 - 110, 60, k0=3.6, k1=4.4)
b.custom(J(), 5, 5.8, gap_fn(850, 1150, TL, 70), sfx="ding")
L(join(P((850, TL - 60), (850, TL + 60)), P((1150, TL - 60), (1150, TL + 60))), 5, 5.8, BLUE, 9)
L(baby(1000, TL - 8, 0.45), 6, 6.8, BLUE, 7, sfx="pop")
T("停几秒", 1000, R2 + 190, 64, BLUE, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- 示意：右边那几秒（场景 8–10）

scene("他问了自己三句", "示意 · 问自己三句", (CR, R2, 0.85))
L(rect(CR, R2, 900, 720, 24), 0, 0.8, BLACK, 8, sfx="wood_low")
for n, s in enumerate(("我在气啥？", "他要的是啥？", "我想要啥结果？")):
    y = R2 - 200 + n * 200
    T(s, 2530, y, 64, k0=1 + 2 * n, sfx="pop")
    L(check(2930, y, 40), 1 + 2 * n + 0.25 * len(s) + 0.05, 1 + 2 * n + 0.25 * len(s) + 0.45, GREEN, 10)

scene("他说了另一句", "右边 · 小林开口", (CR, R3, 0.85))
L(stick(2200, R3 + 350, 0.75), 0, 0.9, BLACK, 10, sfx="wood_high")
L(stick(3000, R3 + 350, 0.75, tie=True), 1, 1.9, BLACK, 10, sfx="wood_high")
L(join(oval(2450, R3 - 300, 360, 160), P((2330, R3 - 148), (2250, R3 - 60), (2410, R3 - 145))), 2, 2.9, BLUE, 8,
  sfx="pop")
T("哪块粗？", 2450, R3 - 350, 60, k0=3, k1=4.0, sfx="pop")
T("我下午补一版", 2450, R3 - 240, 60, k0=4, k1=5.5, sfx="pop")
L(join(nod(3000, R3 + 132 - 15), face(3000, R3 + 350, 0.75, "smile")), 6, 6.8, GREEN, 7, sfx="ding")
T("行", 3150, R3 - 80, 70, GREEN, k0=7, k1=7.8, sfx="pop")

scene("一周后", "一周后", (CL, R3, 0.85))
L(join(calendar(CL, R3 - 400), P((CL, R3 - 260), (CL, R3 + 450))), 0, 0.7, BLACK, 8, sfx="wood_low")
T("+7", CL, R3 - 375, 60, RED, k0=0.7, k1=1.0)
L(join(stick(650, R3 + 350, 0.7), folder(830, R3 + 80)), 1, 1.9, BLACK, 9, sfx="wood_high")
L(cross(830, R3 + 70, 70), 2, 2.6, RED, 11, sfx="rim")
T("项目换人", 650, R3 + 480, 56, RED, k0=3, k1=4.0, sfx="pop")
L(join(stick(1350, R3 + 350, 0.7, "hold"), folder(1500, R3 + 150)), 4, 4.9, BLACK, 9, sfx="wood_high")
T("留下了", 1350, R3 + 480, 56, GREEN, k0=5, k1=5.8, sfx="pop")
L(check(1500, R3 - 60, 55), 6, 6.6, GREEN, 11, sfx="ding")

# ---------------------------------------------------------------- 书中观点 + 做法（场景 11–12）

WH = (1060, R4 + 120, 170)      # 舵
scene("宝宝握住了舵", "书中观点 · 思维舵手", (CL, R4, 0.85))
L(join(wheel(*WH), grips(*WH, (-60, 0, 60))), 0, 1.0, GREEN, 9, sfx="wood_low")
L(baby(760, R4 + 400, 0.9, [(898, WH[1] - 50), (898, WH[1] + 50)]), 1, 1.9, BLUE, 9, sfx="pop")
L(grips(*WH, (180,)), 2, 2.5, RED, 16, sfx="ding")
T("回嘴", 620, R4 - 330, 64, RED, k0=3, k1=3.8, sfx="pop")
L(arrow((710, R4 - 320), (1330, R4 - 320), -0.2, 40), 4, 4.9, GREEN, 9, sfx="wood_high")
T("问一句", 1440, R4 - 330, 64, GREEN, k0=5, k1=5.8, sfx="pop")
L(underline(1350, 1530, R4 - 280, 10, 30), 6, 6.6, GREEN, 7, sfx="wood_low")

scene("会后写一行", "做法 · 下班前写一行", (CR, R4, 0.85))
L(join(rect(2450, R4, 460, 780, 50), P((2400, R4 + 350), (2500, R4 + 350))), 0, 1.0, BLACK, 9, sfx="wood_low")
T("备忘录", 2450, R4 - 290, 52, k0=1, k1=1.8, sfx="pop")
T("哪一下上头？", 2450, R4 - 130, 52, RED, k0=2, k1=3.5, sfx="pop")
T("开会时脸红了", 2450, R4 + 10, 52, BLUE, k0=4, k1=5.5, sfx="pop")
L(calendar(2990, R4 - 60, 260, 240, ticks=3), 6, 6.8, BLACK, 8, sfx="wood_high")
T("每天一行", 2990, R4 + 160, 60, GREEN, k0=7, k1=8.0, sfx="ding")

# ---------------------------------------------------------------- 收束（场景 13：回到上方两栏）

scene("两条路", "两个人 · 两条路", (MID, 1500, 0.41))
L(arrow((1770, 800), (1430, 1060), 0.15, 46), 0, 0.9, RED, 10, sfx="wood_low")
L(arrow((1830, 800), (2170, 1060), -0.15, 46), 1, 1.9, GREEN, 10, sfx="wood_low")
T("当场回嘴", LX, 2560, 110, RED, k0=2, k1=3.0, sfx="pop")
T("停了几秒", RX, 2560, 110, GREEN, k0=4, k1=5.0, sfx="pop")
L(cross(1545, 2560, 42), 6, 6.6, RED, 12, sfx="rim")
L(check(2655, 2560, 50), 7, 7.6, GREEN, 12, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FULL = (1800, 4950, 0.112)
CY = 9300
COMMENT = (MID, CY, 0.85)
scene("评论区聊聊", "评论区见", FULL, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(rect(MID, CY - 110, 1000, 300, 40), 5, 5.8, RED, 8, sfx="pop")
T("你最近一次上头", MID, CY - 170, 76, RED, k0=6, k1=7.75, sfx="pop")
T("是因为啥？", MID, CY - 50, 76, RED, k0=8, k1=9.25)
T("下一讲：忙了一整天，正事一件没干？", MID, CY + 170, 50, k0=10, k1=14.25, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "meta", "元认知", "被说一句就上头，怎么刹住？", ACC, b.shots,
                 [f"{BOOK}第三章 元认知——人类的终极能力：第一节 元认知、第二节 自控力（转述）"],
                 "被说一句|就上头，怎么【刹住】", SQUARE_SHOT,
                 ["书中观点均为转述（第三章第一节“元认知”、第二节“自控力”）：元认知是对自己思维的觉察，"
                  "能跳出来、从旁边看自己正在想什么（书里说成“飞”起来看）；面对选择先停一下，给理智脑上场的机会；"
                  "做自己思维的舵手。上屏均为转述，不是逐字引文；“先停几秒”不写具体秒数，书中是否写死“三秒”未核实。",
                  "三重大脑的“老大 / 老二 / 宝宝”、宝宝飞出脑袋、秒表定格、时间线上插进的空白、舵与握痕均为对书中观点的"
                  "通俗化示意（系列视觉角色，见 juexing/PLAN.md）。",
                  "阿杰与小林、领导那句“这方案太粗了”、两人的回应、三句自问、一周后“项目换人 / 留下了”的结局均为现实场景示意，"
                  "不指向任何具体公司或个人；结局只为对照，不是数据，也不代表书中结论。",
                  "做法（下班前在备忘录写一行：今天哪一下上头了）为据书中思路整理的建议。"],
                 tags="#情绪管理 #职场沟通")
    return b.attach(ep)
