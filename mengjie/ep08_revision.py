"""《梦的解析》08 二次修饰：醒来一想，梦怎么就圆上了？（白板手绘 + AI 旁白，竖屏 2:3）

倒叙（先给讲得很圆的版本）：先看讲给同事听的“圆”故事，再一层层拆回醒来时的碎片。
- 开场：三块碎片 → 一根线缝起来 → 圆成一个球，配音“越讲越圆”；
- 痛点：小李刚醒，梦泡泡里只有几块碎片；讲给同事听时成了 1→2→3 的连环画；
- 身边的例子（drop 在第 2 屏）：梦里在飞 → 讲出来成了“为了赶飞机”，飞机卡砸下；陌生人讲着讲着成了前同事；
- 书中：弗洛伊德与“二次修饰”，缺口补上、乱的排好；梦像房子，正面整齐，门一开里头乱；修得越顺离原意越远；
  梦里冒出“这只是个梦”，看门的说的，好接着睡；醒着时记性也往顺里补；
- 现在怎么看：每回想一次，记忆卡片就悄悄改一点；
- 三步：先写碎片一个词一行、圈出补的“因为 后来 然后”、去掉补的看最怪的一块；吵完架复盘两栏；评论区与下一讲。
文案与出处见 mengjie/PLAN.md「### 08」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_li, draw_worker, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, NOTE_FILL, PAPER_W, WOOD, at_pop, bed, box, draw_freud, dream_cloud, moon,
                         pen, sleeper, sparkle, star)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross

SHARD_COLS = [("#CFE0F5", BLUE), ("#FFF1A8", ORANGE), ("#F6C3BE", RED), ("#D3EDDC", GREEN)]
SHARD_PTS = [((-60, -50), (50, -70), (70, 20), (-10, 60), (-70, 20)),
             ((-50, -60), (60, -40), (40, 60), (-60, 40)),
             ((-70, -30), (10, -70), (70, -10), (30, 60), (-40, 50)),
             ((-40, -70), (60, -50), (50, 50), (-20, 70), (-70, 0))]


def shard(c, x, y, s=1.0, i=0, rot=0.0, alpha=1.0):
    """一块梦的碎片（不规则多边形）。"""
    fill, line = SHARD_COLS[i % 4]
    with K.at(c, x, y, rot, s):
        p = P(*SHARD_PTS[i % 4], close=True)
        c.drawPath(p, K.paint(fill, alpha))
        c.drawPath(p, wb.marker(line, 6, alpha))


def plane(c, x, y, s=1.0, rot=0.0, alpha=1.0):
    """小飞机，机头朝右。"""
    with K.at(c, x, y, rot, s):
        body = skia.Path()
        body.addRoundRect(skia.Rect.MakeXYWH(-120, -24, 240, 48), 24, 24)
        c.drawPath(body, K.paint(PAPER_W, alpha))
        c.drawPath(body, wb.marker(BLUE, 6, alpha))
        for p in (P((-10, -20), (30, -90), (60, -90), (40, -20), close=True),
                  P((-10, 20), (30, 90), (60, 90), (40, 20), close=True),
                  P((-110, -20), (-130, -60), (-100, -60), (-80, -20), close=True)):
            c.drawPath(p, K.paint("#CFE0F5", alpha))
            c.drawPath(p, wb.marker(BLUE, 5, alpha))
        for i in range(3):
            c.drawCircle(60 - i * 40, -4, 8, K.paint(BLUE, alpha))


def flyer(c, x, y, s, T, mood="smile"):
    """张开双臂飞的小李（横躺），(x, y) 为身体中心。"""
    with K.at(c, x, y + 8 * math.sin(T * 3), -80):
        draw_li(c, 0, 150 * s, s, mood, lh=(-130 * s, -90 * s), rh=(130 * s, -90 * s))
    for i in range(3):
        ph = (T * 1.2 + i / 3) % 1
        C.line(c, (x + 140 * s + ph * 60, y - 30 + i * 30), (x + 220 * s + ph * 60, y - 30 + i * 30), GRAY, 5, 1 - ph)


def stranger(c, x, y, s, alpha=1.0):
    """灰色剪影的陌生人（脸上一个问号）。"""
    hy = y - 290 * s
    c.drawCircle(x, hy, 45 * s, K.paint("#B9BEC7", alpha))
    torso = P((x - 50 * s, hy + 55 * s), (x + 50 * s, hy + 55 * s), (x + 60 * s, y - 100 * s), (x - 60 * s, y - 100 * s),
              close=True)
    c.drawPath(torso, K.paint("#B9BEC7", alpha))
    for sg in (-1, 1):
        C.line(c, (x, y - 110 * s), (x + sg * 50 * s, y), "#8A8F99", 12, alpha)
    K.text(c, "？", x, hy + 6 * s, 64 * s, "hand", PAPER_W, alpha)


def ruled(c, x, y, w, h, rows, fill=NOTE_FILL, line=ORANGE, rot=0.0):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, fill, line, 7, 12)
        for r in range(rows):
            yy = -h / 2 + (r + 1) * h / (rows + 1)
            C.line(c, (-w / 2 + 30, yy + 34), (w / 2 - 30, yy + 34), "#E8C873", 3)


def _hook(H, j, cx, cy, acc):
    """开场：三块碎片 → 一根线缝起来 → 圆成一个球；随后“越讲越圆”逐字砸下。"""
    b = H.b
    xs = [(cx - 330, cy - 230), (cx - 70, cy - 150), (cx - 260, cy - 30)]

    def bits(c, kk, T):
        t0 = H.tb(j, 0)
        m = ease_in_out(clamp01((T - H.tb(j, 2)) / 0.3)) if T >= H.tb(j, 2) else 0.0
        for i, (x, y) in enumerate(xs):
            g = pop_scale(T - t0 - i * 0.08)
            if g > 0 and m < 1:
                shard(c, lerp(x, cx + 300, m), lerp(y, cy - 150, m), 1.3 * g * (1 - m), i, (-15, 20, 5)[i], 1 - m)
        return None
    b.custom(j, 0, 0.3, bits, sfx="wood_low", gain=0.7)

    def thread(c, kk, T):
        dt = T - H.tb(j, 1)
        if dt < 0 or T >= H.tb(j, 2) + 0.3:
            return None
        f = ease_out(clamp01(dt / 0.4))
        p = skia.Path()
        p.moveTo(*xs[0])
        p.quadTo(cx - 150, cy - 280, *xs[1])
        p.quadTo(cx - 120, cy, *xs[2])
        meas = skia.PathMeasure(p, False)
        seg = skia.Path()
        meas.getSegment(0, meas.getLength() * f, seg, True)
        c.drawPath(seg, wb.marker(RED, 7))
        return None
    b.custom(j, 1, 1.3, thread, sfx="shaker", gain=0.75)

    def ball(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        with K.at(c, cx + 300, cy - 150, 0, pop_scale(dt - 0.15)):
            c.drawCircle(0, 0, 140, K.paint("#FFE39A"))
            c.drawCircle(0, 0, 140, wb.marker(ORANGE, 9))
            c.drawArc(skia.Rect.MakeXYWH(-90, -100, 70, 70), 180, 90, False, wb.marker(PAPER_W, 10))
        sparkle(c, cx + 300, cy - 150, dt - 0.15, YELLOW, 10, 170, 250)
        return None
    b.custom(j, 2, 2.3, ball, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("08", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第六章 I“二次修饰”。",
    "书中观点：二次修饰像醒着的思维，填补空隙、理顺次序，给梦一个“门面”；梦里“这只是个梦”的判断也出自这道工序，让人接着睡。",
    "现在的研究：记忆重构，每回想一次都会改动一点。小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：刚醒只剩碎片；讲给同事听，成了 1→2→3 的故事
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_bed = 0
k_cl = nx(j, wt(0, 1, 0.5), k_bed)
k_tell = nx(j, wt(1, 0, 0.4), k_cl)
k_story = nx(j, wt(1, 1, 0.5), k_tell)
BED1 = (cx - 520, cy - 130)
HIP1 = (BED1[0] + 200, BED1[1] - 20)
CL1 = (cx + 190, cy - 380)
L.note("1", "2", "3")


def scene1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_bed))
    if sc <= 0:
        return None
    with at_pop(c, BED1[0] + 230, BED1[1], sc):
        bed(c, *BED1, 460)
        sleeper(c, *HIP1, 0.7, T, tb(1, k_bed) + 0.4, "flat")
    return None


ev(j, k_bed, scene1, "wood_low", 0.7)


def cloud1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_cl))
    if not dream_cloud(c, CL1[0], CL1[1], 600, 360, sc, tail_to=(HIP1[0] + 20, HIP1[1] - 200)):
        return None
    with at_pop(c, CL1[0], CL1[1], sc):
        for i, (dx, dy, r) in enumerate(((-180, -20, -15), (-40, 50, 20), (90, -40, 5), (210, 40, -25))):
            shard(c, CL1[0] + dx, CL1[1] + dy, 0.9, i, r + 5 * math.sin(T * 2 + i))
    return None


ev(j, k_cl, cloud1, "pop", 0.75)


def tell1(c, sc, T, cx=cx, cy=cy):
    y = cy + 460
    with at_pop(c, cx, y, sc):
        draw_li(c, cx - 380, y, 0.75, "smile")
        draw_worker(c, cx + 400, y, 0.75, mood="o")
    return None


ev(j, k_tell, pop_fn(j, k_tell, tell1), "wood_high", 0.7)


def story1(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(1, k_story)
    if dt < 0:
        return None
    x, y = cx, cy + 150
    with K.at(c, x, y, 0, pop_scale(dt)):
        c.drawRoundRect(skia.Rect.MakeXYWH(-290, -110, 580, 220), 40, 40, K.paint(PAPER_W))
        c.drawPath(wb.bubble(0, 0, 580, 220, -1), wb.marker(BLACK, 7))
        for i in range(3):
            g = pop_scale(dt - 0.1 - i * 0.12)
            if g <= 0:
                continue
            with K.at(c, -180 + i * 180, 0, 0, g):
                box(c, 0, 0, 120, 120, NOTE_FILL, ORANGE, 5, 10)
                K.text(c, str(i + 1), 0, 4, 64, "hand", ORANGE)
            if i < 2:
                c.drawPath(wb.arrow((-110 + i * 180, 0), (-70 + i * 180, 0), 0.0, 16), wb.marker(BLACK, 5, g))
    return None


ev(j, k_story, story1, "ding", 0.8)

# ================================================================ 屏 2：梦里在飞 → drop：讲出来成了“为了赶飞机”
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_cl2 = 1
k_card = max(k_cl2 + 1, KD - 2)
CL2 = (cx - 120, cy - 300)
L.note("为了赶飞机")


def cloud2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_cl2))
    if not dream_cloud(c, CL2[0], CL2[1], 760, 440, sc):
        return None
    with at_pop(c, CL2[0], CL2[1], sc):
        flyer(c, CL2[0] - 40, CL2[1] + 30, 0.85, T)
        for i, (dx, dy) in enumerate(((-260, -110), (230, -100), (220, 110))):
            dream_cloud(c, CL2[0] + dx, CL2[1] + dy, 90, 50, 1.0)
    return None


ev(j, k_cl2, cloud2, "pop", 0.75)


def li2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_card))
    if sc <= 0:
        return None
    x, y = cx - 380, cy + 470
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.75, "smile", rh=(x + 110, y - 240))
    return None


ev(j, k_card, li2, "wood_high", 0.7)


def card2(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(2, KD)
    g = C.slam_scale(dt)
    if g <= 0:
        return None
    x, y = cx + 120, cy + 210
    with K.at(c, x, y, -4, g):
        box(c, 0, 0, 640, 330, NOTE_FILL, ORANGE, 9, 16)
        K.text(c, "为了赶飞机", 0, -90, 80, "hand", BLACK)
        plane(c, 0, 60, 1.0, -8)
    return None


ev(j, KD, card2, "kick", 0.95)


def up2(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(2, KD) - 0.35
    if dt < 0:
        return None
    with K.at(c, cx + 360, cy - 30, 6, C.slam_scale(dt)):
        K.text(c, "飞起来", 0, 0, 96, "hand", L.ACC)
    return None


L.note("飞起来")
b.custom(j, KD, KD + 0.3, up2)

# ================================================================ 屏 3：陌生人讲着讲着成了前同事
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_cl3 = kq(j, wt(4, 0, 0.5), 0)
k_talk = nx(j, wt(4, 1, 0.4), k_cl3)
k_morph = nx(j, wt(4, 2, 0.6), k_talk)
CL3 = (cx + 150, cy - 230)
GY3 = cy + 450
L.note("前同事")


def cloud3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_cl3))
    if not dream_cloud(c, CL3[0], CL3[1], 640, 560, sc, tail_to=(cx - 250, GY3 - 300)):
        return None
    with at_pop(c, CL3[0], CL3[1], sc):
        x, y = CL3[0], CL3[1] + 210
        m = clamp01((T - tb(3, k_morph)) / 0.4) if T >= tb(3, k_morph) else 0.0
        if m < 1:
            stranger(c, x, y, 1.1, 1 - m)
        if m > 0:
            draw_worker(c, x, y, 1.1, alpha=m, mood="smile")
    return None


ev(j, k_cl3, cloud3, "pop", 0.75)


def li3(c, sc, T, cx=cx, cy=cy):
    x = cx - 320
    with at_pop(c, x, GY3, sc):
        draw_li(c, x, GY3, 0.85, "smile")
    return None


ev(j, k_talk, pop_fn(j, k_talk, li3), "wood_high", 0.7)
ev(j, k_talk, L.pop_bubble("讲着讲着", cx - 390, cy - 80, j, k_talk, 56, BLACK, tail=-1), None)
ev(j, k_morph, L.stamp("前同事", cx + 210, cy + 250, 72, j, k_morph, color=L.ACC, rot=-6), "ding", 0.85)

# ================================================================ 屏 4：弗洛伊德：最后一道工序“二次修饰”——缺的补上，乱的排好
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_fr = kq(j, wt(5, 0, 0.3), 0)
k_last = nx(j, wt(5, 2, 0.5), k_fr)
k_name = nx(j, wt(6, 0, 0.2), k_last)
k_fill = nx(j, wt(6, 1, 0.4), k_name)
k_sort = nx(j, wt(6, 2, 0.4), k_fill)
L.note("二次修饰", "修顺", "补上", "排好")


def fr4(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 380, cy + 450
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 1.0, "smile")
    return None


ev(j, k_fr, pop_fn(j, k_fr, fr4), "wood_low", 0.7)


def last4(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(4, k_last)
    if dt < 0:
        return None
    with K.at(c, cx, cy - 420, -2, C.slam_scale(dt)):
        box(c, 0, 0, 640, 170, PAPER_W, L.ACC, 9, 30)
        K.text(c, "二次修饰", 0, 4, 110, "hand", L.ACC) if T >= tb(4, k_name) else \
            K.text(c, "修顺", 0, 4, 110, "hand", L.ACC)
    return None


ev(j, k_last, last4, "kick", 0.85)
b.hit(j, k_name, "rim", 0.8, "二次修饰")
b.shots[j].shake = [(k_last, 7.0)]


def fill4(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(4, k_fill)
    if dt < 0:
        return None
    x, y = cx + 220, cy - 90
    with at_pop(c, x, y, pop_scale(dt)):
        box(c, x, y, 380, 240, PAPER_W, BLACK, 6, 10)
        for i, (dx, dy) in enumerate(((-110, -50), (0, -50), (110, -50), (-110, 50), (110, 50))):
            box(c, x + dx, y + dy, 96, 86, SHARD_COLS[i % 4][0], SHARD_COLS[i % 4][1], 5, 6)
        f = ease_out(clamp01((dt - 0.15) / 0.4))
        box(c, x, lerp(y - 220, y + 50, f), 96, 86, "#FFE39A", ORANGE, 6, 6)
        K.text(c, "补上", x, y + 180, 60, "hand", ORANGE)
    return None


ev(j, k_fill, fill4, "pop", 0.75)


def sort4(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(4, k_sort)
    if dt < 0:
        return None
    x, y = cx + 220, cy + 300
    m = ease_in_out(clamp01((dt - 0.15) / 0.5))
    with at_pop(c, x, y, pop_scale(dt)):
        for i in range(4):
            w_ = (300, 160, 240, 100)[i]
            tw = 100 + 60 * i
            yy = y - 120 + lerp((2, 0, 3, 1)[i], i, m) * 70
            C.line(c, (x - 160, yy), (x - 160 + lerp(w_, tw, m), yy), BLUE, 18)
        K.text(c, "排好", x + 150, y + 170, 60, "hand", BLUE)
    return None


ev(j, k_sort, sort4, "ding", 0.8)

# ================================================================ 屏 5：梦像房子：正面整齐，里头乱；修得越顺，离原意越远
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_hs = kq(j, wt(7, 1, 0.4), 0)
k_open = nx(j, wt(7, 3, 0.4), k_hs)
k_far = nx(j, wt(8, 1, 0.4), k_open)
HX, HY = cx - 60, cy + 160
L.note("正面", "原来的意思", "越远")


def house5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_hs))
    if sc <= 0:
        return None
    op = ease_out(clamp01((T - tb(5, k_open)) / 0.35)) if T >= tb(5, k_open) else 0.0
    with at_pop(c, HX, HY, sc):
        roof = P((HX - 340, HY - 300), (HX, HY - 520), (HX + 340, HY - 300), close=True)
        c.drawPath(roof, K.paint("#F6C3BE"))
        c.drawPath(roof, wb.marker(BLACK, 8))
        box(c, HX, HY - 80, 560, 440, PAPER_W, BLACK, 8, 6)
        for dx in (-170, 170):
            box(c, HX + dx, HY - 190, 120, 110, "#CFE0F5", BLUE, 6, 4)
            C.line(c, (HX + dx, HY - 245), (HX + dx, HY - 135), BLUE, 4)
        # 门洞里头乱
        box(c, HX, HY + 20, 160, 240, "#3A3F48", BLACK, 6, 4)
        if op > 0:
            c.drawPath(wb.scribble(HX, HY + 20, 120, 190, 9), wb.marker(RED, 6, op))
            for i in range(3):
                shard(c, HX - 40 + i * 40, HY - 40 + (i % 2) * 90, 0.45, i, i * 40, op)
        w = 160 * (1 - 0.85 * op)
        c.drawRect(skia.Rect.MakeXYWH(HX - 80, HY - 100, w, 240), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(HX - 80, HY - 100, w, 240), wb.marker("#A9773E", 6))
        K.text(c, "正面", HX - 400, HY - 120, 60, "hand", GREEN)
        c.drawPath(check(HX - 400, HY - 30, 40), wb.marker(GREEN, 9))
    return None


ev(j, k_hs, house5, "wood_low", 0.7)
b.hit(j, k_open, "tom", 0.8, "门一开里头乱")


def far5(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(5, k_far)
    if dt < 0:
        return None
    y = cy + 440
    f = ease_out(clamp01(dt / 0.5))
    with at_pop(c, cx, y, pop_scale(dt)):
        box(c, cx - 330, y, 300, 90, PAPER_W, NIGHT, 6, 30)
        K.text(c, "原来的意思", cx - 330, y + 2, 46, "hand", NIGHT)
    c.drawPath(wb.arrow((cx - 160, y), (lerp(cx - 160, cx + 330, f), y), 0.0, 34), wb.marker(RED, 9))
    with at_pop(c, cx + 380, y - 90, pop_scale(dt - 0.3)):
        K.text(c, "越远", cx + 380, y - 90, 80, "hand", RED)
    return None


ev(j, k_far, far5, "ding", 0.8)

# ================================================================ 屏 6：梦里冒出“这只是个梦”——看门的说的，好接着睡
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_bed6 = 0
k_cl6 = nx(j, wt(9, 1, 0.3), k_bed6)
k_say6 = nx(j, wt(9, 2, 0.3), k_cl6)
k_guard = nx(j, wt(10, 1, 0.4), k_say6)
k_zz = nx(j, wt(10, 2, 0.3), k_guard)
BED6 = (cx - 420, cy + 380)
CL6 = (cx - 60, cy - 250)
L.note("这只是个梦", "Z")


def sleep6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_bed6))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED6[1], sc):
        bed(c, *BED6, 520)
        sleeper(c, BED6[0] + 230, BED6[1] - 20, 0.75, T, None, "smile" if T >= tb(6, k_zz) else "sad")
        if T >= tb(6, k_zz):
            for i in range(3):
                f = ((T - tb(6, k_zz)) * 0.7 + i / 3) % 1
                K.text(c, "Z", BED6[0] + 40 + f * 60, BED6[1] - 150 - f * 160, 50 + i * 10, "hand", NIGHT, 1 - f)
    return None


b.custom(j, k_bed6, k_bed6 + 0.3, sleep6, sfx="wood_low", gain=0.7)


def cloud6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_cl6))
    if not dream_cloud(c, CL6[0], CL6[1], 820, 500, sc, tail_to=(BED6[0] + 60, BED6[1] - 120)):
        return None
    with at_pop(c, CL6[0], CL6[1], sc):
        x, y = CL6[0] - 170, CL6[1] + 40
        wob = 4 * math.sin(T * 5)
        p = skia.Path()
        p.moveTo(x - 110, y + 120)
        p.quadTo(x - 120, y - 120, x, y - 120 + wob)
        p.quadTo(x + 120, y - 120, x + 110, y + 120)
        for i in range(4):
            p.lineTo(x + 110 - (i + 0.5) * 55, y + 90)
            p.lineTo(x + 110 - (i + 1) * 55, y + 120)
        p.close()
        c.drawPath(p, K.paint("#B9BEC7"))
        c.drawPath(p, wb.marker(BLACK, 6))
        for sg in (-1, 1):
            c.drawCircle(x + sg * 35, y - 30, 14, K.paint(BLACK))
        if T >= tb(6, k_say6):
            g = pop_scale(T - tb(6, k_say6))
            with K.at(c, CL6[0] + 150, CL6[1] - 20, 0, g):
                c.drawRoundRect(skia.Rect.MakeXYWH(-200, -70, 400, 140), 40, 40, K.paint(NOTE_FILL))
                c.drawRoundRect(skia.Rect.MakeXYWH(-200, -70, 400, 140), 40, 40, wb.marker(ORANGE, 6))
                K.text(c, "这只是个梦", 0, 4, 60, "hand", BLACK)
    return None


ev(j, k_cl6, cloud6, "pop", 0.75)
b.hit(j, k_say6, "ding", 0.8, "这只是个梦")


def guard6(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 420, cy + 460
    with at_pop(c, x, y, sc):
        for gx in (x - 110, x + 110):
            box(c, gx, y - 170, 36, 340, WOOD, "#A9773E", 5, 6)
        draw_worker(c, x, y, 0.75, lh=(x - 90, y - 330), mood="smile")
    return None


ev(j, k_guard, pop_fn(j, k_guard, guard6), "wood_high", 0.75)
ev(j, k_zz, L.slam_text("接着睡", cx + 60, cy + 110, 96, NIGHT, j, k_zz, rot=-4), "kick", 0.85)

# ================================================================ 屏 7：醒着的时候，记性也往顺里补
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_li7 = kq(j, wt(11, 0, 0.4), 0)
k_dots = nx(j, wt(11, 1, 0.3), k_li7)
k_patch = nx(j, wt(11, 1, 0.75), k_dots)
L.note("往顺里补", "记性")
PTS7 = [(cx - 420, cy - 120), (cx - 240, cy - 300), (cx - 40, cy - 160), (cx + 160, cy - 340), (cx + 400, cy - 200)]


def li7(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 250, cy + 450
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.85, "smile")
        sun_x, sun_y = x - 220, y - 420
        A.sun(c, sun_x, sun_y, 50)
        K.text(c, "记性", x + 260, y - 120, 60, "hand", NIGHT)
    return None


ev(j, k_li7, pop_fn(j, k_li7, li7), "wood_low", 0.7)


def curve7():
    p = skia.Path()
    p.moveTo(*PTS7[0])
    for i in range(1, len(PTS7) - 1):
        mx, my = (PTS7[i][0] + PTS7[i + 1][0]) / 2, (PTS7[i][1] + PTS7[i + 1][1]) / 2
        p.quadTo(*PTS7[i], mx, my)
    p.lineTo(*PTS7[-1])
    return p


def dots7(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(7, k_dots)
    if dt < 0:
        return None
    p = curve7()
    meas = skia.PathMeasure(p, False)
    L_ = meas.getLength()
    for i in range(6):
        g = pop_scale(dt - i * 0.06)
        if g <= 0:
            continue
        seg = skia.Path()
        meas.getSegment(L_ * i / 6, L_ * (i / 6 + 0.09), seg, True)
        c.drawPath(seg, wb.marker(BLACK, 12, g))
    if T >= tb(7, k_patch):
        f = ease_in_out(clamp01((T - tb(7, k_patch)) / 0.8))
        seg = skia.Path()
        meas.getSegment(0, L_ * f, seg, True)
        c.drawPath(seg, wb.marker(RED, 7))
        pos = meas.getPosTan(L_ * f)[0]
        pen(c, pos.x() - 60, pos.y() - 40, 40, 0.9)
        if f >= 1:
            with at_pop(c, cx + 220, cy + 30, pop_scale(T - tb(7, k_patch) - 0.8)):
                K.text(c, "往顺里补", cx + 220, cy + 30, 80, "hand", RED)
    return None


ev(j, k_dots, dots7, "pop", 0.7)
b.hit(j, k_patch, "shaker", 0.75, "笔把缺口连上")

# ================================================================ 屏 8：现在怎么看——每回想一次，记忆卡片悄悄改一点
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_br8 = kq(j, wt(12, 0, 0.5), 0)
k_c8 = [nx(j, wt(12, 1, 0.3), k_br8)]
k_c8 += [cap(j, k_c8[0] + 1), cap(j, k_c8[0] + 2)]
k_st8 = nx(j, wt(12, 2, 0.5), k_c8[2])
L.note("记忆研究", "第1次", "第2次", "第3次")


def br8(c, sc, T, cx=cx, cy=cy):
    x, y = cx, cy - 330
    with at_pop(c, x, y, sc):
        A.brain(c, x, y, 120)
        K.text(c, "记忆研究", x, y - 190, 56, "hand", BLUE)
    return None


ev(j, k_br8, pop_fn(j, k_br8, br8), "wood_low", 0.7)


def cards8(c, kk, T, cx=cx, cy=cy):
    for i in range(3):
        g = pop_scale(T - tb(8, k_c8[i]))
        if g <= 0:
            continue
        x, y = cx - 360 + i * 360, cy + 140
        with K.at(c, x, y, (-4, 2, 5)[i], g):
            box(c, 0, 0, 280, 320, PAPER_W, BLACK, 7, 12)
            K.text(c, f"第{i + 1}次", 0, -120, 50, "hand", GRAY)
            star(c, 0, 20, 70 + 12 * i, ("#FFE39A", "#FFD27A", "#F6C3BE")[i], (YELLOW, ORANGE, RED)[i], 1.0, i * 0.25)
            if i > 0:
                c.drawCircle(60 + i * 10, 90, 12 + 6 * i, K.paint(BLUE))
        if i < 2:
            c.drawPath(wb.arrow((x + 150, y), (x + 210, y), 0.0, 20), wb.marker(BLACK, 6, g))
    return None


ev(j, k_c8[0], cards8, "pop", 0.7)
b.hit(j, k_c8[1], "pop", 0.7, "第二次")
b.hit(j, k_c8[2], "pop", 0.7, "第三次")
ev(j, k_st8, L.stamp("改一点", cx + 240, cy + 430, 64, j, k_st8, color=RED, rot=-6), "rim", 0.85)

# ================================================================ 屏 9：说回我们自己——别先听讲好的故事；“三步”
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_li9 = kq(j, wt(13, 0, 0.5), 0)
k_x9 = nx(j, wt(13, 1, 0.5), k_li9)
k_3 = nx(j, wt(13, 2, 0.4), k_x9)
GY9 = cy + 420
L.note("三步", "讲好的故事")


def li9(c, sc, T, cx=cx, cy=cy):
    x = cx - 260
    with at_pop(c, x, GY9, sc):
        C.line(c, (x - 300, GY9), (x + 300, GY9), BLACK, 7)
        draw_li(c, x, GY9, 0.9, "smile", rh=(x + 100, GY9 - 300))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 220, cy - 380, 440, 200), 40, 40, K.paint(PAPER_W))
        c.drawPath(wb.bubble(x, cy - 280, 440, 200, -1), wb.marker(BLACK, 7))
        K.text(c, "讲好的故事", x, cy - 276, 60, "hand", BLACK)
    return None


ev(j, k_li9, pop_fn(j, k_li9, li9), "wood_low", 0.7)


def x9(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(9, k_x9)
    if dt < 0:
        return None
    with K.at(c, cx - 260, cy - 280, 0, C.slam_scale(dt)):
        c.drawPath(cross(0, 0, 90), wb.marker(RED, 12, 0.8))
    return None


ev(j, k_x9, x9, "rim", 0.8)


def three9(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(9, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 280, cy + 40, -4, sc):
        c.drawCircle(0, 0, 190, K.paint("#FFF4D6"))
        c.drawCircle(0, 0, 190, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 130, "hand", L.ACC)
    return None


ev(j, k_3, three9, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 10：第一，先写碎片——一个词一行
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_h10 = kq(j, wt(14, 1, 0.3), 0)
k_w10 = [nx(j, wt(14, 2, 0.3), k_h10)]
k_w10 += [cap(j, k_w10[0] + 1), cap(j, k_w10[0] + 2)]
WORDS = ["飞", "机场", "蓝色的门"]
L.note("第一", "先写碎片", *WORDS)


def note10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_h10))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy, sc):
        K.text(c, "第一", cx - 330, cy - 480, 76, "hand", L.ACC)
        K.text(c, "先写碎片", cx + 60, cy - 480, 66, "hand", BLACK)
        ruled(c, cx, cy + 20, 640, 640, 3, rot=-2)
    for i, w_ in enumerate(WORDS):
        g = pop_scale(T - tb(10, k_w10[i]))
        if g <= 0:
            continue
        y = cy - 170 + i * 190
        with K.at(c, cx - 200, y, 0, g):
            shard(c, 0, 0, 0.55, i, 10)
        K.text(c, w_, cx - 110, y + 4, 72, "hand", BLACK, clamp01(g * 2), "left")
    return None


ev(j, k_h10, note10, "wood_low", 0.7)
for i, k_ in enumerate(k_w10):
    b.hit(j, k_, "pop", 0.7, f"写下：{WORDS[i]}")

# ================================================================ 屏 11：第二，圈出补的——因为、后来、然后
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_h11 = kq(j, wt(15, 1, 0.2), 0)
k_mk = [nx(j, wt(15, 1, 0.6), k_h11)]
k_mk += [cap(j, k_mk[0] + 1), cap(j, k_mk[0] + 2)]
k_late = nx(j, wt(15, 2, 0.6), k_mk[2])
ADD = [("因为", "要赶飞机"), ("后来", "飞起来了"), ("然后", "到了机场")]
L.note("第二", "圈出补的", "醒了以后加的", *[a for a, _ in ADD], *[z for _, z in ADD])


def note11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_h11))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy, sc):
        K.text(c, "第二", cx - 330, cy - 480, 76, "hand", L.ACC)
        K.text(c, "圈出补的", cx + 60, cy - 480, 66, "hand", BLACK)
        ruled(c, cx, cy - 20, 760, 600, 3, PAPER_W, GRAY)
        for i, (a, z) in enumerate(ADD):
            y = cy - 190 + i * 160
            K.text(c, a, cx - 250, y, 64, "hand", BLACK)
            K.text(c, z, cx + 60, y, 64, "hand", BLACK)
    for i in range(3):
        dt = T - tb(11, k_mk[i])
        if dt < 0:
            continue
        y = cy - 190 + i * 160
        f = ease_out(clamp01(dt / 0.35))
        r = skia.Rect.MakeXYWH(cx - 340, y - 55, 180, 110)
        c.drawArc(r, -90, 360 * f, False, wb.marker(RED, 8))
    dt = T - tb(11, k_late)
    if dt >= 0:
        with K.at(c, cx + 120, cy + 400, -4, C.slam_scale(dt)):
            box(c, 0, 0, 560, 120, "#FFF4D6", RED, 8, 30)
            K.text(c, "醒了以后加的", 0, 4, 64, "hand", RED)
    return None


ev(j, k_h11, note11, "wood_low", 0.7)
for i, k_ in enumerate(k_mk):
    b.hit(j, k_, "pop", 0.7, f"圈出：{ADD[i][0]}")
b.hit(j, k_late, "kick", 0.8, "醒了以后加的")

# ================================================================ 屏 12：第三，去掉补的，看最怪的那块
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_h12 = kq(j, wt(16, 1, 0.2), 0)
k_erase = nx(j, wt(16, 1, 0.7), k_h12)
k_odd = nx(j, wt(16, 2, 0.6), k_erase)
k_from = nx(j, wt(16, 3, 0.4), k_odd)
L.note("第三", "去掉补的", "最怪", "从这想起")


def note12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_h12))
    if sc <= 0:
        return None
    m = ease_in_out(clamp01((T - tb(12, k_erase)) / 0.5)) if T >= tb(12, k_erase) else 0.0
    with at_pop(c, cx, cy, sc):
        K.text(c, "第三", cx - 330, cy - 480, 76, "hand", L.ACC)
        K.text(c, "去掉补的", cx + 60, cy - 480, 66, "hand", BLACK)
        for i, (a, _) in enumerate(ADD):
            y = cy - 340 + i * 90
            K.text(c, a, cx + 300, y, 54, "hand", GRAY, 1 - 0.6 * m)
            if m > 0:
                C.line(c, (cx + 230, y), (cx + 230 + 140 * m, y), RED, 8)
    for i, w_ in enumerate(WORDS):
        x, y = cx - 300 + i * 300, cy + 120
        odd = i == 2 and T >= tb(12, k_odd)
        g = pop_scale(T - tb(12, k_erase) - 0.3) if T >= tb(12, k_erase) else 0.0
        if g <= 0:
            continue
        with K.at(c, x, y, (-3, 3, -2)[i], g * (1.15 if odd else 1.0)):
            box(c, 0, 0, 250, 170, "#FFF4D6" if odd else PAPER_W, RED if odd else GRAY, 8 if odd else 6, 12)
            K.text(c, w_, 0, 4, 56 if len(w_) > 2 else 70, "hand", RED if odd else BLACK)
    if T >= tb(12, k_odd):
        dt = T - tb(12, k_odd)
        K.ring(c, cx + 300, cy + 120, 170, RED, 9, 1.0, ease_out(clamp01(dt / 0.4)))
        with at_pop(c, cx + 20, cy - 80, pop_scale(dt - 0.1)):
            K.text(c, "最怪", cx + 20, cy - 80, 64, "hand", RED)
        c.drawPath(wb.arrow((cx + 90, cy - 80), (cx + 230, cy - 20), -0.2, 24), wb.marker(RED, 6, clamp01(dt * 3)))
    if T >= tb(12, k_from):
        dt = T - tb(12, k_from)
        x, y = cx + 120, cy + 400
        with K.at(c, x, y, 0, pop_scale(dt)):
            C.line(c, (-180, 50), (-120, 0), "#A9773E", 20)
            c.drawCircle(-60, -50, 80, K.paint(PAPER_W))
            c.drawCircle(-60, -50, 80, wb.marker(BLACK, 9))
            K.text(c, "从这想起", 200, -40, 66, "hand", GREEN)
    return None


ev(j, k_h12, note12, "wood_low", 0.7)
b.hit(j, k_erase, "shaker", 0.75, "划掉补的")
b.hit(j, k_odd, "ding", 0.8, "最怪的一块")
b.hit(j, k_from, "pop", 0.7, "从这想起")

# ================================================================ 屏 13：醒着也好用——吵完架复盘：先写发生了什么，再写你猜的
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_q13 = kq(j, wt(17, 0, 0.6), 0)
k_col1 = nx(j, wt(17, 1, 0.4), k_q13)
k_col2 = nx(j, wt(17, 2, 0.4), k_col1)
L.note("发生了什么", "你猜的", "他没回消息", "他生气了")


def q13(c, sc, T, cx=cx, cy=cy):
    y = cy + 450
    with at_pop(c, cx, y, sc):
        draw_li(c, cx - 200, y, 0.7, "sad")
        draw_worker(c, cx + 200, y, 0.7, mood="sad")
        for i in range(3):
            ph = math.sin(T * 12 + i)
            c.drawPath(P((cx - 40, y - 280 - i * 36), (cx, y - 290 - i * 36 + 6 * ph), (cx - 20, y - 300 - i * 36),
                         (cx + 30, y - 315 - i * 36)), wb.marker(RED, 6))
    return None


ev(j, k_q13, pop_fn(j, k_q13, q13), "wood_low", 0.7)


def cols13(c, kk, T, cx=cx, cy=cy):
    for i, (hd, it, col) in enumerate((("发生了什么", "他没回消息", BLUE), ("你猜的", "他生气了", ORANGE))):
        k_ = (k_col1, k_col2)[i]
        g = pop_scale(T - tb(13, k_))
        if g <= 0:
            continue
        x, y = cx - 260 + i * 520, cy - 200
        with K.at(c, x, y, (-2, 2)[i], g):
            box(c, 0, 0, 460, 420, PAPER_W, col, 8, 14)
            K.text(c, hd, 0, -140, 60, "hand", col)
            C.line(c, (-180, -90), (180, -90), col, 4)
            K.text(c, it, 0, 20, 62, "hand", BLACK)
            if i == 1:
                K.text(c, "？", 0, 130, 80, "hand", ORANGE)
            else:
                c.drawPath(check(0, 130, 40), wb.marker(GREEN, 10))
    return None


ev(j, k_col1, cols13, "pop", 0.7)
b.hit(j, k_col2, "ding", 0.8, "再写你猜的")

# ================================================================ 屏 14：评论区——“你这是编的吧”；碎片先留着；下一讲预告
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_box = kq(j, wt(18, 0, 0.4), 0)
k_type = nx(j, wt(19, 0, 0.5), k_box)
k_likes = nx(j, wt(19, 1, 0.5), k_type)
k_keep = nx(j, wt(20, 0, 0.5), k_likes)
k_n = nx(j, wt(21, 0, 0.1), k_keep)
L.note("评论区", "你这是编的吧", "发送", "+1", "先留着")


def input14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_box))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(14, k_type):
            s_ = "你这是编的吧"
            g = clamp01((T - tb(14, k_type)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], x - w / 2 + 40, y + 2, 58, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, L.ACC)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
        for i in range(6):
            g = pop_scale(T - tb(14, k_likes) - i * 0.15)
            if g > 0:
                with K.at(c, x - 330 + i * 120, y + 140, 0, g):
                    K.rr(c, 0, 0, 100, 60, 30, "#FFF4D6")
                    K.text(c, "+1", 0, 2, 40, "hand", L.ACC)
    return None


ev(j, k_box, input14, "wood_high", 0.7)
b.hit(j, k_type, "pop", 0.6, "打字")
b.hit(j, k_likes, "clap", 0.75, "好多人加一")


def keep14(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(14, k_keep)
    sc = pop_scale(dt)
    if sc <= 0:
        return None
    x, y = cx - 150, cy + 300
    with at_pop(c, x, y, sc):
        draw_li(c, x - 200, y + 60, 0.8, "smile", rh=(x - 90, y - 140))
        jar = P((x + 20, y - 220), (x + 20, y + 50), (x + 320, y + 50), (x + 320, y - 220))
        c.drawRoundRect(skia.Rect.MakeXYWH(x + 20, y - 220, 300, 270), 30, 30, K.paint("#EAF4FB"))
        c.drawPath(jar, wb.marker(BLUE, 8))
        c.drawRoundRect(skia.Rect.MakeXYWH(x + 0, y - 260, 340, 50), 14, 14, K.paint(WOOD))
        c.drawRoundRect(skia.Rect.MakeXYWH(x + 0, y - 260, 340, 50), 14, 14, wb.marker("#A9773E", 6))
        for i in range(4):
            shard(c, x + 90 + (i % 2) * 140, y - 130 + (i // 2) * 100, 0.6, i, i * 30 + 6 * math.sin(T * 2 + i))
        K.text(c, "先留着", x + 470, y - 300, 66, "hand", GREEN)
    sparkle(c, x + 170, y - 100, dt, YELLOW, 10, 170, 250)
    return None


ev(j, k_keep, keep14, "ding", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "为什么总梦见没穿衣服、从高处掉下来？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=4, notes=NOTES)
L.export(globals())
