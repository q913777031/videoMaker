"""《百年孤独》10 羊皮卷：一家人的命，早就写好了吗？（季终；白板手绘 + AI 旁白，竖屏 2:3）

曲线故事 + 季终：梅尔基亚德斯留下的羊皮卷要满一百年才能读懂；布恩迪亚家一百年起起落落；奥雷里亚诺·巴比伦读懂时，
发现这个家的故事早就写好了，一阵大风卷走了马孔多；书的最后一句（范晔译本）。书里的家族没有第二次机会，我们有：
家里传下来的脾气可以在自己这里停一停。最后回看这一季十讲。文案见 bainian/PLAN.md「### 10」。
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
                            YELLOW, almond_tree, at_pop, box, bubble_box, butterfly, chip, draw_lady, draw_li, draw_man,
                            draw_wang, flower_rain, house, melquiades, name_tag, parchment, pop_scale, seal, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "生活里", 1),
    ([2], "生活里", 2),
    ([3, 4], "书里的人", 3),
    ([5, 6], "一百年", 4),
    ([7, 8], "读懂了", 5),
    ([9], "大风", 6),
    ([10], "最后一句", 7),
    ([11, 12], "说回我们", 8),
    ([13], "第一步", 9),
    ([14], "第二步", 10),
    ([15], "第三步", 11),
    ([16, 17, 18], "第一季回看", 12),
    ([19, 20, 21, 22], "季终", 13),
]

THEME = BT.get("10")
L = N.Lesson("10", SCREENS, drop_screen=2, board_size=(5000, 9000), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(12)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》第 20 章（范晔译本）。情节为转述；引文只有全书最后一句（范晔译）。",
    "今人（小李、小王、孩子）为虚构示意；书中人造型为示意（一百多年前的加勒比小镇打扮）。",
]

AB = ("奥雷里亚诺·巴比伦", "第六代 · 梅梅的儿子")
SEASON = ["冰块", "标签", "黑纱布", "粉笔圈", "名字", "眼睛", "黄蝴蝶", "床单", "大雨", "羊皮卷"]


def kid(c, x, y, s=0.6, mood="smile", **kw):
    draw_li(c, x, y, s, mood, **kw)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：小李对孩子吼，背后的影子和他爸爸重叠
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = kq(j, wp(0, 1, 0.4), 0)
    k_like = nx(j, wp(0, 2, 0.4), k_li)
    k_yell = nx(j, wp(1, 0, 0.5), k_like)
    k_shadow = nx(j, wp(1, 2, 0.3), k_yell)
    L.note("快点！")
    LX = cx - 150

    def scene(c, kk, T):
        tl, tk, ty, ts = (tb(j, k) for k in (k_li, k_like, k_yell, k_shadow))
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        if T >= ts:
            a = 0.35 * clamp01((T - ts) / 0.4)
            draw_man(c, LX - 40, GY, 1.1, "gray", beard="mustache", mood="angry", alpha=a, rh=(LX + 120, GY - 330))
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "flat" if T < ty else "sad", rh=(LX + 140, GY - 330) if T >= ty else None)
        kid(c, cx + 300, GY, 0.6, "sad" if T >= ty else "smile")
        if T >= tk:
            for q in range(3):
                r = 40 + q * 30
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(LX + 50 - r, GY - 300 - r, 2 * r, 2 * r), -40, 80)
                c.drawPath(arc, wb.marker(GRAY, 5, clamp01((T - tk) / 0.3)))
        if T >= ty:
            with K.at(c, cx + 120, cy - 260, 0, C.slam_scale(T - ty)):
                bubble_box(c, 0, 0, 260, 120, -1)
                K.text(c, "快点！", 0, 0, 60, "hand", RED)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_like, "pop", 0.65, "口气像爸妈")
    b.hit(j, k_yell, "rim", 0.8, "一着急就吼")
    b.hit(j, k_shadow, "tom", 0.75, "和老一辈一模一样")


screen1()


# ================================================================ 屏 2（drop）：一卷写好的纸从天上落到小李手里
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_li = kq(j, wp(2, 0, 0.3), 0)
    L.note("写好了")

    def scene(c, kk, T):
        tl, td = tb(j, k_li), tb(j, dk)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        hy = GY - 290
        with at_pop(c, cx, GY, g):
            draw_li(c, cx, GY, 1.0, "o" if T >= td else "flat", lh=(cx - 80, hy + 60), rh=(cx + 80, hy + 60))
        f = ease_in_out(clamp01((T - tl) / max(0.3, td - tl)))
        y = lerp(cy - 600, hy - 120, f)
        parchment(c, cx, y, 260, 200, 1.0, 1.0, 3)
        if T >= td:
            with K.at(c, cx + 300, cy - 360, -4, C.slam_scale(T - td)):
                chip(c, 0, 0, "写好了", RED_FILL, RED, 62)
        return None
    ev(j, k_li, scene, "shaker", 0.6)
    b.hit(j, dk, "kick", 0.9, "早就写好了")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：绿皮书翻开；梅尔基亚德斯把一摞羊皮卷放进木箱，箱子上写“一百年”
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(3, 0, 0.4), 0)
    k_mel = nx(j, wp(3, 1, 0.4), k_book)
    k_rolls = nx(j, wp(3, 2, 0.4), k_mel)
    k_100 = nx(j, wp(4, 1, 0.5), k_rolls)
    KT.book(j, k_book, x=cx - 360, y=cy - 300)
    L.note("梅尔基亚德斯", "吉卜赛人", "一百年", "看不懂")
    MX = cx - 280

    def scene(c, kk, T):
        tm, tr, t1 = tb(j, k_mel), tb(j, k_rolls), tb(j, k_100)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        with at_pop(c, MX, GY, g):
            melquiades(c, MX, GY, 1.0, mood="smile", rh=(MX + 160, GY - 230))
        name_tag(c, MX + 60, GY - 500, "梅尔基亚德斯", "#3A3A3A", 42, clamp01(g), "吉卜赛人")
        BX = cx + 250
        if T >= tr:
            for q in range(3):
                with K.at(c, BX - 80 + q * 80, GY - 250 - (q % 2) * 30, (q - 1) * 10, pop_scale(T - tr - q * 0.1)):
                    parchment(c, 0, 0, 90, 160, 1.0, 1.0, 2)
            K.text(c, "看不懂", BX + 210, cy - 40, 48, "hand", GRAY, clamp01((T - tr) / 0.3))
        box(c, BX, GY - 80, 380, 160, "#8A6A3A", "#5E4128", 7, 8, g)
        if T >= t1:
            with K.at(c, BX, GY - 80, -3, C.slam_scale(T - t1)):
                K.text(c, "一百年", 0, 0, 70, "serif_black", BUTTER)
        return None
    ev(j, k_mel, scene, "bongo_low", 0.7)
    b.hit(j, k_rolls, "pop", 0.7, "一堆羊皮卷")
    b.hit(j, k_100, "kick", 0.8, "要等满一百年")


screen3()


# ================================================================ 屏 4：一条起伏的曲线：建村、战争、香蕉公司、大雨、衰落
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    k_gen = kq(j, wp(5, 1, 0.3), 0)
    k_curve = nx(j, wp(6, 0, 0.3), k_gen)
    k_hot = nx(j, wp(6, 1, 0.4), k_curve)
    k_cold = nx(j, wp(6, 2, 0.4), k_hot)
    PTS = [(-480, 200, "建村"), (-260, -60, "冰块"), (-60, 120, "战争"), (160, -250, "香蕉公司"), (330, 180, "大雨"),
           (480, 340, "风")]
    L.note(*(p[2] for p in PTS), "起", "落")

    def scene(c, kk, T):
        tg, tc, th, tco = (tb(j, k) for k in (k_gen, k_curve, k_hot, k_cold))
        g = pop_scale(T - tg)
        if g <= 0:
            return None
        n = min(6, 1 + int((T - tg) / 0.15))
        for q in range(n):
            x = cx - 450 + q * 180
            (draw_man if q % 2 == 0 else draw_lady)(c, x, cy + 560, 0.38, ("white", "blue", "red", "yellow", "green", "purple")[q],
                                                    mood="flat")
        if T >= tc:
            f = ease_out(clamp01((T - tc) / 1.2))
            path = skia.Path()
            path.moveTo(cx + PTS[0][0], cy + PTS[0][1])
            for (x0, y0, _), (x1, y1, _) in zip(PTS, PTS[1:]):
                mx = (x0 + x1) / 2
                path.cubicTo(cx + mx, cy + y0, cx + mx, cy + y1, cx + x1, cy + y1)
            c.drawPath(wb.partial(path, f)[0] if f < 1 else path, wb.marker(RED, 9))
            for i, (x, y, s) in enumerate(PTS):
                if f >= i / (len(PTS) - 1) - 1e-6:
                    c.drawCircle(cx + x, cy + y, 14, K.paint(RED))
                    K.text(c, s, cx + x, cy + y - 50, 40, "hand", INK)
        if T >= th:
            K.text(c, "起", cx + 160, cy - 380, 70, "hand", GREEN, clamp01((T - th) / 0.3))
        if T >= tco:
            K.text(c, "落", cx + 480, cy + 200, 70, "hand", GRAY, clamp01((T - tco) / 0.3))
        return None
    ev(j, k_gen, scene, "shaker", 0.65)
    b.hit(j, k_curve, "wood_high", 0.6, "起过落过")
    b.hit(j, k_hot, "clap", 0.7, "热闹过")
    b.hit(j, k_cold, "xiaoluo", 0.7, "冷清过")


screen4()


# ================================================================ 屏 5：奥雷里亚诺·巴比伦趴在桌上读羊皮卷，字一行行亮起
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_ab = kq(j, wp(7, 1, 0.3), 0)
    k_read = nx(j, wp(7, 2, 0.4), k_ab)
    k_all = nx(j, wp(8, 1, 0.4), k_read)
    k_story = nx(j, wp(8, 2, 0.4), k_all)
    L.note(*AB, "全部故事")

    def scene(c, kk, T):
        ta, tr, tal, ts = (tb(j, k) for k in (k_ab, k_read, k_all, k_story))
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        AX = cx - 330
        with at_pop(c, AX, GY, g):
            draw_man(c, AX, GY, 0.95, "ochre", beard="full", mood="o" if T >= tal else "flat", rh=(AX + 170, GY - 210))
        name_tag(c, AX, GY - 480, AB[0], "#5E4128", 34, clamp01(g), AB[1])
        with K.at(c, cx + 150, GY - 140, 0, g):
            box(c, 0, 0, 600, 28, "#E7D6BA", "#8B6B43", 6, 6)
        f = ease_out(clamp01((T - tr) / 0.5)) if T >= tr else 0
        parchment(c, cx + 150, cy - 140, 560, 640, max(0.05, f))
        if T >= tal:
            n = min(9, 1 + int((T - tal) / 0.12))
            for q in range(n):
                C.line(c, (cx - 90, cy - 380 + q * 60), (cx + 390 - (q % 3) * 50, cy - 380 + q * 60), INK, 6)
        if T >= ts:
            with K.at(c, cx + 150, cy + 260, -2, C.slam_scale(T - ts)):
                chip(c, 0, 0, "全部故事", RED_FILL, RED, 56)
        return None
    ev(j, k_ab, scene, "bongo_low", 0.7)
    b.hit(j, k_read, "wood_high", 0.65, "终于读懂")
    b.hit(j, k_all, "shaker", 0.7, "一百年前就写好")
    b.hit(j, k_story, "ding", 0.85, "这个家的全部故事")


screen5()


# ================================================================ 屏 6：风卷起房子、杏仁树、黄蝴蝶，马孔多被吹散
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_town = kq(j, wp(9, 0, 0.5), 0)
    k_wind = nx(j, wp(9, 1, 0.5), k_town)
    k_gone = nx(j, wp(9, 2, 0.5), k_wind)
    L.note("马孔多")

    def scene(c, kk, T):
        tt, tw, tg = tb(j, k_town), tb(j, k_wind), tb(j, k_gone)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        blow = ease_in_out(clamp01((T - tg) / 1.2)) if T >= tg else 0
        items = [(-350, 0.45, "house"), (-60, 0.5, "tree"), (240, 0.4, "house"), (420, 0.35, "house")]
        for i, (dx, s_, kind) in enumerate(items):
            x = cx + dx + 700 * blow * (0.6 + 0.2 * i)
            y = GY - 60 - 500 * blow * (0.3 + 0.2 * (i % 2))
            with K.at(c, x, y, 60 * blow * (1 if i % 2 else -1), s_ * g * (1 - 0.5 * blow)):
                if kind == "house":
                    house(c, 0, 0, alpha=1 - blow * 0.8)
                else:
                    almond_tree(c, 0, 0, 1.6, 1 - blow * 0.8)
        K.text(c, "马孔多", cx, cy - 420, 70, "serif_black", INK, g * (1 - blow))
        if T >= tw:
            for q in range(5):
                y = cy - 300 + q * 140
                ph = ((T - tw) * 1.2 + q * 0.25) % 1
                c.drawPath(P((cx - 600 + 1100 * ph, y), (cx - 380 + 1100 * ph, y - 30), (cx - 240 + 1100 * ph, y + 10)),
                           wb.marker(BLUE, 6, 0.6))
            for q in range(5):
                u = ((T - tw) * 0.5 + q * 0.2) % 1
                butterfly(c, cx - 500 + 1000 * u, cy - 200 + 120 * math.sin(u * 7 + q), 0.6, T + q)
        return None
    ev(j, k_town, scene, "wood_low", 0.6)
    b.hit(j, k_wind, "shaker", 0.85, "一阵大风")
    b.hit(j, k_gone, "cymbal", 0.6, "卷起整个马孔多")


screen6()


# ================================================================ 屏 7：羊皮卷上一句话逐段写出，末尾“第二次机会”亮起
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_open = kq(j, wp(10, 0, 0.3), 0)
    PIECES = [(1, "因为注定经受"), (2, "百年孤独的家族"), (3, "不会有第二次机会"), (4, "在大地上出现")]
    ks, prev = [], k_open
    for pi, _ in PIECES:
        k_ = nx(j, wp(10, pi, 0.2), prev)
        ks.append(k_)
        prev = k_
    L.note("最后一句", "范晔 译", *(w for _, w in PIECES))

    def scene(c, kk, T):
        to = tb(j, k_open)
        f = ease_out(clamp01((T - to) / 0.7))
        if f <= 0:
            return None
        parchment(c, cx, cy - 40, 900, 980, f)
        a = clamp01((T - to - 0.3) / 0.3)
        K.text(c, "最后一句", cx - 60, cy - 460, 56, "serif_black", RED, a)
        K.text(c, "范晔 译", cx + 260, cy - 460, 34, "sans_medium", GRAY, a)
        for i, (k_, (_, w)) in enumerate(zip(ks, PIECES)):
            t0 = tb(j, k_)
            if T < t0:
                continue
            y = cy - 300 + i * 170
            if i == 2:
                with K.at(c, cx, y, 0, C.slam_scale(T - t0)):
                    K.text(c, w, 0, 0, 74, "serif_black", RED)
                sparkle(c, cx + 300, y, T - t0, YELLOW, 8, 50, 140)
            else:
                K.text(c, w, cx, y, 66, "serif_black", INK, clamp01((T - t0) / 0.25))
        return None
    ev(j, k_open, scene, "wood_low", 0.65)
    for i, k_ in enumerate(ks):
        b.hit(j, k_, "kick" if i == 2 else "pop", 0.85 if i == 2 else 0.6, "最后一句逐段出现")


screen7()


# ================================================================ 屏 8：一卷空白的新纸摊在小李面前；大字“停一停”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_we = kq(j, wp(11, 2, 0.3), 0)
    k_blank = nx(j, wp(12, 0, 0.5), k_we)
    k_stop = nx(j, wp(12, 2, 0.4), k_blank)
    L.note("我们有", "停一停")

    def scene(c, kk, T):
        tw, tbk, ts = tb(j, k_we), tb(j, k_blank), tb(j, k_stop)
        g = pop_scale(T - tw)
        if g <= 0:
            return None
        with at_pop(c, cx - 300, GY, g):
            draw_li(c, cx - 300, GY, 1.0, "smile")
        with K.at(c, cx - 300, cy - 300, 0, C.slam_scale(T - tw)):
            K.text(c, "我们有", 0, 0, 80, "hand", GREEN)
        if T >= tbk:
            f = ease_out(clamp01((T - tbk) / 0.6))
            parchment(c, cx + 220, cy - 60, 460, 560, f)
        if T >= ts:
            with K.at(c, cx + 220, cy - 60, -3, C.slam_scale(T - ts)):
                K.text(c, "停一停", 0, 0, 100, "hand", RED)
        return None
    ev(j, k_we, scene, "ding", 0.75)
    b.hit(j, k_blank, "wood_high", 0.6, "家里传下来的脾气")
    b.hit(j, k_stop, "kick", 0.85, "在你这里停一停")


screen8()


# ================================================================ 屏 9：第一步：本子上写“一着急就吼”
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    k_book = kq(j, wp(13, 0, 0.6), 1)
    k_write = nx(j, wp(13, 1, 0.5), k_book)
    L.note("从家里学来的", "一着急就吼", "不说谢谢", "报喜不报忧")

    def scene(c, kk, T):
        tbk, tw = tb(j, k_book), tb(j, k_write)
        g = pop_scale(T - tbk)
        if g <= 0:
            return None
        with K.at(c, cx, cy + 40, -2, g):
            box(c, 0, 0, 760, 640, "#FFFFFF", BLACK, 7, 14)
            K.text(c, "从家里学来的", 0, -230, 54, "hand", RED)
            for i, s in enumerate(("一着急就吼", "不说谢谢", "报喜不报忧")):
                if T >= tw + i * 0.3:
                    K.text(c, s, 0, -80 + i * 130, 56, "hand", INK, clamp01((T - tw - i * 0.3) / 0.25))
        return None
    ev(j, k_book, scene, "wood_high", 0.65)
    b.hit(j, k_write, "pop", 0.75, "写下一个习惯")


screen9()


# ================================================================ 屏 10：第二步：这张卡被拎出来，打一个叉
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    k_pick = kq(j, wp(14, 1, 0.4), 1)
    k_x = nx(j, wp(14, 2, 0.5), k_pick)
    L.note("一着急就吼", "不传下去")

    def scene(c, kk, T):
        tp, tx = tb(j, k_pick), tb(j, k_x)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 40, -3, g):
            box(c, 0, 0, 640, 220, NOTE_FILL, ORANGE, 7, 14)
            K.text(c, "一着急就吼", 0, 0, 72, "hand", INK)
        if T >= tx:
            f = ease_out(clamp01((T - tx) / 0.3))
            C.line(c, (cx - 280, cy - 150), (lerp(cx - 280, cx + 280, f), lerp(cy - 150, cy + 70, f)), RED, 12)
            C.line(c, (cx + 280, cy - 150), (lerp(cx + 280, cx - 280, f), lerp(cy - 150, cy + 70, f)), RED, 12)
            with K.at(c, cx, cy + 300, 0, C.slam_scale(T - tx)):
                chip(c, 0, 0, "不传下去", GREEN_FILL, GREEN, 60)
        return None
    ev(j, k_pick, scene, "pop", 0.7)
    b.hit(j, k_x, "rim", 0.85, "打一个叉")


screen10()


# ================================================================ 屏 11：第三步：小李蹲下来对孩子轻声说话
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_kneel = kq(j, wp(15, 0, 0.6), 1)
    k_soft = nx(j, wp(15, 1, 0.5), k_kneel)
    k_try = nx(j, wp(15, 2, 0.4), k_soft)
    L.note("不急，慢慢来", "试")

    def scene(c, kk, T):
        tk, ts, tt = tb(j, k_kneel), tb(j, k_soft), tb(j, k_try)
        g = pop_scale(T - tk)
        if g <= 0:
            return None
        with at_pop(c, cx - 180, GY, g):
            draw_li(c, cx - 180, GY, 0.95, "smile", squash=0.8)
        kid(c, cx + 200, GY, 0.62, "smile" if T >= tt else "flat")
        if T >= ts:
            with K.at(c, cx - 40, cy - 200, 0, pop_scale(T - ts)):
                bubble_box(c, 0, 0, 380, 110, 1)
                K.text(c, "不急，慢慢来", 0, 0, 50, "hand", GREEN)
        if T >= tt:
            c.drawPath(C.heart_path(cx + 200, cy + 30, 50), K.paint(RED_FILL))
            c.drawPath(C.heart_path(cx + 200, cy + 30, 50), wb.marker(RED, 6))
            sparkle(c, cx + 200, cy + 30, T - tt, YELLOW, 10, 60, 160)
        return None
    ev(j, k_kneel, scene, "wood_low", 0.6)
    b.hit(j, k_soft, "pop", 0.7, "换一种说法")
    b.hit(j, k_try, "ding", 0.85, "先在最亲的人身上试")


screen11()


# ================================================================ 屏 12：第一季回看：十张卡片排成一面墙
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_wall = kq(j, wp(16, 1, 0.3), 0)
    k_10 = nx(j, wp(16, 2, 0.5), k_wall)
    k_list = nx(j, wp(17, 0, 0.3), k_10)
    k_today = nx(j, wp(18, 2, 0.3), k_list)
    L.note(*SEASON, "第一季", "今天")

    def scene(c, kk, T):
        tw, t10, tl, tt = (tb(j, k) for k in (k_wall, k_10, k_list, k_today))
        if T < tw:
            return None
        K.text(c, "第一季", cx, cy - 520, 64, "serif_black", RED, clamp01((T - tw) / 0.3))
        hi = -1
        if T >= tl:
            hi = min(9, int((T - tl) / max(0.3, (tt - tl) / 10)))
        for i, s_ in enumerate(SEASON):
            r_, q = divmod(i, 2)
            x, y = cx - 230 + q * 460, cy - 400 + r_ * 150
            t0 = tw + i * max(0.04, (t10 - tw) / 10)
            g = pop_scale(T - t0, 0.22)
            if g <= 0:
                continue
            with K.at(c, x, y, 0, g * (1.08 if i == hi else 1)):
                box(c, 0, 0, 420, 120, N.PARCH, N.PARCH_LINE if i != hi else RED, 5 if i != hi else 8, 10)
                K.text(c, f"{i + 1:02d}", -150, 0, 40, "black", RED)
                K.text(c, s_, 40, 0, 50, "serif_black", INK)
        if T >= tt:
            with K.at(c, cx, cy + 420, -3, C.slam_scale(T - tt)):
                chip(c, 0, 0, "今天", GREEN_FILL, GREEN, 60)
        return None
    ev(j, k_wall, scene, "shaker", 0.75)
    b.hit(j, k_10, "ding", 0.85, "十个故事")
    b.hit(j, k_list, "wood_high", 0.6, "一讲讲数过去")
    b.hit(j, k_today, "kick", 0.85, "今天的日子里找到")


screen12()


# ================================================================ 屏 13：季终：评论区；第一讲亮起；小李在新纸上写第一行；黄蝴蝶飞起；“下一季见”
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z_))
    k_chips = nx(j, wp(20, 0, 0.3), 0)
    k_first = nx(j, wp(20, 2, 0.4), k_chips)
    k_write = nx(j, wp(21, 1, 0.3), k_first)
    k_new = nx(j, wp(21, 3, 0.4), k_write)
    k_bye = nx(j, wp(22, 1, 0.3), k_new)
    b.move(j, k_write, (cx, cy + 380, Z_), 1.1)
    CH = ["冰块", "粉笔圈", "羊皮卷"]
    L.note("最想先用哪一讲？", *CH, "第一讲", "新的开头", "下一季见")

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, 0))
        if sc <= 0:
            return None
        with K.at(c, cx + 20, cy - 330, 0, sc):
            bubble_box(c, 0, 0, 1000, 360, -1)
            K.text(c, "最想先用哪一讲？", 0, -110, 62, "hand", RED)
            for i, nm in enumerate(CH):
                g = pop_scale(T - tb(j, k_chips) - i * 0.15, 0.22)
                if g <= 0:
                    continue
                x, y = (-230 + (i % 2) * 460, 10) if i < 2 else (0, 110)
                with K.at(c, x, y, 0, g):
                    chip(c, 0, 0, nm, BLUE_FILL, BLUE, 44)
        tf = tb(j, k_first)
        if T >= tf:
            with K.at(c, cx + 380, cy - 90, 6, C.slam_scale(T - tf)):
                box(c, 0, 0, 220, 90, NOTE_FILL, ORANGE, 5, 10)
                K.text(c, "第一讲", 0, 0, 46, "hand", RED)
        return None
    ev(j, 0, cmt, "pop", 0.7)
    b.hit(j, k_chips, "wood_high", 0.6, "评论冒出来")
    b.hit(j, k_first, "pop", 0.75, "从第一讲看起")
    LY = cy + 640

    def write(c, kk, T):
        tw, tn = tb(j, k_write), tb(j, k_new)
        if T < tw:
            return None
        parchment(c, cx + 180, cy + 380, 460, 420, ease_out(clamp01((T - tw) / 0.5)))
        LX = cx - 300
        with at_pop(c, LX, LY, pop_scale(T - tw)):
            draw_li(c, LX, LY, 0.85, "smile", rh=(cx - 10, cy + 420))
        if T >= tn:
            f = clamp01((T - tn) / 0.6)
            K.text(c, "新的开头", cx + 180, cy + 340, 60, "hand", RED, f)
            for q in range(3):
                u = clamp01((T - tn - q * 0.2) / 1.5)
                butterfly(c, lerp(cx + 180, cx + 300 + q * 80, u), lerp(cy + 380, cy + 100 - q * 60, u), 0.7, T + q, f)
        return None
    ev(j, k_write, write, "wood_low", 0.65)
    b.hit(j, k_new, "ding", 0.85, "写一个新的开头")

    def bye(c, kk, T):
        t0 = tb(j, k_bye)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        with K.at(c, cx + 20, cy + 880, -2, sc):
            box(c, 0, 0, 900, 200, "#FFFFFF", BLACK, 7, 18)
            K.text(c, "下一季见", -60, 0, 90, "serif_black", RED)
            seal(c, 320, 0, "马孔多", 40, -6)
        flower_rain(c, cx - 560, cx + 560, cy + 200, cy + 1000, T, t0, 30)
        return None
    ev(j, k_bye, bye, "cymbal", 0.7)


screen13()

# ================================================================ 收尾
L.finish(cover_shot=7, square_shot=5, notes=NOTES)
L.export(globals())
