"""07 余闲：为什么日程排满，一点意外就崩？"""

from adler import kit as K
from adler.core import Big, Card, Counter, Custom, Fig, Glow, Icon, Label, Pops, Rays, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, episode

ACC = "#3F8F6B"
GROUND = A.GROUND_Y
REFS = [BOOK, "Strategy+Business: Cut Your Company's Fat but Keep Some Slack（St. John's 医院案例）."]

FULL = [(j, r, 1, ACC if (j + r) % 2 else "#6FAE8E", 1 + (j + r) % 4) for j in range(5) for r in range(6)]
BIG_CASE = [(-0.5, -0.3, 70, K.RED), (0.3, -0.35, 60, K.GOLD), (-0.1, 0.25, 80, "#5E8FA8")]
SMALL_CASE = [(-0.55, -0.4, 60, K.RED), (0.0, -0.4, 60, K.GOLD), (0.55, -0.4, 60, "#5E8FA8"),
              (-0.55, 0.3, 60, K.GREEN), (0.0, 0.3, 60, K.OTHER3), (0.55, 0.3, 60, K.OTHER2)]


def clamp(x):
    return max(0.0, min(1.0, x))


def _cases(c, g, t, d):
    A.suitcase(c, -220, 0, 330, 300, "#7C8FA6", BIG_CASE, 1, clamp(g.span(0, 3)))
    A.suitcase(c, 230, 40, 230, 220, ACC, SMALL_CASE, 1, clamp(g.span(4, 7)))


def _dominoes(c, g, t, d):
    """六块骨牌从左到右依次倒下，前五块斜靠在下一块上，最后一块平躺。"""
    K.ground(c, 6, x0=-440, x1=440)
    for i in reversed(range(6)):
        k = clamp(g.since(2 + i * 0.5) / 0.35)
        K.domino(c, -300 + i * 120, 0, 50, 200, (90 if i == 5 else 38) * k * k, K.RED if i == 0 else ACC)


def _jam(c, g, t, d):
    """排满的日程表上硬塞进一块红色“临时会”，其余格子被挤得抖动。"""
    A.calendar(c, g, t, dict(d, blocks=FULL))
    k = clamp(g.since(10) / 0.3)
    if k > 0:
        with K.at(c, 0, -20, -6, 0.6 + 0.4 * k):
            K.rr(c, 0, 0, 330, 110, 18, K.RED, k)
            K.text(c, "临时会议", 0, 0, 46, "serif_black", K.PAPER, k)


def build():
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("日程 排满|一点 意外 就 【崩】？", 540, 760, 100, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "问题不在意外|在于你没留空", "先说结论", [
            Icon("house", 540, 700, 220, color=ACC, at=0, sfx="wood_low"),
            Icon("check", 700, 560, 100, color=K.GREEN, at=1, sfx="rim"),
            Spark(700, 560, at=1),
        ], text_beat=0, note="对勾弹出"),
        Shot(4, "会议一个接一个|临时加一个就全乱了", "情境演绎", [
            Custom(_jam, x=540, y=800, at=0, enter="pop", rows=6),
        ], hits=[(1, "wood_low", 0.7, "日程排满"), (3, "wood_low", 0.7, "日程排满"), (10, "kick", 0.8, "临时会议砸进来")],
            shake=[(10, 10.0)], note="排满的日程被临时会议砸乱"),
        Shot(4, "留出来的空间|就是【余闲】", "原书 · 核心概念", [
            Big("余闲", 540, 700, 220, at=0, sfx="kick", sub="Slack", rays=True, glow=True, shine=True, spark=True,
                note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "大箱子随便装|小箱子每样都得算", "原书 · 比喻", [
            Custom(_cases, x=540, y=800, at=0, enter="fade"),
        ], hits=[(0, "wood_low", 0.8, "大箱子装入"), (4, "wood_low", 0.8, "小箱子装入"), (7, "rim", 0.8, "小箱子塞满")],
            note="行李箱比喻"),
        Shot(4, "没有余闲|一点意外就连环倒", "机制示意", [
            Custom(_dominoes, x=540, y=900, at=0, enter="fade"),
        ], hits=[(2, "rim", 0.9, "第一块倒下"), (4, "wood_low", 0.7, "连锁倒下"), (5, "wood_low", 0.7, "最后一块倒下")],
            note="多米诺连锁倒下"),
        Shot(4, "一家美国医院|手术室排得满满的", "研究证据 · 书中案例", [
            Counter(0, 100, 540, 660, 220, at=0, land=4, suffix="%", sub="手术室排程（接近）"),
        ], research=True, punch=0.02, note="二次钩子：数字落定"),
        Shot(2, "急诊一来|排好的手术只能往后挤", "研究证据 · 书中案例", [
            Card("急诊", 330, 640, 54, at=0, rot=-4, fill=K.RED, color=K.PAPER, sfx="rim"),
            Icon("clock", 740, 640, 170, color=K.INK2, at=2, sfx="wood_low"),
            Label("加班到深夜", 740, 860, 36, at=4, fill=K.INK2, sfx="wood_high"),
        ], text_beat=0, note="急诊挤占排程"),
        Shot(4, "他们干脆空出一间|专接计划外手术", "研究证据 · 书中案例", [
            Rays(540, 720, 520, at=2, alpha=0.18),
            Card("空房", 540, 720, 70, at=2, sfx="ding"),
            Spark(540, 720, at=2),
        ], research=True, flashes=[2], note="空出一间手术室"),
        Shot(4, "手术多了约5%|下午3点后的手术少了45%", "研究证据 · 书中案例", [
            Counter(0, 45, 540, 700, 200, at=0, land=4, suffix="%", sub="下午 3 点后的手术减少"),
        ], research=True, note="结果数字落定"),
        Shot(4, "余闲也不是越多越好|闲置同样有成本", "常见质疑", [
            Icon("scale", 540, 720, 230, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 780, 560, 100, color=K.RED, at=4, sfx="rim"),
        ], note="边界"),
        Shot(2, "试试：每天留|30分钟空白", "小练习", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Fig(540, GROUND, 330, at=0, pose="relax", mood="happy", hair="bun", color=K.OTHER2),
            Spark(540, 560, at=1, sfx="clap"),
        ], draw=A.ground, text_beat=0, punch=0.02, note="回报"),
        end_shot(REFS, "08 跳出稀缺：别靠意志力，靠设计"),
    ]
    return episode(7, "slack", "余闲", "为什么日程排满，一点意外就崩？", ACC, shots, REFS,
                   "日程排满|一点意外就【崩】？",
                   ["「余闲」（slack）与行李箱比喻为《稀缺》第 3 章内容。日程表、多米诺为示意。",
                    "St. John's Regional Health Center（美国密苏里州）手术室接近满负荷，空出一间专接计划外手术后，手术量约增 5.1%，"
                    "下午 3 点后的手术约减 45%（据 Strategy+Business 报道，《稀缺》第 9 章引用该案例）。"],
                   "#时间管理")
