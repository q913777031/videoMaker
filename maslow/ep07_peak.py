"""07 高峰体验：你有过忘了时间的时刻吗？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#B07A2A"
GROUND = A.GROUND_Y
REFS = ["Maslow, A. H. (1962). Toward a Psychology of Being, ch. 6 Cognition of Being in the Peak-Experiences. Van Nostrand.",
        "Maslow, A. H. (1964). Religions, Values, and Peak-Experiences. Ohio State University Press.",
        "Csikszentmihalyi, M. (1990). Flow: The Psychology of Optimal Experience. Harper & Row."]


def flow_chart(c, g, el_t, d):
    """心流示意：横轴能力、纵轴挑战，对角线附近的通道为心流区。"""
    k = ease_out(clamp01(el_t / 0.8))
    W, H = 560, 560
    K.poly(c, [(-W / 2, H / 2), (-W / 2 + 120, H / 2), (W / 2, -H / 2 + 120), (W / 2, -H / 2), (W / 2 - 120, -H / 2),
               (-W / 2, H / 2 - 120)], K.mix(ACC, K.BG, 0.55), k)
    K.seg(c, -W / 2, H / 2, W / 2, H / 2, K.INK, 6, k)
    K.seg(c, -W / 2, H / 2, -W / 2, -H / 2, K.INK, 6, k)
    K.text(c, "能力 →", W / 2 - 60, H / 2 + 50, 32, "sans_medium", K.INK2, k)
    K.text(c, "挑战 ↑", -W / 2 + 10, -H / 2 - 40, 32, "sans_medium", K.INK2, k)
    q = ease_out(clamp01(g.since(d.get("b1", 4)) / 0.6))
    if q > 0:
        K.text(c, "心流", 0, 0, 52, "serif_black", K.INK, q)
        K.text(c, "焦虑", -W / 2 + 120, -H / 2 + 120, 34, "serif_black", K.INK3, q)
        K.text(c, "无聊", W / 2 - 120, H / 2 - 110, 34, "serif_black", K.INK3, q)


def build() -> Episode:
    shots = [
        Shot(3, "看日落、听音乐时|有时会突然被击中", "情境演绎", [
            Fig(360, GROUND, 330, at=0, pose="stand", mood="calm", hair="short",
                moves=[(6, dict(pose="cheer", mood="happy"))]),
            Icon("sun", 780, 760, 220, color=K.GOLD, at=0, sfx="wood_low", note="落日"),
            Custom(lambda c, g, t, d: K.burst(c, 0, 0, t, K.GOLD), x=360, y=720, at=6, enter="none", sfx="clap", note="被击中"),
        ], draw=A.ground, note="看日落时突然心头一亮"),
        Shot(3, "马斯洛请很多人描述|一生中最美好的时刻", "马斯洛原著 · 大意", [
            Fig(300, GROUND, 320, at=0, pose="point", mood="open", hair="short", color="#6A5A4A"),
            Bubble("最美好的一刻？", 420, 620, 38, at=2, sfx="wood_high"),
            Fig(780, GROUND, 300, at=0, color=K.OTHER2, hair="bun", face=-1, mood="happy"),
            Bubble("那天……", 780, 640, 38, at=6, sfx="wood_high"),
        ], draw=A.ground, note="马斯洛提问，受访者回忆"),
        Shot(2, "这种时刻|他叫作——", "马斯洛的视角", [
            Custom(lambda c, g, t, d: A.peak(c, 0, 0, 320, ease_out(clamp01(g.since(2) / 0.8)), g.t), x=540, y=820, at=0),
        ], text_beat=0, hits=[(2, "rim", 0.8, "山顶亮起")], note="山顶亮起"),
        Shot(4, "强烈的喜悦|和完整感", "马斯洛原著 · 大意", [
            Big("高峰体验", 540, 560, 150, at=0, sfx="kick", sub="Peak Experience", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.peak(c, 0, 0, 200, 1, g.t), x=540, y=960, at=2, enter="fade"),
        ], note="drop 处“高峰体验”砸下"),
        Shot(4, "时间好像停了|自我好像消失了", "马斯洛原著 · 大意", [
            Icon("clock", 540, 720, 220, color=ACC, at=0, sfx="wood_low"),
            Custom(lambda c, g, t, d: K.spotlight(c, 0, 0, 300, K.GOLD, 0.5 * clamp01(g.since(4) / 0.8)), x=540, y=720, at=0,
                   enter="none"),
        ], hits=[(4, "tom", 0.7, "光晕铺开")], note="时钟停住，光晕铺开"),
        Shot(4, "觉得一切都对了|世界是好的", "马斯洛原著 · 大意", [
            Fig(540, GROUND, 330, at=0, pose="cheer", mood="happy", hair="short"),
            Icon("sun", 540, 520, 160, color=K.GOLD, at=2, sfx="wood_high"),
        ], draw=A.ground, note="张开双臂的人"),
        Shot(4, "它不只属于圣人|普通人也常有", "马斯洛原著 · 大意", [
            Fig(240, GROUND, 280, at=0, color=K.OTHER, mood="smile"),
            Fig(540, GROUND, 280, at=2, color=K.OTHER2, mood="smile", hair="bun", sfx="wood_low"),
            Fig(840, GROUND, 280, at=4, color=K.OTHER3, mood="smile", face=-1, sfx="wood_low"),
            Custom(lambda c, g, t, d: K.spotlight(c, 0, 0, 500, K.GOLD, 0.3 * clamp01(t / 0.8)), x=540, y=880, at=6, enter="none",
                   sfx="clap"),
        ], draw=A.ground, note="三个普通人都被光照到"),
        Shot(2, "可能在创作、相爱|或看到美的时候", "马斯洛原著 · 大意", [
            Icon("bulb", 300, 760, 150, color=K.GOLD, at=0, sfx="wood_high"),
            Icon("heart", 540, 760, 150, color=K.RED, at=1, sfx="wood_high", gain=0.85),
            Icon("sun", 780, 760, 150, color=K.GOLD, at=2, sfx="wood_high", gain=0.75),
        ], text_beat=0, note="创作、爱、美"),
        Shot(2, "它没法硬求|却会改变一个人", "马斯洛原著 · 大意", [
            Custom(lambda c, g, t, d: A.sprout_grow(c, 0, 0, 300, clamp01(t / 1.6)), x=540, y=880, at=0, sfx="wood_low"),
        ], text_beat=0, note="芽长出"),
        Shot(3, "后来契克森米哈赖|提出了相近的“心流”", "当代理解", [
            Icon("book", 540, 720, 200, color=ACC, at=0, sfx="wood_low"),
            Txt("Csikszentmihalyi，《心流》，1990", 540, 900, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="《心流》"),
        Shot(3, "心流出现在|挑战与能力刚好匹配时", "当代理解", [
            Custom(flow_chart, x=540, y=760, at=0, b1=4, sfx="wood_low"),
        ], hits=[(4, "rim", 0.8, "心流区标出")], note="挑战—能力图，对角通道是心流区"),
        Shot(2, "高峰体验难以测量|多半来自自述", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="天平与问号"),
        Shot(2, "试试：回想一次|你忘了时间的时刻", "小练习", [
            Icon("clock", 540, 760, 200, color=ACC, at=0, sfx="wood_high"),
        ], text_beat=0, note="时钟"),
        Shot(2, "下一讲：|金字塔是马斯洛画的吗", "下一讲", [
            Custom(A.levels, x=540, y=760, at=0, shape="pyramid", w=700, lh=100, sfx="wood_high"),
        ], text_beat=0, note="预告第 08 讲：金字塔的误读"),
        end_shot(REFS, "08 金字塔误读：马斯洛画过金字塔吗？"),
    ]
    return Episode(7, "peak", "高峰体验", "你有过忘了时间的时刻吗？", ACC, shots, refs=REFS,
                   publish_title="你有过忘了时间的时刻吗？｜马斯洛心理学07 高峰体验",
                   hashtags="#马斯洛 #心理学 #高峰体验 #心流",
                   cover_title="你有过|【忘了时间】的时刻吗？", cover_sub="马斯洛的高峰体验", cover_shot=5, cover_t=6.0,
                   notes=["高峰体验见《存在心理学探索》（1962）第 6 章与《宗教、价值与高峰体验》（1964）；马斯洛请受访者描述一生中最美妙的经历，"
                          "归纳出时间感消失、忘我、觉得世界是好的等特征。",
                          "马斯洛后来认为高峰体验并非少数人的专利，多数人都有过，只是常被忽略。",
                          "“心流”由契克森米哈赖提出（《心流》，1990），与高峰体验相近但不相同：心流强调挑战与能力匹配时的专注状态。"]).build()
