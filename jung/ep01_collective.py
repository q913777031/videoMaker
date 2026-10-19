"""01 集体无意识：为什么不同地方的神话这么像？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = A.INDIGO
GROUND = 1130


def ground(g):
    K.ground(g.c, GROUND)


REFS = ["Jung, C. G. (1936/1959). The Concept of the Collective Unconscious. CW 9i.",
        "Jung, C. G. (1962). Memories, Dreams, Reflections.（中译《回忆·梦·思考》）"]


def build() -> Episode:
    shots = [
        Shot(3, "为什么不同地方的神话|长得这么像？", "情境演绎", [
            Fig(220, GROUND, 300, at=0, color=K.OTHER, mood="calm"),
            Fig(540, GROUND, 300, at=0, color=K.OTHER2, mood="calm", hair="bun"),
            Fig(860, GROUND, 300, at=0, color=K.OTHER3, mood="calm", face=-1),
            Bubble("洪水", 220, 640, 40, at=2, sfx="wood_high", note="三人各讲一个故事：洪水"),
            Bubble("洪水", 540, 600, 40, at=3, sfx="wood_high", gain=0.85),
            Bubble("洪水", 860, 640, 40, at=4, sfx="wood_high", gain=0.75),
            Icon("question", 540, 420, 110, color=ACC, at=8, sfx="rim", note="问号弹出"),
        ], draw=ground, note="三个不同地方的人讲出同一个“洪水”故事"),
        Shot(3, "荣格认为|心灵深处有共同的东西", "荣格的视角", [
            Fig(360, GROUND, 360, at=0, pose="think", mood="calm", hair="short", color=A.TEAL,
                moves=[(6, dict(pose="point", mood="open"))]),
            Icon("bulb", 760, 640, 170, color=K.GOLD, at=6, sfx="tom", note="灯泡亮起"),
            Txt("卡尔·荣格（1875–1961），瑞士精神科医生", 540, 1210, 30, at=2, font="sans_medium", color=K.INK2),
        ], draw=ground, note="荣格思考后指出：心灵深处有共通的部分"),
        Shot(2, "他把这一层|叫作——", "荣格的视角", [
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 260, g.t, ease_out(clamp01(t / 1.6)), ACC), x=540, y=760, at=0),
        ], text_beat=0, hits=[(4, "rim", 0.8, "曼陀罗展开")], note="曼陀罗从中心展开，为概念落版蓄势"),
        Shot(4, "每个人都有|但没人亲身经历过", "荣格原著 · 大意", [
            Big("集体无意识", 540, 600, 140, at=0, sfx="kick", sub="Collective Unconscious", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 180, g.t, 1, ACC, alpha=0.35), x=540, y=960, at=0, enter="none"),
            Label("不来自个人经历", 540, 1030, 36, at=8, fill=ACC, sfx="wood_high", note="标签：不来自个人经历"),
        ], note="drop 处“集体无意识”砸下"),
        Shot(4, "意识之下|先是“个人无意识”", "机制示意", [
            Custom(lambda c, g, t, d: A.psyche_layers(c, 820, 760, ease_out(clamp01(g.since(2) / 1.2)), 0, g.t),
                   x=540, y=780, at=0, enter="pop", sfx="wood_low", note="意识层次图出现"),
        ], hits=[(2, "tom", 0.8, "水下的个人无意识显现")], note="水面以上是意识，水下先是个人无意识（遗忘、压抑的个人经历）"),
        Shot(4, "再往下|是人类共有的一层", "机制示意", [
            Custom(lambda c, g, t, d: A.psyche_layers(c, 820, 760, 1, ease_out(clamp01(g.since(2) / 1.4)), g.t),
                   x=540, y=780, at=0, enter="none"),
        ], hits=[(2, "kick", 0.8, "最深处连成一片")], note="三座岛在最深处连成一片：集体无意识（示意图）"),
        Shot(4, "里面不是具体的记忆|而是共同的“倾向”", "荣格原著 · 大意", [
            Card("具体记忆", 300, 700, 46, at=0, rot=-3, sfx="wood_low", note="卡片：具体记忆"),
            Icon("cross", 300, 880, 90, color=K.RED, at=2, sfx="rim", note="打叉"),
            Card("共同倾向", 780, 700, 46, at=4, rot=2, accent=ACC, sfx="wood_low", note="卡片：共同倾向"),
            Icon("check", 780, 880, 90, color=K.GREEN, at=6, sfx="clap", note="打勾"),
        ], note="“具体记忆”打叉，“共同倾向”打勾"),
        Shot(2, "就像鸟会筑巢|不用谁来教", "荣格原著 · 大意", [
            Custom(lambda c, g, t, d: _nest(c, g), x=540, y=760, at=0, enter="pop", sfx="wood_high", note="鸟巢"),
        ], text_beat=0, note="鸟和巢：本能式的、与生俱来的模式"),
        Shot(2, "荣格把它比作本能|在心灵里的样子", "荣格原著 · 大意", [
            Icon("eye", 540, 760, 220, color=ACC, at=0, enter="pop", sfx="tom", note="内观之眼"),
        ], text_beat=0, note="原型被荣格视为与本能相对应的心理模式"),
        Shot(3, "他做过一个梦|房子一层比一层古老", "荣格自述", [
            Custom(lambda c, g, t, d: A.dream_house(c, 640, 720, ease_out(clamp01(g.since(1) / 2.8))), x=540, y=800, at=0,
                   enter="pop", sfx="wood_low", note="梦中的房子"),
        ], hits=[(4, "tom", 0.7, "揭开到地下室"), (8, "tom", 0.8, "揭开到洞穴")],
            note="房子由上往下揭开：客厅、中世纪房间、古罗马地下室、史前洞穴"),
        Shot(3, "最底下的洞穴|他理解为心灵最古老的层", "荣格自述", [
            Custom(lambda c, g, t, d: A.dream_house(c, 640, 720, 1), x=540, y=800, at=0, enter="none"),
            Custom(lambda c, g, t, d: K.spotlight(c, 0, 0, 260, K.GOLD, 0.5 * clamp01(t / 0.6)), x=540, y=1070, at=2, enter="none"),
        ], hits=[(2, "rim", 0.8, "洞穴被照亮")], note="洞穴被照亮：荣格据此思考集体性的、更古老的心灵层次"),
        Shot(2, "这个观点|很难用实验直接证明", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, enter="pop", sfx="wood_low", note="天平"),
            Icon("question", 760, 560, 100, color=K.RED, at=4, sfx="rim", note="问号"),
        ], note="科学界对“集体无意识”多有质疑，难以直接检验"),
        Shot(2, "但它提醒我们|人心深处相通", "荣格的视角", [
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 220, g.t, ease_out(clamp01(t / 2)), ACC, alpha=0.5), x=540, y=700, at=0),
            Fig(300, GROUND, 280, at=0, color=K.OTHER, pose="hug", mood="smile"),
            Fig(540, GROUND, 280, at=1, color=K.OTHER2, pose="hug", mood="smile", hair="bun"),
            Fig(780, GROUND, 280, at=2, color=K.OTHER3, pose="hug", mood="smile", face=-1),
        ], draw=ground, hits=[(6, "cymbal", 0.5, "曼陀罗定格")], note="三个人并肩，身后曼陀罗展开"),
        Shot(2, "那些反复出现的形象|叫“原型”", "下一讲", [
            Card("母亲 · 英雄 · 智者 · 捣蛋鬼", 540, 760, 42, at=0, accent=ACC, sfx="wood_high", note="原型预告卡"),
        ], text_beat=0, note="预告第 02 讲：原型"),
        end_shot(REFS, "02 原型：为什么故事总有那几种人？"),
    ]
    return Episode(1, "collective", "集体无意识", "为什么不同地方的神话这么像？", ACC, shots, refs=REFS,
                   publish_title="为什么不同地方的神话这么像？｜荣格心理学01 集体无意识",
                   hashtags="#荣格 #心理学 #集体无意识 #分析心理学",
                   cover_title="为什么不同地方的|神话【这么像】？", cover_sub="荣格的集体无意识", cover_shot=5, cover_t=6.0,
                   notes=["“集体无意识”见荣格 1936 年演讲 The Concept of the Collective Unconscious（CW 9i）；片中“不是具体记忆而是共同倾向”"
                          "对应荣格“原型是先天的形式、不是遗传的观念”的说法。",
                          "“房子一层比一层古老”的梦见《回忆·梦·思考》（1962），荣格把它与集体无意识的设想联系起来；片中标“荣格自述”。",
                          "集体无意识在实证心理学中难以检验，片中第 12 镜明确列出这一质疑。"]).build()


def _nest(c, g):
    K.poly(c, [(-160, 40), (160, 40), (110, 110), (-110, 110)], K.mix(K.GOLD, K.DARK, 0.45))
    for i in range(7):
        K.seg(c, -150 + i * 50, 44, -110 + i * 40, 104, K.mix(K.GOLD, K.DARK, 0.65), 6)
    for dx in (-50, 0, 50):
        K.dot(c, dx, 30, 30, K.PAPER)
        K.ring(c, dx, 30, 30, K.INK3, 3)
    k = ease_out(clamp01(g.since(1) / 0.6))
    with K.at(c, 120 - 40 * k, -160 + 60 * k, -10):
        K.dot(c, 0, 0, 46, A.TEAL)
        K.poly(c, [(30, -10), (80, 0), (30, 10)], K.GOLD)
        K.poly(c, [(-20, -10), (-90, -60 + 40 * k), (-40, 10)], K.mix(A.TEAL, K.DARK, 0.3))
        K.dot(c, 12, -10, 6, K.INK)
