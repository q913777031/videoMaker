"""01 稀缺心态：为什么一着急，就丢三落四？

节奏要求：每个画面 3 秒内必有新动作（约每 4–6 拍一个事件），动画为主、字幕为辅；结论直接给，不在屏幕上做“待验证”式保留。
"""

import math

import skia

from adler import fx
from adler import kit as K
from adler.core import Big, Bubble, Counter, Custom, Fig, Glow, Icon, Label, Pops, Rays, Shot, Spark, end_shot
from engine.gfx import clamp01, ease_in, ease_out

from . import art as A
from .common import BOOK, episode

ACC = "#D9703A"
GROUND = A.GROUND_Y
REFS = [BOOK, "Radel & Clément-Guillotin (2012). Hunger modulates conscious access. Psychological Science.",
        "Keys et al. (1950). The Biology of Human Starvation."]


def charger(c, x, y, s, alpha=1.0, color=K.INK2):
    """充电头：方块 + 两根插脚 + 一段线。"""
    K.rr(c, x, y, s * 0.5, s * 0.5, s * 0.08, K.PAPER, alpha)
    K.rr_stroke(c, x, y, s * 0.5, s * 0.5, s * 0.08, color, s * 0.04, alpha)
    for dx in (-0.1, 0.1):
        K.rr(c, x + dx * s, y - s * 0.33, s * 0.05, s * 0.16, s * 0.02, color, alpha)
    K.seg(c, x, y + s * 0.25, x + s * 0.2, y + s * 0.5, color, s * 0.04, alpha)


def _item(c, name, x, y, s, alpha=1.0):
    if name == "badge":
        A.badge(c, x, y, s, ACC, alpha)
    elif name == "charger":
        charger(c, x, y, s, alpha)
    else:
        K.icon(c, name, x, y, s, K.INK2 if name != "key" else K.GOLD, alpha, 0.6, 0, 1, 1, K.GOLD)


def _flash_words(c, g, t, d):
    """一闪而过的词：每 2 拍闪一个；食物词闪完后亮着留在下排，其余词消失。"""
    words = d["words"]
    kept = []
    for i, (w, food) in enumerate(words):
        dt = g.since(2 * i)
        if dt < 0:
            continue
        if dt < 0.5:
            a = 1 - ease_in(clamp01((dt - 0.25) / 0.25))
            sc = 1.25 - 0.25 * ease_out(clamp01(dt / 0.15))
            with K.at(c, 0, -130, 0, sc):
                K.card(c, 0, 0, 380, 200, K.PAPER, a, r=26)
                K.text(c, w, 0, 0, 100, "serif_black", g.acc if food else K.INK3, a)
        if food:
            kept.append((w, dt))
    for j, (w, dt) in enumerate(kept):
        k = clamp01((dt - 0.3) / 0.3)
        if k <= 0:
            continue
        x = -260 + j * 260
        fx.glow(c, x, 170, 150, K.GOLD, 0.3 * k + 0.15 * g.pulse(5))
        with K.at(c, x, 170 + (1 - ease_out(k)) * -120, 0, 0.6 + 0.4 * ease_out(k)):
            fx.draw_word(c, w, 0, 0, 66, "serif_black", K.INK, g.acc, K.PAPER, k, True)


def _door_hooks(c, g, t, d):
    """门口挂钩：钥匙、工牌、充电器依次挂上（第 0、2、4 拍），第 6 拍打勾；第 8 拍起时钟提前 10 分钟。"""
    K.icon(c, "door", -260, 0, 380, ACC, 1, 0.8)
    K.rr(c, 170, -150, 360, 20, 10, "#94693C")
    for i, name in enumerate(("key", "badge", "charger")):
        x = 60 + i * 110
        K.seg(c, x, -150, x, -120, "#94693C", 8)
        k = clamp01(g.since(2 * i) / 0.3)
        if k > 0:
            y = -60 - (1 - ease_out(k)) * 260 + 6 * math.sin(g.t * 3 + i)
            _item(c, name, x, y, 110)
    k = clamp01(g.since(6) / 0.3)
    if k > 0:
        with K.at(c, 170, 110, 0, 0.5 + 0.5 * ease_out(k)):
            K.icon(c, "check", 0, 0, 120, K.GREEN, k, 0.5)


# ---------------------------------------------------------------- 开场互动小游戏：3 秒倒计时，桌上带走哪些？

def _wallet(c, x, y, s, a=1.0):
    K.rr(c, x, y, s, s * 0.7, s * 0.12, "#8C5A3C", a)
    K.rr(c, x + s * 0.3, y, s * 0.4, s * 0.3, s * 0.08, "#6E4329", a)
    K.dot(c, x + s * 0.35, y, s * 0.05, K.GOLD, a)


def _headphones(c, x, y, s, a=1.0):
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - s * 0.45, y - s * 0.5, s * 0.9, s * 0.9), 180, 180)
    c.drawPath(p, K.paint(K.INK, a, stroke=s * 0.08))
    for dx in (-0.45, 0.45):
        K.rr(c, x + dx * s, y + s * 0.02, s * 0.2, s * 0.34, s * 0.08, K.DARK, a)


def _cup(c, x, y, s, a=1.0):
    K.poly(c, [(x - s * 0.32, y - s * 0.4), (x + s * 0.32, y - s * 0.4), (x + s * 0.24, y + s * 0.4), (x - s * 0.24, y + s * 0.4)],
           "#F1E3C4", a)
    K.rr(c, x, y - s * 0.45, s * 0.74, s * 0.12, s * 0.05, "#5E4636", a)
    K.rr(c, x, y, s * 0.6, s * 0.18, s * 0.04, ACC, a)


def _lunchbox(c, x, y, s, a=1.0):
    K.rr(c, x, y + s * 0.05, s * 1.0, s * 0.5, s * 0.1, "#7FA34A", a)
    K.rr(c, x, y - s * 0.22, s * 1.04, s * 0.14, s * 0.06, "#5E8C3A", a)


def _umbrella(c, x, y, s, a=1.0):
    with K.at(c, x, y, -70):
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(-s * 0.5, -s * 0.45, s, s * 0.9), 180, 180)
        p.close()
        c.drawPath(p, K.paint("#5E8FA8", a))
        K.seg(c, 0, 0, 0, s * 0.5, K.INK, s * 0.05, a)


DESK = [  # (名称, x, y, 尺寸, 被拿走的拍)：x/y 相对桌面中心；工牌小、先画、半藏在杯子后面，不被拿走
    ("badge", 140, 60, 54, None), ("phone", -330, -70, 120, 8), ("key", -170, -40, 90, 9), ("wallet", -10, -45, 120, 10),
    ("headphones", 170, -60, 120, 11), ("umbrella", 330, -50, 150, 12), ("lunchbox", -250, 70, 120, 13),
    ("cup", 100, 60, 120, 14),
]


def _desk_item(c, name, x, y, s, a=1.0):
    if name == "wallet":
        _wallet(c, x, y, s, a)
    elif name == "headphones":
        _headphones(c, x, y, s, a)
    elif name == "cup":
        _cup(c, x, y, s, a)
    elif name == "lunchbox":
        _lunchbox(c, x, y, s, a)
    elif name == "umbrella":
        _umbrella(c, x, y, s, a)
    elif name == "badge":
        A.badge(c, x, y, s, ACC, a)
    else:
        K.icon(c, name, x, y, s, K.INK2 if name != "key" else K.GOLD, a, 0.6, 0, 1, 1, K.GOLD)


def _desk(c, g, t, d):
    """桌面：mode=show 时物品依次落到桌上；take 时“时间到”后逐个飞走，只剩工牌；
    focus 时只剩工牌，聚光放大并画问号圈。"""
    mode = d["mode"]
    c.save()
    c.scale(1.15, 1.15)
    K.rr(c, 0, 150, 900, 28, 10, "#B98A55")
    K.rr(c, 0, 0, 900, 300, 26, "#E7D3B0")
    K.rr_stroke(c, 0, 0, 900, 300, 26, "#C9A46A", 6)
    for i, (name, x, y, s, take) in enumerate(DESK):
        if mode == "focus" and name != "badge":
            continue
        dx = dy = 0.0
        a = 1.0
        sc = 1.0
        if mode == "show":
            k = clamp01(g.since(1 + i * 0.7) / 0.3)
            if k <= 0:
                continue
            dy = -(1 - ease_out(k)) * 300
            a = k
        elif mode == "take" and take is not None:
            k = clamp01(g.since(take) / 0.45)
            if k >= 1:
                continue
            dy = -ease_in(k) * 700
            dx = (x / 300) * ease_in(k) * 200
            a = 1 - k
        if mode == "focus":
            k = ease_out(clamp01(g.since(0) / 0.6))
            fx.glow(c, x, y, 160 + 120 * k, K.GOLD, 0.35 + 0.2 * g.pulse(5))
            sc = 1 + 1.6 * k
            dx, dy = -x * k, (-y - 30) * k
        with K.at(c, x + dx, y + dy, 0, sc):
            _desk_item(c, name, 0, 0, s, a)
    if mode == "focus":
        k = clamp01(g.since(2) / 0.4)
        if k > 0:
            K.ring(c, 0, -30, 150 * (1.3 - 0.3 * ease_out(k)), K.RED, 8, k)
    c.restore()


def _countdown(c, g, t, d):
    """倒计时：3、2、1 各占 2 拍（约 3 秒），外圈随真实时间收缩；第 6 拍“时间到！”。"""
    b_end = 6
    if g.since(b_end) >= 0:
        dt = g.since(b_end)
        sc = 1 + 0.5 * (1 - ease_out(clamp01(dt / 0.2)))
        with K.at(c, 0, 0, -4, sc):
            K.rr(c, 0, 0, 440, 140, 70, K.RED)
            K.text(c, "时间到！", 0, 0, 80, "serif_black", K.PAPER)
        return
    n = 3 - int(max(0, min(2, g.since(0) // max(1e-6, g.b(2) - g.b(0)))))
    k = clamp01(g.since(0) / max(1e-6, g.b(b_end) - g.b(0)))
    K.dot(c, 0, 0, 92, K.PAPER)
    K.ring(c, 0, 0, 92, K.LINE, 14)
    K.ring(c, 0, 0, 92, K.RED if n == 1 else ACC, 14, 1, 1 - k)
    beat_dt = g.since(2 * (3 - n))
    sc = 1 + 0.35 * (1 - ease_out(clamp01(beat_dt / 0.18)))
    with K.at(c, 0, 0, 0, sc):
        K.text(c, str(n), 0, 0, 120, "black", K.RED if n == 1 else K.INK)


def build():
    shots = [
        # 0–4 秒：互动小游戏开场——你要迟到了，出门带什么？桌上物品依次落下
        Shot(2, "", "互动小游戏", [
            Pops("你 要 迟到 了！|出门 带 【什么】？", 540, 560, 92, at=0, step=1),
            Custom(_desk, x=540, y=1000, at=0, enter="none", mode="show"),
        ], hits=[(0, "kick", 0.7, "开场")], punch=0.025, flashes=[0], note="钩子：抛出问题，桌上东西依次落下"),
        # 4–13 秒：倒计时 3 秒，时间到！东西被一件件拿走，只剩一个不起眼的小工牌
        Shot(4, "倒计时3秒|记住你要带走的东西", "互动小游戏", [
            Custom(_countdown, x=540, y=560, at=0, enter="none"),
            Custom(_desk, x=540, y=1000, at=0, enter="none", mode="take"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (8, "shaker", 0.7, "拿走手机"), (10, "shaker", 0.7, "拿走钱包"), (12, "shaker", 0.7, "拿走雨伞"),
                 (14, "shaker", 0.7, "拿走水杯")], flashes=[6], shake=[(6, 12.0)], punch=0.025,
            note="倒计时、时间到、物品逐个飞走"),
        # 13–17 秒：聚光到工牌——你带了吗？
        Shot(2, "漏了的别慌|看完教你两招", "互动小游戏", [
            Custom(_desk, x=540, y=1000, at=0, enter="none", mode="focus"),
            Pops("工牌 你 【带了吗】？", 540, 560, 96, at=1, step=1),
        ], hits=[(0, "ding", 0.8, "聚光工牌")], text_beat=0, note="只剩工牌，放大追问"),
        Shot(4, "缺什么|脑子就被什么【占满】", "原书 · 核心概念", [
            Big("稀缺心态", 540, 600, 170, at=0, sfx="kick", sub="Scarcity Mindset", rays=True, glow=True, shine=True,
                spark=True, note="概念落版（音乐 drop）"),
            Spark(540, 600, at=3, sfx="wood_high"),
            Pops("缺时间 缺钱 缺吃的", 540, 1000, 64, at=6, step=2, gap=30),
        ], punch=0.035, flashes=[0], shake=[0], note="drop：概念砸下，三种稀缺弹出"),
        # 机制 1：隧道收窄，隧道外的东西逐个被打叉
        Shot(4, "注意力全被“赶时间”吸走|隧道外的小事就漏了", "机制示意", [
            Icon("clock", 540, 780, 180, color=K.RED, at=0, enter="none"),
            Custom(lambda c, g, t, d: _item(c, "key", 0, 0, 130), x=250, y=540, at=0, enter="none"),
            Custom(lambda c, g, t, d: A.badge(c, 0, 0, 130, ACC), x=830, y=540, at=0, enter="none"),
            Custom(lambda c, g, t, d: charger(c, 0, 0, 150), x=250, y=1040, at=0, enter="none"),
            Icon("water", 830, 1040, 120, color=K.INK2, at=0, enter="none"),
            Custom(A.tunnel, x=540, y=780, at=0, enter="fade", r0=900, r=220, close=1.6),
            Icon("cross", 325, 465, 90, color=K.RED, at=4, sfx="rim"), Spark(250, 540, at=4, colors=[K.RED, K.GOLD]),
            Icon("cross", 905, 465, 90, color=K.RED, at=6, sfx="rim"), Spark(830, 540, at=6, colors=[K.RED, K.GOLD]),
            Icon("cross", 325, 965, 90, color=K.RED, at=8, sfx="rim"), Spark(250, 1040, at=8, colors=[K.RED, K.GOLD]),
            Icon("cross", 905, 965, 90, color=K.RED, at=10, sfx="rim"), Spark(830, 1040, at=10, colors=[K.RED, K.GOLD]),
            Label("钥匙", 250, 650, 40, at=4, fill=K.RED), Label("工牌", 830, 650, 40, at=6, fill=K.RED),
            Label("充电器", 250, 1150, 40, at=8, fill=K.RED), Label("水杯", 830, 1150, 40, at=10, fill=K.RED),
            Label("全漏了", 540, 1150, 52, at=13, fill=K.RED, sfx="kick"),
        ], hits=[(0, "tom", 0.7, "隧道收窄")], shake=[(13, 10.0)], note="隧道视野：外面的东西一个个被漏掉"),
        # 机制 2：带宽被一块块占满，最后冒出“钥匙？”
        Shot(4, "脑子的带宽被占满|就没空记钥匙了", "机制示意", [
            Custom(A.meter, x=540, y=760, at=0, enter="pop", eat=[(2, 0.3, "迟到"), (6, 0.25, "老板"), (10, 0.27, "地铁")]),
            Label("钥匙？", 540, 1010, 48, at=13, fill=K.RED, sfx="rim"),
        ], hits=[(2, "wood_low", 0.8, "被占：迟到"), (6, "wood_low", 0.8, "被占：老板"), (10, "rim", 0.9, "被占：地铁")],
            note="带宽条被一块块占满（示意）"),
        # 二次钩子：科学家真的测过
        Shot(4, "科学家真的测过：|让一群人饿着肚子看屏幕", "研究证据 · Radel 2012", [
            Counter(0, 42, 540, 560, 200, at=0, land=4, sub="名大学生"),
            Fig(300, GROUND, 290, at=6, pose="sad", mood="worried", hair="short", sfx="wood_low"),
            Bubble("好饿…", 470, 830, 42, at=8, think=True, sfx="wood_high"),
            Icon("phone", 760, 900, 150, color=K.INK2, at=10, sfx="wood_high"),
            Spark(760, 900, at=10),
        ], draw=A.ground, research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定，饿着的人看屏幕"),
        Shot(4, "词只闪1/300秒|饿着的人，一眼就看见食物", "研究证据 · Radel 2012", [
            Custom(_flash_words, x=540, y=760, at=0, enter="none",
                   words=[("椅子", False), ("面包", True), ("台灯", False), ("蛋糕", True), ("雨伞", False), ("牛奶", True)]),
        ], hits=[(0, "wood_low", 0.7, "椅子"), (2, "ding", 0.8, "面包"), (4, "wood_low", 0.7, "台灯"), (6, "ding", 0.8, "蛋糕"),
                 (8, "wood_low", 0.7, "雨伞"), (10, "ding", 0.9, "牛奶")], research=True, note="词一闪而过，食物词被留下"),
        Shot(4, "长期挨饿的志愿者|满脑子只剩下吃", "研究证据 · 明尼苏达饥饿实验", [
            Counter(0, 36, 540, 540, 200, at=0, land=4, sub="名志愿者长期节食"),
            Pops("面包 牛排 蛋糕 【食谱】", 540, 960, 64, at=6, step=2, gap=22),
        ], research=True, note="数字落定，食物词逐个冒出"),
        Shot(2, "缺什么|注意力就被什么劫持", "原书 · 大意", [
            Big("劫持", 540, 640, 200, at=0, sfx="kick", glow=True, spark=True),
            Pops("你 的 【注意力】", 540, 1000, 80, at=3, step=1),
        ], text_beat=0, punch=0.03, shake=[0], note="劫持二字砸下"),
        # 回报：两招
        Shot(4, "第一招：东西挂门口|出门提前十分钟", "小方法", [
            Custom(_door_hooks, x=540, y=760, at=0, enter="none"),
            Custom(A.clock_digital, x=540, y=1080, at=8, enter="pop", t0=8 * 60 + 40, t1=8 * 60 + 40, b0=8, w=300, h=110,
                   label=""),
            Label("提前 10 分钟", 820, 1080, 40, at=12, fill=K.GREEN, sfx="ding"),
        ], hits=[(0, "wood_high", 0.8, "挂钥匙"), (2, "wood_high", 0.8, "挂工牌"), (4, "wood_high", 0.8, "挂充电器"),
                 (6, "ding", 0.8, "打勾"), (8, "wood_low", 0.7, "时钟")], note="门口挂钩 + 提前出门"),
        Shot(2, "第二招：出门默念|身份证手机钥匙钱", "小方法", [
            Rays(540, 760, 520, at=0, alpha=0.2),
            Pops("身 手 钥 【钱】", 540, 760, 140, at=0, step=1, gap=36),
            Spark(540, 760, at=5, sfx="clap"),
        ], text_beat=0, punch=0.025, note="伸手要钥钱"),
        end_shot(REFS, "02 专注红利：为什么deadline前一晚效率最高"),
    ]
    return episode(1, "mindset", "稀缺心态", "为什么一着急，就丢三落四？", ACC, shots, REFS,
                   "为什么一着急|就【丢三落四】？",
                   ["“稀缺俘获注意力”出自《稀缺》第 1 章。出门忘带东西、挂钩与默念口诀为情境与生活方法。",
                    "Radel & Clément-Guillotin (2012)：42 名大学生，饥饿组对一闪而过（约 1/300 秒）的食物词感知更清楚。",
                    "明尼苏达饥饿实验（Keys 等，1944–45）：36 名志愿者长期半饥饿，思维被食物占据。"])
