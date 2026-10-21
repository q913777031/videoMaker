"""04 奢侈品陷阱：为什么涨了工资，还是不够花？"""

from adler import kit as K
from adler.core import Counter, Custom, Fig, Icon, Shot, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#D9703A"
G = A.GROUND_Y
REFS = [BOOK, "Brickman, Coates & Janoff-Bulman (1978). Lottery winners and accident victims. JPSP."]


def build():
    shots = [
        hook("涨了 工资|还是 【不够花】？", 108),
        loop("不是你乱花钱|是“奢侈”变成了“必需”", pose="shrug", hair="bun", color=K.OTHER2),
        Shot(4, "手机、外卖、打车、会员|现在哪样离得开？", "情境演绎", [
            Custom(A.checklist, x=540, y=800, at=0, enter="pop", b0=2, step=2, title="现在离不开",
                   items=[("手机", True), ("外卖", True), ("打车", True), ("会员", True)]),
        ], hits=[(2, "wood_high", 0.8, "✓"), (4, "wood_high", 0.8, "✓"), (6, "wood_high", 0.8, "✓"), (8, "rim", 0.9, "✓")],
            note="清单全勾"),
        drop("奢侈品陷阱", "Luxury Trap", "昨天的奢侈|今天成了【必需】", 150),
        Shot(4, "书里的例子：有了邮件|我们反而更忙了", "原书 · 例子", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="工作邮箱",
                   msgs=[(1, "请今天回复"), (3, "补充一点"), (5, "再确认一下"), (7, "紧急！")]),
        ], hits=[(1, "wood_high", 0.7, "邮件"), (3, "wood_high", 0.7, "邮件"), (5, "wood_high", 0.7, "邮件"), (7, "rim", 0.9, "邮件")],
            note="邮件一封接一封"),
        line("省下 的 时间|被 更多 的 【事】 填满"),
        Shot(4, "研究者访问了|一批彩票大奖得主", "研究证据 · Brickman 等 1978", [
            Counter(0, 22, 540, 660, 220, at=0, land=4, sub="位大奖得主"),
            Icon("gift", 540, 960, 120, color=ACC, at=5, sfx="wood_high"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "他们并没有比普通人|明显更快乐", "研究证据 · Brickman 等 1978", [
            Fig(360, G, 300, at=0, pose="relax", mood="calm", hair="short"),
            Fig(720, G, 300, at=0, pose="relax", mood="calm", hair="bun", color=K.OTHER2),
            Icon("scale", 540, 560, 160, color=K.INK2, at=2, sfx="rim"),
        ], draw=A.ground, research=True, note="两组差不多"),
        Shot(4, "好日子很快会被习惯|然后变成新的“标准”", "原书 · 大意", [
            Custom(A.two_lines, x=540, y=780, at=0, enter="fade", b0=0, b1=12),
        ], hits=[(0, "wood_low", 0.7, "曲线上升")], note="条件与期望一起上升（示意）"),
        slam("习惯", "一旦习惯|就再也回不去"),
        doubt("这项研究只有22人|也没测中奖前的状态"),
        tip("试试：列一张|“其实可以不要”清单", hair="bun", color=K.OTHER2),
        end_shot(REFS, "05 想象的秩序：为什么名校大厂自带光环"),
    ]
    return episode(4, "luxury", "奢侈品陷阱", "为什么涨了工资，还是不够花？", ACC, shots, REFS,
                   "涨了工资|还是【不够花】？",
                   ["“奢侈品陷阱”与电子邮件的例子出自《人类简史》第 5 章：一代人的奢侈品会变成下一代的必需品。",
                    "Brickman 等 (1978)：22 位彩票大奖得主的幸福感与对照组无显著差异。样本小、未测中奖前状态、对照组非随机分配。",
                    "两条曲线为示意。"])
