"""10 共同体感觉：人在什么时候，会觉得自己有价值？"""

import math

import numpy as np
import skia

from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp, stroke_path

from . import kit as K
from .core import Big, Bubble, Custom, Episode, Fig, Icon, Label, Shot, end_shot

ACC = "#5A5DB0"
GROUND = 1130
FRIEND = K.OTHER3
PEOPLE = [K.OTHER, K.OTHER2, K.OTHER3, "#9C8FB0", "#7F8C76"]


def ground(g):
    K.ground(g.c, GROUND)


def fig_geom(s, p="stand", face=1, bob=0.0):
    """按 kit.figure 的骨架算法求头部中心、头半径与前手位置（相对脚底中点）。"""
    d = K.pose(p)
    u = s
    thigh, shin, upper, fore = 0.235 * u, 0.225 * u, 0.19 * u, 0.18 * u

    def ext(a1, a2):
        (_, ey), (_, fy) = K._limb(0, 0, a1, a2, thigh, shin, 1)
        return max(ey, fy)

    hip_y = -d["seat"] * u if d["seat"] > 0 else -max(ext(d["ll1"], d["ll2"]), ext(d["rl1"], d["rl2"]))
    hip_y -= bob * u
    lean = math.radians(d["lean"])
    sh_x = face * 0.30 * u * math.sin(lean)
    sh_y = hip_y - 0.30 * u * math.cos(lean)
    hd = math.radians(d["head"])
    hx = sh_x + face * 0.15 * u * math.sin(lean + hd * 0.5)
    hy = sh_y - 0.15 * u * math.cos(lean + hd * 0.5)
    _, hand = K._limb(sh_x + 0.06 * u * face, sh_y + 0.03 * u, d["la1"], d["la2"], upper, fore, face)
    return dict(head=(hx, hy), r=0.16 * u, hand=hand, chest=(sh_x * 0.6, sh_y + 0.14 * u))


def idle_bob(g, x):
    return 0.006 * math.sin(g.t * 2.6 + x * 0.02)


def draw_person(c, g, d, color=K.HERO, hair="short"):
    """自绘人物（与 Fig 相同的呼吸起伏），返回骨架几何以便把道具接在手上。"""
    s, p, face = d.get("s", 360), d.get("pose", "stand"), d.get("face", 1)
    bob = idle_bob(g, d["x"])
    K.figure(c, 0, 0, s, p, d.get("color", color), K.SKIN, 1, face, d.get("mood", "calm"), d.get("hair", hair),
             None, bob, 1.0, d.get("look", 0.0))
    return fig_geom(s, p, face, bob)


def cup(c, x, y, s=1.0, fill=0.75, alpha=1.0):
    with K.at(c, x, y, 0, s):
        with K.paper(c, alpha, 0.5):
            path = skia.Path()
            path.moveTo(-26, -34)
            path.lineTo(26, -34)
            path.lineTo(20, 30)
            path.lineTo(-20, 30)
            path.close()
            c.drawPath(path, K.paint("#E8EEF4"))
            if fill > 0:
                top = 30 - 60 * fill
                c.save()
                c.clipPath(path, doAntiAlias=True)
                c.drawRect(skia.Rect.MakeLTRB(-30, top, 30, 32), K.paint("#8FB8D8"))
                c.restore()
            K.seg(c, -26, -34, 26, -34, K.INK3, 3)


def glow_rays(c, x, y, r0, r1, level, color=K.GOLD, n=12, t=0.0):
    if level <= 0.01:
        return
    K.spotlight(c, x, y, r1 * 1.25, color, 0.55 * level)
    for i in range(n):
        a = i * math.tau / n + t * 0.4
        K.seg(c, x + math.cos(a) * r0, y + math.sin(a) * r0, x + math.cos(a) * lerp(r0, r1, level),
              y + math.sin(a) * lerp(r0, r1, level), color, 7, 0.85 * level)


# ---------------------------------------------------------------- 第 1 镜：奖杯的光按拍变暗

BOSS_X = 800
BOSS_HAND = (BOSS_X - fig_geom(350, "give")["hand"][0], GROUND + fig_geom(350, "give")["hand"][1])


def hero_trophy(c, g, el_t, d):
    geo = draw_person(c, g, d)
    hand = geo["hand"]
    # 第 2 拍：奖杯从老板手里交到主角手上
    k = ease_in_out(clamp01((g.since(2) + 0.45) / 0.45)) if g.since(2) > -0.45 else 0.0
    bx, by = BOSS_HAND[0] - d["x"], BOSS_HAND[1] - GROUND
    tx, ty = lerp(bx, hand[0], k), lerp(by, hand[1], k)
    tx, ty = tx + 6, ty - 48
    glow = d.get("glow", 1.0) * clamp01(g.since(2) / 0.4)
    glow_rays(c, tx, ty, 80, 170, glow, K.GOLD, 12, g.t)
    K.icon(c, "trophy", tx, ty, 110, K.mix(K.INK3, K.GOLD, 0.25 + 0.75 * d.get("glow", 1.0)), 1, 0.7)
    K.burst(c, tx, ty, g.since(2), K.GOLD, 70, 200, 12, 7)


def perks(c, g, el_t, d):
    """升职、加薪、被夸奖：三个小图标，随奖杯的光一起变淡。"""
    fade = 1 - 0.6 * clamp01(g.since(6) / 3.0)
    for i, (x, y) in enumerate(((160, 520), (330, 430), (520, 500))):
        k = clamp01((g.since(0.25 + i * 0.4)) / 0.35)
        if k <= 0:
            continue
        sc = 0.3 + 0.7 * ease_out_back(k, 2)
        yy = y + 6 * math.sin(g.t * 1.6 + i)
        with K.at(c, x, yy, 0, sc):
            if i == 0:
                with K.paper(c, fade, 0.6):
                    K.dot(c, 0, 0, 52, ACC)
                K.arrow(c, (0, 26), (0, -26), K.PAPER, 12, fade, 1, 0, 30)
            elif i == 1:
                with K.paper(c, fade, 0.6):
                    K.dot(c, 0, 0, 52, K.GOLD)
                    K.dot(c, 0, 0, 40, K.tint(K.GOLD, 0.25))
                K.text(c, "¥", 0, 0, 52, "black", K.shade(K.GOLD, 0.25), fade)
            else:
                with K.paper(c, fade, 0.6):
                    K.dot(c, 0, 0, 52, K.RED)
                K.star(c, 0, 0, 30, K.PAPER, fade)


# ---------------------------------------------------------------- 第 2 镜：一起抬箱子

CARRY = fig_geom(340, "carry")
CARRY_F = fig_geom(330, "carry", -1)
BOX_W = 150


def box_pair(c, g, el_t, d):
    """主角和朋友抬着一只纸箱（自绘，手扣在箱子两侧），一起向右走。"""
    x = d["x"]
    hero_hand = CARRY["hand"]
    fx = hero_hand[0] + BOX_W - CARRY_F["hand"][0]
    by = GROUND + hero_hand[1] - 20
    q = (x - d["x0"]) / max(1e-6, d["x1"] - d["x0"])
    walking = math.sin(math.pi * q) if 0 < q < 1 else 0.0
    phase = (x - d["x0"]) / (0.28 * 340)
    pose = K.walk(phase, walking, "carry") if walking > 0 else "carry"
    bx = hero_hand[0] + BOX_W / 2
    bob = 6 * abs(math.sin(phase * math.pi)) * walking
    with K.paper(c, 1, 0.8):
        K.rr(c, bx, by - GROUND - bob, BOX_W, 120, 8, "#C9A47E")
        K.rr(c, bx, by - GROUND - 60 - bob, BOX_W, 12, 3, "#B48C64")
        K.rr(c, bx, by - GROUND - 15 - bob, 60, 16, 3, "#E5C29E")
    K.figure(c, 0, 0, 340, pose, K.HERO, mood=d.get("mood", "smile"), hair="short", bob=idle_bob(g, x))
    pose_f = K.walk(phase + 0.5, walking, "carry") if walking > 0 else "carry"
    K.figure(c, fx, 0, 330, pose_f, FRIEND, mood=d.get("mood", "smile"), hair="bun", face=-1,
             bob=idle_bob(g, x + 200))


def hearts(c, g, el_t, d):
    """爱心按拍从箱子上方飘起，停在半空轻轻浮动（开心了好几天）。"""
    for i, (b, hx, hy) in enumerate(((4, 470, 640), (6, 600, 560), (8, 720, 650), (10, 560, 450))):
        k = clamp01(g.since(b) / 0.8)
        if k <= 0:
            continue
        x = lerp(600, hx, ease_out(k)) + 8 * math.sin(g.t * 2 + i)
        y = lerp(860, hy, ease_out(k)) + 6 * math.sin(g.t * 1.7 + i * 2)
        with K.at(c, x, y, 0, 0.3 + 0.7 * ease_out_back(clamp01(k * 2), 2)):
            with K.paper(c, 1, 0.6):
                K.heart(c, 0, 0, 80, K.RED if i % 2 == 0 else K.mix(K.RED, K.GOLD, 0.4))
        K.burst(c, x, y, g.since(b) - 0.2, K.GOLD, 40, 100, 8, 5)


# ---------------------------------------------------------------- 第 3 镜：左右分屏

def panel_trophy(c, w, h):
    gy = h / 2 - 110
    K.ground(c, gy, x0=-w / 2 + 30, x1=w / 2 - 30)
    K.figure(c, -20, gy, 240, "wave", K.HERO, mood="flat", hair="short", lift=0.4)
    geo = fig_geom(240, "wave")
    K.icon(c, "trophy", -20 + geo["hand"][0] + 4, gy + geo["hand"][1] - 34, 80, K.INK3, 1, 0.4)
    K.text(c, "开心一阵", 0, h / 2 - 52, 40, "serif", K.INK2)


def panel_move(c, w, h):
    gy = h / 2 - 110
    K.ground(c, gy, x0=-w / 2 + 30, x1=w / 2 - 30)
    s = 210
    geo = fig_geom(s, "carry")
    hx = geo["hand"][0]
    x0 = -hx - 50
    K.rr(c, x0 + hx + 50, gy + geo["hand"][1] - 14, 100, 80, 6, "#C9A47E")
    K.figure(c, x0, gy, s, "carry", K.HERO, mood="happy", hair="short", lift=0.4)
    K.figure(c, x0 + 2 * hx + 100, gy, s * 0.97, "carry", FRIEND, mood="happy", hair="bun", face=-1, lift=0.4)
    for i, (x, y) in enumerate(((-70, -150), (40, -200), (110, -130))):
        K.heart(c, x, y, 54 - i * 6, K.RED)
    K.text(c, "开心好几天", 0, h / 2 - 52, 40, "serif", ACC)


def panel(fn):
    def draw(c, g, el_t, d):
        K.card(c, 0, 0, 410, 560, K.PAPER, 1, 26, 1.0, d.get("tilt", 0), 1, None, fn)
    return draw


# ---------------------------------------------------------------- 第 4 镜：成为共同体的一员

ROW = [(170, 300, PEOPLE[0], "long", 1), (350, 320, PEOPLE[1], None, 1), (730, 310, PEOPLE[3], "bun", -1),
       (910, 300, PEOPLE[4], "cap", -1)]


def links_row(c, g, el_t, d):
    xs = [170, 350, 540, 730, 910]
    y = 975
    for i in range(4):
        p = clamp01((g.since(6) - i * 0.07) / 0.35)
        if p <= 0:
            continue
        path = K.curve_path((xs[i] + 40, y), (xs[i + 1] - 40, y), -0.18)
        stroke_path(c, path, ACC, 9, 1, ease_out(p), glow=(K.tint(ACC, 0.3), 8) if g.since(8) > 0 else None)
    pr = ease_out(clamp01(g.since(8) / 0.7))
    if pr > 0:
        path = skia.Path()
        path.addOval(skia.Rect.MakeXYWH(100, 735, 880, 445))
        stroke_path(c, path, K.GOLD, 8, 0.85, pr, dash=(20, 14, 0))


# ---------------------------------------------------------------- 第 5 镜：心理健康的标尺

GX, GY0, GY1, GW = 640, 500, 1110, 130


def gauge(c, g, el_t, d):
    with K.paper(c, 1, 0.8):
        K.rr(c, GX, (GY0 + GY1) / 2, GW + 30, GY1 - GY0 + 30, (GW + 30) / 2, K.PAPER)
    K.rr(c, GX, (GY0 + GY1) / 2, GW, GY1 - GY0, GW / 2, "#E7E2F2")
    lvl = 0.0
    for i, b in enumerate((2, 4, 6, 8)):
        lvl = max(lvl, (i + ease_out_back(clamp01(g.since(b) / 0.4), 1.6)) / 4 if g.since(b) > 0 else 0)
    if lvl > 0:
        h = (GY1 - GY0) * min(1.0, lvl)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(GX - GW / 2, GY0, GX + GW / 2, GY1), GW / 2, GW / 2),
                    doAntiAlias=True)
        top = GY1 - h
        sh = skia.GradientShader.MakeLinear([(0, GY1), (0, GY0)], [K.col(K.tint(ACC, 0.25)), K.col(ACC)])
        c.drawRect(skia.Rect.MakeLTRB(GX - GW / 2, top, GX + GW / 2, GY1), skia.Paint(AntiAlias=True, Shader=sh))
        K.rr(c, GX, top + 6, GW, 12, 6, K.tint(ACC, 0.5), 0.8)
        c.restore()
    for k in range(9):
        y = GY1 - 40 - k * (GY1 - GY0 - 80) / 8
        w = 46 if k % 2 == 0 else 28
        K.seg(c, GX - GW / 2 - 20 - w, y, GX - GW / 2 - 20, y, K.INK2, 5)
    hk = clamp01(g.since(8) / 0.4)
    K.heart(c, GX, GY0 - 85, 110, K.RED if hk > 0 else K.LINE)
    if hk > 0:
        K.spotlight(c, GX, GY0 - 85, 160, K.GOLD, 0.5 * hk)
        K.burst(c, GX, GY0 - 85, g.since(8), K.GOLD, 60, 170, 10, 7)


# ---------------------------------------------------------------- 第 6 镜：围墙里的人 vs 连着线的人

def wall(c, g, el_t, d):
    p = ease_out_back(clamp01(el_t / 0.5), 1.2)
    h = 230 * p
    with K.paper(c, 1, 0.8):
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(-200, -h, 200, 0))
        K.rr(c, 0, -115, 340, 230, 8, "#B9A58E")
        for row in range(5):
            y = -230 + row * 46
            off = 0 if row % 2 == 0 else 34
            for col in range(-3, 4):
                bx = col * 68 + off
                if abs(bx) <= 150:
                    K.rr(c, bx, y + 23, 62, 40, 4, K.mix("#B9A58E", "#8E7A64", 0.25 + 0.1 * ((row + col) % 2)))
        c.restore()


def storm(c, g, el_t, d):
    k = clamp01(el_t / 0.4)
    K.icon(c, "cloud", 0, 0, 220, K.INK2, k, 0.6)
    for i in range(7):
        x = -80 + i * 27
        ph = (g.t * 1.6 + i * 0.37) % 1.0
        y0 = 50 + ph * 150
        K.seg(c, x, y0, x - 10, y0 + 30, "#7FA6C2", 6, k * (1 - ph))
    if (g.since(0) % 1.4) < 0.12:
        K.poly(c, [(10, 40), (-20, 110), (5, 110), (-15, 170), (35, 90), (10, 90), (30, 40)], K.GOLD, k)


GROUP = [(640, 270, PEOPLE[0], "long", 1), (790, 295, PEOPLE[2], "bun", -1), (940, 265, PEOPLE[3], None, -1)]


def group_links(c, g, el_t, d):
    pts = []
    for x, s, _, _, f in GROUP:
        geo = fig_geom(s, "stand", f)
        pts.append((x + geo["head"][0], GROUND + geo["head"][1] - geo["r"] - 50))
    pairs = [(0, 1), (1, 2), (0, 2)]
    for j, (a, b) in enumerate(pairs):
        p = clamp01((g.since(4) - j * 0.12) / 0.4)
        if p > 0:
            path = K.curve_path(pts[a], pts[b], -0.25 if j < 2 else -0.3)
            stroke_path(c, path, ACC, 8, 1, ease_out(p), glow=(K.tint(ACC, 0.4), 8))
    for j, (x, y) in enumerate(pts):
        k = clamp01((g.since(4) - j * 0.1) / 0.3)
        if k > 0:
            K.dot(c, x, y, 16 * ease_out_back(k, 2), ACC)
            K.dot(c, x, y, 7 * k, K.PAPER)


# ---------------------------------------------------------------- 第 7 镜：递杯子

GIVE = fig_geom(360, "give")
GIVE_F = fig_geom(340, "give", -1)
H7, F7 = 320, 760


def cup_pass(c, g, el_t, d):
    """杯子：第 2 拍出现在主角手上，第 4 拍交到对方手里。"""
    hx, hy = H7 + GIVE["hand"][0], GROUND + GIVE["hand"][1]
    fx, fy = F7 + GIVE_F["hand"][0], GROUND + GIVE_F["hand"][1]
    a = clamp01(g.since(2) / 0.3)
    if a <= 0:
        return
    k = ease_in_out(clamp01((g.since(4) + 0.4) / 0.4)) if g.since(4) > -0.4 else 0.0
    x, y = lerp(hx + 8, fx - 8, k), lerp(hy, fy, k) - 30 - 30 * math.sin(math.pi * k)
    cup(c, x, y, 1.15, 0.75, a)


def bond(c, g, el_t, d):
    p = ease_out(clamp01(g.since(6) / 0.5))
    hh = (H7 + GIVE["head"][0], GROUND + GIVE["head"][1] - 110)
    fh = (F7 + GIVE_F["head"][0], GROUND + GIVE_F["head"][1] - 110)
    if p > 0:
        path = K.curve_path(hh, fh, -0.25)
        stroke_path(c, path, K.GOLD, 10, 1, p, glow=(K.tint(K.GOLD, 0.3), 10))
        for (x, y) in (hh, fh):
            K.dot(c, x, y, 16 * ease_out_back(clamp01(p * 2), 2), K.GOLD)
    w = clamp01(g.since(8) / 0.6)
    if w > 0:
        cx, cy = H7 + GIVE["head"][0] * 0.4, GROUND - 200
        K.spotlight(c, cx, cy, 330 * ease_out(w), K.GOLD, 0.55)
        K.ripple(c, cx, cy, g.since(8), K.GOLD, 300, 10, 0.8, 0.8)


# ---------------------------------------------------------------- 第 8 镜：夜里独自浇水

NIGHT = "#2F3357"


def night(g):
    c = g.c
    with K.paper(c, 1, 0.6):
        K.rr(c, 540, 772, 880, 820, 36, NIGHT)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(100, 362, 880, 820), 36, 36), doAntiAlias=True)
    rng = np.random.default_rng(5)
    for i in range(30):
        x, y = 120 + rng.random() * 840, 380 + rng.random() * 430
        tw = 0.5 + 0.5 * math.sin(g.t * (1.5 + rng.random() * 2) + i)
        K.dot(c, x, y, 2 + 2.5 * rng.random(), "#FFFFFF", 0.3 + 0.6 * tw)
    K.dot(c, 820, 470, 58, "#F3E9C6")
    K.dot(c, 846, 452, 50, NIGHT)
    K.rr(c, 540, GROUND + 30, 880, 60, 0, "#262A47")
    c.restore()
    K.ground(c, GROUND, color="#4A4F75", x0=110, x1=970)


def can_prop(tilt_fn):
    def prop(c, h):
        with K.at(c, h[0] + 30, h[1] - 6, tilt_fn()):
            K.icon(c, "can", 0, 0, 120, "#8FA3B8", 1, 0.3)
    return prop


def water(c, g, el_t, d):
    """水滴从壶嘴落到小苗上（第 2 拍起）。"""
    if g.since(2) < 0:
        return
    sx, sy = d["spout"]
    tx, ty = d["target"]
    for i in range(8):
        ph = ((g.since(2) * 1.4) + i / 8) % 1.0
        x = lerp(sx, tx, ph) + 10 * math.sin(i)
        y = lerp(sy, ty, ph) + 60 * ph * ph
        K.dot(c, x, y, 7, "#9CC8EA", 0.9 * (1 - ph * 0.5))


def sprout_big(c, g, el_t, d):
    g1 = 0.3 + 0.35 * ease_out(clamp01(g.since(4) / 0.6)) + 0.35 * ease_out(clamp01(g.since(8) / 0.6))
    K.icon(c, "sprout", 0, 0, 230, K.GREEN, 1, 0.6, 0, 1, g1)
    k = clamp01(g.since(12) / 0.4)
    if k > 0:
        y = -230 - 30 * ease_out(clamp01(g.since(12) / 1.2))
        with K.at(c, 0, y, 0, 0.3 + 0.7 * ease_out_back(k, 2.2)):
            K.heart(c, 0, 0, 70, K.RED)
        K.burst(c, 0, y, g.since(12), K.GOLD, 40, 110, 8, 5)


def empty_seats(c, g, el_t, d):
    for i, x in enumerate((775, 858, 940)):
        K.seat(c, x, GROUND, 70, 70, "#4A4F75")
        K.rr(c, x - 28, GROUND - 105, 14, 80, 6, "#4A4F75")


# ---------------------------------------------------------------- 第 9 镜：倒一杯水，认真听

TABLE_Y = 985
SIT_S = 370


def table(c, g, el_t, d):
    with K.paper(c, 1, 0.8):
        K.rr(c, 540, TABLE_Y, 300, 22, 10, K.shade(ACC, 0.15))
        K.rr(c, 430, (TABLE_Y + GROUND) / 2 + 6, 16, GROUND - TABLE_Y - 10, 6, K.shade(ACC, 0.3))
        K.rr(c, 650, (TABLE_Y + GROUND) / 2 + 6, 16, GROUND - TABLE_Y - 10, 6, K.shade(ACC, 0.3))
    for x in (240, 840):
        K.seat(c, x, GROUND, 130, SIT_S * 0.27, K.tint(K.INK3, 0.2))


def table_cup(c, g, el_t, d):
    """第 1 拍倒满水，第 2 拍推到朋友面前。"""
    fill = 0.75 * ease_out(clamp01(g.since(1) / 0.6))
    k = ease_in_out(clamp01((g.since(2) + 0.35) / 0.35)) if g.since(2) > -0.35 else 0.0
    x = lerp(450, 610, k)
    cup(c, x, TABLE_Y - 42, 1.1, fill, 1)
    if 0 < g.since(1) < 0.6:
        K.seg(c, x + 10, TABLE_Y - 150, x + 4, TABLE_Y - 70, "#8FB8D8", 8, 1 - g.since(1) / 0.6)


def nod_moves(beats, base):
    out = []
    for b in beats:
        out.append((b, dict(pose=dict(base, head=base["head"] + 18), dur=0.2)))
        out.append((b + 0.5, dict(pose=dict(base), dur=0.2)))
    return out


# ---------------------------------------------------------------- 第 10–11 镜：网与圆

def avatar(c, x, y, r, color, hair, mood, lit, face=1, ring=None):
    with K.paper(c, 1, 0.6):
        K.dot(c, x, y, r + 7, ring or (ACC if lit > 0.5 else K.LINE))
        K.dot(c, x, y, r, K.mix(K.PAPER, K.tint(ACC, 0.75), lit))
    c.save()
    path = skia.Path()
    path.addCircle(x, y, r)
    c.clipPath(path, doAntiAlias=True)
    K.figure(c, x, y + 2.4 * r, 2.8 * r, "stand", color, mood=mood, hair=hair, face=face, lift=0.0)
    c.restore()


NET = [  # (x, y, 颜色, 发型, 表情, 朝向)
    (220, 470, PEOPLE[0], "long", "smile", 1), (520, 430, PEOPLE[1], None, "calm", 1),
    (850, 500, PEOPLE[2], "bun", "smile", -1), (160, 760, PEOPLE[3], "bun", "calm", 1),
    (420, 690, K.HERO, "short", "smile", 1), (720, 740, PEOPLE[4], "cap", "happy", -1),
    (920, 860, PEOPLE[0], None, "smile", -1), (300, 1010, PEOPLE[2], "short", "happy", 1),
    (600, 1060, PEOPLE[3], "long", "calm", -1), (840, 1120, PEOPLE[1], "bun", "smile", -1),
]
EDGES = [(0, 1), (1, 2), (0, 3), (0, 4), (1, 4), (1, 5), (2, 5), (2, 6), (3, 4), (4, 5), (5, 6), (3, 7),
         (4, 7), (4, 8), (5, 8), (6, 9), (7, 8), (8, 9), (5, 9)]
ORDER = [4, 1, 5, 0, 8, 3, 7, 2, 6, 9]          # 点亮顺序（从主角开始）
LIGHT_BEAT = [2, 2.5, 3, 4, 4.5, 5, 6, 6.5, 7, 8]
HERO_I = 4


def net_lit(g, i, beats=LIGHT_BEAT):
    j = ORDER.index(i)
    return clamp01(g.since(beats[j]) / 0.25)


def network(c, g, el_t, d):
    lit = [net_lit(g, i) for i in range(len(NET))]
    for a, b in EDGES:
        xa, ya = NET[a][:2]
        xb, yb = NET[b][:2]
        on = min(lit[a], lit[b])
        K.seg(c, xa, ya, xb, yb, K.LINE, 7)
        if on > 0:
            p = ease_out(on)
            K.seg(c, xa, ya, lerp(xa, xb, p), lerp(ya, yb, p), ACC, 7)
    for i, (x, y, col, hair, mood, f) in enumerate(NET):
        a = clamp01((g.since(0) - i * 0.05) / 0.3)
        if a <= 0:
            continue
        r = 66 if i == HERO_I else 56
        with K.at(c, x, y, 0, 0.4 + 0.6 * ease_out_back(a, 2)):
            avatar(c, 0, 0, r, col, hair, mood, lit[i], f, K.GOLD if (i == HERO_I and lit[i] > 0.5) else None)
        K.ripple(c, x, y, g.since(LIGHT_BEAT[ORDER.index(i)]), ACC, 120, 6, 0.6, 0.5)


CIRCLE_R = 340
CX, CY = 540, 800


def ring_pos(i):
    """除主角外的 9 个节点在圆上的位置。"""
    others = [k for k in range(len(NET)) if k != HERO_I]
    j = others.index(i)
    a = -math.pi / 2 + j * math.tau / len(others)
    return CX + CIRCLE_R * math.cos(a), CY + CIRCLE_R * 0.98 * math.sin(a)


def circle_net(c, g, el_t, d):
    k = ease_in_out(clamp01(g.since(2) / 0.8))
    spin = 0.12 * clamp01(g.since(8) / 4.0)
    pos = []
    for i, (x, y, *_r) in enumerate(NET):
        if i == HERO_I:
            pos.append((lerp(x, CX, k), lerp(y, CY, k)))
        else:
            tx, ty = ring_pos(i)
            a = math.atan2(ty - CY, tx - CX) + spin
            tx, ty = CX + CIRCLE_R * math.cos(a), CY + CIRCLE_R * 0.98 * math.sin(a)
            pos.append((lerp(x, tx, k), lerp(y, ty, k)))
    glow = clamp01(g.since(8) / 0.6)
    if glow > 0:
        K.spotlight(c, CX, CY, CIRCLE_R + 200, K.tint(ACC, 0.3), 0.45 * glow)
        path = skia.Path()
        path.addOval(skia.Rect.MakeXYWH(CX - CIRCLE_R, CY - CIRCLE_R * 0.98, 2 * CIRCLE_R, 2 * CIRCLE_R * 0.98))
        stroke_path(c, path, K.GOLD, 10, 0.9, ease_out(glow), glow=(K.tint(K.GOLD, 0.35), 12))
    # 边：网的边渐隐，换成从中心到每个人的辐条
    for a, b in EDGES:
        K.seg(c, *pos[a], *pos[b], ACC, 7, 1 - k)
    hk = clamp01(g.since(4) / 0.4)
    for i in range(len(NET)):
        if i != HERO_I:
            K.seg(c, *pos[HERO_I], *pos[i], K.GOLD if hk > 0 else ACC, 6, k * (0.5 + 0.5 * hk))
    for i, (x, y, col, hair, mood, f) in enumerate(NET):
        px, py = pos[i]
        if i == HERO_I:
            r = lerp(66, 96, ease_out_back(hk, 1.8))
            if hk > 0:
                glow_rays(c, px, py, r + 20, r + 90, hk, K.GOLD, 14, g.t)
            avatar(c, px, py, r, col, hair, "happy" if hk > 0.5 else mood, 1, f, K.GOLD)
        else:
            avatar(c, px, py, 56, col, hair, "happy" if glow > 0.5 else mood, 1, f, ACC)
    K.ripple(c, CX, CY, g.since(12), K.GOLD, CIRCLE_R + 140, 12, 0.8, 0.9)


# ---------------------------------------------------------------- 第 12 镜：小事清单

ITEMS = [("倒水", "water"), ("让座", "seat"), ("说谢谢", "bubble")]


def checklist(c, g, el_t, d):
    w, h = 680, 620

    def body(c, w_, h_):
        K.text(c, "今天", -w_ / 2 + 60, -h_ / 2 + 80, 44, "serif_black", ACC, 1, "left")
        K.seg(c, -w_ / 2 + 60, -h_ / 2 + 130, w_ / 2 - 60, -h_ / 2 + 130, K.LINE, 4)
        for i, (name, ic) in enumerate(ITEMS):
            y = -h_ / 2 + 230 + i * 140
            a = clamp01((g.since(1 + i * 0.5)) / 0.3)
            bx = -w_ / 2 + 110
            K.rr_stroke(c, bx, y, 70, 70, 14, K.INK2, 6, a)
            K.text(c, name, bx + 80, y, 54, "serif", K.INK, a, "left")
            ix = w_ / 2 - 110
            if ic == "water":
                K.icon(c, "water", ix, y, 80, "#7FA6C2", a, 0.3)
            elif ic == "seat":
                with K.paper(c, a, 0.3):
                    K.rr(c, ix - 22, y - 12, 13, 62, 5, K.shade(K.OTHER3, 0.15))
                    K.rr(c, ix + 2, y + 14, 62, 14, 5, K.OTHER3)
                    K.rr(c, ix - 22, y + 38, 9, 36, 3, K.shade(K.OTHER3, 0.15))
                    K.rr(c, ix + 27, y + 38, 9, 36, 3, K.shade(K.OTHER3, 0.15))
            else:
                with K.fade(c, a):
                    K.bubble(c, ix, y - 6, "谢", 38, (0, 1), 1, 1, K.tint(ACC, 0.8), ACC)
            k = clamp01(g.since(4 + i * 4) / 0.35)
            if k > 0:
                path = skia.Path()
                path.moveTo(bx - 26, y - 2)
                path.lineTo(bx - 6, y + 22)
                path.lineTo(bx + 34, y - 30)
                stroke_path(c, path, K.GREEN, 13, 1, ease_out(k))
                K.burst(c, bx, y, g.since(4 + i * 4), K.GOLD, 40, 110, 8, 5)

    K.card(c, 0, 0, w, h, K.PAPER, 1, 24, 1.0, -1.5, 1, ACC, body)


# ---------------------------------------------------------------- 第 13 镜：小岛之间架起桥

ISLES = [(192, 925, 205, K.OTHER, "long", 1), (420, 965, 205, K.HERO, "short", 1),
         (662, 915, 215, K.OTHER3, "bun", -1), (885, 955, 195, "#9C8FB0", None, -1)]
SEA_Y = 935


def sea(g):
    c = g.c
    for i, (x, y, s_) in enumerate(((230, 470, 170), (600, 400, 120))):
        K.icon(c, "cloud", x + 14 * math.sin(g.t * 0.5 + i), y, s_, "#FFFFFF", 0.95, 0.5)
    K.icon(c, "sun", 850, 500, 190, K.GOLD, g.p(0, 0.5), 0.6, 0, 1, g.t * 0.3)
    sh = skia.GradientShader.MakeLinear([(0, SEA_Y), (0, 1230)], [K.col("#9CC3DA"), K.col("#7FA6C2")])
    c.drawRoundRect(skia.Rect.MakeLTRB(85, SEA_Y, 995, 1230), 30, 30, skia.Paint(AntiAlias=True, Shader=sh))
    for k in range(6):
        y = SEA_Y + 60 + k * 44
        path = skia.Path()
        x0 = 100 + (k % 2) * 40 + 20 * math.sin(g.t * 1.2 + k)
        path.moveTo(x0, y)
        for j in range(8):
            path.quadTo(x0 + j * 110 + 27, y - 10, x0 + j * 110 + 55, y)
            path.quadTo(x0 + j * 110 + 82, y + 10, x0 + j * 110 + 110, y)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(95, SEA_Y, 985, 1225))
        c.drawPath(path, K.paint("#FFFFFF", 0.35, 4))
        c.restore()


def islands(c, g, el_t, d):
    for i, (x, y, w, col, hair, f) in enumerate(ISLES):
        with K.paper(c, 1, 0.6):
            c.drawOval(skia.Rect.MakeXYWH(x - w / 2, y - 20, w, 90), K.paint("#D9C49A"))
            c.drawOval(skia.Rect.MakeXYWH(x - w / 2 + 10, y - 30, w - 20, 52), K.paint(K.GREEN))
        mood = "happy" if g.since(6) > 0 else ("calm" if i != 1 else "smile")
        pose = ("wave" if i % 2 == 0 else "cheer") if g.since(6) > 0 else "stand"
        k = clamp01(g.since(6) / 0.3)
        p = K.blend("stand", pose, k) if pose != "stand" else "stand"
        K.figure(c, x, y - 10, 235, p, col, mood=mood, hair=hair, face=f, bob=idle_bob(g, x), lift=0.6)


def bridges(c, g, el_t, d):
    for j, b in enumerate((2, 3, 4)):
        x0 = ISLES[j][0] + ISLES[j][2] / 2 - 30
        x1 = ISLES[j + 1][0] - ISLES[j + 1][2] / 2 + 30
        y0, y1 = ISLES[j][1] - 14, ISLES[j + 1][1] - 14
        p = ease_out(clamp01((g.t - (g.b(b) - 0.35)) / 0.35))
        if p <= 0:
            continue
        path = K.curve_path((x0, y0), (x1, y1), -0.28)
        pm = skia.PathMeasure(path, False)
        L = pm.getLength()
        n = 9
        with K.paper(c, 1, 0.5):
            stroke_path(c, path, K.shade("#C9A47E", 0.2), 8, 1, p)
            for q in range(n):
                t = (q + 0.5) / n
                if t > p:
                    break
                pos, tan = pm.getPosTan(L * t)
                ang = math.degrees(math.atan2(tan.y(), tan.x()))
                with K.at(c, pos.x(), pos.y() - 4, ang):
                    K.rr(c, 0, 0, L / n - 4, 22, 3, "#C9A47E")
        if g.since(b) >= 0:
            K.burst(c, (x0 + x1) / 2, min(y0, y1) - 40, g.since(b), K.GOLD, 30, 90, 8, 5)


# ---------------------------------------------------------------- 本期

def build() -> Episode:
    give_f_hand = GIVE_F["hand"]
    shots = [
        # 1
        Shot(3, "升职、加薪、被夸奖……|开心一阵就过去了。", "情境演绎", [
            Custom(perks, at=0, enter="none"),
            Fig(BOSS_X, GROUND, 350, at=0, color=K.OTHER2, hair="cap", face=-1, mood="smile", pose="give",
                moves=[(2.5, dict(pose="stand"))]),
            Custom(hero_trophy, x=360, y=GROUND, at=0, enter="rise", s=370, mood="smile", glow=1.0,
                   moves=[(1.5, dict(pose="give", mood="open")),
                          (3, dict(pose="wave", mood="happy")),
                          (6, dict(glow=0.65, mood="smile", sfx="wood_low", gain=0.9, note="奖杯的光暗了一截")),
                          (8, dict(glow=0.35, mood="calm", pose="stand", sfx="wood_low", gain=0.75,
                                   note="又暗一截")),
                          (10, dict(glow=0.0, mood="flat", sfx="wood_low", gain=0.6, note="光灭了"))]),
        ], draw=ground, hits=[(2, "clap", 0.9, "主角接过奖杯")],
            note="升职、加薪、被夸奖的小图标浮起；主角接过奖杯高高举起，奖杯的光按拍一截截变暗，笑容也淡了"),
        # 2
        Shot(3, "帮朋友搬了一次家，|却开心了好几天。", "情境演绎", [
            Icon("house", 888, 1000, 180, color=K.tint(ACC, 0.3), accent=K.GOLD, p=1, at=0, enter="pop"),
            Custom(box_pair, x=140, y=GROUND, at=0, enter="none", x0=140, x1=420, mood="smile",
                   moves=[(0.5, dict(x=420, dur=2.8)), (6, dict(mood="happy"))]),
            Custom(hearts, at=0, enter="none"),
        ], draw=ground, hits=[(4, "bongo_high", 0.85, "第一颗爱心飘起"), (6, "bongo_low", 0.8, "第二颗"),
                              (8, "bongo_high", 0.75, "第三颗"), (10, "shaker", 0.7, "第四颗")],
            note="主角和朋友一起抬着纸箱走向新家，爱心按拍一颗颗飘起，停在半空不散"),
        # 3
        Shot(2, "差别|在哪儿？", "情境演绎", [
            Custom(panel(panel_trophy), x=290, y=780, at=1, enter="slide_l", tilt=-2, sfx="wood_low",
                   note="左屏：举着暗掉的奖杯"),
            Custom(panel(panel_move), x=790, y=780, at=2, enter="slide_r", tilt=2, sfx="wood_high",
                   note="右屏：一起搬家，爱心不散"),
            Icon("question", 540, 780, 140, color=ACC, at=4, enter="slam", dur=0.22, sfx="rim", note="中间砸下问号"),
        ], text_beat=0, note="左右分屏：左边举着暗掉的奖杯“开心一阵”，右边一起搬家“开心好几天”，中间砸下问号"),
        # 4（drop）
        Shot(3, "把自己当作|共同体的一员。", "阿德勒原著", [
            Big("共同体感觉", 540, 500, 140, at=0, sfx="kick", sub="Gemeinschaftsgefühl · 社会兴趣",
                note="概念落版（音乐 drop）"),
            *[Fig(x, GROUND, s, at=0.5 + i * 0.25, color=col, hair=hair, face=f, mood="smile",
                  moves=[(8, dict(pose="cheer" if i % 2 else "wave", mood="happy"))])
              for i, (x, s, col, hair, f) in enumerate(ROW)],
            Fig(540, GROUND, 340, at=4, enter="drop", dur=0.4, hair="short", mood="open", sfx="tom",
                note="主角落进队伍中间的空位", moves=[(8, dict(pose="cheer", mood="happy"))]),
            Custom(links_row, at=0, enter="none"),
        ], draw=ground, hits=[(6, "shaker", 0.8, "大家之间连上线"), (8, "wood_high", 0.85, "一圈光环把所有人围在一起")],
            note="drop 处“共同体感觉”砸下；一排人中间留着空位，主角落进去，大家之间连上线，光环把所有人围在一起"),
        # 5
        Shot(3, "阿德勒学派把它|看作心理健康的标尺。", "阿德勒学派", [
            Custom(gauge, at=0, enter="fade"),
            Label("共同体感觉", GX, GY1 + 70, 34, at=0.5, fill=ACC),
            Fig(270, GROUND, 340, at=0, hair="short", mood="calm", pose="think",
                moves=[(8, dict(pose="point", mood="smile"))]),
        ], draw=ground, hits=[(2, "wood_low", 0.85, "刻度填到第一格"), (4, "wood_low", 0.75, "第二格"),
                              (6, "wood_high", 0.8, "第三格"), (8, "bongo_high", 0.9, "填满，顶端的心亮起")],
            note="一支竖着的刻度计按拍一格格填满，顶端的心亮起；主角在旁边指着它"),
        # 6
        Shot(3, "“对他人不感兴趣的人，|生活中困难最多。”", "阿德勒原著 · 大意", [
            Fig(270, GROUND, 300, at=0, color="#8A8F99", hair="short", mood="flat", face=1,
                moves=[(2, dict(pose="block", mood="worried")), (8, dict(pose="cover", mood="sad"))]),
            Custom(wall, x=270, y=GROUND, at=2, enter="none", sfx="wood_low", note="围墙升起，把他围在里面"),
            Custom(storm, x=270, y=560, at=8, enter="pop", sfx="rim", note="乌云和雨落在围墙里"),
            *[Fig(x, GROUND, s, at=0.5 + i * 0.25, color=col, hair=hair, face=f, mood="smile",
                  moves=[(6, dict(pose="wave", mood="happy"))] if i == 1 else [])
              for i, (x, s, col, hair, f) in enumerate(GROUP)],
            Custom(group_links, at=0, enter="none"),
        ], draw=ground, hits=[(4, "shaker", 0.8, "墙外的人互相连上线")],
            note="左边一个人被围墙围住，头顶落下乌云和雨；右边三个人之间连着发光的线"),
        # 7
        Shot(3, "感到“我对别人有用”，|就能感到自己的价值。", "岸见一郎阐释", [
            Custom(bond, at=0, enter="none"),
            Fig(H7, GROUND, 360, at=0, hair="short", mood="calm",
                moves=[(1.5, dict(pose="give", mood="smile")), (8, dict(mood="happy"))]),
            Fig(F7, GROUND, 340, at=0, color=FRIEND, hair="long", face=-1, mood="worried",
                moves=[(3.3, dict(pose="give")), (4, dict(mood="happy", sfx="wood_high", note="对方接过杯子，笑了"))]),
            Custom(cup_pass, at=0, enter="none", sfx=None),
        ], hits=[(2, "wood_low", 0.85, "主角递出水杯"), (6, "shaker", 0.8, "两人之间亮起连线"),
                 (8, "bongo_high", 0.9, "主角身上发出暖光")],
            draw=ground, note="主角递出水杯，对方接过笑了；两人之间亮起金色连线，主角身上发出暖光"),
        # 8
        Shot(4, "这不是自我牺牲，|也不必等别人来认可。", "常见误解", [
            Custom(empty_seats, at=0, enter="fade"),
            Custom(sprout_big, x=640, y=1045, at=0, enter="none"),
            Custom(water, at=0, enter="none", spout=(592, 935), target=(645, 1035)),
            Fig(330, GROUND, 340, at=0, enter="none", hair="short", mood="calm", pose="give",
                prop=can_prop(lambda: 0),
                moves=[(1.6, dict(prop=can_prop(lambda: 28))), (12, dict(mood="smile"))]),
        ], draw=night, hits=[(2, "shaker", 0.75, "壶里的水落下"), (4, "wood_low", 0.85, "小苗长高"),
                             (8, "wood_low", 0.7, "小苗再长高"), (12, "bongo_high", 0.85, "小苗上冒出一颗小爱心")],
            note="夜里主角独自给小苗浇水，旁边的观众席空着；小苗按拍长高，冒出一颗小爱心"),
        # 9
        Shot(3, "倒一杯水，|认真听人把话说完，", "情境演绎", [
            Custom(table, at=0, enter="fade"),
            Fig(240, GROUND, SIT_S, at=0, enter="none", hair="short", pose="sit", mood="calm",
                moves=[(1.5, dict(pose="sit", mood="smile"))] + nod_moves((4, 5, 6), K.POSES["sit"])),
            Fig(840, GROUND, SIT_S, at=0, enter="none", color=K.OTHER, hair="bun", face=-1, pose="sit_sad",
                mood="worried", moves=[(8, dict(pose="sit", mood="smile"))]),
            Custom(table_cup, at=0, enter="none"),
            Bubble("其实，我最近……", 750, 590, 44, at=4, tail=(0.3, 1), sfx="wood_high",
                   note="对方开口说话，主角点头倾听"),
            Custom(lambda c, g, t, d: K.heart(c, 0, -25 * ease_out(clamp01(t / 1.0)), 60, K.RED, clamp01(t / 0.3)),
                   x=540, y=820, at=8, enter="pop", sfx="bongo_low", note="对方笑了，桌上方冒出小爱心"),
        ], hits=[(2, "wood_low", 0.85, "主角把水杯推到朋友面前")], draw=ground,
            note="两人隔桌坐着：主角倒好一杯水推过去，对方开口说话，主角一下下点头倾听，对方笑了"),
        # 10
        Shot(3, "都是在为|身边的共同体出一份力。", "机制示意", [
            Custom(network, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.85, "主角这个节点先亮"), (4, "wood_low", 0.8, "亮光沿线传开"),
                 (6, "wood_high", 0.75, "更多节点亮起"), (8, "bongo_high", 0.85, "最后一个节点亮起")],
            note="很多人之间连成一张网，从主角开始，节点按拍一个个点亮，亮光沿着线传开"),
        # 11
        Shot(4, "阿德勒说，人生的意义|在于关心他人、贡献整体。", "阿德勒原著 · 大意", [
            Custom(circle_net, at=0, enter="none"),
        ], cut=True, hits=[(2, "shaker", 0.8, "网收拢成一个大圆"), (4, "tom", 0.85, "主角在圆心亮起"),
                           (8, "cymbal", 0.6, "整张网发光"), (12, "wood_high", 0.8, "光圈向外扩散")],
            note="网收拢成一个大圆，主角在圆心，和每个人连着线；整张网发光，光圈向外扩散"),
        # 12
        Shot(4, "今天，做一件|“对别人有用”的小事。", "小练习", [
            Custom(checklist, x=540, y=800, at=0, enter="pop", sfx="shaker", note="清单弹出"),
        ], hits=[(4, "wood_high", 0.9, "勾上“倒水”"), (8, "bongo_high", 0.85, "勾上“让座”"),
                 (12, "clap", 0.85, "勾上“说谢谢”")],
            note="一张“今天”清单：倒水、让座、说谢谢，按拍一项项打勾"),
        # 13
        Shot(2, "你不是孤岛，|你是连接的一部分。", "阿德勒的视角", [
            Custom(islands, at=0, enter="fade"),
            Custom(bridges, at=0, enter="none"),
        ], draw=sea, hits=[(2, "wood_low", 0.85, "第一座桥架起"), (4, "wood_high", 0.8, "第三座桥架起"),
                           (6, "bongo_high", 0.85, "岛上的人互相挥手")],
            note="海上一座座小岛，桥按拍一座座架起来，岛上的人互相挥手"),
        end_shot(["Adler, A. (1931). What Life Should Mean to You, ch.1.（中译《自卑与超越》）",
                  "Ansbacher, H. L. (1968). The concept of social interest. J. Individual Psychology, 24, 131–149.",
                  "岸见一郎、古贺史健（2013）《被讨厌的勇气》第五夜"], None),
    ]
    return Episode(10, "community", "共同体感觉", "人在什么时候，会觉得自己有价值？", ACC, shots,
                   refs=["Adler, A. (1931). What Life Should Mean to You, ch.1.（中译《自卑与超越》）",
                         "Ansbacher, H. L. (1968). The concept of social interest. J. Individual Psychology, 24, "
                         "131–149.",
                         "岸见一郎、古贺史健（2013）《被讨厌的勇气》第五夜"],
                   publish_title="人在什么时候，会觉得自己有价值？｜阿德勒心理学10 共同体感觉",
                   hashtags="#阿德勒 #心理学 #幸福感 #人际关系 #被讨厌的勇气",
                   cover_title="人在什么时候，|会觉得自己【有价值】？", cover_sub="阿德勒的共同体感觉",
                   cover_shot=10, cover_t=6.5,
                   notes=[
                       "共同体感觉（Gemeinschaftsgefühl，英译 social interest）是阿德勒晚期的核心概念，阿德勒学派以它作为心理健康的"
                       "衡量标准（Ansbacher 1968）。",
                       "第 6 镜为 What Life Should Mean to You 原句大意：“It is the individual who is not interested in his "
                       "fellow men who has the greatest difficulties in life and provides the greatest injury to others.”",
                       "第 11 镜为第 1 章原句大意：“Life means—to be interested in my fellow men, to be part of the whole, to "
                       "contribute my share to the welfare of mankind.”",
                       "“贡献感”（幸福就是贡献感）是《被讨厌的勇气》第五夜的表述，第 7 镜标注“岸见一郎阐释”。",
                   ]).build()
