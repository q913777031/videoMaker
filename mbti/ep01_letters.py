"""01 四个字母：那四个字母，到底是谁发明的？"""

import math

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Big, Bubble, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import kit_mbti as M

ACC = "#3B5B8C"
GROUND = 1130
SERIES = dict(series="MBTI 科普", file_prefix="MBTI")
REFS = ["Jung, C. G. (1921). Psychologische Typen.（英译 Psychological Types, 1923）",
        "The Myers-Briggs Company. Myers-Briggs history（官网时间线）",
        "Myers, I. B. & Myers, P. B. (1980). Gifts Differing.（中译《天生不同》）"]


def ground(g):
    K.ground(g.c, GROUND)


# ---------------------------------------------------------------- 1 聚会自报类型

def party_lights(g):
    ground(g)
    c = g.c
    for i, col in enumerate((K.GOLD, ACC, K.RED, K.GREEN, K.GOLD, ACC)):
        x = 140 + i * 160
        K.seg(c, x - 80, 400 + 20 * math.sin(i), x + 80, 400 + 20 * math.sin(i + 1), K.LINE, 3)
        K.dot(c, x, 412 + 20 * math.sin(i + 0.5), 14, col, 0.75 + 0.25 * math.sin(g.t * 3 + i))


# ---------------------------------------------------------------- 2 字母满天飞

def flying_tiles(c, g, t, d):
    """八个字母牌在半空中缓缓漂浮旋转，按拍依次弹出。"""
    spots = [(-330, -230, "E"), (-120, -300, "N"), (110, -250, "T"), (320, -310, "P"),
             (-360, 20, "I"), (-140, -60, "S"), (130, 10, "F"), (350, -40, "J")]
    for i, (x, y, ch) in enumerate(spots):
        k = M.appear(g, i * 0.5)
        if k <= 0:
            continue
        bob = 14 * math.sin(g.t * 1.8 + i)
        rot = 10 * math.sin(g.t * 1.2 + i * 1.7)
        M.tile(c, x, y + bob, 110, ch, None, clamp01(k * 3), 1, rot, 0.3 + 0.7 * K.ease_out_back(k, 1.8))


# ---------------------------------------------------------------- 4 drop：四对字母

def four_pairs(c, g, t, d):
    """四对字母牌按拍落位：每一对上下排列，被选中的一张抬起变亮。"""
    for i, (a, b) in enumerate(M.PAIRS):
        k = M.appear(g, 4 + 2 * i, 0.3)
        if k <= 0:
            continue
        x = -330 + i * 220
        pick = M.appear(g, 5 + 2 * i, 0.3)
        sc = 0.3 + 0.7 * K.ease_out_back(k, 1.8)
        M.tile(c, x, -70 - 30 * ease_out(pick), 130, a, None, clamp01(k * 3), 1, 0, sc * (1 + 0.08 * pick),
               glow=pick)
        M.tile(c, x, 110, 130, b, None, clamp01(k * 3) * (1 - 0.55 * pick), 1, 0, sc)


# ---------------------------------------------------------------- 5 荣格的书

def jung_book(c, g, t, d):
    M.book(c, 0, 0, 380, "心理|类型", "#6B4A3A", 1, "C. G. Jung · 1921", -3)
    k = M.appear(g, 4, 0.4)
    if k > 0:
        K.arrow(c, (220, -40), (420, -170), K.HERO, 10, k, k, 0.1, 30)
        K.arrow(c, (220, 40), (420, 170), K.OTHER3, 10, k, k, -0.1, 30)


# ---------------------------------------------------------------- 6 母女读书

def reading_scene(g):
    ground(g)
    K.seat(g.c, 540, GROUND, 520, 120, K.mix(K.OTHER, K.PAPER, 0.3))


# ---------------------------------------------------------------- 7 问卷与印章

def questionnaire(c, g, t, d):
    checks = [(i % 2, M.appear(g, 2 + 2 * i, 0.25)) for i in range(3)]
    M.quiz(c, -40, -90, 720, "参加聚会后，你通常|感到充满活力还是疲惫？", ["充满活力", "需要独处恢复"], [checks[0]], 1, 40, ACC)
    M.quiz(c, 60, 300, 640, "你更信任：", ["亲眼看到的事实", "自己的直觉"], [checks[1]], 1, 40, ACC)
    M.stamp(c, 250, -330, 190, "1943", K.RED, 1, M.appear(g, 8, 0.25))


def manual_stack(c, g, t, d):
    for i in range(3):
        k = M.appear(g, i * 0.5, 0.3)
        if k > 0:
            K.rr(c, 0, 120 - i * 60 - (1 - ease_out(k)) * 80, 520 - i * 20, 56, 8,
                 (K.mix(ACC, K.PAPER, 0.2), K.mix(K.GOLD, K.PAPER, 0.2), K.mix(K.GREEN, K.PAPER, 0.3))[i], k)
    M.book(c, 0, -200, 340, "MBTI|手册", ACC, M.appear(g, 2, 0.3), "Manual", 0,
           0.4 + 0.6 * K.ease_out_back(M.appear(g, 2, 0.4), 1.6))
    M.stamp(c, 210, -330, 170, "1962", K.RED, 1, M.appear(g, 4, 0.25))


# ---------------------------------------------------------------- 9 第四个字母

def fourth_letter(c, g, t, d):
    glow = [0, 0, 0, M.appear(g, 3, 0.4)]
    M.code(c, 0, 0, 170, "ESTJ", 1, 0.2, None, False, glow)
    k = M.appear(g, 3, 0.4)
    if k > 0:
        K.ring(c, 285, 0, 130, K.RED, 9, k, k)


# ---------------------------------------------------------------- 10 四个问题

QUESTIONS = [("E", "I", "能量从哪来？"), ("S", "N", "怎么收集信息？"), ("T", "F", "怎么做决定？"), ("J", "P", "怎样安排生活？")]


def four_questions(c, g, t, d):
    for i, (a, b, q) in enumerate(QUESTIONS):
        k = M.appear(g, 2 + 2 * i, 0.35)
        if k <= 0:
            continue
        y = -330 + i * 200
        dx = (1 - ease_out(k)) * 120
        with K.fade(c, clamp01(k * 2.5)):
            M.tile(c, -330 + dx, y, 110, a)
            M.tile(c, -200 + dx, y, 110, b)
            K.text_card(c, 150 + dx, y, [q], 46, 480, K.PAPER, K.INK, ACC, 1, 0, 1, None, "serif", 0.7)


# ---------------------------------------------------------------- 11 惯用手签名

def two_signatures(c, g, t, d):
    def card(x, y, label, wob, k0, hand_color):
        K.card(c, x, y, 820, 230, K.PAPER, 1, 22, 0.9)
        K.text(c, label, x - 380, y - 75, 32, "sans_medium", hand_color, 1, "left")
        K.seg(c, x - 340, y + 70, x + 340, y + 70, K.LINE, 3)
        M.signature(c, x + 20, y + 10, 560, wob, K.ease_in_out(clamp01(g.since(k0) / 1.0)), K.INK, 8, 3)

    card(0, -150, "惯用手", 0.0, 2, K.HERO)
    if g.since(6) >= -0.1:
        card(0, 150, "另一只手", 1.0, 6, K.OTHER3)


# ---------------------------------------------------------------- 12 偏好不是能力

def both_hands(c, g, t, d):
    k = M.appear(g, 0, 0.4)
    swing = [(-0.55, 0), (0.55, 4), (-0.3, 8)]
    pos = -0.55
    for p, b in swing:
        if g.since(b) >= 0:
            q = K.ease_in_out(clamp01(g.since(b) / 0.45))
            pos = K.lerp(pos, p, q) if b else p
    M.scale_bar(c, 0, 0, 820, "E", "I", pos, k, None, 90)


# ---------------------------------------------------------------- 13 猜猜你自己

def guess_scales(c, g, t, d):
    for i, (a, b) in enumerate(M.PAIRS):
        k = M.appear(g, i * 0.5, 0.35)
        if k <= 0:
            continue
        target = (-0.45, 0.35, 0.2, -0.6)[i]
        off, done = M.wiggle(g, 2, 4 + 3 * i, 0.55, 6 + i)
        pos = target if done else off
        if not done and g.since(4 + 3 * i) > -0.45:
            pos = K.lerp(off, target, K.ease_in_out(clamp01((g.since(4 + 3 * i) + 0.45) / 0.45)))
        M.scale_bar(c, 0, -330 + i * 220, 780, a, b, pos, clamp01(k * 2), None, 74, True, True, True)
        if done:
            K.burst(c, pos * (390 - 74 * 0.8), -330 + i * 220, g.since(4 + 3 * i), M.DIM[a if target < 0 else b],
                    30, 80, 8, 5)


# ---------------------------------------------------------------- 14 起点

def start_code(c, g, t, d):
    prog = [M.appear(g, i, 0.35) for i in range(4)]
    M.code(c, 0, 0, 160, "????", 1, 0.2, prog)
    k = M.appear(g, 5, 0.6)
    if k > 0:
        K.road(c, 0, 520, 0, 140, K.LINE, 90, k, k)


def build() -> Episode:
    shots = [
        # 1
        Shot(3, "聚会上，人人都在|报自己的四个字母。", "情境演绎", [
            Fig(220, GROUND, 330, at=0, mood="happy", color=K.OTHER, hair="bun"),
            Fig(860, GROUND, 330, at=0, mood="smile", color=K.OTHER3, face=-1),
            Fig(540, GROUND, 360, at=0, mood="calm", hair="short",
                moves=[(10, dict(pose="think", mood="worried", sfx="tom", note="主角挠头：我是什么？"))]),
            Bubble("我 INFJ！", 230, 640, 46, at=2, sfx="wood_high", note="左边的人自报 INFJ"),
            Bubble("我 ENTP～", 840, 560, 46, at=5, tail=(-0.3, 1), sfx="wood_low", note="右边的人自报 ENTP"),
            Bubble("我是 ISTJ", 400, 470, 40, at=8, sfx="bongo_high", note="又一个声音：ISTJ"),
            Icon("question", 610, 700, 110, color=ACC, at=10, enter="pop"),
        ], draw=party_lights, note="聚会上彩灯闪烁，左右两人按拍自报 INFJ、ENTP、ISTJ，中间的主角挠头"),
        # 2
        Shot(3, "可这四个字母，|到底是谁发明的？", "情境演绎", [
            Custom(flying_tiles, x=540, y=740, at=0, enter="none"),
            Fig(540, GROUND, 340, at=0, enter="none", pose="think", mood="worried", hair="short",
                moves=[(8, dict(look=1.0, mood="surprised", sfx="rim", note="主角抬头看满天的字母"))]),
        ], draw=ground, hits=[(0, "wood_high", 0.7, "第一张字母牌弹出"), (2, "wood_low", 0.7, "第五张字母牌弹出")],
            note="八张字母牌 E/I/S/N/T/F/J/P 依次弹出，在主角头顶漂浮旋转"),
        # 3
        Shot(2, "很多人会说：|“是荣格。”", "常见误解", [
            Bubble("荣格！", 300, 640, 56, at=1, sfx="wood_high", note="有人抢答：荣格"),
            Fig(300, GROUND, 330, at=0, mood="happy", color=K.OTHER, pose="point"),
            Icon("question", 770, 700, 150, color=ACC, at=4, enter="pop", sfx="bongo_low", note="大问号：只对一半"),
        ], draw=ground, note="有人抢答“荣格”，右边弹出大问号——只对了一半"),
        # 4  drop
        Shot(3, "MBTI：四对偏好，|每对选一边。", "机制示意", [
            Big("四个字母", 540, 470, 150, at=0, sfx="kick", sub="Myers-Briggs Type Indicator",
                note="概念落版（音乐 drop）"),
            Custom(four_pairs, x=540, y=880, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.8, "E/I 一对落位"), (6, "wood_low", 0.8, "S/N 一对落位"),
                 (8, "bongo_high", 0.8, "T/F 一对落位"), (10, "bongo_low", 0.8, "J/P 一对落位")],
            note="drop 处“四个字母”砸下；四对字母牌按拍落位，每对上面那张抬起变亮"),
        # 5
        Shot(3, "1921 年，荣格写了|《心理类型》。", "荣格原著", [
            Custom(jung_book, x=420, y=820, at=0, enter="pop", sfx="tom", note="《心理类型》出现"),
            Label("外倾", 900, 650, 40, at=4, fill=K.HERO, sfx="wood_high", note="外倾"),
            Label("内倾", 900, 990, 40, at=5, fill=K.OTHER3, sfx="wood_low", note="内倾"),
            Txt("感觉 · 直觉 · 思维 · 情感", 540, 1180, 38, at=8, font="sans_medium", color=K.INK2),
        ], hits=[(8, "shaker", 0.8, "四种心理功能")],
            note="荣格的书出现，箭头分出“外倾 / 内倾”，底部列出四种心理功能"),
        # 6
        Shot(3, "一对没学过心理学的|母女，读到了它。", "机制示意", [
            Fig(400, GROUND, 330, at=0, pose="sit", mood="calm", hair="bun", color="#7A6A8E"),
            Fig(680, GROUND, 300, at=0, pose="sit", mood="calm", hair="long", color=K.OTHER3, face=-1,
                moves=[(6, dict(mood="surprised", pose="point", sfx="bongo_high", note="女儿指着书：原来如此"))]),
            Label("凯瑟琳·布里格斯", 300, 640, 30, at=2, fill=K.INK2, sfx="wood_low", note="母亲"),
            Label("伊莎贝尔·迈尔斯", 790, 600, 30, at=3, fill=K.INK2, sfx="wood_high", note="女儿"),
            Icon("book", 540, 860, 130, color="#6B4A3A", at=0, enter="pop"),
            Icon("bulb", 760, 430, 120, at=8, enter="pop", sfx="clap", note="灵感灯泡亮起"),
        ], draw=reading_scene, note="母亲与女儿坐在长椅上读荣格的书，名字标签按拍出现，女儿指书、灯泡亮起"),
        # 7
        Shot(3, "她们把它做成问卷，|1943 年有了第一版。", "机制示意", [
            Custom(questionnaire, x=540, y=780, at=0, enter="pop"),
        ], hits=[(2, "wood_high", 0.8, "勾选第 1 题"), (4, "wood_low", 0.8, "勾选第 2 题"),
                 (8, "frame", 0.9, "1943 印章盖下")],
            note="问卷卡上两道题按拍打勾，第 8 拍盖下“1943”印章"),
        # 8
        Shot(2, "1962 年，ETS 出版了|正式的测验手册。", "机制示意", [
            Custom(manual_stack, x=540, y=860, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.7, "书堆落下"), (2, "bongo_high", 0.8, "手册出现"), (4, "frame", 0.9, "1962 印章盖下")],
            text_beat=0, note="书堆按拍叠起，MBTI 手册立在上面，盖下“1962”印章"),
        # 9
        Shot(2, "J/P 这一对，|是母女俩加上的。", "常见误解", [
            Custom(fourth_letter, x=540, y=800, at=0, enter="pop", sfx="wood_high", note="ESTJ 四张牌出现"),
        ], hits=[(3, "rim", 0.9, "J 被圈出")], text_beat=0, note="ESTJ 四张牌，第 3 拍最后一张 J 发光并被红圈圈出"),
        # 10
        Shot(3, "四对字母，|问的是四个问题。", "机制示意", [
            Custom(four_questions, x=540, y=860, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.8, "能量从哪来？"), (4, "wood_low", 0.8, "怎么收集信息？"),
                 (6, "bongo_high", 0.8, "怎么做决定？"), (8, "bongo_low", 0.8, "怎样安排生活？")],
            note="四行问题卡按拍从右滑入：能量从哪来、怎么收集信息、怎么做决定、怎样安排生活"),
        # 11
        Shot(3, "每对字母都是偏好，|就像惯用手。", "官方说明", [
            Custom(two_signatures, x=540, y=830, at=0, enter="pop"),
        ], hits=[(2, "shaker", 0.8, "惯用手签名一气呵成"), (6, "wood_low", 0.8, "换另一只手，签得歪歪扭扭")],
            note="两张签名卡：惯用手一笔流畅签完；换另一只手，签名歪歪扭扭"),
        # 12
        Shot(4, "偏好不是能力：|两边你都会用。", "常见误解", [
            Custom(both_hands, x=540, y=640, at=0, enter="none"),
            Fig(540, GROUND, 340, at=0, mood="calm", hair="short",
                moves=[(4, dict(pose="cheer", mood="happy", sfx="clap", note="主角两手都举起来")),
                       (8, dict(pose="stand", mood="smile"))]),
        ], draw=ground, hits=[(0, "wood_high", 0.7, "量尺出现"), (8, "wood_low", 0.7, "滑块回到偏 E 一侧")],
            note="E—I 量尺上的滑块左右滑动，主角两手都举起来：两边都会用，只是更习惯一边"),
        # 13
        Shot(4, "先别急着测，|猜猜你更像哪一边？", "小练习", [
            Custom(guess_scales, x=540, y=830, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.8, "第一条量尺停下"), (7, "wood_low", 0.8, "第二条停下"),
                 (10, "bongo_high", 0.8, "第三条停下"), (13, "bongo_low", 0.8, "第四条停下")],
            note="四条量尺的滑块各自犹豫摇摆，按拍一条条停在自己的位置"),
        # 14
        Shot(2, "四个字母，|只是认识自己的起点。", "机制示意", [
            Custom(start_code, x=540, y=640, at=0, enter="none"),
            Fig(540, GROUND, 320, at=5, enter="rise", mood="smile", hair="short", face=1),
        ], hits=[(0, "wood_high", 0.7, "第一个问号牌"), (3, "bongo_high", 0.8, "第四个问号牌"),
                 (5, "rim", 0.8, "脚下的路展开")],
            note="四张问号牌依次弹出，下面铺开一条路，主角站上去"),
        end_shot(REFS, "02 E/I：内向的人，就是不爱说话吗？"),
    ]
    return Episode(1, "letters", "四个字母", "那四个字母，到底是谁发明的？", ACC, shots, refs=REFS,
                   publish_title="那四个字母，到底是谁发明的？｜MBTI科普01 四个字母",
                   hashtags="#MBTI #心理学 #荣格 #人格类型 #科普",
                   cover_title="那四个字母，|到底是【谁】发明的？", cover_sub="MBTI 的来历", cover_shot=3, cover_t=6.0,
                   notes=[
                       "荣格《心理类型》1921 年出版德文版，1923 年出英译本；片中“外倾 / 内倾”与四种心理功能取自该书。",
                       "MBTI 由凯瑟琳·布里格斯与女儿伊莎贝尔·迈尔斯编制，两人都没有受过正式的心理学训练（维基百科词条）。",
                       "1943 年 Form A 版权登记，1962 年 ETS 出版研究版问卷与《MBTI 手册》（The Myers-Briggs Company 官网时间线）。",
                       "J/P 作为独立的第四个维度是迈尔斯母女的扩展，这是通行说法；荣格本人区分过判断功能与知觉功能，但没有把它单列为一对偏好。",
                       "第 7 镜问卷题目为示意，不是官方题目原文。",
                       "“偏好就像惯用手”与签名练习出自 MBTI 官方报告中的说明。",
                       "MBTI、Myers-Briggs Type Indicator 是 The Myers-Briggs Company 的注册商标。",
                   ], **SERIES).build()
