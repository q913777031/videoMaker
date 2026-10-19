"""08 巴纳姆效应：为什么人格测试，总觉得说得准？"""

import math

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Episode, Fig, Shot, Txt, end_shot

from . import kit_mbti as M

ACC = "#D06A4C"
GROUND = 1130
SERIES = dict(series="MBTI 科普", file_prefix="MBTI")
REFS = ["Forer, B. R. (1949). The fallacy of personal validation: a classroom demonstration of gullibility. "
        "J. Abnormal and Social Psychology, 44(1), 118–123."]
LINES = ["你渴望被人理解。", "你有时外向，有时内向。", "你还有没发挥的潜力。"]


def ground(g):
    K.ground(g.c, GROUND)


# ---------------------------------------------------------------- 1 读报告点头

def my_report(c, g, t, d):
    nods = [(i, M.appear(g, 2 + 3 * i, 0.3)) for i in range(3)]
    hi = [(i, ease_out(clamp01(g.since(1.5 + 3 * i) / 0.5))) for i in range(3)]
    M.report(c, 0, 0, 640, LINES, hi, 1, 38, "你的人格报告", ACC, nods)


# ---------------------------------------------------------------- 3 两份报告一样

def twin_reports(c, g, t, d):
    M.report(c, -230, 0, 420, ["渴望被理解", "有时外向", "有潜力"], (), 1, 32, "小林的报告", ACC)
    M.report(c, 230, 0, 420, ["渴望被理解", "有时外向", "有潜力"], (), 1, 32, "小周的报告", K.HERO)
    k = M.appear(g, 4, 0.3)
    if k > 0:
        with K.at(c, 0, 0, 0, 0.4 + 0.6 * K.ease_out_back(k, 2)):
            K.dot(c, 0, 0, 52, K.RED, k)
            K.text(c, "=", 0, -4, 80, "black", K.PAPER, k)


# ---------------------------------------------------------------- 4 drop：人人点头

def everyone_nods(c, g, t, d):
    """同一份报告悬在中间，下面一排四个人按拍点头打勾。"""
    M.report(c, 540, 700, 420, ["渴望被理解", "有时外向"], (), 1, 30, "人格报告", ACC)
    xs = (190, 420, 660, 890)
    for i, x in enumerate(xs):
        k = M.appear(g, 4 + 2 * i, 0.3)
        K.figure(c, x, GROUND, 200, "cheer" if k > 0.5 else "stand", (K.OTHER, K.OTHER2, K.OTHER3, K.HERO)[i],
                 alpha=1, face=1 if x < 540 else -1, mood="happy" if k > 0 else "calm", lift=0.6,
                 hair=("bun", None, "long", "short")[i])
        if k > 0:
            K.icon(c, "check", x, GROUND - 270, 62, K.GREEN, clamp01(k * 3), 0.5, 0, 0.3 + 0.7 * K.ease_out_back(k, 2))


# ---------------------------------------------------------------- 5 福勒的课堂

def classroom(g):
    c = g.c
    K.ground(c, GROUND)
    K.rr(c, 300, 640, 420, 250, 14, "#3F5A4E")
    K.rr_stroke(c, 300, 640, 420, 250, 14, "#A0784F", 10)
    K.text(c, "人格测验", 300, 610, 46, "serif_black", K.PAPER)
    K.text(c, "1949", 300, 680, 40, "black", K.tint(K.GOLD, 0.2))


def students(c, g, t, d):
    K.crowd(c, 0, 0, 8, 210, g.t, spread=420, seed=7, rows=2, face_to=-600)


def head_count(c, g, t, d):
    k = M.appear(g, 6, 0.3)
    if k > 0:
        with K.at(c, 0, 0, 0, 0.4 + 0.6 * K.ease_out_back(k, 2)):
            K.dot(c, 0, 0, 90, ACC, k)
            K.text(c, "39", 0, -14, 76, "black", K.PAPER, k)
            K.text(c, "个学生", 0, 44, 26, "sans_medium", K.PAPER, k)


# ---------------------------------------------------------------- 6 “专属”报告

def same_reports(c, g, t, d):
    xs = (-360, -120, 120, 360)
    for i, x in enumerate(xs):
        k = M.appear(g, i, 0.3)
        if k <= 0:
            continue
        rot = (-4, 3, -2, 4)[i]
        with K.at(c, x, (1 - ease_out(k)) * -120, rot, 1):
            K.card(c, 0, 0, 210, 300, K.PAPER, clamp01(k * 3), 16, 0.8, 0, 1, ACC)
            K.text(c, f"学生 {i + 1}", 0, -100, 26, "sans_medium", K.INK2, clamp01(k * 3))
            for j in range(4):
                same = M.appear(g, 6, 0.4)
                col = K.mix(K.LINE, K.tint(ACC, 0.4), same)
                K.rr(c, 0, -40 + j * 46, 150 - (j % 2) * 30, 16, 8, col, clamp01(k * 3))
    k = M.appear(g, 8, 0.3)
    if k > 0:
        M.stamp(c, 0, 230, 200, "同一份", K.RED, 1, k, -6)


# ---------------------------------------------------------------- 7 平均 4.26 分

def score_meter(c, g, t, d):
    w = 760
    fill = ease_out(clamp01(g.since(3) / 1.2)) * 4.26 / 5
    K.rr(c, 0, 0, w, 70, 35, K.LINE)
    if fill > 0:
        K.rr(c, -w / 2 + w * fill / 2, 0, w * fill, 70, 35, ACC)
    for i in range(6):
        x = -w / 2 + w * i / 5
        K.text(c, str(i), x, 80, 34, "sans_medium", K.INK2)
    K.text(c, "0 = 完全不准", -w / 2, -80, 28, "sans_medium", K.INK3, 1, "left")
    K.text(c, "5 = 非常准", w / 2, -80, 28, "sans_medium", K.INK3, 1, "right")
    k = M.appear(g, 6, 0.3)
    if k > 0:
        with K.at(c, w * (4.26 / 5 - 0.5), -230, 0, 0.4 + 0.6 * K.ease_out_back(k, 2)):
            K.text(c, "4.26", 0, 0, 130, "black", ACC, k, shadow=(4, 8, 8, K.SHADOW))
            K.text(c, "平均分", 0, 92, 32, "sans_medium", K.INK2, k)


# ---------------------------------------------------------------- 8 星座书

def horoscope_source(c, g, t, d):
    M.book(c, -260, 0, 330, "星座|运势", "#6E5A9A", 1, "报摊上买的", 4)
    k = M.appear(g, 2, 0.5)
    if k > 0:
        K.arrow(c, (-90, -30), (110, -30), ACC, 10, 1, k, -0.2, 30)
    M.report(c, 300, 0, 330, ["渴望被理解", "有时外向", "有潜力"], (), M.appear(g, 3, 0.3), 30, "人格报告", ACC)


# ---------------------------------------------------------------- 9 三个特点

def three_traits(c, g, t, d):
    items = [("模糊", "说什么都沾点边"), ("正面", "听着让人舒服"), ("两头都说", "外向也说，内向也说")]
    for i, (a, b) in enumerate(items):
        k = M.appear(g, 1 + 2 * i, 0.3)
        if k <= 0:
            continue
        y = -220 + i * 220
        with K.at(c, (1 - ease_out(k)) * 200, y):
            with K.fade(c, clamp01(k * 3)):
                K.pill(c, -200, 0, a, 46, ACC, K.PAPER)
                K.text(c, b, 30, 0, 40, "serif", K.INK, 1, "left")


# ---------------------------------------------------------------- 10 人人点头

def crowd_checks(c, g, t, d):
    xs = (-380, -190, 0, 190, 380)
    for i, x in enumerate(xs):
        k = M.appear(g, (4, 5, 6, 7, 10)[i], 0.3)
        K.figure(c, x, 0, 250, "stand", (K.OTHER, K.OTHER2, K.HERO, K.OTHER3, "#9C8FB0")[i], alpha=1,
                 face=1 if x <= 0 else -1, mood="happy" if k > 0 else "calm", lift=0.6,
                 hair=("bun", None, "short", "long", None)[i])
        if k > 0:
            K.icon(c, "check", x, -330, 70, K.GREEN, clamp01(k * 3), 0.5, 0, 0.3 + 0.7 * K.ease_out_back(k, 2))


# ---------------------------------------------------------------- 11 选择性记忆

MEMO = ["你渴望被理解", "你做事很有条理", "你有没发挥的潜力", "你从不在意别人", "你有时需要独处"]
HIT = (0, 2, 4)


def selective(c, g, t, d):
    w, size = 640, 40
    h = len(MEMO) * size * 1.9 + 80

    def draw(c, w_, h_):
        for i, ln in enumerate(MEMO):
            y = -h_ / 2 + 70 + i * size * 1.9
            if i in HIT:
                k = M.appear(g, 2 + 2 * HIT.index(i), 0.3)
                if k > 0:
                    tw = K.text_w(ln, size, "serif")
                    K.rr(c, -w_ / 2 + 50 + tw * k / 2, y + 6, tw * k + 10, size * 0.45, 8, K.tint(ACC, 0.55), 0.9)
                K.text(c, ln, -w_ / 2 + 50, y, size, "serif", K.INK, 1, "left")
                if k > 0:
                    K.icon(c, "check", w_ / 2 - 56, y, 48, K.GREEN, clamp01(k * 3), 0.4, 0,
                           0.3 + 0.7 * K.ease_out_back(k, 2))
            else:
                fade = 1 - 0.8 * ease_out(clamp01(g.since(8) / 0.6))
                K.text(c, ln, -w_ / 2 + 50, y, size, "serif", K.INK3, fade, "left")

    K.card(c, 0, 0, w, h, K.PAPER, 1, 22, 1.0, 0, 1, ACC, draw)


# ---------------------------------------------------------------- 12 觉得准 ≠ 测得准

def not_equal(c, g, t, d):
    k1, k2, k3 = M.appear(g, 1, 0.3), M.appear(g, 3, 0.3), M.appear(g, 6, 0.25)
    if k1 > 0:
        with K.at(c, -250, 0, 0, 0.4 + 0.6 * K.ease_out_back(k1, 2)):
            K.card(c, 0, 0, 340, 340, K.PAPER, k1, 26, 1.0)
            K.heart(c, 0, -40, 130, ACC, k1)
            K.text(c, "觉得准", 0, 100, 52, "serif_black", K.INK, k1)
    if k2 > 0:
        with K.at(c, 250, 0, 0, 0.4 + 0.6 * K.ease_out_back(k2, 2)):
            K.card(c, 0, 0, 340, 340, K.PAPER, k2, 26, 1.0)
            K.icon(c, "target", 0, -40, 150, K.HERO, k2, 0.5)
            K.text(c, "测得准", 0, 100, 52, "serif_black", K.INK, k2)
    if k3 > 0:
        with K.at(c, 0, 0, 0, 1 + 0.6 * (1 - ease_out(k3))):
            K.dot(c, 0, 0, 62, K.RED, k3)
            K.text(c, "≠", 0, -6, 90, "black", K.PAPER, k3)


# ---------------------------------------------------------------- 13 念给朋友听

def read_scene(g):
    ground(g)


# ---------------------------------------------------------------- 14 说中所有人

def everyone_nobody(c, g, t, d):
    M.report(c, 0, 0, 380, ["渴望被理解", "有时外向"], (), 1, 30, "人格报告", ACC)
    n = 8
    for i in range(n):
        k = M.appear(g, 0.5 * i, 0.3)
        if k <= 0:
            continue
        a = math.tau * i / n - math.pi / 2
        x, y = 360 * math.cos(a), 330 * math.sin(a)
        fade = 1 - 0.7 * ease_out(clamp01(g.since(5) / 0.6))
        K.icon(c, "check", x, y, 64, K.GREEN, clamp01(k * 3) * fade, 0.4, 0, 0.3 + 0.7 * K.ease_out_back(k, 2))


def build() -> Episode:
    shots = [
        # 1
        Shot(3, "测完人格，读报告：|“这说的就是我！”", "情境演绎", [
            Fig(190, GROUND, 330, at=0, mood="calm", hair="short", pose="carry",
                moves=[(2, dict(mood="smile")), (8, dict(mood="happy", pose="cheer", sfx="clap",
                                                         note="主角拍手：这就是我！"))]),
            Custom(my_report, x=640, y=720, at=0, enter="pop"),
        ], draw=ground, hits=[(2, "wood_high", 0.8, "第一句打勾"), (5, "wood_low", 0.8, "第二句打勾")],
            note="主角读人格报告，三句话按拍一句句高亮、打勾，第 8 拍主角举手：这就是我！"),
        # 2
        Shot(3, "朋友测完也说：|“太准了，就是我！”", "情境演绎", [
            Fig(230, GROUND, 320, at=0, mood="calm", color=K.OTHER3, hair="long", pose="carry",
                moves=[(2, dict(mood="happy"))]),
            Fig(850, GROUND, 320, at=0, mood="calm", color=K.OTHER2, face=-1, pose="carry",
                moves=[(6, dict(mood="happy"))]),
            Fig(540, GROUND, 300, at=0, mood="smile", hair="short",
                moves=[(9, dict(mood="surprised", pose="shrug", sfx="tom", note="主角愣住：怎么都说准？"))]),
            Bubble("太准了！", 260, 560, 48, at=2, sfx="wood_high", note="朋友一：太准了"),
            Bubble("就是我！", 820, 520, 48, at=6, tail=(-0.3, 1), sfx="bongo_high", note="朋友二：就是我"),
        ], draw=ground, note="两个朋友各拿一份报告，按拍喊“太准了”“就是我”，中间的主角愣住"),
        # 3
        Shot(2, "可你们俩，|拿到的几乎是同一份。", "情境演绎", [
            Custom(twin_reports, x=540, y=760, at=0, enter="pop", sfx="wood_low", note="两份报告并排"),
        ], hits=[(4, "rim", 0.9, "等号弹出")], note="两份报告并排，内容一模一样，第 4 拍中间弹出等号"),
        # 4  drop
        Shot(3, "把人人适用的描述，|当成在说自己。", "机制示意", [
            Big("巴纳姆效应", 540, 450, 140, at=0, sfx="kick", sub="Barnum effect / Forer effect",
                note="概念落版（音乐 drop）"),
            Custom(everyone_nods, x=0, y=0, at=0, enter="none"),
        ], draw=ground, hits=[(4, "wood_high", 0.8, "左上的人点头"), (6, "wood_low", 0.8, "右上的人点头"),
                 (8, "bongo_high", 0.8, "左下的人点头"), (10, "bongo_low", 0.8, "右下的人点头")],
            note="drop 处“巴纳姆效应”砸下；同一份报告周围的四个人按拍一个个点头打勾"),
        # 5
        Shot(3, "1949 年，心理学家福勒|给学生做了人格测验。", "研究证据", [
            Fig(300, GROUND, 330, at=0, mood="calm", color=K.DARK, pose="point", face=1),
            Custom(students, x=760, y=GROUND, at=0, enter="fade"),
            Custom(head_count, x=760, y=560, at=0, enter="none"),
        ], draw=classroom, hits=[(2, "wood_low", 0.7, "黑板写着人格测验"), (6, "bongo_high", 0.9, "39 个学生")],
            research=True, note="教室里，福勒站在黑板前，右边坐着学生，第 6 拍弹出“39 个学生”"),
        # 6
        Shot(3, "每人拿到一份“专属”报告，|其实内容一模一样。", "研究证据", [
            Custom(same_reports, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.7, "第一份报告发下"), (3, "wood_low", 0.7, "第四份报告发下"),
                 (6, "shaker", 0.8, "所有报告的内容同时变色"), (8, "frame", 0.9, "“同一份”印章盖下")],
            research=True, note="四份写着不同学生名字的报告依次发下，第 6 拍内容同时变色，第 8 拍盖下“同一份”"),
        # 7
        Shot(3, "满分 5 分，学生们|平均打了 4.26 分。", "研究证据", [
            Custom(score_meter, x=540, y=880, at=0, enter="pop"),
            Txt("Forer，1949", 540, 1150, 30, at=2, font="sans_medium", color=K.INK2),
        ], hits=[(3, "shaker", 0.7, "进度条开始增长"), (6, "kick", 0.8, "4.26 弹出")],
            research=True, note="0–5 分的进度条一路涨到 4.26，第 6 拍大字“4.26”弹出"),
        # 8
        Shot(2, "那些句子，其实|摘自报摊买的星座书。", "研究证据", [
            Custom(horoscope_source, x=540, y=800, at=0, enter="pop", sfx="wood_low", note="星座书出现"),
        ], hits=[(2, "rim", 0.8, "箭头从星座书指向报告")], text_beat=0,
            note="左边一本星座运势书，箭头指向右边的“人格报告”"),
        # 9
        Shot(2, "这类句子：模糊、|正面、两头都说。", "机制示意", [
            Custom(three_traits, x=540, y=800, at=0, enter="none"),
        ], hits=[(1, "wood_high", 0.8, "模糊"), (3, "wood_low", 0.8, "正面"), (5, "bongo_high", 0.8, "两头都说")],
            text_beat=0, note="三条特点按拍从右滑入：模糊、正面、两头都说"),
        # 10
        Shot(3, "“你有时外向，|有时又需要独处。”", "机制示意", [
            Card("你有时外向，|有时又需要独处。", 540, 520, 46, at=0, enter="pop", accent=ACC, sfx="wood_low",
                 note="一句两头都说的描述"),
            Custom(crowd_checks, x=540, y=GROUND, at=0, enter="none"),
        ], draw=ground, hits=[(4, "wood_high", 0.7, "第一个人点头"), (6, "wood_low", 0.6, "第三个人点头"),
                              (10, "clap", 0.8, "所有人都点头")],
            note="一句“你有时外向，有时又需要独处”，下面五个人一个接一个点头打勾"),
        # 11
        Shot(3, "说中的记住了，|没说中的忘掉了。", "机制示意", [
            Custom(selective, x=540, y=780, at=0, enter="pop"),
        ], hits=[(2, "wood_high", 0.8, "说中的第一句打勾"), (4, "wood_low", 0.8, "说中的第二句打勾"),
                 (6, "bongo_high", 0.8, "说中的第三句打勾"), (8, "shaker", 0.8, "没说中的句子淡去")],
            note="一张五句话的报告，说中的三句按拍高亮打勾，第 8 拍没说中的两句淡去"),
        # 12
        Shot(4, "觉得准，|不等于测得准。", "常见误解", [
            Custom(not_equal, x=540, y=760, at=0, enter="none"),
        ], hits=[(1, "wood_high", 0.8, "“觉得准”卡片"), (3, "wood_low", 0.8, "“测得准”卡片"),
                 (6, "rim", 1.0, "不等号砸下")],
            note="左边“觉得准”（爱心），右边“测得准”（靶心），第 6 拍中间砸下不等号"),
        # 13
        Shot(4, "把报告念给朋友听：|像不像在说他自己？", "小练习", [
            Fig(300, GROUND, 340, at=0, mood="smile", hair="short", pose="carry",
                moves=[(2, dict(pose="give", sfx="wood_low", note="主角把报告念给朋友")),
                       (12, dict(pose="shrug", mood="happy", sfx="clap", note="主角摊手笑：果然人人适用"))]),
            Fig(780, GROUND, 330, at=0, mood="calm", color=K.OTHER3, face=-1, hair="long",
                moves=[(8, dict(mood="surprised", pose="point", sfx="bongo_high", note="朋友：这也像我啊！"))]),
            Card("你渴望被人理解。", 330, 600, 40, at=2, enter="pop", accent=ACC),
            Bubble("这也像我啊！", 800, 470, 46, at=8, tail=(0, 1)),
        ], draw=read_scene,
            note="主角把报告里的一句话念给朋友，第 8 拍朋友指着自己：这也像我啊！"),
        # 14
        Shot(2, "说中所有人的话，|也就没说中谁。", "机制示意", [
            Custom(everyone_nobody, x=540, y=780, at=0, enter="pop"),
        ], hits=[(0, "wood_high", 0.7, "勾号一圈圈冒出"), (5, "rim", 0.8, "勾号淡去")], text_beat=0,
            note="同一份报告周围冒出一圈勾号，随后一起淡去"),
        end_shot(REFS, "09 科学争议：MBTI，到底科学吗？"),
    ]
    return Episode(8, "barnum", "巴纳姆效应", "为什么人格测试，总觉得说得准？", ACC, shots, refs=REFS,
                   publish_title="为什么人格测试，总觉得说得准？｜MBTI科普08 巴纳姆效应",
                   hashtags="#MBTI #心理学 #巴纳姆效应 #人格测试 #科普",
                   cover_title="人格测试，|为什么总觉得【准】？", cover_sub="巴纳姆效应", cover_shot=3, cover_t=6.0,
                   notes=[
                       "Forer（1949）：39 名学生拿到同一份“个性描述”，按 0–5 分评价准确度，平均 4.26 分；描述取自报摊买的星座书，"
                       "福勒只稍作改写。论文发表于 Journal of Abnormal and Social Psychology 44(1):118–123。",
                       "巴纳姆效应也叫福勒效应；福勒本人称之为“个人验证谬误”（fallacy of personal validation）。",
                       "第 1、3、10、11 镜的报告句子为示意，不是福勒原文，也不是任何测试的原文。",
                       "本期讲的是“觉得准”这种主观感受为什么不可靠，不是说 MBTI 问卷等同于星座；MBTI 的测量问题见第 09 期。",
                   ], **SERIES).build()
