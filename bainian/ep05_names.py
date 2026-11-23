"""《百年孤独》05 名字：换了好几份工作，为什么老在同一处摔跤？（白板手绘 + AI 旁白，竖屏 2:3）

自测：布恩迪亚家七代人名字翻来覆去，叫奥雷里亚诺的孤僻爱琢磨，叫何塞·阿尔卡蒂奥的冲动有闯劲；双胞胎小时候换着身份，
乌尔苏拉怀疑早就换错了；她老了觉得时间在兜圈子。三道题测一测自己是不是也在兜圈子，再给三步改法。
文案见 bainian/PLAN.md「### 05」。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from whiteboard import engine as wb
from whiteboard.engine import P
from bainian import lesson as N
from bainian import theme as BT
from bainian.lesson import (BLACK, BLUE, BLUE_FILL, GRAY, GREEN, GREEN_FILL, INK, NOTE_FILL, ORANGE, RED, RED_FILL, YELLOW,
                            at_pop, box, bubble_box, chip, draw_li, draw_man, draw_wang, name_tag, pop_scale, sparkle, ursula)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "生活里", 1),
    ([2], "生活里", 2),
    ([3], "书里的人", 3),
    ([4, 5], "两种人", 4),
    ([6], "乌尔苏拉", 5),
    ([7], "双胞胎", 6),
    ([8, 9], "兜圈子", 7),
    ([10], "看清楚", 8),
    ([11, 12], "小测试", 9),
    ([13], "第二题", 10),
    ([14], "第三题", 11),
    ([15], "两分以上", 12),
    ([16], "第一步", 13),
    ([17], "第二步", 14),
    ([18], "第三步", 15),
    ([19], "好处", 16),
    ([20, 21, 22, 23], "评论区见", 17),
]

THEME = BT.get("05")
L = N.Lesson("05", SCREENS, drop_screen=2, board_size=(5000, 12400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(16)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》（范晔译本）第 10 章等。情节为转述，不引原文。",
    "今人（小李、小王）为虚构示意；书中人造型为示意（一百多年前的加勒比小镇打扮）。",
]

AUR, JA = "奥雷里亚诺", "何塞·阿尔卡蒂奥"


def stone(c, x, y, a=1.0, s=1.0):
    with K.at(c, x, y, 0, s):
        c.drawOval(skia.Rect.MakeXYWH(-70, -44, 140, 60), K.paint("#9AA0A8", a))
        c.drawOval(skia.Rect.MakeXYWH(-70, -44, 140, 60), wb.marker(BLACK, 6, a))


def building(c, x, y, w=220, h=380, a=1.0):
    box(c, x, y - h / 2, w, h, "#E9EEF4", BLACK, 6, 6, a)
    for r in range(4):
        for q in range(2):
            c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 30 + q * (w / 2), y - h + 40 + r * 70, w / 2 - 60, 40), K.paint(BLUE_FILL, a))


def card(c, x, y, w, h, title, a=1.0):
    box(c, x, y, w, h, "#FFFFFF", BLACK, 7, 16, a)
    K.text(c, title, x, y - h / 2 + 60, 52, "hand", RED, a)


def score_box(c, x, y, n, a=1.0):
    """记分格：三格，前 n 格打勾。"""
    for i in range(3):
        bx = x - 130 + i * 130
        box(c, bx, y, 100, 100, "#FFFFFF", BLACK, 6, 12, a)
        if i < n:
            c.drawPath(wb.check(bx, y, 34), wb.marker(GREEN, 10, a))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：三栋写字楼一字排开，每栋门口盖一个“卡”字；小李拎着纸箱走过
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 470
    k_b = [kq(j, wp(0, 1, 0.3), 0)]
    k_b.append(nx(j, wp(0, 1, 0.8), k_b[0]))
    k_b.append(nx(j, wp(0, 3, 0.4), k_b[1]))
    k_box = nx(j, wp(1, 1, 0.4), k_b[2])
    k_again = nx(j, wp(1, 3, 0.4), k_box)
    L.note("卡", "又来一遍")

    def scene(c, kk, T):
        for i, k_ in enumerate(k_b):
            t0 = tb(j, k_)
            sc = pop_scale(T - t0)
            if sc <= 0:
                continue
            x = cx - 360 + i * 360
            with at_pop(c, x, GY, sc):
                building(c, x, GY)
            if T >= tb(j, k_b[2]) + i * 0.1:
                with K.at(c, x, GY - 460, -6, C.slam_scale(T - tb(j, k_b[2]) - i * 0.1)):
                    c.drawCircle(0, 0, 54, K.paint("#FFFFFF"))
                    c.drawCircle(0, 0, 54, wb.marker(RED, 6))
                    K.text(c, "卡", 0, 2, 64, "hand", RED)
        tbx = tb(j, k_box)
        if T >= tbx:
            f = (T - tbx) / 1.6
            x = lerp(cx - 520, cx + 520, clamp01(f))
            dy = 8 * abs(math.sin((T - tbx) * 7))
            hy = GY + 120 - 290 * 0.7
            draw_li(c, x, GY + 120 - dy, 0.7, "sad", lh=(x - 50, hy + 140), rh=(x + 50, hy + 140))
            box(c, x, hy + 130 - dy, 130, 90, "#E7D6BA", "#8B6B43", 5, 6)
        if T >= tb(j, k_again):
            with K.at(c, cx, cy - 520, 0, C.slam_scale(T - tb(j, k_again))):
                chip(c, 0, 0, "又来一遍", RED_FILL, RED, 56)
        return None
    ev(j, k_b[0], scene, "wood_high", 0.65)
    for k_ in k_b[1:]:
        b.hit(j, k_, "wood_high", 0.65, "又一份工作")
    b.hit(j, k_box, "shaker", 0.7, "拎着纸箱走")
    b.hit(j, k_again, "rim", 0.85, "又来一遍")


screen1()


# ================================================================ 屏 2（drop）：三个背景里，同一块石头在同一个位置
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    dk = L.drop_k()
    k_rows = kq(j, wp(2, 0, 0.3), 0)
    L.note("公司A", "公司B", "公司C", "同一步")

    def scene(c, kk, T):
        tr, td = tb(j, k_rows), tb(j, dk)
        for i, s in enumerate(("公司A", "公司B", "公司C")):
            g = pop_scale(T - tr - i * 0.12)
            if g <= 0:
                continue
            y = cy - 380 + i * 300
            with K.at(c, cx, y, 0, g):
                box(c, 0, 0, 1000, 240, "#FFFFFF", GRAY, 5, 14)
                K.text(c, s, -380, -70, 44, "hand", GRAY)
                C.line(c, (-460, 80), (460, 80), BLACK, 5)
                stone(c, 120, 80)
                if T >= td:
                    ring = skia.Path()
                    ring.addOval(skia.Rect.MakeXYWH(30, 10, 180, 110))
                    c.drawPath(wb.partial(ring, ease_out(clamp01((T - td - i * 0.1) / 0.3)))[0], wb.marker(RED, 8))
        if T >= td:
            with K.at(c, cx + 380, cy + 470, -4, C.slam_scale(T - td)):
                chip(c, 0, 0, "同一步", RED_FILL, RED, 60)
        return None
    ev(j, k_rows, scene, "wood_low", 0.65)
    b.hit(j, dk, "kick", 0.9, "摔跤的那一步没换")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：绿皮书翻开；一棵家谱树，名牌上反复写着两个名字
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    k_book = kq(j, wp(3, 0, 0.4), 0)
    k_tree = nx(j, wp(3, 1, 0.4), k_book)
    k_rep = nx(j, wp(3, 3, 0.2), k_tree)
    KT.book(j, k_book, x=cx - 380, y=cy - 330)
    L.note("家谱", "七代", AUR, JA)
    ROWS = [[JA], [JA, AUR], [AUR, JA], [JA, AUR], [AUR], [AUR]]

    def scene(c, kk, T):
        tt, tr = tb(j, k_tree), tb(j, k_rep)
        if T < tt:
            return None
        K.text(c, "家谱", cx + 230, cy - 520, 60, "serif_black", RED, clamp01((T - tt) / 0.3))
        K.text(c, "七代", cx + 420, cy - 520, 44, "hand", GRAY, clamp01((T - tt) / 0.3))
        for r_, row in enumerate(ROWS):
            for q, nm in enumerate(row):
                t0 = tt + (r_ * 2 + q) * 0.08
                sc = pop_scale(T - t0, 0.25)
                if sc <= 0:
                    continue
                x = cx + 260 + (q - (len(row) - 1) / 2) * 280
                y = cy - 400 + r_ * 150
                if r_:
                    C.line(c, (cx + 260, y - 120), (x, y - 40), GRAY, 4)
                hot = T >= tr and nm == (AUR if (r_ + q) % 2 else JA)
                col = BLUE if nm == AUR else RED
                with K.at(c, x, y, 0, sc * (1.08 if hot else 1)):
                    name_tag(c, 0, 0, nm, col, 34 if nm == AUR else 28)
        return None
    ev(j, k_tree, scene, "shaker", 0.65)
    b.hit(j, k_rep, "pop", 0.8, "名字翻来覆去")


screen3()


# ================================================================ 屏 4：左边奥雷里亚诺们关在屋里琢磨，右边何塞·阿尔卡蒂奥们往外冲
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_a = kq(j, wp(4, 0, 0.4), 0)
    k_room = nx(j, wp(4, 3, 0.3), k_a)
    k_j = nx(j, wp(5, 0, 0.5), k_room)
    k_rush = nx(j, wp(5, 1, 0.5), k_j)
    k_sad = nx(j, wp(5, 2, 0.4), k_rush)
    L.note("孤僻", "爱琢磨", "冲动", "有闯劲", "结局很惨")
    AX, JX = cx - 280, cx + 280

    def scene(c, kk, T):
        ta, tr, tj, tu, ts = (tb(j, k) for k in (k_a, k_room, k_j, k_rush, k_sad))
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        C.line(c, (cx, cy - 560), (cx, GY + 40), GRAY, 4)
        if T >= tr:
            box(c, AX, GY - 220, 420, 460, "#F7EFD9", "#8B6B43", 6, 8, clamp01((T - tr) / 0.3))
        with at_pop(c, AX, GY, g):
            draw_man(c, AX, GY, 0.85, "blue", beard="mustache", mood="flat", rh=(AX + 40, GY - 300))
        name_tag(c, AX, cy - 420, AUR, BLUE, 44, clamp01(g))
        for i, w in enumerate(("孤僻", "爱琢磨")):
            if T >= ta + 0.3 + i * 0.3:
                K.text(c, w, AX - 120 + i * 220, cy - 300, 48, "hand", BLUE, clamp01((T - ta - 0.3 - i * 0.3) / 0.25))
        if T >= tj:
            run = ease_out(clamp01((T - tu) / 0.6)) if T >= tu else 0
            x = JX + 120 * run
            with at_pop(c, x, GY, pop_scale(T - tj)):
                draw_man(c, x, GY, 1.0, "red", beard="full", mood="laugh" if T < ts else "sad",
                         rh=(x + 160, GY - 360), lh=(x - 140, GY - 220), tall=1.08)
            name_tag(c, JX, cy - 420, JA, RED, 38, clamp01((T - tj) / 0.3))
            for i, w in enumerate(("冲动", "有闯劲")):
                if T >= tu + i * 0.2:
                    K.text(c, w, JX - 110 + i * 200, cy - 300, 48, "hand", RED, clamp01((T - tu - i * 0.2) / 0.25))
        if T >= ts:
            with K.at(c, JX, cy - 160, 0, C.slam_scale(T - ts)):
                chip(c, 0, 0, "结局很惨", "#D9DCE1", GRAY, 46)
        return None
    ev(j, k_a, scene, "wood_low", 0.65)
    b.hit(j, k_room, "wood_high", 0.6, "关在屋里")
    b.hit(j, k_j, "bongo_low", 0.75, "何塞·阿尔卡蒂奥们")
    b.hit(j, k_rush, "bongo_high", 0.75, "往外冲")
    b.hit(j, k_sad, "tom", 0.8, "结局很惨")


screen4()


# ================================================================ 屏 5：老年乌尔苏拉戴着老花镜，在本子上画两列记号
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_u = kq(j, wp(6, 0, 0.6), 0)
    k_gen = nx(j, wp(6, 1, 0.5), k_u)
    k_note = nx(j, wp(6, 2, 0.4), k_gen)
    L.note("乌尔苏拉", "第一代 · 母亲", AUR, JA)
    UX = cx - 280

    def scene(c, kk, T):
        tu, tg, tn = tb(j, k_u), tb(j, k_gen), tb(j, k_note)
        g = pop_scale(T - tu)
        if g <= 0:
            return None
        with at_pop(c, UX, GY, g):
            ursula(c, UX, GY, 1.0, old=True, mood="flat", rh=(UX + 160, GY - 260))
            hy = GY - 290
            for sg in (-1, 1):
                c.drawCircle(UX + sg * 17, hy - 2, 15, wb.marker(INK, 4))
        name_tag(c, UX, cy - 360, "乌尔苏拉", "#2F5B8E", 44, clamp01(g), "第一代 · 母亲")
        if T >= tg:
            with K.at(c, cx + 250, cy - 80, 3, pop_scale(T - tg)):
                box(c, 0, 0, 460, 560, "#FFFFFF", "#8B6B43", 6, 8)
                K.text(c, AUR, -110, -220, 34, "hand", BLUE)
                K.text(c, JA, 110, -220, 28, "hand", RED)
                C.line(c, (0, -250), (0, 250), GRAY, 3)
                n = min(5, int((T - tg) / 0.15) + 1)
                for q in range(n):
                    K.text(c, "|", -110, -140 + q * 70, 50, "hand", BLUE)
                    K.text(c, "|", 110, -140 + q * 70, 50, "hand", RED)
        if T >= tn:
            sparkle(c, UX, cy - 120, T - tn, YELLOW, 10, 60, 160)
        return None
    ev(j, k_u, scene, "wood_low", 0.6)
    b.hit(j, k_gen, "pop", 0.7, "看了好几代人")
    b.hit(j, k_note, "ding", 0.8, "琢磨出来")


screen5()


# ================================================================ 屏 6：两个一模一样的小男孩互换名牌，乌尔苏拉挠头
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_twins = kq(j, wp(7, 0, 0.5), 0)
    k_swap = nx(j, wp(7, 1, 0.5), k_twins)
    k_doubt = nx(j, wp(7, 3, 0.4), k_swap)
    k_wrong = nx(j, wp(7, 4, 0.4), k_doubt)
    L.note("双胞胎", "第二", "换错了？")
    N1, N2 = "何塞·阿尔卡蒂奥第二", "奥雷里亚诺第二"

    def scene(c, kk, T):
        tt, ts, td, tw = (tb(j, k) for k in (k_twins, k_swap, k_doubt, k_wrong))
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        X1, X2 = cx - 260, cx + 60
        for i, x in enumerate((X1, X2)):
            with at_pop(c, x, GY, g):
                draw_man(c, x, GY, 0.7, "yellow", mood="laugh" if T >= ts else "smile")
        f = ease_in_out(clamp01((T - ts) / 0.6)) if T >= ts else 0
        for i, nm in enumerate((N1, N2)):
            x0, x1 = (X1, X2) if i == 0 else (X2, X1)
            x = lerp(x0, x1, f)
            y = GY - 330 - 120 * math.sin(f * math.pi) - (40 if i else 0)
            with K.at(c, x, y, 0, g):
                name_tag(c, 0, 0, nm, RED if i == 0 else BLUE, 30)
        K.text(c, "双胞胎", cx - 100, cy - 500, 56, "hand", INK, clamp01(g))
        if T >= td:
            UX = cx + 400
            with at_pop(c, UX, GY, pop_scale(T - td)):
                ursula(c, UX, GY, 0.9, old=True, mood="o", rh=(UX + 40, GY - 340))
        if T >= tw:
            with K.at(c, cx + 330, cy - 300, 4, C.slam_scale(T - tw)):
                bubble_box(c, 0, 0, 280, 110, 1)
                K.text(c, "换错了？", 0, 0, 52, "hand", RED)
        return None
    ev(j, k_twins, scene, "bongo_low", 0.7)
    b.hit(j, k_swap, "shaker", 0.75, "换着身份")
    b.hit(j, k_doubt, "wood_high", 0.65, "乌尔苏拉怀疑")
    b.hit(j, k_wrong, "rim", 0.85, "早就换错了")


screen6()


# ================================================================ 屏 7：一圈小人沿着圆圈走，转回起点；时钟指针转圈
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    k_ring = kq(j, wp(8, 0, 0.4), 0)
    k_same = nx(j, wp(8, 1, 0.4), k_ring)
    k_clock = nx(j, wp(9, 1, 0.3), k_same)
    k_back = nx(j, wp(9, 2, 0.4), k_clock)
    L.note("又转回了开头")

    def scene(c, kk, T):
        tr, ts, tc, tbk = (tb(j, k) for k in (k_ring, k_same, k_clock, k_back))
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        R0 = 330
        oy = cy - 60
        ring = skia.Path()
        ring.addCircle(cx, oy, R0)
        c.drawPath(ring, wb.marker(GRAY, 6, g))
        ang0 = (T - tr) * 0.9
        for q in range(6):
            a = ang0 + q * math.pi / 3
            x, y = cx + R0 * math.cos(a), oy + R0 * math.sin(a) + 60
            (draw_man if q % 2 else N.draw_lady)(c, x, y, 0.42, ("red", "blue")[q % 2], mood="flat")
        if T >= ts:
            K.text(c, "差不多的事", cx, oy - 200, 48, "hand", GRAY, clamp01((T - ts) / 0.3))
        if T >= tc:
            with K.at(c, cx, oy, 0, pop_scale(T - tc)):
                c.drawCircle(0, 0, 130, K.paint("#FFFFFF"))
                c.drawCircle(0, 0, 130, wb.marker(INK, 7))
                a = (T - tc) * 5
                C.line(c, (0, 0), (90 * math.sin(a), -90 * math.cos(a)), RED, 9)
                C.line(c, (0, 0), (55 * math.sin(a / 12), -55 * math.cos(a / 12)), INK, 9)
        if T >= tbk:
            with K.at(c, cx, cy + 460, -2, C.slam_scale(T - tbk)):
                chip(c, 0, 0, "又转回了开头", NOTE_FILL, ORANGE, 52)
        return None
    L.note("差不多的事")
    ev(j, k_ring, scene, "shaker", 0.7)
    b.hit(j, k_same, "wood_low", 0.6, "一代又一代")
    b.hit(j, k_clock, "pop", 0.7, "时间在兜圈子")
    b.hit(j, k_back, "rim", 0.8, "又转回开头")


screen7()


# ================================================================ 屏 8：放大镜照在圆圈上，显出“又来一遍”的那一步
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_ring = kq(j, wp(10, 0, 0.4), 0)
    k_lens = nx(j, wp(10, 3, 0.3), k_ring)
    L.note("这一步")

    def scene(c, kk, T):
        tr, tl = tb(j, k_ring), tb(j, k_lens)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        ring = skia.Path()
        ring.addCircle(cx - 80, cy - 40, 320)
        c.drawPath(ring, wb.marker(GRAY, 8, g))
        for q in range(8):
            a = q * math.pi / 4
            c.drawCircle(cx - 80 + 320 * math.cos(a), cy - 40 + 320 * math.sin(a), 16, K.paint(GRAY, g))
        if T >= tl:
            f = ease_out(clamp01((T - tl) / 0.5))
            lx, ly = lerp(cx + 400, cx + 160, f), lerp(cy + 400, cy + 60, f)
            stone(c, cx + 160, cy + 60, f)
            N.magnifier(c, lx + 40, ly + 30, 1.6, 0.0)
            K.text(c, "这一步", cx + 300, cy - 260, 70, "hand", RED, f)
        return None
    ev(j, k_ring, scene, "wood_low", 0.6)
    b.hit(j, k_lens, "ding", 0.85, "看清楚")


screen8()


# ================================================================ 屏 9：测试卡，第一题：三个场景里同一种麻烦
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_card = kq(j, wp(11, 0, 0.4), 0)
    k_q1 = nx(j, wp(12, 1, 0.3), k_card)
    k_same = nx(j, wp(12, 3, 0.3), k_q1)
    L.note("小测试", "第一题", "麻烦")

    def scene(c, kk, T):
        tc, tq, ts = tb(j, k_card), tb(j, k_q1), tb(j, k_same)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 30, 0, g):
            card(c, 0, 0, 900, 1000, "小测试")
            score_box(c, 0, 380, 0)
        if T >= tq:
            K.text(c, "第一题", cx - 300, cy - 340, 50, "hand", INK, clamp01((T - tq) / 0.3))
            for i in range(3):
                x = cx - 260 + i * 260
                with K.at(c, x, cy - 80, 0, pop_scale(T - tq - 0.1 * i)):
                    box(c, 0, 0, 220, 220, BLUE_FILL, BLUE, 5, 12)
                    if T >= ts:
                        with K.at(c, 0, 0, 0, C.slam_scale(T - ts - 0.08 * i)):
                            K.text(c, "麻烦", 0, 0, 52, "hand", RED)
        return None
    ev(j, k_card, scene, "wood_high", 0.65)
    b.hit(j, k_q1, "pop", 0.7, "第一题")
    b.hit(j, k_same, "rim", 0.8, "同一种麻烦")


screen9()


# ================================================================ 屏 10：第二题：三次出事，小李的反应都是摔门
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_q = kq(j, wp(13, 0, 0.5), 0)
    k_doors = nx(j, wp(13, 2, 0.4), k_q)
    k_same = nx(j, wp(13, 3, 0.4), k_doors)
    L.note("第二题", "砰")

    def scene(c, kk, T):
        tq, td, ts = tb(j, k_q), tb(j, k_doors), tb(j, k_same)
        g = pop_scale(T - tq)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 30, 0, 1):
            card(c, 0, 0, 900, 1000, "第二题", g)
        for i in range(3):
            t0 = td + i * 0.2
            if T < t0:
                continue
            x = cx - 270 + i * 270
            with K.at(c, x, cy + 20, 0, pop_scale(T - t0)):
                box(c, 0, 0, 150, 280, "#B5562E", "#5E2E18", 6, 6)
                c.drawCircle(50, 10, 10, K.paint(YELLOW))
            if T >= ts:
                with K.at(c, x, cy - 220, 0, C.slam_scale(T - ts - 0.08 * i)):
                    K.text(c, "砰", 0, 0, 70, "hand", RED)
        return None
    ev(j, k_q, scene, "wood_high", 0.65)
    b.hit(j, k_doors, "tom", 0.75, "三次出事")
    b.hit(j, k_same, "kick", 0.85, "反应都一样")


screen10()


# ================================================================ 屏 11：第三题：三张便利贴“说过你”，小李捂住耳朵
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 470
    k_q = kq(j, wp(14, 0, 0.5), 0)
    k_notes = nx(j, wp(14, 1, 0.5), k_q)
    k_no = nx(j, wp(14, 2, 0.5), k_notes)
    L.note("第三题", "说过你")

    def scene(c, kk, T):
        tq, tn, tno = tb(j, k_q), tb(j, k_notes), tb(j, k_no)
        g = pop_scale(T - tq)
        if g <= 0:
            return None
        K.text(c, "第三题", cx, cy - 500, 60, "hand", RED, clamp01(g))
        hy = GY - 290
        with at_pop(c, cx, GY, g):
            draw_li(c, cx, GY, 1.0, "flat", lh=(cx - 50, hy) if T >= tno else None, rh=(cx + 50, hy) if T >= tno else None)
        for i in range(3):
            t0 = tn + i * 0.15
            if T < t0:
                continue
            x, y = cx - 360 + i * 360, cy - 280 + (i % 2) * 60
            with K.at(c, x, y, (i - 1) * 6, pop_scale(T - t0)):
                box(c, 0, 0, 240, 130, NOTE_FILL, ORANGE, 5, 6)
                K.text(c, "说过你", 0, 0, 48, "hand", INK)
        return None
    ev(j, k_q, scene, "wood_high", 0.65)
    b.hit(j, k_notes, "pop", 0.7, "提醒过好几次")
    b.hit(j, k_no, "rim", 0.8, "还是没改")


screen11()


# ================================================================ 屏 12：分数格亮到 2，圆圈上出现“兜圈子”
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_score = kq(j, wp(15, 0, 0.5), 0)
    k_loop = nx(j, wp(15, 1, 0.5), k_score)
    k_calm = nx(j, wp(15, 2, 0.5), k_loop)
    L.note("两分以上", "兜圈子", "别慌")

    def scene(c, kk, T):
        ts, tl, tc = tb(j, k_score), tb(j, k_loop), tb(j, k_calm)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        n = 1 + int(clamp01((T - ts) / 0.5) * 1.99)
        score_box(c, cx, cy - 380, n, g)
        K.text(c, "两分以上", cx, cy - 520, 50, "hand", INK, g)
        if T >= tl:
            f = ease_out(clamp01((T - tl) / 0.6))
            ring = skia.Path()
            ring.addArc(skia.Rect.MakeXYWH(cx - 250, cy - 200, 500, 500), -90, 340 * f)
            c.drawPath(ring, wb.marker(ORANGE, 14))
            K.text(c, "兜圈子", cx, cy + 50, 90, "hand", ORANGE, f)
        if T >= tc:
            with K.at(c, cx, cy + 430, -2, C.slam_scale(T - tc)):
                chip(c, 0, 0, "别慌", GREEN_FILL, GREEN, 66)
        return None
    ev(j, k_score, scene, "pop", 0.7)
    b.hit(j, k_loop, "shaker", 0.75, "你也在兜圈子")
    b.hit(j, k_calm, "ding", 0.8, "别慌")


screen12()


# ================================================================ 屏 13：第一步：本子上写三段经过，红笔圈出同一个词
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    k_book = kq(j, wp(16, 1, 0.3), 1)
    k_ring = nx(j, wp(16, 2, 0.5), k_book)
    L.note("第一次", "第二次", "第三次", "委屈")

    def scene(c, kk, T):
        tbk, tr = tb(j, k_book), tb(j, k_ring)
        g = pop_scale(T - tbk)
        if g <= 0:
            return None
        with K.at(c, cx, cy + 20, 0, g):
            box(c, 0, 0, 820, 760, "#FFFFFF", BLACK, 7, 14)
            for i, s in enumerate(("第一次", "第二次", "第三次")):
                y = -250 + i * 220
                K.text(c, s, -270, y, 44, "hand", GRAY)
                C.line(c, (-140, y), (-20, y), GRAY, 6)
                K.text(c, "委屈", 70, y, 52, "hand", INK)
                C.line(c, (150, y), (330, y), GRAY, 6)
                if T >= tr + i * 0.12:
                    ring = skia.Path()
                    ring.addOval(skia.Rect.MakeXYWH(0, y - 48, 140, 96))
                    c.drawPath(wb.partial(ring, ease_out(clamp01((T - tr - i * 0.12) / 0.3)))[0], wb.marker(RED, 8))
        return None
    ev(j, k_book, scene, "wood_high", 0.65)
    b.hit(j, k_ring, "rim", 0.85, "圈出一样的地方")


screen13()


# ================================================================ 屏 14：第二步：动作卡“受委屈 → 想离职”被拎出来
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    k_find = kq(j, wp(17, 1, 0.4), 1)
    k_card = nx(j, wp(17, 2, 0.5), k_find)
    k_quit = nx(j, wp(17, 3, 0.4), k_card)
    L.note("受委屈", "想离职", "动作")

    def scene(c, kk, T):
        tf, tc, tq = tb(j, k_find), tb(j, k_card), tb(j, k_quit)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        K.text(c, "动作", cx, cy - 320, 80, "hand", RED, clamp01(g))
        lift = ease_out(clamp01((T - tc) / 0.4)) if T >= tc else 0
        with K.at(c, cx, cy + 40 - 60 * lift, -3 * lift, g):
            box(c, 0, 0, 760, 220, NOTE_FILL, ORANGE, 7, 16)
            K.text(c, "受委屈", -200, 0, 64, "hand", INK)
            if T >= tq:
                K.text(c, "→", 0, 0, 70, "hand", INK, clamp01((T - tq) / 0.2))
                K.text(c, "想离职", 200, 0, 64, "hand", RED, clamp01((T - tq) / 0.2))
        return None
    ev(j, k_find, scene, "pop", 0.7)
    b.hit(j, k_card, "shaker", 0.7, "拎出动作")
    b.hit(j, k_quit, "rim", 0.8, "一受委屈就想离职")


screen14()


# ================================================================ 屏 15：第三步：在那一步换上新卡“先找人谈一次”
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_step = kq(j, wp(18, 0, 0.5), 1)
    k_swap = nx(j, wp(18, 1, 0.5), k_step)
    k_talk = nx(j, wp(18, 2, 0.4), k_swap)
    L.note("想离职", "先找人谈一次")

    def scene(c, kk, T):
        ts, tw, tt = tb(j, k_step), tb(j, k_swap), tb(j, k_talk)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        stone(c, cx + 60, GY)
        with at_pop(c, cx - 200, GY, g):
            draw_li(c, cx - 200, GY, 0.95, "smile" if T >= tt else "flat")
        f = ease_in_out(clamp01((T - tw) / 0.5)) if T >= tw else 0
        with K.at(c, cx + 150 + 300 * f, cy - 120 - 120 * f, 20 * f, g * (1 - f)):
            box(c, 0, 0, 380, 140, NOTE_FILL, ORANGE, 6, 12)
            K.text(c, "想离职", 0, 0, 60, "hand", RED)
        if T >= tt:
            with K.at(c, cx + 100, cy - 120, -2, C.slam_scale(T - tt)):
                box(c, 0, 0, 520, 150, GREEN_FILL, GREEN, 7, 14)
                K.text(c, "先找人谈一次", 0, 0, 60, "hand", GREEN)
        return None
    ev(j, k_step, scene, "wood_low", 0.6)
    b.hit(j, k_swap, "shaker", 0.7, "换个动作")
    b.hit(j, k_talk, "ding", 0.85, "先找人谈一次")


screen15()


# ================================================================ 屏 16：好处：圆圈断开一个口，小李沿着新路走出去
def screen16(j=16):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_gap = kq(j, wp(19, 1, 0.4), 0)
    k_out = nx(j, wp(19, 2, 0.4), k_gap)
    L.note("新路")

    def scene(c, kk, T):
        tg, to = tb(j, k_gap), tb(j, k_out)
        if T < tg:
            return None
        f = ease_out(clamp01((T - tg) / 0.4))
        ring = skia.Path()
        ring.addArc(skia.Rect.MakeXYWH(cx - 300, cy - 360, 600, 600), 20 + 40 * f, 360 - 40 - 40 * f)
        c.drawPath(ring, wb.marker(ORANGE, 12))
        if T >= to:
            u = ease_in_out(clamp01((T - to) / 1.2))
            road = P((cx + 260, cy - 30), (cx + 420, cy + 200), (cx + 500, cy + 480))
            c.drawPath(wb.partial(road, u)[0], wb.marker(GREEN, 18, 0.8))
            x, y = lerp(cx, cx + 470, u), lerp(cy + 240, cy + 520, u)
            draw_li(c, x, y, 0.7, "smile")
            K.text(c, "新路", cx + 380, cy + 40, 70, "hand", GREEN, u)
        else:
            draw_li(c, cx, cy + 240, 0.7, "flat")
        return None
    ev(j, k_gap, scene, "rim", 0.75)
    b.hit(j, k_out, "ding", 0.85, "走上新路")


screen16()


# ================================================================ 屏 17：评论区；小李迈出圆圈；下一讲预告
def enc(c, T, te, th, cx, cy):
    y = cy + 620
    ring = skia.Path()
    ring.addOval(skia.Rect.MakeXYWH(cx - 380, y - 70, 520, 140))
    c.drawPath(ring, wb.marker(ORANGE, 9, clamp01((T - te) / 0.3)))
    f = ease_out(clamp01((T - th) / 0.5)) if T >= th else 0
    x = lerp(cx - 120, cx + 280, f)
    draw_li(c, x, y, 0.85, "smile")
    if T >= th:
        K.text(c, "多走了一步", cx + 260, cy + 260, 52, "hand", GREEN, f)


def fog_icon(c, x, y, dt):
    with K.at(c, x, y, 0, pop_scale(dt)):
        C.line(c, (0, 50), (0, -50), "#6E4E22", 8)
        box(c, 20, -40, 90, 40, "#FFFFFF", BLACK, 4, 6)
        for q in range(3):
            c.drawOval(skia.Rect.MakeXYWH(-70 + q * 40, 10 + (q % 2) * 10, 90, 30), K.paint("#D9DCE1", 0.8))


L.note("多走了一步")
KT.ending(17, "你测出了几分？", ["0分", "2分", "3分"], 21, 22, enc, 23, ["看不清前路", "怎么办？"],
          enc_piece=3, next_icon=fog_icon)

# ================================================================ 收尾
L.finish(cover_shot=4, square_shot=4, notes=NOTES)
L.export(globals())
