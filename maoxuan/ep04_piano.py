"""04 学会弹钢琴：好几件事一起来，怎么不乱？（快节奏版：42 镜 × 1 小节）

原文出自《党委会的工作方法》（一九四九年三月十三日，《毛泽东选集》第四卷）：
五、学会“弹钢琴”：“弹钢琴要十个指头都动作，不能有的动，有的不动。但是，十个指头同时都按下去，那也不成调子。
要产生好的音乐，十个指头的动作要有节奏，要互相配合。党委要抓紧中心工作，又要围绕中心工作而同时开展其它方面的工作。
……不能只注意一部分问题而把别的丢掉。凡是有问题的地方都要点一下……钢琴有人弹得好，有人弹得不好，这两种人弹出来的
调子差别很大。”六、要“抓紧”：“伸着巴掌，当然什么也抓不住。就是把手握起来，但是不握紧，样子像抓，还是抓不住东西。
……抓而不紧，等于不抓。”七、胸中有“数”：“对情况和问题一定要注意到它们的数量方面，要有基本的数量的分析……一切都是
胸中无‘数’，结果就不能不犯错误。”八、“安民告示”：“开会要事先通知……好像‘兵马已到，粮草未备’……如果没有准备，
就不要急于开会。”
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Fig, Icon, Label, Rays, Spark
from sapiens.art import crowd
from scarcity.art import laptop, phone_chat

from . import art as A
from . import art_b as B
from .common import BOOK, S, episode, outro, pops

ACC = "#3D6E92"
G = A.GROUND_Y
ME = dict(hair="short")
BOSS = dict(color=K.DARK, hair="short")
KEYS = ["", "", "", "", "中心", "", "", "", "", ""]
WORK = [("进度", "六成"), ("预算", "剩三成"), ("人手", "四人"), ("截止", "周五")]


def build():
    shots = [
        # ---- 钩子 1–9
        S("手上三个项目", "灵魂拷问", [
            Icon("brief", 270, 740, 180, color=K.INK2, at=0, sfx="pop"),
            Icon("brief", 540, 740, 180, color=ACC, at=1, sfx="pop"),
            Icon("brief", 810, 740, 180, color=K.GOLD, at=2, sfx="pop"),
            Spark(540, 740, at=3, sfx="ding"),
        ], punch=0.025, flashes=[0]),
        S("领导又塞一个", "灵魂拷问", [
            Fig(760, G, 340, at=0, pose="give", mood="smile", face=-1, **BOSS, sfx="wood_low"),
            Icon("brief", 540, 520, 160, color=K.RED, at=1, sfx="kick"),
            Fig(300, G, 300, at=0, pose="stand", mood="calm", **ME,
                moves=[(2, dict(mood="surprised", pose="cover", dur=0.25, sfx="tom"))]),
        ], draw=A.ground, shake=[1]),
        S("家里也在催", "灵魂拷问", [
            Custom(phone_chat, x=540, y=780, at=0, enter="pop", who="妈妈",
                   msgs=[(0, "周末回来吗"), (1, "体检约了没"), (2, "回个话呀")]),
        ], hits=[(0, "pop", 0.8, "消息"), (1, "pop", 0.8, "消息"), (2, "rim", 0.9, "消息")]),
        S("要么全扑上去", "灵魂拷问", [
            Custom(B.piano, x=540, y=820, at=0, enter="fade", mode="all", all_at=1, labels=KEYS),
        ], hits=[(0, "wood_low", 0.7, "键盘"), (1, "kick", 1.0, "十指齐按")], shake=[1], flashes=[1]),
        S("要么只顾一件", "灵魂拷问", [
            Custom(B.piano, x=540, y=820, at=0, enter="fade", mode="one", key=4, b0=0, labels=KEYS),
        ], hits=[(0, "wood_high", 0.7, "按"), (1, "wood_high", 0.7, "按"), (2, "wood_high", 0.7, "按"),
                 (3, "rim", 0.8, "其它没动")]),
        S("两头都不讨好", "灵魂拷问", [
            Fig(540, G, 320, at=0, pose="sit_sad", mood="sad", **ME),
            Icon("cross", 300, 520, 110, color=K.RED, at=1, sfx="rim"),
            Icon("cross", 780, 520, 110, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground),
        pops("不是事多 是不会 【弹钢琴】", "灵魂拷问", size=120, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="多线 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("毛选里有篇文章", "毛泽东选集", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《党委会的工作方法》|一九四九年三月", 540, 940, 46, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 10–19
        S("", "原文", [
            Big("学会“弹钢琴”", 540, 650, 130, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：原文落版"),
            Big("十个指头都动作", 540, 860, 105, at=1, sfx="kick", sub="《党委会的工作方法》", sub_size=40, shine=True,
                note="原文下半句"),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        S("有的动，有的不动", "原文 · 不能有的动，有的不动", [
            Custom(B.piano, x=540, y=820, at=0, enter="fade", mode="one", key=4, b0=0, labels=KEYS),
            Icon("cross", 860, 460, 110, color=K.RED, at=2, sfx="rim"),
        ], hits=[(0, "wood_high", 0.7, "按"), (1, "wood_high", 0.7, "按")]),
        S("别的全丢掉了", "原文 · 把别的丢掉", [
            Custom(B.sticky_rain, x=540, y=760, at=0, enter="none", b0=0, step=0.5,
                   items=("项目一", "项目二", "新任务")),
            Icon("cross", 240, 680, 100, color=K.RED, at=2, sfx="rim"),
            Icon("cross", 840, 680, 100, color=K.RED, at=3, sfx="rim"),
        ], hits=[(0, "pop", 0.7, "便利贴"), (1, "pop", 0.7, "便利贴")]),
        S("十指同时按下去", "原文 · 十个指头同时都按下去", [
            Custom(B.piano, x=540, y=820, at=0, enter="fade", mode="all", all_at=1, labels=KEYS),
        ], hits=[(0, "wood_low", 0.7, "键盘"), (1, "kick", 1.0, "齐按"), (2, "rim", 0.8, "乱音")], shake=[1]),
        S("那也不成调子", "原文 · 那也不成调子", [
            Custom(B.piano, x=540, y=820, at=0, enter="none", mode="all", all_at=0, labels=KEYS),
            Icon("cross", 540, 380, 110, color=K.RED, at=2, sfx="rim"),
        ], hits=[(0, "kick", 0.8, "乱音")]),
        pops("要有 【节奏】 要 【配合】", "原文 · 要有节奏，要互相配合", size=140, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        S("抓紧中心工作", "原文 · 抓紧中心工作", [
            Custom(B.piano, x=540, y=820, at=0, enter="fade", mode="rhythm", center=4, b0=0,
                   seq=(4, 1, 4, 7, 4, 2, 4, 8), labels=KEYS),
        ], hits=[(0, "ding", 0.8, "中心键"), (1, "ding", 0.8, "中心键"), (2, "ding", 0.8, "中心键"),
                 (3, "ding", 0.8, "中心键")]),
        S("其它围着它转", "原文 · 围绕中心工作", [
            Custom(B.knot_web, x=540, y=780, at=0, enter="fade", center="中心", pick=1, solve=2,
                   items=("项目一", "项目二", "新任务", "家里", "学习")),
        ], hits=[(1, "ding", 1.0, "中心"), (2, "ding", 0.8, "其余跟上")]),
        S("有问题的都点一下", "原文 · 都要点一下", [
            Custom(B.piano, x=540, y=820, at=0, enter="fade", mode="rhythm", center=4, b0=0,
                   seq=(0, 2, 4, 6, 4, 8, 9, 4), labels=KEYS),
        ], hits=[(0, "pop", 0.7, "点"), (1, "ding", 0.8, "中心"), (2, "ding", 0.8, "中心"), (3, "pop", 0.7, "点")]),
        S("弹得好坏，差别很大", "原文 · 调子差别很大", [
            Card("乱按", 300, 700, 64, at=0, sfx="pop"), Card("有节奏", 780, 700, 64, at=1, sfx="pop"),
            Icon("cross", 300, 920, 110, color=K.RED, at=2, sfx="rim"),
            Icon("check", 780, 920, 110, color=K.GREEN, at=3, sfx="ding"),
        ]),
        # ---- 二次钩子：抓紧 20–25
        S("但光抓还不够", "原文 · 要“抓紧”", [
            Big("抓紧", 540, 720, 260, at=0, sfx="kick", rays=True, glow=True, spark=True),
            Icon("question", 820, 480, 110, color=K.RED, at=2, sfx="rim"),
        ], punch=0.03, flashes=[0], shake=[0]),
        S("伸着巴掌", "原文 · 伸着巴掌", [
            Custom(B.grip, x=540, y=780, at=0, enter="fade", stage=0, b=1),
        ], hits=[(1, "wood_high", 0.8, "球落下"), (2, "tom", 0.8, "掉了")]),
        S("握了，但不紧", "原文 · 握起来，但是不握紧", [
            Custom(B.grip, x=540, y=780, at=0, enter="fade", stage=1, b=1),
        ], hits=[(1, "wood_high", 0.8, "球落下"), (2, "tom", 0.8, "漏了")]),
        pops("抓而不紧 等于 【不抓】", "原文 · 抓而不紧，等于不抓", size=140, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("握紧，才抓得住", "原文 · 抓得很紧，才能抓住", [
            Custom(B.grip, x=540, y=780, at=0, enter="fade", stage=2, b=1),
        ], hits=[(1, "kick", 1.0, "握住")], shake=[1]),
        S("还要胸中有数", "原文 · 胸中有“数”", [
            Custom(B.gauges, x=540, y=780, at=0, enter="pop", b0=0, title="心里有数", rows=WORK),
        ], hits=[(0, "ding", 0.7, "数字"), (1, "ding", 0.7, "数字"), (2, "ding", 0.7, "数字"), (3, "ding", 0.9, "数字")]),
        S("心里没数，就犯错", "原文 · 胸中无“数”", [
            Custom(B.gauges, x=540, y=780, at=0, enter="pop", b0=99, title="心里没数", rows=WORK),
            Icon("cross", 860, 480, 110, color=K.RED, at=2, sfx="rim"),
        ], hits=[(0, "pop", 0.7, "问号"), (1, "pop", 0.7, "问号")]),
        S("开会也有讲究", "原文 · “安民告示”", [
            Custom(B.notice, x=540, y=780, at=0, enter="fade", b=0, ready=3, title="会议通知",
                   lines=("议题：排期", "要解决：分工", "请先准备")),
        ], hits=[(0, "wood_low", 0.8, "贴告示"), (1, "pop", 0.7, "议题"), (3, "ding", 0.9, "材料备齐")]),
        S("兵马已到，粮草未备", "原文 · 兵马已到，粮草未备", [
            Custom(crowd, x=540, y=G, at=0, enter="fade", n=6, s=250, spread=820),
            Bubble("今天聊啥？", 540, 520, 50, at=1, enter="pop", sfx="wood_high"),
            Icon("cross", 860, 460, 110, color=K.RED, at=2, sfx="rim"),
        ]),
        S("没准备，别急着开", "原文 · 不要急于开会", [
            Custom(B.notice, x=540, y=780, at=0, enter="fade", b=0, ready=2, title="会议通知",
                   lines=("议题", "目标", "材料")),
        ], hits=[(0, "wood_low", 0.8, "告示"), (2, "ding", 0.9, "准备好了")]),
        # ---- 当下 29–35
        S("今天：消息一来就切", "当下 · 现象", [
            Fig(540, G, 320, at=0, pose="stand", mood="worried", **ME,
                moves=[(1, dict(face=-1, dur=0.15, sfx="wood_high")), (2, dict(face=1, dur=0.15, sfx="wood_high")),
                       (3, dict(face=-1, dur=0.15, sfx="wood_high"))]),
            Icon("phone", 260, 520, 110, color=K.INK2, at=0, sfx="pop"),
            Icon("brief", 820, 520, 110, color=ACC, at=0),
        ], draw=A.ground),
        S("每件都做一半", "当下 · 现象", [
            Custom(laptop, x=540, y=740, at=0, enter="pop", w=520, h=320, title="三个项目", p0=0.1, p1=0.5, b0=0,
                   b1=3, sfx="pop"),
            Label("都卡在一半", 540, 1020, 48, at=3, sfx="rim", fill=K.RED),
        ]),
        S("开会没有议题", "当下 · 现象", [
            Custom(crowd, x=540, y=G, at=0, enter="fade", n=6, s=250, spread=820),
            Bubble("先随便聊聊", 540, 520, 50, at=1, enter="pop", sfx="wood_high"),
            Icon("clock", 860, 460, 110, color=K.INK2, at=2, sfx="wood_high"),
        ]),
        S("进度全靠感觉", "当下 · 现象", [
            Custom(B.gauges, x=540, y=780, at=0, enter="pop", b0=99, title="项目进度", rows=WORK),
            Bubble("应该快了吧", 820, 440, 42, at=1, enter="pop", sfx="wood_high"),
        ], hits=[(2, "rim", 0.8, "没数")]),
        S("一天下来，又累又乱", "当下 · 现象", [
            Fig(540, G, 320, at=0, pose="sit_sad", mood="sad", **ME),
            Icon("cloud", 540, 470, 170, color=K.INK2, at=1, sfx="wood_low"),
            Icon("clock", 820, 520, 110, color=K.INK3, at=2, sfx="wood_high"),
        ], draw=A.ground),
        pops("忙和乱 只差 【方法】", "一句话", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("先定中心，再排节奏", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("消息", K.INK2), ("杂事", K.GOLD), ("配合", K.GREEN), ("中心", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "中心置顶")], flashes=[1], shake=[1]),
        # ---- 多线 4 招 36–41
        S("书里给了乐谱", "多线 4 招", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="多线 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 定一个中心", "多线 4 招 · 抓紧中心工作", [
            Custom(B.piano, x=540, y=820, at=0, enter="fade", mode="rhythm", center=4, b0=0, seq=(4, 4, 4, 4, 4, 4),
                   labels=KEYS),
        ], hits=[(0, "ding", 0.8, "中心"), (1, "ding", 0.8, "中心"), (2, "ding", 0.8, "中心")]),
        S("② 其它点一下", "多线 4 招 · 都要点一下", [
            Custom(B.piano, x=540, y=820, at=0, enter="fade", mode="rhythm", center=4, b0=0,
                   seq=(4, 0, 4, 7, 4, 9, 4, 2), labels=KEYS),
        ], hits=[(0, "ding", 0.8, "中心"), (1, "ding", 0.8, "中心"), (2, "ding", 0.8, "中心"), (3, "ding", 0.8, "中心")]),
        S("③ 主要的抓紧", "多线 4 招 · 要“抓紧”", [
            Custom(B.grip, x=540, y=780, at=0, enter="fade", stage=2, b=1, ball="中心工作"),
        ], hits=[(1, "kick", 1.0, "握住")], shake=[1]),
        S("④ 心里有数", "多线 4 招 · 胸中有“数”", [
            Custom(B.gauges, x=540, y=780, at=0, enter="pop", b0=0, title="心里有数", rows=WORK),
        ], hits=[(0, "ding", 0.7, "数字"), (1, "ding", 0.7, "数字"), (2, "ding", 0.7, "数字"), (3, "ding", 0.9, "数字")]),
        # ---- 片尾 42
        outro("你的“十个指头”都在忙啥？", "目标太远，怎么撑下去？", "抓紧中心，其余点一下"),
    ]
    return episode(4, "piano", "学会弹钢琴", "好几件事一起来，怎么不乱？", ACC, shots,
                   [f"{BOOK}第四卷《党委会的工作方法》（一九四九年三月）"],
                   "事情再多|学会【弹钢琴】", 9,
                   ["引文出自《党委会的工作方法》第五至八条：“学会‘弹钢琴’”“弹钢琴要十个指头都动作，不能有的动，有的不动”"
                    "“十个指头同时都按下去，那也不成调子”“要有节奏，要互相配合”“抓紧中心工作，又要围绕中心工作而同时开展其它方面的工作”"
                    "“把别的丢掉”“凡是有问题的地方都要点一下”“调子差别很大”“伸着巴掌”“握起来，但是不握紧”“抓而不紧，等于不抓”"
                    "“胸中有‘数’”“胸中无‘数’，结果就不能不犯错误”“开会要事先通知”“兵马已到，粮草未备”“不要急于开会”；"
                    "部分镜头字幕为缩写。",
                    "钢琴键盘、抓球、进度表中的数字（六成、剩三成、四人、周五）为示意，不是书中数据。",
                    "多线 4 招为据原文整理的小建议；“当下”部分为现象示意，不点名任何公司；画面不出现历史人物形象。"],
                   tags="#工作方法 #多任务")
