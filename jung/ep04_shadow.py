"""04 阴影：你最讨厌的人，像不像你？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#5B4A7A"
GROUND = A.GROUND_Y
REFS = ["Jung, C. G. (1938). Psychology and Religion. CW 11.", "Jung, C. G. (1951). Aion, ch. 2 The Shadow. CW 9ii."]


def shadowed(c, g, el_t, d):
    p = d.get("p", 1.0)
    p = p(g, el_t) if callable(p) else p
    A.shadow_self(c, 0, 0, d.get("s", 330), p, 1)
    K.figure(c, 0, 0, d.get("s", 330), d.get("pose", "stand"), K.HERO, K.SKIN, 1, 1, d.get("mood", "calm"), "short")


def build() -> Episode:
    shots = [
        Shot(3, "有个同事|你怎么看都不顺眼", "情境演绎", [
            Fig(300, GROUND, 330, at=0, pose="stand", mood="angry", hair="short"),
            Fig(780, GROUND, 330, at=2, color=K.OTHER3, pose="proud", mood="happy", face=-1, sfx="wood_low", note="同事登场"),
            Bubble("又在炫耀", 320, 640, 40, at=6, think=True, sfx="wood_high", note="心里嘀咕"),
        ], draw=A.ground, note="主角看同事不顺眼"),
        Shot(3, "也许他身上|有你不肯承认的东西", "荣格的视角", [
            Custom(shadowed, x=300, y=GROUND, at=0, enter="none", p=lambda g, t: ease_out(clamp01(g.since(4) / 1.0)), mood="worried"),
            Fig(780, GROUND, 330, at=0, enter="none", color=K.OTHER3, pose="proud", mood="happy", face=-1),
        ], draw=A.ground, hits=[(4, "tom", 0.8, "主角的影子长出来")], note="主角脚下长出影子"),
        Shot(2, "荣格把这部分|叫作——", "荣格的视角", [
            Custom(lambda c, g, t, d: A.shadow_self(c, 0, 0, 360, ease_out(clamp01(t / 1.2)), 1), x=540, y=GROUND, at=0),
        ], draw=A.ground, text_beat=0, hits=[(4, "rim", 0.8, "影子定格")], note="一道长长的影子"),
        Shot(4, "自己不愿承认的|那一面", "荣格原著 · 大意", [
            Big("阴影", 540, 620, 180, at=0, sfx="kick", sub="Shadow", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.shadow_self(c, 0, 0, 220, 1, 1), x=540, y=1100, at=2, enter="fade"),
        ], note="drop 处“阴影”砸下"),
        Shot(4, "愤怒、嫉妒、自私……|被推到了身后", "机制示意", [
            Custom(shadowed, x=540, y=GROUND, at=0, enter="rise"),
            Card("愤怒", 820, 560, 40, at=2, rot=4, fill=K.DARK, color=K.PAPER, sfx="wood_low"),
            Card("嫉妒", 900, 720, 40, at=4, rot=-3, fill=K.DARK, color=K.PAPER, sfx="wood_low", gain=0.85),
            Card("自私", 800, 880, 40, at=6, rot=2, fill=K.DARK, color=K.PAPER, sfx="wood_low", gain=0.75),
        ], draw=A.ground, note="三张深色卡片落进影子一侧"),
        Shot(4, "阴影里|也有被压下的优点", "荣格原著 · 大意", [
            Custom(shadowed, x=540, y=GROUND, at=0, enter="none"),
            Card("勇气", 820, 640, 42, at=2, rot=-3, accent=K.GOLD, sfx="wood_high"),
            Card("创造力", 860, 820, 42, at=4, rot=3, accent=K.GOLD, sfx="wood_high"),
        ], draw=A.ground, note="影子里也有金色的卡片：勇气、创造力"),
        Shot(4, "越不承认|越容易“投射”到别人身上", "机制示意", [
            Custom(shadowed, x=300, y=GROUND, at=0, enter="none"),
            Fig(800, GROUND, 330, at=0, color=K.OTHER3, pose="stand", mood="flat", face=-1),
            Arrow((380, 760), (720, 760), at=4, color=ACC, width=14, bend=-0.2, sfx="rim", note="投射箭头"),
            Label("投射", 550, 640, 36, at=4, fill=ACC),
        ], draw=A.ground, note="主角的影子被投射到同事身上"),
        Shot(2, "讨厌别人的地方|常常是自己的影子", "荣格的视角", [
            Icon("mirror", 540, 760, 240, color=ACC, at=0, sfx="wood_low"),
        ], text_beat=0, note="镜子"),
        Shot(2, "荣格：每个人|都带着阴影", "荣格原著 · 大意", [
            Card("Everyone carries a shadow.", 540, 760, 40, at=0, accent=ACC, sfx="wood_high"),
            Txt("《心理学与宗教》，1938", 540, 900, 30, at=2, font="sans_medium", color=K.INK2),
        ], text_beat=0, note="引文卡"),
        Shot(3, "整合阴影|不是放纵它", "常见误区", [
            Icon("chain", 540, 760, 220, color=K.INK2, at=0, sfx="wood_low"),
            Icon("cross", 760, 600, 90, color=K.RED, at=4, sfx="rim"),
        ], note="铁链与叉：整合不等于放纵"),
        Shot(3, "而是看见它|承认：这也是我", "荣格的视角", [
            Custom(shadowed, x=540, y=GROUND, at=0, enter="none", pose="hug", mood="smile"),
        ], draw=A.ground, hits=[(6, "clap", 0.7, "与影子和解")], note="主角抱住自己，与影子并存"),
        Shot(2, "试试：|下次被惹怒时，问一句", "小练习", [
            Fig(540, GROUND, 330, at=0, pose="think", mood="worried", hair="short"),
        ], draw=A.ground, text_beat=0, note="主角停下来思考"),
        Shot(2, "“他哪一点|让我想起了自己？”", "小练习", [
            Bubble("像我吗？", 540, 640, 46, at=0, think=True, sfx="wood_high"),
            Fig(540, GROUND, 330, at=0, enter="none", pose="think", mood="calm", hair="short"),
        ], draw=A.ground, text_beat=0, note="心里的问题"),
        Shot(2, "下一讲：|你心里的“另一半”", "下一讲", [
            Custom(lambda c, g, t, d: A.sun_moon(c, 0, 0, 80, ease_out(clamp01(t / 1.4))), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 05 讲：阿尼玛与阿尼姆斯"),
        end_shot(REFS, "05 阿尼玛与阿尼姆斯：你心里的“另一半”"),
    ]
    return Episode(4, "shadow", "阴影", "你最讨厌的人，像不像你？", ACC, shots, refs=REFS,
                   publish_title="你最讨厌的人，像不像你？｜荣格心理学04 阴影",
                   hashtags="#荣格 #心理学 #阴影 #投射",
                   cover_title="你最讨厌的人|【像不像你】？", cover_sub="荣格的阴影", cover_shot=6, cover_t=6.0,
                   notes=["“Everyone carries a shadow”出自《心理学与宗教》（1938），完整句为：Everyone carries a shadow, and the less it "
                          "is embodied in the individual's conscious life, the blacker and denser it is.",
                          "荣格指出阴影并非全是坏的，也包含未被发展的正面特质；片中第 6 镜据此。",
                          "“讨厌别人的地方常常是自己的影子”是对投射机制的通俗化表述，用“常常”而非“一定”。"]).build()
