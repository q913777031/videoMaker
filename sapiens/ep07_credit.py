"""07 信用：为什么敢背 30 年房贷？"""

from adler import kit as K
from adler.core import Arrow, Counter, Custom, Fig, Icon, Label, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#3A6EA5"
G = A.GROUND_Y
REFS = [BOOK]


def build():
    shots = [
        hook("背 30年 房贷|凭 【什么】？", 108),
        loop("凭的是：相信明天|会比今天更好", pose="think", mood="open"),
        Shot(4, "首付掏空六个钱包|剩下的交给未来", "情境演绎", [
            Icon("house", 360, 720, 240, color=ACC, at=0, sfx="wood_low"),
            Custom(A.bill, x=760, y=720, at=2, enter="drop", rot=-4, title="房贷合同", amount="360期", sfx="rim"),
            Icon("clock", 760, 1020, 110, color=K.INK2, at=5, sfx="wood_high"),
        ], note="房子与房贷合同"),
        drop("信用", "Credit", "拿【未来】的钱|做今天的事", 220),
        Shot(4, "银行借你钱|赌的是你未来能赚到", "原书 · 大意", [
            Icon("clock", 300, 700, 150, color=K.INK2, at=0, sfx="wood_low"),
            Label("未来", 300, 860, 36, at=0, fill=K.INK2),
            Icon("clock", 780, 700, 150, color=ACC, at=2, sfx="wood_low"),
            Label("现在", 780, 860, 36, at=2, fill=ACC),
            Arrow((380, 640), (700, 640), at=4, bend=-0.3, color=ACC, sfx="rim"),
            Spark(700, 640, at=4),
        ], note="从未来借到现在"),
        line("相信 未来|今天 才 敢 【开始】", 100),
        Shot(4, "可要是大家都不信了呢？|书里讲过一个泡沫", "原书 · 例子", [
            Counter(0, 1719, 540, 640, 200, at=0, land=4, fmt="{:.0f}", suffix="年", sub="法国 · 密西西比公司"),
        ], research=True, flashes=[4], note="二次钩子：年份落定"),
        Shot(4, "股价被吹得越来越高|人人都想上车", "原书 · 例子", [
            Custom(A.bubble_pop, x=540, y=760, at=0, enter="none", b0=0, pop=16, r0=80, r1=280, label="股价"),
        ], hits=[(0, "wood_low", 0.7, "泡沫变大"), (8, "wood_high", 0.7, "泡沫变大")], research=True, note="泡沫吹大"),
        Shot(4, "1720年泡沫破裂|无数人倾家荡产", "原书 · 例子", [
            Custom(A.bubble_pop, x=540, y=760, at=0, enter="none", b0=-8, pop=2, r0=200, r1=300, label="股价"),
            Fig(540, G, 300, at=4, pose="sit_sad", mood="sad", hair="short", sfx="wood_low"),
        ], draw=A.ground, hits=[(2, "kick", 0.9, "泡沫破裂")], shake=[(2, 12.0)], flashes=[2], research=True, note="泡沫破裂"),
        slam("泡沫", "信心能造富|也能一夜崩盘"),
        doubt("书中对资本主义的描述|被批评过于简化"),
        tip("试试：借钱前想想|最坏情况扛得住吗"),
        end_shot(REFS, "08 承认无知：为什么敢说“不知道”的人进步最快"),
    ]
    return episode(7, "credit", "信用", "为什么敢背 30 年房贷？", ACC, shots, REFS,
                   "背 30 年房贷|凭【什么】？",
                   ["“信用建立在对未来的信任上”及密西西比泡沫（约翰·劳，1719 年疯涨、1720 年破裂）出自《人类简史》第 16 章。",
                    "房贷情境为演绎；书中对资本主义的叙述被部分经济史学者批评过于简化。"])
