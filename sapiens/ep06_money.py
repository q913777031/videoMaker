"""06 金钱：为什么手机里一串数字，能买到一切？（重做版）"""

from adler import kit as K
from adler.core import Card, Counter, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop2, redo, slam2, tip2

ACC = "#3F8F6B"
G = A.GROUND_Y
REFS = [BOOK, "McLeay, Radia & Thomas (2014). Money creation in the modern economy. Bank of England QB."]
LEFT = ("一张纸币", "100元", ACC)
RIGHT = ("一个", "面包", K.GOLD)


def build():
    shots = [
        ask("流落 荒岛|你 要 【哪个】？", [
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=3, left=LEFT, right=RIGHT),
        ], hits=[(3, "wood_low", 0.8, "选项A"), (4, "wood_low", 0.8, "选项B")], note="互动：荒岛二选一"),
        Shot(4, "倒计时3秒|选一个", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=-9, pick=7, pick_side=1, left=LEFT, right=RIGHT),
            Label("岛上没人收钱", 540, 1260, 46, at=10, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (7, "ding", 0.9, "选中面包")], flashes=[6], shake=[(6, 12.0)], punch=0.025, note="选面包"),
        Shot(2, "没人信它|钱就只是一张纸", "互动小游戏", [
            Pops("钱 值钱|因为 大家 【都信】", 540, 760, 100, at=0, step=1),
        ], text_beat=0, note="揭晓"),
        drop2("金钱", "Money", "钱是人类最成功的|【信任】系统", "贝壳 金币 数字", size=220),
        Shot(4, "贝壳、金币、纸币|再到一串数字", "原书 · 大意", [
            Custom(A.money_steps, x=540, y=760, at=0, enter="none", b0=0, step=3),
            Label("越来越“虚”，却越来越通用", 540, 1080, 40, at=12, fill=ACC, sfx="ding"),
        ], hits=[(0, "wood_low", 0.8, "贝壳"), (3, "wood_low", 0.8, "金币"), (6, "wood_low", 0.8, "纸币"), (9, "ding", 0.9, "数字")],
            note="货币演变"),
        Shot(4, "", "一句话", [
            Pops("你 信 我 也 信|它 就 【值钱】", 540, 780, 100, at=0, step=2),
        ], punch=0.02, flashes=[12], note="金句"),
        Shot(4, "英国央行：公众手里的钱|97%是银行账上的数字", "研究证据 · 英格兰银行 2014", [
            Counter(0, 97, 540, 620, 220, at=0, land=4, suffix="%"),
            Icon("phone", 540, 960, 140, color=ACC, at=6, sfx="wood_high"),
            Label("只是一串数字", 540, 1130, 44, at=10, fill=ACC, sfx="ding"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "真正的纸币和硬币|只占很小一部分", "研究证据 · 英格兰银行 2014", [
            Custom(lambda c, g, t, d: A.banknote(c, 0, 0, 260), x=400, y=740, at=0, enter="pop", sfx="wood_low"),
            Custom(lambda c, g, t, d: A.coin(c, 0, 0, 70), x=720, y=740, at=3, enter="pop", sfx="wood_high"),
            Label("约 3%", 540, 1000, 56, at=8, fill=K.RED, sfx="rim"),
        ], research=True, note="现金只占小部分"),
        Shot(4, "信仰不同、互相敌对的人|也愿意收同一种钱", "原书 · 大意", [
            Fig(300, G, 300, at=0, mood="angry", hair="short", color=K.OTHER3),
            Fig(780, G, 300, at=0, mood="angry", hair="long", color=K.OTHER2, face=-1),
            Custom(lambda c, g, t, d: A.coin(c, 0, 0, 80), x=540, y=620, at=4, enter="pop", sfx="ding"),
            Spark(540, 620, at=4),
            Label("成交", 540, 820, 46, at=10, fill=ACC, sfx="rim"),
        ], draw=A.ground, note="陌生人之间的金币"),
        slam2("信任", "钱 就是|【信任】", "所以钱的背后|是陌生人之间的信任"),
        Shot(4, "第一招：花钱前|换算成工作小时", "小方法", [
            Card("一双鞋 ¥800", 380, 640, 48, at=0, rot=-3, sfx="wood_low"),
            Label("= 工作 16 小时", 380, 820, 44, at=4, fill=K.RED, sfx="rim"),
            Card("一顿外卖 ¥50", 720, 900, 48, at=7, rot=3, sfx="wood_low"),
            Label("= 工作 1 小时", 720, 1080, 44, at=11, fill=ACC, sfx="ding"),
        ], note="按时薪 50 元示意换算"),
        tip2("第二招：关掉免密支付|花钱才有感觉", "关掉 【免密支付】", 110),
        end_shot(REFS, "07 信用：为什么敢背 30 年房贷"),
    ]
    return redo(6, "money", "金钱", "为什么手机里一串数字，能买到一切？", ACC, shots, REFS,
                "手机里一串数字|为什么能【买到一切】？",
                ["“钱是人类最普遍、最有效的互信系统”出自《人类简史》第 10 章；荒岛小游戏为情境演绎。",
                 "英格兰银行 2014 年季刊：英国公众持有的货币中约 97% 是银行存款而非现金。",
                 "工时换算按时薪 50 元示意；两招为方法建议。"])
