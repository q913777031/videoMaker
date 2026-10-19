"""06 内倾与外倾：聚会后，你是累还是兴奋？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#2F6A8C"
GROUND = A.GROUND_Y
REFS = ["Jung, C. G. (1921). Psychologische Typen（Psychological Types）. CW 6.",
        "McCrae, R. R., & Costa, P. T. (1989). Reinterpreting the Myers-Briggs Type Indicator from the perspective of the five-factor model. Journal of Personality, 57(1)."]


def battery(c, g, el_t, d):
    """电量条：d['lvl'] 为 (起, 止)，从入场起 1.2 秒内变化。"""
    a, b = d["lvl"]
    v = a + (b - a) * ease_out(clamp01(el_t / 1.2))
    K.rr(c, 0, 0, 200, 90, 14, K.PAPER)
    K.rr_stroke(c, 0, 0, 200, 90, 14, K.INK, 5)
    K.rr(c, 108, 0, 16, 36, 4, K.INK)
    col = K.GREEN if v > 0.5 else (K.GOLD if v > 0.25 else K.RED)
    K.rr(c, -90 + 180 * v / 2 - 0, 0, 180 * v, 70, 8, col)


def build() -> Episode:
    shots = [
        Shot(3, "聚会结束|有人更累，有人更兴奋", "情境演绎", [
            Fig(320, GROUND, 320, at=0, pose="sad", mood="worried", hair="short"),
            Fig(760, GROUND, 320, at=0, pose="cheer", mood="happy", color=K.OTHER2, face=-1),
            Custom(battery, x=320, y=560, at=2, lvl=(0.8, 0.2), sfx="wood_low", note="左边的人电量下降"),
            Custom(battery, x=760, y=560, at=4, lvl=(0.4, 0.95), sfx="wood_high", note="右边的人电量上升"),
        ], draw=A.ground, note="同一场聚会：一人电量下降、一人电量上升"),
        Shot(3, "这种差别|荣格在 1921 年写进了书里", "荣格原著", [
            Icon("book", 540, 760, 220, color=ACC, at=0, sfx="wood_low"),
            Txt("《心理类型》，1921", 540, 940, 34, at=4, font="sans_medium", color=K.INK2),
        ], note="《心理类型》"),
        Shot(2, "心理能量的方向|叫作——", "荣格的视角", [
            Arrow((540, 760), (300, 760), at=0, color=ACC, width=14, sfx="rim"),
            Arrow((540, 760), (780, 760), at=2, color=K.GOLD, width=14, sfx="rim"),
        ], text_beat=0, note="两支相反的箭头"),
        Shot(4, "能量朝内|还是朝外", "荣格原著 · 大意", [
            Big("内倾 · 外倾", 540, 600, 140, at=0, sfx="kick", sub="Introversion · Extraversion", note="概念落版（音乐 drop）"),
        ], note="drop 处概念砸下"),
        Shot(4, "外倾：|注意力流向外部世界", "荣格原著 · 大意", [
            Fig(540, GROUND, 340, at=0, pose="wave", mood="happy", color=K.OTHER2),
            Arrow((620, 760), (900, 600), at=2, color=K.GOLD, width=12, sfx="wood_high"),
            Icon("friends", 900, 520, 120, color=K.GOLD, at=4, sfx="wood_high"),
        ], draw=A.ground, note="外倾：箭头向外指向人群"),
        Shot(4, "内倾：|注意力流向内心世界", "荣格原著 · 大意", [
            Fig(540, GROUND, 340, at=0, pose="think", mood="calm", hair="short"),
            Bubble("……", 640, 600, 40, at=2, think=True, sfx="wood_high"),
            Icon("book", 860, 900, 120, color=ACC, at=4, sfx="wood_low"),
        ], draw=A.ground, note="内倾：注意力回到内心"),
        Shot(4, "内向不等于害羞|外向也不等于会说话", "常见误区", [
            Card("内向 ≠ 害羞", 540, 680, 48, at=0, rot=-2, sfx="wood_low"),
            Card("外向 ≠ 健谈", 540, 880, 48, at=4, rot=2, sfx="wood_low"),
        ], note="两张纠错卡"),
        Shot(2, "这是方向|不是能力", "荣格的视角", [
            Icon("check", 540, 760, 160, color=K.GREEN, at=0, sfx="clap"),
        ], text_beat=0, note="打勾"),
        Shot(2, "人人两样都有|只是偏向不同", "荣格的视角", [
            Icon("scale", 540, 760, 220, color=ACC, at=0, sfx="wood_low"),
        ], text_beat=0, note="天平稍稍倾斜"),
        Shot(3, "大多数人|处在两者之间", "荣格的视角", [
            Custom(lambda c, g, t, d: _spectrum(c, g, t), x=540, y=760, at=0, enter="pop", sfx="wood_low"),
        ], note="一条从内倾到外倾的光谱，大多数点落在中间"),
        Shot(3, "外向性至今|仍是人格研究的核心维度", "研究证据", [
            Card("大五人格：外向性", 540, 760, 46, at=0, accent=ACC, sfx="wood_high"),
        ], note="大五人格模型中的外向性"),
        Shot(2, "试试：|今天的能量来自哪里？", "小练习", [
            Custom(battery, x=540, y=760, at=0, lvl=(0.3, 0.8), sfx="wood_high"),
        ], text_beat=0, note="电量条回升"),
        Shot(2, "累了，就回到|让你充电的那一边", "小练习", [
            Icon("house", 380, 820, 200, color=ACC, at=0, sfx="wood_low"),
            Icon("friends", 720, 820, 160, color=K.GOLD, at=2, sfx="wood_low"),
        ], text_beat=0, note="独处与相聚两种充电方式"),
        Shot(2, "下一讲：|四种心理功能", "下一讲", [
            Custom(lambda c, g, t, d: A.compass(c, 0, 0, 200, p=ease_out(clamp01(t / 1.2))), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 07 讲：四种功能"),
        end_shot(REFS, "07 四种功能：你先想，还是先感受？"),
    ]
    return Episode(6, "attitude", "内倾与外倾", "聚会后，你是累还是兴奋？", ACC, shots, refs=REFS,
                   publish_title="聚会后，你是累还是兴奋？｜荣格心理学06 内倾与外倾",
                   hashtags="#荣格 #心理学 #内向 #外向 #心理类型",
                   cover_title="聚会后，你是|【累】还是【兴奋】？", cover_sub="荣格的内倾与外倾", cover_shot=0, cover_t=6.0,
                   notes=["内倾与外倾见荣格《心理类型》（1921，CW 6），他以“心理能量（力比多）的方向”来区分两种态度。",
                          "“大多数人处在两者之间”是对荣格“纯粹的类型很少见”说法的通俗表述。",
                          "外向性是大五人格模型的维度之一，但大五的外向性与荣格的内外倾并不完全相同；片中仅说明这一维度在当代研究中仍很重要。"]).build()


def _spectrum(c, g, t):
    K.seg(c, -380, 0, 380, 0, K.INK, 8)
    K.text(c, "内倾", -380, 70, 36, "serif_black", K.INK)
    K.text(c, "外倾", 380, 70, 36, "serif_black", K.INK)
    import math
    for i in range(24):
        x = (math.sin(i * 2.3) * 0.5 + math.sin(i * 0.7) * 0.3) * 330
        k = clamp01((t - 0.3 - i * 0.05) / 0.3)
        K.dot(c, x, -30 - (i % 4) * 22, 12 * k, ACC)
