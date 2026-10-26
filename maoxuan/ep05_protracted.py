"""05 论持久战：目标太远，怎么撑下去？（快节奏版：42 镜 × 1 小节）

原文出自《论持久战》（一九三八年五月，延安抗日战争研究会讲演，《毛泽东选集》第二卷）：
“中国会亡吗？答复：不会亡，最后胜利是中国的。中国能够速胜吗？答复：不能速胜，抗日战争是持久战。”
“失败主义的亡国论者跑出来向人们说：中国会亡”“某些性急的朋友们也跑出来向人们说：中国很快就能战胜，无需乎费大气力”
“抗战十个月的经验”；三个阶段：战略防御、准备反攻、战略反攻；“这个第二阶段是整个战争的过渡阶段，也将是最困难的时期，
然而它是转变的枢纽”“获得转弱为强的力量”“中国抗战的三幕戏，这是第二幕。由于全体演员的努力，最精彩的结幕便能很好地演出来”
“谁也不能造出一本中日战争的‘流年’来；然而给战争趋势描画一个轮廓，却为战略指导所必需”
“一切想要缩短战争时间的人们，惟有努力于增加自己力量减少敌人力量之一法”“持久战和最后胜利没有人做就不会出现”。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Counter, Custom, Fig, Icon, Label, Rays, Spark
from sapiens.art import timeline

from zizhi import art as Z

from . import art as A
from . import art_c as C
from .common import BOOK, S, episode, outro, pops

ACC = "#8A3B2E"
G = A.GROUND_Y
ME = dict(hair="short", role="worker")
ROLES_1938 = ("farmer", "soldier", "scholar", "woman", "merchant", "youth")


ACTS = (("第一幕", "我方|防御"), ("第二幕", "准备|反攻"), ("第三幕", "战略|反攻"))


def build():
    shots = [
        # ---- 钩子 1–8
        S("新年立了个目标", "灵魂拷问", [
            Custom(C.mountain_goal, x=540, y=760, at=0, enter="fade", goal="考下证书", zoom=2),
        ], punch=0.025, flashes=[0], hits=[(0, "wood_low", 0.8, "远山"), (1, "ding", 0.8, "目标"),
                                           (2, "tom", 0.8, "山被拉远")]),
        S("打卡三天就断了", "灵魂拷问", [
            Custom(C.tally, x=540, y=780, at=0, enter="pop", n=14, b0=0, step=0.5, quit=2, quit_n=3, title="学习打卡",
                   sfx="pop"),
        ], hits=[(1, "ding", 0.7, "打勾"), (2, "rim", 1.0, "断了")], shake=[2]),
        S("一种人：马上逆袭", "灵魂拷问", [
            Fig(400, G, 330, at=0, pose="cheer", mood="happy", **ME),
            Bubble("三个月【逆袭】！", 700, 520, 50, at=1, enter="pop", sfx="pop"),
            Spark(700, 520, at=2, sfx="ding"),
        ], draw=A.ground),
        S("一种人：算了吧", "灵魂拷问", [
            Fig(540, G, 330, at=0, pose="sit_sad", mood="sad", **ME),
            Bubble("这辈子【就这样】", 700, 520, 48, at=1, enter="pop", sfx="wood_low"),
            Icon("cloud", 360, 480, 140, color=K.INK2, at=2, sfx="wood_low"),
        ], draw=A.ground),
        S("两种都会放弃", "灵魂拷问", [
            Card("太急", 300, 700, 70, at=0, sfx="pop"),
            Card("太丧", 780, 700, 70, at=1, sfx="pop"),
            Icon("cross", 300, 900, 130, color=K.RED, at=2, sfx="rim"),
            Icon("cross", 780, 900, 130, color=K.RED, at=3, sfx="rim"),
        ]),
        pops("别太急 也别 【认输】", "灵魂拷问", size=140, flash=2, extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label="坚持 4 招", sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2),
        ]),
        S("毛选里有篇讲演", "毛泽东选集", [
            Icon("book", 540, 560, 230, color=ACC, at=0, sfx="wood_low"),
            Card("《论持久战》|一九三八年五月", 540, 940, 50, at=1, sfx="pop"),
            Spark(540, 560, at=2, sfx="ding"),
        ]),
        # ---- drop 9–13
        S("", "原文", [
            Big("不会亡", 540, 640, 170, at=0, sfx="kick", rays=True, glow=True, shine=True, spark=True,
                note="drop：原文落版"),
            Big("不能速胜", 540, 870, 170, at=1, sfx="kick", sub="《论持久战》", sub_size=40, shine=True, note="原文下半句"),
            Spark(540, 870, at=2, sfx="ding"),
        ], punch=0.035, flashes=[0, 1], shake=[0, 1]),
        S("原文自问自答", "原文 · 问题的提起", [
            Fig(170, G, 330, at=0, pose="point", mood="open", color=None, role="scholar"),
            Card("中国会亡吗？|答复：不会亡", 640, 600, 48, at=0, sfx="pop"),
            Card("中国能够速胜吗？|答复：不能速胜", 640, 880, 48, at=2, sfx="pop"),
            Spark(640, 600, at=1, sfx="ding"), Spark(640, 880, at=3, sfx="ding"),
        ]),
        S("亡国论：太悲观", "原文 · 亡国论", [
            Fig(400, G, 330, at=0, pose="sad", mood="sad", color=None, role="scholar"),
            Bubble("【中国会亡】", 700, 540, 52, at=1, enter="pop", sfx="wood_low"),
            Icon("cross", 700, 820, 140, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("速胜论：太性急", "原文 · 速胜论", [
            Fig(400, G, 330, at=0, pose="cheer", mood="happy", color=None, role="merchant"),
            Bubble("很快就能【战胜】", 700, 540, 48, at=1, enter="pop", sfx="pop"),
            Icon("cross", 700, 820, 140, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        pops("答案是 【持久战】", "原文 · 抗日战争是持久战", size=150, flash=1,
             extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        # ---- 三幕戏 14–22
        S("抗战才打十个月", "写作背景", [
            Counter(0, 10, 540, 640, 200, at=0, land=2, suffix="个月", sub="一九三八年五月讲演"),
            Icon("clock", 540, 420, 90, color=K.INK2, at=3, sfx="wood_high"),
            Fig(220, G, 300, at=1, pose="stand", mood="worried", color=None, role="soldier"),
            Fig(860, G, 290, at=1, pose="stand", mood="worried", color=None, role="farmer", face=-1),
        ], hits=[(0, "shaker", 0.8, "滚动")]),
        S("人人都在问结局", "原文 · 能速胜还是不能速胜", [
            Custom(C.crowd_roles, x=540, y=G, at=0, enter="fade", n=6, s=270, spread=820, roles=ROLES_1938),
            Icon("question", 300, 560, 90, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 540, 500, 110, color=K.RED, at=2, sfx="wood_high"),
            Icon("question", 780, 560, 90, color=K.RED, at=3, sfx="wood_high"),
        ]),
        S("像一出三幕戏", "原文 · 三个阶段", [
            Custom(C.stage3, x=540, y=780, at=0, enter="fade", open=0, b0=1, acts=ACTS),
        ], hits=[(0, "wood_low", 0.8, "拉幕"), (1, "pop", 0.8, "第一幕"), (2, "pop", 0.8, "第二幕"),
                 (3, "pop", 0.8, "第三幕")]),
        S("第一幕：先守住", "原文 · 我之战略防御", [
            Custom(C.stage3, x=540, y=780, at=0, enter="none", open=-9, b0=-9, acts=ACTS, hi=0, hi_at=1),
            Icon("shield", 250, 380, 80, color=K.GREEN, at=2, sfx="ding"),
        ], hits=[(0, "wood_low", 0.6, "舞台"), (1, "kick", 0.9, "第一幕放大")], flashes=[1]),
        S("第二幕最难", "原文 · 最困难的时期", [
            Custom(C.stage3, x=540, y=780, at=0, enter="none", open=-9, b0=-9, acts=ACTS, hi=1, hi_at=1),
            Icon("question", 540, 375, 70, color=K.RED, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "舞台"), (1, "kick", 1.0, "第二幕放大")], flashes=[1], shake=[1]),
        S("最难也是转折点", "原文 · 它是转变的枢纽", [
            Custom(C.plateau, x=540, y=780, at=0, enter="fade", b0=0, b1=3, label_at=2, label="最困难 · 转折点",
                   walker="farmer"),
        ], hits=[(0, "shaker", 0.7, "爬坡"), (2, "ding", 1.0, "转折点"), (3, "pop", 0.8, "上扬")]),
        S("撑住就转弱为强", "原文 · 转弱为强", [
            Custom(C.power, x=540, y=780, at=0, enter="fade", grow=1, left="自己的力量", right="困难"),
        ], hits=[(0, "wood_low", 0.7, "对比"), (1, "shaker", 0.8, "长高"), (2, "ding", 1.0, "超过")]),
        S("好戏在最后一幕", "原文 · 最精彩的结幕", [
            Custom(C.stage3, x=540, y=780, at=0, enter="none", open=-9, b0=-9, acts=ACTS, hi=2, hi_at=1),
            Spark(830, 780, at=2, sfx="ding"),
        ], hits=[(0, "wood_low", 0.6, "舞台"), (1, "kick", 1.0, "第三幕放大")], flashes=[1]),
        S("靠全体演员努力", "原文 · 全体演员的努力", [
            Custom(C.crowd_roles, x=540, y=G, at=0, enter="fade", n=7, s=270, spread=860, roles=ROLES_1938,
                   moods=("happy", "smile", "open")),
            Icon("heart", 300, 520, 90, color=ACC, at=1, sfx="pop"),
            Icon("heart", 540, 470, 110, color=ACC, at=2, sfx="pop"),
            Icon("heart", 780, 520, 90, color=ACC, at=3, sfx="pop"),
        ]),
        S("没人做，就不会有", "原文 · 没有人做就不会出现", [
            Fig(330, G, 320, at=0, pose="sit", mood="flat", **ME),
            Big("做", 760, 700, 300, at=2, sfx="kick", glow=True, spark=True),
            Icon("cross", 330, 520, 100, color=K.RED, at=1, sfx="rim"),
        ], shake=[2], draw=A.ground),
        # ---- 二次钩子 23–26
        S("想缩短时间？", "原文 · 想要缩短战争时间", [
            Fig(300, G, 330, at=0, pose="think", mood="worried", color=None, role="scholar"),
            Icon("clock", 720, 680, 240, color=K.INK2, at=0, sfx="wood_high"),
            Icon("question", 880, 470, 110, color=K.RED, at=1, sfx="rim"),
        ], flashes=[0], punch=0.025),
        pops("只有 增加 【自己力量】", "原文 · 惟有努力于增加自己力量", size=140, flash=2,
             extra=[Rays(540, 780, 620, at=2, alpha=0.2)]),
        S("谁也算不准哪天", "原文 · 不能造出一本流年", [
            Fig(260, G, 330, at=0, pose="shrug", mood="flat", color=None, role="sage"),
            Card("哪天成功？", 680, 560, 64, at=0, sfx="pop"),
            Icon("question", 560, 820, 100, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 720, 860, 120, color=K.RED, at=2, sfx="wood_high"),
            Icon("question", 880, 820, 100, color=K.RED, at=3, sfx="wood_high"),
        ]),
        S("但轮廓能画出来", "原文 · 描画一个轮廓", [
            Custom(timeline, x=540, y=780, at=0, enter="fade", b0=1, step=1,
                   points=[("第一幕", "打基础"), ("第二幕", "熬平台"), ("第三幕", "冲刺")]),
        ], hits=[(0, "wood_low", 0.7, "时间轴"), (1, "pop", 0.8, "第一幕"), (2, "pop", 0.8, "第二幕"),
                 (3, "ding", 0.9, "第三幕")]),
        # ---- 当下 27–35
        S("今天：健身一周", "当下 · 现象", [
            Fig(400, G, 330, at=0, pose="fist", mood="happy", **ME),
            Counter(0, 7, 760, 660, 200, at=0, land=2, suffix="天", sub="健身打卡"),
        ], draw=A.ground, hits=[(0, "shaker", 0.7, "滚动")]),
        S("镜子里没变化", "当下 · 现象", [
            Fig(330, G, 330, at=0, pose="stand", mood="worried", **ME),
            Icon("mirror", 720, 760, 260, color=K.INK2, at=1, sfx="pop"),
            Icon("question", 860, 500, 100, color=K.RED, at=2, sfx="rim"),
        ]),
        S("背了一个月单词", "当下 · 现象", [
            Icon("book", 400, 720, 220, color=K.HERO, at=0, sfx="pop"),
            Counter(0, 30, 760, 700, 180, at=0, land=2, suffix="天"),
        ], hits=[(0, "shaker", 0.7, "滚动")]),
        S("还是听不懂", "当下 · 现象", [
            Fig(540, G, 330, at=0, pose="shrug", mood="worried", **ME),
            Bubble("？？？", 780, 520, 54, at=1, enter="pop", sfx="wood_high"),
            Custom(Z.sweat, x=580, y=640, at=2, enter="fade"),
        ], draw=A.ground, hits=[(2, "rim", 0.8, "冷汗")]),
        S("于是就放弃了", "当下 · 现象", [
            Custom(C.tally, x=540, y=780, at=0, enter="pop", n=14, b0=0, step=0.25, quit=2, quit_n=7, title="健身打卡",
                   sfx="pop"),
        ], hits=[(1, "ding", 0.7, "打勾"), (2, "rim", 1.0, "断了")], shake=[2]),
        pops("你卡在了 【第二幕】", "一句话", size=140, flash=1, extra=[Rays(540, 780, 620, at=1, alpha=0.2)]),
        S("其实快到转折了", "落到自己", [
            Custom(C.plateau, x=540, y=780, at=0, enter="fade", b0=0, b1=2, label_at=2, label="你在这里", walker="worker"),
        ], hits=[(0, "shaker", 0.7, "走"), (2, "ding", 1.0, "你在这里")]),
        S("换个打法", "落到自己", [
            Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1,
                   items=[("想速成", K.INK2), ("想放弃", K.GOLD), ("瞎硬撑", K.GREEN), ("打持久战", ACC)]),
        ], hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "持久战置顶")], flashes=[1], shake=[1]),
        S("书里给了方法", "原文 · 论持久战", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, open=1, label="坚持 4 招",
                   sfx="wood_low"),
        ], hits=[(1, "ding", 1.0, "打开")], flashes=[1]),
        # ---- 坚持 4 招 36–41
        S("① 先画个大轮廓", "坚持 4 招 · 描画一个轮廓", [
            Custom(timeline, x=540, y=780, at=0, enter="fade", b0=0, step=1.5,
                   points=[("基础", "前三月"), ("平台", "最难熬"), ("冲刺", "见效")]),
        ], hits=[(0, "pop", 0.8, "基础"), (2, "pop", 0.8, "平台"), (3, "ding", 0.9, "冲刺")]),
        S("② 认准最难那段", "坚持 4 招 · 最困难的时期", [
            Custom(C.plateau, x=540, y=780, at=0, enter="fade", b0=-9, b1=-8, label_at=1, label="提前留好余量",
                   walker="worker"),
            Icon("shield", 860, 380, 110, color=K.GREEN, at=2, sfx="ding"),
        ], hits=[(0, "wood_low", 0.7, "曲线"), (1, "pop", 0.9, "余量")]),
        S("③ 只管增加力量", "坚持 4 招 · 增加自己力量", [
            Custom(C.power, x=540, y=780, at=0, enter="fade", grow=1, left="今天的我", right="目标难度",
                   me0=0.2, me1=0.9),
        ], hits=[(0, "wood_low", 0.7, "对比"), (1, "shaker", 0.8, "长高"), (2, "ding", 1.0, "超过")]),
        S("④ 每天做一点", "坚持 4 招 · 没有人做就不会出现", [
            Custom(C.tally, x=540, y=780, at=0, enter="pop", n=14, b0=0, step=0.25, title="每天一小步"),
        ], hits=[(0, "pop", 0.7, "打勾"), (1, "pop", 0.7, "打勾"), (2, "pop", 0.7, "打勾"),
                 (3, "ding", 0.9, "打满")]),
        S("不急不丧，打持久战", "一句话", [
            Big("持久", 540, 720, 260, at=1, sfx="kick", rays=True, glow=True, spark=True),
            Label("不急", 300, 460, 50, at=0, sfx="pop"), Label("不丧", 780, 460, 50, at=0),
        ], shake=[1], punch=0.025),
        # ---- 片尾 42
        outro("你的目标卡在第几幕？", "起点太低，还有戏吗？", "长期目标，打持久战"),
    ]
    return episode(5, "protracted", "论持久战", "目标太远，怎么撑下去？", ACC, shots,
                   [f"{BOOK}第二卷《论持久战》（一九三八年五月）"],
                   "不急不丧|打【持久战】", 8,
                   ["引文出自《论持久战》：“中国会亡吗？答复：不会亡……中国能够速胜吗？答复：不能速胜，抗日战争是持久战。”"
                    "“中国会亡”“中国很快就能战胜”“抗战十个月的经验”“三幕戏”“最困难的时期，然而它是转变的枢纽”“转弱为强”"
                    "“全体演员的努力，最精彩的结幕”“描画一个轮廓”“惟有努力于增加自己力量”“持久战和最后胜利没有人做就不会出现”；"
                    "“很快就能战胜”为原句缩写。",
                    "三幕牌“我方防御 / 准备反攻 / 战略反攻”为三个阶段的缩写；平台期曲线、力量对比柱、打卡格均为示意。",
                    "“当下”部分（健身、背单词）为现象示意，不引用数据；坚持 4 招为对原文的今日化应用，“前三月”等为示意。"
                    "画面不出现战争场面与历史人物形象。"],
                   tags="#长期主义 #坚持")
