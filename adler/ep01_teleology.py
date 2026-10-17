"""01 目的论：过去，真的决定了现在的你吗？"""

import math

import skia

from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, lerp

from . import kit as K
from .core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

ACC = "#E2603F"
GROUND = 1130


def kids_laughing(c, w, h):
    """回忆照片里的小场景：三个小孩指着中间的小主角笑。"""
    gy = h / 2 - 20
    K.figure(c, 10, gy, 170, "sad", K.HERO, mood="sad", hair="short", lift=0.3)
    for x, f, cc in ((-140, 1, K.OTHER), (150, -1, K.OTHER3)):
        K.figure(c, x, gy + 6, 150, "point", cc, mood="happy", face=f, lift=0.3, hair="bun" if x > 0 else None)


def ground(g):
    K.ground(g.c, GROUND)


def dominoes(c, g, el_t, d):
    """五块骨牌从“过去”向“现在”依次倒下，每块落在一个实测拍点上。"""
    n = 5
    for i in range(n):
        k = clamp01((g.since(d["b0"] + i) + 0.3) / 0.3)
        ang = 64 * ease_in(k)
        K.domino(c, -330 + i * 120 + 34, 0, 44, 150, ang, K.mix(K.INK3, ACC, i / (n - 1)))


def flip_arrow(c, g, el_t, d):
    """一支大箭头：先从身后指向主角（过去→现在），第 4 拍转到身前指向远处（现在→目的）。"""
    k = ease_in_out(clamp01(g.since(4) / 0.35))
    ang = lerp(0, 1, k)
    if ang < 0.5:
        x0, x1, a = -420, -110, 1 - ang * 2
        K.arrow(c, (x0, 0), (x1, 0), K.INK3, 16, a, 1, 0, 44)
    else:
        x0, x1, a = 110, 420, (ang - 0.5) * 2
        K.arrow(c, (x0, 0), (x1, 0), ACC, 16, a, 1, 0, 44)
    K.burst(c, 0, 0, g.since(4), ACC, 120, 260, 10, 7)


def shield_house(c, g, el_t, d):
    K.icon(c, "house", 0, 0, 420, K.HERO, 1, 0.8, 0, 1, 0.0, ACC)


def two_paths(c, g, el_t, d):
    """同一张回忆照片分出两条路。"""
    p = ease_out(clamp01(g.since(2) / 0.6))
    K.arrow(c, (0, -40), (-280, 260), K.INK3, 10, 1, p, 0.15, 30)
    K.arrow(c, (0, -40), (280, 260), ACC, 10, 1, p, -0.15, 30)


def rewrite_card(c, g, el_t, d):
    """改写练习：旧句子被划掉，新句子从下方翻上来。"""
    old = "因为被嘲笑过，|所以我不去。"
    new = "我想交到朋友，|所以先去一次。"
    a_old = 1 - 0.55 * clamp01(g.since(4) / 0.3)
    K.text_card(c, 0, -170, old.split("|"), 44, 640, K.PAPER, K.INK2, ACC, a_old, -2)
    strike = ease_out(clamp01(g.since(4) / 0.3))
    if strike > 0:
        K.seg(c, -260, -170, -260 + 520 * strike, -190, ACC, 9)
    k = clamp01(g.since(8) / 0.4)
    if k > 0:
        K.text_card(c, 0, 120, ["【我想】交到朋友，", "所以【先去】一次。"], 48, 680, K.PAPER, K.INK, ACC, k, 1.5,
                    0.6 + 0.4 * K.ease_out_back(k, 1.6), accent=ACC)


def heart_patch(c, g, el_t, d):
    K.heart(c, 0, 0, 330, K.mix(ACC, K.PAPER, 0.15))
    crack = [(-10, -110), (25, -60), (-15, -15), (20, 30), (-5, 70)]
    path = skia.Path()
    path.moveTo(*crack[0])
    for q in crack[1:]:
        path.lineTo(*q)
    c.drawPath(path, K.paint(K.PAPER, 1, 10))
    k = clamp01(g.since(2) / 0.35)
    if k > 0:
        with K.at(c, 0, -20, -35, 0.6 + 0.4 * K.ease_out_back(k, 2)):
            K.rr(c, 0, 0, 230, 70, 30, "#F1D6B8", k)
            K.rr(c, 0, 0, 70, 66, 6, "#E5C29E", k)
            for dx in (-14, 14):
                for dy in (-14, 14):
                    K.dot(c, dx, dy, 4, "#C9A47E", k)


def build() -> Episode:
    shots = [
        Shot(3, "“我不敢去社交，|因为小时候被嘲笑过”", "情境演绎", [
            Fig(360, GROUND, 380, at=0, mood="worried", hair="short",
                moves=[(4, dict(pose="sad", mood="sad")),
                       (8, dict(face=-1, pose="cover", sfx="rim", note="主角转身捂脸，背对门口"))]),
            Icon("door", 800, 950, 330, color=K.DARK, accent=K.GOLD, p=0.25, at=1, sfx="wood_low", note="门出现"),
            Custom(lambda c, g, t, d: K.memory(c, 0, 0, 420, 330, kids_laughing, 1, -4, 1, "小时候"),
                   x=330, y=520, at=4, enter="pop", sfx="kick", note="回忆照片弹出：小时候被嘲笑"),
        ], draw=ground, text_beat=1, note="主角站在门前犹豫，身后弹出小时候被嘲笑的回忆照片；他转身捂脸"),
        Shot(3, "很合理吧？|过去的伤，造成了现在的我。", "机制示意", [
            Custom(dominoes, x=430, y=GROUND, at=0, enter="none", b0=2,
                   note="骨牌从过去倒向现在"),
            Label("过去", 200, 860, at=0, fill=K.INK3),
            Label("现在", 830, 640, at=7, fill=ACC, sfx="wood_high", note="“现在”标签亮起"),
            Fig(830, GROUND, 330, at=0, enter="none", pose="sad", mood="sad", hair="short", face=-1,
                moves=[(6, dict(pose="crouch", sfx="tom", note="最后一块骨牌撞到主角"))]),
        ], draw=ground, hits=[(2, "wood_low", 0.8, "第 1 块骨牌倒下"), (3, "wood_low", 0.7, "第 2 块"),
                              (4, "wood_low", 0.7, "第 3 块"), (5, "wood_low", 0.7, "第 4 块")],
            note="五块骨牌按拍依次倒下，最后撞到主角——“原因论”的直觉"),
        Shot(2, "阿德勒的视角|正好相反：", "阿德勒的视角", [
            Fig(540, GROUND, 360, at=0, enter="none", pose="stand", mood="calm", hair="short",
                moves=[(4, dict(pose="point", mood="open"))]),
            Custom(flip_arrow, x=540, y=820, at=0, enter="fade", sfx=None),
            Icon("question", 900, 600, 120, color=ACC, at=5, enter="pop", sfx="wood_high", note="问号弹出"),
        ], draw=ground, hits=[(4, "rim", 1.0, "箭头从身后转到身前")], text_beat=0,
            note="箭头从“身后指向我”转为“从我指向前方”"),
        Shot(3, "理解一个行为，|要看它“为了什么”。", "阿德勒原著 · 大意", [
            Big("目的论", 540, 560, 160, at=0, sfx="kick", sub="Teleology · 阿德勒个体心理学", note="概念落版（音乐 drop）"),
            Icon("target", 820, 930, 230, color=K.HERO, accent=ACC, at=2, enter="pop", sfx="wood_low", note="靶子出现"),
            Fig(260, GROUND, 320, at=1, pose="stand", hair="short",
                moves=[(4, dict(pose="point", sfx="tom", note="主角指向靶心"))]),
            Arrow((330, 990), (720, 935), at=4, color=ACC, width=12, bend=-0.12),
        ], draw=ground, note="drop 处“目的论”砸下；主角指向靶心"),
        Shot(3, "不出门，也许正是为了：|不被评价，不再受伤。", "岸见一郎阐释", [
            Custom(shield_house, x=380, y=880, at=0, enter="grow", sfx="wood_low", note="房子升起"),
            Fig(380, 1065, 190, at=0, enter="none", pose="sit_sad", mood="sad", hair="short", lift=0.3),
            Icon("shield", 380, 650, 150, color=ACC, at=2, enter="pop", sfx="rim", note="屋顶上方出现盾牌"),
            Bubble("60分", 840, 640, 40, at=4, tail=(-0.3, 1), sfx="wood_high", note="外面的评价气泡"),
            Bubble("好怪", 760, 520, 40, at=5, tail=(0.3, 1), sfx="wood_high", gain=0.8),
            Fig(860, GROUND, 250, at=3, color=K.OTHER2, face=-1, mood="flat", pose="point"),
        ], draw=ground, note="主角坐在屋里，盾牌护住房子；屋外是评价与议论"),
        Shot(3, "决定我们的不是经历本身，|而是我们赋予它的意义。", "阿德勒原著 · 大意", [
            Custom(lambda c, g, t, d: K.memory(c, 0, 0, 440, 340, kids_laughing, 1, 2, 1, "同一段经历"),
                   x=540, y=700, at=0, enter="pop", sfx="wood_low", note="同一张回忆照片"),
            Label("意义 = ？", 540, 950, 44, at=4, enter="slam", dur=0.22, fill=ACC, sfx="rim", note="“意义＝？”标签砸在照片下"),
            Icon("book", 870, 1050, 150, color=K.HERO, at=6, enter="pop", sfx="shaker", note="书本图标"),
            Txt("《自卑与超越》第1章，1931", 840, 1150, 28, at=6, font="sans_medium", color=K.INK2),
        ], note="回忆照片下方砸下“意义＝？”，出处书本浮现"),
        Shot(3, "同样被嘲笑过，|有人躲起来，有人去练表达。", "情境演绎", [
            Custom(lambda c, g, t, d: K.memory(c, 0, 0, 300, 240, kids_laughing, 1, 0, 1, ""),
                   x=540, y=540, at=0, enter="none"),
            Custom(two_paths, x=540, y=720, at=2, enter="none", sfx="shaker", note="两条路分开"),
            Icon("house", 250, 1010, 220, color=K.INK3, accent=K.INK2, p=0, at=4, enter="pop", sfx="wood_low",
                 note="左：回到屋里"),
            Fig(380, GROUND, 250, at=4, pose="sad", mood="sad", hair="short", face=-1, color=K.mix(K.HERO, K.INK3, 0.4)),
            Icon("megaphone", 900, 960, 150, color=ACC, at=8, enter="pop", note="右：拿起话筒"),
            Fig(740, GROUND, 290, at=6, pose="stand", mood="smile", hair="short",
                moves=[(8, dict(pose="cheer", mood="happy", sfx="clap", note="右边的人举手练表达"))]),
        ], draw=ground, note="同一张照片分出两条路：左边回屋，右边拿起话筒"),
        Shot(2, "这不是说，|创伤不存在。", "常见误解", [
            Custom(heart_patch, x=540, y=760, at=0, enter="pop", sfx="frame", note="带裂痕的心"),
        ], text_beat=0, hits=[(2, "wood_low", 0.8, "贴上创可贴")], note="一颗有裂痕的心，贴上创可贴"),
        Shot(2, "痛是真的，|只是不必成为终点。", "常见误解", [
            Custom(lambda c, g, t, d: K.road(c, -480, 0, 480, 0, K.LINE, 70, 1, ease_out(clamp01(g.since(0) / 0.8)))
                   , x=540, y=GROUND + 36, at=0, enter="none"),
            Icon("flag", 940, 1000, 160, accent=ACC, at=3, enter="pop", sfx="wood_high", note="远处的小旗"),
            Fig(200, GROUND, 300, at=0, enter="none", pose="stand", mood="calm", hair="short",
                moves=[(1, dict(x=620, dur=2.6, ease="io"))]),
            Txt("若长期被困扰，请寻求专业帮助", 540, 1250, 30, at=4, font="sans_medium", color=K.INK2),
        ], text_beat=0, note="主角沿路继续走向远处的小旗；底部提示寻求专业帮助"),
        Shot(3, "当你说|“因为……所以我不能”时，", "小练习", [
            Fig(330, GROUND, 360, at=0, pose="shrug", mood="worried", hair="short"),
            Bubble("因为……|所以我不能……", 690, 700, 46, at=2, tail=(-0.6, 1), sfx="wood_high", note="主角说出口头禅"),
            Icon("cross", 860, 900, 110, color=ACC, at=8, enter="pop", sfx="rim", note="停一下"),
        ], draw=ground, note="主角摊手，气泡里是“因为……所以我不能……”"),
        Shot(3, "试着问：|这个理由，帮我躲开了什么？", "小练习", [
            Icon("shield", 300, 820, 300, color=K.HERO, at=0, enter="none", lift=1.2,
                 moves=[(2, dict(x=235, rot=-12, sfx="shaker", note="盾牌移开"))]),
            Card("被拒绝", 720, 640, 44, at=4, rot=-3, sfx="wood_high", note="藏着的卡片 1"),
            Card("会失败", 760, 820, 44, at=5, rot=2, sfx="wood_high", gain=0.85, note="藏着的卡片 2"),
            Card("被评价", 700, 1000, 44, at=6, rot=-1, sfx="wood_high", gain=0.75, note="藏着的卡片 3"),
            Fig(460, GROUND, 280, at=0, enter="none", pose="think", mood="worried", hair="short"),
        ], draw=ground, note="盾牌挪开，露出背后被回避的三件事"),
        Shot(4, "再问：|我真正想要的是什么？", "小练习", [
            Icon("door", 820, 950, 330, color=K.DARK, accent=K.GOLD, at=0, enter="pop",
                 p=lambda g, t: ease_out(clamp01(g.since(8) / 0.6)) * 0.95 + 0.05, note="门"),
            Custom(lambda c, g, t, d: K.spotlight(c, 0, 0, 380, K.GOLD, 0.5 * clamp01(g.since(8) / 0.6)),
                   x=820, y=950, at=0, enter="none"),
            Bubble("想交到朋友", 560, 560, 46, at=4, tail=(-0.4, 1), think=True, sfx="bongo_high", note="心里的目的浮现"),
            Fig(320, GROUND, 360, at=0, pose="think", mood="calm", hair="short",
                moves=[(8, dict(pose="stand", mood="smile", sfx="tom", note="门打开，光照进来")),
                       (10, dict(x=600, dur=1.8))]),
        ], draw=ground, note="主角想起真正的目的，门打开，他走向门口"),
        Shot(4, "把“因为……所以不能”，|改写成“我想……所以选择”。", "小练习", [
            Custom(rewrite_card, x=540, y=780, at=0, enter="fade", note="旧句被划掉，新句翻上来"),
        ], hits=[(4, "rim", 0.9, "旧句子被划掉"), (8, "clap", 0.9, "新句子出现")],
            note="改写练习：旧句被划掉，新句翻上来"),
        Shot(2, "过去改变不了，|意义可以重新选。", "阿德勒的视角", [
            Icon("sun", 800, 600, 220, color=K.GOLD, at=0, enter="pop", sfx="cymbal", gain=0.7,
                 p=lambda g, t: t * 0.3, note="太阳升起"),
            Fig(380, GROUND, 360, at=0, enter="rise", pose="stand", mood="smile", hair="short",
                moves=[(4, dict(pose="wave", mood="happy"))]),
        ], draw=ground, text_beat=0, note="主角在阳光下挥手"),
        end_shot(["Adler, A. (1931). What Life Should Mean to You.（中译《自卑与超越》）",
                  "岸见一郎、古贺史健（2013）《被讨厌的勇气》"], "02 自卑感：觉得自己不如别人，是坏事吗？"),
    ]
    return Episode(1, "teleology", "目的论", "过去，真的决定了现在的你吗？", ACC, shots,
                   refs=["Adler, A. (1931). What Life Should Mean to You.（中译《自卑与超越》）",
                         "岸见一郎、古贺史健（2013）《被讨厌的勇气》"],
                   publish_title="过去，真的决定了现在的你吗？｜阿德勒心理学01 目的论",
                   hashtags="#阿德勒 #心理学 #被讨厌的勇气 #目的论 #自我成长",
                   cover_title="过去，真的|决定了【现在的你】吗？", cover_sub="阿德勒的目的论", cover_shot=0, cover_t=5.5,
                   notes=[
                       "第 6 镜为阿德勒原句的大意：“We are self-determined by the meaning we give to our experiences… Meanings are "
                       "not determined by situations, but we determine ourselves by the meanings we give to situations.”"
                       "（What Life Should Mean to You, 1931, ch.1 The Meaning of Life）。",
                       "阿德勒的术语是 finalism / 虚构的终极目标（fiktives Endziel）；“原因论 vs 目的论”这对说法与“不出门是为了不受伤”"
                       "的例子来自岸见一郎、古贺史健《被讨厌的勇气》第一夜，片中第 5 镜标注“岸见一郎阐释”。",
                       "片中明确“这不是说创伤不存在”：阿德勒说的是经历不决定成败，他在同一章也承认不利的童年处境需要帮助；"
                       "“创伤不存在”是岸见书中的小节标题，不是阿德勒原话。第 9 镜提示长期困扰时寻求专业帮助。",
                   ]).build()
