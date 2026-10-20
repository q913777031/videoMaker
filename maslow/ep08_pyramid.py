"""08 金字塔误读：马斯洛画过金字塔吗？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#A0522D"
GROUND = A.GROUND_Y
REFS = ["Maslow, A. H. (1943). A Theory of Human Motivation. Psychological Review, 50(4), 370–396.",
        "Bridgman, T., Cummings, S., & Ballard, J. (2019). Who built Maslow's pyramid? Academy of Management Learning & Education, 18(1), 81–98.",
        "Koltko-Rivera, M. E. (2006). Rediscovering the later version of Maslow's hierarchy of needs. Review of General Psychology, 10(4), 302–317."]

PYR = dict(shape="pyramid", w=760, lh=110)


def build() -> Episode:
    shots = [
        Shot(3, "这张金字塔|你一定见过", "情境演绎", [
            Custom(A.levels, x=540, y=760, at=0, grow=2.4, **PYR),
        ], hits=[(1, "wood_low", 0.6, "第二层"), (2, "wood_low", 0.6, "第三层"), (3, "wood_low", 0.6, "第四层"),
                 (4, "rim", 0.8, "塔尖")], note="经典金字塔自下而上搭起"),
        Shot(3, "可在马斯洛的论著里|找不到这张图", "研究证据", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", **PYR),
            Icon("question", 820, 460, 130, color=K.RED, at=4, sfx="rim", note="问号"),
        ], note="金字塔旁出现问号"),
        Shot(2, "它更可能来自|管理学的传播——", "研究证据", [
            Icon("brief", 540, 760, 220, color=K.DARK, at=0, sfx="wood_low"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "公文包定格")], note="公文包：管理学"),
        Shot(4, "1960 年前后|才出现在管理学文章里", "研究证据", [
            Big("金字塔误读", 540, 560, 140, at=0, sfx="kick", sub="The Pyramid Myth", note="概念落版（音乐 drop）"),
            Txt("Bridgman 等，2019：追溯到 McDermid（1960）", 540, 760, 30, at=2, font="sans_medium", color=K.INK2),
            Custom(A.levels, x=540, y=1000, at=2, enter="fade", shape="pyramid", w=420, lh=60, labels=False),
        ], note="drop 处“金字塔误读”砸下"),
        Shot(4, "误读一：|必须一层满了才能上一层", "常见误区", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", fill=(1, 0, 0, 0, 0), fill_at=0),
            Icon("cross", 860, 480, 110, color=K.RED, at=4, sfx="rim"),
        ], hits=[(0, "wood_low", 0.7, "底层灌满")], note="底层满了才往上灌的想象被打叉"),
        Shot(4, "他举例：普通人|各层都只部分满足", "马斯洛原著 · 大意", [
            Custom(A.gauge_set, x=480, y=780, at=0, enter="none", b0=0, pct=True),
        ], hits=[(0, "wood_low", 0.6, "自我实现"), (1, "wood_low", 0.6, "尊重"), (2, "wood_low", 0.6, "归属与爱"),
                 (3, "wood_low", 0.6, "安全"), (4, "tom", 0.7, "生理")], note="马斯洛举的示意数字：85%、70%、50%、40%、10%"),
        Shot(4, "比如生理 85%|自我实现只有 10%", "马斯洛原著 · 大意", [
            Custom(A.gauge_set, x=480, y=780, at=0, enter="none", b0=-99, pct=True),
            Txt("马斯洛注明：这些数字只是为了举例", 540, 1180, 30, at=4, font="sans_medium", color=K.INK2, sfx="wood_high"),
        ], note="同一组满足度条，并注明数字只是示意"),
        Shot(2, "误读二：|顺序对谁都一样", "常见误区", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", w=600, lh=90),
            Icon("cross", 860, 500, 100, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="固定顺序被打叉"),
        Shot(2, "他也说过|有人把尊重看得比爱更重", "马斯洛原著 · 大意", [
            Card("尊重", 400, 700, 48, at=0, rot=-3, accent="#5B6FA8", sfx="wood_low"),
            Card("爱", 680, 860, 48, at=1, rot=2, accent="#C25B6A", sfx="wood_low"),
            Arrow((680, 800), (460, 760), at=2, color=ACC, width=10, sfx="rim"),
        ], text_beat=0, note="尊重卡片排到了爱的前面"),
        Shot(3, "误读三：|自我实现就是终点", "常见误区", [
            Custom(A.levels, x=540, y=800, at=0, enter="none", hi=4, w=600, lh=90),
            Icon("question", 540, 440, 110, color=K.RED, at=4, sfx="rim"),
        ], note="顶层上方出现问号"),
        Shot(3, "晚年他在顶上|又补了“自我超越”", "马斯洛原著 · 大意", [
            Custom(A.levels, x=540, y=840, at=0, enter="none", w=600, lh=90),
            Card("自我超越", 540, 520, 44, at=2, accent="#4A7A6A", sfx="tom", note="顶上多出一层"),
        ], note="层次图顶上多出“自我超越”"),
        Shot(2, "层次是一张地图|不是爬梯比赛", "当代理解", [
            Icon("flag", 400, 760, 200, color=ACC, at=0, sfx="wood_low"),
            Icon("ladder", 720, 760, 200, color=K.INK3, at=1),
            Icon("cross", 720, 760, 100, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="地图上的旗子保留，爬梯打叉"),
        Shot(2, "试试：哪一层|你一直在“跳过”？", "小练习", [
            Custom(A.levels, x=540, y=760, at=0, seq=[(0, 0), (1, 1), (2, 2), (3, 3)], w=600, lh=90, sfx="wood_high"),
        ], text_beat=0, note="高亮逐层上移"),
        Shot(2, "下一讲：|人为什么害怕变好", "下一讲", [
            Custom(lambda c, g, t, d: A.whale(c, 0, 0, 420, 0.3, g.t), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 09 讲：约拿情结"),
        end_shot(REFS, "09 约拿情结：为什么我们害怕变得更好？"),
    ]
    return Episode(8, "pyramid", "金字塔误读", "马斯洛画过金字塔吗？", ACC, shots, refs=REFS,
                   publish_title="马斯洛画过金字塔吗？｜马斯洛心理学08 金字塔误读",
                   hashtags="#马斯洛 #心理学 #需求层次 #冷知识",
                   cover_title="马斯洛|【画过】金字塔吗？", cover_sub="需求层次的三个常见误读", cover_shot=1, cover_t=5.0,
                   notes=["马斯洛本人的论著中没有金字塔图；Bridgman、Cummings 与 Ballard（2019）考证，金字塔画法最早见于 Charles McDermid "
                          "1960 年在 Business Horizons 发表的管理学文章，此后经管理学教材流行。",
                          "“普通人生理需要满足 85%、安全 70%、爱 50%、自尊 40%、自我实现 10%”见马斯洛 1943 年论文，他注明这是为举例而随意设定的数字。",
                          "同文讨论了层次的“倒置”，例如有人把自尊看得比爱更重要。",
                          "晚年马斯洛（1969）提出高于自我实现的“自我超越”，见 Koltko-Rivera（2006）的梳理。"]).build()
