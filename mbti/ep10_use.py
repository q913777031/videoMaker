"""10 正确使用：四个字母，是标签还是语言？"""

import math

from engine.gfx import clamp01, ease_in, ease_out

from adler import kit as K
from adler.core import Big, Bubble, Custom, Episode, Fig, Icon, Shot, Txt, end_shot

from . import kit_mbti as M

ACC = "#B08A2E"
GROUND = 1130
SERIES = dict(series="MBTI 科普", file_prefix="MBTI")
REFS = ["The Myers-Briggs Company / CPP (2013). It is unethical to use the MBTI tool for hiring（官方声明）",
        "McCrae, R. R. & Costa, P. T. (1989). Reinterpreting the Myers-Briggs Type Indicator from the perspective of "
        "the five-factor model of personality. J. Personality, 57(1), 17–40.",
        "Myers, I. B. & Myers, P. B. (1980). Gifts Differing.（中译《天生不同》）"]
REFS_SHORT = ["The Myers-Briggs Company：关于招聘使用的官方声明",
              "McCrae, R. R. & Costa, P. T. (1989). J. Personality, 57(1), 17–40.",
              "Myers, I. B. & Myers, P. B. (1980). Gifts Differing.（中译《天生不同》）"]


def ground(g):
    K.ground(g.c, GROUND)


def pop_scale(k):
    return 0.3 + 0.7 * K.ease_out_back(k, 2)


# ---------------------------------------------------------------- 1 求职表

def job_form(c, g, t, d):
    rows = [("姓名", "小林"), ("学历", "本科"), ("MBTI", "")]

    def draw(c, w, h):
        K.text(c, "求职登记表", 0, -h / 2 + 70, 44, "serif_black", K.INK)
        for i, (a, b) in enumerate(rows):
            y = -h / 2 + 170 + i * 100
            k = M.appear(g, 1 + 2 * i, 0.3)
            K.text(c, a, -w / 2 + 50, y, 38, "sans_medium", K.INK2, 1, "left")
            K.seg(c, -w / 2 + 200, y + 26, w / 2 - 50, y + 26, K.LINE, 3)
            if b and k > 0:
                K.text(c, b, -w / 2 + 230, y, 38, "serif", K.INK, k, "left")
        q = M.appear(g, 6, 0.3)
        if q > 0:
            K.rr_stroke(c, 0, -h / 2 + 370, w - 50, 80, 16, K.RED, 6, q)

    K.card(c, 0, 0, 600, 480, K.PAPER, 1, 22, 1.0, 0, 1, ACC, draw)


# ---------------------------------------------------------------- 2 约会软件

def dating_phone(c, g, t, d):
    w, h = 420, 700
    with K.paper(c, 1, 1.1):
        K.rr(c, 0, 0, w, h, 50, K.DARK)
    K.rr(c, 0, 0, w - 30, h - 74, 30, K.PAPER)
    K.rr(c, 0, -h / 2 + 22, 96, 14, 7, K.INK)
    for i, (x, code, col) in enumerate(((-90, "INTJ", K.HERO), (90, "ESFP", K.OTHER3))):
        k = M.appear(g, 1 + 2 * i, 0.3)
        if k <= 0:
            continue
        with K.at(c, x, -110, 0, pop_scale(k)):
            K.dot(c, 0, 0, 70, K.tint(col, 0.5))
            K.dot(c, 0, -14, 30, K.SKIN)
            K.rr(c, 0, 40, 80, 40, 20, col)
            M.tag(c, 0, 110, 56, code, col, 1)
    k = M.appear(g, 6, 0.3)
    if k > 0:
        K.icon(c, "cross", 0, 150, 110, K.RED, clamp01(k * 3), 0.5, 0, pop_scale(k))
        K.text(c, "类型不合", 0, 250, 40, "serif_black", K.RED, k)


# ---------------------------------------------------------------- 3 标签贴满身

STUCK = [("INTJ", -40, -150, -12, 1), ("I 人", 70, -40, 10, 3), ("不合群", -50, 60, 6, 5)]


def stickers(c, g, t, d):
    for text, x, y, rot, b in STUCK:
        k = M.appear(g, b, 0.25)
        if k > 0:
            M.tag(c, x, y, 62, text, (K.HERO, K.OTHER3, K.RED)[STUCK.index((text, x, y, rot, b))], 1, rot,
                  1 + 0.5 * (1 - ease_out(k)))


# ---------------------------------------------------------------- 4 drop：语言 vs 标签

def lang_vs_label(c, g, t, d):
    k1 = M.appear(g, 4, 0.3)
    if k1 > 0:
        with K.at(c, -230, 0, 0, pop_scale(k1)):
            K.bubble(c, 0, 0, "语言", 64, (0, 1), k1)
            K.icon(c, "check", 0, 170, 90, K.GREEN, k1, 0.5)
    k2 = M.appear(g, 8, 0.3)
    if k2 > 0:
        with K.at(c, 230, 0, 0, pop_scale(k2)):
            M.tag(c, 0, 0, 110, "标签", K.INK2, k2, -6)
            K.icon(c, "cross", 0, 170, 90, K.RED, k2, 0.5)


# ---------------------------------------------------------------- 5 招聘筛选

def hiring_card(c, g, t, d):
    def draw(c, w, h):
        K.text(c, "招聘筛选", 0, -h / 2 + 70, 44, "serif_black", K.INK)
        for i, (code, ok) in enumerate((("ENTJ", True), ("INFP", False), ("ESTJ", True))):
            y = -h / 2 + 160 + i * 80
            K.dot(c, -w / 2 + 70, y, 24, K.LINE)
            K.text(c, "候选人 " + "ABC"[i], -w / 2 + 110, y, 34, "sans_medium", K.INK2, 1, "left")
            K.text(c, code, w / 2 - 110, y, 34, "black", K.INK3, 1, "right")
            K.icon(c, "check" if ok else "cross", w / 2 - 60, y, 44, K.INK3, 1, 0.3)

    K.card(c, 0, 0, 560, 420, K.PAPER, 1, 22, 1.0, 0, 1, K.INK2, draw)
    k = M.appear(g, 4, 0.25)
    if k > 0:
        with K.at(c, 0, 0, 0, 1 + 0.6 * (1 - ease_out(k))):
            K.seg(c, -230, -170, 230, 170, K.RED, 26, k)
            K.seg(c, 230, -170, -230, 170, K.RED, 26, k)
    M.stamp(c, 0, 290, 200, "不道德", K.RED, 1, M.appear(g, 6, 0.25), -4)


# ---------------------------------------------------------------- 6 每种类型都能做任何工作

JOBS = [("INTJ", K.HERO, "brief"), ("ESFP", K.OTHER3, "megaphone"), ("ISFJ", K.OTHER2, "heart"), ("ENTP", "#9C8FB0", "bulb")]


def all_jobs(c, g, t, d):
    for i, (code, col, ic) in enumerate(JOBS):
        x = -390 + i * 260
        K.figure(c, x, 0, 270, "stand", col, mood="smile", lift=0.6, face=1 if x < 0 else -1,
                 hair=("short", "long", "bun", None)[i])
        M.tag(c, x, -360, 54, code, col, 1)
        k = M.appear(g, 2 + 2 * i, 0.3)
        if k > 0:
            K.icon(c, ic, x, -480, 90, col, clamp01(k * 3), 0.6, 0, pop_scale(k), accent=K.GOLD)


# ---------------------------------------------------------------- 7 职业与伴侣

def couple_heart(c, g, t, d):
    k = M.appear(g, 6, 0.35)
    if k > 0:
        with K.at(c, 0, 0, 0, pop_scale(k) * M.pulse(g, [6, 8, 10], 0.1)):
            K.heart(c, 0, 0, 130, K.RED, k)


# ---------------------------------------------------------------- 8 对应大五

BIG5 = [("E", "I", "外向性"), ("S", "N", "开放性"), ("T", "F", "宜人性"), ("J", "P", "尽责性")]


def big_five_map(c, g, t, d):
    for i, (a, b, name) in enumerate(BIG5):
        k = M.appear(g, 2 + 2 * i, 0.35)
        if k <= 0:
            continue
        y = -330 + i * 190
        with K.fade(c, clamp01(k * 2.5)):
            M.tile(c, -360, y, 100, a)
            M.tile(c, -240, y, 100, b)
            K.arrow(c, (-160, y), (20, y), K.INK3, 8, 1, ease_out(k), 0, 24)
            K.text_card(c, 230, y, [name], 50, 340, K.PAPER, K.INK, ACC, 1, 0, 1, ACC, "serif", 0.7)


# ---------------------------------------------------------------- 9 第五个维度

def fifth_missing(c, g, t, d):
    names = ["外向性", "开放性", "宜人性", "尽责性", "情绪稳定性"]
    for i, n in enumerate(names):
        y = -340 + i * 150
        if i < 4:
            K.text_card(c, 0, y, [n], 44, 420, K.PAPER, K.INK, ACC, 1, 0, 1, None, "serif", 0.6)
            K.icon(c, "check", 260, y, 60, K.GREEN, 1, 0.4)
        else:
            k = M.appear(g, 2, 0.3)
            K.rr_stroke(c, 0, y, 420, 100, 22, K.RED if k > 0 else K.INK3, 5, 1, (16, 12))
            K.text(c, n, 0, y, 44, "serif", K.INK3, 1)
            if k > 0:
                K.icon(c, "question", 260, y, 70, K.RED, clamp01(k * 3), 0.4, 0, pop_scale(k))
                K.pill(c, -330, y, "没测", 30, K.RED, K.PAPER, k)


# ---------------------------------------------------------------- 12 差异是天赋

def gifts_row(c, g, t, d):
    k = 1 - ease_out(clamp01(g.since(3) / 0.4))
    if k > 0:
        K.icon(c, "ladder", 0, -560, 200, K.INK3, k, 0.6)
        q = M.appear(g, 2, 0.25)
        if q > 0:
            K.icon(c, "cross", 70, -520, 90, K.RED, q * k, 0.5, 0, pop_scale(q))
    for i, (code, col, _) in enumerate(JOBS):
        x = -390 + i * 260
        kk = M.appear(g, 4 + 2 * i, 0.3)
        K.figure(c, x, 0, 260, "stand" if kk <= 0 else "carry", col, mood="smile" if kk <= 0 else "happy", lift=0.6,
                 face=1 if x < 0 else -1, hair=("short", "long", "bun", None)[i])
        if kk > 0:
            K.icon(c, "gift", x, -330, 100, col, clamp01(kk * 3), 0.6, 0, pop_scale(kk), accent=K.GOLD)
            M.tag(c, x, -440, 48, code, col, clamp01(kk * 3))


# ---------------------------------------------------------------- 13 改写句子

def rewrite(c, g, t, d):
    a_old = 1 - 0.5 * clamp01(g.since(4) / 0.3)
    K.text_card(c, 0, -180, ["我是 I 人，", "所以不去聚会。"], 48, 640, K.PAPER, K.INK2, ACC, a_old, -2)
    s = ease_out(clamp01(g.since(4) / 0.3))
    if s > 0:
        K.seg(c, -230, -180, -230 + 460 * s, -200, K.RED, 9)
    k = clamp01(g.since(8) / 0.4)
    if k > 0:
        K.text_card(c, 0, 140, ["我更喜欢【小聚】，", "大聚会后要【独处充电】。"], 48, 720, K.PAPER, K.INK, ACC, k, 1.5,
                    0.6 + 0.4 * K.ease_out_back(k, 1.6), accent=ACC)


# ---------------------------------------------------------------- 14 撕下标签

def chest_tag(c, g, t, d):
    """主角胸前的类型牌：第 6 拍被撕下，翻转着落到地上。"""
    q = g.since(6)
    if q < 0:
        M.tag(c, 0, 0, 80, "INTJ", K.INK2, 1)
        return
    k = clamp01(q / 0.6)
    x = 160 * ease_out(k)
    y = -60 * math.sin(k * math.pi) + 230 * ease_in(k)
    rot = 200 * k
    M.tag(c, x, y, 80, "INTJ", K.INK2, 1 - 0.5 * k, rot)


def build() -> Episode:
    shots = [
        # 1
        Shot(3, "求职表上写着：|“请填写你的 MBTI”", "情境演绎", [
            Custom(job_form, x=640, y=650, at=0, enter="pop", sfx="wood_low", note="求职登记表出现"),
            Fig(200, GROUND, 320, at=0, mood="calm", hair="short",
                moves=[(6, dict(mood="worried", pose="think", sfx="rim", note="MBTI 一栏被红框圈出，主角皱眉"))]),
        ], draw=ground, hits=[(1, "wood_high", 0.6, "填上姓名"), (3, "wood_low", 0.6, "填上学历")],
            note="求职登记表：姓名、学历按拍填好，第 6 拍“MBTI”一栏被红框圈出，主角皱眉"),
        # 2
        Shot(3, "约会软件提醒你：|“你们类型不合。”", "情境演绎", [
            Custom(dating_phone, x=540, y=700, at=0, enter="pop"),
        ], hits=[(1, "wood_high", 0.8, "INTJ 头像"), (3, "wood_low", 0.8, "ESFP 头像"), (6, "tom", 0.9, "红叉：类型不合")],
            note="手机上两个头像 INTJ 和 ESFP 按拍出现，第 6 拍弹出红叉“类型不合”"),
        # 3
        Shot(2, "四个字母，|在替我们做决定？", "情境演绎", [
            Fig(540, GROUND, 360, at=0, enter="none", mood="sad", pose="sad", hair="short"),
            Custom(stickers, x=560, y=GROUND - 0.66 * 360 + 60, at=0, enter="none"),
        ], draw=ground, hits=[(1, "wood_high", 0.8, "贴上 INTJ"), (3, "wood_low", 0.8, "贴上 I 人"),
                              (5, "bongo_low", 0.8, "贴上不合群")], text_beat=0,
            note="主角身上按拍被贴满标签：INTJ、I 人、不合群"),
        # 4  drop
        Shot(3, "它是描述偏好的语言，|不是给人定型的标签。", "机制示意", [
            Big("正确使用", 540, 470, 150, at=0, sfx="kick", sub="a language, not a label", note="概念落版（音乐 drop）"),
            Custom(lang_vs_label, x=540, y=880, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.9, "语言：打勾"), (8, "rim", 0.9, "标签：打叉")],
            note="drop 处“正确使用”砸下；左边“语言”气泡打勾，右边“标签”牌打叉"),
        # 5
        Shot(3, "出版方：用 MBTI|筛选求职者，不道德。", "官方说明", [
            Custom(hiring_card, x=540, y=760, at=0, enter="pop", sfx="wood_low", note="“招聘筛选”表出现"),
            Txt("The Myers-Briggs Company 声明", 540, 1200, 28, at=2, font="sans_medium", color=K.INK2),
        ], hits=[(4, "rim", 1.0, "大红叉划掉"), (6, "frame", 0.9, "盖下“不道德”")],
            note="一张按类型打勾打叉的“招聘筛选”表，第 4 拍被红叉划掉，第 6 拍盖下“不道德”"),
        # 6
        Shot(3, "测不测应当自愿；|每种类型，都能做任何工作。", "官方说明", [
            Custom(all_jobs, x=540, y=GROUND, at=0, enter="fade"),
        ], draw=ground, hits=[(2, "wood_high", 0.8, "INTJ 拿起公文包"), (4, "wood_low", 0.8, "ESFP 拿起话筒"),
                              (6, "bongo_high", 0.8, "ISFJ 举起爱心"), (8, "bongo_low", 0.8, "ENTP 点亮灯泡")],
            note="四个不同类型的人站成一排，头顶按拍出现各自的工作图标"),
        # 7
        Shot(3, "类型，决定不了|你的职业和伴侣。", "常见误解", [
            Fig(400, GROUND, 330, at=0, mood="smile", hair="short", color=K.HERO, face=1,
                moves=[(6, dict(pose="hug", mood="happy"))]),
            Fig(680, GROUND, 320, at=0, mood="smile", hair="long", color=K.OTHER3, face=-1,
                moves=[(6, dict(pose="hug", mood="happy"))]),
            Custom(lambda c, g, t, d: M.tag(c, 0, 0, 56, "INTJ", K.HERO, 1), x=400, y=640, at=1, enter="pop",
                   sfx="wood_high", note="INTJ"),
            Custom(lambda c, g, t, d: M.tag(c, 0, 0, 56, "ESFP", K.OTHER3, 1), x=680, y=650, at=2, enter="pop",
                   sfx="wood_low", note="ESFP"),
            Custom(couple_heart, x=540, y=520, at=0, enter="none"),
        ], draw=ground, hits=[(6, "clap", 0.9, "两人相拥，爱心升起")],
            note="被判“类型不合”的 INTJ 和 ESFP 走到一起，第 6 拍相拥，爱心跳动"),
        # 8
        Shot(4, "四个维度，能在|“大五人格”里找到对应。", "研究证据", [
            Custom(big_five_map, x=540, y=820, at=0, enter="none"),
            Txt("McCrae & Costa，1989", 540, 1200, 28, at=2, font="sans_medium", color=K.INK2),
        ], hits=[(2, "wood_high", 0.8, "E-I → 外向性"), (4, "wood_low", 0.8, "S-N → 开放性"),
                 (6, "bongo_high", 0.8, "T-F → 宜人性"), (8, "bongo_low", 0.8, "J-P → 尽责性")],
            research=True, note="四对字母按拍连出箭头：E-I→外向性、S-N→开放性、T-F→宜人性、J-P→尽责性"),
        # 9
        Shot(2, "情绪稳定性，|MBTI 没有测。", "研究证据", [
            Custom(fifth_missing, x=540, y=800, at=0, enter="pop", sfx="wood_low", note="大五的五个维度"),
        ], hits=[(2, "rim", 0.9, "第五格：没测")], text_beat=0,
            note="大五人格五个维度依次排开，前四个打勾，第五个“情绪稳定性”是空的虚线框"),
        # 10
        Shot(2, "迈尔斯把她的书|取名《天生不同》。", "迈尔斯原著", [
            Custom(lambda c, g, t, d: M.book(c, 0, 0, 420, "天生|不同", ACC, 1, "1980", -3),
                   x=540, y=800, at=0, enter="pop", sfx="tom", note="《天生不同》出现"),
            Txt("Isabel Briggs Myers · Gifts Differing", 540, 1120, 32, at=1, font="sans_medium", color=K.INK2),
        ], hits=[(4, "shaker", 0.6, "书页微微发光")], text_beat=0, note="迈尔斯的书《天生不同》（Gifts Differing，1980）立在画面中央"),
        # 11
        Shot(3, "差异是天赋，|不是等级。", "机制示意", [
            Custom(gifts_row, x=540, y=GROUND, at=0, enter="fade"),
        ], draw=ground, hits=[(2, "rim", 0.8, "梯子打叉：没有高低"), (4, "wood_high", 0.8, "第一个人拿到礼物"),
                              (6, "wood_low", 0.8, "第二个人"), (8, "bongo_high", 0.8, "第三个人"),
                              (10, "bongo_low", 0.8, "第四个人")],
            note="代表“高低等级”的梯子被打叉淡去，四个不同类型的人站在同一地面上，按拍各自捧起礼物"),
        # 12
        Shot(3, "把“我是 X 型所以……”|换成具体的偏好。", "小练习", [
            Custom(rewrite, x=540, y=780, at=0, enter="pop", sfx="wood_low", note="旧句子出现"),
        ], hits=[(4, "rim", 0.9, "旧句子被划掉"), (8, "bongo_high", 0.9, "新句子翻上来")],
            note="“我是 I 人，所以不去聚会”被划掉，换成“我更喜欢小聚，大聚会后要独处充电”"),
        # 13
        Shot(4, "撕下标签，|留下对自己的理解。", "机制示意", [
            Fig(540, GROUND, 380, at=0, enter="none", mood="calm", hair="short",
                moves=[(6, dict(pose="reach", sfx="rim", note="主角撕下胸前的类型牌")),
                       (9, dict(pose="cheer", mood="happy", sfx="clap", note="主角舒展欢呼"))]),
            Custom(chest_tag, x=550, y=GROUND - 0.66 * 380, at=0, enter="none"),
        ], draw=ground, over=lambda g: K.burst(g.c, 540, 760, g.since(9), K.GOLD, 120, 280, 12, 8)
            if 0 <= g.since(9) <= 0.6 else None,
            note="主角胸前挂着“INTJ”牌，第 6 拍把它撕下、牌子翻落在地，第 9 拍主角舒展欢呼"),
        # 14
        Shot(2, "四个字母，|是认识彼此的语言。", "机制示意", [
            Fig(330, GROUND, 330, at=0, mood="smile", hair="short", face=1),
            Fig(750, GROUND, 320, at=0, mood="smile", hair="long", color=K.OTHER3, face=-1),
            Bubble("我需要独处充电", 300, 560, 38, at=1, sfx="wood_high", note="主角说出自己的偏好"),
            Bubble("我喜欢热闹", 780, 640, 38, at=3, tail=(0, 1), sfx="wood_low", note="对方也说出偏好"),
            Icon("heart", 540, 800, 110, color=K.RED, at=5, enter="pop", sfx="clap", note="两人之间亮起爱心"),
        ], draw=ground, text_beat=0, note="两个人各自说出自己的偏好，中间亮起一颗心"),
        end_shot(REFS_SHORT, None),
    ]
    return Episode(10, "use", "正确使用", "四个字母，是标签还是语言？", ACC, shots, refs=REFS,
                   publish_title="四个字母，是标签还是语言？｜MBTI科普10 正确使用",
                   hashtags="#MBTI #心理学 #大五人格 #人格测试 #科普",
                   cover_title="四个字母，|是【标签】还是语言？", cover_sub="MBTI 的正确用法", cover_shot=12, cover_t=5.0,
                   notes=[
                       "出版方 The Myers-Briggs Company（原 CPP）的立场：用 MBTI 做招聘或选拔是不道德的，施测必须自愿；"
                       "MBTI 的设计前提是所有类型都能胜任各种工作（官方博客与 2013 年 CPP 声明）。",
                       "McCrae & Costa（1989）：MBTI 的 E-I、S-N、T-F、J-P 分别与大五人格的外向性、开放性、宜人性、尽责性对应；"
                       "MBTI 没有测到神经质（情绪稳定性）。",
                       "《天生不同》（Gifts Differing，1980）为伊莎贝尔·迈尔斯与 Peter B. Myers 合著；“差异是天赋，不是等级”是对书名的概括，不是原句。",
                       "第 1、2 镜的求职表与约会软件为情境演绎；第 5 镜的筛选表为示意。",
                       "第 12 镜改写练习为本系列设计的小练习。",
                   ], **SERIES).build()
