"""11 零食：饿了，零食怎么选？"""

import math

import skia

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Big, Bubble, Custom, Episode, Fig, Icon, Shot

from . import kit_tang as T
from .common import GROUND, SERIES, TITLES, ending, ground, refs

ACC = "#8C6A3F"
REFS = refs()


# ---------------------------------------------------------------- 自画小食物

def cucumber(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        for i in range(3):
            cx = x - s * 0.3 + i * s * 0.3
            K.dot(c, cx, y, s * 0.2, "#4E8A3E")
            K.dot(c, cx, y, s * 0.16, "#CFE6A8")
            for j in range(3):
                a = j * 2.1
                K.dot(c, cx + s * 0.06 * math.cos(a), y + s * 0.06 * math.sin(a), s * 0.02, "#F2F7E6")


def candy(c, x, y, s, alpha=1.0):
    with K.fade(c, alpha):
        K.poly(c, [(x - s * 0.45, y - s * 0.18), (x - s * 0.22, y), (x - s * 0.45, y + s * 0.18)], "#E86A8A")
        K.poly(c, [(x + s * 0.45, y - s * 0.18), (x + s * 0.22, y), (x + s * 0.45, y + s * 0.18)], "#E86A8A")
        K.dot(c, x, y, s * 0.24, "#F07A98")
        K.seg(c, x - s * 0.12, y - s * 0.12, x + s * 0.12, y + s * 0.12, "#FFFFFF", s * 0.04)


def snack(c, name, x, y, s, alpha=1.0, scale=1.0):
    if alpha <= 0:
        return
    with K.at(c, x, y, 0, scale):
        with K.paper(c, alpha, 0.7, skia.Rect.MakeXYWH(-s, -s, 2 * s, 2 * s)):
            if name == "cucumber":
                cucumber(c, 0, 0, s)
            elif name == "candy":
                candy(c, 0, 0, s)
            else:
                T.FOODS[name](c, 0, 0, s, 1.0)


def pop(g, k0, dur=0.3):
    k = clamp01(g.since(k0) / dur)
    return k, 0.3 + 0.7 * K.ease_out_back(k, 1.8)


# ---------------------------------------------------------------- 2 甜零食

def sweet_row(c, g, t, d):
    for i, (name, lab) in enumerate((("cookie", "饼干"), ("candy", "糖果"), ("juice", "果汁"))):
        k, sc = pop(g, 2 + 2 * i)
        if k <= 0:
            continue
        x = -300 + i * 300
        snack(c, name, x, 0, 170, k, sc)
        K.text(c, lab, x, 150, 36, "serif_black", K.INK2, k)


# ---------------------------------------------------------------- 3 / 6 曲线

def sweet_spike(c, g, t, d):
    p = clamp01(g.since(0) / max(0.1, g.b(6) - g.b(0)))
    T.chart(c, 0, 0, 820, 520, [(lambda u: T.bump(u, 1.0, 0.2, 2.6, 0.2), T.SPIKE, p, 9, "甜零食")])


def compare(c, g, t, d):
    T.chart(c, 0, 0, 820, 520, [
        (lambda u: T.bump(u, 1.0, 0.2, 2.6, 0.2), T.SPIKE, clamp01(g.since(1) / 1.4), 9, "甜零食"),
        (lambda u: T.bump(u, 0.35, 0.3, 1.6), T.FLAT, clamp01(g.since(6) / 1.4), 9, "咸零食")])


# ---------------------------------------------------------------- 4 / 5 咸零食

SAVORY = (("nuts", "坚果"), ("cheese", "奶酪"), ("egg", "鸡蛋"), ("cucumber", "黄瓜"))


def savory_drop(c, g, t, d):
    for i, (name, _) in enumerate(SAVORY):
        k, sc = pop(g, 4 + 2 * i)
        if k > 0:
            snack(c, name, -330 + i * 220, 0, 150, k, sc)


def savory_grid(c, g, t, d):
    for i, (name, lab) in enumerate(SAVORY):
        k, sc = pop(g, 1 + 2 * i)
        if k <= 0:
            continue
        x, y = -200 + (i % 2) * 400, -170 + (i // 2) * 350
        K.card(c, x, y, 330, 300, K.PAPER, k, 24, 0.9)
        snack(c, name, x, y - 30, 150, k, sc)
        K.text(c, lab, x, y + 100, 38, "serif_black", ACC, k)


# ---------------------------------------------------------------- 8 / 9 无糖包装

def package(c, g, t, d):
    k = clamp01(g.since(0) / 0.35)
    with K.at(c, -120, 0, -4, 0.4 + 0.6 * K.ease_out_back(k, 1.6)):
        with K.paper(c, k, 1.0):
            K.rr(c, 0, 0, 420, 560, 30, "#F2C14E")
            K.rr(c, 0, -190, 420, 40, 10, K.shade("#F2C14E", 0.2))
        K.text(c, "无糖", 0, -90, 90, "serif_black", K.RED, k)
        K.text(c, "饼干", 0, 10, 60, "serif_black", K.INK, k)
        T.food(c, "cookie", 0, 150, 130, k)
    kk = clamp01(g.since(3) / 0.35)
    if kk > 0:
        K.text_card(c, 250, 250, ["配料：", "【小麦粉】、植物油、", "【淀粉】、甜味剂"], 34, 440, K.PAPER, K.INK, K.RED, kk, 2,
                    0.4 + 0.6 * K.ease_out_back(kk, 1.6), None, "sans_medium", 0.9)


def starch_to_glucose(c, g, t, d):
    T.food(c, "cookie", -300, 0, 200, clamp01(g.since(0) / 0.3))
    k = clamp01(g.since(2) / 0.4)
    if k > 0:
        K.arrow(c, (-150, 0), (60, 0), K.INK3, 10, k, k, 0, 30)
    for i in range(10):
        a = i * 2.3
        r = 50 + 20 * (i % 3)
        kk = clamp01(g.since(3 + i * 0.2) / 0.3)
        T.hexa(c, 260 + r * math.cos(a), r * math.sin(a), 22, T.GLU, kk, g.t * 40 + i * 20)
    k3 = clamp01(g.since(6) / 0.3)
    if k3 > 0:
        K.pill(c, 260, 170, "葡萄糖", 34, T.GLU, K.PAPER, k3)


# ---------------------------------------------------------------- 10 别太咸

def salt(c, g, t, d):
    k = clamp01(g.since(0) / 0.35)
    with K.at(c, -200, 0, 10 * math.sin(g.t * 5) * clamp01(g.since(2) / 0.3), 0.4 + 0.6 * K.ease_out_back(k, 1.6)):
        with K.paper(c, k, 1.0):
            K.rr(c, 0, 40, 200, 300, 40, "#FFFFFF")
            K.rr(c, 0, -130, 160, 60, 24, "#9FB6BF")
        K.text(c, "盐", 0, 50, 70, "serif_black", K.INK, k)
        for i in range(3):
            K.dot(c, -40 + i * 40, -140, 6, K.INK3, k)
    if g.since(2) >= 0:
        for i in range(8):
            u = (g.t * 0.8 + i / 8) % 1
            K.dot(c, -200 + 30 * math.sin(i * 1.7), -170 - 0 + 260 * u - 260, 7, K.INK3, min(1, (1 - u) * 3))
    kk = clamp01(g.since(4) / 0.35)
    if kk > 0:
        K.text_card(c, 230, -40, ["营养成分表", "看看【钠】"], 40, 360, K.PAPER, K.INK, K.RED, kk, 0,
                    0.4 + 0.6 * K.ease_out_back(kk, 1.6), ACC, "serif", 0.9)


# ---------------------------------------------------------------- 11 正餐稳了

def meals_line(c, g, t, d):
    """一天的曲线：三顿正餐都平稳，两餐之间没有“低谷”，问号零食淡出。"""
    def day(u):
        v = 0.0
        for m in (0.08, 0.42, 0.75):
            v += T.bump(max(0.0, u - m), 0.4, 0.06, 1.8)
        return min(1.0, v)
    p = clamp01(g.since(0) / max(0.1, g.b(10)))
    T.chart(c, 0, 0, 860, 480, [(day, T.FLAT, p, 8, "")], xlabel="一天", ylabel="血糖")
    for i, (m, lab) in enumerate(((0.08, "早"), (0.42, "午"), (0.75, "晚"))):
        k = clamp01(g.since(1 + 3 * i) / 0.3)
        if k > 0:
            K.text(c, lab, -430 + m * 860 + 30, 280, 30, "serif_black", ACC, k)


# ---------------------------------------------------------------- 12 一小把

def handful(c, g, t, d):
    k = clamp01(g.since(0) / 0.3)
    with K.at(c, -220, 0, 0, 0.4 + 0.6 * K.ease_out_back(k, 1.6)):
        with K.paper(c, k, 0.9):
            K.dot(c, 0, 40, 170, K.SKIN)
            for i in range(4):
                K.rr(c, -120 + i * 80, -90, 60, 150, 30, K.SKIN, k)
        snack(c, "nuts", 0, 10, 160, k)
    kk = clamp01(g.since(4) / 0.35)
    if kk > 0:
        K.text_card(c, 230, 0, ["一小把", "≈ 一个掌心"], 44, 360, K.PAPER, K.INK, ACC, kk, 0,
                    0.4 + 0.6 * K.ease_out_back(kk, 1.6), ACC, "serif", 0.9)
    k3 = clamp01(g.since(8) / 0.35)
    if k3 > 0:
        K.pill(c, 0, 330, "零食也算一天的热量", 34, ACC, K.PAPER, k3)


# ---------------------------------------------------------------- 13 包里放坚果

def bag(c, g, t, d):
    k = clamp01(g.since(0) / 0.35)
    with K.at(c, 0, 80, 0, 0.4 + 0.6 * K.ease_out_back(k, 1.6)):
        with K.paper(c, k, 1.0):
            K.rr(c, 0, 0, 520, 400, 50, "#6B8CA8")
        K.ring(c, 0, -200, 110, K.shade("#6B8CA8", 0.25), 22, k, 0.5, 180)
        K.rr(c, 0, -40, 520, 30, 10, K.shade("#6B8CA8", 0.15), k)
    drop = clamp01(g.since(4) / 0.6)
    if drop > 0:
        y = -420 + 420 * ease_in_out(drop)
        with K.at(c, 0, y):
            with K.paper(c, 1, 0.8):
                K.rr(c, 0, 0, 200, 150, 30, "#E9DCC3")
            snack(c, "nuts", 0, 0, 110)
    if g.since(7) >= 0:
        K.burst(c, 0, -10, g.since(7), K.GOLD, 80, 200, 10, 7)


def finale(c, g, t, d):
    k, sc = pop(g, 0)
    snack(c, "nuts", -190, 0, 230, k, sc)
    k2, sc2 = pop(g, 1)
    snack(c, "cheese", 190, 0, 230, k2, sc2)


def build() -> Episode:
    shots = [
        Shot(3, "下午三点，|肚子咕咕叫。", "情境演绎", [
            Icon("clock", 280, 520, 140, at=1, enter="pop", sfx="wood_high", note="下午三点的钟"),
            Fig(560, GROUND, 360, at=0, mood="calm", hair="short",
                moves=[(4, dict(pose="hug", mood="worried", sfx="tom", note="肚子叫，主角捂住肚子"))]),
            Bubble("咕……", 760, 760, 44, at=5, tail=(-0.5, 1), sfx="bongo_low", note="咕咕声"),
        ], draw=ground, note="下午三点，主角捂着肚子，旁边冒出“咕……”"),
        Shot(3, "顺手抓起饼干、|糖果、果汁？", "情境演绎", [
            Custom(sweet_row, x=540, y=780, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "饼干"), (4, "wood_low", 0.7, "糖果"), (6, "bongo_high", 0.7, "果汁")],
            note="饼干、糖果、果汁按拍依次弹出"),
        Shot(2, "空腹吃甜零食，|容易带来尖峰。", "书中观点", [
            Custom(sweet_spike, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "尖峰曲线画出")], text_beat=0, note="一条甜零食后的尖峰曲线（示意）"),
        Shot(3, "非吃零食不可，|就选咸的。", "书中观点", [
            Big("零食", 540, 470, 150, at=0, sfx="kick", sub="savory snacks", note="概念落版（音乐 drop）"),
            Custom(savory_drop, x=540, y=880, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.7, "坚果"), (6, "wood_low", 0.7, "奶酪"), (8, "bongo_high", 0.7, "鸡蛋"),
                 (10, "bongo_low", 0.7, "黄瓜")],
            note="drop 处“零食”砸下；坚果、奶酪、鸡蛋、黄瓜按拍弹出"),
        Shot(3, "坚果、奶酪、|鸡蛋、黄瓜。", "书中观点", [
            Custom(savory_grid, x=540, y=800, at=0, enter="none"),
        ], hits=[(1, "wood_high", 0.7, "坚果卡"), (3, "wood_low", 0.7, "奶酪卡"), (5, "bongo_high", 0.7, "鸡蛋卡"),
                 (7, "bongo_low", 0.7, "黄瓜卡")],
            note="四张卡片：坚果、奶酪、鸡蛋、黄瓜"),
        Shot(3, "甜的和咸的，|曲线差很多。", "书中观点", [
            Custom(compare, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "甜零食曲线"), (6, "wood_low", 0.7, "咸零食曲线")],
            note="同一张图：甜零食的尖峰与低谷，咸零食的平缓曲线（示意）"),
        Shot(3, "书里说：吃咸的，|不容易很快又饿。", "书中观点", [
            Fig(400, GROUND, 360, at=0, mood="smile", hair="short",
                moves=[(4, dict(pose="cheer", mood="happy", sfx="clap", note="主角精神起来"))]),
            Custom(lambda c, g, t, d: snack(c, "nuts", 0, 0, 190, *pop(g, 1)), x=760, y=760, at=0, enter="none",
                   sfx="wood_high", note="一小碟坚果"),
            Icon("clock", 780, 480, 110, at=6, enter="pop", sfx="wood_low", note="时间过去，还不饿"),
        ], draw=ground, note="主角吃了坚果，精神起来，时钟走过还不饿"),
        Shot(2, "包装写“无糖”，|也要看配料。", "常见误解", [
            Custom(package, x=540, y=780, at=0, enter="none", sfx="wood_low", note="无糖饼干包装"),
        ], hits=[(3, "rim", 0.8, "配料表：小麦粉、淀粉")], text_beat=0,
            note="一包“无糖饼干”，旁边弹出配料表，高亮小麦粉、淀粉"),
        Shot(2, "饼干里的淀粉，|一样会变成葡萄糖。", "常见误解", [
            Custom(starch_to_glucose, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.6, "饼干"), (2, "shaker", 0.7, "箭头"), (6, "rim", 0.8, "葡萄糖")],
            text_beat=0, note="饼干经箭头变成一堆葡萄糖小六边形"),
        Shot(3, "咸的也别太咸，|看看钠含量。", "常见误解", [
            Custom(salt, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "盐瓶"), (2, "shaker", 0.8, "盐撒下来"), (4, "wood_high", 0.7, "营养成分表")],
            note="盐瓶晃动撒盐，旁边弹出“营养成分表：看看钠”"),
        Shot(3, "正餐吃稳了，|两餐之间也没那么饿。", "书中观点", [
            Custom(meals_line, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.7, "早餐"), (4, "wood_low", 0.7, "午餐"), (7, "bongo_high", 0.7, "晚餐")],
            note="一整天的血糖曲线，三顿正餐都平缓（示意）"),
        Shot(4, "零食也算热量，|一小把就够。", "专家提醒", [
            Custom(handful, x=540, y=780, at=0, enter="none", sfx="wood_low", note="手心里一小把坚果"),
        ], hits=[(4, "wood_high", 0.7, "“一小把≈一个掌心”"), (8, "rim", 0.7, "零食也算热量")],
            note="手心里一小把坚果，旁边标“一小把≈一个掌心”，下方提示零食也算一天的热量"),
        Shot(4, "小练习：在包里|放一小把坚果。", "小练习", [
            Custom(bag, x=540, y=780, at=0, enter="none", sfx="wood_low", note="背包出现"),
        ], hits=[(4, "shaker", 0.6, "坚果盒落下"), (7, "clap", 0.8, "装进包里")],
            note="一只背包，坚果盒从上方落进包里"),
        Shot(2, "饿了不慌，|咸的先上。", "书中观点", [
            Custom(finale, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.7, "坚果"), (1, "wood_low", 0.7, "奶酪")], text_beat=0,
            note="坚果和奶酪并排弹出"),
        ending(11, REFS),
    ]
    return Episode(11, "snack", "零食", TITLES[11], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[11]}｜控糖革命11 零食", hashtags="#控糖 #血糖 #零食 #控糖革命 #健康",
                   cover_title="饿了，|零食选【甜】还是【咸】？", cover_sub="控糖革命 · 零食", cover_shot=5, cover_t=5.0,
                   notes=[
                       "“非吃零食不可，就选咸的”是书中第 9 个方法的大意；“吃咸的不容易很快又饿”“正餐吃稳了两餐之间不那么饿”"
                       "也是书中观点，标“书中观点”。",
                       "第 3、6、11 镜曲线为示意，不是实测数据。",
                       "“无糖”食品通常指不额外加蔗糖，但其中的面粉、淀粉同样会被分解成葡萄糖（事实核查 #3）。",
                       "“看看钠含量”“零食也算一天的热量”为通行营养建议；“一小把≈一个掌心”是常见的估量说法。",
                   ], **SERIES).build()
