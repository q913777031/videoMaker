"""《资治通鉴》05 约法三章：规矩定了一大堆，为什么没人守？（白板手绘 + AI 旁白，竖屏 2:3）

比喻贯穿：一大串钥匙（每次开门一把把试）对三把钥匙。刘邦入咸阳——秦法苛细（竹简堆成山）、召父老约法三章、余悉除去、
派人随秦吏逐县逐乡去讲、百姓献牛羊酒食他不受、民唯恐沛公不为秦王；今人部分把二十条规矩砍到三条、写清后果、当面讲到每个人。
古人的屏画在卷轴框里，今人在办公室。文案见 zizhi/PLAN.md「### 05」。
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
                          at_pop, bamboo_slips, box, bubble_box, city_wall, desk, draw_ace, draw_li, draw_wang, flag, gu,
                          head_of, pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "通鉴里的故事", 4),
    ([6, 7], "约法三章", 5),
    ([8], "余悉除去", 6),
    ([9, 10], "派人去讲", 7),
    ([11, 12], "百姓献礼", 8),
    ([13], "民又益喜", 9),
    ([14, 15], "规矩少了", 10),
    ([16, 17], "说回我们自己", 11),
    ([18], "第一步", 12),
    ([19], "第二步", 13),
    ([20], "第三步", 14),
    ([21], "好处", 15),
    ([22, 23, 24, 25], "评论区见", 16),
]

THEME = ZT.get("05")
L = Z.Lesson("05", SCREENS, drop_screen=2, board_size=(5000, 12000), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(15)]
Z_ = 0.72

NOTES = [
    "出处：司马光《资治通鉴》卷九 汉纪一（高帝元年）沛公入咸阳、约法三章。",
    "原文：“父老苦秦苛法久矣，诽谤者族，偶语者弃市……与父老约，法三章耳：杀人者死，伤人及盗抵罪。余悉除去秦法。"
    "诸吏民皆案堵如故……无恐！”“乃使人与秦吏行县、乡、邑告谕之。秦民大喜，争持牛羊酒食献飨军士。沛公又让不受，"
    "曰：仓粟多，非乏，不欲费民。民又益喜，唯恐沛公不为秦王。”",
    "“规矩少了，反倒有人守了”是对这段的概括。今人（小李、小王、同事）为虚构示意；古人造型为示意。",
]

LIU, ELDER, QINLI, MIN = "red", "brown", "gray", "ochre"
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
        c.drawRoundRect(r, 18, 18, K.paint(PARCH, 0.8 * a))
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


def key(c, x, y, s=1.0, rot=0.0, col="#C9A34A", a=1.0):
    with K.at(c, x, y, rot, s):
        c.drawCircle(0, 0, 30, K.paint(col, a))
        c.drawCircle(0, 0, 30, wb.marker(INK, 4, a))
        c.drawCircle(0, 0, 10, K.paint("#FFFFFF", a))
        C.line(c, (28, 0), (110, 0), INK, 9, a)
        C.line(c, (90, 0), (90, 22), INK, 7, a)
        C.line(c, (106, 0), (106, 16), INK, 7, a)


def door(c, x, y, open_=0.0, a=1.0):
    """门（(x, y) 门脚中点），open_ 0–1 向内开。"""
    w, h = 260, 460
    box(c, x, y - h / 2, w + 30, h + 30, "#E3D2BE", "#5E4128", 6, 6, a)
    ww = w * (1 - 0.7 * open_)
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h, ww, h), K.paint("#C98B4B", a))
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h, ww, h), wb.marker("#7A4A1E", 6, a))
    c.drawCircle(x - w / 2 + ww - 30, y - h / 2, 12, K.paint(INK, a))
    if open_ > 0:
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + ww, y - h, w - ww, h), K.paint("#FFF6D6", a))


def rule_list(c, x, y, n, w=420, rowh=34, hot=None, a=1.0, cut=None):
    """规矩清单：n 条横线；cut=(剩几条, 进度) 时其余各条被剪掉、飘走。"""
    h = n * rowh + 70
    box(c, x, y, w, h, "#FFFFFF", BLACK, 6, 10, a)
    for i in range(n):
        yy = y - h / 2 + 50 + i * rowh
        if cut and i >= cut[0]:
            f = cut[1]
            C.line(c, (x - w / 2 + 40 + 60 * f, yy + 80 * f * (i % 3)), (x + w / 2 - 40 + 60 * f, yy + 80 * f * (i % 3)),
                   GRAY, 5, a * (1 - f))
            continue
        C.line(c, (x - w / 2 + 40, yy), (x + w / 2 - 40 - (i % 3) * 30, yy), RED if hot and i < hot else GRAY, 6, a)


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


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：墙上二十条规矩，同事走过不看；流程图过两周绕回原点
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_wall = kq(j, wp(0, 1, 0.3), 0)
    k_20 = nx(j, wp(0, 2, 0.5), k_wall)
    k_walk = nx(j, wp(0, 3, 0.4), k_20)
    k_flow = nx(j, wp(1, 0, 0.6), k_walk)
    k_loop = nx(j, wp(1, 2, 0.4), k_flow)
    L.note("二十条", "第2周")

    def wall(c, kk, T):
        g = pop_scale(T - tb(j, k_wall))
        if g <= 0:
            return None
        with K.at(c, cx - 250, cy - 170, 0, g):
            rule_list(c, 0, 0, 14, 420, 30)
        if T >= tb(j, k_20):
            with K.at(c, cx - 250, cy - 450, -4, C.slam_scale(T - tb(j, k_20))):
                chip(c, 0, 0, "二十条", RED_FILL, RED, 56)
        return None
    ev(j, k_wall, wall, "wood_high", 0.65)
    b.hit(j, k_20, "rim", 0.8, "二十条")

    def walkers(c, kk, T):
        tw = tb(j, k_walk)
        g = pop_scale(T - tw + 0.3)
        if g <= 0:
            return None
        for i in range(2):
            x, dy, _ = C.walk(T, tw + i * 0.2, 1.6, cx - 520 + i * 120, cx + 50 + i * 120, 10)
            with at_pop(c, x, GY + dy, g):
                if i:
                    draw_wang(c, x, GY + dy, 0.8, head_dx=10)
                else:
                    draw_li(c, x, GY + dy, 0.8, "flat")
        return None
    b.custom(j, k_walk, k_walk + 0.3, walkers, sfx="shaker", gain=0.6)

    def flow(c, kk, T):
        tf, tl = tb(j, k_flow), tb(j, k_loop)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        x0, y0 = cx + 300, cy - 200
        pts = [(x0 - 120, y0 - 150), (x0 + 120, y0 - 150), (x0 + 120, y0 + 50), (x0 - 120, y0 + 50)]
        for i, p_ in enumerate(pts):
            box(c, p_[0], p_[1], 120, 80, "#FFFFFF", BLUE, 5, 12, clamp01(g))
        f = ease_in_out(clamp01((T - tl) / 0.8)) if T >= tl else 0
        for i in range(3):
            C.line(c, pts[i], pts[i + 1], BLUE, 4)
        if f > 0:
            c.drawPath(wb.partial(wb.arrow(pts[3], pts[0], 0.4, 26), f)[0], wb.marker(RED, 8))
            K.text(c, "第2周", x0, y0 + 190, 50, "hand", RED, f)
        return None
    ev(j, k_flow, flow, "pop", 0.65)
    b.hit(j, k_loop, "tom", 0.75, "又回到老样子")


screen1()


# ================================================================ 屏 2（drop）：一大串钥匙，小李在门口一把把试
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_keys = kq(j, wp(2, 0, 0.5), 0)
    k_try = nx(j, wp(2, 2, 0.2), k_keys)
    L.note("✕")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, 0))
        if g <= 0:
            return None
        DX = cx + 280
        with at_pop(c, DX, GY, g):
            door(c, DX, GY)
        hy = GY - 290
        LX = cx - 160
        tk, tt, td = tb(j, k_keys), tb(j, k_try), tb(j, dk)
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "sad" if T >= td else "flat", rh=(LX + 150, hy + 100))
        if T >= tk:
            gk = pop_scale(T - tk)
            jig = 8 * math.sin((T - tt) * 20) if T >= tt else 0
            with K.at(c, LX + 170, hy + 100, jig, gk):
                c.drawCircle(0, 0, 40, wb.marker(GRAY, 6))
                for i in range(12):
                    a = -60 + i * 22
                    key(c, 40 * math.cos(math.radians(a)), 40 * math.sin(math.radians(a)), 0.7, a,
                        ("#C9A34A", "#9AA3AD", "#C98B4B")[i % 3])
        if T >= td:
            with K.at(c, DX, cy - 100, 0, C.slam_scale(T - td)):
                c.drawPath(cross(0, 0, 90), wb.marker(RED, 16))
        return None
    ev(j, 0, scene, "wood_low", 0.6)
    b.hit(j, k_keys, "shaker", 0.75, "一大串钥匙")
    b.hit(j, k_try, "wood_high", 0.7, "一把把试")
    b.hit(j, dk, "kick", 0.9, "还是没开")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：制度文件越翻越厚，纸页满天飞，找不到那一页
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_book = kq(j, wp(3, 0, 0.5), 0)
    k_thick = nx(j, wp(3, 1, 0.5), k_book)
    k_fly = nx(j, wp(3, 2, 0.5), k_thick)
    k_q = nx(j, wp(3, 3, 0.4), k_fly)
    L.note("制度文件", "第几页？")
    LX = cx - 330

    def li(c, sc, T):
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 0.95, "sad" if T >= tb(j, k_q) else "flat", rh=(LX + 150, GY - 250))
        return None
    ev(j, 0, L.pop_fn(j, 0, li), "wood_low", 0.6)

    def book(c, kk, T):
        tb_, tt, tf, tq = tb(j, k_book), tb(j, k_thick), tb(j, k_fly), tb(j, k_q)
        g = pop_scale(T - tb_)
        if g <= 0:
            return None
        th = 60 if T < tt else lerp(60, 300, ease_out(clamp01((T - tt) / 0.5)))
        x, y = cx + 160, GY - 220
        with K.at(c, x, y, 0, g):
            c.drawRect(skia.Rect.MakeXYWH(-200, -th, 400, th), K.paint("#FFFFFF"))
            for q in range(int(th / 12)):
                C.line(c, (-200, -q * 12), (200, -q * 12), GRAY, 2)
            c.drawRect(skia.Rect.MakeXYWH(-200, -th, 400, th), wb.marker(BLUE, 6))
            K.text(c, "制度文件", 0, -th - 40, 54, "sans_medium", BLUE)
        if T >= tf:
            for i in range(8):
                f = clamp01((T - tf - i * 0.06) / 0.9)
                if f <= 0:
                    continue
                px = x + (i - 4) * 70 * f * 2
                py = y - 300 - 260 * math.sin(f * math.pi * 0.8) + 100 * f
                with K.at(c, px, py, f * 200 * (1 if i % 2 else -1)):
                    box(c, 0, 0, 120, 160, "#FFFFFF", GRAY, 4, 4)
        if T >= tq:
            with K.at(c, LX + 60, cy - 380, 0, C.slam_scale(T - tq)):
                bubble_box(c, 0, 0, 320, 120, -1)
                K.text(c, "第几页？", 0, 0, 56, "hand", RED)
        return None
    ev(j, k_book, book, "wood_high", 0.6)
    b.hit(j, k_thick, "tom", 0.7, "越翻越厚")
    b.hit(j, k_fly, "shaker", 0.75, "纸页乱飞")
    b.hit(j, k_q, "rim", 0.8, "找不到那一页")


screen3()


# ================================================================ 屏 4：竹简“资治通鉴 卷九”；刘邦进咸阳；秦法竹简堆成山
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_slip = kq(j, wp(4, 0, 0.3), 0)
    k_liu = nx(j, wp(4, 2, 0.3), k_slip)
    k_law = nx(j, wp(5, 1, 0.4), k_liu)
    k_kill = nx(j, wp(5, 3, 0.4), k_law)
    SX = cx - 360
    L.note("资治通鉴", "卷九", "汉纪一", "刘邦", "咸阳", "秦法")

    def slips(c, kk, T):
        f = ease_out(clamp01((T - tb(j, k_slip)) / 0.6))
        if f <= 0:
            return None
        bamboo_slips(c, SX, cy - 150, max(60, 300 * f), 620, n=max(1, int(4 * f)))
        a = clamp01((T - tb(j, k_slip) - 0.3) / 0.3)
        slip_text(c, SX + 40, cy - 400, "资治通鉴", 76, "#3A2A12", a)
        slip_text(c, SX - 70, cy - 370, "卷九", 60, RED, a)
        slip_text(c, SX - 70, cy - 210, "汉纪一", 46, "#5E4128", a, 1.15)
        return None
    ev(j, k_slip, slips, "muyu", 0.7, 0.6)

    def liu(c, kk, T):
        tl = tb(j, k_liu)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, cx + 50, GY, g):
            city_wall(c, cx + 50, GY, 420, 300, label="咸阳")
        x, dy, _ = C.walk(T, tl, 0.9, cx - 300, cx - 120, 10)
        with at_pop(c, x, GY + dy, g):
            gu(c, x, GY + dy, 0.8, LIU, hat="guan", beard="black")
            name_tag(c, x, GY - 360 + dy, "刘邦", "#9C2F25", 40)
        return None
    b.custom(j, k_liu, k_liu + 0.3, liu, sfx="tom", gain=0.75)

    def law(c, kk, T):
        tl, tk = tb(j, k_law), tb(j, k_kill)
        if T < tl:
            return None
        n = int(lerp(1, 9, clamp01((T - tl) / 0.6)))
        for i in range(n):
            r_, q = divmod(i, 3)
            with K.at(c, cx + 300 + (q - 1) * 70 + r_ * 35, cy - 160 - r_ * 110, (q - 1) * 6):
                bamboo_slips(c, 0, 0, 120, 140, n=2)
        K.text(c, "秦法", cx + 300, cy + 20, 56, "serif_black", "#5E4128", clamp01((T - tl) / 0.3))
        if T >= tk:
            with K.at(c, cx + 430, cy + 160, 0, pop_scale(T - tk)):
                gu(c, 0, 0, 0.4, MIN, hat="bun", mood="o")
                bubble_box(c, -120, -200, 160, 80, 1)
                K.text(c, "闲话", -120, -200, 36, "hand", INK)
                c.drawPath(cross(-120, -200, 50), wb.marker(RED, 10))
        return None
    L.note("闲话")
    b.custom(j, k_law, k_law + 0.3, law, sfx="shaker", gain=0.75)
    b.hit(j, k_kill, "rim", 0.8, "说闲话都可能被杀")


screen4()


# ================================================================ 屏 5：刘邦召父老；三根竹简依次落下（约法三章）
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_liu = 0
    k_elders = kq(j, wp(6, 1, 0.4), 1)
    k_say = nx(j, wp(6, 3, 0.3), k_elders)
    k_3 = nx(j, wp(7, 1, 0.5), k_say)
    k_s = [nx(j, wp(7, 2, 0.3), k_3)]
    k_s.append(nx(j, wp(7, 3, 0.4), k_s[0]))
    k_s.append(nx(j, wp(7, 4, 0.3), k_s[1]))
    LX = cx - 400
    RULES = ["杀人者死", "伤人抵罪", "盗抵罪"]
    L.note(*RULES, "三条", "父老")

    def liu(c, sc, T):
        with at_pop(c, LX, GY, sc):
            gu(c, LX, GY, 0.9, LIU, hat="guan", beard="black", rh=(LX + 150, GY - 330) if T >= tb(j, k_say) else None)
            name_tag(c, LX, GY - 410, "刘邦", "#9C2F25", 40)
        return None
    ev(j, k_liu, L.pop_fn(j, k_liu, liu), "muyu", 0.6)

    def elders(c, kk, T):
        te = tb(j, k_elders)
        for i, x in enumerate((cx + 180, cx + 330, cx + 480)):
            g = pop_scale(T - te - i * 0.1)
            if g <= 0:
                continue
            with at_pop(c, x, GY, g):
                gu(c, x, GY, 0.62, ELDER if i != 1 else "gray", hat="bun", beard="white", mood="o")
        if T >= te:
            name_tag(c, cx + 330, GY - 260, "父老", "#5E4128", 36, clamp01((T - te) / 0.3))
        return None
    b.custom(j, k_elders, k_elders + 0.3, elders, sfx="wood_low", gain=0.65)

    def slips(c, kk, T):
        t3 = tb(j, k_3)
        if T >= t3:
            with K.at(c, cx - 80, cy - 470, 0, C.slam_scale(T - t3)):
                chip(c, 0, 0, "三条", RED_FILL, RED, 60)
        for i, (k_, s_) in enumerate(zip(k_s, RULES)):
            t0 = tb(j, k_)
            g = C.slam_scale(T - t0)
            if g <= 0:
                continue
            with K.at(c, cx - 140 + i * 150, cy - 70, 0, g):
                bamboo_slips(c, 0, 0, 110, 560, n=1)
                slip_text(c, 0, -210, s_, 78, RED if i == 0 else INK)
        return None
    b.custom(j, k_3, k_3 + 0.3, slips)
    b.hit(j, k_3, "tom", 0.8, "只约三条")
    for k_ in k_s:
        b.hit(j, k_, "bangzi", 0.8, "一根竹简落下")


screen5()


# ================================================================ 屏 6：秦法竹简山被一推而倒，只留三根
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    k_pile = 0
    k_push = kq(j, wp(8, 1, 0.3), 1)
    L.note("秦法", "废除")

    def pile(c, kk, T):
        g = pop_scale(T - tb(j, k_pile), 0.4)
        if g <= 0:
            return None
        tp = tb(j, k_push)
        f = ease_in_out(clamp01((T - tp) / 0.6)) if T >= tp else 0
        for i in range(15):
            r_, q = divmod(i, 5)
            x = cx - 160 + (q - 2) * 110 + r_ * 30
            y = cy + 200 - r_ * 160
            ang = (q - 2) * 3 + f * (60 + i * 5)
            with K.at(c, x + f * (200 + i * 30), y + f * (150 + r_ * 120), ang, g):
                bamboo_slips(c, 0, 0, 100, 200, n=2, alpha=1 - 0.6 * f)
        K.text(c, "秦法", cx - 160, cy - 420, 70, "serif_black", "#5E4128", clamp01(g) * (1 - f))
        if T >= tp:
            K.burst(c, cx, cy + 100, T - tp, GRAY, 40, 200, 8, 8, 0.6)
            seal(c, cx + 250, cy - 340, "废除", 80, -8, C.slam_scale(T - tp - 0.3))
        for i, s_ in enumerate(("杀人者死", "伤人抵罪", "盗抵罪")):
            gx = cx - 420 + i * 95
            with K.at(c, gx, cy + 140, 0, clamp01(g)):
                bamboo_slips(c, 0, 0, 80, 420, n=1)
                slip_text(c, 0, -150, s_, 60, RED if i == 0 else INK)
        return None
    ev(j, k_pile, pile, "wood_low", 0.65)
    b.hit(j, k_push, "kick", 0.9, "秦法全部废除")
    b.shots[j].shake = [(k_push, 11.0)]


screen6()


# ================================================================ 屏 7：地图上县乡逐个亮起，使者和秦吏并肩走；百姓照旧耕田
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_pair = kq(j, wp(9, 1, 0.3), 0)
    k_map = nx(j, wp(9, 2, 0.5), k_pair)
    k_calm = nx(j, wp(10, 1, 0.5), k_map)
    k_safe = nx(j, wp(10, 2, 0.4), k_calm)
    L.note("县", "乡", "不用害怕")
    PTS = [(cx - 380, cy - 380), (cx - 140, cy - 300), (cx + 120, cy - 420), (cx + 360, cy - 330), (cx - 260, cy - 160),
           (cx + 10, cy - 120), (cx + 280, cy - 170)]

    def mapf(c, kk, T):
        tm = tb(j, k_map)
        g = pop_scale(T - tb(j, k_pair))
        if g <= 0:
            return None
        for i in range(len(PTS) - 1):
            C.line(c, PTS[i], PTS[i + 1], GRAY, 3, 0.6)
        for i, (x, y) in enumerate(PTS):
            lit = T >= tm + i * 0.12
            c.drawCircle(x, y, 40, K.paint(NOTE_FILL if lit else "#FFFFFF"))
            c.drawCircle(x, y, 40, wb.marker(ORANGE if lit else GRAY, 5))
            K.text(c, "县" if i % 2 == 0 else "乡", x, y + 2, 40, "serif_black", INK)
        with at_pop(c, cx - 200, GY - 200, g):
            x, dy, _ = C.walk(T, tb(j, k_pair), 2.0, cx - 300, cx - 120, 8)
            gu(c, x, GY - 200 + dy, 0.6, LIU, hat="bun")
            gu(c, x + 120, GY - 200 + dy, 0.6, QINLI, hat="guan", beard="black")
            name_tag(c, x, GY - 420 + dy, "使者", "#9C2F25", 30)
            name_tag(c, x + 120, GY - 420 + dy, "秦吏", "#5E5E58", 30)
        return None
    L.note("使者", "秦吏")
    b.custom(j, k_pair, k_pair + 0.3, mapf, sfx="wood_low", gain=0.65)
    b.hit(j, k_map, "shaker", 0.75, "一个县一个乡亮起")

    def farm(c, kk, T):
        tc, ts = tb(j, k_calm), tb(j, k_safe)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        hoe = 20 * math.sin((T - tc) * 5)
        for i, x in enumerate((cx + 200, cx + 400)):
            with at_pop(c, x, GY, g):
                gu(c, x, GY, 0.6, MIN, hat="bun", mood="smile" if T >= ts else "flat",
                   rh=(x + 80, GY - 160 + hoe))
                C.line(c, (x + 80, GY - 160 + hoe), (x + 130, GY - 20), "#7A4A1E", 6)
        C.line(c, (cx + 80, GY + 4), (cx + 540, GY + 4), "#8B6B43", 6)
        if T >= ts:
            with K.at(c, cx + 300, cy + 100, 0, C.slam_scale(T - ts)):
                chip(c, 0, 0, "不用害怕", GREEN_FILL, GREEN, 54)
        return None
    b.custom(j, k_calm, k_calm + 0.3, farm, sfx="pop", gain=0.65)
    b.hit(j, k_safe, "ding", 0.8, "不用害怕")


screen7()


# ================================================================ 屏 8：百姓牵牛羊提酒饭来；刘邦摆手，指向粮仓
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_come = kq(j, wp(11, 1, 0.4), 0)
    k_gift = nx(j, wp(11, 2, 0.5), k_come)
    k_no = nx(j, wp(12, 0, 0.6), k_gift)
    k_barn = nx(j, wp(12, 1, 0.5), k_no)
    LX = cx - 380
    L.note("粮仓", "不收")

    def liu(c, kk, T):
        tn = tb(j, k_no)
        g = pop_scale(T - tb(j, 0) - 0.1)
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            gu(c, LX, GY, 0.9, LIU, hat="guan", beard="black", mood="smile",
               rh=(LX + 150 + 25 * math.sin((T - tn) * 10), GY - 300) if T >= tn else None)
            name_tag(c, LX, GY - 410, "刘邦", "#9C2F25", 40)
        if T >= tn:
            with K.at(c, LX + 60, cy - 160, 0, pop_scale(T - tn)):
                bubble_box(c, 0, 0, 200, 110, -1)
                K.text(c, "不收", 0, 0, 56, "hand", RED)
        return None
    b.custom(j, 0, 0.3, liu, sfx="muyu", gain=0.6)
    b.hit(j, k_no, "rim", 0.8, "刘邦不收")

    def people(c, kk, T):
        tc, tg = tb(j, k_come), tb(j, k_gift)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        x, dy, _ = C.walk(T, tc, 1.0, cx + 520, cx + 150, 10)
        with at_pop(c, x, GY + dy, g):
            gu(c, x, GY + dy, 0.7, MIN, hat="bun", mood="smile", lh=(x - 100, GY - 150 + dy))
            gu(c, x + 180, GY + dy, 0.7, "brown", hat="bun", beard="white", mood="smile", lh=(x + 80, GY - 200 + dy))
        if T >= tg:
            gg = pop_scale(T - tg)
            with K.at(c, x - 170, GY - 70, 0, gg):
                c.drawOval(skia.Rect.MakeXYWH(-80, -50, 160, 90), K.paint("#FFFFFF"))
                c.drawOval(skia.Rect.MakeXYWH(-80, -50, 160, 90), wb.marker(INK, 5))
                c.drawCircle(-90, -40, 30, K.paint("#FFFFFF"))
                c.drawCircle(-90, -40, 30, wb.marker(INK, 5))
                for lx in (-50, 40):
                    C.line(c, (lx, 40), (lx, 80), INK, 6)
            with K.at(c, x + 70, GY - 210, 0, gg):
                cup = P((-30, -40), (30, -40), (24, 30), (-24, 30), close=True)
                c.drawPath(cup, K.paint("#C98B4B"))
                c.drawPath(cup, wb.marker("#7A4A1E", 5))
        return None
    b.custom(j, k_come, k_come + 0.3, people, sfx="wood_low", gain=0.65)
    b.hit(j, k_gift, "pop", 0.75, "牛羊酒饭")

    def barn(c, kk, T):
        tb_ = tb(j, k_barn)
        g = pop_scale(T - tb_)
        if g <= 0:
            return None
        with K.at(c, cx + 60, cy - 330, 0, g):
            body = P((-150, 120), (-150, -40), (0, -150), (150, -40), (150, 120), close=True)
            c.drawPath(body, K.paint("#E9D49A"))
            c.drawPath(body, wb.marker("#8B6B43", 6))
            K.text(c, "粮仓", 0, 30, 60, "serif_black", "#5E4128")
            for q in range(3):
                c.drawOval(skia.Rect.MakeXYWH(-120 + q * 80, 70, 70, 40), K.paint(YELLOW))
        return None
    b.custom(j, k_barn, k_barn + 0.3, barn, sfx="ding", gain=0.7)


screen8()


# ================================================================ 屏 9：百姓围着刘邦欢呼，头上冒出“王”字
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_liu = 0
    k_cheer = kq(j, wp(13, 0, 0.6), 1)
    k_wang = nx(j, wp(13, 2, 0.5), k_cheer)
    L.note("王")

    def scene(c, sc, T):
        tc = tb(j, k_cheer)
        with at_pop(c, cx, GY, sc):
            gu(c, cx, GY - 40, 0.95, LIU, hat="guan", beard="black", mood="smile")
            for i, x in enumerate((cx - 430, cx - 280, cx + 280, cx + 430)):
                jump = -abs(math.sin((T - tc) * 6 + i)) * 30 if T >= tc else 0
                gu(c, x, GY + jump, 0.65, (MIN, "brown", ELDER, "gray")[i], hat="bun", mood="laugh" if T >= tc else "smile",
                   rh=(x + 50, GY - 300 + jump) if T >= tc and i % 2 == 0 else None,
                   lh=(x - 50, GY - 300 + jump) if T >= tc and i % 2 == 1 else None)
        return None
    ev(j, k_liu, L.pop_fn(j, k_liu, scene), "wood_low", 0.6)
    b.hit(j, k_cheer, "clap", 0.8, "百姓欢呼")

    def wang(c, kk, T):
        tw = tb(j, k_wang)
        if T < tw:
            return None
        sparkle(c, cx, cy - 300, T - tw, YELLOW, 12, 100, 200)
        seal(c, cx, cy - 340, "王", 110, 0, C.slam_scale(T - tw))
        return None
    ev(j, k_wang, wang, "bianzhong", 0.85)


screen9()


# ================================================================ 屏 10：一大串钥匙换成三把钥匙，门一下就开
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_bunch = 0
    k_three = kq(j, wp(14, 1, 0.4), 1)
    k_open = nx(j, wp(15, 1, 0.5), k_three)
    k_know = nx(j, wp(15, 2, 0.5), k_open)
    L.note("三把", "会怎样")
    DX = cx + 260

    def scene(c, kk, T):
        tt, to, tk = tb(j, k_three), tb(j, k_open), tb(j, k_know)
        g = pop_scale(T - tb(j, k_bunch))
        if g <= 0:
            return None
        op = ease_out(clamp01((T - to) / 0.5)) if T >= to else 0
        with at_pop(c, DX, GY, g):
            door(c, DX, GY, op)
        x, y = cx - 280, cy - 150
        f = ease_in_out(clamp01((T - tt) / 0.4)) if T >= tt else 0
        with K.at(c, x, y, 0, g):
            c.drawCircle(0, 0, 50, wb.marker(GRAY, 6))
            n = 12 if f < 0.5 else 3
            for i in range(n):
                a = -60 + i * (22 if n == 12 else 50)
                key(c, 50 * math.cos(math.radians(a)), 50 * math.sin(math.radians(a)), 0.9 if n == 3 else 0.7, a,
                    ("#C9A34A", "#9AA3AD", "#C98B4B")[i % 3], abs(f - 0.5) * 2 if f else 1)
        if T >= tt:
            K.text(c, "三把", x, y + 220, 64, "hand", GREEN, clamp01((T - tt - 0.3) / 0.2))
        if op:
            sparkle(c, DX, GY - 250, T - to, YELLOW, 10, 80, 170)
        if T >= tk:
            with K.at(c, DX, cy - 400, 0, C.slam_scale(T - tk)):
                chip(c, 0, 0, "犯了会怎样", NOTE_FILL, ORANGE, 48)
        return None
    L.note("犯了会怎样")
    ev(j, k_bunch, scene, "shaker", 0.6)
    b.hit(j, k_three, "pop", 0.75, "换成三把")
    b.hit(j, k_open, "ding", 0.85, "门一下就开")
    b.hit(j, k_know, "rim", 0.7, "知道犯了会怎样")


screen10()


# ================================================================ 屏 11：说回我们：小李对着二十条规矩挠头；“三步”
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_scratch = kq(j, wp(16, 1, 0.4), 1)
    k_3 = nx(j, wp(17, 1, 0.5), k_scratch)
    LX = cx - 330
    L.note("不自觉？", "三步")

    def scene(c, sc, T):
        ts = tb(j, k_scratch)
        hy = GY - 290
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 1.0, "sad", rh=(LX + 40 + 10 * math.sin((T - ts) * 14), hy - 50) if T >= ts else None)
        with K.at(c, cx + 140, cy - 160, 0, sc):
            rule_list(c, 0, 0, 14, 380, 28)
        if T >= ts:
            with K.at(c, LX + 30, cy - 420, 0, pop_scale(T - ts)):
                bubble_box(c, 0, 0, 280, 110, -1)
                K.text(c, "不自觉？", 0, 0, 52, "hand", GRAY)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_scratch, "wood_high", 0.6, "挠头")
    L.stamp_ev(j, k_3, "三步", cx + 280, cy + 300, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen11()


# ================================================================ 屏 12：第一步：二十条清单被剪刀剪到三条
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 0)
    k_list = kq(j, wp(18, 0, 0.6), 1)
    k_cut = nx(j, wp(18, 1, 0.5), k_list)
    k_keep = nx(j, wp(18, 2, 0.5), k_cut)
    L.note("最要紧")

    def scene(c, kk, T):
        tl, tc, tk = tb(j, k_list), tb(j, k_cut), tb(j, k_keep)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        f = ease_in_out(clamp01((T - tc) / 0.7)) if T >= tc else 0
        with K.at(c, cx - 60, cy + 40, 0, g):
            rule_list(c, 0, 0, 20, 460, 34, 3 if T >= tk else None, 1.0, (3, f) if f else None)
        if T >= tc and f < 1:
            sx, sy = cx + 220, lerp(cy - 210, cy + 360, f)
            with K.at(c, sx, sy, 90):
                for sg in (-1, 1):
                    C.line(c, (0, 0), (90, sg * 22 * (0.5 + 0.5 * math.sin(T * 30))), GRAY, 8)
                    c.drawCircle(-30, sg * 26, 22, wb.marker(RED, 6))
        if T >= tk:
            with K.at(c, cx + 300, cy - 300, 4, C.slam_scale(T - tk)):
                chip(c, 0, 0, "最要紧", RED_FILL, RED, 54)
        return None
    ev(j, k_list, scene, "wood_high", 0.65)
    b.hit(j, k_cut, "shaker", 0.8, "剪掉")
    b.hit(j, k_keep, "kick", 0.85, "只留三条")


screen12()


# ================================================================ 屏 13：第二步：每条后面加一张后果小卡——周报晚交 → 周一当面补讲
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 1)
    k_rules = kq(j, wp(19, 0, 0.6), 1)
    k_late = nx(j, wp(19, 2, 0.4), k_rules)
    k_then = nx(j, wp(19, 3, 0.4), k_late)
    ROWS = ["周报周五交", "会议准时到", "改动先说"]
    L.note(*ROWS, "晚交", "周一当面补讲")

    def scene(c, kk, T):
        tr, tl, tt = tb(j, k_rules), tb(j, k_late), tb(j, k_then)
        for i, s_ in enumerate(ROWS):
            g = pop_scale(T - tr - i * 0.12)
            if g <= 0:
                continue
            y = cy - 260 + i * 230
            with K.at(c, cx - 230, y, 0, g):
                box(c, 0, 0, 440, 140, "#FFFFFF", BLUE, 6, 12)
                K.text(c, s_, 0, 0, 54, "hand", INK)
        if T >= tl:
            with K.at(c, cx - 230, cy - 380, -6, C.slam_scale(T - tl)):
                chip(c, 0, 0, "晚交", RED_FILL, RED, 44)
        if T >= tt:
            f = ease_out(clamp01((T - tt) / 0.3))
            c.drawPath(wb.arrow((cx + 20, cy - 260), (cx + 20 + 120 * f, cy - 260), 0.0, 26), wb.marker(ORANGE, 8))
            with K.at(c, cx + 340, cy - 260, 0, pop_scale(T - tt)):
                box(c, 0, 0, 380, 160, NOTE_FILL, ORANGE, 6, 12)
                K.text(c, "周一当面补讲", 0, 0, 50, "hand", INK)
        return None
    ev(j, k_rules, scene, "wood_high", 0.65)
    b.hit(j, k_late, "rim", 0.8, "周报晚交")
    b.hit(j, k_then, "tom", 0.8, "会怎样写清楚")


screen13()


# ================================================================ 屏 14：第三步：小李一个个工位走过去当面讲
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 2)
    GY = cy + 520
    k_group = kq(j, wp(20, 0, 0.6), 1)
    k_walk = nx(j, wp(20, 1, 0.3), k_group)
    k_d = [nx(j, wp(20, 2, 0.5), k_walk)]
    k_d.append(nx(j, wp(20, 3, 0.5), k_d[0]))
    L.note("群消息", "三条")

    def group(c, kk, T):
        tg = tb(j, k_group)
        g = pop_scale(T - tg)
        if g <= 0:
            return None
        with K.at(c, cx + 300, cy - 340, 0, g):
            box(c, 0, 0, 300, 170, "#FFFFFF", GRAY, 5, 16)
            K.text(c, "群消息", 0, -40, 44, "sans_medium", GRAY)
            c.drawPath(cross(0, 30, 40), wb.marker(RED, 8))
        return None
    ev(j, k_group, group, "pop", 0.6)

    def walk(c, kk, T):
        tw = tb(j, k_walk)
        g = pop_scale(T - tw + 0.3)
        if g <= 0:
            return None
        for i, x in enumerate((cx - 230, cx + 250)):
            with at_pop(c, x, GY, g):
                desk(c, x + 60, GY - 170, 240)
                if i:
                    draw_wang(c, x + 150, GY, 0.8, mood="smile" if T >= tb(j, k_d[1]) else "flat")
                else:
                    draw_ace(c, x + 150, GY, 0.8, mood="smug" if T < tb(j, k_d[0]) else "flat")
        tgt = cx - 300 if T < tb(j, k_d[1]) - 0.6 else cx + 170
        x, dy, _ = C.walk(T, tw, 1.0, cx - 520, cx - 300, 10)
        if T >= tb(j, k_d[1]) - 0.6:
            x, dy, _ = C.walk(T, tb(j, k_d[1]) - 0.6, 0.6, cx - 300, tgt, 10)
        with at_pop(c, x, GY + dy, g):
            draw_li(c, x, GY + dy, 0.85, "smile", rh=(x + 120, GY - 280))
        for i, k_ in enumerate(k_d):
            t0 = tb(j, k_)
            if T >= t0:
                with K.at(c, (cx - 230 if i == 0 else cx + 250) + 40, cy + 30, 0, pop_scale(T - t0)):
                    bubble_box(c, 0, 0, 200, 100, -1)
                    K.text(c, "三条", 0, 0, 48, "hand", RED)
        return None
    b.custom(j, k_walk, k_walk + 0.3, walk, sfx="wood_low", gain=0.6)
    for k_ in k_d:
        b.hit(j, k_, "pop", 0.75, "当面讲一遍")


screen14()


# ================================================================ 屏 15：好处：小李不用追着人跑，同事自己按规矩走
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_rules = kq(j, wp(21, 0, 0.6), 0)
    k_relax = nx(j, wp(21, 1, 0.6), k_rules)
    k_go = nx(j, wp(21, 2, 0.5), k_relax)
    L.note("三条")

    def scene(c, kk, T):
        tr, trl, tg = tb(j, k_rules), tb(j, k_relax), tb(j, k_go)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        with K.at(c, cx + 230, cy - 300, 0, g):
            box(c, 0, 0, 340, 240, "#FFFFFF", GREEN, 6, 12)
            K.text(c, "三条", 0, -70, 54, "hand", GREEN)
            for q in range(3):
                C.line(c, (-110, -10 + q * 40), (110, -10 + q * 40), GRAY, 6)
        LX = cx - 380
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "smile" if T >= trl else "flat",
                    rh=(LX + 60, GY - 330) if T >= trl else None, lh=(LX - 60, GY - 330) if T >= trl else None)
        if T >= trl:
            sparkle(c, LX, GY - 380, T - trl, YELLOW, 8, 50, 110)
        if T >= tg:
            for i, x0 in enumerate((cx - 60, cx + 160, cx + 380)):
                x, dy, _ = C.walk(T, tg + i * 0.15, 1.2, x0, x0 + 60, 8)
                with at_pop(c, x, GY + dy, pop_scale(T - tg - i * 0.1)):
                    if i == 1:
                        draw_wang(c, x, GY + dy, 0.75, mood="smile")
                    else:
                        draw_li(c, x, GY + dy, 0.75, "smile")
        return None
    ev(j, k_rules, scene, "wood_high", 0.6)
    b.hit(j, k_relax, "ding", 0.8, "省心")
    b.hit(j, k_go, "shaker", 0.7, "大家自己按规矩走")


screen15()


# ================================================================ 屏 16：评论区；剪刀剪掉一条；下一讲预告
def screen16(j=16):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z_))
    k_cmt = 0
    k_chips = nx(j, wp(23, 0, 0.3), 0)
    k_li = nx(j, wp(24, 0, 0.4), k_chips)
    k_follow = nx(j, wp(24, 3, 0.3), k_li)
    k_next = nx(j, wp(25, 1, 0.2), k_follow)
    b.move(j, k_li, (cx, cy + 380, Z_), 1.1)
    CH = ["周报格式", "打卡时间", "会议纪要"]
    L.note("最没人守的是哪条？", *CH, "下一讲", "手下的人比你强", "怎么带？")
    BY = cy - 330

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 20, BY, 0, sc):
            bubble_box(c, 0, 0, 1000, 360, -1)
            K.text(c, "最没人守的是哪条？", 0, -110, 60, "hand", RED)
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

    def team(c, kk, T):
        tl, tf = tb(j, k_li), tb(j, k_follow)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, LX, LY, g):
            draw_li(c, LX, LY, 0.95, "smile")
        for i, x0 in enumerate((cx - 80, cx + 120, cx + 320)):
            gi = pop_scale(T - tf - i * 0.12)
            if gi <= 0:
                continue
            x, dy, _ = C.walk(T, tf + i * 0.12, 0.8, x0 + 120, x0, 8)
            with at_pop(c, x, LY + dy, gi):
                if i == 1:
                    draw_wang(c, x, LY + dy, 0.8, mood="smile")
                else:
                    draw_li(c, x, LY + dy, 0.8, "smile")
        if T >= tf:
            sparkle(c, LX, LY - 380, T - tf, YELLOW, 10, 60, 130)
        return None
    ev(j, k_li, team, "wood_low", 0.6)
    b.hit(j, k_follow, "ding", 0.8, "大家跟着你")

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
            K.text(c, "手下的人比你强", -90, -60, 58, "hand", BLACK)
            K.text(c, "怎么带？", -200, 40, 58, "hand", BLACK)
            for q in range(3):
                C.line(c, (300 + q * 60, 80), (300 + q * 60, -20 - q * 20), INK, 8)
                c.drawCircle(300 + q * 60, -40 - q * 20, 20, wb.marker(INK, 5))
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen16()

# ================================================================ 收尾
L.finish(cover_shot=5, square_shot=5, notes=NOTES)
L.export(globals())
