"""《资治通鉴》08 不翻旧账：说过你坏话的人，还能共事吗？（白板手绘 + AI 旁白，竖屏 2:3）

倒叙：先给结果——一大堆书信在火盆里烧起来，镜头拉开，下令的是曹操；再倒回去：官渡之战前袁绍兵多粮足、曹操弱得多，
许都和曹营里有人偷偷给袁绍写信；曹操打赢后在袁绍文书里翻出这些信，一封没追究，全部烧掉，“当绍之强，孤犹不能自保，况众人乎”。
今人部分：被同事背后说过怎么翻篇（换位想、删截图打招呼、往后看新的事）。古人的屏画在卷轴框里，今人在办公室。
文案见 zizhi/PLAN.md「### 08」。
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
                          pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "先看结果", 4),
    ([6, 7], "通鉴里的故事", 5),
    ([8, 9], "翻出书信", 6),
    ([10, 11], "皆焚之", 7),
    ([12], "一把火", 8),
    ([13, 14], "说回我们自己", 9),
    ([15], "第一步", 10),
    ([16], "第二步", 11),
    ([17], "第三步", 12),
    ([18], "好处", 13),
    ([19, 20, 21, 22], "评论区见", 14),
]

THEME = ZT.get("08")
L = Z.Lesson("08", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(13)]
Z_ = 0.72

NOTES = [
    "出处：司马光《资治通鉴》卷六十三 汉纪五十五（建安五年）官渡之战。",
    "原文：“收绍书中，得许下及军中人书，皆焚之。曰：当绍之强，孤犹不能自保，况众人乎！”",
    "“按说正好可以一个个查出来”“写过信的人不用再提心吊胆”是讲述者的话。今人（小李、同事）为虚构示意；古人造型为示意。",
]

CAO, YUAN, MIN = "purple", "ochre", "gray"
PARCH, PARCH_LINE = "#F7EFD9", "#9C7A3A"
GRAY_FILL = "#D9DCE1"


def gu_frame(j, k=0):
    cx, cy = R[j]
    L.note("通鉴")

    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k), 0.25)
        if sc <= 0:
            return None
        a = clamp01(sc)
        r = skia.Rect.MakeXYWH(cx - 580, cy - 585, 1160, 1215)
        c.drawRoundRect(r, 18, 18, K.paint(PARCH, 0.75 * a))
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


def letter(c, x, y, s=1.0, rot=0.0, a=1.0, burn=0.0):
    with K.at(c, x, y, rot, s):
        c.drawRect(skia.Rect.MakeXYWH(-60, -80, 120, 160), K.paint(PARCH, a))
        c.drawRect(skia.Rect.MakeXYWH(-60, -80, 120, 160), wb.marker(PARCH_LINE, 4, a))
        for q in range(3):
            C.line(c, (-30 + q * 30, -60), (-30 + q * 30, 60), INK, 3, a * 0.7)
        if burn > 0:
            c.drawRect(skia.Rect.MakeXYWH(-60, 80 - 160 * burn, 120, 160 * burn), K.paint("#3A2A22", a * 0.9))


def brazier(c, x, y, t, flame=1.0, a=1.0):
    """火盆：(x, y) 盆口中心。"""
    p = P((x - 160, y), (x + 160, y), (x + 110, y + 110), (x - 110, y + 110), close=True)
    c.drawPath(p, K.paint("#8A6A4A", a))
    c.drawPath(p, wb.marker(INK, 6, a))
    for dx in (-90, 90):
        C.line(c, (x + dx, y + 110), (x + dx * 1.3, y + 200), INK, 8, a)
    if flame > 0:
        for i, dx in enumerate((-70, 0, 70)):
            h = (120 + 40 * math.sin(t * 9 + i * 2)) * flame * (1.25 if i == 1 else 1)
            fp = P((x + dx - 50, y), (x + dx, y - h), (x + dx + 50, y), close=True)
            c.drawPath(fp, K.paint(ORANGE, a))
            c.drawPath(fp, wb.marker(RED, 4, a))
            c.drawPath(P((x + dx - 20, y), (x + dx, y - h * 0.5), (x + dx + 20, y), close=True), K.paint(YELLOW, a))


def phone(c, x, y, s=1.0, a=1.0):
    with K.at(c, x, y, 0, s):
        box(c, 0, 0, 120, 210, "#FFFFFF", BLACK, 6, 18, a)
        c.drawRect(skia.Rect.MakeXYWH(-46, -80, 92, 150), K.paint(BLUE_FILL, a))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：门外同事小声说“他撑不住”；项目做成后，小李手机里存着截图
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_pair = kq(j, wp(0, 1, 0.3), 0)
    k_say = nx(j, wp(0, 3, 0.3), k_pair)
    k_done = nx(j, wp(1, 0, 0.5), k_say)
    k_shot = nx(j, wp(1, 2, 0.4), k_done)
    L.note("他撑不住", "完成", "截图")
    LX = cx + 330

    def scene(c, kk, T):
        tp, ts, td, tsh = tb(j, k_pair), tb(j, k_say), tb(j, k_done), tb(j, k_shot)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        for i, x in enumerate((cx - 430, cx - 250)):
            with at_pop(c, x, GY, g):
                if i:
                    draw_ace(c, x, GY, 0.85, mood="smug", lh=(x - 40, GY - 270))
                else:
                    draw_wang(c, x, GY, 0.85, mood="o", head_dx=10)
        if T >= ts:
            with K.at(c, cx - 300, cy - 120, 0, pop_scale(T - ts)):
                bubble_box(c, 0, 0, 320, 110, 1, 0.9, "#F0F0F0")
                K.text(c, "他撑不住", 0, 0, 52, "hand", GRAY)
        with at_pop(c, LX, GY, pop_scale(T - tp - 0.2)):
            draw_li(c, LX, GY, 0.95, "smile" if T >= td else "flat", rh=(LX - 100, GY - 220) if T >= tsh else None)
            if T >= tsh:
                phone(c, LX - 120, GY - 240, 0.8)
        if T >= td:
            seal(c, cx + 200, cy - 360, "完成", 70, -6, C.slam_scale(T - td))
        if T >= tsh:
            for q in range(3):
                with K.at(c, LX - 220 + q * 40, cy - 120 - q * 50, -8 + q * 6, pop_scale(T - tsh - q * 0.1)):
                    box(c, 0, 0, 200, 120, "#FFFFFF", GRAY, 4, 10)
                    K.text(c, "截图", 0, 0, 36, "sans_medium", GRAY)
        return None
    ev(j, k_pair, scene, "wood_low", 0.6)
    b.hit(j, k_say, "rim", 0.75, "背后说撑不住")
    b.hit(j, k_done, "kick", 0.75, "项目做成了")
    b.hit(j, k_shot, "pop", 0.7, "截图还存着")


screen1()


# ================================================================ 屏 2（drop）：小李和那位同事开会，小李胸口扎着一根刺
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_meet = kq(j, wp(2, 0, 0.5), 0)
    L.note("刺")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_meet))
        if g <= 0:
            return None
        LX, AX = cx - 300, cx + 300
        with at_pop(c, cx, GY, g):
            box(c, cx, GY - 150, 900, 60, "#E7D6BA", "#8B6B43", 6, 10)
            draw_li(c, LX, GY, 0.95, "sad" if T >= tb(j, dk) else "flat")
            draw_ace(c, AX, GY, 0.95, mood="flat")
        td = tb(j, dk)
        if T >= td:
            f = ease_out(clamp01((T - td) / 0.2))
            hy = GY - 290 * 0.95
            sx, sy = LX + lerp(160, 10, f), hy + lerp(40, 130, f)
            C.line(c, (sx + 160, sy - 120), (sx, sy), "#5E7A2E", 10)
            c.drawPath(P((sx, sy), (sx + 30, sy - 4), (sx + 10, sy - 26), close=True), K.paint("#5E7A2E"))
            K.text(c, "刺", LX + 230, hy - 80, 70, "hand", RED, f)
        return None
    ev(j, k_meet, scene, "wood_low", 0.6)
    b.hit(j, dk, "kick", 0.9, "心里扎着刺")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：左：拍出截图吵翻；右：憋着，头顶冒烟
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_left = kq(j, wp(3, 0, 0.5), 0)
    k_ugly = nx(j, wp(3, 1, 0.5), k_left)
    k_right = nx(j, wp(3, 2, 0.5), k_ugly)
    k_smoke = nx(j, wp(3, 3, 0.5), k_right)
    L.note("难看", "咽不下")

    def scene(c, kk, T):
        tl, tu, tr, ts = tb(j, k_left), tb(j, k_ugly), tb(j, k_right), tb(j, k_smoke)
        C.line(c, (cx, cy - 450), (cx, cy + 540), GRAY, 4)
        g = pop_scale(T - tl)
        if g > 0:
            with at_pop(c, cx - 400, GY, g):
                draw_li(c, cx - 400, GY, 0.8, "sad" if T >= tu else "flat", rh=(cx - 280, GY - 300))
                draw_ace(c, cx - 140, GY, 0.8, mood="cold" if T >= tu else "flat")
            phone(c, cx - 280, cy + 120, 0.7 * g)
            if T >= tu:
                K.burst(c, cx - 270, cy + 40, T - tu, RED, 20, 90, 6, 6)
                with K.at(c, cx - 270, cy - 300, -6, C.slam_scale(T - tu)):
                    chip(c, 0, 0, "难看", RED_FILL, RED, 54)
        gr = pop_scale(T - tr)
        if gr > 0:
            x = cx + 280
            with at_pop(c, x, GY, gr):
                draw_li(c, x, GY, 0.9, "sad", lh=(x - 40, GY - 180), rh=(x + 40, GY - 180))
            if T >= ts:
                hy = GY - 290 * 0.9
                for q in range(3):
                    f = ((T - ts) * 0.9 + q * 0.33) % 1
                    c.drawCircle(x + 20 * math.sin(q + T * 3), hy - 70 - 160 * f, 24 + 20 * f, K.paint(GRAY, 0.5 * (1 - f)))
                with K.at(c, x, cy - 300, 4, C.slam_scale(T - ts)):
                    chip(c, 0, 0, "咽不下", NOTE_FILL, ORANGE, 54)
        return None
    ev(j, k_left, scene, "wood_high", 0.6)
    b.hit(j, k_ugly, "rim", 0.8, "场面难看")
    b.hit(j, k_right, "wood_low", 0.65, "不翻")
    b.hit(j, k_smoke, "tom", 0.75, "咽不下这口气")


screen3()


# ================================================================ 屏 4：先看结果——火盆里一大堆书信烧起来；镜头拉开，曹操站在旁边
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx + 120, cy - 40, Z_ * 1.25))
    gu_frame(j, 0)
    GY = cy + 520
    k_fire = kq(j, wp(4, 0, 0.5), 0)
    k_pile = nx(j, wp(4, 1, 0.5), k_fire)
    k_burn = nx(j, wp(4, 2, 0.5), k_pile)
    k_cao = nx(j, wp(5, 1, 0.3), k_burn)
    b.move(j, k_cao, (cx, cy + 10, Z_), 1.0)
    L.note("曹操")
    BX, BY = cx + 160, cy + 150

    def scene(c, kk, T):
        tf, tp, tbn = tb(j, k_fire), tb(j, k_pile), tb(j, k_burn)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        flame = 0.4 if T < tbn else lerp(0.4, 1.2, ease_out(clamp01((T - tbn) / 0.4)))
        brazier(c, BX, BY, T, flame * g)
        if T >= tp:
            for i in range(7):
                t0 = tp + i * 0.08
                f = ease_in_out(clamp01((T - t0) / 0.5))
                x = lerp(BX - 380 + (i % 3) * 40, BX - 60 + i * 20, f)
                y = lerp(BY - 420 - i * 30, BY - 30, f)
                burn = clamp01((T - tbn - i * 0.1) / 0.8) if T >= tbn else 0
                letter(c, x, y, 0.8, (i * 37 % 40) - 20, 1 - 0.7 * burn, burn)
        if T >= tbn:
            for q in range(6):
                f = ((T - tbn) * 0.7 + q / 6) % 1
                c.drawCircle(BX - 80 + q * 30 + 30 * math.sin(T * 2 + q), BY - 200 - 300 * f, 6, K.paint(ORANGE, 1 - f))
        return None
    ev(j, k_fire, scene, "wood_low", 0.6)
    b.hit(j, k_pile, "shaker", 0.75, "一大堆书信")
    b.hit(j, k_burn, "tom", 0.85, "烧起来")

    def cao(c, kk, T):
        t0 = tb(j, k_cao)
        g = pop_scale(T - t0 - 0.5)
        if g <= 0:
            return None
        x = cx - 370
        with at_pop(c, x, GY, g):
            gu(c, x, GY, 1.0, CAO, hat="guan", beard="black", mood="flat", rh=(x + 160, GY - 250))
            name_tag(c, x, GY - 460, "曹操", "#6B3F7A", 50)
        return None
    b.custom(j, k_cao, k_cao + 0.3, cao, sfx="kick", gain=0.85)


screen4()


# ================================================================ 屏 5：竹简“卷六十三”；天平：袁绍兵多粮足 vs 曹操；几封信奔向袁营
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_slip = kq(j, wp(6, 0, 0.3), 0)
    k_yuan = nx(j, wp(6, 2, 0.4), k_slip)
    k_weak = nx(j, wp(6, 3, 0.4), k_yuan)
    k_mail = nx(j, wp(7, 2, 0.3), k_weak)
    SX = cx - 400
    L.note("资治通鉴", "卷六十三", "汉纪五十五", "袁绍", "曹操", "许都", "曹营")

    def slips(c, kk, T):
        f = ease_out(clamp01((T - tb(j, k_slip)) / 0.6))
        if f <= 0:
            return None
        bamboo_slips(c, SX, cy - 180, max(60, 240 * f), 640, n=max(1, int(3 * f)))
        a = clamp01((T - tb(j, k_slip) - 0.3) / 0.3)
        slip_text(c, SX + 40, cy - 440, "资治通鉴", 64, "#3A2A12", a)
        slip_text(c, SX - 60, cy - 430, "卷六十三", 46, RED, a)
        return None
    ev(j, k_slip, slips, "muyu", 0.7, 0.6)

    def scale(c, kk, T):
        ty, tw = tb(j, k_yuan), tb(j, k_weak)
        g = pop_scale(T - ty)
        if g <= 0:
            return None
        PX, PY = cx + 160, cy - 300
        tilt = 14 * ease_out(clamp01((T - tw) / 0.4)) if T >= tw else 0
        C.line(c, (PX, PY), (PX, PY + 200), "#7A5E3A", 8)
        with K.at(c, PX, PY, -tilt):
            C.line(c, (-260, 0), (260, 0), "#7A5E3A", 8)
            for sg, lab, col in ((-1, "袁绍", "#8A5A1E"), (1, "曹操", "#6B3F7A")):
                with K.at(c, sg * 240, 0, tilt):
                    C.line(c, (0, 0), (0, 50), GRAY, 3)
                    box(c, 0, 100, 160 if sg < 0 else 120, 90 if sg < 0 else 70, "#FFFFFF", col, 5, 8)
                    K.text(c, lab, 0, 100, 44 if sg < 0 else 36, "serif_black", col)
        return None
    b.custom(j, k_yuan, k_yuan + 0.3, scale, sfx="tom", gain=0.75)
    b.hit(j, k_weak, "wood_low", 0.7, "曹操弱得多")

    def mail(c, kk, T):
        tm = tb(j, k_mail)
        g = pop_scale(T - tm + 0.4)
        if g <= 0:
            return None
        YX, YY = cx + 400, GY - 100
        with at_pop(c, YX, YY, g):
            flag(c, YX, YY, 0.5, "袁", "#8A5A1E")
        for i, (nm, x0) in enumerate((("许都", cx - 380), ("曹营", cx - 120))):
            with K.at(c, x0, GY - 80, 0, g):
                box(c, 0, 0, 180, 90, "#FFFFFF", "#6B3F7A", 5, 10)
                K.text(c, nm, 0, 0, 44, "serif_black", "#6B3F7A")
            if T >= tm:
                for q in range(2):
                    f = clamp01((T - tm - i * 0.15 - q * 0.25) / 0.7)
                    if f <= 0:
                        continue
                    x = lerp(x0, YX - 60, f)
                    y = GY - 80 - 200 * math.sin(math.pi * f)
                    letter(c, x, y, 0.45, f * 40)
        return None
    b.custom(j, k_mail, k_mail + 0.3, mail, sfx="shaker", gain=0.75)


screen5()


# ================================================================ 屏 6：曹操在袁绍的文书箱里翻出一摞信；放大镜“可以一个个查”
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_win = kq(j, wp(8, 0, 0.5), 0)
    k_box = nx(j, wp(8, 1, 0.5), k_win)
    k_find = nx(j, wp(8, 2, 0.5), k_box)
    k_lens = nx(j, wp(9, 2, 0.4), k_find)
    CX_ = cx - 360
    L.note("胜", "一个个查")

    def scene(c, kk, T):
        tw, tbx, tf, tl = tb(j, k_win), tb(j, k_box), tb(j, k_find), tb(j, k_lens)
        g = pop_scale(T - tw)
        if g <= 0:
            return None
        with at_pop(c, CX_, GY, g):
            gu(c, CX_, GY, 0.95, CAO, hat="guan", beard="black", mood="smile", rh=(CX_ + 170, GY - 250) if T >= tf else None)
            name_tag(c, CX_, GY - 440, "曹操", "#6B3F7A", 44)
        seal(c, CX_ + 30, cy - 350, "胜", 80, -6, g)
        if T >= tbx:
            with K.at(c, cx + 150, GY - 80, 0, pop_scale(T - tbx)):
                box(c, 0, 0, 380, 160, "#C98B4B", "#7A4A1E", 6, 10)
                K.text(c, "袁", 0, 0, 60, "serif_black", "#FFFFFF")
        if T >= tf:
            for i in range(5):
                f = ease_out(clamp01((T - tf - i * 0.08) / 0.4))
                letter(c, cx + 60 + i * 50, lerp(GY - 140, cy - 120 - (i % 2) * 40, f), 0.7, (i - 2) * 8)
        if T >= tl:
            f = ease_in_out(clamp01((T - tl) / 0.6))
            with K.at(c, lerp(cx + 50, cx + 260, f), cy - 140, 0, pop_scale(T - tl)):
                c.drawCircle(0, 0, 90, K.paint("#FFFFFF", 0.3))
                c.drawCircle(0, 0, 90, wb.marker(BLACK, 9))
                C.line(c, (64, 64), (140, 140), BLACK, 14)
            K.text(c, "一个个查", cx + 200, cy - 380, 60, "hand", RED, clamp01((T - tl - 0.2) / 0.2))
        return None
    ev(j, k_win, scene, "tom", 0.75)
    b.hit(j, k_box, "wood_low", 0.65, "袁绍的文书箱")
    b.hit(j, k_find, "shaker", 0.75, "翻出这些信")
    b.hit(j, k_lens, "pop", 0.7, "可以一个个查")


screen6()


# ================================================================ 屏 7：曹操摆手，整摞信扔进火里；“当绍之强，孤犹不能自保”
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_no = kq(j, wp(10, 0, 0.5), 0)
    k_toss = nx(j, wp(10, 1, 0.5), k_no)
    k_say = nx(j, wp(11, 1, 0.3), k_toss)
    k_them = nx(j, wp(11, 4, 0.3), k_say)
    CX_ = cx - 380
    BX, BY = cx + 220, cy + 300
    L.note("不查", "孤犹不能自保", "况众人乎")

    def scene(c, kk, T):
        tn, tt, ts, tth = tb(j, k_no), tb(j, k_toss), tb(j, k_say), tb(j, k_them)
        g = pop_scale(T - tn)
        if g <= 0:
            return None
        wave = 20 * math.sin((T - tn) * 10) if T < tt else 0
        with at_pop(c, CX_, GY, g):
            gu(c, CX_, GY, 0.95, CAO, hat="guan", beard="black", mood="flat",
               rh=(CX_ + 160, GY - 330 + wave) if T < ts else (CX_ + 120, GY - 230))
            name_tag(c, CX_, GY - 440, "曹操", "#6B3F7A", 44)
        flame = 0.5 if T < tt else 1.2
        brazier(c, BX, BY, T, flame)
        if T < tt + 0.8:
            f = ease_in_out(clamp01((T - tt) / 0.5)) if T >= tt else 0
            for i in range(5):
                letter(c, lerp(CX_ + 230 + i * 30, BX - 40 + i * 20, f), lerp(cy - 100 - i * 20, BY - 40, f), 0.6,
                       (i - 2) * 10 + 200 * f, 1 - 0.8 * clamp01((T - tt - 0.5) / 0.3))
        if T >= tn and T < tt:
            with K.at(c, CX_ + 120, cy - 330, -4, pop_scale(T - tn)):
                chip(c, 0, 0, "不查", RED_FILL, RED, 54)
        if T >= ts:
            with K.at(c, cx + 100, cy - 330, 0, pop_scale(T - ts)):
                bamboo_slips(c, 0, 0, 640, 170, n=8)
                K.text(c, "孤犹不能自保", 0, -10, 64, "serif_black", INK)
        if T >= tth:
            with K.at(c, cx + 120, cy - 150, -4, C.slam_scale(T - tth)):
                chip(c, 0, 0, "况众人乎", NOTE_FILL, ORANGE, 58)
        return None
    ev(j, k_no, scene, "wood_high", 0.65)
    b.hit(j, k_toss, "kick", 0.9, "全部扔进火里")
    b.hit(j, k_say, "bangzi", 0.8, "孤犹不能自保")
    b.hit(j, k_them, "rim", 0.8, "何况别人")
    b.shots[j].shake = [(k_toss, 9.0)]


screen7()


# ================================================================ 屏 8：写过信的几个人，头顶的乌云散开
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_people = 0
    k_clear = kq(j, wp(12, 2, 0.4), 1)
    L.note("安心")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_people))
        if g <= 0:
            return None
        tc = tb(j, k_clear)
        f = ease_out(clamp01((T - tc) / 0.6)) if T >= tc else 0
        for i, x in enumerate((cx - 330, cx, cx + 330)):
            with at_pop(c, x, GY, g):
                gu(c, x, GY, 0.8, (MIN, "brown", "teal")[i], hat="guan", beard="black" if i != 1 else None,
                   mood="smile" if f > 0.5 else "sad")
            hy = GY - 290 * 0.8
            for q in range(3):
                cxx = x - 60 + q * 60 + (q - 1) * 160 * f
                c.drawCircle(cxx, hy - 160 - 40 * (q % 2) - 100 * f, 50, K.paint("#6B6B6B", 0.8 * (1 - f) * g))
            if f > 0:
                sparkle(c, x, hy - 120, T - tc, YELLOW, 8, 40, 100)
        if T >= tc:
            seal(c, cx, cy - 380, "安心", 80, -4, C.slam_scale(T - tc))
        return None
    ev(j, k_people, scene, "wood_low", 0.6)
    b.hit(j, k_clear, "ding", 0.85, "不用再提心吊胆")


screen8()


# ================================================================ 屏 9：说回我们：小李摸摸胸口的刺；“三步”
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_touch = kq(j, wp(13, 1, 0.4), 1)
    k_3 = nx(j, wp(14, 1, 0.5), k_touch)
    LX = cx - 280
    L.note("疙瘩", "三步")

    def scene(c, sc, T):
        tt = tb(j, k_touch)
        hy = GY - 290
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 1.0, "flat", rh=(LX + 20, hy + 130) if T >= tt else None)
            if T >= tt:
                c.drawCircle(LX + 30, hy + 120, 36, wb.marker(RED, 6))
        if T >= tt:
            K.text(c, "疙瘩", LX + 200, hy + 60, 60, "hand", RED, clamp01((T - tt) / 0.2))
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_touch, "wood_high", 0.65, "心里有疙瘩")
    L.stamp_ev(j, k_3, "三步", cx + 250, cy - 300, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen9()


# ================================================================ 屏 10：第一步：换位想——对方那时压力山大，说了句丧气话
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 0)
    GY = cy + 520
    k_li = kq(j, wp(15, 0, 0.6), 1)
    k_think = nx(j, wp(15, 1, 0.5), k_li)
    k_say = nx(j, wp(15, 3, 0.4), k_think)
    LX = cx - 330
    L.note("截止日期", "完了", "压力")

    def scene(c, kk, T):
        tl, tt, ts = tb(j, k_li), tb(j, k_think), tb(j, k_say)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "flat", rh=(LX + 40, GY - 290 * 0.95 - 30))
        if T >= tt:
            gt = pop_scale(T - tt)
            with K.at(c, cx + 180, cy - 80, 0, gt):
                c.drawOval(skia.Rect.MakeXYWH(-340, -300, 680, 600), K.paint("#FFFFFF"))
                c.drawOval(skia.Rect.MakeXYWH(-340, -300, 680, 600), wb.marker(GRAY, 6))
                draw_ace(c, -60, 220, 0.75, mood="flat", lh=(-120, 50), rh=(0, 50))
                for q in range(3):
                    box(c, -60 + (q % 2) * 10, 30 - q * 50, 200, 46, NOTE_FILL, ORANGE, 4, 6)
                K.text(c, "压力", 170, -170, 54, "hand", RED)
            for q in range(2):
                c.drawCircle(LX + 140 + q * 40, cy - 30 - q * 50, 16 - q * 4, wb.marker(GRAY, 5, clamp01(gt)))
        if T >= ts:
            with K.at(c, cx + 300, cy - 180, 0, C.slam_scale(T - ts)):
                bubble_box(c, 0, 0, 220, 100, -1)
                K.text(c, "完了", 0, 0, 52, "hand", GRAY)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_think, "pop", 0.75, "换位想想")
    b.hit(j, k_say, "rim", 0.75, "说了句丧气话")


screen10()


# ================================================================ 屏 11：第二步：截图拖进垃圾桶；见面先说“早”
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 1)
    GY = cy + 520
    k_phone = kq(j, wp(16, 0, 0.6), 1)
    k_del = nx(j, wp(16, 1, 0.5), k_phone)
    k_hi = nx(j, wp(16, 2, 0.5), k_del)
    L.note("早", "截图")

    def scene(c, kk, T):
        tp, td, th = tb(j, k_phone), tb(j, k_del), tb(j, k_hi)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        with K.at(c, cx - 150, cy - 180, 0, g * 2.0):
            phone(c, 0, 0)
            if T < td + 0.4:
                f = ease_in_out(clamp01((T - td) / 0.4)) if T >= td else 0
                with K.at(c, lerp(0, 120, f), lerp(-10, 60, f), 0, 1 - 0.7 * f):
                    box(c, 0, 0, 80, 60, "#FFFFFF", GRAY, 3, 6)
            with K.at(c, 130, 70, 0, 0.5):
                c.drawPath(P((-40, -40), (40, -40), (30, 50), (-30, 50), close=True), K.paint(GRAY_FILL))
                c.drawPath(P((-40, -40), (40, -40), (30, 50), (-30, 50), close=True), wb.marker(INK, 5))
        if T >= th:
            LX, AX = cx - 300, cx + 300
            with at_pop(c, cx, GY, pop_scale(T - th)):
                draw_li(c, LX, GY, 0.85, "smile", rh=(LX + 120, GY - 300))
                draw_ace(c, AX, GY, 0.85, mood="smug")
            with K.at(c, LX + 60, cy + 30, 0, C.slam_scale(T - th)):
                bubble_box(c, 0, 0, 160, 100, -1)
                K.text(c, "早", 0, 0, 56, "hand", GREEN)
        return None
    ev(j, k_phone, scene, "wood_high", 0.65)
    b.hit(j, k_del, "shaker", 0.8, "截图删了")
    b.hit(j, k_hi, "pop", 0.8, "先打个招呼")


screen11()


# ================================================================ 屏 12：第三步：两人一起做新任务，进度条往前走
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 2)
    GY = cy + 520
    k_task = kq(j, wp(17, 0, 0.6), 1)
    k_do = nx(j, wp(17, 1, 0.5), k_task)
    k_bar = nx(j, wp(17, 2, 0.5), k_do)
    L.note("新任务")

    def scene(c, kk, T):
        tt, td, tbr = tb(j, k_task), tb(j, k_do), tb(j, k_bar)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 250, 0, g):
            box(c, 0, 0, 360, 120, NOTE_FILL, ORANGE, 6, 12)
            K.text(c, "新任务", 0, 0, 56, "hand", INK)
        with at_pop(c, cx, GY, g):
            desk(c, cx, GY - 170, 460)
            draw_li(c, cx - 320, GY, 0.85, "flat", rh=(cx - 170, GY - 220) if T >= td else None)
            draw_ace(c, cx + 320, GY, 0.85, mood="flat", lh=(cx + 170, GY - 220) if T >= td else None)
        if T >= tbr:
            p = 0.15 + 0.7 * ease_out(clamp01((T - tbr) / 0.8))
            box(c, cx, cy - 60, 640, 60, "#FFFFFF", BLACK, 5, 30)
            c.drawRoundRect(skia.Rect.MakeXYWH(cx - 310, cy - 84, 620 * p, 48), 24, 24, K.paint(GREEN))
        return None
    ev(j, k_task, scene, "wood_high", 0.65)
    b.hit(j, k_do, "pop", 0.7, "一起干")
    b.hit(j, k_bar, "ding", 0.8, "用新的事说话")


screen12()


# ================================================================ 屏 13：好处：两人之间的一道墙倒下
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_wall = 0
    k_light = kq(j, wp(18, 0, 0.6), 1)
    k_fall = nx(j, wp(18, 1, 0.5), k_light)
    L.note("墙")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_wall))
        if g <= 0:
            return None
        tl, tf = tb(j, k_light), tb(j, k_fall)
        f = ease_in_out(clamp01((T - tf) / 0.5)) if T >= tf else 0
        with at_pop(c, cx, GY, g):
            draw_li(c, cx - 300, GY, 0.95, "smile" if T >= tl else "flat")
            draw_ace(c, cx + 300, GY, 0.95, mood="smile" if T >= tf else "flat")
            with K.at(c, cx, GY, 85 * f):
                for r_ in range(5):
                    for q in range(2):
                        box(c, -45 + q * 90 - (r_ % 2) * 45 + 45, -40 - r_ * 80, 86, 74, "#D8C7A6", "#7A5E3A", 4, 4)
                K.text(c, "墙", 0, -460, 50, "hand", "#7A5E3A", 1 - f)
        if T >= tf:
            K.burst(c, cx + 200, GY - 40, T - tf, GRAY, 30, 120, 8, 7, 0.6)
            sparkle(c, cx, cy - 200, T - tf, YELLOW, 10, 60, 140)
        return None
    ev(j, k_wall, scene, "wood_low", 0.6)
    b.hit(j, k_light, "pop", 0.65, "心里轻了")
    b.hit(j, k_fall, "kick", 0.85, "墙倒了")


screen13()


# ================================================================ 屏 14：评论区；一张截图化成灰；下一讲预告
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z_))
    k_cmt = 0
    k_chips = nx(j, wp(20, 0, 0.3), 0)
    k_shot = nx(j, wp(21, 0, 0.4), k_chips)
    k_ash = nx(j, wp(21, 3, 0.3), k_shot)
    k_next = nx(j, wp(22, 1, 0.2), k_ash)
    b.move(j, k_shot, (cx, cy + 380, Z_), 1.1)
    CH = ["你不行", "又是你", "就这？"]
    L.note("放不下的一句话？", *CH, "下一讲", "想请高手帮忙", "为什么总被拒？", "轻")
    BY = cy - 330

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 20, BY, 0, sc):
            bubble_box(c, 0, 0, 1000, 360, -1)
            K.text(c, "放不下的一句话？", 0, -110, 62, "hand", RED)
            for i, nm in enumerate(CH):
                g = pop_scale(T - tb(j, k_chips) - i * 0.15, 0.22)
                if g <= 0:
                    continue
                x, y = (-230 + (i % 2) * 460, 10) if i < 2 else (0, 110)
                with K.at(c, x, y, 0, g):
                    chip(c, 0, 0, nm, GRAY_FILL, GRAY, 44)
        return None
    ev(j, k_cmt, cmt, "pop", 0.7)
    b.hit(j, k_chips, "wood_high", 0.6, "评论冒出来")
    LX, LY = cx - 300, cy + 640

    def li(c, kk, T):
        ts, ta = tb(j, k_shot), tb(j, k_ash)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        with at_pop(c, LX, LY, g):
            draw_li(c, LX, LY, 0.95, "smile" if T >= ta else "flat", rh=(LX + 150, LY - 300))
        f = clamp01((T - ta) / 0.8) if T >= ta else 0
        x, y = cx + 200, cy + 380
        if f < 1:
            with K.at(c, x, y, -6, g):
                box(c, 0, 0, 300, 200, "#FFFFFF", GRAY, 5, 12, 1 - f)
                K.text(c, "截图", 0, 0, 50, "sans_medium", GRAY, 1 - f)
        if T >= ta:
            for q in range(10):
                ff = clamp01((T - ta - q * 0.03) / 1.0)
                c.drawCircle(x - 120 + q * 26, y + 60 - 300 * ff, 7, K.paint(GRAY, 0.7 * (1 - ff)))
            K.text(c, "轻", x, y + 230, 80, "hand", GREEN, clamp01((T - ta - 0.4) / 0.2))
        return None
    ev(j, k_shot, li, "wood_low", 0.6)
    b.hit(j, k_ash, "ding", 0.8, "截图化成灰")

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
            K.text(c, "想请高手帮忙", -100, -60, 58, "hand", BLACK)
            K.text(c, "为什么总被拒？", -60, 40, 58, "hand", BLACK)
            hut = P((330, 60), (330, -10), (390, -70), (450, -10), (450, 60), close=True)
            c.drawPath(hut, K.paint(PARCH))
            c.drawPath(hut, wb.marker("#7A4A1E", 5))
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen14()

# ================================================================ 收尾
L.finish(cover_shot=7, square_shot=7, notes=NOTES)
L.export(globals())
