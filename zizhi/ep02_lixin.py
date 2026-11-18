"""《资治通鉴》02 立信：说出去的话，为什么没人当真？（白板手绘 + AI 旁白，竖屏 2:3）

倒叙：先看结果——秦都南门口一个人扛着长木走到北门，当场拿到五十金；再倒回去：卫鞅新法写好先不发、立木赏十金没人搬、
加到五十金有人搬、马上兑现、这才下令；太子犯法，罚太子的两位老师；十年后路不拾遗。司马光“信者，人君之大宝也”，
并举魏文侯冒雨赴约。今人部分：群里没人回、规矩没人守、答应的事拖两回；三步攒信用、评论区、下一讲。
古人的屏画在卷轴框里（左上角朱印“通鉴”），今人在办公室；今人不戴安全帽。
文案见 zizhi/PLAN.md「### 02」。
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
from zizhi.lesson import (BLACK, BLUE, BLUE_FILL, GRAY, GREEN, GREEN_FILL, INK, NOTE_FILL, ORANGE, RED, RED_FILL, WATER_LINE,
                          YELLOW, at_pop, bamboo_slips, box, bubble_box, city_wall, cup, desk, draw_li, draw_wang, flag, gu,
                          head_of, pop_scale, seal, slip_text, sparkle)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "身边的例子", 2),
    ([3], "身边的例子", 3),
    ([4], "身边的例子", 4),
    ([5, 6], "先看结果", 5),
    ([7, 8], "通鉴里的故事", 6),
    ([9, 10], "变法之前", 7),
    ([11, 12], "立木", 8),
    ([13, 14], "五十金", 9),
    ([15], "新法下令", 10),
    ([16, 17], "太子犯法", 11),
    ([18, 19], "十年之后", 12),
    ([20], "司马光点评", 13),
    ([21, 22], "魏文侯守约", 14),
    ([23, 24], "说回我们自己", 15),
    ([25], "第一步", 16),
    ([26], "第二步", 17),
    ([27], "第三步", 18),
    ([28], "好处", 19),
    ([29, 30, 31, 32], "评论区见", 20),
]

THEME = ZT.get("02")
L = Z.Lesson("02", SCREENS, drop_screen=2, board_size=(5000, 14000), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(19)]
Z_ = 0.72

NOTES = [
    "出处：司马光《资治通鉴》卷二 周纪二（显王十年）徙木立信与“臣光曰”；魏文侯与虞人期猎见卷一 周纪一。",
    "原文：“恐民之不信己，乃立三丈之木于国都市南门，募民有能徙置北门者予十金。民怪之，莫敢徙。复曰：能徙者予五十金。"
    "有一人徙之，辄予五十金。乃下令。”“太子犯法……刑其傅公子虔，黥其师公孙贾。明日，秦人皆趋令。行之十年，秦国道不拾遗，山无盗贼。”"
    "臣光曰“夫信者，人君之大宝也……魏文侯不弃虞人之期，秦孝公不废徙木之赏”；文侯“吾与虞人期猎……乃往，身自罢之”。",
    "旁白用通鉴原文的“卫鞅”，说明“就是后来的商鞅”。今人（小李、小王、同事）为虚构示意；古人造型为示意。",
]

WEIYANG, MIN, CARRIER, PRINCE, WENHOU, YUREN = "teal", "gray", "ochre", "red", "blue", "green"
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


def gate(c, x, y, label, a=1.0):
    """城门（小）：(x, y) 墙脚中点，门楣写南门 / 北门。"""
    city_wall(c, x, y, 300, 330, a)
    box(c, x, y - 380, 170, 66, PARCH, PARCH_LINE, 5, 6, a)
    K.text(c, label, x, y - 378, 48, "serif_black", INK, a)


def log_(c, x, y, ang=0.0, ln=520, a=1.0):
    """长木（三丈木，示意）：中心 (x, y)。"""
    with K.at(c, x, y, ang):
        c.drawRoundRect(skia.Rect.MakeXYWH(-ln / 2, -18, ln, 36), 18, 18, K.paint("#C98B4B", a))
        c.drawRoundRect(skia.Rect.MakeXYWH(-ln / 2, -18, ln, 36), 18, 18, wb.marker("#7A4A1E", 5, a))
        for q in range(3):
            C.line(c, (-ln / 2 + 80 + q * 150, -6), (-ln / 2 + 140 + q * 150, 4), "#7A4A1E", 3, a)


def coins(c, x, y, n=5, a=1.0):
    for i in range(n):
        c.drawOval(skia.Rect.MakeXYWH(x - 40 + (i % 3) * 10, y - i * 16, 80, 30), K.paint(YELLOW, a))
        c.drawOval(skia.Rect.MakeXYWH(x - 40 + (i % 3) * 10, y - i * 16, 80, 30), wb.marker("#A9842A", 4, a))


def notice(c, x, y, lines, a=1.0, w=360, size=50, hot=None):
    """木牌告示：lines 为几行字；hot 为要标红的行号。"""
    C.line(c, (x, y + 120), (x, y + 300), "#7A4A1E", 10, a)
    box(c, x, y, w, 70 + len(lines) * size * 1.2, PARCH, "#7A4A1E", 6, 8, a)
    for i, s_ in enumerate(lines):
        yy = y + (i - (len(lines) - 1) / 2) * size * 1.2
        K.text(c, s_, x, yy, size, "serif_black", RED if hot == i else INK, a)


def phone(c, x, y, s=1.0, a=1.0):
    with K.at(c, x, y, 0, s):
        box(c, 0, 0, 90, 160, "#FFFFFF", BLACK, 5, 14, a)
        c.drawRect(skia.Rect.MakeXYWH(-34, -60, 68, 110), K.paint(BLUE_FILL, a))


# ================================================================ 屏 0：开场（zizhi/hooks.py zz_unread）
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：小李在群里发通知，同事看完走开；说了三遍，最后自己扛箱子
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_away = kq(j, wp(0, 2, 0.4), 1)
    k_3 = [nx(j, wp(1, 0, 0.3), k_away)]
    k_3.append(cap(j, k_3[0] + 1))
    k_box = nx(j, wp(1, 2, 0.4), k_3[-1])
    L.note("第1遍", "第2遍", "第3遍")
    LX = cx - 330

    def li(c, sc, T):
        tb_ = tb(j, k_box)
        carry = T >= tb_
        hy = GY - 290
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 1.0, "sad" if carry else "flat",
                    lh=(LX - 80, hy - 70) if carry else None, rh=(LX + 80, hy - 70) if carry else (LX + 90, hy + 130))
            if carry:
                d = 30 * (1 - ease_out(clamp01((T - tb_) / 0.3)))
                c.drawPath(C.box_path(LX, hy - 60 - d, 220, 150), K.paint("#E7C99A"))
                c.drawPath(C.box_path(LX, hy - 60 - d, 220, 150), wb.marker("#8B6B43", 6))
            else:
                phone(c, LX + 100, hy + 110, 0.8)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, li), "wood_high", 0.6)

    def crowd(c, kk, T):
        ta = tb(j, k_away)
        for i, x0 in enumerate((cx + 60, cx + 250, cx + 440)):
            g = pop_scale(T - tb(j, 0) - 0.2 - i * 0.1)
            if g <= 0:
                continue
            x, dy, moving = C.walk(T, ta + i * 0.1, 0.9, x0, x0 + 40, 8)
            with at_pop(c, x, GY + dy, g):
                if i == 1:
                    draw_wang(c, x, GY + dy, 0.8)
                else:
                    draw_li(c, x, GY + dy, 0.8, back=T >= ta)
                if T < ta:
                    phone(c, x + 60, GY - 200, 0.6)
        return None
    b.custom(j, 0, 0.3, crowd)
    b.hit(j, k_away, "wood_low", 0.7, "看完就走开")

    def bubbles(c, kk, T):
        for i in range(3):
            t0 = tb(j, k_3[min(i, len(k_3) - 1)]) + (0.27 if i == 2 else 0)
            if i == 1 and len(k_3) > 1:
                t0 = tb(j, k_3[1])
            g = pop_scale(T - t0)
            if g <= 0:
                continue
            with K.at(c, LX + 80 + i * 60, cy - 420 + i * 130, (i - 1) * 3, g):
                bubble_box(c, 0, 0, 260, 110, -1)
                K.text(c, f"第{i + 1}遍", 0, 0, 52, "hand", RED if i == 2 else INK)
        return None
    ev(j, k_3[0], bubbles, "pop", 0.65)
    for k_ in k_3[1:]:
        b.hit(j, k_, "pop", 0.7, "又说一遍")
    b.hit(j, k_box, "tom", 0.75, "自己扛箱子")


screen1()


# ================================================================ 屏 2（drop）：小李的话变成羽毛飘下来，落在秤上，秤针不动——“分量”
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    dk = L.drop_k()
    k_li = 0
    k_feather = kq(j, wp(2, 0, 0.5), 1)
    L.note("分量", "0")
    SX, SY = cx + 180, cy + 300

    def li(c, sc, T):
        with at_pop(c, cx - 380, GY, sc):
            hy = GY - 290
            draw_li(c, cx - 380, GY, 0.95, "sad", rh=(cx - 300, hy + 20))
        return None
    ev(j, k_li, L.pop_fn(j, k_li, li), "wood_low", 0.6)

    def scale(c, kk, T):
        g = pop_scale(T - tb(j, 0) - 0.2)
        if g <= 0:
            return None
        with at_pop(c, SX, SY + 200, g):
            box(c, SX, SY + 80, 360, 200, "#FFFFFF", BLACK, 7, 24)
            c.drawCircle(SX, SY + 80, 70, K.paint("#FFFFFF"))
            c.drawCircle(SX, SY + 80, 70, wb.marker(GRAY, 5))
            td = tb(j, dk)
            wob = 4 * math.exp(-max(0, T - td) * 6) * math.sin(max(0, T - td) * 30) if T >= td else 0
            a = math.radians(-90 + wob)
            C.line(c, (SX, SY + 80), (SX + 55 * math.cos(a), SY + 80 + 55 * math.sin(a)), RED, 6)
            K.text(c, "0", SX, SY + 140, 40, "sans_medium", GRAY)
            box(c, SX, SY - 30, 420, 30, GRAY, BLACK, 5, 10)
            K.text(c, "分量", SX + 260, SY + 80, 56, "hand", INK)
        return None
    b.custom(j, 0, 0.3, scale)

    def feather(c, kk, T):
        tf, td = tb(j, k_feather), tb(j, dk)
        if T < tf:
            return None
        f = clamp01((T - tf) / max(0.3, td - tf))
        x = lerp(cx - 250, SX, f) + 60 * math.sin(f * 9) * (1 - f)
        y = lerp(cy - 380, SY - 70, ease_in_out(f))
        ang = 30 * math.sin(f * 8) * (1 - f)
        with K.at(c, x, y, ang):
            p = skia.Path()
            p.moveTo(-90, 0)
            p.cubicTo(-40, -50, 50, -40, 90, 0)
            p.cubicTo(50, 30, -40, 30, -90, 0)
            c.drawPath(p, K.paint("#FFFFFF"))
            c.drawPath(p, wb.marker(GRAY, 4))
            C.line(c, (-110, 6), (90, 0), GRAY, 4)
        if T < tf + 0.6:
            g = pop_scale(T - tf + 0.3) * (1 - clamp01((T - tf - 0.3) / 0.3))
            with K.at(c, cx - 250, cy - 380, 0, g):
                bubble_box(c, 0, 0, 280, 110, -1)
                K.text(c, "说好了", 0, 0, 52, "hand", INK)
        return None
    L.note("说好了")
    ev(j, k_feather, feather, "shaker", 0.65)
    b.hit(j, dk, "kick", 0.9, "羽毛落秤，秤针不动")
    b.shots[j].shake = [(dk, 10.0)]
    b.shots[j].flashes = [(dk, 0.25)]


screen2()


# ================================================================ 屏 3：小组长小李贴出规矩，同事从旁边绕过去
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = kq(j, wp(3, 0, 0.5), 0)
    k_rule = nx(j, wp(3, 1, 0.5), k_li)
    k_pass = nx(j, wp(3, 2, 0.4), k_rule)
    L.note("组长", "九点开会")
    LX = cx - 400

    def li(c, sc, T):
        with at_pop(c, LX, GY, sc):
            hy = GY - 290
            draw_li(c, LX, GY, 0.95, "flat" if T < tb(j, k_pass) else "sad", rh=(LX + 120, hy + 40))
            box(c, LX - 30, hy + 140, 90, 40, RED_FILL, RED, 4, 6)
            K.text(c, "组长", LX - 30, hy + 142, 30, "sans_medium", RED)
        return None
    ev(j, k_li, L.pop_fn(j, k_li, li), "wood_high", 0.6)

    def rule(c, kk, T):
        g = C.slam_scale(T - tb(j, k_rule))
        if g <= 0:
            return None
        with K.at(c, cx - 60, cy - 220, -2, g):
            box(c, 0, 0, 420, 260, "#FFFFFF", BLUE, 7, 14)
            c.drawCircle(0, -130, 16, K.paint(RED))
            K.text(c, "九点开会", 0, 10, 72, "hand", BLUE)
        return None
    ev(j, k_rule, rule, "rim", 0.8)

    def walkers(c, kk, T):
        tp = tb(j, k_pass)
        for i in range(2):
            x, dy, _ = C.walk(T, tp + i * 0.25, 1.4, cx + 520, cx + 40 - i * 40, 10)
            if T < tp + i * 0.25:
                x = cx + 520
            g = pop_scale(T - tp - i * 0.25 + 0.3)
            if g <= 0:
                continue
            arc = -120 * math.sin(clamp01((cx + 520 - x) / 480) * math.pi)
            with at_pop(c, x, GY + dy + arc * 0.2, g):
                if i == 0:
                    draw_wang(c, x, GY + dy, 0.85, mood="flat")
                else:
                    draw_li(c, x, GY + dy, 0.85, "flat", back=True)
        return None
    b.custom(j, k_pass, k_pass + 0.3, walkers, sfx="shaker", gain=0.6)


screen3()


# ================================================================ 屏 4：日历上两个红圈“拖”，同事听小李说话只是笑笑
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_cal = 0
    k_d = [kq(j, wp(4, 1, 0.2), 1)]
    k_d.append(cap(j, k_d[0] + 1))
    k_talk = nx(j, wp(4, 2, 0.4), k_d[-1])
    k_smile = nx(j, wp(4, 3, 0.4), k_talk)
    L.note("拖", "这次一定", "呵呵")
    CX_, CY_ = cx - 140, cy - 260

    def cal(c, kk, T):
        g = pop_scale(T - tb(j, k_cal))
        if g <= 0:
            return None
        with K.at(c, CX_, CY_, 0, g):
            box(c, 0, 0, 640, 420, "#FFFFFF", BLACK, 7, 16)
            c.drawRect(skia.Rect.MakeXYWH(-320, -210, 640, 70), K.paint(RED_FILL))
            for r in range(3):
                for q in range(6):
                    c.drawRect(skia.Rect.MakeXYWH(-290 + q * 97, -120 + r * 105, 80, 85), wb.marker(GRAY, 3))
            for i, (q, r) in enumerate(((1, 0), (4, 1))):
                ti = tb(j, k_d[min(i, len(k_d) - 1)])
                if T >= ti:
                    f = ease_out(clamp01((T - ti) / 0.3))
                    ring = skia.Path()
                    ring.addOval(skia.Rect.MakeXYWH(-300 + q * 97, -130 + r * 105, 100, 105))
                    c.drawPath(wb.partial(ring, f)[0], wb.marker(RED, 8))
                    K.text(c, "拖", -250 + q * 97, -78 + r * 105, 50, "hand", RED, f)
        return None
    ev(j, k_cal, cal, "wood_high", 0.6)
    for k_ in k_d:
        b.hit(j, k_, "rim", 0.75, "又拖一回")

    def people(c, kk, T):
        tt, ts = tb(j, k_talk), tb(j, k_smile)
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        LX, WX = cx - 300, cx + 280
        with at_pop(c, LX, GY, g):
            draw_li(c, LX, GY, 0.9, "flat", rh=(LX + 110, GY - 300))
        with at_pop(c, WX, GY, g):
            draw_wang(c, WX, GY, 0.9, mood="smile" if T >= ts else "flat")
        with K.at(c, LX + 90, cy + 70, 0, g):
            bubble_box(c, 0, 0, 300, 110, -1)
            K.text(c, "这次一定", 0, 0, 52, "hand", INK)
        if T >= ts:
            gs = pop_scale(T - ts)
            with K.at(c, WX + 60, cy + 70, 0, gs):
                bubble_box(c, 0, 0, 220, 110, 1)
                K.text(c, "呵呵", 0, 0, 56, "hand", GRAY)
        return None
    b.custom(j, k_talk, k_talk + 0.3, people, sfx="pop", gain=0.6)
    b.hit(j, k_smile, "wood_low", 0.7, "人家只是笑笑")


screen4()


# ================================================================ 屏 5：先看结果——南门到北门，一个人扛木走过去，当场拿到五十金
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 470
    k_gates = kq(j, wp(5, 1, 0.3), 0)
    k_lift = nx(j, wp(5, 2, 0.3), k_gates)
    k_arrive = nx(j, wp(5, 3, 0.4), k_lift)
    k_gold = nx(j, wp(6, 1, 0.4), k_arrive)
    L.note("南门", "北门", "五十金", "秦")
    SX, NX_ = cx - 380, cx + 380

    def gates(c, kk, T):
        g = pop_scale(T - tb(j, k_gates), 0.4)
        if g <= 0:
            return None
        with at_pop(c, cx, GY, g):
            gate(c, SX, GY - 30, "南门")
            gate(c, NX_, GY - 30, "北门")
            C.line(c, (cx - 560, GY), (cx + 560, GY), "#8B6B43", 6)
            flag(c, cx, GY - 330, 0.5, "秦", "#2B4C6F", 1.0, math.sin(T * 3))
        return None
    ev(j, k_gates, gates, "muyu", 0.7)

    def man(c, kk, T):
        tl, ta = tb(j, k_lift), tb(j, k_arrive)
        g = pop_scale(T - tl + 0.3)
        if g <= 0:
            return None
        x, dy, _ = C.walk(T, tl, max(0.4, ta - tl), SX + 130, NX_ - 150, 12)
        s = 0.8
        hy = GY + dy - 290 * s
        tg = tb(j, k_gold)
        with at_pop(c, x, GY + dy, g):
            if T < tg:
                gu(c, x, GY + dy, s, CARRIER, hat="bun", lh=(x - 50, hy - 20), rh=(x + 50, hy - 20))
                log_(c, x, hy - 40, -6, 520)
            else:
                gu(c, x, GY + dy, s, CARRIER, hat="bun", mood="laugh", rh=(x + 90, hy + 60))
                log_(c, x - 150, GY - 30, 0, 420)
                coins(c, x + 110, hy + 50, 4)
        if T >= tg:
            sparkle(c, x + 110, hy, T - tg, YELLOW, 10, 60, 140)
            gg = C.slam_scale(T - tg)
            with K.at(c, cx, cy - 380, 0, gg):
                K.text(c, "五十金", 0, 0, 110, "hand", RED)
        return None
    b.custom(j, k_lift, k_lift + 0.3, man, sfx="wood_low", gain=0.7)
    b.hit(j, k_arrive, "tom", 0.75, "走到北门")
    b.hit(j, k_gold, "ding", 0.9, "当场拿到五十金")
    b.shots[j].shake = [(k_gold, 7.0)]


screen5()


# ================================================================ 屏 6：问号；竹简“资治通鉴 卷二”；卫鞅出场
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_q = kq(j, wp(7, 1, 0.3), 0)
    k_slip = nx(j, wp(8, 0, 0.4), k_q)
    k_wei = nx(j, wp(8, 2, 0.3), k_slip)
    k_shang = nx(j, wp(8, 3, 0.4), k_wei)
    L.note("？", "资治通鉴", "卷二", "周纪二", "卫鞅", "商鞅")

    def q(c, kk, T):
        g = C.slam_scale(T - tb(j, k_q))
        if g > 0:
            with K.at(c, cx + 300, cy - 380, 8, g):
                K.text(c, "？", 0, 0, 200, "hand", RED)
        return None
    ev(j, k_q, q, "rim", 0.75)
    SX = cx - 280

    def slips(c, kk, T):
        f = ease_out(clamp01((T - tb(j, k_slip)) / 0.6))
        if f <= 0:
            return None
        bamboo_slips(c, SX, cy - 40, max(60, 420 * f), 820, n=max(1, int(6 * f)))
        a = clamp01((T - tb(j, k_slip) - 0.3) / 0.3)
        slip_text(c, SX + 70, cy - 360, "资治通鉴", 92, "#3A2A12", a)
        slip_text(c, SX - 80, cy - 320, "卷二", 70, RED, a)
        slip_text(c, SX - 80, cy - 100, "周纪二", 54, "#5E4128", a, 1.15)
        return None
    ev(j, k_slip, slips, "muyu", 0.7, 0.6)

    def wei(c, sc, T):
        x = cx + 280
        with at_pop(c, x, GY, sc):
            gu(c, x, GY, 1.05, WEIYANG, hat="guan", beard="black")
            name_tag(c, x, GY - 430, "卫鞅", "#2C6E68", 56)
        if T >= tb(j, k_shang):
            g = pop_scale(T - tb(j, k_shang))
            with K.at(c, x + 130, GY - 330, 6, g):
                chip(c, 0, 0, "商鞅", RED_FILL, RED, 44)
        return None
    ev(j, k_wei, L.pop_fn(j, k_wei, wei), "tom", 0.8)
    b.hit(j, k_shang, "pop", 0.7, "就是后来的商鞅")


screen6()


# ================================================================ 屏 7：卫鞅手里一卷新法，先收起来；老百姓头顶问号
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_wei = 0
    k_law = kq(j, wp(9, 2, 0.3), 1)
    k_hold = nx(j, wp(9, 3, 0.5), k_law)
    k_min = nx(j, wp(10, 1, 0.3), k_hold)
    L.note("新法", "？")
    WX = cx - 300

    def wei(c, sc, T):
        th = tb(j, k_hold)
        hy = GY - 290
        with at_pop(c, WX, GY, sc):
            gu(c, WX, GY, 1.0, WEIYANG, hat="guan", beard="black",
               rh=(WX + 130, hy + 60) if T < th else (WX + 30, hy + 140), mood="flat")
        tl = tb(j, k_law)
        if T >= tl:
            f = ease_in_out(clamp01((T - th) / 0.4)) if T >= th else 0
            g = pop_scale(T - tl)
            x, y = lerp(WX + 230, WX + 60, f), lerp(cy - 100, GY - 160, f)
            with K.at(c, x, y, lerp(0, 70, f), g * lerp(1, 0.45, f)):
                bamboo_slips(c, 0, 0, 280, 340, n=4)
                slip_text(c, 0, -70, "新法", 72, RED)
        return None
    ev(j, k_wei, L.pop_fn(j, k_wei, wei), "muyu", 0.6)
    b.hit(j, k_law, "wood_high", 0.7, "新法写好")
    b.hit(j, k_hold, "wood_low", 0.7, "先收起来")

    def people(c, kk, T):
        tm = tb(j, k_min)
        for i, x in enumerate((cx + 160, cx + 330, cx + 490)):
            g = pop_scale(T - tm - i * 0.1)
            if g <= 0:
                continue
            with at_pop(c, x, GY, g):
                gu(c, x, GY, 0.7, MIN if i != 1 else "brown", hat="bun", mood="o")
            K.text(c, "？", x + 20, GY - 300, 80, "hand", RED, clamp01(g))
        return None
    ev(j, k_min, people, "pop", 0.7)


screen7()


# ================================================================ 屏 8：南门立三丈木，告示“搬到北门 赏十金”；围观的人摇头，没人动
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_log = kq(j, wp(11, 1, 0.3), 0)
    k_note = nx(j, wp(11, 2, 0.4), k_log)
    k_ten = nx(j, wp(11, 3, 0.3), k_note)
    k_shake = nx(j, wp(12, 0, 0.5), k_ten)
    k_none = nx(j, wp(12, 1, 0.5), k_shake)
    L.note("南门", "搬到北门", "赏十金", "三丈", "没人搬")
    LX = cx - 160

    def scene(c, kk, T):
        g = pop_scale(T - tb(j, 0), 0.4)
        if g > 0:
            with at_pop(c, cx, GY, g):
                gate(c, cx - 400, GY, "南门")
        tl = tb(j, k_log)
        if T >= tl:
            f = ease_out(clamp01((T - tl) / 0.4))
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(LX - 60, GY - 860 * f, LX + 60, GY + 10))
            log_(c, LX, GY - 430, 90, 860)
            c.restore()
            if f >= 1:
                K.text(c, "三丈", LX + 90, GY - 640, 50, "hand", "#7A4A1E")
        tn = tb(j, k_note)
        if T >= tn:
            gn = pop_scale(T - tn)
            with K.at(c, cx + 250, cy - 290, 0, gn):
                notice(c, 0, 0, ["搬到北门", "赏十金"], 1.0, 380, 56, 1 if T >= tb(j, k_ten) else None)
        return None
    ev(j, k_log, scene, "tom", 0.75)
    b.hit(j, k_note, "wood_high", 0.7, "告示")
    b.hit(j, k_ten, "ding", 0.6, "赏十金")

    def crowd(c, kk, T):
        ts, tn = tb(j, k_shake), tb(j, k_none)
        for i, x in enumerate((cx + 60, cx + 230, cx + 400)):
            g = pop_scale(T - tb(j, 0) - 0.3 - 0.1 * i)
            if g <= 0:
                continue
            hd = 10 * math.sin((T - ts) * 14) * math.exp(-(T - ts) * 1.5) if T >= ts else 0
            with at_pop(c, x, GY, g):
                gu(c, x, GY, 0.7, MIN if i % 2 == 0 else "brown", hat="bun", mood="o" if T >= ts else "flat",
                   head_dx=hd)
        if T >= tn:
            seal(c, cx + 230, cy + 110, "没人搬", 56, -6, C.slam_scale(T - tn))
        return None
    b.custom(j, 0, 0.3, crowd)
    b.hit(j, k_shake, "shaker", 0.7, "摇头")
    b.hit(j, k_none, "kick", 0.8, "没一个人敢搬")


screen8()


# ================================================================ 屏 9：告示改成五十金；有人扛木到北门，卫鞅马上递上钱
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_note = 0
    k_fifty = kq(j, wp(13, 1, 0.3), 1)
    k_go = nx(j, wp(14, 0, 0.4), k_fifty)
    k_pay = nx(j, wp(14, 1, 0.5), k_go)
    L.note("赏十金", "五十金", "北门")
    NX_ = cx + 380

    def board(c, kk, T):
        g = pop_scale(T - tb(j, k_note))
        if g <= 0:
            return None
        with K.at(c, cx - 300, cy - 300, 0, g):
            notice(c, 0, 0, ["搬到北门", "赏十金"], 1.0, 380, 56)
            tf = tb(j, k_fifty)
            if T >= tf:
                f = ease_out(clamp01((T - tf) / 0.2))
                C.line(c, (-110, 34), (-110 + 220 * f, 34), RED, 9)
                with K.at(c, 30, 110, -8, C.slam_scale(T - tf)):
                    box(c, 0, 0, 260, 90, RED_FILL, RED, 6, 12)
                    K.text(c, "五十金", 0, 2, 64, "hand", RED)
        return None
    ev(j, k_note, board, "wood_high", 0.6)
    b.hit(j, k_fifty, "kick", 0.85, "改成五十金")

    def walk(c, kk, T):
        tg, tp = tb(j, k_go), tb(j, k_pay)
        g = pop_scale(T - tg + 0.3)
        gg = pop_scale(T - tb(j, 0) - 0.2)
        if gg > 0:
            with at_pop(c, NX_, GY, gg):
                gate(c, NX_, GY, "北门")
        if g <= 0:
            return None
        x, dy, _ = C.walk(T, tg, max(0.4, tp - tg - 0.1), cx - 420, NX_ - 260, 12)
        s = 0.78
        hy = GY + dy - 290 * s
        with at_pop(c, x, GY + dy, g):
            if T < tp:
                gu(c, x, GY + dy, s, CARRIER, hat="bun", lh=(x - 50, hy - 20), rh=(x + 50, hy - 20))
                log_(c, x, hy - 40, -6, 480)
            else:
                gu(c, x, GY + dy, s, CARRIER, hat="bun", mood="laugh", rh=(x + 80, hy + 60))
                coins(c, x + 100, hy + 50, 4)
        if T >= tp:
            wx = x - 220
            gw = pop_scale(T - tp)
            with at_pop(c, wx, GY, gw):
                gu(c, wx, GY, 0.85, WEIYANG, hat="guan", beard="black", rh=(wx + 110, GY - 290 * 0.85 + 90))
            sparkle(c, x + 100, hy, T - tp, YELLOW, 10, 60, 140)
        return None
    b.custom(j, k_go, k_go + 0.3, walk, sfx="wood_low", gain=0.7)
    b.hit(j, k_pay, "ding", 0.9, "马上给五十金")


screen9()


# ================================================================ 屏 10：新法竹简盖上大印，贴到城门上
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_wall = 0
    k_law = kq(j, wp(15, 0, 0.6), 1)
    k_seal = nx(j, wp(15, 1, 0.6), k_law)
    L.note("新法", "下令")

    def wall(c, sc, T):
        with at_pop(c, cx, GY, sc):
            city_wall(c, cx, GY, 1000, 560)
        return None
    ev(j, k_wall, L.pop_fn(j, k_wall, wall), "muyu", 0.6)

    def law(c, kk, T):
        tl = tb(j, k_law)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with K.at(c, cx - 60, cy - 160, 0, g):
            bamboo_slips(c, 0, 0, 520, 500, n=7)
            slip_text(c, 0, -170, "新法", 100, INK)
            for q in range(4):
                C.line(c, (-200 + q * 60, 40), (-200 + q * 60, 210), "#5E4128", 4)
        ts = tb(j, k_seal)
        if T >= ts:
            seal(c, cx + 170, cy - 20, "下令", 74, -8, C.slam_scale(T - ts))
        return None
    ev(j, k_law, law, "wood_high", 0.7)
    b.hit(j, k_seal, "kick", 0.85, "盖印下令")
    b.shots[j].shake = [(k_seal, 8.0)]


screen10()


# ================================================================ 屏 11：太子犯法，众人看卫鞅怎么办；太子的两位老师受罚
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 500
    k_prince = kq(j, wp(16, 1, 0.3), 0)
    k_eyes = nx(j, wp(17, 0, 0.5), k_prince)
    k_t1 = nx(j, wp(17, 2, 0.3), k_eyes)
    k_t2 = cap(j, k_t1 + 1)
    L.note("太子", "犯法", "老师", "受罚", "卫鞅")
    PX, WX = cx - 380, cx + 400

    def prince(c, sc, T):
        with at_pop(c, PX, GY, sc):
            gu(c, PX, GY, 0.85, PRINCE, hat="guan", mood="o")
            name_tag(c, PX, GY - 380, "太子", "#9C2F25", 44)
        g = C.slam_scale(T - tb(j, k_prince) - 0.2)
        if g > 0:
            with K.at(c, PX, cy - 300, -6, g):
                chip(c, 0, 0, "犯法", RED_FILL, RED, 54)
        return None
    ev(j, k_prince, L.pop_fn(j, k_prince, prince), "tom", 0.8)

    def wei(c, kk, T):
        g = pop_scale(T - tb(j, 0))
        if g <= 0:
            return None
        with at_pop(c, WX, GY, g):
            gu(c, WX, GY, 0.85, WEIYANG, hat="guan", beard="black", mood="angry" if T >= tb(j, k_t1) else "flat")
            name_tag(c, WX, GY - 380, "卫鞅", "#2C6E68", 40)
        te = tb(j, k_eyes)
        if T >= te:
            for i in range(3):
                x = cx - 120 + i * 120
                y = cy - 420
                gg = pop_scale(T - te - i * 0.08)
                with K.at(c, x, y, 0, gg):
                    c.drawOval(skia.Rect.MakeXYWH(-40, -24, 80, 48), K.paint("#FFFFFF"))
                    c.drawOval(skia.Rect.MakeXYWH(-40, -24, 80, 48), wb.marker(INK, 4))
                    c.drawCircle(14, 0, 12, K.paint(INK))
        return None
    b.custom(j, 0, 0.3, wei)
    b.hit(j, k_eyes, "shaker", 0.65, "都看卫鞅怎么办")

    def teachers(c, kk, T):
        for i, (k_, x) in enumerate(((k_t1, cx - 100), (k_t2, cx + 120))):
            t0 = tb(j, k_)
            g = pop_scale(T - t0 + 0.25)
            if g <= 0:
                continue
            with at_pop(c, x, GY, g):
                gu(c, x, GY, 0.72, "gray", hat="guan", beard="white", mood="sad")
                name_tag(c, x, GY - 320, "老师", "#5E5E58", 34)
            if T >= t0:
                seal(c, x, cy - 160, "受罚", 50, (i * 2 - 1) * 5, C.slam_scale(T - t0))
        return None
    b.custom(j, k_t1, k_t1 + 0.3, teachers)
    b.hit(j, k_t1, "kick", 0.8, "罚第一位老师")
    if k_t2 != k_t1:
        b.hit(j, k_t2, "kick", 0.75, "罚第二位老师")


screen11()


# ================================================================ 屏 12：众人照新法办；路上掉了钱袋没人捡，山里强盗的旗倒了
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 120
    k_line = kq(j, wp(18, 1, 0.3), 0)
    k_purse = nx(j, wp(19, 1, 0.3), k_line)
    k_pass = nx(j, wp(19, 1, 0.9), k_purse)
    k_bandit = nx(j, wp(19, 2, 0.4), k_pass)
    L.note("新法", "十年后", "盗")

    def line(c, kk, T):
        tl = tb(j, k_line)
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with K.at(c, cx - 360, cy - 330, 0, g):
            notice(c, 0, 0, ["新法"], 1.0, 220, 56)
        for i in range(4):
            gi = pop_scale(T - tl - 0.1 * i)
            x = cx - 180 + i * 130
            with at_pop(c, x, GY - 120, gi):
                gu(c, x, GY - 120, 0.55, MIN if i % 2 else "brown", hat="bun")
            if gi > 0.9:
                c.drawPath(check(x, GY - 330, 24), wb.marker(GREEN, 7))
        return None
    ev(j, k_line, line, "wood_high", 0.7)

    def road(c, kk, T):
        tp, tq = tb(j, k_purse), tb(j, k_pass)
        if T < tp:
            return None
        RY = cy + 380
        C.line(c, (cx - 560, RY), (cx + 120, RY), "#8B6B43", 6)
        K.text(c, "十年后", cx - 430, RY - 300, 54, "hand", "#7A4A1E", clamp01((T - tp) / 0.2))
        g = pop_scale(T - tp)
        with K.at(c, cx - 240, RY - 30, 0, g):
            c.drawOval(skia.Rect.MakeXYWH(-50, -40, 100, 70), K.paint("#C98B4B"))
            c.drawOval(skia.Rect.MakeXYWH(-50, -40, 100, 70), wb.marker("#7A4A1E", 5))
            C.line(c, (-20, -40), (20, -40), "#7A4A1E", 6)
        if T >= tq:
            x, dy, _ = C.walk(T, tq, 1.6, cx - 520, cx + 60, 8)
            with at_pop(c, x, RY + dy, 1):
                gu(c, x, RY + dy, 0.55, MIN, hat="bun", head_dx=8)
        return None
    b.custom(j, k_purse, k_purse + 0.3, road, sfx="pop", gain=0.7)
    b.hit(j, k_pass, "wood_low", 0.6, "走过去不捡")

    def mountain(c, kk, T):
        tb_ = tb(j, k_bandit)
        g = pop_scale(T - tb(j, k_line) - 0.3)
        if g <= 0:
            return None
        mx, my = cx + 330, cy + 440
        with at_pop(c, mx, my, g):
            m = P((mx - 220, my), (mx - 60, my - 300), (mx + 40, my - 180), (mx + 120, my - 260), (mx + 220, my), close=True)
            c.drawPath(m, K.paint("#D3E3C8"))
            c.drawPath(m, wb.marker(GREEN, 6))
        f = ease_in_out(clamp01((T - tb_) / 0.4)) if T >= tb_ else 0
        with K.at(c, mx - 60, my - 300, lerp(0, 80, f)):
            flag(c, 0, 0, 0.45, "盗", "#555555", 1.0)
        return None
    b.custom(j, k_line, k_line + 0.3, mountain)
    b.hit(j, k_bandit, "tom", 0.8, "强盗旗倒了")


screen12()


# ================================================================ 屏 13：司马光捧着一颗发光的宝珠“信”
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_sm = 0
    k_xin = kq(j, wp(20, 1, 0.3), 1)
    k_bao = nx(j, wp(20, 3, 0.3), k_xin)
    SX = cx - 260
    L.note("司马光", "信", "宝")

    def sima(c, sc, T):
        hy = GY - 290 * 1.0
        with at_pop(c, SX, GY, sc):
            gu(c, SX, GY, 1.0, "gray", hat="futou", beard="white", lh=(SX + 90, hy + 120), rh=(SX + 210, hy + 120))
            name_tag(c, SX, GY - 430, "司马光", "#5E5E58", 44)
        return None
    ev(j, k_sm, L.pop_fn(j, k_sm, sima), "muyu", 0.65)

    def pearl(c, kk, T):
        tx, tbo = tb(j, k_xin), tb(j, k_bao)
        g = pop_scale(T - tx)
        if g <= 0:
            return None
        x, y = SX + 300, cy - 160
        glow = 1 + 0.06 * math.sin(T * 4)
        if T >= tbo:
            for r, a in ((260, 0.12), (200, 0.2)):
                c.drawCircle(x, y, r * glow, K.paint(YELLOW, a * clamp01((T - tbo) / 0.4)))
        with K.at(c, x, y, 0, g):
            c.drawCircle(0, 0, 140, K.paint("#FFF6D6"))
            c.drawCircle(0, 0, 140, wb.marker("#A9842A", 8))
            K.text(c, "信", 0, 6, 150, "serif_black", RED)
        if T >= tbo:
            sparkle(c, x, y, T - tbo, YELLOW, 12, 160, 260)
            gb = C.slam_scale(T - tbo)
            with K.at(c, x + 230, y + 250, -6, gb):
                seal(c, 0, 0, "宝", 70, 0)
        return None
    ev(j, k_xin, pearl, "ding", 0.75)
    b.hit(j, k_bao, "bianzhong", 0.85, "最贵重的宝贝")


screen13()


# ================================================================ 屏 14：宴席正热闹，外面下大雨；魏文侯冒雨出门，当面说今天不打了
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    gu_frame(j, 0)
    GY = cy + 520
    k_feast = 0
    k_hunt = kq(j, wp(21, 2, 0.3), 1)
    k_rain = nx(j, wp(22, 0, 0.4), k_hunt)
    k_go = nx(j, wp(22, 1, 0.3), k_rain)
    k_say = nx(j, wp(22, 2, 0.5), k_go)
    L.note("魏文侯", "管山林的人", "打猎", "今天不打了")
    WX0, YX = cx - 300, cx + 360

    def feast(c, kk, T):
        g = pop_scale(T - tb(j, k_feast))
        if g <= 0:
            return None
        with at_pop(c, cx - 300, cy - 150, g):
            box(c, cx - 300, cy - 150, 480, 40, "#C98B4B", "#7A4A1E", 5, 8)
            for q in range(3):
                cup(c, cx - 450 + q * 150, cy - 170, 0.8)
            K.text(c, "宴席", cx - 300, cy - 330, 50, "hand", "#7A4A1E")
        th = tb(j, k_hunt)
        if T >= th:
            gh = pop_scale(T - th)
            with K.at(c, cx + 300, cy - 360, 0, gh):
                bubble_box(c, 0, 0, 300, 120, 1)
                K.text(c, "打猎", 0, 0, 58, "hand", GREEN)
        return None
    ev(j, k_feast, feast, "muyu", 0.6)
    b.hit(j, k_hunt, "pop", 0.65, "约好打猎")

    def rain(c, kk, T):
        tr = tb(j, k_rain)
        if T < tr:
            return None
        a = clamp01((T - tr) / 0.4)
        for i in range(36):
            x = cx - 560 + (i * 97) % 1120
            y0 = cy - 560 + ((i * 211 + (T - tr) * 900) % 1100)
            C.line(c, (x, y0), (x - 14, y0 + 50), WATER_LINE, 4, 0.6 * a)
        return None
    b.custom(j, k_rain, k_rain + 0.3, rain, sfx="shaker", gain=0.75)

    def walk(c, kk, T):
        tg, ts = tb(j, k_go), tb(j, k_say)
        x, dy, _ = C.walk(T, tg, max(0.4, ts - tg - 0.1), WX0, YX - 260, 10) if T >= tg else (WX0, 0, False)
        g = pop_scale(T - tb(j, 0) - 0.2)
        if g > 0:
            hy = GY + dy - 290 * 0.9
            with at_pop(c, x, GY + dy, g):
                gu(c, x, GY + dy, 0.9, WENHOU, hat="guan", beard="black",
                   rh=(x + 120, hy + 40) if T >= ts else None)
                if T >= tb(j, k_rain):
                    cape = P((x - 80, hy + 60), (x + 80, hy + 60), (x + 110, hy + 230), (x - 110, hy + 230), close=True)
                    c.drawPath(cape, K.paint("#C9B37A", 0.85))
                    c.drawPath(cape, wb.marker("#7A5E3A", 5))
                    for q in range(5):
                        C.line(c, (x - 70 + q * 35, hy + 80), (x - 90 + q * 45, hy + 225), "#7A5E3A", 3)
                    hat = P((x - 90, hy - 40), (x, hy - 110), (x + 90, hy - 40), close=True)
                    c.drawPath(hat, K.paint("#C9B37A"))
                    c.drawPath(hat, wb.marker("#7A5E3A", 5))
            name_tag(c, x, GY + dy - 400, "魏文侯", "#2F5B8E", 40)
        gy = pop_scale(T - tb(j, k_hunt))
        if gy > 0:
            with at_pop(c, YX, GY, gy):
                gu(c, YX, GY, 0.82, YUREN, hat="bun", mood="o" if T >= ts else "flat")
                name_tag(c, YX, GY - 370, "管山林的人", "#3F6B3A", 34)
        if T >= ts:
            gs = C.slam_scale(T - ts)
            with K.at(c, cx + 120, cy - 130, 0, gs):
                bubble_box(c, 0, 0, 400, 130, -1)
                K.text(c, "今天不打了", 0, 0, 58, "hand", INK)
        return None
    b.custom(j, 0, 0.3, walk)
    b.hit(j, k_go, "wood_low", 0.7, "冒雨出门")
    b.hit(j, k_say, "kick", 0.8, "当面说一声")


screen14()


# ================================================================ 屏 15：说回我们：小李对着没人回的群叹气；存钱罐“信用”投币；“三步”
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_li = 0
    k_jar = kq(j, wp(24, 0, 0.3), 1)
    k_c = [nx(j, wp(24, 0, 0.7), k_jar)]
    k_3 = nx(j, wp(24, 1, 0.5), k_c[0])
    L.note("已读未回", "信用", "三步")
    LX = cx - 330

    def li(c, sc, T):
        hy = GY - 290
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 1.0, "sad", rh=(LX + 100, hy + 110))
            phone(c, LX + 110, hy + 100, 0.9)
        K.text(c, "已读未回", LX, cy - 280, 54, "hand", GRAY, clamp01(sc))
        return None
    ev(j, k_li, L.pop_fn(j, k_li, li), "wood_low", 0.6)

    def jar(c, kk, T):
        g = pop_scale(T - tb(j, k_jar))
        if g <= 0:
            return None
        x, y = cx + 250, cy + 280
        with K.at(c, x, y, 0, g):
            c.drawOval(skia.Rect.MakeXYWH(-180, -150, 360, 300), K.paint("#F6C3D2"))
            c.drawOval(skia.Rect.MakeXYWH(-180, -150, 360, 300), wb.marker("#B0466A", 7))
            C.line(c, (-40, -150), (40, -150), INK, 10)
            K.text(c, "信用", 0, 20, 70, "serif_black", "#B0466A")
            for i in range(3):
                t0 = tb(j, k_c[0]) + i * 0.2
                if T < t0:
                    continue
                f = clamp01((T - t0) / 0.3)
                yy = lerp(-360, -150, f * f)
                if f < 1:
                    c.drawOval(skia.Rect.MakeXYWH(-30, yy - 14, 60, 28), K.paint(YELLOW))
                    c.drawOval(skia.Rect.MakeXYWH(-30, yy - 14, 60, 28), wb.marker("#A9842A", 4))
        return None
    ev(j, k_jar, jar, "pop", 0.65)
    b.hit(j, k_c[0], "ding", 0.7, "一枚枚投进去")
    L.stamp_ev(j, k_3, "三步", cx + 260, cy - 330, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen15()


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


# ================================================================ 屏 16：第一步：挑一件小事（周五前发会议纪要），按时打勾，同事看见
def screen16(j=16):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 0)
    GY = cy + 520
    k_task = kq(j, wp(25, 0, 0.6), 1)
    k_done = nx(j, wp(25, 1, 0.5), k_task)
    k_see = nx(j, wp(25, 2, 0.5), k_done)
    L.note("周五前", "发会议纪要", "看见")

    def task(c, kk, T):
        g = pop_scale(T - tb(j, k_task))
        if g <= 0:
            return None
        with K.at(c, cx - 120, cy - 180, 0, g):
            box(c, 0, 0, 560, 240, NOTE_FILL, ORANGE, 6, 10)
            K.text(c, "周五前", -100, -50, 60, "hand", ORANGE)
            K.text(c, "发会议纪要", 0, 40, 64, "hand", INK)
            td = tb(j, k_done)
            if T >= td:
                f = ease_out(clamp01((T - td) / 0.3))
                c.drawPath(wb.partial(check(220, -40, 60), f)[0], wb.marker(GREEN, 16))
        return None
    ev(j, k_task, task, "wood_high", 0.7)
    b.hit(j, k_done, "ding", 0.85, "按时做到")

    def people(c, kk, T):
        g = pop_scale(T - tb(j, k_task) - 0.2)
        if g > 0:
            with at_pop(c, cx - 320, GY, g):
                draw_li(c, cx - 320, GY, 0.9, "smile" if T >= tb(j, k_done) else "flat")
        ts = tb(j, k_see)
        if T >= ts:
            for i, x in enumerate((cx + 180, cx + 400)):
                gi = pop_scale(T - ts - i * 0.12)
                with at_pop(c, x, GY, gi):
                    if i == 0:
                        draw_wang(c, x, GY, 0.8, mood="smile")
                    else:
                        draw_li(c, x, GY, 0.8, "smile")
                with K.at(c, x, cy + 30, 0, gi):
                    c.drawOval(skia.Rect.MakeXYWH(-46, -26, 92, 52), K.paint("#FFFFFF"))
                    c.drawOval(skia.Rect.MakeXYWH(-46, -26, 92, 52), wb.marker(INK, 5))
                    c.drawCircle(-14, 0, 13, K.paint(INK))
        return None
    b.custom(j, k_task, k_task + 0.3, people)
    b.hit(j, k_see, "pop", 0.7, "同事看见")


screen16()


# ================================================================ 屏 17：第二步：规矩牌“九点开会”，小李和关系好的小王先到
def screen17(j=17):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 1)
    GY = cy + 520
    k_rule = kq(j, wp(26, 0, 0.6), 1)
    k_two = nx(j, wp(26, 1, 0.5), k_rule)
    k_first = nx(j, wp(26, 2, 0.4), k_two)
    L.note("九点开会", "先守", "9:00")

    def rule(c, kk, T):
        g = pop_scale(T - tb(j, k_rule))
        if g <= 0:
            return None
        with K.at(c, cx - 200, cy - 200, 0, g):
            box(c, 0, 0, 420, 220, "#FFFFFF", BLUE, 7, 14)
            K.text(c, "九点开会", 0, 0, 72, "hand", BLUE)
        with K.at(c, cx + 300, cy - 220, 0, g):
            c.drawCircle(0, 0, 110, K.paint("#FFFFFF"))
            c.drawPath(wb.clock(0, 0, 110), wb.marker(BLACK, 6))
            C.line(c, (0, 0), (0, -80), RED, 7)
            C.line(c, (0, 0), (-60, 0), BLACK, 9)
        return None
    ev(j, k_rule, rule, "wood_high", 0.7)

    def pair(c, kk, T):
        t2, tf = tb(j, k_two), tb(j, k_first)
        g = pop_scale(T - t2)
        if g <= 0:
            return None
        for i, x in enumerate((cx - 330, cx - 120)):
            with at_pop(c, x, GY, g):
                if i == 0:
                    draw_li(c, x, GY, 0.9, "smile")
                else:
                    draw_wang(c, x, GY, 0.9, mood="smile")
        c.drawPath(wb.arrow((cx - 230, cy + 130), (cx - 230, cy - 50), 0.0, 36), wb.marker(GREEN, 9))
        if T >= tf:
            seal(c, cx + 180, cy + 220, "先守", 70, -6, C.slam_scale(T - tf))
            for i, x in enumerate((cx + 230, cx + 420)):
                gi = pop_scale(T - tf - 0.2 - i * 0.12)
                with at_pop(c, x, GY, gi):
                    draw_li(c, x, GY, 0.75, "flat")
        return None
    b.custom(j, k_two, k_two + 0.3, pair, sfx="pop", gain=0.7)
    b.hit(j, k_first, "kick", 0.85, "自己人先守")


screen17()


# ================================================================ 屏 18：第三步：做不到提前说——小李走到同事桌前，日历“周三”改到“周五”
def screen18(j=18):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    steps_row(j, 2)
    GY = cy + 520
    k_walk = kq(j, wp(27, 0, 0.6), 1)
    k_wen = nx(j, wp(27, 1, 0.5), k_walk)
    k_say = nx(j, wp(27, 2, 0.4), k_wen)
    L.note("周三", "周五", "周五给你")

    def scene(c, kk, T):
        tw, ts = tb(j, k_walk), tb(j, k_say)
        g = pop_scale(T - tw)
        if g <= 0:
            return None
        WX = cx + 320
        with at_pop(c, WX, GY, g):
            desk(c, WX, GY - 170, 300)
            draw_wang(c, WX + 130, GY, 0.9, mood="smile" if T >= ts else "flat")
        x, dy, _ = C.walk(T, tw, 1.0, cx - 480, cx - 40, 10)
        with at_pop(c, x, GY + dy, g):
            draw_li(c, x, GY + dy, 0.9, "flat", rh=(x + 110, GY - 300) if T >= ts else None)
        if T >= ts:
            gs = C.slam_scale(T - ts)
            with K.at(c, x + 60, cy - 30, 0, gs):
                bubble_box(c, 0, 0, 340, 120, -1)
                K.text(c, "周五给你", 0, 0, 58, "hand", INK)
        return None
    b.custom(j, k_walk, k_walk + 0.3, scene, sfx="wood_low", gain=0.6)

    def cal(c, kk, T):
        tw = tb(j, k_wen)
        g = pop_scale(T - tb(j, k_walk) - 0.2)
        if g <= 0:
            return None
        with K.at(c, cx - 30, cy - 250, 0, g):
            for i, d in enumerate(("周三", "周五")):
                x = -170 + i * 340
                box(c, x, 0, 220, 170, "#FFFFFF", BLACK, 6, 12)
                c.drawRect(skia.Rect.MakeXYWH(x - 110, -85, 220, 50), K.paint(RED_FILL))
                K.text(c, d, x, 30, 60, "hand", INK)
            if T >= tw:
                f = ease_out(clamp01((T - tw) / 0.4))
                c.drawPath(wb.partial(wb.arrow((-60, -20), (60, -20), -0.4, 30), f)[0], wb.marker(ORANGE, 9))
                c.drawPath(wb.partial(cross(-170, 30, 60), f)[0], wb.marker(RED, 9))
        return None
    b.custom(j, k_walk, k_walk + 0.3, cal)
    b.hit(j, k_wen, "rim", 0.75, "改到周五")
    b.hit(j, k_say, "pop", 0.75, "当面说一声")


screen18()


# ================================================================ 屏 19：好处：小李说一句，几个同事跟着站起来
def screen19(j=19):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_jar = 0
    k_say = kq(j, wp(28, 1, 0.4), 1)
    k_up = nx(j, wp(28, 2, 0.4), k_say)
    L.note("信用", "走")
    LX = cx - 380

    def li(c, sc, T):
        ts = tb(j, k_say)
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, 1.0, "smile", rh=(LX + 120, GY - 380) if T >= ts else None)
            c.drawOval(skia.Rect.MakeXYWH(LX - 90, GY - 140, 180, 140), K.paint("#F6C3D2"))
            c.drawOval(skia.Rect.MakeXYWH(LX - 90, GY - 140, 180, 140), wb.marker("#B0466A", 5))
            K.text(c, "信用", LX, GY - 70, 40, "serif_black", "#B0466A")
        if T >= ts:
            g = C.slam_scale(T - ts)
            with K.at(c, LX + 60, cy - 250, 0, g):
                bubble_box(c, 0, 0, 200, 120, -1)
                K.text(c, "走", 0, 0, 70, "hand", RED)
        return None
    ev(j, k_jar, L.pop_fn(j, k_jar, li), "wood_low", 0.6)
    b.hit(j, k_say, "rim", 0.75, "说一句")

    def team(c, kk, T):
        tu = tb(j, k_up)
        for i, x in enumerate((cx - 60, cx + 170, cx + 400)):
            t0 = tu + i * 0.15
            up = ease_out(clamp01((T - t0) / 0.35)) if T >= t0 else 0
            g = pop_scale(T - tb(j, 0) - 0.2 - i * 0.1)
            if g <= 0:
                continue
            c.save()
            c.translate(x, GY)
            c.scale(1, lerp(0.7, 1.0, up))
            c.translate(-x, -GY)
            with at_pop(c, x, GY, g):
                if i == 1:
                    draw_wang(c, x, GY, 0.8, mood="smile" if up > 0.5 else "flat")
                else:
                    draw_li(c, x, GY, 0.8, "smile" if up > 0.5 else "flat")
            c.restore()
            if up > 0:
                sparkle(c, x, GY - 300, T - t0, YELLOW, 6, 40, 90)
        return None
    b.custom(j, 0, 0.3, team)
    b.hit(j, k_up, "ding", 0.85, "大家跟着动")


screen19()


# ================================================================ 屏 20：评论区；小李在清单上补上一件；下一讲预告
def screen20(j=20):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z_))
    k_cmt = 0
    k_chips = nx(j, wp(30, 0, 0.3), 0)
    k_list = nx(j, wp(31, 0, 0.3), k_chips)
    k_tick = nx(j, wp(31, 2, 0.3), k_list)
    k_next = nx(j, wp(32, 1, 0.2), k_tick)
    b.move(j, k_list, (cx, cy + 380, Z_), 1.1)
    CH = ["回消息", "还一本书", "请同事吃饭"]
    L.note("你没做到的是哪一件？", *CH, "下一讲", "说得头头是道", "为什么一做就砸？", "来得及")
    BY = cy - 330

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 20, BY, 0, sc):
            bubble_box(c, 0, 0, 1000, 360, -1)
            K.text(c, "你没做到的是哪一件？", 0, -110, 58, "hand", RED)
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

    def li(c, kk, T):
        g = pop_scale(T - tb(j, k_list))
        if g <= 0:
            return None
        tt = tb(j, k_tick)
        hy = LY - 290 * 0.95
        with at_pop(c, LX, LY, g):
            draw_li(c, LX, LY, 0.95, "smile" if T >= tt else "flat", rh=(LX + 170, hy + 60))
        with K.at(c, cx + 200, cy + 470, 0, g):
            box(c, 0, 0, 480, 300, NOTE_FILL, ORANGE, 6, 12)
            for i, s_ in enumerate(CH):
                yy = -90 + i * 90
                K.text(c, s_, -40, yy, 50, "hand", INK)
                c.drawRect(skia.Rect.MakeXYWH(-210, yy - 22, 44, 44), wb.marker(GRAY, 4))
                if T >= tt + i * 0.2:
                    c.drawPath(check(-188, yy, 26), wb.marker(GREEN, 8))
        if T >= tt:
            sparkle(c, cx + 200, cy + 300, T - tt, YELLOW, 10, 80, 150)
            K.text(c, "来得及", cx + 200, cy + 690, 64, "hand", GREEN, clamp01((T - tt - 0.3) / 0.2))
        return None
    ev(j, k_list, li, "wood_low", 0.6)
    b.hit(j, k_tick, "ding", 0.8, "补上一件")

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
            K.text(c, "说得头头是道", -100, -60, 58, "hand", BLACK)
            K.text(c, "为什么一做就砸？", -60, 40, 58, "hand", BLACK)
            with K.at(c, 390, 0, -6):
                box(c, 0, 0, 150, 170, PARCH, PARCH_LINE, 5, 6)
                for q in range(3):
                    c.drawPath(wb.arrow((-50, -50 + q * 45), (40, -60 + q * 45), 0.3, 14), wb.marker(RED, 4))
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen20()

# ================================================================ 收尾
L.finish(cover_shot=9, square_shot=5, notes=NOTES)
L.export(globals())
