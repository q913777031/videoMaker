"""09 出生顺序：老大懂事、老幺任性，是真的吗？"""

import math

import numpy as np
import skia

from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, ease_out_back, lerp, stroke_path

from . import kit as K
from .core import Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

ACC = "#3E86B5"
GROUND = 1130
C1, C2, C3 = K.OTHER3, K.OTHER2, "#9C8FB0"        # 老大 / 老二 / 老幺
KIDS = [(230, 360, C1, "short"), (540, 300, C2, "bun"), (830, 235, C3, None)]


def ground(g):
    K.ground(g.c, GROUND)


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
    return dict(head=(hx, hy), r=0.16 * u, tilt=d["head"] * 0.35 * face, hand=hand, chest=(sh_x * 0.6, sh_y + 0.14 * u))


# ---------------------------------------------------------------- 标签贴纸

def sticker(text, color, peel=None, size=44):
    """贴在孩子胸前的标签纸；peel 为揭掉的拍（揭起、翻转、飞走）。"""
    def fn(c, g, el_t, d):
        a, dx, dy, rot = 1.0, 0.0, 0.0, 0.0
        if peel is not None and g.since(peel) > 0:
            k = clamp01(g.since(peel) / 0.7)
            rot = -55 * ease_out(min(1, k * 2.2))
            dx, dy = 230 * ease_in(k), -260 * ease_in(k) - 30 * math.sin(math.pi * min(1, k * 2))
            a = 1 - clamp01((k - 0.45) / 0.55)
        if a <= 0:
            return
        w = K.text_w(text, size, "serif") + 40
        with K.at(c, dx - w / 2, dy - 30, rot):
            with K.at(c, w / 2, 30):
                with K.paper(c, a, 0.7):
                    K.rr(c, 0, 0, w, size * 1.6, 8, color)
                    K.rr(c, 0, -size * 0.8, 58, 18, 3, "#EFE6D2", 0.9)
                    K.text(c, text, 0, 0, size, "serif", K.INK)
    return fn


def kid_chest(i, p="stand"):
    x, s, _, _ = KIDS[i]
    geo = fig_geom(s, p)
    return x + geo["chest"][0], GROUND + geo["chest"][1]


def kids(at=0, enter="rise", moves=None, moods=("calm", "calm", "calm"), **kw):
    out = []
    for i, (x, s, col, hair) in enumerate(KIDS):
        out.append(Fig(x, GROUND, s, at=at + i * 0.25 if enter != "none" else at, enter=enter, color=col, hair=hair,
                       mood=moods[i], moves=(moves or {}).get(i, []), **kw))
    return out


# ---------------------------------------------------------------- 第 3 镜：书本

def open_book(c, g, el_t, d):
    w, h = 760, 470
    k = ease_out(clamp01(el_t / 0.5))
    with K.paper(c, 1, 0.9):
        K.rr(c, 0, 8, w + 30, h + 26, 20, K.shade(ACC, 0.2))
        K.rr(c, -w / 4 - 3, 0, w / 2 - 6, h, 10, K.PAPER)
        with K.at(c, 3, 0, 0, 1, 1):
            c.save()
            c.scale(max(0.02, k), 1)
            K.rr(c, w / 4, 0, w / 2 - 6, h, 10, K.PAPER)
            c.restore()
    K.seg(c, 0, -h / 2 + 10, 0, h / 2 - 10, K.LINE, 4)
    # 左页：标题“家庭的影响”（第 2 拍）
    kt = clamp01(g.since(2) / 0.5)
    if kt > 0:
        tw = K.text_w("家庭的影响", 50, "serif_black")
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(-w / 4 - tw / 2 - 6, -h / 2 + 40, (tw + 12) * kt, 90))
        K.text(c, "家庭的影响", -w / 4, -h / 2 + 90, 50, "serif_black", ACC)
        c.restore()
        K.text(c, "Family Influences", -w / 4, -h / 2 + 150, 28, "sans_medium", K.INK2, kt)
    for j in range(5):
        a = clamp01((g.since(2.5) - j * 0.12) / 0.3)
        K.seg(c, -w / 2 + 60, -h / 2 + 210 + j * 44, -60 - (j % 3) * 40, -h / 2 + 210 + j * 44, K.LINE, 8, a)
    # 右页：家庭树（第 4 拍）
    kd = clamp01(g.since(4) / 0.5)
    if kd > 0 and k >= 1:
        px, py = w / 4, -h / 2 + 120
        K.dot(c, px - 30, py, 24, K.INK2, kd)
        K.dot(c, px + 30, py, 24, K.INK2, kd)
        for j, (cx, col) in enumerate(((px - 110, C1), (px, C2), (px + 110, C3))):
            p = clamp01((g.since(4) - j * 0.12) / 0.4)
            K.seg(c, px, py + 30, px, py + 80, K.INK3, 5, 1, p)
            K.seg(c, px, py + 80, cx, py + 80, K.INK3, 5, 1, p)
            K.seg(c, cx, py + 80, cx, py + 130, K.INK3, 5, 1, p)
            if p > 0.6:
                K.dot(c, cx, py + 170, 34 * ease_out_back(clamp01((p - 0.6) / 0.4), 2), col)
                K.text(c, str(j + 1), cx, py + 170, 36, "black", K.PAPER, clamp01((p - 0.6) / 0.4))


# ---------------------------------------------------------------- 第 4 镜：家里的位置

def house(c, g, el_t, d):
    k = ease_out(clamp01(el_t / 0.5))
    w, h = 760, 300
    with K.paper(c, k, 0.8):
        K.poly(c, [(-w / 2 - 40, -h), (0, -h - 150 * k), (w / 2 + 40, -h)], K.shade(ACC, 0.25))
        K.rr(c, 0, -h / 2, w, h, 8, K.tint(ACC, 0.78))
    for x in (-w / 6, w / 6):
        K.seg(c, x, -h + 20, x, -10, K.tint(ACC, 0.55), 6, k)


def badge(c, g, el_t, d):
    """头顶的排行数字，第 8 拍翻成“处境”图标。"""
    k = clamp01(g.since(8) / 0.4)
    if k < 0.5:
        sx = math.cos(k * math.pi)
        with K.at(c, 0, 0, 0, 1, 1):
            c.save()
            c.scale(max(0.02, sx), 1)
            with K.paper(c, 1, 0.6):
                K.dot(c, 0, 0, 40, ACC)
            K.text(c, d["num"], 0, 0, 46, "black", K.PAPER)
            c.restore()
    else:
        sx = -math.cos(k * math.pi)
        c.save()
        c.scale(max(0.02, sx), 1)
        K.icon(c, d["icon"], 0, 0, 96, d["color"], 1, 0.6, 0, 1, 1.0, K.GOLD)
        c.restore()


# ---------------------------------------------------------------- 第 5 镜：被“废黜”的国王

THRONE_X = 320
THRONE_U = 300


def throne(c, g, el_t, d):
    u = THRONE_U
    with K.paper(c, 1, 0.8):
        K.rr(c, -0.2 * u, -0.56 * u, 0.12 * u, 0.62 * u, 14, K.GOLD)
        K.star(c, -0.2 * u, -0.9 * u, 18, K.GOLD)
        K.rr(c, 0, -0.135 * u, 0.5 * u, 0.27 * u, 10, K.shade(K.GOLD, 0.2))
        K.rr(c, 0, -0.27 * u, 0.52 * u, 0.06 * u, 8, K.RED)


def crown(c, g, el_t, d):
    """王冠：戴在老大头上，第 6 拍滑落、翻滚着掉到地上。"""
    geo = fig_geom(THRONE_U, "sit")
    hx, hy = THRONE_X + geo["head"][0], GROUND + geo["head"][1]
    x0, y0 = hx - 4, hy - geo["r"] * 1.12
    k = clamp01(g.since(6) / 0.6)
    if k <= 0:
        x, y, rot = x0, y0, -6
    else:
        x = lerp(x0, 520, k)
        y = lerp(y0, GROUND - 30, ease_in(k)) - 80 * math.sin(math.pi * min(1, k * 1.3))
        rot = -6 + 140 * ease_out(k)
        if k >= 1:
            y += -16 * math.sin(clamp01((g.since(6) - 0.6) / 0.25) * math.pi)
    K.icon(c, "crown", x, y, 100, K.GOLD, 1, 0.6, rot, 1, 1.0, K.RED)


def crib(c, g, el_t, d):
    w, h = 330, 200
    with K.paper(c, 1, 0.8):
        K.rr(c, 0, -60, w, 70, 10, K.tint(ACC, 0.6))
        # 婴儿
        K.dot(c, -60, -115, 34, K.SKIN)
        K.rr(c, 30, -100, 170, 46, 20, K.tint(K.RED, 0.55))
        hand = clamp01(g.since(8) / 0.3)
        if hand > 0:
            K.seg(c, -20, -110, -10 + 16 * math.sin(g.t * 9) * hand, -110 - 70 * ease_out_back(hand, 2), K.SKIN, 16)
        for i in range(9):
            x = -w / 2 + 14 + i * (w - 28) / 8
            K.seg(c, x, -h, x, -30, K.shade(K.GOLD, 0.15), 9)
        K.rr(c, 0, -h, w + 20, 18, 9, K.shade(K.GOLD, 0.25))
        K.rr(c, 0, -30, w + 20, 18, 9, K.shade(K.GOLD, 0.25))
        for sx in (-1, 1):
            K.rr(c, sx * (w / 2 + 2), -h / 2 - 10, 18, h + 30, 9, K.shade(K.GOLD, 0.3))
    if hand > 0:
        K.heart(c, -10, -230 - 30 * clamp01(g.since(8) / 1.2), 46, K.RED, 1 - clamp01((g.since(8) - 0.8) / 0.6))


def spot(g):
    c = g.c
    k = g.p(4, 0.45, ease_in_out)
    x = lerp(THRONE_X, 770, k)
    K.spotlight(c, x, 980, 340, K.GOLD, 0.45)


# ---------------------------------------------------------------- 第 6 镜：赛跑

def track(g):
    c = g.c
    K.road(c, 80, GROUND + 34, 1000, GROUND + 34, K.LINE, 64, 1, 1)
    for k in range(7):
        K.rr(c, 905, GROUND + 8 + k * 9, 14, 9, 0, K.INK if k % 2 == 0 else K.PAPER)


def speed_lines(c, g, el_t, d):
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(75, 330, 1005, 1260))
    for runner in d["runners"]:
        x0, x1, y = runner
        k = ease_in_out(clamp01(g.t / 4.2))
        x = lerp(x0, x1, k)
        sp = math.sin(math.pi * k)
        for j in range(3):
            yy = y - 60 - j * 50
            K.seg(c, x - 110 - j * 20, yy, x - 110 - j * 20 - 90 * sp, yy, K.INK3, 5, 0.6 * sp)
    c.restore()


# ---------------------------------------------------------------- 第 8 镜：柱状图（示意）

TRAITS = ["外向", "情绪稳定", "宜人", "尽责", "想象"]
HTS = [[0.62, 0.615, 0.62], [0.6, 0.605, 0.6], [0.63, 0.63, 0.625], [0.61, 0.605, 0.61], [0.62, 0.62, 0.615]]
CH_X0, CH_X1, CH_Y, CH_H = 120, 960, 1040, 610


def chart(c, g, el_t, d):
    gw = (CH_X1 - CH_X0) / 5
    K.seg(c, CH_X0 - 10, CH_Y, CH_X1 + 10, CH_Y, K.INK2, 5, 1, g.p(0, 0.5))
    with K.paper(c, 1, 0.5):
        for i in range(5):
            for j in range(3):
                q = ease_out(clamp01((g.t - g.b(2 + i)) / 0.45 - j * 0.15)) if g.since(2 + i) > 0 else 0
                if q <= 0:
                    continue
                bh = CH_H * HTS[i][j] * q
                bx = CH_X0 + gw * (i + 0.5) + (j - 1) * 44
                K.rr(c, bx, CH_Y - bh / 2, 38, max(bh, 0.1), 8, (C1, C2, C3)[j])
    for i, t in enumerate(TRAITS):
        a = clamp01(g.since(2 + i) / 0.3)
        K.text(c, t, CH_X0 + gw * (i + 0.5), CH_Y + 42, 30, "sans_medium", K.INK2, a)
    # 图例
    for j, name in enumerate(("老大", "老二", "老三")):
        a = g.p(0.5 + j * 0.25, 0.3)
        x = 300 + j * 190
        K.rr(c, x - 40, 440, 34, 34, 6, (C1, C2, C3)[j], a)
        K.text(c, name, x, 440, 32, "sans_medium", K.INK, a, "left")
    # 第 8 拍：一条水平虚线扫过所有柱顶
    p = ease_out(clamp01(g.since(8) / 0.6))
    if p > 0:
        y = CH_Y - CH_H * 0.632
        path = skia.Path()
        path.moveTo(CH_X0 - 10, y)
        path.lineTo(CH_X1 + 10, y)
        stroke_path(c, path, ACC, 6, 1, p, dash=(18, 12, 0))


# ---------------------------------------------------------------- 第 9 镜：0.02 与几乎水平的线

def odometer(c, g, el_t, d):
    """0.99 滚动到 0.02（第 4 拍停住）。"""
    p = clamp01((g.t - g.b(1)) / max(1e-6, g.b(4) - g.b(1)))
    v = lerp(99, 2, ease_out(p) if p < 1 else 1)
    size = 190
    tw0 = K.text_w("0.", size, "serif_black")
    dw = K.text_w("0", size, "serif_black")
    x0 = -(tw0 + 2 * dw) / 2
    K.text(c, "0.", x0, 0, size, "serif_black", ACC, 1, "left", shadow=(6, 10, 10, K.SHADOW))
    ones = v % 10
    tens = math.floor(v / 10) + max(0.0, (v % 10) - 9)
    for i, val in enumerate((tens, ones)):
        cx = x0 + tw0 + dw * (i + 0.5)
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(cx - dw / 2 - 4, -size * 0.43, dw + 24, size * 0.86 + 22))
        base = math.floor(val) % 10
        frac = val - math.floor(val)
        for k_, off in ((base, -frac), ((base + 1) % 10, 1 - frac)):
            K.text(c, str(k_), cx, off * size * 0.95, size, "serif_black", ACC, 1, "center",
                   shadow=(6, 10, 10, K.SHADOW))
        c.restore()
    K.burst(c, 0, 0, g.since(4), K.GOLD, 160, 330, 12, 8)


SC_X0, SC_X1, SC_Y0, SC_Y1 = 200, 900, 800, 1110


def scatter(c, g, el_t, d):
    a = g.p(0, 0.4)
    K.seg(c, SC_X0, SC_Y1, SC_X1, SC_Y1, K.INK2, 5, a)
    K.seg(c, SC_X0, SC_Y1, SC_X0, SC_Y0 - 20, K.INK2, 5, a)
    K.text(c, "排行", SC_X1 - 10, SC_Y1 + 40, 28, "sans_medium", K.INK2, a, "right")
    K.text(c, "人格", SC_X0 - 22, SC_Y0 - 10, 28, "sans_medium", K.INK2, a, "right")
    rng = np.random.default_rng(9)
    cols = [SC_X0 + 110 + i * 170 for i in range(4)]
    for i, x in enumerate(cols):
        K.text(c, str(i + 1) if i < 3 else "4+", x, SC_Y1 + 40, 28, "sans_medium", K.INK2, a)
        for j in range(13):
            jx = x + (rng.random() - 0.5) * 70
            jy = (SC_Y0 + SC_Y1) / 2 + rng.normal(0, 1) * 62
            k = clamp01((g.since(6) - i * 0.12 - j * 0.015) / 0.25)
            if k > 0:
                K.dot(c, jx, jy, 9 * ease_out_back(k, 2), (C1, C2, C3, K.INK3)[i], 0.85)
    p = ease_out(clamp01(g.since(8) / 0.6))
    if p > 0:
        ym = (SC_Y0 + SC_Y1) / 2
        K.seg(c, SC_X0 + 30, ym + 6, SC_X0 + 30 + (SC_X1 - SC_X0 - 60) * p, ym + 6 - 12 * p, ACC, 9)


# ---------------------------------------------------------------- 第 10 镜：放大镜

BARS = [(420, 470, C1, "老大"), (650, 462, C2, "老二")]
BAR_W = 150


def two_bars(c, scale_ctx=None):
    for x, h, col, name in BARS:
        K.rr(c, x, GROUND - h / 2, BAR_W, h, 12, col)
        K.text(c, name, x, GROUND - 50, 36, "serif", K.PAPER)


def bars_el(c, g, el_t, d):
    with K.paper(c, 1, 0.6):
        two_bars(c)


def magnifier(c, g, el_t, d):
    """放大镜从右下移到两根柱子顶部，镜片里是放大 2.4 倍的柱顶。"""
    cx, cy, r = d["x"], d["y"], 135
    z = 2.4
    with K.paper(c, 1, 0.9):
        K.seg(c, r * 0.7, r * 0.7, r * 1.55, r * 1.55, K.DARK, 34)
        c.drawCircle(0, 0, r + 16, K.paint(K.DARK))
    c.drawCircle(0, 0, r, K.paint(K.PAPER))
    c.save()
    path = skia.Path()
    path.addCircle(0, 0, r)
    c.clipPath(path, doAntiAlias=True)
    c.drawPaint(K.paint("#F6F0E6"))
    c.scale(z, z)
    c.translate(-cx, -cy)
    two_bars(c)
    c.restore()
    # 镜内的小小差距（第 4 拍）
    k = clamp01(g.since(4) / 0.35)
    if k > 0:
        y1 = ((GROUND - 470) - cy) * z
        y2 = ((GROUND - 462) - cy) * z
        K.seg(c, -20, y1, 125, y1, K.RED, 4, k)
        K.seg(c, -20, y2, 125, y2, K.RED, 4, k)
        K.text(c, "≈", 92, (y1 + y2) / 2 - 34, 46, "black", K.RED, k)
    K.ring(c, 0, 0, r, "#FFFFFF", 6, 0.35)


# ---------------------------------------------------------------- 第 13 镜：剧本合上

def script_book(c, g, el_t, d):
    w, h = 280, 340
    k = clamp01(g.since(2) / 0.45)
    with K.paper(c, 1, 0.9):
        if k < 1:
            # 打开状态：左页 + 右页（右页翻过来盖住左页）
            K.rr(c, -w / 2, 0, w, h, 10, K.PAPER)
            K.text(c, "剧本", -w / 2, -h / 2 + 70, 52, "serif_black", K.INK)
            for j in range(5):
                K.seg(c, -w + 50, -h / 2 + 140 + j * 40, -50, -h / 2 + 140 + j * 40, K.LINE, 8)
            sx = math.cos(k * math.pi)
            c.save()
            c.scale(sx if abs(sx) > 0.02 else 0.02, 1)
            K.rr(c, w / 2, 0, w, h, 10, K.PAPER if sx > 0 else ACC)
            if sx > 0:
                for j in range(6):
                    K.seg(c, 50, -h / 2 + 70 + j * 40, w - 50, -h / 2 + 70 + j * 40, K.LINE, 8)
            c.restore()
        else:
            K.rr(c, -w / 2, 0, w, h, 12, ACC)
            K.rr(c, -w + 24, 0, 16, h - 20, 6, K.shade(ACC, 0.25))
            K.text(c, "剧本", -w / 2, -40, 60, "serif_black", K.PAPER)
            K.seg(c, -w / 2 - 70, 40, -w / 2 + 70, 40, K.PAPER, 6, 0.8)


def start_line(c, g, el_t, d):
    p = ease_out(clamp01(el_t / 0.4))
    path = skia.Path()
    path.moveTo(0, GROUND - 6)
    path.lineTo(0, GROUND + 52)
    stroke_path(c, path, K.INK, 8, 1, p, dash=(14, 10, 0))


# ---------------------------------------------------------------- 本期

def build() -> Episode:
    sticks = [("懂事", K.tint(C1, 0.55)), ("夹心", K.tint(C2, 0.55)), ("任性", K.tint(C3, 0.55))]
    s12_pose = dict(lean=0, head=-8, la1=118, la2=-42, ra1=-8, ra2=8, ll1=3, ll2=0, rl1=-3, rl2=0)
    s12_hand = fig_geom(360, s12_pose)["hand"]
    shots = [
        # 1
        Shot(3, "“老大就是懂事，|老幺就是被宠坏。”", "情境演绎", [
            *kids(moves={0: [(2, dict(mood="flat"))], 1: [(4, dict(mood="worried", look=0.6))],
                         2: [(6, dict(mood="angry", pose="fist"))]}),
            Custom(sticker(*sticks[0]), x=kid_chest(0)[0], y=kid_chest(0)[1], at=2, enter="slam", dur=0.2,
                   sfx="wood_high", note="老大身上贴上“懂事”"),
            Custom(sticker(*sticks[1]), x=kid_chest(1)[0], y=kid_chest(1)[1], at=4, enter="slam", dur=0.2,
                   sfx="wood_low", note="老二身上贴上“夹心”"),
            Custom(sticker(*sticks[2]), x=kid_chest(2)[0], y=kid_chest(2)[1], at=6, enter="slam", dur=0.2,
                   sfx="rim", note="老幺身上贴上“任性”"),
        ], draw=ground, note="三个孩子按身高站成一排，标签“懂事”“夹心”“任性”按拍贴上，孩子们的表情随之变化"),
        # 2
        Shot(3, "这种说法，|你是不是也听过？", "情境演绎", [
            Fig(170, GROUND, 330, at=0, color=K.OTHER, hair="long", mood="smile",
                moves=[(2, dict(pose="point")), (6, dict(pose="shrug"))]),
            Fig(912, GROUND, 330, at=0.25, color="#7F8C76", hair="cap", mood="smile", face=-1,
                moves=[(4, dict(pose="point")), (8, dict(pose="shrug", mood="happy"))]),
            Fig(420, GROUND, 250, at=0, enter="none", color=C1, hair="short", mood="flat"),
            Fig(545, GROUND, 210, at=0, enter="none", color=C2, hair="bun", mood="worried"),
            Fig(650, GROUND, 165, at=0, enter="none", color=C3, mood="calm",
                moves=[(8, dict(pose="cover", mood="worried"))]),
            Bubble("老大就是稳重", 320, 545, 42, at=2, tail=(-0.5, 1), sfx="wood_high", note="亲戚议论 1"),
            Bubble("老二最会看脸色", 750, 455, 42, at=4, tail=(0.5, 1), sfx="wood_high", gain=0.8,
                   note="亲戚议论 2"),
            Bubble("小的都被惯坏了", 340, 690, 42, at=6, tail=(-0.5, 1), sfx="bongo_high", note="亲戚议论 3"),
            Bubble("排行看性格", 790, 615, 42, at=8, tail=(0.5, 1), sfx="bongo_low", note="亲戚议论 4"),
        ], draw=ground, note="一家三个孩子站在中间，两边的亲戚指指点点，议论气泡按拍冒出"),
        # 3
        Shot(2, "阿德勒|确实讨论过排行。", "阿德勒原著", [
            Custom(open_book, x=540, y=760, at=0, enter="grow", sfx="wood_low", note="书本打开"),
            Txt("阿德勒《自卑与超越》第6章，1931", 540, 1235, 28, at=4, font="sans_medium", color=K.INK2),
        ], text_beat=0, hits=[(2, "rim", 0.85, "书页上写出“家庭的影响”"), (4, "wood_high", 0.8, "家庭树画出三个孩子")],
            note="一本书打开，左页写着“家庭的影响”，右页画出三个孩子的家庭树"),
        # 4（drop）
        Shot(3, "但他关注的，|是孩子在家里的处境。", "阿德勒原著", [
            Big("出生顺序", 540, 500, 160, at=0, sfx="kick", sub="birth order", note="概念落版（音乐 drop）"),
            Custom(house, x=540, y=GROUND, at=2, enter="fade", sfx="wood_low", note="房子出现"),
            Fig(330, GROUND, 230, at=2.5, color=C1, hair="short", mood="calm"),
            Fig(545, GROUND, 195, at=2.75, color=C2, hair="bun", mood="calm"),
            Fig(750, GROUND, 160, at=3, color=C3, mood="calm"),
            Custom(badge, x=330, y=770, at=4, enter="pop", num="1", icon="crown", color=K.GOLD, sfx="wood_high",
                   note="排行数字 1、2、3 弹出"),
            Custom(badge, x=545, y=805, at=4.25, enter="pop", num="2", icon="flag", color=K.INK),
            Custom(badge, x=750, y=845, at=4.5, enter="pop", num="3", icon="ladder", color=K.INK2),
        ], draw=ground, hits=[(8, "rim", 0.9, "数字翻成各自的处境：王冠、领跑的旗、要爬的梯子")],
            note="drop 处“出生顺序”砸下；房子里三个孩子头顶先出现排行数字，第 8 拍数字翻成各自的处境图标"),
        # 5
        Shot(3, "老大曾是唯一的孩子，|后来像被“废黜”的国王。", "阿德勒原著 · 大意", [
            Custom(throne, x=THRONE_X, y=GROUND, at=0, enter="none",
                   moves=[(6, dict(x=180, rot=-6, dur=0.5))]),
            Fig(THRONE_X, GROUND, THRONE_U, at=0, enter="none", pose="sit", color=C1, hair="short", mood="happy",
                walk=False, moves=[(6, dict(x=180, rot=-6, pose="sit_sad", mood="sad", dur=0.5))]),
            Custom(crown, at=0, enter="none", sfx=None),
            Custom(crib, x=770, y=GROUND, at=4, enter="slide_r", sfx="wood_low", note="婴儿床推进来"),
            Fig(940, GROUND, 330, at=4, color=K.OTHER, hair="long", face=-1, mood="happy",
                moves=[(5, dict(pose=dict(lean=24, head=14, la1=62, la2=22, ra1=46, ra2=30, ll1=3, ll2=0,
                                          rl1=-3, rl2=0)))]),
        ], draw=lambda g: (spot(g), ground(g)),
            hits=[(6, "tom", 0.9, "王冠滑落，王座被推到一边"), (8, "bongo_high", 0.8, "婴儿挥手")],
            note="老大戴着王冠坐在小王座上；婴儿床推进来，聚光灯移过去，王冠滑落，王座被推到一边"),
        # 6
        Shot(3, "老二呢？前面|好像总有人在领跑。", "阿德勒原著 · 大意", [
            Custom(speed_lines, at=0, enter="none", runners=[(430, 790, GROUND), (140, 470, GROUND)]),
            Icon("flag", 942, 1040, 150, accent=ACC, at=0, enter="pop", p=lambda g, t: t * 1.5),
            Fig(430, GROUND, 320, at=0, enter="none", color=C1, hair="short", mood="happy", stride=1.6,
                moves=[(0, dict(x=790, dur=4.2)), (8, dict(pose="cheer", sfx="clap", note="老大先到终点举手"))]),
            Fig(140, GROUND, 275, at=0, enter="none", color=C2, hair="bun", mood="worried", stride=1.7,
                moves=[(0, dict(x=470, dur=4.2)), (8, dict(pose="reach", look=0.5))]),
            Label("老大", 430, 700, 32, at=1, fill=C1, moves=[(0, dict(x=790, dur=4.2))]),
            Label("老二", 140, 760, 32, at=1, fill=C2, moves=[(0, dict(x=470, dur=4.2))]),
        ], draw=track, hits=[(0, "rim", 0.8, "起跑"), (4, "bongo_low", 0.8, "脚步")],
            note="两个孩子赛跑，老大一直跑在前面先到终点，老二在后面伸手追"),
        # 7
        Shot(3, "重要的不是排第几，|而是孩子怎么理解它。", "阿德勒原著 · 大意", [
            *kids(moves={0: [(2, dict(pose="think"))], 1: [(4, dict(pose="fist", mood="smile"))],
                         2: [(6, dict(pose="cheer", mood="happy"))]}),
            Label("1", 230, 1210, 34, at=0.5, fill=K.INK3, out=8),
            Label("2", 540, 1210, 34, at=0.75, fill=K.INK3, out=8),
            Label("3", 830, 1210, 34, at=1, fill=K.INK3, out=8),
            Bubble("我得做榜样", 230, 570, 40, at=2, think=True, sfx="bongo_high", note="老大的理解"),
            Bubble("我要追上去", 540, 650, 40, at=4, think=True, sfx="bongo_low", note="老二的理解"),
            Bubble("我也能行！", 830, 730, 40, at=6, think=True, sfx="wood_high", note="老幺的理解"),
        ], draw=ground, hits=[(8, "shaker", 0.7, "排行数字淡去")],
            note="同一家的三个孩子头顶各自冒出思考气泡：做榜样、追上去、我也能行；脚下的排行数字淡去"),
        # 8（研究）
        Shot(4, "2015年，约两万人的研究：|排行与性格几乎无关。", "研究证据", [
            Custom(chart, at=0, enter="none"),
            Txt("Rohrer 等，PNAS，20,186人（美英德）", 540, 1235, 28, at=1, font="sans_medium", color=K.INK2),
        ], research=True,
            hits=[(2, "wood_low", 0.85, "第 1 组柱子长出"), (4, "wood_low", 0.75, "第 3 组柱子长出"),
                  (6, "wood_high", 0.8, "第 5 组柱子长出"), (8, "rim", 0.9, "一条水平线扫过所有柱顶")],
            note="五组人格特质（外向、情绪稳定、宜人、尽责、想象）的示意柱状图，老大老二老三的柱子几乎一样高"),
        # 9（研究）
        Shot(3, "另一项约37万人的研究：|平均相关只有 0.02。", "研究证据", [
            Txt("平均相关", 540, 420, 34, at=0, font="sans_medium", color=K.INK2),
            Custom(odometer, x=540, y=575, at=0, enter="fade", sfx=None),
            Custom(scatter, at=0, enter="none"),
            Txt("Damian & Roberts，2015，美国高中生", 540, 1235, 28, at=1, font="sans_medium", color=K.INK2),
        ], research=True,
            hits=[(4, "tom", 0.9, "数字停在 0.02"), (6, "shaker", 0.8, "散点按排行落下"),
                  (8, "wood_high", 0.85, "几乎水平的线画出")],
            note="大数字从 0.99 滚动到 0.02；下方按排行分列的散点，中间一条几乎水平的线"),
        # 10（研究）
        Shot(3, "差别小到|日常几乎察觉不到。", "研究证据", [
            Custom(bars_el, at=0, enter="fade"),
            Custom(magnifier, x=230, y=520, at=0, enter="fade",
                   moves=[(2, dict(x=535, y=GROUND - 466, sfx="wood_low", note="放大镜对准两根柱子的顶端"))]),
            Fig(890, GROUND, 320, at=0, color=K.HERO, hair="short", face=-1, mood="calm", pose="think",
                moves=[(4, dict(mood="surprised")),
                       (6, dict(pose="shrug", mood="smile", sfx="bongo_low", note="主角摊手：几乎看不出"))]),
        ], hits=[(4, "rim", 0.85, "镜中标出两根柱顶的微小差距")],
            note="放大镜对准两根几乎一样高的柱子，镜片里也只看出一点点差距；主角摊手"),
        # 11
        Shot(4, "比起排行标签，|更值得看：他怎么回应处境。", "常见误解", [
            Fig(230, GROUND, 330, at=0, enter="none", color=C1, hair="short", mood="flat",
                moves=[(5, dict(pose="wave", mood="happy")), (12, dict(pose="cheer"))]),
            Fig(540, GROUND, 280, at=0, enter="none", color=C2, hair="bun", mood="worried",
                prop=None,
                moves=[(7, dict(pose="give", mood="smile",
                                prop=lambda c, h: K.icon(c, "book", h[0] + 26, h[1] - 18, 80, ACC, 1, 0.3)))]),
            Fig(830, GROUND, 220, at=0, enter="none", color=C3, mood="angry", pose="fist",
                prop=None,
                moves=[(9, dict(pose="give", mood="happy",
                                prop=lambda c, h: K.icon(c, "gift", h[0] + 16, h[1] - 20, 64, K.GOLD, 1, 0.3,
                                                         0, 1, 1, K.RED)))]),
            Custom(sticker(sticks[0][0], sticks[0][1], 4), x=kid_chest(0)[0], y=kid_chest(0)[1], at=0,
                   enter="none"),
            Custom(sticker(sticks[1][0], sticks[1][1], 6), x=kid_chest(1)[0], y=kid_chest(1)[1], at=0,
                   enter="none"),
            Custom(sticker(sticks[2][0], sticks[2][1], 8), x=kid_chest(2, "fist")[0], y=kid_chest(2, "fist")[1],
                   at=0, enter="none"),
        ], draw=ground, hits=[(4, "shaker", 0.8, "揭掉“懂事”"), (6, "wood_high", 0.8, "揭掉“夹心”"),
                              (8, "wood_low", 0.85, "揭掉“任性”"), (12, "clap", 0.85, "三个孩子各自行动")],
            note="孩子们身上的标签按拍揭掉：老大开心挥手，老二捧起书，老幺递出礼物，各做各的回应"),
        # 12
        Shot(4, "想一想：在家里，|你习惯扮演什么角色？", "小练习", [
            Card("懂事的", 770, 520, 48, at=2, enter="slide_r", rot=-4, sfx="wood_high", note="角色卡 1"),
            Card("调皮的", 800, 720, 48, at=3, enter="slide_r", rot=3),
            Card("和事佬", 760, 930, 48, at=4, enter="slide_r", rot=-2, sfx="wood_high", gain=0.8,
                 note="角色卡 3",
                 moves=[(8, dict(x=250 + s12_hand[0] + 72, y=GROUND + s12_hand[1] - 52, rot=6, sfx="tom",
                                 note="主角拿起“和事佬”卡片端详"))]),
            Fig(250, GROUND, 360, at=0, hair="short", mood="calm",
                moves=[(7.5, dict(pose=s12_pose, mood="open")), (12, dict(mood="smile"))]),
            Icon("question", 470, 560, 100, color=ACC, at=12, enter="pop", sfx="bongo_high", note="问号：我是哪一个？"),
        ], draw=ground, note="主角面前飞来几张角色卡“懂事的”“调皮的”“和事佬”，他拿起一张端详"),
        # 13
        Shot(2, "排行是起点，|不是剧本。", "阿德勒的视角", [
            Custom(start_line, x=230, y=0, at=0, enter="none"),
            Label("起点", 230, 1218, 32, at=0, fill=K.INK2),
            Custom(script_book, x=500, y=585, at=0, enter="pop", sfx=None),
            Fig(230, GROUND, 340, at=0, enter="none", hair="short", mood="calm",
                moves=[(3, dict(x=770, dur=1.6)), (6, dict(pose="wave", mood="happy", face=-1, sfx="bongo_high",
                                                          note="主角回头挥手"))]),
        ], draw=ground, hits=[(2, "wood_low", 0.9, "剧本合上")],
            note="悬在起点上方的剧本合上，主角从起点线走开，回头挥手"),
        end_shot(["Adler, A. (1931). What Life Should Mean to You, ch.6.（中译《自卑与超越》）",
                  "Rohrer, J. M., Egloff, B. & Schmukle, S. C. (2015). PNAS, 112(46), 14224–14229.",
                  "Damian, R. I. & Roberts, B. W. (2015). J. Research in Personality, 58, 96–105."],
                 "10 共同体感觉：人在什么时候，会觉得自己有价值？"),
    ]
    return Episode(9, "birth_order", "出生顺序", "老大懂事、老幺任性，是真的吗？", ACC, shots,
                   refs=["Adler, A. (1931). What Life Should Mean to You, ch.6.（中译《自卑与超越》）",
                         "Rohrer, J. M., Egloff, B. & Schmukle, S. C. (2015). PNAS, 112(46), 14224–14229.",
                         "Damian, R. I. & Roberts, B. W. (2015). J. Research in Personality, 58, 96–105."],
                   publish_title="老大懂事、老幺任性，是真的吗？｜阿德勒心理学09 出生顺序",
                   hashtags="#阿德勒 #心理学 #出生顺序 #原生家庭 #科普",
                   cover_title="老大懂事、老幺任性，|是【真的】吗？", cover_sub="阿德勒说过，数据怎么说",
                   cover_shot=0, cover_t=5.8,
                   notes=[
                       "阿德勒在 What Life Should Mean to You 第 6 章 Family Influences 讨论出生顺序，长子“被废黜”（dethroned）"
                       "是他常用的说法；次子“像在赛跑”按大意使用。",
                       "阿德勒强调心理位置而非排行数字（Ansbacher 1956 p.377 二手引用：“It is not, of course, the child's "
                       "number in the order of successive births which influences his character, but the situation into "
                       "which he is born and the way in which he interprets it.”）。",
                       "第 8 镜：Rohrer, Egloff & Schmukle (2015), PNAS 112(46):14224–14229, doi:10.1073/pnas.1506451112；"
                       "20,186 人（美 5,240、英 4,489、德 10,457），外向性、情绪稳定性、宜人性、尽责性、想象力均无出生顺序效应；"
                       "智力有很小的下降，片中不写具体 IQ 数字。",
                       "第 9 镜：Damian & Roberts (2015), J Res Pers 58:96–105, doi:10.1016/j.jrp.2015.05.005；"
                       "约 37.7 万名美国高中生（Project Talent），出生顺序与人格的平均绝对相关约 .02、与智力约 .04。",
                   ]).build()
