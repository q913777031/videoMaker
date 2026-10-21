"""12 碳水穿衣：吃碳水，怎么吃更稳？（系列收尾）"""

import math

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Shot

from . import kit_tang as T
from .common import SERIES, TITLES, ending, refs

ACC = "#B0563E"
REFS = refs("混合膳食与餐后血糖反应的相关研究综述（蛋白质、脂肪、膳食纤维对碳水血糖反应的影响）")
HACKS = ("进食顺序", "先吃蔬菜", "别只数热量", "咸味早餐", "糖都一样", "甜点放饭后", "饭前醋", "饭后走动", "咸味零食",
         "碳水穿衣")


def pop(g, k0, dur=0.3):
    k = clamp01(g.since(k0) / dur)
    return k, 0.3 + 0.7 * K.ease_out_back(k, 1.8)


def shirt(c, x, y, s, color, alpha=1.0):
    """一件小 T 恤（“衣服”）。"""
    with K.fade(c, alpha):
        K.poly(c, [(x - s * 0.5, y - s * 0.3), (x - s * 0.2, y - s * 0.45), (x + s * 0.2, y - s * 0.45),
                   (x + s * 0.5, y - s * 0.3), (x + s * 0.38, y - s * 0.08), (x + s * 0.28, y - s * 0.15),
                   (x + s * 0.28, y + s * 0.45), (x - s * 0.28, y + s * 0.45), (x - s * 0.28, y - s * 0.15),
                   (x - s * 0.38, y - s * 0.08)], color)
        K.dot(c, x, y - s * 0.43, s * 0.1, K.BG)


# ---------------------------------------------------------------- 1–3 光秃秃的面包

def bare_bread(c, g, t, d):
    k, sc = pop(g, 0)
    shiver = 6 * math.sin(g.t * 30) * clamp01(g.since(4) / 0.3)
    T.food(c, "bread", shiver, 0, 280, k, 0, sc)
    if g.since(4) >= 0:
        for i in range(3):
            a = clamp01(g.since(4 + i) / 0.3)
            K.seg(c, -200 - i * 20, -120 + i * 60, -240 - i * 20, -120 + i * 60, K.INK3, 6, a)
            K.seg(c, 200 + i * 20, -120 + i * 60, 240 + i * 20, -120 + i * 60, K.INK3, 6, a)


def bare_spike(c, g, t, d):
    T.food(c, "bread", -330, -310, 120, clamp01(g.since(0) / 0.3))
    p = clamp01(g.since(1) / max(0.1, g.b(10) - g.b(1)))
    T.chart(c, 60, 60, 680, 440, [(lambda u: T.bump(u, 1.0, 0.2, 2.6, 0.15), T.SPIKE, p, 9, "单吃")])


def dress_up(c, g, t, d):
    T.food(c, "bread", 0, 40, 260, 1)
    k = clamp01(g.since(1) / 0.5)
    if k > 0:
        y = -360 + 300 * ease_in_out(k)
        shirt(c, 0, y, 300, K.mix(ACC, K.PAPER, 0.25), 0.92)
    if g.since(2) >= 0:
        K.burst(c, 0, 0, g.since(2), K.GOLD, 140, 300, 10, 7)


# ---------------------------------------------------------------- 4 drop

def three_clothes(c, g, t, d):
    items = (("蛋白质", "egg"), ("脂肪", "nuts"), ("膳食纤维", "broccoli"))
    for i, (lab, name) in enumerate(items):
        k, sc = pop(g, 4 + 2 * i)
        if k <= 0:
            continue
        x = -300 + i * 300
        T.food(c, name, x, -20, 150, k, 0, sc)
        K.pill(c, x, 120, lab, 34, ACC, K.PAPER, k)


# ---------------------------------------------------------------- 5 / 6 搭配

def pair(c, x, y, a, b, k, sc):
    T.food(c, a, x - 90, y, 150, k, 0, sc)
    K.text(c, "+", x, y, 70, "black", K.INK3, k)
    T.food(c, b, x + 90, y, 150, k, 0, sc)


def pairs(c, g, t, d):
    k, sc = pop(g, 1)
    if k > 0:
        pair(c, -230, -60, "bread", "egg", k, sc)
        K.text(c, "面包 + 鸡蛋", -230, 80, 36, "serif_black", K.INK2, k)
    k, sc = pop(g, 5)
    if k > 0:
        pair(c, 230, -60, "cookie", "nuts", k, sc)
        K.text(c, "饼干 + 坚果", 230, 80, 36, "serif_black", K.INK2, k)


def rice_plate(c, g, t, d):
    T.plate(c, 0, 0, 330)
    for i, (name, dx, dy, s) in enumerate((("rice", 0, -110, 170), ("broccoli", -140, 80, 150), ("drumstick", 140, 80, 150))):
        k, sc = pop(g, 1 + 2 * i)
        if k > 0:
            T.food(c, name, dx, dy, s, k, 0, sc)
    labs = (("米饭", 0, -260), ("菜", -280, 230), ("肉", 280, 230))
    for i, (lab, x, y) in enumerate(labs):
        k = clamp01(g.since(1 + 2 * i) / 0.3)
        if k > 0:
            K.text(c, lab, x, y, 36, "serif_black", ACC, k)


# ---------------------------------------------------------------- 7 / 8 研究

def dressed_curve(c, g, t, d):
    T.chart(c, 0, 0, 820, 520, [
        (lambda u: T.bump(u, 1.0, 0.2, 2.6, 0.15), T.SPIKE, clamp01(g.since(1) / 1.4), 9, "单吃碳水"),
        (lambda u: T.bump(u, 0.55, 0.28, 1.8), T.FLAT, clamp01(g.since(6) / 1.4), 9, "穿上衣服")])


def varies(c, g, t, d):
    vals = (0.85, 0.55, 0.7, 0.4)
    labs = ("A", "B", "C", "D")
    for i, v in enumerate(vals):
        k = ease_in_out(clamp01(g.since(i * 0.6) / 0.5))
        x = -300 + i * 200
        bh = 420 * v * k
        K.rr(c, x, 220 - bh / 2, 130, max(1, bh), 14, K.mix(ACC, K.PAPER, 0.15 + 0.15 * i))
        K.text(c, f"搭配 {labs[i]}", x, 270, 30, "sans_medium", K.INK2)
    K.text(c, "示意：降幅各不相同", 0, -260, 28, "sans_medium", K.INK3)


# ---------------------------------------------------------------- 9 别加一大勺油

def oil(c, g, t, d):
    T.food(c, "bread", -200, 40, 230, 1)
    k = clamp01(g.since(1) / 0.4)
    with K.at(c, 120, -120 + 40 * k, -40 * k):
        with K.paper(c, 1, 0.9):
            K.rr(c, 0, 0, 120, 260, 30, "#F2D36B")
            K.rr(c, 0, -150, 50, 60, 10, "#8A6A2A")
        K.text(c, "油", 0, 20, 50, "serif_black", "#8A6A2A")
    if g.since(2) >= 0:
        for i in range(6):
            u = (g.t * 1.2 + i / 6) % 1
            K.dot(c, 40 - 160 * u, -40 + 80 * u, 12, "#F2D36B", min(1, (1 - u) * 3))
    kk = clamp01(g.since(4) / 0.3)
    if kk > 0:
        K.icon(c, "cross", 300, 160, 120, K.RED, kk, 0.5)


# ---------------------------------------------------------------- 10 / 11 十个方法回顾

def tiles(c, g, t, d):
    lo, hi = d["lo"], d["hi"]
    for i in range(10):
        if i < lo - 5:
            continue
        x = -340 + (i % 5) * 170
        y = -170 + (i // 5) * 330
        k = 1.0 if i < lo else clamp01(g.since((i - lo) * 1.0 + 0.5) / 0.3)
        if i >= hi or k <= 0:
            continue
        with K.at(c, x, y, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8) if i >= lo else 1.0):
            with K.paper(c, k, 0.8):
                K.rr(c, 0, 0, 140, 140, 24, ACC if i % 2 == 0 else K.shade(ACC, 0.18))
            K.text(c, str(i + 1), 0, 4, 70, "black", K.PAPER, k)
        name = HACKS[i]
        lines = [name] if len(name) <= 4 else [name[:3], name[3:]]
        for j, ln in enumerate(lines):
            K.text(c, ln, x, y + 110 + j * 40, 32, "serif_black", K.INK2, k)


# ---------------------------------------------------------------- 12 专家提醒

def reminder(c, g, t, d):
    k = clamp01(g.since(0) / 0.35)
    K.text_card(c, 0, -60, ["这些方法是【帮助】，", "不是治疗。"], 52, 760, K.PAPER, K.INK, K.RED, k, 0,
                0.4 + 0.6 * K.ease_out_back(k, 1.6), K.RED, "serif", 1.0)
    kk = clamp01(g.since(6) / 0.35)
    if kk > 0:
        K.icon(c, "heart", -300, 230, 110, K.RED, kk, 0.6)
        K.text(c, "糖尿病患者调整饮食、用药", 40, 210, 36, "sans_medium", K.INK2, kk)
        K.text(c, "请先问医生", 40, 260, 36, "serif_black", K.INK, kk)


# ---------------------------------------------------------------- 13 七天打卡

def seven_days(c, g, t, d):
    K.card(c, 0, 0, 820, 420, K.PAPER, 1, 26, 1.0, 0, 1, ACC)
    K.text(c, "挑一个方法：________", 0, -130, 40, "serif_black", K.INK)
    for i in range(7):
        x = -330 + i * 110
        K.rr_stroke(c, x, 40, 80, 80, 14, K.INK3, 4)
        K.text(c, "一二三四五六日"[i], x, 120, 28, "sans_medium", K.INK3)
        k = clamp01(g.since(2 + i * 1.5) / 0.3)
        if k > 0:
            K.icon(c, "check", x, 40, 70, K.GREEN, k, 0.4)


def finale(c, g, t, d):
    T.chart(c, 0, 0, 760, 460, [(lambda u: T.bump(u, 0.5, 0.28, 1.8), T.FLAT, clamp01(g.since(0) / 2.0), 9, "")])


def build() -> Episode:
    shots = [
        Shot(3, "早上一片白面包，|光秃秃地吃？", "情境演绎", [
            Custom(bare_bread, x=540, y=760, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "面包出现"), (4, "shaker", 0.7, "面包冷得发抖")],
            note="一片白面包单独出现，第 4 拍冷得发抖"),
        Shot(3, "单吃碳水，|曲线容易冲高。", "书中观点", [
            Custom(bare_spike, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "尖峰曲线画出")], note="面包旁边画出一条单吃碳水的尖峰曲线（示意）"),
        Shot(2, "书里说：|给碳水穿件衣服。", "书中观点", [
            Custom(dress_up, x=540, y=780, at=0, enter="none"),
        ], hits=[(1, "wood_high", 0.7, "衣服落下"), (2, "clap", 0.8, "穿上了")], text_beat=0,
            note="一件小 T 恤从上方落到面包上"),
        Shot(3, "碳水穿衣：搭配蛋白质、|脂肪或膳食纤维。", "书中观点", [
            Big("碳水穿衣", 540, 450, 150, at=0, sfx="kick", sub="put clothes on your carbs", note="概念落版（音乐 drop）"),
            Custom(three_clothes, x=540, y=900, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.7, "蛋白质"), (6, "wood_low", 0.7, "脂肪"), (8, "bongo_high", 0.7, "膳食纤维")],
            note="drop 处“碳水穿衣”砸下；鸡蛋（蛋白质）、坚果（脂肪）、西兰花（膳食纤维）按拍弹出"),
        Shot(3, "面包配鸡蛋，|饼干配坚果。", "书中观点", [
            Custom(pairs, x=540, y=780, at=0, enter="none"),
        ], hits=[(1, "wood_high", 0.7, "面包 + 鸡蛋"), (5, "wood_low", 0.7, "饼干 + 坚果")],
            note="两组搭配：面包 + 鸡蛋，饼干 + 坚果"),
        Shot(3, "米饭，配上|菜和肉。", "书中观点", [
            Custom(rice_plate, x=540, y=800, at=0, enter="pop"),
        ], hits=[(1, "wood_high", 0.7, "米饭"), (3, "wood_low", 0.7, "菜"), (5, "bongo_high", 0.7, "肉")],
            note="一个餐盘：米饭、西兰花、鸡腿按拍放上"),
        Shot(3, "研究发现：搭配之后，|餐后血糖反应更低。", "研究证据", [
            Custom(dressed_curve, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "单吃碳水曲线"), (6, "wood_low", 0.7, "穿上衣服曲线")],
            note="单吃碳水的尖峰曲线与搭配后的平缓曲线（示意）"),
        Shot(2, "降多少，|因食物而异。", "研究证据", [
            Custom(varies, x=540, y=780, at=0, enter="fade"),
        ], hits=[(0, "wood_high", 0.6, "柱子长出")], text_beat=0, note="四根高低不一的柱子（示意：不同搭配降幅不同）"),
        Shot(2, "穿衣服，不是|多浇一大勺油。", "常见误解", [
            Custom(oil, x=540, y=780, at=0, enter="none"),
        ], hits=[(1, "wood_low", 0.7, "油瓶倾斜"), (4, "rim", 0.8, "打叉")], text_beat=0,
            note="油瓶往面包上倒油，第 4 拍打叉"),
        Shot(3, "全书十个方法，|一起回顾。", "书中观点", [
            Custom(tiles, x=540, y=760, at=0, enter="none", lo=0, hi=5),
        ], hits=[(0, "wood_high", 0.6, "方法 1"), (2, "wood_low", 0.6, "方法 3"), (4, "bongo_high", 0.6, "方法 5")],
            note="编号方块 1–5 按拍弹出：进食顺序、先吃蔬菜、别只数热量、咸味早餐、糖都一样"),
        Shot(3, "不用全做到，|挑一两个开始。", "书中观点", [
            Custom(tiles, x=540, y=760, at=0, enter="none", lo=5, hi=10),
        ], hits=[(0, "wood_high", 0.6, "方法 6"), (2, "wood_low", 0.6, "方法 8"), (4, "bongo_high", 0.6, "方法 10")],
            cut=True, note="接着弹出 6–10：甜点放饭后、饭前醋、饭后走动、咸味零食、碳水穿衣"),
        Shot(4, "这些方法是帮助，|不是治疗。", "专家提醒", [
            Custom(reminder, x=540, y=780, at=0, enter="none", sfx="wood_low", note="提醒卡"),
        ], hits=[(6, "rim", 0.7, "糖尿病患者请先问医生")],
            note="提醒卡：这些方法是帮助，不是治疗；糖尿病患者调整饮食、用药请先问医生"),
        Shot(4, "小练习：这周挑一个，|试上七天。", "小练习", [
            Custom(seven_days, x=540, y=780, at=0, enter="pop"),
        ], hits=[(2, "wood_high", 0.6, "周一打勾"), (5, "wood_low", 0.6, "周三打勾"), (8, "bongo_high", 0.6, "周五打勾"),
                 (11, "clap", 0.7, "周日打勾")],
            note="七天打卡卡片，一天一个勾"),
        Shot(2, "吃得稳一点，|日子也稳一点。", "书中观点", [
            Custom(finale, x=540, y=780, at=0, enter="pop", sfx="wood_high", note="平缓曲线"),
        ], text_beat=0, note="一条平缓的血糖曲线（示意）"),
        ending(12, REFS),
    ]
    return Episode(12, "clothes", "碳水穿衣", TITLES[12], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[12]}｜控糖革命12 碳水穿衣", hashtags="#控糖 #血糖 #碳水 #控糖革命 #健康",
                   cover_title="吃碳水，|给它【穿件衣服】", cover_sub="控糖革命 · 碳水穿衣", cover_shot=4, cover_t=5.0,
                   notes=[
                       "“给碳水穿上衣服”是书中第 10 个方法的大意，标“书中观点”。",
                       "研究证据：混合膳食研究显示，给碳水搭配蛋白质、脂肪或膳食纤维，餐后血糖反应降低；但不同蛋白、脂肪种类效果不同，"
                       "纤维在整餐里的效果也不总是保留（事实核查 #15）。第 7、8 镜为示意，不是论文数据。",
                       "“穿衣服不是多浇一大勺油”为通行营养建议：脂肪热量高，搭配应适量。",
                       "第 10、11 镜回顾全书 10 个方法（标签为本系列的简称）。",
                       "本片为科普，不构成医疗建议；糖尿病患者调整饮食与用药请遵医嘱。",
                   ], **SERIES).build()
