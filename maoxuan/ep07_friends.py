"""07 谁是我们的朋友：职场里，谁才是你的朋友？（快节奏版：42 镜 × 1 小节）

原文出自《中国社会各阶级的分析》（一九二五年十二月一日，《毛泽东选集》第一卷开篇）：
“谁是我们的敌人？谁是我们的朋友？这个问题是革命的首要问题。中国过去一切革命斗争成效甚少，其基本原因就是因为不能团结
真正的朋友，以攻击真正的敌人。”“我们要分辨真正的敌友，不可不将中国社会各阶级的经济地位及其对于革命的态度，作一个大概的分析。”
小资产阶级“有三个不同的部分”；第二部分“取了中立的态度，但是绝不反对革命。这一部分人数甚多，大概占小资产阶级的一半”；
“到革命潮流高涨、可以看得见胜利的曙光时，不但小资产阶级的左派参加革命，中派亦可参加革命”；
“一切半无产阶级、小资产阶级，是我们最接近的朋友。那动摇不定的中产阶级……但我们要时常提防他们”。
题解：“这两种机会主义都感觉自己力量不足，而不知道到何处去寻找力量，到何处去取得广大的同盟军。”
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Spark
from sapiens.art import crowd
from scarcity.art import laptop
from zizhi import art as Z

from . import art as A
from . import art_c as C
from .common import BOOK, S, episode, outro, pops

ACC = "#3E6A8A"
G = A.GROUND_Y
ME = dict(hair="short")
PEOPLE = [("领导", "支持", -90), ("同组", "支持", -30), ("隔壁组", "中立", 30), ("新人", "中立", 90),
          ("财务", "中立", 150), ("老张", "阻力", 210)]


def build():
    shots = [
        # ---- 钩子 1–8
        S("新项目你牵头", "灵魂拷问", [
            Custom(A.meeting, x=540, y=760, at=0, enter="fade", b0=1, title="项目启动会"),
        ], punch=0.025, flashes=[0], hits=[(0, "wood_low", 0.8, "会议室"), (1, "pop", 0.8, "图表"),
                                           (2, "ding", 0.7, "你牵头")]),
        S("找人帮忙没人理", "灵魂拷问", [
            Fig(540, G, 320, at=0, pose="wave", mood="smile", **ME),
            Bubble("在忙", 260, 560, 44, at=1, enter="pop", sfx="pop"),
            Bubble("下次吧", 820, 560, 44, at=2, enter="pop", sfx="pop"),
            Bubble("……", 540, 420, 44, at=3, enter="pop", sfx="wood_low"),
        ], draw=A.ground),
        S("还有人唱反调", "灵魂拷问", [
            Fig(300, G, 300, at=0, pose="stand", mood="worried", **ME),
            Fig(760, G, 310, at=0, pose="shrug", mood="flat", color=K.DARK, hair="cap", face=-1,
                moves=[(1, dict(pose="point", dur=0.25, sfx="rim"))]),
            Bubble("这能【行】？", 760, 520, 48, at=1, enter="pop"),
            Custom(Z.sweat, x=330, y=740, at=2, enter="fade"),
        ], draw=A.ground, hits=[(2, "wood_low", 0.7, "冷汗")]),
        S("觉得谁都不帮你", "灵魂拷问", [
            Custom(crowd, x=540, y=G, at=0, enter="fade", n=6, s=230, spread=860),
            Fig(540, G - 40, 280, at=1, pose="sad", mood="sad", **ME, sfx="wood_low"),
            Icon("cloud", 540, 430, 170, color=K.INK2, at=2, sfx="wood_low"),
        ]),
        S("其实是没分清", "灵魂拷问", [
            Custom(C.relation_map, x=540, y=760, at=0, enter="fade", people=PEOPLE, b0=0, step=0.5, legend=False),
        ], hits=[(0, "pop", 0.7, "人"), (1, "pop", 0.7, "人"), (2, "pop", 0.7, "人"), (3, "rim", 0.8, "全是问号")]),
        pops("先分清 谁是 【朋友】", "灵魂拷问", size=140, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="识友 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("毛选开篇第一篇", "毛泽东选集", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《中国社会各阶级的分析》|一九二五年十二月", 540, 940, 46, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–12
        S("", "原文", [
            Big("谁是我们的敌人？", 540, 640, 112, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：原文落版"),
            Big("谁是我们的朋友？", 540, 860, 112, at=1, sfx="kick", sub="《中国社会各阶级的分析》", sub_size=40,
                shine=True, note="原文下半句"),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        S("这是首要问题", "原文 · 革命的首要问题", [
            Icon("target", 540, 680, 280, color=ACC, at=0, sfx="kick"),
            Label("首要问题", 540, 960, 56, at=2, sfx="ding", fill=ACC),
        ], shake=[0]),
        S("过去为何成效甚少", "原文 · 成效甚少", [
            Custom(C.power, x=540, y=780, at=0, enter="fade", grow=99, left="出的力", right="成效", me0=0.9, them0=0.2),
            Icon("question", 540, 400, 100, color=K.RED, at=2, sfx="rim"),
        ], hits=[(0, "wood_low", 0.8, "对比")]),
        pops("不能团结 【真正的朋友】", "原文 · 其基本原因", size=130, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        # ---- 写作背景与分析 13–24
        S("当时都嫌力量不足", "写作背景 · 题解", [
            Custom(C.power, x=540, y=780, at=0, enter="fade", grow=99, left="自己", right="对手", me0=0.25, them0=0.9),
            Custom(Z.sweat, x=420, y=520, at=2, enter="fade"),
        ], hits=[(0, "wood_low", 0.8, "对比"), (2, "rim", 0.8, "冷汗")]),
        S("不知去哪找帮手", "写作背景 · 到何处去寻找力量", [
            Fig(540, G, 320, at=0, pose="think", mood="worried", color="#7A6A55", hair="cap"),
            Icon("question", 300, 560, 90, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 540, 480, 110, color=K.RED, at=2, sfx="wood_high"),
            Icon("question", 780, 560, 90, color=K.RED, at=3, sfx="wood_high"),
        ], draw=A.ground),
        S("先作个大概分析", "原文 · 作一个大概的分析", [
            Custom(A.notebook, x=540, y=800, at=0, enter="pop", b0=0, step=1,
                   lines=("谁支持？", "谁观望？", "谁反对？", "为什么？")),
        ], hits=[(0, "shaker", 0.7, "写"), (1, "shaker", 0.7, "写"), (2, "shaker", 0.7, "写"),
                 (3, "ding", 0.9, "写完")]),
        S("看处境也看态度", "原文 · 经济地位及其态度", [
            Card("处境", 300, 700, 80, at=0, sfx="pop"),
            Card("态度", 780, 700, 80, at=1, sfx="pop"),
            Icon("eye", 540, 950, 160, color=ACC, at=2, sfx="ding"), Spark(540, 950, at=2),
        ]),
        S("比如教员、小职员", "原文 · 小资产阶级", [
            Fig(230, G, 280, at=0, pose="stand", mood="smile", color=K.OTHER, hair="bun", sfx="pop"),
            Fig(540, G, 290, at=1, pose="wave", mood="happy", color=K.OTHER2, hair="short", sfx="pop"),
            Fig(850, G, 280, at=2, pose="stand", mood="open", color="#9C8FB0", hair="long", face=-1, sfx="pop"),
            Label("中小学教员", 230, 520, 36, at=0), Label("小事务员", 540, 500, 36, at=1),
            Label("小商人", 850, 520, 36, at=2), Spark(540, 600, at=3, sfx="ding"),
        ], draw=A.ground),
        S("同一群人分三种", "原文 · 三个不同的部分", [
            Custom(C.three_groups, x=540, y=760, at=0, enter="fade", b0=0),
        ], hits=[(0, "pop", 0.8, "观望"), (1, "pop", 0.8, "中立"), (2, "pop", 0.8, "支持")]),
        S("中间的人最多", "原文 · 大概占一半", [
            Custom(C.half_pie, x=540, y=740, at=0, enter="pop", fill=1, text="一半", sub="中立的那部分", sfx="pop"),
        ], hits=[(1, "shaker", 0.8, "扇区"), (2, "ding", 0.9, "一半")]),
        S("中立但不反对", "原文 · 绝不反对革命", [
            Card("中立的态度", 540, 620, 64, at=0, sfx="pop"),
            Card("绝不反对", 540, 880, 64, at=2, sfx="pop"),
            Icon("check", 860, 880, 110, color=K.GREEN, at=3, sfx="ding"),
        ]),
        S("见到曙光就跟上", "原文 · 看得见胜利的曙光", [
            Custom(C.three_groups, x=540, y=760, at=0, enter="none", b0=-9, sun=1),
        ], hits=[(0, "wood_low", 0.7, "三组"), (1, "ding", 1.0, "曙光"), (2, "pop", 0.8, "跟上")], flashes=[1]),
        S("摇摆的要留心", "原文 · 要时常提防他们", [
            Fig(540, G, 320, at=0, pose="stand", mood="flat", color=K.OTHER, hair="bun",
                moves=[(1, dict(pose="point", face=-1, dur=0.25)), (2, dict(pose="point", face=1, dur=0.25)),
                       (3, dict(pose="shrug", dur=0.25))]),
            Icon("eye", 820, 470, 120, color=ACC, at=1, sfx="wood_high"),
        ], draw=A.ground, hits=[(2, "wood_high", 0.7, "摇摆"), (3, "rim", 0.8, "留心")]),
        S("谁是最接近的朋友", "原文 · 最接近的朋友", [
            Custom(C.relation_map, x=540, y=760, at=0, enter="fade", people=PEOPLE, b0=-9, shown=1),
        ], hits=[(0, "wood_low", 0.7, "关系图"), (1, "ding", 1.0, "染色"), (2, "pop", 0.8, "连线")], flashes=[1]),
        pops("朋友 比你想的 【多】", "一句话", size=140, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("多数人不是对手", "落到自己", [
            Custom(C.half_pie, x=540, y=740, at=0, enter="pop", fill=1, text="多数", sub="支持 + 中立", sfx="pop"),
        ], hits=[(1, "shaker", 0.8, "扇区"), (2, "ding", 0.9, "多数")]),
        # ---- 当下 25–33
        S("今天：推新方案", "当下 · 现象", [
            Custom(laptop, x=540, y=780, at=0, enter="pop", w=560, h=350, title="新方案.pptx", p0=0.3, p1=1, b0=0, b1=2,
                   sfx="pop"),
            Spark(540, 780, at=2, sfx="ding"),
        ]),
        S("只盯着反对的人", "当下 · 现象", [
            Fig(300, G, 320, at=0, pose="point", mood="angry", **ME),
            Fig(780, G, 310, at=0, pose="stand", mood="flat", color=K.DARK, hair="cap", face=-1),
            Icon("eye", 540, 520, 130, color=K.RED, at=1, sfx="wood_high"),
            Icon("eye", 540, 520, 160, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        S("跟他争了一下午", "当下 · 现象", [
            Fig(300, G, 320, at=0, pose="fist", mood="angry", **ME),
            Fig(780, G, 310, at=0, pose="point", mood="angry", color=K.DARK, hair="cap", face=-1),
            Bubble("不对！", 300, 540, 50, at=1, enter="pop", sfx="wood_high"),
            Bubble("就不对！", 780, 540, 50, at=2, enter="pop", sfx="wood_high"),
            Icon("clock", 540, 420, 100, color=K.INK2, at=3, sfx="rim"),
        ], draw=A.ground, shake=[2]),
        S("中间的人都走了", "当下 · 现象", [
            Fig(260, G, 280, at=0, pose="stand", mood="worried", color=K.GOLD, hair="bun",
                moves=[(1, dict(x=-200, dur=0.9, sfx="wood_low"))]),
            Fig(540, G, 290, at=0, pose="stand", mood="worried", color=K.GOLD, hair="long",
                moves=[(2, dict(x=-300, dur=0.9, sfx="wood_low"))]),
            Fig(820, G, 280, at=0, pose="stand", mood="worried", color=K.GOLD, hair="short", face=-1,
                moves=[(3, dict(x=1280, dur=0.9, sfx="wood_low"))]),
        ], draw=A.ground),
        S("最后孤军奋战", "当下 · 现象", [
            Fig(540, G, 330, at=0, pose="sad", mood="sad", **ME),
            Icon("cloud", 540, 450, 170, color=K.INK2, at=1, sfx="wood_low"),
            Label("一个人", 540, 1210, 48, at=2, sfx="rim"),
        ], draw=A.ground),
        pops("多数人 在 【中间】", "一句话", size=150, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("换个打法", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("吵赢", K.INK2), ("站队", K.GOLD), ("单干", K.GREEN), ("团结多数", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "团结多数置顶")], flashes=[1], shake=[1]),
        S("书里给了方法", "原文 · 中国社会各阶级的分析", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="识友 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        # ---- 识友 4 招 34–37
        S("① 画张关系图", "识友 4 招 · 作一个大概的分析", [
            Custom(C.relation_map, x=540, y=760, at=0, enter="fade", people=PEOPLE, b0=0, step=0.5, shown=3),
        ], hits=[(0, "pop", 0.7, "人"), (1, "pop", 0.7, "人"), (2, "pop", 0.7, "人"), (3, "ding", 0.9, "染色")]),
        S("② 看处境和态度", "识友 4 招 · 经济地位及其态度", [
            Custom(Z.form, x=540, y=780, at=0, enter="pop", title="看一个人", skip=-1, b0=1,
                   rows=[("处境", "压力大"), ("态度", "中立"), ("顾虑", "怕担责")]),
        ], hits=[(0, "wood_low", 0.7, "表"), (1, "ding", 0.7, "处境"), (2, "ding", 0.7, "态度"),
                 (3, "ding", 0.8, "顾虑")]),
        S("③ 争取中间的人", "识友 4 招 · 中派亦可参加", [
            Custom(C.relation_map, x=540, y=760, at=0, enter="fade", people=PEOPLE, b0=-9, shown=-9, pull=1),
        ], hits=[(0, "wood_low", 0.7, "关系图"), (1, "shaker", 0.8, "靠拢"), (2, "ding", 0.9, "更近")]),
        S("④ 先拿出小成果", "识友 4 招 · 看得见胜利的曙光", [
            Custom(C.three_groups, x=540, y=760, at=0, enter="none", b0=-9, sun=1,
                   groups=(("观望", 2, -360), ("中间", 4, 0), ("支持", 2, 360))),
        ], hits=[(0, "wood_low", 0.7, "三组"), (1, "ding", 1.0, "成果"), (2, "pop", 0.8, "跟上")], flashes=[1]),
        # ---- 收束 38–41
        S("不是为了树敌", "一句话", [
            Icon("cross", 540, 700, 220, color=K.RED, at=0, sfx="rim"),
            Label("树敌", 540, 960, 56, at=1, sfx="wood_low"),
        ]),
        S("是为了团结多数", "一句话", [
            Custom(crowd, x=540, y=G, at=0, enter="fade", n=7, s=250, spread=860),
            Icon("heart", 300, 520, 90, color=ACC, at=1, sfx="pop"),
            Icon("heart", 540, 470, 110, color=ACC, at=2, sfx="pop"),
            Icon("heart", 780, 520, 90, color=ACC, at=3, sfx="pop"),
        ]),
        S("身边都是帮手", "一句话", [
            Custom(C.relation_map, x=540, y=760, at=0, enter="fade", people=PEOPLE, b0=-9, shown=-9, pull=-9),
            Spark(540, 760, at=1, sfx="ding"),
        ], hits=[(0, "wood_low", 0.7, "关系图")]),
        pops("团结 真正的 【朋友】", "原文 · 团结我们的真正的朋友", size=140, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 片尾 42
        outro("你身边谁是“中间的人”？", "写的报告，为什么没人看？", "分清朋友，团结多数"),
    ]
    return episode(7, "friends", "谁是我们的朋友", "职场里，谁才是你的朋友？", ACC, shots,
                   [f"{BOOK}第一卷《中国社会各阶级的分析》（一九二五年十二月一日）"],
                   "先分清|谁是【朋友】", 8,
                   ["引文出自《中国社会各阶级的分析》：“谁是我们的敌人？谁是我们的朋友？这个问题是革命的首要问题。”“成效甚少”"
                    "“不能团结真正的朋友”“作一个大概的分析”“经济地位及其对于革命的态度”“三个不同的部分”“取了中立的态度，但是"
                    "绝不反对革命……大概占小资产阶级的一半”“看得见胜利的曙光时……中派亦可参加革命”“最接近的朋友”“要时常提防他们”；"
                    "“当时都嫌力量不足”“不知去哪找帮手”据《毛泽东选集》题解。",
                    "“一半”指原文中小资产阶级第二部分“大概占小资产阶级的一半”；关系图、占比饼、三组人为示意，"
                    "“多数人不是对手”“朋友比你想的多”为对原文的今日化概括。",
                    "“当下”部分为现象示意，不点名任何公司；识友 4 招为对原文的今日化应用，强调团结多数、不鼓励树敌。"
                    "画面不出现历史人物形象。"],
                   tags="#人际关系 #团队协作")
