"""07 鼓励：为什么“你真棒”，不一定是最好的夸奖？"""

import math

import skia

from engine import gfx
from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, ease_out_back, lerp

from . import core
from . import kit as K
from .core import Arrow, Big, Bubble, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

ACC = "#4F8F5B"
GROUND = 1130
KID = K.OTHER3
WOOD = "#A0784F"
STAR = K.GOLD

KNEEL = dict(lean=4, head=-4, la1=30, la2=40, ra1=10, ra2=30, ll1=90, ll2=-90, rl1=0, rl2=-90)
KNEEL_POINT = dict(KNEEL, la1=80, la2=4, head=-8)
REACH_DOWN = dict(lean=34, head=26, la1=26, la2=6, ra1=12, ra2=10, ll1=22, ll2=-34, rl1=-6, rl2=-22)
GIVE_DOWN = dict(lean=14, head=16, la1=42, la2=-6, ra1=-6, ra2=8, ll1=5, ll2=0, rl1=-5, rl2=0)


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
    eye = (head[0] + face * 0.16 * u * 0.42, head[1] + 0.16 * u * 0.05)
    return dict(head=head, near=near, far=far, eye=eye, chest=(sh_x * 0.55, sh_y + 0.11 * u))


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


def gold_star(c, x, y, r, rot=0.0, alpha=1.0, color=STAR):
    with K.paper(c, alpha, 0.5):
        K.star(c, x, y, r, color, 1, 5, 0.48, rot)
        K.star(c, x, y, r * 0.45, K.tint(color, 0.45), 1, 5, 0.48, rot)


def chest_star(kid, beat_on=-99, wobble=None, fall_at=None, land=None):
    """贴在孩子胸前的金星：跟着孩子走；wobble 拍起摇晃，fall_at 拍脱落、land 拍落地。"""

    def fn(c, g, t, d):
        if g.since(beat_on) < 0:
            return
        x, y = fig_at(kid, g)["chest"]
        rot = 0.0
        if wobble is not None and g.since(wobble) > 0:
            rot = 16 * math.sin(g.since(wobble) * 16) * clamp01(g.since(wobble) / 0.2)
        if fall_at is not None and g.since(fall_at) > 0:
            k = clamp01(g.since(fall_at) / max(1e-3, g.b(land) - g.b(fall_at)))
            gx, gy = x + 130, GROUND - 24
            x = lerp(x, gx, ease_out(k))
            y = lerp(y, gy, ease_in(k))
            rot += 260 * k
            dt = g.since(land)
            if dt > 0:
                y -= 26 * abs(math.sin(min(1, dt / 0.45) * math.pi)) * (1 - clamp01(dt / 0.45))
                rot = 260 + 10 * math.sin(dt * 8) * (1 - clamp01(dt / 0.6))
        dim = clamp01(g.since(d.get("dim", 99)) / 0.5)
        gold_star(c, x, y, d.get("r", 30), rot, 1.0, K.mix(STAR, K.INK3, dim * 0.8))

    return fn


def test_paper(c, s=1.0):
    with K.paper(c, 1, 0.6):
        K.rr(c, 0, 0, 120 * s, 150 * s, 8, K.PAPER)
    for k in range(3):
        K.seg(c, -40 * s, (30 + k * 20) * s, 40 * s, (30 + k * 20) * s, K.LINE, 4)
    K.text(c, "100", 0, -22 * s, 50 * s, "black", K.RED)
    path = skia.Path()
    path.addOval(skia.Rect.MakeXYWH(-52 * s, -52 * s, 104 * s, 62 * s))
    c.drawPath(path, K.paint(K.RED, 1, 4))


# ---------------------------------------------------------------- 1 金星

def held_paper(kid, beat):
    def fn(c, g, t, d):
        k = clamp01(g.since(beat) / 0.35)
        if k <= 0:
            return
        hx, hy = fig_at(kid, g)["near"]
        with K.at(c, hx - 10, hy - 72, -6, 0.3 + 0.7 * ease_out_back(k, 2)):
            test_paper(c)

    return fn


def star_fly(adult, kid, show, land):
    """金星从大人手里出现（show 拍），在 land 拍贴到孩子胸前。"""

    def fn(c, g, t, d):
        k0 = clamp01(g.since(show) / 0.25)
        if k0 <= 0:
            return
        ax, ay = fig_at(adult, g)["near"]
        kx, ky = fig_at(kid, g)["chest"]
        q = clamp01((g.t - g.b(show) - 0.25) / max(1e-3, g.b(land) - g.b(show) - 0.25))
        e = q * q
        x = lerp(ax + 20, kx, e)
        y = lerp(ay - 20, ky, e) - 120 * math.sin(math.pi * e)
        r = lerp(36, 30, e) * (0.3 + 0.7 * ease_out_back(k0, 2))
        gold_star(c, x, y, r, 200 * (1 - e))
        K.burst(c, kx, ky, g.since(land), STAR, 30, 120, 10, 6)

    return fn


# ---------------------------------------------------------------- 2 大问号

def puzzle_card(c, g, t, d):
    k = clamp01(g.since(10) / 0.2)
    rot = 3 * math.sin(g.t * 2) + 4 * math.sin(g.since(10) * 20) * k * (1 - clamp01(g.since(11) / 0.4))

    def draw(c_, w, h):
        K.text(c_, "?", 0, 20, 250, "serif_black", ACC)
        K.text(c_, "难题", 0, -h / 2 + 46, 34, "sans_medium", K.INK2)

    K.card(c, 0, 0, 290, 350, K.PAPER, 1, 26, 1.2, rot, d.get("s", 1.0), ACC, draw)


# ---------------------------------------------------------------- 5 高台与奖牌

def podium(c, g, t, d):
    with K.paper(c, 1, 0.9):
        K.rr(c, 0, -165, 250, 330, 12, K.mix(K.LINE, K.INK3, 0.35))
        K.rr(c, 0, -322, 270, 26, 10, K.INK3)
        K.rr(c, 0, -150, 120, 120, 60, K.mix(K.LINE, K.INK3, 0.2))
    K.star(c, 0, -150, 40, K.PAPER, 0.9)


def medal(c, x, y, s=1.0, rot=0.0):
    with K.at(c, x, y, rot, s):
        with K.paper(c, 1, 0.7):
            K.poly(c, [(-34, -70), (-12, -70), (8, 0), (-14, 0)], "#3A5BA0")
            K.poly(c, [(34, -70), (12, -70), (-8, 0), (14, 0)], K.RED)
            K.dot(c, 0, 18, 34, STAR)
            K.dot(c, 0, 18, 24, K.tint(STAR, 0.35))
            K.star(c, 0, 18, 15, STAR, 1)


def medal_fly(adult, kid, show, land):
    def fn(c, g, t, d):
        k0 = clamp01(g.since(show) / 0.3)
        if k0 <= 0:
            return
        ax, ay = fig_at(adult, g)["near"]
        kx, ky = fig_at(kid, g)["chest"]
        q = clamp01((g.t - (g.b(land) - 0.55)) / 0.55)
        e = q * q
        x = lerp(ax + 10, kx, e)
        y = lerp(ay + 60, ky - 10, e)
        sw = 6 * math.sin(g.t * 5) * (1 - e)
        medal(c, x, y, 0.3 + 0.7 * ease_out_back(k0, 2), sw)
        K.burst(c, kx, ky, g.since(land), STAR, 40, 140, 10, 6)

    return fn


# ---------------------------------------------------------------- 6 梯子

LAD = (560, 655)


def big_ladder(c, g, t, d):
    """从地面向上长出的梯子，顶上一块小平台。"""
    p = ease_out(clamp01(g.since(0) / 0.8))
    x, top = LAD
    y1 = lerp(GROUND, top, p)
    with K.paper(c, 1, 0.8):
        for dx in (-60, 60):
            K.seg(c, x + dx, GROUND, x + dx, y1, WOOD, 14)
        yy = GROUND - 60
        while yy > y1 + 10:
            K.seg(c, x - 60, yy, x + 60, yy, K.shade(WOOD, 0.1), 10)
            yy -= 70
        if p > 0.95:
            K.rr(c, x, top - 6, 230, 24, 10, K.INK3)


# ---------------------------------------------------------------- 7 进度条

def progress(c, g, t, d):
    w, h = 380, 44
    v = sum(ease_out_back(clamp01(g.since(b) / 0.4), 1.6) for b in (2, 5, 8)) / 3
    with K.paper(c, 1, 0.6):
        K.rr(c, 0, 0, w + 16, h + 16, (h + 16) / 2, K.PAPER)
    K.rr(c, 0, 0, w, h, h / 2, K.LINE)
    if v > 0:
        K.rr(c, -w / 2 + w * v / 2, 0, w * v, h, h / 2, ACC)
    for i in (1, 2):
        K.seg(c, -w / 2 + w * i / 3, -h / 2, -w / 2 + w * i / 3, h / 2, K.PAPER, 4)


def grow_steps(base, beats, step):
    return lambda g, t: base + sum(step * ease_out(clamp01(g.since(b) / 0.45)) for b in beats)


# ---------------------------------------------------------------- 8 研究示意

PANELS = ((290, "夸“聪明”", K.INK3, True), (790, "夸“努力”", ACC, False))
PW, PH, PY = 440, 640, 815
KIDS = ((-140, KID, "bun"), (0, K.OTHER, None), (140, K.OTHER2, "short"))
WORK = dict(lean=10, head=12, la1=70, la2=40, ra1=-6, ra2=8, ll1=4, ll2=0, rl1=-4, rl2=0)
GIVE_UP = dict(lean=12, head=22, la1=4, la2=2, ra1=-4, ra2=2, ll1=2, ll2=0, rl1=-2, rl2=0)
TRY = dict(lean=6, head=-10, la1=110, la2=10, ra1=-6, ra2=8, ll1=4, ll2=0, rl1=-4, rl2=0)


def pencil(c, h):
    K.seg(c, h[0], h[1], h[0] + 18, h[1] - 34, K.GOLD, 7)
    K.seg(c, h[0] + 18, h[1] - 34, h[0] + 22, h[1] - 42, K.INK, 4)


def pose_at(g, base, keys):
    cur = prev = base
    for b, p in keys:
        k = clamp01(g.since(b) / 0.45)
        if k <= 0:
            break
        cur = K.blend(prev, p, ease_in_out(k)) if k < 1 else p
        prev = p
    return cur


def study_panel(c, g, t, d):
    """一组孩子面对难题：smart=True 的一组在第 8 拍有两人放下笔；另一组第 10 拍继续尝试、想出办法。"""
    i = d["i"]
    _, label, colr, smart = PANELS[i]
    with K.paper(c, 1, 0.7):
        K.rr(c, 0, 0, PW, PH, 28, K.mix(K.PAPER, K.LINE, 0.25))
    K.pill(c, 0, -PH / 2 + 48, label, 34, colr)
    f = fall(g, 4, 200, 0.3)
    if f is not None:
        with K.at(c, 0, -120 + f[0], -2 if smart else 2, 1, f[1]):
            def draw(c_, w, h):
                K.text(c_, "难题", 0, -18, 46, "serif_black", K.INK)
                K.text(c_, "? ? ?", 0, 34, 34, "black", ACC)
            K.card(c, 0, 0, 220, 150, K.PAPER, 1, 18, 0.9, 0, 1, None, draw)
    feet = PH / 2 - 14
    for j, (dx, kc, hair) in enumerate(KIDS):
        quit_ = smart and j != 1
        keys = [(6, WORK)]
        if quit_:
            keys.append((8 + 0.25 * j, GIVE_UP))
        elif not smart:
            keys.append((10 + 0.2 * j, TRY))
        p = pose_at(g, "stand", keys)
        gave = quit_ and g.since(8 + 0.25 * j) > 0.2
        mood = "sad" if gave else ("open" if (not smart and g.since(10) > 0) else "calm")
        face = 1 if dx <= 0 else -1
        if quit_:
            face *= lerp(1, -1, ease_in_out(clamp01((g.since(8 + 0.25 * j) - 0.1) / 0.4)))
        K.figure(c, dx, feet, 175, p, kc, mood=mood, hair=hair, lift=0.5, face=face,
                 prop=None if gave else pencil)
        if gave:
            ka = clamp01((g.since(8 + 0.25 * j) - 0.3) / 0.3)
            path = skia.Path()
            cx, cy = dx, feet - 225
            path.moveTo(cx - 26, cy)
            for m in range(10):
                path.lineTo(cx - 26 + m * 5.5 + 10 * math.sin(m * 1.9), cy - 12 * math.cos(m * 2.3))
            c.drawPath(path, K.paint(K.INK3, ka, 4))
        if gave:
            k = ease_in(clamp01((g.since(8 + 0.25 * j) - 0.2) / 0.3))
            px, py = dx + 34, lerp(feet - 80, feet - 6, k)
            with K.at(c, px, py, lerp(-60, 0, k)):
                K.seg(c, -26, 0, 26, 0, K.GOLD, 9)
                K.seg(c, 26, 0, 34, 0, K.INK, 6)
    if not smart:
        kb = clamp01(g.since(10) / 0.35)
        if kb > 0:
            K.icon(c, "bulb", 0, feet - 290, 90 * ease_out_back(kb, 2), K.INK2, 1, 0.5, 0, 1, 1.0, K.GOLD)


def fall(g, beat, dist=170, dur=0.3):
    """自定义落下：第 beat 拍落定（撞击帧 = 拍点），之后轻微回弹；返回 (dy, 纵向压缩) 或 None。"""
    dt = g.since(beat)
    if dt < -dur:
        return None
    if dt < 0:
        return -dist * (1 - ease_in(1 + dt / dur)), 1.0
    q = clamp01(dt / 0.28)
    return -10 * math.sin(q * math.pi), 1 - 0.1 * math.sin(q * math.pi)


# ---------------------------------------------------------------- 9 浇水

CAN = (360, 620, 280, 24)


def water_drops(c, g, t, d):
    """从壶嘴落向小苗的水滴（第 1 拍起）。"""
    k = clamp01(g.since(1) / 0.3)
    if k <= 0:
        return
    x, y, s, rot = CAN
    a = math.radians(rot)
    tx, ty = 0.64 * s, -0.28 * s
    sx, sy = x + tx * math.cos(a) - ty * math.sin(a), y + tx * math.sin(a) + ty * math.cos(a)
    ex, ey = 690, 840
    for i in range(7):
        q = (g.since(1) * 1.1 + i / 7) % 1.0
        px = lerp(sx, ex, q) + 20 * math.sin(q * math.pi)
        py = lerp(sy, ey, q * q)
        K.icon(c, "water", px, py, 30, "#7FB3D5", k * (1 - 0.3 * q), 0.2)


# ---------------------------------------------------------------- 10 划掉与打勾

def strike(c, g, t, d):
    k = ease_out(clamp01(g.since(3) / 0.3))
    if k > 0:
        K.seg(c, 345, 574, 345 + 350 * k, 546, K.RED, 10)


# ---------------------------------------------------------------- 11 递箱子

def parcel(c, x, y, rot=0.0):
    with K.at(c, x, y, rot):
        with K.paper(c, 1, 0.8):
            K.rr(c, 0, 0, 150, 110, 10, "#C9A06E")
            K.rr(c, 0, -4, 150, 22, 0, K.shade("#C9A06E", 0.12))
            K.rr(c, 0, 0, 26, 110, 0, K.tint("#C9A06E", 0.25))


def handover(giver, taker, start, end):
    def fn(c, g, t, d):
        jg, jt = fig_at(giver, g), fig_at(taker, g)
        pg = ((jg["near"][0] + jg["far"][0]) / 2, min(jg["near"][1], jg["far"][1]) - 30)
        pt = ((jt["near"][0] + jt["far"][0]) / 2, min(jt["near"][1], jt["far"][1]) - 30)
        q = ease_in_out(clamp01((g.t - g.b(start)) / max(1e-3, g.b(end) - g.b(start))))
        parcel(c, lerp(pg[0], pt[0], q), lerp(pg[1], pt[1], q) - 40 * math.sin(math.pi * q), 0)

    return fn


# ---------------------------------------------------------------- 12 发光

def glow(c, g, t, d):
    a = clamp01(g.since(6) / 0.4)
    if a <= 0:
        return
    K.spotlight(c, 0, -170, 300, K.GOLD, 0.45 * a)
    K.ripple(c, 0, -170, g.since(6), K.GOLD, 300, 8, 0.8, 0.9)


def sparkles(g):
    k = clamp01(g.since(8) / 0.3)
    if k <= 0:
        return
    for i, (dx, dy) in enumerate(((-150, -330), (140, -300), (-120, -120), (170, -150), (10, -420))):
        tw = 0.7 + 0.3 * math.sin(g.t * 5 + i)
        K.star(g.c, 790 + dx, GROUND + dy, 18 * ease_out_back(k, 2) * tw, K.GOLD, 0.95, 4, 0.4)


# ---------------------------------------------------------------- 13 平视

def eye_line(adult, kid):
    def fn(c, g, t, d):
        k = ease_out(clamp01(g.since(4) / 0.5))
        if k <= 0:
            return
        (ax, ay), (kx, ky) = fig_at(adult, g)["eye"], fig_at(kid, g)["eye"]
        y = (ay + ky) / 2
        x0, x1 = ax + 40, kx - 40
        path = skia.Path()
        path.moveTo(x0, y)
        path.lineTo(lerp(x0, x1, k), y)
        gfx.stroke_path(c, path, ACC, 6, 1.0, 1.0, dash=(18, 12, 0))
        hk = clamp01(g.since(6) / 0.4)
        if hk > 0:
            K.heart(c, (x0 + x1) / 2, y - 90 - 10 * math.sin(g.t * 3), 80 * ease_out_back(hk, 2.4), K.RED)

    return fn


# ---------------------------------------------------------------- 组装

def build() -> Episode:
    # 1
    adult1 = Fig(320, GROUND, 380, at=0, hair="short", mood="smile",
                 moves=[(3, dict(pose="give", mood="happy")), (6, dict(pose="stand"))])
    kid1 = Fig(650, GROUND, 230, at=0, color=KID, hair="bun", face=-1, mood="smile",
               moves=[(2, dict(pose="fist", mood="happy", sfx="wood_high", note="孩子举起 100 分的卷子")),
                      (8, dict(pose="cheer", sfx="bongo_high", note="孩子开心地举手"))])
    # 2
    adult2 = Fig(400, GROUND, 380, at=0, hair="short", mood="smile",
                 moves=[(9, dict(mood="worried"))])
    kid2 = Fig(620, GROUND, 230, at=0, color=KID, hair="bun", face=-1, mood="smile",
               moves=[(3, dict(face=1, mood="worried")),
                      (5, dict(x=290, face=-1, dur=0.9, mood="worried", sfx="shaker", note="孩子往后退")),
                      (7.2, dict(face=1)),
                      (8, dict(pose="hide", mood="sad", sfx="wood_low", note="孩子躲到大人身后"))])
    # 3
    kid3 = Fig(470, GROUND, 440, at=0, enter="none", color=KID, hair="bun", mood="worried",
               moves=[(4, dict(mood="surprised")), (5, dict(pose="sad", mood="worried")),
                      (6, dict(pose=REACH_DOWN, look=-0.8, sfx="bongo_low", note="孩子弯腰想捡回金星"))])
    # 5
    adult5 = Fig(300, 812, 320, at=0, hair="short", mood="flat",
                 moves=[(2, dict(pose=GIVE_DOWN, mood="smile"))])
    kid5 = Fig(740, GROUND, 230, at=0, color=KID, hair="bun", face=-1, mood="calm", look=1.0,
               moves=[(4, dict(mood="smile"))])
    # 11
    friend11 = Fig(960, GROUND, 340, at=0, enter="none", color=K.OTHER, hair="bun", face=-1, pose="carry",
                   mood="calm", moves=[(0, dict(x=720, dur=1.0)), (2, dict(pose="give")), (3.2, dict(pose="stand")),
                                       (8, dict(mood="happy"))])
    hero11 = Fig(300, GROUND, 340, at=0, hair="short", mood="calm",
                 moves=[(2.4, dict(pose="carry", mood="surprised")), (5, dict(mood="smile")), (8, dict(mood="happy"))])
    # 13
    adult13 = Fig(320, GROUND, 400, at=0, hair="short", mood="calm",
                  moves=[(2, dict(pose=KNEEL, mood="smile", sfx="wood_low", note="大人蹲下，和孩子一样高")),
                         (6, dict(mood="happy"))])
    kid13 = Fig(720, GROUND, 285, at=0, color=KID, hair="bun", face=-1, mood="calm",
                moves=[(6, dict(mood="happy"))])

    shots = [
        Shot(3, "孩子考了满分，|你说：“你真聪明！”", "情境演绎", [
            adult1, kid1,
            Custom(held_paper(kid1, 2), at=0, enter="none"),
            Custom(star_fly(adult1, kid1, 3, 4), at=0, enter="none"),
            Custom(chest_star(kid1, beat_on=4), at=0, enter="none"),
        ], draw=ground, hits=[(4, "clap", 1.0, "大人给孩子胸前贴上一颗金星")],
            note="小孩举着 100 分的卷子，高大的大人从上方给他贴上一颗金星"),
        Shot(3, "下次遇到一道难题，|他却不敢试了。", "情境演绎", [
            Custom(puzzle_card, x=850, y=760, at=2, enter="slide_r", dur=0.4, sfx="tom", note="一张巨大的“？”难题卡滑进来"),
            kid2,
            Custom(chest_star(kid2), at=0, enter="none"),
            adult2,
        ], draw=ground, note="孩子面前一张巨大的“？”卡，他后退躲到大人身后"),
        Shot(2, "怕显得不聪明，|怕丢掉那颗星。", "机制示意", [
            Custom(puzzle_card, x=860, y=660, at=0, enter="none", alpha=0.55, s=0.8),
            Bubble("要是做错了……", 300, 540, 40, at=1, think=True, tail=(0.5, 1)),
            kid3,
            Custom(chest_star(kid3, wobble=2, fall_at=3.4, land=4), at=0, enter="none", r=46, dim=6),
        ], draw=ground, text_beat=0, hits=[(2, "shaker", 0.9, "胸前的金星开始摇晃"), (4, "tom", 0.9, "金星掉落在地")],
            note="孩子胸前的金星摇晃，第 4 拍掉在地上"),
        Shot(3, "阿德勒学派区分：|表扬与鼓励。", "阿德勒学派", [
            Big("鼓励", 540, 510, 180, at=0, sfx="kick", sub="encouragement", note="概念落版（音乐 drop）"),
            Label("表扬", 860, 655, 40, at=1, fill=K.INK3, alpha=1.0,
                  moves=[(4, dict(x=935, y=720, rot=22, alpha=0.4, dur=0.35, sfx="wood_low",
                                  note="小一号的“表扬”被推开"))]),
            Fig(400, GROUND, 330, at=6, pose=KNEEL, hair="short", mood="calm", sfx="wood_high",
                note="大人蹲下，与孩子平视", moves=[(8, dict(mood="happy"))]),
            Fig(630, GROUND, 240, at=6, color=KID, hair="bun", face=-1, mood="calm",
                moves=[(8, dict(mood="happy"))]),
            Icon("heart", 515, 800, 80, color=K.RED, at=8, enter="pop", sfx="bongo_high", note="两人之间一颗心"),
        ], draw=ground, note="drop 处“鼓励”砸下，旁边小一号的“表扬”被推开；下方大人蹲下与孩子平视"),
        Shot(3, "表扬是评判：|“你真棒，你做得好。”", "阿德勒学派", [
            Custom(podium, x=300, y=GROUND, at=0, enter="none"),
            adult5, kid5,
            Custom(medal_fly(adult5, kid5, 2, 4), at=0, enter="none", sfx=None),
            Arrow((540, 470), (540, 1010), at=6, color=ACC, width=16, head=46, sfx="rim", note="竖直向下的箭头：评判"),
            Label("评判", 640, 560, 36, at=7, fill=ACC),
        ], draw=ground, hits=[(2, "wood_high", 0.9, "大人在高台上拿出奖牌"), (4, "bongo_low", 0.9, "奖牌递到孩子胸前")],
            note="大人站在高台上把奖牌递下来，一支竖直箭头向下"),
        Shot(3, "背后是“上对下”的|评价关系。", "岸见一郎阐释", [
            Custom(big_ladder, at=0, enter="none"),
            Fig(LAD[0], LAD[1] - 16, 240, at=2, enter="drop", hair="short", mood="flat", sfx="wood_high",
                note="大人落在梯子顶上", moves=[(9, dict(pose="proud"))]),
            Fig(780, GROUND, 210, at=4, color=KID, hair="bun", face=-1, mood="worried", look=1.0,
                moves=[(9, dict(pose="sad", mood="sad", look=0.4))]),
            Arrow((180, 1110), (180, 480), at=5, color=K.INK2, width=10, head=36, sfx="rim", note="竖轴画出"),
            Label("纵向关系", 185, 418, 34, at=7, fill=ACC, sfx="bongo_low", note="竖轴标签“纵向关系”"),
            Txt("上", 225, 500, 34, at=6, font="sans_medium", color=K.INK2),
            Txt("下", 225, 1080, 34, at=6, font="sans_medium", color=K.INK2),
        ], draw=ground, note="梯子：大人在上，小孩在下，竖轴标签“纵向关系”"),
        Shot(3, "鼓励看见的是：|努力、进步和贡献。", "阿德勒学派", [
            Fig(230, GROUND, 330, at=0, pose=KNEEL, hair="short", mood="smile",
                moves=[(5, dict(pose=KNEEL_POINT, mood="open"))]),
            Fig(450, GROUND, 240, at=0, color=KID, hair="bun", mood="calm",
                moves=[(8, dict(pose="cheer", mood="happy"))]),
            Custom(progress, x=790, y=520, at=0, enter="pop"),
            Label("努力", 660, 620, 34, at=2, fill=ACC, sfx="wood_high", note="看见努力"),
            Label("进步", 790, 620, 34, at=5, fill=ACC, sfx="bongo_high", note="看见进步"),
            Label("贡献", 920, 620, 34, at=8, fill=ACC, sfx="clap", note="看见贡献"),
            Icon("sprout", 790, GROUND - 0.51 * 330, 330, at=0, enter="pop", lift=0.6,
                 p=grow_steps(0.25, (2, 5, 8), 0.25)),
        ], draw=ground, note="两人在同一高度；进度条一格格增长，小苗按拍长高"),
        Shot(4, "被夸“聪明”的孩子，|受挫后更容易放弃。", "研究证据", [
            Custom(study_panel, x=PANELS[0][0], y=PY, i=0, at=0, enter="pop"),
            Custom(study_panel, x=PANELS[1][0], y=PY, i=1, at=0.5, enter="pop"),
            Txt("Mueller & Dweck，1998；后续重复研究结果不一（Li & Bates，2019）", 540, 1232, 26, at=2,
                font="sans_medium", color=K.INK2),
        ], research=True,
            hits=[(4, "tom", 0.9, "两组孩子面前都落下一道难题"), (8, "wood_low", 0.9, "被夸聪明的一组有两人放下笔"),
                  (10, "wood_high", 0.9, "被夸努力的一组继续尝试，想出办法")],
            note="研究示意：两组孩子（夸聪明 / 夸努力）面对难题，前一组更多人放下笔；小字注明出处与重复研究结果不一"),
        Shot(3, "“孩子需要鼓励，|就像植物需要水。”", "德雷克斯 · 大意", [
            Custom(water_drops, at=1, enter="none"),
            Icon("can", CAN[0], CAN[1], CAN[2], color=K.HERO, at=0, rot=0, enter="pop",
                 moves=[(1, dict(rot=CAN[3], dur=0.35))]),
            Icon("sprout", 690, GROUND - 0.51 * 380, 380, at=0, enter="pop", lift=0.6,
                 p=grow_steps(0.2, (2, 5, 8), 0.27)),
            Txt("德雷克斯（阿德勒的学生与同事），1964", 540, 1232, 28, at=4, font="sans_medium", color=K.INK2),
        ], draw=ground, hits=[(2, "bongo_high", 0.9, "小苗长高一截"), (5, "bongo_low", 0.85, "再长高"),
                              (8, "wood_high", 0.9, "长出新叶")],
            note="洒水壶浇水，小苗按拍长高；底部小字注明德雷克斯与年份"),
        Shot(3, "不说“你真聪明”，|说“你一直没放弃”。", "小练习", [
            Fig(180, GROUND, 320, at=0, hair="short", mood="calm",
                moves=[(3, dict(pose="shrug", mood="worried")), (5, dict(pose="point", mood="smile"))]),
            Fig(900, GROUND, 220, at=0, color=KID, hair="bun", face=-1, mood="flat",
                moves=[(7, dict(mood="smile")), (9, dict(pose="cheer", mood="happy"))]),
            Bubble("你真聪明！", 520, 560, 50, at=0, tail=(-0.5, 1), alpha=1.0, moves=[(3, dict(alpha=0.45))]),
            Custom(strike, at=3, enter="none", sfx="rim", note="“你真聪明”被划掉"),
            Icon("cross", 785, 560, 96, color=K.RED, at=3, enter="pop"),
            Bubble("你一直没放弃。", 540, 830, 50, at=5, tail=(-0.6, 1), sfx="wood_high", note="换成“你一直没放弃”"),
            Icon("check", 840, 820, 96, color=ACC, at=7, enter="pop", sfx="clap", note="打勾"),
        ], draw=ground, note="两句对话：第一句被划掉，第二句打勾，孩子高兴起来"),
        Shot(4, "对身边的人，|说“谢谢，你帮了大忙”。", "岸见一郎阐释", [
            hero11, friend11,
            Custom(handover(friend11, hero11, 2.2, 3), at=0, enter="none"),
            Icon("heart", 515, 720, 110, color=K.RED, at=4, enter="pop", sfx="bongo_high", note="两人之间亮起爱心"),
            Bubble("谢谢！", 330, 630, 46, at=6, tail=(-0.1, 1), sfx="wood_high", note="主角说谢谢"),
            Custom(lambda c, g, t, d: [K.heart(c, 515 + dx, 640 - 60 * ((g.since(8) * 0.6 + o) % 1.0), 40,
                                                K.mix(K.RED, K.PAPER, 0.2), 1 - ((g.since(8) * 0.6 + o) % 1.0))
                                        for dx, o in ((-90, 0), (80, 0.5))], at=8, enter="fade"),
        ], draw=ground, hits=[(3, "wood_low", 0.9, "箱子递到主角手里")],
            note="两个大人同一高度：朋友递来箱子，主角接过说谢谢，两人之间亮起爱心"),
        Shot(4, "今天对一个人，|说出你看见的努力。", "小练习", [
            Custom(glow, x=790, y=GROUND, at=6, enter="none"),
            Fig(270, GROUND, 340, at=0, hair="short", mood="calm",
                moves=[(2, dict(pose="point", mood="open")), (8, dict(pose="wave", mood="happy"))]),
            Fig(790, GROUND, 330, at=0, color=K.OTHER2, face=-1, pose="sad", mood="sad",
                moves=[(6, dict(pose="stand", mood="smile")), (8, dict(pose="cheer", mood="happy"))]),
            Bubble("你这周每天|都坚持了", 470, 640, 46, at=2, tail=(-0.5, 1), sfx="wood_high", note="主角说出看见的努力"),
        ], draw=ground, over=sparkles, hits=[(6, "cymbal", 0.7, "朋友发光"), (8, "clap", 0.85, "朋友开心地举手")],
            note="主角对朋友说“你这周每天都坚持了”，朋友整个人亮了起来"),
        Shot(2, "平视，|才是真正的鼓励。", "阿德勒的视角", [
            adult13, kid13,
            Custom(eye_line(adult13, kid13), at=0, enter="none"),
        ], draw=ground, text_beat=0, hits=[(4, "rim", 0.9, "一条水平线连起两人的眼睛"),
                                           (6, "bongo_high", 0.9, "两人都笑了")],
            note="大人蹲下，两人视线齐平，一条水平线连起两人的眼睛"),
        end_shot(["Dreikurs, R. & Soltz, V. (1964). Children: The Challenge.",
                  "Mueller, C. M. & Dweck, C. S. (1998). JPSP, 75(1), 33–52.",
                  "Li, Y. & Bates, T. C. (2019). JEP: General, 148(9), 1640–1655.",
                  "岸见一郎、古贺史健（2013）《被讨厌的勇气》"],
                 "08 早期记忆：你最早的记忆，藏着什么？"),
    ]
    return Episode(7, "encouragement", "鼓励", "为什么“你真棒”，不一定是最好的夸奖？", ACC, shots,
                   refs=["Dreikurs, R. & Soltz, V. (1964). Children: The Challenge.",
                         "Mueller, C. M. & Dweck, C. S. (1998). JPSP, 75(1), 33–52.",
                         "Li, Y. & Bates, T. C. (2019). JEP: General, 148(9), 1640–1655.",
                         "岸见一郎、古贺史健（2013）《被讨厌的勇气》"],
                   publish_title="为什么“你真棒”，不一定是最好的夸奖？｜阿德勒心理学07 鼓励",
                   hashtags="#阿德勒 #心理学 #育儿 #鼓励 #被讨厌的勇气",
                   cover_title="“你真棒”|不一定是【最好的夸奖】", cover_sub="阿德勒学派：表扬与鼓励",
                   cover_shot=0, cover_t=5.0,
                   notes=[
                       "表扬与鼓励的区分属于阿德勒学派（Dinkmeyer & Dreikurs 1963；Dreikurs & Soltz 1964）。",
                       "“孩子需要鼓励，就像植物需要水”是德雷克斯的话（大意），NASAP 归于 Dreikurs & Soltz (1964) Children: The "
                       "Challenge；不是阿德勒原话。德雷克斯是阿德勒在维也纳的学生兼同事。",
                       "第 8 镜研究：Mueller & Dweck (1998), JPSP 75(1):33–52, doi:10.1037/0022-3514.75.1.33；Li & Bates "
                       "(2019, JEP: General, doi:10.1037/xge0000669) 的重复研究未能复现，片中注明“后续重复研究结果不一”。",
                       "“表扬是上对下的评价、用感谢回应贡献”出自《被讨厌的勇气》第四夜，标注“岸见一郎阐释”。",
                   ]).build()
