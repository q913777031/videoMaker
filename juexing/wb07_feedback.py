"""07 反馈（白板手绘版）：打卡一百天，怎么没变化？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 juexing/build.py）。
叙事（形式 D 误区对照，开局“一面贴满勾的日历”）：一面日历打满一百个勾 → 小林一年读了三十本书 →
同事问“哪本好？”，他一本都讲不出 → drop：一阵风把一百个勾全卷走，一张写着“会了啥？”的空卡砸在日历上 →
亮书（书旁画舵，写“07”）→ 中段四屏一屏一对，中线分开，左栏 ✗ 常见做法、右栏 ✓ 书里说的：
打卡换成记录、上限换成下限、一本书抓一个点去用、做出来换意见 → 读书的六层台阶（封面镜头）→
费曼技巧：讲到外行听懂 → 做法：读完一章，午饭讲给同事听三分钟 → 拉远看四对，右栏四个绿勾依次亮，
再推到小林脑袋里：宝宝握舵，舵上添第 7 道握痕 → 评论区。
系列角色：小林头上的脑袋剖面里住着老大（拄拐）、老二（戴耳机）、宝宝（BLUE）；宝宝握舵，本讲添第 7 道握痕（前 6 道 GREEN，新的一道 RED）。
书中观点为转述（周岭《认知觉醒》第五章 学习力：第二节 深度、第五节 打卡、第六节 反馈；第二章第二节 感性、后记；
第八章第四节 写作）；小林的一百个勾、三十本书、同事那句“哪本好？”、会议纪要先写结论、午饭讲三分钟均为示意，据书中思路整理。
"""

import math
import random

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross, desk,
                               doc, face, join, marker, rect, stick, underline)

from .common import BOOK, episode

ACC = "#2E8F86"
SQUARE_SHOT = 10                 # 场景 11：小林用大白话讲给奶奶听（人物 + 费曼技巧）

b = Board(size=(3600, 21000))
MID, XL, XR = 1800, 1350, 2250  # 误区对照：中线、左栏（✗）、右栏（✓）
ZP = 0.62                       # 对照屏的视角缩放（一屏装下左右两栏）
R1, R2, R3, R4 = 5900, 7900, 9900, 11900   # 四对的行中心（行距 2000，上一行的字不漏进下一屏页眉）
R5 = 13900                      # 读书的六层台阶
R6 = 15900                      # 费曼技巧 / 午饭讲三分钟
HEAD = (1800, 17750, 360)       # 小林的脑袋剖面（场景 13 推近）
CY = 19600                      # 评论区
DROP_J = 3                      # 场景 4（从 0 数）：音乐 drop


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

def mirror(path: skia.Path, x: float) -> skia.Path:
    """以竖线 x 为轴左右翻转（让 point 小人朝左指）。"""
    m = skia.Matrix()
    m.setScale(-1, 1, x, 0)
    out = skia.Path(path)
    out.transform(m)
    return out


def arc(x, y, r, a0, sweep) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), a0, sweep)
    return p


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def thought(x, y, w, h, fx, fy) -> skia.Path:
    """想法泡泡：云朵 (x, y, w, h) + 两个小圆点连到 (fx, fy)。"""
    parts = [oval(x, y, w, h)]
    for f, r in ((0.35, 14), (0.65, 20)):
        parts.append(circle(fx + (x - fx) * f, fy + (y + h * 0.5 - fy) * f, r))
    return join(*parts)


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


def elder(x, y, s=1.0) -> skia.Path:
    """老大（本能脑）：拄拐的老爷爷。"""
    hy = y - 290 * s
    cane = join(P((x + 70 * s, hy + 150 * s), (x + 78 * s, y)), arc(x + 55 * s, hy + 150 * s, 15 * s, 180, 180))
    return join(stick(x, y, s, "down"), cane, P((x - 25 * s, hy + 20 * s), (x, hy + 45 * s), (x + 25 * s, hy + 20 * s)))


def uncle(x, y, s=1.0) -> skia.Path:
    """老二（情绪脑）：戴耳机的大叔。"""
    hy = y - 290 * s
    return join(stick(x, y, s, "down"), arc(x, hy, 58 * s, 180, 180), rect(x - 56 * s, hy, 18 * s, 36 * s, 6 * s),
                rect(x + 56 * s, hy, 18 * s, 36 * s, 6 * s))


def rudder(x, y, r=140) -> skia.Path:
    """船舵：轮圈 + 轮毂 + 八根辐条伸出把手。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.22)]
    for i in range(8):
        a = i / 8 * 2 * math.pi
        parts.append(P((x + math.cos(a) * r * 0.22, y + math.sin(a) * r * 0.22),
                       (x + math.cos(a) * r * 1.28, y + math.sin(a) * r * 1.28)))
        parts.append(circle(x + math.cos(a) * r * 1.33, y + math.sin(a) * r * 1.33, r * 0.07))
    return join(*parts)


def grips(x, y, r, idx) -> skia.Path:
    """舵圈上的握痕：idx 为第几道（从 0 起），每道是轮圈外侧一小段短横。"""
    parts = []
    for i in idx:
        a = (-90 + 22.5 + i * 45) / 180 * math.pi
        for d in (-0.12, 0.0, 0.12):
            b0 = a + d
            parts.append(P((x + math.cos(b0) * r * 0.86, y + math.sin(b0) * r * 0.86),
                           (x + math.cos(b0) * r * 1.14, y + math.sin(b0) * r * 1.14)))
    return join(*parts)


# 日历：10 列 × 10 行，一格一个勾
CAL = (1800, 1000, 1300, 1000)
CAL_TOP = CAL[1] - CAL[3] / 2 + 100       # 顶栏下沿
CW, CH = CAL[2] / 10, (CAL[3] - 100) / 10


def calendar_frame() -> skia.Path:
    x, y, w, h = CAL
    top = y - h / 2
    return join(rect(x, y, w, h, 18), P((x - w / 2, CAL_TOP), (x + w / 2, CAL_TOP)),
                P((x - 300, top - 40), (x - 300, top + 30)), P((x + 300, top - 40), (x + 300, top + 30)))


def calendar_grid() -> skia.Path:
    x, y, w, h = CAL
    x0, y1 = x - w / 2, y + h / 2
    parts = [P((x0 + i * CW, CAL_TOP), (x0 + i * CW, y1)) for i in range(1, 10)]
    parts += [P((x0, CAL_TOP + i * CH), (x0 + w, CAL_TOP + i * CH)) for i in range(1, 10)]
    return join(*parts)


def cell(i):
    col, row = i % 10, i // 10
    return CAL[0] - CAL[2] / 2 + CW * (col + 0.5), CAL_TOP + CH * (row + 0.5), col


_rng = random.Random(7)
TICK_FLY = [(_rng.uniform(0, 0.16), _rng.uniform(-1, 1), _rng.uniform(-1, 1)) for _ in range(100)]


def ticks_fn(c, k, t):
    """一百个打卡勾依次打满；到了 drop（场景 4 第 0 拍）被一阵风从左往右卷走，边飞边转边变淡。"""
    td = b.t_of(DROP_J, 0)
    n = int(100 * k + 1e-6)
    tip = None
    for i in range(n):
        x, y, col = cell(i)
        rot, s = 0.0, 1.0
        alpha = 1.0
        if t >= td:
            d0, ry, rr = TICK_FLY[i]
            f = clamp01((t - td - col * 0.035 - d0) / 0.75)
            if f >= 1:
                continue
            x += 2000 * f * f + 120 * f
            y += -520 * f * (0.6 + 0.4 * ry) + 260 * f * f * rr
            rot = 420 * f * (1 if rr > 0 else -1)
            s = 1 + 0.6 * f
            alpha = 1 - f * f
        elif i == n - 1 and k < 1:
            s = 1.25
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(s, s)
        c.drawPath(check(0, 0, 28), marker(BLUE, 8, alpha))
        c.restore()
        if k < 1 and i == n - 1:
            tip = (x + 28, y - 22)
    return tip


def wind_fn(c, k, t):
    """一阵风：几道弯弯的风线从左扫到右，扫完就没。"""
    if k >= 1:
        return None
    for i, yy in enumerate((560, 780, 1000, 1220, 1440)):
        head = clamp01(k * 1.4 - i * 0.07)
        tail = clamp01(head - 0.4)
        if head <= 0:
            continue
        x0, x1 = 700 + tail * 2400, 700 + head * 2400
        p = skia.Path()
        p.moveTo(x0, yy)
        steps = 12
        for s in range(1, steps + 1):
            xx = x0 + (x1 - x0) * s / steps
            p.lineTo(xx, yy + 40 * math.sin(xx / 140 + i))
        c.drawPath(p, marker(BLACK, 9, 0.45 * (1 - k * 0.6)))
    return None


CARD = (1800, 1060, 780, 560)


def card_fn(c, k, t):
    """空卡片砸下：从 1.6 倍落到原大，落地带一圈尘线。"""
    x, y, w, h = CARD
    f = ease_out(k)
    s = 1 + 0.6 * (1 - f)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    K.rr(c, 22, 26, w, h, 30, BLACK, 0.12 * f)
    K.rr(c, 0, 0, w, h, 30, "#FFFFFF")
    c.drawPath(rect(0, 0, w, h, 30), marker(BLACK, 9))
    c.restore()
    if 0.6 < k:
        g = clamp01((k - 0.6) / 0.4)
        for d in (-1, 1):
            for j in range(3):
                x0 = x + d * (w / 2 + 30 + j * 10)
                y0 = y + h / 2 - 40 - j * 70
                c.drawPath(P((x0, y0), (x0 + d * 70 * g, y0 - 20 * g)), marker(BLACK, 7, 1 - 0.5 * g))
    return None


def book_stack(x, base, n=7) -> skia.Path:
    """一摞书：n 本，宽窄、左右略有错落。"""
    parts = []
    y = base
    for i in range(n):
        w, h = 300 - (i % 3) * 30, 52
        dx = ((i * 37) % 50) - 25
        parts.append(rect(x + dx, y - h / 2, w, h, 8))
        parts.append(P((x + dx - w / 2 + 30, y - h / 2), (x + dx + w / 2 - 30, y - h / 2)))
        y -= h
    return join(*parts)


def phone(x, y, w=110, h=180) -> skia.Path:
    return join(rect(x, y, w, h, 16), P((x - 16, y + h / 2 - 22), (x + 16, y + h / 2 - 22)))


def sweat(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y - 30 * s)
    p.quadTo(x + 22 * s, y + 5 * s, x, y + 20 * s)
    p.quadTo(x - 22 * s, y + 5 * s, x, y - 30 * s)
    return join(p, P((x + 40 * s, y - 50 * s), (x + 55 * s, y - 80 * s)))


def pair_marks(R) -> skia.Path:
    """对照屏的骨架：中线 + 左上角 ✗ + 右上角 ✓。"""
    return join(P((MID, R - 650), (MID, R + 650)), cross(XL - 330, R - 560, 34), check(XR - 330, R - 560, 40))


def boxes(x, y, n=3, s=150, gap=40) -> skia.Path:
    """n×n 的打卡小方格。"""
    parts = []
    step = s + gap
    for r in range(n):
        for col in range(n):
            parts.append(rect(x + (col - (n - 1) / 2) * step, y + (r - (n - 1) / 2) * step, s, s, 14))
    return join(*parts)


def box_ticks(x, y, n=3, s=150, gap=40) -> skia.Path:
    step = s + gap
    return join(*[check(x + (col - (n - 1) / 2) * step, y + (r - (n - 1) / 2) * step, s * 0.3)
                  for r in range(n) for col in range(n)])


def notebook(x, y, w, h) -> skia.Path:
    """笔记本：外框 + 左侧一排装订圈。"""
    parts = [rect(x, y, w, h, 16)]
    for i in range(5):
        parts.append(circle(x - w / 2, y - h / 2 + 70 + i * (h - 140) / 4, 16))
    return join(*parts)


def book_pile(x, base, rows=4, bw=150, bh=60) -> skia.Path:
    """书山：底层 rows 本，往上每层少一本。"""
    parts = []
    for r in range(rows):
        n = rows - r
        y = base - bh / 2 - r * bh
        for i in range(n):
            parts.append(rect(x + (i - (n - 1) / 2) * bw, y, bw - 12, bh - 8, 6))
    return join(*parts)


def sticky(x, y, w=300, h=170) -> skia.Path:
    return join(rect(x, y, w, h, 6), P((x + w / 2 - 50, y + h / 2), (x + w / 2, y + h / 2 - 50)))


def sketch_card(x, y, w=230, h=170) -> skia.Path:
    """举起的一张作品：画框里一条小折线。"""
    return join(rect(x, y, w, h, 10),
                P((x - w / 2 + 30, y + h / 2 - 40), (x - 20, y), (x + 20, y + 25), (x + w / 2 - 30, y - h / 2 + 40)))


def mini_bubbles(x, ys, w=240, h=120) -> skia.Path:
    """三条意见：三个小气泡，里面两道横线。"""
    parts = []
    for y in ys:
        parts += [bubble(x, y, w, h, -1), P((x - w / 2 + 35, y - 15), (x + w / 2 - 35, y - 15)),
                  P((x - w / 2 + 35, y + 22), (x + w / 4, y + 22))]
    return join(*parts)


STEP_W, STEP_H = 250, 170
STAIR_X0, STAIR_BASE = 1150, R5 + 560
STEPS = ["听书", "自己读", "摘抄", "笔记", "实践", "讲给别人"]


def stairs() -> skia.Path:
    pts = [(STAIR_X0, STAIR_BASE)]
    for i in range(6):
        top = STAIR_BASE - (i + 1) * STEP_H
        pts += [(STAIR_X0 + i * STEP_W, top), (STAIR_X0 + (i + 1) * STEP_W, top)]
    pts.append((STAIR_X0 + 6 * STEP_W, STAIR_BASE))
    return join(P(*pts, close=True), P((STAIR_X0 - 300, STAIR_BASE), (STAIR_X0, STAIR_BASE)))


def grandma(x, y, s=1.0) -> skia.Path:
    """奶奶：小人 + 脑后的发髻 + 一根拐杖。"""
    hy = y - 290 * s
    return join(stick(x, y, s, "down"), circle(x + 30 * s, hy - 48 * s, 20 * s),
                P((x - 70 * s, hy + 170 * s), (x - 80 * s, y)))


def nod(x, hy, r=75) -> skia.Path:
    """点头：头两侧上下的两道弧线。"""
    return join(arc(x, hy, r, 200, 40), arc(x, hy, r, 300, 40))


def table(x0, x1, y, h=110) -> skia.Path:
    return join(P((x0, y), (x1, y)), P((x0 + 40, y), (x0 + 40, y + h)), P((x1 - 40, y), (x1 - 40, y + h)))


def bowl(x, y, r=60) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r * 0.9, 2 * r, 1.8 * r), 0, 180)
    return join(p, P((x - r - 10, y), (x + r + 10, y)))


def hourglass(x, y, s=1.0) -> skia.Path:
    w, h = 110 * s, 170 * s
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2)), P((x - w / 2, y + h / 2), (x + w / 2, y + h / 2)),
                P((x - w / 2 + 10, y - h / 2), (x + w / 2 - 10, y + h / 2)),
                P((x + w / 2 - 10, y - h / 2), (x - w / 2 + 10, y + h / 2)),
                P((x - 18 * s, y + h / 2 - 12 * s), (x + 18 * s, y + h / 2 - 12 * s)))


# ---------------------------------------------------------------- 开局：一面贴满勾的日历（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("一百个勾", "开局 · 打卡日历", (1800, 900, 0.6), bars=2)
L(calendar_frame(), 0, 0.9, BLACK, 10, sfx="wood_high")
L(calendar_grid(), 1, 1.9, BLACK, 5, sfx="wood_low")
b.custom(J(), 2, 4.6, ticks_fn, sfx="pop")
H(3, "pop", 0.6)
H(4, "pop", 0.6)
T("打卡 100 天", 1800, 585, 80, k0=5, k1=6.0, sfx="ding")

scene("读了三十本书", "开局 · 小林的一年", (1350, 2500, 0.85))
L(book_stack(1000, 3000), 0, 1.0, BLACK, 8, sfx="wood_low")
T("30 本", 1000, 2480, 96, RED, k0=1.5, k1=2.5)
H(2, "pop")
L(stick(1500, 3000, 0.9, "hold"), 3, 3.9, BLACK, 10, sfx="pop")
L(phone(1680, 2700), 5, 5.7, BLACK, 8, sfx="wood_high")
L(check(1680, 2690, 30), 5.7, 6.0, BLUE, 9)
T("天天打卡", 1700, 2900, 60, BLUE, k0=6, k1=7.0, sfx="pop")
L(underline(880, 1120, 2540, 10, 30), 7, 7.7, RED, 7, sfx="ding")

scene("一本都讲不出", "开局 · 被问住了", (1950, 2500, 0.85))
L(mirror(stick(2350, 3000, 0.9, "point"), 2350), 0, 0.9, BLACK, 10, sfx="wood_high")
L(bubble(2280, 2290, 380, 150, -1), 1, 1.8, BLACK, 9, sfx="wood_low")
T("哪本好？", 2280, 2312, 64, k0=2, k1=3.0, sfx="pop")
L(thought(1560, 2240, 340, 200, 1500, 2690), 4, 4.9, BLACK, 8, sfx="wood_high")
T("？", 1560, 2272, 110, RED, k0=5, k1=5.8, sfx="rim")
L(sweat(1400, 2690, 1.0), 6, 6.6, BLUE, 7, sfx="shaker")
L(face(1500, 3000, 0.9, "sad"), 7, 7.4, BLACK, 8, sfx="wood_low")

# ---------------------------------------------------------------- drop：勾被风卷走，空卡砸下（场景 4）

scene("勾都被吹走了", "掉坑 · 一阵风", (1800, 950, 0.6), shake=[0], flashes=[0])
b.custom(J(), 0, 1.6, wind_fn, sfx="kick")
H(1, "shaker")
b.custom(J(), 2, 2.5, card_fn, sfx="kick")
T("会了啥？", 1800, 1010, 130, RED, k0=4, k1=5.0, sfx="pop")
L(join(P((1520, 1170), (2080, 1170)), P((1520, 1250), (1900, 1250))), 5, 5.8, BLACK, 5, sfx="wood_low")
L(P((1540, 580), (2060, 580)), 6, 6.6, RED, 12, sfx="rim")

# ---------------------------------------------------------------- 亮书（场景 5）

scene("有本书讲过", "亮书 · 认知觉醒", (1800, 3900, 0.85))
L(book(1550, 3950, 440, 300), 0, 0.9, BLACK, 9, sfx="wood_low")
T("《认知觉醒》", 1550, 3700, 72, GREEN, k0=1, k1=2.5, sfx="pop")
T("周岭", 1550, 4230, 56, k0=3, k1=3.8, sfx="pop")
L(rudder(2200, 3880, 130), 4, 4.9, GREEN, 8, sfx="wood_high")
T("07", 2200, 4170, 80, RED, k0=5, k1=5.8, sfx="ding")
T("第五章 学习力", 1800, 3460, 56, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 四对误区（场景 6–9）：中线分开，左 ✗ 右 ✓

scene("打卡换成记录", "误区一 · 打卡和记录", (MID, R1, ZP))
L(pair_marks(R1), 0, 0.9, BLACK, 7, sfx="wood_low")
T("只数勾", XL + 40, R1 - 535, 72, RED, k0=1, k1=1.8, sfx="pop")
L(boxes(XL, R1 + 120), 2, 2.9, BLACK, 8, sfx="wood_high")
L(box_ticks(XL, R1 + 120), 3, 3.8, BLACK, 9, sfx="pop")
T("记下学到啥", XR + 40, R1 - 535, 72, GREEN, k0=4, k1=5.25, sfx="pop")
L(notebook(XR + 20, R1 + 120, 640, 560), 5, 5.9, BLACK, 8, sfx="wood_high")
T("会议纪要", XR + 40, R1 + 50, 72, BLUE, k0=6, k1=6.9, sfx="pop")
T("先写结论", XR + 40, R1 + 200, 72, BLUE, k0=7, k1=8.0, sfx="pop")

scene("上限换成下限", "误区二 · 上限和下限", (MID, R2, ZP))
L(pair_marks(R2), 0, 0.9, BLACK, 7, sfx="wood_low")
T("必须一小时", XL + 40, R2 - 535, 72, RED, k0=1, k1=2.25, sfx="pop")
L(rect(XL, R2 + 40, 560, 260, 20), 2, 2.8, BLACK, 10, sfx="wood_high")
T("每天 1 小时", XL, R2 + 64, 72, k0=3, k1=4.0, sfx="pop")
L(join(stick(XL, R2 + 560, 0.75, "up"), face(XL, R2 + 560, 0.75, "sad")), 4, 4.9, BLACK, 9, sfx="kick")
T("至少一页", XR + 40, R2 - 535, 72, GREEN, k0=5, k1=6.0, sfx="pop")
L(book(XR, R2 + 120, 420, 280), 6, 6.8, BLACK, 9, sfx="wood_high")
T("读嗨了多读", XR, R2 + 470, 70, BLUE, k0=7, k1=8.0, sfx="ding")

scene("读一点用一点", "误区三 · 一个点", (MID, R3, ZP))
L(pair_marks(R3), 0, 0.9, BLACK, 7, sfx="wood_low")
T("一口气读完", XL + 40, R3 - 535, 72, RED, k0=1, k1=2.25, sfx="pop")
L(book_pile(XL + 80, R3 + 560, rows=4), 2, 2.9, BLACK, 8, sfx="wood_high")
L(join(stick(1010, R3 + 560, 0.5, "down"), face(1010, R3 + 560, 0.5, "flat")), 3, 3.8, BLACK, 8, sfx="pop")
T("抓一个点", XR + 40, R3 - 535, 72, GREEN, k0=4, k1=5.0, sfx="pop")
L(book(2020, R3 + 330, 300, 200), 5, 5.8, BLACK, 8, sfx="wood_high")
L(desk(2440, R3 + 520, 380), 6, 6.8, BLACK, 8, sfx="wood_low")
L(join(arrow((2080, R3 + 200), (2270, R3 + 40), -0.2, 36), sticky(2440, R3 + 20, 300, 170)), 7, 7.5, GREEN, 8,
  sfx="pop")
T("先写结论", 2440, R3 + 42, 64, BLUE, k0=7.5, k1=8.0)

scene("做出来给人看", "误区四 · 拿出来", (MID, R4, ZP))
L(pair_marks(R4), 0, 0.9, BLACK, 7, sfx="wood_low")
T("埋头苦读", XL + 40, R4 - 535, 72, RED, k0=1, k1=2.0, sfx="pop")
L(desk(XL + 150, R4 + 330, 380), 2, 2.8, BLACK, 9, sfx="wood_high")
L(join(stick(XL - 170, R4 + 560, 0.8, "point"), face(XL - 170, R4 + 560, 0.8, "flat")), 3, 3.9, BLACK, 9, sfx="pop")
T("拿出来", XR + 40, R4 - 535, 72, GREEN, k0=4, k1=4.8, sfx="pop")
L(join(stick(2030, R4 + 560, 0.8, "up"), face(2030, R4 + 560, 0.8, "smile"), sketch_card(2030, R4 - 90)), 5, 5.9,
  BLACK, 9, sfx="wood_high")
L(mini_bubbles(2470, (R4 - 160, R4 + 70, R4 + 300)), 6, 6.9, BLUE, 7, sfx="pop")
T("三条意见", 2470, R4 + 540, 66, BLUE, k0=7, k1=8.0, sfx="ding")

# ---------------------------------------------------------------- 书中观点：读书的几层、讲给外行听（场景 10–11）

scene("读书有几层", "书中观点 · 读书的几层", (MID, R5, 0.6))
L(stairs(), 0, 0.9, BLACK, 10, sfx="wood_low")
for i, s in enumerate(STEPS):
    top = STAIR_BASE - (i + 1) * STEP_H
    T(s, STAIR_X0 + (i + 0.5) * STEP_W, top - 50, 66, GREEN if i == 5 else BLACK, k0=1 + i,
      k1=1 + i + max(0.8, 0.25 * len(s)), sfx="pop")
L(join(stick(1000, STAIR_BASE, 0.7, "down"), face(1000, STAIR_BASE, 0.7, "smile")), 7, 7.8, BLUE, 9, sfx="wood_high")

CL, CR = 1000, 2600
scene("讲给外行听", "书中观点 · 费曼技巧", (CL, R6, 0.85))
L(join(stick(650, R6 + 400, 0.85, "point"), face(650, R6 + 400, 0.85, "smile")), 0, 0.9, BLUE, 10, sfx="wood_high")
L(join(grandma(1320, R6 + 400, 0.8), face(1320, R6 + 400, 0.8, "smile")), 1, 1.9, BLACK, 10, sfx="pop")
L(bubble(680, R6 - 230, 460, 170, -1), 2, 2.8, BLACK, 9, sfx="wood_low")
T("用大白话", 680, R6 - 208, 66, BLUE, k0=3, k1=4.0, sfx="pop")
L(nod(1320, R6 + 400 - 290 * 0.8, 70), 4, 4.6, BLACK, 7, sfx="shaker")
L(bubble(1340, R6 - 160, 240, 140, -1), 5, 5.7, BLACK, 8, sfx="wood_low")
T("懂了", 1340, R6 - 138, 64, GREEN, k0=6, k1=6.8, sfx="pop")
T("费曼技巧", CL, R6 - 470, 64, k0=7, k1=8.0, sfx="ding")

# ---------------------------------------------------------------- 做法：午饭讲三分钟（场景 12）

scene("这周就试", "做法 · 午饭讲三分钟", (CR, R6, 0.85))
L(table(2150, 3050, R6 + 250), 0, 0.9, BLACK, 10, sfx="wood_low")
L(join(stick(2300, R6 + 420, 0.75, "point"), stick(2900, R6 + 420, 0.75, "down"),
       bowl(2420, R6 + 240), bowl(2780, R6 + 240)), 1, 1.9, BLACK, 9, sfx="pop")
L(hourglass(2600, R6 + 100), 2, 2.8, BLACK, 8, sfx="wood_high")
T("三分钟", 2600, R6 - 70, 66, RED, k0=3, k1=3.8, sfx="pop")
T("读完一章，讲给同事", 2600, R6 - 440, 62, k0=4, k1=6.0, sfx="pop")
L(bubble(2330, R6 - 40, 200, 110, 1), 6, 6.7, BLUE, 8, sfx="wood_low")
L(check(2900, R6 + 40, 50), 7, 7.6, GREEN, 11, sfx="ding")

# ---------------------------------------------------------------- 收束（场景 13）：拉远看四对，再推到小林脑袋里的舵

OVER = (MID, 8900, 0.125)
HV = (HEAD[0], HEAD[1] + 80, 0.85)
scene("四对放一起", "回看 · 四对", OVER)
for n, R in enumerate((R1, R2, R3, R4)):
    L(check(XR + 300, R - 80, 300), n, n + 0.6, GREEN, 48, sfx="ding")
b.move(J(), 3.6, HV, dur=0.9)
hx, hy, hr = HEAD
L(join(circle(hx, hy, hr), P((hx - 80, hy + hr), (hx - 80, hy + hr + 70), (hx - 270, hy + hr + 130)),
       P((hx + 80, hy + hr), (hx + 80, hy + hr + 70), (hx + 270, hy + hr + 130))), 4, 4.9, BLACK, 9, sfx="wood_high")
FOOT = hy + 290
WHEEL = (hx + 230, hy + 150, 58)
L(join(elder(hx - 220, FOOT, 0.55), uncle(hx - 30, FOOT, 0.55)), 5, 5.6, BLACK, 7, sfx="pop")
L(baby(hx + 135, FOOT, 0.45, [(WHEEL[0] - 70, WHEEL[1] - 20), (WHEEL[0] - 70, WHEEL[1] + 20)]), 5.6, 5.95, BLUE, 7)
L(join(rudder(*WHEEL), grips(*WHEEL, range(6))), 6, 6.8, GREEN, 6, sfx="wood_low")
L(grips(*WHEEL, [6]), 7, 7.5, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 10250, 0.047)
COMMENT = (MID, CY, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
L(join(rect(MID, CY - 60, 1100, 460, 40), P((1500, CY + 180), (1440, CY + 270), (1600, CY + 180))), 5, 5.9, BLACK, 9,
  sfx="wood_high")
T("最近读的书", MID, CY - 150, 72, RED, k0=6, k1=7.25, sfx="pop")
T("你能讲出哪一句？", MID, CY - 30, 72, RED, k0=7.25, k1=9.25)
T("下一讲：道理都懂，为啥就是不动？", MID, CY + 380, 50, k0=10, k1=14, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "feedback", "反馈", "打卡一百天，怎么没变化？", ACC, b.shots,
                 [f"{BOOK}第五章 学习力——学习不是一味地努力：第二节 深度、第五节 打卡、第六节 反馈（转述）",
                  f"{BOOK}第二章第二节 感性、后记；第八章第四节 写作：谢谢你，费曼先生（转述）"],
                 "打卡一百天|怎么【没变化】", SQUARE_SHOT,
                 ["书中观点均为转述，不是逐字引文：迷恋打卡容易只追数量，用记录代替打卡，任务设下限、不设上限（第五章第五节）；"
                  "光努力是输入，成长靠反馈，要有作品意识，拿出东西换外界的反馈（第五章第六节）；读书由浅到深分几层："
                  "听书、自己读、读加摘抄、读加笔记、读加实践、实践后再讲给别人（第五章第二节）；一本书抓住最触动自己的一个点去用"
                  "（第二章第二节、后记）；费曼技巧：用自己的话讲到外行也能懂（第八章第四节，费曼只写名字）。",
                  "小林的“打卡 100 天”“30 本”、同事那句“哪本好？”、日历上的勾被风卷走、“会了啥？”空卡均为现实场景示意，"
                  "不指向任何具体公司或个人；数字均为示意，不是数据。",
                  "“会议纪要先写结论”“每天 1 小时 / 至少一页”“三条意见”、讲给奶奶听、读完一章午饭讲给同事听三分钟，"
                  "均为据书中思路整理的例子与做法示意。",
                  "脑内三兄弟（本能脑、情绪脑、理智脑宝宝）与船舵握痕为系列视觉角色，据第一章“三重大脑”与第三章“思维舵手”的比喻；"
                  "本讲舵上添第 7 道握痕。"],
                 tags="#学习方法 #读书")
    return b.attach(ep)
