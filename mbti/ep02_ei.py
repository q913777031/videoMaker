"""02 外向与内向：内向的人，就是不爱说话吗？"""

import math

from engine.gfx import clamp01

from adler import kit as K
from adler.core import Big, Bubble, Custom, Episode, Fig, Icon, Shot, end_shot

from . import kit_mbti as M

ACC = "#C9703A"
GROUND = 1130
SERIES = dict(series="MBTI 科普", file_prefix="MBTI")
REFS = ["Jung, C. G. (1921). Psychologische Typen, 第 10 章“一般描述”.（英译 Psychological Types, 1923）",
        "Myers, I. B. & Myers, P. B. (1980). Gifts Differing.（中译《天生不同》）"]


def ground(g):
    K.ground(g.c, GROUND)


def party(g):
    ground(g)
    c = g.c
    for i, col in enumerate((K.GOLD, ACC, K.RED, K.GREEN, K.GOLD, ACC)):
        x = 140 + i * 160
        K.seg(c, x - 80, 400 + 20 * math.sin(i), x + 80, 400 + 20 * math.sin(i + 1), K.LINE, 3)
        K.dot(c, x, 412 + 20 * math.sin(i + 0.5), 14, col, 0.75 + 0.25 * math.sin(g.t * 3 + i))


def batt(level_fn, s=170, label=None):
    """电量元件：level_fn(g) 返回 0–1；电量低于 0.15 时闪烁。"""

    def fn(c, g, t, d):
        lv = level_fn(g)
        a = 1.0
        if lv < 0.15:
            a = 0.55 + 0.45 * (0.5 + 0.5 * math.cos(g.t * 9))
        M.battery(c, 0, 0, s, lv, K.GREEN, a)
        K.text(c, f"{int(round(lv * 100))}%", 0, s * 0.72, s * 0.2, "black", K.INK2)
        if label:
            K.text(c, label, 0, -s * 0.8, s * 0.2, "sans_medium", K.INK2)

    return fn


# ---------------------------------------------------------------- 2 回家瘫倒

def home(g):
    ground(g)
    c = g.c
    K.rr(c, 540, 610, 300, 240, 14, K.mix(K.DARK, K.PAPER, 0.15))
    K.rr_stroke(c, 540, 610, 300, 240, 14, K.PAPER, 10)
    K.seg(c, 540, 490, 540, 730, K.PAPER, 8)
    K.dot(c, 470, 560, 26, K.tint(K.GOLD, 0.4))
    sofa = K.mix(ACC, K.PAPER, 0.35)
    K.rr(c, 560, GROUND - 90, 560, 160, 30, sofa)
    K.rr(c, 560, GROUND - 210, 520, 120, 30, K.shade(sofa, 0.12))
    K.rr(c, 290, GROUND - 120, 70, 180, 24, K.shade(sofa, 0.2))
    K.rr(c, 830, GROUND - 120, 70, 180, 24, K.shade(sofa, 0.2))


# ---------------------------------------------------------------- 3 外向还是内向

def which_side(c, g, t, d):
    for i, (ch, x) in enumerate((("E", -300), ("I", 300))):
        k = M.appear(g, 1 + 2 * i, 0.3)
        if k <= 0:
            continue
        sw = 10 * math.sin(g.t * 2.2 + i * 2)
        M.tile(c, x, 0, 150, ch, None, clamp01(k * 3), 1, sw, 0.3 + 0.7 * K.ease_out_back(k, 1.8),
               M.PAIR_NAMES[ch])


# ---------------------------------------------------------------- 4 drop：能量方向

def energy_arrows(c, g, t, d):
    """E 牌箭头向外放射，I 牌箭头向内汇聚。"""
    for i, (ch, x) in enumerate((("E", -230), ("I", 230))):
        k = M.appear(g, 4 + 4 * i, 0.3)
        if k <= 0:
            continue
        M.tile(c, x, 0, 150, ch, None, clamp01(k * 3), 1, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8))
        q = M.appear(g, 5 + 4 * i, 0.5)
        if q <= 0:
            continue
        col = M.DIM[ch]
        for j in range(6):
            a = math.radians(j * 60 + 30)
            r0, r1 = 115, 200
            p0 = (x + r0 * math.cos(a), r0 * math.sin(a))
            p1 = (x + r1 * math.cos(a), r1 * math.sin(a))
            if ch == "E":
                K.arrow(c, p0, p1, col, 8, q, q, 0, 22)
            else:
                K.arrow(c, p1, p0, col, 8, q, q, 0, 22)


# ---------------------------------------------------------------- 5 外倾：能量流向外部

OUT_ICONS = [("friends", -330, -250), ("phone", 0, -360), ("sun", 330, -250), ("megaphone", 380, 60),
             ("heart", -380, 60)]


def outward(c, g, t, d):
    for i, (name, x, y) in enumerate(OUT_ICONS):
        k = M.appear(g, 2 + 2 * i, 0.4)
        if k <= 0:
            continue
        ang = math.atan2(y, x)
        K.arrow(c, (190 * math.cos(ang), 190 * math.sin(ang)), (x * 0.78, y * 0.78), ACC, 9, k, k, 0, 26)
        K.icon(c, name, x, y, 120, K.OTHER3 if name != "sun" else K.GOLD, clamp01(k * 3), 0.7, 0,
               0.3 + 0.7 * K.ease_out_back(k, 1.8), 1, ACC)


# ---------------------------------------------------------------- 6 内倾：能量流向内心

def inward(c, g, t, d):
    for i in range(5):
        k = M.appear(g, 2 + 2 * i, 0.45)
        if k <= 0:
            continue
        ang = math.radians(-160 + i * 35)
        r0, r1 = 400, 200
        K.arrow(c, (r0 * math.cos(ang), r0 * math.sin(ang) * 0.8), (r1 * math.cos(ang), r1 * math.sin(ang) * 0.8),
                M.DIM["I"], 9, k, k, 0, 26)


def thought(c, g, t, d):
    k = M.appear(g, 6, 0.4)
    if k <= 0:
        return
    with K.at(c, 0, 0, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8)):
        K.bubble(c, 0, 0, "    ", 60, (0, 1), clamp01(k * 3), 1, K.PAPER, K.INK, ACC, True)
        K.icon(c, "bulb", -70, 0, 70, K.INK, clamp01(k * 3), 0.3, 0, 1, 1, K.GOLD)
        K.icon(c, "book", 40, 0, 70, M.DIM["I"], clamp01(k * 3), 0.3)
        K.heart(c, 125, 0, 40, K.RED, clamp01(k * 3))


# ---------------------------------------------------------------- 7 没有纯粹的类型

def no_pure(c, g, t, d):
    k = M.appear(g, 0, 0.4)
    pos = -0.95
    for p, b in ((0.95, 3), (-0.4, 6), (0.3, 9)):
        if g.since(b) >= 0:
            pos = K.lerp(pos, p, K.ease_in_out(clamp01(g.since(b) / 0.45)))
    M.scale_bar(c, 0, 0, 860, "E", "I", pos, k, None, 100)
    for i, (x, b) in enumerate(((-345, 4), (345, 7))):
        q = M.appear(g, b, 0.3)
        if q > 0:
            K.icon(c, "cross", x, -230, 90, K.RED, clamp01(q * 3), 0.5, 0, 0.3 + 0.7 * K.ease_out_back(q, 2))
            K.text(c, ("纯外向", "纯内向")[i], x, -150, 34, "sans_medium", K.RED, q)


# ---------------------------------------------------------------- 8–9 充电

def charging(c, g, t, d):
    lv = 0.1 + 0.9 * g.span(2, 7)
    M.battery(c, 0, 0, 300, lv, K.GREEN)
    k = M.appear(g, 2, 0.3)
    if k > 0:
        with K.fade(c, k):
            K.poly(c, [(-20, -60), (35, -60), (5, -5), (40, -5), (-25, 80), (-5, 15), (-40, 15)], K.GOLD)


def two_chargers(c, g, t, d):
    for i, (x, name, ch, label) in enumerate(((-250, "friends", "E", "热闹"), (250, "book", "I", "独处"))):
        k = M.appear(g, 1 + 3 * i, 0.35)
        if k <= 0:
            continue
        lv = 0.15 + 0.85 * clamp01(g.since(1 + 3 * i) / 1.6)
        with K.fade(c, clamp01(k * 3)):
            M.battery(c, x, 80, 230, lv, K.GREEN)
            K.icon(c, name, x, -170, 130, M.DIM[ch], 1, 0.6)
            K.pill(c, x, -60, label, 34, M.DIM[ch])


# ---------------------------------------------------------------- 10 内向的人上台

def stage(g):
    ground(g)
    K.rr(g.c, 760, GROUND - 40, 420, 80, 12, K.mix(ACC, K.PAPER, 0.4))
    K.crowd(g.c, 300, GROUND, 4, 230, g.t, spread=360, face_to=760)


def chest_tag(c, g, t, d):
    M.tag(c, 0, 0, 90, "I", K.DARK, 1, -8)


# ---------------------------------------------------------------- 11 讲完回血

def after_talk(c, g, t, d):
    lv = 0.9 - 0.75 * g.span(1, 4)
    if g.since(7) >= 0:
        lv = 0.15 + 0.75 * g.span(7, 11)
    M.battery(c, 0, 0, 200, lv, K.GREEN, 0.55 + 0.45 * (0.5 + 0.5 * math.cos(g.t * 9)) if lv < 0.2 else 1.0)


def sit_ground(g):
    ground(g)
    K.seat(g.c, 400, GROUND, 200, 90, K.mix(ACC, K.PAPER, 0.4), M.appear(g, 4, 0.3))


# ---------------------------------------------------------------- 12 安静的外向者

def crowd_party(g):
    party(g)
    K.crowd(g.c, 540, GROUND, 5, 280, g.t, spread=820, seed=7)


# ---------------------------------------------------------------- 13 小练习

def recharge_quiz(c, g, t, d):
    k = M.appear(g, 0, 0.4)
    checks = []
    for i, b in enumerate((4, 8)):
        q = M.appear(g, b, 0.25)
        if q > 0 and g.since(8 if i == 0 else 99) < 0:
            checks.append((i, q))
    if g.since(8) >= 0:
        checks = [(1, M.appear(g, 8, 0.25))]
    M.quiz(c, 0, -60, 780, "一天结束后，|什么让你回血？", ["约朋友出去聊聊", "一个人安静待着", "都行，看今天"],
           checks, k, 46, ACC)
    q = M.appear(g, 12, 0.3)
    if q > 0:
        K.icon(c, "question", 400, -330, 110, ACC, clamp01(q * 3), 0.5, 0, 0.3 + 0.7 * K.ease_out_back(q, 2))


# ---------------------------------------------------------------- 14 两种充电方式

def two_full(c, g, t, d):
    for i, x in enumerate((-300, 300)):
        k = M.appear(g, i, 0.35)
        if k > 0:
            M.battery(c, x, 0, 160, 0.3 + 0.7 * clamp01(g.since(i) / 0.8), K.GREEN, clamp01(k * 3))


def build() -> Episode:
    shots = [
        # 1
        Shot(3, "派对上，你聊得|比谁都开心。", "情境演绎", [
            Fig(240, GROUND, 320, at=0, mood="happy", color=K.OTHER, hair="bun"),
            Fig(830, GROUND, 320, at=0, mood="smile", color=K.OTHER3, face=-1),
            Fig(540, GROUND, 350, at=0, mood="happy", hair="short",
                moves=[(4, dict(pose="wave", sfx="clap", note="主角挥手大笑")),
                       (8, dict(pose="point", note="主角接着讲"))]),
            Bubble("哈哈哈！", 560, 620, 46, at=2, sfx="wood_high", note="主角笑着聊天"),
            Bubble("然后呢？", 840, 700, 40, at=6, tail=(-0.3, 1), sfx="wood_low", note="朋友追问"),
            Custom(batt(lambda g: 1 - 0.65 * g.span(0, 12), 150), x=900, y=470, at=0, enter="pop"),
        ], draw=party, note="派对上主角说说笑笑，右上角的电量从 100% 一点点往下掉"),
        # 2
        Shot(3, "一回到家，|整个人瘫在沙发上。", "情境演绎", [
            Fig(560, GROUND - 160, 330, at=0, enter="none", pose="sit", mood="flat", hair="short",
                moves=[(4, dict(pose="sit_sad", mood="sad", sfx="tom", note="主角瘫倒在沙发上"))]),
            Custom(batt(lambda g: 0.35 - 0.3 * g.span(2, 6), 150), x=880, y=470, at=0, enter="pop",
                   sfx="wood_low", note="电量只剩三成"),
        ], draw=home, hits=[(8, "shaker", 0.7, "电量闪红")],
            note="夜里回到家，主角一屁股坐进沙发，第 4 拍瘫倒；电量掉到 5% 闪红"),
        # 3
        Shot(2, "这样的你，|算外向，还是内向？", "情境演绎", [
            Custom(which_side, x=540, y=700, at=0, enter="none"),
            Fig(540, GROUND, 330, at=0, enter="none", pose="think", mood="worried", hair="short"),
            Icon("question", 540, 450, 110, color=ACC, at=5, enter="pop", sfx="bongo_high", note="问号弹出"),
        ], draw=ground, hits=[(1, "wood_high", 0.8, "E 牌弹出"), (3, "wood_low", 0.8, "I 牌弹出")],
            note="E、I 两张牌分别在主角左右弹出摇摆，主角犹豫，头顶冒出问号"),
        # 4  drop
        Shot(3, "E/I 问的是：|你的能量朝哪个方向？", "机制示意", [
            Big("外向与内向", 540, 470, 140, at=0, sfx="kick", sub="Extraversion · Introversion",
                note="概念落版（音乐 drop）"),
            Custom(energy_arrows, x=540, y=880, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.8, "E 牌落位"), (5, "shaker", 0.7, "E 的箭头向外放射"),
                 (8, "wood_low", 0.8, "I 牌落位"), (9, "rim", 0.8, "I 的箭头向内汇聚")],
            note="drop 处概念砸下；E 牌箭头向外放射，I 牌箭头向内汇聚"),
        # 5
        Shot(3, "外倾：心理能量|流向外部的人和事。", "荣格原著", [
            Fig(540, 1060, 300, at=0, mood="happy", hair="short", pose="cheer"),
            Custom(outward, x=540, y=800, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "能量流向朋友"), (4, "wood_low", 0.7, "流向手机消息"),
                 (6, "bongo_high", 0.7, "流向阳光"), (8, "bongo_low", 0.7, "流向活动"), (10, "clap", 0.7, "流向他人")],
            note="主角张开双臂，箭头按拍向外伸向朋友、消息、阳光、活动"),
        # 6
        Shot(3, "内倾：心理能量|流向内心的想法与感受。", "荣格原著", [
            Fig(540, 1100, 300, at=0, pose="think", mood="calm", hair="short"),
            Custom(inward, x=540, y=870, at=0, enter="none"),
            Custom(thought, x=540, y=520, at=0, enter="none"),
        ], hits=[(2, "wood_low", 0.7, "第一支箭头向内"), (4, "wood_high", 0.6, "第二支"),
                 (6, "bongo_high", 0.8, "思考气泡冒出：想法、书、感受")],
            note="四周的箭头按拍指向主角，头顶冒出装着灯泡、书和爱心的思考气泡"),
        # 7
        Shot(3, "荣格说：没有纯粹的外向，|也没有纯粹的内向。", "荣格原著", [
            Custom(no_pure, x=540, y=820, at=0, enter="fade"),
        ], hits=[(3, "wood_high", 0.7, "滑块滑到 I 端"), (4, "rim", 0.8, "“纯外向”被打叉"),
                 (7, "rim", 0.8, "“纯内向”被打叉"), (9, "wood_low", 0.7, "滑块停在中间偏 I")],
            note="E—I 量尺上的滑块来回滑动，两端“纯外向”“纯内向”先后被打叉，滑块停在中间附近"),
        # 8
        Shot(2, "区别在于：|你从哪里充电。", "机制示意", [
            Custom(charging, x=540, y=800, at=0, enter="pop", sfx="wood_low", note="空电池出现"),
        ], hits=[(2, "bongo_high", 0.8, "闪电亮起，开始充电")], text_beat=0,
            note="一节空电池，第 2 拍闪电亮起，电量一路涨满"),
        # 9
        Shot(2, "有人靠热闹充电，|有人靠独处充电。", "机制示意", [
            Custom(two_chargers, x=540, y=820, at=0, enter="none"),
        ], hits=[(1, "wood_high", 0.8, "热闹那节电池充起来"), (4, "wood_low", 0.8, "独处那节电池充起来")],
            text_beat=0, note="左边“热闹”、右边“独处”两节电池，按拍先后充满"),
        # 10
        Shot(3, "内向不等于害羞，|也不等于社恐。", "常见误解", [
            Fig(760, GROUND - 80, 330, at=0, mood="happy", hair="long", color=M.DIM["I"], face=-1,
                moves=[(4, dict(pose="point", sfx="wood_high", note="内向的人在台上从容讲话")),
                       (8, dict(pose="wave", mood="happy", sfx="clap", note="台下鼓掌"))]),
            Custom(chest_tag, x=770, y=GROUND - 300, at=2, enter="pop", sfx="wood_low", note="胸前“I”标签"),
            Bubble("大家好！", 600, 640, 44, at=4, tail=(0.4, 1)),
        ], draw=stage, note="胸前贴着“I”的人站上讲台从容开讲，台下观众鼓掌"),
        # 11
        Shot(3, "内向的人也能侃侃而谈，|只是之后需要回血。", "常见误解", [
            Fig(420, GROUND, 330, at=0, enter="none", mood="happy", hair="long", color=M.DIM["I"], pose="point",
                moves=[(4, dict(pose="sit", mood="calm", sfx="wood_low", note="讲完后坐下看书"))]),
            Icon("book", 520, 920, 100, color=K.HERO, at=5, enter="pop", sfx="wood_high", note="翻开一本书"),
            Custom(after_talk, x=820, y=650, at=0, enter="pop"),
        ], draw=sit_ground, hits=[(7, "bongo_high", 0.8, "电量开始回升")],
            note="讲完话电量掉到底，坐下看书后电量一格格回升"),
        # 12
        Shot(4, "外向也不等于话多，|它说的是能量从哪来。", "常见误解", [
            Fig(540, GROUND, 360, at=0, mood="smile", hair="short", color=M.DIM["E"],
                moves=[(6, dict(pose="relax", mood="happy", sfx="wood_high", note="安静的外向者在人群里很自在"))]),
            Custom(batt(lambda g: 0.3 + 0.7 * g.span(4, 12), 150), x=540, y=470, at=2, enter="pop",
                   sfx="wood_low", note="电量出现"),
        ], draw=crowd_party, hits=[(12, "bongo_high", 0.8, "电量充满")],
            note="一个不怎么说话的人站在热闹的人群里，头顶的电量越来越满"),
        # 13
        Shot(4, "一天结束后，|什么让你回血？", "小练习", [
            Custom(recharge_quiz, x=540, y=820, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.7, "题卡出现"), (4, "wood_high", 0.8, "先勾“约朋友出去聊聊”"),
                 (8, "bongo_high", 0.8, "改勾“一个人安静待着”"), (12, "rim", 0.7, "问号：你呢？")],
            note="题卡“一天结束后，什么让你回血？”，勾选在两个选项间来回，最后弹出问号"),
        # 14
        Shot(2, "没有对错，|只是充电方式不同。", "机制示意", [
            Custom(two_full, x=540, y=560, at=0, enter="none"),
            Fig(320, GROUND, 320, at=0, mood="happy", color=M.DIM["E"], hair="short", pose="wave"),
            Fig(760, GROUND, 320, at=0, mood="smile", color=M.DIM["I"], hair="long", face=-1,
                moves=[(4, dict(pose="wave", sfx="clap", note="两人互相挥手"))]),
        ], draw=ground, hits=[(0, "wood_high", 0.7, "左边电池充满"), (1, "wood_low", 0.7, "右边电池充满")],
            note="两个人头顶的电池都充满，互相挥手"),
        end_shot(REFS, "03 S/N：看同一幅画，你先注意到什么？"),
    ]
    return Episode(2, "ei", "外向与内向", "内向的人，就是不爱说话吗？", ACC, shots, refs=REFS,
                   publish_title="内向的人，就是不爱说话吗？｜MBTI科普02 外向与内向",
                   hashtags="#MBTI #心理学 #内向 #外向 #荣格",
                   cover_title="内向的人，|就是【不爱说话】吗？", cover_sub="MBTI 的 E 与 I", cover_shot=3, cover_t=6.0,
                   notes=[
                       "第 5、6 镜：荣格在《心理类型》第 10 章用心理能量（libido）的方向区分外倾与内倾——外倾向外部对象，内倾转向主体内部。片中用大意，不是原句。",
                       "第 7 镜：荣格认为一种机制完全压倒另一种的纯粹类型并不存在，每个人两种都有，只是哪一种占优（大意）。",
                       "“从哪里充电”是通俗比喻，不是荣格或 MBTI 手册原文。",
                       "第 13 镜题目为示意，不是官方题目原文。",
                       "MBTI、Myers-Briggs Type Indicator 是 The Myers-Briggs Company 的注册商标。",
                   ], **SERIES).build()
