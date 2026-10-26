"""04 增强回路：为什么有人越学越快？（快节奏版：42 镜 × 1 小节）

书中观点（转述）：增强回路（正反馈、自我强化回路）是“越多越多”的结构——存量越大，带来的增长越多，增长又让存量更大，
于是系统呈指数式增长或加速衰退。书中例子：银行账户的利息（复利），钱越多利息越多。增强回路既能形成良性循环，
也能形成恶性循环；早期变化不明显，后期越来越快。
"""

from adler import kit as K
from adler.core import Big, Card, Custom, Fig, Icon, Label, Rays, Spark
from maoxuan.art_c import tally
from maoxuan.art_d import daily

from . import art_b as A
from .common import BOOK, S, episode, outro, pops

ACC = "#C0702A"
G = A.GROUND_Y
ME = dict(role="worker")
PEER = dict(role="worker_f", color="#D98E8A", hair="long")
GOOD = ("学得多", "懂得多", "学得快")
BAD = ("刷手机", "没精力", "更想刷")

SQUARE_SHOT = 40


def build():
    shots = [
        # ---- 钩子 1–8
        S("同一年入职", "灵魂拷问", [
            Fig(320, G, 320, at=0, pose="stand", mood="smile", **ME, sfx="pop"),
            Fig(760, G, 310, at=1, pose="wave", mood="happy", face=-1, **PEER, sfx="pop"),
            Label("起点一样", 540, 560, 44, at=2, sfx="ding"),
        ], draw=A.ground, punch=0.025, flashes=[0]),
        S("几年后差距好大", "灵魂拷问", [
            Custom(A.two_curves, x=540, y=780, at=0, enter="fade", b0=0, b1=3.5, lin_label="你", exp_label="她"),
        ], hits=[(0, "wood_low", 0.8, "曲线"), (2, "shaker", 0.7, "拉开"), (3, "rim", 0.9, "差距")]),
        S("她升得飞快", "灵魂拷问", [
            Icon("ladder", 700, 780, 320, color=K.INK2, at=0, sfx="wood_low"),
            Fig(700, 820, 240, at=1, pose="cheer", mood="happy", **PEER, sfx="pop"),
            Icon("crown", 700, 470, 110, color=K.GOLD, at=2, sfx="ding"), Spark(700, 470, at=2),
        ]),
        S("你还在原地", "灵魂拷问", [
            Fig(400, G, 330, at=0, pose="stand", mood="worried", **ME,
                moves=[(2, dict(pose="sad", mood="sad", dur=0.3, sfx="tom"))]),
            Icon("question", 620, 520, 100, color=K.RED, at=1, sfx="rim"),
        ], draw=A.ground),
        S("她也没多聪明", "灵魂拷问", [
            Fig(540, G, 320, at=0, pose="shrug", mood="smile", **PEER),
            Icon("bulb", 330, 520, 120, color=K.INK3, at=1, sfx="pop"),
            Icon("question", 760, 520, 100, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        pops("差别在 有没有 【增强回路】", "灵魂拷问", size=120, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="滚雪球 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("系统之美里说", "系统之美", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《系统之美》|德内拉·梅多斯", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9
        S("", "书中观点", [
            Big("越多", 540, 640, 190, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：核心观点落版"),
            Big("就越多", 540, 860, 170, at=1, sfx="kick", sub="书中观点 · 增强回路", sub_size=40, shine=True),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        # ---- 复利与雪球 10–15
        S("像银行的复利", "书中例子 · 复利", [
            Custom(A.growth_bars, x=540, y=780, at=0, enter="none", n=8, b0=0, step=0.4, label="复利"),
        ], hits=[(0, "pop", 0.7, "第一根"), (1, "pop", 0.7, "长"), (2, "pop", 0.7, "长"), (3, "ding", 0.9, "猛长")]),
        S("利息再生利息", "书中例子 · 复利", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=("本金", "利息", "更多本金"), b0=0, step=1, R=260),
            Custom(A.loop_sign, x=540, y=780, at=0, enter="none", at_b=3, text="增"),
        ], hits=[(0, "pop", 0.7, "本金"), (1, "pop", 0.7, "利息"), (2, "pop", 0.7, "更多"), (3, "kick", 0.9, "增")]),
        S("越到后面越快", "书中例子 · 复利", [
            Custom(A.growth_bars, x=540, y=780, at=0, enter="none", n=10, b0=0, step=0.3, rate=1.5),
        ], hits=[(0, "shaker", 0.6, "长"), (2, "shaker", 0.7, "长"), (3, "ding", 0.9, "飞起来")]),
        S("滚雪球也一样", "打个比方 · 滚雪球", [
            Custom(A.snowball, x=540, y=780, at=0, enter="fade", b0=0, b1=3.8),
        ], hits=[(0, "wood_low", 0.7, "推"), (1, "shaker", 0.6, "滚"), (2, "shaker", 0.7, "滚"), (3, "kick", 0.9, "变大")]),
        pops("自己 推动 【自己】", "书中观点 · 增强回路", size=150, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("这叫增强回路", "书中观点 · 增强回路", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=("存量", "增长", "更大存量"), b0=-6, step=1, R=260,
                   spin_at=1),
            Custom(A.loop_sign, x=540, y=780, at=0, enter="none", at_b=1, text="增"),
        ], hits=[(1, "kick", 0.9, "增"), (2, "shaker", 0.7, "转")], flashes=[1]),
        # ---- 学习 16–20
        S("学得越多，懂得越多", "落到学习", [
            Custom(A.cycle, x=620, y=760, at=0, enter="none", labels=GOOD, b0=0, step=1, R=220),
            Fig(150, G, 280, at=0, pose="point", mood="happy", **PEER),
        ], draw=A.ground, hits=[(0, "pop", 0.7, "学"), (1, "pop", 0.7, "懂"), (2, "pop", 0.7, "快")]),
        S("懂得多，学更快", "落到学习", [
            Custom(A.cycle, x=620, y=760, at=0, enter="none", labels=GOOD, b0=-6, step=1, R=220, spin_at=0),
            Custom(A.loop_sign, x=620, y=760, at=0, enter="none", at_b=1, text="增"),
            Fig(150, G, 280, at=0, enter="none", pose="cheer", mood="happy", **PEER),
        ], draw=A.ground, hits=[(0, "shaker", 0.7, "转"), (1, "kick", 0.9, "增")]),
        S("先慢，后快", "书中观点 · 先慢后快", [
            Custom(A.two_curves, x=540, y=780, at=0, enter="fade", b0=0, b1=3.5),
        ], hits=[(0, "wood_low", 0.8, "曲线"), (2, "shaker", 0.7, "抬头"), (3, "ding", 0.9, "飞起来")]),
        S("前期几乎看不出", "书中观点 · 先慢后快", [
            Custom(A.growth_bars, x=540, y=780, at=0, enter="none", n=10, b0=0, step=0.15, rate=1.5),
            Label("看不出", 330, 600, 46, at=2, sfx="rim", fill=K.RED),
        ], hits=[(0, "pop", 0.6, "长"), (1, "pop", 0.6, "长")]),
        S("很多人就在这放弃", "落到学习", [
            Custom(tally, x=640, y=760, at=0, enter="pop", n=14, b0=0, step=0.5, quit=3, quit_n=4, title="学习打卡",
                   sfx="pop"),
            Fig(150, G, 260, at=3, pose="sad", mood="sad", **ME, sfx="tom"),
        ], draw=A.ground, hits=[(1, "ding", 0.6, "打勾")]),
        # ---- 二次钩子 21–26
        S("但它也能反着转", "书中观点 · 恶性循环", [
            Big("反着转", 540, 720, 200, at=0, sfx="kick", rays=True, glow=True, spark=True),
            Icon("cross", 540, 470, 110, color=K.RED, at=2, sfx="rim"),
        ], punch=0.03, flashes=[0], shake=[0]),
        S("越刷越不想学", "书中观点 · 恶性循环", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=BAD, b0=0, step=1, R=260),
            Custom(A.loop_sign, x=540, y=780, at=0, enter="none", at_b=3, text="增", color=K.RED),
        ], hits=[(0, "pop", 0.7, "刷"), (1, "pop", 0.7, "累"), (2, "pop", 0.7, "更刷"), (3, "rim", 0.9, "恶性")]),
        S("越忙越没空学", "书中观点 · 恶性循环", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=("太忙", "不学", "效率低"), b0=0, step=1, R=260),
            Custom(A.loop_sign, x=540, y=780, at=0, enter="none", at_b=3, text="增", color=K.RED),
        ], hits=[(0, "pop", 0.7, "忙"), (1, "pop", 0.7, "不学"), (2, "pop", 0.7, "低效"), (3, "rim", 0.9, "恶性")]),
        pops("好的 坏的 都会 【越滚越大】", "书中观点 · 增强回路", size=120, flash=3,
             extra=[Rays(540, 780, 620, at=3, alpha=0.2)]),
        S("关键是往哪转", "落到自己", [
            Fig(540, G, 330, at=0, pose="think", mood="calm", **ME),
            Card("向上转", 260, 620, 50, at=1, sfx="pop"),
            Card("向下转", 820, 620, 50, at=2, sfx="pop"),
            Icon("check", 260, 470, 90, color=K.GREEN, at=3, sfx="ding"),
        ], draw=A.ground),
        S("小差距会被放大", "书中观点 · 先慢后快", [
            Custom(A.two_curves, x=540, y=780, at=0, enter="fade", b0=0, b1=3.5, lin_label="晚起步", exp_label="早起步"),
        ], hits=[(0, "wood_low", 0.8, "曲线"), (2, "shaker", 0.7, "拉开"), (3, "ding", 0.9, "放大")]),
        # ---- 当下 27–34
        S("今天：下班就刷", "当下 · 现象", [
            Fig(400, G, 320, at=0, pose="sit", mood="smile", **ME),
            Icon("phone", 660, 760, 150, color=K.INK2, at=1, sfx="pop"),
            Label("再刷一个", 720, 560, 40, at=2, sfx="pop"),
        ], draw=A.ground),
        S("越刷越没劲", "当下 · 现象", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=BAD, b0=-6, step=1, R=260, spin_at=0),
            Custom(A.loop_sign, x=540, y=780, at=0, enter="none", at_b=1, text="增", color=K.RED),
        ], hits=[(0, "shaker", 0.7, "转"), (1, "rim", 0.9, "恶性"), (2, "shaker", 0.6, "转")]),
        S("同事每天学一点", "当下 · 现象", [
            Fig(250, G, 290, at=0, pose="give", mood="smile", **PEER),
            Custom(daily, x=680, y=760, at=0, enter="pop", n=21, b0=1, step=0.12, title="每天一点", cw=80, sfx="pop"),
        ], draw=A.ground, hits=[(2, "shaker", 0.6, "打勾"), (3, "ding", 0.8, "满")]),
        S("后来判若两人", "当下 · 现象", [
            Custom(A.two_curves, x=540, y=780, at=0, enter="fade", b0=0, b1=3.5, lin_label="刷手机", exp_label="每天学"),
        ], hits=[(0, "wood_low", 0.8, "曲线"), (2, "shaker", 0.7, "拉开"), (3, "rim", 0.9, "差距")]),
        S("差距是滚出来的", "当下 · 现象", [
            Custom(A.snowball, x=540, y=780, at=0, enter="fade", b0=0, b1=3.8, label="差距"),
        ], hits=[(1, "shaker", 0.6, "滚"), (2, "shaker", 0.7, "滚"), (3, "kick", 0.9, "变大")]),
        pops("先让 回路 【转起来】", "一句话", size=140, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("转起来就省力", "落到自己", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=GOOD, b0=-6, step=1, R=260, spin_at=0),
            Custom(A.loop_sign, x=540, y=780, at=0, enter="none", at_b=1, text="增"),
        ], hits=[(0, "shaker", 0.7, "转"), (1, "kick", 0.9, "增"), (2, "ding", 0.7, "省力")]),
        S("难的是起步", "落到自己", [
            Fig(540, G, 330, at=0, pose="stand", mood="calm", **ME,
                moves=[(2, dict(pose="fist", mood="happy", dur=0.25, sfx="wood_high"))]),
            Icon("flag", 820, 620, 140, color=ACC, at=1, sfx="pop"),
        ], draw=A.ground),
        # ---- 4 招 35–41
        S("书里的思路，四招", "滚雪球 4 招", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="滚雪球 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 找到你的雪球", "滚雪球 4 招 · 选对回路", [
            Custom(A.snowball, x=600, y=780, at=0, enter="fade", b0=0, b1=6, label="核心技能"),
            Fig(140, G, 260, at=1, pose="point", mood="happy", **ME, sfx="pop"),
        ], draw=A.ground, hits=[(0, "wood_low", 0.7, "雪球"), (2, "ding", 0.8, "就它")]),
        S("② 让它每天滚", "滚雪球 4 招 · 每天一点", [
            Custom(daily, x=540, y=800, at=0, enter="pop", n=21, b0=0, step=0.15, title="每天滚一点", sfx="pop"),
        ], hits=[(1, "shaker", 0.7, "打勾"), (2, "shaker", 0.7, "打勾"), (3, "ding", 0.9, "满")]),
        S("③ 收益再投进去", "滚雪球 4 招 · 复利", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=("学", "用", "再学"), b0=0, step=1, R=260),
            Custom(A.loop_sign, x=540, y=780, at=0, enter="none", at_b=3, text="增"),
        ], hits=[(0, "pop", 0.7, "学"), (1, "pop", 0.7, "用"), (2, "pop", 0.7, "再学"), (3, "kick", 0.9, "增")]),
        S("④ 切断坏回路", "滚雪球 4 招 · 止损", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=BAD, b0=-6, step=1, R=260),
            Icon("cross", 540, 780, 260, color=K.RED, at=1, sfx="kick"),
        ], hits=[(0, "shaker", 0.6, "转"), (2, "rim", 0.8, "断")], shake=[1]),
        S("熬过平的那段", "滚雪球 4 招 · 耐心", [
            Custom(A.two_curves, x=540, y=780, at=0, enter="fade", b0=0, b1=3.5, lin_label="原地", exp_label="熬过去"),
        ], hits=[(0, "wood_low", 0.8, "曲线"), (2, "shaker", 0.7, "抬头"), (3, "ding", 0.9, "起飞")]),
        S("雪球越滚越大", "收束", [
            Custom(A.snowball, x=680, y=780, at=0, enter="fade", b0=-1, b1=3.5, label="你的能力"),
            Fig(110, G, 260, at=2, pose="cheer", mood="happy", **ME, sfx="ding"),
        ], draw=A.ground, hits=[(0, "shaker", 0.6, "滚"), (3, "kick", 0.8, "大")]),
        # ---- 片尾 42
        outro("你的“雪球”是什么？", "为什么越着急，越容易出乱子？", "先慢后快，越滚越大"),
    ]
    return episode(4, "reinforcing", "增强回路", "为什么有人越学越快？", ACC, shots,
                   [f"{BOOK}：增强回路（自我强化）、银行复利"],
                   "越学越会|是【增强回路】", 8,
                   ["出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)；中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                    "“越多就越多”“自己推动自己”“好的坏的都会越滚越大”“先慢后快”为书中增强回路观点的转述，不是原文引文；银行复利为书中例子，滚雪球是常用比方。",
                    "柱状图、曲线、雪球大小、打卡格均为示意，不代表真实数据；同事升职、刷手机、学习等为今日化情境示意；滚雪球 4 招为由书中思路引申的小建议。"],
                   tags="#学习 #成长")
