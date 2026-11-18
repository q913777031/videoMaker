"""《资治通鉴》03 纸上谈兵：说得头头是道，为什么一做就砸？（白板手绘 + AI 旁白，竖屏 2:3）

两人对比：父亲赵奢（打过胜仗、把打仗看得很重）对儿子赵括（兵书背得熟、谁也驳不倒），加上蔺相如“胶柱鼓瑟”、赵母上书两段旁证，
讲到长平之败；今人部分对照“会讲方案的同事”和“方案写得漂亮的自己”，三招落在看人、试做、接手先摸情况。
本讲是墨色黑板底（深色），颜色由 fengtian.theme.Recolor 统一反色。古人的屏画在卷轴框里，今人在办公室。
文案见 zizhi/PLAN.md「### 03」。
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
from zizhi.lesson import (BLACK, BLUE, BLUE_FILL, GRAY, GREEN, GREEN_FILL, INK, NOTE_FILL, ORANGE, RED, RED_FILL, YELLOW,
                          at_pop, bamboo_slips, box, bubble_box, city_wall, desk, draw_ace, draw_li, draw_wang, flag, gu,
                          head_of, pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "通鉴里的故事", 4),
    ([6, 7], "父子谈兵", 5),
    ([8, 9], "赵奢的话", 6),
    ([10, 11], "长平", 7),
    ([12, 13], "换将", 8),
    ([14, 15], "母亲上书", 9),
    ([16, 17], "赵括到任", 10),
    ([18, 19], "长平之战", 11),
    ([20, 21], "结局", 12),
    ([22], "纸上谈兵", 13),
    ([23, 24], "说回我们自己", 14),
    ([25], "第一招", 15),
    ([26], "第二招", 16),
    ([27], "第三招", 17),
    ([28], "好处", 18),
    ([29, 30, 31, 32], "评论区见", 19),
]

THEME = ZT.get("03")
L = Z.Lesson("03", SCREENS, drop_screen=2, board_size=(5000, 13400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(18)]
Z_ = 0.72

NOTES = [
    "出处：司马光《资治通鉴》卷五 周纪五（赧王五十五年）长平之战。",
    "原文：赵括“自少时学兵法，以为天下莫能当”；奢“不能难，然不谓善”，“兵，死地也，而括易言之……破赵军者必括也”；"
    "秦间言“秦之所畏，独畏马服君之子赵括为将耳”；蔺相如“王以名使括，若胶柱鼓瑟耳。括徒能读其父书传，不知合变也”；"
    "括母“父子异心，愿王勿遣”；括“至军，悉更约束，易置军吏”；秦阴使白起为上将军，绝赵粮道，“赵卒不得食四十六日”，"
    "秦人射杀赵括，卒四十万人皆降，白起尽坑杀之，遗其小者二百四十人归赵。",
    "“纸上谈兵”是后人的说法。今人（小李、小王、会说的同事）为虚构示意；古人造型为示意。",
]

KUO, SHE, MOTHER, KING, LIN, LIANPO, BAIQI = "blue", "brown", "red", "ochre", "teal", "gray", "purple"
PARCH, PARCH_LINE = "#F7EFD9", "#9C7A3A"


def gu_frame(j, k=0):
    cx, cy = R[j]
    L.note("通鉴")

    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k), 0.25)
        if sc <= 0:
            return None
        a = clamp01(sc)
        r = skia.Rect.MakeXYWH(cx - 580, cy - 585, 1160, 1215)
        c.drawRoundRect(r, 18, 18, K.paint(PARCH, 0.12 * a))
        c.drawRoundRect(r, 18, 18, wb.marker(PARCH_LINE, 6, a))
        r2 = skia.Rect.MakeXYWH(cx - 562, cy - 567, 1124, 1179)
        c.drawRoundRect(r2, 12, 12, wb.marker(PARCH_LINE, 2.5, 0.8 * a))
        seal(c, cx - 505, cy - 505, "通鉴", 40, -3, 1.0, a)
        return None
    b.custom(j, k, k + 0.2, fn)


def name_tag(c, x, y, s, color=INK, size=44, a=1.0):
    w = K.text_w(s, size, "serif_black") + 34
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - size * 0.7, w, size * 1.4), 10, 10, K.paint("#FFFFFF", 0.85 * a))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - size * 0.7, w, size * 1.4), 10, 10, wb.marker(color, 4, a))
    K.text(c, s, x, y + 2, size, "serif_black", color, a)


def chip(c, x, y, s, fill, line, size=50, a=1.0, rot=0.0):
    w = K.text_w(s, size, "hand") + 50
    with K.at(c, x, y, rot):
        c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -size * 0.75, w, size * 1.5), size * 0.75, size * 0.75, K.paint(fill, a))
        c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -size * 0.75, w, size * 1.5), size * 0.75, size * 0.75,
                        wb.marker(line, 5, a))
        K.text(c, s, 0, 2, size, "hand", line, a)


def books(c, x, y, n=4, a=1.0):
    for i in range(n):
        box(c, x + (i % 2) * 14, y - i * 46, 230, 40, ("#E9D49A", "#D5E3F7", "#F4CFC8", "#D3EDDC")[i % 4], INK, 4, 6, a)


def steps_row(jj, active):
    x0, y0 = R[jj][0] - 180, R[jj][1] - 480
    L.note("一", "二", "三")

    def fn(c, kk, T):
        for i, ch in enumerate("一二三"):
            sc = pop_scale(T - tb(jj, 0) - i * 0.1)
            if sc <= 0:
                continue
            on = i == active
            with K.at(c, x0 + i * 150, y0, 0, sc * (1.15 if on else 1)):
                c.drawCircle(0, 0, 52, K.paint(RED if on else "#FFFFFF"))
                c.drawCircle(0, 0, 52, wb.marker(RED if on else GRAY, 7))
                K.text(c, ch, 0, 2, 56, "serif_black", "#FFFFFF" if on else GRAY)
        return None
    b.custom(jj, 0, 0.3, fn, sfx="wood_high", gain=0.6)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：会说的同事指着白板讲方案，大家点头；交给他做，进度条变红
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_talk = 0
    k_arrows = kq(j, wp(0, 2, 0.3), 1)
    k_nod = nx(j, wp(0, 3, 0.4), k_arrows)
    k_bar = nx(j, wp(1, 0, 0.5), k_nod)
    k_red = nx(j, wp(1, 1, 0.6), k_bar)
    AX = cx - 380
    L.note("进度")

    def ace(c, sc, T):
        with at_pop(c, AX, GY, sc):
            draw_ace(c, AX, GY, 1.0, mood="laugh" if T < tb(j, k_red) else "flat", rh=(AX + 170, GY - 470))
        return None
    ev(j, k_talk, L.pop_fn(j, k_talk, ace), "wood_high", 0.6)

    def board(c, kk, T):
        g = pop_scale(T - tb(j, 0) - 0.2)
        if g <= 0:
            return None
        with K.at(c, cx + 120, cy - 280, 0, g):
            box(c, 0, 0, 640, 420, "#FFFFFF", BLACK, 7, 14)
            ta = tb(j, k_arrows)
            for i in range(4):
                if T < ta + i * 0.12:
                    continue
                f = ease_out(clamp01((T - ta - i * 0.12) / 0.3))
                y = 130 - i * 60
                c.drawPath(wb.partial(wb.arrow((-260 + i * 40, y + 40), (-260 + i * 40 + 460 * f, y - 60 * f), -0.2, 30), 1)[0],
                           wb.marker((GREEN, BLUE, ORANGE, GREEN)[i], 8))
        return None
    ev(j, 0, board, None)
    b.hit(j, k_arrows, "shaker", 0.7, "箭头满墙")

    def crowd(c, kk, T):
        tn = tb(j, k_nod)
        for i, x in enumerate((cx - 30, cx + 180, cx + 400)):
            g = pop_scale(T - tn - i * 0.1)
            if g <= 0:
                continue
            nod = 8 * abs(math.sin((T - tn) * 8)) if T < tn + 1.0 else 0
            with at_pop(c, x, GY, g):
                if i == 1:
                    draw_wang(c, x, GY, 0.75, mood="smile", head_dx=0)
                else:
                    draw_li(c, x, GY + nod * 0, 0.75, "smile")
        return None
    ev(j, k_nod, crowd, "pop", 0.65)

    def bar(c, kk, T):
        tb_, tr = tb(j, k_bar), tb(j, k_red)
        g = pop_scale(T - tb_)
        if g <= 0:
            return None
        with K.at(c, cx + 120, cy + 30, 0, g):
            box(c, 0, 0, 620, 70, "#FFFFFF", BLACK, 6, 35)
            red = T >= tr
            p = 0.75 if not red else lerp(0.75, 0.2, ease_out(clamp01((T - tr) / 0.4)))
            c.drawRoundRect(skia.Rect.MakeXYWH(-300, -27, 600 * p, 54), 27, 27, K.paint(RED if red else GREEN))
            K.text(c, "进度", -380, 0, 46, "hand", INK)
        return None
    ev(j, k_bar, bar, "wood_low", 0.6)
    b.hit(j, k_red, "tom", 0.8, "进度条变红")
    b.shots[j].shake = [(k_red, 7.0)]


screen1()


# ================================================================ 屏 2（drop）：面试满分，第一个活打红叉
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_100 = kq(j, wp(2, 0, 0.6), 1)
    k_task = nx(j, wp(2, 2, 0.4), k_100)
    L.note("面试", "100分", "第一个活")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, 0))
        if g <= 0:
            return None
        NX_ = cx - 300
        with at_pop(c, NX_, GY, g):
            desk(c, NX_ + 200, GY - 170, 360, laptop=False)
            draw_li(c, NX_, GY, 0.95, "smile" if T < tb(j, dk) else "sad", bag=True)
        with K.at(c, cx - 220, cy - 300, -4, g):
            box(c, 0, 0, 340, 260, "#FFFFFF", BLACK, 6, 10)
            K.text(c, "面试", 0, -80, 50, "sans_medium", INK)
            if T >= tb(j, k_100):
                with K.at(c, 0, 30, -8, C.slam_scale(T - tb(j, k_100))):
                    K.text(c, "100分", 0, 0, 80, "hand", GREEN)
        tt = tb(j, k_task)
        if T >= tt:
            with K.at(c, cx + 270, cy - 160, 3, pop_scale(T - tt)):
                box(c, 0, 0, 380, 300, "#FFFFFF", BLACK, 6, 10)
                K.text(c, "第一个活", 0, -100, 52, "hand", INK)
                for r in range(3):
                    C.line(c, (-130, -20 + r * 50), (130 - r * 40, -20 + r * 50), GRAY, 5)
        td = tb(j, dk)
        if T >= td:
            f = ease_out(clamp01((T - td) / 0.2))
            c.drawPath(wb.partial(cross(cx + 270, cy - 160, 130), f)[0], wb.marker(RED, 18))
        return None
    ev(j, 0, scene, "wood_high", 0.6)
    b.hit(j, k_100, "ding", 0.75, "面试满分")
    b.hit(j, k_task, "pop", 0.6, "第一个活")
    b.hit(j, dk, "kick", 0.9, "打红叉")
    b.shots[j].shake = [(dk, 12.0)]
    b.shots[j].flashes = [(dk, 0.3)]


screen2()


# ================================================================ 屏 3：小李的方案文档漂亮，一落地，流程上处处是卡住的红点
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_doc = kq(j, wp(3, 2, 0.3), 0)
    k_flow = nx(j, wp(3, 3, 0.2), k_doc)
    k_stuck = nx(j, wp(3, 3, 0.8), k_flow)
    L.note("方案", "卡住")
    LX = cx - 400

    def li(c, sc, T):
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 0.9, "smile" if T < tb(j, k_stuck) else "sad")
        return None
    ev(j, 0, L.pop_fn(j, 0, li), "wood_low", 0.6)

    def doc(c, kk, T):
        g = pop_scale(T - tb(j, k_doc))
        if g <= 0:
            return None
        with K.at(c, cx - 120, cy - 300, -3, g):
            box(c, 0, 0, 420, 300, "#FFFFFF", BLUE, 7, 12)
            K.text(c, "方案", 0, -100, 56, "sans_medium", BLUE)
            for r in range(3):
                C.line(c, (-150, -20 + r * 55), (150 - (r % 2) * 50, -20 + r * 55), GRAY, 6)
            sparkle(c, 180, -120, T - tb(j, k_doc), YELLOW, 8, 30, 70)
        return None
    ev(j, k_doc, doc, "ding", 0.65)

    def flow(c, kk, T):
        tf, ts = tb(j, k_flow), tb(j, k_stuck)
        if T < tf:
            return None
        pts = [(cx - 200, cy + 150), (cx + 30, cy + 150), (cx + 260, cy + 150), (cx + 260, cy + 360), (cx + 30, cy + 360)]
        f = ease_out(clamp01((T - tf) / 0.5))
        for i, (x, y) in enumerate(pts):
            if i / len(pts) > f:
                break
            box(c, x, y, 160, 100, "#FFFFFF", BLACK, 5, 14)
            if i:
                C.line(c, pts[i - 1], (x, y), GRAY, 5)
        if T >= ts:
            for i, (x, y) in enumerate(pts[1:]):
                g = C.slam_scale(T - ts - i * 0.08)
                if g > 0:
                    with K.at(c, x + 60, y - 50, 0, g):
                        c.drawCircle(0, 0, 30, K.paint(RED))
                        K.text(c, "!", 0, 2, 40, "black", "#FFFFFF")
            K.text(c, "卡住", cx + 440, cy + 250, 70, "hand", RED, clamp01((T - ts) / 0.2))
        return None
    ev(j, k_flow, flow, "wood_high", 0.65)
    b.hit(j, k_stuck, "rim", 0.85, "处处卡住")


screen3()


# ================================================================ 屏 4：竹简“资治通鉴 卷五”；赵括坐在兵书堆里，头顶“天下第一”
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_slip = kq(j, wp(4, 0, 0.3), 0)
    k_kuo = nx(j, wp(4, 3, 0.2), k_slip)
    k_books = nx(j, wp(5, 0, 0.5), k_kuo)
    k_top = nx(j, wp(5, 2, 0.5), k_books)
    SX = cx - 300
    L.note("资治通鉴", "卷五", "周纪五", "赵括", "兵书", "天下第一")

    def slips(c, kk, T):
        f = ease_out(clamp01((T - tb(j, k_slip)) / 0.6))
        if f <= 0:
            return None
        bamboo_slips(c, SX, cy - 60, max(60, 380 * f), 780, n=max(1, int(5 * f)))
        a = clamp01((T - tb(j, k_slip) - 0.3) / 0.3)
        slip_text(c, SX + 60, cy - 370, "资治通鉴", 88, "#3A2A12", a)
        slip_text(c, SX - 80, cy - 330, "卷五", 70, RED, a)
        slip_text(c, SX - 80, cy - 120, "周纪五", 54, "#5E4128", a, 1.15)
        return None
    ev(j, k_slip, slips, "muyu", 0.7, 0.6)

    def kuo(c, sc, T):
        x = cx + 260
        with at_pop(c, x, GY, sc):
            if T >= tb(j, k_books):
                books(c, x + 150, GY - 20, 5)
                books(c, x - 170, GY - 20, 3)
            gu(c, x, GY, 0.95, KUO, hat="guan", mood="smile" if T < tb(j, k_top) else "laugh",
               rh=(x + 120, GY - 400) if T >= tb(j, k_top) else None)
            name_tag(c, x, GY - 400, "赵括", "#2F5B8E", 50)
        if T >= tb(j, k_top):
            with K.at(c, x, cy - 330, -4, C.slam_scale(T - tb(j, k_top))):
                chip(c, 0, 0, "天下第一", NOTE_FILL, ORANGE, 56)
        return None
    ev(j, k_kuo, L.pop_fn(j, k_kuo, kuo), "tom", 0.8)
    b.hit(j, k_books, "wood_high", 0.7, "兵书堆起来")
    b.hit(j, k_top, "rim", 0.8, "天下第一")


screen4()


# ================================================================ 屏 5：父子对坐谈兵，沙盘；赵括说个不停，赵奢摇头不夸；母亲在旁问
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_pair = 0
    k_talk = kq(j, wp(6, 1, 0.5), 1)
    k_win = nx(j, wp(6, 2, 0.4), k_talk)
    k_no = nx(j, wp(6, 3, 0.4), k_win)
    k_ma = nx(j, wp(7, 1, 0.3), k_no)
    KX, SX_, MX = cx + 300, cx - 300, cx + 20
    L.note("赵奢", "赵括", "母亲", "为什么？", "沙盘")

    def pair(c, sc, T):
        tt, tn = tb(j, k_talk), tb(j, k_no)
        with at_pop(c, cx, GY, sc):
            box(c, cx, GY - 140, 340, 90, "#C9A97A", "#7A5E3A", 6, 8)
            for q in range(5):
                c.drawCircle(cx - 120 + q * 60, GY - 150 - (q % 2) * 10, 12, K.paint(RED if q % 2 else BLUE))
            talk = 20 * math.sin((T - tt) * 12) if T >= tt else 0
            gu(c, KX, GY, 0.9, KUO, hat="guan", mood="laugh" if T >= tt else "smile",
               rh=(KX - 160, GY - 330 + talk) if T >= tt else None)
            name_tag(c, KX, GY - 400, "赵括", "#2F5B8E", 40)
            shake = 10 * math.sin((T - tn) * 14) * math.exp(-(T - tn) * 2) if T >= tn else 0
            gu(c, SX_, GY, 0.9, SHE, hat="guan", beard="white", head_dx=shake)
            name_tag(c, SX_, GY - 400, "赵奢", "#5E4128", 40)
        return None
    ev(j, k_pair, L.pop_fn(j, k_pair, pair), "muyu", 0.6)
    b.hit(j, k_talk, "wood_high", 0.65, "赵括讲个不停")

    def words(c, kk, T):
        tw, tn = tb(j, k_win), tb(j, k_no)
        if T >= tw:
            with K.at(c, KX + 20, cy - 120, 3, C.slam_scale(T - tw)):
                bubble_box(c, 0, 0, 340, 130, 1)
                K.text(c, "我赢了", 0, 0, 60, "hand", INK)
        if T >= tn:
            with K.at(c, SX_ + 40, cy - 330, 0, pop_scale(T - tn)):
                bubble_box(c, 0, 0, 220, 120, -1)
                K.text(c, "……", 0, -6, 60, "hand", GRAY)
        tm = tb(j, k_ma)
        if T >= tm:
            g = pop_scale(T - tm)
            with at_pop(c, MX, cy + 60, g):
                gu(c, MX, cy + 60, 0.55, MOTHER, hat="lady")
            with K.at(c, MX + 30, cy - 330, 0, g):
                bubble_box(c, 0, 0, 280, 110, -1)
                K.text(c, "为什么？", 0, 0, 52, "hand", RED)
            name_tag(c, MX, cy - 170, "母亲", "#9C2F25", 34, clamp01(g))
        return None
    L.note("我赢了", "……")
    b.custom(j, k_win, k_win + 0.3, words, sfx="rim", gain=0.7)
    b.hit(j, k_no, "wood_low", 0.7, "赵奢摇头")
    b.hit(j, k_ma, "pop", 0.7, "母亲问为什么")


screen5()


# ================================================================ 屏 6：赵奢的话——“兵，死地也”；预言“破赵军者必括”
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_she = 0
    k_slip1 = kq(j, wp(8, 1, 0.4), 1)
    k_easy = nx(j, wp(8, 2, 0.5), k_slip1)
    k_pred = nx(j, wp(9, 2, 0.3), k_easy)
    k_him = nx(j, wp(9, 3, 0.3), k_pred)
    SX_ = cx - 360
    L.note("兵，死地也", "太轻巧", "破赵军者必括")

    def she(c, sc, T):
        with at_pop(c, SX_, GY, sc):
            gu(c, SX_, GY, 1.0, SHE, hat="guan", beard="white", rh=(SX_ + 150, GY - 330))
            name_tag(c, SX_, GY - 440, "赵奢", "#5E4128", 46)
        return None
    ev(j, k_she, L.pop_fn(j, k_she, she), "muyu", 0.6)

    def slips(c, kk, T):
        for i, (k_, s_, x) in enumerate(((k_slip1, "兵死地也", cx + 60), (k_pred, "破赵军者必括", cx + 330))):
            t0 = tb(j, k_)
            g = pop_scale(T - t0)
            if g <= 0:
                continue
            with K.at(c, x, cy - 70, 0, g):
                bamboo_slips(c, 0, 0, 130, 760, n=1)
                slip_text(c, 0, -300, s_, 84 if len(s_) <= 4 else 70, RED if i else INK)
        te = tb(j, k_easy)
        if T >= te:
            with K.at(c, cx - 170, cy - 360, -6, C.slam_scale(T - te)):
                chip(c, 0, 0, "太轻巧", RED_FILL, RED, 54)
        th = tb(j, k_him)
        if T >= th:
            with K.at(c, cx + 330, cy + 420, 0, pop_scale(T - th)):
                gu(c, 0, 80, 0.4, KUO, hat="guan", mood="o")
                ring = skia.Path()
                ring.addOval(skia.Rect.MakeXYWH(-90, -110, 180, 210))
                c.drawPath(ring, wb.marker(RED, 8))
        return None
    L.note("兵死地也")
    b.custom(j, k_slip1, k_slip1 + 0.3, slips, sfx="bangzi", gain=0.75)
    b.hit(j, k_easy, "rim", 0.75, "说得太轻巧")
    b.hit(j, k_pred, "xiaoluo", 0.8, "破赵军者必括")
    b.hit(j, k_him, "kick", 0.8, "一定是他")


screen6()


# ================================================================ 屏 7：长平地图，廉颇守营垒不出战；秦国探子放话“只怕赵括”
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_map = kq(j, wp(10, 1, 0.3), 0)
    k_lian = nx(j, wp(10, 2, 0.5), k_map)
    k_wall = nx(j, wp(10, 3, 0.4), k_lian)
    k_spy = nx(j, wp(11, 0, 0.5), k_wall)
    k_fear = nx(j, wp(11, 2, 0.3), k_spy)
    L.note("长平", "秦", "赵", "廉颇", "只怕赵括")

    def mapf(c, kk, T):
        g = pop_scale(T - tb(j, k_map), 0.4)
        if g <= 0:
            return None
        with at_pop(c, cx, cy - 250, g):
            box(c, cx, cy - 250, 1000, 420, "#EFE4CC", "#7A5E3A", 6, 20)
            K.text(c, "长平", cx, cy - 400, 60, "serif_black", INK)
            flag(c, cx - 300, cy - 70, 0.5, "赵", "#9C2F25")
            flag(c, cx + 300, cy - 70, 0.5, "秦", "#3D4A63")
            C.line(c, (cx, cy - 360), (cx, cy - 60), GRAY, 4)
        return None
    ev(j, k_map, mapf, "wood_low", 0.65)

    def lian(c, sc, T):
        x = cx - 330
        with at_pop(c, x, GY, sc):
            if T >= tb(j, k_wall):
                p = P((x - 220, GY), (x - 220, GY - 170), (x + 220, GY - 170), (x + 220, GY), close=True)
                c.drawPath(p, K.paint("#D8C7A6"))
                c.drawPath(p, wb.marker("#7A5E3A", 6))
                for q in range(5):
                    C.line(c, (x - 220 + q * 110, GY - 170), (x - 220 + q * 110, GY), "#7A5E3A", 3)
            gu(c, x, GY - 120, 0.75, LIANPO, hat="helmet", beard="white")
            name_tag(c, x, GY - 460, "廉颇", "#5E5E58", 40)
        return None
    ev(j, k_lian, L.pop_fn(j, k_lian, lian), "tom", 0.75)
    b.hit(j, k_wall, "wood_high", 0.7, "守着营垒")

    def spy(c, kk, T):
        ts, tf = tb(j, k_spy), tb(j, k_fear)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        x = cx + 330
        with at_pop(c, x, GY, g):
            gu(c, x, GY, 0.75, "gray", hat="bun", rh=(x - 60, GY - 260), head_dx=-6)
            name_tag(c, x, GY - 330, "秦国探子", "#5E5E58", 34)
        if T >= tf:
            with K.at(c, cx + 140, cy + 20, 0, C.slam_scale(T - tf)):
                bubble_box(c, 0, 0, 400, 140, 1)
                K.text(c, "只怕赵括", 0, 0, 62, "hand", RED)
        return None
    L.note("秦国探子")
    b.custom(j, k_spy, k_spy + 0.3, spy, sfx="shaker", gain=0.6)
    b.hit(j, k_fear, "rim", 0.8, "只怕赵括")


screen7()


# ================================================================ 屏 8：赵王把将印递给赵括；蔺相如劝——“胶柱鼓瑟”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_king = 0
    k_seal = kq(j, wp(12, 1, 0.4), 1)
    k_lin = nx(j, wp(13, 0, 0.4), k_seal)
    k_qin = nx(j, wp(13, 1, 0.6), k_lin)
    k_stuck = nx(j, wp(13, 2, 0.5), k_qin)
    WX, KX, LX = cx - 380, cx - 60, cx + 360
    L.note("赵王", "赵括", "蔺相如", "将印", "胶柱鼓瑟")

    def scene(c, sc, T):
        ts = tb(j, k_seal)
        with at_pop(c, cx, GY, sc):
            gu(c, WX, GY, 0.9, KING, hat="guan", beard="black", rh=(WX + 150, GY - 260) if T >= ts else None)
            name_tag(c, WX, GY - 400, "赵王", "#8A5A1E", 40)
            gu(c, KX, GY, 0.85, KUO, hat="guan", mood="smile", lh=(KX - 110, GY - 250) if T >= ts else None)
            name_tag(c, KX, GY - 380, "赵括", "#2F5B8E", 40)
            if T >= ts:
                f = ease_out(clamp01((T - ts) / 0.4))
                x = lerp(WX + 160, KX - 120, f)
                seal(c, x, GY - 260, "将", 40, 0)
        return None
    ev(j, k_king, L.pop_fn(j, k_king, scene), "muyu", 0.6)
    b.hit(j, k_seal, "tom", 0.75, "递将印")

    def lin(c, kk, T):
        tl, tq, tst = tb(j, k_lin), tb(j, k_qin), tb(j, k_stuck)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            gu(c, LX, GY, 0.85, LIN, hat="guan", beard="black", rh=(LX - 120, GY - 300))
            name_tag(c, LX, GY - 380, "蔺相如", "#2C6E68", 38)
        if T >= tq:
            gq = pop_scale(T - tq)
            with K.at(c, cx + 60, cy - 300, 0, gq):
                box(c, 0, 0, 640, 200, "#F0DDB8", "#7A4A1E", 6, 16)
                for q in range(6):
                    xx = -250 + q * 100
                    C.line(c, (-300, -40 + q * 12), (300, -40 + q * 12), INK, 2)
                    c.drawPath(P((xx - 18, 40), (xx, -20), (xx + 18, 40), close=True), K.paint("#C9A34A"))
                    if T >= tst:
                        c.drawCircle(xx, 30, 22, K.paint("#E8D9A0", 0.9))
                        c.drawCircle(xx, 30, 22, wb.marker("#A9842A", 4))
            if T >= tst:
                with K.at(c, cx + 60, cy - 120, -3, C.slam_scale(T - tst)):
                    chip(c, 0, 0, "胶柱鼓瑟", RED_FILL, RED, 56)
        return None
    b.custom(j, k_lin, k_lin + 0.3, lin, sfx="wood_low", gain=0.65)
    b.hit(j, k_qin, "pop", 0.65, "一张瑟")
    b.hit(j, k_stuck, "kick", 0.8, "琴柱被胶粘死")


screen8()


# ================================================================ 屏 9：母亲上书——赵奢把赏赐分给士兵；赵括把金子锁箱子、看地契
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_ma = kq(j, wp(14, 0, 0.5), 0)
    k_split = nx(j, wp(14, 2, 0.4), k_ma)
    k_give = nx(j, wp(15, 1, 0.5), k_split)
    k_lock = nx(j, wp(15, 3, 0.4), k_give)
    k_land = nx(j, wp(15, 4, 0.4), k_lock)
    L.note("母亲", "父亲", "赵括", "地契")

    def ma(c, kk, T):
        g = pop_scale(T - tb(j, k_ma))
        if g <= 0:
            return None
        with at_pop(c, cx, cy - 300, g):
            gu(c, cx, cy - 300, 0.6, MOTHER, hat="lady", lh=(cx - 60, cy - 370), rh=(cx + 60, cy - 370))
            bamboo_slips(c, cx, cy - 360, 160, 90, n=3)
            name_tag(c, cx, cy - 540, "母亲", "#9C2F25", 34)
        ts = tb(j, k_split)
        if T >= ts:
            f = ease_out(clamp01((T - ts) / 0.4))
            C.line(c, (cx, cy - 160), (cx, cy - 160 + 740 * f), GRAY, 5)
        return None
    ev(j, k_ma, ma, "pop", 0.65)
    b.hit(j, k_split, "wood_high", 0.7, "一左一右")

    def left(c, kk, T):
        tg = tb(j, k_give)
        g = pop_scale(T - tb(j, k_split))
        if g <= 0:
            return None
        x = cx - 300
        with at_pop(c, x, GY, g):
            gu(c, x - 80, GY, 0.7, SHE, hat="guan", beard="white", rh=(x + 30, GY - 200))
            name_tag(c, x - 80, GY - 310, "父亲", "#5E4128", 34)
            for i, xx in enumerate((x + 120, x + 220)):
                gu(c, xx, GY, 0.5, "gray", hat="helmet", mood="smile" if T >= tg else "flat")
        if T >= tg:
            for i in range(2):
                f = ease_in_out(clamp01((T - tg - i * 0.15) / 0.4))
                c.drawOval(skia.Rect.MakeXYWH(lerp(x + 30, x + 120 + i * 100, f) - 30, lerp(GY - 220, GY - 190, f) - 12, 60, 24),
                           K.paint(YELLOW))
        return None
    b.custom(j, k_split, k_split + 0.3, left)
    b.hit(j, k_give, "ding", 0.75, "赏赐分给手下")

    def right(c, kk, T):
        tl, td = tb(j, k_lock), tb(j, k_land)
        g = pop_scale(T - tl + 0.3)
        if g <= 0:
            return None
        x = cx + 300
        with at_pop(c, x, GY, g):
            gu(c, x + 100, GY, 0.7, KUO, hat="guan", mood="smile", lh=(x - 20, GY - 170))
            name_tag(c, x + 100, GY - 310, "赵括", "#2F5B8E", 34)
            box(c, x - 90, GY - 70, 170, 130, "#C98B4B", "#7A4A1E", 6, 10)
            if T >= tl:
                c.drawCircle(x - 90, GY - 70, 16, K.paint(YELLOW))
                c.drawCircle(x - 90, GY - 70, 16, wb.marker("#7A4A1E", 4))
        if T >= td:
            with K.at(c, x + 30, cy - 70, 4, pop_scale(T - td)):
                box(c, 0, 0, 230, 150, PARCH, "#7A5E3A", 5, 8)
                K.text(c, "地契", 0, -30, 50, "serif_black", INK)
                for q in range(2):
                    C.line(c, (-80, 20 + q * 30), (80, 20 + q * 30), GRAY, 4)
        return None
    b.custom(j, k_lock, k_lock + 0.3, right)
    b.hit(j, k_lock, "rim", 0.75, "金子锁进箱子")
    b.hit(j, k_land, "pop", 0.7, "看地契")


screen9()


# ================================================================ 屏 10：赵王摆手不听；赵括到军中，规矩牌全换掉，军官一个个换人
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_no = kq(j, wp(16, 0, 0.5), 0)
    k_arrive = nx(j, wp(17, 0, 0.5), k_no)
    k_rule = nx(j, wp(17, 1, 0.5), k_arrive)
    k_swap = nx(j, wp(17, 2, 0.4), k_rule)
    KX = cx - 330
    L.note("没听", "旧规矩", "新规矩")

    def king(c, kk, T):
        g = pop_scale(T - tb(j, k_no))
        if g <= 0:
            return None
        with K.at(c, cx + 330, cy - 360, 0, g):
            gu(c, 0, 120, 0.45, KING, hat="guan", beard="black", rh=(80, -30 + 15 * math.sin((T - tb(j, k_no)) * 10)))
            with K.at(c, -150, -60, 0, 1):
                bubble_box(c, 0, 0, 200, 100, 1)
                K.text(c, "没听", 0, 0, 48, "hand", RED)
        return None
    ev(j, k_no, king, "wood_low", 0.7)

    def kuo(c, kk, T):
        ta = tb(j, k_arrive)
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        with at_pop(c, KX, GY, g):
            gu(c, KX, GY, 0.9, KUO, hat="helmet", mood="laugh", rh=(KX + 150, GY - 330))
            name_tag(c, KX, GY - 430, "赵括", "#2F5B8E", 40)
        tr = tb(j, k_rule)
        x, y = cx - 30, cy - 120
        with K.at(c, x, y, 0, g):
            if T < tr + 0.15:
                box(c, 0, 0, 280, 170, PARCH, "#7A5E3A", 6, 8)
                K.text(c, "旧规矩", 0, 0, 52, "serif_black", INK)
            if T >= tr:
                f = ease_out(clamp01((T - tr) / 0.3))
                with K.at(c, 0, 0, lerp(-90, 0, f), f):
                    box(c, 0, 0, 280, 170, RED_FILL, RED, 6, 8)
                    K.text(c, "新规矩", 0, 0, 52, "serif_black", RED)
        return None
    b.custom(j, k_arrive, k_arrive + 0.3, kuo, sfx="tom", gain=0.75)
    b.hit(j, k_rule, "rim", 0.8, "规矩全改")

    def officers(c, kk, T):
        tsw = tb(j, k_swap)
        for i, x in enumerate((cx + 120, cx + 280, cx + 440)):
            t0 = tsw + i * 0.15
            out = ease_in_out(clamp01((T - t0) / 0.3)) if T >= t0 else 0
            g = pop_scale(T - tb(j, k_arrive) - 0.2)
            if g <= 0:
                continue
            old_a = 1 - out
            if old_a > 0:
                gu(c, x, GY + 60 * out, 0.6, "gray", hat="helmet", beard="black", alpha=old_a)
            if out > 0:
                gu(c, x, GY - 60 * (1 - out), 0.6, KUO, hat="helmet", mood="smile", alpha=out)
        return None
    b.custom(j, k_arrive, k_arrive + 0.3, officers)
    b.hit(j, k_swap, "shaker", 0.75, "军官换了一批")


screen10()


# ================================================================ 屏 11：白起出场、佯败、断粮道；日历翻到四十六天，粮袋空
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_bai = kq(j, wp(18, 0, 0.6), 0)
    k_back = nx(j, wp(18, 1, 0.5), k_bai)
    k_cut = nx(j, wp(18, 2, 0.6), k_back)
    k_46 = nx(j, wp(19, 1, 0.4), k_cut)
    k_empty = nx(j, wp(19, 2, 0.5), k_46)
    L.note("白起", "粮道", "四十六天")

    def bai(c, sc, T):
        x = cx + 360
        tb_ = tb(j, k_back)
        dx = 80 * ease_in_out(clamp01((T - tb_) / 0.5)) if T >= tb_ else 0
        with at_pop(c, x + dx, GY, sc):
            gu(c, x + dx, GY, 0.9, BAIQI, hat="helmet", beard="black", mood="smile")
            name_tag(c, x + dx, GY - 430, "白起", "#6B3F7A", 44)
        if T >= tb_:
            c.drawPath(wb.arrow((x - 120, GY - 200), (x + 80, GY - 200), 0.0, 30), wb.marker(GRAY, 8))
        return None
    ev(j, k_bai, L.pop_fn(j, k_bai, bai), "tom", 0.8)
    b.hit(j, k_back, "wood_low", 0.7, "假装败退")

    def road(c, kk, T):
        tc = tb(j, k_cut)
        g = pop_scale(T - tb(j, k_bai) - 0.2)
        if g <= 0:
            return None
        y = cy - 330
        C.line(c, (cx - 540, y), (cx + 200, y), "#8B6B43", 14)
        K.text(c, "粮道", cx - 420, y - 60, 50, "hand", "#7A4A1E")
        for q in range(3):
            xx = cx - 300 + q * 160 + 120 * ((T * 0.6) % 1) if T < tc else cx - 300 + q * 160
            c.drawOval(skia.Rect.MakeXYWH(xx - 40, y - 30, 80, 60), K.paint("#E9D49A"))
            c.drawOval(skia.Rect.MakeXYWH(xx - 40, y - 30, 80, 60), wb.marker("#7A5E3A", 4))
        if T >= tc:
            seal(c, cx - 30, y, "断", 70, -8, C.slam_scale(T - tc))
        return None
    b.custom(j, k_bai, k_bai + 0.3, road)
    b.hit(j, k_cut, "kick", 0.85, "粮道被断")

    def cal(c, kk, T):
        t46, te = tb(j, k_46), tb(j, k_empty)
        if T < t46:
            return None
        g = pop_scale(T - t46)
        n = int(lerp(1, 46, clamp01((T - t46) / 0.6)))
        with K.at(c, cx - 260, cy + 60, 0, g):
            box(c, 0, 0, 280, 260, "#FFFFFF", BLACK, 6, 12)
            c.drawRect(skia.Rect.MakeXYWH(-140, -130, 280, 60), K.paint(RED_FILL))
            K.text(c, f"{n}", 0, 40, 110, "black", RED)
            K.text(c, "天", 0, -98, 36, "sans_medium", INK)
        if T >= te:
            with K.at(c, cx + 30, cy + 100, 0, pop_scale(T - te)):
                p = P((-70, 90), (-80, -30), (-40, -80), (40, -80), (80, -30), (70, 90), close=True)
                c.drawPath(p, K.paint("#EFE4CC"))
                c.drawPath(p, wb.marker("#7A5E3A", 5))
                C.line(c, (-40, -80), (40, -80), "#7A5E3A", 8)
                K.text(c, "空", 0, 20, 60, "hand", GRAY)
        return None
    L.note("天", "空")
    b.custom(j, k_46, k_46 + 0.3, cal, sfx="shaker", gain=0.7)
    b.hit(j, k_empty, "wood_low", 0.75, "粮袋空了")


screen11()


# ================================================================ 屏 12：赵括突围中箭倒下；四十万赵军放下兵器
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_out = kq(j, wp(20, 0, 0.5), 0)
    k_arrow = nx(j, wp(20, 1, 0.5), k_out)
    k_down = nx(j, wp(21, 0, 0.6), k_arrow)
    k_bury = nx(j, wp(21, 1, 0.5), k_down)
    L.note("四十万")
    KX = cx - 150

    def kuo(c, kk, T):
        to, ta = tb(j, k_out), tb(j, k_arrow)
        g = pop_scale(T - to)
        if g <= 0:
            return None
        x, dy, _ = C.walk(T, to, max(0.3, ta - to), cx - 450, KX, 12)
        fall = ease_out(clamp01((T - ta) / 0.4)) if T >= ta else 0
        with K.at(c, x, GY - 330 * 0.3, -80 * fall):
            c.translate(-x, -(GY - 330 * 0.3))
            gu(c, x, GY + dy, 0.85, KUO, hat="helmet", mood="o" if fall else "angry", rh=(x + 140, GY - 300))
        for i in range(3):
            t0 = ta - 0.25 + i * 0.06
            if T < t0:
                continue
            f = clamp01((T - t0) / 0.25)
            ex, ey = KX + 20 + i * 18, GY - 230 + i * 30
            sx, sy = ex + 420, ey - 260
            px, py = lerp(sx, ex, f), lerp(sy, ey, f)
            C.line(c, (px, py), (px + 80, py - 50), INK, 5)
            c.drawPath(P((px, py), (px + 22, py - 2), (px + 8, py - 18), close=True), K.paint(INK))
        return None
    b.custom(j, k_out, k_out + 0.3, kuo, sfx="tom", gain=0.75)
    b.hit(j, k_arrow, "kick", 0.85, "中箭")

    def army(c, kk, T):
        td, tbu = tb(j, k_down), tb(j, k_bury)
        if T < td:
            return None
        g = pop_scale(T - td)
        for r in range(2):
            for q in range(6):
                x, y = cx + 30 + q * 90 - r * 40, cy - 180 + r * 130
                gu(c, x, y, 0.3 * g, "gray", hat="helmet", alpha=0.6 if T >= tbu else 1)
                C.line(c, (x - 40, y + 10), (x + 30, y + 10), "#9AA3AD", 4)
        if T >= tbu:
            with K.at(c, cx + 250, cy - 360, 0, C.slam_scale(T - tbu)):
                K.text(c, "四十万", 0, 0, 96, "hand", RED)
        return None
    b.custom(j, k_down, k_down + 0.3, army, sfx="wood_low", gain=0.7)
    b.hit(j, k_bury, "xiaoluo", 0.85, "四十万")
    b.shots[j].shake = [(k_arrow, 9.0)]


screen12()


# ================================================================ 屏 13：一张纸上画满兵阵，被风一吹就飘走；“纸上谈兵”
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_paper = 0
    k_blow = kq(j, wp(22, 1, 0.5), 1)
    k_word = nx(j, wp(22, 2, 0.3), k_blow)
    L.note("纸上谈兵")

    def paper(c, kk, T):
        g = pop_scale(T - tb(j, k_paper))
        if g <= 0:
            return None
        tb_ = tb(j, k_blow)
        f = ease_in_out(clamp01((T - tb_) / 0.9)) if T >= tb_ else 0
        x = lerp(cx - 60, cx + 420, f)
        y = lerp(cy - 160, cy - 420, f) + 40 * math.sin(f * 6)
        with K.at(c, x, y, lerp(-4, 30, f), g * lerp(1, 0.45, f)):
            box(c, 0, 0, 640, 460, PARCH, "#7A5E3A", 6, 6)
            for r in range(3):
                for q in range(4):
                    c.drawRect(skia.Rect.MakeXYWH(-230 + q * 120, -150 + r * 100, 70, 40), wb.marker(RED if r % 2 else BLUE, 4))
            c.drawPath(wb.arrow((-240, 160), (220, -170), 0.3, 40), wb.marker(RED, 8))
        if T >= tb_:
            for q in range(3):
                yy = cy - 100 + q * 90
                xx = cx - 520 + 200 * ((T - tb_) * 1.5 % 1)
                C.line(c, (xx, yy), (xx + 160, yy - 20), GRAY, 5, 0.7)
        return None
    ev(j, k_paper, paper, "wood_high", 0.65)
    b.hit(j, k_blow, "shaker", 0.8, "风一吹")
    L.stamp_ev(j, k_word, "纸上谈兵", cx, cy + 330, 120, -4, "kick", 0.9)
    b.shots[j].shake = [(k_word, 10.0)]


screen13()


# ================================================================ 屏 14：嘴和手放上天平，往“手”那边沉；“三招”
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_mouth = kq(j, wp(23, 0, 0.5), 0)
    k_hand = nx(j, wp(23, 2, 0.4), k_mouth)
    k_3 = nx(j, wp(24, 1, 0.5), k_hand)
    PX, PY = cx - 80, cy - 40
    L.note("会说", "做过", "三招")

    def scale(c, kk, T):
        g = pop_scale(T - tb(j, k_mouth))
        if g <= 0:
            return None
        th = tb(j, k_hand)
        tilt = 12 * ease_out(clamp01((T - th) / 0.5)) if T >= th else 0
        with at_pop(c, PX, GY, g):
            C.line(c, (PX, GY - 60), (PX, PY), "#7A5E3A", 12)
            box(c, PX, GY - 40, 220, 40, "#C9A97A", "#7A5E3A", 6, 8)
            with K.at(c, PX, PY, tilt):
                C.line(c, (-320, 0), (320, 0), "#7A5E3A", 12)
                for sg, lab in ((-1, "会说"), (1, "做过")):
                    with K.at(c, sg * 300, 0, -tilt):
                        C.line(c, (0, 0), (-60, 140), GRAY, 4)
                        C.line(c, (0, 0), (60, 140), GRAY, 4)
                        C.line(c, (-90, 140), (90, 140), GRAY, 8)
                        if sg < 0:
                            m = skia.Path()
                            m.addArc(skia.Rect.MakeXYWH(-60, 60, 120, 70), 0, 180)
                            m.close()
                            c.drawPath(m, K.paint(RED_FILL))
                            c.drawPath(m, wb.marker(RED, 6))
                        elif T >= th:
                            c.drawRoundRect(skia.Rect.MakeXYWH(-50, 40, 100, 96), 30, 30, K.paint("#FFFFFF"))
                            c.drawRoundRect(skia.Rect.MakeXYWH(-50, 40, 100, 96), 30, 30, wb.marker(BLACK, 6))
                            for q in range(4):
                                C.line(c, (-36 + q * 24, 40), (-36 + q * 24, 0), BLACK, 12)
                        K.text(c, lab, 0, 200, 52, "hand", RED if sg < 0 else GREEN)
        return None
    ev(j, k_mouth, scale, "wood_high", 0.65)
    b.hit(j, k_hand, "tom", 0.8, "往“做过”那边沉")
    L.stamp_ev(j, k_3, "三招", cx + 300, cy - 360, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen14()


# ================================================================ 屏 15：第一招：面试时问“讲一件你做砸过的事”，对面的人挠头
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 0)
    GY = cy + 520
    k_desk = kq(j, wp(25, 0, 0.6), 1)
    k_ask = nx(j, wp(25, 1, 0.5), k_desk)
    k_think = nx(j, wp(25, 2, 0.5), k_ask)
    L.note("讲一件你做砸过的事", "嗯……")
    WX, AX = cx - 340, cx + 340

    def scene(c, sc, T):
        ta, tt = tb(j, k_ask), tb(j, k_think)
        with at_pop(c, cx, GY, sc):
            desk(c, cx, GY - 170, 460, laptop=False)
            draw_wang(c, WX, GY, 0.9, mood="flat", rh=(WX + 120, GY - 300) if T >= ta else None)
            draw_ace(c, AX, GY, 0.9, mood="flat" if T >= tt else "smug",
                     rh=(AX + 20, GY - 290 * 0.9 - 50) if T >= tt else None)
        if T >= ta:
            with K.at(c, cx - 120, cy - 220, 0, C.slam_scale(T - ta)):
                bubble_box(c, 0, 0, 640, 140, -1)
                K.text(c, "讲一件你做砸过的事", 0, 0, 56, "hand", INK)
        if T >= tt:
            with K.at(c, AX + 20, cy - 20, 0, pop_scale(T - tt)):
                bubble_box(c, 0, 0, 220, 110, 1)
                K.text(c, "嗯……", 0, -4, 52, "hand", GRAY)
        return None
    ev(j, k_desk, L.pop_fn(j, k_desk, scene), "wood_low", 0.6)
    b.hit(j, k_ask, "rim", 0.8, "问一句")
    b.hit(j, k_think, "pop", 0.7, "对面挠头")


screen15()


# ================================================================ 屏 16：第二招：大方案切出一小块先试，打勾后再拍胸脯
def screen16(j=16):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 1)
    GY = cy + 520
    k_plan = kq(j, wp(26, 1, 0.5), 1)
    k_cut = nx(j, wp(26, 2, 0.5), k_plan)
    k_ok = nx(j, wp(26, 3, 0.3), k_cut)
    k_chest = nx(j, wp(26, 3, 0.9), k_ok)
    L.note("大方案", "先试", "看重一点")
    LX = cx - 380

    def plan(c, kk, T):
        g = pop_scale(T - tb(j, k_plan))
        if g <= 0:
            return None
        tc = tb(j, k_cut)
        f = ease_out(clamp01((T - tc) / 0.4)) if T >= tc else 0
        with K.at(c, cx + 120, cy - 180, 0, g):
            box(c, 0, 0, 520, 400, "#FFFFFF", BLUE, 7, 14)
            K.text(c, "大方案", 0, -140, 56, "sans_medium", BLUE)
            with K.at(c, -150 - 60 * f, 90 + 140 * f, -8 * f):
                box(c, 0, 0, 180, 140, GREEN_FILL if T >= tb(j, k_ok) else BLUE_FILL, GREEN if f else BLUE, 6, 10)
                if f:
                    K.text(c, "先试", 0, 0, 48, "hand", GREEN)
                if T >= tb(j, k_ok):
                    c.drawPath(check(70, -50, 34), wb.marker(GREEN, 10))
        return None
    ev(j, k_plan, plan, "wood_high", 0.65)
    b.hit(j, k_cut, "rim", 0.75, "切出一小块")
    b.hit(j, k_ok, "ding", 0.8, "试成了")

    def li(c, kk, T):
        tch = tb(j, k_chest)
        g = pop_scale(T - tb(j, k_plan) - 0.2)
        if g <= 0:
            return None
        hy = GY - 290
        pat = 10 * math.sin(clamp01((T - tch) / 0.5) * math.pi * 3) if T >= tch else 0
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "smile" if T >= tch else "flat", rh=(LX + 10, hy + 120 + pat) if T >= tch else None)
        if T >= tch:
            sparkle(c, LX, hy + 100, T - tch, YELLOW, 8, 50, 110)
        return None
    b.custom(j, k_plan, k_plan + 0.3, li)
    b.hit(j, k_chest, "tom", 0.8, "拍胸脯")


screen16()


# ================================================================ 屏 17：第三招：接手新项目，先拿本子到处问、记，不急着撕旧规矩
def screen17(j=17):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 2)
    GY = cy + 520
    k_old = kq(j, wp(27, 0, 0.6), 1)
    k_stop = nx(j, wp(27, 1, 0.5), k_old)
    k_ask = nx(j, wp(27, 2, 0.4), k_stop)
    L.note("旧流程", "先问清楚")
    LX = cx - 120

    def scene(c, kk, T):
        to, ts, ta = tb(j, k_old), tb(j, k_stop), tb(j, k_ask)
        g = pop_scale(T - to)
        if g <= 0:
            return None
        with K.at(c, cx - 300, cy - 220, 0, g):
            box(c, 0, 0, 340, 260, PARCH, "#7A5E3A", 6, 10)
            K.text(c, "旧流程", 0, -70, 50, "serif_black", INK)
            for q in range(3):
                C.line(c, (-110, -10 + q * 40), (110 - q * 30, -10 + q * 40), GRAY, 5)
        if T >= ts:
            with K.at(c, cx - 300, cy - 220, 0, C.slam_scale(T - ts)):
                c.drawCircle(0, 0, 170, wb.marker(RED, 8))
                C.line(c, (-120, 120), (120, -120), RED, 8)
            K.text(c, "全改", cx - 300, cy - 420, 44, "hand", RED)
        hy = GY - 290
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "flat", rh=(LX + 100, hy + 120) if T >= ta else None)
            if T >= ta:
                box(c, LX + 120, hy + 110, 90, 120, NOTE_FILL, ORANGE, 5, 6)
        if T >= ta:
            for i, x in enumerate((cx + 200, cx + 400)):
                gi = pop_scale(T - ta - i * 0.15)
                with at_pop(c, x, GY, gi):
                    if i:
                        draw_wang(c, x, GY, 0.8, mood="smile")
                    else:
                        draw_li(c, x, GY, 0.8, "smile")
            with K.at(c, cx + 160, cy - 200, 0, pop_scale(T - ta)):
                bubble_box(c, 0, 0, 340, 120, -1)
                K.text(c, "先问清楚", 0, 0, 54, "hand", GREEN)
        return None
    L.note("全改")
    b.custom(j, k_old, k_old + 0.3, scene, sfx="wood_high", gain=0.6)
    b.hit(j, k_stop, "rim", 0.8, "别一上来全改")
    b.hit(j, k_ask, "pop", 0.75, "先问清楚")


screen17()


# ================================================================ 屏 18：好处：放大镜更清楚，脚下的路更稳
def screen18(j=18):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_lens = kq(j, wp(28, 0, 0.6), 1)
    k_road = nx(j, wp(28, 1, 0.5), k_lens)
    L.note("看人更准", "做事更稳")
    LX = cx - 260

    def scene(c, kk, T):
        tl, tr = tb(j, k_lens), tb(j, k_road)
        g = pop_scale(T - tb(j, 0))
        if g <= 0:
            return None
        if T >= tr:
            f = ease_out(clamp01((T - tr) / 0.5))
            for q in range(5):
                if q / 5 > f:
                    break
                box(c, cx - 400 + q * 200, GY + 20, 180, 40, "#C9A97A", "#7A5E3A", 5, 6)
            K.text(c, "做事更稳", cx + 300, GY - 80, 60, "hand", GREEN, f)
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "smile", rh=(LX + 150, GY - 400) if T >= tl else None)
        if T >= tl:
            with K.at(c, LX + 260, cy - 200, 0, pop_scale(T - tl)):
                c.drawCircle(0, 0, 110, K.paint("#FFFFFF", 0.4))
                c.drawCircle(0, 0, 110, wb.marker(BLACK, 10))
                C.line(c, (-78, 78), (-160, 160), BLACK, 16)
                draw_ace(c, 0, 70, 0.35, mood="flat")
            K.text(c, "看人更准", LX + 300, cy - 400, 60, "hand", BLUE, clamp01((T - tl - 0.2) / 0.2))
        return None
    b.custom(j, 0, 0.3, scene, sfx="wood_low", gain=0.6)
    b.hit(j, k_lens, "ding", 0.75, "看人更准")
    b.hit(j, k_road, "tom", 0.7, "路更稳")


screen18()


# ================================================================ 屏 19：评论区；小李一次次动手，底气条往上涨；下一讲预告
def screen19(j=19):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z_))
    k_cmt = 0
    k_chips = nx(j, wp(30, 0, 0.3), 0)
    k_do = nx(j, wp(31, 0, 0.4), k_chips)
    k_bar = nx(j, wp(31, 3, 0.3), k_do)
    k_next = nx(j, wp(32, 1, 0.2), k_bar)
    b.move(j, k_do, (cx, cy + 380, Z_), 1.1)
    CH = ["装修师傅", "新来的经理", "我自己写的方案"]
    L.note("最会说、做最差的一次？", *CH, "下一讲", "同事当众", "让你下不来台，怎么办？", "底气")
    BY = cy - 330

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 20, BY, 0, sc):
            bubble_box(c, 0, 0, 1000, 360, -1)
            K.text(c, "最会说、做最差的一次？", 0, -110, 58, "hand", RED)
            for i, nm in enumerate(CH):
                g = pop_scale(T - tb(j, k_chips) - i * 0.15, 0.22)
                if g <= 0:
                    continue
                x, y = (-230 + (i % 2) * 460, 10) if i < 2 else (0, 110)
                with K.at(c, x, y, 0, g):
                    chip(c, 0, 0, nm, BLUE_FILL, BLUE, 44)
        return None
    ev(j, k_cmt, cmt, "pop", 0.7)
    b.hit(j, k_chips, "wood_high", 0.6, "评论冒出来")
    LX, LY = cx - 260, cy + 640

    def li(c, kk, T):
        g = pop_scale(T - tb(j, k_do))
        if g <= 0:
            return None
        tbar = tb(j, k_bar)
        hy = LY - 290 * 0.95
        ham = 30 * abs(math.sin((T - tb(j, k_do)) * 6))
        with at_pop(c, LX, LY, g):
            desk(c, LX + 230, LY - 170, 300, laptop=False)
            draw_li(c, LX, LY, 0.95, "smile", rh=(LX + 160, hy + 130 - ham))
        bx = cx + 350
        box(c, bx, cy + 420, 80, 440, "#FFFFFF", GRAY, 5, 14)
        lv = 0.25 + 0.65 * ease_out(clamp01((T - tbar) / 0.6)) if T >= tbar else 0.25
        c.drawRoundRect(skia.Rect.MakeXYWH(bx - 30, cy + 630 - 420 * lv, 60, 420 * lv), 14, 14, K.paint(GREEN))
        K.text(c, "底气", bx, cy + 160, 52, "hand", GREEN)
        if T >= tbar:
            sparkle(c, bx, cy + 630 - 420 * lv, T - tbar, YELLOW, 8, 40, 100)
        return None
    ev(j, k_do, li, "wood_low", 0.6)
    b.hit(j, k_bar, "ding", 0.8, "底气往上涨")

    def nxt(c, kk, T):
        t0 = tb(j, k_next)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        x, y = cx + 20, cy + 860
        with K.at(c, x, y, -2, sc):
            box(c, 0, 0, 1000, 230, "#FFFFFF", BLACK, 7, 18)
            K.rr(c, -380, -70, 170, 60, 30, RED)
            K.text(c, "下一讲", -380, -68, 38, "hand", "#FFFFFF")
            K.text(c, "同事当众", -140, -60, 58, "hand", BLACK)
            K.text(c, "让你下不来台，怎么办？", -40, 40, 54, "hand", BLACK)
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen19()

# ================================================================ 收尾
L.finish(cover_shot=8, square_shot=6, notes=NOTES)
L.export(globals())
