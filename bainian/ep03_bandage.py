"""《百年孤独》03 黑纱布：明明在乎，为什么总把人推开？（白板手绘 + AI 旁白，竖屏 2:3）

倒叙：先给结局——老年阿玛兰妲在廊下织自己的寿衣，手上缠着黑纱布；倒回去讲她和雷贝卡同时爱上意大利技师克雷斯皮，
他选了雷贝卡；后来克雷斯皮来求婚，她说死也不嫁；克雷斯皮死后她烫伤了手；多年后马尔克斯上校求婚，她还是拒绝。
落到“想推开时”的三个小动作。文案见 bainian/PLAN.md「### 03」。
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
                            amaranta, at_pop, box, bubble_box, chip, draw_lady, draw_li, draw_man, draw_wang, name_tag, phone,
                            pop_scale, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "生活里", 1),
    ([2], "生活里", 2),
    ([3, 4], "先看结局", 3),
    ([5, 6], "倒回去", 4),
    ([7], "倒回去", 5),
    ([8, 9], "求婚", 6),
    ([10, 11], "黑纱布", 7),
    ([12, 13], "又一次", 8),
    ([14], "推开的人", 9),
    ([15, 16], "说回我们", 10),
    ([17], "第一个", 11),
    ([18], "第二个", 12),
    ([19], "第三个", 13),
    ([20], "好处", 14),
    ([21, 22, 23, 24], "评论区见", 15),
]

THEME = BT.get("03")
L = N.Lesson("03", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(14)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》第 3–8 章、第 13 章（范晔译本）。情节为转述，不引原文。",
    "今人（小李、小王）为虚构示意；书中人造型为示意（一百多年前的加勒比小镇打扮）。",
]

AMA = ("阿玛兰妲", "第二代 · 女儿")
REB = ("雷贝卡", "养女")
CRE = ("克雷斯皮", "意大利技师")
GER = ("马尔克斯上校", "上校的战友")
TAGC = "#6B3F7A"


def tag(c, x, y, who, a=1.0, size=42, color=TAGC):
    name_tag(c, x, y, who[0], color, size, a, who[1])


def crespi(c, x, y, s, **kw):
    """皮埃特罗·克雷斯皮：小胡子、深蓝坎肩、白衬衫。"""
    kw.setdefault("beard", "mustache")
    draw_man(c, x, y, s, "white", vest="#3D4A63", **kw)


def gerineldo(c, x, y, s, **kw):
    """赫里内勒多·马尔克斯上校：绿军装、军帽。"""
    draw_man(c, x, y, s, "green", hat="kepi", **kw)


def heart(c, x, y, r, fill=RED_FILL, line=RED, a=1.0, broken=0.0):
    p = C.heart_path(x, y, r)
    if broken <= 0:
        c.drawPath(p, K.paint(fill, a))
        c.drawPath(p, wb.marker(line, 6, a))
        return
    for sg in (-1, 1):
        c.save()
        c.translate(sg * broken * 30, broken * 20)
        c.rotate(sg * broken * 12, x, y)
        c.clipRect(skia.Rect.MakeLTRB(x - r * 2 if sg < 0 else x, y - r * 2, x if sg < 0 else x + r * 2, y + r * 2))
        c.drawPath(p, K.paint(fill, a))
        c.drawPath(p, wb.marker(line, 6, a))
        c.restore()


def cloth(c, x, y, w, h, a=1.0):
    """白布（寿衣），下摆垂到地上。"""
    p = P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2 + 20, y + h / 2), (x - w / 2 - 20, y + h / 2), close=True)
    c.drawPath(p, K.paint("#FFFFFF", a))
    c.drawPath(p, wb.marker(GRAY, 5, a))
    for q in range(4):
        C.line(c, (x - w / 2 + 30 + q * w / 4, y - h / 2 + 20), (x - w / 2 + 20 + q * w / 4, y + h / 2 - 20), GRAY_L, 3, a)


GRAY_L = "#C9CCD2"


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：小李抱着膝盖，气泡“我没事”；朋友的邀约、家人的电话被他一一挡回
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    LX = cx - 280
    k_li = kq(j, wp(0, 1, 0.3), 0)
    k_ok = nx(j, wp(0, 2, 0.4), k_li)
    k_friend = nx(j, wp(1, 1, 0.3), k_ok)
    k_family = nx(j, wp(1, 3, 0.3), k_friend)
    L.note("我没事", "一起吃饭？", "在忙", "吃了吗？", "烦")

    def scene(c, kk, T):
        tl, to, tf, tfa = (tb(j, k) for k in (k_li, k_ok, k_friend, k_family))
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "sad", squash=0.8)
        if T >= to:
            with K.at(c, LX + 30, cy - 160, 0, pop_scale(T - to)):
                bubble_box(c, 0, 0, 300, 110, -1)
                K.text(c, "我没事", 0, 0, 56, "hand", BLACK)
        for i, (t0, q, a_) in enumerate(((tf, "一起吃饭？", "在忙"), (tfa, "吃了吗？", "烦"))):
            if T < t0:
                continue
            y = cy - 380 + i * 420
            f = ease_in_out(clamp01((T - t0 - 0.45) / 0.4))
            with K.at(c, cx + 260, y, 0, pop_scale(T - t0)):
                box(c, 0, 0, 340, 120, BLUE_FILL if i == 0 else NOTE_FILL, BLUE if i == 0 else ORANGE, 5, 20, 1 - 0.55 * f)
                K.text(c, q, 0, 0, 48, "hand", INK, 1 - 0.55 * f)
            if T >= t0 + 0.2:
                with K.at(c, cx + 20, y + 150, -4, pop_scale(T - t0 - 0.2)):
                    chip(c, 0, 0, a_, RED_FILL, RED, 46)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_ok, "pop", 0.75, "我没事")
    b.hit(j, k_friend, "wood_high", 0.7, "推说忙")
    b.hit(j, k_family, "rim", 0.75, "嫌家人烦")


screen1()


# ================================================================ 屏 2（drop）：人都走开了，小李一个人坐在空房间
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_go = kq(j, wp(2, 0, 0.3), 0)
    L.note("难受")

    def scene(c, kk, T):
        tg, td = tb(j, k_go), tb(j, dk)
        g = pop_scale(T - tg)
        if g <= 0:
            return None
        C.line(c, (cx - 560, GY + 6), (cx + 560, GY + 6), GRAY, 6)
        for i, x0 in enumerate((cx + 120, cx + 330)):
            f = ease_in_out(clamp01((T - tg - 0.2 * i) / 1.2))
            x = lerp(x0, x0 + 400, f)
            a = 1 - f
            if a > 0:
                (draw_wang if i else draw_li)(c, x, GY, 0.8, alpha=a, **({"back": True} if not i else {}))
        with at_pop(c, cx - 250, GY, g):
            draw_li(c, cx - 250, GY, 0.95, "sad" if T >= td else "flat", squash=0.8)
        if T >= td:
            for q in range(3):
                f = ((T - td) * 0.6 + q / 3) % 1
                c.drawCircle(cx - 250 + 40 * math.sin(q * 2 + T), cy - 60 - 160 * f, 16 + 10 * f, K.paint(GRAY, 0.5 * (1 - f)))
            with K.at(c, cx + 180, cy - 280, -4, C.slam_scale(T - td)):
                chip(c, 0, 0, "难受", GRAY_L, GRAY, 70)
        return None
    ev(j, k_go, scene, "shaker", 0.65)
    b.hit(j, dk, "kick", 0.9, "一个人难受")
    b.shots[j].shake = [(dk, 9.0)]
    b.shots[j].flashes = [(dk, 0.2)]


screen2()


# ================================================================ 屏 3：绿皮书翻开；老年阿玛兰妲坐在廊下织白布，左手缠黑纱布
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(3, 0, 0.4), 0)
    k_old = nx(j, wp(3, 2, 0.3), k_book)
    k_cloth = nx(j, wp(3, 4, 0.3), k_old)
    k_name = nx(j, wp(4, 0, 0.5), k_cloth)
    k_band = nx(j, wp(4, 2, 0.4), k_name)
    KT.book(j, k_book, x=cx - 360, y=cy - 300)
    L.note(*AMA, "寿衣", "黑纱布")
    AX = cx + 180

    def scene(c, kk, T):
        to, tc, tn, tbd = (tb(j, k) for k in (k_old, k_cloth, k_name, k_band))
        g = pop_scale(T - to)
        if g <= 0:
            return None
        for q in range(2):
            C.line(c, (cx - 120 + q * 600, cy - 160), (cx - 120 + q * 600, GY), "#8A6A3A", 14)
        C.line(c, (cx - 160, cy - 160), (cx + 540, cy - 160), "#8A6A3A", 14)
        weave = 14 * math.sin((T - tc) * 6) if T >= tc else 0
        with at_pop(c, AX, GY, g):
            draw_lady(c, AX, GY, 1.0, "purple", hair="gray", mood="flat", bandage="r" if T >= tbd else None,
                      lh=(AX - 110, GY - 220 + weave), rh=(AX + 110, GY - 220 - weave))
        if T >= tc:
            f = ease_out(clamp01((T - tc) / 0.6))
            cloth(c, AX, GY - 120, 260, 220 * max(0.1, f))
            K.text(c, "寿衣", AX + 230, GY - 160, 52, "hand", GRAY, f)
        if T >= tn:
            tag(c, AX, GY - 470, AMA, clamp01((T - tn) / 0.3))
        if T >= tbd:
            hx, hy = AX + 110, GY - 220
            ring = skia.Path()
            ring.addOval(skia.Rect.MakeXYWH(hx - 60, hy - 60, 120, 120))
            c.drawPath(wb.partial(ring, ease_out(clamp01((T - tbd) / 0.3)))[0], wb.marker(RED, 7))
            K.text(c, "黑纱布", hx + 60, hy - 110, 50, "hand", RED, clamp01((T - tbd) / 0.3))
        return None
    ev(j, k_old, scene, "bongo_low", 0.7)
    b.hit(j, k_cloth, "shaker", 0.6, "一针一针织寿衣")
    b.hit(j, k_name, "pop", 0.7, "阿玛兰妲")
    b.hit(j, k_band, "rim", 0.8, "黑纱布")


screen3()


# ================================================================ 屏 4：年轻的克雷斯皮带着自动钢琴来了；两个姑娘的心同时亮起
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_back = kq(j, wp(5, 0, 0.5), 0)
    k_cre = nx(j, wp(5, 2, 0.3), k_back)
    k_dance = nx(j, wp(5, 3, 0.3), k_cre)
    k_love = nx(j, wp(6, 2, 0.4), k_dance)
    L.note("年轻时", *CRE, *REB, "阿玛兰妲")
    CX_ = cx - 300

    def scene(c, kk, T):
        tbk, tc, td, tl = (tb(j, k) for k in (k_back, k_cre, k_dance, k_love))
        sc = pop_scale(T - tbk)
        if sc > 0:
            with K.at(c, cx + 300, cy - 500, 4, sc):
                box(c, 0, 0, 260, 100, NOTE_FILL, ORANGE, 5, 10)
                K.text(c, "年轻时", 0, 2, 52, "hand", RED)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, CX_ - 50, GY - 150, 0, g):
            box(c, 0, 0, 300, 260, "#5E4128", INK, 6, 10)
            for q in range(7):
                c.drawRect(skia.Rect.MakeXYWH(-130 + q * 37, -40, 32, 60), K.paint("#FFFFFF"))
            for q in range(3):
                f = ((T - tc) * 0.7 + q / 3) % 1
                K.text(c, "♪", -60 + q * 60, -170 - 120 * f, 50, "hand", INK, 1 - f)
        bob = 10 * math.sin((T - td) * 6) if T >= td else 0
        with at_pop(c, CX_ + 180, GY, g):
            crespi(c, CX_ + 180, GY - abs(bob), 0.95, mood="smile", rh=(CX_ + 300, GY - 320 + bob))
        tag(c, CX_ + 180, GY - 480, CRE, clamp01(g), 40, "#3D4A63")
        for i, (x, who) in enumerate(((cx + 220, REB), (cx + 430, AMA))):
            s_ = pop_scale(T - td - 0.1 * i)
            if s_ <= 0:
                continue
            with at_pop(c, x, GY, s_):
                if i == 0:
                    draw_lady(c, x, GY, 0.85, "green", hair="long", mood="smile" if T >= tl else "flat")
                else:
                    amaranta(c, x, GY, 0.85, mood="smile" if T >= tl else "flat")
            name_tag(c, x, GY - 400 - i * 110, who[0], "#3F6B3A" if i == 0 else TAGC, 38, clamp01(s_))
            if T >= tl:
                heart(c, x, GY - 340 * 0.85 + 70, 34 * pop_scale(T - tl - 0.08 * i))
        return None
    ev(j, k_back, scene, "wood_low", 0.6)
    b.hit(j, k_cre, "bongo_low", 0.75, "克雷斯皮来了")
    b.hit(j, k_dance, "shaker", 0.65, "教跳舞")
    b.hit(j, k_love, "ding", 0.85, "同时爱上他")


screen4()


# ================================================================ 屏 5：他牵起雷贝卡，阿玛兰妲在门后咬牙
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_pick = kq(j, wp(7, 0, 0.5), 0)
    k_mad = nx(j, wp(7, 1, 0.4), k_pick)
    k_vow = nx(j, wp(7, 2, 0.4), k_mad)
    L.note("拦住这门婚事")

    def scene(c, kk, T):
        tp, tm, tv = tb(j, k_pick), tb(j, k_mad), tb(j, k_vow)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        RX, CX_ = cx - 110, cx - 330
        with at_pop(c, CX_, GY, g):
            crespi(c, CX_, GY, 0.95, mood="smile", rh=(CX_ + 110, GY - 200))
        with at_pop(c, RX, GY, g):
            draw_lady(c, RX, GY, 0.9, "green", hair="long", mood="smile", lh=(RX - 110, GY - 200))
        heart(c, (CX_ + RX) / 2, cy - 60, 50 * g)
        DX = cx + 360
        box(c, DX, GY - 230, 220, 460, "#B5562E", "#5E2E18", 7, 6)
        if T >= tm:
            f = ease_out(clamp01((T - tm) / 0.4))
            with at_pop(c, DX - 100, GY, f):
                amaranta(c, DX - 100, GY, 0.9, mood="angry")
            name_tag(c, DX - 100, GY - 400, "阿玛兰妲", TAGC, 38, f)
        if T >= tv:
            with K.at(c, cx + 200, cy - 420, -3, C.slam_scale(T - tv)):
                bubble_box(c, 0, 0, 460, 120, 1)
                K.text(c, "拦住这门婚事", 0, 0, 52, "hand", RED)
        return None
    ev(j, k_pick, scene, "bongo_high", 0.7)
    b.hit(j, k_mad, "wood_low", 0.7, "阿玛兰妲恨得发誓")
    b.hit(j, k_vow, "rim", 0.85, "拦住婚事")


screen5()


# ================================================================ 屏 6：克雷斯皮捧花走向阿玛兰妲，她转身，大字“不”砸下
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_turn = kq(j, wp(8, 1, 0.4), 0)
    k_hope = nx(j, wp(9, 0, 0.5), k_turn)
    k_ask = nx(j, wp(9, 1, 0.5), k_hope)
    k_no = nx(j, wp(9, 3, 0.2), k_ask)
    L.note("死也不嫁")
    AX = cx + 280

    def scene(c, kk, T):
        tt, th, ta, tn = (tb(j, k) for k in (k_turn, k_hope, k_ask, k_no))
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        walk = ease_in_out(clamp01((T - tt) / 1.0))
        CX_ = lerp(cx - 560, cx - 220, walk)
        kneel = T >= ta
        with at_pop(c, CX_, GY, g):
            crespi(c, CX_, GY + (30 if kneel else 0), 0.95 if not kneel else 0.85, mood="sad" if T >= tn else "smile",
                   rh=(CX_ + 160, GY - 260))
            for q in range(3):
                c.drawCircle(CX_ + 160 + (q - 1) * 26, GY - 300 + (q % 2) * 14, 16, K.paint(RED if q != 1 else YELLOW))
        with at_pop(c, AX, GY, g):
            amaranta(c, AX, GY, 0.95, mood="smile" if T < tn else "flat", head_dx=0 if T < tn else 10)
        if T >= th and T < tn:
            heart(c, AX, cy - 120, 40 * pop_scale(T - th))
        if T >= tn:
            with K.at(c, cx + 20, cy - 320, 0, C.slam_scale(T - tn)):
                K.text(c, "不", 0, 0, 260, "serif_black", RED)
            K.text(c, "死也不嫁", cx + 20, cy - 110, 60, "hand", RED, clamp01((T - tn - 0.2) / 0.3))
            heart(c, CX_ + 60, cy - 50, 44, broken=ease_out(clamp01((T - tn) / 0.4)))
        return None
    ev(j, k_turn, scene, "bongo_low", 0.7)
    b.hit(j, k_hope, "pop", 0.7, "给他希望")
    b.hit(j, k_ask, "ding", 0.75, "真来求婚")
    b.hit(j, k_no, "kick", 0.95, "死也不嫁")
    b.shots[j].shake = [(k_no, 9.0)]


screen6()


# ================================================================ 屏 7：钢琴声停；炉火；一条黑纱布缠上她的手
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_dead = kq(j, wp(10, 1, 0.3), 0)
    k_fire = nx(j, wp(11, 1, 0.3), k_dead)
    k_wrap = nx(j, wp(11, 2, 0.4), k_fire)
    L.note("黑纱布")

    def scene(c, kk, T):
        td, tf, tw = tb(j, k_dead), tb(j, k_fire), tb(j, k_wrap)
        g = pop_scale(T - td)
        if g <= 0:
            return None
        with K.at(c, cx - 300, cy - 260, 0, g):
            box(c, 0, 0, 300, 260, "#5E4128", INK, 6, 10)
            for q in range(7):
                c.drawRect(skia.Rect.MakeXYWH(-130 + q * 37, -40, 32, 60), K.paint("#FFFFFF"))
            K.text(c, "♪", 60, -170, 60, "hand", GRAY, 0.3)
            C.line(c, (20, -210), (110, -130), RED, 8)
        if T < tf:
            return None
        SX = cx + 200
        box(c, SX, GY - 90, 360, 180, "#8A8F99", INK, 7, 10)
        for q in range(4):
            fh = 60 + 30 * math.sin((T - tf) * 9 + q)
            c.drawPath(P((SX - 120 + q * 80, GY - 180), (SX - 90 + q * 80, GY - 180 - fh), (SX - 60 + q * 80, GY - 180), close=True),
                       K.paint(ORANGE))
        AX = cx - 220
        with at_pop(c, AX, GY, pop_scale(T - tf)):
            amaranta(c, AX, GY, 0.95, mood="sad", rh=(SX - 150, GY - 220) if T < tw else (AX + 120, GY - 220),
                     bandage="r" if T >= tw else None)
        if T >= tw:
            sparkle(c, AX + 120, GY - 220, T - tw, GRAY, 8, 30, 100)
            with K.at(c, cx + 200, cy - 60, -3, C.slam_scale(T - tw)):
                chip(c, 0, 0, "黑纱布", GRAY_L, INK, 60)
        return None
    ev(j, k_dead, scene, "xiaoluo", 0.7)
    b.hit(j, k_fire, "tom", 0.75, "炉火")
    b.hit(j, k_wrap, "rim", 0.85, "缠上黑纱布")


screen7()


# ================================================================ 屏 8：马尔克斯上校来陪她下棋、求婚；她又摇头
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_ger = kq(j, wp(12, 1, 0.3), 0)
    k_ask = nx(j, wp(12, 2, 0.4), k_ger)
    k_care = nx(j, wp(13, 0, 0.4), k_ask)
    k_no = nx(j, wp(13, 2, 0.2), k_care)
    L.note(*GER, "很多年后", "不")
    GX, AX = cx - 300, cx + 280

    def scene(c, kk, T):
        tg, ta, tc, tn = (tb(j, k) for k in (k_ger, k_ask, k_care, k_no))
        g = pop_scale(T - tg)
        if g <= 0:
            return None
        K.text(c, "很多年后", cx + 330, cy - 520, 48, "hand", GRAY, clamp01(g))
        with K.at(c, cx, GY - 140, 0, g):
            box(c, 0, 0, 240, 24, "#E7D6BA", "#8B6B43", 5, 4)
            C.line(c, (0, 12), (0, 140), "#8B6B43", 8)
            for q in range(6):
                c.drawCircle(-80 + q * 32, -24, 10, K.paint((RED, BLUE, GREEN)[q % 3]))
        with at_pop(c, GX, GY, g):
            gerineldo(c, GX, GY, 0.95, mood="smile", rh=(GX + 150, GY - 300) if T >= ta else None)
        tag(c, GX, GY - 490, GER, clamp01(g), 38, "#3F6B3A")
        with at_pop(c, AX, GY, g):
            amaranta(c, AX, GY, 0.95, mood="flat", bandage="r", head_dx=-8 * math.sin((T - tn) * 14) if T >= tn else 0)
        if T >= ta:
            with K.at(c, GX + 180, cy - 260, 0, pop_scale(T - ta)):
                c.drawCircle(0, 0, 26, K.paint(YELLOW))
                c.drawCircle(0, 0, 26, wb.marker(INK, 4))
        if T >= tc:
            heart(c, AX, cy - 80, 34 * pop_scale(T - tc), a=0.8)
        if T >= tn:
            with K.at(c, AX, cy - 300, 0, C.slam_scale(T - tn)):
                bubble_box(c, 0, 0, 180, 130, -1)
                K.text(c, "不", 0, 0, 90, "serif_black", RED)
        return None
    ev(j, k_ger, scene, "bongo_low", 0.7)
    b.hit(j, k_ask, "ding", 0.75, "求婚")
    b.hit(j, k_care, "pop", 0.65, "心里在乎")
    b.hit(j, k_no, "kick", 0.85, "还是不")


screen8()


# ================================================================ 屏 9：两个男人的背影越走越远，她站在中间
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_a = kq(j, wp(14, 0, 0.4), 0)
    k_best = nx(j, wp(14, 1, 0.4), k_a)
    L.note("对她最好的人")

    def scene(c, kk, T):
        ta, tbst = tb(j, k_a), tb(j, k_best)
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        f = ease_in_out(clamp01((T - ta) / 1.6))
        crespi(c, lerp(cx - 260, cx - 520, f), GY, 0.8, alpha=1 - 0.5 * f)
        gerineldo(c, lerp(cx + 260, cx + 520, f), GY, 0.8, alpha=1 - 0.5 * f)
        with at_pop(c, cx, GY, g):
            amaranta(c, cx, GY, 1.0, mood="sad", bandage="r")
        if T >= tbst:
            with K.at(c, cx, cy - 330, 0, C.slam_scale(T - tbst)):
                chip(c, 0, 0, "对她最好的人", RED_FILL, RED, 56)
        return None
    ev(j, k_a, scene, "xiaoluo", 0.65)
    b.hit(j, k_best, "rim", 0.8, "推开的都是对她好的人")


screen9()


# ================================================================ 屏 10：小李心口一块小盾牌，盾牌后面写着“怕”；大字“三个小动作”
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = kq(j, wp(15, 0, 0.4), 0)
    k_fear = nx(j, wp(15, 1, 0.4), k_li)
    k_two = nx(j, wp(15, 3, 0.3), k_fear)
    k_three = nx(j, wp(16, 1, 0.4), k_two)
    L.note("怕", "怕被拒绝", "怕受伤", "三个小动作")
    LX = cx - 280

    def scene(c, kk, T):
        tl, tf, t2, t3 = (tb(j, k) for k in (k_li, k_fear, k_two, k_three))
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        hy = GY - 290
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "flat", lh=(LX - 20, hy + 120), rh=(LX + 20, hy + 120))
            sh = P((LX - 70, hy + 60), (LX + 70, hy + 60), (LX + 60, hy + 160), (LX, hy + 210), (LX - 60, hy + 160), close=True)
            c.drawPath(sh, K.paint(BLUE_FILL))
            c.drawPath(sh, wb.marker(BLUE, 6))
        if T >= tf:
            with K.at(c, LX + 260, hy + 40, 0, C.slam_scale(T - tf)):
                K.text(c, "怕", 0, 0, 130, "hand", RED)
        if T >= t2:
            for i, s in enumerate(("怕被拒绝", "怕受伤")):
                with K.at(c, cx + 300, cy - 360 + i * 140, 0, pop_scale(T - t2 - i * 0.15)):
                    chip(c, 0, 0, s, GRAY_L, GRAY, 48)
        if T >= t3:
            with K.at(c, cx + 80, cy - 20, -3, C.slam_scale(T - t3)):
                K.text(c, "三个小动作", 0, 0, 100, "hand", RED)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_fear, "rim", 0.8, "怕")
    b.hit(j, k_two, "pop", 0.65, "怕被拒绝怕受伤")
    b.hit(j, k_three, "kick", 0.85, "三个小动作")


screen10()


# ================================================================ 屏 11：第一个：秒表走十格，“我没事”换成“让我想想”
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    k_clock = kq(j, wp(17, 0, 0.6), 1)
    k_swap = nx(j, wp(17, 1, 0.5), k_clock)
    k_new = nx(j, wp(17, 2, 0.3), k_swap)
    L.note("10秒", "我没事", "让我想想")

    def scene(c, kk, T):
        tc, ts, tn = tb(j, k_clock), tb(j, k_swap), tb(j, k_new)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx - 250, cy - 120, 0, g):
            c.drawCircle(0, 0, 150, K.paint("#FFFFFF"))
            c.drawCircle(0, 0, 150, wb.marker(BLACK, 8))
            ang = min(1.0, (T - tc) / 1.2) * 2 * math.pi
            for q in range(10):
                a = q / 10 * 2 * math.pi - math.pi / 2
                on = q / 10 * 2 * math.pi <= ang
                c.drawCircle(120 * math.cos(a), 120 * math.sin(a), 12, K.paint(GREEN if on else GRAY_L))
            C.line(c, (0, 0), (100 * math.cos(ang - math.pi / 2), 100 * math.sin(ang - math.pi / 2)), RED, 8)
            K.text(c, "10秒", 0, 210, 52, "hand", INK)
        if T >= ts:
            f = clamp01((T - ts) / 0.3)
            with K.at(c, cx + 250, cy - 200, 0, 1):
                bubble_box(c, 0, 0, 340, 120, -1, 1 - f * 0.6)
                K.text(c, "我没事", 0, 0, 56, "hand", BLACK, 1 - f * 0.6)
                C.line(c, (-120, 0), (lerp(-120, 120, f), 0), RED, 8)
        if T >= tn:
            with K.at(c, cx + 250, cy + 60, 0, C.slam_scale(T - tn)):
                bubble_box(c, 0, 0, 380, 130, -1)
                K.text(c, "让我想想", 0, 0, 62, "hand", GREEN)
        return None
    ev(j, k_clock, scene, "wood_high", 0.65)
    b.hit(j, k_swap, "shaker", 0.7, "划掉我没事")
    b.hit(j, k_new, "ding", 0.8, "让我想想")


screen11()


# ================================================================ 屏 12：第二个：对话框里只打半句“我今天有点累”，对面回了一颗心
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    k_ph = kq(j, wp(18, 0, 0.6), 1)
    k_msg = nx(j, wp(18, 2, 0.3), k_ph)
    k_heart = nx(j, wp(18, 2, 0.9), k_msg)
    L.note("我今天有点累", "半句真话")

    def scene(c, kk, T):
        tp, tm, th = tb(j, k_ph), tb(j, k_msg), tb(j, k_heart)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 20, 0, g):
            box(c, 0, 0, 560, 760, "#FFFFFF", BLACK, 8, 40)
            if T >= tm:
                with K.at(c, 60, -60, 0, pop_scale(T - tm)):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-200, -50, 400, 100), 30, 30, K.paint(GREEN_FILL))
                    K.text(c, "我今天有点累", 0, 0, 48, "hand", INK)
            if T >= th:
                with K.at(c, -120, 120, 0, pop_scale(T - th)):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-110, -60, 220, 120), 30, 30, K.paint("#E9EEF4"))
                    heart(c, 0, -10, 34)
        if T >= th:
            with K.at(c, cx + 20, cy + 480, -2, C.slam_scale(T - th - 0.15)):
                chip(c, 0, 0, "半句真话", NOTE_FILL, ORANGE, 52)
        return None
    ev(j, k_ph, scene, "pop", 0.7)
    b.hit(j, k_msg, "wood_high", 0.7, "打半句")
    b.hit(j, k_heart, "ding", 0.85, "对面回了一颗心")


screen12()


# ================================================================ 屏 13：第三个：日历上“以后”划掉，改成“今天”，一张谢谢卡飞出去
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    k_later = kq(j, wp(19, 0, 0.6), 1)
    k_today = nx(j, wp(19, 2, 0.4), k_later)
    k_card = nx(j, wp(19, 3, 0.3), k_today)
    L.note("以后", "今天", "谢谢")

    def scene(c, kk, T):
        tl, tt, tc = tb(j, k_later), tb(j, k_today), tb(j, k_card)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with K.at(c, cx - 200, cy - 140, -3, g):
            box(c, 0, 0, 420, 360, "#FFFFFF", BLACK, 7, 12)
            c.drawRect(skia.Rect.MakeXYWH(-210, -180, 420, 80), K.paint(RED_FILL))
            K.text(c, "以后", 0, 40, 100, "hand", GRAY)
            if T >= tt:
                C.line(c, (-120, 40), (lerp(-120, 120, ease_out(clamp01((T - tt) / 0.25))), 40), RED, 10)
                K.text(c, "今天", 0, 140, 80, "hand", RED, clamp01((T - tt - 0.1) / 0.2))
        if T >= tc:
            f = ease_out(clamp01((T - tc) / 0.7))
            with K.at(c, lerp(cx - 100, cx + 200, f), lerp(cy + 120, cy + 250, f), lerp(-10, 6, f), pop_scale(T - tc)):
                box(c, 0, 0, 300, 180, NOTE_FILL, ORANGE, 6, 10)
                K.text(c, "谢谢", 0, 0, 70, "hand", RED)
            with at_pop(c, cx + 440, cy + 520, pop_scale(T - tc - 0.3)):
                draw_wang(c, cx + 440, cy + 520, 0.7, mood="smile")
        return None
    ev(j, k_later, scene, "wood_high", 0.65)
    b.hit(j, k_today, "rim", 0.8, "改成今天")
    b.hit(j, k_card, "ding", 0.85, "说声谢谢")


screen13()


# ================================================================ 屏 14：好处：小李身边坐回来两个人
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = kq(j, wp(20, 0, 0.6), 0)
    k_back = nx(j, wp(20, 1, 0.4), k_li)
    k_light = nx(j, wp(20, 2, 0.4), k_back)
    L.note("留得住")

    def scene(c, kk, T):
        tl, tbk, tlt = tb(j, k_li), tb(j, k_back), tb(j, k_light)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        C.line(c, (cx - 560, GY + 6), (cx + 560, GY + 6), GRAY, 6)
        with at_pop(c, cx, GY, g):
            draw_li(c, cx, GY, 0.95, "smile" if T >= tbk else "flat")
        if T >= tbk:
            f = ease_out(clamp01((T - tbk) / 0.6))
            draw_wang(c, lerp(cx - 600, cx - 300, f), GY, 0.9, mood="smile")
            draw_man(c, lerp(cx + 600, cx + 300, f), GY, 0.9, "blue", mood="smile")
        if T >= tlt:
            with K.at(c, cx, cy - 330, 0, C.slam_scale(T - tlt)):
                chip(c, 0, 0, "留得住", GREEN_FILL, GREEN, 66)
            sparkle(c, cx, cy - 330, T - tlt, YELLOW, 10, 120, 260)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_back, "clap", 0.75, "人回来了")
    b.hit(j, k_light, "ding", 0.85, "不用一个人扛")


screen14()


# ================================================================ 屏 15：评论区；一双手接住一颗心；下一讲预告：地上一个粉笔圈
def enc(c, T, te, th, cx, cy):
    y = cy + 520
    for sg in (-1, 1):
        f = ease_out(clamp01((T - te) / 0.5))
        x = cx + sg * lerp(400, 140, f)
        c.drawPath(P((x, y + 80), (x - sg * 20, y), (x - sg * 90, y - 40)), wb.marker(BLACK, 12))
    if T >= te:
        hy = lerp(cy + 150, y - 30, ease_in_out(clamp01((T - te) / 0.8))) if T < th else y - 30
        heart(c, cx, hy, 70)
        if T >= th:
            sparkle(c, cx, y - 30, T - th, YELLOW, 12, 90, 220)
            K.text(c, "接住", cx, y + 170, 60, "hand", GREEN, clamp01((T - th) / 0.3))


def chalk_icon(c, x, y, dt):
    with K.at(c, x, y, 0, pop_scale(dt)):
        ring = skia.Path()
        ring.addOval(skia.Rect.MakeXYWH(-70, -30, 140, 60))
        c.drawPath(ring, wb.marker(GRAY, 6))
        C.line(c, (0, 10), (0, -60), BLACK, 6)
        c.drawCircle(0, -76, 16, wb.marker(BLACK, 5))


L.note("接住")
KT.ending(15, "你推开过谁吗？", ["朋友", "家人", "前任"], 22, 23, enc, 24, ["身边全是人", "为什么还是很孤单？"],
          enc_piece=2, next_icon=chalk_icon)

# ================================================================ 收尾
L.finish(cover_shot=6, square_shot=3, notes=NOTES)
L.export(globals())
