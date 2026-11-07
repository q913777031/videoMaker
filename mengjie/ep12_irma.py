"""《梦的解析》12 拆梦：弗洛伊德自己的梦，他是怎么一块块拆开的？（白板手绘 + AI 旁白，竖屏 2:3）

复刻实验：照着弗洛伊德拆伊尔玛的梦，自己也拆一遍。
- 开场：一个打问号的梦泡泡、手机搜“解梦”、十几张说法卡片炸开，配音“说法十几种”逐字砸下；
- 痛点：小李拿着手机，说法卡片围了一圈，脑袋一团乱线，卡片全打叉；
- 身边的例子（drop 在第 2 屏）：解梦大全——掉牙 → 出事；蛇 → 发财（金币砸下）；同一条蛇，怕蛇的人和养蛇的人；
- 书中：弗洛伊德拿剪刀剪开自己的梦；1895 年夏天的聚会、伊尔玛；梦里看喉咙、怪她不听话；几位医生朋友、朋友打针、针头不干净；
  把梦剪成一句一句，每句一个问号；前一天朋友说“好些了，可还没全好”，他心里一沉；“责任”箱子推给别人，自己安心；
  梦的肚脐：线都解开了，中间一个结解不开，连着看不见的深处；
- 现在怎么看：试管上一个问号（很难验证）、小李照镜子问自己、零元硬币；
- 三步：一句一行、每句写三个词、圈出反复出现的词；镜子里是自己；评论区、提灯走出雾，下一讲。
文案与出处见 mengjie/PLAN.md「### 12」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_li, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, NOTE_FILL, PAPER_W, SKIN, WOOD, at_pop, box, draw_freud, dream_cloud, moon,
                         sparkle, star)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross

DARK_GREEN, SNAKE_G = "#2F7D3A", "#9ED39A"


# ================================================================ 本讲小元件

def phone(c, x, y, s=1.0, alpha=1.0):
    """手机：(x, y) 为中心。"""
    with K.at(c, x, y, 0, s):
        box(c, 0, 0, 150, 260, "#2E2A28", BLACK, 5, 22, alpha)
        box(c, 0, -6, 128, 210, "#CFE0F5", BLUE, 3, 10, alpha)


def card(c, x, y, s, rot=0.0, color=BLACK, w=170, h=80):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, PAPER_W, color, 5, 12)
        K.text(c, s, 0, 2, 40, "hand", color)


def snake(c, x, y, s=1.0, alpha=1.0, mood="smile"):
    """一条卡通蛇：(x, y) 为身体中心，头在右。"""
    with K.at(c, x, y, 0, s):
        p = skia.Path()
        p.moveTo(-200, 30)
        p.cubicTo(-140, -60, -80, 100, -10, 20)
        p.cubicTo(50, -50, 100, 70, 150, 0)
        c.drawPath(p, wb.marker(DARK_GREEN, 46, alpha))
        c.drawPath(p, wb.marker(SNAKE_G, 32, alpha))
        c.drawOval(skia.Rect.MakeXYWH(130, -50, 110, 80), K.paint(SNAKE_G, alpha))
        c.drawOval(skia.Rect.MakeXYWH(130, -50, 110, 80), wb.marker(DARK_GREEN, 6, alpha))
        for dx in (170, 205):
            c.drawCircle(dx, -22, 7, K.paint(BLACK, alpha))
        if mood == "smile":
            m = skia.Path()
            m.addArc(skia.Rect.MakeXYWH(175, -10, 40, 24), 20, 140)
            c.drawPath(m, wb.marker(BLACK, 4, alpha))
        c.drawPath(P((238, -6), (272, -4), (286, -16)), wb.marker(RED, 4, alpha))
        c.drawPath(P((272, -4), (288, 6)), wb.marker(RED, 4, alpha))


def tooth(c, x, y, s=1.0):
    with K.at(c, x, y, 0, s):
        p = P((-40, -40), (40, -40), (44, 10), (28, 50), (10, 10), (-10, 10), (-28, 50), (-44, 10), close=True)
        c.drawPath(p, K.paint(PAPER_W))
        c.drawPath(p, wb.marker(BLACK, 6))


def coin(c, x, y, r=40, label="¥"):
    c.drawCircle(x, y, r, K.paint("#FFD27A"))
    c.drawCircle(x, y, r, wb.marker(ORANGE, 6))
    K.text(c, label, x, y + 2, r * 1.1, "black", ORANGE)


def draw_woman(c, x, y, s, mouth="flat", alpha=1.0):
    """伊尔玛：长裙、盘发。(x, y) 为脚底；mouth="open" 时张嘴（让人看喉咙）。"""
    hy = y - 290 * s
    for foot in ((x - 30 * s, y), (x + 30 * s, y)):
        C.line(c, (x, y - 80 * s), foot, BLACK, 9, alpha)
    dress = P((x - 40 * s, hy + 55 * s), (x + 40 * s, hy + 55 * s), (x + 85 * s, y - 50 * s), (x - 85 * s, y - 50 * s), close=True)
    c.drawPath(dress, K.paint("#E7D3F2", alpha))
    c.drawPath(dress, wb.marker(NIGHT, 6, alpha))
    for sg in (-1, 1):
        C.line(c, (x + sg * 30 * s, hy + 70 * s), (x + sg * 75 * s, hy + 160 * s), BLACK, 8, alpha)
    c.drawCircle(x, hy - 50 * s, 26 * s, K.paint("#6B4A35", alpha))
    c.drawCircle(x, hy, 44 * s, K.paint(PAPER_W, alpha))
    hair = skia.Path()
    hair.addArc(skia.Rect.MakeXYWH(x - 46 * s, hy - 48 * s, 92 * s, 70 * s), 180, 180)
    hair.close()
    c.drawPath(hair, K.paint("#6B4A35", alpha))
    c.drawCircle(x, hy, 44 * s, wb.marker(BLACK, 8, alpha))
    for dx in (-15, 15):
        c.drawCircle(x + dx * s, hy, 4 * s, K.paint(BLACK, alpha))
    if mouth == "open":
        c.drawOval(skia.Rect.MakeXYWH(x - 12 * s, hy + 12 * s, 24 * s, 22 * s), K.paint("#7A2E2E", alpha))
    else:
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(x - 12 * s, hy + 14 * s, 24 * s, 14 * s), 200, 140)
        c.drawPath(m, wb.marker(BLACK, 5, alpha))


def draw_doc(c, x, y, s, mood="flat", rh=None, alpha=1.0):
    """医生朋友：白大褂 + 额镜，人形同小李。(x, y) 为脚底。"""
    hy = y - 290 * s
    coat = P((x - 48 * s, hy + 60 * s), (x + 48 * s, hy + 60 * s), (x + 62 * s, y - 70 * s), (x - 62 * s, y - 70 * s), close=True)
    c.drawPath(coat, K.paint(PAPER_W, alpha))
    c.drawPath(coat, wb.marker(GRAY, 5, alpha))
    draw_li(c, x, y, s, mood, rh=rh, alpha=alpha)
    C.line(c, (x - 44 * s, hy - 26 * s), (x + 44 * s, hy - 26 * s), GRAY, 5, alpha)
    c.drawCircle(x, hy - 30 * s, 16 * s, K.paint("#DDE3EA", alpha))
    c.drawCircle(x, hy - 30 * s, 16 * s, wb.marker(GRAY, 4, alpha))


def syringe(c, x, y, s=1.0, rot=0.0, dirty=False, alpha=1.0):
    """卡通针筒：(x, y) 为针筒中心，针头朝右。dirty=True 时针头带脏点与臭气线。"""
    with K.at(c, x, y, rot, s):
        C.line(c, (-140, 0), (-90, 0), GRAY, 10, alpha)
        C.line(c, (-140, -26), (-140, 26), GRAY, 10, alpha)
        box(c, 0, 0, 180, 60, "#DDF0FA", BLUE, 6, 10, alpha)
        for i in range(4):
            C.line(c, (-50 + i * 30, -30), (-50 + i * 30, -12), BLUE, 4, alpha)
        C.line(c, (90, 0), (190, 0), GRAY, 6, alpha)
        if dirty:
            for dx, dy in ((130, -10), (160, 8), (180, -8), (110, 10)):
                c.drawCircle(dx, dy, 7, K.paint("#7A5A2B", alpha))
            for i in range(3):
                c.drawPath(P((120 + i * 30, -30), (110 + i * 30, -55), (125 + i * 30, -80)), wb.marker("#7A5A2B", 4, alpha))


def scissors(c, x, y, s=1.0, rot=0.0, open_=0.5):
    """剪刀：(x, y) 为铆钉，刀口朝右。"""
    a = 12 + 18 * open_
    with K.at(c, x, y, rot, s):
        for sg in (-1, 1):
            with K.at(c, 0, 0, sg * a):
                c.drawPath(P((0, 0), (150, -8 * sg), (150, 4 * sg), close=True), K.paint("#DDE3EA"))
                c.drawPath(P((0, 0), (150, -8 * sg), (150, 4 * sg), close=True), wb.marker(GRAY, 5))
                C.line(c, (0, 0), (-50, 0), RED, 10)
                c.drawCircle(-80, 0, 30, wb.marker(RED, 9))
        c.drawCircle(0, 0, 7, K.paint(BLACK))


def chandelier(c, x, y, s=1.0):
    with K.at(c, x, y, 0, s):
        C.line(c, (0, -90), (0, -20), GRAY, 5)
        c.drawPath(P((-120, 0), (-60, 40), (60, 40), (120, 0)), wb.marker(YELLOW, 8))
        for dx in (-120, -60, 0, 60, 120):
            C.line(c, (dx, 0), (dx, -30), "#C98A1B", 6)
            c.drawCircle(dx, -42, 10, K.paint("#FFD27A"))


def calendar(c, x, y, s_top, s_main, w=240, h=220, color=RED):
    box(c, x, y, w, h, PAPER_W, BLACK, 6, 12)
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, 64), K.paint(color))
    K.text(c, s_top, x, y - h / 2 + 32, 40, "hand", "#FFFFFF")
    K.text(c, s_main, x, y + 30, 54, "hand", BLACK)


# ================================================================ 开场

def _hook(H, j, cx, cy, acc):
    """开场：打问号的梦泡泡 → 手机搜“解梦” → 十几张说法卡片炸开；随后“说法十几种”逐字砸下。"""
    b = H.b
    H.note("？", "解梦", "发财", "出事", "升职", "搬家", "贵人")

    def cl(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if dream_cloud(c, cx - 330, cy - 220, 300, 240, sc):
            with at_pop(c, cx - 330, cy - 220, sc):
                K.text(c, "？", cx - 330, cy - 216, 120, "hand", NIGHT)
        return None
    b.custom(j, 0, 0.3, cl, sfx="wood_low", gain=0.7)

    def ph(c, kk, T):
        sc = pop_scale(T - H.tb(j, 1))
        if sc > 0:
            with K.at(c, cx, cy - 200, 4, sc * 1.1):
                phone(c, 0, 0)
                box(c, 0, -60, 110, 46, PAPER_W, GRAY, 3, 20)
                K.text(c, "解梦", 0, -58, 30, "sans_medium", BLACK)
                for r in range(3):
                    C.line(c, (-44, 0 + r * 30), (44 - r * 14, 0 + r * 30), GRAY, 5)
        return None
    b.custom(j, 1, 1.3, ph, sfx="tom", gain=0.75)

    def burst(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        for i, (s_, dx, dy, r) in enumerate((("发财", 330, -330, -8), ("出事", 420, -180, 6), ("升职", 300, -60, -4),
                                             ("搬家", 180, -360, 8), ("贵人", 170, -20, -6))):
            g = pop_scale(dt - i * 0.06)
            if g > 0:
                f = ease_out(clamp01(dt / 0.3))
                with K.at(c, lerp(cx + 60, cx + dx, f), lerp(cy - 200, cy + dy, f), r, g * 0.9):
                    card(c, 0, 0, s_, 0, (RED, BLACK, BLUE, ORANGE, GREEN)[i], 150, 70)
        return None
    b.custom(j, 2, 2.3, burst, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("12", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第二章“释梦的方法：一个梦例的分析”、第七章。",
    "书中例子：1895 年 7 月 23–24 日夜伊尔玛打针的梦；前一天朋友奥托说伊尔玛“好些了，但没全好”；梦的“肚脐”。",
    "现在的研究认为自由联想解梦难以用实验验证；片中交代为书里的做法。小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：小李查手机，说法卡片围一圈；脑袋一团乱线；卡片全打叉
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_li = 0
k_cl1 = nx(j, wt(0, 0, 0.6), k_li)
k_cards = nx(j, wt(0, 3, 0.2), k_cl1)
k_mess = nx(j, wt(1, 0, 0.4), k_cards)
k_x = nx(j, wt(1, 1, 0.4), k_mess)
GY1 = cy + 440
X1 = cx - 60
CARDS1 = [("发财", -400, -40, -6), ("出事", 380, -60, 8), ("升职", -420, 170, 5), ("搬家", 400, 140, -6),
          ("贵人", -330, -250, 4), ("破财", 320, -260, -5), ("要考试", 440, 330, 4), ("有喜事", -440, 360, -4)]
L.note(*[s_ for s_, *_ in CARDS1])


def li1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_li))
    if sc <= 0:
        return None
    hy = GY1 - 290 * 0.95
    with at_pop(c, X1, GY1, sc):
        C.line(c, (X1 - 260, GY1), (X1 + 260, GY1), BLACK, 7)
        mood = "sad" if T >= tb(1, k_mess) else "flat"
        draw_li(c, X1, GY1, 0.95, mood, rh=(X1 + 80, hy + 170))
        with K.at(c, X1 + 110, hy + 150, 10, 0.55):
            phone(c, 0, 0)
    if T >= tb(1, k_mess):
        g = pop_scale(T - tb(1, k_mess))
        p = skia.Path()
        for i in range(26):
            a = i * 0.9 + T * 3
            rr = 30 + (i % 5) * 9
            pt = (X1 + math.cos(a) * rr * 1.6, hy - 110 + math.sin(a) * rr * 0.8)
            p.moveTo(*pt) if i == 0 else p.lineTo(*pt)
        with at_pop(c, X1, hy - 110, g):
            c.drawPath(p, wb.marker(BLACK, 5))
    return None


ev(j, k_li, li1, "wood_low", 0.7)


def cloud1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_cl1))
    x, y = cx + 20, cy - 420
    if dream_cloud(c, x, y, 300, 190, sc):
        with at_pop(c, x, y, sc):
            moon(c, x - 40, y, 40)
            star(c, x + 60, y - 10, 34)
    return None


ev(j, k_cl1, cloud1, "pop", 0.65)


def cards1(c, kk, T, cx=cx, cy=cy):
    for i, (s_, dx, dy, r) in enumerate(CARDS1):
        g = pop_scale(T - tb(1, k_cards) - i * 0.07)
        if g <= 0:
            continue
        with K.at(c, cx + dx, cy + dy, r, g):
            card(c, 0, 0, s_, 0, (RED, BLACK, BLUE, ORANGE)[i % 4])
            if T >= tb(1, k_x) + i * 0.05:
                c.drawPath(cross(0, 0, 36), wb.marker(RED, 9))
    return None


ev(j, k_cards, cards1, "pop", 0.7)
b.hit(j, k_mess, "shaker", 0.7, "越看越糊涂")
b.hit(j, k_x, "rim", 0.8, "哪个也不信")

# ================================================================ 屏 2：解梦大全——掉牙 → 出事；蛇 → 发财（drop：金币砸下）
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_pg = 1
k_tooth = max(k_pg + 1, min(kq(j, wt(3, 0, 0.5), k_pg + 1), KD - 2))
k_bad = max(k_tooth + 1, min(kq(j, wt(3, 1, 0.3), k_tooth + 1), KD - 1))
L.note("解梦大全", "家里出事", "发财")


def page2(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 60, sc):
        box(c, cx, cy - 60, 940, 880, PAPER_W, BLACK, 8, 30)
        c.drawRoundRect(skia.Rect.MakeXYWH(cx - 470, cy - 500, 940, 120), 30, 30, K.paint(NIGHT))
        K.text(c, "解梦大全", cx, cy - 440, 76, "hand", "#FFE39A")
        moon(c, cx + 340, cy - 440, 34)
        C.line(c, (cx - 420, cy - 60), (cx + 420, cy - 60), GRAY, 4)
    return None


ev(j, k_pg, pop_fn(j, k_pg, page2), "wood_low", 0.7)


def tooth2(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(2, k_tooth))
    if g <= 0:
        return None
    with at_pop(c, cx - 290, cy - 220, g):
        tooth(c, cx - 290, cy - 230, 1.6)
        drop_ = ease_out(clamp01((T - tb(2, k_tooth)) / 0.5))
        tooth(c, cx - 200, cy - 210 + 60 * drop_, 0.7)
    if T >= tb(2, k_bad):
        f = ease_out(clamp01((T - tb(2, k_bad)) / 0.3))
        c.drawPath(wb.arrow((cx - 150, cy - 220), (lerp(cx - 150, cx + 20, f), cy - 220), 0.0, 30), wb.marker(GRAY, 7))
        g2 = pop_scale(T - tb(2, k_bad))
        with K.at(c, cx + 220, cy - 220, -3, g2):
            K.text(c, "家里出事", 0, 0, 74, "hand", BLACK)
    return None


ev(j, k_tooth, tooth2, "wood_high", 0.7)
b.hit(j, k_bad, "rim", 0.75, "家里出事")


def snake2(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(2, KD)
    g = C.slam_scale(dt)
    if g <= 0:
        return None
    with K.at(c, cx - 250, cy + 150, 0, g):
        snake(c, 0, 0, 0.85)
    c.drawPath(wb.arrow((cx - 20, cy + 150), (cx + 90, cy + 150), 0.0, 30), wb.marker(GRAY, 7))
    for i in range(7):
        f = clamp01((dt - i * 0.05) / 0.45)
        if f <= 0:
            continue
        x = cx + 140 + (i * 53) % 300
        y = lerp(cy - 30, cy + 300 - (i % 3) * 45, ease_out(f))
        coin(c, x, y, 36)
    sparkle(c, cx + 280, cy + 180, dt, YELLOW, 10, 140, 260)
    return None


L.note("¥")
ev(j, KD, snake2, "kick", 0.95)
ev(j, KD, L.slam_text("发财", cx + 280, cy + 70, 110, RED, j, KD, rot=-6))

# ================================================================ 屏 3：同一条蛇——怕蛇的人缩成一团，养蛇的人抱着它笑；“能一样吗？”
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_sn = kq(j, wt(4, 0, 0.5), 0)
k_fear = nx(j, wt(4, 1, 0.2), k_sn)
k_keep = nx(j, wt(4, 1, 0.8), k_fear)
k_q3 = nx(j, wt(4, 2, 0.5), k_keep)
GY3 = cy + 440
L.note("怕蛇", "养蛇", "一样吗？")


def sn3(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 300, sc):
        dream_cloud(c, cx, cy - 300, 640, 360, 1.0)
        snake(c, cx - 50, cy - 290, 1.0)
    return None


ev(j, k_sn, pop_fn(j, k_sn, sn3), "pop", 0.7)


def fear3(c, sc, T, cx=cx, cy=cy):
    x = cx - 300
    with at_pop(c, x, GY3, sc):
        sh = 5 * math.sin(T * 45)
        hy = GY3 - 290 * 0.9
        draw_li(c, x + sh, GY3, 0.9, "sad", lh=(x - 40, hy + 30), rh=(x + 40, hy + 30))
        for i in range(3):
            C.line(c, (x - 110 - i * 14, hy - 40 + i * 40), (x - 150 - i * 14, hy - 50 + i * 40), BLUE, 5)
        A._sweat(c, x + 70, hy - 30)
        box(c, x, GY3 + 50, 160, 70, PAPER_W, BLUE, 5, 30)
        K.text(c, "怕蛇", x, GY3 + 52, 44, "hand", BLUE)
    return None


ev(j, k_fear, pop_fn(j, k_fear, fear3), "wood_low", 0.7)


def keep3(c, sc, T, cx=cx, cy=cy):
    x = cx + 300
    with at_pop(c, x, GY3, sc):
        hy = GY3 - 290 * 0.9
        draw_li(c, x, GY3, 0.9, "smile", lh=(x - 70, hy + 140), rh=(x + 70, hy + 140))
        snake(c, x + 10, hy + 150, 0.42)
        c.drawPath(C.heart_path(x + 120, hy - 70, 26), K.paint("#F6C3BE"))
        c.drawPath(C.heart_path(x + 120, hy - 70, 26), wb.marker(RED, 5))
        box(c, x, GY3 + 50, 160, 70, PAPER_W, GREEN, 5, 30)
        K.text(c, "养蛇", x, GY3 + 52, 44, "hand", GREEN)
    return None


ev(j, k_keep, pop_fn(j, k_keep, keep3), "wood_high", 0.7)
ev(j, k_q3, L.slam_text("一样吗？", cx, cy - 20, 96, RED, j, k_q3, rot=-3), "kick", 0.85)
b.shots[j].shake = [(k_q3, 7.0)]

# ================================================================ 屏 4：弗洛伊德拿剪刀剪开自己的梦；1895 年夏天的聚会，伊尔玛
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_fr = kq(j, wt(5, 0, 0.4), 0)
k_cut = nx(j, wt(5, 1, 0.7), k_fr)
k_yr = nx(j, wt(6, 0, 0.4), k_cut)
k_party = nx(j, wt(6, 1, 0.5), k_yr)
k_irma = nx(j, wt(6, 2, 0.6), k_party)
CL4 = (cx + 110, cy - 200)
L.note("自己的梦", "1895 夏", "伊尔玛")


def fr4(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 360, cy + 470
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 0.95, "smile" if T >= tb(4, k_cut) else "flat")
    return None


ev(j, k_fr, pop_fn(j, k_fr, fr4), "wood_low", 0.7)


def cloud4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_fr) - 0.25)
    if not dream_cloud(c, CL4[0], CL4[1], 780, 560, sc, tail_to=(cx - 340, cy + 120)):
        return None
    with at_pop(c, CL4[0], CL4[1], sc):
        x, y = CL4
        if T < tb(4, k_party):
            K.text(c, "自己的梦", x, y, 72, "hand", NIGHT)
        else:
            g = pop_scale(T - tb(4, k_party))
            with at_pop(c, x, y, g):
                chandelier(c, x, y - 150, 0.9)
                for i, dx in enumerate((-220, 200)):
                    draw_li(c, x + dx, y + 210, 0.5, "smile")
                C.line(c, (x - 300, y + 212), (x + 300, y + 212), GRAY, 5)
        if T >= tb(4, k_irma):
            g = pop_scale(T - tb(4, k_irma))
            with at_pop(c, x, y + 210, g):
                draw_woman(c, x, y + 210, 0.62, "flat")
                box(c, x, y - 40, 170, 60, PAPER_W, NIGHT, 4, 30)
                K.text(c, "伊尔玛", x, y - 38, 40, "hand", NIGHT)
    # 剪刀：从泡泡左侧剪进去，留下一道虚线口子
    if T >= tb(4, k_cut):
        dt = T - tb(4, k_cut)
        f = ease_out(clamp01(dt / 0.5))
        x0, y0 = CL4[0] - 400, CL4[1] + 250
        for i in range(int(f * 6)):
            C.line(c, (x0 + i * 40, y0), (x0 + i * 40 + 22, y0), RED, 6)
        scissors(c, x0 - 40 + f * 240, y0, 0.8, 0, 0.5 + 0.5 * math.sin(dt * 18))
    return None


ev(j, k_fr, cloud4, None)
b.hit(j, k_cut, "clap", 0.8, "剪开自己的梦")


def yr4(c, kk, T, cx=cx, cy=cy):
    g = C.slam_scale(T - tb(4, k_yr))
    if g <= 0:
        return None
    with K.at(c, cx + 300, cy + 300, -5, g):
        box(c, 0, 0, 300, 120, NOTE_FILL, ORANGE, 7, 12)
        K.text(c, "1895 夏", 0, 2, 64, "hand", ORANGE)
        A.sun(c, 150, -60, 30)
    return None


ev(j, k_yr, yr4, "tom", 0.8)
b.hit(j, k_party, "pop", 0.7, "梦里一场聚会")
b.hit(j, k_irma, "ding", 0.75, "伊尔玛")

# ================================================================ 屏 5：梦里看喉咙，“是你不听我的”；医生朋友们来了；朋友打针，针头不干净
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_look = kq(j, wt(7, 0, 0.4), 0)
k_blame = nx(j, wt(7, 1, 0.3), k_look)
k_docs = nx(j, wt(8, 0, 0.5), k_blame)
k_shot = nx(j, wt(8, 2, 0.5), k_docs)
k_dirty = nx(j, wt(8, 3, 0.5), k_shot)
GY5 = cy + 430
L.note("梦里", "啊——", "你不听我的", "针头不干净")


def look5(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 300, GY5, sc):
        chandelier(c, cx - 80, cy - 400, 1.1)
        box(c, cx - 420, cy - 420, 150, 66, NIGHT, NIGHT, 4, 30)
        K.text(c, "梦里", cx - 420, cy - 418, 40, "hand", "#FFE39A")
        C.line(c, (cx - 560, GY5), (cx + 560, GY5), GRAY, 6)
        draw_woman(c, cx - 430, GY5, 0.95, "open")
        K.text(c, "啊——", cx - 400, GY5 - 450, 48, "hand", NIGHT)
        hy = GY5 - 290 * 0.95
        draw_freud(c, cx - 220, GY5, 0.95, "sad" if T >= tb(5, k_blame) else "flat", cigar=False)
        # 小手电照向伊尔玛的嘴
        lx, ly = cx - 300, hy + 60
        C.line(c, (lx, ly), (lx - 40, ly - 10), BLACK, 14)
        c.drawPath(P((lx - 40, ly - 10), (cx - 410, hy - 10), (cx - 410, hy + 50), close=True), K.paint("#FFE39A", 0.6))
    return None


ev(j, k_look, pop_fn(j, k_look, look5), "wood_low", 0.7)
ev(j, k_blame, L.pop_bubble("你不听我的", cx - 260, cy - 180, j, k_blame, 52, RED, tail=-1), "rim", 0.75)


def docs5(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx + 300, GY5, sc):
        draw_doc(c, cx + 120, GY5, 0.85, "flat")
        draw_doc(c, cx + 470, GY5, 0.85, "flat")
        shot = T >= tb(5, k_shot)
        hy = GY5 - 290 * 0.85
        draw_doc(c, cx + 300, GY5, 0.85, "smile" if shot else "flat", rh=(cx + 360, hy + 100) if shot else None)
    return None


ev(j, k_docs, pop_fn(j, k_docs, docs5), "wood_high", 0.7)


def shot5(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(5, k_shot))
    if g <= 0:
        return None
    hy = GY5 - 290 * 0.85
    with K.at(c, cx + 300, hy - 150, -25, g):
        syringe(c, 0, 0, 1.05, 0, dirty=T >= tb(5, k_dirty))
    return None


ev(j, k_shot, shot5, "pop", 0.75)
ev(j, k_dirty, L.stamp("针头不干净", cx + 300, cy - 230, 62, j, k_dirty, rot=-6), "kick", 0.85)
b.shots[j].shake = [(k_dirty, 7.0)]

# ================================================================ 屏 6：把梦剪成一句一句，每句后面一个“想到了什么？”
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_c6 = 0
k_split = nx(j, wt(9, 0, 0.7), k_c6)
k_q6 = nx(j, wt(9, 1, 0.6), k_split)
STRIPS = ["一场聚会", "怪伊尔玛", "医生都来了", "朋友打针"]
L.note(*STRIPS, "？", "想到了什么？")


def strips6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_c6))
    if sc <= 0:
        return None
    m = ease_in_out(clamp01((T - tb(6, k_split)) / 0.45)) if T >= tb(6, k_split) else 0.0
    x0, y0 = cx - 160, cy - 120
    if m < 1:
        dream_cloud(c, x0, y0, 720, 640, sc, alpha=1 - m)
    for i, s_ in enumerate(STRIPS):
        y = lerp(y0 - 180 + i * 120, cy - 330 + i * 190, m)
        x = lerp(x0, cx - 230 + (i % 2) * 30, m)
        with at_pop(c, x0, y0, sc):
            with K.at(c, x, y, lerp(0, (-3, 2, -2, 3)[i], m)):
                box(c, 0, 0, 440, 110, PAPER_W, NIGHT, 6, 6, 0.5 + 0.5 * m)
                K.text(c, s_, 0, 2, 56, "hand", NIGHT)
                if m > 0.5:
                    C.line(c, (-230, -55), (-230, 55), RED, 4, m)
        if T >= tb(6, k_q6) + i * 0.15:
            g = pop_scale(T - tb(6, k_q6) - i * 0.15)
            with K.at(c, cx + 230, y, 0, g):
                c.drawCircle(0, 0, 50, K.paint(NOTE_FILL))
                c.drawCircle(0, 0, 50, wb.marker(ORANGE, 6))
                K.text(c, "？", 0, 4, 70, "hand", RED)
            c.drawPath(wb.arrow((x + 230, y), (cx + 170, y), 0.0, 20), wb.marker(GRAY, 5, clamp01(g)))
    return None


ev(j, k_c6, strips6, "pop", 0.7)
b.hit(j, k_split, "clap", 0.8, "剪成一句一句")
b.hit(j, k_q6, "pop", 0.65, "第一个问号")
for i in range(1, 4):
    if k_q6 + i <= KT.klast(j):
        b.hit(j, k_q6 + i, "pop", 0.55, f"第{i + 1}个问号")


def fr6(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(6, k_q6) - 0.6)
    if g <= 0:
        return None
    x, y = cx + 380, cy + 500
    with at_pop(c, x, y, g):
        draw_freud(c, x, y, 0.7, "smile", cigar=False)
    with K.at(c, cx + 110, cy + 400, 0, g):
        box(c, 0, 0, 330, 90, PAPER_W, RED, 5, 40)
        K.text(c, "想到了什么？", 0, 2, 50, "hand", RED)
    return None


b.custom(j, k_q6, k_q6 + 0.3, fr6)

# ================================================================ 屏 7：前一天，朋友说“好些了，可还没全好”；他心里一沉：怪我没治好？
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_cal = kq(j, wt(10, 0, 0.3), 0)
k_talk = nx(j, wt(10, 1, 0.5), k_cal)
k_hurt = nx(j, wt(11, 1, 0.3), k_talk)
GY7 = cy + 440
L.note("前一天", "7月23日", "朋友", "好些了，可还没全好", "怪我没治好？")


def cal7(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 360, cy - 380, sc):
        with K.at(c, cx - 360, cy - 380, -4):
            calendar(c, 0, 0, "前一天", "7月23日", 280, 220)
    return None


ev(j, k_cal, pop_fn(j, k_cal, cal7), "wood_high", 0.7)


def people7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_cal) - 0.3)
    if sc <= 0:
        return None
    hurt = T >= tb(7, k_hurt)
    with at_pop(c, cx, GY7, sc):
        C.line(c, (cx - 520, GY7), (cx + 520, GY7), BLACK, 6)
        draw_doc(c, cx + 300, GY7, 1.0, "flat")
        box(c, cx + 300, GY7 + 55, 130, 60, PAPER_W, GRAY, 4, 30)
        K.text(c, "朋友", cx + 300, GY7 + 57, 38, "hand", GRAY)
        draw_freud(c, cx - 250, GY7, 1.0, "sad" if hurt else "smile", cigar=not hurt)
        if hurt:
            A._sweat(c, cx - 170, GY7 - 330, 1.2)
    return None


b.custom(j, k_cal, k_cal + 0.3, people7)
ev(j, k_talk, L.pop_bubble("好些了，可还没全好", cx + 180, cy - 50, j, k_talk, 50, BLACK, tail=1), "pop", 0.7)


def hurt7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_hurt))
    x, y = cx + 80, cy - 360
    if not dream_cloud(c, x, y, 520, 220, sc, tail_to=(cx - 250, GY7 - 360)):
        return None
    with at_pop(c, x, y, sc):
        K.text(c, "怪我没治好？", x, y + 4, 60, "hand", RED)
    return None


ev(j, k_hurt, hurt7, "tom", 0.8)

# ================================================================ 屏 8：拆到最后——“责任”箱子推给别人，自己安心
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_box8 = kq(j, wt(12, 0, 0.4), 0)
k_push = nx(j, wt(12, 1, 0.6), k_box8)
k_calm = nx(j, wt(12, 2, 0.5), k_push)
GY8 = cy + 420
L.note("责任", "安心")


def push8(c, sc, T, cx=cx, cy=cy):
    calm = T >= tb(8, k_calm)
    f = ease_in_out(clamp01((T - tb(8, k_push)) / 0.7)) if T >= tb(8, k_push) else 0.0
    with at_pop(c, cx, GY8, sc):
        C.line(c, (cx - 540, GY8), (cx + 540, GY8), BLACK, 6)
        for i, dx in enumerate((300, 460)):
            draw_doc(c, cx + dx, GY8, 0.8, "sad" if f > 0.9 else "flat")
        bx = lerp(cx - 120, cx + 130, f)
        with K.at(c, bx, GY8 - 110, 4 * math.sin(f * math.pi * 4)):
            box(c, 0, 0, 230, 210, WOOD, "#A9773E", 8, 10)
            K.text(c, "责任", 0, 4, 70, "hand", RED)
        hy = GY8 - 290 * 0.95
        fx = lerp(cx - 330, cx - 120, f) if not calm else cx - 330
        if calm:
            draw_freud(c, fx, GY8, 0.95, "smile")
        else:
            draw_freud(c, fx, GY8, 0.95, "flat", cigar=False)
            C.line(c, (fx, hy + 80 * 0.95), (bx - 115, GY8 - 150), "#3D4A63", 12)
        if 0 < f < 1:
            for i in range(3):
                C.line(c, (bx - 160 - i * 20, GY8 - 180 + i * 50), (bx - 230 - i * 20, GY8 - 180 + i * 50), GRAY, 5)
    return None


ev(j, k_box8, pop_fn(j, k_box8, push8), "wood_low", 0.7)
b.hit(j, k_push, "tom", 0.8, "责任推过去")


def calm8(c, kk, T, cx=cx, cy=cy):
    g = C.slam_scale(T - tb(8, k_calm))
    if g <= 0:
        return None
    with K.at(c, cx - 200, cy - 230, -4, g):
        c.drawCircle(0, 0, 170, K.paint("#D3EDDC"))
        c.drawCircle(0, 0, 170, wb.marker(GREEN, 10))
        K.text(c, "安心", 0, -10, 100, "hand", GREEN)
        c.drawPath(check(110, 90, 40), wb.marker(GREEN, 10))
    return None


ev(j, k_calm, calm8, "kick", 0.85)
b.shots[j].shake = [(k_calm, 7.0)]

# ================================================================ 屏 9：梦的肚脐——线都解开了，中间一个结解不开，连着看不见的深处
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_cl9 = kq(j, wt(13, 0, 0.3), 0)
k_loose = nx(j, wt(13, 1, 0.5), k_cl9)
k_knot = nx(j, wt(13, 2, 0.6), k_loose)
k_navel = nx(j, wt(13, 3, 0.4), k_knot)
k_deep = nx(j, wt(13, 4, 0.5), k_navel)
CL9 = (cx, cy - 240)
L.note("拆不开", "肚脐", "看不见的深处")


def knot_path(x, y, r):
    p = skia.Path()
    for i in range(40):
        a = i * 2.4
        rr = r * (0.4 + 0.6 * ((i * 7) % 10) / 10)
        pt = (x + math.cos(a) * rr, y + math.sin(a) * rr * 0.8)
        p.moveTo(*pt) if i == 0 else p.lineTo(*pt)
    return p


def navel9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k_cl9))
    if not dream_cloud(c, CL9[0], CL9[1], 900, 600, sc):
        return None
    x, y = CL9
    with at_pop(c, x, y, sc):
        loose = ease_out(clamp01((T - tb(9, k_loose)) / 0.6)) if T >= tb(9, k_loose) else 0.0
        for i in range(6):
            a = -math.pi / 2 + (i - 2.5) * 0.55
            if i >= 3:
                a = math.pi / 2 + (i - 4) * 0.7 + math.pi
            ang = i * math.pi / 3 + 0.3
            ex, ey = x + math.cos(ang) * 330, y + math.sin(ang) * 210
            wav = 30 * (1 - loose)
            p = skia.Path()
            p.moveTo(x, y)
            p.cubicTo(lerp(x, ex, 0.3) + wav, lerp(y, ey, 0.3) - wav, lerp(x, ex, 0.6) - wav * 2, lerp(y, ey, 0.6) + wav, ex, ey)
            c.drawPath(p, wb.marker((RED, BLUE, GREEN, ORANGE, NIGHT, "#8E2C5C")[i], 7))
            if loose > 0:
                c.drawPath(check(ex, ey - 30, 18), wb.marker(GREEN, 6, loose))
        if T >= tb(9, k_knot):
            g = pop_scale(T - tb(9, k_knot))
            with K.at(c, x, y, T * 20, g):
                c.drawCircle(0, 0, 70, K.paint("#F6C3BE"))
                c.drawPath(knot_path(0, 0, 70), wb.marker(RED, 7))
    return None


ev(j, k_cl9, navel9, "pop", 0.7)
b.hit(j, k_loose, "shaker", 0.7, "一根根线解开")
b.hit(j, k_knot, "wood_high", 0.75, "中间一个结")
ev(j, k_navel, L.stamp("肚脐", cx + 280, cy - 470, 70, j, k_navel, rot=6), "kick", 0.85)
b.shots[j].shake = [(k_navel, 6.0)]


def deep9(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k_deep)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.6))
    x, y0 = CL9[0], CL9[1] + 70
    p = skia.Path()
    p.moveTo(x, y0)
    n = int(6 + 20 * f)
    for i in range(n):
        yy = y0 + i * 24
        p.lineTo(x + math.sin(i * 0.8) * (20 + i * 3), yy)
    c.drawPath(p, wb.marker(NIGHT, 6))
    yb = cy + 400
    for i in range(4):
        r = (60 + i * 50) * f
        c.drawOval(skia.Rect.MakeXYWH(x - r * 1.6, yb - r * 0.4, r * 3.2, r * 0.8), wb.marker(NIGHT, 6, 1 - i * 0.2))
    c.drawOval(skia.Rect.MakeXYWH(x - 90 * f, yb - 22 * f, 180 * f, 44 * f), K.paint(NIGHT, 0.85))
    K.text(c, "看不见的深处", x + 320, yb + 80, 50, "hand", NIGHT, f)
    return None


ev(j, k_deep, deep9, "tom", 0.75)


def fr9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k_cl9) - 0.3)
    if sc <= 0:
        return None
    x, y = cx - 420, cy + 500
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 0.75, "flat")
    return None


b.custom(j, k_cl9, k_cl9 + 0.3, fr9)

# ================================================================ 屏 10：现在怎么看——试管上一个问号；小李照镜子问自己；零元硬币
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_lab = kq(j, wt(14, 1, 0.4), 0)
k_self = nx(j, wt(14, 2, 0.5), k_lab)
k_free = nx(j, wt(14, 3, 0.4), k_self)
GY10 = cy + 440
L.note("很难验证", "问问自己", "0元")


def lab10(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 250, cy - 280
    with at_pop(c, x, y, sc):
        for i, dx in enumerate((-130, 0, 130)):
            tube = skia.Rect.MakeXYWH(x + dx - 34, y - 140, 68, 280)
            c.drawRoundRect(tube, 34, 34, K.paint(PAPER_W))
            c.drawRect(skia.Rect.MakeXYWH(x + dx - 34, y + 20 - i * 30, 68, 120 + i * 30), K.paint(("#CFE0F5", "#F6C3BE", "#D3EDDC")[i]))
            c.drawRoundRect(tube, 34, 34, wb.marker(BLACK, 6))
        K.text(c, "？", x + 200, y - 130, 120, "hand", RED)
        box(c, x, y + 220, 300, 80, PAPER_W, RED, 5, 30)
        K.text(c, "很难验证", x, y + 222, 50, "hand", RED)
    return None


ev(j, k_lab, pop_fn(j, k_lab, lab10), "wood_low", 0.7)


def self10(c, sc, T, cx=cx, cy=cy):
    x = cx + 120
    with at_pop(c, x, GY10, sc):
        C.line(c, (x - 220, GY10), (cx + 560, GY10), BLACK, 6)
        draw_li(c, x, GY10, 0.9, "smile", rh=(x + 120, GY10 - 290 * 0.9 + 110))
        mx, my = x + 290, GY10 - 300
        C.line(c, (mx, my + 110), (mx, GY10), "#A9773E", 10)
        c.drawOval(skia.Rect.MakeXYWH(mx - 90, my - 120, 180, 240), K.paint("#E6F2FA"))
        c.drawOval(skia.Rect.MakeXYWH(mx - 90, my - 120, 180, 240), wb.marker("#A9773E", 9))
        draw_li(c, mx, my + 130, 0.42, "smile")
        K.text(c, "问问自己", x + 120, GY10 - 520, 54, "hand", BLUE)
    return None


ev(j, k_self, pop_fn(j, k_self, self10), "wood_high", 0.7)


def free10(c, kk, T, cx=cx, cy=cy):
    g = C.slam_scale(T - tb(10, k_free))
    if g <= 0:
        return None
    with K.at(c, cx - 330, cy + 280, -8, g):
        c.drawCircle(0, 0, 110, K.paint("#FFD27A"))
        c.drawCircle(0, 0, 110, wb.marker(ORANGE, 9))
        c.drawCircle(0, 0, 86, wb.marker(ORANGE, 4))
        K.text(c, "0元", 0, 4, 76, "black", ORANGE)
    sparkle(c, cx - 330, cy + 280, T - tb(10, k_free), YELLOW, 8, 130, 210)
    return None


ev(j, k_free, free10, "ding", 0.8)

# ================================================================ 屏 11：说回我们自己——小李拿剪刀对着自己的梦；“三步”
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_li11 = kq(j, wt(15, 0, 0.4), 0)
k_3 = nx(j, wt(15, 1, 0.5), k_li11)
GY11 = cy + 430
L.note("三步")


def li11(c, sc, T, cx=cx, cy=cy):
    x = cx - 250
    with at_pop(c, x, GY11, sc):
        C.line(c, (x - 300, GY11), (x + 300, GY11), BLACK, 7)
        hy = GY11 - 290 * 0.95
        draw_li(c, x, GY11, 0.95, "smile", rh=(x + 90, hy + 100))
        scissors(c, x + 110, hy + 90, 0.6, -50, 0.5 + 0.5 * math.sin(T * 8))
        dream_cloud(c, x - 20, cy - 300, 360, 230, 1.0, tail_to=(x - 30, hy - 60))
        moon(c, x - 80, cy - 300, 44)
        star(c, x + 50, cy - 310, 38)
    return None


ev(j, k_li11, pop_fn(j, k_li11, li11), "wood_low", 0.7)


def three11(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(11, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 270, cy - 80, -4, sc):
        c.drawCircle(0, 0, 190, K.paint("#FDE2E2"))
        c.drawCircle(0, 0, 190, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 130, "hand", L.ACC)
    return None


ev(j, k_3, three11, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 12：做法一——一句一行：便签上四行短话
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_n12 = kq(j, wt(16, 1, 0.2), 0)
k_ln = [nx(j, wt(16, 1, 0.7), k_n12)]
for _ in range(3):
    k_ln.append(cap(j, k_ln[-1] + 1))
LN12 = ["我在开会", "老板变成了猫", "我找不到笔", "大家都笑了"]
L.note("第一", "一句一行", *LN12)


def note12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_n12))
    if sc <= 0:
        return None
    with K.at(c, cx, cy - 20, -2, sc):
        K.text(c, "第一", -300, -470, 70, "hand", L.ACC)
        K.text(c, "一句一行", 40, -470, 60, "hand", BLACK)
        box(c, 0, 40, 720, 720, NOTE_FILL, ORANGE, 7, 12)
        for i, s_ in enumerate(LN12):
            y = -200 + i * 165
            C.line(c, (-320, y + 55), (320, y + 55), "#E3C79A", 4)
            g = pop_scale(T - tb(12, k_ln[i]))
            if g > 0:
                K.text(c, f"{i + 1}", -280, y, 60, "black", ORANGE, clamp01(g * 2))
                with K.at(c, -220, y, 0, g):
                    K.text(c, s_, 0, 0, 66, "hand", BLACK, 1.0, "left")
    return None


ev(j, k_n12, note12, "wood_low", 0.7)
for i, k_ in enumerate(k_ln):
    b.hit(j, k_, "pop", 0.7, f"第{i + 1}句")

# ================================================================ 屏 13：做法二——每句后面写三个词，不挑不改
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_h13 = kq(j, wt(17, 1, 0.2), 0)
k_row = [nx(j, wt(17, 1, 0.7), k_h13)]
for _ in range(2):
    k_row.append(cap(j, k_row[-1] + 1))
k_noedit = nx(j, wt(17, 2, 0.5), k_row[-1])
ROWS = [("开会", ["周报", "紧张", "迟到"]), ("找不到笔", ["考试", "紧张", "丢三落四"]), ("大家都笑了", ["丢脸", "同事", "紧张"])]
L.note("第二", "每句三个词", "不挑不改", *[r for r, _ in ROWS], *[w for _, ws in ROWS for w in ws])


def chip(c, x, y, s_, color=BLACK, fill=PAPER_W, size=48):
    w = K.text_w(s_, size, "hand") + 50
    box(c, x, y, w, 84, fill, color, 5, 40)
    K.text(c, s_, x, y + 2, size, "hand", color)


def rows13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_h13))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy - 470, sc):
        K.text(c, "第二", cx - 380, cy - 470, 70, "hand", L.ACC)
        K.text(c, "每句三个词", cx - 30, cy - 470, 60, "hand", BLACK)
    for i, (s_, ws) in enumerate(ROWS):
        g = pop_scale(T - tb(13, k_row[i]))
        if g <= 0:
            continue
        y = cy - 240 + i * 240
        with at_pop(c, cx, y, g):
            box(c, cx - 360, y, 340, 100, PAPER_W, NIGHT, 6, 8)
            K.text(c, s_, cx - 360, y + 2, 54, "hand", NIGHT)
            c.drawPath(wb.arrow((cx - 180, y), (cx - 80, y), 0.0, 20), wb.marker(GRAY, 6))
            xx = cx - 60
            for m, w in enumerate(ws):
                ww = K.text_w(w, 48, "hand") + 50
                chip(c, xx + ww / 2, y, w, ORANGE, "#FFF4D6", 48)
                xx += ww + 18
    return None


ev(j, k_h13, rows13, "wood_low", 0.7)
for i, k_ in enumerate(k_row):
    b.hit(j, k_, "pop", 0.7, f"第{i + 1}句写三个词")
ev(j, k_noedit, L.stamp("不挑不改", cx + 150, cy + 420, 70, j, k_noedit, rot=-5), "kick", 0.85)

# ================================================================ 屏 14：做法三——反复出现的词圈出来：“紧张”
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_h14 = kq(j, wt(18, 0, 0.5), 0)
k_circ = nx(j, wt(18, 1, 0.5), k_h14)
k_big = nx(j, wt(18, 2, 0.6), k_circ)
WORDS14 = [["周报", "紧张", "迟到"], ["考试", "紧张", "丢三落四"], ["丢脸", "同事", "紧张"]]
L.note("第三", "反复出现", "最想说的", "紧张")


def grid14(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 200, sc):
        K.text(c, "第三", cx - 380, cy - 470, 70, "hand", L.ACC)
        K.text(c, "反复出现", cx - 50, cy - 470, 60, "hand", BLACK)
        for r, ws in enumerate(WORDS14):
            for m, w in enumerate(ws):
                x, y = cx - 340 + m * 340, cy - 300 + r * 160
                chip(c, x, y, w, RED if w == "紧张" and T >= tb(14, k_circ) else GRAY, PAPER_W, 54)
    return None


ev(j, k_h14, pop_fn(j, k_h14, grid14), "wood_low", 0.7)


def circ14(c, kk, T, cx=cx, cy=cy):
    t0 = tb(14, k_circ)
    if T < t0:
        return None
    for r, ws in enumerate(WORDS14):
        m = ws.index("紧张")
        f = clamp01((T - t0 - r * 0.12) / 0.3)
        x, y = cx - 340 + m * 340, cy - 300 + r * 160
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(x - 120, y - 66, 240, 132), -90, 359 * f)
        c.drawPath(p, wb.marker(RED, 7))
        if T >= tb(14, k_big):
            g = ease_out(clamp01((T - tb(14, k_big)) / 0.4))
            c.drawPath(wb.arrow((x, y + 60), (lerp(x, cx, g), lerp(y + 60, cy + 180, g)), 0.1, 24), wb.marker(RED, 5, g))
    return None


ev(j, k_circ, circ14, "rim", 0.8)


def big14(c, kk, T, cx=cx, cy=cy):
    g = C.slam_scale(T - tb(14, k_big))
    if g <= 0:
        return None
    with K.at(c, cx, cy + 320, -3, g):
        box(c, 0, 0, 440, 200, "#FDE2E2", RED, 9, 30)
        K.text(c, "紧张", 0, -10, 110, "hand", RED)
    K.text(c, "最想说的", cx, cy + 480, 64, "hand", NIGHT, clamp01((T - tb(14, k_big)) / 0.3))
    return None


ev(j, k_big, big14, "kick", 0.85)
b.shots[j].shake = [(k_big, 7.0)]

# ================================================================ 屏 15：这样看梦——纸条飞回小李手里，镜子里是他自己
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k_li15 = 0
k_fly = nx(j, wt(19, 1, 0.3), k_li15)
k_you = nx(j, wt(19, 2, 0.4), k_fly)
GY15 = cy + 440
L.note("你自己")


def li15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_li15))
    if sc <= 0:
        return None
    x = cx - 200
    hy = GY15 - 290
    with at_pop(c, x, GY15, sc):
        C.line(c, (cx - 540, GY15), (cx + 540, GY15), BLACK, 6)
        draw_li(c, x, GY15, 1.0, "smile", rh=(x + 90, hy + 120))
        mx, my = cx + 250, GY15 - 330
        C.line(c, (mx, my + 140), (mx, GY15), "#A9773E", 10)
        c.drawOval(skia.Rect.MakeXYWH(mx - 120, my - 160, 240, 320), K.paint("#E6F2FA"))
        c.drawOval(skia.Rect.MakeXYWH(mx - 120, my - 160, 240, 320), wb.marker("#A9773E", 10))
        draw_li(c, mx, my + 160, 0.6, "smile")
    if T >= tb(15, k_fly):
        for i in range(4):
            f = ease_in_out(clamp01((T - tb(15, k_fly) - i * 0.1) / 0.6))
            sx, sy = cx - 420 + i * 260, cy - 420 + (i % 2) * 60
            ex, ey = x + 90, hy + 100 - i * 18
            with K.at(c, lerp(sx, ex, f), lerp(sy, ey, f), lerp((-10, 8, -6, 10)[i], 0, f), lerp(1.0, 0.45, f)):
                box(c, 0, 0, 220, 70, PAPER_W, NIGHT, 5, 6)
                C.line(c, (-80, 0), (60 - i * 10, 0), NIGHT, 6)
    return None


ev(j, k_li15, li15, "wood_low", 0.7)
b.hit(j, k_fly, "shaker", 0.7, "纸条飞回手里")


def you15(c, kk, T, cx=cx, cy=cy):
    g = C.slam_scale(T - tb(15, k_you))
    if g <= 0:
        return None
    with K.at(c, cx + 20, cy - 160, -4, g):
        K.text(c, "你自己", 0, 0, 130, "hand", L.ACC)
    c.drawPath(C.heart_path(cx + 330, cy - 280, 44), K.paint("#F6C3BE"))
    c.drawPath(C.heart_path(cx + 330, cy - 280, 44), wb.marker(RED, 6))
    sparkle(c, cx + 250, GY15 - 330, T - tb(15, k_you), YELLOW, 10, 150, 240)
    return None


ev(j, k_you, you15, "kick", 0.85)
b.shots[j].shake = [(k_you, 6.0)]

# ================================================================ 屏 16：评论区——“拆出来是怕周报”；提灯走出雾；下一讲预告
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
k_box = kq(j, wt(20, 0, 0.3), 0)
k_type = nx(j, wt(20, 0, 0.8), k_box)
k_likes = nx(j, wt(21, 1, 0.4), k_type)
k_lamp = nx(j, wt(22, 1, 0.3), k_likes)
k_n = nx(j, wt(23, 0, 0.1), k_lamp)
L.note("评论区", "拆出来是怕交周报", "发送", "+1", "不糊涂")


def input16(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(16, k_box))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(16, k_type):
            s_ = "拆出来是怕交周报"
            g = clamp01((T - tb(16, k_type)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], x - w / 2 + 40, y + 2, 56, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, L.ACC)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
        for i in range(6):
            g = pop_scale(T - tb(16, k_likes) - i * 0.15)
            if g > 0:
                with K.at(c, x - 330 + i * 120, y + 140, 0, g):
                    K.rr(c, 0, 0, 100, 60, 30, "#FDE2E2")
                    K.text(c, "+1", 0, 2, 40, "hand", L.ACC)
    return None


ev(j, k_box, input16, "wood_high", 0.7)
b.hit(j, k_type, "pop", 0.6, "打字")
b.hit(j, k_likes, "clap", 0.75, "好多人加一")


def lamp16(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(16, k_lamp))
    if sc <= 0:
        return None
    x, y = cx - 120, cy + 420
    f = ease_out(clamp01((T - tb(16, k_lamp)) / 0.8))
    hy = y - 290 * 0.9
    lx, ly = x + 130, hy + 120
    # 一圈灰色问号，被灯光照散
    for i in range(6):
        ang = i * math.pi / 3 + 0.4
        d = 260 + 200 * f
        a = 0.8 * (1 - f)
        if a > 0.02:
            K.text(c, "？", lx + math.cos(ang) * d, ly + math.sin(ang) * d * 0.7, 80, "hand", GRAY, a)
    with at_pop(c, x, y, sc):
        c.drawCircle(lx, ly, 120 + 120 * f, K.paint("#FFE39A", 0.35))
        draw_li(c, x, y, 0.9, "smile", rh=(lx - 20, ly - 70))
        C.line(c, (lx - 20, ly - 70), (lx, ly - 50), BLACK, 5)
        box(c, lx, ly, 70, 90, "#FFD27A", ORANGE, 6, 12)
        K.text(c, "不糊涂", x + 360, y - 300, 70, "hand", GREEN)
        for i in range(4):
            C.line(c, (x + 200 + i * 80, y), (x + 240 + i * 80, y), GRAY, 6)
    return None


ev(j, k_lamp, lamp16, "ding", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "一百多年过去，梦的解析还靠得住吗？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=5, square_shot=5, notes=NOTES)
L.export(globals())
