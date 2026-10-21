"""01 稀缺心态：为什么一着急，就丢三落四？"""

from adler import fx
from adler import kit as K
from adler.core import Big, Counter, Custom, Fig, Glow, Icon, Pops, Rays, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, episode

ACC = "#D9703A"
GROUND = A.GROUND_Y
REFS = [BOOK, "Radel & Clément-Guillotin (2012). Hunger modulates conscious access. Psychological Science."]


def _words(c, g, t, d):
    """一闪而过的两个词：饥饿的人眼里，食物词更亮。"""
    for x, word, food in ((-200, "面包", True), (200, "椅子", False)):
        on = (g.t * 1.4) % 1 < 0.5
        a = 1.0 if food else 0.35
        if food:
            fx.glow(c, x, 0, 230, g.acc2, 0.35 + 0.2 * g.pulse(5))
        K.card(c, x, 0, 300, 180, K.PAPER, 1, r=24)
        K.text(c, word, x, 0, 84 if on or food else 80, "serif_black", g.acc if food else K.INK3, a)


def build():
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("一着急|就 【丢三落四】？", 540, 760, 108, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "不是你记性差|看完你就知道为什么", "先说结论", [
            Fig(540, GROUND, 330, at=0, pose="shrug", mood="surprised", hair="bun", color=K.OTHER2),
            Icon("question", 760, 520, 110, color=ACC, at=1, sfx="rim"),
            Spark(760, 520, at=1),
        ], draw=A.ground, text_beat=0, note="摊手，问号弹出"),
        Shot(4, "8点52，快迟到了|抓起包就冲出门", "情境演绎", [
            Custom(A.clock_digital, x=540, y=470, at=0, enter="pop", t0=8 * 60 + 50, t1=8 * 60 + 58, b0=2, w=340, h=140),
            Fig(230, GROUND, 320, at=0, pose="stand", mood="worried", hair="bun", color=K.OTHER2,
                moves=[(4, dict(x=760, dur=1.6, pose="push", sfx="wood_low"))]),
            Icon("door", 900, 930, 260, color=ACC, at=0),
        ], draw=A.ground, hits=[(2, "wood_high", 0.7, "时钟开始跳")], note="时钟跳分钟，人冲向门口"),
        Shot(4, "时间一缺|脑子只装得下【赶时间】", "原书 · 核心概念", [
            Big("稀缺心态", 540, 700, 170, at=0, sfx="kick", sub="Scarcity Mindset", rays=True, glow=True, shine=True,
                spark=True, note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "到了公司才发现|工牌、充电器都没带", "情境演绎", [
            Custom(A.checklist, x=540, y=800, at=0, enter="pop", b0=2, step=2,
                   items=[("手机", True), ("钥匙", True), ("工牌", False), ("充电器", False)]),
        ], hits=[(2, "wood_high", 0.8, "手机 ✓"), (4, "wood_high", 0.8, "钥匙 ✓"), (6, "rim", 0.9, "工牌 ✗"),
                 (8, "rim", 0.9, "充电器 ✗")], note="出门清单逐项打勾打叉"),
        Shot(4, "", "一句话", [
            Glow(540, 780, 560, at=0, alpha=0.26),
            Pops("缺 什么|脑子 就 只剩 【什么】", 540, 780, 100, at=0, step=1),
        ], punch=0.02, flashes=[6], note="主题金句逐词弹出"),
        Shot(4, "饿肚子也一样|科学家真的测过", "研究证据 · Radel 2012", [
            Counter(0, 42, 540, 660, 220, at=0, land=4, sub="名大学生参与实验"),
            Icon("clock", 540, 960, 110, color=ACC, at=5, sfx="wood_high"),
        ], research=True, punch=0.02, note="二次钩子：数字落定"),
        Shot(4, "词只闪1/300秒|饿着的人看食物词更清楚", "研究证据 · Radel 2012", [
            Custom(_words, x=540, y=760, at=0, enter="pop", sfx="wood_low"),
        ], research=True, note="面包亮、椅子暗"),
        Shot(4, "注意力不是你选的|是被“缺的东西”抓走的", "原书 · 大意", [
            Icon("eye", 540, 720, 220, color=ACC, at=0, sfx="wood_low"),
            Icon("clock", 300, 980, 110, color=K.INK2, at=2, sfx="wood_high"),
            Icon("water", 540, 1000, 110, color=K.INK2, at=3, sfx="wood_high"),
            Icon("phone", 780, 980, 110, color=K.INK2, at=4, sfx="wood_high"),
        ], note="眼睛被各种“缺”抓走"),
        Shot(2, "缺时间、缺钱、缺吃的|大脑反应很像", "原书 · 大意", [
            Pops("时间 钱 【食物】", 540, 760, 100, at=0, step=1),
        ], text_beat=0, note="三种稀缺"),
        Shot(4, "这个实验只有42人|结论还需要更多验证", "常见质疑", [
            Icon("scale", 540, 720, 230, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 780, 560, 100, color=K.RED, at=4, sfx="rim"),
        ], note="样本量小，书中部分研究也有复现争议"),
        Shot(2, "试试：前一晚|把要带的放门口", "小练习", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Fig(540, GROUND, 330, at=0, pose="cheer", mood="happy", hair="bun", color=K.OTHER2),
            Custom(lambda c, g, t, d: A.badge(c, 0, 0, 150, ACC), x=780, y=640, at=1, enter="pop", sfx="clap"),
            Spark(780, 640, at=1),
        ], draw=A.ground, text_beat=0, punch=0.02, note="回报：一个能立刻用的小办法"),
        end_shot(REFS, "02 专注红利：为什么deadline前一晚效率最高"),
    ]
    return episode(1, "mindset", "稀缺心态", "为什么一着急，就丢三落四？", ACC, shots, REFS,
                   "为什么一着急|就【丢三落四】？",
                   ["「稀缺心态」：稀缺会俘获注意力（《稀缺》第 1 章）。出门忘带东西为情境演绎。",
                    "Radel & Clément-Guillotin (2012, Psychological Science)：42 名大学生，饥饿组对一闪而过的食物词感知更清楚、辨认更准。",
                    "样本量小；《稀缺》引用的部分研究存在复现争议。"])
