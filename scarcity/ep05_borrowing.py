"""05 借未来：为什么越缺，越想“先借一下”？"""

from adler import kit as K
from adler.core import Arrow, Big, Card, Custom, Fig, Glow, Icon, Label, Pops, Rays, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, episode

ACC = "#B5487A"
GROUND = A.GROUND_Y
REFS = [BOOK, "Shah, Mullainathan & Shafir (2012). Some consequences of having too little. Science.",
        "Camerer et al. (2018). Replicability of social science experiments. Nat Hum Behav."]


def build():
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("先 分期|下个月 【再说】？", 540, 760, 108, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "不是你自控差|是稀缺在逼你借", "先说结论", [
            Fig(540, GROUND, 330, at=0, pose="shrug", mood="surprised", hair="long", color=K.OTHER),
            Icon("question", 760, 520, 110, color=ACC, at=1, sfx="rim"),
            Spark(760, 520, at=1),
        ], draw=A.ground, text_beat=0, note="问号弹出"),
        Shot(4, "工资还没到|先分期买了再说", "情境演绎", [
            Fig(300, GROUND, 320, at=0, pose="point", mood="open", hair="long", color=K.OTHER),
            Card("分 12 期|每月只要一点点", 740, 600, 44, at=2, rot=-3, sfx="wood_low"),
            Custom(A.bill, x=760, y=900, at=6, enter="drop", rot=4, title="账单", amount="下月还", sfx="rim"),
        ], draw=A.ground, note="分期卡片与账单"),
        Shot(4, "缺的时候|今天的急压过明天的账", "原书 · 核心概念", [
            Big("借未来", 540, 700, 200, at=0, sfx="kick", sub="Borrowing", rays=True, glow=True, shine=True, spark=True,
                note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "从“以后”|借给“现在”", "机制示意", [
            Icon("clock", 300, 700, 150, color=K.INK2, at=0, sfx="wood_low"),
            Label("以后", 300, 860, 36, at=0, fill=K.INK2),
            Icon("clock", 780, 700, 150, color=K.RED, at=2, sfx="wood_low"),
            Label("现在", 780, 860, 36, at=2, fill=K.RED),
            Arrow((380, 640), (700, 640), at=4, bend=-0.3, color=ACC, sfx="rim"),
            Spark(700, 640, at=4),
        ], note="箭头从以后指向现在"),
        Shot(4, "", "一句话", [
            Pops("熬夜 借 精力|拖延 借 时间|分期 借 【钱】", 540, 780, 88, at=0, step=1, gap=24),
        ], punch=0.02, flashes=[8], note="三种借法逐词弹出"),
        Shot(4, "游戏实验：资源少|又能向下一轮借", "研究证据 · Shah 等 2012", [
            Fig(330, GROUND, 300, at=0, pose="point", mood="open", hair="short"),
            Card("向未来借|要付利息", 750, 600, 46, at=2, rot=3, sfx="wood_low"),
        ], draw=A.ground, research=True, flashes=[2], note="二次钩子：游戏实验"),
        Shot(4, "资源少的玩家|借得更多、总分更低", "研究证据 · Shah 等 2012", [
            Icon("chain", 420, 740, 170, color=K.RED, at=0, sfx="rim"),
            Icon("cross", 720, 740, 130, color=K.RED, at=2, sfx="rim"),
        ], research=True, note="借得越多越亏"),
        Shot(4, "借来的越多|下一轮就越缺", "机制示意", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=["缺", "借", "更缺"], R=250, b0=0, step=2, hi=2,
                   spin_at=7),
        ], hits=[(0, "wood_low", 0.8, "缺"), (2, "wood_low", 0.8, "借"), (4, "rim", 0.9, "更缺"), (7, "ding", 0.8, "循环")],
            note="循环示意"),
        Shot(2, "每借一次|都要付利息", "原书 · 大意", [
            Big("利息", 540, 760, 160, at=0, sfx="kick", glow=True),
        ], text_beat=0, punch=0.03, shake=[0], note="利息二字砸下"),
        Shot(4, "其中一项实验|在大规模重复中没能复现", "常见质疑", [
            Icon("book", 400, 740, 180, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 720, 640, 110, color=K.RED, at=4, sfx="rim"),
        ], note="复现争议"),
        Shot(2, "试试：想分期时|先等一天再决定", "小练习", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Fig(540, GROUND, 330, at=0, pose="cheer", mood="happy", hair="long", color=K.OTHER),
            Spark(540, 560, at=1, sfx="clap"),
        ], draw=A.ground, text_beat=0, punch=0.02, note="回报"),
        end_shot(REFS, "06 稀缺陷阱：为什么总在“救火”，永远忙不完"),
    ]
    return episode(5, "borrowing", "借未来", "为什么越缺，越想“先借一下”？", ACC, shots, REFS,
                   "为什么越缺|越想【先借一下】？",
                   ["「借贷与短视」为《稀缺》第 5 章主题。分期消费为情境演绎，循环图为示意。",
                    "Shah 等 (2012, Science)：资源少的玩家在可借用下一轮资源（带利息）时借得更多、总成绩更差。",
                    "Camerer 等 (2018) 大规模重复中该文一项实验未能复现。"],
                   "#消费 #分期")
