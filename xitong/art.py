"""《系统之美》01 的专用元件：弹簧玩具、系统三要素图（要素·连接·目标）、换人的工位、墙上标语。坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_out, lerp
from maoxuan.art import DESK, RED  # noqa: F401
from scarcity.art import GROUND_Y, ground  # noqa: F401
from zizhi.art import pit, stack, thing  # noqa: F401

TEAL = "#3E7A7A"


# ---------------------------------------------------------------- 弹簧玩具

def slinky(c, g, el_t, d):
    """弹簧玩具：一只手提着弹簧顶端；drop 拍手移开，弹簧按自身结构上下振荡（衰减），说明行为来自结构。"""
    drop = d.get("drop")
    dt = g.since(drop) if drop is not None else -1
    hand_y = -320
    if dt >= 0:
        hand_y -= 220 * ease_out(clamp01(dt / 0.35))
    top = -300
    length = 360
    if dt >= 0:
        length = 360 + 160 * math.sin(dt * 7.5) * math.exp(-dt * 1.2)
    n = 22
    col = d.get("color", TEAL)
    for i in range(n):
        y = top + length * i / (n - 1)
        w = 150 + 10 * math.sin(i)
        c.drawOval(skia.Rect.MakeXYWH(-w / 2, y - 14, w, 28), K.paint(K.shade(col, 0.1 * (i % 2)), 0.95, 9))
    if dt < 0.5:
        a = 1 - clamp01(dt / 0.5) if dt >= 0 else 1
        with K.at(c, 0, hand_y):
            K.rr(c, 0, 0, 120, 70, 30, K.SKIN, a)
            K.rr(c, 0, -80, 80, 120, 20, "#6E9CC2", a)
    if dt >= 0:
        K.text(c, "自己在弹", 220, top + length + 40, 44, "serif_black", K.INK, clamp01((dt - 0.4) / 0.3))


# ---------------------------------------------------------------- 系统三要素

def system_map(c, g, el_t, d):
    """系统图：要素（圆点+标签）在 b0 起依次出现；连接（带箭头的线）在 b1 起画出；目标（中心靶心）在b2 拍亮起。
    swap 拍起要素换颜色（换人），rewire 拍起连接改走向，flip 拍起目标翻成 alt 文字。"""
    nodes = d.get("nodes", [("员工", -280, -180), ("工位", 260, -200), ("电脑", -300, 180), ("客户", 280, 170)])
    goal = d.get("goal", "KPI")
    b0, b1, b2 = d.get("b0", 0), d.get("b1", 1), d.get("b2", 2)
    k1 = clamp01(g.since(b1) / 0.6)
    rewire = clamp01(g.since(d.get("rewire", 99)) / 0.5)
    pairs = [(0, 1), (1, 3), (3, 2), (2, 0)]
    alt = [(0, 3), (1, 2), (0, 1), (2, 3)]
    if k1 > 0:
        for (a, b), (a2, b2_) in zip(pairs, alt):
            ia, ib = (a2, b2_) if rewire > 0.5 else (a, b)
            pa, pb = nodes[ia][1:], nodes[ib][1:]
            K.arrow(c, pa, pb, K.INK2, 7, 0.85, k1, 0.25, 26)
        if d.get("conn_label"):
            K.pill(c, 0, -300, d["conn_label"], 36, K.INK2, K.PAPER, k1)
    swap = clamp01(g.since(d.get("swap", 99)) / 0.3)
    for i, (name, x, y) in enumerate(nodes):
        st = fx.word_pop(g.since(b0 + i * d.get("step", 0.25)))
        if not st:
            continue
        a, s_, _ = st
        colr = K.mix(TEAL, K.GOLD, swap) if swap else TEAL
        with K.at(c, x, y, 0, s_):
            K.dot(c, 0, 0, 78, colr, a)
            K.text(c, name, 0, 0, 40, "serif_black", K.PAPER, a)
    st = fx.word_pop(g.since(b2))
    if st:
        a, s_, _ = st
        flip = clamp01(g.since(d.get("flip", 99)) / 0.3)
        fx.glow(c, 0, 0, 200, K.GOLD, 0.45 * a)
        with K.at(c, 0, 0, 0, s_ * (1 - 0.3 * math.sin(flip * math.pi))):
            K.ring(c, 0, 0, 92, RED, 12, a)
            K.ring(c, 0, 0, 56, RED, 10, a)
            K.dot(c, 0, 0, 34, RED if flip < 0.5 else K.INK, a)
            K.pill(c, 0, 128, goal if flip < 0.5 else d.get("alt", "输球"), 40, RED if flip < 0.5 else K.INK, K.PAPER, a)


# ---------------------------------------------------------------- 换人的工位

def desks(c, g, el_t, d):
    """一排工位，每个工位一个人；swap 拍起人一个个换成新面孔（不同角色颜色），但头顶的 tag 不变。"""
    n = d.get("n", 3)
    tag = d.get("tag")
    old = d.get("old", ("#6E9CC2", "#D98E8A", "#8C9A6A"))
    new = d.get("new", ("#C98B5A", "#7E6FA6", "#5E9A8A"))
    for i in range(n):
        x = (i - (n - 1) / 2) * 300
        K.rr(c, x, 120, 240, 22, 6, DESK)
        K.rr(c, x - 100, 175, 14, 110, 4, K.shade(DESK, 0.3))
        K.rr(c, x + 100, 175, 14, 110, 4, K.shade(DESK, 0.3))
        K.rr(c, x + 40, 70, 110, 76, 8, K.INK2)
        dt = g.since(d.get("swap", 99) + i * d.get("step", 0.5))
        k = clamp01(dt / 0.35) if dt >= 0 else 0
        for col, a in ((old[i % len(old)], 1 - k), (new[i % len(new)], k)):
            if a > 0.02:
                K.figure(c, x - 50, 230, 280, "sit", col, alpha=a, mood=d.get("mood", "flat"),
                         hair=("short", "long", "short")[i % 3], role="worker_f" if i % 3 == 1 else "worker")
        if tag:
            K.pill(c, x - 50, -200, tag, 34, d.get("tag_color", K.INK), K.PAPER)


# ---------------------------------------------------------------- 墙上标语与真实行为

def banner(c, g, el_t, d):
    """墙上横幅：text 竖排写在红底横幅上（b0 拍展开）。"""
    k = ease_out(clamp01(g.since(d.get("b0", 0)) / 0.5))
    w = d.get("w", 620)
    K.rr(c, 0, -170, w + 40, 16, 8, K.shade(DESK, 0.2))
    K.rr(c, 0, -170 + 90 * k, w, 180 * k, 6, RED)
    if k > 0.8:
        K.text(c, d.get("text", "客户第一"), 0, -80, 92, "serif_black", K.PAPER, clamp01((k - 0.8) / 0.2))
