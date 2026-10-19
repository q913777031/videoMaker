"""09 科学争议：MBTI，到底科学吗？"""

import math

from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import kit_mbti as M

ACC = "#4D6A86"
GROUND = 1130
SERIES = dict(series="MBTI 科普", file_prefix="MBTI")
REFS = ["Pittenger, D. J. (1993). Measuring the MBTI… and coming up short. J. Career Planning & Employment, 54(1), 48–52.",
        "McCrae, R. R. & Costa, P. T. (1989). Reinterpreting the Myers-Briggs Type Indicator from the perspective of "
        "the five-factor model of personality. J. Personality, 57(1), 17–40.",
        "ETS (1962). An Assessment of Some Structural Properties of the Jungian Personality Typology."]
REFS_SHORT = ["Pittenger, D. J. (1993). J. Career Planning & Employment, 54(1), 48–52.",
              "McCrae, R. R. & Costa, P. T. (1989). J. Personality, 57(1), 17–40.",
              "ETS 研究报告（1962）：荣格人格类型的结构特性评估"]


def ground(g):
    K.ground(g.c, GROUND)


def flip_k(g, beat, dur=0.4):
    """第 beat 拍开始的翻牌：返回 (翻转系数 |cos|, 是否已翻到背面)。"""
    q = clamp01(g.since(beat) / dur)
    return abs(math.cos(q * math.pi)), q >= 0.5


# ---------------------------------------------------------------- 1 两次结果

def two_results(c, g, t, d):
    k1 = M.appear(g, 2, 0.35)
    if k1 > 0:
        K.text(c, "上个月", -330, -120, 36, "sans_medium", K.INK2, k1, "left")
        M.code(c, 80, -120, 120, "INTJ", k1)
    k2 = M.appear(g, 6, 0.35)
    if k2 > 0:
        K.text(c, "这周", -330, 110, 36, "sans_medium", K.INK2, k2, "left")
        fl, back = flip_k(g, 8)
        letters = "INFJ" if back else "INTJ"
        for i, ch in enumerate(letters):
            x = 80 - 1.5 * 120 * 1.18 + i * 120 * 1.18
            M.tile(c, x, 110, 120, ch, None, clamp01(k2 * 3), fl if i == 2 else 1.0, 0,
                   0.3 + 0.7 * K.ease_out_back(k2, 1.8), glow=M.appear(g, 8, 0.4) if i == 2 else 0)


# ---------------------------------------------------------------- 2 T 还是 F

def tf_flipper(c, g, t, d):
    beats = (2, 4, 6, 8)
    n = sum(g.since(b) >= 0.2 for b in beats)
    fl = 1.0
    for b in beats:
        q = g.since(b)
        if 0 <= q < 0.4:
            fl = abs(math.cos(q / 0.4 * math.pi))
    ch = "TF"[n % 2]
    M.tile(c, 0, 0, 170, ch, None, 1, fl, 0, 1, glow=0.4)


# ---------------------------------------------------------------- 4 drop：三个问题

QS = ["稳定吗？", "分得开吗？", "测到了什么？"]


# ---------------------------------------------------------------- 5 重测

def retest_grid(c, g, t, d):
    codes = ["INTJ", "ENFP", "ISTJ", "ESFJ", "INFP", "ENTJ", "ISFP", "ESTP", "INFJ", "ENTP"]
    after = ["INFJ", "ENFP", "ESTJ", "ESFJ", "INFJ", "ENTJ", "ISFJ", "ESTP", "INFJ", "INTP"]
    order = [0, 2, 4, 6, 9]
    for i, (a, b) in enumerate(zip(codes, after)):
        col, row = i % 5, i // 5
        x, y = -380 + col * 190, -150 + row * 300
        K.figure(c, x, y + 150, 170, "stand", (K.OTHER, K.OTHER2, K.OTHER3, K.HERO, "#9C8FB0")[(i + row) % 5],
                 face=1, mood="calm", lift=0.5, hair=("short", None, "bun", "long", None)[i % 5])
        ch = a
        if i in order:
            kb = order.index(i) + 4
            q = g.since(kb)
            if q >= 0.18:
                ch = b
            sc = M.pulse(g, [kb], 0.25)
            K.spotlight(c, x, y - 70, 90, ACC, 0.5 * clamp01(q / 0.3) if q > 0 else 0)
        else:
            sc = 1.0
        M.tag(c, x, y - 70, 64, ch, ACC if ch != a else K.INK2, 1, 0, sc)


# ---------------------------------------------------------------- 6 单峰分布

def bell_hist(c, g, t, d):
    p = ease_in_out(clamp01(g.since(0) / (g.b(4) + 0.01)))
    M.bell(c, 0, 0, 820, 420, p, ACC, 1, False, 0, True, 0, 0.42, 17)
    M.tile(c, -450, 70, 80, "E", sub=None)
    M.tile(c, 450, 70, 80, "I", sub=None)
    k = M.appear(g, 6, 0.4)
    if k > 0:
        K.arrow(c, (190, -470), (40, -400), K.RED, 9, k, k, 0.2, 28)
        K.text(c, "大多数人在这里", 230, -520, 38, "serif_black", K.RED, k)


# ---------------------------------------------------------------- 7 中线一切

def bell_cut(c, g, t, d):
    M.bell(c, 0, 0, 820, 420, 1.0, ACC, 1, True, ease_out(clamp01(g.since(2) / 0.35)), True)
    for i, (x, lab, b) in enumerate(((-40, "E", 4), (40, "I", 6))):
        k = M.appear(g, b, 0.3)
        if k <= 0:
            continue
        K.dot(c, x, -400, 18, K.INK, k)
        K.seg(c, x, -380, x, -10, K.INK3, 3, k)
        M.tile(c, x * 4.5, -470, 90, lab, None, k, 1, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8))
        K.arrow(c, (x * 4.5 * 0.75, -430), (x * 1.3, -405), K.INK3, 5, k, k, 0.0, 16)
    k = M.appear(g, 8, 0.3)
    if k > 0:
        K.pill(c, 0, 90, "只差一点", 34, K.RED, K.PAPER, k)


# ---------------------------------------------------------------- 8 四条连续量尺

def four_scales(c, g, t, d):
    targets = (-0.22, 0.15, -0.08, 0.3)
    for i, (a, b) in enumerate(M.PAIRS):
        k = M.appear(g, i * 0.5, 0.35)
        if k <= 0:
            continue
        start = (-1, 1, -1, 1)[i]
        q = ease_in_out(clamp01(g.since(2 + 2 * i) / 0.45))
        M.scale_bar(c, 0, -330 + i * 200, 780, a, b, lerp(start * 0.92, targets[i], q), clamp01(k * 2), None, 72)


# ---------------------------------------------------------------- 10 维度是真的

def real_dims(c, g, t, d):
    M.scale_bar(c, 0, -60, 780, "T", "F", -0.2, 1, None, 80)
    k = M.appear(g, 2, 0.3)
    if k > 0:
        K.icon(c, "check", 0, -240, 90, K.GREEN, clamp01(k * 3), 0.5, 0, 0.3 + 0.7 * K.ease_out_back(k, 2))
        K.text(c, "维度", 0, -170, 34, "sans_medium", K.GREEN, k)
    q = M.appear(g, 6, 0.3)
    if q > 0:
        y0, y1 = 60, -150
        for j in range(8):
            ya = lerp(y0, y1, j / 8)
            yb = lerp(y0, y1, (j + 0.5) / 8)
            if (j + 0.5) / 8 > q:
                break
            K.seg(c, 0, ya, 0, yb, K.RED, 7)
        K.icon(c, "cross", 0, 140, 80, K.RED, clamp01(q * 3), 0.5, 0, 0.3 + 0.7 * K.ease_out_back(q, 2))
        K.text(c, "一刀切成两类", 0, 220, 34, "sans_medium", K.RED, q)


# ---------------------------------------------------------------- 11 同一个字母差很远

def same_letter(c, g, t, d):
    M.scale_bar(c, 0, 0, 820, "E", "I", 0, 1, None, 90, knob=False)
    half = 410 - 90 * 0.8
    for x, b, name in ((-0.9, 2, "小林"), (-0.08, 5, "小周")):
        k = M.appear(g, b, 0.3)
        if k <= 0:
            continue
        kx = x * half
        K.dot(c, kx, 0, 30, ACC, k)
        K.ring(c, kx, 0, 30, K.PAPER, 6, k)
        K.figure(c, kx, -60, 160, "stand", K.HERO if b == 2 else K.OTHER3, alpha=k, mood="smile", lift=0.5,
                 hair="short" if b == 2 else "long")
        M.tag(c, kx, -260, 56, "E", ACC, k)
        K.text(c, name, kx, -330, 32, "sans_medium", K.INK2, k)
    q = M.appear(g, 8, 0.4)
    if q > 0:
        x0, x1 = -0.9 * half, -0.08 * half
        K.seg(c, x0, 140, lerp(x0, x1, q), 140, K.RED, 6)
        K.pill(c, (x0 + x1) / 2, 200, "差得很远", 32, K.RED, K.PAPER, q)


# ---------------------------------------------------------------- 13 身高也是连续的

def heights(c, g, t, d):
    n = 7
    for i in range(n):
        x = -420 + i * 140
        s = (220, 245, 280, 288, 305, 320, 340)[i]
        k = M.appear(g, 0, 0.3)
        tall = s * 1.08 > 306
        lab = M.appear(g, 6, 0.3) if i in (2, 3) else M.appear(g, 8, 0.3)
        K.figure(c, x, 0, s, "stand", (K.OTHER, K.OTHER2, K.OTHER3, K.HERO, "#9C8FB0", K.OTHER, K.OTHER2)[i],
                 alpha=k, mood="calm", lift=0.5, hair=(None, "bun", "short", "short", "long", None, "bun")[i])
        if lab > 0:
            K.pill(c, x, -s - 60, "高" if tall else "矮", 30, ACC if tall else K.INK3, K.PAPER, lab)
    q = ease_out(clamp01(g.since(4) / 0.4))
    if q > 0:
        y = -306
        K.seg(c, -500, y, lerp(-500, 500, q), y, K.RED, 6)
    for b in (6,):
        if 0 <= g.since(b) <= 0.5:
            K.burst(c, -420 + 2.5 * 140, -350, g.since(b), K.RED, 60, 140, 8, 5)


# ---------------------------------------------------------------- 14 看分数

def read_scores(c, g, t, d):
    pos = (-0.7, 0.12, -0.35, 0.06)
    for i, (a, b) in enumerate(M.PAIRS):
        y = -330 + i * 200
        M.scale_bar(c, 0, y, 780, a, b, pos[i], 1, None, 72)
        k = M.appear(g, 2 + 3 * i, 0.3)
        if k > 0:
            half = 390 - 72 * 0.8
            K.ring(c, pos[i] * half, y, 46 + 10 * (1 - ease_out(k)), K.RED, 6, k)
            note = "明显" if abs(pos[i]) > 0.3 else "接近中间"
            K.pill(c, pos[i] * half, y - 70, note, 28, K.RED if note == "明显" else K.INK2, K.PAPER, k)


# ---------------------------------------------------------------- 15 不是盒子

def box_to_scales(c, g, t, d):
    k = 1 - ease_out(clamp01(g.since(2) / 0.4))
    if k > 0:
        K.rr_stroke(c, 0, -60, 640, 220, 24, K.INK2, 8, k)
        M.code(c, 0, -60, 120, "INTJ", k)
    q = M.appear(g, 3, 0.4)
    if q > 0:
        for i, (a, b) in enumerate(M.PAIRS):
            M.scale_bar(c, 0, -300 + i * 150, 640, a, b, (-0.3, 0.1, -0.2, 0.15)[i], clamp01(q * 2), None, 56,
                        names=False)


def build() -> Episode:
    shots = [
        # 1
        Shot(3, "上个月测是 INTJ，|这周重测……", "情境演绎", [
            Custom(two_results, x=540, y=640, at=0, enter="none"),
            Fig(540, GROUND, 300, at=0, mood="calm", hair="short", pose="carry",
                moves=[(8, dict(mood="surprised", pose="shrug", sfx="rim", note="T 翻成 F，主角愣住"))]),
        ], draw=ground, hits=[(2, "wood_high", 0.8, "上个月：INTJ"), (6, "wood_low", 0.8, "这周：INTJ 牌弹出")],
            note="两行结果：上个月 INTJ；这周的牌第 8 拍 T 翻成 F，主角愣住"),
        # 2
        Shot(3, "一个字母变了。|到底哪个才是我？", "情境演绎", [
            Custom(tf_flipper, x=540, y=560, at=0, enter="pop"),
            Fig(540, GROUND, 330, at=0, enter="none", pose="think", mood="worried", hair="short",
                moves=[(10, dict(pose="cover", mood="sad", sfx="tom", note="主角抱头"))]),
        ], draw=ground, hits=[(2, "wood_high", 0.7, "翻成 F"), (4, "wood_low", 0.7, "翻回 T"),
                              (6, "wood_high", 0.7, "又翻成 F"), (8, "wood_low", 0.7, "又翻回 T")],
            note="主角头顶的字母牌按拍在 T 和 F 之间来回翻，第 10 拍主角抱头"),
        # 3
        Shot(2, "是上次|测错了吗？", "常见误解", [
            Fig(360, GROUND, 330, at=0, enter="none", pose="think", mood="worried", hair="short"),
            Icon("question", 720, 640, 170, color=ACC, at=1, enter="pop", sfx="bongo_low", note="大问号"),
        ], draw=ground, note="主角托腮，旁边弹出大问号"),
        # 4  drop
        Shot(3, "MBTI 科学吗？|要拆成三个问题看。", "机制示意", [
            Big("科学争议", 540, 470, 150, at=0, sfx="kick", sub="Is the MBTI scientific?",
                note="概念落版（音乐 drop）"),
            Label(QS[0], 540, 760, 52, at=4, fill=ACC, sfx="wood_high", note="问题一：稳定吗？"),
            Label(QS[1], 540, 900, 52, at=6, fill=ACC, sfx="wood_low", note="问题二：分得开吗？"),
            Label(QS[2], 540, 1040, 52, at=8, fill=ACC, sfx="bongo_high", note="问题三：测到了什么？"),
        ], note="drop 处“科学争议”砸下；三个问题按拍弹出：稳定吗、分得开吗、测到了什么"),
        # 5
        Shot(3, "隔几周重测，可能|有多达一半人类型变了。", "研究证据", [
            Custom(retest_grid, x=540, y=760, at=0, enter="fade"),
            Txt("Pittenger，1993：间隔约 5 周的重测研究", 540, 1200, 28, at=2, font="sans_medium", color=K.INK2),
        ], hits=[(4, "wood_high", 0.7, "第 1 人类型变了"), (5, "wood_low", 0.7, "第 2 人"), (6, "wood_high", 0.7, "第 3 人"),
                 (7, "wood_low", 0.7, "第 4 人"), (8, "bongo_high", 0.8, "第 5 人：十个人里五个变了")],
            research=True, note="十个人各挂一个类型牌，第 4–8 拍其中五人的牌按拍改变"),
        # 6
        Shot(3, "原因之一：|大多数人的分数在中间。", "研究证据", [
            Custom(bell_hist, x=540, y=1060, at=0, enter="fade"),
            Txt("分数分布是一座山，不是两座（ETS，1962）", 540, 1200, 28, at=2, font="sans_medium", color=K.INK2),
        ], hits=[(0, "shaker", 0.6, "分布柱从左往右长出"), (6, "rim", 0.8, "箭头指向中间")],
            research=True, note="E—I 分数的分布柱从左到右长出，是一座单峰的山；第 6 拍箭头指向中间：大多数人在这里"),
        # 7
        Shot(3, "中线一切，只差一点的人|被分到两边。", "机制示意", [
            Custom(bell_cut, x=540, y=1060, at=0, enter="none"),
        ], hits=[(2, "rim", 0.9, "红色中线切下"), (4, "wood_high", 0.8, "左边一点：E"), (6, "wood_low", 0.8, "右边一点：I"),
                 (8, "bongo_high", 0.8, "只差一点")],
            note="红色中线从下往上切开分布；中线两侧紧挨的两个点，一个被标成 E、一个被标成 I"),
        # 8
        Shot(4, "四个维度，更像|四条连续的量尺。", "研究证据", [
            Custom(four_scales, x=540, y=780, at=0, enter="none"),
            Txt("McCrae & Costa，1989", 540, 1200, 28, at=2, font="sans_medium", color=K.INK2),
        ], hits=[(2, "wood_high", 0.8, "E-I 滑块滑到中间附近"), (4, "wood_low", 0.8, "S-N"),
                 (6, "bongo_high", 0.8, "T-F"), (8, "bongo_low", 0.8, "J-P")],
            research=True, note="四条量尺的滑块从两端按拍滑到中间附近：偏好有强有弱，不是开关"),
        # 9
        Shot(4, "不是一无是处：|维度测到了，错在二分。", "常见误解", [
            Custom(real_dims, x=540, y=800, at=0, enter="pop"),
        ], hits=[(2, "wood_high", 0.8, "量尺上打勾"), (6, "rim", 0.9, "中线一刀切下，打叉")],
            note="T—F 量尺上方打勾（维度是真的），第 6 拍红线从中间切下并打叉（一刀切成两类）"),
        # 10
        Shot(3, "同一个字母，|可能差得很远。", "机制示意", [
            Custom(same_letter, x=540, y=900, at=0, enter="pop"),
        ], hits=[(2, "wood_high", 0.8, "小林在 E 的最左端"), (5, "wood_low", 0.8, "小周在靠近中线的位置"),
                 (8, "bongo_low", 0.8, "两人之间拉出一段距离")],
            note="E—I 量尺上：小林在最左端，小周紧挨中线，两人都被标成 E，第 8 拍拉出“差得很远”"),
        # 11
        Shot(3, "就像身高：没人只分|“高个”和“矮个”。", "机制示意", [
            Custom(heights, x=540, y=GROUND, at=0, enter="none"),
        ], draw=ground, hits=[(0, "wood_low", 0.6, "七个人从矮到高排好"), (4, "rim", 0.9, "红线横切"),
                              (6, "bongo_high", 0.9, "中间两人被分到两边"), (8, "shaker", 0.7, "其余人贴上标签")],
            note="七个人从矮到高排成一排，一条红线横切，几乎一样高的中间两人被贴上不同标签"),
        # 12
        Shot(4, "看每个维度的分数，|而不只看字母。", "小练习", [
            Custom(read_scores, x=540, y=820, at=0, enter="pop"),
        ], hits=[(2, "wood_high", 0.8, "E-I：明显"), (5, "wood_low", 0.8, "S-N：接近中间"),
                 (8, "bongo_high", 0.8, "T-F：明显"), (11, "bongo_low", 0.8, "J-P：接近中间")],
            note="四条量尺上的位置按拍一一圈出，标注“明显”或“接近中间”"),
        # 13
        Shot(2, "你不是一个盒子，|是四条刻度。", "机制示意", [
            Custom(box_to_scales, x=540, y=820, at=0, enter="pop", sfx="wood_low", note="装着 INTJ 的盒子"),
        ], hits=[(3, "clap", 0.8, "盒子散开成四条量尺")], text_beat=0,
            note="四字母装在一个框里，第 3 拍框散开，变成四条量尺"),
        end_shot(REFS_SHORT, "10 正确使用：四个字母，是标签还是语言？"),
    ]
    return Episode(9, "science", "科学争议", "MBTI，到底科学吗？", ACC, shots, refs=REFS,
                   publish_title="MBTI，到底科学吗？｜MBTI科普09 科学争议",
                   hashtags="#MBTI #心理学 #人格测试 #科学 #科普",
                   cover_title="MBTI，|到底【科学】吗？", cover_sub="重测、分布与二分法", cover_shot=6, cover_t=6.0,
                   notes=[
                       "第 5 镜：Pittenger（1993）引述的研究显示，即使间隔只有约 5 周，也可能有多达 50% 的人被分到不同类型。"
                       "出版方的口径是：重测时约一半人四个字母完全一致，多数人至少三个字母一致——两种说法描述的是同一类数据。"
                       "画面中“十人五变”为示意，不代表具体研究的样本。",
                       "第 6 镜：ETS 1962 年研究报告 An Assessment of Some Structural Properties of the Jungian Personality "
                       "Typology 发现分数分布没有明显双峰。",
                       "第 8 镜：McCrae & Costa（1989）对 468 名成人的研究认为，没有证据表明 MBTI 测的是二分的偏好或质性不同的类型，"
                       "它测到的是四个相对独立的连续维度。",
                       "第 7、10、11 镜为机制示意，说明“中线二分”的一般后果，不代表具体研究数据。",
                       "本期结论是“维度有意义，二分成类型有问题”，不是“MBTI 一无是处”。",
                   ], **SERIES).build()
