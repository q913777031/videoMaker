"""06 增长的极限：业绩为什么涨着涨着就不动了？（快节奏版：42 镜 × 1 小节）

书中观点（转述）：在有限的环境里，靠增强回路推动的增长迟早会碰上调节回路，曲线由陡变平；书中举了开采不可再生资源
（油田）与捕捞可再生资源（渔场）的例子；限制增长的因素不止一个，补上一个，下一个就会成为新的限制，所以要不断找出
当下真正的限制因素；增长管理的真正选择在于接受哪种极限。木桶短板为示意比喻。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Spark
from scarcity.art import GROUND_Y, ground
from zizhi.art import magnifier, thing

from . import art_c as A
from .common import BOOK, S, episode, outro, pops

ACC = "#5E8A4A"
G = GROUND_Y
ME = dict(role="worker", hair="short")
BOSS = dict(role="boss", hair="short")
BARREL = [("人手", 0.8), ("资金", 0.9), ("客户", 0.45), ("产能", 0.68)]
BARREL2 = [("人手", 0.8), ("资金", 0.9), ("客户", 0.95), ("产能", 0.68)]

SQUARE_SHOT = 4


def build():
    shots = [
        # ---- 钩子 1–8
        S("业绩一路往上", "灵魂拷问", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="exp", b0=0, b1=3, ylab="业绩", xlab="时间"),
            Icon("trophy", 820, 500, 110, color=K.GOLD, at=3, sfx="ding"), Spark(820, 500, at=3),
        ], punch=0.025, flashes=[0], hits=[(0, "shaker", 0.8, "上涨")]),
        S("领导：明年翻倍", "灵魂拷问", [
            Fig(760, G, 340, at=0, pose="cheer", mood="happy", face=-1, **BOSS, sfx="wood_low"),
            Bubble("明年【翻倍】！", 560, 500, 52, at=1, enter="pop", sfx="kick"),
            Fig(280, G, 300, at=0, pose="stand", mood="surprised", **ME),
        ], draw=ground, shake=[1]),
        S("加人加班加预算", "灵魂拷问", [
            Icon("friends", 260, 760, 190, color=K.HERO, at=0, sfx="pop"),
            Icon("clock", 540, 740, 180, color=K.INK2, at=1, sfx="pop"),
            Custom(thing, x=820, y=780, at=2, enter="pop", obj="moneybag", s=260, sfx="pop"),
            Spark(540, 740, at=3, sfx="ding"),
        ]),
        S("可曲线变平了", "灵魂拷问", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="s", b0=0, b1=3.6, ylab="业绩", xlab="时间"),
            Icon("question", 820, 470, 90, color=K.RED, at=3, sfx="rim"),
        ], hits=[(0, "shaker", 0.8, "曲线"), (2, "tom", 0.7, "变平")]),
        S("越用力越推不动", "灵魂拷问", [
            Custom(A.rock, x=700, y=G, at=0, enter="fade", s=420, label="瓶颈", shake=1),
            Fig(330, G, 320, at=0, pose="push", mood="worried", **ME,
                moves=[(2, dict(mood="angry", dur=0.2, sfx="kick"))]),
        ], draw=ground, hits=[(1, "tom", 0.8, "推")], shake=[2]),
        pops("不是你不努力 是撞上了 【极限】", "灵魂拷问", size=120, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="突破 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("系统之美里一句话", "系统之美", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《系统之美》|德内拉·梅多斯", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9
        S("", "书中观点", [
            Big("增长总会", 540, 640, 160, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：观点落版"),
            Big("碰到极限", 540, 860, 160, at=1, sfx="kick", sub="《系统之美》", sub_size=40, shine=True),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        # ---- 机制 10–14
        S("增长靠增强回路", "书中观点 · 增强回路", [
            Custom(A.loops, x=540, y=780, at=0, enter="fade", a=0, b=99, labels=("增长", "极限")),
        ], hits=[(0, "pop", 0.8, "回路"), (2, "shaker", 0.7, "越转越快")]),
        pops("赚得多 投得多 赚得 【更多】", "书中观点 · 增强回路", size=120, flash=3),
        S("可环境有上限", "书中观点 · 有限环境", [
            Custom(A.loops, x=540, y=780, at=0, enter="none", a=-9, b=1, labels=("增长", "极限")),
        ], hits=[(1, "kick", 0.9, "调节回路出现")], shake=[1]),
        S("刹车开始起作用", "书中观点 · 调节回路", [
            Custom(A.rock, x=760, y=G, at=0, enter="fade", s=300, label="上限"),
            Fig(380, G, 320, at=0, pose="push", mood="worried", **ME,
                moves=[(2, dict(pose="sad", mood="sad", dur=0.3, sfx="tom"))]),
        ], draw=ground, hits=[(0, "wood_low", 0.8, "上限")]),
        S("增长曲线变平", "书中观点 · 有限环境", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="s_exp", b0=0, b1=3.6, ghost_at=0,
                   ylab="业绩", xlab="时间", marks=[("以为会这样", 0.8, -230), ("其实是这样", 0.95, 70)]),
        ], hits=[(0, "shaker", 0.8, "曲线"), (3, "rim", 0.9, "变平")]),
        # ---- 书中例子 15–20
        S("书里讲了油田", "书中例子 · 油田", [
            Custom(A.derrick, x=540, y=760, at=0, enter="fade", b0=0, b1=3),
            Fig(860, G, 280, at=1, pose="wave", mood="happy", role="worker", color="#8C6A3A", sfx="pop"),
        ], draw=ground, hits=[(0, "wood_low", 0.8, "井架")]),
        S("越挖越难挖", "书中例子 · 油田", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="fall", b0=0, b1=3, ylab="剩余储量", xlab="时间"),
            Icon("cross", 820, 500, 100, color=K.RED, at=3, sfx="rim"),
        ], hits=[(0, "shaker", 0.8, "下降"), (2, "tom", 0.7, "下降")]),
        S("还有个渔场", "书中例子 · 渔场", [
            Custom(A.fishery, x=540, y=760, at=0, enter="fade", boats=[(0, 1)], fish=[(0, 12)]),
        ], hits=[(0, "wood_low", 0.8, "海"), (2, "pop", 0.7, "鱼游")]),
        S("船多了，鱼少了", "书中例子 · 渔场", [
            Custom(A.fishery, x=540, y=760, at=0, enter="none", boats=[(0, 2), (1, 3), (2, 5), (3, 6)],
                   fish=[(0, 10), (1, 7), (2, 4), (3, 2)]),
        ], hits=[(1, "pop", 0.8, "加船"), (2, "pop", 0.8, "加船"), (3, "rim", 0.9, "鱼少")]),
        S("鱼少到捞不上来", "书中例子 · 渔场", [
            Fig(400, G, 320, at=0, pose="sad", mood="sad", role="farmer"),
            Icon("water", 740, 720, 150, color="#4F86B8", at=1, sfx="pop"),
            Icon("cross", 740, 520, 110, color=K.RED, at=2, sfx="rim"),
        ], draw=ground),
        pops("增长 总有 【上限】", "一句话", size=150, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 二次钩子 21–26
        S("但还有更狠的", "反转", [
            Fig(540, G, 330, at=0, pose="think", mood="worried", **ME),
            Icon("question", 360, 480, 100, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 720, 450, 120, color=K.RED, at=2, sfx="rim"),
        ], draw=ground, flashes=[2]),
        S("最短那块定水位", "书中观点 · 限制因素", [
            Custom(A.staves, x=540, y=760, at=0, enter="fade", items=BARREL, tag="卡在这"),
        ], hits=[(0, "wood_low", 0.8, "木桶"), (2, "rim", 0.9, "短板")]),
        S("补上客户这块", "书中观点 · 限制因素", [
            Custom(A.staves, x=540, y=760, at=0, enter="none", items=BARREL, **{"raise": (1, 2, 0.95)}),
        ], hits=[(1, "kick", 0.9, "补长"), (2, "ding", 0.8, "水涨")]),
        S("下一块又成短板", "书中观点 · 限制会转移", [
            Custom(A.staves, x=540, y=760, at=0, enter="none", items=BARREL2, tag="又卡在这"),
            Icon("question", 820, 420, 80, color=K.RED, at=2, sfx="rim"),
        ], hits=[(0, "wood_low", 0.8, "木桶"), (1, "tom", 0.8, "新短板")]),
        pops("限制 会 【转移】", "书中观点", size=160, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("得一直盯着找", "书中观点 · 找限制因素", [
            Fig(360, G, 330, at=0, pose="reach", mood="calm", **ME),
            Custom(magnifier, x=700, y=600, at=1, enter="pop", r=130, sfx="wood_high"),
            Spark(700, 600, at=3, sfx="ding"),
        ], draw=ground),
        # ---- 当下 27–34
        S("今天：客户猛增", "当下 · 现象", [
            Fig(400, G, 330, at=0, pose="cheer", mood="happy", role="worker_f"),
            Icon("phone", 720, 640, 130, color=K.INK2, at=1, sfx="pop"),
            Icon("heart", 820, 460, 90, color=K.RED, at=2, sfx="pop"),
        ], draw=ground),
        S("客服接不过来", "当下 · 现象", [
            Fig(540, G, 330, at=0, pose="cover", mood="worried", **ME),
            Icon("phone", 260, 600, 110, color=K.INK2, at=0, sfx="pop"),
            Icon("phone", 820, 560, 110, color=K.INK2, at=1, sfx="pop"),
            Icon("phone", 300, 420, 100, color=K.INK2, at=2, sfx="pop"),
            Icon("phone", 780, 380, 100, color=K.RED, at=3, sfx="rim"),
        ], draw=ground),
        S("差评越来越多", "当下 · 现象", [
            Icon("cross", 260, 720, 140, color=K.RED, at=0, sfx="rim"),
            Icon("cross", 540, 660, 160, color=K.RED, at=1, sfx="rim"),
            Icon("cross", 820, 720, 140, color=K.RED, at=2, sfx="rim"),
            Label("差评", 540, 900, 50, at=3, sfx="tom", fill=K.RED),
        ], shake=[2]),
        S("又砸钱拉新客", "当下 · 现象", [
            Fig(760, G, 340, at=0, pose="give", mood="happy", face=-1, **BOSS),
            Custom(thing, x=480, y=700, at=1, enter="pop", obj="moneybag", s=240, sfx="kick"),
            Bubble("再多【投】点！", 560, 460, 46, at=2, enter="pop", sfx="wood_high"),
        ], draw=ground),
        S("结果卡得更死", "当下 · 现象", [
            Custom(A.staves, x=540, y=760, at=0, enter="fade",
                   items=[("客户", 0.95), ("资金", 0.9), ("客服", 0.3), ("产品", 0.7)], tag="客服"),
        ], hits=[(0, "wood_low", 0.8, "木桶"), (2, "rim", 1.0, "卡死")], shake=[2]),
        pops("该补 【短板】 不是踩 【油门】", "落到自己", size=120, flash=1),
        S("先看上限在哪", "落到自己", [
            Fig(360, G, 330, at=0, pose="think", mood="calm", **ME),
            Custom(A.rock, x=760, y=G, at=1, enter="pop", s=280, label="上限", sfx="wood_low"),
            Icon("bulb", 360, 400, 100, color=K.GOLD, at=2, sfx="ding"),
        ], draw=ground),
        S("先扩容量再拉客", "落到自己", [
            Fig(300, G, 320, at=0, pose="give", mood="smile", **ME),
            Fig(560, G, 300, at=1, pose="wave", mood="happy", role="worker_f", sfx="pop"),
            Fig(800, G, 300, at=2, pose="wave", mood="happy", role="worker", color="#8C9A6A", face=-1, sfx="pop"),
            Icon("check", 560, 430, 100, color=K.GREEN, at=3, sfx="ding"),
        ], draw=ground),
        # ---- 突破 4 招 35–41
        S("书里给的思路", "书中观点 · 与极限相处", [
            Custom(thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="突破 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 认出刹车回路", "突破 4 招 · 认出调节回路", [
            Custom(A.loops, x=540, y=780, at=0, enter="fade", a=0, b=1, labels=("增长", "极限")),
        ], hits=[(0, "pop", 0.8, "增长"), (1, "kick", 0.8, "刹车")]),
        S("② 找出当下短板", "突破 4 招 · 找限制因素", [
            Custom(A.staves, x=540, y=760, at=0, enter="fade", items=BARREL, tag="短板"),
        ], hits=[(0, "wood_low", 0.8, "木桶"), (2, "ding", 0.9, "找到")]),
        S("③ 先补短板", "突破 4 招 · 补限制因素", [
            Custom(A.staves, x=540, y=760, at=0, enter="fade", items=BARREL, mark=True, **{"raise": (1, 2, 0.95)}),
        ], hits=[(1, "kick", 0.9, "补长"), (2, "ding", 0.9, "水涨")]),
        S("④ 盯住下一块", "突破 4 招 · 限制会转移", [
            Custom(A.staves, x=540, y=760, at=0, enter="fade", items=BARREL2, tag="下一块"),
            Custom(magnifier, x=820, y=440, at=1, enter="pop", r=90, sfx="wood_high"),
        ], hits=[(0, "wood_low", 0.8, "木桶")]),
        S("主动选择上限", "书中观点 · 选择你的极限", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="s", b0=0, b1=3, color=K.GREEN, target="自己选的上限",
                   ylab="业绩", xlab="时间"),
            Icon("check", 860, 480, 90, color=K.GREEN, at=3),
        ], hits=[(0, "shaker", 0.8, "曲线"), (3, "ding", 0.9, "稳住")]),
        S("稳稳长才长久", "收束", [
            Rays(540, 700, 620, at=0, alpha=0.2),
            Fig(540, G, 340, at=0, pose="relax", mood="smile", **ME,
                moves=[(2, dict(pose="cheer", mood="happy", dur=0.3, sfx="ding"))]),
            Icon("sprout", 800, 760, 160, color=K.GREEN, at=1, sfx="pop"),
        ], draw=ground),
        # ---- 片尾 42
        outro("你撞过哪种“天花板”？", "公司冰箱为什么总是乱糟糟？", "找到短板再发力"),
    ]
    return episode(6, "limits", "增长的极限", "业绩为什么涨着涨着就不动了？", ACC, shots,
                   [f"{BOOK}（Thinking in Systems: A Primer, 2008）", "中译本：邱昭良译，浙江人民出版社 2012"],
                   "涨不动|是撞上了【极限】", 8,
                   ["出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)；中译本《系统之美》（邱昭良译，"
                    "浙江人民出版社 2012）。原书中文全文未逐字核对，片中“书中观点”均为转述，不是原话。",
                    "书中例子：开采不可再生资源（油田）与捕捞可再生资源（渔场）对增长的约束；“限制因素会转移”“选择接受哪种极限”"
                    "为书中观点转述。木桶短板为示意比喻，各板高度、船数、鱼数、曲线形状均为示意。",
                    "“当下”部分为现象示意，不点名公司；4 招为据书中观点整理的小建议。"],
                   tags="#增长 #瓶颈 #职场")
