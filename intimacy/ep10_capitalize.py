"""10 积极回应：对方报喜时，你只回了句“哦”？"""

from adler import kit as K
from adler.core import Custom, Fig, Icon, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#3F8F6B"
G = A.GROUND_Y
REFS = [BOOK, "Gable, Reis, Impett & Asher (2004). What do you do when things go right? JPSP."]


def build():
    shots = [
        hook("对方 升职了|你 只回了句 【“哦”】？", 100),
        loop("感情好不好|看你怎么接住好消息", icon="bulb", pose="think", mood="open"),
        Shot(4, "她兴冲冲地发来消息|你正忙，只回了一个字", "情境演绎", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="她",
                   msgs=[(1, "我升职了！！"), (5, "哦"), (9, "……")]),
        ], hits=[(1, "ding", 0.9, "好消息"), (5, "rim", 0.8, "哦"), (9, "wood_low", 0.8, "沉默")], note="冷淡的回复"),
        drop("积极回应", "Active-Constructive", "热情地接住|对方的【好消息】", 180),
        Shot(4, "回应好消息|有四种方式", "原书 · 盖布尔的研究", [
            Custom(A.grid4, x=540, y=780, at=0, enter="none", b0=0, step=2, hi=0,
                   cells=[("积极建设", "太棒了！快说说", K.GREEN), ("消极建设", "嗯，不错", K.INK3),
                          ("积极破坏", "那以后更忙了吧", K.RED), ("消极破坏", "哦。吃啥？", K.INK2)]),
        ], hits=[(0, "ding", 0.9, "积极建设"), (2, "wood_low", 0.7, "消极建设"), (4, "rim", 0.8, "积极破坏"),
                 (6, "rim", 0.8, "消极破坏")], note="四格回应"),
        line("你 的 回应|决定 了 【亲密】", 104),
        Shot(4, "研究发现：分享好消息|本身就让人更快乐", "研究证据 · Gable 等 2004", [
            Fig(400, G, 310, at=0, pose="cheer", mood="happy", hair="long", color=A.HER),
            Icon("sun", 700, 600, 160, color=K.GOLD, at=2, sfx="ding"),
            Spark(700, 600, at=2),
        ], draw=A.ground, research=True, flashes=[2], note="二次钩子：分享好消息"),
        Shot(4, "对方热情回应时|关系满意度和信任更高", "研究证据 · Gable 等 2004", [
            Fig(400, G, 310, at=0, pose="hug", mood="happy", hair="short"),
            Fig(660, G, 300, at=0, pose="hug", mood="happy", hair="long", color=A.HER, face=-1),
            Icon("heart", 530, 560, 120, color=K.RED, at=2, sfx="ding"),
        ], draw=A.ground, research=True, note="拥抱"),
        Shot(4, "敷衍和泼冷水|都在悄悄消耗感情", "原书 · 大意", [
            Icon("heart", 540, 720, 200, color=K.INK3, at=0, sfx="wood_low"),
            Icon("cross", 680, 600, 100, color=K.RED, at=2, sfx="rim"),
        ], note="褪色的心"),
        slam("接住", "接住好消息|就是接住对方"),
        doubt("研究多靠自我报告|效果因人而异"),
        tip("十讲走完|今晚热情回应一次对方", hair="long", color=A.HER),
        end_shot(REFS, None),
    ]
    return episode(10, "capitalize", "积极回应", "对方报喜时，你只回了句“哦”？", ACC, shots, REFS,
                   "对方报喜时|你只回了句【“哦”】？",
                   ["关系维护与“积极建设性回应”（capitalization）为《亲密关系》第 14 章内容。",
                    "Gable 等 (2004)：分享好消息与当日积极情绪、生活满意度相关；被热情回应者报告更高的关系质量。数据多为自我报告。"])
