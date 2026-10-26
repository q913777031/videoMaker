"""05 延迟：为什么越着急，越容易出乱子？（快节奏版：42 镜 × 1 小节）

书中观点（转述）：反馈回路里有延迟时，系统容易来回振荡；书中以汽车经销商的库存为例——感知销量变化、做出订货决定、
工厂交货都需要时间，订单到货时库存已经过量，于是又砍订单，库存上下摆动；在这个模型里，经销商反应得更快反而振荡更厉害，
放慢反应、看平均趋势反而更稳。调水温忽冷忽热为生活类比。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Spark
from scarcity.art import GROUND_Y, ground, laptop
from zizhi.art import thing

from . import art_c as A
from .common import BOOK, S, episode, outro, pops

ACC = "#3E6A8A"
G = GROUND_Y
ME = dict(role="worker", hair="short")
BOSS = dict(role="boss", hair="short")

SQUARE_SHOT = 10


def build():
    shots = [
        # ---- 钩子 1–8
        S("项目突然告急", "灵魂拷问", [
            Fig(400, G, 330, at=0, pose="stand", mood="worried", **ME,
                moves=[(2, dict(pose="cover", mood="surprised", dur=0.25, sfx="rim"))]),
            Icon("phone", 720, 620, 150, color=K.INK2, at=1, sfx="pop"),
            Icon("question", 720, 440, 90, color=K.RED, at=2),
        ], draw=ground, punch=0.025, flashes=[0], hits=[(0, "wood_low", 0.8, "告急")]),
        S("领导：赶紧加人", "灵魂拷问", [
            Fig(760, G, 340, at=0, pose="point", mood="angry", face=-1, **BOSS, sfx="wood_low"),
            Bubble("赶紧【加人】！", 560, 520, 50, at=1, enter="pop", sfx="kick"),
            Fig(280, G, 300, at=0, pose="stand", mood="worried", **ME),
        ], draw=ground, shake=[1]),
        S("一周后人到了", "灵魂拷问", [
            Icon("clock", 540, 460, 130, color=K.INK2, at=0, sfx="wood_high"),
            Fig(300, G, 300, at=1, pose="wave", mood="happy", role="worker_f", sfx="pop"),
            Fig(560, G, 310, at=2, pose="wave", mood="smile", role="worker", color="#8C9A6A", sfx="pop"),
            Fig(810, G, 300, at=3, pose="wave", mood="happy", role="worker_f", color="#C99A3A", sfx="pop"),
        ], draw=ground),
        S("活儿却已经少了", "灵魂拷问", [
            Fig(400, G, 330, at=0, pose="shrug", mood="worried", **ME),
            Custom(laptop, x=760, y=720, at=0, enter="pop", w=380, h=240, title="待办", p0=0.9, p1=0.15, b0=0, b1=3,
                   sfx="pop"),
            Icon("question", 760, 470, 80, color=K.RED, at=3, sfx="rim"),
        ], draw=ground),
        S("人闲着，又要裁", "灵魂拷问", [
            Fig(760, G, 340, at=0, pose="point", mood="flat", face=-1, **BOSS),
            Bubble("这么多人【闲着】？", 560, 520, 46, at=1, enter="pop", sfx="wood_high"),
            Icon("cross", 280, 600, 140, color=K.RED, at=2, sfx="kick"),
        ], draw=ground, shake=[2]),
        pops("越着急 越 【乱】", "灵魂拷问", size=160, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="稳住 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("系统之美里一句话", "系统之美", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《系统之美》|德内拉·梅多斯", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9
        S("", "书中观点", [
            Big("反馈有延迟", 540, 640, 150, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：观点落版"),
            Big("就会来回晃", 540, 860, 150, at=1, sfx="kick", sub="《系统之美》", sub_size=40, shine=True),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        # ---- 调水温 10–14
        S("先说调水温", "生活类比 · 洗澡", [
            Custom(A.shower, x=540, y=800, at=0, enter="fade", b0=0, mode="osc"),
        ], hits=[(0, "wood_low", 0.8, "喷头"), (2, "shaker", 0.8, "水流")]),
        S("太冷，猛拧一下", "生活类比 · 洗澡", [
            Custom(A.shower, x=650, y=800, at=0, enter="fade", b0=0, mode="osc"),
            Fig(170, G, 300, at=0, pose="cover", mood="surprised", **ME,
                moves=[(2, dict(pose="reach", mood="worried", dur=0.25, sfx="rim"))]),
        ], draw=ground, hits=[(1, "shaker", 0.7, "冷水")]),
        S("太烫，再猛拧", "生活类比 · 洗澡", [
            Fig(400, G, 330, at=0, pose="cover", mood="surprised", **ME,
                moves=[(2, dict(pose="reach", dur=0.2, sfx="wood_high"))]),
            Bubble("好【烫】！", 700, 520, 56, at=0, enter="pop", sfx="kick"),
            Icon("water", 720, 780, 120, color=A.HOT, at=1, sfx="pop"),
        ], draw=ground, shake=[0]),
        S("水温忽冷忽热", "生活类比 · 洗澡", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="osc", b0=0, b1=3.6, target="合适",
                   ylab="水温", xlab="时间"),
        ], hits=[(0, "shaker", 0.8, "曲线"), (1, "pop", 0.7, "太烫"), (2, "pop", 0.7, "太冷")]),
        S("水要走一段管子", "生活类比 · 洗澡", [
            Custom(A.delay_chain, x=540, y=780, at=0, enter="fade", b0=0, step=1,
                   labels=("拧旋钮", "水在管里", "才变温")),
        ], hits=[(0, "pop", 0.8, "拧"), (1, "pop", 0.8, "管里"), (2, "ding", 0.9, "变温")]),
        # ---- 车行 15–22
        S("书里有个车行", "书中例子 · 汽车经销商", [
            Custom(A.lot, x=640, y=740, at=0, enter="fade", keys=[(0, 8)], title="车行库存", scale=0.76),
            Fig(160, G, 300, at=1, pose="wave", mood="smile", role="boss", color="#6E5038", sfx="pop"),
        ], hits=[(0, "wood_low", 0.8, "车场")]),
        S("车卖得快了", "书中例子 · 汽车经销商", [
            Custom(A.lot, x=540, y=760, at=0, enter="none", keys=[(0, 8), (1, 7), (2, 6), (3, 5)],
                   title="车行库存", label="卖得快了"),
        ], hits=[(1, "pop", 0.7, "卖出"), (2, "pop", 0.7, "卖出"), (3, "pop", 0.7, "卖出")]),
        S("老板赶紧多订货", "书中例子 · 汽车经销商", [
            Fig(420, G, 340, at=0, pose="point", mood="open", role="boss", color="#6E5038"),
            Icon("phone", 700, 640, 140, color=K.INK2, at=1, sfx="pop"),
            Bubble("再多【订】点！", 720, 460, 48, at=2, enter="pop", sfx="wood_high"),
        ], draw=ground),
        S("可每步都要时间", "书中例子 · 三种延迟", [
            Custom(A.delay_chain, x=540, y=780, at=0, enter="fade", b0=0, step=1,
                   labels=("看出变化", "下定决心", "货才到")),
        ], hits=[(0, "pop", 0.8, "感知"), (1, "pop", 0.8, "决定"), (2, "ding", 0.9, "交货")]),
        S("货到时已太多", "书中例子 · 汽车经销商", [
            Custom(A.lot, x=540, y=760, at=0, enter="fade", keys=[(0, 5), (1, 9), (2, 12), (3, 14)],
                   title="车行库存"),
        ], hits=[(1, "kick", 0.8, "到货"), (2, "kick", 0.8, "到货"), (3, "rim", 1.0, "停不下")], shake=[3]),
        S("于是又砍订单", "书中例子 · 汽车经销商", [
            Fig(420, G, 340, at=0, pose="stand", mood="angry", role="boss", color="#6E5038",
                moves=[(1, dict(pose="fist", dur=0.2, sfx="kick"))]),
            Bubble("别再【送】了！", 720, 480, 48, at=1, enter="pop"),
            Icon("cross", 740, 720, 140, color=K.RED, at=2, sfx="rim"),
        ], draw=ground, shake=[1]),
        S("库存来回振荡", "书中例子 · 汽车经销商", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="osc", b0=0, b1=3.6, target="理想库存",
                   ylab="库存", xlab="时间"),
        ], hits=[(0, "shaker", 0.8, "曲线"), (1, "pop", 0.7, "过多"), (2, "pop", 0.7, "过少")]),
        pops("问题 不在人 在 【延迟】", "书中观点", size=130, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 二次钩子 23–29
        S("那反应快点呢？", "反转", [
            Fig(540, G, 330, at=0, pose="think", mood="smile", **ME),
            Icon("bulb", 760, 480, 120, color=K.GOLD, at=1, sfx="pop"), Spark(760, 480, at=1),
            Icon("question", 320, 480, 90, color=K.RED, at=2, sfx="wood_high"),
        ], draw=ground),
        S("反应越快，越乱", "书中观点 · 越快越晃", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="osc_big", b0=0, b1=3.6, target="理想库存",
                   color=K.RED, ylab="库存", xlab="时间"),
        ], hits=[(0, "kick", 0.9, "猛冲"), (1, "rim", 0.8, "过头"), (2, "rim", 0.8, "过头")], flashes=[0], shake=[0]),
        S("放慢反而稳了", "书中观点 · 看平均趋势", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="smooth", b0=0, b1=3, target="理想库存",
                   color=K.GREEN, ylab="库存", xlab="时间"),
        ], hits=[(0, "shaker", 0.8, "平稳"), (3, "ding", 1.0, "到位")]),
        pops("慢一点 反而 【稳】", "一句话", size=150, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("延迟到处都有", "延迟无处不在", [
            Icon("sprout", 260, 700, 170, color=K.GREEN, at=0, sfx="pop"),
            Icon("clock", 540, 640, 170, color=K.INK2, at=1, sfx="pop"),
            Icon("phone", 820, 700, 150, color=K.INK2, at=2, sfx="pop"),
            Label("种下", 260, 900, 40, at=0), Label("等待", 540, 860, 40, at=1), Label("回音", 820, 900, 40, at=2),
        ]),
        S("锻炼见效要等", "延迟无处不在", [
            Fig(400, G, 330, at=0, pose="fist", mood="happy", **ME,
                moves=[(1, dict(pose="cheer", dur=0.2, sfx="wood_high")), (2, dict(pose="fist", dur=0.2))]),
            Icon("mirror", 760, 680, 170, color=K.INK2, at=2, sfx="pop"),
            Icon("question", 760, 470, 80, color=K.RED, at=3, sfx="rim"),
        ], draw=ground),
        S("新人上手要等", "延迟无处不在", [
            Fig(360, G, 320, at=0, pose="think", mood="worried", role="worker_f"),
            Custom(laptop, x=740, y=720, at=0, enter="pop", w=380, h=240, title="上手中", p0=0.05, p1=0.6, b0=0, b1=3,
                   sfx="pop"),
            Icon("clock", 740, 470, 90, color=K.INK2, at=2, sfx="wood_high"),
        ], draw=ground),
        # ---- 当下 30–35
        S("今天：数据一跌", "当下 · 现象", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="fall", b0=0, b1=2, ylab="数据", xlab="今天"),
            Icon("question", 820, 500, 90, color=K.RED, at=2, sfx="rim"),
        ], hits=[(0, "shaker", 0.8, "下跌"), (1, "tom", 0.7, "下跌")]),
        S("马上改方案", "当下 · 现象", [
            Fig(760, G, 340, at=0, pose="point", mood="angry", face=-1, **BOSS),
            Bubble("马上【改】！", 560, 520, 50, at=1, enter="pop", sfx="kick"),
            Fig(280, G, 300, at=0, pose="stand", mood="worried", **ME,
                moves=[(2, dict(pose="carry", dur=0.25, sfx="wood_high"))]),
        ], draw=ground, shake=[1]),
        S("效果还没出来", "当下 · 现象", [
            Custom(laptop, x=540, y=740, at=0, enter="pop", w=520, h=320, title="新方案", p0=0.0, p1=0.2, b0=0, b1=3,
                   sfx="pop"),
            Icon("clock", 820, 470, 110, color=K.INK2, at=2, sfx="wood_high"),
        ]),
        S("又改了一版", "当下 · 现象", [
            Card("方案一", 260, 700, 46, at=0, sfx="pop"),
            Card("方案二", 540, 760, 46, at=1, sfx="pop"),
            Card("方案三", 820, 700, 46, at=2, sfx="pop"),
            Icon("cross", 260, 560, 90, color=K.RED, at=1),
            Icon("cross", 540, 620, 90, color=K.RED, at=2),
            Icon("question", 820, 540, 80, color=K.RED, at=3, sfx="rim"),
        ]),
        S("越改越乱", "当下 · 现象", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="osc_big", b0=0, b1=3.6, color=K.RED,
                   ylab="效果", xlab="时间"),
        ], hits=[(0, "kick", 0.8, "乱跳"), (2, "rim", 0.8, "乱跳")], shake=[0]),
        pops("改之前 先 【等一等】", "落到自己", size=140, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 稳住 4 招 36–41
        S("书里给的思路", "书中观点 · 与延迟相处", [
            Custom(thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="稳住 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 先认出延迟", "稳住 4 招 · 认出延迟", [
            Custom(A.delay_chain, x=540, y=760, at=0, enter="fade", b0=0, step=1,
                   labels=("做了动作", "还在路上", "才有结果")),
        ], hits=[(0, "pop", 0.8, "动作"), (1, "pop", 0.8, "路上"), (2, "ding", 0.9, "结果")]),
        S("② 看趋势，别看一天", "稳住 4 招 · 看平均趋势", [
            Custom(A.curve, x=540, y=820, at=0, enter="fade", shape="smooth", b0=0, b1=3, color=K.GREEN,
                   target="趋势", ylab="数据", xlab="一段时间"),
        ], hits=[(0, "shaker", 0.8, "曲线"), (3, "ding", 1.0, "趋势")]),
        S("③ 每次拧小一点", "稳住 4 招 · 动作放小", [
            Custom(A.shower, x=650, y=800, at=0, enter="fade", b0=0, mode="calm"),
            Fig(170, G, 300, at=0, pose="reach", mood="smile", **ME,
                moves=[(2, dict(pose="stand", mood="happy", dur=0.3, sfx="ding"))]),
        ], draw=ground, hits=[(0, "wood_high", 0.7, "轻拧")]),
        S("④ 留点余量", "稳住 4 招 · 留缓冲", [
            Custom(A.lot, x=540, y=760, at=0, enter="fade", keys=[(0, 8), (1, 9), (2, 8), (3, 9)],
                   title="留点库存", label="缓冲"),
        ], hits=[(0, "wood_low", 0.8, "车场"), (1, "pop", 0.7, "平稳"), (3, "ding", 0.9, "平稳")]),
        S("稳住，比快重要", "收束", [
            Rays(540, 700, 620, at=0, alpha=0.2),
            Fig(540, G, 340, at=0, pose="relax", mood="smile", **ME,
                moves=[(2, dict(pose="cheer", mood="happy", dur=0.3, sfx="ding"))]),
            Spark(540, 560, at=2),
        ], draw=ground, hits=[(0, "wood_low", 0.7, "稳住")]),
        # ---- 片尾 42
        outro("你被“来回折腾”坑过吗？", "业绩为什么涨着涨着就不动了？", "急事，更要稳着来"),
    ]
    return episode(5, "delay", "延迟", "为什么越着急，越容易出乱子？", ACC, shots,
                   [f"{BOOK}（Thinking in Systems: A Primer, 2008）", "中译本：邱昭良译，浙江人民出版社 2012"],
                   "越着急|越容易【乱】", 8,
                   ["出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)；中译本《系统之美》（邱昭良译，"
                    "浙江人民出版社 2012）。原书中文全文未逐字核对，片中“书中观点”均为转述，不是原话。",
                    "汽车经销商为书中例子：感知、决定、交货三种延迟使库存振荡；“反应越快越乱、放慢反而更稳”为书中对该模型的结论转述。"
                    "片中不上屏具体天数；车场车辆数、曲线形状均为示意。",
                    "调水温忽冷忽热为生活类比，不是书中例子；“当下”部分为现象示意，不点名公司；4 招为据书中观点整理的小建议。"],
                   tags="#延迟 #职场")
