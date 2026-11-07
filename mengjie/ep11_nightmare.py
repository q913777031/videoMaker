"""《梦的解析》11 噩梦：梦要是愿望，为什么还会做噩梦？（白板手绘 + AI 旁白，竖屏 2:3）

曲线故事（一夜的紧张曲线）：从被影子追、吓醒开始，紧张一路往上走——系统崩了、旧领导骂人——
到书里的解释（化妆没化好、守夜人叫醒你、惩罚梦），再到改结局，紧张慢慢落下来。
- 开场：一团黑影子 → 小李拼命跑 → 一颗咚咚跳的心，配音“吓醒了”逐字砸下；
- 痛点：梦里被影子追，跑不动、喊不出声；一下吓醒，心咚咚跳；
- 身边的例子（drop 在第 2 屏）：上线前一晚，梦里满屏红字“崩了”；刚换工作，梦里回到旧公司挨骂；
- 书中：弗洛伊德被问“噩梦算什么”；化妆没化好；心思戴的面具滑下来，人一看就怕；守夜人挡着动静，挡不住就把你叫醒；
  惩罚梦：肩膀上爱挑错的小人借梦罚你；
- 现在怎么看：噩梦像夜里的演习；一周好几次、影响白天，就去找医生聊聊；
- 三步：开灯喝水慢慢呼气、问像白天哪件事、白天给梦改结局（崩了 → 修 → 好了）；影子缩成一小团；评论区与下一讲。
文案与出处见 mengjie/PLAN.md「### 11」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, PAPER_W, WOOD, at_pop, bed, box, draw_freud, dream_cloud, moon, sleeper,
                         sparkle, sun)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross

SHADOW = "#3A3550"
SCREEN_RED = "#F6C3BE"


# ---------------------------------------------------------------- 本讲画面元件

def shadow(c, x, y, s=1.0, T=0.0, alpha=1.0, cute=False):
    """黑影子：一团带波浪下摆的影子，两只白眼睛，两只手往前伸。(x, y) 为身子中心。"""
    wob = math.sin(T * 6) * 8 * s
    p = skia.Path()
    p.moveTo(x - 110 * s, y + 120 * s)
    p.cubicTo(x - 130 * s, y - 40 * s, x - 90 * s, y - 170 * s, x, y - 170 * s)
    p.cubicTo(x + 90 * s, y - 170 * s, x + 130 * s, y - 40 * s, x + 110 * s, y + 120 * s)
    for i in range(4):
        x0 = x + 110 * s - i * 55 * s
        p.quadTo(x0 - 27 * s, y + (90 if i % 2 == 0 else 150) * s + wob, x0 - 55 * s, y + 120 * s)
    p.close()
    c.drawPath(p, K.paint(SHADOW, alpha))
    c.drawPath(p, wb.marker(BLACK, 6, alpha))
    if not cute:
        for sg in (-1, 1):
            C.line(c, (x + 70 * s, y - 20 * s + sg * 30 * s), (x + 190 * s, y - 50 * s + sg * 40 * s + wob), SHADOW, 18 * s,
                   alpha)
    for dx in (-35, 35):
        c.drawOval(skia.Rect.MakeXYWH(x + dx * s - 18 * s, y - 90 * s, 36 * s, 46 * s), K.paint(PAPER_W, alpha))
        c.drawCircle(x + dx * s + 6 * s, y - 64 * s, 8 * s, K.paint(BLACK, alpha))
    if cute:
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(x - 22 * s, y - 30 * s, 44 * s, 26 * s), 20, 140)
        c.drawPath(m, wb.marker(PAPER_W, 5, alpha))
    else:
        c.drawPath(P((x - 40 * s, y - 10 * s), (x - 20 * s, y + 6 * s), (x, y - 10 * s), (x + 20 * s, y + 6 * s),
                     (x + 40 * s, y - 10 * s)), wb.marker(PAPER_W, 5, alpha))


def runner(c, x, y, s, T, mood="o"):
    """跑着的小李（向右）：腿脚交替，身体前倾，身后有速度线。(x, y) 为脚底。"""
    ph = math.sin(T * 14)
    hy = y - 290 * s
    with K.at(c, x, y, 8):
        draw_li(c, 0, 0, s, mood, lh=(-70 * s, hy - y + 150 * s + ph * 40 * s), rh=(80 * s, hy - y + 150 * s - ph * 40 * s))
    for i in range(3):
        C.line(c, (x - 90 * s - i * 10, y - 200 * s + i * 50 * s), (x - 170 * s - i * 10, y - 200 * s + i * 50 * s), GRAY, 5)


def heart(c, x, y, r, T, beat=True, alpha=1.0):
    k = 1 + (0.12 * max(0.0, math.sin(T * 14)) if beat else 0)
    with K.at(c, x, y, 0, k):
        c.drawPath(C.heart_path(0, 0, r), K.paint("#F6C3BE", alpha))
        c.drawPath(C.heart_path(0, 0, r), wb.marker(RED, 7, alpha))


def monitor(c, x, y, w=320, h=220, mode="ok", T=0.0, alpha=1.0):
    """显示器：mode = ok（蓝屏几行字）/ red（满屏红字）/ fixed（绿勾）。(x, y) 为屏幕中心。"""
    C.line(c, (x, y + h / 2), (x, y + h / 2 + 50), GRAY, 12, alpha)
    C.line(c, (x - 60, y + h / 2 + 50), (x + 60, y + h / 2 + 50), GRAY, 10, alpha)
    fill = {"ok": "#DCE6F2", "red": SCREEN_RED, "fixed": "#D3EDDC"}[mode]
    box(c, x, y, w, h, fill, BLACK, 7, 12, alpha)
    if mode == "red":
        for r in range(4):
            fl = 0.6 + 0.4 * abs(math.sin(T * 9 + r))
            C.line(c, (x - w / 2 + 30, y - h / 2 + 40 + r * 45), (x + w / 2 - 30 - (r % 2) * 60, y - h / 2 + 40 + r * 45),
                   RED, 9, alpha * fl)
        c.drawPath(cross(x + w / 2 - 40, y - h / 2 + 40, 22), wb.marker(RED, 7, alpha))
    elif mode == "fixed":
        c.drawPath(check(x, y, 60), wb.marker(GREEN, 14, alpha))
    else:
        for r in range(3):
            C.line(c, (x - w / 2 + 30, y - h / 2 + 50 + r * 50), (x + w / 2 - 60 - r * 30, y - h / 2 + 50 + r * 50), BLUE, 6,
                   alpha)


def lantern(c, x, y, s=1.0, T=0.0):
    """提灯：(x, y) 为提手顶。"""
    C.line(c, (x, y), (x, y + 30 * s), BLACK, 5)
    glow = 0.25 + 0.1 * math.sin(T * 5)
    c.drawCircle(x, y + 85 * s, 80 * s, K.paint("#FFE39A", glow))
    box(c, x, y + 85 * s, 70 * s, 100 * s, "#FFE39A", ORANGE, 6, 12)
    C.line(c, (x - 35 * s, y + 35 * s), (x + 35 * s, y + 35 * s), BLACK, 8)


def watchman(c, x, y, s=1.0, T=0.0, arm="hold", mood="flat"):
    """守夜人：戴帽子的小人，一手提灯；arm = hold（另一手垂着）/ stop（手掌往外挡）/ shake（伸手摇醒）。(x, y) 为脚底。"""
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    lh = (x - 80 * s, hy + 150 * s)
    if arm == "stop":
        rh = (x + 120 * s, hy + 40 * s)
    elif arm == "shake":
        rh = (x - 140 * s + 12 * math.sin(T * 30), hy + 120 * s)
        lh = (x + 70 * s, hy + 160 * s)
    else:
        rh = (x + 70 * s, hy + 170 * s)
    draw_li(c, x, y, s, mood, lh=lh, rh=rh)
    coat = P((x - 50 * s, hy + 60 * s), (x + 50 * s, hy + 60 * s), (x + 60 * s, y - 90 * s), (x - 60 * s, y - 90 * s), close=True)
    c.drawPath(coat, K.paint("#5B6B8C"))
    c.drawPath(coat, wb.marker(BLACK, 6))
    c.drawRect(skia.Rect.MakeXYWH(x - 55 * s, hy - 75 * s, 110 * s, 40 * s), K.paint("#2E2A28"))
    C.line(c, (x - 80 * s, hy - 35 * s), (x + 80 * s, hy - 35 * s), "#2E2A28", 10)
    if arm == "stop":
        c.drawCircle(rh[0], rh[1], 18 * s, K.paint(PAPER_W))
        c.drawCircle(rh[0], rh[1], 18 * s, wb.marker(BLACK, 5))
    lp = (x + 80 * s, hy + 150 * s) if arm == "shake" else lh
    lantern(c, lp[0], lp[1], 0.8 * s, T)


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
    """开场：一团黑影子 → 小李拼命跑 → 一颗咚咚跳的心；随后“吓醒了”逐字砸下。"""
    b = H.b

    def shd(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc > 0:
            with at_pop(c, cx - 360, cy - 200, sc):
                shadow(c, cx - 360, cy - 220, 1.2, T)
        return None
    b.custom(j, 0, 0.3, shd, sfx="wood_low", gain=0.7)

    def run(c, kk, T):
        dt = T - H.tb(j, 1)
        if dt < 0:
            return None
        with at_pop(c, cx + 20, cy + 60, pop_scale(dt)):
            runner(c, cx + 20, cy + 60, 0.9, T)
        return None
    b.custom(j, 1, 1.3, run, sfx="tom", gain=0.75)

    def hrt(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        with at_pop(c, cx + 380, cy - 250, pop_scale(dt)):
            heart(c, cx + 380, cy - 250, 100, T)
        sparkle(c, cx + 380, cy - 250, dt, RED, 10, 130, 210)
        return None
    b.custom(j, 2, 2.3, hrt, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("11", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第七章 C、D（焦虑梦、梦是睡眠的守护者、惩罚梦）。",
    "书中说法：焦虑梦是伪装失手；梦像守夜人，扰动太大时把人叫醒；惩罚梦。",
    "“噩梦像演习”（威胁模拟理论，Revonsuo 2000）与改写噩梦结局（意象排练疗法）是今天的做法；噩梦频繁、影响白天请就医。"
    "小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：梦里被影子追，跑不动，喊不出声；一下吓醒，心咚咚跳
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_bed1 = 0
k_cl1 = nx(j, wt(0, 0, 0.6), k_bed1)
k_mute1 = nx(j, wt(0, 2, 0.4), k_cl1)
k_wake1 = nx(j, wt(0, 3, 0.5), k_mute1)
k_heart1 = nx(j, wt(1, 0, 0.5), k_wake1)
BED1 = (cx - 380, cy + 360)
HIP1 = (BED1[0] + 230, BED1[1] - 20)
CL1 = (cx + 90, cy - 250)
L.note("……", "咚咚")


def scene1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_bed1))
    if sc <= 0:
        return None
    woke = T >= tb(1, k_wake1)
    with at_pop(c, cx, BED1[1], sc):
        bed(c, *BED1, 560)
        sleeper(c, *HIP1, 0.8, T, tb(1, k_wake1), "o" if woke else "sad", sweat=True)
        moon(c, cx + 430, cy + 150, 50)
    return None


ev(j, k_bed1, scene1, "wood_low", 0.7)


def cloud1(c, kk, T, cx=cx, cy=cy):
    out = 1 - ease_in_out(clamp01((T - tb(1, k_wake1)) / 0.3))
    sc = pop_scale(T - tb(1, k_cl1)) * out
    if not dream_cloud(c, CL1[0], CL1[1], 860, 560, sc, tail_to=(HIP1[0] - 280, HIP1[1] - 90)):
        return None
    with at_pop(c, CL1[0], CL1[1], sc):
        gy = CL1[1] + 200
        C.line(c, (CL1[0] - 340, gy), (CL1[0] + 340, gy), BLACK, 6)
        near = 30 * math.sin(T * 1.5)
        shadow(c, CL1[0] - 180 + near, gy - 130, 0.75, T)
        runner(c, CL1[0] + 170, gy, 0.6, T)
        if T >= tb(1, k_mute1):
            g = pop_scale(T - tb(1, k_mute1))
            with K.at(c, CL1[0] + 250, CL1[1] - 180, 0, g):
                c.drawRoundRect(skia.Rect.MakeXYWH(-90, -45, 180, 90), 40, 40, K.paint(PAPER_W))
                c.drawPath(wb.bubble(0, 0, 180, 90, -1), wb.marker(BLACK, 6))
                K.text(c, "……", 0, 0, 56, "hand", GRAY)
    return None


ev(j, k_cl1, cloud1, "pop", 0.75)
b.hit(j, k_mute1, "rim", 0.75, "喊不出声")
b.hit(j, k_wake1, "kick", 0.9, "吓醒")
b.shots[j].shake = [(k_wake1, 10.0)]


def heart1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_heart1))
    if sc <= 0:
        return None
    x, y = cx + 250, cy - 160
    with at_pop(c, x, y, sc):
        heart(c, x, y, 100, T)
        K.text(c, "咚咚", x + 10, y + 170, 80, "hand", RED)
    return None


ev(j, k_heart1, heart1, "tom", 0.85)

# ================================================================ 屏 2：drop——上线前一晚，梦见系统崩了，满屏红字
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_bed2 = 0
k_cal2 = max(1, min(kq(j, wt(3, 0, 0.4), 1), KD - 2))
k_cl2 = max(k_cal2 + 1, min(kq(j, wt(3, 1, 0.4), k_cal2 + 1), KD - 1))
BED2 = (cx - 400, cy + 380)
HIP2 = (BED2[0] + 230, BED2[1] - 20)
CL2 = (cx + 130, cy - 250)
L.note("明天上线", "崩了")


def scene2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_bed2))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED2[1], sc):
        bed(c, *BED2, 560)
        sleeper(c, *HIP2, 0.8, T, None, "o" if T >= tb(2, KD) else "sad", sweat=False)
    return None


ev(j, k_bed2, scene2, "wood_low", 0.7)


def cal2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_cal2))
    if sc <= 0:
        return None
    with K.at(c, cx - 400, cy + 40, -4, sc):
        box(c, 0, 0, 260, 200, PAPER_W, BLACK, 6, 10)
        c.drawRect(skia.Rect.MakeXYWH(-130, -100, 260, 60), K.paint(RED))
        K.text(c, "明天", 0, -70, 42, "hand", "#FFFFFF")
        K.text(c, "上线", 0, 30, 70, "hand", RED)
    return None


L.note("明天", "上线")
ev(j, k_cal2, cal2, "wood_high", 0.7)


def cloud2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_cl2))
    if not dream_cloud(c, CL2[0], CL2[1], 780, 580, sc, tail_to=(HIP2[0] - 150, HIP2[1] - 110)):
        return None
    with at_pop(c, CL2[0], CL2[1], sc):
        red = T >= tb(2, KD)
        monitor(c, CL2[0] - 40, CL2[1] - 40, 420, 280, "red" if red else "ok", T)
        if red:
            for i in range(6):
                f = ((T - tb(2, KD)) * 0.8 + i / 6) % 1
                x = CL2[0] - 260 + (i * 97) % 480
                c.drawPath(cross(x, CL2[1] - 220 + f * 40, 18), wb.marker(RED, 6, 1 - f))
    return None


ev(j, k_cl2, cloud2, "pop", 0.7)
ev(j, KD, L.slam_text("崩了", cx + 260, cy + 160, 140, RED, j, KD, rot=-6), "kick", 0.95)

# ================================================================ 屏 3：刚换工作，梦见又回到旧公司，被领导骂
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_bed3 = 0
k_cl3 = nx(j, wt(4, 1, 0.3), k_bed3)
k_boss3 = nx(j, wt(4, 2, 0.2), k_cl3)
k_yell3 = nx(j, wt(4, 2, 0.7), k_boss3)
BED3 = (cx - 400, cy + 380)
HIP3 = (BED3[0] + 230, BED3[1] - 20)
CL3 = (cx + 100, cy - 240)
L.note("新工牌", "旧公司", "!!!")


def scene3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_bed3))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED3[1], sc):
        bed(c, *BED3, 560)
        sleeper(c, *HIP3, 0.8, T, None, "sad")
        x, y = BED3[0] + 670, BED3[1] - 10
        box(c, x, y + 20, 170, 140, WOOD, "#A9773E", 6, 8)
        with K.at(c, x, y - 120, 6):
            box(c, 0, 0, 150, 100, PAPER_W, BLUE, 5, 10)
            c.drawCircle(-40, -5, 22, wb.marker(BLUE, 4))
            C.line(c, (0, -15), (55, -15), BLUE, 4)
            C.line(c, (0, 15), (45, 15), BLUE, 4)
        K.text(c, "新工牌", x, y - 220, 46, "hand", BLUE)
    return None


ev(j, k_bed3, scene3, "wood_low", 0.7)


def cloud3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_cl3))
    if not dream_cloud(c, CL3[0], CL3[1], 860, 600, sc, tail_to=(HIP3[0] - 280, HIP3[1] - 90)):
        return None
    with at_pop(c, CL3[0], CL3[1], sc):
        gy = CL3[1] + 220
        box(c, CL3[0] - 40, CL3[1] - 200, 300, 90, "#3D4A63", BLACK, 6, 8)
        K.text(c, "旧公司", CL3[0] - 40, CL3[1] - 198, 56, "hand", "#FFFFFF")
        C.line(c, (CL3[0] - 340, gy), (CL3[0] + 340, gy), BLACK, 6)
        draw_li(c, CL3[0] + 180, gy, 0.55, "sad")
        if T >= tb(3, k_boss3):
            g = pop_scale(T - tb(3, k_boss3))
            yell = T >= tb(3, k_yell3)
            x = CL3[0] - 120
            hy = gy - 290 * 0.7
            with at_pop(c, x, gy, g):
                draw_boss(c, x, gy, 0.7, mood="o" if yell else "flat",
                          rh=(x + 110, hy + 60) if yell else None)
            if yell:
                for i in range(3):
                    ph = ((T - tb(3, k_yell3)) * 2 + i / 3) % 1
                    C.line(c, (x + 60 + ph * 40, hy - 30 + i * 30), (x + 100 + ph * 40, hy - 40 + i * 30), RED, 6, 1 - ph)
    return None


ev(j, k_cl3, cloud3, "pop", 0.7)
b.hit(j, k_boss3, "wood_high", 0.7, "领导出现")
ev(j, k_yell3, L.slam_text("!!!", cx + 360, cy - 400, 120, RED, j, k_yell3, rot=8), "rim", 0.85)
b.shots[j].shake = [(k_yell3, 7.0)]

# ================================================================ 屏 4：弗洛伊德被问：噩梦算什么？他答：化妆没化好
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_fr4 = kq(j, wt(5, 0, 0.3), 0)
k_q4 = nx(j, wt(5, 1, 0.4), k_fr4)
k_face4 = nx(j, wt(6, 0, 0.6), k_q4)
k_st4 = nx(j, wt(6, 1, 0.6), k_face4)
L.note("梦的解析", "噩梦算什么？", "没化好")


def fr4(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 340, cy + 40
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 0.85)
        with K.at(c, cx - 120, cy - 360, 6):
            box(c, 0, 0, 200, 260, NIGHT, BLACK, 6, 10)
            K.text(c, "梦的", 0, -45, 50, "serif_black", "#FFE39A")
            K.text(c, "解析", 0, 18, 50, "serif_black", "#FFE39A")
            moon(c, 0, 90, 24)
    return None


ev(j, k_fr4, pop_fn(j, k_fr4, fr4), "wood_low", 0.7)
ev(j, k_q4, L.pop_bubble("噩梦算什么？", cx + 250, cy - 380, j, k_q4, 56, RED, tail=-1), "pop", 0.75)


def face4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_face4))
    if sc <= 0:
        return None
    x, y = cx + 220, cy + 110
    with at_pop(c, x, y, sc):
        box(c, x, y, 400, 420, PAPER_W, BLACK, 6, 20)
        c.drawCircle(x, y - 10, 120, K.paint("#FBE3CF"))
        c.drawCircle(x, y - 10, 120, wb.marker(BLACK, 7))
        # 化了一半的妆：左半边涂得好好的，右半边糊了
        c.drawOval(skia.Rect.MakeXYWH(x - 80, y + 10, 40, 22), K.paint("#F6A5A0"))
        for dx in (-45, 45):
            c.drawCircle(x + dx, y - 40, 10, K.paint(BLACK))
        c.drawPath(P((x + 20, y - 80), (x + 70, y - 20), (x + 40, y + 30), (x + 90, y + 60)), wb.marker(SHADOW, 12, 0.7))
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(x - 35, y + 30, 70, 40), 200, 140)
        c.drawPath(m, wb.marker(BLACK, 6))
        with K.at(c, x - 170, y - 150, -40):
            c.drawRoundRect(skia.Rect.MakeXYWH(-12, -70, 24, 120), 10, 10, K.paint(WOOD))
            c.drawRoundRect(skia.Rect.MakeXYWH(-12, -70, 24, 120), 10, 10, wb.marker("#A9773E", 5))
            c.drawPath(P((-20, 50), (20, 50), (10, 100), (-10, 100), close=True), K.paint("#F6A5A0"))
    return None


ev(j, k_face4, face4, "wood_high", 0.7)
ev(j, k_st4, L.stamp("没化好", cx + 220, cy + 400, 76, j, k_st4, color=RED, rot=-6), "kick", 0.9)
b.shots[j].shake = [(k_st4, 7.0)]

# ================================================================ 屏 5：有些心思伪装得不够，面具滑下来，露了脸，人一看就害怕
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_mon5 = kq(j, wt(7, 0, 0.4), 0)
k_crk5 = nx(j, wt(7, 1, 0.5), k_mon5)
k_slip5 = nx(j, wt(7, 2, 0.4), k_crk5)
k_fear5 = nx(j, wt(7, 3, 0.5), k_slip5)
M5 = (cx + 180, cy - 160)
L.note("心思", "伪装得不够", "害怕")


def mask_path(x, y, r):
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - r, y - r * 1.1, r * 2, r * 2.2))
    return p


def mon5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_mon5))
    if sc <= 0:
        return None
    with at_pop(c, M5[0], M5[1], sc):
        shadow(c, M5[0], M5[1], 1.3, T)
        K.text(c, "心思", M5[0], M5[1] - 300, 64, "hand", SHADOW)
        slip = 0.0
        if T >= tb(5, k_slip5):
            slip = ease_in_out(clamp01((T - tb(5, k_slip5)) / 0.5))
        mx, my = M5[0] + 200 * slip, M5[1] - 70 + 400 * slip
        with K.at(c, mx, my, 50 * slip):
            mp = mask_path(0, 0, 120)
            c.drawPath(mp, K.paint(PAPER_W))
            c.drawPath(mp, wb.marker(BLACK, 7))
            for dx in (-45, 45):
                c.drawOval(skia.Rect.MakeXYWH(dx - 20, -40, 40, 26), K.paint(BLACK))
            m = skia.Path()
            m.addArc(skia.Rect.MakeXYWH(-50, 10, 100, 60), 20, 140)
            c.drawPath(m, wb.marker(BLACK, 7))
            c.drawOval(skia.Rect.MakeXYWH(-90, 10, 36, 20), K.paint("#F6A5A0"))
            c.drawOval(skia.Rect.MakeXYWH(54, 10, 36, 20), K.paint("#F6A5A0"))
            if T >= tb(5, k_crk5):
                f = ease_out(clamp01((T - tb(5, k_crk5)) / 0.3))
                pts = [(20, -130), (0, -80), (30, -40), (10, 0)]
                n = max(2, int(len(pts) * f))
                c.drawPath(P(*pts[:n]), wb.marker(RED, 6))
    return None


ev(j, k_mon5, mon5, "wood_low", 0.7)
ev(j, k_crk5, L.pop_text("伪装得不够", cx + 120, cy + 440, 64, ORANGE, j, k_crk5), "pop", 0.7)
b.hit(j, k_slip5, "tom", 0.8, "面具滑下来")


def fear5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_fear5))
    if sc <= 0:
        return None
    x, gy = cx - 360, cy + 460
    with at_pop(c, x, gy, sc):
        hy = gy - 290 * 0.9
        draw_li(c, x, gy, 0.9, "o", lh=(x - 100, hy - 30), rh=(x + 100, hy - 30))
        for n in range(2):
            ph = ((T - tb(5, k_fear5)) * 1.3 + n * 0.5) % 1.0
            A._sweat(c, x + (-80 if n else 80), hy - 20 + ph * 60, 1.0, 1 - ph)
    return None


ev(j, k_fear5, fear5, "kick", 0.85)
ev(j, k_fear5, L.slam_text("害怕", cx - 360, cy - 40, 110, RED, j, k_fear5, rot=-6), None)
b.shots[j].shake = [(k_fear5, 8.0)]

# ================================================================ 屏 6：守夜的人——平时挡着动静；挡不住就把你叫醒；吓醒也是保护
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_w6 = kq(j, wt(8, 0, 0.6), 0)
k_stop6 = nx(j, wt(8, 1, 0.5), k_w6)
k_big6 = nx(j, wt(9, 0, 0.5), k_stop6)
k_wake6 = nx(j, wt(9, 1, 0.6), k_big6)
k_prot6 = nx(j, wt(10, 1, 0.4), k_wake6)
BED6 = (cx - 520, cy + 400)
HIP6 = (BED6[0] + 230, BED6[1] - 20)
WX6, WY6 = cx + 130, cy + 470
L.note("守夜的人", "咚", "轰", "也是保护")


def bed6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_w6))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED6[1], sc):
        bed(c, *BED6, 500)
        sleeper(c, *HIP6, 0.75, T, tb(6, k_wake6), "o" if T >= tb(6, k_wake6) else "smile")
        moon(c, cx - 420, cy - 300, 50)
    return None


b.custom(j, k_w6, k_w6 + 0.3, bed6)


def w6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_w6))
    if sc <= 0:
        return None
    wake = T >= tb(6, k_wake6)
    arm = "shake" if wake else ("stop" if T >= tb(6, k_stop6) else "hold")
    x = WX6 - (100 * ease_out(clamp01((T - tb(6, k_wake6)) / 0.3)) if wake else 0)
    with at_pop(c, x, WY6, sc):
        watchman(c, x, WY6, 0.95, T, arm, "o" if T >= tb(6, k_big6) else "flat")
    K.text(c, "守夜的人", WX6, cy + 60, 60, "hand", NIGHT, clamp01(sc * 2))
    return None


ev(j, k_w6, w6, "wood_low", 0.7)


def noise6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_stop6)
    if T < t0:
        return None
    big = T >= tb(6, k_big6)
    for i in range(3):
        ph = ((T - t0) * 0.8 + i / 3) % 1
        x = lerp(cx + 540, cx + 320, ph)
        a = 0.0 if big else (1 - ph)
        K.text(c, "咚", x, cy + 30 + i * 90, 54, "hand", GRAY, a)
    if big:
        g = C.slam_scale(T - tb(6, k_big6))
        with K.at(c, cx + 380, cy - 300, 8, g):
            for r in (70, 120, 170):
                a = skia.Path()
                a.addArc(skia.Rect.MakeXYWH(-r, -r, 2 * r, 2 * r), 120, 120)
                c.drawPath(a, wb.marker(RED, 8))
            K.text(c, "轰", 60, 0, 120, "hand", RED)
    return None


ev(j, k_stop6, noise6, "pop", 0.7)
b.hit(j, k_big6, "tom", 0.85, "动静太大")
b.hit(j, k_wake6, "kick", 0.9, "把你叫醒")
b.shots[j].shake = [(k_big6, 8.0)]


def prot6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_prot6))
    if sc <= 0:
        return None
    with K.at(c, cx - 100, cy - 430, -3, sc):
        box(c, 0, 0, 440, 120, "#D3EDDC", GREEN, 7, 40)
        K.text(c, "也是保护", 30, 2, 66, "hand", GREEN)
        c.drawPath(check(-160, 0, 34), wb.marker(GREEN, 10))
    return None


ev(j, k_prot6, prot6, "ding", 0.8)

# ================================================================ 屏 7：惩罚梦——心里那个爱挑错的自己，借梦罚你一下
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_card7 = kq(j, wt(11, 0, 0.3), 0)
k_li7 = nx(j, wt(11, 0, 0.6), k_card7)
k_crit7 = nx(j, wt(11, 0, 0.85), k_li7)
k_cl7 = nx(j, wt(11, 1, 0.5), k_crit7)
GY7 = cy + 460
LX7 = cx - 260
L.note("惩罚梦", "爱挑错", "错", "罚站")


def card7(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(7, k_card7))
    if sc <= 0:
        return None
    with K.at(c, cx, cy - 450, -2, sc):
        box(c, 0, 0, 560, 160, PAPER_W, NIGHT, 9, 30)
        K.text(c, "惩罚梦", 0, 4, 100, "hand", NIGHT)
    return None


ev(j, k_card7, card7, "kick", 0.85)
b.shots[j].shake = [(k_card7, 7.0)]


def li7(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, LX7, GY7, sc):
        C.line(c, (cx - 560, GY7), (cx + 100, GY7), BLACK, 6)
        draw_li(c, LX7, GY7, 1.0, "sad")
    return None


ev(j, k_li7, pop_fn(j, k_li7, li7), "wood_low", 0.7)


def crit7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_crit7))
    if sc <= 0:
        return None
    # 肩膀上的小人：拿红笔
    sx, sy = LX7 + 60, GY7 - 290 + 80
    x, y = sx + 40, sy
    with at_pop(c, x, y, sc):
        hy = y - 290 * 0.42
        wag = 10 * math.sin(T * 8)
        draw_li(c, x, y, 0.42, "flat", rh=(x + 50, hy + 10 + wag))
        with K.at(c, x + 60, hy - 5 + wag, -30):
            c.drawRoundRect(skia.Rect.MakeXYWH(-6, -40, 12, 60), 4, 4, K.paint(RED))
        box(c, LX7 - 170, hy - 60, 220, 90, PAPER_W, RED, 5, 30)
        K.text(c, "爱挑错", LX7 - 170, hy - 58, 50, "hand", RED)
    return None


ev(j, k_crit7, crit7, "pop", 0.75)


def cl7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_cl7))
    x, y = cx + 250, cy - 50
    if not dream_cloud(c, x, y, 520, 460, sc, tail_to=(LX7 + 150, GY7 - 300)):
        return None
    with at_pop(c, x, y, sc):
        A.exam_paper(c, x - 80, y - 20, 200, 250, -6, "", None)
        for i in range(3):
            g = pop_scale(T - tb(7, k_cl7) - 0.2 - i * 0.15)
            if g > 0:
                with K.at(c, x - 80 + (i - 1) * 50, y - 40 + i * 50, 0, g):
                    c.drawPath(cross(0, 0, 28), wb.marker(RED, 8))
        draw_li(c, x + 130, y + 170, 0.45, "sad")
        K.text(c, "罚站", x + 130, y - 120, 50, "hand", RED)
    return None


ev(j, k_cl7, cl7, "rim", 0.8)

# ================================================================ 屏 8：现在怎么看——噩梦像夜里的演习；一周好几次、影响白天，就找医生聊聊
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_drill8 = kq(j, wt(12, 1, 0.4), 0)
k_pass8 = nx(j, wt(12, 2, 0.5), k_drill8)
k_week8 = nx(j, wt(13, 0, 0.6), k_pass8)
k_doc8 = nx(j, wt(13, 2, 0.4), k_week8)
L.note("夜里的演习", "白天怕的事", "一周好几次", "找医生聊聊")


def drill8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_drill8))
    if sc <= 0:
        return None
    x, y = cx, cy - 300
    if not dream_cloud(c, x, y, 900, 420, sc):
        return None
    with at_pop(c, x, y, sc):
        K.text(c, "夜里的演习", x, y - 130, 60, "hand", NIGHT)
        gy = y + 160
        shadow(c, x - 250, gy - 100, 0.55, T)
        draw_li(c, x + 20, gy, 0.5, "flat", lh=(x - 50, gy - 120), rh=(x + 90, gy - 150))
        go = T >= tb(8, k_pass8)
        if go:
            f = ease_out(clamp01((T - tb(8, k_pass8)) / 0.4))
            c.drawPath(wb.arrow((x + 100, gy - 80), (x + 100 + 120 * f, gy - 80), 0.0, 24), wb.marker(GREEN, 6))
            box(c, x + 320, gy - 80, 250, 90, PAPER_W, ORANGE, 5, 12)
            K.text(c, "白天怕的事", x + 320, gy - 78, 44, "hand", ORANGE)
    return None


ev(j, k_drill8, drill8, "pop", 0.75)
b.hit(j, k_pass8, "wood_high", 0.7, "先过一遍")


def week8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_week8))
    if sc <= 0:
        return None
    x, y = cx - 260, cy + 260
    with K.at(c, x, y, -3, sc):
        box(c, 0, 0, 440, 260, PAPER_W, BLACK, 6, 12)
        K.text(c, "一周好几次", 0, -85, 50, "hand", RED)
        for i in range(7):
            bx = -180 + i * 60
            box(c, bx, 30, 48, 48, PAPER_W, GRAY, 4, 6)
            if i in (0, 2, 3, 5):
                c.drawPath(cross(bx, 30, 18), wb.marker(RED, 6))
        K.text(c, "影响白天", 0, 95, 40, "hand", GRAY)
    return None


L.note("影响白天")
ev(j, k_week8, week8, "rim", 0.8)


def doc8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_doc8))
    if sc <= 0:
        return None
    x, gy = cx + 310, cy + 470
    with at_pop(c, x, gy, sc):
        hy = gy - 290 * 0.9
        draw_li(c, x, gy, 0.9, "smile", rh=(x - 90, hy + 120))
        coat = P((x - 52, hy + 55), (x + 52, hy + 55), (x + 66, gy - 80), (x - 66, gy - 80), close=True)
        c.drawPath(coat, K.paint(PAPER_W))
        c.drawPath(coat, wb.marker(BLACK, 6))
        C.line(c, (x + 20, hy + 100), (x + 20, hy + 140), RED, 7)
        C.line(c, (x, hy + 120), (x + 40, hy + 120), RED, 7)
        c.drawPath(P((x - 30, hy + 60), (x - 40, hy + 120), (x - 20, hy + 150)), wb.marker(GRAY, 5))
    return None


ev(j, k_doc8, doc8, "ding", 0.8)
ev(j, k_doc8, L.pop_bubble("找医生聊聊", cx + 160, cy + 60, j, k_doc8, 54, BLUE, tail=1), None)

# ================================================================ 屏 9：说回我们自己——偶尔做噩梦，吓醒以后；“三步”
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_li9 = kq(j, wt(14, 0, 0.5), 0)
k_3 = nx(j, wt(14, 2, 0.5), k_li9)
BED9 = (cx - 480, cy + 400)
HIP9 = (BED9[0] + 230, BED9[1] - 20)
L.note("三步")


def li9(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, BED9[1], sc):
        bed(c, *BED9, 520)
        sleeper(c, *HIP9, 0.8, 99.0, 0.0, "o", sweat=False)
        heart(c, HIP9[0] + 300, HIP9[1] - 230, 50, T)
        dream_cloud(c, cx - 300, cy - 300, 300, 220, 1.0)
        shadow(c, cx - 300, cy - 290, 0.45, T)
    return None


ev(j, k_li9, pop_fn(j, k_li9, li9), "wood_low", 0.7)


def three9(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(9, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 300, cy - 250, -4, sc):
        c.drawCircle(0, 0, 180, K.paint("#FFF4D6"))
        c.drawCircle(0, 0, 180, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 120, "hand", L.ACC)
    return None


ev(j, k_3, three9, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 10：做法一——稳住身体：开灯、喝口水、慢慢呼气
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_h10 = kq(j, wt(15, 0, 0.3), 0)
k_it10 = [nx(j, wt(15, 1, 0.7), k_h10)]
k_it10.append(nx(j, wt(15, 2, 0.5), k_it10[0]))
k_it10.append(nx(j, wt(15, 3, 0.5), k_it10[1]))
header(L, j, k_h10, cx, cy, "第一", "稳住身体", ev, pop_fn)
IT10 = ["开灯", "喝口水", "慢慢呼气"]
L.note(*IT10)


def it10(c, kk, T, cx=cx, cy=cy):
    for i, s_ in enumerate(IT10):
        g = pop_scale(T - tb(10, k_it10[i]))
        if g <= 0:
            continue
        x, y = cx - 350 + i * 350, cy - 100
        with K.at(c, x, y, (-3, 2, -2)[i], g):
            box(c, 0, 0, 310, 380, PAPER_W, (ORANGE, BLUE, GREEN)[i], 6, 16)
            if i == 0:
                c.drawCircle(0, -60, 110, K.paint("#FFE39A", 0.35 + 0.1 * math.sin(T * 4)))
                c.drawPath(P((-70, -40), (70, -40), (40, -120), (-40, -120), close=True), K.paint("#FFE39A"))
                c.drawPath(P((-70, -40), (70, -40), (40, -120), (-40, -120), close=True), wb.marker(ORANGE, 6))
                C.line(c, (0, -40), (0, 60), BLACK, 8)
                C.line(c, (-50, 60), (50, 60), BLACK, 8)
            elif i == 1:
                p = P((-55, -130), (55, -130), (42, 50), (-42, 50), close=True)
                c.drawPath(p, K.paint(PAPER_W))
                c.drawRect(skia.Rect.MakeXYWH(-46, -40, 92, 88), K.paint("#BFDDF7"))
                c.drawPath(p, wb.marker(BLUE, 6))
            else:
                draw_li(c, -40, 80, 0.55, "o")
                for r_ in range(3):
                    ph = (T * 0.6 + r_ / 3) % 1
                    c.drawPath(P((10 + ph * 80, -130 + r_ * 30), (40 + ph * 80, -140 + r_ * 30), (70 + ph * 80, -130 + r_ * 30)),
                               wb.marker(GREEN, 5, 1 - ph))
            K.text(c, s_, 0, 140, 56, "hand", BLACK)
    return None


ev(j, k_it10[0], it10, "pop", 0.7)
b.hit(j, k_it10[1], "pop", 0.7, "喝口水")
b.hit(j, k_it10[2], "shaker", 0.7, "慢慢呼气")


def li10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_it10[2]) - 0.4)
    if sc <= 0:
        return None
    x, gy = cx, cy + 480
    with at_pop(c, x, gy, sc):
        draw_li(c, x, gy, 0.7, "smile")
        heart(c, x + 150, gy - 230, 36, T, beat=False)
    return None


b.custom(j, k_it10[2], k_it10[2] + 0.3, li10)

# ================================================================ 屏 11：做法二——问一句：梦里最怕的东西，像白天的哪件事
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_h11 = kq(j, wt(16, 0, 0.3), 0)
k_cl11 = nx(j, wt(16, 1, 0.6), k_h11)
k_ln11 = nx(j, wt(16, 2, 0.3), k_cl11)
k_day11 = nx(j, wt(16, 2, 0.8), k_ln11)
header(L, j, k_h11, cx, cy, "第二", "问一句", ev, pop_fn)
L.note("梦里最怕的", "白天", "上线", "?")


def cl11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_cl11))
    x, y = cx - 250, cy - 170
    if not dream_cloud(c, x, y, 480, 420, sc):
        return None
    with at_pop(c, x, y, sc):
        shadow(c, x, y + 40, 0.75, T)
        K.text(c, "梦里最怕的", x, y - 160, 46, "hand", NIGHT)
    return None


ev(j, k_cl11, cl11, "pop", 0.7)


def ln11(c, kk, T, cx=cx, cy=cy):
    t0 = tb(11, k_ln11)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.45))
    a, z = (cx - 30, cy - 100), (cx + 140, cy + 60)
    c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), 0.25, 34), wb.marker(NIGHT, 8))
    K.text(c, "?", cx + 110, cy - 130, 110, "hand", L.ACC, f)
    return None


ev(j, k_ln11, ln11, "wood_high", 0.7)


def day11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_day11))
    if sc <= 0:
        return None
    with K.at(c, cx + 300, cy + 230, 4, sc):
        box(c, 0, 0, 340, 320, PAPER_W, BLACK, 7, 12)
        c.drawRect(skia.Rect.MakeXYWH(-170, -160, 340, 80), K.paint(RED))
        K.text(c, "白天", 0, -120, 50, "hand", "#FFFFFF")
        monitor(c, -20, 10, 160, 100, "red", T)
        K.text(c, "上线", 100, 110, 50, "hand", RED)
    return None


ev(j, k_day11, day11, "ding", 0.8)


def li11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_cl11) - 0.3)
    if sc <= 0:
        return None
    x, gy = cx - 250, cy + 470
    with at_pop(c, x, gy, sc):
        hy = gy - 290 * 0.85
        draw_li(c, x, gy, 0.85, "flat", rh=(x + 40, hy + 50))
    return None


b.custom(j, k_cl11, k_cl11 + 0.3, li11)

# ================================================================ 屏 12：做法三——给梦改个结局：系统崩了 → 一步步修 → 修好
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_h12 = kq(j, wt(17, 0, 0.3), 0)
k_p12 = [nx(j, wt(17, 1, 0.6), k_h12)]
k_p12.append(nx(j, wt(17, 2, 0.6), k_p12[0]))
k_p12.append(nx(j, wt(17, 3, 0.6), k_p12[1]))
header(L, j, k_h12, cx, cy, "第三", "改个结局", ev, pop_fn)
P12 = ["崩了", "一步步修", "修好了"]
L.note(*P12)


def p12(c, kk, T, cx=cx, cy=cy):
    for i, s_ in enumerate(P12):
        g = pop_scale(T - tb(12, k_p12[i]))
        if g <= 0:
            continue
        x, y = cx, cy - 300 + i * 290
        with K.at(c, x, y, (-1.5, 1.5, -1)[i], g):
            box(c, 0, 0, 860, 250, PAPER_W, (RED, ORANGE, GREEN)[i], 6, 16)
            if i == 0:
                monitor(c, -250, -20, 220, 140, "red", T)
            elif i == 1:
                monitor(c, -300, -20, 180, 120, "ok", T)
                draw_li(c, -130, 110, 0.4, "flat", rh=(-180, 0))
                with K.at(c, -190, -10, -30 + 15 * math.sin(T * 8)):
                    C.line(c, (0, -30), (0, 30), GRAY, 10)
                    c.drawCircle(0, -36, 14, wb.marker(GRAY, 7))
            else:
                monitor(c, -250, -20, 220, 140, "fixed", T)
            K.text(c, s_, 140, 0, 72, "hand", (RED, ORANGE, GREEN)[i])
        if i > 0:
            C.line(c, (cx + 380, cy - 300 + (i - 1) * 290 + 125), (cx + 380, cy - 300 + i * 290 - 125), GRAY, 6, clamp01(g))
    return None


ev(j, k_p12[0], p12, "rim", 0.75)
b.hit(j, k_p12[1], "pop", 0.7, "一步步修")
b.hit(j, k_p12[2], "ding", 0.8, "修好了")

# ================================================================ 屏 13：这样看梦——改过结局，影子缩成一小团，没那么吓人
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_cl13 = 0
k_shr13 = nx(j, wt(18, 1, 0.4), k_cl13)
k_txt13 = nx(j, wt(18, 2, 0.6), k_shr13)
CL13 = (cx, cy - 150)
L.note("没那么吓人")


def cl13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_cl13))
    if not dream_cloud(c, CL13[0], CL13[1], 900, 680, sc):
        return None
    m = ease_in_out(clamp01((T - tb(13, k_shr13)) / 0.5)) if T >= tb(13, k_shr13) else 0.0
    gy = CL13[1] + 220
    with at_pop(c, CL13[0], CL13[1], sc):
        C.line(c, (CL13[0] - 340, gy), (CL13[0] + 340, gy), BLACK, 6)
        s_ = lerp(1.4, 0.45, m)
        shadow(c, CL13[0] - 130, gy - 120 * s_, s_, T, cute=m > 0.5)
        draw_li(c, CL13[0] + 200, gy, 0.7, "smile" if m > 0.5 else "o",
                rh=(CL13[0] + 130, gy - 290 * 0.7 + 90) if m > 0.5 else None)
    if m > 0:
        sparkle(c, CL13[0] - 130, gy - 60, T - tb(13, k_shr13), YELLOW, 10, 80, 170)
    return None


ev(j, k_cl13, cl13, "pop", 0.7)
b.hit(j, k_shr13, "clap", 0.8, "影子缩小")
ev(j, k_txt13, L.slam_text("没那么吓人", cx, cy + 380, 120, L.ACC, j, k_txt13, rot=-3), "kick", 0.9)
b.shots[j].shake = [(k_txt13, 7.0)]

# ================================================================ 屏 14：评论区——改结局；你已经从梦里跑出来了；下一讲预告
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_box14 = kq(j, wt(19, 0, 0.4), 0)
k_type14 = nx(j, wt(20, 0, 0.5), k_box14)
k_likes14 = nx(j, wt(20, 1, 0.5), k_type14)
k_out14 = nx(j, wt(21, 2, 0.3), k_likes14)
k_n = nx(j, wt(22, 0, 0.1), k_out14)
L.note("评论区", "改成我把狗领回家", "发送", "+1", "跑出来了")


def input14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_box14))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(14, k_type14):
            s_ = "改成我把狗领回家"
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


def out14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_out14))
    if sc <= 0:
        return None
    gy = cy + 420
    with at_pop(c, cx, gy, sc):
        C.line(c, (cx - 520, gy), (cx + 520, gy), BLACK, 6)
        dream_cloud(c, cx - 300, gy - 200, 380, 330, 1.0)
        shadow(c, cx - 320, gy - 190, 0.35, T, cute=True)
        f = ease_out(clamp01((T - tb(14, k_out14)) / 0.8))
        runner(c, lerp(cx - 60, cx + 200, f), gy, 0.85, T, "smile")
        sun(c, cx + 460, gy - 430, 50)
        K.text(c, "跑出来了", cx + 170, gy - 440, 64, "hand", GREEN)
    sparkle(c, cx + 200, gy - 260, T - tb(14, k_out14) - 0.6, YELLOW, 10, 110, 200)
    return None


ev(j, k_out14, out14, "ding", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "弗洛伊德自己的梦，他是怎么一块块拆开的？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=6, notes=NOTES)
L.export(globals())
