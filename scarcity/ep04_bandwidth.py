"""04 带宽税：为什么一有心事，就容易犯低级错误？（重做版）"""

from adler import kit as K
from adler.core import Bubble, Card, Counter, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop, episode, slam, tip2

ACC = "#C8553D"
GROUND = A.GROUND_Y
REFS = [BOOK, "Mani, Mullainathan, Shafir & Zhao (2013). Poverty impedes cognitive function. Science."]
SEQ = list("7391582")


def build():
    shots = [
        ask("3秒 记住|这串 【数字】！", [
            Custom(A.digits, x=540, y=900, at=0, enter="none", seq=SEQ, b0=2, step=0.5),
        ], hits=[(2, "pop", 0.6, "数字"), (3, "pop", 0.6, "数字"), (4, "pop", 0.6, "数字"), (5, "pop", 0.6, "数字")],
            note="互动：记数字"),
        Shot(4, "", "互动小游戏", [
            Custom(A.countdown, x=540, y=480, at=0, enter="none"),
            Custom(A.digits, x=540, y=900, at=0, enter="none", seq=SEQ, b0=-9, hide=6, ask=3),
            Custom(A.bill, x=280, y=1120, at=7, enter="drop", rot=-6, title="房贷", amount="明天扣款", sfx="wood_low"),
            Custom(A.bill, x=800, y=1120, at=9, enter="drop", rot=5, title="信用卡", amount="最低还款", sfx="wood_low"),
            Pops("第 4 个 是 【几】？", 540, 660, 80, at=12, step=1),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到")],
            flashes=[6], shake=[(6, 12.0)], punch=0.025, note="数字被盖住，账单打岔，追问第 4 个"),
        Shot(2, "被账单一打岔|是不是就忘了？", "互动小游戏", [
            Custom(A.digits, x=540, y=900, at=0, enter="none", seq=SEQ, b0=-20, hide=-20, ask=3, reveal=1),
            Pops("答案 是 【1】", 540, 560, 100, at=1, step=1),
        ], text_beat=0, hits=[(1, "ding", 0.9, "揭晓")], note="揭晓答案"),
        drop("带宽税", "Bandwidth Tax", "心事会偷偷占用|你的【思考带宽】", "房贷 账单 焦虑", size=190),
        Shot(4, "剩下的脑子|不够用了", "机制示意", [
            Custom(A.meter, x=540, y=780, at=0, enter="pop", eat=[(2, 0.3, "房贷"), (6, 0.25, "账单"), (10, 0.27, "裁员传闻")]),
            Label("剩下这点，做决定", 540, 1080, 42, at=13, fill=K.RED, sfx="rim"),
        ], hits=[(2, "wood_low", 0.8, "房贷"), (6, "wood_low", 0.8, "账单"), (10, "rim", 0.9, "裁员传闻")], note="带宽被占（示意）"),
        Shot(4, "", "一句话", [
            Pops("发错 群|坐过 站|说错 【话】", 540, 780, 100, at=0, step=2, gap=30),
            Icon("phone", 220, 560, 110, color=K.INK2, at=1, sfx="wood_high"),
            Icon("cross", 860, 1060, 110, color=K.RED, at=11, sfx="rim"),
        ], punch=0.02, flashes=[10], note="低级错误逐词弹出"),
        Shot(4, "科学家真的测过：|先让人想一笔大开支", "研究证据 · Mani 等 2013", [
            Fig(300, GROUND, 300, at=0, pose="think", mood="worried", hair="short"),
            Card("想象：|一笔大额开支", 760, 560, 46, at=2, rot=-3, sfx="wood_low"),
            Icon("puzzle", 760, 860, 150, color=ACC, at=5, sfx="rim"),
            Bubble("钱从哪来…", 340, 560, 40, at=8, think=True, sfx="wood_high"),
            Spark(760, 860, at=11),
        ], draw=A.ground, research=True, punch=0.02, flashes=[2], note="二次钩子：购物中心实验"),
        Shot(4, "收入低的人|推理题成绩明显下降", "研究证据 · Mani 等 2013", [
            Icon("puzzle", 380, 760, 190, color=ACC, at=0, sfx="wood_low"),
            Icon("cross", 720, 760, 150, color=K.RED, at=3, sfx="rim"),
            Spark(720, 760, at=3, colors=[K.RED, K.INK2]),
            Icon("bulb", 540, 520, 110, color=K.INK3, at=5, sfx="wood_high"),
            Label("带宽被占了", 540, 1040, 46, at=8, fill=K.RED, sfx="rim"),
            Spark(540, 1040, at=12, sfx="wood_low", colors=[K.RED, K.GOLD]),
        ], research=True, note="成绩下降"),
        Shot(4, "同一批农民|收获前比收获后考得差", "研究证据 · Mani 等 2013", [
            Counter(0, 464, 540, 600, 200, at=0, land=4, sub="位印度甘蔗农"),
            Icon("sprout", 360, 960, 120, color=K.GREEN, at=6, sfx="wood_high"),
            Label("收获后：成绩回升", 600, 960, 42, at=10, fill=K.GREEN, sfx="ding"),
            Label("收获前：手头紧", 600, 1120, 42, at=7, fill=K.RED, sfx="wood_low"),
            Spark(600, 960, at=13, sfx="wood_high"),
        ], research=True, note="数字落定 464"),
        slam("交税", "不是 笨|是 【交税】", "缺钱时|大脑在加班"),
        Shot(4, "第一招：心烦时|别做重要决定", "小方法", [
            Fig(380, GROUND, 320, at=0, pose="sit_sad", mood="worried", hair="short",
                moves=[(8, dict(pose="relax", mood="smile", dur=0.6))]),
            Card("睡一觉|再决定", 760, 640, 56, at=4, rot=3, sfx="wood_low"),
            Icon("check", 760, 900, 120, color=K.GREEN, at=8, sfx="ding"),
            Label("第二天再签字", 760, 1060, 40, at=12, fill=K.GREEN, sfx="wood_high"),
        ], draw=A.ground, note="睡一觉再决定"),
        tip2("第二招：把烦心事|写在纸上清空大脑", "写 下来|就 【放下】", 120),
        end_shot(REFS, "05 借未来：为什么越缺，越想“先借一下”"),
    ]
    return episode(4, "bandwidth", "带宽税", "为什么一有心事，就容易犯低级错误？", ACC, shots, REFS,
                   "一有心事|就犯【低级错误】？",
                   ["“带宽税”出自《稀缺》第 2 章；记数字小游戏为情境演绎，带宽条为示意，两招为方法建议。",
                    "Mani 等 (2013, Science)：想象大额开支后低收入者推理测试成绩下降；464 位印度甘蔗农收获前成绩低于收获后。"])
