"""《百年孤独》04 粉笔圈：身边全是人，为什么还是很孤单？（白板手绘 + AI 旁白，竖屏 2:3）

比喻贯穿：一个粉笔圈。奥雷里亚诺上校三十二次起义全败、九死一生，权势最大时让副官在他周围画粉笔圈，谁也不准进来；
老了关在作坊里做小金鱼，攒到二十五条就熔掉重做。今天的我们也常给自己画圈，落到“擦掉一段圈”的三件小事。
文案见 bainian/PLAN.md「### 04」。
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
                            at_pop, box, bubble_box, chip, colonel, draw_lady, draw_li, draw_man, draw_wang, name_tag, phone,
                            pop_scale, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "生活里", 1),
    ([2], "生活里", 2),
    ([3, 4], "书里的人", 3),
    ([5], "九死一生", 4),
    ([6, 7, 8], "粉笔圈", 5),
    ([9], "粉笔圈", 6),
    ([10, 11], "小金鱼", 7),
    ([12], "小金鱼", 8),
    ([13, 14], "说回我们", 9),
    ([15], "说回我们", 10),
    ([16], "第一件", 11),
    ([17], "第二件", 12),
    ([18], "第三件", 13),
    ([19], "好处", 14),
    ([20, 21, 22, 23], "评论区见", 15),
]

THEME = BT.get("04")
L = N.Lesson("04", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME,
             trim_head={21: 0.15})       # 第 21 句句首碎音（上一句“候”的尾音，识别成“后”），裁掉
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(14)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》（范晔译本）奥雷里亚诺·布恩迪亚上校的几章。情节为转述，不引原文。",
    "今人（小李、小王）为虚构示意；书中人造型为示意（一百多年前的加勒比小镇打扮）。",
]

COL = ("奥雷里亚诺上校", "第二代 · 次子")
GOLD, GOLD_LINE = "#F2C230", "#9C7A1A"


def tag(c, x, y, who, a=1.0, size=44):
    name_tag(c, x, y, who[0], "#2F5B8E", size, a, who[1])


def chalk_ring(c, x, y, rx, ry, f=1.0, a=1.0, gaps=()):
    """粉笔圈（椭圆，地面透视；黑板底上黑线换成粉笔白），f 为画出的比例；gaps 为擦掉的角度区间 [(a0, a1)]（度）。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry), 0, 359.9 * f)
    if not gaps:
        c.drawPath(p, wb.marker(BLACK, 10, 0.9 * a))
        return
    start = 0.0
    for g0, g1 in sorted(gaps) + [(360, 360)]:
        if g0 > start:
            seg = skia.Path()
            seg.addArc(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry), start, min(g0, 360 * f) - start)
            c.drawPath(seg, wb.marker(BLACK, 10, 0.9 * a))
        start = g1


def goldfish(c, x, y, s=1.0, a=1.0, rot=0.0):
    with K.at(c, x, y, rot, s):
        body = skia.Path()
        body.addOval(skia.Rect.MakeXYWH(-40, -22, 80, 44))
        c.drawPath(body, K.paint(GOLD, a))
        c.drawPath(body, wb.marker(GOLD_LINE, 4, a))
        tail = P((36, 0), (66, -24), (60, 0), (66, 24), close=True)
        c.drawPath(tail, K.paint(GOLD, a))
        c.drawPath(tail, wb.marker(GOLD_LINE, 4, a))
        c.drawCircle(-22, -4, 5, K.paint(INK, a))


def crowd(c, cx, GY, n, a=1.0, s=0.62, spread=520):
    cols = ("white", "ochre", "green", "red", "gray", "blue")
    for i in range(n):
        x = cx - spread + i * (2 * spread / max(1, n - 1))
        if i % 2:
            draw_lady(c, x, GY - (i % 3) * 14, s, cols[i % 6], hair="bun", mood="smile", alpha=a)
        else:
            draw_man(c, x, GY - (i % 3) * 14, s, cols[i % 6], hat="straw" if i % 4 == 0 else None, mood="smile", alpha=a)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：通讯录一路滑到底；饭桌上三个人各低头看手机
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_ph = kq(j, wp(0, 1, 0.3), 0)
    k_scroll = nx(j, wp(0, 2, 0.4), k_ph)
    k_none = nx(j, wp(0, 4, 0.3), k_scroll)
    k_table = nx(j, wp(1, 1, 0.3), k_none)
    k_heads = nx(j, wp(1, 2, 0.3), k_table)
    L.note("几百人", "？")

    def scene(c, kk, T):
        tp, ts, tn, tt, th = (tb(j, k) for k in (k_ph, k_scroll, k_none, k_table, k_heads))
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        if T < tt:
            with K.at(c, cx, cy - 60, 0, g):
                box(c, 0, 0, 520, 820, "#FFFFFF", BLACK, 8, 40)
                c.save()
                c.clipRect(skia.Rect.MakeXYWH(-240, -340, 480, 680))
                off = min(1.0, max(0.0, T - ts) / 1.0) * 1600
                for q in range(24):
                    y = -300 + q * 90 - off
                    c.drawCircle(-180, y, 28, K.paint(BLUE_FILL))
                    C.line(c, (-130, y), (100 - (q % 3) * 40, y), GRAY, 10)
                c.restore()
                K.text(c, "几百人", 0, -370, 44, "sans_medium", INK)
            if T >= tn:
                with K.at(c, cx + 330, cy - 300, 0, C.slam_scale(T - tn)):
                    K.text(c, "？", 0, 0, 160, "hand", RED)
            return None
        f = pop_scale(T - tt)
        with K.at(c, cx, GY - 150, 0, f):
            box(c, 0, 0, 900, 30, "#E7D6BA", "#8B6B43", 6, 6)
            for sg in (-1, 1):
                C.line(c, (sg * 400, 15), (sg * 400, 150), "#8B6B43", 9)
        for i, (x, who) in enumerate(((cx - 300, "li"), (cx, "wang"), (cx + 300, "man"))):
            s_ = pop_scale(T - tt - 0.1 * i)
            if s_ <= 0:
                continue
            down = T >= th
            hy = GY - 290 * 0.85
            with at_pop(c, x, GY, s_):
                if who == "li":
                    draw_li(c, x, GY, 0.85, "flat", rh=(x + 40, hy + 120))
                elif who == "wang":
                    draw_wang(c, x, GY, 0.85, mood="flat", rh=(x + 40, hy + 120), head_dx=0)
                else:
                    draw_man(c, x, GY, 0.85, "blue", mood="flat", rh=(x + 40, hy + 120))
                phone(c, x + 40, hy + 110, 0.45)
            if down:
                c.drawPath(P((x + 10, hy + 40), (x + 40, hy + 90)), wb.marker(BLUE, 4, 0.6))
        return None
    ev(j, k_ph, scene, "pop", 0.7)
    b.hit(j, k_scroll, "shaker", 0.7, "通讯录往下翻")
    b.hit(j, k_none, "rim", 0.8, "找不到人")
    b.hit(j, k_table, "wood_low", 0.65, "下班回家")
    b.hit(j, k_heads, "wood_high", 0.6, "各刷各的手机")


screen1()


# ================================================================ 屏 2（drop）：人群中间的小李，心口是个空洞
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_crowd = kq(j, wp(2, 0, 0.3), 0)
    L.note("空的")

    def scene(c, kk, T):
        tc, td = tb(j, k_crowd), tb(j, dk)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        for i in range(6):
            x = cx - 520 + i * 208
            if abs(x - cx) < 120:
                continue
            (draw_wang if i % 2 else draw_li)(c, x, GY - 20, 0.7, alpha=0.55 * g)
        with at_pop(c, cx, GY, g):
            draw_li(c, cx, GY, 1.0, "flat" if T < td else "sad")
        if T >= td:
            hy = GY - 290
            r = 40 * ease_out(clamp01((T - td) / 0.3))
            c.drawCircle(cx, hy + 140, r, K.paint("#1B1B1F"))
            c.drawCircle(cx, hy + 140, r, wb.marker(GRAY, 4))
            with K.at(c, cx + 280, cy - 260, -4, C.slam_scale(T - td)):
                chip(c, 0, 0, "空的", "#D9DCE1", GRAY, 70)
        return None
    ev(j, k_crowd, scene, "shaker", 0.65)
    b.hit(j, dk, "kick", 0.9, "心里还是空的")
    b.shots[j].shake = [(dk, 9.0)]
    b.shots[j].flashes = [(dk, 0.2)]


screen2()


# ================================================================ 屏 3：绿皮书翻开；上校出场；三十二面小旗一面面倒下
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(3, 0, 0.4), 0)
    k_col = nx(j, wp(3, 2, 0.2), k_book)
    k_flags = nx(j, wp(4, 1, 0.3), k_col)
    k_fail = nx(j, wp(4, 2, 0.3), k_flags)
    KT.book(j, k_book, x=cx - 360, y=cy - 300)
    L.note(*COL, "32", "失败")
    PX = cx - 330

    def scene(c, kk, T):
        tc, tf, tfl = tb(j, k_col), tb(j, k_flags), tb(j, k_fail)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with at_pop(c, PX, GY, g):
            colonel(c, PX, GY, 1.0, mood="flat" if T < tfl else "sad")
        tag(c, PX + 60, GY - 470, COL, clamp01(g), 42)
        if T >= tf:
            for i in range(32):
                r_, q = divmod(i, 8)
                x, y = cx - 40 + q * 72, cy - 120 + r_ * 130
                t0 = tf + i * 0.025
                if T < t0:
                    continue
                fall = ease_in_out(clamp01((T - tfl - (31 - i) * 0.012) / 0.3)) if T >= tfl else 0
                with K.at(c, x, y + 50, -80 * fall, 1):
                    C.line(c, (0, 0), (0, -90), "#8A6A3A", 5)
                    c.drawPath(P((0, -90), (44, -76), (0, -60), close=True), K.paint(RED if fall < 0.5 else GRAY))
            K.text(c, "32", cx + 230, cy - 260, 110, "hand", RED, clamp01((T - tf) / 0.3))
        if T >= tfl:
            with K.at(c, cx + 240, cy + 420, -3, C.slam_scale(T - tfl)):
                chip(c, 0, 0, "失败", "#D9DCE1", GRAY, 60)
        return None
    ev(j, k_col, scene, "tom", 0.75)
    b.hit(j, k_flags, "shaker", 0.7, "三十二次起义")
    b.hit(j, k_fail, "rim", 0.8, "全都失败")


screen3()


# ================================================================ 屏 4：三个数字逐个砸下：14 暗杀、73 埋伏、1 枪决
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    ks = [kq(j, wp(5, 1, 0.3), 0)]
    ks.append(nx(j, wp(5, 2, 0.3), ks[0]))
    ks.append(nx(j, wp(5, 3, 0.4), ks[1]))
    NUM = [("14", "暗杀"), ("73", "埋伏"), ("1", "枪决")]
    L.note(*(n for n, _ in NUM), *(w for _, w in NUM))

    def scene(c, kk, T):
        for i, (k_, (n, w)) in enumerate(zip(ks, NUM)):
            t0 = tb(j, k_)
            if T < t0:
                continue
            x = cx - 340 + i * 340
            with K.at(c, x, cy - 220, 0, C.slam_scale(T - t0)):
                K.text(c, n, 0, 0, 200, "hand", RED)
                K.text(c, w, 0, 150, 66, "hand", INK)
        g = pop_scale(T - tb(j, ks[0]))
        if g > 0:
            with at_pop(c, cx, GY, g):
                colonel(c, cx, GY, 0.9, mood="flat")
        return None
    ev(j, ks[0], scene, "kick", 0.8)
    b.hit(j, ks[1], "kick", 0.8, "七十三次埋伏")
    b.hit(j, ks[2], "tom", 0.9, "一次枪决")


screen4()


# ================================================================ 屏 5：人越围越多；副官画粉笔圈，圈里只有上校，人群被挡在外面
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 470
    k_crowd = kq(j, wp(6, 1, 0.3), 0)
    k_order = nx(j, wp(7, 0, 0.5), k_crowd)
    k_draw = nx(j, wp(7, 3, 0.2), k_order)
    k_out = nx(j, wp(8, 1, 0.3), k_draw)
    L.note("不准进来")

    def scene(c, kk, T):
        tc, to, td, tou = (tb(j, k) for k in (k_crowd, k_order, k_draw, k_out))
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        push = ease_out(clamp01((T - tou) / 0.5)) if T >= tou else 0
        n = 8
        for i in range(n):
            ang = math.pi * (0.1 + 0.8 * i / (n - 1))
            r = lerp(300, 470, push)
            x = cx - math.cos(ang) * r * 1.15
            y = GY - 60 - math.sin(ang) * 60
            s_ = pop_scale(T - tc - 0.06 * i)
            if s_ > 0:
                with at_pop(c, x, y, s_):
                    (draw_lady if i % 2 else draw_man)(c, x, y, 0.55, ("white", "ochre", "green", "red")[i % 4],
                                                       mood="o" if push > 0.5 else "smile")
        if T >= td:
            f = ease_out(clamp01((T - td) / 0.8))
            chalk_ring(c, cx, GY + 10, 260, 80, f)
            AX = cx + 330 - 200 * f
            with at_pop(c, AX, GY + 60, pop_scale(T - td)):
                draw_man(c, AX, GY + 60, 0.6, "blue", hat="kepi", rh=(AX - 80, GY + 50))
        with at_pop(c, cx, GY, g):
            colonel(c, cx, GY, 0.95, mood="flat")
        if T >= to:
            with K.at(c, cx, cy - 420, 0, pop_scale(T - to)):
                box(c, 0, 0, 300, 100, N.PARCH, N.PARCH_LINE, 5, 8)
                K.text(c, "命令", 0, 2, 56, "serif_black", RED)
        if T >= tou:
            with K.at(c, cx + 300, cy - 230, 4, C.slam_scale(T - tou)):
                chip(c, 0, 0, "不准进来", RED_FILL, RED, 54)
        return None
    L.note("命令")
    ev(j, k_crowd, scene, "clap", 0.7)
    b.hit(j, k_order, "bongo_low", 0.75, "下了一道命令")
    b.hit(j, k_draw, "shaker", 0.8, "画粉笔圈")
    b.hit(j, k_out, "kick", 0.85, "谁也不准进来")


screen5()


# ================================================================ 屏 6：圈外的人张嘴说话，气泡碰到粉笔线就碎了
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 470
    k_say = kq(j, wp(9, 0, 0.5), 0)
    k_break = nx(j, wp(9, 2, 0.4), k_say)
    L.note("心里话", "说了算")

    def scene(c, kk, T):
        ts, tbk = tb(j, k_say), tb(j, k_break)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        chalk_ring(c, cx, GY + 10, 260, 80)
        with at_pop(c, cx, GY, 1):
            colonel(c, cx, GY, 0.95, mood="flat")
        with K.at(c, cx, cy - 380, 0, g):
            chip(c, 0, 0, "说了算", NOTE_FILL, ORANGE, 52)
        for i, sg in enumerate((-1, 1)):
            x = cx + sg * 430
            draw_lady(c, x, GY, 0.7, "yellow", hair="bun", mood="smile") if i else draw_man(c, x, GY, 0.7, "white", hat="straw", mood="smile")
            f = clamp01((T - ts - 0.2) / 0.8)
            bx = lerp(x - sg * 40, cx + sg * 270, f)
            by = cy - 60
            if T < tbk:
                with K.at(c, bx, by, 0, pop_scale(T - ts - 0.2)):
                    bubble_box(c, 0, 0, 200, 90, sg)
                    K.text(c, "心里话", 0, 0, 40, "hand", INK)
            else:
                dt = T - tbk
                for q in range(5):
                    a = q * 1.3 + i
                    dx, dy = math.cos(a) * 160 * dt, math.sin(a) * 160 * dt + 300 * dt * dt
                    c.drawRect(skia.Rect.MakeXYWH(cx + sg * 270 + dx - 18, by + dy - 18, 36, 36),
                               K.paint("#FFFFFF", max(0.0, 1 - dt / 0.8)))
        return None
    ev(j, k_say, scene, "pop", 0.65)
    b.hit(j, k_break, "rim", 0.85, "气泡碎了")


screen6()


# ================================================================ 屏 7：作坊里，金鱼一条条排开，数到 25，全倒进坩埚熔掉
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_shop = kq(j, wp(10, 1, 0.4), 0)
    k_fish = nx(j, wp(10, 2, 0.3), k_shop)
    k_25 = nx(j, wp(11, 1, 0.5), k_fish)
    k_melt = nx(j, wp(11, 2, 0.4), k_25)
    L.note("25", "熔掉", "一天两条")

    def scene(c, kk, T):
        ts, tf, t25, tm = (tb(j, k) for k in (k_shop, k_fish, k_25, k_melt))
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        with at_pop(c, cx - 360, GY, g):
            colonel(c, cx - 360, GY, 0.85, mood="flat", hat=None, rh=(cx - 240, GY - 240))
        with K.at(c, cx + 60, GY - 170, 0, g):
            box(c, 0, 0, 760, 28, "#E7D6BA", "#8B6B43", 6, 6)
        if T >= tf:
            n = 25 if T >= t25 else min(24, 2 + int((T - tf) / max(0.05, (t25 - tf) / 22)))
            melt = ease_in_out(clamp01((T - tm) / 0.6)) if T >= tm else 0
            for i in range(n):
                r_, q = divmod(i, 5)
                x0, y0 = cx - 110 + q * 110, cy - 300 + r_ * 70
                x, y = lerp(x0, cx + 360, melt), lerp(y0, GY - 300, melt)
                goldfish(c, x, y, 0.9 * (1 - 0.7 * melt), 1 - melt * 0.8)
            K.text(c, "一天两条", cx - 260, cy - 420, 48, "hand", INK, clamp01((T - tf) / 0.3))
            if T >= t25:
                with K.at(c, cx + 400, cy - 420, 0, C.slam_scale(T - t25)):
                    K.text(c, "25", 0, 0, 120, "hand", RED)
        if T >= tm:
            PX, PY = cx + 360, GY - 260
            with K.at(c, PX, PY, 0, pop_scale(T - tm)):
                pot = P((-110, -60), (110, -60), (80, 80), (-80, 80), close=True)
                c.drawPath(pot, K.paint("#5E5E58"))
                c.drawPath(pot, wb.marker(INK, 6))
                c.drawOval(skia.Rect.MakeXYWH(-100, -76, 200, 36), K.paint(ORANGE))
                for q in range(3):
                    fh = 40 + 20 * math.sin((T - tm) * 9 + q)
                    c.drawPath(P((-60 + q * 60, 90), (-40 + q * 60, 90 + fh), (-20 + q * 60, 90), close=True), K.paint(RED))
            K.text(c, "熔掉", PX, PY + 220, 60, "hand", RED, clamp01((T - tm - 0.3) / 0.3))
        return None
    ev(j, k_shop, scene, "wood_low", 0.6)
    b.hit(j, k_fish, "pop", 0.7, "做小金鱼")
    b.hit(j, k_25, "ding", 0.8, "攒到二十五条")
    b.hit(j, k_melt, "tom", 0.85, "全部熔掉")


screen7()


# ================================================================ 屏 8：金鱼又从头一条条做起，循环箭头
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    k_loop = kq(j, wp(12, 0, 0.4), 0)
    k_heart = nx(j, wp(12, 2, 0.4), k_loop)
    L.note("忙", "别的事")

    def scene(c, kk, T):
        tl, th = tb(j, k_loop), tb(j, k_heart)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        R0 = 300
        ang = (T - tl) * 2.2
        ring = skia.Path()
        ring.addArc(skia.Rect.MakeXYWH(cx - R0, cy - 80 - R0, 2 * R0, 2 * R0), 0, 300)
        c.drawPath(ring, wb.marker(ORANGE, 12, g))
        c.drawPath(P((cx + R0 * math.cos(math.radians(300)) - 30, cy - 80 + R0 * math.sin(math.radians(300)) - 20),
                     (cx + R0 * math.cos(math.radians(300)), cy - 80 + R0 * math.sin(math.radians(300))),
                     (cx + R0 * math.cos(math.radians(300)) - 40, cy - 80 + R0 * math.sin(math.radians(300)) + 24)),
                   wb.marker(ORANGE, 12, g))
        for q in range(5):
            a = ang + q * 2 * math.pi / 5
            goldfish(c, cx + R0 * math.cos(a), cy - 80 + R0 * math.sin(a), 0.9, g, math.degrees(a) + 90)
        K.text(c, "忙", cx, cy - 80, 120, "hand", RED, g)
        if T >= th:
            with K.at(c, cx + 300, cy + 380, 0, pop_scale(T - th)):
                c.drawPath(C.heart_path(0, 0, 60), wb.marker(GRAY, 6))
                K.text(c, "别的事", 0, 120, 50, "hand", GRAY)
            C.line(c, (cx + 200, cy + 300), (cx + 400, cy + 460), RED, 8)
        return None
    ev(j, k_loop, scene, "shaker", 0.7)
    b.hit(j, k_heart, "rim", 0.75, "不去碰别的事")


screen8()


# ================================================================ 屏 9：小李脚下也出现一个圈，圈边写着“忙”“冷脸”“还好”
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 470
    k_li = kq(j, wp(13, 0, 0.4), 0)
    k_ring = nx(j, wp(13, 2, 0.3), k_li)
    k_w = [nx(j, wp(14, 0, 0.3), k_ring)]
    k_w.append(nx(j, wp(14, 1, 0.4), k_w[0]))
    k_out = nx(j, wp(14, 3, 0.3), k_w[1])
    WORDS = [("忙", cx - 360, GY - 40), ("冷脸", cx, GY + 140), ("还好", cx + 360, GY - 40)]
    L.note(*(w for w, _, _ in WORDS), "圈外")

    def scene(c, kk, T):
        tl, tr, to = tb(j, k_li), tb(j, k_ring), tb(j, k_out)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        if T >= tr:
            chalk_ring(c, cx, GY + 10, 300, 90, ease_out(clamp01((T - tr) / 0.8)))
        with at_pop(c, cx, GY, g):
            draw_li(c, cx, GY, 1.0, "flat")
        for i, (w, x, y) in enumerate(WORDS):
            t0 = tb(j, k_w[0]) if i < 2 else tb(j, k_w[1])
            t0 += 0.15 * (i % 2)
            if T >= t0:
                K.text(c, w, x, y, 56, "hand", ORANGE, clamp01((T - t0) / 0.25))
        if T >= to:
            for sg in (-1, 1):
                x = cx + sg * 450
                with at_pop(c, x, cy - 60, pop_scale(T - to)):
                    draw_wang(c, x, cy - 60, 0.6, mood="flat") if sg < 0 else draw_man(c, x, cy - 60, 0.6, "white", mood="flat")
            with K.at(c, cx, cy - 400, 0, C.slam_scale(T - to)):
                chip(c, 0, 0, "圈外", "#D9DCE1", GRAY, 60)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_ring, "shaker", 0.75, "脚下也有圈")
    for k_ in k_w:
        b.hit(j, k_, "pop", 0.65, "画圈的东西")
    b.hit(j, k_out, "rim", 0.8, "把人挡在圈外")


screen9()


# ================================================================ 屏 10：一块黑板擦伸过来；大字“三件小事”
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 470
    k_er = kq(j, wp(15, 0, 0.5), 0)
    k_three = nx(j, wp(15, 1, 0.5), k_er)
    L.note("三件小事")

    def scene(c, kk, T):
        te, t3 = tb(j, k_er), tb(j, k_three)
        g = pop_scale(T - te)
        if g <= 0:
            return None
        f = ease_in_out(clamp01((T - te) / 0.8))
        chalk_ring(c, cx, GY + 10, 300, 90, 1, 1, gaps=[(20, 20 + 70 * f)])
        draw_li(c, cx, GY, 1.0, "smile" if f > 0.8 else "flat")
        a = math.radians(20 + 70 * f)
        ex, ey = cx + 300 * math.cos(a), GY + 10 + 90 * math.sin(a)
        with K.at(c, ex, ey - 30, -20, g):
            box(c, 0, 0, 160, 70, "#C9A46A", "#6E4E22", 6, 10)
            c.drawRect(skia.Rect.MakeXYWH(-80, 10, 160, 25), K.paint("#4A4A4A"))
        if T >= t3:
            with K.at(c, cx, cy - 250, -3, C.slam_scale(T - t3)):
                K.text(c, "三件小事", 0, 0, 130, "hand", RED)
        return None
    ev(j, k_er, scene, "shaker", 0.75)
    b.hit(j, k_three, "kick", 0.85, "三件小事")


screen10()


# ================================================================ 屏 11：第一件：小李对小王说“周末我去爬山了”，两人笑
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_pair = kq(j, wp(16, 0, 0.6), 1)
    k_say = nx(j, wp(16, 1, 0.5), k_pair)
    k_true = nx(j, wp(16, 2, 0.5), k_say)
    L.note("周末我去爬山了", "真事", "工作")

    def scene(c, kk, T):
        tp, ts, tt = tb(j, k_pair), tb(j, k_say), tb(j, k_true)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        LX, WX = cx - 250, cx + 250
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "smile" if T >= ts else "flat")
        with at_pop(c, WX, GY, g):
            draw_wang(c, WX, GY, 0.95, mood="smile" if T >= tt else "flat")
        if T >= ts:
            with K.at(c, cx - 80, cy - 220, 0, pop_scale(T - ts)):
                bubble_box(c, 0, 0, 520, 130, -1)
                K.text(c, "周末我去爬山了", 0, 0, 52, "hand", INK)
            with K.at(c, cx + 360, cy - 440, 0, pop_scale(T - ts)):
                K.text(c, "工作", 0, 0, 50, "hand", GRAY)
                C.line(c, (-60, 0), (60, 0), RED, 8)
        if T >= tt:
            with K.at(c, cx, cy + 40, 0, C.slam_scale(T - tt)):
                chip(c, 0, 0, "真事", GREEN_FILL, GREEN, 60)
        return None
    ev(j, k_pair, scene, "wood_high", 0.65)
    b.hit(j, k_say, "pop", 0.75, "说一件真事")
    b.hit(j, k_true, "ding", 0.8, "跟工作无关")


screen11()


# ================================================================ 屏 12：第二件：日程表里空出一格，写着“空白”；金鱼图标被划掉
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    k_cal = kq(j, wp(17, 0, 0.6), 1)
    k_blank = nx(j, wp(17, 1, 0.5), k_cal)
    k_fish = nx(j, wp(17, 3, 0.3), k_blank)
    L.note("空白")

    def scene(c, kk, T):
        tc, tbl, tf = tb(j, k_cal), tb(j, k_blank), tb(j, k_fish)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx - 120, cy - 40, 0, g):
            box(c, 0, 0, 560, 720, "#FFFFFF", BLACK, 7, 14)
            for r in range(6):
                y = -270 + r * 105
                if r == 3 and T >= tbl:
                    K.text(c, "空白", 0, y, 64, "hand", GREEN, clamp01((T - tbl) / 0.3))
                    c.drawRoundRect(skia.Rect.MakeXYWH(-230, y - 42, 460, 84), 14, 14, wb.marker(GREEN, 5))
                else:
                    c.drawRoundRect(skia.Rect.MakeXYWH(-230, y - 36, 460, 72), 14, 14, K.paint(BLUE_FILL))
        if T >= tf:
            with K.at(c, cx + 350, cy + 300, 0, pop_scale(T - tf)):
                goldfish(c, 0, 0, 1.6)
                C.line(c, (-80, -60), (80, 60), RED, 10)
                C.line(c, (-80, 60), (80, -60), RED, 10)
        return None
    ev(j, k_cal, scene, "wood_high", 0.65)
    b.hit(j, k_blank, "ding", 0.8, "留点空白")
    b.hit(j, k_fish, "rim", 0.8, "别拿忙来躲")


screen12()


# ================================================================ 屏 13：第三件：小李跨进小王脚下的圈，耳朵放大，认真听
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 500
    k_step = kq(j, wp(18, 0, 0.6), 1)
    k_ask = nx(j, wp(18, 2, 0.4), k_step)
    k_ear = nx(j, wp(18, 3, 0.4), k_ask)
    L.note("你最近怎么样？", "听")

    def scene(c, kk, T):
        ts, ta, te = tb(j, k_step), tb(j, k_ask), tb(j, k_ear)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        WX = cx + 200
        chalk_ring(c, WX, GY + 10, 260, 80)
        with at_pop(c, WX + 60, GY, g):
            draw_wang(c, WX + 60, GY, 0.95, mood="smile" if T >= te else "flat")
        f = ease_in_out(clamp01((T - ts) / 0.8))
        LX = lerp(cx - 520, WX - 140, f)
        draw_li(c, LX, GY, 0.95, "smile")
        if T >= ta:
            with K.at(c, cx - 150, cy - 230, 0, pop_scale(T - ta)):
                bubble_box(c, 0, 0, 460, 120, 1)
                K.text(c, "你最近怎么样？", 0, 0, 50, "hand", INK)
        if T >= te:
            hy = GY - 290 * 0.95
            with K.at(c, LX - 50, hy, 0, 1 + 0.6 * pop_scale(T - te)):
                ear = skia.Path()
                ear.addArc(skia.Rect.MakeXYWH(-20, -26, 40, 52), 90, 180)
                c.drawPath(ear, wb.marker(RED, 6))
            K.text(c, "听", LX - 160, hy - 60, 70, "hand", RED, clamp01((T - te) / 0.3))
        return None
    ev(j, k_step, scene, "shaker", 0.65)
    b.hit(j, k_ask, "pop", 0.75, "问一句")
    b.hit(j, k_ear, "ding", 0.8, "认真听完")


screen13()


# ================================================================ 屏 14：好处：粉笔圈一段段被擦开，圈里圈外的人连成一片
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 470
    k_open = kq(j, wp(19, 0, 0.6), 0)
    k_join = nx(j, wp(19, 2, 0.4), k_open)
    k_talk = nx(j, wp(19, 2, 0.95), k_join)
    L.note("能说话的人")

    def scene(c, kk, T):
        to, tj, tt = tb(j, k_open), tb(j, k_join), tb(j, k_talk)
        f = ease_out(clamp01((T - to) / 0.8))
        chalk_ring(c, cx, GY + 10, 300, 90, 1, 1 - 0.7 * f, gaps=[(0, 60 * f), (120, 120 + 60 * f), (240, 240 + 60 * f)])
        draw_li(c, cx, GY, 0.9, "smile")
        u = ease_out(clamp01((T - tj) / 0.6)) if T >= tj else 0
        for i, sg in enumerate((-1, 1)):
            x = lerp(cx + sg * 500, cx + sg * 250, u)
            (draw_wang if i == 0 else draw_man)(c, x, GY, 0.85, **({"mood": "smile"} if i == 0 else {"color": "blue", "mood": "smile"}))
        if T >= tt:
            with K.at(c, cx, cy - 280, 0, C.slam_scale(T - tt)):
                chip(c, 0, 0, "能说话的人", GREEN_FILL, GREEN, 60)
            sparkle(c, cx, cy - 280, T - tt, YELLOW, 10, 120, 280)
        return None
    ev(j, k_open, scene, "shaker", 0.7)
    b.hit(j, k_join, "clap", 0.75, "人走近了")
    b.hit(j, k_talk, "ding", 0.85, "成了能说话的人")


screen14()


# ================================================================ 屏 15：评论区；两个人坐在长椅上说话；下一讲预告
def enc(c, T, te, th, cx, cy):
    y = cy + 620
    g = pop_scale(T - te)
    with K.at(c, cx, y - 110, 0, g):
        box(c, 0, 0, 520, 26, "#E7D6BA", "#8B6B43", 6, 6)
        for sg in (-1, 1):
            C.line(c, (sg * 220, 13), (sg * 220, 110), "#8B6B43", 8)
    with at_pop(c, cx - 140, y, g):
        draw_li(c, cx - 140, y, 0.8, "smile")
    with at_pop(c, cx + 140, y, g):
        draw_wang(c, cx + 140, y, 0.8, mood="smile")
    if T >= th:
        with K.at(c, cx, cy + 300, 0, pop_scale(T - th)):
            c.drawPath(C.heart_path(0, 0, 50), K.paint(RED_FILL))
            c.drawPath(C.heart_path(0, 0, 50), wb.marker(RED, 6))
        sparkle(c, cx, cy + 300, T - th, YELLOW, 10, 70, 180)


def stone_icon(c, x, y, dt):
    with K.at(c, x, y, 0, pop_scale(dt)):
        c.drawOval(skia.Rect.MakeXYWH(-70, -40, 140, 80), K.paint("#8A8F99"))
        c.drawOval(skia.Rect.MakeXYWH(-70, -40, 140, 80), wb.marker(BLACK, 5))


KT.ending(15, "上次说心里话是什么时候？", ["昨天", "上个月", "想不起来"], 21, 22, enc, 23, ["换了好几份工作", "为什么老在同一处摔跤？"],
          enc_piece=2, next_icon=stone_icon)

# ================================================================ 收尾
L.finish(cover_shot=5, square_shot=5, notes=NOTES)
L.export(globals())
