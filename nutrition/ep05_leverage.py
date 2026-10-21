"""05 蛋白质杠杆：为什么低蛋白饮食让人停不下嘴？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#B0473F"
GROUND = A.GROUND_Y
REFS = ["劳本海默、辛普森《动物为什么吃不胖？》（后浪，2023），「The Protein Leverage Hypothesis」一章。",
        "Gosby, A. K., et al. (2011). Testing protein leverage in lean humans: a randomised controlled experimental study. PLoS ONE, 6(10), e25929."]


def lever_el(c, g, el_t, d):
    """杠杆：从水平按到倾斜（d['b1'] 拍起）。"""
    tilt = d.get("tilt", -12) * ease_out(clamp01(g.since(d.get("b1", 1)) / 0.8))
    A.lever(c, 0, 0, d.get("w", 360), tilt)


def three_diets(c, g, el_t, d):
    """三种配比的饭菜卡：10% / 15% / 25% 蛋白质，d['hi'] 高亮一张。"""
    for i, (pct, parts) in enumerate(((10, (0.1, 0.6, 0.3)), (15, (0.15, 0.55, 0.3)), (25, (0.25, 0.45, 0.3)))):
        k = ease_out(clamp01(g.since(i * 2) / 0.5))
        if k <= 0:
            continue
        x = -320 + i * 320
        A.plate(c, x, -20, 100, parts, k)
        K.text(c, f"蛋白质 {pct}%", x, 140, 36, "serif_black", A.PROTEIN if d.get("hi") == i else K.INK, k)
        if d.get("hi") == i:
            K.rr_stroke(c, x, 30, 270, 340, 24, K.GOLD, 7, k)


def bars_intake(c, g, el_t, d):
    """总热量对比：15% 组为 100，10% 组为 112（Gosby 2011 的 +12%）。"""
    for i, (lab, v, col) in enumerate((("蛋白质 15%", 1.0, K.INK3), ("蛋白质 10%", 1.12, A.PROTEIN))):
        k = ease_out(clamp01(g.since(d.get("b0", 0) + i * 2) / 0.8))
        y = -60 + i * 150
        A.nbar(c, 60, y, 480 * v / 1.12, 70, k, col, lab)
        if k > 0.95:
            K.text(c, "100" if i == 0 else "约 112", 60 + 480 * v / 1.12 / 2 + 30, y, 36, "sans_medium", K.INK2, align="left")
    K.text(c, "总热量摄入（相对值）", 60, 230, 30, "sans_medium", K.INK3)


def build() -> Episode:
    shots = [
        Shot(3, "一包零食吃完了|为什么还是不满足？", "情境演绎", [
            Fig(400, GROUND, 330, at=0, pose="sad", mood="worried", hair="short"),
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 180), x=720, y=960, at=0, sfx="wood_low"),
            Bubble("还想吃……", 540, 640, 40, at=4, think=True, sfx="wood_high"),
        ], draw=A.ground, note="吃完零食还想吃"),
        Shot(3, "作者提出一个猜想|解释人为什么会吃多", "原书 · 大意", [
            Icon("bulb", 540, 760, 220, color=K.GOLD, at=0, sfx="wood_low"),
        ], note="灯泡"),
        Shot(2, "这个猜想叫——", "原书 · 大意", [
            Custom(lever_el, x=480, y=820, at=0, b1=1),
        ], text_beat=0, hits=[(1, "rim", 0.8, "杠杆压下")], note="杠杆压下"),
        Shot(4, "缺蛋白质时|人会多吃别的来凑", "原书 · 大意", [
            Big("蛋白质杠杆", 540, 540, 140, at=0, sfx="kick", sub="Protein Leverage", note="概念落版（音乐 drop）"),
            Custom(lever_el, x=480, y=1000, at=2, enter="fade", w=260, b1=-9),
        ], note="drop 处“蛋白质杠杆”砸下"),
        Shot(4, "蛋白质只占饮食的一小部分|却牵动着全部食量", "原书 · 大意", [
            Custom(lever_el, x=480, y=820, at=0, enter="none", b1=2, tilt=-16),
        ], hits=[(2, "tom", 0.8, "小块压动大块")], note="小块蛋白质压动一大块碳水和脂肪"),
        Shot(4, "2011 年|悉尼做了一项人体实验", "研究证据", [
            Icon("book", 540, 720, 200, color=ACC, at=0, sfx="wood_low"),
            Txt("Gosby 等，PLoS ONE，2011", 540, 900, 32, at=2, font="sans_medium", color=K.INK2),
        ], note="研究出处"),
        Shot(4, "22 位志愿者|轮流吃三种配比的饭菜", "研究证据", [
            Custom(three_diets, x=540, y=760, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.7, "10%"), (2, "wood_low", 0.7, "15%"), (4, "wood_low", 0.7, "25%")], note="三种饭菜：10% / 15% / 25% 蛋白质"),
        Shot(2, "蛋白质占比|从 15% 降到 10%", "研究证据", [
            Custom(three_diets, x=540, y=760, at=0, enter="none", hi=0),
        ], text_beat=0, hits=[(1, "rim", 0.7, "高亮 10%")], note="高亮 10% 那组"),
        Shot(2, "总热量|多吃了约 12%", "研究证据", [
            Custom(bars_intake, x=540, y=760, at=0, enter="none", b0=0),
        ], text_beat=0, hits=[(2, "tom", 0.8, "10% 组的条更长")], note="10% 组的总热量条更长"),
        Shot(3, "多出来的|主要是两餐之间的咸味零食", "研究证据", [
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 200), x=380, y=760, at=0, sfx="wood_low"),
            Icon("clock", 720, 760, 170, color=ACC, at=3, sfx="wood_high"),
        ], note="零食与时钟（两餐之间）"),
        Shot(3, "但升到 25%|食量并没有再减少", "研究证据", [
            Custom(three_diets, x=540, y=760, at=0, enter="none", hi=2),
        ], hits=[(2, "rim", 0.7, "高亮 25%")], note="高亮 25% 那组"),
        Shot(2, "研究者也承认|这种补偿并不完全", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=1, sfx="rim"),
        ], text_beat=0, note="天平与问号"),
        Shot(2, "试试：早餐里|留意有没有蛋白质", "小练习", [
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 120, (0.3, 0.45, 0.25)), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="早餐盘"),
        Shot(2, "下一讲：|那多吃蛋白质不就好了？", "下一讲", [
            Custom(lambda c, g, t, d: A.mouse(c, 0, 0, 260, t=g.t), x=540, y=820, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 06 讲"),
        end_shot(REFS, "06 蛋白质的代价：那多吃蛋白质不就好了？"),
    ]
    return Episode(5, "leverage", "蛋白质杠杆", "为什么低蛋白饮食让人停不下嘴？", ACC, shots, refs=REFS,
                   publish_title="为什么低蛋白饮食让人停不下嘴？｜动物为什么吃不胖05 蛋白质杠杆",
                   hashtags="#动物为什么吃不胖 #蛋白质 #减肥 #营养学",
                   cover_title="为什么低蛋白饮食|让人【停不下嘴】？", cover_sub="动物为什么吃不胖 · 蛋白质杠杆", cover_shot=8, cover_t=3.0,
                   notes=["蛋白质杠杆假说见原书同名一章：蛋白质摄入被优先调节，饮食中蛋白质比例偏低时，人会多吃碳水和脂肪来凑够蛋白质。",
                          "Gosby 等（2011，PLoS ONE）：22 名体重正常的志愿者在悉尼轮流吃 10% / 15% / 25% 蛋白质的固定菜单各 4 天；从 15% 降到 10% 时总能量摄入增加约 12%，"
                          "多出的主要来自两餐之间的咸味零食；从 15% 升到 25% 时摄入没有变化。作者指出这种补偿是不完全的。",
                          "片中热量条按 100 与约 112 的相对值绘制。本系列不构成饮食或医疗建议。"]).build()
