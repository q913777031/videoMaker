"""《资治通鉴》13 用人如器：总说没人可用，人到底在哪？（白板手绘 + AI 旁白，竖屏 2:3）

比喻贯穿：一柜子器物（碗盛饭、壶倒水、刀切菜）。唐太宗让封德彝举贤，日历翻过很久名单还是空的，“于今未有奇才”；
太宗“君子用人如器，各取所长……正患己不能知，安可诬一世之人”，蒙着的眼睛揭开看到一群人才；今人：觉得组里没人可用时的三步。
唐人戴幞头。古人的屏画在卷轴框里，今人在办公室。文案见 zizhi/PLAN.md「### 13」。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross, rect
from zizhi import lesson as Z
from zizhi import theme as ZT
from zizhi.lesson import (BLACK, BLUE, BLUE_FILL, GRAY, GREEN, GREEN_FILL, INK, NOTE_FILL, ORANGE, PARCH, PARCH_LINE, RED,
                          RED_FILL, YELLOW, at_pop, bamboo_slips, box, bubble_box, chip, desk, draw_ace, draw_li, draw_wang, gu,
                          name_tag, pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "通鉴里的故事", 4),
    ([6], "未有奇才", 5),
    ([7, 8], "用人如器", 6),
    ([9, 10], "正患己不能知", 7),
    ([11], "一柜子器物", 8),
    ([12, 13], "说回我们自己", 9),
    ([14], "第一步", 10),
    ([15], "第二步", 11),
    ([16], "第三步", 12),
    ([17], "好处", 13),
    ([18, 19, 20, 21], "评论区见", 14),
]

THEME = ZT.get("13")
L = Z.Lesson("13", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(13)]
Z_ = 0.72
KT = Z.Kit(L, R)

NOTES = [
    "出处：司马光《资治通鉴》卷一九二 唐纪八（贞观元年）。",
    "原文：“上令封德彝举贤，久无所举。上诘之，对曰：非不尽心，但于今未有奇才耳！上曰：君子用人如器，各取所长。"
    "古之致治者，岂借才于异代乎？正患己不能知，安可诬一世之人！德彝惭而退。”",
    "器物的比方是节目自加；今人（小李、小王、同事）为虚构示意；古人造型为示意（唐人戴幞头）。",
]

TANG, FENG = "ochre", "gray"


def bowl(c, x, y, s=1.0, a=1.0):
    with K.at(c, x, y, 0, s):
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(-80, -60, 160, 120), 0, 180)
        p.close()
        c.drawPath(p, K.paint("#FFFFFF", a))
        c.drawPath(p, wb.marker(BLUE, 6, a))
        for q in range(5):
            c.drawCircle(-50 + q * 25, -6, 10, K.paint("#F2F2F2", a))


def pot(c, x, y, s=1.0, a=1.0):
    with K.at(c, x, y, 0, s):
        c.drawOval(skia.Rect.MakeXYWH(-70, -60, 140, 120), K.paint("#C98B4B", a))
        c.drawOval(skia.Rect.MakeXYWH(-70, -60, 140, 120), wb.marker("#7A4A1E", 6, a))
        C.line(c, (60, -20), (120, -60), "#7A4A1E", 10, a)
        c.drawRoundRect(skia.Rect.MakeXYWH(-20, -80, 40, 24), 8, 8, K.paint("#7A4A1E", a))


def knife(c, x, y, s=1.0, a=1.0):
    with K.at(c, x, y, -20, s):
        p = P((-90, -10), (60, -30), (90, 0), (-90, 14), close=True)
        c.drawPath(p, K.paint("#DDE3EA", a))
        c.drawPath(p, wb.marker(GRAY, 5, a))
        c.drawRoundRect(skia.Rect.MakeXYWH(-150, -12, 64, 28), 8, 8, K.paint("#7A4A1E", a))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：小李看组员，头顶问号；“太慢”“太嫩”；一个人抱起一摞活
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_look = kq(j, wp(0, 2, 0.4), 0)
    k_q = nx(j, wp(0, 3, 0.4), k_look)
    k_tags = nx(j, wp(1, 1, 0.4), k_q)
    k_pile = nx(j, wp(1, 2, 0.4), k_tags)
    LX = cx - 380
    L.note("太慢", "太嫩")

    def scene(c, kk, T):
        tl, tq, tt, tp = tb(j, k_look), tb(j, k_q), tb(j, k_tags), tb(j, k_pile)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        hy = GY - 290
        with at_pop(c, LX, GY, g):
            if T < tp:
                draw_li(c, LX, GY, 0.95, "flat")
            else:
                C.draw_li(c, LX, GY, 0.95, "sad", lh=(LX - 80, hy - 20), rh=(LX + 80, hy - 20))
                for i in range(4):
                    box(c, LX + (i % 2) * 10 - 5, hy - 50 - i * 52, 240, 48, ("#FFFFFF", NOTE_FILL)[i % 2], GRAY, 4, 4)
        for i, (x, who) in enumerate(((cx - 40, "wang"), (cx + 200, "li"), (cx + 430, "ace"))):
            with at_pop(c, x, GY, g):
                if who == "wang":
                    draw_wang(c, x, GY, 0.8)
                elif who == "li":
                    draw_li(c, x, GY, 0.8, "flat", bag=True)
                else:
                    draw_ace(c, x, GY, 0.8, mood="flat")
            if T >= tq:
                K.text(c, "？", x, cy - 50, 70, "hand", GRAY, clamp01((T - tq - i * 0.1) / 0.2))
        if T >= tt:
            for i, (s_, x) in enumerate((("太慢", cx - 40), ("太嫩", cx + 200))):
                with K.at(c, x, cy - 180, (i * 2 - 1) * 5, C.slam_scale(T - tt - i * 0.15)):
                    chip(c, 0, 0, s_, RED_FILL, RED, 46)
        return None
    ev(j, k_look, scene, "wood_low", 0.6)
    b.hit(j, k_q, "pop", 0.65, "一个个看过去")
    b.hit(j, k_tags, "rim", 0.8, "太慢、太嫩")
    b.hit(j, k_pile, "tom", 0.8, "全揽在自己身上")


screen1()


# ================================================================ 屏 2（drop）：简历堆成小山，红笔一张张打叉
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    dk = L.drop_k()
    k_pile = kq(j, wp(2, 1, 0.4), 0)
    k_x = nx(j, wp(2, 1, 0.95), k_pile)
    L.note("100份", "不满意")

    def scene(c, kk, T):
        tp, tx, td = tb(j, k_pile), tb(j, k_x), tb(j, dk)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        for i in range(9):
            r_, q = divmod(i, 3)
            x, y = cx - 280 + q * 260 + (r_ % 2) * 40, cy - 300 + r_ * 280
            with K.at(c, x, y, (i * 13 % 11) - 5, g):
                c.drawRect(skia.Rect.MakeXYWH(-100, -130, 200, 260), K.paint("#FFFFFF"))
                c.drawRect(skia.Rect.MakeXYWH(-100, -130, 200, 260), wb.marker(BLACK, 5))
                c.drawCircle(-50, -80, 26, wb.marker(GRAY, 4))
                for z in range(3):
                    C.line(c, (-70, 0 + z * 40), (70, 0 + z * 40), GRAY, 4)
                if T >= tx + i * 0.07:
                    f = ease_out(clamp01((T - tx - i * 0.07) / 0.2))
                    c.drawPath(wb.partial(cross(0, 0, 80), f)[0], wb.marker(RED, 10))
        K.text(c, "100份", cx + 380, cy - 470, 54, "hand", GRAY, clamp01(g))
        if T >= td:
            seal(c, cx, cy + 120, "不满意", 80, -6, C.slam_scale(T - td))
        return None
    ev(j, k_pile, scene, "wood_high", 0.65)
    b.hit(j, k_x, "shaker", 0.8, "一张张打叉")
    b.hit(j, dk, "kick", 0.9, "没一个满意")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：隔壁窗户里亮着几颗星，自己这边黑着
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_win = kq(j, wp(3, 0, 0.5), 0)
    k_star = nx(j, wp(3, 1, 0.5), k_win)
    L.note("别人家")

    def scene(c, kk, T):
        tw, ts = tb(j, k_win), tb(j, k_star)
        g = pop_scale(T - tw)
        if g <= 0:
            return None
        for i, (x, lit) in enumerate(((cx - 260, False), (cx + 260, True))):
            with K.at(c, x, cy - 160, 0, g):
                box(c, 0, 0, 380, 420, "#3A4466" if not lit else "#FFF6D6", BLACK, 7, 8)
                C.line(c, (0, -210), (0, 210), BLACK, 5)
                C.line(c, (-190, 0), (190, 0), BLACK, 5)
                if lit and T >= ts:
                    for q in range(4):
                        sx, sy = (-90 + (q % 2) * 180, -100 + (q // 2) * 200)
                        with K.at(c, sx, sy, 0, pop_scale(T - ts - q * 0.08)):
                            pts = [(math.cos(math.radians(-90 + 36 * z)) * (40 if z % 2 == 0 else 16),
                                    math.sin(math.radians(-90 + 36 * z)) * (40 if z % 2 == 0 else 16)) for z in range(10)]
                            c.drawPath(P(*pts, close=True), K.paint(YELLOW))
        if T >= ts:
            K.text(c, "别人家", cx + 260, cy + 120, 56, "hand", ORANGE, clamp01((T - ts) / 0.2))
        with at_pop(c, cx - 260, GY, g):
            draw_li(c, cx - 260, GY, 0.85, "sad")
        return None
    ev(j, k_win, scene, "wood_low", 0.6)
    b.hit(j, k_star, "ding", 0.8, "厉害的人都在别人家")


screen3()


# ================================================================ 屏 4：竹简“卷一九二”；太宗把空名单交给封德彝；日历翻过很久，名单还是空的
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(4, 0, 0.6), 0)
    k_two = nx(j, wp(4, 2, 0.4), k_book)
    k_list = nx(j, wp(4, 3, 0.4), k_two)
    k_cal = nx(j, wp(5, 0, 0.6), k_list)
    k_empty = nx(j, wp(5, 1, 0.5), k_cal)
    KT.book(j, k_book, "卷一九二", "唐纪八")
    L.note("唐太宗", "封德彝", "名单", "空")

    def scene(c, kk, T):
        tt, tl, tc, te = tb(j, k_two), tb(j, k_list), tb(j, k_cal), tb(j, k_empty)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        TX, FX = cx + 40, cx + 400
        with at_pop(c, TX, GY, g):
            gu(c, TX, GY, 0.85, TANG, hat="futou", beard="black", rh=(TX + 150, GY - 250) if T >= tl else None)
            name_tag(c, TX, GY - 430, "唐太宗", "#8A5A1E", 36)
        with at_pop(c, FX, GY, g):
            gu(c, FX, GY, 0.8, FENG, hat="futou", beard="white", lh=(FX - 140, GY - 240) if T >= tl else None)
            name_tag(c, FX, GY - 410, "封德彝", "#5E5E58", 36)
        if T >= tl:
            with K.at(c, cx + 230, GY - 260, 0, pop_scale(T - tl)):
                box(c, 0, 0, 160, 200, "#FFFFFF", BLACK, 5, 6)
                K.text(c, "名单", 0, -60, 36, "serif_black", INK)
        if T >= tc:
            with K.at(c, cx + 220, cy - 300, 0, pop_scale(T - tc)):
                box(c, 0, 0, 220, 180, "#FFFFFF", BLACK, 5, 10)
                c.drawRect(skia.Rect.MakeXYWH(-110, -90, 220, 50), K.paint(RED_FILL))
                n = int(lerp(1, 90, clamp01((T - tc) / 0.8)))
                K.text(c, f"{n}天", 0, 30, 60, "black", RED)
        if T >= te:
            K.text(c, "空", cx + 230, GY - 230, 70, "hand", RED, clamp01((T - te) / 0.2))
        return None
    L.note("天")
    b.custom(j, k_two, k_two + 0.3, scene, sfx="tom", gain=0.75)
    b.hit(j, k_list, "pop", 0.7, "推荐人才")
    b.hit(j, k_cal, "shaker", 0.7, "过了很久")
    b.hit(j, k_empty, "rim", 0.8, "一个也没推荐")


screen4()


# ================================================================ 屏 5：封德彝摊手“没有奇才”
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_feng = 0
    k_try = kq(j, wp(6, 1, 0.5), 1)
    k_none = nx(j, wp(6, 2, 0.5), k_try)
    FX = cx - 200
    L.note("尽力了", "没有奇才")

    def scene(c, sc, T):
        tt, tn = tb(j, k_try), tb(j, k_none)
        hy = GY - 290
        with at_pop(c, FX, GY, sc):
            gu(c, FX, GY, 1.0, FENG, hat="futou", beard="white", mood="sad",
               lh=(FX - 160, hy + 120) if T >= tn else None, rh=(FX + 160, hy + 120) if T >= tn else None)
            name_tag(c, FX, GY - 450, "封德彝", "#5E5E58", 40)
        if T >= tt:
            with K.at(c, FX + 300, cy - 330, 0, pop_scale(T - tt)):
                bubble_box(c, 0, 0, 260, 110, -1)
                K.text(c, "尽力了", 0, 0, 54, "hand", INK)
        if T >= tn:
            with K.at(c, cx + 300, cy - 50, -6, C.slam_scale(T - tn)):
                chip(c, 0, 0, "没有奇才", GRAY_FILL, GRAY, 56)
        return None
    ev(j, k_feng, L.pop_fn(j, k_feng, scene), "muyu", 0.6)
    b.hit(j, k_try, "pop", 0.7, "我尽力了")
    b.hit(j, k_none, "rim", 0.8, "没有奇才")


GRAY_FILL = "#D9DCE1"
screen5()


# ================================================================ 屏 6：太宗指向一柜子器物，“各取所长”；从前的君主难道向别的朝代借人
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_tang = 0
    k_cab = kq(j, wp(7, 1, 0.4), 1)
    k_each = nx(j, wp(7, 2, 0.4), k_cab)
    k_borrow = nx(j, wp(8, 2, 0.4), k_each)
    k_no = nx(j, wp(8, 3, 0.4), k_borrow)
    TX = cx - 380
    L.note("各取所长", "借人？")

    def scene(c, sc, T):
        tc, te, tbw, tn = tb(j, k_cab), tb(j, k_each), tb(j, k_borrow), tb(j, k_no)
        with at_pop(c, TX, GY, sc):
            gu(c, TX, GY, 0.95, TANG, hat="futou", beard="black", mood="smile", rh=(TX + 170, GY - 330) if T >= tc else None)
            name_tag(c, TX, GY - 450, "唐太宗", "#8A5A1E", 40)
        if T >= tc:
            with K.at(c, cx + 150, cy - 140, 0, pop_scale(T - tc)):
                box(c, 0, 0, 520, 500, "#E3D2BE", "#5E4128", 7, 8)
                C.line(c, (-260, 0), (260, 0), "#5E4128", 6)
                bowl(c, -130, -80, 0.8)
                pot(c, 120, -90, 0.8)
                knife(c, 0, 140, 0.9)
        if T >= te:
            with K.at(c, cx + 150, cy + 200, 0, C.slam_scale(T - te)):
                chip(c, 0, 0, "各取所长", NOTE_FILL, ORANGE, 56)
        if T >= tbw:
            with K.at(c, cx + 150, cy - 450, 0, pop_scale(T - tbw)):
                bubble_box(c, 0, 0, 260, 100, 1)
                K.text(c, "借人？", 0, 0, 54, "hand", INK)
            if T >= tn:
                c.drawPath(cross(cx + 150, cy - 450, 70), wb.marker(RED, 10))
        return None
    ev(j, k_tang, L.pop_fn(j, k_tang, scene), "muyu", 0.6)
    b.hit(j, k_cab, "wood_high", 0.7, "一柜子器物")
    b.hit(j, k_each, "kick", 0.85, "各取所长")
    b.hit(j, k_borrow, "pop", 0.7, "难道向别的朝代借人")
    b.hit(j, k_no, "rim", 0.75, "借不来")


screen6()


# ================================================================ 屏 7：一只蒙着的眼睛，揭开后看到一群人才；封德彝低头退下
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_eye = kq(j, wp(9, 1, 0.4), 0)
    k_open = nx(j, wp(9, 3, 0.4), k_eye)
    k_leave = nx(j, wp(10, 1, 0.4), k_open)
    L.note("看不出来")

    def scene(c, kk, T):
        te, to, tl = tb(j, k_eye), tb(j, k_open), tb(j, k_leave)
        g = pop_scale(T - te)
        if g <= 0:
            return None
        op = ease_out(clamp01((T - to) / 0.4)) if T >= to else 0
        with K.at(c, cx, cy - 300, 0, g):
            c.drawOval(skia.Rect.MakeXYWH(-200, -90, 400, 180), K.paint("#FFFFFF"))
            c.drawOval(skia.Rect.MakeXYWH(-200, -90, 400, 180), wb.marker(INK, 7))
            c.drawCircle(0, 0, 60, K.paint(INK))
            c.drawCircle(18, -18, 16, K.paint("#FFFFFF"))
            c.save()
            c.translate(0, -200 * op)
            c.rotate(-15 * op)
            c.drawRoundRect(skia.Rect.MakeXYWH(-240, -60, 480, 120), 30, 30, K.paint("#5E4128", 1 - 0.7 * op))
            c.restore()
        if T < to:
            K.text(c, "看不出来", cx, cy - 120, 52, "hand", GRAY, clamp01(g))
        if op > 0:
            for i in range(5):
                x = cx - 360 + i * 180
                with at_pop(c, x, cy + 120, pop_scale(T - to - i * 0.08)):
                    gu(c, x, cy + 120, 0.45, ("blue", "green", "teal", "red", "brown")[i], hat="futou",
                       beard="black" if i % 2 else None, mood="smile")
                sparkle(c, x, cy - 30, T - to - i * 0.08, YELLOW, 6, 30, 70)
        if T >= tl:
            x, dy, _ = C.walk(T, tl, 1.0, cx + 300, cx + 500, 6)
            with at_pop(c, x, GY + dy, pop_scale(T - tl + 0.3)):
                gu(c, x, GY + dy, 0.6, FENG, hat="futou", beard="white", mood="sad", bow=True)
        return None
    ev(j, k_eye, scene, "wood_low", 0.6)
    b.hit(j, k_open, "ding", 0.9, "揭开看到人才")
    b.hit(j, k_leave, "wood_low", 0.7, "惭愧退下")


screen7()


# ================================================================ 屏 8：碗盛饭、壶倒水、刀切菜，逐个亮起
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_b = kq(j, wp(11, 1, 0.2), 0)
    k_p = nx(j, wp(11, 1, 0.8), k_b)
    k_k = nx(j, wp(11, 2, 0.4), k_p)
    k_all = nx(j, wp(11, 3, 0.4), k_k)
    L.note("盛饭", "倒水", "切菜", "没有废的")

    def scene(c, kk, T):
        tbw, tp, tk, ta = tb(j, k_b), tb(j, k_p), tb(j, k_k), tb(j, k_all)
        for i, (t0, fn, lab, x) in enumerate(((tbw, bowl, "盛饭", cx - 330), (tp, pot, "倒水", cx), (tk, knife, "切菜", cx + 330))):
            g = pop_scale(T - t0)
            if g <= 0:
                continue
            with K.at(c, x, cy - 120, 0, g):
                c.drawCircle(0, 0, 150, K.paint(NOTE_FILL if T < ta else GREEN_FILL))
                c.drawCircle(0, 0, 150, wb.marker(ORANGE if T < ta else GREEN, 6))
                fn(c, 0, 0, 1.0)
                K.text(c, lab, 0, 210, 54, "hand", INK)
        if T >= ta:
            with K.at(c, cx, cy + 330, 0, C.slam_scale(T - ta)):
                chip(c, 0, 0, "没有废的", GREEN_FILL, GREEN, 60)
        return None
    ev(j, k_b, scene, "pop", 0.75)
    b.hit(j, k_p, "pop", 0.75, "壶倒水")
    b.hit(j, k_k, "pop", 0.75, "刀切菜")
    b.hit(j, k_all, "kick", 0.85, "没有一样是废的")


screen8()


# ================================================================ 屏 9：小李被活压得只看到眼前一小块；“三步”
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_tunnel = kq(j, wp(12, 2, 0.4), 1)
    k_3 = nx(j, wp(13, 1, 0.5), k_tunnel)
    LX = cx - 260
    L.note("三步")

    def scene(c, sc, T):
        tt = tb(j, k_tunnel)
        hy = GY - 290
        with at_pop(c, LX, GY, sc):
            C.draw_li(c, LX, GY, 1.0, "sad", lh=(LX - 80, hy - 30), rh=(LX + 80, hy - 30))
            for i in range(4):
                box(c, LX + (i % 2) * 10 - 5, hy - 60 - i * 52, 240, 48, ("#FFFFFF", NOTE_FILL)[i % 2], GRAY, 4, 4)
        if T >= tt:
            f = ease_out(clamp01((T - tt) / 0.5))
            p = skia.Path()
            p.addRect(skia.Rect.MakeXYWH(cx - 600, cy - 600, 1200, 1300))
            p.addCircle(LX + 60, hy + 10, lerp(600, 160, f))
            p.setFillType(skia.PathFillType.kEvenOdd)
            c.drawPath(p, K.paint("#000000", 0.25 * f))
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_tunnel, "tom", 0.75, "看不过来")
    L.stamp_ev(j, k_3, "三步", cx + 280, cy - 300, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen9()


# ================================================================ 屏 10：第一步：组员名单旁写上各自最拿手的一件事
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    k_list = kq(j, wp(14, 0, 0.6), 1)
    k_rows = nx(j, wp(14, 2, 0.4), k_list)
    ROWS = [("小王", "做事细"), ("老周", "能说会道"), ("小赵", "做表快")]
    L.note(*[f"{a}：{b_}" for a, b_ in ROWS], "最拿手")

    def scene(c, kk, T):
        tl, tr = tb(j, k_list), tb(j, k_rows)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with K.at(c, cx, cy, 0, g):
            box(c, 0, 0, 760, 560, "#FFFFFF", BLUE, 7, 14)
            K.text(c, "最拿手", 0, -210, 56, "hand", BLUE)
            for i, (a_, b_) in enumerate(ROWS):
                y = -80 + i * 120
                c.drawCircle(-280, y, 40, K.paint(BLUE_FILL))
                K.text(c, a_, -280, y, 34, "hand", INK)
                a = clamp01((T - tr - i * 0.2) / 0.25)
                K.text(c, f"{a_}：{b_}", -200, y, 52, "hand", INK, a, "left")
                if a >= 1:
                    c.drawPath(check(300, y, 28), wb.marker(GREEN, 8))
        return None
    ev(j, k_list, scene, "wood_high", 0.65)
    b.hit(j, k_rows, "shaker", 0.75, "写下拿手的事")


screen10()


# ================================================================ 屏 11：第二步：核数据的事连到细致的人，跑客户的事连到嘴甜的人
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_tasks = kq(j, wp(15, 0, 0.6), 1)
    k_l1 = nx(j, wp(15, 1, 0.5), k_tasks)
    k_l2 = nx(j, wp(15, 2, 0.5), k_l1)
    L.note("核数据", "跑客户", "细致", "嘴甜")

    def scene(c, kk, T):
        tt, t1, t2 = tb(j, k_tasks), tb(j, k_l1), tb(j, k_l2)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        for i, (s_, y) in enumerate((("核数据", cy - 250), ("跑客户", cy + 30))):
            with K.at(c, cx - 300, y, 0, g):
                box(c, 0, 0, 260, 110, NOTE_FILL, ORANGE, 5, 12)
                K.text(c, s_, 0, 0, 52, "hand", INK)
        with at_pop(c, cx + 300, cy - 120, g):
            draw_wang(c, cx + 300, cy - 120, 0.55)
        K.text(c, "细致", cx + 300, cy - 400, 44, "hand", BLUE, clamp01(g))
        with at_pop(c, cx + 300, GY, g):
            draw_ace(c, cx + 300, GY, 0.6, mood="laugh")
        K.text(c, "嘴甜", cx + 450, GY - 150, 44, "hand", ORANGE, clamp01(g))
        for t0, (a, z) in ((t1, ((cx - 170, cy - 250), (cx + 230, cy - 230))), (t2, ((cx - 170, cy + 30), (cx + 230, GY - 120)))):
            if T >= t0:
                f = ease_out(clamp01((T - t0) / 0.4))
                c.drawPath(wb.partial(wb.arrow(a, z, 0.2, 30), f)[0], wb.marker(GREEN, 8))
        return None
    ev(j, k_tasks, scene, "wood_high", 0.65)
    b.hit(j, k_l1, "pop", 0.75, "细致的去核数据")
    b.hit(j, k_l2, "pop", 0.75, "嘴甜的去跑客户")


screen11()


# ================================================================ 屏 12：第三步：小李对着镜子问：我看清了吗？
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_mir = kq(j, wp(16, 0, 0.6), 1)
    k_ask = nx(j, wp(16, 2, 0.4), k_mir)
    MX = cx + 220
    L.note("看清了吗？")

    def scene(c, kk, T):
        tm, ta = tb(j, k_mir), tb(j, k_ask)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        with K.at(c, MX, cy, 0, g):
            c.drawRoundRect(skia.Rect.MakeXYWH(-160, -300, 320, 560), 150, 150, K.paint("#E8EEF8"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-160, -300, 320, 560), 150, 150, wb.marker(GRAY, 8))
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(MX - 160, cy - 300, 320, 560), 150, 150))
        draw_li(c, MX, cy + 200, 0.75, "flat", alpha=0.5)
        c.restore()
        with at_pop(c, cx - 300, GY, g):
            draw_li(c, cx - 300, GY, 0.95, "flat", rh=(cx - 160, GY - 330) if T >= ta else None)
        if T >= ta:
            with K.at(c, cx - 200, cy - 330, 0, C.slam_scale(T - ta)):
                bubble_box(c, 0, 0, 340, 120, -1)
                K.text(c, "看清了吗？", 0, 0, 54, "hand", RED)
        return None
    ev(j, k_mir, scene, "wood_low", 0.6)
    b.hit(j, k_ask, "rim", 0.8, "先问自己")


screen12()


# ================================================================ 屏 13：好处：组员各自干得顺手，小李肩上轻了
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_team = kq(j, wp(17, 0, 0.6), 0)
    k_smooth = nx(j, wp(17, 1, 0.5), k_team)
    k_light = nx(j, wp(17, 2, 0.5), k_smooth)
    L.note("顺手")

    def scene(c, kk, T):
        tt, ts, tl = tb(j, k_team), tb(j, k_smooth), tb(j, k_light)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        for i, (x, who) in enumerate(((cx - 100, "wang"), (cx + 140, "li"), (cx + 380, "ace"))):
            with at_pop(c, x, GY, g):
                if who == "wang":
                    draw_wang(c, x, GY, 0.75, mood="smile" if T >= ts else "flat")
                elif who == "li":
                    draw_li(c, x, GY, 0.75, "smile" if T >= ts else "flat", bag=True)
                else:
                    draw_ace(c, x, GY, 0.75, mood="smile" if T >= ts else "flat")
                box(c, x, GY - 300, 120, 50, NOTE_FILL, ORANGE, 4, 6)
            if T >= ts:
                c.drawPath(check(x + 80, GY - 360, 22), wb.marker(GREEN, 7))
        LX = cx - 400
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.9, "smile" if T >= tl else "flat",
                    lh=(LX - 60, GY - 330) if T >= tl else None, rh=(LX + 60, GY - 330) if T >= tl else None)
        if T >= tl:
            sparkle(c, LX, GY - 380, T - tl, YELLOW, 10, 50, 120)
            K.text(c, "顺手", cx + 140, cy - 200, 64, "hand", GREEN, clamp01((T - ts) / 0.2))
        return None
    ev(j, k_team, scene, "wood_low", 0.6)
    b.hit(j, k_smooth, "shaker", 0.7, "越用越顺手")
    b.hit(j, k_light, "ding", 0.85, "不用一个人扛")


screen13()


# ================================================================ 屏 14：评论区；小李给同事点赞；下一讲预告
def _enc(c, T, te, th, cx, cy):
    LX, LY = cx - 300, cy + 640
    with at_pop(c, LX, LY, pop_scale(T - te)):
        draw_li(c, LX, LY, 0.9, "smile", rh=(LX + 150, LY - 300))
        with K.at(c, LX + 170, LY - 320, -10):
            c.drawRoundRect(skia.Rect.MakeXYWH(-30, -20, 60, 60), 18, 18, K.paint("#FFFFFF"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-30, -20, 60, 60), 18, 18, wb.marker(BLACK, 5))
            C.line(c, (-10, -20), (-10, -60), BLACK, 12)
    with at_pop(c, cx + 200, LY, pop_scale(T - te - 0.2)):
        draw_wang(c, cx + 200, LY, 0.9, mood="smile" if T >= th else "flat")
    if T >= th:
        sparkle(c, cx + 200, LY - 300, T - th, YELLOW, 10, 60, 140)
        K.text(c, "被看见", cx + 200, LY - 440, 60, "hand", GREEN, clamp01((T - th) / 0.2))


L.note("被看见")


def _icon(c, x, y, t):
    big = 1 + 0.3 * (0.5 + 0.5 * math.sin(t * 3))
    c.drawOval(skia.Rect.MakeXYWH(x - 30 * big, y - 50 * big, 60 * big, 100 * big), K.paint("#FBE3CF"))
    c.drawOval(skia.Rect.MakeXYWH(x - 30 * big, y - 50 * big, 60 * big, 100 * big), wb.marker(INK, 5))


KT.ending(14, "谁有别人比不上的本事？", ["做表最快", "最会安慰人", "记性特别好"], 19, 20, _enc, 21,
          ["只听一个人说", "为什么总看走眼？"], enc_piece=0, next_icon=_icon)

# ================================================================ 收尾
L.finish(cover_shot=6, square_shot=7, notes=NOTES)
L.export(globals())
