"""03 自卑情结：“要不是因为……，我早就……”"""

import math

import skia

from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, ease_out_back, lerp

from . import kit as K
from .core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

ACC = "#8C4F7A"
GROUND = 1130
GRAY = "#A4A2AF"
GRAY_HERO = K.mix(K.HERO, K.INK3, 0.45)
SOFA = "#B98AA8"
BOXC = "#C49A6C"


def ground(g):
    K.ground(g.c, GROUND)


# ---------------------------------------------------------------- 通用小件

def pose_geo(s, p, face=1.0, bob=0.0):
    """按 kit.figure 的骨架算出脚底原点坐标系下的近侧手、头、肩、髋位置（用于挂道具）。"""
    d = K.pose(p)
    u = s
    thigh, shin, upper, fore = 0.235 * u, 0.225 * u, 0.19 * u, 0.18 * u

    def leg_extent(a1, a2):
        (_, ey), (_, fy) = K._limb(0, 0, a1, a2, thigh, shin, 1)
        return max(ey, fy)

    hip_y = -d["seat"] * u if d["seat"] > 0 else -max(leg_extent(d["ll1"], d["ll2"]), leg_extent(d["rl1"], d["rl2"]))
    hip_y -= bob * u
    lean = math.radians(d["lean"])
    sh_x = face * 0.30 * u * math.sin(lean)
    sh_y = hip_y - 0.30 * u * math.cos(lean)
    _, hand = K._limb(sh_x + 0.06 * u * face, sh_y + 0.03 * u, d["la1"], d["la2"], upper, fore, face)
    hd = math.radians(d["head"])
    head = (sh_x + face * 0.15 * u * math.sin(lean + hd * 0.5), sh_y - 0.15 * u * math.cos(lean + hd * 0.5))
    return dict(hand=hand, head=head, sh=(sh_x, sh_y), hip=(0.0, hip_y), r=0.16 * u)


def fig_plus(c, g, el_t, d):
    """人物 + 附件：under(c, g, geo, d) 画在人物之下，attach(c, g, geo, d) 画在人物之上。"""
    s, p, face = d["s"], d.get("pose", "stand"), d.get("face", 1)
    bob = 0.006 * math.sin(g.t * 2.6 + d["x"] * 0.02)
    geo = pose_geo(s, p, face, bob)
    if d.get("under"):
        d["under"](c, g, geo, d)
    K.figure(c, 0, 0, s, p, d.get("color", K.HERO), K.SKIN, 1, face, d.get("mood", "calm"), d.get("hair"),
             d.get("hair_color"), bob, d.get("lift", 1.0), d.get("look", 0.0), d.get("blink", False))
    if d.get("attach"):
        for fn in (d["attach"] if isinstance(d["attach"], (list, tuple)) else [d["attach"]]):
            fn(c, g, geo, d)


def FigPlus(x, y, s, **kw):
    kw.setdefault("enter", "rise")
    return Custom(fig_plus, x=x, y=y, s=s, **kw)


def gcloud(c, x, y, s, alpha=1.0, color=GRAY):
    K.icon(c, "cloud", x, y, s, color, alpha, 0.6)


def dream(c, g, el_t, d):
    """梦泡：一团思考云，里面是一个图标；尾巴的小圆点指向 (tx, ty)（相对元素原点）。"""
    w, h = d.get("w", 300), d.get("h", 230)
    tx, ty = d["tail"]
    shrink = d.get("shrink", 0.0)
    with K.paper(c, 1, 0.8):
        for i, (fx, fy, r) in enumerate(((-0.3, 0.05, 0.36), (0.0, -0.2, 0.42), (0.3, 0.02, 0.36), (0.02, 0.22, 0.36))):
            K.dot(c, fx * w, fy * h, r * min(w, h) * 1.05, K.PAPER)
        K.rr(c, 0, 0, w * 0.86, h * 0.7, h * 0.3, K.PAPER)
        for k, rad in enumerate((20, 13, 8)):
            q = (k + 1) / 4
            K.dot(c, lerp(-w * 0.2, tx, q), lerp(h * 0.42, ty, q), rad, K.PAPER)
    pulse = 1 + 0.06 * math.sin(g.t * 6) * d.get("beat", 0.0)
    sc = (1 - 0.35 * shrink) * pulse
    col = K.mix(d.get("color", K.GOLD), K.INK3, shrink)
    with K.at(c, 0, 0, 0, sc):
        K.icon(c, d["icon"], 0, 0, d.get("is", 140), col, 1 - 0.4 * shrink, 0.5, 0, 1, 1.0, d.get("accent", K.RED))
    if d.get("sparkle") is not None:
        dt = g.since(d["sparkle"])
        if 0 <= dt < 0.8:
            for i in range(4):
                a = i * math.pi / 2 + 0.4
                r = 80 + 40 * ease_out(dt / 0.8)
                K.star(c, math.cos(a) * r, math.sin(a) * r * 0.8, 16 * (1 - dt / 0.8), K.GOLD, 1 - dt / 0.8, 4)


# ---------------------------------------------------------------- 镜 1–3：沙发、学历靠枕、借口毯子

SLOUCH = dict(lean=-16, head=6, la1=74, la2=62, ra1=60, ra2=70, ll1=80, ll2=-66, rl1=74, rl2=-60, seat=0.27)
SNUG = dict(lean=-20, head=-4, la1=60, la2=70, ra1=50, ra2=74, ll1=82, ll2=-70, rl1=76, rl2=-64, seat=0.27)
SOFA_X = 380


def sofa(c, g, el_t, d):
    """侧面的沙发：靠背在人物身后（左侧）。"""
    with K.paper(c, 1, 0.8):
        K.rr(c, -10, -60, 300, 86, 20, SOFA)
        K.rr(c, -150, -170, 70, 290, 28, K.shade(SOFA, 0.12))
        K.rr(c, 136, -80, 52, 120, 18, K.shade(SOFA, 0.06))
        for dx in (-120, 110):
            K.rr(c, dx, -8, 18, 22, 4, K.shade(SOFA, 0.4))
    K.rr(c, -10, -96, 240, 14, 7, K.tint(SOFA, 0.25))


def excuse_card(c, g, geo, d):
    """怀里的“学历”卡；wrap>0 时展开成一条毯子把人裹住。"""
    m = ease_in_out(clamp01(d.get("wrap", 0.0)))
    hx, hy = geo["hip"]
    sx, sy = geo["sh"]
    cx0, cy0 = (sx + hx) / 2 + 52, (sy + hy) / 2 + 6
    cx1, cy1 = hx + 12, sy + 92
    cx, cy = lerp(cx0, cx1, m), lerp(cy0, cy1, m)
    w, h = lerp(120, 215, m), lerp(84, 190, m)
    rot = lerp(-10, -4, m)
    a = d.get("card_a", 1.0)
    if a <= 0:
        return
    with K.at(c, cx, cy, rot):
        with K.paper(c, a, 0.8):
            if m < 0.5:
                K.rr(c, 0, 0, w, h, 12, K.PAPER)
                K.rr(c, 0, -h / 2 + 8, w, 16, 8, ACC)
                K.text(c, "学历", 0, 4, 36, "serif", K.INK)
            else:
                k = (m - 0.5) * 2
                quilt = K.tint(ACC, 0.5)
                K.rr(c, 0, 0, w, h, 34, quilt)
                c.save()
                c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 34, 34), doAntiAlias=True)
                for i in range(-3, 4):
                    K.seg(c, i * 46, -h / 2, i * 46 + 30, h / 2, K.tint(ACC, 0.32), 5, k)
                    K.seg(c, -w / 2, i * 46 + 10, w / 2, i * 46 + 18, K.tint(ACC, 0.32), 5, k)
                K.rr(c, 0, -h / 2 + 18, w, 40, 0, K.tint(ACC, 0.68))
                c.restore()
                with K.at(c, 30, 40, 6, 0.6 + 0.4 * k):
                    K.rr(c, 0, 0, 100, 54, 8, K.PAPER)
                    K.text(c, "学历", 0, 2, 32, "serif", ACC)


def hearts_float(c, g, el_t, d):
    for i in range(3):
        dt = g.since(d["b0"]) - i * 0.35
        if dt < 0:
            continue
        ph = (dt / 1.8) % 1.0
        K.heart(c, i * 40 - 40 + 14 * math.sin(ph * 6 + i), -ph * 200, 30 * (1 - ph * 0.5), K.tint(ACC, 0.3), 1 - ph)


# ---------------------------------------------------------------- 镜 4：灰云变成“我做不到”的牌子

def cloud_to_sign(c, g, el_t, d):
    m = ease_in_out(clamp01(d.get("m", 0.0)))
    if m < 1:
        with K.at(c, 0, 0, 0, 1 - 0.6 * m):
            gcloud(c, lerp(0, 120, m), lerp(0, 80, m), 170, 1 - m)
    if m > 0:
        sc = 0.5 + 0.5 * ease_out_back(m, 1.6)
        K.text_card(c, 190, 175, ["我做不到"], 48, None, K.PAPER, K.INK, ACC, m, -4, sc, accent=GRAY)


# ---------------------------------------------------------------- 镜 6：公式卡，A 变成挡箭牌

def formula_a(c, g, el_t, d):
    m = ease_in_out(clamp01(d.get("m", 0.0)))
    x, y = lerp(0, d["tx"], m), lerp(0, d["ty"], m)
    rot = lerp(-3, 0, m) + 360 * m
    if m < 0.5:
        K.card(c, x, y, 220, 210, K.PAPER, 1, 22, 1.0, rot, 1 - 0.3 * m, ACC,
               lambda c, w, h: (K.text(c, "A", 0, -30, 80, "serif_black", ACC), K.text(c, "学历", 0, 52, 44, "serif")))
    else:
        k = (m - 0.5) * 2
        sc = lerp(0.6, 1.0, k)
        K.icon(c, "shield", x, y, 300, K.mix(ACC, K.HERO, 0.25), 1, 1.0, rot - 360, sc)
        K.text(c, "A", x + 8, y - 8, 96 * sc, "serif_black", K.PAPER)
    if m >= 1:
        K.burst(c, x, y, g.since(d["at_m"]) - 0.45, ACC, 120, 260, 10, 8)


# ---------------------------------------------------------------- 镜 7、13：玻璃罩里的奖杯

def dome(c, g, el_t, d):
    lift = ease_in_out(clamp01(d.get("lift", 0.0)))
    take = ease_in_out(clamp01(d.get("take", 0.0)))
    with K.paper(c, 1, 0.8):
        K.rr(c, 0, -100, 240, 200, 10, "#7C6A80")
        K.rr(c, 0, -196, 270, 22, 8, K.shade("#7C6A80", 0.15))
    # 奖杯（被拿走时飞向 tx, ty）
    tx, ty = d.get("trophy_to", (0, -290))
    px, py = lerp(0, tx, take), lerp(-290, ty, take) - 120 * math.sin(math.pi * take)
    K.icon(c, "trophy", px, py, d.get("ts", 170) * lerp(1, 0.75, take), K.GOLD, 1, 0.6, 0, 1, 1.0, K.RED)
    gl = d.get("glint")
    if gl is not None:
        dt = g.since(gl)
        if 0 <= dt <= 0.7:
            K.star(c, px + 50, py - 60, 22 * math.sin(dt / 0.7 * math.pi), K.PAPER, 1, 4, 0.3)
    # 玻璃罩
    a = 1 - lift
    dx, dy, rot = -60 * lift, -200 * lift, -18 * lift
    with K.at(c, dx, dy - 207, rot):
        path = skia.Path()
        path.moveTo(-118, 0)
        path.lineTo(-118, -180)
        path.cubicTo(-118, -310, 118, -310, 118, -180)
        path.lineTo(118, 0)
        path.close()
        c.drawPath(path, K.paint(K.tint("#BFD6DF", 0.2), 0.35 * a))
        c.drawPath(path, K.paint("#9FB7C2", 0.9 * a, 6))
        K.seg(c, -80, -40, -80, -190, K.PAPER, 10, 0.7 * a)
        K.rr(c, 0, -282, 34, 22, 10, "#9FB7C2", a)
    lock = clamp01(d.get("lock", 0.0))
    if lock > 0:
        sc = 0.5 + 0.5 * ease_out_back(lock, 2.2)
        with K.at(c, 0, -206, 0, sc):
            with K.paper(c, lock, 0.6):
                K.ring(c, 0, -26, 22, K.DARK, 9)
                K.rr(c, 0, 0, 66, 54, 10, K.GOLD)
                K.dot(c, 0, -2, 7, K.DARK)
                K.rr(c, 0, 10, 6, 16, 3, K.DARK)


# ---------------------------------------------------------------- 镜 8–11：王冠与箱子堆

def crown_on(c, g, geo, d):
    """王冠戴在头上；crown_drop 给出落下的拍（drop 落定）。"""
    hx, hy = geo["head"]
    r = geo["r"]
    cy = hy - r * 0.95 - 20
    b = d.get("crown_drop")
    if b is not None:
        T = g.b(b)
        k = clamp01((g.t - (T - 0.42)) / 0.42)
        if g.t < T - 0.42:
            return
        cy -= 420 * (1 - ease_in(k))
        if g.t > T:
            cy -= 12 * math.sin(min(1, (g.t - T) / 0.25) * math.pi)
            K.burst(c, hx, cy, g.t - T, K.GOLD, 70, 200, 10, 7)
    K.icon(c, "crown", hx, cy, r * 2.1, K.GOLD, 1, 0.8, 0, 1, 1, K.RED)


def boxes(c, g, el_t, d):
    """一列列纸箱：cols=[(x, 层数)]，箱子宽 w、高 h。"""
    w, h = d.get("w", 220), d.get("h", 125)
    for x, n in d["cols"]:
        for k in range(n):
            y = -k * h
            with K.paper(c, 1, 0.7):
                K.rr(c, x, y - h / 2, w - 6, h - 6, 8, K.mix(BOXC, K.PAPER, 0.06 * k))
                K.rr(c, x, y - h + 14, w - 6, 18, 6, K.tint(BOXC, 0.2))
            K.seg(c, x, y - h + 26, x, y - 10, K.shade(BOXC, 0.12), 5, 0.6)


def xray(c, g, el_t, d):
    """箱子堆里透出的小影子：一个圆窗打开，里面是缩成一团的人。"""
    k = ease_out(clamp01(d.get("open", 0.0)))
    if k <= 0:
        return
    r = 100 * k
    c.save()
    path = skia.Path()
    path.addCircle(0, 0, r)
    c.clipPath(path, doAntiAlias=True)
    K.dot(c, 0, 0, r, K.shade(BOXC, 0.55))
    K.figure(c, 0, 62, 130, "hide", K.mix(K.INK3, K.INK2, 0.3), K.mix(K.SKIN, K.INK3, 0.4), 1, 1, "sad", None,
             None, 0, 0.2)
    c.restore()
    p = K.paint(K.PAPER, 0.9, 6)
    p.setPathEffect(skia.DashPathEffect.Make([18, 12], g.t * 30))
    c.drawCircle(0, 0, r + 4, p)


def megaphone_at(c, g, geo, d):
    m = clamp01(d.get("mega", 0.0))
    if m <= 0:
        return
    hx, hy = geo["hand"]
    with K.at(c, hx + 40, hy, 0, m):
        K.icon(c, "megaphone", 0, 0, 120, ACC, 1, 0.6)
        for i in range(3):
            ph = (g.t * 2 + i / 3) % 1
            path = skia.Path()
            r = 50 + 70 * ph
            path.addArc(skia.Rect.MakeXYWH(30 - r, -r, 2 * r, 2 * r), -35, 70)
            c.drawPath(path, K.paint(ACC, (1 - ph) * m, 6))


def cloud_trophy_at(c, g, geo, d):
    """把灰云当奖杯举起：灰云下面接一个奖杯底座。"""
    m = clamp01(d.get("ctrophy", 0.0))
    if m <= 0:
        return
    hx, hy = geo["hand"]
    sc = 0.4 + 0.6 * ease_out_back(m, 1.8)
    with K.at(c, hx, hy - 70, 0, sc):
        with K.paper(c, 1, 0.8):
            K.rr(c, 0, 40, 24, 50, 4, K.GOLD)
            K.rr(c, 0, 70, 90, 20, 6, K.shade(K.GOLD, 0.2))
            path = skia.Path()
            path.moveTo(-70, -10)
            path.lineTo(70, -10)
            path.quadTo(66, 30, 0, 36)
            path.quadTo(-66, 30, -70, -10)
            c.drawPath(path, K.paint(K.GOLD))
        gcloud(c, 0, -40, 150)
        for i in range(3):
            dt = (g.t * 1.3 + i / 3) % 1
            K.star(c, -80 + i * 80, -110 - 30 * dt, 14 * math.sin(dt * math.pi), K.GOLD, 1, 4)


# ---------------------------------------------------------------- 镜 12：改写卡

def rewrite_card(c, g, el_t, d):
    a_old = 1 - 0.55 * clamp01(g.since(4) / 0.3)
    K.text_card(c, 0, -170, ["要不是学历不好，", "我早就成功了。"], 44, 640, K.PAPER, K.INK2, ACC, a_old, -2)
    strike = ease_out(clamp01(g.since(4) / 0.3))
    if strike > 0:
        K.seg(c, -260, -160, -260 + 520 * strike, -200, ACC, 9)
    k = clamp01(g.since(8) / 0.4)
    if k > 0:
        K.text_card(c, 0, 130, ["【即使如此】，", "【也试试】投一份简历。"], 48, 680, K.PAPER, K.INK, ACC, k, 1.5,
                    0.6 + 0.4 * ease_out_back(k, 1.6), accent=ACC)


# ---------------------------------------------------------------- 镜 13：清单卡

def checklist(c, g, el_t, d):
    tick = clamp01(g.since(d["tick"]) / 0.35)

    def draw(c, w, h):
        K.text(c, "今天的小事", 0, -48, 36, "serif", ACC)
        K.rr_stroke(c, -136, 34, 40, 40, 8, K.INK2, 4)
        K.text(c, "投一份简历", -100, 34, 40, "serif", K.INK, 1, "left")
        if tick > 0:
            gfx_check(c, -136, 30, 54, tick)
            K.seg(c, -96, 36, -96 + 210 * ease_out(tick), 36, K.tint(ACC, 0.3), 6, 0.0)

    K.card(c, 0, 0, 400, 210, K.PAPER, 1, 22, 1.0, 2, 1, ACC, draw)
    if tick > 0:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(70 - d["x"], 330 - d["y"], 1010 - d["x"], 1262 - d["y"]))
        K.confetti(c, 0, 40, g.since(d["tick"]), [ACC, K.GOLD, K.HERO, K.GREEN], 28, 5)
        c.restore()


def gfx_check(c, x, y, size, p):
    path = skia.Path()
    path.moveTo(x - size * 0.4, y)
    path.lineTo(x - size * 0.08, y + size * 0.3)
    path.lineTo(x + size * 0.45, y - size * 0.38)
    from engine import gfx
    gfx.stroke_path(c, path, K.GREEN, 10, 1.0, ease_out(p))


# ---------------------------------------------------------------- 镜 14：路展开

def road(c, g, el_t, d):
    p = ease_out(clamp01(d.get("p", 0.0)))
    if p <= 0:
        return
    near_y, far = 1175 - d["y"], (820 - d["x"], 650 - d["y"])
    nl, nr = 470 - d["x"], 820 - d["x"]
    fx, fy = far
    ex_l = (lerp(nl, fx - 14, p), lerp(near_y, fy, p))
    ex_r = (lerp(nr, fx + 14, p), lerp(near_y, fy, p))
    with K.paper(c, 1, 0.4):
        K.poly(c, [(nl, near_y), (nr, near_y), ex_r, ex_l], K.tint(ACC, 0.6))
    mid0 = ((nl + nr) / 2, near_y)
    mid1 = ((ex_l[0] + ex_r[0]) / 2, ex_l[1])
    pp = K.paint(K.PAPER, 0.9, 8)
    pp.setPathEffect(skia.DashPathEffect.Make([34, 26], 0))
    c.drawLine(*mid0, *mid1, pp)


# ---------------------------------------------------------------- 分镜

CROWN_FIG = pose_geo(270, "stand", 1)
WAVE_HAND = pose_geo(330, "wave", -1)["hand"]


def build() -> Episode:
    shots = [
        # 1：瘫在沙发上，抱着“学历”卡，梦泡里是奖杯
        Shot(3, "“要不是学历不好，|我早就成功了。”", "情境演绎", [
            Custom(sofa, x=SOFA_X, y=GROUND, at=0, enter="fade"),
            FigPlus(SOFA_X, GROUND, 330, at=0, enter="fade", pose=SLOUCH, hair="short", mood="flat",
                    attach=excuse_card, card_a=0.0,
                    moves=[(2, dict(card_a=1.0, dur=0.25, sfx="wood_low", note="“学历”卡抱进怀里当靠枕")),
                           (4, dict(look=0.8, mood="smile")),
                           (8, dict(pose=dict(SLOUCH, lean=-20, head=16), mood="sad", look=-0.3, sfx="shaker",
                                    gain=0.8, note="叹一口气，缩回沙发"))]),
            Custom(dream, x=760, y=600, at=4, enter="pop", icon="trophy", tail=(-280, 230), sparkle=8,
                   sfx="bongo_high", gain=0.85, note="梦泡里出现奖杯"),
        ], draw=ground, note="主角瘫在沙发上，把“学历”卡抱在怀里当靠枕；梦泡里是一座奖杯，他叹了口气"),

        # 2：另一个人摊手，梦泡里是爱心
        Shot(3, "“要不是长得普通，|我早就脱单了。”", "情境演绎", [
            Fig(380, GROUND, 370, at=0, color=K.OTHER3, hair="bun", pose="think", mood="flat",
                moves=[(2, dict(pose="shrug", mood="worried", sfx="wood_low", gain=0.85, note="她摊开手")),
                       (8, dict(pose="sad", mood="sad", sfx="rim", gain=0.7, note="叹气，梦泡里的爱心变灰"))]),
            Custom(dream, x=770, y=580, at=4, enter="pop", icon="heart", color=K.RED, tail=(-300, 220), beat=1.0,
                   shrink=0.0, sfx="bongo_high", gain=0.85, note="梦泡里出现爱心",
                   moves=[(8, dict(shrink=1.0, beat=0.0, dur=0.5))]),
        ], draw=ground, note="另一个人摊手说“要不是长得普通”，梦泡里是一颗爱心，叹气时爱心变灰变小"),

        # 3：借口卡变成毯子
        Shot(2, "听起来是遗憾，|其实也是安慰。", "机制示意", [
            Custom(sofa, x=SOFA_X, y=GROUND, at=0, enter="none"),
            FigPlus(SOFA_X, GROUND, 330, at=0, enter="none", pose=SLOUCH, hair="short", mood="flat",
                    attach=excuse_card, wrap=0.0,
                    moves=[(2, dict(wrap=1.0, pose=SNUG, dur=0.5, sfx="shaker", note="“学历”卡展开成一条毯子把他裹住")),
                           (4, dict(mood="happy", blink=True, look=0.3, sfx="wood_high", gain=0.8,
                                    note="他裹着毯子舒服地笑了"))]),
            Custom(dream, x=760, y=600, at=0, enter="none", icon="trophy", tail=(-280, 230), alpha=0.55),
            Custom(hearts_float, x=SOFA_X + 40, y=840, at=5, enter="none", b0=5),
        ], draw=ground, note="怀里的“学历”卡展开成毯子把主角裹住，他舒服地眯眼笑——借口也是一种安慰"),

        # 4：drop——“自卑情结”
        Shot(3, "把自卑当成|“我做不到”的理由。", "阿德勒原著", [
            Big("自卑情结", 540, 500, 150, at=0, sfx="kick", sub="inferiority complex", note="概念落版（音乐 drop）"),
            Fig(330, GROUND, 330, at=1, hair="short", mood="worried",
                moves=[(4, dict(pose="give", mood="flat")),
                       (8, dict(pose="relax", mood="smile", sfx="tom", gain=0.8, note="举着牌子，松了口气"))]),
            Custom(cloud_to_sign, x=350, y=720, at=2, enter="pop", m=0.0, sfx="wood_low", gain=0.8,
                   note="头顶飘来小灰云（自卑）",
                   moves=[(4, dict(m=1.0, dur=0.35, sfx="rim", note="灰云变成“我做不到”的牌子"))]),
        ], draw=ground, note="drop 处“自卑情结”砸下；主角头顶的小灰云变成一块“我做不到”的牌子，他举着牌子松了口气"),

        # 5：自卑感 vs 自卑情结
        Shot(3, "自卑感：想变得更好；|自卑情结：干脆不去做。", "阿德勒原著 · 大意", [
            Custom(lambda c, g, t, d: K.seg(c, 0, 0, 0, 760 * ease_out(clamp01(t / 0.6)), K.LINE, 6),
                   x=540, y=380, at=0, enter="none"),
            Label("自卑感", 290, 440, 38, at=1, fill=ACC, sfx="wood_high", gain=0.8, note="左：自卑感"),
            Label("自卑情结", 790, 440, 38, at=5, fill=K.INK2, sfx="wood_low", gain=0.8, note="右：自卑情结"),
            Custom(lambda c, g, t, d: K.stairs(c, 0, 0, 4, 76, 68, ACC, 1, 0.8, clamp01(t / 0.5)),
                   x=200, y=GROUND, at=0, enter="none"),
            Fig(130, GROUND, 270, at=0, hair="short", mood="calm",
                moves=[(2, dict(x=238, y=GROUND - 68, pose="climb", dur=0.35)),
                       (2.7, dict(pose="stand")),
                       (4, dict(x=314, y=GROUND - 136, pose="climb", mood="smile", dur=0.35, sfx="bongo_high",
                                gain=0.8, note="左边的人一步步往上爬")),
                       (4.7, dict(pose="stand")),
                       (6, dict(x=390, y=GROUND - 204, pose="climb", dur=0.35)),
                       (6.7, dict(pose="stand")),
                       (9, dict(x=466, y=GROUND - 272, pose="climb", dur=0.35)),
                       (9.7, dict(pose="cheer", mood="happy"))]),
            Custom(lambda c, g, t, d: K.seat(c, 0, 0, 200, 84, "#9C8C7E"), x=790, y=GROUND, at=0, enter="fade"),
            FigPlus(770, GROUND, 300, at=0, enter="fade", pose="sit_sad", color=GRAY_HERO, hair="short", mood="flat",
                    attach=lambda c, g, geo, d: sign_up(c, g, geo, d), sign=0.0,
                    moves=[(8, dict(pose=dict(K.POSES["sit_sad"], la1=142, la2=12, lean=4, head=4), sign=1.0, dur=0.3,
                                    sfx="rim", gain=0.85, note="右边的人坐着举起“我不行”"))]),
        ], draw=ground, note="左右对照：左边的人一级级爬台阶（自卑感），右边的人坐在箱子上举起“我不行”（自卑情结）"),

        # 6：“因为 A，所以做不到 B”——A 成了挡箭牌
        Shot(3, "“因为A，所以做不到B”，|A 成了挡箭牌。", "岸见一郎阐释", [
            Custom(formula_a, x=210, y=600, at=1, enter="pop", m=0.0, tx=430, ty=360, at_m=8, sfx="wood_low",
                   note="A 卡：学历",
                   moves=[(8, dict(m=1.0, dur=0.45, sfx="rim", note="A 卡旋转着落到主角身前，变成盾牌"))]),
            Arrow((340, 600), (700, 600), at=2, color=K.INK2, width=10),
            Txt("所以", 520, 548, 38, at=2, font="serif", color=K.INK2),
            Custom(lambda c, g, t, d: K.card(c, 0, 0, 220, 210, K.PAPER, 1, 22, 1.0, 3, 1, K.INK3,
                                             lambda c, w, h: (K.text(c, "B", 0, -30, 80, "serif_black", K.INK2),
                                                              K.text(c, "成功", 0, 52, 44, "serif"))),
                   x=850, y=600, at=3, enter="pop", sfx="wood_high", gain=0.85, note="B 卡：成功"),
            Icon("cross", 945, 505, 100, color=K.RED, at=5, enter="pop", sfx="bongo_low", gain=0.8,
                 note="B 被打上叉：做不到"),
            Fig(460, GROUND, 330, at=0, hair="short", mood="calm",
                moves=[(5, dict(mood="worried")), (8.3, dict(pose="hide", mood="flat", dur=0.35))]),
        ], draw=ground, note="公式卡“A 学历 → 所以 → B 成功 ✕”；A 卡旋转飞到主角身前变成盾牌，主角躲在后面"),

        # 7：玻璃罩里的“可能性”
        Shot(3, "只要不去试，|“我本来可以”就永远成立。", "机制示意", [
            Custom(dome, x=640, y=GROUND, at=0, enter="fade", glint=2, lock=0.0,
                   moves=[(8, dict(lock=1.0, dur=0.3, sfx="rim", gain=0.85, note="玻璃罩上了锁"))]),
            Label("可能性", 640, 1030, 36, at=4, fill=ACC, idle=False, sfx="wood_high", gain=0.8,
                  note="底座上的标签：可能性"),
            Fig(250, GROUND, 330, at=0, hair="short", mood="smile",
                moves=[(6, dict(x=420, pose="hug", mood="calm", dur=0.6, sfx="wood_low", gain=0.85,
                                note="主角上前抱住玻璃罩")),
                       (9, dict(mood="worried", look=0.4))]),
        ], draw=ground, hits=[(2, "shaker", 0.7, "奖杯在罩子里闪光")],
            note="玻璃罩里放着奖杯，标签“可能性”；主角抱住罩子守着，罩子上了锁，从不打开"),

        # 8：另一种面具——王冠落下
        Shot(2, "另一种面具：|优越情结。", "阿德勒原著", [
            Custom(lambda c, g, t, d: K.spotlight(c, 0, 0, 430, K.GOLD, 0.4 * clamp01(g.since(4) / 0.3)),
                   x=540, y=860, at=0, enter="none"),
            FigPlus(540, GROUND, 360, at=0, color=K.OTHER2, hair="short", mood="worried", attach=crown_on,
                    crown_drop=4,
                    moves=[(4, dict(pose="proud", mood="smile", dur=0.3, sfx="rim", note="王冠落到头上，立刻挺胸")),
                           (6, dict(mood="happy", sfx="wood_high", gain=0.75, note="得意地笑"))]),
            Custom(lambda c, g, t, d: gcloud(c, 0, 0, d["cs"]), x=560, y=650, at=0, enter="pop", cs=130,
                   moves=[(3.6, dict(y=940, cs=40, alpha=0.0, dur=0.4))]),
        ], draw=ground, text_beat=0, note="一个人头顶飘着小灰云；第 4 拍王冠落下，灰云被压进心里，他立刻挺起胸"),

        # 9：箱子堆上的王冠，里面缩着一个小影子
        Shot(2, "用“假装很强”，|掩盖心里的“我不行”。", "阿德勒原著 · 大意", [
            Custom(boxes, x=0, y=GROUND, at=0, enter="fade", cols=[(540, 3)]),
            Custom(xray, x=540, y=GROUND - 160, at=0, enter="none", open=0.0,
                   moves=[(2, dict(open=1.0, dur=0.4, sfx="shaker", note="箱子堆里透出一个缩成一团的小影子"))]),
            FigPlus(540, GROUND - 375, 270, at=0, enter="fade", color=K.OTHER2, hair="short", mood="smile",
                    pose="proud", attach=crown_on,
                    moves=[(6, dict(pose="cheer", mood="happy", sfx="bongo_low", gain=0.85, note="上面的人更加得意"))]),
            Bubble("我不行", 830, 960, 36, at=4, tail=(-0.8, 0.4), think=True, sfx="wood_low", gain=0.8,
                   note="小影子心里的“我不行”"),
        ], draw=ground, text_beat=0, note="戴王冠的人站在高高的箱子堆上；箱子里透出一个缩成一团的小影子，心里想着“我不行”"),

        # 10：炫耀、贬低、比惨
        Shot(3, "炫耀头衔、贬低别人，|甚至拿不幸来显得特别。", "岸见一郎阐释", [
            FigPlus(330, GROUND, 330, at=0, color=K.OTHER2, hair="short", mood="smile", pose="proud",
                    attach=[crown_on, megaphone_at, cloud_trophy_at], mega=0.0, ctrophy=0.0,
                    moves=[(2, dict(pose="point", mega=1.0, mood="open", dur=0.25, sfx="wood_high", gain=0.85,
                                    note="拿喇叭炫耀头衔")),
                           (4, dict(mega=0.0, mood="angry", dur=0.2, sfx="rim", gain=0.85, note="指着别人贬低")),
                           (6, dict(pose="wave", ctrophy=1.0, mood="happy", dur=0.3, sfx="bongo_high", gain=0.85,
                                    note="把灰云当奖杯高高举起"))]),
            Bubble("我可是总监！", 690, 640, 40, at=2, out=3.8, tail=(-0.6, 1), note=""),
            Fig(860, GROUND, 280, at=0, color=K.OTHER, hair="bun", face=-1, mood="calm",
                moves=[(4, dict(pose="sad", mood="sad", s=255)), (6.4, dict(pose="stand", mood="surprised", s=280))]),
            Bubble("你不行", 690, 640, 40, at=4, out=5.8, tail=(0.5, 1)),
            Bubble("我最惨！", 690, 600, 40, at=6.2, tail=(-0.7, 1)),
        ], draw=ground, note="戴王冠的人三连快切：拿喇叭炫耀头衔、指着别人说“你不行”、把灰云当奖杯举起来说“我最惨”"),

        # 11：摘下王冠，走下箱子
        Shot(3, "真正自信的人，|不需要证明给谁看。", "岸见一郎阐释", [
            Custom(boxes, x=0, y=GROUND, at=0, enter="fade", cols=[(300, 3), (515, 2), (730, 1)], w=210),
            Icon("crown", 330 + CROWN_FIG["head"][0], GROUND - 375 + CROWN_FIG["head"][1] - CROWN_FIG["r"] * 0.95 - 20,
                 CROWN_FIG["r"] * 2.1, color=K.GOLD, accent=K.RED, at=0, enter="fade", idle=False,
                 moves=[(2, dict(y=GROUND - 375 - 380, dur=0.35, ease="out", sfx="wood_low", gain=0.85,
                                 note="他把王冠摘下来")),
                        (3, dict(x=230, y=GROUND - 375 - 30, dur=0.4))]),
            Fig(330, GROUND - 375, 270, at=0, enter="fade", color=K.OTHER2, hair="short", mood="calm",
                moves=[(2, dict(pose="reach", look=0.6, dur=0.3)),
                       (3, dict(pose="stand", look=0.0)),
                       (4, dict(x=515, y=GROUND - 250, mood="smile", dur=0.4, sfx="bongo_low", gain=0.8,
                                note="走下一级箱子")),
                       (5, dict(x=730, y=GROUND - 125, dur=0.4)),
                       (6, dict(x=900, y=GROUND, dur=0.4, sfx="bongo_high", gain=0.75, note="落到地面")),
                       (8, dict(pose="relax", mood="happy", sfx="shaker", gain=0.8, note="轻松地笑"))]),
        ], draw=ground, note="那个人摘下王冠放在箱顶，一级级走下箱子，落地后轻松地笑"),

        # 12：小练习——改写句子
        Shot(4, "听见自己说“要不是”，|换成“即使如此，也试试”。", "小练习", [
            Custom(rewrite_card, x=460, y=720, at=0, enter="fade", note="旧句被划掉，新句翻上来"),
            Fig(900, GROUND, 270, at=0, hair="short", face=-1, pose="shrug", mood="worried",
                moves=[(8, dict(pose="stand", mood="open")),
                       (12, dict(pose="fist", mood="happy", sfx="bongo_high", gain=0.8, note="主角握拳给自己打气"))]),
        ], hits=[(4, "rim", 0.9, "旧句子被划掉"), (8, "clap", 0.9, "新句子出现")], draw=ground,
            note="改写练习：“要不是学历不好，我早就成功了”被划掉，“即使如此，也试试投一份简历”翻上来"),

        # 13：小练习——掀开玻璃罩
        Shot(4, "今天做一件|“本来可以”的小事。", "小练习", [
            Fig(560, GROUND, 330, at=0, hair="short", face=-1, mood="calm",
                moves=[(2, dict(pose="reach", mood="open", look=0.4)),
                       (4, dict(pose="wave", mood="smile", look=0.6)),
                       (12, dict(pose="cheer", mood="happy"))]),
            Custom(dome, x=300, y=GROUND, at=0, enter="fade", lift=0.0, take=0.0, ts=130,
                   trophy_to=(260 + WAVE_HAND[0], WAVE_HAND[1] - 40),
                   moves=[(2, dict(lift=1.0, dur=0.5, sfx="wood_low", gain=0.85, note="主角掀开玻璃罩")),
                          (4, dict(take=1.0, dur=0.5, sfx="bongo_high", gain=0.85, note="拿出一个小奖杯举起来"))]),
            Custom(checklist, x=790, y=560, at=8, enter="pop", tick=12, sfx="wood_high", gain=0.8,
                   note="清单卡：今天的小事"),
        ], draw=ground, hits=[(12, "clap", 0.9, "清单打勾")],
            note="主角掀开玻璃罩，拿出一个小奖杯举起来；清单上“投一份简历”打上勾"),

        # 14：放下挡箭牌，路展开
        Shot(2, "放下挡箭牌，|才看得见路。", "阿德勒的视角", [
            Custom(road, x=0, y=0, at=0, enter="none", p=0.0,
                   moves=[(4, dict(p=1.0, dur=0.7, sfx="shaker", note="前方的路展开"))]),
            Icon("sun", 830, 560, 150, color=K.GOLD, at=4.5, enter="pop", p=lambda g, t: t * 0.4),
            Fig(380, GROUND, 330, at=0, enter="rise", pose="block", hair="short", mood="worried",
                moves=[(2, dict(pose="stand", mood="calm")),
                       (4, dict(mood="smile", look=0.5)),
                       (6, dict(x=520, mood="happy", dur=0.6, sfx="bongo_high", gain=0.8, note="主角迈步上路"))]),
            Icon("shield", 520, 960, 270, color=K.mix(ACC, K.HERO, 0.25), at=0, enter="rise",
                 moves=[(2, dict(x=200, y=1060, rot=-14, s=170, dur=0.45, sfx="wood_low", gain=0.85,
                                 note="主角把盾牌放下"))]),
        ], draw=ground, note="主角举着的盾牌放到一边，前方的路一下展开，通向远处的太阳"),

        end_shot(["Adler, A. (1931). What Life Should Mean to You, ch.3.（中译《自卑与超越》）",
                  "Adler, A. (1929). The Science of Living.（中译《生活的科学》）",
                  "岸见一郎、古贺史健（2013）《被讨厌的勇气》"], "04 追求优越：你一直在和谁比赛？"),
    ]
    return Episode(3, "complex", "自卑情结", "“要不是因为……，我早就……”", ACC, shots,
                   refs=["Adler, A. (1931). What Life Should Mean to You, ch.3.（中译《自卑与超越》）",
                         "Adler, A. (1929). The Science of Living.（中译《生活的科学》）",
                         "岸见一郎、古贺史健（2013）《被讨厌的勇气》"],
                   publish_title="“要不是因为……，我早就……”｜阿德勒心理学03 自卑情结",
                   hashtags="#阿德勒 #心理学 #自卑情结 #借口 #被讨厌的勇气",
                   cover_title="“要不是因为……|我【早就】……”", cover_sub="阿德勒谈自卑情结", cover_shot=0, cover_t=5.6,
                   notes=[
                       "自卑情结的定义据 What Life Should Mean to You 第 3 章：“An inferiority complex appears before a problem "
                       "for which an individual is not properly adapted or equipped, and expresses his conviction that he is "
                       "unable to solve it.” 阿德勒学派把它描述为逃避参与的借口。",
                       "优越情结是阿德勒的概念：用表面的优越掩盖或逃避自卑（The Science of Living, 1929）。",
                       "“因为 A 所以做不到 B”（見かけの因果律）与“拿不幸显得特别”（不幸自慢）出自《被讨厌的勇气》第二夜，"
                       "片中标注“岸见一郎阐释”。",
                   ]).build()


def sign_up(c, g, geo, d):
    """举在手里的“我不行”牌子（竹竿 + 纸牌）。"""
    m = clamp01(d.get("sign", 0.0))
    if m <= 0:
        return
    hx, hy = geo["hand"]
    K.seg(c, hx, hy + 20, hx, hy - 120 * m, "#8C6E52", 8)
    sc = 0.4 + 0.6 * ease_out_back(m, 2)
    K.text_card(c, hx, hy - 150 * m, ["我不行"], 40, None, K.PAPER, K.INK, ACC, m, 3, sc, accent=GRAY)
