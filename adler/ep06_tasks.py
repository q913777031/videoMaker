"""06 课题分离：别人怎么看你，是谁的课题？"""

import math

import skia

from engine import gfx
from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, ease_out_back, lerp

from . import core
from . import kit as K
from .core import Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

ACC = "#C8566E"
GROUND = 1130
WOOD = "#A0784F"
WATER = "#8DBAD3"


# ---------------------------------------------------------------- 通用小工具

def ground(g):
    K.ground(g.c, GROUND)


def joints(s, p="stand", face=1):
    """与 kit.figure 相同的几何：头心、近手、远手、胸口（相对脚底中点）。"""
    d = K.pose(p)
    u = s
    thigh, shin, upper, fore = 0.235 * u, 0.225 * u, 0.19 * u, 0.18 * u

    def ext(a1, a2):
        (_, ey), (_, fy) = K._limb(0, 0, a1, a2, thigh, shin, 1)
        return max(ey, fy)

    hip = -d["seat"] * u if d["seat"] > 0 else -max(ext(d["ll1"], d["ll2"]), ext(d["rl1"], d["rl2"]))
    lean = math.radians(d["lean"])
    sh_x, sh_y = face * 0.30 * u * math.sin(lean), hip - 0.30 * u * math.cos(lean)
    hd = math.radians(d["head"])
    head = (sh_x + face * 0.15 * u * math.sin(lean + hd * 0.5), sh_y - 0.15 * u * math.cos(lean + hd * 0.5))
    _, near = K._limb(sh_x + 0.06 * u * face, sh_y + 0.03 * u, d["la1"], d["la2"], upper, fore, face)
    _, far = K._limb(sh_x - 0.06 * u * face, sh_y + 0.03 * u, d["ra1"], d["ra2"], upper, fore, face)
    return dict(head=head, near=near, far=far, chest=(sh_x * 0.6, sh_y + 0.1 * u), top=(head[0], head[1] - 0.16 * u))


def fig_at(el, g):
    """Fig 元素此刻的关节位置（与引擎绘制同一套关键帧与迈步，忽略入场位移和呼吸起伏）。"""
    d = core._resolve(el, g)
    p = d.get("pose", "stand")
    s = d["s"]
    w = d.get("_walking", 0.0)
    if w > 0:
        p = K.walk(abs(d["x"] - el.props["x"]) / (0.28 * s), w * d.get("stride", 1.0), p if isinstance(p, str) else "stand")
    j = joints(s, p, d.get("face", 1))
    return {k: (d["x"] + v[0], d["y"] + v[1]) for k, v in j.items()}


def fall(g, beat, dist=170, dur=0.3):
    """自定义落下：第 beat 拍落定（撞击帧 = 拍点），之后轻微回弹；返回 (dy, 纵向压缩) 或 None。"""
    dt = g.since(beat)
    if dt < -dur:
        return None
    if dt < 0:
        return -dist * (1 - ease_in(1 + dt / dur)), 1.0
    q = clamp01(dt / 0.28)
    return -10 * math.sin(q * math.pi), 1 - 0.1 * math.sin(q * math.pi)


def squash(g, beats, amt=0.09):
    """箱子被砸中后的纵向压缩系数。"""
    v = 1.0
    for b in beats:
        q = g.since(b)
        if 0 <= q < 0.3:
            v -= amt * math.sin(q / 0.3 * math.pi)
    return v


# ---------------------------------------------------------------- 1 刷新点赞

REFRESH = (3, 6, 9)


def phone_feed(c, g, t, d):
    """大手机：朋友圈一条动态，下拉刷新（第 3/6/9 拍松手），点赞数 0 → 0 → 1。"""
    w, h = 380, 660
    with K.paper(c, 1, 1.1):
        K.rr(c, 0, 0, w, h, 50, K.DARK)
    K.rr(c, 0, 0, w - 30, h - 74, 30, K.PAPER)
    K.rr(c, 0, -h / 2 + 22, 96, 14, 7, K.INK)
    off, spin = 0.0, -1.0
    for b in REFRESH:
        dt = g.since(b)
        if -0.4 <= dt < 0:
            off = 70 * ease_out((dt + 0.4) / 0.4)
            spin = dt + 0.4
        elif 0 <= dt < 0.3:
            off = 70 * (1 - ease_out(dt / 0.3))
            spin = 0.4 + dt
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-(w - 30) / 2, -(h - 74) / 2, w - 30, h - 74), 30, 30), True)
    if spin >= 0:
        K.ring(c, 0, -h / 2 + 72, 18, ACC, 6, 1.0, 0.75, spin * 900)
    with K.at(c, 0, off):
        y0 = -h / 2 + 90
        K.dot(c, -120, y0, 30, K.HERO)
        K.dot(c, -120, y0 - 6, 12, K.SKIN)
        K.rr(c, -10, y0 - 10, 150, 16, 8, K.INK)
        K.rr(c, -30, y0 + 16, 110, 12, 6, K.LINE)
        K.rr(c, 0, y0 + 180, 300, 250, 16, K.tint(ACC, 0.55))
        K.dot(c, 80, y0 + 110, 34, K.GOLD)
        K.poly(c, [(-150, y0 + 305), (-60, y0 + 170), (20, y0 + 260), (70, y0 + 210), (150, y0 + 305)],
               K.mix(ACC, K.INK, 0.25))
        n = sum(g.since(b) >= 0 for b in REFRESH)
        liked = n >= 3
        k = clamp01(g.since(REFRESH[n - 1]) / 0.35) if n else 1.0
        bump = 1 + 0.35 * math.sin(k * math.pi) if n else 1.0
        hy = y0 + 360
        with K.at(c, -100, hy, 0, bump if liked else 1.0):
            if liked:
                K.heart(c, 0, 0, 64, K.RED)
            else:
                path = skia.Path()
                s = 64
                path.moveTo(0, s * 0.42)
                path.cubicTo(-s * 0.62, -s * 0.02, -s * 0.42, -s * 0.58, 0, -s * 0.22)
                path.cubicTo(s * 0.42, -s * 0.58, s * 0.62, -s * 0.02, 0, s * 0.42)
                c.drawPath(path, K.paint(K.INK3, 1, 6))
        with K.at(c, -30, hy, 0, bump):
            K.text(c, "1" if liked else "0", 0, 0, 64, "black", K.RED if liked else K.INK3, 1, "left")
        K.rr(c, 60, hy, 110, 14, 7, K.LINE)
    c.restore()


# ---------------------------------------------------------------- 2 夜里琢磨

def night_window(c, g, t, d):
    """夜窗：月亮在整个镜头里从左上划到右边（一整晚）。"""
    w, h = 300, 260
    with K.paper(c, 1, 0.8):
        K.rr(c, 0, 0, w + 26, h + 26, 14, K.PAPER)
    K.rr(c, 0, 0, w, h, 6, "#2E3552")
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h))
    for x, y in ((-110, -80), (-40, -30), (60, -95), (110, 40), (-90, 60), (20, 80)):
        K.dot(c, x, y, 3 + 1.5 * math.sin(g.t * 3 + x), "#F3E3B0", 0.8)
    k = clamp01(g.t / g.dur)
    mx = lerp(-100, 110, k)
    my = -40 + 0.006 * (mx - 10) ** 2 - 40
    K.dot(c, mx, my, 40, "#F3E3B0")
    K.dot(c, mx + 16, my - 10, 36, "#2E3552")
    c.restore()
    K.seg(c, 0, -h / 2, 0, h / 2, K.PAPER, 10)
    K.seg(c, -w / 2, 0, w / 2, 0, K.PAPER, 10)


def bed(c, g, t, d):
    """床（原点为地面中点）。"""
    with K.paper(c, 1, 0.7):
        K.rr(c, -228, -115, 26, 230, 10, WOOD)
        for x in (-200, 205):
            K.rr(c, x, -16, 18, 32, 4, K.shade(WOOD, 0.2))
        K.rr(c, 0, -62, 460, 64, 14, "#EDE4D6")
        K.rr(c, 70, -58, 320, 58, 14, K.tint(ACC, 0.25))
        K.rr(c, -160, -104, 100, 40, 18, K.PAPER)


def colleague_scene(c, w, h):
    K.figure(c, -50, h / 2 - 8, 120, "stand", K.OTHER2, mood="flat", face=1, lift=0.3)
    K.bubble(c, 55, -20, "随便吧。", 24, (-0.5, 1), 1, 1, K.PAPER, K.INK, ACC, lift=0.3)


SIT_COVER = dict(K.POSES["sit_sad"], la1=112, la2=120, ra1=100, ra2=130, head=20)


# ---------------------------------------------------------------- 3 背着一摞气泡

BURDEN1 = dict(lean=24, head=6, la1=-40, la2=-60, ra1=-30, ra2=-70, ll1=10, ll2=-8, rl1=-8, rl2=-4)
BURDEN2 = dict(lean=32, head=10, la1=-46, la2=-66, ra1=-36, ra2=-74, ll1=24, ll2=-30, rl1=4, rl2=-26)
BURDEN3 = dict(lean=40, head=14, la1=-50, la2=-70, ra1=-40, ra2=-80, ll1=34, ll2=-50, rl1=12, rl2=-40)
STACK = ("他怎么想？", "会不会被笑？", "她生气了吗？", "要不要回？")


def burden(hero):
    """背上的大包 + 一个个落下来压在包上的“别人的想法”气泡（第 1–4 拍各落一个），全部跟着主角的姿势走。"""

    def fn(c, g, t, d):
        j = fig_at(hero, g)
        d_ = core._resolve(hero, g)
        lean = K.pose(d_.get("pose", "stand"))["lean"] if isinstance(d_.get("pose"), str) else d_["pose"]["lean"]
        (cx, cy) = j["chest"]
        bx, by = cx - 96, cy - 20
        rot = lean * 0.8
        with K.at(c, bx, by, rot):
            with K.paper(c, 1, 0.8):
                K.rr(c, 0, 0, 170, 220, 38, K.OTHER3)
                K.rr(c, 0, -78, 136, 44, 20, K.shade(K.OTHER3, 0.2))
                K.rr(c, 0, 34, 100, 78, 16, K.shade(K.OTHER3, 0.12))
        a = math.radians(rot)
        tx, ty = bx + 112 * math.sin(a) - 46, by - 112 * math.cos(a)
        for i, txt in enumerate(STACK):
            f = fall(g, 1 + i, 200, 0.3)
            if f is None:
                continue
            y = ty - 38 - 76 * i + f[0]
            x = tx + (-10, 14, -4, 18)[i]
            with K.at(c, x, y, (-4, 3, -2, 5)[i], 1, f[1]):
                K.bubble(c, 0, 0, txt, 34, (0, 1), 1, 1, K.PAPER, K.INK, ACC, lift=0.6)

    return fn


def sweat(c, g, t, d):
    k = clamp01(g.since(6) / 0.3)
    if k <= 0:
        return
    for i, (dx, dy) in enumerate(((0, 0), (36, 30))):
        q = (g.since(6) * 1.2 + i * 0.4) % 1.0
        K.icon(c, "water", dx, dy + q * 40, 34 * ease_out_back(k, 2), "#7FB3D5", 1 - q, 0.2)


# ---------------------------------------------------------------- 4 两个圆分开

def venn(c, g, t, d):
    """两个重叠的圆（我 / 他人），中间一团乱线；第 4 拍分开，乱线消失。"""
    k = ease_in_out(clamp01(g.since(4) / 0.5))
    sep = lerp(70, 225, k)
    r = 150
    for sgn, colr in ((-1, K.HERO), (1, K.OTHER2)):
        K.dot(c, sgn * sep, 0, r, K.tint(colr, 0.7), 0.75)
        K.ring(c, sgn * sep, 0, r, colr, 5, 0.9)
    if k < 1:
        path = skia.Path()
        path.moveTo(-40, -30)
        for i in range(14):
            a = i * 2.3
            path.quadTo(30 * math.cos(a), 50 * math.sin(a * 1.3), 40 * math.cos(a + 1.1), 60 * math.sin(a + 0.7))
        c.drawPath(path, K.paint(K.INK2, (1 - k) * 0.9, 4))
    K.burst(c, 0, 0, g.since(4), ACC, 60, 200, 10, 7)
    m1 = "smile" if k > 0.5 else "worried"
    K.figure(c, -sep - 10, 95, 165, "stand", K.HERO, mood=m1, hair="short", lift=0.4)
    K.figure(c, sep + 10, 95, 165, "stand", K.OTHER2, mood="calm" if k > 0.5 else "flat", face=-1, lift=0.4)


# ---------------------------------------------------------------- 5 / 13 两个箱子

BOX_W, BOX_H = 270, 170


def box_back(c, g, t, d):
    K.rr(c, 0, -BOX_H * squash(g, d.get("hits", ())), BOX_W - 8, 42, 16, K.shade(d["color"], 0.4))


def box_front(c, g, t, d):
    sq = squash(g, d.get("hits", ()))
    with K.at(c, 0, 0, 0, 1, sq):
        with K.paper(c, 1, 0.9):
            K.rr(c, 0, -BOX_H / 2, BOX_W, BOX_H, 16, d["color"])
            K.rr(c, 0, -BOX_H + 6, BOX_W + 10, 18, 9, K.shade(d["color"], 0.15))
        K.text(c, d["label"], 0, -BOX_H / 2 + 6, d.get("size", 40), "serif_black", K.PAPER)


def fly_card(c, g, t, d):
    """卡片在 show 拍弹出、悬停，然后在 land 拍正好落进箱子（只露出上沿）。"""
    show, land = d["show"], d["land"]
    k = clamp01(g.since(show) / 0.35)
    if k <= 0:
        return
    (x0, y0), (x1, y1) = d["start"], d["target"]
    fly = d.get("fly", 0.55)
    tf = clamp01((g.t - (g.b(land) - fly)) / fly)
    e = tf * tf
    wob = 6 * math.sin(g.t * 2.4) * (1 - tf)
    hold = d.get("hold")
    if hold is not None and tf <= 0:
        q = ease_in_out(clamp01(g.since(hold[0]) / 0.5))
        x0 = lerp(x0, hold[1], q)
    x = lerp(x0, x1, e)
    y = lerp(y0, y1, e) - 170 * math.sin(math.pi * e) + wob
    sc = (0.2 + 0.8 * ease_out_back(k, 2)) * lerp(1, 0.62, e)
    shake = d.get("shake")
    rot = lerp(-3, 8 if x1 > x0 else -8, e)
    if shake is not None:
        rot += 3 * math.sin(g.t * 30) * clamp01(g.since(shake) / 0.2) * (1 - tf)
    K.text_card(c, x, y, d["lines"], d.get("size", 44), None, K.PAPER, K.INK, ACC, 1, rot, sc, accent=d.get("accent"))


# ---------------------------------------------------------------- 6 画板与评分牌

def divider(c, g, t, d):
    p = ease_out(clamp01(g.since(1) / 0.6))
    path = skia.Path()
    path.moveTo(540, 350)
    path.lineTo(540, 1200)
    gfx.stroke_path(c, path, K.INK3, 6, 1.0, p, dash=(26, 18, 0))


def easel(c, g, t, d):
    """画架（原点为地面中点）：第 2 拍画上太阳，第 4 拍画上山。"""
    with K.paper(c, 1, 0.7):
        K.seg(c, -80, 0, 0, -350, WOOD, 12)
        K.seg(c, 80, 0, 0, -350, WOOD, 12)
        K.seg(c, 0, -330, 30, 0, K.shade(WOOD, 0.25), 10)
        K.rr(c, 0, -150, 190, 14, 6, K.shade(WOOD, 0.2))
        K.rr(c, 0, -250, 220, 190, 8, K.PAPER)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(-100, -335, 200, 170))
    k1 = ease_out_back(clamp01(g.since(2) / 0.35), 2)
    if k1 > 0:
        K.dot(c, 45, -295, 26 * k1, K.GOLD)
    k2 = ease_out(clamp01(g.since(4) / 0.5))
    if k2 > 0:
        K.poly(c, [(-110, -165), (-50, -165 - 110 * k2), (10, -165 - 60 * k2), (50, -165 - 90 * k2), (110, -165)],
               K.GREEN)
    c.restore()


def brush(c, h):
    K.seg(c, h[0], h[1], h[0] + 36, h[1] - 40, WOOD, 8)
    K.dot(c, h[0] + 38, h[1] - 43, 8, ACC)


def score_sign(fig, beat, score):
    def fn(c, g, t, d):
        k = clamp01(g.since(beat) / 0.4)
        if k <= 0:
            return
        hx, hy = fig_at(fig, g)["near"]
        sc = 0.2 + 0.8 * ease_out_back(k, 2)
        K.seg(c, hx, hy + 10, hx, hy - 60 * sc, WOOD, 9)
        with K.at(c, hx, hy - 105 * sc, -4, sc):
            with K.paper(c, 1, 0.8):
                K.rr(c, 0, 0, 140, 92, 14, K.PAPER)
            K.text(c, score, -8, 0, 54, "serif_black", ACC)
            K.text(c, "分", 46, 10, 26, "sans_medium", K.INK2)
    return fn


# ---------------------------------------------------------------- 7 马与水

HORSE = "#B07A57"
MANE = "#5A3B2A"


def horse(c, x, y, s, phase=0.0, amp=0.0, turn=0.0, alpha=1.0):
    """侧面纸片马，(x, y) 为地面上身体中点，朝右；phase/amp 为迈步，turn 0→1 把头从前方甩向后方。"""
    with K.paper(c, alpha, 0.8, skia.Rect.MakeXYWH(x - s, y - 1.4 * s, 2 * s, 1.6 * s)):
        c.save()
        c.translate(x, y)
        legs = ((-0.30, 0.0, True), (-0.20, math.pi, False), (0.22, math.pi, True), (0.33, 0.0, False))
        for lx, ph, far in legs:
            a = amp * 22 * math.sin(phase * math.pi + ph)
            col = K.shade(HORSE, 0.22) if far else HORSE
            with K.at(c, lx * s, -0.44 * s, a):
                K.rr(c, 0, 0.21 * s, 0.075 * s, 0.44 * s, 0.03 * s, col)
                K.rr(c, 0, 0.42 * s, 0.085 * s, 0.05 * s, 0.02 * s, K.DARK)
        path = skia.Path()
        path.moveTo(-0.42 * s, -0.64 * s)
        path.quadTo(-0.62 * s, -0.5 * s, -0.56 * s, -0.24 * s)
        c.drawPath(path, K.paint(MANE, 1, 0.07 * s))
        K.rr(c, 0, -0.58 * s, 0.86 * s, 0.32 * s, 0.16 * s, HORSE)
        th = math.radians(lerp(28, -24, turn))
        bx, by = 0.31 * s, -0.66 * s
        L = 0.36 * s
        nx, ny = bx + L * math.sin(th), by - L * math.cos(th)
        path = skia.Path()
        path.moveTo(bx - 0.08 * s, by + 0.05 * s)
        path.lineTo(nx - 0.06 * s * math.cos(th), ny - 0.06 * s * math.sin(th))
        path.lineTo(nx + 0.07 * s * math.cos(th), ny + 0.07 * s * math.sin(th))
        path.lineTo(bx + 0.12 * s, by + 0.08 * s)
        path.close()
        c.drawPath(path, K.paint(HORSE))
        c.drawLine(bx - 0.06 * s, by + 0.02 * s, nx - 0.05 * s * math.cos(th), ny - 0.05 * s * math.sin(th),
                   K.paint(MANE, 1, 0.06 * s))
        phi = lerp(118, -118, ease_in_out(turn))
        with K.at(c, nx, ny, phi - 90):
            K.rr(c, 0.14 * s, 0, 0.34 * s, 0.15 * s, 0.07 * s, HORSE)
            K.dot(c, 0.29 * s, 0.01 * s, 0.035 * s, K.shade(HORSE, 0.3))
            K.dot(c, 0.06 * s, -0.035 * s, 0.022 * s, K.INK)
            K.poly(c, [(-0.04 * s, -0.06 * s), (0.02 * s, -0.16 * s), (0.06 * s, -0.06 * s)], K.shade(HORSE, 0.15))
        c.restore()


def pond(c, x, y, w, t):
    with K.paper(c, 1, 0.3):
        c.drawOval(skia.Rect.MakeXYWH(x - w / 2, y - 26, w, 60), K.paint(WATER))
    for i in range(2):
        q = (t * 0.5 + i * 0.5) % 1.0
        c.drawOval(skia.Rect.MakeXYWH(x - 40 - 50 * q, y - 6 - 8 * q, 80 + 100 * q, 16 + 16 * q),
                   K.paint(K.PAPER, 0.6 * (1 - q), 3))
    for dx in (-w / 2 + 10, w / 2 - 20):
        for k in range(3):
            K.seg(c, x + dx + k * 10, y + 4, x + dx + k * 10 + (k - 1) * 8, y - 50 - 12 * k, K.GREEN, 6)


H7 = dict(x0=290, x1=505, s=340, b=1, dur=2.4)


def horse_scene(c, g, t, d):
    """马被牵到水边（第 1 拍起走，约第 5.5 拍到），第 8 拍把头甩开不喝。"""
    k = clamp01(g.since(H7["b"]) / H7["dur"])
    e = ease_in_out(k)
    x = lerp(H7["x0"], H7["x1"], e)
    amp = math.sin(math.pi * k) if 0 < k < 1 else 0.0
    turn = ease_in_out(clamp01(g.since(8) / 0.45))
    turn -= 0.12 * math.sin(clamp01(g.since(8.9) / 0.5) * math.pi * 2) * (g.since(8.9) > 0)
    pond(c, 810, GROUND + 6, 270, g.t)
    horse(c, x, GROUND, H7["s"], (x - H7["x0"]) / 70, amp, clamp01(turn))
    # 缰绳：马嘴 → 人的远手
    th = math.radians(lerp(28, -24, clamp01(turn)))
    nx, ny = x + 0.31 * H7["s"] + 0.36 * H7["s"] * math.sin(th), GROUND - 0.66 * H7["s"] - 0.36 * H7["s"] * math.cos(th)
    hx, hy = fig_at(d["person"], g)["far"]
    path = skia.Path()
    path.moveTo(nx, ny + 10)
    path.quadTo((nx + hx) / 2, max(ny, hy) + 60, hx, hy)
    c.drawPath(path, K.paint(K.shade(WOOD, 0.3), 1, 5))
    q = g.since(8)
    if 0 <= q < 0.9:
        for i in range(3):
            K.dot(c, nx - 40 - 40 * q * (i + 1) * 0.6, ny - 30 - 30 * q, 10 * (1 - q), K.INK3, 0.8)


# ---------------------------------------------------------------- 9 递梯子

def ledge(c, g, t, d):
    with K.paper(c, 1, 0.8):
        K.rr(c, 935, 980, 170, 300, 10, K.mix(K.LINE, K.INK3, 0.4))
        K.rr(c, 935, 836, 180, 16, 8, K.INK3)
    K.icon(c, "flag", 945, 760, 120, accent=ACC, p=g.t * 0.6)


# ---------------------------------------------------------------- 10 拔河

PULL = dict(lean=-14, head=-2, la1=84, la2=4, ra1=72, ra2=14, ll1=-18, ll2=0, rl1=22, rl2=-10)
PULL2 = dict(lean=-22, head=0, la1=88, la2=0, ra1=78, ra2=8, ll1=-26, ll2=0, rl1=30, rl2=-14)


def tug(adult, kid):
    """两人中间的书，以及两人之间越绷越紧、越抖越厉害的“关系绳”。"""

    def fn(c, g, t, d):
        ja, jk = fig_at(adult, g), fig_at(kid, g)
        tension = sum(clamp01(g.since(b) / 0.3) for b in (2, 5, 8)) / 3
        shake = tension ** 2 * (1 + 2 * clamp01(g.since(10) / 0.2))
        (ax, ay), (kx, ky) = ja["chest"], jk["chest"]
        ay -= 20
        ky -= 20
        path = skia.Path()
        path.moveTo(ax, ay)
        n = 24
        sag = 120 * (1 - tension)
        for i in range(1, n + 1):
            q = i / n
            px = lerp(ax, kx, q)
            py = lerp(ay, ky, q) + sag * math.sin(math.pi * q) + 9 * shake * math.sin(q * math.pi * 6 + g.t * 40) * math.sin(math.pi * q)
            path.lineTo(px, py)
        c.drawPath(path, K.paint(K.mix(K.INK3, K.RED, tension), 1, 7))
        mx, my = (ja["near"][0] + jk["near"][0]) / 2, (ja["near"][1] + jk["near"][1]) / 2
        jit = 6 * shake * math.sin(g.t * 34)
        K.icon(c, "book", mx + jit, my, 130, K.GREEN, 1, 0.8, 0)
        if g.since(8) > 0:
            for sx, (hx, hy) in ((1, ja["head"]), (-1, jk["head"])):
                a = clamp01(g.since(8) / 0.2)
                for k in range(3):
                    ang = math.radians(-60 + k * 30) if sx > 0 else math.radians(-120 - k * 30)
                    K.seg(c, hx + 70 * math.cos(ang), hy + 70 * math.sin(ang), hx + 95 * math.cos(ang),
                          hy + 95 * math.sin(ang), K.RED, 6, a)

    return fn


# ---------------------------------------------------------------- 11–12 提线木偶

BAR = (540, 410)
P_UP1 = dict(K.POSES["stand"], la1=150, la2=20, head=-6)
P_UP2 = dict(P_UP1, ra1=-150, ra2=-20)
P_LIMP = dict(lean=0, head=16, la1=146, la2=34, ra1=-146, ra2=-34, ll1=3, ll2=0, rl1=-3, rl2=0)
P_FREE = dict(lean=2, head=4, la1=12, la2=10, ra1=-12, ra2=10, ll1=3, ll2=0, rl1=-3, rl2=0)


def control_bar(c, x, y, alpha=1.0, rot=0.0):
    with K.at(c, x, y, rot):
        with K.paper(c, alpha, 0.8):
            K.rr(c, 0, 0, 320, 20, 10, WOOD)
            K.rr(c, 0, 18, 20, 110, 10, K.shade(WOOD, 0.15))
            for dx in (-160, 160):
                K.dot(c, dx, 0, 14, K.shade(WOOD, 0.3))


def strings(hero, bar_beat=None, cut_beat=None):
    """提线：从控制杆的两端和中间连到主角的近手、远手、头顶。cut_beat 拍剪断。"""

    def fn(c, g, t, d):
        if bar_beat is not None:
            f = fall(g, bar_beat, 260, 0.35)
            if f is None:
                return
            dy = f[0]
        else:
            dy = 0.0
        bx, by = BAR[0], BAR[1] + dy
        j = fig_at(hero, g)
        anchors = ((bx + 160, by), (bx - 160, by), (bx, by + 125))
        targets = (j["near"], j["far"], j["top"])
        cut = g.since(cut_beat) if cut_beat is not None else -1
        cut_y = 560
        up = 0.0
        if cut >= 0:
            up = ease_in(clamp01(cut / 0.7)) * 420
        a_bar = 1 - clamp01((cut - 0.3) / 0.4) if cut >= 0 else 1.0
        for (ax, ay), (tx, ty) in zip(anchors, targets):
            if cut < 0:
                K.seg(c, ax, ay, tx, ty, K.INK2, 3, 0.9)
            else:
                q = (cut_y - ay) / max(1, ty - ay)
                mx = lerp(ax, tx, q)
                K.seg(c, ax, ay - up, mx, cut_y - up, K.INK2, 3, 0.9 * a_bar)
                drop = clamp01(cut / 0.5)
                lo = lerp(cut_y, ty - 30, ease_in(drop))
                K.seg(c, lerp(mx, tx, ease_in(drop)), lo, tx, ty, K.INK2, 3, 0.9 * (1 - drop))
        if a_bar > 0:
            control_bar(c, bx, by - up, a_bar, 0)
        if 0 <= cut < 0.25:
            K.seg(c, 330, cut_y, 760, cut_y, K.PAPER, 10 * (1 - cut / 0.25))
            K.burst(c, 540, cut_y, cut, ACC, 40, 180, 10, 7)

    return fn


def scissors(c, g, t, d):
    """剪刀：第 2 拍从右侧飞入，第 4 拍合拢剪断。"""
    k = ease_out(clamp01(g.since(2) / 0.6))
    if k <= 0:
        return
    out = clamp01(g.since(5) / 0.5)
    x = lerp(1150, 830, k) + 400 * ease_in(out)
    y = 560
    snap = clamp01(g.since(3.6) / 0.4)
    ang = lerp(26, 2, ease_in(snap))
    with K.at(c, x, y, 0, 1):
        with K.paper(c, 1 - out, 0.9):
            for sgn in (1, -1):
                with K.at(c, 0, 0, sgn * ang):
                    K.poly(c, [(0, -8 * sgn), (-230, -2 * sgn), (0, 10 * sgn)], "#B8BEC8")
                    K.ring(c, 64, sgn * 34, 30, ACC, 14)
            K.dot(c, 0, 0, 9, K.DARK)


def free_glow(c, g, t, d):
    """剪断后：断线落在脚边；第 8 拍主角欢呼，身后亮起光、纸屑飞起。"""
    k = clamp01((g.since(4) - 0.45) / 0.3)
    if k > 0:
        for i, x0 in enumerate((420, 560, 660)):
            path = skia.Path()
            path.moveTo(x0, GROUND - 2)
            for j in range(1, 7):
                path.lineTo(x0 + j * 14, GROUND - 2 - 10 * (j % 2) - 4 * math.sin(i + j))
            c.drawPath(path, K.paint(K.INK2, 0.7 * k, 3))
    a = clamp01(g.since(8) / 0.5)
    if a > 0:
        K.spotlight(c, 540, 860, 420, ACC, 0.22 * a)
        K.ripple(c, 540, 820, g.since(8), ACC, 360, 8, 0.7, 0.9)
        K.confetti(c, 540, 760, g.since(8), [ACC, K.GOLD, K.GREEN, K.HERO], 30, 5)


# ---------------------------------------------------------------- 14 轻快地走

def pops(g):
    for (x, y), b in (((150, 760), 3), ((320, 640), 4)):
        K.burst(g.c, x, y, g.since(b), K.INK3, 30, 110, 8, 6)


# ---------------------------------------------------------------- 组装

def build() -> Episode:
    # 7 牵马的人
    leader = Fig(380, GROUND, 290, at=0, enter="none", hair="short", mood="calm", pose="stand",
                 moves=[(1, dict(x=555, dur=2.4)),
                        (6, dict(pose="point", mood="open", sfx="wood_high", note="人指着水，示意马喝")),
                        (10, dict(face=-1, pose="shrug", mood="flat", sfx="shaker", note="马不喝，人转身摊手"))])
    # 3 背着气泡的主角
    carrier = Fig(610, GROUND, 350, at=0, enter="rise", hair="short", mood="worried", pose=BURDEN1,
                  moves=[(2, dict(pose=BURDEN2, mood="sad")), (4, dict(pose=BURDEN3))])
    # 6 打分的人
    judge1 = Fig(720, GROUND, 290, at=0, color=K.OTHER, face=-1, mood="flat", hair="bun",
                 moves=[(6, dict(pose="fist"))])
    judge2 = Fig(900, GROUND, 300, at=0.5, color=K.OTHER3, face=-1, mood="calm", hair="long",
                 moves=[(7, dict(pose="fist", mood="smile"))])
    # 10 拔河
    adult = Fig(330, GROUND, 360, at=0, color=K.OTHER2, mood="flat",
                moves=[(2, dict(pose=PULL, mood="angry")), (8, dict(pose=PULL2))])
    kid = Fig(760, GROUND, 230, at=0, color=K.OTHER3, face=-1, hair="bun", mood="calm",
              moves=[(2, dict(pose=PULL, mood="worried")), (8, dict(pose=PULL2, mood="sad"))])
    # 11–12 提线木偶
    puppet = Fig(540, GROUND, 340, at=0, hair="short", mood="calm",
                 moves=[(4, dict(pose=P_UP1, mood="worried")), (6, dict(pose=P_UP2)),
                        (9, dict(pose=P_LIMP, mood="flat"))])
    puppet2 = Fig(540, GROUND, 340, at=0, enter="none", hair="short", mood="flat", pose=P_LIMP,
                  moves=[(4, dict(pose=P_FREE, mood="surprised")),
                         (8, dict(pose="cheer", mood="happy", sfx="clap", note="主角舒展身体欢呼"))])
    # 13 担心卡
    asker = Fig(540, GROUND, 320, at=0, hair="short", mood="worried",
                moves=[(4, dict(pose="think")), (8, dict(pose="point", mood="open", sfx="rim",
                                                         note="主角把“担心”卡指向别人的箱子")),
                       (12, dict(pose="relax", mood="smile"))])

    shots = [
        Shot(3, "发了条朋友圈，|一直刷新看有没有人点赞。", "情境演绎", [
            Custom(phone_feed, x=660, y=780, at=0, enter="pop", note="大手机"),
            Fig(300, GROUND, 350, at=0, hair="short", mood="calm",
                moves=[(2.3, dict(pose="reach", mood="worried")), (3, dict(pose="point")),
                       (5.3, dict(pose="reach")), (6, dict(pose="point", mood="sad")),
                       (8.3, dict(pose="reach")), (9, dict(pose="cheer", mood="surprised"))]),
        ], draw=ground, hits=[(3, "wood_high", 0.9, "第一次下拉刷新：点赞 0"), (6, "wood_low", 0.85, "再刷新：还是 0"),
                              (9, "bongo_high", 1.0, "第三次刷新：终于 1 个赞")],
            note="主角盯着大手机，点赞数 0、0、1 按拍跳动，主角焦虑地一遍遍下拉刷新"),
        Shot(3, "同事一句随口的话，|你琢磨了一整晚。", "情境演绎", [
            Custom(night_window, x=820, y=490, at=0, enter="fade"),
            Custom(lambda c, g, t, d: K.memory(c, 0, 0, 300, 250, colleague_scene, 1, -5, 1, "白天"),
                   x=245, y=520, at=0, enter="pop", note="白天同事那句话"),
            Custom(bed, x=420, y=GROUND, at=0, enter="none"),
            Fig(575, GROUND, 320, at=0, enter="none", pose="sit", hair="short", mood="calm",
                moves=[(2, dict(mood="worried", look=0.5)),
                       (9, dict(pose=SIT_COVER, mood="sad", look=0.0, sfx="tom", note="主角抱头"))]),
            Bubble("他是不是|对我有意见？", 600, 718, 40, at=2, think=True, tail=(-0.1, 1), sfx="wood_high",
                   note="脑中冒出：他是不是对我有意见？"),
            Bubble("？", 400, 800, 40, at=5, think=True, tail=(0.6, 1), sfx="shaker", note="更多问号冒出"),
            Bubble("？", 790, 800, 40, at=6, think=True, tail=(-0.6, 1)),
            Bubble("？", 470, 560, 34, at=7, think=True, tail=(0.4, 1)),
        ], draw=ground, note="夜里月亮划过窗口，主角坐在床边，脑中的思考气泡一个个冒出"),
        Shot(2, "我们总在替|别人的想法操心。", "情境演绎", [
            carrier,
            Custom(burden(carrier), at=0, enter="fade"),
            Custom(sweat, x=790, y=800, at=6, enter="none"),
        ], draw=ground, text_beat=0, hits=[(2, "wood_low", 0.9, "第二个气泡压上，主角腰一弯"),
                                           (4, "tom", 0.9, "第四个气泡压上，腰更弯了"),
                                           (6, "shaker", 0.7, "主角冒汗")],
            note="主角背着一摞“别人的想法”气泡，像沉重的行李，越压越弯"),
        Shot(3, "先分清：|这是谁的课题？", "岸见一郎阐释", [
            Big("课题分离", 540, 520, 150, at=0, sfx="kick", sub="separation of tasks", note="概念落版（音乐 drop）"),
            Custom(venn, x=540, y=900, at=0, enter="fade", sfx=None),
            Label("我的课题", 315, 1095, 32, at=6, fill=K.HERO, sfx="wood_high", note="两边各自标上名字"),
            Label("别人的课题", 765, 1095, 32, at=6.5, fill=K.OTHER2),
            Txt("日本阿德勒学派的方法，经《被讨厌的勇气》普及", 540, 1235, 28, at=7, font="sans_medium", color=K.INK2),
        ], hits=[(4, "rim", 1.0, "两个重叠的圆分开，中间的乱线消失")],
            note="drop 处“课题分离”砸下；两个重叠的圆（我 / 他人）分开，纠缠的乱线消失"),
        Shot(3, "看这个选择的后果，|最终由谁来承担。", "岸见一郎阐释", [
            Fig(150, GROUND, 290, at=0, hair="short", mood="calm",
                moves=[(4.2, dict(pose="point", mood="open")), (7, dict(pose="stand", mood="smile"))]),
            Fig(930, GROUND, 290, at=0, color=K.OTHER2, face=-1, mood="calm",
                moves=[(6.2, dict(pose="point", mood="smile")), (9, dict(pose="stand"))]),
            Custom(box_back, x=375, y=GROUND, at=0, enter="none", color=K.HERO, hits=(4,)),
            Custom(box_back, x=705, y=GROUND, at=0, enter="none", color=K.OTHER2, hits=(6,)),
            Custom(fly_card, at=2, enter="none", show=2, land=4, start=(540, 580), target=(375, GROUND - BOX_H - 6),
                   lines=["发不发？"], sfx="wood_high", note="“发不发”卡片弹出"),
            Custom(fly_card, at=4, enter="none", show=4, land=6, start=(540, 580), target=(705, GROUND - BOX_H - 6),
                   lines=["点不点赞？"]),
            Custom(box_front, x=375, y=GROUND, at=0, enter="pop", color=K.HERO, label="我的课题", hits=(4,)),
            Custom(box_front, x=705, y=GROUND, at=0.5, enter="pop", color=K.OTHER2, label="别人的课题", size=36,
                   hits=(6,)),
        ], draw=ground, hits=[(4, "bongo_low", 1.0, "“发不发”落进我的箱子"),
                              (6, "bongo_high", 1.0, "“点不点赞”落进别人的箱子")],
            note="两个箱子“我的课题”“别人的课题”；“发不发”落进我的（第 4 拍），“点不点赞”落进别人的（第 6 拍）"),
        Shot(3, "做什么，是你的课题；|怎么评价，是别人的课题。", "机制示意", [
            Custom(divider, at=1, enter="none", sfx="rim", note="虚线从上到下把舞台分成两半"),
            Custom(easel, x=370, y=GROUND, at=0, enter="pop"),
            Fig(170, GROUND, 320, at=0, hair="short", mood="calm", prop=brush,
                moves=[(2, dict(pose="point", mood="smile", sfx="wood_low", note="主角在画板上画画")),
                       (4, dict(pose="reach")), (5, dict(pose="point"))]),
            judge1, judge2,
            Custom(score_sign(judge1, 6, "60"), at=6, enter="none", sfx="wood_high", note="右边的人举起 60 分"),
            Custom(score_sign(judge2, 7, "95"), at=7, enter="none", sfx="bongo_high", note="另一个举起 95 分"),
            Label("你的课题", 300, 430, 34, at=3, fill=K.HERO),
            Label("别人的课题", 790, 430, 34, at=8, fill=K.OTHER2),
        ], draw=ground, note="虚线把舞台分成两半：左边主角画画，右边他人举着评分牌"),
        Shot(3, "可以把马带到水边，|但不能逼它喝水。", "谚语", [
            Custom(horse_scene, at=0, enter="none", person=leader, note="牵马到水边"),
            leader,
        ], draw=ground, hits=[(8, "bongo_low", 1.0, "马把头一甩，不喝")],
            note="人牵着一匹纸片马走到水边，马把头甩开不喝，人摊手"),
        Shot(2, "分离课题，|不等于冷漠。", "常见误解", [
            Custom(lambda c, g, t, d: gfx.stroke_path(c, K.curve_path((660, 760), (660, 1130)), K.INK3, 5, 0.6,
                                                      1.0, dash=(18, 14, 0)), at=0, enter="fade"),
            Custom(lambda c, g, t, d: K.seat(c, 800, GROUND, 170, 84, K.mix(K.LINE, K.INK3, 0.5)), at=0,
                   enter="none"),
            Fig(790, GROUND, 300, at=0, enter="none", pose="sit_sad", color=K.OTHER3, face=-1, mood="sad",
                hair="long", moves=[(5, dict(pose="sit", mood="smile", look=0.4))]),
            Fig(280, GROUND, 340, at=0, enter="none", hair="short", mood="calm",
                moves=[(1, dict(x=470, dur=0.9)),
                       (3, dict(pose="give", mood="smile", sfx="wood_high", note="主角朝对方伸出手"))]),
            Icon("heart", 660, 760, 90, color=ACC, at=5, enter="pop", sfx="bongo_high", note="对方抬头，一颗心亮起"),
        ], draw=ground, text_beat=0, note="界线还在，但主角走近、朝对方伸出手"),
        Shot(2, "可以帮忙，|但不替对方做决定。", "常见误解", [
            Custom(ledge, at=0, enter="none"),
            Fig(700, GROUND, 290, at=0, enter="none", color=K.OTHER3, face=-1, hair="long", mood="worried", look=0.6,
                moves=[(3, dict(pose="think", mood="calm")),
                       (4, dict(pose="reach", mood="smile", sfx="clap", note="对方自己决定接过梯子")),
                       (6, dict(pose="stand", face=1, look=0.8))]),
            Icon("ladder", 400, 980, 260, color=WOOD, at=0, enter="none", lift=0.8,
                 moves=[(2, dict(x=520, rot=-6)), (4, dict(x=650, rot=0)), (6, dict(x=800, y=975, rot=12))]),
            Fig(280, GROUND, 340, at=0, enter="none", hair="short", mood="calm",
                moves=[(2, dict(pose="give", mood="open", sfx="wood_low", note="主角递出梯子")),
                       (4, dict(pose="stand", mood="smile"))]),
            Icon("check", 700, 700, 90, color=K.GREEN, at=6, enter="pop", sfx="wood_high", gain=0.8,
                 note="梯子靠上台阶，对方自己往上爬"),
        ], draw=ground, text_beat=0, note="主角递出梯子，对方想了想自己接过（第 4 拍），靠上台阶"),
        Shot(3, "替别人做主，|关系会越绷越紧；", "机制示意", [
            adult, kid,
            Custom(tug(adult, kid), at=0, enter="fade"),
        ], draw=ground, hits=[(2, "bongo_low", 0.9, "大人一把抢书"), (5, "tom", 0.85, "绳子绷紧"),
                              (8, "frame", 0.9, "越绷越紧，两人都冒火"), (10, "rim", 0.8, "绳子剧烈抖动")],
            note="大人抢孩子手里的书，两人之间的绳子越绷越紧、抖动"),
        Shot(3, "把自己的事交给别人评判，|人就不自由。", "机制示意", [
            puppet,
            Custom(strings(puppet, bar_beat=2), at=1, enter="none"),
            Label("别人的评价", 850, 410, 30, at=3, fill=K.INK2),
        ], draw=ground, hits=[(2, "wood_low", 0.9, "控制杆落下，提线拴住主角"),
                              (4, "wood_high", 0.9, "右手被提起"), (6, "bongo_high", 0.85, "左手也被提起"),
                              (9, "bongo_low", 0.8, "主角被吊着，垂头丧气")],
            note="主角的手脚被上方“别人的评价”控制杆的提线吊着，像提线木偶"),
        Shot(4, "“自由就是|被别人讨厌。”", "岸见一郎阐释", [
            Custom(free_glow, at=4, enter="none"),
            puppet2,
            Custom(strings(puppet2, cut_beat=4), at=0, enter="none"),
            Label("别人的评价", 850, 410, 30, at=0, enter="none", fill=K.INK2, out=4),
            Custom(scissors, at=2, enter="none", sfx="shaker", note="剪刀从右边飞来"),
            Txt("不是去招人讨厌，而是不再为了不被讨厌而活", 540, 1235, 30, at=9, font="sans_medium", color=K.INK2),
        ], draw=ground, cut=True, cam=(1.035, 1.05), hits=[(4, "rim", 1.0, "提线被剪断")],
            note="第 4 拍提线被剪断，第 8 拍主角舒展欢呼；底部小字说明这句话的意思"),
        Shot(4, "下次焦虑时问：|这个结果，最终由谁承担？", "小练习", [
            asker,
            Custom(box_back, x=210, y=GROUND, at=0, enter="none", color=K.HERO, hits=()),
            Custom(box_back, x=870, y=GROUND, at=0, enter="none", color=K.OTHER2, hits=(10,)),
            Custom(fly_card, at=2, enter="none", show=2, land=10, fly=0.6, start=(540, 600),
                   target=(870, GROUND - BOX_H - 6), hold=(5.5, 470), shake=2.5,
                   lines=["他会不会", "不高兴？"], size=44, accent=ACC, sfx="wood_high", note="“担心”卡悬在空中"),
            Custom(box_front, x=210, y=GROUND, at=0, enter="pop", color=K.HERO, label="我的课题", hits=()),
            Custom(box_front, x=870, y=GROUND, at=0.5, enter="pop", color=K.OTHER2, label="别人的课题", size=36,
                   hits=(10,)),
        ], draw=ground, hits=[(10, "bongo_low", 1.0, "“担心”卡落进别人的箱子")],
            note="一张“担心”卡悬在空中犹豫，主角想了想，把它指向“别人的课题”箱子"),
        Shot(2, "敢于被讨厌，|才能活出自己。", "岸见一郎阐释", [
            Fig(140, GROUND, 290, at=0, enter="none", color=K.OTHER, mood="flat", hair="bun"),
            Fig(310, GROUND, 300, at=0, enter="none", color=K.OTHER2, mood="flat", face=1),
            Bubble("？", 150, 760, 44, at=0, enter="none", out=3, tail=(0.2, 1)),
            Bubble("？", 320, 640, 44, at=0, enter="none", out=4, tail=(0.0, 1)),
            Fig(470, GROUND, 330, at=0, enter="none", hair="short", mood="smile", stride=1.3,
                moves=[(1, dict(x=830, dur=2.0, mood="happy")),
                       (6, dict(pose="wave", sfx="bongo_high", note="主角回头挥手"))]),
            Icon("sun", 860, 520, 170, color=K.GOLD, at=2, enter="pop", sfx="wood_high", gain=0.8,
                 p=lambda g, t: t * 0.3, note="太阳出来"),
        ], draw=ground, text_beat=0, over=pops, hits=[(4, "shaker", 0.7, "身后的问号气泡破掉")],
            note="主角轻快地往前走，身后别人的“？”气泡一个个破掉、淡去"),
        end_shot(["岸见一郎、古贺史健（2013）《被讨厌的勇气》第三夜",
                  "野田俊作显彰财团：「課題の分離」说明（adler.or.jp）"],
                 "07 鼓励：为什么“你真棒”，不一定是最好的夸奖？"),
    ]
    return Episode(6, "tasks", "课题分离", "别人怎么看你，是谁的课题？", ACC, shots,
                   refs=["岸见一郎、古贺史健（2013）《被讨厌的勇气》第三夜",
                         "野田俊作显彰财团：「課題の分離」说明（adler.or.jp）"],
                   publish_title="别人怎么看你，是谁的课题？｜阿德勒心理学06 课题分离",
                   hashtags="#阿德勒 #心理学 #课题分离 #被讨厌的勇气 #人际关系",
                   cover_title="别人怎么看你，|是【谁】的课题？", cover_sub="课题分离与被讨厌的勇气",
                   cover_shot=10, cover_t=5.0,
                   notes=[
                       "“课题分离”不是阿德勒原著术语：野田俊作显彰财团说明，它是野田俊作把德雷克斯“弄清是谁的责任”的思路改写为"
                       "“这是谁的课题”后形成的方法，由《被讨厌的勇气》第三夜普及。片中第 4 镜小字说明。",
                       "判断标准“这个选择带来的后果最终由谁承担”出自《被讨厌的勇气》第三夜。",
                       "“可以把马带到水边，但不能逼它喝水”作为谚语使用，不标注出处。",
                       "“自由就是被别人讨厌”是岸见一郎书中的话，不是阿德勒原话。",
                   ]).build()
