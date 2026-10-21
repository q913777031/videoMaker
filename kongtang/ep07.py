"""07 糖：蜂蜜，比白糖更健康吗？（书中第 5 个方法：喜欢哪种糖就吃哪种——它们都一样）"""

import math

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Icon, Shot, Txt

from . import kit_tang as T
from .common import GROUND, SERIES, TITLES, ending, ground, refs

ACC = "#C8763A"
FRU = "#5E9A6E"          # 果糖
GLC = T.GLU              # 葡萄糖
OTH = "#C9C1B3"          # 水和其他
REFS = refs("蜂蜜糖分组成研究（PMC10582368）；USDA 食物成分数据")


def pop(g, k, dur=0.3):
    return clamp01(g.since(k) / dur)


def popscale(k):
    return 0.3 + 0.7 * K.ease_out_back(k, 1.8) if k > 0 else 0


def comp_bar(c, x, y, w, h, parts, p, size=30):
    """成分条：parts=[(比例, 颜色, 标签)]，p 为从左到右的填充进度。"""
    K.rr(c, x, y, w, h, 16, K.LINE)
    acc = 0.0
    x0 = x - w / 2
    for frac, col, lab in parts:
        seg = w * frac
        shown = clamp01((p * w - acc) / max(seg, 1e-6))
        if shown > 0:
            K.rr(c, x0 + acc + seg * shown / 2, y, max(1.0, seg * shown - 4), h - 8, 12, col)
            if shown >= 1 and lab:
                K.text(c, lab, x0 + acc + seg / 2, y, size, "serif_black", K.PAPER if col != OTH else K.INK2)
        acc += seg


def legend(c, x, y, k):
    for i, (col, lab) in enumerate(((GLC, "葡萄糖"), (FRU, "果糖"), (OTH, "水和其他"))):
        K.dot(c, x + i * 220 - 220, y, 14, col, k)
        K.text(c, lab, x + i * 220 - 196, y, 28, "sans_medium", K.INK2, k, "left")


# ---------------------------------------------------------------- 1–2 钩子

def shelf(c, g, t, d):
    """超市货架：蜂蜜、方糖（红糖色）、糖浆瓶按拍上架，第 6 拍贴“天然”标签。"""
    K.rr(c, 0, 140, 640, 26, 12, K.mix(K.OTHER, K.PAPER, 0.2))
    k = pop(g, 0)
    if k > 0:
        T.food(c, "honey", -220, 30, 200, clamp01(k * 3), 0, popscale(k))
    k = pop(g, 2)
    if k > 0:
        with K.at(c, 0, 40, 0, popscale(k)):
            for dx, dy in ((-40, 30), (40, 30), (0, -40)):
                K.rr(c, dx, dy, 70, 70, 10, "#B2763E", clamp01(k * 3))
        K.text(c, "红糖", 0, 120, 28, "sans_medium", K.INK2, k)
    k = pop(g, 4)
    if k > 0:
        with K.at(c, 220, 20, 0, popscale(k)):
            K.rr(c, 0, 30, 110, 190, 20, "#C9873A", clamp01(k * 3))
            K.rr(c, 0, -85, 50, 50, 8, K.DARK, clamp01(k * 3))
            K.rr(c, 0, 40, 84, 60, 8, K.PAPER, clamp01(k * 3))
            K.text(c, "糖浆", 0, 41, 26, "serif_black", "#8A5A2B", clamp01(k * 3))


def natural_tag(c, g, t, d):
    T.food(c, "honey", -170, 30, 360, 1)
    k = pop(g, 2)
    if k > 0:
        with K.at(c, 220, -110, 10, 1.3 * popscale(k)):
            with K.paper(c, k, 0.8):
                K.rr(c, 0, 0, 220, 90, 16, K.GREEN)
            K.text(c, "天然", 0, 2, 48, "serif_black", K.PAPER, k)
    k = pop(g, 6)
    if k > 0:
        K.text(c, "更健康？", 230, 120, 70, "serif_black", ACC, k)


# ---------------------------------------------------------------- 5–7 成分

def sucrose(c, g, t, d):
    k = pop(g, 0, 0.4)
    T.food(c, "sugar", 0, -200, 220, k, 0, popscale(k))
    comp_bar(c, 0, 120, 840, 110, [(0.5, GLC, "葡萄糖 50%"), (0.5, FRU, "果糖 50%")],
             ease_in_out(clamp01(g.since(2) / 1.2)), 34)
    legend(c, 0, 260, pop(g, 6))


def honey_comp(c, g, t, d):
    k = pop(g, 0, 0.4)
    T.food(c, "honey", 0, -210, 220, k, 0, popscale(k))
    comp_bar(c, 0, 120, 840, 110, [(0.31, GLC, "31%"), (0.38, FRU, "38%"), (0.31, OTH, "")],
             ease_in_out(clamp01(g.since(2) / 1.2)), 34)
    legend(c, 0, 260, pop(g, 6))
    k2 = pop(g, 8)
    if k2 > 0:
        K.text(c, "约数，因产地而异", 0, 330, 28, "sans_medium", K.INK3, k2)


def agave(c, g, t, d):
    k = pop(g, 0, 0.4)
    with K.at(c, 0, -210, 0, popscale(k)):
        with K.paper(c, k, 1.0):
            K.rr(c, 0, 30, 130, 230, 24, "#D9A13A")
            K.rr(c, 0, -100, 60, 50, 10, K.DARK)
        K.rr(c, 0, 40, 100, 70, 10, K.PAPER, k)
        K.text(c, "龙舌兰", 0, 32, 24, "serif_black", "#8A5A2B", k)
        K.text(c, "糖浆", 0, 58, 24, "serif_black", "#8A5A2B", k)
    comp_bar(c, 0, 120, 840, 110, [(0.15, GLC, ""), (0.6, FRU, "果糖为主"), (0.25, OTH, "")],
             ease_in_out(clamp01(g.since(2) / 1.2)), 34)
    legend(c, 0, 260, pop(g, 6))


# ---------------------------------------------------------------- 8–9 果糖

def fructose_curve(c, g, t, d):
    p = clamp01(g.since(1) / max(0.1, g.b(6) - g.b(1)))
    T.chart(c, 0, 0, 820, 500, [(lambda u: T.bump(u, 0.3, 0.3, 1.6), FRU, p, 9, "果糖")])


def still_sugar(c, g, t, d):
    k = pop(g, 0, 0.4)
    K.icon(c, "scale", 0, -60, 300, K.INK, k, 0.8, 0, popscale(k))
    k2 = pop(g, 3)
    if k2 > 0:
        T.food(c, "sugar", -150, 160, 130, k2, 0, popscale(k2))
        T.food(c, "honey", 150, 160, 130, k2, 0, popscale(k2))
        K.text(c, "=", 0, 160, 70, "black", ACC, k2)


# ---------------------------------------------------------------- 10 都是糖

def merge(c, g, t, d):
    """四种糖从四周滑向中间，第 8 拍合成一堆方糖。"""
    m = ease_in_out(clamp01(g.since(4) / 1.6))
    names = [("honey", -300, -180, "蜂蜜"), ("sugar", 300, -180, "白糖"), ("cookie", -300, 200, "椰糖"),
             ("juice", 300, 200, "糖浆")]
    for i, (name, x, y, lab) in enumerate(names):
        k = pop(g, i * 0.5)
        if k <= 0:
            continue
        px, py = x * (1 - m), y * (1 - m)
        a = clamp01(k * 3) * (1 - clamp01((g.since(8)) / 0.3))
        T.food(c, name, px, py, 150, a, 0, popscale(k) * (1 - 0.5 * m))
        K.text(c, lab, px, py + 110, 30, "sans_medium", K.INK2, a)
    k = pop(g, 8, 0.35)
    if k > 0:
        T.food(c, "sugar", 0, 0, 260, k, 0, popscale(k))
        K.text(c, "都是糖", 0, 200, 50, "serif_black", ACC, k)


def not_healthier(c, g, t, d):
    natural_tag_static = 1.0
    with K.at(c, 0, -60, -6, 1):
        with K.paper(c, natural_tag_static, 0.8):
            K.rr(c, 0, 0, 340, 130, 20, K.GREEN)
        K.text(c, "天然", 0, 2, 70, "serif_black", K.PAPER)
    k = pop(g, 2, 0.25)
    if k > 0:
        K.seg(c, -200, -140, -200 + 400 * k, 20 + 0 * k - 160 * (1 - k) + 0, K.RED, 14)
    k2 = pop(g, 6)
    if k2 > 0:
        K.text(c, "≠ 更健康", 0, 170, 60, "serif_black", K.RED, k2)


def small_spoon(c, g, t, d):
    """一把小勺：勺里的糖按拍变少。"""
    k = pop(g, 0, 0.4)
    with K.at(c, 0, 0, -20, 1.4 * popscale(k)):
        K.rr(c, 180, 0, 360, 34, 17, "#B8B8B8", k)
        K.dot(c, -60, 0, 90, "#CFCFCF", k)
        left = 1 - 0.65 * ease_in_out(clamp01(g.since(4) / 1.6))
        for i in range(int(9 * left)):
            a = i * 0.9
            K.rr(c, -60 + 45 * math.cos(a) * (i % 3) / 2, -10 + 30 * math.sin(a) * (i % 3) / 2, 34, 34, 6,
                 "#FFFFFF", k)
    k2 = pop(g, 8)
    if k2 > 0:
        K.pill(c, 0, 230, "哪种都要少吃", 40, ACC, K.PAPER, k2)


# ---------------------------------------------------------------- 13 配料表

NAMES = ["白砂糖", "果葡糖浆", "麦芽糖浆", "浓缩果汁"]


def label_card(c, g, t, d):
    lines = ["配料：小麦粉、", "白砂糖、植物油、", "果葡糖浆、鸡蛋、", "麦芽糖浆、浓缩果汁、", "食用盐"]
    w, h = 680, 520
    K.card(c, 0, 0, w, h, K.PAPER, 1, 22, 1.0, 0, 1, ACC)
    y0 = -h / 2 + 90
    for i, ln in enumerate(lines):
        x = -w / 2 + 50
        y = y0 + i * 82
        K.text(c, ln, x, y, 42, "serif", K.INK, 1, "left")
        for j, nm in enumerate(NAMES):
            pos = ln.find(nm)
            if pos < 0:
                continue
            k = pop(g, 2 + 2 * j, 0.35)
            if k <= 0:
                continue
            pre = K.text_w(ln[:pos], 42, "serif")
            nw = K.text_w(nm, 42, "serif")
            K.rr(c, x + pre + nw * k / 2, y + 8, nw * k + 8, 22, 8, K.tint(ACC, 0.45), 0.9)
            K.text(c, ln, x, y, 42, "serif", K.INK, 1, "left")


def build() -> Episode:
    shots = [
        Shot(3, "蜂蜜、红糖、糖浆，|听起来更健康？", "情境演绎", [
            Custom(shelf, x=640, y=640, at=0, enter="none"),
            Fig(200, GROUND, 340, at=0, mood="smile", hair="short",
                moves=[(8, dict(pose="think", mood="worried", sfx="rim", note="主角犹豫"))]),
        ], draw=ground, hits=[(0, "wood_low", 0.7, "蜂蜜上架"), (2, "wood_high", 0.7, "红糖上架"), (4, "bongo_high", 0.7, "糖浆上架")],
            note="货架上按拍摆出蜂蜜、红糖、糖浆，主角站在下面犹豫"),
        Shot(3, "瓶子上还写着|“天然”。", "情境演绎", [
            Custom(natural_tag, x=540, y=780, at=0, enter="fade"),
        ], hits=[(2, "bongo_low", 0.8, "“天然”标签贴上"), (6, "wood_high", 0.7, "“更健康？”")],
            note="蜂蜜罐上贴出绿色“天然”标签，旁边打出“更健康？”"),
        Shot(2, "书里的回答是：|它们都一样。", "书中观点", [
            Icon("question", 540, 760, 220, color=ACC, at=0, enter="pop", sfx="wood_low", note="问号"),
        ], text_beat=0, note="画面中央一个大问号"),
        Shot(3, "糖：|换个名字，还是糖。", "书中观点", [
            Big("糖", 540, 470, 170, at=0, sfx="kick", sub="书中第 5 个方法", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: [T.food(c, n, -300 + i * 200, 0, 140, pop(g, 2 + 2 * i), 0,
                                              popscale(pop(g, 2 + 2 * i)))
                                       for i, n in enumerate(("sugar", "honey", "cookie", "juice"))],
                   x=540, y=930, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.6, "方糖"), (4, "wood_low", 0.6, "蜂蜜"), (6, "bongo_high", 0.6, "饼干"),
                 (8, "bongo_low", 0.6, "果汁")],
            note="drop 处“糖”砸下；方糖、蜂蜜、饼干、果汁按拍排开"),
        Shot(3, "白砂糖：|一半葡萄糖，一半果糖。", "机制示意", [
            Custom(sucrose, x=540, y=820, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "方糖"), (2, "shaker", 0.7, "成分条填充"), (6, "wood_high", 0.6, "图例")],
            note="方糖下方一条成分条：葡萄糖 50%、果糖 50%"),
        Shot(3, "蜂蜜：约 31% 葡萄糖，|38% 果糖。", "机制示意", [
            Custom(honey_comp, x=540, y=820, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "蜂蜜罐"), (2, "shaker", 0.7, "成分条填充"), (8, "wood_high", 0.6, "“因产地而异”")],
            note="蜂蜜成分条：葡萄糖约 31%、果糖约 38%，其余主要是水（因产地而异）"),
        Shot(3, "龙舌兰糖浆，|果糖比例更高。", "机制示意", [
            Custom(agave, x=540, y=820, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "糖浆瓶"), (2, "shaker", 0.7, "成分条填充")],
            note="龙舌兰糖浆的成分条以果糖为主（示意比例）"),
        Shot(2, "果糖本身，|升血糖不多；", "书中观点", [
            Custom(fructose_curve, x=540, y=790, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "果糖曲线")], text_beat=0, note="一条较低的果糖曲线（示意）"),
        Shot(2, "但它同样是糖，|多吃一样不好。", "书中观点", [
            Custom(still_sugar, x=540, y=800, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "天平"), (3, "rim", 0.8, "蜂蜜 = 白糖")], text_beat=0,
            note="天平两边：方糖与蜂蜜，中间一个等号"),
        Shot(3, "蜂蜜、白糖、椰糖、糖浆，|本质都是糖。", "书中观点", [
            Custom(merge, x=540, y=790, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.6, "四种糖出现"), (4, "shaker", 0.7, "滑向中间"), (8, "bongo_low", 0.8, "合成一堆方糖")],
            note="四种糖从四角滑向中间，第 8 拍合成一堆方糖，写“都是糖”"),
        Shot(3, "“天然”两个字，|不等于更健康。", "常见误解", [
            Custom(not_healthier, x=540, y=790, at=0, enter="pop"),
        ], hits=[(2, "rim", 0.9, "红线划掉"), (6, "wood_high", 0.7, "“≠ 更健康”")],
            note="绿色“天然”标签被红线划掉，下方写“≠ 更健康”"),
        Shot(4, "不管哪一种，|都要少吃。", "专家提醒", [
            Custom(small_spoon, x=540, y=780, at=0, enter="none"),
            Txt("通行营养学建议：限制添加糖", 540, 1180, 28, at=4, font="sans_medium", color=K.INK2),
        ], hits=[(0, "wood_low", 0.6, "小勺"), (4, "shaker", 0.7, "勺里的糖变少"), (8, "rim", 0.8, "“哪种都要少吃”")],
            note="一把小勺里的糖慢慢变少，标“哪种都要少吃”"),
        Shot(4, "小练习：看配料表，|认出各种糖的名字。", "小练习", [
            Custom(label_card, x=540, y=780, at=0, enter="pop"),
        ], hits=[(2, "wood_high", 0.7, "白砂糖"), (4, "wood_low", 0.7, "果葡糖浆"), (6, "bongo_high", 0.7, "麦芽糖浆"),
                 (8, "bongo_low", 0.7, "浓缩果汁")],
            note="一张配料表，白砂糖、果葡糖浆、麦芽糖浆、浓缩果汁按拍被高亮（示例配料表）"),
        Shot(2, "喜欢哪种就吃哪种，|但量要少。", "书中观点", [
            Custom(lambda c, g, t, d: T.food(c, "honey", 0, 0, 240, 1, 0, 1 + 0.03 * math.sin(g.t * 4)),
                   x=540, y=780, at=0, enter="pop", sfx="clap", note="一小罐蜂蜜"),
        ], text_beat=0, note="一小罐蜂蜜居中"),
        ending(7, REFS),
    ]
    return Episode(7, "sugar", "糖", TITLES[7], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[7]}｜控糖革命07 糖", hashtags="#控糖 #蜂蜜 #添加糖 #控糖革命 #健康",
                   cover_title="蜂蜜、红糖、糖浆，|真的比白糖【健康】？", cover_sub="控糖革命 · 糖",
                   cover_shot=5, cover_t=5.5,
                   notes=[
                       "“喜欢哪种糖就吃哪种——它们都一样”是书中第 5 个方法，片中标“书中观点”。",
                       "白砂糖（蔗糖）由一分子葡萄糖和一分子果糖组成，按分子计各占一半；蜂蜜约 38% 果糖、31% 葡萄糖、17% 水，"
                       "不同产地样本果糖约 34%–47%、葡萄糖约 33%–44%（PMC10582368）；龙舌兰糖浆以果糖为主，第 7 镜比例为示意。",
                       "果糖升血糖较少，但同样属于糖；“多吃一样不好”是书中观点与通行营养学建议（限制添加糖）的共同结论，"
                       "片中不展开果糖代谢的具体危害。",
                       "第 13 镜配料表为示例，不对应任何具体商品。",
                       "第 8 镜曲线为示意，不是实测数据。",
                   ], **SERIES).build()
