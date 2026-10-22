"""07 信用：为什么敢背 30 年房贷？（重做版）"""

from adler import kit as K
from adler.core import Arrow, Card, Counter, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop2, redo, slam2, tip2

ACC = "#3A6EA5"
G = A.GROUND_Y
REFS = [BOOK]
LEFT = ("一共还", "约100万", K.INK2)
RIGHT = ("一共还", "约193万", K.RED)


def build():
    shots = [
        ask("房贷 借 100万|30年 一共 还 【多少】？", [
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=3, left=LEFT, right=RIGHT),
        ], hits=[(3, "wood_low", 0.8, "选项A"), (4, "wood_low", 0.8, "选项B")], note="互动：猜总还款"),
        Shot(4, "倒计时3秒|猜一个", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=-9, pick=7, pick_side=1, left=LEFT, right=RIGHT),
            Label("按年利率 5% 等额本息", 540, 1260, 42, at=10, fill=ACC, sfx="ding"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (7, "rim", 0.9, "揭晓 193 万")], flashes=[6], shake=[(6, 12.0)], punch=0.025, note="揭晓约 193 万"),
        Shot(2, "多还的93万|是你押给未来的", "互动小游戏", [
            Pops("你 敢 借|因为 你 【相信未来】", 540, 760, 96, at=0, step=1),
        ], text_beat=0, note="揭晓"),
        drop2("信用", "Credit", "拿【未来】的钱|做今天的事", "房贷 创业 贷款", size=220),
        Shot(4, "银行借你钱|赌的是你未来能赚到", "原书 · 大意", [
            Icon("clock", 300, 700, 150, color=K.INK2, at=0, sfx="wood_low"),
            Label("未来", 300, 860, 36, at=0, fill=K.INK2),
            Icon("clock", 780, 700, 150, color=ACC, at=3, sfx="wood_low"),
            Label("现在", 780, 860, 36, at=3, fill=ACC),
            Arrow((380, 640), (700, 640), at=6, bend=-0.3, color=ACC, sfx="rim"),
            Spark(700, 640, at=6),
            Label("经济就这样越做越大", 540, 1060, 42, at=11, fill=ACC, sfx="ding"),
        ], note="从未来借到现在"),
        Shot(4, "", "一句话", [
            Pops("相信 未来|今天 才 敢 【开始】", 540, 780, 100, at=0, step=2),
        ], punch=0.02, flashes=[10], note="金句"),
        Shot(4, "可要是大家都不信了呢？|书里讲过一个泡沫", "原书 · 例子", [
            Counter(0, 1719, 540, 600, 200, at=0, land=4, fmt="{:.0f}", suffix="年", sub="法国 · 密西西比公司"),
            Icon("house", 540, 960, 140, color=ACC, at=7, sfx="wood_high"),
            Label("都说能发大财", 540, 1130, 44, at=11, fill=K.GOLD, sfx="ding"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：年份落定"),
        Shot(4, "股价被吹得越来越高|人人都想上车", "原书 · 例子", [
            Custom(A.bubble_pop, x=540, y=760, at=0, enter="none", b0=0, pop=16, r0=80, r1=280, label="股价"),
            Label("涨！", 260, 520, 44, at=4, fill=K.RED, sfx="wood_high"),
            Label("还在涨！", 820, 560, 44, at=8, fill=K.RED, sfx="wood_high"),
            Label("快上车！", 300, 1080, 44, at=12, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_low", 0.7, "泡沫变大")], research=True, note="泡沫吹大"),
        Shot(4, "1720年泡沫破裂|无数人倾家荡产", "原书 · 例子", [
            Custom(A.bubble_pop, x=540, y=760, at=0, enter="none", b0=-8, pop=2, r0=200, r1=300, label="股价"),
            Fig(540, G, 300, at=5, pose="sit_sad", mood="sad", hair="short", sfx="wood_low"),
            Custom(lambda c, g, t, d: A.banknote(c, 0, 0, 220, rot=-20), x=300, y=700, at=7, enter="drop", sfx="wood_low"),
            Label("一夜归零", 540, 520, 50, at=10, fill=K.RED, sfx="rim"),
        ], draw=A.ground, hits=[(2, "kick", 0.9, "泡沫破裂")], shake=[(2, 12.0)], flashes=[2], research=True, note="泡沫破裂"),
        slam2("泡沫", "信心 能 造富|也 能 【崩盘】", "信用是双刃剑"),
        Shot(4, "第一招：借钱前|先算清总共要还多少", "小方法", [
            Card("借 100 万", 540, 600, 60, at=0, sfx="wood_low"),
            Arrow((540, 680), (540, 860), at=3, color=K.RED, sfx="wood_high"),
            Card("30 年还约 193 万", 540, 960, 56, at=6, fill=K.RED, color=K.PAPER, sfx="rim"),
            Label("看总额，别只看月供", 540, 1150, 42, at=10, fill=ACC, sfx="ding"),
        ], note="算总额"),
        tip2("第二招：借之前想想|最坏能扛住吗", "最坏 情况|【扛得住】？", 110),
        end_shot(REFS, "08 承认无知：为什么敢说“不知道”的人进步最快"),
    ]
    return redo(7, "credit", "信用", "为什么敢背 30 年房贷？", ACC, shots, REFS,
                "背 30 年房贷|凭【什么】？",
                ["“信用建立在对未来的信任上”及密西西比泡沫（约翰·劳，1719 年疯涨、1720 年破裂）出自《人类简史》第 16 章。",
                 "房贷总额按 100 万、30 年、年利率 5%、等额本息计算：月供约 5368 元，合计约 193 万元。两招为方法建议。"])
