"""09 充分发挥功能的人：好的生活是什么样？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#C08A3A"
GROUND = A.GROUND_Y
REFS = ["Rogers, C. R. (1961). On Becoming a Person, ch. 9 A Therapist's View of the Good Life: The Fully Functioning Person. Houghton Mifflin."]


def build() -> Episode:
    shots = [
        Shot(3, "好的生活|是一直开心吗？", "情境演绎", [
            Fig(400, GROUND, 330, at=0, pose="cheer", mood="happy", hair="short",
                moves=[(6, dict(pose="shrug", mood="worried"))]),
            Icon("question", 760, 600, 120, color=K.INK2, at=6, sfx="rim"),
        ], draw=A.ground, note="欢呼的人停下来，耸肩"),
        Shot(3, "罗杰斯说|好的生活是一个过程", "罗杰斯原著 · 大意", [
            Arrow((240, 760), (840, 760), at=0, color=ACC, width=16, sfx="wood_low"),
            Label("过程", 540, 660, 40, at=4, fill=ACC, sfx="wood_high"),
        ], note="一条向前的长箭头"),
        Shot(2, "他描述过一种人——", "罗杰斯原著", [
            Fig(540, GROUND, 340, at=0, pose="wave", mood="smile", hair="short", sfx="wood_low"),
        ], draw=A.ground, text_beat=0, hits=[(4, "rim", 0.8, "人物定格")], note="挥手的人"),
        Shot(4, "不是终点|而是一个方向", "罗杰斯原著 · 大意", [
            Big("充分发挥功能的人", 540, 600, 104, at=0, sfx="kick", sub="The Fully Functioning Person", note="概念落版（音乐 drop）"),
            Arrow((380, 940), (700, 940), at=2, color=ACC, width=12),
        ], note="drop 处概念砸下"),
        Shot(4, "第一：对经验开放|不急着防御", "罗杰斯原著 · 大意", [
            Icon("door", 720, 860, 300, color=K.GOLD, at=0, sfx="wood_low"),
            Fig(360, GROUND, 330, at=2, pose="wave", mood="open", hair="short", sfx="wood_high"),
        ], draw=A.ground, note="敞开的门"),
        Shot(4, "第二：活在当下|每一刻都是新的", "罗杰斯原著 · 大意", [
            Icon("sun", 540, 640, 200, color=K.GOLD, at=0, sfx="wood_low"),
            Icon("clock", 540, 920, 140, color=ACC, at=4, sfx="wood_high"),
        ], note="太阳与时钟"),
        Shot(4, "第三：信任自己的感受|来做选择", "罗杰斯原著 · 大意", [
            Fig(400, GROUND, 330, at=0, pose="think", mood="calm", hair="short",
                moves=[(4, dict(pose="point", mood="smile"))]),
            Icon("heart", 400, 900, 64, color=K.RED, at=2, sfx="wood_low"),
            Icon("target", 800, 700, 180, color=ACC, at=4, sfx="tom"),
        ], draw=A.ground, note="凭内心感受指向目标"),
        Shot(2, "也更自由|更有创造力", "罗杰斯原著 · 大意", [
            Icon("bulb", 540, 760, 220, color=K.GOLD, at=0, sfx="wood_high"),
        ], text_beat=0, note="灯泡"),
        Shot(2, "这样的人|也会难过、会迷茫", "罗杰斯原著 · 大意", [
            Fig(540, GROUND, 320, at=0, pose="sit_sad", mood="sad", hair="short"),
        ], draw=A.ground, text_beat=0, note="同一个人也会难过"),
        Shot(3, "他说：好的生活|不适合胆小的人", "罗杰斯原著 · 大意", [
            Fig(400, GROUND, 330, at=0, pose="climb", mood="open", hair="short"),
            Icon("flag", 780, 700, 200, color=ACC, at=4, sfx="wood_high"),
        ], draw=A.ground, note="攀登的人与远处的旗子"),
        Shot(3, "它意味着|不断成为自己", "罗杰斯原著 · 大意", [
            Custom(lambda c, g, t, d: A.footprints(c, 0, 0, 280, clamp01(t / 3.0)), x=540, y=760, at=0, sfx="wood_low"),
        ], hits=[(6, "wood_high", 0.6, "脚印延伸")], note="脚印一路向前"),
        Shot(2, "批评：概念模糊|难以测量", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="天平与问号"),
        Shot(2, "试试：允许自己|有一种坏情绪", "小练习", [
            Icon("cloud", 540, 760, 220, color=K.INK3, at=0, sfx="wood_high"),
        ], text_beat=0, note="一朵云"),
        Shot(2, "下一讲：|关系为什么能疗愈", "下一讲", [
            Custom(A.two_chairs, x=540, y=1060, at=0, s=300, gap=320, sfx="wood_high"),
        ], text_beat=0, note="预告第 10 讲：关系的力量"),
        end_shot(REFS, "10 关系的力量：为什么关系本身就能疗愈？"),
    ]
    return Episode(9, "fully", "充分发挥功能的人", "好的生活是什么样？", ACC, shots, refs=REFS,
                   publish_title="好的生活是什么样？｜罗杰斯心理学09 充分发挥功能的人",
                   hashtags="#罗杰斯 #心理学 #好的生活 #个人成长",
                   cover_title="好的生活|是【什么样】？", cover_sub="罗杰斯的充分发挥功能的人", cover_shot=6, cover_t=6.0,
                   notes=["“充分发挥功能的人”见《个人形成论》（1961）第 9 章：对经验日益开放、越来越活在当下、越来越信任自己的机体感受。",
                          "“好的生活是一个过程，而不是一种状态；是一个方向，而不是终点”“好的生活不适合胆小的人”均为该章说法的大意。",
                          "批评者认为这些概念模糊、难以操作化测量，片中第 12 镜列出这一质疑。"]).build()
