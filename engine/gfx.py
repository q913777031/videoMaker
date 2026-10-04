"""Skia 绘图工具集：缓动、字体回退、文字特效、Emoji、形状、背景粒子与后期效果。

所有函数都是"时间的纯函数"：相同参数必然画出相同结果，便于多进程并行逐帧渲染。
坐标约定：除特别说明外，(x, y) 均为元素中心点；文字的 y 为视觉中线。
"""

import functools
import math
from pathlib import Path

import numpy as np
import skia

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"
EMOJI_DIR = ROOT / "assets" / "emoji"
W, H = 1080, 1920

FONT_FILES = {
    "title": "SmileySans-Oblique.ttf",
    "black": "NotoSansCJKsc-Black.otf",
    "bold": "NotoSansCJKsc-Bold.otf",
}
SAMPLING = skia.SamplingOptions(skia.CubicResampler.Mitchell())
CONFETTI = ("#FF5E7E", "#FFD23F", "#3BCEAC", "#4CC9F0", "#B388FF", "#FF9F1C")


# ---------------------------------------------------------------- 缓动

def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def lerp(a: float, b: float, x: float) -> float:
    return a + (b - a) * x


def ease_out(x: float) -> float:
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in(x: float) -> float:
    return clamp01(x) ** 3


def ease_in_out(x: float) -> float:
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_back(x: float, s: float = 1.70158) -> float:
    x = clamp01(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def prog(t: float, start: float, dur: float = 0.4) -> float:
    """从 start 开始、持续 dur 秒的线性进度 [0, 1]。"""
    return clamp01((t - start) / dur) if dur > 0 else float(t >= start)


# ---------------------------------------------------------------- 颜色

@functools.lru_cache(maxsize=None)
def rgb(c) -> tuple:
    """"#RRGGBB" 或 (r, g, b) 统一为 (r, g, b)。"""
    if isinstance(c, str):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(v) for v in c[:3])


def col(c, a: float = 1.0) -> int:
    r, g, b = rgb(c)
    return skia.Color(r, g, b, int(255 * clamp01(a)))


def mix(c1, c2, x: float) -> tuple:
    a, b = rgb(c1), rgb(c2)
    return tuple(int(p + (q - p) * clamp01(x)) for p, q in zip(a, b))


# ---------------------------------------------------------------- 字体与文字

@functools.lru_cache(maxsize=None)
def typeface(name: str) -> skia.Typeface:
    tf = skia.Typeface.MakeFromFile(str(FONT_DIR / FONT_FILES[name]))
    if tf is None:
        raise FileNotFoundError(f"font not found: {FONT_FILES[name]}")
    return tf


@functools.lru_cache(maxsize=4096)
def _font(name: str, size: float) -> skia.Font:
    f = skia.Font(typeface(name), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def font(name: str, size: float) -> skia.Font:
    return _font(name, round(size * 2) / 2)


@functools.lru_cache(maxsize=8192)
def runs(text: str, name: str) -> tuple:
    """把文本切成 (片段, 字体名) 序列；首选字体缺字的字符回退到思源黑体 Black。"""
    if name == "black":
        return ((text, "black"),)
    glyphs = typeface(name).unicharsToGlyphs([ord(ch) for ch in text])
    out: list[list[str]] = []
    for ch, g in zip(text, glyphs):
        n = name if g != 0 else "black"
        if out and out[-1][1] == n:
            out[-1][0] += ch
        else:
            out.append([ch, n])
    return tuple((s, n) for s, n in out)


def text_width(text: str, size: float, name: str = "black") -> float:
    return sum(font(n, size).measureText(s) for s, n in runs(text, name))


def parse_marks(text: str) -> list[tuple[str, bool]]:
    """解析【关键词】标记，返回 (片段, 是否高亮) 列表。"""
    out, hi, buf = [], False, ""
    for ch in text:
        if ch in "【】":
            if buf:
                out.append((buf, hi))
            buf, hi = "", ch == "【"
        else:
            buf += ch
    if buf:
        out.append((buf, hi))
    return out


def plain(text: str) -> str:
    return text.replace("【", "").replace("】", "")


def _blur(sigma: float) -> skia.MaskFilter:
    return skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(sigma, 0.1))


def _text_paints(alpha, y, size, fill, stroke, glow, shadow, gradient):
    """按绘制顺序生成 (画笔, dx, dy) 图层：阴影 → 外发光 → 描边 → 填充。"""
    layers = []
    if shadow:
        dx, dy, blur, sc = shadow
        layers.append((skia.Paint(AntiAlias=True, Color=col(sc, 0.55 * alpha), MaskFilter=_blur(blur)), dx, dy))
    if glow:
        gc, sigma = glow
        layers.append((skia.Paint(AntiAlias=True, Color=col(gc, alpha), MaskFilter=_blur(sigma)), 0, 0))
    if stroke:
        sc, sw = stroke
        layers.append((skia.Paint(AntiAlias=True, Color=col(sc, alpha), Style=skia.Paint.kStroke_Style,
                                  StrokeWidth=sw, StrokeJoin=skia.Paint.kRound_Join), 0, 0))
    fp = skia.Paint(AntiAlias=True, Color=col(fill, alpha))
    if gradient:
        fp.setShader(skia.GradientShader.MakeLinear(
            [(0, y - size * 0.55), (0, y + size * 0.45)], [col(g, alpha) for g in gradient]))
    layers.append((fp, 0, 0))
    return layers


def draw_text(c: skia.Canvas, text: str, x: float, y: float, size: float, name: str = "black",
              fill="#FFFFFF", alpha: float = 1.0, align: str = "center", stroke=None, glow=None,
              shadow=None, gradient=None) -> float:
    """绘制单行文字并返回宽度。stroke=(色, 宽)，glow=(色, 模糊)，shadow=(dx, dy, 模糊, 色)，
    gradient=[上色, 下色] 时覆盖 fill。"""
    if alpha <= 0 or not text:
        return 0.0
    w = text_width(text, size, name)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    base = y + size * 0.36
    pieces, cx = [], x0
    for s, n in runs(text, name):
        f = font(n, size)
        pieces.append((skia.TextBlob.MakeFromString(s, f), cx))
        cx += f.measureText(s)
    for p, dx, dy in _text_paints(alpha, y, size, fill, stroke, glow, shadow, gradient):
        for blob, bx in pieces:
            c.drawTextBlob(blob, bx + dx, base + dy, p)
    return w


def draw_rich(c: skia.Canvas, text: str, x: float, y: float, size: float, name: str = "black",
              fill="#FFFFFF", hi="#FFE14D", alpha: float = 1.0, align: str = "center", stroke=None,
              glow=None, shadow=None) -> float:
    """绘制带【关键词】高亮的单行文字，返回宽度。"""
    segs = parse_marks(text)
    w = sum(text_width(s, size, name) for s, _ in segs)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    for s, h in segs:
        x0 += draw_text(c, s, x0, y, size, name, hi if h else fill, alpha, "left", stroke, glow, shadow)
    return w


@functools.lru_cache(maxsize=4096)
def _char_layout(text: str, size: float, name: str) -> tuple:
    """逐字的 (字符, 字体名, 宽度)，用于逐字动画排版。"""
    out = []
    for s, n in runs(text, name):
        f = font(n, size)
        out.extend((ch, n, f.measureText(ch)) for ch in s)
    return tuple(out)


def draw_kinetic(c: skia.Canvas, text: str, x: float, y: float, size: float, t: float, start: float,
                 name: str = "title", style: str = "pop", stagger: float = 0.045, dur: float = 0.4,
                 fill="#FFFFFF", hi="#FFE14D", alpha: float = 1.0, stroke=None, glow=None, shadow=None,
                 gradient=None, align: str = "center"):
    """逐字入场动画文字，支持【关键词】高亮。style：pop 弹出 / slam 砸入 / rise 上浮 / drop 下落 / zoom 放大。"""
    if alpha <= 0 or t < start:
        return
    colors = []
    for s, h in parse_marks(text):
        colors.extend([hi if h else fill] * len(s))
    layout = _char_layout(plain(text), size, name)
    w = sum(cw for _, _, cw in layout)
    cx = x - w / 2 if align == "center" else x - w if align == "right" else x
    for i, (ch, n, cw) in enumerate(layout):
        p = prog(t, start + i * stagger, dur)
        mid = cx + cw / 2
        cx += cw
        if p <= 0:
            continue
        s, dy, a = 1.0, 0.0, 1.0
        if style == "pop":
            s, a = ease_out_back(p, 2.2), clamp01(p * 2.5)
        elif style == "slam":
            s, a = 1 + 1.5 * (1 - ease_out(p)), clamp01(p * 3)
        elif style == "rise":
            dy, a = (1 - ease_out(p)) * size * 0.7, clamp01(p * 2)
        elif style == "drop":
            dy, a = -(1 - ease_out_back(p)) * size * 0.9, clamp01(p * 3)
        elif style == "zoom":
            s, a = 0.3 + 0.7 * ease_out(p), p
        c.save()
        c.translate(mid, y + dy)
        c.scale(s, s)
        draw_text(c, ch, 0, 0, size, n, colors[i], alpha * a, "center", stroke, glow, shadow, gradient)
        c.restore()


# ---------------------------------------------------------------- Emoji

def emoji_file(name: str) -> str:
    """与 fetch_assets.emoji_file 保持一致的文件名映射。"""
    return name.lower().replace(" ", "_").replace("-", "_") + ".png"


@functools.lru_cache(maxsize=None)
def emoji_image(name: str) -> skia.Image:
    path = EMOJI_DIR / emoji_file(name)
    img = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(path))) if path.exists() else None
    if img is None:
        raise FileNotFoundError(f"emoji not found: {path}")
    return img


@functools.lru_cache(maxsize=64)
def _gray_filter(g: float) -> skia.ColorFilter:
    """按比例 g 把颜色向灰度插值的颜色矩阵。"""
    lum = (0.299, 0.587, 0.114)
    m = []
    for row in range(3):
        for k in range(3):
            m.append((1 - g) * (1.0 if row == k else 0.0) + g * lum[k])
        m += [0.0, 0.0]
    m += [0.0, 0.0, 0.0, 1.0, 0.0]
    return skia.ColorFilters.Matrix(m)


def draw_emoji(c: skia.Canvas, name: str, x: float, y: float, size: float, alpha: float = 1.0,
               rot: float = 0.0, sx: float = 1.0, sy: float = 1.0, shadow: float = 0.3, glow=None,
               gray: float = 0.0):
    """以 (x, y) 为中心绘制 3D Emoji；sx/sy 用于挤压拉伸，glow=(色, 模糊) 在背后加光晕，gray 为去色比例。"""
    if alpha <= 0 or size <= 1:
        return
    img = emoji_image(name)
    if shadow > 0:
        sp = skia.Paint(AntiAlias=True, Color=col("#000000", shadow * alpha), MaskFilter=_blur(size * 0.05))
        c.drawOval(skia.Rect.MakeXYWH(x - size * 0.3 * sx, y + size * 0.44 * sy, size * 0.6 * sx, size * 0.1), sp)
    if glow:
        circle(c, x, y, size * 0.42, glow[0], 0.55 * alpha, blur=glow[1], blend=skia.BlendMode.kPlus)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(sx, sy)
    p = skia.Paint(AntiAlias=True, Alphaf=clamp01(alpha))
    if gray > 0:
        p.setColorFilter(_gray_filter(round(clamp01(gray), 2)))
    c.drawImageRect(img, skia.Rect.MakeXYWH(-size / 2, -size / 2, size, size), SAMPLING, p)
    c.restore()


# ---------------------------------------------------------------- 形状

def rrect(c: skia.Canvas, x: float, y: float, w: float, h: float, r: float, fill=None, alpha: float = 1.0,
          stroke=None, shadow: float = 0.0, gradient=None):
    """以中心点绘制圆角矩形；stroke=(色, 宽)，shadow 为投影不透明度，gradient=[上色, 下色]。"""
    if alpha <= 0:
        return
    rect = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    if shadow > 0:
        sp = skia.Paint(AntiAlias=True, Color=col("#000000", shadow * alpha), MaskFilter=_blur(24))
        c.drawRoundRect(rect.makeOffset(0, 16), r, r, sp)
    if fill is not None or gradient:
        p = skia.Paint(AntiAlias=True, Color=col(fill or "#FFFFFF", alpha))
        if gradient:
            p.setShader(skia.GradientShader.MakeLinear(
                [(0, y - h / 2), (0, y + h / 2)], [col(g, alpha) for g in gradient]))
        c.drawRoundRect(rect, r, r, p)
    if stroke:
        p = skia.Paint(AntiAlias=True, Color=col(stroke[0], alpha), Style=skia.Paint.kStroke_Style,
                       StrokeWidth=stroke[1])
        c.drawRoundRect(rect, r, r, p)


def circle(c: skia.Canvas, x: float, y: float, r: float, fill, alpha: float = 1.0, blur: float = 0.0,
           blend=None):
    if alpha <= 0 or r <= 0:
        return
    p = skia.Paint(AntiAlias=True, Color=col(fill, alpha))
    if blur > 0:
        p.setMaskFilter(_blur(blur))
    if blend is not None:
        p.setBlendMode(blend)
    c.drawCircle(x, y, r, p)


def partial(path: skia.Path, p: float, start: float = 0.0) -> skia.Path:
    """截取路径 [start, p] 比例的一段，用于描线动画。"""
    pm = skia.PathMeasure(path, False)
    total = pm.getLength()
    seg = skia.Path()
    if p > start:
        pm.getSegment(total * clamp01(start), total * clamp01(p), seg, True)
    return seg


def stroke_path(c: skia.Canvas, path: skia.Path, color, width: float, alpha: float = 1.0, p: float = 1.0,
                glow=None, dash=None, cap=skia.Paint.kRound_Cap):
    """描边路径；p<1 时只画前段（描线动画），glow=(色, 模糊) 叠加发光，dash=(实, 虚, 相位)。"""
    if alpha <= 0 or p <= 0:
        return
    seg = path if p >= 1 else partial(path, p)
    paint = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width, StrokeCap=cap,
                       StrokeJoin=skia.Paint.kRound_Join)
    if dash:
        paint.setPathEffect(skia.DashPathEffect.Make([dash[0], dash[1]], dash[2]))
    if glow:
        gp = skia.Paint(paint)
        gp.setColor(col(glow[0], alpha))
        gp.setStrokeWidth(width * 1.6)
        gp.setMaskFilter(_blur(glow[1]))
        c.drawPath(seg, gp)
    paint.setColor(col(color, alpha))
    c.drawPath(seg, paint)


def check(c: skia.Canvas, x: float, y: float, size: float, p: float, color="#3BE07A", width: float = 14,
          alpha: float = 1.0):
    """以描线动画画一个对勾。"""
    path = skia.Path()
    path.moveTo(x - size * 0.45, y)
    path.lineTo(x - size * 0.1, y + size * 0.35)
    path.lineTo(x + size * 0.5, y - size * 0.4)
    stroke_path(c, path, color, width, alpha, ease_out(p))


def star4(c: skia.Canvas, x: float, y: float, r: float, color="#FFFFFF", alpha: float = 1.0, rot: float = 0.0):
    """四角闪光星。"""
    if alpha <= 0 or r <= 0:
        return
    path = skia.Path()
    for k in range(8):
        ang = math.radians(rot + k * 45)
        rr = r if k % 2 == 0 else r * 0.22
        px, py = x + rr * math.sin(ang), y - rr * math.cos(ang)
        path.lineTo(px, py) if k else path.moveTo(px, py)
    path.close()
    c.drawPath(path, skia.Paint(AntiAlias=True, Color=col(color, alpha)))
    circle(c, x, y, r * 0.5, color, alpha * 0.5, blur=r * 0.4, blend=skia.BlendMode.kPlus)


def bubble(c: skia.Canvas, x: float, y: float, text: str, size: float, alpha: float = 1.0, scale: float = 1.0,
           fill="#FFFFFF", fg="#1E2230", tail: str = "down", name: str = "black"):
    """对话气泡；(x, y) 为气泡中心，tail 为尾巴方向 down / left / right。"""
    if alpha <= 0 or scale <= 0:
        return
    w = text_width(text, size, name) + size * 1.4
    h = size * 2.0
    c.save()
    c.translate(x, y)
    c.scale(scale, scale)
    rrect(c, 0, 0, w, h, h * 0.45, fill, alpha, shadow=0.25)
    tp = skia.Path()
    if tail == "down":
        tp.moveTo(-size * 0.4, h / 2 - 2)
        tp.lineTo(-size * 0.1, h / 2 + size * 0.6)
        tp.lineTo(size * 0.35, h / 2 - 2)
    else:
        sgn = -1 if tail == "left" else 1
        tp.moveTo(sgn * (w / 2 - size * 0.9), h / 2 - 4)
        tp.lineTo(sgn * (w / 2 - size * 0.1), h / 2 + size * 0.55)
        tp.lineTo(sgn * (w / 2 - size * 0.3), h / 2 - 4)
    tp.close()
    c.drawPath(tp, skia.Paint(AntiAlias=True, Color=col(fill, alpha)))
    draw_text(c, text, 0, 0, size, name, fg, alpha)
    c.restore()


def chip(c: skia.Canvas, x: float, y: float, text: str, size: float, fill="#FFFFFF", fg="#1E2230",
         alpha: float = 1.0, scale: float = 1.0, emoji: str | None = None, name: str = "black"):
    """胶囊标签，可带前置 Emoji；(x, y) 为中心。"""
    if alpha <= 0 or scale <= 0:
        return
    ew = size * 1.25 if emoji else 0
    w = text_width(text, size, name) + size * 1.3 + ew
    h = size * 1.8
    c.save()
    c.translate(x, y)
    c.scale(scale, scale)
    rrect(c, 0, 0, w, h, h / 2, fill, alpha, shadow=0.2)
    if emoji:
        draw_emoji(c, emoji, -w / 2 + size * 0.65 + ew / 2 - size * 0.1, 0, size * 1.3, alpha, shadow=0)
    draw_text(c, text, ew / 2, 0, size, name, fg, alpha)
    c.restore()


def battery(c: skia.Canvas, x: float, y: float, w: float, h: float, level: float, alpha: float = 1.0,
            bolt: bool = False, outline="#FFFFFF"):
    """横向电池图标；电量颜色随 level 从红到黄到绿渐变。"""
    if alpha <= 0:
        return
    level = clamp01(level)
    color = mix("#FF4D4D", "#FFD23F", level / 0.5) if level < 0.5 else mix("#FFD23F", "#3BE07A", (level - 0.5) / 0.5)
    rrect(c, x - w * 0.03, y, w, h, h * 0.22, None, alpha, stroke=(outline, h * 0.08))
    rrect(c, x + w * 0.5, y, w * 0.06, h * 0.42, h * 0.08, outline, alpha)
    pad = h * 0.14
    fw = (w - pad * 2) * level
    if fw > 1:
        left = x - w * 0.03 - w / 2 + pad
        p = skia.Paint(AntiAlias=True, Color=col(color, alpha))
        r = skia.Rect.MakeXYWH(left, y - h / 2 + pad, fw, h - pad * 2)
        gp = skia.Paint(AntiAlias=True, Color=col(color, alpha * 0.6), MaskFilter=_blur(h * 0.25))
        c.drawRoundRect(r, h * 0.12, h * 0.12, gp)
        c.drawRoundRect(r, h * 0.12, h * 0.12, p)
    if bolt:
        bp = skia.Path()
        s = h * 0.38
        pts = [(0.15, -1), (-0.55, 0.12), (-0.02, 0.12), (-0.18, 1), (0.55, -0.15), (0.02, -0.15)]
        for k, (px, py) in enumerate(pts):
            bp.lineTo(x + px * s, y + py * s) if k else bp.moveTo(x + px * s, y + py * s)
        bp.close()
        c.drawPath(bp, skia.Paint(AntiAlias=True, Color=col("#FFFFFF", alpha)))


# ---------------------------------------------------------------- 背景与粒子

def gradient_bg(c: skia.Canvas, colors, alpha: float = 1.0):
    """竖向多色渐变铺满画布。"""
    stops = [i / (len(colors) - 1) for i in range(len(colors))]
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (0, H)], [col(k, alpha) for k in colors], stops))
    c.drawPaint(p)


def aurora(c: skia.Canvas, t: float, colors, alpha: float = 0.35):
    """缓慢游动的大面积柔光色块，营造流光背景。"""
    for i, k in enumerate(colors):
        ph = i * 2.1
        x = W * (0.5 + 0.38 * math.sin(t * 0.23 + ph))
        y = H * (0.45 + 0.32 * math.cos(t * 0.17 + ph * 1.3))
        circle(c, x, y, 420 + 80 * math.sin(t * 0.3 + ph), k, alpha, blur=160)


@functools.lru_cache(maxsize=64)
def _rand(seed: int, n: int, k: int) -> np.ndarray:
    return np.random.default_rng(seed).random((n, k))


def dust(c: skia.Canvas, t: float, color, n: int = 40, seed: int = 1, speed: float = 0.025,
         smin: float = 2.0, smax: float = 9.0, alpha: float = 0.6):
    """向上缓慢漂浮、明灭闪烁的光尘粒子（加色混合）。"""
    r = _rand(seed, n, 5)
    for x0, y0, v, s, ph in r:
        y = ((y0 - t * speed * (0.5 + v)) % 1.0) * (H + 100) - 50
        x = (x0 + 0.015 * math.sin(t * 0.6 + ph * 6)) * W
        a = alpha * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * (1 + v * 2) + ph * 6.28)))
        size = smin + (smax - smin) * s
        circle(c, x, y, size, color, a, blur=size * 0.8, blend=skia.BlendMode.kPlus)


def light_rays(c: skia.Canvas, x: float, y: float, t: float, color, alpha: float = 0.25, n: int = 14,
               length: float = 1700, speed: float = 8.0):
    """从 (x, y) 向外旋转放射的光芒。"""
    if alpha <= 0:
        return
    path = skia.Path()
    for k in range(n):
        a0 = math.radians(t * speed + k * 360 / n)
        a1 = a0 + math.radians(360 / n * 0.42)
        path.moveTo(x, y)
        path.lineTo(x + length * math.cos(a0), y + length * math.sin(a0))
        path.lineTo(x + length * math.cos(a1), y + length * math.sin(a1))
        path.close()
    p = skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kPlus, Shader=skia.GradientShader.MakeRadial(
        (x, y), length, [col(color, alpha), col(color, 0)]))
    c.drawPath(path, p)


def shockwave(c: skia.Canvas, x: float, y: float, p: float, color="#FFFFFF", rmax: float = 700, width: float = 16):
    """冲击波圆环，p 为扩散进度。"""
    if p <= 0 or p >= 1:
        return
    e = ease_out(p)
    paint = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * (1 - e) + 1,
                       Color=col(color, (1 - p) * 0.8), MaskFilter=_blur(4))
    c.drawCircle(x, y, rmax * e, paint)


def confetti(c: skia.Canvas, x: float, y: float, dt: float, n: int = 70, seed: int = 3, power: float = 1.0):
    """从 (x, y) 喷发的彩带碎片，dt 为喷发后经过的秒数。"""
    if dt < 0 or dt > 3.0:
        return
    r = _rand(seed, n, 6)
    for ang, spd, rs, ci, sz, ph in r:
        a = math.radians(-90 + (ang - 0.5) * 150)
        v = (900 + 900 * spd) * power
        px = x + math.cos(a) * v * dt * 0.8
        py = y + math.sin(a) * v * dt + 1400 * dt * dt
        alpha = 1 - prog(dt, 2.0, 1.0)
        c.save()
        c.translate(px, py)
        c.rotate(dt * 600 * (rs - 0.5) + ph * 360)
        c.scale(1, abs(math.cos(dt * 8 + ph * 6)) + 0.2)
        s = 10 + sz * 12
        c.drawRect(skia.Rect.MakeXYWH(-s / 2, -s / 4, s, s / 2),
                   skia.Paint(AntiAlias=True, Color=col(CONFETTI[int(ci * len(CONFETTI)) % len(CONFETTI)], alpha)))
        c.restore()


def sparkles(c: skia.Canvas, t: float, x: float, y: float, w: float, h: float, n: int = 10, seed: int = 5,
             color="#FFFFFF", alpha: float = 1.0, size: float = 26):
    """在矩形区域内随机闪烁的星光。"""
    if alpha <= 0:
        return
    for px, py, ph, s in _rand(seed, n, 4):
        tw = math.sin(t * 3.2 + ph * 6.28)
        if tw > 0:
            star4(c, x + (px - 0.5) * w, y + (py - 0.5) * h, size * (0.5 + s) * tw, color, alpha * tw,
                  rot=t * 40 + ph * 90)


def warp(c: skia.Canvas, t: float, x: float, y: float, intensity: float, color="#FFFFFF", n: int = 70, seed: int = 9):
    """向外飞散的速度线，营造"穿越"感。"""
    if intensity <= 0:
        return
    for ang, spd, ph in _rand(seed, n, 3):
        a = ang * math.tau
        d = ((t * (0.6 + spd) * 1.6 + ph) % 1.0)
        r0 = 60 + d * d * 1300
        r1 = r0 + 40 + 260 * d * intensity
        p = skia.Paint(AntiAlias=True, Color=col(color, intensity * d * 0.9), StrokeWidth=2 + 4 * d,
                       StrokeCap=skia.Paint.kRound_Cap, BlendMode=skia.BlendMode.kPlus)
        c.drawLine(x + r0 * math.cos(a), y + r0 * math.sin(a), x + r1 * math.cos(a), y + r1 * math.sin(a), p)


@functools.lru_cache(maxsize=None)
def _vignette_shader() -> skia.Shader:
    return skia.GradientShader.MakeRadial((W / 2, H * 0.45), H * 0.72,
                                          [col("#000000", 0), col("#000000", 0), col("#000000", 1)], [0, 0.55, 1])


def vignette(c: skia.Canvas, strength: float = 0.5):
    if strength > 0:
        c.drawPaint(skia.Paint(Shader=_vignette_shader(), Alphaf=clamp01(strength)))


# ---------------------------------------------------------------- 后期

def glitch(arr: np.ndarray, amount: float, frame: int) -> np.ndarray:
    """RGB 通道错位 + 水平切片位移的故障效果；arr 为 (H, W, 4) uint8。"""
    if amount <= 0:
        return arr
    rng = np.random.default_rng(frame * 7919)
    out = arr.copy()
    shift = int(6 + 30 * amount)
    out[..., 0] = np.roll(arr[..., 0], shift, axis=1)
    out[..., 2] = np.roll(arr[..., 2], -shift, axis=1)
    for _ in range(int(3 + 9 * amount)):
        y0 = int(rng.integers(0, H - 40))
        hgt = int(rng.integers(8, 70))
        dx = int(rng.integers(-80, 80) * amount)
        out[y0:y0 + hgt] = np.roll(out[y0:y0 + hgt], dx, axis=1)
    return out
