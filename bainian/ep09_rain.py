"""《百年孤独》09 大雨：明明出了事，为什么大家都说没有？（白板手绘 + AI 旁白，竖屏 2:3）

经典问答：“出了什么事？”“什么事也没有。”香蕉公司工人罢工，车站广场军队开枪；何塞·阿尔卡蒂奥第二在运尸的火车上醒来，
跳车走回镇上挨家挨户问，人人都说没发生过；雨下了四年十一个月零两天；他关在屋里到死念叨“三千多人”。
落到“被所有人说没事”时的三步。开枪一段只画人群与远处的剪影，不画伤亡。文案见 bainian/PLAN.md「### 09」。
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
                            at_pop, box, bubble_box, chip, desk, draw_lady, draw_li, draw_man, draw_wang, name_tag, pop_scale,
                            sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "生活里", 1),
    ([2], "生活里", 2),
    ([3, 4], "书里的人", 3),
    ([5], "广场", 4),
    ([6, 7], "火车", 5),
    ([8], "什么事也没有", 6),
    ([9], "大雨", 7),
    ([10, 11], "记得的人", 8),
    ([12], "说回我们", 9),
    ([13], "说回我们", 10),
    ([14], "第一步", 11),
    ([15], "第二步", 12),
    ([16], "第三步", 13),
    ([17], "好处", 14),
    ([18, 19, 20, 21], "评论区见", 15),
]

THEME = BT.get("09")
L = N.Lesson("09", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(14)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》第 15–16 章（范晔译本）。情节为转述，不引原文；开枪一段只画人群与远处剪影。",
    "今人（小李、小王）为虚构示意；书中人造型为示意（一百多年前的加勒比小镇打扮）。",
]

JA2 = ("何塞·阿尔卡蒂奥第二", "第四代")


def tag(c, x, y, who, a=1.0, size=38):
    name_tag(c, x, y, who[0], "#2F5B8E", size, a, who[1])


def ja2(c, x, y, s, **kw):
    """何塞·阿尔卡蒂奥第二：草帽、白衬衫、小胡子。"""
    kw.setdefault("beard", "mustache")
    kw.setdefault("hat", "straw")
    draw_man(c, x, y, s, "white", **kw)


def rain(c, x0, x1, y0, y1, T, n=70, a=0.7, speed=900):
    for i in range(n):
        r = (i * 9301 + 49297) % 233280 / 233280
        r2 = (i * 7919 + 104729) % 1000 / 1000
        x = x0 + (x1 - x0) * r
        y = y0 + ((T * speed + r2 * (y1 - y0)) % (y1 - y0))
        C.line(c, (x, y), (x - 10, y + 40), BLUE, 4, a)


def no_bubble(c, x, y, s="没事", sc=1.0, a=1.0, tail=-1):
    with K.at(c, x, y, 0, sc):
        bubble_box(c, 0, 0, K.text_w(s, 46, "hand") + 70, 100, tail, a)
        K.text(c, s, 0, 0, 46, "hand", GRAY, a)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：会议室里一圈人摆手说“没事”；小李举手，旁边飘来“想多了”“别添乱”
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_room = kq(j, wp(0, 1, 0.4), 0)
    k_ok = nx(j, wp(0, 2, 0.4), k_room)
    k_raise = nx(j, wp(1, 0, 0.4), k_room + 2)
    k_lol = nx(j, wp(1, 1, 0.4), k_raise)
    k_stop = nx(j, wp(1, 2, 0.4), k_lol)
    L.note("没事", "想多了", "别添乱")

    def scene(c, kk, T):
        tr, to, tra, tl, ts = (tb(j, k) for k in (k_room, k_ok, k_raise, k_lol, k_stop))
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        with K.at(c, cx, GY - 140, 0, g):
            box(c, 0, 0, 960, 30, "#E7D6BA", "#8B6B43", 6, 6)
        for i, x in enumerate((cx - 400, cx - 160, cx + 160, cx + 400)):
            if i == 1:
                continue
            (draw_wang if i == 2 else draw_man)(c, x, GY, 0.8, **({"mood": "smile"} if i == 2 else {"color": "gray", "mood": "smile"}))
            if T >= to:
                no_bubble(c, x, cy - 60 - (i % 2) * 70, "没事", pop_scale(T - to - 0.08 * i))
        LX = cx - 160
        hy = GY - 290 * 0.85
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.85, "flat" if T < tl else "sad", rh=(LX + 60, hy - 120) if T >= tra else None)
        if T >= tl:
            with K.at(c, cx + 200, cy - 360, 0, pop_scale(T - tl)):
                chip(c, 0, 0, "想多了", "#D9DCE1", GRAY, 48)
        if T >= ts:
            with K.at(c, cx - 380, cy - 420, 0, pop_scale(T - ts)):
                chip(c, 0, 0, "别添乱", "#D9DCE1", GRAY, 48)
        return None
    ev(j, k_room, scene, "wood_low", 0.6)
    b.hit(j, k_ok, "pop", 0.7, "大家都说没事")
    b.hit(j, k_raise, "wood_high", 0.65, "你一提")
    b.hit(j, k_lol, "rim", 0.7, "想多了")
    b.hit(j, k_stop, "rim", 0.75, "别添乱")


screen1()


# ================================================================ 屏 2（drop）：小李头顶一个问号越来越大
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_li = kq(j, wp(2, 0, 0.3), 0)
    L.note("看错了？")

    def scene(c, kk, T):
        tl, td = tb(j, k_li), tb(j, dk)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            draw_li(c, cx, GY, 1.0, "o" if T >= td else "flat")
        grow = 0.4 + 0.6 * ease_out(clamp01((T - tl) / 2.5))
        with K.at(c, cx, cy - 250, 0, grow if T < td else grow * (1 + 0.3 * C.slam_scale(T - td))):
            K.text(c, "？", 0, 0, 300, "hand", BLUE)
        if T >= td:
            with K.at(c, cx + 300, cy + 40, -4, C.slam_scale(T - td)):
                chip(c, 0, 0, "看错了？", RED_FILL, RED, 56)
        return None
    ev(j, k_li, scene, "shaker", 0.65)
    b.hit(j, dk, "kick", 0.9, "连你都怀疑")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：绿皮书翻开；香蕉园、工人举着牌子
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(3, 0, 0.4), 0)
    k_big = nx(j, wp(3, 2, 0.4), k_book)
    k_strike = nx(j, wp(4, 0, 0.5), k_big)
    k_sign = nx(j, wp(4, 1, 0.4), k_strike)
    KT.book(j, k_book, x=cx - 360, y=cy - 300)
    L.note("香蕉公司", "改善待遇", "罢工")

    def scene(c, kk, T):
        tbg, ts, tsg = tb(j, k_big), tb(j, k_strike), tb(j, k_sign)
        g = pop_scale(T - tbg)
        if g <= 0:
            return None
        for q in range(3):
            x = cx + 160 + q * 150
            with K.at(c, x, cy - 160, 0, g):
                C.line(c, (0, 0), (0, -200), "#6E4E22", 10)
                for a in (-50, -20, 20, 50):
                    c.drawPath(P((0, -200), (a * 3, -150), (a * 2.4, -120)), wb.marker(N.LEAF_LINE, 12))
                c.drawOval(skia.Rect.MakeXYWH(-20, -150, 40, 80), K.paint(YELLOW))
        K.text(c, "香蕉公司", cx + 300, cy - 420, 50, "serif_black", INK, g)
        if T >= ts:
            for i in range(4):
                x = cx - 420 + i * 230
                s_ = pop_scale(T - ts - i * 0.08)
                with at_pop(c, x, GY, s_):
                    draw_man(c, x, GY, 0.7, ("white", "ochre", "white", "gray")[i], hat="straw", mood="angry",
                             rh=(x + 80, GY - 330))
                if T >= tsg:
                    with K.at(c, x + 80, GY - 360, 0, pop_scale(T - tsg - i * 0.08)):
                        C.line(c, (0, 0), (0, 80), "#6E4E22", 6)
                        box(c, 0, -30, 160, 70, "#FFFFFF", RED, 5, 6)
                        K.text(c, ("罢工", "改善待遇")[i % 2], 0, -30, 30 if i % 2 else 40, "hand", RED)
        return None
    ev(j, k_big, scene, "wood_low", 0.6)
    b.hit(j, k_strike, "bongo_low", 0.75, "工人罢工")
    b.hit(j, k_sign, "rim", 0.75, "要求改善待遇")


screen3()


# ================================================================ 屏 4：火车站前的广场黑压压一片人，远处一排剪影
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_crowd = kq(j, wp(5, 1, 0.3), 0)
    k_army = nx(j, wp(5, 2, 0.3), k_crowd)
    k_shot = nx(j, wp(5, 2, 0.85), k_army)
    L.note("火车站", "几千人")

    def scene(c, kk, T):
        tc, ta, ts = tb(j, k_crowd), tb(j, k_army), tb(j, k_shot)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx + 250, cy - 380, 0, g):
            box(c, 0, 0, 420, 160, ADOBE, "#8A4B2A", 6, 6)
            K.text(c, "火车站", 0, 0, 56, "serif_black", INK)
        for r_ in range(4):
            for q in range(9):
                x = cx - 500 + q * 120 + (r_ % 2) * 60
                y = cy + 40 + r_ * 110
                if T >= tc + (r_ * 9 + q) * 0.01:
                    c.drawCircle(x, y, 26, K.paint("#4A4A4A"))
                    c.drawRoundRect(skia.Rect.MakeXYWH(x - 26, y + 22, 52, 60), 18, 18, K.paint("#4A4A4A"))
        K.text(c, "几千人", cx - 340, cy - 40, 54, "hand", INK, g)
        if T >= ta:
            for q in range(6):
                x = cx - 500 + q * 90
                with K.at(c, x, cy - 300, 0, pop_scale(T - ta - q * 0.05)):
                    c.drawRect(skia.Rect.MakeXYWH(-16, -60, 32, 90), K.paint("#2A2A2A"))
                    c.drawCircle(0, -78, 18, K.paint("#2A2A2A"))
        if T >= ts:
            f = 1 - clamp01((T - ts) / 0.4)
            c.drawRect(skia.Rect.MakeXYWH(cx - 580, cy - 585, 1160, 1215), K.paint("#FFFFFF", 0.6 * f))
        return None
    ev(j, k_crowd, scene, "shaker", 0.7)
    b.hit(j, k_army, "tom", 0.8, "军队")
    b.hit(j, k_shot, "kick", 0.95, "开了枪")
    b.shots[j].shake = [(k_shot, 9.0)]


ADOBE = N.ADOBE
screen4()


# ================================================================ 屏 5：一列长火车开向海边；何塞·阿尔卡蒂奥第二跳车，沿铁轨往回走
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_wake = kq(j, wp(6, 1, 0.4), 0)
    k_train = nx(j, wp(6, 3, 0.3), k_wake)
    k_jump = nx(j, wp(7, 0, 0.5), k_train)
    k_walk = nx(j, wp(7, 2, 0.3), k_jump)
    L.note(*JA2, "海边")

    def scene(c, kk, T):
        tw, tt, tj, twk = (tb(j, k) for k in (k_wake, k_train, k_jump, k_walk))
        g = pop_scale(T - tw)
        if g <= 0:
            return None
        TY = cy + 80
        C.line(c, (cx - 580, TY + 70), (cx + 580, TY + 70), INK, 6)
        for q in range(12):
            C.line(c, (cx - 560 + q * 100, TY + 60), (cx - 540 + q * 100, TY + 82), "#6E4E22", 8)
        move = (T - tt) * 70 if T >= tt else 0
        for q in range(4):
            x = cx - 380 + q * 260 + move
            if x > cx + 640:
                continue
            box(c, x, TY, 240, 110, "#6B5A48", INK, 6, 6)
            c.drawCircle(x - 70, TY + 60, 22, K.paint(INK))
            c.drawCircle(x + 70, TY + 60, 22, K.paint(INK))
        K.text(c, "海边 →", cx + 380, TY - 130, 46, "hand", GRAY, g)
        if T < tj:
            ja2(c, cx - 120 + move, TY - 50, 0.5, mood="o")
        else:
            u = ease_out(clamp01((T - tj) / 0.5))
            x0 = cx - 120 + (tj - tt) * 70
            x = lerp(x0, cx - 300, u) - (T - twk) * 90 * (T >= twk)
            x = max(x, cx - 380)
            ja2(c, x, GY, 0.9, mood="sad")
            tag(c, x, GY - 470, JA2, 1)
        return None
    ev(j, k_wake, scene, "xiaoluo", 0.7)
    b.hit(j, k_train, "shaker", 0.75, "装满尸体的火车")
    b.hit(j, k_jump, "tom", 0.8, "跳下火车")
    b.hit(j, k_walk, "wood_low", 0.65, "走回镇上")


screen5()


# ================================================================ 屏 6：一扇扇门打开，每个人都摇头：“没发生过”
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_doors = [kq(j, wp(8, 0, 0.5), 0)]
    k_doors.append(nx(j, wp(8, 1, 0.4), k_doors[0]))
    k_doors.append(nx(j, wp(8, 2, 0.5), k_doors[1]))
    L.note("没发生过")

    def scene(c, kk, T):
        if T < tb(j, k_doors[0]):
            return None
        ja2(c, cx - 450, GY, 0.85, mood="o", rh=(cx - 330, GY - 300))
        for i, k_ in enumerate(k_doors):
            t0 = tb(j, k_)
            if T < t0:
                continue
            x = cx - 120 + i * 260
            open_ = ease_out(clamp01((T - t0) / 0.3))
            box(c, x, GY - 200, 200, 400, "#3A2A12", "#5E2E18", 6, 4)
            (draw_lady if i % 2 else draw_man)(c, x, GY, 0.7, ("blue", "red", "ochre")[i],
                                               mood="flat", head_dx=12 * math.sin((T - t0) * 14))
            c.drawRect(skia.Rect.MakeXYWH(x - 100 + 200 * open_ - (200 if open_ > 0.99 else 0) * 0, GY - 400, 200 * (1 - open_), 400),
                       K.paint("#B5562E"))
            no_bubble(c, x, cy - 250 - (i % 2) * 90, "没发生过", pop_scale(T - t0 - 0.2))
        return None
    ev(j, k_doors[0], scene, "wood_high", 0.65)
    for k_ in k_doors[1:]:
        b.hit(j, k_, "wood_high", 0.65, "又一扇门")


screen6()


# ================================================================ 屏 7：大雨落个不停，日历一页页翻：四年、十一个月、两天
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    k_rain = kq(j, wp(9, 0, 0.5), 0)
    k_n = [nx(j, wp(9, 1, 0.3), k_rain)]
    k_n.append(nx(j, wp(9, 1, 0.8), k_n[0]))
    k_n.append(nx(j, wp(9, 2, 0.4), k_n[1]))
    NUM = ["四年", "十一个月", "零两天"]
    L.note(*NUM)

    def scene(c, kk, T):
        tr = tb(j, k_rain)
        if T < tr:
            return None
        rain(c, cx - 560, cx + 560, cy - 580, cy + 600, T - tr, 90, clamp01((T - tr) / 0.5) * 0.7)
        for i, (k_, s) in enumerate(zip(k_n, NUM)):
            t0 = tb(j, k_)
            if T < t0:
                continue
            with K.at(c, cx, cy - 280 + i * 230, 0, C.slam_scale(T - t0)):
                box(c, 0, 0, 520, 180, "#FFFFFF", INK, 6, 12)
                K.text(c, s, 0, 0, 90, "hand", BLUE)
        return None
    ev(j, k_rain, scene, "shaker", 0.75)
    for k_ in k_n:
        b.hit(j, k_, "tom", 0.75, "又一页日历")


screen7()


# ================================================================ 屏 8：小屋里他对着墙念叨“三千多”，墙上写满记号
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_room = kq(j, wp(10, 1, 0.4), 0)
    k_say = nx(j, wp(10, 3, 0.3), k_room)
    k_only = nx(j, wp(11, 0, 0.6), k_say)
    L.note("三千多人", "只有他记得")

    def scene(c, kk, T):
        tr, ts, to = tb(j, k_room), tb(j, k_say), tb(j, k_only)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        box(c, cx, cy - 20, 1000, 1000, "#EFE6D2", "#8B6B43", 7, 6, g)
        n = min(40, int((T - tr) / 0.06))
        for q in range(n):
            r_, c_ = divmod(q, 10)
            x, y = cx - 430 + c_ * 60, cy - 460 + r_ * 70
            for k in range(4):
                C.line(c, (x + k * 9, y), (x + k * 9, y + 40), GRAY, 3)
            C.line(c, (x - 4, y + 34), (x + 34, y + 6), GRAY, 3)
        ja2(c, cx + 250, GY, 0.95, mood="sad", hat=None, beard="full")
        if T >= ts:
            with K.at(c, cx - 120, cy + 80, 0, C.slam_scale(T - ts)):
                bubble_box(c, 0, 0, 380, 120, 1)
                K.text(c, "三千多人", 0, 0, 60, "hand", RED)
        if T >= to:
            with K.at(c, cx + 250, cy - 120, 3, pop_scale(T - to)):
                chip(c, 0, 0, "只有他记得", NOTE_FILL, ORANGE, 46)
        return None
    ev(j, k_room, scene, "xiaoluo", 0.7)
    b.hit(j, k_say, "rim", 0.8, "那天死了三千多人")
    b.hit(j, k_only, "ding", 0.75, "只有他记得")


screen8()


# ================================================================ 屏 9：小李手里一张报表，四周的“没事”气泡把他围住
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = kq(j, wp(12, 0, 0.4), 0)
    k_ring = nx(j, wp(12, 1, 0.4), k_li)
    k_self = nx(j, wp(12, 2, 0.4), k_ring)
    L.note("相信自己")

    def scene(c, kk, T):
        tl, tr, ts = tb(j, k_li), tb(j, k_ring), tb(j, k_self)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        hy = GY - 290
        with at_pop(c, cx, GY, g):
            draw_li(c, cx, GY, 1.0, "flat" if T < ts else "smile", rh=(cx + 120, hy + 100))
            doc = skia.Rect.MakeXYWH(cx + 90, hy + 20, 120, 160)
            c.drawRect(doc, K.paint("#FFFFFF"))
            c.drawRect(doc, wb.marker(RED, 5))
        if T >= tr:
            for q in range(8):
                if q == 6:
                    continue
                a = q / 8 * 2 * math.pi
                no_bubble(c, cx + 430 * math.cos(a), cy - 60 + 400 * math.sin(a), "没事", pop_scale(T - tr - q * 0.05))
        if T >= ts:
            c.drawCircle(cx + 150, hy + 100, 120, K.paint(YELLOW, 0.3))
            with K.at(c, cx, cy - 420, 0, C.slam_scale(T - ts)):
                chip(c, 0, 0, "相信自己", GREEN_FILL, GREEN, 56)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_ring, "shaker", 0.7, "都说没事")
    b.hit(j, k_self, "ding", 0.8, "还相信自己看见的")


screen9()


# ================================================================ 屏 10：大字“三步”
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = kq(j, wp(13, 0, 0.5), 0)
    k_three = nx(j, wp(13, 1, 0.5), k_li)
    L.note("三步")

    def scene(c, kk, T):
        tl, t3 = tb(j, k_li), tb(j, k_three)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, cx - 250, GY, g):
            draw_li(c, cx - 250, GY, 1.0, "smile")
        if T >= t3:
            with K.at(c, cx + 150, cy - 150, -3, C.slam_scale(T - t3)):
                K.text(c, "三步", 0, 0, 160, "hand", RED)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_three, "kick", 0.85, "三步")


screen10()


# ================================================================ 屏 11：第一步：本子上写下：时间、数字、谁在场
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    k_book = kq(j, wp(14, 1, 0.3), 1)
    k_rows = nx(j, wp(14, 2, 0.4), k_book)
    ROWS = [("时间", "周三 10:00"), ("数字", "退货 38%"), ("谁在场", "我、小王")]
    L.note("记下来", *(a for a, _ in ROWS), *(b_ for _, b_ in ROWS))

    def scene(c, kk, T):
        tbk, tr = tb(j, k_book), tb(j, k_rows)
        g = pop_scale(T - tbk)
        if g <= 0:
            return None
        with K.at(c, cx, cy + 40, -2, g):
            box(c, 0, 0, 760, 640, "#FFFFFF", BLACK, 7, 14)
            K.text(c, "记下来", 0, -240, 60, "hand", RED)
            for i, (a, v) in enumerate(ROWS):
                if T < tr + i * 0.3:
                    continue
                y = -100 + i * 130
                al = clamp01((T - tr - i * 0.3) / 0.25)
                K.text(c, a, -200, y, 50, "hand", BLUE, al)
                K.text(c, v, 120, y, 50, "hand", INK, al)
        return None
    ev(j, k_book, scene, "wood_high", 0.65)
    b.hit(j, k_rows, "pop", 0.75, "时间数字谁在场")


screen11()


# ================================================================ 屏 12：第二步：小王凑过来看本子，点头“我也看到了”
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_pair = kq(j, wp(15, 1, 0.5), 1)
    k_nod = nx(j, wp(15, 3, 0.5), k_pair)
    L.note("我也看到了", "核对")

    def scene(c, kk, T):
        tp, tn = tb(j, k_pair), tb(j, k_nod)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        LX, WX = cx - 200, cx + 200
        hy = GY - 290
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "smile", rh=(LX + 140, hy + 90))
        with at_pop(c, WX, GY, g):
            draw_wang(c, WX, GY + 6 * math.sin((T - tn) * 12) * (T >= tn), 0.95, mood="smile" if T >= tn else "flat")
        box(c, cx, hy + 100, 160, 120, "#FFFFFF", INK, 5, 6)
        K.text(c, "核对", cx, cy - 330, 66, "hand", BLUE, clamp01(g))
        if T >= tn:
            with K.at(c, WX + 130, cy - 120, 0, pop_scale(T - tn)):
                bubble_box(c, 0, 0, 340, 110, -1)
                K.text(c, "我也看到了", 0, 0, 50, "hand", GREEN)
        return None
    ev(j, k_pair, scene, "wood_low", 0.6)
    b.hit(j, k_nod, "ding", 0.8, "不是你一个人看见")


screen12()


# ================================================================ 屏 13：第三步：小李在会上递出一张卡：问题 + 办法
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_card = kq(j, wp(16, 1, 0.5), 1)
    k_fact = nx(j, wp(16, 2, 0.4), k_card)
    k_fix = nx(j, wp(16, 3, 0.4), k_fact)
    L.note("事实", "办法", "退货 38%", "换包装")

    def scene(c, kk, T):
        tc, tf, tx = tb(j, k_card), tb(j, k_fact), tb(j, k_fix)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with at_pop(c, cx - 380, GY, g):
            draw_li(c, cx - 380, GY, 0.9, "smile", rh=(cx - 260, GY - 300))
        draw_man(c, cx + 400, GY, 0.85, "gray", mood="flat" if T < tx else "smile")
        with K.at(c, cx, cy - 60, 0, g):
            box(c, 0, 0, 620, 420, "#FFFFFF", BLACK, 7, 14)
            if T >= tf:
                K.text(c, "事实", -180, -110, 52, "hand", RED, clamp01((T - tf) / 0.2))
                K.text(c, "退货 38%", 90, -110, 48, "hand", INK, clamp01((T - tf) / 0.2))
            if T >= tx:
                K.text(c, "办法", -180, 60, 52, "hand", GREEN, clamp01((T - tx) / 0.2))
                K.text(c, "换包装", 90, 60, 48, "hand", INK, clamp01((T - tx) / 0.2))
        return None
    ev(j, k_card, scene, "wood_high", 0.65)
    b.hit(j, k_fact, "pop", 0.7, "带上事实")
    b.hit(j, k_fix, "ding", 0.85, "也带上办法")


screen13()


# ================================================================ 屏 14：好处：红色报表摊在桌子中间，大家围过来
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_doc = kq(j, wp(17, 1, 0.4), 0)
    k_crowd = nx(j, wp(17, 3, 0.3), k_doc)
    L.note("被看见")

    def scene(c, kk, T):
        td, tc = tb(j, k_doc), tb(j, k_crowd)
        g = pop_scale(T - td)
        if g <= 0:
            return None
        with K.at(c, cx, GY - 140, 0, 1):
            box(c, 0, 0, 900, 30, "#E7D6BA", "#8B6B43", 6, 6)
        with K.at(c, cx, cy - 120, 0, g):
            box(c, 0, 0, 380, 300, "#FFFFFF", RED, 7, 6)
            C.line(c, (-130, 60), (-40, -20), RED, 9)
            C.line(c, (-40, -20), (40, 30), RED, 9)
            C.line(c, (40, 30), (130, 110), RED, 9)
        if T >= tc:
            for i, x in enumerate((cx - 380, cx - 160, cx + 160, cx + 380)):
                u = ease_out(clamp01((T - tc - i * 0.08) / 0.5))
                xx = lerp(x + (-200 if x < cx else 200), x, u)
                (draw_li if i == 1 else draw_wang if i == 2 else draw_man)(
                    c, xx, GY, 0.8, **({"mood": "smile"} if i in (1, 2) else {"color": "gray", "mood": "smile"}))
            with K.at(c, cx, cy - 420, 0, C.slam_scale(T - tc - 0.2)):
                chip(c, 0, 0, "被看见", GREEN_FILL, GREEN, 60)
        return None
    ev(j, k_doc, scene, "wood_low", 0.6)
    b.hit(j, k_crowd, "clap", 0.8, "问题早被看见")


screen14()


# ================================================================ 屏 15：评论区；雨停了，一把伞下小李攥着本子；下一讲预告
def enc(c, T, te, th, cx, cy):
    LX, LY = cx - 120, cy + 640
    stop = clamp01((T - th) / 0.8) if T >= th else 0
    if stop < 1:
        rain(c, cx - 560, cx + 560, cy + 180, cy + 700, T, 50, 0.6 * (1 - stop))
    hy = LY - 290 * 0.9
    with at_pop(c, LX, LY, pop_scale(T - te)):
        draw_li(c, LX, LY, 0.9, "smile", rh=(LX + 60, hy + 40))
        C.line(c, (LX + 60, hy + 40), (LX + 60, hy - 160), INK, 6)
        um = skia.Path()
        um.addArc(skia.Rect.MakeXYWH(LX + 60 - 170, hy - 260, 340, 200), 180, 180)
        um.close()
        c.drawPath(um, K.paint(RED_FILL))
        c.drawPath(um, wb.marker(RED, 6))
    if T >= th:
        sparkle(c, cx + 250, cy + 300, T - th, YELLOW, 10, 60, 180)
        K.text(c, "勇气", cx + 260, cy + 300, 70, "hand", GREEN, stop)


def scroll_icon(c, x, y, dt):
    with K.at(c, x, y, 0, pop_scale(dt)):
        N.parchment(c, 0, 0, 110, 130, 1.0, 1.0, 2)


L.note("勇气")
KT.ending(15, "被说成想多了，后来呢？", ["说了", "忍了", "走了"], 19, 20, enc, 21, ["一家人的命", "早就写好了吗？"],
          enc_piece=3, next_icon=scroll_icon)

# ================================================================ 收尾
L.finish(cover_shot=7, square_shot=5, notes=NOTES)
L.export(globals())
