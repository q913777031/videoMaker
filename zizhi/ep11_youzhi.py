"""《资治通鉴》11 有志者：想做一件难事，周围都说不行怎么办？（白板手绘 + AI 旁白，竖屏 2:3）

曲线故事：一条难度曲线贯穿——开头最陡；耿弇早年出“先北后东、打下齐地”的大主意，光武帝觉得难；一站站打过去，到齐地碰上张步，
中箭自截箭杆接着打，张步大败；光武帝劳军“有志者事竟成”。今人：想转岗、考证被劝“别折腾”，三步（拆成小站、受挫先处理伤口、每过一站记一笔）。
古人的屏画在卷轴框里，今人在办公室。文案见 zizhi/PLAN.md「### 11」。
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
                          RED_FILL, YELLOW, at_pop, bamboo_slips, box, bubble_box, chip, city_wall, desk, draw_ace, draw_li,
                          draw_wang, flag, gu, name_tag, pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "通鉴里的故事", 4),
    ([6], "光武帝的担心", 5),
    ([7, 8], "一路打过去", 6),
    ([9, 10], "截箭再战", 7),
    ([11, 12], "有志者事竟成", 8),
    ([13, 14], "说回我们自己", 9),
    ([15], "第一步", 10),
    ([16], "第二步", 11),
    ([17], "第三步", 12),
    ([18], "好处", 13),
    ([19, 20, 21, 22], "评论区见", 14),
]

THEME = ZT.get("11")
L = Z.Lesson("11", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME,
             trim_tail={5: 0.12})          # 第 5 句句尾碎音（识别成“去”），裁掉
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(13)]
Z_ = 0.72
KT = Z.Kit(L, R)

NOTES = [
    "出处：司马光《资治通鉴》卷四十一 汉纪三十三（建武五年）耿弇平齐。",
    "原文：“飞矢中弇股，以佩刀截之，左右无知者”；帝至临淄劳军，谓弇曰“将军前在南阳建此大策，常以为落落难合，有志者事竟成也”。",
    "耿弇早年大策的内容（先北后东）见《后汉书·耿弇传》，待核；今人（小李、小王、家人朋友）为虚构示意；古人造型为示意。",
]

GENG, GUANGWU, ZHANG = "blue", "ochre", "gray"


def curve_pts(x0, x1, y0, h, n=60):
    """难度曲线：开头最陡，往后渐缓。"""
    pts = []
    for i in range(n + 1):
        u = i / n
        pts.append((lerp(x0, x1, u), y0 - h * (1 - (1 - u) ** 3)))
    return pts


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：小李手里“转岗”“考证”两张卡，周围的人摆手；脚步变慢
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_cards = kq(j, wp(0, 1, 0.5), 1)
    k_wave = nx(j, wp(0, 3, 0.4), k_cards)
    k_slow = nx(j, wp(1, 1, 0.4), k_wave)
    LX = cx - 80
    L.note("转岗", "考证")

    def scene(c, kk, T):
        tc, tw, ts = tb(j, k_cards), tb(j, k_wave), tb(j, k_slow)
        g = pop_scale(T - tb(j, k_li))
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "sad" if T >= ts else "smile", lh=(LX - 120, GY - 330), rh=(LX + 120, GY - 330))
        if T >= tc:
            for i, s_ in enumerate(("转岗", "考证")):
                with K.at(c, LX + (i * 2 - 1) * 160, cy - 120, (i * 2 - 1) * 6, pop_scale(T - tc - i * 0.12)):
                    box(c, 0, 0, 180, 110, NOTE_FILL, ORANGE, 5, 10)
                    K.text(c, s_, 0, 0, 54, "hand", INK)
        if T >= tw:
            for i, x in enumerate((cx - 430, cx + 330)):
                with at_pop(c, x, GY, pop_scale(T - tw - i * 0.12)):
                    if i:
                        draw_wang(c, x, GY, 0.8, mood="flat", rh=(x - 110, GY - 300 + 20 * math.sin((T - tw) * 12)))
                    else:
                        draw_ace(c, x, GY, 0.8, mood="flat", rh=(x + 110, GY - 300 + 20 * math.sin((T - tw) * 12)))
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_cards, "pop", 0.75, "转岗、考证")
    b.hit(j, k_wave, "rim", 0.75, "劝你别折腾")
    b.hit(j, k_slow, "tom", 0.7, "开始犹豫")


screen1()


# ================================================================ 屏 2（drop）：家里人、同事、朋友三个气泡逐个砸下
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_b = [kq(j, wp(2, 0, 0.5), 0)]
    k_b.append(nx(j, wp(2, 1, 0.5), k_b[0]))
    BUB = [("太难", cx - 250, cy - 380), ("不现实", cx + 230, cy - 300), ("再等等", cx - 30, cy - 120)]
    L.note("家里人", "同事", "朋友", "太难", "不现实", "再等等")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, 0))
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            draw_li(c, cx, GY, 0.9, "sad" if T >= tb(j, dk) else "flat")
        times = [tb(j, k_b[0]), tb(j, k_b[1]), tb(j, dk)]
        for i, ((s_, x, y), t0) in enumerate(zip(BUB, times)):
            if T < t0:
                continue
            with K.at(c, x, y, (i - 1) * 5, C.slam_scale(T - t0)):
                bubble_box(c, 0, 0, 280, 120, 1 if x < cx else -1)
                K.text(c, s_, 0, 0, 56, "hand", RED)
                K.text(c, ("家里人", "同事", "朋友")[i], 0, -90, 36, "sans_medium", GRAY)
        return None
    ev(j, 0, scene, "wood_low", 0.6)
    for k_ in k_b:
        b.hit(j, k_, "rim", 0.75, "又一句劝")
    b.hit(j, dk, "kick", 0.9, "再等等")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：一条难度曲线，开头最陡
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_axis = 0
    k_curve = kq(j, wp(3, 1, 0.3), 1)
    k_steep = nx(j, wp(3, 2, 0.5), k_curve)
    L.note("难度", "开头最陡")
    x0, x1, y0 = cx - 460, cx + 480, cy + 360
    pts = curve_pts(x0 + 20, x1, y0, 700)
    b.path(j, k_axis, k_axis + 0.5, P((x0, cy - 440), (x0, y0), (x1 + 40, y0)), BLACK, 8, sfx="wood_low")
    b.text(j, k_axis + 0.3, k_axis + 0.6, "难度", x0 + 100, cy - 420, 50, BLACK)
    b.path(j, k_curve, k_curve + 1.2, P(*pts), RED, 12, sfx="shaker", gain=0.7)

    def steep(c, kk, T):
        ts = tb(j, k_steep)
        if T < ts:
            return None
        ring = skia.Path()
        ring.addOval(skia.Rect.MakeXYWH(x0 - 40, y0 - 520, 260, 560))
        c.drawPath(wb.partial(ring, ease_out(clamp01((T - ts) / 0.3)))[0], wb.marker(ORANGE, 8))
        K.text(c, "开头最陡", x0 + 380, y0 - 300, 64, "hand", ORANGE, clamp01((T - ts) / 0.2))
        return None
    ev(j, k_steep, steep, "tom", 0.8)


screen3()


# ================================================================ 屏 4：竹简“卷四十一”；耿弇在地图上画路线：先北，再往东到齐地
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(4, 0, 0.3), 0)
    k_geng = nx(j, wp(4, 2, 0.4), k_book)
    k_plan = nx(j, wp(4, 3, 0.4), k_geng)
    k_north = nx(j, wp(5, 0, 0.5), k_plan)
    k_qi = nx(j, wp(5, 2, 0.4), k_north)
    KT.book(j, k_book, "卷四十一", "汉纪三十三")
    L.note("耿弇", "北", "齐地")

    def scene(c, kk, T):
        tg, tp, tn, tq = tb(j, k_geng), tb(j, k_plan), tb(j, k_north), tb(j, k_qi)
        g = pop_scale(T - tg)
        if g <= 0:
            return None
        GX = cx + 380
        with at_pop(c, GX, GY, g):
            gu(c, GX, GY, 0.85, GENG, hat="helmet", mood="smile", rh=(GX - 150, GY - 300) if T >= tp else None)
            name_tag(c, GX, GY - 420, "耿弇", "#2F5B8E", 40)
        if T >= tp:
            with K.at(c, cx + 40, cy - 140, 0, pop_scale(T - tp)):
                box(c, 0, 0, 520, 420, PARCH, PARCH_LINE, 6, 8)
                start = (-180, 140)
                north = (-120, -130)
                qi = (200, -40)
                c.drawCircle(start[0], start[1], 20, K.paint(INK))
                if T >= tn:
                    f = ease_out(clamp01((T - tn) / 0.5))
                    c.drawPath(wb.partial(wb.arrow(start, north, 0.1, 30), f)[0], wb.marker(BLUE, 9))
                    K.text(c, "北", north[0] - 50, north[1], 50, "serif_black", BLUE, f)
                if T >= tq:
                    f = ease_out(clamp01((T - tq) / 0.5))
                    c.drawPath(wb.partial(wb.arrow(north, qi, -0.3, 30), f)[0], wb.marker(RED, 9))
                    flag(c, qi[0] + 20, qi[1] + 120, 0.35, "齐", "#9C2F25")
        return None
    b.custom(j, k_geng, k_geng + 0.3, scene, sfx="tom", gain=0.75)
    b.hit(j, k_plan, "pop", 0.7, "出主意")
    b.hit(j, k_north, "shaker", 0.7, "扫平北边")
    b.hit(j, k_qi, "kick", 0.8, "打下齐地")


screen4()


# ================================================================ 屏 5：光武帝摇头，路线图上画了个问号
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_gw = 0
    k_shake = kq(j, wp(6, 1, 0.4), 1)
    k_q = nx(j, wp(6, 2, 0.4), k_shake)
    WX = cx - 330
    L.note("光武帝", "太难")

    def scene(c, sc, T):
        ts, tq = tb(j, k_shake), tb(j, k_q)
        shake = 12 * math.sin((T - ts) * 14) * math.exp(-(T - ts) * 1.5) if T >= ts else 0
        with at_pop(c, WX, GY, sc):
            gu(c, WX, GY, 1.0, GUANGWU, hat="guan", beard="black", head_dx=shake)
            name_tag(c, WX, GY - 450, "光武帝", "#8A5A1E", 44)
        with K.at(c, cx + 220, cy - 120, 3, sc):
            box(c, 0, 0, 440, 360, PARCH, PARCH_LINE, 6, 8)
            c.drawPath(wb.arrow((-150, 120), (-100, -100), 0.1, 26), wb.marker(BLUE, 7))
            c.drawPath(wb.arrow((-100, -100), (150, -30), -0.3, 26), wb.marker(RED, 7))
            if T >= tq:
                with K.at(c, 30, 40, 0, C.slam_scale(T - tq)):
                    K.text(c, "？", 0, 0, 220, "hand", RED)
        if T >= ts:
            with K.at(c, WX + 40, cy - 330, 0, pop_scale(T - ts)):
                bubble_box(c, 0, 0, 220, 110, -1)
                K.text(c, "太难", 0, 0, 58, "hand", INK)
        return None
    ev(j, k_gw, L.pop_fn(j, k_gw, scene), "muyu", 0.6)
    b.hit(j, k_shake, "wood_low", 0.7, "觉得太难")
    b.hit(j, k_q, "rim", 0.8, "很难办成")


screen5()


# ================================================================ 屏 6：曲线一站站往上爬；齐地张步大军；一支箭射来
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_go = kq(j, wp(7, 1, 0.4), 0)
    k_qi = nx(j, wp(7, 2, 0.5), k_go)
    k_zhang = nx(j, wp(7, 3, 0.4), k_qi)
    k_arrow = nx(j, wp(8, 1, 0.5), k_zhang)
    L.note("张步", "齐地")
    x0, x1, y0 = cx - 480, cx + 100, cy + 100
    pts = curve_pts(x0, x1, y0, 420, 40)

    def scene(c, kk, T):
        tg, tq, tz, ta = tb(j, k_go), tb(j, k_qi), tb(j, k_zhang), tb(j, k_arrow)
        g = pop_scale(T - tg)
        if g <= 0:
            return None
        f = ease_in_out(clamp01((T - tg) / max(0.5, tq - tg)))
        n = max(2, int(f * len(pts)))
        c.drawPath(P(*pts[:n]), wb.marker(RED, 10))
        for q in range(4):
            i = int(q / 3 * (len(pts) - 1))
            if i < n:
                c.drawCircle(pts[i][0], pts[i][1], 18, K.paint(NOTE_FILL))
                c.drawCircle(pts[i][0], pts[i][1], 18, wb.marker(ORANGE, 4))
        hx, hy = pts[n - 1]
        with at_pop(c, hx, hy, 1):
            gu(c, hx, hy, 0.4, GENG, hat="helmet", mood="angry")
        if T >= tz:
            for r_ in range(2):
                for q in range(4):
                    x, y = cx + 250 + q * 70, GY - 60 - r_ * 90
                    with at_pop(c, x, y, pop_scale(T - tz - q * 0.05)):
                        gu(c, x, y, 0.35, ZHANG, hat="helmet")
            flag(c, cx + 520, GY, 0.45, "张", "#5E5E58")
            K.text(c, "齐地", cx + 380, cy - 60, 56, "hand", "#5E4128", clamp01((T - tz) / 0.3))
        if T >= ta:
            f2 = clamp01((T - ta) / 0.25)
            ax, ay = lerp(cx + 300, hx + 10, f2), lerp(GY - 300, hy - 40, f2)
            C.line(c, (ax, ay), (ax + 70, ay - 30), INK, 5)
            c.drawPath(P((ax, ay), (ax + 18, ay - 12), (ax + 6, ay + 12), close=True), K.paint(INK))
        return None
    ev(j, k_go, scene, "wood_low", 0.6)
    b.hit(j, k_qi, "shaker", 0.7, "到了齐地")
    b.hit(j, k_zhang, "tom", 0.8, "张步大军")
    b.hit(j, k_arrow, "kick", 0.85, "一箭射中大腿")
    b.shots[j].shake = [(k_arrow, 9.0)]


screen6()


# ================================================================ 屏 7：耿弇拔刀截断箭杆，接着冲；张步的旗倒下
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_knife = kq(j, wp(9, 0, 0.5), 0)
    k_cut = nx(j, wp(9, 1, 0.5), k_knife)
    k_charge = nx(j, wp(9, 2, 0.5), k_cut)
    k_flag = nx(j, wp(10, 1, 0.4), k_charge)
    GX = cx - 250
    L.note("截", "大败")

    def scene(c, kk, T):
        tk, tc, tch, tf = tb(j, k_knife), tb(j, k_cut), tb(j, k_charge), tb(j, k_flag)
        g = pop_scale(T - tk + 0.3)
        if g <= 0:
            return None
        x, dy, _ = C.walk(T, tch, 1.0, GX, GX + 200, 14) if T >= tch else (GX, 0, False)
        hy = GY - 290 * 0.95
        with at_pop(c, x, GY + dy, g):
            gu(c, x, GY + dy, 0.95, GENG, hat="helmet", mood="angry",
               rh=(x + 40, GY - 120 + dy) if tk <= T < tch else (x + 150, hy - 60 + dy))
            name_tag(c, x, GY - 430 + dy, "耿弇", "#2F5B8E", 40)
            stub = 80 if T < tc else 14
            C.line(c, (x - 30, GY - 130 + dy), (x - 30 - stub, GY - 130 - stub * 0.4 + dy), INK, 6)
            if T >= tk:
                C.line(c, (x + 40, GY - 120 + dy) if T < tch else (x + 150, hy - 60 + dy),
                       (x + 40 - 80, GY - 160 + dy) if T < tch else (x + 230, hy - 160 + dy), "#9AA3AD", 10)
        if T >= tc and T < tc + 1.2:
            f = clamp01((T - tc) / 1.2)
            C.line(c, (GX - 110, GY - 162 + 300 * f * f), (GX - 180, GY - 190 + 300 * f * f), INK, 6, 1 - f)
            K.burst(c, GX - 60, GY - 140, T - tc, ORANGE, 10, 40, 5, 4)
        f2 = ease_in_out(clamp01((T - tf) / 0.5)) if T >= tf else 0
        with K.at(c, cx + 380, GY, 80 * f2):
            flag(c, 0, 0, 0.6, "张", "#5E5E58")
        if T >= tf:
            seal(c, cx + 250, cy - 280, "大败", 80, -6, C.slam_scale(T - tf))
        return None
    ev(j, k_knife, scene, "wood_high", 0.65)
    b.hit(j, k_cut, "rim", 0.85, "一刀截断箭杆")
    b.hit(j, k_charge, "tom", 0.8, "接着打")
    b.hit(j, k_flag, "kick", 0.9, "张步大败")
    b.shots[j].shake = [(k_flag, 10.0)]


screen7()


# ================================================================ 屏 8：光武帝劳军，拍耿弇肩膀；竹简“有志者事竟成”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_come = kq(j, wp(11, 0, 0.5), 0)
    k_pat = nx(j, wp(11, 2, 0.4), k_come)
    k_words = nx(j, wp(12, 1, 0.3), k_pat)
    L.note("有志者事竟成")

    def scene(c, kk, T):
        tcm, tp, tw = tb(j, k_come), tb(j, k_pat), tb(j, k_words)
        g = pop_scale(T - tcm)
        if g <= 0:
            return None
        WX, GX = cx - 330, cx - 40
        pat = 10 * math.sin(clamp01((T - tp) / 0.6) * math.pi * 3) if T >= tp else 0
        with at_pop(c, WX, GY, g):
            gu(c, WX, GY, 0.9, GUANGWU, hat="guan", beard="black", mood="smile",
               rh=(GX - 60, GY - 290 * 0.85 + 70 + pat) if T >= tp else None)
            name_tag(c, WX, GY - 420, "光武帝", "#8A5A1E", 38)
        with at_pop(c, GX, GY, g):
            gu(c, GX, GY, 0.85, GENG, hat="helmet", mood="smile", bow=T >= tp)
            name_tag(c, GX, GY - 400, "耿弇", "#2F5B8E", 38)
        if T >= tw:
            with K.at(c, cx + 380, cy - 80, 0, C.slam_scale(T - tw)):
                bamboo_slips(c, 0, 0, 140, 720, n=1)
                slip_text(c, 0, -290, "有志者事竟成", 92, RED)
            sparkle(c, cx + 380, cy - 300, T - tw, YELLOW, 12, 80, 170)
        return None
    ev(j, k_come, scene, "muyu", 0.65)
    b.hit(j, k_pat, "clap", 0.75, "劳军")
    b.hit(j, k_words, "kick", 0.9, "有志者事竟成")
    b.shots[j].shake = [(k_words, 9.0)]


screen8()


# ================================================================ 屏 9：小李头上一盆冷水；“三步”
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_water = kq(j, wp(13, 1, 0.4), 1)
    k_good = nx(j, wp(13, 4, 0.4), k_water)
    k_3 = nx(j, wp(14, 1, 0.5), k_good)
    LX = cx - 260
    L.note("为你好", "三步")

    def scene(c, sc, T):
        tw, tg = tb(j, k_water), tb(j, k_good)
        hy = GY - 290
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 1.0, "sad" if T >= tw else "flat")
        if T >= tw:
            f = clamp01((T - tw) / 0.4)
            with K.at(c, LX + 40, hy - 220, 130 * f):
                c.drawPath(P((-80, -40), (80, -40), (60, 50), (-60, 50), close=True), K.paint("#9AA3AD"))
                c.drawPath(P((-80, -40), (80, -40), (60, 50), (-60, 50), close=True), wb.marker(INK, 5))
            for q in range(8):
                ff = clamp01((T - tw - 0.2 - q * 0.03) / 0.5)
                if 0 < ff < 1:
                    c.drawCircle(LX - 60 + q * 18, hy - 160 + 260 * ff, 9, K.paint("#7FB6E0", 1 - ff))
        if T >= tg:
            with K.at(c, cx + 250, cy - 120, 0, pop_scale(T - tg)):

                c.drawPath(C.heart_path(0, 0, 60), K.paint(RED_FILL))
                c.drawPath(C.heart_path(0, 0, 60), wb.marker(RED, 6))
                K.text(c, "为你好", 0, 120, 48, "hand", RED)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_water, "shaker", 0.8, "泼冷水")
    b.hit(j, k_good, "pop", 0.7, "也是为你好")
    L.stamp_ev(j, k_3, "三步", cx + 250, cy + 220, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen9()


# ================================================================ 屏 10：第一步：大目标拆成一站站小站牌
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_big = kq(j, wp(15, 0, 0.6), 1)
    k_split = nx(j, wp(15, 1, 0.5), k_big)
    k_walk = nx(j, wp(15, 3, 0.3), k_split)
    STOPS = ["报名", "学一章", "做题", "考试"]
    L.note("大目标", *STOPS)

    def scene(c, kk, T):
        tbg, ts, tw = tb(j, k_big), tb(j, k_split), tb(j, k_walk)
        g = pop_scale(T - tbg)
        if g <= 0:
            return None
        if T < ts + 0.2:
            with K.at(c, cx + 300, cy - 280, 0, g * (1 - clamp01((T - ts) / 0.2))):
                box(c, 0, 0, 300, 140, RED_FILL, RED, 6, 12)
                K.text(c, "大目标", 0, 0, 60, "hand", RED)
        if T >= ts:
            for i, s_ in enumerate(STOPS):
                x = cx - 380 + i * 260
                y = cy + 100 - i * 120
                with K.at(c, x, y, 0, pop_scale(T - ts - i * 0.1)):
                    C.line(c, (0, 0), (0, 140), "#7A5E3A", 8)
                    box(c, 0, -30, 180, 80, NOTE_FILL, ORANGE, 5, 8)
                    K.text(c, s_, 0, -30, 40, "hand", INK)
        if T >= tw:
            f = ease_in_out(clamp01((T - tw) / 1.2))
            seg = min(2, int(f * 3))
            u = f * 3 - seg
            x = lerp(cx - 380 + seg * 260, cx - 380 + (seg + 1) * 260, u)
            y = lerp(cy + 240 - seg * 120, cy + 240 - (seg + 1) * 120, u)
            with at_pop(c, x, y, 1):
                draw_li(c, x, y, 0.45, "smile")
        return None
    ev(j, k_big, scene, "wood_high", 0.65)
    b.hit(j, k_split, "shaker", 0.75, "拆成小站")
    b.hit(j, k_walk, "pop", 0.7, "一站一站走")


screen10()


# ================================================================ 屏 11：第二步：小李摔了一跤，先贴创可贴，再站起来
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_fall = kq(j, wp(16, 0, 0.6), 1)
    k_band = nx(j, wp(16, 1, 0.5), k_fall)
    k_up = nx(j, wp(16, 2, 0.5), k_band)
    L.note("挫折", "别放弃")
    LX = cx - 60

    def scene(c, kk, T):
        tf, tbd, tu = tb(j, k_fall), tb(j, k_band), tb(j, k_up)
        g = pop_scale(T - tf + 0.3)
        if g <= 0:
            return None
        down = 1.0 if tf <= T < tu else 0.0
        if T >= tu:
            down = 1 - ease_out(clamp01((T - tu) / 0.4))
        with K.at(c, LX, GY, -70 * down):
            c.translate(-LX, -GY)
            draw_li(c, LX, GY, 0.95, "sad" if down > 0.5 else "smile")
            if T >= tbd:
                with K.at(c, LX - 30, GY - 60, 30, 1):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-40, -14, 80, 28), 10, 10, K.paint("#F6D9B8"))
                    c.drawRoundRect(skia.Rect.MakeXYWH(-40, -14, 80, 28), 10, 10, wb.marker(ORANGE, 3))
        c.drawCircle(LX - 260, GY - 20, 50, K.paint("#B0A090"))
        K.text(c, "挫折", LX - 260, GY - 120, 44, "hand", GRAY)
        if T >= tu:
            with K.at(c, cx + 300, cy - 200, 0, C.slam_scale(T - tu)):
                chip(c, 0, 0, "别放弃", GREEN_FILL, GREEN, 56)
        return None
    ev(j, k_fall, scene, "tom", 0.75)
    b.hit(j, k_band, "pop", 0.75, "处理伤口")
    b.hit(j, k_up, "ding", 0.8, "站起来")


screen11()


# ================================================================ 屏 12：第三步：每过一站打一个勾，怀疑的人探头看
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_book = kq(j, wp(17, 0, 0.6), 1)
    k_ticks = nx(j, wp(17, 1, 0.5), k_book)
    k_peek = nx(j, wp(17, 3, 0.4), k_ticks)
    STOPS = ["报名", "学一章", "做题"]
    L.note(*STOPS, "进展")

    def scene(c, kk, T):
        tbk, tt, tp = tb(j, k_book), tb(j, k_ticks), tb(j, k_peek)
        g = pop_scale(T - tbk)
        if g <= 0:
            return None
        with K.at(c, cx - 60, cy - 120, 0, g):
            box(c, 0, 0, 480, 420, NOTE_FILL, ORANGE, 6, 10)
            K.text(c, "进展", 0, -160, 52, "hand", ORANGE)
            for i, s_ in enumerate(STOPS):
                y = -60 + i * 100
                K.text(c, s_, -40, y, 48, "hand", INK)
                if T >= tt + i * 0.25:
                    c.drawPath(check(140, y, 30), wb.marker(GREEN, 9))
        if T >= tp:
            for i, x in enumerate((cx + 330, cx + 460)):
                with at_pop(c, x, GY, pop_scale(T - tp - i * 0.12)):
                    if i:
                        draw_ace(c, x, GY, 0.75, mood="flat", head_dx=-20)
                    else:
                        draw_wang(c, x, GY, 0.75, mood="o", head_dx=-20)
        return None
    ev(j, k_book, scene, "wood_high", 0.65)
    b.hit(j, k_ticks, "ding", 0.75, "记一笔")
    b.hit(j, k_peek, "pop", 0.7, "怀疑的人探头看")


screen12()


# ================================================================ 屏 13：好处：曲线越往后越平缓，小李越走越稳
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_curve = kq(j, wp(18, 0, 0.6), 0)
    k_walk = nx(j, wp(18, 1, 0.5), k_curve)
    k_bold = nx(j, wp(18, 2, 0.5), k_walk)
    x0, x1, y0 = cx - 480, cx + 480, cy + 360
    pts = curve_pts(x0, x1, y0, 640)
    b.path(j, k_curve, k_curve + 0.8, P(*pts), RED, 12, sfx="shaker", gain=0.7)
    L.note("有底气")

    def li(c, kk, T):
        tw, tb_ = tb(j, k_walk), tb(j, k_bold)
        if T < tw:
            return None
        f = ease_in_out(clamp01((T - tw) / 1.4))
        i = int(lerp(5, len(pts) - 1, f))
        x, y = pts[i]
        with at_pop(c, x, y, 1):
            draw_li(c, x, y, 0.5, "smile")
        if T >= tb_:
            sparkle(c, x, y - 160, T - tb_, YELLOW, 10, 50, 120)
            K.text(c, "有底气", cx + 200, cy + 180, 64, "hand", GREEN, clamp01((T - tb_) / 0.2))
        return None
    ev(j, k_walk, li, "pop", 0.65)
    b.hit(j, k_bold, "ding", 0.85, "越走越有底气")


screen13()


# ================================================================ 屏 14：评论区；小李走在路上，路标往前；下一讲预告
def _enc(c, T, te, th, cx, cy):
    LX, LY = cx - 300, cy + 640
    x, dy, _ = C.walk(T, te, 2.0, LX, LX + 200, 8)
    C.line(c, (cx - 560, LY + 6), (cx + 560, LY + 6), "#8B6B43", 6)
    with at_pop(c, x, LY + dy, pop_scale(T - te)):
        draw_li(c, x, LY + dy, 0.9, "smile")
    if T >= th:
        with K.at(c, cx + 300, LY, 0, pop_scale(T - th)):
            C.line(c, (0, 0), (0, -260), "#7A5E3A", 8)
            c.drawPath(P((-20, -280), (160, -280), (200, -230), (160, -180), (-20, -180), close=True), K.paint(NOTE_FILL))
            c.drawPath(P((-20, -280), (160, -280), (200, -230), (160, -180), (-20, -180), close=True), wb.marker(ORANGE, 5))
            K.text(c, "路上", 80, -230, 44, "hand", INK)
        sparkle(c, x, LY - 380, T - th, YELLOW, 10, 60, 130)


L.note("路上")


def _icon(c, x, y, t):
    box(c, x, y + 20, 160, 40, "#FFFFFF", BLACK, 4, 20)
    f = min(1.0, (t % 2.0) / 1.2)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 76, y + 6, 152 * (0.99 if f < 0.8 else 0.0), 28), 14, 14, K.paint(GREEN))
    K.text(c, "99%", x, y - 40, 36, "black", RED)


L.note("99%")
KT.ending(14, "你想做的那件事？", ["转岗", "考个证", "开始跑步"], 20, 21, _enc, 22,
          ["优势那么大", "怎么还会输？"], enc_piece=0, next_icon=_icon)

# ================================================================ 收尾
L.finish(cover_shot=7, square_shot=8, notes=NOTES)
L.export(globals())
