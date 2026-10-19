"""04 思考与情感：讲道理的人，就没有感情吗？"""

import math

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Icon, Shot, end_shot

from . import kit_mbti as M

ACC = "#B84D66"
GROUND = 1130
SERIES = dict(series="MBTI 科普", file_prefix="MBTI")
REFS = ["Jung, C. G. (1921). Psychologische Typen.（英译 Psychological Types, 1923）",
        "Myers, I. B. & Myers, P. B. (1980). Gifts Differing.（中译《天生不同》）"]

T_COL, F_COL = M.DIM["T"], M.DIM["F"]


def ground(g):
    K.ground(g.c, GROUND)


# ---------------------------------------------------------------- 通用：天平

def balance(c, g, tilt, s=1.0, left="T", right="F", alpha=1.0, tiles=True):
    """天平：tilt ∈ [-1, 1]（正值右侧下沉）；两个秤盘上放字母牌。原点为支点。"""
    ang = math.radians(tilt * 14)
    arm = 300 * s
    with K.fade(c, alpha):
        K.rr(c, 0, 380 * s, 260 * s, 30 * s, 10, K.INK2)
        K.seg(c, 0, 380 * s, 0, 0, K.INK2, 16 * s)
        for sgn, ch in ((-1, left), (1, right)):
            ex, ey = sgn * arm * math.cos(ang), sgn * arm * math.sin(ang)
            K.seg(c, ex, ey, ex - 70 * s, ey + 150 * s, K.INK3, 4 * s)
            K.seg(c, ex, ey, ex + 70 * s, ey + 150 * s, K.INK3, 4 * s)
            K.rr(c, ex, ey + 155 * s, 200 * s, 22 * s, 10, K.shade(M.DIM.get(ch, K.GOLD), 0.15))
            if tiles:
                M.tile(c, ex, ey + 85 * s, 110 * s, ch)
        K.seg(c, -arm * math.cos(ang), -arm * math.sin(ang), arm * math.cos(ang), arm * math.sin(ang), K.INK2, 14 * s)
        K.dot(c, 0, 0, 20 * s, K.GOLD)


# ---------------------------------------------------------------- 1 朋友哭了

def tears(c, g, t, d):
    """两行泪珠循环落下。"""
    for i in range(4):
        ph = (g.t * 1.4 + i * 0.25) % 1.0
        for sgn in (-1, 1):
            K.dot(c, sgn * 28, ph * 110, 9 * (1 - ph * 0.4), "#8DBAD3", 1 - ph)


# ---------------------------------------------------------------- 2 列出方案

def plan_card(c, g, t, d):
    items = ["1. 先冷静几天", "2. 别再翻聊天记录", "3. 多出去走走"]
    for i, s in enumerate(items):
        k = M.appear(g, 3 + 2 * i, 0.3)
        if k > 0:
            K.text_card(c, 0, -110 + i * 105, [s], 38, 440, K.PAPER, K.INK, ACC, clamp01(k * 3), 0, 1,
                        T_COL if i == 0 else None, "sans_medium", 0.7)


# ---------------------------------------------------------------- 3 纸巾

def tissue(c, g, t, d):
    c.scale(0.7, 0.7)
    with K.paper(c, 1, 0.8):
        K.rr(c, 0, 0, 150, 90, 12, K.mix(F_COL, K.PAPER, 0.35))
    K.rr(c, 0, -45, 70, 14, 7, K.shade(F_COL, 0.3))
    k = M.appear(g, 3, 0.4)
    if k > 0:
        path_y = -45 - 70 * ease_out(k)
        K.poly(c, [(-30, -45), (30, -45), (40, path_y), (-25, path_y - 12)], K.PAPER, 1)


# ---------------------------------------------------------------- 4 drop

def two_tiles(c, g, t, d):
    for i, (ch, x) in enumerate((("T", -220), ("F", 220))):
        k = M.appear(g, 4 + 4 * i, 0.3)
        if k > 0:
            M.tile(c, x, 0, 170, ch, None, clamp01(k * 3), 1, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8),
                   M.PAIR_NAMES[ch])


# ---------------------------------------------------------------- 5 判断功能

def judge_scale(c, g, t, d):
    k = M.appear(g, 4, 0.4)
    tilt = 0.6 * math.sin(g.t * 1.6) * (1 - ease_out(k))
    balance(c, g, tilt, 0.9, alpha=1)
    q = M.appear(g, 8, 0.4)
    if q > 0:
        K.pill(c, 0, -130, "判断功能：怎样做决定", 40, ACC, K.PAPER, q)


# ---------------------------------------------------------------- 6 T：逻辑

def logic_chain(c, g, t, d):
    labels = ["事实", "推理", "结论"]
    for i, s in enumerate(labels):
        k = M.appear(g, 2 + 2 * i, 0.3)
        if k <= 0:
            continue
        x = -300 + i * 300
        K.text_card(c, x, -60, [s], 52, 200, K.PAPER, K.INK, ACC, clamp01(k * 3), 0,
                    0.3 + 0.7 * K.ease_out_back(k, 1.8), T_COL, "serif", 0.8)
        if i:
            K.arrow(c, (x - 200, -60), (x - 110, -60), T_COL, 9, k, k, 0, 24)
    q = M.appear(g, 8, 0.3)
    if q > 0:
        K.icon(c, "check", 0, 170, 150, K.GREEN, clamp01(q * 3), 0.5, 0, 0.3 + 0.7 * K.ease_out_back(q, 2))


# ---------------------------------------------------------------- 7 F：人与价值

def people_hearts(c, g, t, d):
    pos = [(-280, 80), (0, -60), (280, 80)]
    cols = (K.OTHER, F_COL, K.OTHER3)
    for i, (x, y) in enumerate(pos):
        K.figure(c, x, y + 170, 200, "stand", cols[i], face=1 if x < 0 else -1, mood="smile", lift=0.6,
                 hair=("bun", "long", "short")[i])
    for i, (a, b) in enumerate(((0, 1), (1, 2), (0, 2))):
        k = M.appear(g, 2 + 2 * i, 0.4)
        if k <= 0:
            continue
        (x0, y0), (x1, y1) = pos[a], pos[b]
        K.arrow(c, (x0, y0 - 20), (x1, y1 - 20), F_COL, 6, k, k, 0.25, 0, (14, 12))
        K.heart(c, (x0 + x1) / 2, (y0 + y1) / 2 - 130 - (40 if i == 2 else 0), 60 * K.ease_out_back(k, 2), F_COL, k)


# ---------------------------------------------------------------- 8 都是理性的判断

def level_scale(c, g, t, d):
    k = g.span(0, 3)
    tilt = 0.8 * (1 - k) * math.cos(g.t * 3)
    balance(c, g, tilt, 0.85)


# ---------------------------------------------------------------- 9 依据不同

def basis(c, g, t, d):
    for i, (ch, label, name) in enumerate((("T", "逻辑", "check"), ("F", "价值", "heart"))):
        k = M.appear(g, 1 + 3 * i, 0.35)
        if k <= 0:
            continue
        x = (-1 if i == 0 else 1) * 230
        M.tile(c, x, -100, 160, ch, None, clamp01(k * 3), 1, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8))
        K.pill(c, x, 60, label, 42, M.DIM[ch], K.PAPER, k)
        K.icon(c, name, x, 200, 100, M.DIM[ch], k, 0.4)


# ---------------------------------------------------------------- 10 F 不是情绪化

def storm(c, g, t, d):
    K.icon(c, "cloud", 0, 0, 220, K.INK3, 1, 0.5)
    for i in range(3):
        ph = (g.t * 1.6 + i / 3) % 1
        K.seg(c, -60 + i * 60, 60 + ph * 60, -70 + i * 60, 80 + ph * 60, "#8DBAD3", 5, 1 - ph)
    k = M.appear(g, 6, 0.3)
    if k > 0:
        K.icon(c, "cross", 0, 0, 280, K.RED, clamp01(k * 3) * 0.9, 0.3, 0, 0.3 + 0.7 * K.ease_out_back(k, 2))


# ---------------------------------------------------------------- 11 T 不是冷漠

def warm_heart(c, g, t, d):
    k = M.appear(g, 4, 0.4)
    if k > 0:
        K.spotlight(c, 0, 0, 160, K.GOLD, 0.5 * k)
        K.heart(c, 0, 0, 90 * (0.3 + 0.7 * K.ease_out_back(k, 2)) * M.pulse(g, (8,), 0.2), K.RED, k)


# ---------------------------------------------------------------- 12 两样都看

def both(c, g, t, d):
    k = M.appear(g, 2, 0.4)
    tilt = K.lerp(0.9, 0.0, K.ease_in_out(clamp01(g.since(6) / 0.6))) if g.since(6) >= 0 else 0.9 * k
    balance(c, g, tilt, 0.85, alpha=1)


# ---------------------------------------------------------------- 13 小练习：两个问题

def two_questions(c, g, t, d):
    qs = [("T", "这样合理吗？"), ("F", "这样对人好吗？")]
    for i, (ch, q) in enumerate(qs):
        k = M.appear(g, 2 + 4 * i, 0.35)
        if k <= 0:
            continue
        y = -170 + i * 260
        dx = (1 - ease_out(k)) * 140
        with K.fade(c, clamp01(k * 2.5)):
            M.tile(c, -300 + dx, y, 130, ch)
            K.text_card(c, 110 + dx, y, [q], 52, 520, K.PAPER, K.INK, ACC, 1, 0, 1, M.DIM[ch], "serif", 0.8)
        c_k = M.appear(g, 4 + 4 * i, 0.25)
        if c_k > 0:
            K.icon(c, "check", 420, y, 90, K.GREEN, clamp01(c_k * 3), 0.4, 0, 0.3 + 0.7 * K.ease_out_back(c_k, 2))


def build() -> Episode:
    shots = [
        # 1
        Shot(3, "朋友失恋了，|哭着来找你们。", "情境演绎", [
            Fig(540, GROUND, 330, at=0, color=K.OTHER2, hair="short", mood="sad", pose="cover",
                sfx="wood_low", note="朋友捂着脸哭"),
            Custom(tears, x=548, y=840, at=1, enter="fade"),
            Fig(200, GROUND, 330, at=4, color=T_COL, hair="short", mood="worried", sfx="wood_high",
                note="左边的朋友赶来"),
            Fig(880, GROUND, 330, at=6, color=F_COL, hair="long", mood="worried", face=-1, sfx="bongo_high",
                note="右边的朋友赶来"),
        ], draw=ground, hits=[(10, "shaker", 0.6, "抽泣")],
            note="中间的朋友捂脸哭，泪珠一直往下掉；两个朋友一左一右赶到"),
        # 2
        Shot(3, "一个人马上开始|帮忙分析问题。", "情境演绎", [
            Fig(200, GROUND, 330, at=0, enter="none", color=T_COL, hair="short", mood="open",
                moves=[(2, dict(pose="point", sfx="wood_low", note="左边的人开始讲道理"))]),
            Fig(540, GROUND, 330, at=0, enter="none", color=K.OTHER2, hair="short", mood="sad", pose="sad"),
            Custom(plan_card, x=330, y=560, at=0, enter="none"),
        ], draw=ground, hits=[(3, "wood_high", 0.7, "第 1 条建议"), (5, "wood_low", 0.7, "第 2 条"),
                              (7, "bongo_high", 0.7, "第 3 条")],
            note="左边的人指着一张清单，三条建议按拍列出"),
        # 3
        Shot(2, "另一个人，|先递上了纸巾。", "情境演绎", [
            Fig(540, GROUND, 330, at=0, enter="none", color=K.OTHER2, hair="short", mood="sad", pose="sad",
                moves=[(5, dict(mood="calm", sfx="wood_low", note="朋友抬起头"))]),
            Fig(860, GROUND, 330, at=0, enter="none", color=F_COL, hair="long", mood="worried", face=-1,
                moves=[(1, dict(x=810, sfx="wood_high", note="右边的人走近")),
                       (3, dict(pose="give", mood="smile", note="递出纸巾"))]),
            Custom(tissue, x=680, y=965, at=3, enter="pop", sfx="bongo_high", note="一张纸巾抽出来"),
        ], draw=ground, note="右边的人走近，递出一盒纸巾，抽出一张；朋友抬起头"),
        # 4  drop
        Shot(3, "T/F 问的是：|你靠什么做决定？", "机制示意", [
            Big("思考与情感", 540, 470, 140, at=0, sfx="kick", sub="Thinking · Feeling", note="概念落版（音乐 drop）"),
            Custom(two_tiles, x=540, y=880, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.8, "T 牌落位"), (8, "wood_low", 0.8, "F 牌落位")],
            note="drop 处概念砸下；T、F 两张牌按拍落位"),
        # 5
        Shot(3, "荣格把思维和情感，|都叫作“判断功能”。", "荣格原著", [
            Custom(judge_scale, x=540, y=620, at=0, enter="pop", sfx="wood_low", note="天平出现"),
        ], hits=[(4, "wood_high", 0.8, "天平停稳"), (8, "rim", 0.8, "判断功能：怎样做决定")],
            note="一架天平左右秤盘放着 T、F，摇晃后停稳，上方落下“判断功能”"),
        # 6
        Shot(3, "T 先看：|这样合不合逻辑？", "机制示意", [
            Custom(logic_chain, x=540, y=780, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "“事实”"), (4, "wood_low", 0.7, "“推理”"), (6, "bongo_high", 0.7, "“结论”"),
                 (8, "clap", 0.8, "打勾")],
            note="“事实 → 推理 → 结论”三张卡片按拍连成一条链，最后打勾"),
        # 7
        Shot(3, "F 先看：|这样对人好不好？", "机制示意", [
            Custom(people_hearts, x=540, y=720, at=0, enter="fade"),
        ], hits=[(2, "wood_high", 0.7, "第一颗心"), (4, "wood_low", 0.7, "第二颗心"), (6, "bongo_high", 0.8, "第三颗心")],
            note="三个人之间按拍连起虚线，每条线上冒出一颗心"),
        # 8
        Shot(2, "两种都是|理性的判断。", "机制示意", [
            Custom(level_scale, x=540, y=600, at=0, enter="pop", sfx="wood_low", note="天平摇晃"),
        ], hits=[(3, "rim", 0.8, "天平停在水平")], note="天平晃了几下，第 3 拍停在正中"),
        # 9
        Shot(2, "只是依据|不一样。", "机制示意", [
            Custom(basis, x=540, y=820, at=0, enter="none"),
        ], hits=[(1, "wood_high", 0.8, "T：逻辑"), (4, "wood_low", 0.8, "F：价值")],
            note="T 下面写“逻辑”配对勾，F 下面写“价值”配爱心"),
        # 10
        Shot(3, "情感型不等于|情绪化。", "常见误解", [
            Fig(540, GROUND, 340, at=0, color=F_COL, hair="long", mood="calm",
                moves=[(2, dict(pose="think", note="F 型的人冷静思考"))]),
            Custom(storm, x=540, y=560, at=0, enter="pop", sfx="wood_low", note="头顶乌云"),
        ], draw=ground, hits=[(6, "rim", 0.9, "乌云被打叉")],
            note="F 型的人冷静地托腮思考，头顶的“情绪乌云”第 6 拍被打叉"),
        # 11
        Shot(3, "思考型也不等于|冷漠。", "常见误解", [
            Fig(400, GROUND, 340, at=0, color=T_COL, hair="short", mood="calm",
                moves=[(2, dict(x=520, sfx="wood_high", note="T 型的人走向朋友")),
                       (6, dict(pose="hug", mood="smile", sfx="clap", note="给朋友一个拥抱"))]),
            Fig(700, GROUND, 330, at=0, color=K.OTHER2, hair="short", mood="sad", face=-1,
                moves=[(8, dict(mood="smile", pose="hug"))]),
            Custom(warm_heart, x=610, y=560, at=0, enter="none"),
        ], draw=ground, hits=[(4, "bongo_high", 0.8, "心亮起"), (8, "wood_low", 0.6, "朋友笑了")],
            note="T 型的人走过去抱住朋友，两人头顶亮起一颗心"),
        # 12
        Shot(4, "好的决定，|往往两样都看。", "常见误解", [
            Custom(both, x=540, y=600, at=0, enter="none"),
        ], hits=[(2, "wood_low", 0.7, "天平先往一边倒"), (6, "wood_high", 0.8, "两边都放稳"),
                 (10, "clap", 0.8, "天平平衡")],
            note="天平先往一边倒，第 6 拍回到平衡"),
        # 13
        Shot(4, "下次做决定，|两个问题都问一遍。", "小练习", [
            Custom(two_questions, x=540, y=800, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.8, "“这样合理吗？”"), (4, "shaker", 0.6, "打勾"),
                 (6, "wood_low", 0.8, "“这样对人好吗？”"), (8, "clap", 0.7, "打勾")],
            note="两张问题卡“这样合理吗？”“这样对人好吗？”按拍滑入并打勾"),
        # 14
        Shot(2, "讲道理和讲感情，|并不冲突。", "机制示意", [
            Fig(360, GROUND, 330, at=0, color=T_COL, hair="short", mood="happy",
                moves=[(2, dict(pose="give", sfx="wood_high", note="两人伸出手"))]),
            Fig(720, GROUND, 330, at=0, color=F_COL, hair="long", mood="happy", face=-1,
                moves=[(2, dict(pose="give"))]),
            Icon("heart", 540, 560, 120, color=ACC, at=4, enter="pop", sfx="bongo_high", note="中间亮起一颗心"),
        ], draw=ground, note="T 型和 F 型两人握手，中间亮起一颗心"),
        end_shot(REFS, "05 J/P：做计划的人，一定更自律吗？"),
    ]
    return Episode(4, "tf", "思考与情感", "讲道理的人，就没有感情吗？", ACC, shots, refs=REFS,
                   publish_title="讲道理的人，就没有感情吗？｜MBTI科普04 思考与情感",
                   hashtags="#MBTI #心理学 #思考 #情感 #荣格",
                   cover_title="讲道理的人，|就没有【感情】吗？", cover_sub="MBTI 的 T 与 F", cover_shot=2, cover_t=3.5,
                   notes=[
                       "第 5 镜：荣格把思维与情感归为“理性功能”，MBTI 称为判断功能（judging functions），与感觉、直觉两种知觉功能相对。",
                       "第 8 镜“两种都是理性的判断”即取荣格把两者都列为理性功能之意。",
                       "T 看逻辑一致、F 看人与价值，是 MBTI 对两种偏好的通行描述；第 6、7 镜为示意。",
                       "第 13 镜两个问题是帮助做决定的小练习，不是官方材料原文。",
                       "MBTI、Myers-Briggs Type Indicator 是 The Myers-Briggs Company 的注册商标。",
                   ], **SERIES).build()
