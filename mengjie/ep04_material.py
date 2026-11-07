"""《梦的解析》04 梦的材料：怎么会梦见八百年没想起的人？（白板手绘 + AI 旁白，竖屏 2:3）

侦探追查：拿放大镜一路查梦里的东西从哪来。
- 开场：一张旧照片（戴红领巾的小学同学）、放大镜扫过、冒出“！”，配音“怎么是他”逐字砸下；
- 痛点：小李梦见小学同学，梦里还有路牌、杯子，清清楚楚；
- 身边的例子（drop 在第 2 屏）：上午路过奶茶店 → 梦里在那儿上班；梦见老家院子，墙上的裂缝都还在；
- 书中：弗洛伊德拿放大镜查“材料从哪来”，脚印通向“前一天”；植物学的书：梦里摊开 ↔ 前一天书店橱窗瞟到；
  聚光灯照着小杯子，“大事”被挡在台下；童年旧照片在梦里原样出现；前一天的小事像钩子，钩上很久以前的心事；
- 现在怎么看：前一两天的经历常入梦，一周左右又冒一次（柱状示意）；
- 三步：找钩子（日历上的三件小事）、找年份（身高尺）、问那时候（考第一 → 现在还在意吗）；梦变成旧照片；评论区与下一讲。
文案与出处见 mengjie/PLAN.md「### 04」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_li, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, NOTE_FILL, PAPER_W, WOOD, at_pop, bed, box, draw_freud, dream_cloud, moon,
                         sleeper, sparkle, star)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross

BROWN = "#A9773E"


# ================================================================ 本讲小元件

def kid(c, x, y, s, mood="smile", lh=None, rh=None):
    """小学生：小人 + 红领巾。(x, y) 为脚底。"""
    draw_li(c, x, y, s, mood, lh=lh, rh=rh)
    hy = y - 290 * s
    sc = P((x - 34 * s, hy + 52 * s), (x + 34 * s, hy + 52 * s), (x, hy + 110 * s), close=True)
    c.drawPath(sc, K.paint(RED))
    c.drawPath(sc, wb.marker(RED, 5))


def magnifier(c, x, y, r=120, rot=0.0, alpha=1.0):
    with K.at(c, x, y, rot):
        C.line(c, (r * 0.7, r * 0.7), (r * 1.4, r * 1.4), BROWN, r * 0.16, alpha)
        c.drawCircle(0, 0, r, K.paint("#FFFFFF", 0.35 * alpha))
        c.drawCircle(0, 0, r, wb.marker(BLACK, 9, alpha))


def photo(c, x, y, w, h, rot=0.0, s_kid=0.5, sepia=True):
    """旧照片：白边 + 泛黄底 + 一个戴红领巾的孩子。"""
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, PAPER_W, GRAY, 5, 4)
        box(c, 0, -h * 0.08, w - 30, h * 0.72, "#F3E2B8" if sepia else "#DCE6F2", BROWN, 3, 2)
        kid(c, 0, -h * 0.08 + h * 0.36 - 6, s_kid)


def cup(c, x, y, s=1.0, straw=True):
    """奶茶杯：(x, y) 为杯底中心。"""
    with K.at(c, x, y, 0, s):
        c.drawPath(P((-45, 0), (45, 0), (55, -140), (-55, -140), close=True), K.paint("#F1D9B5"))
        c.drawPath(P((-45, 0), (45, 0), (55, -140), (-55, -140), close=True), wb.marker(BROWN, 6))
        for dx in (-20, 5, 25):
            c.drawCircle(dx, -22, 9, K.paint("#3A2A20"))
        box(c, 0, -146, 124, 18, PAPER_W, BROWN, 4, 6)
        if straw:
            C.line(c, (10, -150), (30, -210), RED, 9)


def signpost(c, x, y, s=1.0, word="东门"):
    with K.at(c, x, y, 0, s):
        C.line(c, (0, 0), (0, -220), GRAY, 10)
        c.drawPath(P((-90, -220), (80, -220), (110, -185), (80, -150), (-90, -150), close=True), K.paint("#D3EDDC"))
        c.drawPath(P((-90, -220), (80, -220), (110, -185), (80, -150), (-90, -150), close=True), wb.marker(GREEN, 6))
        K.text(c, word, 0, -184, 44, "hand", GREEN)


def botany_book(c, x, y, s=1.0, rot=0.0, open_=False):
    """植物学的书：绿封面 + 一朵花；open_=True 摊开。"""
    with K.at(c, x, y, rot, s):
        if open_:
            for sg in (-1, 1):
                pg = P((0, -90), (sg * 170, -110), (sg * 170, 90), (0, 110), close=True)
                c.drawPath(pg, K.paint(PAPER_W))
                c.drawPath(pg, wb.marker(BLACK, 6))
            flower(c, -85, 0, 0.7)
            for r in range(3):
                C.line(c, (30, -40 + r * 40), (140, -44 + r * 40), GRAY, 5)
        else:
            box(c, 0, 0, 200, 260, "#2F7D5B", BLACK, 6, 8)
            flower(c, 0, 10, 0.8)
            K.text(c, "植物学", 0, -90, 40, "hand", PAPER_W)


def flower(c, x, y, s=1.0):
    with K.at(c, x, y, 0, s):
        C.line(c, (0, 10), (0, 90), GREEN, 7)
        for i in range(5):
            a = i * 2 * math.pi / 5 - math.pi / 2
            c.drawCircle(math.cos(a) * 26, math.sin(a) * 26, 20, K.paint("#E58FB1"))
            c.drawCircle(math.cos(a) * 26, math.sin(a) * 26, 20, wb.marker(RED, 4))
        c.drawCircle(0, 0, 14, K.paint("#FFE39A"))


def calendar(c, x, y, w, h, head, color=RED, rot=0.0):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, PAPER_W, BLACK, 6, 10)
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, 70), K.paint(color))
        K.text(c, head, 0, -h / 2 + 36, 44, "hand", "#FFFFFF")


def _hook(H, j, cx, cy, acc):
    """开场：旧照片 → 放大镜扫过 → 冒出“！”；随后“怎么是他”逐字砸下。"""
    b = H.b
    H.note("！")
    PX, PY = cx - 60, cy - 230

    def ph(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc > 0:
            with K.at(c, PX, PY, -5, sc):
                photo(c, 0, 0, 380, 440, 0, 0.75)
        return None
    b.custom(j, 0, 0.3, ph, sfx="wood_low", gain=0.7)

    def mg(c, kk, T):
        dt = T - H.tb(j, 1)
        if dt < 0:
            return None
        f = ease_out(clamp01(dt / 0.4))
        magnifier(c, lerp(PX + 380, PX + 10, f), PY - 110, 110 * pop_scale(dt))
        return None
    b.custom(j, 1, 1.3, mg, sfx="tom", gain=0.75)

    def ex(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        with K.at(c, PX + 330, PY - 180, 10, C.slam_scale(dt)):
            K.text(c, "！", 0, 0, 200, "hand", RED)
        sparkle(c, PX + 330, PY - 180, dt, YELLOW, 8, 90, 170)
        return None
    b.custom(j, 2, 2.3, ex, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("04", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第五章“梦的材料与来源”A、B 节。",
    "书中例子：植物学专著的梦——前一天早上在书店橱窗看到一本仙客来属的专著；梦常挑近期“无关紧要”的印象；童年材料在梦里重现。",
    "“前一两天和一周左右的经历更常入梦”（梦滞后效应）是今天的研究（Nielsen 等）。小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：梦见小学同学；路牌、杯子清清楚楚
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_bed = 0
k_cl = nx(j, wt(0, 0, 0.5), k_bed)
k_sign = nx(j, wt(1, 1, 0.5), k_cl)
k_cup = nx(j, wt(1, 2, 0.7), k_sign)
k_clear = nx(j, wt(1, 3, 0.3), k_cup)
BED1 = (cx - 380, cy + 340)
HIP1 = (BED1[0] + 230, BED1[1] - 20)
CL1 = (cx + 90, cy - 260)
L.note("小学同学", "东门")


def scene1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_bed))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED1[1], sc):
        bed(c, *BED1, 560)
        sleeper(c, *HIP1, 0.8, T, None, "o")
    return None


ev(j, k_bed, scene1, "wood_low", 0.7)


def cloud1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_cl))
    if not dream_cloud(c, CL1[0], CL1[1], 900, 560, sc, tail_to=(HIP1[0] - 300, HIP1[1] - 120)):
        return None
    with at_pop(c, CL1[0], CL1[1], sc):
        x, y = CL1[0] - 250, CL1[1] + 170
        kid(c, x, y, 0.8, "smile", rh=(x + 80, y - 290 * 0.8 - 10))
        K.text(c, "小学同学", x, y - 300, 46, "hand", RED)
        if T >= tb(1, k_sign):
            with at_pop(c, CL1[0] + 40, y, pop_scale(T - tb(1, k_sign))):
                signpost(c, CL1[0] + 40, y, 1.0)
        if T >= tb(1, k_cup):
            with at_pop(c, CL1[0] + 280, y, pop_scale(T - tb(1, k_cup))):
                cup(c, CL1[0] + 280, y, 1.1, straw=False)
    return None


ev(j, k_cl, cloud1, "pop", 0.75)
b.hit(j, k_sign, "wood_high", 0.7, "路牌")
b.hit(j, k_cup, "pop", 0.7, "杯子")
ev(j, k_clear, L.stamp("清清楚楚", cx + 260, cy + 140, 70, j, k_clear, rot=-6), "rim", 0.85)
b.shots[j].shake = [(k_clear, 6.0)]

# ================================================================ 屏 2：上午路过奶茶店 → drop：梦里在那儿上班
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_shop = 1
k_walk = max(k_shop + 1, min(kq(j, wt(3, 0, 0.6), k_shop + 1), KD - 2))
k_cl2 = max(k_walk + 1, KD - 1) if KD - 1 > k_walk else k_walk
GY2 = cy + 450
SHOP = (cx - 280, GY2)
L.note("奶茶", "上午")


def shop2(c, sc, T, cx=cx, cy=cy):
    x, y = SHOP
    with at_pop(c, x, y, sc):
        c.drawRect(skia.Rect.MakeXYWH(x - 220, y - 340, 440, 340), K.paint(PAPER_W))
        c.drawRect(skia.Rect.MakeXYWH(x - 220, y - 340, 440, 340), wb.marker(BROWN, 8))
        for i in range(4):
            col = ("#F6C3BE", PAPER_W)[i % 2]
            c.drawPath(P((x - 240 + i * 120, y - 340), (x - 120 + i * 120, y - 340), (x - 120 + i * 120, y - 400),
                         (x - 240 + i * 120, y - 400), close=True), K.paint(col))
        c.drawRect(skia.Rect.MakeXYWH(x - 240, y - 400, 480, 60), wb.marker(RED, 6))
        box(c, x, y - 460, 200, 76, "#FFF4D6", BROWN, 5, 12)
        K.text(c, "奶茶", x, y - 458, 50, "hand", BROWN)
        box(c, x - 80, y - 200, 160, 180, "#DCE6F2", BLUE, 5, 6)
        cup(c, x + 120, y - 120, 0.8)
        box(c, cx - 400, cy - 470, 200, 80, PAPER_W, BLACK, 6, 14)
        K.text(c, "上午", cx - 400, cy - 468, 50, "hand", ORANGE)
        A.sun(c, cx - 210, cy - 470, 40)
    return None


ev(j, k_shop, pop_fn(j, k_shop, shop2), "wood_low", 0.7)


def walk2(c, kk, T, cx=cx, cy=cy):
    t0 = tb(2, k_walk)
    if T < t0:
        return None
    x, dy, moving = C.walk(T, t0, 1.2, cx + 120, cx + 330)
    draw_li(c, x, GY2 + dy, 0.8, "flat", bag=True)
    return None


ev(j, k_walk, walk2, "shaker", 0.7)
CL2 = (cx + 200, cy - 300)


def dream2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_cl2))
    if not dream_cloud(c, CL2[0], CL2[1], 640, 460, sc, tail_to=(cx + 330, GY2 - 290)):
        return None
    with at_pop(c, CL2[0], CL2[1], sc):
        x, y = CL2[0], CL2[1] + 150
        g = C.slam_scale(T - tb(2, KD))
        draw_li(c, x - 60, y, 0.7, "smile" if g > 0 else "flat", rh=(x + 40, y - 150))
        box(c, x - 60, y - 110, 70, 90, "#F6C3BE", RED, 4, 8)
        c.drawRect(skia.Rect.MakeXYWH(x - 210, y - 100, 420, 30), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(x - 210, y - 100, 420, 30), wb.marker(BROWN, 6))
        if g > 0:
            with K.at(c, x + 80, y - 100, 0, g):
                cup(c, 0, 0, 0.7)
                cup(c, 90, 0, 0.7)
    return None


ev(j, k_cl2, dream2, "pop", 0.7)
ev(j, KD, L.slam_text("上班", cx - 330, cy - 250, 130, RED, j, KD, rot=-6), "kick", 0.95)

# ================================================================ 屏 3：梦见老家的院子，墙上的裂缝都还在
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_cl3 = 0
k_wall = nx(j, wt(4, 0, 0.6), k_cl3)
k_crack = nx(j, wt(4, 1, 0.3), k_wall)
k_mag3 = nx(j, wt(4, 1, 0.8), k_crack)
CL3 = (cx, cy - 110)
L.note("老家", "都还在")


def cloud3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_cl3))
    if not dream_cloud(c, CL3[0], CL3[1], 1020, 740, sc):
        return None
    with at_pop(c, CL3[0], CL3[1], sc):
        K.text(c, "老家", CL3[0] - 300, CL3[1] - 260, 60, "hand", NIGHT)
        if T >= tb(3, k_wall):
            g = pop_scale(T - tb(3, k_wall))
            x, y = CL3[0] - 40, CL3[1] + 200
            with at_pop(c, x, y, g):
                c.drawRect(skia.Rect.MakeXYWH(x - 340, y - 300, 620, 300), K.paint("#EFE3CF"))
                for r in range(5):
                    for q in range(6):
                        c.drawRect(skia.Rect.MakeXYWH(x - 340 + q * 104 + (r % 2) * 50, y - 300 + r * 60, 100, 56),
                                   wb.marker("#C9A87A", 3))
                c.drawRect(skia.Rect.MakeXYWH(x - 340, y - 300, 620, 300), wb.marker(BROWN, 7))
                C.line(c, (x + 380, y), (x + 380, y - 260), BROWN, 14)
                for i in range(5):
                    c.drawCircle(x + 380 + (i - 2) * 40, y - 290 - (i % 2) * 40, 60, K.paint("#9CCB8E"))
                c.drawCircle(x + 380, y - 320, 90, wb.marker(GREEN, 5))
        if T >= tb(3, k_crack):
            f = clamp01((T - tb(3, k_crack)) / 0.35)
            x, y = CL3[0] - 120, CL3[1] - 60
            pts = [(x, y), (x + 30, y + 50), (x + 5, y + 90), (x + 40, y + 150), (x + 20, y + 200)]
            n = max(2, int(2 + f * 3))
            c.drawPath(P(*pts[:n]), wb.marker(BLACK, 6))
    return None


ev(j, k_cl3, cloud3, "pop", 0.75)
b.hit(j, k_wall, "wood_low", 0.7, "院墙")
b.hit(j, k_crack, "rim", 0.75, "裂缝")


def mag3(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(3, k_mag3)
    if dt < 0:
        return None
    magnifier(c, cx - 100, cy - 20, 130 * pop_scale(dt), 0)
    if dt > 0.2:
        K.text(c, "都还在", cx + 260, cy + 450, 80, "hand", RED, clamp01((dt - 0.2) / 0.2))
    return None


ev(j, k_mag3, mag3, "ding", 0.8)

# ================================================================ 屏 4：弗洛伊德查梦的材料从哪来；脚印通向“前一天”
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_fr = kq(j, wt(5, 0, 0.3), 0)
k_q4 = nx(j, wt(5, 2, 0.3), k_fr)
k_steps = nx(j, wt(6, 1, 0.3), k_q4)
k_day = nx(j, wt(6, 2, 0.6), k_steps)
L.note("从哪来", "前一天", "影子")


def fr4(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 330, cy + 440
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 1.0, "flat", cigar=False)
        magnifier(c, x + 120, y - 240, 70, 0)
    return None


ev(j, k_fr, pop_fn(j, k_fr, fr4), "wood_low", 0.7)


def q4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_q4))
    if sc <= 0:
        return None
    x, y = cx - 150, cy - 330
    dream_cloud(c, x, y, 520, 340, sc)
    with at_pop(c, x, y, sc):
        star(c, x - 150, y - 30, 36)
        cup(c, x - 40, y + 30, 0.45, False)
        signpost(c, x + 80, y + 50, 0.45)
        K.text(c, "从哪来", x + 40, y + 110, 52, "hand", RED)
        K.text(c, "？", x + 200, y - 60, 90, "hand", RED)
    return None


ev(j, k_q4, q4, "pop", 0.75)


def steps4(c, kk, T, cx=cx, cy=cy):
    t0 = tb(4, k_steps)
    if T < t0:
        return None
    pts = [(cx - 120, cy + 380), (cx - 20, cy + 300), (cx + 40, cy + 200), (cx + 140, cy + 130), (cx + 200, cy + 30)]
    for i, (x, y) in enumerate(pts):
        a = clamp01((T - t0 - i * 0.08) / 0.15)
        if a > 0:
            with K.at(c, x + (i % 2) * 30, y, 30):
                c.drawOval(skia.Rect.MakeXYWH(-16, -26, 32, 52), K.paint(BROWN, a))
    return None


ev(j, k_steps, steps4, "shaker", 0.7)


def day4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_day))
    if sc <= 0:
        return None
    x, y = cx + 330, cy - 120
    with K.at(c, x, y, 4, sc):
        calendar(c, 0, 0, 300, 300, "前一天")
        cup(c, -50, 110, 0.6, False)
        signpost(c, 60, 120, 0.5)
    K.text(c, "影子", x, y + 230, 64, "hand", NIGHT, clamp01((T - tb(4, k_day)) / 0.3))
    return None


ev(j, k_day, day4, "ding", 0.8)

# ================================================================ 屏 5：梦见植物学的书 ↔ 前一天书店橱窗里瞟到
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_cl5 = kq(j, wt(7, 1, 0.3), 0)
k_win = nx(j, wt(8, 1, 0.3), k_cl5)
k_look = nx(j, wt(8, 3, 0.2), k_win)
k_same = nx(j, wt(8, 3, 0.8), k_look)
CL5 = (cx - 150, cy - 300)
WIN = (cx + 230, cy + 260)
L.note("书店", "前一天早上", "同一本")


def cloud5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_cl5))
    if not dream_cloud(c, CL5[0], CL5[1], 640, 420, sc, tail_to=(cx - 340, cy + 110)):
        return None
    with at_pop(c, CL5[0], CL5[1], sc):
        botany_book(c, CL5[0], CL5[1] + 10, 1.0, -4, open_=True)
    return None


def fr5(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 360, cy + 460
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 0.95, "smile")
    return None


ev(j, k_cl5, pop_fn(j, k_cl5, fr5), "wood_low", 0.7)
ev(j, k_cl5, cloud5, "pop", 0.75)


def win5(c, sc, T, cx=cx, cy=cy):
    x, y = WIN
    with at_pop(c, x, y, sc):
        c.drawRect(skia.Rect.MakeXYWH(x - 250, y - 300, 500, 480), K.paint(PAPER_W))
        c.drawRect(skia.Rect.MakeXYWH(x - 250, y - 300, 500, 480), wb.marker(BROWN, 8))
        box(c, x, y - 360, 200, 76, "#FFF4D6", BROWN, 5, 10)
        K.text(c, "书店", x, y - 358, 48, "hand", BROWN)
        c.drawRect(skia.Rect.MakeXYWH(x - 200, y - 240, 400, 330), K.paint("#DCE6F2"))
        c.drawRect(skia.Rect.MakeXYWH(x - 200, y - 240, 400, 330), wb.marker(BLUE, 5))
        botany_book(c, x - 60, y - 70, 0.8, 0)
        box(c, x + 110, y - 60, 100, 200, "#F6C3BE", RED, 4, 6)
        C.line(c, (x - 200, y + 90), (x + 200, y + 90), BROWN, 8)
        K.text(c, "前一天早上", x, y + 140, 46, "hand", ORANGE)
    return None


ev(j, k_win, pop_fn(j, k_win, win5), "wood_high", 0.7)


def look5(c, kk, T, cx=cx, cy=cy):
    t0 = tb(5, k_look)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.4))
    a, z = (cx - 300, cy + 150), (WIN[0] - 110, WIN[1] - 70)
    c.drawPath(P(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f))), wb.marker(GRAY, 5, 0.9))
    if T >= tb(5, k_same):
        g = clamp01((T - tb(5, k_same)) / 0.45)
        p0, p1 = (WIN[0] - 60, WIN[1] - 210), (CL5[0] + 260, CL5[1] + 150)
        c.drawPath(wb.arrow(p0, (lerp(p0[0], p1[0], g), lerp(p0[1], p1[1], g)), -0.25, 34), wb.marker(RED, 8))
    return None


ev(j, k_look, look5, "pop", 0.7)
ev(j, k_same, L.pop_bubble("同一本", cx + 330, cy - 420, j, k_same, 60, RED, tail=-1), "ding", 0.85)

# ================================================================ 屏 6：梦挑没留意的小事，大事反而不上场
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_stage = kq(j, wt(9, 0, 0.5), 0)
k_small = nx(j, wt(9, 1, 0.6), k_stage)
k_big = nx(j, wt(9, 2, 0.3), k_small)
k_out = nx(j, wt(9, 2, 0.8), k_big)
GY6 = cy + 260
L.note("大事", "小事", "梦")


def stage6(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, GY6, sc):
        c.drawRect(skia.Rect.MakeXYWH(cx - 520, GY6, 700, 80), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(cx - 520, GY6, 700, 80), wb.marker(BROWN, 7))
        for sg in (-1, 1):
            xx = cx - 170 + sg * 330
            c.drawPath(P((xx, GY6), (xx, GY6 - 620), (xx - sg * 70, GY6 - 620), (xx - sg * 40, GY6), close=True),
                       K.paint("#C0392B"))
        dream_cloud(c, cx - 170, GY6 - 560, 300, 120, 1.0)
        K.text(c, "梦", cx - 170, GY6 - 556, 60, "hand", NIGHT)
    return None


ev(j, k_stage, pop_fn(j, k_stage, stage6), "wood_low", 0.7)


def small6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_small)
    if T < t0:
        return None
    a = clamp01((T - t0) / 0.25)
    x = cx - 170
    c.drawPath(P((x - 30, GY6 - 480), (x + 30, GY6 - 480), (x + 170, GY6), (x - 170, GY6), close=True), K.paint("#FFF1A8", 0.6 * a))
    with K.at(c, x, GY6, 0, pop_scale(T - t0)):
        cup(c, 0, 0, 0.9)
    K.text(c, "小事", x, GY6 + 140, 56, "hand", ORANGE, a)
    return None


ev(j, k_small, small6, "ding", 0.75)


def big6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_big)
    if T < t0:
        return None
    out = ease_in_out(clamp01((T - tb(6, k_out)) / 0.4)) if T >= tb(6, k_out) else 0.0
    x, y = cx + 360 + out * 40, GY6 - 100
    with K.at(c, x, y, 4 * out, pop_scale(T - t0)):
        box(c, 0, 0, 280, 220, "#CFE0F5", BLUE, 8, 10)
        K.text(c, "大事", 0, 4, 90, "hand", BLUE)
        if out > 0:
            c.drawPath(cross(0, 0, 90 * out + 10), wb.marker(RED, 12))
    return None


ev(j, k_big, big6, "wood_high", 0.75)
ev(j, k_out, L.stamp("不上场", cx + 330, cy - 330, 76, j, k_out, rot=-6), "rim", 0.85)
b.shots[j].shake = [(k_out, 6.0)]

# ================================================================ 屏 7：另一个来源是小时候；早忘的童年小事在梦里原样出现
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_card7 = kq(j, wt(10, 1, 0.3), 0)
k_old = nx(j, wt(11, 1, 0.5), k_card7)
k_cl7 = nx(j, wt(11, 2, 0.3), k_old)
k_eq = nx(j, wt(11, 2, 0.8), k_cl7)
L.note("小时候", "原样")


def card7(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(7, k_card7))
    if sc <= 0:
        return None
    with K.at(c, cx, cy - 430, -2, sc):
        box(c, 0, 0, 560, 160, PAPER_W, NIGHT, 8, 30)
        K.text(c, "小时候", 0, 4, 100, "hand", NIGHT)
    return None


ev(j, k_card7, card7, "kick", 0.85)
b.shots[j].shake = [(k_card7, 6.0)]


def old7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_old))
    if sc <= 0:
        return None
    with K.at(c, cx - 290, cy + 60, -6, sc):
        photo(c, 0, 0, 360, 420, 0, 0.7)
    return None


ev(j, k_old, old7, "wood_low", 0.7)


def cl7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_cl7))
    x, y = cx + 290, cy + 40
    if not dream_cloud(c, x, y, 500, 560, sc):
        return None
    with at_pop(c, x, y, sc):
        photo(c, x, y + 10, 300, 350, 4, 0.58)
    return None


ev(j, k_cl7, cl7, "pop", 0.75)


def eq7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_eq))
    if sc <= 0:
        return None
    with K.at(c, cx, cy + 40, 0, sc):
        C.line(c, (-40, -18), (40, -18), RED, 12)
        C.line(c, (-40, 18), (40, 18), RED, 12)
    K.text(c, "原样", cx, cy + 420, 90, "hand", RED, clamp01((T - tb(7, k_eq)) / 0.2))
    return None


ev(j, k_eq, eq7, "ding", 0.8)

# ================================================================ 屏 8：前一天的小事像钩子，钩上很久以前的心事
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_rod = kq(j, wt(12, 0, 0.4), 0)
k_dip = nx(j, wt(12, 1, 0.3), k_rod)
k_pull = nx(j, wt(12, 2, 0.3), k_dip)
k_heart = nx(j, wt(12, 2, 0.85), k_pull)
WY = cy - 120
L.note("前一天", "很久以前", "心事")


def water8(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, WY, sc):
        for i, col in enumerate(("#CFE0F5", "#A9C4E6", "#7F9FCF")):
            c.drawRect(skia.Rect.MakeXYWH(cx - 560, WY + i * 210, 1120, 210), K.paint(col))
        p = skia.Path()
        p.moveTo(cx - 560, WY)
        for i in range(14):
            p.quadTo(cx - 520 + i * 80, WY - 20 * (1 if i % 2 else -1), cx - 480 + i * 80, WY)
        c.drawPath(p, wb.marker(BLUE, 7))
        K.text(c, "很久以前", cx + 380, WY + 560, 46, "hand", PAPER_W)
        x = cx - 200
        draw_li(c, x, WY - 60, 0.75, "flat", rh=(x + 90, WY - 230))
        c.drawRect(skia.Rect.MakeXYWH(x - 140, WY - 60, 280, 60), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(x - 140, WY - 60, 280, 60), wb.marker(BROWN, 6))
        C.line(c, (x + 90, WY - 230), (cx + 220, WY - 440), BROWN, 9)
    return None


ev(j, k_rod, pop_fn(j, k_rod, water8), "wood_low", 0.7)
TIP = (cx + 220, WY - 440)


def line8(c, kk, T, cx=cx, cy=cy):
    t0 = tb(8, k_dip)
    if T < t0:
        return None
    down = ease_out(clamp01((T - t0) / 0.5))
    up = ease_in_out(clamp01((T - tb(8, k_pull)) / 0.6)) if T >= tb(8, k_pull) else 0.0
    depth = WY + 520 * down - 560 * up
    hx = TIP[0]
    C.line(c, TIP, (hx, depth), BLACK, 4)
    p = skia.Path()
    p.moveTo(hx, depth)
    p.lineTo(hx, depth + 40)
    p.quadTo(hx, depth + 70, hx - 30, depth + 60)
    c.drawPath(p, wb.marker(GRAY, 7))
    with K.at(c, hx - 110, max(TIP[1] + 70, depth - 20), 0, 1.0):
        cup(c, 0, 30, 0.45, False)
    K.text(c, "前一天", hx - 220, TIP[1] + 60, 46, "hand", ORANGE)
    if up > 0:
        bx, by = hx, depth + 120
        with K.at(c, bx, by, -6 + 6 * up):
            box(c, 0, 0, 200, 140, "#C9A87A", BROWN, 7, 8)
            C.line(c, (-100, -20), (100, -20), BROWN, 6)
            c.drawCircle(0, 0, 14, K.paint(YELLOW))
    return None


ev(j, k_dip, line8, "pop", 0.7)
b.hit(j, k_pull, "tom", 0.8, "钩上来")


def heart8(c, kk, T, cx=cx, cy=cy):
    t0 = tb(8, k_heart)
    if T < t0:
        return None
    x, y = TIP[0] + 230, WY - 30
    with K.at(c, x, y, 0, C.slam_scale(T - t0)):
        c.drawPath(C.heart_path(0, 0, 70), K.paint("#F6C3BE"))
        c.drawPath(C.heart_path(0, 0, 70), wb.marker(RED, 7))
        K.text(c, "心事", 0, 120, 64, "hand", RED)
    sparkle(c, x, y, T - t0, YELLOW, 8, 90, 160)
    return None


ev(j, k_heart, heart8, "ding", 0.85)

# ================================================================ 屏 9：现在的研究：前一两天的经历常入梦，一周左右又冒一次
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_ax = kq(j, wt(13, 0, 0.5), 0)
k_b1 = nx(j, wt(13, 1, 0.5), k_ax)
k_b7 = nx(j, wt(13, 3, 0.3), k_b1)
L.note("研究", "入梦次数", "1天", "2天", "7天", "隔几天")
BARS = [0.9, 0.75, 0.35, 0.25, 0.3, 0.55, 0.7, 0.3]


def axis9(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy, sc):
        A.brain(c, cx - 420, cy - 420, 70)
        K.text(c, "研究", cx - 140, cy - 420, 56, "hand", BLUE)
        x0, y0 = cx - 460, cy + 280
        C.line(c, (x0, y0), (x0 + 940, y0), BLACK, 7)
        C.line(c, (x0, y0), (x0, y0 - 560), BLACK, 7)
        K.text(c, "入梦次数", x0 + 120, y0 - 600, 44, "hand", GRAY)
        K.text(c, "隔几天", x0 + 860, y0 + 70, 44, "hand", GRAY)
    return None


ev(j, k_ax, pop_fn(j, k_ax, axis9), "wood_low", 0.7)


def bars9(c, kk, T, cx=cx, cy=cy):
    x0, y0 = cx - 460, cy + 280
    for i, h in enumerate(BARS):
        k = k_b1 if i < 5 else k_b7
        dt = T - tb(9, k) - (i % 5 if i < 5 else i - 5) * 0.08
        if dt < 0:
            continue
        f = ease_out(clamp01(dt / 0.35))
        hot = i < 2 or i in (5, 6)
        x = x0 + 60 + i * 110
        c.drawRect(skia.Rect.MakeXYWH(x, y0 - 500 * h * f, 80, 500 * h * f), K.paint("#F6C3BE" if hot else "#E3E3E3"))
        c.drawRect(skia.Rect.MakeXYWH(x, y0 - 500 * h * f, 80, 500 * h * f), wb.marker(RED if hot else GRAY, 5))
        if i in (0, 1, 6):
            K.text(c, ("1天", "2天", "", "", "", "", "7天")[i], x + 40, y0 + 50, 40, "hand", BLACK)
    if T >= tb(9, k_b7):
        a = clamp01((T - tb(9, k_b7) - 0.3) / 0.3)
        x = x0 + 60 + 5 * 110 + 95
        c.drawPath(wb.arrow((x + 150, y0 - 520), (x + 20, y0 - 390), 0.2, 30), wb.marker(RED, 7, a))
    return None


ev(j, k_b1, bars9, "pop", 0.75)
b.hit(j, k_b7, "ding", 0.8, "一周左右又冒一次")

# ================================================================ 屏 10：别急着猜他想你了 → 三步
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_li10 = kq(j, wt(14, 0, 0.5), 0)
k_guess = nx(j, wt(14, 1, 0.3), k_li10)
k_x10 = nx(j, wt(14, 1, 0.8), k_guess)
k_3 = nx(j, wt(14, 2, 0.5), k_x10)
GY10 = cy + 420
L.note("他想我了？", "三步")


def li10(c, sc, T, cx=cx, cy=cy):
    x = cx - 280
    with at_pop(c, x, GY10, sc):
        C.line(c, (x - 260, GY10), (x + 260, GY10), BLACK, 7)
        draw_li(c, x, GY10, 0.9, "smile", rh=(x + 80, GY10 - 300))
        box(c, x + 80, GY10 - 300, 60, 100, "#2E2A28", BLACK, 4, 10)
    return None


ev(j, k_li10, pop_fn(j, k_li10, li10), "wood_low", 0.7)


def guess10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_guess))
    if sc <= 0:
        return None
    x, y = cx - 100, cy - 320
    with K.at(c, x, y, -3, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(-280, -100, 560, 200), 50, 50, K.paint(PAPER_W))
        c.drawPath(wb.bubble(0, 0, 560, 200, -1), wb.marker(BLACK, 8))
        K.text(c, "他想我了？", 0, 4, 80, "hand", RED)
        if T >= tb(10, k_x10):
            with K.at(c, 0, 0, 0, pop_scale(T - tb(10, k_x10))):
                c.drawPath(cross(0, 0, 100), wb.marker(RED, 16))
    return None


ev(j, k_guess, guess10, "pop", 0.75)
b.hit(j, k_x10, "rim", 0.85, "打叉")


def three10(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(10, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 270, cy + 80, -4, sc):
        c.drawCircle(0, 0, 190, K.paint("#FFF4D6"))
        c.drawCircle(0, 0, 190, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 130, "hand", L.ACC)
    return None


ev(j, k_3, three10, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 11：第一，找钩子——前一两天，什么东西让你想到他
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_h11 = kq(j, wt(15, 0, 0.3), 0)
k_cal = nx(j, wt(15, 1, 0.5), k_h11)
k_items = nx(j, wt(15, 2, 0.3), k_cal)
k_mag = nx(j, wt(15, 2, 0.85), k_items)
L.note("第一", "找钩子", "前一两天", "一首老歌", "一件校服", "一杯奶茶")
ITEMS = ["一杯奶茶", "一首老歌", "一件校服"]


def h11(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第一", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "找钩子", cx - 140, cy - 500, 56, "hand", BLACK)
    return None


ev(j, k_h11, pop_fn(j, k_h11, h11), "wood_low", 0.6)


def cal11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_cal))
    if sc <= 0:
        return None
    with K.at(c, cx - 60, cy, 0, sc):
        calendar(c, 0, 0, 760, 640, "前一两天", ORANGE)
        for i, it in enumerate(ITEMS):
            g = pop_scale(T - tb(11, k_items) - i * 0.15)
            if g <= 0:
                continue
            y = -150 + i * 170
            with K.at(c, 0, y, 0, g):
                c.drawCircle(-280, 0, 16, K.paint(GRAY))
                K.text(c, it, -240, 0, 66, "hand", BLACK, 1.0, "left")
    return None


ev(j, k_cal, cal11, "wood_high", 0.7)
b.hit(j, k_items, "pop", 0.7, "三件小事")


def mag11(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(11, k_mag)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.35))
    magnifier(c, lerp(cx + 450, cx - 170, f), cy + 190, 150, 0)
    if dt > 0.35:
        with K.at(c, cx + 380, cy + 420, 0, pop_scale(dt - 0.35)):
            kid(c, 0, 0, 0.6, "smile")
        c.drawPath(wb.arrow((cx + 70, cy + 330), (cx + 300, cy + 330), 0.2, 26), wb.marker(RED, 6, clamp01((dt - 0.35) / 0.2)))
    return None


ev(j, k_mag, mag11, "ding", 0.8)

# ================================================================ 屏 12：第二，找年份——梦里的你大概几岁（身高尺）
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_h12 = kq(j, wt(16, 0, 0.3), 0)
k_ruler = nx(j, wt(16, 1, 0.3), k_h12)
k_kid = nx(j, wt(16, 1, 0.8), k_ruler)
k_age = nx(j, wt(16, 2, 0.5), k_kid)
GY12 = cy + 440
L.note("第二", "找年份", "几岁？", "十岁", "现在")


def h12(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第二", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "找年份", cx - 140, cy - 500, 56, "hand", BLACK)
    return None


ev(j, k_h12, pop_fn(j, k_h12, h12), "wood_low", 0.6)


def ruler12(c, sc, T, cx=cx, cy=cy):
    x = cx - 40
    with at_pop(c, x, GY12, sc):
        c.drawRect(skia.Rect.MakeXYWH(x - 50, GY12 - 820, 100, 820), K.paint("#FFF1A8"))
        c.drawRect(skia.Rect.MakeXYWH(x - 50, GY12 - 820, 100, 820), wb.marker(ORANGE, 6))
        for i in range(17):
            w = 40 if i % 4 == 0 else 20
            C.line(c, (x - 50, GY12 - i * 50), (x - 50 + w, GY12 - i * 50), ORANGE, 4)
        draw_li(c, x + 230, GY12, 1.0, "smile")
        K.text(c, "现在", x + 230, GY12 - 360, 46, "hand", GRAY)
    return None


ev(j, k_ruler, pop_fn(j, k_ruler, ruler12), "wood_high", 0.7)


def kid12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_kid))
    x = cx - 330
    feet = cy + 320
    hy = feet - 290 * 0.6
    if not dream_cloud(c, x, cy + 60, 420, 680, sc):
        return None
    with at_pop(c, x, feet, sc):
        kid(c, x, feet, 0.6, "smile")
        if T < tb(12, k_age):
            K.text(c, "几岁？", x, hy - 200, 60, "hand", RED)
    if T >= tb(12, k_age):
        g = pop_scale(T - tb(12, k_age))
        y = hy - 50
        c.drawPath(P((x + 60, y), (cx - 90, y)), wb.marker(RED, 5))
        with K.at(c, x, y - 170, -6, g):
            box(c, 0, 0, 200, 100, PAPER_W, RED, 6, 14)
            K.text(c, "十岁", 0, 2, 66, "hand", RED)
    return None


ev(j, k_kid, kid12, "pop", 0.7)
b.hit(j, k_age, "ding", 0.8, "十岁")

# ================================================================ 屏 13：第三，问那时候：最在意什么，现在还在意吗
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_h13 = kq(j, wt(17, 0, 0.3), 0)
k_then = nx(j, wt(17, 1, 0.5), k_h13)
k_now = nx(j, wt(17, 2, 0.3), k_then)
k_ans = nx(j, wt(17, 2, 0.85), k_now)
GY13 = cy + 440
L.note("第三", "问那时候", "考第一", "还在意吗？")


def h13(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第三", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "问那时候", cx - 110, cy - 500, 56, "hand", BLACK)
    return None


ev(j, k_h13, pop_fn(j, k_h13, h13), "wood_low", 0.6)


def then13(c, sc, T, cx=cx, cy=cy):
    x = cx - 300
    with at_pop(c, x, GY13, sc):
        kid(c, x, GY13, 0.75, "sad")
        dream_cloud(c, x, cy - 160, 380, 260, 1.0, tail_to=(x, GY13 - 260))
        A.exam_paper(c, x - 60, cy - 160, 150, 180, -6, "", None)
        K.text(c, "考第一", x + 90, cy - 160, 50, "hand", RED)
    return None


ev(j, k_then, pop_fn(j, k_then, then13), "pop", 0.7)


def now13(c, sc, T, cx=cx, cy=cy):
    x = cx + 300
    with at_pop(c, x, GY13, sc):
        draw_li(c, x, GY13, 1.0, "flat" if T < tb(13, k_ans) else "smile")
        box(c, x, cy - 160, 340, 120, PAPER_W, BLUE, 6, 40)
        K.text(c, "还在意吗？", x, cy - 158, 56, "hand", BLUE)
        c.drawPath(wb.arrow((cx - 120, cy + 120), (cx + 120, cy + 120), 0.0, 34), wb.marker(GRAY, 7))
    return None


ev(j, k_now, pop_fn(j, k_now, now13), "wood_high", 0.7)


def ans13(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(13, k_ans)
    if dt < 0:
        return None
    x, y = cx + 430, cy + 110
    with K.at(c, x, y, 0, pop_scale(dt)):
        c.drawPath(C.heart_path(0, 0, 50), K.paint("#F6C3BE"))
        c.drawPath(C.heart_path(0, 0, 50), wb.marker(RED, 6))
    sparkle(c, x, y, dt, YELLOW, 8, 70, 130)
    return None


ev(j, k_ans, ans13, "ding", 0.8)

# ================================================================ 屏 14：一个怪梦就是一张旧照片，帮你翻出忘了的自己
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_cl14 = 0
k_turn = nx(j, wt(18, 2, 0.3), k_cl14)
k_self = nx(j, wt(18, 3, 0.6), k_turn)
L.note("忘了的自己")


def turn14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_cl14))
    if sc <= 0:
        return None
    m = ease_in_out(clamp01((T - tb(14, k_turn)) / 0.45)) if T >= tb(14, k_turn) else 0.0
    x, y = cx, cy - 140
    if m < 1:
        dream_cloud(c, x, y, 760 * (1 - m * 0.5), 520 * (1 - m * 0.5), sc, alpha=1 - m)
        with K.at(c, x, y, 0, 1 - m * 0.5):
            K.text(c, "？", -150, 0, 140, "hand", NIGHT, 1 - m)
            cup(c, 60, 80, 0.7, False)
            signpost(c, 220, 90, 0.6)
    if m > 0:
        with K.at(c, x, y, -4 * m, lerp(0.3, 1.0, m)):
            photo(c, 0, 0, 520, 600, 0, 1.0)
    return None


ev(j, k_cl14, turn14, "pop", 0.7)
b.hit(j, k_turn, "clap", 0.8, "梦变成旧照片")


def self14(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(14, k_self)
    if dt < 0:
        return None
    x, y = cx + 300, cy + 470
    with at_pop(c, x, y, pop_scale(dt)):
        draw_li(c, x, y, 0.75, "smile", rh=(x - 100, y - 290 * 0.75 + 60))
    K.text(c, "忘了的自己", cx - 200, cy + 300, 70, "hand", RED, clamp01(dt / 0.25))
    return None


ev(j, k_self, self14, "ding", 0.8)

# ================================================================ 屏 15：评论区——“梦见小学同桌”；发个消息；心里好好待着；下一讲预告
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k_box = kq(j, wt(19, 0, 0.4), 0)
k_type = nx(j, wt(20, 0, 0.3), k_box)
k_msg = nx(j, wt(20, 1, 0.4), k_type)
k_keep = nx(j, wt(21, 1, 0.4), k_msg)
k_n = nx(j, wt(22, 0, 0.1), k_keep)
L.note("评论区", "梦见小学同桌", "发送", "好久不见")


def input15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_box))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(15, k_type):
            s_ = "梦见小学同桌"
            g = clamp01((T - tb(15, k_type)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], x - w / 2 + 40, y + 2, 58, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, L.ACC)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
    return None


ev(j, k_box, input15, "wood_high", 0.7)
b.hit(j, k_type, "pop", 0.6, "打字")


def msg15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_msg))
    if sc <= 0:
        return None
    x, y = cx - 260, cy + 400
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.85, "smile", rh=(x + 90, y - 300))
        box(c, x + 90, y - 300, 70, 120, "#2E2A28", BLACK, 4, 10)
        dt = T - tb(15, k_msg) - 0.3
        f = ease_out(clamp01(dt / 0.6))
        if dt > 0:
            bx, by = lerp(x + 150, x + 260, f), lerp(y - 340, y - 520, f)
            with K.at(c, bx, by, 0, 1.0):
                box(c, 0, 0, 280, 90, "#D3EDDC", GREEN, 5, 30)
                K.text(c, "好久不见", 0, 2, 50, "hand", GREEN)
    return None


ev(j, k_msg, msg15, "ding", 0.8)


def keep15(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(15, k_keep)
    if dt < 0:
        return None
    x, y = cx + 300, cy + 120
    with K.at(c, x, y, 0, pop_scale(dt)):
        c.drawPath(C.heart_path(0, 0, 150), K.paint("#F6C3BE"))
        c.drawPath(C.heart_path(0, 0, 150), wb.marker(RED, 8))
        photo(c, 0, -10, 140, 170, -5, 0.25)
    sparkle(c, x, y, dt, YELLOW, 10, 160, 240)
    return None


ev(j, k_keep, keep15, "clap", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "梦里那个人，怎么像好几个人？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=5, notes=NOTES)
L.export(globals())
