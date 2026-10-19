"""05 阿尼玛与阿尼姆斯：你心里的“另一半”"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#A0526B"
GROUND = A.GROUND_Y
REFS = ["Jung, C. G. (1951). Aion, ch. 3 The Syzygy: Anima and Animus. CW 9ii.",
        "Jung, C. G. (1928). The Relations between the Ego and the Unconscious. CW 7."]


def build() -> Episode:
    shots = [
        Shot(3, "为什么有人|总被同一类人吸引？", "情境演绎", [
            Fig(300, GROUND, 330, at=0, pose="stand", mood="smile", hair="short"),
            Icon("heart", 600, 640, 90, color=ACC, at=2, sfx="wood_high"),
            Icon("heart", 720, 560, 90, color=ACC, at=4, sfx="wood_high", gain=0.85),
            Icon("heart", 840, 640, 90, color=ACC, at=6, sfx="wood_high", gain=0.75),
        ], draw=A.ground, note="一颗颗心飘向同一种人"),
        Shot(3, "荣格说|心里住着“另一半”", "荣格的视角", [
            Custom(lambda c, g, t, d: A.sun_moon(c, 0, 0, 100, ease_out(clamp01(t / 2))), x=540, y=760, at=0, sfx="tom"),
        ], note="日与月慢慢靠近"),
        Shot(2, "男人心里有女性面|女人也有男性面", "荣格的视角", [
            Fig(380, GROUND, 320, at=0, pose="stand", mood="calm", hair="short"),
            Fig(700, GROUND, 320, at=0, pose="stand", mood="calm", color=K.OTHER3, hair="bun", face=-1),
        ], draw=A.ground, text_beat=0, note="一男一女并立"),
        Shot(4, "心灵里|异性的那一面", "荣格原著 · 大意", [
            Big("阿尼玛 · 阿尼姆斯", 540, 600, 110, at=0, sfx="kick", sub="Anima · Animus", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.sun_moon(c, 0, 0, 80, 1), x=540, y=920, at=2, enter="pop", sfx="wood_low"),
        ], note="drop 处概念砸下"),
        Shot(4, "阿尼玛：|男性心中的女性形象", "荣格原著 · 大意", [
            Fig(380, GROUND, 340, at=0, pose="think", mood="calm", hair="short"),
            Bubble("", 700, 600, 40, at=2, think=True, sfx="wood_high"),
            Fig(700, 700, 140, at=2, enter="pop", color=K.OTHER3, hair="bun", mood="smile", face=-1),
        ], draw=A.ground, note="男人心中浮现女性形象"),
        Shot(4, "阿尼姆斯：|女性心中的男性形象", "荣格原著 · 大意", [
            Fig(380, GROUND, 340, at=0, pose="think", mood="calm", color=K.OTHER3, hair="bun"),
            Bubble("", 700, 600, 40, at=2, think=True, sfx="wood_high"),
            Fig(700, 700, 140, at=2, enter="pop", hair="short", mood="smile", face=-1),
        ], draw=A.ground, note="女人心中浮现男性形象"),
        Shot(4, "我们常把它|投射到心仪的人身上", "机制示意", [
            Fig(300, GROUND, 330, at=0, pose="point", mood="happy", hair="short"),
            Fig(800, GROUND, 330, at=0, color=K.OTHER3, hair="bun", mood="calm", face=-1),
            Arrow((380, 700), (740, 700), at=4, color=ACC, width=14, bend=-0.2, sfx="rim", note="投射"),
            Custom(lambda c, g, t, d: K.spotlight(c, 0, 0, 220, K.GOLD, 0.5 * clamp01(t / 0.6)), x=800, y=900, at=6, enter="none"),
        ], draw=A.ground, hits=[(6, "wood_high", 0.7, "对方被理想化地照亮")], note="把心中的形象投到对方身上"),
        Shot(2, "所以一见钟情|有时爱的是投影", "荣格的视角", [
            Icon("photo", 540, 760, 220, color=ACC, at=0, sfx="wood_low"),
        ], text_beat=0, note="照片：投影"),
        Shot(2, "相处久了|投影落空，就失望", "情境演绎", [
            Fig(380, GROUND, 320, at=0, pose="sad", mood="sad", hair="short"),
            Fig(700, GROUND, 320, at=0, color=K.OTHER3, hair="bun", mood="flat", face=-1),
        ], draw=A.ground, text_beat=0, hits=[(4, "tom", 0.6, "失望")], note="两人相对失望"),
        Shot(3, "这套划分|带着那个时代的性别观", "常见质疑", [
            Icon("clock", 540, 760, 220, color=K.INK2, at=0, sfx="wood_low"),
            Txt("当代荣格学派已有许多修正", 540, 1000, 32, at=4, font="sans_medium", color=K.INK2),
        ], note="时钟：时代的局限"),
        Shot(3, "今天更常理解为|每个人心里都有另一种特质", "当代理解", [
            Custom(lambda c, g, t, d: A.sun_moon(c, 0, 0, 90, 1), x=540, y=760, at=0, sfx="wood_high"),
        ], note="日月并存"),
        Shot(2, "先认识它|别只在别人身上找它", "荣格的视角", [
            Icon("mirror", 540, 760, 230, color=ACC, at=0, sfx="wood_low"),
        ], text_beat=0, note="镜子"),
        Shot(2, "两面合一|人才更完整", "荣格的视角", [
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 220, g.t, ease_out(clamp01(t / 1.6)), ACC), x=540, y=760, at=0),
        ], text_beat=0, hits=[(4, "cymbal", 0.5, "曼陀罗展开")], note="曼陀罗展开"),
        Shot(2, "下一讲：|内向和外向，起点是荣格", "下一讲", [
            Fig(380, GROUND, 300, at=0, pose="relax", mood="calm", hair="short"),
            Fig(700, GROUND, 300, at=0, pose="cheer", mood="happy", color=K.OTHER2, face=-1),
        ], draw=A.ground, text_beat=0, hits=[(4, "wood_high", 0.7, "预告")], note="预告第 06 讲：内倾与外倾"),
        end_shot(REFS, "06 内倾与外倾：聚会后，你是累还是兴奋？"),
    ]
    return Episode(5, "anima", "阿尼玛与阿尼姆斯", "你心里的“另一半”", ACC, shots, refs=REFS,
                   publish_title="你心里的“另一半”｜荣格心理学05 阿尼玛与阿尼姆斯",
                   hashtags="#荣格 #心理学 #阿尼玛 #阿尼姆斯 #投射",
                   cover_title="你心里|住着【另一半】", cover_sub="荣格的阿尼玛与阿尼姆斯", cover_shot=6, cover_t=6.0,
                   notes=["阿尼玛 / 阿尼姆斯见《伊雍》第 3 章（1951）。荣格的原始表述以男女二分为前提，带有时代的性别观念；"
                          "当代荣格学派多有修正，片中第 10、11 镜说明。",
                          "“一见钟情有时爱的是投影”是对荣格投射说的通俗化表述，用“有时”。"]).build()
