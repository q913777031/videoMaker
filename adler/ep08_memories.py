"""08 早期记忆：你最早的记忆，藏着什么？"""

import math
from contextlib import contextmanager

import skia

from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, ease_out_back, lerp

from . import kit as K
from .core import Big, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

ACC = "#B8763A"
GROUND = 1130
LENS_GRAY = "#8C929C"
LENS_WARM = "#F0A93A"


def ground(g):
    K.ground(g.c, GROUND)


# ---------------------------------------------------------------- 通用小工具

def fig_geom(s, p="stand", face=1, bob=0.0):
    """按 kit.figure 的骨架算法求头部中心、头半径、头部倾角与前手位置（相对脚底中点）。"""
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
    return dict(head=(hx, hy), r=0.16 * u, tilt=d["head"] * 0.35 * face, hand=hand)


def mat(kind: str, k: float = 1.0) -> list:
    """颜色矩阵（与单位矩阵按 k 插值）：gray 灰阶 / amber 琥珀单色 / warm 暖调。"""
    ident = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]
    lum = (0.299, 0.587, 0.114)
    if kind == "none":
        return ident
    if kind == "gray":
        m = [*[x * 0.94 for x in lum], 0, 0, *[x * 0.94 for x in lum], 0, 0, *[x * 0.96 for x in lum], 0, 0,
             0, 0, 0, 1, 0]
    elif kind == "amber":
        a = (1.16, 0.93, 0.66)
        m = [*[x * a[0] for x in lum], 0, 0, *[x * a[1] for x in lum], 0, 0, *[x * a[2] for x in lum], 0, 0,
             0, 0, 0, 1, 0]
    else:  # warm
        m = [1.07, 0.05, 0, 0, 0, 0.02, 1.0, 0, 0, 0, 0, 0, 0.86, 0, 0, 0, 0, 0, 1, 0]
    return [lerp(a_, b_, k) for a_, b_ in zip(ident, m)]


def mat_mix(m1, m2, k):
    return [lerp(a, b, k) for a, b in zip(m1, m2)]


@contextmanager
def filt(c, m):
    """颜色滤镜图层：块内绘制的内容整体经过颜色矩阵。"""
    c.saveLayer(None, skia.Paint(ColorFilter=skia.ColorFilters.Matrix(m)))
    try:
        yield
    finally:
        c.restore()


def glasses(c, R, frame=K.INK, lens=None, lens_a=0.35, temples="both", face=1, alpha=1.0, glint=-1.0):
    """一副圆框眼镜（正视）：原点为鼻梁中心，R 为镜片半径；temples=both 两侧镜腿 / back 只画脑后一侧。
    glint ∈ [0, 1] 时镜片上扫过一道反光。"""
    if alpha <= 0:
        return
    fw = max(3.5, 0.2 * R)
    for sx in (-1, 1):
        cx = sx * 1.12 * R
        if lens:
            K.dot(c, cx, 0, R, lens, lens_a * alpha)
        if 0 <= glint <= 1:
            c.save()
            path = skia.Path()
            path.addCircle(cx, 0, R)
            c.clipPath(path, doAntiAlias=True)
            gx = cx + lerp(-1.6 * R, 1.6 * R, glint)
            K.poly(c, [(gx - 0.25 * R, -R), (gx + 0.15 * R, -R), (gx - 0.15 * R, R), (gx - 0.55 * R, R)], K.PAPER,
                   0.7 * alpha)
            c.restore()
        K.ring(c, cx, 0, R, frame, fw, alpha)
        if lens:
            K.seg(c, cx - 0.45 * R, -0.35 * R, cx - 0.2 * R, -0.6 * R, K.PAPER, max(2, 0.09 * R), 0.75 * alpha)
    br = skia.Path()
    br.moveTo(-0.16 * R, -0.12 * R)
    br.quadTo(0, -0.42 * R, 0.16 * R, -0.12 * R)
    c.drawPath(br, K.paint(frame, alpha, fw))
    if temples == "both":
        for sx in (-1, 1):
            K.seg(c, sx * 2.12 * R, -0.25 * R, sx * 2.62 * R, -0.62 * R, frame, fw, alpha)
    elif temples == "back":
        K.seg(c, -face * 2.12 * R, -0.12 * R, -face * 3.2 * R, -0.3 * R, frame, fw, alpha)


def face_glasses(c, geo, face, lens, lens_a=0.45, alpha=1.0, dx=0.0, dy=0.0, rot=0.0, z=1.0, temples="back",
                 frame=K.INK):
    """把眼镜戴在 fig_geom 求出的头部上（dx/dy/rot/z 为相对脸上位置的偏移，用于戴上 / 摘下的过程）。"""
    hx, hy = geo["head"]
    r = geo["r"]
    with K.at(c, hx, hy, geo["tilt"]):
        with K.at(c, face * 0.42 * r + dx, 0.05 * r + dy, rot, z):
            glasses(c, 0.2 * r, frame, lens, lens_a, temples, face, alpha)


def padlock(c, s, color=K.INK, alpha=1.0):
    with K.paper(c, alpha, 0.6):
        path = skia.Path()
        path.addArc(skia.Rect.MakeXYWH(-s * 0.28, -s * 0.62, s * 0.56, s * 0.6), 180, 180)
        c.drawPath(path, K.paint(color, 1, s * 0.12))
        K.seg(c, -s * 0.28, -s * 0.32, -s * 0.28, -s * 0.12, color, s * 0.12)
        K.seg(c, s * 0.28, -s * 0.32, s * 0.28, -s * 0.12, color, s * 0.12)
        K.rr(c, 0, s * 0.12, s * 0.8, s * 0.56, s * 0.1, ACC)
        K.dot(c, 0, s * 0.06, s * 0.07, K.INK)
        K.seg(c, 0, s * 0.08, 0, s * 0.24, K.INK, s * 0.06)


# ---------------------------------------------------------------- 回忆照片里的小场景

def sc_first(c, w, h):
    """最早的记忆：雾里的小人与太阳，看不太清。"""
    gy = h / 2 - 16
    K.dot(c, 90, -40, 30, K.GOLD)
    K.figure(c, -30, gy, 120, "wave", K.HERO, mood="happy", hair="short", lift=0.3)
    K.icon(c, "house", 80, gy - 40, 90, K.OTHER3, 1, 0.2, 0, 1, 1.0, K.GOLD)
    for x, y, r in ((-110, -30, 70), (20, 30, 60), (130, 50, 70), (-60, 70, 60)):
        c.drawCircle(x, y, r, K.paint("#FFFFFF", 0.5, 0, 18))


def sc_praise(c, w, h):
    """被夸奖：大人摸摸小孩的头，小孩举手欢呼。"""
    gy = h / 2 - 14
    K.figure(c, 52, gy, 200, "give", K.OTHER3, face=-1, mood="happy", hair="bun", lift=0.3)
    K.figure(c, -40, gy, 112, "cheer", K.HERO, mood="happy", hair="short", lift=0.3)
    K.star(c, -110, gy - 120, 15, K.GOLD)
    K.star(c, -80, gy - 160, 10, K.GOLD)


def sc_lost(c, w, h):
    """迷路：一群大人的腿匆匆走过，小孩站在中间抬头张望。"""
    gy = h / 2 - 14
    for x, cc, f, ph in ((-120, K.OTHER2, 1, 0.5), (118, K.OTHER, -1, 1.5), (-40, "#9C8FB0", -1, 1.0)):
        K.figure(c, x, gy, 300, K.walk(ph, 1.0), cc, face=f, lift=0.3)
    K.figure(c, 30, gy, 104, "stand", K.HERO, mood="worried", hair="short", look=1, lift=0.3, face=-1)
    K.text(c, "?", 60, gy - 135, 44, "black", ACC)


def sc_left(c, w, h):
    """被落下：大人走远，小孩伸手去追。"""
    gy = h / 2 - 14
    K.figure(c, -100, gy, 108, "reach", K.HERO, mood="sad", hair="short", lift=0.3)
    K.figure(c, 70, gy, 165, K.walk(0.5, 1.0), K.OTHER3, hair="bun", lift=0.3)
    K.figure(c, 128, gy, 178, K.walk(1.5, 1.0), K.OTHER2, lift=0.3)


def sc_ball(c, w, h):
    gy = h / 2 - 14
    K.figure(c, -20, gy, 110, "push", K.HERO, mood="happy", hair="short", lift=0.3)
    K.dot(c, 50, gy - 14, 14, K.RED)


def sc_cake(c, w, h):
    gy = h / 2 - 14
    K.figure(c, -40, gy, 110, "cheer", K.HERO, mood="happy", hair="short", lift=0.3)
    K.rr(c, 50, gy - 22, 70, 44, 8, K.PAPER)
    K.rr(c, 50, gy - 40, 70, 10, 4, K.RED)
    for dx in (-18, 0, 18):
        K.seg(c, 50 + dx, gy - 46, 50 + dx, gy - 64, K.GOLD, 5)


def sc_sea(c, w, h):
    gy = h / 2 - 14
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, gy - 50, w, 70), K.paint("#7FA6C2"))
    K.dot(c, 60, -40, 22, K.GOLD)
    K.figure(c, -30, gy, 100, "wave", K.HERO, mood="happy", hair="short", lift=0.3)


def sc_rain(c, w, h):
    gy = h / 2 - 14
    K.figure(c, 0, gy, 105, "sad", K.HERO, mood="sad", hair="short", lift=0.3)
    for k in range(9):
        x = -100 + k * 26
        K.seg(c, x, -80 + (k % 3) * 20, x - 8, -50 + (k % 3) * 20, "#7FA6C2", 4)


SCENES = [sc_ball, sc_cake, sc_sea, sc_rain, sc_praise, sc_left]


# ---------------------------------------------------------------- 第 1 镜：照片从头顶飘出

def thought_dots(c, g, el_t, d):
    for i, (x, y, r) in enumerate(((440, 705, 10), (472, 664, 14), (510, 622, 18))):
        k = clamp01((g.since(2.5 + i * 0.5)) / 0.25)
        if k > 0:
            K.dot(c, x, y, r * ease_out_back(k, 2), K.PAPER, 1)
            K.ring(c, x, y, r * ease_out_back(k, 2), K.LINE, 3)


def float_photo(c, g, el_t, d):
    """回忆照片从头顶的一点长大，飘到目标位置并轻轻浮动。"""
    k = ease_out(clamp01(el_t / d["fly"]))
    if el_t < 0:
        return
    x = lerp(d["x0"], d["x1"], k)
    y = lerp(d["y0"], d["y1"], k) + 6 * math.sin(g.t * 1.5 + d["ph"]) * k
    K.memory(c, x, y, d["w"], d["h"], d["scene"], d.get("a", 1.0), lerp(0, d["rot"], k), lerp(0.12, 1, k),
             d.get("label", ""))


# ---------------------------------------------------------------- 第 2–3 镜：三张回忆照片

def photo(scene, w, h, label):
    def fn(c, g, el_t, d):
        K.memory(c, 0, 0, w, h, scene, 1, 0, d.get("z", 1.0), label)
    return fn


def spotlight_bg(g):
    c = g.c
    k = g.p(4, 0.5)
    if k <= 0:
        return
    beam = skia.Path()
    beam.moveTo(490, 386)
    beam.lineTo(590, 386)
    beam.lineTo(880, 1040)
    beam.lineTo(200, 1040)
    beam.close()
    sh2 = skia.GradientShader.MakeLinear([(0, 386), (0, 1040)], [K.col(K.GOLD, 0.34 * k), K.col(K.GOLD, 0.0)])
    c.drawPath(beam, skia.Paint(AntiAlias=True, Shader=sh2))
    K.spotlight(c, 540, 720, 470, K.GOLD, 0.32 * k)
    with K.paper(c, 1, 0.7):
        K.poly(c, [(500, 352), (580, 352), (605, 390), (475, 390)], K.DARK)
    K.rr(c, 540, 392, 120, 10, 5, K.tint(K.GOLD, 0.2), k)


# ---------------------------------------------------------------- 第 4 镜：骰子（偶然）被打叉

def dice(c, g, el_t, d):
    spin = 0.0 if el_t >= 0 else (-el_t / 0.42) * 280
    with K.at(c, 0, 0, spin, 1.2):
        with K.paper(c, 1, 0.9):
            K.rr(c, 0, 0, 150, 150, 30, K.PAPER)
            K.rr_stroke(c, 0, 0, 150, 150, 30, K.LINE, 4)
            for px, py in ((-38, -38), (38, -38), (0, 0), (-38, 38), (38, 38)):
                K.dot(c, px, py, 13, K.INK)


def photo_fan(c, g, el_t, d):
    k = ease_out(clamp01(el_t / 0.5))
    for i, (sc, rot) in enumerate(((sc_sea, -14), (sc_lost, 2), (sc_praise, 15))):
        K.memory(c, (i - 1) * 72 * k, (abs(i - 1)) * 14 * k, 280, 228, sc, 1, rot * k, 1, "")


# ---------------------------------------------------------------- 第 5 镜：磁铁把有关的照片吸进相框

def magnet(c, s, color=K.RED):
    w = s * 0.62
    path = skia.Path()
    path.moveTo(-w / 2, s * 0.42)
    path.lineTo(-w / 2, 0)
    path.arcTo(skia.Rect.MakeXYWH(-w / 2, -w / 2, w, w), 180, 180, False)
    path.lineTo(w / 2, s * 0.42)
    p = K.paint(color, 1, s * 0.26)
    p.setStrokeCap(skia.Paint.kButt_Cap)
    with K.paper(c, 1, 0.8):
        c.drawPath(path, p)
        for sx in (-1, 1):
            K.rr(c, sx * w / 2, s * 0.42, s * 0.26, s * 0.16, 2, "#D7D3CC")


MAG_X, MAG_Y = 620, 450
FRAME_X, FRAME_Y, FRAME_W, FRAME_H = 620, 830, 420, 470
REL = [((210, 470, -8), (555, 720, -6), sc_praise), ((912, 690, 7), (690, 805, 5), sc_lost),
       ((230, 1010, 5), (585, 935, -3), sc_left)]
UNREL = [((200, 745, 6), (-1, 0.2), sc_cake), ((905, 440, -6), (1, -0.3), sc_rain),
         ((905, 990, -4), (1, 0.4), sc_ball)]


def magnet_scene(c, g, el_t, d):
    # 相框
    with K.paper(c, 1, 0.9):
        K.rr(c, FRAME_X, FRAME_Y, FRAME_W, FRAME_H, 18, K.shade(ACC, 0.1))
        K.rr(c, FRAME_X, FRAME_Y, FRAME_W - 52, FRAME_H - 52, 8, K.tint(ACC, 0.82))
    glow = g.p(8, 0.5)
    if glow > 0:
        K.spotlight(c, FRAME_X, FRAME_Y, 420, K.GOLD, 0.35 * glow * (0.8 + 0.2 * math.sin(g.t * 4)))
    # 磁铁（第 2 拍落下）
    km = clamp01((g.t - (g.b(2) - 0.35)) / 0.35)
    if km > 0:
        dy = -380 * (1 - ease_in(km))
        with K.at(c, MAG_X, MAG_Y + dy):
            magnet(c, 170)
    # 磁力线（第 4 拍起脉动）
    for j in range(3):
        dt = g.since(4) - j * 0.18
        if 0 <= dt <= 0.9:
            kk = dt / 0.9
            path = skia.Path()
            rw = lerp(60, 220, kk)
            path.addArc(skia.Rect.MakeXYWH(MAG_X - rw, MAG_Y + 60 - rw * 0.35, 2 * rw, rw * 0.7), 20, 140)
            c.drawPath(path, K.paint(ACC, 0.8 * (1 - kk), 6))
    # 有关的照片飞进相框
    for i, ((x0, y0, r0), (x1, y1, r1), sc) in enumerate(REL):
        k = ease_in_out(clamp01((g.since(4) + 0.42 - i * 0.07) / 0.42)) if g.since(4) > -0.42 else 0.0
        x = lerp(x0, x1, k)
        y = lerp(y0, y1, k) + 6 * math.sin(g.t * 1.6 + i) * (1 - k)
        a = clamp01(g.since(i * 0.25) / 0.3)
        K.memory(c, x, y, 165, 135, sc, a, lerp(r0, r1, k), lerp(1, 1.05, k), "")
        if k <= 0:
            K.rr_stroke(c, x, y, 172, 142, 12, ACC, 5, a * 0.9)
    # 无关的照片飘走（只在舞台内淡出）
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(70, 330, 1010, 1262))
    for i, ((x0, y0, r0), (vx, vy), sc) in enumerate(UNREL):
        k = ease_in(clamp01(g.since(6) / 0.9))
        a = clamp01(g.since(0.12 + i * 0.25) / 0.3) * (1 - k) ** 1.4
        x = x0 + vx * 120 * k
        y = y0 + vy * 120 * k + 6 * math.sin(g.t * 1.6 + i + 3)
        K.memory(c, x, y, 165, 135, sc, a, r0 + vx * 25 * k, 1, "")
    c.restore()


# ---------------------------------------------------------------- 第 6 镜：眼镜落版

def big_glasses(c, g, el_t, d):
    gl = (g.since(8) / 0.6) if g.since(8) >= 0 else -1
    glasses(c, 105, K.INK, ACC, 0.28, "both", 1, 1, gl if gl <= 1 else -1)


def link_lines(c, g, el_t, d):
    for i, x in enumerate((250, 540, 830)):
        p = clamp01((g.since(6) - i * 0.08) / 0.4)
        if p > 0:
            K.arrow(c, (x, 905), (540 + (x - 540) * 0.45, 760), ACC, 7, 0.9, p, 0, 22, dash=(14, 12, 0))


def photo_row(c, g, el_t, d):
    for i, (x, sc, rot) in enumerate(((250, sc_praise, -5), (540, sc_lost, 3), (830, sc_left, -2))):
        a = clamp01(g.since(i * 0.3) / 0.35)
        K.memory(c, x, 1010 + 4 * math.sin(g.t * 1.5 + i), 230, 190, sc, a, rot, 1, "")


# ---------------------------------------------------------------- 第 7 镜：戴上眼镜，世界变成同一种色调

def hero_specs(c, g, el_t, d):
    """主角（自绘以便把眼镜戴在脸上）：第 2 拍眼镜从左上飞来落在脸上。"""
    s, p, face = d.get("s", 380), d.get("pose", "stand"), 1
    bob = 0.006 * math.sin(g.t * 2.6 + d["x"] * 0.02)
    K.figure(c, 0, 0, s, p, K.HERO, K.SKIN, 1, face, d.get("mood", "calm"), "short", None, bob, 1.0,
             d.get("look", 0.0))
    geo = fig_geom(s, p, face, bob)
    k = clamp01((g.t - (g.b(2) - 0.55)) / 0.55)
    if k <= 0:
        return
    e = ease_in_out(k)
    face_glasses(c, geo, face, ACC, 0.5, 1, lerp(-480, 0, e), lerp(-430, 0, e) - 120 * math.sin(math.pi * e),
                 lerp(-25, 0, e), lerp(5.0, 1, e), "both" if k < 1 else "back")
    hx, hy = geo["head"]
    K.burst(c, hx + 25, hy, g.since(2), ACC, 50, 130, 10, 6)
    kl = clamp01(g.since(8) / 0.3)
    if kl > 0:
        with K.at(c, hx + 95, hy - 70, -8, 0.4 + 0.6 * ease_out_back(kl, 2)):
            padlock(c, 64, K.INK, kl)


def tint_open(kind_from, kind_to, beat, dur=0.6, base=None, wash_from=None, wash_to=None):
    """在 draw 中打开一层颜色滤镜（over 中关闭），第 beat 拍起在 dur 秒内从 kind_from 过渡到 kind_to；
    wash_* 为 (颜色, 透明度) 的舞台中心柔光，让纸底也带上该色调。"""
    def draw(g):
        k = g.p(beat, dur, ease_in_out)
        g.c.saveLayer(None, skia.Paint(ColorFilter=skia.ColorFilters.Matrix(mat_mix(mat(kind_from), mat(kind_to), k))))
        for wash, w in ((wash_from, 1 - k), (wash_to, k)):
            if wash and wash[1] * w > 0:
                sh = skia.GradientShader.MakeRadial((540, 795), 470, [K.col(wash[0], wash[1] * w), K.col(wash[0], 0)],
                                                    [0.3, 1])
                g.c.drawRect(skia.Rect.MakeLTRB(70, 325, 1010, 1265), skia.Paint(AntiAlias=True, Shader=sh))
        if base:
            base(g)
    return draw


def tint_close(extra=None):
    def over(g):
        g.c.restore()
        if extra:
            extra(g)
    return over


def wash_ring(g):
    """第 4 拍：色调从眼镜处扩散出去的光环。"""
    g.c.save()
    g.c.clipRect(skia.Rect.MakeLTRB(70, 330, 1010, 1262))
    K.ripple(g.c, 565, 787, g.since(4), ACC, 640, 14, 0.7, 0.9)
    g.c.restore()


# ---------------------------------------------------------------- 第 8 镜：研究证据（年龄轴、雾与拼图）

AX0, AX_Y, AX_STEP = 150, 1020, 130
PAWNS = [(165 + i * 83, 560) for i in range(10)]
CLAIM = (1, 3, 6, 8)
PZ_X, PZ_Y, PZ_W, PZ_H = 340, 830, 280, 210
PIECES = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
SCATTER = [(-120, -110, -28), (130, -90, 24), (-140, 90, 18), (120, 110, -30)]


def pawn(c, x, y, s, color, alpha=1.0):
    with K.paper(c, alpha, 0.5):
        K.dot(c, x, y - s * 0.78, s * 0.19, color)
        path = skia.Path()
        path.addRoundRect(skia.Rect.MakeXYWH(x - s * 0.27, y - s * 0.55, s * 0.54, s * 0.55), s * 0.22, s * 0.22)
        c.drawPath(path, K.paint(color))


def puzzle_scene(c, w, h):
    K.rr(c, 0, 0, w, h, 4, "#C9B79C")
    K.dot(c, w * 0.28, -h * 0.22, h * 0.13, K.GOLD)
    K.figure(c, -w * 0.12, h * 0.42, h * 0.62, "wave", K.HERO, mood="happy", hair="short", lift=0.2)
    K.icon(c, "house", w * 0.24, h * 0.24, h * 0.38, K.OTHER3, 1, 0.1, 0, 1, 1.0, K.GOLD)


def research_scene(c, g, el_t, d):
    # 年龄轴 0–6 岁
    pa = g.p(0, 0.6)
    K.seg(c, AX0, AX_Y, AX0 + 6 * AX_STEP + 20, AX_Y, K.INK2, 6, 1, pa)
    for i in range(7):
        x = AX0 + i * AX_STEP
        a = clamp01((g.since(0) - i * 0.06) / 0.3)
        K.seg(c, x, AX_Y - 12, x, AX_Y + 12, K.INK2, 5, a)
        K.text(c, f"{i}岁" if i in (0, 6) else str(i), x, AX_Y + 46, 30, "sans_medium", K.INK2, a)
    # 3 岁前的雾
    fa = g.p(0, 0.8)
    sh = skia.GradientShader.MakeLinear([(AX0 + 2.6 * AX_STEP, 0), (AX0 + 3.3 * AX_STEP, 0)],
                                        [K.col(K.INK3, 0.16 * fa), K.col(K.INK3, 0)])
    c.drawRoundRect(skia.Rect.MakeLTRB(AX0 - 50, 650, AX0 + 3.3 * AX_STEP, AX_Y + 30), 40, 40,
                    skia.Paint(AntiAlias=True, Shader=sh))
    for j, (fx, fy, r) in enumerate(((210, 990, 95), (330, 960, 110), (450, 1000, 95), (240, 830, 105),
                                     (420, 800, 115), (320, 700, 95), (500, 900, 90), (190, 700, 80))):
        dx = 22 * math.sin(g.t * 0.7 + j * 1.3)
        c.drawCircle(fx + dx, fy, r, K.paint("#FFFFFF", 0.62 * fa, 0, 22))
    # 十个人，其中四个说记得两岁前（第 4 拍）
    for i, (x, y) in enumerate(PAWNS):
        a = clamp01((g.since(0.5) - i * 0.05) / 0.3)
        lit = i in CLAIM and g.since(4) >= 0
        pawn(c, x, y, 110, ACC if lit else K.INK3, a)
    for j, i in enumerate(CLAIM):
        x, y = PAWNS[i]
        k = clamp01(g.since(4) / 0.3)
        if k <= 0:
            continue
        # 头顶的小回忆片：第 6 拍飞进雾里变成拼图碎片
        f = ease_in_out(clamp01((g.since(6) + 0.0) / 0.55))
        if f < 1:
            sx, sy, srot = SCATTER[j]
            tx, ty = PZ_X + sx, PZ_Y + sy
            px, py = lerp(x, tx, f), lerp(y - 150, ty, f) - 80 * math.sin(math.pi * f)
            with K.at(c, px, py, srot * f, (0.5 + 0.5 * ease_out_back(k, 2)) * lerp(0.6, 1, f)):
                with K.paper(c, 1, 0.5):
                    K.rr(c, 0, 0, 62, 50, 4, K.PAPER)
                    K.rr(c, 0, -3, 50, 34, 2, "#C9B79C")
                    K.dot(c, 10, -8, 6, K.GOLD)
    # 拼图：第 6 拍散落在雾里，第 8 拍拼起
    if g.since(6) + 0.0 >= 0.5:
        asm = ease_in_out(clamp01((g.t - (g.b(8) - 0.5)) / 0.5))
        for j, (qx, qy) in enumerate(PIECES):
            sx, sy, srot = SCATTER[j]
            ox, oy = lerp(sx, qx * PZ_W / 4, asm), lerp(sy, qy * PZ_H / 4, asm)
            gap = 6 * (1 - asm)
            with K.at(c, PZ_X + ox + qx * gap, PZ_Y + oy + qy * gap, srot * (1 - asm)):
                with K.paper(c, 1, 0.5 * (1 - asm) + 0.15):
                    c.save()
                    c.clipRect(skia.Rect.MakeXYWH(-PZ_W / 4, -PZ_H / 4, PZ_W / 2, PZ_H / 2))
                    c.translate(-qx * PZ_W / 4, -qy * PZ_H / 4)
                    puzzle_scene(c, PZ_W, PZ_H)
                    c.restore()
                    # 拼图凸起
                    K.dot(c, -qx * PZ_W / 4 * 0 + (PZ_W / 4 if qx < 0 else -PZ_W / 4), 0, 13, "#C9B79C")
        if asm >= 1:
            K.rr_stroke(c, PZ_X, PZ_Y, PZ_W, PZ_H, 6, K.PAPER, 4, 0.9)
            K.seg(c, PZ_X - PZ_W / 2, PZ_Y, PZ_X + PZ_W / 2, PZ_Y, K.PAPER, 3, 0.8)
            K.seg(c, PZ_X, PZ_Y - PZ_H / 2, PZ_X, PZ_Y + PZ_H / 2, K.PAPER, 3, 0.8)
    # 平均约 3.2 岁（第 12 拍）
    kp = clamp01((g.t - (g.b(12) - 0.3)) / 0.3)
    if kp > 0:
        x = AX0 + 3.2 * AX_STEP
        y = AX_Y - 420 * (1 - ease_in(kp))
        with K.paper(c, kp, 0.7):
            path = skia.Path()
            path.moveTo(x, y)
            path.lineTo(x - 26, y - 46)
            path.arcTo(skia.Rect.MakeXYWH(x - 34, y - 102, 68, 68), 150, 240, False)
            path.close()
            c.drawPath(path, K.paint(ACC))
            K.dot(c, x, y - 68, 13, K.PAPER)
        K.ripple(c, x, AX_Y, g.since(12), ACC, 110, 6, 0.7, 0.6)


# ---------------------------------------------------------------- 第 9 镜：不是诊断书，更像镜子

def diagnosis(c, g, el_t, d):
    with K.paper(c, 1, 0.9):
        K.rr(c, 0, 0, 280, 340, 16, K.PAPER)
        K.rr(c, 0, -170, 110, 40, 10, K.INK3)
        K.text(c, "诊断书", 0, -100, 46, "serif_black", K.INK)
        for k in range(4):
            K.seg(c, -100, -20 + k * 46, 100 - (k % 2) * 50, -20 + k * 46, K.LINE, 8)
    p = ease_out(clamp01(g.since(3) / 0.3))
    if p > 0:
        K.seg(c, -150, -140, -150 + 300 * p, -140 + 300 * p, K.RED, 14)
        K.seg(c, 150, -140, 150 - 300 * clamp01(p * 1.3 - 0.3), -140 + 300 * clamp01(p * 1.3 - 0.3), K.RED, 14)


MIR_X, MIR_Y, MIR_W, MIR_H = 760, 780, 300, 420


def mirror(c, g, el_t, d):
    """落地镜：镜面里映出主角（朝左），与主角同步换姿势和表情。"""
    with K.paper(c, 1, 0.9):
        K.rr(c, 0, (MIR_H / 2 + GROUND - MIR_Y) / 2, 26, GROUND - MIR_Y - MIR_H / 2, 8, K.shade(ACC, 0.25))
        K.rr(c, 0, GROUND - MIR_Y - 8, 190, 22, 11, K.shade(ACC, 0.25))
        c.drawOval(skia.Rect.MakeXYWH(-MIR_W / 2 - 18, -MIR_H / 2 - 18, MIR_W + 36, MIR_H + 36), K.paint(ACC))
    oval = skia.Rect.MakeXYWH(-MIR_W / 2, -MIR_H / 2, MIR_W, MIR_H)
    c.drawOval(oval, K.paint("#DCE6EC"))
    c.save()
    path = skia.Path()
    path.addOval(oval)
    c.clipPath(path, doAntiAlias=True)
    a = ease_out(clamp01(g.since(6.4) / 0.5))
    if a > 0:
        p = d.get("pose", "stand")
        K.figure(c, 0, MIR_H / 2 + 40, 300, p, K.mix(K.HERO, "#DCE6EC", 0.18), alpha=a, face=-1,
                 mood=d.get("mood", "calm"), hair="short", lift=0.0)
    K.poly(c, [(-MIR_W * 0.2, -MIR_H / 2), (-MIR_W * 0.02, -MIR_H / 2), (-MIR_W * 0.5, MIR_H * 0.1),
               (-MIR_W * 0.5, -MIR_H * 0.15)], "#FFFFFF", 0.45)
    c.restore()


# ---------------------------------------------------------------- 第 10 镜：同一张照片，两副眼镜

def lens_photo(kind, glass_col, beat, glass_dx):
    def fn(c, g, el_t, d):
        k = g.p(beat, 0.45, ease_in_out)
        m = mat(kind, k)
        with filt(c, m):
            K.memory(c, 0, 0, 400, 310, sc_lost, 1, 0, 1, "迷路")
        kg = clamp01((g.t - (g.b(beat) - 0.35)) / 0.35)
        if kg > 0:
            with K.at(c, glass_dx, -190 - 300 * (1 - ease_in(kg))):
                glasses(c, 58, K.INK, glass_col, 0.55, "both", 1, kg)
            K.burst(c, glass_dx, -190, g.since(beat), glass_col, 60, 170, 10, 6)
    return fn


# ---------------------------------------------------------------- 第 11 镜：摘下旧眼镜，戴上新眼镜

def hero_swap(c, g, el_t, d):
    s, p, face = d.get("s", 380), d.get("pose", "stand"), 1
    bob = 0.006 * math.sin(g.t * 2.6 + d["x"] * 0.02)
    K.figure(c, 0, 0, s, p, K.HERO, K.SKIN, 1, face, d.get("mood", "calm"), "short", None, bob, 1.0,
             d.get("look", 0.0))
    geo = fig_geom(s, p, face, bob)
    hx, hy = geo["head"]
    # 旧眼镜：第 4 拍从脸上弹起，翻滚着落到脚边
    ko = clamp01(g.since(4) / 0.75)
    if ko <= 0:
        face_glasses(c, geo, face, LENS_GRAY, 0.6)
    else:
        ex, ey = hx + 0.42 * geo["r"], hy
        tx, ty = -190, -14
        x = lerp(ex, tx, ko)
        y = lerp(ey, ty, ko) - 220 * math.sin(math.pi * min(1, ko * 1.1)) * (1 - ko * 0.3)
        with K.at(c, x, y, -260 * ease_out(ko), lerp(1, 2.2, ease_out(ko))):
            glasses(c, 0.2 * geo["r"], K.INK, LENS_GRAY, 0.6, "both", 1, 1)
    # 新眼镜：第 8 拍从上方落到脸上
    kn = clamp01((g.t - (g.b(8) - 0.5)) / 0.5)
    if kn > 0:
        e = ease_in(kn)
        face_glasses(c, geo, face, LENS_WARM, 0.5, 1, 0, lerp(-360, 0, e), 0, lerp(3.0, 1, e),
                     "both" if kn < 1 else "back")
        K.burst(c, hx + 25, hy, g.since(8), K.GOLD, 50, 140, 10, 6)


# ---------------------------------------------------------------- 第 12 镜：写下最早的记忆

NB_X, NB_Y = 540, 800
LINES = [(-150, 290, 2, 3.4), (-80, 250, 4, 5.4), (-10, 300, 6, 7.4), (60, 170, 8, 9.0)]


def scribble(x0, y0, length, seed):
    path = skia.Path()
    path.moveTo(x0, y0)
    n = int(length / 14)
    for i in range(1, n + 1):
        x = x0 + i * length / n
        y = y0 + (5 if i % 2 else -5) * (0.6 + 0.4 * math.sin(i * 1.7 + seed))
        path.lineTo(x, y)
    return path


def pencil(c, x, y, alpha=1.0):
    with K.at(c, x, y, 40):
        with K.paper(c, alpha, 0.8):
            K.rr(c, 0, -80, 26, 130, 4, K.GOLD)
            K.rr(c, 0, -150, 26, 18, 4, "#E79AA0")
            K.poly(c, [(-13, -15), (13, -15), (0, 10)], "#F1D6B8")
            K.poly(c, [(-4, 2), (4, 2), (0, 10)], K.INK)


def notebook(c, g, el_t, d):
    w, h = 800, 560
    with K.paper(c, 1, 0.9):
        K.rr(c, 0, 0, w + 20, h + 20, 22, K.shade(ACC, 0.15))
        K.rr(c, -w / 4 - 4, 0, w / 2 - 12, h - 10, 12, K.PAPER)
        K.rr(c, w / 4 + 4, 0, w / 2 - 12, h - 10, 12, K.PAPER)
    for k in range(9):
        y = -h / 2 + 40 + k * 60
        K.ring(c, 0, y, 13, K.INK2, 5)
    # 左页：贴着那张“迷路”照片
    K.memory(c, -205, -40, 280, 230, sc_lost, 1, -4, 1, "")
    K.rr(c, -205, -158, 80, 26, 4, K.tint(ACC, 0.5), 0.85)
    K.text(c, "最早的记忆", -205, 150, 34, "serif", K.INK2)
    # 右页：按拍写出的线条
    tip = None
    for i, (yy, ln, b0, b1) in enumerate(LINES):
        p = clamp01((g.t - g.b(b0)) / max(1e-6, g.b(b1) - g.b(b0)))
        if p <= 0:
            continue
        path = scribble(60, yy, ln, i)
        gfx_stroke(c, path, K.INK2, 6, p)
        if p < 1:
            pm = skia.PathMeasure(path, False)
            pos, _ = pm.getPosTan(pm.getLength() * p)
            tip = (pos.x(), pos.y())
    # 问句（第 10 拍逐字写出），第 12 拍画圈
    q = "它在提醒我什么？"
    kq = clamp01(g.since(10) / 0.9)
    if kq > 0:
        tw = K.text_w(q, 40, "serif")
        x0 = 60
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(x0 - 4, 110, tw * kq + 8, 80))
        K.text(c, q, x0, 150, 40, "serif", ACC, 1, "left")
        c.restore()
        if kq < 1:
            tip = (x0 + tw * kq, 168)
        kc = clamp01(g.since(12) / 0.5)
        if kc > 0:
            path = skia.Path()
            path.addOval(skia.Rect.MakeXYWH(x0 - 24, 108, tw + 48, 86))
            gfx_stroke(c, path, K.RED, 6, kc)
            if kc < 1:
                pm = skia.PathMeasure(path, False)
                pos, _ = pm.getPosTan(pm.getLength() * kc)
                tip = (pos.x(), pos.y())
    if tip is None:
        tip = (360, 240)
    pencil(c, *tip)


def gfx_stroke(c, path, color, width, p):
    from engine.gfx import stroke_path
    stroke_path(c, path, color, width, 1.0, p)


# ---------------------------------------------------------------- 第 13 镜：照片围绕主角排成一圈

RING = [(-180, 0), (-148, 0), (-116, 0), (-90, 0), (-64, 0), (-32, 0), (0, 0), (150, 1), (30, 1)]
RING_SC = [sc_ball, sc_praise, sc_cake, sc_lost, sc_sea, sc_left, sc_rain, sc_first, sc_praise]


def photo_ring(c, g, el_t, d):
    cx, cy, rx, ry = 540, 820, 362, 372
    for i, (ang, low) in enumerate(RING):
        a = math.radians(ang)
        tx, ty = cx + rx * math.cos(a), cy + ry * math.sin(a)
        if low:
            ty = 1060
            tx = 180 if ang > 90 else 900
        k = ease_out(clamp01((g.since(0) - i * 0.07) / 0.55)) if i < 7 else ease_out(clamp01((g.since(1)) / 0.5))
        if g.since(2) >= 0:
            k = 1.0
        x = lerp(540, tx, k)
        y = lerp(790, ty, k) + 5 * math.sin(g.t * 1.7 + i)
        glow = clamp01(1 - g.since(6) / 0.5) if g.since(6) >= 0 else 0
        if glow > 0:
            K.spotlight(c, x, y, 150, K.GOLD, 0.5 * glow)
        K.memory(c, x, y, 186, 152, RING_SC[i], clamp01(k * 3), (i % 3 - 1) * 6, lerp(0.3, 1, k), "")


# ---------------------------------------------------------------- 本期

def build() -> Episode:
    shots = [
        # 1
        Shot(3, "闭上眼想一想：|你最早记得的一件事。", "情境演绎", [
            Fig(360, GROUND, 380, at=0, mood="calm", hair="short", blink=False,
                moves=[(2, dict(pose="think", blink=True, sfx="rim", note="主角闭上眼，托腮回想")),
                       (8, dict(mood="smile"))]),
            Custom(thought_dots, at=2, enter="none"),
            Custom(float_photo, at=4, enter="none", sfx="wood_low", note="最早的记忆照片从头顶飘出",
                   x0=520, y0=620, x1=740, y1=500, w=380, h=300, rot=4, ph=0.0, fly=0.8, scene=sc_first,
                   label="最早的记忆"),
            Custom(float_photo, at=8, enter="none", sfx="shaker", note="更多模糊的回忆片段飘出",
                   x0=400, y0=700, x1=230, y1=470, w=220, h=180, rot=-7, ph=1.0, fly=0.7, scene=sc_cake, a=0.75),
            Custom(float_photo, at=9, enter="none",
                   x0=430, y0=700, x1=860, y1=830, w=220, h=180, rot=6, ph=2.0, fly=0.7, scene=sc_sea, a=0.75),
        ], draw=ground, note="主角闭眼托腮回想，最早的记忆照片从头顶飘出，随后更多模糊的片段浮起"),
        # 2
        Shot(3, "被夸奖？迷路？|还是被大人落下？", "情境演绎", [
            Custom(photo(sc_praise, 380, 300, "被夸奖"), x=290, y=560, rot=-5, at=2, enter="pop", sfx="wood_high",
                   note="回忆照片 1：被夸奖"),
            Custom(photo(sc_lost, 380, 300, "迷路"), x=780, y=650, rot=4, at=4, enter="pop", sfx="wood_low",
                   note="回忆照片 2：迷路"),
            Custom(photo(sc_left, 380, 300, "被落下"), x=420, y=990, rot=-2, at=6, enter="pop", sfx="rim",
                   note="回忆照片 3：被大人落下"),
        ], note="三张回忆照片按拍弹出：被夸奖、迷路、被大人落下"),
        # 3
        Shot(2, "为什么偏偏|记住了这一件？", "情境演绎", [
            Custom(photo(sc_praise, 380, 300, "被夸奖"), x=290, y=560, rot=-5, at=0, enter="none", out=2,
                   moves=[(2, dict(x=200, y=520))]),
            Custom(photo(sc_left, 380, 300, "被落下"), x=420, y=990, rot=-2, at=0, enter="none", out=2,
                   moves=[(2, dict(x=330, y=1060))]),
            Custom(photo(sc_lost, 380, 300, "迷路"), x=780, y=650, rot=4, at=0, enter="none", z=1.0,
                   moves=[(2, dict(x=540, y=720, rot=0, z=1.5, sfx="wood_low", note="“迷路”照片移到中央放大"))]),
            Icon("question", 870, 430, 110, color=ACC, at=6, enter="pop", sfx="wood_high", note="问号弹出"),
        ], draw=spotlight_bg, cut=True, text_beat=0, hits=[(4, "frame", 0.8, "聚光灯打在“迷路”照片上")],
            note="其余两张照片淡出，“迷路”照片移到中央放大，聚光灯打亮，旁边弹出问号"),
        # 4（drop）
        Shot(3, "“没有偶然的记忆。”", "阿德勒原著", [
            Big("早期记忆", 540, 520, 160, at=0, sfx="kick", sub="early recollections", note="概念落版（音乐 drop）"),
            Custom(photo_fan, x=315, y=930, at=2, enter="pop", note="一叠回忆照片展开"),
            Custom(dice, x=665, y=975, at=4, enter="slide_r", sfx="wood_low", note="骰子（偶然）滚进来"),
            Icon("cross", 745, 895, 120, color=K.RED, at=6, enter="slam", dur=0.22, sfx="rim",
                 note="骰子被打叉：没有偶然"),
            Icon("book", 895, 1080, 160, color=K.HERO, at=8, enter="pop", sfx="shaker", note="出处：阿德勒原著"),
            Txt("阿德勒《自卑与超越》第4章，1931", 540, 1235, 28, at=8, font="sans_medium", color=K.INK2),
        ], note="drop 处“早期记忆”砸下；回忆照片展开，代表偶然的骰子滚进来被打叉"),
        # 5
        Shot(3, "我们记住的，|是和当下的自己有关的事。", "阿德勒原著 · 大意", [
            Custom(magnet_scene, at=0, enter="none", note="磁铁把有关的照片吸进相框"),
            Label("现在的我", FRAME_X, FRAME_Y + FRAME_H / 2, 34, at=8, enter="pop", fill=ACC, sfx="wood_high",
                  note="相框底部亮出“现在的我”，主角指向相框"),
            Fig(185, GROUND, 300, at=7, mood="calm", hair="short",
                moves=[(8, dict(pose="point", mood="smile"))]),
        ], draw=ground, hits=[(2, "wood_low", 0.9, "磁铁落在相框上方"), (4, "tom", 0.85, "有关的三张照片被吸进相框"),
                 (6, "shaker", 0.8, "其余照片飘走")],
            note="磁铁落下，带橙框的三张照片被吸进相框，其他照片飘走淡出；相框亮起“现在的我”"),
        # 6
        Shot(3, "背后，是一个人的|“生活风格”。", "阿德勒原著", [
            Custom(photo_row, at=0, enter="none"),
            Custom(big_glasses, x=540, y=520, at=2, enter="drop", dur=0.4, sfx="tom", note="一副眼镜落版"),
            Label("生活风格 · style of life", 540, 700, 40, at=4, enter="slam", dur=0.22, fill=ACC, sfx="rim",
                  note="“生活风格”标签砸下"),
            Custom(link_lines, at=6, enter="none", sfx="wood_high", note="回忆照片与眼镜连上虚线"),
        ], note="三张回忆照片在下方，一副眼镜落版，标签“生活风格”砸下，照片与眼镜之间连起虚线"),
        # 7
        Shot(3, "看自己、看他人、看世界的|一副固定眼镜。", "阿德勒原著 · 大意", [
            Icon("mirror", 185, 760, 190, color=K.shade(ACC, 0.1), accent=K.HERO, at=0, enter="pop"),
            Icon("friends", 895, 790, 190, color=K.OTHER3, at=0.25, enter="pop"),
            Icon("sun", 540, 440, 170, color=K.GOLD, at=0.5, enter="pop", p=lambda g, t: t * 0.4),
            Custom(hero_specs, x=540, y=GROUND, at=0, enter="rise", sfx=None, note="主角戴上眼镜"),
            Label("自己", 185, 920, 34, at=5, fill=K.INK2, sfx="wood_high", note="标签：自己"),
            Label("他人", 895, 920, 34, at=6, fill=K.INK2),
            Label("世界", 540, 570, 34, at=7, fill=K.INK2),
        ], draw=tint_open("none", "amber", 4, 0.7, base=ground, wash_to=(K.GOLD, 0.16)), over=tint_close(wash_ring),
            hits=[(2, "rim", 1.0, "眼镜落在主角脸上"), (4, "frame", 0.8, "世界被染成同一种色调"),
                  (8, "wood_low", 0.8, "眼镜上了锁：固定的看法")],
            note="眼镜飞来戴在主角脸上，色调从眼镜扩散，镜子、他人、太阳都被染成同一种琥珀色；眼镜旁出现一把锁"),
        # 8（研究）
        Shot(4, "近四成人说记得两岁前，|研究者认为多半是想象。", "研究证据", [
            Custom(research_scene, at=0, enter="none"),
            Label("想象", PZ_X + 120, PZ_Y - 110, 36, at=10, enter="slam", dur=0.22, fill=K.RED, rot=-8,
                  sfx="rim", note="拼起的回忆盖上“想象”"),
            Label("平均约3.2岁", AX0 + 3.2 * AX_STEP + 120, AX_Y - 150, 30, at=12, fill=ACC),
            Txt("Akhtar 等，2018，6641人；最早记忆平均约3.2岁", 540, 1235, 28, at=1, font="sans_medium",
                color=K.INK2),
        ], research=True,
            hits=[(4, "wood_high", 0.8, "十人中四人亮起：说记得两岁前"), (8, "wood_low", 0.9, "雾里的碎片拼成一张回忆"),
                  (12, "tom", 0.8, "图钉落在 3.2 岁")],
            note="年龄轴 0–6 岁，3 岁前笼着雾；十个人里四个亮起，他们的回忆片飞进雾里，像拼图一样被拼起，盖上“想象”；"
                 "图钉落在平均 3.2 岁"),
        # 9
        Shot(3, "所以它不是“诊断书”，|更像一面镜子。", "常见误解", [
            Custom(diagnosis, x=280, y=560, at=0, enter="pop", rot=-4),
            Custom(mirror, x=MIR_X, y=MIR_Y, at=5, enter="grow", sfx="wood_low", note="落地镜出现",
                   pose="stand", mood="calm",
                   moves=[(8, dict(pose="wave", mood="happy"))]),
            Fig(250, GROUND, 340, at=0, enter="none", pose="stand", mood="calm", hair="short",
                moves=[(6, dict(x=470, dur=0.9)),
                       (8, dict(pose="wave", mood="happy", sfx="bongo_high", note="主角对镜子挥手，镜中人也挥手"))]),
        ], hits=[(3, "rim", 0.9, "“诊断书”被划掉")],
            note="“诊断书”被红叉划掉；落地镜升起，主角走到镜前，镜中映出自己并一起挥手"),
        # 10
        Shot(3, "同一段回忆，|换副眼镜，意义就不同。", "机制示意", [
            Custom(photo(sc_lost, 400, 310, "迷路"), x=540, y=640, at=0, enter="pop", out=2),
            Custom(lens_photo("gray", LENS_GRAY, 4, 0), x=290, y=680, at=2, enter="fade", dur=0.3, rot=-3,
                   sfx="shaker", note="照片一分为二"),
            Custom(lens_photo("warm", LENS_WARM, 6, 0), x=790, y=680, at=2, enter="fade", dur=0.3, rot=3),
            Card("我总被落下", 290, 1010, 46, at=5, rot=-2, color=K.INK2, fill="#ECEAE6"),
            Card("我学会了|自己找路", 790, 1045, 46, at=8, rot=2, accent=ACC, sfx="bongo_high",
                 note="暖镜片下的解读"),
        ], hits=[(4, "rim", 0.85, "灰镜片落下，照片变灰"), (6, "wood_high", 0.9, "暖镜片落下，照片变暖")],
            note="同一张“迷路”照片一分为二：灰镜片下变灰，写着“我总被落下”；暖镜片下变暖，写着“我学会了自己找路”"),
        # 11
        Shot(4, "生活风格约五岁前后成形，|但不是不能改变。", "阿德勒原著 · 大意", [
            Icon("sun", 870, 470, 190, color=K.GOLD, at=0, enter="pop", p=lambda g, t: t * 0.3),
            Icon("sprout", 160, 1045, 170, at=0, enter="pop",
                 p=lambda g, t: 0.25 + 0.75 * ease_out(clamp01(g.since(10) / 0.8))),
            Fig(820, GROUND, 330, at=0, enter="none", color=K.OTHER3, face=-1, hair="bun", mood="calm",
                moves=[(8, dict(pose="wave", mood="happy"))]),
            Custom(hero_swap, x=440, y=GROUND, at=0, enter="none", s=200, mood="flat",
                   moves=[(2, dict(s=380, dur=0.9)),
                          (4, dict(pose="think", mood="surprised", sfx="rim", note="主角摘下灰色旧眼镜")),
                          (7, dict(pose="stand", mood="calm")),
                          (8, dict(mood="happy", note="新眼镜落在脸上")),
                          (12, dict(pose="cheer", sfx="clap", note="主角张开双臂"))]),
        ], draw=tint_open("gray", "warm", 8, 0.7, base=ground, wash_from=(K.INK3, 0.12), wash_to=(K.GOLD, 0.12)), over=tint_close(),
            hits=[(8, "tom", 0.9, "暖色新眼镜落下，世界变暖"), (10, "wood_high", 0.8, "小苗长高")],
            note="小孩戴着灰眼镜长成大人，世界是灰的；第 4 拍摘下旧眼镜，第 8 拍戴上暖色新眼镜，世界变暖，小苗长高"),
        # 12
        Shot(4, "写下你最早的记忆，|问：它在提醒我什么？", "小练习", [
            Custom(notebook, x=NB_X, y=NB_Y, at=0, enter="rise"),
        ], hits=[(2, "shaker", 0.8, "铅笔开始写"), (6, "wood_low", 0.7, "写下第三行"),
                 (10, "wood_high", 0.9, "写出问句"), (12, "rim", 0.9, "问句被圈出")],
            note="笔记本左页贴着那张回忆照片，右页铅笔按拍写出几行字，最后写下“它在提醒我什么？”并圈起来"),
        # 13
        Shot(2, "你记得什么，|也在说明你是谁。", "阿德勒的视角", [
            Custom(photo_ring, at=0, enter="none", sfx=None),
            Fig(540, GROUND, 340, at=0, enter="rise", mood="smile", hair="short",
                moves=[(4, dict(pose="wave", mood="happy", sfx="bongo_high", note="主角挥手"))]),
        ], draw=ground, hits=[(2, "wood_low", 0.85, "照片围绕主角排成一圈"), (6, "shaker", 0.7, "照片一起发光")],
            note="回忆照片从主角身边飞出，围成一圈；主角挥手，照片一起发光"),
        end_shot(["Adler, A. (1931). What Life Should Mean to You, ch.4.（中译《自卑与超越》）",
                  "Akhtar, S. et al. (2018). Fictional First Memories. Psychological Science, 29(10).",
                  "Bauer, P. J. & Larkina, M. (2014). Memory, 22(8), 907–924."],
                 "09 出生顺序：老大懂事、老幺任性，是真的吗？"),
    ]
    return Episode(8, "memories", "早期记忆", "你最早的记忆，藏着什么？", ACC, shots,
                   refs=["Adler, A. (1931). What Life Should Mean to You, ch.4.（中译《自卑与超越》）",
                         "Akhtar, S. et al. (2018). Fictional First Memories. Psychological Science, 29(10).",
                         "Bauer, P. J. & Larkina, M. (2014). Memory, 22(8), 907–924."],
                   publish_title="你最早的记忆，藏着什么？｜阿德勒心理学08 早期记忆",
                   hashtags="#阿德勒 #心理学 #记忆 #自我认识 #被讨厌的勇气",
                   cover_title="你最早的记忆，|藏着【什么】？", cover_sub="阿德勒：没有偶然的记忆",
                   cover_shot=1, cover_t=5.5,
                   notes=[
                       "“没有偶然的记忆”据 What Life Should Mean to You 第 4 章 Early Memories：“There are no ‘chance "
                       "memories’: out of the incalculable number of impressions which meet an individual, he chooses to "
                       "remember only those which he feels… to have a bearing on his situation.”",
                       "生活风格约在五岁前后成形为阿德勒原意（不同著作中给出 3–5 岁不等）；《被讨厌的勇气》中的“10 岁前后”不采用。",
                       "第 8 镜：Akhtar, Justice, Morrison & Conway (2018), Psychological Science 29(10):1612–1619, "
                       "doi:10.1177/0956797618778831；6,641 人中 2,487 人报告 2 岁及以前的记忆（约 37%，摘要称 nearly 40%），"
                       "最早记忆平均编码年龄 3.2 岁。",
                       "早期记忆在阿德勒学派中用作理解当下生活风格的线索，不是诊断工具；记忆会被重构（Bartlett 1932）。",
                   ]).build()
