"""《毛选》02–04 讲专用元件：便利贴雨、矛盾网、竹子迎刃而解、迷雾、三庄联盟、跷跷板（主次方面互相转化）、
梨子咬一口、认识循环、收藏夹、印象到概念的飞跃、高阁、山洞、钢琴键盘、抓手、数字仪表。坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_in, ease_out, lerp

from .art import DESK, PAPER2, RED

NOTE = ("#FFE8A3", "#FFD0C2", "#CDE8D2", "#D3E2F2", "#EAD7F2")


# ---------------------------------------------------------------- 便利贴雨（事情一大堆）

def sticky_rain(c, g, el_t, d):
    """便利贴从上方依次落下贴满（b0 起每 step 拍一张），每张写一件事。"""
    items = d["items"]
    b0, step = d.get("b0", 0), d.get("step", 0.5)
    for i, s in enumerate(items):
        dt = g.since(b0 + i * step)
        if dt < 0:
            continue
        k = ease_out(clamp01(dt / 0.25))
        col, row = i % 3, i // 3
        x = -300 + col * 300 + (row % 2) * 40
        y = -280 + row * 210
        rot = ((i * 37) % 13 - 6)
        with K.at(c, x, lerp(y - 500, y, k), rot):
            K.card(c, 0, 0, 250, 170, NOTE[i % len(NOTE)], 1, r=8)
            K.text(c, s, 0, 0, 44, "serif_black", K.INK)


# ---------------------------------------------------------------- 矛盾网：捉住中心，其余迎刃而解

def knot_web(c, g, el_t, d):
    """一张乱线网：中心结 center 与外围 items 相连；pick 拍中心结被圈出（金光），solve 拍外围逐个打勾、连线变绿。"""
    items = d["items"]
    n = len(items)
    pick, solve = d.get("pick", 99), d.get("solve", 99)
    ks = ease_out(clamp01(g.since(solve) / 0.4))
    pts = [(math.cos(-math.pi / 2 + 2 * math.pi * i / n) * 330, math.sin(-math.pi / 2 + 2 * math.pi * i / n) * 300)
           for i in range(n)]
    for i, (x, y) in enumerate(pts):
        K.seg(c, 0, 0, x, y, K.mix(K.INK3, K.GREEN, ks), 8)
        x2, y2 = pts[(i + 2) % n]
        K.seg(c, x, y, x2, y2, K.LINE, 4, 1 - ks)
    for i, ((x, y), s) in enumerate(zip(pts, items)):
        dt = g.since(solve + 0.25 * i) if ks > 0 else -1
        K.pill(c, x, y, s, 40, K.GREEN if dt >= 0 else K.INK2, K.PAPER)
        if dt >= 0:
            with K.at(c, x + 70, y - 40, 0, fx.word_pop(dt)[1]):
                K.icon(c, "check", 0, 0, 60, K.GREEN, 1, 0.3)
    kp = g.since(pick)
    if kp >= 0:
        fx.glow(c, 0, 0, 220, K.GOLD, 0.5)
        K.ring(c, 0, 0, 120, K.GOLD, 10, 1, ease_out(clamp01(kp / 0.4)))
    K.dot(c, 0, 0, 95, g.acc)
    K.text(c, d.get("center", "主要"), 0, 0, 52, "serif_black", K.PAPER)


def bamboo_split(c, g, el_t, d):
    """迎刃而解：一根竹子立着，刀在 cut 拍劈下，竹子从上到下裂成两半向两侧倒开。"""
    cut = d.get("cut", 1)
    dt = g.since(cut)
    k = ease_out(clamp01(dt / 0.45)) if dt >= 0 else 0
    for side in (-1, 1):
        with K.at(c, side * 30 * k, 380, side * 22 * k):
            K.rr(c, side * 34, -380, 68, 700, 14, "#7FA65A")
            for j in range(5):
                K.seg(c, side * 34 - 34, -650 + j * 140, side * 34 + 34, -650 + j * 140, K.shade("#7FA65A", 0.3), 6)
    by = lerp(-560, 300, ease_in(clamp01((dt + 0.15) / 0.3))) if dt > -0.15 else -560
    with K.at(c, 120, by, -20):
        K.poly(c, [(-180, -30), (60, -30), (110, 0), (60, 30), (-180, 30)], "#C9CED6")
        K.rr(c, -230, 0, 110, 50, 10, K.shade(DESK, 0.2))
    if dt >= 0:
        K.burst(c, 0, -250, dt, K.GOLD, 40, 200, 12, 8)


def fog(c, g, el_t, d):
    """如堕烟海：人物在灰雾里打转，问号漂浮；雾团随时间缓慢飘动。"""
    K.figure(c, 0, 300, 320, "think", K.HERO, mood="worried", hair="short", face=1 if math.sin(g.t * 2) > 0 else -1)
    for i in range(9):
        x = math.sin(g.t * 0.8 + i * 1.7) * 380
        y = -300 + i * 70 + math.cos(g.t + i) * 30
        K.dot(c, x, y, 120 + 30 * (i % 3), "#B8B2A8", 0.35)
    for i in range(3):
        a = clamp01(g.since(d.get("b0", 1) + i) / 0.2)
        K.icon(c, "question", -260 + i * 260, -340 + (i % 2) * 60, 90, K.RED, a, 0.3)


def villages(c, g, el_t, d):
    """三庄联盟：李、扈、祝三个寨子用绳子连着；tries=[(拍, 是否成功)] 依次一支箭射向祝家庄；
    untie 拍绳子断开，最后一次成功时祝家庄插上旗。"""
    pos = {"李": (-300, -120), "祝": (0, 140), "扈": (300, -120)}
    untie = d.get("untie", 99)
    ku = ease_out(clamp01(g.since(untie) / 0.35))
    for a, b in (("李", "祝"), ("扈", "祝")):
        (x0, y0), (x1, y1) = pos[a], pos[b]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        K.seg(c, x0, y0, lerp(x1, mx, ku), lerp(y1, my, ku), WOODROPE, 10)
        if ku > 0:
            K.seg(c, x1, y1, lerp(mx, x1, 0.3 * ku + 0.7), lerp(my, y1, 0.3 * ku + 0.7), WOODROPE, 10)
    for name, (x, y) in pos.items():
        s = 1.25 if name == "祝" else 1.0
        with K.at(c, x, y, 0, s):
            K.poly(c, [(-110, 0), (0, -90), (110, 0)], "#9C6B45")
            K.rr(c, 0, 60, 180, 120, 6, "#D9C6A5")
            K.rr(c, 0, 90, 50, 70, 6, K.shade("#D9C6A5", 0.4))
            K.text(c, name, 0, 30, 54, "serif_black", K.INK)
    win = False
    for i, (b, ok) in enumerate(d.get("tries", ())):
        dt = g.since(b)
        if dt < 0:
            continue
        x, y = pos["祝"]
        tx, ty = x - 40 + 30 * i, y + 20
        sx, sy = -480, 420
        k = clamp01(dt / 0.25)
        ax, ay = lerp(sx, tx, k), lerp(sy, ty, k)
        K.arrow(c, (ax - 90, ay + 60), (ax, ay), K.INK2, 8, 1, 1, 0, 26)
        if k >= 1:
            if ok:
                win = True
            else:
                with K.at(c, -230 + i * 230, 360, 0, fx.word_pop(dt - 0.25)[1] if dt > 0.25 else 0.01):
                    K.icon(c, "cross", 0, 0, 100, K.RED, 1, 0.3)
    if win:
        x, y = pos["祝"]
        K.seg(c, x, y - 130, x, y - 290, K.INK2, 8)
        K.poly(c, [(x, y - 290), (x + 110, y - 255), (x, y - 220)], RED)
        K.icon(c, "check", 300, 360, 110, K.GREEN, 1, 0.3)


WOODROPE = "#B58A55"


def seesaw(c, g, el_t, d):
    """跷跷板：左“甲”右“乙”两个砝码，开始甲重（左低），flip 拍砝码大小互换，板子翻向另一边。"""
    flip = d.get("flip", 99)
    k = ease_out(clamp01(g.since(flip) / 0.5))
    ang = lerp(-14, 14, k)
    K.poly(c, [(-70, 250), (70, 250), (0, 120)], K.INK2)
    with K.at(c, 0, 110, ang):
        K.rr(c, 0, 0, 820, 34, 14, DESK)
        la, lb = d.get("labels", ("甲", "乙"))
        sa, sb = lerp(1.25, 0.75, k), lerp(0.75, 1.25, k)
        for x, s, lab, col in ((-320, sa, la, g.acc), (320, sb, lb, K.INK2)):
            with K.at(c, x, -20 - 80 * s, -ang, s):
                K.rr(c, 0, 0, 160, 160, 24, col)
                K.text(c, lab, 0, 0, 70, "serif_black", K.PAPER)
    K.text(c, "主要", lerp(-320, 320, k), -330, 46, "serif_black", K.GOLD)


# ---------------------------------------------------------------- 梨子与实践

def pear(c, g, el_t, d):
    """梨子：bite 拍被咬一口（缺口 + 汁水星光），label 在咬后弹出。"""
    s = d.get("s", 1.0)
    with K.at(c, 0, 0, math.sin(g.t * 3) * 3, s):
        p = skia.Path()
        p.addCircle(0, 90, 170)
        p.addCircle(0, -80, 110)
        c.drawPath(p, K.paint("#D8C24A"))
        c.drawCircle(-50, 40, 60, K.paint("#E9DA7A", 0.7))
        K.rr(c, 10, -210, 16, 70, 8, "#6B4A2A")
        with K.at(c, 60, -200, -30):
            c.drawOval(skia.Rect.MakeXYWH(0, -18, 90, 36), K.paint(K.GREEN))
        dt = g.since(d.get("bite", 99))
        if dt >= 0:
            k = ease_out(clamp01(dt / 0.15))
            for j in range(3):
                c.drawCircle(150 - 10 * j, 20 + j * 55, 52 * k, K.paint(K.BG))
            fx.sparks(c, 150, 60, dt, [K.GOLD, "#FFFFFF", "#E9DA7A"], 14, 3, 200, 16)
    lab = d.get("label")
    if lab:
        st = fx.word_pop(g.since(d.get("bite", 99) + 1))
        if st:
            a, s_, _ = st
            with K.at(c, 0, 330, 0, s_):
                K.pill(c, 0, 0, lab, 50, g.acc, K.PAPER, a)


def loop(c, g, el_t, d):
    """认识循环：实践→认识→再实践→再认识 四个节点在圆上从 b0 起每拍亮起，最后一拍整体上移一层（高一级）。"""
    names = d.get("names", ("实践", "认识", "再实践", "再认识"))
    b0 = d.get("b0", 0)
    up = ease_out(clamp01(g.since(b0 + len(names)) / 0.5)) if d.get("up", True) else 0
    r = 250
    with K.at(c, 0, -60 * up):
        K.ring(c, 0, 0, r, K.LINE, 12)
        lit = 0
        for i, s in enumerate(names):
            dt = g.since(b0 + i)
            ang = -math.pi / 2 + i * math.pi / 2
            x, y = math.cos(ang) * r, math.sin(ang) * r
            if dt >= 0:
                lit = i + 1
            K.pill(c, x, y, s, 46, g.acc if dt >= 0 else K.INK3, K.PAPER)
        if lit:
            K.ring(c, 0, 0, r, g.acc, 12, 1, min(1.0, g.span(b0, b0 + len(names), ease=lambda x: x)), -90)
    if up > 0:
        K.arrow(c, (380, 200), (380, -200), K.GOLD, 12, up, up, 0, 36)
        K.text(c, "高一级", 380, -260, 44, "serif_black", K.GOLD, up)


def favorites(c, g, el_t, d):
    """收藏夹：手机里一格格“已收藏”的课程卡片从 b0 起每半拍一张堆满，计数跳涨；dust 拍起蒙上灰。"""
    K.card(c, 0, 0, 520, 820, K.DARK, 1, r=48)
    K.rr(c, 0, 0, 490, 790, 36, K.PAPER)
    K.text(c, d.get("title", "我的收藏"), 0, -340, 44, "sans_medium", K.INK)
    b0 = d.get("b0", 0)
    n = 0
    for i in range(10):
        dt = g.since(b0 + i * 0.35)
        if dt < 0:
            continue
        n += 1
        st = fx.word_pop(dt)
        r, cc = divmod(i, 2)
        with K.at(c, -110 + cc * 220, -230 + r * 125, 0, st[1]):
            K.rr(c, 0, 0, 200, 105, 14, NOTE[i % len(NOTE)])
            K.icon(c, "book", -55, 0, 60, K.INK2, 1, 0.2)
            K.rr(c, 30, -12, 80, 12, 6, K.INK3)
            K.rr(c, 20, 14, 60, 12, 6, K.LINE)
    if n:
        K.dot(c, 250, -400, 48, K.RED)
        K.text(c, f"{n * 10}+", 250, -400, 34, "black", K.PAPER)
    dk = clamp01(g.since(d.get("dust", 99)) / 0.5)
    if dk > 0:
        K.rr(c, 0, 20, 490, 690, 20, "#9C9488", 0.55 * dk)
        K.text(c, "从没打开", 0, 20, 64, "serif_black", K.PAPER, dk)


def leap(c, g, el_t, d):
    """感性 → 理性：零散的“印象”小点从 b0 起陆续出现、反复聚拢，leap 拍飞跃成一个发光的“概念”灯泡。"""
    lk = ease_out(clamp01(g.since(d.get("leap", 3)) / 0.4))
    for i in range(12):
        a = clamp01(g.since(d.get("b0", 0) + i * 0.2) / 0.15)
        ang = i * 2.4
        rr = 300 + 40 * math.sin(g.t * 2 + i)
        x, y = math.cos(ang) * rr * (1 - lk), math.sin(ang) * rr * 0.8 * (1 - lk) + 60
        K.dot(c, x, y, 26, (K.INK2, g.acc2, K.GREEN)[i % 3], a * (1 - lk))
    if g.since(d.get("b0", 0)) >= 0:
        K.text(c, "印象", -330, -330, 44, "serif_black", K.INK2, 1 - lk)
    if lk > 0:
        fx.glow(c, 0, 0, 280, K.GOLD, 0.55 * lk)
        with K.at(c, 0, 0, 0, 0.4 + 0.6 * lk):
            K.icon(c, "bulb", 0, 0, 260, K.GOLD, lk, 0.5)
        K.pill(c, 0, 230, "概念", 56, g.acc, K.PAPER, lk)


def high_shelf(c, g, el_t, d):
    """束之高阁：一本写着 label 的书在 b 拍被放到高高的架子上，落一层灰。"""
    K.rr(c, 0, -300, 640, 26, 6, DESK)
    K.rr(c, -280, -250, 20, 90, 4, K.shade(DESK, 0.3))
    K.rr(c, 280, -250, 20, 90, 4, K.shade(DESK, 0.3))
    k = ease_out(clamp01(g.since(d.get("b", 1)) / 0.45))
    x, y = lerp(-200, 0, k), lerp(250, -380, k)
    K.card(c, x, y, 200, 130, g.acc, 1, r=10)
    K.text(c, d.get("label", "道理"), x, y, 50, "serif_black", K.PAPER)
    dk = clamp01(g.since(d.get("b", 1) + 1) / 0.6)
    for i in range(10):
        K.dot(c, x - 90 + i * 20, y - 66, 8, "#9C9488", dk)
    if dk > 0:
        K.pill(c, 0, 0, "不用 = 没用", 50, K.INK2, K.PAPER, dk)


def cave(c, g, el_t, d):
    """虎穴：黑色山洞里亮起两只眼睛（eyes 拍），go 拍人物走进洞口。"""
    K.poly(c, [(-460, 300), (-300, -200), (0, -330), (300, -200), (460, 300)], "#8C7B66")
    p = skia.Path()
    p.moveTo(-200, 300)
    p.cubicTo(-200, -120, 200, -120, 200, 300)
    p.close()
    c.drawPath(p, K.paint("#1E1B18"))
    ke = clamp01(g.since(d.get("eyes", 1)) / 0.2)
    for sx in (-1, 1):
        K.dot(c, sx * 50, 90, 18, K.GOLD, ke)
    kg = g.span(d.get("go", 2), d.get("go", 2) + 1.5)
    if g.since(d.get("go", 2)) >= 0:
        K.figure(c, lerp(-380, -120, kg), 300, 260, K.walk(g.t * 2.4, 1.0), K.HERO, mood="open", hair="short")
    else:
        K.figure(c, -380, 300, 260, "stand", K.HERO, mood="worried", hair="short")


# ---------------------------------------------------------------- 弹钢琴

def piano(c, g, el_t, d):
    """钢琴：10 个白键（对应十个指头）。mode=one：只有 key 号键一直按、其余灰掉；mode=all：all_at 拍十键齐按、
    乱音波纹；mode=rhythm：从 b0 起按 seq 顺序每半拍按一个键，冒出音符；center 键标金色。"""
    labels = d.get("labels", [""] * 10)
    mode = d.get("mode", "rhythm")
    kw, kh = 92, 360
    x0 = -(10 * kw) / 2 + kw / 2
    K.rr(c, 0, -kh / 2 - 40, 10 * kw + 40, 80, 14, K.INK)
    pressed = set()
    noise = 0.0
    if mode == "one":
        k = d.get("key", 0)
        if g.since(d.get("b0", 0)) >= 0 and (g.t * 4) % 1 < 0.6:
            pressed.add(k)
    elif mode == "all":
        dt = g.since(d.get("all_at", 1))
        if dt >= 0:
            pressed = set(range(10))
            noise = clamp01(1 - dt / 1.2)
    else:
        for i, kk in enumerate(d.get("seq", ())):
            dt = g.since(d.get("b0", 0) + i * 0.5)
            if 0 <= dt < 0.35:
                pressed.add(kk)
            if dt >= 0:
                xx = x0 + kk * kw
                yy = -kh / 2 - 100 - 150 * clamp01(dt / 1.4)
                a = 1 - clamp01((dt - 0.8) / 0.6)
                K.text(c, "♪", xx, yy, 70, "black", g.acc if kk == d.get("center") else K.INK2, a)
    for i in range(10):
        x = x0 + i * kw
        dim = mode == "one" and i != d.get("key", 0)
        down = i in pressed
        col = K.PAPER if not dim else "#D8D2C8"
        if i == d.get("center"):
            col = K.tint(K.GOLD, 0.5)
        K.rr(c, x, (12 if down else 0), kw - 8, kh, 10, K.shade(col, 0.15) if down else col)
        if labels[i]:
            K.text(c, labels[i], x, 100 + (12 if down else 0), 34, "serif_black", K.INK2)
    for i in (0, 1, 3, 4, 5, 7, 8):
        K.rr(c, x0 + i * kw + kw / 2, -kh / 2 + 90, 52, 200, 6, K.INK)
    if noise > 0:
        for j in range(5):
            r = 200 + j * 70 + 120 * (1 - noise)
            K.ring(c, 0, -60, r, K.RED, 6, noise * 0.7)
        K.text(c, "不成调子", 0, -kh / 2 - 160, 70, "serif_black", K.RED, noise)


def grip(c, g, el_t, d):
    """抓与抓紧：一个球从上方落进手里（b 拍）。stage 0 伸着巴掌、1 握而不紧：球从手前滑落出画；2 抓紧：球被握住、金光。"""
    stage = d.get("stage", 2)
    dt = g.since(d.get("b", 1))
    by = lerp(-420, -60, ease_in(clamp01(dt / 0.35))) if dt >= 0 else -420
    caught = stage == 2 and dt >= 0.35
    slip = stage < 2 and dt >= 0.35
    if slip:
        by = lerp(-60, 700, ease_in(clamp01((dt - 0.35) / 0.5)))
    if not caught and not slip:
        K.dot(c, 0, by, 70, g.acc)
        K.text(c, d.get("ball", "主要工作"), 0, by - 110, 40, "serif_black", K.INK2)
    sk = K.SKIN
    if caught:
        fx.glow(c, 0, 40, 260, K.GOLD, 0.45)
        K.dot(c, 0, 10, 70, g.acc)
    K.rr(c, 0, 220, 170, 200, 40, sk)
    if stage == 0:
        for i in range(4):
            K.rr(c, -66 + i * 44, 50, 36, 170, 18, sk)
        with K.at(c, 110, 150, 40):
            K.rr(c, 0, 0, 40, 130, 20, sk)
    else:
        K.rr(c, 0, 90, 220, 120 if stage == 2 else 150, 50, sk)
        for i in range(4):
            K.seg(c, -60 + i * 40, 50, -60 + i * 40, 120, K.shade(sk, 0.25), 5)
        if stage == 1:
            K.rr(c, 0, 20, 120, 40, 18, K.shade(sk, 0.45))
    if slip:
        K.dot(c, 0, by, 70, g.acc, 1 - clamp01((dt - 0.6) / 0.3))
    lab = ("伸着巴掌", "抓而不紧", "抓紧")[stage]
    K.pill(c, 0, 420, lab, 50, (K.INK3, K.RED, K.GREEN)[stage], K.PAPER)


def gauges(c, g, el_t, d):
    """胸中有数：一张表，rows [(名称, 数值文字)] 从 b0 起每拍一行亮出数字。"""
    rows = d["rows"]
    w, rh = 680, 110
    h = rh * len(rows) + 130
    K.card(c, 0, 0, w, h, K.PAPER, 1, r=22, accent=g.acc)
    K.text(c, d.get("title", "心里有数"), 0, -h / 2 + 62, 48, "serif_black", K.INK)
    for i, (name, val) in enumerate(rows):
        y = -h / 2 + 150 + i * rh
        K.text(c, name, -w / 2 + 60, y, 46, "serif", K.INK, 1, "left")
        st = fx.word_pop(g.since(d.get("b0", 0) + i))
        if st:
            a, s_, _ = st
            with K.at(c, w / 2 - 110, y, 0, s_):
                K.text(c, val, 0, 0, 52, "black", g.acc, a)
        else:
            K.text(c, "?", w / 2 - 110, y, 52, "black", K.INK3)


def notice(c, g, el_t, d):
    """安民告示：告示纸在 b 拍贴上（议题逐行出现），旁边一个“粮草”箱子在 ready 拍盖上勾。"""
    k = ease_out(clamp01(g.since(d.get("b", 0)) / 0.3))
    with K.at(c, -120, 0, -2, 0.5 + 0.5 * k):
        K.card(c, 0, 0, 520, 620, PAPER2, k, r=8)
        K.text(c, d.get("title", "会议通知"), 0, -230, 56, "serif_black", RED, k)
        for i, s in enumerate(d.get("lines", ())):
            a = clamp01(g.since(d.get("b", 0) + 1 + i * 0.5) / 0.2)
            K.text(c, s, -200, -110 + i * 90, 44, "serif", K.INK, a, "left")
    st = fx.word_pop(g.since(d.get("ready", 3)))
    K.rr(c, 330, 200, 200, 150, 12, DESK)
    K.text(c, "材料", 330, 200, 46, "serif_black", K.PAPER)
    if st:
        a, s_, _ = st
        with K.at(c, 330, 70, 0, s_):
            K.icon(c, "check", 0, 0, 100, K.GREEN, a, 0.3)
