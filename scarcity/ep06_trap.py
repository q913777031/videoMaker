"""06 稀缺陷阱：为什么总在“救火”，永远忙不完？"""

from adler import kit as K
from adler.core import Big, Counter, Custom, Fig, Glow, Icon, Label, Pops, Rays, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, episode

ACC = "#8E5BA8"
GROUND = A.GROUND_Y
REFS = [BOOK, "Karlan, Mullainathan & Roth (2019). Debt Traps? Market Vendors and Moneylender Debt "
              "in India and the Philippines. AER: Insights."]

RED = K.RED
FIX = [(0, 0, 1, ACC, 1), (0, 1, 2, RED, 5), (0, 3, 3, RED, 10),
       (1, 0, 2, ACC, 1), (1, 2, 2, RED, 6), (1, 4, 2, RED, 11),
       (2, 0, 2, ACC, 2), (2, 2, 2, RED, 7), (2, 4, 2, RED, 12),
       (3, 0, 2, ACC, 2), (3, 2, 1, RED, 8), (3, 3, 3, RED, 13),
       (4, 0, 1, ACC, 3), (4, 1, 2, RED, 9), (4, 3, 3, RED, 14)]


def build():
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("天天 加班|还是 【忙不完】？", 540, 760, 108, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "不是你效率低|是掉进了一个循环", "先说结论", [
            Fig(540, GROUND, 330, at=0, pose="sad", mood="sad", hair="short", color=K.OTHER3),
            Icon("question", 760, 520, 110, color=ACC, at=1, sfx="rim"),
            Spark(760, 520, at=1),
        ], draw=A.ground, text_beat=0, note="问号弹出"),
        Shot(4, "今天补昨天的锅|明天补今天的", "情境演绎", [
            Custom(A.calendar, x=540, y=800, at=0, enter="pop", rows=6, blocks=FIX),
        ], hits=[(1, "wood_low", 0.7, "正常日程"), (5, "rim", 0.8, "补救任务涌入"), (9, "rim", 0.8, "补救任务"),
                 (13, "rim", 0.9, "日程全红")], note="日程表被红色补救任务填满"),
        Shot(4, "越缺越忙|越忙越缺", "原书 · 核心概念", [
            Big("稀缺陷阱", 540, 700, 180, at=0, sfx="kick", sub="Scarcity Trap", rays=True, glow=True, shine=True,
                spark=True, note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "这是一个|会自我加固的循环", "机制示意", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=["没时间", "赶工", "出错", "返工"], R=280, b0=0,
                   step=2, hi=0, spin_at=9),
        ], hits=[(0, "wood_low", 0.8, "没时间"), (2, "wood_low", 0.8, "赶工"), (4, "wood_low", 0.8, "出错"),
                 (6, "rim", 0.9, "返工"), (9, "ding", 0.8, "循环转起来")], note="四个节点连成循环"),
        Shot(4, "", "一句话", [
            Pops("拆 东墙|补 【西墙】", 540, 780, 110, at=0, step=2, gap=34),
        ], punch=0.02, flashes=[6], note="逐词弹出"),
        Shot(4, "研究者帮上千名商贩|直接还清了高息债", "研究证据 · Karlan 等 2019", [
            Counter(0, 1000, 540, 640, 200, at=0, land=4, sub="位印度金奈商贩参与实验"),
            Icon("gift", 540, 960, 120, color=ACC, at=5, sfx="wood_high"),
        ], research=True, punch=0.02, note="二次钩子：数字落定"),
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
        Shot(2, "一次意外|就能把人推回去", "研究证据", [
            Big("意外", 540, 760, 160, at=0, sfx="kick", glow=True),
        ], text_beat=0, punch=0.03, shake=[0], note="意外二字砸下"),
        Shot(4, "原因不止一种|意外冲击、自控都有份", "常见质疑", [
            Icon("question", 540, 720, 200, color=K.RED, at=0, sfx="rim"),
        ], note="研究者未确定单一原因"),
        Shot(2, "要跳出循环|缺的不只是钱", "下一讲预告", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Pops("还缺 【余闲】", 540, 760, 100, at=0, step=2),
        ], text_beat=0, punch=0.02, note="引出下一讲"),
        end_shot(REFS, "07 余闲：为什么日程排满，一点意外就崩"),
    ]
    return episode(6, "trap", "稀缺陷阱", "为什么总在“救火”，永远忙不完？", ACC, shots, REFS,
                   "为什么总在救火|永远【忙不完】？",
                   ["「稀缺陷阱」为《稀缺》第 6 章概念。日程表与循环图为示意。",
                    "Karlan, Mullainathan & Roth (2019, AER: Insights)：为印度金奈约 1000 名商贩中的部分人还清高息债，多数人几周内重新借贷，"
                    "一到两年后与对照组借贷水平相当；研究者认为原因可能包括收支冲击与自控问题。"])
