"""《梦的解析》02 愿望的满足：缺什么，为什么梦里就来什么？（白板手绘 + AI 旁白，竖屏 2:3）

比喻贯穿：梦像夜里替你补货的小店——白天缺什么，梦里就上架什么。
- 开场：碎屏旧手机、彩票球滚出“中”、新手机闪光，配音“梦里中大奖”逐字砸下；
- 痛点：小李睡着，梦泡泡里一张大奖支票和新手机；一睁眼泡泡没了，床头还是碎屏手机；
- 身边的例子（drop 在第 2 屏）：加班到十点饿着 → 梦里一大桌外卖砸下；方案被否 → 梦里领导鼓掌；赖床 → 梦里已经坐上地铁；
- 书中：弗洛伊德与书；学医的年轻人被房东叫起 → 梦见已躺在医院病床、床头挂名牌 → 接着睡；“图省事的梦”印章；
  南极帐篷里梦大餐、小孩梦樱桃；“愿望的满足”与三个空格被梦补上；为什么要补：翻来覆去 → 满足后睡踏实；
- 现在怎么看：书 vs 研究在争论，放大镜照“最近缺什么”；
- 三步：记下梦里得到什么（三个勾选框）、连到白天的事、今天给自己一点（七点吃饭、十一点睡）；大餐变成便条；评论区与下一讲。
文案与出处见 mengjie/PLAN.md「### 02」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, NOTE_FILL, PAPER_W, SKIN, WOOD, at_pop, bed, box, draw_freud, draw_girl,
                         dream_cloud, moon, sleeper, sparkle, star, sun)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross, rect


def phone(c, x, y, s=1.0, cracked=False, shiny=False, alpha=1.0):
    """手机：(x, y) 为中心。"""
    with K.at(c, x, y, 0, s):
        box(c, 0, 0, 150, 260, "#2E2A28", BLACK, 5, 22, alpha)
        box(c, 0, -6, 128, 210, "#CFE0F5" if shiny else "#9AA6B8", BLUE if shiny else GRAY, 3, 10, alpha)
        if cracked:
            c.drawPath(P((-50, -80), (-10, -30), (-30, 10), (20, 60), (10, 90)), wb.marker(BLACK, 4, alpha))
            c.drawPath(P((-10, -30), (50, -50)), wb.marker(BLACK, 4, alpha))
        if shiny:
            C.line(c, (-40, -70), (-10, -100), PAPER_W, 8, alpha)


def _hook(H, j, cx, cy, acc):
    """开场：碎屏旧手机 → 彩票球滚出“中” → 新手机闪光；随后“梦里中大奖”逐字砸下。"""
    b = H.b
    H.note("中")

    def old(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc > 0:
            with K.at(c, cx - 330, cy - 200, -8, sc):
                phone(c, 0, 0, 1.1, cracked=True)
        return None
    b.custom(j, 0, 0.3, old, sfx="wood_low", gain=0.7)

    def ball(c, kk, T):
        dt = T - H.tb(j, 1)
        if dt < 0:
            return None
        f = ease_out(clamp01(dt / 0.35))
        x = lerp(cx - 120, cx, f)
        with K.at(c, x, cy - 200, f * 360, pop_scale(dt)):
            c.drawCircle(0, 0, 90, K.paint("#FFD27A"))
            c.drawCircle(0, 0, 90, wb.marker(ORANGE, 8))
            K.text(c, "中", 0, 4, 100, "hand", RED)
        return None
    b.custom(j, 1, 1.3, ball, sfx="tom", gain=0.75)

    def new(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        with K.at(c, cx + 330, cy - 200, 6, pop_scale(dt)):
            phone(c, 0, 0, 1.2, shiny=True)
        sparkle(c, cx + 330, cy - 200, dt, YELLOW, 10, 150, 240)
        return None
    b.custom(j, 2, 2.3, new, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("02", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第三章“梦是愿望的满足”。",
    "书中例子：医学生被房东叫起，梦见已躺在医院病床、床头挂着名牌，于是接着睡（图省事的梦）；南极探险队员常梦见丰盛饭菜；小孩梦见吃光樱桃。",
    "现在的研究不认为每个梦都在满足愿望；片中交代为书里的看法。小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：梦泡泡里大奖支票与新手机；一睁眼泡泡没了，床头碎屏手机
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_bed = 0
k_cl = nx(j, wt(0, 1, 0.3), k_bed + 1)
k_ph = nx(j, wt(0, 2, 0.4), k_cl)
k_wake = nx(j, wt(1, 0, 0.3), k_ph)
k_old = nx(j, wt(1, 2, 0.3), k_wake)
BED1 = (cx - 360, cy + 320)
HIP1 = (BED1[0] + 230, BED1[1] - 20)
CL1 = (cx + 110, cy - 260)
L.note("大奖", "500万", "碎着", "月底")


def scene1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_bed))
    if sc <= 0:
        return None
    woke = T >= tb(1, k_wake)
    with at_pop(c, cx, BED1[1], sc):
        bed(c, *BED1, 560)
        sleeper(c, *HIP1, 0.8, T, tb(1, k_wake), "sad" if woke else "smile")
        box(c, BED1[0] + 660, BED1[1] + 10, 170, 140, WOOD, "#A9773E", 6, 8)
        with K.at(c, BED1[0] + 660, BED1[1] - 130, -6, 0.75):
            phone(c, 0, 0, 1.0, cracked=True)
        box(c, cx - 380, cy - 480, 200, 80, PAPER_W, RED, 5, 12)
        K.text(c, "月底", cx - 380, cy - 478, 44, "hand", RED)
    return None


ev(j, k_bed, scene1, "wood_low", 0.7)


def cloud1(c, kk, T, cx=cx, cy=cy):
    out = 1 - ease_in_out(clamp01((T - tb(1, k_wake)) / 0.3))
    sc = pop_scale(T - tb(1, k_cl)) * out
    if not dream_cloud(c, CL1[0], CL1[1], 760, 500, sc, tail_to=(HIP1[0] - 280, HIP1[1] - 80)):
        return None
    with at_pop(c, CL1[0], CL1[1], sc):
        with K.at(c, CL1[0] - 120, CL1[1] - 20, -4):
            box(c, 0, 0, 360, 190, "#FFF4D6", ORANGE, 7, 10)
            K.text(c, "大奖", -90, -40, 60, "hand", RED)
            K.text(c, "500万", 40, 40, 64, "hand", BLACK)
        if T >= tb(1, k_ph):
            g = pop_scale(T - tb(1, k_ph))
            with K.at(c, CL1[0] + 210, CL1[1] + 10, 8, g * 0.8):
                phone(c, 0, 0, 1.0, shiny=True)
            sparkle(c, CL1[0] + 210, CL1[1], T - tb(1, k_ph), YELLOW, 8, 110, 180)
    return None


ev(j, k_cl, cloud1, "pop", 0.75)
b.hit(j, k_ph, "ding", 0.75, "梦里挑新手机")
b.hit(j, k_wake, "kick", 0.85, "一睁眼")
b.shots[j].shake = [(k_wake, 8.0)]
ev(j, k_old, L.stamp("碎着", BED1[0] + 660, BED1[1] - 330, 60, j, k_old, rot=8), "rim", 0.8)

# ================================================================ 屏 2：加班到十点饿着 → drop：梦里一大桌外卖砸下
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_desk = 1
k_gu = kq(j, wt(3, 0, 0.7), k_desk + 1)
k_cl2 = max(k_gu + 1, KD - 3)
GY2 = cy + 430
L.note("22:00", "咕", "外卖")


def desk2(c, sc, T, cx=cx, cy=cy):
    x = cx - 280
    with at_pop(c, x, GY2, sc):
        draw_li(c, x, GY2, 0.85, "sad" if T >= tb(2, k_gu) else "flat", lh=(x + 60, GY2 - 150), rh=(x + 110, GY2 - 150))
        c.drawRect(skia.Rect.MakeXYWH(x - 60, GY2 - 160, 420, 30), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(x - 60, GY2 - 160, 420, 30), wb.marker("#A9773E", 6))
        for lx in (x - 40, x + 340):
            C.line(c, (lx, GY2 - 130), (lx, GY2), "#A9773E", 8)
        box(c, x + 200, GY2 - 250, 200, 140, "#2E2A28", BLACK, 5, 8)
        box(c, cx - 420, cy - 300, 220, 90, PAPER_W, BLACK, 6, 14)
        K.text(c, "22:00", cx - 420, cy - 298, 54, "black", RED)
    return None


ev(j, k_desk, pop_fn(j, k_desk, desk2), "wood_low", 0.7)
ev(j, k_gu, L.pop_text("咕", cx - 200, GY2 - 330, 80, ORANGE, j, k_gu), "tom", 0.75)
CL2 = (cx + 230, cy - 230)


def feast2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_cl2))
    if not dream_cloud(c, CL2[0], CL2[1], 620, 520, sc, tail_to=(cx - 280, GY2 - 330)):
        return None
    with at_pop(c, CL2[0], CL2[1], sc):
        land = tb(2, KD)
        g = C.slam_scale(T - land)
        if g > 0:
            with K.at(c, CL2[0], CL2[1] + 40, 0, g):
                for i, (dx, dy) in enumerate(((-150, 30), (0, 60), (150, 30), (-75, -60), (75, -60))):
                    box(c, dx, dy, 120, 90, ("#F6C3BE", "#FFF1A8", "#D3EDDC", "#CFE0F5", "#F6C3BE")[i], BLACK, 5, 10)
                    C.line(c, (dx - 40, dy - 20), (dx + 40, dy - 20), GRAY, 4)
                for i in range(3):
                    ph = (T * 0.8 + i / 3) % 1
                    sx = -100 + i * 100
                    c.drawPath(P((sx, -120 - ph * 10), (sx + 18, -160 - ph * 40), (sx - 8, -200 - ph * 50)),
                               wb.marker(GRAY, 5, 1 - ph))
    return None


ev(j, k_cl2, feast2, "pop", 0.7)
ev(j, KD, L.slam_text("外卖", cx + 230, cy + 120, 130, RED, j, KD, rot=-6), "kick", 0.95)

# ================================================================ 屏 3：方案被否 → 梦里领导当众鼓掌
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_no = kq(j, wt(4, 0, 0.6), 0)
k_cl3 = nx(j, wt(4, 1, 0.2), k_no)
k_clap = nx(j, wt(4, 1, 0.8), k_cl3)
GY3 = cy + 430
L.note("方案", "否", "干得好")


def doc3(c, sc, T, cx=cx, cy=cy):
    x = cx - 300
    with at_pop(c, x, GY3, sc):
        draw_boss(c, x - 60, GY3, 0.7, mood="flat")
        with K.at(c, x + 150, GY3 - 260, -5):
            box(c, 0, 0, 200, 250, PAPER_W, BLACK, 6, 8)
            K.text(c, "方案", 0, -70, 50, "hand", BLACK)
            for r in range(3):
                C.line(c, (-70, -10 + r * 40), (70 - r * 20, -10 + r * 40), GRAY, 5)
    return None


ev(j, k_no, pop_fn(j, k_no, doc3), "wood_low", 0.7)
ev(j, k_no, L.stamp("否", cx - 150, cy + 100, 90, j, k_no, rot=-10))
b.hit(j, k_no, "rim", 0.8, "方案被否")
CL3 = (cx + 200, cy - 220)


def cloud3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_cl3))
    if not dream_cloud(c, CL3[0], CL3[1], 660, 560, sc, tail_to=(cx - 300, cy - 50)):
        return None
    with at_pop(c, CL3[0], CL3[1], sc):
        x, y = CL3[0] - 100, CL3[1] + 200
        clap = T >= tb(3, k_clap)
        hy = y - 290 * 0.6
        ph = math.sin((T - tb(3, k_clap)) * 14) if clap else 0
        draw_boss(c, x, y, 0.6, lh=(x - 10 + 14 * ph, hy + 100), rh=(x + 30 - 14 * ph, hy + 100), mood="smile" if clap else "flat")
        draw_li(c, x + 220, y, 0.6, "smile")
        if clap:
            sparkle(c, x + 10, hy + 90, T - tb(3, k_clap), YELLOW, 8, 40, 90)
    return None


ev(j, k_cl3, cloud3, "pop", 0.7)
ev(j, k_clap, L.pop_bubble("干得好", CL3[0] - 60, CL3[1] - 160, j, k_clap, 60, RED, tail=-1), "clap", 0.8)

# ================================================================ 屏 4：赖床 → 梦里已经坐上地铁
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_bed4 = 0
k_cl4 = nx(j, wt(5, 1, 0.2), k_bed4 + 1)
k_metro = nx(j, wt(5, 2, 0.4), k_cl4)
BED4 = (cx - 380, cy + 360)
HIP4 = (BED4[0] + 230, BED4[1] - 20)
CL4 = (cx + 130, cy - 230)
L.note("07:30", "地铁")


def scene4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_bed4))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED4[1], sc):
        bed(c, *BED4, 560)
        sleeper(c, *HIP4, 0.8, T, None, "smile")
        x, y = BED4[0] + 650, BED4[1] - 60
        shake = 6 * math.sin(T * 40)
        with K.at(c, x + shake, y, 0):
            c.drawCircle(0, 0, 70, K.paint(PAPER_W))
            c.drawCircle(0, 0, 70, wb.marker(RED, 8))
            K.text(c, "07:30", 0, 4, 34, "black", RED)
            for sg in (-1, 1):
                c.drawCircle(sg * 50, -66, 18, K.paint(RED))
    return None


ev(j, k_bed4, scene4, "wood_low", 0.7)


def cloud4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_cl4))
    if not dream_cloud(c, CL4[0], CL4[1], 760, 540, sc, tail_to=(HIP4[0] - 280, HIP4[1] - 80)):
        return None
    with at_pop(c, CL4[0], CL4[1], sc):
        x, y = CL4[0], CL4[1] + 30
        go = ease_out(clamp01((T - tb(4, k_metro)) / 0.6)) if T >= tb(4, k_metro) else 0.0
        with K.at(c, x - 40 * go, y, 0):
            box(c, 0, 0, 520, 230, "#DCE6F2", BLUE, 7, 40)
            for i in range(3):
                box(c, -160 + i * 160, -30, 110, 80, PAPER_W, BLUE, 4, 10)
            draw_li(c, -160, 90, 0.42, "smile", bag=True)
            K.text(c, "地铁", 160, 80, 50, "hand", BLUE)
        for i in range(3):
            C.line(c, (x + 300 + i * 20, y - 40 + i * 40), (x + 360 + i * 20, y - 40 + i * 40), GRAY, 5, go)
    return None


ev(j, k_cl4, cloud4, "pop", 0.7)
b.hit(j, k_metro, "shaker", 0.7, "地铁开动")

# ================================================================ 屏 5：弗洛伊德与书；学医的年轻人，房东敲门“该去医院了”
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_fr = kq(j, wt(6, 0, 0.3), 0)
k_bk = nx(j, wt(6, 1, 0.3), k_fr)
k_yg = nx(j, wt(7, 0, 0.6), k_bk)
k_knock = nx(j, wt(7, 1, 0.4), k_yg)
L.note("梦的解析", "学医", "该去医院了")


def fr5(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 330, cy - 40
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 0.8)
    return None


ev(j, k_fr, pop_fn(j, k_fr, fr5), "wood_low", 0.7)


def bk5(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(5, k_bk))
    if sc <= 0:
        return None
    with K.at(c, cx - 100, cy - 330, 6, sc):
        box(c, 0, 0, 220, 290, NIGHT, BLACK, 6, 10)
        K.text(c, "梦的", 0, -50, 54, "serif_black", "#FFE39A")
        K.text(c, "解析", 0, 20, 54, "serif_black", "#FFE39A")
        moon(c, 0, 100, 28)
    return None


ev(j, k_bk, bk5, "ding", 0.75)
BED5 = (cx - 60, cy + 380)


def young5(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx + 150, BED5[1], sc):
        bed(c, *BED5, 520)
        sleeper(c, BED5[0] + 230, BED5[1] - 20, 0.75, T, None, "flat")
        hx = BED5[0] + 230 - 290 * 0.75 + 120 * 0.75
        for sg in (-1, 1):
            c.drawCircle(hx + sg * 14, BED5[1] - 20 - 6, 10, wb.marker(BLACK, 4))
        box(c, BED5[0] + 120, BED5[1] - 190, 140, 60, PAPER_W, BLUE, 4, 30)
        K.text(c, "学医", BED5[0] + 120, BED5[1] - 188, 40, "sans_medium", BLUE)
    return None


ev(j, k_yg, pop_fn(j, k_yg, young5), "wood_low", 0.7)


def door5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_knock))
    if sc <= 0:
        return None
    x, y = cx + 470, cy + 380
    with at_pop(c, x, y, sc):
        c.drawRect(skia.Rect.MakeXYWH(x - 90, y - 400, 180, 400), K.paint("#F1E3CB"))
        c.drawRect(skia.Rect.MakeXYWH(x - 90, y - 400, 180, 400), wb.marker("#A9773E", 8))
        draw_girl(c, x - 10, y, 1.0, "flat")
        for i in range(2):
            ph = ((T - tb(5, k_knock)) * 2 + i * 0.5) % 1
            C.line(c, (x - 130 - ph * 30, y - 250 - i * 30), (x - 160 - ph * 30, y - 260 - i * 30), BLACK, 5, 1 - ph)
    return None


ev(j, k_knock, door5, "wood_high", 0.75)
ev(j, k_knock, L.pop_bubble("该去医院了", cx + 250, cy - 120, j, k_knock, 52, BLACK, tail=1), None)

# ================================================================ 屏 6：梦里已躺在医院病床，床头挂名牌；“接着睡”
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_cl6 = kq(j, wt(8, 0, 0.4), 0)
k_tag = nx(j, wt(8, 1, 0.5), k_cl6)
k_ok = nx(j, wt(9, 0, 0.6), k_tag)
k_zz = nx(j, wt(9, 1, 0.5), k_ok)
BED6 = (cx - 330, cy + 400)
CL6 = (cx + 60, cy - 200)
L.note("医院", "医学生", "Z", "接着睡")


def sleep6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, 0))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED6[1], sc):
        bed(c, *BED6, 520)
        sleeper(c, BED6[0] + 230, BED6[1] - 20, 0.75, T, None, "smile")
        if T >= tb(6, k_zz):
            for i in range(3):
                f = ((T - tb(6, k_zz)) * 0.7 + i / 3) % 1
                K.text(c, "Z", BED6[0] + 40 + f * 60, BED6[1] - 150 - f * 160, 50 + i * 10, "hand", NIGHT, 1 - f)
    return None


b.custom(j, 0, 0.3, sleep6)


def cloud6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_cl6))
    if not dream_cloud(c, CL6[0], CL6[1], 860, 560, sc, tail_to=(BED6[0] + 60, BED6[1] - 120)):
        return None
    with at_pop(c, CL6[0], CL6[1], sc):
        x, y = CL6[0] - 60, CL6[1] + 120
        c.drawRect(skia.Rect.MakeXYWH(x - 260, y - 20, 520, 40), K.paint(PAPER_W))
        c.drawRect(skia.Rect.MakeXYWH(x - 260, y - 20, 520, 40), wb.marker(BLUE, 6))
        for lx in (x - 250, x + 250):
            C.line(c, (lx, y + 20), (lx, y + 110), BLUE, 7)
        C.line(c, (x - 260, y - 120), (x - 260, y + 110), BLUE, 9)
        with K.at(c, x + 20, y - 40, -90):
            draw_li(c, 0, 0, 0.45, "smile")
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 120, y - 50, 360, 46), 20, 20, K.paint("#FFFFFF"))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 120, y - 50, 360, 46), 20, 20, wb.marker(BLUE, 5))
        c.drawPath(P((x + 330, y - 230), (x + 330, y - 130), (x + 300, y - 130)), wb.marker(RED, 8))
        c.drawPath(P((x + 305, y - 205), (x + 355, y - 205)), wb.marker(RED, 8))
        c.drawPath(P((x + 330, y - 230), (x + 330, y - 180)), wb.marker(RED, 8))
        K.text(c, "医院", x + 420, y - 180, 48, "hand", RED)
        if T >= tb(6, k_tag):
            g = pop_scale(T - tb(6, k_tag))
            with K.at(c, x - 330, y - 160, -6, g):
                C.line(c, (0, -70), (40, -110), GRAY, 4)
                box(c, 0, 0, 200, 110, PAPER_W, BLACK, 5, 8)
                K.text(c, "医学生", 0, 2, 46, "hand", BLACK)
    return None


ev(j, k_cl6, cloud6, "pop", 0.75)
b.hit(j, k_tag, "ding", 0.75, "床头挂名牌")
ev(j, k_ok, L.pop_bubble("人已经在医院了", cx + 230, cy + 120, j, k_ok, 46, BLACK, tail=-1), "pop", 0.65)
ev(j, k_zz, L.slam_text("接着睡", cx + 260, cy + 300, 100, NIGHT, j, k_zz, rot=-4), "kick", 0.8)

# ================================================================ 屏 7：“图省事的梦”印章，被子一拉
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_lazy = kq(j, wt(10, 0, 0.3), 0)
k_st = nx(j, wt(10, 0, 0.85), k_lazy)
L.note("图省事的梦", "该起床了", "已经到了")


def lazy7(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy + 300, sc):
        draw_freud(c, cx - 330, cy + 380, 0.9, "smile")
        bed(c, cx - 120, cy + 300, 520)
        sleeper(c, cx + 110, cy + 280, 0.75, T, None, "smile")
        box(c, cx + 200, cy - 20, 300, 100, PAPER_W, RED, 5, 40)
        K.text(c, "该起床了", cx + 200, cy - 18, 50, "hand", RED)
        c.drawPath(wb.arrow((cx + 200, cy + 40), (cx + 200, cy + 150), 0.0, 30), wb.marker(GRAY, 6))
        box(c, cx + 200, cy + 200, 300, 90, "#E4E2F6", NIGHT, 5, 40)
        K.text(c, "已经到了", cx + 200, cy + 202, 50, "hand", NIGHT)
    return None


ev(j, k_lazy, pop_fn(j, k_lazy, lazy7), "wood_low", 0.7)
ev(j, k_st, L.stamp("图省事的梦", cx, cy - 330, 90, j, k_st, color=RED, rot=-5), "kick", 0.9)
b.shots[j].shake = [(k_st, 8.0)]

# ================================================================ 屏 8：南极帐篷里梦大餐；小孩梦樱桃
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_tent = kq(j, wt(11, 1, 0.3), 0)
k_feast = nx(j, wt(11, 3, 0.4), k_tent)
k_kid = nx(j, wt(12, 0, 0.6), k_feast)
k_cherry = nx(j, wt(12, 1, 0.5), k_kid)
L.note("南极", "饿", "樱桃")
C8L, C8R = (cx - 290, cy - 280), (cx + 290, cy - 280)


def tent8(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 290, cy + 380
    with at_pop(c, x, y, sc):
        c.drawPath(P((x - 240, y), (x - 60, y - 40), (x + 120, y - 10), (x + 240, y), close=True), K.paint("#FFFFFF"))
        tent = P((x - 160, y), (x, y - 260), (x + 160, y), close=True)
        c.drawPath(tent, K.paint("#F2B705"))
        c.drawPath(tent, wb.marker(ORANGE, 8))
        c.drawPath(P((x - 40, y), (x, y - 120), (x + 40, y), close=True), K.paint("#3A3F48"))
        for i in range(10):
            f = (T * 0.3 + i / 10) % 1
            c.drawCircle(x - 220 + (i * 47) % 440, y - 400 + f * 380, 6, K.paint("#9AA6B8", 1 - f * 0.5))
        K.text(c, "南极", x, y + 70, 46, "sans_medium", BLUE)
        K.text(c, "饿", x + 170, y - 230, 60, "hand", ORANGE)
    return None


ev(j, k_tent, pop_fn(j, k_tent, tent8), "wood_low", 0.7)


def feast8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_feast))
    if not dream_cloud(c, *C8L, 480, 420, sc, tail_to=(cx - 290, cy + 130)):
        return None
    with at_pop(c, *C8L, sc):
        x, y = C8L
        c.drawOval(skia.Rect.MakeXYWH(x - 170, y + 20, 340, 80), K.paint(PAPER_W))
        c.drawOval(skia.Rect.MakeXYWH(x - 170, y + 20, 340, 80), wb.marker(BLACK, 6))
        chick = skia.Path()
        chick.addOval(skia.Rect.MakeXYWH(x - 100, y - 60, 200, 120))
        c.drawPath(chick, K.paint("#E0A21B"))
        c.drawPath(chick, wb.marker(ORANGE, 6))
        for sg in (-1, 1):
            C.line(c, (x + sg * 90, y - 30), (x + sg * 130, y - 70), PAPER_W, 14)
            C.line(c, (x + sg * 90, y - 30), (x + sg * 130, y - 70), ORANGE, 4)
        for i in range(3):
            ph = (T * 0.8 + i / 3) % 1
            c.drawPath(P((x - 60 + i * 60, y - 80 - ph * 10), (x - 45 + i * 60, y - 120 - ph * 30)), wb.marker(GRAY, 5, 1 - ph))
    return None


ev(j, k_feast, feast8, "ding", 0.75)


def kid8(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 290, cy + 420
    with at_pop(c, x, y, sc):
        draw_girl(c, x, y, 0.9, "smile" if T >= tb(8, k_cherry) else "flat")
    return None


ev(j, k_kid, pop_fn(j, k_kid, kid8), "wood_high", 0.7)


def cherry8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_cherry))
    if not dream_cloud(c, *C8R, 480, 420, sc, tail_to=(cx + 290, cy + 150)):
        return None
    with at_pop(c, *C8R, sc):
        x, y = C8R
        c.drawPath(P((x - 120, y + 60), (x - 100, y + 120), (x + 100, y + 120), (x + 120, y + 60), close=True), K.paint(WOOD))
        c.drawPath(P((x - 120, y + 60), (x - 100, y + 120), (x + 100, y + 120), (x + 120, y + 60), close=True),
                   wb.marker("#A9773E", 6))
        for i, (dx, dy) in enumerate(((-70, 30), (-20, 10), (30, 30), (80, 15), (0, -30), (-50, -20), (50, -25))):
            C.line(c, (x + dx, y + dy), (x + dx + 15, y + dy - 60), GREEN, 4)
            c.drawCircle(x + dx, y + dy, 26, K.paint("#E5484D"))
            c.drawCircle(x + dx, y + dy, 26, wb.marker(RED, 4))
    sparkle(c, C8R[0], C8R[1], T - tb(8, k_cherry), YELLOW, 8, 140, 220)
    return None


ev(j, k_cherry, cherry8, "ding", 0.8)

# ================================================================ 屏 9：“愿望的满足”；三个空格（想要的、缺的、躲的），梦逐个补上
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_card = kq(j, wt(13, 1, 0.5), 0)
k_slot = [nx(j, wt(14, 0, 0.2), k_card)]
k_slot += [cap(j, k_slot[0] + 1), cap(j, k_slot[0] + 2)]
k_fill = nx(j, wt(14, 2, 0.4), k_slot[2])
SLOTS = ["想要的", "缺的", "躲的"]
L.note("愿望的满足", "补上", *SLOTS)


def card9(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(9, k_card))
    if sc <= 0:
        return None
    with K.at(c, cx, cy - 420, -2, sc):
        box(c, 0, 0, 760, 180, PAPER_W, NIGHT, 9, 30)
        K.text(c, "愿望的满足", 0, 4, 110, "hand", NIGHT)
    return None


ev(j, k_card, card9, "kick", 0.85)
b.shots[j].shake = [(k_card, 7.0)]


def slots9(c, kk, T, cx=cx, cy=cy):
    for i, s_ in enumerate(SLOTS):
        g = pop_scale(T - tb(9, k_slot[i]))
        if g <= 0:
            continue
        x, y = cx - 330 + i * 330, cy + 20
        with K.at(c, x, y, 0, g):
            K.text(c, s_, 0, -170, 56, "hand", BLACK)
            filled = T >= tb(9, k_fill) + i * 0.15
            box(c, 0, 0, 240, 240, "#FFF4D6" if filled else PAPER_W, ORANGE if filled else GRAY, 7, 20)
            if not filled:
                K.text(c, "？", 0, 4, 110, "hand", GRAY)
            elif i == 0:
                star(c, 0, 0, 70)
            elif i == 1:
                moon(c, 0, 0, 70)
            else:
                c.drawPath(C.heart_path(0, 0, 70), K.paint("#F6C3BE"))
                c.drawPath(C.heart_path(0, 0, 70), wb.marker(RED, 6))
    if T >= tb(9, k_fill):
        x, y = cx, cy + 370
        dream_cloud(c, x, y, 560, 200, pop_scale(T - tb(9, k_fill)))
        with at_pop(c, x, y, pop_scale(T - tb(9, k_fill))):
            K.text(c, "梦替你补上", x, y + 4, 64, "hand", NIGHT)
        for i in range(3):
            c.drawPath(wb.arrow((x - 120 + i * 120, y - 100), (cx - 330 + i * 330, cy + 140), 0.1, 24),
                       wb.marker(NIGHT, 5, clamp01((T - tb(9, k_fill)) / 0.3)))
    return None


L.note("梦替你补上")
ev(j, k_slot[0], slots9, "pop", 0.65)
b.hit(j, k_slot[1], "pop", 0.65, "第二格")
b.hit(j, k_slot[2], "pop", 0.65, "第三格")
b.hit(j, k_fill, "ding", 0.8, "梦替你补上")

# ================================================================ 屏 10：为什么要补——愿望没满足就翻来覆去；梦先满足，睡踏实
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_toss = kq(j, wt(15, 0, 0.5), 0)
k_q10 = nx(j, wt(15, 1, 0.3), k_toss)
k_sat = nx(j, wt(16, 0, 0.5), k_q10)
k_calm = nx(j, wt(16, 1, 0.5), k_sat)
L.note("睡不踏实", "睡踏实了", "想要")


def toss10(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 280, cy + 380
    calm = T >= tb(10, k_calm)
    with at_pop(c, x, y, sc):
        bed(c, x - 230, y - 40, 460)
        wob = 0 if calm else 14 * math.sin(T * 7)
        with K.at(c, x + wob, y - 60, wob * 0.5):
            sleeper(c, 0, 0, 0.7, T, None, "smile" if calm else "sad")
        if not calm and T >= tb(10, k_q10):
            g = pop_scale(T - tb(10, k_q10))
            with K.at(c, x - 30, y - 360, 0, g):
                box(c, 0, 0, 200, 90, PAPER_W, RED, 5, 40)
                K.text(c, "想要", 0, 2, 50, "hand", RED)
        if calm:
            for i in range(3):
                f = ((T - tb(10, k_calm)) * 0.7 + i / 3) % 1
                K.text(c, "Z", x - 150 + f * 60, y - 200 - f * 160, 50 + i * 10, "hand", NIGHT, 1 - f)
        K.text(c, "睡踏实了" if calm else "睡不踏实", x, y + 160, 56, "hand", GREEN if calm else RED)
    return None


ev(j, k_toss, pop_fn(j, k_toss, toss10), "wood_low", 0.7)
b.hit(j, k_q10, "pop", 0.65, "想要的冒出来")


def sat10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_sat))
    x, y = cx + 260, cy - 200
    if not dream_cloud(c, x, y, 520, 420, sc, tail_to=(cx - 300, cy + 200)):
        return None
    with at_pop(c, x, y, sc):
        star(c, x, y, 90)
        c.drawPath(check(x + 120, y + 100, 50), wb.marker(GREEN, 10))
    return None


ev(j, k_sat, sat10, "ding", 0.75)
b.hit(j, k_calm, "wood_high", 0.7, "睡踏实了")

# ================================================================ 屏 11：现在怎么看——书 vs 研究在争论；放大镜照“最近缺什么”
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_book = kq(j, wt(17, 1, 0.3), 0)
k_lab = nx(j, wt(17, 2, 0.4), k_book)
k_mag = nx(j, wt(18, 1, 0.6), k_lab)
L.note("书里的看法", "研究", "还在争论", "最近缺什么")


def debate11(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 200, sc):
        box(c, cx - 300, cy - 300, 240, 300, NIGHT, BLACK, 6, 10)
        K.text(c, "梦的", cx - 300, cy - 340, 50, "serif_black", "#FFE39A")
        K.text(c, "解析", cx - 300, cy - 280, 50, "serif_black", "#FFE39A")
        K.text(c, "书里的看法", cx - 300, cy - 100, 46, "hand", NIGHT)
    return None


ev(j, k_book, pop_fn(j, k_book, debate11), "wood_low", 0.7)


def lab11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_lab))
    if sc <= 0:
        return None
    x, y = cx + 280, cy - 300
    with at_pop(c, x, y, sc):
        A.brain(c, x, y, 110)
        K.text(c, "研究", x, y - 170, 50, "hand", BLUE)
        K.text(c, "还在争论", cx, cy - 300, 50, "hand", ORANGE)
        for sg in (-1, 1):
            C.line(c, (cx + sg * 30, cy - 360), (cx + sg * 70, cy - 400), ORANGE, 6)
    return None


ev(j, k_lab, lab11, "wood_high", 0.7)


def mag11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_mag))
    if sc <= 0:
        return None
    x, y = cx, cy + 260
    with K.at(c, x, y, 0, sc):
        C.line(c, (110, 110), (210, 210), "#A9773E", 22)
        c.drawCircle(0, 0, 160, K.paint(PAPER_W))
        c.drawCircle(0, 0, 160, wb.marker(BLACK, 10))
        K.text(c, "最近", 0, -40, 60, "hand", BLACK)
        K.text(c, "缺什么", 0, 40, 64, "hand", RED)
    return None


ev(j, k_mag, mag11, "ding", 0.8)

# ================================================================ 屏 12：说回我们自己——小李醒来笑笑，不笑话自己；“三步”
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_li12 = kq(j, wt(19, 0, 0.5), 0)
k_3 = nx(j, wt(19, 2, 0.5), k_li12)
GY12 = cy + 420
L.note("三步", "哈", "别急着笑")


def li12(c, sc, T, cx=cx, cy=cy):
    x = cx - 220
    with at_pop(c, x, GY12, sc):
        C.line(c, (x - 300, GY12), (x + 300, GY12), BLACK, 7)
        draw_li(c, x, GY12, 0.9, "smile")
        dream_cloud(c, x - 120, cy - 300, 260, 160, 1.0)
        star(c, x - 160, cy - 300, 40)
        K.text(c, "500万", x - 70, cy - 290, 40, "hand", RED)
        box(c, x + 170, cy - 120, 240, 90, PAPER_W, GREEN, 5, 40)
        K.text(c, "别急着笑", x + 170, cy - 118, 46, "hand", GREEN)
    return None


ev(j, k_li12, pop_fn(j, k_li12, li12), "wood_low", 0.7)


def three12(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(12, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 270, cy - 160, -4, sc):
        c.drawCircle(0, 0, 190, K.paint("#FFF4D6"))
        c.drawCircle(0, 0, 190, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 130, "hand", L.ACC)
    return None


ev(j, k_3, three12, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 13：做法一——便签上三个勾选框：一顿饭、一句夸、一张床
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_n13 = kq(j, wt(20, 1, 0.2), 0)
k_it = [nx(j, wt(20, 1, 0.8), k_n13), nx(j, wt(20, 2, 0.4), k_n13 + 1), nx(j, wt(20, 3, 0.4), k_n13 + 2)]
ITEMS = ["一顿饭", "一句夸", "一张床"]
L.note("第一", "梦里得到了什么", *ITEMS)


def note13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_n13))
    if sc <= 0:
        return None
    with K.at(c, cx, cy - 20, -2, sc):
        K.text(c, "第一", -300, -470, 70, "hand", L.ACC)
        K.text(c, "梦里得到了什么", 80, -470, 56, "hand", BLACK)
        box(c, 0, 20, 640, 640, NOTE_FILL, ORANGE, 7, 12)
        for i, it in enumerate(ITEMS):
            y = -170 + i * 190
            c.drawRect(skia.Rect.MakeXYWH(-250, y - 40, 80, 80), K.paint(PAPER_W))
            c.drawRect(skia.Rect.MakeXYWH(-250, y - 40, 80, 80), wb.marker(BLACK, 6))
            g = pop_scale(T - tb(13, k_it[i]))
            if g > 0:
                K.text(c, it, 60, y, 72, "hand", BLACK, clamp01(g * 2))
                with K.at(c, -210, y, 0, g):
                    c.drawPath(check(0, 0, 40), wb.marker(GREEN, 10))
    return None


ev(j, k_n13, note13, "wood_low", 0.7)
for i, k_ in enumerate(k_it):
    b.hit(j, k_, "pop", 0.7, f"勾上：{ITEMS[i]}")

# ================================================================ 屏 14：做法二——梦里的那顿饭，连线到白天的日程“加班到十点，没吃晚饭”
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_d14 = kq(j, wt(21, 1, 0.2), 0)
k_cal14 = nx(j, wt(21, 1, 0.8), k_d14)
k_ln14 = nx(j, wt(21, 2, 0.5), k_cal14)
L.note("第二", "白天哪件事", "梦里", "一顿饭", "白天", "没吃晚饭")


def d14(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 260, cy, sc):
        K.text(c, "第二", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "白天哪件事", cx - 60, cy - 500, 56, "hand", BLACK)
        dream_cloud(c, cx - 260, cy - 120, 400, 300, 1.0)
        K.text(c, "梦里", cx - 260, cy - 200, 44, "sans_medium", NIGHT)
        K.text(c, "一顿饭", cx - 260, cy - 110, 64, "hand", ORANGE)
    return None


ev(j, k_d14, pop_fn(j, k_d14, d14), "wood_low", 0.7)


def cal14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_cal14))
    if sc <= 0:
        return None
    with K.at(c, cx + 250, cy + 200, 4, sc):
        box(c, 0, 0, 360, 360, PAPER_W, BLACK, 7, 12)
        c.drawRect(skia.Rect.MakeXYWH(-180, -180, 360, 80), K.paint(RED))
        K.text(c, "白天", 0, -140, 52, "hand", "#FFFFFF")
        K.text(c, "加班到十点", 0, -20, 52, "hand", BLACK)
        K.text(c, "没吃晚饭", 0, 80, 60, "hand", RED)
    return None


L.note("加班到十点")
ev(j, k_cal14, cal14, "wood_high", 0.7)


def ln14(c, kk, T, cx=cx, cy=cy):
    t0 = tb(14, k_ln14)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.45))
    a, z = (cx - 120, cy + 20), (cx + 60, cy + 180)
    c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), 0.25, 34), wb.marker(NIGHT, 8))
    return None


ev(j, k_ln14, ln14, "ding", 0.8)

# ================================================================ 屏 15：做法三——今天给自己一点：七点吃饭、十一点睡
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k_h15 = kq(j, wt(22, 1, 0.2), 0)
k_eat = nx(j, wt(22, 2, 0.7), k_h15)
k_bed15 = nx(j, wt(22, 3, 0.4), k_eat)
L.note("第三", "给自己一点", "19:00", "23:00")


def h15(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第三", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "给自己一点", cx - 60, cy - 500, 56, "hand", BLACK)
    return None


ev(j, k_h15, pop_fn(j, k_h15, h15), "wood_low", 0.6)


def eat15(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 260, cy + 300
    with at_pop(c, x, y, sc):
        box(c, x, y - 380, 220, 90, PAPER_W, BLACK, 6, 14)
        K.text(c, "19:00", x, y - 378, 54, "black", ORANGE)
        draw_li(c, x, y + 80, 0.8, "smile", rh=(x + 80, y - 110))
        c.drawPath(P((x + 40, y - 80), (x + 200, y - 80), (x + 170, y - 20), (x + 70, y - 20), close=True), K.paint(PAPER_W))
        c.drawPath(P((x + 40, y - 80), (x + 200, y - 80), (x + 170, y - 20), (x + 70, y - 20), close=True), wb.marker(BLACK, 6))
        for i in range(2):
            ph = (T * 0.8 + i / 2) % 1
            c.drawPath(P((x + 100 + i * 40, y - 100 - ph * 10), (x + 115 + i * 40, y - 140 - ph * 30)), wb.marker(GRAY, 5, 1 - ph))
    return None


ev(j, k_eat, pop_fn(j, k_eat, eat15), "pop", 0.7)


def bed15(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 120, cy + 300
    with at_pop(c, x + 200, y, sc):
        box(c, x + 240, y - 380, 220, 90, PAPER_W, BLACK, 6, 14)
        K.text(c, "23:00", x + 240, y - 378, 54, "black", NIGHT)
        bed(c, x, y, 440)
        sleeper(c, x + 220, y - 20, 0.6, T, None, "smile")
        moon(c, x + 420, y - 260, 40)
    return None


ev(j, k_bed15, pop_fn(j, k_bed15, bed15), "ding", 0.75)

# ================================================================ 屏 16：这样看梦——梦里的大餐折成便条“该好好吃饭了”
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
k_cl16 = 0
k_fold = nx(j, wt(23, 1, 0.6), k_cl16)
k_txt = nx(j, wt(23, 2, 0.6), k_fold)
L.note("便条", "该好好吃饭了")


def fold16(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(16, k_cl16))
    if sc <= 0:
        return None
    m = ease_in_out(clamp01((T - tb(16, k_fold)) / 0.45)) if T >= tb(16, k_fold) else 0.0
    x, y = cx, cy - 120
    if m < 1:
        dream_cloud(c, x, y, 700 * (1 - m * 0.6), 480 * (1 - m * 0.6), sc, alpha=1 - m)
        with K.at(c, x, y, 0, 1 - m * 0.6):
            for i, dx in enumerate((-150, 0, 150)):
                box(c, dx, 40, 120, 90, ("#F6C3BE", "#FFF1A8", "#D3EDDC")[i], BLACK, 5, 10, 1 - m)
    if m > 0:
        with K.at(c, x, y, -3 * m, lerp(0.3, 1.0, m)):
            box(c, 0, 0, 640, 420, NOTE_FILL, ORANGE, 7, 10)
            c.drawRect(skia.Rect.MakeXYWH(-80, -230, 160, 50), K.paint("#F2B705", 0.7))
            K.text(c, "便条", -220, -150, 54, "hand", ORANGE)
            if T >= tb(16, k_txt):
                g = clamp01((T - tb(16, k_txt)) / 0.6)
                s_ = "该好好吃饭了"
                n = max(1, int(math.ceil(len(s_) * g)))
                K.text(c, s_[:n], -240, 20, 70, "hand", RED, 1.0, "left")
    return None


ev(j, k_cl16, fold16, "pop", 0.7)
b.hit(j, k_fold, "clap", 0.8, "大餐折成便条")
b.hit(j, k_txt, "pop", 0.7, "写上：该好好吃饭了")


def li16(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(16, k_txt) - 0.8)
    if sc <= 0:
        return None
    x, y = cx + 300, cy + 470
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.75, "smile", rh=(x - 90, y - 290 * 0.75 + 80))
    return None


b.custom(j, k_txt, k_txt + 0.3, li16)

# ================================================================ 屏 17：评论区——“梦里中了五百万”；礼物盒“给自己一点”；下一讲预告
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
k_box = kq(j, wt(24, 0, 0.4), 0)
k_type = nx(j, wt(25, 0, 0.5), k_box)
k_likes = nx(j, wt(25, 1, 0.5), k_type)
k_gift = nx(j, wt(26, 1, 0.3), k_likes)
k_n = nx(j, wt(27, 0, 0.1), k_gift)
L.note("评论区", "梦里中了五百万", "发送", "+1", "给自己一点")


def input17(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(17, k_box))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(17, k_type):
            s_ = "梦里中了五百万"
            g = clamp01((T - tb(17, k_type)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], x - w / 2 + 40, y + 2, 58, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, L.ACC)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
        for i in range(6):
            g = pop_scale(T - tb(17, k_likes) - i * 0.15)
            if g > 0:
                with K.at(c, x - 330 + i * 120, y + 140, 0, g):
                    K.rr(c, 0, 0, 100, 60, 30, "#FFF4D6")
                    K.text(c, "+1", 0, 2, 40, "hand", L.ACC)
    return None


ev(j, k_box, input17, "wood_high", 0.7)
b.hit(j, k_type, "pop", 0.6, "打字")
b.hit(j, k_likes, "clap", 0.75, "好多人加一")


def gift17(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(17, k_gift))
    if sc <= 0:
        return None
    x, y = cx - 150, cy + 300
    with at_pop(c, x, y, sc):
        draw_li(c, x - 160, y, 0.8, "smile", rh=(x - 40, y - 180))
        box(c, x + 80, y - 120, 200, 170, "#F6C3BE", RED, 7, 10)
        C.line(c, (x + 80, y - 205), (x + 80, y - 35), RED, 10)
        C.line(c, (x - 20, y - 120), (x + 180, y - 120), RED, 10)
        K.text(c, "给自己一点", x + 300, y - 280, 60, "hand", GREEN)
    sparkle(c, x + 80, y - 120, T - tb(17, k_gift), YELLOW, 10, 110, 200)
    return None


ev(j, k_gift, gift17, "ding", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "梦里的事，为什么总拐着弯说？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=6, notes=NOTES)
L.export(globals())
