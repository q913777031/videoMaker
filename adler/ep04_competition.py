"""04 追求优越：你一直在和谁比赛？"""

import math

import skia

from engine import gfx
from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, ease_out_back, lerp

from . import kit as K
from .core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

ACC = "#2C8C84"
GROUND = 1130
TRACK = "#D49A7C"
STAGE = skia.Rect.MakeLTRB(60, 330, 1020, 1262)


def ground(g):
    K.ground(g.c, GROUND)


# ---------------------------------------------------------------- 跑步与跑道

def run_pose(ph, amp=1.35, lean=10):
    """跑步姿势：ph 以步为单位；手肘弯曲、身体前倾。"""
    d = K.walk(ph, amp)
    d["lean"] += lean
    d["la2"] = 80 + 10 * math.sin(ph * math.pi)
    d["ra2"] = 80 - 10 * math.sin(ph * math.pi)
    d["ll2"] -= 20
    d["rl2"] -= 20
    return d


def draw_runner(c, x, y, s, ph, color=K.HERO, face=1.0, mood="calm", hair=None, amp=1.35, lean=10, pose=None,
                alpha=1.0, lift=0.9):
    bounce = 0.035 * s * abs(math.sin(ph * math.pi)) * min(1.0, amp)
    p = pose if pose is not None else run_pose(ph, amp, lean)
    K.figure(c, x, y - bounce, s, p, color, K.SKIN, alpha, face, mood, hair, None, 0, lift)


def track_bg(g, speed=260.0, y0=1092, y1=1192, stop=None):
    """两条跑道；分道线的虚线随主角跑动向左滚动（stop 拍之后停住）。"""
    c = g.c
    t = g.t if stop is None else min(g.t, g.b(stop))
    K.rr(c, 540, (y0 + y1) / 2, 960, y1 - y0, 14, K.tint(TRACK, 0.25))
    for y in (y0 + 4, y1 - 4):
        K.seg(c, 70, y, 1010, y, K.PAPER, 4, 0.9)
    p = K.paint(K.PAPER, 0.95, 5)
    p.setPathEffect(skia.DashPathEffect.Make([46, 34], (t * speed) % 80))
    c.drawLine(74, (y0 + y1) / 2, 1006, (y0 + y1) / 2, p)


def sweat(c, x, y, t, n=3, alpha=1.0):
    for i in range(n):
        ph = (t * 1.8 + i / n) % 1.0
        xx = x + (i - 1) * 22 + 30 * ph
        yy = y - 10 + 40 * ph * ph
        path = skia.Path()
        path.moveTo(xx, yy - 12)
        path.quadTo(xx + 8, yy, xx, yy + 6)
        path.quadTo(xx - 8, yy, xx, yy - 12)
        c.drawPath(path, K.paint("#8FC3D9", alpha * (1 - ph)))


# ---------------------------------------------------------------- 镜 1：别人带着成就从身边跑过

PASSERS = [  # 超过主角的拍, 颜色, 发型, 标签, 道具
    (2, K.OTHER2, "cap", "升职了", "brief"),
    (4, K.OTHER3, "bun", "买房了", "house"),
]


def race_pass(c, g, el_t, d):
    hero_x, hero_y = 360, 1180
    ph = g.t * 2.3
    face = d.get("face", 1.0)
    # 超车的人在后一条跑道上（画在主角之前）
    c.save()
    c.clipRect(STAGE)
    for b, col, hair, lab, prop in PASSERS:
        x = hero_x + 40 + (g.t - g.b(b)) * 640
        if x < -200 or x > 1300:
            continue
        y, s = 1136, 300
        pp = g.t * 3.4 + b
        if prop == "house":
            p = run_pose(pp, 1.2, 6)
            p.update(la1=165, la2=5, ra1=-165, ra2=-5)
            draw_runner(c, x, y, s, pp, col, 1, "happy", hair, pose=p)
            K.icon(c, "house", x + 6, y - s * 1.32, 120, K.HERO, 1, 0.8, 0, 1, 1.0, K.GOLD)
            K.pill(c, x, y - s * 1.32 - 108, lab, 30, ACC, K.PAPER)
        else:
            draw_runner(c, x, y, s, pp, col, 1, "happy", hair)
            geo_hand = (x + 0.36 * s, y - 0.56 * s)
            K.icon(c, "brief", geo_hand[0] + 10, geo_hand[1] + 20, 96, K.DARK, 1, 0.6, 0, 1, 1.0, K.GOLD)
            K.pill(c, x, y - s * 1.12 - 56, lab, 30, ACC, K.PAPER)
    c.restore()
    mood = d.get("mood", "calm")
    draw_runner(c, hero_x, hero_y, 330, ph, K.HERO, face, mood, "short")
    if g.since(8) > 0:
        sweat(c, hero_x + 70, hero_y - 360, g.t, 3, clamp01(g.since(8) / 0.3))


def notice(c, g, el_t, d):
    """动态消息卡：头像 + 图标 + 一句话。"""
    def draw(c, w, h):
        K.dot(c, -w / 2 + 56, 0, 30, d["color"])
        K.icon(c, d["icon"], -w / 2 + 56, 2, 40, K.PAPER, 1, 0.0, 0, 1, 1.0, d["color"])
        K.text(c, d["who"], -w / 2 + 104, -20, 28, "sans_medium", K.INK3, 1, "left")
        K.text(c, d["text"], -w / 2 + 104, 22, 38, "serif", K.INK, 1, "left")
    K.card(c, 0, 0, 380, 124, K.PAPER, 1, 22, 1.0, d.get("tilt", 0), 1, None, draw)


# ---------------------------------------------------------------- 镜 2：排行榜上的名次一路下滑

RANK_COLORS = [K.OTHER, K.OTHER3, K.OTHER2, "#9C8FB0", K.OTHER, K.OTHER3, K.OTHER2]


def leaderboard(c, g, el_t, d):
    states = [2, 4, 7]
    k1 = ease_in_out(clamp01(g.since(2) / 0.4))
    k2 = ease_in_out(clamp01(g.since(5) / 0.4))
    hero_slot = lerp(lerp(states[0], states[1], k1), states[2], k2)
    w, h = 440, 520
    row_h = 52

    def slot_y(i):
        return -h / 2 + 108 + i * row_h

    def draw(c, w_, h_):
        K.text(c, "排行榜", 0, -h / 2 + 52, 38, "serif_black", K.INK)
        for i in range(8):
            K.text(c, str(i + 1), -w / 2 + 44, slot_y(i), 30, "black", K.INK3)
        for j in range(7):
            s0 = j if j < states[0] else j + 1
            s1 = j if j < states[1] else j + 1
            s2 = j if j < states[2] else j + 1
            sl = lerp(lerp(s0, s1, k1), s2, k2)
            y = slot_y(sl)
            K.dot(c, -w / 2 + 104, y, 17, RANK_COLORS[j])
            K.rr(c, -w / 2 + 130 + (240 - 20 * j) / 2, y, 240 - 20 * j, 18, 9, K.LINE)
        y = slot_y(hero_slot)
        K.rr(c, 14, y, w - 50, row_h - 6, 14, K.tint(ACC, 0.2))
        K.dot(c, -w / 2 + 104, y, 19, K.HERO)
        K.text(c, "我", -w / 2 + 104, y, 24, "serif_black", K.PAPER)
        K.rr(c, -w / 2 + 130 + 70, y, 140, 18, 9, ACC)
        for b, txt in ((2, "↓2"), (5, "↓3")):
            dt = g.since(b)
            if 0 <= dt <= 1.6:
                a = clamp01(dt / 0.15) * (1 - clamp01((dt - 1.2) / 0.4))
                K.pill(c, w / 2 - 50, y, txt, 26, K.RED, K.PAPER, a)

    K.card(c, 0, 0, w, h, K.PAPER, 1, 22, 1.0, 2, 1, ACC, draw)


def anxious_runner(c, g, el_t, d):
    b2, b5 = g.b(2), g.b(5)
    t = g.t
    ph = 2.2 * t + 0.7 * max(0, t - b2) + 1.0 * max(0, t - b5)
    mood = "calm" if t < b2 else "worried" if t < b5 else "sad"
    draw_runner(c, 0, 0, 320, ph, K.HERO, 1, mood, "short", amp=1.35 + 0.15 * (t > b5), lean=10 + 6 * (t > b5))
    if g.since(8) > 0:
        sweat(c, 70, -350, t, 4, clamp01(g.since(8) / 0.3))
        for i in range(3):
            K.seg(c, -120 - i * 26, -260 + i * 50, -190 - i * 26, -260 + i * 50, K.INK3, 6, 0.6)


# ---------------------------------------------------------------- 镜 3：领先时回头张望，第 4 拍摔倒

SIT_GROUND = dict(lean=10, head=16, la1=110, la2=120, ra1=100, ra2=130, ll1=84, ll2=-30, rl1=70, rl2=-40, seat=0.07)
PRONE = dict(lean=0, head=-25, la1=170, la2=0, ra1=158, ra2=6, ll1=12, ll2=-20, rl1=-8, rl2=-30)


def lead_and_fall(c, g, el_t, d):
    t = g.t
    b4 = g.b(4)
    # 后面的追赶者
    for i, (x0, col, hair) in enumerate(((150, K.OTHER, "bun"), (330, K.OTHER2, None))):
        x = x0 + 40 * math.sin(t * 0.8 + i) + max(0, t - b4 - 0.3) * (520 + 60 * i)
        draw_runner(c, x, 1136, 290, t * 3.1 + i * 0.5, col, 1, "flat", hair)
    hx, hy = 600, 1180
    face = d.get("face", 1.0)
    # 头顶的“第1名”：摔倒时掉下来
    kf = clamp01((t - b4) / 0.5)
    tag_x = hx + 10 + 160 * kf
    tag_y = hy - 330 * 1.12 - 50 + 380 * ease_in(kf)
    if kf < 1:
        with K.at(c, tag_x, tag_y, 70 * kf):
            K.pill(c, 0, 0, "第1名", 32, K.GOLD, K.PAPER, 1 - kf)
    if t < b4:
        draw_runner(c, hx, hy, 330, t * 2.6, K.HERO, face, "worried" if face < 0.5 else "calm", "short")
        return
    k = clamp01((t - b4) / 0.32)
    up = ease_in_out(clamp01(g.since(6) / 0.45))
    rot = 82 * ease_in(k) * (1 - up)
    x = hx + 40 * ease_out(k)
    p = K.blend(run_pose(b4 * 2.6), PRONE, k) if up <= 0 else K.blend(PRONE, SIT_GROUND, up)
    with K.at(c, x, hy, rot):
        K.figure(c, 0, 0, 330, p, K.HERO, K.SKIN, 1, 1, "sad" if k > 0.5 else "surprised", "short", None, 0, 0.9)
    dt = t - b4 - 0.3
    if 0 <= dt <= 0.6:
        for i in range(7):
            ang = math.radians(-170 + i * 26)
            r = 60 + 120 * ease_out(dt / 0.6)
            K.dot(c, x + 330 + math.cos(ang) * r * 0.6, hy - 40 + math.sin(ang) * r * 0.4, 14 * (1 - dt / 0.6),
                  K.tint(TRACK, 0.2), 0.9)
    if up > 0:
        for sx in (-1, 1):
            K.dot(c, x + 40 + sx * 30, hy - 250, 12, K.RED, 0.35 * up)


# ---------------------------------------------------------------- 镜 4：小芽与孩子

def star_twinkle(c, g, el_t, d):
    k = ease_out_back(clamp01(el_t / 0.4), 2)
    r = 46 * k * (1 + 0.08 * math.sin(g.t * 5))
    K.spotlight(c, 0, 0, 160, K.GOLD, 0.4 * k)
    K.star(c, 0, 0, r, K.GOLD, 1, 5, 0.45, 8 * math.sin(g.t * 2))


# ---------------------------------------------------------------- 镜 5：岔路口

def fork(c, g, el_t, d):
    p = ease_out(clamp01(el_t / 0.7))
    col = K.tint(ACC, 0.62)
    stem = skia.Path()
    stem.moveTo(540, 1195)
    stem.lineTo(540, lerp(1195, 960, p))
    c.drawPath(stem, K.paint(col, 1, 110))
    if p > 0.5:
        q = (p - 0.5) * 2
        for tx in (260, 820):
            path = skia.Path()
            path.moveTo(540, 980)
            path.quadTo(540, 860, lerp(540, tx, q), lerp(980, 720, q))
            c.drawPath(path, K.paint(col, 1, 90))
    pp = K.paint(K.PAPER, 0.9, 7)
    pp.setPathEffect(skia.DashPathEffect.Make([28, 24], 0))
    c.drawLine(540, 1190, 540, lerp(1190, 980, p), pp)


# ---------------------------------------------------------------- 镜 6：理想的自己（条纹虚影）

def ghost_figure(c, x, y, s, pose="stand", face=1, alpha=1.0, color=ACC, mood="smile", glow=0.0, t=0.0):
    if glow > 0:
        K.spotlight(c, x, y - s * 0.55, s * 0.95, color, 0.35 * glow)
    c.saveLayer(skia.Rect.MakeLTRB(x - s, y - s * 1.4, x + s, y + s * 0.2), skia.Paint(Alphaf=alpha))
    K.figure(c, x, y, s, pose, K.tint(color, 0.15), K.tint(color, 0.5), 1, face, mood, "short",
             K.shade(color, 0.2), 0.006 * math.sin(t * 2.6), 0.0)
    cut = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK, BlendMode=skia.BlendMode.kDstOut, StrokeWidth=7,
                     Style=skia.Paint.kStroke_Style)
    for yy in range(int(y - s * 1.4), int(y + s * 0.2), 17):
        c.drawLine(x - s, yy, x + s, yy - s * 0.25, cut)
    c.restore()


def ideal_self(c, g, el_t, d):
    ghost_figure(c, 0, 0, d["s"], "wave", -1, 1.0, ACC, "smile", clamp01(d.get("glow", 0.0)), g.t)


# ---------------------------------------------------------------- 镜 7：各走各的路

LANES = [  # 路面 y, 身高, [(起点 x, 终点 x, 颜色, 发型, 是否主角)]
    (650, 165, [(260, 380, K.OTHER, "bun", False), (700, 800, K.OTHER2, None, False)]),
    (810, 210, [(520, 650, "#9C8FB0", "long", False), (860, 950, K.OTHER3, "cap", False)]),
    (975, 255, [(160, 300, K.HERO, "short", True), (640, 760, K.OTHER, None, False)]),
    (1150, 300, [(420, 540, K.OTHER3, "short", False), (800, 900, K.OTHER2, "bun", False)]),
]


def lanes(g):
    c = g.c
    for i, (y, s, _) in enumerate(LANES):
        p = ease_out(clamp01(g.since(i * 0.5) / 0.6))
        if p <= 0:
            continue
        w = 6 + i * 3
        K.rr(c, 540, y + 6, 900 * p, w * 2, w, K.tint(ACC, 0.55 - 0.08 * i))


# ---------------------------------------------------------------- 镜 8：闪电

def lightning(c, g, el_t, d):
    k = clamp01(el_t / 0.12)
    flick = 0.75 + 0.25 * math.sin(g.t * 40)
    pts = [(-20, -150), (40, -150), (5, -40), (50, -40), (-40, 150), (-5, 10), (-50, 10)]
    with K.paper(c, k * flick, 1.0):
        K.poly(c, pts, K.GOLD)
    K.burst(c, 0, 0, el_t, K.GOLD, 90, 230, 12, 8)


# ---------------------------------------------------------------- 镜 9：乌云

def storm(c, g, el_t, d):
    k = ease_out_back(clamp01(el_t / 0.4), 1.4)
    with K.at(c, 0, 0, 0, k):
        K.icon(c, "cloud", 0, 0, 340, K.DARK, 1, 0.9)
        K.icon(c, "cloud", -150, 40, 200, K.shade(K.DARK, 0.1), 1, 0.6)
        K.icon(c, "cloud", 160, 46, 220, K.mix(K.DARK, K.INK2, 0.3), 1, 0.6)
    dt = g.since(6)
    if 0 <= dt <= 0.5:
        a = 1 - dt / 0.5
        K.poly(c, [(-10, 60), (30, 60), (5, 130), (35, 130), (-25, 230), (-5, 150), (-30, 150)], K.GOLD, a)
    for i in range(6):
        ph = (g.t * 1.6 + i / 6) % 1
        K.seg(c, -150 + i * 60, 90 + ph * 160, -158 + i * 60, 110 + ph * 160, "#8FA9B8", 4, 0.7 * (1 - ph) * k)


# ---------------------------------------------------------------- 镜 10：两个罐子

def jar(c, g, el_t, d):
    level = clamp01(d.get("level", 0.3))
    w, h = 210, 290
    col = d.get("liquid", ACC)
    with K.paper(c, 1, 0.6):
        K.rr(c, 0, -h / 2, w, h, 30, K.tint("#CFE0E4", 0.35))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 + 10, -h + 10, w - 20, h - 20), 24, 24),
                doAntiAlias=True)
    lh = (h - 20) * level
    wob = 6 * math.sin(g.t * 3)
    path = skia.Path()
    path.moveTo(-w / 2, -10 - lh + wob)
    path.quadTo(0, -10 - lh - wob, w / 2, -10 - lh + wob)
    path.lineTo(w / 2, 0)
    path.lineTo(-w / 2, 0)
    path.close()
    c.drawPath(path, K.paint(col, 0.9))
    c.restore()
    c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h, w, h), 30, 30, K.paint("#A9C2CA", 1, 6))
    K.seg(c, -w / 2 + 34, -h + 50, -w / 2 + 34, -h + 150, K.PAPER, 10, 0.7)
    K.rr(c, 0, -h - 12, w * 0.8, 28, 10, K.shade("#A9C2CA", 0.2))
    for b in d.get("drops", ()):
        T = g.b(b)
        k = (g.t - (T - 0.35)) / 0.35
        if 0 <= k <= 1:
            yy = lerp(-h - 260, -10 - lh, ease_in(k))
            K.dot(c, 0, yy, 22, K.GOLD)
            K.dot(c, -6, yy - 6, 7, K.tint(K.GOLD, 0.6))
        dt = g.t - T
        if 0 <= dt <= 0.4:
            K.ripple(c, 0, -10 - lh, dt, K.PAPER, 90, 5, 0.9, 0.4)
    sp = d.get("sparkle")
    if sp is not None:
        dt = g.since(sp)
        if 0 <= dt <= 0.9:
            for i in range(4):
                a = i * math.pi / 2 + 0.6
                r = 110 + 40 * ease_out(dt / 0.9)
                K.star(c, math.cos(a) * r, -h / 2 + math.sin(a) * r, 18 * (1 - dt / 0.9), K.GOLD, 1, 4)


def neq(c, g, el_t, d):
    k = ease_out_back(clamp01(el_t / 0.35), 2)
    with K.at(c, 0, 0, 0, k):
        K.rr(c, 0, -22, 110, 18, 9, K.INK)
        K.rr(c, 0, 22, 110, 18, 9, K.INK)
        K.seg(c, 30, -70, -30, 70, K.RED, 16)


# ---------------------------------------------------------------- 镜 12：台阶上的昨天与今天

STEP_W, STEP_H, STEP_X = 170, 80, 180


def step_top(i):
    return STEP_X + STEP_W * (i + 0.5), GROUND - STEP_H * (i + 1)


def yesterday(c, g, el_t, d):
    x, y = step_top(0)
    K.figure(c, x - d["x"], y - d["y"], 300, "stand", K.tint(K.HERO, 0.55), K.tint(K.SKIN, 0.4), 0.55, 1, "calm",
             "short", K.tint(K.HERO, 0.3), 0.006 * math.sin(g.t * 2.6), 0.0)


def ruler(c, g, el_t, d):
    p = ease_out(clamp01(el_t / 0.4))
    x = STEP_X + STEP_W * 2 + 26
    y0, y1 = GROUND - STEP_H, GROUND - STEP_H * 2
    K.seg(c, x, y0, x, lerp(y0, y1, p), ACC, 8)
    for yy in (y0, lerp(y0, y1, p)):
        K.seg(c, x - 16, yy, x + 16, yy, ACC, 8)
    if p > 0.6:
        K.pill(c, x + 70, (y0 + y1) / 2, "+1", 40, ACC, K.PAPER, (p - 0.6) / 0.4)


# ---------------------------------------------------------------- 镜 13：清单

ROWS = [("多跑了一次步", 2, 4), ("早睡了两天", 6, 8), ("主动问了一个问题", 10, 12)]


def pencil(c, x, y, rot=-35):
    with K.at(c, x, y, rot):
        with K.paper(c, 1, 0.6):
            K.rr(c, 0, -60, 26, 110, 4, K.GOLD)
            K.rr(c, 0, -118, 26, 18, 4, "#E58C8C")
            K.poly(c, [(-13, -5), (13, -5), (0, 22)], "#F1D6B8")
            K.poly(c, [(-4, 14), (4, 14), (0, 22)], K.INK)


def checklist(c, g, el_t, d):
    w, h = 780, 560
    pen = None

    def draw(c, w_, h_):
        nonlocal pen
        K.text(c, "这周多做到的", 0, -h / 2 + 62, 40, "serif_black", ACC)
        K.seg(c, -w / 2 + 50, -h / 2 + 110, w / 2 - 50, -h / 2 + 110, K.LINE, 4)
        for i, (txt, b_in, b_tick) in enumerate(ROWS):
            y = -h / 2 + 190 + i * 120
            K.rr_stroke(c, -w / 2 + 90, y, 48, 48, 10, K.INK2, 5)
            K.seg(c, -w / 2 + 140, y + 34, w / 2 - 60, y + 34, K.LINE, 3)
            k = clamp01(g.since(b_in) / 0.6)
            n = int(round(len(txt) * k))
            if n > 0:
                K.text(c, txt[:n], -w / 2 + 140, y, 42, "serif", K.INK, 1, "left")
            if 0 < k < 1:
                pen = (-w / 2 + 140 + K.text_w(txt[:n], 42, "serif") + 10, y + 10)
            pt = clamp01(g.since(b_tick) / 0.3)
            if pt > 0:
                path = skia.Path()
                path.moveTo(-w / 2 + 70, y)
                path.lineTo(-w / 2 + 86, y + 18)
                path.lineTo(-w / 2 + 118, y - 22)
                gfx.stroke_path(c, path, K.GREEN, 10, 1.0, ease_out(pt))
                K.burst(c, -w / 2 + 90, y, g.since(b_tick), K.GREEN, 40, 90, 8, 5)

    K.card(c, 0, 0, w, h, K.PAPER, 1, 22, 1.0, -1, 1, ACC, draw)
    if pen:
        pencil(c, pen[0], pen[1])


# ---------------------------------------------------------------- 镜 14：小路与日出

def sunrise_bg(g):
    c = g.c
    sun_y = lerp(880, 660, ease_out(g.span(1, 5)))
    K.spotlight(c, 700, sun_y, 420, K.GOLD, 0.35)
    K.icon(c, "sun", 700, sun_y, 230, K.GOLD, 1, 0.4, 0, 1, g.t * 0.3)
    panel = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(72, 600, 1008, 1196), 28, 28)
    c.save()
    c.clipRRect(panel, doAntiAlias=True)
    with K.paper(c, 1, 0.5):
        hill = skia.Path()
        hill.moveTo(70, 860)
        hill.quadTo(300, 760, 560, 830)
        hill.quadTo(820, 740, 1010, 820)
        hill.lineTo(1010, 1200)
        hill.lineTo(70, 1200)
        hill.close()
        c.drawPath(hill, K.paint(K.tint(ACC, 0.7)))
    with K.paper(c, 1, 0.4):
        hill2 = skia.Path()
        hill2.moveTo(70, 960)
        hill2.quadTo(400, 880, 700, 940)
        hill2.quadTo(880, 970, 1010, 930)
        hill2.lineTo(1010, 1200)
        hill2.lineTo(70, 1200)
        hill2.close()
        c.drawPath(hill2, K.paint(K.tint(ACC, 0.55)))
    p = ease_out(clamp01(g.t / 1.0))
    path = skia.Path()
    path.moveTo(330, 1200)
    path.cubicTo(420, 1090, 760, 1060, 640, 960)
    path.quadTo(560, 900, 690, 850)
    gfx.stroke_path(c, path, K.tint(TRACK, 0.35), 64, 1.0, p)
    gfx.stroke_path(c, path, K.PAPER, 6, 0.8, p, dash=(22, 22, 0))
    c.restore()


# ---------------------------------------------------------------- 分镜

def build() -> Episode:
    shots = [
        # 1：跑道上，别人带着“升职”“买房”从身边超过去
        Shot(3, "同学升职了，|朋友买房了……", "情境演绎", [
            Custom(race_pass, at=0, enter="fade", face=1.0, mood="calm",
                   moves=[(5, dict(mood="worried")),
                          (6, dict(face=-1.0, dur=0.25, sfx="rim", gain=0.8, note="主角回头张望")),
                          (7.5, dict(face=1.0, mood="sad", dur=0.25))]),
            Custom(notice, x=640, y=480, at=2, enter="pop", color=K.OTHER2, icon="brief", who="同学", text="升职了！",
                   tilt=-2),
            Custom(notice, x=700, y=650, at=4, enter="pop", color=K.OTHER3, icon="house", who="朋友", text="买房了！",
                   tilt=2),
        ], draw=lambda g: track_bg(g), hits=[(2, "wood_high", 0.85, "同学拿着公文包超过去"),
                                             (4, "wood_low", 0.85, "朋友举着房子超过去")],
            note="跑道上，同学拿着公文包、朋友举着房子从主角身边超过去；主角回头张望，越跑越慌"),

        # 2：排行榜名次一路下滑
        Shot(3, "人生好像一场|永远跑不完的比赛。", "情境演绎", [
            Custom(leaderboard, x=740, y=600, at=0, enter="pop"),
            Custom(anxious_runner, x=290, y=1176, at=0, enter="fade"),
        ], draw=lambda g: track_bg(g, 340), hits=[(2, "wood_high", 0.85, "名次从第 3 掉到第 5"),
                                                  (5, "wood_low", 0.85, "名次掉到第 8"),
                                                  (8, "bongo_low", 0.8, "主角满头大汗地加速")],
            note="排行榜上主角的名次按拍下滑（3→5→8），主角越跑越急、满头大汗"),

        # 3：领先时回头张望，第 4 拍摔倒
        Shot(2, "赢了怕被追上，|输了觉得丢人。", "情境演绎", [
            Custom(lead_and_fall, at=0, enter="fade", face=1.0,
                   moves=[(1, dict(face=-1.0, dur=0.22, sfx="wood_high", gain=0.8, note="领先时回头张望")),
                          (2.6, dict(face=1.0, dur=0.22))]),
        ], draw=lambda g: track_bg(g, 300, stop=4), text_beat=1,
            hits=[(4, "tom", 0.95, "主角摔倒"), (6, "shaker", 0.75, "别人从身边跑过，他捂着脸坐起来")],
            note="主角领先时频频回头，第 4 拍摔倒；后面的人跑过去，他红着脸坐在跑道上"),

        # 4：drop——“追求优越”
        Shot(3, "想变得更好，|是人的天性。", "阿德勒原著", [
            Big("追求优越", 540, 500, 150, at=0, sfx="kick", sub="striving for superiority", note="概念落版（音乐 drop）"),
            Icon("sprout", 260, 1040, 220, at=2, enter="pop", sfx="wood_low", gain=0.8, note="小芽破土",
                 p=lambda g, t: clamp01(t / 1.6)),
            Fig(560, GROUND, 230, at=1, pose="crouch", color=K.OTHER, hair="bun", mood="calm",
                moves=[(4, dict(pose="stand", mood="open", dur=0.4, sfx="bongo_low", gain=0.85, note="孩子站了起来")),
                       (8, dict(pose="reach", mood="happy", look=0.8, sfx="bongo_high", gain=0.85,
                                note="孩子伸手去够星星"))]),
            Custom(star_twinkle, x=790, y=770, at=6, enter="none"),
        ], draw=ground, note="drop 处“追求优越”砸下；小芽破土，孩子从蹲着到站起，再伸手去够星星"),

        # 5：岔路口
        Shot(3, "问题不在想变好，|而在往哪个方向用力。", "阿德勒原著 · 大意", [
            Custom(fork, at=0, enter="none"),
            Card(["【有用的一面】", "也对他人有益"], 255, 590, 38, at=2, accent=ACC, rot=-2, sfx="wood_high", gain=0.85,
                 note="左边路牌：有用的一面"),
            Card(["【无用的一面】", "只想压过别人"], 825, 590, 38, at=4, accent=K.INK3, hi=K.RED, rot=2, sfx="wood_low",
                 gain=0.85, note="右边路牌：无用的一面"),
            Fig(540, GROUND + 20, 300, at=0, enter="rise", hair="short", mood="calm",
                moves=[(6, dict(face=-1, look=0.5, dur=0.3)), (7, dict(face=1, dur=0.3)),
                       (8, dict(pose="think", mood="open", look=0.3, sfx="rim", gain=0.8, note="主角站在路口思考"))]),
            Icon("question", 660, 780, 90, color=ACC, at=8.5, enter="pop"),
        ], note="岔路口两块路牌：“有用的一面：也对他人有益” / “无用的一面：只想压过别人”，主角站在路口"),

        # 6：走向理想的自己
        Shot(3, "健全的比较对象，|是“理想的自己”。", "岸见一郎阐释", [
            Custom(ideal_self, x=800, y=GROUND, s=340, at=2, enter="fade", dur=0.6, glow=0.0, sfx="shaker",
                   gain=0.8, note="前方浮现一个条纹虚影：理想的自己",
                   moves=[(10, dict(glow=1.0, dur=0.4, sfx="bongo_high", gain=0.85, note="走近时虚影亮起"))]),
            Label("理想的自己", 820, 1130 - 340 * 1.08 - 100, 34, at=4, fill=ACC, sfx="wood_high", gain=0.8,
                  note="标签：理想的自己"),
            Arrow((330, 1180), (620, 1180), at=5, color=K.INK3, width=8, dash=(18, 14, 0)),
            Fig(210, GROUND, 330, at=0, hair="short", mood="calm",
                moves=[(6, dict(x=560, mood="smile", dur=2.1, sfx="wood_low", gain=0.8, note="主角迈步走向它")),
                       (10, dict(pose="wave", mood="happy"))]),
        ], draw=ground, note="主角朝前方一个条纹虚影走去，虚影标着“理想的自己”，走近时亮起"),

        # 7：每个人都在自己的路上
        Shot(3, "每个人都在自己的路上，|有人在前，有人在后。", "机制示意", [
            *[Fig(x0, y, s, at=1 if i < 2 else 3, color=col, hair=hair, mood="smile" if hero else "calm",
                  sfx=("wood_low" if i == 0 else "wood_high") if j == 0 and i in (0, 2) else None, gain=0.8,
                  note=("远处的人出现" if i == 0 else "近处的人出现") if j == 0 and i in (0, 2) else "",
                  moves=[(4, dict(x=x1, dur=4.2 + 0.3 * j + 0.2 * i, stride=0.8,
                                  **({"sfx": "bongo_low", "gain": 0.8, "note": "大家各自往前走"} if hero else {})))]
                  + ([(10, dict(pose="wave", mood="happy"))] if hero else []))
              for i, (y, s, people) in enumerate(LANES) for j, (x0, x1, col, hair, hero) in enumerate(people)],
        ], draw=lanes, hits=[(10, "shaker", 0.7, "主角朝前面的人挥挥手")],
            note="平地上四条各自的路，很多人各走各的，前后错落，没有终点线"),

        # 8：转身面对面，中间闪电
        Shot(2, "一旦把别人当对手，", "岸见一郎阐释", [
            Fig(330, GROUND, 340, at=0, hair="short", face=-1, mood="calm",
                moves=[(2, dict(face=1, pose="fist", mood="angry", dur=0.3, sfx="wood_low", gain=0.85,
                                note="两人转身面对面"))]),
            Fig(750, GROUND, 340, at=0, color=K.OTHER3, hair="bun", face=1, mood="calm",
                moves=[(2, dict(face=-1, pose="fist", mood="angry", dur=0.3))]),
            Custom(lightning, x=540, y=820, at=4, enter="none", sfx="rim", note="两人之间劈下闪电"),
        ], draw=ground, text_beat=0, note="两个人背对背，转身面对面握拳，中间劈下一道闪电"),

        # 9：一圈皱眉的人，乌云
        Shot(2, "世界就成了|处处是敌人的地方。", "岸见一郎阐释", [
            *[Fig(x, y, s, at=1 + 0.25 * i, color=col, hair=hair, face=1 if x < 540 else -1, mood="calm",
                  sfx="wood_low" if i == 0 else None, gain=0.8, note="周围的人一个个出现" if i == 0 else "",
                  moves=[(4, dict(mood="angry", pose="point" if i % 2 == 0 else "fist"))])
              for i, (x, y, s, col, hair) in enumerate([
                  (300, 930, 230, K.OTHER, "bun"), (780, 930, 230, K.OTHER2, None), (420, 870, 200, "#9C8FB0", "cap"),
                  (660, 870, 200, K.OTHER3, "long"), (165, 1180, 320, K.OTHER2, "short"),
                  (915, 1180, 320, K.OTHER, None)])],
            Fig(540, 1080, 290, at=0, hair="short", mood="calm",
                moves=[(4, dict(mood="worried")), (6, dict(pose="block", mood="sad", look=0.5))]),
            Custom(storm, x=540, y=500, at=4, enter="none", sfx="tom", gain=0.85, note="头顶压下一片乌云"),
        ], text_beat=0, hits=[(6, "rim", 0.75, "乌云里闪了一下")],
            note="一圈人都皱着眉指向主角，头顶压下乌云"),

        # 10：两个罐子
        Shot(3, "别人的成功，|不等于你的失败。", "机制示意", [
            Custom(jar, x=330, y=GROUND, at=0, enter="pop", level=0.22, drops=(2, 4, 6),
                   moves=[(2, dict(level=0.45, dur=0.3, sfx="wood_high", gain=0.8, note="别人的罐子涨了一截")),
                          (4, dict(level=0.65, dur=0.3, sfx="wood_low", gain=0.8, note="又涨了一截")),
                          (6, dict(level=0.86, dur=0.3, sfx="wood_high", gain=0.75, note="快满了"))]),
            Custom(jar, x=750, y=GROUND, at=0, enter="pop", level=0.35, liquid=K.HERO, drops=(8,), sparkle=8,
                   moves=[(8, dict(level=0.5, dur=0.35, sfx="bongo_high", gain=0.85, note="自己的罐子也涨了一点"))]),
            Label("别人", 330, 1205, 32, at=0, fill=K.INK2),
            Label("我", 750, 1205, 32, at=0, fill=K.HERO),
            Fig(140, GROUND, 270, at=1, color=K.OTHER3, hair="bun", mood="happy", pose="cheer"),
            Fig(940, GROUND, 270, at=1, hair="short", face=-1, mood="worried",
                moves=[(3, dict(look=0.5)), (8, dict(mood="happy", pose="cheer", look=0.2))]),
            Custom(neq, x=540, y=880, at=10, enter="none"),
        ], draw=ground, note="两个罐子：别人的罐子按拍越涨越满，主角的不受影响；第 8 拍主角的也涨了一点，中间出现“≠”"),

        # 11：停下来，把摔倒的人拉起来
        Shot(3, "不再忙着赢，|才有空看见身边的人。", "情境演绎", [
            Fig(110, GROUND, 330, at=0, enter="fade", hair="short", mood="calm",
                moves=[(0.1, dict(x=420, dur=1.0)),
                       (2.4, dict(mood="open")),
                       (4, dict(pose="give", mood="smile", sfx="bongo_low", gain=0.8, note="主角伸出手")),
                       (6, dict(pose="carry", x=400)),
                       (8, dict(pose="cheer", mood="happy"))]),
            Fig(660, GROUND, 300, at=0, enter="fade", color=K.OTHER2, face=-1, pose=SIT_GROUND, mood="sad",
                moves=[(4.3, dict(pose=dict(SIT_GROUND, la1=80, la2=20, head=-4), mood="open")),
                       (6, dict(pose="stand", mood="smile", dur=0.5)),
                       (8, dict(pose="wave", mood="happy"))]),
        ], draw=lambda g: track_bg(g, 0),
            hits=[(2, "wood_low", 0.85, "主角停下脚步"), (8, "clap", 0.9, "两人都笑了")],
            note="主角停下脚步，伸手把坐在跑道上的人拉起来，两人都笑了"),

        # 12：和昨天的自己比
        Shot(4, "和昨天的自己比：|今天进步了一点吗？", "小练习", [
            Custom(lambda c, g, t, d: K.stairs(c, 0, 0, 4, STEP_W, STEP_H, ACC, 1, 0.8, clamp01(t / 0.6)),
                   x=STEP_X, y=GROUND, at=0, enter="none"),
            Custom(yesterday, x=0, y=0, at=2, enter="fade", dur=0.6),
            Label("昨天", step_top(0)[0], step_top(0)[1] - 300 * 1.08 - 50, 32, at=2, fill=K.INK3,
                  sfx="wood_low", gain=0.8, note="淡色的“昨天的我”留在第 1 级"),
            Fig(step_top(0)[0], step_top(0)[1], 300, at=0, hair="short", mood="calm",
                moves=[(4, dict(x=step_top(1)[0], y=step_top(1)[1], pose="climb", mood="smile", dur=0.4,
                                sfx="bongo_high", gain=0.85, note="“今天的我”迈上第 2 级")),
                       (4.8, dict(pose="stand")),
                       (12, dict(pose="cheer", mood="happy"))]),
            Label("今天", step_top(1)[0], step_top(1)[1] - 300 * 1.08 - 50, 32, at=5, fill=ACC),
            Custom(ruler, x=0, y=0, at=8, enter="none", sfx="rim", gain=0.85, note="标尺量出 +1"),
        ], draw=ground, hits=[(12, "clap", 0.85, "主角为自己欢呼")],
            note="台阶上两个主角：淡色的“昨天”在第 1 级，“今天”迈上第 2 级，标尺量出 +1"),

        # 13：清单打勾
        Shot(4, "写下：这周|比上周多做到的一件事。", "小练习", [
            Custom(checklist, x=540, y=740, at=0, enter="pop"),
        ], hits=[(4, "wood_high", 0.85, "第 1 行打勾"), (8, "wood_low", 0.85, "第 2 行打勾"),
                 (12, "bongo_high", 0.85, "第 3 行打勾")],
            note="清单卡“这周多做到的”，笔按拍写下三行，逐行打勾"),

        # 14：沿小路走向日出
        Shot(2, "人生不是比赛，|是自己的路。", "阿德勒的视角", [
            Fig(360, 1170, 300, at=0, hair="short", mood="smile",
                moves=[(2, dict(x=600, y=1050, s=250, dur=1.4, stride=0.9, sfx="wood_low", gain=0.75,
                                note="主角沿小路往前走")),
                       (5, dict(x=660, y=965, s=200, dur=1.0, stride=0.8)),
                       (7, dict(pose="wave", mood="happy"))]),
        ], draw=sunrise_bg, hits=[(1, "cymbal", 0.6, "太阳升起")], text_beat=1,
            note="主角沿着蜿蜒的小路走向日出"),

        end_shot(["Adler, A. (1931). What Life Should Mean to You, ch.3.（中译《自卑与超越》）",
                  "Ansbacher, H. L. & Ansbacher, R. R. (1956). The Individual Psychology of Alfred Adler.",
                  "岸见一郎、古贺史健（2013）《被讨厌的勇气》"], "05 人生课题：为什么烦恼，总和人有关？"),
    ]
    return Episode(4, "competition", "追求优越", "你一直在和谁比赛？", ACC, shots,
                   refs=["Adler, A. (1931). What Life Should Mean to You, ch.3.（中译《自卑与超越》）",
                         "Ansbacher, H. L. & Ansbacher, R. R. (1956). The Individual Psychology of Alfred Adler.",
                         "岸见一郎、古贺史健（2013）《被讨厌的勇气》"],
                   publish_title="你一直在和谁比赛？｜阿德勒心理学04 追求优越",
                   hashtags="#阿德勒 #心理学 #比较 #焦虑 #被讨厌的勇气",
                   cover_title="你一直在|和【谁】比赛？", cover_sub="阿德勒谈追求优越", cover_shot=1, cover_t=5.6,
                   notes=[
                       "追求优越（striving for superiority）为阿德勒原意，晚期多称“追求完善 / 克服”（Ansbacher 1956 第 4 章）；"
                       "“人生有用的一面 / 无用的一面”以是否对共同体有益为标准。",
                       "“健全的比较对象是理想的自己”“把竞争当作人际关系的轴心就无法摆脱不幸”出自《被讨厌的勇气》第二夜，"
                       "片中标注“岸见一郎阐释”。",
                   ]).build()
