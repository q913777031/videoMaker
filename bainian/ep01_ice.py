"""《百年孤独》01 冰块（故事体）：一桩命案，怎么变出了一个小镇？（白板手绘 + AI 旁白，竖屏 2:3）

连载第一讲，按小说时间顺序讲第 1–2 章：表兄妹成婚，怕生出猪尾巴 → 乌尔苏拉穿铁扣帆布裤 → 斗鸡后普鲁邓希奥·阿基拉尔嘲笑新郎，
被一矛杀死（剪影，不画血）→ 鬼魂在院子里洗伤口 → 翻山找海两年多 → 梦见镜子城马孔多 → 建镇 → 吉卜赛人的新玩意儿、
金币熔掉 → 帐篷里的冰 → “很多年后”行刑队前（旧色闪回）→ 全书第一句（范晔译本）→ 点题 → 评论区与下一讲。
只画书中人，都在羊皮卷框里、挂名牌。文案见 bainian/PLAN.md「### 01 冰块」。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from whiteboard import engine as wb
from whiteboard.engine import P
from bainian import hooks as BH
from bainian import lesson as N
from bainian import plan as BP
from bainian import theme as BT
from bainian.lesson import (BLACK, BLUE, BLUE_FILL, BUTTER, GRAY, GREEN, GREEN_FILL, INK, NOTE_FILL, ORANGE, RED, RED_FILL,
                            YELLOW, at_pop, box, bubble_box, butterfly, chip, draw_lady, draw_man, house, ice_block, jose,
                            magnet, magnifier, melquiades, name_tag, parchment, pop_scale, seal, sparkle, ursula)

SCREENS = [
    ([], "开场", 0),
    ([0, 1], "表兄妹", 1),
    ([2, 3], "帆布裤", 2),
    ([4], "斗鸡", 3),
    ([5], "长矛", 4),
    ([6], "鬼魂", 5),
    ([7, 8], "出走", 6),
    ([9], "梦", 7),
    ([10], "建镇", 8),
    ([11], "吉卜赛人", 9),
    ([12, 13], "新玩意儿", 10),
    ([14, 15], "帐篷", 11),
    ([16, 17], "摸冰", 12),
    ([18, 19], "很多年后", 13),
    ([20], "第一句", 14),
    ([21, 22, 23], "这个父亲", 15),
    ([24, 25, 26], "下一讲", 16),
]

THEME = BT.get("01")
assert BP.load("01").get("HOOK_TEXT") == BH.HOOK_TEXT[THEME["hook"]], "PLAN.md 的 HOOK_TEXT 与开场钩子大字不一致"
L = N.Lesson("01", SCREENS, drop_screen=4, board_size=(5000, 12400), theme=THEME)
b = L.b
tb, wp, kq, nx, cap, ev = L.tb, L.wp, L.kq, L.nx, L.cap, L.ev

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(15)]
Z_ = 0.72
KT = N.Kit(L, R)

NOTES = [
    "出处：加西亚·马尔克斯《百年孤独》第 1–2 章（范晔译本）。情节为转述；引文只有全书第一句（范晔译）。",
    "书中人造型为示意（一百多年前的加勒比小镇打扮）；命案与行刑队只画剪影，不画血。",
]

TAGC = "#5E4128"
JOSE = ("何塞·阿尔卡蒂奥·布恩迪亚", "新郎 · 第一代")
URS = ("乌尔苏拉", "新娘 · 第一代")
PRU = ("普鲁邓希奥·阿基拉尔", "斗鸡输了的人")
AUR = ("奥雷里亚诺", "小儿子 · 第二代")
SIL = "#2A2622"
SEPIA, SEPIA_LINE = "#D9BE8E", "#7A5A30"


def tag(c, x, y, who, a=1.0, size=40, color=TAGC):
    name_tag(c, x, y, who[0], color, size, a, who[1])


def prudencio(c, x, y, s, alpha=1.0, **kw):
    """普鲁邓希奥·阿基拉尔：草帽、小胡子、赭色衬衫。"""
    kw.setdefault("beard", "mustache")
    draw_man(c, x, y, s, "ochre", hat="straw", alpha=alpha, **kw)


def kid(c, x, y, s, color="red", **kw):
    draw_man(c, x, y, s, color, **kw)


def rooster(c, x, y, s=1.0, col="#C0392B", a=1.0, down=0.0):
    """斗鸡：(x, y) 为脚底；down=1 倒地。"""
    with K.at(c, x, y, 90 * down, s):
        for dx in (-14, 14):
            C.line(c, (dx, -50), (dx, 0), "#C9A34A", 6, a)
        body = skia.Path()
        body.addOval(skia.Rect.MakeXYWH(-60, -120, 120, 80))
        c.drawPath(body, K.paint(col, a))
        c.drawPath(body, wb.marker(INK, 5, a))
        c.drawPath(P((-50, -100), (-110, -150), (-90, -90), (-120, -110), (-60, -70), close=True), K.paint(INK, a))
        c.drawCircle(50, -140, 30, K.paint(col, a))
        c.drawCircle(50, -140, 30, wb.marker(INK, 5, a))
        c.drawPath(P((40, -170), (52, -190), (60, -172), (70, -188), (74, -166), close=True), K.paint(RED, a))
        c.drawPath(P((78, -146), (102, -138), (78, -130), close=True), K.paint("#E0A21B", a))
        c.drawCircle(58, -146, 5, K.paint(INK, a))


def spear(c, x0, y0, x1, y1, a=1.0, color=SIL):
    C.line(c, (x0, y0), (x1, y1), color, 10, a)
    d = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    c.drawPath(P((x1 + ux * 50, y1 + uy * 50), (x1 - uy * 18, y1 + ux * 18), (x1 + uy * 18, y1 - ux * 18), close=True),
               K.paint(color, a))


def silhouette(c, x, y, s, a=1.0, arm=None, fall=0.0, hat=False):
    """剪影小人（全黑填充）：(x, y) 脚底；arm 为手的位置；fall 0–1 向后倒。"""
    with K.at(c, x, y, -80 * fall, 1):
        hy = -290 * s
        c.drawCircle(0, hy, 48 * s, K.paint(SIL, a))
        if hat:
            c.drawRect(skia.Rect.MakeXYWH(-80 * s, hy - 50 * s, 160 * s, 16 * s), K.paint(SIL, a))
        body = P((-46 * s, hy + 50 * s), (46 * s, hy + 50 * s), (40 * s, -120 * s), (-40 * s, -120 * s), close=True)
        c.drawPath(body, K.paint(SIL, a))
        for sg in (-1, 1):
            C.line(c, (sg * 20 * s, -120 * s), (sg * 46 * s, 0), SIL, 22 * s, a)
        ax, ay = arm or (60 * s, -150 * s)
        C.line(c, (36 * s, hy + 80 * s), (ax, ay), SIL, 20 * s, a)
        C.line(c, (-36 * s, hy + 80 * s), (-60 * s, -150 * s), SIL, 20 * s, a)


def mule(c, x, y, s=1.0, a=1.0, load=True):
    col, line = "#B9B2A6", "#5E5A52"
    with K.at(c, x, y, 0, s):
        for dx in (-50, -26, 26, 50):
            C.line(c, (dx, -60), (dx, 0), line, 9, a)
        c.drawOval(skia.Rect.MakeXYWH(-80, -120, 160, 80), K.paint(col, a))
        c.drawOval(skia.Rect.MakeXYWH(-80, -120, 160, 80), wb.marker(line, 5, a))
        hd = skia.Rect.MakeXYWH(70, -170, 60, 44)
        c.drawRoundRect(hd, 18, 18, K.paint(col, a))
        c.drawRoundRect(hd, 18, 18, wb.marker(line, 5, a))
        C.line(c, (60, -110), (82, -150), line, 14, a)
        for dx in (78, 94):
            C.line(c, (dx, -168), (dx - 6, -206), line, 7, a)
        if load:
            box(c, -10, -150, 110, 60, "#C9A46A", "#6E4E22", 5, 6, a)
            c.drawOval(skia.Rect.MakeXYWH(-60, -190, 70, 40), K.paint("#5E5E58", a))


def ghost(c, x, y, s, a=0.45, T=0.0):
    """半透明鬼魂：普鲁邓希奥的灰色轮廓，下半身淡出成波浪。"""
    bob = 8 * math.sin(T * 2.2)
    c.saveLayerAlpha(None, int(255 * a))
    prudencio(c, x, y + bob, s, mood="sad", rh=(x + 110 * s, y - 230 * s + bob), lh=(x + 60 * s, y - 230 * s + bob))
    c.restore()
    p = P((x - 70 * s, y - 120 * s + bob), (x + 70 * s, y - 120 * s + bob), (x + 50 * s, y + 10), (x + 20 * s, y - 20),
          (x - 10 * s, y + 10), (x - 40 * s, y - 20), (x - 70 * s, y + 10), close=True)
    c.drawPath(p, K.paint("#FFFFFF", 0.35))


def tent(c, x, y, w=560, h=460, open_=0.0, a=1.0):
    """吉卜赛人的条纹帐篷：(x, y) 为地面中点；open_ 帘子掀开比例。"""
    top = (x, y - h)
    left = P(top, (x - w / 2, y), (x, y), close=True)
    right = P(top, (x + w / 2, y), (x, y), close=True)
    for p_, col in ((left, "#E8C24A"), (right, "#C0392B")):
        c.drawPath(p_, K.paint(col, a))
        c.drawPath(p_, wb.marker(INK, 6, a))
    for q in range(1, 4):
        C.line(c, top, (x - w / 2 + q * w / 8, y), "#FFFFFF", 6, 0.6 * a)
        C.line(c, top, (x + w / 2 - q * w / 8, y), "#FFFFFF", 6, 0.6 * a)
    door = P((x - 90, y), (x, y - h * 0.55), (x + 90, y), close=True)
    c.drawPath(door, K.paint("#3A2A12", a))
    if open_ < 1:
        cur = P((x - 90, y), (x, y - h * 0.55), (x + 90 - 180 * open_, y), close=True)
        c.drawPath(cur, K.paint("#8E2A1C", a))
        c.drawPath(cur, wb.marker(INK, 4, a))
    c.drawPath(P(top, (top[0], top[1] - 60), (top[0] + 50, top[1] - 45), (top[0], top[1] - 30)), wb.marker(INK, 5, a))


def mirror_city(c, x, y, s=1.0, T=0.0, a=1.0):
    """镜子砌成的城：一排高低不一的玻璃塔，闪光。"""
    with K.at(c, x, y, 0, s):
        for i, (dx, h) in enumerate(((-150, 160), (-80, 230), (0, 300), (80, 210), (150, 150))):
            r = skia.Rect.MakeXYWH(dx - 34, -h, 68, h)
            c.drawRect(r, K.paint("#DCEFFA", a))
            c.drawRect(r, wb.marker("#3F7FB8", 5, a))
            C.line(c, (dx - 18, -h + 20), (dx - 4, -h + 70), "#FFFFFF", 6, a)
            if (int(T * 3) + i) % 3 == 0:
                sparkle(c, dx, -h - 10, (T * 1.5) % 0.9, YELLOW, 6, 6, 30)


def coin(c, x, y, r=26, a=1.0):
    c.drawCircle(x, y, r, K.paint("#F2C230", a))
    c.drawCircle(x, y, r, wb.marker("#9C7A1A", 4, a))
    c.drawCircle(x, y, r * 0.55, wb.marker("#9C7A1A", 2, a))


def crucible(c, x, y, T, a=1.0):
    pot = P((x - 110, y - 120), (x + 110, y - 120), (x + 80, y), (x - 80, y), close=True)
    c.drawPath(pot, K.paint("#5E5E58", a))
    c.drawPath(pot, wb.marker(INK, 6, a))
    c.drawOval(skia.Rect.MakeXYWH(x - 100, y - 136, 200, 34), K.paint(ORANGE, a))
    for q in range(3):
        fh = 40 + 20 * math.sin(T * 9 + q)
        c.drawPath(P((x - 60 + q * 60, y + 10), (x - 40 + q * 60, y + 10 + fh), (x - 20 + q * 60, y + 10), close=True),
                   K.paint(RED, a))


def astrolabe(c, x, y, r, T, a=1.0):
    c.drawCircle(x, y, r, K.paint("#E9CF8A", a))
    c.drawCircle(x, y, r, wb.marker("#8A6A2A", 6, a))
    c.drawCircle(x, y, r * 0.65, wb.marker("#8A6A2A", 3, a))
    ang = T * 1.4
    C.line(c, (x - r * math.cos(ang), y - r * math.sin(ang)), (x + r * math.cos(ang), y + r * math.sin(ang)), INK, 6, a)


def rifle_row(c, x0, y, n, a=1.0, gap=120):
    """行刑队剪影：一排士兵侧影举枪（只画剪影）。"""
    for i in range(n):
        x = x0 + i * gap
        silhouette(c, x, y, 0.55, a, arm=(-100 * 0.55, -200 * 0.55), hat=True)
        C.line(c, (x - 40, y - 190 * 0.55 - 30), (x - 200, y - 200 * 0.55 - 40), SIL, 9, a)


# ================================================================ 屏 0：开场（只有砸字音效）
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：表兄妹成婚；两边老人摇头，气泡里一条卷卷的猪尾巴
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_pair = kq(j, wp(0, 1, 0.3), 0)
    k_cous = nx(j, wp(0, 2, 0.4), k_pair)
    k_old = nx(j, wp(1, 0, 0.5), k_cous)
    k_tail = nx(j, wp(1, 2, 0.4), k_old)
    L.note(*JOSE, *URS, "表兄妹")
    JX, UX = cx - 170, cx + 170

    def scene(c, kk, T):
        tp, tc, to, tt = (tb(j, k) for k in (k_pair, k_cous, k_old, k_tail))
        g = pop_scale(T - tp)
        if g <= 0:
            return None
        with at_pop(c, JX, GY, g):
            jose(c, JX, GY, 0.95, mood="smile", rh=(cx, GY - 220))
        with at_pop(c, UX, GY, g):
            ursula(c, UX, GY, 0.95, mood="smile", lh=(cx, GY - 220))
        tag(c, JX - 70, GY - 470, JOSE, clamp01(g), 34)
        tag(c, UX + 120, GY - 470, URS, clamp01(g), 38)
        if T >= tc:
            with K.at(c, cx, GY - 600, 0, pop_scale(T - tc)):
                chip(c, 0, 0, "表兄妹", RED_FILL, RED, 50)
            c.drawPath(C.heart_path(cx, GY - 250, 36), K.paint(RED_FILL))
        if T >= to:
            for i, x in enumerate((cx - 470, cx + 470)):
                s_ = pop_scale(T - to - 0.1 * i)
                head = 10 * math.sin((T - to) * 9 + i) if T < tt + 1.0 else 0
                with at_pop(c, x, GY, s_):
                    if i == 0:
                        draw_man(c, x, GY, 0.75, "gray", beard="white", mood="sad", head_dx=head)
                    else:
                        draw_lady(c, x, GY, 0.75, "gray", hair="gray", mood="sad", head_dx=head)
        if T >= tt:
            with K.at(c, cx + 240, cy - 300, 0, pop_scale(T - tt)):
                bubble_box(c, 0, 0, 380, 220, 1)
                BH.pig_tail(c, -100, 0, 0.9, 1.0, ease_out(clamp01((T - tt) / 0.6)))
                K.text(c, "？", 140, 0, 90, "hand", RED)
        return None
    ev(j, k_pair, scene, "bongo_low", 0.7)
    b.hit(j, k_cous, "pop", 0.75, "表兄妹")
    b.hit(j, k_old, "wood_low", 0.65, "老人摇头")
    b.hit(j, k_tail, "rim", 0.85, "猪尾巴")


screen1()


# ================================================================ 屏 2：乌尔苏拉抱胳膊，帆布裤上铁扣扣上；窗外村民交头接耳
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_u = kq(j, wp(2, 0, 0.5), 0)
    k_pants = nx(j, wp(2, 2, 0.3), k_u)
    k_lock = nx(j, wp(2, 2, 0.8), k_pants)
    k_talk = nx(j, wp(3, 1, 0.3), k_lock)
    L.note("铁扣", "帆布裤", "闲话")
    UX = cx - 250

    def scene(c, kk, T):
        tu, tp, tl, tt = (tb(j, k) for k in (k_u, k_pants, k_lock, k_talk))
        g = pop_scale(T - tu)
        if g <= 0:
            return None
        hy = GY - 290
        with at_pop(c, UX, GY, g):
            ursula(c, UX, GY, 1.05, mood="flat", lh=(UX + 30, hy + 140), rh=(UX - 30, hy + 140))
        tag(c, UX, GY - 480, URS, clamp01(g))
        if T >= tp:
            f = ease_out(clamp01((T - tp) / 0.4))
            with K.at(c, cx + 220, cy - 120, 0, f):
                pants = P((-110, -150), (110, -150), (120, 160), (20, 160), (0, -20), (-20, 160), (-120, 160), close=True)
                c.drawPath(pants, K.paint("#C9B48A"))
                c.drawPath(pants, wb.marker("#6E4E22", 6))
                for q in range(4):
                    C.line(c, (-100 + q * 12, -120 + q * 70), (-60 + q * 12, -120 + q * 70), "#8A6A3A", 3)
                c.drawRect(skia.Rect.MakeXYWH(-110, -150, 220, 30), K.paint("#8A6A3A"))
                locked = T >= tl
                bx = 0
                c.drawRoundRect(skia.Rect.MakeXYWH(bx - 34, -160, 68, 50), 8, 8, K.paint("#8A8F99"))
                c.drawRoundRect(skia.Rect.MakeXYWH(bx - 34, -160, 68, 50), 8, 8, wb.marker(INK, 5))
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(bx - 22, -200 + (0 if locked else -24), 44, 70), 180, 180)
                c.drawPath(arc, wb.marker(INK, 8))
            K.text(c, "帆布裤", cx + 220, cy + 110, 52, "hand", INK, f)
            if T >= tl:
                with K.at(c, cx + 370, cy - 260, 6, C.slam_scale(T - tl)):
                    K.text(c, "咔哒", 0, 0, 56, "hand", RED)
        if T >= tt:
            for i in range(3):
                x = cx + 140 + i * 170
                s_ = pop_scale(T - tt - i * 0.12)
                if s_ <= 0:
                    continue
                (draw_man if i % 2 == 0 else draw_lady)(c, x, GY, 0.52, ("white", "green", "ochre")[i], mood="o")
                with K.at(c, x + 20, cy + 230 - (i % 2) * 40, 0, s_):
                    bubble_box(c, 0, 0, 130, 70, -1)
                    K.text(c, "……", 0, -6, 40, "hand", GRAY)
            K.text(c, "闲话", cx + 310, cy + 380, 50, "hand", ORANGE, clamp01((T - tt) / 0.3))
        return None
    ev(j, k_u, scene, "wood_low", 0.65)
    b.hit(j, k_pants, "shaker", 0.65, "帆布裤")
    b.hit(j, k_lock, "rim", 0.85, "铁扣扣上")
    b.hit(j, k_talk, "pop", 0.7, "村里有了闲话")


screen2()


# ================================================================ 屏 3：两只斗鸡对冲，一只倒下；普鲁邓希奥指着何塞大笑，“不中用”
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_fight = kq(j, wp(4, 0, 0.4), 0)
    k_down = nx(j, wp(4, 1, 0.5), k_fight)
    k_pru = nx(j, wp(4, 2, 0.4), k_down)
    k_laugh = nx(j, wp(4, 4, 0.2), k_pru)
    L.note(*PRU, "不中用")

    def scene(c, kk, T):
        tf, td, tp, tl = (tb(j, k) for k in (k_fight, k_down, k_pru, k_laugh))
        g = pop_scale(T - tf)
        if g <= 0:
            return None
        ring = skia.Path()
        ring.addOval(skia.Rect.MakeXYWH(cx - 300, cy - 190, 600, 160))
        c.drawPath(ring, wb.marker("#8A6A3A", 6, g))
        u = ease_in_out(clamp01((T - tf) / 0.6))
        down = ease_out(clamp01((T - td) / 0.3)) if T >= td else 0
        jit = 10 * math.sin((T - tf) * 20) * (1 - down)
        rooster(c, lerp(cx - 260, cx - 90, u) + jit, cy - 90, 0.9, "#C0392B")
        c.save()
        c.translate(lerp(cx + 260, cx + 90, u) - jit + 60 * down, cy - 90)
        c.scale(-1, 1)
        rooster(c, 0, 0, 0.9, "#E0A21B", 1, down)
        c.restore()
        if down > 0:
            for q in range(5):
                C.line(c, (cx + 120 + q * 20, cy - 220 - 30 * down), (cx + 130 + q * 20, cy - 240 - 50 * down), "#E0A21B", 5,
                       1 - down * 0.5)
        if T >= tp:
            PX, JX = cx + 260, cx - 320
            jose(c, JX, GY, 0.85, mood="sad")
            with at_pop(c, PX, GY, pop_scale(T - tp)):
                prudencio(c, PX, GY, 0.95, mood="laugh" if T >= tl else "flat", rh=(PX - 160, GY - 300) if T >= tl else None)
            tag(c, PX - 10, GY - 470, PRU, clamp01((T - tp) / 0.3), 32)
            if T >= tl:
                with K.at(c, cx - 30, cy + 80, -4, C.slam_scale(T - tl)):
                    bubble_box(c, 0, 0, 300, 120, 1)
                    K.text(c, "不中用", 0, 0, 62, "hand", RED)
        return None
    ev(j, k_fight, scene, "bongo_high", 0.75)
    b.hit(j, k_down, "tom", 0.8, "一只斗鸡倒下")
    b.hit(j, k_pru, "pop", 0.7, "普鲁邓希奥")
    b.hit(j, k_laugh, "rim", 0.85, "当众嘲笑")


screen3()


# ================================================================ 屏 4（drop）：剪影——何塞掷出长矛，对面剪影倒下；红章“命案”
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    dk = L.drop_k()
    k_home = kq(j, wp(5, 2, 0.3), 0)
    k_spear = nx(j, wp(5, 3, 0.4), k_home)
    L.note(*JOSE, "命案")

    def scene(c, kk, T):
        th, ts, td = tb(j, k_home), tb(j, k_spear), tb(j, dk)
        g = pop_scale(T - th)
        if g <= 0:
            return None
        sky = skia.Rect.MakeXYWH(cx - 562, cy - 567, 1124, 1179)
        c.drawRect(sky, K.paint("#E9B37A", 0.55))
        c.drawCircle(cx, cy + 120, 260, K.paint("#F6D08A", 0.7))
        C.line(c, (cx - 560, GY + 6), (cx + 560, GY + 6), SIL, 10)
        JX, PX = cx - 330, cx + 330
        thrown = T >= td
        silhouette(c, JX, GY, 1.0, 1, arm=(-30, -420) if not thrown else (120, -300))
        if not thrown:
            spear(c, JX - 80, GY - 220, JX + 10, GY - 470)
        else:
            u = ease_out(clamp01((T - td) / 0.18))
            sx = lerp(JX + 60, PX - 40, u)
            spear(c, sx - 260, GY - 330, sx, GY - 330)
        fall = ease_out(clamp01((T - td - 0.15) / 0.5)) if thrown else 0
        silhouette(c, PX, GY, 1.0, 1, fall=fall, hat=True)
        tag(c, JX, GY - 520, JOSE, clamp01(g), 32)
        if T >= td:
            seal(c, cx, cy - 330, "命案", 110, -6, C.slam_scale(T - td))
        return None
    ev(j, k_home, scene, "wood_low", 0.65)
    b.hit(j, k_spear, "shaker", 0.7, "取了长矛")
    b.hit(j, dk, "kick", 0.95, "一矛杀了他")
    b.shots[j].shake = [(dk, 12.0)]
    b.shots[j].flashes = [(dk, 0.3)]


screen4()


# ================================================================ 屏 5：夜里院子：半透明的普鲁邓希奥在水罐边洗脖子；何塞躲在门后
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_night = kq(j, wp(6, 0, 0.5), 0)
    k_ghost = nx(j, wp(6, 1, 0.4), k_night)
    k_wash = nx(j, wp(6, 4, 0.3), k_ghost)
    L.note("鬼魂", "夜里")

    def scene(c, kk, T):
        tn, tg, tw = tb(j, k_night), tb(j, k_ghost), tb(j, k_wash)
        g = pop_scale(T - tn)
        if g <= 0:
            return None
        c.drawRect(skia.Rect.MakeXYWH(cx - 562, cy - 567, 1124, 1179), K.paint("#2F3A55", 0.35 * clamp01(g)))
        c.drawCircle(cx + 400, cy - 440, 60, K.paint("#F6E7A6"))
        K.text(c, "夜里", cx - 420, cy - 450, 56, "hand", BLUE, clamp01(g))
        DX = cx - 330
        box(c, DX, GY - 230, 200, 460, "#6E4E22", INK, 6, 6)
        jose(c, DX + 70, GY, 0.9, mood="o")
        for q in range(2):
            c.drawPath(P((DX + 110 + q * 30, GY - 330), (DX + 104 + q * 30, GY - 310), (DX + 116 + q * 30, GY - 310), close=True),
                       K.paint("#7FB2D9"))
        JX = cx + 300
        box(c, JX - 150, GY - 60, 110, 120, "#B5562E", "#5E2E18", 5, 20)
        if T >= tg:
            ghost(c, JX, GY, 0.95, 0.5 * clamp01((T - tg) / 0.5), T)
            K.text(c, "鬼魂", JX + 160, cy - 140, 54, "hand", GRAY, clamp01((T - tg) / 0.4))
        if T >= tw:
            hy = GY - 290 * 0.95
            for q in range(4):
                f = ((T - tw) * 1.2 + q / 4) % 1
                c.drawCircle(JX - 10 + 20 * math.sin(q), hy + 60 + 120 * f, 7, K.paint("#7FB2D9", 1 - f))
            ring = skia.Path()
            ring.addOval(skia.Rect.MakeXYWH(JX - 50, hy + 30, 100, 60))
            c.drawPath(ring, wb.marker(RED, 5, 0.6))
        return None
    ev(j, k_night, scene, "wood_low", 0.6)
    b.hit(j, k_ghost, "xiaoluo", 0.7, "鬼魂")
    b.hit(j, k_wash, "shaker", 0.65, "一遍遍洗伤口")


screen5()


# ================================================================ 屏 6：一列人赶着骡子翻山；虚线画到画外“海？”；日历翻过两年
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_go = kq(j, wp(7, 1, 0.4), 0)
    k_mtn = nx(j, wp(7, 3, 0.4), k_go)
    k_sea = nx(j, wp(7, 4, 0.3), k_mtn)
    k_years = nx(j, wp(8, 0, 0.5), k_sea)
    k_none = nx(j, wp(8, 1, 0.4), k_years)
    L.note("海？", "两年多")

    def scene(c, kk, T):
        tg, tm, ts, ty, tn = (tb(j, k) for k in (k_go, k_mtn, k_sea, k_years, k_none))
        g = pop_scale(T - tg)
        if g <= 0:
            return None
        if T >= tm:
            f = ease_out(clamp01((T - tm) / 0.6))
            for i, (dx, h) in enumerate(((-300, 420), (60, 560), (380, 380))):
                p = P((cx + dx - 300, GY - 120), (cx + dx, GY - 120 - h * f), (cx + dx + 300, GY - 120), close=True)
                c.drawPath(p, K.paint("#B7C9A0"))
                c.drawPath(p, wb.marker(N.LEAF_LINE, 6))
        route = P((cx - 520, GY - 60), (cx - 300, GY - 360), (cx + 60, GY - 680), (cx + 380, GY - 400), (cx + 560, GY - 640))
        if T >= ts:
            pth = wb.marker(INK, 6)
            pth.setPathEffect(skia.DashPathEffect.Make([24, 18], 0))
            c.drawPath(wb.partial(route, min(0.999, ease_out(clamp01((T - ts) / 1.0))))[0], pth)
            K.text(c, "海？", cx + 440, cy - 300, 66, "hand", BLUE, clamp01((T - ts - 0.6) / 0.3))
        walk = (T - tg) * 70
        for i in range(4):
            x = cx - 520 + ((walk + i * 150) % 900)
            dy = 6 * abs(math.sin((T - tg) * 7 + i))
            if i == 1:
                mule(c, x, GY - dy, 0.6)
            elif i == 0:
                jose(c, x, GY - dy, 0.55, mood="flat")
            elif i == 2:
                ursula(c, x, GY - dy, 0.55, mood="flat")
            else:
                draw_man(c, x, GY - dy, 0.55, "white", hat="straw", mood="flat")
        if T >= ty:
            with K.at(c, cx - 330, cy - 420, 0, pop_scale(T - ty)):
                box(c, 0, 0, 240, 200, "#FFFFFF", INK, 6, 10)
                c.drawRect(skia.Rect.MakeXYWH(-120, -100, 240, 60), K.paint(RED_FILL))
                yrs = min(2, int((T - ty) / 0.4) + 1)
                K.text(c, f"{yrs}年", 0, 30, 70, "hand", INK)
            K.text(c, "两年多", cx - 330, cy - 260, 46, "hand", ORANGE, clamp01((T - ty) / 0.3))
        if T >= tn:
            with K.at(c, cx + 440, cy - 300, 0, C.slam_scale(T - tn)):
                C.line(c, (-70, -50), (70, 50), RED, 10)
                C.line(c, (-70, 50), (70, -50), RED, 10)
        return None
    ev(j, k_go, scene, "shaker", 0.7)
    b.hit(j, k_mtn, "tom", 0.7, "翻过大山")
    b.hit(j, k_sea, "pop", 0.7, "去找海")
    b.hit(j, k_years, "wood_high", 0.65, "走了两年多")
    b.hit(j, k_none, "rim", 0.85, "海没找到")


screen6()


# ================================================================ 屏 7：何塞睡在河边，梦泡里一座镜子砌成的城闪光，牌子“马孔多”
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_sleep = kq(j, wp(9, 0, 0.5), 0)
    k_dream = nx(j, wp(9, 1, 0.5), k_sleep)
    k_city = nx(j, wp(9, 2, 0.4), k_dream)
    k_name = nx(j, wp(9, 3, 0.4), k_city)
    L.note("马孔多", "Z")

    def scene(c, kk, T):
        ts, td, tc, tn = (tb(j, k) for k in (k_sleep, k_dream, k_city, k_name))
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        rv = P((cx - 560, GY + 10), (cx - 100, GY - 60), (cx + 560, GY - 20))
        c.drawPath(rv, wb.marker("#7FB2D9", 40, 0.7))
        with K.at(c, cx - 250, GY - 120, -90, g):
            jose(c, 0, 0, 0.8, mood="smile")
        for q in range(3):
            f = ((T - ts) * 0.6 + q / 3) % 1
            K.text(c, "Z", cx - 300 + 40 * q, cy + 80 - 120 * f, 40 + 10 * q, "hand", BLUE, 1 - f)
        if T >= td:
            for q, (x, y, r) in enumerate(((cx - 180, cy + 10, 16), (cx - 120, cy - 60, 26))):
                c.drawCircle(x, y, r, wb.marker(INK, 4))
            s_ = pop_scale(T - td)
            with K.at(c, cx + 150, cy - 260, 0, s_):
                c.drawOval(skia.Rect.MakeXYWH(-360, -230, 720, 460), K.paint("#FFFFFF"))
                c.drawOval(skia.Rect.MakeXYWH(-360, -230, 720, 460), wb.marker(INK, 6))
                if T >= tc:
                    mirror_city(c, 0, 140, 1.0 * pop_scale(T - tc), T)
                if T >= tn:
                    with K.at(c, 0, 180, -3, C.slam_scale(T - tn)):
                        box(c, 0, 0, 260, 80, "#F7EFD9", "#6E4E22", 6, 8)
                        K.text(c, "马孔多", 0, 2, 54, "serif_black", RED)
        return None
    ev(j, k_sleep, scene, "wood_low", 0.6)
    b.hit(j, k_dream, "pop", 0.7, "梦")
    b.hit(j, k_city, "ding", 0.8, "镜子砌成的城")
    b.hit(j, k_name, "kick", 0.8, "马孔多")


screen7()


# ================================================================ 屏 8：河边土坯房一间间冒出，红章“马孔多”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_stop = kq(j, wp(10, 1, 0.4), 0)
    k_build = nx(j, wp(10, 2, 0.3), k_stop)
    k_seal = nx(j, wp(10, 2, 0.9), k_build)
    L.note("马孔多")

    def scene(c, kk, T):
        ts, tbd, tse = tb(j, k_stop), tb(j, k_build), tb(j, k_seal)
        g = pop_scale(T - ts)
        if g <= 0:
            return None
        rv = P((cx - 560, GY + 10), (cx - 100, GY - 40), (cx + 560, GY))
        c.drawPath(rv, wb.marker("#7FB2D9", 50, 0.7))
        for q in range(3):
            c.drawOval(skia.Rect.MakeXYWH(cx - 400 + q * 300, GY - 10, 90, 40), K.paint("#FFFFFF"))
            c.drawOval(skia.Rect.MakeXYWH(cx - 400 + q * 300, GY - 10, 90, 40), wb.marker(GRAY, 4))
        if T >= tbd:
            spots = [(cx - 340, GY - 120, 0.5), (cx - 60, GY - 160, 0.55), (cx + 230, GY - 130, 0.5), (cx - 200, GY - 330, 0.4),
                     (cx + 100, GY - 360, 0.42), (cx + 380, GY - 320, 0.38)]
            for i, (x, y, s_) in enumerate(spots):
                sc = pop_scale(T - tbd - i * 0.12)
                if sc > 0:
                    with K.at(c, x, y, 0, s_ * sc):
                        house(c, 0, 0)
        if T >= tse:
            seal(c, cx, cy - 380, "马孔多", 90, -5, C.slam_scale(T - tse))
        return None
    ev(j, k_stop, scene, "wood_low", 0.6)
    b.hit(j, k_build, "shaker", 0.75, "盖起房子")
    b.hit(j, k_seal, "kick", 0.85, "马孔多")


screen8()


# ================================================================ 屏 9：梅尔基亚德斯戴宽檐黑帽打鼓，箱子里冒出新鲜玩意儿
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_march = kq(j, wp(11, 0, 0.3), 0)
    k_mel = nx(j, wp(11, 2, 0.3), k_march)
    k_box = nx(j, wp(11, 4, 0.3), k_mel)
    L.note("每年三月", "梅尔基亚德斯", "吉卜赛人")
    MX = cx - 280

    def scene(c, kk, T):
        tm, tml, tbx = tb(j, k_march), tb(j, k_mel), tb(j, k_box)
        sc = pop_scale(T - tm)
        if sc > 0:
            with K.at(c, cx + 300, cy - 440, 4, sc):
                box(c, 0, 0, 300, 110, NOTE_FILL, ORANGE, 5, 10)
                K.text(c, "每年三月", 0, 2, 54, "hand", RED)
        g = pop_scale(T - tml)
        if g <= 0:
            return None
        x = lerp(cx - 700, MX, ease_out(clamp01((T - tml) / 0.6)))
        beat = 14 * abs(math.sin((T - tml) * 8))
        with at_pop(c, x, GY, g):
            melquiades(c, x, GY, 1.0, mood="smile", rh=(x + 130, GY - 230 - beat))
            c.drawOval(skia.Rect.MakeXYWH(x + 60, GY - 230, 130, 70), K.paint("#C0392B"))
            c.drawOval(skia.Rect.MakeXYWH(x + 60, GY - 230, 130, 70), wb.marker(INK, 5))
        name_tag(c, x, GY - 510, "梅尔基亚德斯", "#3A3A3A", 44, clamp01(g), "吉卜赛人")
        BX, BY = cx + 250, GY - 60
        open_ = ease_out(clamp01((T - tbx) / 0.4)) if T >= tbx else 0
        box(c, BX, BY, 340, 200, "#B5562E", "#5E2E18", 7, 10)
        with K.at(c, BX - 170, BY - 100, -70 * open_):
            box(c, 170, -20, 340, 40, "#C96A3E", "#5E2E18", 6, 8)
        if T >= tbx:
            items = ((magnet, -110, -270, 0.6), (magnifier, 30, -340, 0.6), (None, 150, -260, 1.0))
            for i, (fn, dx, dy, s) in enumerate(items):
                f = ease_out(clamp01((T - tbx - i * 0.12) / 0.45))
                if f <= 0:
                    continue
                xx, yy = BX + dx * f, BY - 80 + (dy + 80) * f
                if fn is None:
                    astrolabe(c, xx, yy, 60 * f, T)
                else:
                    fn(c, xx, yy, s * f)
            sparkle(c, BX, BY - 140, T - tbx, YELLOW, 10, 80, 200)
        return None
    ev(j, k_march, scene, "pop", 0.7)
    b.hit(j, k_mel, "bongo_high", 0.75, "吉卜赛人来了")
    b.hit(j, k_box, "ding", 0.8, "新玩意儿")


screen9()


# ================================================================ 屏 10：磁铁吸飞锅钉、放大镜聚光、星盘转；乌尔苏拉的金币掉进坩埚熔掉
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_mag = kq(j, wp(12, 0, 0.2), 0)
    k_lens = nx(j, wp(12, 0, 0.55), k_mag)
    k_astro = nx(j, wp(12, 0, 0.9), k_lens)
    k_coin = nx(j, wp(13, 0, 0.5), k_astro)
    k_melt = nx(j, wp(13, 2, 0.4), k_coin)
    L.note("金币")

    def scene(c, kk, T):
        tm, tl, ta, tc, tml = (tb(j, k) for k in (k_mag, k_lens, k_astro, k_coin, k_melt))
        g = pop_scale(T - tm)
        if g <= 0:
            return None
        with K.at(c, cx - 360, cy - 360, 0, g):
            magnet(c, 0, 0, 0.9)
        for i in range(4):
            u = clamp01((T - tm - 0.1 * i) / 0.6)
            sx, sy = cx - 520 + i * 60, cy - 60 + (i % 2) * 90
            x = lerp(sx, cx - 360, ease_in_out(u))
            y = lerp(sy, cy - 300, ease_in_out(u))
            if i % 2 == 0:
                c.drawOval(skia.Rect.MakeXYWH(x - 30, y - 16, 60, 32), K.paint("#5E5E58"))
            else:
                C.line(c, (x - 22, y), (x + 22, y), "#5E5E58", 7)
        if T >= tl:
            with K.at(c, cx - 30, cy - 380, 0, pop_scale(T - tl)):
                magnifier(c, 0, 0, 0.8, 0.5)
            c.drawPath(P((cx - 60, cy - 330), (cx - 10, cy - 200)), wb.marker(ORANGE, 6, 0.8))
            c.drawCircle(cx - 10, cy - 200, 12, K.paint(RED, 0.7))
        if T >= ta:
            astrolabe(c, cx + 320, cy - 360, 90 * pop_scale(T - ta), T)
        jose(c, cx - 380, GY, 0.85, mood="laugh", rh=(cx - 280, GY - 330))
        tag(c, cx - 380, GY - 440, JOSE, 1, 30)
        if T >= tc:
            UX = cx + 410
            with at_pop(c, UX, GY, pop_scale(T - tc)):
                ursula(c, UX, GY, 0.8, mood="sad" if T >= tml else "o")
            PX, PY = cx + 90, GY - 20
            crucible(c, PX, PY, T)
            for i in range(5):
                u = clamp01((T - tc - i * 0.15) / 0.6)
                x = lerp(cx + 300, PX + (i - 2) * 25, ease_in_out(u))
                y = lerp(cy + 40, PY - 150, ease_in_out(u)) - 80 * math.sin(u * math.pi)
                melt = clamp01((T - tml - i * 0.05) / 0.4) if T >= tml else 0
                if u < 1 or melt < 1:
                    coin(c, x, y + 30 * melt, 26 * (1 - 0.8 * melt), 1 - melt)
            K.text(c, "金币", cx + 300, cy - 40, 52, "hand", ORANGE, clamp01((T - tc) / 0.3))
        return None
    ev(j, k_mag, scene, "ding", 0.7)
    b.hit(j, k_lens, "pop", 0.65, "放大镜")
    b.hit(j, k_astro, "wood_high", 0.6, "星盘")
    b.hit(j, k_coin, "shaker", 0.75, "乌尔苏拉的金币")
    b.hit(j, k_melt, "tom", 0.8, "熔了做实验")


screen10()


# ================================================================ 屏 11：帐篷帘掀开，父亲牵着两个儿子进去；箱盖打开，一块冒冷气的冰
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_tent = kq(j, wp(14, 1, 0.4), 0)
    k_pay = nx(j, wp(14, 3, 0.4), k_tent)
    k_in = nx(j, wp(15, 0, 0.5), k_pay)
    k_ice = nx(j, wp(15, 2, 0.4), k_in)
    L.note("看一眼要交钱", "冰")

    def scene(c, kk, T):
        tt, tp, ti, tic = (tb(j, k) for k in (k_tent, k_pay, k_in, k_ice))
        g = pop_scale(T - tt)
        if g <= 0:
            return None
        if T < tic:
            with K.at(c, cx + 120, GY, 0, g):
                tent(c, 0, 0, 640, 600, ease_out(clamp01((T - ti) / 0.4)) if T >= ti else 0)
            if T >= tp:
                with K.at(c, cx + 340, cy - 360, 0, pop_scale(T - tp)):
                    bubble_box(c, 0, 0, 380, 110, -1)
                    K.text(c, "看一眼要交钱", 0, 0, 44, "hand", RED)
                coin(c, cx - 140, cy + 80, 26)
            u = ease_in_out(clamp01((T - ti) / 1.0)) if T >= ti else 0
            x = lerp(cx - 420, cx - 20, u)
            jose(c, x, GY, 0.85, mood="smile", rh=(x + 110, GY - 180))
            kid(c, x + 150, GY, 0.55, "red", mood="smile")
            kid(c, x - 140, GY, 0.65, "yellow", mood="smile")
            return None
        s_ = pop_scale(T - tic)
        box(c, cx, GY - 90, 520, 180, "#8A6A3A", "#5E4128", 7, 8, s_)
        with at_pop(c, cx, GY - 170, s_):
            ice_block(c, cx, GY - 170, 300, 220, T)
        sparkle(c, cx, GY - 480, T - tic, "#7FB2D9", 12, 80, 220)
        with K.at(c, cx, cy - 430, 0, C.slam_scale(T - tic)):
            K.text(c, "冰", 0, 0, 130, "serif_black", BLUE)
        return None
    ev(j, k_tent, scene, "bongo_low", 0.7)
    b.hit(j, k_pay, "pop", 0.7, "看一眼要交钱")
    b.hit(j, k_in, "shaker", 0.65, "掀帘进去")
    b.hit(j, k_ice, "ding", 0.9, "一大块冰")


screen11()


# ================================================================ 屏 12：父亲手按冰上，四周一圈光；小奥雷里亚诺一摸缩手，“冰得像烫手”
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_hand = kq(j, wp(16, 0, 0.6), 0)
    k_holy = nx(j, wp(16, 1, 0.5), k_hand)
    k_aur = nx(j, wp(17, 0, 0.6), k_holy)
    k_hot = nx(j, wp(17, 2, 0.4), k_aur)
    L.note(*AUR, "神迹", "冰得像烫手")
    IX, IY = cx + 20, cy + 230

    def scene(c, kk, T):
        th, tho, ta, tht = (tb(j, k) for k in (k_hand, k_holy, k_aur, k_hot))
        g = pop_scale(T - th)
        if g <= 0:
            return None
        if T >= tho:
            f = ease_out(clamp01((T - tho) / 0.6))
            for q in range(12):
                a = q / 12 * 2 * math.pi + (T - tho) * 0.3
                C.line(c, (IX + 170 * math.cos(a), IY - 120 + 170 * math.sin(a)),
                       (IX + (170 + 120 * f) * math.cos(a), IY - 120 + (170 + 120 * f) * math.sin(a)), YELLOW, 8, f)
            K.text(c, "神迹", cx - 330, cy - 420, 70, "hand", ORANGE, f)
        box(c, IX, IY + 60, 420, 120, "#8A6A3A", "#5E4128", 6, 8)
        ice_block(c, IX, IY, 260, 190, T)
        JX = cx - 330
        with at_pop(c, JX, GY, g):
            jose(c, JX, GY, 1.0, mood="laugh" if T >= tho else "o", rh=(IX - 120, IY - 140))
        tag(c, JX, GY - 490, JOSE, clamp01(g), 30)
        if T >= ta:
            KX = cx + 380
            back = T >= tht
            with at_pop(c, KX, GY, pop_scale(T - ta)):
                kid(c, KX, GY, 0.62, "red", mood="o" if back else "smile",
                    lh=(KX - 80, GY - 230) if back else (IX + 140, IY - 100))
            tag(c, KX, GY - 300, AUR, clamp01((T - ta) / 0.3), 34)
            if back:
                with K.at(c, cx + 280, cy - 230, 4, C.slam_scale(T - tht)):
                    chip(c, 0, 0, "冰得像烫手", BLUE_FILL, BLUE, 50)
                sparkle(c, KX - 80, GY - 230, T - tht, RED, 8, 20, 80)
        return None
    ev(j, k_hand, scene, "bongo_low", 0.7)
    b.hit(j, k_holy, "ding", 0.85, "像摸到神迹")
    b.hit(j, k_aur, "pop", 0.7, "小儿子也摸")
    b.hit(j, k_hot, "rim", 0.85, "冰得像烫手")


screen12()


# ================================================================ 屏 13：旧色闪回“很多年后”：上校背靠墙，对面一排枪的剪影；他的回忆气泡里是那块冰
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    GY = cy + 520
    k_later = kq(j, wp(18, 0, 0.4), 0)
    k_col = nx(j, wp(18, 1, 0.4), k_later)
    k_squad = nx(j, wp(18, 2, 0.4), k_col)
    k_aim = nx(j, wp(18, 3, 0.4), k_squad)
    k_ice = nx(j, wp(19, 2, 0.4), k_aim)
    L.note("很多年后", "奥雷里亚诺上校", "第二代")

    def old(c, kk, T):
        a = clamp01((T - tb(j, 0)) / 0.5)
        r = skia.Rect.MakeXYWH(cx - 580, cy - 585, 1160, 1215)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(r, 18, 18), doAntiAlias=True)
        c.drawRoundRect(r, 18, 18, K.paint(SEPIA, a))
        c.drawRoundRect(r, 18, 18, wb.marker(SEPIA_LINE, 7, a))
        for q in range(14):
            x = cx - 560 + (q * 83) % 1120
            C.line(c, (x, cy - 585), (x + 6, cy + 630), SEPIA_LINE, 2, 0.18 * a)
        for corner in ((cx - 580, cy - 585), (cx + 580, cy - 585), (cx - 580, cy + 630), (cx + 580, cy + 630)):
            c.drawCircle(*corner, 300, K.paint("#5E4128", 0.25 * a))
        c.restore()
        c.drawRoundRect(r, 18, 18, wb.marker(SEPIA_LINE, 7, a))
        return None
    b.custom(j, 0, 0.3, old)

    def scene(c, kk, T):
        tl, tc, ts, ta, ti = (tb(j, k) for k in (k_later, k_col, k_squad, k_aim, k_ice))
        g = pop_scale(T - tl)
        if g <= 0:
            return None
        with K.at(c, cx, cy - 480, -2, C.slam_scale(T - tl)):
            box(c, 0, 0, 360, 100, "#F3E3C0", SEPIA_LINE, 6, 10)
            K.text(c, "很多年后", 0, 2, 62, "serif_black", "#7A3A1E")
        WX = cx - 300
        box(c, WX, GY - 300, 300, 600, "#C9AE80", SEPIA_LINE, 6, 4)
        for q in range(6):
            C.line(c, (WX - 150, GY - 560 + q * 100), (WX + 150, GY - 560 + q * 100), SEPIA_LINE, 3, 0.5)
        if T >= tc:
            with at_pop(c, WX, GY, pop_scale(T - tc)):
                c.saveLayerAlpha(None, 230)
                N.colonel(c, WX, GY, 0.95, mood="flat")
                c.restore()
            name_tag(c, WX, GY - 470, "奥雷里亚诺上校", "#7A3A1E", 38, clamp01((T - tc) / 0.3), "第二代")
        if T >= ts:
            u = ease_out(clamp01((T - ts) / 0.5))
            rifle_row(c, lerp(cx + 650, cx + 160, u), GY, 4, 0.85, 120)
        if T >= ta:
            for q in range(4):
                C.line(c, (cx + 120 + q * 120 - 200, GY - 150), (WX + 60, GY - 200), SEPIA_LINE, 2, 0.5)
        if T >= ti:
            with K.at(c, WX + 90, cy - 230, 0, pop_scale(T - ti)):
                for q, (x, y, r) in enumerate(((-60, 140, 14), (-30, 90, 22))):
                    c.drawCircle(x, y, r, wb.marker(SEPIA_LINE, 4))
                c.drawOval(skia.Rect.MakeXYWH(0, -120, 340, 220), K.paint("#F3E3C0"))
                c.drawOval(skia.Rect.MakeXYWH(0, -120, 340, 220), wb.marker(SEPIA_LINE, 6))
                ice_block(c, 170, 50, 130, 100, T)
            sparkle(c, WX + 260, cy - 240, T - ti, "#7FB2D9", 10, 80, 200)
        return None
    ev(j, k_later, scene, "xiaoluo", 0.7)
    b.hit(j, k_col, "wood_low", 0.65, "奥雷里亚诺上校")
    b.hit(j, k_squad, "tom", 0.8, "行刑队")
    b.hit(j, k_aim, "rim", 0.75, "枪口对着他")
    b.hit(j, k_ice, "ding", 0.9, "想起那块冰")


screen13()


# ================================================================ 屏 14：羊皮卷上第一句逐行展开，“冰块”亮起
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    k_open = kq(j, wp(20, 0, 0.3), 0)
    WORDS = [(3, "多年以后"), (4, "面对行刑队"), (5, "奥雷里亚诺·布恩迪亚上校"), (6, "将会回想起"), (7, "父亲带他去"),
             (8, "见识冰块的"), (9, "那个遥远的下午")]
    ks, prev = [], k_open
    for pi, _ in WORDS:
        k_ = nx(j, wp(20, pi, 0.2), prev)
        ks.append(k_)
        prev = k_
    L.note("第一句", "范晔 译", *(w for _, w in WORDS))

    def scene(c, kk, T):
        to = tb(j, k_open)
        f = ease_out(clamp01((T - to) / 0.7))
        if f <= 0:
            return None
        parchment(c, cx, cy - 40, 1000, 1140, f)
        a = clamp01((T - to - 0.3) / 0.3)
        K.text(c, "第一句", cx - 60, cy - 520, 56, "serif_black", RED, a)
        K.text(c, "范晔 译", cx + 250, cy - 520, 34, "sans_medium", GRAY, a)
        for i, (k_, (_, w)) in enumerate(zip(ks, WORDS)):
            t0 = tb(j, k_)
            if T < t0:
                continue
            y = cy - 400 + i * 130
            hot = i == 5
            size = 60 if len(w) < 9 else 46
            if hot:
                with K.at(c, cx, y, 0, C.slam_scale(T - t0)):
                    K.text(c, w, 0, 0, 74, "serif_black", BLUE)
                sparkle(c, cx + 220, y, T - t0, "#7FB2D9", 10, 50, 150)
            else:
                K.text(c, w, cx, y, size, "serif_black", INK, clamp01((T - t0) / 0.25))
        return None
    ev(j, k_open, scene, "wood_low", 0.65)
    for i, k_ in enumerate(ks):
        b.hit(j, k_, "ding" if i == 5 else "pop", 0.85 if i == 5 else 0.5, "第一句逐段出现")


screen14()


# ================================================================ 屏 15：左边三张卡“杀过人”“败过家”“迷新玩意儿”；右边父亲牵着小儿子走向冰块，夕阳
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z_))
    KT.gu_frame(j, 0)
    GY = cy + 520
    k_c = [kq(j, wp(21, 0, 0.6), 0)]
    k_c.append(nx(j, wp(21, 1, 0.4), k_c[0]))
    k_c.append(nx(j, wp(21, 2, 0.4), k_c[1]))
    k_walk = nx(j, wp(22, 2, 0.3), k_c[2])
    k_sun = nx(j, wp(23, 2, 0.4), k_walk)
    CARDS = ["杀过人", "败过家", "迷新玩意儿"]
    L.note(*CARDS, "一个下午")

    def scene(c, kk, T):
        tw, ts = tb(j, k_walk), tb(j, k_sun)
        if T >= ts:
            f = ease_out(clamp01((T - ts) / 0.8))
            c.drawCircle(cx + 260, cy + 120, 230 * f, K.paint("#F6C84C", 0.55))
        for i, (k_, s) in enumerate(zip(k_c, CARDS)):
            t0 = tb(j, k_)
            if T < t0:
                continue
            fade = 0.45 if T >= tw else 1.0
            with K.at(c, cx - 330, cy - 380 + i * 170, (i - 1) * 3, pop_scale(T - t0)):
                box(c, 0, 0, 340, 120, "#FFFFFF", GRAY if T >= tw else RED, 6, 12, fade)
                K.text(c, s, 0, 0, 50, "hand", INK, fade)
        if T >= tw:
            u = ease_in_out(clamp01((T - tw) / 2.0))
            x = lerp(cx - 120, cx + 200, u)
            box(c, cx + 400, GY - 60, 170, 120, "#8A6A3A", "#5E4128", 5, 6)
            ice_block(c, cx + 400, GY - 120, 110, 90, T)
            jose(c, x, GY, 0.85, mood="smile", rh=(x + 100, GY - 160))
            kid(c, x + 120, GY, 0.55, "red", mood="smile", lh=(x + 100, GY - 160))
        if T >= ts:
            K.text(c, "一个下午", cx + 120, cy - 300, 70, "hand", ORANGE, clamp01((T - ts) / 0.3))
        return None
    ev(j, k_c[0], scene, "wood_high", 0.65)
    for k_ in k_c[1:]:
        b.hit(j, k_, "wood_high", 0.65, "又一张卡")
    b.hit(j, k_walk, "shaker", 0.6, "牵着去看冰")
    b.hit(j, k_sun, "ding", 0.85, "这样一个下午")


screen15()


# ================================================================ 屏 16：评论区；猪尾巴打问号“一百年后”；下一讲：全镇的人睡不着、贴满标签
def enc(c, T, te, th, cx, cy):
    g = pop_scale(T - te)
    with K.at(c, cx - 60, cy + 420, 0, g):
        box(c, 0, 0, 520, 260, N.PARCH, N.PARCH_LINE, 6, 14)
        BH.pig_tail(c, -170, 0, 0.9, 1.0, ease_out(clamp01((T - te) / 0.6)))
        K.text(c, "？", 130, -10, 110, "hand", RED)
    if T >= th:
        with K.at(c, cx + 330, cy + 300, 4, C.slam_scale(T - th)):
            chip(c, 0, 0, "一百年后", NOTE_FILL, ORANGE, 46)


def next_icon(c, x, y, dt):
    with K.at(c, x, y, 0, pop_scale(dt)):
        c.drawCircle(0, -10, 44, K.paint("#FFFFFF"))
        c.drawCircle(0, -10, 44, wb.marker(BLACK, 5))
        for sg in (-1, 1):
            c.drawCircle(sg * 16, -16, 9, K.paint("#FFFFFF"))
            c.drawCircle(sg * 16, -16, 9, wb.marker(BLACK, 4))
            c.drawCircle(sg * 16, -16, 4, K.paint(BLACK))
        c.drawRect(skia.Rect.MakeXYWH(-50, 40, 100, 34), K.paint(NOTE_FILL))
        c.drawRect(skia.Rect.MakeXYWH(-50, 40, 100, 34), wb.marker(RED, 3))


L.note("一百年后")
KT.ending(16, "谁带你第一次见识了什么？", ["爸爸", "外婆", "老师"], 24, 25, enc, 26, ["全镇睡不着了", "连自己是谁都忘了"],
          enc_piece=1, next_icon=next_icon)

# ================================================================ 收尾
L.finish(cover_shot=12, square_shot=11, notes=NOTES)
L.export(globals())
