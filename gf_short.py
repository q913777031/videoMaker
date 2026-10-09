"""《轮盘连开十次黑,下一把押红吗?》赌徒谬误竖屏知识短视频(无声版)。

按 scripts/gamblers_fallacy.md 的 14 镜分镜固定排时(共 108 秒),只输出画面与屏幕文字:
不含配音、配乐、音效,也不烧录口播字幕;口播字幕按估算时间另存为同名 .srt,供后期配音对位。
画面全部为矢量绘制的复古插画风格,1913 年相关镜头带"情景再现"角标。

用法:python3 gf_short.py [输出路径]       生成视频、字幕与封面
依赖资源:python3 fetch_assets.py(只需字体)
"""

import math
import sys
from pathlib import Path

import numpy as np
import skia

from engine.gfx import (W, H, circle, clamp01, col, draw_kinetic, draw_rich, draw_text, ease_in_out,
                        ease_out, ease_out_back, lerp, plain, prog, rrect, stroke_path)
from engine.timeline import Line, Scene, Video

GOLD, CREAM, INK = "#E8B04A", "#F3E3C3", "#1A1210"
RED, BLK, GREEN = "#C8302C", "#17120F", "#2E7D4F"
WOOD, WOOD_D, FELT = "#7A4320", "#3E200E", "#1E4A33"

TITLE = dict(stroke=("#1A0E06", 12), shadow=(0, 8, 14, "#000000"), gradient=["#FFF4D6", "#F2C14E"])
TXT = dict(stroke=("#0B0705", 9), shadow=(0, 5, 8, "#000000"))

PALETTES = {
    "casino": dict(bg=["#0B0806", "#1C130C", "#2B1B10"], blobs=["#8A5A1E", "#5A2A12", "#6E4A18"],
                   dust="#F5C46A", hi="#F2C14E", aurora=0.22, vignette=0.7, dust_a=0.35, dust_n=26),
    "felt": dict(bg=["#07110C", "#0F2419", "#173726"], blobs=["#2E6B45", "#7A5A1E", "#1E4A35"],
                 dust="#F5C46A", hi="#F2C14E", aurora=0.2, vignette=0.65, dust_a=0.3, dust_n=22),
    "dark": dict(bg=["#030303", "#07060A", "#0D0A08"], blobs=["#2A1C0C", "#120C08", "#1E140A"],
                 dust="#F5C46A", hi="#F2C14E", aurora=0.08, vignette=0.85, dust_a=0.15, dust_n=12),
    "coin": dict(bg=["#090E0B", "#112019", "#1A2C22"], blobs=["#6A5520", "#2A4A3A", "#4A3A15"],
                 dust="#F5C46A", hi="#F2C14E", aurora=0.2, vignette=0.6, dust_a=0.3, dust_n=22),
}


# ---------------------------------------------------------------- 通用

def w(x, i: int, word: str) -> float:
    """第 i 句读到 word 的估计时刻。"""
    idx = plain(x.s.lines[i].text).find(word)
    if idx < 0:
        raise ValueError(f"'{word}' not in line {i} of scene {x.s.name}")
    return x.at(i, idx)


def fade(t: float, start: float, end: float | None = None, dur: float = 0.35) -> float:
    a = prog(t, start, dur)
    if end is not None:
        a *= 1 - prog(t, end, 0.3)
    return a


def tag(x, text: str = "情景再现"):
    """右上角情景再现角标。"""
    a = fade(x.t, 0.2) * (1 - prog(x.t, x.dur - 0.3, 0.3))
    rrect(x.c, W - 150, 110, 210, 60, 30, "#000000", 0.45 * a, stroke=(GOLD, 2))
    draw_text(x.c, text, W - 150, 110, 30, "bold", CREAM, a)


def paint(color, a: float = 1.0, stroke: float = 0.0, blur: float = 0.0) -> skia.Paint:
    p = skia.Paint(AntiAlias=True, Color=col(color, a))
    if stroke > 0:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def radial(cx, cy, r, colors, stops=None, a: float = 1.0) -> skia.Paint:
    return skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (cx, cy), r, [col(k, a) for k in colors], stops))


def spotlight(x, cx: float, cy: float, r: float, color="#F2C14E", a: float = 0.35):
    """背景层聚光(在 1/4 分辨率背景画布上调用)。"""
    x.c.drawCircle(cx, cy, r, radial(cx, cy, r, [color, "#00000000"], [0, 1], a))


# ---------------------------------------------------------------- 轮盘、记分牌、筹码、硬币

N_POCKET = 37


def pocket_color(k: int) -> str:
    return GREEN if k == 0 else RED if k % 2 else BLK


def pocket_angle(k: int, rot: float) -> float:
    return rot + (k + 0.5) * 360 / N_POCKET


def wheel(c, cx, cy, R, rot, ball=None, alpha: float = 1.0, squash: float = 1.0):
    """俯视轮盘:木质外框、37 格(1 绿 + 红黑交替)、中心转塔;ball=(角度, 半径比例) 时画小球。"""
    if alpha <= 0:
        return
    c.save()
    c.translate(cx, cy)
    c.scale(1, squash)
    c.drawCircle(0, 18, R * 1.02, paint("#000000", 0.5 * alpha, blur=26))
    c.drawCircle(0, 0, R, radial(0, 0, R, ["#9A5A2C", WOOD, WOOD_D], [0.55, 0.85, 1], alpha))
    c.drawCircle(0, 0, R * 0.97, paint(GOLD, 0.8 * alpha, stroke=4))
    c.drawCircle(0, 0, R * 0.88, paint("#2A160A", alpha))
    r1, r2 = R * 0.6, R * 0.84
    o1, o2 = skia.Rect.MakeLTRB(-r1, -r1, r1, r1), skia.Rect.MakeLTRB(-r2, -r2, r2, r2)
    sweep = 360 / N_POCKET
    for k in range(N_POCKET):
        a0 = rot + k * sweep
        p = skia.Path()
        p.arcTo(o2, a0, sweep, True)
        p.arcTo(o1, a0 + sweep, -sweep, False)
        p.close()
        c.drawPath(p, paint(pocket_color(k), alpha))
    sep = paint(GOLD, 0.75 * alpha, stroke=2.2)
    for k in range(N_POCKET):
        a = math.radians(rot + k * sweep)
        c.drawLine(r1 * math.cos(a), r1 * math.sin(a), r2 * math.cos(a), r2 * math.sin(a), sep)
    c.drawCircle(0, 0, r2, paint(GOLD, 0.7 * alpha, stroke=3))
    c.drawCircle(0, 0, r1, paint(GOLD, 0.9 * alpha, stroke=4))
    c.drawCircle(0, 0, r1 * 0.98, radial(0, -r1 * 0.3, r1, ["#B87A3A", "#6B3A18", "#3A1E0C"], [0, 0.6, 1], alpha))
    for k in range(8):
        a = math.radians(rot * 1.0 + k * 45)
        c.drawLine(r1 * 0.18 * math.cos(a), r1 * 0.18 * math.sin(a), r1 * 0.8 * math.cos(a),
                   r1 * 0.8 * math.sin(a), paint("#2A160A", 0.5 * alpha, stroke=3))
    c.save()
    c.rotate(rot * 1.0)
    for k in range(4):
        c.rotate(90)
        c.drawRoundRect(skia.Rect.MakeLTRB(-6, -r1 * 0.42, 6, 0), 6, 6, radial(0, -r1 * 0.2, r1 * 0.4,
                        ["#FFE7A8", GOLD, "#8A5A1E"], None, alpha))
        c.drawCircle(0, -r1 * 0.42, 12, paint("#FFE7A8", alpha))
    c.restore()
    c.drawCircle(0, 0, r1 * 0.14, radial(-6, -6, r1 * 0.16, ["#FFF1C8", GOLD, "#7A4A12"], None, alpha))
    if ball is not None:
        ang, rr = ball
        a = math.radians(ang)
        bx, by = R * rr * math.cos(a), R * rr * math.sin(a)
        c.drawCircle(bx + 4, by + 6, R * 0.04, paint("#000000", 0.5 * alpha, blur=5))
        c.drawCircle(bx, by, R * 0.038, radial(bx - R * 0.012, by - R * 0.012, R * 0.05,
                                               ["#FFFFFF", "#E8E2D6", "#9A928A"], None, alpha))
    c.restore()


def spin(t: float, t0: float, t_land: float, rot0: float, speed: float, k: int):
    """一次开球:轮盘匀减速转动,小球反向绕行并在 t_land 落入第 k 格。返回 (轮盘角, 小球)。"""
    dur = t_land - t0 + 2.5
    p = clamp01((t - t0) / dur)
    rot = rot0 + speed * dur * (p - p * p / 2) if t >= t0 else rot0
    if t < t0:
        return rot, None
    target = pocket_angle(k, rot)
    q = clamp01((t - t0) / max(t_land - t0, 0.01))
    if q < 1:
        off = -(1 - ease_out(q)) * 900
        rr = lerp(0.93, 0.72, ease_in_out(clamp01((q - 0.55) / 0.45)))
        rr += 0.03 * math.sin(q * 40) * clamp01((q - 0.7) / 0.3) * (1 - q) * 3
        return rot, (target + off, rr)
    return rot, (target, 0.72)


def black_pocket(n: int) -> int:
    """第 n 个黑格(偶数、非 0)的下标。"""
    return 2 + 2 * (n % 18)


def dot(c, x, y, r, color, alpha=1.0, glow=0.0):
    if alpha <= 0:
        return
    if glow > 0:
        c.drawCircle(x, y, r * 1.6, paint(GOLD, glow * alpha, blur=r * 0.8))
    c.drawCircle(x, y + 3, r, paint("#000000", 0.4 * alpha, blur=4))
    c.drawCircle(x, y, r, radial(x - r * 0.3, y - r * 0.3, r * 1.3,
                                 ["#5A4A40" if color == BLK else "#F06A5A", color], None, alpha))
    c.drawCircle(x, y, r, paint(GOLD, alpha, stroke=4))
    c.drawCircle(x - r * 0.35, y - r * 0.38, r * 0.22, paint("#FFFFFF", 0.55 * alpha, blur=r * 0.08))


def board(c, x, y0, step, r, lit_times, t, slots: int, alpha: float = 1.0):
    """竖排记分灯:lit_times[i] 为第 i 个黑点亮起的时刻;未亮的位置画暗槽。"""
    slot = paint(GOLD, 0.22 * alpha, stroke=2)
    slot.setPathEffect(skia.DashPathEffect.Make([5, 5], 0))
    for i in range(slots):
        y = y0 + i * step
        c.drawCircle(x, y, r * 0.8, slot)
        if i < len(lit_times) and t >= lit_times[i]:
            p = prog(t, lit_times[i], 0.3)
            c.save()
            c.translate(x, y)
            s = ease_out_back(p, 2.5)
            c.scale(s, s)
            dot(c, 0, 0, r, BLK, alpha, glow=0.6 * (1 - prog(t, lit_times[i] + 0.3, 0.6)))
            c.restore()


def chip_top(c, x, y, r, color, alpha=1.0):
    """俯视筹码:彩色圆盘、白色边纹、金色内圈。"""
    c.drawCircle(x + 3, y + 5, r, paint("#000000", 0.45 * alpha, blur=5))
    c.drawCircle(x, y, r, paint(color, alpha))
    stripes = paint("#F3E3C3", alpha, stroke=r * 0.22)
    stripes.setPathEffect(skia.DashPathEffect.Make([r * 0.35, r * 0.45], 0))
    c.drawCircle(x, y, r * 0.86, stripes)
    c.drawCircle(x, y, r * 0.58, paint(GOLD, alpha, stroke=3))


def chip_stack(c, x, y, r, n, color, alpha=1.0):
    """侧俯视的一摞筹码(椭圆叠放)。"""
    for k in range(n):
        yy = y - k * r * 0.22
        rect = skia.Rect.MakeLTRB(x - r, yy - r * 0.42, x + r, yy + r * 0.42)
        c.drawOval(rect.makeOffset(0, r * 0.12), paint("#00000080" if k == 0 else "#000000", 0.35 * alpha))
        c.drawOval(rect, paint(color, alpha))
        c.drawOval(rect, paint(CREAM, 0.7 * alpha, stroke=2))
    top = y - (n - 1) * r * 0.22
    c.drawOval(skia.Rect.MakeLTRB(x - r * 0.6, top - r * 0.25, x + r * 0.6, top + r * 0.25),
               paint(GOLD, alpha, stroke=2.5))


def star_path(cx, cy, r) -> skia.Path:
    p = skia.Path()
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.42
        a = math.radians(-90 + k * 36)
        (p.lineTo if k else p.moveTo)(cx + rr * math.cos(a), cy + rr * math.sin(a))
    p.close()
    return p


def moon_path(cx, cy, r) -> skia.Path:
    a, b = skia.Path(), skia.Path()
    a.addCircle(cx, cy, r)
    b.addCircle(cx + r * 0.45, cy - r * 0.2, r * 0.85)
    return skia.Op(a, b, skia.PathOp.kDifference_PathOp)


def coin(c, x, y, r, face: str = "star", alpha=1.0, flip: float = 1.0, dim: float = 0.0):
    """金币;face 为 star(正面)/ moon(反面);flip 为横向压缩(-1..1,翻转动画)。"""
    if alpha <= 0 or r <= 0:
        return
    c.save()
    c.translate(x, y)
    c.drawCircle(4, 8, r, paint("#000000", 0.45 * alpha, blur=r * 0.12))
    c.scale(max(abs(flip), 0.04), 1)
    gold = ["#FFF1C0", "#E8B04A", "#9A6A1E"] if dim == 0 else ["#BFAF88", "#8A7444", "#5A4420"]
    c.drawCircle(0, 0, r, radial(-r * 0.35, -r * 0.35, r * 1.6, gold, [0, 0.55, 1], alpha))
    c.drawCircle(0, 0, r * 0.95, paint("#7A4A12", 0.8 * alpha, stroke=max(2, r * 0.05)))
    c.drawCircle(0, 0, r * 0.78, paint("#7A4A12", 0.5 * alpha, stroke=max(1.5, r * 0.025)))
    sym = star_path(0, 0, r * 0.48) if face == "star" else moon_path(-r * 0.1, 0, r * 0.42)
    c.drawPath(sym, paint("#7A4A12", 0.9 * alpha))
    c.restore()


def gentleman(c, x, y, s, alpha=1.0, rim=0.8):
    """戴礼帽绅士的侧背影剪影,带暖金轮廓光;(x, y) 为头部中心。"""
    body = skia.Path()
    body.moveTo(x - 260 * s, y + 620 * s)
    body.cubicTo(x - 250 * s, y + 260 * s, x - 170 * s, y + 140 * s, x - 40 * s, y + 120 * s)
    body.lineTo(x + 60 * s, y + 120 * s)
    body.cubicTo(x + 200 * s, y + 140 * s, x + 270 * s, y + 260 * s, x + 280 * s, y + 620 * s)
    body.close()
    neck = skia.Rect.MakeLTRB(x - 45 * s, y + 40 * s, x + 50 * s, y + 140 * s)
    hat = skia.Path()
    hat.addRoundRect(skia.Rect.MakeLTRB(x - 85 * s, y - 250 * s, x + 85 * s, y - 70 * s), 14 * s, 14 * s)
    brim = skia.Rect.MakeLTRB(x - 150 * s, y - 95 * s, x + 150 * s, y - 50 * s)
    fill = paint("#120B07", alpha)
    for p in (body,):
        c.drawPath(p, paint(GOLD, rim * 0.5 * alpha, stroke=10 * s, blur=8 * s))
    c.drawCircle(x, y, 110 * s, paint(GOLD, rim * 0.5 * alpha, stroke=10 * s, blur=8 * s))
    c.drawPath(body, fill)
    c.drawRect(neck, fill)
    c.drawCircle(x, y, 110 * s, fill)
    c.drawPath(hat, paint(GOLD, rim * 0.5 * alpha, stroke=8 * s, blur=7 * s))
    c.drawPath(hat, fill)
    c.drawOval(brim, fill)
    c.drawRect(skia.Rect.MakeLTRB(x - 85 * s, y - 115 * s, x + 85 * s, y - 85 * s), paint("#4A1A12", alpha))
    c.drawCircle(x + 112 * s, y + 10 * s, 18 * s, fill)


def head(c, x, y, s, alpha=1.0, hat=False):
    """小人头肩剪影。"""
    c.drawCircle(x, y, 44 * s, paint("#120B07", alpha))
    c.drawCircle(x, y, 44 * s, paint(GOLD, 0.35 * alpha, stroke=3))
    sh = skia.Path()
    sh.addRoundRect(skia.Rect.MakeLTRB(x - 85 * s, y + 50 * s, x + 85 * s, y + 220 * s), 70 * s, 70 * s)
    c.drawPath(sh, paint("#120B07", alpha))
    c.drawPath(sh, paint(GOLD, 0.3 * alpha, stroke=3))
    if hat:
        c.drawRoundRect(skia.Rect.MakeLTRB(x - 34 * s, y - 100 * s, x + 34 * s, y - 30 * s), 6, 6,
                        paint("#120B07", alpha))
        c.drawOval(skia.Rect.MakeLTRB(x - 62 * s, y - 42 * s, x + 62 * s, y - 24 * s), paint("#120B07", alpha))


def two_lines(c, a: str, b: str, y: float, size: float, t: float, start: float, gap: float = 1.25,
              alpha: float = 1.0, style: str = "pop", name: str = "title", **kw):
    draw_kinetic(c, a, W / 2, y, size, t, start, name, style, alpha=alpha, **kw)
    draw_kinetic(c, b, W / 2, y + size * gap, size, t, start + 0.25, name, style, alpha=alpha, **kw)


def title_style(**over):
    st = dict(TITLE)
    st.update(over)
    return st


# ---------------------------------------------------------------- 镜 1:开场问题

def s01(x):
    c, t = x.c, x.t
    out = ease_in_out(prog(t, x.dur - 0.7, 0.7))
    c.save()
    c.translate(W / 2, 1060)
    c.scale(1 - 0.2 * out, 1 - 0.2 * out)
    c.translate(-W / 2, -1060 - 140 * out)
    rot, ball = spin(t, -2.0, 1.5, 20, 160, black_pocket(4))
    wheel(c, 450, 1080, 360, rot, ball)
    board(c, 975, 640, 88, 30, [0.35 + i * 0.2 for i in range(10)], t, 10)
    c.restore()
    a = 1 - prog(t, x.dur - 0.25, 0.25)
    draw_kinetic(c, "轮盘连开【10次】黑", W / 2, 300, 118, t, 0.05, "title", "slam", 0.05, alpha=a,
                 hi="#FF5A4A", **TITLE)
    draw_kinetic(c, "下一把你押红吗？", W / 2, 450, 118, t, 0.55, "title", "pop", 0.05, alpha=a, **TITLE)


def s01_bg(x):
    spotlight(x, 450, 1080, 620, a=0.35)
    spotlight(x, 540, 360, 520, a=0.18)


# ---------------------------------------------------------------- 镜 2:1913 赌场大厅

def s02(x):
    c, t = x.c, x.t
    push = 1 + 0.22 * ease_in_out(t / x.dur)
    c.save()
    c.translate(W / 2, 1250)
    c.scale(push, push)
    c.translate(-W / 2, -1250)
    for k, ax in enumerate((150, 410, 670, 930)):
        arch = skia.Path()
        arch.addRoundRect(skia.Rect.MakeLTRB(ax - 105, 520, ax + 105, 1180), 105, 105)
        c.drawPath(arch, paint("#2A1A10", 0.75))
        c.drawPath(arch, paint(GOLD, 0.35, stroke=4))
        for j in range(3):
            c.drawLine(ax - 90, 700 + j * 150, ax + 90, 700 + j * 150, paint(GOLD, 0.12, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, 1200), paint(GOLD, 0.4))
    cx, cy = 540, 360
    stroke_path(c, _line(cx, 0, cx, cy - 60), GOLD, 4, 0.8)
    for k in range(7):
        a = math.radians(-180 + k * 30)
        px, py = cx + 190 * math.cos(a), cy + 80 + 60 * math.sin(a) * -1
        stroke_path(c, _line(cx, cy - 40, px, py), GOLD, 3, 0.6)
        flick = 0.85 + 0.15 * math.sin(t * 7 + k * 1.7)
        circle(c, px, py, 30, "#FFD27A", 0.5 * flick, blur=18, blend=skia.BlendMode.kPlus)
        circle(c, px, py, 9, "#FFF3C8", flick)
    circle(c, cx, cy, 30, GOLD)
    cone = skia.Path()
    cone.moveTo(cx - 60, cy + 40)
    cone.lineTo(cx + 60, cy + 40)
    cone.lineTo(cx + 420, 1330)
    cone.lineTo(cx - 420, 1330)
    cone.close()
    cp = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, cy), (0, 1330)], [col("#FFD27A", 0.0), col("#FFD27A", 0.22)]))
    c.drawPath(cone, cp)
    for k, (hx, hy, hs, hat) in enumerate(((140, 1180, 1.0, True), (300, 1150, 0.85, False),
                                          (780, 1150, 0.85, True), (950, 1180, 1.0, False))):
        head(c, hx, hy, hs, 0.95, hat)
    table = skia.Rect.MakeLTRB(150, 1250, 930, 1520)
    c.drawOval(table.makeOffset(0, 30), paint("#000000", 0.6, blur=20))
    c.drawOval(table, paint(WOOD_D))
    c.drawOval(skia.Rect.MakeLTRB(175, 1262, 905, 1500), paint(FELT))
    c.drawOval(skia.Rect.MakeLTRB(175, 1262, 905, 1500), paint(GOLD, 0.6, stroke=3))
    rot = t * 40
    wheel(c, 540, 1380, 150, rot, (rot * -2.3, 0.9), squash=0.42)
    for k, (hx, hy, hs) in enumerate(((210, 1600, 1.3), (870, 1610, 1.3))):
        head(c, hx, hy, hs, 1.0, k == 0)
    c.restore()
    draw_kinetic(c, "1913年8月18日", W / 2, 300, 104, t, 0.25, "title", "rise", 0.04, **TITLE)
    draw_kinetic(c, "蒙特卡洛赌场", W / 2, 430, 72, t, w(x, 0, "蒙特卡洛"), "black", "rise", 0.05,
                 fill=CREAM, **TXT)
    tag(x)


def s02_bg(x):
    spotlight(x, 540, 380, 700, "#FFC864", 0.4)
    spotlight(x, 540, 1380, 650, "#FFC864", 0.3)


def _line(x0, y0, x1, y1) -> skia.Path:
    p = skia.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y1)
    return p


# ---------------------------------------------------------------- 镜 3:黑色越排越长

def s03(x):
    c, t = x.c, x.t
    l1 = w(x, 0, "落进黑格")
    l2 = w(x, 0, "还是黑")
    l3 = w(x, 0, "越排越长")
    if t < 2.6:
        rot, ball = spin(t, -1.5, l1, 30, 150, black_pocket(11))
    else:
        rot, ball = spin(t, 2.6 - 1.0, l2, 170, 150, black_pocket(12))
    wheel(c, 400, 1080, 330, rot, ball)
    rrect(c, 930, 1000, 150, 1160, 24, gradient=["#5A3218", "#3A1E0C"], shadow=0.5, stroke=(GOLD, 4))
    lit = [-1] * 10 + [l1 + 0.05, l2 + 0.05, l3]
    board(c, 930, 470, 82, 28, lit, t, 13)
    n = 10 + sum(t >= v for v in lit[10:])
    p = prog(t, max([v for v in lit if t >= v] or [0]), 0.35)
    c.save()
    c.translate(930, 300)
    s = 1 + 0.35 * (1 - ease_out(p)) if n > 10 else 1
    c.scale(s, s)
    draw_text(c, str(n), 0, 0, 120, "title", "#FFFFFF", 1, stroke=("#1A0E06", 12), gradient=["#FFF4D6", "#F2C14E"],
              shadow=(0, 8, 14, "#000000"))
    c.restore()
    draw_text(c, "连续黑色", 930, 395, 34, "bold", CREAM, 0.9)
    tag(x)


def s03_bg(x):
    spotlight(x, 400, 1080, 560, a=0.32)
    spotlight(x, 930, 900, 420, a=0.15)


# ---------------------------------------------------------------- 镜 4:心理独白

def s04(x):
    c, t = x.c, x.t
    for i in range(13):
        dot(c, 900 + (i % 2) * 70, 260 + (i // 2) * 70, 24, BLK, 0.45)
    gentleman(c, 330, 1180, 1.25, rim=0.9)
    tap = abs(math.sin(t * 9)) * 18 * (1 - prog(t, x.cue(1), 0.3))
    c.drawRect(skia.Rect.MakeLTRB(0, 1700, W, H), paint(WOOD_D))
    c.drawRect(skia.Rect.MakeLTRB(0, 1690, W, 1705), paint(GOLD, 0.6))
    c.drawRoundRect(skia.Rect.MakeLTRB(860, 1630 - tap, 960, 1700 - tap), 30, 30, paint("#2A1A12"))
    c.drawRoundRect(skia.Rect.MakeLTRB(780, 1610, 900, 1700), 20, 20, paint("#F3E3C3", 0.9))
    st = x.cue(0) + 0.4
    for k, (bx, by, br) in enumerate(((560, 980, 18), (610, 900, 28))):
        a = fade(t, st + k * 0.15)
        circle(c, bx, by, br, CREAM, a)
    p = ease_out_back(prog(t, st + 0.35, 0.45), 1.8)
    if p > 0:
        c.save()
        c.translate(780, 700)
        c.scale(p, p)
        for bx, by, br in ((-150, 0, 120), (-40, -70, 135), (100, -30, 130), (150, 70, 105), (-10, 80, 120),
                           (-140, 90, 90)):
            circle(c, bx, by, br + 6, "#000000", 0.25, blur=12)
        for bx, by, br in ((-150, 0, 120), (-40, -70, 135), (100, -30, 130), (150, 70, 105), (-10, 80, 120),
                           (-140, 90, 90)):
            circle(c, bx, by, br, CREAM)
        pulse = 1 + 0.08 * math.sin(t * 6)
        dot(c, 0, 10, 70 * pulse, RED, 1, glow=0.4)
        c.restore()
    q0 = x.cue(1)
    draw_kinetic(c, "“都这么多次黑了，", W / 2, 1420, 70, t, q0, "title", "rise", 0.03, **TITLE)
    draw_kinetic(c, "总该轮到【红】了吧？”", W / 2, 1515, 70, t, q0 + 0.6, "title", "rise", 0.03,
                 hi="#FF5A4A", **TITLE)
    draw_text(c, "情境化独白", W / 2, 1595, 32, "bold", CREAM, 0.75 * fade(t, q0 + 1.2))
    tag(x)


def s04_bg(x):
    spotlight(x, 780, 700, 520, a=0.25)
    spotlight(x, 330, 1300, 600, a=0.2)


# ---------------------------------------------------------------- 镜 5:筹码推向红色

def s05(x):
    c, t = x.c, x.t
    pan = -60 * ease_in_out(t / x.dur)
    c.save()
    c.translate(pan, 0)
    c.drawRect(skia.Rect.MakeLTRB(-100, 0, W + 200, H), paint(FELT))
    red = skia.Rect.MakeLTRB(120, 420, 1020, 1000)
    blk = skia.Rect.MakeLTRB(120, 1060, 1020, 1640)
    for r, color in ((red, RED), (blk, BLK)):
        c.drawRoundRect(r, 24, 24, paint(color, 0.92))
        c.drawRoundRect(r, 24, 24, paint(GOLD, 0.9, stroke=6))
        c.drawRoundRect(r.makeInset(18, 18), 14, 14, paint(GOLD, 0.35, stroke=2))
    stacks = ((330, 640), (560, 700), (790, 620), (430, 860), (690, 880))
    for k, (sx, sy) in enumerate(stacks):
        st = x.cue(0) + k * 0.45
        p = ease_out(prog(t, st, 0.9))
        if p <= 0:
            continue
        y = lerp(H + 160, sy, p)
        xx = lerp(sx + 120, sx, p)
        for j in range(3):
            chip_top(c, xx + j * 8, y - j * 10, 62, ("#E8E2D6", "#3A6EA5", "#D9822B")[k % 3])
        hand = 1 - prog(t, st + 0.95, 0.4)
        if hand > 0:
            c.drawRoundRect(skia.Rect.MakeLTRB(xx - 55, y + 70, xx + 55, y + 400), 30, 30, paint("#1A1210", hand))
            c.drawRoundRect(skia.Rect.MakeLTRB(xx - 60, y + 60, xx + 60, y + 110), 14, 14, paint(CREAM, hand))
            circle(c, xx, y + 125, 9, GOLD, hand)
    c.restore()
    tag(x)


def s05_bg(x):
    spotlight(x, 540, 800, 800, a=0.3)


# ---------------------------------------------------------------- 镜 6:天平隐喻

def s06(x):
    c, t = x.c, x.t
    n_disc = sum(t >= x.cue(0) + 0.2 + k * 0.32 for k in range(9))
    tilt = -3 - 1.6 * n_disc + 1.2 * math.sin(t * 2.2) * (1 - n_disc / 12)
    px, py = 540, 860
    c.drawRect(skia.Rect.MakeLTRB(510, py, 570, 1380), radial(540, 1000, 300, ["#FFE7A8", GOLD, "#7A4A12"]))
    c.drawRoundRect(skia.Rect.MakeLTRB(380, 1370, 700, 1420), 18, 18, paint(GOLD))
    c.save()
    c.translate(px, py)
    c.rotate(tilt)
    c.drawRoundRect(skia.Rect.MakeLTRB(-380, -14, 380, 14), 14, 14, paint(GOLD))
    c.restore()
    circle(c, px, py, 30, "#FFE7A8")
    for side in (-1, 1):
        a = math.radians(tilt)
        ex, ey = px + side * 360 * math.cos(a), py + side * 360 * math.sin(a)
        pan_y = ey + 300
        for dx in (-110, 110):
            stroke_path(c, _line(ex, ey, ex + dx, pan_y), GOLD, 3, 0.85)
        c.drawOval(skia.Rect.MakeLTRB(ex - 150, pan_y - 22, ex + 150, pan_y + 30), paint("#8A5A1E"))
        c.drawOval(skia.Rect.MakeLTRB(ex - 150, pan_y - 30, ex + 150, pan_y + 20), paint(GOLD))
        if side < 0:
            for k in range(n_disc):
                dx = ((k % 3) - 1) * 70
                dy = -(k // 3) * 46
                drop = 1 - ease_out(prog(t, x.cue(0) + 0.2 + k * 0.32, 0.3))
                dot(c, ex + dx, pan_y - 40 + dy - 300 * drop, 34, BLK)
        else:
            pulse = 0.5 + 0.5 * math.sin(t * 4)
            dash = paint("#FF5A4A", 0.5 + 0.4 * pulse, stroke=5)
            dash.setPathEffect(skia.DashPathEffect.Make([16, 12], t * 30))
            c.drawCircle(ex, pan_y - 70, 46, dash)
    for k, (hx, hs) in enumerate(((200, 1.1), (430, 0.95), (680, 1.0), (900, 1.15))):
        head(c, hx, 1620, hs, 1.0, k % 2 == 0)
    draw_text(c, "赌客的直觉", W / 2, 300, 46, "bold", GOLD, fade(t, 0.3))
    draw_kinetic(c, "“黑多了，【红】要补回来”", W / 2, 420, 84, t, w(x, 0, "欠了账") - 0.6, "title", "pop",
                 0.04, hi="#FF5A4A", **TITLE)
    tag(x)


def s06_bg(x):
    spotlight(x, 540, 1000, 700, a=0.3)


# ---------------------------------------------------------------- 镜 7:一直连到 26 次

def s07(x):
    c, t = x.c, x.t
    t26 = w(x, 0, "二十六次")
    lit = [-1.0] * 13 + [lerp(0.6, t26, k / 12) for k in range(13)]
    newest = 13 + sum(t >= v for v in lit[13:])
    step = 64
    target = max(0, (newest - 1) * step - 900)
    c.save()
    c.translate(0, -target)
    c.drawRoundRect(skia.Rect.MakeLTRB(160, 240, 340, 380 + 26 * step), 24, 24, paint("#3A1E0C"))
    c.drawRoundRect(skia.Rect.MakeLTRB(160, 240, 340, 380 + 26 * step), 24, 24, paint(GOLD, 0.8, stroke=4))
    board(c, 250, 320, step, 25, lit, t, 26)
    c.restore()
    p26 = prog(t, t26, 0.5)
    draw_text(c, "连续", 720, 330, 60, "black", CREAM, 1, **TXT)
    c.save()
    c.translate(720, 500)
    s = 1 + 0.4 * (1 - ease_out_back(p26, 2)) if p26 > 0 else 1
    c.scale(s, s)
    draw_text(c, str(newest), 0, 0, 230, "title", "#FFFFFF", 1, stroke=("#1A0E06", 16),
              gradient=["#FFF4D6", "#F2C14E"], shadow=(0, 10, 18, "#000000"),
              glow=("#FF8A3D", 40) if p26 > 0 else None)
    c.restore()
    draw_text(c, "次黑色", 720, 680, 60, "black", CREAM, 1, **TXT)
    draw_text(c, "据广泛引用的记载", 720, 770, 34, "bold", CREAM, 0.8 * fade(t, w(x, 0, "据广为")))
    lose = w(x, 0, "押红的人")
    rect = skia.Rect.MakeLTRB(470, 1080, 1000, 1500)
    c.drawRoundRect(rect, 24, 24, paint(RED, 0.92))
    c.drawRoundRect(rect, 24, 24, paint(GOLD, 0.9, stroke=6))
    rake = ease_in_out(prog(t, lose, 1.6))
    for k, (sx, sy, n) in enumerate(((600, 1280, 6), (760, 1230, 8), (880, 1330, 5), (700, 1400, 7))):
        xx = sx + rake * 700
        chip_stack(c, xx, sy, 56, n, ("#E8E2D6", "#3A6EA5", "#D9822B", "#E8E2D6")[k])
    if prog(t, lose - 0.3, 0.3) > 0:
        rx = 430 + rake * 700
        ra = prog(t, lose - 0.3, 0.3) * (1 - prog(t, lose + 1.6, 0.3))
        c.drawRoundRect(skia.Rect.MakeLTRB(rx - 12, 1100, rx + 12, 1520), 10, 10, paint("#C8A060", ra))
        c.drawLine(rx, 1300, rx + 420, 1850, paint("#8A5A1E", ra, stroke=16))
    lost = fade(t, lose + 0.4)
    draw_text(c, "押红的筹码，被收走了", 735, 1600, 40, "bold", CREAM, 0.85 * lost)
    tag(x)


def s07_bg(x):
    spotlight(x, 720, 520, 520, "#FF9A5A", 0.25)
    spotlight(x, 735, 1290, 520, a=0.2)


# ---------------------------------------------------------------- 镜 8:轮盘不会记账

def s08(x):
    c, t = x.c, x.t
    dim = 1 - 0.35 * prog(t, x.cue(1), 0.6)
    wheel(c, 540, 760, 300, 12, (pocket_angle(black_pocket(26), 12), 0.72), alpha=dim)
    q = x.cue(1)
    draw_kinetic(c, "问题出在哪？", W / 2, 230, 64, t, x.cue(0), "black", "rise", 0.04, fill=CREAM,
                 alpha=1 - prog(t, q, 0.3), **TXT)
    two_lines(c, "轮盘不会记账，", "也不欠谁一次【红】。", 1230, 92, t, q, 1.3, style="slam", hi="#FF5A4A",
              **TITLE)
    close = ease_in_out(prog(t, q + 0.2, 0.7))
    bx, by = 540, 1650
    c.drawRect(skia.Rect.MakeLTRB(bx - 230, by - 150, bx + 230, by + 150).makeOffset(10, 16),
               paint("#000000", 0.5, blur=14))
    c.drawRoundRect(skia.Rect.MakeLTRB(bx - 230, by - 150, bx, by + 150), 10, 10, paint("#5A2414"))
    c.drawRoundRect(skia.Rect.MakeLTRB(bx - 210, by - 135, bx - 10, by + 135), 4, 4, paint(CREAM, 1 - close))
    for k in range(6):
        c.drawLine(bx - 190, by - 90 + k * 36, bx - 30, by - 90 + k * 36, paint("#8A7A60", 0.6 * (1 - close), stroke=2))
    cosv = math.cos(math.pi * close)
    c.save()
    c.translate(bx, by)
    c.scale(cosv, 1)
    if cosv > 0:
        c.drawRoundRect(skia.Rect.MakeLTRB(10, -135, 210, 135), 4, 4, paint(CREAM))
        for k in range(6):
            c.drawLine(30, -90 + k * 36, 190, -90 + k * 36, paint("#8A7A60", 0.6, stroke=2))
    else:
        c.drawRoundRect(skia.Rect.MakeLTRB(0, -150, 230, 150), 10, 10, paint("#6A2C18"))
        c.drawRoundRect(skia.Rect.MakeLTRB(20, -130, 210, 130), 6, 6, paint(GOLD, 0.6, stroke=3))
    c.restore()


def s08_bg(x):
    spotlight(x, 540, 760, 480, a=0.4 * (1 - 0.4 * prog(x.t, x.cue(1), 0.6)))


# ---------------------------------------------------------------- 镜 9:公平硬币

def s09(x):
    c, t = x.c, x.t
    push = ease_in_out(prog(t, w(x, 0, "推到一边") - 0.2, 0.9))
    for k in range(10):
        bx = 108 + k * 96
        tx = 70 + k * 14
        xx = lerp(bx, tx, push)
        a = fade(t, 0.3 + k * 0.08) * (1 - 0.6 * push)
        coin(c, xx, 700 + 40 * push, lerp(42, 30, push), "star", a, dim=push)
    if push > 0:
        draw_text(c, "前十次", 140, 790, 30, "bold", CREAM, 0.7 * push)
    st = w(x, 0, "只看下一次")
    up = prog(t, st, 1.8)
    hgt = math.sin(math.pi * up) * 330
    spins = up * 7.5
    flip = math.cos(spins * math.pi * 2) if 0 < up < 1 else 1
    face = "star" if flip >= 0 else "moon"
    ca = fade(t, w(x, 0, "推到一边"))
    circle(c, 540, 1300, 150 * (1 - 0.4 * hgt / 330), "#000000", 0.4 * ca, blur=20)
    coin(c, 540, 1180 - hgt, 150, face, ca, flip)
    draw_text(c, "前提：公平硬币 · 每次独立", W / 2, 330, 52, "black", CREAM, fade(t, 0.2), **TXT)
    coin(c, 380, 440, 26, "star", fade(t, 0.5))
    draw_text(c, "正面", 450, 440, 36, "bold", CREAM, fade(t, 0.5))
    coin(c, 640, 440, 26, "moon", fade(t, 0.5))
    draw_text(c, "反面", 710, 440, 36, "bold", CREAM, fade(t, 0.5))
    half = w(x, 0, "正面一半")
    for k, (cx, label, face2) in enumerate(((290, "正面  1/2", "star"), (790, "反面  1/2", "moon"))):
        p = ease_out_back(prog(t, half + k * 0.35, 0.45), 2)
        if p <= 0:
            continue
        c.save()
        c.translate(cx, 1560)
        c.scale(p, p)
        rrect(c, 0, 0, 420, 150, 30, "#000000", 0.55, stroke=(GOLD, 3))
        coin(c, -135, 0, 44, face2)
        draw_text(c, label, 50, 0, 64, "title", "#FFFFFF", 1, gradient=["#FFF4D6", "#F2C14E"])
        c.restore()
    draw_text(c, "下一次", W / 2, 1440, 40, "bold", CREAM, fade(t, half))


def s09_bg(x):
    spotlight(x, 540, 1150, 600, a=0.3)


# ---------------------------------------------------------------- 镜 10:两道不同的题

def s10(x):
    c, t = x.c, x.t
    pre = x.cue(0)
    after = w(x, 0, "可前十次")
    a_top = fade(t, pre + 0.1)
    rrect(c, W / 2, 380, 200, 64, 32, GOLD, a_top)
    draw_text(c, "开抛前", W / 2, 380, 36, "black", INK, a_top)
    for k in range(11):
        cx = 110 + k * 86
        fill = prog(t, w(x, 0, "连出十一次") + k * 0.12, 0.25)
        c.drawCircle(cx, 520, 38, paint("#000000", 0.4 * a_top))
        c.drawCircle(cx, 520, 38, paint(GOLD, 0.5 * a_top, stroke=3))
        if fill > 0:
            coin(c, cx, 520, 34 * ease_out_back(fill, 2), "star", a_top)
    p = fade(t, w(x, 0, "约两千次"))
    draw_text(c, "连出 11 次正面", W / 2, 650, 50, "black", CREAM, p, **TXT)
    draw_text(c, "≈ 1/2048", W / 2, 760, 100, "title", "#FFFFFF", p, gradient=["#FFF4D6", "#F2C14E"],
              stroke=("#1A0E06", 12))
    c.drawLine(80, 900, 1000, 900, paint(GOLD, 0.6 * fade(t, after - 0.3), stroke=3))
    a_bot = fade(t, after)
    rrect(c, W / 2, 1000, 200, 64, 32, CREAM, a_bot)
    draw_text(c, "已发生", W / 2, 1000, 36, "black", INK, a_bot)
    for k in range(11):
        cx = 110 + k * 86
        if k < 10:
            coin(c, cx, 1140, 34, "star", a_bot * 0.75, dim=0.5)
        else:
            blink = 0.55 + 0.45 * math.sin(t * 8)
            c.drawCircle(cx, 1140, 40, paint(GOLD, a_bot * blink, stroke=5))
            c.drawCircle(cx, 1140, 52, paint(GOLD, 0.4 * a_bot * blink, blur=14))
            draw_text(c, "?", cx, 1140, 48, "title", "#FFFFFF", a_bot)
    q = fade(t, w(x, 0, "只问下一次"))
    draw_text(c, "下一次正面", W / 2, 1270, 50, "black", CREAM, q, **TXT)
    draw_text(c, "= 1/2", W / 2, 1380, 100, "title", "#FFFFFF", q, gradient=["#FFF4D6", "#F2C14E"],
              stroke=("#1A0E06", 12))
    two = w(x, 0, "这是两道题")
    pp = ease_out_back(prog(t, two, 0.5), 2)
    if pp > 0:
        c.save()
        c.translate(W / 2, 1620)
        c.scale(pp, pp)
        rrect(c, 0, 0, 640, 130, 65, RED, 1, shadow=0.4, stroke=(GOLD, 4))
        draw_text(c, "两道不同的题", 0, 0, 66, "title", "#FFFFFF", 1)
        c.restore()


def s10_bg(x):
    spotlight(x, 540, 560, 520, a=0.2)
    spotlight(x, 540, 1200, 520, a=0.2)


# ---------------------------------------------------------------- 镜 11:长期比例是"冲淡"

def _sim_curve() -> list[tuple[float, float]]:
    """模拟示意:前 10 次正面,之后 2990 次公平随机抛掷的累计正面比例(固定种子)。"""
    rng = np.random.default_rng(2024)
    flips = np.concatenate([np.ones(10), rng.integers(0, 2, 2990)])
    ratio = np.cumsum(flips) / np.arange(1, len(flips) + 1)
    idx = sorted({int(round(v)) for v in np.geomspace(1, len(flips), 500)})
    return [(i, float(ratio[i - 1])) for i in idx]


CURVE = _sim_curve()


def s11(x):
    c, t = x.c, x.t
    L, R, T, B = 140, 980, 620, 1360
    lo, hi = 0.3, 1.0

    def px(n):
        return L + (R - L) * math.log10(n) / math.log10(3000)

    def py(v):
        return B - (B - T) * (v - lo) / (hi - lo)

    a = fade(t, 0.1)
    rrect(c, (L + R) / 2, (T + B) / 2 + 30, R - L + 120, B - T + 200, 30, "#000000", 0.4 * a, stroke=(GOLD, 2))
    c.drawLine(L, B, R, B, paint(CREAM, 0.6 * a, stroke=3))
    c.drawLine(L, T, L, B, paint(CREAM, 0.6 * a, stroke=3))
    half = paint(CREAM, 0.8 * a, stroke=3)
    half.setPathEffect(skia.DashPathEffect.Make([18, 12], 0))
    c.drawLine(L, py(0.5), R, py(0.5), half)
    draw_text(c, "50%", L - 10, py(0.5), 36, "black", CREAM, a, align="right")
    draw_text(c, "100%", L - 10, py(1.0), 30, "bold", CREAM, 0.7 * a, align="right")
    for n, label in ((1, "1"), (10, "10"), (100, "100"), (1000, "1000")):
        draw_text(c, label, px(n), B + 40, 30, "bold", CREAM, 0.7 * a)
    draw_text(c, "抛掷次数（对数刻度）→", (L + R) / 2, B + 100, 32, "bold", CREAM, 0.75 * a)
    draw_text(c, "正面比例", L + 90, T - 40, 32, "bold", CREAM, 0.75 * a)
    path = skia.Path()
    for k, (n, v) in enumerate(CURVE):
        (path.lineTo if k else path.moveTo)(px(n), py(v))
    p = ease_in_out(prog(t, 0.5, 4.6))
    stroke_path(c, path, GOLD, 6, 1, p, glow=("#FFB347", 10))
    draw_text(c, "模拟示意：前 10 次正面，之后随机", W / 2, 1610, 34, "bold", CREAM, 0.8 * a)
    draw_kinetic(c, "长期 ≈ 50%", W / 2, 320, 96, t, 0.2, "title", "pop", 0.04, **TITLE)
    draw_kinetic(c, "是“冲淡”，不是“补回”", W / 2, 460, 70, t, w(x, 0, "冲淡"), "title", "rise", 0.04,
                 **title_style(gradient=["#FFFFFF", "#F3E3C3"]))


def s11_bg(x):
    spotlight(x, 540, 1000, 700, a=0.18)


# ---------------------------------------------------------------- 镜 12:定义卡

def s12(x):
    c, t = x.c, x.t
    wheel(c, 290, 520, 170, t * 12, None)
    coin(c, 790, 520, 130, "star", 1, math.cos(t * 1.2))
    c.drawLine(540, 330, 540, 710, paint(GOLD, 0.9, stroke=4))
    drop = ease_out_back(prog(t, x.cue(0) - 0.1, 0.7), 1.2)
    cy = lerp(-500, 1240, drop)
    rrect(c, W / 2, cy, 940, 860, 30, gradient=["#F7EBD0", "#E8D4AA"], shadow=0.6, stroke=(GOLD, 6))
    c.drawRoundRect(skia.Rect.MakeXYWH(W / 2 - 440, cy - 400, 880, 800), 22, 22, paint("#8A5A1E", 0.6, stroke=2))
    draw_text(c, "赌徒谬误", W / 2, cy - 280, 110, "title", INK)
    draw_text(c, "（又称 蒙特卡洛谬误）", W / 2, cy - 165, 42, "bold", "#6A4A2A")
    c.drawLine(W / 2 - 300, cy - 100, W / 2 + 300, cy - 100, paint("#8A5A1E", 0.7, stroke=2))
    d0 = w(x, 0, "在独立")
    rows = ("在【独立】、【概率不变】的", "随机事件里，误以为", "前面的结果，会让", "相反结果更容易出现")
    for k, row in enumerate(rows):
        a = fade(t, d0 + k * 1.2)
        draw_rich(c, row, W / 2, cy + k * 82 - 10, 58, "black", INK, RED, a)


def s12_bg(x):
    spotlight(x, 540, 1240, 760, a=0.3)


# ---------------------------------------------------------------- 镜 13:抽奖的例子

def s13(x):
    c, t = x.c, x.t
    pull = max(0.0, math.sin(math.pi * prog(t, 1.2, 1.0)))
    mx, my = 330, 1080
    dome = skia.Rect.MakeLTRB(mx - 190, my - 560, mx + 190, my - 180)
    c.drawOval(dome, paint("#FFFFFF", 0.08))
    c.drawOval(dome, paint(CREAM, 0.6, stroke=4))
    for k in range(14):
        ang = t * (1.5 + k * 0.17) + k
        bx = mx + 130 * math.sin(ang * 1.3 + k)
        by = my - 330 + 100 * math.cos(ang + k * 0.7) * (0.4 + pull)
        circle(c, bx, by, 26, ("#C8302C", "#E8B04A", "#3A6EA5", "#F3E3C3")[k % 4], 0.95)
    rrect(c, mx, my + 80, 440, 520, 30, gradient=["#B87A3A", "#6B3A18"], shadow=0.5, stroke=(GOLD, 5))
    rrect(c, mx, my + 20, 300, 120, 16, "#2A160A", 1, stroke=(GOLD, 3))
    draw_text(c, "第 11 次", mx, my + 20, 54, "title", "#FFFFFF", fade(t, 0.3), gradient=["#FFF4D6", "#F2C14E"])
    hx, hy = mx + 220, my - 20
    ang = math.radians(-60 + 110 * pull)
    ex, ey = hx + 190 * math.cos(ang), hy + 190 * math.sin(ang)
    stroke_path(c, _line(hx, hy, ex, ey), "#C8A060", 18)
    circle(c, ex, ey, 34, RED)
    out = ease_out(prog(t, 2.2, 0.8))
    if out > 0:
        rrect(c, mx, my + 360 + 120 * out, 220, 130, 10, CREAM, 1, shadow=0.4)
        draw_text(c, "未中", mx, my + 360 + 120 * out, 50, "title", "#8A7A60", out)
    sep = paint(GOLD, 0.7, stroke=4)
    sep.setPathEffect(skia.DashPathEffect.Make([20, 14], 0))
    c.drawLine(690, 700, 690, 1700, sep)
    g0 = w(x, 1, "带保底")
    a2 = 0.5 + 0.5 * fade(t, g0 - 0.3)
    gx, gy = 880, 1120
    rrect(c, gx, gy, 280, 420, 24, gradient=["#6A6A7A", "#3A3A48"], alpha=a2, stroke=(CREAM, 3))
    gauge = skia.Rect.MakeLTRB(gx - 100, gy - 140, gx + 100, gy + 60)
    c.drawArc(gauge, 180, 180, False, paint(CREAM, a2, stroke=10))
    c.drawArc(gauge, 300, 60, False, paint("#7CFFB2", a2, stroke=10))
    needle = math.radians(180 + 160 * clamp01(prog(t, g0, 2.0)))
    c.drawLine(gx, gy - 40, gx + 90 * math.cos(needle), gy - 40 + 90 * math.sin(needle), paint("#FF5A4A", a2, stroke=6))
    circle(c, gx, gy - 40, 10, CREAM, a2)
    draw_text(c, "保底进度", gx, gy + 110, 36, "bold", CREAM, a2)
    draw_kinetic(c, "无保底 · 中奖率固定", W / 2, 300, 64, t, x.cue(0) + 0.2, "black", "rise", 0.04,
                 fill=CREAM, **TXT)
    draw_kinetic(c, "前面没中 ≠ 下次更易中", W / 2, 420, 76, t, w(x, 0, "前面没中"), "title", "pop", 0.04,
                 **TITLE)
    p = fade(t, g0)
    rrect(c, 840, 1560, 330, 130, 20, "#000000", 0.6 * p, stroke=(GOLD, 2))
    draw_text(c, "有保底 / 动态概率", 840, 1535, 34, "bold", CREAM, p)
    draw_text(c, "不能直接套用", 840, 1590, 36, "black", "#FF7A6A", p)


def s13_bg(x):
    spotlight(x, 330, 1000, 600, a=0.3)


# ---------------------------------------------------------------- 镜 14:结尾自问

def s14(x):
    c, t = x.c, x.t
    push = 1 + 0.12 * ease_in_out(t / x.dur)
    c.save()
    c.translate(W / 2, 1150)
    c.scale(push, push)
    c.translate(-W / 2, -1150)
    wheel(c, 540, 1060, 330, 12, (pocket_angle(black_pocket(26), 12), 0.72))
    for r, color in ((skia.Rect.MakeLTRB(170, 1470, 540, 1700), RED), (skia.Rect.MakeLTRB(540, 1470, 910, 1700), BLK)):
        c.drawRect(r, paint(color, 0.95))
    c.drawRect(skia.Rect.MakeLTRB(170, 1470, 910, 1700), paint(GOLD, 0.9, stroke=6))
    c.drawLine(540, 1470, 540, 1700, paint(GOLD, 0.9, stroke=4))
    bob = 14 * math.sin(t * 2.4)
    circle(c, 540, 1600, 60, "#000000", 0.4, blur=12)
    chip_top(c, 540, 1530 + bob, 62, "#E8E2D6")
    c.restore()
    q1, q2 = x.cue(0), x.cue(1)
    ask = w(x, 0, "我觉得")
    a1 = 1 - prog(t, q2 - 0.3, 0.4)
    draw_kinetic(c, "条件真的变了？", W / 2, 300, 92, t, w(x, 0, "条件真的变了"), "title", "pop", 0.04,
                 alpha=a1, **TITLE)
    draw_kinetic(c, "还是只是【前面输了】？", W / 2, 440, 84, t, w(x, 0, "还是仅仅"), "title", "pop", 0.04,
                 alpha=a1, hi="#FF5A4A", **TITLE)
    draw_text(c, "先问自己一句", W / 2, 180, 42, "bold", CREAM, fade(t, ask - 0.6) * a1)
    draw_kinetic(c, "“该轮到我了”？", W / 2, 360, 96, t, q1 + 0.1, "title", "pop", 0.04,
                 alpha=1 - prog(t, w(x, 0, "条件真的变了") - 0.4, 0.3), **TITLE)
    two_lines(c, "十次黑之后，", "押红并不更容易赢", 300, 92, t, w(x, 1, "十次黑之后"), 1.4, style="rise",
              **TITLE)


def s14_bg(x):
    spotlight(x, 540, 1060, 600, a=0.32 * (1 - 0.6 * prog(x.t, x.dur - 3, 3)))


# ---------------------------------------------------------------- 时间线

L = lambda text, pause=0.3, speed=1.0: Line(text, speed, pause, caption=False)  # noqa: E731

SCENES = [
    Scene("s01", [L("轮盘已经连开十次黑色。下一把，你押红，还是押黑？")], s01, "casino", "cut", bg=s01_bg, lead=0.15),
    Scene("s02", [L("一九一三年八月十八日，蒙特卡洛赌场，真有张桌子把这道题摆了出来。")], s02, "casino", "black",
          bg=s02_bg),
    Scene("s03", [L("小球一圈圈转，落进黑格。再转，还是黑。记分牌上的黑，越排越长。")], s03, "casino", "whip",
          bg=s03_bg),
    Scene("s04", [L("桌边的人坐不住了：", 0.05), L("“都这么多次黑了，总该轮到红了吧？”")], s04, "casino", "cut",
          bg=s04_bg, lead=0.05),
    Scene("s05", [L("于是，筹码一摞一摞，推向了红色。")], s05, "felt", "cut", bg=s05_bg, lead=0.2),
    Scene("s06", [L("这念头很好懂：红黑本该差不多各半，黑出多了，红就像欠了账，迟早要还。", speed=1.1)], s06, "casino", "black",
          bg=s06_bg, lead=0.05),
    Scene("s07", [L("可小球落下，还是黑。据广为流传的记载，这串黑一直连到了二十六次。押红的人，越输越多。")], s07,
          "casino", "cut", bg=s07_bg, lead=0.2),
    Scene("s08", [L("问题出在哪？", 0.5), L("轮盘不会记账，也不欠谁一次红。")], s08, "dark", "cut", bg=s08_bg,
          lead=0.2, exit="black"),
    Scene("s09", [L("换成公平硬币更清楚。已连出十次正面，把它们推到一边，只看下一次：正面一半，反面一半。")], s09,
          "coin", "black", bg=s09_bg, lead=0.3),
    Scene("s10", [L("你会说：连出十一次正面多难啊！对，开抛前看，约两千次才一次。可前十次已经发生，现在只问下一次——"
                    "这是两道题。")], s10, "coin", "whip", bg=s10_bg, lead=0.1),
    Scene("s11", [L("长期接近一半，靠海量次数把偏差冲淡，不靠下一次专门出反面来补。")], s11, "coin", "cut", bg=s11_bg,
          lead=0.3),
    Scene("s12", [L("这就是赌徒谬误，又叫蒙特卡洛谬误：在独立、概率不变的随机事件里，误以为前面的结果，"
                    "会让相反结果更容易出现。")], s12, "casino", "zoom", bg=s12_bg, lead=0.2),
    Scene("s13", [L("生活里：没有保底、中奖率固定的抽奖，前面没中，下次也不更容易中。", 0.05, 1.08),
                  L("带保底或概率会变的抽卡，不能这么套。", speed=1.08)], s13, "casino", "whip", bg=s13_bg,
          lead=0.05),
    Scene("s14", [L("下次觉得“该轮到我了”，先问一句：我觉得下一次更有希望，是条件真的变了，还是仅仅因为前面输了？", 0.8),
                  L("所以开头那一把：十次黑之后，押红并不更容易赢。")], s14, "casino", "cut", bg=s14_bg, lead=0.2,
          exit="black"),
]

# 分镜表时间段(秒):0–5–12–18–23–27–33–42–47–56–66–73–84–93–108
DURATIONS = [5, 7, 6, 5, 4, 6, 9, 5, 9, 10, 7, 11, 9, 15]


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(video: Video, path: Path):
    """按估算语速输出口播字幕(SRT),每句一条;起止不越过本镜头边界。"""
    rows = []
    for s in video.scenes:
        for i, ln in enumerate(s.lines):
            st = s.t0 + s.starts[i]
            en = min(s.t0 + s.ends[i], s.t0 + s.duration - 0.05)
            rows.append((st, en, plain(ln.text)))
    out = [f"{k}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n" for k, (a, b, txt) in enumerate(rows, 1)]
    path.write_text("\n".join(out), encoding="utf-8")


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "out/gamblers_fallacy_silent.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    video = Video(SCENES, PALETTES, music=[])
    video.layout_fixed(DURATIONS)
    write_srt(video, out.with_suffix(".srt"))
    skia.Image.fromarray(video.still(2.9), colorType=skia.kRGBA_8888_ColorType).save(
        str(out.with_name("cover.png")), skia.kPNG)
    video.render(str(out), silent=True)
    print(f"done: {out} ({video.total:.1f}s)")


if __name__ == "__main__":
    main()
