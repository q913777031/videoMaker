"""02 原型：为什么故事总有那几种人？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = A.PLUM
GROUND = A.GROUND_Y
REFS = ["Jung, C. G. (1934/1954). Archetypes of the Collective Unconscious. CW 9i.",
        "Campbell, J. (1949). The Hero with a Thousand Faces.（中译《千面英雄》）"]


def build() -> Episode:
    shots = [
        Shot(3, "为什么故事里|总有那几种人？", "情境演绎", [
            Icon("book", 260, 720, 170, color=K.HERO, at=0, sfx="wood_low", note="第一本书"),
            Icon("book", 540, 700, 170, color=K.RED, at=2, sfx="wood_low", gain=0.85, note="第二本书"),
            Icon("book", 820, 720, 170, color=K.GREEN, at=4, sfx="wood_low", gain=0.75, note="第三本书"),
            Icon("question", 540, 450, 110, color=ACC, at=8, sfx="rim", note="问号"),
        ], note="三本不同的故事书依次弹出"),
        Shot(3, "慈爱的母亲、闯关的英雄|指路的老智者", "情境演绎", [
            Icon("heart", 230, 760, 150, color=K.RED, at=0, sfx="wood_high", note="母亲"),
            Icon("trophy", 540, 740, 160, color=K.GOLD, at=2, sfx="wood_high", note="英雄"),
            Icon("bulb", 850, 760, 150, color=K.GOLD, at=4, sfx="wood_high", note="智者"),
            Label("母亲", 230, 930, 34, at=0, fill=K.RED), Label("英雄", 540, 930, 34, at=2, fill=K.GOLD),
            Label("智者", 850, 930, 34, at=4, fill=ACC),
        ], note="三种反复出现的角色：母亲、英雄、智者"),
        Shot(2, "荣格给它们|起了个名字——", "荣格的视角", [
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 240, g.t, ease_out(clamp01(t / 1.6)), ACC), x=540, y=760, at=0),
        ], text_beat=0, hits=[(4, "rim", 0.8, "曼陀罗展开")], note="曼陀罗展开蓄势"),
        Shot(4, "人类共有的|心理“模具”", "荣格原著 · 大意", [
            Big("原型", 540, 620, 170, at=0, sfx="kick", sub="Archetype", note="概念落版（音乐 drop）"),
            Label("先天的形式，不是遗传的观念", 540, 940, 34, at=8, fill=ACC, sfx="wood_high", note="标签"),
        ], note="drop 处“原型”砸下"),
        Shot(4, "原型本身看不见|只能透过形象显现", "荣格原著 · 大意", [
            Custom(A.cookie_mold, x=540, y=820, at=0, enter="pop", sfx="wood_low", b0=6, note="模具出现"),
        ], hits=[(6, "wood_high", 0.8, "压出第一块"), (7, "wood_high", 0.7, "第二块"), (8, "wood_high", 0.7, "第三块"),
                 (9, "wood_high", 0.6, "第四块"), (10, "wood_high", 0.6, "第五块")],
            note="同一个星形模具压出五块不同花色的饼干（示意：原型 vs 原型意象）"),
        Shot(4, "就像同一个模具|压出不同花色的饼干", "机制示意", [
            Custom(A.cookie_mold, x=540, y=820, at=0, enter="none", b0=-8),
            Label("示意", 900, 560, 30, at=2, fill=K.INK3),
        ], note="五块饼干定格；右上标注“示意”"),
        Shot(4, "英雄：离家、经历考验|带着收获回来", "坎贝尔的延伸", [
            Custom(A.hero_loop, x=540, y=780, at=0, enter="pop", acc=ACC, sfx="tom", note="英雄之旅圆环"),
            Txt("“英雄之旅”由坎贝尔（1949）归纳", 540, 1230, 30, at=4, font="sans_medium", color=K.INK2),
        ], hits=[(8, "clap", 0.7, "回到家")], note="小人沿圆环走一圈：家—考验—收获"),
        Shot(2, "母亲：滋养|也可能过度保护", "荣格原著 · 大意", [
            Icon("heart", 400, 760, 200, color=K.RED, at=0, sfx="wood_low", note="滋养"),
            Icon("shield", 700, 760, 200, color=K.INK2, at=4, sfx="wood_low", note="过度保护"),
        ], text_beat=0, note="母亲原型的两面"),
        Shot(2, "智慧老人：|在迷路时出现", "荣格原著 · 大意", [
            Fig(320, GROUND, 320, at=0, pose="shrug", mood="worried", hair="short"),
            Fig(760, GROUND, 340, at=2, color=K.mix(ACC, K.PAPER, 0.3), pose="point", mood="smile", face=-1, prop=A.cane,
                sfx="rim", note="老智者出现指路"),
        ], draw=A.ground, text_beat=0, note="迷路的人遇到指路的老者"),
        Shot(3, "捣蛋鬼：|打破规矩，带来变化", "荣格原著 · 大意", [
            Card("规矩", 360, 700, 48, at=0, rot=-2, sfx="wood_low", note="规矩卡"),
            Fig(760, GROUND, 300, at=2, color=K.GOLD, pose="cheer", mood="happy", face=-1,
                moves=[(6, dict(pose="push", sfx="kick", note="捣蛋鬼推翻规矩卡"))]),
        ], draw=A.ground, note="捣蛋鬼推翻“规矩”卡"),
        Shot(3, "电影、广告、神话里|到处都有原型", "情境演绎", [
            Icon("photo", 260, 760, 150, color=K.HERO, at=0, sfx="wood_high"),
            Icon("megaphone", 540, 740, 150, color=K.RED, at=2, sfx="wood_high"),
            Icon("book", 820, 760, 150, color=K.GREEN, at=4, sfx="wood_high"),
        ], note="电影、广告、神话三类图标"),
        Shot(2, "原型是否先天遗传|学界仍有争议", "常见质疑", [
            Icon("scale", 540, 760, 230, color=K.INK2, at=0, sfx="wood_low"),
        ], text_beat=0, note="天平：原型是否先天，学界有争议"),
        Shot(2, "但认出它们|能看懂故事，也看懂自己", "荣格的视角", [
            Icon("mirror", 540, 760, 220, color=ACC, at=0, sfx="tom"),
        ], text_beat=0, note="镜子：从故事里看见自己"),
        Shot(2, "下一讲：|你每天戴着的那张“面具”", "下一讲", [
            Custom(lambda c, g, t, d: A.mask(c, 0, 0, 220, K.PAPER, "smile", clamp01(t / 0.4)), x=540, y=760, at=0,
                   sfx="wood_high", note="面具预告"),
        ], text_beat=0, note="预告第 03 讲：人格面具"),
        end_shot(REFS, "03 人格面具：你每天戴着哪张脸？"),
    ]
    return Episode(2, "archetype", "原型", "为什么故事总有那几种人？", ACC, shots, refs=REFS,
                   publish_title="为什么故事总有那几种人？｜荣格心理学02 原型",
                   hashtags="#荣格 #心理学 #原型 #英雄之旅",
                   cover_title="为什么故事|总有【那几种人】？", cover_sub="荣格的原型", cover_shot=1, cover_t=5.5,
                   notes=["“原型是先天的形式而非遗传的观念”为荣格 CW 9i 中说法的大意。",
                          "“英雄之旅”是约瑟夫·坎贝尔在《千面英雄》（1949）中的归纳，受荣格影响，片中标“坎贝尔的延伸”。",
                          "“模具与饼干”是本片为说明原型（形式）与原型意象（具体形象）的区别所作的比喻，标“示意”。",
                          "原型是否先天遗传在学界有争议，第 12 镜列出。"]).build()
