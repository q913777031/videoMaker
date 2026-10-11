"""《为什么你刷短视频停不下来？》黑金风格无声科普竖屏短视频（第二版：动画主导）。

完全无声：无旁白、无音乐、无音效，成片不含音频流。
每屏只留一句短话，信息主要由动画承担；每 3 秒内至少有一次动画事件（见 docs/scroll_short/storyboard.md）。
叙事线：第一视角刷手机的开场 → 历史（1992 协同过滤 / 1997 多巴胺与预期 / 2000s—2010s 无限滚动与自动播放）
→ 理论（示意循环与习惯）→ 推荐反馈 → 停止节点 → 方法（“如果—就”停止计划）→ 收束 → 参考资料。

用法：
  python3 scroll_short.py [输出路径]          渲染成片（默认 out/scroll_short.mp4）与两张封面
  python3 scroll_short.py --still 秒 [...]    只渲染指定时刻的单帧 PNG，用于检查画面
依赖资源：python3 fetch_assets.py（只需其中的思源黑体）
"""

import functools
import math
import random
import subprocess
import sys
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import skia

ROOT = Path(__file__).resolve().parent
FONT_DIR = ROOT / "assets" / "fonts"
W, H, FPS = 1080, 1920, 30
TOTAL = 97.0

BG = "#08090B"
GOLD = "#D8B46A"
LIGHT = "#E8DCC0"
DARK = "#75613C"
GOLD_HI = "#F0D696"  # 金色字的轻微渐变上沿
GOLD_LO = "#C29A52"  # 金色字的轻微渐变下沿
WARM = "#FFE6B0"     # 光效高光色
MUTED = "#A8987A"    # 小字

# 安全区：避开右侧操作栏（约 190px）与底部说明区（约 340px）
CX = 480
LEFT, RIGHT = 72, 888

WEIGHTS = {"r": "Regular", "m": "Medium", "b": "Bold", "k": "Black"}


# ---------------------------------------------------------------- 缓动与时间

def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def lerp(a: float, b: float, x: float) -> float:
    return a + (b - a) * x


def ease_out(x: float) -> float:
    return 1 - (1 - clamp01(x)) ** 3


def ease_in(x: float) -> float:
    return clamp01(x) ** 3


def ease_in_out(x: float) -> float:
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_back(x: float, s: float = 1.9) -> float:
    x = clamp01(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def prog(t: float, start: float, dur: float = 0.4) -> float:
    return clamp01((t - start) / dur) if dur > 0 else float(t >= start)


def life(t: float, t0: float, t1: float | None = None, fin: float = 0.4, fout: float = 0.35) -> float:
    """元素透明度：t0 起淡入，t1 起淡出；只做单次渐变，不做明暗闪烁。"""
    a = ease_out(prog(t, t0, fin))
    if t1 is not None:
        a *= 1 - ease_in_out(prog(t, t1, fout))
    return a


def bump(t: float, t0: float, dur: float = 0.6) -> float:
    """t0 起一次性的 0→1→0 脉冲（光晕爆发用），持续 dur 秒。"""
    p = prog(t, t0, dur)
    return math.sin(math.pi * p) if 0 < p < 1 else 0.0


# ---------------------------------------------------------------- 颜色与字体

@functools.lru_cache(maxsize=None)
def rgb(c: str) -> tuple:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def col(c: str, a: float = 1.0) -> int:
    r, g, b = rgb(c)
    return skia.Color(r, g, b, int(round(255 * clamp01(a))))


def mix(c1: str, c2: str, x: float) -> str:
    a, b = rgb(c1), rgb(c2)
    return "#%02X%02X%02X" % tuple(int(p + (q - p) * clamp01(x)) for p, q in zip(a, b))


@functools.lru_cache(maxsize=None)
def typeface(weight: str) -> skia.Typeface:
    path = FONT_DIR / f"NotoSansCJKsc-{WEIGHTS[weight]}.otf"
    tf = skia.Typeface.MakeFromFile(str(path))
    if tf is None:
        raise FileNotFoundError(f"font not found: {path} (run fetch_assets.py)")
    return tf


@functools.lru_cache(maxsize=2048)
def font(weight: str, size: float) -> skia.Font:
    f = skia.Font(typeface(weight), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def text_w(s: str, size: float, weight: str = "b") -> float:
    return font(weight, size).measureText(s.replace("【", "").replace("】", ""))


@functools.lru_cache(maxsize=64)
def _blur(sigma: float) -> skia.MaskFilter:
    return skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma)


def paint(color: str, a: float = 1.0, stroke: float = 0.0, blur: float = 0.0) -> skia.Paint:
    p = skia.Paint(AntiAlias=True, Color=col(color, a))
    if stroke > 0:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(_blur(round(blur, 1)))
    return p


def _segments(s: str) -> list[tuple[str, bool]]:
    segs, buf, on = [], "", False
    for ch in s:
        if ch in "【】":
            if buf:
                segs.append((buf, on))
            buf, on = "", ch == "【"
        else:
            buf += ch
    if buf:
        segs.append((buf, on))
    return segs


def text(c: skia.Canvas, s: str, x: float, y: float, size: float, weight: str = "b", color: str = LIGHT,
         a: float = 1.0, align: str = "center", hi: str = GOLD, gold: bool = False, glow: float = 0.0) -> float:
    """绘制单行文字，y 为视觉中线；【】片段用金色 hi；gold=True 整行轻微金色渐变；
    glow>0 时先画一层模糊金光（强度 0–1）。返回行宽。"""
    if a <= 0 or not s:
        return 0.0
    segs = _segments(s)
    f = font(weight, size)
    w = sum(f.measureText(t) for t, _ in segs)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    base = y + size * 0.36
    if glow > 0:
        gp = paint(GOLD, a * 0.55 * clamp01(glow), blur=size * 0.22)
        xx = x0
        for t, _ in segs:
            c.drawTextBlob(skia.TextBlob.MakeFromString(t, f), xx, base, gp)
            xx += f.measureText(t)
    xx = x0
    for t, on in segs:
        if gold or on:
            p = skia.Paint(AntiAlias=True)
            p.setShader(skia.GradientShader.MakeLinear(
                [(0, y - size * 0.5), (0, y + size * 0.45)], [col(GOLD_HI, a), col(GOLD_LO, a)]))
        else:
            p = paint(color, a)
        c.drawTextBlob(skia.TextBlob.MakeFromString(t, f), xx, base, p)
        xx += f.measureText(t)
    return w


def sweep(c: skia.Canvas, s: str, x: float, y: float, size: float, weight: str, a: float, t: float, t0: float,
          dur: float = 1.0, align: str = "center"):
    """扫光：一条斜向高光带从左到右扫过已画好的文字（只作用在文字像素上）。"""
    p = prog(t, t0, dur)
    if not 0 < p < 1 or a <= 0:
        return
    w = text_w(s, size, weight)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    bounds = skia.Rect(x0 - 10, y - size * 0.7, x0 + w + 10, y + size * 0.7)
    c.saveLayer(bounds)
    text(c, s, x, y, size, weight, LIGHT, 1.0, align)
    bx = lerp(x0 - size, x0 + w + size, ease_in_out(p))
    band = skia.Paint(AntiAlias=True)
    band.setShader(skia.GradientShader.MakeLinear(
        [(bx - size * 0.9, y - size), (bx + size * 0.9, y + size)],
        [col(WARM, 0), col("#FFFFFF", 0.9 * a), col(WARM, 0)]))
    band.setBlendMode(skia.BlendMode.kSrcIn)
    c.drawRect(bounds, band)
    c.restore()


def streak(c: skia.Canvas, x: float, y: float, length: float, a: float, thick: float = 3):
    """横向镜头光条：中间亮、两端渐隐，配合大字砸入。"""
    if a <= 0:
        return
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear(
        [(x - length / 2, y), (x + length / 2, y)],
        [col(GOLD, 0), col(WARM, a), col(GOLD, 0)]))
    c.drawRect(skia.Rect(x - length / 2, y - thick / 2, x + length / 2, y + thick / 2), p)
    p2 = skia.Paint(AntiAlias=True, MaskFilter=_blur(10.0))
    p2.setShader(skia.GradientShader.MakeLinear(
        [(x - length / 3, y), (x + length / 3, y)], [col(GOLD, 0), col(GOLD, a * 0.6), col(GOLD, 0)]))
    c.drawRect(skia.Rect(x - length / 3, y - 10, x + length / 3, y + 10), p2)


def bloom(c: skia.Canvas, x: float, y: float, r: float, a: float, color: str = GOLD):
    """径向柔光（叠加混合），用于节点点亮、屏幕光、爆发。"""
    if a <= 0 or r <= 0:
        return
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((x, y), r, [col(color, a), col(color, a * 0.35), col(color, 0)],
                                               [0.0, 0.35, 1.0]))
    p.setBlendMode(skia.BlendMode.kScreen)
    c.drawCircle(x, y, r, p)


def slam(c: skia.Canvas, rows: list[str], x: float, y: float, size: float, lh: float, t: float, t0: float,
         t1: float | None = None, gold_rows: tuple = (), stagger: float = 0.45):
    """钩子大字：逐行从 1.25 倍砸到原大，伴随一次金色光晕与横向光条；t1 起淡出。"""
    for i, row in enumerate(rows):
        s0 = t0 + i * stagger
        a = life(t, s0, t1, fin=0.1, fout=0.35)
        if a <= 0:
            continue
        k = lerp(1.25, 1.0, ease_out_back(prog(t, s0, 0.35), 1.4))
        yy = y + i * lh
        g = bump(t, s0 + 0.05, 0.9)
        c.save()
        c.translate(x, yy)
        c.scale(k, k)
        text(c, row, 0, 0, size, "k", LIGHT, a, gold=i in gold_rows, glow=0.35 + g)
        c.restore()
        streak(c, x, yy + size * 0.62, 760 * ease_out(prog(t, s0, 0.5)), a * g * 0.9)


def caption(c: skia.Canvas, s: str, y: float, t: float, t0: float, t1: float | None, size: float = 64,
            sub: str | None = None, sub_t: float | None = None):
    """单句说明：上浮淡入 + 一次扫光；可带一行小字（sub）。"""
    a = life(t, t0, t1, 0.45)
    if a > 0:
        dy = (1 - ease_out(prog(t, t0, 0.5))) * 26
        text(c, s, CX, y + dy, size, "b", LIGHT, a, glow=0.15)
        sweep(c, s, CX, y + dy, size, "b", a, t, t0 + 0.5, 1.1)
    if sub:
        sa = life(t, sub_t if sub_t is not None else t0 + 0.6, t1, 0.4)
        text(c, sub, CX, y + size * 0.6 + 44, 34, "m", MUTED, sa)


def note(c: skia.Canvas, s: str, x: float, y: float, a: float, align: str = "center", size: float = 30):
    """出处/示意等小字标注。"""
    text(c, s, x, y, size, "r", MUTED, a * 0.9, align)


def chip(c: skia.Canvas, s: str, x: float, y: float, a: float, filled: bool = False, size: float = 30):
    if a <= 0:
        return
    w = text_w(s, size, "m") + size * 1.1
    if filled:
        rrect(c, x, y, w, size * 1.6, size * 0.8, fill=GOLD, fa=a)
        text(c, s, x, y, size, "m", BG, a)
    else:
        rrect(c, x, y, w, size * 1.6, size * 0.8, stroke=GOLD, sa=a * 0.85, sw=2)
        text(c, s, x, y, size, "m", GOLD, a)


# ---------------------------------------------------------------- 图形元件

def rrect(c: skia.Canvas, cx: float, cy: float, w: float, h: float, r: float, fill: str | None = None,
          fa: float = 1.0, stroke: str | None = None, sa: float = 1.0, sw: float = 2.0, glow: float = 0.0):
    rect = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h), r, r)
    if glow > 0:
        c.drawRRect(rect, paint(GOLD, glow * 0.6, sw + 6, blur=14))
    if fill and fa > 0:
        c.drawRRect(rect, paint(fill, fa))
    if stroke and sa > 0:
        c.drawRRect(rect, paint(stroke, sa, sw))


def arrow_head(c: skia.Canvas, x: float, y: float, ang: float, size: float, color: str, a: float):
    p = skia.Path()
    p.moveTo(x + math.cos(ang) * size, y + math.sin(ang) * size)
    p.lineTo(x + math.cos(ang + 2.5) * size * 0.8, y + math.sin(ang + 2.5) * size * 0.8)
    p.lineTo(x + math.cos(ang - 2.5) * size * 0.8, y + math.sin(ang - 2.5) * size * 0.8)
    p.close()
    c.drawPath(p, paint(color, a))


def polyline(c: skia.Canvas, pts: list[tuple], frac: float, color: str, a: float, width: float = 3,
             head: float = 0.0, glow: float = 0.0) -> tuple:
    """按长度比例 frac 描出折线（路径描边动画）；head>0 画箭头，glow>0 加模糊光。返回笔尖坐标。"""
    if frac <= 0 or a <= 0 or len(pts) < 2:
        return pts[0]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    goal = sum(seg) * clamp01(frac)
    path, acc = skia.Path(), 0.0
    path.moveTo(*pts[0])
    end, ang = pts[0], 0.0
    for i, L in enumerate(seg):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        if L > 0:
            ang = math.atan2(y1 - y0, x1 - x0)
        if acc + L >= goal:
            k = (goal - acc) / L if L else 1
            end = (lerp(x0, x1, k), lerp(y0, y1, k))
            path.lineTo(*end)
            break
        path.lineTo(x1, y1)
        end, acc = (x1, y1), acc + L
    if glow > 0:
        c.drawPath(path, paint(GOLD, a * glow * 0.7, width + 8, blur=8))
    c.drawPath(path, paint(color, a, width))
    if head > 0:
        arrow_head(c, end[0], end[1], ang, head, color, a)
    return end


def ellipse_pt(cx, cy, rx, ry, deg) -> tuple:
    r = math.radians(deg)
    return cx + rx * math.cos(r), cy + ry * math.sin(r)


def ellipse_pts(cx, cy, rx, ry, a0, a1, n=64) -> list[tuple]:
    return [ellipse_pt(cx, cy, rx, ry, lerp(a0, a1, i / n)) for i in range(n + 1)]


def bezier(p0, p1, p2, k: float) -> tuple:
    u = 1 - k
    return (u * u * p0[0] + 2 * u * k * p1[0] + k * k * p2[0], u * u * p0[1] + 2 * u * k * p1[1] + k * k * p2[1])


def orb(c: skia.Canvas, x: float, y: float, r: float, a: float):
    """发光光球：外圈柔光 + 亮核。"""
    bloom(c, x, y, r * 5, a * 0.55)
    c.drawCircle(x, y, r, paint(WARM, a))
    c.drawCircle(x, y, r * 0.55, paint("#FFFFFF", a * 0.9))


def ring_burst(c: skia.Canvas, x: float, y: float, t: float, t0: float, r0: float, r1: float, a: float = 1.0):
    """一次性扩散光环（节点点亮、按钮消散时用）。"""
    p = prog(t, t0, 0.8)
    if 0 < p < 1:
        c.drawCircle(x, y, lerp(r0, r1, ease_out(p)), paint(GOLD, a * (1 - p), 3 * (1 - p) + 1))
        bloom(c, x, y, lerp(r0, r1, ease_out(p)) * 1.2, a * 0.35 * (1 - p))


def shape(c: skia.Canvas, kind: str, x: float, y: float, s: float, color: str, a: float, stroke: float = 0):
    """内容上的抽象主题符号：circle / tri / square / diamond。"""
    p = paint(color, a, stroke) if stroke else paint(color, a)
    if kind == "circle":
        c.drawCircle(x, y, s * 0.5, p)
    elif kind == "tri":
        path = skia.Path()
        path.moveTo(x, y - s * 0.52)
        path.lineTo(x + s * 0.55, y + s * 0.42)
        path.lineTo(x - s * 0.55, y + s * 0.42)
        path.close()
        c.drawPath(path, p)
    elif kind == "diamond":
        path = skia.Path()
        path.moveTo(x, y - s * 0.55)
        path.lineTo(x + s * 0.45, y)
        path.lineTo(x, y + s * 0.55)
        path.lineTo(x - s * 0.45, y)
        path.close()
        c.drawPath(path, p)
    else:
        c.drawRect(skia.Rect.MakeXYWH(x - s * 0.42, y - s * 0.42, s * 0.84, s * 0.84), p)


def pause_icon(c: skia.Canvas, x: float, y: float, r: float, a: float):
    c.drawCircle(x, y, r, paint(GOLD, a))
    bw, bh = r * 0.22, r * 0.86
    for dx in (-r * 0.26, r * 0.26):
        rrect(c, x + dx, y, bw, bh, bw * 0.3, fill=BG, fa=a)


def doc_card(c: skia.Canvas, x: float, y: float, w: float, h: float, a: float, star: float = 0.0, dim: float = 0.0):
    """1992 场景的“文档”卡片；star>0 时右上角出现金色星标。"""
    if a <= 0:
        return
    k = 1 - 0.7 * dim
    rrect(c, x, y, w, h, 10, fill="#121317", fa=a * k, stroke=mix(DARK, GOLD, star), sa=a * k, sw=2 + star,
          glow=star * 0.5 * a * k)
    for i, lw in enumerate((0.6, 0.7, 0.45)):
        yy = y - h * 0.22 + i * h * 0.2
        c.drawLine(x - w * 0.32, yy, x - w * 0.32 + w * lw * 0.9, yy, paint(DARK, a * k, 5))
    if star > 0:
        star_shape(c, x + w * 0.36, y - h * 0.4, 18 * ease_out_back(star), a * k)


def star_shape(c: skia.Canvas, x: float, y: float, r: float, a: float):
    if r <= 0:
        return
    p = skia.Path()
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        ang = -math.pi / 2 + i * math.pi / 5
        (p.moveTo if i == 0 else p.lineTo)(x + rr * math.cos(ang), y + rr * math.sin(ang))
    p.close()
    bloom(c, x, y, r * 2.5, a * 0.4)
    c.drawPath(p, paint(GOLD, a))


def person(c: skia.Canvas, x: float, y: float, s: float, a: float, color: str = MUTED):
    c.drawCircle(x, y - s * 0.55, s * 0.28, paint(color, a))
    rect = skia.Rect(x - s * 0.5, y - s * 0.15, x + s * 0.5, y + s * 0.75)
    c.drawArc(rect, 180, 180, True, paint(color, a))


# ---------------------------------------------------------------- 环境光与粒子

random.seed(7)
DUST = [(random.uniform(0, W), random.uniform(0, H), random.uniform(1.2, 3.2), random.uniform(6, 22),
         random.uniform(0, 6.28), random.uniform(0.05, 0.22)) for _ in range(46)]


def ambient(c: skia.Canvas, t: float, glow_y: float = 980, glow_a: float = 0.08):
    """背景：近黑底 + 中部极淡暖光 + 缓慢上漂的金色微尘（亮度缓慢起伏，不闪烁）。"""
    c.clear(col(BG))
    bloom(c, CX, glow_y, 900, glow_a, "#3A2E18")
    for x, y, r, v, ph, al in DUST:
        yy = (y - t * v) % (H + 40) - 20
        xx = x + 14 * math.sin(t * 0.3 + ph)
        aa = al * (0.6 + 0.4 * math.sin(t * 0.5 + ph))
        c.drawCircle(xx, yy, r * 3.2, paint(GOLD, aa * 0.25, blur=r * 1.6))
        c.drawCircle(xx, yy, r * 0.7, paint(WARM, aa))


def vignette(c: skia.Canvas):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((W / 2, H / 2), H * 0.72,
                                               [col("#000000", 0), col("#000000", 0), col("#000000", 0.55)],
                                               [0.0, 0.62, 1.0]))
    c.drawRect(skia.Rect(0, 0, W, H), p)


# ---------------------------------------------------------------- 手机与信息流

def phone(c: skia.Canvas, x: float, y: float, w: float, h: float, a: float, screen, light: float = 1.0):
    """手机：屏幕光外溢 + 机身 + 屏幕内容（screen(c, l, t, w, h) 在裁剪区内绘制）。"""
    if a <= 0:
        return
    bloom(c, x, y, max(w, h) * 0.75, a * 0.16 * light, "#C9A35A")
    rrect(c, x, y, w + 22, h + 22, w * 0.13, fill="#0B0C0E", fa=a, stroke=mix(DARK, GOLD, 0.45), sa=a, sw=3)
    l, tp = x - w / 2, y - h / 2
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(l, tp, w, h), w * 0.11, w * 0.11), doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(l, tp, w, h), paint("#0F1013", a))
    screen(c, l, tp, w, h)
    c.restore()
    rrect(c, x, tp + h * 0.025, w * 0.26, h * 0.022, h * 0.011, fill="#000000", fa=a)


def feed_card(c: skia.Canvas, l: float, tp: float, w: float, h: float, oy: float, kind: str, t: float, a: float,
              lit: float = 0.5, progress: float = 0.0):
    """屏内一条“短视频”：暖色背景光 + 抽象主体 + 字幕占位 + 右侧互动图标 + 进度条。oy 为纵向偏移。"""
    if a <= 0:
        return
    y0 = tp + oy
    if y0 > tp + h or y0 + h < tp:
        return
    tint = {"circle": "#3B2E16", "tri": "#2E2614", "square": "#272219", "diamond": "#33281A"}[kind]
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([(0, y0), (0, y0 + h)], [col(tint, a), col("#0E0F12", a)]))
    c.drawRect(skia.Rect.MakeXYWH(l, y0, w, h), p)
    cx, cy = l + w / 2, y0 + h * 0.42
    bob = math.sin(t * 2.2) * h * 0.012
    bloom(c, cx, cy + bob, w * 0.55, a * 0.35 * (0.5 + lit))
    shape(c, kind, cx, cy + bob, w * 0.36, mix(DARK, GOLD, 0.4 + 0.6 * lit), a)
    for i, lw in enumerate((0.55, 0.38)):
        yy = y0 + h * (0.8 + 0.045 * i)
        c.drawLine(l + w * 0.08, yy, l + w * (0.08 + lw), yy, paint(MUTED, a * 0.7, max(4, w * 0.014)))
    for i in range(3):
        c.drawCircle(l + w * 0.88, y0 + h * (0.55 + 0.085 * i), w * 0.035, paint(LIGHT, a * 0.55))
    c.drawLine(l, y0 + h - 6, l + w * clamp01(progress), y0 + h - 6, paint(GOLD, a * 0.9, 5))


def status_bar(c: skia.Canvas, l: float, tp: float, w: float, clock: str, battery: float, a: float):
    s = w * 0.05
    text(c, clock, l + w * 0.09, tp + s * 1.4, s, "b", LIGHT, a, "left")
    bx, by, bw, bh = l + w * 0.78, tp + s * 1.4, w * 0.09, s * 0.62
    rrect(c, bx + bw / 2, by, bw, bh, 4, stroke=LIGHT, sa=a * 0.8, sw=2)
    fill = GOLD if battery > 0.2 else "#C8693C"
    c.drawRect(skia.Rect.MakeXYWH(bx + 3, by - bh / 2 + 3, (bw - 6) * battery, bh - 6), paint(fill, a))


def swipe_feed(c, l, tp, w, h, t: float, swipes: list[float], kinds: list[str], a: float = 1.0,
               dur: float = 0.42):
    """按 swipes 时刻依次上滑的信息流；滑动中带残影（运动模糊）。返回当前是第几条。"""
    idx, off = 0, 0.0
    for i, s in enumerate(swipes):
        if t >= s + dur:
            idx = i + 1
        elif t >= s:
            idx, off = i, ease_in_out(prog(t, s, dur))
            break
    for ghost in ((0.0, 1.0), (0.05, 0.25), (0.1, 0.12)) if 0 < off < 1 else ((0.0, 1.0),):
        o = max(0.0, off - ghost[0])
        ga = a * ghost[1]
        start = swipes[idx - 1] + dur if idx > 0 else 0.0
        feed_card(c, l, tp, w, h, -o * h, kinds[idx % len(kinds)], t, ga, 0.6,
                  progress=prog(t, start, 2.5))
        feed_card(c, l, tp, w, h, (1 - o) * h, kinds[(idx + 1) % len(kinds)], t, ga, 0.6)
    return idx, off


def touch(c: skia.Canvas, x: float, y0: float, y1: float, k: float, a: float):
    """手指滑动示意：触点 + 拖尾。k 为滑动进度。"""
    if a <= 0 or not 0 < k < 1:
        return
    y = lerp(y0, y1, ease_in_out(k))
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([(x, y0), (x, y)], [col(WARM, 0), col(WARM, a * 0.5)]))
    p.setStyle(skia.Paint.kStroke_Style)
    p.setStrokeWidth(18)
    p.setStrokeCap(skia.Paint.kRound_Cap)
    c.drawLine(x, lerp(y0, y, 0.3), x, y, p)
    bloom(c, x, y, 70, a * 0.5, WARM)
    c.drawCircle(x, y, 26, paint("#FFFFFF", a * 0.75))


# ---------------------------------------------------------------- 场景框架

def layer(c: skia.Canvas, t: float, t0: float, t1: float, fn, zoom_in: float = 0.06, zoom_out: float = 0.08,
          fin: float = 0.5, fout: float = 0.5):
    """场景容器：t0 起淡入并从略小推近，t1 前开始淡出并继续推近（镜头感）。"""
    if not t0 <= t < t1:
        return
    a = life(t, t0, t1 - fout, fin, fout)
    if a <= 0:
        return
    k = 1 - zoom_in * (1 - ease_out(prog(t, t0, fin + 0.3))) + zoom_out * ease_in(prog(t, t1 - fout, fout))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(k, k)
    c.translate(-W / 2, -H / 2)
    if a < 0.999:
        c.saveLayerAlpha(None, int(a * 255))
        fn(c, t)
        c.restore()
    else:
        fn(c, t)
    c.restore()


# ---------------------------------------------------------------- A 0–8 秒：第一视角开场

HOOK_SWIPES = [1.0, 2.3, 3.05, 3.55, 3.95, 4.25, 4.5]
HOOK_CLOCK = ["23:07", "23:16", "23:31", "23:52", "00:08", "00:24", "00:37", "00:41"]
KINDS = ["circle", "tri", "square", "diamond"]


def scene_hook(c: skia.Canvas, t: float):
    # 镜头：开场手机占满画面，4.7 秒后后拉、压暗，让位给标题
    pull = ease_in_out(prog(t, 4.7, 1.0))
    py, pw, ph = lerp(1010, 1240, pull), lerp(560, 420, pull), lerp(1120, 840, pull)
    screen_on = ease_out(prog(t, 0.0, 0.6))
    dim = 0.55 * pull

    def screen(c, l, tp, w, h):
        idx, off = swipe_feed(c, l, tp, w, h, t, HOOK_SWIPES, KINDS, screen_on)
        ci = min(len(HOOK_CLOCK) - 1, idx + (1 if off > 0.5 else 0))
        status_bar(c, l, tp, w, HOOK_CLOCK[ci], lerp(0.64, 0.18, ci / (len(HOOK_CLOCK) - 1)), screen_on)
        if dim > 0:
            c.drawRect(skia.Rect.MakeXYWH(l, tp, w, h), paint("#000000", dim))

    phone(c, CX, py, pw, ph, 1.0, screen, light=screen_on * (1 - 0.5 * pull))
    for s in HOOK_SWIPES:
        touch(c, CX + 60, py + ph * 0.3, py - ph * 0.15, prog(t, s - 0.05, 0.45), 1 - pull)
    # 时间跳动时的小标记
    for i, s in enumerate(HOOK_SWIPES[1:], 1):
        ring_burst(c, CX - pw / 2 + pw * 0.15, py - ph / 2 + pw * 0.07, t, s + 0.2, 10, 60, 0.8 * (1 - pull))
    # 文字
    a1 = life(t, 1.3, 2.25, 0.2, 0.3)
    if a1 > 0:
        k = lerp(1.2, 1.0, ease_out_back(prog(t, 1.3, 0.3)))
        c.save()
        c.translate(CX, 300)
        c.scale(k, k)
        text(c, "再刷一条……", 0, 0, 72, "k", LIGHT, a1, glow=0.4)
        c.restore()
    a2 = life(t, 2.45, 4.55, 0.2, 0.3)
    if a2 > 0:
        text(c, "又一条……", CX, 300, 64, "b", LIGHT, a2 * 0.9)
    slam(c, ["为什么你刷短视频", "停不下来？"], CX, 330, 82, 160, t, 4.9, None, gold_rows=(1,), stagger=0.6)
    sweep(c, "停不下来？", CX, 490, 82, "k", 1.0, t, 6.3, 1.0)


def scene_hook_out(c: skia.Canvas, t: float):
    """7.2–8.4 秒：一束光从屏幕射出，拉成时间线（转场）。"""
    k = ease_in_out(prog(t, 7.2, 1.0))
    a = 1 - prog(t, 8.0, 0.4)
    y = lerp(1240, 760, k)
    bloom(c, CX, y, lerp(120, 260, k), 0.6 * a, WARM)
    streak(c, CX, y, lerp(0, 1000, k), a, 4)


# ---------------------------------------------------------------- B 8–32 秒：历史

HIST_LINE_Y = 760
HIST_NODES = [  # (起点, 年份, 标签, 是否实心)
    (8.6, "1992", "技术发展", True),
    (15.6, "1997", "研究背景", False),
    (22.6, "2000s—2010s", "产品发展", True),
]


def hist_pan(t: float) -> float:
    """历史段镜头横移量（像素）：每个节点一屏。"""
    x = 0.0
    for i, (s, *_r) in enumerate(HIST_NODES[1:], 1):
        x += 1080 * ease_in_out(prog(t, s - 0.9, 0.9))
    return x


def scene_history(c: skia.Canvas, t: float):
    pan = hist_pan(t)
    over = ease_in_out(prog(t, 29.6, 0.9))   # 30 秒起缩成总览
    note(c, "历史背景 · 时间先后不代表因果", CX, 210, life(t, 8.6, 29.6))
    c.save()
    c.translate(-pan * (1 - over), 0)
    # 光线时间轴：贯穿三屏
    head = lerp(-100, 3 * 1080 + 200, clamp01((t - 8.0) / 21.0))
    polyline(c, [(-100, HIST_LINE_Y), (head, HIST_LINE_Y)], 1, mix(DARK, GOLD, 0.4), 1 - over, 3, glow=0.5)
    orb(c, head, HIST_LINE_Y, 9, 1 - over)
    for i, (s, year, tag, filled) in enumerate(HIST_NODES):
        x0 = CX + i * 1080
        on = prog(t, s, 0.4)
        if on > 0:
            c.drawCircle(x0, HIST_LINE_Y, 14, paint(GOLD, (1 - over)))
            ring_burst(c, x0, HIST_LINE_Y, t, s, 14, 120)
            bloom(c, x0, HIST_LINE_Y, 90, 0.35 * (1 - over))
        ya = life(t, s, None, 0.3) * (1 - over)
        if ya > 0:
            yr = year if not year.isdigit() else str(int(lerp(1950, int(year), ease_out(prog(t, s, 0.9)))))
            size = 150 if year.isdigit() else 104
            text(c, yr, x0, 560, size, "k", LIGHT, ya, gold=True, glow=0.5 + bump(t, s + 0.8, 0.8))
            chip(c, tag, x0, 670, ya * life(t, s + 0.6), filled)
    c.restore()
    loc = t
    if t < 29.9:
        node = 0 if t < HIST_NODES[1][0] - 0.5 else 1 if t < HIST_NODES[2][0] - 0.5 else 2
        start = HIST_NODES[node][0]
        nxt = HIST_NODES[node + 1][0] - 0.9 if node < 2 else 29.6
        c.save()
        c.translate(-(pan - node * 1080), 0)
        a = life(loc, start + 0.4, nxt - 0.3, 0.4, 0.4)
        if a > 0:
            [vig_1992, vig_1997, vig_scroll][node](c, loc, start, a)
        c.restore()
    if over > 0:
        hist_overview(c, t, over)


def vig_1992(c: skia.Canvas, t: float, s: float, a: float):
    """1992：别人的标注（星标）筛出文档，流向“你”。"""
    xs = [180, 330, 480, 630, 780]
    stars = {0: 2.6, 2: 3.0, 3: 3.3}
    for i, x in enumerate(xs):
        da = a * life(t, s + 0.8 + 0.12 * i)
        drop = (1 - ease_out_back(prog(t, s + 0.8 + 0.12 * i, 0.5), 1.2)) * 140
        st = prog(t, s + stars[i], 0.4) if i in stars else 0
        flow = ease_in_out(prog(t, s + 4.0 + 0.15 * i, 0.9))
        y = 960 - drop
        dim = ease_out(prog(t, s + 4.0, 0.6)) if i not in stars else 0
        if i in stars:
            x, y = lerp(x, CX, flow), lerp(y, 1330, flow)
            sc = 1 - 0.45 * flow
        else:
            sc = 1
        doc_card(c, x, y, 120 * sc, 150 * sc, da * (1 - 0.9 * flow if i in stars and flow > 0.95 else 1), st, dim)
    # 其他用户：发出星标光点
    for j, (px, tgt) in enumerate(((150, 0), (480, 2), (810, 3))):
        pa = a * life(t, s + 1.9)
        person(c, px, 1180, 56, pa)
        st = s + list(stars.values())[j] - 0.55
        k = prog(t, st, 0.55)
        if 0 < k < 1:
            p = bezier((px, 1140), ((px + xs[tgt]) / 2, 1080), (xs[tgt] + 50, 900), ease_in_out(k))
            orb(c, p[0], p[1], 7, a)
    note(c, "其他人的标注", 480, 1250, a * life(t, s + 2.0))
    note(c, "Goldberg 等, 1992", RIGHT, 1380, a * life(t, s + 4.6), "right")
    # 你
    ya = a * life(t, s + 4.4)
    rrect(c, CX, 1380, 150, 90, 16, stroke=GOLD, sa=ya, sw=3, glow=ya * bump(t, s + 4.9, 0.8))
    text(c, "你", CX, 1380, 44, "b", GOLD, ya)
    caption(c, "别人的反馈，帮你筛选", 1500, t, s + 4.6, None, 60,
            sub="协同过滤 · 推荐系统的早期源头之一")


def vig_1997(c: skia.Canvas, t: float, s: float, a: float):
    """1997：猴子实验中多巴胺信号对“意外的奖励”反应更强（示意，非原始数据）。"""
    rows = [(930, "意外的奖励", s + 1.2, None), (1190, "意料之中", s + 3.6, s + 3.0)]
    for y, label, t_rew, t_cue in rows:
        ra = a * life(t, t_rew - 0.9 if t_cue is None else t_cue - 0.6)
        if ra <= 0:
            continue
        text(c, label, LEFT, y - 70, 40, "b", LIGHT, ra, "left")
        x0, x1 = LEFT, RIGHT
        scan = prog(t, (t_cue or t_rew) - 0.8, 2.6)
        xr = lerp(x0, x1, 0.62)
        xc = lerp(x0, x1, 0.32)
        pts = []
        for i in range(161):
            u = i / 160
            x = lerp(x0, x1, u)
            v = 0.0
            if t_cue is None:
                v += math.exp(-((x - xr) / 16) ** 2) * 70
            else:
                v += math.exp(-((x - xc) / 16) ** 2) * 52
            v += 3 * math.sin(i * 1.7 + y)
            pts.append((x, y + 40 - v))
        end = polyline(c, pts, scan, GOLD, ra, 3, glow=0.6)
        if 0 < scan < 1:
            orb(c, end[0], end[1], 6, ra)
        # 奖励水滴落下 / 提示灯
        dk = prog(t, t_rew - 0.5, 0.5)
        if dk > 0:
            dy = lerp(y - 140, y - 10, ease_in(dk))
            drop(c, xr, dy, 14, ra * (1 - prog(t, t_rew + 0.2, 0.4)))
            if dk >= 1:
                ring_burst(c, xr, y + 40, t, t_rew, 6, 70, ra)
        if t_cue is not None:
            ca = ra * life(t, t_cue - 0.1)
            c.drawCircle(xc, y - 100, 13, paint(GOLD, ca))
            bloom(c, xc, y - 100, 60, ca * 0.6 * (0.4 + bump(t, t_cue, 0.8)))
            note(c, "提示", xc + 26, y - 100, ca, "left")
        note(c, "奖励", xr + 24, y - 100, ra * life(t, t_rew - 0.6), "left")
    note(c, "示意 · 非原始数据", RIGHT, 1310, a * life(t, s + 1.0), "right")
    caption(c, "多巴胺：对“意外”反应更强", 1440, t, s + 4.6, None, 58,
            sub="猴子实验，只是理论线索；多巴胺不是“快乐物质”")


def drop(c: skia.Canvas, x: float, y: float, r: float, a: float):
    if a <= 0:
        return
    p = skia.Path()
    p.moveTo(x, y - r * 1.8)
    p.cubicTo(x + r * 0.2, y - r * 1.0, x + r, y - r * 0.4, x + r, y + r * 0.2)
    p.cubicTo(x + r, y + r * 0.8, x + r * 0.5, y + r * 1.1, x, y + r * 1.1)
    p.cubicTo(x - r * 0.5, y + r * 1.1, x - r, y + r * 0.8, x - r, y + r * 0.2)
    p.cubicTo(x - r, y - r * 0.4, x - r * 0.2, y - r * 1.0, x, y - r * 1.8)
    bloom(c, x, y, r * 3, a * 0.5)
    c.drawPath(p, paint(WARM, a))


def vig_scroll(c: skia.Canvas, t: float, s: float, a: float):
    """2000s—2010s：“下一页”按钮化为光点消散，列表无限延伸；自动播放倒计时自动接下一条。"""
    lx, top, pw, ph = 290, 860, 340, 520
    rrect(c, lx, top + ph / 2, pw + 14, ph + 14, 26, stroke=mix(DARK, GOLD, 0.4), sa=a * life(t, s + 0.6), sw=3)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(lx - pw / 2, top, pw, ph))
    gone = prog(t, s + 2.4, 0.6)
    scroll = 170 * max(0.0, t - (s + 2.9)) if gone >= 1 else 0
    for i in range(40):
        y = top + 60 + i * 110 - scroll
        if y < top - 60 or y > top + ph + 60:
            continue
        ia = a * life(t, s + 0.7 + 0.08 * min(i, 6))
        rrect(c, lx, y, pw - 40, 88, 12, fill="#141519", fa=ia, stroke=DARK, sa=ia * 0.7, sw=2)
        shape(c, KINDS[i % 4], lx - pw / 2 + 60, y, 36, DARK, ia)
        c.drawLine(lx - pw / 2 + 100, y - 10, lx + pw / 2 - 40, y - 10, paint(DARK, ia * 0.8, 5))
    c.restore()
    by = top + ph - 50
    if gone < 1:
        ba = a * life(t, s + 1.2) * (1 - gone)
        rrect(c, lx, by, 200, 64, 32, fill="#1C1912", fa=ba, stroke=GOLD, sa=ba, sw=3, glow=ba * 0.5)
        text(c, "下一页 ›", lx, by, 34, "b", GOLD, ba)
    if gone > 0:
        rnd = random.Random(3)
        for k in range(26):
            ang = rnd.uniform(0, 6.28)
            sp = rnd.uniform(60, 220)
            px = lx + math.cos(ang) * sp * ease_out(gone)
            py = by + math.sin(ang) * sp * ease_out(gone) - 80 * gone
            pa = a * (1 - gone) * 0.9
            c.drawCircle(px, py, 4, paint(WARM, pa))
            bloom(c, px, py, 16, pa * 0.5)
    note(c, "无限滚动", lx, top + ph + 56, a * life(t, s + 3.0))
    # 自动播放
    rx, ry, rw, rh = 690, 1060, 300, 400
    aa = a * life(t, s + 3.6)
    if aa > 0:
        cycle = max(0.0, t - (s + 4.2))
        k = (cycle % 1.6) / 1.6
        n = int(cycle // 1.6)
        rrect(c, rx, ry, rw + 14, rh + 14, 26, stroke=mix(DARK, GOLD, 0.4), sa=aa, sw=3)
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(rx - rw / 2, ry - rh / 2, rw, rh))
        slide = ease_in_out(prog(k, 0.8, 0.2))
        feed_card(c, rx - rw / 2, ry - rh / 2, rw, rh, -slide * rh, KINDS[n % 4], t, aa, 0.5)
        feed_card(c, rx - rw / 2, ry - rh / 2, rw, rh, (1 - slide) * rh, KINDS[(n + 1) % 4], t, aa, 0.5)
        c.restore()
        ring = min(1.0, k / 0.8)
        c.drawArc(skia.Rect.MakeXYWH(rx - 44, ry + rh / 2 - 120, 88, 88), -90, 360 * ring, False,
                  paint(GOLD, aa, 6))
        text(c, str(max(1, 3 - int(ring * 3))), rx, ry + rh / 2 - 76, 40, "k", LIGHT, aa)
        note(c, "自动播放", rx, ry + rh / 2 + 56, aa)
    caption(c, "“下一页”消失了", 1520, t, s + 4.9, None, 60, sub="无限滚动、自动播放逐渐普及")


def hist_overview(c: skia.Canvas, t: float, over: float):
    """30–32 秒：三个节点并排的总览，强调“时间先后不代表因果”。"""
    a = over * (1 - prog(t, 31.6, 0.5))
    y = 960
    polyline(c, [(LEFT, y), (RIGHT, y)], over, mix(DARK, GOLD, 0.5), a, 3, glow=0.6)
    for i, (s, year, tag, filled) in enumerate(HIST_NODES):
        x = [190, 480, 770][i]
        c.drawCircle(x, y, 14, paint(GOLD, a))
        bloom(c, x, y, 80, a * 0.4)
        text(c, year, x, y - 80, 46 if year.isdigit() else 34, "k", LIGHT, a, gold=True)
        chip(c, tag, x, y + 70, a, filled, 28)
    text(c, "时间先后 ≠ 因果", CX, 1200, 56, "b", LIGHT, a * life(t, 30.2), glow=0.3)
    sweep(c, "时间先后 ≠ 因果", CX, 1200, 56, "b", a, t, 30.7, 1.0)


# ---------------------------------------------------------------- C 32–50 秒：理论（示意循环）

LOOP = dict(cx=CX, cy=1080, rx=300, ry=430)
LOOP_LABELS = ["看到", "期待", "滑动", "新内容"]
LOOP_ANG = [-90, 0, 90, 180]


def loop_angle_theory(t: float) -> float:
    """光球在环上的角度：先逐站停靠（每站约 2.5 秒），41.5 秒后越转越快。"""
    stops = [(33.0, -90), (35.5, 0), (38.0, 90), (40.0, 180), (41.5, 270)]
    ang = -90.0
    for i, (ts, a) in enumerate(stops):
        if t >= ts:
            ang = a
            if i + 1 < len(stops):
                ang = lerp(a, stops[i + 1][1], ease_in_out(prog(t, stops[i + 1][0] - 0.9, 0.9)))
    if t > 41.5:
        dt = t - 41.5
        ang = 270 + 360 * (0.35 * dt + 0.09 * dt * dt)
    return ang


def draw_loop(c: skia.Canvas, t: float, a: float, cx: float, cy: float, rx: float, ry: float, angle: float | None,
              lit: list[float], width: float = 3, scale: float = 1.0, pause: float = 0.0, labels=LOOP_LABELS,
              trail: bool = False, glow: float = 0.4):
    """四节点示意循环：椭圆环 + 箭头 + 节点胶囊 + 沿环运动的光球；pause>0 时在“滑动→新内容”间插入暂停节点。"""
    if a <= 0:
        return
    for i in range(4):
        a0, a1 = LOOP_ANG[i] + 16, LOOP_ANG[i] + 74
        if i == 2 and pause > 0:
            polyline(c, ellipse_pts(cx, cy, rx, ry, a0, 135 - 12 * pause), 1, mix(DARK, GOLD, 0.5), a, width,
                     glow=glow)
            polyline(c, ellipse_pts(cx, cy, rx, ry, 135 + 12 * pause, a1), 1, mix(DARK, GOLD, 0.5), a, width,
                     head=12 * scale, glow=glow)
            continue
        polyline(c, ellipse_pts(cx, cy, rx, ry, a0, a1), 1, mix(DARK, GOLD, 0.5), a, width, head=12 * scale,
                 glow=glow)
    if angle is not None:
        if trail:
            for k in range(1, 14):
                x, y = ellipse_pt(cx, cy, rx, ry, angle - k * 4.5)
                c.drawCircle(x, y, (9 - k * 0.5) * scale, paint(WARM, a * (1 - k / 14) * 0.6))
        x, y = ellipse_pt(cx, cy, rx, ry, angle)
        orb(c, x, y, 11 * scale, a)
    for i, ang in enumerate(LOOP_ANG):
        x, y = ellipse_pt(cx, cy, rx, ry, ang)
        L = lit[i]
        w = (text_w(labels[i], 46 * scale, "b") + 60 * scale)
        bloom(c, x, y, 150 * scale, a * 0.5 * L)
        rrect(c, x, y, w, 88 * scale, 44 * scale, fill=mix("#101114", "#2C2517", L), fa=a,
              stroke=mix(DARK, GOLD, L), sa=a, sw=2 + 2 * L, glow=a * L * 0.6)
        text(c, labels[i], x, y, 46 * scale, "b", mix(MUTED, GOLD_HI, L), a)
    if pause > 0:
        x, y = ellipse_pt(cx, cy, rx, ry, 135)
        k = ease_out_back(clamp01(pause), 2.2)
        bloom(c, x, y, 160 * k * scale, a * 0.6)
        c.drawCircle(x, y, 60 * k * scale, paint(BG, a))
        pause_icon(c, x, y, 48 * k * scale, a)


def node_lit(t: float, angle: float, arrivals: list[float]) -> list[float]:
    """节点亮度：光球到站时亮起并缓慢回落。"""
    lit = []
    for i, ang in enumerate(LOOP_ANG):
        d = abs(((angle - ang + 180) % 360) - 180)
        near = clamp01(1 - d / 25)
        hold = life(t, arrivals[i], arrivals[i] + 2.0, 0.2, 0.6) if arrivals[i] else 0
        lit.append(max(near, hold * 0.8))
    return lit


def scene_theory(c: skia.Canvas, t: float):
    ang = loop_angle_theory(t)
    arrivals = [33.0, 35.5, 38.0, 40.0]
    lit = node_lit(t, ang, arrivals)
    laps = clamp01((t - 41.5) / 4.0)
    a = life(t, 32.2, None, 0.6)
    note(c, "示意模型 · 帮助理解，非实验结论", CX, 210, life(t, 32.6, 48.9))

    # 中央手机：随光球到站做出反应
    def screen(c, l, tp, w, h):
        swipes = [38.2, 40.2] + [41.5 + k * 0.62 for k in range(1, 12)]
        idx, off = swipe_feed(c, l, tp, w, h, t, swipes, ["tri", "circle", "diamond", "square"], 1.0, 0.35)
        status_bar(c, l, tp, w, "00:41", 0.18, 1.0)
        qa = life(t, 35.6, 37.9, 0.3, 0.3)
        if qa > 0:
            text(c, "？", l + w / 2, tp + h * 0.42, w * 0.5, "k", WARM, qa, glow=1.0)

    phone(c, CX, LOOP["cy"], 300, 600, a, screen, light=0.8)
    draw_loop(c, t, a, LOOP["cx"], LOOP["cy"], LOOP["rx"], LOOP["ry"], ang if t >= 32.8 else None, lit,
              width=3 + 6 * laps, trail=t > 41.5, glow=0.4 + 0.8 * laps)
    for i, ts in enumerate(arrivals):
        x, y = ellipse_pt(LOOP["cx"], LOOP["cy"], LOOP["rx"], LOOP["ry"], LOOP_ANG[i])
        ring_burst(c, x, y, t, ts, 40, 170)
    # 收拢：历史总览的三个光点飞入环
    k = prog(t, 32.0, 0.9)
    if k < 1:
        for j, x0 in enumerate((190, 480, 770)):
            p = bezier((x0, 960), (x0, 760), (480, 650), ease_in_out(k))
            orb(c, p[0], p[1], 9, 1 - k * 0.5)
    caption(c, "不知道下一条好不好看", 380, t, 33.3, 35.4, 60)
    caption(c, "这份不确定，让人期待", 380, t, 35.6, 37.9, 60)
    caption(c, "手一滑，下一条就来", 380, t, 38.1, 41.2, 60)
    caption(c, "重复多了，就成了习惯", 380, t, 42.6, 48.9, 60,
            sub="习惯研究综述（Wood & Rünger, 2016）", sub_t=43.5)


# ---------------------------------------------------------------- D 50–64 秒：推荐反馈

CORE = (650, 760)
REC_PHONE = (290, 1110, 300, 600)


def scene_rec(c: skia.Canvas, t: float):
    slam(c, ["为什么越刷", "越合你口味？"], CX, 320, 90, 130, t, 49.6, 52.4, gold_rows=(1,), stagger=0.4)
    note(c, "示意流程 · 各平台具体权重未公开", CX, 210, life(t, 52.6, 63.4))
    px, py, pw, ph = REC_PHONE
    a = life(t, 50.6, None, 0.5)
    deliver = [56.6 + 0.5 * k for k in range(4)] + [60.6 + 0.35 * k for k in range(6)]

    def screen(c, l, tp, w, h):
        swipe_feed(c, l, tp, w, h, t, [52.2, 53.0, 53.8] + deliver, ["square", "circle", "tri", "square",
                                                                      "circle", "tri", "circle", "tri"], 1.0, 0.35)

    phone(c, px, py, pw, ph, a, screen, light=0.8)
    # 推荐系统核心：旋转光环，接收反馈后转速与亮度上升
    ca = life(t, 51.4)
    spin = 40 * (t - 51.4) + 220 * ease_in(prog(t, 55.0, 2.0)) * max(0, t - 55.0)
    energy = 0.3 + 0.7 * ease_out(prog(t, 52.6, 3.4))
    cx, cy = CORE
    bloom(c, cx, cy, 260, ca * 0.35 * energy)
    for r, sw, span, sp in ((112, 4, 250, 1.0), (88, 3, 200, -1.6), (64, 6, 120, 2.4)):
        c.drawArc(skia.Rect(cx - r, cy - r, cx + r, cy + r), spin * sp, span, False,
                  paint(GOLD, ca * (0.5 + 0.5 * energy), sw, blur=0))
    c.drawCircle(cx, cy, 34, paint(WARM, ca * energy))
    bloom(c, cx, cy, 120, ca * energy * (0.5 + 0.5 * bump(t, 55.0, 1.2)), WARM)
    text(c, "推荐系统", cx, cy + 170, 44, "b", GOLD, ca)
    # 三种反馈：从手机飞向核心
    fb = [("看完", 52.6, True), ("点赞", 53.4, True), ("很快划走", 54.2, False)]
    for i, (lab, ts, good) in enumerate(fb):
        y = 1010 + i * 120
        x = 600
        fa = a * life(t, ts)
        k = lerp(1.25, 1.0, ease_out_back(prog(t, ts, 0.3)))
        c.save()
        c.translate(x, y)
        c.scale(k, k)
        chip(c, lab, 0, 0, fa, good, 36)
        c.restore()
        for j in range(5):
            u = (t - ts - 0.3 - j * 0.12) / 0.9
            if 0 < u < 1:
                p = bezier((x, y - 30), (x + 160, (y + cy) / 2), (cx + 40, cy + 60), ease_in_out(u))
                if good:
                    orb(c, p[0], p[1], 6, a * (1 - u * 0.3))
                else:
                    c.drawCircle(p[0], p[1], 5, paint(MUTED, a * 0.6 * (1 - u)))
    # 核心向手机吐出“更合口味”的内容
    for j, ts in enumerate(deliver):
        u = prog(t, ts - 0.7, 0.7)
        if 0 < u < 1:
            p = bezier((cx - 60, cy + 40), (px + 60, cy), (px, py - 120), ease_in_out(u))
            c.save()
            c.translate(*p)
            sc = lerp(1.0, 0.5, u)
            c.scale(sc, sc)
            rrect(c, 0, 0, 90, 120, 12, fill="#1C1912", fa=a, stroke=GOLD, sa=a, sw=3, glow=a * 0.6)
            shape(c, ["circle", "tri"][j % 2], 0, -6, 40, GOLD, a)
            c.restore()
    caption(c, "你的每次停留，都在“教”它", 1550, t, 57.4, None, 52,
            sub=None)
    note(c, "依据：TikTok 说明（2020）、YouTube 论文（2016）", CX, 1478, life(t, 57.8) * 0.9)


# ---------------------------------------------------------------- E 64–72 秒：停止节点

def scene_stop(c: skia.Canvas, t: float):
    note(c, "示意界面", CX, 210, life(t, 64.2, 71.4))
    top, ph, pw = 560, 760, 330
    lx, rx = 285, 680
    for x, lab in ((lx, "有终点"), (rx, "持续加载")):
        text(c, lab, x, 500, 48, "b", LIGHT, life(t, 64.3))
    off_l = 660 * ease_in_out(prog(t, 64.6, 1.8))

    def left(c, l, tp, w, h):
        for i in range(7):
            y = tp + 70 + i * 140 - off_l
            rrect(c, l + w / 2, y, w - 40, 118, 14, fill="#141519", fa=1, stroke=DARK, sa=0.8, sw=2)
            shape(c, KINDS[i % 4], l + 62, y, 40, DARK, 1)
            c.drawLine(l + 104, y - 12, l + w - 40, y - 12, paint(DARK, 0.8, 6))
        ey = tp + 70 + 7 * 140 - off_l - 20
        ea = prog(t, 66.2, 0.4)
        text(c, "— 到底了 —", l + w / 2, ey, 38, "b", GOLD, 0.6 + 0.4 * ea, glow=ea)

    def right(c, l, tp, w, h):
        sp = 260 + 520 * ease_in(prog(t, 68.6, 2.0))
        off = sp * max(0.0, t - 64.6)
        for g, ga in ((0, 1.0), (24, 0.25), (48, 0.12)):
            o = off - g * (sp / 400)
            for i in range(int(o // 140) - 1, int(o // 140) + 8):
                y = tp + 70 + i * 140 - o
                rrect(c, l + w / 2, y, w - 40, 118, 14, fill="#141519", fa=ga, stroke=DARK, sa=0.8 * ga, sw=2)
                shape(c, KINDS[i % 4], l + 62, y, 40, DARK, ga)
        cy = tp + h - 46
        c.drawCircle(l + w / 2, cy, 30, paint(BG, 1))
        c.drawArc(skia.Rect.MakeXYWH(l + w / 2 - 20, cy - 20, 40, 40), (t * 420) % 360, 260, False,
                  paint(GOLD, 1, 4))

    a = life(t, 64.2)
    phone(c, lx, top + ph / 2, pw, ph, a, left, light=0.6)
    phone(c, rx, top + ph / 2, pw, ph, a, right, light=0.6 + 0.6 * ease_in(prog(t, 68.6, 2.0)))
    na = life(t, 66.4)
    if na > 0:
        endy = top + 70 + 7 * 140 - 660 - 20
        ring_burst(c, lx, endy, t, 66.4, 30, 200)
        rrect(c, lx, endy, 280, 76, 38, stroke=GOLD, sa=na, sw=3, glow=na * (0.4 + bump(t, 66.4, 1.0)))
        text(c, "停止节点", lx, top + ph + 70, 48, "b", GOLD, na, glow=0.4)
    text(c, "没有终点", rx, top + ph + 70, 48, "b", MUTED, life(t, 67.0))
    caption(c, "少了一个“停下来”的点", 1490, t, 67.6, None, 56)
    note(c, "参考：Rixen 等（2023）无限滚动研究", CX, 1572, life(t, 68.0))


# ---------------------------------------------------------------- F 72–86 秒：方法

def scene_method(c: skia.Canvas, t: float):
    slam(c, ["怎样给自己", "一个暂停？"], CX, 320, 96, 140, t, 71.8, 74.3, gold_rows=(1,), stagger=0.4)
    cx, cy, rx, ry = CX, 1100, 290, 370
    a = life(t, 72.6, None, 0.6)
    stop_t = 78.2
    if t < stop_t:
        ang = -90 + 360 * (0.55 * (t - 72.6) + 0.04 * (t - 72.6) ** 2)
        # 收在暂停节点（135°）
        target = 135 + 360 * math.ceil(((-90 + 360 * (0.55 * (stop_t - 72.6) + 0.04 * (stop_t - 72.6) ** 2))
                                        - 135) / 360)
        k = prog(t, stop_t - 1.0, 1.0)
        ang = lerp(ang, target, ease_out(k))
    else:
        ang = 135.0
    pause = prog(t, stop_t, 0.5)
    lit = node_lit(t, ang, [0, 0, 0, 0]) if t < stop_t else [0.15] * 4
    locked = ease_in_out(prog(t, 81.2, 1.0))
    timer = prog(t, 75.4, stop_t - 75.4)

    def screen(c, l, tp, w, h):
        swipe_feed(c, l, tp, w, h, t, [73.4 + 0.75 * k for k in range(6)], KINDS, 1.0, 0.35)
        status_bar(c, l, tp, w, "23:07" if t < 79 else "23:22", 0.6, 1.0)
        if timer > 0:
            r = w * 0.2
            ta = life(t, 75.4) * (1 - locked)
            c.drawCircle(l + w / 2, tp + h * 0.25, r + 14, paint(BG, ta * 0.85))
            c.drawArc(skia.Rect(l + w / 2 - r, tp + h * 0.25 - r, l + w / 2 + r, tp + h * 0.25 + r), -90,
                      360 * timer, False, paint(GOLD, ta, 8))
            text(c, "计时", l + w / 2, tp + h * 0.25, w * 0.09, "b", LIGHT, ta)
            if timer >= 1:
                bloom(c, l + w / 2, tp + h * 0.25, r * 2.5, ta * bump(t, stop_t, 1.0))
        if locked > 0:
            c.drawRect(skia.Rect.MakeXYWH(l, tp, w, h), paint("#050506", locked * 0.94))
            text(c, "23:22", l + w / 2, tp + h * 0.3, w * 0.2, "k", LIGHT, locked, gold=True, glow=0.4)
            text(c, "已锁屏", l + w / 2, tp + h * 0.42, w * 0.07, "m", MUTED, locked)

    phone(c, cx, cy, 300, 600, a, screen, light=1 - 0.6 * locked)
    draw_loop(c, t, a * (1 - 0.3 * locked), cx, cy, rx, ry, ang, lit, pause=pause, trail=t < stop_t, glow=0.5)
    if t >= stop_t:
        x, y = ellipse_pt(cx, cy, rx, ry, 135)
        ring_burst(c, x, y, t, stop_t, 50, 260)
        ring_burst(c, x, y, t, stop_t + 0.25, 50, 200, 0.6)
        ring_burst(c, x, y, t, 83.6, 50, 320, 0.8)
        bloom(c, x, y, 220, 0.5 * bump(t, 83.6, 1.2), WARM)
    caption(c, "开刷前，设个计时", 1562, t, 75.2, 78.1, 52)
    # 如果—就 计划卡
    ka = life(t, 78.6)
    if ka > 0:
        dy = (1 - ease_out(prog(t, 78.6, 0.5))) * 30
        rrect(c, CX, 330 + dy, 816, 250, 26, fill="#16140F", fa=ka * 0.92, stroke=GOLD, sa=ka, sw=3,
              glow=ka * (0.3 + bump(t, 78.8, 1.0)))
        ia = life(t, 78.9)
        text(c, "如果", LEFT + 50, 280 + dy, 58, "k", GOLD, ia, "left", glow=0.3)
        text(c, "计时提醒响了", LEFT + 190, 280 + dy, 58, "b", LIGHT, ia, "left")
        ja = life(t, 79.7)
        text(c, "就", LEFT + 50, 380 + dy, 58, "k", GOLD, ja, "left", glow=0.3)
        text(c, "先锁屏，再决定", LEFT + 190, 380 + dy, 58, "b", LIGHT, ja, "left")
    note(c, "“如果—就”计划：Gollwitzer & Sheeran, 2006", CX, 1556, life(t, 81.6))
    note(c, "打开前加一道确认，约 36% 被放弃：Grüning 等, 2023", CX, 1598, life(t, 82.2))
    text(c, "不保证对每个人有效，可以试试", CX, 520, 38, "m", MUTED, life(t, 82.8))


# ---------------------------------------------------------------- G 86–91 秒：收束

def scene_close(c: skia.Canvas, t: float):
    def screen(c, l, tp, w, h):
        text(c, "23:22", l + w / 2, tp + h * 0.3, w * 0.2, "k", LIGHT, 1, gold=True, glow=0.3)

    a = life(t, 86.0, None, 0.6)
    phone(c, CX, 1220, 300, 600, a * 0.8, screen, light=0.3 + 0.4 * bump(t, 87.0, 3.0))
    caption(c, "下一条，一直都在", 380, t, 86.3, None, 66)
    al = life(t, 87.6, None, 0.3)
    if al > 0:
        k = lerp(1.15, 1.0, ease_out_back(prog(t, 87.6, 0.4), 1.4))
        c.save()
        c.translate(CX, 540)
        c.scale(k, k)
        text(c, "停在哪，由你决定。", 0, 0, 84, "k", LIGHT, al, gold=True, glow=0.4 + bump(t, 87.6, 1.0))
        c.restore()
        streak(c, CX, 600, 760 * ease_out(prog(t, 87.6, 0.6)), al * bump(t, 87.6, 1.0))
    sweep(c, "停在哪，由你决定。", CX, 540, 84, "k", al, t, 89.0, 1.1)


# ---------------------------------------------------------------- H 91–97 秒：参考资料

REFS = [
    "Goldberg D, et al. (1992). Using collaborative filtering to weave an information tapestry. Commun. ACM, 35(12).",
    "Schultz W, Dayan P, Montague PR (1997). A neural substrate of prediction and reward. Science, 275.",
    "Wood W, Rünger D (2016). Psychology of habit. Annu. Rev. Psychol., 67.",
    "Covington P, Adams J, Sargin E (2016). Deep neural networks for YouTube recommendations. RecSys '16.",
    "TikTok Newsroom (2020). How TikTok recommends videos #ForYou.",
    "Rixen JO, et al. (2023). The loop and reasons to break it: infinite scrolling behaviour in social media apps. MobileHCI '23.",
    "European Commission (2026-02-06). Preliminary findings on TikTok's addictive design under the DSA.",
    "Gollwitzer PM, Sheeran P (2006). Implementation intentions and goal achievement. Adv. Exp. Soc. Psychol., 38.",
    "Grüning DJ, Riedel F, Lorenz-Spreen P (2023). Directing smartphone use through the self-nudge app one sec. PNAS, 120(8).",
    "CNET (2015). How to turn off YouTube's new autoplay feature.",
]


def wrap_words(s: str, size: float, max_w: float, weight: str = "r") -> list[str]:
    out, cur = [], ""
    for word in s.split(" "):
        trial = f"{cur} {word}".strip()
        if cur and text_w(trial, size, weight) > max_w:
            out.append(cur)
            cur = word
        else:
            cur = trial
    return out + [cur] if cur else out


def scene_refs(c: skia.Canvas, t: float):
    a = life(t, 91.0, None, 0.6)
    text(c, "参考资料", LEFT, 210, 56, "k", GOLD, a, "left", gold=True)
    c.drawLine(LEFT, 262, LEFT + 160, 262, paint(DARK, a, 2))
    y = 330
    for i, ref in enumerate(REFS):
        ra = a * life(t, 91.2 + 0.06 * i)
        text(c, f"{i + 1:>2}", LEFT, y, 28, "b", GOLD, ra, "left")
        rows = wrap_words(ref, 28, RIGHT - LEFT - 52)
        for j, row in enumerate(rows):
            text(c, row, LEFT + 52, y + j * 38, 28, "r", LIGHT, ra, "left")
        y += 38 * len(rows) + 26
    text(c, "示意图仅帮助理解，不代表效果大小", LEFT, y + 30, 30, "m", DARK, a, "left")


# ---------------------------------------------------------------- 合成

def draw_frame(c: skia.Canvas, t: float):
    ambient(c, t)
    layer(c, t, 0.0, 7.6, scene_hook, zoom_in=0.0, zoom_out=0.25, fin=0.01, fout=0.7)
    if 7.2 <= t < 8.5:
        scene_hook_out(c, t)
    layer(c, t, 8.0, 32.4, scene_history, zoom_in=0.04, zoom_out=0.06, fin=0.4, fout=0.5)
    layer(c, t, 31.9, 49.6, scene_theory, zoom_in=0.06, zoom_out=0.1)
    layer(c, t, 49.4, 64.2, scene_rec, zoom_in=0.04, zoom_out=0.08)
    layer(c, t, 64.0, 71.9, scene_stop, zoom_in=0.04, zoom_out=0.08)
    layer(c, t, 71.6, 86.0, scene_method, zoom_in=0.04, zoom_out=0.06, fout=0.6)
    layer(c, t, 85.8, 91.2, scene_close, zoom_in=0.03, zoom_out=0.0, fout=0.6)
    if t >= 90.8:
        scene_refs(c, t)
    vignette(c)


# ---------------------------------------------------------------- 输出

_BUF: np.ndarray | None = None
_SURF: skia.Surface | None = None


def _render(frame: int) -> bytes:
    global _BUF, _SURF
    if _SURF is None:
        _BUF = np.zeros((H, W, 4), np.uint8)
        _SURF = skia.Surface(_BUF)
    draw_frame(_SURF.getCanvas(), frame / FPS)
    return _BUF.tobytes()


def still(t: float, path: str):
    buf = np.frombuffer(_render(int(round(t * FPS))), np.uint8).reshape(H, W, 4)
    skia.Image.fromarray(buf.copy()).save(path, skia.kPNG)


def render(out_path: str, workers: int = 4):
    """多进程逐帧渲染，经 FFmpeg 编码为不含音频流的 H.264 MP4。"""
    n = int(round(TOTAL * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        with get_context("fork").Pool(workers) as pool:
            for buf in pool.imap(_render, range(n), chunksize=8):
                proc.stdin.write(buf)
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")


# ---------------------------------------------------------------- 封面

def cover(path: str, w: int, h: int):
    """同风格封面：竖版 1080×1920，横版 1920×1080。"""
    arr = np.zeros((h, w, 4), np.uint8)
    surf = skia.Surface(arr)
    c = surf.getCanvas()
    c.clear(col(BG))

    def screen(c, l, tp, sw, sh):
        feed_card(c, l, tp, sw, sh, 0, "circle", 0.0, 1.0, 0.9, 0.6)
        status_bar(c, l, tp, sw, "00:41", 0.18, 1.0)

    if h > w:
        bloom(c, CX, 1250, 800, 0.1, "#3A2E18")
        text(c, "为什么你刷短视频", LEFT, 360, 92, "k", LIGHT, 1, "left", glow=0.3)
        text(c, "停不下来？", LEFT, 510, 140, "k", LIGHT, 1, "left", gold=True, glow=0.6)
        streak(c, 400, 600, 700, 0.8)
        draw_loop(c, 0, 1, CX, 1180, 290, 400, -30, [0.9, 0.3, 0.3, 0.3], pause=1.0, glow=0.6)
        phone(c, CX, 1180, 300, 600, 1, screen)
        text(c, "无声科普 · 历史 / 理论 / 方法", LEFT, 1660, 34, "m", MUTED, 1, "left")
    else:
        bloom(c, 1440, 540, 700, 0.1, "#3A2E18")
        text(c, "为什么你刷短视频", 110, 380, 92, "k", LIGHT, 1, "left", glow=0.3)
        text(c, "停不下来？", 110, 530, 140, "k", LIGHT, 1, "left", gold=True, glow=0.6)
        streak(c, 440, 620, 700, 0.8)
        text(c, "无声科普 · 历史 / 理论 / 方法", 110, 760, 34, "m", MUTED, 1, "left")
        draw_loop(c, 0, 1, 1440, 540, 260, 330, -30, [0.9, 0.3, 0.3, 0.3], pause=1.0, scale=0.85, glow=0.6)
        phone(c, 1440, 540, 220, 440, 1, screen)
    vignette_c(c, w, h)
    skia.Image.fromarray(arr.copy()).save(path, skia.kPNG)


def vignette_c(c: skia.Canvas, w: int, h: int):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((w / 2, h / 2), max(w, h) * 0.72,
                                               [col("#000000", 0), col("#000000", 0), col("#000000", 0.5)],
                                               [0.0, 0.62, 1.0]))
    c.drawRect(skia.Rect(0, 0, w, h), p)


def main():
    args = sys.argv[1:]
    if args and args[0] == "--still":
        out = ROOT / "out" / "stills"
        out.mkdir(parents=True, exist_ok=True)
        for s in args[1:]:
            still(float(s), str(out / f"t{float(s):06.2f}.png"))
        return
    out_path = Path(args[0] if args else ROOT / "out" / "scroll_short.mp4")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cover(str(out_path.with_name("scroll_cover_vertical.png")), 1080, 1920)
    cover(str(out_path.with_name("scroll_cover_horizontal.png")), 1920, 1080)
    render(str(out_path))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
