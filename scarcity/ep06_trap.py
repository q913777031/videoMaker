"""06 稀缺陷阱：为什么总在“救火”，永远忙不完？（重做版）"""

from adler import kit as K
from adler.core import Counter, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop, episode, slam, tip2

ACC = "#8E5BA8"
GROUND = A.GROUND_Y
REFS = [BOOK, "Karlan, Mullainathan & Roth (2019). Debt Traps? Market Vendors and Moneylender Debt. AER: Insights."]
RED = K.RED
NORMAL = [(j, 0, 1, ACC, -9) for j in range(5)] + [(j, 1, 1, "#B79BC7", -9) for j in range(5)]
FIRE_SPOTS = [(-260, 30, 0), (90, 120, 1), (300, -10, 2), (-90, 220, 3), (180, 300, 4), (-300, 330, 5), (0, 50, 6), (300, 220, 6)]


def build():
    shots = [
        ask("3秒 数一数|他 要 救 【几场火】？", [
            Custom(A.calendar, x=540, y=1010, at=0, enter="pop", rows=5, blocks=NORMAL),
        ], hits=[(2, "wood_low", 0.7, "日程")], note="互动：数火苗"),
        Shot(4, "", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.calendar, x=540, y=1010, at=0, enter="none", rows=5, blocks=NORMAL),
            Custom(A.fires, x=540, y=1010, at=0, enter="none", spots=FIRE_SPOTS, count=False),
            Counter(0, 8, 540, 625, 110, at=7, land=9, suffix=" 场"),
            Label("刚灭一场，又冒两场", 540, 1290, 44, at=12, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_high", 0.9, "3"), (1, "shaker", 0.7, "火"), (2, "wood_high", 0.9, "2"), (3, "shaker", 0.7, "火"),
                 (4, "rim", 1.0, "1"), (5, "shaker", 0.7, "火"), (6, "kick", 0.9, "时间到")], flashes=[6], shake=[(6, 12.0)],
            punch=0.025, note="倒计时里火苗不断冒出；时间到后揭晓 8 场"),
        Shot(2, "这就是“稀缺陷阱”|看完教你两招", "互动小游戏", [
            Pops("越 救|越 【多】", 540, 760, 130, at=0, step=1),
            Spark(540, 760, at=4, sfx="rim"),
        ], text_beat=0, note="揭晓"),
        drop("稀缺陷阱", "Scarcity Trap", "越缺越忙|越忙越缺", "救火 返工 补锅", size=180),
        Shot(4, "这是一个|自我加固的循环", "机制示意", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=["没时间", "赶工", "出错", "返工"], R=280, b0=0, step=2,
                   hi=0, spin_at=9),
            Label("停不下来", 540, 1180, 44, at=12, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_low", 0.8, "没时间"), (2, "wood_low", 0.8, "赶工"), (4, "wood_low", 0.8, "出错"),
                 (6, "rim", 0.9, "返工"), (9, "ding", 0.8, "循环")], note="四个节点连成循环"),
        Shot(4, "", "一句话", [
            Pops("拆 东墙|补 【西墙】", 540, 700, 120, at=0, step=2, gap=34),
            Custom(A.fires, x=540, y=1080, at=0, enter="none", count=False,
                   spots=[(-300, 0, 1), (-100, 20, 3), (100, 0, 5), (300, 20, 7), (0, 60, 9)]),
        ], hits=[(1, "shaker", 0.6, "火"), (3, "shaker", 0.6, "火"), (5, "shaker", 0.6, "火"), (7, "shaker", 0.6, "火"),
                 (9, "shaker", 0.6, "火")], punch=0.02, flashes=[6], note="逐词弹出，火苗继续冒"),
        Shot(4, "研究者帮上千名商贩|直接还清了高息债", "研究证据 · Karlan 等 2019", [
            Counter(0, 1000, 540, 620, 200, at=0, land=4, sub="位印度金奈商贩参与实验"),
            Icon("gift", 540, 960, 130, color=ACC, at=6, sfx="wood_high"),
            Spark(540, 960, at=10, sfx="ding"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "结果多数人|几周内又借上了", "研究证据 · Karlan 等 2019", [
            Fig(330, GROUND, 300, at=0, pose="relax", mood="smile", hair="short", color=K.OTHER3,
                moves=[(6, dict(pose="sad", mood="sad", dur=0.6))]),
            Icon("chain", 740, 640, 170, color=K.RED, at=6, sfx="rim"),
            Spark(740, 640, at=6, colors=[K.RED, K.INK2]),
            Label("又借了", 740, 860, 44, at=10, fill=K.RED, sfx="rim"),
        ], draw=A.ground, research=True, note="从轻松到又被债锁住"),
        Shot(4, "一两年后|借贷和没被帮的人一样", "研究证据 · Karlan 等 2019", [
            Icon("scale", 540, 720, 230, color=K.INK2, at=0, sfx="wood_low"),
            Label("被帮的", 330, 960, 40, at=3, fill=ACC, sfx="wood_high"),
            Label("没被帮的", 750, 960, 40, at=5, fill=K.INK2, sfx="wood_high"),
            Label("一样", 540, 1120, 50, at=10, fill=K.RED, sfx="kick"),
        ], research=True, note="两组持平"),
        slam("意外", "一次 意外|就 【推回去】", "只给钱不够|还得给余闲"),
        Shot(4, "第一招：每周先留一块|专门应付突发", "小方法", [
            Custom(A.calendar, x=540, y=800, at=0, enter="none", rows=5, blocks=NORMAL + [(2, 3, 2, K.GREEN, 4)]),
            Label("突发专用", 540, 1000, 40, at=4, fill=K.GREEN, sfx="ding"),
            Custom(A.fires, x=540, y=800, at=0, enter="none", count=False, spots=[(0, 200, 8), (0, 250, 10)]),
            Icon("check", 820, 1120, 110, color=K.GREEN, at=12, sfx="ding"),
        ], hits=[(8, "shaker", 0.6, "火进格子"), (10, "shaker", 0.6, "火进格子")], note="突发有固定的位置"),
        tip2("第二招：一次只灭|最大的那场火", "先 灭 【最大的】", 120),
        end_shot(REFS, "07 余闲：为什么日程排满，一点意外就崩"),
    ]
    return episode(6, "trap", "稀缺陷阱", "为什么总在“救火”，永远忙不完？", ACC, shots, REFS,
                   "为什么总在救火|永远【忙不完】？",
                   ["“稀缺陷阱”出自《稀缺》第 6 章；数火苗小游戏、日程表与循环图为示意，两招为方法建议。",
                    "Karlan, Mullainathan & Roth (2019, AER: Insights)：为印度金奈约 1000 名商贩中的部分人还清高息债，多数人几周内重新借贷，"
                    "一到两年后与对照组借贷水平相当。"])
