"""02 专注红利：为什么 deadline 前一晚，效率最高？（重做版：互动开场、每 3 秒一变、结论直给）"""

import math

from adler import kit as K
from adler.core import Arrow, Card, Custom, Fig, Glow, Icon, Label, Pops, Shot, Spark, end_shot
from engine.gfx import clamp01, ease_out

from . import art as A
from .common import BOOK, ask, drop, episode, slam, tip2

ACC = "#3A6EA5"
GROUND = A.GROUND_Y
REFS = [BOOK, "Shah, Mullainathan & Shafir (2012). Some consequences of having too little. Science."]


def _darts(c, g, t, d):
    """飞镖：第 0、3、6、9 拍各飞出一支，命中靶心附近并闪光。"""
    K.icon(c, "target", 0, 0, 300, ACC, 1, 0.8, 0, 1, 1, K.GOLD)
    for i, b in enumerate((0, 3, 6, 9)):
        k = clamp01(g.since(b) / 0.3)
        if k <= 0:
            continue
        ang = -0.6 + i * 0.4
        ex, ey = 18 * math.cos(ang * 3), 18 * math.sin(ang * 3)
        sx, sy = -520, -260 + i * 150
        x, y = sx + (ex - sx) * ease_out(k), sy + (ey - sy) * ease_out(k)
        K.seg(c, x - 90, y, x, y, K.INK, 10)
        K.poly(c, [(x + 22, y), (x - 4, y - 12), (x - 4, y + 12)], K.RED)
        if k >= 1:
            K.ripple(c, ex, ey, g.since(b) - 0.3, K.GOLD, 120, 6)


def build():
    shots = [
        ask("3秒内|找到 【红色闹钟】！", [
            Custom(A.find_grid, x=540, y=930, at=0, enter="none", b0=1, target=(3, 2), odd=(0, 3)),
        ], note="互动：找红色闹钟"),
        Shot(4, "倒计时3秒|找到了吗？", "互动小游戏", [
            Custom(A.countdown, x=540, y=430, at=0, enter="none"),
            Custom(A.find_grid, x=540, y=930, at=0, enter="none", b0=-9, target=(3, 2), odd=(0, 3), found=7, odd_at=11),
            Label("找到了！", 540, 1240, 44, at=7, fill=K.GREEN),
            Label("那这个礼物盒呢？", 540, 1240, 44, at=11, fill=K.RED),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (7, "ding", 0.9, "找到红闹钟"), (11, "rim", 0.9, "礼物盒")], flashes=[6], shake=[(6, 12.0)], punch=0.025,
            note="倒计时、找到、追问礼物盒"),
        Shot(2, "盯住一件事很快|别的就看不见了", "互动小游戏", [
            Pops("越 赶|越 【专注】", 540, 760, 120, at=0, step=1),
            Spark(540, 760, at=4, sfx="ding"),
        ], text_beat=0, note="揭晓"),
        drop("专注红利", "Focus Dividend", "缺时间时|注意力会自动【聚焦】", "deadline 考试前夜 抢票"),
        Shot(4, "截止前一晚|你一口气写完了PPT", "情境演绎", [
            Fig(170, GROUND, 300, at=0, pose="sit", mood="open", hair="short"),
            Custom(A.laptop, x=660, y=800, at=0, enter="pop", w=480, p0=0.05, p1=1.0, b0=0, b1=12, title="汇报.pptx"),
            Label("灵感来了", 660, 520, 40, at=4, fill=ACC),
            Label("越写越快", 660, 520, 40, at=8, fill=ACC),
            Label("搞定！", 660, 520, 48, at=12, fill=K.GREEN),
        ], draw=A.ground, hits=[(0, "wood_low", 0.7, "开始写"), (4, "wood_high", 0.7, "灵感"), (8, "wood_high", 0.7, "加速"),
                                 (12, "ding", 0.9, "完成")], note="进度条一路冲到 100%"),
        Shot(4, "杂念被挤出去|只剩眼前这件事", "机制示意", [
            Icon("target", 540, 780, 220, color=ACC, at=0, sfx="wood_low"),
            Icon("phone", 150, 450, 110, color=K.INK2, at=1), Icon("friends", 930, 450, 110, color=K.INK2, at=3),
            Icon("cloud", 150, 1110, 110, color=K.INK2, at=5), Icon("gift", 930, 1110, 110, color=K.INK2, at=7),
            Arrow((180, 480), (430, 690), at=2, color=K.INK2, sfx="wood_high"),
            Arrow((900, 480), (650, 690), at=4, color=K.INK2, sfx="wood_high"),
            Arrow((180, 1080), (430, 870), at=6, color=K.INK2, sfx="wood_high"),
            Arrow((900, 1080), (650, 870), at=8, color=K.INK2, sfx="wood_high"),
            Spark(540, 780, at=10, sfx="rim"),
            Label("只剩这一件", 540, 1150, 44, at=12, fill=ACC, sfx="ding"),
        ], note="注意力收向靶心"),
        Shot(4, "科学家用游戏测过：|给一组人很少的机会", "研究证据 · Shah 等 2012", [
            Fig(300, GROUND, 300, at=0, pose="point", mood="open", hair="short"),
            Card("机会：很少", 760, 560, 50, at=2, rot=-3, sfx="wood_low"),
            Icon("target", 760, 860, 170, color=ACC, at=4, sfx="rim"),
            Spark(760, 860, at=8, sfx="wood_high"),
            Label("每次都很认真", 760, 1080, 40, at=11, fill=ACC, sfx="ding"),
        ], draw=A.ground, research=True, punch=0.02, flashes=[4], note="二次钩子：游戏实验"),
        Shot(4, "机会少的玩家|每一次都瞄得更准", "研究证据 · Shah 等 2012", [
            Custom(_darts, x=600, y=780, at=0, enter="none"),
            Spark(618, 780, at=0), Spark(618, 780, at=3), Spark(618, 780, at=6), Spark(618, 780, at=9),
            Label("4 / 4 命中", 600, 1080, 48, at=12, fill=K.GREEN, sfx="ding"),
        ], hits=[(0, "rim", 0.8, "命中"), (3, "rim", 0.8, "命中"), (6, "rim", 0.8, "命中"), (9, "ding", 0.9, "命中")],
            research=True, note="飞镖接连命中"),
        Shot(4, "缺，反而逼出了效率|这就是专注红利", "原书 · 大意", [
            Icon("clock", 300, 760, 170, color=K.RED, at=0, sfx="wood_low"),
            Arrow((420, 760), (650, 760), at=3, color=ACC, sfx="wood_high"),
            Icon("bulb", 780, 760, 190, color=K.GOLD, at=6, sfx="ding"),
            Spark(780, 760, at=6),
            Label("效率", 780, 960, 48, at=10, fill=ACC, sfx="rim"),
        ], note="时间压力 → 效率"),
        slam("红利", "缺 也 是 【燃料】", "用好它|而不是被它推着走"),
        Shot(4, "第一招：大任务拆小|每块定一个截止时间", "小方法", [
            Custom(A.checklist, x=540, y=800, at=0, enter="pop", b0=2, step=3, title="汇报拆成 4 块",
                   items=[("周一：列提纲", True), ("周二：找数据", True), ("周三：做图表", True), ("周四：彩排", True)]),
        ], hits=[(0, "wood_low", 0.7, "清单"), (2, "wood_high", 0.8, "✓"), (5, "wood_high", 0.8, "✓"), (8, "wood_high", 0.8, "✓"),
                 (11, "ding", 0.9, "✓")], note="大任务拆成带截止日的小块"),
        tip2("第二招：番茄钟|一次只做一件事", "25分钟|只做 【一件事】", 110),
        end_shot(REFS, "03 管窥：为什么一忙，连妈妈的消息都忘了回"),
    ]
    return episode(2, "focus", "专注红利", "为什么deadline前一晚，效率最高？", ACC, shots, REFS,
                   "为什么deadline前一晚|效率【最高】？",
                   ["“专注红利”出自《稀缺》第 1 章；找闹钟小游戏、赶 PPT 为情境演绎，拆分任务与番茄钟为方法建议。",
                    "Shah, Mullainathan & Shafir (2012, Science)：游戏中资源少的玩家每次出手更认真。"])
