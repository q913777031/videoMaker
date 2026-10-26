"""02 抓主要矛盾：事情一大堆，先干哪件？（快节奏版：42 镜 × 1 小节）

原文出自《矛盾论》（一九三七年八月，《毛泽东选集》第一卷）第四节“主要的矛盾和主要的矛盾方面”：
“其中必有一种是主要的矛盾”“就要用全力找出它的主要矛盾。捉住了这个主要矛盾，一切问题就迎刃而解了。”
“万千的学问家和实行家，不懂得这种方法，结果如堕烟海，找不到中心”“不能把过程中所有的矛盾平均看待”
“然而这种情形不是固定的，矛盾的主要和非主要的方面互相转化着”；第三节“不同质的矛盾，只有用不同质的方法才能解决”；
第五节宋江三打祝家庄：“两次都因情况不明，方法不对，打了败仗。后来改变方法，从调查情形入手，于是熟悉了盘陀路，
拆散了李家庄、扈家庄和祝家庄的联盟……第三次就打了胜仗。”
"""

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Spark
from scarcity.art import laptop, phone_chat

from . import art as A
from . import art_b as B
from .common import BOOK, S, episode, outro, pops

ACC = A.RED
G = A.GROUND_Y
ME = dict(hair="short", role="worker")
SONG = dict(role="hero")                      # 宋江（《水浒传》人物）
ZHUANG = dict(role="youth", color="#8A6A4A")  # 祝家庄庄丁
TASKS = ("回消息", "报销", "开会", "写周报", "对账", "改格式")


def build():
    shots = [
        # ---- 钩子 1–8
        S("周一一早，消息炸了", "灵魂拷问", [
            Custom(phone_chat, x=540, y=780, at=0, enter="pop", who="工作群",
                   msgs=[(0, "在吗？"), (1, "方案呢？"), (2, "报销单！"), (3, "十点开会")]),
        ], punch=0.025, flashes=[0], hits=[(0, "pop", 0.8, "消息"), (1, "pop", 0.8, "消息"), (2, "pop", 0.8, "消息"),
                                           (3, "rim", 0.9, "消息")]),
        S("待办贴满一屏", "灵魂拷问", [
            Custom(B.sticky_rain, x=540, y=800, at=0, enter="none", b0=0, step=0.5, items=TASKS),
        ], hits=[(0, "pop", 0.7, "便利贴"), (1, "pop", 0.7, "便利贴"), (2, "pop", 0.7, "便利贴")]),
        S("每件都很急", "灵魂拷问", [
            Fig(540, G, 330, at=0, pose="stand", mood="worried", **ME,
                moves=[(2, dict(pose="cover", mood="sad", dur=0.25, sfx="tom"))]),
            Icon("clock", 260, 500, 120, color=K.RED, at=0, sfx="wood_high"),
            Icon("clock", 820, 520, 120, color=K.RED, at=1, sfx="wood_high"),
        ], draw=A.ground),
        S("忙到下班", "灵魂拷问", [
            Fig(540, G, 320, at=0, pose="sit_sad", mood="sad", **ME),
            Custom(laptop, x=540, y=560, at=0, enter="pop", w=420, h=260, title="今日", p0=0.1, p1=0.9, b0=0, b1=3,
                   sfx="pop"),
            Icon("sun", 870, 440, 110, color=K.GOLD, at=1, sfx="wood_low",
                 moves=[(3, dict(y=640, alpha=0.2, dur=0.6, sfx="wood_low"))]),
        ], draw=A.ground),
        S("最要紧的，没动", "灵魂拷问", [
            Card("核心方案|进度 0%", 540, 720, 60, at=0, sfx="pop"),
            Icon("cross", 540, 470, 130, color=K.RED, at=2, sfx="kick"),
        ], shake=[2], flashes=[2]),
        pops("不是你不努力 是没抓 【主要矛盾】", "灵魂拷问", size=110, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="排序 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("毛选里有篇文章", "毛泽东选集", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《矛盾论》|一九三七年八月", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–15
        S("", "原文", [
            Big("捉住了这个主要矛盾", 540, 650, 92, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：原文落版"),
            Big("一切问题就迎刃而解", 540, 860, 92, at=1, sfx="kick", sub="《矛盾论》", sub_size=40, shine=True,
                note="原文下半句"),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        S("刀一到，竹就开", "原文 · 迎刃而解", [
            Custom(B.bamboo_split, x=540, y=760, at=0, enter="fade", cut=1),
        ], hits=[(0, "wood_low", 0.8, "竹子"), (1, "kick", 1.0, "劈开")], shake=[1]),
        S("总有一件最要紧", "原文 · 必有一种是主要的矛盾", [
            Custom(B.knot_web, x=540, y=780, at=0, enter="fade", center="主要", pick=2, items=TASKS),
        ], hits=[(0, "wood_low", 0.8, "乱线"), (2, "ding", 1.0, "圈出主要")]),
        S("捉住它，其余跟着解", "原文 · 一切问题就迎刃而解", [
            Custom(B.knot_web, x=540, y=780, at=0, enter="none", center="主要", pick=-9, solve=1, items=TASKS),
        ], hits=[(0, "wood_high", 0.7, "捉住"), (1, "ding", 0.9, "逐个解开"), (3, "ding", 0.9, "全部解开")],
            flashes=[1]),
        pops("不能 【平均看待】", "原文 · 不能平均看待", size=140, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        S("否则：如堕烟海", "原文 · 如堕烟海", [
            Custom(B.fog, x=540, y=780, at=0, enter="fade", b0=1, role="scholar"),
        ], hits=[(0, "wood_low", 0.7, "起雾"), (1, "rim", 0.7, "问号"), (2, "rim", 0.7, "问号"), (3, "rim", 0.7, "问号")]),
        S("找不到中心", "原文 · 找不到中心", [
            Icon("target", 540, 700, 280, color=ACC, at=0, sfx="pop"),
            Fig(250, G, 290, at=1, pose="shrug", mood="worried", role="scholar", sfx="wood_high"),
            Icon("cross", 540, 700, 200, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        # ---- 三打祝家庄 16–24
        S("书里举了个例子", "书中例子", [
            Icon("book", 380, 520, 180, color=K.INK2, at=0, sfx="wood_low"),
            Card("《水浒传》|三打祝家庄", 380, 800, 50, at=1, sfx="pop"), Spark(380, 800, at=2, sfx="ding"),
            Fig(820, G, 340, at=1, pose="proud", mood="calm", face=-1, **SONG),
            Label("宋江", 820, 640, 40, at=3, sfx="pop"),
        ]),
        S("宋江打祝家庄", "书中例子 · 三打祝家庄", [
            Custom(B.villages, x=540, y=680, at=0, enter="pop", sfx="wood_low"),
            Fig(150, G, 300, at=1, pose="point", mood="angry", **SONG, sfx="wood_high"),
            Fig(940, G, 270, at=2, pose="fist", mood="angry", face=-1, **ZHUANG, sfx="pop"),
        ]),
        S("第一次：败", "书中例子 · 三打祝家庄", [
            Custom(B.villages, x=540, y=680, at=0, enter="none", tries=[(1, False)]),
            Fig(150, G, 300, at=0, enter="none", pose="point", mood="angry", **SONG,
                moves=[(2, dict(pose="sad", mood="sad", dur=0.3))]),
            Fig(940, G, 270, at=0, enter="none", pose="fist", mood="angry", face=-1, **ZHUANG,
                moves=[(2, dict(pose="cheer", mood="happy", dur=0.25))]),
        ], hits=[(1, "wood_high", 0.8, "放箭"), (2, "rim", 0.9, "败")]),
        S("第二次：又败", "书中例子 · 三打祝家庄", [
            Custom(B.villages, x=540, y=680, at=0, enter="none", tries=[(-9, False), (1, False)]),
            Fig(150, G, 300, at=0, enter="none", pose="point", mood="angry", **SONG,
                moves=[(2, dict(pose="cover", mood="sad", dur=0.3))]),
            Fig(940, G, 270, at=0, enter="none", pose="cheer", mood="happy", face=-1, **ZHUANG),
        ], hits=[(1, "wood_high", 0.8, "放箭"), (2, "rim", 0.9, "又败")], shake=[2]),
        S("情况不明，方法不对", "原文 · 情况不明，方法不对", [
            Card("情况不明", 260, 560, 54, at=0, sfx="pop"), Card("方法不对", 820, 560, 54, at=1, sfx="pop"),
            Icon("cross", 260, 740, 100, color=K.RED, at=2, sfx="rim"),
            Icon("cross", 820, 740, 100, color=K.RED, at=3, sfx="rim"),
            Fig(540, G, 340, at=0, pose="think", mood="worried", **SONG),
        ]),
        S("改从调查入手", "原文 · 从调查情形入手", [
            Custom(A.footprints, x=580, y=720, at=0, enter="none", n=7, b0=0, step=0.5, label="盘陀路"),
            Fig(100, G, 290, at=0, pose=K.walk(0.3), mood="open", **SONG),
        ], hits=[(0, "wood_high", 0.7, "迈步"), (1, "wood_high", 0.7, "迈步"), (2, "wood_high", 0.7, "迈步"),
                 (3, "ding", 0.9, "摸清盘陀路")]),
        S("拆散三庄联盟", "原文 · 拆散了联盟", [
            Custom(B.villages, x=540, y=680, at=0, enter="none", tries=[(-9, False), (-8, False)], untie=1),
            Fig(150, G, 300, at=0, enter="none", pose="point", mood="open", **SONG,
                moves=[(1, dict(pose="fist", mood="happy", dur=0.25))]),
        ], hits=[(0, "wood_low", 0.7, "三庄"), (1, "rim", 1.0, "绳断")], flashes=[1]),
        S("第三次：胜", "原文 · 第三次就打了胜仗", [
            Custom(B.villages, x=540, y=680, at=0, enter="none", tries=[(-9, False), (-8, False), (1, True)],
                   untie=-5),
            Fig(150, G, 300, at=0, enter="none", pose="point", mood="angry", **SONG,
                moves=[(2, dict(pose="cheer", mood="happy", dur=0.25))]),
            Spark(540, 520, at=2, sfx="ding"),
        ], hits=[(1, "kick", 1.0, "中箭插旗")], shake=[1], flashes=[1]),
        pops("拆散联盟 才是 【关键】", "一句话", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 二次钩子 25–29
        pops("主次 不是 【固定】 的", "原文 · 这种情形不是固定的", size=140, flash=2,
             extra=[Icon("question", 540, 470, 100, color=K.RED, at=3, sfx="rim")]),
        S("主次会互相转化", "原文 · 互相转化着", [
            Custom(B.seesaw, x=540, y=760, at=0, enter="fade", flip=2, labels=("方案", "上线")),
        ], hits=[(0, "wood_low", 0.8, "跷跷板"), (2, "kick", 1.0, "翻转")], shake=[2]),
        S("今天主要，明天会换", "原文 · 互易其位置", [
            Card("今天：写方案", 540, 600, 54, at=0, sfx="pop"),
            Arrow((540, 680), (540, 820), at=1, sfx="wood_high"),
            Card("明天：赶上线", 540, 900, 54, at=2, sfx="pop", fill=K.tint(ACC, 0.7)),
            Spark(540, 900, at=3, sfx="ding"),
        ]),
        pops("隔段时间 【重新找】", "一句话", size=140, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        S("不同问题，不同解法", "原文 · 不同质的方法", [
            Icon("key", 300, 640, 180, color=K.GOLD, at=0, sfx="pop"),
            Icon("key", 780, 640, 180, color=K.GREEN, at=1, sfx="pop"),
            Label("这把锁", 300, 860, 44, at=2, sfx="wood_high"),
            Label("那把锁", 780, 860, 44, at=3, sfx="wood_high", fill=K.GREEN),
        ]),
        # ---- 当下 30–36
        S("今天：先改格式", "当下 · 现象", [
            Custom(laptop, x=540, y=720, at=0, enter="pop", w=520, h=320, title="方案.pptx", p0=0.1, p1=0.3, b0=0, b1=3,
                   sfx="pop"),
            Label("换字体", 300, 1000, 42, at=1, sfx="pop"), Label("调配色", 540, 1060, 42, at=2, sfx="pop"),
            Label("对齐", 780, 1000, 42, at=3, sfx="pop"),
        ]),
        S("方案逻辑没想清", "当下 · 现象", [
            Card("核心逻辑", 540, 520, 60, at=0, sfx="pop"),
            Icon("question", 260, 470, 90, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 820, 470, 90, color=K.RED, at=2, sfx="wood_high"),
            Fig(540, G, 330, at=0, pose="think", mood="worried", **ME),
            Icon("cross", 780, 720, 100, color=K.RED, at=3, sfx="rim"),
        ]),
        S("减肥先买装备", "当下 · 现象", [
            Icon("gift", 280, 480, 150, color=ACC, at=0, sfx="pop"), Label("跑鞋", 280, 620, 40, at=0),
            Icon("baggage", 540, 480, 150, color=K.INK2, at=1, sfx="pop"), Label("运动服", 540, 620, 40, at=1),
            Icon("clock", 800, 480, 140, color=K.GOLD, at=2, sfx="pop"), Label("手环", 800, 620, 40, at=2),
            Fig(540, G, 330, at=0, pose="stand", mood="happy", role="worker_f", hair="long", color="#C97B84",
                moves=[(3, dict(pose="cheer", dur=0.25, sfx="pop"))]),
        ]),
        S("一次都没跑", "当下 · 现象", [
            Fig(540, G, 320, at=0, pose="sit", mood="flat", **ME),
            Icon("phone", 700, 760, 100, color=K.INK2, at=1, sfx="pop"),
            Icon("cross", 540, 470, 120, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        S("眉毛胡子一把抓", "当下 · 现象", [
            Custom(B.sticky_rain, x=540, y=760, at=0, enter="none", b0=0, step=0.25, items=TASKS),
            Fig(540, G, 300, at=2, pose="fist", mood="angry", **ME, sfx="kick"),
        ], hits=[(0, "shaker", 0.8, "全部落下")], shake=[2]),
        pops("忙 不等于 【有用】", "一句话", size=150, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("把主要的放第一", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("回消息", K.INK2), ("报销", K.GOLD), ("开会", K.GREEN), ("核心方案", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "主要置顶")], flashes=[1], shake=[1]),
        # ---- 排序 4 招 37–41
        S("书里给了方法", "排序 4 招", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="排序 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 全部写下来", "排序 4 招 · 先摸清全部矛盾", [
            Custom(A.notebook, x=540, y=800, at=0, enter="pop", b0=0, step=1,
                   lines=("回消息", "报销", "开会", "核心方案")),
        ], hits=[(0, "shaker", 0.7, "写"), (1, "shaker", 0.7, "写"), (2, "shaker", 0.7, "写"), (3, "ding", 0.9, "写完")]),
        S("② 找牵动全局那件", "排序 4 招 · 找出主要矛盾", [
            Custom(B.knot_web, x=540, y=780, at=0, enter="fade", center="方案", pick=1, solve=2,
                   items=("回消息", "报销", "开会", "写周报", "对账")),
        ], hits=[(1, "ding", 1.0, "圈出"), (2, "ding", 0.8, "跟着解开")]),
        S("③ 集中火力先办它", "排序 4 招 · 用全力", [
            Custom(B.grip, x=540, y=780, at=0, enter="fade", stage=2, b=1, ball="核心方案"),
        ], hits=[(1, "kick", 1.0, "握住")], shake=[1]),
        S("④ 定期重新排", "排序 4 招 · 主次会转化", [
            Custom(B.seesaw, x=540, y=760, at=0, enter="fade", flip=2, labels=("方案", "上线")),
            Icon("clock", 880, 440, 110, color=K.INK2, at=1, sfx="wood_high"),
        ], hits=[(2, "kick", 0.9, "翻转")]),
        # ---- 片尾 42
        outro("你今天的“主要矛盾”是哪件？", "道理都懂，为什么还是做不好？", "先抓主要的，再管其余"),
    ]
    return episode(2, "contradiction", "抓主要矛盾", "事情一大堆，先干哪件？", ACC, shots,
                   [f"{BOOK}第一卷《矛盾论》（一九三七年八月）"],
                   "事情再多|先抓【主要矛盾】", 8,
                   ["引文出自《矛盾论》：“其中必有一种是主要的矛盾”“就要用全力找出它的主要矛盾。捉住了这个主要矛盾，一切问题就"
                    "迎刃而解了”“如堕烟海，找不到中心”“不能把过程中所有的矛盾平均看待”“这种情形不是固定的”“互相转化着”“互易其位置”"
                    "“不同质的矛盾，只有用不同质的方法才能解决”；“不能平均看待”“不同问题，不同解法”为缩写。",
                    "三打祝家庄见《矛盾论》第五节对《水浒传》的引用：“两次都因情况不明，方法不对，打了败仗……熟悉了盘陀路，拆散了"
                    "李家庄、扈家庄和祝家庄的联盟……第三次就打了胜仗”；三庄位置与放箭画面为示意。",
                    "竹子迎刃而解、跷跷板、便利贴为比喻示意；“眉毛胡子一把抓”为俗语，非本文原文；排序 4 招为据原文整理的小建议。",
                    "“当下”部分为现象示意，不点名任何公司、不引用数字；画面不出现历史人物形象。"],
                   tags="#矛盾论 #时间管理")
