"""03 管窥：为什么一忙起来，连妈妈的消息都忘了回？（重做版）"""

from adler import kit as K
from adler.core import Bubble, Card, Counter, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot
from engine.gfx import clamp01, ease_in_out

from . import art as A
from .common import BOOK, ask, drop, episode, slam, tip2

ACC = "#2F8F8A"
GROUND = A.GROUND_Y
REFS = [BOOK, "Simons & Chabris (1999). Gorillas in our midst. Perception."]

PASS_X = (200, 420, 660, 880)


def _passing(c, g, t, d):
    """传球：四个人站成一排，白衣两人之间来回传球（每拍一次），右上角计数。"""
    for i, x in enumerate(PASS_X):
        K.figure(c, x, 0, 260, "point" if i % 2 == 0 else "reach", K.PAPER if i % 2 == 0 else K.DARK,
                 face=1 if i < 2 else -1, mood="calm", hair=("short", "bun", "long", "short")[i], lift=0.8)
    span = max(1e-6, g.b(1) - g.b(0))
    n = max(0, int(g.since(0) // span))
    k = clamp01((g.since(0) - n * span) / span)
    a, b = (PASS_X[0], PASS_X[2]) if n % 2 == 0 else (PASS_X[2], PASS_X[0])
    x = a + (b - a) * ease_in_out(k)
    y = -200 - 120 * 4 * k * (1 - k)
    K.dot(c, x, y, 22, K.GOLD)
    if d.get("count", True):
        K.rr(c, 330, -460, 220, 90, 45, ACC)
        K.text(c, f"传球 {n}", 330, -460, 46, "black", K.PAPER)


def build():
    shots = [
        ask("盯住 中间 的 倒计时|【别眨眼】！", [
            Custom(A.countdown, x=540, y=860, at=0, enter="none", b0=99, r=150),
            Icon("eye", 540, 860, 200, color=ACC, at=2, sfx="wood_low"),
        ], note="互动：盯住倒计时"),
        Shot(4, "", "互动小游戏", [
            Custom(A.countdown, x=540, y=760, at=0, enter="none", r=150),
            Custom(A.toasts, x=0, y=0, at=0, enter="none", hold=4,
                   items=[(1, 280, 420, "妈妈：周末回家吗？"), (3, 800, 1080, "快递已到驿站"), (5, 300, 1180, "体检预约提醒")]),
            Pops("刚才 妈妈 问了 【什么】？", 540, 1100, 70, at=9, step=1),
        ], hits=[(0, "wood_high", 0.9, "3"), (1, "pop", 0.6, "通知"), (2, "wood_high", 0.9, "2"), (3, "pop", 0.6, "通知"),
                 (4, "rim", 1.0, "1"), (5, "pop", 0.6, "通知"), (6, "kick", 0.9, "时间到")], flashes=[6], shake=[(6, 12.0)],
            punch=0.025, note="盯着倒计时时，边上弹出三条通知；时间到后追问"),
        Shot(2, "没注意到？|这就是今天要讲的", "互动小游戏", [
            Card("妈妈：周末回家吗？", 540, 760, 56, at=0, sfx="ding"),
            Spark(540, 760, at=0),
            Icon("cross", 860, 640, 100, color=K.RED, at=3, sfx="rim"),
        ], text_beat=0, note="揭晓：妈妈的消息被漏掉"),
        drop("管窥", "Tunneling", "缺时间时|你只看得见【隧道】里的事", "急事 截止日 绩效", size=220),
        Shot(4, "隧道外的家人、健康|全被挡在外面", "机制示意", [
            Icon("heart", 250, 540, 120, color=K.RED, at=0, enter="none"),
            Icon("house", 830, 540, 120, color=K.INK2, at=0, enter="none"),
            Icon("friends", 250, 1040, 120, color=K.INK2, at=0, enter="none"),
            Icon("sun", 830, 1040, 120, color=K.GOLD, at=0, enter="none"),
            Icon("clock", 540, 780, 180, color=K.RED, at=0, enter="none"),
            Custom(A.tunnel, x=540, y=780, at=0, enter="fade", r0=900, r=220, close=1.6),
            Label("健康", 250, 650, 40, at=4, fill=K.RED, sfx="rim"), Label("家", 830, 650, 40, at=6, fill=K.RED, sfx="rim"),
            Label("朋友", 250, 1150, 40, at=8, fill=K.RED, sfx="rim"), Label("休息", 830, 1150, 40, at=10, fill=K.RED, sfx="rim"),
            Label("全被挡在外面", 540, 1215, 46, at=13, fill=K.RED, sfx="kick"),
        ], hits=[(0, "tom", 0.7, "隧道收窄")], note="隧道外的东西逐个被点名"),
        Shot(4, "赶项目的一周|妈妈的消息一条没回", "情境演绎", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="妈妈",
                   msgs=[(1, "吃饭了吗？"), (4, "周末回家吗？"), (7, "体检约了没？"), (10, "怎么不回消息")]),
            Label("已读未回", 540, 1240, 40, at=13, fill=K.INK2, sfx="rim"),
        ], hits=[(1, "wood_high", 0.8, "消息"), (4, "wood_high", 0.8, "消息"), (7, "wood_high", 0.8, "消息"),
                 (10, "rim", 0.9, "消息")], note="消息一条条弹出"),
        Shot(4, "科学家做过实验：|数清白衣队传了几次球", "研究证据 · Simons & Chabris 1999", [
            Custom(_passing, x=0, y=GROUND, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.6, "传球"), (2, "wood_high", 0.6, "传球"), (4, "wood_high", 0.6, "传球"),
                 (6, "wood_high", 0.6, "传球"), (8, "wood_high", 0.6, "传球"), (10, "wood_high", 0.6, "传球"),
                 (12, "wood_high", 0.6, "传球"), (14, "wood_high", 0.6, "传球")],
            draw=A.ground, research=True, punch=0.02, note="二次钩子：传球实验"),
        Shot(4, "一只“大猩猩”走过场中|约一半的人没看见", "研究证据 · Simons & Chabris 1999", [
            Custom(_passing, x=0, y=GROUND, at=0, enter="none", count=False),
            Fig(-120, GROUND, 330, at=0, enter="none", color="#3B3B3B", head_color="#4A4A4A", mood="happy", hair=None,
                moves=[(1, dict(x=1200, dur=6.0, ease="io", sfx="tom"))]),
            Counter(0, 50, 540, 520, 160, at=6, land=10, suffix="%", sub="的人没看见"),
        ], draw=A.ground, research=True, note="黑影走过，一半人没看见"),
        Shot(4, "注意力有一条隧道|隧道外的东西就像不存在", "原书 · 大意", [
            Icon("eye", 540, 780, 160, color=ACC, at=0, enter="none"),
            Custom(A.tunnel, x=540, y=780, at=0, enter="fade", r0=500, r=140, close=2.4, dark=0.85),
            Label("看不见", 540, 1100, 46, at=6, fill=K.RED, sfx="rim"),
            Spark(540, 780, at=10, sfx="ding"),
        ], hits=[(0, "tom", 0.7, "隧道收窄")], note="隧道收窄"),
        slam("隧道", "缺得 越狠|隧道 越 【窄】", "所以忘了回消息|不等于你不爱"),
        Shot(4, "第一招：重要的人和事|设成固定提醒", "小方法", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="每周提醒", unread=False,
                   msgs=[(2, "周日：给妈打电话"), (5, "周三：去体检"), (8, "周五：约朋友吃饭")]),
            Icon("check", 820, 1150, 110, color=K.GREEN, at=11, sfx="ding"),
        ], hits=[(2, "ding", 0.8, "提醒"), (5, "ding", 0.8, "提醒"), (8, "ding", 0.8, "提醒")], note="固定提醒"),
        tip2("第二招：收工前|抬头看看隧道外", "吃了 睡够 【家人】", 100),
        end_shot(REFS, "04 带宽税：为什么一有心事，就容易犯低级错误"),
    ]
    return episode(3, "tunneling", "管窥", "为什么一忙起来，连妈妈的消息都忘了回？", ACC, shots, REFS,
                   "一忙起来|连妈妈的消息都【忘了回】？",
                   ["“管窥”出自《稀缺》第 1 章；盯倒计时小游戏、忘回消息为情境演绎，提醒与收工自查为方法建议。",
                    "Simons & Chabris (1999)：观看者专心数白衣队传球时，约一半没有注意到穿大猩猩服装走过的人。"])
