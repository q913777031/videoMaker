"""01 来访者中心：为什么最好的帮助，是不急着给建议？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = A.SAGE
GROUND = A.GROUND_Y
REFS = ["Rogers, C. R. (1942). Counseling and Psychotherapy. Houghton Mifflin.",
        "Rogers, C. R. (1951). Client-Centered Therapy. Houghton Mifflin."]


def build() -> Episode:
    shots = [
        Shot(3, "朋友找你诉苦|你马上给了一堆建议", "情境演绎", [
            Fig(300, GROUND, 320, at=0, pose="point", mood="open", hair="short"),
            Fig(780, GROUND, 320, at=0, pose="sad", mood="sad", color=K.OTHER2, hair="bun", face=-1),
            Bubble("你应该……", 320, 600, 38, at=2, sfx="wood_high"),
            Bubble("你得……", 420, 480, 34, at=4, sfx="wood_high", gain=0.85),
            Bubble("要我说……", 260, 400, 32, at=6, sfx="wood_high", gain=0.75),
        ], draw=A.ground, note="一人连珠炮给建议，另一人低头"),
        Shot(3, "可对方|反而更不想说了", "情境演绎", [
            Fig(300, GROUND, 320, at=0, enter="none", pose="shrug", mood="worried", hair="short"),
            Fig(780, GROUND, 320, at=0, enter="none", pose="sad", mood="sad", color=K.OTHER2, hair="bun", face=-1,
                moves=[(4, dict(face=1, pose="cover"))]),
        ], draw=A.ground, hits=[(4, "rim", 0.8, "对方转身")], note="对方转过身去"),
        Shot(2, "罗杰斯提出了|另一种做法——", "罗杰斯的视角", [
            Custom(A.two_chairs, x=540, y=GROUND, at=0, enter="pop", sfx="wood_low"),
        ], draw=A.ground, text_beat=0, hits=[(4, "rim", 0.8, "两把椅子定格")], note="两把椅子面对面"),
        Shot(4, "相信对方|最清楚自己的路", "罗杰斯原著 · 大意", [
            Big("来访者中心", 540, 580, 140, at=0, sfx="kick", sub="Client-Centered", note="概念落版（音乐 drop）"),
            Custom(A.two_chairs, x=540, y=1100, at=2, enter="fade", s=240, gap=260),
        ], note="drop 处“来访者中心”砸下"),
        Shot(4, "他把“病人”|改叫“来访者”", "罗杰斯原著 · 大意", [
            Card("病人", 340, 680, 50, at=0, rot=-3, sfx="wood_low"),
            Icon("cross", 340, 860, 100, color=K.RED, at=2, sfx="rim"),
            Card("来访者", 760, 760, 50, at=4, rot=2, accent=ACC, sfx="tom", note="改称来访者"),
            Txt("卡尔·罗杰斯（1902–1987），美国心理学家", 540, 1180, 30, at=1, font="sans_medium", color=K.INK2),
        ], note="“病人”打叉，换成“来访者”"),
        Shot(4, "咨询师不当专家|不替人做决定", "罗杰斯原著 · 大意", [
            Custom(A.two_chairs, x=540, y=GROUND, at=0, enter="none"),
            Icon("brief", 300, 600, 120, color=K.DARK, at=2, sfx="wood_low", note="专家的公文包"),
            Icon("cross", 300, 600, 90, color=K.RED, at=4, sfx="rim"),
        ], draw=A.ground, note="咨询师一侧的“专家”公文包被打叉"),
        Shot(4, "而是陪对方|把自己的感受说清楚", "罗杰斯原著 · 大意", [
            Custom(A.two_chairs, x=540, y=GROUND, at=0, enter="none", right_mood="worried"),
            Bubble("其实我很怕……", 740, 560, 36, at=2, sfx="wood_high"),
            Icon("heart", 540, 520, 90, color=K.RED, at=6, sfx="clap", note="被听见"),
        ], draw=A.ground, note="来访者说出心里话"),
        Shot(2, "他相信|人有自己改变的力量", "罗杰斯原著 · 大意", [
            Custom(lambda c, g, t, d: A.potato(c, 0, 0, 200, clamp01(t / 1.6)), x=480, y=900, at=0, sfx="wood_low"),
        ], text_beat=0, note="一只土豆发芽（预告第 02 讲的比喻）"),
        Shot(2, "早年这被叫作|“非指导式”咨询", "罗杰斯原著", [
            Card("非指导式", 540, 720, 54, at=0, accent=ACC, sfx="wood_low"),
            Txt("《咨询与心理治疗》，1942", 540, 880, 30, at=1, font="sans_medium", color=K.INK2),
        ], text_beat=0, note="非指导式咨询"),
        Shot(3, "他也是最早把咨询过程|录音研究的人之一", "研究证据", [
            Custom(lambda c, g, t, d: A.recorder(c, 0, 0, 360, g.t), x=540, y=760, at=0, sfx="wood_low", note="录音机"),
        ], hits=[(4, "wood_high", 0.6, "磁带转动")], note="开盘录音机转动"),
        Shot(3, "后来这套做法|改称“以人为中心”", "罗杰斯原著", [
            Card("以人为中心", 540, 720, 52, at=0, accent=ACC, sfx="wood_low"),
            Txt("Person-Centered Approach", 540, 860, 32, at=2, font="sans_medium", color=K.INK2),
        ], note="以人为中心"),
        Shot(2, "批评：只靠倾听|有些问题不够", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="天平与问号"),
        Shot(2, "试试：先别给建议|问“你怎么想？”", "小练习", [
            Bubble("你怎么想？", 540, 720, 48, at=0, sfx="wood_high"),
        ], text_beat=0, note="对话框"),
        Shot(2, "下一讲：|地窖里的土豆", "下一讲", [
            Custom(lambda c, g, t, d: A.potato(c, 0, 0, 240, 0.3), x=540, y=800, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 02 讲：实现倾向"),
        end_shot(REFS, "02 实现倾向：人天生想变好吗？"),
    ]
    return Episode(1, "client", "来访者中心", "为什么最好的帮助，是不急着给建议？", ACC, shots, refs=REFS,
                   publish_title="为什么最好的帮助，是不急着给建议？｜罗杰斯心理学01 来访者中心",
                   hashtags="#罗杰斯 #心理学 #心理咨询 #人本主义",
                   cover_title="最好的帮助|是【不急着】给建议", cover_sub="罗杰斯的来访者中心疗法", cover_shot=6, cover_t=6.0,
                   notes=["罗杰斯在《咨询与心理治疗》（1942）中提出非指导式咨询，《来访者中心疗法》（1951）正式使用“来访者中心”，"
                          "后期扩展为“以人为中心取向”。他以“来访者”（client）取代“病人”（patient）。",
                          "罗杰斯是最早系统录音并逐字分析咨询过程的研究者之一，《咨询与心理治疗》收录了完整录音转写的个案。",
                          "批评者认为非指导式取向对重性精神障碍等问题不够，片中第 12 镜列出这一质疑。"]).build()
