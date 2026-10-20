"""06 自我实现：活成自己的人是什么样？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#8A5BA8"
GROUND = A.GROUND_Y
REFS = ["Maslow, A. H. (1943). A Theory of Human Motivation. Psychological Review, 50(4), 370–396.",
        "Maslow, A. H. (1950/1954). Self-Actualizing People: A Study of Psychological Health. In Motivation and Personality, ch. 11."]


def build() -> Episode:
    shots = [
        Shot(3, "有人什么都不缺|却还是觉得空", "情境演绎", [
            Icon("house", 260, 600, 130, color=K.HERO, at=0, sfx="wood_low"),
            Icon("friends", 540, 560, 130, color=K.OTHER3, at=1, sfx="wood_low", gain=0.85),
            Icon("trophy", 820, 600, 130, color=K.GOLD, at=2, sfx="wood_low", gain=0.75),
            Fig(540, GROUND, 330, at=0, pose="shrug", mood="flat", hair="short",
                moves=[(6, dict(pose="sad", mood="worried"))]),
        ], draw=A.ground, note="房子、朋友、奖杯都有，人却耸肩发呆"),
        Shot(3, "马斯洛说：音乐家必须作曲|画家必须画画", "马斯洛原著 · 大意", [
            Fig(300, GROUND, 320, at=0, pose="reach", mood="happy", hair="short"),
            Icon("photo", 700, 720, 220, color=ACC, at=4, sfx="wood_high", note="画布"),
        ], draw=A.ground, note="画家伸手作画"),
        Shot(2, "一个人能成为什么|就必须成为什么——", "马斯洛原著 · 大意", [
            Custom(A.levels, x=540, y=760, at=0, hi=4, w=600, lh=90),
        ], text_beat=0, hits=[(4, "rim", 0.8, "顶层定格")], note="顶层高亮"),
        Shot(4, "把潜能|活出来", "马斯洛原著 · 大意", [
            Big("自我实现", 540, 600, 150, at=0, sfx="kick", sub="Self-Actualization", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.sprout_grow(c, 0, 0, 240, clamp01(t / 2)), x=540, y=1020, at=2, enter="fade"),
        ], note="drop 处“自我实现”砸下"),
        Shot(4, "他研究了一批人|比如林肯、爱因斯坦", "马斯洛原著 · 大意", [
            Card("林肯", 280, 680, 44, at=0, rot=-3, sfx="wood_low"),
            Card("爱因斯坦", 600, 620, 44, at=2, rot=2, sfx="wood_low", gain=0.85),
            Card("埃莉诺·罗斯福", 520, 840, 40, at=4, rot=-2, sfx="wood_low", gain=0.75),
            Card("……", 840, 780, 44, at=6, rot=3, sfx="wood_low", gain=0.65),
        ], note="研究对象名单卡片"),
        Shot(4, "他们更能看清现实|也更能接纳自己和别人", "马斯洛原著 · 大意", [
            Icon("eye", 360, 760, 180, color=ACC, at=0, sfx="wood_low", note="看清现实"),
            Icon("heart", 720, 760, 160, color=K.RED, at=4, sfx="wood_high", note="接纳"),
        ], note="眼睛与心"),
        Shot(4, "专注于要解决的问题|不太随波逐流", "马斯洛原著 · 大意", [
            Icon("target", 720, 700, 200, color=ACC, at=0, sfx="wood_low"),
            Fig(320, GROUND, 320, at=0, pose="point", mood="calm", hair="short"),
            Fig(160, GROUND, 240, at=4, color=K.OTHER, face=-1, mood="flat", sfx="wood_high"),
            Fig(80, GROUND, 240, at=4, color=K.OTHER2, face=-1, mood="flat"),
        ], draw=A.ground, note="主角盯着目标，人群朝反方向走"),
        Shot(2, "需要独处|也有几段很深的关系", "马斯洛原著 · 大意", [
            Icon("house", 360, 760, 160, color=K.HERO, at=0, sfx="wood_low"),
            Icon("rings", 720, 760, 160, color=K.GOLD, at=2, sfx="wood_low"),
        ], text_beat=0, note="独处与深交"),
        Shot(2, "他们也有缺点|并不完美", "马斯洛原著 · 大意", [
            Fig(540, GROUND, 320, at=0, pose="shrug", mood="smile", hair="short"),
        ], draw=A.ground, text_beat=0, hits=[(2, "wood_high", 0.6, "耸肩一笑")], note="耸肩一笑的人"),
        Shot(3, "他估计这样的人|不到人口的 1%", "马斯洛原著 · 大意", [
            Custom(lambda c, g, t, d: _dots(c, g, t), x=540, y=760, at=0, enter="none"),
        ], hits=[(4, "rim", 0.8, "一个点亮起")], note="一百个点里只亮一个（示意）"),
        Shot(3, "批评：样本由他挑选|标准也偏主观", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=4, sfx="rim"),
        ], note="天平与问号"),
        Shot(2, "自我实现不是成名|是成为你自己", "马斯洛的视角", [
            Card("成名", 340, 720, 48, at=0, rot=-3, sfx="wood_low"),
            Icon("cross", 340, 880, 90, color=K.RED, at=1, sfx="rim"),
            Icon("mirror", 760, 760, 200, color=ACC, at=2, sfx="wood_high"),
        ], text_beat=0, note="“成名”打叉，镜子里是自己"),
        Shot(2, "试试：哪件事|你不做就不安？", "小练习", [
            Icon("bulb", 540, 760, 200, color=K.GOLD, at=0, sfx="wood_high"),
        ], text_beat=0, note="灯泡"),
        Shot(2, "下一讲：|忘了时间的那些时刻", "下一讲", [
            Custom(lambda c, g, t, d: A.peak(c, 0, 0, 260, clamp01(t / 1.2), g.t), x=540, y=820, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 07 讲：高峰体验"),
        end_shot(REFS, "07 高峰体验：你有过忘了时间的时刻吗？"),
    ]
    return Episode(6, "actualization", "自我实现", "活成自己的人是什么样？", ACC, shots, refs=REFS,
                   publish_title="活成自己的人是什么样？｜马斯洛心理学06 自我实现",
                   hashtags="#马斯洛 #心理学 #自我实现 #潜能",
                   cover_title="活成【自己】的人|是什么样？", cover_sub="马斯洛的自我实现", cover_shot=6, cover_t=6.0,
                   notes=["“音乐家必须作曲，画家必须画画，诗人必须写诗”“一个人能成为什么，就必须成为什么”见马斯洛 1943 年论文。",
                          "自我实现者研究见《动机与人格》（1954）第 11 章（1950 年首发），研究对象包括林肯、杰斐逊、爱因斯坦、埃莉诺·罗斯福等；"
                          "片中特征为该章所列特征的节选，马斯洛同时专门讨论了他们的缺点。",
                          "“不到人口的 1%”为马斯洛本人的粗略估计；片中一百个点只亮一个为示意。",
                          "该研究样本由马斯洛按自己的标准挑选，常被批评为主观、缺乏可重复性；片中第 11 镜列出这一质疑。"]).build()


def _dots(c, g, t):
    for i in range(100):
        x = (i % 10 - 4.5) * 64
        y = (i // 10 - 4.5) * 64
        k = clamp01((t - i * 0.006) / 0.3)
        lit = i == 57 and g.since(4) >= 0
        K.dot(c, x, y, (22 if lit else 16) * k, ACC if lit else K.LINE)
        if lit:
            K.ring(c, x, y, 32, K.GOLD, 5, ease_out(clamp01(g.since(4) / 0.4)))
