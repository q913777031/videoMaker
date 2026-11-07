"""《丰田模式》02 拉动：活儿越做越多，为什么反而越乱？（白板手绘 + AI 旁白，竖屏 2:3）

比喻贯穿：超市货架。顾客拿走一瓶，后面那排滑上来，店员从后面补一瓶（拉动）；对照“把仓库堆满”（过量生产）；
说回职场时，小李提前做的方案、周报、表格都是“堆起来的货”。
- 0–3 秒：系列开场“丰田模式”四字（与第 01 讲相同），缓推到小李和越摞越高的文件；
- drop：第 2 屏“最大浪费”红印章砸在堆满的仓库上（重击 + 震屏 + 闪白）；
- 车间：后工序员工拿着看板来取货，前工序只补被取走的那一件；
- 职场三例 → 共情 → 三步做法 → 准点走 → 评论区 + 下一讲预告。
文案见 fengtian/PLAN.md「### 02 拉动」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, draw_ohno, draw_worker,
                             pop_scale, rest_hands, shoulder, walk, wobble)
from whiteboard import engine as wb
from whiteboard.engine import P, arrow, book, check, circle, cross, doc, join, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "丰田模式 · 书中做法", 2),
    ([3, 4], "丰田模式 · 书中做法", 3),
    ([5, 6], "丰田模式 · 书中做法", 4),
    ([7, 8], "丰田模式 · 书中做法", 5),
    ([9], "书中观点", 6),
    ([10, 11], "为什么不提前做", 7),
    ([12, 13], "为什么不提前做", 8),
    ([14, 15], "说回我们自己", 9),
    ([16], "说回我们自己", 10),
    ([17], "说回我们自己", 11),
    ([18, 19], "说回我们自己", 12),
    ([20, 21], "说回我们自己", 13),
    ([22], "做法一 · 示意", 14),
    ([23], "做法二 · 示意", 15),
    ([24], "做法三 · 示意", 16),
    ([25], "准点下班", 17),
    ([26, 27, 28, 29], "评论区见", 18),
]

THEME = FT.get("02")          # 本讲样式（fengtian/theme.py）：浅灰蓝点阵、开场 pile、转场 pan
L = C.Lesson("02", SCREENS, drop_screen=2, board_size=(5000, 13000), extra_hold={11: 0.3, 13: 0.8, 17: 0.4}, theme=THEME)
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

# 各屏在白板上的区块中心（相邻屏相距 1600，蛇形排列，切屏平移距离短）
R = [(2600, 800), (900, 900), (900, 2500), (2500, 2500), (4100, 2500), (4100, 4100), (2500, 4100), (900, 4100),
     (900, 5700), (2500, 5700), (4100, 5700), (4100, 7300), (2500, 7300), (900, 7300), (900, 8900), (2500, 8900),
     (4100, 8900), (4100, 10500), (2500, 10500)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 3——使用拉动式生产方式以避免生产过剩（Use \"Pull\" Systems to Avoid Overproduction）；"
    "书中把过量生产列为七种浪费里最严重的一种；大野耐一从美国超市补货得到启发，看板是后工序向前工序取货的凭证。",
    "超市货架画成牛奶冷柜的侧视图（前面拿、后面补）为示意；小李、小王、领导为虚构人物，“三版”“五页”“21:00”为示意。",
]


# ================================================================ 道具

def bottle(c, x, yb, s=1.0, alpha=1.0):
    """牛奶瓶：(x, yb) 为瓶底中点，高约 120·s。"""
    w, h = 64 * s, 86 * s
    body = skia.Rect.MakeXYWH(x - w / 2, yb - h, w, h)
    c.drawRoundRect(body, 14 * s, 14 * s, K.paint("#FFFFFF", alpha))
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 3, yb - h * 0.62, w - 6, h * 0.3), K.paint("#BFD5F2", alpha))
    c.drawRoundRect(body, 14 * s, 14 * s, wb.marker(BLACK, 6, alpha))
    neck = skia.Rect.MakeXYWH(x - 17 * s, yb - h - 24 * s, 34 * s, 26 * s)
    c.drawRect(neck, K.paint("#FFFFFF", alpha))
    c.drawRect(neck, wb.marker(BLACK, 5, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 20 * s, yb - h - 36 * s, 40 * s, 14 * s), 4, 4, K.paint(BLUE, alpha))


def box(c, x, yb, w=150, h=110, alpha=1.0, fill="#F1DDB8", color="#A9773E", rot=0.0):
    """纸箱（填色）：(x, yb) 为底边中点。"""
    with K.at(c, x, yb - h / 2, rot):
        r = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
        c.drawRoundRect(r, 8, 8, K.paint(fill, alpha))
        c.drawRoundRect(r, 8, 8, wb.marker(color, 7, alpha))
        c.drawLine(-w / 2, -h / 2 + 24, w / 2, -h / 2 + 24, wb.marker(color, 5, alpha))
        c.drawLine(0, -h / 2, 0, -h / 2 + 24, wb.marker(color, 5, alpha))


def paper(c, x, y, w, h, alpha=1.0, rot=0.0, lines=4, fill="#FFFFFF", color=BLACK):
    """一张纸（填白，带横线）：(x, y) 为中心。"""
    with K.at(c, x, y, rot):
        c.drawPath(doc(0, 0, w, h, lines), K.paint(fill, alpha))
        c.drawPath(doc(0, 0, w, h, lines), wb.marker(color, 6, alpha))


def shelf_path(x0, x1, roof, floors, foot):
    """侧视冷柜：两根立柱（roof → foot）+ 顶板 + 各层隔板。"""
    parts = [P((x0, roof), (x0, foot)), P((x1, roof), (x1, foot)), P((x0 - 20, roof), (x1 + 20, roof))]
    for y in floors:
        parts.append(P((x0, y), (x1, y)))
    return join(*parts)


def draw_customer(c, x, y, s, lh=None, rh=None, alpha=1.0, basket=True, mood="smile"):
    """顾客：橙色上衣、扎马尾，右手挎购物篮。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = shoulder(x, y, s)
    hip = (x, y - 120 * s)
    for foot in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, foot, BLACK, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 40 * s, hy + 55 * s, x + 40 * s, y - 100 * s)
    c.drawRoundRect(torso, 16 * s, 16 * s, K.paint("#F8D2B0", alpha))
    c.drawRoundRect(torso, 16 * s, 16 * s, wb.marker(ORANGE, 7, alpha))
    C.line(c, sh, lh, ORANGE, 10, alpha)
    C.line(c, sh, rh, ORANGE, 10, alpha)
    c.drawCircle(x + 52 * s, hy - 18 * s, 20 * s, K.paint(BLACK, alpha))
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    fr = skia.Path()
    fr.addArc(skia.Rect.MakeXYWH(x - 46 * s, hy - 46 * s, 92 * s, 60 * s), 180, 180)
    c.drawPath(fr, wb.marker(BLACK, 12, alpha))
    C._eyes_mouth(c, x, hy, s, mood, alpha)
    if basket:
        bx, by = rh
        c.drawPath(P((bx - 45 * s, by + 10 * s), (bx - 35 * s, by + 70 * s), (bx + 35 * s, by + 70 * s), (bx + 45 * s, by + 10 * s),
                     close=True), K.paint("#FBE3C8", alpha))
        c.drawPath(P((bx - 45 * s, by + 10 * s), (bx - 35 * s, by + 70 * s), (bx + 35 * s, by + 70 * s), (bx + 45 * s, by + 10 * s),
                     close=True), wb.marker(ORANGE, 6, alpha))
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(bx - 35 * s, by - 30 * s, 70 * s, 80 * s), 180, 180)
        c.drawPath(arc, wb.marker(ORANGE, 5, alpha))


def draw_clerk(c, x, y, s, lh=None, rh=None, alpha=1.0, mood="smile"):
    """店员：绿围裙、绿帽。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = shoulder(x, y, s)
    hip = (x, y - 120 * s)
    C.line(c, (x, hy + 45 * s), hip, BLACK, 10, alpha)
    for foot in ((x - 52 * s, y), (x + 52 * s, y)):
        C.line(c, hip, foot, BLACK, 10, alpha)
    apron = P((x - 30 * s, hy + 70 * s), (x + 30 * s, hy + 70 * s), (x + 48 * s, y - 70 * s), (x - 48 * s, y - 70 * s), close=True)
    c.drawPath(apron, K.paint("#CDEBD7", alpha))
    c.drawPath(apron, wb.marker(GREEN, 7, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 20 * s, hy + 130 * s, 40 * s, 30 * s), 5, 5, wb.marker(GREEN, 5, alpha))
    C.line(c, sh, lh, BLACK, 10, alpha)
    C.line(c, sh, rh, BLACK, 10, alpha)
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    C._eyes_mouth(c, x, hy, s, mood, alpha)
    cap = skia.Path()
    cap.addArc(skia.Rect.MakeXYWH(x - 46 * s, hy - 66 * s, 92 * s, 66 * s), 180, 180)
    cap.close()
    c.drawPath(cap, K.paint(GREEN, alpha))
    c.drawPath(cap, wb.marker(BLACK, 6, alpha))
    C.line(c, (x + 10 * s, hy - 33 * s), (x + 78 * s, hy - 28 * s), BLACK, 10, alpha)


def pop_fn(j, k, draw, dur=0.32):
    """第 j 屏第 k 拍弹出：draw(c, sc, T)，sc 为弹出缩放（调用方自己决定以哪里为中心缩放）。"""
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k), dur)
        if sc > 0:
            draw(c, sc, T)
        return None
    return fn


@contextmanager
def at_pop(c, x, y, sc):
    """以 (x, y) 为中心缩放 sc（里面照常用白板绝对坐标画）。"""
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    c.translate(-x, -y)
    try:
        yield
    finally:
        c.restore()


def label(j, k0, s, x, y, size=70, color=BLACK, sfx=None):
    b.text(j, k0, k0 + 0.1 + 0.12 * len(s), s, x, y, size, color, sfx=sfx)


def draw_wang(c, x, y, s, lh=None, rh=None, mood="flat", head_dy=0.0):
    """同事小王（办公室，不戴安全帽）：照抄第 06/07 讲造型。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s + head_dy
    sh = (x, y - 290 * s + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, ft, BLUE, 10)
    C.line(c, sh, lh, BLUE, 10)
    C.line(c, sh, rh, BLUE, 10)
    torso = skia.Rect.MakeLTRB(x - 42 * s, y - 235 * s, x + 42 * s, y - 105 * s)
    c.drawRoundRect(torso, 18 * s, 18 * s, K.paint("#FFFFFF"))
    c.drawRoundRect(torso, 18 * s, 18 * s, wb.marker(BLUE, 7))
    badge = skia.Rect.MakeXYWH(x - 20 * s, y - 180 * s, 40 * s, 30 * s)
    c.drawRoundRect(badge, 4, 4, K.paint("#DCE8F7"))
    c.drawRoundRect(badge, 4, 4, wb.marker(BLUE, 4))
    c.drawRoundRect(skia.Rect.MakeLTRB(x - 54 * s, hy - 46 * s, x + 54 * s, hy + 40 * s), 26 * s, 26 * s, K.paint("#2E2A28"))
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF"))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 9))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(x - 50 * s, hy - 52 * s, 100 * s, 72 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint("#2E2A28"))
    c.drawCircle(x + 36 * s, hy - 24 * s, 9 * s, K.paint(ORANGE))
    C._eyes_mouth(c, x, hy + 4 * s, s, mood, 1.0)


# ================================================================ 屏 0：系列开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：小李怕领导要，文件越摞越高；一半用不上，一半重改
cx, cy = R[1]
j = L.scene(1, (cx, cy + 70, Z))
DESK = (cx + 110, cy + 200)
LI1 = (cx - 330, cy + 340, 0.95)
b.path(j, 0, 0.8, join(P((DESK[0] - 240, DESK[1]), (DESK[0] + 240, DESK[1])),
                       P((DESK[0] - 210, DESK[1]), (DESK[0] - 210, DESK[1] + 140)),
                       P((DESK[0] + 210, DESK[1]), (DESK[0] + 210, DESK[1] + 140))), BLACK, 9, sfx="wood_high")
S1 = {}


def li1_fn(c, kk, T):
    x, y, s = LI1
    sc = pop_scale(T - tb(1, 1))
    if sc <= 0:
        return None
    mood = "sad" if T >= S1["redo"]() else ("o" if T >= S1["half"]() else "flat")
    hy = y - 290 * s
    look = 0.0
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "flat" if mood == "o" else mood, lh=(x - 80 * s, hy + 160 * s),
                rh=(x + 110 * s, hy + 110 * s + look))
        if mood == "o":
            c.drawCircle(x, hy + 20 * s, 8 * s, wb.marker(BLACK, 5))
    return None


b.custom(j, 1, 1.3, li1_fn, sfx="pop")
label(j, 1.3, "小李", LI1[0], LI1[1] + 90, 72)
k_boss = kb(j, wt(0, 0, 0.75), lo=2)


def think_boss(c, sc, T):
    cx, cy = R[1]
    x, y = LI1[0] + 10, cy - 210
    with K.at(c, x, y, 0, sc):
        for (dx, dy, r) in ((-60, 175, 14), (-40, 140, 22)):
            c.drawCircle(dx, dy, r, K.paint("#FFFFFF"))
            c.drawCircle(dx, dy, r, wb.marker(BLACK, 6))
        oval = skia.Rect.MakeXYWH(-170, -120, 340, 230)
        c.drawOval(oval, K.paint("#FFFFFF"))
        c.drawOval(oval, wb.marker(BLACK, 7))
        draw_boss(c, -50, 90, 0.5)
        K.text(c, "？", 75, -5, 120, "hand", RED)


b.custom(j, k_boss, k_boss + 0.3, pop_fn(j, k_boss, think_boss), sfx="pop")
k_p0 = kb(j, wt(0, 1, 0.05), lo=k_boss + 1)
NPILE = 9
PILE_TOP = [None] * NPILE


def doc_slab(i):
    def draw(c, sc, T):
        y = DESK[1] - 24 - i * 46
        x = DESK[0] + (7, -5, 9, -8, 4, -10, 6, -4, 8)[i]
        crossed = T >= S1["half"]() and i >= 5
        with K.at(c, x, y + (1 - sc) * -60, (i % 3 - 1) * 1.5, 1.0):
            r = skia.Rect.MakeXYWH(-130, -21, 260, 42)
            c.drawRoundRect(r, 6, 6, K.paint("#E9EDF3" if crossed else "#FFFFFF", clamp01(sc * 2)))
            c.drawRoundRect(r, 6, 6, wb.marker("#9AA0AC" if crossed else BLACK, 6, clamp01(sc * 2)))
            c.drawLine(-100, 0, 60, 0, wb.marker("#9AA0AC", 4, clamp01(sc * 2)))
    return draw


ks = []
k = k_p0
for i in range(NPILE):
    ks.append(k)
    b.custom(j, k, k + 0.3, pop_fn(j, k, doc_slab(i), 0.22), sfx=("wood_high", "wood_low")[i % 2] if i % 2 == 0 else None,
             gain=0.6)
    k += 0.5 if i % 2 == 0 else 0.5
    k = round(k * 2) / 2
k_half = kb(j, wt(1, 0, 0.55), lo=int(math.ceil(ks[-1])) + 1)
k_redo = kb(j, wt(1, 1, 0.55), lo=k_half + 1)
S1["half"] = lambda: tb(1, k_half)
S1["redo"] = lambda: tb(1, k_redo)
top_c = DESK[1] - 24 - 7 * 46
b.path(j, k_half, k_half + 0.5, cross(DESK[0], top_c, 120), RED, 13, sfx="rim")
b.custom(j, k_half + 0.5, k_half + 0.8, L.pop_text("用不上", DESK[0] + 340, top_c, 72, RED, j, k_half + 0.5))
bot_c = DESK[1] - 24 - 2 * 46
b.path(j, k_redo, k_redo + 0.6, C.loop_arrow(DESK[0] + 210, bot_c, 46), ORANGE, 11, sfx="wood_low")
b.custom(j, k_redo + 0.6, k_redo + 0.9, L.pop_text("重改", DESK[0] + 360, bot_c, 72, ORANGE, j, k_redo + 0.6))

# ================================================================ 屏 2：过量生产——仓库堆满，drop 时“最大浪费”印章砸下
cx, cy = R[2]
j = L.scene(2, (cx, cy + 20, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
b.path(j, 0, 0.6, book(cx - 420, cy - 450, 150, 100), GREEN, 7, sfx="wood_low")
b.text(j, 0.6, 1.4, "丰田模式", cx - 160, cy - 450, 76, GREEN)
RACK = (cx - 440, cx + 440, cy - 300, cy + 260)
rows = [cy - 300 + 140, cy - 300 + 280, cy + 260]
b.path(j, 1, 1.8, shelf_path(RACK[0], RACK[1], RACK[2], rows[:2], RACK[3]), BLACK, 9, sfx="wood_high")
k_fill = 2


def rack_row(r):
    def draw(c, sc, T):
        yb = rows[r] - 4
        for i in range(5):
            x = RACK[0] + 90 + i * 175
            with at_pop(c, x, yb, pop_scale(T - tb(2, k_fill + r) - i * 0.05)):
                box(c, x, yb, 150, 112)
    return draw


for r in range(3):
    b.custom(j, k_fill + r, k_fill + r + 0.4, pop_fn(j, k_fill + r, rack_row(r)), sfx=("wood_low", "wood_high", "wood_low")[r])
k_over = k_fill + 3


def floor_boxes(c, sc, T):
    cx, cy = R[2]
    for i, (dx, rot) in enumerate(((-370, -6), (-215, 4), (-60, -3), (95, 7), (250, -5), (400, 6))):
        f = pop_scale(T - tb(2, k_over) - i * 0.06)
        if f > 0:
            with at_pop(c, cx + dx, cy + 440, f):
                box(c, cx + dx, cy + 440, 140, 104, rot=rot)


b.custom(j, k_over, k_over + 0.5, pop_fn(j, k_over, floor_boxes), sfx="tom", gain=0.6)
k_label = kb(j, wt(2, 0, 0.6), lo=k_over + 1)
b.custom(j, k_label, k_label + 0.3, L.pop_text("过量生产", cx + 250, cy - 450, 84, RED, j, k_label), sfx="pop")
b.custom(j, KD, KD + 0.3, L.stamp("最大浪费", cx, cy + 10, 120, j, KD), sfx="kick", gain=0.95)

# ================================================================ 屏 3：那它怎么办？答案来自超市——大野耐一看补货，想通了
cx, cy = R[3]
j = L.scene(3, (cx, cy + 20, Z))
SH3 = (cx - 60, cx + 470, cy - 180, [cy + 20, cy + 220], cy + 330)
OH = (cx - 360, cy + 330, 0.95)
b.path(j, 0, 0.8, shelf_path(SH3[0], SH3[1], SH3[2], SH3[3], SH3[4]), BLACK, 9, sfx="wood_high")


def shelf3_bottles(c, sc, T):
    for r, fy in enumerate(SH3[3]):
        for i in range(4):
            x = SH3[0] + 75 + i * 125
            f = pop_scale(T - tb(3, 1) - (r * 4 + i) * 0.04)
            if f > 0:
                with at_pop(c, x, fy - 4, f):
                    bottle(c, x, fy - 4, 1.0)


b.custom(j, 1, 1.4, pop_fn(j, 1, shelf3_bottles), sfx="wood_low")
k_q = kb(j, wt(3, 0, 0.2), lo=2)
k_sign = kb(j, wt(3, 0, 0.85), lo=k_q + 1)
k_oh = kb(j, wt(4, 0, 0.15), lo=k_sign + 1)
k_bulb = kb(j, wt(4, 1, 0.5), lo=k_oh + 2)
QB = (OH[0], cy - 150)


def question3(c, sc, T):
    f = sc * (1 - ease_in_out(clamp01((T - tb(3, k_bulb) + 0.05) / 0.2)))
    if f > 0:
        with K.at(c, QB[0], QB[1], 0, f):
            K.text(c, "？", 0, 0, 170, "hand", RED)


L.note("？")
b.custom(j, k_q, k_q + 0.3, pop_fn(j, k_q, question3), sfx="rim", gain=0.7)


def sign3(c, sc, T):
    cx, cy = R[3]
    x, y = (SH3[0] + SH3[1]) / 2, cy - 360
    with K.at(c, x, y, 0, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(-170, -70, 340, 140), 18, 18, K.paint("#FFF4D6"))
        c.drawRoundRect(skia.Rect.MakeXYWH(-170, -70, 340, 140), 18, 18, wb.marker(ORANGE, 9))
        K.text(c, "超市", 0, 0, 100, "hand", ORANGE)
        c.drawLine(-110, 70, -110, 110, wb.marker(BLACK, 6))
        c.drawLine(110, 70, 110, 110, wb.marker(BLACK, 6))


L.note("超市")
b.custom(j, k_sign, k_sign + 0.3, pop_fn(j, k_sign, sign3), sfx="ding", gain=0.7)


def ohno3(c, sc, T):
    x, y, s = OH
    lit = T >= tb(3, k_bulb)
    hy = y - 290 * s
    rh = (x + 110 * s, hy + 60 * s) if lit else (x + 60 * s, hy + 190 * s)
    lh = (x - 30 * s, hy + 60 * s) if not lit else (x - 70 * s, hy + 170 * s)
    with at_pop(c, x, y, sc):
        draw_ohno(c, x, y, s, lh=lh, rh=rh, mood="smile" if lit else "flat",
                  head_dx=6 * math.sin((T - tb(3, k_oh)) * 2.4) if not lit else 0.0)


b.custom(j, k_oh, k_oh + 0.3, pop_fn(j, k_oh, ohno3), sfx="wood_high")
label(j, k_oh + 0.4, "大野耐一", OH[0], OH[1] + 90, 70, BLACK)


def bulb3(c, sc, T):
    with at_pop(c, QB[0], QB[1], sc):
        c.drawCircle(QB[0], QB[1], 80, K.paint(YELLOW, 0.25 * sc, blur=30))
        c.drawCircle(QB[0], QB[1], 50, K.paint("#FFF1B8"))
        c.drawPath(C.bulb_path(QB[0], QB[1], 50), wb.marker(ORANGE, 9))


b.custom(j, k_bulb, k_bulb + 0.3, pop_fn(j, k_bulb, bulb3), sfx="ding")

# ================================================================ 屏 4：顾客拿走一瓶，后面滑上来，店员从后面补一瓶；不堆货、不断货
cx, cy = R[4]
j = L.scene(4, (cx, cy + 30, Z))
SX0, SX1 = cx - 300, cx + 300
TOP_F, LOW_F, ROOF, FOOT = cy + 20, cy + 220, cy - 180, cy + 330
SLOT = [SX0 + 60 + i * 120 for i in range(5)]
CU = (cx + 450, cy + 330, 1.0)
CL = (cx - 470, cy + 330, 1.0)
b.path(j, 0, 0.8, shelf_path(SX0, SX1, ROOF, [TOP_F, LOW_F], FOOT), BLACK, 9, sfx="wood_high")
S4 = {}


def bottles4(c, kk, T):
    t_take, t_slide, t_fill = S4["take"](), S4["slide"](), S4["fill"]()
    for i in range(5):                                     # 下层：静止
        f = pop_scale(T - tb(4, 1) - i * 0.04)
        if f > 0:
            with at_pop(c, SLOT[i], LOW_F - 4, f):
                bottle(c, SLOT[i], LOW_F - 4)
    for i in range(5):                                     # 上层：最前面（右）那瓶被拿走，其余往前滑一格
        f = pop_scale(T - tb(4, 1) - (5 + i) * 0.04)
        if f <= 0:
            continue
        if i == 4 and T >= t_take:
            continue
        x = SLOT[i]
        if T >= t_slide:
            x = lerp(SLOT[i], SLOT[i + 1], ease_out(clamp01((T - t_slide) / 0.3)))
        with at_pop(c, x, TOP_F - 4, f):
            bottle(c, x, TOP_F - 4)
    if T >= t_fill:                                        # 店员补上的那瓶
        bottle(c, SLOT[0], TOP_F - 4)
    if t_slide <= T < t_fill:                              # 后面空出一格：红虚线框闪
        a = 0.5 + 0.5 * math.cos((T - t_slide) * 9)
        r = skia.Rect.MakeXYWH(SLOT[0] - 45, TOP_F - 132, 90, 128)
        p = K.paint(RED, a, 5)
        p.setPathEffect(skia.DashPathEffect.Make([16, 10], 0))
        c.drawRoundRect(r, 10, 10, p)
    return None


def take_pos(T):
    """被拿走的那瓶：从货架最前面到顾客的篮子里。"""
    t0 = S4["take"]()
    f = ease_in_out(clamp01((T - t0) / 0.45))
    x, y, s = CU
    basket = (x + 70 * s, y - 290 * s + 170 * s)
    return lerp(SLOT[4], basket[0], f), lerp(TOP_F - 4, basket[1] + 50, f), f


def customer4(c, kk, T):
    x, y, s = CU
    t_in = tb(4, S4["k_cu"])
    if T < t_in:
        return None
    xx, dy, moving = walk(T, t_in, 0.8, x + 120, x)
    hy = y - 290 * s
    t0 = S4["take"]()
    reach = ease_out(clamp01((T - (t0 - 0.35)) / 0.35)) * (1 - ease_in_out(clamp01((T - t0) / 0.45)))
    lh = (lerp(xx - 70 * s, SLOT[4] + 30, reach), lerp(hy + 170 * s, TOP_F - 60, reach))
    a = clamp01((T - t_in) / 0.25)
    if T >= t0:
        bx, by, f = take_pos(T)
        if f < 1:
            lh = (bx + 20, by - 40)
    c.save()
    c.translate(0, dy)
    draw_customer(c, xx, y, s, lh=lh, alpha=a)
    c.restore()
    if T >= t0:
        bx, by, f = take_pos(T)
        with K.at(c, bx, by, 0, lerp(1.0, 0.7, f)):
            bottle(c, 0, 0)
    return None


def clerk4(c, kk, T):
    x, y, s = CL
    t_in = tb(4, S4["k_cl"])
    if T < t_in:
        return None
    xx, dy, moving = walk(T, t_in, 0.8, x - 120, x)
    hy = y - 290 * s
    t_fill = S4["fill"]()
    reach = ease_out(clamp01((T - (t_fill - 0.45)) / 0.45)) * (1 - ease_in_out(clamp01((T - t_fill - 0.35) / 0.4)))
    rh = (lerp(xx + 70 * s, SLOT[0] - 40, reach), lerp(hy + 140 * s, TOP_F - 50, reach))
    a = clamp01((T - t_in) / 0.25)
    c.save()
    c.translate(0, dy)
    draw_clerk(c, xx, y, s, rh=rh, alpha=a)
    c.restore()
    if T < t_fill:                                         # 补上之后这瓶由 bottles4 画在货架上
        g = ease_out(clamp01((T - t_fill + 0.12) / 0.12))
        with K.at(c, lerp(rh[0] + 20, SLOT[0], g), lerp(rh[1] + 50, TOP_F - 4, g), 0, 1.0):
            bottle(c, 0, 0, alpha=a)
    if T >= t_fill and T - t_fill < 0.4:
        K.ripple(c, SLOT[0], TOP_F - 60, T - t_fill, GREEN, 110, 6, 0.8, 0.4)
    return None


b.custom(j, 1, 1.4, bottles4, sfx="wood_low")
S4["k_cu"] = kb(j, wt(5, 0, 0.0), lo=2)
k_take = kb(j, wt(5, 0, 0.6), lo=S4["k_cu"] + 2)
S4["take"] = lambda: tb(4, k_take)
S4["slide"] = lambda: tb(4, k_take + 1)
S4["k_cl"] = k_take
k_fill4 = kb(j, wt(5, 1, 0.75), lo=k_take + 2)
S4["fill"] = lambda: tb(4, k_fill4)
b.custom(j, S4["k_cu"], S4["k_cu"] + 0.3, customer4, sfx="bongo_low", gain=0.7)
label(j, S4["k_cu"] + 0.6, "顾客", CU[0], CU[1] + 90, 68, ORANGE)
b.hit(j, k_take, "pop", 0.8, "顾客拿走最前面一瓶")
b.hit(j, k_take + 1, "shaker", 0.7, "后面几瓶往前滑一格")
b.custom(j, k_take, k_take + 0.3, clerk4)
label(j, k_take + 0.8, "店员", CL[0], CL[1] + 90, 68, GREEN)
b.hit(j, k_fill4, "ding", 0.8, "店员从后面补上一瓶")
k_ok1 = kb(j, wt(6, 0, 0.6), lo=k_fill4 + 1)
k_ok2 = kb(j, wt(6, 1, 0.6), lo=k_ok1 + 1)
for kk_, txt, x in ((k_ok1, "不堆货", cx - 230), (k_ok2, "不断货", cx + 210)):
    b.custom(j, kk_, kk_ + 0.3, L.pop_text(txt, x, cy - 330, 76, BLACK, j, kk_), sfx="pop")
    b.path(j, kk_ + 0.3, kk_ + 0.7, check(x + 165, cy - 330, 34), GREEN, 12)

# ================================================================ 屏 5：车间——后工序拿看板来取货，前工序只补被取走的那件
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
TBL = [(cx - 250, cy + 60), (cx + 260, cy + 60)]
FW = (cx - 470, cy + 330, 0.9)
RW = (cx + 480, cy + 330, 0.9)


def table_path(x, y, w=280):
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 20, y), (x - w / 2 + 20, y + 120)),
                P((x + w / 2 - 20, y), (x + w / 2 - 20, y + 120)))


b.path(j, 0, 0.8, join(table_path(*TBL[0]), table_path(*TBL[1])), BLACK, 9, sfx="wood_high")
b.text(j, 0.8, 1.2, "前工序", TBL[0][0], TBL[0][1] + 190, 66, BLUE)
b.text(j, 1.2, 1.6, "后工序", TBL[1][0], TBL[1][1] + 190, 66, BLUE)
S5 = {}
k_go = kb(j, wt(7, 0, 0.55), lo=2)
k_grab = k_go + 2
k_make = kb(j, wt(7, 1, 0.5), lo=k_grab + 1)
k_card = kb(j, wt(8, 1, 0.3), lo=k_make + 1)
k_kb = kb(j, wt(8, 2, 0.5), lo=k_card + 1)


def boxes5(c, kk, T):
    """前工序桌上两箱；后工序员工取走一箱；前工序再做一箱补上。"""
    t_grab, t_make = tb(5, k_grab), tb(5, k_make)
    for i, dx in enumerate((-60, 60)):
        f = pop_scale(T - tb(5, 2) - i * 0.06)
        if f <= 0 or (i == 1 and T >= t_grab):
            continue
        with at_pop(c, TBL[0][0] + dx, TBL[0][1] - 2, f):
            box(c, TBL[0][0] + dx, TBL[0][1] - 2, 110, 90)
    if T >= t_make:
        f = pop_scale(T - t_make)
        with at_pop(c, TBL[0][0] + 60, TBL[0][1] - 2, f):
            box(c, TBL[0][0] + 60, TBL[0][1] - 2, 110, 90, fill="#DCEFD9", color=GREEN)
    return None


def rear_x(T):
    t0 = tb(5, k_go)
    x, dy, _ = walk(T, t0, tb(5, k_grab) - t0 - 0.05, RW[0], TBL[0][0] + 230)
    if T >= tb(5, k_grab) + 0.35:
        x, dy, _ = walk(T, tb(5, k_grab) + 0.35, 1.0, TBL[0][0] + 230, RW[0])
    return x, dy


def card_draw(c, x, y, s=1.0, alpha=1.0, text=True):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 46 * s, y - 32 * s, 92 * s, 64 * s), 8, 8, K.paint("#FFE9A8", alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 46 * s, y - 32 * s, 92 * s, 64 * s), 8, 8, wb.marker(ORANGE, 6, alpha))
    if text:
        K.text(c, "看板", x, y, 34 * s, "hand", BLACK, alpha)


def rear5(c, kk, T):
    x0, y, s = RW
    x, dy = rear_x(T)
    hy = y - 290 * s
    t_grab = tb(5, k_grab)
    carrying = T >= t_grab
    lh = (x - 90 * s, hy + 120 * s)                      # 左手举着看板
    rh = (x + 60 * s, hy + 150 * s)
    if carrying:
        lh, rh = (x - 60 * s, hy + 140 * s), (x + 60 * s, hy + 140 * s)
    c.save()
    sc = pop_scale(T - tb(5, 2))
    c.translate(x, y)
    c.scale(sc, sc)
    c.translate(-x, -y + dy)
    draw_worker(c, x, y, s, lh=lh, rh=rh, mood="smile")
    if carrying:
        bx = lerp(TBL[0][0] + 60, x, ease_out(clamp01((T - t_grab) / 0.3)))
        by = lerp(TBL[0][1] - 2, hy + 175 * s, ease_out(clamp01((T - t_grab) / 0.3)))
        box(c, bx, by, 110, 90)
    if not carrying:
        card_draw(c, lh[0], lh[1] - 20, 1.0)
    c.restore()
    if T >= t_grab:                                      # 看板留在前工序桌上
        card_draw(c, TBL[0][0] - 60, TBL[0][1] - 45, 1.0)
    return None


L.note("看板")
b.custom(j, 2, 2.4, boxes5, sfx="wood_low")
b.custom(j, 2, 2.3, L.figure(draw_worker, j, 2, FW[0], FW[1], FW[2], mood="flat",
                             rh=lambda T: (FW[0] + 120 * FW[2], FW[1] - 290 * FW[2] + (90 if T < tb(5, k_make) - 0.2
                                                                                        or T > tb(5, k_make) + 0.3 else 30) * FW[2])))
b.custom(j, 2, 2.3, rear5)
b.path(j, k_go, k_go + 0.8, arrow((cx + 300, cy - 200), (cx - 200, cy - 200), 0.12, 40), BLUE, 10, sfx="bongo_low")
b.custom(j, k_go + 0.8, k_go + 1.1, L.pop_text("来取", cx + 50, cy - 300, 72, BLUE, j, k_go + 0.8))
b.hit(j, k_grab, "pop", 0.8, "后工序取走一箱，看板留在桌上")
b.hit(j, k_make, "tom", 0.8, "前工序只补做一箱")
b.custom(j, k_make, k_make + 0.3, L.pop_text("补一件", TBL[0][0] + 60, cy - 100, 62, GREEN, j, k_make))


def big_card(c, sc, T):
    cx, cy = R[5]
    x, y = cx, cy - 440
    with at_pop(c, x, y, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 150, y - 75, 300, 150), 14, 14, K.paint("#FFE9A8"))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 150, y - 75, 300, 150), 14, 14, wb.marker(ORANGE, 9))
        K.text(c, "看板", x, y, 96, "hand", RED)


b.custom(j, k_kb, k_kb + 0.3, pop_fn(j, k_kb, big_card), sfx="rim")
b.hit(j, k_card, "wood_high", 0.7, "看板卡片在桌上一亮")
S5["k_kb"] = k_kb

# ================================================================ 屏 6：书中观点——拉动：下一步拉一下，你再做
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
b.path(j, 0, 0.6, book(cx - 420, cy - 450, 150, 100), GREEN, 7, sfx="wood_low")
b.text(j, 0.6, 1.3, "书中观点", cx - 180, cy - 450, 64, GREEN)
k_ld = kb(j, wt(9, 0, 0.2), lo=1)
b.custom(j, k_ld, k_ld + 0.3, L.slam_text("拉动", cx, cy - 250, 190, RED, j, k_ld), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_ld, 12.0)]
LI6 = (cx - 300, cy + 380, 1.1)
WK6 = (cx + 340, cy + 380, 1.1)
k_pull = kb(j, wt(9, 0, 0.75), lo=k_ld + 2)
k_make6 = kb(j, wt(9, 1, 0.3), lo=k_pull + 1)


def tug6(T):
    return ease_out(clamp01((T - tb(6, k_pull)) / 0.2)) * (1 - 0.6 * ease_in_out(clamp01((T - tb(6, k_pull) - 0.5) / 0.6)))


def rope6(c, kk, T):
    cx, cy = R[6]
    sc = pop_scale(T - tb(6, 2))
    c.save()
    c.translate(cx, cy + 340)
    c.scale(sc, sc)
    c.translate(-cx, -cy - 340)
    _rope6(c, T)
    c.restore()
    return None


def _rope6(c, T):
    f = tug6(T)
    xl, y, s = LI6
    xr = WK6[0]
    lean = 18 * f
    hy = y - 290 * s
    a = (xl + 120 * s + lean, hy + 130 * s)
    z = (xr - 120 * s + 25 * f, hy + 130 * s)
    sag = 70 * (1 - f)
    p = skia.Path()
    p.moveTo(*a)
    p.quadTo((a[0] + z[0]) / 2, a[1] + sag, *z)
    c.drawPath(p, wb.marker(ORANGE, 9))
    if f > 0.05:
        m = ((a[0] + z[0]) / 2, a[1] - 50)
        c.drawPath(arrow((m[0] - 70, m[1]), (m[0] + 90, m[1]), 0, 26), wb.marker(RED, 7, clamp01(f * 2)))
    c.save()
    c.translate(lean, 0)
    draw_li(c, xl, y, s, "flat", rh=a)
    c.restore()
    draw_worker(c, WK6[0] + 25 * f, y, WK6[2], lh=z, rh=(z[0] + 30, z[1] + 10), mood="smile")
    return None


b.custom(j, 2, 2.3, rope6, sfx="wood_high")
b.text(j, 2.4, 2.6, "你", LI6[0], LI6[1] + 90, 76, BLACK)
b.text(j, 2.6, 3.0, "下一步", WK6[0], WK6[1] + 90, 76, BLUE)
b.hit(j, k_pull, "clap", 0.9, "下一步拉一下绳")


def made6(c, sc, T):
    x, y = LI6[0] - 200, LI6[1]
    with at_pop(c, x, y, sc):
        box(c, x, y, 120, 96, fill="#DCEFD9", color=GREEN)
    c.drawPath(check(x + 10, y - 150, 34), wb.marker(GREEN, 11, clamp01(sc)))


b.custom(j, k_make6, k_make6 + 0.3, pop_fn(j, k_make6, made6), sfx="ding")

# ================================================================ 屏 7：提前做好不是更保险？——小李抱的箱子越摞越高，晃
cx, cy = R[7]
j = L.scene(7, (cx, cy + 20, Z))
LI7 = (cx - 280, cy + 360, 0.95)
k_b7 = kb(j, wt(10, 0, 0.6), lo=1)
k_bub7 = kb(j, wt(10, 1, 0.3), lo=k_b7 + 2)
k_more = kb(j, wt(11, 0, 0.3), lo=k_bub7 + 1)
k_pile7 = kb(j, wt(11, 1, 0.6), lo=k_more + 2)
N7 = 7


def stack7_ks():
    out = [k_b7, k_b7 + 1]
    k = k_more
    while len(out) < N7:
        out.append(k)
        k += 1
    return out


KS7 = stack7_ks()


def li7(c, kk, T):
    x, y, s = LI7
    if T < tb(7, 1):
        return None
    sc = pop_scale(T - tb(7, 1))
    hy = y - 290 * s
    n = sum(1 for k in KS7 if T >= tb(7, k))
    sway = 0.0
    if n >= 4:
        sway = (n - 3) * 2.2 * math.sin((T - tb(7, KS7[3])) * 3.4)
    sway += wobble(T - tb(7, k_pile7), 6, 16, 3)
    hands = ((x + 95 * s, hy + 160 * s), (x + 225 * s, hy + 160 * s))
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad" if n >= 5 else "flat", lh=hands[0], rh=hands[1])
        base = hy + 150 * s
        for i in range(n):
            f = pop_scale(T - tb(7, KS7[i]), 0.25)
            with K.at(c, x + 165 * s, base, sway * (i / max(1, N7 - 1)) * 1.6):
                yb = -i * 92 - (1 - f) * 80
                with K.at(c, (i % 2) * 10 - 5, yb - 45, 0, f):
                    box(c, 0, 45, 150, 90)
    return None


b.custom(j, 1, 1.3, li7, sfx="pop")
label(j, 1.4, "小李", LI7[0], LI7[1] + 90, 72)
for i, k in enumerate(KS7[1:]):
    b.hit(j, k, ("wood_high", "wood_low")[i % 2], 0.6, "又摞上一箱")
b.custom(j, k_bub7, k_bub7 + 0.3, L.pop_bubble("更保险？", cx + 300, cy - 330, j, k_bub7, 76, BLUE, tail=-1), sfx="pop")
b.custom(j, k_pile7, k_pile7 + 0.3, L.slam_text("堆起来", cx + 330, cy + 120, 110, RED, j, k_pile7), sfx="rim")

# ================================================================ 屏 8：堆着占地方、毛病看不出、要求一变全白做——越多越乱
cx, cy = R[8]
j = L.scene(8, (cx, cy + 20, Z))
PILE8 = []
for r, n in enumerate((5, 4, 3, 2)):
    for i in range(n):
        PILE8.append((cx - 130 + (i - (n - 1) / 2) * 160, cy + 300 - r * 112, r))
k_fl = kb(j, wt(12, 0, 0.2), lo=1)
k_crack = kb(j, wt(12, 1, 0.5), lo=k_fl + 2)
k_req = kb(j, wt(12, 2, 0.3), lo=k_crack + 1)
k_x8 = kb(j, wt(12, 3, 0.5), lo=k_req + 1)
k_mess = kb(j, wt(13, 1, 0.3), lo=k_x8 + 1)
CRACK = PILE8[2]


def pile8(c, kk, T):
    t_x = tb(8, k_x8)
    mess = T >= tb(8, k_mess)
    for i, (x, yb, r) in enumerate(PILE8):
        f = pop_scale(T - tb(8, k_fl + r) - i % 5 * 0.04)
        if f <= 0:
            continue
        rot, dx, dy = 0.0, 0.0, 0.0
        if mess:
            dt = T - tb(8, k_mess)
            g = ease_out(clamp01(dt / 0.35))
            rot = ((i * 37) % 21 - 10) * 1.4 * g
            dx = ((i * 53) % 31 - 15) * 3 * g
            dy = -abs(((i * 17) % 13 - 6)) * 2 * g
        with at_pop(c, x, yb, f):
            box(c, x + dx, yb + dy, 150, 104, fill="#E9EDF3" if T >= t_x else "#F1DDB8",
                color="#8A8F99" if T >= t_x else "#A9773E", rot=rot)
    if T >= tb(8, k_crack):
        x, yb, _ = CRACK
        f = clamp01((T - tb(8, k_crack)) / 0.3)
        p = P((x - 40, yb - 80), (x - 15, yb - 55), (x - 30, yb - 35), (x + 5, yb - 20), (x - 5, yb - 5))
        part, _ = wb.partial(p, f)
        c.drawPath(part, wb.marker(RED, 7))
    return None


for r in range(4):
    b.hit(j, k_fl + r, ("wood_low", "wood_high")[r % 2], 0.6, "箱子堆满地面")
b.custom(j, k_fl, k_fl + 0.3, pile8)


def magnifier(c, sc, T):
    x, yb, _ = CRACK
    mx, my = x - 20, yb - 45
    with at_pop(c, mx, my, sc):
        c.drawCircle(mx, my, 72, K.paint("#FFFFFF", 0.25))
        c.drawCircle(mx, my, 72, wb.marker(BLACK, 9))
        c.drawLine(mx - 52, my - 52, mx - 115, my - 115, wb.marker(BLACK, 16))


b.custom(j, k_crack, k_crack + 0.3, pop_fn(j, k_crack, magnifier), sfx="rim", gain=0.6)
BO8 = (cx + 440, cy + 340, 0.9)
b.custom(j, k_req, k_req + 0.3, L.figure(draw_boss, j, k_req, *BO8, mood="flat",
                                         rh=lambda T: (BO8[0] - 40, BO8[1] - 290 * BO8[2] + 20)), sfx="wood_high")
b.custom(j, k_req, k_req + 0.3, L.pop_bubble("要求改了", cx + 350, cy - 300, j, k_req, 70, RED, tail=1))
b.text(j, k_req + 0.4, k_req + 0.7, "领导", BO8[0], BO8[1] + 85, 64, BLACK)
b.path(j, k_x8, k_x8 + 0.4, cross(cx - 130, cy + 130, 230), RED, 15, sfx="kick", gain=0.8)
b.shots[j].shake = [(k_x8, 12.0)]
b.custom(j, k_mess, k_mess + 0.3, L.slam_text("越多越乱", cx - 90, cy + 510, 110, RED, j, k_mess), sfx="rim")

# ================================================================ 屏 9：领导随口一句，小李连夜做三版，第二天方向换了
cx, cy = R[9]
j = L.scene(9, (cx, cy + 20, Z))
BO9 = (cx - 430, cy + 340, 0.9)
LI9 = (cx + 470, cy + 340, 0.9)
DK9 = (cx + 170, cy + 200)
k_yan = kb(j, wt(14, 1, 0.6), lo=1)
k_bo9 = kb(j, wt(15, 0, 0.1), lo=k_yan + 1)
k_night = kb(j, wt(15, 1, 0.1), lo=k_bo9 + 1)
k_d1 = kb(j, wt(15, 1, 0.55), lo=k_night + 1)
k_chg = kb(j, wt(15, 3, 0.2), lo=k_d1 + 3)
k_bin = k_chg + 1


def eye9(c, sc, T):
    cx, cy = R[9]
    x, y = cx, cy - 470
    with at_pop(c, x, y, sc):
        c.drawPath(P((x - 90, y), (x - 45, y - 40), (x + 45, y - 40), (x + 90, y), (x + 45, y + 40), (x - 45, y + 40),
                     close=True), wb.marker(BLACK, 8))
        c.drawCircle(x, y, 26, K.paint(BLACK))
        K.text(c, "眼熟？", x + 220, y, 72, "hand", RED)


L.note("眼熟？")
b.custom(j, k_yan, k_yan + 0.3, pop_fn(j, k_yan, eye9), sfx="pop")
b.custom(j, k_bo9, k_bo9 + 0.3, L.figure(draw_boss, j, k_bo9, *BO9, mood="smile",
                                         lh=lambda T: (BO9[0] + 40, BO9[1] - 290 * BO9[2] + 40)), sfx="wood_high")
b.custom(j, k_bo9, k_bo9 + 0.3, L.pop_bubble("做个方案？", cx - 330, cy - 160, j, k_bo9, 62, BLACK, tail=-1,
                                             until=(j, k_chg - 0.3)))
b.text(j, k_bo9 + 0.4, k_bo9 + 0.7, "领导", BO9[0], BO9[1] + 85, 64, BLACK)
b.path(j, k_night - 0.9, k_night - 0.1, join(P((DK9[0] - 190, DK9[1]), (DK9[0] + 190, DK9[1])),
                                              P((DK9[0] - 170, DK9[1]), (DK9[0] - 170, DK9[1] + 140)),
                                              P((DK9[0] + 170, DK9[1]), (DK9[0] + 170, DK9[1] + 140))), BLACK, 9)


def night9(c, sc, T):
    cx, cy = R[9]
    lx, ly = DK9[0] - 150, DK9[1]
    with at_pop(c, lx, ly, sc):
        cone = P((lx + 40, ly - 150), (lx + 230, ly - 4), (lx - 20, ly - 4), close=True)
        c.drawPath(cone, K.paint("#FFE9A8", 0.6))
        c.drawPath(P((lx - 30, ly), (lx, ly - 100), (lx + 40, ly - 150)), wb.marker(BLACK, 8))
        c.drawPath(P((lx + 10, ly - 180), (lx + 75, ly - 140), (lx + 40, ly - 120), close=True), K.paint(BLACK))
    mx, my = cx + 450, cy - 300
    with at_pop(c, mx, my, sc):
        m = skia.Path()
        m.addCircle(mx, my, 60)
        m2 = skia.Path()
        m2.addCircle(mx + 30, my - 18, 52)
        moon = skia.Op(m, m2, skia.PathOp.kDifference_PathOp)
        c.drawPath(moon, K.paint("#FFE08A"))
        c.drawPath(moon, wb.marker(ORANGE, 6))


b.custom(j, k_night, k_night + 0.3, pop_fn(j, k_night, night9), sfx="ding", gain=0.6)
b.custom(j, k_night, k_night + 0.3, L.figure(draw_li, j, k_night, *LI9,
                                             mood=lambda T: "sad" if T >= tb(9, k_chg) else "flat",
                                             lh=lambda T: (LI9[0] - 120, LI9[1] - 290 * LI9[2] + 150 + 12 * math.sin(T * 14))))
b.text(j, k_night + 0.4, k_night + 0.7, "小李", LI9[0], LI9[1] + 85, 64, BLACK)
D9 = [(DK9[0] - 100 + i * 115, DK9[1] - 230) for i in range(3)]
BIN9 = (cx - 110, cy + 340)


def docs9(c, kk, T):
    t_bin = tb(9, k_bin)
    for i, (x, y) in enumerate(D9):
        t0 = tb(9, k_d1 + i)
        f = pop_scale(T - t0)
        if f <= 0:
            continue
        rot = (i - 1) * 6
        if T >= t_bin:
            g = ease_in_out(clamp01((T - t_bin - i * 0.08) / 0.45))
            x = lerp(x, BIN9[0], g)
            y = lerp(y, BIN9[1] - 150, g) - math.sin(g * math.pi) * 120
            rot += 200 * g
            f *= lerp(1.0, 0.55, g)
            if g >= 1:
                continue
        with K.at(c, x, y, rot, f):
            paper(c, 0, 0, 120, 150)
            K.text(c, str(i + 1), 0, 10, 70, "hand", BLUE)
    if T >= t_bin - 0.6:
        f = pop_scale(T - (t_bin - 0.6))
        with at_pop(c, BIN9[0], BIN9[1], f):
            c.drawPath(P((BIN9[0] - 70, BIN9[1] - 150), (BIN9[0] - 55, BIN9[1]), (BIN9[0] + 55, BIN9[1]),
                         (BIN9[0] + 70, BIN9[1] - 150)), wb.marker(BLACK, 9))
            c.drawLine(BIN9[0] - 85, BIN9[1] - 150, BIN9[0] + 85, BIN9[1] - 150, wb.marker(BLACK, 9))
            for dx in (-25, 0, 25):
                c.drawLine(BIN9[0] + dx, BIN9[1] - 125, BIN9[0] + dx * 0.8, BIN9[1] - 20, wb.marker(BLACK, 5))
    return None


L.note("1", "2", "3")
b.custom(j, k_d1, k_d1 + 0.3, docs9, sfx="pop")
b.hit(j, k_d1 + 1, "pop", 0.8, "第二版")
b.hit(j, k_d1 + 2, "pop", 0.8, "第三版")
b.custom(j, k_chg, k_chg + 0.3, L.pop_bubble("方向换了", cx - 330, cy - 160, j, k_chg, 70, RED, tail=-1), sfx="rim")
b.hit(j, k_bin, "tom", 0.85, "三版方案一起进垃圾桶")

# ================================================================ 屏 10：周报五页，开会没人翻到第二页
cx, cy = R[10]
j = L.scene(10, (cx, cy + 20, Z))
PG = [(cx - 330 + i * 26, cy - 140 - i * 26) for i in range(5)]
k_pg = kb(j, wt(16, 0, 0.2), lo=1)
k_meet = kb(j, wt(16, 1, 0.2), lo=k_pg + 3)
k_none = kb(j, wt(16, 2, 0.6), lo=k_meet + 1)
TB10 = (cx + 150, cy + 250)


def pages10(c, kk, T):
    dust = T >= tb(10, k_none)
    for i in range(4, -1, -1):
        t0 = tb(10, k_pg) + i * 0.27
        f = pop_scale(T - t0, 0.25)
        if f <= 0:
            continue
        x, y = PG[i]
        with K.at(c, x, y, -3 + i, f):
            paper(c, 0, 0, 230, 290, lines=5, fill="#ECEEF2" if dust and i > 0 else "#FFFFFF",
                  color="#9AA0AC" if dust and i > 0 else BLACK)
            if i == 0:
                K.text(c, "周报", -10, -118, 50, "hand", BLUE)
    if dust:
        g = clamp01((T - tb(10, k_none)) / 0.4)
        for n in range(16):
            x = PG[4][0] - 90 + (n * 47) % 190
            y = PG[4][1] - 120 + (n * 31) % 90
            c.drawCircle(x, y, 5, K.paint("#9AA0AC", 0.8 * g))
    return None


L.note("周报")
b.custom(j, k_pg, k_pg + 0.3, pages10, sfx="wood_high")
b.custom(j, k_pg + 2, k_pg + 2.3, L.pop_text("5页", cx + 200, cy - 330, 96, RED, j, k_pg + 2), sfx="pop")


def meeting10(c, sc, T):
    x, y = TB10
    with at_pop(c, x, y, sc):
        for i, dx in enumerate((-220, 0, 220)):
            px, py, s = x + dx, y + 40, 0.75
            look = 8 * math.sin((T - tb(10, k_meet)) * 2 + i)
            c.save()
            c.translate(look, 0)
            draw_li(c, px, py, s, "flat") if i == 1 else draw_wang(c, px, py, s) if i == 0 else draw_boss(c, px, py, s)
            c.restore()
        oval = skia.Rect.MakeXYWH(x - 330, y - 70, 660, 140)
        c.drawOval(oval, K.paint("#F3E6CF"))
        c.drawOval(oval, wb.marker("#A9773E", 8))


b.custom(j, k_meet, k_meet + 0.3, pop_fn(j, k_meet, meeting10), sfx="wood_low")
b.text(j, k_meet + 0.4, k_meet + 1.0, "开会", TB10[0], TB10[1] + 150, 66, BLACK)
b.hit(j, k_none, "rim", 0.8, "后四页落灰")
b.custom(j, k_none + 1, k_none + 1.3, L.pop_text("没人翻", cx + 230, cy - 160, 80, RED, j, k_none + 1), sfx="pop", gain=0.6)

# ================================================================ 屏 11：下周的表格先做了，周一模板一改，全部重来
cx, cy = R[11]
j = L.scene(11, (cx, cy + 20, Z))
LI11 = (cx - 400, cy + 340, 0.9)
SHEET = (cx + 60, cy + 60)
k_fri = kb(j, wt(17, 0, 0.3), lo=1)
k_tab = kb(j, wt(17, 1, 0.4), lo=k_fri + 1)
k_mon = kb(j, wt(17, 2, 0.2), lo=k_tab + 2)
k_tpl = kb(j, wt(17, 2, 0.75), lo=k_mon + 1)
k_redo11 = kb(j, wt(17, 3, 0.4), lo=k_tpl + 1)


def cal_page(x, y, day, color):
    def draw(c, sc, T):
        with at_pop(c, x, y, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 95, y - 85, 190, 170), 14, 14, K.paint("#FFFFFF"))
            c.drawRect(skia.Rect.MakeXYWH(x - 95, y - 85, 190, 48), K.paint(color))
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 95, y - 85, 190, 170), 14, 14, wb.marker(BLACK, 8))
            for dx in (-45, 45):
                c.drawLine(x + dx, y - 105, x + dx, y - 70, wb.marker(BLACK, 8))
            K.text(c, day, x, y + 25, 64, "hand", BLACK)
    return draw


L.note("周五", "周一")
b.custom(j, k_fri, k_fri + 0.3, pop_fn(j, k_fri, cal_page(cx - 330, cy - 360, "周五", "#BFD5F2")), sfx="pop")
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI11, mood=lambda T: "sad" if T >= tb(11, k_redo11) else "smile",
                             rh=lambda T: (LI11[0] + 120, LI11[1] - 290 * LI11[2] + 120 + (8 * math.sin(T * 16)
                                                                                         if tb(11, k_tab) <= T < tb(11, k_mon) else 0))),
         sfx="wood_high")
b.text(j, 1.4, 1.7, "小李", LI11[0], LI11[1] + 85, 64, BLACK)


def sheet11(c, kk, T):
    t0 = tb(11, k_tab)
    x, y = SHEET
    f = clamp01((T - t0) / 0.9)
    gray = T >= tb(11, k_redo11)
    col = "#9AA0AC" if gray else BLACK
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 220, y - 150, 440, 300), 12, 12, K.paint("#FFFFFF"))
    parts = [rect(x, y, 440, 300, 12)]
    for i in range(1, 4):
        parts.append(P((x - 220, y - 150 + i * 75), (x + 220, y - 150 + i * 75)))
    for i in range(1, 3):
        parts.append(P((x - 220 + i * 147, y - 150), (x - 220 + i * 147, y + 150)))
    path = join(*parts)
    part, tip = wb.partial(path, f)
    c.drawPath(part, wb.marker(col, 7))
    if f >= 1:
        c.drawRect(skia.Rect.MakeXYWH(x - 216, y - 146, 432, 71), K.paint("#BFD5F2" if not gray else "#E3E6EA", 0.8))
    return tip


b.custom(j, k_tab, k_tab + 0.9, sheet11, sfx="wood_low")
b.path(j, k_tab + 1, k_tab + 1.4, check(SHEET[0] + 270, SHEET[1] - 40, 40), GREEN, 12, sfx="pop", gain=0.6)
b.path(j, k_mon - 0.6, k_mon - 0.1, arrow((cx - 210, cy - 360), (cx + 170, cy - 360), 0, 32), BLACK, 8)
b.custom(j, k_mon, k_mon + 0.3, pop_fn(j, k_mon, cal_page(cx + 300, cy - 360, "周一", "#F6C3BE")), sfx="pop")


def notice11(c, sc, T):
    cx, cy = R[11]
    x, y = cx + 300, cy - 200
    with K.at(c, x, y, wobble(T - tb(11, k_tpl), 5, 30, 6), sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(-170, -48, 340, 96), 18, 18, K.paint("#FFFFFF"))
        c.drawRoundRect(skia.Rect.MakeXYWH(-170, -48, 340, 96), 18, 18, wb.marker(RED, 8))
        K.text(c, "模板改了", 12, 0, 62, "hand", RED)
        c.drawCircle(-140, -40, 18, K.paint(RED))


L.note("模板改了")
b.custom(j, k_tpl, k_tpl + 0.3, pop_fn(j, k_tpl, notice11), sfx="rim")
b.path(j, k_redo11, k_redo11 + 0.4, cross(SHEET[0], SHEET[1], 130), RED, 14, sfx="kick", gain=0.75)
b.path(j, k_redo11 + 0.5, k_redo11 + 1.0, C.loop_arrow(SHEET[0] + 300, SHEET[1] + 105, 50), ORANGE, 11)
b.custom(j, k_redo11 + 1, k_redo11 + 1.3, L.pop_text("重来", SHEET[0] + 300, SHEET[1] + 225, 72, ORANGE, j, k_redo11 + 1),
         sfx="pop", gain=0.6)
b.shots[j].shake = [(k_redo11, 10.0)]

# ================================================================ 屏 12：抢着多做，怕被说不够努力——多做的都变成了加班
cx, cy = R[12]
j = L.scene(12, (cx, cy + 20, Z))
LI12 = (cx - 330, cy + 340, 0.95)
CLK = (cx + 250, cy - 170, 150)
k_run = 1
k_fear = kb(j, wt(18, 1, 0.3), lo=2)
k_fly = kb(j, wt(19, 0, 0.5), lo=k_fear + 1)
k_ot = kb(j, wt(19, 1, 0.7), lo=k_fly + 2)


def li12(c, kk, T):
    x, y, s = LI12
    sc = pop_scale(T - tb(12, k_run))
    if sc <= 0:
        return None
    t_fly = tb(12, k_fly)
    run = 1.0 - ease_in_out(clamp01((T - t_fly) / 0.5))
    bob = -abs(math.sin((T - tb(12, k_run)) * 7)) * 14 * run
    hy = y - 290 * s
    with at_pop(c, x, y, sc):
        c.translate(0, bob)
        draw_li(c, x, y, s, "flat" if run > 0.5 else "sad", lh=(x - 75 * s, hy + 150 * s), rh=(x + 75 * s, hy + 150 * s))
        for i in range(3):                                     # 抱着三箱；飞向钟面
            g = ease_in_out(clamp01((T - t_fly - i * 0.12) / 0.6))
            if g >= 1:
                continue
            bx = lerp(x + (i % 2) * 8, CLK[0], g)
            by = lerp(hy + 150 * s - i * 88, CLK[1], g) - math.sin(g * math.pi) * 120
            with K.at(c, bx, by, 180 * g, 1 - 0.8 * g):
                box(c, 0, 45, 140, 84)
        if run > 0.05:
            for i in range(3):
                yy = y - 220 * s + i * 50
                c.drawLine(x - 110 - i * 10, yy, x - 170 - i * 10, yy, wb.marker(BLACK, 6, 0.7 * run))
    return None


b.custom(j, k_run, k_run + 0.3, li12, sfx="bongo_low")
b.text(j, k_run + 0.4, k_run + 0.7, "小李", LI12[0], LI12[1] + 85, 64, BLACK)


def fear12(c, sc, T):
    cx, cy = R[12]
    x, y = LI12[0] + 60, cy - 330
    with at_pop(c, x, y, sc):
        for (dx, dy, r) in ((-80, 150, 14), (-60, 115, 22)):
            c.drawCircle(x + dx, y + dy, r, K.paint("#FFFFFF"))
            c.drawCircle(x + dx, y + dy, r, wb.marker("#8A8F99", 6))
        oval = skia.Rect.MakeXYWH(x - 210, y - 80, 420, 160)
        c.drawOval(oval, K.paint("#FFFFFF"))
        c.drawOval(oval, wb.marker("#8A8F99", 7))
        K.text(c, "不够努力？", x, y, 66, "hand", "#6B7080")


L.note("不够努力？")
b.custom(j, k_fear, k_fear + 0.3, pop_fn(j, k_fear, fear12), sfx="pop", gain=0.7)


def clock12(c, kk, T):
    x, y, r = CLK
    t0 = tb(12, k_fly) + 0.4
    f = ease_in_out(clamp01((T - t0) / (tb(12, k_ot) - t0)))
    hour = 18 + 3 * f
    c.drawCircle(x, y, r, K.paint("#FFFFFF"))
    c.drawPath(wb.clock(x, y, r), wb.marker(BLACK, 9))
    c.drawPath(wb.hands_at(x, y, r, hour % 12, (hour * 60) % 60), wb.marker(RED if f > 0 else BLACK, 9))
    K.text(c, f"{int(hour):02d}:{int((hour * 60) % 60):02d}", x, y + r + 60, 64, "sans_medium", RED if f >= 1 else BLACK)
    return None


L.note("18:00", "21:00")
b.path(j, 0.4, 1.0, wb.clock(*CLK), BLACK, 9, sfx="wood_high")
b.custom(j, 1.0, 1.1, clock12)
b.hit(j, k_fly, "shaker", 0.7, "多做的箱子飞向钟面")
b.custom(j, k_ot, k_ot + 0.3, L.slam_text("加班", CLK[0], cy + 230, 140, RED, j, k_ot), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_ot, 14.0)]

# ================================================================ 屏 13：谁都不想被问“怎么还没好？”——试试这三步
cx, cy = R[13]
j = L.scene(13, (cx, cy + 20, Z))
LI13 = (cx - 300, cy + 340, 0.95)
BO13 = (cx + 380, cy + 340, 0.95)
k_heart = kb(j, wt(20, 0, 0.5), lo=1)
k_ask = kb(j, wt(20, 1, 0.75), lo=k_heart + 1)
k_three = kb(j, wt(21, 1, 0.5), lo=k_ask + 2)
k_away = k_three - 1


def li13(c, kk, T):
    x, y, s = LI13
    sc = pop_scale(T - tb(13, 1))
    if sc <= 0:
        return None
    dt = T - tb(13, k_ask)
    sq = 1.0
    if dt >= 0:
        sq = lerp(1.0, 0.86, ease_out(clamp01(dt / 0.15))) + 0.04 * math.exp(-dt * 6) * math.sin(dt * 25)
        sq = lerp(sq, 1.0, ease_in_out(clamp01((T - tb(13, k_three)) / 0.4)))
    mood = "smile" if T >= tb(13, k_three) else ("sad" if dt >= 0 else "flat")
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, mood, squash=sq)
    if 0 <= dt and T < tb(13, k_three):
        a = clamp01(dt / 0.2)
        c.drawPath(heart_drop(x + 70, y - 330 * s * sq), K.paint("#BFD5F2", a))
        c.drawPath(heart_drop(x + 70, y - 330 * s * sq), wb.marker(BLUE, 5, a))
    return None


def heart_drop(x, y):
    p = skia.Path()
    p.moveTo(x, y - 30)
    p.quadTo(x + 22, y, x, y + 14)
    p.quadTo(x - 22, y, x, y - 30)
    return p


b.custom(j, 1, 1.3, li13, sfx="wood_high")
b.text(j, 1.4, 1.7, "小李", LI13[0], LI13[1] + 85, 64, BLACK)


def heart13(c, sc, T):
    cx, cy = R[13]
    g = 1 - ease_in_out(clamp01((T - tb(13, k_away)) / 0.3))
    x, y = LI13[0], cy - 160
    with at_pop(c, x, y, sc * g):
        hp = C.heart_path(x, y, 62)
        c.drawPath(hp, K.paint("#F8D3CF"))
        c.drawPath(hp, wb.marker(RED, 9))


b.custom(j, k_heart, k_heart + 0.3, pop_fn(j, k_heart, heart13), sfx="ding", gain=0.7)
b.custom(j, k_ask - 1, k_ask - 0.7, L.figure(draw_boss, j, k_ask - 1, *BO13, mood="flat",
                                             lh=lambda T: (BO13[0] - 60, BO13[1] - 290 * BO13[2] + 70)), sfx="wood_low")
b.text(j, k_ask - 0.6, k_ask - 0.3, "领导", BO13[0], BO13[1] + 85, 64, BLACK)
b.custom(j, k_ask, k_ask + 0.3, L.pop_bubble("怎么还没好？", cx + 250, cy - 140, j, k_ask, 64, RED, tail=1,
                                             until=(j, k_away)), sfx="rim")
b.custom(j, k_three, k_three + 0.3, L.slam_text("试试这三步", cx + 40, cy - 330, 110, RED, j, k_three), sfx="kick", gain=0.8)
for i in range(3):
    kk_ = k_three + 1 + i
    b.custom(j, kk_, kk_ + 0.3, L.pop_path(join(circle(cx - 200 + i * 240, cy - 130, 62)), cx - 200 + i * 240, cy - 130,
                                           BLUE, 9, j, kk_, fill="#E4EDFA"), sfx="pop", gain=0.6)
    b.custom(j, kk_, kk_ + 0.3, L.pop_text(str(i + 1), cx - 200 + i * 240, cy - 130, 80, BLUE, j, kk_))

# ================================================================ 屏 14：第一，开工前问一句：这个谁用，什么时候用？
cx, cy = R[14]
j = L.scene(14, (cx, cy + 20, Z))
LI14 = (cx - 330, cy + 340, 0.95)
WK14 = (cx + 360, cy + 340, 0.95)
b.custom(j, 0, 0.3, L.pop_text("① 先问一句", cx, cy - 470, 92, BLUE, j, 0), sfx="pop")
k_hand = kb(j, wt(22, 1, 0.2), lo=1)
k_who = kb(j, wt(22, 1, 0.75), lo=k_hand + 1)
k_when = kb(j, wt(22, 2, 0.4), lo=k_who + 1)
k_ans = k_when + 1


def li14(c, kk, T):
    x, y, s = LI14
    hy = y - 290 * s
    up = ease_out(clamp01((T - tb(14, k_hand)) / 0.25))
    rh = (lerp(x + 70 * s, x + 95 * s, up), lerp(hy + 170 * s, hy - 70 * s, up))
    draw_li(c, x, y, s, "smile" if T >= tb(14, k_ans) else "flat", rh=rh)
    return None


def li14_pop(c, kk, T):
    x, y, s = LI14
    sc = pop_scale(T - tb(14, 1))
    if sc > 0:
        with at_pop(c, x, y, sc):
            li14(c, 0, T)
    return None


b.custom(j, 1, 1.3, li14_pop, sfx="wood_high")

b.text(j, 1.4, 1.7, "小李", LI14[0], LI14[1] + 85, 64, BLACK)
b.hit(j, k_hand, "shaker", 0.6, "小李举手")


def ask14(c, kk, T):
    cx, cy = R[14]
    x, y = cx - 220, cy - 210
    sc = pop_scale(T - tb(14, k_who))
    if sc <= 0:
        return None
    w, h = 520, 230
    with at_pop(c, x, y, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 40, 40, K.paint("#FFFFFF"))
        c.drawPath(wb.bubble(x, y, w, h, -1), wb.marker(BLACK, 7))
        K.text(c, "谁用？", x, y - 48, 70, "hand", BLUE)
        a = clamp01(pop_scale(T - tb(14, k_when)))
        if a > 0:
            K.text(c, "什么时候用？", x, y + 50, 70, "hand", BLUE, a)
    return None


L.note("谁用？", "什么时候用？")
b.custom(j, k_who, k_who + 0.3, ask14, sfx="pop")
b.hit(j, k_when, "pop", 0.7, "第二问")
b.custom(j, k_hand, k_hand + 0.3, L.figure(draw_wang, j, k_hand, *WK14, mood=lambda T: "smile" if T >= tb(14, k_ans) else "flat"))
b.text(j, k_hand + 0.4, k_hand + 0.8, "同事小王", WK14[0], WK14[1] + 85, 64, BLUE)
b.custom(j, k_ans, k_ans + 0.3, L.pop_bubble("周三要", cx + 330, cy - 170, j, k_ans, 70, GREEN, tail=1), sfx="ding")

# ================================================================ 屏 15：第二，先交一小版，对方点头了再往下做
cx, cy = R[15]
j = L.scene(15, (cx, cy + 20, Z))
LI15 = (cx - 360, cy + 340, 0.95)
BO15 = (cx + 380, cy + 340, 0.95)
b.custom(j, 0, 0.3, L.pop_text("② 先交小版", cx, cy - 470, 92, BLUE, j, 0), sfx="pop")
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI15, mood="smile",
                             rh=lambda T: ((LI15[0] + 130, LI15[1] - 290 * LI15[2] + 110) if tb(15, k_give) - 0.4 <= T < tb(15, k_give) + 0.5
                                           else (LI15[0] + 70 * LI15[2], LI15[1] - 120 * LI15[2])), ), sfx="wood_high")
k_give = kb(j, wt(23, 1, 0.6), lo=2)
k_nod = kb(j, wt(23, 2, 0.3), lo=k_give + 1)
k_next = kb(j, wt(23, 2, 0.85), lo=k_nod + 1)
b.text(j, 1.4, 1.7, "小李", LI15[0], LI15[1] + 85, 64, BLACK)
b.custom(j, 1.5, 1.8, L.figure(draw_boss, j, 2, *BO15, mood=lambda T: "smile" if T >= tb(15, k_nod) else "flat",
                               head_dy=lambda T: 12 * math.sin(clamp01((T - tb(15, k_nod)) / 0.7) * math.pi * 2),
                               lh=lambda T: (BO15[0] - 110, BO15[1] - 290 * BO15[2] + 120)))
b.hit(j, 2, "wood_low", 0.7, "领导出现")
b.text(j, 2.4, 2.7, "领导", BO15[0], BO15[1] + 85, 64, BLACK)


def small_doc(c, kk, T):
    t0 = tb(15, k_give)
    if T < t0 - 0.4:
        return None
    g = ease_in_out(clamp01((T - t0) / 0.5))
    x = lerp(LI15[0] + 150, BO15[0] - 140, g)
    y = lerp(LI15[1] - 290 * LI15[2] + 90, BO15[1] - 290 * BO15[2] + 90, g) - math.sin(g * math.pi) * 140
    with K.at(c, x, y, -8 + 16 * g, pop_scale(T - (t0 - 0.4))):
        paper(c, 0, 0, 90, 115, lines=3)
    return None


b.custom(j, k_give, k_give + 0.3, small_doc, sfx="pop")
b.custom(j, k_give, k_give + 0.3, L.pop_text("小版", cx + 60, cy + 140, 70, ORANGE, j, k_give))
b.path(j, k_nod, k_nod + 0.4, check(BO15[0] + 20, cy - 150, 52), GREEN, 14, sfx="ding")


def next15(c, sc, T):
    cx, cy = R[15]
    x, y = LI15[0] + 20, cy - 220
    with at_pop(c, x, y, sc):
        paper(c, x, y, 150, 190, lines=5)
    with at_pop(c, x + 150, y - 40, sc):
        c.drawPath(arrow((x + 110, y + 40), (x + 190, y - 70), 0, 26), wb.marker(GREEN, 9))


b.custom(j, k_next, k_next + 0.3, pop_fn(j, k_next, next15), sfx="wood_high")

# ================================================================ 屏 16：第三，桌上贴一张小卡片，只写下一步要交的那一件
cx, cy = R[16]
j = L.scene(16, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("③ 贴张卡片", cx, cy - 470, 92, BLUE, j, 0), sfx="pop")
DK16 = (cx + 80, cy + 180)
MON = (cx + 80, cy - 40, 360, 230)
b.path(j, 1, 1.8, join(P((DK16[0] - 300, DK16[1]), (DK16[0] + 300, DK16[1])),
                       P((DK16[0] - 270, DK16[1]), (DK16[0] - 270, DK16[1] + 150)),
                       P((DK16[0] + 270, DK16[1]), (DK16[0] + 270, DK16[1] + 150)),
                       rect(MON[0], MON[1], MON[2], MON[3], 14), P((MON[0], MON[1] + 115), (MON[0], DK16[1])),
                       P((MON[0] - 60, DK16[1]), (MON[0] + 60, DK16[1]))), BLACK, 9, sfx="wood_high")
LI16 = (cx - 410, cy + 340, 0.9)
k_stick = kb(j, wt(24, 1, 0.7), lo=2)
k_write = kb(j, wt(24, 2, 0.4), lo=k_stick + 1)
k_echo = k_write + 2
b.custom(j, 2, 2.3, L.figure(draw_li, j, 2, *LI16, mood="smile",
                             rh=lambda T: (LI16[0] + 140, LI16[1] - 290 * LI16[2] + 60) if T >= tb(16, k_stick) - 0.3
                             else (LI16[0] + 70 * LI16[2], LI16[1] - 120 * LI16[2])), sfx="pop")
b.text(j, 2.4, 2.7, "小李", LI16[0], LI16[1] + 85, 64, BLACK)
NOTE = (MON[0] - 50, MON[1] - 10)


def note16(c, kk, T):
    t0 = tb(16, k_stick)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    with K.at(c, NOTE[0], NOTE[1], -4, sc):
        c.drawRect(skia.Rect.MakeXYWH(-130, -80, 260, 160), K.paint("#FFE9A8"))
        c.drawRect(skia.Rect.MakeXYWH(-130, -80, 260, 160), wb.marker(ORANGE, 7))
        c.drawRect(skia.Rect.MakeXYWH(-130, -80, 260, 26), K.paint("#F6D27A"))
        a1 = clamp01((T - tb(16, k_write)) / 0.3)
        a2 = clamp01((T - tb(16, k_write) - 0.5) / 0.4)
        K.text(c, "下一件", 0, -18, 50, "hand", RED, a1)
        K.text(c, "周三交周报", 0, 42, 44, "hand", BLACK, a2)
    return None


L.note("下一件", "周三交周报")
b.custom(j, k_stick, k_stick + 0.3, note16, sfx="clap")
b.hit(j, k_write, "pop", 0.7, "卡片上写下一件")


def echo16(c, sc, T):
    cx, cy = R[16]
    x, y = cx + 400, cy - 330
    with at_pop(c, x, y, sc):
        card_draw(c, x, y, 1.4)
        K.text(c, "像车间看板", x, y - 80, 46, "hand", "#6B7080")
    p = K.paint("#9AA0AC", clamp01(sc), 6)
    p.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
    c.drawPath(arrow((x - 70, y + 30), (NOTE[0] + 140, NOTE[1] - 60), 0.15, 24), p)


L.note("像车间看板")
b.custom(j, k_echo, k_echo + 0.3, pop_fn(j, k_echo, echo16), sfx="ding", gain=0.6)

# ================================================================ 屏 17：少做白做的，你就能准点走
cx, cy = R[17]
j = L.scene(17, (cx, cy + 20, Z))
k_less = kb(j, wt(25, 0, 0.3), lo=1)
k_clock = kb(j, wt(25, 1, 0.1), lo=k_less + 1)
k_go17 = k_clock + 1


def pile17(c, sc, T):
    cx, cy = R[17]
    for i, (dx, dy) in enumerate(((-80, 0), (80, 0), (0, -100))):
        x, y = cx - 360 + dx, cy + 340 + dy
        with at_pop(c, x, y, sc):
            box(c, x, y, 140, 96, fill="#E9EDF3", color="#8A8F99")


b.custom(j, k_less, k_less + 0.3, pop_fn(j, k_less, pile17), sfx="wood_low")
b.path(j, k_less + 0.4, k_less + 0.9, cross(cx - 360, cy + 240, 130), RED, 13, sfx="rim", gain=0.0)
b.path(j, k_clock, k_clock + 0.6, join(wb.clock(cx - 280, cy - 300, 120), wb.hands_at(cx - 280, cy - 300, 120, 6, 0)), BLACK, 9,
       sfx="ding")
b.text(j, k_clock + 0.6, k_clock + 1.0, "18:00", cx - 280, cy - 120, 66, RED)
DOOR = (cx + 400, cy + 160)
b.path(j, 0, 0.8, join(rect(DOOR[0], DOOR[1], 220, 360, 10), circle(DOOR[0] - 70, DOOR[1] + 10, 11)), BLACK, 8, sfx="wood_high")


def home17(c, kk, T):
    cx, cy = R[17]
    t0 = tb(17, k_go17)
    if T < tb(17, 1):
        return None
    sc = pop_scale(T - tb(17, 1))
    x, dy, moving = walk(T, t0, 1.4, cx - 150, cx + 170, 14)
    s = 0.9
    y = cy + 340
    hy = y - 290 * s
    wave = ease_out(clamp01((T - t0 - 1.4) / 0.3))
    rh = (x + 90 * s, lerp(hy + 170 * s, hy - 60 * s, wave) + 14 * math.sin(T * 9) * wave)
    with at_pop(c, x, y, sc):
        c.translate(0, dy)
        draw_li(c, x, y, s, "smile", bag=True, rh=rh)
    return None


b.custom(j, 1, 1.3, home17, sfx="pop")
b.hit(j, k_go17, "bongo_low", 0.8, "小李背包往门口走")
b.custom(j, k_go17 + 2, k_go17 + 2.3, L.pop_text("准点走", cx + 150, cy - 320, 100, BLUE, j, k_go17 + 2), sfx="ding", gain=0.8)

# ================================================================ 屏 18：评论区见 + 下一讲预告
cx, cy = R[18]
j = L.scene(18, (cx, cy + 20, Z))
b.path(j, 0, 0.8, wb.bubble(cx, cy - 360, 1000, 280, -1), BLACK, 9, sfx="wood_high")
k_c1 = kb(j, wt(26, 0, 0.2), lo=1)
b.text(j, k_c1, k_c1 + 1.3, "你最近做过最白费的一件事", cx, cy - 410, 66, RED, sfx="pop")
b.text(j, k_c1 + 1.3, k_c1 + 1.8, "是什么？", cx, cy - 310, 66, RED)
k_av = kb(j, wt(27, 0, 0.3), lo=k_c1 + 2)
AV = [(cx - 330, cy - 70, draw_li), (cx - 110, cy - 70, draw_worker), (cx + 110, cy - 70, draw_li), (cx + 330, cy - 70, draw_worker)]
for i, (x, y, fn) in enumerate(AV):
    def av(c, sc, T, x=x, y=y, fn=fn, i=i):
        with at_pop(c, x, y, sc):
            c.drawCircle(x, y, 78, K.paint(("#E4EDFA", "#FBE3C8", "#DCEFD9", "#F8D3CF")[i]))
            c.save()
            c.clipRect(skia.Rect.MakeXYWH(x - 78, y - 78, 156, 156))
            fn(c, x, y + 150, 0.62) if fn is draw_worker else fn(c, x, y + 150, 0.62, "smile")
            c.restore()
    b.custom(j, k_av + i * 0.5, k_av + i * 0.5 + 0.3, pop_fn(j, k_av + i * 0.5, av), sfx="pop" if i % 2 == 0 else None, gain=0.6)
k_help = kb(j, wt(27, 1, 0.2), lo=k_av + 2)
b.custom(j, k_help, k_help + 0.3, L.pop_text("说出来，大家帮你避开", cx, cy + 70, 58, BLACK, j, k_help, "sans_medium"),
         sfx="ding")
# 2026-11 收尾鼓励（第 28 句）：镜头下移，小李把“下一件”卡片递给等着用的小王，小王点头；预告卡整体下移 DY
DY = 670
k_e = kb(j, wt(28, 0, 0.0), lo=k_help + 1)
b.move(j, k_e, (cx, cy + 740, Z), 1.1)
k_e1 = k_e + 2
k_give = kb(j, wt(28, 1, 0.15), lo=k_e1 + 1)
k_ok = kb(j, wt(28, 1, 0.8), lo=k_give + 1)
LI18, WG18 = (cx - 260, cy + 700, 0.8), (cx + 260, cy + 700, 0.8)


def give18(c, kk, T):
    """小李伸手递卡片，卡片飞到小王手里；小王点两下头、笑。"""
    (lx, ly, s), (wx, wy, _) = LI18, WG18
    sc = pop_scale(T - tb(18, k_e1))
    if sc <= 0:
        return None
    f = ease_in_out(clamp01((T - tb(18, k_give)) / 0.5))
    nod = T - tb(18, k_ok)
    head = 14 * abs(math.sin(nod * 2 * math.pi * 1.6)) if 0 <= nod < 0.65 else 0.0
    hy = ly - 290 * s
    li_rh = (lx + lerp(70, 150, min(1.0, f * 3)) * s, lerp(hy + 170 * s, hy + 110 * s, min(1.0, f * 3)))
    wg_lh = (wx - 150 * s, hy + 110 * s) if f > 0 else None
    with at_pop(c, cx, ly - 120, sc):
        draw_li(c, lx, ly, s, "smile", rh=li_rh)
        draw_wang(c, wx, wy, s, lh=wg_lh, mood="smile" if nod >= 0 else "flat", head_dy=head)
        x = lerp(li_rh[0] + 20, wx - 150 * s - 20, f)
        y = hy + 110 * s - 60 - 90 * math.sin(math.pi * f)
        r = skia.Rect.MakeXYWH(x - 85, y - 55, 170, 110)
        c.drawRoundRect(r, 10, 10, K.paint("#FFF4C2"))
        c.drawRoundRect(r, 10, 10, wb.marker(ORANGE, 6))
        K.text(c, "下一件", x, y, 44, "hand", BLACK)
    return None


L.note("下一件")
b.custom(j, k_e1, k_e1 + 0.3, give18, sfx="pop", gain=0.6)
b.hit(j, k_give, "wood_high", 0.7, "卡片递出去")
b.path(j, k_ok, k_ok + 0.5, check(WG18[0] + 150, WG18[1] - 330, 40), GREEN, 11, sfx="ding")
b.custom(j, k_ok + 1, k_ok + 1.3, L.pop_text("花在有人等的地方", cx, cy + 250, 64, BLUE, j, k_ok + 1), sfx="pop", gain=0.6)
k_n = kb(j, wt(29, 0, 0.2), lo=k_ok + 1)
b.path(j, k_n, k_n + 0.6, rect(cx, cy + 330 + DY, 1000, 260, 24), BLUE, 8, sfx="wood_high")
b.text(j, k_n + 0.5, k_n + 0.8, "下一讲", cx, cy + 245 + DY, 52, BLUE)
b.text(j, k_n + 0.8, k_n + 2.2, "为什么总是忙一阵闲一阵？", cx, cy + 330 + DY, 60, BLACK)
wave = skia.Path()
wave.moveTo(cx - 200, cy + 405 + DY)
for i in range(1, 41):
    wave.lineTo(cx - 200 + i * 10, cy + 405 + DY - 22 * math.sin(i / 40 * 4 * math.pi) * (1 if (i // 10) % 2 == 0 else 1.6))
b.path(j, k_n + 2.2, k_n + 3.0, wave, ORANGE, 7)

# ================================================================ 收尾
L.finish(cover_shot=4)
L.export(globals())
