"""02 血糖尖峰：血糖尖峰，真的那么可怕吗？"""

import math

from engine.gfx import clamp01

from adler import kit as K
from adler.core import Big, Bubble, Custom, Episode, Fig, Icon, Shot

from . import kit_tang as T
from .common import GROUND, SERIES, TITLES, ending, ground, refs

ACC = "#D9593A"
REFS = refs("JAMA 观点文章（2021）；营养师致 Channel 4 公开信（2025）")


def spike_fn(u):
    return T.bump(u, 1.0, 0.2, 2.6, 0.2)


def gentle_fn(u):
    return T.bump(u, 0.42, 0.3, 1.7)


# ---------------------------------------------------------------- 1 两条曲线

def hook_curves(c, g, t, d):
    p1 = clamp01(g.since(1) / max(0.1, g.b(6) - g.b(1)))
    p2 = clamp01(g.since(6) / max(0.1, g.b(11) - g.b(6)))
    T.chart(c, 0, 0, 820, 520, [(spike_fn, T.SPIKE, p1, 9, "尖峰"), (gentle_fn, T.FLAT, p2, 9, "平稳")])


# ---------------------------------------------------------------- 4 drop

def drop_curve(c, g, t, d):
    p = clamp01(g.since(0) / max(0.1, g.b(6)))
    T.chart(c, 0, 0, 780, 480, [(spike_fn, T.SPIKE, p, 10, "")])
    k = clamp01(g.since(6) / 0.3)
    if k > 0:
        x = -390 + 0.2 * 780
        y = 240 - (0.22 + 0.78 * 0.92) * 480
        K.ring(c, x, y, 50 + 10 * (1 - k), K.RED, 7, k)


# ---------------------------------------------------------------- 5 葡萄糖涌入

def flood(c, g, t, d):
    T.vessel(c, 0, -60, 900, 230)
    n = 6 + int(14 * clamp01(g.since(2) / 2.0))
    T.particles(c, -440, -60, 440, -60, g.t, n, 18, T.GLU, 1, 0.35, 3, 40)
    K.text(c, "血液里的葡萄糖", -400, -210, 30, "sans_medium", K.INK2, 1, "left")
    k = clamp01(g.since(6) / 0.4)
    if k > 0:
        K.pill(c, 0, 170, "一下子涌进来很多", 36, T.SPIKE, K.PAPER, k)


# ---------------------------------------------------------------- 6 胰岛素与储存

def store(c, g, t, d):
    for i in range(5):
        k = clamp01(g.since(1 + 0.5 * i) / 0.3)
        if k > 0:
            K.icon(c, "key", -330 + i * 60, -230 + 20 * math.sin(g.t * 3 + i), 80, K.GOLD, k, 0.6, -20)
    K.text(c, "胰岛素大量分泌", -210, -130, 32, "serif_black", K.GOLD, clamp01(g.since(1) / 0.3))
    k1 = clamp01(g.since(5) / 0.35)
    k2 = clamp01(g.since(8) / 0.35)
    for x, label, col, k in ((-200, "糖原", "#C98A2B", k1), (220, "脂肪", "#E8C66A", k2)):
        if k <= 0:
            continue
        with K.at(c, x, 130, 0, 0.4 + 0.6 * K.ease_out_back(k, 1.6)):
            with K.paper(c, k, 0.8):
                K.rr(c, 0, 0, 280, 200, 30, K.tint(col, 0.4))
            for j in range(6):
                T.hexa(c, -80 + (j % 3) * 80, -30 + (j // 3) * 60, 22, T.GLU, k)
            K.text(c, label, 0, 140, 36, "serif_black", K.shade(col, 0.2), k)
    if k1 > 0:
        K.arrow(c, (-120, -100), (-180, 20), K.INK3, 7, k1, k1, 0, 22)
    if k2 > 0:
        K.arrow(c, (40, -100), (180, 20), K.INK3, 7, k2, k2, 0, 22)


# ---------------------------------------------------------------- 7 回落低于起点

def dip_curve(c, g, t, d):
    p = clamp01(g.since(0) / max(0.1, g.b(8)))
    T.chart(c, 0, 0, 820, 520, [(spike_fn, T.SPIKE, p, 9, "")])
    k = clamp01(g.since(8) / 0.35)
    if k > 0:
        x0, y0, h = -410, 260, 520
        yb = y0 - 0.22 * h
        K.seg(c, x0, yb, x0 + 820 * k, yb, K.INK3, 3)
        K.text(c, "起点", x0 + 12, yb + 28, 26, "sans_medium", K.INK3, k, "left")
        tm = 0.2 * 2.6
        vm = 0.22 + 0.78 * 0.92 * spike_fn(tm)
        K.ring(c, x0 + tm * 820, y0 - vm * h, 40, K.RED, 6, k)
        K.text(c, "低于起点", x0 + tm * 820, y0 - vm * h + 70, 30, "serif_black", K.RED, k)


# ---------------------------------------------------------------- 8–9 回落时的感受

def feelings(c, g, t, d):
    items = [("困", K.OTHER2), ("饿", T.SPIKE), ("想吃甜", "#D96A9A")]
    for i, (s, col) in enumerate(items):
        k = clamp01(g.since(d["b0"] + i) / 0.3)
        if k <= 0:
            continue
        w = K.text_w(s, 46, "serif_black") + 60
        with K.at(c, -260 + i * 260, 0, -4 + 4 * i, 0.3 + 0.7 * K.ease_out_back(k, 1.8)):
            with K.paper(c, k, 0.8):
                K.rr(c, 0, 0, w, 90, 45, col)
            K.text(c, s, 0, 2, 46, "serif_black", K.PAPER, k)


# ---------------------------------------------------------------- 10–11 专家提醒

def normal_band(c, g, t, d):
    T.chart(c, 0, 0, 820, 520, [(gentle_fn, T.FLAT, clamp01(g.since(1) / 1.6), 9, "正常起伏")], 1, (0.0, 0.62))
    k = clamp01(g.since(7) / 0.35)
    if k > 0:
        K.pill(c, 0, 330, "健康人饭后升高，是正常的", 34, T.FLAT, K.PAPER, k)


def debate(c, g, t, d):
    """左：书的观点；右：营养学界的批评；中间一个天平。"""
    K.icon(c, "scale", 0, 40, 260, K.INK2, 1, 0.8, 4 * math.sin(g.t * 1.5))
    k1 = clamp01(g.since(1) / 0.35)
    k2 = clamp01(g.since(5) / 0.35)
    if k1 > 0:
        K.text_card(c, -230, -230, ["书：尖峰", "值得留意"], 38, 360, K.PAPER, K.INK, ACC, k1, -3,
                    0.4 + 0.6 * K.ease_out_back(k1, 1.6), ACC, "serif", 0.8)
    if k2 > 0:
        K.text_card(c, 230, -230, ["批评：对健康人", "证据还不够"], 38, 380, K.PAPER, K.INK, K.HERO, k2, 3,
                    0.4 + 0.6 * K.ease_out_back(k2, 1.6), K.HERO, "serif", 0.8)


def who_cares(c, g, t, d):
    """三张卡：健康人 / 糖尿病前期 / 糖尿病，后两张亮起“重点关注”。"""
    labels = [("健康人", K.FLAT if hasattr(K, "FLAT") else T.FLAT, False), ("糖尿病前期", ACC, True),
              ("糖尿病", K.shade(ACC, 0.25), True)]
    for i, (s, col, hot) in enumerate(labels):
        k = clamp01(g.since(i) / 0.3)
        if k <= 0:
            continue
        x = -300 + i * 300
        K.figure(c, x, 140, 260, "stand", col, mood="calm", alpha=k, hair=("short", "bun", None)[i])
        K.text(c, s, x, 210, 34, "serif_black", col, k)
        kh = clamp01(g.since(5 + i) / 0.3)
        if hot and kh > 0:
            K.pill(c, x, -220, "重点关注", 30, ACC, K.PAPER, kh)


# ---------------------------------------------------------------- 13 小练习

def habit(c, g, t, d):
    """一周七天的小格子：偶尔一个红点不要紧，看整体颜色。"""
    days = "一二三四五六日"
    cols = [T.FLAT, T.FLAT, T.SPIKE, T.FLAT, T.FLAT, T.FLAT, T.FLAT]
    K.card(c, 0, 0, 860, 380, K.PAPER, 1, 26, 1.0, 0, 1, ACC)
    K.text(c, "看一周，不看一顿", 0, -120, 40, "serif_black", K.INK)
    for i in range(7):
        k = clamp01(g.since(1 + i) / 0.3)
        x = -330 + i * 110
        K.text(c, days[i], x, 110, 28, "sans_medium", K.INK3)
        K.rr_stroke(c, x, 30, 80, 80, 14, K.LINE, 4)
        if k > 0:
            K.rr(c, x, 30, 70 * k, 70 * k, 12, cols[i])


def build() -> Episode:
    shots = [
        Shot(3, "同一碗饭，|有人曲线像过山车。", "情境演绎", [
            Custom(hook_curves, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "尖峰曲线开始画"), (6, "wood_low", 0.6, "平稳曲线开始画")],
            note="同一张图上先画出一条高高的尖峰曲线，再画一条平稳曲线（示意）"),
        Shot(3, "饭后一下子冲高，|又一下子掉下来。", "情境演绎", [
            Fig(300, GROUND, 360, at=0, mood="happy", hair="short",
                moves=[(4, dict(pose="cheer", sfx="wood_high", note="冲高：主角很兴奋")),
                       (8, dict(pose="sad", mood="flat", sfx="tom", note="掉下来：主角蔫了"))]),
            Custom(lambda c, g, t, d: T.chart(c, 0, 0, 260, 200, [(spike_fn, T.SPIKE, clamp01(g.since(2) / 3.0), 6, "")],
                                              1, None, "", "", False, False), x=740, y=700, at=1, enter="pop"),
        ], draw=ground, note="主角跟着曲线起伏：冲高时兴奋举手，第 8 拍蔫下来"),
        Shot(2, "这就是书里说的……", "书中观点", [
            Icon("book", 540, 760, 360, color=ACC, at=0, enter="pop", sfx="wood_low", note="书出现"),
        ], text_beat=0, note="一本书弹出"),
        Shot(3, "尖峰：短时间里|血糖冲得又高又快。", "机制示意", [
            Big("血糖尖峰", 540, 450, 140, at=0, sfx="kick", sub="glucose spike", note="概念落版（音乐 drop）"),
            Custom(drop_curve, x=540, y=930, at=0, enter="fade"),
        ], hits=[(6, "rim", 0.8, "红圈圈出尖峰")],
            note="drop 处“血糖尖峰”砸下；一条陡峭的尖峰曲线画出，第 6 拍红圈圈出峰顶（示意）"),
        Shot(3, "大量葡萄糖|一下子涌进血液，", "机制示意", [
            Custom(flood, x=540, y=780, at=0, enter="fade"),
        ], hits=[(2, "shaker", 0.7, "葡萄糖越来越多"), (6, "wood_high", 0.7, "“一下子涌进来很多”")],
            note="血管里的葡萄糖颗粒越来越多，挤满血管"),
        Shot(3, "胰岛素大量分泌，多余的|变成糖原和脂肪存起来。", "机制示意", [
            Custom(store, x=540, y=780, at=0, enter="none"),
        ], hits=[(1, "wood_high", 0.7, "胰岛素钥匙一把把出现"), (5, "bongo_low", 0.8, "存进糖原"),
                 (8, "bongo_high", 0.8, "存进脂肪")],
            note="一把把胰岛素钥匙出现；葡萄糖分别装进“糖原”和“脂肪”两个仓库"),
        Shot(3, "书里说：回落时，|有时会掉到起点以下。", "书中观点", [
            Custom(dip_curve, x=540, y=780, at=0, enter="fade"),
        ], hits=[(8, "rim", 0.8, "红圈圈出低谷")],
            note="尖峰曲线回落到起点线以下，红圈标“低于起点”（示意）"),
        Shot(2, "这时人可能|犯困、发饿，", "书中观点", [
            Custom(feelings, x=540, y=760, at=0, enter="none", b0=1),
        ], hits=[(1, "wood_high", 0.7, "困"), (2, "wood_low", 0.7, "饿")], text_beat=0,
            note="标签“困”“饿”按拍弹出"),
        Shot(2, "还特别想吃甜的。", "书中观点", [
            Custom(feelings, x=540, y=760, at=0, enter="none", b0=-2),
            Bubble("来块蛋糕？", 540, 1040, 40, at=1, sfx="bongo_high", note="想吃甜的"),
        ], text_beat=0, cut=True, note="第三个标签“想吃甜”弹出，下面冒出“来块蛋糕？”"),
        Shot(3, "但要说清楚：健康人|饭后血糖升高是正常的。", "专家提醒", [
            Custom(normal_band, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "正常曲线画出"), (7, "wood_high", 0.7, "“正常”标签")],
            note="浅绿色正常范围里一条平缓的曲线；标签“健康人饭后升高，是正常的”"),
        Shot(3, "“每次尖峰都有害”，|对健康人证据还不够。", "专家提醒", [
            Custom(debate, x=540, y=820, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.7, "书的观点卡"), (5, "wood_low", 0.7, "批评卡")],
            note="天平两边：书的观点“尖峰值得留意”，营养学界的批评“对健康人证据还不够”"),
        Shot(4, "真正要重点关注的，|是糖尿病和糖尿病前期。", "专家提醒", [
            Custom(who_cares, x=540, y=880, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "健康人"), (1, "wood_high", 0.6, "糖尿病前期"), (2, "bongo_high", 0.6, "糖尿病"),
                 (5, "rim", 0.8, "“重点关注”标签")],
            note="三个人：健康人、糖尿病前期、糖尿病；后两人头顶亮起“重点关注”"),
        Shot(4, "小练习：别为一次尖峰焦虑，|看长期的饮食习惯。", "小练习", [
            Custom(habit, x=540, y=800, at=0, enter="pop"),
        ], hits=[(1, "wood_high", 0.6, "周一"), (3, "rim", 0.7, "周三一个红格"), (7, "wood_low", 0.6, "周日")],
            note="一周七格按拍填色：偶尔一格红色，整体是绿色"),
        Shot(2, "接下来，|看看书里的第一个方法。", "书中观点", [
            Custom(lambda c, g, t, d: T.step_order(c, 0, 0, [("broccoli", ""), ("drumstick", ""), ("rice", "")],
                                                   [clamp01(g.since(i) / 0.3) for i in range(3)], 140, 260),
                   x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.6, "蔬菜"), (1, "wood_low", 0.6, "肉"), (2, "bongo_high", 0.6, "米饭")],
            text_beat=0, note="蔬菜、鸡腿、米饭按 1、2、3 排开，预告下一期"),
        ending(2, REFS),
    ]
    return Episode(2, "spike", "血糖尖峰", TITLES[2], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[2]}｜控糖革命02 血糖尖峰", hashtags="#控糖 #血糖 #控糖革命 #健康 #科普",
                   cover_title="血糖尖峰，|真的那么【可怕】吗？", cover_sub="控糖革命 · 血糖尖峰",
                   cover_shot=3, cover_t=5.0,
                   notes=[
                       "第 1、2、4、7、10 镜曲线为示意，不是实测数据。",
                       "大量葡萄糖进入血液后胰岛素分泌增加，多余葡萄糖以糖原和脂肪形式储存，为通行生理学。",
                       "“回落低于起点”“犯困、饥饿、想吃甜”是书中观点，并非每个人都会出现，这些感受也有很多其他原因。",
                       "健康人饭后血糖升高是正常的；对健康人而言“每一次尖峰都有害”证据不足，营养学界有批评"
                       "（营养师致 Channel 4 公开信；JAMA 2021 观点文章）。糖尿病与糖尿病前期是确定需要关注的情况（ADA）。",
                   ], **SERIES).build()
