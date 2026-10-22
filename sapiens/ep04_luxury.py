"""04 奢侈品陷阱：为什么涨了工资，还是不够花？（重做版）"""

from adler import kit as K
from adler.core import Counter, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop2, redo, slam2, tip2

ACC = "#D9703A"
G = A.GROUND_Y
REFS = [BOOK, "Brickman, Coates & Janoff-Bulman (1978). Lottery winners and accident victims. JPSP."]
CARDS = [("phone", "手机", True), ("gift", "外卖", True), ("target", "网约车", True),
         ("heart", "会员", True), ("cloud", "空调", True), ("house", "电梯", True)]


def build():
    shots = [
        ask("下面 这些|你 离得开 【几样】？", [
            Custom(A.pick_cards, x=540, y=950, at=0, enter="none", cards=CARDS, b0=3),
        ], hits=[(3, "pop", 0.6, "卡"), (4, "pop", 0.6, "卡"), (5, "pop", 0.6, "卡"), (6, "pop", 0.6, "卡")],
            note="互动：离不开的东西"),
        Shot(4, "倒计时3秒|数一数", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.pick_cards, x=540, y=950, at=0, enter="none", cards=CARDS, b0=-9, reveal=8),
            Label("一样都离不开", 540, 1262, 46, at=11, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (8, "ding", 0.9, "全部打勾")], flashes=[6], shake=[(6, 12.0)], punch=0.025, note="全部打勾"),
        Shot(2, "它们以前|全都是奢侈品", "互动小游戏", [
            Pops("昨天 的 奢侈|今天 的 【必需】", 540, 760, 100, at=0, step=1),
        ], text_beat=0, note="揭晓"),
        drop2("奢侈品陷阱", "Luxury Trap", "多出来的钱|很快变成新的【必需】", "升级 消费 习惯", size=150),
        Shot(4, "书里的例子：有了邮件|我们反而更忙了", "原书 · 例子", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="工作邮箱",
                   msgs=[(1, "请今天回复"), (4, "补充一点"), (7, "再确认一下"), (10, "紧急！")]),
        ], hits=[(1, "wood_high", 0.7, "邮件"), (4, "wood_high", 0.7, "邮件"), (7, "wood_high", 0.7, "邮件"),
                 (10, "rim", 0.9, "邮件")], note="邮件一封接一封"),
        Shot(4, "", "一句话", [
            Pops("省下 的 时间|被 更多 的 【事】 填满", 540, 780, 96, at=0, step=2),
        ], punch=0.02, flashes=[10], note="金句"),
        Shot(4, "研究者访问了|一批彩票大奖得主", "研究证据 · Brickman 等 1978", [
            Counter(0, 22, 540, 620, 220, at=0, land=4, sub="位大奖得主"),
            Icon("gift", 540, 960, 130, color=ACC, at=6, sfx="wood_high"),
            Spark(540, 960, at=6),
            Label("一夜暴富", 540, 1120, 44, at=10, fill=K.GOLD, sfx="ding"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "他们并没有比普通人|更快乐", "研究证据 · Brickman 等 1978", [
            Fig(360, G, 300, at=0, pose="relax", mood="calm", hair="short"),
            Fig(720, G, 300, at=2, pose="relax", mood="calm", hair="bun", color=K.OTHER2, sfx="wood_low"),
            Icon("scale", 540, 560, 160, color=K.INK2, at=5, sfx="rim"),
            Label("差不多", 540, 760, 46, at=10, fill=K.INK2, sfx="wood_high"),
        ], draw=A.ground, research=True, note="两组差不多"),
        Shot(4, "好日子很快被习惯|变成新的“标准”", "原书 · 大意", [
            Custom(A.two_lines, x=540, y=780, at=0, enter="fade", b0=0, b1=12),
            Label("条件涨", 300, 1080, 40, at=4, fill=ACC, sfx="wood_high"),
            Label("期望也涨", 780, 1080, 40, at=8, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_low", 0.7, "曲线上升")], note="条件与期望一起上升（示意）"),
        slam2("习惯", "一旦 习惯|就 【回不去】", "升级很容易|降级很痛苦"),
        Shot(4, "第一招：列一张|“其实可以不要”清单", "小方法", [
            Custom(A.checklist, x=540, y=800, at=0, enter="pop", b0=2, step=3, title="其实可以不要",
                   items=[("第三个会员", False), ("天天外卖", False), ("顺手打车", False), ("冲动换机", False)]),
        ], hits=[(2, "rim", 0.8, "✗"), (5, "rim", 0.8, "✗"), (8, "rim", 0.8, "✗"), (11, "ding", 0.9, "✗")], note="可以不要清单"),
        tip2("第二招：想升级时|先等一周", "升级 前 等 【一周】", 110),
        end_shot(REFS, "05 想象的秩序：为什么名校大厂自带光环"),
    ]
    return redo(4, "luxury", "奢侈品陷阱", "为什么涨了工资，还是不够花？", ACC, shots, REFS,
                "涨了工资|还是【不够花】？",
                ["“奢侈品陷阱”与电子邮件的例子出自《人类简史》第 5 章；离不开清单小游戏为情境演绎，曲线为示意，两招为方法建议。",
                 "Brickman 等 (1978)：22 位彩票大奖得主的幸福感与对照组无显著差异。"])
