"""10 杠杆点：想改变，该从哪里下手？（快节奏版：42 镜 × 1 小节，系列最后一讲）

出处：Donella H. Meadows (1999), Leverage Points: Places to Intervene in a System（《系统之美》第六章亦有收录与展开）。
文中列出 12 个杠杆点（中文为意译，12 最弱 → 1 最强）：12 常数、参数、数字；11 缓冲的大小；10 存量流量的结构；
9 延迟的长短；8 调节回路的强度；7 增强回路的强度；6 信息流的结构；5 系统的规则；4 增加、改变、演化或自组织系统结构的能力；
3 系统的目标；2 系统赖以产生的心智模式（范式）；1 超越范式的能力。文中说参数在强力干预清单上排在最后，
并指出人们常常找对了杠杆点却朝错误的方向推。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Shot, Spark, W
from adler.core import G as Gc
from maoxuan.art import notebook

from . import art_d as A
from .build import PLAN
from .common import BOOK, S, episode, pops

ACC = "#B8322A"
G = A.GROUND_Y
ME = dict(role="worker")
SQUARE_SHOT = 9


def final_outro() -> Shot:
    """系列片尾：评论区回顾问题 + “系列完结”；最后一击落在原曲最后一个强拍。"""

    def draw(g: Gc):
        c = g.c
        with K.at(c, W / 2, 620, 0, 1.0):
            K.icon(c, "book", 0, 0, 240, A.RED, g.p(0, 0.4), 0.8, 0, 1, 0.0, g.acc2)
        K.card(c, W / 2, 900, 900, 150, K.PAPER, g.p(1, 0.3), r=30, accent=g.acc)
        K.text(c, "十讲里，你最想用哪个？", W / 2, 905, 46, "serif_black", K.INK, g.p(1, 0.3))
        ap = g.p(2, 0.4)
        K.text(c, "系统之美 · 10讲", W / 2, 1060, 34, "sans_medium", K.INK3, ap)
        K.text(c, "系列完结 · 谢谢一路同行", W / 2, 1130, 50, "serif_black", g.acc, ap)

    return Shot(1, "收藏合集，常翻常新", "评论区见", [], over=draw, text_beat=0, note="系列片尾：回顾互动",
                hits=[(0, "cymbal", 0.5, "片尾落版"), (1, "pop", 0.8, "问题卡"), (2, "wood_high", 0.7, "系列完结"),
                      (4, "kick", 0.55, "原曲最后一击")])


def lad(text, tag, hi=(), marker=None, arrow=None, extra=(), hits=None, **kw):
    """十二级阶梯镜头：hi 为高亮等级，阶梯整体在第 0 拍已在画面上。"""
    return S(text, tag, [Custom(A.ladder12, x=540, y=780, at=0, enter="none", b0=-9, hi=hi, marker=marker,
                                arrow=arrow)] + list(extra),
             hits=hits if hits is not None else [(0, "wood_high", 0.8, "高亮"), (1, "pop", 0.7, "人物")], **kw)


def build():
    shots = [
        # ---- 钩子 1–8
        S("想改变，买新本子", "灵魂拷问", [
            Fig(330, G, 330, at=0, pose="cheer", mood="happy", **ME),
            Icon("book", 760, 640, 200, color=ACC, at=1, sfx="pop"), Spark(760, 640, at=1),
        ], draw=A.ground, punch=0.025, flashes=[0], hits=[(2, "wood_high", 0.7, "翻开")]),
        S("又下了个新软件", "灵魂拷问", [
            Fig(330, G, 330, at=0, pose="point", mood="smile", **ME),
            Icon("phone", 760, 640, 170, color=K.INK2, at=1, sfx="pop"),
            Spark(760, 640, at=2, sfx="ding"),
        ], draw=A.ground),
        S("闹钟调早一点", "灵魂拷问", [
            Icon("clock", 540, 680, 260, color=K.INK2, at=0, sfx="pop"),
            Label("早一点", 540, 920, 50, at=2, sfx="wood_high"),
        ]),
        S("过了很久：没变", "灵魂拷问", [
            Fig(540, G, 330, at=0, pose="shrug", mood="worried", **ME),
            Icon("cross", 800, 520, 120, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground, hits=[(0, "tom", 0.8, "没变")]),
        S("力气全用在小处", "灵魂拷问", [
            Custom(A.knob, x=540, y=760, at=0, enter="pop", b0=0, label="小细节", sfx="pop"),
        ], hits=[(1, "wood_high", 0.7, "拧"), (2, "wood_high", 0.7, "拧"), (3, "rim", 0.8, "没反应")]),
        pops("不是 不努力 是 【没找对点】", "灵魂拷问", size=130, flash=3, extra=[Rays(540, 780, 620, at=3, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="找杠杆 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("梅多斯有篇文章", "系统之美", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《杠杆点》|梅多斯 · 一九九九", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–10
        S("", "书中观点", [
            Big("杠杆点", 540, 700, 210, at=0, sfx="kick", sub="干预系统的位置", sub_size=44, rays=True,
                glow=True, shine=True, spark=True, note="drop：概念落版"),
            Spark(540, 700, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0], shake=[0]),
        S("小力气撬动大石头", "书中观点 · 杠杆点", [
            Custom(A.lever, x=540, y=760, at=0, enter="fade", push=1, label="问题"),
        ], draw=A.ground, hits=[(0, "wood_low", 0.8, "杠杆"), (1, "kick", 0.9, "压下"), (2, "ding", 0.9, "撬起")],
            shake=[1]),
        # ---- 十二级 11–22
        S("她列了十二个", "梅多斯 · 十二个杠杆点", [
            Custom(A.ladder12, x=540, y=780, at=0, enter="none", b0=0, step=0.25),
        ], hits=[(0, "pop", 0.7, "第一级"), (1, "pop", 0.7, "往上"), (2, "pop", 0.7, "往上"), (3, "ding", 0.9, "第十二级")]),
        lad("最弱：调数字", "十二个杠杆点 · 第十二", hi=12, marker=1),
        lad("排在清单最后", "十二个杠杆点 · 第十二", hi=12,
            extra=[Label("最弱", 860, 1120, 44, at=1, sfx="rim", fill=K.RED)]),
        lad("往上：缓冲与结构", "十二个杠杆点 · 十一到十", hi=(11, 10), marker=1),
        lad("延迟与反馈回路", "十二个杠杆点 · 九到七", hi=(9, 8, 7), marker=1),
        lad("信息：谁知道什么", "十二个杠杆点 · 第六", hi=6, marker=1),
        lad("规则：奖与罚", "十二个杠杆点 · 第五", hi=5, marker=1),
        lad("能自己长出新结构", "十二个杠杆点 · 第四", hi=4, marker=1),
        lad("系统的目标", "十二个杠杆点 · 第三", hi=3, marker=1),
        lad("范式：底层信念", "十二个杠杆点 · 第二", hi=2, marker=1),
        lad("最强：超越范式", "十二个杠杆点 · 第一", hi=1, marker=1, arrow=2,
            hits=[(0, "wood_high", 0.8, "高亮"), (1, "pop", 0.7, "人物"), (2, "ding", 1.0, "越有力")], flashes=[2]),
        pops("越往上 越难 也 【越有力】", "一句话", size=130, flash=3, extra=[Rays(540, 780, 620, at=3, alpha=0.2)]),
        # ---- 二次钩子 23–26
        S("但要小心", "书中观点 · 推反方向", [
            Fig(540, G, 340, at=0, pose="block", mood="worried", **ME),
            Icon("question", 760, 480, 120, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground, punch=0.025, flashes=[2], hits=[(0, "tom", 0.8, "停")]),
        S("常常推反了方向", "书中观点 · 推反方向", [
            Custom(A.lever, x=540, y=760, at=0, enter="fade", push=1, wrong=True, label="问题"),
        ], draw=A.ground, hits=[(0, "wood_low", 0.8, "杠杆"), (1, "kick", 0.9, "推反"), (2, "tom", 0.8, "石头压回")],
            shake=[1]),
        S("越用力，越糟", "书中观点 · 推反方向", [
            Custom(A.lever, x=540, y=760, at=0, enter="none", push=-9, wrong=True, label="问题"),
            Icon("cross", 820, 440, 110, color=K.RED, at=1, sfx="rim"),
            Icon("cross", 260, 440, 90, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        S("大家都盯着数字", "书中观点 · 参数", [
            Custom(A.knob, x=540, y=640, at=0, enter="pop", b0=0, label="数字", sfx="pop"),
            Custom(A.ink_crowd, x=540, y=G + 80, at=1, enter="fade", roles=("worker", "boss", "worker_f"), spread=460,
                   s=200, sfx="wood_low"),
        ], hits=[(2, "wood_high", 0.7, "拧"), (3, "rim", 0.8, "没反应")]),
        # ---- 当下 27–32
        S("今天：想多存钱", "当下 · 例子", [
            Fig(330, G, 330, at=0, pose="fist", mood="happy", **ME),
            Card("存钱", 760, 620, 70, at=1, sfx="pop"),
            Icon("target", 760, 860, 140, color=ACC, at=2, sfx="ding"),
        ], draw=A.ground),
        S("只会少喝杯奶茶", "当下 · 调数字", [
            Custom(A.knob, x=540, y=740, at=0, enter="pop", b0=0, label="奶茶", sfx="pop"),
            Label("第十二级", 540, 460, 44, at=2, sfx="rim", fill=K.INK2),
        ], hits=[(1, "wood_high", 0.7, "拧"), (3, "rim", 0.8, "没反应")]),
        S("改规则：先存后花", "当下 · 改规则", [
            Card("工资", 220, 720, 50, at=0, sfx="pop"),
            Card("先存", 540, 720, 50, at=1, sfx="pop"),
            Card("再花", 860, 720, 50, at=2, sfx="pop"),
            Label("第五级", 540, 480, 44, at=3, sfx="ding"),
        ]),
        S("让钱看得见", "当下 · 信息流", [
            Icon("phone", 360, 700, 200, color=K.INK2, at=0, sfx="pop"),
            Card("每笔|看得见", 740, 700, 52, at=1, sfx="pop"),
            Label("第六级", 540, 460, 44, at=2, sfx="ding"),
        ]),
        S("想清为啥存钱", "当下 · 目标", [
            Fig(330, G, 330, at=0, pose="think", mood="calm", **ME,
                moves=[(2, dict(pose="cheer", mood="happy", dur=0.25, sfx="ding"))]),
            Icon("house", 760, 640, 200, color=ACC, at=1, sfx="pop"),
            Label("第三级", 760, 440, 44, at=2),
        ], draw=A.ground),
        pops("改规则 比 改数字 【更有用】", "一句话", size=120, flash=3, extra=[Rays(540, 780, 620, at=3, alpha=0.2)]),
        # ---- 4 招 33–37
        S("杠杆这样找", "找杠杆 4 招", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="找杠杆 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 先画出整张图", "找杠杆 4 招 · 小建议", [
            Custom(A.loop_diagram, x=540, y=760, at=0, enter="fade", b0=0, step=0.5, loop="R",
                   names=("目标", "规则", "信息", "数字")),
        ], hits=[(0, "pop", 0.7, "节点"), (1, "pop", 0.7, "节点"), (2, "ding", 0.9, "成图")]),
        S("② 少拧数字旋钮", "找杠杆 4 招 · 小建议", [
            Custom(A.knob, x=540, y=740, at=0, enter="pop", b0=0, label="数字", sfx="pop"),
            Icon("cross", 390, 520, 110, color=K.RED, at=2, sfx="rim"),
        ]),
        lad("③ 改规则和信息", "找杠杆 4 招 · 小建议", hi=(6, 5), marker=1),
        lad("④ 问清真正的目标", "找杠杆 4 招 · 小建议", hi=3, marker=1),
        # ---- 系列回顾 38–41
        S("十讲，回头看看", "系列回顾", [
            Custom(A.chips, x=540, y=820, at=0, enter="none", b0=0, step=0.25, items=[(k, c) for k, c, _ in PLAN]),
        ], hits=[(0, "pop", 0.7, "第一讲"), (1, "pop", 0.7, "回顾"), (2, "ding", 0.9, "第十讲")]),
        pops("看见 【结构】 就不慌", "一句话", size=150, flash=1, extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        S("遇到难题先画图", "落到自己", [
            Fig(300, G, 320, at=0, pose="think", mood="calm", **ME),
            Custom(notebook, x=720, y=700, at=1, enter="pop", b0=1, step=0.5, lines=("存量：", "回路：", "杠杆："),
                   sfx="pop"),
        ], draw=A.ground, hits=[(2, "shaker", 0.7, "写"), (3, "ding", 0.8, "写完")]),
        S("再找那根杠杆", "落到自己", [
            Custom(A.lever, x=540, y=760, at=0, enter="fade", push=1, label="难题"),
            Spark(800, 560, at=2, sfx="ding"),
        ], draw=A.ground, hits=[(0, "wood_low", 0.8, "杠杆"), (1, "kick", 0.9, "撬起")], shake=[1]),
        # ---- 片尾 42
        final_outro(),
    ]
    return episode(10, "leverage", "杠杆点", "想改变，该从哪里下手？", ACC, shots,
                   ["Donella H. Meadows (1999), Leverage Points: Places to Intervene in a System",
                    f"{BOOK}第六章 · 杠杆点"],
                   "找对地方|【小力】撬大石", 8,
                   ["十二个杠杆点为 Meadows (1999) Leverage Points: Places to Intervene in a System 的意译：12 Constants, "
                    "parameters, numbers；11 The sizes of buffers；10 The structure of material stocks and flows；9 The lengths "
                    "of delays；8 The strength of negative feedback loops；7 The gain around driving positive feedback loops；"
                    "6 The structure of information flows；5 The rules of the system；4 The power to add, change, evolve, or "
                    "self-organize system structure；3 The goals of the system；2 The mindset or paradigm；1 The power to "
                    "transcend paradigms。阶梯上的中文标签为缩写意译。",
                    "“参数排在最后”转述自原文 Parameters are dead last on my list of powerful interventions；“推反方向”转述自文中"
                    "关于人们常把杠杆往错误方向推的论述。中译本《系统之美》（邱昭良译，浙江人民出版社 2012）；上屏均为转述。",
                    "存钱例子与各级对应（奶茶=参数、先存后花=规则、记账=信息流、为啥存=目标）为创作者示意；4 招为小建议。"],
                   tags="#改变 #方法论")
