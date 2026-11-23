"""《百年孤独》01 冰块：想法一个接一个，为什么一件也没做成？（白板手绘 + AI 旁白，竖屏 2:3）

两人对比：何塞·阿尔卡蒂奥·布恩迪亚被吉卜赛人的新玩意儿一个个勾走（磁铁、找出路），一件没做成；
乌尔苏拉撑着家，出门追儿子，带回了通往外面的路。中间是全书第一句（范晔译本）和那块冰。文案见 bainian/PLAN.md「### 01」。
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
                            YELLOW, almond_tree, at_pop, box, bubble_box, butterfly, chip, draw_lady, draw_li, draw_man, draw_wang,
                            house, ice_block, jose, magnet, magnifier, melquiades, name_tag, parchment, pop_scale, progress,
                            sparkle, ursula)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "生活里", 1),
    ([2], "生活里", 2),
    ([3, 4], "书里的人", 3),
    ([5], "吉卜赛人", 4),
    ([6, 7], "磁铁", 5),
    ([8, 9], "找路", 6),
    ([10], "乌尔苏拉", 7),
    ([11, 12, 13, 14], "她找到了路", 8),
    ([15], "第一句", 9),
    ([16], "冰块", 10),
    ([17, 18], "说回我们", 11),
    ([19], "第一步", 12),
    ([20], "第二步", 13),
    ([21], "第三步", 14),
    ([22], "好处", 15),
    ([23, 24, 25, 26], "评论区见", 16),
]

THEME = BT.get("01")
L = N.Lesson("01", SCREENS, drop_screen=2, board_size=(5000, 12400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(17)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》第 1 章（范晔译本）。情节为转述；引文只有全书第一句（范晔译）。",
    "今人（小李、小王）为虚构示意；书中人造型为示意（一百多年前的加勒比小镇打扮）。",
]

JOSE_TAG = ("何塞·阿尔卡蒂奥·布恩迪亚", "第一代 · 父亲")
URS_TAG = ("乌尔苏拉", "第一代 · 母亲")


def tag(c, x, y, who, a=1.0, size=44):
    s, sub = who
    name_tag(c, x, y, s, "#5E4128", size, a, sub)


def animal(c, x, y, s, kind="mule", a=1.0):
    """骡子 / 山羊（简笔）：(x, y) 为脚底中点。"""
    col, line = ("#B9B2A6", "#5E5A52") if kind == "mule" else ("#FFFFFF", "#6B6B6B")
    with K.at(c, x, y, 0, s):
        for dx in (-50, -26, 26, 50):
            C.line(c, (dx, -60), (dx, 0), line, 9, a)
        c.drawOval(skia.Rect.MakeXYWH(-80, -120, 160, 80), K.paint(col, a))
        c.drawOval(skia.Rect.MakeXYWH(-80, -120, 160, 80), wb.marker(line, 5, a))
        hd = skia.Rect.MakeXYWH(70, -170, 60 if kind == "mule" else 48, 44)
        c.drawRoundRect(hd, 18, 18, K.paint(col, a))
        c.drawRoundRect(hd, 18, 18, wb.marker(line, 5, a))
        C.line(c, (60, -110), (82, -150), line, 14, a)
        c.drawCircle(100, -156, 4, K.paint(BLACK, a))
        if kind == "mule":
            for dx in (78, 94):
                C.line(c, (dx, -168), (dx - 6, -206), line, 7, a)
        else:
            c.drawPath(P((80, -168), (66, -200), (58, -176)), wb.marker(line, 5, a))
            C.line(c, (100, -128), (98, -110), line, 5, a)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：小李头顶冒出想法气泡；脚边课程和书越堆越高
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    LX = cx - 240
    k_a = kq(j, wp(0, 1, 0.4), 0)
    k_b = nx(j, wp(0, 2, 0.4), k_a)
    k_c = nx(j, wp(1, 0, 0.5), k_b)
    k_d = nx(j, wp(1, 1, 0.5), k_c)
    L.note("剪视频", "副业", "课程", "书")
    BUB = [("剪视频", cx - 330, cy - 420), ("副业", cx + 80, cy - 480)]

    def scene(c, kk, T):
        ta, tbb, tc, td = tb(j, k_a), tb(j, k_b), tb(j, k_c), tb(j, k_d)
        g = pop_scale(T - ta + 0.3)
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "smile" if T < td else "o")
        for i, (s, x, y) in enumerate(BUB):
            t0 = (ta, tbb)[i]
            sc = pop_scale(T - t0)
            if sc <= 0:
                continue
            with K.at(c, x, y + 8 * math.sin(T * 2 + i), 0, sc):
                c.drawOval(skia.Rect.MakeXYWH(-150, -70, 300, 140), K.paint("#FFFFFF"))
                c.drawOval(skia.Rect.MakeXYWH(-150, -70, 300, 140), wb.marker(BLACK, 6))
                K.text(c, s, 0, 0, 56, "hand", BLUE)
            for q in range(2):
                c.drawCircle(lerp(LX + 30, x, 0.3 + q * 0.25), lerp(GY - 380, y + 80, 0.3 + q * 0.25), 14 - q * 4,
                             wb.marker(BLACK, 4, clamp01(sc)))
        PX = cx + 300
        if T >= tc:
            for q in range(3):
                sc = pop_scale(T - tc - q * 0.12)
                if sc <= 0:
                    continue
                with K.at(c, PX, GY - 50 - q * 95, (q - 1) * 4, sc):
                    box(c, 0, 0, 320, 80, BLUE_FILL, BLUE, 5, 10)
                    K.text(c, "课程", 0, 0, 42, "hand", BLUE)
        if T >= td:
            for q in range(5):
                sc = pop_scale(T - td - q * 0.08)
                if sc <= 0:
                    continue
                with K.at(c, PX + 10, GY - 330 - q * 50, (q % 2) * 5 - 2, sc):
                    box(c, 0, 0, 280, 44, ("#F6C3BE", "#FFF1A8", "#D3EDDC")[q % 3], INK, 4, 6)
            K.text(c, "书", PX + 220, GY - 450, 54, "hand", ORANGE, clamp01((T - td) / 0.3))
        return None
    ev(j, k_a, scene, "pop", 0.7)
    b.hit(j, k_b, "pop", 0.7, "想做副业")
    b.hit(j, k_c, "wood_high", 0.7, "课买了")
    b.hit(j, k_d, "shaker", 0.75, "书囤了一摞")


screen1()


# ================================================================ 屏 2（drop）：一排进度条全卡住，红章“没做完”
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    dk = L.drop_k()
    k_bars = kq(j, wp(2, 0, 0.3), 0)
    ROWS = [("剪视频", 0.08), ("副业", 0.05), ("课程", 0.12), ("读书", 0.03)]
    L.note(*(r[0] for r in ROWS))

    def scene(c, kk, T):
        t0 = tb(j, k_bars)
        for i, (s, f) in enumerate(ROWS):
            sc = pop_scale(T - t0 - i * 0.12)
            if sc <= 0:
                continue
            y = cy - 420 + i * 190
            with K.at(c, cx, y, 0, sc):
                K.text(c, s, -380, 0, 54, "hand", INK)
                progress(c, 120, 0, 600, f * ease_out(clamp01((T - t0 - i * 0.12) / 0.4)), RED, 1, 34)
        return None
    ev(j, k_bars, scene, "wood_low", 0.65)
    ev(j, dk, L.stamp("没做完", cx + 40, cy + 400, 110, j, dk, RED, -6), "kick", 0.9)
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：绿皮书翻开；何塞·阿尔卡蒂奥·布恩迪亚出场；河边几间土坯房“马孔多”
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(3, 0, 0.4), 0)
    k_jose = nx(j, wp(3, 2, 0.2), k_book)
    k_town = nx(j, wp(4, 1, 0.3), k_jose)
    k_name = nx(j, wp(4, 2, 0.3), k_town)
    KT.book(j, k_book, x=cx - 360, y=cy - 300)
    L.note(*JOSE_TAG, "马孔多")
    JX = cx - 330

    def scene(c, kk, T):
        tj, tt, tn = tb(j, k_jose), tb(j, k_town), tb(j, k_name)
        g = pop_scale(T - tj)
        if g <= 0:
            return None
        if T >= tt:
            f = ease_out(clamp01((T - tt) / 0.5))
            rv = P((cx - 40, GY + 60), (cx + 180, GY - 60), (cx + 560, GY - 40))
            c.drawPath(wb.partial(rv, f)[0], wb.marker("#7FB2D9", 40, 0.8))
            for i, (hx, sc_) in enumerate(((cx + 140, 0.55), (cx + 360, 0.5), (cx + 250, 0.42))):
                s = pop_scale(T - tt - 0.1 * i)
                if s > 0:
                    with K.at(c, hx, GY - 130 - i * 90, 0, sc_ * s):
                        house(c, 0, 0)
        if T >= tn:
            with K.at(c, cx + 260, cy - 160, -3, C.slam_scale(T - tn)):
                box(c, 0, 0, 340, 110, "#FFFFFF", RED, 6, 12)
                K.text(c, "马孔多", 0, 2, 70, "serif_black", RED)
        with at_pop(c, JX, GY, g):
            jose(c, JX, GY, 0.95, mood="smile")
        tag(c, JX + 80, GY - 470, JOSE_TAG, clamp01(g))
        return None
    ev(j, k_jose, scene, "bongo_low", 0.75)
    b.hit(j, k_town, "shaker", 0.65, "建起村子")
    b.hit(j, k_name, "rim", 0.8, "马孔多")


screen3()


# ================================================================ 屏 4：梅尔基亚德斯戴宽檐黑帽，箱子打开，冒出新鲜玩意儿
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_march = kq(j, wp(5, 0, 0.3), 0)
    k_mel = nx(j, wp(5, 2, 0.2), k_march)
    k_box = nx(j, wp(5, 3, 0.4), k_mel)
    L.note("每年三月", "梅尔基亚德斯", "吉卜赛人")
    MX = cx - 260

    def scene(c, kk, T):
        tm, tml, tbx = tb(j, k_march), tb(j, k_mel), tb(j, k_box)
        sc = pop_scale(T - tm)
        if sc > 0:
            with K.at(c, cx + 300, cy - 420, 4, sc):
                box(c, 0, 0, 300, 110, NOTE_FILL, ORANGE, 5, 10)
                K.text(c, "每年三月", 0, 2, 54, "hand", RED)
        g = pop_scale(T - tml)
        if g <= 0:
            return None
        x = lerp(cx - 700, MX, ease_out(clamp01((T - tml) / 0.6)))
        with at_pop(c, x, GY, g):
            melquiades(c, x, GY, 1.0, mood="smile", rh=(x + 150, GY - 220))
        name_tag(c, x, GY - 500, "梅尔基亚德斯", "#3A3A3A", 46, clamp01(g), "吉卜赛人")
        BX, BY = cx + 230, GY - 60
        open_ = ease_out(clamp01((T - tbx) / 0.4)) if T >= tbx else 0
        box(c, BX, BY, 340, 200, "#B5562E", "#5E2E18", 7, 10)
        with K.at(c, BX - 170, BY - 100, -70 * open_):
            box(c, 170, -20, 340, 40, "#C96A3E", "#5E2E18", 6, 8)
        if T >= tbx:
            items = ((magnet, -110, -260, 0.6), (magnifier, 20, -330, 0.6), (None, 140, -250, 1.0))
            for i, (fn, dx, dy, s) in enumerate(items):
                f = ease_out(clamp01((T - tbx - i * 0.12) / 0.45))
                if f <= 0:
                    continue
                xx, yy = BX + dx * f, BY - 80 + (dy + 80) * f
                if fn is None:
                    N.ice_block(c, xx, yy + 50, 110, 90, T, f)
                else:
                    fn(c, xx, yy, s * f)
            sparkle(c, BX, BY - 140, T - tbx, YELLOW, 10, 80, 200)
        return None
    ev(j, k_march, scene, "pop", 0.7)
    b.hit(j, k_mel, "bongo_high", 0.75, "吉卜赛人来了")
    b.hit(j, k_box, "ding", 0.8, "新鲜玩意儿")


screen4()


# ================================================================ 屏 5：骡子和山羊换来磁铁；拖着磁铁走，铁锅钉子飞过来；挖出旧盔甲
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_mag = kq(j, wp(6, 0, 0.4), 0)
    k_trade = nx(j, wp(6, 2, 0.3), k_mag)
    k_gold = nx(j, wp(6, 3, 0.5), k_trade)
    k_drag = nx(j, wp(7, 0, 0.3), k_gold)
    k_armor = nx(j, wp(7, 2, 0.4), k_drag)
    L.note("金子？", "旧盔甲")

    def scene(c, kk, T):
        tm, tt, tg, td, ta = (tb(j, k) for k in (k_mag, k_trade, k_gold, k_drag, k_armor))
        dragging = T >= td
        if not dragging:
            sc = pop_scale(T - tm)
            if sc <= 0:
                return None
            with K.at(c, cx, cy - 330, 0, sc):
                magnet(c, 0, 0, 1.2)
            if T >= tt:
                f = pop_scale(T - tt)
                with K.at(c, cx - 300, cy + 40, 0, f):
                    animal(c, 0, 0, 1.0, "mule")
                for i in range(2):
                    with K.at(c, cx + 170 + i * 220, cy + 40, 0, pop_scale(T - tt - 0.1 - 0.1 * i)):
                        animal(c, 0, 0, 0.75, "goat")
                with K.at(c, cx, cy - 130, 0, f):
                    C.line(c, (-80, 0), (80, 0), INK, 8)
                    c.drawPath(P((50, -24), (84, 0), (50, 24)), wb.marker(INK, 8))
                    c.drawPath(P((-50, -24), (-84, 0), (-50, 24)), wb.marker(INK, 8))
            if T >= tg:
                with K.at(c, cx + 300, cy - 420, 6, C.slam_scale(T - tg)):
                    chip(c, 0, 0, "金子？", NOTE_FILL, ORANGE, 56)
            return None
        f = clamp01((T - td) / 1.6)
        JX = lerp(cx - 420, cx + 80, ease_in_out(f))
        dy = 10 * abs(math.sin((T - td) * 8))
        with at_pop(c, JX, GY - dy, 1):
            jose(c, JX, GY - dy, 0.9, mood="smile", rh=(JX + 150, GY - 140))
        magnet(c, JX + 210, GY - 110, 0.55, -90)
        for i in range(6):
            u = clamp01((T - td - 0.1 * i) / 0.6)
            sx, sy = cx - 520 + i * 190, cy - 450 + (i % 2) * 120
            x = lerp(sx, JX + 250, ease_in_out(u))
            y = lerp(sy, GY - 110, ease_in_out(u)) - 60 * math.sin(u * math.pi)
            if i % 2 == 0:
                c.drawOval(skia.Rect.MakeXYWH(x - 40, y - 22, 80, 44), K.paint("#5E5E58"))
                C.line(c, (x - 40, y - 22), (x - 60, y - 40), INK, 6)
            else:
                C.line(c, (x - 26, y), (x + 26, y), "#5E5E58", 8)
                C.line(c, (x - 26, y - 10), (x - 26, y + 10), "#5E5E58", 8)
        if T >= ta:
            g = pop_scale(T - ta)
            AX, AY = cx + 380, GY - 40
            c.drawOval(skia.Rect.MakeXYWH(AX - 150, AY + 10, 300, 60), K.paint("#8A6A3A", 0.6))
            with K.at(c, AX, AY - 60 * g, 0, g):
                body = P((-60, -120), (60, -120), (70, 40), (-70, 40), close=True)
                c.drawPath(body, K.paint("#9AA3AD"))
                c.drawPath(body, wb.marker(INK, 6))
                c.drawCircle(0, -170, 48, K.paint("#9AA3AD"))
                c.drawCircle(0, -170, 48, wb.marker(INK, 6))
                C.line(c, (-28, -170), (28, -170), INK, 8)
                for q in range(4):
                    c.drawCircle(-40 + q * 26, -40 + (q % 2) * 30, 9, K.paint("#B5562E", 0.7))
            K.text(c, "旧盔甲", AX, AY - 300, 54, "hand", GRAY, clamp01((T - ta) / 0.3))
        return None
    ev(j, k_mag, scene, "ding", 0.75)
    b.hit(j, k_trade, "bongo_low", 0.75, "骡子和山羊换磁铁")
    b.hit(j, k_gold, "pop", 0.7, "想吸金子")
    b.hit(j, k_drag, "shaker", 0.75, "铁锅钉子飞过来")
    b.hit(j, k_armor, "tom", 0.8, "只挖出旧盔甲")


screen5()


# ================================================================ 屏 8：沼泽、藤蔓；林子里一艘大帆船；地图上马孔多四周涂成水
def screen8(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_walk = kq(j, wp(8, 0, 0.3), 0)
    k_ship = nx(j, wp(8, 3, 0.3), k_walk)
    k_map = nx(j, wp(9, 0, 0.5), k_ship)
    k_water = nx(j, wp(9, 1, 0.4), k_map)
    L.note("四面是水", "马孔多")

    def scene(c, kk, T):
        tw, ts, tm, tW = (tb(j, k) for k in (k_walk, k_ship, k_map, k_water))
        if T < tw:
            return None
        if T < tm:
            for q in range(7):
                x = cx - 540 + q * 170
                c.drawPath(P((x, cy - 560), (x + 30 * math.sin(q), cy - 300), (x - 20, cy - 120)), wb.marker(N.LEAF_LINE, 6, 0.7))
            for q in range(4):
                c.drawOval(skia.Rect.MakeXYWH(cx - 520 + q * 280, GY - 20 + (q % 2) * 30, 240, 50), K.paint("#9FB58A", 0.6))
            f = clamp01((T - tw) / 2.0)
            for i in range(3):
                x = lerp(cx - 560, cx - 80, f) - i * 150
                dy = 8 * abs(math.sin((T - tw) * 7 + i))
                if i == 0:
                    jose(c, x, GY - dy, 0.75, mood="flat")
                else:
                    draw_man(c, x, GY - dy, 0.7, "ochre", hat="straw")
            if T >= ts:
                g = pop_scale(T - ts)
                SX, SY = cx + 320, GY - 80
                with K.at(c, SX, SY, -8, g):
                    hull = P((-220, -60), (220, -60), (170, 40), (-170, 40), close=True)
                    c.drawPath(hull, K.paint("#8A6A3A"))
                    c.drawPath(hull, wb.marker(INK, 6))
                    C.line(c, (0, -60), (0, -380), "#5E4128", 12)
                    sail = P((10, -360), (150, -300), (130, -120), (10, -100), close=True)
                    c.drawPath(sail, K.paint("#F2E8D2"))
                    c.drawPath(sail, wb.marker(INK, 5))
                    for q in range(3):
                        c.drawPath(P((-200 + q * 160, 40), (-180 + q * 160, -80), (-150 + q * 160, -10)),
                                   wb.marker(N.LEAF_LINE, 6))
            return None
        g = pop_scale(T - tm)
        with K.at(c, cx, cy - 40, 0, g):
            parchment(c, 0, 0, 760, 760)
            for hx, hy in ((-40, 0), (60, 30), (10, -60)):
                with K.at(c, hx, hy + 40, 0, 0.22):
                    house(c, 0, 0)
            K.text(c, "马孔多", 0, 110, 50, "serif_black", INK)
            if T >= tW:
                f = ease_out(clamp01((T - tW) / 0.6))
                ring = skia.Path()
                ring.addOval(skia.Rect.MakeXYWH(-300, -270, 600, 560))
                c.drawPath(wb.partial(ring, f)[0], wb.marker("#7FB2D9", 70, 0.85))
                K.text(c, "四面是水", 0, 250, 56, "hand", BLUE, f)
        return None
    ev(j, k_walk, scene, "shaker", 0.7)
    b.hit(j, k_ship, "tom", 0.8, "林子里的大帆船")
    b.hit(j, k_map, "wood_high", 0.65, "地图")
    b.hit(j, k_water, "bongo_low", 0.75, "四面是水")


screen8()


# ================================================================ 屏 9：乌尔苏拉系着围裙，一手锅一手孩子，地里还有活
def screen9(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_u = kq(j, wp(10, 0, 0.1), 0)
    k_jobs = [nx(j, wp(10, 0, 0.5), k_u)]
    k_jobs.append(nx(j, wp(10, 0, 0.8), k_jobs[0]))
    k_all = nx(j, wp(10, 1, 0.5), k_jobs[1])
    L.note(*URS_TAG, "地里", "孩子", "吃饭")
    UX = cx - 80

    def scene(c, kk, T):
        tu, ta = tb(j, k_u), tb(j, k_all)
        g = pop_scale(T - tu)
        if g <= 0:
            return None
        with at_pop(c, UX, GY, g):
            N.ursula(c, UX, GY, 1.05, mood="flat" if T < ta else "smile", rh=(UX + 150, GY - 220), lh=(UX - 150, GY - 200))
        tag(c, UX, GY - 480, URS_TAG, clamp01(g))
        icons = [("吃饭", cx + 330, cy - 120), ("孩子", cx - 420, cy - 60), ("地里", cx + 330, cy + 200)]
        for i, (s, x, y) in enumerate(icons):
            t0 = tu if i == 0 else tb(j, k_jobs[i - 1])
            sc = pop_scale(T - t0)
            if sc <= 0:
                continue
            with K.at(c, x, y, 0, sc):
                if i == 0:
                    c.drawOval(skia.Rect.MakeXYWH(-90, -20, 180, 90), K.paint("#5E5E58"))
                    c.drawOval(skia.Rect.MakeXYWH(-90, -40, 180, 50), K.paint("#8A8F99"))
                    for q in range(3):
                        f = ((T - t0) * 0.8 + q / 3) % 1
                        c.drawCircle(-40 + q * 40, -60 - 80 * f, 12 + 8 * f, K.paint("#FFFFFF", 0.7 * (1 - f)))
                elif i == 1:
                    draw_man(c, 0, 160, 0.45, "red", mood="smile")
                    draw_lady(c, 90, 160, 0.4, "yellow", hair="short", mood="smile")
                else:
                    for q in range(4):
                        C.line(c, (-110 + q * 70, 60), (-110 + q * 70, -10), N.LEAF_LINE, 8)
                        c.drawOval(skia.Rect.MakeXYWH(-130 + q * 70, -40, 40, 30), K.paint(N.LEAF))
                K.text(c, s, 0, 120 if i != 1 else 210, 48, "hand", ORANGE)
        if T >= ta:
            with K.at(c, UX, cy - 520, 0, C.slam_scale(T - ta)):
                chip(c, 0, 0, "全靠她", RED_FILL, RED, 58)
        return None
    L.note("全靠她")
    ev(j, k_u, scene, "bongo_low", 0.7)
    for k_ in k_jobs:
        b.hit(j, k_, "wood_high", 0.65, "又一件活")
    b.hit(j, k_all, "kick", 0.85, "全靠乌尔苏拉")


screen9()


# ================================================================ 屏 10：乌尔苏拉出门；回来身后跟着一群人；一条路通到马孔多，“两天”
def screen10(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_go = kq(j, wp(11, 2, 0.3), 0)
    k_back = nx(j, wp(12, 0, 0.4), k_go)
    k_crowd = nx(j, wp(12, 2, 0.3), k_back)
    k_road = nx(j, wp(13, 0, 0.5), k_crowd)
    k_two = nx(j, wp(13, 1, 0.4), k_road)
    k_found = nx(j, wp(14, 1, 0.4), k_two)
    L.note("两天", "找到了", "马孔多")

    def scene(c, kk, T):
        tg, tbk, tcr, trd, ttw, tf = (tb(j, k) for k in (k_go, k_back, k_crowd, k_road, k_two, k_found))
        if T < tg:
            return None
        VX = cx + 360
        with K.at(c, VX, cy - 330, 0, 0.45):
            house(c, 0, 0)
        K.text(c, "马孔多", VX, cy - 260, 44, "serif_black", INK)
        if T >= trd:
            f = ease_out(clamp01((T - trd) / 0.7))
            rd = P((cx - 540, cy - 200), (cx - 200, cy - 280), (cx + 60, cy - 220), (VX - 120, cy - 300))
            c.drawPath(wb.partial(rd, f)[0], wb.marker("#C9A46A", 30, 0.9))
            c.drawPath(wb.partial(rd, f)[0], wb.marker("#8A6A3A", 4, 0.9))
            if T >= ttw:
                with K.at(c, cx - 160, cy - 400, 0, C.slam_scale(T - ttw)):
                    chip(c, 0, 0, "两天", NOTE_FILL, ORANGE, 60)
        if T < tbk:
            x = lerp(cx + 60, cx - 640, ease_in_out(clamp01((T - tg) / 1.4)))
            N.ursula(c, x, GY, 0.95, mood="flat", head_dx=-6)
            return None
        f = ease_out(clamp01((T - tbk) / 1.0))
        UX = lerp(cx - 640, cx - 60, f)
        if T >= tcr:
            for i in range(4):
                g = pop_scale(T - tcr - 0.1 * i)
                if g <= 0:
                    continue
                px = UX - 170 - i * 120
                with at_pop(c, px, GY - (i % 2) * 20, g):
                    if i % 2:
                        draw_lady(c, px, GY - (i % 2) * 20, 0.7, ("green", "red")[i // 2], hair="bun", mood="smile")
                    else:
                        draw_man(c, px, GY - (i % 2) * 20, 0.72, ("ochre", "white")[i // 2], hat="straw", mood="smile")
        N.ursula(c, UX, GY, 0.95, mood="smile")
        tag(c, UX, GY - 460, URS_TAG, 1, 40)
        if T >= tf:
            JX = cx + 400
            with at_pop(c, JX, GY, pop_scale(T - tf)):
                jose(c, JX, GY, 0.8, mood="o")
            with K.at(c, cx + 120, cy + 40, 4, C.slam_scale(T - tf)):
                chip(c, 0, 0, "找到了", GREEN_FILL, GREEN, 56)
        return None
    ev(j, k_go, scene, "shaker", 0.65)
    b.hit(j, k_back, "bongo_low", 0.7, "她回来了")
    b.hit(j, k_crowd, "clap", 0.75, "带回一群人")
    b.hit(j, k_road, "wood_high", 0.65, "从沼泽另一边来")
    b.hit(j, k_two, "pop", 0.75, "走两天就到")
    b.hit(j, k_found, "kick", 0.85, "她一趟就找到了")


screen10()


# ================================================================ 屏 11：羊皮卷展开，全书第一句（范晔译本）；末尾“冰块”亮起
def screen11(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_open = kq(j, wp(15, 0, 0.3), 0)
    WORDS = [(1, "多年以后"), (2, "面对行刑队"), (3, "奥雷里亚诺"), (5, "父亲带他去"), (6, "见识冰块")]
    ks, prev = [], k_open
    for pi, _ in WORDS:
        k_ = nx(j, wp(15, pi, 0.3), prev)
        ks.append(k_)
        prev = k_
    L.note("范晔 译", "第一句", *(w for _, w in WORDS))

    def scene(c, kk, T):
        to = tb(j, k_open)
        f = ease_out(clamp01((T - to) / 0.7))
        if f <= 0:
            return None
        parchment(c, cx, cy - 60, 900, 1060, f)
        a = clamp01((T - to - 0.3) / 0.3)
        K.text(c, "第一句", cx, cy - 520, 56, "serif_black", RED, a)
        K.text(c, "范晔 译", cx + 300, cy - 520, 34, "sans_medium", GRAY, a)
        for i, (k_, (_, w)) in enumerate(zip(ks, WORDS)):
            t0 = tb(j, k_)
            if T < t0:
                continue
            last = i == len(WORDS) - 1
            y = cy - 380 + i * 160
            al = clamp01((T - t0) / 0.25)
            if last:
                with K.at(c, cx, y + 20, 0, C.slam_scale(T - t0)):
                    K.text(c, w, 0, 0, 96, "serif_black", BLUE)
                sparkle(c, cx + 200, y, T - t0, "#7FB2D9", 10, 60, 160)
            else:
                K.text(c, w, cx, y, 66, "serif_black", INK, al)
        return None
    ev(j, k_open, scene, "wood_low", 0.65)
    for i, k_ in enumerate(ks):
        b.hit(j, k_, "ding" if i == len(ks) - 1 else "pop", 0.85 if i == len(ks) - 1 else 0.6, "第一句逐段出现")


screen11()


# ================================================================ 屏 12：一块冒着冷气的冰，父亲和小奥雷里亚诺伸手去摸
def screen12(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_ice = 0
    k_touch = kq(j, wp(16, 0, 0.6), 1)
    k_wow = nx(j, wp(16, 1, 0.4), k_touch)
    L.note("了不起", "奥雷里亚诺", "第二代 · 次子")
    IX, IY = cx + 40, cy + 200

    def scene(c, sc, T):
        tt, tw = tb(j, k_touch), tb(j, k_wow)
        touch = T >= tt
        JX, KX = cx - 330, cx + 380
        with at_pop(c, JX, GY, sc):
            jose(c, JX, GY, 1.0, mood="laugh" if T >= tw else "smile",
                 rh=(IX - 150, IY - 140) if touch else None)
        with at_pop(c, KX, GY, sc):
            draw_man(c, KX, GY, 0.62, "red", mood="o" if touch else "smile", lh=(IX + 150, IY - 120) if touch else None)
        name_tag(c, KX, GY - 320, "奥雷里亚诺", "#5E4128", 40, clamp01(sc), "第二代 · 次子")
        with at_pop(c, IX, IY, sc):
            ice_block(c, IX, IY, 260, 200, T)
        if T >= tw:
            sparkle(c, IX, IY - 260, T - tw, "#7FB2D9", 12, 80, 220)
            with K.at(c, cx, cy - 430, -2, C.slam_scale(T - tw)):
                chip(c, 0, 0, "了不起", BLUE_FILL, BLUE, 66)
        return None
    ev(j, k_ice, L.pop_fn(j, k_ice, scene), "ding", 0.7)
    b.hit(j, k_touch, "bongo_high", 0.75, "伸手摸冰")
    b.hit(j, k_wow, "kick", 0.85, "了不起的发明")


screen12()


# ================================================================ 屏 13：说回我们：小李满天想法气泡，小王扛着家里的担子；大字“三步”
def screen13(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_ideas = kq(j, wp(17, 0, 0.4), 0)
    k_load = nx(j, wp(17, 3, 0.3), k_ideas)
    k_three = nx(j, wp(18, 1, 0.4), k_load)
    L.note("想法", "担子", "三步")
    LX, WX = cx - 300, cx + 300

    def scene(c, kk, T):
        ti, tl, t3 = tb(j, k_ideas), tb(j, k_load), tb(j, k_three)
        g = pop_scale(T - ti)
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "smile")
        for q in range(5):
            sc = pop_scale(T - ti - q * 0.1)
            if sc <= 0:
                continue
            x, y = LX - 200 + (q % 3) * 180, cy - 180 - (q // 3) * 170 + 10 * math.sin(T * 2 + q)
            with K.at(c, x, y, 0, sc):
                c.drawOval(skia.Rect.MakeXYWH(-70, -46, 140, 92), K.paint("#FFFFFF"))
                c.drawOval(skia.Rect.MakeXYWH(-70, -46, 140, 92), wb.marker(BLUE, 5))
                c.drawCircle(0, -6, 18, K.paint(YELLOW))
        if T >= tl:
            s = pop_scale(T - tl)
            with at_pop(c, WX, GY, s):
                draw_wang(c, WX, GY, 0.95, mood="sad", lh=(WX - 80, GY - 400), rh=(WX + 80, GY - 400))
                box(c, WX, GY - 440, 300, 120, "#E7D6BA", "#8B6B43", 6, 12)
                K.text(c, "担子", WX, GY - 440, 50, "hand", INK)
        if T >= t3:
            with K.at(c, cx, cy + 40, -3, C.slam_scale(T - t3)):
                K.text(c, "三步", 0, 0, 150, "hand", RED)
        return None
    ev(j, k_ideas, scene, "pop", 0.7)
    b.hit(j, k_load, "tom", 0.75, "担子落在别人肩上")
    b.hit(j, k_three, "kick", 0.85, "三步")


screen13()


# ================================================================ 屏 14：第一步：新想法写进本子，日历翻过七天，还亮着的才动手
def screen14(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(19, 1, 0.4), 1)
    k_week = nx(j, wp(19, 2, 0.4), k_book)
    k_go = nx(j, wp(19, 3, 0.4), k_week)
    L.note("想法本", "一星期", "动手")

    def scene(c, kk, T):
        tbk, tw, tg = tb(j, k_book), tb(j, k_week), tb(j, k_go)
        g = pop_scale(T - tbk)
        if g <= 0:
            return None
        with K.at(c, cx - 250, cy - 80, -4, g):
            box(c, 0, 0, 380, 460, "#FFFFFF", BLACK, 7, 14)
            K.text(c, "想法本", 0, -170, 54, "hand", BLUE)
            for q in range(4):
                C.line(c, (-140, -80 + q * 70), (140 - (q % 2) * 50, -80 + q * 70), GRAY, 5)
            if T >= tg:
                c.drawCircle(-150, -10, 16, K.paint(GREEN))
        if T >= tw:
            CX = cx + 260
            K.text(c, "一星期", CX, cy - 320, 54, "hand", INK, clamp01((T - tw) / 0.3))
            for q in range(7):
                x, y = CX - 150 + (q % 4) * 100, cy - 200 + (q // 4) * 100
                box(c, x, y, 84, 84, "#FFFFFF", GRAY, 4, 8)
                if T >= tw + q * 0.1:
                    C.line(c, (x - 26, y - 26), (x + 26, y + 26), RED, 6)
        if T >= tg:
            with K.at(c, cx + 260, cy + 220, 0, C.slam_scale(T - tg)):
                chip(c, 0, 0, "还想做 → 动手", GREEN_FILL, GREEN, 50)
            bp = C.bulb_path(cx + 260, cy + 60, 50)
            c.drawPath(bp, K.paint(NOTE_FILL))
            c.drawPath(bp, wb.marker(ORANGE, 6))
            sparkle(c, cx + 260, cy + 50, T - tg, YELLOW, 8, 60, 130)
        with at_pop(c, cx - 250, cy + 520, g):
            draw_li(c, cx - 250, cy + 520, 0.75, "smile" if T >= tg else "flat")
        return None
    L.note("还想做 → 动手")
    ev(j, k_book, scene, "wood_high", 0.7)
    b.hit(j, k_week, "shaker", 0.7, "放一个星期")
    b.hit(j, k_go, "ding", 0.8, "还想做再动手")


screen14()


# ================================================================ 屏 15：第二步：只留一件事，进度条一格格涨满，弹出“小结果”
def screen15(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    k_cards = kq(j, wp(20, 0, 0.6), 1)
    k_one = nx(j, wp(20, 1, 0.4), k_cards)
    k_fill = nx(j, wp(20, 2, 0.5), k_one)
    k_res = nx(j, wp(20, 3, 0.2), k_fill)
    CARDS = ["剪视频", "副业", "健身"]
    L.note(*CARDS, "小结果", "30天剪出一条视频")

    def scene(c, kk, T):
        tc, to, tf, tr = (tb(j, k) for k in (k_cards, k_one, k_fill, k_res))
        for i, s in enumerate(CARDS):
            g = pop_scale(T - tc - i * 0.1)
            if g <= 0:
                continue
            x0, y0 = cx - 360 + i * 360, cy - 200
            if i and T >= to:
                f = ease_in_out(clamp01((T - to) / 0.4))
                x0 += f * (300 if i == 2 else 600)
                g *= 1 - f
                if g <= 0:
                    continue
            if i == 0 and T >= to:
                x0 = lerp(x0, cx, ease_in_out(clamp01((T - to) / 0.4)))
            with K.at(c, x0, y0, 0, g):
                box(c, 0, 0, 300, 150, "#FFFFFF", BLUE, 6, 14)
                K.text(c, s, 0, 0, 56, "hand", BLUE)
        if T >= tf:
            progress(c, cx, cy + 60, 760, ease_out(clamp01((T - tf) / 1.0)), GREEN, 1, 44)
        if T >= tr:
            with K.at(c, cx, cy + 260, -2, C.slam_scale(T - tr)):
                chip(c, 0, 0, "小结果", NOTE_FILL, ORANGE, 66)
            K.text(c, "30天剪出一条视频", cx, cy + 420, 50, "hand", INK, clamp01((T - tr - 0.2) / 0.3))
        return None
    ev(j, k_cards, scene, "pop", 0.7)
    b.hit(j, k_one, "shaker", 0.7, "只留一件")
    b.hit(j, k_fill, "wood_high", 0.65, "进度涨起来")
    b.hit(j, k_res, "ding", 0.85, "看得见的小结果")


screen15()


# ================================================================ 屏 16：第三步：每周清单，做不下去的一条条划掉
def screen16(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    k_list = kq(j, wp(21, 0, 0.5), 1)
    k_look = nx(j, wp(21, 1, 0.4), k_list)
    k_cut = nx(j, wp(21, 2, 0.5), k_look)
    k_free = nx(j, wp(21, 3, 0.4), k_cut)
    ITEMS = ["剪视频", "学日语", "开网店", "健身"]
    L.note("每周", *ITEMS, "轻了")

    def scene(c, kk, T):
        tl, tlk, tc, tf = (tb(j, k) for k in (k_list, k_look, k_cut, k_free))
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with K.at(c, cx - 60, cy - 20, 0, g):
            box(c, 0, 0, 640, 620, "#FFFFFF", BLACK, 7, 14)
            K.text(c, "每周", 0, -240, 58, "hand", RED)
            for i, s in enumerate(ITEMS):
                y = -120 + i * 110
                c.drawRect(skia.Rect.MakeXYWH(-250, y - 24, 48, 48), wb.marker(BLACK, 5))
                K.text(c, s, -170, y, 52, "hand", INK, 1, "left")
                if i in (1, 2) and T >= tc + (i - 1) * 0.25:
                    f = ease_out(clamp01((T - tc - (i - 1) * 0.25) / 0.25))
                    C.line(c, (-180, y), (lerp(-180, 120, f), y), RED, 9)
                if i == 0 and T >= tlk:
                    c.drawPath(wb.check(-226, y, 40), wb.marker(GREEN, 8))
        if T >= tlk:
            with at_pop(c, cx + 400, cy + 520, pop_scale(T - tlk)):
                draw_li(c, cx + 400, cy + 520, 0.8, "smile" if T >= tf else "flat")
        if T >= tf:
            with K.at(c, cx + 360, cy - 360, 4, C.slam_scale(T - tf)):
                chip(c, 0, 0, "轻了", GREEN_FILL, GREEN, 60)
        return None
    ev(j, k_list, scene, "wood_high", 0.7)
    b.hit(j, k_look, "pop", 0.65, "看一眼手头")
    b.hit(j, k_cut, "rim", 0.8, "划掉")
    b.hit(j, k_free, "ding", 0.75, "别一直挂着")


screen16()


# ================================================================ 屏 17：好处：一个想法气泡落到地上，长成一棵杏仁树
def screen17(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_fall = kq(j, wp(22, 0, 0.4), 0)
    k_tree = nx(j, wp(22, 1, 0.4), k_fall)
    L.note("落地")

    def scene(c, kk, T):
        tf, tt = tb(j, k_fall), tb(j, k_tree)
        if T < tf:
            return None
        C.line(c, (cx - 560, GY + 6), (cx + 560, GY + 6), "#8B6B43", 8)
        TX = cx + 120
        if T < tt:
            f = ease_in_out(clamp01((T - tf) / 0.8))
            y = lerp(cy - 520, GY - 40, f)
            c.drawOval(skia.Rect.MakeXYWH(TX - 70, y - 46, 140, 92), K.paint("#FFFFFF"))
            c.drawOval(skia.Rect.MakeXYWH(TX - 70, y - 46, 140, 92), wb.marker(BLUE, 5))
            c.drawCircle(TX, y - 6, 18, K.paint(YELLOW))
        else:
            g = ease_out(clamp01((T - tt) / 0.8))
            almond_tree(c, TX, GY, 1.6 * max(0.05, g))
            for q in range(3):
                butterfly(c, TX - 200 + q * 180, cy - 260 - 40 * math.sin(T * 1.5 + q), 0.7, T + q, clamp01((T - tt - 0.4) / 0.4))
            K.text(c, "落地", cx - 330, cy - 300, 80, "hand", GREEN, g)
        with at_pop(c, cx - 380, GY, 1):
            draw_li(c, cx - 380, GY, 0.9, "smile" if T >= tt else "flat")
        return None
    ev(j, k_fall, scene, "wood_low", 0.65)
    b.hit(j, k_tree, "ding", 0.85, "长成一棵树")


screen17()


# ================================================================ 屏 18：评论区；小李眼里的光照在一件事上；下一讲预告
def enc(c, T, te, th, cx, cy):
    g = pop_scale(T - te)
    LX, LY = cx - 300, cy + 640
    with at_pop(c, LX, LY, g):
        draw_li(c, LX, LY, 0.85, "smile")
    if T >= th:
        f = ease_out(clamp01((T - th) / 0.4))
        hy = LY - 290 * 0.85
        c.drawPath(P((LX + 30, hy), (lerp(LX + 30, cx + 220, f), lerp(hy, cy + 420, f))), wb.marker(YELLOW, 22, 0.7))
        with K.at(c, cx + 260, cy + 430, 0, pop_scale(T - th)):
            box(c, 0, 0, 260, 140, NOTE_FILL, ORANGE, 6, 14)
            K.text(c, "一件事", 0, 0, 54, "hand", RED)
        sparkle(c, cx + 260, cy + 430, T - th, YELLOW, 10, 90, 200)


def sticky_icon(c, x, y, dt):
    for q in range(3):
        with K.at(c, x - 40 + q * 40, y - 30 + q * 20, (q - 1) * 8, pop_scale(dt - q * 0.1)):
            box(c, 0, 0, 90, 90, NOTE_FILL, ORANGE, 4, 6)


KT.ending(16, "哪件事还没做完？", ["剪视频", "健身", "读书"], 24, 25, enc, 26, ["忙到最后", "为什么什么都记不住？"],
          enc_piece=2, next_icon=sticky_icon)
L.note("一件事")

# ================================================================ 收尾
L.finish(cover_shot=10, square_shot=4, notes=NOTES)
L.export(globals())
