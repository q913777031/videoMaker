"""10 愚公移山：事太难，还干不干？（快节奏版：42 镜 × 1 小节，系列最后一讲）

原文出自《愚公移山》（一九四五年六月十一日，中国共产党第七次全国代表大会闭幕词，《毛泽东选集》第三卷）：
寓言部分——“北山愚公”“一座叫做太行山，一座叫做王屋山”“愚公下决心率领他的儿子们要用锄头挖去这两座大山”
“智叟的看了发笑，说是你们这样干未免太愚蠢了……是完全不可能的”“我死了以后有我的儿子，儿子死了，又有孙子，
子子孙孙是没有穷尽的。这两座山虽然很高，却是不会再增高了，挖一点就会少一点，为什么挖不平呢？”
“毫不动摇，每天挖山不止”“派了两个神仙下凡，把两座山背走了”；“下定决心，不怕牺牲，排除万难，去争取胜利”
“我们一定要坚持下去，一定要不断地工作”“一齐起来和我们一道挖这两座山，有什么挖不平呢？”。本片只取坚持之意。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Shot, Spark, W, G as Gc
from scarcity.art import memo
from sapiens.art import crowd
from zizhi.art import brush_text

from . import art as A
from . import art_d as D
from .build import PLAN
from .common import BOOK, S, episode, pops

ACC = A.RED
G = A.GROUND_Y
ME = dict(role="worker")
OLD = dict(role="elder")          # 愚公（寓言人物）
SAGE = dict(role="sage")         # 智叟（寓言人物）
MY = 1020                                         # 山脚地面 y


def final_outro() -> Shot:
    """系列片尾：评论区回顾问题 + “系列完结”；最后一击落在原曲最后一个强拍。"""

    def draw(g: Gc):
        c = g.c
        with K.at(c, W / 2, 620, 0, 1.0):
            K.icon(c, "book", 0, 0, 240, A.RED, g.p(0, 0.4), 0.8, 0, 1, 0.0, g.acc2)
        K.card(c, W / 2, 900, 900, 150, K.PAPER, g.p(1, 0.3), r=30, accent=g.acc)
        K.text(c, "十讲里，你最想用哪一招？", W / 2, 905, 46, "serif_black", K.INK, g.p(1, 0.3))
        ap = g.p(2, 0.4)
        K.text(c, "毛选 · 10讲", W / 2, 1060, 34, "sans_medium", K.INK3, ap)
        K.text(c, "系列完结 · 谢谢一路同行", W / 2, 1130, 50, "serif_black", g.acc, ap)

    return Shot(1, "收藏合集，常翻常新", "评论区见", [], over=draw, text_beat=0, note="系列片尾：回顾互动",
                hits=[(0, "cymbal", 0.5, "片尾落版"), (1, "pop", 0.8, "问题卡"), (2, "wood_high", 0.7, "系列完结"),
                      (4, "kick", 0.55, "原曲最后一击")])


def build():
    shots = [
        # ---- 钩子 1–8
        S("年初立了三个目标", "灵魂拷问", [
            Custom(memo, x=540, y=780, at=0, enter="pop", title="今年目标", items=("考下证书", "减重十斤", "读完十本书"),
                   b0=1, sfx="wood_low"),
        ], punch=0.025, flashes=[0], hits=[(1, "pop", 0.8, "目标"), (2, "pop", 0.8, "目标"), (3, "pop", 0.8, "目标")]),
        S("三个月后全放下", "灵魂拷问", [
            Custom(memo, x=540, y=780, at=0, enter="none", title="今年目标", items=("考下证书", "减重十斤", "读完十本书"),
                   b0=-9),
            Icon("cross", 860, 712, 80, color=K.RED, at=1, sfx="rim"),
            Icon("cross", 860, 804, 80, color=K.RED, at=2, sfx="rim"),
            Icon("cross", 860, 896, 80, color=K.RED, at=3, sfx="rim"),
        ]),
        S("这事也太难了", "灵魂拷问", [
            Custom(D.mountains, x=540, y=MY - 300, at=0, enter="none", drop=0, names=("考证", "减重"), house=False),
            Fig(540, G, 160, at=2, pose="sad", mood="sad", **ME, sfx="tom"),
        ], hits=[(0, "kick", 0.9, "大山"), (1, "kick", 0.9, "大山")], shake=[0, 1]),
        S("旁人还笑你傻", "灵魂拷问", [
            Custom(crowd, x=700, y=G, at=0, enter="fade", n=3, s=240, spread=380),
            Bubble("别折腾了", 640, 520, 44, at=1, enter="pop", sfx="wood_high"),
            Bubble("哈哈", 860, 600, 44, at=2, enter="pop", sfx="pop"),
            Fig(240, G, 290, at=0, pose="stand", mood="worried", **ME, moves=[(3, dict(pose="sad", dur=0.3, sfx="tom"))]),
        ], draw=A.ground),
        S("你也开始动摇", "灵魂拷问", [
            Fig(540, G, 320, at=0, pose="sit_sad", mood="sad", **ME),
            Icon("question", 400, 520, 80, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 680, 480, 100, color=K.RED, at=2, sfx="wood_high"),
            Label("算了吧？", 540, 380, 50, at=3, sfx="rim", fill=K.INK2),
        ], draw=A.ground),
        pops("难的不是山 是 【放下锄头】", "灵魂拷问", size=120, flash=3,
             extra=[Rays(540, 780, 620, at=3, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="坚持 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("毛选里有篇文章", "毛泽东选集", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《愚公移山》|一九四五年六月", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9
        S("", "原文", [
            Big("挖一点", 540, 640, 170, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：原文落版"),
            Big("就会少一点", 540, 870, 150, at=1, sfx="kick", sub="《愚公移山》", sub_size=40, shine=True,
                note="原文下半句"),
            Spark(540, 870, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        # ---- 寓言 10–24
        S("古代有个寓言", "原文 · 愚公移山", [
            Custom(brush_text, x=440, y=780, at=0, enter="none", text="愚公移山", size=150, b0=0, step=0.5),
            Custom(D.digger, x=780, y=G, at=1, enter="rise", b0=99, s=320, **OLD),
        ], hits=[(0, "wood_low", 0.8, "写"), (1, "wood_high", 0.7, "写"), (2, "ding", 0.8, "写完")]),
        S("两座大山挡住出路", "原文 · 太行山 王屋山", [
            Custom(D.mountains, x=540, y=MY - 300, at=0, enter="none", drop=1),
            Fig(960, MY, 220, at=3, pose="shrug", mood="worried", face=-1, **OLD),
        ], hits=[(0, "wood_low", 0.8, "小屋"), (1, "kick", 1.0, "太行山"), (2, "kick", 1.0, "王屋山")], shake=[1, 2]),
        S("愚公带儿子挖山", "原文 · 用锄头挖", [
            Custom(D.mountains, x=540, y=MY - 300, at=0, enter="none", drop=-9, dig=0, dig_end=4, low=0.92),
            Custom(D.digger, x=300, y=MY, at=0, enter="rise", b0=0, s=260, **OLD),
            Custom(D.digger, x=480, y=MY, at=1, enter="rise", b0=1, s=230, role="youth"),
        ], hits=[(0, "wood_low", 0.8, "挖"), (1, "wood_low", 0.8, "挖"), (2, "wood_low", 0.8, "挖"),
                 (3, "wood_low", 0.8, "挖")]),
        S("智叟笑他太愚蠢", "原文 · 智叟发笑", [
            Fig(760, G, 320, at=0, pose="point", mood="happy", face=-1, **SAGE),
            Bubble("太【愚蠢】了", 620, 520, 50, at=1, enter="pop", sfx="rim"),
            Fig(280, G, 300, at=0, pose="stand", mood="calm", **OLD),
            Bubble("哈哈", 900, 420, 40, at=2, enter="pop", sfx="pop"),
        ], draw=A.ground),
        S("完全不可能的", "原文 · 完全不可能的", [
            Big("不可能", 540, 720, 200, at=1, sfx="kick", glow=True),
            Fig(860, G, 260, at=0, pose="shrug", mood="happy", face=-1, **SAGE),
        ], draw=A.ground, shake=[1], hits=[(0, "wood_low", 0.7, "智叟")]),
        S("我死了有儿子", "原文 · 愚公回答", [
            Fig(260, G, 320, at=0, pose="stand", mood="calm", **OLD, moves=[(1, dict(pose="point", dur=0.25, sfx="wood_high"))]),
            Fig(560, G, 270, at=2, pose="stand", mood="smile", role="youth", sfx="pop"),
            Spark(560, 600, at=2),
        ], draw=A.ground, hits=[(3, "ding", 0.7, "儿子")]),
        S("儿子死了有孙子", "原文 · 愚公回答", [
            Fig(260, G, 270, at=0, enter="none", pose="stand", mood="smile", role="youth"),
            Fig(560, G, 220, at=1, pose="wave", mood="happy", role="youth", color=K.GREEN, sfx="pop"),
            Fig(800, G, 170, at=2, pose="cheer", mood="happy", role="youth", color=K.GOLD, sfx="pop"),
        ], draw=A.ground, hits=[(3, "ding", 0.8, "孙子")]),
        S("子子孙孙，没有穷尽", "原文 · 子子孙孙", [
            Custom(D.ink_crowd, x=540, y=G, at=0, enter="fade", spread=880, s=230,
                   roles=("elder", "youth", "woman", "youth", "farmer", "youth", "youth")),
            Label("没有穷尽", 540, 480, 60, at=2, sfx="ding"),
        ], hits=[(0, "shaker", 0.8, "人越来越多")]),
        S("山却不会再长高", "原文 · 不会再增高了", [
            Custom(D.mountains, x=540, y=MY - 300, at=0, enter="none", drop=-9, house=False),
            Fig(960, MY, 230, at=0, pose="point", mood="smile", face=-1, **OLD),
            Label("封顶", 330, 360, 50, at=1, sfx="pop", fill=K.GREEN),
            Icon("check", 760, 380, 110, color=K.GREEN, at=2, sfx="ding"),
        ], hits=[(3, "wood_high", 0.7, "确认")]),
        pops("挖一点 就会 【少一点】", "原文 · 挖一点就会少一点", size=140, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("为什么挖不平呢", "原文 · 为什么挖不平呢", [
            Custom(D.mountains, x=540, y=MY - 300, at=0, enter="none", drop=-9, dig=0, dig_end=3, low=0.6, house=False),
            Custom(D.digger, x=230, y=MY, at=0, enter="none", b0=0, s=260, **OLD),
            Custom(D.digger, x=420, y=MY, at=0, enter="none", b0=0, s=230, role="youth"),
            Icon("question", 540, 400, 120, color=K.RED, at=3, sfx="rim"),
        ], hits=[(0, "wood_low", 0.8, "挖"), (1, "wood_low", 0.8, "挖"), (2, "wood_low", 0.8, "挖")]),
        S("每天挖山不止", "原文 · 每天挖山不止", [
            Custom(D.daily, x=540, y=780, at=0, enter="pop", n=21, b0=0, step=0.15, title="每天挖一点"),
        ], hits=[(0, "pop", 0.7, "一天"), (1, "pop", 0.7, "一天"), (2, "pop", 0.7, "一天"), (3, "ding", 0.9, "三周")]),
        S("毫不动摇", "原文 · 毫不动摇", [
            Custom(D.digger, x=540, y=MY, at=0, enter="none", b0=0, s=320, mood="angry", **OLD),
            Icon("shield", 820, 520, 140, color=ACC, at=2, sfx="ding"), Spark(820, 520, at=2),
        ], hits=[(0, "wood_low", 0.8, "挖"), (1, "wood_low", 0.8, "挖"), (3, "wood_low", 0.8, "挖")]),
        S("神仙把山背走了", "原文 · 把两座山背走了", [
            Custom(D.immortals, x=540, y=780, at=0, enter="fade", b0=0, b1=2),
        ], hits=[(0, "cymbal", 0.6, "天光"), (2, "kick", 0.9, "背起"), (3, "ding", 0.9, "飞走")], flashes=[2]),
        S("这是一篇闭幕词", "原文 · 七大闭幕词", [
            Icon("book", 540, 560, 200, color=ACC, at=0, sfx="wood_low"),
            Card("一九四五年六月十一日|大会闭幕词", 540, 900, 48, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        pops("下定决心 不怕牺牲 排除万难 去争取胜利", "原文 · 闭幕词", size=96, flash=None),
        # ---- 二次钩子 26
        pops("一定要 【坚持下去】", "原文 · 我们一定要坚持下去", size=140, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        # ---- 当下 27–33
        S("今天：证书考两回", "当下 · 现象", [
            Card("考试成绩", 540, 600, 54, at=0, sfx="pop"),
            Card("第一次|没过", 330, 830, 50, at=1, sfx="rim"),
            Card("第二次|还差一点", 750, 830, 50, at=2, sfx="rim"),
            Icon("question", 540, 1060, 90, color=K.RED, at=3, sfx="wood_high"),
        ]),
        S("减重卡在平台期", "当下 · 现象", [
            Icon("scale", 540, 700, 260, color=K.INK2, at=0, sfx="wood_low"),
            Label("一周没动", 540, 960, 50, at=2, sfx="rim", fill=K.RED),
            Icon("question", 780, 480, 90, color=K.RED, at=3, sfx="wood_high"),
        ], hits=[(1, "shaker", 0.7, "称")]),
        S("身边人：算了吧", "当下 · 现象", [
            Fig(760, G, 320, at=0, pose="shrug", mood="happy", face=-1, role="worker_f"),
            Bubble("【算了】吧", 620, 520, 50, at=1, enter="pop", sfx="wood_high"),
            Fig(280, G, 300, at=0, pose="stand", mood="worried", **ME, moves=[(3, dict(pose="sad", dur=0.3, sfx="tom"))]),
        ], draw=A.ground),
        S("可山不会再长高", "落到自己", [
            Custom(D.mountains, x=540, y=MY - 300, at=0, enter="none", drop=-9, names=("考证", "减重"), house=False,
                   dig=1, dig_end=3, low=0.75),
            Label("你每天在挖", 540, 380, 50, at=0, sfx="pop"),
        ], hits=[(1, "wood_low", 0.8, "挖"), (2, "wood_low", 0.8, "挖"), (3, "ding", 0.8, "矮了")]),
        S("每天少一点", "落到自己", [
            Custom(D.daily, x=540, y=780, at=0, enter="pop", n=28, b0=0, step=0.1, title="打卡"),
        ], hits=[(0, "pop", 0.7, "一天"), (1, "pop", 0.7, "一天"), (2, "ding", 0.9, "四周")]),
        pops("差的不是能力 是 【不停】", "一句话", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("把难事拆成每天", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("等灵感", K.INK2), ("靠运气", K.GOLD), ("一口吃", K.GREEN), ("每天挖", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "每天挖置顶")], flashes=[1], shake=[1]),
        # ---- 坚持 4 招 34–39
        S("书里藏着方法", "原文 · 怎么坚持", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="坚持 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 先下定决心", "坚持 4 招 · 下定决心", [
            Big("决心", 540, 700, 220, at=1, sfx="kick", glow=True, shine=True),
            Fig(540, G, 260, at=0, pose="stand", mood="calm", **ME, moves=[(2, dict(pose="fist", dur=0.2, sfx="wood_high"))]),
        ], draw=A.ground, shake=[1]),
        S("② 拆成一小锄", "坚持 4 招 · 挖一点就会少一点", [
            Custom(D.mountains, x=540, y=MY - 300, at=0, enter="none", drop=-9, house=False, names=("大目标", "")),
            Custom(D.digger, x=860, y=MY, at=0, enter="rise", b0=0, s=240, role="worker"),
            Label("今天：一页书", 300, 400, 42, at=1, sfx="pop"),
            Label("今天：一道题", 780, 460, 42, at=2, sfx="pop"),
            Spark(540, 600, at=3, sfx="ding"),
        ]),
        S("③ 每天挖，不停", "坚持 4 招 · 每天挖山不止", [
            Custom(D.digger, x=400, y=MY, at=0, enter="rise", b0=0, s=300, role="worker"),
            Custom(D.daily, x=800, y=560, at=0, enter="pop", n=9, cols=3, b0=0, step=0.4, title="", cw=80),
        ], hits=[(0, "wood_low", 0.8, "挖"), (1, "wood_low", 0.8, "挖"), (2, "wood_low", 0.8, "挖"),
                 (3, "ding", 0.8, "打卡")]),
        S("④ 拉上人一起挖", "坚持 4 招 · 一道挖", [
            Custom(D.digger, x=220, y=MY, at=0, enter="rise", b0=0, s=260, role="worker"),
            Custom(D.digger, x=500, y=MY, at=1, enter="rise", b0=1, s=250, role="worker_f"),
            Custom(D.digger, x=780, y=MY, at=2, enter="rise", b0=2, s=250, role="worker", color=K.GREEN),
        ], hits=[(0, "pop", 0.8, "一人"), (1, "pop", 0.8, "两人"), (2, "pop", 0.8, "三人"), (3, "ding", 0.9, "一起")]),
        S("别被笑声劝退", "落到自己", [
            Bubble("别折腾了", 300, 520, 44, at=0, enter="pop", sfx="wood_high"),
            Bubble("没用的", 760, 600, 44, at=1, enter="pop", sfx="wood_high"),
            Icon("cross", 300, 680, 110, color=K.RED, at=2, sfx="rim"),
            Icon("cross", 760, 760, 110, color=K.RED, at=3, sfx="rim"),
            Fig(540, G, 280, at=2, enter="none", pose="stand", mood="calm", **ME,
                moves=[(3, dict(pose="fist", mood="smile", dur=0.2))]),
        ]),
        # ---- 系列回顾 40–41
        S("十讲，回头看看", "系列回顾", [
            Custom(D.chips, x=540, y=820, at=0, enter="none", b0=0, step=0.375,
                   items=[(k, c) for k, c, _ in PLAN]),
        ], hits=[(0, "pop", 0.7, "回顾"), (1, "pop", 0.7, "回顾"), (2, "pop", 0.7, "回顾"), (3, "ding", 0.9, "第十讲")]),
        S("愿你挖平那座山", "系列回顾", [
            Custom(D.mountains, x=540, y=MY - 300, at=0, enter="none", drop=-9, dig=0, dig_end=2, low=0.02, house=False),
            Rays(540, 600, 600, at=2, alpha=0.22),
            Fig(540, G, 300, at=2, pose="cheer", mood="happy", **ME, sfx="ding"),
            Spark(540, 560, at=3, sfx="ding"),
        ], hits=[(0, "wood_low", 0.8, "挖"), (1, "wood_low", 0.8, "挖")]),
        # ---- 片尾 42
        final_outro(),
    ]
    return episode(10, "yugong", "愚公移山", "事太难，还干不干？", ACC, shots,
                   [f"{BOOK}第三卷《愚公移山》（一九四五年六月十一日）"],
                   "事再难|也【挖得平】", 8,
                   ["引文出自《愚公移山》：寓言部分“太行山”“王屋山”“用锄头挖去这两座大山”“未免太愚蠢了”“完全不可能的”"
                    "“我死了以后有我的儿子，儿子死了，又有孙子，子子孙孙是没有穷尽的”“却是不会再增高了，挖一点就会少一点，"
                    "为什么挖不平呢”“毫不动摇，每天挖山不止”“派了两个神仙下凡，把两座山背走了”；"
                    "“下定决心，不怕牺牲，排除万难，去争取胜利”“我们一定要坚持下去”；该文是七大闭幕词（题注）。"
                    "原文中“上帝”的引申义未上屏，本片只取坚持之意。",
                    "坚持 4 招对应原文：“下定决心”“挖一点就会少一点”“每天挖山不止”“一齐起来和我们一道挖”（片中引申为拉上同伴），"
                    "“拆成每天一页书、一道题”为创作者的小建议。愚公、智叟为寓言人物，画面不出现历史人物形象。",
                    "“当下”部分为现象示意（证书分数、目标清单为示意），不点名任何公司；“子子孙孙”画面中的“100代+”为夸张示意。"],
                   tags="#愚公移山 #坚持 #自律")
