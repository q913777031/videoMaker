"""06 蛋白质的代价：那多吃蛋白质不就好了？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#6A5A8C"
GROUND = A.GROUND_Y
REFS = ["劳本海默、辛普森《动物为什么吃不胖？》（后浪，2023），「Why Not Just Eat More Protein?」一章。",
        "Solon-Biet, S. M., et al. (2014). The ratio of macronutrients, not caloric intake, dictates cardiometabolic health, aging, and longevity in ad libitum-fed mice. Cell Metabolism, 19, 418–430."]


def mice_grid(c, g, el_t, d):
    """5×5 个小方格代表 25 种饮食；d['hi'] 拍后，低蛋白高碳水的角落亮起。"""
    for r in range(5):
        for col in range(5):
            k = ease_out(clamp01(g.since((r * 5 + col) * 0.12) / 0.3))
            if k <= 0:
                continue
            x, y = -300 + col * 150, -300 + r * 150
            p = (4 - r) / 4
            fill = K.mix(A.CARB, A.PROTEIN, p)
            K.rr(c, x, y, 120 * k, 120 * k, 18, K.mix(fill, K.BG, 0.45))
            if d.get("hi") is not None and g.since(d["hi"]) >= 0 and r == 4 and col <= 1:
                K.rr_stroke(c, x, y, 136, 136, 22, K.GOLD, 7)
                A.mouse(c, x + 10, y + 40, 90, t=g.t)
    K.text(c, "↑ 蛋白质越高", -300, -420, 30, "sans_medium", A.PROTEIN)
    K.text(c, "碳水越高 ↓", 300, 420, 30, "sans_medium", A.CARB)


def build() -> Episode:
    shots = [
        Shot(3, "既然缺蛋白会吃多|那就拼命吃蛋白？", "情境演绎", [
            Fig(400, GROUND, 330, at=0, pose="fist", mood="happy", hair="short"),
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 110, (0.85, 0.05, 0.1)), x=760, y=900, at=3, sfx="wood_low", note="全是蛋白质的盘子"),
        ], draw=A.ground, note="举拳头的人与一盘几乎全是蛋白质的饭"),
        Shot(3, "书里给的答案|没那么简单", "原书 · 大意", [
            Icon("book", 540, 760, 220, color=ACC, at=0, sfx="wood_low"),
        ], note="书"),
        Shot(2, "因为蛋白质|也有代价——", "原书 · 大意", [
            Icon("scale", 540, 760, 260, color=ACC, at=0, sfx="rim"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "天平定格")], note="天平"),
        Shot(4, "长得快|不一定活得久", "原书 · 大意", [
            Big("蛋白质的代价", 540, 540, 120, at=0, sfx="kick", sub="The Protein Trade-off", note="概念落版（音乐 drop）"),
            Icon("scale", 540, 940, 160, color=ACC, at=2, enter="fade"),
        ], note="drop 处“蛋白质的代价”砸下"),
        Shot(4, "悉尼的团队给小鼠|配了 25 种不同的饮食", "研究证据", [
            Custom(mice_grid, x=540, y=720, at=0, enter="none"),
            Txt("Solon-Biet 等，Cell Metabolism，2014", 540, 1210, 30, at=4, font="sans_medium", color=K.INK2),
        ], hits=[(0, "wood_low", 0.6, "格子铺开")], note="25 个饮食格子"),
        Shot(4, "低蛋白、高碳水的那几组|活得最长", "研究证据", [
            Custom(mice_grid, x=540, y=720, at=0, enter="none", hi=2),
        ], hits=[(2, "clap", 0.8, "长寿角亮起")], note="低蛋白高碳水角落亮起"),
        Shot(4, "高蛋白有利于|长身体和繁殖", "原书 · 大意", [
            Icon("sprout", 380, 760, 200, color=K.GREEN, at=0, sfx="wood_low"),
            Icon("heart", 720, 760, 170, color=K.RED, at=4, sfx="wood_high"),
        ], note="芽与心：生长与繁殖"),
        Shot(2, "却不一定|有利于长寿", "原书 · 大意", [
            Icon("clock", 540, 760, 220, color=ACC, at=0, sfx="wood_low"),
        ], text_beat=0, note="时钟"),
        Shot(2, "不是越多越好|而是刚刚好", "原书 · 大意", [
            Custom(A.geo, x=560, y=760, at=0, size=420, target=(0.45, 0.4), t_label=False, sfx="wood_high"),
        ], text_beat=0, note="营养几何图上的目标点"),
        Shot(3, "人一生中|需要的蛋白比例也在变", "原书 · 大意", [
            Fig(240, GROUND, 200, at=0, mood="happy", hair="short", sfx="wood_low"),
            Fig(540, GROUND, 340, at=2, mood="calm", color=K.OTHER2, hair="bun", sfx="wood_low"),
            Fig(840, GROUND, 300, at=4, mood="smile", color=K.OTHER, pose="sad", sfx="wood_low"),
        ], draw=A.ground, note="孩子、成人、老人"),
        Shot(3, "比如老年人|往往需要更多蛋白质", "原书 · 大意", [
            Fig(540, GROUND, 320, at=0, mood="smile", color=K.OTHER, pose="stand"),
            Label("更多蛋白质", 780, 640, 38, at=4, fill=A.PROTEIN, sfx="wood_high"),
        ], draw=A.ground, note="老人与标签"),
        Shot(2, "小鼠的结果|不能直接搬到人身上", "常见质疑", [
            Custom(lambda c, g, t, d: A.mouse(c, 0, 0, 260, t=g.t), x=420, y=820, at=0, sfx="wood_low"),
            Icon("question", 760, 640, 110, color=K.RED, at=1, sfx="rim"),
        ], text_beat=0, note="小鼠与问号"),
        Shot(2, "试试：别迷信|“越多越好”", "小练习", [
            Card("越多越好", 540, 720, 54, at=0, rot=-3, sfx="wood_low"),
            Icon("cross", 540, 880, 100, color=K.RED, at=1, sfx="rim"),
        ], text_beat=0, note="“越多越好”打叉"),
        Shot(2, "下一讲：|零食把蛋白质冲淡了吗", "下一讲", [
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 220), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 07 讲"),
        end_shot(REFS, "07 超加工食品：是零食把蛋白质冲淡了吗？"),
    ]
    return Episode(6, "tradeoff", "蛋白质的代价", "那多吃蛋白质不就好了？", ACC, shots, refs=REFS,
                   publish_title="那多吃蛋白质不就好了？｜动物为什么吃不胖06 蛋白质的代价",
                   hashtags="#动物为什么吃不胖 #蛋白质 #长寿 #营养学",
                   cover_title="那多吃蛋白质|【不就好了】？", cover_sub="动物为什么吃不胖 · 蛋白质的代价", cover_shot=5, cover_t=5.0,
                   notes=["Solon-Biet 等（2014，Cell Metabolism）用营养几何框架给小鼠 25 种自由采食的饮食：碳水替代蛋白质、低蛋白高碳水的饮食与更长寿命、更好的代谢健康相关；"
                          "通过高蛋白或稀释饮食实现的热量限制并没有延长寿命。片中 5×5 格子为示意。",
                          "“高蛋白利于生长与繁殖、低蛋白利于长寿”的取舍，以及“老年人往往需要更多蛋白质”，为原书「为什么不干脆多吃蛋白质」一章观点的大意。",
                          "动物实验结论不能直接套用到人。本系列不构成饮食或医疗建议。"]).build()
