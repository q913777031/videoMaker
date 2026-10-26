"""08 目标侵蚀：标准为什么越来越低？（快节奏版：42 镜 × 1 小节）

书中观点（转述）：梅多斯《系统之美》第五章“系统陷阱”之一“目标侵蚀”（drift to low performance）——
绩效标准受过去表现影响，且人们对坏消息的感知更重，于是“表现变差 → 预期降低 → 标准降低 → 努力减少 → 表现更差”
形成一个往下走的增强回路；变化缓慢，不易察觉。书中给出的出路：保持绝对标准，或让标准参照过去最好的表现而非最差的表现。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Spark
from maoxuan.art import notebook
from scarcity.art import checklist, memo

from . import art_d as A
from .common import BOOK, S, episode, outro, pops

ACC = "#9A5B3C"
G = A.GROUND_Y
ME = dict(role="worker")
BOSS = dict(role="boss")
SQUARE_SHOT = 9


def build():
    shots = [
        # ---- 钩子 1–8
        S("年初：每天跑一小时", "灵魂拷问", [
            Fig(330, G, 330, at=0, pose="cheer", mood="happy", **ME),
            Card("每天跑步|一小时", 760, 620, 52, at=1, sfx="pop"),
            Icon("clock", 760, 860, 120, color=K.INK2, at=2, sfx="wood_high"),
        ], draw=A.ground, punch=0.025, flashes=[0]),
        S("忙了一周：半小时", "灵魂拷问", [
            Card("一小时", 540, 560, 60, at=0, enter="none"),
            Icon("cross", 540, 560, 150, color=K.RED, at=1, sfx="rim"),
            Card("半小时", 540, 860, 60, at=2, sfx="pop"),
        ]),
        S("又累了：十分钟", "灵魂拷问", [
            Card("半小时", 540, 560, 60, at=0, enter="none"),
            Icon("cross", 540, 560, 150, color=K.RED, at=1, sfx="rim"),
            Card("十分钟", 540, 860, 60, at=2, sfx="pop"),
        ]),
        S("后来：有空再说", "灵魂拷问", [
            Fig(540, G, 330, at=0, pose="sit_sad", mood="flat", **ME),
            Bubble("有空再说", 760, 520, 50, at=1, enter="pop", sfx="wood_high"),
            Icon("cloud", 300, 520, 140, color=K.INK3, at=2, sfx="wood_low"),
        ], draw=A.ground),
        S("标准一路往下掉", "灵魂拷问", [
            Custom(A.goal_line, x=540, y=780, at=0, enter="fade", b0=0, b1=3, mode="drift"),
        ], hits=[(0, "wood_low", 0.8, "图表"), (1, "tom", 0.8, "目标下降"), (3, "tom", 0.9, "目标再降")]),
        pops("不是你懒 是标准 【在溜走】", "灵魂拷问", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="守住标准 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("系统之美讲过", "系统之美", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《系统之美》|梅多斯", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–15
        S("", "书中观点", [
            Big("目标侵蚀", 540, 700, 190, at=0, sfx="kick", sub="书中观点 · 系统陷阱", sub_size=40, rays=True,
                glow=True, shine=True, spark=True, note="drop：概念落版"),
            Spark(540, 700, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0], shake=[0]),
        S("标准跟着表现走", "书中观点 · 目标侵蚀", [
            Custom(A.goal_line, x=540, y=760, at=0, enter="fade", b0=0, b1=3, mode="drift"),
            Fig(150, G + 60, 220, at=1, pose="point", mood="worried", **ME),
        ], hits=[(0, "shaker", 0.7, "表现线"), (1, "tom", 0.8, "目标跟降"), (3, "tom", 0.8, "目标再降")]),
        S("坏消息记得更牢", "书中观点 · 目标侵蚀", [
            Custom(A.sizes, x=540, y=720, at=0, enter="pop", b=1, sfx="pop"),
            Fig(540, G + 40, 230, at=2, pose="think", mood="worried", **ME, sfx="wood_high"),
        ], hits=[(1, "tom", 0.9, "坏消息变大")]),
        S("于是越定越低", "书中观点 · 目标侵蚀", [
            Custom(A.goal_line, x=540, y=780, at=0, enter="none", b0=-1, b1=2, mode="drift",
                   pts=[0.6, 0.5, 0.52, 0.4, 0.42, 0.3, 0.32, 0.2]),
        ], hits=[(0, "tom", 0.8, "下降"), (1, "tom", 0.8, "下降"), (2, "kick", 0.9, "触底")], shake=[2]),
        pops("目标 降一点 表现 【再降一点】", "书中观点 · 往下的回路", size=110, flash=3),
        S("一圈又一圈", "书中观点 · 往下的回路", [
            Custom(A.loop_diagram, x=540, y=760, at=0, enter="fade", b0=0, step=0.5, loop="R", down=True,
                   names=("表现变差", "预期降低", "标准降低", "努力减少")),
        ], hits=[(0, "pop", 0.7, "节点"), (1, "pop", 0.7, "节点"), (2, "kick", 0.9, "R")]),
        S("往下滚的增强回路", "书中观点 · 往下的回路", [
            Custom(A.loop_diagram, x=540, y=760, at=0, enter="none", b0=-3, step=0.5, loop="R", down=True,
                   names=("表现变差", "预期降低", "标准降低", "努力减少")),
            Icon("cross", 860, 470, 100, color=K.RED, at=1, sfx="rim"),
            Spark(540, 760, at=2, sfx="ding"),
        ]),
        # ---- 团队里 16–24
        S("团队也一样", "团队里也常见", [
            Custom(A.ink_crowd, x=540, y=G, at=0, enter="fade", roles=("worker", "worker_f", "boss", "worker", "worker_f"),
                   spread=760, s=280, sfx="wood_low"),
            Icon("question", 540, 450, 100, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        S("这季没达标", "团队里也常见", [
            Fig(760, G, 340, at=0, pose="point", mood="worried", face=-1, **BOSS),
            Card("目标|没达标", 360, 640, 52, at=1, sfx="pop"),
            Icon("cross", 360, 860, 110, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        S("那下季调低点", "团队里也常见", [
            Fig(760, G, 340, at=0, pose="shrug", mood="smile", face=-1, **BOSS),
            Bubble("调低点吧", 560, 520, 50, at=1, enter="pop", sfx="wood_high"),
            Icon("ladder", 300, 760, 180, color=K.INK2, at=2, sfx="tom"),
        ], draw=A.ground),
        S("大家松了口气", "团队里也常见", [
            Custom(A.ink_crowd, x=540, y=G, at=0, enter="fade", roles=("worker", "worker_f", "worker", "worker_f"),
                   spread=700, s=280),
            Bubble("还好还好", 540, 500, 50, at=1, enter="pop", sfx="pop"),
            Spark(540, 500, at=2, sfx="ding"),
        ], draw=A.ground),
        S("然后又没达标", "团队里也常见", [
            Custom(A.goal_line, x=540, y=780, at=0, enter="fade", b0=0, b1=2, mode="drift",
                   pts=[0.7, 0.62, 0.55, 0.5, 0.42, 0.4, 0.33, 0.3]),
            Icon("cross", 860, 440, 100, color=K.RED, at=3, sfx="rim"),
        ], hits=[(0, "wood_low", 0.8, "图表"), (2, "tom", 0.8, "又降")]),
        S("目标再调低", "团队里也常见", [
            Fig(760, G, 340, at=0, pose="shrug", mood="flat", face=-1, **BOSS),
            Card("下季目标", 360, 600, 50, at=0, sfx="pop"),
            Icon("cross", 360, 600, 120, color=K.RED, at=1, sfx="rim"),
            Card("再低一点", 360, 840, 50, at=2, sfx="tom"),
        ], draw=A.ground),
        S("没人觉得出了事", "团队里也常见", [
            Custom(A.ink_crowd, x=540, y=G, at=0, enter="fade", roles=("worker_f", "boss", "worker"), spread=560, s=290),
            Icon("eye", 540, 470, 120, color=K.INK3, at=1, sfx="wood_high"),
            Icon("cross", 540, 470, 90, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        S("像温水煮青蛙", "常见比喻", [
            Custom(A.frog, x=540, y=760, at=0, enter="pop", b0=0, b1=3, sfx="pop"),
        ], hits=[(1, "shaker", 0.7, "加热"), (3, "shaker", 0.8, "加热")]),
        S("变化慢到看不见", "常见比喻", [
            Custom(A.frog, x=540, y=760, at=0, enter="none", b0=-3, b1=3),
            Bubble("还挺暖", 760, 470, 46, at=1, enter="pop", sfx="pop"),
            Icon("question", 300, 470, 100, color=K.RED, at=3, sfx="rim"),
        ]),
        pops("慢慢变差 最 【难察觉】", "一句话", size=140, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 二次钩子 · 出路 26–31
        S("那怎么破？", "书中给的出路", [
            Fig(540, G, 340, at=0, pose="think", mood="worried", **ME),
            Icon("key", 800, 500, 130, color=K.GOLD, at=2, sfx="ding"), Spark(800, 500, at=2),
        ], draw=A.ground, punch=0.025, flashes=[2]),
        S("一：守住绝对标准", "书中观点 · 出路", [
            Custom(A.goal_line, x=540, y=780, at=0, enter="fade", b0=0, b1=3, mode="fixed", goal=0.82,
                   goal_label="绝对标准", pts=[0.7, 0.6, 0.66, 0.55, 0.7, 0.68, 0.76, 0.8]),
        ], hits=[(0, "wood_low", 0.8, "图表"), (1, "wood_high", 0.7, "标准不动"), (3, "ding", 0.9, "追上来")]),
        S("不管上周怎样", "书中观点 · 出路", [
            Custom(memo, x=540, y=760, at=0, enter="pop", title="底线不变", items=("每周跑三次", "每次三十分钟"),
                   b0=1, sfx="wood_low"),
            Icon("shield", 860, 480, 120, color=ACC, at=3, sfx="ding"),
        ], hits=[(1, "pop", 0.8, "条目"), (2, "pop", 0.8, "条目")]),
        S("二：向最好看齐", "书中观点 · 出路", [
            Custom(A.goal_line, x=540, y=780, at=0, enter="fade", b0=0, b1=3, mode="ratchet", goal_label="最好表现"),
        ], hits=[(0, "wood_low", 0.8, "图表"), (1, "ding", 0.7, "目标上调"), (3, "ding", 0.9, "目标上调")]),
        S("好消息也记一笔", "书中观点 · 出路", [
            Custom(A.sizes, x=540, y=720, at=0, enter="pop", even=True, sfx="pop"),
            Fig(540, G + 40, 230, at=1, pose="cheer", mood="happy", **ME, sfx="ding"),
            Spark(310, 720, at=2, sfx="ding"),
        ]),
        S("标准只升不降", "书中观点 · 出路", [
            Icon("ladder", 540, 760, 300, color=ACC, at=0, sfx="wood_low"),
            Fig(760, G, 260, at=1, pose="climb", mood="happy", **ME, sfx="pop"),
            Icon("flag", 540, 470, 120, color=K.GOLD, at=3, sfx="ding"),
        ], draw=A.ground),
        # ---- 当下 32–36
        S("今天：一本变一页", "当下 · 现象", [
            Icon("book", 320, 700, 220, color=ACC, at=0, sfx="pop"),
            Icon("cross", 320, 700, 160, color=K.RED, at=1, sfx="rim"),
            Card("一页", 760, 700, 70, at=2, sfx="tom"),
        ]),
        S("交稿：能交就行", "当下 · 现象", [
            Fig(400, G, 330, at=0, pose="shrug", mood="flat", **ME),
            Bubble("凑合吧", 680, 520, 50, at=1, enter="pop", sfx="wood_high"),
            Icon("check", 760, 760, 120, color=K.INK3, at=2, sfx="pop"),
        ], draw=A.ground),
        S("一年后回头看", "当下 · 现象", [
            Custom(A.goal_line, x=540, y=780, at=0, enter="fade", b0=-3, b1=0, mode="drift"),
            Fig(150, G + 60, 220, at=1, pose="cover", mood="surprised", **ME, sfx="tom"),
        ], hits=[(0, "wood_low", 0.8, "回头看"), (2, "kick", 0.9, "吓一跳")], shake=[2]),
        pops("标准 是你 【定的】", "一句话", size=150, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("把底线写下来", "落到自己", [
            Custom(notebook, x=540, y=780, at=0, enter="pop", b0=0, step=1, lines=("底线：", "最好：", "本周：")),
        ], hits=[(0, "shaker", 0.7, "写"), (1, "shaker", 0.7, "写"), (2, "ding", 0.9, "写完")]),
        # ---- 4 招 37–41
        S("书里给了出路", "守住标准 4 招", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="守住标准 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 写下绝对标准", "守住标准 4 招 · 小建议", [
            Card("底线|不随心情变", 540, 640, 52, at=0, sfx="pop"),
            Icon("shield", 540, 900, 150, color=ACC, at=2, sfx="ding"),
        ]),
        S("② 和最好的自己比", "守住标准 4 招 · 小建议", [
            Fig(330, G, 300, at=0, pose="stand", mood="calm", **ME),
            Fig(750, G, 300, at=1, pose="cheer", mood="happy", **ME, face=-1, sfx="pop"),
            Label("最好的那次", 750, 470, 40, at=2, sfx="ding"),
        ], draw=A.ground),
        S("③ 好消息也记一笔", "守住标准 4 招 · 小建议", [
            Custom(checklist, x=540, y=780, at=0, enter="pop", w=620, title="本周做到的",
                   items=[("早起", True), ("跑步", True), ("读书", True)], b0=1, step=1),
        ], hits=[(0, "wood_high", 0.8, "清单"), (1, "ding", 0.7, "勾"), (2, "ding", 0.7, "勾"), (3, "ding", 0.8, "勾")]),
        S("④ 定期回看底线", "守住标准 4 招 · 小建议", [
            Icon("clock", 330, 720, 200, color=K.INK2, at=0, sfx="pop"),
            Custom(A.magnifier, x=760, y=720, at=1, enter="pop", r=120, sfx="wood_high"),
            Icon("check", 760, 720, 90, color=K.GREEN, at=2, sfx="ding"),
        ]),
        # ---- 片尾 42
        outro("你的哪个标准在悄悄降？", "为什么越熬夜越离不开咖啡？", "守住标准，慢慢变好"),
    ]
    return episode(8, "drift", "目标侵蚀", "标准为什么越来越低？", ACC, shots,
                   [f"{BOOK}第五章 · 系统陷阱：目标侵蚀", "Donella H. Meadows, Thinking in Systems: A Primer (2008)"],
                   "标准一降再降|是【系统陷阱】", 8,
                   ["书中观点为转述：Donella H. Meadows, Thinking in Systems: A Primer (2008)，第五章 System Traps 之 "
                    "Drift to Low Performance；中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。上屏均为转述，不是逐字引文。",
                    "回路节点（表现变差、预期降低、标准降低、努力减少）为对书中机制的通俗化转述；出路“保持绝对标准”“参照最好表现”"
                    "为书中给出的两条出路的转述。",
                    "“温水煮青蛙”为常见比喻；跑步、读书、团队目标等为示意情境，图表与数字均为示意。"],
                   tags="#目标管理 #自律")
