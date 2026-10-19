"""07 网络测试：你测的，真的是 MBTI 吗？"""

import math

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Label, Shot, end_shot

from . import kit_mbti as M

ACC = "#2F8A8A"
GROUND = 1130
SERIES = dict(series="MBTI 科普", file_prefix="MBTI")
REFS = ["16Personalities 官网对 NERIS Type Explorer 的说明",
        "The Myers & Briggs Foundation. Ethical use of the MBTI instrument",
        "The Myers-Briggs Company. Myers-Briggs history（官网时间线）"]


def ground(g):
    K.ground(g.c, GROUND)


def phone(c, x, y, s=1.0, content=None, alpha=1.0, rot=0.0):
    """大手机：content(c, w, h) 在屏幕坐标系（屏幕中心为原点）中绘制。"""
    w, h = 380 * s, 660 * s
    with K.at(c, x, y, rot):
        with K.paper(c, alpha, 1.1):
            K.rr(c, 0, 0, w, h, 50 * s, K.DARK)
        K.rr(c, 0, 0, w - 30 * s, h - 74 * s, 30 * s, K.PAPER, alpha)
        K.rr(c, 0, -h / 2 + 22 * s, 96 * s, 14 * s, 7 * s, K.INK, alpha)
        if content:
            with K.fade(c, alpha):
                content(c, w - 30 * s, h - 74 * s)


def model_box(c, x, y, name, color, out_code, k_in=1.0, k_out=1.0, sub=None):
    """一个“模型”黑箱：左边题目进，右边四字母出。"""
    with K.paper(c, 1, 0.9):
        K.rr(c, x, y, 300, 200, 26, color)
    K.text(c, name, x, y - 20, 46, "serif_black", K.PAPER)
    if sub:
        K.text(c, sub, x, y + 45, 28, "sans_medium", K.mix(color, K.PAPER, 0.75))
    if k_in > 0:
        K.arrow(c, (x - 330, y), (x - 160, y), K.INK3, 9, k_in, k_in, 0, 26)
        K.icon(c, "check", x - 370, y, 60, K.INK2, k_in, 0.3)
    if k_out > 0:
        K.arrow(c, (x + 160, y), (x + 260, y), K.INK3, 9, k_out, k_out, 0, 26)


# ---------------------------------------------------------------- 1 广告

def ad_screen(g):
    def draw(c, w, h):
        K.rr(c, 0, -150, w - 40, 260, 20, K.tint(ACC, 0.55))
        K.text(c, "免费", 0, -200, 70, "black", K.PAPER)
        K.text(c, "10 分钟", 0, -110, 52, "black", K.INK)
        K.text(c, "测出你的人格", 0, 30, 40, "serif_black", K.INK)
        K.text(c, "已有很多人参与", 0, 90, 26, "sans_medium", K.INK3)
        press = M.pulse(g, (8,), -0.12, 0.3)
        with K.at(c, 0, 200, 0, press):
            K.rr(c, 0, 0, 240, 80, 40, ACC)
            K.text(c, "开始测试", 0, 0, 34, "black", K.PAPER)
    return draw


def ad_phone(c, g, t, d):
    phone(c, 0, 0, 1.0, ad_screen(g))


# ---------------------------------------------------------------- 2 结果

def result_screen(c, g, t, d):
    def draw(c, w, h):
        q = sum(M.appear(g, b, 0.3) for b in (1, 2, 3, 4)) / 4
        if g.since(5.5) < 0:
            K.text(c, "第 %d / 60 题" % max(1, int(q * 60)), 0, -60, 34, "sans_medium", K.INK2)
            K.rr(c, 0, 0, w - 80, 26, 13, K.LINE)
            K.rr(c, -(w - 80) / 2 + (w - 80) * q / 2, 0, max(26, (w - 80) * q), 26, 13, ACC)
        else:
            K.text(c, "你的结果", 0, -200, 36, "serif_black", K.INK)
            prog = [M.appear(g, 6 + 0.5 * i, 0.3) for i in range(4)]
            M.code(c, 0, -60, 70, "INFJ", 1, 0.12, prog)
            k = M.appear(g, 8, 0.3)
            if k > 0:
                M.tag(c, 0, 80, 90, "-T", K.DARK, k, -6, 0.3 + 0.7 * K.ease_out_back(k, 2))
    phone(c, 0, 0, 1.0, draw)


# ---------------------------------------------------------------- 3 -T 是什么

def big_t(c, g, t, d):
    M.tag(c, 0, 0, 200, "-T", K.DARK, 1, -6)
    k = M.appear(g, 2, 0.3)
    if k > 0:
        with K.at(c, 200, -140, 0, 0.3 + 0.7 * K.ease_out_back(k, 2)):
            K.icon(c, "question", 0, 0, 130, ACC, k, 0.5)


# ---------------------------------------------------------------- 4 drop

def vs(c, g, t, d):
    def mini(c, w, h):
        M.code(c, 0, -40, 54, "INFJ", 1, 0.1)
        M.tag(c, 0, 80, 70, "-T", K.DARK, 1, -6)
    k1 = M.appear(g, 4, 0.3)
    if k1 > 0:
        phone(c, -240, 0, 0.62, mini, k1, -4)
    k2 = M.appear(g, 6, 0.3)
    if k2 > 0:
        M.book(c, 240, 0, 330, "MBTI|问卷", "#3B5B8C", k2, "官方", 4)
    k3 = M.appear(g, 8, 0.25)
    if k3 > 0:
        with K.at(c, 0, 0, 0, 1 + 0.4 * (1 - ease_out(k3))):
            K.text(c, "≠", 0, 0, 150, "black", K.RED, k3)


# ---------------------------------------------------------------- 5 自家模型

def own_model(c, g, t, d):
    model_box(c, -40, 0, "自家模型", ACC, None, M.appear(g, 2, 0.4), M.appear(g, 4, 0.4), "NERIS")
    k = M.appear(g, 4, 0.3)
    if k > 0:
        M.code(c, 340, 0, 50, "INFJ", k, 0.1)
    k = M.appear(g, 6, 0.35)
    if k > 0:
        K.text(c, "例：16Personalities", -40, -190, 40, "sans_medium", K.INK2, k)


# ---------------------------------------------------------------- 6 -A / -T

def fifth_dim(c, g, t, d):
    M.code(c, -110, 0, 150, "INFJ", 1, 0.15)
    k = M.appear(g, 6, 0.3)
    if k > 0:
        flip = int(max(0, g.since(9)) * 1.6) % 2
        M.tag(c, 400, 0, 140, "-T" if flip else "-A", K.DARK, k, -6, 0.3 + 0.7 * K.ease_out_back(k, 2))
        K.text(c, "第五维", 400, 140, 40, "serif_black", ACC, k)


# ---------------------------------------------------------------- 7 官方问卷没有

def official_four(c, g, t, d):
    M.book(c, -300, 0, 300, "MBTI|问卷", "#3B5B8C", 1, "官方", -3)
    M.code(c, 80, 0, 110, "INFJ", 1, 0.12)
    K.rr_stroke(c, 400, 0, 120, 110, 18, K.INK3, 5, 1, (14, 10))
    k = M.appear(g, 6, 0.3)
    if k > 0:
        with K.at(c, 400, 0, 0, 0.3 + 0.7 * K.ease_out_back(k, 2)):
            K.icon(c, "cross", 0, 0, 90, K.RED, k, 0.4)


# ---------------------------------------------------------------- 8 认证施测师

def session(g):
    ground(g)
    K.seat(g.c, 540, GROUND, 260, 160, K.mix(K.OTHER, K.PAPER, 0.4))


def report_sheet(c, g, t, d):
    k = M.appear(g, 3, 0.35)
    if k > 0:
        M.report(c, 0, 0, 320, ["偏好：I", "偏好：N", "……"], (), k, 26, "解读报告", ACC)


# ---------------------------------------------------------------- 9 看到 -A/-T

def warn_tags(c, g, t, d):
    M.code(c, -120, 0, 120, "ENFP", 1, 0.12)
    M.tag(c, 330, 0, 120, "-A", K.DARK, 1, -6)
    k = M.appear(g, 2, 0.3)
    if k > 0:
        K.ring(c, 330, 0, 120, K.RED, 9, k, k)
        K.text(c, "不是官方问卷的结果", 0, 200, 48, "serif_black", K.RED, k)


# ---------------------------------------------------------------- 10 两个模型

def two_models(c, g, t, d):
    for i, (name, col, y) in enumerate((("模型 A", ACC, -170), ("模型 B", "#3B5B8C", 170))):
        b = 2 + 4 * i
        model_box(c, -80, y, name, col, None, M.appear(g, b, 0.4), M.appear(g, b + 2, 0.4))
        k = M.appear(g, b + 2, 0.3)
        if k > 0:
            M.code(c, 330, y, 48, "INFJ", k, 0.1)


# ---------------------------------------------------------------- 11 计分不同

def two_scales(c, g, t, d):
    k = M.appear(g, 0, 0.3)
    for i, (lab, target) in enumerate((("测试 A", -0.15), ("测试 B", 0.2))):
        y = -150 + i * 300
        b = 2 + 4 * i
        q = ease_in_out(clamp01(g.since(b) / 0.5))
        K.text(c, lab, -390, y - 100, 36, "sans_medium", K.INK2, k, "left")
        M.scale_bar(c, 0, y, 780, "E", "I", target * q, k, None, 80)


# ---------------------------------------------------------------- 12 对不上

def mismatch(c, g, t, d):
    def scr(c, w, h):
        M.code(c, 0, -30, 60, "INFJ", 1, 0.1)
        M.tag(c, 0, 90, 70, "-T", K.DARK, 1, -6)
    phone(c, -240, 0, 0.68, scr, 1, -4)
    k = M.appear(g, 4, 0.35)
    if k > 0:
        K.card(c, 230, 0, 330, 300, K.PAPER, k, 22, 1, 4, 1, "#3B5B8C")
        K.text(c, "另一个测试", 230, -80, 30, "sans_medium", K.INK2, k)
        M.code(c, 230, 20, 56, "INFP", k, 0.1, None, False, [0, 0, 0, M.appear(g, 6, 0.4)])


# ---------------------------------------------------------------- 13 小练习：看一眼模型

def fine_print(c, g, t, d):
    def scr(c, w, h):
        K.text(c, "人格测试", 0, -220, 40, "serif_black", K.INK)
        for i in range(4):
            K.rr(c, 0, -130 + i * 50, w - 80, 18, 9, K.LINE)
        hk = M.appear(g, 8, 0.4)
        if hk > 0:
            K.rr(c, -10, 140, (w - 60) * ease_out(hk), 46, 10, K.tint(ACC, 0.5), 0.9)
        K.text(c, "本测试基于 ____ 模型", 0, 140, 32, "sans_medium", K.INK2)
        K.text(c, "关于本测试 · 方法说明", 0, 215, 28, "sans_medium", K.INK3)
    phone(c, 0, 0, 1.1, scr)
    # 放大镜从上往下扫，第 8 拍停在“基于什么模型”那一行
    y = K.lerp(-220, 150, ease_in_out(clamp01(g.since(2) / max(0.1, g.b(8) - g.b(2)))))
    x = 170 + 30 * math.sin(g.t * 2)
    K.ring(c, x, y, 70, K.DARK, 14)
    K.seg(c, x + 50, y + 50, x + 130, y + 130, K.DARK, 20)


# ---------------------------------------------------------------- 14 知道测的是什么

def wrap_up(c, g, t, d):
    def scr(c, w, h):
        K.text(c, "基于 · 某某模型", 0, -60, 30, "sans_medium", K.INK2)
        M.code(c, 0, 60, 50, "INFJ", 1, 0.1)
    phone(c, 0, 0, 0.7, scr)
    k = M.appear(g, 2, 0.3)
    if k > 0:
        with K.at(c, 200, -200, 0, 0.3 + 0.7 * K.ease_out_back(k, 2)):
            K.icon(c, "check", 0, 0, 110, K.GREEN, k, 0.5)


def build() -> Episode:
    shots = [
        # 1
        Shot(3, "刷到一个测试：|免费，10 分钟。", "情境演绎", [
            Fig(260, GROUND, 340, at=0, mood="calm", hair="short", pose="point",
                moves=[(8, dict(mood="happy", sfx="wood_high", note="主角点下“开始测试”"))]),
            Custom(ad_phone, x=700, y=760, at=0, enter="pop", sfx="wood_low", note="手机广告弹出"),
        ], draw=ground, hits=[(4, "shaker", 0.6, "广告闪动")],
            note="主角刷到一个广告：“免费 · 10 分钟 · 测出你的人格”，第 8 拍点下开始测试"),
        # 2
        Shot(3, "做完题，|结果是 INFJ-T。", "情境演绎", [
            Custom(result_screen, x=540, y=760, at=0, enter="none"),
        ], hits=[(1, "wood_low", 0.5, "答题"), (2, "wood_low", 0.5, "答题"), (3, "wood_low", 0.5, "答题"),
                 (4, "wood_low", 0.5, "答题"), (6, "bongo_high", 0.8, "结果 INFJ 弹出"),
                 (8, "rim", 0.9, "“-T”贴上")],
            note="答题进度条按拍增长；第 6 拍出结果 INFJ，第 8 拍贴上“-T”"),
        # 3
        Shot(2, "等等，|这个 -T 是什么？", "情境演绎", [
            Custom(big_t, x=600, y=620, at=0, enter="pop"),
            Fig(300, GROUND, 320, at=0, enter="none", pose="think", mood="worried", hair="short"),
        ], draw=ground, hits=[(2, "bongo_low", 0.8, "问号弹出")], text_beat=0,
            note="大号“-T”标签，旁边弹出问号，主角托腮"),
        # 4 drop
        Shot(3, "你做的测试，|未必是 MBTI。", "网络测试", [
            Big("网络测试", 540, 470, 150, at=0, sfx="kick", sub="online tests", note="概念落版（音乐 drop）"),
            Custom(vs, x=540, y=900, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.8, "手机结果出现"), (6, "wood_low", 0.8, "官方问卷出现"),
                 (8, "rim", 0.9, "不等号砸下")],
            note="drop 处“网络测试”砸下；手机上的 INFJ-T 与官方 MBTI 问卷之间砸下不等号"),
        # 5
        Shot(3, "很多流行的免费测试，|用的是自家模型。", "网络测试", [
            Custom(own_model, x=540, y=820, at=0, enter="pop"),
        ], hits=[(2, "wood_low", 0.7, "题目进入模型"), (4, "wood_high", 0.8, "四字母输出"),
                 (6, "shaker", 0.6, "例：16Personalities")],
            note="题目进入“自家模型（NERIS）”黑箱，右边输出四字母；上方标注“例：16Personalities”"),
        # 6
        Shot(3, "它在四个字母后，|多加了一维：-A/-T。", "网络测试", [
            Custom(fifth_dim, x=540, y=800, at=0, enter="pop", sfx="wood_low", note="四张字母牌"),
        ], hits=[(6, "frame", 0.9, "第五维 -A 贴上")],
            note="INFJ 四张牌后面，第 6 拍贴上第五个标签，在 -A 与 -T 之间切换"),
        # 7
        Shot(3, "官方 MBTI 问卷，|没有这一维。", "机制示意", [
            Custom(official_four, x=540, y=800, at=0, enter="pop", sfx="wood_low", note="官方问卷与四张牌"),
        ], hits=[(6, "rim", 0.9, "第五个空位打叉")],
            note="官方问卷旁只有四张字母牌，第五个虚线空位被打叉"),
        # 8
        Shot(2, "官方版要付费，|由认证施测师解读。", "机制示意", [
            Fig(240, GROUND, 320, at=0, mood="calm", hair="short"),
            Fig(840, GROUND, 320, at=0, mood="smile", hair="bun", color=K.OTHER3, face=-1, pose="give"),
            Label("认证施测师", 840, 690, 32, at=1, fill=ACC, sfx="wood_high", note="认证施测师"),
            Label("付费", 240, 690, 32, at=2, fill=K.INK2, sfx="wood_low", note="付费"),
            Custom(report_sheet, x=540, y=760, at=0, enter="none"),
        ], draw=session, hits=[(3, "bongo_high", 0.8, "解读报告摊开")], text_beat=0,
            note="主角与认证施测师隔桌而坐，中间摊开一份解读报告"),
        # 9
        Shot(2, "看到 -A/-T，|就不是官方问卷。", "常见误解", [
            Custom(warn_tags, x=540, y=780, at=0, enter="pop"),
        ], hits=[(2, "rim", 0.9, "“-A”被红圈圈出")], text_beat=0,
            note="ENFP-A 的“-A”被红圈圈出：不是官方问卷的结果"),
        # 10
        Shot(3, "字母一样，|背后的模型可以不同。", "机制示意", [
            Custom(two_models, x=540, y=800, at=0, enter="pop"),
        ], hits=[(2, "wood_low", 0.7, "模型 A 收题"), (4, "wood_high", 0.7, "模型 A 输出 INFJ"),
                 (6, "wood_low", 0.7, "模型 B 收题"), (8, "wood_high", 0.7, "模型 B 也输出 INFJ")],
            note="两个不同的黑箱模型 A、B，按拍各自输出一样的 INFJ"),
        # 11
        Shot(3, "怎么计分、怎么解释，|各家都不一样。", "机制示意", [
            Custom(two_scales, x=540, y=800, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "测试 A 的滑块停下"), (6, "wood_low", 0.7, "测试 B 的滑块停在另一侧")],
            note="同一个人在两个测试的 E—I 量尺上，滑块停在不同位置"),
        # 12
        Shot(4, "两个测试对不上，|也不必奇怪。", "情境演绎", [
            Custom(mismatch, x=540, y=640, at=0, enter="pop"),
            Fig(540, GROUND, 300, at=0, mood="worried", hair="short",
                moves=[(8, dict(pose="shrug", mood="smile", sfx="bongo_low", note="主角耸耸肩"))]),
        ], draw=ground, hits=[(4, "wood_high", 0.7, "另一个测试的结果出现"), (6, "rim", 0.8, "P 和 J 对不上")],
            note="手机上是 INFJ-T，另一个测试给出 INFP，最后一个字母发光；主角耸耸肩"),
        # 13
        Shot(4, "做测试前看一眼：|它用的是什么模型？", "小练习", [
            Custom(fine_print, x=540, y=780, at=0, enter="pop"),
        ], hits=[(2, "shaker", 0.6, "放大镜开始往下扫"), (8, "wood_high", 0.9, "停在“基于什么模型”那一行")],
            note="放大镜在手机页面上往下扫，第 8 拍停在“本测试基于 ____ 模型”，这一行被高亮"),
        # 14
        Shot(2, "知道测的是什么，|结果才好理解。", "机制示意", [
            Custom(wrap_up, x=540, y=580, at=0, enter="pop", sfx="wood_low", note="手机标着模型名"),
            Fig(540, GROUND, 260, at=0, mood="smile", hair="short"),
        ], draw=ground, hits=[(2, "clap", 0.8, "绿色对勾")],
            note="手机上写清“基于某某模型”，旁边亮起绿色对勾"),
        end_shot(REFS, "08 巴纳姆效应：为什么人格测试，总觉得说得准？"),
    ]
    return Episode(7, "online", "网络测试", "你测的，真的是 MBTI 吗？", ACC, shots, refs=REFS,
                   publish_title="你测的，真的是 MBTI 吗？｜MBTI科普07 网络测试",
                   hashtags="#MBTI #心理学 #人格测试 #16型人格 #科普",
                   cover_title="你测的，|真的是【MBTI】吗？", cover_sub="免费测试与官方问卷", cover_shot=3, cover_t=6.0,
                   notes=[
                       "16Personalities 官网自述：使用自己开发的 NERIS Type Explorer 模型，沿用常见的四字母类型代码，第五个维度 Identity 给出 -A（Assertive）/ -T（Turbulent），不使用荣格认知功能。官方 MBTI 问卷没有 -A/-T 这一维。",
                       "有第三方分析认为 16Personalities 的计分更接近大五人格的连续特质；这不是厂商表述，片中不上屏。",
                       "官方 MBTI 是付费测评，由认证施测师解读（Myers & Briggs Foundation“Ethical use of the MBTI instrument”）。",
                       "第 1–3、12 镜为情境演绎；手机界面、题数与“模型 A / 模型 B”均为示意，不对应任何真实产品界面。",
                       "MBTI、Myers-Briggs Type Indicator 是 The Myers-Briggs Company 的注册商标；16Personalities、NERIS Type Explorer 是 NERIS Analytics 的商标。片中只作事实性提及，未使用其 logo、插画与配色。",
                   ], **SERIES).build()
