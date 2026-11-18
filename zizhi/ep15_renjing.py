"""《资治通鉴》15 以人为镜：谁来告诉你，你哪里错了？（季终；白板手绘 + AI 旁白，竖屏 2:3）

经典问答 + 季终：先是“只会点头的镜子”；魏征常当面指出太宗的错，太宗下朝要杀“田舍翁”，长孙皇后换朝服道贺“主明臣直”，太宗气消；
魏征去世后太宗的三面镜子（铜镜、古镜、人镜），“魏征没，朕亡一镜矣”；三步找一面人镜；回看这一季十五讲；评论区、借前人的路走、
愿你身边有一面敢说真话的镜子，下一季见。唐人戴幞头。文案见 zizhi/PLAN.md「### 15」。
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
                          RED_FILL, YELLOW, at_pop, bamboo_slips, box, bubble_box, chip, desk, draw_ace, draw_li, draw_wang, gu,
                          name_tag, pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "通鉴里的故事", 4),
    ([6, 7], "主明臣直", 5),
    ([8], "气消了", 6),
    ([9, 10], "三面镜子", 7),
    ([11, 12], "说回我们自己", 8),
    ([13], "第一步", 9),
    ([14], "第二步", 10),
    ([15], "第三步", 11),
    ([16], "好处", 12),
    ([17, 18], "第一季回看", 13),
    ([19, 20, 21, 22, 23], "季终", 14),
]

THEME = ZT.get("15")
L = Z.Lesson("15", SCREENS, drop_screen=2, board_size=(5000, 10400), theme=THEME,
             trim_head={7: 0.18})         # 第 7 句句首碎音（上一句“佬”的尾音，识别成“老”），裁掉
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(13)]
Z_ = 0.72
KT = Z.Kit(L, R)

NOTES = [
    "出处：司马光《资治通鉴》卷一九四 唐纪十（贞观六年，卷次待核）“会须杀此田舍翁”与长孙皇后道贺；卷一九六 唐纪十二（贞观十七年）三镜之语。",
    "原文：上尝罢朝，怒曰“会须杀此田舍翁”……后退，具朝服立于庭……“妾闻主明臣直；今魏征直，由陛下之明故也，妾敢不贺！”上乃悦。"
    "“人以铜为镜，可以正衣冠；以古为镜，可以见兴替；以人为镜，可以知得失。魏征没，朕亡一镜矣！”",
    "今人（小李、小王、同事）为虚构示意；古人造型为示意（唐人戴幞头）。",
]

TANG, WEI, QUEEN = "ochre", "teal", "red"
SEASON = ["才与德", "立信", "纸上谈兵", "将相和", "约法三章", "三不如", "萧规曹随", "不翻旧账", "三顾", "劝学", "有志者",
          "投鞭断流", "用人如器", "兼听", "以人为镜"]


def mirror(c, x, y, w=280, h=460, a=1.0, frame="#8A6A3A"):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), w / 2, w / 2, K.paint("#E8EEF8", a))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), w / 2, w / 2, wb.marker(frame, 10, a))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：同事们围着方案竖大拇指；交上去后漏洞一个个冒出来
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_doc = kq(j, wp(0, 1, 0.4), 0)
    k_ok = nx(j, wp(0, 2, 0.4), k_doc)
    k_submit = nx(j, wp(1, 0, 0.5), k_ok)
    k_holes = nx(j, wp(1, 1, 0.5), k_submit)
    L.note("方案", "挺好")

    def scene(c, kk, T):
        td, to, ts, th = tb(j, k_doc), tb(j, k_ok), tb(j, k_submit), tb(j, k_holes)
        g = pop_scale(T - td)
        if g <= 0:
            return None
        f = ease_in_out(clamp01((T - ts) / 0.5)) if T >= ts else 0
        with K.at(c, lerp(cx - 120, cx + 220, f), lerp(cy - 250, cy - 330, f), 0, g):
            box(c, 0, 0, 340, 260, "#FFFFFF", BLUE, 7, 10)
            K.text(c, "方案", 0, -80, 52, "sans_medium", BLUE)
            for q in range(2):
                C.line(c, (-120, 0 + q * 50), (120 - q * 40, 0 + q * 50), GRAY, 5)
            if T >= th:
                for i, (hx, hy) in enumerate(((-90, -20), (60, 30), (-30, 90), (110, -60))):
                    gg = pop_scale(T - th - i * 0.1)
                    c.drawCircle(hx, hy, 22 * gg, K.paint(RED))
        for i, x in enumerate((cx - 400, cx - 200, cx + 380)):
            with at_pop(c, x, GY, g):
                if i == 1:
                    draw_wang(c, x, GY, 0.8, mood="smile", rh=(x + 80, GY - 280) if T >= to else None)
                elif i == 0:
                    draw_ace(c, x, GY, 0.8, mood="smile", rh=(x + 80, GY - 280) if T >= to else None)
                else:
                    draw_li(c, x, GY, 0.9, "sad" if T >= th else "smile")
        if T >= to and T < ts + 0.3:
            K.text(c, "挺好", cx - 300, cy + 20, 60, "hand", GREEN, clamp01((T - to) / 0.2))
        return None
    ev(j, k_doc, scene, "wood_high", 0.6)
    b.hit(j, k_ok, "clap", 0.75, "大家都说挺好")
    b.hit(j, k_submit, "shaker", 0.65, "交上去")
    b.hit(j, k_holes, "rim", 0.85, "漏洞一大堆")


screen1()


# ================================================================ 屏 2（drop）：两边都怕：同事捂嘴、小李捂耳朵
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_mouth = kq(j, wp(2, 0, 0.5), 0)
    L.note("怕得罪", "怕难听")

    def scene(c, kk, T):
        tm, td = tb(j, k_mouth), tb(j, dk)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        AX, LX = cx - 300, cx + 300
        hyA = GY - 290 * 0.95
        with at_pop(c, AX, GY, g):
            draw_wang(c, AX, GY, 0.95, mood="flat", lh=(AX - 20, hyA + 30), rh=(AX + 20, hyA + 30))
        K.text(c, "怕得罪", AX, cy - 120, 54, "hand", GRAY, clamp01(g))
        if T >= td:
            with at_pop(c, LX, GY, pop_scale(T - td + 0.2)):
                draw_li(c, LX, GY, 0.95, "sad", lh=(LX - 50, hyA), rh=(LX + 50, hyA))
            with K.at(c, LX, cy - 120, 0, C.slam_scale(T - td)):
                chip(c, 0, 0, "怕难听", RED_FILL, RED, 54)
        return None
    ev(j, k_mouth, scene, "wood_low", 0.6)
    b.hit(j, dk, "kick", 0.9, "你也怕难听的话")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：一面只会点头的镜子
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_m = kq(j, wp(3, 1, 0.4), 0)
    k_nod = nx(j, wp(3, 2, 0.4), k_m)
    L.note("只会点头")
    MX = cx + 150

    def scene(c, kk, T):
        tm, tn = tb(j, k_m), tb(j, k_nod)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        with at_pop(c, cx - 330, GY, g):
            draw_li(c, cx - 330, GY, 0.95, "flat")
        mirror(c, MX, cy - 80, 380, 700, clamp01(g))
        nod = 14 * abs(math.sin((T - tn) * 7)) if T >= tn else 0
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(MX - 190, cy - 430, 380, 700), 190, 190))
        draw_li(c, MX, cy + 220 + nod * 0.3, 0.85, "smile", alpha=0.6)
        c.restore()
        if T >= tn:
            K.text(c, "只会点头", MX, cy + 380, 60, "hand", ORANGE, clamp01((T - tn) / 0.2))
        return None
    ev(j, k_m, scene, "wood_low", 0.6)
    b.hit(j, k_nod, "pop", 0.8, "只会点头")


screen3()


# ================================================================ 屏 4：竹简“资治通鉴”；魏征当面指出太宗的错，太宗脸红
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_book = kq(j, wp(4, 0, 0.5), 0)
    k_wei = nx(j, wp(4, 3, 0.3), k_book)
    k_point = nx(j, wp(5, 1, 0.4), k_wei)
    k_red = nx(j, wp(5, 3, 0.4), k_point)
    KT.book(j, k_book, "卷一九四", "唐纪十")
    L.note("唐太宗", "魏征", "镜子")

    def scene(c, kk, T):
        tw, tp, tr = tb(j, k_wei), tb(j, k_point), tb(j, k_red)
        g = pop_scale(T - tw)
        if g <= 0:
            return None
        TX, WX = cx + 80, cx + 400
        with at_pop(c, TX, GY, g):
            gu(c, TX, GY, 0.85, TANG, hat="futou", beard="black", mood="sad" if T >= tr else "flat")
            name_tag(c, TX, GY - 420, "唐太宗", "#8A5A1E", 34)
            if T >= tr:
                hy = GY - 290 * 0.85
                for sg in (-1, 1):
                    c.drawOval(skia.Rect.MakeXYWH(TX + sg * 22 - 12, hy + 4, 24, 14), K.paint(RED, 0.7))
        with at_pop(c, WX, GY, g):
            gu(c, WX, GY, 0.85, WEI, hat="futou", beard="black", mood="flat", rh=(WX - 160, GY - 300) if T >= tp else None)
            name_tag(c, WX, GY - 420, "魏征", "#2C6E68", 34)
        if T >= tw:
            mirror(c, WX, cy - 300, 140, 200, clamp01((T - tw) / 0.3))
        return None
    b.custom(j, k_wei, k_wei + 0.3, scene, sfx="tom", gain=0.75)
    b.hit(j, k_point, "rim", 0.8, "当面指出错")
    b.hit(j, k_red, "wood_high", 0.7, "下不来台")


screen4()


# ================================================================ 屏 5：太宗下朝气冲冲；长孙皇后换上礼服道贺
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_angry = kq(j, wp(6, 1, 0.4), 0)
    k_say = nx(j, wp(6, 3, 0.4), k_angry)
    k_queen = nx(j, wp(7, 0, 0.6), k_say)
    k_bow = nx(j, wp(7, 1, 0.4), k_queen)
    k_why = nx(j, wp(7, 3, 0.4), k_bow)
    TX, QX = cx - 320, cx + 300
    L.note("乡巴佬", "主明臣直")

    def scene(c, kk, T):
        ta, ts, tq, tbw, tw = tb(j, k_angry), tb(j, k_say), tb(j, k_queen), tb(j, k_bow), tb(j, k_why)
        g = pop_scale(T - ta)
        if g <= 0:
            return None
        with at_pop(c, TX, GY, g):
            gu(c, TX, GY, 0.95, TANG, hat="futou", beard="black", mood="angry",
               rh=(TX + 150, GY - 330 + 20 * math.sin((T - ts) * 12)) if T >= ts else None)
            name_tag(c, TX, GY - 450, "唐太宗", "#8A5A1E", 38)
            for q in range(3):
                f = ((T - ta) * 1.1 + q * 0.33) % 1
                c.drawCircle(TX - 30 + 30 * q, GY - 330 - 120 * f, 18 + 10 * f, K.paint(GRAY, 0.5 * (1 - f)))
        if T >= ts:
            with K.at(c, TX + 120, cy - 360, 0, C.slam_scale(T - ts)):
                bubble_box(c, 0, 0, 300, 110, -1)
                K.text(c, "乡巴佬", 0, 0, 58, "hand", RED)
        if T >= tq:
            with at_pop(c, QX, GY, pop_scale(T - tq)):
                gu(c, QX, GY, 0.95, QUEEN, hat="lady", mood="smile", bow=T >= tbw)
                name_tag(c, QX, GY - 450, "长孙皇后", "#9C2F25", 34)
                C.line(c, (QX - 60, GY - 120), (QX + 60, GY - 120), "#C9A34A", 8)
        if T >= tw:
            with K.at(c, QX - 40, cy - 330, 0, C.slam_scale(T - tw)):
                bamboo_slips(c, 0, 0, 380, 140, n=6)
                K.text(c, "主明臣直", 0, 0, 60, "serif_black", RED)
        return None
    ev(j, k_angry, scene, "muyu", 0.6)
    b.hit(j, k_say, "rim", 0.85, "早晚杀了他")
    b.hit(j, k_queen, "pop", 0.7, "皇后换礼服")
    b.hit(j, k_bow, "wood_high", 0.7, "道贺")
    b.hit(j, k_why, "bangzi", 0.8, "主明臣直")


screen5()


# ================================================================ 屏 6：太宗头顶的火苗熄灭，笑了
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_tang = 0
    k_calm = kq(j, wp(8, 1, 0.4), 1)
    TX = cx

    def scene(c, sc, T):
        tc = tb(j, k_calm)
        calm = T >= tc
        with at_pop(c, TX, GY, sc):
            gu(c, TX, GY, 1.05, TANG, hat="futou", beard="black", mood="smile" if calm else "angry")
        f = ease_out(clamp01((T - tc) / 0.4)) if calm else 0
        hy = GY - 290 * 1.05
        h = 140 * (1 - f)
        if h > 2:
            c.drawPath(P((TX - 60, hy - 120), (TX, hy - 120 - h), (TX + 60, hy - 120), close=True), K.paint(ORANGE))
        if calm:
            for q in range(3):
                ff = ((T - tc) * 0.8 + q * 0.33) % 1
                c.drawCircle(TX + 30 * math.sin(q + T * 3), hy - 140 - 160 * ff, 14 + 10 * ff, K.paint(GRAY, 0.4 * (1 - ff)))
            sparkle(c, TX, hy, T - tc, YELLOW, 10, 80, 160)
        return None
    ev(j, k_tang, L.pop_fn(j, k_tang, scene), "muyu", 0.6)
    b.hit(j, k_calm, "ding", 0.85, "气消了")


screen6()


# ================================================================ 屏 7：铜镜照衣帽、史书镜照兴衰、人镜照对错；魏征那面镜子空了
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_m = [kq(j, wp(9, 1, 0.4), 0)]
    k_m.append(nx(j, wp(9, 3, 0.4), k_m[0]))
    k_m.append(nx(j, wp(10, 0, 0.5), k_m[1]))
    k_gone = nx(j, wp(10, 3, 0.4), k_m[2])
    L.note("铜", "史", "人", "衣帽", "兴衰", "对错")
    LAB = [("铜", "衣帽"), ("史", "兴衰"), ("人", "对错")]

    def scene(c, kk, T):
        tgo = tb(j, k_gone)
        for i, (k_, (t1, t2)) in enumerate(zip(k_m, LAB)):
            t0 = tb(j, k_)
            g = pop_scale(T - t0)
            if g <= 0:
                continue
            x = cx - 350 + i * 350
            with K.at(c, x, cy - 160, 0, g):
                mirror(c, 0, 0, 240, 380, 1.0, "#C9A34A" if i == 0 else ("#5E4128" if i == 1 else "#2C6E68"))
                if i == 0:
                    c.drawRect(skia.Rect.MakeXYWH(-40, -60, 80, 40), K.paint(INK))
                elif i == 1:
                    bamboo_slips(c, 0, 0, 120, 160, n=2)
                elif T < tgo:
                    gu(c, 0, 140, 0.4, WEI, hat="futou", beard="black", mood="smile")
                else:
                    gu(c, 0, 140, 0.4, WEI, hat="futou", beard="black", alpha=max(0.0, 1 - (T - tgo) / 0.5))
                K.text(c, t1, 0, -230, 56, "serif_black", INK)
                K.text(c, t2, 0, 250, 50, "hand", ORANGE)
        if T >= tgo:
            with at_pop(c, cx - 300, GY, pop_scale(T - tgo)):
                gu(c, cx - 300, GY, 0.6, TANG, hat="futou", beard="black", mood="sad")
            with K.at(c, cx + 200, cy + 300, -4, C.slam_scale(T - tgo)):
                chip(c, 0, 0, "少了一面镜子", GRAY_FILL, GRAY, 48)
        return None
    L.note("少了一面镜子")
    ev(j, k_m[0], scene, "muyu", 0.7)
    for k_ in k_m[1:]:
        b.hit(j, k_, "bangzi", 0.75, "又一面镜子")
    b.hit(j, k_gone, "xiaoluo", 0.8, "魏征走了")


GRAY_FILL = "#D9DCE1"
screen7()


# ================================================================ 屏 8：小李嘴边的“别说了”被擦掉，留出一个开口的空位
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_stop = kq(j, wp(11, 2, 0.3), 1)
    k_erase = nx(j, wp(11, 3, 0.5), k_stop)
    k_how = nx(j, wp(12, 1, 0.4), k_erase)
    LX = cx - 260
    L.note("别说了", "你说", "人镜")

    def scene(c, sc, T):
        ts, te, th = tb(j, k_stop), tb(j, k_erase), tb(j, k_how)
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 1.0, "smile" if T >= te else "flat", rh=(LX + 140, GY - 330) if ts <= T < te else None)
        if T >= ts:
            f = clamp01((T - te) / 0.4) if T >= te else 0
            with K.at(c, LX + 200, cy - 280, 0, pop_scale(T - ts)):
                bubble_box(c, 0, 0, 280, 110, -1, 1 - f)
                K.text(c, "别说了", 0, 0, 54, "hand", RED, 1 - f)
            if T >= te:
                with K.at(c, LX + 200, cy - 280, 0, pop_scale(T - te)):
                    bubble_box(c, 0, 0, 220, 110, -1)
                    K.text(c, "你说", 0, 0, 56, "hand", GREEN)
        if T >= th:
            with K.at(c, cx + 300, cy - 50, 0, pop_scale(T - th)):
                mirror(c, 0, 0, 200, 320)
                K.text(c, "人镜", 0, 210, 54, "hand", "#2C6E68")
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_stop, "rim", 0.75, "别说了")
    b.hit(j, k_erase, "shaker", 0.75, "擦掉")
    b.hit(j, k_how, "ding", 0.8, "找一面人镜")


screen8()


# ================================================================ 屏 9：第一步：日历每月一格，敢说真话的同事圈出一个毛病
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 0)
    GY = cy + 520
    k_pair = kq(j, wp(13, 1, 0.5), 1)
    k_cal = nx(j, wp(13, 2, 0.5), k_pair)
    k_ring = nx(j, wp(13, 3, 0.4), k_cal)
    L.note("每月一次", "毛病")

    def scene(c, kk, T):
        tp, tc, tr = tb(j, k_pair), tb(j, k_cal), tb(j, k_ring)
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            draw_li(c, cx - 330, GY, 0.9, "flat")
            draw_wang(c, cx + 330, GY, 0.9, mood="flat", lh=(cx + 200, GY - 300) if T >= tr else None)
        if T >= tc:
            with K.at(c, cx, cy - 200, 0, pop_scale(T - tc)):
                box(c, 0, 0, 560, 320, "#FFFFFF", BLACK, 6, 12)
                K.text(c, "每月一次", 0, -120, 46, "hand", INK)
                for q in range(6):
                    c.drawRect(skia.Rect.MakeXYWH(-240 + q * 82, -60, 70, 70), wb.marker(GRAY, 3))
                if T >= tr:
                    ring = skia.Path()
                    ring.addOval(skia.Rect.MakeXYWH(-260, -80, 110, 110))
                    c.drawPath(wb.partial(ring, ease_out(clamp01((T - tr) / 0.3)))[0], wb.marker(RED, 8))
                    K.text(c, "毛病", -60, 90, 54, "hand", RED, clamp01((T - tr) / 0.2))
        return None
    ev(j, k_pair, scene, "wood_low", 0.6)
    b.hit(j, k_cal, "pop", 0.7, "每月一次")
    b.hit(j, k_ring, "rim", 0.8, "挑一个毛病")


screen9()


# ================================================================ 屏 10：第二步：刺耳的话飞来，小李先说“谢谢”，回家再想
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 1)
    GY = cy + 520
    k_spike = kq(j, wp(14, 0, 0.6), 1)
    k_thx = nx(j, wp(14, 1, 0.5), k_spike)
    k_home = nx(j, wp(14, 2, 0.5), k_thx)
    LX = cx - 280
    L.note("谢谢", "回去再想")

    def scene(c, kk, T):
        ts, tt, th = tb(j, k_spike), tb(j, k_thx), tb(j, k_home)
        g = pop_scale(T - ts + 0.3)
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "smile" if T >= tt else "o")
        if T >= ts:
            f = clamp01((T - ts) / 0.4)
            x = lerp(cx + 500, LX + 160, f)
            with K.at(c, x, cy - 150, 0, 1):
                pts = [(math.cos(math.radians(36 * z)) * (60 if z % 2 == 0 else 26),
                        math.sin(math.radians(36 * z)) * (60 if z % 2 == 0 else 26)) for z in range(10)]
                c.drawPath(P(*pts, close=True), K.paint(RED_FILL))
                c.drawPath(P(*pts, close=True), wb.marker(RED, 5))
        if T >= tt:
            with K.at(c, LX + 60, cy - 380, 0, C.slam_scale(T - tt)):
                bubble_box(c, 0, 0, 220, 110, -1)
                K.text(c, "谢谢", 0, 0, 58, "hand", GREEN)
        if T >= th:
            with K.at(c, cx + 280, cy + 40, 0, pop_scale(T - th)):
                p = P((-140, 120), (-140, -20), (0, -140), (140, -20), (140, 120), close=True)
                c.drawPath(p, K.paint(NOTE_FILL))
                c.drawPath(p, wb.marker(ORANGE, 6))
                K.text(c, "回去再想", 0, 40, 46, "hand", INK)
        return None
    ev(j, k_spike, scene, "rim", 0.75)
    b.hit(j, k_thx, "pop", 0.8, "先说谢谢")
    b.hit(j, k_home, "ding", 0.75, "回去再想")


screen10()


# ================================================================ 屏 11：第三步：遇到难事，小李翻开一卷竹简
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.steps_row(j, 2)
    GY = cy + 520
    k_hard = kq(j, wp(15, 0, 0.6), 1)
    k_open = nx(j, wp(15, 1, 0.5), k_hard)
    k_mirror = nx(j, wp(15, 3, 0.4), k_open)
    L.note("难事", "历史当镜子")

    def scene(c, kk, T):
        th, to, tm = tb(j, k_hard), tb(j, k_open), tb(j, k_mirror)
        g = pop_scale(T - th)
        if g <= 0:
            return None
        LX = cx - 330
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "smile" if T >= to else "sad", lh=(LX + 60, GY - 230) if T >= to else None,
                    rh=(LX + 200, GY - 230) if T >= to else None)
        if T < to:
            K.text(c, "难事", LX, cy - 120, 60, "hand", RED, clamp01(g))
        if T >= to:
            f = ease_out(clamp01((T - to) / 0.5))
            bamboo_slips(c, cx + 60, cy - 120, max(60, 500 * f), 360, n=max(1, int(7 * f)))
        if T >= tm:
            with K.at(c, cx + 60, cy + 200, 0, C.slam_scale(T - tm)):
                chip(c, 0, 0, "历史当镜子", GREEN_FILL, GREEN, 54)
        return None
    ev(j, k_hard, scene, "wood_low", 0.6)
    b.hit(j, k_open, "muyu", 0.8, "翻开竹简")
    b.hit(j, k_mirror, "kick", 0.85, "拿历史当镜子")


screen11()


# ================================================================ 屏 12：好处：错误早早被圈出来，小李走得稳
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_road = kq(j, wp(16, 0, 0.6), 0)
    k_ring = nx(j, wp(16, 1, 0.5), k_road)
    k_walk = nx(j, wp(16, 2, 0.5), k_ring)
    L.note("更稳")

    def scene(c, kk, T):
        tr, trg, tw = tb(j, k_road), tb(j, k_ring), tb(j, k_walk)
        g = pop_scale(T - tr)
        if g <= 0:
            return None
        C.line(c, (cx - 560, GY + 6), (cx + 560, GY + 6), "#8B6B43", 8)
        c.drawOval(skia.Rect.MakeXYWH(cx + 40, GY - 20, 160, 44), K.paint("#5E4128"))
        if T >= trg:
            ring = skia.Path()
            ring.addOval(skia.Rect.MakeXYWH(cx + 10, GY - 60, 220, 120))
            c.drawPath(wb.partial(ring, ease_out(clamp01((T - trg) / 0.3)))[0], wb.marker(RED, 8))
            flag_x = cx + 120
            C.line(c, (flag_x, GY - 30), (flag_x, GY - 180), INK, 5)
            c.drawPath(P((flag_x, GY - 180), (flag_x + 70, GY - 160), (flag_x, GY - 140), close=True), K.paint(RED))
        x, dy, _ = C.walk(T, tw, 1.4, cx - 480, cx - 80, 8) if T >= tw else (cx - 480, 0, False)
        with at_pop(c, x, GY + dy, g):
            draw_li(c, x, GY + dy, 0.9, "smile")
        if T >= tw:
            K.text(c, "更稳", cx - 200, cy - 200, 70, "hand", GREEN, clamp01((T - tw) / 0.2))
        return None
    ev(j, k_road, scene, "wood_low", 0.6)
    b.hit(j, k_ring, "rim", 0.75, "错误早早圈出来")
    b.hit(j, k_walk, "ding", 0.8, "走得更稳")


screen12()


# ================================================================ 屏 13：第一季回看：十五张卡片排成一面墙
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_wall = kq(j, wp(17, 1, 0.3), 0)
    k_15 = nx(j, wp(17, 2, 0.5), k_wall)
    k_use = nx(j, wp(18, 2, 0.4), k_15)
    L.note(*SEASON, "第一季", "拿来就用")

    def scene(c, kk, T):
        tw, t15, tu = tb(j, k_wall), tb(j, k_15), tb(j, k_use)
        if T < tw:
            return None
        K.text(c, "第一季", cx, cy - 500, 64, "serif_black", RED, clamp01((T - tw) / 0.3))
        for i, s_ in enumerate(SEASON):
            r_, q = divmod(i, 3)
            x, y = cx - 340 + q * 340, cy - 390 + r_ * 150
            t0 = tw + i * max(0.04, (t15 - tw) / 15)
            g = pop_scale(T - t0, 0.22)
            if g <= 0:
                continue
            with K.at(c, x, y, 0, g):
                box(c, 0, 0, 310, 120, PARCH, PARCH_LINE, 5, 10)
                K.text(c, f"{i + 1:02d}", -110, 0, 36, "black", RED)
                K.text(c, s_, 30, 0, min(44.0, 44 * 190 / K.text_w(s_, 44, "serif_black")), "serif_black", INK)
        if T >= tu:
            with K.at(c, cx, cy + 420, -3, C.slam_scale(T - tu)):
                chip(c, 0, 0, "拿来就用", GREEN_FILL, GREEN, 58)
        return None
    ev(j, k_wall, scene, "shaker", 0.75)
    b.hit(j, k_15, "bianzhong", 0.85, "十五讲")
    b.hit(j, k_use, "kick", 0.85, "拿来就用")


screen13()


# ================================================================ 屏 14：季终：评论区；第一讲亮起；一条长路从竹简里延伸到小李脚下；镜子里的人笑着点头；“下一季见”
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z_))
    k_chips = nx(j, wp(20, 0, 0.3), 0)
    k_first = nx(j, wp(20, 2, 0.4), k_chips)
    k_road = nx(j, wp(21, 2, 0.3), k_first)
    k_mirror = nx(j, wp(22, 1, 0.4), k_road)
    k_bye = nx(j, wp(23, 1, 0.3), k_mirror)
    b.move(j, k_road, (cx, cy + 380, Z_), 1.1)
    CH = ["才与德", "立信", "兼听"]
    L.note("最想先用哪一讲？", *CH, "第一讲", "下一季见", "借着走")

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, 0))
        if sc <= 0:
            return None
        with K.at(c, cx + 20, cy - 330, 0, sc):
            bubble_box(c, 0, 0, 1000, 360, -1)
            K.text(c, "最想先用哪一讲？", 0, -110, 62, "hand", RED)
            for i, nm in enumerate(CH):
                g = pop_scale(T - tb(j, k_chips) - i * 0.15, 0.22)
                if g <= 0:
                    continue
                x, y = (-230 + (i % 2) * 460, 10) if i < 2 else (0, 110)
                with K.at(c, x, y, 0, g):
                    chip(c, 0, 0, nm, BLUE_FILL, BLUE, 44)
        tf = tb(j, k_first)
        if T >= tf:
            with K.at(c, cx + 380, cy - 90, 6, C.slam_scale(T - tf)):
                box(c, 0, 0, 220, 90, NOTE_FILL, ORANGE, 5, 10)
                K.text(c, "第一讲", 0, 0, 46, "hand", RED)
        return None
    ev(j, 0, cmt, "pop", 0.7)
    b.hit(j, k_chips, "wood_high", 0.6, "评论冒出来")
    b.hit(j, k_first, "pop", 0.75, "从第一讲看起")
    LY = cy + 640

    def road(c, kk, T):
        tr, tm = tb(j, k_road), tb(j, k_mirror)
        if T < tr:
            return None
        f = ease_out(clamp01((T - tr) / 0.8))
        bamboo_slips(c, cx - 420, cy + 330, 160, 240, n=3)
        p = P((cx - 380, cy + 450), (lerp(cx - 380, cx - 60, f), lerp(cy + 450, LY - 10, f)))
        c.drawPath(p, wb.marker("#8B6B43", 40, 0.5))
        LX = cx - 40
        with at_pop(c, LX, LY, pop_scale(T - tr - 0.3)):
            draw_li(c, LX, LY, 0.85, "smile")
        K.text(c, "借着走", cx - 230, cy + 280, 52, "hand", GREEN, f)
        if T >= tm:
            MX = cx + 330
            g = pop_scale(T - tm)
            with K.at(c, MX, cy + 440, 0, g):
                mirror(c, 0, 0, 220, 360)
            nod = 10 * abs(math.sin((T - tm) * 5))
            c.save()
            c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(MX - 110, cy + 260, 220, 360), 110, 110))
            draw_li(c, MX, cy + 600 + nod * 0.3, 0.6, "smile", alpha=0.6)
            c.restore()
            sparkle(c, MX, cy + 300, T - tm, YELLOW, 10, 60, 140)
        return None
    ev(j, k_road, road, "wood_low", 0.65)
    b.hit(j, k_mirror, "ding", 0.85, "镜子里的人笑着点头")

    def bye(c, kk, T):
        t0 = tb(j, k_bye)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        with K.at(c, cx + 20, cy + 880, -2, sc):
            box(c, 0, 0, 900, 200, "#FFFFFF", BLACK, 7, 18)
            K.text(c, "下一季见", -60, 0, 90, "serif_black", RED)
            seal(c, 320, 0, "通鉴", 50, -6)
        return None
    ev(j, k_bye, bye, "bianzhong", 0.9)


screen14()

# ================================================================ 收尾
L.finish(cover_shot=7, square_shot=5, notes=NOTES)
L.export(globals())
