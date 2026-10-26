"""01 没有调查没有发言权：汇报被领导一句话问住，差在哪？（快节奏版：42 镜 × 1 小节）

原文出自《反对本本主义》（一九三〇年五月，《毛泽东选集》第一卷）：“没有调查，没有发言权”“便一定是瞎说一顿”
“调查就像‘十月怀胎’，解决问题就像‘一朝分娩’。调查就是解决问题。”“开口闭口‘拿本本来’”“一味盲目执行”
“迈开你的两脚……未出门时脑子是空的，归来时脑子已经不是空的了”“一切结论产生于调查情况的末尾，而不是在它的先头”
“他一定要产生错办法和错主意”“喜欢一到就宣布政见……指手画脚”；第七节“调查的技术”：要开调查会、至少需要三人、
要定调查纲目（商业→布匹、粮食、杂货、药材→洋布、土布、绸缎）、要亲身出马（不能单靠书面报告）、要自己做记录。
寻乌调查：1930 年 5 月在江西寻乌开调查会 10 多天，郭友梅等提供材料，1931 年整理为 8 万多字的《寻乌调查》（求是网）。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Counter, Custom, Fig, Icon, Label, Rays, Spark
from scarcity.art import laptop

from . import art as A
from .common import BOOK, S, episode, outro, pops

ACC = A.RED
G = A.GROUND_Y
ME = dict(hair="short")
BOSS = dict(color=K.DARK, hair="short")


def build():
    shots = [
        # ---- 钩子 1–8
        S("例会上，轮到你汇报", "灵魂拷问", [
            Custom(A.meeting, x=540, y=760, at=0, enter="fade", b0=1),
        ], punch=0.025, flashes=[0], hits=[(0, "wood_low", 0.8, "会议室"), (1, "pop", 0.8, "柱子长高"),
                                           (2, "ding", 0.7, "图表")]),
        S("汇报熬了一整晚", "灵魂拷问", [
            Custom(laptop, x=540, y=800, at=0, enter="pop", w=560, h=350, title="汇报.pptx", p0=0.3, p1=1, b0=0, b1=3,
                   sfx="pop"),
            Icon("clock", 830, 480, 130, color=K.INK2, at=1, sfx="wood_high"),
            Spark(540, 800, at=3, sfx="ding"),
        ]),
        S("领导问：数据哪来的？", "灵魂拷问", [
            Fig(760, G, 340, at=0, pose="stand", mood="flat", face=-1, **BOSS,
                moves=[(1, dict(pose="point", dur=0.25, sfx="wood_high"))]),
            Bubble("数据【哪来的】？", 640, 520, 50, at=1, enter="pop"),
            Fig(280, G, 300, at=0, pose="stand", mood="smile", **ME,
                moves=[(3, dict(mood="surprised", dur=0.2, sfx="rim"))]),
        ], draw=A.ground),
        S("“网上……搜的”", "灵魂拷问", [
            Fig(400, G, 320, at=0, pose="shrug", mood="worried", **ME),
            Icon("phone", 700, 640, 160, color=K.INK2, at=1, sfx="pop"),
            Icon("question", 700, 450, 90, color=K.RED, at=2, sfx="rim"),
            Icon("question", 260, 470, 80, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("“你去现场看过吗？”", "灵魂拷问", [
            Fig(760, G, 340, at=0, enter="none", pose="point", mood="angry", face=-1, **BOSS),
            Bubble("你去【现场】看过吗？", 600, 500, 48, at=0, enter="pop", sfx="kick"),
            Fig(280, G, 300, at=0, enter="none", pose="stand", mood="surprised", **ME,
                moves=[(2, dict(pose="sad", mood="sad", dur=0.3, sfx="tom"))]),
        ], draw=A.ground, shake=[0]),
        pops("不是你笨 是你 【没去看】", "灵魂拷问", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="调查 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("毛选里有篇文章", "毛泽东选集", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《反对本本主义》|一九三〇年五月", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–12
        S("", "原文", [
            Big("没有调查", 540, 640, 150, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：原文落版"),
            Big("没有发言权", 540, 860, 150, at=1, sfx="kick", sub="《反对本本主义》", sub_size=40, shine=True,
                note="原文下半句"),
            Spark(540, 860, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        S("没调查=瞎说一顿", "原文 · 便一定是瞎说一顿", [
            Custom(A.talker, x=540, y=780, at=0, enter="fade", b0=0, step=1,
                   words=("我觉得", "应该是", "肯定行", "听我的")),
        ], hits=[(0, "pop", 0.8, "我觉得"), (1, "pop", 0.8, "应该是"), (2, "pop", 0.8, "肯定行"),
                 (3, "rim", 0.9, "听我的")]),
        S("十月怀胎，一朝分娩", "原文 · 十月怀胎", [
            Custom(A.months, x=540, y=780, at=0, enter="fade", b0=0, step=0.33, last=3),
        ], hits=[(0, "shaker", 0.8, "调查一格格点亮"), (3, "ding", 1.0, "解决")]),
        pops("调查 就是 【解决问题】", "原文 · 调查就是解决问题", size=140, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 本本主义 13–17
        S("那年，红四军里", "写作背景", [
            Counter(1900, 1930, 540, 720, 220, at=0, land=2, fmt="{:.0f}", sub="年 · 红四军"),
        ], hits=[(0, "shaker", 0.8, "年份滚动")]),
        S("有人开口闭口", "原文 · 拿本本来", [
            Fig(400, G, 330, at=0, pose="stand", mood="open", color="#7A6A55", hair="cap",
                moves=[(1, dict(pose="fist", dur=0.25, sfx="wood_high"))]),
            Bubble("拿【本本】来！", 700, 540, 54, at=1, enter="pop"),
            Icon("book", 760, 800, 150, color=ACC, at=2, sfx="pop"), Spark(760, 800, at=2),
        ], draw=A.ground),
        S("书上写的，就照办", "原文 · 以为上了书的就是对的", [
            Card("书上写的", 300, 640, 54, at=0, sfx="pop"),
            Icon("check", 300, 860, 130, color=K.GREEN, at=1, sfx="ding"),
            Card("实际情况", 780, 640, 54, at=2, sfx="pop"),
            Icon("cross", 780, 860, 130, color=K.RED, at=3, sfx="rim"),
        ]),
        S("一味盲目执行", "原文 · 一味盲目执行", [
            Custom(A.blind_walk, x=540, y=780, at=0, enter="fade", b0=0, bump=2, wall=280),
        ], hits=[(0, "wood_low", 0.7, "走"), (2, "kick", 1.0, "撞墙")], shake=[2], flashes=[2]),
        S("怎么治？只有一招", "原文 · 只有向实际情况作调查", [
            Big("调查", 540, 720, 240, at=1, sfx="kick", rays=True, glow=True, spark=True),
            Icon("question", 540, 480, 110, color=K.RED, at=0, sfx="wood_high"),
        ], punch=0.025, shake=[1]),
        # ---- 迈开两脚 18–19
        S("迈开你的两脚", "原文 · 迈开你的两脚", [
            Custom(A.footprints, x=540, y=800, at=0, enter="none", n=7, b0=0, step=0.5, label="去现场"),
        ], hits=[(0, "wood_high", 0.7, "第一步"), (1, "wood_high", 0.7, "迈步"), (2, "wood_high", 0.7, "迈步"),
                 (3, "ding", 0.9, "到现场")]),
        S("出门前脑子是空的", "原文 · 归来时脑子已经不是空的了", [
            Custom(A.head_fill, x=540, y=780, at=0, enter="pop", fill=2, step=0.5,
                   items=[("现状", ACC), ("历史", K.INK2), ("数字", K.GREEN), ("原因", K.GOLD)]),
        ], hits=[(0, "pop", 0.8, "空脑袋"), (2, "ding", 0.9, "装满"), (3, "pop", 0.8, "装满")]),
        # ---- 寻乌调查 20–25
        S("他自己就这么干", "寻乌调查", [
            Custom(A.map_pin, x=540, y=780, at=0, enter="fade", pin=1, region="江西", place="1930.5 寻乌"),
        ], hits=[(0, "wood_low", 0.8, "地图"), (1, "kick", 0.9, "图钉落下"), (2, "pop", 0.8, "地名")]),
        S("调查会开了十多天", "寻乌调查", [
            Counter(0, 10, 540, 760, 260, at=0, land=2, suffix="多天", sub="调查会"),
            Icon("clock", 540, 460, 110, color=K.INK2, at=3, sfx="wood_high"),
        ], hits=[(0, "shaker", 0.8, "滚动")]),
        S("店主、老童生、乡干部", "寻乌调查 · 提供材料的人", [
            Fig(230, G, 290, at=0, pose="stand", mood="smile", color=K.OTHER, hair="cap", sfx="pop"),
            Fig(540, G, 300, at=1, pose="wave", mood="happy", color=K.OTHER2, hair="bun", sfx="pop"),
            Fig(850, G, 290, at=2, pose="stand", mood="open", color="#9C8FB0", hair="short", face=-1, sfx="pop"),
            Label("杂货店主", 230, 520, 38, at=0), Label("老童生", 540, 500, 38, at=1),
            Label("乡干部", 850, 520, 38, at=2), Spark(540, 600, at=3, sfx="ding"),
        ], draw=A.ground),
        S("县城的店，一家家问", "寻乌调查 · 商业", [
            Custom(A.shops, x=540, y=800, at=0, enter="fade", b0=0, step=0.5,
                   names=("盐", "杂货", "油", "豆腐", "理发", "打铁", "药材", "爆竹")),
        ], hits=[(0, "pop", 0.7, "盐"), (1, "pop", 0.7, "油"), (2, "pop", 0.7, "理发"), (3, "ding", 0.9, "药材")]),
        S("地主有几个，数清楚", "寻乌调查 · 土地", [
            Counter(0, 8, 220, 760, 140, at=0, land=1, sub="头等大地主"),
            Counter(0, 12, 540, 760, 140, at=0, land=2, sub="大地主"),
            Counter(0, 113, 860, 760, 140, at=0, land=3, sub="中地主"),
        ], hits=[(0, "shaker", 0.8, "滚动")]),
        S("写成八万多字", "寻乌调查", [
            Custom(A.papers, x=540, y=820, at=0, enter="fade", b0=0, b1=2, title="寻乌调查"),
            Counter(0, 8, 840, 520, 150, at=0, land=3, suffix="万+", sub="字"),
        ], hits=[(0, "shaker", 0.8, "纸越堆越高"), (2, "wood_low", 0.8, "堆满")]),
        # ---- 二次钩子 26–30
        S("先下结论？反了", "原文 · 结论产生于调查的末尾", [
            Custom(A.conclusion_line, x=540, y=800, at=0, enter="fade", cross=0, b0=1, end=3),
        ], hits=[(0, "rim", 1.0, "先头的结论打叉"), (1, "wood_high", 0.7, "调查"), (2, "wood_high", 0.7, "调查"),
                 (3, "ding", 1.0, "末尾的结论")], flashes=[0]),
        S("关起门“想办法”？", "原文 · 冥思苦索地想办法", [
            Fig(540, G, 330, at=0, pose="think", mood="worried", **ME),
            Icon("door", 220, 760, 200, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 440, 460, 80, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 640, 430, 100, color=K.RED, at=2, sfx="wood_high"),
            Icon("bulb", 840, 520, 120, color=K.INK2, at=3, sfx="rim"),
        ], draw=A.ground),
        pops("一定要产生 【错主意】", "原文 · 错办法和错主意", size=140, flash=1,
             extra=[Icon("cross", 540, 470, 110, color=K.RED, at=2, sfx="rim")]),
        S("刚到就指手画脚", "原文 · 一到就宣布政见", [
            Fig(540, G, 340, at=0, pose="point", mood="angry", **BOSS,
                moves=[(2, dict(pose="fist", dur=0.2, sfx="kick"))]),
            Bubble("这也【不对】", 300, 520, 46, at=1, enter="pop", sfx="wood_high"),
            Bubble("那也【错误】", 800, 560, 46, at=2, enter="pop"),
        ], draw=A.ground, shake=[2]),
        S("一定弄坏事情", "原文 · 一定要弄坏事情", [
            Custom(A.pit, x=540, y=900, at=0, enter="fade", fall=1, label="瞎说一顿"),
        ], hits=[(0, "wood_low", 0.8, "坑"), (1, "tom", 0.8, "掉坑"), (2, "tom", 0.8, "掉坑")]),
        # ---- 当下 31–36
        S("今天：方案拍脑袋", "当下 · 现象", [
            Fig(400, G, 330, at=0, pose="think", mood="smile", **ME,
                moves=[(1, dict(pose="cheer", mood="happy", dur=0.25, sfx="pop"))]),
            Icon("bulb", 680, 520, 140, color=K.GOLD, at=1), Spark(680, 520, at=1),
            Icon("cross", 680, 520, 160, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("用户要啥？全靠猜", "当下 · 现象", [
            Icon("question", 270, 700, 130, color=K.RED, at=0, sfx="wood_high"),
            Icon("question", 540, 640, 160, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 810, 700, 130, color=K.RED, at=2, sfx="wood_high"),
            Label("我猜", 540, 920, 50, at=3, sfx="rim"),
        ]),
        S("买房只看效果图", "当下 · 现象", [
            Icon("photo", 300, 760, 220, color=K.GOLD, at=0, sfx="pop"),
            Label("效果图", 300, 960, 42, at=0),
            Icon("house", 780, 760, 220, color=K.INK3, at=2, sfx="wood_low"),
            Label("没去现场", 780, 960, 42, at=3, sfx="rim", fill=K.RED),
        ]),
        S("问题越想越大", "当下 · 现象", [
            Fig(540, G, 330, at=0, pose="sit_sad", mood="sad", **ME),
            Icon("cloud", 540, 470, 180, color=K.INK2, at=1, sfx="wood_low"),
            Icon("cloud", 360, 540, 120, color=K.INK3, at=2, sfx="wood_low"),
            Icon("cloud", 730, 540, 140, color=K.INK3, at=3, sfx="wood_low"),
        ], draw=A.ground),
        pops("差的不是脑子 是 【腿】", "一句话", size=140, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("把调查放在开口前", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("开口", K.INK2), ("拍板", K.GOLD), ("执行", K.GREEN), ("调查", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "调查置顶")], flashes=[1], shake=[1]),
        # ---- 调查 4 招 37–41
        S("书里教了调查技术", "原文 · 调查的技术", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="调查 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        S("① 亲自去，别只看报告", "调查 4 招 · 要亲身出马", [
            Custom(A.report, x=300, y=760, at=0, enter="pop", cross=2, sfx="pop"),
            Fig(780, G, 320, at=1, pose="wave", mood="happy", **ME, sfx="pop"),
        ], draw=A.ground, hits=[(2, "kick", 0.9, "盖章")]),
        S("② 找人聊，至少三个", "调查 4 招 · 至少需要三人", [
            Custom(A.round_table, x=540, y=800, at=0, enter="fade", b0=0, roles=("老员工", "一线", "客户")),
            Counter(0, 3, 540, 1180, 100, at=0, land=3, suffix="人"),
        ], hits=[(0, "pop", 0.8, "入座"), (1, "pop", 0.8, "入座"), (2, "pop", 0.8, "入座")]),
        S("③ 先列提纲再发问", "调查 4 招 · 要定调查纲目", [
            Custom(A.outline, x=540, y=800, at=0, enter="fade", b0=0, b1=1, b2=3, step=0.5),
        ], hits=[(0, "pop", 0.8, "大纲"), (1, "pop", 0.8, "细目"), (2, "pop", 0.8, "细目"),
                 (3, "ding", 0.9, "更细")]),
        S("④ 亲手记下来", "调查 4 招 · 要自己做记录", [
            Custom(A.notebook, x=540, y=800, at=0, enter="pop", b0=0, step=1,
                   lines=("现状：", "历史：", "原因：", "办法：")),
        ], hits=[(0, "shaker", 0.7, "写"), (1, "shaker", 0.7, "写"), (2, "shaker", 0.7, "写"),
                 (3, "ding", 0.9, "写完")]),
        # ---- 片尾 42
        outro("你被“拍脑袋决策”坑过吗？", "事情一大堆，先干哪件？", "下次开口前，先去看一眼"),
    ]
    return episode(1, "investigation", "没有调查没有发言权", "汇报被领导一句话问住，差在哪？", ACC, shots,
                   [f"{BOOK}第一卷《反对本本主义》（一九三〇年五月）", "《寻乌调查》（一九三〇年五月调查）"],
                   "没调查就开口|等于【瞎说】", 8,
                   ["引文出自《反对本本主义》：“没有调查，没有发言权”“便一定是瞎说一顿”“调查就像‘十月怀胎’，解决问题就像"
                    "‘一朝分娩’。调查就是解决问题。”“开口闭口‘拿本本来’”“一味盲目执行”“迈开你的两脚”“一切结论产生于调查情况的"
                    "末尾，而不是在它的先头”“错办法和错主意”“一到就宣布政见”“一定要弄坏事情”；调查 4 招对应第七节“调查的技术”"
                    "中的“要亲身出马”“至少需要三人”“要定调查纲目”“要自己做记录”，“老员工/一线/客户”为今日化示意。",
                    "寻乌调查：1930 年 5 月，调查会开了 10 多天；提供材料者有杂货店主郭友梅、清朝老童生、乡苏维埃干部等；"
                    "8 个头等大地主、12 个大地主、113 个中地主；1931 年整理为 8 万多字（据求是网《继承和弘扬〈寻乌调查〉的优良传统》）。"
                    "店铺招牌为调查涉及的行业示意。",
                    "“当下”部分为现象示意，不点名任何公司、不引用数字；画面不出现历史人物形象。"],
                   tags="#调查研究 #汇报")
