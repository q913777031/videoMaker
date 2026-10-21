"""04 带宽税：为什么一有心事，就容易犯低级错误？"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Counter, Custom, Fig, Glow, Icon, Pops, Rays, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, episode

ACC = "#C8553D"
GROUND = A.GROUND_Y
REFS = [BOOK, "Mani, Mullainathan, Shafir & Zhao (2013). Poverty impedes cognitive function. Science.",
        "Carvalho, Meier & Wang (2016). Poverty and economic decision-making. AER."]


def build():
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("一有 心事|就 犯 【低级错误】？", 540, 760, 100, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "不是你变笨了|是脑子在“交税”", "先说结论", [
            Fig(540, GROUND, 330, at=0, pose="think", mood="surprised", hair="short"),
            Icon("question", 760, 520, 110, color=ACC, at=1, sfx="rim"),
            Spark(760, 520, at=1),
        ], draw=A.ground, text_beat=0, note="问号弹出"),
        Shot(4, "月底了，房贷信用卡|开会时满脑子都是钱", "情境演绎", [
            Fig(330, GROUND, 320, at=0, pose="sit_sad", mood="worried", hair="short"),
            Bubble("还款日…", 330, 560, 40, at=1, think=True),
            Custom(A.bill, x=760, y=560, at=2, enter="drop", rot=-6, title="房贷", amount="待还", sfx="wood_low"),
            Custom(A.bill, x=820, y=760, at=4, enter="drop", rot=5, title="信用卡", amount="最低还款", sfx="wood_low"),
            Custom(A.bill, x=700, y=920, at=6, enter="drop", rot=-3, title="房租", amount="逾期", sfx="rim"),
        ], draw=A.ground, note="账单一张张砸下来"),
        Shot(4, "心事会偷偷占用|你的【思考带宽】", "原书 · 核心概念", [
            Big("带宽税", 540, 700, 190, at=0, sfx="kick", sub="Bandwidth Tax", rays=True, glow=True, shine=True,
                spark=True, note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "剩下的脑子|不够用了", "机制示意", [
            Custom(A.meter, x=540, y=800, at=0, enter="pop", eat=[(2, 0.25, "房贷"), (4, 0.2, "信用卡"), (6, 0.22, "裁员传闻")]),
        ], hits=[(2, "wood_low", 0.8, "带宽被占：房贷"), (4, "wood_low", 0.8, "带宽被占：信用卡"),
                 (6, "rim", 0.9, "带宽被占：裁员传闻")], note="带宽条被一块块占掉（示意）"),
        Shot(4, "", "一句话", [
            Pops("发错 群|坐过 站|说错 【话】", 540, 780, 100, at=0, step=1, gap=30),
        ], punch=0.02, flashes=[5], note="低级错误逐词弹出"),
        Shot(4, "研究者让人|先想一笔大额开支", "研究证据 · Mani 等 2013", [
            Fig(330, GROUND, 300, at=0, pose="think", mood="worried", hair="short"),
            Card("想象：|一笔大额开支", 740, 560, 44, at=2, rot=-3, sfx="wood_low"),
            Icon("puzzle", 740, 860, 130, color=ACC, at=4, sfx="rim"),
        ], draw=A.ground, research=True, flashes=[4], note="二次钩子：真实实验"),
        Shot(4, "收入低的人|推理题成绩明显下降", "研究证据 · Mani 等 2013", [
            Icon("puzzle", 420, 760, 180, color=ACC, at=0, sfx="wood_low"),
            Icon("cross", 720, 760, 140, color=K.RED, at=2, sfx="rim"),
            Spark(720, 760, at=2, colors=[K.RED, K.INK2]),
        ], research=True, note="成绩下降"),
        Shot(4, "同一批农民|收获前比收获后考得差", "研究证据 · Mani 等 2013", [
            Counter(0, 464, 540, 640, 200, at=0, land=4, sub="位印度甘蔗农"),
            Icon("sprout", 360, 960, 110, color=K.GREEN, at=5, sfx="wood_high"),
            Icon("clock", 720, 960, 110, color=ACC, at=6, sfx="wood_low"),
        ], research=True, note="数字落定 464"),
        Shot(2, "不是吃得差|也不是不够努力", "研究证据", [
            Icon("check", 540, 760, 200, color=K.GREEN, at=0, sfx="rim"),
            Spark(540, 760, at=0),
        ], text_beat=0, note="研究排除了营养、时间与努力差异"),
        Shot(4, "也有研究没发现这种效应|结论仍有争议", "常见质疑 · Carvalho 等 2016", [
            Icon("scale", 540, 720, 230, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 780, 560, 100, color=K.RED, at=4, sfx="rim"),
        ], note="发薪日前后未发现认知差异"),
        Shot(2, "试试：重要决定|别在焦虑时做", "小练习", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Fig(540, GROUND, 330, at=0, pose="relax", mood="happy", hair="short"),
            Spark(540, 560, at=1, sfx="clap"),
        ], draw=A.ground, text_beat=0, punch=0.02, note="回报"),
        end_shot(REFS, "05 借未来：为什么越缺，越想“先借一下”"),
    ]
    return episode(4, "bandwidth", "带宽税", "为什么一有心事，就容易犯低级错误？", ACC, shots, REFS,
                   "一有心事|就犯【低级错误】？",
                   ["「带宽税」为《稀缺》第 2 章概念。月底还款走神为情境演绎，带宽条占比为示意。",
                    "Mani 等 (2013, Science)：想象大额开支后低收入者推理测试成绩下降；464 位印度甘蔗农收获前成绩低于收获后。",
                    "Carvalho 等 (2016, AER) 发薪日前后未发现认知差异；结论仍有争议。"])
