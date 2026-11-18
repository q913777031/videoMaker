"""《资治通鉴》14 兼听：只听一个人说，为什么总看走眼？（白板手绘 + AI 旁白，竖屏 2:3）

两人对比：先看只听一边的后果；唐太宗问魏征“人主何为而明，何为而暗”，“兼听则明，偏信则暗”，秦二世偏信赵高、隋炀帝偏信虞世基；
“兼听广纳则贵臣不得拥蔽，下情得以上通”，太宗曰“善”；再把同一件事分成两栏：小李听一面之词就站队，小王多问两人、看聊天记录发现是误会；
最后三步（问三方、追问谁说的、留一天）。本讲是石墨板底（深色）。文案见 zizhi/PLAN.md「### 14」。
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
                          draw_wang, gu, name_tag, phone, pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "通鉴里的故事", 4),
    ([6, 7], "偏信的下场", 5),
    ([8, 9], "下情上通", 6),
    ([10], "兼听", 7),
    ([11, 12], "两人对比", 8),
    ([13, 14], "说回我们自己", 9),
    ([15], "第一步", 10),
    ([16], "第二步", 11),
    ([17], "第三步", 12),
    ([18], "好处", 13),
    ([19, 20, 21, 22], "评论区见", 14),
]

THEME = ZT.get("14")
L = Z.Lesson("14", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(13)]
Z_ = 0.72
KT = Z.Kit(L, R, frame_alpha=0.12)

NOTES = [
    "出处：司马光《资治通鉴》卷一九二 唐纪八（贞观二年）。",
    "原文：“上问魏征曰：人主何为而明，何为而暗？对曰：兼听则明，偏信则暗。……秦二世偏信赵高，以成望夷之祸；……隋炀帝偏信虞世基，"
    "以致彭城阁之变。是故人君兼听广纳，则贵臣不得拥蔽，而下情得以上通也。上曰：善！”",
    "“他还蒙在鼓里”概括虞世基瞒报各地起事（见通鉴隋纪），不是本段原文。今人（小李、小王、同事、领导）为虚构示意；古人造型为示意。",
]

TANG, WEI, ER, ZHAO, YANG, YU = "ochre", "teal", "red", "gray", "purple", "brown"


def ear(c, x, y, s=1.0, a=1.0):
    with K.at(c, x, y, 0, s):
        c.drawOval(skia.Rect.MakeXYWH(-40, -70, 80, 140), K.paint("#FFFFFF", a))
        c.drawOval(skia.Rect.MakeXYWH(-40, -70, 80, 140), wb.marker(BLACK, 6, a))
        ar = skia.Path()
        ar.addArc(skia.Rect.MakeXYWH(-20, -40, 40, 70), 90, 220)
        c.drawPath(ar, wb.marker(BLACK, 4, a))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：同事凑在小李耳边吐槽，小李心里给另一个人打叉；真相卡片翻过来
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_pair = kq(j, wp(0, 1, 0.3), 0)
    k_x = nx(j, wp(0, 4, 0.4), k_pair)
    k_flip = nx(j, wp(1, 1, 0.5), k_x)
    k_diff = nx(j, wp(1, 2, 0.4), k_flip)
    LX, AX, WX = cx - 250, cx - 420, cx + 360
    L.note("他偷懒", "真相", "他在加班")

    def scene(c, kk, T):
        tp, tx, tf, td = tb(j, k_pair), tb(j, k_x), tb(j, k_flip), tb(j, k_diff)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            draw_ace(c, AX, GY, 0.9, mood="smug", rh=(LX - 60, GY - 280))
            draw_li(c, LX, GY, 0.9, "flat")
            draw_wang(c, WX, GY, 0.9, mood="flat")
        with K.at(c, AX + 70, cy - 220, 0, g):
            bubble_box(c, 0, 0, 260, 100, -1)
            K.text(c, "他偷懒", 0, 0, 48, "hand", INK)
        if T >= tx:
            with K.at(c, WX, cy - 120, 0, C.slam_scale(T - tx)):
                c.drawPath(cross(0, 0, 80), wb.marker(RED, 12))
        if T >= tf:
            f = clamp01((T - tf) / 0.4)
            sx = abs(math.cos(math.pi * f))
            with K.at(c, cx + 120, cy - 380, 0, 1):
                c.scale(max(0.05, sx), 1)
                box(c, 0, 0, 340, 150, "#FFFFFF" if f < 0.5 else GREEN_FILL, GRAY if f < 0.5 else GREEN, 6, 12)
                K.text(c, "真相" if f < 0.5 else "他在加班", 0, 0, 50, "hand", INK)
        if T >= td:
            sparkle(c, cx + 120, cy - 380, T - td, YELLOW, 8, 60, 130)
        return None
    ev(j, k_pair, scene, "wood_low", 0.6)
    b.hit(j, k_x, "rim", 0.8, "心里打了叉")
    b.hit(j, k_flip, "pop", 0.75, "真相翻过来")
    b.hit(j, k_diff, "ding", 0.75, "完全两样")


screen1()


# ================================================================ 屏 2（drop）：领导只听一个人汇报就拍板，全组人抱着文件返工
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_rep = kq(j, wp(2, 0, 0.5), 0)
    k_ok = nx(j, wp(2, 1, 0.5), k_rep)
    L.note("就这么定", "返工")

    def scene(c, kk, T):
        tr, to, td = tb(j, k_rep), tb(j, k_ok), tb(j, dk)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        BX = cx - 360
        with at_pop(c, BX, GY, g):
            C.draw_boss(c, BX, GY, 0.95, mood="flat", rh=(BX + 120, GY - 330) if T >= to else None)
            draw_ace(c, BX + 260, GY, 0.85, mood="smug", lh=(BX + 150, GY - 260))
        if T >= to:
            with K.at(c, BX + 40, cy - 330, 0, C.slam_scale(T - to)):
                bubble_box(c, 0, 0, 300, 110, -1)
                K.text(c, "就这么定", 0, 0, 52, "hand", INK)
        if T >= td:
            for i, x in enumerate((cx + 200, cx + 340, cx + 480)):
                with at_pop(c, x, GY, pop_scale(T - td - i * 0.1)):
                    draw_li(c, x, GY, 0.7, "sad", lh=(x - 50, GY - 170), rh=(x + 50, GY - 170))
                    box(c, x, GY - 180, 110, 60, "#FFFFFF", GRAY, 4, 4)
            seal(c, cx + 340, cy - 120, "返工", 80, -6, C.slam_scale(T - td))
        return None
    ev(j, k_rep, scene, "wood_low", 0.6)
    b.hit(j, k_ok, "rim", 0.8, "拍板")
    b.hit(j, dk, "kick", 0.9, "全组返工")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：一只眼睛被蒙住一半，看到的画面只有一半
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_eye = kq(j, wp(3, 0, 0.5), 0)
    k_half = nx(j, wp(3, 1, 0.5), k_eye)
    L.note("看走眼")

    def scene(c, kk, T):
        te, th = tb(j, k_eye), tb(j, k_half)
        g = pop_scale(T - te)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 200, 0, g):
            c.drawOval(skia.Rect.MakeXYWH(-320, -140, 640, 280), K.paint("#FFFFFF"))
            c.drawOval(skia.Rect.MakeXYWH(-320, -140, 640, 280), wb.marker(INK, 8))
            c.drawCircle(0, 0, 100, K.paint(INK))
            c.drawCircle(30, -30, 26, K.paint("#FFFFFF"))
            if T >= th:
                f = ease_out(clamp01((T - th) / 0.4))
                c.drawRect(skia.Rect.MakeXYWH(0, -160, 340 * f, 320), K.paint("#5E4128", 0.92))
        if T >= th:
            with K.at(c, cx, cy + 260, -4, C.slam_scale(T - th - 0.2)):
                chip(c, 0, 0, "看走眼", RED_FILL, RED, 64)
        return None
    ev(j, k_eye, scene, "wood_low", 0.6)
    b.hit(j, k_half, "tom", 0.8, "只看一半")


screen3()


# ================================================================ 屏 4：竹简“卷一九二”；太宗问魏征；“兼听则明 偏信则暗”两根竹简落下
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(4, 1, 0.3), 0)
    k_ask = nx(j, wp(4, 2, 0.4), k_book)
    k_ming = nx(j, wp(5, 1, 0.5), k_ask)
    k_an = nx(j, wp(5, 2, 0.5), k_ming)
    KT.book(j, k_book, "卷一九二", "唐纪八")
    L.note("唐太宗", "魏征", "兼听则明", "偏信则暗")

    def scene(c, kk, T):
        ta, tm, tn = tb(j, k_ask), tb(j, k_ming), tb(j, k_an)
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        TX, WX = cx + 40, cx + 400
        with at_pop(c, TX, GY, g):
            gu(c, TX, GY, 0.8, TANG, hat="futou", beard="black", rh=(TX + 130, GY - 290))
            name_tag(c, TX, GY - 410, "唐太宗", "#8A5A1E", 34)
        with at_pop(c, WX, GY, g):
            gu(c, WX, GY, 0.8, WEI, hat="futou", beard="black", bow=T < tm, rh=(WX - 130, GY - 300) if T >= tm else None)
            name_tag(c, WX, GY - 410, "魏征", "#2C6E68", 34)
        for i, (t0, s_, x) in enumerate(((tm, "兼听则明", cx + 330), (tn, "偏信则暗", cx + 130))):
            if T < t0:
                continue
            with K.at(c, x, cy - 250, 0, C.slam_scale(T - t0)):
                bamboo_slips(c, 0, 0, 110, 440, n=1)
                slip_text(c, 0, -160, s_, 74, GREEN if i == 0 else RED)
        return None
    b.custom(j, k_ask, k_ask + 0.3, scene, sfx="tom", gain=0.75)
    b.hit(j, k_ming, "bangzi", 0.8, "兼听则明")
    b.hit(j, k_an, "bangzi", 0.8, "偏信则暗")


screen4()


# ================================================================ 屏 5：秦二世身后只站着赵高；隋炀帝被虞世基捂住耳朵，外面烽火
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_er = kq(j, wp(6, 1, 0.4), 0)
    k_er_end = nx(j, wp(6, 2, 0.5), k_er)
    k_yang = nx(j, wp(7, 0, 0.5), k_er_end)
    k_fire = nx(j, wp(7, 1, 0.5), k_yang)
    k_yang_end = nx(j, wp(7, 3, 0.5), k_fire)
    L.note("秦二世", "赵高", "隋炀帝", "虞世基")

    def scene(c, kk, T):
        te, tee, ty, tf, tye = tb(j, k_er), tb(j, k_er_end), tb(j, k_yang), tb(j, k_fire), tb(j, k_yang_end)
        g = pop_scale(T - te)
        if g <= 0:
            return None
        Y1 = cy - 30
        C.line(c, (cx - 560, cy + 80), (cx + 560, cy + 80), GRAY, 4)
        with at_pop(c, cx - 280, Y1, g):
            gu(c, cx - 300, Y1, 0.6, ER, hat="guan", mood="sad" if T >= tee else "smile")
            gu(c, cx - 150, Y1, 0.6, ZHAO, hat="guan", beard="black", mood="smile", lh=(cx - 250, Y1 - 210))
            name_tag(c, cx - 300, Y1 - 260, "秦二世", "#9C2F25", 30)
            name_tag(c, cx - 150, Y1 - 260, "赵高", "#5E5E58", 30)
        if T >= tee:
            seal(c, cx + 200, cy - 280, "被逼死", 56, -6, C.slam_scale(T - tee))
        if T >= ty:
            with at_pop(c, cx - 200, GY, pop_scale(T - ty)):
                gu(c, cx - 220, GY, 0.65, YANG, hat="futou", beard="black", mood="smile")
                hy = GY - 290 * 0.65
                gu(c, cx - 70, GY, 0.6, YU, hat="futou", beard="black", lh=(cx - 250, hy), rh=(cx - 190, hy - 10))
                name_tag(c, cx - 220, GY - 280, "隋炀帝", "#6B3F7A", 30)
                name_tag(c, cx - 70, GY - 270, "虞世基", "#5E4128", 30)
        if T >= tf:
            for i in range(3):
                x = cx + 220 + i * 110
                h = (80 + 30 * math.sin(T * 8 + i)) * pop_scale(T - tf - i * 0.1)
                c.drawPath(P((x - 30, GY - 60), (x, GY - 60 - h), (x + 30, GY - 60), close=True), K.paint(ORANGE))
                c.drawPath(P((x - 30, GY - 60), (x, GY - 60 - h), (x + 30, GY - 60), close=True), wb.marker(RED, 4))
        if T >= tye:
            seal(c, cx + 330, GY - 260, "兵变", 60, -6, C.slam_scale(T - tye))
        return None
    L.note("被逼死", "兵变")
    ev(j, k_er, scene, "muyu", 0.65)
    b.hit(j, k_er_end, "kick", 0.8, "秦二世被逼死")
    b.hit(j, k_yang, "pop", 0.7, "隋炀帝只信虞世基")
    b.hit(j, k_fire, "shaker", 0.75, "天下大乱")
    b.hit(j, k_yang_end, "kick", 0.85, "死于兵变")


screen5()


# ================================================================ 屏 6：宫墙上一扇扇门打开，下面的声音传上来；太宗点头“善”
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_wall = kq(j, wp(8, 1, 0.4), 0)
    k_open = nx(j, wp(8, 2, 0.5), k_wall)
    k_up = nx(j, wp(8, 4, 0.4), k_open)
    k_good = nx(j, wp(9, 1, 0.4), k_up)
    L.note("善")

    def scene(c, kk, T):
        tw, to, tu, tg = tb(j, k_wall), tb(j, k_open), tb(j, k_up), tb(j, k_good)
        g = pop_scale(T - tw)
        if g <= 0:
            return None
        with at_pop(c, cx, cy + 60, g):
            city_wall(c, cx, cy + 60, 900, 300)
        for i in range(3):
            x = cx - 300 + i * 300
            op = ease_out(clamp01((T - to - i * 0.12) / 0.4)) if T >= to else 0
            c.drawRect(skia.Rect.MakeXYWH(x - 60, cy - 120, 120, 180), K.paint("#5E4128" if op < 0.5 else NOTE_FILL))
            c.drawRect(skia.Rect.MakeXYWH(x - 60, cy - 120, 120, 180), wb.marker(INK, 4))
            if T >= tu:
                for q in range(2):
                    f = ((T - tu) * 0.9 + q * 0.5 + i * 0.2) % 1
                    c.drawCircle(x + 20 * math.sin(q + T * 2), cy - 160 - 220 * f, 12, K.paint(GREEN, 1 - f))
        for i in range(5):
            x = cx - 400 + i * 200
            with at_pop(c, x, GY, pop_scale(T - tu + 0.2 - i * 0.05)):
                gu(c, x, GY, 0.4, ("gray", "brown", "ochre", "blue", "green")[i], hat="bun", mood="smile")
        if T >= tg:
            with at_pop(c, cx, cy - 400, pop_scale(T - tg)):
                gu(c, cx - 200, cy - 280, 0.45, TANG, hat="futou", beard="black", mood="smile")
            seal(c, cx + 100, cy - 420, "善", 90, -4, C.slam_scale(T - tg))
        return None
    ev(j, k_wall, scene, "muyu", 0.6)
    b.hit(j, k_open, "wood_high", 0.75, "门打开")
    b.hit(j, k_up, "shaker", 0.75, "实情传上来")
    b.hit(j, k_good, "kick", 0.85, "太宗说好")


screen6()


# ================================================================ 屏 7：一间屋子多开几扇窗，光照进来
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_room = kq(j, wp(10, 0, 0.6), 0)
    k_wins = nx(j, wp(10, 1, 0.5), k_room)
    L.note("兼听")

    def scene(c, kk, T):
        tr, tw = tb(j, k_room), tb(j, k_wins)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 60, 0, g):
            box(c, 0, 0, 840, 680, "#3A4466", BLACK, 8, 10)
            for i, (x, y) in enumerate(((-240, -150), (240, -150), (-240, 150), (240, 150))):
                op = T >= tw + i * 0.15
                c.drawRect(skia.Rect.MakeXYWH(x - 110, y - 90, 220, 180), K.paint(YELLOW if op else "#24293B"))
                c.drawRect(skia.Rect.MakeXYWH(x - 110, y - 90, 220, 180), wb.marker(BLACK, 6))
                if op:
                    beam = P((x - 100, y + 90), (x + 100, y + 90), (x * 0.2 + 60, 330), (x * 0.2 - 60, 330), close=True)
                    c.drawPath(beam, K.paint(YELLOW, 0.25))
            K.text(c, "兼听", 0, 0, 90, "serif_black", "#FFFFFF" if T < tw else INK)
        return None
    ev(j, k_room, scene, "wood_low", 0.6)
    b.hit(j, k_wins, "ding", 0.85, "多开几扇窗")


screen7()


# ================================================================ 屏 8：左：小李听完一面之词就站队；右：小王问了两个人、翻聊天记录，发现是误会
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_left = kq(j, wp(11, 2, 0.4), 0)
    k_side = nx(j, wp(11, 3, 0.4), k_left)
    k_ask = nx(j, wp(12, 0, 0.5), k_side)
    k_chat = nx(j, wp(12, 1, 0.5), k_ask)
    k_oops = nx(j, wp(12, 2, 0.5), k_chat)
    L.note("小李", "小王", "站队", "误会")

    def scene(c, kk, T):
        tl, ts, ta, tc, to = tb(j, k_left), tb(j, k_side), tb(j, k_ask), tb(j, k_chat), tb(j, k_oops)
        C.line(c, (cx, cy - 480), (cx, GY + 20), GRAY, 4)
        g = pop_scale(T - tl)
        if g > 0:
            LX = cx - 300
            with at_pop(c, LX, GY, g):
                draw_ace(c, LX - 150, GY, 0.7, mood="smug")
                draw_li(c, LX + 60, GY, 0.75, "flat", rh=(LX + 160, GY - 280) if T >= ts else None)
            name_tag(c, LX + 60, cy - 30, "小李", "#4A5160", 34)
            if T >= ts:
                with K.at(c, LX + 40, cy - 280, -6, C.slam_scale(T - ts)):
                    chip(c, 0, 0, "站队", RED_FILL, RED, 54)
        if T >= ta:
            RX = cx + 300
            with at_pop(c, RX, GY, pop_scale(T - ta)):
                draw_wang(c, RX, GY, 0.75, mood="smile" if T >= to else "flat")
                for i, x in enumerate((RX - 180, RX + 170)):
                    draw_ace(c, x, GY, 0.55, mood="flat") if i == 0 else draw_li(c, x, GY, 0.55, "flat")
            name_tag(c, RX, cy - 30, "小王", "#2F5B8E", 34)
            if T >= tc:
                with K.at(c, RX, cy - 300, 0, pop_scale(T - tc)):
                    phone(c, 0, 0, 0.9)
            if T >= to:
                with K.at(c, RX, cy - 120, 4, C.slam_scale(T - to)):
                    chip(c, 0, 0, "误会", GREEN_FILL, GREEN, 54)
        return None
    ev(j, k_left, scene, "wood_low", 0.6)
    b.hit(j, k_side, "rim", 0.8, "当场站队")
    b.hit(j, k_ask, "pop", 0.7, "多问两个人")
    b.hit(j, k_chat, "pop", 0.7, "看聊天记录")
    b.hit(j, k_oops, "ding", 0.85, "原来是误会")


screen8()


# ================================================================ 屏 9：小李忙得只顾听身边人；“三步”
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_busy = kq(j, wp(13, 1, 0.4), 1)
    k_trust = nx(j, wp(13, 2, 0.5), k_busy)
    k_3 = nx(j, wp(14, 1, 0.5), k_trust)
    LX = cx - 260
    L.note("忙", "信得过", "三步")

    def scene(c, sc, T):
        tbz, tt = tb(j, k_busy), tb(j, k_trust)
        with at_pop(c, LX, GY, sc):
            desk(c, LX + 180, GY - 170, 380)
            draw_li(c, LX, GY, 0.95, "flat", rh=(LX + 120, GY - 230))
        if T >= tbz:
            with K.at(c, LX + 200, cy - 280, 0, pop_scale(T - tbz)):
                chip(c, 0, 0, "忙", NOTE_FILL, ORANGE, 56)
        if T >= tt:
            with at_pop(c, LX - 180, GY, pop_scale(T - tt)):
                draw_ace(c, LX - 180, GY, 0.8, mood="smile")
            with K.at(c, LX - 180, cy - 120, 0, pop_scale(T - tt)):
                chip(c, 0, 0, "信得过", GREEN_FILL, GREEN, 44)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_busy, "pop", 0.7, "因为忙")
    b.hit(j, k_trust, "pop", 0.7, "信得过")
    L.stamp_ev(j, k_3, "三步", cx + 280, cy + 180, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen9()


# ================================================================ 屏 10：第一步：三方——当事人、旁边的人、意见不同的人，三条线连到小李
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_li = kq(j, wp(15, 0, 0.6), 1)
    k_a = nx(j, wp(15, 1, 0.3), k_li)
    k_b = nx(j, wp(15, 1, 0.8), k_a)
    k_c = nx(j, wp(15, 2, 0.5), k_b)
    WHO = ["当事人", "旁边的人", "意见不同的人"]
    L.note(*WHO)

    def scene(c, kk, T):
        tl = tb(j, k_li)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        LX, LY = cx, cy + 300
        pos = [(cx - 380, cy - 230), (cx, cy - 330), (cx + 380, cy - 230)]
        for i, (t0, (x, y), s_) in enumerate(zip((tb(j, k_a), tb(j, k_b), tb(j, k_c)), pos, WHO)):
            if T < t0:
                continue
            f = ease_out(clamp01((T - t0) / 0.4))
            C.line(c, (LX, LY - 260), (lerp(LX, x, f), lerp(LY - 260, y + 60, f)), GREEN, 6)
            with K.at(c, x, y, 0, pop_scale(T - t0)):
                c.drawCircle(0, -40, 60, K.paint("#FFFFFF"))
                c.drawCircle(0, -40, 60, wb.marker((BLUE, ORANGE, RED)[i], 6))
                K.text(c, s_, 0, 70, 40 if len(s_) < 5 else 34, "hand", INK)
        with at_pop(c, LX, LY + 200, g):
            draw_li(c, LX, LY + 200, 0.8, "smile")
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    for k_ in (k_a, k_b, k_c):
        b.hit(j, k_, "pop", 0.75, "问一方")


screen10()


# ================================================================ 屏 11：第二步：“大家都说”被追问“谁说的？”，变成具体一两个名字
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_all = kq(j, wp(16, 0, 0.6), 1)
    k_who = nx(j, wp(16, 2, 0.4), k_all)
    k_names = nx(j, wp(16, 2, 0.95), k_who)
    L.note("大家都说", "谁说的？", "就老周")

    def scene(c, kk, T):
        ta, tw, tn = tb(j, k_all), tb(j, k_who), tb(j, k_names)
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        shrink = ease_out(clamp01((T - tn) / 0.4)) if T >= tn else 0
        with K.at(c, cx + 100, cy - 260, 0, g * lerp(1, 0.6, shrink)):
            bubble_box(c, 0, 0, 420, 140, 1, 1 - 0.5 * shrink)
            K.text(c, "大家都说", 0, 0, 62, "hand", INK, 1 - 0.5 * shrink)
        with at_pop(c, cx - 330, GY, g):
            draw_li(c, cx - 330, GY, 0.95, "flat", rh=(cx - 190, GY - 330) if T >= tw else None)
        if T >= tw:
            with K.at(c, cx - 230, cy - 20, 0, C.slam_scale(T - tw)):
                bubble_box(c, 0, 0, 300, 120, -1)
                K.text(c, "谁说的？", 0, 0, 58, "hand", RED)
        if T >= tn:
            with K.at(c, cx + 250, cy + 10, 0, pop_scale(T - tn)):
                chip(c, 0, 0, "就老周", NOTE_FILL, ORANGE, 52)
        return None
    ev(j, k_all, scene, "wood_high", 0.65)
    b.hit(j, k_who, "rim", 0.8, "追问谁说的")
    b.hit(j, k_names, "pop", 0.75, "具体一两个人")


screen11()


# ================================================================ 屏 12：第三步：日历上留出一天，第二天才落笔
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_cal = kq(j, wp(17, 0, 0.6), 1)
    k_wait = nx(j, wp(17, 1, 0.5), k_cal)
    k_pen = nx(j, wp(17, 2, 0.5), k_wait)
    L.note("今天", "明天", "判断")

    def scene(c, kk, T):
        tc, tw, tp = tb(j, k_cal), tb(j, k_wait), tb(j, k_pen)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 180, 0, g):
            for i, d in enumerate(("今天", "明天")):
                x = -200 + i * 400
                box(c, x, 0, 260, 220, "#FFFFFF", BLACK, 6, 12)
                c.drawRect(skia.Rect.MakeXYWH(x - 130, -110, 260, 60), K.paint(BLUE_FILL))
                K.text(c, d, x, -80, 46, "hand", INK)
            if T >= tw:
                c.drawPath(wb.arrow((-60, 40), (60, 40), -0.3, 26), wb.marker(ORANGE, 8, clamp01((T - tw) / 0.3)))
                K.text(c, "等一天", 0, 120, 40, "hand", ORANGE, clamp01((T - tw) / 0.3))
            if T >= tp:
                with K.at(c, 200, 40, -20, pop_scale(T - tp)):
                    C.line(c, (0, -60), (0, 60), INK, 12)
                    c.drawPath(P((-8, 60), (8, 60), (0, 90), close=True), K.paint(INK))
                K.text(c, "判断", 200, 160, 44, "hand", GREEN, clamp01((T - tp) / 0.2))
        with at_pop(c, cx - 380, GY, g):
            draw_li(c, cx - 380, GY, 0.9, "flat")
        return None
    L.note("等一天")
    ev(j, k_cal, scene, "wood_high", 0.65)
    b.hit(j, k_wait, "pop", 0.7, "留一天")
    b.hit(j, k_pen, "ding", 0.8, "再下判断")


screen12()


# ================================================================ 屏 13：好处：小李不再被人拿来当枪使
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_gun = kq(j, wp(18, 0, 0.6), 0)
    k_drop = nx(j, wp(18, 1, 0.5), k_gun)
    L.note("枪")

    def scene(c, kk, T):
        tg, td = tb(j, k_gun), tb(j, k_drop)
        g = pop_scale(T - tg)
        if g <= 0:
            return None
        LX, AX = cx - 60, cx - 320
        f = ease_in_out(clamp01((T - td) / 0.5)) if T >= td else 0
        with at_pop(c, AX, GY, g):
            draw_ace(c, AX, GY, 0.85, mood="smug" if f < 0.5 else "o", rh=(lerp(LX - 40, AX + 100, f), GY - 280))
        with at_pop(c, LX, GY, g):
            draw_li(c, LX + 120 * f, GY, 0.85, "o" if f < 0.5 else "smile")
        with K.at(c, lerp(LX + 140, LX + 380, f), lerp(GY - 300, GY - 30, f), 70 * f):
            box(c, 0, 0, 160, 40, GRAY, INK, 4, 6)
            box(c, -50, 30, 40, 60, GRAY, INK, 4, 6)
        if T >= td:
            sparkle(c, LX + 120, GY - 300, T - td, YELLOW, 10, 50, 120)
        return None
    ev(j, k_gun, scene, "wood_low", 0.6)
    b.hit(j, k_drop, "kick", 0.85, "不再被当枪使")


screen13()


# ================================================================ 屏 14：评论区；小李多问一句，心里亮起一盏灯；下一讲预告
def _enc(c, T, te, th, cx, cy):
    LX, LY = cx - 200, cy + 640
    with at_pop(c, LX, LY, pop_scale(T - te)):
        draw_li(c, LX, LY, 0.95, "smile" if T >= th else "flat")
    if T >= th:
        hy = LY - 290 * 0.95
        c.drawPath(C.bulb_path(LX + 220, hy - 60, 60), K.paint(YELLOW, 0.8))
        c.drawPath(C.bulb_path(LX + 220, hy - 60, 60), wb.marker(ORANGE, 6))
        sparkle(c, LX + 220, hy - 60, T - th, YELLOW, 10, 70, 150)
        K.text(c, "亮堂", LX + 420, hy, 64, "hand", GREEN, clamp01((T - th) / 0.2))


L.note("亮堂")


def _icon(c, x, y, t):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 60, y - 90, 120, 180), 60, 60, K.paint("#E8EEF8"))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 60, y - 90, 120, 180), 60, 60, wb.marker(GRAY, 5))
    c.drawCircle(x, y - 20 + 8 * math.sin(t * 6), 22, wb.marker(INK, 4))


KT.ending(14, "你听错过一面之词吗？", ["同事吐槽", "领导传话", "家里亲戚"], 20, 21, _enc, 22,
          ["谁来告诉你", "你哪里错了？"], enc_piece=0, next_icon=_icon)

# ================================================================ 收尾
L.finish(cover_shot=5, square_shot=4, notes=NOTES)
L.export(globals())
