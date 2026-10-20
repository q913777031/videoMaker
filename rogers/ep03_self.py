"""03 自我概念：你心里的“我”，是真的你吗？"""

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = A.DUSK
GROUND = A.GROUND_Y
REFS = ["Rogers, C. R. (1959). A theory of therapy, personality, and interpersonal relationships. In S. Koch (Ed.), Psychology: A Study of a Science.",
        "Butler, J. M., & Haigh, G. V. (1954). In Rogers & Dymond (Eds.), Psychotherapy and Personality Change.",
        "Rogers, C. R. (1961). On Becoming a Person. Houghton Mifflin."]


def build() -> Episode:
    shots = [
        Shot(3, "你觉得自己|是个什么样的人？", "情境演绎", [
            Fig(400, GROUND, 330, at=0, pose="think", mood="calm", hair="short"),
            Bubble("我是……", 560, 620, 42, at=4, think=True, sfx="wood_high"),
        ], draw=A.ground, note="人托腮想“我是谁”"),
        Shot(3, "罗杰斯说|每个人心里都有一幅“自画像”", "罗杰斯原著 · 大意", [
            Icon("photo", 540, 740, 260, color=ACC, at=0, sfx="wood_low", note="自画像"),
        ], hits=[(6, "rim", 0.7, "画像定格")], note="一幅画像"),
        Shot(2, "这幅画|叫作——", "罗杰斯的视角", [
            Icon("mirror", 540, 760, 260, color=ACC, at=0, sfx="rim"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "镜子定格")], note="镜子"),
        Shot(4, "“我是谁”|的那套看法", "罗杰斯原著 · 大意", [
            Big("自我概念", 540, 600, 150, at=0, sfx="kick", sub="Self-Concept", note="概念落版（音乐 drop）"),
            Icon("mirror", 540, 930, 130, color=ACC, at=2, enter="fade"),
        ], note="drop 处“自我概念”砸下"),
        Shot(4, "里面有现在的我|也有想成为的我", "罗杰斯原著 · 大意", [
            Custom(A.ideal_gap, x=540, y=GROUND, at=0, gap=1.0, sfx="wood_low"),
        ], draw=A.ground, hits=[(4, "wood_high", 0.7, "理想自我浮现")], note="实线的真实自我、虚线的理想自我"),
        Shot(4, "两者差得太远|人就容易痛苦", "罗杰斯原著 · 大意", [
            Custom(A.ideal_gap, x=540, y=GROUND, at=0, enter="none", mood="worried",
                   gap=lambda g, t: 1 + 0.6 * ease_out(clamp01(g.since(2) / 1.2))),
        ], draw=A.ground, hits=[(2, "tom", 0.8, "距离拉大")], note="两者越拉越远"),
        Shot(4, "研究：咨询之后|两者的距离变近了", "研究证据", [
            Custom(A.ideal_gap, x=540, y=GROUND, at=0, enter="none", mood="smile",
                   gap=lambda g, t: 1 - 0.55 * ease_in_out(clamp01(g.since(2) / 1.6))),
            Txt("Butler & Haigh，1954：Q 分类法", 540, 560, 30, at=4, font="sans_medium", color=K.INK2),
        ], draw=A.ground, hits=[(2, "wood_low", 0.7, "距离收拢")], note="真实自我与理想自我靠拢"),
        Shot(2, "自画像常来自|别人怎么看你", "罗杰斯原著 · 大意", [
            Fig(540, GROUND, 300, at=0, pose="stand", mood="calm", hair="short"),
            Fig(220, GROUND, 260, at=0, color=K.OTHER, pose="point", mood="flat"),
            Fig(860, GROUND, 260, at=1, color=K.OTHER3, pose="point", mood="flat", face=-1, sfx="wood_low"),
        ], draw=A.ground, text_beat=0, note="两旁的人指指点点"),
        Shot(2, "画得不准|也会照着它活", "机制示意", [
            Icon("photo", 540, 740, 220, color=K.INK3, at=0, sfx="wood_low"),
            Icon("question", 700, 600, 90, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="模糊的画像与问号"),
        Shot(3, "罗杰斯说：当我接纳自己|反而能够改变", "罗杰斯原著 · 大意", [
            Fig(540, GROUND, 330, at=0, pose="hug", mood="calm", hair="short", moves=[(4, dict(mood="smile"))]),
            Icon("sprout", 780, 1040, 150, color=K.GREEN, at=4, sfx="wood_high"),
        ], draw=A.ground, note="抱住自己的人，身旁长出新芽"),
        Shot(3, "他称之为|一个“奇妙的悖论”", "罗杰斯原著", [
            Card("接纳", 340, 720, 50, at=0, rot=-3, accent=ACC, sfx="wood_low"),
            Arrow((440, 760), (640, 760), at=2, color=ACC, width=12, sfx="rim"),
            Card("改变", 760, 760, 50, at=4, rot=2, accent=K.GREEN, sfx="wood_low"),
        ], note="接纳 → 改变"),
        Shot(2, "自我概念|可以一点点改写", "当代理解", [
            Icon("book", 540, 760, 220, color=ACC, at=0, sfx="wood_low"),
        ], text_beat=0, note="翻开的本子"),
        Shot(2, "试试：写下三句|“我是……”", "小练习", [
            Card(["我是……", "我是……", "我是……"], 540, 760, 40, at=0, sfx="wood_high"),
        ], text_beat=0, note="三行“我是……”"),
        Shot(2, "下一讲：|“表现好才配被爱”", "下一讲", [
            Custom(lambda c, g, t, d: A.tag_heart(c, 0, 0, 160), x=480, y=800, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 04 讲：价值条件"),
        end_shot(REFS, "04 价值条件：为什么总觉得表现好才配被爱？"),
    ]
    return Episode(3, "self", "自我概念", "你心里的“我”，是真的你吗？", ACC, shots, refs=REFS,
                   publish_title="你心里的“我”，是真的你吗？｜罗杰斯心理学03 自我概念",
                   hashtags="#罗杰斯 #心理学 #自我认知",
                   cover_title="你心里的“我”|是【真的你】吗？", cover_sub="罗杰斯的自我概念", cover_shot=4, cover_t=6.0,
                   notes=["自我概念、真实自我与理想自我见罗杰斯 1959 年的理论总论（Koch 主编《心理学：一门科学的研究》第 3 卷）。",
                          "Butler 与 Haigh（1954）用 Q 分类法测量来访者“自我”与“理想自我”的相关，咨询后两者的一致程度明显上升。",
                          "“奇妙的悖论是：当我如实接纳自己时，我才能改变”见《个人形成论》（On Becoming a Person，1961），片中为大意。"]).build()
