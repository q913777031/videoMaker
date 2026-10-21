"""02 专注红利：为什么deadline前一晚，效率最高？"""

from adler import kit as K
from adler.core import Arrow, Big, Card, Custom, Fig, Glow, Icon, Pops, Rays, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, episode

ACC = "#3A6EA5"
GROUND = A.GROUND_Y
REFS = [BOOK, "Shah, Mullainathan & Shafir (2012). Some consequences of having too little. Science.",
        "Camerer et al. (2018). Replicability of social science experiments. Nat Hum Behav."]


def build():
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("拖了 两周|最后 一晚 【写完】？", 540, 760, 100, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "不是你突然变厉害|是“缺时间”在帮你", "先说结论", [
            Fig(540, GROUND, 330, at=0, pose="think", mood="open", hair="short"),
            Icon("bulb", 760, 520, 110, color=ACC, at=1, sfx="rim"),
            Spark(760, 520, at=1),
        ], draw=A.ground, text_beat=0, note="灯泡弹出"),
        Shot(4, "截止前一晚|你一口气写完了PPT", "情境演绎", [
            Fig(170, GROUND, 300, at=0, pose="sit", mood="open", hair="short"),
            Custom(A.laptop, x=660, y=800, at=0, enter="pop", w=480, p0=0.05, p1=1.0, b0=2, b1=14, title="汇报.pptx"),
        ], draw=A.ground, hits=[(2, "wood_low", 0.7, "开始写"), (14, "ding", 0.9, "写完 100%")], note="进度条一路冲到 100%"),
        Shot(4, "缺时间的时候|注意力会自动聚焦", "原书 · 核心概念", [
            Big("专注红利", 540, 700, 170, at=0, sfx="kick", sub="Focus Dividend", rays=True, glow=True, shine=True,
                spark=True, note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "杂念被挤出去|只剩眼前这件事", "机制示意", [
            Icon("target", 540, 780, 220, color=ACC, at=0, sfx="wood_low"),
            Arrow((180, 480), (430, 690), at=2, color=K.INK2, sfx="wood_high"),
            Arrow((900, 480), (650, 690), at=3, color=K.INK2, sfx="wood_high"),
            Arrow((180, 1080), (430, 870), at=4, color=K.INK2, sfx="wood_high"),
            Arrow((900, 1080), (650, 870), at=5, color=K.INK2, sfx="wood_high"),
            Spark(540, 780, at=6, sfx="rim"),
        ], note="四面八方的注意力收向靶心"),
        Shot(4, "", "一句话", [
            Glow(540, 780, 560, at=0, alpha=0.26),
            Pops("别人 一周|你 一晚 【搞定】", 540, 780, 104, at=0, step=1),
        ], punch=0.02, flashes=[4], note="金句逐词弹出"),
        Shot(4, "科学家用游戏|验证过这件事", "研究证据 · Shah 等 2012", [
            Fig(330, GROUND, 300, at=0, pose="point", mood="open", hair="short"),
            Card("机会：很少", 750, 560, 46, at=2, rot=-3, sfx="wood_low"),
            Icon("target", 750, 860, 160, color=ACC, at=4, sfx="rim"),
        ], draw=A.ground, research=True, flashes=[4], note="二次钩子：游戏实验"),
        Shot(4, "机会少的玩家|每一次都瞄得更认真", "研究证据 · Shah 等 2012", [
            Icon("target", 540, 760, 240, color=ACC, at=0, sfx="wood_low"),
            Spark(540, 760, at=2, sfx="ding"),
        ], research=True, note="专注红利"),
        Shot(4, "可聚焦的另一面|是别的事全看不见", "原书 · 大意", [
            Icon("eye", 540, 720, 220, color=K.INK2, at=0, sfx="wood_low"),
            Icon("cross", 680, 600, 100, color=K.RED, at=4, sfx="rim"),
        ], note="预告下一讲：管窥"),
        Shot(2, "专注的红利|也是有代价的", "原书 · 大意", [
            Big("代价", 540, 760, 160, at=0, sfx="kick", glow=True),
        ], text_beat=0, punch=0.03, shake=[0], note="代价二字砸下"),
        Shot(4, "其中一项实验|在大规模重复中没能复现", "常见质疑", [
            Icon("book", 400, 740, 180, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 720, 640, 110, color=K.RED, at=4, sfx="rim"),
        ], note="Camerer 2018 复现研究"),
        Shot(2, "试试：给大任务|自己定一个截止日", "小练习", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Fig(540, GROUND, 330, at=0, pose="cheer", mood="happy", hair="short"),
            Spark(540, 560, at=1, sfx="clap"),
        ], draw=A.ground, text_beat=0, punch=0.02, note="回报"),
        end_shot(REFS, "03 管窥：为什么一忙，连妈妈的消息都忘了回"),
    ]
    return episode(2, "focus", "专注红利", "为什么deadline前一晚，效率最高？", ACC, shots, REFS,
                   "为什么deadline前一晚|效率【最高】？",
                   ["「专注红利」（focus dividend）为《稀缺》第 1 章概念。熬夜赶 PPT 为情境演绎。",
                    "Shah, Mullainathan & Shafir (2012, Science)：游戏中资源少的玩家每次出手更认真。",
                    "Camerer 等 (2018) 大规模重复中该文一项实验未能复现。"])
