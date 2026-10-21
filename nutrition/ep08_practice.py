"""08 像动物一样吃：把动物的智慧带回餐桌"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#4A7A5A"
GROUND = A.GROUND_Y
REFS = ["劳本海默、辛普森《动物为什么吃不胖？》（后浪，2023），「Putting Lessons into Practice」一章。",
        "Raubenheimer, D., & Simpson, S. J. (2020). Eat Like the Animals: What Nature Teaches Us About the Science of Healthy Eating. Houghton Mifflin Harcourt."]


def build() -> Episode:
    shots = [
        Shot(3, "学了七讲|到底该怎么吃？", "情境演绎", [
            Fig(420, GROUND, 330, at=0, pose="think", mood="calm", hair="short"),
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 100, (0.3, 0.45, 0.25)), x=780, y=900, at=3, sfx="wood_low"),
            Icon("question", 620, 560, 100, color=ACC, at=5, sfx="rim"),
        ], draw=A.ground, note="对着餐盘思考"),
        Shot(3, "书的最后一章|给了几条思路", "原书 · 大意", [
            Icon("book", 540, 760, 220, color=ACC, at=0, sfx="wood_low"),
        ], note="书"),
        Shot(2, "核心就是——", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, size=420, target=(0.45, 0.45), t_at=1, t_label=False),
        ], text_beat=0, hits=[(1, "rim", 0.8, "目标点亮起")], note="营养几何图上的目标点"),
        Shot(4, "让食欲|重新对准目标", "原书 · 大意", [
            Big("像动物一样吃", 540, 540, 120, at=0, sfx="kick", sub="Eat Like the Animals", note="概念落版（音乐 drop）"),
            Custom(A.geo, x=560, y=990, at=2, enter="fade", size=280, target=(0.45, 0.45), t_label=False),
        ], note="drop 处书名概念砸下"),
        Shot(4, "一：先吃够蛋白质|食欲会自己收住", "原书 · 大意", [
            Custom(A.gauge_row, x=540, y=760, at=0, enter="none", b0=-9, vals=(0.9, 0.6, 0.6, 0.6, 0.6), hi=0),
        ], note="蛋白质条先满"),
        Shot(4, "二：少吃超加工食品|多吃完整的食物", "原书 · 大意", [
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 180), x=320, y=760, at=0, sfx="wood_low"),
            Icon("cross", 320, 920, 90, color=K.RED, at=2, sfx="rim"),
            Icon("sprout", 760, 760, 200, color=K.GREEN, at=4, sfx="wood_high"),
        ], note="零食打叉，完整食物（蔬菜）留下"),
        Shot(4, "三：信任身体的信号|别只盯着卡路里", "原书 · 大意", [
            Card("卡路里", 340, 720, 50, at=0, rot=-3, sfx="wood_low"),
            Icon("cross", 340, 880, 90, color=K.RED, at=2, sfx="rim"),
            Icon("heart", 760, 760, 200, color=K.RED, at=4, sfx="wood_high"),
        ], note="卡路里打叉，心（身体信号）留下"),
        Shot(2, "四：人生不同阶段|目标也不一样", "原书 · 大意", [
            Fig(300, GROUND, 220, at=0, mood="happy", hair="short"),
            Fig(540, GROUND, 330, at=0, mood="calm", color=K.OTHER2, hair="bun"),
            Fig(780, GROUND, 300, at=0, mood="smile", color=K.OTHER),
        ], draw=A.ground, text_beat=0, note="孩子、成人、老人"),
        Shot(2, "也别走极端|高蛋白也有代价", "原书 · 大意", [
            Icon("scale", 540, 760, 240, color=ACC, at=0, sfx="wood_low"),
        ], text_beat=0, note="天平"),
        Shot(3, "这套理论|还在被更多研究检验", "常见质疑", [
            Icon("book", 400, 760, 180, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 720, 680, 110, color=K.RED, at=4, sfx="rim"),
        ], note="书与问号"),
        Shot(3, "它给的是|理解食欲的一个新角度", "当代理解", [
            Custom(lambda c, g, t, d: A.locust(c, 0, 0, 220, g.t), x=260, y=760, at=0, sfx="wood_low"),
            Custom(lambda c, g, t, d: A.cat(c, 0, 0, 220, t=g.t), x=540, y=860, at=2, sfx="wood_low"),
            Fig(820, GROUND - 160, 240, at=4, mood="smile", hair="short", sfx="wood_low"),
        ], note="蝗虫、猫、人"),
        Shot(2, "本系列为科普|不构成饮食医疗建议", "说明", [
            Icon("shield", 540, 760, 200, color=K.INK2, at=0, sfx="wood_low"),
        ], text_beat=0, note="盾牌"),
        Shot(2, "试试：下一顿饭|先吃蛋白质那一口", "小练习", [
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 120, (0.3, 0.45, 0.25)), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="餐盘"),
        Shot(2, "八讲走完|愿你吃得明白", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, size=420, target=(0.45, 0.45), t_label=False,
                   rails=[(1.0, ACC, "", -9)], dots=[(0, 0, 0.45, 3)]),
        ], text_beat=0, hits=[(3, "clap", 0.8, "到达目标"), (6, "cymbal", 0.5, "系列收尾")], note="点沿轨道走到目标"),
        end_shot(REFS, None),
    ]
    return Episode(8, "practice", "像动物一样吃", "把动物的智慧带回餐桌", ACC, shots, refs=REFS,
                   publish_title="把动物的智慧带回餐桌｜动物为什么吃不胖08 像动物一样吃",
                   hashtags="#动物为什么吃不胖 #营养学 #健康饮食 #读书",
                   cover_title="把动物的智慧|带回【餐桌】", cover_sub="动物为什么吃不胖 · 像动物一样吃", cover_shot=4, cover_t=6.0,
                   notes=["四条思路（先吃够蛋白质、少吃超加工食品多吃完整食物、信任身体信号而非只算卡路里、不同人生阶段目标不同）为原书最后一章「把经验付诸实践」的大意概括，"
                          "具体建议以原书为准。",
                          "蛋白质杠杆等观点仍在研究检验中；高蛋白饮食也有代价（见第 06 讲）。本系列为书籍内容科普，不构成饮食或医疗建议。"]).build()
