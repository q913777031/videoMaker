"""07 真诚一致：为什么装出来的好会让人累？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from jung import art as J

from . import art as A

ACC = "#6A5A8A"
GROUND = A.GROUND_Y
REFS = ["Rogers, C. R. (1959). A theory of therapy, personality, and interpersonal relationships. In S. Koch (Ed.), Psychology: A Study of a Science.",
        "Kolden, G. G., et al. (2018). Congruence/genuineness: A meta-analysis. Psychotherapy, 55(4), 424–433."]


def masked(c, g, el_t, d):
    """人物举着笑脸面具；d['off'] 为面具挪开的程度。"""
    off = d.get("off", 0)
    off = off(g, el_t) if callable(off) else off
    K.figure(c, 0, 0, 330, "stand", K.HERO, K.SKIN, 1, 1, d.get("mood", "worried"), "short")
    J.mask(c, 30 + 150 * off, -300 + 110 * off, 120, K.PAPER, "smile", 1, -10 * off)


def build() -> Episode:
    shots = [
        Shot(3, "明明很烦|嘴上却说“没事”", "情境演绎", [
            Fig(400, GROUND, 330, at=0, pose="stand", mood="smile", hair="short"),
            Bubble("没事！", 540, 620, 42, at=2, sfx="wood_high"),
            Icon("cloud", 400, 470, 160, color=K.DARK, at=4, sfx="tom", note="头顶乌云"),
        ], draw=A.ground, note="笑着说没事，头顶却有乌云"),
        Shot(3, "里面一个样|外面一个样", "情境演绎", [
            Custom(masked, x=540, y=GROUND, at=0, sfx="wood_low"),
        ], draw=A.ground, hits=[(4, "rim", 0.7, "面具后的愁容")], note="笑脸面具后面是愁容"),
        Shot(2, "罗杰斯看重的是——", "罗杰斯的视角", [
            Custom(A.circles, x=540, y=760, at=0, ov=(0.1, 0.9), b1=1, labels=None, r=180),
        ], text_beat=0, hits=[(1, "wood_low", 0.7, "两圆合拢")], note="两个圆合拢"),
        Shot(4, "里外|是同一个人", "罗杰斯原著 · 大意", [
            Big("真诚一致", 540, 600, 150, at=0, sfx="kick", sub="Congruence", note="概念落版（音乐 drop）"),
            Custom(A.circles, x=540, y=960, at=2, enter="fade", ov=(0.9, 0.9), labels=None, r=110),
        ], note="drop 处“真诚一致”砸下"),
        Shot(4, "心里的感受|和说出口的话对得上", "罗杰斯原著 · 大意", [
            Custom(A.circles, x=540, y=780, at=0, enter="pop", ov=(0.15, 0.85), b1=2, labels=("感受", "表达")),
        ], hits=[(2, "wood_low", 0.7, "感受与表达重合")], note="“感受”与“表达”两圆重合"),
        Shot(4, "不一致时|人会焦虑，会防御", "罗杰斯原著 · 大意", [
            Custom(A.circles, x=540, y=780, at=0, enter="pop", ov=(0.75, 0.1), b1=2),
        ], hits=[(2, "tom", 0.8, "两圆拉开")], note="“自我概念”与“真实经验”两圆拉开"),
        Shot(4, "要么扭曲经验|要么干脆否认", "罗杰斯原著 · 大意", [
            Card("扭曲", 340, 700, 50, at=0, rot=-3, fill=K.DARK, color=K.PAPER, sfx="wood_low"),
            Card("否认", 740, 820, 50, at=4, rot=2, fill=K.DARK, color=K.PAPER, sfx="wood_low"),
        ], note="两种防御：扭曲、否认"),
        Shot(2, "咨询师也要真诚|不躲在身份后面", "罗杰斯原著 · 大意", [
            Custom(A.two_chairs, x=540, y=GROUND, at=0, sfx="wood_low"),
        ], draw=A.ground, text_beat=0, note="两把椅子"),
        Shot(2, "真诚不是什么都说|而是不装", "常见误区", [
            Custom(masked, x=540, y=GROUND, at=0, enter="none", mood="calm", off=lambda g, t: ease_out(clamp01(g.since(1) / 0.8))),
        ], draw=A.ground, text_beat=0, hits=[(1, "wood_high", 0.7, "放下面具")], note="放下面具"),
        Shot(3, "研究：咨询师的真诚|与疗效正相关", "研究证据", [
            Custom(A.circles, x=540, y=720, at=0, ov=(0.85, 0.85), labels=None, r=140, sfx="wood_low"),
            Txt("Kolden 等，2018：元分析", 540, 940, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="真诚与疗效的元分析"),
        Shot(3, "里外一致的人|更省力，也更可信", "罗杰斯的视角", [
            Fig(540, GROUND, 330, at=0, pose="relax", mood="smile", hair="short"),
            Icon("check", 780, 640, 120, color=K.GREEN, at=4, sfx="clap"),
        ], draw=A.ground, note="放松的人"),
        Shot(2, "可以温和地|说出真实的感受", "罗杰斯的视角", [
            Bubble("我今天有点累", 540, 720, 46, at=0, sfx="wood_high"),
        ], text_beat=0, note="温和的真话"),
        Shot(2, "试试：把一句“没事”|换成一句真话", "小练习", [
            Card("没事", 340, 720, 48, at=0, rot=-3, sfx="wood_low"),
            Arrow((440, 760), (620, 760), at=1, color=ACC, width=12),
            Card("真话", 740, 760, 48, at=2, rot=2, accent=ACC, sfx="wood_high"),
        ], text_beat=0, note="没事 → 真话"),
        Shot(2, "下一讲：|怎样听，别人才愿意说", "下一讲", [
            Custom(lambda c, g, t, d: A.ear(c, 0, 0, 260, "#3F7F6F", 1, 1, g.t), x=600, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 08 讲：积极倾听"),
        end_shot(REFS, "08 积极倾听：怎样听，别人才愿意说？"),
    ]
    return Episode(7, "congruence", "真诚一致", "为什么装出来的好会让人累？", ACC, shots, refs=REFS,
                   publish_title="为什么装出来的好会让人累？｜罗杰斯心理学07 真诚一致",
                   hashtags="#罗杰斯 #心理学 #真诚 #情绪",
                   cover_title="为什么【装出来】的好|会让人累？", cover_sub="罗杰斯的真诚一致", cover_shot=1, cover_t=5.0,
                   notes=["一致与不一致见罗杰斯 1959 年的理论总论：自我概念与经验不一致时，个体体验到焦虑，并以扭曲或否认来防御。",
                          "真诚一致是 1957 年论文所列咨询师三项核心条件之一。",
                          "Kolden 等（2018）的元分析显示，咨询师的真诚 / 一致与疗效呈正相关。"]).build()
