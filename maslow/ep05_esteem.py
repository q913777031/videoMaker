"""05 尊重需要：为什么我们那么在乎被认可？"""

import math

from engine.gfx import clamp01, ease_in, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#5B6FA8"
GROUND = A.GROUND_Y
REFS = ["Maslow, A. H. (1943). A Theory of Human Motivation. Psychological Review, 50(4), 370–396.",
        "Maslow, A. H. (1954/1970). Motivation and Personality, ch. 4. Harper & Row."]


def like_tower(c, g, el_t, d):
    """点赞叠成的塔：fall 拍之后倾倒。"""
    f = ease_in(clamp01(g.since(d.get("fall", 4)) / 0.8))
    for i in range(5):
        with K.at(c, f * (i * 40), 200 - i * 100 + f * i * 30, f * (8 + i * 9)):
            K.rr(c, 0, 0, 200, 80, 14, K.PAPER)
            K.rr_stroke(c, 0, 0, 200, 80, 14, K.INK2, 4)
            K.heart(c, -50, 0, 40, K.RED)
            K.text(c, "+1", 30, 0, 34, "sans_medium", K.INK2)


def build() -> Episode:
    shots = [
        Shot(3, "发了条朋友圈|一直刷有没有人点赞", "情境演绎", [
            Fig(380, GROUND, 330, at=0, pose="stand", mood="worried", hair="short"),
            Icon("phone", 520, 820, 110, color=K.INK2, at=0, enter="none"),
            Icon("heart", 720, 640, 90, color=K.RED, at=4, sfx="wood_high", note="一个赞"),
            Icon("heart", 820, 560, 70, color=K.RED, at=6, sfx="wood_high", gain=0.8),
        ], draw=A.ground, note="盯着手机等点赞"),
        Shot(3, "马斯洛说|人还需要被看重", "马斯洛原著 · 大意", [
            Custom(A.levels, x=540, y=760, at=0, seq=[(0, 2), (4, 3)], sfx="wood_low"),
        ], hits=[(4, "tom", 0.8, "高亮上移到尊重")], note="高亮从归属上移到尊重"),
        Shot(2, "这一层|叫作——", "马斯洛的视角", [
            Icon("trophy", 540, 760, 240, color=ACC, at=0, sfx="rim"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "奖杯定格")], note="奖杯"),
        Shot(4, "自己看得起自己|也被别人看得起", "马斯洛原著 · 大意", [
            Big("尊重需要", 540, 600, 150, at=0, sfx="kick", sub="Esteem Needs", note="概念落版（音乐 drop）"),
            Icon("trophy", 540, 930, 120, color=ACC, at=2, enter="fade"),
        ], note="drop 处“尊重需要”砸下"),
        Shot(4, "一种来自自己：|能力、成就、独立", "马斯洛原著 · 大意", [
            Fig(260, GROUND, 300, at=0, pose="proud", mood="smile", hair="short"),
            Card("能力", 640, 600, 42, at=2, rot=-2, accent=ACC, sfx="wood_low"),
            Card("成就", 820, 760, 42, at=4, rot=2, accent=ACC, sfx="wood_low", gain=0.85),
            Card("独立", 640, 920, 42, at=6, rot=-1, accent=ACC, sfx="wood_low", gain=0.75),
        ], draw=A.ground, note="自尊：能力、成就、独立"),
        Shot(4, "一种来自别人：|名声、认可、关注", "马斯洛原著 · 大意", [
            Fig(260, GROUND, 300, at=0, pose="wave", mood="happy", hair="short"),
            Card("名声", 640, 600, 42, at=2, rot=2, sfx="wood_high"),
            Card("认可", 820, 760, 42, at=4, rot=-2, sfx="wood_high", gain=0.85),
            Card("关注", 640, 920, 42, at=6, rot=1, sfx="wood_high", gain=0.75),
        ], draw=A.ground, note="他尊：名声、认可、关注"),
        Shot(4, "最稳的自尊|来自配得上的尊重", "马斯洛原著 · 大意", [
            Icon("scale", 540, 720, 240, color=ACC, at=0, sfx="wood_low"),
            Label("配得上", 540, 960, 40, at=4, fill=ACC, sfx="wood_high"),
        ], note="天平平衡：名实相符"),
        Shot(2, "而不是虚名|和别人的吹捧", "马斯洛原著 · 大意", [
            Card("虚名", 540, 720, 48, at=0, rot=-3, sfx="wood_low"),
            Icon("cross", 540, 880, 100, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="“虚名”打叉"),
        Shot(2, "这层受挫|人会觉得自卑、无助", "马斯洛原著 · 大意", [
            Fig(540, GROUND, 320, at=0, pose="sad", mood="sad", hair="short"),
        ], draw=A.ground, text_beat=0, note="垂头的人"),
        Shot(3, "只靠点赞撑着的自尊|一阵风就倒", "机制示意", [
            Custom(like_tower, x=540, y=760, at=0, fall=4, sfx="wood_low"),
        ], hits=[(4, "tom", 0.9, "点赞塔倒下")], note="点赞叠成的塔倒下"),
        Shot(3, "靠能力长出来的自尊|更扎得住", "机制示意", [
            Custom(lambda c, g, t, d: A.sprout_grow(c, 0, 0, 440, clamp01(t / 3.0)), x=540, y=980, at=0, sfx="wood_low"),
        ], hits=[(6, "wood_high", 0.7, "叶子展开")], note="一棵扎根的芽"),
        Shot(2, "被认可很重要|但别全交给别人", "马斯洛的视角", [
            Icon("heart", 400, 760, 140, color=K.RED, at=0, sfx="wood_low"),
            Icon("trophy", 680, 760, 160, color=ACC, at=2, sfx="wood_low"),
        ], text_beat=0, note="点赞与奖杯并列"),
        Shot(2, "试试：写下一件|靠自己做成的事", "小练习", [
            Icon("check", 540, 760, 180, color=K.GREEN, at=0, sfx="clap"),
        ], text_beat=0, note="打勾"),
        Shot(2, "下一讲：|活成自己的人什么样", "下一讲", [
            Custom(A.levels, x=540, y=760, at=0, hi=4, w=560, lh=86, sfx="wood_high"),
        ], text_beat=0, note="预告第 06 讲：自我实现"),
        end_shot(REFS, "06 自我实现：活成自己的人是什么样？"),
    ]
    return Episode(5, "esteem", "尊重需要", "为什么我们那么在乎被认可？", ACC, shots, refs=REFS,
                   publish_title="为什么我们那么在乎被认可？｜马斯洛心理学05 尊重需要",
                   hashtags="#马斯洛 #心理学 #自尊 #认可",
                   cover_title="为什么那么在乎|【被认可】？", cover_sub="马斯洛的尊重需要", cover_shot=9, cover_t=5.0,
                   notes=["尊重需要见马斯洛 1943 年论文：一类是实力、成就、胜任与独立，另一类是名声、地位、认可与关注；受挫会带来自卑、软弱与无助感。",
                          "“最稳定、最健康的自尊建立在应得的尊重之上，而不是外在的名声或无根据的吹捧”为《动机与人格》第 4 章说法的大意。",
                          "“点赞”是片中的现代示例，非马斯洛原文。"]).build()
