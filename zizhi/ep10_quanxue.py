"""《资治通鉴》10 劝学：天天加班，哪还有空学东西？（白板手绘 + AI 旁白，竖屏 2:3）

自测：开头一张三道题的测试卡，符合一条记一分（计分牌逐题跳），两分以上往下看；再讲孙权劝吕蒙读书——“没空”“孤岂欲卿治经为博士邪”
“卿言多务，孰若孤”、吕蒙就学、鲁肃“非复吴下阿蒙”、“士别三日”、拜母结友；最后加班族三步（每天十页、零碎时间、讲给同事听）。
本讲是墨绿黑板底（深色）。古人的屏画在卷轴框里，今人在办公室。文案见 zizhi/PLAN.md「### 10」。
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
                          RED_FILL, YELLOW, at_pop, bamboo_slips, box, bubble_box, chip, desk, draw_ace, draw_li, draw_wang,
                          gu, name_tag, phone, pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "小测试", 1),
    ([2], "小测试", 2),
    ([3], "小测试", 3),
    ([4], "小测试", 4),
    ([5, 6], "通鉴里的故事", 5),
    ([7, 8], "没空", 6),
    ([9, 10], "孰若孤", 7),
    ([11, 12], "刮目相看", 8),
    ([13], "结友而别", 9),
    ([14, 15], "说回我们自己", 10),
    ([16], "第一步", 11),
    ([17], "第二步", 12),
    ([18], "第三步", 13),
    ([19], "好处", 14),
    ([20, 21, 22, 23], "评论区见", 15),
]

THEME = ZT.get("10")
L = Z.Lesson("10", SCREENS, drop_screen=2, board_size=(5000, 12000), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(14)]
Z_ = 0.72
KT = Z.Kit(L, R, frame_alpha=0.12)

NOTES = [
    "出处：司马光《资治通鉴》卷六十六 汉纪五十八（建安十五年前后，纪年待核）。",
    "原文：权谓吕蒙曰“卿今当涂掌事，不可不学”；蒙辞以军中多务；权曰“孤岂欲卿治经为博士邪！但当涉猎，见往事耳。卿言多务，孰若孤？"
    "孤常读书，自以为大有所益”；蒙乃始就学；鲁肃“卿今者才略，非复吴下阿蒙”；蒙曰“士别三日，即更刮目相待”；肃遂拜蒙母，结友而别。",
    "今人（小李、小王、同事）为虚构示意；古人造型为示意。测试题为节目自拟。",
]

SUN, LV, LU, MA = "purple", "blue", "teal", "red"


def quiz(c, x, y, n_on, hot=None, a=1.0):
    """测试卡：三行“第一题 / 第二题 / 第三题”，前 n_on 行打勾。"""
    box(c, x, y, 520, 330, "#FFFFFF", BLACK, 6, 14, a)
    for i in range(3):
        yy = y - 100 + i * 100
        c.drawRect(skia.Rect.MakeXYWH(x - 220, yy - 26, 52, 52), wb.marker(GRAY, 5, a))
        K.text(c, ("第一题", "第二题", "第三题")[i], x - 60, yy, 46, "hand", RED if hot == i else INK, a)
        if i < n_on:
            c.drawPath(check(x - 194, yy, 30), wb.marker(GREEN, 9, a))


def score(c, x, y, n, a=1.0, pulse=1.0):
    with K.at(c, x, y, 0, pulse):
        c.drawCircle(0, 0, 90, K.paint(NOTE_FILL, a))
        c.drawCircle(0, 0, 90, wb.marker(ORANGE, 7, a))
        K.text(c, f"{n}", 0, -10, 90, "black", RED, a)
        K.text(c, "分", 0, 60, 34, "hand", INK, a)


L.note("第一题", "第二题", "第三题", "分")


def quiz_corner(j, n_from, k_tick):
    """每题屏右上角的计分牌：k_tick 拍从 n_from 跳到 n_from+1。"""
    cx, cy = R[j]

    def fn(c, kk, T):
        g = pop_scale(T - tb(j, 0))
        if g <= 0:
            return None
        tk = tb(j, k_tick)
        n = n_from + (1 if T >= tk else 0)
        pulse = 1 + 0.3 * max(0.0, 1 - (T - tk) / 0.3) if T >= tk else 1
        score(c, cx + 400, cy - 400, n, g, pulse)
        return None
    b.custom(j, 0, 0.3, fn)
    b.hit(j, k_tick, "ding", 0.75, "记一分")


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：测试卡；第一题：日历一年翻过，书签还在第一页
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_card = 0
    k_q1 = kq(j, wp(1, 1, 0.3), 1)
    k_cal = nx(j, wp(1, 1, 0.9), k_q1)
    k_tick = nx(j, wp(1, 2, 0.5), k_cal)
    L.note("1年", "第1页")

    def card(c, kk, T):
        g = pop_scale(T - tb(j, k_card))
        if g <= 0:
            return None
        with K.at(c, cx - 140, cy - 330, -2, g * 0.85):
            quiz(c, 0, 0, 1 if T >= tb(j, k_tick) else 0, 0 if T >= tb(j, k_q1) else None)
        return None
    ev(j, k_card, card, "wood_high", 0.65)

    def scene(c, kk, T):
        tq, tc = tb(j, k_q1), tb(j, k_cal)
        g = pop_scale(T - tq)
        if g <= 0:
            return None
        LX = cx - 330
        with at_pop(c, LX, GY, g):
            desk(c, LX + 200, GY - 170, 380)
            draw_li(c, LX, GY, 0.95, "sad", rh=(LX + 120, GY - 240))
            c.drawCircle(LX + 300, GY - 330, 40, K.paint(YELLOW, 0.8))
        if T >= tc:
            f = clamp01((T - tc) / 0.8)
            with K.at(c, cx + 300, cy + 20, 0, pop_scale(T - tc)):
                box(c, 0, 0, 220, 200, "#FFFFFF", BLACK, 6, 10)
                n = int(lerp(1, 12, f))
                K.text(c, f"{n}月", 0, 10, 70, "black", RED)
                K.text(c, "1年", 0, 140, 44, "hand", INK)
            with K.at(c, cx + 50, cy + 120, 0, pop_scale(T - tc)):
                box(c, 0, 0, 160, 110, "#D5E3F7", BLUE, 5, 6)
                K.text(c, "第1页", 0, 0, 40, "hand", RED)
        return None
    L.note("月")
    b.custom(j, k_q1, k_q1 + 0.3, scene, sfx="pop", gain=0.65)
    b.hit(j, k_cal, "shaker", 0.7, "一年翻过")
    quiz_corner(j, 0, k_tick)


screen1()


# ================================================================ 屏 2（drop）：第二题：待办上“学新东西”一次次往后挪
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    dk = L.drop_k()
    k_list = kq(j, wp(2, 1, 0.3), 0)
    k_move = max(k_list + 1, min(dk - 1, kq(j, wp(2, 2, 0.3), k_list + 1)))
    ROWS = ["回邮件", "周报", "开会", "学新东西"]
    L.note(*ROWS, "待办")

    def scene(c, kk, T):
        tl, tm = tb(j, k_list), tb(j, k_move)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with K.at(c, cx - 120, cy - 60, 0, g):
            box(c, 0, 0, 520, 560, "#FFFFFF", BLACK, 6, 14)
            K.text(c, "待办", 0, -230, 54, "sans_medium", INK)
            pos = [0, 1, 2, 3]
            f = clamp01((T - tm) / 0.8) if T >= tm else 0
            for i, s_ in enumerate(ROWS):
                y = -120 + i * 100
                if i == 3:
                    y += 120 * f + 30 * math.sin(f * 12)
                box(c, 0, y, 420, 80, NOTE_FILL if i == 3 else "#F2F2F2", ORANGE if i == 3 else GRAY, 4, 10)
                K.text(c, s_, 0, y, 46, "hand", RED if i == 3 else INK)
            if T >= tm:
                K.text(c, "下周", 300, 290, 44, "hand", GRAY, f)
        return None
    L.note("下周")
    ev(j, k_list, scene, "wood_high", 0.65)
    b.hit(j, k_move, "shaker", 0.75, "又往后挪")
    quiz_corner(j, 1, dk)
    b.hit(j, dk, "kick", 0.85, "第二题也中")
    b.shots[j].shake = [(dk, 9.0)]
    b.shots[j].flashes = [(dk, 0.2)]


screen2()


# ================================================================ 屏 3：第三题：会上大家聊新词，小李头顶问号
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_meet = kq(j, wp(3, 1, 0.4), 0)
    k_q = nx(j, wp(3, 2, 0.4), k_meet)
    k_tick = nx(j, wp(3, 2, 0.95), k_q)
    L.note("新工具", "新玩法", "？")

    def scene(c, kk, T):
        tm, tq = tb(j, k_meet), tb(j, k_q)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            box(c, cx, GY - 150, 980, 60, "#E7D6BA", "#8B6B43", 6, 10)
            draw_wang(c, cx - 380, GY, 0.85, mood="smile")
            draw_ace(c, cx - 150, GY, 0.85, mood="laugh")
            draw_li(c, cx + 300, GY, 0.85, "sad" if T >= tq else "flat")
        for i, s_ in enumerate(("新工具", "新玩法")):
            with K.at(c, cx - 300 + i * 220, cy - 120 - i * 80, 0, pop_scale(T - tm - 0.2 - i * 0.15)):
                bubble_box(c, 0, 0, 230, 100, -1)
                K.text(c, s_, 0, 0, 46, "hand", INK)
        if T >= tq:
            with K.at(c, cx + 300, cy - 60, 0, C.slam_scale(T - tq)):
                K.text(c, "？", 0, 0, 140, "hand", RED)
        return None
    ev(j, k_meet, scene, "wood_low", 0.6)
    b.hit(j, k_q, "rim", 0.8, "插不上话")
    quiz_corner(j, 2, k_tick)


screen3()


# ================================================================ 屏 4：计分牌跳到两分以上，指针指向“这一讲给你”
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_board = 0
    k_two = kq(j, wp(4, 0, 0.5), 1)
    k_you = nx(j, wp(4, 1, 0.5), k_two)
    L.note("两分以上", "给你的")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_board))
        if g <= 0:
            return None
        tt, ty = tb(j, k_two), tb(j, k_you)
        with K.at(c, cx - 160, cy - 160, 0, g):
            quiz(c, 0, 0, 3)
        score(c, cx + 300, cy - 300, 3, g, 1 + 0.3 * max(0.0, 1 - (T - tt) / 0.3) if T >= tt else 1)
        if T >= tt:
            with K.at(c, cx + 300, cy - 120, 0, pop_scale(T - tt)):
                chip(c, 0, 0, "两分以上", RED_FILL, RED, 48)
        if T >= ty:
            f = ease_out(clamp01((T - ty) / 0.4))
            c.drawPath(wb.arrow((cx + 100, cy + 120), (cx + 100 - 60 * f, cy + 300), 0.2, 34), wb.marker(ORANGE, 10))
            with K.at(c, cx - 60, cy + 380, -4, C.slam_scale(T - ty)):
                box(c, 0, 0, 420, 130, NOTE_FILL, ORANGE, 6, 14)
                K.text(c, "给你的", 0, 0, 70, "hand", RED)
        return None
    ev(j, k_board, scene, "wood_high", 0.6)
    b.hit(j, k_two, "tom", 0.75, "两分以上")
    b.hit(j, k_you, "kick", 0.85, "这一讲给你")


screen4()


# ================================================================ 屏 5：竹简“卷六十六”；吕蒙（盔甲、拿刀）；孙权拍拍他：得学点东西
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(5, 0, 0.3), 0)
    k_lv = nx(j, wp(5, 2, 0.3), k_book)
    k_sun = nx(j, wp(6, 0, 0.5), k_lv)
    k_learn = nx(j, wp(6, 2, 0.4), k_sun)
    KT.book(j, k_book, "卷六十六", "汉纪五十八")
    L.note("吕蒙", "孙权", "得学点")

    def scene(c, kk, T):
        tl, ts, tle = tb(j, k_lv), tb(j, k_sun), tb(j, k_learn)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        LX = cx + 330
        with at_pop(c, LX, GY, g):
            gu(c, LX, GY, 0.9, LV, hat="helmet", beard="black", mood="flat", rh=(LX + 120, GY - 330))
            C.line(c, (LX + 120, GY - 330), (LX + 200, GY - 470), "#9AA3AD", 10)
            name_tag(c, LX, GY - 430, "吕蒙", "#2F5B8E", 40)
        if T >= ts:
            SX = cx + 40
            with at_pop(c, SX, GY, pop_scale(T - ts)):
                gu(c, SX, GY, 0.9, SUN, hat="guan", beard="black", mood="smile", rh=(SX + 160, GY - 290))
                name_tag(c, SX, GY - 430, "孙权", "#6B3F7A", 40)
        if T >= tle:
            with K.at(c, cx + 180, cy - 330, -4, C.slam_scale(T - tle)):
                chip(c, 0, 0, "得学点", NOTE_FILL, ORANGE, 54)
        return None
    b.custom(j, k_lv, k_lv + 0.3, scene, sfx="tom", gain=0.75)
    b.hit(j, k_sun, "pop", 0.7, "孙权劝")
    b.hit(j, k_learn, "rim", 0.75, "得学点东西")


screen5()


# ================================================================ 屏 6：吕蒙摆手“没空”；孙权：不用当博士，翻翻书就行
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_no = kq(j, wp(7, 2, 0.3), 0)
    k_hat = nx(j, wp(8, 1, 0.4), k_no)
    k_book = nx(j, wp(8, 3, 0.4), k_hat)
    LX, SX = cx - 360, cx + 360
    L.note("没空", "博士", "从前的事")

    def scene(c, kk, T):
        tn, th, tbk = tb(j, k_no), tb(j, k_hat), tb(j, k_book)
        g = pop_scale(T - tb(j, 0))
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            gu(c, LX, GY, 0.9, LV, hat="helmet", beard="black",
               rh=(LX + 140 + 20 * math.sin((T - tn) * 12), GY - 300) if T >= tn else None)
        with at_pop(c, SX, GY, g):
            gu(c, SX, GY, 0.9, SUN, hat="guan", beard="black", mood="smile")
        if T >= tn:
            with K.at(c, LX + 60, cy - 330, 0, C.slam_scale(T - tn)):
                bubble_box(c, 0, 0, 220, 110, -1)
                K.text(c, "没空", 0, 0, 60, "hand", RED)
        if T >= th:
            with K.at(c, cx + 60, cy - 300, 0, pop_scale(T - th)):
                c.drawRect(skia.Rect.MakeXYWH(-90, -20, 180, 40), K.paint(INK))
                c.drawPath(P((-120, -20), (0, -70), (120, -20), close=True), K.paint(INK))
                K.text(c, "博士", 0, 60, 44, "hand", INK)
                c.drawPath(cross(0, 0, 110), wb.marker(RED, 12))
        if T >= tbk:
            with K.at(c, cx + 60, cy + 30, 0, pop_scale(T - tbk)):
                bamboo_slips(c, 0, 0, 300, 220, n=5)
                K.text(c, "从前的事", 0, 0, 50, "serif_black", INK)
            sparkle(c, cx + 60, cy + 30, T - tbk, YELLOW, 8, 60, 140)
        return None
    ev(j, 0, scene, "muyu", 0.6)
    b.hit(j, k_no, "rim", 0.8, "没空")
    b.hit(j, k_hat, "wood_high", 0.7, "不用当博士")
    b.hit(j, k_book, "ding", 0.8, "翻翻书就行")


screen6()


# ================================================================ 屏 7：孙权指着自己一摞文书、手里还捧着书；吕蒙坐下翻书
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_pile = kq(j, wp(9, 1, 0.4), 0)
    k_read = nx(j, wp(9, 2, 0.5), k_pile)
    k_gain = nx(j, wp(9, 3, 0.4), k_read)
    k_lv = nx(j, wp(10, 1, 0.4), k_gain)
    SX = cx - 300
    L.note("我忙", "收获")

    def scene(c, kk, T):
        tp, tr, tg, tl = tb(j, k_pile), tb(j, k_read), tb(j, k_gain), tb(j, k_lv)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        with at_pop(c, SX, GY, g):
            for i in range(6):
                box(c, SX + 220 + (i % 2) * 10, GY - 30 - i * 50, 200, 44, PARCH, PARCH_LINE, 4, 4)
            hy = GY - 290 * 0.95
            gu(c, SX, GY, 0.95, SUN, hat="guan", beard="black", mood="smile",
               lh=(SX - 40, hy + 140) if T >= tr else None, rh=(SX + 40, hy + 140) if T >= tr else (SX + 150, GY - 300))
            if T >= tr:
                bamboo_slips(c, SX, hy + 120, 140, 90, n=3)
        if T >= tp:
            K.text(c, "我忙", SX + 230, cy - 60, 54, "hand", ORANGE, clamp01((T - tp) / 0.2))
        if T >= tg:
            sparkle(c, SX, GY - 380, T - tg, YELLOW, 10, 60, 140)
            with K.at(c, SX, cy - 380, 0, C.slam_scale(T - tg)):
                chip(c, 0, 0, "收获", GREEN_FILL, GREEN, 54)
        if T >= tl:
            LX = cx + 330
            with at_pop(c, LX, GY, pop_scale(T - tl)):
                box(c, LX, GY - 80, 240, 40, "#C98B4B", "#7A4A1E", 4, 6)
                gu(c, LX, GY - 40, 0.75, LV, hat="helmet", beard="black", lh=(LX - 50, GY - 190), rh=(LX + 50, GY - 190))
                bamboo_slips(c, LX, GY - 200, 130, 80, n=3)
        return None
    ev(j, k_pile, scene, "wood_low", 0.6)
    b.hit(j, k_read, "pop", 0.7, "孙权也读书")
    b.hit(j, k_gain, "ding", 0.75, "收获很大")
    b.hit(j, k_lv, "tom", 0.75, "吕蒙开始读书")


screen7()


# ================================================================ 屏 8：鲁肃和吕蒙对坐聊天，鲁肃眼睛瞪大；“士别三日”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_sit = kq(j, wp(11, 1, 0.4), 0)
    k_wow = nx(j, wp(11, 2, 0.5), k_sit)
    k_amen = nx(j, wp(11, 4, 0.4), k_wow)
    k_three = nx(j, wp(12, 1, 0.5), k_amen)
    k_eyes = nx(j, wp(12, 2, 0.5), k_three)
    L.note("鲁肃", "吕蒙", "吴下阿蒙", "士别三日", "刮目相待")

    def scene(c, kk, T):
        ts, tw, ta, tt, te = tb(j, k_sit), tb(j, k_wow), tb(j, k_amen), tb(j, k_three), tb(j, k_eyes)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            box(c, cx, GY - 100, 260, 40, "#C98B4B", "#7A4A1E", 4, 6)
            gu(c, cx - 260, GY, 0.85, LU, hat="guan", beard="black", mood="o" if T >= tw else "smile")
            name_tag(c, cx - 260, GY - 390, "鲁肃", "#2C6E68", 38)
            gu(c, cx + 260, GY, 0.85, LV, hat="guan", beard="black", mood="smile", rh=(cx + 120, GY - 260))
            name_tag(c, cx + 260, GY - 390, "吕蒙", "#2F5B8E", 38)
        if T >= tw:
            K.text(c, "！", cx - 200, cy - 70, 90, "hand", RED, clamp01((T - tw) / 0.2))
        if T >= ta:
            with K.at(c, cx - 230, cy - 300, -4, pop_scale(T - ta)):
                chip(c, 0, 0, "吴下阿蒙", GRAY_FILL, GRAY, 46)
                c.drawPath(cross(0, 0, 90), wb.marker(RED, 9))
        if T >= tt:
            with K.at(c, cx + 250, cy - 360, 0, pop_scale(T - tt)):
                bamboo_slips(c, 0, 0, 120, 360, n=1)
                slip_text(c, 0, -140, "士别三日", 60, INK)
        if T >= te:
            with K.at(c, cx + 60, cy - 120, 0, C.slam_scale(T - te)):
                K.text(c, "刮目相待", 0, 0, 72, "serif_black", RED)
        return None
    L.note("！")
    ev(j, k_sit, scene, "muyu", 0.65)
    b.hit(j, k_wow, "rim", 0.8, "鲁肃大吃一惊")
    b.hit(j, k_amen, "pop", 0.7, "早不是阿蒙了")
    b.hit(j, k_three, "bangzi", 0.75, "士别三日")
    b.hit(j, k_eyes, "kick", 0.85, "换个眼光看")


GRAY_FILL = "#D9DCE1"
screen8()


# ================================================================ 屏 9：鲁肃向吕蒙的母亲行礼，两人拱手告别
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_ma = kq(j, wp(13, 0, 0.6), 0)
    k_bow = nx(j, wp(13, 1, 0.5), k_ma)
    k_friend = nx(j, wp(13, 2, 0.5), k_bow)
    L.note("母亲", "朋友")

    def scene(c, kk, T):
        tm, tb_, tf = tb(j, k_ma), tb(j, k_bow), tb(j, k_friend)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        with at_pop(c, cx + 330, GY, g):
            gu(c, cx + 330, GY, 0.8, MA, hat="lady", mood="smile")
            name_tag(c, cx + 330, GY - 360, "母亲", "#9C2F25", 36)
        with at_pop(c, cx, GY, g):
            gu(c, cx, GY, 0.85, LU, hat="guan", beard="black", mood="smile", bow=T >= tb_)
        with at_pop(c, cx - 330, GY, g):
            gu(c, cx - 330, GY, 0.85, LV, hat="guan", beard="black", mood="smile", bow=T >= tf)
        if T >= tf:
            seal(c, cx - 160, cy - 300, "朋友", 80, -4, C.slam_scale(T - tf))
            sparkle(c, cx - 160, cy - 300, T - tf, YELLOW, 10, 80, 160)
        return None
    ev(j, k_ma, scene, "muyu", 0.6)
    b.hit(j, k_bow, "wood_high", 0.7, "拜见母亲")
    b.hit(j, k_friend, "ding", 0.8, "结友而别")


screen9()


# ================================================================ 屏 10：小李加班到深夜，揉眼睛；“三步”
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_rub = kq(j, wp(14, 1, 0.4), 1)
    k_3 = nx(j, wp(15, 1, 0.5), k_rub)
    LX = cx - 260
    L.note("23:30", "三步")

    def scene(c, sc, T):
        tr = tb(j, k_rub)
        hy = GY - 290
        with at_pop(c, LX, GY, sc):
            desk(c, LX + 200, GY - 170, 380)
            draw_li(c, LX, GY, 1.0, "sad", rh=(LX + 20, hy - 5 + 6 * math.sin((T - tr) * 16)) if T >= tr else (LX + 140, GY - 230))
        with K.at(c, cx + 300, cy - 300, 0, sc):
            box(c, 0, 0, 260, 120, "#3A4466", BLACK, 5, 14)
            K.text(c, "23:30", 0, 0, 60, "black", YELLOW)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_rub, "wood_high", 0.6, "揉眼睛")
    L.stamp_ev(j, k_3, "三步", cx + 300, cy + 60, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen10()


# ================================================================ 屏 11：第一步：一本书只翻十页，书签往前挪一点
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(16, 0, 0.6), 1)
    k_ten = nx(j, wp(16, 1, 0.5), k_book)
    k_rel = nx(j, wp(16, 2, 0.5), k_ten)
    L.note("十页", "跟手上的活有关")

    def scene(c, kk, T):
        tbk, tt, tr = tb(j, k_book), tb(j, k_ten), tb(j, k_rel)
        g = pop_scale(T - tbk)
        if g <= 0:
            return None
        with K.at(c, cx + 60, cy - 120, 0, g):
            c.drawRect(skia.Rect.MakeXYWH(-300, -160, 600, 320), K.paint("#FFFFFF"))
            c.drawRect(skia.Rect.MakeXYWH(-300, -160, 600, 320), wb.marker(BLUE, 6))
            C.line(c, (0, -160), (0, 160), BLUE, 4)
            for q in range(4):
                C.line(c, (-260, -100 + q * 60), (-40, -100 + q * 60), GRAY, 4)
                C.line(c, (40, -100 + q * 60), (260, -100 + q * 60), GRAY, 4)
            f = ease_out(clamp01((T - tt) / 0.6)) if T >= tt else 0
            bx = lerp(-200, 120, f)
            c.drawPath(P((bx - 20, -160), (bx + 20, -160), (bx + 20, -60), (bx, -80), (bx - 20, -60), close=True), K.paint(RED))
        if T >= tt:
            K.text(c, "十页", cx + 60, cy + 110, 70, "hand", RED, clamp01((T - tt) / 0.2))
        if T >= tr:
            with K.at(c, cx + 60, cy + 240, 0, pop_scale(T - tr)):
                chip(c, 0, 0, "跟手上的活有关", GREEN_FILL, GREEN, 46)
        with at_pop(c, cx - 380, GY, g):
            draw_li(c, cx - 380, GY, 0.9, "smile")
        return None
    ev(j, k_book, scene, "wood_high", 0.65)
    b.hit(j, k_ten, "pop", 0.75, "每天十页")
    b.hit(j, k_rel, "ding", 0.75, "跟活有关")


screen11()


# ================================================================ 屏 12：第二步：地铁上、排队时看书，时钟上亮出几段零碎时间
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_sub = kq(j, wp(17, 0, 0.6), 1)
    k_q = nx(j, wp(17, 1, 0.4), k_sub)
    k_sun = nx(j, wp(17, 2, 0.5), k_q)
    L.note("通勤", "排队", "孙权")

    def scene(c, kk, T):
        ts, tq, tsn = tb(j, k_sub), tb(j, k_q), tb(j, k_sun)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        with K.at(c, cx + 250, cy - 200, 0, g):
            c.drawCircle(0, 0, 160, K.paint("#FFFFFF"))
            c.drawPath(wb.clock(0, 0, 160), wb.marker(BLACK, 6))
            for i, (a0, s_) in enumerate(((-80, "通勤"), (60, "排队"))):
                if T >= (ts if i == 0 else tq):
                    p = skia.Path()
                    p.moveTo(0, 0)
                    p.arcTo(skia.Rect.MakeXYWH(-150, -150, 300, 300), a0, 40, False)
                    p.close()
                    c.drawPath(p, K.paint(YELLOW, 0.8))
                    K.text(c, s_, 230 * math.cos(math.radians(a0 + 20)), 230 * math.sin(math.radians(a0 + 20)), 40, "hand", ORANGE)
        LX = cx - 330
        with at_pop(c, LX, GY, g):
            C.line(c, (LX - 40, GY - 400), (LX - 40, GY - 250), GRAY, 6)
            draw_li(c, LX, GY, 0.9, "smile", lh=(LX - 40, GY - 330), rh=(LX + 100, GY - 240))
            phone(c, LX + 120, GY - 260, 0.6)
        if T >= tsn:
            with K.at(c, cx - 30, cy + 120, 0, pop_scale(T - tsn)):
                gu(c, 0, 120, 0.45, SUN, hat="guan", beard="black", lh=(-40, 20), rh=(40, 20))
                bamboo_slips(c, 0, 20, 100, 60, n=2)
                K.text(c, "孙权", 0, -100, 34, "serif_black", "#6B3F7A")
        return None
    ev(j, k_sub, scene, "wood_high", 0.65)
    b.hit(j, k_q, "pop", 0.7, "排队也能看")
    b.hit(j, k_sun, "ding", 0.75, "孙权那么忙都能读")


screen12()


# ================================================================ 屏 13：第三步：小李在茶水间讲给小王听，小王点头
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_pair = kq(j, wp(18, 1, 0.4), 1)
    k_talk = nx(j, wp(18, 1, 0.9), k_pair)
    k_nod = nx(j, wp(18, 2, 0.5), k_talk)
    L.note("我昨天看到……", "茶水间")

    def scene(c, kk, T):
        tp, tt, tn = tb(j, k_pair), tb(j, k_talk), tb(j, k_nod)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            box(c, cx, GY - 170, 260, 30, "#E7D6BA", "#8B6B43", 4, 6)
            draw_li(c, cx - 280, GY, 0.95, "smile", rh=(cx - 150, GY - 330) if T >= tt else None)
            draw_wang(c, cx + 280, GY, 0.95, mood="smile" if T >= tn else "flat")
            K.text(c, "茶水间", cx, GY - 240, 40, "hand", GRAY)
        if T >= tt:
            with K.at(c, cx - 140, cy - 280, 0, C.slam_scale(T - tt)):
                bubble_box(c, 0, 0, 420, 120, -1)
                K.text(c, "我昨天看到……", 0, 0, 50, "hand", INK)
        if T >= tn:
            sparkle(c, cx + 280, cy + 180, T - tn, YELLOW, 8, 50, 110)
        return None
    ev(j, k_pair, scene, "wood_low", 0.6)
    b.hit(j, k_talk, "pop", 0.75, "讲给同事听")
    b.hit(j, k_nod, "ding", 0.75, "小王点头")


screen13()


# ================================================================ 屏 14：半年后的会上，小李接上话，同事们眼睛一亮
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_meet = kq(j, wp(19, 0, 0.6), 0)
    k_talk = nx(j, wp(19, 1, 0.5), k_meet)
    k_wow = nx(j, wp(19, 2, 0.5), k_talk)
    L.note("半年后", "刮目相看")

    def scene(c, kk, T):
        tm, tt, tw = tb(j, k_meet), tb(j, k_talk), tb(j, k_wow)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        K.text(c, "半年后", cx - 360, cy - 420, 56, "hand", GRAY, clamp01(g))
        with at_pop(c, cx, GY, g):
            box(c, cx, GY - 150, 980, 60, "#E7D6BA", "#8B6B43", 6, 10)
            draw_li(c, cx - 380, GY, 0.9, "smile", rh=(cx - 240, GY - 330) if T >= tt else None)
            draw_wang(c, cx - 60, GY, 0.85, mood="o" if T >= tw else "flat")
            draw_ace(c, cx + 260, GY, 0.85, mood="flat")
        if T >= tt:
            with K.at(c, cx - 300, cy - 230, 0, pop_scale(T - tt)):
                bubble_box(c, 0, 0, 260, 110, -1)
                K.text(c, "我来说说", 0, 0, 48, "hand", INK)
        if T >= tw:
            for x in (cx - 60, cx + 260):
                sparkle(c, x, GY - 290 * 0.85, T - tw, YELLOW, 8, 50, 100)
            with K.at(c, cx + 200, cy - 330, 0, C.slam_scale(T - tw)):
                chip(c, 0, 0, "刮目相看", NOTE_FILL, ORANGE, 52)
        return None
    L.note("我来说说")
    ev(j, k_meet, scene, "wood_low", 0.6)
    b.hit(j, k_talk, "pop", 0.75, "接上话")
    b.hit(j, k_wow, "ding", 0.85, "刮目相看")


screen14()


# ================================================================ 屏 15：评论区；一年下来书架上摆满一排；下一讲预告
def _enc(c, T, te, th, cx, cy):
    LX, LY = cx - 300, cy + 640
    with at_pop(c, LX, LY, pop_scale(T - te)):
        draw_li(c, LX, LY, 0.9, "smile", rh=(LX + 140, LY - 300) if T >= th else None)
    n = int(lerp(1, 12, clamp01((T - te) / max(0.4, th - te))))
    SX, SY = cx + 80, cy + 500
    box(c, SX + 160, SY + 20, 560, 20, "#C98B4B", "#7A4A1E", 4, 4)
    for i in range(n):
        h = 120 + (i * 37) % 50
        c.drawRect(skia.Rect.MakeXYWH(SX - 110 + i * 44, SY + 10 - h, 38, h),
                   K.paint(("#D5E3F7", "#F6C3BE", "#D3EDDC", NOTE_FILL)[i % 4]))
        c.drawRect(skia.Rect.MakeXYWH(SX - 110 + i * 44, SY + 10 - h, 38, h), wb.marker(INK, 3))
    if T >= th:
        sparkle(c, SX + 160, SY - 160, T - th, YELLOW, 10, 60, 140)
        K.text(c, "一年", SX + 160, SY + 110, 56, "hand", GREEN, clamp01((T - th) / 0.2))


L.note("一年")


def _icon(c, x, y, t):
    for q in range(3):
        c.drawPath(P((x - 60 + q * 50, y + 60), (x - 40 + q * 50, y - 40)), wb.marker(RED, 6))
    K.text(c, "不行", x, y - 70, 34, "hand", RED)


L.note("不行")
KT.ending(15, "你最近在读哪一本？", ["行业报告", "一本小说", "资治通鉴"], 21, 22, _enc, 23,
          ["想做一件难事", "周围都说不行怎么办？"], enc_piece=0, next_icon=_icon)

# ================================================================ 收尾
L.finish(cover_shot=8, square_shot=6, notes=NOTES)
L.export(globals())
