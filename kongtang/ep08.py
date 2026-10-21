"""08 甜点：想吃甜的，什么时候吃？（书中第 6 个方法：选餐后甜点，不选甜零食）"""

import math

import skia

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Icon, Shot, Txt

from . import kit_tang as T
from .common import GROUND, SERIES, TITLES, ending, ground, refs

ACC = "#D96A8A"
REFS = refs("Shukla, A. P. et al. (2015). Food Order Has a Significant Impact on Postprandial Glucose and Insulin "
            "Levels. Diabetes Care, 38(7), e98–e99.")


def pop(g, k, dur=0.3):
    return clamp01(g.since(k) / dur)


def popscale(k):
    return 0.3 + 0.7 * K.ease_out_back(k, 1.8) if k > 0 else 0


def empty_fn(u):
    return T.bump(u, 1.0, 0.18, 2.8, 0.2)


def after_fn(u):
    return T.bump(u, 0.5, 0.3, 1.7)


# ---------------------------------------------------------------- 1–2 下午三点的蛋糕

def three_pm(c, g, t, d):
    k = pop(g, 0, 0.4)
    K.icon(c, "clock", -220, 0, 170, K.INK, k, 0.8, 0, popscale(k))
    K.text(c, "15:00", -220, 130, 40, "black", K.INK2, k)
    k2 = pop(g, 4)
    if k2 > 0:
        T.food(c, "cake", 180, 20, 220, k2, 0, popscale(k2) * (1 + 0.04 * math.sin(g.t * 5)))


def empty_spike(c, g, t, d):
    p = clamp01(g.since(1) / max(0.1, g.b(7) - g.b(1)))
    T.chart(c, 0, 60, 820, 480, [(empty_fn, T.SPIKE, p, 9, "空腹吃蛋糕")])
    k = pop(g, 0)
    if k > 0:
        T.food(c, "cake", -300, -320, 120, k, 0, popscale(k))
        K.text(c, "空腹", -180, -320, 40, "serif_black", T.SPIKE, k, "left")


# ---------------------------------------------------------------- 5–7 对比

def two_plates(c, g, t, d):
    """左：空盘 + 蛋糕；右：吃完的饭 + 蛋糕。"""
    for i, (x, lab, full) in enumerate(((-250, "空腹吃", False), (250, "饭后吃", True))):
        k = pop(g, i * 2)
        if k <= 0:
            continue
        with K.fade(c, clamp01(k * 3)):
            T.plate(c, x, 40, 165)
            if full:
                T.food(c, "salad", x - 55, 5, 90)
                T.food(c, "drumstick", x + 55, 5, 90)
                T.food(c, "rice", x, 95, 90)
            T.food(c, "cake", x, -230, 150, 1, 0, popscale(k))
            K.text(c, lab, x, 260, 44, "serif_black", T.SPIKE if not full else T.FLAT)
    k = pop(g, 6)
    if k > 0:
        K.text(c, "vs", 0, 40, 60, "black", K.INK3, k)


def two_curves(c, g, t, d):
    p1 = clamp01(g.since(1) / max(0.1, g.b(5) - g.b(1)))
    p2 = clamp01(g.since(5) / max(0.1, g.b(9) - g.b(5)))
    T.chart(c, 0, 0, 820, 520, [(empty_fn, T.SPIKE, p1, 8, "空腹吃"), (after_fn, T.FLAT, p2, 9, "饭后吃")])


def stomach(c, g, t, d):
    """胃的剖面：底下是菜和肉，上面落下的糖颗粒慢慢渗出去。"""
    p = skia.Path()
    p.moveTo(-200, -260)
    p.cubicTo(-330, -120, -320, 180, -60, 240)
    p.cubicTo(140, 290, 330, 160, 260, -40)
    p.cubicTo(220, -160, 60, -140, 0, -230)
    p.close()
    c.drawPath(p, K.paint(K.tint("#E9B3A8", 0.35)))
    c.drawPath(p, K.paint(K.shade("#E9B3A8", 0.15), 1, 12))
    k = pop(g, 1, 0.4)
    if k > 0:
        T.food(c, "salad", -120, 120, 110, k)
        T.food(c, "drumstick", 60, 130, 110, k)
        T.food(c, "broccoli", 170, 40, 90, k)
    if g.since(3) >= 0:
        for i in range(8):
            u = clamp01((g.since(3) - i * 0.25) / 2.5)
            if u <= 0:
                continue
            T.hexa(c, -60 + 20 * math.sin(i * 1.7), -200 + 260 * ease_out(u), 16, T.GLU, 1)
    k2 = pop(g, 8)
    if k2 > 0:
        K.pill(c, 0, -360, "慢一点进入血液", 34, T.FLAT, K.PAPER, k2)


# ---------------------------------------------------------------- 9 挪时间

def move_time(c, g, t, d):
    k = ease_in_out(clamp01(g.since(1) / 0.8))
    K.icon(c, "clock", -260, -60, 150, K.INK, 1, 0.8)
    K.text(c, "15:00", -260, 60, 34, "black", K.INK3, 1)
    K.icon(c, "clock", 260, -60, 150, K.INK, 1, 0.8)
    K.text(c, "晚饭后", 260, 60, 34, "black", K.INK2, 1)
    T.food(c, "cake", -260 + 520 * k, -260 - 80 * math.sin(k * math.pi), 130, 1)


# ---------------------------------------------------------------- 10–12 误解与提醒

def not_more(c, g, t, d):
    for i in range(3):
        k = pop(g, i)
        if k > 0:
            T.food(c, "cake", -220 + i * 220, 0, 170, k, 0, popscale(k))
    k = pop(g, 4, 0.25)
    if k > 0:
        K.seg(c, -360, -150, -360 + 720 * k, 150 * (2 * k - 1), K.RED, 14)
        K.seg(c, 360, -150, 360 - 720 * k, 150 * (2 * k - 1), K.RED, 14)


def if_then(c, g, t, d):
    K.text_card(c, 0, -60, ["如果要吃，", "就放在【饭后】。"], 64, 720, K.PAPER, K.INK, ACC, pop(g, 0, 0.4), 0,
                popscale(pop(g, 0, 0.4)), ACC, "serif", 1.0)
    k = pop(g, 4)
    if k > 0:
        T.food(c, "cake", 0, 220, 160, k, 0, popscale(k))


def same_calories(c, g, t, d):
    k = pop(g, 0, 0.4)
    K.icon(c, "scale", 0, -60, 320, K.INK, k, 0.8, 0, popscale(k))
    k2 = pop(g, 4)
    if k2 > 0:
        T.food(c, "cake", -160, 150, 130, k2, 0, popscale(k2))
        T.food(c, "cake", 160, 150, 130, k2, 0, popscale(k2))
        K.text(c, "=", 0, 150, 70, "black", ACC, k2)
        K.text(c, "空腹", -160, 260, 30, "sans_medium", K.INK2, k2)
        K.text(c, "饭后", 160, 260, 30, "sans_medium", K.INK2, k2)
    k3 = pop(g, 8)
    if k3 > 0:
        K.pill(c, 0, -330, "热量和糖一点没少", 36, ACC, K.PAPER, k3)


# ---------------------------------------------------------------- 13 小练习

def save_for_later(c, g, t, d):
    T.plate(c, 0, 80, 240)
    T.food(c, "salad", -80, 60, 110, 1)
    T.food(c, "rice", 80, 60, 110, 1)
    land = g.since(6)
    if land > -0.35:
        dy = -380 * (1 - ease_out(clamp01((land + 0.35) / 0.35))) if land < 0 else -12 * math.sin(
            clamp01(land / 0.3) * math.pi)
        T.food(c, "cake", 0, dy, 140, 1)
    k = pop(g, 2)
    if k > 0:
        K.pill(c, 0, -300, "先吃饭", 40, T.FLAT, K.PAPER, k)
    k2 = pop(g, 10)
    if k2 > 0:
        K.pill(c, 0, 360, "甜点留到最后", 40, ACC, K.PAPER, k2)


def build() -> Episode:
    shots = [
        Shot(3, "下午三点，饿了，|来块蛋糕？", "情境演绎", [
            Custom(three_pm, x=620, y=620, at=0, enter="none", sfx="wood_low", note="下午三点的钟"),
            Fig(220, GROUND, 360, at=0, mood="happy", hair="short",
                moves=[(4, dict(pose="reach", sfx="bongo_high", note="主角伸手拿蛋糕"))]),
        ], draw=ground, note="钟指向下午三点，第 4 拍一块蛋糕出现，主角伸手去拿"),
        Shot(3, "空腹吃甜的，|血糖一下冲上去。", "书中观点", [
            Custom(empty_spike, x=540, y=800, at=0, enter="fade"),
        ], hits=[(0, "wood_low", 0.6, "蛋糕"), (1, "shaker", 0.7, "尖峰曲线画出")],
            note="空腹吃蛋糕后的尖峰曲线（示意）"),
        Shot(2, "换个时间吃，|会不一样吗？", "情境演绎", [
            Fig(540, GROUND, 360, at=0, enter="none", pose="think", mood="worried", hair="short"),
            Icon("question", 760, 640, 140, color=ACC, at=2, enter="pop", sfx="bongo_low", note="问号"),
        ], draw=ground, text_beat=0, note="主角托腮想，头顶弹出问号"),
        Shot(3, "甜点：|放在饭后吃。", "书中观点", [
            Big("甜点", 540, 470, 150, at=0, sfx="kick", sub="书中第 6 个方法", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: (T.plate(c, 0, 40, 200), T.food(c, "cake", 0, 20, 190, pop(g, 4), 0,
                                                                     popscale(pop(g, 4)))),
                   x=540, y=930, at=0, enter="pop"),
        ], hits=[(4, "wood_high", 0.7, "蛋糕落在餐盘上")],
            note="drop 处“甜点”砸下；空盘子，第 4 拍放上一块蛋糕"),
        Shot(3, "同一块蛋糕：|空腹吃，还是饭后吃？", "书中观点", [
            Custom(two_plates, x=540, y=820, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "空腹那一盘"), (2, "wood_high", 0.6, "饭后那一盘"), (6, "rim", 0.7, "vs")],
            note="左边空盘配蛋糕（空腹吃），右边吃剩的饭菜配蛋糕（饭后吃）"),
        Shot(3, "书中的曲线：|饭后吃，起伏小得多。", "书中观点", [
            Custom(two_curves, x=540, y=790, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "空腹曲线"), (5, "wood_high", 0.7, "饭后曲线")],
            note="同一张图：空腹吃的尖峰与饭后吃的平缓曲线（示意）"),
        Shot(3, "胃里已经有菜和肉，|糖进入血液慢一些。", "机制示意", [
            Custom(stomach, x=540, y=820, at=0, enter="fade"),
        ], hits=[(1, "wood_low", 0.6, "胃里的菜和肉"), (3, "shaker", 0.7, "糖颗粒慢慢落下"),
                 (8, "rim", 0.7, "“慢一点进入血液”")],
            note="胃的剖面：底下是菜和肉，上面落下的糖颗粒慢慢沉下去（示意）"),
        Shot(2, "这和“先吃菜、后吃饭”|是同一个道理。", "书中观点", [
            Custom(lambda c, g, t, d: T.step_order(c, 0, 0, [("salad", ""), ("drumstick", ""), ("cake", "")],
                                                   [pop(g, 0), pop(g, 1), pop(g, 2)], 130, 260),
                   x=540, y=780, at=0, enter="none"),
            Txt("进食顺序研究见第 03 期", 540, 1000, 28, at=3, font="sans_medium", color=K.INK2),
        ], hits=[(0, "wood_high", 0.6, "1 菜"), (1, "wood_low", 0.6, "2 肉"), (2, "bongo_high", 0.6, "3 甜点")],
            text_beat=0, note="菜 → 肉 → 甜点按顺序排开，下方注“进食顺序研究见第 03 期”"),
        Shot(2, "下午茶的甜点，|挪到晚饭后。", "书中观点", [
            Custom(move_time, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.7, "蛋糕从下午三点跳到晚饭后")], text_beat=0,
            note="两只钟：15:00 与晚饭后，蛋糕从左边跳到右边"),
        Shot(3, "这不是鼓励|多吃甜点。", "常见误解", [
            Custom(not_more, x=540, y=800, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "三块蛋糕"), (4, "rim", 0.9, "红叉")],
            note="一排三块蛋糕，第 4 拍被红叉划掉"),
        Shot(3, "而是：|如果要吃，就放在饭后。", "常见误解", [
            Custom(if_then, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.7, "文字卡"), (4, "bongo_low", 0.7, "一块蛋糕")],
            note="文字卡“如果要吃，就放在饭后”，下面一块蛋糕"),
        Shot(4, "放在饭后吃，|热量和糖一点没少。", "专家提醒", [
            Custom(same_calories, x=540, y=800, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "天平"), (4, "rim", 0.8, "两块蛋糕一样重"), (8, "wood_high", 0.7, "提示标签")],
            note="天平两边是同样的蛋糕（空腹 / 饭后），标“热量和糖一点没少”"),
        Shot(4, "小练习：想吃甜的，|留到下一顿饭后。", "小练习", [
            Custom(save_for_later, x=540, y=780, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "“先吃饭”"), (6, "bongo_low", 0.8, "蛋糕落进盘子"), (10, "rim", 0.7, "“甜点留到最后”")],
            note="先吃饭菜，第 6 拍蛋糕落进盘子，标“甜点留到最后”"),
        Shot(2, "时间对了，|甜点也能吃得稳一点。", "书中观点", [
            Custom(lambda c, g, t, d: T.chart(c, 0, 0, 640, 300, [(after_fn, T.FLAT, clamp01(g.since(0) / 1.2), 8,
                                                                    "")], grid=False),
                   x=540, y=800, at=0, enter="pop", sfx="clap", note="一条平缓的曲线"),
        ], text_beat=0, note="一条平缓的饭后曲线（示意）"),
        ending(8, REFS),
    ]
    return Episode(8, "dessert", "甜点", TITLES[8], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[8]}｜控糖革命08 甜点", hashtags="#控糖 #甜点 #血糖 #控糖革命 #健康",
                   cover_title="同一块蛋糕，|【什么时候】吃更好？", cover_sub="控糖革命 · 甜点",
                   cover_shot=5, cover_t=5.5,
                   notes=[
                       "“选餐后甜点，不选甜零食”是书中第 6 个方法：同样的甜食，饭后吃比空腹当零食吃血糖起伏更小。属书中观点，"
                       "与进食顺序研究（碳水放最后吃时餐后血糖更低，Shukla 等 2015，11 名 2 型糖尿病患者）方向一致，但没有直接比较甜点时间的大型研究。",
                       "第 2、6、14 镜曲线和第 7 镜胃的剖面为示意，不是实测数据。",
                       "饭后吃甜点不会减少甜点本身的热量和糖，片中第 12 镜专门提醒。",
                   ], **SERIES).build()
