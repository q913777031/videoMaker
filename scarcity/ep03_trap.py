"""03 稀缺陷阱：为什么帮人还清债，没多久又欠了？"""

from adler import kit as K
from adler.core import Big, Card, Counter, Custom, Episode, Fig, Glow, Icon, Label, Pops, Rays, Shot, Spark, end_shot

from . import art as A

ACC = "#8E5BA8"
GROUND = A.GROUND_Y
REFS = ["Mullainathan & Shafir (2013). Scarcity: Why Having Too Little Means So Much.",
        "Karlan, Mullainathan & Roth (2019). Debt Traps? Market Vendors and Moneylender Debt "
        "in India and the Philippines. AER: Insights."]


def build() -> Episode:
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("帮他 还清 债|然后 【呢】？", 540, 760, 104, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "有人真的这么做了|结果出人意料", "先说结论", [
            Fig(540, GROUND, 330, at=0, pose="shrug", mood="surprised", hair="short", color=K.OTHER3),
            Icon("question", 760, 520, 110, color=ACC, at=1, sfx="rim"),
            Spark(760, 520, at=1),
        ], draw=A.ground, text_beat=0, note="摊手，问号弹出"),
        Shot(4, "一些小商贩|长期借高息贷款进货", "情境演绎", [
            Fig(330, GROUND, 320, at=0, pose="carry", mood="worried", hair="short", color=K.OTHER3),
            Custom(lambda c, g, t, d: A.basket(c, 0, 0, 220), x=720, y=960, at=2, enter="rise", sfx="wood_low"),
            Custom(A.bill, x=760, y=560, at=4, enter="drop", rot=-5, title="借据", amount="高息", sfx="rim"),
        ], draw=A.ground, note="商贩、果篮与借据"),
        Shot(4, "越缺越借|越借越缺", "原书 · 核心概念", [
            Big("稀缺陷阱", 540, 700, 180, at=0, sfx="kick", sub="Scarcity Trap", rays=True, glow=True, shine=True,
                spark=True, note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "这是一个|会自我加固的循环", "机制示意", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=["缺钱", "借钱", "付利息"], R=270, b0=0, step=2,
                   hi=0, spin_at=7),
        ], hits=[(0, "wood_low", 0.8, "节点：缺钱"), (2, "wood_low", 0.8, "节点：借钱"), (4, "wood_low", 0.8, "节点：付利息"),
                 (7, "rim", 0.9, "循环转起来")], note="三个节点逐个弹出，箭头连成循环"),
        Shot(4, "", "拆东墙补西墙", [
            Pops("拆 东墙|补 【西墙】", 540, 780, 110, at=0, step=2, gap=34),
        ], punch=0.02, flashes=[6], note="逐词弹出"),
        # 二次钩子：真实的大规模实验
        Shot(4, "研究者直接帮上千名商贩|还清了高息债", "研究证据 · Karlan 等 2019", [
            Counter(0, 1000, 540, 640, 200, at=0, land=4, sub="位印度金奈商贩参与实验"),
            Icon("gift", 540, 960, 120, color=ACC, at=5, sfx="wood_high"),
        ], research=True, punch=0.02, note="数字滚动落定"),
        Shot(4, "结果多数人|几周内又借上了", "研究证据 · Karlan 等 2019", [
            Fig(330, GROUND, 300, at=0, pose="sad", mood="sad", hair="short", color=K.OTHER3),
            Icon("chain", 740, 640, 170, color=K.RED, at=2, sfx="rim"),
            Spark(740, 640, at=2, colors=[K.RED, K.INK2]),
        ], draw=A.ground, research=True, note="重新借贷"),
        Shot(4, "一两年后|借贷和没被帮的人差不多", "研究证据 · Karlan 等 2019", [
            Icon("scale", 540, 720, 230, color=K.INK2, at=0, sfx="wood_low"),
            Label("被帮的", 340, 940, 36, at=2, fill=ACC, sfx="wood_high"),
            Label("没被帮的", 740, 940, 36, at=3, fill=K.INK2, sfx="wood_high"),
        ], research=True, note="两组持平"),
        Shot(2, "一次意外开支|就能把人推回去", "研究证据", [
            Big("意外", 540, 760, 160, at=0, sfx="kick", glow=True),
        ], text_beat=0, punch=0.03, shake=[0], note="意外二字砸下"),
        Shot(4, "原因不止一种|意外冲击、自控都有份", "常见质疑", [
            Icon("question", 540, 720, 200, color=K.RED, at=0, sfx="rim"),
        ], note="研究者未确定单一原因"),
        Shot(2, "要走出陷阱|缺的不只是钱", "下一讲预告", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Pops("还缺 【余闲】", 540, 760, 100, at=0, step=2),
        ], text_beat=0, punch=0.02, note="引出下一讲：余闲"),
        end_shot(REFS, "04 余闲：为什么留白反而更高效"),
    ]
    return Episode(3, "trap", "稀缺陷阱", "为什么帮人还清债，没多久又欠了？", ACC, shots, refs=REFS,
                   publish_title="为什么帮人还清债，没多久又欠了？｜稀缺03 稀缺陷阱",
                   hashtags="#稀缺 #行为经济学 #债务 #读书",
                   cover_title="帮人还清债|没多久又【欠】了？", cover_sub="稀缺 · 稀缺陷阱", cover_shot=3, cover_t=1.6,
                   notes=["「稀缺陷阱」为《稀缺》（2013）的概念：稀缺带来的借贷与“拆东墙补西墙”式应对，反过来让人更稀缺。",
                          "还债实验见 Karlan, Mullainathan & Roth (2019), AER: Insights：2007 年在印度金奈约 1000 名长期向放贷人借款的市场商贩"
                          "（另有菲律宾两次实验）中，研究者为部分人还清了高息债务；多数人在几周内重新借贷，一到两年后被帮者与对照组的借贷水平相当。",
                          "研究者没有确定单一原因，提出的可能解释包括难以避免的收入与支出冲击、以及当下偏好等自控问题。片中以「原因不止一种」呈现。",
                          "循环图为概念示意。"]).build()
