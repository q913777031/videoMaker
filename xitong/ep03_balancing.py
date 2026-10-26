"""03 调节回路：减肥为什么总会反弹？（快节奏版：42 镜 × 1 小节）

书中观点（转述）：调节回路（平衡反馈回路）是寻求目标的结构——它比较“现状”和“目标”，出现差距就采取行动去缩小差距，
从而让系统稳定在目标附近、抵抗变化。书中例子：房间恒温器（低于设定温度就加热，到了就停）；一杯热咖啡逐渐变凉到室温，
差距越小、变化越慢。要让系统稳定在新的水平，往往要改变回路的目标（设定值），而不只是一次次用力推它。
"""

from adler import kit as K
from adler.core import Big, Card, Custom, Fig, Icon, Label, Rays, Spark
from maoxuan.art_c import tally
from maoxuan.art_d import daily
from scarcity.art import laptop

from . import art_b as A
from .common import BOOK, S, episode, outro, pops

ACC = "#3E8A6E"
G = A.GROUND_Y
ME = dict(role="worker")
LOOP3 = ("现状", "差距", "行动")

SQUARE_SHOT = 18


def build():
    th = dict(x=540, y=800)
    shots = [
        # ---- 钩子 1–8
        S("节食了整整一个月", "灵魂拷问", [
            Custom(daily, x=640, y=760, at=0, enter="pop", n=28, b0=0, step=0.12, title="少吃一点", sfx="pop"),
            Fig(150, G, 280, at=1, pose="fist", mood="happy", **ME, sfx="wood_high"),
        ], draw=A.ground, punch=0.025, flashes=[0], hits=[(2, "shaker", 0.7, "打勾"), (3, "ding", 0.8, "满")]),
        S("真的瘦下来了", "灵魂拷问", [
            Custom(A.rebound, x=540, y=780, at=0, enter="fade", b0=-1, b1=1, kmax=0.4, drop_at=1, set_label="原来"),
            Fig(870, G, 260, at=2, pose="cheer", mood="happy", **ME, sfx="ding"),
        ], hits=[(0, "wood_low", 0.8, "曲线")]),
        S("一停下来", "灵魂拷问", [
            Fig(400, G, 330, at=0, pose="relax", mood="smile", **ME),
            Label("奶茶", 760, 640, 44, at=1, sfx="pop"),
            Label("火锅", 880, 780, 44, at=2, sfx="pop"),
            Label("夜宵", 700, 900, 44, at=3, sfx="pop"),
        ], draw=A.ground),
        S("又胖回去了", "灵魂拷问", [
            Custom(A.rebound, x=540, y=780, at=0, enter="fade", b0=-3, b1=1.5, set_label="原来"),
            Icon("question", 860, 420, 100, color=K.RED, at=2, sfx="rim"),
        ], hits=[(0, "shaker", 0.7, "回弹"), (1, "tom", 0.8, "回来了")], shake=[1]),
        S("又回到老样子", "灵魂拷问", [
            Fig(540, G, 330, at=0, pose="stand", mood="surprised", **ME,
                moves=[(2, dict(pose="sit_sad", mood="sad", dur=0.3, sfx="tom"))]),
            Icon("cloud", 540, 520, 160, color=K.INK2, at=1, sfx="wood_low"),
        ], draw=A.ground),
        pops("不是 意志差 是 【调节回路】", "灵魂拷问", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="不反弹 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("系统之美里说", "系统之美", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《系统之美》|德内拉·梅多斯", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9
        S("", "书中观点", [
            Big("系统会把你", 540, 640, 150, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：核心观点落版"),
            Big("拉回原位", 540, 860, 160, at=1, sfx="kick", sub="书中观点 · 调节回路", sub_size=40, shine=True),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        # ---- 恒温器 10–14
        S("像房间里的恒温器", "书中例子 · 恒温器", [
            Custom(A.thermostat, **th, at=0, enter="fade", t0=22, target=22),
            Spark(340, 690, at=2, sfx="ding"),
        ], hits=[(0, "wood_low", 0.8, "恒温器"), (1, "pop", 0.7, "设定")]),
        S("冷了，就加热", "书中例子 · 恒温器", [
            Custom(A.thermostat, **th, at=0, enter="none", t0=12, target=22, b0=1, b1=6),
        ], hits=[(0, "rim", 0.8, "变冷"), (1, "pop", 0.8, "暖气开"), (2, "shaker", 0.6, "升温")]),
        S("到了，就停下", "书中例子 · 恒温器", [
            Custom(A.thermostat, **th, at=0, enter="none", t0=19, target=22, b0=-1, b1=2),
            Label("停", 860, 460, 50, at=2, sfx="ding", fill=K.GREEN),
        ], hits=[(0, "shaker", 0.6, "升温")]),
        S("比一比，再纠正", "书中观点 · 调节回路", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=LOOP3, b0=0, step=1, R=260),
        ], hits=[(0, "pop", 0.8, "现状"), (1, "pop", 0.8, "差距"), (2, "pop", 0.8, "行动"), (3, "wood_high", 0.7, "回到现状")]),
        pops("有差距 就 【纠正】", "书中观点 · 调节回路", size=150, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 咖啡 15–18
        S("热咖啡会变凉", "书中例子 · 咖啡", [
            Custom(A.coffee, x=520, y=760, at=0, enter="pop", b0=0, b1=4, sfx="pop"),
        ], hits=[(1, "shaker", 0.6, "冒热气"), (3, "pop", 0.7, "变凉")]),
        S("一直凉到室温", "书中例子 · 咖啡", [
            Custom(A.coffee, x=520, y=760, at=0, enter="none", b0=-4, b1=3),
            Label("不再变", 300, 450, 44, at=2, sfx="ding", fill=K.INK2),
        ], hits=[(0, "shaker", 0.5, "降温")]),
        S("差距越小，变得越慢", "书中例子 · 咖啡", [
            Card("差距大|变得快", 300, 760, 50, at=0, sfx="pop"),
            Card("差距小|变得慢", 780, 760, 50, at=1, sfx="pop"),
            Icon("water", 300, 540, 100, color=A.WARM, at=2, sfx="wood_high"),
            Icon("water", 780, 540, 100, color=A.COOL, at=3, sfx="wood_high"),
        ]),
        S("这就是调节回路", "书中观点 · 调节回路", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=LOOP3, b0=-6, step=1, R=260),
            Custom(A.loop_sign, x=540, y=780, at=0, enter="none", at_b=1, text="调"),
        ], hits=[(1, "kick", 0.9, "调"), (2, "ding", 0.7, "稳")], flashes=[1]),
        # ---- 落到身体 19–24
        S("身体像个恒温器", "打个比方", [
            Custom(A.rebound, x=650, y=760, at=0, enter="fade", b0=-6, b1=-6, set_label="身体的设定"),
            Fig(110, G, 260, at=1, pose="point", mood="open", **ME, sfx="pop"),
        ], draw=A.ground, hits=[(0, "wood_low", 0.8, "曲线"), (2, "ding", 0.7, "设定")]),
        S("你使劲往下压", "打个比方", [
            Custom(A.rebound, x=540, y=780, at=0, enter="none", b0=-1, b1=2, kmax=0.4, drop_at=2),
        ], hits=[(0, "shaker", 0.7, "往下"), (1, "shaker", 0.7, "往下")]),
        S("一松手，弹回来", "打个比方", [
            Custom(A.rebound, x=540, y=780, at=0, enter="none", b0=-3.2, b1=3),
        ], hits=[(1, "tom", 0.8, "弹回"), (2, "tom", 0.8, "弹回")], shake=[1]),
        S("作息习惯也一样", "打个比方", [
            Icon("clock", 270, 760, 170, color=K.INK2, at=0, sfx="pop"),
            Icon("phone", 540, 760, 170, color=K.INK2, at=1, sfx="pop"),
            Icon("sun", 810, 760, 170, color=K.GOLD, at=2, sfx="pop"),
            Label("被拉回", 540, 1000, 46, at=3, sfx="rim", fill=K.RED),
        ]),
        S("回路一直在工作", "书中观点 · 调节回路", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=LOOP3, b0=-6, step=1, R=260, spin_at=1),
            Custom(A.loop_sign, x=540, y=780, at=0, enter="none", at_b=-2, text="调"),
        ], hits=[(1, "shaker", 0.7, "转"), (2, "shaker", 0.7, "转")]),
        S("那怎么办？", "书中观点", [
            Fig(540, G, 330, at=0, pose="think", mood="worried", **ME),
            Icon("question", 360, 520, 90, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 720, 480, 110, color=K.RED, at=2, sfx="wood_high"),
        ], draw=A.ground),
        # ---- 二次钩子 25–29
        S("关键在设定值", "书中观点 · 改目标", [
            Big("设定值", 540, 720, 200, at=0, sfx="kick", rays=True, glow=True, spark=True),
            Icon("key", 540, 470, 120, color=K.GOLD, at=2, sfx="ding"),
        ], punch=0.03, flashes=[0], shake=[0]),
        S("光猛拧暖气没用", "书中观点 · 改目标", [
            Custom(A.thermostat, **th, at=0, enter="fade", t0=16, target=22, b0=0, b1=9),
            Icon("cross", 860, 440, 110, color=K.RED, at=2, sfx="rim"),
        ], hits=[(0, "pop", 0.7, "拧"), (1, "pop", 0.7, "拧")]),
        S("要改设定值", "书中观点 · 改目标", [
            Custom(A.thermostat, **th, at=0, enter="fade", t0=22, target=26, b0=1, b1=3.8),
            Spark(340, 650, at=1, sfx="ding"),
        ], hits=[(0, "pop", 0.8, "改设定"), (2, "shaker", 0.6, "升温")]),
        S("系统才稳在新处", "书中观点 · 改目标", [
            Custom(A.thermostat, **th, at=0, enter="none", t0=25, target=26, b0=-1, b1=1),
            Label("稳了", 860, 460, 50, at=2, sfx="ding", fill=K.GREEN),
        ], hits=[(0, "shaker", 0.5, "稳")]),
        pops("改 【目标】 系统 才跟着变", "一句话", size=130, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        # ---- 当下 30–35
        S("今天：突击赶工", "当下 · 现象", [
            Custom(laptop, x=700, y=720, at=0, enter="pop", w=420, h=270, title="项目", p0=0.2, p1=1, b0=0, b1=3,
                   sfx="pop"),
            Fig(250, G, 300, at=1, pose="fist", mood="angry", **ME, sfx="wood_high"),
        ], draw=A.ground),
        S("忙完马上松懈", "当下 · 现象", [
            Fig(540, G, 330, at=0, pose="relax", mood="smile", **ME,
                moves=[(2, dict(pose="sit", dur=0.3, sfx="wood_low"))]),
            Icon("phone", 820, 600, 130, color=K.INK2, at=1, sfx="pop"),
        ], draw=A.ground),
        S("早起只坚持几天", "当下 · 现象", [
            Custom(tally, x=540, y=780, at=0, enter="pop", n=14, b0=0, step=0.5, quit=3, quit_n=4, title="早起打卡",
                   sfx="pop"),
        ], hits=[(1, "ding", 0.6, "打勾"), (3, "rim", 1.0, "断了")]),
        S("又回到老作息", "当下 · 现象", [
            Fig(400, G, 330, at=0, pose="sad", mood="sad", **ME),
            Icon("clock", 760, 600, 170, color=K.INK2, at=1, sfx="wood_high"),
            Icon("cross", 760, 820, 100, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        pops("不改设定 就会 【被拉回】", "一句话", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("先看清是谁在拉", "落到自己", [
            Custom(A.cycle, x=540, y=760, at=0, enter="none", labels=LOOP3, b0=0, step=1, R=240),
        ], hits=[(0, "pop", 0.7, "现状"), (1, "pop", 0.7, "差距"), (2, "pop", 0.7, "行动")]),
        # ---- 4 招 36–41
        S("书里的思路，四招", "不反弹 4 招", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="不反弹 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 找到你的回路", "不反弹 4 招 · 看清结构", [
            Custom(A.cycle, x=620, y=760, at=0, enter="none", labels=LOOP3, b0=0, step=1, R=220),
            Fig(150, G, 280, at=0, pose="point", mood="open", **ME),
        ], draw=A.ground, hits=[(0, "pop", 0.7, "现状"), (1, "pop", 0.7, "差距"), (2, "pop", 0.7, "行动")]),
        S("② 改设定值", "不反弹 4 招 · 改目标", [
            Custom(A.thermostat, **th, at=0, enter="fade", t0=22, target=26, b0=1, b1=3.8),
        ], hits=[(0, "pop", 0.8, "改设定"), (1, "ding", 0.8, "新目标"), (2, "shaker", 0.6, "升温")]),
        S("③ 小步慢调", "不反弹 4 招 · 别猛拧", [
            Card("小步|慢调", 300, 760, 60, at=0, sfx="pop"),
            Card("猛拧|猛松", 780, 760, 60, at=1, sfx="pop"),
            Icon("check", 300, 520, 100, color=K.GREEN, at=2, sfx="ding"),
            Icon("cross", 780, 520, 100, color=K.RED, at=3, sfx="rim"),
        ]),
        S("④ 让新状态成习惯", "不反弹 4 招 · 稳住", [
            Custom(daily, x=540, y=800, at=0, enter="pop", n=21, b0=0, step=0.15, title="新习惯", sfx="pop"),
        ], hits=[(1, "shaker", 0.7, "打勾"), (2, "shaker", 0.7, "打勾"), (3, "ding", 0.9, "稳了")]),
        S("稳在新的位置", "收束", [
            Custom(A.thermostat, x=640, y=800, at=0, enter="fade", t0=26, target=26),
            Fig(150, G, 280, at=1, pose="cheer", mood="happy", **ME, sfx="ding"),
        ], draw=A.ground, hits=[(0, "wood_low", 0.7, "稳"), (2, "pop", 0.7, "好")]),
        # ---- 片尾 42
        outro("你被什么“拉回”过？", "为什么有人越学越快？", "改设定值，才不反弹"),
    ]
    return episode(3, "balancing", "调节回路", "减肥为什么总会反弹？", ACC, shots,
                   [f"{BOOK}：调节回路（平衡反馈）、恒温器、一杯咖啡变凉"],
                   "不改设定值|就会【被拉回】", 8,
                   ["出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)；中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                    "“系统会把你拉回原位”“有差距就纠正”“改目标系统才跟着变”为书中调节回路观点的转述，不是原文引文；恒温器、咖啡变凉为书中例子。",
                    "“身体像个恒温器”“作息习惯也一样”是用书中概念打的比方，不是医学结论；体重曲线、恒温器读数、打卡格均为示意，不代表真实数据；不反弹 4 招为由书中思路引申的小建议，不构成减肥或医疗建议。"],
                   tags="#减肥 #习惯")
