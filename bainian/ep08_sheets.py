"""《百年孤独》08 床单：太在意别人怎么看，怎么办？（白板手绘 + AI 旁白，竖屏 2:3）

误区对照：今天的我们出门换三套衣服、开会先想十遍别人怎么看；书里的俏姑娘雷梅黛丝一点不在乎——嫌梳头麻烦剃了头发，
嫌衣服麻烦套一件粗麻布长袍，男人为她着迷她也不放在心上，最后抓着床单升上了天，费尔南达只心疼床单。
她活得太不食人间烟火，学她一半就够。文案见 bainian/PLAN.md「### 08」。
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
                            YELLOW, at_pop, box, bubble_box, chip, draw_lady, draw_li, draw_man, draw_wang, flower_rain,
                            name_tag, pop_scale, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "生活里", 1),
    ([2], "生活里", 2),
    ([3, 4], "书里的人", 3),
    ([5, 6], "怎么舒服怎么来", 4),
    ([7, 8], "不在乎", 5),
    ([9, 10], "床单", 6),
    ([11], "床单", 7),
    ([12], "学一半", 8),
    ([13], "说回我们", 9),
    ([14], "第一步", 10),
    ([15], "第二步", 11),
    ([16], "第三步", 12),
    ([17], "好处", 13),
    ([18, 19, 20, 21], "评论区见", 14),
]

THEME = BT.get("08")
L = N.Lesson("08", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(13)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》第 9–12 章（范晔译本）俏姑娘雷梅黛丝。情节为转述，不引原文。",
    "今人（小李、小王）为虚构示意；书中人造型为示意（一百多年前的加勒比小镇打扮）。",
]

REM = ("俏姑娘雷梅黛丝", "马孔多最美的人")
FER = ("费尔南达", "")


def remedios(c, x, y, s, shaved=True, **kw):
    """俏姑娘雷梅黛丝：剃光的头、粗麻布长袍（灰白）；shaved=False 时是长发、白裙。"""
    if shaved:
        draw_lady(c, x, y, s, "gray", hair="none", **kw)
    else:
        draw_lady(c, x, y, s, "white", hair="long", **kw)


def eye(c, x, y, s=1.0, a=1.0, closed=0.0):
    with K.at(c, x, y, 0, s):
        h = 26 * (1 - closed)
        c.drawOval(skia.Rect.MakeXYWH(-50, -max(2, h), 100, 2 * max(2, h)), K.paint("#FFFFFF", a))
        c.drawOval(skia.Rect.MakeXYWH(-50, -max(2, h), 100, 2 * max(2, h)), wb.marker(BLACK, 5, a))
        if closed < 0.7:
            c.drawCircle(0, 0, 16 * (1 - closed), K.paint(BLACK, a))


def shirt(c, x, y, col, s=1.0, rot=0.0, a=1.0):
    with K.at(c, x, y, rot, s):
        p = skia.Path()
        p.addPoly([skia.Point(*q) for q in ((-60, -60), (-25, -70), (25, -70), (60, -60), (80, 0), (45, 10), (45, 70), (-45, 70),
                                            (-45, 10), (-80, 0))], True)
        c.drawPath(p, K.paint(col, a))
        c.drawPath(p, wb.marker(BLACK, 5, a))


def sheet(c, x, y, w, h, wave, a=1.0):
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.lineTo(x + w / 2, y)
    n = 16
    for i in range(n + 1):
        u = 1 - i / n
        p.lineTo(x - w / 2 + w * u, y + h + 18 * math.sin(u * 9 + wave))
    p.close()
    c.drawPath(p, K.paint("#FFFFFF", a))
    c.drawPath(p, wb.marker(GRAY, 5, a))


def scale_beam(c, x, y, tilt, left, right, a=1.0):
    """天平：tilt>0 左边下沉。"""
    C.line(c, (x, y + 220), (x, y), INK, 10, a)
    c.drawPath(P((x - 60, y + 220), (x + 60, y + 220), (x, y + 190), close=True), K.paint(INK, a))
    ang = math.radians(-12 * tilt)
    dx, dy = 300 * math.cos(ang), 300 * math.sin(ang)
    C.line(c, (x - dx, y - dy), (x + dx, y + dy), INK, 10, a)
    for sg, lab in ((-1, left), (1, right)):
        px, py = x + sg * dx, y + sg * dy
        C.line(c, (px, py), (px, py + 90), INK, 4, a)
        c.drawOval(skia.Rect.MakeXYWH(px - 110, py + 80, 220, 40), K.paint("#E7D6BA", a))
        c.drawOval(skia.Rect.MakeXYWH(px - 110, py + 80, 220, 40), wb.marker(INK, 5, a))
        K.text(c, lab, px, py + 160, 44, "hand", INK, a)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：床上堆着三套衣服；会议桌边小李举手又放下，四周一圈眼睛
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_clothes = kq(j, wp(0, 1, 0.4), 0)
    k_ugly = nx(j, wp(0, 2, 0.4), k_clothes)
    k_meet = nx(j, wp(1, 0, 0.5), k_ugly)
    k_eyes = nx(j, wp(1, 2, 0.3), k_meet)
    L.note("不好看？")

    def scene(c, kk, T):
        tc, tu, tm, te = (tb(j, k) for k in (k_clothes, k_ugly, k_meet, k_eyes))
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        if T < tm:
            box(c, cx + 120, GY - 120, 600, 100, "#FFFFFF", INK, 6, 12, g)
            for i, col in enumerate((RED, BLUE, ORANGE)):
                if T >= tc + i * 0.15:
                    shirt(c, cx - 60 + i * 160, GY - 230, col, 1.0, (i - 1) * 15)
            draw_li(c, cx - 380, GY, 0.95, "sad" if T >= tu else "flat")
            if T >= tu:
                with K.at(c, cx - 200, cy - 220, 0, pop_scale(T - tu)):
                    bubble_box(c, 0, 0, 280, 110, -1)
                    K.text(c, "不好看？", 0, 0, 50, "hand", RED)
            return None
        f = pop_scale(T - tm)
        hy = GY - 290
        up = T >= tm and T < te
        with at_pop(c, cx, GY, f):
            draw_li(c, cx, GY, 1.0, "o" if T >= te else "flat", rh=(cx + 60, hy - 120) if up else None)
        if T >= te:
            for q in range(7):
                a = math.pi + q / 6 * math.pi
                eye(c, cx + 430 * math.cos(a), cy - 40 + 260 * math.sin(a), pop_scale(T - te - q * 0.06))
        return None
    ev(j, k_clothes, scene, "pop", 0.65)
    b.hit(j, k_ugly, "rim", 0.7, "怕别人说不好看")
    b.hit(j, k_meet, "wood_low", 0.6, "开会想发言")
    b.hit(j, k_eyes, "shaker", 0.75, "四周的眼睛")


screen1()


# ================================================================ 屏 2（drop）：天平一边“别人的眼光”一边“自己的想法”，眼光那边重重压下
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    dk = L.drop_k()
    k_beam = kq(j, wp(2, 0, 0.3), 0)
    L.note("别人的眼光", "自己的想法", "重")

    def scene(c, kk, T):
        tb_, td = tb(j, k_beam), tb(j, dk)
        g = pop_scale(T - tb_)
        if g <= 0:
            return None
        tilt = ease_out(clamp01((T - td) / 0.3)) if T >= td else 0.15 * math.sin((T - tb_) * 4)
        scale_beam(c, cx, cy - 160, tilt, "别人的眼光", "自己的想法", g)
        if T >= td:
            with K.at(c, cx - 300, cy - 330, 0, C.slam_scale(T - td)):
                K.text(c, "重", 0, 0, 120, "hand", RED)
        return None
    ev(j, k_beam, scene, "wood_low", 0.65)
    b.hit(j, dk, "kick", 0.9, "眼光比想法还重")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：绿皮书翻开；俏姑娘雷梅黛丝出场，周围一圈小星星
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(3, 0, 0.4), 0)
    k_girl = nx(j, wp(3, 2, 0.4), k_book)
    k_name = nx(j, wp(4, 0, 0.6), k_girl)
    k_star = nx(j, wp(4, 1, 0.4), k_name)
    KT.book(j, k_book, x=cx - 360, y=cy - 300)
    L.note(*REM, "不在乎")
    RX = cx + 200

    def scene(c, kk, T):
        tg, tn, ts = tb(j, k_girl), tb(j, k_name), tb(j, k_star)
        g = pop_scale(T - tg)
        if g <= 0:
            return None
        with at_pop(c, RX, GY, g):
            remedios(c, RX, GY, 1.05, shaved=False, mood="smile")
        K.text(c, "不在乎", RX - 300, cy + 40, 56, "hand", BLUE, clamp01(g))
        if T >= tn:
            name_tag(c, RX, GY - 480, REM[0], "#6A3D8C", 44, clamp01((T - tn) / 0.3), REM[1])
        if T >= ts:
            for q in range(8):
                a = q / 8 * 2 * math.pi + (T - ts) * 0.6
                sparkle(c, RX + 220 * math.cos(a), GY - 230 + 260 * math.sin(a), (T - ts) % 0.9, YELLOW, 6, 6, 26)
        return None
    ev(j, k_girl, scene, "ding", 0.7)
    b.hit(j, k_name, "pop", 0.7, "俏姑娘雷梅黛丝")
    b.hit(j, k_star, "shaker", 0.7, "最美的人")


screen3()


# ================================================================ 屏 4：头发剃掉；一件粗麻布长袍套上，她伸懒腰
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_comb = kq(j, wp(5, 0, 0.5), 0)
    k_shave = nx(j, wp(5, 1, 0.5), k_comb)
    k_robe = nx(j, wp(6, 1, 0.5), k_shave)
    k_comfy = nx(j, wp(6, 2, 0.4), k_robe)
    L.note("梳头麻烦", "粗麻布长袍", "舒服")
    RX = cx - 60

    def scene(c, kk, T):
        tc, tsh, tr, tf = (tb(j, k) for k in (k_comb, k_shave, k_robe, k_comfy))
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        shaved = T >= tsh
        robe = T >= tr
        hy = GY - 290 * 1.05
        arms = dict(lh=(RX - 150, hy - 90), rh=(RX + 150, hy - 90)) if T >= tf else {}
        with at_pop(c, RX, GY, g):
            if robe:
                remedios(c, RX, GY, 1.05, shaved=True, mood="smile", **arms)
            else:
                draw_lady(c, RX, GY, 1.05, "white", hair="none" if shaved else "long", mood="flat" if not shaved else "smile")
        if T < tsh:
            with K.at(c, RX + 220, hy - 40, 20 * math.sin((T - tc) * 8), 1):
                box(c, 0, 0, 160, 40, "#E7D6BA", "#8B6B43", 5, 6)
                for q in range(6):
                    C.line(c, (-60 + q * 24, 20), (-60 + q * 24, 60), "#8B6B43", 4)
            K.text(c, "梳头麻烦", RX + 300, cy - 300, 50, "hand", GRAY, 1)
        else:
            for q in range(5):
                f = clamp01((T - tsh - q * 0.05) / 0.8)
                c.drawPath(P((RX - 30 + q * 15, hy - 50 + 400 * f * f), (RX - 10 + q * 15, hy - 20 + 400 * f * f)),
                           wb.marker(N.HAIR, 6, 1 - f))
        if robe:
            K.text(c, "粗麻布长袍", RX + 330, cy + 20, 50, "hand", INK, clamp01((T - tr) / 0.3))
        if T >= tf:
            with K.at(c, RX + 320, cy - 330, 4, C.slam_scale(T - tf)):
                chip(c, 0, 0, "舒服", GREEN_FILL, GREEN, 62)
        return None
    ev(j, k_comb, scene, "wood_low", 0.6)
    b.hit(j, k_shave, "shaker", 0.75, "头发剃了")
    b.hit(j, k_robe, "pop", 0.75, "套上长袍")
    b.hit(j, k_comfy, "ding", 0.8, "怎么舒服怎么来")


screen4()


# ================================================================ 屏 5：家里人捧着裙子首饰追着她；一排男人捧着花，她走过去没看一眼
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_fam = kq(j, wp(7, 0, 0.5), 0)
    k_dress = nx(j, wp(7, 1, 0.5), k_fam)
    k_ignore = nx(j, wp(7, 2, 0.3), k_dress)
    k_men = nx(j, wp(8, 0, 0.5), k_ignore)
    k_pass = nx(j, wp(8, 1, 0.4), k_men)
    L.note("体面", "不理")

    def scene(c, kk, T):
        tf, td, ti, tm, tp = (tb(j, k) for k in (k_fam, k_dress, k_ignore, k_men, k_pass))
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        if T < tm:
            RX = cx + 240
            remedios(c, RX, GY, 0.95, mood="smile")
            for i, x in enumerate((cx - 420, cx - 180)):
                with at_pop(c, x, GY, g):
                    draw_lady(c, x, GY, 0.85, ("blue", "black")[i], hair="bun", mood="o", rh=(x + 140, GY - 240))
                if T >= td:
                    shirt(c, x + 150, GY - 260, (RED, YELLOW)[i], 0.8)
            if T >= td:
                K.text(c, "体面", cx - 300, cy - 260, 56, "hand", ORANGE, clamp01((T - td) / 0.3))
            if T >= ti:
                with K.at(c, RX + 40, cy - 300, 0, C.slam_scale(T - ti)):
                    chip(c, 0, 0, "不理", "#D9DCE1", GRAY, 56)
            return None
        u = ease_in_out(clamp01((T - tp) / 1.6)) if T >= tp else 0
        for i in range(4):
            x = cx - 420 + i * 200
            with at_pop(c, x, GY, pop_scale(T - tm - i * 0.08)):
                draw_man(c, x, GY, 0.75, ("white", "ochre", "green", "blue")[i], hat="straw" if i % 2 else None,
                         mood="smile", rh=(x + 90, GY - 230))
                for q in range(3):
                    c.drawCircle(x + 90 + (q - 1) * 20, GY - 260 - (q % 2) * 14, 14, K.paint((RED, YELLOW, RED)[q]))
        RX = lerp(cx - 500, cx + 480, u)
        remedios(c, RX, GY + 40, 0.9, mood="flat", head_dx=0)
        return None
    ev(j, k_fam, scene, "wood_high", 0.6)
    b.hit(j, k_dress, "pop", 0.7, "想打扮她")
    b.hit(j, k_ignore, "rim", 0.75, "一点不理")
    b.hit(j, k_men, "clap", 0.7, "好多男人着迷")
    b.hit(j, k_pass, "shaker", 0.7, "没放在心上")


screen5()


# ================================================================ 屏 6：院子里晾着白床单，起风；她抓着床单升上天，黄花飘落
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_yard = kq(j, wp(9, 1, 0.4), 0)
    k_fold = nx(j, wp(9, 2, 0.4), k_yard)
    k_wind = nx(j, wp(10, 0, 0.5), k_fold)
    k_up = nx(j, wp(10, 2, 0.3), k_wind)
    L.note("风")

    def scene(c, kk, T):
        ty, tf, tw, tu = (tb(j, k) for k in (k_yard, k_fold, k_wind, k_up))
        g = pop_scale(T - ty)
        if g <= 0:
            return None
        C.line(c, (cx - 520, cy - 260), (cx + 520, cy - 260), INK, 4, g)
        wave = (T - tw) * 6 if T >= tw else 0
        for i in range(3):
            if i == 1 and T >= tu:
                continue
            sheet(c, cx - 340 + i * 340, cy - 260, 260, 320, wave + i, g)
        up = ease_in_out(clamp01((T - tu) / 2.0)) if T >= tu else 0
        RX, RY = cx, lerp(GY, cy - 120, up)
        if T >= tf:
            hy = RY - 290 * 0.95
            remedios(c, RX, RY, 0.95, mood="smile", lh=(RX - 120, hy - 60) if up > 0 else None,
                     rh=(RX + 120, hy - 60) if up > 0 else None)
            if up > 0:
                sheet(c, RX, hy - 260 * (1 - 0.3 * up), 300, 260, wave)
        if T >= tw:
            for q in range(4):
                y = cy - 420 + q * 100
                ph = ((T - tw) * 1.5 + q * 0.3) % 1
                c.drawPath(P((cx - 560 + 900 * ph, y), (cx - 420 + 900 * ph, y - 20)), wb.marker(BLUE, 5, 0.6))
            K.text(c, "风", cx - 420, cy - 480, 60, "hand", BLUE, clamp01((T - tw) / 0.3))
        if T >= tu:
            flower_rain(c, cx - 560, cx + 560, cy - 600, GY, T, tu, 40)
        return None
    ev(j, k_yard, scene, "wood_low", 0.6)
    b.hit(j, k_fold, "pop", 0.65, "叠床单")
    b.hit(j, k_wind, "shaker", 0.8, "一阵风")
    b.hit(j, k_up, "ding", 0.9, "升上了天")


screen6()


# ================================================================ 屏 7：费尔南达在下面伸手够床单
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_fer = kq(j, wp(11, 0, 0.5), 0)
    k_sheet = nx(j, wp(11, 1, 0.5), k_fer)
    L.note("费尔南达", "我的床单！")

    def scene(c, kk, T):
        tf, ts = tb(j, k_fer), tb(j, k_sheet)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        FX = cx - 120
        hy = GY - 290
        with at_pop(c, FX, GY, g):
            draw_lady(c, FX, GY, 1.0, "black", hair="bun", mood="o", rh=(FX + 120, hy - 140))
        name_tag(c, FX - 260, GY - 300, "费尔南达", "#3A3A3A", 40, clamp01(g))
        sheet(c, cx + 250, cy - 420 - 60 * (T - tf), 200, 160, (T - tf) * 5)
        if T >= ts:
            with K.at(c, cx + 200, cy - 100, 0, C.slam_scale(T - ts)):
                bubble_box(c, 0, 0, 360, 110, -1)
                K.text(c, "我的床单！", 0, 0, 50, "hand", RED)
        return None
    ev(j, k_fer, scene, "wood_low", 0.6)
    b.hit(j, k_sheet, "rim", 0.8, "只心疼床单")


screen7()


# ================================================================ 屏 8：天平：左边“全不在乎”，右边“太在乎”，中间亮起“一半”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_beam = kq(j, wp(12, 1, 0.3), 0)
    k_half = nx(j, wp(12, 2, 0.5), k_beam)
    L.note("全不在乎", "太在乎", "一半")

    def scene(c, kk, T):
        tbm, th = tb(j, k_beam), tb(j, k_half)
        g = pop_scale(T - tbm)
        if g <= 0:
            return None
        tilt = 0.8 * math.sin((T - tbm) * 3) * (1 - ease_out(clamp01((T - th) / 0.6))) if T >= tbm else 0
        scale_beam(c, cx, cy - 160, tilt, "全不在乎", "太在乎", g)
        if T >= th:
            with K.at(c, cx, cy - 330, 0, C.slam_scale(T - th)):
                chip(c, 0, 0, "一半", GREEN_FILL, GREEN, 70)
            sparkle(c, cx, cy - 330, T - th, YELLOW, 10, 80, 200)
        return None
    ev(j, k_beam, scene, "wood_low", 0.6)
    b.hit(j, k_half, "ding", 0.85, "学她一半")


screen8()


# ================================================================ 屏 9：小李身边的眼睛一只只闭上；大字“三步”
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_eyes = kq(j, wp(13, 0, 0.4), 0)
    k_close = nx(j, wp(13, 1, 0.4), k_eyes)
    L.note("三步")

    def scene(c, kk, T):
        te, tc = tb(j, k_eyes), tb(j, k_close)
        g = pop_scale(T - te)
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            draw_li(c, cx, GY, 1.0, "smile" if T >= tc else "flat")
        for q in range(7):
            a = math.pi + q / 6 * math.pi
            cl = ease_out(clamp01((T - tc - q * 0.06) / 0.25)) if T >= tc else 0
            eye(c, cx + 430 * math.cos(a), cy + 40 + 260 * math.sin(a), g, 1, cl)
        if T >= tc:
            with K.at(c, cx, cy - 380, -3, C.slam_scale(T - tc)):
                K.text(c, "三步", 0, 0, 140, "hand", RED)
        return None
    ev(j, k_eyes, scene, "wood_low", 0.6)
    b.hit(j, k_close, "kick", 0.85, "三步")


screen9()


# ================================================================ 屏 10：第一步：日历翻过一个月，别人的气泡淡掉
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    k_cal = kq(j, wp(14, 1, 0.4), 1)
    k_fade = nx(j, wp(14, 2, 0.5), k_cal)
    L.note("一个月后", "她穿得好怪", "？")

    def scene(c, kk, T):
        tc, tf = tb(j, k_cal), tb(j, k_fade)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx - 230, cy - 60, 0, g):
            box(c, 0, 0, 360, 380, "#FFFFFF", BLACK, 7, 12)
            c.drawRect(skia.Rect.MakeXYWH(-180, -190, 360, 90), K.paint(RED_FILL))
            pages = min(30, int((T - tc) / 0.04))
            K.text(c, str(1 + pages), 0, 40, 130, "hand", INK)
        K.text(c, "一个月后", cx - 230, cy + 220, 50, "hand", INK, g)
        fade = ease_out(clamp01((T - tf) / 0.8)) if T >= tf else 0
        with K.at(c, cx + 250, cy - 120, 0, g):
            bubble_box(c, 0, 0, 340, 120, -1, 1 - 0.8 * fade)
            K.text(c, "她穿得好怪", 0, 0, 46, "hand", GRAY, 1 - 0.8 * fade)
        if T >= tf:
            K.text(c, "？", cx + 250, cy + 100, 120, "hand", BLUE, fade)
        return None
    ev(j, k_cal, scene, "wood_high", 0.65)
    b.hit(j, k_fade, "shaker", 0.75, "没人记得")


screen10()


# ================================================================ 屏 11：第二步：小李穿着舒服的卫衣，喝一杯热茶
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_tea = kq(j, wp(15, 1, 0.4), 1)
    k_nope = nx(j, wp(15, 2, 0.4), k_tea)
    L.note("舒服", "不解释")

    def scene(c, kk, T):
        tt, tn = tb(j, k_tea), tb(j, k_nope)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        LX = cx - 150
        hy = GY - 290
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "smile", rh=(LX + 120, hy + 120))
            c.drawRoundRect(skia.Rect.MakeXYWH(LX - 50, hy + 60, 100, 150), 20, 20, K.paint("#F6C3BE", 0.8))
        box(c, LX + 150, hy + 110, 70, 80, "#FFFFFF", INK, 5, 8)
        for q in range(3):
            f = ((T - tt) * 0.8 + q / 3) % 1
            c.drawCircle(LX + 130 + q * 20, hy + 40 - 100 * f, 10 + 6 * f, K.paint(GRAY, 0.5 * (1 - f)))
        K.text(c, "舒服", cx + 280, cy - 200, 70, "hand", GREEN, clamp01(g))
        if T >= tn:
            with K.at(c, cx + 280, cy + 40, 0, C.slam_scale(T - tn)):
                chip(c, 0, 0, "不解释", NOTE_FILL, ORANGE, 56)
        return None
    ev(j, k_tea, scene, "ding", 0.7)
    b.hit(j, k_nope, "pop", 0.75, "不解释")


screen11()


# ================================================================ 屏 12：第三步：三张小脸亮着，其他人的气泡变灰
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    k_three = kq(j, wp(16, 1, 0.5), 1)
    k_gray = nx(j, wp(16, 2, 0.5), k_three)
    L.note("真心对你好的人")

    def scene(c, kk, T):
        tt, tg = tb(j, k_three), tb(j, k_gray)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        gr = ease_out(clamp01((T - tg) / 0.4)) if T >= tg else 0
        for q in range(8):
            a = q / 8 * 2 * math.pi
            x, y = cx + 440 * math.cos(a), cy - 40 + 380 * math.sin(a)
            bubble_box(c, x, y, 140, 80, -1, 1 - 0.75 * gr, "#FFFFFF")
        for i in range(3):
            x = cx - 220 + i * 220
            with K.at(c, x, cy - 40, 0, g * (1 + 0.1 * gr)):
                c.drawCircle(0, 0, 80, K.paint(NOTE_FILL))
                c.drawCircle(0, 0, 80, wb.marker(ORANGE, 6))
                for sg in (-1, 1):
                    c.drawCircle(sg * 24, -10, 7, K.paint(INK))
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(-26, 4, 52, 34), 20, 140)
                c.drawPath(arc, wb.marker(INK, 5))
        if T >= tg:
            K.text(c, "真心对你好的人", cx, cy + 180, 52, "hand", RED, gr)
        return None
    ev(j, k_three, scene, "pop", 0.7)
    b.hit(j, k_gray, "ding", 0.8, "只听他们的")


screen12()


# ================================================================ 屏 13：好处：小李开口，声音波纹一圈圈出去
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_light = kq(j, wp(17, 1, 0.5), 0)
    k_voice = nx(j, wp(17, 2, 0.5), k_light)
    L.note("我的声音")

    def scene(c, kk, T):
        tl, tv = tb(j, k_light), tb(j, k_voice)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        LX = cx - 250
        hy = GY - 290
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "smile")
        if T >= tv:
            for q in range(4):
                r = 60 + q * 70 + ((T - tv) * 120) % 70
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(LX + 40 - r, hy + 10 - r, 2 * r, 2 * r), -40, 80)
                c.drawPath(arc, wb.marker(BLUE, 7, clamp01(1 - q * 0.2)))
            with K.at(c, cx + 230, cy - 200, 0, C.slam_scale(T - tv)):
                chip(c, 0, 0, "我的声音", GREEN_FILL, GREEN, 60)
        return None
    ev(j, k_light, scene, "wood_low", 0.6)
    b.hit(j, k_voice, "ding", 0.85, "你自己的声音")


screen13()


# ================================================================ 屏 14：评论区；小李放风筝，线在手里；下一讲预告：一场大雨
def enc(c, T, te, th, cx, cy):
    LX, LY = cx - 280, cy + 640
    g = pop_scale(T - te)
    with at_pop(c, LX, LY, g):
        draw_li(c, LX, LY, 0.85, "smile", rh=(LX + 100, LY - 330))
    KX = cx + 260 + 30 * math.sin(T * 1.6)
    KY = cy + 220 + 20 * math.cos(T * 1.3)
    if T >= te:
        c.drawPath(P((LX + 100, LY - 330), (KX - 20, KY + 60)), wb.marker(INK, 3))
        with K.at(c, KX, KY, 10 * math.sin(T * 2), g):
            kite = P((0, -90), (70, 0), (0, 110), (-70, 0), close=True)
            c.drawPath(kite, K.paint(RED_FILL))
            c.drawPath(kite, wb.marker(RED, 6))
    if T >= th:
        K.text(c, "线在你手里", cx - 60, cy + 280, 52, "hand", GREEN, clamp01((T - th) / 0.3))
        sparkle(c, LX + 100, LY - 330, T - th, YELLOW, 8, 40, 120)


def rain_icon(c, x, y, dt):
    with K.at(c, x, y, 0, pop_scale(dt)):
        c.drawOval(skia.Rect.MakeXYWH(-70, -60, 140, 70), K.paint("#C9CED6"))
        for q in range(4):
            C.line(c, (-45 + q * 30, 20), (-55 + q * 30, 60), BLUE, 5)


L.note("线在你手里")
KT.ending(14, "你为别人的看法放弃过什么？", ["穿搭", "发言", "爱好"], 19, 20, enc, 21, ["明明出了事", "大家都说没有？"],
          enc_piece=2, next_icon=rain_icon)

# ================================================================ 收尾
L.finish(cover_shot=6, square_shot=6, notes=NOTES)
L.export(globals())
