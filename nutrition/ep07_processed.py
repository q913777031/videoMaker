"""07 超加工食品：是零食把蛋白质冲淡了吗？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#C27A2A"
GROUND = A.GROUND_Y
REFS = ["劳本海默、辛普森《动物为什么吃不胖？》（后浪，2023），「Modern Environments」一章。",
        "Martínez Steele, E., et al. (2018). Public Health Nutrition.（NHANES）",
        "Hall, K. D., et al. (2019). Cell Metabolism, 30(1).（超加工饮食对照实验）"]


def shelf(c, g, el_t, d):
    """超市货架：一排排零食袋和易拉罐依次出现。"""
    for r in range(3):
        K.rr(c, 0, -220 + r * 220 + 90, 860, 14, 4, K.mix(K.GOLD, K.DARK, 0.5))
        for i in range(6):
            k = ease_out(clamp01(g.since(r * 2 + i * 0.25) / 0.3))
            if k <= 0:
                continue
            x = -360 + i * 144
            y = -220 + r * 220
            cols = ("#D9593A", "#E3A33B", "#5E8FA8", "#7A4F9A", "#5E9A6A")
            if (i + r) % 2:
                A.chips(c, x, y, 150 * k, color=cols[(i + r) % 5])
            else:
                A.soda(c, x, y + 10, 140 * k, color=cols[(i * 2 + r) % 5])


def quintile(c, g, el_t, d):
    """五档超加工食品占比：蛋白质能量占比从约 18.2% 降到约 13.3%。"""
    vals = (18.2, 17.0, 15.9, 14.6, 13.3)
    for i, v in enumerate(vals):
        k = ease_out(clamp01(g.since(d.get("b0", 0) + i * 0.5) / 0.5))
        if k <= 0:
            continue
        x = -340 + i * 170
        h = v / 18.2 * 380 * k
        K.rr(c, x, 200 - h / 2, 100, h, 14, A.PROTEIN)
        if i in (0, 4):
            K.text(c, f"{v}%", x, 200 - h - 36, 34, "sans_medium", K.INK, k)
    K.text(c, "超加工食品占比：低 → 高", 0, 270, 32, "sans_medium", K.INK2)
    K.text(c, "（中间三档为示意）", 0, 320, 26, "sans_medium", K.INK3)


def build() -> Episode:
    shots = [
        Shot(3, "超市里|为什么到处都是零食？", "情境演绎", [
            Custom(shelf, x=540, y=740, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "第一排"), (2, "wood_low", 0.6, "第二排"), (4, "wood_low", 0.6, "第三排")], note="货架一排排摆满零食"),
        Shot(3, "作者认为|我们的食物环境变了", "原书 · 大意", [
            Icon("house", 360, 760, 200, color=ACC, at=0, sfx="wood_low"),
            Arrow((480, 760), (640, 760), at=2, color=ACC, width=12, sfx="rim"),
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 200), x=760, y=760, at=4, sfx="wood_low"),
        ], note="家常饭 → 零食"),
        Shot(2, "很多食物|被加工成了——", "原书 · 大意", [
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 260), x=440, y=760, at=0, sfx="wood_low"),
            Custom(lambda c, g, t, d: A.soda(c, 0, 0, 220), x=680, y=780, at=1, sfx="wood_low"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "定格")], note="零食袋与易拉罐"),
        Shot(4, "便宜、好吃|蛋白质却被冲淡了", "原书 · 大意", [
            Big("超加工食品", 540, 540, 140, at=0, sfx="kick", sub="Ultra-processed Food", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 180), x=540, y=950, at=2, enter="fade"),
        ], note="drop 处“超加工食品”砸下"),
        Shot(4, "便宜的碳水和脂肪|加上调味，就很好吃", "原书 · 大意", [
            Label("碳水", 300, 700, 44, at=0, fill=A.CARB, sfx="wood_low"),
            Label("脂肪", 540, 700, 44, at=2, fill=A.FAT, sfx="wood_low"),
            Label("调味", 780, 700, 44, at=4, fill=K.RED, sfx="wood_low"),
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 200), x=540, y=920, at=6, sfx="clap"),
        ], note="碳水 + 脂肪 + 调味 = 零食"),
        Shot(4, "美国调查：超加工吃得越多|蛋白质占比越低", "研究证据", [
            Custom(quintile, x=540, y=720, at=0, enter="none", b0=0),
            Txt("Martínez Steele 等，2018，NHANES", 540, 1150, 30, at=4, font="sans_medium", color=K.INK2),
        ], hits=[(0, "wood_low", 0.6, "第一档"), (2, "rim", 0.7, "最后一档")], note="五档柱子逐渐变矮"),
        Shot(4, "从约 18% 降到约 13%|总热量却更高", "研究证据", [
            Custom(quintile, x=540, y=720, at=0, enter="none", b0=-9),
            Label("总热量 ↑", 820, 520, 40, at=4, fill=K.RED, sfx="tom"),
        ], note="柱子与“总热量上升”标签"),
        Shot(2, "按蛋白质杠杆|人就会多吃来凑", "原书 · 大意", [
            Custom(lambda c, g, t, d: A.lever(c, 0, 0, 300, -14), x=480, y=820, at=0, sfx="wood_low"),
        ], text_beat=0, note="杠杆"),
        Shot(2, "美国 NIH|做过一项对照实验", "研究证据", [
            Icon("book", 540, 720, 200, color=ACC, at=0, sfx="wood_low"),
            Txt("Hall 等，Cell Metabolism，2019", 540, 900, 30, at=1, font="sans_medium", color=K.INK2),
        ], text_beat=0, note="研究出处"),
        Shot(3, "吃超加工饮食的两周|每天多吃约 500 千卡", "研究证据", [
            Fig(400, GROUND, 330, at=0, mood="calm", hair="short", moves=[(4, dict(mood="worried"))]),
            Label("每天 +约 500 千卡", 740, 640, 40, at=4, fill=K.RED, sfx="tom"),
        ], draw=A.ground, note="志愿者与标签"),
        Shot(3, "不过那项实验里|两组吃的蛋白质差不多", "常见质疑", [
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 100, (0.15, 0.5, 0.35)), x=360, y=760, at=0, sfx="wood_low"),
            Label("≈", 540, 760, 60, at=2, fill=K.INK2),
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 100, (0.15, 0.55, 0.3)), x=720, y=760, at=2, sfx="wood_low"),
        ], note="两盘蛋白质占比差不多"),
        Shot(2, "所以吃胖的原因|还不止这一个", "常见质疑", [
            Icon("question", 540, 760, 200, color=K.RED, at=0, sfx="rim"),
        ], text_beat=0, note="问号"),
        Shot(2, "试试：看看配料表|和蛋白质含量", "小练习", [
            Card(["营养成分表", "蛋白质 …… ? g"], 540, 760, 44, at=0, rot=-2, accent=ACC, sfx="wood_high"),
        ], text_beat=0, note="营养成分表"),
        Shot(2, "下一讲：|把动物的智慧带回餐桌", "下一讲", [
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 130, (0.3, 0.45, 0.25)), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 08 讲"),
        end_shot(REFS, "08 像动物一样吃：把动物的智慧带回餐桌"),
    ]
    return Episode(7, "processed", "超加工食品", "是零食把蛋白质冲淡了吗？", ACC, shots, refs=REFS,
                   publish_title="是零食把蛋白质冲淡了吗？｜动物为什么吃不胖07 超加工食品",
                   hashtags="#动物为什么吃不胖 #超加工食品 #减肥 #营养学",
                   cover_title="是零食把蛋白质|【冲淡】了吗？", cover_sub="动物为什么吃不胖 · 超加工食品", cover_shot=5, cover_t=5.0,
                   notes=["原书「现代环境」一章认为：廉价的碳水和脂肪经调味加工后美味而蛋白质比例偏低，按蛋白质杠杆会导致多吃。",
                          "Martínez Steele 等（2018，Public Health Nutrition）分析美国 NHANES 2009–2010 数据（n = 9042）：超加工食品占比从最低到最高五分位，蛋白质能量占比从 18.2% 降到 13.3%，"
                          "总能量摄入上升；这是横断面相关研究，不能证明因果。片中中间三档柱子为示意。",
                          "Hall 等（2019，Cell Metabolism）：20 名成人在 NIH 住院各吃两周超加工 / 未加工饮食，超加工期每天平均多摄入约 508 千卡、体重增加约 0.9 kg；"
                          "两组蛋白质摄入没有实质差异，因此该实验并不能直接证明蛋白质杠杆机制。本系列不构成饮食或医疗建议。"]).build()
