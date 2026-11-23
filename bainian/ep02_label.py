"""《百年孤独》02 标签：忙到最后，为什么什么都记不住？（白板手绘 + AI 旁白，竖屏 2:3）

复刻实验：马孔多染上失眠症、开始失忆，奥雷里亚诺给每样东西写名字，后来写用途，镇口立起“马孔多”的牌子；
梅尔基亚德斯回来，父亲喝下药水，记忆回来了。照着这套办法给今天的我们做三件事。文案见 bainian/PLAN.md「### 02」。
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
                            at_pop, box, bubble_box, chip, draw_lady, draw_li, draw_man, house, jose, melquiades, name_tag,
                            phone, pop_scale, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "生活里", 1),
    ([2], "生活里", 2),
    ([3, 4], "书里的人", 3),
    ([5, 6], "失眠症", 4),
    ([7], "开始忘事", 5),
    ([8, 9], "贴标签", 6),
    ([10, 11], "写用途", 7),
    ([12, 13], "马孔多", 8),
    ([14], "记起来了", 9),
    ([15, 16], "说回我们", 10),
    ([17], "第一件", 11),
    ([18], "第二件", 12),
    ([19], "第三件", 13),
    ([20], "好处", 14),
    ([21, 22, 23, 24], "评论区见", 15),
]

THEME = BT.get("02")
L = N.Lesson("02", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(14)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》第 3 章（范晔译本）。情节为转述，不引原文。",
    "今人（小李、小王）为虚构示意；书中人造型为示意（一百多年前的加勒比小镇打扮）。",
]

REB = ("雷贝卡", "养女")
AUR = ("奥雷里亚诺", "第二代 · 次子")
JOSE = ("何塞·阿尔卡蒂奥·布恩迪亚", "第一代 · 父亲")


def tag(c, x, y, who, a=1.0, size=44):
    name_tag(c, x, y, who[0], "#5E4128", size, a, who[1])


def label(c, x, y, s, size=44, a=1.0, rot=0.0, fill="#FFFFFF"):
    """手写标签纸（白底、红线框）。"""
    w = K.text_w(s, size, "hand") + 36
    with K.at(c, x, y, rot):
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -size * 0.75, w, size * 1.5), K.paint(fill, a))
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -size * 0.75, w, size * 1.5), wb.marker(RED, 4, a))
        K.text(c, s, 0, 2, size, "hand", INK, a)


def memory(c, x, y, s, a=1.0, full=1.0, txt=None):
    """记忆气泡：full 1 满（淡黄）→ 0 空（虚线）。"""
    with K.at(c, x, y, 0, s):
        c.drawOval(skia.Rect.MakeXYWH(-110, -70, 220, 140), K.paint(NOTE_FILL, a * full))
        c.drawOval(skia.Rect.MakeXYWH(-110, -70, 220, 140), wb.marker(GRAY if full < 0.5 else ORANGE, 5, a))
        if txt:
            K.text(c, txt, 0, 0, 44, "hand", INK, a * full)


def cow(c, x, y, s=1.0, a=1.0):
    """奶牛（简笔）：(x, y) 脚底中点。"""
    with K.at(c, x, y, 0, s):
        for dx in (-70, -40, 40, 70):
            C.line(c, (dx, -80), (dx, 0), INK, 10, a)
        c.drawRoundRect(skia.Rect.MakeXYWH(-110, -190, 220, 120), 50, 50, K.paint("#FFFFFF", a))
        c.drawRoundRect(skia.Rect.MakeXYWH(-110, -190, 220, 120), 50, 50, wb.marker(INK, 6, a))
        for dx, dy, r in ((-50, -150, 26), (30, -120, 30), (70, -165, 18)):
            c.drawCircle(dx, dy, r, K.paint(INK, a))
        hd = skia.Rect.MakeXYWH(90, -250, 90, 80)
        c.drawRoundRect(hd, 30, 30, K.paint("#FFFFFF", a))
        c.drawRoundRect(hd, 30, 30, wb.marker(INK, 6, a))
        c.drawOval(skia.Rect.MakeXYWH(120, -205, 60, 36), K.paint("#F6C3BE", a))
        for dx in (96, 170):
            C.line(c, (dx, -248), (dx + (dx - 133) * 0.4, -278), INK, 7, a)
        c.drawCircle(120, -228, 5, K.paint(INK, a))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：小李举起手机，头顶的念头气泡破了；密码、日历、蛋糕三个图标打问号
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    LX = cx - 250
    k_li = kq(j, wp(0, 1, 0.3), 0)
    k_pop = nx(j, wp(0, 2, 0.4), k_li)
    k_icons = [nx(j, wp(1, 0, 0.5), k_pop)]
    k_icons.append(nx(j, wp(1, 1, 0.5), k_icons[0]))
    k_icons.append(nx(j, wp(1, 3, 0.3), k_icons[1]))
    L.note("回消息", "密码", "约好的事", "生日")

    def scene(c, kk, T):
        tl, tp = tb(j, k_li), tb(j, k_pop)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        hy = GY - 290
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "o" if T >= tp else "flat", rh=(LX + 120, hy + 40))
            phone(c, LX + 150, hy + 10, 0.7)
        if T < tp:
            memory(c, LX + 60, cy - 330, g, 1, 1, "回消息")
        else:
            f = clamp01((T - tp) / 0.25)
            if f < 1:
                memory(c, LX + 60, cy - 330, 1 + 0.3 * f, 1 - f, 1, "回消息")
            sparkle(c, LX + 60, cy - 330, T - tp, GRAY, 8, 40, 140)
        for i, (k_, s) in enumerate(zip(k_icons, ("密码", "约好的事", "生日"))):
            t0 = tb(j, k_)
            sc = pop_scale(T - t0)
            if sc <= 0:
                continue
            x, y = cx + 330, cy - 380 + i * 270
            with K.at(c, x, y, 0, sc):
                box(c, 0, 0, 380, 200, "#FFFFFF", BLUE, 6, 18)
                if i == 0:
                    K.text(c, "＊＊＊＊", 0, -30, 50, "hand", INK)
                elif i == 1:
                    for q in range(5):
                        c.drawRect(skia.Rect.MakeXYWH(-150 + q * 62, -60, 50, 50), wb.marker(GRAY, 3))
                else:
                    box(c, 0, -30, 120, 60, "#F6C3BE", RED, 4, 8)
                    C.line(c, (0, -62), (0, -96), ORANGE, 6)
                K.text(c, s, -40, 55, 44, "hand", BLUE)
                K.text(c, "？", 150, 40, 80, "hand", RED)
        return None
    ev(j, k_li, scene, "wood_high", 0.65)
    b.hit(j, k_pop, "pop", 0.85, "转头就忘")
    for k_ in k_icons:
        b.hit(j, k_, "wood_low", 0.65, "又一件记不住")


screen1()


# ================================================================ 屏 2（drop）：脑袋里塞满方块，最底下“妈妈生日”被挤掉
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    dk = L.drop_k()
    k_head = kq(j, wp(2, 0, 0.3), 0)
    k_full = nx(j, wp(2, 1, 0.4), k_head)
    BLK = ["开会", "报表", "群消息", "快递", "加班", "回电话", "改方案"]
    L.note(*BLK, "妈妈生日")

    def scene(c, kk, T):
        th, tf, td = tb(j, k_head), tb(j, k_full), tb(j, dk)
        g = pop_scale(T - th)
        if g <= 0:
            return None
        HX, HY = cx - 60, cy - 60
        with K.at(c, HX, HY, 0, g):
            c.drawCircle(0, 0, 400, K.paint("#FFFFFF"))
            c.drawCircle(0, 0, 400, wb.marker(BLACK, 10))
        n = len(BLK) if T >= tf else 3
        for i in range(n):
            t0 = th if i < 3 else tf + (i - 3) * 0.08
            sc = pop_scale(T - t0)
            if sc <= 0:
                continue
            x, y = HX - 190 + (i % 3) * 190, HY - 220 + (i // 3) * 140
            with K.at(c, x, y, (i % 2) * 6 - 3, sc):
                box(c, 0, 0, 180, 110, BLUE_FILL, BLUE, 5, 10)
                K.text(c, BLK[i], 0, 0, 40, "hand", BLUE)
        mx, my = HX + 20, HY + 230
        if T >= td:
            f = ease_in_out(clamp01((T - td) / 0.5))
            mx, my = lerp(mx, cx + 380, f), lerp(my, cy + 470, f)
        with K.at(c, mx, my, -6 if T >= td else 0, 1):
            box(c, 0, 0, 280, 110, RED_FILL, RED, 6, 10)
            K.text(c, "妈妈生日", 0, 0, 48, "hand", RED)
        return None
    ev(j, k_head, scene, "wood_low", 0.65)
    b.hit(j, k_full, "shaker", 0.75, "脑子塞满")
    b.hit(j, dk, "kick", 0.9, "最要紧的先丢了")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：绿皮书翻开；雷贝卡背着帆布袋走进马孔多
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(3, 0, 0.4), 0)
    k_town = nx(j, wp(3, 2, 0.3), k_book)
    k_reb = nx(j, wp(4, 1, 0.3), k_town)
    k_bag = nx(j, wp(4, 3, 0.3), k_reb)
    KT.book(j, k_book, x=cx - 360, y=cy - 300)
    L.note(*REB, "马孔多", "父母的骨头")

    def scene(c, kk, T):
        tt, tr, tbg = tb(j, k_town), tb(j, k_reb), tb(j, k_bag)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        for i, (hx, s_) in enumerate(((cx + 300, 0.5), (cx + 120, 0.42))):
            with K.at(c, hx, GY - 200 - i * 90, 0, s_ * pop_scale(T - tt - 0.1 * i)):
                house(c, 0, 0)
        with K.at(c, cx + 230, cy - 380, -3, g):
            box(c, 0, 0, 300, 100, "#FFFFFF", RED, 6, 12)
            K.text(c, "马孔多", 0, 2, 64, "serif_black", RED)
        if T >= tr:
            f = ease_out(clamp01((T - tr) / 1.0))
            RX = lerp(cx - 640, cx - 200, f)
            dy = 8 * abs(math.sin((T - tr) * 7)) * (1 - f)
            draw_lady(c, RX, GY - dy, 0.72, "green", hair="long", mood="flat", rh=(RX + 60, GY - 300 * 0.72))
            if T >= tbg:
                with K.at(c, RX + 60, GY - 230 * 0.72 - dy, 0, pop_scale(T - tbg)):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-10, -40, 110, 150), 30, 30, K.paint("#C9B48A"))
                    c.drawRoundRect(skia.Rect.MakeXYWH(-10, -40, 110, 150), 30, 30, wb.marker("#6E4E22", 5))
                K.text(c, "父母的骨头", RX + 260, GY - 60, 46, "hand", GRAY, clamp01((T - tbg) / 0.3))
            tag(c, RX, GY - 330, REB, clamp01(f * 3))
        return None
    ev(j, k_town, scene, "shaker", 0.6)
    b.hit(j, k_reb, "bongo_low", 0.75, "雷贝卡来了")
    b.hit(j, k_bag, "tom", 0.75, "一袋骨头")


screen3()


# ================================================================ 屏 4：一排房子的窗户夜里都亮着；人们笑着加班
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_night = kq(j, wp(5, 0, 0.4), 0)
    k_awake = nx(j, wp(5, 1, 0.4), k_night)
    k_happy = nx(j, wp(6, 0, 0.5), k_awake)
    k_work = nx(j, wp(6, 2, 0.3), k_happy)
    L.note("睡不着", "多干活")

    def scene(c, kk, T):
        tn, ta, th, tw = (tb(j, k) for k in (k_night, k_awake, k_happy, k_work))
        g = pop_scale(T - tn)
        if g <= 0:
            return None
        c.drawCircle(cx + 420, cy - 440, 70 * g, K.paint("#F6E7A6"))
        c.drawCircle(cx + 450, cy - 460, 60 * g, K.paint(N.PARCH))
        for i in range(3):
            hx = cx - 360 + i * 340
            with K.at(c, hx, cy - 60, 0, 0.55 * pop_scale(T - tn - 0.1 * i)):
                house(c, 0, 0)
                if T >= ta + 0.1 * i:
                    for sg in (-1, 1):
                        c.drawRect(skia.Rect.MakeXYWH(sg * 126 - 40, -210, 80, 70), K.paint(YELLOW))
        if T >= ta:
            K.text(c, "睡不着", cx - 330, cy - 420, 60, "hand", BLUE, clamp01((T - ta) / 0.3))
        if T >= th:
            for i in range(3):
                px = cx - 380 + i * 330
                s_ = pop_scale(T - th - 0.1 * i)
                swing = 30 * math.sin((T - tw) * 6 + i) if T >= tw else 0
                with at_pop(c, px, GY, s_):
                    draw_man(c, px, GY, 0.72, ("white", "ochre", "green")[i], hat="straw" if i != 1 else None,
                             mood="laugh", rh=(px + 90, GY - 330 + swing))
                    C.line(c, (px + 90, GY - 330 + swing), (px + 150, GY - 140 + swing), "#6E4E22", 8)
            if T >= tw:
                with K.at(c, cx + 300, cy + 120, 4, C.slam_scale(T - tw)):
                    chip(c, 0, 0, "多干活", NOTE_FILL, ORANGE, 56)
        return None
    ev(j, k_night, scene, "wood_low", 0.6)
    b.hit(j, k_awake, "pop", 0.7, "窗户全亮")
    b.hit(j, k_happy, "clap", 0.7, "大家挺高兴")
    b.hit(j, k_work, "bongo_high", 0.75, "多干活")


screen4()


# ================================================================ 屏 5：记忆气泡一个个变空：小时候、名字
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_ppl = kq(j, wp(7, 0, 0.4), 0)
    k_kid = nx(j, wp(7, 2, 0.4), k_ppl)
    k_name = nx(j, wp(7, 3, 0.5), k_kid)
    L.note("小时候", "这叫什么？")

    def scene(c, kk, T):
        tp, tk, tn = tb(j, k_ppl), tb(j, k_kid), tb(j, k_name)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        PX = cx - 220
        with at_pop(c, PX, GY, g):
            draw_man(c, PX, GY, 1.0, "white", hat="straw", mood="o" if T >= tn else "flat", rh=(PX + 140, GY - 330))
        fk = 1 - clamp01((T - tk) / 0.5) if T >= tk else 1
        memory(c, PX - 150, cy - 330, g, 1, fk, "小时候")
        if T >= tk and fk < 1:
            K.text(c, "？", PX - 150, cy - 330, 70, "hand", GRAY, 1 - fk)
        CX, CY = cx + 300, GY - 120
        with K.at(c, CX, CY, 0, g):
            box(c, 0, 0, 260, 26, "#E7D6BA", "#8B6B43", 6, 6)
            for sg in (-1, 1):
                C.line(c, (sg * 110, 13), (sg * 110, 140), "#8B6B43", 8)
        if T >= tn:
            with K.at(c, CX, CY - 200, 0, pop_scale(T - tn)):
                bubble_box(c, 0, 0, 340, 110, -1)
                K.text(c, "这叫什么？", 0, 0, 52, "hand", RED)
        return None
    ev(j, k_ppl, scene, "wood_low", 0.6)
    b.hit(j, k_kid, "shaker", 0.7, "忘了小时候")
    b.hit(j, k_name, "rim", 0.8, "忘了东西叫什么")


screen5()


# ================================================================ 屏 6：奥雷里亚诺拿小刷子写字；桌子、椅子、钟、门、床、锅贴上标签
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_aur = kq(j, wp(8, 0, 0.3), 0)
    k_brush = nx(j, wp(8, 2, 0.4), k_aur)
    k_labels = [nx(j, wp(9, 0, 0.3), k_brush)]
    k_labels.append(nx(j, wp(9, 1, 0.4), k_labels[0]))
    k_all = nx(j, wp(9, 2, 0.4), k_labels[1])
    OBJ = [("桌子", cx + 80, cy + 260), ("椅子", cx + 380, cy + 300), ("钟", cx + 380, cy - 300),
           ("门", cx + 80, cy - 260), ("床", cx - 120, cy + 380), ("锅", cx - 400, cy - 300)]
    L.note(*AUR, *(o[0] for o in OBJ), "标签")

    def scene(c, kk, T):
        ta, tbr, ta2 = tb(j, k_aur), tb(j, k_brush), tb(j, k_all)
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        AX = cx - 330
        wr = 20 * math.sin((T - tbr) * 10) if T >= tbr else 0
        with at_pop(c, AX, GY, g):
            draw_man(c, AX, GY, 0.95, "red", mood="flat", rh=(AX + 150, GY - 300 + wr))
            if T >= tbr:
                C.line(c, (AX + 150, GY - 300 + wr), (AX + 210, GY - 360 + wr), "#6E4E22", 8)
                c.drawCircle(AX + 214, GY - 364 + wr, 12, K.paint(INK))
        tag(c, AX, GY - 470, AUR, clamp01(g), 40)
        for i, (s, x, y) in enumerate(OBJ):
            t0 = tb(j, k_labels[0]) + i * 0.12 if i < 3 else tb(j, k_labels[1]) + (i - 3) * 0.12
            sc = pop_scale(T - t0)
            if sc <= 0:
                continue
            with K.at(c, x, y, 0, sc):
                if s == "桌子":
                    box(c, 0, 0, 220, 22, "#E7D6BA", "#8B6B43", 5, 4)
                    for sg in (-1, 1):
                        C.line(c, (sg * 90, 11), (sg * 90, 110), "#8B6B43", 7)
                elif s == "椅子":
                    C.line(c, (-50, -120), (-50, 100), "#8B6B43", 8)
                    C.line(c, (-50, 10), (60, 10), "#8B6B43", 8)
                    C.line(c, (60, 10), (60, 100), "#8B6B43", 8)
                elif s == "钟":
                    c.drawCircle(0, 0, 70, K.paint("#FFFFFF"))
                    c.drawCircle(0, 0, 70, wb.marker(INK, 6))
                    C.line(c, (0, 0), (0, -46), INK, 6)
                    C.line(c, (0, 0), (34, 10), INK, 6)
                elif s == "门":
                    box(c, 0, 0, 130, 200, "#B5562E", "#5E2E18", 6, 6)
                    c.drawCircle(40, 10, 9, K.paint(YELLOW))
                elif s == "床":
                    box(c, 0, 20, 260, 50, "#FFFFFF", INK, 5, 8)
                    box(c, -110, -20, 40, 110, "#E7D6BA", "#8B6B43", 5, 4)
                else:
                    c.drawOval(skia.Rect.MakeXYWH(-80, -20, 160, 80), K.paint("#5E5E58"))
                    C.line(c, (80, 10), (150, -10), INK, 8)
                label(c, 0, -110 if s != "床" else -80, s, 44, 1.0, (i % 2) * 6 - 3)
        if T >= ta2:
            with K.at(c, cx + 100, cy - 500, -2, C.slam_scale(T - ta2)):
                chip(c, 0, 0, "全贴上标签", RED_FILL, RED, 52)
        return None
    L.note("全贴上标签")
    ev(j, k_aur, scene, "bongo_low", 0.7)
    b.hit(j, k_brush, "shaker", 0.7, "蘸墨水写字")
    for k_ in k_labels:
        b.hit(j, k_, "pop", 0.75, "贴标签")
    b.hit(j, k_all, "kick", 0.8, "全贴上了")


screen6()


# ================================================================ 屏 7：奶牛脖子上挂着牌子，字一行行写出来
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_name = kq(j, wp(10, 0, 0.5), 0)
    k_use = nx(j, wp(10, 2, 0.4), k_name)
    k_cow = nx(j, wp(11, 0, 0.4), k_use)
    k_l1 = nx(j, wp(11, 2, 0.3), k_cow)
    k_l2 = nx(j, wp(11, 3, 0.3), k_l1)
    L.note("名字", "用途", "这是奶牛", "每天早上要挤奶")

    def scene(c, kk, T):
        tn, tu, tc, t1, t2 = (tb(j, k) for k in (k_name, k_use, k_cow, k_l1, k_l2))
        g = pop_scale(T - tn)
        if g <= 0:
            return None
        if T < tc:
            with K.at(c, cx - 230, cy - 200, -3, g):
                label(c, 0, 0, "名字", 70)
            if T >= tu:
                with K.at(c, cx + 230, cy - 200, 3, C.slam_scale(T - tu)):
                    label(c, 0, 0, "用途", 70, fill=NOTE_FILL)
                C.line(c, (cx - 80, cy - 200), (cx + 80, cy - 200), INK, 8)
            return None
        s_ = pop_scale(T - tc)
        with at_pop(c, cx - 120, GY - 20, s_):
            cow(c, cx - 120, GY - 20, 1.7)
        SX, SY = cx + 230, cy - 330
        C.line(c, (cx + 70, GY - 20 - 250 * 1.7 + 80), (SX, SY - 80), INK, 4)
        with K.at(c, SX, SY, 4, s_):
            box(c, 0, 60, 520, 260, "#FFFFFF", "#8B6B43", 7, 10)
            if T >= t1:
                K.text(c, "这是奶牛", 0, 10, 62, "hand", INK, clamp01((T - t1) / 0.3))
            if T >= t2:
                K.text(c, "每天早上要挤奶", 0, 110, 52, "hand", RED, clamp01((T - t2) / 0.3))
        return None
    ev(j, k_name, scene, "pop", 0.7)
    b.hit(j, k_use, "rim", 0.8, "还得写用途")
    b.hit(j, k_cow, "bongo_low", 0.75, "奶牛")
    b.hit(j, k_l1, "wood_high", 0.65, "这是奶牛")
    b.hit(j, k_l2, "ding", 0.75, "每天早上要挤奶")


screen7()


# ================================================================ 屏 8：镇口立起大牌子“马孔多”；满街都是字
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_post = kq(j, wp(12, 1, 0.4), 0)
    k_sign = nx(j, wp(12, 2, 0.3), k_post)
    k_words = nx(j, wp(13, 0, 0.5), k_sign)
    k_go = nx(j, wp(13, 1, 0.4), k_words)
    L.note("马孔多", "井", "树", "路", "家")

    def scene(c, kk, T):
        tp, ts, tw, tg = (tb(j, k) for k in (k_post, k_sign, k_words, k_go))
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        SX = cx - 150
        for sg in (-1, 1):
            C.line(c, (SX + sg * 220, GY), (SX + sg * 220, cy - 120), "#6E4E22", 18)
        if T >= ts:
            with K.at(c, SX, cy - 250, 0, C.slam_scale(T - ts)):
                box(c, 0, 0, 640, 220, "#F7EFD9", "#6E4E22", 9, 10)
                K.text(c, "马孔多", 0, 4, 130, "serif_black", RED)
        if T >= tw:
            for i, (s, x, y) in enumerate((("井", cx + 320, cy + 330), ("树", cx + 420, cy - 20), ("路", cx - 450, cy + 380),
                                            ("家", cx + 240, cy - 420))):
                sc = pop_scale(T - tw - i * 0.1)
                if sc > 0:
                    with K.at(c, x, y, (i % 2) * 8 - 4, sc):
                        label(c, 0, 0, s, 50)
        if T >= tg:
            for i in range(2):
                px = lerp(cx - 640, cx + 120, ease_in_out(clamp01((T - tg - i * 0.3) / 1.4))) - i * 150
                dy = 8 * abs(math.sin((T - tg) * 7 + i))
                if i == 0:
                    draw_man(c, px, GY - dy, 0.62, "white", hat="straw", mood="smile")
                else:
                    draw_lady(c, px, GY - dy, 0.6, "yellow", hair="bun", mood="smile")
        return None
    ev(j, k_post, scene, "wood_low", 0.65)
    b.hit(j, k_sign, "kick", 0.85, "马孔多")
    b.hit(j, k_words, "pop", 0.7, "满街都是字")
    b.hit(j, k_go, "shaker", 0.65, "日子撑下去")


screen8()


# ================================================================ 屏 9：梅尔基亚德斯递上药水，父亲喝下，头顶的气泡重新亮起
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_mel = kq(j, wp(14, 1, 0.3), 0)
    k_give = nx(j, wp(14, 2, 0.4), k_mel)
    k_drink = nx(j, wp(14, 3, 0.4), k_give)
    k_back = nx(j, wp(14, 4, 0.3), k_drink)
    L.note("梅尔基亚德斯", *JOSE, "记起来了")
    MX, JX = cx - 300, cx + 280

    def scene(c, kk, T):
        tm, tg, td, tbk = (tb(j, k) for k in (k_mel, k_give, k_drink, k_back))
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        with at_pop(c, MX, GY, g):
            melquiades(c, MX, GY, 1.0, mood="smile", rh=(MX + 160, GY - 260) if tg <= T < td else None)
        name_tag(c, MX, GY - 500, "梅尔基亚德斯", "#3A3A3A", 42, clamp01(g))
        back = T >= tbk
        with at_pop(c, JX, GY, g):
            jose(c, JX, GY, 1.0, mood="laugh" if back else "flat", lh=(JX - 60, GY - 300) if T >= td else None)
        name_tag(c, JX - 40, GY - 520, JOSE[0], "#5E4128", 38, clamp01(g), JOSE[1])
        if T >= tg:
            px, py = (MX + 180, GY - 270) if T < td else (JX - 50, GY - 310)
            with K.at(c, px, py, 0, pop_scale(T - tg)):
                c.drawRoundRect(skia.Rect.MakeXYWH(-24, -60, 48, 80), 14, 14, K.paint("#9FD3C7"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-24, -60, 48, 80), 14, 14, wb.marker(INK, 4))
                c.drawRect(skia.Rect.MakeXYWH(-10, -82, 20, 24), K.paint("#8A6A3A"))
        if T >= td:
            full = clamp01((T - tbk) / 0.5) if back else 0
            memory(c, JX + 60, cy - 300, pop_scale(T - td), 1, full, "记起来了" if back else None)
            if back:
                sparkle(c, JX + 60, cy - 300, T - tbk, YELLOW, 10, 100, 220)
        return None
    ev(j, k_mel, scene, "bongo_high", 0.75)
    b.hit(j, k_give, "pop", 0.7, "递上药水")
    b.hit(j, k_drink, "wood_high", 0.65, "喝下去")
    b.hit(j, k_back, "ding", 0.85, "记忆回来")


screen9()


# ================================================================ 屏 10：小李脑袋里的方块搬到墙上的便利贴；大字“三件事”
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = kq(j, wp(15, 0, 0.4), 0)
    k_move = nx(j, wp(15, 2, 0.3), k_li)
    k_three = nx(j, wp(16, 1, 0.4), k_move)
    L.note("三件事")
    LX = cx - 300

    def scene(c, kk, T):
        tl, tm, t3 = tb(j, k_li), tb(j, k_move), tb(j, k_three)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 1.0, "smile" if T >= tm else "sad")
        box(c, cx + 300, cy - 220, 440, 520, "#FFFFFF", GRAY, 5, 10)
        for i in range(4):
            sx, sy = LX - 40 + (i % 2) * 90, GY - 380 - (i // 2) * 70
            ex, ey = cx + 200 + (i % 2) * 200, cy - 340 + (i // 2) * 220
            f = ease_in_out(clamp01((T - tm - i * 0.15) / 0.6)) if T >= tm else 0
            with K.at(c, lerp(sx, ex, f), lerp(sy, ey, f), (i % 2) * 6 - 3, lerp(0.5, 1.0, f)):
                box(c, 0, 0, 150, 150, (N.NOTE_FILL, BLUE_FILL)[i % 2], (ORANGE, BLUE)[i % 2], 5, 6)
        if T >= t3:
            with K.at(c, cx, cy + 300, -3, C.slam_scale(T - t3)):
                K.text(c, "三件事", 0, 0, 140, "hand", RED)
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_move, "shaker", 0.7, "搬到墙上")
    b.hit(j, k_three, "kick", 0.85, "三件事")


screen10()


# ================================================================ 屏 11：第一件：便利贴贴在电脑屏幕边，一抬头就看见
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_desk = kq(j, wp(17, 0, 0.6), 1)
    k_write = nx(j, wp(17, 1, 0.5), k_desk)
    k_stick = nx(j, wp(17, 2, 0.5), k_write)
    k_see = nx(j, wp(17, 3, 0.3), k_stick)
    L.note("贴标签", "交电费", "回王姐消息")

    def scene(c, kk, T):
        td, tw, ts, tse = (tb(j, k) for k in (k_desk, k_write, k_stick, k_see))
        g = pop_scale(T - td)
        if g <= 0:
            return None
        with at_pop(c, cx + 120, GY - 220, g):
            N.desk(c, cx + 120, GY - 220, 600, 26, laptop=False)
            box(c, cx + 120, GY - 470, 420, 280, "#E9EEF4", BLACK, 7, 12)
        with at_pop(c, cx - 380, GY, g):
            draw_li(c, cx - 380, GY, 0.95, "smile" if T >= tse else "flat",
                    rh=(cx - 260, GY - 380) if tw <= T < ts else None)
        for i, s in enumerate(("交电费", "回王姐消息")):
            if T < tw + i * 0.2:
                continue
            f = ease_out(clamp01((T - ts - i * 0.2) / 0.4)) if T >= ts else 0
            x = lerp(cx - 220, cx + 420, f)
            y = lerp(cy - 360 + i * 30, cy - 160 + i * 170, f)
            with K.at(c, x, y, (i * 2 - 1) * 5, pop_scale(T - tw - i * 0.2)):
                box(c, 0, 0, 250, 130, NOTE_FILL, ORANGE, 5, 6)
                K.text(c, s, 0, 0, 40 if i else 46, "hand", INK)
        if T >= tse:
            c.drawPath(P((cx - 340, GY - 300), (cx + 280, cy - 100)), wb.marker(YELLOW, 10, 0.7))
            with K.at(c, cx + 300, cy + 420, 0, C.slam_scale(T - tse)):
                chip(c, 0, 0, "贴标签", GREEN_FILL, GREEN, 56)
        return None
    ev(j, k_desk, scene, "wood_high", 0.65)
    b.hit(j, k_write, "pop", 0.7, "写下来")
    b.hit(j, k_stick, "shaker", 0.7, "贴到屏幕边")
    b.hit(j, k_see, "ding", 0.8, "一抬头就看见")


screen11()


# ================================================================ 屏 12：第二件：便利贴从“交电费”改成“周五前 · 手机交”
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    k_note = kq(j, wp(18, 1, 0.4), 1)
    k_fri = nx(j, wp(18, 2, 0.4), k_note)
    k_ph = nx(j, wp(18, 3, 0.3), k_fri)
    L.note("写用途", "交电费", "周五前", "用手机交")

    def scene(c, kk, T):
        tn, tf, tp = tb(j, k_note), tb(j, k_fri), tb(j, k_ph)
        g = pop_scale(T - tn)
        if g <= 0:
            return None
        with K.at(c, cx - 40, cy - 40, -3, g):
            box(c, 0, 0, 600, 560, NOTE_FILL, ORANGE, 7, 8)
            K.text(c, "交电费", 0, -150, 90, "hand", INK)
            if T >= tf:
                K.text(c, "周五前", 0, 0, 80, "hand", RED, clamp01((T - tf) / 0.25))
                c.drawPath(wb.underline(-150, 150, 60, 10, 40), wb.marker(RED, 6))
            if T >= tp:
                K.text(c, "用手机交", 0, 150, 76, "hand", BLUE, clamp01((T - tp) / 0.25))
        if T >= tp:
            with K.at(c, cx + 380, cy + 300, 8, pop_scale(T - tp)):
                phone(c, 0, 0, 1.0)
            with K.at(c, cx - 300, cy + 380, -2, C.slam_scale(T - tp - 0.15)):
                chip(c, 0, 0, "写用途", GREEN_FILL, GREEN, 56)
        return None
    ev(j, k_note, scene, "pop", 0.7)
    b.hit(j, k_fri, "rim", 0.8, "周五前")
    b.hit(j, k_ph, "ding", 0.8, "用手机交")


screen12()


# ================================================================ 屏 13：第三件：日历上每周日圈一格，电话响起
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    k_cal = kq(j, wp(19, 1, 0.4), 1)
    k_ring = nx(j, wp(19, 2, 0.5), k_cal)
    k_call = nx(j, wp(19, 3, 0.4), k_ring)
    L.note("立牌子", "日", "家")

    def scene(c, kk, T):
        tc, tr, tl = tb(j, k_cal), tb(j, k_ring), tb(j, k_call)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 120, 0, g):
            box(c, 0, 0, 840, 500, "#FFFFFF", BLACK, 7, 12)
            c.drawRect(skia.Rect.MakeXYWH(-420, -250, 840, 90), K.paint(RED_FILL))
            for r in range(3):
                for q in range(7):
                    x, y = -360 + q * 120, -100 + r * 110
                    box(c, x, y, 100, 90, "#FFFFFF", GRAY, 3, 6)
                    if q == 6 and T >= tr + r * 0.15:
                        ring = skia.Path()
                        ring.addOval(skia.Rect.MakeXYWH(x - 50, y - 46, 100, 92))
                        c.drawPath(wb.partial(ring, ease_out(clamp01((T - tr - r * 0.15) / 0.3)))[0], wb.marker(RED, 7))
            K.text(c, "日", 360, -205, 50, "hand", RED)
        if T >= tl:
            sh = 8 * math.sin((T - tl) * 40) * max(0, 1 - (T - tl) / 0.8)
            with K.at(c, cx - 200 + sh, cy + 360, 0, pop_scale(T - tl)):
                c.drawRoundRect(skia.Rect.MakeXYWH(-90, -40, 180, 80), 40, 40, K.paint(GREEN))
                K.text(c, "家", 0, 2, 50, "hand", "#FFFFFF")
            for q in range(3):
                C.line(c, (cx - 80 + q * 30, cy + 300 - q * 20), (cx - 50 + q * 30, cy + 280 - q * 20), GREEN, 6)
            with K.at(c, cx + 250, cy + 360, 3, C.slam_scale(T - tl - 0.15)):
                chip(c, 0, 0, "立牌子", GREEN_FILL, GREEN, 56)
        return None
    ev(j, k_cal, scene, "wood_high", 0.65)
    b.hit(j, k_ring, "pop", 0.75, "每周圈一天")
    b.hit(j, k_call, "ding", 0.8, "给家里打电话")


screen13()


# ================================================================ 屏 14：好处：脑袋里空出一块地方，亮起“妈妈”
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_head = kq(j, wp(20, 0, 0.6), 0)
    k_mom = nx(j, wp(20, 1, 0.5), k_head)
    k_keep = nx(j, wp(20, 2, 0.4), k_mom)
    L.note("妈妈", "丢不了")

    def scene(c, kk, T):
        th, tm, tk = tb(j, k_head), tb(j, k_mom), tb(j, k_keep)
        g = pop_scale(T - th)
        if g <= 0:
            return None
        HX, HY = cx, cy - 80
        with K.at(c, HX, HY, 0, g):
            c.drawCircle(0, 0, 400, K.paint("#FFFFFF"))
            c.drawCircle(0, 0, 400, wb.marker(BLACK, 10))
            for i in range(2):
                box(c, -150 + i * 300, -200, 180, 100, BLUE_FILL, BLUE, 5, 10)
        if T >= tm:
            with K.at(c, HX, HY + 60, 0, C.slam_scale(T - tm)):
                c.drawPath(C.heart_path(0, 0, 110), K.paint(RED_FILL))
                c.drawPath(C.heart_path(0, 0, 110), wb.marker(RED, 7))
                K.text(c, "妈妈", 0, 10, 70, "hand", RED)
            sparkle(c, HX, HY + 60, T - tm, YELLOW, 10, 130, 260)
        if T >= tk:
            with K.at(c, HX, cy + 480, -2, C.slam_scale(T - tk)):
                chip(c, 0, 0, "丢不了", GREEN_FILL, GREEN, 64)
        return None
    ev(j, k_head, scene, "wood_low", 0.6)
    b.hit(j, k_mom, "ding", 0.85, "要紧的人")
    b.hit(j, k_keep, "kick", 0.8, "丢不了")


screen14()


# ================================================================ 屏 15：评论区；一张标签贴在心口；下一讲预告
def enc(c, T, te, th, cx, cy):
    LX, LY = cx - 200, cy + 640
    with at_pop(c, LX, LY, pop_scale(T - te)):
        draw_li(c, LX, LY, 0.9, "smile")
    if T >= th:
        hy = LY - 290 * 0.9
        with K.at(c, LX, hy + 120, -6, C.slam_scale(T - th)):
            label(c, 0, 0, "在乎", 40, fill=NOTE_FILL)
        sparkle(c, LX, hy + 120, T - th, YELLOW, 10, 80, 200)
        with K.at(c, cx + 280, cy + 420, 0, pop_scale(T - th - 0.1)):
            box(c, 0, 0, 300, 180, "#FFFFFF", BLACK, 6, 12)
            for q in range(3):
                C.line(c, (-110, -50 + q * 50), (110 - q * 30, -50 + q * 50), GRAY, 6)
            K.text(c, "写下来", 0, 130, 46, "hand", RED)


def bandage_icon(c, x, y, dt):
    with K.at(c, x, y, -10, pop_scale(dt)):
        c.drawRoundRect(skia.Rect.MakeXYWH(-50, -70, 100, 140), 40, 40, K.paint("#FFFFFF"))
        c.drawRoundRect(skia.Rect.MakeXYWH(-50, -70, 100, 140), 40, 40, wb.marker(BLACK, 5))
        c.drawRect(skia.Rect.MakeXYWH(-54, -10, 108, 46), K.paint("#1E1E1E"))


L.note("在乎", "写下来")
KT.ending(15, "最近忘了什么事？", ["回消息", "生日", "密码"], 22, 23, enc, 24, ["明明在乎", "为什么总把人推开？"],
          enc_piece=2, next_icon=bandage_icon)

# ================================================================ 收尾
L.finish(cover_shot=6, square_shot=7, notes=NOTES)
L.export(globals())
