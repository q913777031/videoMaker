"""02 实现倾向：人天生想变好吗？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#7A8A3A"
GROUND = A.GROUND_Y
REFS = ["Rogers, C. R. (1980). A Way of Being, ch. 7 The Foundations of a Person-Centered Approach. Houghton Mifflin.",
        "Ryan, R. M., & Deci, E. L. (2000). Self-determination theory and the facilitation of intrinsic motivation. American Psychologist, 55(1), 68–78."]


def build() -> Episode:
    shots = [
        Shot(3, "人为什么|总想变得更好一点？", "情境演绎", [
            Fig(400, GROUND, 330, at=0, pose="reach", mood="open", hair="short"),
            Icon("sun", 780, 520, 180, color=K.GOLD, at=4, sfx="wood_high", note="远处的太阳"),
        ], draw=A.ground, note="人伸手够向远处的光"),
        Shot(3, "罗杰斯讲过|他小时候的一件事", "罗杰斯自述", [
            Fig(420, GROUND, 220, at=0, pose="stand", mood="smile", hair="short"),
            Icon("house", 760, 900, 300, color=ACC, at=2, sfx="wood_low", note="老家的房子"),
        ], draw=A.ground, note="小罗杰斯与老家的房子"),
        Shot(2, "地窖里存着土豆|只有一扇小窗", "罗杰斯自述", [
            Custom(A.basement, x=540, y=760, at=0, enter="fade", sprout=0),
        ], text_beat=0, hits=[(2, "rim", 0.7, "小窗透光")], note="昏暗的地窖、一扇小窗、一只土豆"),
        Shot(4, "生命总朝着|成长的方向", "罗杰斯原著 · 大意", [
            Big("实现倾向", 540, 560, 150, at=0, sfx="kick", sub="Actualizing Tendency", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.potato(c, 0, 0, 180, ease_out(clamp01(t / 3.0)) * 0.5), x=460, y=1000, at=2, enter="fade"),
        ], note="drop 处“实现倾向”砸下"),
        Shot(4, "土豆长出长长的白芽|一直伸向那点光", "罗杰斯自述", [
            Custom(A.basement, x=540, y=760, at=0, enter="fade",
                   sprout=lambda g, t: 0.1 + 0.9 * ease_out(clamp01(g.since(1) / 4.0))),
        ], hits=[(1, "wood_low", 0.6, "芽开始长"), (5, "tom", 0.7, "芽伸到光里")], note="白芽一路伸向小窗的光"),
        Shot(4, "罗杰斯说：人也一样|条件再差，也想长", "罗杰斯原著 · 大意", [
            Fig(400, GROUND, 330, at=0, pose="sit_sad", mood="worried", hair="short",
                moves=[(4, dict(pose="reach", mood="open"))]),
            Custom(lambda c, g, t, d: K.spotlight(c, 0, 0, 220, K.GOLD, 0.4 * clamp01(g.since(4) / 0.6)), x=760, y=560, at=0,
                   enter="none"),
        ], draw=A.ground, hits=[(4, "tom", 0.7, "站起来伸手")], note="人从蜷坐到站起伸手够光"),
        Shot(4, "这是人最根本的动力|不需要外力来推", "罗杰斯原著 · 大意", [
            Arrow((540, 1000), (540, 560), at=0, color=ACC, width=16, sfx="wood_low"),
            Icon("sprout", 540, 1060, 120, color=K.GREEN, at=0, enter="none"),
            Label("由内而外", 760, 760, 40, at=4, fill=ACC, sfx="wood_high"),
        ], note="一支向上的箭头：由内而外"),
        Shot(2, "芽又白又弱|却从没放弃", "罗杰斯自述", [
            Custom(lambda c, g, t, d: A.potato(c, 0, 0, 220, 0.8), x=440, y=920, at=0, sfx="wood_low"),
        ], text_beat=0, note="又白又细的芽"),
        Shot(2, "他想到那些|处境艰难的来访者", "罗杰斯自述", [
            Fig(540, GROUND, 320, at=0, pose="sit_sad", mood="sad", color=K.OTHER2, hair="bun"),
        ], draw=A.ground, text_beat=0, note="蜷坐的人"),
        Shot(3, "所以咨询不是“修好”人|而是给他一点光", "罗杰斯的视角", [
            Card("修好", 320, 680, 48, at=0, rot=-3, sfx="wood_low"),
            Icon("cross", 320, 840, 90, color=K.RED, at=2, sfx="rim"),
            Icon("sun", 760, 740, 200, color=K.GOLD, at=4, sfx="wood_high"),
        ], note="“修好”打叉，换成一束光"),
        Shot(3, "批评：这对人性|太乐观了", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=4, sfx="rim"),
        ], note="天平与问号"),
        Shot(2, "当代研究也认为|人有成长的动机", "当代理解", [
            Icon("sprout", 540, 720, 200, color=K.GREEN, at=0, sfx="wood_low"),
            Txt("自我决定理论（Ryan & Deci）", 540, 900, 30, at=1, font="sans_medium", color=K.INK2),
        ], text_beat=0, note="自我决定理论"),
        Shot(2, "试试：你最近|在朝哪束光长？", "小练习", [
            Icon("sun", 540, 760, 220, color=K.GOLD, at=0, sfx="wood_high"),
        ], text_beat=0, note="太阳"),
        Shot(2, "下一讲：|你心里的那个“我”", "下一讲", [
            Icon("mirror", 540, 760, 220, color=A.DUSK, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 03 讲：自我概念"),
        end_shot(REFS, "03 自我概念：你心里的“我”，是真的你吗？"),
    ]
    return Episode(2, "actualizing", "实现倾向", "人天生想变好吗？", ACC, shots, refs=REFS,
                   publish_title="人天生想变好吗？｜罗杰斯心理学02 实现倾向",
                   hashtags="#罗杰斯 #心理学 #成长 #人本主义",
                   cover_title="人天生|想【变好】吗？", cover_sub="罗杰斯的实现倾向", cover_shot=4, cover_t=6.5,
                   notes=["地窖土豆的故事见罗杰斯《存在之道》（A Way of Being，1980）：童年家中地窖里储存的土豆，在昏暗中长出苍白的长芽，"
                          "伸向远处小窗透进的光；他以此比喻一切生命朝向实现的倾向，并联想到处境极差的病人。",
                          "实现倾向被罗杰斯视为人唯一的基本动机。批评者认为这一人性观过于乐观，片中第 11 镜列出这一质疑。",
                          "自我决定理论（Ryan & Deci）关于内在动机的研究与这一观点相呼应，但并非罗杰斯理论本身。"]).build()
