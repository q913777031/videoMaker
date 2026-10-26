"""02 存量与流量：工资涨了，为什么还是存不下钱？（快节奏版：42 镜 × 1 小节）

书中观点（转述）：存量是系统里可以看见、可以计量的积累；流量是让存量随时间变化的流入与流出。
浴缸是最简单的系统：进水多于出水，水位上升；出水多于进水，水位下降；进出相等，水位保持不变（动态平衡）。
想提高水位，既可以加大进水，也可以减少出水。存量的变化需要时间，存量本身起到缓冲作用，让进出流量可以暂时不一致。
"""

from adler import kit as K
from adler.core import Big, Card, Counter, Custom, Fig, Icon, Label, Rays, Spark
from maoxuan.art import notebook
from maoxuan.art_d import daily
from scarcity.art import bill, laptop

from . import art_b as A
from .common import BOOK, S, episode, outro, pops

ACC = "#3E7FA8"
G = A.GROUND_Y
ME = dict(role="worker")

SQUARE_SHOT = 14


def build():
    tub = dict(x=600, y=820)
    shots = [
        # ---- 钩子 1–8
        S("工资又涨了", "灵魂拷问", [
            Fig(330, G, 330, at=0, pose="stand", mood="smile", **ME,
                moves=[(1, dict(pose="cheer", mood="happy", dur=0.25, sfx="pop"))]),
            Icon("phone", 760, 620, 170, color=K.INK2, at=0, sfx="wood_high"),
            Label("工资到账", 760, 440, 40, at=2, sfx="ding", fill=K.GREEN), Spark(760, 620, at=2),
        ], draw=A.ground, punch=0.025, flashes=[0]),
        S("可月底一看", "灵魂拷问", [
            Custom(A.jar, x=540, y=800, at=0, enter="pop", l0=0.7, l1=0.15, b0=0, b1=3, label="存款", sfx="pop"),
        ], hits=[(1, "shaker", 0.7, "往下掉"), (3, "rim", 0.9, "见底")]),
        S("又见底了", "灵魂拷问", [
            Custom(A.jar, x=720, y=800, at=0, enter="none", l0=0.05, l1=0.05, label="存款"),
            Fig(300, G, 320, at=0, pose="stand", mood="surprised", **ME,
                moves=[(2, dict(pose="sad", mood="sad", dur=0.3, sfx="tom"))]),
        ], draw=A.ground, hits=[(0, "rim", 0.8, "空罐")]),
        S("钱都去哪了？", "灵魂拷问", [
            Custom(bill, x=270, y=760, at=0, enter="pop", sfx="pop"),
            Custom(bill, x=540, y=740, at=1, enter="pop", sfx="pop"),
            Custom(bill, x=810, y=760, at=2, enter="pop", sfx="pop"),
            Icon("question", 540, 470, 110, color=K.RED, at=3, sfx="rim"),
        ]),
        S("涨薪也存不住", "灵魂拷问", [
            Card("收入|涨了", 300, 740, 50, at=0, sfx="pop"),
            Card("存款|没动", 780, 740, 50, at=1, sfx="pop"),
            Icon("check", 300, 520, 100, color=K.GREEN, at=2, sfx="ding"),
            Icon("cross", 780, 520, 100, color=K.RED, at=3, sfx="rim"),
        ]),
        pops("问题不在 收入 在 【进出】", "灵魂拷问", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="存钱 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("系统之美里说", "系统之美", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《系统之美》|德内拉·梅多斯", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9
        S("", "书中观点", [
            Big("看水位", 540, 640, 160, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：核心观点落版"),
            Big("要看进和出", 540, 860, 150, at=1, sfx="kick", sub="书中观点 · 存量与流量", sub_size=40, shine=True),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        # ---- 浴缸机制 10–17
        S("像一只浴缸", "书中观点 · 浴缸", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.4, l1=0.4, inflow=0, outflow=0),
            Label("存量", 600, 1010, 46, at=1, sfx="pop", fill=ACC),
            Spark(600, 800, at=2, sfx="ding"),
        ], hits=[(0, "wood_low", 0.8, "浴缸")]),
        S("进水：流入", "书中观点 · 流入", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.25, l1=0.7, b0=1, b1=3.8, inflow=0.8, outflow=0, in_label="流入"),
        ], hits=[(0, "pop", 0.8, "开水龙头"), (1, "shaker", 0.7, "进水"), (3, "ding", 0.8, "水位升")]),
        S("出水：流出", "书中观点 · 流出", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.7, l1=0.2, b0=1, b1=3.8, inflow=0, outflow=0.8, out_label="流出"),
        ], hits=[(0, "pop", 0.8, "拔塞子"), (1, "shaker", 0.7, "出水"), (3, "rim", 0.8, "水位降")]),
        S("进等于出，水位不动", "书中观点 · 动态平衡", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.45, l1=0.45, inflow=0.6, outflow=0.6, in_label="流入",
                   out_label="流出"),
            Label("动态平衡", 600, 1010, 46, at=2, sfx="ding", fill=ACC),
        ], hits=[(0, "shaker", 0.7, "进出同时")]),
        pops("一直在流 却 【不涨】", "书中观点 · 动态平衡", size=140, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("存款就是这缸水", "落到钱包", [
            Custom(A.bathtub, x=640, y=820, at=0, enter="fade", l0=0.35, l1=0.35, inflow=0.6, outflow=0.6,
                   in_label="工资", out_label="开销", label="存款", w=560),
            Fig(150, G, 280, at=1, pose="point", mood="open", **ME, sfx="pop"),
        ], draw=A.ground, hits=[(0, "wood_low", 0.8, "浴缸"), (2, "ding", 0.8, "存款")]),
        S("工资涨了，开销也涨", "落到钱包", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.3, l1=0.3, inflow=1.0, outflow=1.0, in_label="工资涨",
                   out_label="开销涨"),
        ], hits=[(0, "pop", 0.8, "进水变粗"), (2, "pop", 0.8, "出水变粗")]),
        S("水位还是不动", "落到钱包", [
            Custom(A.bathtub, **tub, at=0, enter="none",  l0=0.3, l1=0.3, inflow=1.0, outflow=1.0),
            Label("还是不动", 600, 1010, 46, at=1, sfx="rim", fill=K.RED),
            Icon("cross", 860, 520, 100, color=K.RED, at=3, sfx="rim"),
        ]),
        # ---- 两头都能调 18–20
        S("只盯着进水口？", "书中观点 · 两个口", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.3, l1=0.3, inflow=0.6, outflow=0.6),
            Icon("eye", 300, 450, 130, color=K.INK2, at=1, sfx="pop"),
            Icon("question", 840, 1000, 100, color=K.RED, at=3, sfx="rim"),
        ]),
        S("关小出水也行", "书中观点 · 两个口", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.3, l1=0.65, b0=1, b1=3.8, inflow=0.6, outflow=0.2, out_label="关小"),
        ], hits=[(0, "pop", 0.8, "拧阀门"), (1, "shaker", 0.7, "水位涨"), (3, "ding", 0.9, "涨了")]),
        S("两头都能调", "书中观点 · 两个口", [
            Card("加大流入", 300, 760, 54, at=0, sfx="pop"),
            Card("减少流出", 780, 760, 54, at=1, sfx="pop"),
            Icon("check", 300, 540, 100, color=K.GREEN, at=2, sfx="ding"),
            Icon("check", 780, 540, 100, color=K.GREEN, at=3, sfx="ding"),
        ]),
        # ---- 需要时间 21–24
        S("但水位涨得很慢", "书中观点 · 存量变化需要时间", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.2, l1=0.32, b0=0, b1=3.9, inflow=0.5, outflow=0.3),
            Icon("clock", 880, 450, 120, color=K.INK2, at=1, sfx="wood_high"),
        ], hits=[(2, "shaker", 0.6, "慢慢涨"), (3, "pop", 0.7, "一点点")]),
        pops("存量 变化 需要 【时间】", "书中观点 · 存量变化需要时间", size=130, flash=3,
             extra=[Rays(540, 780, 620, at=3, alpha=0.2)]),
        S("体重技能也一样", "书中观点 · 存量变化需要时间", [
            Icon("heart", 270, 760, 170, color=K.RED, at=0, sfx="pop"),
            Icon("book", 540, 760, 170, color=ACC, at=1, sfx="pop"),
            Icon("sprout", 810, 760, 170, color=K.GREEN, at=2, sfx="pop"),
            Label("都是存量", 540, 1000, 46, at=3, sfx="ding", fill=ACC),
        ]),
        S("别急着看结果", "落到自己", [
            Fig(400, G, 330, at=0, pose="think", mood="calm", **ME),
            Icon("clock", 720, 560, 160, color=K.INK2, at=1, sfx="wood_high"),
            Icon("check", 720, 820, 100, color=K.GREEN, at=3, sfx="ding"),
        ], draw=A.ground),
        # ---- 缓冲 25–29（二次钩子）
        S("存量还有个用处", "书中观点 · 缓冲", [
            Icon("shield", 540, 700, 260, color=ACC, at=0, sfx="kick"),
            Icon("question", 760, 480, 100, color=K.RED, at=2, sfx="rim"),
        ], punch=0.025, flashes=[0], shake=[0]),
        S("进水忽大忽小", "书中观点 · 缓冲", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.5, l1=0.5, inflow=1.0, outflow=0.5, pulse=True, in_label="忽大忽小"),
        ], hits=[(0, "shaker", 0.7, "忽大"), (1, "shaker", 0.5, "忽小"), (2, "shaker", 0.7, "忽大")]),
        S("出水照样稳", "书中观点 · 缓冲", [
            Custom(A.bathtub, **tub, at=0, enter="none",  l0=0.5, l1=0.5, inflow=1.0, outflow=0.5, pulse=True,
                   out_label="稳稳的"),
            Label("缓冲", 600, 1010, 46, at=2, sfx="ding", fill=ACC),
        ], hits=[(0, "pop", 0.7, "出水稳")]),
        S("存款就是安全垫", "落到钱包", [
            Fig(330, G, 330, at=0, pose="relax", mood="smile", **ME),
            Custom(A.jar, x=760, y=800, at=1, enter="pop", l0=0.75, l1=0.75, label="应急金", sfx="pop"),
            Spark(760, 700, at=2, sfx="ding"),
        ], draw=A.ground),
        S("没缓冲就慌了", "落到钱包", [
            Fig(330, G, 330, at=0, pose="stand", mood="worried", **ME,
                moves=[(2, dict(pose="cover", dur=0.25, sfx="tom"))]),
            Custom(A.jar, x=760, y=800, at=0, enter="pop", l0=0.03, l1=0.03, label="应急金"),
            Icon("cross", 930, 560, 100, color=K.RED, at=1, sfx="rim"),
        ], draw=A.ground, shake=[2]),
        # ---- 当下 30–35
        S("今天：钱来就花", "当下 · 现象", [
            Custom(laptop, x=320, y=720, at=0, enter="pop", w=420, h=270, title="购物车", p0=0.2, p1=1, b0=0, b1=3,
                   sfx="pop"),
            Icon("phone", 800, 720, 170, color=K.INK2, at=1, sfx="pop"),
            Label("已付款", 800, 500, 40, at=2, sfx="rim", fill=K.RED),
        ]),
        S("小额订阅一大堆", "当下 · 现象", [
            Label("会员", 270, 620, 44, at=0, sfx="pop"),
            Label("外卖", 540, 560, 44, at=1, sfx="pop"),
            Label("打车", 810, 620, 44, at=2, sfx="pop"),
            Label("奶茶", 540, 760, 44, at=3, sfx="pop"),
            Custom(bill, x=540, y=980, at=0, enter="fade", w=220, h=260),
        ]),
        S("出水口没人管", "当下 · 现象", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.5, l1=0.12, b0=1, b1=3.8, inflow=0.6, outflow=1.0, out_label="没人管"),
        ], hits=[(0, "pop", 0.7, "出水"), (1, "shaker", 0.7, "哗哗流"), (3, "rim", 0.9, "见底")]),
        S("缸里总是空的", "当下 · 现象", [
            Custom(A.jar, x=720, y=800, at=0, enter="none", l0=0.03, l1=0.03, label="存款"),
            Fig(300, G, 320, at=0, pose="sit_sad", mood="sad", **ME),
            Icon("cloud", 300, 520, 140, color=K.INK2, at=1, sfx="wood_low"),
            Icon("cloud", 470, 480, 100, color=K.INK3, at=2, sfx="wood_low"),
        ], draw=A.ground),
        pops("存不住 是没管 【出水口】", "一句话", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("先看清两个口", "落到自己", [
            Card("流入|工资 · 副业", 300, 760, 46, at=0, sfx="pop"),
            Card("流出|开销 · 订阅", 780, 760, 46, at=1, sfx="pop"),
            Icon("eye", 540, 500, 130, color=ACC, at=2, sfx="ding"), Spark(540, 500, at=2),
        ]),
        # ---- 4 招 36–41
        S("书里的思路，四招", "存钱 4 招", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="存钱 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 记下流出", "存钱 4 招 · 看清出水口", [
            Custom(notebook, x=540, y=800, at=0, enter="pop", b0=0, step=1, lines=("房租：", "吃饭：", "订阅：", "其他：")),
        ], hits=[(0, "shaker", 0.7, "写"), (1, "shaker", 0.7, "写"), (2, "shaker", 0.7, "写"), (3, "ding", 0.9, "写完")]),
        S("② 先拧小出水", "存钱 4 招 · 减少流出", [
            Custom(A.bathtub, **tub, at=0, enter="fade", l0=0.25, l1=0.55, b0=1, b1=3.8, inflow=0.6, outflow=0.25, out_label="拧小"),
        ], hits=[(0, "pop", 0.8, "拧阀门"), (1, "shaker", 0.7, "涨"), (3, "ding", 0.9, "涨了")]),
        S("③ 留一缸缓冲", "存钱 4 招 · 建缓冲", [
            Custom(A.jar, x=540, y=800, at=0, enter="pop", l0=0.1, l1=0.7, b0=0, b1=3, label="应急金", sfx="pop"),
            Spark(540, 640, at=3, sfx="ding"),
        ], hits=[(1, "shaker", 0.7, "存"), (2, "shaker", 0.7, "存")]),
        S("④ 给存量时间", "存钱 4 招 · 耐心", [
            Custom(daily, x=540, y=800, at=0, enter="pop", n=21, b0=0, step=0.15, title="每月存一点", sfx="pop"),
        ], hits=[(1, "shaker", 0.7, "打勾"), (2, "shaker", 0.7, "打勾"), (3, "ding", 0.9, "满了")]),
        S("水位慢慢涨", "收束", [
            Custom(A.bathtub, x=640, y=820, at=0, enter="fade", l0=0.3, l1=0.75, b0=0, b1=3.6, inflow=0.6,
                   outflow=0.25, w=560, label="存款"),
            Fig(150, G, 280, at=2, pose="cheer", mood="happy", **ME, sfx="ding"),
        ], draw=A.ground, hits=[(0, "shaker", 0.7, "涨"), (1, "pop", 0.7, "涨")]),
        # ---- 片尾 42
        outro("你的“出水口”在哪？", "减肥为什么总会反弹？", "看住进出，水位才涨"),
    ]
    return episode(2, "stock", "存量与流量", "工资涨了，为什么还是存不下钱？", ACC, shots,
                   [f"{BOOK}：存量与流量、浴缸、动态平衡、存量的缓冲作用"],
                   "收入涨了|也要看【出水口】", 8,
                   ["出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)；中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                    "“看水位要看进和出”“存量变化需要时间”“存量是缓冲”为书中观点的转述，不是原文引文；浴缸、动态平衡为书中例子与概念。",
                    "工资、开销、存款、应急金、订阅等是今日化示意，画面中的水位、罐子高度、打卡格数均为示意，不代表任何真实数据；存钱 4 招为由书中思路引申的小建议。"],
                   tags="#存钱 #理财")
