"""03 实践论：道理都懂，为什么还是做不好？（快节奏版：42 镜 × 1 小节）

原文出自《实践论》（一九三七年七月，《毛泽东选集》第一卷）：“你要知道梨子的滋味，你就得变革梨子，亲口吃一吃。”
“一切真知都是从直接经验发源的。”“世上最可笑的是那些‘知识里手’，有了道听途说的一知半解，便自封为‘天下第一’”
“‘秀才不出门，全知天下事’，在技术不发达的古代只是一句空话”“不入虎穴，焉得虎子”；考察团到延安：“看到了延安的
地形、街道、屋宇……听到了各种说话”“这叫做认识的感性阶段”“反复了多次，于是……生起了一个认识过程中的突变（即飞跃），
产生了概念”；“如果只到理性认识为止，那末还只说到问题的一半”“只是把它空谈一阵，束之高阁，并不实行，那末，这种理论再好
也是没有意义的”“看它是否能够达到预想的目的”“‘失败者成功之母’，‘吃一堑长一智’”“实践、认识、再实践、再认识，
这种形式，循环往复以至无穷……都比较地进到了高一级的程度”。
"""

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Counter, Custom, Fig, Icon, Label, Rays, Spark
from scarcity.art import laptop

from . import art as A
from . import art_b as B
from .common import BOOK, S, episode, outro, pops

ACC = "#3E7A5C"
G = A.GROUND_Y
ME = dict(hair="short")


def build():
    shots = [
        # ---- 钩子 1–8
        S("收藏了一堆课", "灵魂拷问", [
            Custom(B.favorites, x=540, y=780, at=0, enter="pop", b0=0, title="我的收藏"),
        ], punch=0.025, flashes=[0], hits=[(0, "pop", 0.8, "收藏"), (1, "pop", 0.8, "收藏"), (2, "pop", 0.8, "收藏"),
                                           (3, "ding", 0.8, "满了")]),
        S("一节没打开", "灵魂拷问", [
            Custom(B.favorites, x=540, y=780, at=0, enter="none", b0=-9, dust=1, title="我的收藏"),
            Icon("cross", 860, 440, 110, color=K.RED, at=2, sfx="rim"),
        ], hits=[(1, "wood_low", 0.8, "落灰")]),
        S("健身视频看了好多", "灵魂拷问", [
            Fig(400, G, 320, at=0, pose="sit", mood="smile", **ME),
            Icon("phone", 560, 720, 110, color=K.INK2, at=0, sfx="pop"),
            Label("已收藏", 760, 480, 44, at=1, sfx="pop"), Label("已点赞", 760, 600, 44, at=2, sfx="pop", fill=K.GOLD),
            Label("下次练", 760, 720, 44, at=3, sfx="pop", fill=K.INK2),
        ], draw=A.ground),
        S("道理全都懂", "灵魂拷问", [
            Fig(540, G, 330, at=0, pose="proud", mood="happy", **ME,
                moves=[(2, dict(pose="cheer", dur=0.25, sfx="pop"))]),
            Icon("bulb", 300, 500, 120, color=K.GOLD, at=1, sfx="ding"),
            Icon("bulb", 780, 500, 120, color=K.GOLD, at=2), Spark(780, 500, at=2),
        ], draw=A.ground),
        S("一上手就懵", "灵魂拷问", [
            Fig(540, G, 330, at=0, pose="stand", mood="surprised", **ME,
                moves=[(1, dict(pose="cover", mood="worried", dur=0.25, sfx="tom"))]),
            Icon("question", 300, 520, 100, color=K.RED, at=2, sfx="rim"),
            Icon("question", 780, 500, 120, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground, shake=[1]),
        pops("懂了 不等于 【会了】", "灵魂拷问", size=150, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="上手 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("毛选里有篇文章", "毛泽东选集", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《实践论》|一九三七年七月", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–12
        S("", "原文", [
            Big("要知道梨子的滋味", 540, 650, 108, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：原文落版"),
            Big("就得亲口吃一吃", 540, 860, 108, at=1, sfx="kick", sub="《实践论》", sub_size=40, shine=True,
                note="原文下半句"),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        S("听人说甜，不算", "原文 · 梨子的滋味", [
            Custom(B.pear, x=540, y=760, at=0, enter="pop", s=1.0, sfx="pop"),
            Bubble("听说很甜", 800, 460, 46, at=1, enter="pop", sfx="wood_high"),
            Icon("cross", 800, 600, 100, color=K.RED, at=3, sfx="rim"),
        ]),
        S("咬一口，才知道", "原文 · 亲口吃一吃", [
            Custom(B.pear, x=540, y=740, at=0, enter="none", s=1.0, bite=1, label="真知"),
        ], hits=[(1, "kick", 1.0, "咬"), (2, "ding", 0.9, "真知")], shake=[1], flashes=[1]),
        pops("一切真知 都从 【直接经验】 来", "原文 · 一切真知", size=120, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 知识里手 13–18
        S("书里嘲讽一种人", "原文 · 知识里手", [
            Fig(540, G, 340, at=0, pose="proud", mood="happy", color="#7A6A55", hair="short"),
            Label("知识里手", 540, 420, 48, at=1, sfx="pop"), Spark(540, 420, at=2, sfx="ding"),
        ], draw=A.ground),
        S("道听途说，一知半解", "原文 · 道听途说", [
            Fig(540, G, 330, at=0, enter="none", pose="proud", mood="happy", color="#7A6A55", hair="short"),
            Bubble("听说……", 260, 500, 44, at=1, enter="pop", sfx="pop"),
            Bubble("据说……", 820, 520, 44, at=2, enter="pop", sfx="pop"),
            Label("一知半解", 540, 400, 44, at=3, sfx="rim", fill=K.INK2),
        ], draw=A.ground),
        S("便自封天下第一", "原文 · 自封为天下第一", [
            Fig(540, G, 330, at=0, enter="none", pose="cheer", mood="happy", color="#7A6A55", hair="short"),
            Icon("crown", 540, 430, 140, color=K.GOLD, at=1, sfx="ding"),
            Icon("cross", 540, 640, 200, color=K.RED, at=3, sfx="kick"),
        ], draw=A.ground, shake=[3]),
        S("秀才不出门？", "原文 · 秀才不出门", [
            Fig(400, G, 320, at=0, pose="sit", mood="smile", color=K.OTHER, hair="bun"),
            Icon("book", 620, 760, 120, color=K.INK2, at=1, sfx="pop"),
            Bubble("全知天下事", 720, 500, 46, at=2, enter="pop", sfx="wood_high"),
        ], draw=A.ground),
        S("古代只是一句空话", "原文 · 只是一句空话", [
            Fig(400, G, 320, at=0, enter="none", pose="sit", mood="worried", color=K.OTHER, hair="bun"),
            Bubble("全知天下事", 720, 500, 46, at=0, enter="none",
                   moves=[(2, dict(alpha=0.2, dur=0.3, sfx="rim"))]),
            Icon("cross", 720, 500, 160, color=K.RED, at=2),
            Label("空话", 720, 680, 48, at=3, sfx="pop", fill=K.INK2),
        ], draw=A.ground),
        S("不入虎穴，焉得虎子", "原文 · 不入虎穴", [
            Custom(B.cave, x=540, y=780, at=0, enter="fade", eyes=1, go=2),
        ], hits=[(0, "wood_low", 0.8, "山洞"), (1, "rim", 0.9, "眼睛"), (2, "tom", 0.8, "走进去")]),
        # ---- 考察团 19–24
        S("书里举了个例子", "书中例子 · 考察团", [
            Custom(A.map_pin, x=540, y=720, at=0, enter="fade", pin=1, region="陕西", place="延安", px=60, py=40),
            Label("外来的考察团", 540, 1110, 46, at=3, sfx="pop", fill=K.INK2),
        ], hits=[(0, "wood_low", 0.8, "地图"), (1, "kick", 0.8, "图钉"), (2, "pop", 0.8, "地名")]),
        S("看街道，听说话", "原文 · 看到了街道、屋宇", [
            Icon("house", 270, 700, 170, color=ACC, at=0, sfx="pop"),
            Icon("eye", 540, 700, 170, color=K.INK2, at=1, sfx="pop"),
            Icon("megaphone", 810, 700, 170, color=K.GOLD, at=2, sfx="pop"),
            Label("各种印象", 540, 940, 46, at=3, sfx="ding"),
        ]),
        S("这只是感性认识", "原文 · 认识的感性阶段", [
            Custom(B.leap, x=540, y=760, at=0, enter="fade", b0=0, leap=99),
        ], hits=[(0, "pop", 0.7, "印象"), (1, "pop", 0.7, "印象"), (2, "pop", 0.7, "印象")]),
        S("反复多次之后", "原文 · 反复了多次", [
            Custom(B.leap, x=540, y=760, at=0, enter="none", b0=-9, leap=99),
            Counter(1, 9, 860, 440, 110, at=0, land=3, suffix="次"),
        ], hits=[(0, "shaker", 0.8, "反复")]),
        S("飞跃：有了概念", "原文 · 突变（即飞跃）", [
            Custom(B.leap, x=540, y=760, at=0, enter="none", b0=-9, leap=1),
        ], hits=[(0, "shaker", 0.7, "聚拢"), (1, "kick", 1.0, "飞跃")], shake=[1], flashes=[1]),
        pops("从 【感性】 到 【理性】", "原文 · 感性到理性", size=140, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        # ---- 二次钩子 25–29
        S("但这才一半", "原文 · 还只说到问题的一半", [
            Big("一半", 540, 720, 260, at=0, sfx="kick", rays=True, glow=True, spark=True),
            Icon("question", 820, 480, 110, color=K.RED, at=2, sfx="rim"),
        ], punch=0.03, flashes=[0], shake=[0]),
        S("道理不用，束之高阁", "原文 · 束之高阁", [
            Custom(B.high_shelf, x=540, y=780, at=0, enter="fade", b=1, label="道理"),
        ], hits=[(0, "wood_low", 0.7, "架子"), (1, "wood_high", 0.8, "放上去"), (2, "shaker", 0.7, "落灰")]),
        S("再好也没有意义", "原文 · 再好也是没有意义的", [
            Icon("trophy", 540, 680, 260, color=K.GOLD, at=0, sfx="pop",
                 moves=[(2, dict(alpha=0.3, dur=0.3, sfx="rim"))]),
            Icon("cross", 540, 680, 220, color=K.RED, at=2),
            Label("不实行", 540, 940, 48, at=3, sfx="pop", fill=K.INK2),
        ]),
        S("对不对？用结果看", "原文 · 达到预想的目的", [
            Icon("target", 680, 700, 280, color=ACC, at=0, sfx="pop"),
            Arrow((180, 980), (650, 720), at=1, sfx="wood_high", color=K.INK2),
            Spark(680, 700, at=2, sfx="ding"), Icon("check", 860, 500, 110, color=K.GREEN, at=3, sfx="ding"),
        ]),
        S("失败了，也是老师", "原文 · 失败者成功之母", [
            Card("失败者成功之母", 540, 640, 58, at=0, sfx="pop"),
            Card("吃一堑长一智", 540, 880, 58, at=2, sfx="pop", fill=K.tint(ACC, 0.7)),
            Spark(540, 880, at=3, sfx="ding"),
        ]),
        # ---- 当下 30–35
        S("今天：囤书囤课", "当下 · 现象", [
            Icon("book", 280, 720, 170, color=K.INK2, at=0, sfx="pop"),
            Icon("book", 540, 700, 190, color=ACC, at=1, sfx="pop"),
            Icon("book", 800, 720, 170, color=K.GOLD, at=2, sfx="pop"),
            Label("还没看", 540, 940, 46, at=3, sfx="rim", fill=K.INK2),
        ]),
        S("看攻略，不出门", "当下 · 现象", [
            Fig(400, G, 320, at=0, pose="sit", mood="smile", **ME),
            Icon("phone", 560, 720, 110, color=K.INK2, at=1, sfx="pop"),
            Icon("photo", 800, 520, 150, color=K.GOLD, at=2, sfx="pop"),
            Icon("cross", 800, 520, 120, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("方案不试就上", "当下 · 现象", [
            Custom(laptop, x=540, y=720, at=0, enter="pop", w=520, h=320, title="新方案", p0=0.6, p1=1, b0=0, b1=2,
                   sfx="pop"),
            Label("直接全量", 540, 1000, 48, at=2, sfx="rim", fill=K.RED),
        ]),
        S("一上线就翻车", "当下 · 现象", [
            Custom(A.pit, x=540, y=900, at=0, enter="fade", fall=1, label="没试过"),
        ], hits=[(0, "wood_low", 0.8, "坑"), (1, "tom", 0.8, "掉坑"), (2, "tom", 0.8, "掉坑")]),
        pops("做一次 胜过 【看十遍】", "一句话", size=140, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("第一步，先动手", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("收藏", K.INK2), ("看完", K.GOLD), ("想透", K.GREEN), ("动手", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "动手置顶")], flashes=[1], shake=[1]),
        # ---- 上手 4 招 36–41
        S("书里给了路线图", "上手 4 招", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="上手 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 先亲口吃一吃", "上手 4 招 · 亲口吃一吃", [
            Custom(B.pear, x=540, y=740, at=0, enter="pop", s=0.9, bite=2, label="先做一次", sfx="pop"),
        ], hits=[(2, "kick", 0.9, "咬")]),
        S("② 多做几次再下结论", "上手 4 招 · 反复多次", [
            Custom(B.leap, x=540, y=760, at=0, enter="fade", b0=0, leap=2),
        ], hits=[(0, "pop", 0.7, "印象"), (1, "pop", 0.7, "印象"), (2, "kick", 0.9, "飞跃")]),
        S("③ 用结果检验", "上手 4 招 · 实践是标准", [
            Icon("target", 540, 680, 300, color=ACC, at=0, sfx="pop"),
            Arrow((120, 1060), (500, 720), at=1, sfx="wood_high", color=K.INK2),
            Icon("check", 820, 470, 120, color=K.GREEN, at=2, sfx="ding"), Spark(540, 680, at=2),
        ]),
        S("④ 再做，再想", "上手 4 招 · 再实践，再认识", [
            Custom(B.loop, x=540, y=800, at=0, enter="fade", b0=0, up=False),
        ], hits=[(0, "pop", 0.8, "实践"), (1, "pop", 0.8, "认识"), (2, "pop", 0.8, "再实践"), (3, "ding", 0.9, "再认识")]),
        S("每一圈都高一级", "原文 · 进到了高一级的程度", [
            Custom(B.loop, x=540, y=800, at=0, enter="none", b0=-4, up=True),
        ], hits=[(0, "kick", 1.0, "上一层"), (2, "ding", 0.9, "高一级")], flashes=[0]),
        # ---- 片尾 42
        outro("你最近“亲口吃”了哪个梨？", "好几件事一起来，怎么不乱？", "今天就动手做一次"),
    ]
    return episode(3, "practice", "实践论", "道理都懂，为什么还是做不好？", ACC, shots,
                   [f"{BOOK}第一卷《实践论》（一九三七年七月）"],
                   "道理都懂|还得【亲口吃一吃】", 8,
                   ["引文出自《实践论》：“你要知道梨子的滋味，你就得变革梨子，亲口吃一吃”（drop 处缩为“要知道梨子的滋味/就得亲口吃一吃”）"
                    "“一切真知都是从直接经验发源的”“知识里手”“道听途说的一知半解，便自封为‘天下第一’”“秀才不出门，全知天下事”“只是一句空话”"
                    "“不入虎穴，焉得虎子”“认识的感性阶段”“反复了多次”“突变（即飞跃）”“还只说到问题的一半”“束之高阁”“再好也是没有意义的”"
                    "“达到预想的目的”“失败者成功之母”“吃一堑长一智”“实践、认识、再实践、再认识”“进到了高一级的程度”。",
                    "考察团例子见《实践论》中“外来的考察团先生们”到延安的叙述；地图、印象圆点、灯泡为示意，“1→9 次”为示意计数，不是书中数字。",
                    "上手 4 招为据原文整理的小建议；“当下”部分为现象示意，不点名任何公司、不引用数字；画面不出现历史人物形象。"],
                   tags="#实践论 #执行力")
