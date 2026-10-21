"""02 管窥：为什么越忙越乱？"""

from adler import kit as K
from adler.core import Arrow, Big, Card, Custom, Episode, Fig, Glow, Icon, Label, Pops, Rays, Shot, Spark, end_shot

from . import art as A

ACC = "#3A6EA5"
GROUND = A.GROUND_Y
REFS = ["Mullainathan & Shafir (2013). Scarcity: Why Having Too Little Means So Much.",
        "Shah, Mullainathan & Shafir (2012). Some consequences of having too little. Science.",
        "Camerer et al. (2018). Replicability of social science experiments. Nat Hum Behav."]


def build() -> Episode:
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("为什么 越忙|越【乱】？", 540, 760, 110, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "看到最后|有一招帮你走出隧道", "先说结论", [
            Fig(540, GROUND, 330, at=0, pose="think", mood="worried", hair="bun", color=K.OTHER2),
            Icon("key", 770, 540, 110, color=ACC, at=1, sfx="rim"),
            Spark(770, 540, at=1),
        ], draw=A.ground, text_beat=0, note="主角思考，钥匙弹出（预告最后的办法）"),
        Shot(4, "截止日期前|你的效率高得惊人", "情境演绎", [
            Fig(360, GROUND, 330, at=0, pose="push", mood="open", hair="bun", color=K.OTHER2),
            Icon("clock", 760, 600, 170, color=K.RED, at=2, sfx="wood_low"),
            Pops("【专注红利】", 740, 880, 64, at=5, step=1),
        ], draw=A.ground, note="截止日期逼出专注"),
        Shot(4, "可稀缺也让你只看见|【隧道】里的东西", "原书 · 核心概念", [
            Big("管窥", 540, 700, 220, at=0, sfx="kick", sub="Tunneling", rays=True, glow=True, shine=True, spark=True,
                note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "隧道外的一切|都被自动忽略", "机制示意", [
            Icon("heart", 250, 520, 120, color=K.RED, at=0),
            Icon("house", 830, 520, 120, color=K.INK2, at=0),
            Icon("friends", 250, 1050, 120, color=K.INK2, at=0),
            Icon("sun", 830, 1050, 120, color=K.GOLD, at=0),
            Icon("clock", 540, 780, 180, color=K.RED, at=0, enter="none"),
            Custom(A.tunnel, x=540, y=780, at=1, enter="fade", r0=900, r=230, close=1.6, sfx="tom"),
        ], note="四周压暗成隧道，只剩中间的截止时钟"),
        Shot(4, "", "管窥税", [
            Pops("忘了 吃饭|忘了 家人|忘了 【休息】", 540, 780, 92, at=0, step=1, gap=30),
        ], punch=0.02, note="被忽略的东西逐词弹出"),
        # 二次钩子
        Shot(4, "但更可怕的是|为了眼前你会去借", "反转", [
            Icon("clock", 300, 700, 150, color=K.INK2, at=0, sfx="wood_low"),
            Label("以后", 300, 860, 36, at=0, fill=K.INK2),
            Icon("clock", 780, 700, 150, color=K.RED, at=2, sfx="wood_low"),
            Label("现在", 780, 860, 36, at=2, fill=K.RED),
            Arrow((380, 640), (700, 640), at=4, bend=-0.3, color=ACC, sfx="rim"),
            Spark(700, 640, at=4),
        ], flashes=[4], punch=0.02, note="从“以后”借时间/资源给“现在”"),
        Shot(4, "游戏实验：资源少的玩家|每一次出手都更专注", "研究证据 · Shah 等 2012", [
            Fig(330, GROUND, 300, at=0, pose="point", mood="open", hair="short"),
            Card("机会：很少", 750, 560, 46, at=2, rot=-3, sfx="wood_low"),
            Icon("target", 750, 860, 160, color=ACC, at=4, sfx="rim"),
            Spark(750, 860, at=4),
        ], draw=A.ground, research=True, note="资源少 → 每次更专注（专注红利）"),
        Shot(4, "可以借的时候|他们借得更多、总分更低", "研究证据 · Shah 等 2012", [
            Card("向未来借|要付利息", 330, 640, 46, at=0, rot=3, sfx="wood_low"),
            Icon("chain", 760, 640, 160, color=K.RED, at=2, sfx="rim"),
            Icon("cross", 760, 900, 110, color=K.RED, at=4, sfx="rim"),
        ], research=True, note="带利息的“借”让总成绩变差（示意）"),
        Shot(2, "专注的红利|变成了管窥的代价", "原书 · 大意", [
            Big("代价", 540, 760, 160, at=0, sfx="kick", glow=True),
        ], text_beat=0, punch=0.03, shake=[0], note="代价二字砸下"),
        Shot(4, "其中一项实验|在大规模重复中没能复现", "常见质疑", [
            Icon("book", 400, 740, 180, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 720, 640, 110, color=K.RED, at=4, sfx="rim"),
        ], note="复现研究：Shah 2012 的一项实验未能复现，其余结果多数得到支持"),
        Shot(2, "试试：把重要的事|提前放进日程", "小练习", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Fig(540, GROUND, 330, at=0, pose="cheer", mood="happy", hair="bun", color=K.OTHER2),
            Spark(540, 560, at=1, sfx="clap"),
        ], draw=A.ground, text_beat=0, punch=0.02, note="走出隧道（回报）"),
        end_shot(REFS, "03 稀缺陷阱：为什么帮人还清债，没多久又欠了"),
    ]
    return Episode(2, "tunneling", "管窥", "为什么越忙越乱？", ACC, shots, refs=REFS,
                   publish_title="为什么越忙越乱？｜稀缺02 管窥",
                   hashtags="#稀缺 #行为经济学 #时间管理 #读书",
                   cover_title="为什么|越忙越【乱】？", cover_sub="稀缺 · 管窥", cover_shot=3, cover_t=1.6,
                   notes=["「专注红利」与「管窥」（tunneling）为《稀缺》（2013）的核心概念：稀缺让注意力集中在眼前的缺口上，"
                          "带来更高的效率，同时忽略隧道之外的事情，代价往往是借贷与拖延重要但不紧急的事。",
                          "游戏实验见 Shah, Mullainathan & Shafir (2012), Science 338: 682–685：资源少的玩家每次出手更专注；"
                          "允许以利息借用未来回合资源时，资源少的玩家借得更多、总成绩更差。片中卡片为示意，未标注原实验的具体参数。",
                          "复现情况：Camerer 等 (2018) 对社会科学实验的大规模重复中，Shah 等 2012 的一项实验未能复现；"
                          "Shah 等 (2019) 的后续重复也报告该实验未复现、其余多数结果得到支持。片中以「没能复现」如实呈现。"]).build()
