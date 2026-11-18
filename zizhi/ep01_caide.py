"""《资治通鉴》01 才与德：能力那么强，为什么最后没人帮他？（白板手绘 + AI 旁白，竖屏 2:3）

故事贯穿：先看办公室里“能干但坑人”的同事（抢功、甩锅、打断别人），再进《资治通鉴》卷一，跟着智瑶走完一生——
父亲要立他、智果劝谏（五强一弱）、智果改姓分家、蓝台宴上戏弄韩魏、索地、围晋阳、“水可以亡人国”、韩魏反水、
智氏灭族、唯辅果在——最后是司马光“才胜德”的评语（天平、四种人），落到打工人的三招、评论区与下一讲。
古人的屏都画在卷轴框里（左上角朱印“通鉴”），今人在办公室，两边分得开；今人不戴安全帽。
文案见 zizhi/PLAN.md「### 01」；时间轴、配乐、相机来自 fengtian/common.py 的 Lesson，人物与道具见 zizhi/lesson.py。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross, join, rect
from zizhi import lesson as Z
from zizhi import theme as ZT
from zizhi.lesson import (BLACK, BLUE, GRAY, GRAY_FILL, GREEN, GREEN_FILL, INK, NOTE_FILL, ORANGE, RED, RED_FILL, BLUE_FILL,
                          WATER, WATER_LINE, YELLOW, at_pop, bamboo_slips, box, bubble_box, city_wall, cup, desk, draw_ace,
                          draw_boss, draw_li, draw_wang, flag, gu, head_of, pop_scale, seal, slip_text, sparkle, water)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4], "身边的例子", 4),
    ([5], "通鉴里的故事", 5),
    ([6, 7], "智果劝谏", 6),
    ([8, 9], "五强一弱", 7),
    ([10, 11], "智果劝谏", 8),
    ([12], "智果分家", 9),
    ([13, 14], "当家之后", 10),
    ([15, 16], "索地", 11),
    ([17, 18], "围晋阳", 12),
    ([19, 20], "得意忘形", 13),
    ([21, 22], "反水", 14),
    ([23], "唯辅果在", 15),
    ([24, 25], "司马光点评", 16),
    ([26], "司马光点评", 17),
    ([27, 28], "说回我们自己", 18),
    ([29], "第一招", 19),
    ([30], "第二招", 20),
    ([31], "第三招", 21),
    ([32], "好处", 22),
    ([33, 34, 35, 36], "评论区见", 23),
]

THEME = ZT.get("01")
L = Z.Lesson("01", SCREENS, drop_screen=2, board_size=(5000, 15400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(22)]
Z_ = 0.72

NOTES = [
    "出处：司马光《资治通鉴》卷一 周纪一（威烈王二十三年，追叙晋阳之战与智氏之亡）及“臣光曰”。",
    "原文：智果曰“瑶之贤于人者五，其不逮者一也……如是而甚不仁……若果立瑶也，智宗必灭”；“智果别族于太史，为辅氏”；"
    "智伯戏康子而侮段规，“难将由我，我不为难，谁敢兴之”；韩、魏各致万家之邑，赵襄子弗与；“城不浸者三版，沈灶产蛙”；"
    "“吾乃今知水可以亡人国也”；“桓子肘康子，康子履桓子之跗”；张孟谈“唇亡则齿寒”；襄子决水灌智伯军，韩、魏翼而击之，"
    "尽灭智氏之族，唯辅果在；臣光曰“智伯之亡也，才胜德也……与其得小人，不若得愚人”。",
    "今人（小李、小王、能人同事、新人）均为虚构示意；古人造型为示意，不代表真实服饰考据。",
]

# 人物配色
ZHIYAO, ZHIGUO, FATHER, HAN, WEI, ZHAO = "purple", "green", "brown", "blue", "ochre", "red"
PARCH, PARCH_LINE = "#F7EFD9", "#9C7A3A"


def gu_frame(j, k=0):
    """古人屏：卷轴框（米色纸 + 双线边框 + 左上角朱印“通鉴”），和今人的办公室分开。"""
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


def trophy(c, x, y, s=1.0, a=1.0):
    with K.at(c, x, y, 0, s):
        cupp = P((-50, -150), (50, -150), (36, -80), (12, -60), (-12, -60), (-36, -80), close=True)
        c.drawPath(cupp, K.paint(YELLOW, a))
        c.drawPath(cupp, wb.marker("#A9842A", 6, a))
        for sg in (-1, 1):
            ar = skia.Path()
            ar.addArc(skia.Rect.MakeXYWH(sg * 50 - 22, -140, 44, 44), -90 if sg > 0 else 90, 180)
            c.drawPath(ar, wb.marker("#A9842A", 6, a))
        C.line(c, (0, -60), (0, -24), "#A9842A", 8, a)
        box(c, 0, -12, 90, 24, "#C98B4B", "#7A4A1E", 5, 6, a)


def newbie(c, x, y, s, mood="flat", lh=None, rh=None, a=1.0):
    """新人：小李式黑线小人 + 背包 + 胸前绿色“新人”牌。"""
    draw_li(c, x, y, s, mood, bag=True, lh=lh, rh=rh, alpha=a)
    hy = y - 290 * s
    box(c, x, hy + 135 * s, 74 * s, 36 * s, GREEN_FILL, GREEN, 4, 6, a)
    K.text(c, "新人", x, hy + 136 * s, 26 * s, "sans_medium", GREEN, a)


def sweat(c, x, y, dt, a=1.0):
    if dt < 0:
        return
    for i in range(2):
        f = (dt * 1.3 + i * 0.5) % 1.0
        yy = y + f * 60
        p = P((x + i * 30, yy - 20), (x + i * 30 - 12, yy + 6), (x + i * 30 + 12, yy + 6), close=True)
        c.drawPath(p, K.paint(WATER, a * (1 - f)))
        c.drawPath(p, wb.marker(WATER_LINE, 3, a * (1 - f)))


L.note("新人")


# ================================================================ 屏 0：开场（zizhi/hooks.py zz_credit）
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：能人同事在奖杯堆里，小李小王缩在边上；抢功 / 甩锅 / 看不起人
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_ace = 0
    k_t1 = kq(j, wp(0, 2, 0.3), 1)
    k_t2 = nx(j, wp(0, 3, 0.6), k_t1)
    k_pair = nx(j, wp(1, 0, 0.1), k_t2)
    k_c = [nx(j, wp(1, 0, 0.5), k_pair, 0)]
    k_c.append(nx(j, wp(1, 1, 0.3), k_c[0]))
    k_c.append(nx(j, wp(1, 2, 0.5), k_c[1]))
    L.note("抢功", "甩锅", "看不起人")
    AX = cx + 180

    def ace(c, sc, T):
        laugh = T >= tb(j, k_t2)
        with at_pop(c, AX, GY, sc):
            draw_ace(c, AX, GY, 1.05, mood="laugh" if laugh else "smug", chin=1 if laugh else 0,
                     rh=(AX + 110, GY - 420) if laugh else None)
    ev(j, k_ace, L.pop_fn(j, k_ace, ace), "wood_high", 0.7)

    def trophies(c, kk, T):
        for i, (k_, x, y, s) in enumerate(((k_t1, AX + 330, GY - 40, 1.1), (k_t2, AX - 330, GY - 40, 1.0),
                                          (k_t2, AX + 360, GY - 300, 0.8))):
            g = pop_scale(T - tb(j, k_) - (0.18 if i == 2 else 0))
            if g > 0:
                trophy(c, x, y, s * g)
                sparkle(c, x, y - 110 * s, T - tb(j, k_), YELLOW, 8, 60, 120)
        return None
    ev(j, k_t1, trophies, "ding", 0.7)
    b.hit(j, k_t2, "ding", 0.6, "又一座奖杯")

    def pair(c, sc, T):
        for x, who in ((cx - 470, "li"), (cx - 300, "wang")):
            with at_pop(c, x, GY, sc):
                if who == "li":
                    draw_li(c, x, GY, 0.7, "sad")
                else:
                    draw_wang(c, x, GY, 0.7, mood="sad")
    ev(j, k_pair, L.pop_fn(j, k_pair, pair), "wood_low", 0.6)

    def chips(c, kk, T):
        for i, (k_, s_) in enumerate(zip(k_c, ("抢功", "甩锅", "看不起人"))):
            g = C.slam_scale(T - tb(j, k_))
            if g > 0:
                with K.at(c, cx - 300 + i * 40, cy - 420 + i * 150, (i - 1) * 4, g):
                    chip(c, 0, 0, s_, RED_FILL, RED, 58)
        return None
    ev(j, k_c[0], chips, "rim", 0.75)
    for k_ in k_c[1:]:
        b.hit(j, k_, "rim", 0.75, "标签砸下")


screen1()


# ================================================================ 屏 2（drop）：项目汇报，署名只剩他一个；drop 时红圈
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_doc = 0
    k_ok = kq(j, wp(2, 0, 0.7), 1)
    dk = L.drop_k()
    k_erase = max(k_ok + 1, min(dk - 1, kq(j, wp(2, 1, 0.3), k_ok + 1)))
    x, top, w, h = cx - 60, cy - 560, 760, 1000
    L.note("项目汇报", "完成", "署名", "小王", "小李", "他")
    b.path(j, k_doc, k_doc + 0.6, rect(x, top + h / 2, w, h, 26), BLACK, 9, sfx="wood_high")
    b.text(j, k_doc + 0.2, k_doc + 0.6, "项目汇报", x, top + 100, 76, BLACK, font="sans_medium")
    for i in range(3):
        b.path(j, k_doc + 0.4, k_doc + 0.8, P((x - 280, top + 200 + i * 70), (x + 280 - (i % 2) * 120, top + 200 + i * 70)),
               GRAY, 6)
    L.stamp_ev(j, k_ok, "完成", x + 230, top + 300, 64, -10, "clap", 0.8, GREEN)
    b.text(j, k_doc + 0.5, k_doc + 0.9, "署名", x - 250, top + 520, 56, GRAY, font="sans_medium")
    names = [("小王", x - 120, top + 640), ("小李", x + 130, top + 640), ("他", x, top + 820)]

    def sign(c, kk, T):
        te = tb(j, k_erase)
        for i, (s_, nx_, ny_) in enumerate(names):
            if i < 2:
                f = ease_in_out(clamp01((T - te - i * 0.2) / 0.35))
                a = 1 - f
                if a > 0:
                    K.text(c, s_, nx_, ny_, 80, "hand", BLACK, a)
                if 0 < f < 1:
                    box(c, nx_ - 60 + 120 * f, ny_, 70, 46, "#F4D9D9", "#C97A7A", 4, 10)
            else:
                g = 1 + 0.5 * C.slam_scale(T - tb(j, dk)) if T >= tb(j, dk) else 1
                with K.at(c, nx_, ny_, 0, g):
                    K.text(c, s_, 0, 0, 110, "hand", BLACK)
        return None
    b.custom(j, k_doc + 0.5, k_doc + 0.9, sign)
    b.hit(j, k_erase, "shaker", 0.7, "别人的名字被擦掉")
    ring = skia.Path()
    ring.addOval(skia.Rect.MakeXYWH(x - 140, top + 820 - 110, 280, 220))
    b.path(j, dk, dk + 0.3, ring, RED, 13, sfx="kick", gain=0.9)
    b.shots[j].shake = [(dk, 12.0)]
    b.shots[j].flashes = [(dk, 0.3)]


screen2()


# ================================================================ 屏 3：出了岔子，报表被他一推，推到新人桌上
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_err = kq(j, wp(3, 0, 0.5), 0)
    k_push = nx(j, wp(3, 1, 0.6), k_err)
    k_land = nx(j, wp(3, 2, 0.6), k_push)
    L.note("出错")
    AX, NX = cx + 330, cx - 330
    DY = GY - 170

    def scene(c, sc, T):
        with at_pop(c, cx, GY, sc):
            desk(c, AX - 80, DY, 280, laptop=False)
            desk(c, NX + 80, DY, 280, laptop=False)
            tp = tb(j, k_push)
            pushing = tp <= T < tp + 0.5
            hy = GY - 290
            draw_ace(c, AX + 170, GY, 0.95, mood="smug" if T < tp else "cold",
                     lh=(AX - 20, DY - 40) if pushing else None)
            tl = tb(j, k_land)
            newbie(c, NX - 150, GY, 0.95, "o" if T >= tl else "flat",
                   lh=(NX - 240, hy + 40) if T >= tl else None, rh=(NX - 60, hy + 40) if T >= tl else None)
            if T >= tl:
                sweat(c, NX - 90, hy - 60, T - tl)
        return None
    ev(j, 0, L.pop_fn(j, 0, scene), "wood_high", 0.6)

    def sheet(c, kk, T):
        t0 = tb(j, k_err)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        tp, tl = tb(j, k_push), tb(j, k_land)
        f = ease_in_out(clamp01((T - tp) / max(0.2, tl - tp)))
        x = lerp(AX - 80, NX + 80, f)
        y = DY - 60 - math.sin(math.pi * f) * 160
        with K.at(c, x, y, lerp(-6, 8, f) + 360 * f * (1 if f < 1 else 0), sc * 0.85):
            box(c, 0, 0, 230, 150, "#FFFFFF", RED, 7, 10)
            for r in range(3):
                C.line(c, (-80, -40 + r * 34), (60 - (r % 2) * 40, -40 + r * 34), GRAY, 5)
            c.drawPath(cross(70, 30, 34), wb.marker(RED, 10))
            K.text(c, "出错", -40, 56, 40, "hand", RED)
        return None
    ev(j, k_err, sheet, "rim", 0.75)
    b.hit(j, k_push, "shaker", 0.7, "一推")
    b.hit(j, k_land, "tom", 0.8, "落到新人桌上")
    b.shots[j].shake = [(k_land, 7.0)]


screen3()


# ================================================================ 屏 4：会上小王刚开口，他笑着打断：这都不懂？
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_wang = kq(j, wp(4, 0, 0.5), 0)
    k_cut = nx(j, wp(4, 1, 0.5), k_wang)
    k_big = nx(j, wp(4, 2, 0.4), k_cut)
    WX, AX = cx - 300, cx + 300
    L.note("我觉得……", "这都不懂？")

    def table(c, sc, T):
        with at_pop(c, cx, GY, sc):
            box(c, cx, GY - 150, 980, 60, "#E7D6BA", "#8B6B43", 6, 10)
            for dx in (-420, 420):
                C.line(c, (cx + dx, GY - 120), (cx + dx, GY), "#8B6B43", 9)
        return None
    ev(j, 0, L.pop_fn(j, 0, table), "wood_low", 0.6)

    def people(c, kk, T):
        tw, tc, tg = tb(j, k_wang), tb(j, k_cut), tb(j, k_big)
        g = pop_scale(T - tw)
        if g > 0:
            shrink = 1 - 0.12 * ease_out(clamp01((T - tg) / 0.4)) if T >= tg else 1
            with at_pop(c, WX, GY, g * shrink):
                hy = GY - 290
                draw_wang(c, WX, GY, 0.95, mood="sad" if T >= tc else "flat",
                          rh=(WX + 60, hy - 70) if T < tc else None)
            if T < tc + 0.25:
                a = 1 - clamp01((T - tc) / 0.25) if T >= tc else 1
                bubble_box(c, WX - 30, cy - 330, 330, 140, 1, a * clamp01(g))
                K.text(c, "我觉得……", WX - 30, cy - 330, 54, "hand", BLACK, a * clamp01(g))
        ga = pop_scale(T - tb(j, 0) - 0.15)
        if ga > 0:
            with at_pop(c, AX, GY, ga):
                draw_ace(c, AX, GY, 1.0, mood="laugh" if T >= tc else "smug", lh=(AX - 140, GY - 330) if T >= tc else None)
        if T >= tc:
            sc = C.slam_scale(T - tc) * (1 + 0.25 * pop_scale(T - tg)) if T >= tg else C.slam_scale(T - tc)
            with K.at(c, AX - 60, cy - 330, 3, sc):
                bubble_box(c, 0, 0, 440, 170, -1)
                K.text(c, "这都不懂？", 0, 0, 68, "hand", RED)
        return None
    b.custom(j, 0, 0.3, people)
    b.hit(j, k_wang, "pop", 0.6, "小王举手")
    b.hit(j, k_cut, "rim", 0.8, "笑着打断")
    b.hit(j, k_big, "tom", 0.75, "小王缩了")
    b.shots[j].shake = [(k_cut, 6.0)]


screen4()


# ================================================================ 屏 5：竹简展开“资治通鉴 卷一”，智瑶出场
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_slip = 0
    k_txt = kq(j, wp(5, 0, 0.5), 1)
    k_jin = nx(j, wp(5, 1, 0.4), k_txt)
    k_yao = nx(j, wp(5, 2, 0.2), k_jin)
    SX = cx - 270
    L.note("资治通鉴", "卷一", "周纪一", "智瑶", "晋国")

    def slips(c, kk, T):
        f = ease_out(clamp01((T - tb(j, k_slip)) / 0.6))
        if f <= 0:
            return None
        w = 420 * f
        bamboo_slips(c, SX, cy - 60, max(60, w), 820, n=max(1, int(6 * f)))
        if T >= tb(j, k_txt):
            a = clamp01((T - tb(j, k_txt)) / 0.3)
            slip_text(c, SX + 70, cy - 380, "资治通鉴", 92, "#3A2A12", a)
            slip_text(c, SX - 80, cy - 340, "卷一", 70, RED, a)
            slip_text(c, SX - 80, cy - 120, "周纪一", 54, "#5E4128", a, 1.15)
        return None
    ev(j, k_slip, slips, "muyu", 0.7, 0.6)
    b.hit(j, k_txt, "wood_high", 0.7, "书名写上竹简")

    def jin(c, kk, T):
        g = C.slam_scale(T - tb(j, k_jin))
        if g > 0:
            seal(c, cx + 270, cy - 420, "晋国", 64, 4, g)
        return None
    ev(j, k_jin, jin, "bangzi", 0.7)

    def yao(c, sc, T):
        x = cx + 260
        with at_pop(c, x, GY, sc):
            gu(c, x, GY, 1.05, ZHIYAO, hat="guan", mood="smile")
            name_tag(c, x, GY - 420, "智瑶", "#6B3F7A", 56)
    ev(j, k_yao, L.pop_fn(j, k_yao, yao), "tom", 0.8)


screen5()


# ================================================================ 屏 6：父亲看中智瑶，智果拱手劝：强在五处，差在一处
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_fa = 0
    k_pick = kq(j, wp(6, 1, 0.3), 1)
    k_guo = nx(j, wp(7, 0, 0.3), k_pick)
    k_five = nx(j, wp(7, 1, 0.5), k_guo)
    k_one = nx(j, wp(7, 2, 0.5), k_five)
    FX, YX, GX = cx - 380, cx - 30, cx + 360
    L.note("父亲", "智瑶", "智果", "五处", "一处")

    def fa(c, sc, T):
        pick = T >= tb(j, k_pick)
        with at_pop(c, FX, GY, sc):
            gu(c, FX, GY, 0.95, FATHER, hat="guan", beard="white", mood="smile" if pick else "flat",
               rh=(FX + 150, GY - 300) if pick else None)
            name_tag(c, FX, GY - 410, "父亲", "#5E4128", 44)
        return None
    ev(j, k_fa, L.pop_fn(j, k_fa, fa), "muyu", 0.6)

    def yao(c, sc, T):
        with at_pop(c, YX, GY, sc):
            gu(c, YX, GY, 0.95, ZHIYAO, hat="guan", mood="smile")
            name_tag(c, YX, GY - 410, "智瑶", "#6B3F7A", 44)
        if T >= tb(j, k_pick):
            sparkle(c, YX, GY - 300, T - tb(j, k_pick), YELLOW, 10, 80, 160)
        return None
    ev(j, 0.4, L.pop_fn(j, 0.4, yao))
    b.hit(j, k_pick, "ding", 0.7, "父亲看中智瑶")

    def guo(c, sc, T):
        with at_pop(c, GX, GY, sc):
            gu(c, GX, GY, 0.95, ZHIGUO, hat="bun", beard="black", bow=True)
            name_tag(c, GX, GY - 410, "智果", "#3F6B3A", 44)
        return None
    ev(j, k_guo, L.pop_fn(j, k_guo, guo), "wood_low", 0.7)

    def stars(c, kk, T):
        t5, t1 = tb(j, k_five), tb(j, k_one)
        for i in range(6):
            t0 = t5 + i * 0.09 if i < 5 else t1
            g = pop_scale(T - t0)
            if g <= 0:
                continue
            x, y = cx - 400 + i * 160, cy - 400
            with K.at(c, x, y, 0, g):
                pts = [(math.cos(math.radians(-90 + 36 * q)) * (56 if q % 2 == 0 else 24),
                        math.sin(math.radians(-90 + 36 * q)) * (56 if q % 2 == 0 else 24)) for q in range(10)]
                st = P(*pts, close=True)
                if i < 5:
                    c.drawPath(st, K.paint(YELLOW))
                    c.drawPath(st, wb.marker("#A9842A", 5))
                else:
                    c.drawPath(st, K.paint("#FFFFFF"))
                    c.drawPath(st, wb.marker(RED, 6))
                    C.line(c, (-30, -40), (30, 40), RED, 8)
        if T >= t5:
            K.text(c, "五处", cx - 80, cy - 290, 56, "hand", "#A9842A", clamp01((T - t5) / 0.3))
        if T >= t1:
            K.text(c, "一处", cx + 400, cy - 290, 56, "hand", RED, clamp01((T - t1) / 0.3))
        return None
    ev(j, k_five, stars, "shaker", 0.7)
    b.hit(j, k_one, "rim", 0.8, "一颗空心星")


screen6()


# ================================================================ 屏 7：五样本事逐个点亮，一颗心裂开“刻薄”
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    pieces = L.LINES[8][1]
    ks = [kq(j, wp(8, 0, 0.3), 0)]
    ks.append(nx(j, wp(8, 1, 0.4), ks[-1]))
    ks.append(nx(j, wp(8, 2, 0.2), ks[-1]))
    ks.append(nx(j, wp(8, 2, 0.8), ks[-1]))
    ks.append(nx(j, wp(8, 3, 0.3), ks[-1]))
    k_heart = nx(j, wp(9, 1, 0.4), ks[-1])
    LBL = ["个子高", "能射箭驾车", "手艺多", "口才好", "果断"]
    L.note(*LBL, "刻薄")
    del pieces
    pos = [(cx - 360, cy - 330), (cx, cy - 330), (cx + 360, cy - 330), (cx - 180, cy + 10), (cx + 180, cy + 10)]

    def icon(c, i, x, y):
        if i == 0:                                    # 个子高：人 + 身高尺
            gu(c, x - 30, y + 90, 0.5, ZHIYAO, hat="guan")
            C.line(c, (x + 60, y - 90), (x + 60, y + 90), "#8B6B43", 6)
            for q in range(5):
                C.line(c, (x + 60, y - 90 + q * 45), (x + 80, y - 90 + q * 45), "#8B6B43", 4)
        elif i == 1:                                  # 射箭：弓 + 箭
            bow = skia.Path()
            bow.addArc(skia.Rect.MakeXYWH(x - 90, y - 80, 110, 160), -70, 140)
            c.drawPath(bow, wb.marker("#8B4A1E", 9))
            C.line(c, (x + 2, y - 76), (x + 2, y + 76), INK, 3)
            C.line(c, (x - 60, y), (x + 90, y), INK, 6)
            c.drawPath(P((x + 90, y), (x + 66, y - 14), (x + 66, y + 14), close=True), K.paint(INK))
        elif i == 2:                                  # 手艺：锤 + 尺
            C.line(c, (x - 50, y + 70), (x + 30, y - 40), "#8B4A1E", 12)
            box(c, x + 40, y - 54, 90, 44, GRAY_FILL, INK, 5, 6)
            C.line(c, (x - 80, y - 60), (x - 10, y + 80), "#C9A34A", 14)
        elif i == 3:                                  # 口才：毛笔 + 气泡
            bubble_box(c, x - 20, y - 20, 150, 100, -1)
            C.line(c, (x + 40, y + 80), (x + 90, y - 20), "#8B4A1E", 10)
            c.drawPath(P((x + 32, y + 78), (x + 48, y + 82), (x + 30, y + 110), close=True), K.paint(INK))
        else:                                         # 果断：剑
            C.line(c, (x - 70, y + 70), (x + 60, y - 60), "#9AA3AD", 14)
            C.line(c, (x - 50, y + 30), (x - 20, y + 60), "#8B4A1E", 10)
            C.line(c, (x - 70, y + 70), (x - 50, y + 50), "#8B4A1E", 12)

    def cards(c, kk, T):
        for i, ((x, y), k_, s_) in enumerate(zip(pos, ks, LBL)):
            g = pop_scale(T - tb(j, k_))
            if g <= 0:
                continue
            with K.at(c, x, y, 0, g):
                box(c, 0, 0, 300, 300, "#FFFFFF", "#A9842A", 6, 18)
                icon(c, i, 0, -30)
                K.text(c, s_, 0, 115, 44 if len(s_) < 5 else 38, "hand", INK)
                c.drawCircle(120, -120, 22, K.paint(YELLOW))
                c.drawCircle(120, -120, 22, wb.marker("#A9842A", 4))
        return None
    ev(j, ks[0], cards, "wood_high", 0.7)
    for k_ in ks[1:]:
        b.hit(j, k_, "wood_high", 0.7, "又一样本事")

    def heart(c, kk, T):
        t0 = tb(j, k_heart)
        g = C.slam_scale(T - t0)
        if g <= 0:
            return None
        x, y = cx, cy + 360
        crack = ease_out(clamp01((T - t0) / 0.3))
        with K.at(c, x, y, 0, g):
            for sg in (-1, 1):
                c.save()
                c.translate(sg * 18 * crack, 0)
                c.rotate(sg * 6 * crack)
                c.clipRect(skia.Rect.MakeLTRB(-200 if sg < 0 else 0, -200, 0 if sg < 0 else 200, 200))
                hp = C.heart_path(0, 0, 90)
                c.drawPath(hp, K.paint(RED_FILL))
                c.drawPath(hp, wb.marker(RED, 8))
                c.restore()
            c.drawPath(P((0, -40), (-18, 0), (14, 30), (-6, 80)), wb.marker(RED, 7))
            K.text(c, "刻薄", 230, 10, 80, "hand", RED)
        return None
    ev(j, k_heart, heart, "kick", 0.85)
    b.shots[j].shake = [(k_heart, 8.0)]


screen7()


# ================================================================ 屏 8：智瑶站在五样本事上压人；“智宗必灭”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_stack = 0
    k_yao = kq(j, wp(10, 0, 0.6), 1)
    k_press = nx(j, wp(10, 1, 0.5), k_yao)
    k_q = nx(j, wp(10, 2, 0.4), k_press)
    k_doom = nx(j, wp(11, 1, 0.3), k_q)
    SX = cx - 120
    L.note("智宗必灭", "谁受得了？")
    LBL = ["果断", "口才", "手艺", "射御", "个子"]

    def stack(c, kk, T):
        tp = tb(j, k_press)
        sq = 0.12 * ease_out(clamp01((T - tp) / 0.25)) if T >= tp else 0
        for i, s_ in enumerate(LBL):
            g = pop_scale(T - tb(j, k_stack) - i * 0.08)
            if g <= 0:
                continue
            y = GY - 60 - i * 92
            with K.at(c, SX, y, (i % 2) * 2 - 1, g):
                box(c, 0, 0, 380 - i * 20, 80, NOTE_FILL, "#A9842A", 6, 10)
                K.text(c, s_, 0, 2, 46, "hand", INK)
        # 底下被压的小人
        for q, x in enumerate((SX - 330, SX + 330)):
            gp = pop_scale(T - tb(j, k_stack) - 0.3)
            if gp <= 0:
                continue
            c.save()
            c.translate(x, GY)
            c.scale(1, 1 - sq * 2.2)
            c.translate(-x, -GY)
            gu(c, x, GY, 0.55, "gray", hat="bun", mood="sad")
            c.restore()
        if T >= tp:
            for x in (SX - 330, SX + 330):
                K.burst(c, x, GY - 200, T - tp, GRAY, 20, 70, 6, 5, 0.7)
        return None
    ev(j, k_stack, stack, "wood_low", 0.7)

    def yao(c, sc, T):
        x, y = SX, GY - 60 - 4 * 92 - 40
        tp = tb(j, k_press)
        dy = 30 * math.sin(clamp01((T - tp) / 0.25) * math.pi) if T >= tp else 0
        with at_pop(c, x, y + dy, sc):
            gu(c, x, y + dy, 0.75, ZHIYAO, hat="guan", mood="laugh" if T >= tp else "smile",
               lh=(x - 140, y - 200), rh=(x + 140, y - 200))
        return None
    ev(j, k_yao, L.pop_fn(j, k_yao, yao), "tom", 0.75)
    b.hit(j, k_press, "kick", 0.75, "往下一压")
    b.shots[j].shake = [(k_press, 8.0)]

    def q(c, kk, T):
        g = pop_scale(T - tb(j, k_q))
        if g > 0:
            with K.at(c, cx - 380, cy - 420, -4, g):
                bubble_box(c, 0, 0, 340, 140, 1)
                K.text(c, "谁受得了？", 0, 0, 52, "hand", INK)
        return None
    ev(j, k_q, q, "pop", 0.6)

    def doom(c, kk, T):
        t0 = tb(j, k_doom)
        g = C.slam_scale(T - t0)
        if g <= 0:
            return None
        x, y = cx + 400, cy - 160
        with K.at(c, x, y, 3, g):
            bamboo_slips(c, 0, 0, 170, 560, n=2)
            slip_text(c, 0, -200, "智宗必灭", 88, RED)
        return None
    ev(j, k_doom, doom, "xiaoluo", 0.8)


screen8()


# ================================================================ 屏 9：父亲摆手；智果到太史那里改姓辅，背包离开
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_no = kq(j, wp(12, 0, 0.5), 0)
    k_shi = nx(j, wp(12, 1, 0.4), k_no)
    k_x = nx(j, wp(12, 2, 0.2), k_shi)
    k_fu = nx(j, wp(12, 2, 0.9), k_x)
    k_go = nx(j, wp(12, 3, 0.3), k_fu)
    FX, SX, GX = cx - 420, cx + 300, cx - 130
    L.note("不听", "太史", "智", "辅", "族谱")

    def fa(c, sc, T):
        wave = T >= tb(j, k_no)
        with at_pop(c, FX, GY, sc):
            hy = GY - 290 * 0.85
            ph = (T - tb(j, k_no)) * 9
            gu(c, FX, GY, 0.85, FATHER, hat="guan", beard="white", mood="angry" if wave else "flat",
               rh=(FX + 110 + 30 * math.sin(ph), hy - 40) if wave else None)
        if wave:
            g = pop_scale(T - tb(j, k_no))
            with K.at(c, FX, cy - 330, 0, g):
                bubble_box(c, 0, 0, 220, 120, 1)
                K.text(c, "不听", 0, 0, 56, "hand", RED)
        return None
    ev(j, 0, L.pop_fn(j, 0, fa), "muyu", 0.6)
    b.hit(j, k_no, "wood_high", 0.7, "父亲摆手")

    def shi(c, sc, T):
        with at_pop(c, SX, GY, sc):
            gu(c, SX + 140, GY, 0.8, "gray", hat="guan", beard="black", rh=(SX + 40, GY - 180))
            name_tag(c, SX + 140, GY - 360, "太史", "#5E5E58", 40)
            box(c, SX - 40, GY - 150, 320, 34, "#C9A97A", "#7A5E3A", 5, 6)
        return None
    ev(j, k_shi, L.pop_fn(j, k_shi, shi), "wood_low", 0.65)

    def book(c, kk, T):
        g = pop_scale(T - tb(j, k_shi))
        if g <= 0:
            return None
        x, y = SX - 60, cy - 120
        with K.at(c, x, y, 0, g):
            bamboo_slips(c, 0, 0, 420, 300, n=6)
            K.text(c, "族谱", 0, -195, 46, "serif_black", "#5E4128")
            tx = tb(j, k_x)
            K.text(c, "智", -10, 10, 96, "serif_black", INK)
            K.text(c, "果", 110, 10, 96, "serif_black", INK)
            if T >= tx:
                f = ease_out(clamp01((T - tx) / 0.2))
                C.line(c, (-60, -40), (-60 + 100 * f, -40 + 90 * f), RED, 10)
            tf = tb(j, k_fu)
            if T >= tf:
                gg = C.slam_scale(T - tf)
                with K.at(c, -140, 10, -8, gg):
                    K.text(c, "辅", 0, 0, 96, "serif_black", RED)
        return None
    ev(j, k_shi, book)
    b.hit(j, k_x, "rim", 0.75, "划掉“智”")
    b.hit(j, k_fu, "bangzi", 0.8, "写上“辅”")

    def guo(c, kk, T):
        t0 = tb(j, k_go)
        g = pop_scale(T - tb(j, k_shi) - 0.2)
        if g <= 0:
            return None
        x, dy, moving = C.walk(T, t0, 1.2, GX, GX + 150, 10)
        with at_pop(c, x, GY + dy, g):
            hy = GY + dy - 290 * 0.8
            gu(c, x, GY + dy, 0.8, ZHIGUO, hat="bun", beard="black", lh=(x - 40, hy + 110) if T >= t0 else None)
            if T >= t0:
                c.drawCircle(x + 60, hy + 120, 46, K.paint(BLUE_FILL))
                c.drawCircle(x + 60, hy + 120, 46, wb.marker(BLUE, 5))
                C.line(c, (x + 20, hy + 70), (x + 60, hy + 80), BLUE, 5)
            name_tag(c, x, GY + dy - 350, "智果", "#3F6B3A", 40)
        return None
    b.custom(j, k_shi, k_shi + 0.3, guo)
    b.hit(j, k_go, "wood_low", 0.65, "智果背包离开")


screen9()


# ================================================================ 屏 10：蓝台宴席，戏弄韩家主人、羞辱家臣；有人劝，他摆手
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_tab = 0
    k_tease = kq(j, wp(13, 2, 0.4), 1)
    k_shame = nx(j, wp(13, 3, 0.4), k_tease)
    k_warn = nx(j, wp(14, 0, 0.5), k_shame)
    k_reply = nx(j, wp(14, 3, 0.2), k_warn)
    YX, HX, DX = cx - 60, cx + 330, cx + 470
    L.note("蓝台", "韩", "魏", "家臣", "防着点", "谁敢找我？")

    def table(c, sc, T):
        with at_pop(c, cx, GY, sc):
            box(c, cx, GY - 130, 1000, 50, "#C98B4B", "#7A4A1E", 6, 8)
            for i, x in enumerate((cx - 330, cx - 110, cx + 110, cx + 330)):
                cup(c, x, GY - 160, 1.0)
            name_tag(c, cx - 380, cy - 470, "蓝台宴", "#7A4A1E", 44)
        return None
    ev(j, k_tab, L.pop_fn(j, k_tab, table), "muyu", 0.6)

    def guests(c, kk, T):
        g = pop_scale(T - tb(j, k_tab) - 0.2)
        if g <= 0:
            return None
        tt, ts = tb(j, k_tease), tb(j, k_shame)
        with at_pop(c, HX, GY, g):
            gu(c, HX, GY, 0.82, HAN, hat="guan", beard="black", mood="angry" if T >= tt else "flat")
            name_tag(c, HX, GY - 370, "韩", "#2F5B8E", 40)
        with at_pop(c, cx - 430, GY, g):
            gu(c, cx - 430, GY, 0.82, WEI, hat="guan", mood="o" if T >= tt else "flat")
            name_tag(c, cx - 430, GY - 370, "魏", "#8A5A1E", 40)
        if T >= ts:
            gs = pop_scale(T - ts)
            with at_pop(c, DX, GY, gs):
                gu(c, DX, GY, 0.6, "gray", hat="bun", mood="sad", head_dx=8)
                name_tag(c, DX, GY - 270, "家臣", "#5E5E58", 34)
        return None
    b.custom(j, k_tab, k_tab + 0.3, guests)

    def yao(c, kk, T):
        g = pop_scale(T - tb(j, k_tab) - 0.35)
        if g <= 0:
            return None
        tt, tw, tr = tb(j, k_tease), tb(j, k_warn), tb(j, k_reply)
        hy = GY - 290 * 0.95
        rh = (YX + 170, hy - 30) if tt <= T < tw else ((YX + 120, hy - 150 + 20 * math.sin((T - tr) * 10)) if T >= tr else None)
        with at_pop(c, YX, GY, g):
            gu(c, YX, GY, 0.95, ZHIYAO, hat="guan", mood="laugh" if T >= tt else "smile", rh=rh,
               lh=(YX - 110, hy + 60))
            cup(c, YX - 110, hy + 90, 0.7)
        if T >= tt:
            K.text(c, "哈哈", YX - 170, hy - 110, 54, "hand", RED, clamp01((T - tt) / 0.2) * (1 if T < tw else 0.4))
        return None
    b.custom(j, k_tab, k_tab + 0.3, yao)
    b.hit(j, k_tease, "rim", 0.75, "戏弄韩家主人")
    b.hit(j, k_shame, "tom", 0.7, "家臣低头")

    def talk(c, kk, T):
        tw, tr = tb(j, k_warn), tb(j, k_reply)
        if T >= tw:
            g = pop_scale(T - tw)
            with K.at(c, cx + 300, cy - 380, 0, g):
                bubble_box(c, 0, 0, 300, 120, -1)
                K.text(c, "防着点", 0, 0, 54, "hand", INK)
        if T >= tr:
            g = C.slam_scale(T - tr)
            with K.at(c, YX - 200, cy - 230, -3, g):
                bubble_box(c, 0, 0, 380, 140, 1)
                K.text(c, "谁敢找我？", 0, 0, 58, "hand", RED)
        return None
    b.custom(j, k_warn, k_warn + 0.3, talk)
    b.hit(j, k_warn, "pop", 0.6, "有人劝")
    b.hit(j, k_reply, "kick", 0.75, "谁敢找我")


screen10()


# ================================================================ 屏 11：地图上韩、魏各送一座万户之城，赵家不给
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    k_map = 0
    k_han = kq(j, wp(15, 2, 0.3), 1)
    k_wei = nx(j, wp(15, 2, 0.9), k_han)
    k_zhao = nx(j, wp(16, 0, 0.4), k_wei)
    k_no = nx(j, wp(16, 1, 0.4), k_zhao)
    L.note("智", "韩", "魏", "赵", "万户", "不给")
    REG = dict(智=(cx - 40, cy - 180, 360, 300, "#E6D6EE", "#6B3F7A"), 韩=(cx - 330, cy + 250, 330, 250, "#D4E1F2", "#2F5B8E"),
               魏=(cx + 250, cy + 250, 330, 250, "#F0DDB8", "#8A5A1E"), 赵=(cx + 330, cy - 250, 300, 300, "#F4CFC8", "#9C2F25"))

    def mapf(c, kk, T):
        g = pop_scale(T - tb(j, k_map), 0.4)
        if g <= 0:
            return None
        with at_pop(c, cx, cy, g):
            for nm, (x, y, w, h, fill, line) in REG.items():
                rr = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
                c.drawRoundRect(rr, 50, 50, K.paint(fill))
                c.drawRoundRect(rr, 50, 50, wb.marker(line, 6))
                K.text(c, nm, x - w / 2 + 60, y - h / 2 + 60, 64, "serif_black", line)
        return None
    ev(j, k_map, mapf, "wood_low", 0.7)

    def towns(c, kk, T):
        for nm, k_ in (("韩", k_han), ("魏", k_wei)):
            x0, y0 = REG[nm][0] + 30, REG[nm][1] + 20
            x1, y1 = REG["智"][0] + (-90 if nm == "韩" else 90), REG["智"][1] + 60
            t0 = tb(j, k_)
            f = ease_in_out(clamp01((T - t0) / 0.5)) if T >= t0 else 0
            x, y = lerp(x0, x1, f), lerp(y0, y1, f) - 80 * math.sin(math.pi * f)
            with K.at(c, x, y, 0, 1):
                city_wall(c, 0, 50, 150, 90, 1.0)
                K.text(c, "万户", 0, 90, 34, "hand", INK)
            if 0 < f < 1:
                C.line(c, (x0, y0), (x, y), RED, 5, 0.5)
        return None
    b.custom(j, k_map + 0.4, k_map + 0.6, towns)
    b.hit(j, k_han, "tom", 0.75, "韩家送城")
    b.hit(j, k_wei, "tom", 0.75, "魏家送城")

    def zhao(c, kk, T):
        t0 = tb(j, k_zhao)
        x, y = REG["赵"][0], REG["赵"][1]
        if T >= t0:
            f = ease_out(clamp01((T - t0) / 0.4))
            c.drawPath(P((REG["智"][0] + 160, REG["智"][1] - 60), (lerp(REG["智"][0] + 160, x - 140, f),
                                                                     lerp(REG["智"][1] - 60, y, f))), wb.marker("#6B3F7A", 8))
        tn = tb(j, k_no)
        if T >= tn:
            seal(c, x + 10, y + 30, "不给", 70, -8, C.slam_scale(T - tn))
        return None
    b.custom(j, k_zhao, k_zhao + 0.4, zhao, sfx="wood_high", gain=0.7)
    b.hit(j, k_no, "kick", 0.85, "赵家不给")
    b.shots[j].shake = [(k_no, 8.0)]


screen11()


# ================================================================ 屏 12：晋阳城被围、水一格格涨；灶台泡在水里，冒出青蛙
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 330
    k_wall = 0
    k_flags = kq(j, wp(17, 0, 0.5), 1)
    k_w = [nx(j, wp(17, 2, 0.2), k_flags)]
    k_w.append(nx(j, wp(18, 0, 0.5), k_w[0]))
    k_frog = nx(j, wp(18, 2, 0.3), k_w[1])
    L.note("晋阳", "智", "韩", "魏", "呱")
    WH = 520

    def wall(c, sc, T):
        with at_pop(c, cx, GY, sc):
            city_wall(c, cx + 60, GY, 760, WH, label="晋阳")
        return None
    ev(j, k_wall, L.pop_fn(j, k_wall, wall), "muyu", 0.7)

    def flags(c, kk, T):
        for i, (ch, x, col) in enumerate((("智", cx - 500, "#6B3F7A"), ("韩", cx - 470, "#2F5B8E"), ("魏", cx + 470, "#8A5A1E"))):
            g = pop_scale(T - tb(j, k_flags) - i * 0.12)
            if g > 0:
                flag(c, x, GY + 100 - (i == 1) * 0, 0.7 * g, ch, col, 1.0, math.sin(T * 3 + i))
        return None
    ev(j, k_flags, flags, "bangzi", 0.75)

    def flood(c, kk, T):
        lv = 0.0
        for q, k_ in enumerate(k_w):
            t0 = tb(j, k_)
            if T >= t0:
                lv = lerp(lv, (0.45, 0.82)[q], ease_out(clamp01((T - t0) / 0.6)))
        if lv <= 0:
            return None
        level = GY - WH * lv
        water(c, cx - 580, cx + 580, level, GY + 260, T, 0.72)
        return None
    b.custom(j, k_w[0], k_w[0] + 0.4, flood)
    for k_ in k_w:
        b.hit(j, k_, "shaker", 0.75, "水位上涨")

    def stove(c, kk, T):
        t0 = tb(j, k_frog)
        g = pop_scale(T - t0 + 0.15)
        if g <= 0:
            return None
        x, y = cx + 350, cy - 420
        with K.at(c, x, y, 0, g):
            c.drawCircle(0, 0, 150, K.paint("#FFFFFF"))
            c.drawCircle(0, 0, 150, wb.marker(INK, 6))
            c.save()
            c.clipRect(skia.Rect.MakeXYWH(-150, -150, 300, 300))
            box(c, 0, 60, 180, 90, "#C9A97A", "#7A5E3A", 5, 8)
            c.drawRect(skia.Rect.MakeXYWH(-150, 20, 300, 140), K.paint(WATER, 0.7))
            C.line(c, (-150, 20), (150, 20), WATER_LINE, 5)
            fg = pop_scale(T - t0)
            if fg > 0:
                with K.at(c, 0, 0, 0, fg):
                    c.drawOval(skia.Rect.MakeXYWH(-46, -40, 92, 64), K.paint("#7DBE6A"))
                    c.drawOval(skia.Rect.MakeXYWH(-46, -40, 92, 64), wb.marker("#2E6B2A", 5))
                    for sg in (-1, 1):
                        c.drawCircle(sg * 22, -44, 14, K.paint("#FFFFFF"))
                        c.drawCircle(sg * 22, -44, 14, wb.marker("#2E6B2A", 4))
                        c.drawCircle(sg * 22, -44, 5, K.paint(BLACK))
            c.restore()
            if T >= t0:
                K.text(c, "呱", 170, -120, 64, "hand", GREEN, clamp01((T - t0) / 0.2))
        return None
    ev(j, k_frog, stove, "pop", 0.8)


screen12()


# ================================================================ 屏 13：车上智瑶指着水大笑；后面韩、魏用胳膊肘互碰，各想起自家城边的河
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 470
    k_car = 0
    k_laugh = kq(j, wp(19, 3, 0.3), 1)
    k_nudge = nx(j, wp(20, 1, 0.4), k_laugh)
    k_think = nx(j, wp(20, 2, 0.5), k_nudge)
    L.note("水能灭国", "安邑", "平阳", "智瑶", "韩", "魏")
    CX = cx - 40

    def car(c, kk, T):
        g = pop_scale(T - tb(j, k_car), 0.4)
        if g <= 0:
            return None
        with at_pop(c, CX, GY, g):
            for wx in (CX - 190, CX + 190):
                c.drawCircle(wx, GY - 80, 80, K.paint("#FFFFFF"))
                c.drawCircle(wx, GY - 80, 80, wb.marker("#7A4A1E", 8))
                for q in range(4):
                    a = math.radians(q * 45 + T * 40)
                    C.line(c, (wx - 70 * math.cos(a), GY - 80 - 70 * math.sin(a)),
                           (wx + 70 * math.cos(a), GY - 80 + 70 * math.sin(a)), "#7A4A1E", 4)
            box(c, CX, GY - 175, 560, 60, "#C98B4B", "#7A4A1E", 6, 8)
            tl, tn = tb(j, k_laugh), tb(j, k_nudge)
            hy = GY - 205 - 290 * 0.72
            gu(c, CX + 170, GY - 205, 0.72, ZHIYAO, hat="guan", mood="laugh" if T >= tl else "smile",
               rh=(CX + 330, hy - 40) if T >= tl else None)
            nud = 0 if T < tn else math.sin(clamp01((T - tn) / 0.35) * math.pi)
            gu(c, CX - 40, GY - 205, 0.62, WEI, hat="guan", mood="o" if T >= tn else "flat",
               lh=(CX - 110 - 0 * nud, GY - 330), rh=(CX + 40 + 40 * nud, GY - 330))
            gu(c, CX - 200, GY - 205, 0.62, HAN, hat="guan", beard="black", mood="o" if T >= tn else "flat",
               rh=(CX - 120 - 10 * nud, GY - 330), head_dx=-6 * nud)
            name_tag(c, CX + 170, GY - 520, "智瑶", "#6B3F7A", 36)
            name_tag(c, CX - 40, GY - 470, "魏", "#8A5A1E", 32)
            name_tag(c, CX - 200, GY - 470, "韩", "#2F5B8E", 32)
        if T >= tb(j, k_nudge):
            K.burst(c, CX - 120, GY - 330, T - tb(j, k_nudge), ORANGE, 10, 50, 5, 4, 0.8)
        return None
    ev(j, k_car, car, "muyu", 0.6, 0.4)
    water_ = lambda c, kk, T: water(c, cx - 580, cx + 580, GY + 10, GY + 140, T, 0.6) or None  # noqa: E731
    b.custom(j, 0, 0.2, water_)

    def laugh(c, kk, T):
        tl = tb(j, k_laugh)
        if T >= tl:
            g = C.slam_scale(T - tl)
            with K.at(c, CX + 360, cy - 230, 4, g):
                bubble_box(c, 0, 0, 380, 140, -1)
                K.text(c, "水能灭国", 0, 0, 62, "hand", RED)
        return None
    ev(j, k_laugh, laugh, "rim", 0.8)
    b.hit(j, k_nudge, "wood_high", 0.75, "胳膊肘一碰")

    def think(c, kk, T):
        t0 = tb(j, k_think)
        for i, (nm, x) in enumerate((("平阳", cx - 380), ("安邑", cx - 30))):
            g = pop_scale(T - t0 - i * 0.18)
            if g <= 0:
                continue
            with K.at(c, x, cy - 420, 0, g):
                c.drawOval(skia.Rect.MakeXYWH(-160, -110, 320, 220), K.paint("#FFFFFF"))
                c.drawOval(skia.Rect.MakeXYWH(-160, -110, 320, 220), wb.marker(GRAY, 5))
                city_wall(c, -40, 75, 150, 80)
                p = skia.Path()
                p.moveTo(70, -90)
                p.cubicTo(30, -30, 120, 10, 60, 90)
                c.drawPath(p, wb.marker(WATER_LINE, 12))
                K.text(c, nm, -40, -55, 40, "serif_black", INK)
            for q in range(2):
                c.drawCircle(x + 60 + q * 30, cy - 280 + q * 40, 12 - q * 3, wb.marker(GRAY, 4, clamp01(g)))
        return None
    ev(j, k_think, think, "pop", 0.75)


screen13()


# ================================================================ 屏 14：张孟谈夜里出城“唇亡齿寒”；掘开堤坝，水反灌智营，韩魏两边夹击
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_out = 0
    k_say = kq(j, wp(21, 2, 0.3), 1)
    k_dike = nx(j, wp(22, 0, 0.5), k_say)
    k_flood = nx(j, wp(22, 1, 0.5), k_dike)
    k_side = nx(j, wp(22, 2, 0.4), k_flood)
    k_end = nx(j, wp(22, 3, 0.4), k_side)
    L.note("唇亡齿寒", "智", "韩", "魏", "灭族")

    def night(c, kk, T):
        g = pop_scale(T - tb(j, k_out))
        if g <= 0:
            return None
        GL = cy - 60
        c.drawCircle(cx + 470, cy - 480, 46, K.paint(NOTE_FILL, g))
        c.drawCircle(cx + 488, cy - 494, 40, K.paint(PARCH, g))
        city_wall(c, cx - 440, GL, 220, 300, g)
        x, dy, _ = C.walk(T, tb(j, k_out), 1.4, cx - 440, cx - 200, 8)
        with at_pop(c, x, GL + dy, g):
            gu(c, x, GL + dy, 0.62, ZHAO, hat="bun")
            name_tag(c, x, GL - 250 + dy, "赵家使者", "#9C2F25", 30)
        tsay = tb(j, k_say)
        if T >= tsay:
            gs = pop_scale(T - tsay)
            with K.at(c, cx + 10, cy - 450, 0, gs):
                bubble_box(c, 0, 0, 360, 130, -1)
                K.text(c, "唇亡齿寒", 0, 0, 60, "hand", RED)
            for i, (nm, col, x2) in enumerate((("韩", HAN, cx + 220), ("魏", WEI, cx + 400))):
                gg = pop_scale(T - tsay - 0.1 * i)
                with at_pop(c, x2, GL, gg):
                    gu(c, x2, GL, 0.55, col, hat="guan", mood="o")
                    name_tag(c, x2, GL - 230, nm, "#2F5B8E" if nm == "韩" else "#8A5A1E", 30)
        return None
    ev(j, k_out, night, "wood_low", 0.6)
    b.hit(j, k_say, "bangzi", 0.75, "唇亡齿寒")

    def battle(c, kk, T):
        td, tf, ts, te = tb(j, k_dike), tb(j, k_flood), tb(j, k_side), tb(j, k_end)
        g = pop_scale(T - td)
        if g <= 0:
            return None
        DY = GY - 40
        # 堤坝（左）与智营帐篷（右）
        with at_pop(c, cx - 360, DY, g):
            dike = P((cx - 560, DY), (cx - 470, DY - 170), (cx - 260, DY - 170), (cx - 170, DY), close=True)
            c.drawPath(dike, K.paint("#C9A97A"))
            c.drawPath(dike, wb.marker("#7A5E3A", 7))
        if T >= td:
            f = ease_out(clamp01((T - td) / 0.3))
            c.drawPath(P((cx - 380, DY - 170), (cx - 360, DY - 120 * f), (cx - 340, DY - 160), (cx - 320, DY - 60 * f)),
                       wb.marker(RED, 8))
        for i, x in enumerate((cx + 60, cx + 270)):
            tent = P((x - 110, DY), (x, DY - 190), (x + 110, DY), close=True)
            c.drawPath(tent, K.paint("#E6D6EE"))
            c.drawPath(tent, wb.marker("#6B3F7A", 7))
        flag(c, cx + 400, DY, 0.5, "智", "#6B3F7A", 1.0, math.sin(T * 3))
        if T >= tf:
            f = ease_in_out(clamp01((T - tf) / 0.7))
            xr = lerp(cx - 300, cx + 540, f)
            water(c, cx - 300, xr, DY - 60 - 40 * (1 - f), DY + 40, T, 0.75, 14)
        if T >= ts:
            for sg, col in ((-1, "#2F5B8E"), (1, "#8A5A1E")):
                f = ease_out(clamp01((T - ts) / 0.4))
                x0 = cx + 165 + sg * 360
                xa = lerp(x0, cx + 165 + sg * 160, f)
                ya = DY - 290
                c.drawPath(wb.arrow((x0, ya), (xa, ya + 60 * f), 0.2, 40), wb.marker(col, 12))
        if T >= te:
            seal(c, cx - 360, cy + 150, "灭族", 74, 6, C.slam_scale(T - te))
        return None
    b.custom(j, k_dike, k_dike + 0.3, battle)
    b.hit(j, k_dike, "tom", 0.8, "掘开堤坝")
    b.hit(j, k_flood, "shaker", 0.8, "水反灌智营")
    b.hit(j, k_side, "rim", 0.8, "韩魏两边夹击")
    b.hit(j, k_end, "kick", 0.9, "智家灭族")
    b.shots[j].shake = [(k_end, 10.0)]


screen14()


# ================================================================ 屏 15：族谱一格格熄灭，只剩“辅”那一格亮着
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    k_tree = 0
    k_off = [kq(j, wp(23, 0, 0.6), 1)]
    k_off.append(nx(j, wp(23, 1, 0.5), k_off[0]))
    k_fu = nx(j, wp(23, 2, 0.3), k_off[1])
    L.note("智氏", "辅")
    top = (cx, cy - 400)
    kids = [(cx - 450 + i * 180, cy - 80) for i in range(6)]
    grand = [(x + dx, cy + 200) for x, _ in kids for dx in (-45, 45)]
    FU = (cx + 380, cy + 420)

    def tree(c, kk, T):
        g = pop_scale(T - tb(j, k_tree), 0.4)
        if g <= 0:
            return None
        t1, t2, tf = tb(j, k_off[0]), tb(j, k_off[1]), tb(j, k_fu)
        with at_pop(c, cx, cy, g):
            for (x, y) in kids:
                C.line(c, top, (x, y), GRAY, 4)
            for i, (x, y) in enumerate(grand):
                C.line(c, kids[i // 2], (x, y), GRAY, 3)
            C.line(c, top, FU, GREEN, 4)
            box(c, top[0], top[1], 200, 110, "#E6D6EE", "#6B3F7A", 6, 12)
            K.text(c, "智氏", top[0], top[1] + 2, 60, "serif_black", "#6B3F7A")
            for i, (x, y) in enumerate(kids + grand):
                off_t = t1 + (i % 6) * 0.06 if i < 6 else t2 + (i % 6) * 0.05
                dead = T >= off_t
                c.drawCircle(x, y, 40 if i < 6 else 28, K.paint(GRAY_FILL if dead else "#E6D6EE"))
                c.drawCircle(x, y, 40 if i < 6 else 28, wb.marker(GRAY if dead else "#6B3F7A", 5))
                if dead:
                    r = 22 if i < 6 else 15
                    C.line(c, (x - r, y - r), (x + r, y + r), GRAY, 4)
                    C.line(c, (x + r, y - r), (x - r, y + r), GRAY, 4)
            lit = T >= tf
            box(c, FU[0], FU[1], 170, 110, GREEN_FILL if lit else "#FFFFFF", GREEN, 7, 14)
            K.text(c, "辅", FU[0], FU[1] + 2, 70, "serif_black", GREEN)
        if T >= tf:
            sparkle(c, FU[0], FU[1], T - tf, YELLOW, 12, 100, 200)
            gg = pop_scale(T - tf)
            with at_pop(c, FU[0] - 260, cy + 560, gg):
                gu(c, FU[0] - 260, cy + 560, 0.6, ZHIGUO, hat="bun", beard="black", mood="flat")
        return None
    ev(j, k_tree, tree, "muyu", 0.7, 0.4)
    b.hit(j, k_off[0], "tom", 0.75, "一支支熄灭")
    b.hit(j, k_off[1], "tom", 0.7, "又一片熄灭")
    b.hit(j, k_fu, "bianzhong", 0.8, "只剩辅氏")


screen15()


# ================================================================ 屏 16：司马光与天平：才重德轻，“才胜德”；才越大，翘得越高
def screen16(j=16):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_sm = 0
    k_scale = kq(j, wp(24, 1, 0.2), 1)
    k_stamp = nx(j, wp(24, 2, 0.3), k_scale)
    k_grow = nx(j, wp(25, 0, 0.6), k_stamp)
    k_bad = nx(j, wp(25, 2, 0.4), k_grow)
    SX = cx - 400
    PX, PY = cx + 160, cy - 160
    L.note("司马光", "才", "德", "才胜德", "坏事")

    def sima(c, sc, T):
        with at_pop(c, SX, GY, sc):
            gu(c, SX, GY, 0.9, "gray", hat="futou", beard="white", rh=(SX + 140, GY - 300))
            name_tag(c, SX, GY - 420, "司马光", "#5E5E58", 40)
        return None
    ev(j, k_sm, L.pop_fn(j, k_sm, sima), "muyu", 0.65)

    def balance(c, kk, T):
        g = pop_scale(T - tb(j, k_scale))
        if g <= 0:
            return None
        tg, tbd = tb(j, k_grow), tb(j, k_bad)
        grow = ease_out(clamp01((T - tg) / 0.5)) if T >= tg else 0
        tilt = (14 + 8 * grow) * ease_out(clamp01((T - tb(j, k_scale)) / 0.5))
        with at_pop(c, PX, GY, g):
            C.line(c, (PX, GY - 40), (PX, PY), "#7A5E3A", 12)
            box(c, PX, GY - 30, 220, 40, "#C9A97A", "#7A5E3A", 6, 8)
            with K.at(c, PX, PY, -tilt):
                C.line(c, (-330, 0), (330, 0), "#7A5E3A", 12)
                c.drawCircle(0, 0, 16, K.paint("#7A5E3A"))
                for sg, lab, size, col in ((-1, "才", 1.0 + 0.6 * grow, ORANGE), (1, "德", 0.6, GREEN)):
                    px = sg * 300
                    with K.at(c, px, 0, tilt):
                        C.line(c, (0, 0), (-70, 150), GRAY, 4)
                        C.line(c, (0, 0), (70, 150), GRAY, 4)
                        C.line(c, (-90, 150), (90, 150), GRAY, 8)
                        bw = 110 * size
                        box(c, 0, 150 - bw / 2 - 4, bw, bw, "#FFFFFF", col, 7, 12)
                        K.text(c, lab, 0, 150 - bw / 2, 70 * size, "serif_black", col)
        if T >= tbd:
            gb = pop_scale(T - tbd)
            with K.at(c, PX - 300, GY - 120, 0, gb):
                c.drawPath(wb.arrow((0, 0), (-60, 180), 0.1, 36), wb.marker(RED, 10))
                K.text(c, "坏事", 90, 120, 56, "hand", RED)
        return None
    ev(j, k_scale, balance, "wood_high", 0.7)
    b.hit(j, k_grow, "tom", 0.75, "才越来越大")
    b.hit(j, k_bad, "rim", 0.75, "坏事也大")
    L.stamp_ev(j, k_stamp, "才胜德", cx + 200, cy - 440, 84, -5, "kick", 0.9)
    b.shots[j].shake = [(k_stamp, 9.0)]


screen16()


# ================================================================ 屏 17：四种人：圣人、君子、小人、愚人；宁要老实人，也别用小人
def screen17(j=17):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    k_grid = kq(j, wp(26, 0, 0.3), 0)
    k_cards = nx(j, wp(26, 1, 0.5), k_grid)
    k_ok = nx(j, wp(26, 2, 0.6), k_cards)
    k_no = nx(j, wp(26, 3, 0.5), k_ok)
    CARDS = [("圣人", "才德都好", cx - 260, cy - 260), ("君子", "德胜才", cx + 260, cy - 260),
             ("小人", "才胜德", cx - 260, cy + 200), ("愚人", "本事平平", cx + 260, cy + 200)]
    L.note(*[a for a, *_ in CARDS], *[s for _, s, *_ in CARDS], "宁可")

    def cards(c, kk, T):
        for i, (nm, sub, x, y) in enumerate(CARDS):
            t0 = tb(j, k_grid if i < 2 else k_cards) + (i % 2) * 0.12
            g = pop_scale(T - t0)
            if g <= 0:
                continue
            with K.at(c, x, y, 0, g):
                hot = i == 2 and T >= tb(j, k_no)
                good = i == 3 and T >= tb(j, k_ok)
                box(c, 0, 0, 440, 360, RED_FILL if hot else (GREEN_FILL if good else "#FFFFFF"),
                    RED if hot else (GREEN if good else "#7A5E3A"), 7, 20)
                K.text(c, nm, 0, -60, 96, "serif_black", INK)
                K.text(c, sub, 0, 80, 54, "hand", "#5E4128")
        to, tn = tb(j, k_ok), tb(j, k_no)
        if T >= to:
            c.drawPath(check(cx + 420, cy + 60, 60), wb.marker(GREEN, 14))
            K.text(c, "宁可", cx + 260, cy + 440, 60, "hand", GREEN, clamp01((T - to) / 0.2))
        if T >= tn:
            f = ease_out(clamp01((T - tn) / 0.25))
            c.drawPath(wb.partial(cross(cx - 260, cy + 200, 150), f)[0], wb.marker(RED, 16))
        return None
    ev(j, k_grid, cards, "wood_high", 0.7)
    b.hit(j, k_cards, "wood_high", 0.7, "下面两张")
    b.hit(j, k_ok, "ding", 0.8, "宁可要老实人")
    b.hit(j, k_no, "kick", 0.85, "小人打叉")
    b.shots[j].shake = [(k_no, 8.0)]


screen17()


# ================================================================ 屏 18：说回我们：小李叹气，一只手拍拍他的肩；“三招”
def screen18(j=18):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_sigh = kq(j, wp(27, 1, 0.3), 1)
    k_pat = nx(j, wp(27, 2, 0.4), k_sigh)
    k_3 = nx(j, wp(28, 1, 0.5), k_pat)
    LX = cx - 140
    L.note("唉", "三招")

    def li(c, sc, T):
        tp = tb(j, k_pat)
        with at_pop(c, LX, GY, sc):
            desk(c, LX - 40, GY - 170, 420)
            draw_li(c, LX, GY, 1.0, "sad" if T < tp else "flat")
        if T >= tb(j, k_sigh):
            K.text(c, "唉", LX - 300, cy - 200, 96, "hand", GRAY, clamp01((T - tb(j, k_sigh)) / 0.2) * (1 if T < tp else 0.4))
        if T >= tp:
            g = pop_scale(T - tp)
            hx, hy = head_of(LX, GY, 1.0)
            pat = 12 * math.sin(clamp01((T - tp) / 0.6) * math.pi * 3)
            with K.at(c, LX + 260, hy + 60 + pat, -30, g):
                C.line(c, (40, 0), (260, 60), BLUE, 18)
                c.drawRoundRect(skia.Rect.MakeXYWH(-50, -30, 100, 70), 30, 30, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-50, -30, 100, 70), 30, 30, wb.marker(BLACK, 6))
        return None
    ev(j, k_li, L.pop_fn(j, k_li, li), "wood_low", 0.6)
    b.hit(j, k_sigh, "wood_high", 0.6, "叹气")
    b.hit(j, k_pat, "clap", 0.7, "拍拍肩")
    L.stamp_ev(j, k_3, "三招", cx + 280, cy - 300, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen18()


def steps_row(jj, active):
    """顶上三枚圆章“一 二 三”，当前一招亮红。"""
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


# ================================================================ 屏 19：第一招：对领导笑、对保洁冷脸；放大镜照冷脸那边
def screen19(j=19):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 0)
    GY = cy + 520
    k_boss = kq(j, wp(29, 1, 0.4), 1)
    k_cold = nx(j, wp(29, 3, 0.2), k_boss)
    k_lens = nx(j, wp(29, 3, 0.8), k_cold)
    L.note("用不上的人")
    BX, AX1, AX2, CX_ = cx - 450, cx - 220, cx + 160, cx + 420

    def left(c, sc, T):
        with at_pop(c, BX, GY, sc):
            draw_boss(c, BX, GY, 0.85, mood="smile")
            draw_ace(c, AX1, GY, 0.85, mood="laugh", rh=(AX1 - 120, GY - 230))
        return None
    ev(j, k_boss, L.pop_fn(j, k_boss, left), "pop", 0.65)

    def right(c, sc, T):
        with at_pop(c, AX2, GY, sc):
            draw_ace(c, AX2, GY, 0.85, mood="cold", chin=1)
            hy = GY - 290 * 0.8
            draw_li(c, CX_, GY, 0.8, "sad", rh=(CX_ - 70, hy + 30))
            C.line(c, (CX_ - 70, hy + 30), (CX_ - 140, GY), "#8B6B43", 8)
            c.drawOval(skia.Rect.MakeXYWH(CX_ - 190, GY - 20, 100, 30), K.paint(BLUE_FILL))
        return None
    ev(j, k_cold, L.pop_fn(j, k_cold, right), "wood_low", 0.7)

    def lens(c, kk, T):
        t0 = tb(j, k_lens)
        g = pop_scale(T - t0)
        if g <= 0:
            return None
        x = lerp(cx - 300, AX2 + 60, ease_in_out(clamp01((T - t0) / 0.5)))
        with K.at(c, x, cy - 160, 0, g):
            c.drawCircle(0, 0, 120, K.paint("#FFFFFF", 0.25))
            c.drawCircle(0, 0, 120, wb.marker(BLACK, 10))
            C.line(c, (85, 85), (190, 190), BLACK, 18)
        if T >= t0 + 0.5:
            K.text(c, "用不上的人", CX_ - 20, cy - 360, 58, "hand", RED, clamp01((T - t0 - 0.5) / 0.2))
        return None
    ev(j, k_lens, lens, "ding", 0.8)


screen19()


# ================================================================ 屏 20：第二招：学智果留后路——分工、功劳写进共享文档
def screen20(j=20):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 1)
    k_guo = kq(j, wp(30, 0, 0.6), 1)
    k_doc = nx(j, wp(30, 1, 0.5), k_guo)
    k_rows = nx(j, wp(30, 2, 0.4), k_doc)
    k_save = nx(j, wp(30, 3, 0.4), k_rows)
    ROWS = [("方案", "小李"), ("数据", "小王"), ("汇报", "他")]
    L.note("分工表", "存档", *[f"{a}：{b_}" for a, b_ in ROWS])

    def guo(c, sc, T):
        x, y = cx - 400, cy + 100
        with at_pop(c, x, y, sc):
            c.drawCircle(x, y - 150, 170, K.paint("#F7EFD9"))
            c.drawCircle(x, y - 150, 170, wb.marker("#9C7A3A", 5))
            gu(c, x, y, 0.8, ZHIGUO, hat="bun", beard="black", lh=(x - 40, y - 120))
            c.drawCircle(x + 55, y - 120, 40, K.paint(BLUE_FILL))
            c.drawCircle(x + 55, y - 120, 40, wb.marker(BLUE, 5))
            name_tag(c, x, y + 60, "智果", "#3F6B3A", 40)
        return None
    ev(j, k_guo, L.pop_fn(j, k_guo, guo), "muyu", 0.6)

    def doc(c, kk, T):
        g = pop_scale(T - tb(j, k_doc))
        if g <= 0:
            return None
        x, y = cx + 220, cy + 60
        with K.at(c, x, y, 0, g):
            box(c, 0, 0, 600, 640, "#FFFFFF", BLUE, 8, 20)
            c.drawRect(skia.Rect.MakeXYWH(-300, -320, 600, 90), K.paint(BLUE_FILL))
            K.text(c, "分工表", 0, -274, 52, "sans_medium", BLUE)
            for i, (a, b_) in enumerate(ROWS):
                t0 = tb(j, k_rows) + i * 0.15
                gg = clamp01((T - t0) / 0.2)
                if gg <= 0:
                    continue
                yy = -150 + i * 120
                c.drawRoundRect(skia.Rect.MakeXYWH(-260, yy - 44, 520, 88), 14, 14, K.paint(GREEN_FILL, gg))
                K.text(c, f"{a}：{b_}", -230, yy, 52, "hand", INK, gg, "left")
                c.drawPath(check(200, yy, 26), wb.marker(GREEN, 8, gg))
        return None
    ev(j, k_doc, doc, "pop", 0.7)
    b.hit(j, k_rows, "shaker", 0.7, "一行行写上")
    L.seal_ev(j, k_save, "存档", cx + 380, cy + 330, 58, "kick", 0.85, -8)


screen20()


# ================================================================ 屏 21：第三招：本事涨了，也给别人留余地——小李伸手拉新人一把
def screen21(j=21):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 2)
    GY = cy + 520
    k_li = kq(j, wp(31, 0, 0.6), 1)
    k_up = nx(j, wp(31, 1, 0.5), k_li)
    k_hand = nx(j, wp(31, 2, 0.6), k_up)
    LX, NX_ = cx - 120, cx + 330
    L.note("本事")

    def li(c, sc, T):
        tu, th = tb(j, k_up), tb(j, k_hand)
        up = ease_out(clamp01((T - tu) / 0.5)) if T >= tu else 0
        s = 0.9 + 0.12 * up
        hy = GY - 290 * s
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, s, "smile", rh=(LX + 150, hy + 140) if T >= th else None)
        # 本事条
        bx, by = cx - 470, cy - 220
        box(c, bx, by + 100, 70, 420, "#FFFFFF", GRAY, 5, 12)
        hgt = 140 + 240 * up
        c.drawRoundRect(skia.Rect.MakeXYWH(bx - 26, by + 300 - hgt, 52, hgt), 12, 12, K.paint(ORANGE))
        K.text(c, "本事", bx, by - 150, 50, "hand", ORANGE)
        if T >= tu:
            c.drawPath(wb.arrow((bx + 70, by + 160), (bx + 70, by - 40), 0.0, 30), wb.marker(ORANGE, 8))
        if T >= th:
            g = pop_scale(T - th)
            with at_pop(c, NX_, GY, g):
                newbie(c, NX_, GY, 0.8, "smile", lh=(NX_ - 110, GY - 290 * 0.8 + 140))
            sparkle(c, (LX + NX_) / 2, GY - 300, T - th, YELLOW, 8, 50, 110)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, li), "wood_low", 0.6)
    b.hit(j, k_up, "tom", 0.7, "本事涨了")
    b.hit(j, k_hand, "ding", 0.8, "伸手拉新人一把")


screen21()


# ================================================================ 屏 22：好处：一条路，坑被跨过去，越走越长
def screen22(j=22):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 420
    k_road = 0
    k_hole = kq(j, wp(32, 0, 0.5), 1)
    k_jump = nx(j, wp(32, 0, 0.95), k_hole)
    k_long = nx(j, wp(32, 1, 0.5), k_jump)
    L.note("坑")
    HX = cx - 60

    def road(c, kk, T):
        g = clamp01((T - tb(j, k_road)) / 0.5)
        if g <= 0:
            return None
        tl = tb(j, k_long)
        ext = ease_out(clamp01((T - tl) / 0.6)) if T >= tl else 0
        far_y = lerp(cy - 120, cy - 460, ext)
        p = P((cx - 560, GY + 160), (cx - 150, far_y), (cx + 150, far_y), (cx + 560, GY + 160), close=True)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(cx - 600, lerp(GY + 160, far_y - 10, g), cx + 600, GY + 200))
        c.drawPath(p, K.paint("#E7D6BA"))
        c.drawPath(p, wb.marker("#8B6B43", 6))
        c.restore()
        th = tb(j, k_hole)
        if T >= th:
            gh = pop_scale(T - th)
            with K.at(c, HX, GY + 20, 0, gh):
                c.drawOval(skia.Rect.MakeXYWH(-120, -36, 240, 72), K.paint("#5E4128"))
                K.text(c, "坑", 0, 90, 56, "hand", "#5E4128")
        if T >= tl:
            sparkle(c, cx, far_y, T - tl, YELLOW, 10, 60, 140)
        return None
    b.custom(j, k_road, k_road + 0.5, road, sfx="wood_low", gain=0.6)
    b.hit(j, k_hole, "tom", 0.7, "路上的坑")

    def li(c, kk, T):
        tj = tb(j, k_jump)
        f = ease_in_out(clamp01((T - tj) / 0.6)) if T >= tj else 0
        x = lerp(cx - 400, cx + 300, f)
        y = GY + 60 - 180 * math.sin(math.pi * f)
        s = lerp(0.85, 0.7, f)
        g = pop_scale(T - tb(j, k_road) - 0.3)
        if g <= 0:
            return None
        with at_pop(c, x, y, g):
            draw_li(c, x, y, s, "smile")
        return None
    b.custom(j, k_road, k_road + 0.3, li)
    b.hit(j, k_jump, "pop", 0.75, "跨过坑")
    b.hit(j, k_long, "ding", 0.75, "路越走越长")


screen22()


# ================================================================ 屏 23：评论区；小李手里一杆秤；下一讲预告
def screen23(j=23):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z_))
    k_cmt = 0
    k_chips = nx(j, wp(34, 1, 0.3), 0)
    k_scale = nx(j, wp(35, 1, 0.3), k_chips)
    k_even = nx(j, wp(35, 3, 0.3), k_scale)
    k_next = nx(j, wp(36, 1, 0.2), k_even)
    b.move(j, k_scale, (cx, cy + 380, Z_), 1.1)
    CH = ["抢功的组长", "甩锅的同学", "我自己也有过"]
    L.note("你碰到过才胜德的人吗？", *CH, "下一讲", "说出去的话", "为什么没人当真？", "才", "德", "踏实")
    BY = cy - 330

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 20, BY, 0, sc):
            bubble_box(c, 0, 0, 1000, 360, -1)
            K.text(c, "你碰到过才胜德的人吗？", 0, -110, 58, "hand", RED)
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

    LX, LY = cx - 200, cy + 640

    def li(c, kk, T):
        g = pop_scale(T - tb(j, k_scale))
        if g <= 0:
            return None
        te = tb(j, k_even)
        even = ease_out(clamp01((T - te) / 0.5)) if T >= te else 0
        s = 0.95
        hx, hy = head_of(LX, LY, s)
        hand = (LX + 140, hy + 40)
        with at_pop(c, LX, LY, g):
            draw_li(c, LX, LY, s, "smile" if even else "flat", rh=hand)
            ang = lerp(12, 0, even)
            with K.at(c, hand[0] + 120, hand[1] - 10, ang):
                C.line(c, (-200, 0), (200, 0), "#8B4A1E", 10)
                C.line(c, (-120, 0), (-120, -20), "#8B4A1E", 6)
                for sg, lab, col in ((-1, "才", ORANGE), (1, "德", GREEN)):
                    px = sg * 190
                    with K.at(c, px, 0, -ang):
                        C.line(c, (0, 0), (0, 100), GRAY, 4)
                        c.drawCircle(0, 140, 44, K.paint("#FFFFFF"))
                        c.drawCircle(0, 140, 44, wb.marker(col, 6))
                        K.text(c, lab, 0, 142, 50, "serif_black", col)
            C.line(c, (hand[0] + 120 - 120, hand[1] - 10), (hand[0], hand[1]), "#8B4A1E", 6)
        if even:
            sparkle(c, LX + 260, hy - 60, T - te, YELLOW, 10, 60, 130)
            K.text(c, "踏实", LX + 330, LY - 40, 76, "hand", GREEN, clamp01((T - te - 0.2) / 0.2))
        return None
    ev(j, k_scale, li, "wood_low", 0.6)
    b.hit(j, k_even, "ding", 0.8, "秤放平了")

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
            K.text(c, "说出去的话", -120, -60, 58, "hand", BLACK)
            K.text(c, "为什么没人当真？", -60, 40, 58, "hand", BLACK)
            with K.at(c, 390, 20, -12 + 6 * math.sin((T - t0) * 3)):
                box(c, 0, 0, 40, 210, "#C98B4B", "#7A4A1E", 5, 8)
                for q in range(3):
                    C.line(c, (-14, -70 + q * 60), (14, -60 + q * 60), "#7A4A1E", 3)
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen23()

# ================================================================ 收尾
L.finish(cover_shot=13, square_shot=16, notes=NOTES)
L.export(globals())
