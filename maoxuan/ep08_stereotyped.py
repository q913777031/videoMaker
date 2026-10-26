"""08 反对党八股：写的报告，为什么没人看？（快节奏版：42 镜 × 1 小节）

原文出自《反对党八股》（一九四二年二月八日，《毛泽东选集》第三卷）：八大罪状——“空话连篇，言之无物”
（“懒婆娘的裹脚，又长又臭”“群众见了就摇头”）、“装腔作势，借以吓人”、“无的放矢，不看对象”（“射箭要看靶子，
弹琴要看听众”）、“语言无味，像个瘪三”、“甲乙丙丁，开中药铺”、“不负责任，到处害人”（洗脸照镜子之喻、
“下笔千言，离题万里”）、“流毒全党，妨害革命”、“传播出去，祸国殃民”；“不是说任何东西都以短为好”
“看菜吃饭，量体裁衣”“尤其需要有内容的文章”“赶快扔到垃圾桶里去”“拿不出来的东西就不要拿出来”
“要向人民群众学习语言”。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Counter, Custom, Fig, Icon, Label, Rays, Spark
from sapiens.art import crowd
from scarcity.art import laptop

from . import art as A
from . import art_d as D
from .common import BOOK, S, episode, outro, pops

ACC = A.RED
G = A.GROUND_Y
ME = dict(hair="short")
BOSS = dict(color=K.DARK, hair="short")
CRIMES = ("空话连篇", "装腔作势", "无的放矢", "语言无味", "甲乙丙丁", "不负责任", "流毒全党", "传播出去")


def build():
    shots = [
        # ---- 钩子 1–8
        S("周五晚上写周报", "灵魂拷问", [
            Custom(laptop, x=540, y=800, at=0, enter="pop", w=560, h=350, title="周报.docx", p0=0.1, p1=1, b0=0, b1=3,
                   sfx="pop"),
            Icon("clock", 830, 480, 130, color=K.INK2, at=1, sfx="wood_high"),
            Spark(540, 800, at=3, sfx="ding"),
        ], punch=0.025, flashes=[0]),
        S("洋洋洒洒写满三页", "灵魂拷问", [
            Custom(D.long_doc, x=540, y=820, at=0, enter="fade", b0=0, b1=3, title="周报", pages="3 页"),
        ], hits=[(0, "wood_low", 0.8, "纸"), (1, "shaker", 0.7, "越拉越长"), (3, "ding", 0.8, "三页")]),
        S("领导：说重点", "灵魂拷问", [
            Fig(760, G, 340, at=0, pose="stand", mood="flat", face=-1, **BOSS,
                moves=[(1, dict(pose="point", dur=0.25, sfx="wood_high"))]),
            Bubble("【重点】是啥？", 640, 520, 50, at=1, enter="pop"),
            Fig(280, G, 300, at=0, pose="stand", mood="smile", **ME,
                moves=[(3, dict(mood="surprised", dur=0.2, sfx="rim"))]),
        ], draw=A.ground),
        S("你翻了半天", "灵魂拷问", [
            Fig(400, G, 320, at=0, pose="carry", mood="worried", **ME),
            Icon("question", 650, 520, 90, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 760, 440, 70, color=K.RED, at=2, sfx="wood_high"),
            Icon("question", 230, 470, 80, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("领导转身走了", "灵魂拷问", [
            Fig(640, G, 340, at=0, enter="none", pose="stand", mood="flat", face=1, **BOSS,
                moves=[(1, dict(x=980, dur=0.9, walk=True, sfx="wood_low"))]),
            Fig(280, G, 300, at=0, enter="none", pose="stand", mood="surprised", **ME,
                moves=[(3, dict(pose="sad", mood="sad", dur=0.3, sfx="tom"))]),
        ], draw=A.ground),
        pops("写得长 不等于 【写得好】", "灵魂拷问", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="写作 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("毛选里有篇文章", "毛泽东选集", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《反对党八股》|一九四二年二月", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–12
        S("", "原文", [
            Big("空话连篇", 540, 640, 160, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：原文落版"),
            Big("言之无物", 540, 860, 160, at=1, sfx="kick", sub="《反对党八股》", sub_size=40, shine=True,
                note="原文下半句"),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        S("懒婆娘的裹脚", "原文 · 又长又臭", [
            Custom(D.cloth, x=540, y=780, at=0, enter="fade", b0=0, b1=3),
        ], hits=[(0, "wood_low", 0.8, "布"), (1, "shaker", 0.7, "拉长"), (2, "shaker", 0.7, "拉长"),
                 (3, "rim", 0.9, "臭")]),
        S("群众见了就摇头", "原文 · 群众见了就摇头", [
            Custom(crowd, x=540, y=G, at=0, enter="fade", n=6, s=250, spread=820),
            Icon("cross", 300, 520, 90, color=K.RED, at=1, sfx="rim"),
            Icon("cross", 540, 480, 110, color=K.RED, at=2, sfx="rim"),
            Icon("cross", 780, 520, 90, color=K.RED, at=3, sfx="rim"),
        ]),
        S("他列了八大罪状", "原文 · 八大罪状", [
            Counter(0, 8, 540, 740, 260, at=0, land=2, suffix="条", sub="罪状"),
            Icon("megaphone", 540, 470, 120, color=ACC, at=3, sfx="wood_high"),
        ], hits=[(0, "shaker", 0.8, "滚动")]),
        # ---- 八条罪状 13–23
        S("装腔作势，借以吓人", "罪状 · 二", [
            Fig(540, G, 360, at=0, pose="proud", mood="angry", **BOSS,
                moves=[(2, dict(pose="fist", dur=0.2, sfx="kick"))]),
            Icon("megaphone", 800, 560, 150, color=K.INK2, at=1, sfx="wood_high"),
            Fig(230, G, 240, at=0, pose="cover", mood="worried", color=K.OTHER, hair="long"),
        ], draw=A.ground, shake=[2]),
        S("无的放矢，不看对象", "罪状 · 三", [
            Custom(D.target, x=540, y=760, at=0, enter="pop", arrows=[(1, False), (2, False)], sfx="pop"),
        ], hits=[(1, "rim", 0.9, "射偏"), (2, "rim", 0.9, "又射偏")]),
        S("射箭要看靶子", "原文 · 射箭要看靶子", [
            Custom(D.target, x=540, y=760, at=0, enter="pop", arrows=[(2, True)], label="靶子", sfx="pop"),
        ], hits=[(2, "kick", 1.0, "正中靶心")], flashes=[2]),
        S("弹琴要看听众", "原文 · 弹琴要看听众", [
            Custom(crowd, x=540, y=G, at=0, enter="fade", n=5, s=240, spread=760),
            Label("听众是谁？", 540, 520, 54, at=1, sfx="pop"),
            Icon("eye", 540, 400, 110, color=ACC, at=2, sfx="ding"), Spark(540, 400, at=2),
        ]),
        S("对牛弹琴，笑弹琴人", "原文 · 讥笑弹琴者", [
            Fig(300, G, 320, at=0, pose="wave", mood="happy", **ME),
            Label("对牛弹琴", 300, 470, 46, at=0, sfx="pop"),
            Custom(crowd, x=760, y=G, at=1, enter="fade", n=3, s=230, spread=360),
            Bubble("听不懂", 760, 560, 44, at=2, enter="pop", sfx="wood_high"),
            Icon("cross", 300, 640, 120, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("语言无味，像个瘪三", "罪状 · 四", [
            Custom(A.talker, x=540, y=780, at=0, enter="fade", b0=0, step=1,
                   words=("综上所述", "综上所述", "总而言之", "综上所述")),
        ], hits=[(0, "pop", 0.8, "套话"), (1, "pop", 0.8, "套话"), (2, "pop", 0.8, "套话"), (3, "rim", 0.9, "又是套话")]),
        S("甲乙丙丁，开中药铺", "罪状 · 五", [
            Custom(D.drawers, x=540, y=780, at=0, enter="pop", b0=0, step=0.25,
                   labels=("壹", "贰", "叁", "肆", "一", "二", "三", "四", "甲", "乙", "丙", "丁", "子", "丑", "寅", "卯"),
                   sfx="wood_low"),
        ], hits=[(1, "pop", 0.7, "抽屉"), (2, "pop", 0.7, "抽屉"), (3, "ding", 0.8, "满柜")]),
        pops("大壹贰叁肆 小一二三四", "原文 · 开中药铺", size=110, flash=None),
        S("不负责任，到处害人", "罪状 · 六", [
            Custom(A.pit, x=540, y=900, at=0, enter="fade", fall=1, label="不负责任"),
        ], hits=[(0, "wood_low", 0.8, "坑"), (1, "tom", 0.8, "掉坑"), (2, "tom", 0.8, "掉坑")]),
        S("下笔千言，离题万里", "原文 · 下笔千言", [
            Custom(D.long_doc, x=300, y=800, at=0, enter="fade", b0=0, b1=1, title="千言", h0=300, h1=700, w=400),
            Custom(D.target, x=820, y=700, at=0, enter="pop", arrows=[(2, False)], r=150),
        ], hits=[(0, "shaker", 0.7, "下笔千言"), (2, "rim", 1.0, "离题")]),
        S("八条，条条扎心", "原文 · 八大罪状", [
            Custom(D.drawers, x=540, y=780, at=0, enter="pop", b0=0.5, step=0.375, cols=2, cw=330, labels=CRIMES),
        ], hits=[(0, "wood_low", 0.8, "清单"), (1, "pop", 0.7, "罪状"), (2, "pop", 0.7, "罪状"), (3, "ding", 0.9, "八条")]),
        # ---- 二次钩子 24–26
        S("可他不是说要短", "原文 · 不是说都以短为好", [
            Custom(D.long_doc, x=300, y=800, at=0, enter="pop", b0=0, b1=0.5, title="长", h0=600, h1=600, w=360, sfx="pop"),
            Custom(D.long_doc, x=780, y=800, at=1, enter="pop", b0=1, b1=1.5, title="短", h0=260, h1=260, w=360, sfx="pop"),
            Icon("question", 540, 500, 110, color=K.RED, at=3, sfx="rim"),
        ]),
        S("看菜吃饭，量体裁衣", "原文 · 看菜吃饭", [
            Card("到什么山上|唱什么歌", 540, 640, 56, at=0, sfx="pop"),
            Icon("check", 540, 900, 130, color=K.GREEN, at=2, sfx="ding"), Spark(540, 900, at=2),
        ], hits=[(1, "wood_high", 0.7, "俗话")]),
        pops("要的是 【有内容】", "原文 · 需要有内容的文章", size=150, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 当下 27–33
        S("今天：周报凑字数", "当下 · 现象", [
            Custom(D.long_doc, x=540, y=820, at=0, enter="fade", b0=0, b1=2, title="周报"),
            Counter(0, 3000, 820, 520, 110, at=0, land=3, suffix="字", sub="凑出来的"),
        ], hits=[(0, "shaker", 0.7, "凑字数")]),
        S("汇报堆满黑话", "当下 · 现象", [
            Custom(D.slide, x=540, y=780, at=0, enter="pop", b0=1, step=0.5, title="汇报",
                   words=("赋能", "抓手", "闭环", "颗粒度", "对齐", "打通"), sfx="pop"),
        ], hits=[(1, "pop", 0.7, "黑话"), (2, "pop", 0.7, "黑话"), (3, "rim", 0.9, "满屏")]),
        S("分点层层套娃", "当下 · 现象", [
            Custom(D.nested, x=540, y=780, at=0, enter="pop", b0=0, step=0.75, sfx="pop"),
        ], hits=[(1, "wood_high", 0.7, "套娃"), (2, "wood_high", 0.7, "套娃"), (3, "rim", 0.9, "套娃")]),
        S("读的人看不懂", "当下 · 现象", [
            Fig(540, G, 330, at=0, pose="think", mood="worried", color=K.OTHER2, hair="long"),
            Icon("phone", 760, 600, 120, color=K.INK2, at=0, sfx="pop"),
            Icon("question", 420, 460, 80, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 620, 420, 100, color=K.RED, at=2, sfx="wood_high"),
        ], draw=A.ground, hits=[(3, "rim", 0.8, "看不懂")]),
        S("赶快扔进垃圾桶", "原文 · 扔到垃圾桶里去", [
            Custom(D.trash, x=540, y=820, at=0, enter="fade", b=1, label="裹脚布"),
        ], hits=[(0, "wood_low", 0.8, "桶"), (1, "tom", 0.9, "扔进去"), (2, "ding", 0.8, "清爽")]),
        pops("写给谁看 先 【想清楚】", "一句话", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("把读者放第一", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("堆字数", K.INK2), ("套话", K.GOLD), ("分点", K.GREEN), ("读者", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "读者置顶")], flashes=[1], shake=[1]),
        # ---- 写作 4 招 34–41
        S("书里给了改法", "原文 · 怎么改", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="写作 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 有内容再动笔", "写作 4 招 · 拿不出来的就不要拿出来", [
            Custom(A.notebook, x=540, y=800, at=0, enter="pop", b0=0, step=1, lines=("事实：", "问题：", "建议：")),
            Icon("check", 820, 470, 110, color=K.GREEN, at=3, sfx="ding"),
        ], hits=[(0, "shaker", 0.7, "写"), (1, "shaker", 0.7, "写"), (2, "shaker", 0.7, "写")]),
        S("② 先看读者是谁", "写作 4 招 · 射箭要看靶子", [
            Custom(D.target, x=540, y=720, at=0, enter="pop", arrows=[(2, True)], label="读者", sfx="pop"),
        ], hits=[(1, "wood_high", 0.7, "瞄准"), (2, "kick", 1.0, "命中")], flashes=[2]),
        S("③ 用大白话写", "写作 4 招 · 向人民群众学习语言", [
            Card("赋能", 300, 640, 60, at=0, sfx="pop"),
            Icon("cross", 300, 880, 120, color=K.RED, at=1, sfx="rim"),
            Card("帮他做成", 780, 640, 60, at=2, sfx="pop"),
            Icon("check", 780, 880, 120, color=K.GREEN, at=3, sfx="ding"),
        ]),
        S("④ 写完照照镜子", "写作 4 招 · 像洗脸一样负责", [
            Icon("mirror", 540, 640, 260, color=ACC, at=0, sfx="pop"),
            Fig(240, G, 300, at=1, pose="think", mood="smile", **ME, sfx="pop"),
            Spark(540, 640, at=2, sfx="ding"),
            Icon("check", 820, 520, 110, color=K.GREEN, at=3, sfx="ding"),
        ], draw=A.ground),
        S("三页改成一页", "落到自己 · 小建议", [
            Custom(D.long_doc, x=540, y=820, at=0, enter="fade", b0=0, b1=2, title="周报", h0=820, h1=320,
                   pages="1 页"),
        ], hits=[(0, "wood_low", 0.8, "三页"), (2, "ding", 0.9, "一页")]),
        S("重点写第一句", "落到自己 · 小建议", [
            Card("结论：本周上线|原因：……", 540, 720, 54, at=0, sfx="pop"),
            Rays(540, 640, 400, at=1, alpha=0.2), Spark(540, 640, at=1, sfx="ding"),
            Icon("eye", 540, 960, 110, color=K.INK2, at=2, sfx="wood_high"),
        ]),
        S("领导一看就懂", "落到自己", [
            Fig(700, G, 340, at=0, pose="stand", mood="smile", face=-1, **BOSS,
                moves=[(1, dict(pose="cheer", mood="happy", dur=0.25, sfx="pop"))]),
            Fig(300, G, 300, at=0, pose="stand", mood="happy", **ME),
            Icon("check", 700, 440, 110, color=K.GREEN, at=2, sfx="ding"), Spark(700, 440, at=2),
        ], draw=A.ground),
        # ---- 片尾 42
        outro("你见过最长的周报有几页？", "开会说漂亮话，为什么没用？", "写之前，先想读者"),
    ]
    return episode(8, "stereotyped", "反对党八股", "写的报告，为什么没人看？", ACC, shots,
                   [f"{BOOK}第三卷《反对党八股》（一九四二年二月八日）"],
                   "又长又空|等于不想让人【看】", 8,
                   ["引文出自《反对党八股》：八大罪状“空话连篇，言之无物”“装腔作势，借以吓人”“无的放矢，不看对象”"
                    "“语言无味，像个瘪三”“甲乙丙丁，开中药铺”“不负责任，到处害人”“流毒全党，妨害革命”“传播出去，祸国殃民”"
                    "（清单只列每条前四字）；“懒婆娘的裹脚，又长又臭”“群众见了就摇头”“射箭要看靶子，弹琴要看听众”"
                    "“下笔千言，离题万里”“不是说任何东西都以短为好”“到什么山上唱什么歌”“看菜吃饭，量体裁衣”"
                    "“尤其需要有内容的文章”“扔到垃圾桶里去”；中药铺抽屉标签取自原文“大壹贰叁肆，小一二三四，甲乙丙丁，子丑寅卯”。",
                    "写作 4 招对应原文：“拿不出来的东西就不要拿出来”“射箭要看靶子”“要向人民群众学习语言”"
                    "“只要像洗脸这样负责”（写完照镜子为比喻）；“三页改一页”“重点写第一句”为创作者的小建议，不是书中原话。",
                    "“当下”部分为现象示意（周报字数、黑话词为示意），不点名任何公司；画面不出现历史人物形象。"],
                   tags="#写作 #周报")
