"""07 收工仪式（白板手绘版）：下班了，脑子怎么还在上班？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（G 倒叙，先给结局）：周一早上小周顶着黑眼圈、方案一个字没有（结局）→ 时间轴从右往左倒回：周日夜里躺床上
想方案、床头小红点一直叮 → 周五下班电脑没关、清单空着，一团线头跟着回家（找到原因：没收尾）→
drop：一枚“停工完毕”印章砸在周五的清单上，线头剪断，床头的小红点被吹灭，小周睡着 →
书中观点（亮书；停工仪式；没写下计划的事会一直缠着你，写进本子就松开；放空时脑子在后台想难题；注意力要充电；
一天能专注的额度有限，夜里加班不值）→ 正着讲做法（扫一眼待办和邮箱 / 写好明天第一件事 / 说一声收工，之后不碰）→
时间轴正着走回周一：黑眼圈擦掉，方案打勾 → 拉远看全板，推到评论区。
小红点这一讲：半夜在床头一直叮，drop 时被吹灭。
书中观点为转述：卡尔·纽波特《深度工作》第二部分准则1“工作要深入”中“图安逸”一节（下班彻底停工、无意识思考、
注意力恢复、每天专注时长有限、停工仪式、蔡格尼克效应及后续研究）；中译本宋伟译，江西人民出版社·后浪 2017。
周一黑眼圈、周日夜里、线头、电池与额度格子为示意；三步收工流程为据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, cross,
                               desk, face, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#5B4FA8"                 # 本讲主色：夜里的紫
SQUARE_SHOT = 3                 # 场景 4：印章砸在清单上、线头剪断、床头小红点吹灭（小周 + 核心示意）

b = Board(size=(3600, 8600))
GREY = "#55555E"


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = J() if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


# ---------------------------------------------------------------- 本讲画法

def quad(p0, c, p1) -> skia.Path:
    p = skia.Path()
    p.moveTo(*p0)
    p.quadTo(*c, *p1)
    return p


def tangle(p0, c, p1, n=7, amp=32) -> skia.Path:
    """沿一条二次曲线打一串小圈的线团（线头）。"""
    p = skia.Path()
    steps = n * 24
    for i in range(steps + 1):
        u = i / steps
        x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u ** 2 * p1[0]
        y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u ** 2 * p1[1]
        a = u * n * 2 * math.pi
        x += amp * math.sin(a) * math.sin(math.pi * u) ** 0.4
        y += amp * (1 - math.cos(a)) * 0.6 * math.sin(math.pi * u) ** 0.4
        (p.moveTo if i == 0 else p.lineTo)(x, y)
    return p


def head_loops(x, y, r=150, n=5) -> skia.Path:
    """缠着脑袋的一圈圈乱线。"""
    p = skia.Path()
    steps = n * 40
    for i in range(steps + 1):
        u = i / steps
        a = u * n * 2 * math.pi
        rr = r * (1 + 0.12 * math.sin(a * 2.3 + 1)) + 10 * math.sin(a * 5)
        px, py = x + rr * math.cos(a) * 1.05, y + rr * math.sin(a) * 0.62 + 40 * math.sin(a * 0.7)
        (p.moveTo if i == 0 else p.lineTo)(px, py)
    return p


def checklist(x, y, w, h, n=3) -> skia.Path:
    """清单：外框 + n 行（小方框 + 横线）。"""
    parts = [rect(x, y, w, h, 14)]
    top, step = y - h / 2 + h / (n + 1) * 0.75, h / (n + 0.5)
    for i in range(n):
        yy = top + i * step + step * 0.35
        bx = x - w / 2 + w * 0.2
        parts += [rect(bx, yy, w * 0.14, w * 0.14, 4), P((bx + w * 0.14, yy), (x + w / 2 - w * 0.12, yy))]
    return join(*parts)


def row_box(x, y, w, h, n, i):
    """checklist 第 i 行小方框的中心。"""
    top, step = y - h / 2 + h / (n + 1) * 0.75, h / (n + 0.5)
    return x - w / 2 + w * 0.2, top + i * step + step * 0.35


def scissors(x, y, s=1.0) -> skia.Path:
    return join(circle(x - 40 * s, y + 45 * s, 22 * s), circle(x + 40 * s, y + 45 * s, 22 * s),
                P((x - 28 * s, y + 28 * s), (x + 30 * s, y - 60 * s)), P((x + 28 * s, y + 28 * s), (x - 30 * s, y - 60 * s)))


def wind(x, y, w=110) -> skia.Path:
    parts = []
    for dy, ww in ((-40, w), (0, w * 1.2), (40, w * 0.85)):
        p = skia.Path()
        p.moveTo(x - ww, y + dy)
        p.quadTo(x - ww * 0.4, y + dy - 18, x, y + dy)
        p.quadTo(x + 22, y + dy + 2, x + 10, y + dy - 22)
        parts.append(p)
    return join(*parts)


def smoke(x, y, h=150) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y)
    p.cubicTo(x - 40, y - h * 0.3, x + 40, y - h * 0.55, x, y - h * 0.75)
    p.cubicTo(x - 30, y - h * 0.9, x + 20, y - h, x + 5, y - h * 1.05)
    return p


def bed(x0, x1, top) -> skia.Path:
    """床：左侧床头 + 床垫 + 床腿，top 为床垫上沿。"""
    return join(P((x0, top - 190), (x0, top + 140)), P((x0, top), (x1, top), (x1, top + 60), (x0, top + 60)),
                P((x1 - 10, top + 60), (x1 - 10, top + 140)), rect(x0 + 80, top - 25, 130, 50, 20))


def blanket(x0, x1, top) -> skia.Path:
    p = skia.Path()
    p.moveTo(x0, top)
    p.cubicTo(x0 + 120, top - 110, x1 - 200, top - 90, x1, top)
    return p


def table(x, top, w=170) -> skia.Path:
    return join(P((x - w / 2, top), (x + w / 2, top)), P((x - w / 2 + 20, top), (x - w / 2 + 20, top + 110)),
                P((x + w / 2 - 20, top), (x + w / 2 - 20, top + 110)))


def bust(x, y, r=120) -> skia.Path:
    """半身像：大脑袋 + 肩膀。(x, y) 为脑袋中心。"""
    sh = skia.Path()
    sh.moveTo(x - 190, y + r + 270)
    sh.quadTo(x - 170, y + r + 70, x, y + r + 60)
    sh.quadTo(x + 170, y + r + 70, x + 190, y + r + 270)
    return join(circle(x, y, r), P((x - 25, y + r), (x - 25, y + r + 60)), P((x + 25, y + r), (x + 25, y + r + 60)), sh)


def eyes_mouth(x, y, r=120, mood="flat") -> skia.Path:
    p = join(circle(x - r * 0.35, y - r * 0.1, 7), circle(x + r * 0.35, y - r * 0.1, 7))
    if mood == "smile":
        p.addArc(skia.Rect.MakeXYWH(x - r * 0.3, y + r * 0.05, r * 0.6, r * 0.45), 20, 140)
    else:
        p.moveTo(x - r * 0.25, y + r * 0.4)
        p.lineTo(x + r * 0.25, y + r * 0.4)
    return p


def notebook(x, y, w=300, h=360) -> skia.Path:
    parts = [rect(x, y, w, h, 16)]
    for i in range(4):
        parts.append(circle(x - w / 2 + 50 + i * (w - 100) / 3, y - h / 2, 14))
    return join(*parts)


def tree(x, ground, s=1.0) -> skia.Path:
    crown = []
    cy = ground - 360 * s
    for i in range(40):
        a = i / 40 * 2 * math.pi
        rr = 150 * s * (1 + 0.1 * math.sin(a * 7))
        crown.append((x + rr * math.cos(a), cy + rr * math.sin(a) * 0.85))
    return join(P((x - 20 * s, ground), (x - 12 * s, cy + 110 * s)), P((x + 20 * s, ground), (x + 12 * s, cy + 110 * s)),
                P(*crown, close=True))


def bulb(x, y, r=40) -> skia.Path:
    parts = [circle(x, y, r), P((x - r * 0.45, y + r * 0.9), (x + r * 0.45, y + r * 0.9)),
             P((x - r * 0.35, y + r * 1.2), (x + r * 0.35, y + r * 1.2))]
    for a in (-150, -120, -90, -60, -30):
        t = math.radians(a)
        parts.append(P((x + math.cos(t) * r * 1.35, y + math.sin(t) * r * 1.35),
                       (x + math.cos(t) * r * 1.8, y + math.sin(t) * r * 1.8)))
    return join(*parts)


def sun(x, y, r=45) -> skia.Path:
    parts = [circle(x, y, r)]
    for i in range(8):
        t = i / 8 * 2 * math.pi
        parts.append(P((x + math.cos(t) * r * 1.35, y + math.sin(t) * r * 1.35),
                       (x + math.cos(t) * r * 1.8, y + math.sin(t) * r * 1.8)))
    return join(*parts)


def moon(x, y, r=55) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def envelope(x, y, w=200, h=140) -> skia.Path:
    return join(rect(x, y, w, h, 10), P((x - w / 2 + 6, y - h / 2 + 8), (x, y + 10), (x + w / 2 - 6, y - h / 2 + 8)))


def gear_path(x, y, r, teeth=8, rot=0.0) -> skia.Path:
    pts = []
    for i in range(teeth * 4):
        a = rot + i / (teeth * 4) * 2 * math.pi
        rr = r * (1.22 if (i % 4) in (1, 2) else 1.0)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return join(P(*pts, close=True), circle(x, y, r * 0.35))


# ---------------------------------------------------------------- 动态项（custom）

J_DROP = 3                       # 场景 4（从 0 数）：drop


def reddot_fn(x, y, r=55, n="9"):
    """小红点：红色实心圆 + 白字数字 + 两条小腿，一直“叮”；drop 场景第 3 拍被吹灭（缩没）。"""

    def fn(c, k, t):
        tb = b.t_of(J_DROP, 3)
        s = ease_out(k) * (1 - clamp01((t - tb) / 0.3))
        if s <= 0:
            return None
        for dx in (-1, 1):
            K.seg(c, x + dx * r * 0.3, y + r * 0.8, x + dx * r * 0.45, y + r * 1.8, BLACK, 7)
            K.seg(c, x + dx * r * 0.45, y + r * 1.8, x + dx * r * 0.75, y + r * 1.8, BLACK, 7)
        K.dot(c, x, y, r * s, RED)
        K.text(c, n, x, y + 4 * s, 74 * s, "hand", "#FFFFFF")
        if k >= 1:
            a = 0.35 + 0.65 * abs(math.sin(t * 5.0))
            for i, rr in enumerate((r * 1.5, r * 2.0)):
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(x - rr, y - rr, 2 * rr, 2 * rr), -50, 100)
                c.drawPath(arc, K.paint(RED, a * s * (1 - 0.3 * i), 6))
            K.text(c, "叮！", x + 10, y - r - 75, 66, "hand", RED, s)
        return (x + r, y) if k < 1 else None

    return fn


def thread_fn(path, cut_j, cut_k, color=GREY, width=7):
    """线团：按进度描出；到 (cut_j, cut_k) 被剪断后 0.5 秒内淡掉。"""

    def fn(c, k, t):
        tc = b.t_of(cut_j, cut_k)
        a = 1 - clamp01((t - tc) / 0.5)
        if a <= 0:
            return None
        part, tip = wb.partial(path, k)
        c.drawPath(part, wb.marker(color, width, a))
        return tip

    return fn


def stamp_fn(x, y, w=330, h=130, rot=-9):
    """“停工完毕”印章：从上方放大落下，第 0 拍砸实，再扩散一圈墨印。"""

    def fn(c, k, t):
        sc = lerp(2.3, 1.0, k * k)
        with K.at(c, x, y - 260 * (1 - k * k), rot, sc):
            K.rr(c, 0, 0, w, h, 18, "#FFFFFF", 0.55 * k)
            K.rr_stroke(c, 0, 0, w, h, 18, RED, 12, k)
            K.rr_stroke(c, 0, 0, w - 34, h - 34, 10, RED, 4, k)
            K.text(c, "停工完毕", 0, 2, 72, "hand", RED, k)
        if k >= 1:
            dt = t - b.t_of(J_DROP, 0)
            if 0 <= dt < 0.5:
                f = dt / 0.5
                c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 80 * f, y - h / 2 - 50 * f, w + 160 * f, h + 100 * f),
                                30, 30, K.paint(RED, 0.5 * (1 - f), 8))
        return None

    return fn


def lying_eyes_fn(x, y):
    """躺着的小周：睁眼（瞪着天花板）；drop 场景第 5 拍闭眼。"""

    def fn(c, k, t):
        if t < b.t_of(J_DROP, 5):
            K.dot(c, x - 14, y - 6, 6, BLACK, k)
            K.dot(c, x + 14, y - 6, 6, BLACK, k)
            K.seg(c, x - 24, y - 26, x - 6, y - 20, BLACK, 5, k)
            K.seg(c, x + 24, y - 26, x + 6, y - 20, BLACK, 5, k)
        else:
            for dx in (-14, 14):
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(x + dx - 10, y - 14, 20, 14), 10, 160)
                c.drawPath(arc, wb.marker(BLACK, 5))
        return None

    return fn


def gear_fn(x, y, r, speed, color=BLACK):
    def fn(c, k, t):
        rot = t * speed
        with K.at(c, x, y, 0, max(0.01, ease_out(k))):
            c.drawPath(gear_path(0, 0, r, 8, rot), wb.marker(color, 7))
        return (x + r, y) if k < 1 else None

    return fn


def battery_fn(j, x, y, w, h):
    """电池电量：第 2–4 拍上班耗光，第 6–7.5 拍散步看树回升。"""

    def fn(c, k, t):
        t2, t4, t6, t75 = (b.t_of(j, kk) for kk in (2, 4, 6, 7.5))
        if t < t4:
            lv = lerp(0.95, 0.08, ease_in_out(clamp01((t - t2) / (t4 - t2))))
        elif t < t6:
            lv = 0.08
        else:
            lv = lerp(0.08, 0.75, ease_in_out(clamp01((t - t6) / (t75 - t6))))
        col = K.mix(RED, GREEN, clamp01((lv - 0.15) / 0.35))
        iw, ih = (w - 44) * lv, h - 44
        K.rr(c, x - (w - 44) / 2 + iw / 2, y, iw, ih, 12, col, 0.85)
        return None

    return fn


def quota_fn(j, x0, y, cw, ch, n=6):
    """专注额度格子：第 3 拍全部填满，第 4–6 拍从左到右一格格用掉。"""

    def fn(c, k, t):
        t4, t6 = b.t_of(j, 4), b.t_of(j, 6)
        for i in range(n):
            te = t4 + (t6 - t4) * i / n
            a = k * (1 - clamp01((t - te) / 0.25))
            if a > 0:
                K.rr(c, x0 + cw * (i + 0.5), y, cw - 26, ch - 26, 8, BLUE, 0.8 * a)
        return None

    return fn


def lid_fn(j, hx, hy, ln=210):
    """笔记本屏幕：先画成打开（亮着），第 3 拍合上。"""

    def fn(c, k, t):
        t0, t3 = b.t_of(j, 2.3), b.t_of(j, 3)
        grow = clamp01((t - t0) / max(1e-3, t3 - t0 - 0.05))
        close = ease_in_out(clamp01((t - t3) / 0.3))
        ang = math.radians(lerp(-100, -2, close))
        ex, ey = hx + math.cos(ang) * ln * grow, hy + math.sin(ang) * ln * grow
        if close < 1:
            mx, my = hx + math.cos(ang) * ln * 0.55, hy + math.sin(ang) * ln * 0.55
            K.dot(c, mx + 40, my, 55 * grow, BLUE, 0.25 * (1 - close))
        c.drawLine(hx, hy, ex, ey, wb.marker(BLACK, 14))
        return (ex, ey) if grow < 1 else None

    return fn


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 结局先行：周一早上（场景 1）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。
# 第一排（y≈1000）是一条从右往左倒着走的时间轴：周一（右）← 周日夜里（中）← 周五下班（左）。

MON = (2620, 1420)              # 周一小周脚底
DOC = (3080, 870)               # 墙上的方案
scene("周一崩了", "先看结局", (2950, 1000, 0.85), bars=2)
L(stick(*MON, 1.0), 0, 0.8, sfx="wood_high")
L(face(*MON, 1.0, "flat"), 0.8, 1.0)
L(join(circle(MON[0] - 16, MON[1] - 298, 15), circle(MON[0] + 16, MON[1] - 298, 15)), 1, 1.7, GREY, 9, sfx="rim")
L(join(desk(3080, 1180, 440), rect(*DOC, 340, 240, 16)), 2, 2.9, sfx="wood_low")
T("方案", DOC[0], DOC[1] - 70, 60, k0=3, sfx="pop")
T("空白", DOC[0], DOC[1] + 50, 72, RED, k0=4, sfx="rim")
T("周一早上", 2950, 530, 64, k0=5, sfx="pop")

# ---------------------------------------------------------------- 倒回去：周日夜里、周五下班（场景 2–3）

DOT = (1400, 1070)              # 床头的小红点
scene("倒回周日夜里", "倒回去 · 周日", (1800, 1000, 0.85))
L(arrow((2380, 610), (1260, 610), 0.0, 40), 0, 0.9, BLACK, 8, sfx="wood_low")
T("倒回", 1340, 530, 56, k0=1, sfx="pop")
T("周日夜里", 1880, 530, 64, k0=2, sfx="pop")
L(bed(1560, 2150, 1160), 3, 3.9, sfx="wood_high")
L(join(circle(1650, 1085, 42), blanket(1700, 2140, 1160)), 4, 4.8, BLACK, 9, sfx="wood_low")
C(4.8, 5.0, lying_eyes_fn(1650, 1085))
L(bubble(1960, 860, 380, 120, -1), 5, 5.6, BLACK, 8, sfx="pop")
T("方案咋写", 1960, 860, 54, k0=5.6)
L(table(DOT[0], 1180), 6, 6.6, sfx="wood_high")
C(7, 7.5, reddot_fn(*DOT), sfx="ding")
H(8, "ding", 0.6)

PC = (880, 1120)                # 周五桌上的电脑屏
LIST = (700, 1060, 170, 230)    # 周五的清单（x, y, w, h）
WALK = (330, 1420)              # 周五离开的小周脚底
TH = ((900, 1070), (650, 560), (355, 1140))
scene("线头带回家", "倒回去 · 周五", (650, 1000, 0.85))
L(arrow((1180, 610), (220, 610), 0.0, 40), 0, 0.9, BLACK, 8, sfx="wood_low")
T("周五下班", 700, 530, 64, k0=1, sfx="pop")
L(desk(840, 1180, 420), 2, 2.9, sfx="wood_high")
L(checklist(*LIST, 3), 3, 3.9, BLACK, 7, sfx="pop")
L(join(P((960, 1100), (1005, 1092)), P((955, 1068), (992, 1035)), P((960, 1135), (1005, 1142))), 4, 4.5, BLUE, 7,
  sfx="rim")
T("没关", 1010, 975, 58, RED, k0=4.5, k1=5.3)
L(stick(*WALK, 0.85), 6, 6.8, sfx="wood_high")
L(face(*WALK, 0.85, "sad"), 6.8, 7.0)
C(7, 8, thread_fn(tangle(*TH, n=7, amp=30), J_DROP, 1.6), sfx="shaker")

# ---------------------------------------------------------------- drop（场景 4）：停工完毕

scene("停工完毕", "停工完毕", (1200, 950, 0.56), shake=[0], flashes=[0])
assert J() == J_DROP
C(-0.25, 0, stamp_fn(LIST[0], LIST[1]))
H(0, "kick", 1.0)
L(scissors(502, 924, 1.0), 1, 1.6, RED, 9, sfx="rim")
L(wind(DOT[0] - 110, DOT[1] - 10, 110), 2, 2.8, BLUE, 8, sfx="shaker")
H(3, "tom")
L(smoke(DOT[0], DOT[1] + 30, 170), 4, 4.8, GREY, 7, sfx="wood_low")
T("Zzz", 1760, 950, 90, BLUE, k0=5, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 5–9）

scene("书里有个仪式", "深度工作 · 书中观点", (1100, 3300, 0.85))
L(book(900, 3330, 440, 300), 0, 0.9, sfx="wood_low")
T("深度工作", 900, 3110, 76, GREEN, k0=1, sfx="pop")
T("卡尔 · 纽波特", 900, 3570, 50, k0=3, k1=4.5, sfx="pop")
L(rect(1430, 3300, 340, 120, 14), 5, 5.8, RED, 10, sfx="wood_high")
T("停工完毕", 1430, 3300, 64, RED, k0=6, sfx="pop")
T("停工仪式", 1100, 3720, 90, RED, k0=7, sfx="ding")

HD = (2300, 3200)               # 半身像脑袋中心
scene("写下来就松", "书中观点 · 写下来", (2500, 3300, 0.85))
L(bust(*HD, 120), 0, 0.9, sfx="wood_high")
L(eyes_mouth(*HD, 120, "flat"), 0.9, 1.0, BLACK, 8)
C(1, 2, thread_fn(head_loops(*HD, 170, 5), J() , 7.6, GREY, 6), sfx="shaker")
T("没做完的事", 2300, 2930, 56, k0=2, sfx="pop")
L(arrow((2490, 3110), (2630, 3170), -0.2, 34), 4, 4.8, GREEN, 8, sfx="wood_low")
L(notebook(2800, 3260, 300, 360), 5, 5.9, sfx="wood_high")
T("计划", 2800, 3200, 66, GREEN, k0=6, sfx="pop")
L(scissors(2470, 3030, 0.8), 7, 7.5, RED, 8, sfx="rim")
L(eyes_mouth(HD[0], HD[1], 120, "smile"), 7.5, 7.9, BLUE, 8)

ME7 = (480, 5230)
scene("放空也在想", "书中观点 · 放空", (650, 4800, 0.85))
L(quad((200, 5250), (650, 5300), (1120, 5170)), 0, 0.9, BLACK, 8, sfx="wood_low")
L(tree(950, 5160, 1.0), 1, 1.9, GREEN, 9, sfx="wood_high")
L(stick(*ME7, 0.8, "down"), 2, 2.8, sfx="pop")
L(face(*ME7, 0.8, "smile"), 2.8, 3.0)
C(3, 3.6, gear_fn(430, 4770, 62, 1.6), sfx="tom")
C(4, 4.6, gear_fn(548, 4690, 44, -2.3, BLUE), sfx="wood_high")
T("后台在想难题", 650, 4470, 60, k0=5, sfx="pop")
L(bulb(700, 4640, 38), 7, 7.8, ORANGE, 8, sfx="ding")

BAT = (1800, 4650, 620, 280)
scene("注意力要充电", "书中观点 · 充电", (1800, 4800, 0.85))
L(join(rect(*BAT, 30), rect(BAT[0] + BAT[2] / 2 + 22, BAT[1], 40, 110, 8)), 0, 0.9, sfx="wood_high")
T("上班一天", 1800, 4400, 64, k0=1, sfx="pop")
C(2, 2.5, battery_fn(J(), *BAT), sfx="shaker")
L(tree(1560, 5180, 0.6), 4, 4.8, GREEN, 8, sfx="wood_high")
L(stick(1760, 5190, 0.6, "down"), 5, 5.8, sfx="pop")
L(face(1760, 5190, 0.6, "smile"), 5.8, 6.0)
H(6, "ding")
T("散步看树", 2060, 5060, 60, GREEN, k0=7, sfx="pop")

CX0, CY, CW, CH = 2560, 4650, 130, 160
scene("晚上没电了", "书中观点 · 额度", (2950, 4800, 0.85))
T("专注额度", 2950, 4400, 64, k0=0, sfx="pop")
L(join(*[rect(CX0 + CW * (i + 0.5), CY, CW, CH, 6) for i in range(6)]), 1, 1.9, sfx="wood_high")
L(sun(2625, 4930, 42), 2, 2.8, ORANGE, 8, sfx="wood_low")
C(3, 3.5, quota_fn(J(), CX0, CY, CW, CH), sfx="pop")
H(4, "tom")
H(5, "tom", 0.7)
L(moon(3275, 4930, 52), 6, 6.8, BLUE, 8, sfx="wood_low")
T("没电了", 3275, 5100, 72, RED, k0=7, sfx="rim")

# ---------------------------------------------------------------- 做法（场景 10–12），从右往左

CL = (2780, 6300, 520, 560)
scene("扫一眼待办", "第一步 · 扫待办", (2950, 6300, 0.85))
T("① 扫一眼待办", 2950, 5880, 72, BLUE, k0=0, sfx="pop")
L(checklist(*CL, 3), 2, 2.9, sfx="wood_high")
for n in range(2):
    bx, by = row_box(*CL, 3, n)
    L(check(bx, by, 44), 3 + n, 3.5 + n, GREEN, 10, sfx="pop")
bx, by = row_box(*CL, 3, 2)
T("明天", bx + 170, by - 2, 56, BLUE, k0=5, sfx="pop")
L(envelope(3270, 6200), 6, 6.8, sfx="wood_low")
T("都有着落", 2950, 6690, 64, GREEN, k0=7, sfx="ding")

scene("写好明天", "第二步 · 写明天", (1800, 6300, 0.85))
T("② 写好明天", 1800, 5880, 72, BLUE, k0=0, sfx="pop")
L(join(rect(1800, 6280, 560, 460, 10), P((2020, 6510), (2080, 6450))), 2, 2.9, ORANGE, 9, sfx="wood_high")
T("明天先写", 1800, 6200, 64, k0=3, sfx="pop")
T("方案第二节", 1800, 6330, 64, k0=4, sfx="pop")
L(circle(1800, 6070, 22), 6, 6.4, RED, 10, sfx="rim")
L(underline(1640, 1960, 6390, 10, 32), 7, 7.8, RED, 7, sfx="ding")

ME12 = (400, 6560)
scene("说声收工", "第三步 · 说收工", (650, 6300, 0.85))
T("③ 说声收工", 650, 5880, 72, BLUE, k0=0, sfx="pop")
L(join(table(800, 6390, 460), P((720, 6378), (950, 6378))), 2, 2.8, BLACK, 10, sfx="wood_high")
C(2.3, 3.6, lid_fn(J(), 724, 6372))
H(3, "rim")
L(stick(*ME12, 0.8, "down"), 4, 4.8, sfx="pop")
L(face(*ME12, 0.8, "smile"), 4.8, 5.0)
L(bubble(430, 6090, 300, 120, -1), 5, 5.6, BLACK, 8, sfx="wood_low")
T("收工！", 430, 6090, 60, k0=5.6)
L(rect(1100, 6310, 80, 130, 12), 6, 6.5, BLACK, 8, sfx="pop")
L(cross(1100, 6310, 60), 7, 7.6, RED, 10, sfx="rim")

# ---------------------------------------------------------------- 正着走回周一（场景 13）

scene("周一好多了", "回到周一", (2350, 1000, 0.56))
H(0, "shaker", 0.6)
L(arrow((1450, 685), (3250, 685), 0.0, 46), 1, 2.0, GREEN, 10, sfx="wood_high")
b.move(J(), 3, (2950, 1000, 0.85))
HX, HY = MON[0], MON[1] - 290
b.erase(J(), 3, 3.5, HX, HY, 120, 120)
b.erase(J(), 3.5, 3.9, DOC[0], DOC[1] + 50, 260, 110)
H(3, "rim")
L(join(circle(HX, HY, 45), face(*MON, 1.0, "smile")), 4, 4.8, BLACK, 10, sfx="pop")
L(join(*[P((DOC[0] - 110, DOC[1] + 10 + i * 45), (DOC[0] + 60 - i * 30, DOC[1] + 10 + i * 45)) for i in range(3)]), 5, 5.8,
  BLACK, 7, sfx="wood_low")
L(check(DOC[0] + 120, DOC[1] + 50, 50), 6, 6.8, GREEN, 12, sfx="ding")
T("精神好", HX, 960, 64, GREEN, k0=7, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：拉远看全板 → 推到评论区

FULL = (1800, 3560, 0.22)
scene("评论区聊聊", "评论区见", FULL, bars=4)
H(0, "cymbal", 0.5)
H(2, "ding")
b.move(J(), 4, (1800, 7800, 0.8))
H(4, "wood_high", 0.6)
T("你下班后最常想起啥活？", 1800, 7700, 70, RED, k0=6, sfx="pop")
T("下一讲：排队两分钟，也要掏手机？", 1800, 7880, 50, k0=10, sfx="wood_high")
L(P((1400, 7935), (2200, 7935)), 14, 14.8, BLACK, 6)
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "shutdown", "收工仪式", "下班了，脑子怎么还在上班？", ACC, b.shots,
                 [f"{BOOK}第二部分 准则1“工作要深入”·“图安逸”一节（停工仪式、无意识思考、注意力恢复、"
                  "每天专注时长有限、蔡格尼克效应及后续研究；转述）",
                  "中译本：《深度工作：如何有效使用每一点脑力》，宋伟译，江西人民出版社·后浪 2017"],
                 "下班了|脑子还在【上班】", SQUARE_SHOT,
                 ["书中观点均为转述（准则1“工作要深入”中“图安逸”一节）：下班就彻底停下工作；放空时的无意识思考能帮人想难题；"
                  "注意力用久了要靠休息恢复（书中引注意力恢复理论，例如到自然环境里散步）；一天能高强度专注的时间有限，"
                  "晚上加的那点班价值不大；书中建议每天收工时走一遍“停工仪式”——检查每件没做完的事、给它定好计划，"
                  "最后说一句固定的结束语；没做完的事一旦写下计划，脑子就不再一直惦记它（书中引蔡格尼克效应及后续研究）。"
                  "上屏均为转述，不是逐字引文；“停工完毕”为画面上的印章字样，具体措辞以中译本为准。",
                  "每天专注时长的具体数字未上屏（未核实中译本措辞）。",
                  "周一早上的黑眼圈、周日夜里躺床上想方案、周五下班电脑没关、跟着回家的线头、床头小红点、"
                  "电池电量、专注额度格子均为示意，不是数据；“方案第二节”为示意。",
                  "三步收工流程（扫一眼待办和邮箱、写好明天第一件事、说一声收工之后不碰）为据书中“停工仪式”思路整理的做法。"],
                 tags="#下班")
    return b.attach(ep)
