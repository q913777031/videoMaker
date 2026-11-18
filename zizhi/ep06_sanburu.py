"""《资治通鉴》06 三不如：手下的人比你强，怎么带？（白板手绘 + AI 旁白，竖屏 2:3）

经典问答：刘邦在洛阳南宫摆酒发问（我为什么得天下、项羽为什么失天下）→ 高起、王陵答“有功就分”→ 刘邦“只说对了一半”，
三个“吾不如”（张良、萧何、韩信）各占一屏 → “三者皆人杰，吾能用之”，项羽有范增不能用 → 群臣服气。
今人部分：小组长小李带比自己强的同事，三步（写下别人强在哪、把事交给合适的人、功劳分出去）。本讲是藏青蓝图底（深色）。
文案见 zizhi/PLAN.md「### 06」。
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
                          at_pop, bamboo_slips, box, bubble_box, city_wall, cup, desk, draw_ace, draw_li, draw_wang, flag, gu,
                          head_of, pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "通鉴里的故事", 4),
    ([6, 7], "大臣答", 5),
    ([8], "只对一半", 6),
    ([9], "我不如张良", 7),
    ([10], "我不如萧何", 8),
    ([11], "我不如韩信", 9),
    ([12, 13], "能用", 10),
    ([14], "群臣服气", 11),
    ([15, 16], "说回我们自己", 12),
    ([17], "第一步", 13),
    ([18], "第二步", 14),
    ([19], "第三步", 15),
    ([20], "好处", 16),
    ([21, 22, 23, 24], "评论区见", 17),
]

THEME = ZT.get("06")
L = Z.Lesson("06", SCREENS, drop_screen=2, board_size=(5000, 12000), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(16)]
Z_ = 0.72

NOTES = [
    "出处：司马光《资治通鉴》卷十一 汉纪三（高帝五年）洛阳南宫置酒。",
    "原文：“吾所以有天下者何？项氏之所以失天下者何？”高起、王陵对“陛下使人攻城略地，因以与之，与天下同其利；项羽不然，"
    "有功者害之，贤者疑之”；上曰“公知其一，未知其二。夫运筹帷幄之中，决胜千里之外，吾不如子房；填国家，抚百姓，给饷馈，"
    "不绝粮道，吾不如萧何；连百万之众，战必胜，攻必取，吾不如韩信。三者皆人杰，吾能用之，此吾所以取天下者也。"
    "项羽有一范增而不能用，此所以为我禽也。”群臣说服。",
    "今人（小李、小王、同事）为虚构示意；古人造型为示意。",
]

LIU, GAO, WANG_L, XIANG, ZL, XH, HX, FZ = "red", "gray", "brown", "purple", "teal", "ochre", "blue", "gray"
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
        c.drawRoundRect(r, 18, 18, K.paint(PARCH, 0.1 * a))
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


def boxes_stack(c, x, y, n, a=1.0):
    for i in range(n):
        c.drawPath(C.box_path(x + (i % 2) * 10 - 5, y - i * 70, 190, 70), K.paint("#E7C99A", a))
        c.drawPath(C.box_path(x + (i % 2) * 10 - 5, y - i * 70, 190, 70), wb.marker("#8B6B43", 5, a))


def badge(c, x, y, s, a=1.0):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 44 * s, y - 20 * s, 88 * s, 40 * s), 6, 6, K.paint(RED_FILL, a))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 44 * s, y - 20 * s, 88 * s, 40 * s), 6, 6, wb.marker(RED, 3, a))
    K.text(c, "组长", x, y + 1, 28 * s, "sans_medium", RED, a)


def bow_figure(c, x, y, s, col, label, tc, mood="smile", beard="black", hat="guan"):
    gu(c, x, y, s, col, hat=hat, beard=beard, mood=mood, bow=True)
    name_tag(c, x, y - 380 * s - 40, label, tc, 36)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：组长小李和两个强同事（懂技术 / 会沟通），小李冒汗
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = kq(j, wp(0, 1, 0.4), 0)
    k_tech = nx(j, wp(0, 2, 0.5), k_li)
    k_talk = nx(j, wp(0, 3, 0.5), k_tech)
    k_sweat = nx(j, wp(1, 0, 0.6), k_talk)
    k_small = nx(j, wp(1, 1, 0.5), k_sweat)
    LX, AX, WX = cx - 60, cx - 380, cx + 330
    L.note("懂技术", "会沟通")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_li))
        if g <= 0:
            return None
        tsm = tb(j, k_small)
        s = 0.95 if T < tsm else lerp(0.95, 0.78, ease_out(clamp01((T - tsm) / 0.4)))
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, s, "sad" if T >= tb(j, k_sweat) else "flat")
            badge(c, LX, GY - 290 * s + 140 * s, s)
        if T >= tb(j, k_sweat):
            hy = GY - 290 * s
            for q in range(2):
                f = ((T - tb(j, k_sweat)) * 1.2 + q * 0.5) % 1
                c.drawCircle(LX + 60 + q * 20, hy - 30 + 60 * f, 10, K.paint(BLUE, 1 - f))
        for k_, x, who, lab in ((k_tech, AX, "ace", "懂技术"), (k_talk, WX, "wang", "会沟通")):
            t0 = tb(j, k_)
            gi = pop_scale(T - t0)
            if gi <= 0:
                continue
            with at_pop(c, x, GY, gi):
                if who == "ace":
                    draw_ace(c, x, GY, 1.0, mood="smug")
                else:
                    draw_wang(c, x, GY, 1.0, mood="smile")
            with K.at(c, x, cy - 300, 0, gi):
                chip(c, 0, 0, lab, NOTE_FILL, ORANGE, 52)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_tech, "pop", 0.7, "懂技术")
    b.hit(j, k_talk, "pop", 0.7, "会沟通")
    b.hit(j, k_sweat, "wood_high", 0.6, "心里发虚")
    b.hit(j, k_small, "tom", 0.75, "怕被比下去")


screen1()


# ================================================================ 屏 2（drop）：小李一个人扛一摞箱子，越压越低
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_li = 0
    k_b = [kq(j, wp(2, 1, 0.3), 1)]
    k_b.append(max(k_b[0] + 1, min(dk - 1, kq(j, wp(2, 2, 0.3), k_b[0] + 1))))
    LX = cx - 60
    L.note("累")

    def scene(c, sc, T):
        n = 1 + sum(1 for k_ in k_b if T >= tb(j, k_)) * 2 + (2 if T >= tb(j, dk) else 0)
        sq = 1.0 - 0.05 * (n - 1)
        hy = GY - 290 * sq
        with at_pop(c, LX, GY, sc):
            C.draw_li(c, LX, GY, 1.0, "sad", squash=sq, lh=(LX - 80, GY - 330 * sq), rh=(LX + 80, GY - 330 * sq))
            boxes_stack(c, LX, GY - 330 * sq, n)
        if T >= tb(j, dk):
            K.text(c, "累", LX + 330, cy, 110, "hand", RED, clamp01((T - tb(j, dk)) / 0.2))
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    for k_ in k_b:
        b.hit(j, k_, "wood_high", 0.75, "又压上两箱")
    b.hit(j, dk, "kick", 0.9, "越忙越累")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：能人同事闲着转笔，小李不敢开口
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_ace = kq(j, wp(3, 0, 0.5), 0)
    k_mute = nx(j, wp(3, 1, 0.5), k_ace)
    k_q = nx(j, wp(3, 2, 0.5), k_mute)
    L.note("……", "怎么用？")
    AX, LX = cx + 260, cx - 330

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_ace))
        if g <= 0:
            return None
        with at_pop(c, AX, GY, g):
            desk(c, AX - 80, GY - 170, 320)
            hy = GY - 290
            draw_ace(c, AX + 100, GY, 0.95, mood="flat", rh=(AX + 10, hy + 90))
            a = math.radians((T - tb(j, k_ace)) * 500)
            C.line(c, (AX + 10 - 40 * math.cos(a), hy + 90 - 40 * math.sin(a)),
                   (AX + 10 + 40 * math.cos(a), hy + 90 + 40 * math.sin(a)), ORANGE, 6)
        tm = tb(j, k_mute)
        with at_pop(c, LX, GY, pop_scale(T - tm + 0.3)):
            draw_li(c, LX, GY, 0.95, "sad", rh=(LX + 60, GY - 290 * 0.95 + 30) if T >= tm else None)
            badge(c, LX, GY - 290 * 0.95 + 140 * 0.95, 0.95)
        if T >= tm:
            with K.at(c, LX + 60, cy - 120, 0, pop_scale(T - tm)):
                bubble_box(c, 0, 0, 200, 100, -1)
                K.text(c, "……", 0, -6, 56, "hand", GRAY)
        if T >= tb(j, k_q):
            with K.at(c, cx, cy - 360, 0, C.slam_scale(T - tb(j, k_q))):
                K.text(c, "怎么用？", 0, 0, 88, "hand", RED)
        return None
    ev(j, k_ace, scene, "wood_low", 0.6)
    b.hit(j, k_mute, "pop", 0.65, "不敢开口")
    b.hit(j, k_q, "rim", 0.8, "不知道怎么用")


screen3()


# ================================================================ 屏 4：竹简“资治通鉴 卷十一”；南宫摆酒，刘邦举杯发问
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_slip = kq(j, wp(4, 0, 0.3), 0)
    k_liu = nx(j, wp(4, 1, 0.4), k_slip)
    k_q1 = nx(j, wp(5, 1, 0.5), k_liu)
    k_q2 = nx(j, wp(5, 2, 0.5), k_q1)
    SX = cx - 360
    L.note("资治通鉴", "卷十一", "汉纪三", "刘邦", "南宫", "得天下？", "丢天下？")

    def slips(c, kk, T):
        f = ease_out(clamp01((T - tb(j, k_slip)) / 0.6))
        if f <= 0:
            return None
        bamboo_slips(c, SX, cy - 150, max(60, 300 * f), 640, n=max(1, int(4 * f)))
        a = clamp01((T - tb(j, k_slip) - 0.3) / 0.3)
        slip_text(c, SX + 40, cy - 410, "资治通鉴", 76, "#3A2A12", a)
        slip_text(c, SX - 70, cy - 380, "卷十一", 54, RED, a)
        slip_text(c, SX - 70, cy - 170, "汉纪三", 44, "#5E4128", a, 1.15)
        return None
    ev(j, k_slip, slips, "muyu", 0.7, 0.6)

    def liu(c, kk, T):
        tl = tb(j, k_liu)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        x = cx + 230
        with at_pop(c, x, GY, g):
            box(c, x, GY - 140, 440, 40, "#C98B4B", "#7A4A1E", 5, 8)
            for q in range(3):
                cup(c, x - 140 + q * 140, GY - 160, 0.8)
            gu(c, x, GY - 60, 0.9, LIU, hat="guan", beard="black", mood="smile",
               rh=(x + 140, GY - 400) if T >= tb(j, k_q1) else None)
            name_tag(c, x, GY - 460, "刘邦", "#9C2F25", 40)
            name_tag(c, x - 180, GY - 40, "南宫", "#7A4A1E", 34)
        for i, (k_, s_, y) in enumerate(((k_q1, "得天下？", cy - 420), (k_q2, "丢天下？", cy - 280))):
            t0 = tb(j, k_)
            if T >= t0:
                with K.at(c, cx + 300, y, (i * 2 - 1) * 3, C.slam_scale(T - t0)):
                    chip(c, 0, 0, s_, NOTE_FILL if i == 0 else RED_FILL, ORANGE if i == 0 else RED, 54)
        return None
    b.custom(j, k_liu, k_liu + 0.3, liu, sfx="tom", gain=0.75)
    b.hit(j, k_q1, "rim", 0.75, "我为什么得天下")
    b.hit(j, k_q2, "rim", 0.75, "项羽为什么丢天下")


screen4()


# ================================================================ 屏 5：大臣答——城池分给有功的人 / 项羽：有功被害、有本事被猜疑
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_two = kq(j, wp(6, 0, 0.5), 0)
    k_share = nx(j, wp(6, 2, 0.5), k_two)
    k_xiang = nx(j, wp(7, 0, 0.6), k_share)
    k_harm = nx(j, wp(7, 1, 0.5), k_xiang)
    k_doubt = nx(j, wp(7, 2, 0.5), k_harm)
    L.note("高起", "王陵", "项羽", "有功", "有本事")

    def two(c, kk, T):
        g = pop_scale(T - tb(j, k_two))
        if g <= 0:
            return None
        for i, (x, col, nm) in enumerate(((cx - 440, GAO, "高起"), (cx - 270, WANG_L, "王陵"))):
            with at_pop(c, x, GY, g):
                bow_figure(c, x, GY, 0.7, col, nm, "#5E5E58")
        ts = tb(j, k_share)
        if T >= ts:
            with K.at(c, cx - 330, cy - 250, 0, pop_scale(T - ts)):
                city_wall(c, 0, 0, 220, 130)
                for q in range(3):
                    f = ease_out(clamp01((T - ts - q * 0.1) / 0.4))
                    c.drawOval(skia.Rect.MakeXYWH(-30 + (q - 1) * 120 * f, 40 + 120 * f, 60, 26), K.paint(YELLOW))
                K.text(c, "分给有功的人", 0, 230, 44, "hand", GREEN)
        return None
    L.note("分给有功的人")
    b.custom(j, k_two, k_two + 0.3, two, sfx="wood_low", gain=0.65)
    b.hit(j, k_share, "ding", 0.75, "城池分给有功的人")

    def xiang(c, kk, T):
        tx = tb(j, k_xiang)
        g = pop_scale(T - tx)
        if g <= 0:
            return None
        XX = cx + 280
        C.line(c, (cx + 20, cy - 450), (cx + 20, cy + 540), GRAY, 4)
        with at_pop(c, XX, GY, g):
            gu(c, XX, GY, 0.85, XIANG, hat="helmet", beard="black", mood="angry")
            name_tag(c, XX, GY - 420, "项羽", "#6B3F7A", 40)
        for i, (k_, s_) in enumerate(((k_harm, "有功"), (k_doubt, "有本事"))):
            t0 = tb(j, k_)
            if T < t0:
                continue
            with K.at(c, cx + 300, cy - 360 + i * 190, 0, pop_scale(T - t0)):
                chip(c, 0, 0, s_, GREEN_FILL, GREEN, 48)
                f = ease_out(clamp01((T - t0 - 0.2) / 0.25))
                c.drawPath(wb.partial(cross(0, 0, 70), f)[0], wb.marker(RED, 12))
        return None
    b.custom(j, k_xiang, k_xiang + 0.3, xiang, sfx="tom", gain=0.75)
    b.hit(j, k_harm, "rim", 0.8, "有功就害")
    b.hit(j, k_doubt, "rim", 0.8, "有本事就猜疑")


screen5()


# ================================================================ 屏 6：刘邦伸出手，一个圆被切掉一半——“只对一半”
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_liu = 0
    k_half = kq(j, wp(8, 1, 0.5), 1)
    LX = cx - 300
    L.note("一半")

    def scene(c, sc, T):
        th = tb(j, k_half)
        with at_pop(c, LX, GY, sc):
            gu(c, LX, GY, 1.0, LIU, hat="guan", beard="black", mood="smile", rh=(LX + 160, GY - 360))
            name_tag(c, LX, GY - 450, "刘邦", "#9C2F25", 44)
        x, y = cx + 240, cy - 120
        f = ease_out(clamp01((T - th) / 0.5)) if T >= th else 0
        with K.at(c, x, y, 0, sc):
            c.save()
            c.translate(-40 * f, 0)
            c.clipRect(skia.Rect.MakeLTRB(-260, -260, 0, 260))
            c.drawCircle(0, 0, 220, K.paint(NOTE_FILL))
            c.drawCircle(0, 0, 220, wb.marker(ORANGE, 8))
            c.restore()
            c.save()
            c.translate(60 * f, 40 * f)
            c.rotate(18 * f)
            c.clipRect(skia.Rect.MakeLTRB(0, -260, 260, 260))
            c.drawCircle(0, 0, 220, K.paint(GRAY_FILL, 1 - 0.5 * f))
            c.drawCircle(0, 0, 220, wb.marker(GRAY, 8, 1 - 0.5 * f))
            c.restore()
        if T >= th:
            with K.at(c, x - 40, y + 330, 0, C.slam_scale(T - th)):
                K.text(c, "一半", 0, 0, 110, "hand", RED)
        return None
    ev(j, k_liu, L.pop_fn(j, k_liu, scene), "muyu", 0.6)
    b.hit(j, k_half, "kick", 0.85, "只说对一半")
    b.shots[j].shake = [(k_half, 8.0)]


GRAY_FILL = "#D9DCE1"
screen6()


def buru(j, name, col, tc, k_name):
    """“我不如 X”印章 + X 的名牌，在第 k_name 拍砸下。"""
    cx, cy = R[j]
    L.stamp_ev(j, k_name, f"我不如{name}", cx, cy - 430, 80, -4, "kick", 0.9, RED)
    b.shots[j].shake = [(k_name, 9.0)]


# ================================================================ 屏 7：帐篷里张良在地图前出主意，千里外一面旗子倒向汉军
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_tent = kq(j, wp(9, 0, 0.4), 0)
    k_win = nx(j, wp(9, 1, 0.6), k_tent)
    k_name = nx(j, wp(9, 2, 0.5), k_win)
    TX = cx - 220
    L.note("张良", "千里之外", "汉")

    def tent(c, kk, T):
        g = pop_scale(T - tb(j, k_tent))
        if g <= 0:
            return None
        with at_pop(c, TX, GY, g):
            tp = P((TX - 330, GY), (TX, GY - 600), (TX + 330, GY), close=True)
            c.drawPath(tp, K.paint("#E6D6EE", 0.6))
            c.drawPath(tp, wb.marker("#6B3F7A", 7))
            box(c, TX + 70, GY - 170, 280, 160, "#F0DDB8", "#7A4A1E", 5, 8)
            for q in range(3):
                c.drawCircle(TX + 10 + q * 60, GY - 190 + (q % 2) * 30, 12, K.paint(RED if q % 2 else BLUE))
            gu(c, TX - 140, GY, 0.75, ZL, hat="guan", mood="smile", rh=(TX + 20, GY - 220))
            name_tag(c, TX - 140, GY - 340, "张良", "#2C6E68", 38)
        return None
    ev(j, k_tent, tent, "muyu", 0.65)

    def far(c, kk, T):
        tw = tb(j, k_win)
        g = pop_scale(T - tb(j, k_tent) - 0.3)
        if g <= 0:
            return None
        x, y = cx + 340, cy - 50
        p = wb.arrow((TX + 220, GY - 300), (x - 60, y + 80), 0.3, 30)
        dash = wb.marker(ORANGE, 6, clamp01(g))
        dash.setPathEffect(skia.DashPathEffect.Make([20, 14], 0))
        c.drawPath(p, dash)
        K.text(c, "千里之外", x, y - 330, 48, "hand", ORANGE, clamp01(g))
        f = ease_out(clamp01((T - tw) / 0.4)) if T >= tw else 0
        with K.at(c, x, y + 120, 0, 1):
            flag(c, 0, 0, 0.6, "楚" if f < 0.5 else "汉", "#6B3F7A" if f < 0.5 else "#9C2F25", 1.0, math.sin(T * 3))
        if T >= tw:
            sparkle(c, x + 40, y - 120, T - tw, YELLOW, 10, 60, 140)
        return None
    L.note("楚")
    b.custom(j, k_tent, k_tent + 0.3, far)
    b.hit(j, k_win, "tom", 0.8, "千里之外打赢")
    buru(j, "张良", ZL, "#2C6E68", k_name)


screen7()


# ================================================================ 屏 8：萧何管账本，粮车一路不断
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_xiao = kq(j, wp(10, 0, 0.4), 0)
    k_carts = nx(j, wp(10, 1, 0.4), k_xiao)
    k_name = nx(j, wp(10, 2, 0.5), k_carts)
    XX = cx - 330
    L.note("萧何", "粮")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_xiao))
        if g <= 0:
            return None
        with at_pop(c, XX, GY, g):
            box(c, XX + 150, GY - 160, 240, 40, "#C98B4B", "#7A4A1E", 5, 8)
            bamboo_slips(c, XX + 150, GY - 220, 200, 70, n=4)
            gu(c, XX, GY, 0.9, XH, hat="guan", beard="black", rh=(XX + 110, GY - 220))
            name_tag(c, XX, GY - 410, "萧何", "#8A5A1E", 40)
        tc = tb(j, k_carts)
        if T >= tc:
            RY = cy - 80
            C.line(c, (cx - 560, RY + 40), (cx + 560, RY + 40), "#8B6B43", 6)
            for q in range(4):
                x = cx - 600 + ((T - tc) * 160 + q * 300) % 1200
                with K.at(c, x, RY, 0, 1):
                    box(c, 0, -40, 160, 70, "#C98B4B", "#7A4A1E", 5, 8)
                    K.text(c, "粮", 0, -40, 40, "serif_black", "#FFFFFF")
                    for wx in (-50, 50):
                        c.drawCircle(wx, 10, 26, K.paint("#FFFFFF"))
                        c.drawCircle(wx, 10, 26, wb.marker("#7A4A1E", 4))
        return None
    ev(j, k_xiao, scene, "muyu", 0.65)
    b.hit(j, k_carts, "shaker", 0.75, "粮车一路不断")
    buru(j, "萧何", XH, "#8A5A1E", k_name)


screen8()


# ================================================================ 屏 9：韩信带兵，城门一座座打开
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_han = kq(j, wp(11, 0, 0.4), 0)
    k_w = nx(j, wp(11, 1, 0.5), k_han)
    k_name = nx(j, wp(11, 2, 0.5), k_w)
    HXX = cx - 380
    L.note("韩信")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_han))
        if g <= 0:
            return None
        with at_pop(c, HXX, GY, g):
            gu(c, HXX, GY, 0.9, HX, hat="helmet", beard="black", mood="smile", rh=(HXX + 150, GY - 380))
            name_tag(c, HXX, GY - 440, "韩信", "#2F5B8E", 40)
            for r_ in range(2):
                for q in range(4):
                    gu(c, HXX + 160 + q * 70, GY - r_ * 60, 0.3, HX, hat="helmet")
        tw = tb(j, k_w)
        for i in range(3):
            x = cx + 30 + i * 200
            opened = T >= tw + i * 0.2
            with K.at(c, x, cy - 30, 0, g):
                city_wall(c, 0, 0, 180, 190)
                if opened:
                    c.drawRect(skia.Rect.MakeXYWH(-30, -95, 60, 95), K.paint(NOTE_FILL))
                    flag(c, 0, -190, 0.35, "汉", "#9C2F25")
        return None
    L.note("汉")
    ev(j, k_han, scene, "tom", 0.75)
    b.hit(j, k_w, "shaker", 0.8, "城门一座座打开")
    buru(j, "韩信", HX, "#2F5B8E", k_name)


screen9()


# ================================================================ 屏 10：三人站成一排，刘邦把他们连起来；项羽把范增推开
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 120
    k_three = kq(j, wp(12, 0, 0.5), 0)
    k_link = nx(j, wp(12, 2, 0.5), k_three)
    k_why = nx(j, wp(12, 3, 0.5), k_link)
    k_fan = nx(j, wp(13, 0, 0.6), k_why)
    k_push = nx(j, wp(13, 1, 0.5), k_fan)
    k_lose = nx(j, wp(13, 2, 0.5), k_push)
    L.note("人杰", "范增", "项羽", "用好", "用不好")

    def three(c, kk, T):
        g = pop_scale(T - tb(j, k_three))
        if g <= 0:
            return None
        tl = tb(j, k_link)
        xs = [(cx - 420, ZL, "张良", "#2C6E68"), (cx - 140, XH, "萧何", "#8A5A1E"), (cx + 140, HX, "韩信", "#2F5B8E")]
        for x, col, nm, tc in xs:
            with at_pop(c, x, GY, g):
                gu(c, x, GY, 0.55, col, hat="helmet" if nm == "韩信" else "guan", beard="black" if nm != "张良" else None)
                name_tag(c, x, GY - 230, nm, tc, 30)
        if T >= tl:
            f = ease_out(clamp01((T - tl) / 0.5))
            lx = cx + 380
            with at_pop(c, lx, GY, pop_scale(T - tl)):
                gu(c, lx, GY, 0.65, LIU, hat="guan", beard="black", mood="smile")
                name_tag(c, lx, GY - 270, "刘邦", "#9C2F25", 30)
            for x, *_ in xs:
                C.line(c, (lx - 60, GY - 120), (lerp(lx - 60, x + 40, f), GY - 120), RED, 5)
                c.drawCircle(lerp(lx - 60, x + 40, f), GY - 120, 10, K.paint(RED))
        if T >= tb(j, k_why):
            with K.at(c, cx + 300, cy - 420, 0, C.slam_scale(T - tb(j, k_why))):
                chip(c, 0, 0, "用好", GREEN_FILL, GREEN, 54)
        return None
    b.custom(j, k_three, k_three + 0.3, three, sfx="wood_low", gain=0.65)
    b.hit(j, k_link, "ding", 0.8, "我能用好他们")
    b.hit(j, k_why, "pop", 0.7, "得天下的原因")

    def fan(c, kk, T):
        tf, tp, tl = tb(j, k_fan), tb(j, k_push), tb(j, k_lose)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        Y = cy + 520
        C.line(c, (cx - 560, cy + 190), (cx + 560, cy + 190), GRAY, 4)
        push = ease_out(clamp01((T - tp) / 0.4)) if T >= tp else 0
        with at_pop(c, cx - 150, Y, g):
            gu(c, cx - 150, Y, 0.6, XIANG, hat="helmet", beard="black", mood="angry",
               rh=(cx - 40, Y - 160) if T >= tp else None)
            name_tag(c, cx - 150, Y - 270, "项羽", "#6B3F7A", 30)
        fx_ = cx + 20 + 160 * push
        with K.at(c, fx_, Y, -20 * push, g):
            c.translate(-fx_, -Y)
            gu(c, fx_, Y, 0.6, FZ, hat="guan", beard="white", mood="sad" if push else "flat")
            name_tag(c, fx_, Y - 270, "范增", "#5E5E58", 30)
        if T >= tl:
            with K.at(c, cx + 360, cy + 300, -5, C.slam_scale(T - tl)):
                chip(c, 0, 0, "用不好", RED_FILL, RED, 50)
        return None
    b.custom(j, k_fan, k_fan + 0.3, fan, sfx="tom", gain=0.7)
    b.hit(j, k_push, "rim", 0.8, "推开范增")
    b.hit(j, k_lose, "kick", 0.85, "被打败")


screen10()


# ================================================================ 屏 11：群臣点头拱手
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_row = kq(j, wp(14, 0, 0.5), 0)
    k_bow = nx(j, wp(14, 1, 0.4), k_row)
    L.note("服")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_row))
        if g <= 0:
            return None
        tbw = tb(j, k_bow)
        with at_pop(c, cx, GY - 520, g):
            gu(c, cx, GY - 520, 0.6, LIU, hat="guan", beard="black", mood="smile")
        for i in range(5):
            x = cx - 440 + i * 220
            with at_pop(c, x, GY, pop_scale(T - tb(j, k_row) - i * 0.08)):
                gu(c, x, GY, 0.65, ("gray", "brown", "ochre", "blue", "teal")[i], hat="guan",
                   beard="black" if i % 2 else "white", bow=T >= tbw, head_dx=0, mood="smile" if T >= tbw else "flat")
        if T >= tbw:
            seal(c, cx, cy - 120, "服", 120, 0, C.slam_scale(T - tbw))
        return None
    ev(j, k_row, scene, "muyu", 0.65)
    b.hit(j, k_bow, "kick", 0.85, "群臣服气")


screen11()


# ================================================================ 屏 12：说回我们：小李把箱子放下；“三步”
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_down = kq(j, wp(15, 1, 0.5), 1)
    k_3 = nx(j, wp(16, 1, 0.5), k_down)
    LX = cx - 280
    L.note("好事", "三步")

    def scene(c, sc, T):
        td = tb(j, k_down)
        f = ease_out(clamp01((T - td) / 0.4)) if T >= td else 0
        hy = GY - 290
        with at_pop(c, LX, GY, sc):
            if f < 1:
                C.draw_li(c, LX, GY, 1.0, "sad", lh=(LX - 80, hy - 40 + 300 * f), rh=(LX + 80, hy - 40 + 300 * f))
            else:
                draw_li(c, LX, GY, 1.0, "smile")
            boxes_stack(c, lerp(LX, LX + 260, f), lerp(hy - 40, GY, f), 3)
        if T >= td:
            with K.at(c, cx + 260, cy - 300, 0, pop_scale(T - td)):
                chip(c, 0, 0, "好事", GREEN_FILL, GREEN, 60)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_down, "tom", 0.75, "放下箱子")
    L.stamp_ev(j, k_3, "三步", cx + 260, cy + 50, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen12()


# ================================================================ 屏 13：第一步：纸上写下每个人强在哪，贴出来
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 0)
    GY = cy + 520
    k_paper = kq(j, wp(17, 0, 0.6), 1)
    k_rows = nx(j, wp(17, 2, 0.4), k_paper)
    k_ok = nx(j, wp(17, 3, 0.5), k_rows)
    ROWS = [("小王", "会沟通"), ("老周", "懂技术"), ("小赵", "做表快")]
    L.note(*[f"{a}：{b_}" for a, b_ in ROWS], "比我强")

    def scene(c, kk, T):
        tp, tr, to = tb(j, k_paper), tb(j, k_rows), tb(j, k_ok)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        with K.at(c, cx + 140, cy - 80, -2, g):
            box(c, 0, 0, 560, 500, "#FFFFFF", BLUE, 7, 12)
            K.text(c, "比我强", 0, -190, 56, "hand", BLUE)
            for i, (a_, b_) in enumerate(ROWS):
                f = clamp01((T - tr - i * 0.2) / 0.25)
                if f > 0:
                    K.text(c, f"{a_}：{b_}", -200, -70 + i * 110, 54, "hand", INK, f, "left")
        LX = cx - 380
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "smile" if T >= to else "flat", rh=(LX + 150, GY - 330) if T >= to else None)
        if T >= to:
            sparkle(c, LX + 150, GY - 330, T - to, YELLOW, 8, 40, 100)
        return None
    ev(j, k_paper, scene, "wood_high", 0.65)
    b.hit(j, k_rows, "shaker", 0.7, "一个个写下来")
    b.hit(j, k_ok, "ding", 0.8, "大方承认")


screen13()


# ================================================================ 屏 14：第二步：三件事连到最合适的人，小李在中间管方向
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 1)
    GY = cy + 520
    k_tasks = kq(j, wp(18, 0, 0.6), 1)
    k_link = nx(j, wp(18, 1, 0.5), k_tasks)
    k_wheel = nx(j, wp(18, 2, 0.5), k_link)
    TASKS = ["对接客户", "写代码", "做报表"]
    L.note(*TASKS, "方向")

    def scene(c, kk, T):
        tt, tl, tw = tb(j, k_tasks), tb(j, k_link), tb(j, k_wheel)
        for i, s_ in enumerate(TASKS):
            g = pop_scale(T - tt - i * 0.1)
            if g <= 0:
                continue
            with K.at(c, cx - 300, cy - 300 + i * 160, 0, g):
                box(c, 0, 0, 300, 110, NOTE_FILL, ORANGE, 5, 12)
                K.text(c, s_, 0, 0, 50, "hand", INK)
        people = [(cx + 300, cy - 300, "wang"), (cx + 300, cy - 140, "ace"), (cx + 300, cy + 20, "li")]
        for i, (x, y, who) in enumerate(people):
            g = pop_scale(T - tt - 0.2 - i * 0.1)
            if g <= 0:
                continue
            with K.at(c, x, y, 0, g):
                c.drawCircle(0, 0, 60, K.paint("#FFFFFF"))
                c.drawCircle(0, 0, 60, wb.marker(BLUE if who == "wang" else (GRAY if who == "ace" else BLACK), 6))
                K.text(c, ("小王", "老周", "小赵")[i], 0, 0, 36, "hand", INK)
            if T >= tl + i * 0.15:
                f = ease_out(clamp01((T - tl - i * 0.15) / 0.3))
                C.line(c, (cx - 150, cy - 300 + i * 160), (lerp(cx - 150, x - 60, f), lerp(cy - 300 + i * 160, y, f)), GREEN, 6)
        LX = cx - 120
        with at_pop(c, LX, GY, pop_scale(T - tw)):
            draw_li(c, LX, GY, 0.9, "smile", lh=(LX - 60, GY - 230), rh=(LX + 60, GY - 230))
            c.drawCircle(LX, GY - 240, 70, wb.marker(INK, 8))
            for a in (0, 120, 240):
                C.line(c, (LX, GY - 240), (LX + 70 * math.cos(math.radians(a + 90)), GY - 240 + 70 * math.sin(math.radians(a + 90))), INK, 5)
        if T >= tw:
            K.text(c, "方向", LX + 200, GY - 240, 56, "hand", RED, clamp01((T - tw) / 0.2))
        return None
    L.note("小王", "老周", "小赵")
    ev(j, k_tasks, scene, "wood_high", 0.65)
    b.hit(j, k_link, "shaker", 0.75, "交给合适的人")
    b.hit(j, k_wheel, "tom", 0.75, "你管方向")


screen14()


# ================================================================ 屏 15：第三步：汇报时小李把聚光灯打到同事身上
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 2)
    GY = cy + 520
    k_report = kq(j, wp(19, 0, 0.6), 1)
    k_light = nx(j, wp(19, 2, 0.5), k_report)
    L.note("汇报", "小王做成的")
    LX, WX = cx - 360, cx + 250

    def scene(c, kk, T):
        tr, tl = tb(j, k_report), tb(j, k_light)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        with K.at(c, cx - 60, cy - 280, 0, g):
            box(c, 0, 0, 380, 220, "#FFFFFF", BLACK, 6, 10)
            K.text(c, "汇报", 0, -60, 54, "sans_medium", INK)
            for q in range(2):
                C.line(c, (-130, 10 + q * 45), (130 - q * 50, 10 + q * 45), GRAY, 5)
        if T >= tl:
            f = ease_out(clamp01((T - tl) / 0.3))
            beam = P((WX - 40, cy - 400), (WX - 200, GY), (WX + 200, GY), (WX + 40, cy - 400), close=True)
            c.drawPath(beam, K.paint(YELLOW, 0.3 * f))
            c.drawCircle(WX, cy - 410, 40, K.paint(YELLOW, f))
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "smile", rh=(LX + 160, GY - 330) if T >= tl else None)
        with at_pop(c, WX, GY, g):
            draw_wang(c, WX, GY, 0.95, mood="smile" if T >= tl else "flat")
        if T >= tl:
            with K.at(c, WX, cy + 30, 0, pop_scale(T - tl)):
                chip(c, 0, 0, "小王做成的", GREEN_FILL, GREEN, 46)
        return None
    ev(j, k_report, scene, "wood_high", 0.65)
    b.hit(j, k_light, "ding", 0.85, "点出是谁做成的")


screen15()


# ================================================================ 屏 16：好处：同事们跟在小李后面，小李肩上轻了
def screen16(j=16):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_team = kq(j, wp(20, 0, 0.6), 0)
    k_light = nx(j, wp(20, 2, 0.5), k_team)
    L.note("轻松")

    def scene(c, kk, T):
        tt, tl = tb(j, k_team), tb(j, k_light)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        LX = cx - 80
        x, dy, _ = C.walk(T, tt, 2.0, LX, LX + 300, 8)
        with at_pop(c, x, GY + dy, g):
            draw_li(c, x, GY + dy, 0.95, "smile", rh=(x + 120, GY - 380) if T >= tl else None)
            badge(c, x, GY + dy - 290 * 0.95 + 140 * 0.95, 0.95)
        for i, (dx_, who) in enumerate(((-220, "wang"), (-400, "ace"), (-560, "li"))):
            x0 = cx - 260 - i * 170
            xi, dyi, _ = C.walk(T, tt + 0.2 + i * 0.1, 2.0, x0, x0 + 300, 8)
            with at_pop(c, xi, GY + dyi, pop_scale(T - tt - 0.2 - i * 0.1)):
                if who == "wang":
                    draw_wang(c, xi, GY + dyi, 0.8, mood="smile")
                elif who == "ace":
                    draw_ace(c, xi, GY + dyi, 0.8, mood="smile")
                else:
                    draw_li(c, xi, GY + dyi, 0.8, "smile")
        if T >= tl:
            sparkle(c, x, GY - 380, T - tl, YELLOW, 10, 60, 130)
            K.text(c, "轻松", x, cy - 300, 70, "hand", GREEN, clamp01((T - tl) / 0.2))
        return None
    ev(j, k_team, scene, "wood_low", 0.6)
    b.hit(j, k_light, "ding", 0.85, "不用一个人扛")


screen16()


# ================================================================ 屏 17：评论区；小李给同事竖大拇指；下一讲预告
def screen17(j=17):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z_))
    k_cmt = 0
    k_chips = nx(j, wp(22, 0, 0.3), 0)
    k_li = nx(j, wp(23, 0, 0.4), k_chips)
    k_grow = nx(j, wp(23, 3, 0.3), k_li)
    k_next = nx(j, wp(24, 1, 0.2), k_grow)
    b.move(j, k_li, (cx, cy + 380, Z_), 1.1)
    CH = ["做表比我快", "脾气比我好", "能扛事"]
    L.note("谁比你强？", *CH, "下一讲", "接手别人的活", "要不要全推翻？", "带人的本事")
    BY = cy - 330

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 20, BY, 0, sc):
            bubble_box(c, 0, 0, 1000, 360, -1)
            K.text(c, "谁比你强？", 0, -110, 62, "hand", RED)
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
    LX, LY = cx - 300, cy + 640

    def li(c, kk, T):
        tl, tg = tb(j, k_li), tb(j, k_grow)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        hy = LY - 290 * 0.95
        with at_pop(c, LX, LY, g):
            draw_li(c, LX, LY, 0.95, "smile", rh=(LX + 150, hy + 40))
            with K.at(c, LX + 170, hy + 20, -10):
                c.drawRoundRect(skia.Rect.MakeXYWH(-30, -20, 60, 60), 18, 18, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-30, -20, 60, 60), 18, 18, wb.marker(BLACK, 5))
                C.line(c, (-10, -20), (-10, -60), BLACK, 12)
            draw_wang(c, LX + 420, LY, 0.9, mood="smile")
        bx = cx + 380
        lv = 0.25 + 0.65 * ease_out(clamp01((T - tg) / 0.6)) if T >= tg else 0.25
        box(c, bx, cy + 420, 80, 440, "#FFFFFF", GRAY, 5, 14)
        c.drawRoundRect(skia.Rect.MakeXYWH(bx - 30, cy + 630 - 420 * lv, 60, 420 * lv), 14, 14, K.paint(GREEN))
        K.text(c, "带人的本事", bx - 40, cy + 170, 44, "hand", GREEN)
        if T >= tg:
            sparkle(c, bx, cy + 630 - 420 * lv, T - tg, YELLOW, 8, 40, 100)
        return None
    ev(j, k_li, li, "wood_low", 0.6)
    b.hit(j, k_grow, "ding", 0.8, "本事一点点长出来")

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
            K.text(c, "接手别人的活", -110, -60, 58, "hand", BLACK)
            K.text(c, "要不要全推翻？", -60, 40, 58, "hand", BLACK)
            box(c, 390, 0, 150, 120, NOTE_FILL, ORANGE, 5, 8)
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen17()

# ================================================================ 收尾
L.finish(cover_shot=10, square_shot=10, notes=NOTES)
L.export(globals())
