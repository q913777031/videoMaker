"""05 人生课题：为什么烦恼，总和人有关？"""

import math

import skia

from engine import gfx
from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, ease_out_back, lerp

from . import kit as K
from .core import Big, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

ACC = "#3A5BA0"
GROUND = 1130
CLOUD = "#9AA0AC"
STORM = "#6E7382"
HEART = K.RED


# ---------------------------------------------------------------- 通用小工具

def ground(g):
    K.ground(g.c, GROUND)


def pose_at(g, base, keys):
    """按 [(拍, 姿势)] 关键帧求当前姿势（与引擎 Fig 相同的 0.45 秒缓动）。"""
    cur = prev = base
    for b, p in keys:
        k = clamp01(g.since(b) / 0.45)
        if k <= 0:
            break
        cur = K.blend(prev, p, ease_in_out(k)) if k < 1 else p
        prev = p
    return cur


def val_at(g, base, keys, dur=0.45):
    """按 [(拍, 数值)] 关键帧求当前数值。"""
    v = base
    for b, x in keys:
        k = clamp01(g.since(b) / dur)
        if k <= 0:
            break
        v = lerp(v, x, ease_in_out(k))
    return v


def joints(s, p="stand", face=1):
    """与 kit.figure 相同的几何：返回头心、近手、远手、眼睛（相对脚底中点）。"""
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
    return dict(head=head, near=near, far=far, chest=(sh_x * 0.6, sh_y + 0.1 * u))


def lightning(c, x, y, s, color=K.GOLD, alpha=1.0):
    K.poly(c, [(x - 0.1 * s, y - 0.5 * s), (x + 0.22 * s, y - 0.5 * s), (x + 0.04 * s, y - 0.08 * s),
               (x + 0.26 * s, y - 0.08 * s), (x - 0.18 * s, y + 0.5 * s), (x - 0.02 * s, y + 0.02 * s),
               (x - 0.24 * s, y + 0.02 * s)], color, alpha)


# ---------------------------------------------------------------- 1 三朵乌云

def fall(g, beat, dist=170, dur=0.3):
    """自定义落下：在 beat 拍落定（撞击帧 = 拍点），之后轻微回弹；返回 (dy, 纵向压缩) 或 None。"""
    dt = g.since(beat)
    if dt < -dur:
        return None
    if dt < 0:
        return -dist * (1 - ease_in(1 + dt / dur)), 1.0
    q = clamp01(dt / 0.28)
    return -10 * math.sin(q * math.pi), 1 - 0.1 * math.sin(q * math.pi)


def storm_cloud(c, g, t, d):
    """灰云从上方落到主角头顶（第 d['land'] 拍落定），云肚子里是课题图标；d['rain'] 拍起下雨。"""
    f = fall(g, d["land"])
    if f is None:
        return
    with K.at(c, 0, f[0], 0, 1, f[1]):
        _cloud_body(c, g, d)


def _cloud_body(c, g, d):
    s = d.get("cs", 240)
    rt = g.since(d.get("rain", 99))
    if rt > 0:
        for i in range(5):
            x = (i - 2) * s * 0.17
            ph = (rt * 2.2 + i * 0.37) % 1.0
            y0 = s * 0.28 + ph * 150
            K.seg(c, x, y0, x - 6, y0 + 34, "#8C93A3", 6, 0.8 * clamp01(rt / 0.3) * (1 - ph * 0.6))
    K.icon(c, "cloud", 0, 0, s, d.get("ccol", CLOUD), 1, 0.9)
    K.icon(c, d["name"], 0, s * 0.02, s * 0.34, "#F4F1EA", 1, 0.0, accent="#F4F1EA")


# ---------------------------------------------------------------- 2–3 三个房间

ROOMS = (("工作", 215), ("交友", 540), ("爱", 865))
RW, RH, RY, FL = 290, 440, 800, 150
LIT_X = (80, 92, 62)      # 每个房间里“他人”的位置


def room(c, g, t, d):
    """一个房间格子：i=0 工作 / 1 交友 / 2 爱；act 拍起房间里的冲突发生；lit 拍起“他人”被点亮。"""
    i, act, lit = d["i"], d["act"], d.get("lit", 99)
    ka = ease_out(clamp01(g.since(act) / 0.45))
    with K.paper(c, 1, 0.8):
        K.rr(c, 0, 0, RW, RH, 26, K.PAPER)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-RW / 2, -RH / 2, RW, RH), 26, 26), True)
    K.rr(c, 0, FL + 40, RW, 80, 0, K.mix(K.LINE, K.PAPER, 0.45))
    lt = g.since(lit)
    ox = LIT_X[i]
    if lt >= 0:
        K.spotlight(c, ox, FL - 95, 150, K.GOLD, 0.6 * clamp01(lt / 0.3))
        K.ripple(c, ox, FL - 95, lt, K.GOLD, 150, 6, 0.9)
    lit_mood = "open" if lt >= 0 else None
    if i == 0:
        # 墙上的下跌曲线 + 上司指责
        K.rr(c, -10, -120, 170, 110, 10, K.mix(K.LINE, K.PAPER, 0.6))
        pts = [(-80, -150), (-40, -135), (-5, -140), (30, -110), (65, -85)]
        path = skia.Path()
        path.moveTo(*pts[0])
        for q in pts[1:]:
            path.lineTo(*q)
        gfx.stroke_path(c, path, K.RED, 7, 1.0, 0.45 + 0.55 * ka)
        K.figure(c, -75, FL, 165, K.blend("stand", "sad", ka), K.HERO, mood="sad" if ka > 0.5 else "worried",
                 hair="short", lift=0.4)
        K.figure(c, ox, FL, 175, K.blend("stand", "point", ka), K.OTHER2, face=-1,
                 mood=lit_mood or ("angry" if ka > 0.5 else "flat"), lift=0.4)
    elif i == 1:
        # 朋友转身走远
        x = lerp(36, ox, ka)
        walking = 0 < ka < 1
        p = K.walk((x - 36) / 40, math.sin(math.pi * ka)) if walking else "stand"
        K.figure(c, -70, FL, 165, K.blend("stand", "reach", ka), K.HERO, mood="sad" if ka > 0.5 else "calm",
                 hair="short", lift=0.4)
        K.figure(c, x, FL, 165, p, K.OTHER, face=1 if ka > 0.15 else -1, mood=lit_mood or "flat", hair="bun",
                 lift=0.4)
    else:
        # 两人争吵，中间一道闪电
        K.figure(c, -62, FL, 165, K.blend("stand", "block", ka), K.HERO, mood="angry" if ka > 0.5 else "flat",
                 hair="short", lift=0.4)
        K.figure(c, ox, FL, 160, K.blend("stand", "point", ka), K.OTHER3, face=-1,
                 mood=lit_mood or ("angry" if ka > 0.5 else "flat"), hair="long", lift=0.4)
        if ka > 0:
            with K.at(c, 0, FL - 205, 0, 0.4 + 0.6 * ease_out_back(clamp01(g.since(act) / 0.3), 2)):
                lightning(c, 0, 0, 70, K.GOLD)
    c.restore()
    K.pill(c, 0, -RH / 2 - 40, ROOMS[i][0], 32, ACC)


def room_els(act, lit=None, enter="pop", ats=(1, 3, 5), sfx=(None, None, None), notes=("", "", "")):
    out = []
    for i, (name, x) in enumerate(ROOMS):
        kw = dict(i=i, act=act[i] if isinstance(act, tuple) else act)
        if lit:
            kw["lit"] = lit[i]
        out.append(Custom(room, x=x, y=RY, at=ats[i], enter=enter, sfx=sfx[i], note=notes[i], gain=1.0, **kw))
    return out


def common_thread(g):
    """第 3 镜：三个被点亮的“他人”被一条虚线串起来。"""
    k = ease_out(clamp01(g.since(6) / 0.6))
    if k <= 0:
        return
    pts = [(ROOMS[i][1] + LIT_X[i], RY + FL - 160) for i in range(3)]
    path = skia.Path()
    path.moveTo(*pts[0])
    path.quadTo(pts[0][0] + 170, pts[0][1] - 230, *pts[1])
    path.quadTo(pts[1][0] + 150, pts[1][1] - 230, *pts[2])
    gfx.stroke_path(g.c, path, ACC, 7, 0.95, k, dash=(18, 14, 0))
    for i, (x, y) in enumerate(pts):
        if k > i / 3:
            K.dot(g.c, x, y, 11, ACC)


# ---------------------------------------------------------------- 5 三角关系图

HUB = (540, 1000)
NODES = ((540, 440, "brief", K.OTHER2, None, "工作", (695, 440)),
         (255, 915, "friends", K.OTHER, "bun", "交友", (255, 1055)),
         (825, 915, "heart", K.OTHER3, "long", "爱", (825, 1055)))


def node_disc(c, g, t, d):
    """圆形头像：课题里的那个“他人”，右上角是课题图标。"""
    r = 92
    _, _, icon, colr, hair, _, _ = NODES[d["i"]]
    with K.paper(c, 1, 0.9):
        K.dot(c, 0, 0, r, K.PAPER)
    c.save()
    path = skia.Path()
    path.addCircle(0, 0, r - 9)
    c.clipPath(path, doAntiAlias=True)
    K.dot(c, 0, 0, r - 9, K.tint(colr, 0.7))
    lit = g.since(8) >= 0
    K.figure(c, 0, 205, 230, "stand", colr, mood="smile" if lit else "calm", hair=hair, lift=0,
             face=-1 if d["i"] == 2 else 1)
    c.restore()
    K.icon(c, icon, r * 0.74, -r * 0.74, 74, HEART if icon == "heart" else K.DARK, 1, 0.6, accent=ACC)


def links(c, g, t, d):
    """主角与三个课题里的他人之间的连线：第 2/4/6 拍依次画出，第 8 拍亮起并有光点来回流动。"""
    hx, hy = HUB[0], HUB[1] - 190
    ends = [((540, 700), (540, 536)), ((485, 835), (345, 893)), ((595, 835), (735, 893))]
    lit = clamp01(g.since(8) / 0.3)
    for i, (a, b) in enumerate(ends):
        p = ease_out(clamp01(g.since(2 + 2 * i) / 0.4))
        if p <= 0:
            continue
        path = skia.Path()
        path.moveTo(*a)
        path.lineTo(*b)
        gfx.stroke_path(c, path, K.mix(K.INK3, ACC, lit), 8 + 3 * lit, 1.0, p)
        if lit > 0:
            for j in range(2):
                q = (g.since(8) * 0.9 + j * 0.5) % 1.0
                K.dot(c, lerp(a[0], b[0], q), lerp(a[1], b[1], q), 9, K.GOLD)
    K.ripple(c, hx, hy, g.since(8), ACC, 240, 7, 0.8)


def orbit(c, g, t, d):
    k = ease_out(clamp01(g.since(1) / 0.8))
    if k > 0:
        K.ring(c, 540, 760, 330, K.LINE, 5, 0.9, k, -90)


# ---------------------------------------------------------------- 6 书里翻出的卡片

def flip_card(c, g, t, d):
    """卡片从书里升起并翻面：前半程是背面（强调色），后半程翻出正面文字。"""
    k = clamp01(g.since(2) / 0.6)
    if k <= 0:
        return
    e = ease_out(k)
    y = lerp(330, 0, e)
    sy = abs(math.cos(math.pi * (1 - e)))
    sc = lerp(0.35, 1, e)
    with K.at(c, 0, y, 0, sc, sc * max(sy, 0.02)):
        if e < 0.5:
            K.card(c, 0, 0, 420, 230, ACC, 1, 22, 1.0)
        else:
            K.text_card(c, 0, 0, ["烦恼都来自", "【人际关系】"], 58, 440, K.PAPER, K.INK, ACC, 1, 0, 1, accent=ACC)
    K.burst(c, 0, 0, g.since(2.6), K.GOLD, 200, 330, 12, 7)


# ---------------------------------------------------------------- 7 只剩一人的星球

PLANET = (540, 1005, 255)
STARS = ((150, 430, 1), (330, 560, 2), (890, 430, 3), (770, 600, 1.5), (175, 740, 2.5), (950, 770, 3.5),
         (470, 390, 4), (650, 470, 2), (95, 590, 5), (990, 590, 4.5), (300, 380, 6), (820, 360, 7))


def planet(c, g, t, d):
    cx, cy, r = 0, 0, PLANET[2]
    K.spotlight(c, cx, cy, r * 1.6, ACC, 0.16)
    with K.paper(c, 1, 1.0):
        K.dot(c, cx, cy, r, K.mix(ACC, K.PAPER, 0.5))
        c.save()
        path = skia.Path()
        path.addCircle(cx, cy, r)
        c.clipPath(path, doAntiAlias=True)
        K.dot(c, cx + r * 0.35, cy + r * 0.3, r * 0.95, K.mix(ACC, K.PAPER, 0.38))
        for x, y, rr_ in ((-90, 60, 34), (60, 120, 22), (110, -10, 16), (-30, 160, 18)):
            K.dot(c, x, y, rr_, K.mix(ACC, K.PAPER, 0.3))
        c.restore()


def stars(g):
    for x, y, b in STARS:
        k = clamp01(g.since(b) / 0.3)
        if k <= 0:
            continue
        tw = 0.75 + 0.25 * math.sin(g.t * 3 + x)
        K.star(g.c, x, y, 24 * ease_out_back(k, 2) * tw, K.GOLD, 0.9)


def on_planet(theta, s, **kw):
    """站在星球表面 theta 度处的人。"""
    cx, cy, r = PLANET
    a = math.radians(theta)
    x, y = cx + r * math.sin(a), cy - r * math.cos(a)
    out = kw.pop("leave")
    lx, ly = x + 140 * math.sin(a), y - 140 * math.cos(a)
    return Fig(x, y + 4, s, rot=theta, alpha=1.0, walk=False, lift=0.6, enter="none",
               moves=[(out, dict(x=lx, y=ly, alpha=0.0, dur=0.6, sfx=kw.pop("sfx"), note=kw.pop("note"),
                                 gain=kw.pop("gain", 0.9)))], **kw)


# ---------------------------------------------------------------- 8 帘子后面

def curtain(c, g, t, d):
    """帘子：杆 + 竖褶布，左缘随时间轻轻摆动。"""
    x0, x1, top = 600, 1000, 430
    base, dark = "#B4584A", "#93453B"
    K.rr(c, (x0 + x1) / 2, top - 18, x1 - x0 + 24, 18, 9, K.DARK)
    with K.paper(c, 1, 0.9):
        n = 9
        w = (x1 - x0) / n
        for i in range(n):
            sway = 6 * math.sin(g.t * 1.7 + i * 0.6) * (1 - i / n)
            path = skia.Path()
            xl = x0 + i * w
            path.moveTo(xl, top)
            path.lineTo(xl + w + 1, top)
            path.lineTo(xl + w + 1 + sway * 0.5, GROUND)
            path.lineTo(xl + sway, GROUND)
            path.close()
            c.drawPath(path, K.paint(base if i % 2 == 0 else dark))
        for i in range(n):
            K.dot(c, x0 + (i + 0.5) * w, top - 4, 9, K.GOLD)


HIDE_X, HIDE_S = (690, 600), 330
HIDE_KEYS = [(4, "reach")]
SIGN_OFF = (-150, -195)


def hide_hand(g):
    """帘子后主角近手的当前位置（与 Fig 的关键帧一致）。"""
    x = val_at(g, HIDE_X[0], [(1, HIDE_X[1])], 0.6)
    j = joints(HIDE_S, pose_at(g, "stand", HIDE_KEYS), -1)
    return x + j["near"][0], GROUND + j["near"][1]


def excuse_sign(c, g, t, d):
    """主角从帘子后伸手举出的牌子：“等我准备好再说”。第 12 拍起发抖。"""
    k = clamp01(g.since(4) / 0.42)
    if k <= 0:
        return
    hx, hy = hide_hand(g)
    cx, cy = hx + SIGN_OFF[0], hy + SIGN_OFF[1]
    shake = 4 * math.sin(g.t * 42) * clamp01(g.since(12) / 0.2) * (1 - clamp01(g.since(14) / 0.5))
    sc = 0.2 + 0.8 * ease_out_back(k, 2.0)
    with K.fade(c, clamp01(k * 3)):
        K.seg(c, hx, hy, lerp(hx, cx, sc) + 50, lerp(hy, cy, sc) + 60, "#8A6A4E", 11)
        K.text_card(c, cx + shake, cy, ["等我准备好", "再说"], 46, 330, K.PAPER, K.INK, ACC, 1, -4 + shake * 0.4, sc)


def lie_stamp(c, g, t, d):
    """“人生的谎言”印章：砸在牌子上。"""
    w, h = 330, 96
    K.rr_stroke(c, 0, 0, w, h, 16, K.RED, 8, 0.95)
    K.rr_stroke(c, 0, 0, w - 22, h - 22, 10, K.RED, 3, 0.8)
    K.text(c, "人生的谎言", 0, -2, 56, "serif_black", K.RED, 0.95)
    K.text(c, "Lebenslüge", 0, h / 2 + 30, 28, "sans_medium", K.RED, 0.85)


# ---------------------------------------------------------------- 9 长椅、日历与时钟

def bench(c, g, t, d):
    """长椅（原点为地面中点）+ 第 10 拍起在椅背角落结出蛛网。"""
    with K.paper(c, 1, 0.7):
        for x in (-130, 120):
            K.rr(c, x, -40, 16, 80, 4, K.DARK)
        K.rr(c, -150, -105, 14, 150, 4, K.DARK)
        K.rr(c, 0, -76, 320, 20, 8, "#A0784F")
        K.rr(c, -138, -150, 20, 120, 6, "#A0784F")
    k = ease_out(clamp01(g.since(10) / 0.6))
    if k > 0:
        cx, cy = -128, -88
        for i in range(5):
            a = math.radians(-90 + i * 22)
            K.seg(c, cx, cy, cx + math.cos(a) * 90 * k, cy + math.sin(a) * 90 * k, K.INK3, 2.5, 0.9)
        for r in (30, 55, 80):
            if r < 90 * k:
                path = skia.Path()
                path.addArc(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), -90, 90)
                c.drawPath(path, K.paint(K.INK3, 0.9, 2.5))


MONTHS = ("3月", "6月", "9月", "12月", "3月", "6月")
FLIPS = (2, 4, 6, 8, 10)


def calendar(c, g, t, d):
    """台历：第 2/4/6/8/10 拍各翻一页（月份越翻越远）。"""
    w, h = 290, 310
    n = sum(g.since(b) >= 0 for b in FLIPS)
    with K.paper(c, 1, 0.9):
        K.rr(c, 0, 0, w, h, 18, K.PAPER)
        K.rr(c, 0, -h / 2 + 34, w, 68, 0, ACC)
        K.rr(c, 0, -h / 2 + 18, w, 36, 18, ACC)
        K.text(c, MONTHS[n], 0, 34, 110, "serif_black", K.INK)
        K.text(c, "等我…", 0, -h / 2 + 36, 30, "sans_medium", K.PAPER)
    for x in (-60, 60):
        K.rr(c, x, -h / 2 - 2, 14, 34, 7, K.DARK)
    if n > 0:
        k = clamp01(g.since(FLIPS[n - 1]) / 0.32)
        if k < 1:
            # 上一页向上翻起
            with K.at(c, 0, -h / 2, 0, 1, max(0.02, 1 - ease_out(k))):
                K.rr(c, 0, h / 2, w, h, 18, K.mix(K.PAPER, K.LINE, 0.3), 1 - k * 0.5)
                K.text(c, MONTHS[n - 1], 0, h / 2 + 34, 110, "serif_black", K.INK2, 1 - k)


# ---------------------------------------------------------------- 10 越来越大的乌云

def growing_cloud(c, g, t, d):
    steps = sum(ease_out_back(clamp01(g.since(b) / 0.35), 2.2) for b in (2, 5, 8))
    s = 150 + 51 * steps
    colr = K.mix(CLOUD, K.DARK, 0.2 * steps)
    lt = g.since(10)
    if d.get("bolt") and lt >= 0:
        a = 1 - clamp01((lt - 0.5) / 0.4)
        lightning(c, 10, s * 0.55, 120, K.GOLD, a)
        if lt < 0.12:
            K.dot(c, 0, 0, s * 0.8, K.GOLD, 0.25)
    K.icon(c, "cloud", 0, 0, s, colr, 1, 0.9)
    if g.since(8) > 0:
        rt = g.since(8)
        for i in range(4):
            ph = (rt * 2.0 + i * 0.29) % 1.0
            x = (i - 1.5) * s * 0.2
            y0 = s * 0.24 + ph * 140
            K.seg(c, x, y0, x - 6, y0 + 30, "#8C93A3", 6, 0.8 * (1 - ph * 0.5))


# ---------------------------------------------------------------- 11 三扇门

DOORS = ((330, "工作"), (600, "交友"), (870, "爱"))
DOOR_S = 250


def door_light(c, g, t, d):
    """门打开后洒出的光：门洞光晕 + 地面上的光斑。"""
    k = ease_out(clamp01(g.since(8) / 0.6))
    if k <= 0:
        return
    x = DOORS[1][0]
    K.spotlight(c, x, GROUND - 140, 330, K.GOLD, 0.45 * k)
    K.poly(c, [(x - 90, GROUND), (x + 90, GROUND), (x + 30 + 200 * k, GROUND + 110),
               (x - 30 - 200 * k, GROUND + 110)], K.GOLD, 0.28 * k)


def choose_ring(c, g, t, d):
    """第 4 拍：选中的那扇门被虚线框圈出。"""
    K.rr_stroke(c, 0, 0, DOOR_S * 0.72 + 50, DOOR_S * 1.1 + 50, 24, ACC, 6, 1.0, dash=(20, 12))


# ---------------------------------------------------------------- 12 三个最小的一步

def paper_plane(c, g, t, d):
    """消息发出：纸飞机从手机飞向右上方，身后一串虚线。"""
    k = ease_out(clamp01(g.since(2.5) / 0.9))
    if k <= 0:
        return
    x, y = lerp(0, 150, k), lerp(0, -170, k) + 40 * math.sin(k * math.pi)
    path = skia.Path()
    path.moveTo(0, 0)
    path.quadTo(75, -40 + 50, x, y)
    gfx.stroke_path(c, path, ACC, 4, 0.7, 1.0, dash=(10, 9, 0))
    with K.at(c, x, y, -30):
        with K.paper(c, 1, 0.6):
            K.poly(c, [(-34, -10), (34, 0), (-34, 18)], K.PAPER)
            K.poly(c, [(-34, 18), (34, 0), (-14, 4)], K.mix(K.PAPER, K.LINE, 0.6))


def meal(c, g, t, d):
    """一碗饭 + 一杯茶，冒着热气。"""
    with K.paper(c, 1, 0.8):
        path = skia.Path()
        path.addArc(skia.Rect.MakeXYWH(-120, -60, 170, 130), 0, 180)
        path.close()
        c.drawPath(path, K.paint(ACC))
        K.rr(c, -35, 6, 182, 12, 6, K.mix(ACC, K.INK, 0.25))
        path = skia.Path()
        path.addArc(skia.Rect.MakeXYWH(-108, -30, 146, 60), 180, 180)
        c.drawPath(path, K.paint(K.PAPER))
        K.seg(c, -60, -40, 20, -110, "#A0784F", 8)
        K.seg(c, -40, -40, 40, -104, "#A0784F", 8)
        K.rr(c, 110, 20, 70, 84, 12, K.OTHER3)
        K.ring(c, 152, 20, 20, K.OTHER3, 9)
    for i, x in enumerate((-50, 0, 110)):
        ph = (g.t * 0.8 + i * 0.33) % 1.0
        path = skia.Path()
        y0 = -40 - ph * 70 if i < 2 else -40 - ph * 60
        path.moveTo(x, y0)
        path.quadTo(x + 14, y0 - 20, x, y0 - 40)
        c.drawPath(path, K.paint(K.INK3, 0.7 * math.sin(ph * math.pi), 5))


def thanks_heart(c, g, t, d):
    K.icon(c, "heart", 0, 0, 190, HEART, 1, 0.8)
    K.text(c, "谢谢", 0, -6, 44, "serif_black", K.PAPER)


# ---------------------------------------------------------------- 13 人与人之间的线

P13 = ((260, 1, K.HERO, "short"), (820, -1, K.OTHER3, "long"))
S13 = 330


def thread13(c, g, t, d):
    """两人之间一根细线：中点先挂着一朵小灰云（烦恼），第 4 拍变成爱心（幸福）。"""
    pts = []
    for x, f, _, _ in P13:
        p = pose_at(g, "stand", [(2, "give")])
        j = joints(S13, p, f)
        pts.append((x + j["near"][0], GROUND + j["near"][1]))
    (x0, y0), (x1, y1) = pts
    mx, my = (x0 + x1) / 2, max(y0, y1) + 40
    path = skia.Path()
    path.moveTo(x0, y0)
    path.quadTo(mx, my + 40, x1, y1)
    gfx.stroke_path(c, path, K.mix(K.INK3, HEART, clamp01(g.since(4) / 0.4)), 5, 1.0,
                    ease_out(clamp01(g.since(0.5) / 0.6)))
    cy = 0.25 * (y0 + y1) + 0.5 * (my + 40)     # 曲线中点
    k = clamp01(g.since(4) / 0.25)
    if k < 1:
        K.icon(c, "cloud", mx, cy - 50, 120 * (1 - k), CLOUD, 1, 0.7)
    if k > 0:
        K.heart(c, mx, cy - 50, 110 * ease_out_back(clamp01(g.since(4) / 0.4), 2.5), HEART)
        K.ripple(c, mx, cy - 50, g.since(4), HEART, 200, 6, 0.8)
    for i, (dx, b) in enumerate(((-150, 6), (150, 6))):
        kk = clamp01(g.since(b) / 0.4)
        if kk > 0:
            fy = cy - 50 - 30 - 60 * ease_out(kk) - 18 * g.since(b) + 10 * math.sin(g.t * 3 + i)
            K.heart(c, mx + dx, fy, 66 * ease_out_back(kk, 2.5), K.mix(HEART, K.PAPER, 0.15))


# ---------------------------------------------------------------- 组装

def build() -> Episode:
    shots = [
        Shot(3, "工作不顺、朋友疏远、|感情又吵架……", "情境演绎", [
            Fig(540, GROUND, 360, at=0, mood="calm", hair="short",
                moves=[(2, dict(mood="worried", look=0.8)),
                       (4, dict(pose="sad", mood="sad", look=0.0)),
                       (6, dict(pose="cover", mood="sad"))]),
            Custom(storm_cloud, x=290, y=600, at=1.2, enter="none", land=2, name="brief", rain=8),
            Custom(storm_cloud, x=540, y=505, at=3.2, enter="none", land=4, name="friends", rain=8.3),
            Custom(storm_cloud, x=790, y=600, at=5.2, enter="none", land=6, name="rings", rain=8.6),
        ], draw=ground, hits=[(2, "wood_low", 1.0, "第一朵乌云落到头顶：工作（公文包）"),
                              (4, "bongo_low", 1.0, "第二朵乌云落下：朋友"),
                              (6, "tom", 1.0, "第三朵乌云落下：感情（对戒），主角抱头"),
                              (8, "shaker", 0.7, "三朵云一起下起雨")],
            note="三朵灰云按拍落到主角头顶，云里分别是公文包、两个人、对戒；随后下起雨"),
        Shot(3, "烦恼好像|一件和一件不一样。", "情境演绎",
             room_els((8, 8.5, 9), ats=(1, 3, 5), sfx=("wood_high", "bongo_high", "wood_low"),
                      notes=("格子一：工作", "格子二：交友", "格子三：爱")),
             hits=[(9, "rim", 0.8, "三个格子里的冲突同时上演")],
             note="三个分开的格子，各自是不同场景：上司指责、朋友走远、伴侣吵架"),
        Shot(2, "阿德勒却看到|一个共同点。", "阿德勒的视角",
             room_els((-99, -99, -99), lit=(2, 3, 4), enter="none", ats=(0, 0, 0),
                      sfx=(None, None, None)) + [
                 Icon("question", 540, 420, 100, color=ACC, at=6, enter="pop", note="共同点？"),
             ], over=common_thread, text_beat=0, cut=True, cam=(1.035, 1.05),
             hits=[(2, "wood_high", 0.9, "格子一里的上司被点亮"), (3, "bongo_high", 0.85, "格子二里的朋友被点亮"),
                   (4, "rim", 0.9, "格子三里的伴侣被点亮")],
             note="三个格子里的“他人”依次被点亮，一条虚线把他们串起来"),
        Shot(3, "工作、交友、爱，|是每个人都要面对的课题。", "阿德勒原著", [
            Big("人生三大课题", 540, 530, 118, at=0, sfx="kick", sub="工作 · 交友 · 爱", note="概念落版（音乐 drop）"),
            Icon("brief", 250, 900, 170, color=K.HERO, accent=K.GOLD, at=4, sfx="wood_high", note="工作"),
            Icon("friends", 540, 900, 170, color=K.OTHER3, at=6, sfx="bongo_high", note="交友"),
            Icon("heart", 830, 905, 160, color=HEART, at=8, sfx="rim", note="爱"),
            Label("工作", 250, 1050, 34, at=4.5, fill=K.INK2),
            Label("交友", 540, 1050, 34, at=6.5, fill=K.INK2),
            Label("爱", 830, 1050, 34, at=8.5, fill=K.INK2),
        ], note="drop 处“人生三大课题”砸下，三个课题图标依次弹出"),
        Shot(3, "这三个课题，|都离不开与他人的关系。", "阿德勒原著 · 大意", [
            Custom(orbit, at=0, enter="none"),
            Custom(links, at=0, enter="none", note="连线"),
            Fig(HUB[0], HUB[1], 270, at=0, enter="rise", hair="short", mood="calm",
                moves=[(8, dict(mood="smile", pose="relax"))]),
            *[Custom(node_disc, x=x, y=y, i=i, at=2 + 2 * i, enter="pop", sfx=sx, note=nt)
              for i, ((x, y, *_), sx, nt) in enumerate(zip(NODES, ("wood_high", "bongo_high", "wood_low"),
                                                          ("连向工作里的同事", "连向朋友", "连向伴侣")))],
            *[Label(NODES[i][5], *NODES[i][6], 32, at=2.5 + 2 * i, fill=ACC) for i in range(3)],
        ], hits=[(8, "rim", 0.9, "三条连线同时亮起")],
            note="三个课题围成一圈，主角在中间，三条线分别连向课题里的他人"),
        Shot(3, "有人把它概括为：|烦恼都来自人际关系。", "岸见一郎阐释", [
            Icon("book", 650, 1000, 240, color=ACC, at=0, enter="pop", sfx="wood_low", note="《被讨厌的勇气》翻开"),
            Txt("《被讨厌的勇气》", 650, 1110, 30, at=1, font="sans_medium", color=K.INK2),
            Custom(flip_card, x=650, y=670, at=2, enter="none", sfx="wood_high", note="卡片从书里翻出"),
            Fig(210, GROUND, 330, at=0, pose="think", mood="calm", hair="short",
                moves=[(5, dict(pose="point", mood="open", sfx="bongo_low", note="主角指向卡片"))]),
            Txt("岸见一郎的概括，不是阿德勒原句", 540, 1235, 30, at=6, font="sans_medium", color=K.INK2),
        ], draw=ground, note="书里翻出卡片“烦恼都来自人际关系”；底部小字说明这是岸见一郎的概括"),
        Shot(3, "想彻底摆脱这类烦恼？|除非世上只剩你一人。", "机制示意", [
            Custom(planet, x=PLANET[0], y=PLANET[1], at=0, enter="grow"),
            on_planet(-40, 170, color=K.OTHER, mood="smile", hair="bun", face=-1, leave=4, sfx="shaker",
                      note="第一个人离开星球"),
            on_planet(33, 170, color=K.OTHER2, mood="smile", leave=5, sfx="wood_high", note="第二个人离开"),
            on_planet(60, 155, color=K.OTHER3, mood="calm", hair="long", leave=6, sfx="bongo_high", gain=0.8,
                      note="第三个人离开"),
            Fig(540, PLANET[1] - PLANET[2] + 70, 250, at=0, enter="none", pose="sit", mood="smile", hair="short",
                lift=0.6, moves=[(7, dict(mood="worried", look=0.6)),
                                 (9, dict(pose="sit_sad", mood="sad", look=0.0, sfx="frame", gain=0.8,
                                          note="只剩主角一个人，抱膝发呆"))]),
        ], draw=stars, note="小星球上的其他人一个个离开，只剩主角坐着，四周星星"),
        Shot(4, "逃避课题的借口，|阿德勒叫它“人生的谎言”", "阿德勒原著", [
            Fig(HIDE_X[0], GROUND, HIDE_S, at=0, enter="none", face=-1, pose="stand", mood="worried", hair="short",
                walk=False, moves=[(1, dict(x=HIDE_X[1], dur=0.6)),
                                   (4, dict(pose="reach")),
                                   (12, dict(mood="sad"))]),
            Custom(curtain, at=0, enter="fade"),
            Icon("brief", 140, 1062, 105, color=K.HERO, accent=K.GOLD, at=2, enter="drop", sfx="wood_low",
                 note="三个课题落在门外等着",
                 moves=[(12, dict(y=1032, dur=0.15)), (12.4, dict(y=1062, dur=0.2))]),
            Icon("friends", 265, 1062, 105, color=K.OTHER3, at=2.5, enter="drop",
                 moves=[(12, dict(y=1032, dur=0.15)), (12.4, dict(y=1062, dur=0.2))]),
            Icon("heart", 385, 1066, 95, color=HEART, at=3, enter="drop",
                 moves=[(12, dict(y=1036, dur=0.15)), (12.4, dict(y=1066, dur=0.2))]),
            Custom(excuse_sign, at=4, enter="none", sfx="wood_high", note="主角从帘子后伸手举出牌子“等我准备好再说”"),
            Custom(lie_stamp, x=330, y=752, at=8, enter="slam", dur=0.22, rot=-8, sfx="rim",
                   note="“人生的谎言”印章砸在牌子上"),
        ], draw=ground, hits=[(12, "bongo_low", 0.8, "三个课题在门外跳着敲门")],
            note="主角躲在帘子后，举着“等我准备好再说”的牌子；第 8 拍“人生的谎言”印章落下"),
        Shot(3, "“等我变优秀了再交朋友”|“等对的人出现再说”", "情境演绎", [
            Custom(bench, x=345, y=GROUND, at=0, enter="none"),
            Fig(380, GROUND, 300, at=0, enter="none", pose="sit", mood="calm", hair="short",
                moves=[(2, dict(pose=dict(K.POSES["sit"], la1=40, la2=120, head=-8), mood="calm")),
                       (8, dict(pose="sit_sad", mood="sad"))]),
            Custom(calendar, x=770, y=630, at=0, enter="pop", note="日历"),
            Icon("clock", 775, 985, 180, color=K.INK2, at=0, enter="pop", p=lambda g, t: 0.15 + t * 1.1),
        ], draw=ground, hits=[(2, "wood_high", 0.9, "日历翻页"), (6, "bongo_high", 0.8, "日历再翻页"),
                              (10, "shaker", 0.8, "椅背结出蛛网")],
            note="主角坐在长椅上等，日历按拍翻页、时钟飞转，椅背结了蛛网"),
        Shot(3, "课题不会因为等待|而变得简单。", "机制示意", [
            Icon("clock", 540, 420, 100, color=K.INK2, at=0, enter="pop", p=lambda g, t: t * 1.4),
            Custom(growing_cloud, x=230, y=650, at=0, enter="none"),
            Custom(growing_cloud, x=540, y=630, at=0, enter="none", bolt=True),
            Custom(growing_cloud, x=850, y=650, at=0, enter="none"),
            Icon("brief", 230, 1020, 185, color=K.HERO, accent=K.GOLD, at=0,
                 moves=[(2, dict(s=170)), (5, dict(s=155)), (8, dict(s=140))]),
            Icon("friends", 540, 1020, 185, color=K.OTHER3, at=0,
                 moves=[(2, dict(s=170)), (5, dict(s=155)), (8, dict(s=140))]),
            Icon("heart", 850, 1025, 170, color=HEART, at=0,
                 moves=[(2, dict(s=156)), (5, dict(s=142)), (8, dict(s=128))]),
        ], draw=ground, hits=[(2, "bongo_low", 0.8, "乌云变大"), (5, "tom", 0.8, "乌云更大"),
                              (8, "frame", 0.9, "乌云再变大，开始下雨"), (10, "rim", 0.8, "中间的云打下闪电")],
            note="三个课题图标上的乌云按拍变大、变暗，图标被压小，最后下雨打闪"),
        Shot(4, "选一个你在回避的课题，|迈出最小的一步。", "小练习", [
            Custom(door_light, at=0, enter="none"),
            *[Icon("door", x, GROUND - DOOR_S * 0.55, DOOR_S, color=K.DARK, accent=K.GOLD, at=0.5 * i, lift=0.6,
                   p=(lambda g, t: ease_out(clamp01(g.since(8) / 0.6))) if i == 1 else 0.0,
                   sfx="wood_low" if i == 0 else None, note="三扇门：工作 / 交友 / 爱" if i == 0 else "")
              for i, (x, _) in enumerate(DOORS)],
            *[Label(name, x, GROUND - DOOR_S * 1.1 - 62, 32, at=1 + 0.5 * i, fill=K.INK2,
                    moves=[(4, dict(fill=ACC))] if i == 1 else [])
              for i, (x, name) in enumerate(DOORS)],
            Custom(choose_ring, x=DOORS[1][0], y=GROUND - DOOR_S * 0.55, at=4, enter="pop", sfx="wood_high",
                   note="选中“交友”这扇门", out=8),
            Fig(150, GROUND, 320, at=0, mood="worried", hair="short",
                moves=[(2, dict(pose="think")),
                       (4, dict(pose="point", mood="open")),
                       (6, dict(x=430, pose="stand", dur=1.0)),
                       (8, dict(pose="push", mood="calm", sfx="tom", note="推开门，光照进来")),
                       (10, dict(x=480, pose="stand", dur=0.6, mood="smile")),
                       (12, dict(pose="wave", mood="happy", sfx="bongo_high", note="站在光里回头挥手"))]),
        ], draw=ground, note="三扇门（工作 / 交友 / 爱），主角选中一扇推开，光照进来"),
        Shot(4, "发一条消息、约一顿饭、|说一句谢谢。", "小练习", [
            Icon("phone", 220, 700, 200, color=K.DARK, accent=ACC, at=2, sfx="bongo_high", note="消息发出"),
            Custom(paper_plane, x=230, y=640, at=2, enter="none"),
            Custom(meal, x=560, y=560, at=4, enter="pop", sfx="wood_low", note="约一顿饭"),
            Custom(thanks_heart, x=860, y=700, at=8, enter="pop", sfx="clap", note="说一句谢谢"),
            Label("发消息", 220, 860, 30, at=2.5, fill=K.INK2),
            Label("约饭", 540, 690, 30, at=4.5, fill=K.INK2),
            Label("说谢谢", 860, 860, 30, at=8.5, fill=K.INK2),
            Fig(540, GROUND, 300, at=0, mood="calm", hair="short",
                moves=[(2, dict(pose="point", mood="open")), (4, dict(pose="give", mood="smile")),
                       (8, dict(pose="cheer", mood="happy")), (12, dict(pose="wave"))]),
        ], draw=ground, hits=[(12, "cymbal", 0.6, "主角挥手，三件小事都完成")],
            note="手机消息发出（第 2 拍）、饭和茶（第 4 拍）、写着谢谢的爱心（第 8 拍）"),
        Shot(2, "烦恼来自人与人之间，|幸福也是。", "阿德勒的视角", [
            Custom(thread13, at=0, enter="none", note="两人之间的线"),
            *[Fig(x, GROUND, S13, at=0, enter="none", face=f, color=colr, hair=hair, mood="flat",
                  moves=[(2, dict(pose="give", mood="calm")), (4, dict(mood="smile")), (6, dict(mood="happy"))])
              for x, f, colr, hair in P13],
        ], draw=ground, text_beat=0,
            hits=[(2, "wood_low", 0.8, "两人伸手，线拉直"), (4, "bongo_high", 0.9, "线上的乌云变成爱心"),
                  (6, "clap", 0.8, "又飘起两颗爱心")],
            note="两人之间的细线上，乌云变成爱心——烦恼和幸福都在人与人之间"),
        end_shot(["Adler, A. (1931). What Life Should Mean to You, ch.1.（中译《自卑与超越》）",
                  "Adler, A. (1914). Lebenslüge und Verantwortlichkeit in der Neurose und Psychose.",
                  "岸见一郎、古贺史健（2013）《被讨厌的勇气》"],
                 "06 课题分离：别人怎么看你，是谁的课题？"),
    ]
    return Episode(5, "life_tasks", "人生课题", "为什么烦恼，总和人有关？", ACC, shots,
                   refs=["Adler, A. (1931). What Life Should Mean to You, ch.1.（中译《自卑与超越》）",
                         "Adler, A. (1914). Lebenslüge und Verantwortlichkeit in der Neurose und Psychose.",
                         "岸见一郎、古贺史健（2013）《被讨厌的勇气》"],
                   publish_title="为什么烦恼，总和人有关？｜阿德勒心理学05 人生三大课题",
                   hashtags="#阿德勒 #心理学 #人际关系 #拖延 #被讨厌的勇气",
                   cover_title="为什么烦恼，|总和【人】有关？", cover_sub="阿德勒的人生三大课题",
                   cover_shot=4, cover_t=5.5,
                   notes=[
                       "三大课题据 What Life Should Mean to You 第 1 章（three main ties：职业、社会/友谊、爱与婚姻）；"
                       "“自我”“灵性”两个课题是后来 Dreikurs 与 Mosak 增补的，不属阿德勒原文。",
                       "“人的烦恼皆源于人际关系”是《被讨厌的勇气》第二夜对阿德勒思想的概括，不是阿德勒原句，片中第 6 镜标注。",
                       "“人生的谎言”（Lebenslüge）是阿德勒用过的术语，见 1914 年论文 Lebenslüge und Verantwortlichkeit in der "
                       "Neurose und Psychose。",
                   ]).build()
