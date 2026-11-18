"""《资治通鉴》09 三顾：想请高手帮忙，为什么总被拒？（白板手绘 + AI 旁白，竖屏 2:3）

复刻实验：先看小李发“在吗？”、喊人“过来一下”的结果；再看刘备怎么请诸葛亮——到处打听、徐庶“此人可就见，不可屈致”、
“凡三往，乃见”、屏人坦白处境、隆中对、“犹鱼之有水”；最后照刘备的做法把请教重做一遍（三步）。
古人的屏画在卷轴框里，今人在办公室。文案见 zizhi/PLAN.md「### 09」。
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
                          draw_wang, flag, gu, name_tag, phone, pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "通鉴里的故事", 4),
    ([6, 7], "叫不来", 5),
    ([8, 9], "三往乃见", 6),
    ([10, 11], "隆中对", 7),
    ([12, 13], "说回我们自己", 8),
    ([14], "第一步", 9),
    ([15], "第二步", 10),
    ([16], "第三步", 11),
    ([17], "好处", 12),
    ([18, 19, 20, 21], "评论区见", 13),
]

THEME = ZT.get("09")
L = Z.Lesson("09", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(12)]
Z_ = 0.72
KT = Z.Kit(L, R)

NOTES = [
    "出处：司马光《资治通鉴》卷六十五 汉纪五十七（建安十二年）。",
    "原文：徐庶谓备曰“诸葛孔明，卧龙也……此人可就见，不可屈致也。将军宜枉驾顾之”；“备由是诣亮，凡三往，乃见。因屏人曰：汉室倾颓……”；"
    "隆中对“跨有荆、益……外结好孙权”；“孤之有孔明，犹鱼之有水也”。",
    "今人（小李、小王、前辈）为虚构示意；古人造型为示意。",
]

LIU, XU, ZHUGE = "green", "gray", "teal"


def hut(c, x, y, door=0.0, a=1.0):
    """茅屋：(x, y) 墙脚中点，door 0–1 开门。"""
    roof = P((x - 230, y - 200), (x, y - 360), (x + 230, y - 200), close=True)
    c.drawPath(roof, K.paint("#D8C38A", a))
    c.drawPath(roof, wb.marker("#8A6A3A", 6, a))
    for q in range(5):
        C.line(c, (x - 180 + q * 90, y - 220), (x - 150 + q * 70, y - 320), "#8A6A3A", 3, a)
    box(c, x, y - 100, 360, 200, "#EFE4CC", "#8A6A3A", 6, 4, a)
    dw = 90 * (1 - 0.8 * door)
    c.drawRect(skia.Rect.MakeXYWH(x - 45, y - 150, dw, 150), K.paint("#8A5A2E", a))
    c.drawRect(skia.Rect.MakeXYWH(x - 45, y - 150, 90, 150), wb.marker(INK, 4, a))


def zhuge(c, x, y, s, **kw):
    gu(c, x, y, s, ZHUGE, hat="guan", **kw)
    hy = y - 290 * s
    with K.at(c, x + 90 * s, hy + 150 * s, -20):
        c.drawOval(skia.Rect.MakeXYWH(-30 * s, -50 * s, 60 * s, 90 * s), K.paint("#FFFFFF"))
        c.drawOval(skia.Rect.MakeXYWH(-30 * s, -50 * s, 60 * s, 90 * s), wb.marker(GRAY, 3))
        C.line(c, (0, 40 * s), (0, 80 * s), "#8A5A2E", 5)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：小李给前辈发“在吗？”，时钟从下午转到天黑
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_send = kq(j, wp(0, 3, 0.3), 1)
    k_clock = nx(j, wp(1, 0, 0.5), k_send)
    k_none = nx(j, wp(1, 1, 0.5), k_clock)
    LX, PX = cx - 330, cx + 320
    L.note("在吗？", "前辈")

    def scene(c, kk, T):
        ts, tc, tn = tb(j, k_send), tb(j, k_clock), tb(j, k_none)
        g = pop_scale(T - tb(j, k_li))
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "sad" if T >= tn else "flat", rh=(LX + 110, GY - 230))
            phone(c, LX + 130, GY - 260, 0.7)
        with at_pop(c, PX, GY, g):
            desk(c, PX - 60, GY - 170, 320)
            draw_ace(c, PX + 120, GY, 0.9, mood="flat")
            name_tag(c, PX + 120, GY - 380, "前辈", "#4A5160", 36)
        if T >= ts:
            f = ease_out(clamp01((T - ts) / 0.5))
            with K.at(c, lerp(LX + 130, PX, f), lerp(cy - 120, cy - 320, f), 0, 1):
                bubble_box(c, 0, 0, 220, 100, -1)
                K.text(c, "在吗？", 0, 0, 48, "hand", INK)
        if T >= tc:
            hrs = clamp01((T - tc) / 1.2)
            with K.at(c, cx, cy - 350, 0, pop_scale(T - tc)):
                c.drawCircle(0, 0, 100, K.paint("#FFFFFF" if hrs < 0.6 else "#3A4466"))
                c.drawPath(wb.clock(0, 0, 100), wb.marker(BLACK, 6))
                a = math.radians(-90 + 360 * 3 * hrs)
                C.line(c, (0, 0), (70 * math.cos(a), 70 * math.sin(a)), RED, 6)
        if T >= tn:
            K.text(c, "没回音", PX - 40, cy - 120, 56, "hand", GRAY, clamp01((T - tn) / 0.2))
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_send, "pop", 0.75, "在吗")
    b.hit(j, k_clock, "shaker", 0.7, "等了一下午")
    b.hit(j, k_none, "tom", 0.75, "没回音")
    L.note("没回音")


screen1()


# ================================================================ 屏 2（drop）：小李喊别的部门“过来一下”，对方摆手“没空”
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_call = kq(j, wp(2, 1, 0.4), 0)
    L.note("过来一下", "没空")

    def scene(c, kk, T):
        tc, td = tb(j, k_call), tb(j, dk)
        g = pop_scale(T - tb(j, 0))
        if g <= 0:
            return None
        C.line(c, (cx, cy - 300), (cx, GY), GRAY, 4)
        with at_pop(c, cx - 320, GY, g):
            draw_li(c, cx - 320, GY, 0.95, "flat", rh=(cx - 180, GY - 360) if T >= tc else None)
        with at_pop(c, cx + 320, GY, g):
            draw_wang(c, cx + 320, GY, 0.95, mood="flat",
                      lh=(cx + 200 + 20 * math.sin((T - td) * 14), GY - 330) if T >= td else None)
        if T >= tc:
            with K.at(c, cx - 230, cy - 330, 0, pop_scale(T - tc)):
                bubble_box(c, 0, 0, 300, 110, -1)
                K.text(c, "过来一下", 0, 0, 52, "hand", INK)
        if T >= td:
            with K.at(c, cx + 260, cy - 200, 0, C.slam_scale(T - td)):
                bubble_box(c, 0, 0, 220, 110, 1)
                K.text(c, "没空", 0, 0, 60, "hand", RED)
        return None
    ev(j, 0, scene, "wood_low", 0.6)
    b.hit(j, k_call, "pop", 0.7, "喊人过来")
    b.hit(j, dk, "kick", 0.9, "没空")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：小李一个人扛着一大摞活
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_alone = kq(j, wp(3, 1, 0.4), 0)
    k_pile = nx(j, wp(3, 2, 0.4), k_alone)
    L.note("硬扛")

    def scene(c, kk, T):
        ta, tp = tb(j, k_alone), tb(j, k_pile)
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        n = 2 + (4 if T >= tp else 0)
        sq = 1 - 0.04 * n
        x = cx - 60
        with at_pop(c, x, GY, g):
            C.draw_li(c, x, GY, 1.0, "sad", squash=sq, lh=(x - 90, GY - 330 * sq), rh=(x + 90, GY - 330 * sq))
            for i in range(n):
                box(c, x + (i % 2) * 14 - 7, GY - 360 * sq - i * 58, 260, 54, ("#FFFFFF", NOTE_FILL)[i % 2], GRAY, 4, 4)
        if T >= tp:
            with K.at(c, cx + 330, cy - 300, -5, C.slam_scale(T - tp)):
                chip(c, 0, 0, "硬扛", RED_FILL, RED, 60)
        return None
    ev(j, k_alone, scene, "wood_low", 0.65)
    b.hit(j, k_pile, "tom", 0.8, "闷头硬扛")


screen3()


# ================================================================ 屏 4：竹简“卷六十五”；刘备在新野；有人递上名牌“卧龙”
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(4, 0, 0.3), 0)
    k_liu = nx(j, wp(4, 1, 0.4), k_book)
    k_ask = nx(j, wp(5, 0, 0.5), k_liu)
    k_long = nx(j, wp(5, 2, 0.4), k_ask)
    KT.book(j, k_book, "卷六十五", "汉纪五十七")
    L.note("刘备", "新野", "卧龙")

    def scene(c, kk, T):
        tl, ta, tg = tb(j, k_liu), tb(j, k_ask), tb(j, k_long)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, cx + 250, GY, g):
            city_wall(c, cx + 250, GY - 300, 300, 160, label="新野")
            gu(c, cx + 150, GY, 0.85, LIU, hat="guan", beard="black", rh=(cx + 290, GY - 290) if T >= ta else None)
            name_tag(c, cx + 150, GY - 400, "刘备", "#3F6B3A", 40)
        if T >= ta:
            with at_pop(c, cx + 430, GY, pop_scale(T - ta)):
                gu(c, cx + 430, GY, 0.7, XU, hat="bun", mood="smile")
        if T >= tg:
            with K.at(c, cx + 300, cy - 260, -6, C.slam_scale(T - tg)):
                box(c, 0, 0, 200, 100, NOTE_FILL, ORANGE, 5, 10)
                K.text(c, "卧龙", 0, 0, 60, "serif_black", INK)
            sparkle(c, cx + 300, cy - 260, T - tg, YELLOW, 8, 60, 120)
        return None
    b.custom(j, k_liu, k_liu + 0.3, scene, sfx="tom", gain=0.75)
    b.hit(j, k_ask, "pop", 0.7, "到处打听")
    b.hit(j, k_long, "ding", 0.8, "卧龙值得一见")


screen4()


# ================================================================ 屏 5：刘备招手“带他来”；徐庶摇头：只能去见，叫不来
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_liu = 0
    k_call = kq(j, wp(6, 1, 0.4), 1)
    k_xu = nx(j, wp(7, 0, 0.6), k_call)
    k_no = nx(j, wp(7, 3, 0.4), k_xu)
    LX, XX = cx - 330, cx + 300
    L.note("带他来", "叫不来", "徐庶")

    def scene(c, sc, T):
        tc, tx, tn = tb(j, k_call), tb(j, k_xu), tb(j, k_no)
        with at_pop(c, LX, GY, sc):
            gu(c, LX, GY, 0.95, LIU, hat="guan", beard="black", mood="smile",
               rh=(LX + 150, GY - 300 + 20 * math.sin((T - tc) * 8)) if tc <= T < tn else None)
            name_tag(c, LX, GY - 430, "刘备", "#3F6B3A", 40)
        if T >= tc:
            with K.at(c, LX + 160, cy - 300, 0, pop_scale(T - tc)):
                bubble_box(c, 0, 0, 280, 110, -1)
                K.text(c, "带他来", 0, 0, 54, "hand", INK)
        if T >= tx:
            shake = 10 * math.sin((T - tn) * 14) * math.exp(-(T - tn) * 2) if T >= tn else 0
            with at_pop(c, XX, GY, pop_scale(T - tx)):
                gu(c, XX, GY, 0.9, XU, hat="bun", beard="black", head_dx=shake)
                name_tag(c, XX, GY - 410, "徐庶", "#5E5E58", 40)
        if T >= tn:
            with K.at(c, XX - 40, cy - 160, 4, C.slam_scale(T - tn)):
                bubble_box(c, 0, 0, 300, 120, 1)
                K.text(c, "叫不来", 0, 0, 58, "hand", RED)
            with K.at(c, cx, cy + 100, 0, pop_scale(T - tn - 0.2)):
                c.drawPath(wb.arrow((-200, 0), (200, 0), 0.0, 30), wb.marker(GREEN, 9))
                K.text(c, "去见", 0, -50, 44, "hand", GREEN)
        return None
    L.note("去见")
    ev(j, k_liu, L.pop_fn(j, k_liu, scene), "muyu", 0.6)
    b.hit(j, k_call, "pop", 0.7, "带他来见我")
    b.hit(j, k_xu, "wood_low", 0.65, "徐庶")
    b.hit(j, k_no, "rim", 0.8, "叫是叫不来的")


screen5()


# ================================================================ 屏 6：刘备三次走到茅屋门口，第三次门开；屋里屏退旁人，两人对坐
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 160
    k_go = [kq(j, wp(8, 1, 0.3), 0)]
    k_go.append(nx(j, wp(8, 2, 0.2), k_go[0]))
    k_go.append(nx(j, wp(8, 2, 0.8), k_go[1]))
    k_meet = nx(j, wp(8, 3, 0.4), k_go[2])
    k_talk = nx(j, wp(9, 3, 0.3), k_meet)
    HX = cx + 300
    L.note("隆中", "一", "二", "三")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_go[0]) + 0.3)
        if g <= 0:
            return None
        tm = tb(j, k_meet)
        with at_pop(c, HX, GY, g):
            hut(c, HX, GY, ease_out(clamp01((T - tm) / 0.4)) if T >= tm else 0)
            name_tag(c, HX, GY - 400, "隆中", "#8A6A3A", 36)
        n = sum(1 for k_ in k_go if T >= tb(j, k_))
        if n:
            t0 = tb(j, k_go[n - 1])
            x, dy, _ = C.walk(T, t0, 0.5, cx - 420, HX - 260, 10)
            with at_pop(c, x, GY + dy, 1):
                gu(c, x, GY + dy, 0.7, LIU, hat="guan", beard="black", mood="smile" if T >= tm else "flat")
            for i in range(n):
                with K.at(c, cx - 420 + i * 110, cy - 380, 0, pop_scale(T - tb(j, k_go[i]))):
                    c.drawCircle(0, 0, 44, K.paint(RED if i == 2 else "#FFFFFF"))
                    c.drawCircle(0, 0, 44, wb.marker(RED, 6))
                    K.text(c, "一二三"[i], 0, 2, 48, "serif_black", "#FFFFFF" if i == 2 else RED)
        if T >= tm:
            sparkle(c, HX, GY - 120, T - tm, YELLOW, 10, 60, 140)
        tt = tb(j, k_talk)
        if T >= tt:
            Y = cy + 500
            with at_pop(c, cx, Y, pop_scale(T - tt)):
                box(c, cx, Y - 70, 200, 30, "#C98B4B", "#7A4A1E", 4, 6)
                gu(c, cx - 170, Y, 0.45, LIU, hat="guan", beard="black", rh=(cx - 90, Y - 120))
                zhuge(c, cx + 170, Y, 0.45, mood="smile")
                for q in range(3):
                    f = ((T - tt) * 0.8 + q * 0.33) % 1
                    c.drawCircle(cx - 60 + 120 * f, Y - 200 - 20 * q, 8, K.paint(GRAY, 1 - f))
        return None
    b.custom(j, k_go[0], k_go[0] + 0.3, scene)
    for i, k_ in enumerate(k_go):
        b.hit(j, k_, "wood_low" if i < 2 else "tom", 0.75, f"第 {i + 1} 次上门")
    b.hit(j, k_meet, "ding", 0.85, "门开了")
    b.hit(j, k_talk, "pop", 0.7, "一五一十说出来")


screen6()


# ================================================================ 屏 7：诸葛亮在地图上画路线：荆州、益州、联合孙权；鱼和水
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_map = kq(j, wp(10, 1, 0.3), 0)
    k_jy = nx(j, wp(10, 2, 0.5), k_map)
    k_sun = nx(j, wp(10, 3, 0.4), k_jy)
    k_fish = nx(j, wp(11, 2, 0.3), k_sun)
    L.note("荆州", "益州", "孙权", "诸葛亮")

    def scene(c, kk, T):
        tm, tj, ts, tf = tb(j, k_map), tb(j, k_jy), tb(j, k_sun), tb(j, k_fish)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        with K.at(c, cx + 80, cy - 220, 0, g):
            box(c, 0, 0, 760, 440, PARCH, PARCH_LINE, 6, 8)
            regs = [("益州", -230, 40, "#D3EDDC", GREEN), ("荆州", 30, 20, "#D5E3F7", BLUE), ("孙权", 250, 40, "#F6C3BE", RED)]
            for i, (nm, x, y, fill, line) in enumerate(regs):
                t0 = tj if i < 2 else ts
                a = clamp01((T - t0 - (0.15 if i == 0 else 0)) / 0.3)
                if a <= 0:
                    continue
                c.drawRoundRect(skia.Rect.MakeXYWH(x - 100, y - 80, 200, 160), 40, 40, K.paint(fill, a))
                c.drawRoundRect(skia.Rect.MakeXYWH(x - 100, y - 80, 200, 160), 40, 40, wb.marker(line, 5, a))
                K.text(c, nm, x, y, 48, "serif_black", line, a)
            if T >= ts:
                f = ease_out(clamp01((T - ts) / 0.4))
                c.drawPath(wb.partial(P((30, 20), (140, -40), (250, 40)), f)[0], wb.marker(ORANGE, 7))
        with at_pop(c, cx - 380, GY, g):
            zhuge(c, cx - 380, GY, 0.9, mood="smile", rh=(cx - 220, GY - 330))
            name_tag(c, cx - 380, GY - 420, "诸葛亮", "#2C6E68", 38)
        if T >= tf:
            gf = pop_scale(T - tf)
            with K.at(c, cx + 220, cy + 280, 0, gf):
                c.drawOval(skia.Rect.MakeXYWH(-220, -60, 440, 140), K.paint("#BFD9EE"))
                c.drawOval(skia.Rect.MakeXYWH(-220, -60, 440, 140), wb.marker("#3F7FB8", 5))
                sw = 20 * math.sin((T - tf) * 6)
                fish = P((-60 + sw, 0), (20 + sw, -36), (80 + sw, 0), (20 + sw, 36), close=True)
                c.drawPath(fish, K.paint(ORANGE))
                c.drawPath(fish, wb.marker(RED, 4))
                c.drawPath(P((-60 + sw, 0), (-100 + sw, -30), (-100 + sw, 30), close=True), K.paint(ORANGE))
                K.text(c, "鱼得水", 0, 120, 52, "hand", BLUE)
        return None
    L.note("鱼得水")
    ev(j, k_map, scene, "wood_high", 0.65)
    b.hit(j, k_jy, "tom", 0.75, "荆州益州")
    b.hit(j, k_sun, "rim", 0.75, "联合孙权")
    b.hit(j, k_fish, "ding", 0.85, "鱼有了水")


screen7()


# ================================================================ 屏 8：说回我们：小李收起手机；“三步”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_put = kq(j, wp(12, 2, 0.4), 1)
    k_3 = nx(j, wp(13, 1, 0.5), k_put)
    LX = cx - 300
    L.note("金贵", "三步")

    def scene(c, sc, T):
        tp = tb(j, k_put)
        f = ease_out(clamp01((T - tp) / 0.4)) if T >= tp else 0
        hy = GY - 290
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 1.0, "flat", rh=(lerp(LX + 120, LX + 50, f), lerp(hy + 80, hy + 200, f)))
            phone(c, lerp(LX + 140, LX + 60, f), lerp(hy + 70, hy + 190, f), lerp(0.7, 0.4, f))
        with K.at(c, cx + 250, cy - 120, 0, sc):
            c.drawCircle(0, 0, 110, K.paint("#FFFFFF"))
            c.drawPath(wb.clock(0, 0, 110), wb.marker(BLACK, 6))
            K.text(c, "金贵", 0, 170, 54, "hand", ORANGE)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_put, "pop", 0.6, "收起手机")
    L.stamp_ev(j, k_3, "三步", cx + 250, cy + 280, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen8()


# ================================================================ 屏 9：第一步：小李在本子上记前辈擅长什么、最近忙什么
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_note = kq(j, wp(14, 0, 0.6), 1)
    k_good = nx(j, wp(14, 1, 0.5), k_note)
    k_busy = nx(j, wp(14, 2, 0.5), k_good)
    L.note("擅长：数据分析", "最近：赶季度报告")

    def scene(c, kk, T):
        tn, tg, tbz = tb(j, k_note), tb(j, k_good), tb(j, k_busy)
        g = pop_scale(T - tn)
        if g <= 0:
            return None
        with K.at(c, cx + 120, cy - 170, -2, g):
            box(c, 0, 0, 640, 360, NOTE_FILL, ORANGE, 6, 10)
            K.text(c, "擅长：数据分析", -270, -60, 50, "hand", INK, clamp01((T - tg) / 0.3), "left")
            K.text(c, "最近：赶季度报告", -270, 60, 50, "hand", INK, clamp01((T - tbz) / 0.3), "left")
        LX = cx - 380
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "flat", rh=(LX + 150, GY - 290))
        return None
    ev(j, k_note, scene, "wood_high", 0.65)
    b.hit(j, k_good, "pop", 0.7, "擅长什么")
    b.hit(j, k_busy, "pop", 0.7, "在忙什么")


screen9()


# ================================================================ 屏 10：第二步：小李走到前辈桌前，手里拿着写好问题的纸
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_walk = kq(j, wp(15, 0, 0.6), 1)
    k_q = nx(j, wp(15, 1, 0.5), k_walk)
    k_no = nx(j, wp(15, 2, 0.5), k_q)
    PX = cx + 300
    L.note("这个表怎么拆？", "在吗？")

    def scene(c, kk, T):
        tw, tq, tn = tb(j, k_walk), tb(j, k_q), tb(j, k_no)
        g = pop_scale(T - tw)
        if g <= 0:
            return None
        with at_pop(c, PX, GY, g):
            desk(c, PX - 40, GY - 170, 300)
            draw_ace(c, PX + 140, GY, 0.9, mood="smile" if T >= tq else "flat")
        x, dy, _ = C.walk(T, tw, 1.0, cx - 500, PX - 260, 10)
        with at_pop(c, x, GY + dy, g):
            draw_li(c, x, GY + dy, 0.9, "smile", rh=(x + 120, GY - 270))
            if T >= tq:
                box(c, x + 150, GY - 300, 120, 150, "#FFFFFF", BLUE, 5, 6)
        if T >= tq:
            with K.at(c, cx - 40, cy - 280, 0, C.slam_scale(T - tq)):
                bubble_box(c, 0, 0, 460, 120, -1)
                K.text(c, "这个表怎么拆？", 0, 0, 52, "hand", INK)
        if T >= tn:
            with K.at(c, cx - 300, cy + 40, 0, pop_scale(T - tn)):
                bubble_box(c, 0, 0, 200, 90, -1, 0.6)
                K.text(c, "在吗？", 0, 0, 40, "hand", GRAY, 0.6)
                c.drawPath(cross(0, 0, 60), wb.marker(RED, 8))
        return None
    ev(j, k_walk, scene, "wood_low", 0.6)
    b.hit(j, k_q, "rim", 0.8, "带着具体问题")
    b.hit(j, k_no, "pop", 0.7, "别只发在吗")


screen10()


# ================================================================ 屏 11：第三步：日历上第一次打叉，换个时间，第二次打勾
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_cal = kq(j, wp(16, 0, 0.6), 1)
    k_x = nx(j, wp(16, 0, 0.95), k_cal)
    k_ok = nx(j, wp(16, 2, 0.5), k_x)
    L.note("周二", "周四")

    def scene(c, kk, T):
        tc, tx, to = tb(j, k_cal), tb(j, k_x), tb(j, k_ok)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 160, 0, g):
            for i, d in enumerate(("周二", "周四")):
                x = -200 + i * 400
                box(c, x, 0, 260, 220, "#FFFFFF", BLACK, 6, 12)
                c.drawRect(skia.Rect.MakeXYWH(x - 130, -110, 260, 60), K.paint(RED_FILL))
                K.text(c, d, x, -80, 44, "hand", INK)
            if T >= tx:
                c.drawPath(wb.partial(cross(-200, 40, 60), ease_out(clamp01((T - tx) / 0.25)))[0], wb.marker(RED, 12))
                c.drawPath(wb.arrow((-60, 40), (60, 40), -0.3, 26), wb.marker(ORANGE, 7, clamp01((T - tx - 0.3) / 0.3)))
            if T >= to:
                c.drawPath(wb.partial(check(200, 40, 56), ease_out(clamp01((T - to) / 0.25)))[0], wb.marker(GREEN, 12))
        with at_pop(c, cx - 300, GY, g):
            draw_li(c, cx - 300, GY, 0.9, "smile" if T >= to else "flat")
        if T >= to:
            sparkle(c, cx + 200, cy - 120, T - to, YELLOW, 10, 60, 130)
        return None
    ev(j, k_cal, scene, "wood_high", 0.65)
    b.hit(j, k_x, "rim", 0.75, "第一次没约上")
    b.hit(j, k_ok, "ding", 0.85, "换个时间约上了")


screen11()


# ================================================================ 屏 12：好处：前辈给小李指路，弯路变直
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_road = kq(j, wp(17, 0, 0.5), 0)
    k_point = nx(j, wp(17, 0, 0.95), k_road)
    k_straight = nx(j, wp(17, 1, 0.5), k_point)

    def scene(c, kk, T):
        tr, tp, ts = tb(j, k_road), tb(j, k_point), tb(j, k_straight)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        f = ease_in_out(clamp01((T - ts) / 0.6)) if T >= ts else 0
        pts = []
        for i in range(41):
            u = i / 40
            y = lerp(cy + 300, cy - 400, u)
            x = cx + 120 + 260 * math.sin(u * 9) * (1 - f)
            pts.append((x, y))
        c.drawPath(P(*pts), wb.marker("#8B6B43", 26, 0.5))
        c.drawPath(P(*pts), wb.marker("#8B6B43", 4))
        with at_pop(c, cx - 380, GY, g):
            draw_ace(c, cx - 200, GY, 0.85, mood="smile", rh=(cx - 40, GY - 350) if T >= tp else None)
            draw_li(c, cx - 420, GY, 0.85, "smile" if T >= ts else "flat")
        if T >= ts:
            sparkle(c, cx + 120, cy - 400, T - ts, YELLOW, 10, 60, 130)
        return None
    ev(j, k_road, scene, "wood_low", 0.6)
    b.hit(j, k_point, "pop", 0.7, "前辈指路")
    b.hit(j, k_straight, "ding", 0.85, "弯路变直")


screen12()


# ================================================================ 屏 13：评论区；小李跑了三趟终于敲开门；下一讲预告
def _enc(c, T, te, th, cx, cy):
    LX, LY = cx - 250, cy + 640
    n = 1 + int(clamp01((T - te) / max(0.3, th - te)) * 2.99)
    for i in range(n):
        x = cx - 480 + i * 120
        c.drawPath(P((x, LY + 10), (x + 40, LY + 10)), wb.marker(GRAY, 6))
    with at_pop(c, LX, LY, pop_scale(T - te)):
        draw_li(c, LX, LY, 0.9, "smile" if T >= th else "flat", rh=(LX + 150, LY - 300) if T >= th else None)
    DX = cx + 240
    op = ease_out(clamp01((T - th) / 0.4)) if T >= th else 0
    box(c, DX, LY - 230, 260, 460, "#E3D2BE", "#5E4128", 6, 6)
    c.drawRect(skia.Rect.MakeXYWH(DX - 115, LY - 450, 230 * (1 - 0.7 * op), 440), K.paint("#C98B4B"))
    if op:
        c.drawRect(skia.Rect.MakeXYWH(DX - 115 + 230 * (1 - 0.7 * op), LY - 450, 230 * 0.7 * op, 440), K.paint("#FFF6D6"))
        sparkle(c, DX, LY - 250, T - th, YELLOW, 10, 60, 150)
    K.text(c, "第三趟", DX - 300, LY - 420, 54, "hand", GREEN, clamp01((T - th) / 0.3))


L.note("第三趟")


def _icon(c, x, y, t):
    with K.at(c, x, y, -4):
        box(c, 0, 0, 170, 140, "#FFFFFF", GRAY, 5, 6)
        for q in range(3):
            box(c, 0, 50 - q * 26, 120, 22, NOTE_FILL, ORANGE, 3, 3)


KT.ending(13, "你最想请教谁？", ["带你的师傅", "隔壁组老大", "以前的领导"], 19, 20, _enc, 21,
          ["天天加班", "哪还有空学东西？"], enc_piece=1, next_icon=_icon)

# ================================================================ 收尾
L.finish(cover_shot=6, square_shot=6, notes=NOTES)
L.export(globals())
