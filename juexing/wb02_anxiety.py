"""02 焦虑的根源（白板手绘版）：事一多就慌，到底在慌啥？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 E 自测清单）：开局一张五格清单，观众边看边在心里打勾（待办列二十条、刷到同龄人升职就慌、收藏的课没看、
一天没结果就想换、周日晚上最慌）→ drop：十个气球往十个方向扯，“马上见效”秒表砸在中间（书中观点：想同时做很多事，
又想马上见效）→ 亮书（书旁舵写“02”）→ 两个源头（想要的比做得到的多；急着见效是天性，不用骂自己；老二情绪脑在旁边跺脚）→
揭晓（第一、三条：完成焦虑，日程塞太满；第二条：定位焦虑，跟最强的人比）→ 做法（一张纸只写三件；跟上个月的自己比；
一件事给够一个月）→ 拉远：头顶只剩三个气球，脑袋里宝宝握舵，握痕 + 1 → 评论区。
出处：周岭《认知觉醒》第一章第二节“焦虑：焦虑的根源”、第三节“耐心”（转述）；清单五条、例子与做法为示意，据书中思路整理。
"""

import math

import skia

from adler import kit as K
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, circle, clock, cross, check,
                               face, join, rect, stick, underline)
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#C9772B"
SQUARE_SHOT = 3                 # 场景 4：十个气球扯着小人，秒表砸在中间

b = Board(size=(3600, 11700))
OY = 0                          # 各行整体下移量：上一行的字不漏进下一屏页眉


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前场景写字：时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y + OY, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    if OY:
        path = skia.Path(path)
        path.offset(0, OY)
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=(view[0], view[1] + OY, view[2]), bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def rot_rect(x, y, w, h, deg) -> skia.Path:
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = [(x + dx * ca - dy * sa, y + dx * sa + dy * ca) for dx, dy in
           ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    return P(*pts, close=True)


def pen(x, y, s=1.0) -> skia.Path:
    """斜着的笔，笔尖在 (x, y)，笔身朝右上。"""
    a = math.radians(200)
    ux, uy = math.cos(a), math.sin(a)          # 笔身方向
    nx, ny = -uy, ux
    L0, w = 260 * s, 20 * s

    def pt(d, o):
        return x + ux * d + nx * o, y + uy * d + ny * o

    return join(P(pt(0, 0), pt(40 * s, -w), pt(L0, -w), pt(L0, w), pt(40 * s, w), close=True),
                P(pt(40 * s, -w), pt(40 * s, w)), P(pt(L0 - 50 * s, -w), pt(L0 - 50 * s, w)))


def stopwatch(x, y, r) -> skia.Path:
    """秒表外框 + 顶钮 + 刻度（指针另画）。"""
    return join(clock(x, y, r), rect(x, y - r - 22, r * 0.36, 34, 8), P((x, y - r), (x, y - r - 5)),
                P((x + r * 0.68, y - r * 0.72), (x + r * 0.85, y - r * 0.9)), circle(x, y, 8))


def helm(x, y, r, marks=1) -> skia.Path:
    """船舵：轮圈 + 舵毂 + 八根辐条（伸出轮圈带把手）+ 已有握痕（轮圈上的短粗道）。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.86), circle(x, y, r * 0.24)]
    for i in range(8):
        a = i / 8 * 2 * math.pi
        ca, sa = math.cos(a), math.sin(a)
        parts.append(P((x + ca * r * 0.24, y + sa * r * 0.24), (x + ca * r * 1.28, y + sa * r * 1.28)))
        parts.append(circle(x + ca * r * 1.36, y + sa * r * 1.36, r * 0.09))
    for i in range(marks):
        parts.append(grip(x, y, r, i))
    return join(*parts)


def grip(x, y, r, i) -> skia.Path:
    """第 i 道握痕：轮圈左下方的一道横向短线。"""
    a = math.radians(150 + i * 22)
    cx, cy = x + math.cos(a) * r * 0.93, y + math.sin(a) * r * 0.93
    tx, ty = -math.sin(a), math.cos(a)
    return P((cx - tx * r * 0.16 - math.cos(a) * r * 0.12, cy - ty * r * 0.16 - math.sin(a) * r * 0.12),
             (cx + tx * r * 0.16 + math.cos(a) * r * 0.12, cy + ty * r * 0.16 + math.sin(a) * r * 0.12))


def clipboard(x, y, w, h) -> skia.Path:
    return join(rect(x, y, w, h, 30), rect(x, y - h / 2, 240, 70, 16))


def boxes(x, ys, s=72) -> skia.Path:
    return join(*[rect(x, yy, s, s, 10) for yy in ys])


def todo_pile(x, y) -> skia.Path:
    """一摞待办卡片：(x, y) 为最底下一张的中心。"""
    parts = []
    for i, dx in enumerate((0, -14, 10, -8, 12, -4)):
        yy = y - i * 58
        parts += [rot_rect(x + dx, yy, 150, 52, (-3, 4, -5, 3, -4, 2)[i]), P((x + dx - 50, yy), (x + dx + 40, yy))]
    return join(*parts)


def palm(x, y, s=1.0) -> skia.Path:
    """摊开的小手（掌心朝上）：(x, y) 为掌心。"""
    pm = skia.Path()
    pm.addArc(skia.Rect.MakeXYWH(x - 45 * s, y - 30 * s, 90 * s, 70 * s), 0, 180)
    parts = [pm, P((x - 45 * s, y + 5 * s), (x + 45 * s, y + 5 * s))]
    for i, dx in enumerate((-36, -12, 12, 36)):
        parts.append(P((x + dx * s, y + 5 * s), (x + dx * 1.15 * s, y - (40 + 8 * (i % 2)) * s)))
    parts.append(P((x - 45 * s, y + 10 * s), (x - 85 * s, y - 15 * s)))
    return join(*parts)


def seesaw(cx, ground) -> skia.Path:
    """跷跷板：左低右高，(cx, ground) 为支点底边中点。"""
    l, r = (cx - 500, ground - 25), (cx + 500, ground - 275)
    return join(P((cx - 90, ground), (cx, ground - 150), (cx + 90, ground), close=True),
                P(l, r), P((l[0], l[1] + 18), (r[0], r[1] + 18)), P((cx - 650, ground), (cx + 650, ground)))


def headphones(x, y, s) -> skia.Path:
    """配合 stick 的耳机：(x, y) 为小人脚底。"""
    hy = y - 290 * s
    arc = skia.Path()
    arc.addArc(skia.Rect.MakeXYWH(x - 58 * s, hy - 62 * s, 116 * s, 116 * s), 190, 160)
    return join(arc, rect(x - 52 * s, hy + 2 * s, 22 * s, 40 * s, 8 * s), rect(x + 52 * s, hy + 2 * s, 22 * s, 40 * s, 8 * s))


def phone(x, y, w=44, h=76) -> skia.Path:
    return join(rect(x, y, w, h, 8), P((x - 8, y + h / 2 - 12), (x + 8, y + h / 2 - 12)))


def stomp(x, y, s=1.0) -> skia.Path:
    """跺脚的冲击线。"""
    return join(P((x - 70 * s, y - 10 * s), (x - 110 * s, y - 40 * s)), P((x - 60 * s, y + 10 * s), (x - 115 * s, y + 10 * s)),
                P((x + 70 * s, y - 10 * s), (x + 110 * s, y - 40 * s)), P((x + 60 * s, y + 10 * s), (x + 115 * s, y + 10 * s)))


def planner(x, y, w, h) -> skia.Path:
    """日程本：7 列 × 4 行，每格都写满。"""
    parts = [rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 70), (x + w / 2, y - h / 2 + 70))]
    for i in range(4):
        parts.append(circle(x - w * 0.3 + i * w * 0.2, y - h / 2, 14))
    cw, ch = w / 7, (h - 70) / 4
    for c in range(1, 7):
        parts.append(P((x - w / 2 + c * cw, y - h / 2 + 70), (x - w / 2 + c * cw, y + h / 2)))
    for r in range(1, 4):
        parts.append(P((x - w / 2, y - h / 2 + 70 + r * ch), (x + w / 2, y - h / 2 + 70 + r * ch)))
    for r in range(4):
        for c in range(7):
            gx, gy = x - w / 2 + c * cw, y - h / 2 + 70 + r * ch
            for q in range(3):
                parts.append(P((gx + 12, gy + 18 + q * (ch - 24) / 2.5), (gx + cw - 14 - (q % 2) * 16, gy + 18 + q * (ch - 24) / 2.5)))
    return join(*parts)


def spill(x, y, w) -> skia.Path:
    """从日程本顶上挤出来的几张纸 + 动势线。"""
    parts = []
    for dx, dy, a in ((-w * 0.32, -40, -18), (-w * 0.08, -60, 8), (w * 0.18, -45, -10), (w * 0.4, -30, 22)):
        parts.append(rot_rect(x + dx, y + dy, 110, 70, a))
    return join(*parts)


def stairs(x0, y0, n=5, dx=110, dy=55) -> skia.Path:
    pts = [(x0, y0)]
    x, y = x0, y0
    for _ in range(n):
        y -= dy
        pts.append((x, y))
        x += dx
        pts.append((x, y))
    pts.append((x, y0))
    return P(*pts, close=True)


def cloud(x, y, w=300, h=130) -> skia.Path:
    p = skia.Path()
    bumps = [(-0.38, 0.1, 0.32), (-0.15, -0.18, 0.4), (0.15, -0.2, 0.38), (0.38, 0.08, 0.3)]
    for bx, by, br in bumps:
        p.addArc(skia.Rect.MakeXYWH(x + bx * w - br * w / 2, y + by * h - br * w / 2, br * w, br * w), 160, 220)
    p.moveTo(x - w * 0.52, y + h * 0.3)
    p.lineTo(x + w * 0.52, y + h * 0.3)
    return p


def dashed(a, b_, n=9) -> skia.Path:
    (x0, y0), (x1, y1) = a, b_
    parts = []
    for i in range(n):
        f0, f1 = i / n, (i + 0.55) / n
        parts.append(P((x0 + (x1 - x0) * f0, y0 + (y1 - y0) * f0), (x0 + (x1 - x0) * f1, y0 + (y1 - y0) * f1)))
    return join(*parts)


def note(x, y, w, h) -> skia.Path:
    """便签纸：右下角折起。"""
    f = 60
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - f), (x + w / 2 - f, y + h / 2),
                  (x - w / 2, y + h / 2), close=True),
                P((x + w / 2, y + h / 2 - f), (x + w / 2 - f, y + h / 2 - f), (x + w / 2 - f, y + h / 2)))


def cabinet(x, y, w=340, h=300) -> skia.Path:
    """抽屉柜：上层抽屉拉开。(x, y) 为柜身中心。"""
    top = y - h / 2
    return join(rect(x, y, w, h, 10), P((x - w / 2, y), (x + w / 2, y)), P((x - 30, y + h / 4), (x + 30, y + h / 4)),
                P((x - w / 2 + 20, top), (x - w / 2 + 50, top - 70), (x + w / 2 - 50, top - 70), (x + w / 2 - 20, top)),
                P((x - 30, top + h / 4), (x + 30, top + h / 4)))


def calendar(x, y, w, h) -> skia.Path:
    parts = [rect(x, y, w, h, 16), P((x - w / 2, y - h / 2 + 90), (x + w / 2, y - h / 2 + 90))]
    for dx in (-w * 0.28, w * 0.28):
        parts.append(P((x + dx, y - h / 2 - 30), (x + dx, y - h / 2 + 30)))
    cw, ch = w / 7, (h - 90) / 5
    for c in range(1, 7):
        parts.append(P((x - w / 2 + c * cw, y - h / 2 + 90), (x - w / 2 + c * cw, y + h / 2)))
    for r in range(1, 5):
        parts.append(P((x - w / 2, y - h / 2 + 90 + r * ch), (x + w / 2, y - h / 2 + 90 + r * ch)))
    return join(*parts)


def cane_old(x, y, s) -> skia.Path:
    """老大“本能脑”：拄拐的老爷爷（脚底 (x, y)）。"""
    hy = y - 290 * s
    return join(stick(x, y, s, "down"), P((x - 70 * s, hy + 170 * s), (x - 85 * s, y)),
                P((x - 85 * s, hy + 170 * s), (x - 55 * s, hy + 160 * s)), face(x, y, s, "flat"))


def uncle(x, y, s) -> skia.Path:
    """老二“情绪脑”：戴耳机、攥手机的大叔。"""
    hy = y - 290 * s
    return join(stick(x, y, s, "hold"), headphones(x, y, s), phone(x + 115 * s, hy + 70 * s, 44 * s, 76 * s),
                face(x, y, s, "frown"))


def baby(x, y, s) -> skia.Path:
    """老三“理智脑”：小一号的头、戴围嘴的宝宝，手伸向右边。"""
    hy = y - 290 * s
    bib = skia.Path()
    bib.addArc(skia.Rect.MakeXYWH(x - 30 * s, hy + 30 * s, 60 * s, 60 * s), 0, 180)
    return join(stick(x, y, s, "point"), bib, face(x, y, s, "smile"))


# ---- 动态：气球、秒表

BAL_C = (2650, 1150)            # 气球放射中心（小人举起的双手之间）
BAL_R = 520
BAL_WORDS = ["健身", "英语", "副业", "考证", "理财", "读书", "早起", "写作", "跳槽", "减肥"]
BAL_COLORS = [RED, BLUE, GREEN, ORANGE]
HANDS = ((2578, 1153), (2722, 1153))


def _balloon_pos(i, T):
    a = math.radians(190 + i * (160 / 9))
    wob = math.sin(T * 2.6 + i * 1.7) * 12
    x = BAL_C[0] + math.cos(a) * BAL_R - math.sin(a) * wob
    y = BAL_C[1] + math.sin(a) * BAL_R + math.cos(a) * wob
    return a, x, y


def balloons_fn(c, k, T):
    """十个气球：绳子从双手往十个方向猛地甩出，气球鼓起，之后一直往外扯着晃。"""
    for i, word in enumerate(BAL_WORDS):
        f = ease_out(clamp01(k * 1.25 - i * 0.025))
        if f <= 0:
            continue
        a, bx, by = _balloon_pos(i, T)
        hx, hy = HANDS[0] if math.cos(a) < 0 else HANDS[1]
        ex, ey = hx + (bx - hx) * f, hy + (by - hy) * f
        s = skia.Path()
        s.moveTo(hx, hy)
        s.quadTo((hx + ex) / 2 + 25 * math.sin(T * 3 + i), (hy + ey) / 2, ex, ey + 80 * f)
        c.drawPath(s, K.paint(BLACK, 1, 5))
        g = clamp01((f - 0.6) / 0.4)
        if g <= 0:
            continue
        col = BAL_COLORS[i % 4]
        rx, ry = 75 * g, 85 * g
        o = skia.Rect.MakeXYWH(ex - rx, ey - ry, 2 * rx, 2 * ry)
        c.drawOval(o, K.paint("#FFFFFF"))
        c.drawOval(o, K.paint(col, 0.12))
        c.drawOval(o, K.paint(col, 1, 8))
        c.drawPath(P((ex - 10 * g, ey + ry + 14 * g), (ex, ey + ry), (ex + 10 * g, ey + ry + 14 * g)), K.paint(col, 1, 6))
        if g > 0.8:
            K.text(c, word, ex, ey, 54, "hand", BLACK, (g - 0.8) / 0.2)
    return None


SW = (2650, 860, 100)


def slam_fn(c, k, T):
    """“马上见效”秒表从上方砸下来，落地压扁再弹回。"""
    x, y, r = SW
    fall = clamp01(k / 0.55)
    yy = lerp(y - 700, y, fall * fall)
    sq = 1.0
    if k > 0.55:
        u = (k - 0.55) / 0.45
        sq = 1 - 0.18 * math.sin(u * math.pi) * (1 - u)
    c.save()
    c.translate(x, yy + r)
    c.scale(1 / sq, sq)
    c.translate(-x, -(yy + r))
    c.drawCircle(x, yy, r, K.paint("#FFFFFF"))
    c.drawPath(stopwatch(x, yy, r), K.paint(BLACK, 1, 8))
    c.drawPath(P((x, yy), (x + r * 0.55, yy - r * 0.45)), K.paint(RED, 1, 9))
    K.rr(c, x, yy + r + 55, 270, 74, 14, RED)
    K.text(c, "马上见效", x, yy + r + 55, 54, "hand", "#FFFFFF")
    c.restore()
    if 0.55 <= k < 0.9:
        u = (k - 0.55) / 0.35
        for d in (-1, 1):
            c.drawPath(P((x + d * (r + 20 + 60 * u), y - 20), (x + d * (r + 70 + 60 * u), y - 50)),
                       K.paint(BLACK, 1 - u, 7))
    return None


def lerp(a, b_, k):
    return a + (b_ - a) * k


def spin_fn(x, y, r, j):
    """秒表指针：本场景里一直飞快地转，场景结束后停住。"""

    def fn(c, k, T):
        t0, t1 = b.t_of(j, 1), b.t_of(j, 12)
        ang = -math.pi / 2 + (min(T, t1) - t0) * 7.0
        c.drawPath(P((x, y), (x + math.cos(ang) * r * 0.78, y + math.sin(ang) * r * 0.78)), K.paint(RED, 1, 10))
        return None

    return fn


# ---------------------------------------------------------------- 开局：自测清单（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

ROWS = [720, 870, 1020, 1170, 1320]
BX, TX = 600, 1000              # 方框、条目文字的 x

scene("对照打个勾", "自测 · 你中了几条", (900, 1000, 0.85), bars=2)
L(clipboard(900, 1000, 1000, 1050), 0, 0.9, sfx="wood_high")
T("自测清单", 900, 590, 80, k0=1, k1=2, sfx="pop")
L(boxes(BX, ROWS), 3, 3.9, BLACK, 8, sfx="wood_low")
L(pen(BX - 50, ROWS[0] + 10, 0.75), 5, 5.8, RED, 8, sfx="pop")

ITEMS = ["待办列了二十条", "同龄人升职就慌", "收藏的课没看过", "一天没结果就想换", "周日晚上最慌"]

scene("前三条", "自测 · 前三条", (950, 960, 0.92))
T(ITEMS[0], TX, ROWS[0], 56, k0=0, sfx="pop")
L(check(BX, ROWS[0], 34), 2, 2.7, RED, 10, sfx="wood_high")
T(ITEMS[1], TX, ROWS[1], 56, k0=3, sfx="pop")
L(check(BX, ROWS[1], 34), 5, 5.7, RED, 10, sfx="wood_high")
T(ITEMS[2], TX, ROWS[2], 56, k0=6, k1=7.4, sfx="pop")
L(check(BX, ROWS[2], 34), 7.4, 8.0, RED, 10)

scene("后两条", "自测 · 后两条", (950, 1000, 0.92))
T(ITEMS[3], TX, ROWS[3], 56, k0=0, sfx="pop")
L(check(BX, ROWS[3], 34), 2, 2.7, RED, 10, sfx="wood_high")
T(ITEMS[4], TX, ROWS[4], 56, k0=3, sfx="pop")
L(check(BX, ROWS[4], 34), 5, 5.7, RED, 10, sfx="wood_high")
T("勾了几个？", 900, 1450, 64, RED, k0=6, k1=7.25, sfx="ding")

# ---------------------------------------------------------------- drop：两样东西在扯你（场景 4）

scene("两样东西在扯你", "书中观点 · 焦虑从哪来", (2650, 1150, 0.75), shake=[0, (2, 18.0)], flashes=[0])
L(join(stick(2650, 1450, 0.9, "up"), face(2650, 1450, 0.9, "frown")), 0, 0.8, BLACK, 10)
b.custom(J(), 0, 0.7, balloons_fn, sfx="kick", gain=1.0)
H(1, "shaker", 0.6)
b.custom(J(), 2, 2.5, slam_fn, sfx="kick", gain=0.9)
T("想同时做很多事", 2650, 1590, 64, k0=4, sfx="pop")
T("又想马上见效", 2650, 1700, 64, RED, k0=6, sfx="pop")

# ---------------------------------------------------------------- 亮书（场景 5）

OY = 150

scene("有本书讲过", "认知觉醒 · 周岭", (2650, 2550, 0.85))
L(book(2380, 2500, 460, 320), 0, 0.9, BLACK, 10, sfx="wood_low")
T("《认知觉醒》", 2380, 2250, 80, GREEN, k0=1, k1=2.5, sfx="pop")
T("周岭 著", 2380, 2790, 60, k0=3, k1=4, sfx="pop")
L(helm(3000, 2480, 130, marks=1), 4, 4.9, GREEN, 9, sfx="wood_high")
T("02", 3000, 2760, 72, GREEN, k0=6, k1=6.8, sfx="ding")

# ---------------------------------------------------------------- 书中观点：两个源头（场景 6–7）

scene("事太多了", "书中观点 · 想要的太多", (950, 2550, 0.85))
L(seesaw(950, 2930), 0, 0.9, BLACK, 10, sfx="wood_low")
L(todo_pile(510, 2850), 1, 1.9, RED, 8, sfx="pop")
T("想要的", 510, 2465, 64, RED, k0=3, k1=3.8, sfx="pop")
L(palm(1420, 2600, 0.9), 4, 4.8, BLUE, 8, sfx="wood_high")
T("做得到的", 1380, 2460, 60, BLUE, k0=5, k1=6, sfx="pop")
L(underline(400, 620, 2508, 10, 30), 6.2, 7.0, RED, 7)

OY = 450
SWB = (720, 3600, 160)          # 场景 7 的大秒表（白板坐标另加 OY）
scene("又想马上有用", "书中观点 · 急着见效", (950, 3750, 0.85))
L(stopwatch(*SWB), 0, 0.9, BLACK, 10, sfx="wood_high")
b.custom(J(), 1, 1.3, spin_fn(SWB[0], SWB[1] + OY, SWB[2], J()), sfx="shaker", gain=0.7)
L(uncle(1250, 4050, 0.8), 2, 2.9, RED, 9, sfx="wood_low")
L(rect(1250, 3920, 80, 56, 10), 3, 3.4, RED, 6, sfx="pop")
T("55", 1250, 3920, 46, RED, k0=3.4, k1=3.9)
L(stomp(1250, 4060, 0.9), 4, 4.5, RED, 7, sfx="tom")
L(stomp(1250, 4060, 1.25), 5, 5.5, RED, 6, sfx="tom")
T("天性，不用骂自己", 950, 4230, 64, BLUE, k0=6, sfx="ding")

# ---------------------------------------------------------------- 揭晓（场景 8–9）

scene("勾一和勾三", "揭晓 · 完成焦虑", (2650, 3750, 0.85))
T("第一、三条", 2650, 3290, 72, k0=0, k1=1.25, sfx="pop")
L(planner(2650, 3650, 560, 380), 2, 2.9, BLACK, 6, sfx="wood_high")
L(spill(2650, 3460, 560), 3, 3.8, RED, 7, sfx="pop")
T("日程塞太满", 2650, 3950, 60, k0=4, k1=5.25, sfx="pop")
T("完成焦虑", 2650, 4120, 96, RED, k0=6, k1=7.2, sfx="ding")

OY = 750
scene("勾二", "揭晓 · 定位焦虑", (2650, 4950, 0.85))
L(stairs(2060, 5350), 0, 0.9, BLACK, 9, sfx="wood_low")
L(join(stick(2110, 5350, 0.55, "down"), face(2110, 5350, 0.55, "frown")), 1, 1.8, BLACK, 8, sfx="pop")
L(join(P((2720, 5350), (2960, 4850)), P((3040, 4850), (3260, 5350)), P((2640, 5350), (3285, 5350))), 2, 2.9, BLACK, 9,
  sfx="wood_high")
L(cloud(3000, 4800, 300, 130), 3, 3.8, BLUE, 8, sfx="pop")
L(dashed((2135, 5170), (2930, 4840)), 4, 4.8, RED, 6, sfx="shaker")
T("② 定位焦虑", 2650, 4480, 88, RED, k0=5, k1=6.5, sfx="ding")
T("跟最强的人比", 2650, 4600, 60, k0=6.6, k1=8.0)

# ---------------------------------------------------------------- 做法（场景 10–12）

scene("一张纸只写三件", "做法 · 示意", (950, 4950, 0.85))
L(note(720, 4850, 440, 480), 0, 0.9, BLACK, 9, sfx="wood_high")
T("① 写周报", 720, 4720, 60, k0=1, k1=2.2, sfx="pop")
T("② 回消息", 720, 4850, 60, k0=2.3, k1=3.5)
T("③ 交报销", 720, 4980, 60, k0=3.6, k1=4.8)
L(cabinet(1320, 5060), 5, 5.9, BLACK, 9, sfx="wood_low")
L(join(rot_rect(1250, 4640, 110, 66, -14), rot_rect(1380, 4620, 110, 66, 12), arrow((1320, 4700), (1320, 4830), 0, 30)),
  6, 6.8, RED, 7, sfx="pop")
T("写完再加", 950, 5330, 72, BLUE, k0=7, k1=8, sfx="ding")

OY = 1050
scene("跟上月的自己比", "做法 · 据书中思路", (950, 6150, 0.85))
L(join(P((420, 6400), (1480, 6400)), P((960, 6400), (960, 6320), (1460, 6320), (1460, 6400))), 0, 0.9, BLACK, 9,
  sfx="wood_low")
L(join(stick(700, 6400, 0.7, "down"), face(700, 6400, 0.7, "flat")), 1, 1.8, BLACK, 9, sfx="pop")
L(join(stick(1210, 6320, 0.7, "up"), face(1210, 6320, 0.7, "smile")), 2, 2.8, BLUE, 9, sfx="wood_high")
T("上个月", 700, 6480, 60, k0=3, k1=3.8, sfx="pop")
T("这个月", 1210, 6480, 60, BLUE, k0=4, k1=4.8, sfx="pop")
L(arrow((760, 5990), (1150, 5930), -0.25, 36), 5, 5.8, GREEN, 9, sfx="ding")
T("多一步就好", 950, 5790, 72, GREEN, k0=6, k1=7.25, sfx="pop")

scene("一件事给够时间", "做法 · 据书中思路", (2650, 6150, 0.85))
L(stopwatch(2250, 6080, 120), 0, 0.9, BLACK, 9, sfx="wood_high")
L(cross(2250, 6080, 110), 1, 1.8, RED, 12, sfx="rim")
L(calendar(2900, 6080, 520, 460), 2, 2.9, BLACK, 8, sfx="wood_low")
L(oval(2900, 6090, 660, 600), 4, 4.9, GREEN, 9, sfx="ding")
T("一个月后再看", 2650, 6560, 72, BLUE, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 收束：气球少了，宝宝握舵（场景 13）

OY = 1100
ME = (1500, 8150)
HB = (2150, 7550, 330)          # 脑袋剖面
scene("气球少了", "收束 · 只扯三根", (1800, 7550, 0.7))
L(join(stick(*ME, 1.0, "point"), face(*ME, 1.0, "smile"), P((1250, ME[1]), (1750, ME[1]))), 0, 0.9, BLACK, 10,
  sfx="wood_low")
HAND = (ME[0] + 120, ME[1] - 290 + 60)
L(join(*[join(P(HAND, (bx, by + 85)), oval(bx, by, 140, 170)) for bx, by in ((1430, 7330), (1600, 7220), (1770, 7330))]),
  1, 1.9, RED, 8, sfx="pop")
T("只剩三个", 1180, 7330, 60, RED, k0=2, k1=3, sfx="pop")
L(join(circle(*HB), circle(1700, 7720, 22), circle(1780, 7680, 34)), 3, 3.8, BLACK, 9, sfx="wood_high")
b.move(J(), 4, (HB[0], HB[1] + 50 + OY, 0.95), dur=1.1)
L(join(cane_old(1950, 7760, 0.6), uncle(2110, 7760, 0.6)), 4, 4.8, BLACK, 8, sfx="pop")
L(baby(2250, 7760, 0.42), 5, 5.6, BLUE, 8, sfx="pop")
L(helm(2370, 7570, 68, marks=1), 5.6, 6.4, GREEN, 8)
L(grip(2370, 7570, 68, 1), 7, 7.6, GREEN, 14, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FULL = (1800, 4300 - OY, 0.13)        # 全板（scene() 会加 OY）
CMT = (1800, 9150 + OY, 0.85)
scene("评论区聊聊", "评论区见", FULL, bars=4)
b.move(J(), 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(rect(1800, 9000, 1000, 300, 40), 5, 5.8, RED, 8, sfx="pop")
T("你勾了几个？", 1800, 9000, 80, RED, k0=6, k1=7.5, sfx="pop")
T("下一讲：学了三个月没起色，还学吗？", 1800, 9260, 50, k0=9, k1=13.25, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "anxiety", "焦虑的根源", "事一多就慌，到底在慌啥？", ACC, b.shots,
                 [f"{BOOK}第一章第二节“焦虑：焦虑的根源”、第三节“耐心：得耐心者得天下”（转述）"],
                 "事一多就慌|到底在【慌啥】", SQUARE_SHOT,
                 ["书中观点均为转述（第一章第二节）：焦虑来自想同时做很多事，又想立刻看到效果——想要的比做得到的多，又缺耐心；"
                  "急于求成是天性，不必自责（第一章第一、三节）。书中分了几种焦虑，本讲只用两种：完成焦虑（日程排太满）、"
                  "定位焦虑（拿自己跟领域里的高手比）。上屏均为转述，不是逐字引文。",
                  "五条自测清单（待办列了二十条、同龄人升职就慌、收藏的课没看过、一天没结果就想换、周日晚上最慌）"
                  "及“第一、三条 = 完成焦虑，第二条 = 定位焦虑”的对应为示意，不是书中量表；第三条的对应据书中思路整理。",
                  "十个气球及上面的词、“马上见效”秒表、跷跷板、日程本、台阶与云里的山、便签上的三件事均为示意，不是数据，"
                  "不指向任何具体公司或个人。",
                  "三条做法（一张纸只写三件、写完再加；跟上个月的自己比；一件事给够一个月再看结果）为据书中思路整理的建议。",
                  "系列角色：脑内三兄弟（老大本能脑、老二情绪脑、宝宝理智脑）与船舵据第一章“三重大脑”、第三章“思维舵手”的"
                  "比喻画成，年龄牌“55”为书中比喻的转述；作者周岭只写名字，不画肖像。"],
                 tags="#焦虑 #职场")
    return b.attach(ep)
