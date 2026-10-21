"""06 早餐：早餐，为什么别吃太甜？（书中第 4 个方法：让早餐曲线变平）"""

import math

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Icon, Shot, Txt

from . import kit_tang as T
from .common import GROUND, SERIES, TITLES, ending, ground, refs

ACC = "#E0A030"
REFS = refs()


def pop(g, k, dur=0.3):
    return clamp01(g.since(k) / dur)


def popscale(k):
    return 0.3 + 0.7 * K.ease_out_back(k, 1.8) if k > 0 else 0


# ---------------------------------------------------------------- 1 甜早餐

def sweet_table(c, g, t, d):
    """桌上一杯果汁、一个甜面包、一碗含糖麦片，按拍弹出。"""
    items = [("juice", -230, 0), ("bread", 0, 2), ("cookie", 230, 4)]
    K.rr(c, 30, 130, 640, 24, 12, K.mix(K.OTHER, K.PAPER, 0.2))
    for name, x, b in items:
        k = pop(g, b)
        if k > 0:
            T.food(c, name, x, 20, 170, clamp01(k * 3), 0, popscale(k))
    k = pop(g, 6)
    if k > 0:
        K.pill(c, 230, -120, "含糖麦片", 30, ACC, K.PAPER, k)


# ---------------------------------------------------------------- 2 上午十点

def ten_clock(c, g, t, d):
    k = pop(g, 0, 0.4)
    K.icon(c, "clock", 0, 0, 160, K.INK, k, 0.8, 0, popscale(k))
    K.text(c, "10:00", 0, 130, 40, "black", K.INK2, k)


# ---------------------------------------------------------------- 3 / 5 / 7 曲线

def morning_spike(c, g, t, d):
    p = clamp01(g.since(1) / max(0.1, g.b(6) - g.b(1)))
    T.chart(c, 0, 0, 820, 500, [(lambda u: T.bump(u, 0.95, 0.2, 2.6, 0.2), T.SPIKE, p, 9, "早餐后")],
            xlabel="上午")


def sweet_spike(c, g, t, d):
    p = clamp01(g.since(2) / max(0.1, g.b(9) - g.b(2)))
    T.chart(c, 0, 80, 820, 460, [(lambda u: T.bump(u, 1.0, 0.18, 2.8, 0.22), T.SPIKE, p, 9, "甜早餐")])
    for i, name in enumerate(("juice", "bread", "cookie")):
        k = pop(g, i * 0.5)
        if k > 0:
            T.food(c, name, -260 + i * 260, -330, 110, clamp01(k * 3), 0, popscale(k))


def savory_plate(c, g, t, d):
    T.plate(c, 0, 40, 330)
    spots = [("egg", -110, -40, 2, "鸡蛋"), ("cheese", 120, -30, 4, "奶酪"), ("salad", 0, 150, 6, "蔬菜")]
    for name, x, y, b, lab in spots:
        k = pop(g, b)
        if k > 0:
            T.food(c, name, x, y + 40, 160, clamp01(k * 3), 0, popscale(k))
    k = pop(g, 8)
    if k > 0:
        K.pill(c, 0, -360, "也可以是豆腐、豆浆", 32, ACC, K.PAPER, k)


def two_breakfasts(c, g, t, d):
    p1 = clamp01(g.since(1) / max(0.1, g.b(5) - g.b(1)))
    p2 = clamp01(g.since(5) / max(0.1, g.b(9) - g.b(5)))
    T.chart(c, 0, 0, 820, 520, [(lambda u: T.bump(u, 1.0, 0.18, 2.8, 0.22), T.SPIKE, p1, 8, "甜早餐"),
                                (lambda u: T.bump(u, 0.42, 0.32, 1.6), T.FLAT, p2, 9, "咸早餐")])


# ---------------------------------------------------------------- 8–10 水果与果汁

def fiber_web(c, x, y, s, k, t):
    """水果里的膳食纤维：一圈细网。"""
    for i in range(7):
        a = i * math.pi / 7 + 0.2 * math.sin(t + i)
        K.seg(c, x - s * math.cos(a), y - s * math.sin(a) * 0.8, x + s * math.cos(a), y + s * math.sin(a) * 0.8,
              T.FLAT, 4, k)


def whole_fruit(c, g, t, d):
    T.food(c, "apple", 0, 0, 300, 1)
    k = pop(g, 2, 0.5)
    if k > 0:
        fiber_web(c, 0, 20, 150, 0.8 * k, g.t)
        K.pill(c, 0, 250, "膳食纤维", 36, T.FLAT, K.PAPER, k)


def juicing(c, g, t, d):
    """苹果变成果汁，纤维网从杯子旁掉落、变淡。"""
    k = ease_in_out(clamp01(g.since(0) / 0.8))
    T.food(c, "apple", -220, -40, 200, 1 - k)
    T.food(c, "juice", 120, -40, 260, clamp01(k * 1.5))
    kk = clamp01(g.since(2) / 1.0)
    if kk > 0:
        fiber_web(c, 330, -40 + 260 * kk, 70, 0.8 * (1 - kk), g.t)
        K.text(c, "纤维", 330, -150 + 260 * kk, 30, "sans_medium", T.FLAT, 1 - kk)


def apple_vs_juice(c, g, t, d):
    p1 = clamp01(g.since(1) / max(0.1, g.b(6) - g.b(1)))
    p2 = clamp01(g.since(5) / max(0.1, g.b(10) - g.b(5)))
    T.chart(c, 0, 60, 820, 480, [(lambda u: T.bump(u, 0.92, 0.17, 2.8, 0.15), T.SPIKE, p2, 8, "果汁"),
                                 (lambda u: T.bump(u, 0.45, 0.3, 1.7), T.FLAT, p1, 9, "整颗水果")])


# ---------------------------------------------------------------- 11–12 碳水可以有

def bread_ok(c, g, t, d):
    T.plate(c, 0, 0, 300)
    T.food(c, "egg", -90, -10, 150, 1)
    T.food(c, "bread", 100, 10, 150, 1)
    k = pop(g, 4)
    if k > 0:
        K.icon(c, "check", 260, -230, 120, K.GREEN, k, 0.5, 0, popscale(k))


def order_breakfast(c, g, t, d):
    T.step_order(c, 0, 0, [("egg", "先吃蛋白质"), ("salad", "再吃菜"), ("bread", "碳水放最后")],
                 [pop(g, 2), pop(g, 5), pop(g, 8)], 160, 300)


# ---------------------------------------------------------------- 13 小练习

def add_egg(c, g, t, d):
    T.plate(c, 0, 60, 300)
    T.food(c, "bread", 90, 60, 150, 1)
    land = g.since(4)
    if land > -0.35:
        dy = -380 * (1 - ease_out(clamp01((land + 0.35) / 0.35))) if land < 0 else -12 * math.sin(clamp01(land / 0.3)
                                                                                                    * math.pi)
        T.food(c, "egg", -100, 40 + dy, 170, 1)
    k = pop(g, 8)
    if k > 0:
        K.pill(c, 0, -330, "+1 个鸡蛋", 40, ACC, K.PAPER, k)


def sunrise(c, g, t, d):
    k = pop(g, 0, 0.5)
    K.icon(c, "sun", 0, -140, 200, K.GOLD, k, 0.6, g.t * 10, popscale(k))
    T.chart(c, 0, 190, 640, 240, [(lambda u: T.bump(u, 0.4, 0.3, 1.6), T.FLAT, clamp01(g.since(1) / 1.2), 8, "")],
            grid=False, xlabel="上午")


def build() -> Episode:
    shots = [
        Shot(3, "早餐一杯果汁，|再来个甜面包？", "情境演绎", [
            Fig(220, GROUND, 360, at=0, mood="happy", hair="short",
                moves=[(8, dict(pose="point", sfx="wood_high", note="主角指着一桌甜早餐"))]),
            Custom(sweet_table, x=660, y=860, at=0, enter="none"),
        ], draw=ground, hits=[(0, "wood_low", 0.7, "果汁"), (2, "wood_high", 0.7, "甜面包"), (4, "bongo_high", 0.7, "麦片")],
            note="桌上按拍弹出果汁、甜面包、含糖麦片"),
        Shot(3, "上午十点，|又饿又没精神。", "情境演绎", [
            Fig(400, GROUND, 360, at=0, enter="none", mood="worried", hair="short",
                moves=[(6, dict(pose="sad", mood="flat", sfx="tom", note="主角垂头丧气"))]),
            Custom(ten_clock, x=780, y=600, at=0, enter="none", sfx="wood_low", note="上午十点的钟"),
            Icon("question", 560, 600, 100, color=ACC, at=8, enter="pop", sfx="bongo_low", note="肚子又饿了"),
        ], draw=ground, note="钟指向上午十点，主角又饿又没精神，垂下头"),
        Shot(2, "书里说：一天的曲线，|从早餐开始。", "书中观点", [
            Custom(morning_spike, x=540, y=790, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.7, "早餐后的曲线画出")], text_beat=0,
            note="一条早餐后的尖峰曲线（示意）"),
        Shot(3, "早餐：|让第一条曲线变平。", "书中观点", [
            Big("早餐", 540, 470, 150, at=0, sfx="kick", sub="书中第 4 个方法", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: T.chart(c, 0, 0, 760, 360, [
                (lambda u: T.bump(u, 0.95 - 0.55 * ease_in_out(clamp01(g.since(4) / 1.2)), 0.22, 2.2), T.FLAT, 1, 9,
                 "")], xlabel="上午"), x=540, y=930, at=0, enter="pop"),
        ], hits=[(4, "wood_high", 0.7, "曲线开始压平"), (8, "wood_low", 0.7, "曲线变平")],
            note="drop 处“早餐”砸下；下方一条尖峰曲线慢慢被压平（示意）"),
        Shot(3, "空腹吃甜的，|容易一早就冲出大尖峰。", "书中观点", [
            Custom(sweet_spike, x=540, y=800, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "果汁"), (1, "wood_high", 0.6, "甜面包"), (2, "shaker", 0.7, "尖峰曲线画出")],
            note="上方三样甜早餐，下方一条高高的尖峰曲线（示意）"),
        Shot(3, "书里建议：|咸味、带蛋白质的早餐。", "书中观点", [
            Custom(savory_plate, x=540, y=820, at=0, enter="pop", sfx="wood_low", note="空盘子"),
        ], hits=[(2, "wood_high", 0.7, "鸡蛋"), (4, "bongo_high", 0.7, "奶酪"), (6, "wood_low", 0.7, "蔬菜"),
                 (8, "rim", 0.7, "豆制品也可以")],
            note="盘子里按拍放上鸡蛋、奶酪、蔬菜，标注“也可以是豆腐、豆浆”"),
        Shot(3, "同样吃饱，|曲线平稳得多。", "书中观点", [
            Custom(two_breakfasts, x=540, y=790, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "甜早餐曲线"), (5, "wood_high", 0.7, "咸早餐曲线")],
            note="同一张图：甜早餐的尖峰与咸早餐的平稳曲线（示意）"),
        Shot(2, "整颗水果里，|有膳食纤维。", "机制示意", [
            Custom(whole_fruit, x=540, y=780, at=0, enter="pop", sfx="wood_low", note="一颗苹果"),
        ], hits=[(2, "wood_high", 0.7, "纤维网出现")], text_beat=0,
            note="一颗苹果，第 2 拍显出里面的纤维网"),
        Shot(2, "打成果汁，纤维|大多被去掉了。", "机制示意", [
            Custom(juicing, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "shaker", 0.7, "苹果变果汁"), (2, "rim", 0.8, "纤维掉落")], text_beat=0,
            note="苹果变成一杯果汁，纤维网从旁边掉落、变淡"),
        Shot(3, "所以喝果汁，|血糖升得更快。", "机制示意", [
            Custom(apple_vs_juice, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "整颗水果曲线"), (5, "wood_high", 0.7, "果汁曲线")],
            note="整颗水果的平稳曲线与果汁的尖峰曲线（示意）"),
        Shot(3, "这不是说|早餐不能吃碳水。", "常见误解", [
            Custom(bread_ok, x=540, y=800, at=0, enter="pop", sfx="wood_low", note="鸡蛋配面包"),
        ], hits=[(4, "clap", 0.7, "打勾：可以吃")], note="盘子里鸡蛋配面包，第 4 拍打勾"),
        Shot(4, "可以有，搭配蛋白质，|碳水放在后面吃。", "常见误解", [
            Custom(order_breakfast, x=540, y=790, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "1 鸡蛋"), (5, "wood_low", 0.7, "2 蔬菜"), (8, "bongo_high", 0.7, "3 面包")],
            note="三样食物按顺序排开：先蛋白质、再蔬菜、碳水最后"),
        Shot(4, "小练习：明天早餐，|加一个鸡蛋。", "小练习", [
            Custom(add_egg, x=540, y=820, at=0, enter="pop"),
        ], hits=[(4, "bongo_low", 0.8, "鸡蛋落进盘子"), (8, "wood_high", 0.7, "“+1 个鸡蛋”")],
            note="盘子里只有面包，第 4 拍一个煎蛋从上方落进盘子"),
        Shot(2, "早餐稳一点，|上午也会轻松些。", "书中观点", [
            Custom(sunrise, x=540, y=740, at=0, enter="none", sfx="clap", note="太阳升起"),
            Txt("书中观点；每个人感受不同", 540, 1225, 26, at=1, font="sans_medium", color=K.INK2),
        ], text_beat=0, note="太阳升起，下面一条平稳的上午曲线"),
        ending(6, REFS),
    ]
    return Episode(6, "breakfast", "早餐", TITLES[6], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[6]}｜控糖革命06 早餐", hashtags="#控糖 #早餐 #血糖 #控糖革命 #健康",
                   cover_title="早餐一杯果汁，|血糖【一早】就冲高？", cover_sub="控糖革命 · 早餐",
                   cover_shot=6, cover_t=5.5,
                   notes=[
                       "“让早餐曲线变平”是书中第 4 个方法：书中认为早上空腹吃甜食（甜面包、果汁、含糖麦片）容易出现当天最大的尖峰，"
                       "建议改吃咸味、含蛋白质与脂肪的早餐。属书中观点，片中标注。",
                       "整颗水果含膳食纤维，榨汁后纤维大多被滤掉，果汁升糖更快，属通行营养学说法；第 7、10 镜曲线为示意，不是实测数据。",
                       "第 6 镜的豆腐、豆浆是为中国观众补充的蛋白质来源示例，不是书中原文。",
                       "第 14 镜“上午会轻松些”是书中观点，个人感受差异很大。",
                   ], **SERIES).build()
