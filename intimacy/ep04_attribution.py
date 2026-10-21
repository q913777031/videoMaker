"""04 归因：他迟到一次，你就觉得他不在乎你？"""

from adler import kit as K
from adler.core import Card, Custom, Fig, Icon, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#C8553D"
G = A.GROUND_Y
REFS = [BOOK, "Bradbury & Fincham (1990). Attributions in marriage: Review and critique. Psych Bull."]


def build():
    shots = [
        hook("他 迟到 一次|你 就 觉得 他 【不在乎你】？", 88),
        loop("问题不在迟到|在你怎么解释它", hair="long", color=A.HER),
        Shot(4, "约好七点见|他晚到了二十分钟", "情境演绎", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="他",
                   msgs=[(1, "路上堵车了"), (4, "马上到"), (7, "真的对不起"), (10, "还有五分钟")]),
        ], hits=[(1, "wood_high", 0.8, "消息"), (4, "wood_high", 0.8, "消息"), (7, "wood_high", 0.8, "消息"),
                 (10, "rim", 0.9, "消息")], note="他的消息一条条弹出"),
        drop("归因", "Attribution", "同一件事|不同的【解释】", 220),
        Shot(4, "“他就是不在乎我”|还是“今天路上太堵”？", "原书 · 大意", [
            Card("他就是|不在乎我", 300, 760, 50, at=0, rot=-4, fill=K.RED, color=K.PAPER, sfx="rim"),
            Card("今天路上|太堵了", 780, 760, 50, at=3, rot=3, fill=K.GREEN, color=K.PAPER, sfx="wood_high"),
        ], note="两种解释"),
        line("怪 人品|还是 怪 【情境】？", 104),
        Shot(4, "研究发现：不幸福的伴侣|爱把错怪到对方人品上", "研究证据 · Bradbury & Fincham 1990", [
            Fig(360, G, 300, at=0, pose="point", mood="angry", hair="long", color=A.HER),
            Fig(740, G, 300, at=0, pose="sad", mood="sad", hair="short", face=-1),
            Icon("cross", 740, 560, 100, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground, research=True, flashes=[2], note="二次钩子：指责"),
        Shot(4, "坏事归给“他就这样”|好事归给“碰巧而已”", "研究证据 · Bradbury & Fincham 1990", [
            Card("坏事 → 性格", 540, 640, 52, at=0, fill=K.RED, color=K.PAPER, sfx="wood_low"),
            Card("好事 → 运气", 540, 860, 52, at=2, fill=K.INK2, color=K.PAPER, sfx="wood_low"),
        ], research=True, note="维持痛苦的归因"),
        Shot(4, "而幸福的伴侣|正好反过来想", "研究证据 · Bradbury & Fincham 1990", [
            Card("好事 → 性格", 540, 640, 52, at=0, fill=K.GREEN, color=K.PAPER, sfx="ding"),
            Card("坏事 → 情境", 540, 860, 52, at=2, fill=ACC, color=K.PAPER, sfx="wood_low"),
            Spark(540, 640, at=0),
        ], research=True, note="增进关系的归因"),
        slam("解释", "你怎么解释|关系就怎么走"),
        doubt("也可能是关系先变差|解释才变得负面"),
        tip("试试：生气前|先想一个情境原因", hair="long", color=A.HER),
        end_shot(REFS, "05 四骑士：为什么一吵架就越说越僵"),
    ]
    return episode(4, "attribution", "归因", "他迟到一次，你就觉得他不在乎你？", ACC, shots, REFS,
                   "他迟到一次|你就觉得他【不在乎你】？",
                   ["“维持痛苦型归因”与“增进关系型归因”为《亲密关系》第 4 章内容。",
                    "Bradbury & Fincham (1990) 综述：不满意的伴侣倾向把对方的负面行为归于稳定的性格原因、把正面行为归于偶然；纵向研究提示两者可能互为因果。"])
