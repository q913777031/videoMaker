"""04 余闲：为什么留白反而更高效？"""

from adler import kit as K
from adler.core import Big, Card, Counter, Custom, Episode, Fig, Glow, Icon, Label, Pops, Rays, Shot, Spark, end_shot

from . import art as A

ACC = "#3F8F6B"
GROUND = A.GROUND_Y
REFS = ["Mullainathan & Shafir (2013). Scarcity: Why Having Too Little Means So Much.",
        "Strategy+Business: Cut Your Company's Fat but Keep Some Slack（St. John's 医院案例）.",
        "Carvalho, Meier & Wang (2016). Poverty and economic decision-making. AER."]

BIG_CASE = [(-0.5, -0.3, 70, K.RED), (0.3, -0.35, 60, K.GOLD), (-0.1, 0.25, 80, "#5E8FA8")]
SMALL_CASE = [(-0.55, -0.4, 60, K.RED), (0.0, -0.4, 60, K.GOLD), (0.55, -0.4, 60, "#5E8FA8"),
              (-0.55, 0.3, 60, K.GREEN), (0.0, 0.3, 60, K.OTHER3), (0.55, 0.3, 60, K.OTHER2)]


def _cases(c, g, t, d):
    A.suitcase(c, -220, 0, 330, 300, "#7C8FA6", BIG_CASE, 1, clamp(g.span(0, 3)))
    A.suitcase(c, 230, 40, 230, 220, ACC, SMALL_CASE, 1, clamp(g.span(4, 7)))


def _dominoes(c, g, t, d):
    """六块骨牌从左到右依次倒下，前五块斜靠在下一块上，最后一块平躺。"""
    K.ground(c, 6, x0=-440, x1=440)
    for i in reversed(range(6)):
        k = clamp(g.since(2 + i * 0.5) / 0.35)
        final = 90 if i == 5 else 38
        K.domino(c, -300 + i * 120, 0, 50, 200, final * k * k, K.RED if i == 0 else ACC)


def clamp(x):
    return max(0.0, min(1.0, x))


def build() -> Episode:
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("空着 一间 手术室|效率 反而 【更高】？", 540, 760, 92, at=0, step=1, gap=22),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "这家医院|真的这么做了", "先说结论", [
            Icon("house", 540, 700, 220, color=ACC, at=0, sfx="wood_low"),
            Icon("check", 700, 560, 100, color=K.GREEN, at=1, sfx="rim"),
            Spark(700, 560, at=1),
        ], text_beat=0, note="医院与对勾（预告结果）"),
        Shot(4, "大箱子随便装|小箱子每样都得算", "原书 · 比喻", [
            Custom(_cases, x=540, y=800, at=0, enter="fade"),
        ], hits=[(0, "wood_low", 0.8, "大箱子装入"), (4, "wood_low", 0.8, "小箱子装入"), (7, "rim", 0.8, "小箱子塞满")],
            note="行李箱比喻：大箱子松，小箱子满"),
        Shot(4, "留出来的空间|就是【余闲】", "原书 · 核心概念", [
            Big("余闲", 540, 700, 220, at=0, sfx="kick", sub="Slack", rays=True, glow=True, shine=True, spark=True,
                note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "没有余闲|一点意外就全盘打乱", "机制示意", [
            Custom(_dominoes, x=540, y=900, at=0, enter="fade"),
        ], hits=[(2, "rim", 0.9, "第一块倒下"), (4, "wood_low", 0.7, "连锁倒下"), (5, "wood_low", 0.7, "最后一块倒下")],
            note="多米诺连锁倒下"),
        Shot(4, "", "连环崩", [
            Pops("插单 加班|改期 【连环崩】", 540, 780, 100, at=0, step=1, gap=30),
        ], punch=0.02, flashes=[3], note="逐词弹出"),
        # 二次钩子：真实案例
        Shot(4, "一家美国医院|手术室排得满满的", "研究证据 · 书中案例", [
            Counter(0, 100, 540, 660, 220, at=0, land=4, suffix="%", sub="手术室使用率（接近）"),
        ], research=True, punch=0.02, note="数字滚动落定"),
        Shot(2, "急诊一来|排好的手术只能往后挤", "研究证据 · 书中案例", [
            Card("急诊", 330, 640, 54, at=0, rot=-4, fill=K.RED, color=K.PAPER, sfx="rim"),
            Icon("clock", 740, 640, 170, color=K.INK2, at=2, sfx="wood_low"),
            Label("加班到深夜", 740, 860, 36, at=4, fill=K.INK2, sfx="wood_high"),
        ], text_beat=0, note="急诊挤占排程"),
        Shot(4, "他们空出一间|专接计划外手术", "研究证据 · 书中案例", [
            Rays(540, 720, 520, at=2, alpha=0.18),
            Card("空房", 540, 720, 70, at=2, rot=0, sfx="ding"),
            Spark(540, 720, at=2),
        ], research=True, flashes=[2], note="空出一间手术室"),
        Shot(4, "手术多了约5%|下午3点后的手术少了45%", "研究证据 · 书中案例", [
            Counter(0, 45, 540, 700, 200, at=0, land=4, suffix="%", sub="下午 3 点后的手术减少"),
        ], research=True, note="结果数字落定"),
        Shot(4, "《稀缺》的部分研究|也存在争议与复现问题", "常见质疑", [
            Icon("scale", 540, 720, 230, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 780, 560, 100, color=K.RED, at=4, sfx="rim"),
        ], note="理论边界"),
        Shot(2, "试试：在日程里|留一段空白", "小练习", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Fig(540, GROUND, 330, at=0, pose="relax", mood="happy", hair="bun", color=K.OTHER2),
            Spark(540, 560, at=1, sfx="clap"),
        ], draw=A.ground, text_beat=0, punch=0.02, note="留白（回报）"),
        end_shot(REFS, None),
    ]
    return Episode(4, "slack", "余闲", "为什么留白反而更高效？", ACC, shots, refs=REFS,
                   publish_title="为什么留白反而更高效？｜稀缺04 余闲",
                   hashtags="#稀缺 #行为经济学 #效率 #读书",
                   cover_title="空着一间手术室|效率反而【更高】？", cover_sub="稀缺 · 余闲", cover_shot=3, cover_t=1.6,
                   notes=["「余闲」（slack）与行李箱比喻为《稀缺》（2013）的内容：资源宽裕时不必精打细算，余闲能吸收意外冲击。",
                          "医院案例：美国密苏里州 St. John's Regional Health Center 的手术室曾接近满负荷排程，急诊（约占两成）不断挤占已排手术；"
                          "在顾问建议下空出一间手术室专接计划外手术后，手术总量增加约 5.1%，下午 3 点后进行的手术减少约 45%。"
                          "数据据 Strategy+Business《Cut Your Company's Fat but Keep Some Slack》的报道，《稀缺》书中亦引用该案例。",
                          "理论边界：《稀缺》引用的部分实验存在复现问题（如 Shah 等 2012 的一项实验），"
                          "Carvalho 等 (2016) 未发现发薪日前后认知功能差异。片中以「存在争议与复现问题」呈现。",
                          "多米诺与行李箱为概念示意。"]).build()
