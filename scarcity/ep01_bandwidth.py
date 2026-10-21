"""01 带宽税：穷，会让人变笨吗？"""

from adler import kit as K
from adler.core import Big, Card, Counter, Custom, Episode, Fig, Glow, Icon, Pops, Rays, Shot, Spark, end_shot

from . import art as A

ACC = "#C8553D"
GROUND = A.GROUND_Y
REFS = ["Mullainathan & Shafir (2013). Scarcity: Why Having Too Little Means So Much.",
        "Mani, Mullainathan, Shafir & Zhao (2013). Poverty impedes cognitive function. Science.",
        "Carvalho, Meier & Wang (2016). Poverty and economic decision-making. AER."]


def build() -> Episode:
    shots = [
        # 0–3 秒钩子：一句反常识问题逐词砸出 + 闪白，第一秒就有画面事件
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("穷 会让人|变【笨】吗？", 540, 760, 104, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        # 开放回路：先许诺一个反直觉的结论，留住到最后
        Shot(2, "科学家真的做了实验|答案出人意料", "先说结论", [
            Fig(540, GROUND, 330, at=0, pose="think", mood="surprised", hair="short"),
            Icon("question", 760, 520, 110, color=ACC, at=1, sfx="rim"),
            Spark(760, 520, at=1),
        ], draw=A.ground, text_beat=0, note="主角思考，问号弹出"),
        Shot(4, "钱不够的时候|脑子好像也不够用了", "情境演绎", [
            Fig(380, GROUND, 330, at=0, pose="sit_sad", mood="worried", hair="short"),
            Custom(A.bill, x=760, y=560, at=2, enter="drop", rot=-6, title="房租", amount="待付", sfx="wood_low"),
            Custom(A.bill, x=820, y=760, at=4, enter="drop", rot=5, title="水电", amount="逾期", sfx="wood_low"),
            Custom(A.bill, x=700, y=900, at=6, enter="drop", rot=-3, title="信用卡", amount="最低还款", sfx="rim"),
        ], draw=A.ground, note="账单一张张砸下来"),
        # 音乐 drop：概念名砸下 + 旋转光束 + 扫光 + 星光 + 闪白 + 抖动
        Shot(4, "稀缺会向你的大脑|收一笔【带宽税】", "原书 · 核心概念", [
            Big("带宽税", 540, 700, 190, at=0, sfx="kick", sub="Bandwidth Tax", rays=True, glow=True, shine=True,
                spark=True, note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "带宽：你用来思考|和自控的心智容量", "原书 · 大意", [
            Icon("bulb", 540, 560, 170, color=ACC, at=0, sfx="wood_low"),
            Pops("【认知能力】 + 【执行控制力】", 540, 860, 66, at=2, step=2, gap=20),
        ], note="带宽的两个部分逐个弹出"),
        Shot(4, "缺钱的念头|会一直占着后台", "机制示意", [
            Custom(A.meter, x=540, y=800, at=0, enter="pop", eat=[(2, 0.25, "房租"), (4, 0.2, "账单"), (6, 0.2, "借钱")]),
        ], hits=[(2, "wood_low", 0.8, "带宽被占：房租"), (4, "wood_low", 0.8, "带宽被占：账单"), (6, "rim", 0.9, "带宽被占：借钱")],
            note="带宽条被一块块占掉（示意）"),
        # 45 秒前后的二次钩子：反转
        Shot(4, "", "反转", [
            Glow(540, 780, 560, at=0, alpha=0.26),
            Pops("不是 人 笨|是 处境 在 【收税】", 540, 780, 96, at=0, step=1, maxw=820),
        ], punch=0.02, flashes=[6], note="二次钩子：不是人笨，是处境在收税"),
        Shot(4, "想到一笔大开支|低收入者成绩下降", "研究证据 · Mani 等 2013", [
            Fig(330, GROUND, 300, at=0, pose="think", mood="worried", hair="short"),
            Card("想象：|一笔大额开支", 740, 560, 44, at=2, rot=-3, sfx="wood_low"),
            Icon("puzzle", 740, 860, 130, color=ACC, at=4, sfx="rim"),
        ], draw=A.ground, research=True, note="实验情境：先想开支，再做推理题"),
        Shot(4, "同一批农民|收获前比收获后考得差", "研究证据 · Mani 等 2013", [
            Counter(0, 464, 540, 640, 200, at=0, land=4, sub="位印度甘蔗农"),
            Icon("sprout", 360, 960, 110, color=K.GREEN, at=5, sfx="wood_high"),
            Icon("clock", 720, 960, 110, color=ACC, at=6, sfx="wood_low"),
        ], research=True, note="数字滚动落定 464"),
        Shot(2, "不是吃得差|也不是不够努力", "研究证据", [
            Icon("check", 540, 760, 200, color=K.GREEN, at=0, sfx="rim"),
            Spark(540, 760, at=0),
        ], text_beat=0, note="研究排除了营养、时间与努力程度的差异"),
        Shot(4, "也有研究没看到这种效应|结论仍有争议", "常见质疑 · Carvalho 等 2016", [
            Icon("scale", 540, 720, 230, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 780, 560, 100, color=K.RED, at=4, sfx="rim"),
        ], note="天平与问号：发薪日前后实验未发现认知差异"),
        Shot(2, "所以先别骂自己|先给大脑【减负】", "小练习", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Fig(540, GROUND, 330, at=0, pose="cheer", mood="happy", hair="short"),
            Spark(540, 560, at=1, sfx="clap"),
        ], draw=A.ground, text_beat=0, punch=0.02, note="主角松一口气（收束与回报）"),
        end_shot(REFS, "02 管窥：为什么越忙越乱"),
    ]
    return Episode(1, "bandwidth", "带宽税", "穷，会让人变笨吗？", ACC, shots, refs=REFS,
                   publish_title="穷，会让人变笨吗？｜稀缺01 带宽税",
                   hashtags="#稀缺 #行为经济学 #心理学 #读书",
                   cover_title="穷，会让人|变【笨】吗？", cover_sub="稀缺 · 带宽税", cover_shot=3, cover_t=1.6,
                   notes=["「带宽」（认知能力 + 执行控制力）与「带宽税」为穆来纳森、沙菲尔《稀缺》（2013）的核心概念。",
                          "购物中心实验与甘蔗农研究见 Mani, Mullainathan, Shafir & Zhao (2013), Science 341: 976–980："
                          "让低收入者先想象一笔大额开支，其推理与自控测试成绩下降，高收入者不受影响；印度 464 位甘蔗农在收获前（手头紧）"
                          "的测试成绩低于收获后，作者认为营养、时间与努力程度差异不能解释这一结果。",
                          "反面证据：Carvalho, Meier & Wang (2016, AER) 对比美国低收入者发薪日前后，未发现认知功能差异；"
                          "也有学者批评 Mani 等的结论依赖于把被试按收入划分的方式。片中以「结论仍有争议」呈现。",
                          "带宽条的占用比例仅为示意，不是测量数据。"]).build()
