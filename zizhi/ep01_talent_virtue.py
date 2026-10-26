"""01 才德之辨：招人、找对象，最怕看走眼的是什么？（快节奏版：42 镜 × 1 小节）

故事出自《资治通鉴》卷一·周纪一：智宣子立智瑶为后，智果谏“瑶之贤于人者五，其不逮者一……如是而甚不仁”，
“若果立瑶也，智宗必灭”，智果别族为辅氏；智瑶索地于韩、魏、赵，围晋阳，“城不浸者三版”，
“吾乃今知水可以亡人国也”；韩、魏反，三家灭智氏，唯辅果在。臣光曰：“智伯之亡也，才胜德也……
才胜德谓之小人……与其得小人，不若得愚人。”
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Counter, Custom, Fig, Icon, Label, Pops, Rays, Spark
from sapiens.art import crowd
from scarcity.art import checklist, laptop

from . import art as A
from .common import BOOK, S, episode, outro, pops

ACC = A.CINNABAR
G = A.GROUND_Y
ZY = dict(color="#7A4E8A", hair="bun")          # 智瑶
ZG = dict(color="#6E7F5A", hair="bun")          # 智果
ME = dict(hair="short")
HAN, WEI = A.FLAG["韩"], A.FLAG["魏"]


def build():
    shots = [
        # ---- 钩子 1–8
        S("招人、交朋友、找对象", "灵魂拷问", [
            Icon("brief", 270, 740, 190, color=K.INK2, at=0, sfx="pop"),
            Icon("friends", 540, 740, 200, color=K.HERO, at=1, sfx="pop"),
            Icon("heart", 810, 740, 180, color=ACC, at=2, sfx="pop"),
        ], punch=0.025, flashes=[0]),
        S("最怕看走眼的是？", "灵魂拷问", [
            Custom(crowd, x=540, y=G, at=0, enter="fade", n=6, s=250, spread=820),
            Custom(A.magnifier, x=540, y=640, at=0, enter="pop", r=130, blur_at=2, sfx="wood_high"),
            Icon("question", 760, 470, 100, color=K.RED, at=2, sfx="rim"),
        ]),
        S("技术？才华？", "灵魂拷问", [
            Custom(laptop, x=300, y=760, at=0, enter="pop", w=380, h=240, title="代码", p0=0.2, p1=1, b0=0, b1=3,
                   sfx="pop"),
            Icon("trophy", 790, 740, 220, color=K.GOLD, at=2, sfx="pop"), Spark(790, 740, at=2),
        ]),
        S("还是钱？", "灵魂拷问", [
            Custom(A.thing, x=540, y=760, at=0, enter="pop", obj="moneybag", s=320, sfx="kick"),
            Spark(540, 700, at=0), Icon("question", 760, 520, 90, color=K.RED, at=2, sfx="rim"),
        ], shake=[0]),
        S("全都不是", "灵魂拷问", [
            Custom(laptop, x=230, y=760, at=0, enter="none", w=300, h=190, title="代码"),
            Icon("trophy", 540, 740, 170, color=K.GOLD, at=0, enter="none"),
            Custom(A.thing, x=840, y=760, at=0, enter="none", obj="moneybag", s=220),
            Icon("cross", 230, 760, 150, color=K.RED, at=1, sfx="rim"),
            Icon("cross", 540, 740, 150, color=K.RED, at=2, sfx="rim"),
            Icon("cross", 840, 760, 150, color=K.RED, at=3, sfx="rim"),
        ]),
        pops("是 【人品】 ！", "灵魂拷问", size=170, flash=1, extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="识人 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("资治通鉴一句话", "资治通鉴", [
            Icon("book", 540, 470, 150, color=ACC, at=0, sfx="wood_low"),
            Custom(A.bamboo, x=540, y=860, at=0, enter="none", text="资治通鉴", n=8, h=430, w=64, b0=1, step=0.5),
        ], hits=[(1, "wood_high", 0.8, "竹简展开"), (2, "shaker", 0.7, "写字")]),
        # ---- drop 9–11
        S("", "原文", [
            Big("德者，才之帅也", 540, 720, 120, at=0, sfx="kick", sub="《资治通鉴 · 周纪一》", sub_size=40, rays=True,
                glow=True, shine=True, spark=True, note="drop：原文落版"),
            Spark(540, 720, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0], shake=[0]),
        S("才是马，德是缰绳", "原文 · 才者，德之资也", [
            Custom(A.horse_reins, x=540, y=760, at=0, enter="fade"),
        ], hits=[(0, "wood_low", 0.8, "马"), (2, "wood_high", 0.8, "缰绳")]),
        S("缰绳一断，越快越险", "原文 · 才者，德之资也", [
            Custom(A.horse_reins, x=540, y=760, at=0, enter="none", snap=1, cliff=True),
        ], hits=[(1, "rim", 1.0, "缰绳断"), (3, "kick", 0.8, "坠崖")], shake=[3]),
        # ---- 开挂的人 12–18
        S("两千多年前，晋国", "春秋末年", [
            Custom(A.scroll_map, x=540, y=780, at=0, enter="fade", b0=0, b1=1, step=0.5,
                   labels=[("智", -120, -60), ("韩", 130, -100), ("赵", -70, 110), ("魏", 160, 90)]),
        ], hits=[(0, "wood_low", 0.8, "卷轴"), (1, "pop", 0.8, "智"), (2, "pop", 0.8, "赵")]),
        S("开挂：又帅又能打", "智瑶", [
            Fig(540, G, 340, at=0, pose="proud", mood="happy", **ZY),
            Label("颜值 MAX", 300, 520, 42, at=1, sfx="pop"),
            Label("武力 MAX", 780, 520, 42, at=2, sfx="pop", fill=K.GOLD),
            Spark(540, 560, at=3, sfx="ding"),
        ], draw=A.ground),
        S("能说会道，果断刚强", "智瑶", [
            Fig(540, G, 340, at=0, enter="none", pose="proud", mood="happy", **ZY,
                moves=[(2, dict(pose="fist", dur=0.25, sfx="kick"))]),
            Bubble("【听我的】！", 780, 560, 52, at=0, enter="pop", sfx="rim"),
        ], draw=A.ground, shake=[2]),
        S("五项全能，人生赢家", "智瑶", [
            Counter(0, 5, 540, 800, 280, at=0, land=2, sub="项都比人强"),
            Icon("crown", 540, 480, 160, color=K.GOLD, at=3, sfx="ding"), Spark(540, 480, at=3),
        ], hits=[(0, "shaker", 0.8, "滚动")]),
        S("他叫智瑶，要当家主", "智氏立嗣", [
            Custom(A.family_tree, x=540, y=780, at=0, enter="fade", fill=(1, "瑶")),
        ], hits=[(0, "wood_low", 0.8, "族谱"), (1, "ding", 0.9, "填名")]),
        S("族人智果却说：不行", "智氏立嗣", [
            Fig(760, G, 330, at=0, pose="proud", mood="happy", face=-1, **ZY,
                moves=[(1, dict(mood="surprised", dur=0.2))]),
            Fig(300, G, 310, at=0, pose="stand", mood="worried", **ZG,
                moves=[(1, dict(pose="block", dur=0.25, sfx="rim"))]),
            Bubble("不行！", 300, 600, 56, at=1, enter="pop"),
        ], draw=A.ground),
        S("大家都问：凭什么？", "智氏立嗣", [
            Custom(crowd, x=540, y=G, at=0, enter="fade", n=6, s=250, spread=820),
            Icon("question", 300, 560, 90, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 540, 500, 110, color=K.RED, at=2, sfx="wood_high"),
            Icon("question", 780, 560, 90, color=K.RED, at=3, sfx="wood_high"),
        ]),
        # ---- 反转 19–22
        S("他只缺一样", "反转", [
            Big("1", 540, 720, 300, at=0, sfx="kick", sub="样", sub_size=60, rays=True, glow=True, shine=True, spark=True),
            Spark(540, 720, at=2, sfx="ding"),
        ], punch=0.03, flashes=[0], shake=[0]),
        S("甚不仁：心不善", "原文 · 如是而甚不仁", [
            Custom(A.crack_char, x=540, y=740, at=0, enter="pop", text="仁", s=380, split=2, sfx="wood_low"),
        ], hits=[(2, "rim", 1.0, "裂开")], shake=[2]),
        pops("智宗 必灭", "原文 · 智果之谏", size=180, flash=1,
             extra=[Icon("cross", 540, 470, 110, color=K.RED, at=2, sfx="rim")]),
        S("改姓走了，没人当真", "智果别族为辅氏", [
            Custom(A.family_tree, x=540, y=780, at=0, enter="none", fill=(-9, "瑶"), alt=(1, "辅")),
            Bubble("哈哈", 900, 420, 40, at=2, enter="pop", sfx="pop"),
        ], hits=[(1, "ding", 0.8, "改姓")]),
        # ---- 覆灭 23–28
        S("四处要地，赵不给", "贪得无厌", [
            Custom(A.flags, x=0, y=1060, at=0, enter="none", s=320,
                   items=[("韩", 270, 0, 0, None, None), ("魏", 540, 0, 1, None, None), ("赵", 810, 0, 2, None, None)]),
            Bubble("不给！", 870, 420, 52, at=3, enter="pop", sfx="rim"),
        ], hits=[(0, "pop", 0.8, "韩"), (1, "pop", 0.8, "魏"), (2, "pop", 0.8, "赵")]),
        S("引水灌城，只剩三版", "晋阳之战", [
            Custom(A.city, x=540, y=760, at=0, enter="pop", b0=0.5, b1=3, sfx="wood_low"),
        ], hits=[(1, "shaker", 0.8, "水涨"), (3, "ding", 0.9, "只剩三版")]),
        S("智瑶大笑：水可亡国", "原文 · 水可以亡人国", [
            Fig(400, G, 340, at=0, pose="cheer", mood="happy", **ZY),
            Bubble("水可以【亡人国】！", 640, 560, 46, at=1, enter="pop", sfx="rim"), Spark(640, 560, at=1),
        ], draw=A.ground),
        S("韩魏：下一个是我们", "原文 · 肘足相蹑", [
            Fig(400, G, 310, at=0, pose="stand", mood="worried", color=HAN, hair="short",
                moves=[(2, dict(pose="give", dur=0.2, sfx="wood_high", note="手肘碰"))]),
            Fig(680, G, 310, at=0, pose="stand", mood="worried", color=WEI, hair="bun", face=-1),
            Custom(A.sweat, x=440, y=780, at=1, enter="fade"), Custom(A.sweat, x=660, y=780, at=1, enter="fade"),
            Icon("question", 540, 480, 90, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("一夜反水，智氏灭族", "三家灭智", [
            Custom(A.night, x=540, y=800, at=0, enter="fade"),
            Custom(A.flags, x=0, y=1060, at=0, enter="none", s=320,
                   items=[("韩", 270, 0, 0, None, 1), ("智", 540, 0, 0, 2, None), ("魏", 810, 0, 0, None, 1)]),
        ], hits=[(1, "rim", 0.9, "调转"), (2, "kick", 0.9, "智旗折断")], shake=[2], flashes=[2]),
        S("只有智果活了下来", "唯辅果在", [
            Custom(A.family_tree, x=540, y=780, at=0, enter="fade", fill=(-9, "瑶"), alt=(-9, "辅"), fall=0),
        ], hits=[(0, "wood_low", 0.8, "灭族"), (2, "ding", 0.9, "辅")]),
        # ---- 司马光 29–30
        S("才胜德，谓之小人", "臣光曰", [
            Label("司马光曰", 540, 400, 44, at=0, sfx="wood_low"),
            Custom(A.brush_text, x=540, y=820, at=0, enter="none", text="才胜德谓之小人", size=88, b0=0, step=0.4),
        ], hits=[(2, "wood_high", 0.8, "落笔")]),
        S("宁用愚人，不用小人", "臣光曰", [
            Card("愚人|没本事 · 坏不了事", 290, 760, 40, at=0, sfx="pop"),
            Card("小人|有才 · 作恶更大", 790, 760, 40, at=1, sfx="pop"),
            Icon("check", 290, 540, 100, color=K.GREEN, at=2, sfx="ding"),
            Icon("cross", 790, 540, 100, color=K.RED, at=3, sfx="rim"),
        ]),
        # ---- 当下 31–37
        S("今天招人：先看学历", "当下 · 现象", [
            Icon("brief", 300, 760, 200, color=K.INK2, at=0, sfx="pop"),
            Big("名校", 700, 740, 170, at=1, sfx="kick", glow=True),
        ], shake=[1]),
        S("再看能力，人品？跳过", "当下 · 现象", [
            Custom(A.form, x=540, y=780, at=0, enter="pop", title="录用审核", rows=[("学历", "985"), ("能力", "A+"),
                                                                              ("人品", None)], skip=2, skip_at=2),
        ], hits=[(0, "ding", 0.7, "学历"), (1, "ding", 0.7, "能力"), (2, "rim", 1.0, "跳过")]),
        S("找对象：有房有车吗", "当下 · 现象", [
            Icon("house", 300, 780, 220, color=ACC, at=0, sfx="pop"),
            Custom(A.thing, x=780, y=800, at=1, enter="pop", obj="car", s=300, sfx="pop"),
            Bubble("有房吗？", 300, 520, 44, at=2, enter="pop", sfx="wood_high"),
            Bubble("有车吗？", 780, 540, 44, at=3, enter="pop", sfx="wood_high"),
        ]),
        S("年薪多少？人品？跳过", "当下 · 现象", [
            Custom(A.form, x=540, y=780, at=0, enter="pop", title="相亲清单", rows=[("年薪", "50万"), ("工作", "大厂"),
                                                                              ("人品", None)], skip=2, skip_at=2),
        ], hits=[(0, "ding", 0.7, "年薪"), (1, "ding", 0.7, "工作"), (2, "rim", 1.0, "跳过")]),
        S("条件齐了，日子散了", "当下 · 现象", [
            Custom(A.crack_floor, x=540, y=900, at=0, enter="fade", b=1),
        ], hits=[(0, "wood_low", 0.8, "婚房"), (1, "rim", 1.0, "裂开")], shake=[1]),
        S("两千年，同一个坑", "一句话", [
            Custom(A.pit, x=540, y=900, at=0, enter="fade", fall=1, label="才胜德"),
        ], hits=[(0, "wood_low", 0.8, "坑"), (1, "tom", 0.8, "古人掉坑"), (2, "tom", 0.8, "今人掉坑")]),
        S("交友择偶，人品第一", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("学历", K.INK2), ("房车", K.GOLD), ("年薪", K.GREEN), ("人品", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "人品置顶")], flashes=[1], shake=[1]),
        # ---- 识人 4 招 38–41
        S("① 看他对“没用”的人", "识人 4 招 · 小建议", [
            Custom(A.thing, x=540, y=470, at=0, enter="pop", obj="chest", s=200, open=0, sfx="ding"),
            Custom(A.rating, x=540, y=880, at=0, enter="none", b0=1,
                   rows=[("对服务员", 5), ("对保安", 5), ("对外卖员", 5)]),
        ], hits=[(1, "pop", 0.8, "服务员"), (2, "pop", 0.8, "保安"), (3, "pop", 0.8, "外卖员")]),
        S("② 看小事守不守约", "识人 4 招 · 小建议", [
            Custom(checklist, x=540, y=780, at=0, enter="pop", w=620, title="小事见人品",
                   items=[("准时到", True), ("借了还", True), ("答应的事", True)], b0=1, step=1),
        ], hits=[(0, "wood_high", 0.8, "清单"), (1, "ding", 0.7, "打勾"), (2, "ding", 0.7, "打勾"),
                 (3, "ding", 0.8, "打勾")]),
        S("③ 看他不顺心的时候", "识人 4 招 · 小建议", [
            Fig(540, G, 330, at=0, pose="stand", mood="calm", **ME,
                moves=[(2, dict(pose="fist", mood="angry", dur=0.25, sfx="rim"))]),
            Custom(A.thing, x=250, y=560, at=0, enter="pop", obj="car", s=180, sfx="pop"),
            Icon("phone", 830, 560, 110, color=K.INK2, at=1, sfx="pop"),
            Bubble("凭什么！", 760, 400, 44, at=2, enter="pop"),
        ], draw=A.ground, shake=[2]),
        S("④ 听他老朋友怎么说", "识人 4 招 · 小建议", [
            Fig(540, G, 330, at=0, pose="stand", mood="smile", **ME),
            Fig(250, G, 290, at=0, pose="point", mood="happy", color=K.OTHER, hair="long", sfx="pop"),
            Fig(830, G, 290, at=1, pose="point", mood="happy", color=K.OTHER2, face=-1, sfx="pop"),
            Icon("check", 250, 560, 90, color=K.GREEN, at=2, sfx="ding"),
            Icon("check", 830, 560, 90, color=K.GREEN, at=3, sfx="ding"),
        ], draw=A.ground),
        # ---- 片尾 42
        outro("你被“有才无德”的人坑过吗？", None, "收藏这4招，看人不走眼"),
    ]
    return episode(1, "talent_virtue", "才德之辨", "招人、找对象，最怕看走眼的是什么？", ACC, shots,
                   [f"{BOOK}卷一 · 周纪一（智氏立嗣、晋阳之战、臣光曰）"], "有才没德|越能干越【危险】", 8,
                   ["故事与引文出自《资治通鉴》卷一·周纪一：“如是而甚不仁”“智宗必灭”“城不浸者三版”“吾乃今知水可以亡人国也”"
                    "“智伯之亡也，才胜德也”“才胜德谓之小人”“与其得小人，不若得愚人”；“水可亡国”为缩写。",
                    "“才是马，德是缰绳”是对“才者，德之资也；德者，才之帅也”的比喻，为创作者阐释。",
                    "“当下”部分为现象示意，不点名任何公司，不引用数字；识人 4 招为小建议，不是书中原话。"],
                   tags="#找对象 #职场")
