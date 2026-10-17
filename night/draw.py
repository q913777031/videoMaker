"""Skia 绘图基元：缓动、颜色、纸卡与柔和阴影、金属细线、透视、城市剪影、灯光、原创中性人物。

全部为时间的纯函数（随机元素使用固定种子），可多进程逐帧并行渲染。
场景内坐标为 1000×1000 的舞台单位，由渲染器映射到各画幅的舞台区。
"""

import functools
import math
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import skia

from .config import BG, GOLD, WHITE

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
FONTS = {"serif": "NotoSerifCJKsc-Bold.otf", "serif_semi": "NotoSerifCJKsc-SemiBold.otf",
         "sans": "NotoSansCJKsc-Medium.otf", "sans_bold": "NotoSansCJKsc-Bold.otf"}

INK = "#1B1D21"          # 人物衣服
INK_BACK = "#141619"
SKIN = "#A9978A"
HAIR = "#121316"
WALL = "#101114"
FLOOR = "#0C0D0F"
PAPER_DIM = "#3A3631"


# ---------------------------------------------------------------- 缓动

def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def lerp(a, b, x):
    return a + (b - a) * x


def prog(t: float, start: float, dur: float) -> float:
    return clamp01((t - start) / dur) if dur > 0 else float(t >= start)


def ease_out(x: float) -> float:
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in(x: float) -> float:
    return clamp01(x) ** 3


def ease_io(x: float) -> float:
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_back(x: float, s: float = 1.4) -> float:
    x = clamp01(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def pulse(t: float, at: float, dur: float = 0.35) -> float:
    """在 at 时刻瞬间到 1、随后指数回落的撞击包络。"""
    if t < at:
        return 0.0
    return math.exp(-(t - at) / dur * 3.0)


# ---------------------------------------------------------------- 颜色

@functools.lru_cache(maxsize=None)
def rgb(c) -> tuple:
    if isinstance(c, str):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(v) for v in c[:3])


def col(c, a: float = 1.0) -> int:
    r, g, b = rgb(c)
    return skia.Color(r, g, b, int(round(255 * clamp01(a))))


def mix(c1, c2, x: float) -> tuple:
    a, b = rgb(c1), rgb(c2)
    return tuple(int(round(p + (q - p) * clamp01(x))) for p, q in zip(a, b))


def fill(c, a: float = 1.0, blur: float = 0.0) -> skia.Paint:
    p = skia.Paint(Color=col(c, a), AntiAlias=True)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def stroke(c, width: float, a: float = 1.0, cap=skia.Paint.kRound_Cap, dash=None, blur: float = 0.0) -> skia.Paint:
    p = skia.Paint(Color=col(c, a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                   StrokeCap=cap, StrokeJoin=skia.Paint.kRound_Join)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(list(dash[0]), dash[1]))
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


# ---------------------------------------------------------------- 字体

@functools.lru_cache(maxsize=None)
def typeface(name: str) -> skia.Typeface:
    tf = skia.Typeface.MakeFromFile(str(FONT_DIR / FONTS[name]))
    if tf is None:
        raise FileNotFoundError(f"font not found: {FONTS[name]} (run fetch_assets.py)")
    return tf


@functools.lru_cache(maxsize=512)
def font(name: str, size: float) -> skia.Font:
    f = skia.Font(typeface(name), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def text_width(s: str, name: str, size: float) -> float:
    return font(name, size).measureText(s)


def draw_text(c: skia.Canvas, s: str, x: float, y: float, size: float, color=WHITE, a: float = 1.0,
              name: str = "serif", align: str = "center", shadow: bool = True):
    """y 为视觉中线（按 CJK 字面框中心）。"""
    f = font(name, size)
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else x
    base = y + size * 0.36
    if shadow:
        c.drawString(s, x0, base + size * 0.05, f, fill("#000000", 0.75 * a, blur=size * 0.08))
    c.drawString(s, x0, base, f, fill(color, a))


# ---------------------------------------------------------------- 基本形状

def rect(cx, cy, w, h) -> skia.Rect:
    return skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h)


def rrect(cx, cy, w, h, r) -> skia.RRect:
    return skia.RRect.MakeRectXY(rect(cx, cy, w, h), r, r)


def soft_shadow(c, cx, cy, w, h, r=8, lift=1.0, a=0.6):
    """纸卡投影：偏移与模糊随抬升高度 lift 增大。"""
    c.drawRRect(rrect(cx + 6 * lift, cy + 14 * lift, w, h, r), fill("#000000", a, blur=6 + 14 * lift))


def paper(c, cx, cy, w, h, rot=0.0, shade=0.0, lift=1.0, lines=0, mark=None, edge=True, a=1.0,
          line_seed=0, ticks=0):
    """纸卡：柔和投影、暖白纸面（shade 0–1 逐渐变暗）、可选文字行与金色待修改标记。

    mark=(行号, 强度) 时在该行画金色圆圈标记；ticks>0 时在前若干行末画浅色勾。
    """
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * clamp01(a)))
    soft_shadow(c, 0, 0, w, h, r=min(w, h) * 0.05, lift=lift, a=0.55 + 0.25 * shade)
    face = mix(WHITE, PAPER_DIM, shade)
    c.drawRRect(rrect(0, 0, w, h, min(w, h) * 0.05), fill(face))
    # 纸面微弱渐变，模拟顶光
    g = skia.GradientShader.MakeLinear([(0, -h / 2), (0, h / 2)],
                                       [col("#FFFFFF", 0.10 * (1 - shade)), col("#000000", 0.10 + 0.15 * shade)])
    c.drawRRect(rrect(0, 0, w, h, min(w, h) * 0.05), skia.Paint(Shader=g, AntiAlias=True))
    if edge:
        c.drawRRect(rrect(0, 0, w - 1, h - 1, min(w, h) * 0.05), stroke(GOLD, max(1.0, w * 0.004), 0.35 + 0.3 * shade))
    if lines:
        rng = np.random.default_rng(line_seed)
        top, gap = -h / 2 + h * 0.16, (h * 0.72) / max(lines, 1)
        ink = mix("#9A948A", "#5A554F", shade)
        for i in range(lines):
            y = top + i * gap
            ln = w * (0.55 + 0.3 * rng.random()) if i % 3 != 2 else w * 0.35
            c.drawLine(-w * 0.38, y, -w * 0.38 + ln * 0.85, y, stroke(ink, max(1.5, h * 0.012)))
            if i < ticks:
                tx = w * 0.40
                c.drawLine(tx - 6, y - 1, tx - 2, y + 4, stroke("#B9AE94", 2.2, 0.8))
                c.drawLine(tx - 2, y + 4, tx + 7, y - 6, stroke("#B9AE94", 2.2, 0.8))
        if mark is not None:
            i, k = mark
            y = top + i * gap
            c.drawOval(skia.Rect.MakeLTRB(-w * 0.42, y - gap * 0.55, w * 0.18, y + gap * 0.55),
                       stroke(GOLD, max(2.5, w * 0.008), k))
    if a < 1:
        c.restore()
    c.restore()


def mark_card(c, cx, cy, w=130, h=88, rot=0.0, shade=0.0, lift=1.0, a=1.0):
    """白天那张小小的“修改卡”：一行字迹 + 一个金色圆圈标记。整片的核心物体。"""
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * clamp01(a)))
    soft_shadow(c, 0, 0, w, h, r=w * 0.06, lift=lift, a=0.6)
    c.drawRRect(rrect(0, 0, w, h, w * 0.06), fill(mix(WHITE, PAPER_DIM, shade)))
    ink = mix("#9A948A", "#5A554F", shade)
    c.drawLine(-w * 0.34, -h * 0.12, w * 0.26, -h * 0.12, stroke(ink, max(1.5, h * 0.045)))
    c.drawLine(-w * 0.34, h * 0.16, w * 0.06, h * 0.16, stroke(ink, max(1.5, h * 0.045)))
    c.drawOval(skia.Rect.MakeLTRB(-w * 0.42, -h * 0.34, w * 0.36, h * 0.12), stroke(GOLD, max(2.0, w * 0.025)))
    c.drawRRect(rrect(0, 0, w - 1, h - 1, w * 0.06), stroke(GOLD, max(1.0, w * 0.01), 0.4))
    if a < 1:
        c.restore()
    c.restore()


def quad_matrix(w, h, quad) -> skia.Matrix:
    """把以原点为中心的 w×h 矩形映射到四边形 quad（左上、右上、右下、左下），用于桌面透视。"""
    m = skia.Matrix()
    src = [skia.Point(-w / 2, -h / 2), skia.Point(w / 2, -h / 2), skia.Point(w / 2, h / 2), skia.Point(-w / 2, h / 2)]
    m.setPolyToPoly(src, [skia.Point(*p) for p in quad])
    return m


def tilt_quad(cx, cy, w, h, tilt=0.25, scale=1.0):
    """桌面 2.5D 倾斜：上边缩短、整体压扁，模拟俯视斜角。"""
    w, h = w * scale, h * scale
    top, bot = w * (1 - tilt) / 2, w / 2
    hh = h * (1 - tilt * 0.6) / 2
    return [(cx - top, cy - hh), (cx + top, cy - hh), (cx + bot, cy + hh), (cx - bot, cy + hh)]


def glow(c, x, y, r, color=GOLD, a=0.5):
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y), r, [col(color, a), col(color, a * 0.35), col(color, 0)],
                                        [0, 0.35, 1])
    c.drawCircle(x, y, r, skia.Paint(Shader=sh, AntiAlias=True))


def room(c, view, wall=WALL, floor_y=760, warm=(0, 0, 0)):
    """背景墙与地面（覆盖整个可见舞台），warm=(x, y, 强度) 给出暖光照到墙上的位置。"""
    l, t, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t, r, floor_y), fill(wall))
    c.drawRect(skia.Rect.MakeLTRB(l, floor_y, r, b), fill(FLOOR))
    g = skia.GradientShader.MakeLinear([(0, floor_y - 2), (0, floor_y + 60)], [col(GOLD, 0.10), col(GOLD, 0)])
    c.drawRect(skia.Rect.MakeLTRB(l, floor_y - 2, r, floor_y + 60), skia.Paint(Shader=g))
    c.drawLine(l, floor_y, r, floor_y, stroke(GOLD, 1.2, 0.18))
    if warm[2] > 0:
        glow(c, warm[0], warm[1], 620, "#C9A86A", 0.16 * warm[2])


def backdrop(c, view, a=1.0):
    l, t, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t, r, b), fill(BG, a))
    glow(c, 500, 420, 900, "#2A2620", 0.55 * a)


@functools.lru_cache(maxsize=8)
def skyline_rects(seed: int = 7, n: int = 26) -> tuple:
    """城市剪影：(x0, 宽, 高) 序列，x 从 0 到 1 归一化。"""
    rng = np.random.default_rng(seed)
    out, x = [], 0.0
    while x < 1.0:
        w = rng.uniform(0.03, 0.075)
        h = rng.uniform(0.25, 1.0) * (0.55 + 0.45 * math.sin(x * math.pi))
        out.append((x, w, h))
        x += w + rng.uniform(0.002, 0.01)
    return tuple(out)


def skyline_path(x0, base, width, height, seed=7) -> skia.Path:
    p = skia.Path()
    p.moveTo(x0, base)
    for x, w, h in skyline_rects(seed):
        X, Wd, Ht = x0 + x * width, w * width, h * height
        p.lineTo(X, base)
        p.lineTo(X, base - Ht)
        if Wd > width * 0.05:          # 部分楼顶加天线
            p.lineTo(X + Wd * 0.45, base - Ht)
            p.lineTo(X + Wd * 0.45, base - Ht - height * 0.06)
            p.lineTo(X + Wd * 0.52, base - Ht - height * 0.06)
            p.lineTo(X + Wd * 0.52, base - Ht)
        p.lineTo(X + Wd, base - Ht)
        p.lineTo(X + Wd, base)
    p.lineTo(x0 + width, base)
    p.close()
    return p


def ellipse_path(cx, cy, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def lamp(c, x, y_table, on=1.0):
    """床头小台灯：灯罩、灯杆、桌面，on 控制亮度。返回光源点。"""
    c.drawRect(skia.Rect.MakeLTRB(x - 70, y_table, x + 70, y_table + 120), fill("#15161A"))
    c.drawLine(x - 70, y_table, x + 70, y_table, stroke(GOLD, 1.5, 0.4))
    c.drawLine(x, y_table, x, y_table - 90, stroke("#3B3832", 4))
    sx, sy = x, y_table - 110
    shade = skia.Path()
    shade.moveTo(sx - 26, sy - 22)
    shade.lineTo(sx + 26, sy - 22)
    shade.lineTo(sx + 44, sy + 22)
    shade.lineTo(sx - 44, sy + 22)
    shade.close()
    c.drawPath(shade, fill(mix("#3A352C", "#E8D2A0", on)))
    if on > 0:
        glow(c, sx, sy + 26, 260, "#E8C987", 0.55 * on)
        glow(c, sx, sy + 26, 70, "#FFF1D2", 0.6 * on)
    return sx, sy + 20


def bed(c, x0, x1, top):
    """床：深色床体 + 金色细边，枕头。"""
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, top, x1, top + 70), 14, 14), fill("#1A1B1F"))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 6, top + 70, x1 - 6, top + 120), fill("#111215"))
    c.drawLine(x0 + 10, top + 2, x1 - 10, top + 2, stroke(GOLD, 1.5, 0.35))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0 + 20, top - 34, x0 + 150, top + 6), 18, 18), fill("#24252A"))


# ---------------------------------------------------------------- 人物

@dataclass(frozen=True)
class Pose:
    """关节角（度）：躯干前倾、头部前低；肩角从竖直向下量起、向前为正；肘/膝为相对弯曲。"""
    torso: float = 3
    head: float = 6
    sa_f: float = 6
    ea_f: float = 8
    sa_b: float = -4
    ea_b: float = 6
    ha_f: float = 2
    ka_f: float = -2
    ha_b: float = -2
    ka_b: float = -2


STAND = Pose()
SIT = Pose(torso=24, head=22, sa_f=38, ea_f=52, sa_b=30, ea_b=56, ha_f=86, ka_f=-84, ha_b=82, ka_b=-82)
SIT_EASE = Pose(torso=10, head=8, sa_f=30, ea_f=44, sa_b=22, ea_b=40, ha_f=86, ka_f=-84, ha_b=82, ka_b=-82)
HOLD = Pose(torso=4, head=16, sa_f=28, ea_f=62, sa_b=22, ea_b=66)
LOWER = Pose(torso=16, head=18, sa_f=48, ea_f=12, sa_b=40, ea_b=16)
REACH = Pose(torso=6, head=10, sa_f=62, ea_f=18, sa_b=-2, ea_b=8)
SLUMP = Pose(torso=12, head=26, sa_f=10, ea_f=6, sa_b=4, ea_b=6)


def blend(a: Pose, b: Pose, x: float) -> Pose:
    x = clamp01(x)
    return Pose(*[lerp(getattr(a, k), getattr(b, k), x) for k in Pose.__dataclass_fields__])


def walk(phase: float, base: Pose = STAND) -> Pose:
    s = math.sin(phase)
    return replace(base, torso=base.torso + 3, ha_f=24 * s, ka_f=-18 * max(0, -s) - 4,
                   ha_b=-24 * s, ka_b=-18 * max(0, s) - 4, sa_f=-18 * s, ea_f=14, sa_b=18 * s, ea_b=14)


SEG = {"torso": 150, "neck": 18, "head": 31, "ua": 72, "fa": 66, "th": 92, "sh": 94}


def _down(p, ang, L, facing):
    a = math.radians(ang)
    return p[0] + facing * L * math.sin(a), p[1] + L * math.cos(a)


def figure_joints(x, y, pose: Pose, facing=1, scale=1.0) -> dict:
    """计算关节点（hip=(x, y)），供绘制与道具挂接（如双手位置）。"""
    S = {k: v * scale for k, v in SEG.items()}
    hip = (x, y)
    ta = math.radians(pose.torso)
    sh = (x + facing * S["torso"] * math.sin(ta), y - S["torso"] * math.cos(ta))
    ha = math.radians(pose.torso + pose.head)
    neck = (sh[0] + facing * S["neck"] * math.sin(ha), sh[1] - S["neck"] * math.cos(ha))
    head = (neck[0] + facing * S["head"] * math.sin(ha), neck[1] - S["head"] * math.cos(ha))
    j = {"hip": hip, "sh": sh, "neck": neck, "head": head, "S": S}
    for side in ("f", "b"):
        sa, ea = getattr(pose, "sa_" + side), getattr(pose, "ea_" + side)
        el = _down(sh, sa, S["ua"], facing)
        hd = _down(el, sa + ea, S["fa"], facing)
        hp, kp = getattr(pose, "ha_" + side), getattr(pose, "ka_" + side)
        kn = _down(hip, hp, S["th"], facing)
        ft = _down(kn, hp + kp, S["sh"], facing)
        j["el_" + side], j["hand_" + side], j["kn_" + side], j["ft_" + side] = el, hd, kn, ft
    return j


def figure(c, x, y, pose: Pose, facing=1, scale=1.0, a=1.0, rim=0.5):
    """原创中性上班族：深色衣服、短发、无面部细节；领口一道金色识别线。rim 为边缘暖光强度。"""
    j = figure_joints(x, y, pose, facing, scale)
    S = j["S"]
    if a < 1:
        c.saveLayerAlpha(None, int(255 * clamp01(a)))
    lw, aw, tw = 30 * scale, 22 * scale, 58 * scale

    def limb(p0, p1, p2, w, color):
        path = skia.Path()
        path.moveTo(*p0)
        path.lineTo(*p1)
        path.lineTo(*p2)
        c.drawPath(path, stroke(color, w))
        if rim > 0:
            c.drawPath(path, stroke(GOLD, max(1.0, 1.4 * scale), 0.12 * rim))

    limb(j["hip"], j["kn_b"], j["ft_b"], lw, INK_BACK)
    c.drawOval(rect(j["ft_b"][0] + facing * 10 * scale, j["ft_b"][1] + 2 * scale, 36 * scale, 14 * scale), fill("#0E0F11"))
    limb(j["sh"], j["el_b"], j["hand_b"], aw, INK_BACK)
    c.drawCircle(*j["hand_b"], 9 * scale, fill(mix(SKIN, "#000000", 0.25)))
    # 躯干
    torso = skia.Path()
    torso.moveTo(*j["hip"])
    torso.lineTo(*j["sh"])
    c.drawPath(torso, stroke(INK, tw))
    c.drawPath(torso, stroke(GOLD, max(1.0, 1.5 * scale), 0.14 * rim))
    limb(j["hip"], j["kn_f"], j["ft_f"], lw, INK)
    c.drawOval(rect(j["ft_f"][0] + facing * 10 * scale, j["ft_f"][1] + 2 * scale, 38 * scale, 15 * scale), fill("#0E0F11"))
    # 颈、头、头发
    c.drawLine(*j["sh"], *j["neck"], stroke(mix(SKIN, "#000000", 0.2), 18 * scale))
    hx, hy = j["head"]
    r = S["head"]
    c.drawCircle(hx, hy, r, fill(SKIN))
    ha = math.radians(pose.torso + pose.head)
    front = math.degrees(math.atan2(math.sin(ha), facing * math.cos(ha)))
    hair = skia.Path()
    hair.addArc(skia.Rect.MakeLTRB(hx - r * 1.06, hy - r * 1.06, hx + r * 1.06, hy + r * 1.06),
                front - facing * 20, -facing * 225)
    hair.close()
    c.drawPath(hair, fill(HAIR))
    c.drawCircle(hx, hy, r, stroke(GOLD, max(1.0, 1.2 * scale), 0.15 * rim))
    # 领口金色识别线：沿肩部的一道短弧
    ux, uy = math.sin(ha) * facing, -math.cos(ha)
    px, py = -uy, ux
    cx_, cy_ = j["sh"][0] - ux * 8 * scale, j["sh"][1] - uy * 8 * scale
    c.drawLine(cx_ - px * 22 * scale, cy_ - py * 22 * scale, cx_ + px * 22 * scale, cy_ + py * 22 * scale,
               stroke(GOLD, 3.2 * scale, 0.95))
    limb(j["sh"], j["el_f"], j["hand_f"], aw, INK)
    c.drawCircle(*j["hand_f"], 9.5 * scale, fill(SKIN))
    if a < 1:
        c.restore()
    return j


def floor_shadow(c, x, y, w, a=0.5):
    c.drawOval(rect(x, y, w, w * 0.16), fill("#000000", a, blur=10))


def sparks(c, x, y, t, t0, n=14, r=120, seed=3, color=GOLD):
    """局部金色粒子（只在撞击点附近、短时出现）。"""
    k = t - t0
    if k < 0 or k > 1.2:
        return
    rng = np.random.default_rng(seed)
    for _ in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        sp = rng.uniform(0.5, 1.0)
        d = r * sp * ease_out(k / 1.0)
        a = (1 - k / 1.2) * rng.uniform(0.4, 0.9)
        c.drawCircle(x + d * math.cos(ang), y + d * math.sin(ang) * 0.8, rng.uniform(1.5, 3.2), fill(color, a))
