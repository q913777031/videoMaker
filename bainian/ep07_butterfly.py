"""《百年孤独》07 黄蝴蝶：爱一个人，为什么变成了管着他？（白板手绘 + AI 旁白，竖屏 2:3）

两人对比：书里的母亲费尔南达用规矩把女儿梅梅越管越紧——不准她和身边总绕着黄蝴蝶的修车小伙子来往，
请人守夜，小伙子被一枪打中瘫在床上，梅梅被送进修道院再没开口——守住了规矩，失去了女儿；
今天换一种做法的爸妈：先问、再商量、留一块他做主的地方。文案见 bainian/PLAN.md「### 07」。
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
from bainian.lesson import (BLACK, BLUE, BLUE_FILL, BUTTER, GRAY, GREEN, GREEN_FILL, INK, NOTE_FILL, ORANGE, RED, RED_FILL,
                            YELLOW, at_pop, box, bubble_box, butterfly, chip, draw_lady, draw_li, draw_man, draw_wang, name_tag,
                            phone, pop_scale, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "生活里", 1),
    ([2], "生活里", 2),
    ([3, 4], "书里的人", 3),
    ([5, 6], "黄蝴蝶", 4),
    ([7], "不准", 5),
    ([8], "夜里", 6),
    ([9, 10], "守夜", 7),
    ([11, 12], "沉默", 8),
    ([13], "说回我们", 9),
    ([14], "说回我们", 10),
    ([15], "第一步", 11),
    ([16], "第二步", 12),
    ([17], "第三步", 13),
    ([18], "好处", 14),
    ([19, 20, 21, 22], "评论区见", 15),
]

THEME = BT.get("07")
L = N.Lesson("07", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(14)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》第 14 章（范晔译本）。情节为转述，不引原文；开枪一段画面只画“砰”字和四散的蝴蝶。",
    "今人（小李、小王、孩子）为虚构示意；书中人造型为示意（一百多年前的加勒比小镇打扮）。",
]

FER = ("费尔南达", "梅梅的母亲")
MEME = ("梅梅", "第五代 · 女儿")
MAU = ("马乌里西奥·巴比伦", "修车的小伙子")


def tag(c, x, y, who, color, a=1.0, size=40):
    name_tag(c, x, y, who[0], color, size, a, who[1])


def fernanda(c, x, y, s, **kw):
    """费尔南达：一身黑裙、发髻。"""
    draw_lady(c, x, y, s, "black", hair="bun", **kw)


def meme(c, x, y, s, **kw):
    """梅梅：黄裙、长发。"""
    draw_lady(c, x, y, s, "yellow", hair="long", **kw)


def mauricio(c, x, y, s, **kw):
    """马乌里西奥·巴比伦：蓝色工装、小胡子。"""
    kw.setdefault("beard", "mustache")
    draw_man(c, x, y, s, "blue", vest="#2F5B8E", **kw)


def swarm(c, x, y, T, n=6, r=150, a=1.0, scatter=0.0):
    for q in range(n):
        ang = T * 1.3 + q * 2 * math.pi / n
        rr = r * (1 + 2.5 * scatter) + 20 * math.sin(T * 3 + q)
        butterfly(c, x + rr * math.cos(ang), y + rr * 0.6 * math.sin(ang), 0.55, T + q, a * (1 - scatter))


def kid(c, x, y, s=0.6, mood="smile", **kw):
    draw_li(c, x, y, s, mood, **kw)


def lock(c, x, y, s=1.0, a=1.0):
    with K.at(c, x, y, 0, s):
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(-50, -110, 100, 110), 180, 180)
        c.drawPath(arc, wb.marker(GRAY, 14, a))
        box(c, 0, 20, 160, 130, "#C9CED6", BLACK, 6, 14, a)
        c.drawCircle(0, 10, 14, K.paint(BLACK, a))


def heart(c, x, y, r, a=1.0):
    c.drawPath(C.heart_path(x, y, r), K.paint(RED_FILL, a))
    c.drawPath(C.heart_path(x, y, r), wb.marker(RED, 6, a))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：妈妈举着手机看小李的聊天；后来小李当了爸爸，同样举着手机
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_mom = kq(j, wp(0, 1, 0.3), 0)
    k_ph = nx(j, wp(0, 2, 0.4), k_mom)
    k_clock = nx(j, wp(0, 4, 0.3), k_ph)
    k_dad = nx(j, wp(1, 0, 0.5), k_clock)
    k_same = nx(j, wp(1, 2, 0.4), k_dad)
    L.note("22:00", "报备")

    def scene(c, kk, T):
        tm, tp, tc, td, ts = (tb(j, k) for k in (k_mom, k_ph, k_clock, k_dad, k_same))
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        if T < td:
            MX, LX = cx - 250, cx + 250
            with at_pop(c, MX, GY, g):
                draw_wang(c, MX, GY, 1.0, mood="flat", rh=(MX + 130, GY - 330) if T >= tp else None)
            if T >= tp:
                phone(c, MX + 150, GY - 360, 0.8)
            with at_pop(c, LX, GY, g):
                draw_li(c, LX, GY, 0.85, "sad")
            if T >= tc:
                with K.at(c, cx, cy - 400, 0, pop_scale(T - tc)):
                    box(c, 0, 0, 320, 110, "#FFFFFF", RED, 6, 14)
                    K.text(c, "22:00", -40, 0, 56, "hand", RED)
                    K.text(c, "报备", 100, 0, 40, "hand", INK)
            return None
        f = pop_scale(T - td)
        DX, KX = cx - 200, cx + 260
        with at_pop(c, DX, GY, f):
            draw_li(c, DX, GY, 1.0, "flat", rh=(DX + 130, GY - 330) if T >= ts else None)
        if T >= ts:
            phone(c, DX + 150, GY - 360, 0.8)
            K.text(c, "又是这样", cx + 200, cy - 380, 56, "hand", ORANGE, clamp01((T - ts) / 0.3))
        with at_pop(c, KX, GY, f):
            kid(c, KX, GY, 0.6, "sad")
        return None
    L.note("又是这样")
    ev(j, k_mom, scene, "wood_high", 0.65)
    b.hit(j, k_ph, "pop", 0.7, "手机要看")
    b.hit(j, k_clock, "rim", 0.75, "几点回家要报备")
    b.hit(j, k_dad, "wood_low", 0.65, "自己当了爸妈")
    b.hit(j, k_same, "pop", 0.75, "又这样管孩子")


screen1()


# ================================================================ 屏 2（drop）：一颗心慢慢变成一把锁
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    dk = L.drop_k()
    k_heart = kq(j, wp(2, 0, 0.3), 0)
    L.note("爱", "管")

    def scene(c, kk, T):
        th, td = tb(j, k_heart), tb(j, dk)
        g = pop_scale(T - th)
        if g <= 0:
            return None
        f = ease_in_out(clamp01((T - td) / 0.3)) if T >= td else 0
        heart(c, cx, cy - 80, 220 * g, 1 - f)
        K.text(c, "爱", cx, cy - 60, 120, "hand", RED, (1 - f) * g)
        if T >= td:
            with K.at(c, cx, cy - 60, 0, C.slam_scale(T - td) * 2.2):
                lock(c, 0, 0, 1.0)
            K.text(c, "管", cx, cy + 360, 120, "hand", INK, clamp01((T - td) / 0.2))
        return None
    ev(j, k_heart, scene, "ding", 0.6)
    b.hit(j, dk, "kick", 0.9, "爱变成管")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：绿皮书翻开；黑裙的费尔南达，手里一张长长的规矩单
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(3, 0, 0.4), 0)
    k_fer = nx(j, wp(3, 1, 0.4), k_book)
    k_list = nx(j, wp(4, 0, 0.4), k_fer)
    k_long = nx(j, wp(4, 2, 0.4), k_list)
    KT.book(j, k_book, x=cx - 360, y=cy - 300)
    RULES = ["吃饭不许出声", "说话要轻", "裙子过膝", "天黑前回家", "……"]
    L.note(*FER, "规矩", *RULES)
    FX = cx + 60

    def scene(c, kk, T):
        tf, tl, tlg = tb(j, k_fer), tb(j, k_list), tb(j, k_long)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        with at_pop(c, FX, GY, g):
            fernanda(c, FX, GY, 1.0, mood="flat", rh=(FX + 150, GY - 260))
        tag(c, FX, GY - 470, FER, "#3A3A3A", clamp01(g), 42)
        if T >= tl:
            n = len(RULES) if T >= tlg else 2
            h = 90 + n * 70
            top = cy - 120
            with K.at(c, FX + 330, top, 0, pop_scale(T - tl)):
                box(c, 0, h / 2, 300, h, "#FFFFFF", "#8B6B43", 5, 6)
                K.text(c, "规矩", 0, 40, 44, "serif_black", RED)
                for i in range(n):
                    K.text(c, RULES[i], 0, 100 + i * 70, 32, "hand", INK)
        return None
    ev(j, k_fer, scene, "bongo_low", 0.7)
    b.hit(j, k_list, "wood_high", 0.65, "规矩单")
    b.hit(j, k_long, "shaker", 0.75, "样样有规矩")


screen3()


# ================================================================ 屏 4：梅梅和修车小伙子见面，他身边绕着一群黄蝴蝶
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_meme = kq(j, wp(5, 0, 0.4), 0)
    k_mau = nx(j, wp(5, 2, 0.4), k_meme)
    k_fly = nx(j, wp(6, 2, 0.3), k_mau)
    L.note(*MEME, *MAU)
    MX, UX = cx - 280, cx + 240

    def scene(c, kk, T):
        tm, tu, tfl = tb(j, k_meme), tb(j, k_mau), tb(j, k_fly)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        with at_pop(c, MX, GY, g):
            meme(c, MX, GY, 0.95, mood="smile")
        tag(c, MX, GY - 450, MEME, "#9C7A1A", clamp01(g))
        if T >= tu:
            with at_pop(c, UX, GY, pop_scale(T - tu)):
                mauricio(c, UX, GY, 1.0, mood="smile", rh=(UX + 120, GY - 140))
                C.line(c, (UX + 120, GY - 140), (UX + 190, GY - 230), "#8A8F99", 12)
            tag(c, UX + 40, GY - 490, MAU, "#2F5B8E", clamp01((T - tu) / 0.3), 34)
            heart(c, cx - 20, cy - 60, 50 * pop_scale(T - tu - 0.2))
        if T >= tfl:
            swarm(c, UX, cy - 40, T - tfl, 7, 220, clamp01((T - tfl) / 0.4))
        return None
    ev(j, k_meme, scene, "bongo_high", 0.7)
    b.hit(j, k_mau, "pop", 0.7, "修车的小伙子")
    b.hit(j, k_fly, "ding", 0.85, "一群黄蝴蝶")


screen4()


# ================================================================ 屏 5：费尔南达在两人中间竖起一道墙
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_fer = kq(j, wp(7, 0, 0.5), 0)
    k_shame = nx(j, wp(7, 1, 0.4), k_fer)
    k_wall = nx(j, wp(7, 2, 0.2), k_shame)
    L.note("丢人", "不准")

    def scene(c, kk, T):
        tf, ts, tw = tb(j, k_fer), tb(j, k_shame), tb(j, k_wall)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        meme(c, cx - 380, GY, 0.85, mood="sad" if T >= tw else "smile")
        mauricio(c, cx + 400, GY, 0.85, mood="flat")
        swarm(c, cx + 400, cy + 60, T, 5, 140)
        with at_pop(c, cx, GY, g):
            fernanda(c, cx, GY, 1.0, mood="angry")
        if T >= ts:
            with K.at(c, cx + 230, cy - 330, 0, pop_scale(T - ts)):
                bubble_box(c, 0, 0, 220, 110, -1)
                K.text(c, "丢人", 0, 0, 56, "hand", RED)
        if T >= tw:
            h = 700 * ease_out(clamp01((T - tw) / 0.4))
            for sg in (-1, 1):
                x = cx + sg * 170
                box(c, x, GY - h / 2, 60, h, "#B5562E", "#5E2E18", 6, 4)
            with K.at(c, cx, cy - 480, 0, C.slam_scale(T - tw)):
                chip(c, 0, 0, "不准", RED_FILL, RED, 66)
        return None
    ev(j, k_fer, scene, "wood_low", 0.65)
    b.hit(j, k_shame, "rim", 0.75, "丢人")
    b.hit(j, k_wall, "kick", 0.85, "不准来往")


screen5()


# ================================================================ 屏 6：月亮；浴室的小窗，黄蝴蝶从缝里钻进去
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_moon = kq(j, wp(8, 0, 0.5), 0)
    k_night = nx(j, wp(8, 1, 0.4), k_moon)
    k_in = nx(j, wp(8, 2, 0.4), k_night)
    L.note("夜里")

    def scene(c, kk, T):
        tm, tn, ti = tb(j, k_moon), tb(j, k_night), tb(j, k_in)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        c.drawCircle(cx + 380, cy - 430, 70 * g, K.paint("#F6E7A6"))
        c.drawCircle(cx + 410, cy - 450, 60 * g, K.paint(N.PARCH))
        K.text(c, "夜里", cx - 380, cy - 440, 60, "hand", BLUE, clamp01(g))
        with K.at(c, cx - 80, GY - 30, 0, g):
            N.house(c, 0, 0, 520, 420)
        WX, WY = cx - 80 + 156, GY - 30 - 420 + 85
        if T >= tn:
            c.drawRect(skia.Rect.MakeXYWH(WX - 40, WY - 35, 80, 70), K.paint(YELLOW, 0.8))
        if T >= ti:
            for q in range(4):
                f = clamp01((T - ti - q * 0.2) / 0.8)
                x = lerp(cx + 450, WX, ease_in_out(f))
                y = lerp(cy - 100 + q * 60, WY, ease_in_out(f)) - 60 * math.sin(f * math.pi)
                butterfly(c, x, y, 0.6 * (1 - 0.6 * f), T + q, 1 - f * 0.8)
        return None
    ev(j, k_moon, scene, "wood_low", 0.6)
    b.hit(j, k_night, "pop", 0.65, "夜里偷偷")
    b.hit(j, k_in, "ding", 0.8, "在浴室见面")


screen6()


# ================================================================ 屏 7：守夜人提着灯；一声“砰”，黄蝴蝶四散
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_ask = kq(j, wp(9, 0, 0.5), 0)
    k_thief = nx(j, wp(9, 1, 0.5), k_ask)
    k_guard = nx(j, wp(9, 2, 0.3), k_thief)
    k_bang = nx(j, wp(10, 1, 0.5), k_guard)
    k_bed = nx(j, wp(10, 2, 0.4), k_bang)
    L.note("偷鸡贼", "砰")

    def scene(c, kk, T):
        ta, tt, tg, tbng, tbd = (tb(j, k) for k in (k_ask, k_thief, k_guard, k_bang, k_bed))
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        if T < tbd:
            with at_pop(c, cx - 380, GY, g):
                fernanda(c, cx - 380, GY, 0.85, mood="flat", rh=(cx - 250, GY - 300))
            if T >= tt:
                with K.at(c, cx - 200, cy - 360, 0, pop_scale(T - tt)):
                    bubble_box(c, 0, 0, 300, 110, 1)
                    K.text(c, "偷鸡贼", 0, 0, 56, "hand", RED)
            if T >= tg:
                GX = cx + 120
                with at_pop(c, GX, GY, pop_scale(T - tg)):
                    draw_man(c, GX, GY, 0.95, "gray", hat="straw", mood="flat", rh=(GX + 130, GY - 220))
                c.drawCircle(GX + 140, GY - 200, 60, K.paint(YELLOW, 0.4))
                box(c, GX + 140, GY - 190, 40, 60, "#FFF1A8", ORANGE, 4, 6)
            sc_ = clamp01((T - tbng) / 0.8) if T >= tbng else 0
            swarm(c, cx + 380, cy - 200, T, 6, 120, 1, sc_)
            if T >= tbng:
                with K.at(c, cx + 330, cy - 380, -6, C.slam_scale(T - tbng)):
                    K.text(c, "砰", 0, 0, 160, "hand", RED)
            return None
        f = pop_scale(T - tbd)
        with K.at(c, cx, GY - 140, 0, f):
            box(c, 0, 0, 640, 140, "#FFFFFF", INK, 6, 12)
            box(c, -250, -60, 120, 80, "#FFFFFF", INK, 5, 20)
        with K.at(c, cx - 230, GY - 230, -90, f):
            mauricio(c, 0, 0, 0.7, mood="sad")
        butterfly(c, cx + 200, cy - 120, 0.6, T, 0.7)
        K.text(c, "瘫在床上", cx + 160, cy - 300, 56, "hand", GRAY, f)
        return None
    L.note("瘫在床上")
    ev(j, k_ask, scene, "wood_low", 0.6)
    b.hit(j, k_thief, "rim", 0.75, "说是偷鸡贼")
    b.hit(j, k_guard, "wood_high", 0.6, "请人守夜")
    b.hit(j, k_bang, "kick", 0.9, "一枪打中")
    b.hit(j, k_bed, "xiaoluo", 0.7, "瘫在床上")


screen7()


# ================================================================ 屏 8：修道院高墙，梅梅嘴上一道线；费尔南达手里只剩规矩单
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_wall = kq(j, wp(11, 1, 0.4), 0)
    k_mute = nx(j, wp(11, 3, 0.3), k_wall)
    k_rule = nx(j, wp(12, 0, 0.5), k_mute)
    k_lost = nx(j, wp(12, 1, 0.5), k_rule)
    L.note("修道院", "规矩")

    def scene(c, kk, T):
        tw, tm, tr, tl = (tb(j, k) for k in (k_wall, k_mute, k_rule, k_lost))
        g = pop_scale(T - tw)
        if g <= 0:
            return None
        WX = cx + 230
        with K.at(c, WX, GY - 300, 0, g):
            box(c, 0, 0, 520, 600, "#E2E2DE", "#5E5E58", 7, 6)
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(-80, -260, 160, 160), 180, 180)
            c.drawPath(arc, wb.marker("#5E5E58", 6))
            K.text(c, "修道院", 0, -340, 48, "serif_black", "#5E5E58")
        hy = GY - 290 * 0.85
        meme(c, WX, GY, 0.85, mood="flat")
        if T >= tm:
            C.line(c, (WX - 16, hy + 20), (WX + 16, hy + 20), BLACK, 8)
            K.text(c, "……", WX + 120, hy - 60, 60, "hand", GRAY, clamp01((T - tm) / 0.3))
        if T >= tr:
            FX = cx - 320
            with at_pop(c, FX, GY, pop_scale(T - tr)):
                fernanda(c, FX, GY, 0.95, mood="flat" if T < tl else "sad", rh=(FX + 140, GY - 250))
            with K.at(c, FX + 170, GY - 330, 4, 1):
                box(c, 0, 0, 160, 220, "#FFFFFF", "#8B6B43", 5, 6)
                K.text(c, "规矩", 0, -70, 40, "serif_black", RED)
        if T >= tl:
            with K.at(c, cx - 140, cy - 330, 0, pop_scale(T - tl)):
                c.drawPath(C.heart_path(0, 0, 60), wb.marker(GRAY, 6))
                C.line(c, (-10, -50), (12, 50), GRAY, 6)
        return None
    ev(j, k_wall, scene, "xiaoluo", 0.7)
    b.hit(j, k_mute, "wood_low", 0.65, "再没开口")
    b.hit(j, k_rule, "wood_high", 0.6, "守住了规矩")
    b.hit(j, k_lost, "tom", 0.8, "失去了女儿")


screen8()


# ================================================================ 屏 9：小李当了爸爸，心口一个“怕”字
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_dad = kq(j, wp(13, 0, 0.4), 0)
    k_fear = nx(j, wp(13, 1, 0.4), k_dad)
    k_two = nx(j, wp(13, 2, 0.3), k_fear)
    L.note("怕", "吃亏", "走错路")

    def scene(c, kk, T):
        td, tf, t2 = tb(j, k_dad), tb(j, k_fear), tb(j, k_two)
        g = pop_scale(T - td)
        if g <= 0:
            return None
        DX = cx - 200
        with at_pop(c, DX, GY, g):
            draw_li(c, DX, GY, 1.0, "flat")
            kid(c, DX + 300, GY, 0.6, "smile")
        if T >= tf:
            with K.at(c, DX + 170, GY - 420, 0, C.slam_scale(T - tf)):
                K.text(c, "怕", 0, 0, 110, "hand", RED)
        if T >= t2:
            for i, s in enumerate(("吃亏", "走错路")):
                with K.at(c, cx + 300, cy - 340 + i * 140, 0, pop_scale(T - t2 - 0.15 * i)):
                    chip(c, 0, 0, s, "#D9DCE1", GRAY, 50)
        return None
    ev(j, k_dad, scene, "wood_low", 0.6)
    b.hit(j, k_fear, "rim", 0.8, "多半是怕")
    b.hit(j, k_two, "pop", 0.65, "怕吃亏怕走错路")


screen9()


# ================================================================ 屏 10：锁慢慢变回一颗心；大字“三步”
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_lock = kq(j, wp(14, 0, 0.4), 0)
    k_three = nx(j, wp(14, 1, 0.5), k_lock)
    L.note("三步")

    def scene(c, kk, T):
        tl, t3 = tb(j, k_lock), tb(j, k_three)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        f = ease_in_out(clamp01((T - tl - 0.3) / 0.8))
        lock(c, cx, cy - 200, 1.6 * g, 1 - f)
        heart(c, cx, cy - 200, 150 * f, f)
        if T >= t3:
            with K.at(c, cx, cy + 300, -3, C.slam_scale(T - t3)):
                K.text(c, "三步", 0, 0, 150, "hand", RED)
        return None
    ev(j, k_lock, scene, "ding", 0.65)
    b.hit(j, k_three, "kick", 0.85, "三步")


screen10()


# ================================================================ 屏 11：第一步：小李蹲下来问孩子“你怎么想？”
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_ask = kq(j, wp(15, 0, 0.6), 1)
    k_worry = nx(j, wp(15, 1, 0.5), k_ask)
    L.note("你怎么想？", "我担心……")

    def scene(c, kk, T):
        ta, tw = tb(j, k_ask), tb(j, k_worry)
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        DX, KX = cx - 200, cx + 180
        with at_pop(c, DX, GY, g):
            draw_li(c, DX, GY, 0.9, "smile", squash=0.8)
        with at_pop(c, KX, GY, g):
            kid(c, KX, GY, 0.62, "smile")
        with K.at(c, cx - 160, cy - 160, 0, g):
            bubble_box(c, 0, 0, 340, 110, -1)
            K.text(c, "你怎么想？", 0, 0, 52, "hand", BLUE)
        if T >= tw:
            with K.at(c, cx + 220, cy - 360, 0, pop_scale(T - tw)):
                bubble_box(c, 0, 0, 320, 110, -1)
                K.text(c, "我担心……", 0, 0, 50, "hand", INK)
        return None
    ev(j, k_ask, scene, "pop", 0.7)
    b.hit(j, k_worry, "wood_high", 0.65, "再说担心什么")


screen11()


# ================================================================ 屏 12：第二步：规矩单从一个人写变成两个人一起写
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_list = kq(j, wp(16, 0, 0.6), 1)
    k_talk = nx(j, wp(16, 1, 0.5), k_list)
    k_both = nx(j, wp(16, 2, 0.5), k_talk)
    L.note("命令", "商量", "我们的约定", "周末玩1小时", "九点前说一声")

    def scene(c, kk, T):
        tl, tt, tb2 = tb(j, k_list), tb(j, k_talk), tb(j, k_both)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 80, 0, g):
            box(c, 0, 0, 560, 520, "#FFFFFF", BLACK, 7, 12)
            if T < tt:
                K.text(c, "命令", 0, -180, 60, "serif_black", RED)
            else:
                K.text(c, "我们的约定", 0, -180, 56, "hand", GREEN, clamp01((T - tt) / 0.3))
            if T >= tb2:
                K.text(c, "周末玩1小时", 0, -40, 48, "hand", INK, clamp01((T - tb2) / 0.3))
                K.text(c, "九点前说一声", 0, 60, 48, "hand", INK, clamp01((T - tb2 - 0.2) / 0.3))
        if T >= tt:
            with K.at(c, cx + 320, cy + 260, 0, C.slam_scale(T - tt)):
                chip(c, 0, 0, "商量", GREEN_FILL, GREEN, 56)
        if T >= tb2:
            draw_li(c, cx - 340, GY, 0.8, "smile", rh=(cx - 220, GY - 300))
            kid(c, cx - 80, GY, 0.55, "smile")
        return None
    ev(j, k_list, scene, "wood_high", 0.65)
    b.hit(j, k_talk, "pop", 0.75, "换成商量")
    b.hit(j, k_both, "ding", 0.8, "一起定")


screen12()


# ================================================================ 屏 13：第三步：画一个小圈写“你做主”，孩子在圈里搭积木，倒了又搭
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 500
    k_ring = kq(j, wp(17, 1, 0.4), 1)
    k_fall = nx(j, wp(17, 2, 0.4), k_ring)
    k_again = nx(j, wp(17, 2, 0.9), k_fall)
    L.note("你做主")

    def scene(c, kk, T):
        tr, tf, ta = tb(j, k_ring), tb(j, k_fall), tb(j, k_again)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        ring = skia.Path()
        ring.addOval(skia.Rect.MakeXYWH(cx - 360, GY - 70, 720, 160))
        c.drawPath(wb.partial(ring, ease_out(clamp01((T - tr) / 0.5)))[0], wb.marker(GREEN, 8))
        K.text(c, "你做主", cx + 340, cy - 120, 60, "hand", GREEN, g)
        kid(c, cx - 150, GY + 20, 0.62, "o" if tf <= T < ta else "smile")
        fallen = tf <= T < ta
        for q in range(4):
            col = (RED, BLUE, YELLOW, GREEN)[q]
            if fallen:
                x, y, rot = cx + 40 + q * 90, GY + 30, q * 20
            else:
                x, y, rot = cx + 120, GY - 30 - q * 70, 0
            with K.at(c, x, y, rot, g):
                box(c, 0, 0, 90, 64, col, BLACK, 4, 6)
        return None
    ev(j, k_ring, scene, "wood_high", 0.65)
    b.hit(j, k_fall, "tom", 0.7, "错了")
    b.hit(j, k_again, "ding", 0.8, "让他自己试")


screen13()


# ================================================================ 屏 14：好处：孩子凑到小李耳边说悄悄话
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_pair = kq(j, wp(18, 0, 0.6), 0)
    k_ear = nx(j, wp(18, 1, 0.5), k_pair)
    L.note("听得进去")

    def scene(c, kk, T):
        tp, te = tb(j, k_pair), tb(j, k_ear)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        DX = cx - 100
        with at_pop(c, DX, GY, g):
            draw_li(c, DX, GY, 0.95, "smile", squash=0.8)
        kid(c, DX + 160, GY, 0.62, "smile", lh=(DX + 80, GY - 230))
        if T >= te:
            for q in range(3):
                r = 30 + q * 24
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(DX + 60 - r, GY - 260 - r, 2 * r, 2 * r), 140, 80)
                c.drawPath(arc, wb.marker(GREEN, 5))
            with K.at(c, cx + 100, cy - 300, 0, C.slam_scale(T - te)):
                chip(c, 0, 0, "听得进去", GREEN_FILL, GREEN, 60)
            sparkle(c, cx + 100, cy - 300, T - te, YELLOW, 10, 120, 260)
        return None
    ev(j, k_pair, scene, "wood_low", 0.6)
    b.hit(j, k_ear, "ding", 0.85, "他才听得进去")


screen14()


# ================================================================ 屏 15：评论区；一扇窗打开，黄蝴蝶飞进来；下一讲预告
def enc(c, T, te, th, cx, cy):
    WX, WY = cx - 80, cy + 470
    g = pop_scale(T - te)
    with K.at(c, WX, WY, 0, g):
        box(c, 0, 0, 360, 300, "#E9EEF4", "#8B6B43", 8, 8)
        f = ease_out(clamp01((T - th) / 0.5)) if T >= th else 0
        for sg in (-1, 1):
            w = 180 * (1 - 0.7 * f)
            c.drawRect(skia.Rect.MakeXYWH(sg * 180 - (w if sg > 0 else 0), -150, w, 300), K.paint("#B5562E"))
            c.drawRect(skia.Rect.MakeXYWH(sg * 180 - (w if sg > 0 else 0), -150, w, 300), wb.marker("#5E2E18", 5))
    if T >= th:
        for q in range(4):
            u = clamp01((T - th - q * 0.2) / 1.2)
            butterfly(c, lerp(cx + 460, WX, ease_in_out(u)), lerp(cy + 260 + q * 40, WY, u) - 80 * math.sin(u * math.pi), 0.7, T + q)


def mirror_icon(c, x, y, dt):
    with K.at(c, x, y, 0, pop_scale(dt)):
        c.drawRoundRect(skia.Rect.MakeXYWH(-50, -80, 100, 160), 50, 50, K.paint("#E8EEF8"))
        c.drawRoundRect(skia.Rect.MakeXYWH(-50, -80, 100, 160), 50, 50, wb.marker("#8A6A3A", 6))
        c.drawOval(skia.Rect.MakeXYWH(-30, -14, 60, 28), wb.marker(BLACK, 4))
        c.drawCircle(0, 0, 9, K.paint(BLACK))


KT.ending(15, "你被管得最紧的是哪件事？", ["手机", "穿衣", "找对象"], 20, 21, enc, 22, ["太在意", "别人怎么看？"],
          enc_piece=1, next_icon=mirror_icon)

# ================================================================ 收尾
L.finish(cover_shot=4, square_shot=4, notes=NOTES)
L.export(globals())
