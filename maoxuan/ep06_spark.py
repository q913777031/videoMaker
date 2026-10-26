"""06 星星之火：起点太低，还有戏吗？（快节奏版：42 镜 × 1 小节）

原文出自《星星之火，可以燎原》（一九三〇年一月五日，《毛泽东选集》第一卷；题解：这是一封答复对红军前途悲观估计的信）：
“剩下的一点小小的力量，若仅依据某些现象来看，自然要使同志们……发生悲观的念头。但若从实质上看，便大大不然。
这里用得着中国的一句老话：‘星星之火，可以燎原。’这就是说，现在虽只有一点小小的力量，但是它的发展会是很快的。”
“我们看事情必须要看它的实质，而把它的现象只看作入门的向导”“把这种一时的特殊的小的环境，一般化扩大化起来，
仿佛……革命胜利的前途未免渺茫得很”“中国是全国都布满了干柴，很快就会燃成烈火”
“犯着革命急性病的同志们不切当地看大了革命的主观力量……如果把革命的主观力量看小了……这也是一种不切当的估量”
“有根据地的，有计划地建设政权的……政权发展是波浪式地向前扩大的”“单纯的流动游击政策，不能完成……任务”
结尾：“它是站在海岸遥望海中已经看得见桅杆尖头了的一只航船，它是立于高山之巅远看东方已见光芒四射喷薄欲出的一轮朝日，
它是躁动于母腹中的快要成熟了的一个婴儿。”
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Counter, Custom, Fig, Icon, Label, Rays, Spark
from xingzuo import art as XZ
from zizhi import art as Z

from . import art as A
from . import art_c as C
from .common import BOOK, S, episode, outro, pops

ACC = "#C0502A"
G = A.GROUND_Y
ME = dict(hair="short")


def build():
    shots = [
        # ---- 钩子 1–8
        S("新开的账号", "灵魂拷问", [
            Icon("phone", 400, 740, 280, color=K.INK2, at=0, sfx="pop"),
            Counter(0, 12, 760, 700, 170, at=0, land=2, suffix="个", sub="粉丝"),
        ], punch=0.025, flashes=[0], hits=[(0, "shaker", 0.7, "滚动")]),
        S("同届都升职了", "灵魂拷问", [
            Icon("ladder", 540, 760, 420, color=K.INK2, at=0, sfx="wood_low"),
            Fig(640, 560, 200, at=1, pose="cheer", mood="happy", color=K.OTHER, hair="bun", sfx="pop"),
            Fig(440, 700, 200, at=2, pose="wave", mood="happy", color=K.OTHER2, hair="long", sfx="pop"),
        ]),
        S("我还在原地", "灵魂拷问", [
            Fig(540, G, 330, at=0, pose="sad", mood="sad", **ME),
            Icon("cloud", 540, 450, 180, color=K.INK2, at=1, sfx="wood_low"),
            Custom(Z.sweat, x=580, y=640, at=2, enter="fade"),
        ], draw=A.ground, hits=[(2, "rim", 0.8, "冷汗")]),
        S("起点是不是太低", "灵魂拷问", [
            Fig(400, G, 320, at=0, pose="think", mood="worried", **ME),
            Bubble("我是不是【没戏】了？", 680, 520, 46, at=1, enter="pop", sfx="wood_high"),
            Icon("question", 820, 760, 110, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("越想越悲观", "灵魂拷问", [
            Custom(C.magnify_split, x=540, y=740, at=0, enter="fade", grow=2, label="一点点差距"),
        ], hits=[(0, "wood_low", 0.7, "乌云"), (2, "kick", 1.0, "放大")], shake=[2]),
        pops("起点小 不等于 【没戏】", "灵魂拷问", size=130, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="起步 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("毛选里有封回信", "毛泽东选集", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《星星之火，可以燎原》|一九三〇年一月", 540, 940, 48, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–14
        S("", "原文", [
            Big("星星之火", 540, 640, 170, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：原文落版"),
            Big("可以燎原", 540, 870, 170, at=1, sfx="kick", sub="中国的一句老话", sub_size=40, shine=True,
                note="原文下半句"),
            Spark(540, 870, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        S("一粒火星烧满草原", "原文 · 星星之火，可以燎原", [
            Custom(C.prairie, x=540, y=760, at=0, enter="fade", spark=0, b1=3),
        ], hits=[(0, "pop", 0.8, "火星落下"), (1, "shaker", 0.8, "起火"), (3, "kick", 0.9, "烧满")], shake=[3]),
        S("写给悲观同志的信", "写作背景", [
            Card("一封回信", 540, 620, 70, at=0, sfx="pop"),
            Icon("cloud", 360, 880, 150, color=K.INK2, at=1, sfx="wood_low"),
            Icon("cloud", 720, 900, 120, color=K.INK3, at=2, sfx="wood_low"),
        ]),
        S("他觉得前途渺茫", "原文 · 前途未免渺茫得很", [
            Fig(400, G, 320, at=0, pose="sad", mood="worried", color="#7A6A55", hair="cap"),
            Bubble("前途【渺茫】", 700, 520, 52, at=1, enter="pop", sfx="wood_low"),
            Icon("question", 760, 760, 110, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("力量确实很小", "原文 · 一点小小的力量", [
            Custom(XZ.flame, x=540, y=720, at=0, enter="pop", s=110, sfx="pop"),
            Label("小小的力量", 540, 960, 50, at=2, sfx="wood_high"),
        ]),
        pops("但它的发展 会是 【很快的】", "原文 · 它的发展会是很快的", size=120, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 怎么看、怎么做 15–23
        S("要看实质", "原文 · 必须要看它的实质", [
            Custom(XZ.flame, x=540, y=760, at=0, enter="fade", s=90),
            Custom(Z.magnifier, x=540, y=740, at=1, enter="pop", r=170, sfx="wood_high"),
            Spark(540, 740, at=2, sfx="ding"),
        ]),
        S("现象只是向导", "原文 · 现象只看作入门的向导", [
            Icon("door", 400, 740, 260, color=K.INK2, at=0, sfx="wood_low"),
            Label("现象", 400, 980, 46, at=0),
            Icon("key", 760, 740, 160, color=K.GOLD, at=2, sfx="ding"),
            Label("实质", 760, 980, 46, at=2, fill=K.GOLD),
        ]),
        S("一时挫折别放大", "原文 · 一般化扩大化", [
            Custom(C.magnify_split, x=540, y=740, at=0, enter="fade", grow=1, label="一次败仗"),
            Icon("cross", 820, 440, 110, color=K.RED, at=3, sfx="rim"),
        ], hits=[(1, "kick", 0.9, "放大")]),
        S("到处都是干柴", "原文 · 全国都布满了干柴", [
            Custom(C.prairie, x=540, y=760, at=0, enter="fade", spark=1, b1=3),
        ], hits=[(0, "wood_low", 0.7, "干柴"), (1, "pop", 0.8, "火星"), (3, "kick", 0.9, "烈火")]),
        S("看大看小都不对", "原文 · 不切当的估量", [
            Card("看大了", 300, 700, 64, at=0, sfx="pop"),
            Card("看小了", 780, 700, 64, at=1, sfx="pop"),
            Icon("cross", 300, 900, 120, color=K.RED, at=2, sfx="rim"),
            Icon("cross", 780, 900, 120, color=K.RED, at=3, sfx="rim"),
        ]),
        S("那该怎么做？", "原文 · 行动问题", [
            Icon("question", 540, 660, 240, color=K.RED, at=0, sfx="wood_high"),
            Icon("key", 780, 900, 140, color=K.GOLD, at=2, sfx="ding"), Spark(780, 900, at=2),
        ], punch=0.02),
        S("不是到处乱跑", "原文 · 流动游击", [
            Custom(C.base_vs_roam, x=540, y=780, at=0, enter="fade", grow=1, b=2),
        ], hits=[(0, "wood_low", 0.7, "流动"), (1, "pop", 0.8, "扎根"), (2, "ding", 0.9, "对比")]),
        S("先扎根一块地方", "原文 · 有根据地的", [
            Custom(C.waves, x=540, y=760, at=0, enter="fade", n=1, b0=0, core="根据地"),
            Label("有计划地建设", 540, 1080, 46, at=2, sfx="ding"),
        ], hits=[(0, "kick", 0.8, "扎根")]),
        S("再波浪式扩大", "原文 · 波浪式地向前扩大", [
            Custom(C.waves, x=540, y=760, at=0, enter="fade", n=4, b0=0, core="根据地"),
        ], hits=[(0, "pop", 0.8, "第一圈"), (1, "pop", 0.8, "第二圈"), (2, "pop", 0.8, "第三圈"),
                 (3, "ding", 0.9, "第四圈")]),
        # ---- 二次钩子 24–27
        S("信的结尾最燃", "原文 · 结尾", [
            Icon("megaphone", 540, 700, 260, color=ACC, at=0, sfx="kick"),
            Spark(540, 700, at=1, sfx="ding"), Spark(700, 560, at=2, sfx="ding"),
        ], flashes=[0], punch=0.025, shake=[0]),
        S("已见桅杆的航船", "原文 · 看得见桅杆尖头了的一只航船", [
            Custom(C.ship_mast, x=540, y=780, at=0, enter="fade", b0=0, b1=3),
        ], hits=[(0, "wood_low", 0.7, "海"), (1, "pop", 0.8, "桅杆"), (3, "ding", 0.9, "船身")]),
        S("喷薄欲出的朝日", "原文 · 喷薄欲出的一轮朝日", [
            Custom(C.sunrise, x=540, y=780, at=0, enter="fade", b0=0, b1=3),
        ], hits=[(0, "wood_low", 0.7, "山"), (2, "pop", 0.8, "日出"), (3, "ding", 1.0, "光芒")], flashes=[3]),
        pops("快要 成熟了的 【婴儿】", "原文 · 躁动于母腹中", size=130, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        # ---- 当下 28–35
        S("今天：刚入行", "当下 · 现象", [
            Fig(540, G, 330, at=0, pose="stand", mood="smile", **ME),
            Icon("brief", 300, 760, 170, color=K.INK2, at=1, sfx="pop"),
            Label("新人", 540, 470, 50, at=2, sfx="wood_high"),
        ], draw=A.ground),
        S("副业没几个人看", "当下 · 现象", [
            Icon("phone", 400, 740, 280, color=K.INK2, at=0, sfx="pop"),
            Counter(0, 3, 760, 700, 180, at=0, land=2, suffix="赞"),
        ], hits=[(0, "shaker", 0.7, "滚动")]),
        S("跟别人一比", "当下 · 现象", [
            Custom(C.power, x=540, y=780, at=0, enter="fade", grow=99, left="我", right="别人", me0=0.2, them0=0.85),
            Icon("question", 540, 400, 100, color=K.RED, at=2, sfx="rim"),
        ], hits=[(0, "wood_low", 0.8, "对比")]),
        S("就觉得没戏了", "当下 · 现象", [
            Fig(540, G, 330, at=0, pose="sit_sad", mood="sad", **ME),
            Icon("cloud", 540, 470, 180, color=K.INK2, at=1, sfx="wood_low"),
            Icon("cloud", 760, 540, 130, color=K.INK3, at=2, sfx="wood_low"),
        ], draw=A.ground),
        pops("你只看到了 【现象】", "一句话", size=140, flash=1, extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        S("火星就在你手里", "落到自己", [
            Fig(400, G, 330, at=0, pose="give", mood="smile", **ME),
            Custom(XZ.flame, x=640, y=870, at=1, enter="pop", s=130, sfx="pop"),
            Spark(640, 870, at=2, sfx="ding"),
        ], draw=A.ground),
        S("换个看法", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("比较", K.INK2), ("焦虑", K.GOLD), ("乱跑", K.GREEN), ("扎根", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "扎根置顶")], flashes=[1], shake=[1]),
        S("书里给了方法", "原文 · 星星之火，可以燎原", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="起步 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        # ---- 起步 4 招 36–39
        S("① 看实质别看表面", "起步 4 招 · 看它的实质", [
            Custom(XZ.flame, x=540, y=760, at=0, enter="fade", s=90),
            Custom(Z.magnifier, x=540, y=740, at=1, enter="pop", r=170, sfx="wood_high"),
            Label("在长吗？", 540, 1010, 50, at=2, sfx="ding"),
        ]),
        S("② 挫折别扩大化", "起步 4 招 · 一时的小的环境", [
            Icon("cloud", 540, 680, 180, color=K.INK2, at=0, sfx="wood_low"),
            Label("只是这一次", 540, 900, 50, at=1, sfx="pop"),
            Icon("sun", 800, 470, 140, color=K.GOLD, at=2, sfx="ding"),
        ]),
        S("③ 先扎根一块", "起步 4 招 · 有根据地", [
            Custom(C.base_vs_roam, x=540, y=780, at=0, enter="fade", grow=1, b=2),
        ], hits=[(0, "wood_low", 0.7, "流动"), (1, "pop", 0.8, "扎根"), (2, "ding", 0.9, "对比")]),
        S("④ 一圈圈往外扩", "起步 4 招 · 波浪式扩大", [
            Custom(C.waves, x=540, y=760, at=0, enter="fade", n=4, b0=0, core="一个点"),
        ], hits=[(0, "pop", 0.8, "第一圈"), (1, "pop", 0.8, "第二圈"), (2, "pop", 0.8, "第三圈"),
                 (3, "ding", 0.9, "第四圈")]),
        # ---- 收束 40–41
        S("火星不怕小", "一句话", [
            Custom(C.prairie, x=540, y=760, at=0, enter="fade", spark=0, b1=3),
        ], hits=[(0, "pop", 0.8, "火星"), (1, "shaker", 0.8, "起火"), (3, "kick", 0.9, "燎原")]),
        S("怕的是自己熄了", "一句话", [
            Custom(C.sunrise, x=540, y=780, at=0, enter="fade", b0=0, b1=2),
            Label("别熄火", 540, 1190, 56, at=3, sfx="ding", fill=ACC),
        ], hits=[(0, "wood_low", 0.7, "山"), (2, "pop", 0.8, "日出")]),
        # ---- 片尾 42
        outro("你手里的火星是什么？", "职场里，谁才是你的朋友？", "起点低，不等于没戏"),
    ]
    return episode(6, "spark", "星星之火", "起点太低，还有戏吗？", ACC, shots,
                   [f"{BOOK}第一卷《星星之火，可以燎原》（一九三〇年一月五日）"],
                   "起点低|不等于【没戏】", 8,
                   ["引文出自《星星之火，可以燎原》：“星星之火，可以燎原”“一点小小的力量，但是它的发展会是很快的”"
                    "“必须要看它的实质，而把它的现象只看作入门的向导”“一时的特殊的小的环境，一般化扩大化起来”“前途未免渺茫得很”"
                    "“全国都布满了干柴”“看大了……看小了……不切当的估量”“有根据地的，有计划地建设政权的”“波浪式地向前扩大的”"
                    "“流动游击”“看得见桅杆尖头了的一只航船”“喷薄欲出的一轮朝日”“快要成熟了的一个婴儿”。",
                    "“写给悲观同志的信”据《毛泽东选集》题解（答复对红军前途的悲观估计），不点名；草原火势、波浪圈、扎根方块为示意。",
                    "“当下”部分（新账号粉丝数、点赞数）为现象示意，数字为示意不引用数据；起步 4 招为对原文的今日化应用。"
                    "画面不出现战争场面与历史人物形象。"],
                   tags="#成长 #起点")
