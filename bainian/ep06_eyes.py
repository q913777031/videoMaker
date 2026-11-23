"""《百年孤独》06 眼睛：看不清前路的时候，怎么办？（白板手绘 + AI 旁白，竖屏 2:3）

故事贯穿：乌尔苏拉老了眼睛看不见，谁也没告诉，照样操持一大家子；她记下每样东西的位置和每个人的声音，
发现家里人每天走同样的路、做同样的事，跟着习惯就知道东西在哪；费尔南达的结婚戒指丢了，她顺着那天的路一下摸到。
落到“看不清前路”的三步。文案见 bainian/PLAN.md「### 06」。
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
                            at_pop, box, bubble_box, chip, draw_lady, draw_li, draw_man, draw_wang, name_tag, pop_scale,
                            sparkle, ursula)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "生活里", 1),
    ([2], "生活里", 2),
    ([3, 4, 5], "书里的人", 3),
    ([6], "心里的地图", 4),
    ([7, 8], "习惯", 5),
    ([9, 10], "戒指", 6),
    ([11, 12], "没人发现", 7),
    ([13], "说回我们", 8),
    ([14], "第一步", 9),
    ([15], "第二步", 10),
    ([16], "第三步", 11),
    ([17], "好处", 12),
    ([18, 19, 20, 21], "评论区见", 13),
]

THEME = BT.get("06")
L = N.Lesson("06", SCREENS, drop_screen=2, board_size=(5000, 9000), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(12)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》（范晔译本）乌尔苏拉晚年失明的一章。情节为转述，不引原文。",
    "今人（小李、小王）为虚构示意；书中人造型为示意（一百多年前的加勒比小镇打扮）。",
]

URS = ("乌尔苏拉", "第一代 · 母亲")
FER = ("费尔南达", "曾孙媳妇")
FOG = "#D9DCE1"


def tag(c, x, y, who, a=1.0, size=44, color="#2F5B8E"):
    name_tag(c, x, y, who[0], color, size, a, who[1])


def blind_ursula(c, x, y, s, **kw):
    """看不见的乌尔苏拉：花白发髻，眼睛画成两道弯线。"""
    kw.setdefault("mood", "smile")
    ursula(c, x, y, s, old=True, **kw)
    hy = y - 290 * s
    for sg in (-1, 1):
        c.drawCircle(x + sg * 15 * s, hy - 2 * s, 7 * s, K.paint("#FFFFFF"))
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(x + sg * 15 * s - 10 * s, hy - 8 * s, 20 * s, 14 * s), 200, 140)
        c.drawPath(arc, wb.marker(BLACK, 4))


def fog(c, cx, cy, f, a=0.6, seed=0):
    for q in range(10):
        fx = cx - 560 + (q % 4) * 380 + 50 * math.sin(q * 1.7 + seed)
        fy = cy - 520 + (q // 4) * 420 + 40 * math.cos(q + seed)
        w = 600 * f
        c.drawOval(skia.Rect.MakeXYWH(fx - w / 2, fy - w * 0.2, w, w * 0.4), K.paint(FOG, a * f))


def dashed(c, path, color, w=6, a=1.0, on=26, off=18):
    p = wb.marker(color, w, a)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    c.drawPath(path, p)


def ring_icon(c, x, y, s=1.0, a=1.0):
    with K.at(c, x, y, 0, s):
        c.drawCircle(0, 0, 34, wb.marker("#C9A34A", 10, a))
        c.drawPath(P((-14, -36), (0, -56), (14, -36), close=True), K.paint("#9FD3F0", a))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：组织架构图一晃重排，小李的工位卡片被挪走；小李扶着额头
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_org = kq(j, wp(0, 1, 0.4), 0)
    k_shuffle = nx(j, wp(0, 2, 0.4), k_org)
    k_lost = nx(j, wp(0, 3, 0.4), k_shuffle)
    k_tired = nx(j, wp(1, 2, 0.4), k_lost)
    L.note("小李", "往哪走？", "累")

    def scene(c, kk, T):
        to, ts, tl, tt = (tb(j, k) for k in (k_org, k_shuffle, k_lost, k_tired))
        g = pop_scale(T - to)
        if g <= 0:
            return None
        sh = ease_in_out(clamp01((T - ts) / 0.6)) if T >= ts else 0
        top = (cx, cy - 470)
        box(c, top[0], top[1], 200, 90, BLUE_FILL, BLUE, 5, 10, g)
        for i in range(4):
            x0 = cx - 390 + i * 260
            x1 = cx - 390 + ((i * 3 + 1) % 4) * 260
            x = lerp(x0, x1, sh)
            y = cy - 250 + 40 * math.sin(sh * math.pi) * (1 if i % 2 else -1)
            C.line(c, (top[0], top[1] + 45), (x, y - 45), GRAY, 4, g)
            me = i == 2
            if me and T >= tl:
                x, y = lerp(x, cx + 460, ease_out(clamp01((T - tl) / 0.4))), lerp(y, cy - 40, ease_out(clamp01((T - tl) / 0.4)))
            box(c, x, y, 200, 90, NOTE_FILL if me else "#FFFFFF", ORANGE if me else GRAY, 5, 10, g)
            if me:
                K.text(c, "小李", x, y, 40, "hand", INK, g)
        LX = cx - 260
        with at_pop(c, LX, GY, g):
            hy = GY - 290
            draw_li(c, LX, GY, 1.0, "sad" if T >= tt else "o", rh=(LX + 40, hy - 40) if T >= tt else None)
        if T >= tl:
            with K.at(c, cx + 200, cy + 120, 0, pop_scale(T - tl)):
                bubble_box(c, 0, 0, 300, 110, -1)
                K.text(c, "往哪走？", 0, 0, 50, "hand", RED)
        if T >= tt:
            K.text(c, "累", LX + 160, cy + 20, 70, "hand", GRAY, clamp01((T - tt) / 0.3))
        return None
    ev(j, k_org, scene, "wood_high", 0.65)
    b.hit(j, k_shuffle, "shaker", 0.75, "架构一调整")
    b.hit(j, k_lost, "rim", 0.8, "不知道往哪走")
    b.hit(j, k_tired, "wood_low", 0.65, "脑子转不动")


screen1()


# ================================================================ 屏 2（drop）：雾从两边涌上来，前面的路不见了
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_road = kq(j, wp(2, 0, 0.3), 0)
    L.note("不敢迈")

    def scene(c, kk, T):
        tr, td = tb(j, k_road), tb(j, dk)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        road = P((cx - 120, GY + 40), (cx - 40, cy - 100), (cx + 60, cy - 520))
        c.drawPath(road, wb.marker("#C9A46A", 70, 0.8 * g))
        f = ease_out(clamp01((T - tr) / 2.0))
        fog(c, cx, cy, 0.4 + 0.6 * f, 0.75)
        with at_pop(c, cx - 200, GY, g):
            draw_li(c, cx - 200, GY, 1.0, "o" if T >= td else "flat")
        if T >= td:
            with K.at(c, cx + 200, cy + 120, -4, C.slam_scale(T - td)):
                chip(c, 0, 0, "不敢迈", RED_FILL, RED, 64)
        return None
    ev(j, k_road, scene, "shaker", 0.65)
    b.hit(j, dk, "kick", 0.9, "一步也不敢迈")
    b.shots[j].shake = [(dk, 9.0)]
    b.shots[j].flashes = [(dk, 0.22)]


screen2()


# ================================================================ 屏 3：绿皮书翻开；老年乌尔苏拉看不见了，手里照样端着锅；身后一排小名牌
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(3, 0, 0.4), 0)
    k_u = nx(j, wp(3, 1, 0.4), k_book)
    k_eyes = nx(j, wp(3, 2, 0.4), k_u)
    k_pot = nx(j, wp(4, 1, 0.4), k_eyes)
    k_gens = nx(j, wp(5, 1, 0.4), k_pot)
    KT.book(j, k_book, x=cx - 360, y=cy - 300)
    L.note(*URS, "一百多岁", "看不见了")
    UX = cx + 180

    def scene(c, kk, T):
        tu, te, tp, tg = (tb(j, k) for k in (k_u, k_eyes, k_pot, k_gens))
        g = pop_scale(T - tu)
        if g <= 0:
            return None
        if T >= tg:
            for i in range(5):
                x = cx - 480 + i * 140
                s_ = pop_scale(T - tg - i * 0.08)
                if s_ > 0:
                    (draw_man if i % 2 else draw_lady)(c, x, GY, 0.42 * s_, ("red", "green", "yellow", "blue", "purple")[i],
                                                       mood="smile")
            K.text(c, "一百多岁", cx - 200, cy + 80, 54, "hand", ORANGE, clamp01((T - tg) / 0.3))
        with at_pop(c, UX, GY, g):
            if T >= te:
                blind_ursula(c, UX, GY, 1.05, rh=(UX + 150, GY - 230) if T >= tp else None)
            else:
                ursula(c, UX, GY, 1.05, old=True, mood="flat")
        if T >= tp:
            with K.at(c, UX + 190, GY - 250, 0, pop_scale(T - tp)):
                c.drawOval(skia.Rect.MakeXYWH(-70, -10, 140, 60), K.paint("#5E5E58"))
                c.drawOval(skia.Rect.MakeXYWH(-70, -26, 140, 36), K.paint("#8A8F99"))
        tag(c, UX, GY - 480, URS, clamp01(g))
        if T >= te:
            K.text(c, "看不见了", UX + 220, cy - 120, 50, "hand", GRAY, clamp01((T - te) / 0.3))
        return None
    ev(j, k_u, scene, "bongo_low", 0.7)
    b.hit(j, k_eyes, "xiaoluo", 0.65, "眼睛看不见了")
    b.hit(j, k_pot, "wood_high", 0.65, "照样操持")
    b.hit(j, k_gens, "clap", 0.7, "好几代人")


screen3()


# ================================================================ 屏 4：她心里浮出一张屋子的平面图：桌子、门、每个人的声音波纹
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_plan = kq(j, wp(6, 1, 0.4), 0)
    k_items = nx(j, wp(6, 1, 0.9), k_plan)
    k_voice = nx(j, wp(6, 3, 0.3), k_items)
    L.note("门", "桌", "床", "锅", "声音")

    def scene(c, kk, T):
        tp, ti, tv = tb(j, k_plan), tb(j, k_items), tb(j, k_voice)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        blind_ursula(c, cx - 360, GY, 0.85)
        with K.at(c, cx + 150, cy - 160, 0, g):
            box(c, 0, 0, 660, 600, "#FFFFFF", "#8B6B43", 7, 8)
            C.line(c, (-330, 60), (60, 60), "#8B6B43", 6)
            C.line(c, (60, -300), (60, 0), "#8B6B43", 6)
            for i, (s, x, y) in enumerate((("门", -260, 260), ("桌", -150, -150), ("床", 200, -180), ("锅", 220, 190))):
                if T >= ti + i * 0.1:
                    box(c, x, y, 120, 80, NOTE_FILL, ORANGE, 4, 8)
                    K.text(c, s, x, y, 46, "hand", INK)
        if T >= tv:
            for i, (x, y) in enumerate(((cx + 40, cy + 300), (cx + 380, cy + 260))):
                for q in range(3):
                    r = 30 + q * 26 + 10 * math.sin((T - tv) * 6 - q)
                    arc = skia.Path()
                    arc.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -50, 100)
                    c.drawPath(arc, wb.marker(BLUE, 5, clamp01((T - tv) / 0.3)))
            K.text(c, "声音", cx + 220, cy + 420, 54, "hand", BLUE, clamp01((T - tv) / 0.3))
        return None
    ev(j, k_plan, scene, "wood_low", 0.6)
    b.hit(j, k_items, "pop", 0.7, "东西放在哪")
    b.hit(j, k_voice, "ding", 0.75, "每个人的声音")


screen4()


# ================================================================ 屏 5：家里几个人沿着各自的虚线来回走，每天同一条线
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    k_paths = kq(j, wp(7, 2, 0.3), 0)
    k_walk = nx(j, wp(7, 3, 0.4), k_paths)
    k_know = nx(j, wp(8, 1, 0.4), k_walk)
    L.note("秘密", "每天同一条路", "东西在哪")
    ROUTES = [
        (P((cx - 450, cy - 380), (cx - 100, cy - 380), (cx - 100, cy - 100)), "red"),
        (P((cx + 420, cy - 300), (cx + 150, cy - 120), (cx + 300, cy + 120)), "green"),
        (P((cx - 420, cy + 120), (cx - 120, cy + 260), (cx + 200, cy + 330)), "yellow"),
    ]

    def scene(c, kk, T):
        tp, tw, tk = tb(j, k_paths), tb(j, k_walk), tb(j, k_know)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        K.text(c, "秘密", cx + 330, cy - 520, 56, "hand", RED, g)
        for i, (path, col) in enumerate(ROUTES):
            dashed(c, path, GRAY, 6, g)
            if T >= tw:
                u = ((T - tw) * 0.35 + i * 0.3) % 1
                u = 1 - abs(1 - 2 * u)
                (x, y), _ = wb.partial(path, min(0.999, max(0.001, u)))[1], None
                (draw_man if i != 2 else draw_lady)(c, x, y + 90, 0.38, col, mood="flat")
        if T >= tw:
            K.text(c, "每天同一条路", cx, cy + 470, 54, "hand", INK, clamp01((T - tw) / 0.3))
        if T >= tk:
            for i, (path, _) in enumerate(ROUTES):
                ex, ey = wb.partial(path, 0.999)[1]
                with K.at(c, ex, ey, 0, pop_scale(T - tk - 0.1 * i)):
                    c.drawCircle(0, 0, 30, K.paint(YELLOW))
                    c.drawCircle(0, 0, 30, wb.marker(ORANGE, 5))
            with K.at(c, cx + 20, cy - 500, -3, C.slam_scale(T - tk)):
                chip(c, 0, 0, "东西在哪", GREEN_FILL, GREEN, 46)
        return None
    ev(j, k_paths, scene, "pop", 0.65)
    b.hit(j, k_walk, "shaker", 0.7, "同样的路")
    b.hit(j, k_know, "ding", 0.8, "就知道东西在哪")


screen5()


# ================================================================ 屏 6：戒指丢了，全家翻箱倒柜；乌尔苏拉沿着费尔南达的虚线一摸，戒指亮了
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_ring = kq(j, wp(9, 1, 0.4), 0)
    k_search = nx(j, wp(9, 3, 0.3), k_ring)
    k_follow = nx(j, wp(10, 1, 0.4), k_search)
    k_found = nx(j, wp(10, 2, 0.4), k_follow)
    L.note(*FER, "？")
    route = P((cx - 420, cy - 300), (cx - 80, cy - 360), (cx + 150, cy - 150), (cx + 400, cy - 200))

    def scene(c, kk, T):
        tr, ts, tf, tfd = (tb(j, k) for k in (k_ring, k_search, k_follow, k_found))
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        FX = cx - 380
        with at_pop(c, FX, GY, g):
            draw_lady(c, FX, GY, 0.85, "black", hair="bun", mood="sad")
        tag(c, FX, GY - 420, FER, clamp01(g), 38, "#3A3A3A")
        if T < tf:
            ring_icon(c, cx - 220, cy - 380, 1.2 * g, 0.5)
            K.text(c, "？", cx - 120, cy - 420, 70, "hand", RED, g)
        if T >= ts:
            for i in range(3):
                x = cx + 40 + i * 160
                with K.at(c, x, GY - 70, 8 * math.sin((T - ts) * 12 + i), pop_scale(T - ts - 0.1 * i)):
                    box(c, 0, 0, 130, 120, "#E7D6BA", "#8B6B43", 5, 6)
        if T >= tf:
            u = ease_in_out(clamp01((T - tf) / 1.0))
            dashed(c, route, ORANGE, 7)
            x, y = wb.partial(route, min(0.999, max(0.001, u)))[1]
            blind_ursula(c, x, y + 330, 0.6, rh=(x + 60, y + 150))
        if T >= tfd:
            ex, ey = wb.partial(route, 0.999)[1]
            ring_icon(c, ex + 70, ey + 140, 1.4)
            sparkle(c, ex + 70, ey + 140, T - tfd, YELLOW, 10, 60, 160)
        return None
    ev(j, k_ring, scene, "pop", 0.65)
    b.hit(j, k_search, "shaker", 0.75, "全家翻遍")
    b.hit(j, k_follow, "wood_high", 0.65, "顺着那天的路")
    b.hit(j, k_found, "ding", 0.9, "摸到戒指")


screen6()


# ================================================================ 屏 7：一家人围着饭桌，乌尔苏拉在中间笑，没人察觉；她心里的地图亮着
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_table = kq(j, wp(11, 0, 0.5), 0)
    k_none = nx(j, wp(11, 1, 0.5), k_table)
    k_map = nx(j, wp(12, 1, 0.4), k_none)
    L.note("没人发现", "换一种看法")

    def scene(c, kk, T):
        tt, tn, tm = tb(j, k_table), tb(j, k_none), tb(j, k_map)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        with K.at(c, cx, GY - 140, 0, g):
            box(c, 0, 0, 900, 30, "#E7D6BA", "#8B6B43", 6, 6)
            for sg in (-1, 1):
                C.line(c, (sg * 400, 15), (sg * 400, 150), "#8B6B43", 9)
        for i, x in enumerate((cx - 380, cx - 200, cx + 200, cx + 380)):
            (draw_man if i % 2 else draw_lady)(c, x, GY, 0.62, ("red", "green", "yellow", "white")[i], mood="laugh" if T >= tn else "smile")
        with at_pop(c, cx, GY, g):
            blind_ursula(c, cx, GY, 0.8)
        if T >= tn:
            with K.at(c, cx + 250, cy - 330, 4, C.slam_scale(T - tn)):
                chip(c, 0, 0, "没人发现", NOTE_FILL, ORANGE, 52)
        if T >= tm:
            with K.at(c, cx - 250, cy - 320, 0, pop_scale(T - tm)):
                c.drawOval(skia.Rect.MakeXYWH(-180, -110, 360, 220), K.paint("#FFFFFF"))
                c.drawOval(skia.Rect.MakeXYWH(-180, -110, 360, 220), wb.marker(BLUE, 5))
                for q in range(3):
                    dashed(c, P((-130, -50 + q * 45), (130, -30 + q * 45)), ORANGE, 5)
            sparkle(c, cx - 250, cy - 320, T - tm, YELLOW, 10, 120, 240)
        return None
    ev(j, k_table, scene, "wood_low", 0.6)
    b.hit(j, k_none, "pop", 0.75, "没人发现")
    b.hit(j, k_map, "ding", 0.8, "换了一种看的办法")


screen7()


# ================================================================ 屏 8：大雾里，小李手里多了一盏小灯；大字“三步”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_fog = kq(j, wp(13, 1, 0.3), 0)
    k_lamp = nx(j, wp(13, 3, 0.3), k_fog)
    k_three = nx(j, wp(13, 3, 0.95), k_lamp)
    L.note("三步")

    def scene(c, kk, T):
        tf, tl, t3 = tb(j, k_fog), tb(j, k_lamp), tb(j, k_three)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        fog(c, cx, cy, g, 0.7, 2)
        LX = cx - 250
        hy = GY - 290
        draw_li(c, LX, GY, 1.0, "smile" if T >= tl else "flat", rh=(LX + 130, hy + 60) if T >= tl else None)
        if T >= tl:
            s_ = pop_scale(T - tl)
            c.drawCircle(LX + 140, hy + 100, 140 * s_, K.paint(YELLOW, 0.3))
            box(c, LX + 140, hy + 100, 50, 70, "#FFF1A8", ORANGE, 5, 8)
        if T >= t3:
            with K.at(c, cx + 200, cy - 200, -3, C.slam_scale(T - t3)):
                K.text(c, "三步", 0, 0, 150, "hand", RED)
        return None
    ev(j, k_fog, scene, "shaker", 0.6)
    b.hit(j, k_lamp, "ding", 0.75, "乌尔苏拉的办法")
    b.hit(j, k_three, "kick", 0.85, "三步")


screen8()


# ================================================================ 屏 9：第一步：小李摸到三块石头：本事、朋友、家人
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_stones = [kq(j, wp(14, 1, 0.5), 1)]
    k_stones.append(nx(j, wp(14, 2, 0.5), k_stones[0]))
    k_stones.append(nx(j, wp(14, 3, 0.5), k_stones[1]))
    L.note("本事", "朋友", "家人", "不变的东西")

    def scene(c, kk, T):
        t0 = tb(j, k_stones[0])
        g = pop_scale(T - t0)
        if g <= 0:
            return None
        fog(c, cx, cy + 220, 1, 0.45, 3)
        LX = cx - 380
        draw_li(c, LX, GY, 0.9, "smile", rh=(LX + 140, GY - 150))
        for i, (k_, s) in enumerate(zip(k_stones, ("本事", "朋友", "家人"))):
            t = tb(j, k_)
            if T < t:
                continue
            x = cx - 80 + i * 240
            with K.at(c, x, GY - 60, 0, pop_scale(T - t)):
                c.drawOval(skia.Rect.MakeXYWH(-100, -60, 200, 110), K.paint("#C9CED6"))
                c.drawOval(skia.Rect.MakeXYWH(-100, -60, 200, 110), wb.marker(BLACK, 6))
                K.text(c, s, 0, -4, 48, "hand", INK)
        if T >= tb(j, k_stones[2]):
            with K.at(c, cx + 160, cy - 200, 0, C.slam_scale(T - tb(j, k_stones[2]) - 0.2)):
                chip(c, 0, 0, "不变的东西", GREEN_FILL, GREEN, 56)
        return None
    ev(j, k_stones[0], scene, "wood_low", 0.7)
    for k_ in k_stones[1:]:
        b.hit(j, k_, "wood_low", 0.7, "又摸到一块")


screen9()


# ================================================================ 屏 10：第二步：地上一串脚印有节奏地重复，小李跟着走
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_prints = kq(j, wp(15, 1, 0.4), 1)
    k_follow = nx(j, wp(15, 2, 0.5), k_prints)
    k_ok = nx(j, wp(15, 3, 0.4), k_follow)
    L.note("规律", "不迷路")

    def scene(c, kk, T):
        tp, tf, to = tb(j, k_prints), tb(j, k_follow), tb(j, k_ok)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        n = min(8, 1 + int((T - tp) / 0.12))
        for i in range(n):
            x = cx - 480 + i * 130
            y = GY - 40 - (i % 2) * 50
            c.drawOval(skia.Rect.MakeXYWH(x - 24, y - 40, 48, 80), K.paint(BLUE_FILL))
            c.drawOval(skia.Rect.MakeXYWH(x - 24, y - 40, 48, 80), wb.marker(BLUE, 4))
        K.text(c, "规律", cx, cy - 200, 80, "hand", BLUE, g)
        if T >= tf:
            u = ease_in_out(clamp01((T - tf) / 1.4))
            x = lerp(cx - 480, cx + 400, u)
            draw_li(c, x, GY - 80, 0.8, "smile")
        if T >= to:
            with K.at(c, cx + 300, cy - 360, 4, C.slam_scale(T - to)):
                chip(c, 0, 0, "不迷路", GREEN_FILL, GREEN, 56)
        return None
    ev(j, k_prints, scene, "pop", 0.65)
    b.hit(j, k_follow, "shaker", 0.7, "跟着节奏走")
    b.hit(j, k_ok, "ding", 0.8, "不容易迷路")


screen10()


# ================================================================ 屏 11：第三步：雾里只照亮脚下一格；小李举手问路
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_fog = kq(j, wp(16, 1, 0.4), 1)
    k_step = nx(j, wp(16, 2, 0.4), k_fog)
    k_ask = nx(j, wp(16, 3, 0.5), k_step)
    L.note("下一步", "请问？")

    def scene(c, kk, T):
        tf, ts, ta = tb(j, k_fog), tb(j, k_step), tb(j, k_ask)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        fog(c, cx, cy + 220, g, 0.7, 4)
        LX = cx - 200
        if T >= ts:
            s_ = ease_out(clamp01((T - ts) / 0.4))
            c.drawOval(skia.Rect.MakeXYWH(LX + 60, GY - 30, 260 * s_, 70), K.paint(YELLOW, 0.8))
            K.text(c, "下一步", LX + 190, GY + 90, 50, "hand", ORANGE, s_)
        hy = GY - 290
        draw_li(c, LX, GY, 1.0, "smile", rh=(LX + 60, hy - 120) if T >= ta else None)
        if T >= ta:
            with at_pop(c, cx + 330, GY, pop_scale(T - ta)):
                draw_wang(c, cx + 330, GY, 0.9, mood="smile")
            with K.at(c, LX + 120, cy - 120, 0, pop_scale(T - ta)):
                bubble_box(c, 0, 0, 240, 100, -1)
                K.text(c, "请问？", 0, 0, 50, "hand", BLUE)
        return None
    ev(j, k_fog, scene, "shaker", 0.6)
    b.hit(j, k_step, "ding", 0.8, "看清下一步")
    b.hit(j, k_ask, "pop", 0.75, "开口问")


screen11()


# ================================================================ 屏 12：好处：雾慢慢退开，一格一格的路连起来
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_clear = kq(j, wp(17, 1, 0.4), 0)
    k_walk = nx(j, wp(17, 2, 0.4), k_clear)
    L.note("一步一步")

    def scene(c, kk, T):
        tc, tw = tb(j, k_clear), tb(j, k_walk)
        if T < tc:
            return None
        f = ease_out(clamp01((T - tc) / 1.2))
        for i in range(6):
            x = cx - 450 + i * 180
            y = GY - 20 - i * 120
            box(c, x, y, 160, 60, "#C9A46A", "#8A6A3A", 4, 8, clamp01(f * 6 - i))
        fog(c, cx, cy, 1 - 0.8 * f, 0.7, 5)
        u = ease_in_out(clamp01((T - tw) / 1.4)) if T >= tw else 0
        i_ = u * 5
        x = cx - 450 + i_ * 180
        y = GY - 20 - i_ * 120
        draw_li(c, x, y - 30, 0.6, "smile")
        if T >= tw:
            K.text(c, "一步一步", cx - 200, cy - 380, 70, "hand", GREEN, clamp01((T - tw) / 0.3))
        return None
    ev(j, k_clear, scene, "shaker", 0.65)
    b.hit(j, k_walk, "ding", 0.85, "一步一步往前走")


screen12()


# ================================================================ 屏 13：评论区；小李在雾里迈出一小步，脚下亮起；下一讲预告
def enc(c, T, te, th, cx, cy):
    y = cy + 620
    fog(c, cx, cy + 380, 1, 0.45, 6)
    f = ease_out(clamp01((T - th) / 0.4)) if T >= th else 0
    x = lerp(cx - 200, cx + 40, f)
    if T >= th:
        c.drawOval(skia.Rect.MakeXYWH(cx - 80, y - 30, 260, 70), K.paint(YELLOW, 0.8 * f))
        sparkle(c, cx + 50, y, T - th, YELLOW, 10, 60, 180)
    draw_li(c, x, y, 0.85, "smile" if T >= th else "flat")


def butterfly_icon(c, x, y, dt):
    N.butterfly(c, x, y, 1.1 * pop_scale(dt), dt)


KT.ending(13, "你最看不清的是哪件事？", ["换工作", "带孩子", "要不要搬家"], 19, 20, enc, 21, ["爱一个人", "为什么变成了管着他？"],
          enc_piece=1, next_icon=butterfly_icon)

# ================================================================ 收尾
L.finish(cover_shot=6, square_shot=6, notes=NOTES)
L.export(globals())
