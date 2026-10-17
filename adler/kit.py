"""阿德勒系列的绘图元件：纸片剪影风格的人物、道具、图标、气泡、箭头与文字。

所有函数都是时间的纯函数（相同参数画出相同结果），坐标默认以元素中心为准；人物以脚底中点为准。
纸片感来自两点：每个元件带一层偏右下的柔和投影；轮廓平直、无描边。
"""

import functools
import math
from contextlib import contextmanager

import numpy as np
import skia

from engine import gfx
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp

W, H = 1080, 1920

BG = "#F3ECE0"
PAPER = "#FCF8F1"
INK = "#24293B"
INK2 = "#5E6475"
INK3 = "#A39C90"
LINE = "#DCD2C2"
SKIN = "#F4D9BF"
HERO = "#3D6E92"        # 主角（“你”）
OTHER = "#B49F8A"       # 他人
OTHER2 = "#8E9AA8"
OTHER3 = "#C58B6C"
DARK = "#3B3F4E"
GOLD = "#E3A33B"
RED = "#D9593A"
GREEN = "#5E9A6A"
SHADOW = "#2A2218"


def col(c, a: float = 1.0) -> int:
    return gfx.col(c, a)


def mix(c1, c2, x: float):
    return gfx.mix(c1, c2, x)


def shade(c, k: float = 0.18):
    """把颜色压暗 k（0–1），用于人物远侧肢体与立体面。"""
    return gfx.mix(c, "#141018", k)


def tint(c, k: float = 0.5):
    """把颜色提亮到接近纸白。"""
    return gfx.mix(c, PAPER, k)


def paint(color, alpha: float = 1.0, stroke: float = 0.0, blur: float = 0.0) -> skia.Paint:
    p = skia.Paint(AntiAlias=True, Color=col(color, clamp01(alpha)))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


# ---------------------------------------------------------------- 图层与变换

@functools.lru_cache(maxsize=64)
def _shadow_filter(dx: float, dy: float, sigma: float, alpha: float) -> skia.ImageFilter:
    return skia.ImageFilters.DropShadow(dx, dy, sigma, sigma, col(SHADOW, alpha))


@contextmanager
def paper(c, alpha: float = 1.0, lift: float = 1.0, bounds: skia.Rect | None = None):
    """纸片图层：块内绘制的内容整体带一层右下投影；alpha 为整体不透明度，lift 控制投影距离（悬浮高度）。"""
    if alpha <= 0:
        c.save()
        c.clipRect(skia.Rect.MakeWH(0, 0))
        try:
            yield
        finally:
            c.restore()
        return
    lift = max(0.0, lift)
    p = skia.Paint(Alphaf=clamp01(alpha))
    if lift > 0:
        p.setImageFilter(_shadow_filter(round(4 + 5 * lift, 1), round(6 + 9 * lift, 1), round(4 + 5 * lift, 1),
                                        round(0.16 + 0.05 * lift, 2)))
    c.saveLayer(bounds, p)
    try:
        yield
    finally:
        c.restore()


@contextmanager
def fade(c, alpha: float):
    """无投影的整体透明度图层。"""
    if alpha >= 0.999:
        yield
        return
    c.saveLayerAlpha(None, int(255 * clamp01(alpha)))
    try:
        yield
    finally:
        c.restore()


@contextmanager
def at(c, x: float = 0.0, y: float = 0.0, rot: float = 0.0, s: float = 1.0, sy: float | None = None):
    c.save()
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    if s != 1.0 or sy is not None:
        c.scale(s, s if sy is None else sy)
    try:
        yield
    finally:
        c.restore()


# ---------------------------------------------------------------- 基础形状

def rr(c, x, y, w, h, r, color, alpha=1.0):
    if w <= 0 or h <= 0:
        return
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), r, r, paint(color, alpha))


def rr_stroke(c, x, y, w, h, r, color, width, alpha=1.0, dash=None):
    p = paint(color, alpha, width)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), r, r, p)


def dot(c, x, y, r, color, alpha=1.0):
    if r > 0:
        c.drawCircle(x, y, r, paint(color, alpha))


def ring(c, x, y, r, color, width, alpha=1.0, p: float = 1.0, start: float = -90):
    if r <= 0 or p <= 0:
        return
    if p >= 1:
        c.drawCircle(x, y, r, paint(color, alpha, width))
        return
    path = skia.Path()
    path.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), start, 360 * p)
    c.drawPath(path, paint(color, alpha, width))


def poly(c, pts, color, alpha=1.0):
    path = skia.Path()
    path.moveTo(*pts[0])
    for q in pts[1:]:
        path.lineTo(*q)
    path.close()
    c.drawPath(path, paint(color, alpha))


def seg(c, x0, y0, x1, y1, color, width, alpha=1.0, p: float = 1.0):
    if p <= 0:
        return
    c.drawLine(x0, y0, lerp(x0, x1, p), lerp(y0, y1, p), paint(color, alpha, width))


def curve_path(p0, p1, bend: float = 0.0) -> skia.Path:
    """p0→p1 的二次曲线，bend 为控制点相对弦长的侧向偏移比例（正值向左弯）。"""
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    path = skia.Path()
    path.moveTo(x0, y0)
    path.quadTo(mx - dy * bend, my + dx * bend, x1, y1)
    return path


def arrow(c, p0, p1, color=INK, width=10.0, alpha=1.0, p: float = 1.0, bend: float = 0.0, head: float = 30,
          dash=None):
    """带箭头的（曲线）线段，p 为描线进度；箭头只在线画完 85% 后出现。"""
    if p <= 0 or alpha <= 0:
        return
    path = curve_path(p0, p1, bend)
    gfx.stroke_path(c, path, col_hex(color), width, alpha, ease_out(p), dash=dash)
    if p < 0.85:
        return
    pm = skia.PathMeasure(path, False)
    L = pm.getLength() * ease_out(p)
    pos, tan = pm.getPosTan(L)
    ang = math.atan2(tan.y(), tan.x())
    k = clamp01((p - 0.85) / 0.15)
    hp = skia.Path()
    hx, hy = pos.x(), pos.y()
    hp.moveTo(hx + math.cos(ang) * head * 0.35, hy + math.sin(ang) * head * 0.35)
    for s in (-1, 1):
        a = ang + math.pi - s * 0.55
        hp.lineTo(hx + math.cos(a) * head * k, hy + math.sin(a) * head * k)
    hp.close()
    c.drawPath(hp, paint(color, alpha))


def col_hex(c):
    return c


def star(c, x, y, r, color, alpha=1.0, n=5, inner=0.45, rot=0.0):
    path = skia.Path()
    for k in range(2 * n):
        ang = math.radians(rot) - math.pi / 2 + k * math.pi / n
        rr_ = r if k % 2 == 0 else r * inner
        px, py = x + rr_ * math.cos(ang), y + rr_ * math.sin(ang)
        path.lineTo(px, py) if k else path.moveTo(px, py)
    path.close()
    c.drawPath(path, paint(color, alpha))


def heart(c, x, y, s, color, alpha=1.0):
    """心形，s 为宽度。"""
    path = skia.Path()
    path.moveTo(x, y + s * 0.42)
    path.cubicTo(x - s * 0.62, y - s * 0.02, x - s * 0.42, y - s * 0.58, x, y - s * 0.22)
    path.cubicTo(x + s * 0.42, y - s * 0.58, x + s * 0.62, y - s * 0.02, x, y + s * 0.42)
    path.close()
    c.drawPath(path, paint(color, alpha))


def burst(c, x, y, dt, color=GOLD, r0=40, r1=170, n=10, width=8, alpha=1.0):
    """撞击瞬间向外放射的短线（dt 为撞击后秒数，0.35 秒内消失）。"""
    if dt < 0 or dt > 0.4:
        return
    k = ease_out(dt / 0.4)
    a = alpha * (1 - dt / 0.4)
    for i in range(n):
        ang = i * math.tau / n + 0.3
        ra, rb = lerp(r0, r1 * 0.75, k), lerp(r0, r1, k)
        seg(c, x + ra * math.cos(ang), y + ra * math.sin(ang), x + rb * math.cos(ang), y + rb * math.sin(ang),
            color, width * (1 - 0.6 * k), a)


def ripple(c, x, y, dt, color=GOLD, rmax=260, width=6, alpha=0.8, dur=0.7):
    """撞击后扩散的圆环。"""
    if dt < 0 or dt > dur:
        return
    k = ease_out(dt / dur)
    ring(c, x, y, rmax * k, color, width * (1 - k) + 1, alpha * (1 - dt / dur))


def confetti(c, x, y, dt, colors, n=26, seed=3, spread=1.0, alpha=1.0):
    """纸屑：从 (x, y) 向上抛出后下落，2.2 秒内消失。"""
    if dt < 0 or dt > 2.2:
        return
    rng = np.random.default_rng(seed)
    for _ in range(n):
        ang = math.radians(-90 + (rng.random() - 0.5) * 140 * spread)
        v = 500 + 700 * rng.random()
        px = x + math.cos(ang) * v * dt * 0.7
        py = y + math.sin(ang) * v * dt + 900 * dt * dt
        a = alpha * (1 - clamp01((dt - 1.4) / 0.8))
        with at(c, px, py, dt * 500 * (rng.random() - 0.5) + rng.random() * 360, 1, abs(math.cos(dt * 7 + rng.random() * 6)) + 0.2):
            sz = 10 + rng.random() * 10
            rr(c, 0, 0, sz, sz * 0.55, 2, colors[int(rng.random() * len(colors)) % len(colors)], a)


# ---------------------------------------------------------------- 文字

def text(c, s, x, y, size, font="serif", color=INK, alpha=1.0, align="center", **kw) -> float:
    """单行文字，y 为视觉中线；返回宽度。"""
    return gfx.draw_text(c, s, x, y, size, font, color, alpha, align, **kw)


def text_w(s, size, font="serif") -> float:
    return gfx.text_width(s, size, font)


def wrap_lines(s: str, size: float, maxw: float, font: str = "serif") -> list[str]:
    """按 | 手动换行；单行超宽时按宽度均分折行（标点不出现在行首）。"""
    out = []
    for part in s.split("|"):
        if text_w(gfx.plain(part), size, font) <= maxw:
            out.append(part)
            continue
        line, w = "", 0.0
        for ch in part:
            cw = text_w(ch, size, font) if ch not in "【】" else 0
            if w + cw > maxw and line and ch not in "，。！？、；：”’）》…":
                out.append(line)
                line, w = "", 0.0
            line += ch
            w += cw
        if line:
            out.append(line)
    # 跨行的高亮标记补齐
    fixed, open_ = [], False
    for ln in out:
        if open_:
            ln = "【" + ln
        n_open = ln.count("【") - ln.count("】")
        open_ = n_open > 0
        fixed.append(ln + ("】" if open_ else ""))
    return fixed


# ---------------------------------------------------------------- 人物

POSES = {
    "stand": dict(lean=0, head=0, la1=6, la2=4, ra1=-6, ra2=4, ll1=3, ll2=0, rl1=-3, rl2=0),
    "relax": dict(lean=-2, head=-4, la1=10, la2=8, ra1=-10, ra2=8, ll1=5, ll2=0, rl1=-5, rl2=0),
    "sad": dict(lean=14, head=18, la1=2, la2=2, ra1=-2, ra2=2, ll1=2, ll2=0, rl1=-2, rl2=0),
    "think": dict(lean=0, head=-8, la1=40, la2=120, ra1=-8, ra2=10, ll1=3, ll2=0, rl1=-3, rl2=0),
    "point": dict(lean=-2, head=-4, la1=88, la2=0, ra1=-8, ra2=8, ll1=4, ll2=0, rl1=-4, rl2=0),
    "wave": dict(lean=-2, head=-6, la1=150, la2=20, ra1=-8, ra2=6, ll1=3, ll2=0, rl1=-3, rl2=0),
    "cheer": dict(lean=-4, head=-12, la1=158, la2=10, ra1=-158, ra2=-10, ll1=6, ll2=0, rl1=-6, rl2=0),
    "shrug": dict(lean=0, head=8, la1=42, la2=-95, ra1=-42, ra2=95, ll1=3, ll2=0, rl1=-3, rl2=0),
    "reach": dict(lean=6, head=-14, la1=128, la2=6, ra1=-10, ra2=10, ll1=4, ll2=0, rl1=-8, rl2=0),
    "push": dict(lean=14, head=-4, la1=86, la2=12, ra1=74, ra2=18, ll1=18, ll2=-6, rl1=-22, rl2=-4),
    "carry": dict(lean=4, head=-2, la1=60, la2=60, ra1=50, ra2=70, ll1=3, ll2=0, rl1=-3, rl2=0),
    "hide": dict(lean=22, head=26, la1=60, la2=130, ra1=50, ra2=140, ll1=30, ll2=-60, rl1=20, rl2=-50),
    "crouch": dict(lean=30, head=10, la1=40, la2=60, ra1=30, ra2=70, ll1=70, ll2=-110, rl1=60, rl2=-100),
    "sit": dict(lean=2, head=0, la1=20, la2=40, ra1=12, ra2=50, ll1=88, ll2=-88, rl1=82, rl2=-82, seat=0.27),
    "sit_sad": dict(lean=18, head=22, la1=26, la2=60, ra1=18, ra2=66, ll1=88, ll2=-92, rl1=80, rl2=-84, seat=0.27),
    "hug": dict(lean=4, head=-6, la1=70, la2=50, ra1=62, ra2=58, ll1=4, ll2=0, rl1=-4, rl2=0),
    "give": dict(lean=6, head=-2, la1=72, la2=-8, ra1=-8, ra2=8, ll1=6, ll2=0, rl1=-6, rl2=0),
    "fist": dict(lean=-4, head=-8, la1=140, la2=60, ra1=-10, ra2=10, ll1=8, ll2=0, rl1=-6, rl2=0),
    "block": dict(lean=-6, head=6, la1=72, la2=70, ra1=64, ra2=80, ll1=-6, ll2=0, rl1=-14, rl2=-4),
    "cover": dict(lean=10, head=14, la1=110, la2=120, ra1=100, ra2=130, ll1=4, ll2=0, rl1=-4, rl2=0),
    "proud": dict(lean=-8, head=-16, la1=-40, la2=100, ra1=40, ra2=-100, ll1=8, ll2=0, rl1=-8, rl2=0),
    "climb": dict(lean=8, head=-14, la1=150, la2=20, ra1=110, ra2=40, ll1=50, ll2=-60, rl1=-10, rl2=-10),
}

_POSE_KEYS = ("lean", "head", "la1", "la2", "ra1", "ra2", "ll1", "ll2", "rl1", "rl2", "seat")


def pose(name_or_dict) -> dict:
    d = dict(POSES[name_or_dict]) if isinstance(name_or_dict, str) else dict(name_or_dict)
    d.setdefault("seat", 0.0)
    return d


def blend(p1, p2, k: float) -> dict:
    a, b = pose(p1), pose(p2)
    k = clamp01(k)
    return {key: lerp(a.get(key, 0.0), b.get(key, 0.0), k) for key in _POSE_KEYS}


def walk(phase: float, amp: float = 1.0, base="stand") -> dict:
    """行走步态：phase 以步为单位（每 1.0 迈一步），amp 为摆幅（0 即站立）。"""
    d = pose(base)
    s = math.sin(phase * math.pi)
    d["ll1"] += 26 * s * amp
    d["rl1"] -= 26 * s * amp
    d["ll2"] += -24 * max(0, -s) * amp
    d["rl2"] += -24 * max(0, s) * amp
    d["la1"] -= 22 * s * amp
    d["ra1"] += 22 * s * amp
    d["lean"] += 4 * amp
    return d


def _limb(x, y, a1, a2, l1, l2, face):
    r1, r2 = math.radians(a1), math.radians(a1 + a2)
    ex, ey = x + face * l1 * math.sin(r1), y + l1 * math.cos(r1)
    hx, hy = ex + face * l2 * math.sin(r2), ey + l2 * math.cos(r2)
    return (ex, ey), (hx, hy)


def figure(c, x, y, s, p="stand", color=HERO, head_color=SKIN, alpha=1.0, face: int = 1, mood="calm",
           hair=None, hair_color=None, bob: float = 0.0, lift: float = 1.0, look: float = 0.0, blink: bool = False,
           scarf=None, prop=None):
    """纸片人物：(x, y) 为脚底中点，s 为站立身高（像素）。

    p 为姿势名或姿势字典（见 POSES / blend / walk）；face=1 朝右、-1 朝左；mood 为 calm / smile / happy / sad /
    worried / open / surprised / flat / angry；hair 为 None / short / long / bun / cap；look 为视线上下偏移（-1 向下，1 向上）；
    prop(c, hand_xy) 可在前手位置绘制手持物。
    """
    if alpha <= 0 or s <= 0:
        return
    d = pose(p)
    u = s
    thigh, shin = 0.235 * u, 0.225 * u
    upper, fore = 0.19 * u, 0.18 * u
    lw = 0.082 * u

    # 腿：计算两腿在竖直方向上的伸展，决定髋部高度（脚落地），坐姿时用座高
    def leg_extent(a1, a2):
        (_, ey), (_, fy) = _limb(0, 0, a1, a2, thigh, shin, 1)
        return max(ey, fy)

    if d["seat"] > 0:
        hip_y = -d["seat"] * u
    else:
        hip_y = -max(leg_extent(d["ll1"], d["ll2"]), leg_extent(d["rl1"], d["rl2"]))
    hip_y -= bob * u
    lean = math.radians(d["lean"])
    torso = 0.30 * u
    sh_x = face * torso * math.sin(lean)
    sh_y = hip_y - torso * math.cos(lean)
    far = shade(color, 0.22)
    bounds = skia.Rect.MakeLTRB(x - u * 0.9, y - u * 1.35, x + u * 0.9, y + u * 0.15)
    with paper(c, alpha, lift, bounds):
        c.save()
        c.translate(x, y)
        # 远侧手臂与腿
        hips = [(-0.035 * u * face, hip_y), (0.035 * u * face, hip_y)]
        shoulders = [(sh_x - 0.06 * u * face, sh_y + 0.03 * u), (sh_x + 0.06 * u * face, sh_y + 0.03 * u)]
        k_r, f_r = _limb(*hips[0], d["rl1"], d["rl2"], thigh, shin, face)
        _stroke3(c, hips[0], k_r, f_r, far, lw)
        _foot(c, f_r, face, lw, far)
        e_r, h_r = _limb(*shoulders[0], d["ra1"], d["ra2"], upper, fore, face)
        _stroke3(c, shoulders[0], e_r, h_r, far, lw * 0.92)
        dot(c, *h_r, lw * 0.62, mix(head_color, far, 0.25))
        # 躯干
        tp = skia.Path()
        bw, tw = 0.115 * u, 0.13 * u
        cx0, cy0 = 0, hip_y
        nx, ny = math.cos(lean), math.sin(lean) * face
        pts = [(cx0 - bw * nx, cy0 - bw * ny * 0), (sh_x - tw * nx, sh_y), (sh_x + tw * nx, sh_y), (cx0 + bw * nx, cy0)]
        tp.moveTo(pts[0][0], cy0 + 0.04 * u)
        tp.lineTo(pts[1][0], pts[1][1] + 0.03 * u)
        tp.quadTo(sh_x, sh_y - 0.05 * u, pts[2][0], pts[2][1] + 0.03 * u)
        tp.lineTo(pts[3][0], cy0 + 0.04 * u)
        tp.quadTo(0, cy0 + 0.09 * u, pts[0][0], cy0 + 0.04 * u)
        tp.close()
        c.drawPath(tp, paint(color))
        if scarf:
            c.drawCircle(sh_x, sh_y - 0.005 * u, 0.07 * u, paint(scarf))
        # 近侧腿
        k_l, f_l = _limb(*hips[1], d["ll1"], d["ll2"], thigh, shin, face)
        _stroke3(c, hips[1], k_l, f_l, color, lw)
        _foot(c, f_l, face, lw, color)
        # 头
        hd = math.radians(d["head"])
        neck = (sh_x, sh_y)
        hr = 0.16 * u
        hx = neck[0] + face * (0.15 * u) * math.sin(lean + hd * 0.5)
        hy = neck[1] - (0.15 * u) * math.cos(lean + hd * 0.5)
        _head(c, hx, hy, hr, head_color, face, mood, hair, hair_color or shade(color, 0.45), d["head"], look, blink)
        # 近侧手臂
        e_l, h_l = _limb(*shoulders[1], d["la1"], d["la2"], upper, fore, face)
        _stroke3(c, shoulders[1], e_l, h_l, color, lw * 0.92)
        dot(c, *h_l, lw * 0.62, head_color)
        if prop:
            prop(c, h_l)
        c.restore()


def _stroke3(c, a, b, d, color, width):
    path = skia.Path()
    path.moveTo(*a)
    path.lineTo(*b)
    path.lineTo(*d)
    c.drawPath(path, paint(color, 1.0, width))


def _foot(c, f, face, lw, color):
    path = skia.Path()
    path.moveTo(f[0] - face * lw * 0.2, f[1])
    path.lineTo(f[0] + face * lw * 0.75, f[1] + lw * 0.05)
    c.drawPath(path, paint(color, 1.0, lw * 0.85))


def _head(c, x, y, r, color, face, mood, hair, hair_color, tilt, look, blink):
    with at(c, x, y, tilt * 0.35 * face):
        if hair == "long":
            c.drawRoundRect(skia.Rect.MakeXYWH(-r * 1.05 - face * r * 0.15, -r * 1.02, r * 2.1, r * 2.0), r, r,
                            paint(hair_color))
        c.drawCircle(0, 0, r, paint(color))
        if hair in ("short", "long", "bun"):
            path = skia.Path()
            path.addArc(skia.Rect.MakeXYWH(-r * 1.04, -r * 1.06, r * 2.08, r * 2.0), 180, 180)
            path.quadTo(r * 0.2 * face, -r * 0.35, -r * 1.04, -r * 0.02)
            path.close()
            c.drawPath(path, paint(hair_color))
            if hair == "bun":
                c.drawCircle(-face * r * 0.7, -r * 0.85, r * 0.36, paint(hair_color))
        elif hair == "cap":
            path = skia.Path()
            path.addArc(skia.Rect.MakeXYWH(-r, -r * 1.05, r * 2, r * 1.9), 180, 180)
            path.close()
            c.drawPath(path, paint(hair_color))
            c.drawRoundRect(skia.Rect.MakeXYWH(face * r * 0.2 - (r * 0.9 if face < 0 else 0), -r * 0.2, r * 0.9, r * 0.18),
                            r * 0.09, r * 0.09, paint(hair_color))
        ex = face * r * 0.42
        ey = r * 0.05 - look * r * 0.12
        gap = r * 0.36
        eye = INK
        for k, sx in enumerate((ex - gap / 2, ex + gap / 2)):
            if blink or mood == "happy":
                path = skia.Path()
                path.addArc(skia.Rect.MakeXYWH(sx - r * 0.1, ey - r * 0.06, r * 0.2, r * 0.18), 200, 140)
                c.drawPath(path, paint(eye, 1, r * 0.06))
            elif mood == "sad":
                c.drawCircle(sx, ey + r * 0.04, r * 0.07, paint(eye))
                seg(c, sx - r * 0.1, ey - r * 0.13 - (0.05 * r if k == 0 else -0.05 * r) * face,
                    sx + r * 0.1, ey - r * 0.13 + (0.05 * r if k == 0 else -0.05 * r) * face, eye, r * 0.05)
            elif mood == "worried":
                c.drawCircle(sx, ey, r * 0.075, paint(eye))
                seg(c, sx - r * 0.1, ey - r * 0.17 + (0.04 * r if k == 0 else -0.04 * r),
                    sx + r * 0.1, ey - r * 0.17 - (0.04 * r if k == 0 else -0.04 * r), eye, r * 0.05)
            elif mood == "angry":
                c.drawCircle(sx, ey, r * 0.075, paint(eye))
                seg(c, sx - r * 0.11, ey - r * 0.2 + (-0.06 * r if k == 0 else 0.06 * r),
                    sx + r * 0.11, ey - r * 0.2 - (-0.06 * r if k == 0 else 0.06 * r), eye, r * 0.055)
            elif mood == "surprised":
                c.drawCircle(sx, ey, r * 0.095, paint(eye))
            else:
                c.drawCircle(sx, ey, r * 0.075, paint(eye))
        mx, my = ex, r * 0.42 - look * r * 0.06
        if mood in ("smile", "happy"):
            path = skia.Path()
            path.addArc(skia.Rect.MakeXYWH(mx - r * 0.2, my - r * 0.2, r * 0.4, r * 0.3), 20, 140)
            c.drawPath(path, paint(eye, 1, r * 0.065))
            if mood == "happy":
                c.drawCircle(mx - r * 0.38, my - r * 0.1, r * 0.09, paint(RED, 0.25))
                c.drawCircle(mx + r * 0.38, my - r * 0.1, r * 0.09, paint(RED, 0.25))
        elif mood in ("sad", "worried"):
            path = skia.Path()
            path.addArc(skia.Rect.MakeXYWH(mx - r * 0.16, my + r * 0.02, r * 0.32, r * 0.22), 200, 140)
            c.drawPath(path, paint(eye, 1, r * 0.06))
        elif mood in ("open", "surprised"):
            c.drawOval(skia.Rect.MakeXYWH(mx - r * 0.08, my - r * 0.06, r * 0.16, r * 0.2), paint(eye))
        elif mood in ("flat", "angry"):
            seg(c, mx - r * 0.13, my, mx + r * 0.13, my, eye, r * 0.06)


def crowd(c, x, y, n, s, t=0.0, colors=(OTHER, OTHER2, OTHER3, "#9C8FB0"), alpha=1.0, spread=520, seed=4,
          moods=("calm", "smile", "flat"), face_to=None, rows=1):
    """一排（或多排）他人剪影，带轻微呼吸起伏。face_to 指定众人朝向的 x 坐标。"""
    rng = np.random.default_rng(seed)
    for i in range(n):
        row = i % rows
        k = i // rows
        m = max(1, (n + rows - 1) // rows - 1)
        px = x - spread / 2 + spread * k / m + (rng.random() - 0.5) * 30 + (row % 2) * spread / m / 2
        py = y - row * s * 0.32
        sc = s * (0.9 + 0.2 * rng.random()) * (1 - 0.12 * row)
        f = 1 if face_to is None else (1 if face_to > px else -1)
        figure(c, px, py, sc, "stand", colors[i % len(colors)], alpha=alpha, face=f,
               mood=moods[i % len(moods)], bob=0.006 * math.sin(t * 2.4 + i), lift=0.6,
               hair=("short", None, "bun", "long")[i % 4])


# ---------------------------------------------------------------- 卡片与气泡

def card(c, x, y, w, h, fill=PAPER, alpha=1.0, r=22, lift=1.0, rot=0.0, scale=1.0, accent=None, draw=None):
    """纸卡：draw(c, w, h) 在以卡片中心为原点的坐标系中绘制内容；accent 为顶部色条。"""
    if alpha <= 0 or scale <= 0:
        return
    with at(c, x, y, rot, scale):
        with paper(c, alpha, lift, skia.Rect.MakeXYWH(-w, -h, 2 * w, 2 * h)):
            rr(c, 0, 0, w, h, r, fill)
            if accent:
                c.save()
                c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), r, r), doAntiAlias=True)
                c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, 16), paint(accent))
                c.restore()
            if draw:
                draw(c, w, h)


def text_card(c, x, y, lines, size=46, w=None, fill=PAPER, color=INK, hi=RED, alpha=1.0, rot=0.0, scale=1.0,
              accent=None, font="serif", lift=1.0, pad=44, gap=1.45):
    """自动尺寸的文字卡；lines 为若干行，支持【高亮】。"""
    tw = max(text_w(gfx.plain(s), size, font) for s in lines)
    w = w or tw + pad * 2
    h = size * gap * len(lines) + pad * 1.3

    def draw(c, w_, h_):
        for i, s in enumerate(lines):
            gfx.draw_rich(c, s, 0, (i - (len(lines) - 1) / 2) * size * gap + (6 if accent else 0), size, font,
                          color, hi, 1.0)

    card(c, x, y, w, h, fill, alpha, 22, lift, rot, scale, accent, draw)
    return w, h


def bubble(c, x, y, s, size=44, tail=(0, 1), alpha=1.0, scale=1.0, fill=PAPER, color=INK, hi=RED, think=False,
           font="serif", lift=0.8):
    """对话 / 思考气泡：(x, y) 为气泡中心，tail 为尾巴指向的相对方向（单位向量）。"""
    if alpha <= 0 or scale <= 0:
        return
    lines = s.split("|")
    tw = max(text_w(gfx.plain(ln), size, font) for ln in lines)
    w, h = tw + size * 1.3, size * 1.45 * len(lines) + size * 0.8
    with at(c, x, y, 0, scale):
        with paper(c, alpha, lift, skia.Rect.MakeXYWH(-w * 1.2, -h * 1.5, w * 2.4, h * 3)):
            r = min(h / 2, size * 1.0)
            rr(c, 0, 0, w, h, r, fill)
            tx, ty = tail
            if think:
                for k, rad in enumerate((size * 0.32, size * 0.2)):
                    dot(c, tx * (w / 2 + size * (0.25 + 0.6 * k)) * 0.8, ty * (h / 2 + size * (0.3 + 0.55 * k)), rad, fill)
            else:
                bx, by = tx * w * 0.18, ty * h / 2
                poly(c, [(bx - size * 0.32, by - ty * 4), (bx + size * 0.32, by - ty * 4),
                         (bx + tx * size * 0.6, by + ty * size * 0.62)], fill)
            for i, ln in enumerate(lines):
                gfx.draw_rich(c, ln, 0, (i - (len(lines) - 1) / 2) * size * 1.45, size, font, color, hi, 1.0)


def pill(c, x, y, s, size=30, fill=INK, color=PAPER, alpha=1.0, font="sans_medium", align="center", pad=22):
    w = text_w(s, size, font) + pad * 2
    h = size * 1.7
    x0 = x if align == "left" else x - w / 2 if align == "center" else x - w
    rr(c, x0 + w / 2, y, w, h, h / 2, fill, alpha)
    text(c, s, x0 + w / 2, y, size, font, color, alpha)
    return w


# ---------------------------------------------------------------- 道具与图标（s 为整体尺寸）

def icon(c, name, x, y, s, color=INK, alpha=1.0, lift=0.8, rot=0.0, scale=1.0, p: float = 1.0, accent=GOLD):
    """常用图标；p 为部分图标的动画进度（如沙漏、植物生长）。"""
    if alpha <= 0 or scale <= 0:
        return
    fn = ICONS[name]
    with at(c, x, y, rot, scale):
        with paper(c, alpha, lift, skia.Rect.MakeXYWH(-s * 1.5, -s * 1.5, s * 3, s * 3)):
            fn(c, s, color, p, accent)


def _i_door(c, s, color, p, accent):
    rr(c, 0, 0, s * 0.72, s * 1.1, 8, shade(color, 0.15))
    open_ = clamp01(p)
    w = s * 0.62 * (1 - 0.75 * open_)
    if open_ > 0:
        rr(c, 0, 0, s * 0.62, s * 1.0, 4, accent)
    c.drawRect(skia.Rect.MakeXYWH(-s * 0.31, -s * 0.5, w, s * 1.0), paint(color))
    dot(c, -s * 0.31 + w * 0.82, s * 0.04, s * 0.04, tint(color, 0.6))


def _i_house(c, s, color, p, accent):
    poly(c, [(-s * 0.6, -s * 0.05), (0, -s * 0.6), (s * 0.6, -s * 0.05)], shade(color, 0.2))
    rr(c, 0, s * 0.22, s * 0.9, s * 0.6, 6, color)
    rr(c, 0, s * 0.3, s * 0.22, s * 0.44, 4, accent if p > 0.5 else shade(color, 0.35))
    rr(c, -s * 0.27, s * 0.12, s * 0.16, s * 0.16, 3, tint(accent, 0.3) if p > 0.5 else shade(color, 0.3))


def _i_brief(c, s, color, p, accent):
    rr(c, 0, -s * 0.28, s * 0.32, s * 0.2, 8, shade(color, 0.3))
    rr(c, 0, -s * 0.28, s * 0.2, s * 0.09, 4, PAPER)
    rr(c, 0, s * 0.05, s * 0.9, s * 0.6, 12, color)
    c.drawRect(skia.Rect.MakeXYWH(-s * 0.45, -s * 0.02, s * 0.9, s * 0.05), paint(shade(color, 0.25)))
    rr(c, 0, s * 0.0, s * 0.12, s * 0.12, 3, accent)


def _i_friends(c, s, color, p, accent):
    for dx, cc in ((-0.2, shade(color, 0.2)), (0.2, color)):
        dot(c, dx * s, -s * 0.22, s * 0.16, cc)
        path = skia.Path()
        path.addArc(skia.Rect.MakeXYWH(dx * s - s * 0.27, -s * 0.02, s * 0.54, s * 0.62), 180, 180)
        path.close()
        c.drawPath(path, paint(cc))


def _i_heart(c, s, color, p, accent):
    heart(c, 0, 0, s, color)


def _i_rings(c, s, color, p, accent):
    ring(c, -s * 0.16, 0, s * 0.27, color, s * 0.09)
    ring(c, s * 0.16, 0, s * 0.27, accent, s * 0.09)


def _i_book(c, s, color, p, accent):
    rr(c, 0, 0, s * 0.95, s * 0.66, 8, shade(color, 0.25))
    rr(c, -s * 0.23, -s * 0.02, s * 0.44, s * 0.6, 6, PAPER)
    rr(c, s * 0.23, -s * 0.02, s * 0.44, s * 0.6, 6, PAPER)
    for k in range(4):
        seg(c, -s * 0.38, -s * 0.18 + k * s * 0.11, -s * 0.08, -s * 0.18 + k * s * 0.11, LINE, 4)
        seg(c, s * 0.08, -s * 0.18 + k * s * 0.11, s * 0.38, -s * 0.18 + k * s * 0.11, LINE, 4)


def _i_target(c, s, color, p, accent):
    for k, cc in enumerate((color, PAPER, color, PAPER, accent)):
        dot(c, 0, 0, s * (0.5 - k * 0.1), cc)


def _i_shield(c, s, color, p, accent):
    path = skia.Path()
    path.moveTo(0, -s * 0.5)
    path.quadTo(s * 0.3, -s * 0.36, s * 0.45, -s * 0.38)
    path.quadTo(s * 0.48, s * 0.25, 0, s * 0.52)
    path.quadTo(-s * 0.48, s * 0.25, -s * 0.45, -s * 0.38)
    path.quadTo(-s * 0.3, -s * 0.36, 0, -s * 0.5)
    c.drawPath(path, paint(color))
    path2 = skia.Path()
    path2.moveTo(0, -s * 0.38)
    path2.quadTo(s * 0.32, s * 0.15, 0, s * 0.38)
    path2.close()
    c.drawPath(path2, paint(tint(color, 0.25)))


def _i_crown(c, s, color, p, accent):
    poly(c, [(-s * 0.45, s * 0.25), (-s * 0.5, -s * 0.25), (-s * 0.22, 0), (0, -s * 0.38), (s * 0.22, 0),
             (s * 0.5, -s * 0.25), (s * 0.45, s * 0.25)], color)
    for dx in (-0.5, 0, 0.5):
        dot(c, dx * s, -s * (0.25 if dx else 0.38) - s * 0.04, s * 0.06, accent)


def _i_trophy(c, s, color, p, accent):
    path = skia.Path()
    path.moveTo(-s * 0.3, -s * 0.4)
    path.lineTo(s * 0.3, -s * 0.4)
    path.quadTo(s * 0.3, s * 0.05, 0, s * 0.1)
    path.quadTo(-s * 0.3, s * 0.05, -s * 0.3, -s * 0.4)
    c.drawPath(path, paint(color))
    ring(c, -s * 0.32, -s * 0.22, s * 0.12, color, s * 0.05)
    ring(c, s * 0.32, -s * 0.22, s * 0.12, color, s * 0.05)
    rr(c, 0, s * 0.2, s * 0.08, s * 0.2, 2, color)
    rr(c, 0, s * 0.36, s * 0.36, s * 0.1, 4, shade(color, 0.2))


def _i_cloud(c, s, color, p, accent):
    for dx, dy, r in ((-0.25, 0.05, 0.22), (0.0, -0.08, 0.28), (0.26, 0.04, 0.22)):
        dot(c, dx * s, dy * s, r * s, color)
    rr(c, 0, s * 0.12, s * 0.8, s * 0.24, s * 0.12, color)


def _i_sun(c, s, color, p, accent):
    for k in range(10):
        a = k * math.tau / 10 + p * 0.6
        seg(c, math.cos(a) * s * 0.36, math.sin(a) * s * 0.36, math.cos(a) * s * 0.5, math.sin(a) * s * 0.5,
            color, s * 0.06)
    dot(c, 0, 0, s * 0.28, color)


def _i_sprout(c, s, color, p, accent):
    g = clamp01(p)
    rr(c, 0, s * 0.36, s * 0.5, s * 0.3, 8, OTHER3)
    seg(c, 0, s * 0.22, 0, s * (0.22 - 0.55 * g), GREEN, s * 0.06)
    if g > 0.3:
        k = ease_out((g - 0.3) / 0.7)
        for sgn in (-1, 1):
            path = skia.Path()
            bx, by = 0, s * (0.22 - 0.45 * g)
            path.moveTo(bx, by)
            path.quadTo(bx + sgn * s * 0.3 * k, by - s * 0.22 * k, bx + sgn * s * 0.34 * k, by - s * 0.02)
            path.quadTo(bx + sgn * s * 0.12 * k, by + s * 0.04, bx, by)
            c.drawPath(path, paint(GREEN))


def _i_can(c, s, color, p, accent):
    rr(c, 0, s * 0.05, s * 0.55, s * 0.5, 12, color)
    poly(c, [(s * 0.25, -s * 0.05), (s * 0.62, -s * 0.32), (s * 0.66, -s * 0.24), (s * 0.27, s * 0.12)], color)
    ring(c, -s * 0.32, s * 0.02, s * 0.16, shade(color, 0.15), s * 0.06)


def _i_clock(c, s, color, p, accent):
    dot(c, 0, 0, s * 0.45, color)
    dot(c, 0, 0, s * 0.37, PAPER)
    a = p * math.tau
    seg(c, 0, 0, math.sin(a) * s * 0.26, -math.cos(a) * s * 0.26, INK, s * 0.05)
    seg(c, 0, 0, math.sin(a / 12) * s * 0.17, -math.cos(a / 12) * s * 0.17, INK, s * 0.06)


def _i_mirror(c, s, color, p, accent):
    c.drawOval(skia.Rect.MakeXYWH(-s * 0.35, -s * 0.5, s * 0.7, s * 0.9), paint(color))
    c.drawOval(skia.Rect.MakeXYWH(-s * 0.28, -s * 0.43, s * 0.56, s * 0.76), paint(tint(accent, 0.65)))
    rr(c, 0, s * 0.48, s * 0.1, s * 0.16, 3, color)
    rr(c, 0, s * 0.56, s * 0.36, s * 0.07, 3, color)


def _i_photo(c, s, color, p, accent):
    rr(c, 0, 0, s * 0.9, s * 0.75, 6, PAPER)
    rr(c, 0, -s * 0.06, s * 0.76, s * 0.5, 3, tint(color, 0.35))
    poly(c, [(-s * 0.38, s * 0.19), (-s * 0.1, -s * 0.12), (s * 0.1, s * 0.08), (s * 0.2, -s * 0.02), (s * 0.38, s * 0.19)],
         color)
    dot(c, s * 0.22, -s * 0.18, s * 0.06, accent)


def _i_baggage(c, s, color, p, accent):
    rr(c, 0, -s * 0.3, s * 0.3, s * 0.18, 8, shade(color, 0.3))
    rr(c, 0, -s * 0.3, s * 0.18, s * 0.08, 4, PAPER)
    rr(c, 0, s * 0.08, s * 0.72, s * 0.66, 10, color)
    for dx in (-0.18, 0.18):
        c.drawRect(skia.Rect.MakeXYWH(dx * s - s * 0.03, -s * 0.25, s * 0.06, s * 0.66), paint(shade(color, 0.2)))


def _i_check(c, s, color, p, accent):
    dot(c, 0, 0, s * 0.45, color)
    path = skia.Path()
    path.moveTo(-s * 0.2, 0)
    path.lineTo(-s * 0.05, s * 0.15)
    path.lineTo(s * 0.22, -s * 0.15)
    gfx.stroke_path(c, path, PAPER, s * 0.09, 1.0, clamp01(p) if p > 0 else 1.0)


def _i_cross(c, s, color, p, accent):
    dot(c, 0, 0, s * 0.45, color)
    seg(c, -s * 0.16, -s * 0.16, s * 0.16, s * 0.16, PAPER, s * 0.09)
    seg(c, s * 0.16, -s * 0.16, -s * 0.16, s * 0.16, PAPER, s * 0.09)


def _i_question(c, s, color, p, accent):
    dot(c, 0, 0, s * 0.45, color)
    text(c, "?", 0, -s * 0.02, s * 0.62, "black", PAPER)


def _i_bulb(c, s, color, p, accent):
    if p > 0:
        dot(c, 0, -s * 0.1, s * 0.5 * (0.8 + 0.2 * p), tint(accent, 0.4), 0.5 * p)
    dot(c, 0, -s * 0.1, s * 0.3, accent if p > 0 else INK3)
    rr(c, 0, s * 0.24, s * 0.26, s * 0.16, 4, color)
    rr(c, 0, s * 0.35, s * 0.2, s * 0.06, 3, color)


def _i_flag(c, s, color, p, accent):
    seg(c, -s * 0.25, -s * 0.5, -s * 0.25, s * 0.5, INK, s * 0.05)
    wave = math.sin(p * math.tau) * s * 0.04
    path = skia.Path()
    path.moveTo(-s * 0.25, -s * 0.48)
    path.quadTo(s * 0.05, -s * 0.55 + wave, s * 0.35, -s * 0.42)
    path.lineTo(s * 0.35, -s * 0.12)
    path.quadTo(s * 0.05, -s * 0.25 - wave, -s * 0.25, -s * 0.18)
    path.close()
    c.drawPath(path, paint(accent))


def _i_gift(c, s, color, p, accent):
    rr(c, 0, s * 0.12, s * 0.72, s * 0.56, 8, color)
    rr(c, 0, -s * 0.2, s * 0.82, s * 0.18, 6, shade(color, 0.12))
    c.drawRect(skia.Rect.MakeXYWH(-s * 0.06, -s * 0.29, s * 0.12, s * 0.7), paint(accent))
    for sgn in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(sgn * s * 0.14 - s * 0.12, -s * 0.44, s * 0.24, s * 0.16), paint(accent))


def _i_chain(c, s, color, p, accent):
    for k in range(3):
        c.save()
        c.translate((k - 1) * s * 0.34, 0)
        c.rotate(30 if k % 2 else -30)
        c.drawRoundRect(skia.Rect.MakeXYWH(-s * 0.22, -s * 0.12, s * 0.44, s * 0.24), s * 0.12, s * 0.12,
                        paint(color, 1, s * 0.07))
        c.restore()


def _i_key(c, s, color, p, accent):
    ring(c, -s * 0.24, 0, s * 0.17, color, s * 0.08)
    seg(c, -s * 0.07, 0, s * 0.42, 0, color, s * 0.08)
    seg(c, s * 0.3, 0, s * 0.3, s * 0.14, color, s * 0.07)
    seg(c, s * 0.4, 0, s * 0.4, s * 0.12, color, s * 0.07)


def _i_eye(c, s, color, p, accent):
    path = skia.Path()
    path.moveTo(-s * 0.48, 0)
    path.quadTo(0, -s * 0.42, s * 0.48, 0)
    path.quadTo(0, s * 0.42, -s * 0.48, 0)
    c.drawPath(path, paint(PAPER))
    c.drawPath(path, paint(color, 1, s * 0.05))
    dot(c, 0, 0, s * 0.15, color)
    dot(c, s * 0.05, -s * 0.05, s * 0.04, PAPER)


def _i_ladder(c, s, color, p, accent):
    for dx in (-0.22, 0.22):
        seg(c, dx * s, -s * 0.6, dx * s, s * 0.6, color, s * 0.06)
    for k in range(6):
        y = -s * 0.5 + k * s * 0.2
        seg(c, -s * 0.22, y, s * 0.22, y, color, s * 0.045)


def _i_scale(c, s, color, p, accent):
    """天平：p ∈ [-1, 1] 为倾斜（正值右侧下沉）。"""
    tilt = p * 14
    rr(c, 0, s * 0.45, s * 0.5, s * 0.08, 4, color)
    seg(c, 0, s * 0.45, 0, -s * 0.35, color, s * 0.06)
    with at(c, 0, -s * 0.35, tilt):
        seg(c, -s * 0.48, 0, s * 0.48, 0, color, s * 0.05)
        for sgn in (-1, 1):
            with at(c, sgn * s * 0.48, 0, -tilt):
                seg(c, 0, 0, -s * 0.16, s * 0.3, color, s * 0.02)
                seg(c, 0, 0, s * 0.16, s * 0.3, color, s * 0.02)
                path = skia.Path()
                path.addArc(skia.Rect.MakeXYWH(-s * 0.2, s * 0.18, s * 0.4, s * 0.24), 0, 180)
                path.close()
                c.drawPath(path, paint(accent if sgn > 0 else shade(accent, 0.25)))
    dot(c, 0, -s * 0.35, s * 0.05, accent)


def _i_megaphone(c, s, color, p, accent):
    poly(c, [(-s * 0.3, -s * 0.12), (s * 0.3, -s * 0.36), (s * 0.3, s * 0.36), (-s * 0.3, s * 0.12)], color)
    rr(c, -s * 0.36, 0, s * 0.16, s * 0.3, 6, shade(color, 0.2))


def _i_water(c, s, color, p, accent):
    path = skia.Path()
    path.moveTo(0, -s * 0.48)
    path.quadTo(s * 0.4, 0, s * 0.3, s * 0.2)
    path.quadTo(0, s * 0.55, -s * 0.3, s * 0.2)
    path.quadTo(-s * 0.4, 0, 0, -s * 0.48)
    c.drawPath(path, paint(color))
    dot(c, -s * 0.1, s * 0.12, s * 0.07, tint(color, 0.6))


def _i_phone(c, s, color, p, accent):
    rr(c, 0, 0, s * 0.5, s * 0.9, s * 0.08, color)
    rr(c, 0, -s * 0.02, s * 0.42, s * 0.72, s * 0.04, tint(accent, 0.55))


def _i_puzzle(c, s, color, p, accent):
    rr(c, 0, 0, s * 0.6, s * 0.6, 8, color)
    dot(c, s * 0.3, 0, s * 0.12, color)
    dot(c, 0, -s * 0.3, s * 0.12, color)


ICONS = {
    "door": _i_door, "house": _i_house, "brief": _i_brief, "friends": _i_friends, "heart": _i_heart, "rings": _i_rings,
    "book": _i_book, "target": _i_target, "shield": _i_shield, "crown": _i_crown, "trophy": _i_trophy,
    "cloud": _i_cloud, "sun": _i_sun, "sprout": _i_sprout, "can": _i_can, "clock": _i_clock, "mirror": _i_mirror,
    "photo": _i_photo, "baggage": _i_baggage, "check": _i_check, "cross": _i_cross, "question": _i_question,
    "bulb": _i_bulb, "flag": _i_flag, "gift": _i_gift, "chain": _i_chain, "key": _i_key, "eye": _i_eye,
    "ladder": _i_ladder, "scale": _i_scale, "megaphone": _i_megaphone, "water": _i_water, "phone": _i_phone,
    "puzzle": _i_puzzle,
}


# ---------------------------------------------------------------- 场景道具

def memory(c, x, y, w, h, fn=None, alpha=1.0, rot=-3.0, scale=1.0, label="小时候", tone="#C9B79C"):
    """回忆照片：泛黄相纸 + 内框，fn(c, w, h) 在内框坐标（中心为原点）中绘制小场景。"""
    if alpha <= 0 or scale <= 0:
        return
    with at(c, x, y, rot, scale):
        with paper(c, alpha, 1.0, skia.Rect.MakeXYWH(-w, -h, 2 * w, 2 * h)):
            rr(c, 0, 0, w, h, 10, "#FBF3E4")
            iw, ih = w - 36, h - 90
            rr(c, 0, -22, iw, ih, 4, tone)
            if fn:
                c.save()
                c.clipRect(skia.Rect.MakeXYWH(-iw / 2, -22 - ih / 2, iw, ih))
                c.translate(0, -22)
                fn(c, iw, ih)
                c.restore()
            if label:
                text(c, label, 0, h / 2 - 34, 30, "sans_medium", INK2)


def domino(c, x, y, w, h, angle, color, alpha=1.0):
    """多米诺骨牌：(x, y) 为底边右下角支点（向右倒），angle 为倾倒角度（0 直立，90 平躺）。"""
    with at(c, x, y, angle):
        rr(c, -w / 2, -h / 2, w, h, 8, color, alpha)
        dot(c, -w / 2, -h * 0.72, w * 0.16, tint(color, 0.6), alpha)
        dot(c, -w / 2, -h * 0.28, w * 0.16, tint(color, 0.6), alpha)


def ground(c, y, alpha=1.0, color=LINE, x0=60, x1=W - 60):
    """地平线：一条带圆头的细纸条。"""
    rr(c, (x0 + x1) / 2, y + 6, x1 - x0, 12, 6, color, alpha)


def stairs(c, x, y, n, step_w, step_h, color, alpha=1.0, lift=0.8, p: float = 1.0):
    """自左下向右上的台阶，(x, y) 为第一级左下角；p 为出现进度（逐级升起）。"""
    with paper(c, alpha, lift):
        for k in range(n):
            q = clamp01(p * n - k)
            if q <= 0:
                continue
            h = step_h * (k + 1) * ease_out_back(q, 1.2)
            c.drawRoundRect(skia.Rect.MakeXYWH(x + k * step_w, y - h, step_w + 1, h), 6, 6,
                            paint(mix(color, PAPER, 0.08 * (n - k))))


def seat(c, x, y, w, h, color, alpha=1.0):
    """方凳 / 箱子：(x, y) 为底边中点。"""
    with paper(c, alpha, 0.7):
        rr(c, x, y - h / 2, w, h, 10, color)
        rr(c, x, y - h + 8, w, 16, 8, tint(color, 0.18))


def road(c, x0, y0, x1, y1, color=LINE, width=60, alpha=1.0, p: float = 1.0, dash_color=PAPER):
    """道路：直线纸条，中间虚线。"""
    if p <= 0:
        return
    xe, ye = lerp(x0, x1, p), lerp(y0, y1, p)
    c.drawLine(x0, y0, xe, ye, paint(color, alpha, width))
    pp = paint(dash_color, alpha, width * 0.08)
    pp.setPathEffect(skia.DashPathEffect.Make([22, 20], 0))
    c.drawLine(x0, y0, xe, ye, pp)


def spotlight(c, x, y, r, color=GOLD, alpha=0.35):
    if alpha <= 0:
        return
    sh = skia.GradientShader.MakeRadial((x, y), r, [col(color, alpha), col(color, 0)], [0, 1])
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=sh))


def bar_chart(c, x, y, w, h, values, colors, p: float = 1.0, labels=(), size=30, vmax=None, alpha=1.0, gap=0.35):
    """柱状图：(x, y) 为底边中点；values 为 0–vmax，p 为生长进度。"""
    n = len(values)
    vmax = vmax or max(values)
    bw = w / (n + (n - 1) * gap)
    with paper(c, alpha, 0.6):
        for i, v in enumerate(values):
            q = ease_out(clamp01(p * n * 0.7 - i * 0.5))
            bh = h * v / vmax * q
            bx = x - w / 2 + i * bw * (1 + gap) + bw / 2
            rr(c, bx, y - bh / 2, bw, max(bh, 0.1), min(12, bw / 4), colors[i % len(colors)])
            if i < len(labels):
                text(c, labels[i], bx, y + size * 0.95, size, "sans_medium", INK2)
