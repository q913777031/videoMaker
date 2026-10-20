"""06 共情：共情就是“我懂你”吗？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#4F7F9A"
GROUND = A.GROUND_Y
REFS = ["Rogers, C. R. (1957). The necessary and sufficient conditions of therapeutic personality change. Journal of Consulting Psychology, 21(2), 95–103.",
        "Elliott, R., Bohart, A. C., Watson, J. C., & Murphy, D. (2018). Therapist empathy and client outcome: An updated meta-analysis. Psychotherapy, 55(4), 399–410."]


def build() -> Episode:
    shots = [
        Shot(3, "你说很难过|对方马上讲起了自己", "情境演绎", [
            Fig(300, GROUND, 320, at=0, pose="sad", mood="sad", hair="short"),
            Fig(780, GROUND, 320, at=0, pose="point", mood="open", color=K.OTHER2, hair="bun", face=-1),
            Bubble("我好难过……", 300, 620, 38, at=0, sfx="wood_low"),
            Bubble("我懂！我上次……", 760, 600, 36, at=4, sfx="wood_high"),
        ], draw=A.ground, note="你说难过，对方马上讲自己的事"),
        Shot(3, "这不是共情|是把话题拿走了", "常见误区", [
            Fig(300, GROUND, 320, at=0, enter="none", pose="sad", mood="flat", hair="short"),
            Fig(780, GROUND, 320, at=0, enter="none", pose="wave", mood="happy", color=K.OTHER2, hair="bun", face=-1),
            Arrow((420, 640), (680, 600), at=4, color=K.RED, width=12, sfx="rim", note="话题被拿走"),
        ], draw=A.ground, note="话题被拉到对方那边"),
        Shot(2, "罗杰斯说|真正的理解叫作——", "罗杰斯的视角", [
            Custom(lambda c, g, t, d: A.footprints(c, 0, 0, 280, clamp01(t / 1.6)), x=540, y=760, at=0, sfx="wood_low"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "脚印定格")], note="一串脚印"),
        Shot(4, "体会对方的世界|好像那就是你的", "罗杰斯原著 · 大意", [
            Big("共情", 540, 600, 180, at=0, sfx="kick", sub="Empathy", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.footprints(c, 0, 0, 200, 1), x=540, y=940, at=2, enter="fade"),
        ], note="drop 处“共情”砸下"),
        Shot(4, "但永远别丢掉|“好像”这两个字", "罗杰斯原著 · 大意", [
            Custom(A.circles, x=540, y=760, at=0, enter="pop", ov=(0.1, 0.55), b1=2, labels=("我", "你"), center=""),
            Label("好像", 540, 1060, 40, at=4, fill=ACC, sfx="wood_high"),
        ], hits=[(2, "wood_low", 0.7, "两圆靠近但不重合")], note="两个圆靠近但不合并：仍是两个人"),
        Shot(4, "共情不是同情|也不是“我也一样”", "常见误区", [
            Card("同情", 300, 700, 46, at=0, rot=-3, sfx="wood_low"),
            Card("我也一样", 760, 700, 46, at=2, rot=2, sfx="wood_low"),
            Icon("cross", 300, 860, 80, color=K.RED, at=4, sfx="rim"),
            Icon("cross", 760, 860, 80, color=K.RED, at=5, sfx="rim", gain=0.8),
        ], note="两张卡都打叉"),
        Shot(4, "而是准确说出|对方没说出口的感受", "罗杰斯原著 · 大意", [
            Fig(300, GROUND, 320, at=0, pose="sad", mood="sad", hair="short", moves=[(6, dict(pose="relax", mood="calm"))]),
            Fig(780, GROUND, 320, at=0, pose="stand", mood="calm", color=K.OTHER2, hair="bun", face=-1),
            Bubble("你是觉得委屈吧？", 760, 600, 36, at=2, sfx="wood_high"),
            Icon("heart", 300, 640, 80, color=K.RED, at=6, sfx="clap", note="被说中"),
        ], draw=A.ground, note="对方说出“委屈”，主角松了口气"),
        Shot(2, "说错了也没关系|对方会纠正你", "罗杰斯原著 · 大意", [
            Bubble("不是委屈，是累", 540, 720, 40, at=0, sfx="wood_low"),
        ], text_beat=0, note="被纠正"),
        Shot(2, "被理解的人|会更理解自己", "罗杰斯原著 · 大意", [
            Icon("mirror", 540, 760, 220, color=ACC, at=0, sfx="wood_high"),
        ], text_beat=0, note="镜子"),
        Shot(3, "元分析：咨询中的共情|与疗效中等程度相关", "研究证据", [
            Custom(lambda c, g, t, d: A.footprints(c, 0, 0, 200, 1), x=540, y=700, at=0, sfx="wood_low"),
            Txt("Elliott 等，2018", 540, 880, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="共情与疗效的元分析"),
        Shot(3, "共情可以练|不全是天生的", "研究证据", [
            Icon("ladder", 540, 740, 240, color=ACC, at=0, sfx="wood_low"),
            Txt("共情训练元分析：Teding van Berkhout & Malouff，2016", 540, 940, 28, at=2, font="sans_medium", color=K.INK2),
        ], note="共情训练有效"),
        Shot(2, "先别急着解决|先陪他待一会儿", "罗杰斯的视角", [
            Fig(400, GROUND, 300, at=0, pose="sit", mood="calm", hair="short"),
            Fig(660, GROUND, 300, at=0, pose="sit_sad", mood="sad", color=K.OTHER2, hair="bun", face=-1),
        ], draw=A.ground, text_beat=0, note="两人并排坐着"),
        Shot(2, "试试：用“你是觉得……”|开头回应", "小练习", [
            Bubble("你是觉得……", 540, 720, 48, at=0, sfx="wood_high"),
        ], text_beat=0, note="对话框"),
        Shot(2, "下一讲：|里外如一", "下一讲", [
            Custom(A.circles, x=540, y=760, at=0, ov=(0.9, 0.9), labels=None, r=160, center="", sfx="wood_high"),
        ], text_beat=0, note="预告第 07 讲：真诚一致"),
        end_shot(REFS, "07 真诚一致：为什么装出来的好会让人累？"),
    ]
    return Episode(6, "empathy", "共情", "共情就是“我懂你”吗？", ACC, shots, refs=REFS,
                   publish_title="共情就是“我懂你”吗？｜罗杰斯心理学06 共情",
                   hashtags="#罗杰斯 #心理学 #共情 #沟通",
                   cover_title="共情就是|“【我懂你】”吗？", cover_sub="罗杰斯的共情", cover_shot=6, cover_t=6.0,
                   notes=["罗杰斯 1957 年把共情定义为：体会来访者的私人世界，好像那就是你自己的，但永远不失去“好像”这一性质。",
                          "Elliott 等（2018）对 82 项研究的元分析显示，咨询师共情与疗效呈中等程度相关。",
                          "Teding van Berkhout 与 Malouff（2016，Journal of Counseling Psychology）的元分析显示共情训练总体有效。",
                          "片中对话为示例，非罗杰斯原文。"]).build()
