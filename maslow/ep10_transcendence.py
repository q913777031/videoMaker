"""10 自我超越：自我实现之后，还有什么？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#4A7A6A"
GROUND = A.GROUND_Y
REFS = ["Maslow, A. H. (1969). The Farther Reaches of Human Nature. Journal of Transpersonal Psychology, 1(1), 1–9.",
        "Koltko-Rivera, M. E. (2006). Rediscovering the later version of Maslow's hierarchy of needs. Review of General Psychology, 10(4), 302–317.",
        "Maslow, A. H. (1954). Motivation and Personality, ch. 18 Toward a Positive Psychology. Harper & Row."]


def plus_layer(c, g, el_t, d):
    """五层之上再加一层“自我超越”：虚线框在 b1 拍后实化。"""
    A.hierarchy(c, 0, 80, 600, 90, 1, d.get("hi"))
    k = ease_out(clamp01(g.since(d.get("b1", 0)) / 0.6))
    y = 80 - 3 * 90 - 30
    K.rr_stroke(c, 0, y, 380, 78, 16, ACC, 5, 1, dash=(14, 10))
    if k > 0:
        K.rr(c, 0, y, 380, 78, 16, ACC, k)
        K.text(c, "自我超越", 0, y, 38, "serif_black", K.PAPER, k)


def build() -> Episode:
    shots = [
        Shot(3, "该有的都有了|然后呢？", "情境演绎", [
            Custom(lambda c, g, t, d: A.peak(c, 0, 0, 520, 0.4, g.t), x=540, y=900, at=0, enter="fade"),
            Fig(540, 640, 160, at=2, pose="stand", mood="calm", hair="short", sfx="wood_low",
                moves=[(6, dict(pose="think", mood="worried"))]),
            Bubble("然后呢？", 680, 460, 38, at=6, think=True, sfx="rim"),
        ], note="人站在山顶，望着前方"),
        Shot(3, "晚年的马斯洛|开始思考更高的一层", "马斯洛原著 · 大意", [
            Custom(plus_layer, x=540, y=760, at=0, b1=99, sfx="wood_low"),
        ], note="五层之上出现一个虚线框"),
        Shot(2, "他称它为——", "马斯洛原著 · 大意", [
            Custom(plus_layer, x=540, y=760, at=0, enter="none", b1=2),
        ], text_beat=0, hits=[(2, "rim", 0.8, "虚线框实化")], note="虚线框实化"),
        Shot(4, "为比自己|更大的东西而活", "马斯洛原著 · 大意", [
            Big("自我超越", 540, 600, 150, at=0, sfx="kick", sub="Self-Transcendence", note="概念落版（音乐 drop）"),
            Icon("sun", 540, 940, 140, color=K.GOLD, at=2, enter="fade"),
        ], note="drop 处“自我超越”砸下"),
        Shot(4, "关心他人、自然|或某种意义", "马斯洛原著 · 大意", [
            Icon("friends", 280, 760, 150, color=ACC, at=0, sfx="wood_low"),
            Icon("sprout", 540, 760, 150, color=K.GREEN, at=2, sfx="wood_low", gain=0.85),
            Icon("sun", 800, 760, 150, color=K.GOLD, at=4, sfx="wood_low", gain=0.75),
        ], note="他人、自然、意义"),
        Shot(4, "这一层|很少被画进流行的图里", "研究证据", [
            Custom(A.levels, x=540, y=800, at=0, enter="none", shape="pyramid", w=640, lh=96),
            Txt("Koltko-Rivera，2006", 540, 1150, 30, at=4, font="sans_medium", color=K.INK2, sfx="wood_high"),
        ], note="常见的五层金字塔里没有这一层"),
        Shot(4, "他称人本主义为|心理学的“第三势力”", "马斯洛原著 · 大意", [
            Card("行为主义", 300, 640, 40, at=0, rot=-2, sfx="wood_low"),
            Card("精神分析", 780, 640, 40, at=2, rot=2, sfx="wood_low", gain=0.85),
            Card("人本主义", 540, 880, 46, at=4, accent=ACC, sfx="tom", note="第三势力"),
        ], note="行为主义、精神分析之后的第三股力量"),
        Shot(2, "不只研究病|也研究人能有多好", "马斯洛的视角", [
            Icon("sprout", 540, 760, 200, color=K.GREEN, at=0, sfx="wood_high"),
        ], text_beat=0, note="芽"),
        Shot(2, "批评：概念模糊|难以实证检验", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="天平与问号"),
        Shot(3, "1954 年他就用过|“积极心理学”这个词", "当代理解", [
            Icon("book", 540, 720, 200, color=ACC, at=0, sfx="wood_low"),
            Txt("《动机与人格》第 18 章 Toward a Positive Psychology", 540, 900, 28, at=4, font="sans_medium", color=K.INK2),
        ], note="《动机与人格》最后一章的标题"),
        Shot(3, "今天它仍是|理解动机的常用框架", "当代理解", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", w=640, lh=96),
        ], hits=[(4, "wood_high", 0.6, "层次图定格")], note="需求层次图"),
        Shot(2, "试试：做一件事|只为别人，不图回报", "小练习", [
            Icon("gift", 540, 760, 200, color=ACC, at=0, sfx="wood_high"),
        ], text_beat=0, note="礼物"),
        Shot(2, "回到开头：|你现在最需要什么？", "小练习", [
            Custom(A.levels, x=540, y=760, at=0, seq=[(0, 0), (1, 1), (2, 2), (3, 3)], w=600, lh=90, sfx="wood_high"),
        ], text_beat=0, note="高亮逐层上移"),
        Shot(2, "十讲走完|愿你成为你能成为的人", "马斯洛的视角", [
            Custom(lambda c, g, t, d: A.peak(c, 0, 0, 360, ease_out(clamp01(t / 1.2)), g.t), x=540, y=860, at=0),
            Fig(540, 690, 120, at=1, pose="cheer", mood="happy", hair="short"),
        ], text_beat=0, hits=[(6, "cymbal", 0.5, "系列收尾")], note="山顶亮起，小人举起双手"),
        end_shot(REFS, None),
    ]
    return Episode(10, "transcendence", "自我超越", "自我实现之后，还有什么？", ACC, shots, refs=REFS,
                   publish_title="自我实现之后，还有什么？｜马斯洛心理学10 自我超越",
                   hashtags="#马斯洛 #心理学 #自我超越 #人本主义",
                   cover_title="自我实现之后|还有【什么】？", cover_sub="马斯洛的自我超越", cover_shot=1, cover_t=5.0,
                   notes=["晚年马斯洛在 1969 年的演讲与文章（The Farther Reaches of Human Nature）中提出“自我超越”，"
                          "Koltko-Rivera（2006）指出这一后期版本常被教材忽略。",
                          "马斯洛称人本主义心理学为继行为主义、精神分析之后的“第三势力”。",
                          "《动机与人格》（1954）最后一章题为 Toward a Positive Psychology；当代积极心理学由塞利格曼等人在 1998 年前后推动，"
                          "与马斯洛的设想有渊源，但并非他创立。",
                          "需求层次理论在实证上支持有限，片中第 9 镜列出这一质疑。"]).build()
