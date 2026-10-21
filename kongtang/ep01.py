"""01 葡萄糖：血糖曲线，是什么样的？"""

import math

import skia

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Big, Bubble, Custom, Episode, Fig, Icon, Shot

from . import kit_tang as T
from .common import GROUND, SERIES, TITLES, ending, ground, refs

ACC = "#D9773A"
REFS = refs("American Diabetes Association. Standards of Care in Diabetes（空腹与餐后 2 小时血糖诊断切点）")


# ---------------------------------------------------------------- 1–3 钩子

def desk(g):
    ground(g)
    K.seat(g.c, 560, GROUND, 170, 100, K.mix(K.OTHER, K.PAPER, 0.3))
    K.seat(g.c, 860, GROUND, 300, 230, K.mix(K.OTHER2, K.PAPER, 0.4))


def zzz(c, g, t, d):
    for i in range(3):
        k = clamp01(g.since(4 + 2 * i) / 0.4)
        if k > 0:
            dy = -30 * ((g.t * 0.5 + i * 0.3) % 1)
            K.text(c, "Z", i * 46, -i * 56 + dy, 50 + 14 * i, "black", K.INK3, k)


def book_card(c, g, t, d):
    k = clamp01(g.since(0) / 0.4)
    with K.at(c, 0, 0, -4, 0.4 + 0.6 * K.ease_out_back(k, 1.6)):
        with K.paper(c, k, 1.0):
            K.rr(c, 0, 0, 300, 420, 14, "#F2EADB")
            K.rr(c, -135, 0, 30, 420, 6, K.shade(ACC, 0.2))
        K.text(c, "控糖", 10, -110, 70, "serif_black", ACC, k)
        K.text(c, "革命", 10, -30, 70, "serif_black", ACC, k)
        path_k = clamp01(g.since(1) / 0.8)
        p = skia.Path()
        for i in range(41):
            u = i / 40 * path_k
            (p.moveTo if i == 0 else p.lineTo)(-110 + u * 230, 130 - 90 * T.bump(u, 0.9, 0.3))
        c.drawPath(p, K.paint(T.SPIKE, k, 6))


# ---------------------------------------------------------------- 5 淀粉 → 葡萄糖

def breakdown(c, g, t, d):
    T.food(c, "rice", -330, -40, 200, clamp01(g.since(0) / 0.3))
    T.food(c, "bread", -330, 220, 170, clamp01(g.since(1) / 0.3))
    k = clamp01(g.since(3) / 0.4)
    if k > 0:
        K.arrow(c, (-180, 90), (20, 90), K.INK3, 10, k, k, 0, 30)
    if g.since(4) >= 0:
        for i in range(14):
            a = i * 2.4
            r = 60 + 22 * (i % 4)
            kk = clamp01(g.since(4 + i * 0.25) / 0.3)
            T.hexa(c, 260 + r * math.cos(a), 90 + r * math.sin(a), 24, T.GLU, kk, g.t * 40 + i * 20)
    kk = clamp01(g.since(8) / 0.35)
    if kk > 0:
        K.pill(c, 260, 290, "葡萄糖", 36, T.GLU, K.PAPER, kk)


# ---------------------------------------------------------------- 6 胰岛素开门

def insulin(c, g, t, d):
    T.vessel(c, 0, -170, 900, 190)
    T.particles(c, -440, -170, 440, -170, g.t, 12, 18, T.GLU, 1, 0.25)
    K.text(c, "血液", -400, -300, 30, "sans_medium", K.INK2, 1, "left")
    open_k = ease_out(clamp01(g.since(5) / 0.4))
    fill = clamp01(g.since(6) / 2.0)
    T.cell(c, 150, 210, 160, open_k, fill)
    K.text(c, "细胞", 150, 410, 30, "sans_medium", K.INK2)
    kk = clamp01(g.since(2) / 0.35)
    if kk > 0:
        x = -230 + 160 * ease_in_out(clamp01(g.since(3) / 0.8))
        K.icon(c, "key", x, 200, 110, K.GOLD, kk, 0.6, -20)
        K.text(c, "胰岛素", x, 290, 30, "serif_black", K.GOLD, kk)
    if fill > 0:
        for i in range(4):
            u = (g.t * 0.6 + i / 4) % 1
            T.hexa(c, -40 + 60 * u, -60 + 230 * u, 14, T.GLU, min(1, (1 - u) * 4))


# ---------------------------------------------------------------- 7 / 11 曲线

def gentle(c, g, t, d):
    p = clamp01(g.since(1) / max(0.1, g.b(10) - g.b(1)))
    T.chart(c, 0, 0, 820, 520, [(lambda u: T.bump(u, 0.55, 0.3, 1.8), T.FLAT, p, 9, "")])
    k = clamp01(g.since(3) / 0.3)
    if k > 0:
        K.text(c, "上升", -150, -150, 32, "serif_black", T.FLAT, k)
    k = clamp01(g.since(8) / 0.3)
    if k > 0:
        K.text(c, "回落", 230, -60, 32, "serif_black", T.FLAT, k)


def ranges(c, g, t, d):
    """正常范围带：空腹 < 5.6、餐后 2 小时 < 7.8（mmol/L）。"""
    T.chart(c, 0, 0, 820, 520, [(lambda u: T.bump(u, 0.62, 0.3, 1.8), T.FLAT, 1, 9, "")], 1, None, demo=False)
    x0, y0, h = -410, 260, 520
    lines = [(0.22, "空腹 5.6", d["k0"]), (0.62, "餐后 2 小时 7.8", d["k1"])]
    for v, lab, kb in lines:
        k = clamp01(g.since(kb) / 0.35)
        if k > 0:
            yy = y0 - h * (v + 0.06)
            K.seg(c, x0, yy, x0 + 820 * k, yy, K.RED, 4, 0.9)
            K.text(c, lab, x0 + 16, yy - 26, 28, "sans_medium", K.RED, k, "left")
    K.text(c, "单位：mmol/L", 0, 330, 26, "sans_medium", K.INK3)


def cgm(c, g, t, d):
    """手臂上的血糖仪 + 手机上的曲线。"""
    with K.paper(c, 1, 1.0):
        K.rr(c, 200, 0, 300, 520, 40, K.DARK)
    K.rr(c, 200, 0, 270, 470, 28, K.PAPER)
    p = clamp01(g.since(2) / 2.5)
    path = skia.Path()
    n = 80
    for i in range(int(n * p) + 1):
        u = i / n
        v = 0.25 + 0.5 * T.bump((u * 3) % 1, 0.9 if int(u * 3) != 1 else 0.4, 0.3)
        (path.moveTo if i == 0 else path.lineTo)(80 + u * 240, 120 - v * 200)
    c.drawPath(path, K.paint(T.SPIKE, 1, 6))
    K.text(c, "连续血糖仪", 200, -190, 28, "sans_medium", K.INK2)


def two_curves(c, g, t, d):
    p = clamp01(g.since(1) / max(0.1, g.b(8) - g.b(1)))
    T.chart(c, 0, 0, 820, 520, [(lambda u: T.bump(u, 1.0, 0.2, 2.6, 0.18), T.SPIKE, p, 9, "尖峰"),
                                (lambda u: T.bump(u, 0.4, 0.32, 1.6), T.FLAT, clamp01(g.since(5) / 1.0), 9, "平稳")])


def checklist(c, g, t, d):
    items = ["犯困吗？", "很快又饿吗？", "想吃甜的吗？"]
    K.card(c, 0, 0, 640, 480, K.PAPER, 1, 26, 1.0, 0, 1, ACC)
    K.text(c, "饭后两小时，问问自己", 0, -160, 40, "serif_black", K.INK)
    for i, s in enumerate(items):
        k = clamp01(g.since(3 + 3 * i) / 0.3)
        y = -50 + i * 100
        K.rr_stroke(c, -230, y, 44, 44, 8, K.INK3, 4)
        K.text(c, s, -180, y, 40, "serif", K.INK, 1, "left")
        if k > 0:
            K.icon(c, "check", -230, y, 50, K.GREEN, k, 0.4)


def ten_tiles(c, g, t, d):
    for i in range(10):
        k = clamp01(g.since(i * 0.5) / 0.3)
        if k <= 0:
            continue
        x = -340 + (i % 5) * 170
        y = -110 + (i // 5) * 200
        with K.at(c, x, y, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8)):
            with K.paper(c, k, 0.8):
                K.rr(c, 0, 0, 140, 140, 24, ACC if i % 2 == 0 else K.shade(ACC, 0.18))
            K.text(c, str(i + 1), 0, 4, 70, "black", K.PAPER, k)


def build() -> Episode:
    shots = [
        Shot(3, "吃完午饭，|眼皮就开始打架？", "情境演绎", [
            Fig(560, GROUND, 360, at=0, pose="sit", mood="calm", hair="short",
                moves=[(4, dict(pose="sit_sad", mood="flat", sfx="wood_low", note="主角开始犯困，头往下点")),
                       (8, dict(mood="worried", sfx="tom", note="猛地惊醒"))]),
            Custom(zzz, x=700, y=560, at=4, enter="fade"),
            Icon("clock", 260, 520, 140, at=1, enter="pop", sfx="wood_high", note="下午一点的钟"),
        ], draw=desk, note="午饭后，主角坐着犯困，Z 字一个个冒出，第 8 拍猛地惊醒"),
        Shot(3, "一会儿又饿了，|特别想吃甜的。", "情境演绎", [
            Fig(400, GROUND, 360, at=0, enter="none", pose="think", mood="worried", hair="short"),
            Bubble("好想吃蛋糕……", 640, 560, 44, at=2, tail=(-0.4, 1), sfx="wood_high", note="想吃蛋糕"),
            Custom(lambda c, g, t, d: T.food(c, "cake", 0, 0, 180, clamp01(g.since(6) / 0.3), 0,
                                             1 + 0.06 * math.sin(g.t * 6)), x=800, y=800, at=6, enter="pop",
                   sfx="bongo_high", note="蛋糕在眼前晃"),
        ], draw=ground, note="主角想吃甜的，头顶冒出“好想吃蛋糕”，一块蛋糕在眼前晃"),
        Shot(2, "一本书说：|问题可能出在血糖曲线。", "书中观点", [
            Custom(book_card, x=540, y=760, at=0, enter="none", sfx="wood_low", note="《控糖革命》出现"),
        ], hits=[(1, "shaker", 0.7, "封面上的曲线画出")], text_beat=0,
            note="《控糖革命》立在画面中央，封面上画出一条起伏的曲线"),
        Shot(3, "葡萄糖：|身体最主要的燃料。", "机制示意", [
            Big("葡萄糖", 540, 470, 150, at=0, sfx="kick", sub="glucose", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: [T.hexa(c, -300 + i * 150, 30 * math.sin(g.t * 2 + i), 50, T.GLU,
                                              clamp01(g.since(2 + i * 2) / 0.3), g.t * 30 + i * 40) for i in range(5)],
                   x=540, y=900, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "第一个葡萄糖分子"), (6, "wood_low", 0.7, "第三个"), (10, "bongo_high", 0.7, "第五个")],
            note="drop 处“葡萄糖”砸下；五个六边形葡萄糖分子按拍弹出、轻轻浮动"),
        Shot(3, "米饭、面包里的淀粉，|会被分解成葡萄糖。", "机制示意", [
            Custom(breakdown, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.7, "米饭"), (1, "wood_high", 0.7, "面包"), (3, "shaker", 0.7, "箭头"),
                 (8, "rim", 0.8, "“葡萄糖”标签")],
            note="米饭和面包经箭头分解成一堆葡萄糖小六边形"),
        Shot(3, "葡萄糖进入血液，|胰岛素帮它进到细胞里。", "机制示意", [
            Custom(insulin, x=540, y=800, at=0, enter="fade"),
        ], hits=[(2, "wood_high", 0.8, "胰岛素钥匙出现"), (5, "rim", 0.9, "细胞的门打开")],
            note="血管里葡萄糖流动；胰岛素（钥匙）滑到细胞旁，第 5 拍细胞开门，葡萄糖流进细胞"),
        Shot(3, "所以饭后，血糖先升高，|再慢慢回落。", "机制示意", [
            Custom(gentle, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "曲线开始画出"), (3, "wood_high", 0.7, "“上升”"), (8, "wood_low", 0.7, "“回落”")],
            note="一条平缓的餐后血糖曲线从左到右画出，标“上升”“回落”（示意）"),
        Shot(2, "健康人空腹，|血糖一般低于 5.6。", "研究证据", [
            Custom(ranges, x=540, y=780, at=0, enter="fade", k0=1, k1=99),
        ], hits=[(1, "rim", 0.8, "空腹线")], text_beat=0,
            note="曲线图上画出空腹 5.6 mmol/L 参考线"),
        Shot(2, "饭后两小时，|一般低于 7.8。", "研究证据", [
            Custom(ranges, x=540, y=780, at=0, enter="none", k0=-9, k1=1),
        ], hits=[(1, "rim", 0.8, "餐后 2 小时线")], text_beat=0, cut=True,
            note="再画出餐后 2 小时 7.8 mmol/L 参考线（ADA 诊断切点）"),
        Shot(3, "作者戴着血糖仪，|记录了大量饭后曲线。", "书中观点", [
            Fig(330, GROUND, 380, at=0, mood="smile", hair="long", color=ACC,
                moves=[(6, dict(pose="point", sfx="wood_high", note="作者指向手机上的曲线"))]),
            Custom(cgm, x=540, y=740, at=0, enter="pop"),
            Custom(lambda c, g, t, d: (K.dot(c, 0, 0, 20, "#FFFFFF"), K.ring(c, 0, 0, 20, K.INK3, 4),
                                       K.text(c, "血糖仪", -40, -10, 28, "sans_medium", K.INK2, 1, "right")),
                   x=318, y=880, at=2, enter="pop", sfx="wood_low", note="手臂上的血糖仪"),
        ], draw=ground, note="作者手臂上贴着连续血糖仪，手机上一条条曲线画出来"),
        Shot(3, "同样的食物，换个吃法，|曲线可能很不一样。", "书中观点", [
            Custom(two_curves, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "尖峰曲线画出"), (5, "wood_low", 0.7, "平稳曲线画出")],
            note="同一张图上两条曲线：一条高高的尖峰，一条平稳（示意）"),
        Shot(4, "饭后血糖升高本身正常；|要留意的是起伏太大。", "专家提醒", [
            Custom(lambda c, g, t, d: T.chart(c, 0, 0, 820, 520, [
                (lambda u: T.bump(u, 0.55, 0.3, 1.8), T.FLAT, 1, 9, "正常起伏"),
                (lambda u: T.bump(u, 1.0, 0.2, 2.6, 0.18), T.SPIKE, clamp01(g.since(6) / 1.4), 7, "起伏太大")],
                1, (0.0, 0.62)), x=540, y=780, at=0, enter="fade"),
        ], hits=[(0, "wood_low", 0.6, "正常起伏曲线"), (6, "shaker", 0.7, "大起伏曲线画出")],
            note="浅绿色正常范围带里是一条正常起伏的曲线；再画出一条冲出范围的大起伏曲线（示意）"),
        Shot(4, "小练习：下一顿饭后，|留意自己的感觉。", "小练习", [
            Custom(checklist, x=540, y=780, at=0, enter="pop"),
        ], hits=[(3, "wood_high", 0.7, "犯困？"), (6, "wood_low", 0.7, "很快又饿？"), (9, "bongo_high", 0.7, "想吃甜的？")],
            note="清单卡：犯困吗？很快又饿吗？想吃甜的吗？按拍打勾"),
        Shot(2, "接下来，|一起看书里的十个方法。", "书中观点", [
            Custom(ten_tiles, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.6, "方法 1"), (2, "wood_low", 0.6, "方法 5"), (4, "bongo_high", 0.7, "方法 9")],
            text_beat=0, note="十个编号方块按拍依次弹出"),
        ending(1, REFS),
    ]
    return Episode(1, "glucose", "葡萄糖", TITLES[1], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[1]}｜控糖革命01 葡萄糖", hashtags="#控糖 #血糖 #控糖革命 #健康 #科普",
                   cover_title="吃完就困、很快又饿？|看看你的【血糖曲线】", cover_sub="控糖革命 · 葡萄糖",
                   cover_shot=10, cover_t=5.5,
                   notes=[
                       "本系列依据杰西·安佐斯佩《控糖革命》的结构讲解，书中内容标“书中观点”，用自己的话转述。",
                       "空腹血糖 < 5.6 mmol/L（100 mg/dL）、餐后 2 小时 < 7.8 mmol/L（140 mg/dL）为 ADA 的正常切点；"
                       "第 7、8、11、12 镜曲线为示意，不是实测数据。",
                       "作者用连续血糖仪做自我实验，是书中及出版社介绍的说法。",
                       "犯困、饥饿、想吃甜食与血糖波动的关系是书中观点；这些感受也有很多其他原因。",
                   ], **SERIES).build()
