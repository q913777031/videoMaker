"""《资治通鉴》12 投鞭断流：优势那么大，怎么还会输？（白板手绘 + AI 旁白，竖屏 2:3）

误区对照：把“人多就赢”和苻坚对照——群臣劝东晋有能人、有长江；苻坚“投鞭于江，足断其流”；苻融、太子都劝，不听；
八十多万南下对八万；淝水边晋军请秦军稍退，秦军一退就乱、“秦兵败矣”、风声鹤唳；苻融战死，苻坚中箭北逃；
最后把“人多 = 赢定了”的等号划掉，三步（找唱反调的人、列对手长处、想好退路）。古人的屏画在卷轴框里，今人在办公室。
文案见 zizhi/PLAN.md「### 12」。
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
                          RED_FILL, WATER, WATER_LINE, YELLOW, at_pop, bamboo_slips, box, bubble_box, chip, city_wall, desk,
                          draw_ace, draw_li, draw_wang, flag, gu, name_tag, pop_scale, seal, slip_text, sparkle, water)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "通鉴里的故事", 4),
    ([6], "投鞭断流", 5),
    ([7, 8], "不听劝", 6),
    ([9, 10], "淝水边", 7),
    ([11, 12], "一退就乱", 8),
    ([13], "结局", 9),
    ([14, 15], "说回我们自己", 10),
    ([16], "第一步", 11),
    ([17], "第二步", 12),
    ([18], "第三步", 13),
    ([19], "好处", 14),
    ([20, 21, 22, 23], "评论区见", 15),
]

THEME = ZT.get("12")
from fengtian import build as _FB  # noqa: E402
_FB.limiter.__defaults__ = (-3.4, 0.004)   # 本讲接片尾重编码后 32.5s 处真峰值冒到 -0.6，限幅天花板压低 0.8 dB（只影响本进程）
L = Z.Lesson("12", SCREENS, drop_screen=2, board_size=(5000, 12000), theme=THEME,
             trim_tail={13: 0.12})         # 第 13 句句尾碎音（识别成“吃/之”），裁掉
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(14)]
Z_ = 0.72
KT = Z.Kit(L, R)

NOTES = [
    "出处：司马光《资治通鉴》卷一〇四 晋纪二十六（太元七年）、卷一〇五 晋纪二十七（太元八年）。",
    "原文：坚曰“以吾之众旅，投鞭于江，足断其流”；阳平公融、太子宏等谏，不听；坚发长安“戎卒六十余万，骑二十七万”，晋“众共八万”；"
    "玄请秦军“少却”，坚欲半渡击之；“秦兵遂退，不可复止”，朱序呼“秦兵败矣”；“闻风声鹤唳，皆以为王师已至”；融战死，坚为流矢所中。",
    "今人（小李、小王、同事）为虚构示意；古人造型为示意。",
]

FU, RONG, PRINCE, JIN = "purple", "teal", "red", "blue"


def soldiers(c, x, y, rows, cols, s=0.3, col="purple", dx=70, dy=60, a=1.0, fall=0.0):
    for r_ in range(rows):
        for q in range(cols):
            fx = fall * ((q * 7 + r_ * 3) % 5 - 2) * 20
            with K.at(c, x + q * dx - r_ * 20 + fx, y - r_ * dy, fall * ((q + r_) % 3 - 1) * 40):
                gu(c, 0, 0, s, col, hat="helmet", alpha=a)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：资源堆成山、业绩箭头朝上，“稳了”；一个细节漏掉，订单飞走
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_res = kq(j, wp(0, 1, 0.5), 1)
    k_up = nx(j, wp(0, 2, 0.5), k_res)
    k_safe = nx(j, wp(0, 3, 0.4), k_up)
    k_fly = nx(j, wp(1, 1, 0.4), k_safe)
    LX = cx - 330
    L.note("稳了", "订单", "细节")

    def scene(c, kk, T):
        tr, tu, ts, tf = tb(j, k_res), tb(j, k_up), tb(j, k_safe), tb(j, k_fly)
        g = pop_scale(T - tb(j, k_li))
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "sad" if T >= tf else "smile", rh=(LX + 120, GY - 330) if ts <= T < tf else None)
        if T >= tr:
            for i in range(6):
                with K.at(c, cx + 80 + (i % 3) * 120, GY - 40 - (i // 3) * 90, 0, pop_scale(T - tr - i * 0.06)):
                    box(c, 0, 0, 110, 80, ("#D5E3F7", NOTE_FILL, GREEN_FILL)[i % 3], GRAY, 4, 8)
        if T >= tu:
            f = ease_out(clamp01((T - tu) / 0.5))
            c.drawPath(wb.partial(wb.arrow((cx - 60, cy + 40), (cx + 300, cy - 300), 0.2, 40), f)[0], wb.marker(GREEN, 12))
        if T >= ts and T < tf + 0.2:
            with K.at(c, LX + 80, cy - 300, 0, pop_scale(T - ts)):
                bubble_box(c, 0, 0, 220, 110, -1)
                K.text(c, "稳了", 0, 0, 60, "hand", GREEN)
        if T >= tf:
            f = ease_in_out(clamp01((T - tf) / 0.8))
            with K.at(c, lerp(cx + 200, cx + 560, f), lerp(cy - 100, cy - 500, f), 30 * f, 1):
                box(c, 0, 0, 180, 120, "#FFFFFF", RED, 5, 10)
                K.text(c, "订单", 0, 0, 44, "hand", RED)
            c.drawCircle(cx - 40, cy + 200, 30, wb.marker(RED, 6))
            K.text(c, "细节", cx - 40, cy + 280, 40, "hand", RED)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_res, "pop", 0.7, "资源最多")
    b.hit(j, k_up, "shaker", 0.7, "业绩最好")
    b.hit(j, k_safe, "ding", 0.7, "稳了")
    b.hit(j, k_fly, "tom", 0.85, "整单丢了")


screen1()


# ================================================================ 屏 2（drop）：比分牌领先一大截，后半场被一口气追平
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    dk = L.drop_k()
    k_lead = kq(j, wp(2, 0, 0.5), 0)
    k_slack = nx(j, wp(2, 1, 0.5), k_lead)
    L.note("我们", "对手", "松劲")

    def scene(c, kk, T):
        tl, ts, td = tb(j, k_lead), tb(j, k_slack), tb(j, dk)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 150, 0, g):
            box(c, 0, 0, 700, 360, "#24293B", BLACK, 6, 18)
            K.text(c, "我们", -170, -110, 46, "sans_medium", "#FFFFFF")
            K.text(c, "对手", 170, -110, 46, "sans_medium", "#FFFFFF")
            us = 30
            them = 10 if T < ts else int(lerp(10, 30, clamp01((T - ts) / max(0.3, td - ts))))
            K.text(c, f"{us}", -170, 40, 130, "black", YELLOW)
            K.text(c, f"{them}", 170, 40, 130, "black", RED if them >= us else "#FFFFFF")
            K.text(c, ":", 0, 30, 100, "black", "#FFFFFF")
        if T >= ts:
            K.text(c, "松劲", cx - 300, cy + 200, 60, "hand", GRAY, clamp01((T - ts) / 0.2))
        if T >= td:
            seal(c, cx + 250, cy + 220, "追平", 80, -6, C.slam_scale(T - td))
        return None
    L.note("追平")
    ev(j, k_lead, scene, "wood_high", 0.65)
    b.hit(j, k_slack, "shaker", 0.7, "后半场松劲")
    b.hit(j, dk, "kick", 0.9, "被追上")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：小李戴着耳机摆手，劝的人的话弹开
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = kq(j, wp(3, 0, 0.5), 0)
    k_b = nx(j, wp(3, 1, 0.5), k_li)
    LX = cx - 160
    L.note("小心点", "再看看")

    def scene(c, kk, T):
        tl, tbn = tb(j, k_li), tb(j, k_b)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        hy = GY - 290
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "smile", rh=(LX + 130, hy + 40 + 20 * math.sin(T * 8)))
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(LX - 60, hy - 70, 120, 110), 180, 180)
            c.drawPath(arc, wb.marker(INK, 8))
            for sg in (-1, 1):
                c.drawRoundRect(skia.Rect.MakeXYWH(LX + sg * 55 - 15, hy - 20, 30, 50), 10, 10, K.paint(RED))
        for i, s_ in enumerate(("小心点", "再看看")):
            t0 = tbn + i * 0.3
            if T < t0:
                continue
            f = clamp01((T - t0) / 0.8)
            x = lerp(cx + 400, LX + 120, min(1, f * 2)) if f < 0.5 else lerp(LX + 120, cx + 520, (f - 0.5) * 2)
            y = cy - 200 + i * 160 - (0 if f < 0.5 else 200 * (f - 0.5))
            with K.at(c, x, y, f * 60 if f > 0.5 else 0, 1):
                bubble_box(c, 0, 0, 240, 100, 1)
                K.text(c, s_, 0, 0, 48, "hand", INK)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_b, "rim", 0.8, "劝的话弹开")


screen3()


# ================================================================ 屏 4：竹简“卷一〇四”；苻坚站在北方，指向东晋；大臣劝：能人、长江
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(4, 0, 0.3), 0)
    k_fu = nx(j, wp(4, 1, 0.4), k_book)
    k_jin = nx(j, wp(4, 3, 0.4), k_fu)
    k_warn = nx(j, wp(5, 1, 0.4), k_jin)
    k_river = nx(j, wp(5, 2, 0.4), k_warn)
    KT.book(j, k_book, "卷一〇四", "晋纪二十六")
    L.note("苻坚", "前秦", "东晋", "能人", "长江")

    def scene(c, kk, T):
        tf, tj, tw, tr = tb(j, k_fu), tb(j, k_jin), tb(j, k_warn), tb(j, k_river)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        with K.at(c, cx + 120, cy - 230, 0, g):
            box(c, 0, 0, 600, 360, PARCH, PARCH_LINE, 6, 8)
            c.drawRect(skia.Rect.MakeXYWH(-290, -170, 580, 170), K.paint("#E6D6EE", 0.8))
            K.text(c, "前秦", -150, -90, 56, "serif_black", "#6B3F7A")
            if T >= tr:
                p = skia.Path()
                p.moveTo(-290, 30)
                p.cubicTo(-100, -10, 100, 70, 290, 20)
                c.drawPath(p, wb.marker(WATER_LINE, 18))
                K.text(c, "长江", 180, -20, 40, "hand", BLUE)
            if T >= tj:
                K.text(c, "东晋", 120, 110, 56, "serif_black", BLUE, clamp01((T - tj) / 0.3))
                c.drawPath(wb.arrow((-120, -60), (90, 80), 0.2, 30), wb.marker(RED, 8, clamp01((T - tj) / 0.3)))
        FX = cx - 350
        with at_pop(c, FX, GY, g):
            gu(c, FX, GY, 0.95, FU, hat="guan", beard="black", mood="laugh", rh=(FX + 160, GY - 360) if T >= tj else None)
            name_tag(c, FX, GY - 440, "苻坚", "#6B3F7A", 42)
        if T >= tw:
            x = cx + 300
            with at_pop(c, x, GY, pop_scale(T - tw)):
                gu(c, x, GY, 0.75, "gray", hat="guan", beard="white", bow=True)
            with K.at(c, x - 40, cy + 70, 0, pop_scale(T - tw)):
                chip(c, 0, 0, "能人", GREEN_FILL, GREEN, 46)
        return None
    b.custom(j, k_fu, k_fu + 0.3, scene, sfx="tom", gain=0.75)
    b.hit(j, k_jin, "rim", 0.75, "要打东晋")
    b.hit(j, k_warn, "pop", 0.7, "东晋有能人")
    b.hit(j, k_river, "shaker", 0.75, "还有长江")


screen4()


# ================================================================ 屏 5：无数马鞭扔进江里，江水被截断（苻坚想象的画面）
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_fu = 0
    k_toss = kq(j, wp(6, 2, 0.3), 1)
    k_cut = nx(j, wp(6, 3, 0.5), k_toss)
    L.note("截断", "想象")
    RY = cy + 80

    def scene(c, kk, T):
        tt, tc = tb(j, k_toss), tb(j, k_cut)
        g = pop_scale(T - tb(j, k_fu))
        if g <= 0:
            return None
        c.drawOval(skia.Rect.MakeXYWH(cx - 560, cy - 560, 1120, 1000), K.paint("#FFFFFF", 0.35))
        K.text(c, "想象", cx - 420, cy - 470, 40, "hand", GRAY)
        cut = ease_out(clamp01((T - tc) / 0.5)) if T >= tc else 0
        for sg in (-1, 1):
            x0, x1 = (cx - 560, cx - 60 - 200 * cut * 0) if sg < 0 else (cx + 60, cx + 560)
            if sg > 0 and cut > 0:
                lvl = RY + 20 + 80 * cut
            else:
                lvl = RY
            water(c, x0, x1, lvl if sg > 0 else RY, RY + 160, T, 0.7)
        water(c, cx - 60, cx + 60, RY + 160 * cut, RY + 160, T, 0.7)
        if T >= tt:
            for i in range(14):
                t0 = tt + (i % 7) * 0.06
                f = clamp01((T - t0) / 0.5)
                if f <= 0:
                    continue
                sx = cx - 300 + (i * 47) % 600
                x = lerp(sx, cx - 40 + (i % 5) * 20, f)
                y = lerp(cy - 420, RY + 40 + (i // 5) * 30, f * f)
                with K.at(c, x, y, f * 280 + i * 20):
                    C.line(c, (-60, 0), (60, 0), "#7A4A1E", 7)
                    C.line(c, (60, 0), (90, 20), INK, 3)
        if T >= tc:
            seal(c, cx + 280, cy - 300, "截断", 80, -6, C.slam_scale(T - tc))
        with at_pop(c, cx - 380, GY, g):
            gu(c, cx - 380, GY, 0.8, FU, hat="guan", beard="black", mood="laugh", rh=(cx - 240, GY - 320))
        return None
    ev(j, k_fu, scene, "wood_low", 0.6)
    b.hit(j, k_toss, "shaker", 0.85, "马鞭扔进江里")
    b.hit(j, k_cut, "kick", 0.9, "江水截断")
    b.shots[j].shake = [(k_cut, 9.0)]


screen5()


# ================================================================ 屏 6：苻融、太子拉袖子，他甩开；兵力对比条：八十多万 vs 八万
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_rong = kq(j, wp(7, 0, 0.5), 0)
    k_prince = nx(j, wp(7, 1, 0.4), k_rong)
    k_no = nx(j, wp(7, 2, 0.4), k_prince)
    k_bar = nx(j, wp(8, 1, 0.5), k_no)
    k_jin = nx(j, wp(8, 2, 0.5), k_bar)
    FX = cx - 80
    L.note("苻融", "太子", "八十多万", "八万", "秦", "晋")

    def scene(c, kk, T):
        tr, tp, tn, tbr, tj = tb(j, k_rong), tb(j, k_prince), tb(j, k_no), tb(j, k_bar), tb(j, k_jin)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        sh = 18 * math.sin((T - tn) * 16) * math.exp(-(T - tn) * 3) if T >= tn else 0
        with at_pop(c, FX, GY, g):
            gu(c, FX + sh, GY, 0.9, FU, hat="guan", beard="black", mood="angry" if T >= tn else "flat")
            name_tag(c, FX, GY - 420, "苻坚", "#6B3F7A", 38)
        for i, (t0, x, col, nm) in enumerate(((tr, cx - 380, RONG, "苻融"), (tp, cx + 230, PRINCE, "太子"))):
            if T < t0:
                continue
            back = 40 * ease_out(clamp01((T - tn) / 0.3)) if T >= tn else 0
            xx = x + (-back if i == 0 else back)
            with at_pop(c, xx, GY, pop_scale(T - t0)):
                gu(c, xx, GY, 0.75, col, hat="guan", beard="black" if i == 0 else None, mood="o",
                   rh=(FX - 60, GY - 230) if i == 0 and T < tn else None, lh=(FX + 60, GY - 230) if i == 1 and T < tn else None)
                name_tag(c, xx, GY - 350, nm, "#2C6E68" if i == 0 else "#9C2F25", 34)
        if T >= tbr:
            f = ease_out(clamp01((T - tbr) / 0.6))
            y = cy - 330
            c.drawRoundRect(skia.Rect.MakeXYWH(cx - 460, y - 40, 860 * f, 80), 20, 20, K.paint("#E6D6EE"))
            c.drawRoundRect(skia.Rect.MakeXYWH(cx - 460, y - 40, 860 * f, 80), 20, 20, wb.marker("#6B3F7A", 5))
            K.text(c, "秦 八十多万", cx - 40, y, 46, "hand", "#6B3F7A", f)
        if T >= tj:
            f = ease_out(clamp01((T - tj) / 0.4))
            y = cy - 200
            c.drawRoundRect(skia.Rect.MakeXYWH(cx - 460, y - 40, 86 * f, 80), 20, 20, K.paint(BLUE_FILL))
            c.drawRoundRect(skia.Rect.MakeXYWH(cx - 460, y - 40, 86 * f, 80), 20, 20, wb.marker(BLUE, 5))
            K.text(c, "晋 八万", cx - 230, y, 46, "hand", BLUE, f)
        return None
    L.note("秦 八十多万", "晋 八万")
    ev(j, k_rong, scene, "wood_low", 0.6)
    b.hit(j, k_prince, "pop", 0.65, "太子也劝")
    b.hit(j, k_no, "rim", 0.8, "他都没听")
    b.hit(j, k_bar, "shaker", 0.75, "八十多万南下")
    b.hit(j, k_jin, "tom", 0.75, "东晋八万")


screen6()


# ================================================================ 屏 7：两军隔着淝水，晋军使者请秦军后退；苻坚点头，打算半渡而击
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_river = kq(j, wp(9, 0, 0.5), 0)
    k_ask = nx(j, wp(9, 1, 0.5), k_river)
    k_plan = nx(j, wp(10, 1, 0.5), k_ask)
    k_yes = nx(j, wp(10, 2, 0.4), k_plan)
    L.note("淝水", "往后退一点", "半渡而击")
    RX = cx + 60

    def scene(c, kk, T):
        tr, ta, tp, ty = tb(j, k_river), tb(j, k_ask), tb(j, k_plan), tb(j, k_yes)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        c.drawRect(skia.Rect.MakeXYWH(RX - 90, cy - 520, 180, 1100), K.paint(WATER, 0.75))
        C.line(c, (RX - 90, cy - 520), (RX - 90, cy + 580), WATER_LINE, 6)
        C.line(c, (RX + 90, cy - 520), (RX + 90, cy + 580), WATER_LINE, 6)
        K.text(c, "淝水", RX, cy - 460, 50, "serif_black", BLUE)
        soldiers(c, cx - 480, GY - 200, 4, 4, 0.3, "purple")
        soldiers(c, cx + 260, GY - 200, 2, 3, 0.3, "blue")
        if T >= ta:
            with K.at(c, cx + 300, cy - 250, 0, pop_scale(T - ta)):
                bubble_box(c, 0, 0, 360, 110, -1)
                K.text(c, "往后退一点", 0, 0, 50, "hand", INK)
        if T >= tp:
            with at_pop(c, cx - 300, cy - 30, pop_scale(T - tp)):
                gu(c, cx - 300, cy - 30, 0.55, FU, hat="guan", beard="black", mood="smile")
            with K.at(c, cx - 300, cy - 330, 0, pop_scale(T - tp)):
                c.drawOval(skia.Rect.MakeXYWH(-170, -70, 340, 140), K.paint("#FFFFFF"))
                c.drawOval(skia.Rect.MakeXYWH(-170, -70, 340, 140), wb.marker(GRAY, 5))
                K.text(c, "半渡而击", 0, 0, 50, "hand", "#6B3F7A")
        if T >= ty:
            c.drawPath(wb.partial(check(cx - 140, cy - 60, 40), ease_out(clamp01((T - ty) / 0.3)))[0], wb.marker(GREEN, 10))
        return None
    ev(j, k_river, scene, "muyu", 0.65)
    b.hit(j, k_ask, "pop", 0.7, "请秦军后退")
    b.hit(j, k_plan, "wood_high", 0.7, "想趁过河时打")
    b.hit(j, k_yes, "ding", 0.75, "答应了")


screen7()


# ================================================================ 屏 8：秦军一退就倒成一片；“秦兵败矣”；风声鹤唳
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_back = kq(j, wp(11, 0, 0.5), 0)
    k_stop = nx(j, wp(11, 1, 0.5), k_back)
    k_shout = nx(j, wp(11, 3, 0.3), k_stop)
    k_mess = nx(j, wp(12, 1, 0.5), k_shout)
    k_crane = nx(j, wp(12, 2, 0.5), k_mess)
    L.note("秦兵败了", "风声", "鹤叫")

    def scene(c, kk, T):
        tbk, ts, tsh, tm, tc = tb(j, k_back), tb(j, k_stop), tb(j, k_shout), tb(j, k_mess), tb(j, k_crane)
        g = pop_scale(T - tbk)
        if g <= 0:
            return None
        fall = ease_out(clamp01((T - tm) / 0.6)) if T >= tm else 0
        shift = -80 * clamp01((T - tbk) / 0.8) - (60 * clamp01((T - ts) / 0.6) if T >= ts else 0)
        soldiers(c, cx - 300 + shift, GY - 120, 4, 6, 0.3, "purple", 80, 70, 1.0, fall)
        if T >= tsh:
            with K.at(c, cx + 200, cy - 330, -4, C.slam_scale(T - tsh)):
                bubble_box(c, 0, 0, 380, 130, -1)
                K.text(c, "秦兵败了！", 0, 0, 58, "hand", RED)
        if T >= tc:
            for q in range(4):
                f = ((T - tc) * 0.8 + q * 0.25) % 1
                C.line(c, (cx - 520 + 300 * f, cy - 380 + q * 40), (cx - 400 + 300 * f, cy - 390 + q * 40), GRAY, 5, 1 - f)
            with K.at(c, cx + 340, cy - 100, 0, pop_scale(T - tc)):
                p = P((-60, 0), (0, -20), (60, -60), (20, 0), (60, 30), (0, 10), close=True)
                c.drawPath(p, K.paint("#FFFFFF"))
                c.drawPath(p, wb.marker(INK, 4))
                C.line(c, (0, 10), (0, 80), INK, 4)
            K.text(c, "风声", cx - 380, cy - 440, 44, "hand", GRAY, clamp01((T - tc) / 0.2))
            K.text(c, "鹤叫", cx + 340, cy - 200, 44, "hand", GRAY, clamp01((T - tc) / 0.2))
        return None
    ev(j, k_back, scene, "wood_low", 0.65)
    b.hit(j, k_stop, "shaker", 0.8, "停不下来")
    b.hit(j, k_shout, "rim", 0.85, "秦兵败了")
    b.hit(j, k_mess, "kick", 0.9, "乱成一团")
    b.hit(j, k_crane, "xiaoluo", 0.8, "风声鹤唳")
    b.shots[j].shake = [(k_mess, 11.0)]


screen8()


# ================================================================ 屏 9：苻融倒下，苻坚中箭，单骑逃回北方
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_rong = kq(j, wp(13, 0, 0.5), 0)
    k_arrow = nx(j, wp(13, 1, 0.5), k_rong)
    k_flee = nx(j, wp(13, 2, 0.4), k_arrow)
    L.note("北方")

    def scene(c, kk, T):
        tr, ta, tf = tb(j, k_rong), tb(j, k_arrow), tb(j, k_flee)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        with K.at(c, cx - 220, GY - 60, -85):
            gu(c, 0, 0, 0.7, RONG, hat="guan", beard="black", mood="sad")
        x, dy, _ = C.walk(T, tf, 1.2, cx + 50, cx + 380, 14) if T >= tf else (cx + 50, 0, False)
        with at_pop(c, x, GY + dy, g):
            gu(c, x, GY + dy, 0.8, FU, hat="guan", beard="black", mood="sad")
            if T >= ta:
                C.line(c, (x - 20, GY - 160 + dy), (x - 100, GY - 210 + dy), INK, 5)
        if T >= tf:
            c.drawPath(wb.arrow((cx + 300, cy - 200), (cx + 300, cy - 460), 0.0, 40), wb.marker(GRAY, 10))
            K.text(c, "北方", cx + 420, cy - 400, 56, "hand", GRAY)
        return None
    ev(j, k_rong, scene, "tom", 0.75)
    b.hit(j, k_arrow, "rim", 0.85, "苻坚中箭")
    b.hit(j, k_flee, "wood_low", 0.75, "逃回北方")


screen9()


# ================================================================ 屏 10：“人多 = 赢定了”的等号被划掉；“三步”
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_eq = kq(j, wp(14, 1, 0.4), 0)
    k_cross = nx(j, wp(14, 2, 0.5), k_eq)
    k_3 = nx(j, wp(15, 1, 0.5), k_cross)
    L.note("人多", "赢定了", "三步")

    def scene(c, kk, T):
        te, tc = tb(j, k_eq), tb(j, k_cross)
        g = pop_scale(T - te)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 200, 0, g):
            box(c, -280, 0, 240, 130, "#E6D6EE", "#6B3F7A", 6, 14)
            K.text(c, "人多", -280, 0, 60, "hand", "#6B3F7A")
            K.text(c, "=", 0, 0, 110, "black", INK)
            box(c, 280, 0, 280, 130, NOTE_FILL, ORANGE, 6, 14)
            K.text(c, "赢定了", 280, 0, 60, "hand", ORANGE)
            if T >= tc:
                f = ease_out(clamp01((T - tc) / 0.25))
                C.line(c, (-60, 70), (-60 + 120 * f, 70 - 140 * f), RED, 14)
        return None
    ev(j, k_eq, scene, "wood_high", 0.65)
    b.hit(j, k_cross, "rim", 0.85, "等号划掉")
    L.stamp_ev(j, k_3, "三步", cx, cy + 260, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen10()


# ================================================================ 屏 11：第一步：小李请唱反调的同事坐下，认真记笔记
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_sit = kq(j, wp(16, 1, 0.4), 1)
    k_say = nx(j, wp(16, 1, 0.95), k_sit)
    k_note = nx(j, wp(16, 2, 0.5), k_say)
    L.note("我不同意", "风险")

    def scene(c, kk, T):
        ts, tsy, tn = tb(j, k_sit), tb(j, k_say), tb(j, k_note)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            desk(c, cx, GY - 170, 440, laptop=False)
            draw_li(c, cx - 320, GY, 0.9, "flat", rh=(cx - 170, GY - 210) if T >= tn else None)
            draw_ace(c, cx + 320, GY, 0.9, mood="flat", lh=(cx + 180, GY - 300) if T >= tsy else None)
        if T >= tsy:
            with K.at(c, cx + 240, cy - 230, 0, C.slam_scale(T - tsy)):
                bubble_box(c, 0, 0, 340, 120, 1)
                K.text(c, "我不同意", 0, 0, 54, "hand", RED)
        if T >= tn:
            with K.at(c, cx - 140, cy + 40, 0, pop_scale(T - tn)):
                box(c, 0, 0, 220, 160, NOTE_FILL, ORANGE, 5, 8)
                K.text(c, "风险", 0, -30, 44, "hand", RED)
                C.line(c, (-70, 30), (70, 30), GRAY, 4)
        return None
    ev(j, k_sit, scene, "wood_low", 0.6)
    b.hit(j, k_say, "rim", 0.75, "唱反调")
    b.hit(j, k_note, "pop", 0.75, "认真记下")


screen11()


# ================================================================ 屏 12：第二步：对手的长处一条条列在白板上
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_board = kq(j, wp(17, 0, 0.6), 1)
    k_rows = nx(j, wp(17, 1, 0.5), k_board)
    k_ours = nx(j, wp(17, 2, 0.5), k_rows)
    ROWS = ["价格低", "交货快", "老客户多"]
    L.note("对手的长处", *ROWS, "我们有多少")

    def scene(c, kk, T):
        tbd, tr, to = tb(j, k_board), tb(j, k_rows), tb(j, k_ours)
        g = pop_scale(T - tbd)
        if g <= 0:
            return None
        with K.at(c, cx + 80, cy - 140, 0, g):
            box(c, 0, 0, 620, 440, "#FFFFFF", BLACK, 6, 12)
            K.text(c, "对手的长处", 0, -170, 52, "hand", BLUE)
            for i, s_ in enumerate(ROWS):
                a = clamp01((T - tr - i * 0.2) / 0.2)
                K.text(c, f"{i + 1}. {s_}", -200, -70 + i * 90, 50, "hand", INK, a, "left")
        if T >= to:
            with K.at(c, cx + 80, cy + 220, 0, pop_scale(T - to)):
                chip(c, 0, 0, "我们有多少", GRAY_FILL, GRAY, 44)
                c.drawPath(cross(0, 0, 100), wb.marker(RED, 8))
        with at_pop(c, cx - 400, GY, g):
            draw_li(c, cx - 400, GY, 0.85, "flat", rh=(cx - 260, GY - 330))
        return None
    ev(j, k_board, scene, "wood_high", 0.65)
    b.hit(j, k_rows, "shaker", 0.75, "一条条列出来")
    b.hit(j, k_ours, "rim", 0.75, "别只数自己")


GRAY_FILL = "#D9DCE1"
screen12()


# ================================================================ 屏 13：第三步：台阶图——万一出岔子，退到第二级还能站稳
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_steps = kq(j, wp(18, 0, 0.6), 1)
    k_slip = nx(j, wp(18, 1, 0.5), k_steps)
    k_hold = nx(j, wp(18, 2, 0.5), k_slip)
    L.note("岔子", "稳住")

    def scene(c, kk, T):
        ts, tsl, th = tb(j, k_steps), tb(j, k_slip), tb(j, k_hold)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        for i in range(4):
            box(c, cx - 300 + i * 200, GY - 60 - i * 140, 200, 120 + i * 140 * 0, ("#E7D6BA", "#E7D6BA", GREEN_FILL, "#E7D6BA")[i],
                "#8B6B43" if i != 1 else GREEN, 5, 4)
        top = 3
        lvl = top
        if T >= tsl:
            lvl = 1 if T >= th else lerp(3, 1, clamp01((T - tsl) / max(0.3, th - tsl)))
        x = cx - 300 + lvl * 200
        y = GY - 120 - lvl * 140
        with at_pop(c, x, y, g):
            draw_li(c, x, y, 0.5, "smile" if T >= th else ("o" if T >= tsl else "smile"))
        if T >= tsl:
            K.text(c, "岔子", cx + 380, GY - 560, 50, "hand", RED, clamp01((T - tsl) / 0.2))
        if T >= th:
            with K.at(c, cx - 100, GY - 420, 0, C.slam_scale(T - th)):
                chip(c, 0, 0, "稳住", GREEN_FILL, GREEN, 54)
        return None
    ev(j, k_steps, scene, "wood_high", 0.65)
    b.hit(j, k_slip, "tom", 0.75, "出岔子")
    b.hit(j, k_hold, "ding", 0.8, "退到一级还能稳住")


screen13()


# ================================================================ 屏 14：好处：优势变成实打实的结果，奖杯稳稳放在桌上
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_res = kq(j, wp(19, 1, 0.4), 0)
    k_cup = nx(j, wp(19, 1, 0.95), k_res)
    k_keep = nx(j, wp(19, 2, 0.5), k_cup)
    L.note("结果")

    def scene(c, kk, T):
        tr, tc, tk = tb(j, k_res), tb(j, k_cup), tb(j, k_keep)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            desk(c, cx + 100, GY - 170, 420, laptop=False)
            draw_li(c, cx - 300, GY, 0.95, "smile", rh=(cx - 160, GY - 330) if T >= tk else None)
        if T >= tc:
            with K.at(c, cx + 100, GY - 190, 0, C.slam_scale(T - tc)):
                cupp = P((-60, -200), (60, -200), (40, -110), (12, -80), (-12, -80), (-40, -110), close=True)
                c.drawPath(cupp, K.paint(YELLOW))
                c.drawPath(cupp, wb.marker("#A9842A", 6))
                C.line(c, (0, -80), (0, -30), "#A9842A", 10)
                box(c, 0, -15, 120, 30, "#C98B4B", "#7A4A1E", 5, 6)
            K.text(c, "结果", cx + 100, cy - 220, 64, "hand", GREEN, clamp01((T - tc) / 0.2))
        if T >= tk:
            sparkle(c, cx + 100, GY - 300, T - tk, YELLOW, 12, 70, 160)
        return None
    ev(j, k_res, scene, "wood_low", 0.6)
    b.hit(j, k_cup, "kick", 0.8, "优势变成结果")
    b.hit(j, k_keep, "ding", 0.8, "稳稳放在桌上")


screen14()


# ================================================================ 屏 15：评论区；小李低头看路，绕过一个坑；下一讲预告
def _enc(c, T, te, th, cx, cy):
    LX, LY = cx - 400, cy + 640
    C.line(c, (cx - 560, LY + 6), (cx + 560, LY + 6), "#8B6B43", 6)
    c.drawOval(skia.Rect.MakeXYWH(cx - 60, LY - 20, 200, 50), K.paint("#5E4128"))
    f = ease_in_out(clamp01((T - te) / max(0.5, th - te + 0.6)))
    x = lerp(LX, cx + 340, f)
    y = LY - 140 * math.sin(math.pi * clamp01((x - (cx - 160)) / 400)) if cx - 160 < x < cx + 240 else LY
    with at_pop(c, x, y, pop_scale(T - te)):
        draw_li(c, x, y, 0.85, "smile")
    if T >= th:
        sparkle(c, x, y - 300, T - th, YELLOW, 10, 50, 120)
        K.text(c, "多看一眼", cx, LY - 380, 60, "hand", GREEN, clamp01((T - th) / 0.2))


L.note("多看一眼")


def _icon(c, x, y, t):
    for q in range(3):
        with K.at(c, x - 30 + q * 25, y + 10 - q * 8, (q - 1) * 10 + 20 * math.sin(t * 2 + q)):
            box(c, 0, 0, 110, 140, "#FFFFFF", GRAY, 4, 6)
            C.line(c, (-30, -30), (30, -30), GRAY, 4)
            C.line(c, (-30, 0), (30, 0), GRAY, 4)


KT.ending(15, "赢面很大却输了的一次？", ["比赛", "投标", "考试"], 21, 22, _enc, 23,
          ["总说没人可用", "人到底在哪？"], enc_piece=0, next_icon=_icon)

# ================================================================ 收尾
L.finish(cover_shot=5, square_shot=8, notes=NOTES)
L.export(globals())
