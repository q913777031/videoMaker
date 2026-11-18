"""《资治通鉴》04 将相和：同事当众让你下不来台，怎么办？（白板手绘 + AI 旁白，竖屏 2:3）

对话改写：先回放小李被当众顶了以后“当场怼回去”的那场会（两人越吵越凶、背对背），再讲蔺相如与廉颇——渑池之会后
蔺相如位在廉颇之上、廉颇放话、蔺相如称病避让、门客要走、“两虎共斗”、“先国家之急而后私仇”、负荆请罪——
最后用倒带按钮把那场会按蔺相如的办法重来一遍（三步）。古人的屏画在卷轴框里，今人在办公室。
文案见 zizhi/PLAN.md「### 04」。
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
                          at_pop, bamboo_slips, box, bubble_box, desk, draw_ace, draw_li, draw_wang, flag, gu, head_of,
                          pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3, 4], "先回放一遍", 3),
    ([5, 6], "通鉴里的故事", 4),
    ([7, 8], "渑池之会", 5),
    ([9, 10], "廉颇不服", 6),
    ([11, 12], "称病避让", 7),
    ([13, 14], "手下要走", 8),
    ([15, 16], "两虎共斗", 9),
    ([17], "先国家之急", 10),
    ([18, 19], "负荆请罪", 11),
    ([20, 21], "说回我们自己", 12),
    ([22], "第一步", 13),
    ([23], "第二步", 14),
    ([24], "第三步", 15),
    ([25], "好处", 16),
    ([26, 27, 28, 29], "评论区见", 17),
]

THEME = ZT.get("04")
L = Z.Lesson("04", SCREENS, drop_screen=2, board_size=(5000, 12000), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(16)]
Z_ = 0.72

NOTES = [
    "出处：司马光《资治通鉴》卷四 周纪四（赧王三十六年，纪年待核）渑池之会与将相和。",
    "原文：相如为上卿，“位在廉颇之右”；廉颇“我为赵将，有攻城野战之大功。蔺相如素贱人，徒以口舌而位居我上……我见相如，必辱之”；"
    "相如“每朝常称病，不欲争列。出而望见，辄引车避匿”；舍人以为耻；“子视廉将军孰与秦王……夫以秦王之威，而相如廷叱之……"
    "强秦所以不敢加兵于赵者，徒以吾两人在也。今两虎共斗，其势不俱生。吾所以为此者，以先国家之急而后私仇也”；"
    "“廉颇闻之，肉袒负荆，至门谢罪，遂为刎颈之交。”",
    "今人（小李、同事）为虚构示意；古人造型为示意。",
]

LIANPO, LIN, KING, QIN, KE = "gray", "teal", "ochre", "purple", "brown"
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
        c.drawRoundRect(r, 18, 18, K.paint(PARCH, 0.7 * a))
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


def flame(c, x, y, s=1.0, a=1.0):
    with K.at(c, x, y, 0, s):
        p = P((0, -90), (40, -30), (36, 30), (0, 60), (-36, 30), (-40, -30), close=True)
        c.drawPath(p, K.paint(ORANGE, a))
        c.drawPath(p, wb.marker(RED, 5, a))


def cart(c, x, y, s=1.0, a=1.0, col="#C98B4B"):
    with K.at(c, x, y, 0, s):
        box(c, 0, -110, 240, 110, col, "#7A4A1E", 6, 10, a)
        for wx in (-80, 80):
            c.drawCircle(wx, -30, 46, K.paint("#FFFFFF", a))
            c.drawCircle(wx, -30, 46, wb.marker("#7A4A1E", 6, a))


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


def meeting(c, cx, GY, a=1.0):
    box(c, cx, GY - 150, 980, 60, "#E7D6BA", "#8B6B43", 6, 10, a)
    for dx in (-420, 420):
        C.line(c, (cx + dx, GY - 120), (cx + dx, GY), "#8B6B43", 9, a)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：会上同事指着小李的方案摇头，大家看过来；小李脸红
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_table = 0
    k_point = kq(j, wp(0, 2, 0.4), 1)
    k_no = nx(j, wp(0, 3, 0.5), k_point)
    k_red = nx(j, wp(1, 1, 0.4), k_no)
    LX, AX = cx - 330, cx + 330
    L.note("小李的方案", "不行")

    def scene(c, sc, T):
        tp, tn, tr = tb(j, k_point), tb(j, k_no), tb(j, k_red)
        with at_pop(c, cx, GY, sc):
            meeting(c, cx, GY)
            draw_li(c, LX, GY, 0.95, "sad" if T >= tn else "flat")
            if T >= tr:
                hy = GY - 290 * 0.95
                f = clamp01((T - tr) / 0.4)
                c.drawCircle(LX, hy, 42, K.paint(RED, 0.35 * f))
                for sg in (-1, 1):
                    c.drawOval(skia.Rect.MakeXYWH(LX + sg * 24 - 14, hy + 4, 28, 16), K.paint(RED, 0.75 * f))
                    C.line(c, (LX + sg * 70, hy - 50), (LX + sg * 90, hy - 80), RED, 5, f)
            draw_ace(c, AX, GY, 0.95, mood="smug", rh=(AX - 150, GY - 300) if T >= tp else None,
                     head_dx=8 * math.sin((T - tn) * 12) * math.exp(-(T - tn) * 2) if T >= tn else 0)
        return None
    ev(j, k_table, L.pop_fn(j, k_table, scene), "wood_low", 0.6)

    def doc(c, kk, T):
        g = pop_scale(T - tb(j, k_point))
        if g <= 0:
            return None
        with K.at(c, cx, cy - 280, -3, g):
            box(c, 0, 0, 440, 280, "#FFFFFF", BLUE, 7, 12)
            K.text(c, "小李的方案", 0, -80, 52, "sans_medium", BLUE)
            for r in range(2):
                C.line(c, (-150, 10 + r * 50), (150 - r * 50, 10 + r * 50), GRAY, 6)
        tn = tb(j, k_no)
        if T >= tn:
            with K.at(c, cx + 130, cy - 200, -8, C.slam_scale(T - tn)):
                chip(c, 0, 0, "不行", RED_FILL, RED, 70)
        return None
    ev(j, k_point, doc, "pop", 0.65)
    b.hit(j, k_no, "rim", 0.85, "当众说不行")
    b.hit(j, k_red, "tom", 0.75, "脸红了")
    b.shots[j].shake = [(k_no, 7.0)]


screen1()


# ================================================================ 屏 2（drop）：群里一句阴阳怪气的话，小李盯着屏幕，窗外天黑
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_phone = 0
    k_msg = kq(j, wp(2, 1, 0.5), 1)
    k_night = max(k_msg + 1, min(dk - 1, kq(j, wp(2, 2, 0.5), k_msg + 1)))
    L.note("哟，大方案", "气")
    LX = cx - 280

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_phone))
        if g <= 0:
            return None
        tn, td = tb(j, k_night), tb(j, dk)
        night = ease_out(clamp01((T - tn) / 0.6)) if T >= tn else 0
        with K.at(c, cx + 300, cy - 300, 0, g):
            box(c, 0, 0, 300, 300, "#FFFFFF" if not night else "#3A4466", BLACK, 7, 10)
            C.line(c, (-150, 0), (150, 0), BLACK, 5)
            C.line(c, (0, -150), (0, 150), BLACK, 5)
            if night:
                c.drawCircle(70, -70, 34, K.paint(NOTE_FILL, night))
        hy = GY - 290
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "sad", rh=(LX + 110, hy + 100), lh=(LX - 20, hy + 120))
            box(c, LX + 120, hy + 80, 120, 200, "#FFFFFF", BLACK, 6, 16)
        tm = tb(j, k_msg)
        if T >= tm:
            with K.at(c, cx - 40, cy - 330, 0, pop_scale(T - tm)):
                bubble_box(c, 0, 0, 400, 130, -1, 1.0, "#F0F0F0")
                K.text(c, "哟，大方案", 0, 0, 56, "hand", INK)
        if T >= td:
            for i in range(3):
                flame(c, LX - 120 + i * 120, hy - 140 - (i % 2) * 30, 0.8 * C.slam_scale(T - td - i * 0.06))
        return None
    ev(j, k_phone, scene, "wood_low", 0.6)
    b.hit(j, k_msg, "pop", 0.75, "阴阳怪气")
    b.hit(j, k_night, "shaker", 0.65, "天黑了")
    b.hit(j, dk, "kick", 0.9, "气了一晚上")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：回放——拍桌子怼回去，气泡越吵越大，最后两人背对背
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_rec = 0
    k_slam = kq(j, wp(3, 1, 0.4), 1)
    k_b = [nx(j, wp(4, 0, 0.3), k_slam)]
    k_b.append(nx(j, wp(4, 0, 0.9), k_b[0]))
    k_back = nx(j, wp(4, 2, 0.4), k_b[-1])
    LX, AX = cx - 320, cx + 320
    L.note("回放", "你懂什么", "你才不懂")

    def rec(c, kk, T):
        g = pop_scale(T - tb(j, k_rec))
        if g <= 0:
            return None
        with K.at(c, cx - 420, cy - 500, 0, g):
            c.drawCircle(-60, 0, 18, K.paint(RED, 0.6 + 0.4 * math.sin(T * 6)))
            K.text(c, "回放", 20, 0, 50, "sans_medium", RED)
        return None
    ev(j, k_rec, rec, "wood_high", 0.6)

    def scene(c, kk, T):
        ts, tbk = tb(j, k_slam), tb(j, k_back)
        g = pop_scale(T - tb(j, 0) - 0.15)
        if g <= 0:
            return None
        back = T >= tbk
        sep = 60 * ease_out(clamp01((T - tbk) / 0.4)) if back else 0
        hy = GY - 290
        with at_pop(c, cx, GY, g):
            meeting(c, cx, GY)
            draw_li(c, LX - sep, GY, 0.95, "flat" if back else "sad", back=back,
                    rh=None if back or T < ts else (LX + 150, GY - 170))
            draw_ace(c, AX + sep, GY, 0.95, mood="cold" if back else "laugh")
        if ts <= T < ts + 0.4:
            K.burst(c, LX + 160, GY - 170, T - ts, ORANGE, 20, 80, 6, 6)
        for i, k_ in enumerate(k_b):
            t0 = tb(j, k_)
            if T < t0 or back:
                continue
            gg = C.slam_scale(T - t0)
            s_ = ("你懂什么", "你才不懂")[i]
            x = (LX + 60) if i == 0 else (AX - 60)
            with K.at(c, x, cy - 260 - i * 60, (i * 2 - 1) * 4, gg * (1 + 0.2 * i)):
                bubble_box(c, 0, 0, 360, 130, -1 if i == 0 else 1)
                K.text(c, s_, 0, 0, 58, "hand", RED)
        if back:
            for i, x in enumerate((LX - sep, AX + sep)):
                flame(c, x, hy - 140, 0.6)
        return None
    b.custom(j, 0, 0.3, scene)
    b.hit(j, k_slam, "kick", 0.85, "拍桌子")
    for k_ in k_b:
        b.hit(j, k_, "rim", 0.75, "你一句我一句")
    b.hit(j, k_back, "tom", 0.8, "背对背不说话")
    b.shots[j].shake = [(k_slam, 8.0)]


screen3()


# ================================================================ 屏 4：竹简“资治通鉴 卷四”；廉颇与蔺相如
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_slip = kq(j, wp(5, 0, 0.3), 0)
    k_two = nx(j, wp(5, 2, 0.4), k_slip)
    k_lian = nx(j, wp(6, 0, 0.6), k_two)
    k_lin = nx(j, wp(6, 1, 0.6), k_lian)
    SX = cx - 330
    L.note("资治通鉴", "卷四", "周纪四", "廉颇", "蔺相如")

    def slips(c, kk, T):
        f = ease_out(clamp01((T - tb(j, k_slip)) / 0.6))
        if f <= 0:
            return None
        bamboo_slips(c, SX, cy - 80, max(60, 340 * f), 760, n=max(1, int(5 * f)))
        a = clamp01((T - tb(j, k_slip) - 0.3) / 0.3)
        slip_text(c, SX + 50, cy - 380, "资治通鉴", 84, "#3A2A12", a)
        slip_text(c, SX - 80, cy - 340, "卷四", 66, RED, a)
        slip_text(c, SX - 80, cy - 140, "周纪四", 50, "#5E4128", a, 1.15)
        return None
    ev(j, k_slip, slips, "muyu", 0.7, 0.6)

    def two(c, kk, T):
        tt = tb(j, k_two)
        if T < tt:
            return None
        for k_, x, col, nm, hat, beard, tc in ((k_lian, cx + 120, LIANPO, "廉颇", "helmet", "white", "#5E5E58"),
                                               (k_lin, cx + 410, LIN, "蔺相如", "guan", "black", "#2C6E68")):
            t0 = tb(j, k_)
            g = pop_scale(T - t0 + (0.3 if k_ == k_lian else 0))
            if g <= 0 or T < tt:
                continue
            with at_pop(c, x, GY, g):
                gu(c, x, GY, 0.85, col, hat=hat, beard=beard, mood="angry" if nm == "廉颇" else "flat")
                name_tag(c, x, GY - 400, nm, tc, 40)
        if T >= tt:
            sparkle(c, cx + 265, cy - 120, T - tt, ORANGE, 8, 40, 90)
        return None
    b.custom(j, k_two, k_two + 0.3, two, sfx="wood_high", gain=0.65)
    b.hit(j, k_lian, "tom", 0.8, "廉颇")
    b.hit(j, k_lin, "tom", 0.75, "蔺相如")


screen4()


# ================================================================ 屏 5：渑池之会——蔺相如在秦王面前一步不让；回国后位次排到廉颇前面
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 80
    k_meet = kq(j, wp(7, 1, 0.3), 0)
    k_firm = nx(j, wp(7, 2, 0.5), k_meet)
    k_face = nx(j, wp(7, 3, 0.5), k_firm)
    k_steps = nx(j, wp(8, 1, 0.3), k_face)
    k_front = nx(j, wp(8, 2, 0.5), k_steps)
    L.note("秦王", "赵王", "蔺相如", "廉颇", "面子")

    def meet(c, kk, T):
        g = pop_scale(T - tb(j, k_meet))
        if g <= 0:
            return None
        tf = tb(j, k_firm)
        with at_pop(c, cx, GY, g):
            gu(c, cx + 380, GY, 0.7, QIN, hat="guan", beard="black", mood="angry" if T >= tf else "smile")
            name_tag(c, cx + 380, GY - 320, "秦王", "#6B3F7A", 34)
            gu(c, cx - 380, GY, 0.7, KING, hat="guan", beard="black")
            name_tag(c, cx - 380, GY - 320, "赵王", "#8A5A1E", 34)
            gu(c, cx - 50, GY, 0.75, LIN, hat="guan", beard="black", mood="angry" if T >= tf else "flat",
               rh=(cx + 90, GY - 220) if T >= tf else None)
        if T >= tb(j, k_face):
            with K.at(c, cx - 50, cy - 450, 0, C.slam_scale(T - tb(j, k_face))):
                chip(c, 0, 0, "保住面子", GREEN_FILL, GREEN, 50)
        return None
    L.note("保住面子")
    b.custom(j, k_meet, k_meet + 0.3, meet, sfx="muyu", gain=0.65)
    b.hit(j, k_firm, "rim", 0.8, "一步不让")
    b.hit(j, k_face, "ding", 0.75, "保住面子")

    def steps(c, kk, T):
        ts, tf = tb(j, k_steps), tb(j, k_front)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        BY = cy + 520
        with at_pop(c, cx, BY, g):
            for q in range(3):
                box(c, cx, BY - q * 50, 900 - q * 200, 50, "#E3D2BE", "#5E4128", 4, 4)
            f = ease_in_out(clamp01((T - tf) / 0.5)) if T >= tf else 0
            lx = lerp(cx + 160, cx - 160, f)
            px = lerp(cx - 160, cx + 160, f)
            gu(c, lx, BY - 150, 0.42, LIN, hat="guan", beard="black")
            gu(c, px, BY - 150, 0.42, LIANPO, hat="helmet", beard="white", mood="angry" if f > 0.5 else "flat")
            if f > 0.5:
                K.text(c, "前", cx - 160, BY - 330, 44, "hand", GREEN, clamp01((f - 0.5) * 3))
        return None
    L.note("前")
    b.custom(j, k_steps, k_steps + 0.3, steps, sfx="wood_low", gain=0.65)
    b.hit(j, k_front, "tom", 0.8, "排到廉颇前面")


screen5()


# ================================================================ 屏 6：廉颇不服——战功 vs 一张嘴；放话“必辱之”
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_lian = 0
    k_war = kq(j, wp(9, 1, 0.4), 1)
    k_mouth = nx(j, wp(9, 2, 0.5), k_war)
    k_shout = nx(j, wp(10, 0, 0.5), k_mouth)
    k_shame = nx(j, wp(10, 2, 0.4), k_shout)
    LX = cx - 330
    L.note("攻城打仗", "一张嘴", "必辱之")

    def lian(c, sc, T):
        tsh = tb(j, k_shout)
        with at_pop(c, LX, GY, sc):
            gu(c, LX, GY, 1.0, LIANPO, hat="helmet", beard="white", mood="angry",
               rh=(LX + 150, GY - 420) if T >= tsh else (LX + 130, GY - 230))
            name_tag(c, LX, GY - 450, "廉颇", "#5E5E58", 44)
        return None
    ev(j, k_lian, L.pop_fn(j, k_lian, lian), "tom", 0.7)

    def items(c, kk, T):
        tw, tm = tb(j, k_war), tb(j, k_mouth)
        if T >= tw:
            with K.at(c, cx + 200, cy - 280, 0, pop_scale(T - tw)):
                box(c, 0, 0, 440, 220, "#FFFFFF", "#7A5E3A", 6, 12)
                for q in range(3):
                    flag(c, -140 + q * 110, 70, 0.32, "赵", "#9C2F25")
                K.text(c, "攻城打仗", 60, -60, 50, "hand", INK)
        if T >= tm:
            with K.at(c, cx + 200, cy + 60, 0, pop_scale(T - tm)):
                box(c, 0, 0, 440, 200, "#FFFFFF", "#7A5E3A", 6, 12)
                m = skia.Path()
                m.addArc(skia.Rect.MakeXYWH(-160, -30, 120, 70), 0, 180)
                m.close()
                c.drawPath(m, K.paint(RED_FILL))
                c.drawPath(m, wb.marker(RED, 6))
                K.text(c, "一张嘴", 80, 0, 50, "hand", INK)
        return None
    b.custom(j, k_war, k_war + 0.3, items, sfx="wood_high", gain=0.65)
    b.hit(j, k_mouth, "pop", 0.7, "一张嘴")
    L.seal_ev(j, k_shame, "必辱之", cx + 220, cy + 380, 64, "kick", 0.85, -6)
    b.hit(j, k_shout, "rim", 0.75, "放话")
    b.shots[j].shake = [(k_shame, 9.0)]


screen6()


# ================================================================ 屏 7：称病不上朝，座位空着；路上两辆车，蔺相如的车拐到一边
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    k_seat = kq(j, wp(11, 1, 0.4), 0)
    k_sick = nx(j, wp(11, 2, 0.5), k_seat)
    k_carts = nx(j, wp(12, 1, 0.4), k_sick)
    k_turn = nx(j, wp(12, 3, 0.3), k_carts)
    L.note("称病", "蔺", "廉")

    def seat(c, kk, T):
        g = pop_scale(T - tb(j, k_seat))
        if g <= 0:
            return None
        with K.at(c, cx - 120, cy - 300, 0, g):
            for q in range(3):
                box(c, -260 + q * 260, 80, 180, 40, "#C98B4B", "#7A4A1E", 5, 6)
                if q != 1:
                    gu(c, -260 + q * 260, 60, 0.45, "gray", hat="guan")
            if T >= tb(j, k_sick):
                with K.at(c, 0, -60, -6, C.slam_scale(T - tb(j, k_sick))):
                    chip(c, 0, 0, "称病", NOTE_FILL, ORANGE, 52)
        return None
    ev(j, k_seat, seat, "muyu", 0.6)
    b.hit(j, k_sick, "wood_high", 0.7, "称病")

    def carts(c, kk, T):
        tc, tt = tb(j, k_carts), tb(j, k_turn)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        RY = cy + 380
        C.line(c, (cx - 560, RY), (cx + 560, RY), "#8B6B43", 6)
        c.drawPath(P((cx - 60, RY), (cx - 160, RY + 200)), wb.marker("#8B6B43", 5))
        f = ease_in_out(clamp01((T - tt) / 0.6)) if T >= tt else 0
        lx = lerp(cx - 380, cx - 220, f)
        ly = RY + 150 * f
        with K.at(c, lx, ly, 20 * f, g * lerp(1, 0.8, f)):
            cart(c, 0, 0, 0.8)
            K.text(c, "蔺", 0, -90, 50, "serif_black", "#2C6E68")
        with K.at(c, cx + 300, RY, 0, g):
            cart(c, 0, 0, 0.8, 1.0, "#9AA3AD")
            K.text(c, "廉", 0, -90, 50, "serif_black", INK)
        return None
    b.custom(j, k_carts, k_carts + 0.3, carts, sfx="wood_low", gain=0.7)
    b.hit(j, k_turn, "shaker", 0.75, "车躲到一边")


screen7()


# ================================================================ 屏 8：门客收拾包袱要走；蔺相如问：廉将军和秦王，谁厉害？
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_ke = kq(j, wp(13, 0, 0.5), 0)
    k_go = nx(j, wp(13, 1, 0.3), k_ke)
    k_ask = nx(j, wp(14, 1, 0.3), k_go)
    k_who = nx(j, wp(14, 2, 0.4), k_ask)
    LX = cx - 360
    L.note("丢脸", "廉将军", "秦王", "谁厉害？")

    def ke(c, kk, T):
        g = pop_scale(T - tb(j, k_ke))
        if g <= 0:
            return None
        tg = tb(j, k_go)
        for i, x0 in enumerate((cx + 160, cx + 380)):
            x, dy, _ = C.walk(T, tg + i * 0.1, 1.0, x0, x0 + 50, 8) if T >= tg else (x0, 0, False)
            with at_pop(c, x, GY + dy, g):
                gu(c, x, GY + dy, 0.7, KE if i else "gray", hat="bun", mood="sad",
                   lh=(x - 40, GY - 200) if T >= tg else None)
                if T >= tg:
                    c.drawCircle(x - 60, GY - 190, 40, K.paint(BLUE_FILL))
                    c.drawCircle(x - 60, GY - 190, 40, wb.marker(BLUE, 5))
        K.text(c, "丢脸", cx + 270, cy - 40, 56, "hand", GRAY, clamp01(g))
        return None
    ev(j, k_ke, ke, "wood_low", 0.6)
    b.hit(j, k_go, "shaker", 0.65, "要走")

    def lin(c, kk, T):
        ta, tw = tb(j, k_ask), tb(j, k_who)
        g = pop_scale(T - tb(j, 0) - 0.2)
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            gu(c, LX, GY, 0.95, LIN, hat="guan", beard="black", rh=(LX + 140, GY - 320) if T >= ta else None)
            name_tag(c, LX, GY - 430, "蔺相如", "#2C6E68", 40)
        if T >= ta:
            ga = pop_scale(T - ta)
            with K.at(c, cx - 30, cy - 330, 0, ga):
                box(c, -170, 0, 230, 110, "#FFFFFF", GRAY, 5, 12)
                K.text(c, "廉将军", -170, 0, 50, "hand", INK)
                K.text(c, "vs", 0, 0, 44, "sans_medium", GRAY)
                box(c, 170, 0, 230, 110, "#FFFFFF", GRAY, 5, 12)
                K.text(c, "秦王", 170, 0, 54, "hand", INK)
        if T >= tw:
            with K.at(c, cx - 30, cy - 170, 0, C.slam_scale(T - tw)):
                K.text(c, "谁厉害？", 0, 0, 72, "hand", RED)
        return None
    b.custom(j, 0, 0.3, lin)
    b.hit(j, k_ask, "pop", 0.7, "蔺相如问")
    b.hit(j, k_who, "rim", 0.8, "谁厉害")


screen8()


# ================================================================ 屏 9：当面顶秦王的回放；两只老虎相斗，秦国在旁边看
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    k_qin = kq(j, wp(15, 0, 0.4), 0)
    k_dare = nx(j, wp(15, 1, 0.4), k_qin)
    k_two = nx(j, wp(16, 1, 0.4), k_dare)
    k_fight = nx(j, wp(16, 2, 0.5), k_two)
    k_dead = nx(j, wp(16, 3, 0.5), k_fight)
    L.note("秦", "赵", "活不成")

    def qin(c, kk, T):
        g = pop_scale(T - tb(j, k_qin))
        if g <= 0:
            return None
        td = tb(j, k_dare)
        with K.at(c, cx - 200, cy - 300, 0, g):
            c.drawCircle(0, 0, 230, K.paint("#FFFFFF", 0.6))
            c.drawCircle(0, 0, 230, wb.marker(GRAY, 5))
            gu(c, -80, 150, 0.5, LIN, hat="guan", beard="black", mood="angry", rh=(40, 0) if T >= td else None)
            gu(c, 90, 150, 0.5, QIN, hat="guan", beard="black", mood="o" if T >= td else "smile",
               head_dx=10 if T >= td else 0)
        return None
    ev(j, k_qin, qin, "wood_high", 0.6)
    b.hit(j, k_dare, "rim", 0.8, "当面顶秦王")

    def tigers(c, kk, T):
        tt, tf, tdd = tb(j, k_two), tb(j, k_fight), tb(j, k_dead)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        Y = cy + 300
        close = 120 * ease_in_out(clamp01((T - tf) / 0.4)) if T >= tf else 0
        for sg, lab in ((-1, "廉"), (1, "蔺")):
            x = cx + sg * (260 - close)
            with K.at(c, x, Y, 0, g):
                body = skia.Rect.MakeXYWH(-120, -60, 240, 120)
                c.drawRoundRect(body, 60, 60, K.paint(NOTE_FILL))
                c.drawRoundRect(body, 60, 60, wb.marker(ORANGE, 6))
                for q in range(3):
                    C.line(c, (-60 + q * 40, -58), (-50 + q * 40, -20), INK, 6)
                c.drawCircle(sg * -130, -50, 60, K.paint(NOTE_FILL))
                c.drawCircle(sg * -130, -50, 60, wb.marker(ORANGE, 6))
                c.drawCircle(sg * -150, -60, 8, K.paint(INK))
                K.text(c, lab, 0, 10, 54, "serif_black", INK)
        if T >= tf:
            K.burst(c, cx, Y - 40, T - tf, RED, 20, 90, 7, 7)
        with K.at(c, cx + 380, cy - 360, 0, g):
            flag(c, 0, 120, 0.5, "秦", "#3D4A63")
        if T >= tdd:
            seal(c, cx, cy + 520, "活不成", 56, -4, C.slam_scale(T - tdd))
        return None
    b.custom(j, k_two, k_two + 0.3, tigers, sfx="tom", gain=0.75)
    b.hit(j, k_fight, "kick", 0.85, "两虎相斗")
    b.hit(j, k_dead, "xiaoluo", 0.8, "总有一只活不成")
    b.shots[j].shake = [(k_fight, 9.0)]


screen9()


# ================================================================ 屏 10：天平——国家急事 vs 私人恩怨，国家那边沉
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_lin = 0
    k_state = kq(j, wp(17, 1, 0.4), 1)
    k_grudge = nx(j, wp(17, 2, 0.5), k_state)
    PX, PY = cx + 120, cy - 120
    LX = cx - 400
    L.note("国家急事", "私人恩怨")

    def lin(c, sc, T):
        with at_pop(c, LX, GY, sc):
            gu(c, LX, GY, 0.9, LIN, hat="guan", beard="black", rh=(LX + 140, GY - 300))
            name_tag(c, LX, GY - 410, "蔺相如", "#2C6E68", 40)
        return None
    ev(j, k_lin, L.pop_fn(j, k_lin, lin), "muyu", 0.6)

    def balance(c, kk, T):
        ts, tg = tb(j, k_state), tb(j, k_grudge)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        tilt = -14 * ease_out(clamp01((T - tg) / 0.5)) if T >= tg else 0
        with at_pop(c, PX, GY, g):
            C.line(c, (PX, GY - 40), (PX, PY), "#7A5E3A", 12)
            box(c, PX, GY - 30, 220, 40, "#C9A97A", "#7A5E3A", 6, 8)
            with K.at(c, PX, PY, tilt):
                C.line(c, (-300, 0), (300, 0), "#7A5E3A", 12)
                for sg, lab, col, show in ((-1, "国家急事", RED, True), (1, "私人恩怨", GRAY, T >= tg)):
                    with K.at(c, sg * 280, 0, -tilt):
                        C.line(c, (0, 0), (-60, 140), GRAY, 4)
                        C.line(c, (0, 0), (60, 140), GRAY, 4)
                        C.line(c, (-90, 140), (90, 140), GRAY, 8)
                        if show:
                            sz = 1.0 if sg < 0 else 0.6
                            box(c, 0, 140 - 60 * sz, 230 * sz, 110 * sz, "#FFFFFF", col, 6, 10)
                            K.text(c, lab, 0, 140 - 60 * sz, 46 * sz, "hand", col)
        return None
    b.custom(j, k_state, k_state + 0.3, balance, sfx="tom", gain=0.75)
    b.hit(j, k_grudge, "rim", 0.8, "私仇放后面")


screen10()


# ================================================================ 屏 11：廉颇光膀子背荆条上门；两人握手，“刎颈之交”
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_ear = kq(j, wp(18, 0, 0.5), 0)
    k_strip = nx(j, wp(18, 1, 0.5), k_ear)
    k_thorn = nx(j, wp(18, 2, 0.5), k_strip)
    k_kneel = nx(j, wp(18, 3, 0.4), k_thorn)
    k_hand = nx(j, wp(19, 1, 0.4), k_kneel)
    LX, RX = cx - 260, cx + 260
    L.note("请罪", "刎颈之交")

    def scene(c, kk, T):
        te, ts, tt, tk, th = tb(j, k_ear), tb(j, k_strip), tb(j, k_thorn), tb(j, k_kneel), tb(j, k_hand)
        g = pop_scale(T - te)
        if g <= 0:
            return None
        kneel = 0.0 if T < tk or T >= th else ease_out(clamp01((T - tk) / 0.3))
        with at_pop(c, LX, GY, g):
            c.save()
            c.translate(LX, GY)
            c.scale(1, 1 - 0.25 * kneel)
            c.translate(-LX, -GY)
            if T < ts:
                gu(c, LX, GY, 0.95, LIANPO, hat="helmet", beard="white", mood="o")
            else:
                hy = GY - 290 * 0.95
                gu(c, LX, GY, 0.95, "brown", hat="bun", beard="white", mood="sad",
                   rh=(LX + 150, hy + 120) if T >= th else None)
                c.drawRect(skia.Rect.MakeXYWH(LX - 40, hy + 50, 80, 90), K.paint("#FBE3CF"))
            if T >= tt:
                for q in range(3):
                    C.line(c, (LX - 90 + q * 20, GY - 300), (LX + 60 + q * 20, GY - 120), "#5E7A2E", 7)
                    for w_ in range(3):
                        px = LX - 70 + q * 20 + w_ * 40
                        py = GY - 280 + w_ * 50
                        C.line(c, (px, py), (px + 14, py - 14), "#5E7A2E", 4)
            c.restore()
            name_tag(c, LX, GY - 430, "廉颇", "#5E5E58", 40)
        with at_pop(c, RX, GY, g):
            gu(c, RX, GY, 0.95, LIN, hat="guan", beard="black", mood="smile" if T >= th else "o",
               lh=(RX - 140, GY - 290 * 0.95 + 120) if T >= th else None)
            name_tag(c, RX, GY - 430, "蔺相如", "#2C6E68", 40)
        if T >= te and T < ts + 0.6:
            with K.at(c, LX - 80, cy - 320, 0, pop_scale(T - te) * (1 - clamp01((T - ts - 0.3) / 0.3))):
                c.drawOval(skia.Rect.MakeXYWH(-50, -70, 100, 140), wb.marker(GRAY, 6))
                K.text(c, "!", 0, 0, 70, "hand", RED)
        if T >= tk:
            with K.at(c, cx, cy - 340, -4, C.slam_scale(T - tk)):
                chip(c, 0, 0, "请罪", RED_FILL, RED, 60)
        if T >= th:
            sparkle(c, cx, GY - 290 * 0.95 + 120, T - th, YELLOW, 10, 50, 120)
            with K.at(c, cx, cy - 180, 0, C.slam_scale(T - th)):
                K.text(c, "刎颈之交", 0, 0, 80, "serif_black", RED)
        return None
    L.note("!")
    b.custom(j, k_ear, k_ear + 0.3, scene, sfx="pop", gain=0.6)
    b.hit(j, k_strip, "wood_high", 0.7, "脱了上衣")
    b.hit(j, k_thorn, "shaker", 0.7, "背上荆条")
    b.hit(j, k_kneel, "tom", 0.8, "上门请罪")
    b.hit(j, k_hand, "bianzhong", 0.85, "生死之交")


screen11()


# ================================================================ 屏 12：说回我们：小李摸摸发烫的脸；倒带按钮，那场会重来一遍
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_ok = kq(j, wp(20, 1, 0.5), 1)
    k_rew = nx(j, wp(21, 1, 0.4), k_ok)
    k_again = nx(j, wp(21, 2, 0.4), k_rew)
    LX = cx - 300
    L.note("重来一遍")

    def li(c, sc, T):
        to = tb(j, k_ok)
        hy = GY - 290
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 1.0, "sad" if T < to else "flat", rh=(LX + 40, hy + 10), lh=(LX - 40, hy + 10))
            a = 0.5 if T < to else lerp(0.5, 0.15, clamp01((T - to) / 0.6))
            for sg in (-1, 1):
                c.drawOval(skia.Rect.MakeXYWH(LX + sg * 24 - 14, hy + 4, 28, 16), K.paint(RED, a))
        return None
    ev(j, k_li, L.pop_fn(j, k_li, li), "wood_low", 0.6)
    b.hit(j, k_ok, "pop", 0.6, "难受很正常")

    def rew(c, kk, T):
        tr = tb(j, k_rew)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        with K.at(c, cx + 230, cy - 160, 0, g):
            c.drawCircle(0, 0, 170, K.paint("#FFFFFF"))
            c.drawCircle(0, 0, 170, wb.marker(BLACK, 8))
            for dx in (-60, 20):
                c.drawPath(P((dx + 60, -60), (dx, 0), (dx + 60, 60), close=True), K.paint(BLUE))
            a = -(T - tr) * 400
            ar = skia.Path()
            ar.addArc(skia.Rect.MakeXYWH(-210, -210, 420, 420), a, 250)
            c.drawPath(ar, wb.marker(GRAY, 6))
        return None
    ev(j, k_rew, rew, "shaker", 0.75)
    L.stamp_ev(j, k_again, "重来一遍", cx + 230, cy + 260, 84, -6, "kick", 0.9)
    b.shots[j].shake = [(k_again, 8.0)]


screen12()


# ================================================================ 屏 13：第一步：会上平静地说“会后细聊”，火苗熄掉
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 0)
    GY = cy + 520
    k_fire = kq(j, wp(22, 0, 0.6), 1)
    k_say = nx(j, wp(22, 2, 0.3), k_fire)
    k_out = nx(j, wp(22, 3, 0.4), k_say)
    LX, AX = cx - 330, cx + 330
    L.note("会后细聊")

    def scene(c, sc, T):
        tf, ts, to = tb(j, k_fire), tb(j, k_say), tb(j, k_out)
        with at_pop(c, cx, GY, sc):
            meeting(c, cx, GY)
            draw_li(c, LX, GY, 0.95, "smile" if T >= to else "flat", rh=(LX + 130, GY - 260) if T >= ts else None)
            draw_ace(c, AX, GY, 0.95, mood="flat" if T >= to else "smug")
        f = 1.0 if T < to else 1 - ease_out(clamp01((T - to) / 0.4))
        if T >= tf and f > 0:
            flame(c, cx, cy - 20, 1.3 * f * C.slam_scale(T - tf))
        if T >= to:
            for q in range(3):
                yy = cy - 60 - (T - to) * 120 - q * 40
                c.drawCircle(cx + 20 * math.sin(T * 3 + q), yy, 18 + q * 6, K.paint(GRAY, 0.3 * (1 - clamp01((T - to) / 1.5))))
        if T >= ts:
            with K.at(c, LX + 140, cy - 280, 0, pop_scale(T - ts)):
                bubble_box(c, 0, 0, 380, 130, -1)
                K.text(c, "会后细聊", 0, 0, 60, "hand", GREEN)
        return None
    ev(j, k_fire, L.pop_fn(j, k_fire, scene), "rim", 0.7)
    b.hit(j, k_say, "pop", 0.75, "会后细聊")
    b.hit(j, k_out, "ding", 0.8, "火苗熄掉")


screen13()


# ================================================================ 屏 14：第二步：会后单独坐下，“你担心什么？”，事和人分成两栏
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 1)
    GY = cy + 520
    k_sit = kq(j, wp(23, 0, 0.6), 1)
    k_ask = nx(j, wp(23, 1, 0.5), k_sit)
    k_cols = nx(j, wp(23, 2, 0.4), k_ask)
    L.note("你担心什么？", "事", "人")

    def scene(c, sc, T):
        ta = tb(j, k_ask)
        with at_pop(c, cx, GY, sc):
            box(c, cx, GY - 150, 420, 40, "#E7D6BA", "#8B6B43", 6, 8)
            c.drawCircle(cx - 40, GY - 190, 26, K.paint("#FFFFFF"))
            c.drawCircle(cx - 40, GY - 190, 26, wb.marker(BROWN_LINE, 5))
            c.drawCircle(cx + 40, GY - 190, 26, K.paint("#FFFFFF"))
            c.drawCircle(cx + 40, GY - 190, 26, wb.marker(BROWN_LINE, 5))
            draw_li(c, cx - 330, GY, 0.9, "flat", rh=(cx - 200, GY - 250) if T >= ta else None)
            draw_ace(c, cx + 330, GY, 0.9, mood="flat")
        if T >= ta:
            with K.at(c, cx - 200, cy - 80, 0, pop_scale(T - ta)):
                bubble_box(c, 0, 0, 420, 130, -1)
                K.text(c, "你担心什么？", 0, 0, 56, "hand", INK)
        return None
    ev(j, k_sit, L.pop_fn(j, k_sit, scene), "wood_low", 0.6)
    b.hit(j, k_ask, "pop", 0.75, "先问他担心什么")

    def cols(c, kk, T):
        tc = tb(j, k_cols)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx + 120, cy - 330, 0, g):
            for i, (lab, col, fill) in enumerate((("事", BLUE, BLUE_FILL), ("人", GREEN, GREEN_FILL))):
                x = -150 + i * 300
                box(c, x, 0, 260, 180, fill, col, 6, 14)
                K.text(c, lab, x, 0, 100, "serif_black", col)
            C.line(c, (0, -110), (0, 110), GRAY, 6)
        return None
    ev(j, k_cols, cols, "rim", 0.8)


BROWN_LINE = "#8B6B43"
screen14()


# ================================================================ 屏 15：第三步：两人中间一面共同的目标旗，并排看向它
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 2)
    GY = cy + 520
    k_flag = kq(j, wp(24, 1, 0.5), 1)
    k_turn = nx(j, wp(24, 3, 0.4), k_flag)
    L.note("项目上线", "共同目标")

    def scene(c, kk, T):
        tf, tt = tb(j, k_flag), tb(j, k_turn)
        g = pop_scale(T - tb(j, 0) - 0.2)
        if g <= 0:
            return None
        close = 120 * ease_out(clamp01((T - tt) / 0.5)) if T >= tt else 0
        with at_pop(c, cx, GY, g):
            draw_li(c, cx - 380 + close, GY, 0.9, "smile" if T >= tt else "flat")
            draw_ace(c, cx + 380 - close, GY, 0.9, mood="smug" if T >= tt else "flat")
        if T >= tf:
            gf = C.slam_scale(T - tf)
            with K.at(c, cx, cy - 100, 0, gf):
                C.line(c, (0, 420), (0, -220), "#7A4A1E", 10)
                p = P((0, -220), (260, -200 + 10 * math.sin(T * 4)), (250, -60), (0, -80), close=True)
                c.drawPath(p, K.paint(RED))
                c.drawPath(p, wb.marker(INK, 5))
                K.text(c, "项目上线", 125, -140, 48, "hand", "#FFFFFF")
            K.text(c, "共同目标", cx, cy + 360, 56, "hand", RED, clamp01((T - tf - 0.3) / 0.2))
        if T >= tt:
            sparkle(c, cx + 120, cy - 240, T - tt, YELLOW, 10, 60, 140)
        return None
    b.custom(j, 0, 0.3, scene, sfx="wood_low", gain=0.6)
    b.hit(j, k_flag, "kick", 0.85, "目标旗立起来")
    b.hit(j, k_turn, "ding", 0.8, "并排看向它")


screen15()


# ================================================================ 屏 16：好处：面子没丢、事办成，两人一起举杯（咖啡）
def screen16(j=16):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_face = kq(j, wp(25, 0, 0.6), 1)
    k_done = nx(j, wp(25, 1, 0.5), k_face)
    k_cheer = nx(j, wp(25, 3, 0.3), k_done)
    L.note("面子", "办成了")

    def scene(c, kk, T):
        tfc, td, tc = tb(j, k_face), tb(j, k_done), tb(j, k_cheer)
        g = pop_scale(T - tb(j, 0) - 0.2)
        if g <= 0:
            return None
        lift = 60 * ease_out(clamp01((T - tc) / 0.3)) if T >= tc else 0
        with at_pop(c, cx, GY, g):
            hy = GY - 290 * 0.95
            draw_li(c, cx - 200, GY, 0.95, "smile", rh=(cx - 70, hy + 80 - lift))
            draw_ace(c, cx + 200, GY, 0.95, mood="laugh" if T >= tc else "smug", lh=(cx + 70, hy + 80 - lift))
            for sg in (-1, 1):
                box(c, cx + sg * 55, hy + 50 - lift, 60, 80, "#FFFFFF", "#8B6B43", 5, 8)
        if T >= tfc:
            with K.at(c, cx - 300, cy - 330, -5, pop_scale(T - tfc)):
                chip(c, 0, 0, "面子", GREEN_FILL, GREEN, 56)
                c.drawPath(check(110, 0, 30), wb.marker(GREEN, 9))
        if T >= td:
            with K.at(c, cx + 260, cy - 330, 5, pop_scale(T - td)):
                chip(c, 0, 0, "办成了", BLUE_FILL, BLUE, 56)
        if T >= tc:
            sparkle(c, cx, hy + 20 - lift, T - tc, YELLOW, 12, 50, 130)
        return None
    b.custom(j, 0, 0.3, scene, sfx="wood_low", gain=0.6)
    b.hit(j, k_face, "pop", 0.7, "面子没丢")
    b.hit(j, k_done, "pop", 0.7, "事办成了")
    b.hit(j, k_cheer, "ding", 0.85, "碰杯")


screen16()


# ================================================================ 屏 17：评论区；小李把火苗压进杯子，心里一面大旗；下一讲预告
def screen17(j=17):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z_))
    k_cmt = 0
    k_chips = nx(j, wp(27, 0, 0.3), 0)
    k_press = nx(j, wp(28, 0, 0.5), k_chips)
    k_big = nx(j, wp(28, 1, 0.5), k_press)
    k_next = nx(j, wp(29, 1, 0.2), k_big)
    b.move(j, k_press, (cx, cy + 380, Z_), 1.1)
    CH = ["当场怼回去", "笑一笑过去了", "会后去找他"]
    L.note("你是怎么收场的？", *CH, "下一讲", "规矩定了一大堆", "为什么没人守？", "大事")
    BY = cy - 330

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 20, BY, 0, sc):
            bubble_box(c, 0, 0, 1000, 360, -1)
            K.text(c, "你是怎么收场的？", 0, -110, 60, "hand", RED)
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
    LX, LY = cx - 250, cy + 640

    def li(c, kk, T):
        tp, tbg = tb(j, k_press), tb(j, k_big)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        hy = LY - 290 * 0.95
        f = ease_in_out(clamp01((T - tp - 0.2) / 0.5))
        with at_pop(c, LX, LY, g):
            draw_li(c, LX, LY, 0.95, "smile" if T >= tbg else "flat", rh=(LX + 150, hy + 60))
            box(c, LX + 180, hy + 120, 90, 110, "#FFFFFF", "#8B6B43", 5, 8)
            flame(c, LX + 180, lerp(hy - 20, hy + 100, f), lerp(0.8, 0.2, f), 1 - f * 0.8)
        if T >= tbg:
            gb = C.slam_scale(T - tbg)
            with K.at(c, cx + 250, cy + 420, 0, gb):
                C.line(c, (0, 200), (0, -160), "#7A4A1E", 10)
                p = P((0, -160), (220, -140), (210, -20), (0, -40), close=True)
                c.drawPath(p, K.paint(RED))
                c.drawPath(p, wb.marker(INK, 5))
                K.text(c, "大事", 105, -90, 56, "hand", "#FFFFFF")
            sparkle(c, cx + 300, cy + 300, T - tbg, YELLOW, 10, 60, 140)
        return None
    ev(j, k_press, li, "wood_low", 0.6)
    b.hit(j, k_big, "ding", 0.8, "心里装着大事")

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
            K.text(c, "规矩定了一大堆", -80, -60, 58, "hand", BLACK)
            K.text(c, "为什么没人守？", -60, 40, 58, "hand", BLACK)
            for q in range(4):
                box(c, 390 + q * 6, 40 - q * 26, 150, 30, "#FFFFFF", GRAY, 4, 4)
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen17()

# ================================================================ 收尾
L.finish(cover_shot=11, square_shot=10, notes=NOTES)
L.export(globals())
