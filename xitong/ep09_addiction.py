"""09 上瘾：为什么越熬夜越离不开咖啡？（快节奏版：42 镜 × 1 小节）

书中观点（转述）：梅多斯《系统之美》第五章“系统陷阱”之一“上瘾”（addiction，也称转嫁负担 shifting the burden）——
用一个外部干预去压住症状，系统自身解决问题的能力反而萎缩，于是需要越来越多的干预，越来越离不开它。
书中给出的出路：一开始就避免只治标；已经陷入时，加强系统自身的能力，再逐步撤掉外部干预（撤的过程会难受）。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Spark
from maoxuan.art_c import plateau
from scarcity.art import checklist
from zizhi.art import night

from . import art_d as A
from .common import BOOK, S, episode, outro, pops

ACC = "#4F6D8F"
G = A.GROUND_Y
ME = dict(role="worker")
BOSS = dict(role="boss")
SQUARE_SHOT = 15


def build():
    shots = [
        # ---- 钩子 1–8
        S("又熬到深夜", "灵魂拷问", [
            Custom(night, x=540, y=800, at=0, enter="fade"),
            Fig(540, G, 330, at=0, pose="sit", mood="smile", **ME, sfx="wood_low"),
            Icon("phone", 760, 600, 130, color=K.INK2, at=1, sfx="pop"),
            Bubble("再刷一会", 760, 420, 44, at=2, enter="pop", sfx="pop"),
        ], draw=A.ground, punch=0.025, flashes=[0]),
        S("第二天困到不行", "灵魂拷问", [
            Fig(400, G, 330, at=0, pose="sad", mood="sad", **ME),
            Icon("clock", 760, 640, 140, color=K.INK2, at=1, sfx="wood_high"),
            Bubble("好困", 400, 420, 50, at=2, enter="pop", sfx="tom"),
        ], draw=A.ground),
        S("来杯咖啡，满血", "灵魂拷问", [
            Custom(A.cups, x=760, y=700, at=0, enter="none", n=1, b0=0, s=170),
            Fig(330, G, 330, at=0, pose="stand", mood="calm", **ME,
                moves=[(2, dict(pose="cheer", mood="happy", dur=0.25, sfx="ding"))]),
            Spark(330, 500, at=2),
        ], draw=A.ground, hits=[(0, "pop", 0.8, "咖啡")]),
        S("晚上精神，又熬", "灵魂拷问", [
            Custom(night, x=540, y=800, at=0, enter="fade"),
            Fig(540, G, 330, at=0, pose="sit", mood="happy", **ME, sfx="wood_low"),
            Icon("phone", 760, 600, 130, color=K.INK2, at=1, sfx="pop"),
            Icon("clock", 300, 520, 110, color=K.PAPER, at=2, sfx="wood_high"),
        ], draw=A.ground),
        S("第二天：两杯", "灵魂拷问", [
            Custom(A.cups, x=540, y=740, at=0, enter="none", n=2, b0=0, step=1, s=180, gap=260),
            Icon("question", 540, 450, 100, color=K.RED, at=2, sfx="rim"),
        ], hits=[(0, "pop", 0.8, "一杯"), (1, "pop", 0.8, "两杯")]),
        pops("治的是 【困】 不是 【缺觉】", "灵魂拷问", size=130, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="戒掉依赖 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("系统之美讲过", "系统之美", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《系统之美》|梅多斯", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–17
        S("", "书中观点", [
            Big("上瘾", 540, 700, 230, at=0, sfx="kick", sub="书中观点 · 系统陷阱", sub_size=40, rays=True,
                glow=True, shine=True, spark=True, note="drop：概念落版"),
            Spark(540, 700, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0], shake=[0]),
        S("外力压住症状", "书中观点 · 上瘾", [
            Custom(A.press, x=540, y=760, at=0, enter="fade", b=1, label="困"),
        ], hits=[(0, "wood_low", 0.8, "弹簧"), (1, "kick", 0.9, "压下"), (2, "ding", 0.7, "不困了")], shake=[1]),
        S("一松手，更困", "书中观点 · 上瘾", [
            Custom(A.press, x=540, y=760, at=0, enter="none", b=-9, rel=1, label="困"),
            Icon("cross", 820, 460, 100, color=K.RED, at=3, sfx="rim"),
        ], hits=[(1, "tom", 0.9, "弹回更高")], shake=[1]),
        S("自己的本事在退化", "书中观点 · 上瘾", [
            Custom(A.twin_bars, x=540, y=740, at=0, enter="fade", b0=0, b1=3,
                   bars=[("自身能力", 0.8, 0.3, K.GREEN), ("依赖", 0.2, 0.8, ACC)]),
        ], hits=[(0, "wood_low", 0.8, "柱子"), (2, "tom", 0.8, "能力下降"), (3, "tom", 0.8, "依赖上升")]),
        S("只好加大剂量", "书中观点 · 上瘾", [
            Custom(A.cups, x=540, y=740, at=0, enter="none", n=3, b0=0, step=1, s=160, gap=230),
            Fig(900, G, 250, at=2, pose="shrug", mood="worried", face=-1, **ME),
        ], draw=A.ground, hits=[(0, "pop", 0.8, "一杯"), (1, "pop", 0.8, "两杯"), (2, "pop", 0.9, "三杯")]),
        S("越喝越离不开", "书中观点 · 上瘾", [
            Custom(A.loop_diagram, x=540, y=760, at=0, enter="fade", b0=0, step=0.5, loop="R",
                   names=("困", "喝咖啡", "精神", "晚睡")),
        ], hits=[(0, "pop", 0.7, "节点"), (1, "pop", 0.7, "节点"), (2, "kick", 0.9, "R")]),
        pops("治标的药 让 【本事】 退化", "一句话", size=130, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("像拄拐杖", "比喻", [
            Custom(A.crutch_man, x=540, y=G, at=0, enter="rise", s=360),
            Label("拐杖", 760, 820, 40, at=1, sfx="pop"),
            Label("外力", 760, 900, 34, at=2, sfx="wood_high"),
        ], draw=A.ground),
        S("拄久了，腿就软", "比喻", [
            Custom(A.crutch_man, x=540, y=G, at=0, enter="none", s=360, drop=2),
            Icon("cross", 300, 520, 100, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground, hits=[(0, "wood_low", 0.7, "拄着"), (2, "tom", 0.9, "腿软")], shake=[2]),
        # ---- 团队 18–24
        S("团队也会上瘾", "团队里也常见", [
            Custom(A.ink_crowd, x=540, y=G, at=0, enter="fade", roles=("worker", "worker_f", "boss", "worker", "worker_f"),
                   spread=760, s=280, sfx="wood_low"),
            Icon("question", 540, 450, 100, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        S("进度慢，靠加班", "团队里也常见", [
            Fig(760, G, 340, at=0, pose="point", mood="worried", face=-1, **BOSS),
            Bubble("加个班", 560, 520, 50, at=1, enter="pop", sfx="wood_high"),
            Icon("clock", 300, 700, 160, color=K.INK2, at=2, sfx="pop"),
        ], draw=A.ground),
        S("这次赶上了", "团队里也常见", [
            Fig(400, G, 330, at=0, pose="cheer", mood="happy", **BOSS),
            Icon("check", 760, 660, 150, color=K.GREEN, at=1, sfx="ding"), Spark(760, 660, at=1),
        ], draw=A.ground, hits=[(2, "pop", 0.7, "欢呼")]),
        S("流程没改，人更累", "团队里也常见", [
            Custom(A.twin_bars, x=540, y=740, at=0, enter="fade", b0=0, b1=3,
                   bars=[("流程", 0.4, 0.3, K.GREEN), ("加班", 0.3, 0.85, ACC)]),
        ], hits=[(0, "wood_low", 0.8, "柱子"), (2, "tom", 0.8, "加班变多"), (3, "tom", 0.8, "加班变多")]),
        S("下次只能再加班", "团队里也常见", [
            Icon("clock", 300, 720, 140, color=K.INK2, at=0, sfx="pop"),
            Icon("clock", 540, 720, 160, color=K.INK2, at=1, sfx="pop"),
            Icon("clock", 780, 720, 180, color=K.RED, at=2, sfx="pop"),
            Icon("cross", 540, 480, 100, color=K.RED, at=3, sfx="rim"),
        ]),
        S("越来越离不开", "团队里也常见", [
            Custom(A.loop_diagram, x=540, y=760, at=0, enter="fade", b0=0, step=0.5, loop="R",
                   names=("进度慢", "加班", "赶上了", "不改流程")),
        ], hits=[(0, "pop", 0.7, "节点"), (1, "pop", 0.7, "节点"), (2, "kick", 0.9, "R")]),
        pops("症状 压住了 病根 【还在】", "一句话", size=130, flash=3, extra=[Rays(540, 780, 620, at=3, alpha=0.2)]),
        # ---- 二次钩子 · 出路 25–30
        S("那怎么戒？", "书中给的出路", [
            Fig(540, G, 340, at=0, pose="think", mood="worried", **ME),
            Icon("key", 800, 500, 130, color=K.GOLD, at=2, sfx="ding"), Spark(800, 500, at=2),
        ], draw=A.ground, punch=0.025, flashes=[2]),
        S("先找症状从哪来", "书中观点 · 出路", [
            Fig(300, G, 320, at=0, pose="point", mood="calm", **ME),
            Custom(A.magnifier, x=700, y=640, at=1, enter="pop", r=130, sfx="wood_high"),
            Label("缺觉", 700, 860, 46, at=2, sfx="ding", fill=K.RED),
        ], draw=A.ground),
        S("加强系统自己", "书中观点 · 出路", [
            Custom(A.twin_bars, x=540, y=740, at=0, enter="fade", b0=0, b1=3,
                   bars=[("自身能力", 0.3, 0.8, K.GREEN), ("依赖", 0.8, 0.2, ACC)]),
        ], hits=[(0, "wood_low", 0.8, "柱子"), (2, "ding", 0.8, "能力回升"), (3, "ding", 0.8, "依赖下降")]),
        S("拐杖慢慢撤", "书中观点 · 出路", [
            Custom(A.crutch_man, x=540, y=G, at=0, enter="none", s=360, drop=2, weak=False),
            Spark(540, 520, at=2, sfx="ding"),
        ], draw=A.ground, hits=[(0, "wood_low", 0.7, "拄着")]),
        S("撤的时候会难受", "书中观点 · 出路", [
            Fig(540, G, 330, at=0, pose="sad", mood="worried", **ME, moves=[(2, dict(pose="crouch", dur=0.3, sfx="tom"))]),
            Bubble("好难受", 760, 500, 46, at=1, enter="pop", sfx="wood_high"),
        ], draw=A.ground),
        S("撑过去就好了", "书中观点 · 出路", [
            Custom(plateau, x=540, y=760, at=0, enter="fade", b0=0, b1=3, label_at=1, label="难受期", walker="worker",
                   goal=True),
        ], hits=[(0, "wood_low", 0.8, "曲线"), (1, "pop", 0.8, "难受期"), (3, "ding", 0.9, "走出来")]),
        # ---- 当下 31–35
        S("今天：靠闹钟起床", "当下 · 现象", [
            Icon("clock", 300, 700, 150, color=K.RED, at=0, sfx="pop"),
            Icon("clock", 540, 700, 150, color=K.RED, at=1, sfx="pop"),
            Icon("clock", 780, 700, 150, color=K.RED, at=2, sfx="pop"),
        ]),
        S("压力大就刷手机", "当下 · 现象", [
            Fig(400, G, 330, at=0, pose="sit", mood="smile", **ME),
            Icon("phone", 700, 620, 140, color=K.INK2, at=1, sfx="pop"),
            Bubble("刷会儿", 720, 430, 44, at=2, enter="pop", sfx="pop"),
        ], draw=A.ground),
        S("越刷越焦虑", "当下 · 现象", [
            Fig(540, G, 330, at=0, pose="sit_sad", mood="worried", **ME),
            Icon("cloud", 360, 500, 140, color=K.INK2, at=1, sfx="wood_low"),
            Icon("cloud", 720, 480, 170, color=K.INK2, at=2, sfx="wood_low"),
        ], draw=A.ground),
        S("问题还在原地", "当下 · 现象", [
            Card("压力", 540, 700, 90, at=0, sfx="kick"),
            Icon("cross", 540, 900, 100, color=K.RED, at=2, sfx="rim"),
        ], shake=[0]),
        pops("别只压 【症状】 要补 【本事】", "一句话", size=130, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 4 招 36–41
        S("书里给了出路", "戒掉依赖 4 招", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="戒掉依赖 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 先找真正的病根", "戒掉依赖 4 招 · 小建议", [
            Custom(A.magnifier, x=540, y=640, at=0, enter="pop", r=140, sfx="pop"),
            Card("困 ← 缺觉", 540, 900, 52, at=2, sfx="ding"),
        ]),
        S("② 先补睡眠这个本", "戒掉依赖 4 招 · 小建议", [
            Custom(checklist, x=540, y=780, at=0, enter="pop", w=620, title="今晚",
                   items=[("早点睡", True), ("手机放远", True), ("少喝一杯", True)], b0=1, step=1),
        ], hits=[(0, "wood_high", 0.8, "清单"), (1, "ding", 0.7, "勾"), (2, "ding", 0.7, "勾"), (3, "ding", 0.8, "勾")]),
        S("③ 咖啡一天少一杯", "戒掉依赖 4 招 · 小建议", [
            Custom(A.cups, x=540, y=740, at=0, enter="none", n=3, b0=-9, s=160, gap=230),
            Icon("cross", 770, 740, 130, color=K.RED, at=1, sfx="rim"),
            Spark(540, 520, at=2, sfx="ding"),
        ]),
        S("④ 撑过难受那几天", "戒掉依赖 4 招 · 小建议", [
            Custom(plateau, x=540, y=760, at=0, enter="fade", b0=0, b1=3, label_at=1, label="撑住", walker="worker"),
        ], hits=[(0, "wood_low", 0.8, "曲线"), (1, "pop", 0.8, "撑住"), (3, "ding", 0.9, "过去了")]),
        S("靠自己，不靠拐杖", "落到自己", [
            Custom(A.crutch_man, x=540, y=G, at=0, enter="none", s=360, drop=1, weak=False),
            Spark(540, 520, at=1, sfx="ding"),
            Rays(540, 600, 500, at=2, alpha=0.18),
        ], draw=A.ground, hits=[(0, "wood_low", 0.7, "拄着"), (2, "pop", 0.7, "站稳")]),
        # ---- 片尾 42
        outro("你离不开的“拐杖”是什么？", "想改变，该从哪里下手？", "治本，才能不依赖"),
    ]
    return episode(9, "addiction", "上瘾", "为什么越熬夜越离不开咖啡？", ACC, shots,
                   [f"{BOOK}第五章 · 系统陷阱：上瘾（转嫁负担）", "Donella H. Meadows, Thinking in Systems: A Primer (2008)"],
                   "压住症状|【本事】在退化", 8,
                   ["书中观点为转述：Donella H. Meadows, Thinking in Systems: A Primer (2008)，第五章 System Traps 之 "
                    "Addiction / Shifting the Burden to the Intervenor；中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。"
                    "上屏均为转述，不是逐字引文。",
                    "“拐杖”“弹簧”为创作者比喻；回路节点（困→喝咖啡→精神→晚睡）、团队加班回路为对书中机制的通俗化示意。",
                    "咖啡杯数、柱子高低、难受期曲线均为示意，不是数据；4 招中“补睡眠”“每天少一杯”为生活化小建议。"],
                   tags="#熬夜 #习惯")
