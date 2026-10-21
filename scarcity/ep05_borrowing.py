"""05 借未来：为什么越缺，越想“先借一下”？（重做版）"""

from adler import kit as K
from adler.core import Arrow, Card, Counter, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop, episode, slam, tip2

ACC = "#B5487A"
GROUND = A.GROUND_Y
REFS = [BOOK, "Shah, Mullainathan & Shafir (2012). Some consequences of having too little. Science."]


def build():
    shots = [
        ask("房租 还差 一点|你 选 【哪个】？", [
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=3, left=("现在拿", "¥100", K.RED),
                   right=("下个月拿", "¥150", K.INK2)),
        ], hits=[(3, "wood_low", 0.8, "选项A"), (4, "wood_low", 0.8, "选项B")], note="互动：二选一"),
        Shot(4, "倒计时3秒|快选！", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=-9, pick=7, pick_side=0,
                   left=("现在拿", "¥100", K.RED), right=("下个月拿", "¥150", K.INK2)),
            Label("缺钱时，“现在”最大", 540, 1240, 44, at=10, fill=ACC, sfx="ding"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (7, "rim", 0.9, "选中现在")], flashes=[6], shake=[(6, 12.0)], punch=0.025, note="倒计时，选中“现在”"),
        Shot(2, "这就是“借未来”|看完教你两招", "互动小游戏", [
            Pops("今天 的 急|压过 明天 的 【账】", 540, 760, 92, at=0, step=1),
        ], text_beat=0, note="揭晓"),
        drop("借未来", "Borrowing", "缺的时候|最容易向未来伸手", "花呗 分期 熬夜", size=200),
        Shot(4, "从“以后”|借给“现在”", "机制示意", [
            Icon("clock", 300, 700, 150, color=K.INK2, at=0, sfx="wood_low"),
            Label("以后", 300, 860, 36, at=0, fill=K.INK2),
            Icon("clock", 780, 700, 150, color=K.RED, at=2, sfx="wood_low"),
            Label("现在", 780, 860, 36, at=2, fill=K.RED),
            Arrow((380, 640), (700, 640), at=5, bend=-0.3, color=ACC, sfx="rim"),
            Spark(700, 640, at=5),
            Label("+ 利息", 540, 1000, 50, at=10, fill=K.RED, sfx="kick"),
        ], note="箭头从以后指向现在，再加上利息"),
        Shot(4, "", "一句话", [
            Pops("熬夜 借 精力|拖延 借 时间|分期 借 【钱】", 540, 780, 88, at=0, step=1, gap=24),
        ], punch=0.02, flashes=[8], note="三种借法"),
        Shot(4, "科学家用游戏测过：|资源少的人能向下一轮借", "研究证据 · Shah 等 2012", [
            Fig(300, GROUND, 300, at=0, pose="point", mood="open", hair="short"),
            Card("向下一轮借|要付利息", 760, 600, 48, at=2, rot=3, sfx="wood_low"),
            Icon("chain", 760, 900, 150, color=K.RED, at=6, sfx="rim"),
            Spark(760, 900, at=10, colors=[K.RED, K.GOLD]),
        ], draw=A.ground, research=True, punch=0.02, flashes=[2], note="二次钩子：借贷游戏"),
        Shot(4, "资源少的玩家|借得更多、总分更低", "研究证据 · Shah 等 2012", [
            Icon("chain", 380, 760, 180, color=K.RED, at=0, sfx="rim"),
            Icon("cross", 720, 760, 150, color=K.RED, at=3, sfx="rim"),
            Label("+ 利息", 380, 560, 50, at=5, fill=K.RED, sfx="wood_high"),
            Label("借得越多，越亏", 540, 1040, 46, at=8, fill=K.RED, sfx="rim"),
            Icon("cross", 380, 560, 90, color=K.RED, at=12, sfx="rim"),
        ], research=True, note="借得越多越亏"),
        Shot(4, "借来的越多|下一轮就越缺", "机制示意", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=["缺", "借", "更缺"], R=250, b0=0, step=2, hi=2,
                   spin_at=7),
        ], hits=[(0, "wood_low", 0.8, "缺"), (2, "wood_low", 0.8, "借"), (4, "rim", 0.9, "更缺"), (7, "ding", 0.8, "循环")],
            note="循环示意"),
        slam("利息", "借 一次|付 【利息】", "借的不只是钱|还有未来的自己"),
        Shot(4, "第一招：想分期时|先等24小时", "小方法", [
            Counter(0, 24, 540, 600, 200, at=0, land=4, suffix="小时"),
            Fig(380, GROUND, 300, at=5, pose="think", mood="calm", hair="long", color=K.OTHER, sfx="wood_low",
                moves=[(10, dict(pose="relax", mood="smile", dur=0.6))]),
            Icon("check", 760, 900, 120, color=K.GREEN, at=10, sfx="ding"),
        ], draw=A.ground, note="冷静 24 小时"),
        tip2("第二招：每月先存一笔|应急备用金", "先 存 后 【花】", 130),
        end_shot(REFS, "06 稀缺陷阱：为什么总在“救火”，永远忙不完"),
    ]
    return episode(5, "borrowing", "借未来", "为什么越缺，越想“先借一下”？", ACC, shots, REFS,
                   "为什么越缺|越想【先借一下】？",
                   ["“借贷与短视”出自《稀缺》第 5 章；二选一小游戏、分期为情境演绎，循环图为示意，两招为方法建议。",
                    "Shah 等 (2012, Science)：资源少的玩家在可借用下一轮资源（带利息）时借得更多、总成绩更差。"],
                   "#消费 #分期")
