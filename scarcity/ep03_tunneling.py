"""03 管窥：为什么一忙起来，连妈妈的消息都忘了回？"""

from adler import kit as K
from adler.core import Big, Bubble, Counter, Custom, Fig, Glow, Icon, Pops, Rays, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, episode

ACC = "#2F8F8A"
GROUND = A.GROUND_Y
REFS = [BOOK, "Keys et al. (1950). The Biology of Human Starvation（明尼苏达饥饿实验）."]


def build():
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("一忙 起来|连 饭 都 【忘了吃】？", 540, 760, 100, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "你不是不在乎|是被“隧道”挡住了", "先说结论", [
            Fig(540, GROUND, 330, at=0, pose="sad", mood="sad", hair="short", color=K.OTHER3),
            Icon("heart", 760, 520, 110, color=K.RED, at=1, sfx="rim"),
            Spark(760, 520, at=1),
        ], draw=A.ground, text_beat=0, note="心弹出"),
        Shot(4, "赶项目的一周|妈妈的消息一条没回", "情境演绎", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="妈妈",
                   msgs=[(2, "吃饭了吗？"), (5, "周末回家吗？"), (8, "体检约了没？"), (11, "怎么不回消息")]),
        ], hits=[(2, "wood_high", 0.8, "消息 1"), (5, "wood_high", 0.8, "消息 2"), (8, "wood_high", 0.8, "消息 3"),
                 (11, "rim", 0.9, "消息 4")], note="妈妈的消息一条条弹出，未读数增加"),
        Shot(4, "缺时间时|你只看得见【隧道】里的事", "原书 · 核心概念", [
            Big("管窥", 540, 700, 220, at=0, sfx="kick", sub="Tunneling", rays=True, glow=True, shine=True, spark=True,
                note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下"),
        Shot(4, "隧道外的事|全都被自动忽略", "机制示意", [
            Icon("heart", 250, 520, 120, color=K.RED, at=0),
            Icon("house", 830, 520, 120, color=K.INK2, at=0),
            Icon("friends", 250, 1050, 120, color=K.INK2, at=0),
            Icon("sun", 830, 1050, 120, color=K.GOLD, at=0),
            Icon("clock", 540, 780, 180, color=K.RED, at=0, enter="none"),
            Custom(A.tunnel, x=540, y=780, at=1, enter="fade", r0=900, r=230, close=1.6, sfx="tom"),
        ], note="四周压暗成隧道，只剩截止时钟"),
        Shot(4, "", "一句话", [
            Pops("忘了 吃饭|忘了 回消息|忘了 【体检】", 540, 780, 92, at=0, step=1, gap=30),
        ], punch=0.02, flashes=[6], note="被忽略的事逐词弹出"),
        Shot(4, "最极端的例子|是二战末的一场饥饿实验", "研究证据 · 明尼苏达饥饿实验", [
            Counter(0, 36, 540, 660, 220, at=0, land=4, sub="名志愿者长期节食"),
        ], research=True, punch=0.02, note="二次钩子：数字落定"),
        Shot(4, "一位参与者回忆：|食物成了生活唯一的中心", "研究证据 · 明尼苏达饥饿实验", [
            Fig(330, GROUND, 300, at=0, pose="think", mood="worried", hair="short", color=K.OTHER3),
            Bubble("满脑子|都是吃的", 720, 640, 50, at=2, think=True, sfx="wood_low"),
        ], draw=A.ground, research=True, note="想的全是食物"),
        Shot(4, "缺得越狠|隧道就越窄", "原书 · 大意", [
            Custom(A.tunnel, x=540, y=780, at=0, enter="fade", r0=320, r=120, close=2.4, dark=0.85),
            Icon("water", 540, 780, 130, color=ACC, at=0, enter="none"),
        ], hits=[(0, "tom", 0.7, "隧道收窄")], note="隧道继续收窄"),
        Shot(2, "所以忘了回消息|不等于你不爱", "原书 · 大意", [
            Icon("heart", 540, 760, 220, color=K.RED, at=0, sfx="ding"),
            Spark(540, 760, at=0),
        ], text_beat=0, note="心"),
        Shot(4, "这是极端实验|日常的忙没那么严重", "常见质疑", [
            Icon("scale", 540, 720, 230, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 780, 560, 100, color=K.RED, at=4, sfx="rim"),
        ], note="外推有边界"),
        Shot(2, "试试：把重要的人|设成每周提醒", "小练习", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Icon("phone", 540, 720, 200, color=ACC, at=0),
            Spark(540, 720, at=1, sfx="clap"),
        ], text_beat=0, punch=0.02, note="回报"),
        end_shot(REFS, "04 带宽税：为什么一有心事，就容易犯低级错误"),
    ]
    return episode(3, "tunneling", "管窥", "为什么一忙起来，连妈妈的消息都忘了回？", ACC, shots, REFS,
                   "一忙起来|连妈妈的消息都【忘了回】？",
                   ["「管窥」（tunneling）为《稀缺》第 1 章概念。忘回妈妈消息为情境演绎。",
                    "明尼苏达饥饿实验（1944–45，Keys 等）：36 名志愿者长期半饥饿，食物占据了他们的思维；《稀缺》以此说明稀缺对注意力的俘获。",
                    "极端饥饿与日常忙碌程度不同，外推需谨慎。"])
