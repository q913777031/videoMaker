"""09 实事求是：开会说漂亮话，为什么没用？（快节奏版：42 镜 × 1 小节）

原文出自《改造我们的学习》（一九四一年五月，《毛泽东选集》第三卷）：“‘实事’就是客观存在着的一切事物，‘是’就是
客观事物的内部联系，即规律性，‘求’就是我们去研究。”“从客观的真实的情况出发，而不是从主观的愿望出发”
“往往单凭热情，把感想当政策”“‘闭塞眼睛捉麻雀’，‘瞎子摸鱼’，粗枝大叶，夸夸其谈，满足于一知半解”
“仅仅根据一知半解，根据‘想当然’，就在那里发号施令”“或作讲演，则甲乙丙丁、一二三四的一大串”
“无实事求是之意，有哗众取宠之心。华而不实，脆而不坚。”对子“墙上芦苇，头重脚轻根底浅；山间竹笋，嘴尖皮厚腹中空。”
“你们看，像不像？”“把它贴在自己房子里的墙壁上”“科学是老老实实的学问”；方法：“不凭主观想象，不凭一时的热情，
不凭死的书本，而凭客观存在的事实，详细地占有材料”“找出周围事变的内部联系”“有的放矢”。
"""

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Counter, Custom, Fig, Icon, Label, Rays, Spark
from scarcity.art import laptop
from zizhi.art import crack_char, magnifier

from . import art as A
from . import art_d as D
from .common import BOOK, S, episode, outro, pops

ACC = A.RED
G = A.GROUND_Y
ME = dict(hair="short")
BOSS = dict(color=K.DARK, hair="short")


def build():
    shots = [
        # ---- 钩子 1–8
        S("开会轮到你发言", "灵魂拷问", [
            Custom(A.meeting, x=540, y=760, at=0, enter="fade", b0=1, title="季度复盘"),
        ], punch=0.025, flashes=[0], hits=[(0, "wood_low", 0.8, "会议室"), (1, "pop", 0.8, "柱子长高"),
                                           (2, "ding", 0.7, "图表")]),
        S("你说：形势一片大好", "灵魂拷问", [
            Custom(A.talker, x=540, y=780, at=0, enter="fade", b0=0, step=1,
                   words=("一片大好", "全面突破", "稳中向好", "马上落地")),
        ], hits=[(0, "pop", 0.8, "漂亮话"), (1, "pop", 0.8, "漂亮话"), (2, "pop", 0.8, "漂亮话"), (3, "ding", 0.8, "漂亮话")]),
        S("领导问：数据呢？", "灵魂拷问", [
            Fig(760, G, 340, at=0, pose="stand", mood="flat", face=-1, **BOSS,
                moves=[(1, dict(pose="point", dur=0.25, sfx="wood_high"))]),
            Bubble("【数据】呢？", 640, 520, 54, at=1, enter="pop"),
            Fig(280, G, 300, at=0, pose="stand", mood="smile", **ME,
                moves=[(3, dict(mood="surprised", dur=0.2, sfx="rim"))]),
        ], draw=A.ground),
        S("你：大概……应该……", "灵魂拷问", [
            Fig(400, G, 320, at=0, pose="shrug", mood="worried", **ME),
            Bubble("大概……", 660, 520, 44, at=1, enter="pop", sfx="wood_high"),
            Bubble("应该……", 760, 660, 44, at=2, enter="pop", sfx="wood_high"),
            Icon("question", 260, 460, 80, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("会议室突然安静", "灵魂拷问", [
            Custom(crack_char, x=540, y=740, at=0, enter="pop", text="静", s=380, split=2, sfx="wood_low"),
        ], hits=[(2, "rim", 1.0, "尴尬裂开")], shake=[2]),
        pops("话说得 再漂亮 也不顶 【事】", "灵魂拷问", size=120, flash=3,
             extra=[Rays(540, 780, 620, at=3, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="务实 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("毛选里有篇文章", "毛泽东选集", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《改造我们的学习》|一九四一年五月", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–13
        S("", "原文", [
            Big("实事求是", 540, 720, 220, at=0, sfx="kick", sub="《改造我们的学习》", sub_size=40, rays=True,
                glow=True, shine=True, spark=True, note="drop：原文落版"),
            Spark(540, 720, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0], shake=[0]),
        S("实事：客观事物", "原文 · 实事", [
            Big("实事", 540, 600, 170, at=0, sfx="kick", glow=True),
            Card("客观存在着的|一切事物", 540, 880, 52, at=1, sfx="pop"),
            Spark(540, 880, at=2, sfx="ding"),
        ]),
        S("是：内部规律", "原文 · 是", [
            Big("是", 540, 600, 200, at=0, sfx="kick", glow=True),
            Card("客观事物的内部联系|即规律性", 540, 880, 50, at=1, sfx="pop"),
            Spark(540, 880, at=2, sfx="ding"),
        ]),
        S("求：去研究", "原文 · 求", [
            Big("求", 540, 600, 200, at=0, sfx="kick", glow=True),
            Card("就是我们去研究", 540, 880, 54, at=1, sfx="pop"),
            Custom(A.footprints, x=540, y=900, at=2, enter="none", n=4, b0=2, step=0.5),
        ], hits=[(2, "wood_high", 0.7, "走"), (3, "wood_high", 0.7, "走")]),
        pops("从 【事实】 出发", "原文 · 从客观的真实的情况出发", size=150, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        # ---- 反面 14–22
        S("把感想当政策", "原文 · 把感想当政策", [
            Icon("bulb", 300, 700, 180, color=K.GOLD, at=0, sfx="pop"), Label("感想", 300, 900, 46, at=0),
            Arrow((420, 700), (620, 700), at=1, sfx="wood_high"),
            Card("政策", 780, 700, 70, at=2, sfx="kick"),
            Icon("cross", 780, 900, 110, color=K.RED, at=3, sfx="rim"),
        ]),
        S("闭塞眼睛捉麻雀", "原文 · 闭塞眼睛捉麻雀", [
            Custom(D.blind_catch, x=540, y=780, at=0, enter="fade", grab=2),
        ], hits=[(0, "wood_low", 0.7, "蒙眼"), (2, "rim", 1.0, "扑空")]),
        S("瞎子摸鱼", "原文 · 瞎子摸鱼", [
            Custom(D.blind_catch, x=540, y=780, at=0, enter="fade", grab=2, fish=True),
        ], hits=[(0, "wood_low", 0.7, "下水"), (2, "rim", 1.0, "鱼跑了")]),
        S("粗枝大叶，夸夸其谈", "原文 · 粗枝大叶", [
            Custom(A.talker, x=540, y=780, at=0, enter="fade", b0=0, step=1,
                   words=("差不多", "没问题", "包在我", "身上")),
        ], hits=[(0, "pop", 0.8, "空话"), (1, "pop", 0.8, "空话"), (2, "pop", 0.8, "空话"), (3, "rim", 0.9, "空话")]),
        S("满足于一知半解", "原文 · 满足于一知半解", [
            Custom(laptop, x=540, y=780, at=0, enter="pop", w=560, h=350, title="了解程度", p0=0, p1=0.5, b0=0, b1=2,
                   sfx="pop"),
            Label("就这？", 830, 520, 50, at=3, sfx="rim", fill=K.RED),
        ], hits=[(2, "ding", 0.8, "停在一半")]),
        S("凭想当然发号令", "原文 · 根据想当然", [
            Fig(540, G, 340, at=0, pose="point", mood="angry", **BOSS,
                moves=[(2, dict(pose="fist", dur=0.2, sfx="kick"))]),
            Icon("megaphone", 800, 560, 150, color=K.INK2, at=1, sfx="wood_high"),
            Bubble("我觉得【行】", 280, 520, 48, at=1, enter="pop"),
        ], draw=A.ground, shake=[2]),
        S("甲乙丙丁一大串", "原文 · 甲乙丙丁、一二三四的一大串", [
            Custom(D.drawers, x=540, y=760, at=0, enter="pop", b0=0.5, step=0.375,
                   labels=("甲", "乙", "丙", "丁", "一", "二", "三", "四"), sfx="wood_low"),
            Bubble("还有……", 820, 470, 44, at=3, enter="pop", sfx="rim"),
        ], hits=[(1, "pop", 0.7, "一串"), (2, "pop", 0.7, "一串")]),
        S("", "原文", [
            Big("无实事求是之意", 540, 660, 110, at=0, sfx="kick", glow=True),
            Big("有哗众取宠之心", 540, 880, 110, at=1, sfx="kick", shine=True),
            Spark(540, 880, at=2, sfx="ding"),
        ], punch=0.025, flashes=[0]),
        S("华而不实，脆而不坚", "原文 · 华而不实", [
            Custom(crack_char, x=540, y=740, at=0, enter="pop", text="华", s=380, split=2, sfx="ding"),
        ], hits=[(2, "rim", 1.0, "一碰就裂")], shake=[2]),
        # ---- 对子 23–27
        S("有副对子画像", "原文 · 对子", [
            Custom(D.couplet, x=540, y=780, at=0, enter="fade", b0=0, step=0.25,
                   left="墙上芦苇头重脚轻根底浅", right="山间竹笋嘴尖皮厚腹中空"),
        ], hits=[(0, "wood_low", 0.8, "上联"), (1, "shaker", 0.6, "写"), (2, "shaker", 0.6, "写"),
                 (3, "ding", 0.8, "下联")]),
        S("头重脚轻根底浅", "原文 · 墙上芦苇", [
            Custom(D.reed, x=540, y=760, at=0, enter="fade", sway=1, lab=2),
        ], hits=[(0, "wood_low", 0.8, "墙"), (1, "shaker", 0.8, "摇晃"), (2, "pop", 0.8, "头重脚轻"),
                 (3, "pop", 0.8, "根底浅")]),
        S("嘴尖皮厚腹中空", "原文 · 山间竹笋", [
            Custom(D.shoot, x=540, y=760, at=0, enter="fade", lab=1, cut=2),
        ], hits=[(0, "wood_low", 0.8, "竹笋"), (1, "pop", 0.8, "嘴尖"), (2, "rim", 1.0, "剖开")]),
        pops("你们看 【像不像】？", "原文 · 你们看，像不像？", size=150, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        S("劝你贴在墙上", "原文 · 贴在墙壁上", [
            Custom(D.couplet, x=540, y=780, at=0, enter="pop", b0=-9, step=0.1,
                   left="墙上芦苇头重脚轻根底浅", right="山间竹笋嘴尖皮厚腹中空", sfx="kick"),
            Fig(540, G, 260, at=1, pose="think", mood="worried", **ME, sfx="pop"),
            Icon("eye", 540, 420, 100, color=ACC, at=2, sfx="ding"),
        ], draw=A.ground),
        # ---- 当下 28–34
        S("今天：汇报只报喜", "当下 · 现象", [
            Custom(A.meeting, x=540, y=760, at=0, enter="fade", b0=0, title="全是好消息"),
            Icon("check", 300, 400, 90, color=K.GREEN, at=1, sfx="ding"),
            Icon("check", 780, 400, 90, color=K.GREEN, at=2, sfx="ding"),
        ], hits=[(3, "ding", 0.8, "又一个好消息")]),
        S("问题藏进脚注", "当下 · 现象", [
            Custom(D.long_doc, x=540, y=820, at=0, enter="fade", b0=0, b1=1, title="汇报", h0=500, h1=700),
            Custom(magnifier, x=760, y=1080, at=1, enter="pop", r=110, sfx="wood_high"),
            Label("风险：……", 700, 1090, 30, at=3, sfx="rim", fill=K.RED),
        ], hits=[(0, "wood_low", 0.8, "文档")]),
        S("方案全是形容词", "当下 · 现象", [
            Custom(D.slide, x=540, y=780, at=0, enter="pop", b0=1, step=0.5, title="方案",
                   words=("极致", "全面", "深度", "高效", "颠覆", "领先"), sfx="pop"),
        ], hits=[(1, "pop", 0.7, "形容词"), (2, "pop", 0.7, "形容词"), (3, "rim", 0.9, "满屏")]),
        S("落地全靠想当然", "当下 · 现象", [
            Custom(A.pit, x=540, y=900, at=0, enter="fade", fall=1, label="想当然"),
        ], hits=[(0, "wood_low", 0.8, "坑"), (1, "tom", 0.8, "掉坑"), (2, "tom", 0.8, "掉坑")]),
        S("最后项目翻车", "当下 · 现象", [
            Custom(A.thing, x=540, y=780, at=0, enter="pop", obj="car", s=380, sfx="wood_low",
                   moves=[(2, dict(rot=160, y=840, dur=0.35, sfx="kick"))]),
            Icon("cross", 540, 480, 120, color=K.RED, at=3, sfx="rim"),
        ], shake=[2], flashes=[2]),
        pops("数据 比 【形容词】 有力", "一句话", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("先摆事实再说话", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("形容词", K.INK2), ("口号", K.GOLD), ("表态", K.GREEN), ("事实", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "事实置顶")], flashes=[1], shake=[1]),
        # ---- 务实 4 招 35–41
        S("书里给了方法", "原文 · 怎么做", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="务实 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 只凭事实说话", "务实 4 招 · 不凭主观想象", [
            Card("主观想象", 300, 560, 46, at=0, sfx="pop"), Card("一时热情", 780, 560, 46, at=0),
            Card("死的书本", 300, 760, 46, at=0),
            Icon("cross", 540, 660, 160, color=K.RED, at=1, sfx="rim"),
            Card("【客观存在的事实】", 640, 960, 52, at=2, sfx="ding"),
            Spark(640, 960, at=3, sfx="ding"),
        ]),
        S("② 材料占全", "务实 4 招 · 详细地占有材料", [
            Custom(A.papers, x=540, y=820, at=0, enter="fade", b0=0, b1=2, title="材料"),
            Icon("check", 820, 500, 110, color=K.GREEN, at=3, sfx="ding"),
        ], hits=[(0, "shaker", 0.8, "收集"), (2, "wood_low", 0.8, "堆满")]),
        S("③ 找出内部联系", "务实 4 招 · 找出内部联系", [
            Custom(A.head_fill, x=540, y=780, at=0, enter="pop", fill=1, step=0.5,
                   items=[("原因", ACC), ("结果", K.INK2), ("规律", K.GOLD), ("对策", K.GREEN)]),
        ], hits=[(0, "pop", 0.8, "脑袋"), (1, "pop", 0.8, "原因"), (2, "pop", 0.8, "规律"), (3, "ding", 0.9, "连起来")]),
        S("④ 有的放矢", "务实 4 招 · 有的放矢", [
            Custom(D.target, x=540, y=720, at=0, enter="pop", arrows=[(2, True)], label="的＝要解决的问题", sfx="pop"),
        ], hits=[(1, "wood_high", 0.7, "瞄准"), (2, "kick", 1.0, "命中")], flashes=[2]),
        S("老老实实的学问", "原文 · 科学是老老实实的学问", [
            Custom(A.notebook, x=540, y=800, at=0, enter="pop", b0=0, step=1,
                   lines=("事实：", "数据：", "问题：", "下一步：")),
        ], hits=[(0, "shaker", 0.7, "写"), (1, "shaker", 0.7, "写"), (2, "shaker", 0.7, "写"), (3, "ding", 0.9, "写完")]),
        S("开会有一说一", "落到自己", [
            Fig(700, G, 340, at=0, pose="stand", mood="smile", face=-1, **BOSS,
                moves=[(2, dict(pose="cheer", mood="happy", dur=0.25, sfx="pop"))]),
            Fig(300, G, 300, at=0, pose="point", mood="happy", **ME),
            Bubble("数据是【这样】", 420, 540, 46, at=1, enter="pop", sfx="wood_high"),
            Icon("check", 700, 440, 110, color=K.GREEN, at=3, sfx="ding"), Spark(700, 440, at=3),
        ], draw=A.ground),
        # ---- 片尾 42
        outro("你开会时说过哪句漂亮话？", "事太难，还干不干？", "少说形容词，多摆事实"),
    ]
    return episode(9, "truth", "实事求是", "开会说漂亮话，为什么没用？", ACC, shots,
                   [f"{BOOK}第三卷《改造我们的学习》（一九四一年五月）"],
                   "话再漂亮|不如【事实】", 8,
                   ["引文出自《改造我们的学习》：“‘实事’就是客观存在着的一切事物，‘是’就是客观事物的内部联系，即规律性，"
                    "‘求’就是我们去研究”“从客观的真实的情况出发”“把感想当政策”“闭塞眼睛捉麻雀”“瞎子摸鱼”“粗枝大叶，夸夸其谈”"
                    "“满足于一知半解”“根据‘想当然’，就在那里发号施令”“无实事求是之意，有哗众取宠之心”“华而不实，脆而不坚”"
                    "“墙上芦苇，头重脚轻根底浅；山间竹笋，嘴尖皮厚腹中空”“你们看，像不像？”“贴在自己房子里的墙壁上”"
                    "“科学是老老实实的学问”。",
                    "务实 4 招对应原文：“不凭主观想象，不凭一时的热情，不凭死的书本，而凭客观存在的事实”“详细地占有材料”"
                    "“找出周围事变的内部联系”“有的放矢”；原文的“的”指中国革命，片中“的＝要解决的问题”为今日化引申。",
                    "芦苇、竹笋画面为对子的图解示意；“当下”部分为现象示意，不点名任何公司；画面不出现历史人物形象。"],
                   tags="#实事求是 #开会")
