"""《资治通鉴》07 萧规曹随：接手别人的活，要不要全推翻？（白板手绘 + AI 旁白，竖屏 2:3）

误区对照：“新官上任三把火”对照曹参接班——萧何临死推荐有过节的曹参；曹参一条规矩不改，斥去好出风头的吏、留下厚道的；
惠帝着急来问，曹参两个反问（陛下比高祖、我比萧何）；“遵而勿失”；百姓歌“萧何为法，讲若画一；曹参代之，守而勿失”。
今人部分：接手前任项目的三步（先照旧跑一遍、留顺手的改卡住的、改前打招呼）。古人的屏画在卷轴框里，今人在办公室。
文案见 zizhi/PLAN.md「### 07」。
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
                          at_pop, bamboo_slips, box, bubble_box, cup, desk, draw_ace, draw_li, draw_wang, gu, pop_scale, seal,
                          slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4, 5], "通鉴里的故事", 4),
    ([6, 7], "一遵何之约束", 5),
    ([8, 9], "皇帝来问", 6),
    ([10, 11], "两个反问", 7),
    ([12, 13], "守而勿失", 8),
    ([14, 15], "百姓的歌", 9),
    ([16, 17], "说回我们自己", 10),
    ([18], "第一步", 11),
    ([19], "第二步", 12),
    ([20], "第三步", 13),
    ([21], "好处", 14),
    ([22, 23, 24, 25], "评论区见", 15),
]

THEME = ZT.get("07")
L = Z.Lesson("07", SCREENS, drop_screen=2, board_size=(5000, 12000), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(14)]
Z_ = 0.72

NOTES = [
    "出处：司马光《资治通鉴》卷十二 汉纪四（惠帝二年；惠帝问答所在年份待核）。",
    "原文：“参始微时，与萧何善；及为将相，有隙。至何且死，所推贤唯参。参代何为相国，举事无所变更，一遵何之约束。"
    "择郡国吏木诎于文辞、重厚长者，即召除为丞相史；吏之言文刻深、欲务声名者，辄斥去之。日夜饮醇酒。”"
    "“陛下自察圣武孰与高帝？……陛下观参孰与萧何贤？……高帝与萧何定天下，法令既明；今陛下垂拱，参等守职，遵而勿失，不亦可乎！"
    "帝曰：善！”百姓歌之曰：“萧何为法，讲若画一；曹参代之，守而勿失。”",
    "今人（小李、小王、同事）为虚构示意；古人造型为示意。",
]

XIAO, CAO, HUI, GAOZU, MIN = "ochre", "teal", "red", "brown", "gray"
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


def flowchart(c, x, y, marks=None, a=1.0):
    """四格流程图（2×2），marks[i] 为 None / "x" / "ok" / "fix"。"""
    pts = [(x - 150, y - 100), (x + 150, y - 100), (x + 150, y + 100), (x - 150, y + 100)]
    for i in range(3):
        C.line(c, pts[i], pts[i + 1], GRAY, 5, a)
    for i, (px, py) in enumerate(pts):
        box(c, px, py, 170, 100, "#FFFFFF", BLUE, 5, 12, a)
        m = (marks or [None] * 4)[i]
        if m == "x":
            c.drawPath(cross(px, py, 40), wb.marker(RED, 9, a))
        elif m == "ok":
            c.drawPath(check(px, py, 34), wb.marker(GREEN, 9, a))
        elif m == "fix":
            c.drawCircle(px, py, 60, wb.marker(RED, 7, a))
    return pts


def fire(c, x, y, s=1.0, a=1.0, t=0.0):
    with K.at(c, x, y, 0, s):
        w = 1 + 0.08 * math.sin(t * 14)
        p = P((0, -100 * w), (44, -30), (40, 30), (0, 60), (-40, 30), (-44, -30), close=True)
        c.drawPath(p, K.paint(ORANGE, a))
        c.drawPath(p, wb.marker(RED, 5, a))
        p2 = P((0, -40 * w), (20, 0), (0, 40), (-20, 0), close=True)
        c.drawPath(p2, K.paint(YELLOW, a))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：小李翻前任的项目皱眉；表格、流程图一个个红叉
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_frown = kq(j, wp(0, 2, 0.5), 1)
    k_x1 = nx(j, wp(1, 0, 0.5), k_frown)
    k_x2 = nx(j, wp(1, 1, 0.5), k_x1)
    k_all = nx(j, wp(1, 2, 0.5), k_x2)
    LX = cx - 380
    L.note("前任的项目", "全推翻")

    def scene(c, sc, T):
        tf = tb(j, k_frown)
        with at_pop(c, LX, GY, sc):
            desk(c, LX + 140, GY - 170, 360)
            draw_li(c, LX, GY, 0.95, "sad" if T >= tf else "flat", rh=(LX + 120, GY - 230))
        with K.at(c, cx - 30, cy - 330, 0, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(-180, -90, 360, 180), 12, 12, K.paint("#F6D98A"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-180, -90, 360, 180), 12, 12, wb.marker(ORANGE, 5))
            K.text(c, "前任的项目", 0, 0, 50, "hand", INK)
        x1 = T >= tb(j, k_x1)
        x2 = T >= tb(j, k_x2)
        with K.at(c, cx + 300, cy - 280, 0, pop_scale(T - tb(j, k_x1) + 0.3)):
            box(c, 0, 0, 300, 200, "#FFFFFF", GRAY, 5, 8)
            for r in range(3):
                for q in range(3):
                    c.drawRect(skia.Rect.MakeXYWH(-120 + q * 80, -70 + r * 50, 70, 40), wb.marker(GRAY, 3))
            if x1:
                c.drawPath(cross(0, 0, 70), wb.marker(RED, 12))
        with K.at(c, cx + 220, cy + 60, 0, pop_scale(T - tb(j, k_x2) + 0.3)):
            flowchart(c, 0, 0, ["x", None, "x", None] if x2 else None)
        if T >= tb(j, k_all):
            with K.at(c, cx - 30, cy - 130, -6, C.slam_scale(T - tb(j, k_all))):
                chip(c, 0, 0, "全推翻", RED_FILL, RED, 60)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_frown, "wood_high", 0.6, "越看越不顺眼")
    b.hit(j, k_x1, "rim", 0.75, "表格打叉")
    b.hit(j, k_x2, "rim", 0.75, "流程打叉")
    b.hit(j, k_all, "kick", 0.8, "全推翻")


screen1()


# ================================================================ 屏 2（drop）：一个月后，客户电话没人接，同事抱着文件乱转
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_cal = kq(j, wp(2, 0, 0.5), 0)
    k_phone = nx(j, wp(2, 1, 0.5), k_cal)
    L.note("一个月", "？")

    def scene(c, kk, T):
        tc, tp, td = tb(j, k_cal), tb(j, k_phone), tb(j, dk)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx - 300, cy - 330, 0, g):
            box(c, 0, 0, 260, 200, "#FFFFFF", BLACK, 6, 10)
            c.drawRect(skia.Rect.MakeXYWH(-130, -100, 260, 50), K.paint(RED_FILL))
            n = int(lerp(1, 30, clamp01((T - tc) / 0.8)))
            K.text(c, f"{n}", 0, 30, 80, "black", RED)
            K.text(c, "一个月", 0, 130, 44, "hand", INK)
        if T >= tp:
            with K.at(c, cx + 270, cy - 330, 10 * math.sin((T - tp) * 30), pop_scale(T - tp)):
                box(c, 0, 0, 120, 200, "#FFFFFF", BLACK, 6, 18)
                for q in range(3):
                    ar = skia.Path()
                    ar.addArc(skia.Rect.MakeXYWH(40 - q * 10, -60 - q * 20, 60 + q * 40, 60 + q * 40), -60, 120)
                    c.drawPath(ar, wb.marker(RED, 5))
                K.text(c, "？", 0, 0, 70, "hand", RED)
        if T >= td:
            for i, x0 in enumerate((cx - 300, cx, cx + 300)):
                x = x0 + 60 * math.sin((T - td) * 4 + i * 2)
                with at_pop(c, x, GY, pop_scale(T - td - i * 0.08)):
                    if i == 1:
                        draw_wang(c, x, GY, 0.8, mood="sad", lh=(x - 60, GY - 200), rh=(x + 60, GY - 200))
                    else:
                        draw_li(c, x, GY, 0.8, "sad", lh=(x - 60, GY - 200), rh=(x + 60, GY - 200))
                    box(c, x, GY - 200, 130, 60, "#FFFFFF", GRAY, 4, 4)
        return None
    ev(j, k_cal, scene, "wood_high", 0.65)
    b.hit(j, k_phone, "rim", 0.75, "客户找不到人")
    b.hit(j, dk, "kick", 0.9, "同事也跟着乱")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：三把火越烧越大，把小李的衣角也点着了
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_f = [kq(j, wp(3, 0, 0.3), 0)]
    k_f.append(nx(j, wp(3, 0, 0.7), k_f[0]))
    k_f.append(nx(j, wp(3, 1, 0.5), k_f[1]))
    k_burn = nx(j, wp(3, 2, 0.5), k_f[2])
    LX = cx - 300
    L.note("三把火")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_f[0]) + 0.2)
        if g <= 0:
            return None
        tbn = tb(j, k_burn)
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "o" if T >= tbn else "smile", rh=(LX + 120, GY - 330))
        for i, k_ in enumerate(k_f):
            t0 = tb(j, k_)
            if T < t0:
                continue
            grow = 1 + 0.4 * clamp01((T - tbn) / 0.5) if T >= tbn else 1
            fire(c, cx + 20 + i * 180, GY - 120, (0.8 + 0.2 * i) * grow * C.slam_scale(T - t0), 1.0, T)
        K.text(c, "三把火", cx + 200, cy - 300, 70, "hand", RED, clamp01((T - tb(j, k_f[2])) / 0.3))
        if T >= tbn:
            fire(c, LX + 40, GY - 140, 0.45 * pop_scale(T - tbn), 1.0, T)
            sparkle(c, LX, GY - 380, T - tbn, ORANGE, 8, 40, 100)
        return None
    b.custom(j, k_f[0], k_f[0] + 0.3, scene)
    for k_ in k_f:
        b.hit(j, k_, "tom", 0.7, "一把火")
    b.hit(j, k_burn, "kick", 0.85, "把自己也烧进去")
    b.shots[j].shake = [(k_burn, 9.0)]


screen3()


# ================================================================ 屏 4：竹简“资治通鉴 卷十二”；萧何病榻上推荐曹参；两人之间一道旧裂缝
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_slip = kq(j, wp(4, 0, 0.3), 0)
    k_xiao = nx(j, wp(4, 1, 0.4), k_slip)
    k_cao = nx(j, wp(4, 2, 0.4), k_xiao)
    k_crack = nx(j, wp(5, 1, 0.4), k_cao)
    k_point = nx(j, wp(5, 3, 0.4), k_crack)
    SX = cx - 380
    L.note("资治通鉴", "卷十二", "汉纪四", "萧何", "曹参", "旧怨")

    def slips(c, kk, T):
        f = ease_out(clamp01((T - tb(j, k_slip)) / 0.6))
        if f <= 0:
            return None
        bamboo_slips(c, SX, cy - 200, max(60, 280 * f), 560, n=max(1, int(4 * f)))
        a = clamp01((T - tb(j, k_slip) - 0.3) / 0.3)
        slip_text(c, SX + 40, cy - 420, "资治通鉴", 70, "#3A2A12", a)
        slip_text(c, SX - 70, cy - 390, "卷十二", 50, RED, a)
        slip_text(c, SX - 70, cy - 210, "汉纪四", 42, "#5E4128", a, 1.15)
        return None
    ev(j, k_slip, slips, "muyu", 0.7, 0.6)

    def scene(c, kk, T):
        tx, tc, tcr, tp = tb(j, k_xiao), tb(j, k_cao), tb(j, k_crack), tb(j, k_point)
        g = pop_scale(T - tx)
        if g <= 0:
            return None
        BX = cx - 80
        with at_pop(c, BX, GY, g):
            box(c, BX, GY - 80, 420, 60, "#C98B4B", "#7A4A1E", 5, 8)
            with K.at(c, BX, GY - 150, -80):
                gu(c, 0, 0, 0.6, XIAO, hat="guan", beard="white", mood="sad",
                   rh=(80, -180) if T >= tp else None)
            name_tag(c, BX - 40, GY - 260, "萧何", "#8A5A1E", 36)
        gc = pop_scale(T - tc)
        if gc > 0:
            CX_ = cx + 380
            with at_pop(c, CX_, GY, gc):
                gu(c, CX_, GY, 0.85, CAO, hat="guan", beard="black", mood="o" if T >= tp else "flat")
                name_tag(c, CX_, GY - 400, "曹参", "#2C6E68", 40)
        if T >= tcr:
            f = ease_out(clamp01((T - tcr) / 0.4))
            mx = cx + 180
            c.drawPath(wb.partial(P((mx, cy - 120), (mx - 30, cy - 40), (mx + 20, cy + 40), (mx - 20, cy + 120)), f)[0],
                       wb.marker(GRAY, 8))
            K.text(c, "旧怨", mx + 90, cy - 160, 48, "hand", GRAY, f)
        if T >= tp:
            f = ease_out(clamp01((T - tp) / 0.4))
            c.drawPath(wb.arrow((cx - 40, GY - 330), (lerp(cx - 40, cx + 300, f), GY - 360), -0.3, 34), wb.marker(GREEN, 9))
            sparkle(c, cx + 380, GY - 360, T - tp, YELLOW, 10, 60, 140)
        return None
    b.custom(j, k_xiao, k_xiao + 0.3, scene, sfx="wood_low", gain=0.65)
    b.hit(j, k_cao, "tom", 0.75, "曹参接班")
    b.hit(j, k_crack, "rim", 0.7, "闹过别扭")
    b.hit(j, k_point, "ding", 0.85, "萧何推荐曹参")


screen4()


# ================================================================ 屏 5：曹参捧着萧何的规矩一根不动；花哨的官吏被请出门，厚道的留下
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_cao = kq(j, wp(6, 0, 0.5), 0)
    k_keep = nx(j, wp(6, 1, 0.5), k_cao)
    k_out = nx(j, wp(7, 2, 0.4), k_keep)
    k_stay = nx(j, wp(7, 4, 0.4), k_out)
    L.note("萧何的规矩", "原样", "花哨", "厚道")

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, k_cao))
        if g <= 0:
            return None
        CX_ = cx - 300
        with at_pop(c, CX_, GY, g):
            gu(c, CX_, GY, 0.95, CAO, hat="guan", beard="black", lh=(CX_ - 60, GY - 300), rh=(CX_ + 60, GY - 300))
            name_tag(c, CX_, GY - 440, "曹参", "#2C6E68", 40)
        with K.at(c, CX_, cy - 120, 0, g):
            bamboo_slips(c, 0, 0, 380, 280, n=6)
            K.text(c, "萧何的规矩", 0, -20, 46, "serif_black", INK)
        tk = tb(j, k_keep)
        if T >= tk:
            with K.at(c, CX_, cy - 330, -4, C.slam_scale(T - tk)):
                chip(c, 0, 0, "原样", GREEN_FILL, GREEN, 54)
        to, ts = tb(j, k_out), tb(j, k_stay)
        if T >= to - 0.3:
            f = ease_in_out(clamp01((T - to) / 0.6)) if T >= to else 0
            x = lerp(cx + 220, cx + 520, f)
            with at_pop(c, x, GY, pop_scale(T - to + 0.3)):
                gu(c, x, GY, 0.65, "purple", hat="guan", mood="laugh", alpha=1 - 0.5 * f, head_dx=10)
            K.text(c, "花哨", cx + 260, cy - 60, 48, "hand", RED, clamp01((T - to + 0.3) / 0.2) * (1 - 0.5 * f))
        if T >= ts:
            with at_pop(c, cx + 200, GY, pop_scale(T - ts)):
                gu(c, cx + 200, GY, 0.7, MIN, hat="guan", beard="black", mood="smile", bow=True)
            K.text(c, "厚道", cx + 200, cy + 120, 48, "hand", GREEN, clamp01((T - ts) / 0.2))
        return None
    ev(j, k_cao, scene, "muyu", 0.65)
    b.hit(j, k_keep, "kick", 0.8, "一条没改")
    b.hit(j, k_out, "shaker", 0.7, "花哨的打发走")
    b.hit(j, k_stay, "ding", 0.75, "厚道的留下")


screen5()


# ================================================================ 屏 6：曹参举杯喝酒，惠帝着急派人来问；曹参反问：您和高祖比？
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_drink = kq(j, wp(8, 0, 0.5), 0)
    k_worry = nx(j, wp(8, 2, 0.3), k_drink)
    k_ask = nx(j, wp(9, 1, 0.4), k_worry)
    k_who = nx(j, wp(9, 2, 0.4), k_ask)
    CX_, HX_ = cx - 320, cx + 330
    L.note("惠帝", "曹参", "您和高祖比？")

    def scene(c, kk, T):
        td, tw, ta, tw2 = tb(j, k_drink), tb(j, k_worry), tb(j, k_ask), tb(j, k_who)
        g = pop_scale(T - td)
        if g <= 0:
            return None
        sip = 20 * math.sin((T - td) * 4)
        with at_pop(c, CX_, GY, g):
            gu(c, CX_, GY, 0.9, CAO, hat="guan", beard="black", mood="smile",
               rh=(CX_ + 60, GY - 330 + sip) if T < ta else (CX_ + 150, GY - 330))
            if T < ta:
                cup(c, CX_ + 60, GY - 300 + sip, 0.7)
            name_tag(c, CX_, GY - 430, "曹参", "#2C6E68", 38)
        if T >= tw:
            with at_pop(c, HX_, GY, pop_scale(T - tw)):
                gu(c, HX_, GY, 0.85, HUI, hat="guan", mood="angry" if T < ta else "o",
                   rh=(HX_ - 140, GY - 300 + 15 * math.sin((T - tw) * 10)) if T < ta else None)
                name_tag(c, HX_, GY - 410, "惠帝", "#9C2F25", 38)
            if T < ta:
                K.text(c, "！", HX_ + 90, cy - 40, 80, "hand", RED)
        if T >= tw2:
            with K.at(c, cx, cy - 300, 0, C.slam_scale(T - tw2)):
                bubble_box(c, 0, 0, 480, 140, -1)
                K.text(c, "您和高祖比？", 0, 0, 58, "hand", INK)
        return None
    L.note("！")
    ev(j, k_drink, scene, "muyu", 0.65)
    b.hit(j, k_worry, "rim", 0.75, "皇帝着急")
    b.hit(j, k_ask, "pop", 0.7, "曹参反问")
    b.hit(j, k_who, "kick", 0.8, "谁更英明")


screen6()


def scale_pair(c, x, y, left, right, tilt, a=1.0):
    """小天平：左右两张名牌，tilt>0 左边沉。"""
    C.line(c, (x, y), (x, y + 180), "#7A5E3A", 8, a)
    box(c, x, y + 190, 140, 26, "#C9A97A", "#7A5E3A", 4, 6, a)
    with K.at(c, x, y, -tilt):
        C.line(c, (-200, 0), (200, 0), "#7A5E3A", 8, a)
        for sg, lab in ((-1, left), (1, right)):
            with K.at(c, sg * 190, 0, tilt):
                C.line(c, (0, 0), (0, 50), GRAY, 3, a)
                box(c, 0, 90, 140 if sg < 0 else 120, 70 if sg < 0 else 60, "#FFFFFF", RED if sg < 0 else GRAY, 5, 8, a)
                K.text(c, lab, 0, 90, 40 if sg < 0 else 34, "serif_black", INK, a)


# ================================================================ 屏 7：两个天平：惠帝 vs 高祖、曹参 vs 萧何，都往前人那边沉
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    k_s1 = kq(j, wp(10, 1, 0.5), 0)
    k_s2 = nx(j, wp(10, 4, 0.4), k_s1)
    k_ans = nx(j, wp(11, 1, 0.5), k_s2)
    L.note("高祖", "惠帝", "萧何", "曹参", "不如")

    def scene(c, kk, T):
        t1, t2, ta = tb(j, k_s1), tb(j, k_s2), tb(j, k_ans)
        for i, (t0, l_, r_, y) in enumerate(((t1, "高祖", "惠帝", cy - 330), (t2, "萧何", "曹参", cy + 150))):
            g = pop_scale(T - t0)
            if g <= 0:
                continue
            tilt = 14 * ease_out(clamp01((T - t0 - 0.3) / 0.4))
            with K.at(c, cx, y, 0, g):
                scale_pair(c, 0, 0, l_, r_, tilt)
        if T >= ta:
            with K.at(c, cx + 300, cy + 470, -4, C.slam_scale(T - ta)):
                chip(c, 0, 0, "不如", RED_FILL, RED, 60)
        return None
    ev(j, k_s1, scene, "tom", 0.75)
    b.hit(j, k_s2, "tom", 0.75, "第二个天平")
    b.hit(j, k_ans, "rim", 0.8, "你好像不如他")


screen7()


# ================================================================ 屏 8：高祖和萧何画好的规矩图，曹参在旁边守着、照着走
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_map = kq(j, wp(12, 1, 0.5), 0)
    k_clear = nx(j, wp(12, 2, 0.5), k_map)
    k_walk = nx(j, wp(13, 1, 0.4), k_map + 1)
    k_ok = nx(j, wp(13, 2, 0.5), k_walk)
    L.note("法令", "守好本分", "这不就行了？")

    def scene(c, kk, T):
        tm, tc, tw, to = tb(j, k_map), tb(j, k_clear), tb(j, k_walk), tb(j, k_ok)
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        with K.at(c, cx + 60, cy - 220, 0, g):
            box(c, 0, 0, 760, 420, PARCH, PARCH_LINE, 6, 8)
            K.text(c, "法令", -300, -160, 52, "serif_black", RED)
            pts = [(-280, 100), (-120, -40), (60, 60), (240, -80)]
            f = ease_out(clamp01((T - tc) / 0.5)) if T >= tc else 0.4
            for i in range(3):
                C.line(c, pts[i], pts[i + 1], INK, 6)
            for i, p_ in enumerate(pts):
                c.drawCircle(p_[0], p_[1], 26, K.paint(GREEN if f > i / 4 else "#FFFFFF"))
                c.drawCircle(p_[0], p_[1], 26, wb.marker(INK, 5))
            if T >= tw:
                fw = clamp01((T - tw) / 1.2)
                seg = min(2, int(fw * 3))
                u = fw * 3 - seg
                px = lerp(pts[seg][0], pts[seg + 1][0], u)
                py = lerp(pts[seg][1], pts[seg + 1][1], u)
                c.drawCircle(px, py - 40, 22, K.paint(RED))
        x = cx - 360
        with at_pop(c, x, GY, g):
            gu(c, x, GY, 0.85, CAO, hat="guan", beard="black", mood="smile", bow=T >= to)
            name_tag(c, x, GY - 390, "曹参", "#2C6E68", 38)
        if T >= tw:
            with K.at(c, cx + 180, cy + 180, 0, pop_scale(T - tw)):
                chip(c, 0, 0, "守好本分", GREEN_FILL, GREEN, 52)
        if T >= to:
            with K.at(c, cx + 180, cy + 380, 0, C.slam_scale(T - to)):
                bubble_box(c, 0, 0, 480, 130, -1)
                K.text(c, "这不就行了？", 0, 0, 56, "hand", INK)
        return None
    ev(j, k_map, scene, "wood_high", 0.65)
    b.hit(j, k_clear, "ding", 0.7, "法令清清楚楚")
    b.hit(j, k_walk, "shaker", 0.7, "照着走")
    b.hit(j, k_ok, "kick", 0.8, "这不就行了")


screen8()


# ================================================================ 屏 9：惠帝点头“善”；百姓拍手唱歌，竹简上一行歌词
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_hui = kq(j, wp(14, 0, 0.5), 0)
    k_good = nx(j, wp(14, 1, 0.3), k_hui)
    k_song = nx(j, wp(15, 0, 0.5), k_good)
    k_l1 = nx(j, wp(15, 1, 0.4), k_song)
    k_l2 = nx(j, wp(15, 2, 0.4), k_l1)
    L.note("善", "讲若画一", "守而勿失")

    def scene(c, kk, T):
        th, tg = tb(j, k_hui), tb(j, k_good)
        g = pop_scale(T - th)
        if g <= 0:
            return None
        HX_ = cx - 380
        nod = 10 * math.sin((T - tg) * 8) * math.exp(-(T - tg) * 2) if T >= tg else 0
        with at_pop(c, HX_, cy - 30, g):
            gu(c, HX_, cy - 30, 0.65, HUI, hat="guan", mood="smile", head_dx=0)
            name_tag(c, HX_, cy - 300, "惠帝", "#9C2F25", 34)
        if T >= tg:
            seal(c, HX_ + 200, cy - 300 + nod, "善", 90, -6, C.slam_scale(T - tg))
        ts = tb(j, k_song)
        for i, x in enumerate((cx - 400, cx - 240, cx - 80)):
            gi = pop_scale(T - ts - i * 0.1)
            if gi <= 0:
                continue
            clap = abs(math.sin((T - ts) * 7 + i)) * 30
            with at_pop(c, x, GY, gi):
                gu(c, x, GY, 0.55, (MIN, "brown", "ochre")[i], hat="bun", mood="laugh",
                   lh=(x - 20 - clap * 0.3, GY - 220), rh=(x + 20 + clap * 0.3, GY - 220))
            for q in range(2):
                f = ((T - ts) * 0.8 + q * 0.5 + i * 0.2) % 1
                K.text(c, "♪", x + 40 + 30 * f, GY - 300 - 120 * f, 44, "sans_medium", ORANGE, 1 - f)
        for k_, s_, x in ((k_l1, "讲若画一", cx + 300), (k_l2, "守而勿失", cx + 150)):
            t0 = tb(j, k_)
            if T >= t0:
                with K.at(c, x, cy - 60, 0, C.slam_scale(T - t0)):
                    bamboo_slips(c, 0, 0, 120, 540, n=1)
                    slip_text(c, 0, -200, s_, 80, RED if s_ == "守而勿失" else INK)
        return None
    L.note("♪")
    ev(j, k_hui, scene, "muyu", 0.65)
    b.hit(j, k_good, "kick", 0.8, "善")
    b.hit(j, k_song, "clap", 0.8, "百姓唱歌")
    b.hit(j, k_l1, "bangzi", 0.75, "萧何定法")
    b.hit(j, k_l2, "bangzi", 0.75, "曹参守着")


screen9()


# ================================================================ 屏 10：小李的手按在“改”字按钮上又收回；“三步”
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_press = kq(j, wp(16, 1, 0.4), 1)
    k_mark = nx(j, wp(16, 3, 0.4), k_press)
    k_3 = nx(j, wp(17, 1, 0.5), k_mark)
    LX = cx - 320
    L.note("改", "印子", "三步")

    def scene(c, sc, T):
        tp, tm = tb(j, k_press), tb(j, k_mark)
        back = ease_out(clamp01((T - tm) / 0.4)) if T >= tm else 0
        reach = ease_out(clamp01((T - tp) / 0.3)) if T >= tp else 0
        hy = GY - 290
        hand = (lerp(LX + 80, LX + 230, reach * (1 - back)), lerp(hy + 140, hy + 40, reach * (1 - back)))
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 1.0, "flat", rh=hand)
            box(c, LX + 280, hy + 60, 150, 100, RED, INK, 6, 20)
            K.text(c, "改", LX + 280, hy + 60, 60, "hand", "#FFFFFF")
        if T >= tm:
            with K.at(c, cx + 230, cy - 300, 0, pop_scale(T - tm)):
                c.drawOval(skia.Rect.MakeXYWH(-90, -120, 180, 240), K.paint(GRAY_FILL))
                for q in range(5):
                    ar = skia.Path()
                    ar.addOval(skia.Rect.MakeXYWH(-80 + q * 14, -110 + q * 18, 160 - q * 28, 220 - q * 36))
                    c.drawPath(ar, wb.marker(GRAY, 3))
                K.text(c, "印子", 0, 170, 48, "hand", GRAY)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, scene), "wood_low", 0.6)
    b.hit(j, k_press, "wood_high", 0.65, "想按“改”")
    b.hit(j, k_mark, "pop", 0.7, "想留下自己的印子")
    L.stamp_ev(j, k_3, "三步", cx + 230, cy + 140, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


GRAY_FILL = "#D9DCE1"
screen10()


# ================================================================ 屏 11：第一步：第一个月照旧跑一遍，每条规矩旁边写“为什么”
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 0)
    GY = cy + 520
    k_cal = kq(j, wp(18, 0, 0.6), 1)
    k_run = nx(j, wp(18, 1, 0.5), k_cal)
    k_why = nx(j, wp(18, 3, 0.4), k_run)
    L.note("第一个月", "为什么？")

    def scene(c, kk, T):
        tc, tr, tw = tb(j, k_cal), tb(j, k_run), tb(j, k_why)
        g = pop_scale(T - tc)
        if g <= 0:
            return None
        with K.at(c, cx - 300, cy - 250, 0, g):
            box(c, 0, 0, 260, 200, "#FFFFFF", BLACK, 6, 10)
            c.drawRect(skia.Rect.MakeXYWH(-130, -100, 260, 50), K.paint(BLUE_FILL))
            K.text(c, "第一个月", 0, 30, 50, "hand", BLUE)
        with K.at(c, cx + 200, cy - 120, 0, g):
            pts = flowchart(c, 0, 0, ["ok", "ok", None, None] if T >= tr + 0.4 else None)
            if T >= tr:
                fw = clamp01((T - tr) / 1.0)
                seg = min(2, int(fw * 3))
                u = fw * 3 - seg
                c.drawCircle(lerp(pts[seg][0], pts[seg + 1][0], u), lerp(pts[seg][1], pts[seg + 1][1], u), 18, K.paint(RED))
            if T >= tw:
                for i, (px, py) in enumerate(pts):
                    a = clamp01((T - tw - i * 0.1) / 0.2)
                    K.text(c, "为什么？", px, py - 80, 32, "hand", ORANGE, a)
        LX = cx - 380
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.95, "flat", rh=(LX + 140, GY - 300) if T >= tw else None)
        return None
    ev(j, k_cal, scene, "wood_high", 0.65)
    b.hit(j, k_run, "shaker", 0.7, "照旧跑一遍")
    b.hit(j, k_why, "pop", 0.75, "弄清为什么")


screen11()


# ================================================================ 屏 12：第二步：流程图大部分打勾留下，一两处卡住的红圈改掉
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 1)
    GY = cy + 520
    k_flow = kq(j, wp(19, 0, 0.6), 1)
    k_keep = nx(j, wp(19, 0, 0.95), k_flow)
    k_fix = nx(j, wp(19, 2, 0.4), k_keep)
    L.note("留下", "改")

    def scene(c, kk, T):
        tf, tk, tx = tb(j, k_flow), tb(j, k_keep), tb(j, k_fix)
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        marks = [None] * 4
        if T >= tk:
            marks = ["ok", "ok", None, "ok"]
        if T >= tx:
            marks[2] = "fix"
        with K.at(c, cx, cy - 80, 0, g * 1.4):
            flowchart(c, 0, 0, marks)
        if T >= tk:
            K.text(c, "留下", cx - 300, cy + 180, 56, "hand", GREEN, clamp01((T - tk) / 0.2))
        if T >= tx:
            with K.at(c, cx + 330, cy + 180, -5, C.slam_scale(T - tx)):
                chip(c, 0, 0, "改", RED_FILL, RED, 60)
        LX = cx - 380
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.85, "smile" if T >= tx else "flat")
        return None
    ev(j, k_flow, scene, "wood_high", 0.65)
    b.hit(j, k_keep, "ding", 0.7, "顺手的留下")
    b.hit(j, k_fix, "rim", 0.8, "卡住的改一两处")


screen12()


# ================================================================ 屏 13：第三步：改之前先给老同事、老客户打个招呼
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 2)
    GY = cy + 520
    k_li = kq(j, wp(20, 0, 0.6), 1)
    k_col = nx(j, wp(20, 1, 0.3), k_li)
    k_cli = nx(j, wp(20, 1, 0.8), k_col)
    k_hi = nx(j, wp(20, 2, 0.4), k_cli)
    L.note("下周改这一步", "好")
    LX = cx - 80

    def scene(c, kk, T):
        tl, tco, tcl, th = tb(j, k_li), tb(j, k_col), tb(j, k_cli), tb(j, k_hi)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.9, "smile", rh=(LX + 140, GY - 300) if T >= th else (LX + 100, GY - 280))
        if T >= tco:
            with at_pop(c, cx - 380, GY, pop_scale(T - tco)):
                draw_wang(c, cx - 380, GY, 0.85, mood="smile" if T >= th else "flat")
        if T >= tcl:
            with K.at(c, cx + 340, cy + 50, 0, pop_scale(T - tcl)):
                box(c, 0, 0, 140, 240, "#FFFFFF", BLACK, 6, 20)
                c.drawCircle(0, -40, 40, wb.marker(GRAY, 5))
                C.line(c, (-20, 40), (20, 40), GRAY, 5)
        if T >= th:
            with K.at(c, cx + 60, cy - 300, 0, C.slam_scale(T - th)):
                bubble_box(c, 0, 0, 480, 130, -1)
                K.text(c, "下周改这一步", 0, 0, 56, "hand", INK)
            K.text(c, "好", cx - 380, cy - 60, 70, "hand", GREEN, clamp01((T - th - 0.3) / 0.2))
        return None
    ev(j, k_li, scene, "wood_low", 0.6)
    b.hit(j, k_col, "pop", 0.7, "老同事")
    b.hit(j, k_cli, "pop", 0.7, "老客户")
    b.hit(j, k_hi, "ding", 0.8, "打个招呼")


screen13()


# ================================================================ 屏 14：好处：交接线不断，事情一路往前走
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_line = kq(j, wp(21, 0, 0.6), 0)
    k_go = nx(j, wp(21, 1, 0.5), k_line)
    k_team = nx(j, wp(21, 2, 0.5), k_go)
    L.note("不断档")

    def scene(c, kk, T):
        tl, tg, tt = tb(j, k_line), tb(j, k_go), tb(j, k_team)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        f = ease_out(clamp01((T - tl) / 0.6))
        C.line(c, (cx - 540, cy - 80), (lerp(cx - 540, cx + 540, f), cy - 80), GREEN, 10)
        K.text(c, "不断档", cx, cy - 170, 60, "hand", GREEN, f)
        for i in range(4):
            x = cx - 450 + i * 300
            box(c, x, cy - 80, 90, 60, NOTE_FILL, ORANGE, 4, 8, clamp01(f * 4 - i))
        if T >= tg:
            fx = ease_in_out(clamp01((T - tg) / 1.4))
            c.drawCircle(lerp(cx - 450, cx + 450, fx), cy - 80, 26, K.paint(RED))
        if T >= tt:
            for i, x in enumerate((cx - 300, cx, cx + 300)):
                with at_pop(c, x, GY, pop_scale(T - tt - i * 0.1)):
                    if i == 1:
                        draw_wang(c, x, GY, 0.8, mood="smile", rh=(x + 80, GY - 300))
                    else:
                        draw_li(c, x, GY, 0.8, "smile", rh=(x + 80, GY - 300))
        return None
    ev(j, k_line, scene, "wood_high", 0.65)
    b.hit(j, k_go, "shaker", 0.7, "事情往前走")
    b.hit(j, k_team, "ding", 0.8, "大家愿意配合")


screen14()


# ================================================================ 屏 15：评论区；小李稳稳站住再动手；下一讲预告
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z_))
    k_cmt = 0
    k_chips = nx(j, wp(23, 0, 0.3), 0)
    k_li = nx(j, wp(24, 0, 0.4), k_chips)
    k_base = nx(j, wp(24, 4, 0.3), k_li)
    k_next = nx(j, wp(25, 1, 0.2), k_base)
    b.move(j, k_li, (cx, cy + 380, Z_), 1.1)
    CH = ["先列清单", "问老同事", "全推翻了"]
    L.note("最乱的一摊活？", *CH, "下一讲", "说过你坏话的人", "还能共事吗？", "有底")
    BY = cy - 330

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 20, BY, 0, sc):
            bubble_box(c, 0, 0, 1000, 360, -1)
            K.text(c, "最乱的一摊活？", 0, -110, 62, "hand", RED)
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
    LX, LY = cx - 250, cy + 640

    def li(c, kk, T):
        tl, tb_ = tb(j, k_li), tb(j, k_base)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with at_pop(c, LX, LY, g):
            box(c, LX, LY + 10, 300, 30, "#C9A97A", "#7A5E3A", 5, 6)
            draw_li(c, LX, LY - 20, 0.95, "smile" if T >= tb_ else "flat", rh=(LX + 150, LY - 300) if T >= tb_ else None)
        if T >= tb_:
            sparkle(c, LX, LY - 380, T - tb_, YELLOW, 10, 60, 130)
            K.text(c, "有底", LX + 330, LY - 200, 76, "hand", GREEN, clamp01((T - tb_ - 0.2) / 0.2))
        return None
    ev(j, k_li, li, "wood_low", 0.6)
    b.hit(j, k_base, "ding", 0.8, "稳住了")

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
            K.text(c, "说过你坏话的人", -90, -60, 58, "hand", BLACK)
            K.text(c, "还能共事吗？", -110, 40, 58, "hand", BLACK)
            for q in range(3):
                box(c, 380 + q * 10, 20 - q * 14, 140, 90, PARCH, PARCH_LINE, 4, 4)
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen15()

# ================================================================ 收尾
L.finish(cover_shot=7, square_shot=8, notes=NOTES)
L.export(globals())
