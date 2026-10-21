"""10 饭后走动：吃完饭，要不要走走？"""

import math

import skia

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Shot, Txt

from . import kit_tang as T
from .common import GROUND, SERIES, TITLES, ending, ground, refs

ACC = "#3E8EA8"
MUSCLE = "#C9605A"
REFS = refs("Buffey, A. J. et al. (2022). Sports Medicine, 52(8), 1765–1787.")


# ---------------------------------------------------------------- 1 沙发

def sofa(g):
    ground(g)
    c = g.c
    with K.paper(c, 1, 0.8):
        K.rr(c, 560, GROUND - 60, 460, 120, 24, K.mix(ACC, K.PAPER, 0.45))
        K.rr(c, 560, GROUND - 170, 460, 110, 30, K.mix(ACC, K.PAPER, 0.3))
        K.rr(c, 330, GROUND - 100, 60, 200, 24, K.mix(ACC, K.PAPER, 0.25))
        K.rr(c, 790, GROUND - 100, 60, 200, 24, K.mix(ACC, K.PAPER, 0.25))


# ---------------------------------------------------------------- 2 / 7 / 14 曲线

def rising(c, g, t, d):
    p = clamp01(g.since(1) / max(0.1, g.b(10) - g.b(1)))
    T.chart(c, 0, 0, 820, 520, [(lambda u: T.bump(u, 1.0, 0.22, 2.4), T.SPIKE, p * 0.55, 9, "")])
    k = clamp01(g.since(6) / 0.3)
    if k > 0:
        K.arrow(c, (-200, 120), (-200, -140), T.SPIKE, 10, k, k, 0, 30)


def sit_vs_walk(c, g, t, d):
    T.chart(c, 0, 0, 820, 520, [
        (lambda u: T.bump(u, 1.0, 0.22, 2.4), T.SPIKE, clamp01(g.since(1) / 1.6), 9, "饭后坐着"),
        (lambda u: T.bump(u, 0.5, 0.26, 1.8), T.FLAT, clamp01(g.since(6) / 1.6), 9, "饭后走动")])


def calm(c, g, t, d):
    T.chart(c, 0, 0, 760, 460, [(lambda u: T.bump(u, 0.5, 0.26, 1.8), T.FLAT, clamp01(g.since(0) / 2.0), 9, "")])


# ---------------------------------------------------------------- 5 / 6 肌肉海绵

def muscle_shape(c, x, y, w, h, fill=0.0, alpha=1.0, pulse=1.0):
    """肌肉：一块带纹理的长椭圆，fill 为吸进去的葡萄糖量。"""
    with K.at(c, x, y, 0, pulse):
        with K.paper(c, alpha, 0.9):
            K.rr(c, 0, 0, w, h, h / 2, MUSCLE)
        for i in range(5):
            yy = -h * 0.3 + i * h * 0.15
            K.seg(c, -w * 0.35, yy, w * 0.35, yy, K.shade(MUSCLE, 0.2), 4, alpha * 0.8)
        n = int(10 * clamp01(fill))
        for i in range(n):
            T.hexa(c, -w * 0.3 + (i % 5) * w * 0.15, -h * 0.12 + (i // 5) * h * 0.26, 14, T.GLU, alpha)


def muscle_use(c, g, t, d):
    T.vessel(c, 0, -230, 880, 170)
    K.text(c, "血液", -400, -350, 30, "sans_medium", K.INK2, 1, "left")
    T.particles(c, -420, -230, 420, -230, g.t, 10, 16, T.GLU, 1, 0.22)
    work = clamp01(g.since(2) / 0.3)
    pulse = 1 + 0.05 * work * math.sin(g.t * 9)
    muscle_shape(c, 0, 200, 560, 220, clamp01(g.since(4) / 2.5), 1, pulse)
    K.text(c, "肌肉", 0, 350, 32, "serif_black", MUSCLE)
    if g.since(3) >= 0:
        for i in range(5):
            u = (g.t * 0.7 + i / 5) % 1
            T.hexa(c, -180 + i * 90, -150 + 260 * u, 16, T.GLU, min(1, (1 - u) * 4))


def sponge(c, g, t, d):
    """血管里的葡萄糖越来越少，被下面的肌肉吸走。"""
    T.vessel(c, 0, -230, 880, 170)
    left = 1 - clamp01(g.since(2) / 3.0) * 0.7
    T.particles(c, -420, -230, 420, -230, g.t, max(3, int(12 * left)), 16, T.GLU, 1, 0.22)
    muscle_shape(c, 0, 200, 560, 220, 0.4 + 0.6 * clamp01(g.since(2) / 3.0), 1, 1 + 0.03 * math.sin(g.t * 5))
    for i in range(6):
        u = (g.t * 0.9 + i / 6) % 1
        T.hexa(c, -220 + i * 88, -150 + 260 * u, 15, T.GLU, min(1, (1 - u) * 4))
    k = clamp01(g.since(6) / 0.35)
    if k > 0:
        K.pill(c, 330, 30, "像海绵一样吸走", 32, MUSCLE, K.PAPER, k)


# ---------------------------------------------------------------- 8 三种动法

def broom(c, x, y, s, t):
    K.seg(c, x, y - s * 0.6, x + s * 0.15, y + s * 0.2, "#8A6A45", s * 0.06)
    with K.at(c, x + s * 0.18, y + s * 0.3, 10 * math.sin(t * 6)):
        K.poly(c, [(-s * 0.18, -s * 0.1), (s * 0.18, -s * 0.1), (s * 0.28, s * 0.25), (-s * 0.28, s * 0.25)], K.GOLD)


def three_ways(c, g, t, d):
    labels = ("散步", "做家务", "爬楼梯")
    for i, lab in enumerate(labels):
        k = clamp01(g.since(i * 1.5) / 0.3)
        if k <= 0:
            continue
        x = -320 + i * 320
        with K.fade(c, k):
            K.card(c, x, 0, 280, 420, K.PAPER, 1, 24, 0.9)
            ph = g.t * 6
            if i == 0:
                K.figure(c, x, 130, 230, K.walk(ph, 1.0), K.HERO, mood="smile", hair="short")
            elif i == 1:
                K.figure(c, x - 30, 130, 230, "push", K.HERO, mood="calm", hair="short")
                broom(c, x + 70, 60, 200, g.t)
            else:
                K.stairs(c, x - 10, 140, 4, 34, 40, K.mix(ACC, K.PAPER, 0.4))
                K.figure(c, x - 40, 140 - 40 * (int(g.t * 2) % 3), 200, "climb", K.HERO, mood="happy", hair="short")
            K.text(c, lab, x, 170, 36, "serif_black", ACC)


# ---------------------------------------------------------------- 9 十分钟

def ten_min(c, g, t, d):
    k = clamp01(g.since(0) / 0.3)
    with K.at(c, 0, 0, 0, 0.4 + 0.6 * K.ease_out_back(k, 1.6)):
        with K.paper(c, k, 1.0):
            K.dot(c, 0, 0, 230, K.PAPER)
        K.ring(c, 0, 0, 230, K.INK, 12, k)
        p = clamp01(g.since(1) / 2.0) * (10 / 60)
        if p > 0:
            path = skia.Path()
            path.moveTo(0, 0)
            path.arcTo(skia.Rect.MakeLTRB(-205, -205, 205, 205), -90, 360 * p, False)
            path.close()
            c.drawPath(path, K.paint(ACC, 0.85 * k))
        for i in range(12):
            a = math.radians(i * 30 - 90)
            K.seg(c, 185 * math.cos(a), 185 * math.sin(a), 210 * math.cos(a), 210 * math.sin(a), K.INK, 6, k)
        kk = clamp01(g.since(3) / 0.3)
        if kk > 0:
            K.text(c, "10 分钟", 0, 60, 60, "black", K.INK, kk)


# ---------------------------------------------------------------- 10 不用剧烈

def easy_walk(c, g, t, d):
    ph = g.t * 6
    K.figure(c, -230, 280, 340, K.walk(ph * 1.6, 1.8), K.OTHER2, mood="worried", hair="short", lift=0.7)
    K.text(c, "拼命跑", -230, 340, 34, "serif_black", K.INK3)
    k = clamp01(g.since(2) / 0.3)
    if k > 0:
        K.icon(c, "cross", -230, -140, 120, K.RED, k, 0.5)
    kk = clamp01(g.since(4) / 0.3)
    if kk > 0:
        K.figure(c, 230, 280, 340, K.walk(ph * 0.8, 0.8), K.HERO, alpha=kk, mood="smile", hair="short")
        K.text(c, "轻松走", 230, 340, 34, "serif_black", ACC, kk)
    k3 = clamp01(g.since(6) / 0.3)
    if k3 > 0:
        K.icon(c, "check", 230, -140, 120, K.GREEN, k3, 0.5)


# ---------------------------------------------------------------- 11 站起来也好

def office(g):
    ground(g)
    K.seat(g.c, 760, GROUND, 320, 250, K.mix(K.OTHER2, K.PAPER, 0.4))
    K.seat(g.c, 420, GROUND, 170, 100, K.mix(K.OTHER, K.PAPER, 0.3))


# ---------------------------------------------------------------- 12 研究柱状图

def study_bars(c, g, t, d):
    vals = (100, 90.5, 83)
    labels = ("一直坐着", "穿插站立", "穿插走动")
    cols = (K.INK3, K.mix(ACC, K.PAPER, 0.35), ACC)
    w, h, base = 220, 520, 300
    for i in range(3):
        k = ease_in_out(clamp01(g.since(1 + i * 2) / 0.6))
        if k <= 0:
            continue
        x = -300 + i * 300
        bh = h * vals[i] / 100 * k
        K.rr(c, x, base - bh / 2, w, bh, 16, cols[i])
        K.text(c, labels[i], x, base + 44, 34, "sans_medium", K.INK2)
        if i and k >= 1:
            K.text(c, ("", "约 −9.5%", "约 −17%")[i], x, base - bh - 40, 44, "black", cols[i] if i == 2 else K.INK2)
    K.text(c, "餐后血糖（以一直坐着为 100，示意比例）", 0, -310, 26, "sans_medium", K.INK3)


# ---------------------------------------------------------------- 13 小练习

def walk_path(c, g, t, d):
    p = clamp01(g.since(1) / max(0.1, g.b(14) - g.b(1)))
    K.road(c, -420, 230, 420, 230, K.LINE, 70, 1, 1)
    x = -380 + 760 * p
    K.figure(c, x, 220, 260, K.walk(p * 40, 1.0), K.HERO, mood="smile", hair="short")
    K.ring(c, 0, -250, 110, K.LINE, 16)
    K.ring(c, 0, -250, 110, ACC, 16, 1, p, -90)
    K.text(c, f"{int(round(p * 10))}", 0, -258, 70, "black", K.INK)
    K.text(c, "分钟", 0, -190, 28, "sans_medium", K.INK2)


def build() -> Episode:
    shots = [
        Shot(3, "吃完饭，|往沙发上一躺？", "情境演绎", [
            Fig(560, GROUND - 120, 340, at=0, pose="sit", mood="happy", hair="short",
                moves=[(6, dict(pose="sit_sad", mood="flat", sfx="tom", note="主角瘫进沙发"))]),
        ], draw=sofa, hits=[(0, "wood_low", 0.6, "沙发")], note="饭后主角坐进沙发，第 6 拍整个人瘫下去"),
        Shot(3, "这时，血糖|正在往上走。", "机制示意", [
            Custom(rising, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "曲线开始上升"), (6, "wood_high", 0.8, "向上箭头")],
            note="曲线图上饭后血糖开始上升，竖起一支向上的箭头（示意）"),
        Shot(2, "书里的办法很简单：|起来动一动。", "书中观点", [
            Fig(540, GROUND, 360, at=0, enter="none", pose="sit_sad", mood="flat", hair="short",
                moves=[(2, dict(pose="cheer", mood="happy", sfx="clap", note="主角起身伸懒腰"))]),
        ], draw=ground, text_beat=0, note="主角从瘫坐状态一下站起来伸懒腰"),
        Shot(3, "饭后走动：|吃完动上一会儿。", "书中观点", [
            Big("饭后走动", 540, 470, 150, at=0, sfx="kick", sub="move after eating", note="概念落版（音乐 drop）"),
            Fig(200, GROUND, 330, at=0, enter="rise", mood="smile", hair="short",
                moves=[(2, dict(x=880, dur=4.0, sfx="wood_high", note="主角开始散步")),
                       (10, dict(face=-1, sfx="wood_low", note="走到头转身"))]),
        ], draw=ground, note="drop 处“饭后走动”砸下；主角从左走到右，第 10 拍转身"),
        Shot(3, "肌肉一动，|会直接用掉葡萄糖。", "书中观点", [
            Custom(muscle_use, x=540, y=800, at=0, enter="fade"),
        ], hits=[(2, "rim", 0.8, "肌肉开始收缩"), (4, "shaker", 0.7, "葡萄糖流进肌肉")],
            note="上方血管里流着葡萄糖，下方肌肉一收一缩，葡萄糖一颗颗落进肌肉"),
        Shot(3, "像海绵一样，|把血里的葡萄糖吸走。", "机制示意", [
            Custom(sponge, x=540, y=800, at=0, enter="fade"),
        ], hits=[(2, "shaker", 0.7, "血管里的葡萄糖变少"), (6, "wood_high", 0.8, "“像海绵一样吸走”")],
            note="血管里的葡萄糖越来越少，肌肉像海绵一样越吸越满"),
        Shot(3, "饭后坐着和饭后走动，|曲线不一样。", "书中观点", [
            Custom(sit_vs_walk, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "“坐着”曲线画出"), (6, "wood_low", 0.7, "“走动”曲线画出")],
            note="同一张图：饭后坐着的高尖峰，饭后走动的平缓曲线（示意）"),
        Shot(2, "散步、做家务、|爬楼梯都行。", "书中观点", [
            Custom(three_ways, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.7, "散步"), (2, "wood_low", 0.7, "做家务"), (3, "bongo_high", 0.7, "爬楼梯")],
            text_beat=0, note="三张卡：散步、扫地做家务、爬楼梯"),
        Shot(2, "十分钟，|也有用。", "书中观点", [
            Custom(ten_min, x=540, y=780, at=0, enter="none", sfx="wood_low", note="表盘弹出"),
        ], hits=[(3, "rim", 0.8, "“10 分钟”")], text_beat=0, note="表盘上扫出十分钟的扇形"),
        Shot(3, "不需要剧烈运动，|轻松走走就行。", "常见误解", [
            Custom(easy_walk, x=540, y=820, at=0, enter="fade"),
        ], hits=[(2, "rim", 0.8, "拼命跑：打叉"), (4, "wood_high", 0.7, "轻松走出现"), (6, "clap", 0.8, "轻松走：打勾")],
            note="左边拼命跑的人被打叉，右边轻松散步的人打勾"),
        Shot(3, "就算只是站起来，|也比一直坐着好。", "研究证据", [
            Fig(420, GROUND - 100, 340, at=0, pose="sit", mood="flat", hair="short",
                moves=[(4, dict(pose="stand", y=GROUND, mood="smile", sfx="wood_high", note="主角从工位站起来"))]),
        ], draw=office, note="主角从工位椅子上站起来"),
        Shot(4, "7 项研究汇总：|走动，血糖低约 17%。", "研究证据", [
            Custom(study_bars, x=540, y=760, at=0, enter="fade"),
            Txt("Buffey 等，2022，Sports Medicine", 540, 1245, 26, at=2, font="sans_medium", color=K.INK2),
        ], research=True, hits=[(1, "wood_low", 0.7, "“一直坐着”柱"), (3, "wood_high", 0.7, "“穿插站立”柱"),
                                (5, "bongo_high", 0.8, "“穿插走动”柱")],
            note="三根柱：一直坐着 100、穿插站立约低 9.5%、穿插轻度走动约低 17%"),
        Shot(4, "小练习：下一顿饭后，|散步十分钟。", "小练习", [
            Custom(walk_path, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "开始散步"), (14, "clap", 0.8, "十分钟走完")],
            note="主角沿小路散步，右上角计时环从 0 走到 10 分钟"),
        Shot(2, "动一动，|曲线就缓一缓。", "书中观点", [
            Custom(calm, x=540, y=780, at=0, enter="pop", sfx="wood_high", note="平缓曲线"),
        ], text_beat=0, note="一条平缓的饭后曲线（示意）"),
        ending(10, REFS),
    ]
    return Episode(10, "walk", "饭后走动", TITLES[10], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[10]}｜控糖革命10 饭后走动", hashtags="#控糖 #血糖 #饭后散步 #控糖革命 #健康",
                   cover_title="吃完饭，|要不要【走走】？", cover_sub="控糖革命 · 饭后走动", cover_shot=6, cover_t=5.0,
                   notes=[
                       "“饭后动一动，十分钟也有用”是书中第 8 个方法的大意，标“书中观点”。",
                       "研究证据：Buffey 等（2022，Sports Medicine 52(8):1765–1787）汇总 7 项急性试验：与久坐相比，"
                       "穿插轻度步行使血糖平均降低约 17.01%，穿插站立约 9.51%（数值为第一作者向 CNN 的说明）。"
                       "这些试验多为一整天里每 20–30 分钟起身 2–5 分钟，不全是“饭后散步”。第 12 镜柱高为按该比例的示意。",
                       "第 2、7、14 镜曲线为示意，不是实测数据。",
                       "“肌肉像海绵一样吸走葡萄糖”为比喻：肌肉收缩时可不依赖胰岛素摄取葡萄糖。",
                   ], **SERIES).build()
