"""01 系统是什么：换了一批人，公司为什么还是老样子？（快节奏版：42 镜 × 1 小节）

书中观点（转述，Meadows, Thinking in Systems 第一章）：系统由要素、连接、功能或目标三部分组成；系统大于各部分之和；
开篇弹簧玩具的演示——手一松弹簧自己上下弹，行为来自弹簧自身的结构；三部分里改变要素通常影响最小，改变连接与目标影响最大，
而目标是最不显眼、却最能决定系统行为的部分；系统的目标要从它的行为推断，而不是看口号。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Spark

from . import art as A
from .common import BOOK, S, episode, outro, pops

ACC = A.TEAL
G = A.GROUND_Y
ME = dict(role="worker")
BOSS = dict(role="boss")
SQUARE_SHOT = 34


def build():
    shots = [
        # ---- 钩子 1–8
        S("新部门来了新领导", "灵魂拷问", [
            Fig(760, G, 340, at=0, pose="wave", mood="smile", face=-1, **BOSS, sfx="wood_low"),
            Fig(230, G, 300, at=1, pose="stand", mood="calm", **ME, sfx="pop"),
            Bubble("咱们【重新出发】！", 640, 520, 44, at=2, enter="pop", sfx="pop"),
        ], draw=A.ground, punch=0.025, flashes=[0]),
        S("团队也换了一半", "灵魂拷问", [
            Custom(A.desks, x=540, y=760, at=0, enter="fade", swap=1, step=0.5, mood="smile"),
        ], hits=[(0, "wood_low", 0.8, "工位"), (1, "pop", 0.8, "换人"), (2, "pop", 0.8, "换人")]),
        S("大家干劲十足", "灵魂拷问", [
            Fig(300, G, 300, at=0, pose="cheer", mood="happy", **ME, sfx="pop"),
            Fig(540, G, 310, at=1, pose="cheer", mood="happy", role="worker_f", sfx="pop"),
            Fig(780, G, 300, at=2, pose="fist", mood="happy", role="worker", color="#C98B5A", face=-1, sfx="pop"),
            Spark(540, 520, at=3, sfx="ding"),
        ], draw=A.ground),
        S("三个月后", "灵魂拷问", [
            Icon("clock", 540, 700, 260, color=K.INK2, at=0, sfx="wood_low"),
            Label("三个月后", 540, 960, 50, at=2, sfx="rim"),
        ]),
        S("还是加班，还是扯皮", "灵魂拷问", [
            Custom(A.desks, x=540, y=760, at=0, enter="fade", mood="sad", old=("#C98B5A", "#7E6FA6", "#5E9A8A")),
            Icon("sun", 900, 430, 90, color=K.INK2, at=0, enter="none"),
            Bubble("不是我的事", 300, 450, 40, at=1, enter="pop", sfx="wood_high"),
            Bubble("等领导定", 760, 470, 40, at=2, enter="pop", sfx="wood_high"),
        ], shake=[2]),
        pops("换了 人 没换 【系统】", "灵魂拷问", size=140, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="看系统 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("有本书讲透了", "系统之美", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《系统之美》|德内拉·梅多斯", 540, 940, 48, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–12
        S("", "书中观点", [
            Big("不是人的问题", 540, 660, 130, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：观点落版"),
            Big("是结构", 540, 880, 170, at=1, sfx="kick", sub="书中观点", sub_size=40, shine=True, note="下半句"),
            Spark(540, 880, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        S("书一开头，拿出弹簧", "书中例子 · 弹簧玩具", [
            Custom(A.slinky, x=540, y=760, at=0, enter="pop", sfx="pop"),
            Icon("question", 820, 460, 90, color=K.RED, at=2, sfx="wood_high"),
        ]),
        S("手一松，它自己弹", "书中例子 · 弹簧玩具", [
            Custom(A.slinky, x=540, y=760, at=0, enter="none", drop=1),
        ], hits=[(1, "kick", 0.9, "松手"), (2, "tom", 0.7, "回弹"), (3, "tom", 0.6, "回弹")], shake=[1]),
        pops("行为 藏在 【结构】 里", "书中观点", size=140, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 三要素 13–20
        S("系统由三样组成", "书中观点 · 系统是什么", [
            Custom(A.system_map, x=540, y=780, at=0, enter="fade", b0=0, b1=1.5, b2=2.5),
        ], hits=[(0, "pop", 0.8, "要素"), (1, "pop", 0.8, "要素"), (2, "wood_high", 0.8, "连接"), (3, "ding", 0.9, "目标")]),
        S("一是要素", "书中观点 · 要素", [
            Custom(A.system_map, x=540, y=760, at=0, enter="none", b0=0, step=0.5, b1=9, b2=9),
            Fig(540, G + 40, 240, at=2, pose="point", mood="smile", **ME, sfx="pop"),
        ], hits=[(0, "pop", 0.8, "员工"), (1, "pop", 0.8, "电脑")]),
        S("二是连接", "书中观点 · 连接", [
            Custom(A.system_map, x=540, y=760, at=0, enter="none", b0=-9, b1=0, b2=9, conn_label="流程 · 汇报 · 信息"),
        ], hits=[(0, "wood_high", 0.8, "画线"), (1, "pop", 0.8, "流程"), (2, "pop", 0.8, "汇报")]),
        S("三是目标", "书中观点 · 目标", [
            Custom(A.system_map, x=540, y=760, at=0, enter="none", b0=-9, b1=-9, b2=1),
            Spark(540, 760, at=1, sfx="ding"),
        ], hits=[(0, "wood_low", 0.7, "整体"), (2, "pop", 0.8, "目标")], flashes=[1]),
        S("比如一支球队", "示意 · 球队", [
            Custom(A.system_map, x=540, y=760, at=0, enter="fade", b0=0, step=0.25, b1=1.5, b2=2.5, goal="赢球",
                   nodes=[("前锋", -280, -180), ("中场", 260, -200), ("后卫", -300, 180), ("门将", 280, 170)]),
        ], hits=[(0, "pop", 0.8, "球员"), (1, "pop", 0.8, "球员"), (2, "wood_high", 0.8, "配合"), (3, "ding", 0.9, "赢球")]),
        S("球员就是要素", "示意 · 球队", [
            Fig(270, G, 300, at=0, pose="wave", mood="happy", role="worker", color="#C0502A", sfx="pop"),
            Fig(540, G, 310, at=1, pose="cheer", mood="happy", role="worker", color="#C0502A", sfx="pop"),
            Fig(810, G, 300, at=2, pose="fist", mood="happy", role="worker", color="#C0502A", face=-1, sfx="pop"),
            Label("要素", 540, 470, 50, at=3, sfx="ding"),
        ], draw=A.ground),
        S("传球配合是连接", "示意 · 球队", [
            Fig(220, G, 290, at=0, pose="give", mood="smile", role="worker", color="#C0502A"),
            Fig(860, G, 290, at=0, pose="reach", mood="happy", role="worker", color="#C0502A", face=-1),
        ], draw=A.ground, over=lambda g: _ball(g), hits=[(0, "wood_high", 0.8, "传"), (2, "pop", 0.9, "接"), (3, "ding", 0.7, "连接")]),
        S("赢球是目标", "示意 · 球队", [
            Icon("trophy", 540, 700, 260, color=K.GOLD, at=0, sfx="kick"), Spark(540, 700, at=0),
            Label("目标", 540, 980, 50, at=2, sfx="ding"),
        ], flashes=[0]),
        # ---- 换哪样影响最大 21–29
        S("换掉哪样，影响最大？", "二次钩子", [
            Card("换要素", 230, 760, 48, at=0, sfx="pop"),
            Card("改连接", 540, 760, 48, at=1, sfx="pop"),
            Card("改目标", 850, 760, 48, at=2, sfx="pop"),
            Icon("question", 540, 500, 120, color=K.RED, at=3, sfx="rim"),
        ], flashes=[3]),
        S("全换球员，队还在", "书中观点 · 换要素", [
            Custom(A.system_map, x=540, y=760, at=0, enter="none", b0=-9, b1=-9, b2=-9, swap=1, goal="赢球",
                   nodes=[("前锋", -280, -180), ("中场", 260, -200), ("后卫", -300, 180), ("门将", 280, 170)]),
            Label("影响最小", 540, 1130, 44, at=3, sfx="ding", fill=K.INK2),
        ], hits=[(1, "pop", 0.8, "换人")]),
        S("改了规则，打法全变", "书中观点 · 改连接", [
            Custom(A.system_map, x=540, y=760, at=0, enter="none", b0=-9, b1=-9, b2=-9, rewire=1, goal="赢球",
                   nodes=[("前锋", -280, -180), ("中场", 260, -200), ("后卫", -300, 180), ("门将", 280, 170)]),
            Label("影响很大", 540, 1130, 44, at=3, sfx="ding", fill=K.GOLD),
        ], hits=[(1, "wood_high", 0.9, "改线")], shake=[1]),
        S("目标改成输球？", "书中观点 · 改目标", [
            Custom(A.system_map, x=540, y=760, at=0, enter="none", b0=-9, b1=-9, b2=-9, flip=1, goal="赢球",
                   nodes=[("前锋", -280, -180), ("中场", 260, -200), ("后卫", -300, 180), ("门将", 280, 170)]),
            Label("整个系统都变了", 540, 1130, 44, at=2, sfx="kick", fill=K.RED),
        ], hits=[(1, "rim", 1.0, "翻转")], shake=[2], flashes=[2]),
        pops("目标 最不显眼 却最 【关键】", "书中观点", size=130, flash=3, extra=[Rays(540, 780, 620, at=3, alpha=0.2)]),
        S("看行为，不看口号", "书中观点 · 从行为看目标", [
            Icon("eye", 300, 740, 200, color=ACC, at=0, sfx="pop"),
            Icon("megaphone", 780, 740, 200, color=K.INK3, at=1, sfx="pop"),
            Icon("check", 300, 520, 90, color=K.GREEN, at=2, sfx="ding"),
            Icon("cross", 780, 520, 90, color=K.RED, at=3, sfx="rim"),
        ]),
        S("墙上写着客户第一", "示意 · 口号", [
            Custom(A.banner, x=540, y=760, at=0, enter="none", b0=0, text="客户第一"),
            Fig(540, G, 300, at=1, pose="point", mood="smile", **BOSS, sfx="pop"),
        ], draw=A.ground, hits=[(0, "wood_low", 0.8, "横幅")]),
        S("考核只看业绩", "示意 · 行为", [
            Card("月度考核|业绩 · 业绩 · 业绩", 540, 700, 50, at=0, sfx="pop"),
            Icon("cross", 540, 960, 120, color=K.RED, at=2, sfx="rim"),
            Label("客户满意？没人问", 540, 1120, 40, at=3, sfx="wood_high", fill=K.INK2),
        ]),
        S("真目标就是业绩", "书中观点 · 从行为看目标", [
            Big("业绩", 540, 740, 240, at=0, sfx="kick", glow=True, rays=True),
            Spark(540, 740, at=2, sfx="ding"),
        ], shake=[0]),
        # ---- 当下 30–35
        S("今天：新领导上任", "当下 · 现象", [
            Fig(540, G, 340, at=0, pose="proud", mood="happy", **BOSS, sfx="wood_low"),
            Bubble("先换【一批人】", 760, 520, 44, at=1, enter="pop", sfx="pop"),
            Spark(760, 520, at=2, sfx="ding"),
        ], draw=A.ground),
        S("先换一批人", "当下 · 现象", [
            Custom(A.desks, x=540, y=760, at=0, enter="none", swap=0, step=0.5, mood="smile"),
        ], hits=[(0, "pop", 0.8, "换人"), (1, "pop", 0.8, "换人"), (2, "ding", 0.7, "换完")]),
        S("流程照旧，考核照旧", "当下 · 现象", [
            Custom(A.desks, x=540, y=760, at=0, enter="none", mood="flat", old=("#C98B5A", "#7E6FA6", "#5E9A8A"),
                   tag="老流程", tag_color=K.INK2),
            Label("老考核", 540, 430, 44, at=2, sfx="rim", fill=K.RED),
        ], hits=[(0, "wood_low", 0.7, "照旧"), (1, "wood_high", 0.7, "照旧")]),
        S("三个月，又回原样", "当下 · 现象", [
            Custom(A.desks, x=540, y=760, at=0, enter="none", mood="sad", old=("#C98B5A", "#7E6FA6", "#5E9A8A")),
            Bubble("不是我的事", 300, 450, 40, at=1, enter="pop", sfx="wood_high"),
            Bubble("等领导定", 760, 470, 40, at=2, enter="pop", sfx="rim"),
        ], shake=[2]),
        pops("换 人 不如 【换结构】", "一句话", size=150, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("先把系统画出来", "落到自己", [
            Custom(A.system_map, x=540, y=760, at=0, enter="fade", b0=0, step=0.25, b1=1.5, b2=2.5),
            Fig(985, G + 40, 230, at=2, pose="point", mood="smile", face=-1, **ME),
        ], hits=[(0, "pop", 0.8, "要素"), (1, "pop", 0.8, "要素"), (2, "wood_high", 0.8, "连接"), (3, "ding", 0.9, "目标")]),
        # ---- 看系统 4 招 36–41
        S("书里给了思路", "看系统 4 招", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="看系统 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 先看行为再找原因", "看系统 4 招 · 书中观点", [
            Fig(300, G, 300, at=0, pose="think", mood="calm", **ME, sfx="pop"),
            Icon("eye", 760, 600, 170, color=ACC, at=1, sfx="pop"),
            Icon("photo", 760, 860, 150, color=K.GOLD, at=2, sfx="ding"),
        ], draw=A.ground),
        S("② 画出要素和连接", "看系统 4 招", [
            Custom(A.system_map, x=540, y=760, at=0, enter="fade", b0=0, step=0.25, b1=1.5, b2=99),
        ], hits=[(0, "pop", 0.8, "要素"), (1, "pop", 0.8, "要素"), (2, "wood_high", 0.8, "连接")]),
        S("③ 从行为找真目标", "看系统 4 招 · 书中观点", [
            Custom(A.system_map, x=540, y=760, at=0, enter="none", b0=-9, b1=-9, b2=1),
            Spark(540, 760, at=1, sfx="ding"),
            Label("真目标", 540, 1150, 44, at=2, sfx="pop", fill=A.RED),
        ], hits=[(0, "wood_low", 0.7, "系统")]),
        S("④ 先动连接和目标", "看系统 4 招 · 书中观点", [
            Custom(A.system_map, x=540, y=760, at=0, enter="none", b0=-9, b1=-9, b2=-9, rewire=1),
            Fig(985, G + 40, 230, at=0, pose="push", mood="happy", face=-1, **ME),
        ], hits=[(1, "wood_high", 0.9, "改线"), (2, "ding", 0.8, "改目标")], shake=[1]),
        S("别只盯着换人", "一句话", [
            Custom(A.desks, x=540, y=760, at=0, enter="fade", mood="happy", tag="新流程", tag_color=ACC),
            Spark(540, 540, at=2, sfx="ding"),
        ], hits=[(0, "wood_low", 0.7, "工位"), (1, "pop", 0.8, "新流程")]),
        # ---- 片尾 42
        outro("你们公司换过一批人吗？", "工资涨了，为什么还是存不下钱？", "先看结构，再看人"),
    ]
    return episode(1, "system", "系统是什么", "换了一批人，公司为什么还是老样子？", ACC, shots,
                   [f"{BOOK}第一章（转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                   "换了人|没换【结构】", 8,
                   ["书中观点均为转述，非原文引用：系统由要素、连接、功能或目标三部分组成；系统大于各部分之和；开篇弹簧玩具演示"
                    "说明行为来自结构；改变要素通常影响最小，改变连接与目标影响更大，目标是最不显眼却最关键的部分；系统目标要从"
                    "行为推断而非口号。出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)，中译本《系统之美》"
                    "（邱昭良译，浙江人民出版社 2012）。",
                    "球队、客户第一横幅、考核只看业绩、新领导换人均为示意，“看系统 4 招”为据书中观点整理的小建议。"],
                   tags="#管理 #团队")


def _ball(g):
    """传球：球从左边人手里沿弧线飞到右边。"""
    from engine.gfx import clamp01, lerp

    k = clamp01(g.since(0) / max(0.01, g.b(2) - g.b(0)))
    x = lerp(300, 780, k)
    y = 900 - 260 * 4 * k * (1 - k)
    K.dot(g.c, x, y, 34, K.PAPER)
    K.ring(g.c, x, y, 34, K.INK, 5)
