"""01 需求层次：人到底想要什么？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#7A4F9A"
GROUND = A.GROUND_Y
REFS = ["Maslow, A. H. (1943). A Theory of Human Motivation. Psychological Review, 50(4), 370–396.",
        "Tay, L., & Diener, E. (2011). Needs and subjective well-being around the world. Journal of Personality and Social Psychology, 101(2), 354–365."]


def build() -> Episode:
    shots = [
        Shot(3, "饿着肚子的时候|你还想谈理想吗？", "情境演绎", [
            Fig(380, GROUND, 330, at=0, pose="sad", mood="worried", hair="short"),
            Custom(lambda c, g, t, d: A.bowl(c, 0, 0, 200, 0), x=740, y=1000, at=2, sfx="wood_low", note="空碗"),
            Bubble("饭……", 500, 620, 42, at=4, think=True, sfx="wood_high", note="满脑子是饭"),
            Icon("bulb", 760, 520, 110, color=K.INK3, at=6, sfx="rim", note="理想的灯泡暗着"),
        ], draw=A.ground, note="饿着肚子的人，满脑子是饭，“理想”的灯泡暗着"),
        Shot(3, "马斯洛认为|人的需要有先后之分", "马斯洛的视角", [
            Fig(360, GROUND, 360, at=0, pose="think", mood="calm", hair="short", color="#6A5A4A",
                moves=[(6, dict(pose="point", mood="open"))]),
            Icon("ladder", 760, 760, 260, color=ACC, at=6, sfx="tom", note="梯子"),
            Txt("亚伯拉罕·马斯洛（1908–1970），美国心理学家", 540, 1210, 30, at=2, font="sans_medium", color=K.INK2),
        ], draw=A.ground, note="马斯洛思考后指向一架梯子"),
        Shot(2, "1943 年|他提出了——", "马斯洛原著", [
            Custom(A.levels, x=540, y=760, at=0, grow=2.0),
        ], text_beat=0, hits=[(1, "wood_low", 0.6, "第二层"), (2, "wood_low", 0.6, "第三层"), (3, "wood_low", 0.6, "第四层"),
                              (4, "rim", 0.8, "第五层")], note="五层自下而上长出"),
        Shot(4, "从最基本的生存|到最高的追求", "马斯洛原著 · 大意", [
            Big("需求层次", 540, 540, 150, at=0, sfx="kick", sub="Hierarchy of Needs", note="概念落版（音乐 drop）"),
            Custom(A.levels, x=540, y=930, at=2, enter="fade", w=520, lh=66, labels=False),
        ], note="drop 处“需求层次”砸下"),
        Shot(4, "最底层：生理需要|吃、喝、睡觉", "马斯洛原著 · 大意", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", hi=0),
            Custom(lambda c, g, t, d: A.bowl(c, 0, 0, 120, 1), x=880, y=1080, at=2, sfx="wood_high", note="饭碗"),
        ], hits=[(0, "tom", 0.8, "高亮生理层")], note="高亮最底层：生理需要"),
        Shot(4, "往上是安全、|归属与爱、尊重", "马斯洛原著 · 大意", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", seq=[(0, 1), (2, 2), (4, 3)]),
        ], hits=[(0, "wood_low", 0.8, "安全"), (2, "wood_low", 0.8, "归属与爱"), (4, "wood_low", 0.8, "尊重")],
            note="高亮依次上移：安全、归属与爱、尊重"),
        Shot(4, "最顶上：自我实现|成为你能成为的人", "马斯洛原著 · 大意", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", hi=4),
            Custom(lambda c, g, t, d: K.burst(c, 0, 0, t, K.GOLD), x=540, y=480, at=2, enter="none", sfx="clap", note="顶层闪光"),
        ], note="高亮顶层：自我实现"),
        Shot(2, "底层没满足时|上层往往顾不上", "机制示意", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", fill=(0.15, 0, 0, 0, 0), fill_at=0),
        ], text_beat=0, hits=[(2, "rim", 0.7, "上层全空")], note="底层只满了一点，上面各层都是空的"),
        Shot(2, "极度饥饿的人|连做梦都梦见吃", "马斯洛原著 · 大意", [
            Fig(400, GROUND, 300, at=0, pose="sit_sad", mood="worried", hair="short"),
            Bubble("……", 560, 680, 40, at=0, think=True),
            Custom(lambda c, g, t, d: A.bowl(c, 0, 0, 140, 1), x=640, y=600, at=1, sfx="wood_high", note="梦里的饭碗"),
        ], draw=A.ground, text_beat=0, note="饿着的人梦里也是饭碗"),
        Shot(3, "但它不是死板的阶梯|几层可以同时进行", "马斯洛原著 · 大意", [
            Custom(A.gauge_set, x=500, y=780, at=0, enter="none", b0=0),
        ], hits=[(0, "wood_low", 0.6, "自我实现"), (1, "wood_low", 0.6, "尊重"), (2, "wood_low", 0.6, "归属与爱"),
                 (3, "wood_low", 0.6, "安全"), (4, "tom", 0.7, "生理")], note="五根满足度条同时都有一部分（示意）"),
        Shot(3, "跨文化研究发现|这些需要相当普遍", "研究证据", [
            Icon("friends", 540, 700, 220, color=ACC, at=0, sfx="wood_low"),
            Txt("Tay & Diener，2011：盖洛普世界调查，123 个国家", 540, 900, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="跨 123 个国家的调查：这些需要普遍存在"),
        Shot(2, "但顺序不是铁律|下层不满也能向上", "研究证据", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", fill=(0.4, 0.3, 0.8, 0.6, 0.3), fill_at=0),
        ], text_beat=0, hits=[(2, "rim", 0.7, "上层也有满足")], note="下层没满，上层也可以有满足"),
        Shot(2, "试试：现在|你最缺的是哪一层？", "小练习", [
            Custom(A.levels, x=540, y=760, at=0, seq=[(0, 0), (1, 1), (2, 2), (3, 3)], sfx="wood_high"),
        ], text_beat=0, note="高亮一层层往上走"),
        Shot(2, "下一讲：|“缺”和“长”的区别", "下一讲", [
            Custom(lambda c, g, t, d: A.sprout_grow(c, 0, 0, 300, clamp01(t / 1.4)), x=540, y=860, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 02 讲：匮乏与成长"),
        end_shot(REFS, "02 匮乏与成长：为什么有的需要满足了就停？"),
    ]
    return Episode(1, "hierarchy", "需求层次", "人到底想要什么？", ACC, shots, refs=REFS,
                   publish_title="人到底想要什么？｜马斯洛心理学01 需求层次",
                   hashtags="#马斯洛 #心理学 #需求层次 #人本主义",
                   cover_title="人到底|【想要】什么？", cover_sub="马斯洛的需求层次", cover_shot=6, cover_t=5.0,
                   notes=["需求层次见马斯洛 1943 年论文 A Theory of Human Motivation（Psychological Review）：生理、安全、爱（归属）、尊重、自我实现五类。",
                          "“极度饥饿的人连做梦都梦见食物”“层次并非固定不变、多种需要可同时部分满足”均为该文中说法的大意。",
                          "Tay 与 Diener（2011）用盖洛普世界调查（123 个国家）发现这些需要普遍存在，但满足的先后顺序并不严格。"]).build()
