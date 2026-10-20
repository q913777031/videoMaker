"""02 匮乏与成长：为什么有的需要满足了就停？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#C8873A"
GROUND = A.GROUND_Y
REFS = ["Maslow, A. H. (1962). Toward a Psychology of Being, ch. 3. Van Nostrand.",
        "Keys, A., et al. (1950). The Biology of Human Starvation. University of Minnesota Press."]


def two_kinds(c, g, el_t, d):
    """层次图旁加括号：下四层为匮乏需要，顶层为成长需要。"""
    A.hierarchy(c, -80, 0, 600, 100, 1, d.get("hi"))
    k1 = ease_out(clamp01(g.since(d.get("b1", 0)) / 0.5))
    k2 = ease_out(clamp01(g.since(d.get("b2", 4)) / 0.5))
    if k1 > 0:
        K.seg(c, 260, -100, 260, 240, ACC, 6, k1)
        K.text(c, "匮乏需要", 360, 70, 36, "serif_black", ACC, k1)
    if k2 > 0:
        K.text(c, "成长需要", 360, -200, 36, "serif_black", "#8A5BA8", k2)


def build() -> Episode:
    shots = [
        Shot(3, "吃饱了就不想再吃|可有些事越做越想做", "情境演绎", [
            Fig(300, GROUND, 320, at=0, pose="relax", mood="smile", hair="short"),
            Custom(lambda c, g, t, d: A.bowl(c, 0, 0, 130, 0.2), x=470, y=1060, at=0, sfx="wood_low", note="吃空的碗"),
            Fig(780, GROUND, 320, at=4, pose="reach", mood="happy", color=K.OTHER2, hair="bun", face=-1, sfx="wood_low"),
            Icon("book", 760, 620, 130, color=ACC, at=6, sfx="wood_high", note="越读越想读"),
        ], draw=A.ground, note="左：吃饱就停；右：越读越想读"),
        Shot(3, "马斯洛把需要|分成了两大类", "马斯洛的视角", [
            Icon("book", 540, 720, 200, color=ACC, at=0, sfx="wood_low"),
            Txt("《存在心理学探索》，1962", 540, 900, 32, at=4, font="sans_medium", color=K.INK2),
        ], note="《存在心理学探索》（Toward a Psychology of Being）"),
        Shot(2, "缺什么补什么的|叫作——", "马斯洛的视角", [
            Custom(lambda c, g, t, d: A.bowl(c, 0, 0, 260, ease_out(clamp01(g.since(2) / 0.8))), x=540, y=780, at=0, sfx="wood_low"),
        ], text_beat=0, hits=[(2, "rim", 0.8, "碗被盛满")], note="空碗被盛满"),
        Shot(4, "像身体缺维生素|补够了就不再惦记", "马斯洛原著 · 大意", [
            Big("匮乏需要", 540, 600, 150, at=0, sfx="kick", sub="Deficiency Needs", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.bowl(c, 0, 0, 160, 1), x=540, y=950, at=2, enter="fade"),
        ], note="drop 处“匮乏需要”砸下"),
        Shot(4, "生理、安全、归属、尊重|都属于这一类", "马斯洛原著 · 大意", [
            Custom(two_kinds, x=540, y=760, at=0, enter="pop", b1=2, b2=99),
        ], hits=[(2, "wood_high", 0.8, "括号：匮乏需要")], note="层次图下四层括为“匮乏需要”"),
        Shot(4, "研究：长期半饥饿的志愿者|满脑子都是食物", "研究证据", [
            Fig(400, GROUND, 320, at=0, pose="sit_sad", mood="worried", hair="short"),
            Bubble("食谱……", 560, 640, 40, at=2, think=True, sfx="wood_high"),
            Txt("明尼苏达饥饿实验，1944–1945", 540, 1220, 30, at=4, font="sans_medium", color=K.INK2),
        ], draw=A.ground, note="半饥饿的志愿者整天想着食物、收集食谱"),
        Shot(4, "另一类|越满足，越想要", "马斯洛原著 · 大意", [
            Custom(lambda c, g, t, d: A.sprout_grow(c, 0, 0, 420, clamp01(t / 3.5)), x=540, y=960, at=0, sfx="wood_low",
                   note="芽越长越高"),
            Label("成长需要", 540, 560, 40, at=4, fill="#8A5BA8", sfx="wood_high"),
        ], note="芽越长越高：成长需要"),
        Shot(2, "好奇、创造、求美|都是成长需要", "马斯洛原著 · 大意", [
            Icon("bulb", 300, 760, 150, color=K.GOLD, at=0, sfx="wood_high"),
            Icon("book", 540, 760, 150, color=ACC, at=1, sfx="wood_high", gain=0.85),
            Icon("sun", 780, 760, 150, color=K.GOLD, at=2, sfx="wood_high", gain=0.75),
        ], text_beat=0, note="灯泡、书、太阳"),
        Shot(2, "匮乏推着人|想“摆脱”", "机制示意", [
            Icon("cross", 360, 760, 120, color=K.RED, at=0, sfx="rim"),
            Arrow((460, 760), (760, 760), at=1, color=K.INK2, width=12, sfx="wood_low"),
        ], text_beat=0, note="箭头背离“缺”"),
        Shot(3, "成长拉着人|想“靠近”", "机制示意", [
            Icon("sprout", 760, 760, 160, color=K.GREEN, at=0, sfx="wood_low"),
            Arrow((300, 760), (640, 760), at=2, color=K.GREEN, width=12, sfx="wood_high"),
        ], note="箭头朝向成长"),
        Shot(3, "同一件事|可以出于两种动机", "机制示意", [
            Fig(540, GROUND, 330, at=0, pose="think", mood="calm", hair="short"),
            Bubble("怕挂科", 340, 620, 40, at=2, sfx="wood_low"),
            Bubble("真有意思", 760, 620, 40, at=4, sfx="wood_high"),
        ], draw=A.ground, note="学习：怕挂科 vs 真有意思"),
        Shot(2, "只被“缺”推着走|容易越活越累", "马斯洛的视角", [
            Fig(540, GROUND, 330, at=0, pose="sad", mood="worried", hair="short"),
        ], draw=A.ground, text_beat=0, note="被推着走的人显得疲惫"),
        Shot(2, "试试：今天的事|是补缺还是成长？", "小练习", [
            Custom(lambda c, g, t, d: A.bowl(c, 0, 0, 140, 1), x=360, y=780, at=0, sfx="wood_low"),
            Custom(lambda c, g, t, d: A.sprout_grow(c, 0, 0, 220, clamp01(t / 1.2)), x=720, y=860, at=2, sfx="wood_high"),
        ], text_beat=0, note="饭碗与芽"),
        Shot(2, "下一讲：|安全感从哪里来", "下一讲", [
            Icon("shield", 540, 760, 220, color="#5E8C61", at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 03 讲：安全需要"),
        end_shot(REFS, "03 安全需要：为什么人一不安就想抓紧？"),
    ]
    return Episode(2, "deficiency", "匮乏与成长", "为什么有的需要满足了就停？", ACC, shots, refs=REFS,
                   publish_title="为什么有的需要满足了就停？｜马斯洛心理学02 匮乏与成长",
                   hashtags="#马斯洛 #心理学 #动机 #成长",
                   cover_title="为什么有些需要|满足了就【停】？", cover_sub="马斯洛的匮乏需要与成长需要", cover_shot=4, cover_t=6.0,
                   notes=["匮乏需要（D-needs）与成长需要见马斯洛《存在心理学探索》（1962）；他把匮乏需要比作身体对维生素、矿物质的需要。",
                          "明尼苏达饥饿实验（Ancel Keys 主持，1944–1945）中，半饥饿的志愿者普遍对食物念念不忘、收集食谱；片中为通俗概括。",
                          "“只被缺推着走容易越活越累”为对马斯洛“匮乏动机者更焦虑、更依赖他人”观点的通俗表述。"]).build()
