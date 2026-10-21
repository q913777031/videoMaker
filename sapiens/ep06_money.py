"""06 金钱：为什么手机里一串数字，能买到一切？"""

from adler import kit as K
from adler.core import Card, Counter, Custom, Fig, Icon, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#3F8F6B"
G = A.GROUND_Y
REFS = [BOOK, "McLeay, Radia & Thomas (2014). Money creation in the modern economy. Bank of England QB."]


def build():
    shots = [
        hook("手机里 一串 数字|为什么 能 【买到一切】？", 88),
        loop("不是数字值钱|是所有人都信它", pose="point", mood="open"),
        Shot(4, "工资到账、扫码付款|钱从没摸到过", "情境演绎", [
            Custom(A.balance, x=540, y=790, at=0, enter="pop", v0=0, v1=8888, b0=1, b1=5),
        ], hits=[(1, "wood_low", 0.7, "余额滚动"), (5, "ding", 0.9, "工资到账")], note="手机余额滚动到账"),
        drop("金钱", "Money", "钱是人类最成功的|【信任】系统", 220),
        Shot(4, "贝壳、金币、纸币|再到一串数字", "原书 · 大意", [
            Custom(A.money_steps, x=540, y=760, at=0, enter="none", b0=0, step=2),
        ], hits=[(0, "wood_low", 0.8, "贝壳"), (2, "wood_low", 0.8, "金币"), (4, "wood_low", 0.8, "纸币"), (6, "ding", 0.9, "数字")],
            note="货币演变"),
        line("你 信 我 也 信|它 就 【值钱】", 100),
        Shot(4, "英国央行：公众持有的钱|97%是银行存款", "研究证据 · 英格兰银行 2014", [
            Counter(0, 97, 540, 660, 220, at=0, land=4, suffix="%", sub="是银行账上的数字"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "真正的纸币和硬币|只占很小一部分", "研究证据 · 英格兰银行 2014", [
            Custom(lambda c, g, t, d: A.banknote(c, 0, 0, 260), x=420, y=760, at=0, enter="pop", sfx="wood_low"),
            Custom(lambda c, g, t, d: A.coin(c, 0, 0, 70), x=720, y=760, at=2, enter="pop", sfx="wood_high"),
        ], research=True, note="现金只占小部分"),
        Shot(4, "信仰不同、彼此敌对的人|也愿意收同一种钱", "原书 · 大意", [
            Fig(300, G, 300, at=0, mood="flat", hair="short", color=K.OTHER3),
            Fig(780, G, 300, at=0, mood="flat", hair="long", color=K.OTHER2),
            Custom(lambda c, g, t, d: A.coin(c, 0, 0, 70), x=540, y=640, at=2, enter="pop", sfx="ding"),
            Spark(540, 640, at=2),
        ], draw=A.ground, note="陌生人之间的金币"),
        slam("信任", "钱的背后|是陌生人之间的信任"),
        doubt("信任一旦崩塌|钱也会一夜贬值", tag="边界"),
        tip("试试：关掉免密支付|让花钱有点“感觉”"),
        end_shot(REFS, "07 信用：为什么敢背 30 年房贷"),
    ]
    return episode(6, "money", "金钱", "为什么手机里一串数字，能买到一切？", ACC, shots, REFS,
                   "手机里一串数字|为什么能【买到一切】？",
                   ["“钱是人类最普遍、最有效的互信系统”出自《人类简史》第 10 章。",
                    "英格兰银行 2014 年季刊：英国公众持有的货币中约 97% 是银行存款而非现金。",
                    "关掉免密支付为生活小建议，非书中内容。"])
