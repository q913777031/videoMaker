"""《梦的解析》07 变成画面：梦里为什么不讲道理？（白板手绘 + AI 旁白，竖屏 2:3）

对话改写（把画面翻译成话）：每个怪画面旁边配一张“翻译卡”，把它改写回一句人话。
- 开场：胶片上一格开会、剪刀一剪、下一格海边，配音“说切就切”；
- 痛点：梦泡泡里会议室一刀切到海边；小李讲给同事听，气泡“没逻辑”；
- 身边的例子（drop 在第 2 屏）：项目要黄 → 梦里一串香蕉变黄；压力山大 → 梦里背着一座山走路；
- 书中：弗洛伊德与放映幕，“因为 所以 如果”被划掉；俗话画成真事（“要黄了” → 文件夹真变黄）；
  一前一后 = 因为所以（下雨 → 打伞）；同框 = 一伙；要么要么 → 两个都放；逻辑藏在前后和远近里；
- 现在怎么看：管逻辑的脑区“下班”，画面跳来跳去；
- 三步：画面翻成一句话（背山 → 压力大）、两格之间补“因为所以”、对一对口头禅；一串画面收成一句话；评论区与下一讲。
文案与出处见 mengjie/PLAN.md「### 07」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, draw_worker, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, NOTE_FILL, PAPER_W, WOOD, at_pop, box, draw_freud, dream_cloud, exam_paper,
                         pen, sparkle, sun)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross

BANANA_G, BANANA_Y = "#B9DB8A", "#FFD84D"


def frame(c, x, y, w, h, rot=0.0, fill=PAPER_W, line=BLACK, alpha=1.0):
    """一格画面（照片框）。"""
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, fill, line, 7, 10, alpha)


def meeting(c, x, y, s=1.0, alpha=1.0):
    """小会议室：桌子 + 白板 + 领导。(x, y) 为中心。"""
    with K.at(c, x, y, 0, s):
        box(c, 0, -60, 200, 110, PAPER_W, GRAY, 5, 6, alpha)
        for r in range(3):
            C.line(c, (-70, -85 + r * 25), (50 - r * 20, -85 + r * 25), BLUE, 4, alpha)
        draw_boss(c, -120, 110, 0.4, alpha=alpha)
        c.drawRect(skia.Rect.MakeXYWH(-40, 40, 200, 22), K.paint(WOOD, alpha))
        c.drawRect(skia.Rect.MakeXYWH(-40, 40, 200, 22), wb.marker("#A9773E", 5, alpha))


def beach(c, x, y, s=1.0, T=0.0, alpha=1.0):
    """海边：太阳 + 波浪 + 沙滩 + 椰树。(x, y) 为中心。"""
    with K.at(c, x, y, 0, s):
        sun(c, 70, -80, 36, alpha)
        for i in range(2):
            ph = 10 * math.sin(T * 2 + i)
            p = skia.Path()
            p.moveTo(-130, 10 + i * 30)
            for k in range(4):
                p.quadTo(-100 + k * 65 + ph, -10 + i * 30, -65 + k * 65 + ph, 10 + i * 30)
            c.drawPath(p, wb.marker(BLUE, 6, alpha))
        c.drawOval(skia.Rect.MakeXYWH(-140, 60, 280, 60), K.paint("#F5DFA8", alpha))
        C.line(c, (-80, 80), (-60, -60), "#A9773E", 8, alpha)
        for a in (-150, -110, -60, -20):
            r = math.radians(a)
            C.line(c, (-60, -60), (-60 + 60 * math.cos(r), -60 + 40 * math.sin(r) + 20), GREEN, 7, alpha)


def banana(c, x, y, s=1.0, rot=0.0, fill=BANANA_Y, alpha=1.0):
    """一根香蕉（弯月形）：(x, y) 为中心。"""
    with K.at(c, x, y, rot, s):
        p = skia.Path()
        p.moveTo(-90, -30)
        p.quadTo(0, 70, 90, -30)
        p.quadTo(0, 30, -90, -30)
        p.close()
        c.drawPath(p, K.paint(fill, alpha))
        c.drawPath(p, wb.marker("#B8860B", 5, alpha))
        C.line(c, (88, -30), (100, -44), "#6B4E16", 7, alpha)


def bunch(c, x, y, s, fill, alpha=1.0):
    for i, (dx, dy, r) in enumerate(((-20, -40, -30), (0, 0, -10), (20, 40, 10))):
        banana(c, x + dx * s, y + dy * s, s, r, fill, alpha)


def mountain(c, x, y, s=1.0, alpha=1.0):
    """一座山：(x, y) 为山脚中点。"""
    with K.at(c, x, y, 0, s):
        p = P((-150, 0), (-40, -200), (10, -150), (60, -230), (150, 0), close=True)
        c.drawPath(p, K.paint("#B9C9A3", alpha))
        c.drawPath(p, wb.marker(GREEN, 7, alpha))
        snow = P((-40, -200), (-70, -150), (-20, -170), (10, -150), close=True)
        c.drawPath(snow, K.paint(PAPER_W, alpha))
        c.drawPath(P((60, -230), (35, -180), (85, -180), close=True), K.paint(PAPER_W, alpha))


def folder(c, x, y, s=1.0, fill="#CFE0F5", line=BLUE, label="项目", alpha=1.0):
    with K.at(c, x, y, 0, s):
        c.drawPath(P((-130, -90), (-50, -90), (-30, -70), (130, -70), (130, 90), (-130, 90), close=True), K.paint(fill, alpha))
        c.drawPath(P((-130, -90), (-50, -90), (-30, -70), (130, -70), (130, 90), (-130, 90), close=True),
                   wb.marker(line, 7, alpha))
        K.text(c, label, 0, 14, 60, "hand", BLACK, alpha)


def cards_left(c, x, y, s_, size=58, col=BLACK, fill=NOTE_FILL, line=ORANGE, rot=0.0, w=None):
    """翻译卡：便签底 + 一句话。"""
    w = w or K.text_w(s_, size, "hand") + 80
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, size + 70, fill, line, 7, 12)
        K.text(c, s_, 0, 4, size, "hand", col)


def _hook(H, j, cx, cy, acc):
    """开场：胶片一格开会 → 剪刀一剪 → 下一格海边；随后“说切就切”逐字砸下。"""
    b = H.b

    def f1(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc > 0:
            with at_pop(c, cx - 260, cy - 200, sc):
                frame(c, cx - 260, cy - 200, 380, 320, -3)
                meeting(c, cx - 260, cy - 200, 1.0)
        return None
    b.custom(j, 0, 0.3, f1, sfx="wood_low", gain=0.7)

    def cut(c, kk, T):
        dt = T - H.tb(j, 1)
        if dt < 0:
            return None
        f = ease_out(clamp01(dt / 0.3))
        y = lerp(cy - 420, cy + 20, f)
        c.drawPath(P((cx, cy - 420), (cx - 20, cy - 330), (cx + 20, cy - 240), (cx - 20, cy - 150), (cx, y)),
                   wb.marker(RED, 8))
        with K.at(c, cx + 10, y, 90 + 20 * math.sin(dt * 30) * (1 - f), 1.0):
            for sg in (-1, 1):
                with K.at(c, 0, 0, sg * 18):
                    C.line(c, (-90, 0), (60, 0), GRAY, 12)
                    c.drawCircle(-110, 0, 26, wb.marker(RED, 8))
        return None
    b.custom(j, 1, 1.3, cut, sfx="rim", gain=0.8)

    def f2(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        with at_pop(c, cx + 260, cy - 200, pop_scale(dt)):
            frame(c, cx + 260, cy - 200, 380, 320, 3, "#EAF4FB", BLUE)
            beach(c, cx + 260, cy - 200, 1.0, T)
        sparkle(c, cx + 260, cy - 200, dt, YELLOW, 10, 200, 270)
        return None
    b.custom(j, 2, 2.3, f2, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("07", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第六章 C“梦的表现手段”、D“可表现性”。",
    "书中观点：梦没有表达“如果、因为、要么”的手段，用同时、先后、一个变成另一个来表现；“要么要么”在梦里变成“都”；抽象想法换成具体画面，常借字面意思。",
    "现在的研究：快速眼动睡眠时前额叶活动降低。小李为虚构人物，“项目要黄”“压力山大”等例子是示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：梦里会议室一刀切到海边；讲给同事听，“没逻辑”
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_cl = kq(j, wt(0, 0, 0.5), 0)
k_bch = nx(j, wt(0, 1, 0.4), k_cl)
k_cut = nx(j, wt(0, 2, 0.4), k_bch)
k_tell = nx(j, wt(1, 0, 0.3), k_cut)
k_no = nx(j, wt(1, 1, 0.5), k_tell)
CL1 = (cx, cy - 290)
GY1 = cy + 450


def cloud1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_cl))
    if not dream_cloud(c, CL1[0], CL1[1], 960, 500, sc):
        return None
    with at_pop(c, CL1[0], CL1[1], sc):
        meeting(c, CL1[0] - 220, CL1[1] + 10, 1.1)
        if T >= tb(1, k_bch):
            with at_pop(c, CL1[0] + 220, CL1[1], pop_scale(T - tb(1, k_bch))):
                beach(c, CL1[0] + 220, CL1[1], 1.1, T)
        if T >= tb(1, k_cut):
            f = ease_out(clamp01((T - tb(1, k_cut)) / 0.3))
            x = CL1[0]
            c.drawPath(P((x, CL1[1] - 200), (x - 25, CL1[1] - 100), (x + 25, CL1[1]), (x - 25, CL1[1] + 100),
                         (x, lerp(CL1[1] - 200, CL1[1] + 200, f))), wb.marker(RED, 9))
    return None


ev(j, k_cl, cloud1, "pop", 0.75)
b.hit(j, k_bch, "shaker", 0.7, "海边")
b.hit(j, k_cut, "rim", 0.8, "硬切")


def tell1(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, GY1, sc):
        draw_li(c, cx - 230, GY1, 0.8, "smile")
        draw_worker(c, cx + 230, GY1, 0.8, mood="o")
    return None


ev(j, k_tell, pop_fn(j, k_tell, tell1), "wood_low", 0.7)
ev(j, k_no, L.pop_bubble("没逻辑", cx - 40, cy + 110, j, k_no, 60, RED, tail=-1), "pop", 0.7)

# ================================================================ 屏 2：项目要黄 → drop：梦里一串香蕉变黄
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_desk = 1
k_cl2 = max(k_desk + 1, KD - 3)
GY2 = cy + 440
CL2 = (cx + 170, cy - 230)
L.note("项目")


def desk2(c, sc, T, cx=cx, cy=cy):
    x = cx - 300
    with at_pop(c, x, GY2, sc):
        draw_li(c, x, GY2, 0.85, "sad", lh=(x - 70, GY2 - 160), rh=(x + 80, GY2 - 160))
        c.drawRect(skia.Rect.MakeXYWH(x - 160, GY2 - 160, 380, 30), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(x - 160, GY2 - 160, 380, 30), wb.marker("#A9773E", 6))
        for lx in (x - 140, x + 200):
            C.line(c, (lx, GY2 - 130), (lx, GY2), "#A9773E", 8)
        folder(c, x - 90, cy - 330, 0.9)
    return None


ev(j, k_desk, pop_fn(j, k_desk, desk2), "wood_low", 0.7)


def cloud2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_cl2))
    if not dream_cloud(c, CL2[0], CL2[1], 700, 560, sc, tail_to=(cx - 300, GY2 - 330)):
        return None
    with at_pop(c, CL2[0], CL2[1], sc):
        land = tb(2, KD)
        y = T >= land
        g = C.slam_scale(T - land) if y else 1.0
        with K.at(c, CL2[0], CL2[1] + 20, 0, g):
            bunch(c, 0, 0, 1.25, BANANA_Y if y else BANANA_G)
        if y:
            sparkle(c, CL2[0], CL2[1], T - land, YELLOW, 12, 180, 280)
    return None


ev(j, k_cl2, cloud2, "pop", 0.7)
ev(j, KD, L.slam_text("变黄", cx + 220, cy + 220, 140, ORANGE, j, KD, rot=-6), "kick", 0.95)

# ================================================================ 屏 3：压力山大 → 梦里背着一座山走路
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_li3 = kq(j, wt(4, 0, 0.4), 0)
k_cl3 = nx(j, wt(4, 1, 0.2), k_li3)
k_mt = nx(j, wt(4, 1, 0.7), k_cl3)
GY3 = cy + 440
CL3 = (cx + 210, cy - 250)


def li3(c, sc, T, cx=cx, cy=cy):
    x = cx - 320
    with at_pop(c, x, GY3, sc):
        draw_li(c, x, GY3, 0.85, "sad")
    return None


ev(j, k_li3, pop_fn(j, k_li3, li3), "wood_low", 0.7)
ev(j, k_li3, L.pop_bubble("压力山大", cx - 370, cy + 20, j, k_li3, 56, BLACK, tail=-1), None)


def cloud3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_cl3))
    if not dream_cloud(c, CL3[0], CL3[1], 660, 600, sc, tail_to=(cx - 200, cy + 120)):
        return None
    with at_pop(c, CL3[0], CL3[1], sc):
        x, y = CL3[0] - 40 + 30 * math.sin(T * 1.5), CL3[1] + 200
        bob = abs(math.sin(T * 4)) * 8
        draw_li(c, x, y - bob, 0.6, "sad", lh=(x - 20, y - 190), rh=(x + 20, y - 190))
        g = C.slam_scale(T - tb(3, k_mt))
        if g > 0:
            with K.at(c, x, y - 160 - bob, 0, g):
                mountain(c, 0, 0, 1.1)
    return None


ev(j, k_cl3, cloud3, "pop", 0.7)
b.hit(j, k_mt, "tom", 0.85, "背上一座山")
b.shots[j].shake = [(k_mt, 8.0)]

# ================================================================ 屏 4：弗洛伊德：梦只会放画面，不会说因为、所以、如果；想法变成看得见的东西
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_fr = kq(j, wt(5, 0, 0.3), 0)
k_scr = nx(j, wt(5, 1, 0.4), k_fr)
k_words = nx(j, wt(5, 2, 0.3), k_scr)
k_x = nx(j, wt(5, 2, 0.9), k_words)
k_obj = nx(j, wt(6, 1, 0.5), k_x)
WORDS4 = ["因为", "所以", "如果"]
L.note(*WORDS4, "只放画面")


def fr4(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 380, cy + 420
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 1.0, "flat")
    return None


ev(j, k_fr, pop_fn(j, k_fr, fr4), "wood_low", 0.7)


def scr4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_scr))
    if sc <= 0:
        return None
    x, y = cx + 140, cy - 280
    with at_pop(c, x, y, sc):
        C.line(c, (x - 330, y - 230), (x + 330, y - 230), BLACK, 12)
        box(c, x, y, 600, 400, PAPER_W, BLACK, 7, 6)
        flip = T >= tb(4, k_obj)
        if flip:
            with at_pop(c, x, y + 20, pop_scale(T - tb(4, k_obj))):
                mountain(c, x - 120, y + 140, 0.9)
                bunch(c, x + 150, y, 0.8, BANANA_Y)
        else:
            dream_cloud(c, x, y, 300, 200, 1.0)
            K.text(c, "？", x, y + 4, 90, "hand", NIGHT)
        K.text(c, "只放画面", x, y + 260, 60, "hand", NIGHT)
    return None


ev(j, k_scr, scr4, "wood_high", 0.7)
b.hit(j, k_obj, "ding", 0.8, "变成看得见的东西")


def words4(c, kk, T, cx=cx, cy=cy):
    for i, w_ in enumerate(WORDS4):
        g = pop_scale(T - tb(4, k_words) - i * 0.12)
        if g <= 0:
            continue
        x, y = cx - 30 + i * 220, cy + 300
        with K.at(c, x, y, (-4, 3, -2)[i], g):
            box(c, 0, 0, 180, 110, PAPER_W, GRAY, 6, 14)
            K.text(c, w_, 0, 4, 60, "hand", BLACK)
            if T >= tb(4, k_x):
                gx = C.slam_scale(T - tb(4, k_x) - i * 0.08)
                if gx > 0:
                    with K.at(c, 0, 0, 0, gx):
                        c.drawPath(cross(0, 0, 55), wb.marker(RED, 11))
    return None


ev(j, k_words, words4, "pop", 0.7)
b.hit(j, k_x, "rim", 0.85, "划掉")

# ================================================================ 屏 5：俗话画成真事——“要黄了” → 文件夹真变黄
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_say = kq(j, wt(7, 0, 0.5), 0)
k_ar5 = nx(j, wt(7, 1, 0.6), k_say)
k_yel = nx(j, wt(7, 2, 0.5), k_ar5)
L.note("要黄了", "真的变黄")


def say5(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 230, cy + 420
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.85, "sad")
    return None


ev(j, k_say, pop_fn(j, k_say, say5), "wood_low", 0.7)
ev(j, k_say, L.pop_bubble("要黄了", cx - 230, cy - 160, j, k_say, 76, BLACK, tail=-1), None)


def ar5(c, kk, T, cx=cx, cy=cy):
    t0 = tb(5, k_ar5)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.4))
    a, z = (cx - 60, cy - 300), (cx + 160, cy - 380)
    c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), -0.3, 34), wb.marker(NIGHT, 8))
    return None


ev(j, k_ar5, ar5, "wood_high", 0.7)


def fold5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_ar5))
    if sc <= 0:
        return None
    x, y = cx + 300, cy - 280
    dream_cloud(c, x, y, 460, 380, sc)
    yl = T >= tb(5, k_yel)
    m = clamp01((T - tb(5, k_yel)) / 0.3) if yl else 0.0
    with at_pop(c, x, y, sc * (C.slam_scale(T - tb(5, k_yel)) if yl else 1.0)):
        fill = "#FFD84D" if m > 0.5 else "#CFE0F5"
        folder(c, x, y, 0.9, fill, ORANGE if m > 0.5 else BLUE)
    if yl:
        sparkle(c, x, y, T - tb(5, k_yel), YELLOW, 10, 160, 240)
        with at_pop(c, x, cy + 60, pop_scale(T - tb(5, k_yel) - 0.15)):
            K.text(c, "真的变黄", x, cy + 60, 72, "hand", ORANGE)
    return None


b.custom(j, k_ar5, k_ar5 + 0.3, fold5)
b.hit(j, k_yel, "ding", 0.85, "真变黄")

# ================================================================ 屏 6：一前一后 = 因为所以（下雨 → 打伞）
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_f1 = kq(j, wt(8, 0, 0.55), 0)
k_f2 = nx(j, wt(8, 0, 0.85), k_f1)
k_so = nx(j, wt(8, 1, 0.5), k_f2)
L.note("前", "后", "因为所以")


def rain(c, x, y, T, s=1.0):
    with K.at(c, x, y, 0, s):
        dream_cloud(c, 0, -60, 220, 110, 1.0)
        for i in range(6):
            f = (T * 1.2 + i / 6) % 1
            xx = -90 + i * 36
            C.line(c, (xx, 10 + f * 100), (xx - 10, 40 + f * 100), BLUE, 5, 1 - f)


def umbrella(c, x, y, s=1.0):
    with K.at(c, x, y, 0, s):
        p = skia.Path()
        p.moveTo(-120, 0)
        p.quadTo(0, -140, 120, 0)
        p.close()
        c.drawPath(p, K.paint("#F6C3BE"))
        c.drawPath(p, wb.marker(RED, 7))
        C.line(c, (0, -70), (0, 110), BLACK, 7)
        draw_li(c, 0, 230, 0.5, "smile", rh=(0, 90))


def f6(c, kk, T, cx=cx, cy=cy):
    for i in range(2):
        k_ = (k_f1, k_f2)[i]
        g = pop_scale(T - tb(6, k_))
        if g <= 0:
            continue
        x, y = cx - 270 + i * 540, cy - 160
        with K.at(c, x, y, (-3, 3)[i], g):
            box(c, 0, 0, 420, 440, PAPER_W, BLACK, 7, 12)
            K.text(c, ("前", "后")[i], -160, -180, 56, "hand", GRAY)
            if i == 0:
                rain(c, 0, -20, T, 1.2)
            else:
                umbrella(c, 0, -40, 1.0)
    return None


ev(j, k_f1, f6, "pop", 0.7)
b.hit(j, k_f2, "pop", 0.7, "后一格")


def so6(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k_so)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.35))
    c.drawPath(wb.arrow((cx - 60, cy - 160), (lerp(cx - 60, cx + 60, f), cy - 160), 0.0, 34), wb.marker(L.ACC, 10))
    with K.at(c, cx, cy + 270, -3, C.slam_scale(dt)):
        box(c, 0, 0, 520, 170, "#FFF4D6", L.ACC, 9, 24)
        K.text(c, "因为所以", 0, 4, 100, "hand", L.ACC)
    return None


ev(j, k_so, so6, "kick", 0.9)
b.shots[j].shake = [(k_so, 7.0)]

# ================================================================ 屏 7：同框 = 一伙；要么要么 → 两个都放
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_box7 = kq(j, wt(9, 0, 0.5), 0)
k_gang = nx(j, wt(9, 1, 0.6), k_box7)
k_or = nx(j, wt(10, 0, 0.5), k_gang)
k_both = nx(j, wt(10, 1, 0.5), k_or)
L.note("一伙", "要么", "都要", "咖啡", "奶茶")


def box7(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 120, cy - 290
    with at_pop(c, x, y, sc):
        box(c, x, y, 560, 380, PAPER_W, BLACK, 7, 12)
        draw_boss(c, x - 130, y + 170, 0.7, mood="flat")
        exam_paper(c, x + 140, y + 10, 180, 220, 6, "考试", "60")
    return None


L.note("考试", "60")
ev(j, k_box7, pop_fn(j, k_box7, box7), "wood_low", 0.7)


def gang7(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(7, k_gang)
    if dt < 0:
        return None
    x, y = cx - 120, cy - 290
    K.ring(c, x, y, 250, RED, 9, 1.0, ease_out(clamp01(dt / 0.4)))
    with K.at(c, cx + 340, cy - 380, 6, pop_scale(dt - 0.1)):
        box(c, 0, 0, 200, 110, PAPER_W, RED, 7, 30)
        K.text(c, "一伙", 0, 4, 64, "hand", RED)
    return None


ev(j, k_gang, gang7, "ding", 0.8)


def drink(c, x, y, s, fill, label):
    with K.at(c, x, y, 0, s):
        p = P((-55, -80), (55, -80), (42, 80), (-42, 80), close=True)
        c.drawPath(p, K.paint(fill))
        c.drawPath(p, wb.marker(BLACK, 6))
        C.line(c, (10, -80), (30, -140), RED, 7)
        K.text(c, label, 0, 130, 46, "hand", BLACK)


def or7(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(7, k_or)
    if dt < 0:
        return None
    y = cy + 260
    both = T >= tb(7, k_both)
    m = ease_in_out(clamp01((T - tb(7, k_both)) / 0.4)) if both else 0.0
    with at_pop(c, cx, y, pop_scale(dt)):
        if m < 1:
            K.text(c, "要么", cx - 400, y - 160, 50, "hand", GRAY, 1 - m)
            K.text(c, "要么", cx - 100, y - 160, 50, "hand", GRAY, 1 - m)
        xa, xb = lerp(cx - 400, cx + 80, m), lerp(cx - 100, cx + 300, m)
        if m > 0:
            dream_cloud(c, cx + 190, y + 10, 600 * m, 420 * m, 1.0)
        drink(c, xa, y, 1.1, "#C8A27A", "咖啡")
        drink(c, xb, y, 1.1, "#F3D9C1", "奶茶")
    if both:
        with K.at(c, cx - 300, y + 20, -4, C.slam_scale(T - tb(7, k_both) - 0.35)):
            K.text(c, "都要", 0, 0, 80, "hand", L.ACC)
    return None


ev(j, k_or, or7, "pop", 0.7)
b.hit(j, k_both, "kick", 0.85, "两个都放")

# ================================================================ 屏 8：逻辑藏在画面的前后和远近里
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_strip = kq(j, wt(11, 0, 0.4), 0)
k_fb = nx(j, wt(11, 1, 0.5), k_strip)
k_far = nx(j, wt(11, 1, 0.9), k_fb)
L.note("前后", "远近", "没逻辑？")


def strip8(c, sc, T, cx=cx, cy=cy):
    y = cy - 280
    with at_pop(c, cx, y, sc):
        c.drawRect(skia.Rect.MakeXYWH(cx - 540, y - 170, 1080, 340), K.paint("#3A3F48"))
        for i in range(14):
            for yy in (y - 150, y + 130):
                c.drawRect(skia.Rect.MakeXYWH(cx - 520 + i * 76, yy, 34, 22), K.paint(PAPER_W))
        for i in range(3):
            x = cx - 350 + i * 350
            box(c, x, y, 300, 220, PAPER_W, BLACK, 4, 6)
            if i == 0:
                meeting(c, x, y, 0.75)
            elif i == 1:
                mountain(c, x, y + 90, 0.7)
            else:
                beach(c, x, y, 0.75, T)
        K.text(c, "没逻辑？", cx, y - 240, 60, "hand", GRAY)
    return None


ev(j, k_strip, pop_fn(j, k_strip, strip8), "wood_low", 0.7)


def fb8(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k_fb)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.5))
    y = cy - 60
    c.drawPath(wb.arrow((cx - 380, y), (lerp(cx - 380, cx + 380, f), y), 0.0, 40), wb.marker(L.ACC, 10))
    with at_pop(c, cx, y + 80, pop_scale(dt)):
        K.text(c, "前后", cx, y + 80, 76, "hand", L.ACC)
    return None


ev(j, k_fb, fb8, "wood_high", 0.75)


def far8(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k_far)
    if dt < 0:
        return None
    y = cy + 330
    with at_pop(c, cx, y, pop_scale(dt)):
        C.line(c, (cx - 500, y + 120), (cx + 500, y + 120), BLACK, 6)
        c.drawPath(P((cx - 420, y + 120), (cx - 60, y - 60), (cx + 60, y - 60), (cx + 420, y + 120)), wb.marker(GRAY, 5))
        draw_boss(c, cx + 60, y - 40, 0.3)
        draw_li(c, cx - 200, y + 110, 0.65, "smile")
        K.text(c, "远近", cx + 300, y - 30, 76, "hand", L.ACC)
    return None


ev(j, k_far, far8, "ding", 0.8)

# ================================================================ 屏 9：现在怎么看——管逻辑的脑区“下班”，梦跳来跳去
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_br = kq(j, wt(12, 1, 0.5), 0)
k_off = nx(j, wt(12, 2, 0.6), k_br)
k_jump = nx(j, wt(12, 3, 0.4), k_off)
L.note("研究", "管逻辑", "下班", "Z")


def br9(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 100, cy - 260
    with at_pop(c, x, y, sc):
        A.brain(c, x, y, 160)
        K.text(c, "研究", x - 280, y - 250, 56, "hand", BLUE)
        c.drawPath(wb.arrow((x + 330, y - 230), (x - 120, y - 70), 0.15, 30), wb.marker(BLACK, 6))
        K.text(c, "管逻辑", x + 360, y - 280, 56, "hand", BLACK)
    return None


ev(j, k_br, pop_fn(j, k_br, br9), "wood_low", 0.7)


def off9(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(9, k_off)
    if dt < 0:
        return None
    x, y = cx - 100, cy - 260
    with K.at(c, x - 120, y - 110, -8, C.slam_scale(dt)):
        box(c, 0, 0, 200, 90, NOTE_FILL, ORANGE, 6, 10)
        K.text(c, "下班", 0, 4, 56, "hand", ORANGE)
    for i in range(3):
        f = (dt * 0.7 + i / 3) % 1
        K.text(c, "Z", x + 200 + f * 60, y - 60 - f * 140, 50 + i * 10, "hand", NIGHT, 1 - f)
    return None


ev(j, k_off, off9, "rim", 0.8)


def jump9(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(9, k_jump)
    if dt < 0:
        return None
    y = cy + 330
    for i in range(3):
        g = pop_scale(dt - i * 0.15)
        if g <= 0:
            continue
        x = cx - 360 + i * 360
        with K.at(c, x, y + (60 if i % 2 else 0), (-5, 4, -3)[i], g):
            box(c, 0, 0, 240, 180, PAPER_W, BLACK, 6, 8)
            if i == 0:
                meeting(c, 0, 0, 0.6)
            elif i == 1:
                bunch(c, 0, 0, 0.5, BANANA_Y)
            else:
                beach(c, 0, 0, 0.6, T)
        if i < 2:
            c.drawPath(wb.arrow((x + 100, y - 110), (x + 260, y - 110 + (60 if i == 0 else -60)), 0.5, 26),
                       wb.marker(NIGHT, 6, clamp01(dt * 3)))
    return None


ev(j, k_jump, jump9, "shaker", 0.75)

# ================================================================ 屏 10：说回我们自己——没头没尾的梦；“三步”
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_li10 = kq(j, wt(13, 0, 0.5), 0)
k_3 = nx(j, wt(13, 2, 0.4), k_li10)
GY10 = cy + 420
L.note("三步", "乱梦？")


def li10(c, sc, T, cx=cx, cy=cy):
    x = cx - 240
    with at_pop(c, x, GY10, sc):
        C.line(c, (x - 300, GY10), (x + 300, GY10), BLACK, 7)
        draw_li(c, x, GY10, 0.9, "flat")
        dream_cloud(c, x - 40, cy - 280, 380, 260, 1.0, tail_to=(x, GY10 - 300))
        c.drawPath(wb.scribble(x - 40, cy - 280, 220, 140, 9), wb.marker(GRAY, 6))
        K.text(c, "乱梦？", x - 40, cy - 460, 56, "hand", GRAY)
    return None


ev(j, k_li10, pop_fn(j, k_li10, li10), "wood_low", 0.7)


def three10(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(10, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 270, cy - 60, -4, sc):
        c.drawCircle(0, 0, 190, K.paint("#FFF4D6"))
        c.drawCircle(0, 0, 190, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 130, "hand", L.ACC)
    return None


ev(j, k_3, three10, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 11：第一，画面翻成一句话——背着山 → 压力大
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_h11 = kq(j, wt(14, 0, 0.5), 0)
k_pic = nx(j, wt(14, 1, 0.6), k_h11)
k_tr = nx(j, wt(14, 2, 0.4), k_pic)
L.note("第一", "翻成一句话", "压力大")


def h11(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 480, sc):
        K.text(c, "第一", cx - 330, cy - 480, 76, "hand", L.ACC)
        K.text(c, "翻成一句话", cx + 80, cy - 480, 66, "hand", BLACK)
    return None


ev(j, k_h11, pop_fn(j, k_h11, h11), "wood_low", 0.7)


def pic11(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 220, cy - 120
    with at_pop(c, x, y, sc):
        frame(c, x, y, 460, 460, -3)
        draw_li(c, x, y + 200, 0.6, "sad", lh=(x - 20, y + 10), rh=(x + 20, y + 10))
        mountain(c, x, y + 30, 0.9)
    return None


ev(j, k_pic, pop_fn(j, k_pic, pic11), "pop", 0.7)


def tr11(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(11, k_tr)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.35))
    a, z = (cx - 10, cy + 120), (cx + 150, cy + 220)
    c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), -0.3, 30), wb.marker(NIGHT, 8))
    with K.at(c, cx + 260, cy + 330, 3, pop_scale(dt - 0.15)):
        box(c, 0, 0, 400, 160, NOTE_FILL, ORANGE, 8, 14)
        K.text(c, "压力大", 0, 4, 90, "hand", RED)
    return None


ev(j, k_tr, tr11, "ding", 0.85)

# ================================================================ 屏 12：第二，前后两格之间补一个“因为所以”
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_h12 = kq(j, wt(15, 0, 0.5), 0)
k_two = nx(j, wt(15, 1, 0.5), k_h12)
k_ins = nx(j, wt(15, 2, 0.5), k_two)
L.note("第二", "中间补一句", "因为累了", "所以想逃")


def h12(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 480, sc):
        K.text(c, "第二", cx - 330, cy - 480, 76, "hand", L.ACC)
        K.text(c, "中间补一句", cx + 80, cy - 480, 66, "hand", BLACK)
    return None


ev(j, k_h12, pop_fn(j, k_h12, h12), "wood_low", 0.7)


def two12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_two))
    if sc <= 0:
        return None
    m = ease_in_out(clamp01((T - tb(12, k_ins)) / 0.4)) if T >= tb(12, k_ins) else 0.0
    gap = lerp(0, 130, m)
    for i in range(2):
        x, y = cx + (-1 if i == 0 else 1) * (200 + gap), cy - 100
        with K.at(c, x, y, (-3, 3)[i], sc):
            box(c, 0, 0, 340, 300, PAPER_W, BLACK, 7, 10)
            if i == 0:
                meeting(c, 0, 0, 0.9)
            else:
                beach(c, 0, 0, 0.9, T)
    return None


ev(j, k_two, two12, "pop", 0.7)


def ins12(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(12, k_ins)
    if dt < 0:
        return None
    y = lerp(cy + 380, cy + 230, ease_out(clamp01(dt / 0.4)))
    with K.at(c, cx, y, 0, pop_scale(dt)):
        box(c, 0, 0, 380, 220, "#FFF4D6", L.ACC, 8, 16)
        K.text(c, "因为累了", 0, -45, 62, "hand", L.ACC)
        K.text(c, "所以想逃", 0, 45, 62, "hand", L.ACC)
    c.drawPath(wb.arrow((cx, y - 120), (cx, cy - 60), 0.0, 30), wb.marker(L.ACC, 7, clamp01(dt * 3)))
    return None


ev(j, k_ins, ins12, "ding", 0.85)

# ================================================================ 屏 13：第三，对一对口头禅
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_h13 = kq(j, wt(16, 0, 0.5), 0)
k_card13 = nx(j, wt(16, 1, 0.5), k_h13)
k_say13 = nx(j, wt(16, 2, 0.4), k_card13)
k_eq13 = nx(j, wt(16, 2, 0.9), k_say13)
L.note("第三", "像不像口头禅", "压力大", "压力好大", "对上了")


def h13(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 480, sc):
        K.text(c, "第三", cx - 330, cy - 480, 76, "hand", L.ACC)
        K.text(c, "像不像口头禅", cx + 100, cy - 480, 62, "hand", BLACK)
    return None


ev(j, k_h13, pop_fn(j, k_h13, h13), "wood_low", 0.7)
def card13(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(13, k_card13))
    if g > 0:
        with at_pop(c, cx - 260, cy - 240, g):
            cards_left(c, cx - 260, cy - 240, "压力大", 76, RED, rot=-3)
    return None


ev(j, k_card13, card13, "pop", 0.7)


def say13(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 250, cy + 420
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.85, "sad")
    return None


ev(j, k_say13, pop_fn(j, k_say13, say13), "wood_high", 0.7)
ev(j, k_say13, L.pop_bubble("压力好大", cx + 200, cy - 120, j, k_say13, 64, BLACK, tail=1), None)


def eq13(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(13, k_eq13)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.35))
    a, z = (cx - 140, cy - 160), (cx + 40, cy - 130)
    c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), 0.3, 26), wb.marker(GREEN, 8))
    with K.at(c, cx - 260, cy + 180, -6, C.slam_scale(dt - 0.1)):
        box(c, 0, 0, 300, 130, PAPER_W, GREEN, 8, 30)
        K.text(c, "对上了", 0, 4, 70, "hand", GREEN)
    return None


ev(j, k_eq13, eq13, "kick", 0.85)

# ================================================================ 屏 14：这样看梦——一串画面收成一句你自己的话
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_row = kq(j, wt(17, 1, 0.4), 0)
k_suck = nx(j, wt(17, 2, 0.2), k_row)
k_line = nx(j, wt(17, 2, 0.7), k_suck)
L.note("最近压力好大")


def row14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_row))
    if sc <= 0:
        return None
    m = ease_in_out(clamp01((T - tb(14, k_suck)) / 0.6)) if T >= tb(14, k_suck) else 0.0
    for i in range(3):
        x0, y0 = cx - 360 + i * 360, cy - 300
        x, y = lerp(x0, cx - 260 + i * 260, m), lerp(y0, cy - 260, m)
        with K.at(c, x, y, (-4, 2, 5)[i] * (1 - m), sc * (1 - 0.25 * m)):
            box(c, 0, 0, 280, 220, PAPER_W, BLACK, 6, 8)
            if i == 0:
                mountain(c, 0, 90, 0.7)
            elif i == 1:
                bunch(c, 0, 0, 0.55, BANANA_Y)
            else:
                beach(c, 0, 0, 0.7, T)
        if m > 0:
            c.drawPath(wb.arrow((cx - 260 + i * 260, cy - 150), (lerp(cx - 260 + i * 260, cx + (i - 1) * 120, m), lerp(cy - 150, cy - 20, m)),
                                0.0, 26), wb.marker(NIGHT, 6, m))
    return None


ev(j, k_row, row14, "pop", 0.7)
b.hit(j, k_suck, "shaker", 0.7, "画面收起来")


def line14(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(14, k_line)
    if dt < 0:
        return None
    y = cy + 120
    with K.at(c, cx, y, 0, pop_scale(dt)):
        c.drawRoundRect(skia.Rect.MakeXYWH(-400, -100, 800, 200), 40, 40, K.paint(PAPER_W))
        c.drawPath(wb.bubble(0, 0, 800, 200, 1), wb.marker(BLACK, 8))
        g = clamp01(dt / 0.7)
        s_ = "最近压力好大"
        n = max(1, int(math.ceil(len(s_) * g)))
        K.text(c, s_[:n], -330, 4, 90, "hand", RED, 1.0, "left")
    sc = pop_scale(dt - 0.3)
    if sc > 0:
        with at_pop(c, cx + 390, cy + 500, sc):
            draw_li(c, cx + 390, cy + 500, 0.65, "smile")
    return None


ev(j, k_line, line14, "ding", 0.85)

# ================================================================ 屏 15：评论区——“梦里香蕉变黄了”；拿笔画出来；下一讲预告
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k_box = kq(j, wt(18, 0, 0.4), 0)
k_type = nx(j, wt(19, 0, 0.5), k_box)
k_likes = nx(j, wt(19, 1, 0.5), k_type)
k_draw = nx(j, wt(20, 1, 0.3), k_likes)
k_n = nx(j, wt(21, 0, 0.1), k_draw)
L.note("评论区", "梦里香蕉变黄了", "发送", "+1", "画出来")


def input15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_box))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(15, k_type):
            s_ = "梦里香蕉变黄了"
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


def draw15(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(15, k_draw)
    sc = pop_scale(dt)
    if sc <= 0:
        return None
    x, y = cx - 150, cy + 330
    with at_pop(c, x, y, sc):
        draw_li(c, x - 200, y + 50, 0.8, "smile", rh=(x - 60, y - 150))
        box(c, x + 160, y - 150, 360, 300, PAPER_W, BLACK, 6, 8)
        f = clamp01((dt - 0.2) / 0.8)
        p = C.heart_path(x + 160, y - 150, 70)
        meas = skia.PathMeasure(p, False)
        seg = skia.Path()
        meas.getSegment(0, meas.getLength() * f, seg, True)
        c.drawPath(seg, wb.marker(RED, 9))
        pen(c, x - 40, y - 160, -30, 0.9)
        K.text(c, "画出来", x + 420, y - 330, 64, "hand", GREEN)
    return None


ev(j, k_draw, draw15, "ding", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "醒来一想，梦怎么就圆上了？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=4, notes=NOTES)
L.export(globals())
