"""02 营养几何：一张图，看懂你到底吃了什么"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#3B6E8C"
GROUND = A.GROUND_Y
REFS = ["劳本海默、辛普森《动物为什么吃不胖？》（后浪，2023），第 3 章「Picturing Nutrition」。",
        "Simpson, S. J., & Raubenheimer, D. (2012). The Nature of Nutrition. Princeton University Press."]

T = (0.42, 0.5)
ON = 0.5 / 0.42          # 正好穿过目标点的轨道
HI = 2.4                 # 偏蛋白质的食物
LO = 0.5                 # 偏碳水的食物


def build() -> Episode:
    shots = [
        Shot(3, "一顿饭|能不能画成一个点？", "情境演绎", [
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 120, (0.3, 0.5, 0.2)), x=380, y=760, at=0, sfx="wood_low"),
            Arrow((540, 760), (700, 760), at=3, color=ACC, width=12, sfx="rim"),
            Custom(lambda c, g, t, d: K.dot(c, 0, 0, 26 * ease_out(clamp01(t / 0.3)), ACC), x=800, y=760, at=5, enter="none", sfx="wood_high"),
        ], note="一盘饭变成一个点"),
        Shot(3, "横轴是碳水|纵轴是蛋白质", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, sfx="wood_low", note="坐标轴画出"),
        ], note="营养几何图的两根轴"),
        Shot(2, "这张图叫作——", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, enter="none", target=T, t_at=1, t_label=False),
        ], text_beat=0, hits=[(1, "rim", 0.8, "目标点亮起")], note="目标点亮起蓄势"),
        Shot(4, "把吃进去的营养|画成一张地图", "原书 · 大意", [
            Big("营养几何", 540, 540, 150, at=0, sfx="kick", sub="Nutritional Geometry", note="概念落版（音乐 drop）"),
            Custom(A.geo, x=560, y=990, at=2, enter="fade", size=300, target=T, t_label=False),
        ], note="drop 处“营养几何”砸下"),
        Shot(4, "每种食物|都是一条从原点出发的轨道", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, enter="none",
                   rails=[(HI, A.PROTEIN, "肉、蛋", 1), (ON, ACC, "正好", 3), (LO, A.CARB, "米饭、面包", 5)]),
        ], hits=[(1, "wood_low", 0.7, "偏蛋白轨道"), (3, "wood_low", 0.7, "均衡轨道"), (5, "wood_low", 0.7, "偏碳水轨道")],
            note="三条食物轨道"),
        Shot(4, "吃得越多|就沿着轨道走得越远", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, enter="none", rails=[(LO, A.CARB, "米饭、面包", -9)], dots=[(0, 1, 0.8, 5)]),
        ], hits=[(1, "wood_high", 0.6, "开始吃")], note="一个点沿偏碳水轨道越走越远"),
        Shot(4, "目标点|就是身体想要的那个组合", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, enter="none", target=T, t_at=1),
        ], hits=[(1, "tom", 0.8, "目标点出现")], note="金色目标点"),
        Shot(2, "对准目标的食物|吃到就停", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, enter="none", target=T, rails=[(ON, ACC, "正好", -9)], dots=[(0, 0, T[0], 3)]),
        ], text_beat=0, hits=[(3, "wood_high", 0.8, "到达目标")], note="均衡食物：点正好走到目标"),
        Shot(2, "食物偏了|就永远到不了目标", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, enter="none", target=T, rails=[(LO, A.CARB, "米饭、面包", -9)], dots=[(0, 0, 0.6, 3)]),
        ], text_beat=0, note="偏碳水轨道和目标点擦肩而过"),
        Shot(3, "这时只能取舍：|蛋白质不够，或碳水超标", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, enter="none", target=T, rails=[(LO, A.CARB, "米饭、面包", -9)],
                   dots=[(0, -9, 0.42, 1)], gaps=[(0.42, 0.21, 2), (1.0, 0.5, 5)]),
            Custom(lambda c, g, t, d: _end_dot(c, g), x=560, y=760, at=0, enter="none"),
        ], hits=[(2, "rim", 0.8, "蛋白质缺口"), (5, "rim", 0.8, "碳水超标")], note="两种结局：停在碳水够、蛋白不够处；或吃到蛋白够、碳水大大超标"),
        Shot(3, "两种偏的食物混着吃|也能凑到目标", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, enter="none", target=T, rails=[(HI, A.PROTEIN, "肉、蛋", -9), (LO, A.CARB, "米饭、面包", -9)], zig=(1, 4)),
        ], hits=[(1, "wood_low", 0.6, "交替吃"), (7, "clap", 0.8, "凑到目标")], note="在两条轨道之间来回，折线走到目标"),
        Shot(2, "图是简化的示意|真实饮食更复杂", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
        ], text_beat=0, note="天平"),
        Shot(2, "试试：把午饭|在这张图上点一下", "小练习", [
            Custom(A.geo, x=560, y=760, at=0, size=380, target=T, t_label=False, sfx="wood_high"),
        ], text_beat=0, note="空白营养几何图"),
        Shot(2, "下一讲：|五种食欲", "下一讲", [
            Custom(A.gauge_row, x=540, y=760, at=0, enter="none", b0=0),
        ], text_beat=0, note="预告第 03 讲"),
        end_shot(REFS, "03 五种食欲：为什么吃饱了还想来点咸的？"),
    ]
    return Episode(2, "geometry", "营养几何", "一张图，看懂你到底吃了什么", ACC, shots, refs=REFS,
                   publish_title="一张图，看懂你到底吃了什么｜动物为什么吃不胖02 营养几何",
                   hashtags="#动物为什么吃不胖 #营养学 #科普 #营养几何",
                   cover_title="一张图|看懂你【到底吃了什么】", cover_sub="动物为什么吃不胖 · 营养几何", cover_shot=9, cover_t=5.0,
                   notes=["营养几何（Geometric Framework）由两位作者提出，原书第 3 章用坐标图、目标点和食物“轨道”讲解；片中坐标与比例均为示意。",
                          "“食物偏离目标时只能在蛋白质不足与碳水过量之间取舍”“混吃互补食物可以到达目标”为原书观点的通俗表述。",
                          "本系列为书籍内容科普，不构成饮食或医疗建议。"]).build()


def _end_dot(c, g):
    """碳水超标的那一端：轨道上 x=1 处一个点（第 5 拍出现）。"""
    if g.since(5) < 0:
        return
    S = 620
    x, y = -S / 2 + 1.0 * S, S / 2 - LO * 1.0 * S
    K.dot(c, x, y, 18, A.CARB)
    K.ring(c, x, y, 18, K.INK, 4)
