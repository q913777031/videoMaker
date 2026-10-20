"""10 关系的力量：为什么关系本身就能疗愈？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#7A5F4A"
GROUND = A.GROUND_Y
REFS = ["Rogers, C. R. (1957). The necessary and sufficient conditions of therapeutic personality change. J. Consult. Psychol., 21(2).",
        "Norcross, J. C., & Lambert, M. J. (2018). Psychotherapy relationships that work III. Psychotherapy, 55(4).",
        "Flückiger, C., et al. (2018). The alliance in adult psychotherapy. Psychotherapy, 55(4)."]


def build() -> Episode:
    shots = [
        Shot(3, "为什么有时候|被听见，就好了一半？", "情境演绎", [
            Custom(A.two_chairs, x=540, y=GROUND, at=0, right_mood="sad"),
            Icon("heart", 640, 560, 90, color=K.RED, at=6, sfx="clap", note="心里一松"),
        ], draw=A.ground, note="两把椅子，来访者心里一松"),
        Shot(3, "1957 年罗杰斯提出|治疗改变的几个条件", "罗杰斯原著", [
            Icon("book", 540, 700, 220, color=ACC, at=0, sfx="wood_low"),
            Txt("《治疗性人格改变的充分必要条件》", 540, 880, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="1957 年论文"),
        Shot(2, "其中核心的三条|合起来就是——", "罗杰斯原著 · 大意", [
            Card("共情", 540, 600, 44, at=0, rot=-2, accent="#4F7F9A", sfx="wood_low"),
            Card("无条件积极关注", 540, 760, 44, at=1, rot=2, accent="#B05070", sfx="wood_low", gain=0.85),
            Card("真诚一致", 540, 920, 44, at=2, rot=-1, accent="#6A5A8A", sfx="wood_low", gain=0.75),
        ], text_beat=0, hits=[(4, "rim", 0.8, "三张卡定格")], note="三项核心条件"),
        Shot(4, "比方法更重要的|是这段关系本身", "罗杰斯原著 · 大意", [
            Big("关系的力量", 540, 580, 140, at=0, sfx="kick", sub="The Therapeutic Relationship", note="概念落版（音乐 drop）"),
            Custom(A.two_chairs, x=540, y=1100, at=2, enter="fade", s=240, gap=260),
        ], note="drop 处“关系的力量”砸下"),
        Shot(4, "他认为：条件具备|改变就会发生", "罗杰斯原著 · 大意", [
            Icon("check", 360, 760, 140, color=K.GREEN, at=0, sfx="wood_low"),
            Arrow((460, 760), (640, 760), at=2, color=ACC, width=12, sfx="rim"),
            Icon("sprout", 760, 760, 180, color=K.GREEN, at=4, sfx="wood_high"),
        ], note="条件 → 改变"),
        Shot(4, "后来的研究发现：关系很重要|但不是全部", "研究证据", [
            Icon("scale", 540, 720, 240, color=ACC, at=0, sfx="wood_low"),
            Txt("Norcross & Lambert，2018", 540, 920, 30, at=4, font="sans_medium", color=K.INK2),
        ], note="天平：关系与其他因素"),
        Shot(4, "咨询联盟|是疗效的稳定预测因素", "研究证据", [
            Custom(A.two_chairs, x=540, y=GROUND, at=0, enter="none"),
            Txt("Flückiger 等，2018：元分析", 540, 1220, 30, at=2, font="sans_medium", color=K.INK2, sfx="wood_high"),
        ], draw=A.ground, note="咨询联盟的元分析"),
        Shot(2, "关系的力量|不只在咨询室", "当代理解", [
            Icon("house", 540, 760, 220, color=ACC, at=0, sfx="wood_low"),
        ], text_beat=0, note="房子"),
        Shot(2, "也在家庭、学校|和职场里", "当代理解", [
            Icon("house", 300, 760, 150, color=ACC, at=0, sfx="wood_low"),
            Icon("book", 540, 760, 150, color=K.GOLD, at=1, sfx="wood_low", gain=0.85),
            Icon("brief", 780, 760, 150, color=K.DARK, at=2, sfx="wood_low", gain=0.75),
        ], text_beat=0, note="家、学校、职场"),
        Shot(3, "晚年他到冲突地区|主持对话小组", "罗杰斯自述", [
            Fig(240, GROUND, 280, at=0, color=K.OTHER, mood="angry"),
            Fig(840, GROUND, 280, at=0, color=K.OTHER3, mood="angry", face=-1),
            Fig(540, GROUND, 300, at=2, pose="give", mood="calm", hair="short", color="#6A5A4A", sfx="wood_low"),
        ], draw=A.ground, hits=[(6, "wood_high", 0.6, "双方转向中间")], note="两方之间站着一位倾听者"),
        Shot(3, "1987 年|他被提名诺贝尔和平奖", "当代理解", [
            Icon("trophy", 540, 740, 220, color=K.GOLD, at=0, sfx="wood_low"),
        ], hits=[(4, "rim", 0.7, "奖杯定格")], note="奖杯"),
        Shot(2, "批评：单靠关系|对重症往往不够", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="天平与问号"),
        Shot(2, "试试：对一个人|多一点耐心和真诚", "小练习", [
            Icon("heart", 540, 760, 200, color=K.RED, at=0, sfx="wood_high"),
        ], text_beat=0, note="心"),
        Shot(2, "十讲走完|愿你被理解，也去理解", "罗杰斯的视角", [
            Fig(400, GROUND, 300, at=0, pose="hug", mood="happy", hair="short"),
            Fig(660, GROUND, 300, at=1, pose="hug", mood="happy", color=K.OTHER2, hair="bun", face=-1),
        ], draw=A.ground, text_beat=0, hits=[(6, "cymbal", 0.5, "系列收尾")], note="系列收尾：两人相拥"),
        end_shot(REFS, None),
    ]
    return Episode(10, "relationship", "关系的力量", "为什么关系本身就能疗愈？", ACC, shots, refs=REFS,
                   publish_title="为什么关系本身就能疗愈？｜罗杰斯心理学10 关系的力量",
                   hashtags="#罗杰斯 #心理学 #心理咨询 #关系",
                   cover_title="为什么【关系】|本身就能疗愈？", cover_sub="罗杰斯的治疗性关系", cover_shot=0, cover_t=6.0,
                   notes=["罗杰斯 1957 年提出治疗性人格改变的六项“充分必要条件”，其中咨询师方面的核心是共情、无条件积极关注与真诚一致。",
                          "后续研究（Norcross & Lambert, 2018）认为治疗关系对疗效有实质贡献，但“充分”一说未获支持；"
                          "Flückiger 等（2018）的元分析显示咨询联盟与疗效稳定相关。",
                          "罗杰斯晚年在北爱尔兰、南非等地主持跨冲突群体的对话工作坊；1987 年他被提名诺贝尔和平奖，同年去世。"]).build()
