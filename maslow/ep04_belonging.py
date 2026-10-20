"""04 归属与爱：为什么一个人待久了会难受？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#C25B6A"
GROUND = A.GROUND_Y
REFS = ["Maslow, A. H. (1943). A Theory of Human Motivation. Psychological Review, 50(4), 370–396.",
        "Harlow, H. F. (1958). The nature of love. American Psychologist, 13(12), 673–685.",
        "Holt-Lunstad, J., Smith, T. B., & Layton, J. B. (2010). Social relationships and mortality risk. PLoS Medicine, 7(7)."]


def mothers(c, g, el_t, d):
    """哈洛实验示意：左边铁丝“妈妈”带奶瓶，右边绒布“妈妈”；小猴抱着绒布妈妈。"""
    for sx in (-1, 1):
        x = sx * 220
        K.dot(c, x, -240, 60, K.mix(K.INK3, K.BG, 0.3) if sx < 0 else "#D9B48A")
        if sx < 0:
            for i in range(7):
                K.seg(c, x - 80, -170 + i * 50, x + 80, -170 + i * 50, K.INK3, 6)
            K.seg(c, x - 80, -170, x - 80, 130, K.INK3, 6)
            K.seg(c, x + 80, -170, x + 80, 130, K.INK3, 6)
            K.rr(c, x + 110, -60, 30, 90, 10, K.PAPER)
            K.rr_stroke(c, x + 110, -60, 30, 90, 10, K.INK2, 3)
        else:
            K.rr(c, x, -20, 170, 300, 70, "#D9B48A")
        K.seg(c, x, 130, x, 230, K.INK2, 8)
    k = ease_out(clamp01(g.since(d.get("b1", 1)) / 0.8))
    mx = 160 * k
    K.dot(c, mx, -20 + 40 * (1 - k), 44 * max(k, 0.4), "#8A6A4A")
    K.dot(c, mx - 20, -60 + 40 * (1 - k), 26 * max(k, 0.4), "#8A6A4A")
    K.text(c, "铁丝 + 奶瓶", -220, 300, 30, "sans_medium", K.INK2)
    K.text(c, "绒布", 220, 300, 30, "sans_medium", K.INK2)


def build() -> Episode:
    shots = [
        Shot(3, "一个人待久了|会莫名地难受", "情境演绎", [
            Fig(420, GROUND, 320, at=0, pose="sit_sad", mood="sad", hair="short"),
            Icon("phone", 700, 960, 110, color=K.INK2, at=2, sfx="wood_low", note="没有消息的手机"),
            Icon("cloud", 600, 560, 160, color=K.INK3, at=6, sfx="rim"),
        ], draw=A.ground, note="独坐，手机没有消息"),
        Shot(3, "马斯洛说|安全之后，人渴望归属", "马斯洛原著 · 大意", [
            Custom(A.levels, x=540, y=760, at=0, seq=[(0, 1), (4, 2)], sfx="wood_low"),
        ], hits=[(4, "tom", 0.8, "高亮上移到归属与爱")], note="高亮从安全上移到归属与爱"),
        Shot(2, "这一层|叫作——", "马斯洛的视角", [
            Icon("heart", 540, 760, 240, color=ACC, at=0, sfx="rim"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "心定格")], note="一颗心"),
        Shot(4, "被接纳|也去爱别人", "马斯洛原著 · 大意", [
            Big("归属与爱", 540, 600, 150, at=0, sfx="kick", sub="Love & Belonging", note="概念落版（音乐 drop）"),
            Icon("heart", 540, 930, 120, color=ACC, at=2, enter="fade"),
        ], note="drop 处“归属与爱”砸下"),
        Shot(4, "爱既包括给出|也包括得到", "马斯洛原著 · 大意", [
            Fig(280, GROUND, 320, at=0, pose="give", mood="smile", hair="short"),
            Fig(800, GROUND, 320, at=0, pose="give", mood="smile", color=K.OTHER2, hair="bun", face=-1),
            Arrow((360, 720), (720, 720), at=2, color=ACC, width=12, bend=-0.25, sfx="wood_high"),
            Arrow((720, 820), (360, 820), at=4, color=ACC, width=12, bend=-0.25, sfx="wood_high"),
        ], draw=A.ground, note="两个人之间，爱的箭头双向流动"),
        Shot(4, "朋友、伴侣、家人|还有一个“我们”", "马斯洛原著 · 大意", [
            Icon("friends", 280, 760, 150, color=ACC, at=0, sfx="wood_low"),
            Icon("rings", 540, 760, 150, color=K.GOLD, at=2, sfx="wood_low", gain=0.85),
            Icon("house", 800, 760, 150, color=K.HERO, at=4, sfx="wood_low", gain=0.75),
        ], note="朋友、伴侣、家三个图标"),
        Shot(4, "马斯洛认为这一层受挫|常是心理困扰的核心", "马斯洛原著 · 大意", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", fill=(1, 1, 0.1, 0, 0), fill_at=0, hi=2),
        ], hits=[(2, "tom", 0.8, "归属层几乎是空的")], note="归属与爱这一层几乎是空的"),
        Shot(2, "他的导师哈洛|用小猴做过实验", "研究证据", [
            Txt("哈洛（Harry Harlow），威斯康星大学", 540, 1110, 30, at=0, font="sans_medium", color=K.INK2),
            Custom(mothers, x=540, y=700, at=0, b1=99),
        ], text_beat=0, note="哈洛的两个“代理妈妈”"),
        Shot(2, "小猴更爱抱着|软软的“布妈妈”", "研究证据", [
            Custom(mothers, x=540, y=700, at=0, enter="none", b1=0),
        ], text_beat=0, hits=[(1, "wood_high", 0.8, "小猴扑向布妈妈")], note="小猴抱住绒布妈妈"),
        Shot(3, "后来的研究也认为|归属是人的基本需要", "研究证据", [
            Icon("friends", 540, 720, 220, color=ACC, at=0, sfx="wood_low"),
            Txt("Baumeister & Leary，1995", 540, 900, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="“归属需要”综述"),
        Shot(3, "长期孤独|对健康的影响不容小看", "研究证据", [
            Icon("heart", 540, 720, 200, color=K.RED, at=0, sfx="wood_low"),
            Txt("Holt-Lunstad 等，2010：148 项研究的元分析", 540, 900, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="社会关系与健康的元分析"),
        Shot(2, "归属不在人多|在真被接纳", "当代理解", [
            Fig(400, GROUND, 300, at=0, pose="hug", mood="happy", hair="short"),
            Fig(660, GROUND, 300, at=0, pose="hug", mood="happy", color=K.OTHER2, hair="bun", face=-1),
        ], draw=A.ground, text_beat=0, hits=[(2, "wood_high", 0.7, "拥抱")], note="两个人相拥"),
        Shot(2, "试试：今天|主动联系一个人", "小练习", [
            Icon("phone", 540, 760, 200, color=ACC, at=0, sfx="wood_high"),
        ], text_beat=0, note="手机"),
        Shot(2, "下一讲：|为什么那么在乎被认可", "下一讲", [
            Icon("trophy", 540, 760, 200, color="#5B6FA8", at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 05 讲：尊重需要"),
        end_shot(REFS, "05 尊重需要：为什么我们那么在乎被认可？"),
    ]
    return Episode(4, "belonging", "归属与爱", "为什么一个人待久了会难受？", ACC, shots, refs=REFS,
                   publish_title="为什么一个人待久了会难受？｜马斯洛心理学04 归属与爱",
                   hashtags="#马斯洛 #心理学 #孤独 #归属感",
                   cover_title="一个人待久了|为什么会【难受】？", cover_sub="马斯洛的归属与爱", cover_shot=4, cover_t=6.0,
                   notes=["归属与爱见马斯洛 1943 年论文：爱的需要“既包括给予爱，也包括接受爱”；他认为这类需要受挫是心理失调中最常见的核心。",
                          "马斯洛 1934 年在威斯康星大学获得博士学位，导师是哈利·哈洛；哈洛的代理母亲实验发表于 1958 年（The Nature of Love）。",
                          "Baumeister 与 Leary（1995，Psychological Bulletin）提出“归属需要”是人的基本动机；Holt-Lunstad 等（2010）对 148 项研究的元分析显示社会关系与死亡风险相关。"]).build()
