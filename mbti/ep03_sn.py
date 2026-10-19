"""03 实感与直觉：看同一幅画，你先注意到什么？"""

import math

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Big, Bubble, Custom, Episode, Fig, Icon, Label, Shot, end_shot

from . import kit_mbti as M

ACC = "#4F8A5B"
GROUND = 1130
SERIES = dict(series="MBTI 科普", file_prefix="MBTI")
REFS = ["Jung, C. G. (1921). Psychologische Typen.（英译 Psychological Types, 1923）",
        "Myers, I. B. & Myers, P. B. (1980). Gifts Differing.（中译《天生不同》）"]

S_COL, N_COL = M.DIM["S"], M.DIM["N"]
PX, PY = 540, 585            # 画框中心（舞台坐标）
PW, PH = 640, 440


def ground(g):
    K.ground(g.c, GROUND)


# ---------------------------------------------------------------- 画框：站台送别

def painting(c, x, y, s=1.0, alpha=1.0):
    """一幅站台小画：两个人、一只箱子、一面钟、远处的火车。(x, y) 为画框中心。"""
    w, h = PW * s, PH * s
    with K.at(c, x, y, 0, s):
        with K.paper(c, alpha, 1.0):
            K.rr(c, 0, 0, PW + 40, PH + 40, 10, "#8A6A48")
            K.rr(c, 0, 0, PW, PH, 4, "#F4E6CF")
        with K.fade(c, alpha):
            K.rr(c, 0, -60, PW, PH - 120, 2, "#E9D6B8")
            K.rr(c, 0, PH / 2 - 60, PW, 120, 2, "#CDB797")
            K.rr(c, 170, 10, 250, 90, 14, K.mix(K.HERO, K.PAPER, 0.35))
            for i in range(4):
                K.rr(c, 85 + i * 58, 0, 34, 30, 4, K.PAPER)
            K.icon(c, "clock", -220, -130, 90, K.INK2, 1, 0.3)
            K.figure(c, -90, PH / 2 - 40, 170, "reach", K.HERO, face=1, mood="calm", lift=0.3, hair="short")
            K.figure(c, 30, PH / 2 - 40, 160, "wave", K.OTHER3, face=-1, mood="calm", lift=0.3, hair="long")
            K.icon(c, "baggage", -190, PH / 2 - 85, 80, K.OTHER, 1, 0.3)
    return w, h


DETAILS = [(-30, 100, "1 · 两个人"), (-190, 135, "2 · 一只箱子"), (-220, -130, "3 · 一面钟")]


def detail_marks(c, g, t, d):
    painting(c, 0, 0)
    for i, (dx, dy, label) in enumerate(DETAILS):
        k = M.appear(g, 2 + 3 * i, 0.3)
        if k <= 0:
            continue
        K.ring(c, dx, dy, 90 if i == 0 else 62, S_COL, 7, k, k)
        K.pill(c, 200, PH / 2 + 100 + i * 75, label, 34, S_COL, K.PAPER, clamp01(k * 3), "sans_medium", "left")


def story_glow(c, g, t, d):
    painting(c, 0, 0)
    k = M.appear(g, 2, 0.6)
    if k > 0:
        K.spotlight(c, -30, 110, 260, K.GOLD, 0.45 * k)
        K.heart(c, -30, -20, 70 * (0.4 + 0.6 * K.ease_out_back(k, 2)), K.RED, k)


# ---------------------------------------------------------------- 4 drop

def two_tiles(c, g, t, d):
    for i, (ch, x) in enumerate((("S", -220), ("N", 220))):
        k = M.appear(g, 4 + 4 * i, 0.3)
        if k > 0:
            M.tile(c, x, 0, 170, ch, None, clamp01(k * 3), 1, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8),
                   M.PAIR_NAMES[ch])


# ---------------------------------------------------------------- 5 知觉功能

def perceive(c, g, t, d):
    K.icon(c, "eye", 0, 0, 240, K.INK, 1, 0.7, 0, 1, 1, ACC)
    for i, (ch, x, label) in enumerate((("S", -330, "感觉"), ("N", 330, "直觉"))):
        k = M.appear(g, 4 + 2 * i, 0.4)
        if k <= 0:
            continue
        M.tile(c, x, -230, 130, ch, None, clamp01(k * 3), 1, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8))
        K.arrow(c, (x * 0.85, -140), (x * 0.4, -40), M.DIM[ch], 9, k, k, 0.1 if i else -0.1, 26)
        K.text(c, label, x, -110 + 40, 38, "serif_black", M.DIM[ch], k)
    q = M.appear(g, 8, 0.4)
    if q > 0:
        K.pill(c, 0, 230, "知觉功能：怎样接收信息", 40, ACC, K.PAPER, q)


# ---------------------------------------------------------------- 6 S：事实与经验

FACTS = ["看得见的", "摸得着的", "做过的"]


def facts(c, g, t, d):
    for i, s in enumerate(FACTS):
        k = M.appear(g, 2 + 2 * i, 0.3)
        if k <= 0:
            continue
        y = -220 + i * 170
        dy = -(1 - ease_out(k)) * 80
        K.text_card(c, -40, y + dy, [s], 52, 460, K.PAPER, K.INK, ACC, clamp01(k * 3), 0, 1, S_COL, "serif", 0.8)
        q = M.appear(g, 3 + 2 * i, 0.25)
        if q > 0:
            K.icon(c, "check", 260, y, 90, K.GREEN, clamp01(q * 3), 0.4, 0, 0.3 + 0.7 * K.ease_out_back(q, 2))


# ---------------------------------------------------------------- 7 N：规律与可能

STARS = [(-300, -150), (-150, -260), (0, -120), (150, -240), (300, -130), (-200, 60), (80, 80), (280, 120)]
LINKS = [(0, 1), (1, 2), (2, 3), (3, 4), (2, 6), (5, 6), (6, 7)]


def constellation(c, g, t, d):
    for i, (a, b) in enumerate(LINKS):
        k = M.appear(g, 2 + i * 0.75, 0.4)
        if k > 0:
            (x0, y0), (x1, y1) = STARS[a], STARS[b]
            K.seg(c, x0, y0, K.lerp(x0, x1, k), K.lerp(y0, y1, k), N_COL, 6, 0.8)
    for i, (x, y) in enumerate(STARS):
        K.star(c, x, y, 26 + 4 * math.sin(g.t * 3 + i), K.GOLD)
    q = M.appear(g, 8, 0.4)
    if q > 0:
        K.icon(c, "bulb", 0, 260, 140, K.INK, clamp01(q * 3), 0.5, 0, 0.3 + 0.7 * K.ease_out_back(q, 2), 1, K.GOLD)


# ---------------------------------------------------------------- 8 树木与森林

def tree(c, x, y, s, color=ACC, alpha=1.0):
    K.rr(c, x, y - s * 0.2, s * 0.12, s * 0.4, 4, "#8A6A48", alpha)
    K.dot(c, x, y - s * 0.55, s * 0.32, color, alpha)
    K.dot(c, x - s * 0.18, y - s * 0.42, s * 0.22, K.shade(color, 0.12), alpha)


def tree_forest(c, g, t, d):
    k = M.appear(g, 1, 0.4)
    if k > 0:
        with K.fade(c, k):
            K.ring(c, -250, -40, 210, S_COL, 8)
            tree(c, -250, 110, 300, S_COL)
            for i in range(3):
                K.dot(c, -300 + i * 50, -150 + (i % 2) * 40, 10, K.GOLD)
    q = M.appear(g, 4, 0.4)
    if q > 0:
        with K.fade(c, q):
            for i in range(9):
                tx = 120 + (i % 3) * 110 + (i // 3) * 30
                ty = -60 + (i // 3) * 90
                tree(c, tx, ty, 120, N_COL)


# ---------------------------------------------------------------- 9 两条路收集信息

def two_inputs(c, g, t, d):
    K.icon(c, "puzzle", 0, 120, 200, ACC, 1, 0.6)
    for i, ch in enumerate("SN"):
        k = M.appear(g, 1 + 3 * i, 0.35)
        if k <= 0:
            continue
        x = (-1 if i == 0 else 1) * 300
        M.tile(c, x, -180, 130, ch, None, clamp01(k * 3), 1, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8))
        K.arrow(c, (x * 0.9, -100), (x * 0.3, 40), M.DIM[ch], 10, k, k, 0.15 if i else -0.15, 28)


# ---------------------------------------------------------------- 10 N 不更聪明

def podium(c, g, t, d):
    K.rr(c, 0, 120, 300, 200, 12, K.mix(K.GOLD, K.PAPER, 0.4))
    K.text(c, "1", 0, 120, 110, "black", K.PAPER)
    M.tile(c, 0, -60, 150, "N")
    k = M.appear(g, 2, 0.3)
    if k > 0:
        K.icon(c, "crown", 0, -190, 120, K.GOLD, clamp01(k * 3), 0.5)
    q = M.appear(g, 6, 0.3)
    if q > 0:
        K.icon(c, "cross", 0, 0, 380, K.RED, clamp01(q * 3) * 0.9, 0.3, 0, 0.3 + 0.7 * K.ease_out_back(q, 2))


# ---------------------------------------------------------------- 11 S 也有想象力

def model_house(c, g, t, d):
    for i in range(4):
        k = M.appear(g, 1 + i, 0.3)
        if k <= 0:
            continue
        y = 120 - i * 70 - (1 - ease_out(k)) * 120
        K.rr(c, 0, y, 260 - i * 40, 66, 8, (S_COL, K.GOLD, K.OTHER3, N_COL)[i], clamp01(k * 3))
    q = M.appear(g, 5, 0.3)
    if q > 0:
        K.poly(c, [(-110, -150), (0, -260), (110, -150)], K.RED, clamp01(q * 3))


# ---------------------------------------------------------------- 12 偏好不是能力

def sn_scale(c, g, t, d):
    k = M.appear(g, 0, 0.4)
    pos = -0.6
    for p, b in ((0.5, 4), (-0.2, 8)):
        if g.since(b) >= 0:
            pos = K.lerp(pos, p, K.ease_in_out(clamp01(g.since(b) / 0.45)))
    M.scale_bar(c, 0, 0, 860, "S", "N", pos, k, None, 100)
    for i, (x, name, b) in enumerate(((-345, "eye", 2), (345, "bulb", 6))):
        q = M.appear(g, b, 0.3)
        if q > 0:
            K.icon(c, name, x, -200, 110, K.INK, clamp01(q * 3), 0.5, 0, 0.3 + 0.7 * K.ease_out_back(q, 2), 1, K.GOLD)


# ---------------------------------------------------------------- 13 小练习：早餐

def breakfast(c, g, t, d):
    k = M.appear(g, 0, 0.35)
    with K.fade(c, k):
        K.dot(c, 0, -230, 120, K.PAPER)
        K.ring(c, 0, -230, 120, K.LINE, 6)
        K.rr(c, -30, -240, 110, 80, 18, "#E2B77A")
        K.rr(c, -10, -220, 110, 80, 18, "#EDC891")
        K.rr(c, 170, -230, 60, 110, 10, K.PAPER)
        K.rr_stroke(c, 170, -230, 60, 110, 10, K.INK3, 5)


def build() -> Episode:
    shots = [
        # 1
        Shot(3, "同一幅画，|两个人一起看。", "情境演绎", [
            Custom(lambda c, g, t, d: painting(c, 0, 0), x=PX, y=PY, at=0, enter="pop", sfx="wood_low",
                   note="一幅站台小画出现"),
            Fig(300, GROUND, 290, at=2, color=S_COL, hair="short", mood="calm", sfx="wood_high", note="左边的人走来",
                moves=[(8, dict(pose="think", note="左边的人凑近细看"))]),
            Fig(780, GROUND, 290, at=4, color=N_COL, hair="long", mood="calm", face=-1, sfx="bongo_high",
                note="右边的人走来", moves=[(10, dict(look=0.6, mood="open", sfx="shaker", note="右边的人出神"))]),
        ], draw=ground, note="墙上挂着一幅站台小画：两个人、一只箱子、一面钟；两个人一左一右走来看画"),
        # 2
        Shot(3, "一个说：两个人、|一只箱子、一面钟。", "情境演绎", [
            Custom(detail_marks, x=PX, y=PY, at=0, enter="none"),
            Fig(300, GROUND, 290, at=0, enter="none", color=S_COL, hair="short", mood="open", pose="point"),
        ], draw=ground, hits=[(2, "wood_high", 0.8, "圈出两个人"), (5, "wood_low", 0.8, "圈出箱子"),
                              (8, "bongo_high", 0.8, "圈出钟")],
            note="左边的人指着画，细节按拍被一个个圈出并编号"),
        # 3
        Shot(2, "另一个说：|“像是在告别。”", "情境演绎", [
            Custom(story_glow, x=PX, y=PY, at=0, enter="none"),
            Fig(780, GROUND, 290, at=0, enter="none", color=N_COL, hair="long", mood="sad", face=-1),
            Bubble("像是在告别……", 480, 980, 42, at=2, tail=(1, 0.2), sfx="bongo_low", note="右边的人：像是在告别"),
        ], draw=ground, hits=[(2, "shaker", 0.6, "画中光晕亮起")],
            note="右边的人轻声说“像是在告别”，画中两人周围亮起暖光和一颗心"),
        # 4  drop
        Shot(3, "S/N 问的是：|你先接收哪种信息？", "机制示意", [
            Big("实感与直觉", 540, 470, 140, at=0, sfx="kick", sub="Sensing · Intuition", note="概念落版（音乐 drop）"),
            Custom(two_tiles, x=540, y=880, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.8, "S 牌落位"), (8, "wood_low", 0.8, "N 牌落位")],
            note="drop 处概念砸下；S、N 两张牌按拍落位"),
        # 5
        Shot(3, "荣格把感觉和直觉，|都叫作“知觉功能”。", "荣格原著", [
            Custom(perceive, x=540, y=830, at=0, enter="pop", sfx="wood_low", note="一只大眼睛"),
        ], hits=[(4, "wood_high", 0.8, "“感觉”流入"), (6, "bongo_high", 0.8, "“直觉”流入"),
                 (8, "rim", 0.8, "知觉功能：怎样接收信息")],
            note="中间一只大眼睛，“感觉”“直觉”两路箭头按拍流入，底部落下“知觉功能”"),
        # 6
        Shot(3, "S 更相信具体的事实|和亲身的经验。", "机制示意", [
            Custom(facts, x=540, y=820, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "“看得见的”"), (3, "shaker", 0.6, "打勾"), (4, "wood_low", 0.7, "“摸得着的”"),
                 (5, "shaker", 0.6, "打勾"), (6, "bongo_high", 0.7, "“做过的”"), (7, "clap", 0.7, "打勾")],
            note="三张卡片“看得见的、摸得着的、做过的”按拍落下并打勾"),
        # 7
        Shot(3, "N 更爱看规律、|联系和可能性。", "机制示意", [
            Custom(constellation, x=540, y=820, at=0, enter="fade"),
        ], hits=[(2, "wood_high", 0.6, "第一条连线"), (5, "wood_low", 0.6, "连线成形"), (8, "bongo_high", 0.8, "灯泡亮起")],
            note="散落的星星被一条条连成星座，最后亮起灯泡"),
        # 8
        Shot(2, "一个先看树木，|一个先看森林。", "机制示意", [
            Custom(tree_forest, x=540, y=820, at=0, enter="none"),
        ], hits=[(1, "wood_high", 0.8, "放大镜里的一棵树"), (4, "wood_low", 0.8, "一片森林")], text_beat=0,
            note="左边放大圈里一棵树的细节，右边一整片森林"),
        # 9
        Shot(2, "两种方式，|都在收集信息。", "机制示意", [
            Custom(two_inputs, x=540, y=820, at=0, enter="pop"),
        ], hits=[(1, "wood_high", 0.8, "S 一路"), (4, "wood_low", 0.8, "N 一路")], text_beat=0,
            note="S、N 两路箭头汇向同一块拼图"),
        # 10
        Shot(3, "直觉型不等于|更聪明。", "常见误解", [
            Custom(podium, x=540, y=820, at=0, enter="pop", sfx="wood_low", note="N 站上领奖台"),
        ], hits=[(2, "bongo_high", 0.8, "戴上皇冠"), (6, "rim", 0.9, "大叉划掉")],
            note="N 牌站上第一名领奖台戴上皇冠，第 6 拍被一个大叉划掉"),
        # 11
        Shot(3, "实感型也不等于|没有想象力。", "常见误解", [
            Fig(300, GROUND, 290, at=0, color=S_COL, hair="short", mood="calm",
                moves=[(1, dict(pose="carry", sfx="wood_high", note="一块块搭起积木")),
                       (6, dict(pose="cheer", mood="happy", sfx="clap", note="搭出一座小房子"))]),
            Custom(model_house, x=700, y=900, at=0, enter="none"),
            Icon("bulb", 330, 600, 110, at=6, enter="pop"),
        ], draw=ground, hits=[(3, "wood_low", 0.6, "第三块"), (5, "bongo_high", 0.7, "屋顶盖上")],
            note="S 型的人一块块搭积木，盖上屋顶后举手欢呼，头顶亮起灯泡"),
        # 12
        Shot(4, "偏好说的是先注意什么，|不是能做到什么。", "常见误解", [
            Custom(sn_scale, x=540, y=820, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "眼睛：细节"), (4, "wood_low", 0.7, "滑块滑向 N"), (6, "bongo_high", 0.7, "灯泡：可能"),
                 (8, "wood_low", 0.7, "滑块回到中间偏 S")],
            note="S—N 量尺两端分别亮起眼睛与灯泡，滑块来回滑动"),
        # 13
        Shot(4, "描述一下你的早餐：|你先说了什么？", "小练习", [
            Custom(breakfast, x=540, y=800, at=0, enter="pop", sfx="wood_low", note="一盘早餐"),
            Bubble("两片面包，一杯牛奶", 540, 830, 42, at=4, sfx="wood_high", note="一种说法：列出吃了什么"),
            Label("S", 190, 830, 40, at=4, fill=S_COL),
            Bubble("起晚了，随便对付了一口", 540, 1030, 42, at=8, sfx="bongo_high", note="另一种说法：讲早上的情形"),
            Label("N", 190, 1030, 40, at=8, fill=N_COL),
            Icon("question", 870, 560, 100, color=ACC, at=12, enter="pop", sfx="rim", note="问号：你呢？"),
        ], note="一盘早餐，两种描述按拍浮现，最后弹出问号"),
        # 14
        Shot(2, "细节和可能都看见，|画面才完整。", "机制示意", [
            Custom(lambda c, g, t, d: painting(c, 0, 0), x=PX, y=PY, at=0, enter="pop"),
            Label("细节", 130, 960, 38, at=1, fill=S_COL, sfx="wood_high", note="“细节”标签"),
            Label("可能", 950, 960, 38, at=3, fill=N_COL, sfx="wood_low", note="“可能”标签"),
            Fig(300, GROUND, 300, at=0, color=S_COL, hair="short", mood="happy", face=1, pose="wave"),
            Fig(780, GROUND, 300, at=0, color=N_COL, hair="long", mood="happy", face=-1,
                moves=[(5, dict(pose="wave", sfx="clap", note="两人相视挥手"))]),
        ], draw=ground, note="同一幅画下，“细节”“可能”两个标签亮起，两人相视挥手"),
        end_shot(REFS, "04 T/F：讲道理的人，就没有感情吗？"),
    ]
    return Episode(3, "sn", "实感与直觉", "看同一幅画，你先注意到什么？", ACC, shots, refs=REFS,
                   publish_title="看同一幅画，你先注意到什么？｜MBTI科普03 实感与直觉",
                   hashtags="#MBTI #心理学 #实感 #直觉 #荣格",
                   cover_title="看同一幅画，|你先注意到【什么】？", cover_sub="MBTI 的 S 与 N", cover_shot=1, cover_t=6.0,
                   notes=[
                       "第 5 镜：荣格把感觉与直觉归为“非理性功能”，MBTI 称为知觉功能（perceiving functions），与思维、情感两种判断功能相对。",
                       "S 关注具体事实与经验、N 关注模式与可能性，是 MBTI 对两种偏好的通行描述；片中第 6–9 镜为示意。",
                       "第 13 镜两种早餐描述只是帮助觉察偏好的示意，不能据此判定类型。",
                       "MBTI、Myers-Briggs Type Indicator 是 The Myers-Briggs Company 的注册商标。",
                   ], **SERIES).build()
