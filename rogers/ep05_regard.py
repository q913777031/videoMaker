"""05 无条件积极关注：接纳一个人，等于认同一切吗？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#B05070"
GROUND = A.GROUND_Y
REFS = ["Rogers, C. R. (1957). The necessary and sufficient conditions of therapeutic personality change. Journal of Consulting Psychology, 21(2), 95–103.",
        "Farber, B. A., Suzuki, J. Y., & Lynch, D. A. (2018). Positive regard and psychotherapy outcome: A meta-analytic review. Psychotherapy, 55(4), 411–423."]


def build() -> Episode:
    shots = [
        Shot(3, "孩子打碎了杯子|你第一句会说什么？", "情境演绎", [
            Fig(360, GROUND, 340, at=0, color=K.OTHER, pose="stand", mood="surprised"),
            Fig(680, GROUND, 220, at=0, pose="cover", mood="worried", hair="short"),
            Custom(lambda c, g, t, d: _shards(c, t), x=860, y=1110, at=2, enter="none", sfx="clap", note="杯子碎了"),
            Bubble("……", 380, 660, 44, at=6, sfx="wood_high"),
        ], draw=A.ground, note="杯子碎了，孩子捂脸，大人还没开口"),
        Shot(3, "罗杰斯认为|改变需要一种特别的关注", "罗杰斯原著 · 大意", [
            Icon("heart", 540, 740, 240, color=ACC, at=0, sfx="wood_low"),
        ], hits=[(6, "rim", 0.7, "心跳一下")], note="一颗心"),
        Shot(2, "这种关注|叫作——", "罗杰斯的视角", [
            Icon("heart", 540, 760, 280, color=ACC, at=0, enter="none"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "心定格")], note="心放大"),
        Shot(4, "接纳这个人|不附加条件", "罗杰斯原著 · 大意", [
            Big("无条件积极关注", 540, 600, 110, at=0, sfx="kick", sub="Unconditional Positive Regard", note="概念落版（音乐 drop）"),
            Icon("heart", 540, 920, 130, color=ACC, at=2, enter="fade"),
        ], note="drop 处“无条件积极关注”砸下"),
        Shot(4, "不是“你做到了才好”|而是“你本身就值得”", "罗杰斯原著 · 大意", [
            Custom(lambda c, g, t, d: A.tag_heart(c, 0, 0, 150, "做到了"), x=300, y=760, at=0, sfx="wood_low"),
            Icon("cross", 300, 940, 90, color=K.RED, at=2, sfx="rim"),
            Icon("heart", 760, 760, 180, color=ACC, at=4, sfx="tom", note="没有价签的心"),
        ], note="带价签的心打叉，没有价签的心留下"),
        Shot(4, "接纳这个人|不等于认同他的所有行为", "常见误区", [
            Card("人：接纳", 340, 700, 46, at=0, rot=-2, accent=ACC, sfx="wood_low"),
            Icon("check", 340, 860, 90, color=K.GREEN, at=2, sfx="clap"),
            Card("行为：可以不同意", 720, 760, 42, at=4, rot=2, sfx="wood_low"),
        ], note="人与行为分开"),
        Shot(4, "可以说：我不同意这么做|但我仍然在乎你", "罗杰斯的视角", [
            Fig(320, GROUND, 340, at=0, color=K.OTHER, pose="give", mood="calm"),
            Fig(700, GROUND, 230, at=0, pose="sad", mood="worried", hair="short", face=-1,
                moves=[(4, dict(pose="hug", mood="smile"))]),
            Icon("heart", 520, 640, 90, color=ACC, at=4, sfx="wood_high"),
        ], draw=A.ground, note="大人蹲下说话，孩子露出笑容"),
        Shot(2, "被接纳的人|才敢看见自己", "罗杰斯原著 · 大意", [
            Icon("mirror", 540, 760, 220, color=ACC, at=0, sfx="wood_low"),
        ], text_beat=0, note="镜子"),
        Shot(2, "也才敢|说出真实的感受", "罗杰斯原著 · 大意", [
            Bubble("其实我很害怕", 540, 720, 44, at=0, sfx="wood_high"),
        ], text_beat=0, note="说出真话"),
        Shot(3, "研究：咨询师的积极关注|与疗效正相关", "研究证据", [
            Icon("heart", 540, 700, 200, color=ACC, at=0, sfx="wood_low"),
            Txt("Farber 等，2018：元分析", 540, 880, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="积极关注与疗效的元分析"),
        Shot(3, "批评：完全无条件|现实中很难做到", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=4, sfx="rim"),
        ], note="天平与问号"),
        Shot(2, "它更像一个方向|而不是完美标准", "罗杰斯的视角", [
            Arrow((340, 760), (740, 760), at=0, color=ACC, width=14, sfx="wood_low"),
        ], text_beat=0, note="一支向前的箭头"),
        Shot(2, "试试：先问感受|再谈对错", "小练习", [
            Bubble("吓到了吗？", 540, 720, 46, at=0, sfx="wood_high"),
        ], text_beat=0, note="先问感受"),
        Shot(2, "下一讲：|共情是什么", "下一讲", [
            Custom(lambda c, g, t, d: A.footprints(c, 0, 0, 260, clamp01(t / 1.2)), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 06 讲：共情"),
        end_shot(REFS, "06 共情：共情就是“我懂你”吗？"),
    ]
    return Episode(5, "regard", "无条件积极关注", "接纳一个人，等于认同一切吗？", ACC, shots, refs=REFS,
                   publish_title="接纳一个人，等于认同一切吗？｜罗杰斯心理学05 无条件积极关注",
                   hashtags="#罗杰斯 #心理学 #接纳 #亲子关系",
                   cover_title="接纳一个人|等于【认同一切】吗？", cover_sub="罗杰斯的无条件积极关注", cover_shot=6, cover_t=6.0,
                   notes=["无条件积极关注见罗杰斯 1957 年论文《治疗性人格改变的充分必要条件》，是三项核心条件之一。",
                          "罗杰斯本人也承认，完全无条件的关注是一种理想，咨询师只能在一定程度上做到；片中第 11–12 镜对应这一点。",
                          "Farber、Suzuki 与 Lynch（2018）的元分析显示，咨询师的积极关注与疗效呈正相关。",
                          "打碎杯子与“我不同意这么做，但我仍然在乎你”为片中示例，非罗杰斯原文。"]).build()


def _shards(c, t):
    K.burst(c, 0, -20, t, K.INK3, 20, 90, 8, 5)
    for i, (dx, rot) in enumerate(((-60, 20), (-10, -35), (45, 60), (90, -10))):
        with K.at(c, dx * min(1, t * 4), 0, rot):
            K.poly(c, [(-18, 0), (16, -6), (6, 14)], "#9FB8C8")
