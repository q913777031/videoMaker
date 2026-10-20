"""08 积极倾听：怎样听，别人才愿意说？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#3F7F6F"
GROUND = A.GROUND_Y
REFS = ["Rogers, C. R., & Farson, R. E. (1957). Active Listening. Industrial Relations Center, University of Chicago.",
        "Rogers, C. R. (1986). Reflection of feelings. Person-Centered Review, 1(4), 375–377."]


def ear_el(c, g, el_t, d):
    A.ear(c, 0, 0, d.get("s", 260), ACC, 1, d.get("waves", 1), g.t)


def build() -> Episode:
    shots = [
        Shot(3, "他在说话|你在想怎么回", "情境演绎", [
            Fig(300, GROUND, 320, at=0, pose="point", mood="open", color=K.OTHER2, hair="bun"),
            Fig(780, GROUND, 320, at=0, pose="think", mood="flat", hair="short", face=-1),
            Bubble("最近我……", 320, 620, 38, at=0, sfx="wood_low"),
            Bubble("我要说……", 760, 600, 38, at=4, think=True, sfx="wood_high"),
        ], draw=A.ground, note="一人说话，另一人在想自己要说什么"),
        Shot(3, "罗杰斯和法森|写过一篇著名的文章", "罗杰斯原著", [
            Icon("book", 540, 720, 220, color=ACC, at=0, sfx="wood_low"),
            Txt("Rogers & Farson，1957", 540, 900, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="《积极倾听》"),
        Shot(2, "题目就叫——", "罗杰斯原著", [
            Custom(ear_el, x=600, y=760, at=0, sfx="rim"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "耳朵定格")], note="耳朵与声波"),
        Shot(4, "听懂内容|也听懂感受", "罗杰斯原著 · 大意", [
            Big("积极倾听", 540, 600, 150, at=0, sfx="kick", sub="Active Listening", note="概念落版（音乐 drop）"),
            Custom(ear_el, x=580, y=940, at=2, enter="fade", s=150),
        ], note="drop 处“积极倾听”砸下"),
        Shot(4, "第一：|听完，不打断", "罗杰斯原著 · 大意", [
            Fig(300, GROUND, 320, at=0, pose="point", mood="open", color=K.OTHER2, hair="bun"),
            Fig(780, GROUND, 320, at=0, pose="stand", mood="calm", hair="short", face=-1),
            Bubble("……", 320, 620, 44, at=0, sfx="wood_low"),
            Custom(ear_el, x=760, y=560, at=2, s=120, sfx="wood_high"),
        ], draw=A.ground, note="对方说，自己只听"),
        Shot(4, "第二：|用自己的话说回去", "罗杰斯原著 · 大意", [
            Bubble("我天天加班", 320, 640, 40, at=0, sfx="wood_low"),
            Bubble("你最近累坏了？", 740, 860, 40, at=4, sfx="wood_high"),
        ], note="复述：加班 → 累坏了"),
        Shot(4, "第三：|回应话里的感受", "罗杰斯原著 · 大意", [
            Bubble("老板根本不管", 320, 640, 40, at=0, sfx="wood_low"),
            Bubble("听起来很委屈", 740, 860, 40, at=4, sfx="wood_high"),
            Icon("heart", 540, 1060, 90, color=K.RED, at=6, sfx="clap"),
        ], note="回应感受：委屈"),
        Shot(2, "少问“为什么”|多说“听起来……”", "当代理解", [
            Card("为什么？", 340, 720, 46, at=0, rot=-3, sfx="wood_low"),
            Card("听起来……", 740, 800, 46, at=1, rot=2, accent=ACC, sfx="wood_high"),
        ], text_beat=0, note="两种问法"),
        Shot(2, "不急着评价|也不急着给答案", "罗杰斯原著 · 大意", [
            Icon("scale", 340, 760, 160, color=K.INK3, at=0, sfx="wood_low"),
            Icon("cross", 340, 760, 90, color=K.RED, at=1, sfx="rim"),
            Icon("bulb", 740, 760, 160, color=K.INK3, at=2, sfx="wood_low"),
            Icon("cross", 740, 760, 90, color=K.RED, at=3, sfx="rim"),
        ], text_beat=0, note="评价与答案都先放下"),
        Shot(3, "晚年他说：这不是“反映”|而是在核对我的理解", "罗杰斯原著 · 大意", [
            Card("反映感受", 340, 700, 44, at=0, rot=-3, sfx="wood_low"),
            Arrow((440, 740), (620, 800), at=2, color=ACC, width=12, sfx="rim"),
            Card("核对理解", 740, 840, 44, at=4, rot=2, accent=ACC, sfx="wood_low"),
        ], note="“反映感受”→“核对理解”"),
        Shot(3, "倾听不是技巧表演|而是真的想懂", "罗杰斯的视角", [
            Custom(ear_el, x=440, y=760, at=0, s=200, sfx="wood_low"),
            Icon("heart", 760, 760, 160, color=K.RED, at=4, sfx="wood_high"),
        ], note="耳朵与心"),
        Shot(2, "被认真听见|本身就有力量", "罗杰斯的视角", [
            Fig(540, GROUND, 330, at=0, pose="relax", mood="smile", color=K.OTHER2, hair="bun"),
        ], draw=A.ground, text_beat=0, note="松了口气的人"),
        Shot(2, "试试：今天对一个人|只听不评", "小练习", [
            Custom(ear_el, x=600, y=760, at=0, s=220, sfx="wood_high"),
        ], text_beat=0, note="耳朵"),
        Shot(2, "下一讲：|好的生活是什么样", "下一讲", [
            Icon("sun", 540, 760, 220, color=K.GOLD, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 09 讲：充分发挥功能的人"),
        end_shot(REFS, "09 充分发挥功能的人：好的生活是什么样？"),
    ]
    return Episode(8, "listening", "积极倾听", "怎样听，别人才愿意说？", ACC, shots, refs=REFS,
                   publish_title="怎样听，别人才愿意说？｜罗杰斯心理学08 积极倾听",
                   hashtags="#罗杰斯 #心理学 #倾听 #沟通技巧",
                   cover_title="怎样听|别人才【愿意说】？", cover_sub="罗杰斯的积极倾听", cover_shot=6, cover_t=6.0,
                   notes=["《积极倾听》（Active Listening）由罗杰斯与 Richard Farson 于 1957 年写成，面向管理者，强调听出内容与感受、"
                          "避免评判与说教。",
                          "罗杰斯 1986 年在 Person-Centered Review 发表短文，表示不喜欢“反映感受”这一说法，更愿称之为“核对理解”。",
                          "“少问为什么”为当代沟通练习中的常见建议，非罗杰斯原文；片中对话均为示例。"]).build()
