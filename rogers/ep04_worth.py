"""04 价值条件：为什么总觉得表现好才配被爱？"""

import math

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = A.CLAY
GROUND = A.GROUND_Y
REFS = ["Rogers, C. R. (1959). A theory of therapy, personality, and interpersonal relationships. In S. Koch (Ed.), Psychology: A Study of a Science.",
        "Assor, A., Roth, G., & Deci, E. L. (2004). The emotional costs of parents' conditional regard. Journal of Personality, 72(1), 47–88."]


def heart_el(c, g, el_t, d):
    A.tag_heart(c, 0, 0, d.get("s", 180), d.get("cond", "考第一"), 1, 6 * math.sin(g.t * 2.2))


def build() -> Episode:
    shots = [
        Shot(3, "考了第一，爸妈很高兴|考砸了，家里就冷了", "情境演绎", [
            Fig(260, GROUND, 340, at=0, color=K.OTHER, pose="cheer", mood="happy",
                moves=[(6, dict(pose="block", mood="angry"))]),
            Fig(560, GROUND, 220, at=0, pose="stand", mood="happy", hair="short",
                moves=[(6, dict(pose="sad", mood="sad"))]),
            Card("100 分", 820, 640, 46, at=2, rot=3, accent=K.GREEN, sfx="wood_high", out=6),
            Card("60 分", 820, 640, 46, at=6, rot=-3, accent=K.RED, sfx="rim"),
        ], draw=A.ground, note="分数高时家长欢呼，分数低时脸色一变"),
        Shot(3, "孩子慢慢学会：|我得表现好，才配被爱", "罗杰斯原著 · 大意", [
            Custom(heart_el, x=460, y=760, at=2, sfx="wood_low", note="带价签的爱心"),
        ], hits=[(6, "rim", 0.7, "价签晃动")], note="一颗挂着价签“考第一”的爱心"),
        Shot(2, "罗杰斯把这|叫作——", "罗杰斯的视角", [
            Custom(heart_el, x=460, y=760, at=0, enter="none", s=220),
        ], text_beat=0, hits=[(4, "rim", 0.8, "爱心定格")], note="价签爱心放大"),
        Shot(4, "只有怎样怎样|我才有价值", "罗杰斯原著 · 大意", [
            Big("价值条件", 540, 600, 150, at=0, sfx="kick", sub="Conditions of Worth", note="概念落版（音乐 drop）"),
            Custom(heart_el, x=460, y=960, at=2, enter="fade", s=120, cond="只有……"),
        ], note="drop 处“价值条件”砸下"),
        Shot(4, "“乖才可爱”|“哭就不是男子汉”", "情境演绎", [
            Card("乖才可爱", 340, 680, 46, at=0, rot=-3, sfx="wood_low"),
            Card("哭就不是男子汉", 640, 860, 46, at=4, rot=2, sfx="wood_low"),
        ], note="两句常见的“条件”"),
        Shot(4, "这些条件被吞进心里|变成了自己的标准", "罗杰斯原著 · 大意", [
            Fig(540, GROUND, 340, at=0, pose="stand", mood="flat", hair="short"),
            Card("只有……", 820, 520, 40, at=0, rot=3, sfx="wood_low"),
            Arrow((780, 580), (580, 780), at=4, color=ACC, width=12, sfx="tom", note="条件进入人心里"),
        ], draw=A.ground, note="条件卡片被吸进人的胸口"),
        Shot(4, "于是人会否认|不符合条件的感受", "罗杰斯原著 · 大意", [
            Fig(400, GROUND, 330, at=0, pose="block", mood="worried", hair="short"),
            Card("生气", 760, 700, 44, at=2, rot=-4, fill=K.DARK, color=K.PAPER, sfx="wood_low"),
            Card("害怕", 820, 880, 44, at=4, rot=3, fill=K.DARK, color=K.PAPER, sfx="wood_low", gain=0.85),
        ], draw=A.ground, note="人伸手挡开“生气”“害怕”"),
        Shot(2, "比如明明很累|却不敢承认", "机制示意", [
            Fig(540, GROUND, 320, at=0, pose="stand", mood="smile", hair="short"),
            Bubble("我不累", 680, 600, 40, at=1, sfx="wood_high"),
        ], draw=A.ground, text_beat=0, note="强撑着说“我不累”"),
        Shot(2, "长大以后|还在为“条件”打工", "机制示意", [
            Fig(400, GROUND, 320, at=0, pose="carry", mood="worried", hair="short"),
            Icon("brief", 760, 900, 160, color=K.DARK, at=1, sfx="wood_low"),
        ], draw=A.ground, text_beat=0, note="背着重担的成年人"),
        Shot(3, "研究：有条件的关爱|和自尊不稳有关", "研究证据", [
            Custom(heart_el, x=460, y=720, at=0, s=150, sfx="wood_low"),
            Txt("Assor, Roth & Deci，2004", 540, 940, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="有条件的关爱研究"),
        Shot(3, "它往往不是谁故意的|而是一代代传下来的", "当代理解", [
            Fig(240, GROUND, 360, at=0, color=K.OTHER, mood="calm"),
            Fig(540, GROUND, 320, at=1, color=K.OTHER3, mood="calm", hair="bun", sfx="wood_low"),
            Fig(820, GROUND, 220, at=2, mood="calm", hair="short", sfx="wood_low"),
        ], draw=A.ground, note="祖辈、父母、孩子三代"),
        Shot(2, "可以爱一个人|但不认同他的行为", "罗杰斯的视角", [
            Icon("heart", 540, 760, 220, color=K.RED, at=0, sfx="wood_high"),
        ], text_beat=0, note="不带价签的爱心"),
        Shot(2, "试试：你心里|有哪句“只有……才……”？", "小练习", [
            Card("只有……才……", 540, 760, 48, at=0, sfx="wood_high"),
        ], text_beat=0, note="卡片"),
        Shot(2, "下一讲：|不附加条件的接纳", "下一讲", [
            Icon("heart", 540, 760, 200, color="#B05070", at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 05 讲：无条件积极关注"),
        end_shot(REFS, "05 无条件积极关注：接纳一个人，等于认同一切吗？"),
    ]
    return Episode(4, "worth", "价值条件", "为什么总觉得表现好才配被爱？", ACC, shots, refs=REFS,
                   publish_title="为什么总觉得表现好才配被爱？｜罗杰斯心理学04 价值条件",
                   hashtags="#罗杰斯 #心理学 #原生家庭 #自尊",
                   cover_title="为什么总觉得|【表现好】才配被爱？", cover_sub="罗杰斯的价值条件", cover_shot=1, cover_t=5.0,
                   notes=["价值条件见罗杰斯 1959 年的理论总论：当重要他人的关注带有条件，个体会把这些条件内化为自己的价值标准，"
                          "并否认或扭曲不符合条件的经验。",
                          "Assor、Roth 与 Deci（2004）发现，父母“有条件的关注”与子女的不稳定自尊、对父母的怨恨等相关；片中为通俗概括。",
                          "“乖才可爱”“哭就不是男子汉”为片中示例，非罗杰斯原文。"]).build()
