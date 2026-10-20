"""09 约拿情结：为什么我们害怕变得更好？"""

import math

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#3F6F8F"
GROUND = A.GROUND_Y
REFS = ["Maslow, A. H. (1971). The Farther Reaches of Human Nature, ch. 3 Neurosis as a Failure of Personal Growth. Viking.",
        "《约拿书》（Book of Jonah），旧约圣经。"]


def sea(c, g, el_t, d):
    """海面与小船上的约拿；d['swallow'] 拍之后鲸鱼出现并张嘴。"""
    K.rr(c, 0, 220, 1000, 400, 0, K.mix(A.SEA, K.BG, 0.55))
    for i in range(6):
        x = -450 + i * 180 + math.sin(g.t * 2 + i) * 10
        K.seg(c, x, 30, x + 90, 30, K.PAPER, 6, 0.7)
    q = ease_out(clamp01(g.since(d.get("swallow", 99)) / 0.8))
    bx = lerp_(160, -60, q)
    if q > 0:
        A.whale(c, -40, 150, 460, q, g.t)
    if q < 0.95:
        with K.at(c, bx, 10 + math.sin(g.t * 2) * 6):
            K.poly(c, [(-110, 0), (110, 0), (80, 50), (-80, 50)], K.mix(K.GOLD, K.DARK, 0.4), 1 - q)
            K.seg(c, 0, 0, 0, -160, K.INK2, 6, 1 - q)
            K.poly(c, [(6, -150), (90, -40), (6, -40)], K.PAPER, 1 - q)
            K.figure(c, -50, 4, 120, "hide", K.HERO, K.SKIN, 1 - q, 1, "worried", "short")


def lerp_(a, b, k):
    return a + (b - a) * k


def build() -> Episode:
    shots = [
        Shot(3, "机会来了|你却先打了退堂鼓", "情境演绎", [
            Icon("door", 780, 860, 300, color=K.GOLD, at=0, sfx="wood_low", note="发光的门"),
            Custom(lambda c, g, t, d: K.spotlight(c, 0, 0, 260, K.GOLD, 0.4 * clamp01(t / 0.6)), x=780, y=820, at=0, enter="none"),
            Fig(380, GROUND, 320, at=0, pose="stand", mood="calm", hair="short",
                moves=[(4, dict(pose="hide", mood="worried"))]),
        ], draw=A.ground, hits=[(4, "rim", 0.8, "往后缩")], note="门开着发光，人却往后缩"),
        Shot(3, "马斯洛发现|人不只怕失败，也怕成功", "马斯洛原著 · 大意", [
            Card("怕失败", 340, 700, 46, at=0, rot=-3, sfx="wood_low"),
            Card("怕成功", 740, 820, 46, at=4, rot=2, accent=ACC, sfx="tom", note="第二张卡更出人意料"),
        ], note="两张卡：怕失败、怕成功"),
        Shot(2, "他借《圣经》的故事|叫它——", "马斯洛的视角", [
            Custom(lambda c, g, t, d: A.whale(c, 0, 0, 520, 0, g.t), x=540, y=780, at=0, sfx="wood_low"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "鲸鱼定格")], note="一条大鱼"),
        Shot(4, "逃避自己的|最好可能", "马斯洛原著 · 大意", [
            Big("约拿情结", 540, 600, 150, at=0, sfx="kick", sub="Jonah Complex", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.whale(c, 0, 0, 300, 0, g.t), x=540, y=960, at=2, enter="fade"),
        ], note="drop 处“约拿情结”砸下"),
        Shot(4, "约拿被交付使命|却坐船逃走", "词源", [
            Custom(sea, x=540, y=820, at=0, enter="fade", sfx="wood_low"),
        ], hits=[(4, "wood_high", 0.6, "小船摇晃")], note="约拿坐船逃走"),
        Shot(4, "被大鱼吞下|最后还是回到了使命", "词源", [
            Custom(sea, x=540, y=820, at=0, enter="none", swallow=2),
        ], hits=[(2, "kick", 0.8, "大鱼张口")], note="大鱼张口吞下小船"),
        Shot(4, "我们也会躲开|自己最大的可能", "马斯洛原著 · 大意", [
            Fig(340, GROUND, 320, at=0, pose="cover", mood="worried", hair="short"),
            Custom(lambda c, g, t, d: A.sprout_grow(c, 0, 0, 380, clamp01(g.since(2) / 2.4)), x=760, y=1110, at=0, enter="none"),
        ], draw=A.ground, hits=[(2, "wood_low", 0.6, "芽长出")], note="人捂着眼，不看身边长高的芽"),
        Shot(2, "怕显得自大|怕担不起", "马斯洛原著 · 大意", [
            Icon("crown", 540, 720, 200, color=K.GOLD, at=0, sfx="wood_low"),
            Icon("baggage", 540, 920, 140, color=K.INK2, at=2, sfx="wood_low"),
        ], text_beat=0, note="皇冠与沉重的行李"),
        Shot(2, "也怕被人说|“你算老几”", "机制示意", [
            Fig(360, GROUND, 300, at=0, pose="sad", mood="worried", hair="short"),
            Bubble("你算老几？", 760, 620, 40, at=1, sfx="rim"),
            Fig(780, GROUND, 300, at=0, color=K.OTHER3, pose="point", mood="angry", face=-1),
        ], draw=A.ground, text_beat=0, note="别人的嘲讽"),
        Shot(3, "他常问学生：|谁打算成为伟大的人？", "马斯洛自述", [
            Fig(260, GROUND, 330, at=0, pose="point", mood="open", hair="short", color="#6A5A4A"),
            Fig(600, GROUND, 260, at=0, color=K.OTHER, mood="flat"),
            Fig(760, GROUND, 260, at=0, color=K.OTHER2, mood="flat", hair="bun"),
            Fig(920, GROUND, 260, at=0, color=K.OTHER3, mood="flat", face=-1),
            Bubble("谁会成为伟大的人？", 380, 600, 36, at=2, sfx="wood_high"),
        ], draw=A.ground, note="课堂上马斯洛提问"),
        Shot(3, "学生们笑着躲开|他问：不是你，那会是谁？", "马斯洛自述", [
            Fig(260, GROUND, 330, at=0, enter="none", pose="point", mood="smile", hair="short", color="#6A5A4A"),
            Fig(600, GROUND, 260, at=0, enter="none", color=K.OTHER, mood="worried", moves=[(2, dict(pose="hide"))]),
            Fig(760, GROUND, 260, at=0, enter="none", color=K.OTHER2, mood="worried", hair="bun", moves=[(2, dict(pose="cover"))]),
            Fig(920, GROUND, 260, at=0, enter="none", color=K.OTHER3, mood="worried", face=-1, moves=[(2, dict(pose="hide"))]),
            Bubble("不是你，那会是谁？", 380, 600, 36, at=4, sfx="tom"),
        ], draw=A.ground, hits=[(2, "wood_low", 0.6, "学生们躲开")], note="学生们躲开，马斯洛反问"),
        Shot(2, "承认自己的潜力|不等于自大", "马斯洛的视角", [
            Icon("check", 540, 760, 170, color=K.GREEN, at=0, sfx="clap"),
        ], text_beat=0, note="打勾"),
        Shot(2, "试试：写下一件|想做又不敢说的事", "小练习", [
            Icon("book", 540, 760, 200, color=ACC, at=0, sfx="wood_high"),
        ], text_beat=0, note="本子"),
        Shot(2, "下一讲：|自我实现之后还有什么", "下一讲", [
            Icon("sun", 540, 760, 220, color=K.GOLD, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 10 讲：自我超越"),
        end_shot(REFS, "10 自我超越：自我实现之后，还有什么？"),
    ]
    return Episode(9, "jonah", "约拿情结", "为什么我们害怕变得更好？", ACC, shots, refs=REFS,
                   publish_title="为什么我们害怕变得更好？｜马斯洛心理学09 约拿情结",
                   hashtags="#马斯洛 #心理学 #约拿情结 #潜能",
                   cover_title="为什么我们|【害怕】变得更好？", cover_sub="马斯洛的约拿情结", cover_shot=0, cover_t=6.0,
                   notes=["约拿情结见马斯洛遗著《人性能达到的境界》（1971）第 3 章：人不仅害怕自己最坏的一面，也害怕自己最好的一面，"
                          "会回避自己的潜能；他提到这一名称得自友人 Frank Manuel 的建议。",
                          "约拿的故事见旧约《约拿书》：约拿受命去尼尼微却乘船逃往他施，被大鱼吞下，三日后被吐出并前往尼尼微。",
                          "课堂提问“谁打算成为伟大的人？……如果不是你，那会是谁？”为马斯洛在同书中自述的大意。"]).build()
