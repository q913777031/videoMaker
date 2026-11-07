"""《梦的解析》05 凝缩：梦里那个人，怎么像好几个人？（白板手绘 + AI 旁白，竖屏 2:3）

复刻实验：把梦里那个“拼起来的人”一块块拆开。
- 开场：领导的头、妈妈的围裙、高中校服裤依次拼成一个人，冒出问号，配音“这人是谁”逐字砸下；
- 痛点：梦里一个人，脸像领导、说话像妈；地方一半公司一半老家；
- 身边的例子（drop 在第 2 屏）：穿校服的同事在你家厨房开会；醒来三句话讲完，箱子里却塞满了事；
- 书中：好几样东西压成一张画；梦半页、想法好几页；植物学的书连着同事、妻子爱的花、小时候撕过的画册；
  三个人各出一块拼成一个人，连到同一件事；装的心思越多越容易进梦；
- 现在怎么看：睡觉时大脑把相像的记忆放在一块儿；
- 三步：拆开（脸、声音、衣服）、找共同点（都在拿我比）、写成一句话并看看感觉；乱线团理成一句话；评论区与下一讲。
文案与出处见 mengjie/PLAN.md「### 05」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, NOTE_FILL, PAPER_W, WOOD, at_pop, bed, box, draw_freud, dream_cloud, moon,
                         sleeper, sparkle, star)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross

BROWN = "#A9773E"
MOM_FILL, MOM_LINE = "#FFE39A", ORANGE
UNI_FILL, UNI_LINE = "#CFE0F5", BLUE


# ================================================================ 本讲小元件：拼起来的人（头 / 身子 / 腿各来自一个人）

def part_legs(c, x, y, s, uni=True):
    """腿：uni=True 画成高中校服裤（蓝裤 + 白条）。(x, y) 为脚底。"""
    for sg in (-1, 1):
        a, z = (x + sg * 14 * s, y - 115 * s), (x + sg * 48 * s, y)
        if uni:
            C.line(c, a, z, UNI_LINE, 26 * s)
            C.line(c, a, z, PAPER_W, 6 * s)
        else:
            C.line(c, a, z, BLACK, 10)


def part_body(c, x, y, s, kind="mom"):
    """身子：mom 为黄衣 + 白围裙；uni 为蓝白校服上衣；boss 为深色西装。"""
    hy = y - 290 * s
    sh = (x, hy + 75 * s)
    for sg in (-1, 1):
        C.line(c, sh, (x + sg * 75 * s, hy + 175 * s), BLACK, 9)
    if kind == "mom":
        p = P((x - 40 * s, hy + 50 * s), (x + 40 * s, hy + 50 * s), (x + 62 * s, y - 100 * s), (x - 62 * s, y - 100 * s), close=True)
        c.drawPath(p, K.paint(MOM_FILL))
        c.drawPath(p, wb.marker(MOM_LINE, 6))
        box(c, x, y - 150 * s, 66 * s, 86 * s, PAPER_W, GRAY, 4, 8)
    elif kind == "uni":
        p = P((x - 44 * s, hy + 50 * s), (x + 44 * s, hy + 50 * s), (x + 46 * s, y - 100 * s), (x - 46 * s, y - 100 * s), close=True)
        c.drawPath(p, K.paint(UNI_FILL))
        c.drawPath(p, wb.marker(UNI_LINE, 6))
        C.line(c, (x, hy + 52 * s), (x, y - 102 * s), PAPER_W, 6)
    else:
        p = P((x - 50 * s, hy + 55 * s), (x + 50 * s, hy + 55 * s), (x + 46 * s, y - 100 * s), (x - 46 * s, y - 100 * s), close=True)
        c.drawPath(p, K.paint("#3D4A63"))
        c.drawPath(P((x - 18 * s, hy + 55 * s), (x, hy + 110 * s), (x + 18 * s, hy + 55 * s), close=True), K.paint(PAPER_W))


def part_head(c, x, hy, s, kind="boss", mood="flat"):
    """头：boss 为背头；mom 为盘发；uni 为短发。hy 为头中心。"""
    if kind == "mom":
        c.drawCircle(x, hy - 50 * s, 24 * s, K.paint("#5A3A2A"))
        c.drawCircle(x, hy - 6 * s, 50 * s, K.paint("#5A3A2A"))
    c.drawCircle(x, hy, 45 * s, K.paint(PAPER_W))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 8))
    C._eyes_mouth(c, x, hy, s, mood, 1.0)
    if kind == "boss":
        hair = skia.Path()
        hair.addArc(skia.Rect.MakeXYWH(x - 48 * s, hy - 50 * s, 96 * s, 70 * s), 180, 180)
        hair.close()
        c.drawPath(hair, K.paint(BLACK))
        C.line(c, (x - 20 * s, hy - 30 * s), (x + 30 * s, hy - 42 * s), PAPER_W, 4)
    elif kind == "uni":
        c.drawPath(P((x - 45 * s, hy - 5 * s), (x - 30 * s, hy - 45 * s), (x + 30 * s, hy - 45 * s), (x + 50 * s, hy + 10 * s)),
                   wb.marker(BLACK, 9))


def person(c, x, y, s, head="boss", body="mom", legs=True, mood="flat"):
    """拼起来的人：(x, y) 为脚底。"""
    part_legs(c, x, y, s, legs)
    part_body(c, x, y, s, body)
    part_head(c, x, y - 290 * s, s, head, mood)


def mom(c, x, y, s, mood="smile"):
    person(c, x, y, s, "mom", "mom", False, mood)


def student(c, x, y, s, mood="smile"):
    person(c, x, y, s, "uni", "uni", True, mood)


def combo(c, x, y, s, mood="flat"):
    """领导的脸 + 妈妈的围裙 + 高中校服裤。"""
    person(c, x, y, s, "boss", "mom", True, mood)


def flower(c, x, y, s=1.0):
    with K.at(c, x, y, 0, s):
        C.line(c, (0, 10), (0, 90), GREEN, 7)
        for i in range(5):
            a = i * 2 * math.pi / 5 - math.pi / 2
            c.drawCircle(math.cos(a) * 26, math.sin(a) * 26, 20, K.paint("#E58FB1"))
            c.drawCircle(math.cos(a) * 26, math.sin(a) * 26, 20, wb.marker(RED, 4))
        c.drawCircle(0, 0, 14, K.paint("#FFE39A"))


def botany_book(c, x, y, s=1.0, rot=0.0):
    with K.at(c, x, y, rot, s):
        for sg in (-1, 1):
            pg = P((0, -90), (sg * 170, -110), (sg * 170, 90), (0, 110), close=True)
            c.drawPath(pg, K.paint(PAPER_W))
            c.drawPath(pg, wb.marker(BLACK, 6))
        flower(c, -85, -10, 0.7)
        for r in range(3):
            C.line(c, (30, -40 + r * 40), (140, -44 + r * 40), GRAY, 5)


def mini(c, x, y, i, s=1.0):
    """小图标：0 星星、1 杯子、2 房子、3 心。"""
    with K.at(c, x, y, 0, s):
        if i == 0:
            star(c, 0, 0, 50)
        elif i == 1:
            c.drawPath(P((-35, -45), (35, -45), (28, 45), (-28, 45), close=True), K.paint("#F1D9B5"))
            c.drawPath(P((-35, -45), (35, -45), (28, 45), (-28, 45), close=True), wb.marker(BROWN, 6))
        elif i == 2:
            c.drawPath(P((-50, -5), (0, -55), (50, -5), close=True), K.paint("#F6C3BE"))
            c.drawPath(P((-50, -5), (0, -55), (50, -5), close=True), wb.marker(RED, 5))
            c.drawRect(skia.Rect.MakeXYWH(-38, -5, 76, 55), K.paint(PAPER_W))
            c.drawRect(skia.Rect.MakeXYWH(-38, -5, 76, 55), wb.marker(BLACK, 5))
        else:
            c.drawPath(C.heart_path(0, 0, 45), K.paint("#F6C3BE"))
            c.drawPath(C.heart_path(0, 0, 45), wb.marker(RED, 6))


def tangle(c, x, y, w, h, alpha=1.0, n=9):
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    for i in range(n):
        a = i * 2.3
        p.quadTo(x + math.cos(a) * w * 0.55, y + math.sin(a * 1.3) * h * 0.55,
                 x + math.cos(a + 1.1) * w * 0.4, y + math.sin(a * 0.7 + 1) * h * 0.4)
    c.drawPath(p, wb.marker(GRAY, 6, alpha))


def _hook(H, j, cx, cy, acc):
    """开场：领导的头 → 妈妈的围裙 → 校服裤，拼成一个人并冒出问号；随后“这人是谁”逐字砸下。"""
    b = H.b
    H.note("？")
    X, Y, S = cx - 40, cy + 90, 1.25
    hy = Y - 290 * S

    def head(c, kk, T):
        dt = T - H.tb(j, 0)
        if dt < 0:
            return None
        f = ease_out(clamp01(dt / 0.3))
        part_head(c, X, lerp(hy - 260, hy, f), S, "boss")
        return None
    b.custom(j, 0, 0.3, head, sfx="wood_low", gain=0.7)

    def body(c, kk, T):
        dt = T - H.tb(j, 1)
        if dt < 0:
            return None
        f = ease_out(clamp01(dt / 0.3))
        with K.at(c, lerp(-420, 0, f), 0):
            part_body(c, X, Y, S, "mom")
        return None
    b.custom(j, 1, 1.3, body, sfx="tom", gain=0.75)

    def legs(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        f = ease_out(clamp01(dt / 0.3))
        with K.at(c, lerp(420, 0, f), 0):
            part_legs(c, X, Y, S, True)
        if dt > 0.3:
            with K.at(c, X + 230, hy - 60, 10, pop_scale(dt - 0.3)):
                K.text(c, "？", 0, 0, 180, "hand", RED)
        return None
    b.custom(j, 2, 2.3, legs, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("05", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第六章 A 节“凝缩作用”。",
    "书中例子：梦的内容简短、梦念长得多；植物学专著的梦连着同事、妻子喜爱的花、童年和妹妹撕彩色图册；集体人物与拼合人物。",
    "“睡眠中大脑整理、归并相近记忆”是今天的研究。小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：梦里一个人，脸像领导，声音像妈；地方一半公司一半老家
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_cl = nx(j, wt(0, 0, 0.6), 0)
k_face = nx(j, wt(0, 1, 0.4), k_cl)
k_voice = nx(j, wt(0, 2, 0.4), k_face)
k_place = nx(j, wt(1, 0, 0.5), k_voice)
k_where = nx(j, wt(1, 2, 0.4), k_place)
BED1 = (cx - 400, cy + 360)
HIP1 = (BED1[0] + 230, BED1[1] - 20)
CL1 = (cx + 60, cy - 220)
L.note("公司", "老家", "领导的脸", "妈的声音", "吃了没？", "哪儿？")


def scene1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, 0))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED1[1], sc):
        bed(c, *BED1, 560)
        sleeper(c, *HIP1, 0.8, T, None, "o")
    return None


ev(j, 0, scene1, "wood_low", 0.7)


def cloud1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_cl))
    if not dream_cloud(c, CL1[0], CL1[1], 1000, 660, sc, tail_to=(HIP1[0] - 300, HIP1[1] - 120)):
        return None
    with at_pop(c, CL1[0], CL1[1], sc):
        x0, y0 = CL1[0], CL1[1] + 220
        if T >= tb(1, k_place):
            g = clamp01((T - tb(1, k_place)) / 0.3)
            c.drawRect(skia.Rect.MakeXYWH(x0 - 400, y0 - 400, 400, 400), K.paint("#DCE6F2", g))
            c.drawRect(skia.Rect.MakeXYWH(x0, y0 - 400, 400, 400), K.paint("#F3E2B8", g))
            box(c, x0 - 300, y0 - 280, 130, 100, "#2E2A28", BLACK, 4, 6, g)
            K.text(c, "公司", x0 - 200, y0 - 360, 44, "hand", BLUE, g)
            c.drawRect(skia.Rect.MakeXYWH(x0 + 220, y0 - 320, 120, 120), wb.marker(BROWN, 6, g))
            C.line(c, (x0 + 280, y0 - 320), (x0 + 280, y0 - 200), BROWN, 5, g)
            K.text(c, "老家", x0 + 200, y0 - 360, 44, "hand", BROWN, g)
        combo(c, x0, y0, 0.95, "flat")
        if T >= tb(1, k_face):
            g = pop_scale(T - tb(1, k_face))
            with K.at(c, x0 - 250, y0 - 220, 0, g):
                box(c, 0, 0, 200, 64, PAPER_W, BLACK, 4, 30)
                K.text(c, "领导的脸", 0, 2, 38, "hand", BLACK)
            c.drawPath(wb.arrow((x0 - 150, y0 - 220), (x0 - 55, y0 - 270), 0.1, 18), wb.marker(BLACK, 4, clamp01(g)))
        if T >= tb(1, k_voice):
            g = pop_scale(T - tb(1, k_voice))
            with K.at(c, x0 + 230, y0 - 150, 0, g):
                c.drawRoundRect(skia.Rect.MakeXYWH(-120, -50, 240, 100), 40, 40, K.paint("#FFF4D6"))
                c.drawPath(wb.bubble(0, 0, 240, 100, -1), wb.marker(ORANGE, 5))
                K.text(c, "吃了没？", 0, 2, 44, "hand", ORANGE)
                K.text(c, "妈的声音", 0, 90, 34, "hand", ORANGE)
    return None


ev(j, k_cl, cloud1, "pop", 0.75)
b.hit(j, k_face, "pop", 0.7, "脸像领导")
b.hit(j, k_voice, "wood_high", 0.7, "声音像妈")
b.hit(j, k_place, "shaker", 0.65, "一半公司一半老家")
ev(j, k_where, L.pop_text("哪儿？", cx + 330, cy + 240, 90, RED, j, k_where), "rim", 0.8)

# ================================================================ 屏 2：drop——穿高中校服的同事，在你家厨房开会
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_kit = 1
k_stu = max(k_kit + 1, min(kq(j, wt(3, 0, 0.6), k_kit + 1), KD - 1))
CL2 = (cx, cy - 60)
L.note("开会", "高中校服")


def cloud2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_kit))
    if not dream_cloud(c, CL2[0], CL2[1], 1060, 860, sc):
        return None
    with at_pop(c, CL2[0], CL2[1], sc):
        gy = CL2[1] + 280
        fx = CL2[0] - 330
        box(c, fx, gy - 200, 180, 400, PAPER_W, GRAY, 6, 14)
        C.line(c, (fx - 90, gy - 260), (fx + 90, gy - 260), GRAY, 5)
        C.line(c, (fx + 60, gy - 360), (fx + 60, gy - 300), GRAY, 8)
        sx = CL2[0] + 330
        c.drawRect(skia.Rect.MakeXYWH(sx - 120, gy - 180, 240, 180), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(sx - 120, gy - 180, 240, 180), wb.marker(BROWN, 6))
        c.drawOval(skia.Rect.MakeXYWH(sx - 90, gy - 230, 140, 50), K.paint("#3A3F48"))
        C.line(c, (sx + 40, gy - 210), (sx + 110, gy - 240), "#3A3F48", 8)
        C.line(c, (CL2[0] - 480, gy), (CL2[0] + 480, gy), BROWN, 6)
        if T >= tb(2, k_stu):
            g = pop_scale(T - tb(2, k_stu))
            with at_pop(c, CL2[0], gy, g):
                student(c, CL2[0] - 110, gy, 0.75, "flat")
                student(c, CL2[0] + 110, gy, 0.75, "flat")
        if T >= tb(2, KD):
            g = C.slam_scale(T - tb(2, KD))
            with K.at(c, CL2[0], CL2[1] - 200, 0, g):
                box(c, 0, 0, 320, 180, PAPER_W, BLACK, 6, 8)
                for i, h in enumerate((60, 100, 80)):
                    c.drawRect(skia.Rect.MakeXYWH(-90 + i * 70, 60 - h, 44, h), K.paint((RED, BLUE, GREEN)[i]))
                C.line(c, (-110, 60), (110, 60), BLACK, 4)
    return None


ev(j, k_kit, cloud2, "pop", 0.75)
b.hit(j, k_stu, "wood_high", 0.75, "穿校服的同事")
ev(j, KD, L.slam_text("开会", cx + 300, cy - 400, 140, RED, j, KD, rot=-6), "kick", 0.95)
ev(j, max(k_stu, KD - 1), L.pop_text("高中校服", cx - 300, cy + 420, 60, BLUE, j, max(k_stu, KD - 1)), None)

# ================================================================ 屏 3：醒来三句话就讲完了，可感觉装了好多事
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_talk = kq(j, wt(4, 0, 0.4), 0)
k_three = nx(j, wt(4, 1, 0.5), k_talk)
k_bag = nx(j, wt(4, 2, 0.5), k_three)
GY3 = cy + 440
L.note("一", "二", "三", "好多事")


def talk3(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, GY3, sc):
        draw_li(c, cx - 330, GY3, 0.9, "smile", rh=(cx - 230, GY3 - 300))
        draw_li(c, cx - 30, GY3, 0.9, "flat")
    return None


ev(j, k_talk, pop_fn(j, k_talk, talk3), "wood_low", 0.7)


def three3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_three))
    if sc <= 0:
        return None
    x, y = cx - 220, cy - 320
    with K.at(c, x, y, 0, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(-250, -150, 500, 300), 50, 50, K.paint(PAPER_W))
        c.drawPath(wb.bubble(0, 0, 500, 300, -1), wb.marker(BLACK, 7))
        for i, s_ in enumerate(("一", "二", "三")):
            K.text(c, s_, -160, -80 + i * 80, 48, "hand", RED)
            C.line(c, (-110, -80 + i * 80), (150 - i * 40, -80 + i * 80), GRAY, 8)
    return None


ev(j, k_three, three3, "pop", 0.75)


def bag3(c, kk, T, cx=cx, cy=cy):
    t0 = tb(3, k_bag)
    if T < t0:
        return None
    x, y = cx + 330, cy + 300
    with K.at(c, x, y, 0, pop_scale(T - t0)):
        for i in range(6):
            dt = T - t0 - 0.15 - i * 0.07
            if dt < 0:
                continue
            f = ease_out(clamp01(dt / 0.35))
            ang = -math.pi / 2 + (i - 2.5) * 0.4
            mini(c, math.cos(ang) * 260 * f, -60 + math.sin(ang) * 260 * f, i % 4, 0.8)
        box(c, 0, 40, 340, 260, "#C9A87A", BROWN, 8, 18)
        C.line(c, (-170, -20), (170, -20), BROWN, 6)
        box(c, 0, -110, 120, 40, "#C9A87A", BROWN, 6, 14)
    K.text(c, "好多事", x, y + 230, 70, "hand", RED, clamp01((T - t0 - 0.4) / 0.2))
    return None


ev(j, k_bag, bag3, "clap", 0.85)
b.shots[j].shake = [(k_bag, 6.0)]

# ================================================================ 屏 4：凝缩——好几样东西压成一张画；梦半页，想法好几页
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_items = kq(j, wt(5, 0, 0.6), 0)
k_press = nx(j, wt(5, 1, 0.4), k_items)
k_half = nx(j, wt(6, 1, 0.5), k_press)
k_pages = nx(j, wt(6, 3, 0.4), k_half)
PX, PY = cx - 180, cy - 160
L.note("凝缩", "梦", "想法", "半页", "好几页")


def press4(c, kk, T, cx=cx, cy=cy):
    t0 = tb(4, k_items)
    if T < t0:
        return None
    pr = ease_in_out(clamp01((T - tb(4, k_press)) / 0.35)) if T >= tb(4, k_press) else 0.0
    for i in range(4):
        g = pop_scale(T - t0 - i * 0.08)
        if g <= 0:
            continue
        ox, oy = (-240, -120, 120, 240)[i], (-200, -250, -250, -200)[i]
        x, y = lerp(PX + ox, PX + (i - 1.5) * 60, pr), lerp(PY + oy, PY + 80, pr)
        mini(c, x, y, i, g * (1 - pr * 0.45))
    py = lerp(PY - 470, PY + 20, pr)
    c.drawRect(skia.Rect.MakeXYWH(PX - 200, py - 60, 400, 60), K.paint(GRAY))
    c.drawRect(skia.Rect.MakeXYWH(PX - 200, py - 60, 400, 60), wb.marker(BLACK, 6))
    C.line(c, (PX, py - 60), (PX, PY - 560), BLACK, 14)
    if pr > 0:
        box(c, PX, PY + 80, 320, 120, PAPER_W, NIGHT, 6, 10, pr)
        for i in range(4):
            mini(c, PX + (i - 1.5) * 60, PY + 80, i, 0.5 * pr)
    return None


ev(j, k_items, press4, "wood_low", 0.7)
ev(j, k_press, L.stamp("凝缩", cx + 300, cy - 300, 100, j, k_press, color=L.ACC, rot=-6), "kick", 0.9)
b.shots[j].shake = [(k_press, 7.0)]


def pages4(c, kk, T, cx=cx, cy=cy):
    t0 = tb(4, k_half)
    if T < t0:
        return None
    y = cy + 360
    with K.at(c, cx - 260, y, -4, pop_scale(T - t0)):
        box(c, 0, 0, 200, 140, PAPER_W, BLACK, 5, 4)
        for r in range(2):
            C.line(c, (-70, -20 + r * 40), (70, -20 + r * 40), GRAY, 5)
        K.text(c, "梦 · 半页", 0, 110, 46, "hand", NIGHT)
    if T >= tb(4, k_pages):
        for i in range(7):
            g = pop_scale(T - tb(4, k_pages) - i * 0.06)
            if g > 0:
                with K.at(c, cx + 250 + (i % 2) * 10, y + 60 - i * 34, (i % 3 - 1) * 3, g):
                    box(c, 0, 0, 260, 30, PAPER_W, BLACK, 4, 3)
        K.text(c, "想法 · 好几页", cx + 250, y + 140, 46, "hand", RED, clamp01((T - tb(4, k_pages)) / 0.3))
    return None


L.note("梦 · 半页", "想法 · 好几页")
ev(j, k_half, pages4, "pop", 0.7)
b.hit(j, k_pages, "shaker", 0.75, "好几页")

# ================================================================ 屏 5：植物学的书连着同事、妻子爱的花、小时候撕过的画册
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_book = kq(j, wt(7, 0, 0.5), 0)
k_l1 = nx(j, wt(7, 1, 0.4), k_book)
k_l2 = nx(j, wt(7, 2, 0.4), k_l1)
k_l3 = nx(j, wt(7, 4, 0.5), k_l2)
BK = (cx + 40, cy - 60)
NODES = [(cx - 300, cy - 400), (cx + 340, cy - 380), (cx + 300, cy + 330)]
L.note("同事", "妻子爱的花", "小时候")


def book5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_book))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy, sc):
        draw_freud(c, cx - 360, cy + 460, 0.85, "smile")
    if dream_cloud(c, BK[0], BK[1], 460, 340, sc, tail_to=(cx - 360, cy + 180)):
        with at_pop(c, BK[0], BK[1], sc):
            botany_book(c, BK[0], BK[1], 0.95, -4)
    return None


ev(j, k_book, book5, "wood_low", 0.7)


def links5(c, kk, T, cx=cx, cy=cy):
    for i, k in enumerate((k_l1, k_l2, k_l3)):
        t0 = tb(5, k)
        if T < t0:
            continue
        f = ease_out(clamp01((T - t0) / 0.35))
        nxp, nyp = NODES[i]
        a = (BK[0] + (nxp - BK[0]) * 0.42, BK[1] + (nyp - BK[1]) * 0.42)
        z = (lerp(a[0], nxp, f * 0.75), lerp(a[1], nyp, f * 0.75))
        c.drawPath(P(a, z), wb.marker(RED, 6))
        g = pop_scale(T - t0 - 0.2)
        if g <= 0:
            continue
        x, y = nxp, nyp
        with K.at(c, x, y, 0, g):
            c.drawCircle(0, 0, 130, K.paint(PAPER_W))
            c.drawCircle(0, 0, 130, wb.marker(RED, 7))
            if i == 0:
                draw_li(c, 0, 100, 0.55, "smile", bag=True)
                K.text(c, "同事", 0, 170, 46, "hand", BLACK)
            elif i == 1:
                flower(c, 0, -30, 1.3)
                K.text(c, "妻子爱的花", 0, 170, 46, "hand", BLACK)
            else:
                with K.at(c, -30, 0, -10):
                    box(c, 0, 0, 120, 150, "#CFE0F5", BLUE, 5, 4)
                    star(c, 0, -10, 30)
                with K.at(c, 50, 10, 14):
                    box(c, 0, 0, 80, 150, "#F6C3BE", RED, 5, 4)
                c.drawPath(P((20, -75), (34, -40), (14, -10), (30, 30), (16, 75)), wb.marker(BLACK, 5))
                K.text(c, "小时候", 0, 170, 46, "hand", BLACK)
    return None


ev(j, k_l1, links5, "pop", 0.75)
b.hit(j, k_l2, "pop", 0.75, "妻子爱的花")
b.hit(j, k_l3, "ding", 0.8, "小时候撕过的画册")

# ================================================================ 屏 6：一个人身上拼着好几个人；共同点：同一件事；多看一眼
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_src = kq(j, wt(8, 0, 0.6), 0)
k_fly = nx(j, wt(8, 1, 0.5), k_src)
k_same = nx(j, wt(9, 1, 0.5), k_fly)
k_look = nx(j, wt(10, 1, 0.5), k_same)
SRC = [(cx - 380, cy - 160), (cx, cy - 210), (cx + 380, cy - 160)]
GY6 = cy + 470
L.note("领导", "妈", "同学", "同一件事")


def src6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_src)
    if T < t0:
        return None
    fly = ease_in_out(clamp01((T - tb(6, k_fly)) / 0.6)) if T >= tb(6, k_fly) else 0.0
    for i, (x, y) in enumerate(SRC):
        g = pop_scale(T - t0 - i * 0.1)
        if g <= 0:
            continue
        with at_pop(c, x, y, g):
            s = 0.6
            if i == 0:
                draw_boss(c, x, y, s, alpha=1 - fly * 0.6)
            elif i == 1:
                mom(c, x, y, s)
            else:
                student(c, x, y, s)
            K.text(c, ("领导", "妈", "同学")[i], x, y + 50, 44, "hand", GRAY)
    if fly > 0:
        s = 1.0
        X = cx
        hy = GY6 - 290 * s
        a_ = clamp01(fly * 3)
        hx, hyy = lerp(SRC[0][0], X, fly), lerp(SRC[0][1] - 290 * 0.6, hy, fly)
        with K.at(c, lerp(SRC[2][0], X, fly) - X, lerp(SRC[2][1], GY6, fly) - GY6):
            part_legs(c, X, GY6, s, True)
        with K.at(c, lerp(SRC[1][0], X, fly) - X, lerp(SRC[1][1], GY6, fly) - GY6):
            part_body(c, X, GY6, s, "mom")
        part_head(c, hx, hyy, s, "boss", "flat")
    return None


ev(j, k_src, src6, "wood_low", 0.7)
b.hit(j, k_fly, "tom", 0.8, "拼成一个人")


def same6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_same)
    if T < t0:
        return None
    x, y = cx + 360, cy + 240
    with K.at(c, x, y, 3, pop_scale(T - t0)):
        box(c, 0, 0, 300, 120, NOTE_FILL, ORANGE, 6, 10)
        K.text(c, "同一件事", 0, 2, 56, "hand", RED)
    a = clamp01((T - t0) / 0.3)
    for (sx, sy) in SRC:
        c.drawPath(P((sx + 40, sy + 70), (x - 60, y - 60)), wb.marker(ORANGE, 4, a * 0.8))
    return None


ev(j, k_same, same6, "ding", 0.8)


def look6(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k_look)
    if dt < 0:
        return None
    with K.at(c, cx - 300, cy + 240, 0, pop_scale(dt)):
        C.line(c, (90, 90), (170, 170), BROWN, 20)
        c.drawCircle(0, 0, 120, K.paint("#FFFFFF", 0.3))
        c.drawCircle(0, 0, 120, wb.marker(BLACK, 9))
        for sg in (-1, 1):
            c.drawCircle(sg * 30, 0, 12, K.paint(BLACK))
    K.text(c, "多看一眼", cx - 300, cy + 420, 56, "hand", L.ACC, clamp01(dt / 0.25))
    return None


L.note("多看一眼")
ev(j, k_look, look6, "pop", 0.75)

# ================================================================ 屏 7：为什么要压？装下越多心思的画面，越容易被选进梦里
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_q7 = kq(j, wt(11, 0, 0.3), 0)
k_one = nx(j, wt(11, 1, 0.3), k_q7)
k_many = nx(j, wt(11, 1, 0.8), k_one)
k_pick = nx(j, wt(11, 2, 0.5), k_many)
L.note("为什么要压？", "选进梦里")


def q7(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(7, k_q7))
    if sc <= 0:
        return None
    with K.at(c, cx, cy - 450, -2, sc):
        box(c, 0, 0, 700, 160, PAPER_W, NIGHT, 8, 30)
        K.text(c, "为什么要压？", 0, 4, 90, "hand", NIGHT)
    return None


ev(j, k_q7, q7, "kick", 0.8)


def cards7(c, kk, T, cx=cx, cy=cy):
    for idx, k in enumerate((k_one, k_many)):
        g = pop_scale(T - tb(7, k))
        if g <= 0:
            continue
        x, y = cx - 280, cy - 140 + idx * 340
        with K.at(c, x, y, (-3, 3)[idx], g):
            box(c, 0, 0, 340, 240, PAPER_W, BLACK, 6, 8)
            if idx == 0:
                mini(c, 0, 0, 1, 1.2)
            else:
                for i in range(4):
                    mini(c, -90 + (i % 2) * 180, -55 + (i // 2) * 110, i, 0.8)
    if T >= tb(7, k_pick):
        f = ease_out(clamp01((T - tb(7, k_pick)) / 0.4))
        a, z = (cx - 90, cy + 200), (cx + 160, cy + 60)
        c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), 0.2, 34), wb.marker(GREEN, 8))
        with K.at(c, cx - 280, cy + 200, 0, pop_scale(T - tb(7, k_pick) - 0.2)):
            c.drawPath(check(150, -110, 50), wb.marker(GREEN, 12))
    return None


ev(j, k_one, cards7, "pop", 0.7)
b.hit(j, k_many, "pop", 0.75, "装了好多心思的画面")


def door7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_one))
    x, y = cx + 340, cy + 40
    if not dream_cloud(c, x, y, 380, 420, sc):
        return None
    with at_pop(c, x, y, sc):
        K.text(c, "选进梦里", x, y - 110, 50, "hand", NIGHT)
        if T >= tb(7, k_pick):
            g = pop_scale(T - tb(7, k_pick) - 0.3)
            with K.at(c, x, y + 40, 0, g * 0.45):
                box(c, 0, 0, 340, 240, PAPER_W, BLACK, 6, 8)
                for i in range(4):
                    mini(c, -90 + (i % 2) * 180, -55 + (i // 2) * 110, i, 0.8)
    return None


ev(j, k_one, door7, None)
b.hit(j, k_pick, "ding", 0.8, "被选进梦里")

# ================================================================ 屏 8：现在的研究：睡觉时大脑把相像的记忆放在一块儿
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_br = kq(j, wt(12, 0, 0.5), 0)
k_mem = nx(j, wt(12, 1, 0.5), k_br)
k_sort = nx(j, wt(12, 2, 0.5), k_mem)
L.note("研究", "放在一块儿")
MEM = [(1, -380, 60), (3, -150, 260), (1, 120, 120), (0, 360, 300), (3, 300, -40), (0, -300, 330)]


def br8(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 330, sc):
        A.brain(c, cx - 120, cy - 330, 130)
        K.text(c, "研究", cx + 230, cy - 380, 60, "hand", BLUE)
        moon(c, cx + 300, cy - 260, 50)
        for i in range(3):
            K.text(c, "Z", cx + 140 + i * 50, cy - 230 - i * 40, 40 + i * 8, "hand", NIGHT)
    return None


L.note("Z")
ev(j, k_br, pop_fn(j, k_br, br8), "wood_low", 0.7)


def mem8(c, kk, T, cx=cx, cy=cy):
    t0 = tb(8, k_mem)
    if T < t0:
        return None
    srt = ease_in_out(clamp01((T - tb(8, k_sort)) / 0.6)) if T >= tb(8, k_sort) else 0.0
    count = {0: 0, 1: 0, 3: 0}
    if srt > 0:
        for kind, gx in ((1, -330), (3, 0), (0, 330)):
            box(c, cx + gx, cy + 300, 260, 200, "#F3E2B8", BROWN, 6, 12, srt)
    for i, (kind, dx, dy) in enumerate(MEM):
        g = pop_scale(T - t0 - i * 0.07)
        if g <= 0:
            continue
        gx = {1: -330, 3: 0, 0: 330}[kind]
        n = count[kind]
        count[kind] += 1
        tx, ty = cx + gx + (n - 0.5) * 90, cy + 280
        x, y = lerp(cx + dx, tx, srt), lerp(cy + dy - 100, ty, srt)
        with K.at(c, x, y, (i % 3 - 1) * 8 * (1 - srt), g):
            box(c, 0, 0, 120, 120, PAPER_W, GRAY, 4, 8)
            mini(c, 0, 0, kind, 0.8)
    if srt >= 1:
        K.text(c, "放在一块儿", cx, cy + 470, 64, "hand", RED)
    return None


ev(j, k_mem, mem8, "pop", 0.75)
b.hit(j, k_sort, "shaker", 0.75, "相像的归到一块儿")

# ================================================================ 屏 9：下次梦见拼起来的人，别慌 → 三步
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_li9 = kq(j, wt(13, 0, 0.5), 0)
k_calm = nx(j, wt(13, 1, 0.5), k_li9)
k_3 = nx(j, wt(13, 2, 0.5), k_calm)
GY9 = cy + 420
L.note("别慌", "三步")


def li9(c, sc, T, cx=cx, cy=cy):
    x = cx - 280
    with at_pop(c, x, GY9, sc):
        C.line(c, (x - 260, GY9), (x + 260, GY9), BLACK, 7)
        draw_li(c, x, GY9, 0.9, "smile" if T >= tb(9, k_calm) else "o")
        dream_cloud(c, x - 20, cy - 280, 380, 400, 1.0, tail_to=(x, GY9 - 300))
        combo(c, x - 20, cy - 120, 0.55)
    return None


ev(j, k_li9, pop_fn(j, k_li9, li9), "wood_low", 0.7)
ev(j, k_calm, L.pop_bubble("别慌", cx + 40, cy + 40, j, k_calm, 64, GREEN, tail=-1), "pop", 0.75)


def three9(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(9, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 300, cy - 260, -4, sc):
        c.drawCircle(0, 0, 190, K.paint("#FFF4D6"))
        c.drawCircle(0, 0, 190, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 130, "hand", L.ACC)
    return None


ev(j, k_3, three9, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 10：第一，把他拆开：脸像谁，声音像谁，衣服像谁
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_h10 = kq(j, wt(14, 0, 0.3), 0)
k_split = [nx(j, wt(14, 1, 0.5), k_h10)]
k_split.append(nx(j, wt(14, 2, 0.5), k_split[0]))
k_split.append(nx(j, wt(14, 3, 0.5), k_split[1]))
GY10 = cy + 420
L.note("第一", "把他拆开", "脸 → 领导", "声音 → 妈", "衣服 → 同学")
LABELS = ["脸 → 领导", "声音 → 妈", "衣服 → 同学"]


def h10(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第一", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "把他拆开", cx - 110, cy - 500, 56, "hand", BLACK)
    return None


ev(j, k_h10, pop_fn(j, k_h10, h10), "wood_low", 0.6)


def split10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_h10))
    if sc <= 0:
        return None
    s = 1.3
    X = cx - 250
    hy = GY10 - 290 * s
    off = [ease_out(clamp01((T - tb(10, k)) / 0.35)) if T >= tb(10, k) else 0.0 for k in k_split]
    with at_pop(c, X, GY10, sc):
        with K.at(c, -60 * off[2], 40 * off[2]):
            part_legs(c, X, GY10, s, True)
        with K.at(c, -60 * off[1], 0):
            part_body(c, X, GY10, s, "mom")
        part_head(c, X - 60 * off[0], hy - 60 * off[0], s, "boss")
    ys = [hy - 60, hy + 160, GY10 - 80]
    for i in range(3):
        if off[i] <= 0:
            continue
        g = pop_scale(T - tb(10, k_split[i]))
        c.drawPath(P((X + 80, ys[i]), (cx + 30, ys[i])), wb.marker(GRAY, 5, clamp01(g)))
        with K.at(c, cx + 250, ys[i], 0, g):
            box(c, 0, 0, 420, 110, PAPER_W, (RED, ORANGE, BLUE)[i], 6, 16)
            K.text(c, LABELS[i], 0, 2, 54, "hand", (RED, ORANGE, BLUE)[i])
    return None


ev(j, k_h10, split10, None)
for i, k_ in enumerate(k_split):
    b.hit(j, k_, "pop", 0.75, LABELS[i])

# ================================================================ 屏 11：第二，找共同点：这几个人最近都跟哪件事沾边
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_h11 = kq(j, wt(15, 0, 0.3), 0)
k_three11 = nx(j, wt(15, 1, 0.5), k_h11)
k_link = nx(j, wt(15, 2, 0.3), k_three11)
k_ans = nx(j, wt(15, 2, 0.85), k_link)
L.note("第二", "找共同点", "都在拿我比")
FR11 = [(cx - 360, cy - 190), (cx, cy - 220), (cx + 360, cy - 190)]


def h11(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第二", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "找共同点", cx - 110, cy - 500, 56, "hand", BLACK)
    return None


ev(j, k_h11, pop_fn(j, k_h11, h11), "wood_low", 0.6)


def three11(c, kk, T, cx=cx, cy=cy):
    for i, (x, y) in enumerate(FR11):
        g = pop_scale(T - tb(11, k_three11) - i * 0.12)
        if g <= 0:
            continue
        with K.at(c, x, y, (-4, 2, 5)[i], g):
            box(c, 0, 0, 260, 300, PAPER_W, BLACK, 7, 8)
            if i == 0:
                draw_boss(c, 0, 130, 0.75)
            elif i == 1:
                mom(c, 0, 130, 0.75)
            else:
                student(c, 0, 130, 0.75)
    if T >= tb(11, k_link):
        f = ease_out(clamp01((T - tb(11, k_link)) / 0.4))
        z = (cx, cy + 260)
        for (x, y) in FR11:
            a = (x, y + 160)
            c.drawPath(P(a, (lerp(a[0], z[0], f), lerp(a[1], z[1] - 90, f))), wb.marker(ORANGE, 6))
    if T >= tb(11, k_ans):
        g = pop_scale(T - tb(11, k_ans))
        with K.at(c, cx, cy + 300, -2, g):
            box(c, 0, 0, 520, 160, NOTE_FILL, ORANGE, 7, 12)
            K.text(c, "都在拿我比", 0, 4, 76, "hand", RED)
    return None


ev(j, k_three11, three11, "wood_high", 0.7)
b.hit(j, k_link, "pop", 0.7, "连到一起")
b.hit(j, k_ans, "ding", 0.85, "共同点")

# ================================================================ 屏 12：第三，把那件事写成一句话，看看你对它的感觉
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_h12 = kq(j, wt(16, 0, 0.3), 0)
k_wr = nx(j, wt(16, 1, 0.3), k_h12)
k_faces = nx(j, wt(16, 2, 0.5), k_wr)
k_pick = nx(j, wt(16, 3, 0.4), k_faces)
L.note("第三", "写成一句话", "我怕被比下去", "怕", "烦", "还好")
FACES = [("怕", "o"), ("烦", "sad"), ("还好", "smile")]


def h12(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第三", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "写成一句话", cx - 80, cy - 500, 56, "hand", BLACK)
    return None


ev(j, k_h12, pop_fn(j, k_h12, h12), "wood_low", 0.6)


def note12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_wr))
    if sc <= 0:
        return None
    with K.at(c, cx, cy - 190, -2, sc):
        box(c, 0, 0, 820, 260, NOTE_FILL, ORANGE, 7, 10)
        s_ = "我怕被比下去"
        g = clamp01((T - tb(12, k_wr)) / 0.8)
        n = max(1, int(math.ceil(len(s_) * g)))
        K.text(c, s_[:n], -330, 4, 90, "hand", RED, 1.0, "left")
    return None


ev(j, k_wr, note12, "shaker", 0.7)


def faces12(c, kk, T, cx=cx, cy=cy):
    for i, (w, mood) in enumerate(FACES):
        g = pop_scale(T - tb(12, k_faces) - i * 0.12)
        if g <= 0:
            continue
        x, y = cx - 330 + i * 330, cy + 220
        with K.at(c, x, y, 0, g):
            c.drawCircle(0, 0, 110, K.paint(PAPER_W))
            c.drawCircle(0, 0, 110, wb.marker(BLACK, 8))
            C._eyes_mouth(c, 0, 0, 2.2, mood, 1.0)
            K.text(c, w, 0, 170, 56, "hand", BLACK)
    if T >= tb(12, k_pick):
        g = pop_scale(T - tb(12, k_pick))
        with K.at(c, cx - 330, cy + 260, 0, g):
            c.drawOval(skia.Rect.MakeXYWH(-160, -180, 320, 380), wb.marker(RED, 9))
    return None


ev(j, k_faces, faces12, "pop", 0.7)
b.hit(j, k_pick, "ding", 0.8, "圈出感觉")

# ================================================================ 屏 13：拆开以后，乱糟糟的梦成了一句清楚的话
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_mess = 0
k_untie = nx(j, wt(17, 1, 0.6), k_mess)
k_clear = nx(j, wt(17, 3, 0.4), k_untie)
L.note("我怕被比下去")


def mess13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_mess))
    if sc <= 0:
        return None
    m = ease_in_out(clamp01((T - tb(13, k_untie)) / 0.6)) if T >= tb(13, k_untie) else 0.0
    x, y = cx, cy - 160
    if m < 1:
        dream_cloud(c, x, y, 800 * (1 - 0.4 * m), 600 * (1 - 0.4 * m), sc, alpha=1 - m)
        with K.at(c, x, y, m * 90, 1 - 0.5 * m):
            tangle(c, 0, 0, 520, 360, 1 - m)
            combo(c, -160, 140, 0.5)
            mini(c, 180, -60, 2, 0.8)
            mini(c, 150, 120, 1, 0.8)
    if m > 0:
        C.line(c, (cx - 380 * m, cy - 160), (cx + 380 * m, cy - 160), GRAY, 6, m)
    if T >= tb(13, k_clear):
        g = pop_scale(T - tb(13, k_clear))
        with K.at(c, cx, cy - 20, -2, g):
            box(c, 0, 0, 760, 200, NOTE_FILL, ORANGE, 7, 10)
            K.text(c, "我怕被比下去", 0, 4, 84, "hand", RED)
    return None


ev(j, k_mess, mess13, "pop", 0.7)
b.hit(j, k_untie, "shaker", 0.75, "线团理开")
b.hit(j, k_clear, "ding", 0.85, "一句清楚的话")


def li13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_clear) - 0.5)
    if sc <= 0:
        return None
    x, y = cx + 300, cy + 470
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.75, "smile", rh=(x - 90, y - 290 * 0.75 + 80))
    return None


b.custom(j, k_clear, k_clear + 0.3, li13)

# ================================================================ 屏 14：评论区——“领导穿着我妈的围裙”；哈哈；一件一件拆；下一讲预告
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_box = kq(j, wt(18, 0, 0.4), 0)
k_type = nx(j, wt(19, 0, 0.5), k_box)
k_ha = nx(j, wt(19, 1, 0.5), k_type)
k_unpack = nx(j, wt(20, 2, 0.3), k_ha)
k_n = nx(j, wt(21, 0, 0.1), k_unpack)
L.note("评论区", "领导系着我妈的围裙", "发送", "哈哈")


def input14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_box))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(14, k_type):
            s_ = "领导系着我妈的围裙"
            g = clamp01((T - tb(14, k_type)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], x - w / 2 + 40, y + 2, 54, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, L.ACC)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
        for i in range(5):
            g = pop_scale(T - tb(14, k_ha) - i * 0.15)
            if g > 0:
                with K.at(c, x - 320 + i * 160, y + 140, 0, g):
                    K.rr(c, 0, 0, 140, 64, 30, "#FFF4D6")
                    K.text(c, "哈哈", 0, 2, 40, "hand", L.ACC)
    return None


ev(j, k_box, input14, "wood_high", 0.7)
b.hit(j, k_type, "pop", 0.6, "打字")
b.hit(j, k_ha, "clap", 0.75, "大家乐一乐")


def unpack14(c, kk, T, cx=cx, cy=cy):
    t0 = tb(14, k_unpack)
    if T < t0:
        return None
    x, y = cx - 340, cy + 320
    with at_pop(c, x, y, pop_scale(T - t0)):
        draw_li(c, x, y + 120, 0.75, "smile", rh=(x + 90, y - 40))
        box(c, x + 160, y + 50, 180, 140, "#C9A87A", BROWN, 7, 12)
    for i in range(4):
        dt = T - t0 - 0.2 - i * 0.18
        if dt < 0:
            continue
        f = ease_out(clamp01(dt / 0.35))
        tx = cx - 20 + i * 160
        with K.at(c, lerp(x + 160, tx, f), lerp(y - 20, y + 60, f), 0, 0.9):
            mini(c, 0, 0, i, 1.0)
        if f >= 1:
            c.drawPath(check(tx, y + 170, 30), wb.marker(GREEN, 8))
    K.text(c, "一件一件拆", cx + 220, cy + 160, 60, "hand", GREEN, clamp01((T - t0 - 0.9) / 0.3))
    return None


L.note("一件一件拆")
ev(j, k_unpack, unpack14, "ding", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "梦里的重点，为什么总跑偏？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=5, notes=NOTES)
L.export(globals())
