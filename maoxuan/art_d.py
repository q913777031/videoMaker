"""《毛选》08–10 讲专用元件：长文档、裹脚布、靶子与箭、中药铺抽屉、黑话幻灯片、套娃分点、垃圾桶、对联、墙上芦苇、
山间竹笋、蒙眼捉麻雀、事实三卡、大山与挖山、每日格子、神仙背山。坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, lerp

from .art import DESK, PAPER2, RED

MOUNT = "#7E8C6A"
SOIL = "#9C7A55"


# ---------------------------------------------------------------- 写作类

def long_doc(c, g, el_t, d):
    """长文档：一张纸从顶部向下越拉越长（b0→b1），满是灰色字行；右上角页码牌 pages。"""
    w = d.get("w", 560)
    k = g.span(d.get("b0", 0), d.get("b1", 2))
    top = -420
    h = lerp(d.get("h0", 260), d.get("h1", 860), k)
    K.card(c, 0, top + h / 2, w, h, K.PAPER, 1, r=10)
    K.text(c, d.get("title", "周报"), 0, top + 50, 46, "serif_black", K.INK)
    n = int((h - 110) / 38)
    for i in range(max(0, n)):
        K.rr(c, -10 + (i % 3) * 8, top + 110 + i * 38, w - 120 - (i % 4) * 40, 14, 7, K.LINE)
    if d.get("pages"):
        K.pill(c, w / 2 - 40, top + 20, d["pages"], 34, g.acc, K.PAPER)


def cloth(c, g, el_t, d):
    """裹脚布：一卷布从左向右（再折回）越拉越长，上方飘着臭味波浪线。"""
    k = g.span(d.get("b0", 0), d.get("b1", 3), ease=ease_out)
    L = 2600 * k
    rows = [(-300, 1), (-100, -1), (100, 1), (300, -1)]
    left = L
    for y, dirn in rows:
        seg = min(800.0, max(0.0, left))
        left -= 800
        if seg <= 0:
            break
        x0 = -400 if dirn > 0 else 400
        x1 = x0 + dirn * seg
        K.rr(c, (x0 + x1) / 2, y, abs(x1 - x0) + 2, 90, 12, "#EADBC0")
        for j in range(int(seg / 80)):
            xx = x0 + dirn * (40 + j * 80)
            K.seg(c, xx, y - 40, xx, y + 40, K.shade("#EADBC0", 0.15), 3)
    for i in range(3):
        x = -200 + i * 200
        p = skia.Path()
        ph = g.t * 3 + i
        p.moveTo(x, -380)
        for j in range(1, 7):
            p.lineTo(x + math.sin(ph + j) * 20, -380 - j * 22)
        a = clamp01(k * 3 - 0.5)
        c.drawPath(p, K.paint("#8FA05E", a * 0.8, 6))
    K.pill(c, 0, 420, d.get("label", "又长又臭"), 46, RED, K.PAPER)


def target(c, g, el_t, d):
    """靶子：arrows [(拍, 命中?)] 依次飞来，命中扎在靶心，偏了扎在靶外并打叉。"""
    r = d.get("r", 220)
    for i, col in enumerate((K.PAPER, RED, K.PAPER, RED, K.GOLD)):
        K.dot(c, 0, 0, r * (1 - i * 0.2), col)
    K.ring(c, 0, 0, r, K.INK2, 6)
    for b, hit in d.get("arrows", ()):
        dt = g.since(b)
        if dt < 0:
            continue
        k = ease_in(clamp01(dt / 0.25))
        tx, ty = (0, 0) if hit else (r + 140, -r - 40)
        x, y = lerp(-600, tx, k), lerp(-300, ty, k)
        ang = math.degrees(math.atan2(ty + 300, tx + 600))
        with K.at(c, x, y, ang):
            K.seg(c, -170, 0, 0, 0, WOODC, 10)
            K.poly(c, [(0, -14), (30, 0), (0, 14)], K.INK)
            K.poly(c, [(-170, 0), (-200, -22), (-150, 0), (-200, 22)], K.GOLD)
        if k >= 1:
            if hit:
                K.ripple(c, 0, 0, dt - 0.25, K.GOLD, 200, 6)
            else:
                K.icon(c, "cross", tx, ty + 120, 100, K.RED, clamp01((dt - 0.25) / 0.15), 0.3)
    if d.get("label"):
        K.pill(c, 0, r + 70, d["label"], 44, K.INK, K.PAPER)


WOODC = "#8A5A35"


def drawers(c, g, el_t, d):
    """中药铺药柜：4×4 抽屉格，标签 labels 从 b0 起每 step 拍依次亮起。"""
    labels = d["labels"]
    cols = d.get("cols", 4)
    rows = (len(labels) + cols - 1) // cols
    cw, ch = d.get("cw", 190), 130
    K.card(c, 0, 0, cols * cw + 40, rows * ch + 40, "#6E4A2E", 1, r=10)
    for i, lab in enumerate(labels):
        r, j = divmod(i, cols)
        x = -cols * cw / 2 + cw * (j + 0.5)
        y = -rows * ch / 2 + ch * (r + 0.5)
        K.rr(c, x, y, cw - 14, ch - 14, 8, "#A87B52")
        K.dot(c, x, y + 34, 9, K.GOLD)
        on = g.since(d.get("b0", 0) + i * d.get("step", 0.25)) >= 0
        K.rr(c, x, y - 12, cw - 60, 52, 6, K.PAPER if on else "#C9A57E")
        if on:
            K.text(c, lab, x, y - 12, 34, "serif_black", K.INK)


def slide(c, g, el_t, d):
    """幻灯片：标题 + words 从 b0 起每 step 拍散落弹出（颜色轮换，略带旋转）。"""
    K.card(c, 0, 0, 860, 560, K.PAPER, 1, r=16)
    K.rr(c, 0, -240, 860, 80, 0, g.acc)
    K.text(c, d.get("title", "汇报"), 0, -240, 44, "serif_black", K.PAPER)
    pos = [(-250, -110), (200, -90), (-120, 40), (250, 60), (-260, 180), (80, 190)]
    for i, w in enumerate(d["words"]):
        st = fx.word_pop(g.since(d.get("b0", 0) + i * d.get("step", 0.5)))
        if st:
            a, s_, _ = st
            x, y = pos[i % len(pos)]
            with K.at(c, x, y, (-6, 5, -3, 7, -5, 4)[i % 6], s_):
                K.pill(c, 0, 0, w, 50, (K.INK2, g.acc, K.GOLD, K.GREEN)[i % 4], K.PAPER, a)


def nested(c, g, el_t, d):
    """套娃分点：1. / 1.1 / 1.1.1 / 1.1.1.1 逐级缩进出现（b0 起每拍一级）。"""
    K.card(c, 0, 0, 800, 600, K.PAPER, 1, r=16)
    tags = ("1.", "1.1", "1.1.1", "1.1.1.1", "(1)")
    for i, t in enumerate(tags):
        st = fx.word_pop(g.since(d.get("b0", 0) + i * d.get("step", 0.75)))
        if st:
            a, s_, _ = st
            x, y = -320 + i * 70, -220 + i * 110
            with K.at(c, x, y, 0, s_):
                K.text(c, t, 0, 0, 46, "black", g.acc, a, "left")
                K.rr(c, K.text_w(t, 46, "black") + 140, 0, 200 - i * 20, 16, 8, K.LINE, a)


def trash(c, g, el_t, d):
    """垃圾桶：一卷长纸在 b 拍掉进桶里。"""
    K.poly(c, [(-150, -40), (150, -40), (120, 260), (-120, 260)], K.INK2)
    K.rr(c, 0, -60, 340, 40, 12, K.shade(K.INK2, 0.2))
    for i in range(4):
        K.seg(c, -80 + i * 55, 0, -70 + i * 47, 220, K.shade(K.INK2, 0.3), 6)
    dt = g.since(d.get("b", 1))
    k = ease_in(clamp01(dt / 0.4)) if dt >= 0 else 0
    if k < 1:
        y = lerp(-420, -60, k)
        with K.at(c, 0, y, 30 * k):
            K.rr(c, 0, 0, 200, 300, 10, K.PAPER)
            for i in range(6):
                K.rr(c, 0, -110 + i * 40, 140, 12, 6, K.LINE)
            K.text(c, d.get("label", "空话"), 0, -150, 36, "serif_black", K.INK)
    else:
        K.burst(c, 0, -80, dt - 0.4, K.GOLD, 30, 160, 10, 8)


# ---------------------------------------------------------------- 实事求是

def couplet(c, g, el_t, d):
    """对联：左右两条红纸，上联 left 与下联 right 逐字写出（b0 起每 step 拍一字，下联在上联之后）。"""
    left, right = d["left"], d["right"]
    b0, step = d.get("b0", 0), d.get("step", 0.2)
    n = max(len(left), len(right))
    sp = min(80.0, 820 / n)
    h = n * sp + 60
    for side, txt, bb in ((1, left, b0), (-1, right, b0 + len(left) * step)):
        x = side * 170
        K.rr(c, x, 0, 120, h, 6, RED)
        K.rr_stroke(c, x, 0, 104, h - 16, 4, K.GOLD, 3)
        for j, ch in enumerate(txt):
            a = clamp01(g.since(bb + j * step) / 0.15)
            K.text(c, ch, x, -h / 2 + 30 + sp * (j + 0.5), sp * 0.78, "serif_black", K.INK, a)


def reed(c, g, el_t, d):
    """墙上芦苇：墙头上一棵芦苇，穗子又大又重，根很浅；sway 拍起随风大幅摇晃。"""
    K.rr(c, 0, 220, 760, 300, 6, "#B9A88A")
    for r in range(4):
        K.seg(c, -380, 90 + r * 75, 380, 90 + r * 75, K.shade("#B9A88A", 0.25), 4)
    sw = math.sin(g.t * 5) * (18 if g.since(d.get("sway", 1)) >= 0 else 4)
    with K.at(c, 0, 70, sw):
        K.seg(c, 0, 0, 0, -360, "#9C8F5A", 10)
        c.drawOval(skia.Rect.MakeXYWH(-90, -560, 180, 240), K.paint("#C9B27A"))
        for i in range(4):
            K.seg(c, 0, -60 - i * 70, (-1) ** i * 90, -120 - i * 70, "#9C8F5A", 8)
    for i in range(3):
        K.seg(c, 0, 70, -30 + i * 30, 100, "#6E5E3A", 5)
    K.pill(c, 260, -300, "头重脚轻", 44, RED, K.PAPER, g.p(d.get("lab", 2), 0.2))
    K.pill(c, 240, 30, "根底浅", 44, K.INK, K.PAPER, g.p(d.get("lab", 2) + 1, 0.2))


def shoot(c, g, el_t, d):
    """山间竹笋：尖尖的竹笋，外壳一层层；cut 拍剖开露出空心。"""
    K.poly(c, [(-460, 320), (-150, 120), (120, 200), (460, 320)], "#9DB07E")
    k = ease_out(clamp01(g.since(d.get("cut", 2)) / 0.35))
    for side in (-1, 1):
        with K.at(c, side * 60 * k, 0):
            for i in range(6):
                y0 = 260 - i * 90
                w = 220 - i * 32
                pts = [(0, y0 - 140), (side * w / 2, y0), (0, y0 + 10)] if side > 0 else [(0, y0 - 140), (-w / 2, y0), (0, y0 + 10)]
                K.poly(c, pts, K.mix("#B88A4E", "#8E6A3A", i / 6))
    if k > 0:
        K.text(c, "空", 0, 100, 90, "serif_black", K.INK2, k)
    K.pill(c, -280, -260, "嘴尖", 44, RED, K.PAPER, g.p(d.get("lab", 1), 0.2))
    K.pill(c, 300, -120, "皮厚", 44, K.INK, K.PAPER, g.p(d.get("lab", 1) + 0.5, 0.2))
    K.pill(c, 300, 140, "腹中空", 44, K.INK, K.PAPER, g.p(d.get("cut", 2), 0.2))


def blind_catch(c, g, el_t, d):
    """蒙着眼捉：人蒙眼伸手扑（grab 拍），麻雀（或鱼 fish=True）在扑之前一刻飞走。"""
    grab = d.get("grab", 2)
    dg = g.since(grab)
    pose = K.blend(K.pose("stand"), K.pose("reach"), clamp01((dg + 0.3) / 0.3)) if dg > -0.3 else K.pose("stand")
    x = -200 + (60 * ease_out(clamp01(dg / 0.2)) if dg >= 0 else 0)
    K.figure(c, x, 300, 340, pose, d.get("color", K.HERO), mood="flat", hair="short")
    hy = 300 - 340 * 0.88
    K.rr(c, x + 18, hy, 120, 26, 10, K.INK)
    fish = d.get("fish", False)
    for i in range(3):
        bx, by = 180 + i * 90, (120 if fish else -40) + (i % 2) * 50
        if dg >= -0.1:
            k = ease_out(clamp01((dg + 0.1) / 0.6))
            bx += 200 * k + i * 40 * k
            by -= (260 if not fish else -60) * k * (1 if not fish else 0) + (0 if not fish else 0)
            if fish:
                by += -120 * math.sin(math.pi * k)
        if fish:
            with K.at(c, bx, by, -20):
                c.drawOval(skia.Rect.MakeXYWH(-50, -22, 100, 44), K.paint(K.GOLD))
                K.poly(c, [(-50, 0), (-80, -24), (-80, 24)], K.GOLD)
                K.dot(c, 28, -6, 5, K.INK)
        else:
            with K.at(c, bx, by):
                c.drawOval(skia.Rect.MakeXYWH(-34, -22, 68, 44), K.paint("#8A6A4A"))
                K.dot(c, 30, -16, 18, "#8A6A4A")
                K.dot(c, 36, -20, 4, K.INK)
                K.poly(c, [(46, -16), (60, -12), (46, -8)], K.GOLD)
                flap = math.sin(g.t * 30) * 20 if dg >= -0.1 else 0
                K.poly(c, [(-10, -10), (-40, -40 - flap), (10, -14)], K.shade("#8A6A4A", 0.3))
    if fish:
        K.rr(c, 0, 220, 1000, 140, 30, K.tint("#5B8DB8", 0.4), 0.8)
    if dg >= 0.2:
        K.icon(c, "cross", x + 160, -260, 110, K.RED, clamp01((dg - 0.2) / 0.15), 0.3)


# ---------------------------------------------------------------- 愚公移山

def _mountain(c, x, y, w, h, name, color=MOUNT, alpha=1.0):
    if h <= 4:
        K.rr(c, x, y - 4, w, 10, 5, SOIL, alpha)
        return
    K.poly(c, [(x - w / 2, y), (x - w * 0.12, y - h), (x + w * 0.05, y - h * 0.86), (x + w * 0.16, y - h * 0.95), (x + w / 2, y)],
           color, alpha)
    K.poly(c, [(x - w * 0.12, y - h), (x - w * 0.2, y - h * 0.8), (x - w * 0.05, y - h * 0.84), (x + w * 0.05, y - h * 0.86)],
           K.PAPER, 0.7 * alpha)
    if name:
        K.pill(c, x, y - h * 0.45, name, 40, K.shade(color, 0.4), K.PAPER, alpha)


def mountains(c, g, el_t, d):
    """两座大山（names），山脚一间小屋；dig 拍起每 step 拍矮一截（到 low 比例）；drop 拍前山依次落下。"""
    names = d.get("names", ("太行山", "王屋山"))
    low = d.get("low", 1.0)
    k = 1.0
    if d.get("dig") is not None:
        k = lerp(1.0, low, g.span(d["dig"], d.get("dig_end", d["dig"] + 3), ease=lambda x: x))
    K.seg(c, -520, 300, 520, 300, K.LINE, 8)
    for i, nm in enumerate(names):
        b = d.get("drop", -9) + i
        dt = g.since(b)
        if dt < 0:
            continue
        kk = ease_out(clamp01(dt / 0.25))
        x = (-200, 220)[i]
        _mountain(c, x, 300 - 200 * (1 - kk), 440, 560 * k * (1 - 0.15 * i), nm)
    if d.get("house", True):
        K.icon(c, "house", -420, 230, 120, K.INK2, 1, 0.5)


def hoe(c, h):
    """手持锄头。"""
    x, y = h
    with K.at(c, x, y, -30):
        K.rr(c, 0, -10, 12, 220, 6, "#8A5A35")
        K.poly(c, [(-8, -120), (60, -130), (56, -100), (-8, -100)], K.INK2)


def digger(c, g, el_t, d):
    """挖山的人：举锄头（每拍砸下一次），砸下时溅起土块。"""
    x0 = d.get("x0", 0)
    s = d.get("s", 300)
    b0 = d.get("b0", 0)
    beat = g.since(b0)
    ph = (beat / max(1e-3, g.b(b0 + 1) - g.b(b0))) % 1 if beat >= 0 else 0
    up = K.blend(K.pose("fist"), K.pose("crouch"), ease_in_out(clamp01(ph * 2 if ph < 0.5 else 2 - ph * 2)))
    K.figure(c, x0, 0, s, up if beat >= 0 else "stand", d.get("color", "#7A6A55"), mood=d.get("mood", "calm"),
             hair=d.get("hair", "bun"), face=d.get("face", 1), prop=hoe)
    if beat >= 0 and ph < 0.3:
        for i in range(5):
            a = i * 0.8 + 0.5
            K.dot(c, x0 + d.get("face", 1) * 90 + math.cos(a) * 80 * ph * 3, -20 - math.sin(a) * 90 * ph * 3, 12, SOIL,
                  1 - ph * 3)


def daily(c, g, el_t, d):
    """每日格子：n 格，从 b0 起逐格打勾（每 step 拍一格），上方 Counter 式文字“第 x 天”。"""
    n, cols = d.get("n", 21), d.get("cols", 7)
    cw = d.get("cw", 110)
    rows = (n + cols - 1) // cols
    K.card(c, 0, 0, cols * cw + 60, rows * cw + 140, K.PAPER, 1, r=20)
    if d.get("title", "每天挖一点"):
        K.text(c, d.get("title", "每天挖一点"), 0, -rows * cw / 2 - 30, 46, "serif_black", K.INK)
    done = 0
    for i in range(n):
        r, j = divmod(i, cols)
        x = -cols * cw / 2 + cw * (j + 0.5)
        y = -rows * cw / 2 + 40 + cw * (r + 0.5)
        on = g.since(d.get("b0", 0) + i * d.get("step", 0.15)) >= 0
        K.rr(c, x, y, cw - 14, cw - 14, 12, g.acc if on else K.LINE)
        if on:
            done += 1
            K.seg(c, x - cw * 0.2, y, x - cw * 0.05, y + cw * 0.16, K.PAPER, cw * 0.09)
            K.seg(c, x - cw * 0.05, y + cw * 0.16, x + cw * 0.22, y - cw * 0.16, K.PAPER, cw * 0.09)


def immortals(c, g, el_t, d):
    """神仙背山：天上放光，两个发光的小人从天而降（b0），背起两座山飞走（b1 起）。"""
    fx.rays(c, 0, -460, 900, K.GOLD, g.t, 16, 0.25)
    k = ease_out(clamp01(g.since(d.get("b0", 0)) / 0.5))
    up = ease_in(clamp01(g.since(d.get("b1", 2)) / 0.8))
    for i, x in enumerate((-200, 220)):
        y = lerp(-500, 200, k) - 700 * up
        _mountain(c, x, y + 100, 300 * (1 - 0.1 * i), 360, "" if up > 0 else ("太行山", "王屋山")[i], alpha=1 - 0.3 * up)
        if k > 0:
            fx.glow(c, x, y - 300, 140, K.GOLD, 0.5 * k)
            K.figure(c, x, y - 220, 180, "carry", K.PAPER, alpha=k, mood="smile", hair="bun")


def chips(c, g, el_t, d):
    """系列回顾：items（期号, 概念）以 2 列网格从 b0 起每 step 拍弹出。"""
    items = d["items"]
    for i, (no, name) in enumerate(items):
        st = fx.word_pop(g.since(d.get("b0", 0) + i * d.get("step", 0.25)))
        if not st:
            continue
        a, s_, _ = st
        r, j = divmod(i, 2)
        x, y = (-220, 220)[j], -360 + r * 150
        with K.at(c, x, y, (-2, 2)[(i + r) % 2], s_):
            K.rr(c, 0, 0, 400, 112, 24, g.acc if i == len(items) - 1 else K.PAPER, a)
            lab = f"{no} {name}"
            size = min(40.0, 40 * 360 / K.text_w(lab, 40, "serif_black"))
            K.text(c, lab, 0, 0, size, "serif_black", K.PAPER if i == len(items) - 1 else K.INK, a)
