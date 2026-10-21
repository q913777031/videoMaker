"""01 营养目标：一只蝗虫，凭什么知道该吃多少？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = A.LEAF
GROUND = A.GROUND_Y
REFS = ["劳本海默、辛普森《动物为什么吃不胖？》（范雪竹译，后浪 / 贵州人民出版社，2023），第 1 章。",
        "Simpson, S. J., & Raubenheimer, D. (2012). The Nature of Nutrition: A Unifying Framework from Animal Adaptation to Human Obesity. Princeton University Press."]


def dishes(c, g, el_t, d):
    """三盘配比不同的饲料：蛋白质（红）/ 碳水（金）比例各不相同。"""
    for i, (p, cb) in enumerate(((0.7, 0.3), (0.45, 0.55), (0.2, 0.8))):
        k = ease_out(clamp01(g.since(i) / 0.5))
        if k <= 0:
            continue
        x = -300 + i * 300
        A.plate(c, x, 0, 100, (p, cb, 0), k)
        K.text(c, f"{round(p * 100)} : {round(cb * 100)}", x, 160, 34, "sans_medium", K.INK2, k)


def intake(c, g, el_t, d):
    """蝗虫与两根营养条：蛋白质条总停在目标刻度上，碳水条随饲料变。"""
    A.locust(c, -260, -40, 300, g.t)
    pv = d.get("p", 0.8)
    cv = d.get("cb", 0.5)
    q = ease_out(clamp01(g.since(d.get("b0", 2)) / 1.6))
    A.nbar(c, 280, -60, 420, 46, pv * q, A.PROTEIN, "蛋白质", target=0.8)
    A.nbar(c, 280, 40, 420, 46, cv * q, A.CARB, "碳水", target=0.6)


def build() -> Episode:
    shots = [
        Shot(3, "你有没有过：|明明吃饱了，还想再吃点？", "情境演绎", [
            Fig(420, GROUND, 330, at=0, pose="relax", mood="calm", hair="short", moves=[(4, dict(pose="think", mood="worried"))]),
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 80, (0.15, 0.6, 0.25)), x=760, y=980, at=0, sfx="wood_low", note="吃空的餐盘"),
            Bubble("再来点？", 560, 620, 42, at=4, think=True, sfx="wood_high"),
        ], draw=A.ground, note="吃完一盘还想再吃"),
        Shot(3, "两位生物学家|从一只蝗虫开始找答案", "原书 · 大意", [
            Custom(lambda c, g, t, d: A.locust(c, 0, 0, 420, g.t), x=540, y=760, at=0, sfx="wood_low", note="一只蝗虫"),
            Txt("大卫·劳本海默 & 史蒂芬·辛普森", 540, 980, 32, at=2, font="sans_medium", color=K.INK2),
        ], note="蝗虫登场"),
        Shot(2, "他们给蝗虫|配了比例不同的饲料——", "原书 · 大意", [
            Custom(dishes, x=540, y=760, at=0, enter="none"),
        ], text_beat=0, hits=[(0, "wood_low", 0.7, "饲料 1"), (1, "wood_low", 0.7, "饲料 2"), (2, "wood_low", 0.7, "饲料 3")],
            note="三盘蛋白质 : 碳水比例不同的饲料"),
        Shot(4, "不管怎么配|吃进的蛋白质都差不多", "原书 · 大意", [
            Big("营养目标", 540, 560, 150, at=0, sfx="kick", sub="Intake Target", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.locust(c, 0, 0, 260, g.t), x=540, y=940, at=2, enter="fade"),
        ], note="drop 处“营养目标”砸下"),
        Shot(4, "蛋白质给得少|它就多吃，直到吃够", "机制示意", [
            Custom(intake, x=540, y=760, at=0, enter="pop", p=0.8, cb=0.95, b0=2),
        ], hits=[(2, "wood_low", 0.7, "营养条上涨")], note="低蛋白饲料：多吃，蛋白质到达目标、碳水超出"),
        Shot(4, "蛋白质给得多|它就少吃，宁可别的不够", "机制示意", [
            Custom(intake, x=540, y=760, at=0, enter="pop", p=0.8, cb=0.35, b0=2),
        ], hits=[(2, "wood_low", 0.7, "营养条上涨")], note="高蛋白饲料：吃到蛋白质目标就停，碳水不足"),
        Shot(4, "就像身体里|有一张看不见的配餐表", "原书 · 大意", [
            Card(["蛋白质 ……… ✓", "碳水 ……… ✓", "脂肪 ……… ✓"], 540, 740, 44, at=0, rot=-2, accent=ACC, sfx="wood_low"),
        ], note="一张配餐清单"),
        Shot(2, "这个目标|不靠计算卡路里", "原书 · 大意", [
            Card("卡路里", 540, 720, 54, at=0, rot=-3, sfx="wood_low"),
            Icon("cross", 540, 880, 100, color=K.RED, at=1, sfx="rim"),
        ], text_beat=0, note="“卡路里”打叉"),
        Shot(2, "靠的是|几种分开的食欲", "原书 · 大意", [
            Custom(A.gauge_row, x=540, y=760, at=0, enter="none", b0=0),
        ], text_beat=0, note="五根食欲条（预告第 03 讲）"),
        Shot(3, "后来他们发现|很多动物都有这样的目标", "原书 · 大意", [
            Custom(lambda c, g, t, d: A.cat(c, 0, 0, 260, t=g.t), x=260, y=900, at=0, sfx="wood_low"),
            Custom(lambda c, g, t, d: A.baboon(c, 0, 0, 300, t=g.t), x=560, y=900, at=2, sfx="wood_low"),
            Custom(lambda c, g, t, d: A.mouse(c, 0, 0, 200, t=g.t), x=850, y=900, at=4, sfx="wood_low"),
        ], note="猫、狒狒、小鼠依次出现"),
        Shot(3, "包括我们|人类自己", "原书 · 大意", [
            Fig(540, GROUND, 340, at=0, pose="wave", mood="smile", hair="short"),
        ], draw=A.ground, note="人"),
        Shot(2, "动物实验|不能直接套用到人", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=1, sfx="rim"),
        ], text_beat=0, note="天平与问号"),
        Shot(2, "试试：今天留意|你最馋的是什么", "小练习", [
            Bubble("想吃……", 540, 720, 48, at=0, think=True, sfx="wood_high"),
        ], text_beat=0, note="想吃什么"),
        Shot(2, "下一讲：|一张图看懂营养", "下一讲", [
            Custom(A.geo, x=560, y=760, at=0, size=360, target=(0.5, 0.45), t_at=1, t_label=False, sfx="wood_high"),
        ], text_beat=0, note="预告第 02 讲：营养几何"),
        end_shot(REFS, "02 营养几何：一张图，看懂你到底吃了什么"),
    ]
    return Episode(1, "target", "营养目标", "一只蝗虫，凭什么知道该吃多少？", ACC, shots, refs=REFS,
                   publish_title="一只蝗虫，凭什么知道该吃多少？｜动物为什么吃不胖01 营养目标",
                   hashtags="#动物为什么吃不胖 #营养学 #科普 #减肥",
                   cover_title="一只蝗虫|凭什么知道【该吃多少】？", cover_sub="动物为什么吃不胖 · 营养目标", cover_shot=4, cover_t=6.0,
                   notes=["营养目标（intake target）与蝗虫配比饲料实验见原书第 1 章「The Day of the Locusts」。片中饲料比例、营养条为示意，不是原始数据。",
                          "“不靠计算卡路里，靠几种分开的食欲”为原书观点的通俗表述；五种食欲见第 03 讲。",
                          "本系列为书籍内容科普，不构成饮食或医疗建议。"]).build()
