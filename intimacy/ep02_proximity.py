"""02 接近性：为什么总会喜欢上身边的人？"""

from adler import kit as K
from adler.core import Bubble, Counter, Custom, Fig, Icon, Label, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#B5487A"
G = A.GROUND_Y
REFS = [BOOK, "Festinger, Schachter & Back (1950). Social Pressures in Informal Groups.",
        "Moreland & Beach (1992). Exposure effects in the classroom. JESP."]


def build():
    shots = [
        hook("为什么 总会 喜欢上|【身边的人】？", 100),
        loop("不是缘分|是“见得多”", pose="think", mood="open"),
        Shot(4, "同一个工位、同一班地铁|天天见着见着就心动了", "情境演绎", [
            Fig(340, G, 310, at=0, mood="smile", hair="short"),
            Fig(740, G, 300, at=2, mood="smile", hair="long", color=A.HER, face=-1, sfx="wood_low"),
            Icon("heart", 540, 560, 110, color=K.RED, at=5, sfx="ding"),
            Spark(540, 560, at=5),
        ], draw=A.ground, note="两人相遇，爱心弹出"),
        drop("接近性", "Proximity", "离得近、见得多|就更容易【喜欢】", 200),
        Shot(4, "1950年代一项宿舍研究：|朋友多半是邻居", "研究证据 · Festinger 等 1950", [
            Custom(A.building, x=540, y=780, at=0, enter="pop", friends=[(1, 1), (1, 2), (1, 3)], b0=2, step=2),
        ], hits=[(2, "wood_high", 0.8, "窗亮"), (4, "wood_high", 0.8, "窗亮"), (6, "ding", 0.9, "成了朋友")],
            research=True, note="相邻窗户依次亮起"),
        line("见得 越多|越 【顺眼】", 110),
        Shot(4, "研究者请4位女生|在课堂上出现不同次数", "研究证据 · Moreland & Beach 1992", [
            Counter(0, 4, 540, 660, 220, at=0, land=4, sub="位女生（从不与同学交谈）"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子"),
        Shot(4, "出现0、5、10、15次|来得越多，被评越有魅力", "研究证据 · Moreland & Beach 1992", [
            Label("0 次", 210, 760, 40, at=0, fill=K.INK3, sfx="wood_low"),
            Label("5 次", 420, 760, 40, at=1, fill=K.INK2, sfx="wood_low"),
            Label("10 次", 650, 760, 40, at=2, fill=ACC, sfx="wood_low"),
            Label("15 次", 880, 760, 46, at=3, fill=K.RED, sfx="ding"),
            Spark(880, 760, at=3),
        ], research=True, note="出现次数越多评价越高"),
        Shot(4, "这叫“单纯曝光效应”|熟悉本身就会带来好感", "原书 · 大意", [
            Icon("eye", 540, 720, 220, color=ACC, at=0, sfx="wood_low"),
            Bubble("眼熟！", 760, 540, 46, at=2, sfx="wood_high"),
        ], note="眼熟"),
        slam("熟悉", "熟悉|就是好感的开始"),
        doubt("但第一印象很差时|见得越多反而越讨厌", tag="边界"),
        tip("试试：想认识谁|先让对方常看到你"),
        end_shot(REFS, "03 相似性：互补的人真的更合适吗"),
    ]
    return episode(2, "proximity", "接近性", "为什么总会喜欢上身边的人？", ACC, shots, REFS,
                   "为什么总会喜欢上|【身边的人】？",
                   ["接近性与单纯曝光效应为《亲密关系》第 3 章内容。",
                    "Festinger 等 (1950) 的大学宿舍研究：住得近的人更容易成为朋友。Moreland & Beach (1992)：4 位女助手分别出现 0、5、10、15 次课，出现越多被评价越有吸引力。",
                    "曝光效应有边界：初始印象负面时，接触增多可能加深反感。"])
