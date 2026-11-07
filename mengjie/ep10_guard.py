"""《梦的解析》10 守护睡眠：闹钟响了，为什么梦里先变成了别的声音？（白板手绘 + AI 旁白，竖屏 2:3）

故事贯穿（一夜的动静）：从闹钟变成教堂钟声开始，一路跟着夜里的动静走——空调、憋尿、床头木板、洒水。
- 开场：响个不停的闹钟 → 箭头 → 晃动的大钟，配音“铃声变钟声”逐字砸下；
- 痛点：床头闹钟在响，梦里教堂敲钟、小李跟着数；数完才醒，“五分钟”；
- 身边的例子（drop 在第 2 屏）：空调冷风钻进梦里 → 雪地里找不到外套；憋尿 → 一排厕所门都打不开；
- 书中：弗洛伊德与书；床头木板掉下来砸到脖子 → 梦见法国大革命、断头台（卡通，刀落“咚”）→ 醒了；
  “睡眠的守护者”：小梦泡举着盾牌，把闹铃挡成故事，接着睡；口渴、憋尿、太冷都被编进去，动静太大才醒；
- 现在怎么看：往睡着的人身上洒水，醒来说梦里下雨了；
- 三步：换个陌生铃声、闹钟放远得下床关、睡前温度合适少喝水手机静音；梦护着觉、你也照顾它；评论区与下一讲。
文案与出处见 mengjie/PLAN.md「### 10」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_li, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, PAPER_W, WOOD, at_pop, bed, box, draw_freud, dream_cloud, moon, sleeper,
                         sparkle, sun)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross

ICE = "#CFE6F7"


# ---------------------------------------------------------------- 本讲画面元件

def alarm(c, x, y, r=70, T=0.0, ring=False, alpha=1.0, color=RED):
    """闹钟：(x, y) 为钟面中心；ring=True 时抖动并冒出声波。"""
    sh = 6 * math.sin(T * 40) if ring else 0
    with K.at(c, x + sh, y, sh * 0.6):
        for sg in (-1, 1):
            C.line(c, (sg * r * 0.6, r * 0.8), (sg * r * 0.8, r * 1.15), BLACK, 7, alpha)
            c.drawCircle(sg * r * 0.7, -r * 0.95, r * 0.26, K.paint(color, alpha))
            c.drawCircle(sg * r * 0.7, -r * 0.95, r * 0.26, wb.marker(BLACK, 4, alpha))
        c.drawCircle(0, 0, r, K.paint(PAPER_W, alpha))
        c.drawCircle(0, 0, r, wb.marker(color, 8, alpha))
        C.line(c, (0, 0), (0, -r * 0.6), BLACK, 6, alpha)
        C.line(c, (0, 0), (r * 0.45, r * 0.1), BLACK, 6, alpha)
    if ring:
        for i in range(2):
            ph = (T * 2 + i * 0.5) % 1
            for sg in (-1, 1):
                a = skia.Path()
                rr = r * (1.25 + ph * 0.5)
                a.addArc(skia.Rect.MakeXYWH(x - rr, y - rr, rr * 2, rr * 2), (-30 if sg > 0 else 150), 60)
                c.drawPath(a, wb.marker(color, 5, alpha * (1 - ph)))


def big_bell(c, x, y, s=1.0, swing=0.0, alpha=1.0):
    """大钟：(x, y) 为挂点，swing 为摆动角度。"""
    with K.at(c, x, y, swing, s):
        C.line(c, (0, -20), (0, 20), "#A9773E", 10, alpha)
        p = skia.Path()
        p.moveTo(-40, 20)
        p.cubicTo(-50, 60, -60, 120, -100, 150)
        p.lineTo(100, 150)
        p.cubicTo(60, 120, 50, 60, 40, 20)
        p.close()
        c.drawPath(p, K.paint("#F2C14E", alpha))
        c.drawPath(p, wb.marker(ORANGE, 7, alpha))
        c.drawCircle(0, 168, 18, K.paint("#A9773E", alpha))


def church(c, x, y, s=1.0, swing=0.0):
    """教堂钟楼：(x, y) 为楼底中心，钟在楼顶开口里摆。"""
    with K.at(c, x, y, 0, s):
        box(c, 0, -170, 200, 340, "#F1E3CB", "#A9773E", 6, 6)
        c.drawPath(P((-120, -340), (0, -470), (120, -340), close=True), K.paint("#F6C3BE"))
        c.drawPath(P((-120, -340), (0, -470), (120, -340), close=True), wb.marker(RED, 6))
        C.line(c, (0, -470), (0, -530), BLACK, 6)
        C.line(c, (-22, -508), (22, -508), BLACK, 6)
        box(c, 0, -230, 130, 150, PAPER_W, "#A9773E", 5, 60)
        big_bell(c, 0, -295, 0.55, swing)
        c.drawRect(skia.Rect.MakeXYWH(-30, -90, 60, 90), K.paint("#A9773E"))


def snowflake(c, x, y, r=18, alpha=1.0, color=BLUE):
    for i in range(3):
        a = i * math.pi / 3
        C.line(c, (x - math.cos(a) * r, y - math.sin(a) * r), (x + math.cos(a) * r, y + math.sin(a) * r), color, 4, alpha)


def ac_unit(c, x, y, T=0.0, blow=True):
    """墙上的空调，往下吹冷风。(x, y) 为机身中心。"""
    box(c, x, y, 300, 100, PAPER_W, GRAY, 6, 18)
    C.line(c, (x - 120, y + 30), (x + 120, y + 30), GRAY, 4)
    c.drawCircle(x + 120, y - 20, 7, K.paint(GREEN))
    if blow:
        for i in range(3):
            ph = (T * 1.2 + i / 3) % 1
            yy = y + 70 + ph * 140
            c.drawPath(P((x - 100 + i * 80, yy), (x - 80 + i * 80, yy + 20), (x - 100 + i * 80, yy + 40)),
                       wb.marker(BLUE, 5, 1 - ph))
        for i in range(3):
            ph = (T * 0.8 + i / 3) % 1
            snowflake(c, x - 80 + i * 80, y + 90 + ph * 160, 14, 1 - ph)


def door(c, x, y, w=130, h=230, label="厕所", crossed=0.0, alpha=1.0):
    """门：(x, y) 为门底中心；crossed>0 时画红叉。"""
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h, w, h), K.paint("#F1E3CB", alpha))
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h, w, h), wb.marker("#A9773E", 6, alpha))
    c.drawCircle(x + w / 2 - 22, y - h / 2, 7, K.paint("#A9773E", alpha))
    box(c, x, y - h + 40, w - 30, 46, PAPER_W, BLUE, 4, 8, alpha)
    K.text(c, label, x, y - h + 42, 30, "hand", BLUE, alpha)
    if crossed > 0:
        with K.at(c, x, y - h / 2, 0, crossed):
            c.drawPath(cross(0, 0, 50), wb.marker(RED, 10))


def nightcap(c, hx, hy, s, rot=-90):
    """睡帽：hx, hy 为头心；随身体转动 rot。"""
    with K.at(c, hx, hy, rot + 90):
        p = P((-46 * s, -24 * s), (46 * s, -24 * s), (70 * s, -100 * s), close=True)
        c.drawPath(p, K.paint("#CFE0F5"))
        c.drawPath(p, wb.marker(BLUE, 5))
        c.drawCircle(70 * s, -100 * s, 12 * s, K.paint(PAPER_W))
        c.drawCircle(70 * s, -100 * s, 12 * s, wb.marker(BLUE, 4))


def guardian(c, x, y, s=1.0, T=0.0, shield=True, alpha=1.0):
    """梦小卫士：一团带笑脸的梦泡，举着盾牌。(x, y) 为泡泡中心。"""
    bob = 6 * math.sin(T * 3)
    y = y + bob
    for sg in (-1, 1):
        C.line(c, (x + sg * 40 * s, y + 70 * s), (x + sg * 50 * s, y + 140 * s), NIGHT, 8, alpha)
    dream_cloud(c, x, y, 220 * s, 170 * s, 1.0, alpha=alpha)
    for dx in (-26, 26):
        c.drawCircle(x + dx * s, y - 10 * s, 7 * s, K.paint(BLACK, alpha))
    m = skia.Path()
    m.addArc(skia.Rect.MakeXYWH(x - 22 * s, y + 4 * s, 44 * s, 28 * s), 20, 140)
    c.drawPath(m, wb.marker(BLACK, 5, alpha))
    if shield:
        sx, sy = x + 110 * s, y + 20 * s
        C.line(c, (x + 60 * s, y + 20 * s), (sx - 20 * s, sy), NIGHT, 8, alpha)
        p = P((sx - 55 * s, sy - 75 * s), (sx + 55 * s, sy - 75 * s), (sx + 55 * s, sy + 10 * s), (sx, sy + 80 * s),
              (sx - 55 * s, sy + 10 * s), close=True)
        c.drawPath(p, K.paint("#CFE0F5", alpha))
        c.drawPath(p, wb.marker(BLUE, 7, alpha))
        moon(c, sx, sy - 5 * s, 26 * s, alpha)


def zzz(c, x, y, T, t0, color=NIGHT):
    if T < t0:
        return
    for i in range(3):
        f = ((T - t0) * 0.7 + i / 3) % 1
        K.text(c, "Z", x + f * 60, y - f * 160, 50 + i * 10, "hand", color, 1 - f)


def header(L, j, k, cx, cy, first, rest, ev, pop_fn):
    def fn(c, sc, T):
        with at_pop(c, cx, cy - 500, sc):
            K.text(c, first, cx - 380, cy - 500, 70, "hand", L.ACC)
            K.text(c, rest, cx - 290 + K.text_w(rest, 60, "hand") / 2, cy - 500, 60, "hand", BLACK)
        return None
    L.note(first, rest)
    ev(j, k, pop_fn(j, k, fn), "wood_low", 0.6)


# ---------------------------------------------------------------- 开场

def _hook(H, j, cx, cy, acc):
    """开场：响个不停的闹钟 → 箭头 → 晃动的大钟；随后“铃声变钟声”逐字砸下。"""
    b = H.b

    def clk(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc > 0:
            with at_pop(c, cx - 320, cy - 200, sc):
                alarm(c, cx - 320, cy - 200, 110, T, ring=True)
        return None
    b.custom(j, 0, 0.3, clk, sfx="wood_low", gain=0.7)

    def arr(c, kk, T):
        dt = T - H.tb(j, 1)
        if dt < 0:
            return None
        f = ease_out(clamp01(dt / 0.35))
        c.drawPath(wb.arrow((cx - 120, cy - 200), (lerp(cx - 120, cx + 90, f), cy - 200), 0.2, 44), wb.marker(GRAY, 9))
        return None
    b.custom(j, 1, 1.3, arr, sfx="tom", gain=0.75)

    def bell(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        with at_pop(c, cx + 320, cy - 300, pop_scale(dt)):
            C.line(c, (cx + 180, cy - 380), (cx + 460, cy - 380), "#A9773E", 14)
            big_bell(c, cx + 320, cy - 360, 1.2, 18 * math.sin(dt * 5))
        sparkle(c, cx + 320, cy - 160, dt, YELLOW, 10, 150, 240)
        return None
    b.custom(j, 2, 2.3, bell, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("10", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第一章（外界刺激）、第五章 C、第七章（梦是睡眠的守护者）。",
    "书中例子：莫里（Maury）睡觉时床头板落下砸到脖子，梦见法国大革命、被送上断头台，刀落下时醒来（第一章）。",
    "往睡着的人身上洒水、醒来报告梦里有水，见 Dement & Wolpert（1958）。小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：闹钟在响，梦里教堂敲钟，小李跟着数；数完才醒，五分钟
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_bed1 = 0
k_cl1 = nx(j, wt(0, 1, 0.3), k_bed1)
k_cnt1 = nx(j, wt(0, 2, 0.4), k_cl1)
k_wake1 = nx(j, wt(1, 0, 0.6), k_cnt1)
k_five1 = nx(j, wt(1, 1, 0.6), k_wake1)
BED1 = (cx - 380, cy + 360)
HIP1 = (BED1[0] + 230, BED1[1] - 20)
CL1 = (cx + 90, cy - 250)
NUMS1 = ["1", "2", "3", "4", "5"]
L.note(*NUMS1, "五分钟")


def scene1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_bed1))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED1[1], sc):
        bed(c, *BED1, 560)
        sleeper(c, *HIP1, 0.8, T, tb(1, k_wake1), "o" if T >= tb(1, k_wake1) else "smile")
        box(c, BED1[0] + 670, BED1[1] + 10, 170, 140, WOOD, "#A9773E", 6, 8)
        alarm(c, BED1[0] + 670, BED1[1] - 130, 60, T, ring=True)
    return None


ev(j, k_bed1, scene1, "wood_low", 0.7)


def cloud1(c, kk, T, cx=cx, cy=cy):
    out = 1 - ease_in_out(clamp01((T - tb(1, k_wake1)) / 0.3))
    sc = pop_scale(T - tb(1, k_cl1)) * out
    if not dream_cloud(c, CL1[0], CL1[1], 820, 560, sc, tail_to=(HIP1[0] - 280, HIP1[1] - 90)):
        return None
    with at_pop(c, CL1[0], CL1[1], sc):
        church(c, CL1[0] - 170, CL1[1] + 250, 0.8, 20 * math.sin(T * 4))
        if T >= tb(1, k_cnt1):
            n = min(len(NUMS1), 1 + int((T - tb(1, k_cnt1)) / 0.45))
            for i in range(n):
                g = pop_scale(T - tb(1, k_cnt1) - i * 0.45)
                with K.at(c, CL1[0] + 70 + (i % 3) * 100, CL1[1] - 110 + (i // 3) * 120, 0, g):
                    K.text(c, NUMS1[i], 0, 0, 80, "hand", ORANGE)
    return None


ev(j, k_cl1, cloud1, "pop", 0.75)
b.hit(j, k_cnt1, "ding", 0.7, "跟着数")
b.hit(j, k_wake1, "kick", 0.85, "数完才醒")
b.shots[j].shake = [(k_wake1, 8.0)]
ev(j, k_five1, L.stamp("五分钟", BED1[0] + 670, BED1[1] - 340, 64, j, k_five1, rot=8), "rim", 0.8)

# ================================================================ 屏 2：drop——空调太冷，梦里在雪地里找不到外套
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_bed2 = 0
k_ac2 = max(1, min(kq(j, wt(2, 0, 0.4), 1), KD - 2))
k_cl2 = max(k_ac2 + 1, min(kq(j, wt(3, 0, 0.6), k_ac2 + 1), KD - 1))
BED2 = (cx - 400, cy + 380)
HIP2 = (BED2[0] + 230, BED2[1] - 20)
CL2 = (cx + 150, cy - 260)
L.note("外套？", "冷")


def scene2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_bed2))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED2[1], sc):
        bed(c, *BED2, 560)
        shiver = 4 * math.sin(T * 50) if T >= tb(2, k_ac2) else 0
        with K.at(c, shiver, 0, 0):
            sleeper(c, *HIP2, 0.8, T, None, "sad" if T >= tb(2, k_ac2) else "flat")
    return None


ev(j, k_bed2, scene2, "wood_low", 0.7)


def ac2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_ac2))
    if sc <= 0:
        return None
    x, y = cx - 400, cy + 120
    with at_pop(c, x, y, sc):
        ac_unit(c, x, y, T)
        K.text(c, "冷", x - 40, y - 110, 70, "hand", BLUE)
    return None


ev(j, k_ac2, ac2, "shaker", 0.75)


def cloud2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_cl2))
    if not dream_cloud(c, CL2[0], CL2[1], 720, 560, sc, tail_to=(HIP2[0] - 100, HIP2[1] - 120)):
        return None
    with at_pop(c, CL2[0], CL2[1], sc):
        gy = CL2[1] + 200
        c.drawPath(P((CL2[0] - 320, gy), (CL2[0] - 100, gy - 40), (CL2[0] + 120, gy - 10), (CL2[0] + 320, gy),
                     (CL2[0] + 320, gy + 60), (CL2[0] - 320, gy + 60), close=True), K.paint(ICE))
        c.drawPath(P((CL2[0] - 320, gy), (CL2[0] - 100, gy - 40), (CL2[0] + 120, gy - 10), (CL2[0] + 320, gy)),
                   wb.marker(BLUE, 6))
        x = CL2[0] - 40 + 50 * math.sin(T * 1.5)
        hy = gy - 290 * 0.6
        draw_li(c, x, gy, 0.6, "sad", lh=(x - 80, hy + 60), rh=(x + 80, hy + 60))
        A._sweat(c, x + 60, hy - 30, 0.8)
        for i in range(12):
            f = (T * 0.25 + i / 12) % 1
            snowflake(c, CL2[0] - 300 + (i * 53) % 600, CL2[1] - 220 + f * 400, 14, 1 - f * 0.5)
    return None


ev(j, k_cl2, cloud2, "pop", 0.7)


def coat2(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(2, KD)
    sc = C.slam_scale(dt)
    if sc <= 0:
        return None
    with K.at(c, cx + 270, cy + 190, -6, sc):
        box(c, 0, 0, 320, 150, PAPER_W, RED, 8, 20)
        K.text(c, "外套？", 0, 4, 100, "hand", RED)
    return None


ev(j, KD, coat2, "kick", 0.95)

# ================================================================ 屏 3：憋着尿睡觉，梦里到处找厕所，就是找不到
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_bed3 = 0
k_cl3 = nx(j, wt(4, 1, 0.1), k_bed3)
k_x3 = [nx(j, wt(4, 1, 0.5), k_cl3)]
k_x3.append(nx(j, wt(4, 1, 0.9), k_x3[0]))
k_no3 = nx(j, wt(4, 2, 0.5), k_x3[1])
BED3 = (cx - 400, cy + 380)
HIP3 = (BED3[0] + 230, BED3[1] - 20)
CL3 = (cx + 90, cy - 230)
L.note("厕所", "找不到")


def scene3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_bed3))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED3[1], sc):
        bed(c, *BED3, 560)
        wob = 6 * math.sin(T * 9)
        with K.at(c, 0, wob * 0.3, 0):
            sleeper(c, *HIP3, 0.8, T, None, "sad")
        c.drawPath(P((HIP3[0] + 180, HIP3[1] - 110), (HIP3[0] + 200, HIP3[1] - 140), (HIP3[0] + 220, HIP3[1] - 110)),
                   wb.marker(RED, 5))
        K.text(c, "!", HIP3[0] + 200, HIP3[1] - 190, 60, "hand", RED)
    return None


L.note("!")
ev(j, k_bed3, scene3, "wood_low", 0.7)


def cloud3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_cl3))
    if not dream_cloud(c, CL3[0], CL3[1], 860, 600, sc, tail_to=(HIP3[0] - 280, HIP3[1] - 90)):
        return None
    with at_pop(c, CL3[0], CL3[1], sc):
        gy = CL3[1] + 190
        C.line(c, (CL3[0] - 340, gy), (CL3[0] + 340, gy), BLACK, 6)
        for i in range(3):
            x = CL3[0] - 220 + i * 220
            k_ = k_x3[min(i, 1)] if i < 2 else k_no3
            door(c, x, gy, crossed=pop_scale(T - tb(3, k_)))
        run = ((T - tb(3, k_cl3)) * 0.5) % 1.0
        x = lerp(CL3[0] - 300, CL3[0] + 300, ease_in_out(abs(run * 2 - 1)))
        draw_li(c, x, gy + 10, 0.45, "o")
    return None


ev(j, k_cl3, cloud3, "pop", 0.7)
b.hit(j, k_x3[0], "rim", 0.75, "第一扇门不行")
b.hit(j, k_x3[1], "rim", 0.75, "第二扇门不行")
ev(j, k_no3, L.slam_text("找不到", cx + 280, cy + 180, 110, RED, j, k_no3, rot=-5), "kick", 0.85)
b.shots[j].shake = [(k_no3, 7.0)]

# ================================================================ 屏 4：弗洛伊德收集例子；有个人睡觉，床头木板掉下来砸到脖子
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_fr4 = kq(j, wt(5, 0, 0.3), 0)
k_bk4 = nx(j, wt(5, 1, 0.3), k_fr4)
k_man4 = nx(j, wt(6, 0, 0.5), k_bk4)
k_fall4 = nx(j, wt(6, 1, 0.5), k_man4)
k_hit4 = nx(j, wt(6, 2, 0.4), k_fall4)
L.note("梦的解析", "咚")
BED4 = (cx - 200, cy + 360)
HIP4 = (BED4[0] + 230, BED4[1] - 20)


def fr4(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 360, cy - 40
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 0.8)
    return None


ev(j, k_fr4, pop_fn(j, k_fr4, fr4), "wood_low", 0.7)


def bk4(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(4, k_bk4))
    if sc <= 0:
        return None
    with K.at(c, cx - 110, cy - 330, 6, sc):
        box(c, 0, 0, 220, 290, NIGHT, BLACK, 6, 10)
        K.text(c, "梦的", 0, -50, 54, "serif_black", "#FFE39A")
        K.text(c, "解析", 0, 20, 54, "serif_black", "#FFE39A")
        moon(c, 0, 100, 28)
    for i in range(3):
        g = pop_scale(T - tb(4, k_bk4) - 0.3 - i * 0.15)
        if g > 0:
            with K.at(c, cx + 150 + i * 120, cy - 380 + (i % 2) * 60, (-8, 6, -4)[i], g):
                box(c, 0, 0, 110, 140, PAPER_W, GRAY, 5, 6)
                for r in range(3):
                    C.line(c, (-35, -30 + r * 30), (35, -30 + r * 30), GRAY, 4)
    return None


ev(j, k_bk4, bk4, "ding", 0.75)


def board_fall(T, t_fall, t_hit, x0, y0, x1, y1):
    if T < t_fall:
        return x0, y0, 0.0
    f = clamp01((T - t_fall) / max(0.2, t_hit - t_fall))
    f = f * f
    return lerp(x0, x1, f), lerp(y0, y1, f), lerp(0, 80, f)


def man4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_man4))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED4[1], sc):
        C.line(c, (BED4[0], BED4[1] - 330), (BED4[0], BED4[1] + 110), "#A9773E", 14)
        bed(c, *BED4, 560)
        hx, hy = sleeper(c, *HIP4, 0.8, T, None, "o" if T >= tb(4, k_hit4) else "smile")
        nightcap(c, hx, hy, 0.8)
        bx, by, rot = board_fall(T, tb(4, k_fall4), tb(4, k_hit4), BED4[0] + 20, BED4[1] - 330, hx + 70, hy - 50)
        with K.at(c, bx, by, rot):
            c.drawRect(skia.Rect.MakeXYWH(-20, 0, 40, 180), K.paint(WOOD))
            c.drawRect(skia.Rect.MakeXYWH(-20, 0, 40, 180), wb.marker("#A9773E", 6))
    return None


ev(j, k_man4, man4, "wood_low", 0.7)
b.hit(j, k_fall4, "tom", 0.7, "木板松了")
ev(j, k_hit4, L.slam_text("咚", cx + 120, cy + 110, 150, RED, j, k_hit4, rot=-8), "kick", 0.9)
b.shots[j].shake = [(k_hit4, 9.0)]

# ================================================================ 屏 5：梦里法国大革命、断头台，刀落下来，醒了；一下编出前因后果
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_cl5 = kq(j, wt(7, 0, 0.4), 0)
k_gil5 = nx(j, wt(7, 1, 0.4), k_cl5)
k_drop5 = nx(j, wt(7, 2, 0.4), k_gil5)
k_wake5 = nx(j, wt(7, 3, 0.4), k_drop5)
k_st5 = nx(j, wt(8, 1, 0.6), k_wake5)
CL5 = (cx + 40, cy - 280)
BED5 = (cx - 500, cy + 400)
HIP5 = (BED5[0] + 200, BED5[1] - 20)
L.note("法国大革命", "咚", "醒了", "一下", "前因后果")


def flag(c, x, y, s=1.0, T=0.0):
    C.line(c, (x, y), (x, y - 260 * s), "#A9773E", 8)
    w = 60 * s
    wave = 8 * math.sin(T * 4)
    for i, col in enumerate(("#2E5AAC", "#FFFFFF", "#D93A3A")):
        c.drawRect(skia.Rect.MakeXYWH(x + i * w, y - 260 * s + wave * (i / 3), w, 120 * s), K.paint(col))
    c.drawRect(skia.Rect.MakeXYWH(x, y - 260 * s, 3 * w, 120 * s), wb.marker(BLACK, 4))


def guillotine(c, x, y, s, blade):
    """卡通断头台：两根立柱、横梁、斜刃（blade 0 在顶，1 落到底）。(x, y) 为底座中心。"""
    with K.at(c, x, y, 0, s):
        box(c, 0, -15, 260, 30, WOOD, "#A9773E", 6, 4)
        for sg in (-1, 1):
            c.drawRect(skia.Rect.MakeXYWH(sg * 80 - 14, -440, 28, 430), K.paint(WOOD))
            c.drawRect(skia.Rect.MakeXYWH(sg * 80 - 14, -440, 28, 430), wb.marker("#A9773E", 6))
        box(c, 0, -450, 220, 30, WOOD, "#A9773E", 6, 4)
        by = lerp(-420, -150, blade)
        p = P((-66, by), (66, by), (66, by + 50), (-66, by + 90), close=True)
        c.drawPath(p, K.paint("#C9D2DC"))
        c.drawPath(p, wb.marker(GRAY, 6))
        box(c, 0, -110, 132, 50, WOOD, "#A9773E", 6, 6)


def cloud5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_cl5))
    if not dream_cloud(c, CL5[0], CL5[1], 900, 560, sc, tail_to=(HIP5[0] - 180, HIP5[1] - 90)):
        return None
    with at_pop(c, CL5[0], CL5[1], sc):
        gy = CL5[1] + 230
        flag(c, CL5[0] - 330, gy, 0.85, T)
        K.text(c, "法国大革命", CL5[0] - 160, CL5[1] - 220, 52, "hand", NIGHT)
        for i in range(4):
            draw_li(c, CL5[0] - 290 + i * 70, gy + 30, 0.32, "o", back=i % 2 == 1)
        if T >= tb(5, k_gil5):
            g = pop_scale(T - tb(5, k_gil5))
            blade = 0.0
            if T >= tb(5, k_drop5):
                blade = clamp01((T - tb(5, k_drop5)) / 0.18) ** 2
            with at_pop(c, CL5[0] + 150, gy, g):
                guillotine(c, CL5[0] + 150, gy, 0.85, blade)
                hy = gy - 290 * 0.45
                draw_li(c, CL5[0] + 330, gy, 0.45, "o" if blade > 0 else "sad")
                A._sweat(c, CL5[0] + 380, hy - 30, 0.8)
    return None


ev(j, k_cl5, cloud5, "pop", 0.7)
b.hit(j, k_gil5, "wood_high", 0.7, "断头台")
ev(j, k_drop5, L.slam_text("咚", cx + 340, cy - 440, 110, RED, j, k_drop5, rot=8), "kick", 0.9)
b.shots[j].shake = [(k_drop5, 9.0)]


def bed5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_cl5))
    if sc <= 0:
        return None
    with at_pop(c, BED5[0] + 200, BED5[1], sc):
        bed(c, *BED5, 420)
        hx, hy = sleeper(c, *HIP5, 0.7, T, tb(5, k_wake5), "o" if T >= tb(5, k_wake5) else "flat", sweat=True)
        nightcap(c, hx, hy, 0.7, lerp(-90, 0, ease_out(clamp01((T - tb(5, k_wake5)) / 0.25))) if T >= tb(5, k_wake5) else -90)
    return None


b.custom(j, k_cl5, k_cl5 + 0.3, bed5)
ev(j, k_wake5, L.pop_text("醒了", cx - 20, cy + 180, 70, NIGHT, j, k_wake5), "wood_high", 0.7)


def chain5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_st5))
    if sc <= 0:
        return None
    x0, y0 = cx + 80, cy + 410
    with at_pop(c, x0, y0, sc):
        with K.at(c, x0, y0, 70):
            c.drawRect(skia.Rect.MakeXYWH(-16, -70, 32, 140), K.paint(WOOD))
            c.drawRect(skia.Rect.MakeXYWH(-16, -70, 32, 140), wb.marker("#A9773E", 5))
        K.text(c, "一下", x0, y0 + 80, 46, "hand", "#A9773E")
        c.drawPath(wb.arrow((x0 + 100, y0), (x0 + 190, y0), 0.0, 26), wb.marker(GRAY, 6))
        for i in range(4):
            box(c, x0 + 250 + i * 55, y0 - 40 + i * 20, 90, 110, PAPER_W, NIGHT, 5, 6)
    return None


ev(j, k_st5, chain5, "pop", 0.7)
ev(j, k_st5, L.stamp("前因后果", cx + 330, cy + 220, 62, j, k_st5, color=RED, rot=-5), "rim", 0.8)

# ================================================================ 屏 6：梦是睡眠的守护者——小梦泡举盾，把闹铃挡成故事，接着睡
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_bed6 = kq(j, wt(9, 0, 0.3), 0)
k_card6 = nx(j, wt(9, 1, 0.4), k_bed6)
k_g6 = nx(j, wt(10, 0, 0.4), k_card6)
k_blk6 = nx(j, wt(10, 1, 0.5), k_g6)
k_zz6 = nx(j, wt(10, 3, 0.3), k_blk6)
BED6 = (cx - 480, cy + 400)
HIP6 = (BED6[0] + 230, BED6[1] - 20)
G6 = (cx + 60, cy - 40)
L.note("睡眠的守护者", "叮铃", "接着睡")


def bed6(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, BED6[1], sc):
        bed(c, *BED6, 520)
        sleeper(c, *HIP6, 0.8, T, None, "smile")
        zzz(c, BED6[0] + 40, BED6[1] - 150, T, tb(6, k_zz6))
    return None


ev(j, k_bed6, pop_fn(j, k_bed6, bed6), "wood_low", 0.7)


def card6(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(6, k_card6))
    if sc <= 0:
        return None
    with K.at(c, cx, cy - 430, -2, sc):
        box(c, 0, 0, 820, 170, PAPER_W, NIGHT, 9, 30)
        K.text(c, "睡眠的守护者", 0, 4, 100, "hand", NIGHT)
    return None


ev(j, k_card6, card6, "kick", 0.85)
b.shots[j].shake = [(k_card6, 7.0)]


def guard6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_g6))
    if sc <= 0:
        return None
    with at_pop(c, *G6, sc):
        guardian(c, G6[0], G6[1], 1.3, T)
    # 闹铃声从右边飞来
    t0 = tb(6, k_g6)
    blk = tb(6, k_blk6)
    for i in range(3):
        ph = ((T - t0) * 0.9 + i / 3) % 1
        x = lerp(cx + 500, G6[0] + 270, ph)
        if T >= blk:
            x = cx + 430
        K.text(c, "叮铃", x, cy - 160 + i * 90, 56, "hand", RED, (1 - ph * 0.7) if T < blk else 0.8)
    return None


ev(j, k_g6, guard6, "wood_high", 0.7)


def story6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_blk6))
    x, y = cx - 260, cy - 180
    if not dream_cloud(c, x, y, 320, 200, sc, tail_to=(HIP6[0] - 200, HIP6[1] - 120)):
        return None
    with at_pop(c, x, y, sc):
        big_bell(c, x - 50, y - 60, 0.45, 15 * math.sin(T * 5))
        K.text(c, "钟声", x + 70, y + 10, 46, "hand", ORANGE)
    return None


L.note("钟声")
ev(j, k_blk6, story6, "rim", 0.8)
ev(j, k_zz6, L.pop_text("接着睡", cx + 300, cy + 330, 80, NIGHT, j, k_zz6), "ding", 0.75)

# ================================================================ 屏 7：口渴、憋尿、太冷都被编进去；动静太大，编不下去，才醒
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_sig7 = [kq(j, wt(11, 0, 0.55), 0)]
k_sig7.append(nx(j, wt(11, 0, 0.75), k_sig7[0]))
k_sig7.append(nx(j, wt(11, 0, 0.95), k_sig7[1]))
k_in7 = nx(j, wt(11, 1, 0.5), k_sig7[2])
k_big7 = nx(j, wt(12, 1, 0.3), k_in7)
k_wake7 = nx(j, wt(12, 2, 0.4), k_big7)
SIG7 = ["口渴", "憋尿", "太冷"]
CL7 = (cx + 120, cy - 200)
BED7 = (cx - 380, cy + 400)
HIP7 = (BED7[0] + 230, BED7[1] - 20)
L.note(*SIG7, "动静太大", "醒")


def icon7(c, i, x, y):
    if i == 0:
        p = P((x - 30, y - 40), (x + 30, y - 40), (x + 22, y + 40), (x - 22, y + 40), close=True)
        c.drawPath(p, K.paint(PAPER_W))
        c.drawPath(p, wb.marker(BLUE, 5))
        c.drawRect(skia.Rect.MakeXYWH(x - 22, y + 20, 44, 18), K.paint("#BFDDF7"))
    elif i == 1:
        door(c, x, y + 50, 70, 100, "", 0)
    else:
        snowflake(c, x, y, 36, 1.0)


def cloud7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_in7))
    wob = 0.0
    if tb(7, k_big7) <= T < tb(7, k_wake7):
        wob = 10 * math.sin(T * 40)
    with K.at(c, wob, 0, 0):
        if not dream_cloud(c, CL7[0], CL7[1], 800, 460, sc, tail_to=(HIP7[0] - 100, HIP7[1] - 140)):
            return None
    if T >= tb(7, k_wake7):
        f = ease_out(clamp01((T - tb(7, k_wake7)) / 0.25))
        x0 = CL7[0] - 60
        pts = [(x0, CL7[1] - 230), (x0 + 50, CL7[1] - 120), (x0 - 20, CL7[1] - 30), (x0 + 60, CL7[1] + 80), (x0 + 10, CL7[1] + 220)]
        n = max(2, int(len(pts) * f))
        c.drawPath(P(*pts[:n]), wb.marker(RED, 9))
    return None

def sig7(c, kk, T, cx=cx, cy=cy):
    cloud7(c, kk, T)
    for i, s_ in enumerate(SIG7):
        g = pop_scale(T - tb(7, k_sig7[i]))
        if g <= 0:
            continue
        x, y = cx - 410, cy - 380 + i * 200
        if T >= tb(7, k_in7):
            f = ease_in_out(clamp01((T - tb(7, k_in7) - i * 0.12) / 0.5))
            x, y = lerp(x, CL7[0] - 240 + i * 240, f), lerp(y, CL7[1] + 10, f)
            g *= lerp(1.0, 0.88, f)
        with K.at(c, x, y, 0, g):
            box(c, 0, 0, 250, 150, PAPER_W, (BLUE, ORANGE, BLUE)[i], 6, 20)
            icon7(c, i, -65, 0)
            K.text(c, s_, 45, 0, 60, "hand", BLACK)
    return None


ev(j, k_sig7[0], sig7, "pop", 0.7)
b.hit(j, k_sig7[1], "pop", 0.7, "憋尿")
b.hit(j, k_sig7[2], "pop", 0.7, "太冷")


b.hit(j, k_in7, "ding", 0.75, "都被编进去")


def bed7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_sig7[0]))
    if sc <= 0:
        return None
    with at_pop(c, BED7[0] + 280, BED7[1], sc):
        bed(c, *BED7, 560)
        sleeper(c, *HIP7, 0.8, T, tb(7, k_wake7), "o" if T >= tb(7, k_wake7) else "smile", sweat=True)
    return None


b.custom(j, k_sig7[0], k_sig7[0] + 0.3, bed7)


def big7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_big7))
    if sc <= 0:
        return None
    x, y = cx + 380, cy + 250
    with at_pop(c, x, y, sc):
        alarm(c, x, y, 80, T, ring=True)
    K.text(c, "动静太大", cx + 380, cy + 420, 56, "hand", RED, clamp01(sc * 2))
    return None


ev(j, k_big7, big7, "tom", 0.8)
ev(j, k_wake7, L.slam_text("醒", cx - 400, cy + 40, 140, RED, j, k_wake7, rot=-8), "kick", 0.9)
b.shots[j].shake = [(k_wake7, 9.0)]

# ================================================================ 屏 8：现在的实验——往睡着的人身上洒点水，醒来说梦里下雨了
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_lab8 = kq(j, wt(13, 0, 0.3), 0)
k_wat8 = nx(j, wt(13, 0, 0.75), k_lab8)
k_cl8 = nx(j, wt(13, 1, 0.5), k_wat8)
k_say8 = nx(j, wt(13, 2, 0.4), k_cl8)
BED8 = (cx - 420, cy + 400)
HIP8 = (BED8[0] + 230, BED8[1] - 20)
CL8 = (cx + 150, cy - 280)
L.note("实验", "梦里下雨了")


def lab8(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, BED8[1], sc):
        bed(c, *BED8, 560)
        sleeper(c, *HIP8, 0.8, T, None, "flat")
        x, y = cx - 420, cy - 380
        p = P((x - 30, y - 60), (x + 30, y - 60), (x + 30, y - 10), (x + 70, y + 60), (x - 70, y + 60), (x - 30, y - 10),
              close=True)
        c.drawPath(p, K.paint("#D3EDDC"))
        c.drawPath(p, wb.marker(GREEN, 6))
        K.text(c, "实验", x + 140, y + 10, 60, "hand", GREEN)
    return None


ev(j, k_lab8, pop_fn(j, k_lab8, lab8), "wood_low", 0.7)


def wat8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_wat8))
    if sc <= 0:
        return None
    x, y = HIP8[0] + 120, HIP8[1] - 330
    with at_pop(c, x, y, sc):
        with K.at(c, x, y, 20):
            box(c, 0, 0, 140, 100, "#CFE0F5", BLUE, 6, 14)
            C.line(c, (60, -10), (130, -50), BLUE, 10)
            c.drawPath(P((-70, -30), (-110, -60), (-110, 20), (-70, 20)), wb.marker(BLUE, 6))
        for i in range(6):
            f = ((T - tb(8, k_wat8)) * 1.4 + i / 6) % 1
            dx = x + 120 + (i % 3) * 22
            c.drawCircle(dx, y + 20 + f * 210, 8, K.paint("#7FB6E8", 1 - f * 0.6))
    return None


ev(j, k_wat8, wat8, "shaker", 0.75)


def cloud8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_cl8))
    if not dream_cloud(c, CL8[0], CL8[1], 640, 440, sc, tail_to=(HIP8[0] - 250, HIP8[1] - 90)):
        return None
    with at_pop(c, CL8[0], CL8[1], sc):
        rc = A.cloud_path(CL8[0] - 20, CL8[1] - 120, 260, 110)
        c.drawPath(rc, K.paint("#C9D2DC"))
        c.drawPath(rc, wb.marker(GRAY, 5))
        for i in range(8):
            f = (T * 1.2 + i / 8) % 1
            x = CL8[0] - 130 + (i * 37) % 240
            C.line(c, (x, CL8[1] - 60 + f * 200), (x - 8, CL8[1] - 40 + f * 200), BLUE, 4, 1 - f)
        x, gy = CL8[0] + 60, CL8[1] + 170
        draw_li(c, x, gy, 0.4, "o", rh=(x + 30, gy - 160))
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(x - 60, gy - 210, 160, 100), 180, 180)
        arc.close()
        c.drawPath(arc, K.paint(RED))
        c.drawPath(arc, wb.marker(BLACK, 4))
    return None


ev(j, k_cl8, cloud8, "pop", 0.7)
ev(j, k_say8, L.pop_bubble("梦里下雨了", cx + 160, cy + 90, j, k_say8, 56, BLUE, tail=-1), "ding", 0.75)

# ================================================================ 屏 9：说回我们自己——老被闹钟骗进梦里；“三步”
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_li9 = kq(j, wt(14, 0, 0.4), 0)
k_3 = nx(j, wt(14, 1, 0.5), k_li9)
GY9 = cy + 420
L.note("三步")


def li9(c, sc, T, cx=cx, cy=cy):
    x = cx - 220
    with at_pop(c, x, GY9, sc):
        C.line(c, (x - 300, GY9), (x + 300, GY9), BLACK, 7)
        draw_li(c, x, GY9, 0.9, "o")
        alarm(c, x + 200, GY9 - 60, 55, T, ring=True)
        dream_cloud(c, x - 100, cy - 300, 300, 220, 1.0)
        big_bell(c, x - 100, cy - 380, 0.6, 15 * math.sin(T * 5))
    return None


ev(j, k_li9, pop_fn(j, k_li9, li9), "wood_low", 0.7)


def three9(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(9, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 300, cy - 200, -4, sc):
        c.drawCircle(0, 0, 180, K.paint("#FFF4D6"))
        c.drawCircle(0, 0, 180, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 120, "hand", L.ACC)
    return None


ev(j, k_3, three9, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 10：做法一——换闹钟：听惯的铃声划掉，换个陌生的
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_h10 = kq(j, wt(15, 0, 0.3), 0)
k_old10 = nx(j, wt(15, 1, 0.4), k_h10)
k_x10 = nx(j, wt(15, 1, 0.85), k_old10)
k_new10 = nx(j, wt(15, 2, 0.5), k_x10)
header(L, j, k_h10, cx, cy, "第一", "换闹钟", ev, pop_fn)
L.note("听惯了", "陌生的")


def old10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_old10))
    if sc <= 0:
        return None
    x, y = cx - 260, cy - 120
    with at_pop(c, x, y, sc):
        alarm(c, x, y, 120, T, ring=T < tb(10, k_x10))
        box(c, x, y + 230, 260, 100, PAPER_W, GRAY, 5, 40)
        K.text(c, "听惯了", x, y + 232, 56, "hand", GRAY)
        if T >= tb(10, k_x10):
            with K.at(c, x, y, 0, pop_scale(T - tb(10, k_x10))):
                c.drawPath(cross(0, 0, 150), wb.marker(RED, 14))
    return None


ev(j, k_old10, old10, "wood_high", 0.7)
b.hit(j, k_x10, "rim", 0.8, "划掉")


def new10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_new10))
    if sc <= 0:
        return None
    x, y = cx + 260, cy - 120
    with at_pop(c, x, y, sc):
        alarm(c, x, y, 120, T, ring=True, color=GREEN)
        for i in range(2):
            ph = (T * 0.8 + i / 2) % 1
            nx_, ny_ = x + 130 + i * 50, y - 120 - ph * 80
            c.drawCircle(nx_, ny_, 14, K.paint(BLUE, 1 - ph))
            C.line(c, (nx_ + 12, ny_), (nx_ + 12, ny_ - 50), BLUE, 5, 1 - ph)
        box(c, x, y + 230, 260, 100, PAPER_W, GREEN, 5, 40)
        K.text(c, "陌生的", x, y + 232, 56, "hand", GREEN)
        c.drawPath(check(x + 160, y + 230, 40), wb.marker(GREEN, 10))
    sparkle(c, x, y, T - tb(10, k_new10), YELLOW, 10, 140, 230)
    return None


ev(j, k_new10, new10, "ding", 0.8)


def li10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_new10) - 0.4)
    if sc <= 0:
        return None
    x, gy = cx, cy + 480
    with at_pop(c, x, gy, sc):
        draw_li(c, x, gy, 0.7, "o")
        K.text(c, "!", x + 70, gy - 290 * 0.7 - 60, 70, "hand", RED)
    return None


b.custom(j, k_new10, k_new10 + 0.3, li10)

# ================================================================ 屏 11：做法二——闹钟放远一点，得下床才能关
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_h11 = kq(j, wt(16, 0, 0.3), 0)
k_bed11 = nx(j, wt(16, 0, 0.6), k_h11)
k_clk11 = nx(j, wt(16, 0, 0.9), k_bed11)
k_walk11 = nx(j, wt(16, 1, 0.3), k_clk11)
k_off11 = nx(j, wt(16, 1, 0.8), k_walk11)
header(L, j, k_h11, cx, cy, "第二", "放远一点", ev, pop_fn)
GY11 = cy + 380
L.note("得下床")


def bed11(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 300, GY11, sc):
        C.line(c, (cx - 560, GY11 + 110), (cx + 560, GY11 + 110), BLACK, 6)
        bed(c, cx - 540, GY11, 460)
    return None


ev(j, k_bed11, pop_fn(j, k_bed11, bed11), "wood_low", 0.7)


def clk11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_clk11))
    if sc <= 0:
        return None
    x, y = cx + 400, cy - 60
    with at_pop(c, x, y, sc):
        c.drawRect(skia.Rect.MakeXYWH(x - 130, y + 70, 260, 26), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(x - 130, y + 70, 260, 26), wb.marker("#A9773E", 6))
        alarm(c, x, y - 10, 60, T, ring=T < tb(11, k_off11))
    return None


ev(j, k_clk11, clk11, "wood_high", 0.7)


def walk11(c, kk, T, cx=cx, cy=cy):
    t0 = tb(11, k_walk11)
    if T < t0:
        hx, hy_ = cx - 310, GY11 - 20
        sleeper(c, hx, hy_, 0.75, T, None, "flat")
        return None
    f = ease_in_out(clamp01((T - t0) / max(0.4, tb(11, k_off11) - t0)))
    x = lerp(cx - 200, cx + 300, f)
    bob = -abs(math.sin((T - t0) * 9)) * 12 * (1 - (f >= 1))
    hy = GY11 + 110 - 290 * 0.85
    reach = f >= 1
    draw_li(c, x, GY11 + 110 + bob, 0.85, "flat" if not reach else "smile",
            rh=(x + 110, hy + 10) if reach else None)
    for i in range(4):
        if f > i / 4:
            fx = cx - 220 + i * 130
            c.drawOval(skia.Rect.MakeXYWH(fx - 20, GY11 + 130 + (i % 2) * 20, 40, 18), K.paint(GRAY, 0.6))
    if T >= t0:
        K.text(c, "得下床", cx - 20, cy + 0, 64, "hand", L.ACC, clamp01((T - t0) / 0.3))
    return None


b.custom(j, k_bed11, k_bed11 + 0.3, walk11)
b.hit(j, k_walk11, "shaker", 0.7, "下床走过去")
b.hit(j, k_off11, "ding", 0.8, "关掉闹钟")

# ================================================================ 屏 12：做法三——睡前弄舒服：温度合适、少喝水、手机静音
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_h12 = kq(j, wt(17, 0, 0.3), 0)
k_it12 = [nx(j, wt(17, 1, 0.7), k_h12)]
k_it12.append(nx(j, wt(17, 2, 0.4), k_it12[0]))
k_it12.append(nx(j, wt(17, 3, 0.4), k_it12[1]))
header(L, j, k_h12, cx, cy, "第三", "弄舒服", ev, pop_fn)
IT12 = ["温度合适", "少喝水", "手机静音"]
L.note(*IT12, "24°")


def it12(c, kk, T, cx=cx, cy=cy):
    for i, s_ in enumerate(IT12):
        g = pop_scale(T - tb(12, k_it12[i]))
        if g <= 0:
            continue
        x, y = cx, cy - 300 + i * 260
        with K.at(c, x, y, (-2, 2, -1)[i], g):
            box(c, 0, 0, 800, 220, PAPER_W, (ORANGE, BLUE, NIGHT)[i], 6, 20)
            ix = -290
            if i == 0:
                c.drawRoundRect(skia.Rect.MakeXYWH(ix - 18, -80, 36, 130), 18, 18, K.paint(PAPER_W))
                c.drawRoundRect(skia.Rect.MakeXYWH(ix - 18, -80, 36, 130), 18, 18, wb.marker(BLACK, 5))
                c.drawCircle(ix, 60, 30, K.paint(RED))
                C.line(c, (ix, 50), (ix, -20), RED, 14)
                K.text(c, "24°", ix + 80, -40, 44, "hand", RED)
            elif i == 1:
                p = P((ix - 45, -70), (ix + 45, -70), (ix + 35, 70), (ix - 35, 70), close=True)
                c.drawPath(p, K.paint(PAPER_W))
                c.drawRect(skia.Rect.MakeXYWH(ix - 37, 30, 74, 38), K.paint("#BFDDF7"))
                c.drawPath(p, wb.marker(BLUE, 6))
            else:
                box(c, ix, 0, 90, 150, "#2E2A28", BLACK, 5, 14)
                big_bell(c, ix, -45, 0.32)
                C.line(c, (ix - 45, -60), (ix + 45, 40), RED, 9)
            K.text(c, s_, 30, 0, 70, "hand", BLACK)
            c.drawPath(check(310, 0, 40), wb.marker(GREEN, 10))
    return None


ev(j, k_it12[0], it12, "pop", 0.7)
b.hit(j, k_it12[1], "pop", 0.7, "少喝水")
b.hit(j, k_it12[2], "pop", 0.7, "手机静音")

# ================================================================ 屏 13：这样看梦——梦护着你的觉，你也照顾它；第二天有精神
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_bed13 = 0
k_heart13 = nx(j, wt(18, 0, 0.7), k_bed13)
k_sun13 = nx(j, wt(18, 1, 0.3), k_heart13)
k_txt13 = nx(j, wt(18, 1, 0.8), k_sun13)
BED13 = (cx - 480, cy - 40)
HIP13 = (BED13[0] + 230, BED13[1] - 20)
L.note("有精神")


def bed13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_bed13))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED13[1], sc):
        bed(c, *BED13, 520)
        sleeper(c, *HIP13, 0.8, T, None, "smile")
        guardian(c, cx + 230, cy - 300, 1.0, T)
        moon(c, cx + 450, cy - 470, 40)
    return None


ev(j, k_bed13, bed13, "pop", 0.7)


def heart13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_heart13))
    if sc <= 0:
        return None
    x, y = cx + 30, cy - 330
    with K.at(c, x, y - 8 * math.sin(T * 3), 0, sc):
        c.drawPath(C.heart_path(0, 0, 50), K.paint("#F6C3BE"))
        c.drawPath(C.heart_path(0, 0, 50), wb.marker(RED, 6))
    return None


ev(j, k_heart13, heart13, "ding", 0.75)


def sun13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_sun13))
    if sc <= 0:
        return None
    gy = cy + 470
    with at_pop(c, cx + 200, gy, sc):
        C.line(c, (cx - 200, gy), (cx + 560, gy), BLACK, 6)
        sun(c, cx + 430, cy + 150, 60)
        hy = gy - 290 * 0.9
        draw_li(c, cx + 150, gy, 0.9, "smile", lh=(cx + 50, hy - 50), rh=(cx + 250, hy - 50), bag=True)
    sparkle(c, cx + 150, gy - 300, T - tb(13, k_sun13), YELLOW, 10, 120, 210)
    return None


ev(j, k_sun13, sun13, "wood_high", 0.75)
ev(j, k_txt13, L.slam_text("有精神", cx - 300, cy + 300, 110, L.ACC, j, k_txt13, rot=-5), "kick", 0.85)
b.shots[j].shake = [(k_txt13, 7.0)]

# ================================================================ 屏 14：评论区——“闹钟变成了消防车”；今晚先早点睡；下一讲预告
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_box14 = kq(j, wt(19, 0, 0.4), 0)
k_type14 = nx(j, wt(20, 0, 0.5), k_box14)
k_likes14 = nx(j, wt(20, 1, 0.5), k_type14)
k_sleep14 = nx(j, wt(21, 2, 0.3), k_likes14)
k_n = nx(j, wt(22, 0, 0.1), k_sleep14)
L.note("评论区", "闹钟变成了消防车", "发送", "+1", "早点睡")


def input14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_box14))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(14, k_type14):
            s_ = "闹钟变成了消防车"
            g = clamp01((T - tb(14, k_type14)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], x - w / 2 + 40, y + 2, 58, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, L.ACC)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
        for i in range(6):
            g = pop_scale(T - tb(14, k_likes14) - i * 0.15)
            if g > 0:
                with K.at(c, x - 330 + i * 120, y + 140, 0, g):
                    K.rr(c, 0, 0, 100, 60, 30, "#FFF4D6")
                    K.text(c, "+1", 0, 2, 40, "hand", L.ACC)
    return None


ev(j, k_box14, input14, "wood_high", 0.7)
b.hit(j, k_type14, "pop", 0.6, "打字")
b.hit(j, k_likes14, "clap", 0.75, "好多人加一")


def sleep14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_sleep14))
    if sc <= 0:
        return None
    bx, by = cx - 300, cy + 330
    with at_pop(c, cx, by, sc):
        bed(c, bx, by, 520)
        sleeper(c, bx + 230, by - 20, 0.8, T, None, "smile")
        moon(c, cx + 330, cy - 40, 60)
        K.text(c, "早点睡", cx + 330, cy + 110, 70, "hand", NIGHT)
        zzz(c, bx + 40, by - 150, T, tb(14, k_sleep14))
    return None


ev(j, k_sleep14, sleep14, "ding", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "梦要是愿望，为什么还会做噩梦？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=6, notes=NOTES)
L.export(globals())
