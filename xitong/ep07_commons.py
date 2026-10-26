"""07 公地悲剧：公司冰箱为什么总是乱糟糟？（快节奏版：42 镜 × 1 小节）

书中观点（转述）：公地悲剧这一系统陷阱里，每个使用者独享使用共享资源的好处，代价却由所有人分摊，资源状况到决策者之间的
反馈太弱，于是资源被过度使用直至衰败；书中给出的出路有三条：教育与劝导、把公地分到个人（私有化）、对公地进行管理
（大家共同商定规则并监督执行）。“公地悲剧”一词出自哈丁 1968 年发表于《科学》的文章，草场放牧为其经典例子。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Spark
from maoxuan.art import meeting
from maoxuan.art_d import ink_crowd
from scarcity.art import GROUND_Y, ground, laptop
from zizhi.art import thing

from . import art_c as A
from .common import BOOK, S, episode, outro, pops

ACC = "#A0663A"
G = GROUND_Y
ME = dict(role="worker", hair="short")
BOSS = dict(role="boss", hair="short")
FOOD = ("牛奶", "饭盒", "蛋糕", "可乐", "水果", "酸奶", "剩菜", "咖啡", "面包")
NAMES = ("小王", "小李", "小张")

SQUARE_SHOT = 1


def build():
    shots = [
        # ---- 钩子 1–8
        S("打开公司冰箱", "灵魂拷问", [
            Custom(A.fridge, x=600, y=780, at=0, enter="fade", items=FOOD[:6], b0=0, step=0.5, mess=True),
        ], punch=0.025, flashes=[0], hits=[(0, "wood_low", 0.8, "开门"), (1, "pop", 0.7, "塞满"), (2, "pop", 0.7, "塞满")]),
        S("全是没人认的", "灵魂拷问", [
            Custom(A.fridge, x=640, y=780, at=0, enter="none", items=FOOD, b0=-9, mess=True),
            Fig(170, G, 300, at=0, pose="cover", mood="surprised", role="worker_f",
                moves=[(2, dict(pose="shrug", mood="worried", dur=0.25, sfx="rim"))]),
            Icon("question", 170, 470, 80, color=K.RED, at=1, sfx="wood_high"),
        ], draw=ground),
        S("谁都不想收拾", "灵魂拷问", [
            Fig(260, G, 300, at=0, pose="shrug", mood="flat", role="worker", color="#8C9A6A", sfx="pop"),
            Fig(540, G, 310, at=1, pose="shrug", mood="flat", role="worker_f", color="#C99A3A", sfx="pop"),
            Fig(820, G, 300, at=2, pose="shrug", mood="flat", role="worker", color="#9C8FB0", face=-1, sfx="pop"),
            Bubble("不是我的", 540, 480, 44, at=3, enter="pop", sfx="wood_high"),
        ], draw=ground),
        S("你也只放不管", "灵魂拷问", [
            Custom(A.fridge, x=680, y=780, at=0, enter="none", items=FOOD[:7], b0=-9, mess=True),
            Fig(200, G, 300, at=0, pose="give", mood="smile", **ME,
                moves=[(2, dict(pose="stand", mood="calm", dur=0.25, sfx="wood_high"))]),
            Icon("check", 200, 470, 80, color=K.GREEN, at=1, sfx="pop"),
        ], draw=ground),
        S("越来越乱", "灵魂拷问", [
            Custom(A.fridge, x=540, y=780, at=0, enter="none", items=FOOD, b0=-9, mess=True),
            Icon("cross", 840, 460, 120, color=K.RED, at=1, sfx="kick"),
            Label("发臭了", 840, 620, 44, at=2, sfx="rim", fill=K.RED),
        ], shake=[1]),
        pops("不是人太懒 是 【结构】 出了问题", "灵魂拷问", size=120, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="治乱 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("系统之美里一句话", "系统之美", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《系统之美》|德内拉·梅多斯", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9
        S("", "书中观点", [
            Big("好处归自己", 540, 640, 150, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：观点落版"),
            Big("代价大家摊", 540, 860, 150, at=1, sfx="kick", sub="《系统之美》", sub_size=40, shine=True),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        # ---- 草场 10–18
        S("这叫公地悲剧", "书中观点 · 系统陷阱", [
            Card("公地悲剧|哈丁 · 一九六八", 540, 700, 60, at=0, sfx="wood_low"),
            Icon("book", 540, 980, 130, color=ACC, at=1, sfx="pop"),
            Spark(540, 700, at=2, sfx="ding"),
        ]),
        S("一片公共草场", "经典例子 · 公共草场", [
            Custom(A.pasture, x=540, y=820, at=0, enter="fade", keys=[(0, 3)], cap=6),
            Custom(ink_crowd, x=540, y=800, at=1, enter="fade", roles=("farmer", "farmer", "farmer"), spread=600, s=200),
        ], hits=[(0, "wood_low", 0.8, "草场"), (1, "pop", 0.8, "牧民")]),
        S("每家多放一头", "经典例子 · 公共草场", [
            Custom(A.pasture, x=540, y=820, at=0, enter="fade", keys=[(0, 3), (1, 4), (2, 5), (3, 6)], cap=6),
        ], hits=[(1, "pop", 0.8, "加牛"), (2, "pop", 0.8, "加牛"), (3, "pop", 0.8, "加牛")]),
        S("多赚全归自己", "经典例子 · 好处", [
            Fig(360, G, 330, at=0, pose="cheer", mood="happy", role="farmer"),
            Custom(thing, x=760, y=720, at=1, enter="pop", obj="moneybag", s=240, sfx="ding"),
            Label("好处：全是我的", 700, 480, 40, at=2, sfx="pop"),
        ], draw=ground),
        S("损失大家分摊", "经典例子 · 代价", [
            Custom(ink_crowd, x=540, y=G, at=0, enter="fade", roles=("farmer", "woman", "youth", "farmer", "elder"),
                   spread=760, s=280),
            Label("代价：大家一起扛", 540, 470, 40, at=1, sfx="pop", fill=K.RED),
            Icon("cross", 540, 340, 80, color=K.RED, at=2, sfx="rim"),
        ], draw=ground),
        S("草场越吃越秃", "经典例子 · 公共草场", [
            Custom(A.pasture, x=540, y=820, at=0, enter="fade", keys=[(0, 7), (1, 9), (2, 11), (3, 12)], cap=6),
        ], hits=[(1, "pop", 0.8, "加牛"), (2, "pop", 0.8, "加牛"), (3, "rim", 0.9, "草秃")]),
        S("最后谁都没了", "经典例子 · 公共草场", [
            Custom(A.pasture, x=540, y=820, at=0, enter="fade", keys=[(0, 12), (1, 6), (2, 2), (3, 0)], cap=6),
            Fig(860, G - 120, 240, at=3, pose="sad", mood="sad", role="farmer", face=-1),
        ], hits=[(1, "tom", 0.8, "减少"), (2, "tom", 0.8, "减少")], shake=[2]),
        S("坏了没人察觉", "书中观点 · 反馈太弱", [
            Fig(360, G, 330, at=0, pose="relax", mood="smile", role="farmer"),
            Icon("eye", 740, 620, 170, color=K.INK2, at=1, sfx="pop"),
            Icon("cross", 740, 620, 190, color=K.RED, at=2, sfx="rim"),
        ], draw=ground),
        pops("人人都 【理性】 结果 【全输】", "书中观点", size=130, flash=3),
        # ---- 二次钩子 19–24
        S("公地到处都是", "反转", [
            Icon("house", 260, 720, 190, color=ACC, at=0, sfx="pop"),
            Icon("phone", 540, 680, 170, color=K.INK2, at=1, sfx="pop"),
            Icon("water", 820, 720, 170, color="#4F86B8", at=2, sfx="pop"),
            Label("会议室", 260, 900, 40, at=0), Label("工作群", 540, 900, 40, at=1), Label("公共水电", 820, 900, 40, at=2),
        ], flashes=[0]),
        S("会议室没人收", "当下 · 现象", [
            Custom(meeting, x=540, y=760, at=0, enter="fade", b0=9, title="会议室"),
            Icon("cross", 820, 460, 110, color=K.RED, at=2, sfx="rim"),
            Icon("can", 300, 960, 110, color=K.INK3, at=1, sfx="pop"),
        ]),
        S("工作群被刷屏", "当下 · 现象", [
            Icon("phone", 540, 760, 260, color=K.INK2, at=0, sfx="pop"),
            Bubble("收到", 300, 520, 40, at=1, enter="pop", sfx="pop"),
            Bubble("哈哈哈", 780, 560, 40, at=2, enter="pop", sfx="pop"),
            Bubble("广告", 340, 960, 40, at=3, enter="pop", sfx="rim"),
        ]),
        S("共享文档乱成团", "当下 · 现象", [
            Custom(laptop, x=540, y=740, at=0, enter="pop", w=560, h=350, title="共享文档", p0=0.9, p1=0.2, b0=0, b1=3,
                   sfx="pop"),
            Icon("question", 820, 470, 90, color=K.RED, at=3, sfx="rim"),
        ]),
        S("公共的不心疼", "当下 · 现象", [
            Fig(540, G, 330, at=0, pose="shrug", mood="flat", **ME),
            Bubble("又不是我的", 760, 480, 44, at=1, enter="pop", sfx="wood_high"),
            Icon("cross", 300, 520, 100, color=K.RED, at=2, sfx="rim"),
        ], draw=ground),
        S("那怎么破？", "转折", [
            Fig(540, G, 330, at=0, pose="think", mood="worried", **ME),
            Icon("question", 360, 480, 90, color=K.RED, at=1, sfx="wood_high"),
            Icon("bulb", 720, 460, 120, color=K.GOLD, at=2, sfx="ding"), Spark(720, 460, at=2),
        ], draw=ground),
        # ---- 书中出路 25–32
        S("书里给了三条路", "书中观点 · 三条出路", [
            Card("劝导", 260, 760, 54, at=0, sfx="pop"),
            Card("分到人", 540, 760, 54, at=1, sfx="pop"),
            Card("定规则", 820, 760, 54, at=2, sfx="pop"),
            Spark(540, 760, at=3, sfx="ding"),
        ]),
        S("第一：讲道理", "书中观点 · 教育劝导", [
            Fig(260, G, 330, at=0, pose="point", mood="open", **BOSS),
            Icon("megaphone", 420, 520, 110, color=ACC, at=1, sfx="pop"),
            Custom(ink_crowd, x=730, y=G, at=0, enter="fade", roles=("worker", "worker_f", "worker"), spread=320, s=260,
                   face_to=-400),
            Bubble("用完请收好", 640, 430, 40, at=2, enter="pop", sfx="wood_high"),
        ], draw=ground),
        S("光靠自觉不够", "书中观点 · 教育劝导", [
            Custom(A.fridge, x=540, y=780, at=0, enter="fade", items=FOOD[:7], b0=-9, mess=True),
            Icon("cross", 840, 460, 120, color=K.RED, at=1, sfx="rim"),
            Label("过两天又乱了", 840, 620, 38, at=2, sfx="tom"),
        ]),
        S("第二：分到人头", "书中观点 · 分到个人", [
            Custom(A.fridge, x=540, y=780, at=0, enter="fade", items=FOOD[:6], b0=-9, names=NAMES, names_at=1),
        ], hits=[(1, "pop", 0.8, "贴名字"), (2, "pop", 0.8, "贴名字")]),
        S("各管各的格子", "书中观点 · 分到个人", [
            Custom(A.pasture, x=540, y=820, at=0, enter="fade", keys=[(0, 6)], cap=8, label="各家一块"),
            Icon("check", 860, 520, 100, color=K.GREEN, at=2, sfx="ding"),
        ], hits=[(0, "wood_low", 0.8, "分块")]),
        S("第三：一起定规", "书中观点 · 共同管理", [
            Custom(A.fridge, x=600, y=780, at=0, enter="fade", items=FOOD[:6], b0=-9, names=NAMES, names_at=-9, rule=1),
        ], hits=[(1, "wood_high", 0.9, "贴规则"), (2, "ding", 0.8, "清爽")]),
        S("一起商量监督", "书中观点 · 共同管理", [
            Custom(ink_crowd, x=540, y=G, at=0, enter="fade",
                   roles=("worker", "worker_f", "boss", "worker_f", "worker"), spread=760, s=290),
            Icon("check", 540, 440, 110, color=K.GREEN, at=2, sfx="ding"),
            Bubble("就这么定", 300, 470, 40, at=1, enter="pop", sfx="pop"),
        ], draw=ground),
        pops("让后果 回到 【自己】 身上", "一句话", size=130, flash=3),
        # ---- 当下与 4 招 33–41
        S("回到公司冰箱", "落到自己", [
            Custom(A.fridge, x=640, y=780, at=0, enter="fade", items=FOOD[:4], b0=-9, names=NAMES, names_at=-9, rule=-9),
            Fig(190, G, 300, at=1, pose="wave", mood="happy", role="worker_f", sfx="pop"),
        ], draw=ground, hits=[(0, "wood_low", 0.7, "开门")]),
        S("书里给的思路", "书中观点 · 走出陷阱", [
            Custom(thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="治乱 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 看清谁在买单", "治乱 4 招 · 看清代价", [
            Card("好处：谁拿", 300, 720, 48, at=0, sfx="pop"),
            Card("代价：谁扛", 780, 720, 48, at=1, sfx="pop"),
            Icon("eye", 540, 960, 130, color=ACC, at=2, sfx="ding"),
        ]),
        S("② 让后果看得见", "治乱 4 招 · 拉近反馈", [
            Fig(360, G, 330, at=0, pose="point", mood="open", **ME),
            Icon("eye", 740, 600, 170, color=ACC, at=1, sfx="pop"),
            Label("谁放的一目了然", 740, 800, 38, at=2, sfx="ding"),
        ], draw=ground),
        S("③ 能分就分到人", "治乱 4 招 · 分到个人", [
            Custom(A.fridge, x=540, y=780, at=0, enter="fade", items=FOOD[:6], b0=-9, names=NAMES, names_at=0.5),
        ], hits=[(0, "wood_low", 0.7, "冰箱"), (1, "pop", 0.8, "名字"), (2, "pop", 0.8, "名字")]),
        S("④ 一起定规矩", "治乱 4 招 · 共同管理", [
            Custom(A.fridge, x=640, y=780, at=0, enter="fade", items=FOOD[:5], b0=-9, names=NAMES, names_at=-9, rule=1),
            Fig(190, G, 300, at=2, pose="point", mood="smile", **ME, sfx="pop"),
        ], draw=ground, hits=[(1, "wood_high", 0.9, "规则")]),
        S("冰箱终于清爽", "收束", [
            Custom(A.fridge, x=640, y=780, at=0, enter="fade", items=FOOD[:3], b0=-9, names=NAMES, names_at=-9, rule=-9),
            Fig(190, G, 300, at=0, pose="stand", mood="smile", role="worker_f",
                moves=[(2, dict(pose="cheer", mood="happy", dur=0.3, sfx="ding"))]),
            Spark(640, 600, at=2),
        ], draw=ground, hits=[(0, "wood_low", 0.7, "清爽")]),
        S("公共的也是自己的", "收束", [
            Rays(540, 700, 620, at=0, alpha=0.2),
            Custom(ink_crowd, x=540, y=G, at=0, enter="fade",
                   roles=("worker", "worker_f", "boss", "worker_f", "worker"), spread=760, s=290),
            Spark(540, 560, at=2, sfx="ding"),
        ], draw=ground, hits=[(0, "wood_low", 0.7, "大家")]),
        S("从贴个名字开始", "收束", [
            Fig(400, G, 330, at=0, pose="give", mood="happy", **ME),
            Label("小王", 700, 640, 60, at=1, sfx="pop"),
            Icon("check", 700, 460, 110, color=K.GREEN, at=2, sfx="ding"),
        ], draw=ground),
        # ---- 片尾 42
        outro("你们公司的“公地”是哪儿？", "标准为什么越来越低？", "公共的，也要有人管"),
    ]
    return episode(7, "commons", "公地悲剧", "公司冰箱为什么总是乱糟糟？", ACC, shots,
                   [f"{BOOK}（Thinking in Systems: A Primer, 2008）", "Garrett Hardin, The Tragedy of the Commons, Science, 1968"],
                   "好处归自己|代价【大家摊】", 8,
                   ["出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)；中译本《系统之美》（邱昭良译，"
                    "浙江人民出版社 2012）。原书中文全文未逐字核对，片中“书中观点”均为转述，不是原话。",
                    "“公地悲剧”一词出自 Garrett Hardin 1968 年发表于 Science 的同名文章，公共草场放牧为其经典例子；书中把它列为系统陷阱，"
                    "出路为教育劝导、分到个人、共同管理（商定规则并监督），片中均为转述。草场牛数、草色变化为示意。",
                    "“当下”部分（冰箱、会议室、工作群、共享文档）为现象示意，不点名公司；4 招为据书中观点整理的小建议。"],
                   tags="#公地悲剧 #团队管理 #职场")
