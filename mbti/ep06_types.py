"""06 16型：16 种人格，是怎么拼出来的？"""

import math

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Icon, Shot, end_shot

from . import kit_mbti as M

ACC = "#7A5C9E"
GROUND = 1130
SERIES = dict(series="MBTI 科普", file_prefix="MBTI")
REFS = ["Myers, I. B. & Myers, P. B. (1980). Gifts Differing.（中译《天生不同》）",
        "Keirsey, D. & Bates, M. (1978). Please Understand Me.",
        "Keirsey, D. (1998). Please Understand Me II."]

ALL16 = [a + b + t + j for a in "EI" for b in "SN" for t in "TF" for j in "JP"]
GRID16 = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP",
          "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
TEMPS = [("NT", "理性者"), ("NF", "理想主义者"), ("SJ", "护卫者"), ("SP", "技艺者")]
TEMP_COL = {"NT": M.DIM["T"], "NF": M.DIM["F"], "SJ": M.DIM["J"], "SP": M.DIM["P"]}


def ground(g):
    K.ground(g.c, GROUND)


def temp_of(code: str) -> str:
    if code[1] == "N":
        return "N" + code[2]
    return "S" + code[3]


def mini_code(c, x, y, code, s=46, alpha=1.0, scale=1.0, color=None):
    """一枚小号四字母卡：单色底 + 四个字母。"""
    if alpha <= 0 or scale <= 0:
        return
    w = s * 4.2
    col = color or ACC
    with K.at(c, x, y, 0, scale):
        with K.paper(c, alpha, 0.6):
            K.rr(c, 0, 0, w, s * 1.4, s * 0.3, col)
        K.text(c, code, 0, s * 0.03, s, "black", K.PAPER, alpha)


# ---------------------------------------------------------------- 1 翻面的字母牌

def flipping(c, g, t, d):
    """四张牌，每张两面（E/I、S/N、T/F、J/P）；第 2/4/6/8 拍依次翻到另一面。"""
    for i, (a, b) in enumerate(M.PAIRS):
        x = -330 + i * 220
        k = clamp01(g.since(2 + 2 * i) / 0.4)
        ang = math.pi * ease_in_out(k)
        ch = a if ang < math.pi / 2 else b
        M.tile(c, x, 0, 170, ch, None, 1, abs(math.cos(ang)), 0, 1)


def shuffle(c, g, t, d):
    """四张牌不停随机翻面，下方的计数器跳动。"""
    for i, (a, b) in enumerate(M.PAIRS):
        x = -330 + i * 220
        ph = g.t * (2.2 + 0.4 * i) + i
        ang = (ph % 1) * math.pi
        ch = a if (int(ph + 0.5) % 2 == 0) else b
        M.tile(c, x, 0, 160, ch, None, 1, abs(math.cos(ang)), 0, 1)
    K.text(c, "组合：?", 0, -190, 60, "serif_black", ACC, M.appear(g, 6))


# ---------------------------------------------------------------- 4 drop：2×2×2×2

def multiply(c, g, t, d):
    items = ["2", "×2", "×2", "×2", "= 16"]
    xs = [-385, -235, -75, 85, 300]
    for i, s in enumerate(items):
        k = M.appear(g, 4 + 2 * i if i < 4 else 11, 0.25)
        if k <= 0:
            continue
        with K.at(c, xs[i], 0, 0, 1 + 0.4 * (1 - ease_out(k))):
            K.text(c, s, 0, 0, 96 if i < 4 else 110, "black", K.RED if i == 4 else K.INK, clamp01(k * 3))


# ---------------------------------------------------------------- 5 分叉树

def tree(c, g, t, d):
    """四层分叉：每拍多一层，节点数 2 → 4 → 8 → 16。"""
    levels = 4
    top = -400
    gap = 230
    K.dot(c, 0, top - 60, 18, K.INK)
    for lv in range(levels):
        k = M.appear(g, 2 + 2 * lv, 0.4)
        if k <= 0:
            break
        n = 2 ** (lv + 1)
        a, b = M.PAIRS[lv]
        y = top + lv * gap + 60
        span = 860
        for j in range(n):
            x = -span / 2 + span * (j + 0.5) / n
            px = -span / 2 + span * (j // 2 + 0.5) / (n // 2) if lv > 0 else 0
            py = y - gap if lv > 0 else top - 60
            K.seg(c, px, py + (20 if lv else 0), K.lerp(px, x, ease_out(k)), K.lerp(py + (20 if lv else 0), y - 26, ease_out(k)),
                  K.LINE, 5)
            ch = a if j % 2 == 0 else b
            sz = (90, 74, 56, 46)[lv]
            if k > 0.6:
                M.tile(c, x, y, sz, ch, None, clamp01((k - 0.6) * 3))
        K.text(c, str(n), 470, y, 44, "black", ACC, k)


# ---------------------------------------------------------------- 6 4×4 网格

def grid(c, g, t, d, group=False):
    for i, code in enumerate(GRID16):
        r, col = i // 4, i % 4
        k = M.appear(g, 2 + 2 * r, 0.35) if not group else 1.0
        if k <= 0:
            continue
        x = -330 + col * 220
        y = -270 + r * 180
        color = TEMP_COL[temp_of(code)] if group else ACC
        mini_code(c, x, y, code, 42, clamp01(k * 3), 0.3 + 0.7 * K.ease_out_back(k, 1.8), color)


def grid_plain(c, g, t, d):
    grid(c, g, t, d)


# ---------------------------------------------------------------- 7/8 Keirsey 四组

def four_temps(c, g, t, d):
    for i, (tc, name) in enumerate(TEMPS):
        k = M.appear(g, 2 + 2 * i, 0.35)
        if k <= 0:
            continue
        x = -230 + (i % 2) * 460
        y = -170 + (i // 2) * 340
        sc = 0.3 + 0.7 * K.ease_out_back(k, 1.8)
        with K.at(c, x, y, 0, sc):
            K.card(c, 0, 0, 400, 280, K.PAPER, clamp01(k * 3), 26, 1, 0, 1, TEMP_COL[tc])
            M.tile(c, -60, -30, 110, tc[0], alpha=clamp01(k * 3))
            M.tile(c, 60, -30, 110, tc[1], alpha=clamp01(k * 3))
            K.text(c, name, 0, 80, 40, "serif_black", K.INK, clamp01(k * 3))


def grouped_grid(c, g, t, d):
    """16 个类型按气质组着色、并归拢到四个角。"""
    k = ease_in_out(clamp01(g.since(1) / 0.6))
    corners = {"NT": (-230, -200), "NF": (230, -200), "SJ": (-230, 200), "SP": (230, 200)}
    slots: dict = {}
    for i, code in enumerate(GRID16):
        r, col = i // 4, i % 4
        x0, y0 = -330 + col * 220, -270 + r * 180
        tp = temp_of(code)
        j = slots.get(tp, 0)
        slots[tp] = j + 1
        cx, cy = corners[tp]
        x1, y1 = cx + (j % 2 - 0.5) * 200, cy + (j // 2 - 0.5) * 110
        color = K.mix(ACC, TEMP_COL[tp], clamp01(g.since(0) / 0.4))
        mini_code(c, K.lerp(x0, x1, k), K.lerp(y0, y1, k), code, 38, 1, 1, color)
    for tp, (cx, cy) in corners.items():
        kk = M.appear(g, 4 + 0.5 * list(corners).index(tp), 0.3)
        if kk > 0:
            K.pill(c, cx, cy - 145 if cy < 0 else cy + 145, tp, 34, TEMP_COL[tp], K.PAPER, kk)


# ---------------------------------------------------------------- 9 不是官方分法

def not_official(c, g, t, d):
    M.book(c, -220, 0, 330, "Please|Understand|Me", "#5A4A6E", 1, "Keirsey & Bates · 1978", -4)
    M.book(c, 220, 0, 330, "MBTI|手册", "#3B5B8C", 1, "Manual", 3)
    k = M.appear(g, 3, 0.3)
    if k > 0:
        K.text(c, "≠", 0, 0, 150, "black", K.RED, k)


# ---------------------------------------------------------------- 10 排行榜

PODIUM = [("INTJ", 0, 330), ("ENFP", -300, 240), ("ISTP", 300, 170)]


def podium(c, g, t, d, flatten=0.0):
    for i, (code, x, h) in enumerate(PODIUM):
        k = M.appear(g, 2 + 2 * i, 0.35)
        if k <= 0:
            continue
        hh = K.lerp(h, 170, flatten) * ease_out(k)
        K.rr(c, x, 300 - hh / 2, 260, hh, 10, K.mix(ACC, K.PAPER, 0.25 + 0.15 * i))
        K.text(c, str(i + 1) if flatten < 0.5 else "", x, 300 - hh / 2, 70, "black", K.PAPER, k)
        mini_code(c, x, 300 - hh - 60, code, 40, k, 1)
    if flatten <= 0:
        kc = M.appear(g, 8, 0.3)
        if kc > 0:
            with K.at(c, 0, 300 - 330 - 170, 0, 0.3 + 0.7 * K.ease_out_back(kc, 2)):
                K.icon(c, "crown", 0, 0, 110, K.GOLD, kc, 0.5)


def podium_rise(c, g, t, d):
    podium(c, g, t, d)
    k = M.appear(g, 9, 0.3)
    if k > 0:
        K.text_card(c, 0, -350, ["“最稀有，最厉害”"], 44, None, K.PAPER, K.INK, ACC, k, -3, 1, None, "serif", 0.8)


def podium_flat(c, g, t, d):
    """领奖台在第 6 拍塌平成一样高，皇冠消失。"""
    f = ease_in_out(clamp01(g.since(6) / 0.45))
    for i, (code, x, h) in enumerate(PODIUM):
        hh = K.lerp(h, 170, f)
        K.rr(c, x, 300 - hh / 2, 260, hh, 10, K.mix(ACC, K.PAPER, 0.25 + 0.15 * i))
        if f < 0.5:
            K.text(c, str(i + 1), x, 300 - hh / 2, 70, "black", K.PAPER, 1 - 2 * f)
        mini_code(c, x, 300 - hh - 60, code, 40, 1, 1)
    ka = 1 - f
    if ka > 0:
        K.icon(c, "crown", 0, 300 - 330 - 170, 110, K.GOLD, ka, 0.5)
    k = M.appear(g, 8, 0.35)
    if k > 0:
        K.text(c, "偏好组合 ≠ 能力等级", 0, -350, 52, "serif_black", ACC, k)


# ---------------------------------------------------------------- 12 各有各的习惯

def codes_over(c, g, t, d):
    for i, (code, x) in enumerate((("ISTJ", -360), ("ENFP", -120), ("INTP", 120), ("ESFJ", 360))):
        k = M.appear(g, 1 + 2 * i, 0.35)
        if k > 0:
            mini_code(c, x, 0, code, 36, k, 0.3 + 0.7 * K.ease_out_back(k, 1.8), TEMP_COL[temp_of(code)])


# ---------------------------------------------------------------- 13 最不确定的字母

def unsure(c, g, t, d):
    targets = (-0.55, 0.5, 0.05, -0.4)
    for i, (a, b) in enumerate(M.PAIRS):
        k = M.appear(g, i * 0.5, 0.35)
        if k <= 0:
            continue
        y = -330 + i * 220
        if i == 2:
            pos = 0.35 * math.sin(g.t * 3.2) * (1 - 0.3 * clamp01(g.since(12) / 1))
        else:
            off, done = M.wiggle(g, 2, 4 + 2 * min(i, 2) + (2 if i == 3 else 0), 0.5, 6 + i)
            pos = targets[i] if done else off
        M.scale_bar(c, 0, y, 760, a, b, pos, clamp01(k * 2), None, 74)
        if i == 2:
            kq = M.appear(g, 12, 0.3)
            if kq > 0:
                with K.at(c, 0, y - 95, 0, 0.3 + 0.7 * K.ease_out_back(kq, 2)):
                    K.icon(c, "question", 0, 0, 90, ACC, kq, 0.5)


# ---------------------------------------------------------------- 14 地图

def map_grid(c, g, t, d):
    for i, code in enumerate(GRID16):
        r, col = i // 4, i % 4
        k = M.appear(g, (i % 4) * 0.5, 0.3)
        mini_code(c, -330 + col * 220, -270 + r * 150, code, 38, k, 1, TEMP_COL[temp_of(code)])


def build() -> Episode:
    shots = [
        # 1
        Shot(3, "四张字母牌，|每张都有正反两面。", "情境演绎", [
            Custom(flipping, x=540, y=760, at=0, enter="pop"),
        ], hits=[(2, "wood_high", 0.8, "E 翻成 I"), (4, "wood_low", 0.8, "S 翻成 N"),
                 (6, "bongo_high", 0.8, "T 翻成 F"), (8, "bongo_low", 0.8, "J 翻成 P")],
            note="E、S、T、J 四张牌按拍依次翻面，露出 I、N、F、P"),
        # 2
        Shot(3, "随便翻一翻，|能拼出多少种组合？", "情境演绎", [
            Custom(shuffle, x=540, y=640, at=0, enter="none"),
            Fig(540, GROUND, 300, at=0, pose="think", mood="worried", hair="short",
                moves=[(8, dict(mood="surprised", look=1.0, sfx="rim", note="主角抬头数组合"))]),
        ], draw=ground, hits=[(0, "shaker", 0.6, "四张牌开始乱翻"), (6, "wood_high", 0.7, "“组合：?”出现")],
            note="四张牌在主角头顶不停乱翻，下方出现“组合：?”"),
        # 3
        Shot(2, "猜一猜，|一共有几种？", "情境演绎", [
            Fig(400, GROUND, 330, at=0, enter="none", pose="think", mood="calm", hair="short"),
            Icon("question", 700, 650, 200, color=ACC, at=2, enter="pop", sfx="bongo_low", note="大问号"),
        ], draw=ground, note="主角托腮思考，身旁弹出大问号"),
        # 4 drop
        Shot(3, "每对二选一：|2×2×2×2 ＝ 16。", "机制示意", [
            Big("16 型", 540, 470, 160, at=0, sfx="kick", sub="16 types", note="概念落版（音乐 drop）"),
            Custom(multiply, x=540, y=860, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.8, "2"), (6, "wood_low", 0.8, "×2"), (8, "wood_high", 0.8, "×2"),
                 (10, "wood_low", 0.8, "×2"), (11, "clap", 0.9, "= 16")],
            note="drop 处“16 型”砸下；算式 2×2×2×2 按拍一个个出现，第 11 拍“= 16”"),
        # 5
        Shot(3, "每多一对字母，|组合就翻一倍。", "机制示意", [
            Custom(tree, x=540, y=840, at=0, enter="fade"),
        ], hits=[(2, "wood_high", 0.7, "第一层：E / I"), (4, "wood_low", 0.7, "第二层：4 种"),
                 (6, "bongo_high", 0.7, "第三层：8 种"), (8, "bongo_low", 0.8, "第四层：16 种")],
            note="分叉树每两拍长出一层，右侧计数 2 → 4 → 8 → 16"),
        # 6
        Shot(3, "16 个四字母组合，|就是 16 种类型。", "机制示意", [
            Custom(grid_plain, x=540, y=820, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "第一行四个类型"), (4, "wood_low", 0.7, "第二行"),
                 (6, "wood_high", 0.7, "第三行"), (8, "wood_low", 0.7, "第四行")],
            note="4×4 类型网格，每两拍弹出一行"),
        # 7
        Shot(3, "有人把 16 型|再分成四组。", "Keirsey 气质论", [
            Custom(four_temps, x=540, y=800, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.8, "NT 组"), (4, "wood_low", 0.8, "NF 组"),
                 (6, "bongo_high", 0.8, "SJ 组"), (8, "bongo_low", 0.8, "SP 组")],
            note="四张气质卡按拍弹出：NT 理性者、NF 理想主义者、SJ 护卫者、SP 技艺者"),
        # 8
        Shot(2, "NT、NF、SJ、SP，|叫作四种气质。", "Keirsey 气质论", [
            Custom(grouped_grid, x=540, y=820, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.7, "16 个类型归拢到四个角"), (4, "wood_high", 0.7, "四组标签出现")], text_beat=0,
            note="16 张类型卡按气质组变色，归拢到四个角"),
        # 9
        Shot(2, "这是 Keirsey 的分法，|不是 MBTI 官方的。", "常见误解", [
            Custom(not_official, x=540, y=800, at=0, enter="pop"),
        ], hits=[(3, "rim", 0.9, "两本书之间的不等号")], text_beat=0,
            note="Keirsey 的书与 MBTI 手册并排，中间砸下不等号"),
        # 10
        Shot(3, "网上常说：|某型最稀有、最厉害。", "常见误解", [
            Custom(podium_rise, x=540, y=800, at=0, enter="none"),
        ], hits=[(2, "wood_low", 0.7, "领奖台：第一个"), (4, "wood_low", 0.7, "第二个"), (6, "wood_high", 0.7, "第三个"),
                 (8, "cymbal", 0.6, "皇冠落下"), (9, "shaker", 0.6, "“最稀有，最厉害”")],
            note="三个类型站上领奖台，第一名戴上皇冠，旁边是“最稀有，最厉害”"),
        # 11
        Shot(3, "可类型说的是偏好，|不是能力等级。", "机制示意", [
            Custom(podium_flat, x=540, y=800, at=0, enter="none"),
        ], hits=[(6, "tom", 0.9, "领奖台塌平"), (8, "wood_high", 0.8, "“偏好组合 ≠ 能力等级”")],
            note="领奖台在第 6 拍塌成一样高，皇冠消失"),
        # 12
        Shot(4, "16 种组合，|各有各的习惯。", "机制示意", [
            Custom(codes_over, x=540, y=560, at=0, enter="none"),
            Fig(180, GROUND, 300, at=0, mood="calm", hair="short", color=M.DIM["J"],
                moves=[(1, dict(pose="carry", sfx="wood_high", note="ISTJ 抱着文件"))]),
            Fig(420, GROUND, 300, at=0, mood="happy", hair="long", color=M.DIM["F"],
                moves=[(3, dict(pose="wave", sfx="wood_low", note="ENFP 挥手"))]),
            Fig(660, GROUND, 300, at=0, mood="calm", hair="cap", color=M.DIM["T"],
                moves=[(5, dict(pose="think", sfx="bongo_high", note="INTP 托腮"))]),
            Fig(900, GROUND, 300, at=0, mood="smile", hair="bun", color=M.DIM["P"], face=-1,
                moves=[(7, dict(pose="give", sfx="bongo_low", note="ESFJ 递东西"))]),
        ], draw=ground, note="四个人头顶各自的类型卡，按拍做出不同的动作，站在同一条地面上"),
        # 13
        Shot(4, "四个字母里，|你最不确定的是哪个？", "小练习", [
            Custom(unsure, x=540, y=830, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.7, "E/I 停下"), (6, "wood_low", 0.7, "S/N 停下"), (8, "bongo_high", 0.7, "J/P 停下"),
                 (12, "rim", 0.8, "T/F 仍在摇摆，问号弹出")],
            note="四条量尺三条停下，T/F 那条一直摇摆，第 12 拍上方弹出问号"),
        # 14
        Shot(2, "16 型是一张地图，|不是排行榜。", "机制示意", [
            Custom(map_grid, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.7, "地图第一列"), (2, "wood_low", 0.7, "地图最后一列")], text_beat=0,
            note="16 个类型平铺成一张地图，一样大小，一样高"),
        end_shot(REFS, "07 网络测试：你测的，真的是 MBTI 吗？"),
    ]
    return Episode(6, "types", "16型", "16 种人格，是怎么拼出来的？", ACC, shots, refs=REFS,
                   publish_title="16 种人格，是怎么拼出来的？｜MBTI科普06 16型",
                   hashtags="#MBTI #心理学 #16型人格 #人格类型 #科普",
                   cover_title="16 种人格，|是怎么【拼】出来的？", cover_sub="四对偏好的组合", cover_shot=4, cover_t=5.5,
                   notes=[
                       "16 型是四对偏好的组合（2×2×2×2），每个类型代表一组偏好，不代表能力高低或优劣。",
                       "NT / NF / SJ / SP 四组气质出自 Keirsey & Bates (1978) Please Understand Me，不是 MBTI 官方分法，片中角标“Keirsey 气质论”。",
                       "“理性者 / 理想主义者 / 护卫者 / 技艺者”是 Keirsey 1998 年 Please Understand Me II 中的称呼；1978 年第一版用的是希腊神话名。",
                       "第 10 镜“某型最稀有、最厉害”是网络常见说法的情境演绎，不是研究结论；片中没有引用任何类型比例数据。",
                       "MBTI、Myers-Briggs Type Indicator 是 The Myers-Briggs Company 的注册商标。",
                   ], **SERIES).build()
