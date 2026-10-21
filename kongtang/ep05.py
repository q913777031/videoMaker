"""05 卡路里：热量一样，效果也一样吗？（书中第 3 个方法“别只数卡路里”）"""

import math

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Big, Bubble, Custom, Episode, Fig, Shot, Txt

from . import kit_tang as T
from .common import GROUND, SERIES, TITLES, ending, ground, refs

ACC = "#C98A2B"
REFS = refs("Hall 等（2019）Cell Metabolism 30(1):67–77")


def spike_fn(u):
    return T.bump(u, 1.0, 0.18, 2.8, 0.2)


def flat_fn(u):
    return T.bump(u, 0.38, 0.32, 1.6)


def soda(c, x, y, s, alpha=1.0):
    """一瓶甜饮料（示意，不画任何品牌）。"""
    with K.fade(c, alpha):
        with K.paper(c, 1, 0.8):
            K.rr(c, x, y + s * 0.08, s * 0.42, s * 0.8, s * 0.12, "#C94A4A")
        K.rr(c, x, y - s * 0.42, s * 0.2, s * 0.16, s * 0.04, "#C94A4A")
        K.rr(c, x, y - s * 0.52, s * 0.22, s * 0.06, s * 0.02, K.DARK)
        K.rr(c, x, y + s * 0.1, s * 0.42, s * 0.22, 0, K.PAPER)
        K.text(c, "甜饮料", x, y + s * 0.11, s * 0.1, "serif_black", "#C94A4A")


def kcal_tag(c, x, y, s, alpha=1.0):
    K.pill(c, x, y, s, 30, K.INK, K.PAPER, alpha)


# ---------------------------------------------------------------- 1 数热量

def counting(c, g, t, d):
    """计算器式的热量牌：数字按拍往上跳。"""
    vals = [120, 350, 680, 1240]
    n = sum(g.since(2 + 2 * i) >= 0 for i in range(len(vals)))
    v = vals[n - 1] if n else 0
    K.card(c, 0, 0, 460, 260, K.DARK, 1, 30, 1.0)
    K.text(c, "今日热量", 0, -70, 32, "sans_medium", "#C9D2E6")
    bump = 1 + 0.12 * math.sin(clamp01(g.since(2 + 2 * (n - 1)) / 0.3) * math.pi) if n else 1
    with K.at(c, 0, 30, 0, bump):
        K.text(c, f"{v} 千卡", 0, 0, 72, "black", "#FFE7A8")


# ---------------------------------------------------------------- 2 同热量两份

def two_meals(c, g, t, d):
    k1 = clamp01(g.since(0) / 0.35)
    k2 = clamp01(g.since(d.get("b1", 2)) / 0.35)
    if k1 > 0:
        soda(c, -230, -20, 300, k1)
        kcal_tag(c, -230, 200, "约 200 千卡", k1)
    if k2 > 0:
        T.plate(c, 230, -20, 180, k2)
        T.food(c, "egg", 180, -50, 110, k2)
        T.food(c, "broccoli", 280, 10, 100, k2)
        T.food(c, "nuts", 230, -110, 80, k2)
        kcal_tag(c, 230, 200, "约 200 千卡", k2)
    k = clamp01(g.since(d.get("beq", 6)) / 0.3)
    if k > 0:
        K.text(c, "=", 0, -20, 110, "black", ACC, k)


# ---------------------------------------------------------------- 6 曲线对比

def compare(c, g, t, d):
    p1 = clamp01(g.since(1) / max(0.1, g.b(5) - g.b(1)))
    p2 = clamp01(g.since(6) / max(0.1, g.b(10) - g.b(6)))
    T.chart(c, 0, 0, 820, 520, [(spike_fn, T.SPIKE, p1, 9, "甜饮料"), (flat_fn, T.FLAT, p2, 9, "鸡蛋配菜")])


# ---------------------------------------------------------------- 7 饱腹感

def fullness(c, g, t, d):
    """两个饱腹感进度条：甜饮料很快掉下去，鸡蛋配菜维持得更久（示意）。"""
    for i, (lab, col, decay) in enumerate((("甜饮料", T.SPIKE, 0.55), ("鸡蛋配菜", T.FLAT, 0.12))):
        y = -120 + i * 240
        K.text(c, lab, -420, y, 40, "serif_black", col, 1, "left")
        K.rr(c, 90, y, 560, 60, 30, K.LINE)
        tt = max(0.0, g.since(2))
        lvl = clamp01(1 - decay * tt) if g.since(2) >= 0 else 1
        w = 560 * max(0.05, lvl)
        K.rr(c, 90 - 280 + w / 2, y, w, 60, 30, col)
    K.text(c, "饱腹感（示意）", 90, -260, 30, "sans_medium", K.INK2)


# ---------------------------------------------------------------- 10 研究证据

def hall(c, g, t, d):
    """两周超加工 + 两周未加工；每天多吃约 500 千卡的柱子。"""
    K.text(c, "20 位成年人 · 住院 4 周 · 想吃多少吃多少", 0, -350, 32, "sans_medium", K.INK2,
           clamp01(g.since(0) / 0.3))
    for i, (lab, col, h) in enumerate((("未加工饮食", T.FLAT, 300), ("超加工饮食", T.SPIKE, 300 + 125))):
        x = -200 + i * 400
        k = clamp01(g.since(2 + 2 * i) / 0.6)
        if k <= 0:
            continue
        hh = h * ease_in_out(k)
        K.rr(c, x, 260 - hh / 2, 200, max(1, hh), 18, K.tint(col, 0.2))
        K.text(c, lab, x, 310, 34, "serif_black", col, 1)
    k = clamp01(g.since(7) / 0.35)
    if k > 0:
        K.seg(c, 100, 260 - 300, 300, 260 - 300, K.INK3, 4, k)
        K.arrow(c, (340, 260 - 300), (340, 260 - 420), K.RED, 8, k, k, 0, 24)
        K.pill(c, 200, -230, "每天多吃约 500 千卡", 34, K.RED, K.PAPER, k)


# ---------------------------------------------------------------- 11 专家提醒

def balance_scale(c, g, t, d):
    K.icon(c, "scale", 0, 60, 300, K.INK2, 1, 0.8, 3 * math.sin(g.t * 1.4))
    k1 = clamp01(g.since(1) / 0.35)
    k2 = clamp01(g.since(4) / 0.35)
    if k1 > 0:
        K.pill(c, -230, -170, "吃进的热量", 34, ACC, K.PAPER, k1)
    if k2 > 0:
        K.pill(c, 230, -170, "消耗的热量", 34, K.HERO, K.PAPER, k2)


def not_only(c, g, t, d):
    """“只看热量”被划掉，换成“热量 + 吃的是什么”。"""
    K.text(c, "只看热量", 0, -110, 70, "serif_black", K.INK3)
    k = clamp01(g.since(2) / 0.3)
    if k > 0:
        K.seg(c, -170, -110, -170 + 340 * k, -110, K.RED, 10)
    k2 = clamp01(g.since(5) / 0.4)
    if k2 > 0:
        K.text_card(c, 0, 140, ["热量 + 【吃的是什么】"], 52, None, K.PAPER, K.INK, ACC, k2, 0,
                    0.4 + 0.6 * K.ease_out_back(k2, 1.6), ACC, "serif", 0.8)


# ---------------------------------------------------------------- 13 小练习

def label(c, g, t, d):
    """营养标签：热量之外，按拍圈出“糖”和“膳食纤维”。"""
    rows = [("能量", "850 千焦"), ("蛋白质", "3.2 克"), ("脂肪", "5.1 克"), ("碳水化合物", "30.4 克"),
            ("— 糖", "18.0 克"), ("膳食纤维", "1.2 克")]
    K.card(c, 0, 0, 600, 620, K.PAPER, 1, 18, 1.0)
    K.text(c, "营养成分表（示意）", 0, -250, 36, "serif_black", K.INK)
    K.seg(c, -260, -210, 260, -210, K.INK, 4)
    for i, (a, b) in enumerate(rows):
        y = -160 + i * 72
        K.text(c, a, -240, y, 32, "serif", K.INK, 1, "left")
        K.text(c, b, 240, y, 32, "serif", K.INK, 1, "right")
        K.seg(c, -260, y + 36, 260, y + 36, K.LINE, 2)
    for i, (row, b) in enumerate(((0, 2), (4, 5), (5, 8))):
        k = clamp01(g.since(b) / 0.3)
        if k > 0:
            y = -160 + row * 72
            K.rr_stroke(c, 0, y, 560 + 20 * (1 - k), 62, 14, (K.INK3, K.RED, T.FLAT)[i], 6, k)


def build() -> Episode:
    shots = [
        Shot(3, "减肥时，很多人|每一口都在算热量。", "情境演绎", [
            Custom(counting, x=540, y=600, at=0, enter="pop"),
            Fig(540, GROUND, 330, at=0, pose="think", mood="worried", hair="short"),
        ], draw=ground, hits=[(2, "wood_high", 0.6, "热量 120"), (4, "wood_low", 0.6, "350"), (6, "bongo_high", 0.6, "680"),
                              (8, "bongo_low", 0.7, "1240")],
            note="热量牌上的数字按拍往上跳，主角皱眉算着"),
        Shot(3, "同样 200 千卡，|一瓶甜饮料，一份鸡蛋配菜。", "情境演绎", [
            Custom(two_meals, x=540, y=760, at=0, enter="none", b1=2, beq=6),
        ], hits=[(0, "wood_low", 0.7, "甜饮料"), (2, "wood_high", 0.7, "鸡蛋配菜"), (6, "rim", 0.8, "等号")],
            note="左边一瓶甜饮料，右边一盘鸡蛋、青菜、坚果，都标“约 200 千卡”，中间等号（示意）"),
        Shot(2, "对身体来说，|真的一样吗？", "情境演绎", [
            Custom(two_meals, x=540, y=760, at=0, enter="none", b1=-9, beq=-9),
            Custom(lambda c, g, t, d: K.icon(c, "question", 0, 0, 120, ACC, clamp01(g.since(2) / 0.3), 0.6),
                   x=540, y=500, at=0, enter="none", sfx="bongo_low", note="问号"),
        ], text_beat=0, cut=True, note="等号上方冒出问号"),
        Shot(3, "书中第 3 个方法：|别只数卡路里。", "书中观点", [
            Big("卡路里", 540, 470, 150, at=0, sfx="kick", sub="方法 3 · stop counting calories", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: [K.text(c, s, -260 + i * 260, 30 * math.sin(g.t * 2 + i), 60, "black", K.INK3,
                                              clamp01(g.since(3 + 2 * i) / 0.3)) for i, s in enumerate(("120", "350", "680"))],
                   x=540, y=900, at=0, enter="none"),
        ], hits=[(3, "wood_high", 0.6, "数字"), (5, "wood_low", 0.6, "数字"), (7, "bongo_high", 0.6, "数字")],
            note="drop 处“卡路里”砸下，几个热量数字飘在下面"),
        Shot(3, "书里说：同样的热量，|对血糖的影响可能不同。", "书中观点", [
            Custom(lambda c, g, t, d: two_meals(c, g, t, dict(b1=-9, beq=-9)), x=540, y=760, at=0, enter="fade"),
        ], note="甜饮料与鸡蛋配菜并排（示意）"),
        Shot(3, "甜饮料冲得快，|鸡蛋配菜平得多。", "书中观点", [
            Custom(compare, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "甜饮料的尖峰曲线"), (6, "wood_low", 0.7, "鸡蛋配菜的平稳曲线")],
            note="两条曲线：甜饮料尖峰，鸡蛋配菜平稳（示意）"),
        Shot(3, "饱腹感也不一样：|有的很快又饿了。", "书中观点", [
            Custom(fullness, x=540, y=780, at=0, enter="fade"),
        ], hits=[(2, "shaker", 0.6, "饱腹感条开始下降"), (6, "wood_high", 0.6, "甜饮料那条见底")],
            note="两条饱腹感进度条：甜饮料很快掉下去，鸡蛋配菜维持更久（示意）"),
        Shot(2, "有研究支持|“吃什么”很重要吗？", "研究证据", [
            Custom(lambda c, g, t, d: K.icon(c, "question", 0, 0, 220, ACC, clamp01(g.since(0) / 0.3), 0.8),
                   x=540, y=760, at=0, enter="none", sfx="bongo_low", note="大问号"),
        ], text_beat=0, note="一个大问号"),
        Shot(2, "2019 年，|美国一项住院试验：", "研究证据", [
            Custom(lambda c, g, t, d: K.icon(c, "house", 0, 0, 280, K.HERO, clamp01(g.since(0) / 0.3), 0.8),
                   x=540, y=760, at=0, enter="none", sfx="wood_high", note="研究机构"),
            Txt("Hall 等 · Cell Metabolism", 540, 1000, 32, at=1, font="sans_medium", color=K.INK2),
        ], text_beat=0, note="一栋建筑代表住院研究，标 Hall 等 · Cell Metabolism"),
        Shot(4, "超加工饮食随便吃，|每天多吃约 500 千卡。", "研究证据", [
            Custom(hall, x=540, y=800, at=0, enter="none"),
        ], research=True, hits=[(0, "wood_low", 0.6, "研究说明"), (2, "wood_high", 0.7, "未加工饮食柱"),
                                (4, "bongo_high", 0.7, "超加工饮食柱"), (7, "rim", 0.8, "多吃约 500 千卡")],
            note="20 位成年人住院 4 周，两种饮食各两周、想吃多少吃多少：超加工饮食组每天多吃约 500 千卡"),
        Shot(3, "但要说清楚：|热量平衡依然决定体重。", "专家提醒", [
            Custom(balance_scale, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.7, "吃进的热量"), (4, "wood_low", 0.7, "消耗的热量")],
            note="天平两边：吃进的热量、消耗的热量"),
        Shot(3, "书的意思是“别只看热量”，|不是“热量不重要”。", "专家提醒", [
            Custom(not_only, x=540, y=780, at=0, enter="none"),
        ], hits=[(2, "rim", 0.8, "划掉“只看热量”"), (5, "wood_high", 0.7, "热量 + 吃的是什么")],
            note="“只看热量”被红线划掉，换成“热量 + 吃的是什么”"),
        Shot(4, "小练习：看营养标签时，|除了热量，也看糖和纤维。", "小练习", [
            Custom(label, x=540, y=790, at=0, enter="pop"),
        ], hits=[(2, "wood_low", 0.6, "圈出能量"), (5, "rim", 0.8, "圈出糖"), (8, "wood_high", 0.7, "圈出膳食纤维")],
            note="营养成分表（示意）：先圈能量，再圈糖和膳食纤维"),
        Shot(2, "下一讲：|早餐，为什么别吃太甜？", "书中观点", [
            Custom(lambda c, g, t, d: (T.food(c, "cake", -120, 0, 200, clamp01(g.since(0) / 0.3)),
                                       T.food(c, "egg", 140, 0, 200, clamp01(g.since(1) / 0.3))),
                   x=540, y=760, at=0, enter="none", sfx="wood_high", note="蛋糕与鸡蛋"),
            Bubble("早餐吃哪个？", 540, 560, 40, at=2, sfx="bongo_high", note="气泡"),
        ], text_beat=0, note="蛋糕与煎蛋并排，预告下一期"),
        ending(5, REFS),
    ]
    return Episode(5, "calories", "卡路里", TITLES[5], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[5]}｜控糖革命05 卡路里", hashtags="#控糖 #卡路里 #控糖革命 #减肥 #科普",
                   cover_title="热量一样，|效果也【一样】吗？", cover_sub="控糖革命 · 方法 3", cover_shot=3, cover_t=5.5,
                   notes=[
                       "“别只数卡路里”是书中第 3 个方法；甜饮料与鸡蛋配菜各约 200 千卡的对比、曲线与饱腹感条均为示意。",
                       "Hall 等（2019，Cell Metabolism）：20 位成年人住院，超加工与未加工饮食各吃两周、想吃多少吃多少，"
                       "超加工饮食期间每天多摄入约 500 千卡。具体数值来自对论文的记忆，未与原文逐字核对。",
                       "热量平衡依然决定体重；书的意思是除了热量，也要看吃的是什么。",
                       "第 13 镜营养成分表为示意数据。",
                   ], **SERIES).build()
