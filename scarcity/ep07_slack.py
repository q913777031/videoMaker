"""07 余闲：为什么日程排满，一点意外就崩？（重做版）"""

from adler import kit as K
from adler.core import Card, Counter, Custom, Icon, Label, Pops, Rays, Shot, Spark, end_shot
from engine.gfx import clamp01, ease_out

from . import art as A
from .common import BOOK, ask, drop, episode, slam, tip2

ACC = "#3F8F6B"
GROUND = A.GROUND_Y
REFS = [BOOK, "Strategy+Business: Cut Your Company's Fat but Keep Some Slack（St. John's 医院案例）."]

SMALL = [(-0.55, -0.4, 60, K.RED), (0.0, -0.4, 60, K.GOLD), (0.55, -0.4, 60, "#5E8FA8"),
         (-0.55, 0.3, 60, K.GREEN), (0.0, 0.3, 60, K.OTHER3), (0.55, 0.3, 60, K.OTHER2)]
BIG = [(-0.5, -0.3, 70, K.RED), (0.3, -0.35, 60, K.GOLD), (-0.1, 0.25, 80, "#5E8FA8")]
FULL = [(j, r, 1, ACC if (j + r) % 2 else "#6FAE8E", -9) for j in range(5) for r in range(6)]


def clamp(x):
    return max(0.0, min(1.0, x))


def _pack(c, g, t, d):
    """小箱子装满（第 0–5 拍逐件放入），第 8 拍“临时会议”砸下被弹开。"""
    A.suitcase(c, 0, 0, 380, 340, ACC, SMALL, 1, clamp(g.span(0, 5)))
    k = g.since(8)
    if k >= 0:
        u = clamp(k / 0.25)
        y = -560 + 380 * ease_out(u) if k < 0.25 else -180 - 160 * clamp((k - 0.25) / 0.4)
        x = 0 if k < 0.25 else 260 * clamp((k - 0.25) / 0.4)
        with K.at(c, x, y, 20 * clamp((k - 0.25) / 0.4)):
            K.rr(c, 0, 0, 260, 90, 16, K.RED)
            K.text(c, "临时会议", 0, 0, 44, "serif_black", K.PAPER)


def _bigcase(c, g, t, d):
    """大箱子有空位，“临时会议”轻松放进去。"""
    A.suitcase(c, 0, 0, 560, 400, "#7C8FA6", BIG, 1, 1)
    k = clamp(g.since(1) / 0.4)
    with K.at(c, 120, -320 + 400 * ease_out(k), 0, 0.8):
        K.rr(c, 0, 0, 260, 90, 16, K.RED)
        K.text(c, "临时会议", 0, 0, 44, "serif_black", K.PAPER)


def _dominoes(c, g, t, d):
    K.ground(c, 6, x0=-440, x1=440)
    for i in reversed(range(6)):
        k = clamp(g.since(2 + i * 0.5) / 0.35)
        K.domino(c, -300 + i * 120, 0, 50, 200, (90 if i == 5 else 38) * k * k, K.RED if i == 0 else ACC)


def build():
    shots = [
        ask("箱子 快满 了|还 塞得下 【吗】？", [
            Custom(_pack, x=540, y=960, at=0, enter="none"),
        ], hits=[(1, "wood_low", 0.6, "装箱"), (3, "wood_low", 0.6, "装箱"), (5, "wood_low", 0.6, "装满")],
            note="互动：小箱子快装满"),
        Shot(4, "倒计时3秒|一件急事要塞进来", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(_pack, x=540, y=960, at=0, enter="none"),
            Label("塞不下！", 540, 1250, 50, at=10, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (8, "kick", 0.9, "临时会议砸下被弹开")], flashes=[6], shake=[(6, 12.0), (8, 14.0)], punch=0.025,
            note="临时会议砸下，被弹开"),
        Shot(2, "大箱子随手放下|差别在于留没留空", "互动小游戏", [
            Custom(_bigcase, x=540, y=880, at=0, enter="none"),
            Icon("check", 820, 620, 110, color=K.GREEN, at=3, sfx="ding"),
        ], text_beat=0, hits=[(1, "wood_low", 0.8, "放进去")], note="大箱子放得下"),
        drop("余闲", "Slack", "留出来的空间|就是【余闲】", "留白 缓冲 备用", size=220),
        Shot(4, "会议一个接一个|临时加一个就全乱了", "情境演绎", [
            Custom(A.calendar, x=540, y=800, at=0, enter="pop", rows=6, blocks=FULL),
            Card("临时会议", 540, 780, 56, at=6, fill=K.RED, color=K.PAPER, rot=-6, sfx="kick"),
            Label("全天后移", 540, 1180, 44, at=10, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_low", 0.7, "日程排满")], shake=[(6, 12.0)], note="排满的日程被砸乱"),
        Shot(4, "没有余闲|一点意外就连环倒", "机制示意", [
            Custom(_dominoes, x=540, y=900, at=0, enter="fade"),
            Label("一环扣一环", 540, 1120, 44, at=10, fill=K.RED, sfx="rim"),
        ], hits=[(2, "rim", 0.9, "第一块倒下"), (4, "wood_low", 0.7, "连锁倒下"), (5, "wood_low", 0.7, "最后一块")],
            note="多米诺连锁倒下"),
        Shot(4, "一家美国医院|手术室排得满满的", "研究证据 · 书中案例", [
            Counter(0, 100, 540, 620, 220, at=0, land=4, suffix="%", sub="手术室排程"),
            Card("急诊", 300, 980, 54, at=6, fill=K.RED, color=K.PAPER, rot=-5, sfx="rim"),
            Label("排好的手术往后挤", 680, 980, 40, at=9, fill=K.INK2, sfx="wood_high"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：满负荷医院"),
        Shot(4, "他们干脆空出一间|专接急诊", "研究证据 · 书中案例", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Card("空房", 540, 760, 80, at=0, sfx="ding"),
            Card("急诊", 540, 500, 54, at=5, enter="drop", fill=K.RED, color=K.PAPER, sfx="wood_low"),
            Icon("check", 760, 760, 110, color=K.GREEN, at=9, sfx="ding"),
        ], research=True, note="空出一间手术室"),
        Shot(4, "下午3点后的手术|少了45%", "研究证据 · 书中案例", [
            Counter(0, 45, 540, 640, 220, at=0, land=4, suffix="%", sub="下午 3 点后的手术减少"),
            Label("手术总量还多了约5%", 540, 980, 42, at=8, fill=ACC, sfx="ding"),
        ], research=True, note="结果数字落定"),
        slam("留白", "留白 不是 【浪费】", "是给意外|留一个位置"),
        Shot(4, "第一招：日程只排满八成", "小方法", [
            Custom(A.calendar, x=540, y=800, at=0, enter="none", rows=5,
                   blocks=[(j, r, 1, ACC, j * 0.5 + r * 0.25) for j in range(5) for r in range(4)]),
            Label("留 20% 空白", 540, 1080, 46, at=8, fill=K.GREEN, sfx="ding"),
            Spark(540, 1080, at=8),
        ], hits=[(0, "wood_low", 0.7, "排日程"), (4, "wood_low", 0.7, "排日程")], note="只排四行，留一行"),
        tip2("第二招：每天留|30分钟空白", "留 30 分钟|【空白】", 120),
        end_shot(REFS, "08 跳出稀缺：别靠意志力，靠设计"),
    ]
    return episode(7, "slack", "余闲", "为什么日程排满，一点意外就崩？", ACC, shots, REFS,
                   "日程排满|一点意外就【崩】？",
                   ["“余闲”与行李箱比喻出自《稀缺》第 3 章；装箱小游戏、日程表、多米诺为示意，两招为方法建议。",
                    "St. John's Regional Health Center（美国密苏里州）空出一间手术室专接计划外手术后，手术量约增 5.1%，"
                    "下午 3 点后的手术约减 45%（据 Strategy+Business 报道，《稀缺》第 9 章引用该案例）。"],
                   "#时间管理")
