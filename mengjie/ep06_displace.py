"""《梦的解析》06 移置：梦里的重点，为什么总跑偏？（白板手绘 + AI 旁白，竖屏 2:3）

两人对比（看画面 vs 看情绪）：同一个梦，只看画面会盯住最大的东西；看情绪才找得到心里分量重的那件事。
- 开场：房子着火、一只大袜子砸下、红箭头从房子拐到袜子，配音“重点跑偏了”；
- 痛点：小李睡着，梦泡泡里房子着火，他却趴着找袜子；醒来袜子被圈上“最揪心”；
- 身边的例子（drop 在第 2 屏）：明天答辩 → 梦里一只大鞋、鞋带系不上；吵了一架 → 梦里只剩一杯打翻的水；
- 书中：“移置”卡片，分量砝码从“要紧的事”挪到小袜子；聚光灯下的大袜子最轻，要紧的躲在角落；
  弗洛伊德自己的梦，画面里最清楚的是一本书，往下追连着事业和得失；看门的拦下烫手的心思，换成袜子放过去；分量重排；
- 所以看情绪：大画面打叉，情绪表指向“着急”；现在怎么看：书的读法 vs 研究看梦里情绪跟白天对不对得上；
- 三步：找情绪（三格梦里圈出最着急的一格）、小事放一边找“这种着急”、往前挪一步（再练一遍、发个消息）；
  袜子领路到“要紧的事”；评论区与下一讲。
文案与出处见 mengjie/PLAN.md「### 06」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, draw_worker, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, NOTE_FILL, PAPER_W, WOOD, at_pop, bed, box, draw_freud, dream_cloud, moon,
                         sleeper, sparkle, sun)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross

SOCK_FILL = "#F6C3BE"


def sock(c, x, y, s=1.0, rot=0.0, alpha=1.0, fill=SOCK_FILL, line=RED):
    """一只袜子：(x, y) 约为中心，脚尖朝右。"""
    with K.at(c, x, y, rot, s):
        p = skia.Path()
        p.moveTo(-70, -120)
        p.lineTo(10, -120)
        p.lineTo(10, 10)
        p.quadTo(90, 0, 110, 50)
        p.quadTo(120, 110, 50, 110)
        p.lineTo(-30, 110)
        p.quadTo(-80, 100, -70, 40)
        p.close()
        c.drawPath(p, K.paint(fill, alpha))
        c.drawPath(p, wb.marker(line, 7, alpha))
        for yy in (-95, -70):
            C.line(c, (-70, yy), (10, yy), line, 6, alpha)


def flame(c, x, y, h, T, ph=0.0, alpha=1.0):
    w = h * (0.42 + 0.06 * math.sin(T * 9 + ph))
    tip = x + h * 0.12 * math.sin(T * 7 + ph)
    p = skia.Path()
    p.moveTo(tip, y - h)
    p.quadTo(x + w, y - h * 0.35, x + w * 0.7, y - h * 0.05)
    p.quadTo(x, y + h * 0.12, x - w * 0.7, y - h * 0.05)
    p.quadTo(x - w, y - h * 0.35, tip, y - h)
    c.drawPath(p, K.paint("#FFB347", alpha))
    c.drawPath(p, wb.marker(RED, 5, alpha))


def house(c, x, y, s, T, fire=True, alpha=1.0):
    """房子：(x, y) 为地面中点；fire=True 时屋顶冒火。"""
    with K.at(c, x, y, 0, s):
        box(c, 0, -90, 240, 180, PAPER_W, BLACK, 7, 6, alpha)
        roof = P((-150, -180), (0, -300), (150, -180), close=True)
        c.drawPath(roof, K.paint("#F6C3BE", alpha))
        c.drawPath(roof, wb.marker(BLACK, 7, alpha))
        box(c, -50, -60, 60, 120, WOOD, "#A9773E", 5, 4, alpha)
        box(c, 55, -110, 70, 60, "#CFE0F5", BLUE, 5, 4, alpha)
        if fire:
            for i, (dx, dy, h) in enumerate(((-70, -200, 110), (10, -270, 150), (90, -190, 100))):
                flame(c, dx, dy, h, T, i * 1.7, alpha)


def shoe(c, x, y, s=1.0, T=0.0, loose=True, alpha=1.0):
    """一只运动鞋，(x, y) 为鞋底中点；loose=True 时鞋带散着晃。"""
    with K.at(c, x, y, 0, s):
        p = skia.Path()
        p.moveTo(-150, 0)
        p.lineTo(-150, -110)
        p.quadTo(-120, -140, -60, -130)
        p.lineTo(20, -70)
        p.quadTo(150, -60, 160, -10)
        p.lineTo(160, 0)
        p.close()
        c.drawPath(p, K.paint("#CFE0F5", alpha))
        c.drawPath(p, wb.marker(BLUE, 7, alpha))
        C.line(c, (-160, 0), (170, 0), BLACK, 12, alpha)
        for i in range(3):
            C.line(c, (-70 + i * 30, -115 + i * 18), (-30 + i * 30, -100 + i * 18), BLACK, 5, alpha)
        if loose:
            sw = 18 * math.sin(T * 6)
            c.drawPath(P((-20, -85), (-50 + sw * 0.5, -40), (-70 + sw, -10)), wb.marker(RED, 6, alpha))
            c.drawPath(P((-20, -85), (10 - sw * 0.5, -40), (0 - sw, -10)), wb.marker(RED, 6, alpha))


def cup(c, x, y, tip, s=1.0, alpha=1.0):
    """水杯：tip 0→1 从立着到倒下，倒下后流出一摊水。(x, y) 为桌面上杯底中点。"""
    if tip > 0.3:
        f = clamp01((tip - 0.3) / 0.7)
        r = skia.Rect.MakeXYWH(x - (120 + 220 * f) * s, y - 22 * s, (100 + 240 * f) * s, 44 * s)
        c.drawOval(r, K.paint("#BFDDF7", alpha))
        c.drawOval(r, wb.marker(BLUE, 5, alpha))
    with K.at(c, x, y - 58 * s * tip, -90 * tip, s):
        p = P((-50, 0), (-62, -150), (62, -150), (50, 0), close=True)
        c.drawPath(p, K.paint("#E9F3FB", alpha))
        c.drawPath(p, wb.marker(BLACK, 6, alpha))
        if tip < 0.5:
            c.drawRect(skia.Rect.MakeXYWH(-56, -100, 112, 96), K.paint("#BFDDF7", alpha))


def weight(c, x, y, s=1.0, label="分量", alpha=1.0):
    """砝码：(x, y) 为中心。"""
    with K.at(c, x, y, 0, s):
        c.drawCircle(0, -95, 26, wb.marker(BLACK, 8, alpha))
        p = P((-80, -70), (80, -70), (110, 70), (-110, 70), close=True)
        c.drawPath(p, K.paint("#3A3F48", alpha))
        c.drawPath(p, wb.marker(BLACK, 6, alpha))
        K.text(c, label, 0, 4, 54, "hand", PAPER_W, alpha)


def heart(c, x, y, r, fill="#F6C3BE", line=RED, alpha=1.0):
    c.drawPath(C.heart_path(x, y, r), K.paint(fill, alpha))
    c.drawPath(C.heart_path(x, y, r), wb.marker(line, 6, alpha))


def _hook(H, j, cx, cy, acc):
    """开场：房子着火 → 一只大袜子砸下 → 红箭头从房子拐到袜子；随后“重点跑偏了”逐字砸下。"""
    b = H.b

    def hs(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc > 0:
            with at_pop(c, cx - 300, cy + 40, sc):
                house(c, cx - 300, cy + 40, 0.95, T)
        return None
    b.custom(j, 0, 0.3, hs, sfx="wood_low", gain=0.7)

    def sk(c, kk, T):
        sc = C.slam_scale(T - H.tb(j, 1))
        if sc > 0:
            sock(c, cx + 300, cy - 150, 1.25 * sc, 10)
        return None
    b.custom(j, 1, 1.3, sk, sfx="tom", gain=0.8)

    def ar(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        f = ease_out(clamp01(dt / 0.35))
        a, z = (cx - 160, cy - 340), (cx + 190, cy - 330)
        c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), -0.35, 40), wb.marker(RED, 10))
        sparkle(c, cx + 300, cy - 150, dt, YELLOW, 10, 170, 250)
        return None
    b.custom(j, 2, 2.3, ar, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("06", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第六章 B“移置作用”。",
    "书中观点：精神强度的移置，梦里最显眼的元素不一定在梦念里最重要；梦对一切心理价值重新估价。",
    "书中例子：弗洛伊德自己的“植物学专著”之梦，画面最清楚的是一本专著，联想下去连着他的事业与得失。",
    "现在的研究更多看梦中情绪与白天生活的连续性；片中交代为弗洛伊德的读法。小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：梦里房子着火，小李只顾找袜子；醒来最揪心的是袜子
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_bed = 0
k_cl = nx(j, wt(0, 0, 0.6), k_bed)
k_sk = nx(j, wt(0, 2, 0.4), k_cl)
k_wake = nx(j, wt(1, 0, 0.3), k_sk)
k_ring = nx(j, wt(1, 2, 0.3), k_wake)
BED1 = (cx - 380, cy + 330)
HIP1 = (BED1[0] + 230, BED1[1] - 20)
CL1 = (cx + 60, cy - 250)
L.note("最揪心")


def scene1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_bed))
    if sc <= 0:
        return None
    woke = T >= tb(1, k_wake)
    with at_pop(c, cx, BED1[1], sc):
        bed(c, *BED1, 560)
        sleeper(c, *HIP1, 0.8, T, tb(1, k_wake), "sad" if woke else "flat")
    return None


ev(j, k_bed, scene1, "wood_low", 0.7)


def cloud1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_cl))
    if not dream_cloud(c, CL1[0], CL1[1], 900, 560, sc, tail_to=(HIP1[0] - 260, HIP1[1] - 100)):
        return None
    with at_pop(c, CL1[0], CL1[1], sc):
        house(c, CL1[0] - 260, CL1[1] + 30, 0.55, T)
        if T >= tb(1, k_sk):
            g = pop_scale(T - tb(1, k_sk))
            x, y = CL1[0] + 70, CL1[1] + 170
            with K.at(c, x, y, -12, g):
                draw_li(c, 0, 0, 0.5, "flat", lh=(-70, -60), rh=(-40, -40))
            with K.at(c, CL1[0] + 250, CL1[1] - 20, 0, g):
                sock(c, 0, 0, 0.75, 14)
    return None


ev(j, k_cl, cloud1, "pop", 0.75)
b.hit(j, k_sk, "tom", 0.75, "只顾着找袜子")
b.hit(j, k_wake, "kick", 0.85, "醒来")
b.shots[j].shake = [(k_wake, 8.0)]


def ring1(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(1, k_ring)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.4))
    x, y = CL1[0] + 250, CL1[1] - 20
    K.ring(c, x, y, 140, RED, 9, 1.0, f)
    g = pop_scale(dt - 0.15)
    if g > 0:
        with K.at(c, x + 30, y - 220, -4, g):
            box(c, 0, 0, 240, 90, PAPER_W, RED, 6, 30)
            K.text(c, "最揪心", 0, 2, 54, "hand", RED)
    return None


ev(j, k_ring, ring1, "rim", 0.8)

# ================================================================ 屏 2：明天答辩 → drop：梦里一只大鞋，鞋带系不上
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_cal = 1
k_cl2 = max(k_cal + 1, KD - 3)
GY2 = cy + 440
CL2 = (cx + 160, cy - 230)
L.note("明天", "答辩", "鞋带")


def li2(c, sc, T, cx=cx, cy=cy):
    x = cx - 330
    with at_pop(c, x, GY2, sc):
        draw_li(c, x, GY2, 0.85, "sad", lh=(x - 110, GY2 - 300))
        with K.at(c, x - 110, cy - 420, -4):
            box(c, 0, 0, 230, 210, PAPER_W, BLACK, 6, 12)
            c.drawRect(skia.Rect.MakeXYWH(-115, -105, 230, 70), K.paint(RED))
            K.text(c, "明天", 0, -70, 46, "hand", PAPER_W)
            K.text(c, "答辩", 0, 30, 70, "hand", BLACK)
    return None


ev(j, k_cal, pop_fn(j, k_cal, li2), "wood_low", 0.7)


def cloud2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_cl2))
    if not dream_cloud(c, CL2[0], CL2[1], 760, 560, sc, tail_to=(cx - 330, GY2 - 330)):
        return None
    with at_pop(c, CL2[0], CL2[1], sc):
        x, y = CL2[0] - 170, CL2[1] + 170
        draw_li(c, x, y, 0.55, "sad", lh=(x + 60, y - 40), rh=(x + 90, y - 30))
        g = C.slam_scale(T - tb(2, KD))
        if g > 0:
            with K.at(c, CL2[0] + 110, CL2[1] + 100, 0, g):
                shoe(c, 0, 0, 1.15, T)
    return None


ev(j, k_cl2, cloud2, "pop", 0.7)
ev(j, KD, L.slam_text("着急", cx + 200, cy + 230, 140, RED, j, KD, rot=-6), "kick", 0.95)

# ================================================================ 屏 3：吵了一架 → 梦里吵架没了，只剩一杯打翻的水
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_q = kq(j, wt(4, 0, 0.5), 0)
k_cl3 = nx(j, wt(4, 1, 0.3), k_q)
k_tip = nx(j, wt(4, 2, 0.5), k_cl3)
GY3 = cy + 440
CL3 = (cx + 170, cy - 240)
L.note("哼", "吵架")


def fight3(c, sc, T, cx=cx, cy=cy):
    x = cx - 330
    with at_pop(c, x, GY3, sc):
        draw_li(c, x - 120, GY3, 0.75, "sad", rh=(x - 20, GY3 - 210))
        draw_worker(c, x + 140, GY3, 0.75, lh=(x + 40, GY3 - 200), mood="sad")
        for i in range(3):
            ph = math.sin(T * 12 + i)
            c.drawPath(P((x - 30, GY3 - 330 - i * 40), (x + 10, GY3 - 345 - i * 40 + 6 * ph), (x - 10, GY3 - 360 - i * 40),
                         (x + 30, GY3 - 375 - i * 40)), wb.marker(RED, 6))
        K.text(c, "吵架", x, GY3 + 70, 54, "hand", RED)
    return None


ev(j, k_q, pop_fn(j, k_q, fight3), "wood_low", 0.7)
ev(j, k_q, L.pop_bubble("哼", cx - 520, cy - 60, j, k_q, 60, RED, tail=1), None)


def cloud3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_cl3))
    if not dream_cloud(c, CL3[0], CL3[1], 700, 520, sc, tail_to=(cx - 330, GY3 - 380)):
        return None
    with at_pop(c, CL3[0], CL3[1], sc):
        x, y = CL3[0] + 40, CL3[1] + 120
        C.line(c, (x - 260, y), (x + 260, y), "#A9773E", 10)
        tip = ease_out(clamp01((T - tb(3, k_tip)) / 0.35)) if T >= tb(3, k_tip) else 0.0
        cup(c, x + 120, y - 6, tip, 1.3)
    return None


ev(j, k_cl3, cloud3, "pop", 0.7)
b.hit(j, k_tip, "tom", 0.8, "杯子打翻")


def drops3(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(3, k_tip) - 0.3
    if dt < 0:
        return None
    for i in range(3):
        f = (dt * 0.9 + i / 3) % 1
        x, y = CL3[0] - 160 - i * 50, CL3[1] + 100 + f * 30
        c.drawCircle(x, y - 40 * (1 - f), 10, K.paint("#BFDDF7", 1 - f))
    return None


b.custom(j, k_tip, k_tip + 0.3, drops3)

# ================================================================ 屏 4：“移置”——分量从要紧的事挪到不起眼的小事
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_card = kq(j, wt(5, 0, 0.35), 0)
k_big = nx(j, wt(5, 1, 0.3), k_card)
k_mv = nx(j, wt(5, 2, 0.5), k_big)
L.note("移置", "要紧的事", "小事", "分量")


def card4(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(4, k_card))
    if sc <= 0:
        return None
    with K.at(c, cx, cy - 420, -2, sc):
        box(c, 0, 0, 460, 180, PAPER_W, L.ACC, 9, 30)
        K.text(c, "移置", 0, 4, 120, "hand", L.ACC)
    return None


ev(j, k_card, card4, "kick", 0.85)
b.shots[j].shake = [(k_card, 7.0)]


def pair4(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy + 250, sc):
        box(c, cx - 290, cy + 260, 340, 260, "#E4E2F6", NIGHT, 7, 14)
        K.text(c, "要紧的事", cx - 290, cy + 450, 60, "hand", NIGHT)
        K.text(c, "？", cx - 290, cy + 260, 120, "hand", NIGHT)
        sock(c, cx + 300, cy + 280, 0.7, 10)
        K.text(c, "小事", cx + 300, cy + 450, 60, "hand", RED)
    return None


ev(j, k_big, pop_fn(j, k_big, pair4), "wood_low", 0.7)


def mv4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_big))
    if sc <= 0:
        return None
    f = ease_in_out(clamp01((T - tb(4, k_mv)) / 0.6)) if T >= tb(4, k_mv) else 0.0
    x = lerp(cx - 290, cx + 300, f)
    y = cy - 70 - 120 * math.sin(math.pi * f)
    if f > 0:
        a, z = (cx - 220, cy - 60), (cx + 230, cy - 60)
        c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), z[1]), 0.0, 36), wb.marker(GRAY, 6, 0.6))
    weight(c, x, y + 0, 0.9 * sc)
    return None


b.custom(j, k_big, k_big + 0.3, mv4)
b.hit(j, k_mv, "ding", 0.8, "分量挪到小事上")

# ================================================================ 屏 5：最显眼的在心里最轻；要紧的躲在角落
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_spot = kq(j, wt(6, 1, 0.3), 0)
k_light = nx(j, wt(6, 2, 0.3), k_spot)
k_corner = nx(j, wt(6, 3, 0.2), k_light)
L.note("最显眼", "轻", "要紧")


def spot5(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy, sc):
        cone = P((cx - 40, cy - 520), (cx + 40, cy - 520), (cx + 300, cy + 180), (cx - 300, cy + 180), close=True)
        c.drawPath(cone, K.paint("#FFF1A8", 0.75))
        c.drawPath(cone, wb.marker(YELLOW, 5))
        c.drawOval(skia.Rect.MakeXYWH(cx - 300, cy + 130, 600, 100), K.paint("#FFE39A"))
        sock(c, cx, cy - 40, 1.55, 8)
        K.text(c, "最显眼", cx - 340, cy - 330, 64, "hand", ORANGE)
    return None


ev(j, k_spot, pop_fn(j, k_spot, spot5), "wood_low", 0.7)


def light5(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(5, k_light)
    if dt < 0:
        return None
    x, y = cx + 360, cy - 230
    sw = 10 * math.sin(T * 3)
    with K.at(c, x, y + sw, 20 + sw, pop_scale(dt)):
        p = skia.Path()
        p.moveTo(0, -90)
        p.quadTo(60, -20, 0, 90)
        p.quadTo(-60, -20, 0, -90)
        c.drawPath(p, K.paint(PAPER_W))
        c.drawPath(p, wb.marker(GRAY, 6))
        C.line(c, (0, -70), (0, 110), GRAY, 4)
    with at_pop(c, x + 60, y + 170, pop_scale(dt)):
        K.text(c, "轻", x + 60, y + 170, 80, "hand", BLUE)
    return None


ev(j, k_light, light5, "pop", 0.7)


def corner5(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(5, k_corner)
    if dt < 0:
        return None
    x, y = cx - 430, cy + 380
    with at_pop(c, x, y, pop_scale(dt)):
        box(c, x, y, 200, 200, "#3A3F48", BLACK, 6, 8)
        C.line(c, (x - 100, y - 40), (x + 100, y - 40), BLACK, 4)
        heart(c, x, y + 30, 50, "#E5484D", RED)
        K.text(c, "要紧", x, y - 160, 60, "hand", RED)
    sparkle(c, x, y, dt, YELLOW, 8, 120, 190)
    return None


ev(j, k_corner, corner5, "ding", 0.8)

# ================================================================ 屏 6：弗洛伊德自己的梦——最清楚的是一本书；往下追，连着事业和得失
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_fr = kq(j, wt(7, 0, 0.2), 0)
k_book = nx(j, wt(7, 1, 0.4), k_fr)
k_dig = nx(j, wt(8, 0, 0.4), k_book)
k_ends = nx(j, wt(8, 1, 0.5), k_dig)
CL6 = (cx + 170, cy - 300)
L.note("一本书", "事业", "得失")


def fr6(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 360, cy + 260
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 0.95, "flat")
    return None


ev(j, k_fr, pop_fn(j, k_fr, fr6), "wood_low", 0.7)


def book6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_book))
    if not dream_cloud(c, CL6[0], CL6[1], 680, 440, sc, tail_to=(cx - 360, cy - 50)):
        return None
    with at_pop(c, CL6[0], CL6[1], sc):
        with K.at(c, CL6[0], CL6[1] + 10, -6):
            box(c, 0, 0, 340, 220, "#D3EDDC", GREEN, 7, 10)
            C.line(c, (0, -110), (0, 110), GREEN, 6)
            for sg in (-1, 1):
                for r in range(3):
                    C.line(c, (sg * 30, -50 + r * 40), (sg * 130, -50 + r * 40), GREEN, 4)
            K.text(c, "一本书", 0, -150, 56, "hand", GREEN)
    return None


ev(j, k_book, book6, "pop", 0.75)


def dig6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_dig)
    if T < t0:
        return None
    x0, y0 = CL6[0], CL6[1] + 220
    f = ease_out(clamp01((T - t0) / 0.8))
    yb = y0 + 400 * f
    c.drawPath(P((x0, y0), (x0 - 40, y0 + 130 * f), (x0 + 30, y0 + 260 * f), (x0, yb)), wb.marker(NIGHT, 7))
    for i in range(3):
        yy = y0 + 70 + i * 120
        if yy < yb:
            C.line(c, (x0 - 200, yy + 30), (x0 + 200, yy + 30), GRAY, 4, 0.6)
    return None


ev(j, k_dig, dig6, "shaker", 0.7)


def ends6(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k_ends)
    if dt < 0:
        return None
    for i, (s_, col) in enumerate((("事业", NIGHT), ("得失", RED))):
        g = pop_scale(dt - i * 0.15)
        if g <= 0:
            continue
        x, y = CL6[0] - 150 + i * 300, cy + 390
        with K.at(c, x, y, (-1) ** i * 3, g):
            box(c, 0, 0, 240, 130, "#FFF4D6", col, 8, 14)
            K.text(c, s_, 0, 4, 70, "hand", col)
    return None


ev(j, k_ends, ends6, "ding", 0.8)

# ================================================================ 屏 7：看门的拦下烫手的心思，换成袜子放过去；分量重排
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_gate = kq(j, wt(9, 0, 0.45), 0)
k_hot = nx(j, wt(9, 0, 0.8), k_gate)
k_pass = nx(j, wt(9, 2, 0.3), k_hot)
k_re = nx(j, wt(10, 2, 0.3), k_pass)
GY7 = cy + 300
L.note("烫手", "重新排")


def gate7(c, sc, T, cx=cx, cy=cy):
    x = cx + 60
    with at_pop(c, x, GY7, sc):
        for gx in (x - 120, x + 120):
            box(c, gx, GY7 - 180, 50, 360, WOOD, "#A9773E", 6, 6)
        c.drawRect(skia.Rect.MakeXYWH(x - 140, GY7 - 300, 280, 30), K.paint(RED))
        draw_worker(c, x + 240, GY7, 0.75, lh=(x + 170, GY7 - 230))
    return None


ev(j, k_gate, pop_fn(j, k_gate, gate7), "wood_low", 0.7)


def hot7(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(7, k_hot)
    if dt < 0:
        return None
    x, y = cx - 330, GY7 - 120
    passed = T >= tb(7, k_pass)
    a = 1.0 - (0.65 if passed else 0.0)
    with K.at(c, x, y, 0, pop_scale(dt)):
        box(c, 0, 0, 180, 150, "#E5484D", RED, 7, 14, a)
        for i in range(3):
            ph = (T * 0.9 + i / 3) % 1
            c.drawPath(P((-50 + i * 50, -90 - ph * 20), (-35 + i * 50, -130 - ph * 40), (-55 + i * 50, -170 - ph * 50)),
                       wb.marker(ORANGE, 6, (1 - ph) * a))
        K.text(c, "烫手", 0, 120, 60, "hand", RED, a)
    if dt > 0.15:
        g = pop_scale(dt - 0.15)
        with K.at(c, x + 160, y - 20, 0, g):
            c.drawPath(cross(0, 0, 50), wb.marker(RED, 12))
    return None


ev(j, k_hot, hot7, "rim", 0.8)


def pass7(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(7, k_pass)
    if dt < 0:
        return None
    f = ease_in_out(clamp01(dt / 0.7))
    x = lerp(cx - 330, cx + 60, f)
    sock(c, x, GY7 - 100, 0.6 * pop_scale(dt), 10)
    if f >= 1:
        g = pop_scale(dt - 0.7)
        with K.at(c, cx + 60, GY7 - 400, 0, g):
            c.drawPath(check(0, 0, 50), wb.marker(GREEN, 12))
    return None


ev(j, k_pass, pass7, "shaker", 0.7)


def re7(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(7, k_re)
    if dt < 0:
        return None
    x, y = cx, cy - 420
    with K.at(c, x, y, -2, pop_scale(dt)):
        box(c, 0, 0, 520, 150, NOTE_FILL, ORANGE, 7, 12)
        K.text(c, "重新排", 0, 4, 80, "hand", ORANGE)
        f = ease_in_out(clamp01((dt - 0.2) / 0.5))
        for sg in (-1, 1):
            c.drawPath(wb.arrow((sg * 330, -50), (sg * 330, 50) if f > 0 else (sg * 330, -49), 0.0, 24),
                       wb.marker(ORANGE, 6, f))
    return None


ev(j, k_re, re7, "ding", 0.8)

# ================================================================ 屏 8：看梦——别盯最大的画面，看情绪落在哪
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_cl8 = kq(j, wt(11, 0, 0.3), 0)
k_x8 = nx(j, wt(11, 1, 0.6), k_cl8)
k_hr8 = nx(j, wt(11, 2, 0.6), k_x8)
CL8 = (cx, cy - 240)
L.note("着急", "情绪")


def cloud8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_cl8))
    if not dream_cloud(c, CL8[0], CL8[1], 860, 520, sc):
        return None
    with at_pop(c, CL8[0], CL8[1], sc):
        house(c, CL8[0] - 110, CL8[1] + 190, 0.95, T)
        sock(c, CL8[0] + 290, CL8[1] + 120, 0.45, 10)
    return None


ev(j, k_cl8, cloud8, "pop", 0.7)


def x8(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k_x8)
    if dt < 0:
        return None
    with K.at(c, CL8[0] - 110, CL8[1], 0, C.slam_scale(dt)):
        c.drawPath(cross(0, 0, 120), wb.marker(RED, 14, 0.85))
    return None


ev(j, k_x8, x8, "rim", 0.8)


def heart8(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k_hr8)
    if dt < 0:
        return None
    x, y = cx - 120, cy + 300
    with at_pop(c, x, y, pop_scale(dt)):
        heart(c, x, y, 120, "#E5484D", RED)
        K.text(c, "情绪", x, y + 190, 60, "hand", RED)
        box(c, x + 380, y - 20, 220, 100, PAPER_W, RED, 6, 30)
        K.text(c, "着急", x + 380, y - 18, 60, "hand", RED)
    f = ease_out(clamp01((dt - 0.2) / 0.4))
    a, z = (CL8[0] + 290, CL8[1] + 220), (x + 380, y - 90)
    c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), 0.15, 30), wb.marker(NIGHT, 7, f))
    return None


ev(j, k_hr8, heart8, "ding", 0.8)

# ================================================================ 屏 9：现在怎么看——书的读法 vs 研究看情绪跟白天对不对得上
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_bk9 = kq(j, wt(12, 1, 0.3), 0)
k_lab9 = nx(j, wt(12, 2, 0.4), k_bk9)
k_eq9 = nx(j, wt(12, 3, 0.4), k_lab9)
L.note("梦的", "解析", "他的读法", "研究", "梦里", "白天", "对得上？")


def bk9(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 290, cy - 300, sc):
        box(c, cx - 290, cy - 320, 240, 300, NIGHT, BLACK, 6, 10)
        K.text(c, "梦的", cx - 290, cy - 360, 50, "serif_black", "#FFE39A")
        K.text(c, "解析", cx - 290, cy - 300, 50, "serif_black", "#FFE39A")
        K.text(c, "他的读法", cx - 290, cy - 110, 54, "hand", NIGHT)
    return None


ev(j, k_bk9, pop_fn(j, k_bk9, bk9), "wood_low", 0.7)


def lab9(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 280, cy - 320
    with at_pop(c, x, y, sc):
        A.brain(c, x, y, 110)
        K.text(c, "研究", x, y + 170, 54, "hand", BLUE)
    return None


ev(j, k_lab9, pop_fn(j, k_lab9, lab9), "wood_high", 0.7)


def eq9(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(9, k_eq9)
    if dt < 0:
        return None
    y = cy + 260
    with at_pop(c, cx, y, pop_scale(dt)):
        dream_cloud(c, cx - 290, y, 300, 220, 1.0)
        heart(c, cx - 290, y + 10, 50, "#E5484D", RED)
        K.text(c, "梦里", cx - 290, y - 170, 52, "hand", NIGHT)
        sun(c, cx + 290, y, 70)
        K.text(c, "白天", cx + 290, y - 170, 52, "hand", ORANGE)
        f = ease_out(clamp01((dt - 0.15) / 0.4))
        c.drawPath(wb.arrow((cx - 110, y), (lerp(cx - 110, cx + 180, f), y), 0.0, 30), wb.marker(BLACK, 7))
        c.drawPath(wb.arrow((cx + 180, y + 40), (lerp(cx + 180, cx - 110, f), y + 40), 0.0, 30), wb.marker(BLACK, 7))
        K.text(c, "对得上？", cx, y + 200, 66, "hand", L.ACC)
    return None


ev(j, k_eq9, eq9, "ding", 0.8)

# ================================================================ 屏 10：说回我们自己——梦里为小事着急；“三步”
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_li10 = kq(j, wt(13, 0, 0.5), 0)
k_3 = nx(j, wt(13, 1, 0.5), k_li10)
GY10 = cy + 420


def li10(c, sc, T, cx=cx, cy=cy):
    x = cx - 240
    with at_pop(c, x, GY10, sc):
        C.line(c, (x - 300, GY10), (x + 300, GY10), BLACK, 7)
        draw_li(c, x, GY10, 0.9, "sad")
        dream_cloud(c, x - 60, cy - 280, 340, 220, 1.0, tail_to=(x, GY10 - 300))
        sock(c, x - 60, cy - 280, 0.55, 10)
        for sg in (-1, 1):
            A._sweat(c, x + sg * 80, GY10 - 300, 1.2)
    return None


ev(j, k_li10, pop_fn(j, k_li10, li10), "wood_low", 0.7)


def three10(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(10, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 270, cy - 80, -4, sc):
        c.drawCircle(0, 0, 190, K.paint("#FFF4D6"))
        c.drawCircle(0, 0, 190, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 130, "hand", L.ACC)
    return None


L.note("三步")
ev(j, k_3, three10, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 11：第一，找情绪——三格梦里圈出最着急的一下
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_h11 = kq(j, wt(14, 0, 0.5), 0)
k_fr11 = [nx(j, wt(14, 1, 0.15), k_h11)]
k_fr11 += [cap(j, k_fr11[0] + 1), cap(j, k_fr11[0] + 2)]
k_ring11 = nx(j, wt(14, 1, 0.75), k_fr11[2])
L.note("第一", "找情绪", "最着急")


def h11(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 480, sc):
        K.text(c, "第一", cx - 330, cy - 480, 76, "hand", L.ACC)
        K.text(c, "找情绪", cx + 40, cy - 480, 66, "hand", BLACK)
    return None


ev(j, k_h11, pop_fn(j, k_h11, h11), "wood_low", 0.7)


def frames11(c, kk, T, cx=cx, cy=cy):
    for i in range(3):
        g = pop_scale(T - tb(11, k_fr11[i]))
        if g <= 0:
            continue
        x, y = cx - 360 + i * 360, cy - 40
        with K.at(c, x, y, (-3, 2, -2)[i], g):
            box(c, 0, 0, 300, 320, PAPER_W, BLACK, 7, 12)
            if i == 0:
                house(c, 0, 110, 0.6, T)
            elif i == 1:
                draw_li(c, -30, 130, 0.5, "sad", lh=(-80, 20), rh=(-50, 40))
                sock(c, 80, 30, 0.35, 10)
            else:
                cup(c, 0, 100, 1.0, 0.7)
    return None


ev(j, k_fr11[0], frames11, "pop", 0.65)
b.hit(j, k_fr11[1], "pop", 0.65, "第二格")
b.hit(j, k_fr11[2], "pop", 0.65, "第三格")


def ring11(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(11, k_ring11)
    if dt < 0:
        return None
    K.ring(c, cx, cy - 40, 230, RED, 10, 1.0, ease_out(clamp01(dt / 0.4)))
    g = pop_scale(dt - 0.2)
    if g > 0:
        with K.at(c, cx, cy + 300, -3, g):
            heart(c, -180, 0, 60, "#E5484D", RED)
            K.text(c, "最着急", 60, 4, 80, "hand", RED)
    return None


ev(j, k_ring11, ring11, "ding", 0.8)

# ================================================================ 屏 12：第二，小事放一边——这种着急最近在哪出现过
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_h12 = kq(j, wt(15, 0, 0.5), 0)
k_aside = nx(j, wt(15, 1, 0.5), k_h12)
k_feel = nx(j, wt(15, 2, 0.5), k_aside)
k_where = nx(j, wt(15, 3, 0.4), k_feel)
L.note("第二", "放一边", "这种着急", "最近", "答辩")


def h12(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 480, sc):
        K.text(c, "第二", cx - 330, cy - 480, 76, "hand", L.ACC)
        K.text(c, "放一边", cx + 40, cy - 480, 66, "hand", BLACK)
    return None


ev(j, k_h12, pop_fn(j, k_h12, h12), "wood_low", 0.7)


def sock12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_h12))
    if sc <= 0:
        return None
    f = ease_in_out(clamp01((T - tb(12, k_aside)) / 0.5)) if T >= tb(12, k_aside) else 0.0
    x, y = lerp(cx, cx - 400, f), lerp(cy - 200, cy + 380, f)
    sock(c, x, y, lerp(1.1, 0.55, f) * sc, lerp(0, 40, f), lerp(1.0, 0.45, f))
    return None


b.custom(j, k_h12, k_h12 + 0.3, sock12)
b.hit(j, k_aside, "shaker", 0.7, "袜子放一边")


def feel12(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(12, k_feel)
    if dt < 0:
        return None
    x, y = cx + 30, cy - 160
    with at_pop(c, x, y, pop_scale(dt)):
        heart(c, x - 200, y, 70, "#E5484D", RED)
        K.text(c, "这种着急", x + 90, y + 4, 70, "hand", RED)
    return None


ev(j, k_feel, feel12, "pop", 0.7)


def where12(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(12, k_where)
    if dt < 0:
        return None
    x, y = cx + 220, cy + 260
    f = ease_out(clamp01(dt / 0.4))
    a, z = (cx + 40, cy - 60), (x - 20, y - 150)
    c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), -0.2, 30), wb.marker(NIGHT, 7))
    with K.at(c, x, y, 4, pop_scale(dt - 0.15)):
        box(c, 0, 0, 320, 260, PAPER_W, BLACK, 7, 12)
        c.drawRect(skia.Rect.MakeXYWH(-160, -130, 320, 80), K.paint(RED))
        K.text(c, "最近", 0, -88, 50, "hand", PAPER_W)
        K.text(c, "答辩", 0, 40, 86, "hand", BLACK)
    return None


ev(j, k_where, where12, "ding", 0.8)

# ================================================================ 屏 13：第三，往前挪一步——再练一遍、先发个消息
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_h13 = kq(j, wt(16, 1, 0.3), 0)
k_pr = nx(j, wt(16, 2, 0.6), k_h13)
k_msg = nx(j, wt(16, 3, 0.4), k_pr)
GY13 = cy + 420
L.note("第三", "往前挪一步", "再练一遍", "上次是我急了")


def h13(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 480, sc):
        K.text(c, "第三", cx - 330, cy - 480, 76, "hand", L.ACC)
        K.text(c, "往前挪一步", cx + 80, cy - 480, 66, "hand", BLACK)
        for i in range(3):
            c.drawOval(skia.Rect.MakeXYWH(cx - 200 + i * 150, cy - 370 - (i % 2) * 30, 60, 34), K.paint(GRAY, 0.6))
    return None


ev(j, k_h13, pop_fn(j, k_h13, h13), "wood_low", 0.7)


def pr13(c, sc, T, cx=cx, cy=cy):
    x = cx - 300
    with at_pop(c, x, GY13, sc):
        box(c, x + 40, GY13 - 470, 300, 190, "#2E2A28", BLACK, 6, 10)
        K.text(c, "答辩", x + 40, GY13 - 470, 60, "hand", PAPER_W)
        draw_li(c, x, GY13, 0.8, "smile", rh=(x + 100, GY13 - 330))
        K.text(c, "再练一遍", x, GY13 + 70, 58, "hand", GREEN)
    return None


ev(j, k_pr, pop_fn(j, k_pr, pr13), "pop", 0.7)


def msg13(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 300, cy + 150
    with at_pop(c, x, y, sc):
        box(c, x, y, 260, 440, "#2E2A28", BLACK, 6, 28)
        box(c, x, y - 10, 228, 360, "#CFE0F5", BLUE, 4, 12)
        box(c, x + 10, y - 60, 200, 130, PAPER_W, GREEN, 5, 18)
        K.text(c, "上次是", x + 10, y - 85, 44, "hand", BLACK)
        K.text(c, "我急了", x + 10, y - 35, 44, "hand", BLACK)
        c.drawPath(check(x + 60, y + 80, 30), wb.marker(GREEN, 8))
    return None


L.note("上次是", "我急了")
ev(j, k_msg, pop_fn(j, k_msg, msg13), "ding", 0.8)

# ================================================================ 屏 14：这样看梦——袜子领路，把你领到要紧的事上
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_s14 = kq(j, wt(17, 1, 0.3), 0)
k_path14 = nx(j, wt(17, 2, 0.2), k_s14)
k_goal14 = nx(j, wt(17, 2, 0.8), k_path14)
L.note("要紧的事")
PATH14 = [(cx - 340, cy - 260), (cx - 120, cy - 60), (cx - 300, cy + 140), (cx + 60, cy + 260), (cx + 260, cy + 120)]


def s14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_s14))
    if sc <= 0:
        return None
    sock(c, cx - 340, cy - 330, 0.85 * sc, -10)
    with at_pop(c, cx - 120, cy + 470, sc):
        draw_li(c, cx - 120 + 40 * math.sin(T * 2), cy + 470, 0.75, "smile")
    return None


ev(j, k_s14, s14, "pop", 0.7)


def path14(c, kk, T, cx=cx, cy=cy):
    t0 = tb(14, k_path14)
    if T < t0:
        return None
    f = ease_in_out(clamp01((T - t0) / 0.8))
    p = skia.Path()
    p.moveTo(*PATH14[0])
    for i in range(1, len(PATH14) - 1, 2):
        p.quadTo(*PATH14[i], *PATH14[i + 1])
    meas = skia.PathMeasure(p, False)
    seg = skia.Path()
    meas.getSegment(0, meas.getLength() * f, seg, True)
    pt = wb.marker(NIGHT, 7)
    pt.setPathEffect(skia.DashPathEffect.Make([30, 22], 0))
    c.drawPath(seg, pt)
    return None


ev(j, k_path14, path14, "wood_high", 0.7)


def goal14(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(14, k_goal14)
    if dt < 0:
        return None
    x, y = cx + 310, cy - 60
    with K.at(c, x, y, 3, pop_scale(dt)):
        box(c, 0, 0, 360, 200, "#FFF4D6", L.ACC, 9, 20)
        K.text(c, "要紧的事", 0, 4, 76, "hand", L.ACC)
    sparkle(c, x, y, dt, YELLOW, 10, 200, 280)
    return None


ev(j, k_goal14, goal14, "ding", 0.85)

# ================================================================ 屏 15：评论区——“梦里一直找袜子”；砝码挪回来；下一讲预告
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k_box = kq(j, wt(18, 0, 0.4), 0)
k_type = nx(j, wt(19, 0, 0.5), k_box)
k_likes = nx(j, wt(19, 1, 0.5), k_type)
k_back = nx(j, wt(20, 2, 0.3), k_likes)
k_n = nx(j, wt(21, 0, 0.1), k_back)
L.note("评论区", "梦里一直找袜子", "发送", "+1", "挪回来")


def input15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_box))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(15, k_type):
            s_ = "梦里一直找袜子"
            g = clamp01((T - tb(15, k_type)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], x - w / 2 + 40, y + 2, 58, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, L.ACC)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
        for i in range(6):
            g = pop_scale(T - tb(15, k_likes) - i * 0.15)
            if g > 0:
                with K.at(c, x - 330 + i * 120, y + 140, 0, g):
                    K.rr(c, 0, 0, 100, 60, 30, "#FFF4D6")
                    K.text(c, "+1", 0, 2, 40, "hand", L.ACC)
    return None


ev(j, k_box, input15, "wood_high", 0.7)
b.hit(j, k_type, "pop", 0.6, "打字")
b.hit(j, k_likes, "clap", 0.75, "好多人加一")


def back15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_back))
    if sc <= 0:
        return None
    y = cy + 300
    f = ease_in_out(clamp01((T - tb(15, k_back) - 0.2) / 0.7))
    with at_pop(c, cx, y, sc):
        sock(c, cx + 340, y - 60, 0.5, 10)
        box(c, cx - 360, y - 40, 200, 160, "#E4E2F6", NIGHT, 6, 12)
        heart(c, cx - 360, y - 40, 40, "#E5484D", RED)
        xw = lerp(cx + 300, cx - 100, f)
        weight(c, xw, y - 60, 0.7)
        draw_li(c, xw + 150, y + 120, 0.75, "smile", lh=(xw + 60, y - 60), rh=(xw + 70, y - 40))
        K.text(c, "挪回来", cx, y - 260, 70, "hand", GREEN)
    return None


ev(j, k_back, back15, "ding", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "梦里为什么不讲道理？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=6, notes=NOTES)
L.export(globals())
