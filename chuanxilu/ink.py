"""水墨基础元件：宣纸、远山、云雾、墨晕、溅墨、朱砂印、竖排原文卡、灯火、渐显笔触。

全部为确定性绘制（固定种子），1080×1920 竖屏坐标。
"""

import functools
import math

import numpy as np
import skia

from engine import gfx

PAPER = (238, 229, 209)
PAPER_DARK = (226, 214, 188)
INK = (30, 27, 24)
CINNABAR = (178, 51, 42)
OCHRE = (150, 104, 62)
DAI = (62, 82, 92)
W, H = gfx.W, gfx.H


def color(rgb, a: float = 1.0) -> int:
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(255 * max(0.0, min(1.0, a))))


def paint(rgb, a: float = 1.0, blur: float = 0.0, stroke: float = 0.0, cap=skia.Paint.kRound_Cap) -> skia.Paint:
    p = skia.Paint(Color=color(rgb, a), AntiAlias=True)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if stroke > 0:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def _smooth_noise(shape, scale: float, seed: int) -> np.ndarray:
    import cv2
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, int(shape[0] / scale)), max(2, int(shape[1] / scale)))).astype(np.float32)
    return cv2.resize(small, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)


# ---------------------------------------------------------------- 宣纸

@functools.lru_cache(maxsize=1)
def paper_image() -> skia.Image:
    """宣纸（首次生成后缓存为 PNG）。"""
    path = gfx.ROOT / ".cache" / "chuanxilu" / "paper_v1.png"
    if path.exists():
        return skia.Image.open(str(path))
    img = _make_paper()
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path))
    return img


def _make_paper() -> skia.Image:
    """宣纸：底色 + 云状深浅 + 纤维丝 + 细颗粒，四角略暗。"""
    rng = np.random.default_rng(11)
    base = np.array(PAPER, np.float32)
    mott = _smooth_noise((H, W), 160, 1) * 0.6 + _smooth_noise((H, W), 40, 2) * 0.4
    img = base[None, None, :] - (mott[..., None] - 0.5) * 14
    img -= rng.random((H, W, 1)).astype(np.float32) * 6
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W * 0.75), (yy - H / 2) / (H * 0.7))
    img -= np.clip(r - 0.55, 0, 1)[..., None] * 40
    rgba = np.concatenate([np.clip(img, 0, 255), np.full((H, W, 1), 255, np.float32)], axis=2).astype(np.uint8)
    surf = skia.Surface(rgba)
    c = surf.getCanvas()
    for _ in range(2600):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        ang, ln = rng.uniform(0, math.pi), rng.uniform(8, 46)
        p = skia.Path()
        p.moveTo(x, y)
        p.quadTo(x + math.cos(ang) * ln * 0.5 + rng.normal(0, 4), y + math.sin(ang) * ln * 0.5 + rng.normal(0, 4),
                 x + math.cos(ang) * ln, y + math.sin(ang) * ln)
        tone = (255, 252, 240) if rng.random() < 0.6 else (190, 175, 145)
        c.drawPath(p, paint(tone, rng.uniform(0.08, 0.22), stroke=rng.uniform(0.6, 1.4)))
    return surf.makeImageSnapshot()


def draw_paper(c: skia.Canvas):
    c.drawImage(paper_image(), 0, 0)


# ---------------------------------------------------------------- 远山、云雾

@functools.lru_cache(maxsize=32)
def _ridge(seed: int, n: int = 600) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, n)
    y = np.zeros(n)
    for octave in range(5):
        f = 2 ** octave * 1.5
        y += rng.uniform(0.4, 1.0) / (octave + 1) ** 1.3 * np.sin(2 * np.pi * (f * x + rng.random()))
    peaks = np.zeros(n)
    for _ in range(3):
        cx, w = rng.uniform(0.1, 0.9), rng.uniform(0.06, 0.16)
        peaks += rng.uniform(0.6, 1.4) * np.exp(-((x - cx) / w) ** 2)
    v = y * 0.35 + peaks
    return (v - v.min()) / (v.max() - v.min() + 1e-9)


def mountains(c: skia.Canvas, base_y: float, height: float, seed: int, tone=DAI, alpha: float = 0.5,
              shift: float = 0.0, width: float = 2.4 * W, blur: float = 0.0, reveal: float = 1.0):
    """一层远山：山脊浓、向下渐淡（墨分五色），shift 为横向视差位移；reveal 由下往上显现。"""
    r = _ridge(seed)
    xs = np.linspace(-0.2 * W, -0.2 * W + width, len(r)) - shift
    p = skia.Path()
    p.moveTo(xs[0], base_y + height)
    for x, v in zip(xs, r):
        p.lineTo(x, base_y + height * (1 - v * reveal))
    p.lineTo(xs[-1], base_y + height)
    p.close()
    top = base_y + height * (1 - reveal)
    shader = skia.GradientShader.MakeLinear([(0, top), (0, base_y + height)],
                                            [color(tone, alpha), color(tone, alpha * 0.35), color(tone, 0)],
                                            [0.0, 0.55, 1.0])
    pt = skia.Paint(Shader=shader, AntiAlias=True)
    if blur > 0:
        pt.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    c.drawPath(p, pt)
    edge = skia.Path()
    edge.moveTo(xs[0], base_y + height * (1 - r[0] * reveal))
    for x, v in zip(xs[::3], r[::3]):
        edge.lineTo(x, base_y + height * (1 - v * reveal))
    c.drawPath(edge, paint(INK, alpha * 0.35, blur=1.2 + blur * 0.3, stroke=2.2))


def mist(c: skia.Canvas, t: float, y: float, alpha: float = 0.55, seed: int = 0, n: int = 4):
    """飘动的云雾带（纸色柔光）。"""
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = (rng.uniform(-300, W) + t * rng.uniform(8, 22)) % (W + 700) - 350
        yy = y + rng.uniform(-60, 60)
        w, h = rng.uniform(380, 700), rng.uniform(50, 110)
        c.drawOval(skia.Rect.MakeXYWH(x, yy - h / 2, w, h), paint((247, 242, 230), alpha, blur=h * 0.45))


# ---------------------------------------------------------------- 墨晕、溅墨

def bloom(c: skia.Canvas, x: float, y: float, r: float, p: float, seed: int = 0, tone=INK, alpha: float = 0.5):
    """墨滴落纸、沿纤维晕开：不规则多瓣软边，p 为扩散进度。"""
    if p <= 0:
        return
    rng = np.random.default_rng(seed)
    e = 1 - (1 - min(1.0, p)) ** 3
    for k in range(7):
        ang = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, 0.35) * r * e
        rr = r * e * rng.uniform(0.45, 0.9)
        c.drawCircle(x + math.cos(ang) * d, y + math.sin(ang) * d, rr,
                     paint(tone, alpha * rng.uniform(0.35, 0.7), blur=rr * 0.35))
    c.drawCircle(x, y, r * e * 0.35, paint(tone, alpha * 0.9, blur=r * 0.08))


def splash(c: skia.Canvas, x: float, y: float, dt: float, seed: int = 0, power: float = 1.0, tone=INK):
    """溅墨：不规则墨团 + 沿放射方向拉长的墨滴，dt 为距撞击的秒数（0.25 秒内溅开后定格）。"""
    if dt < 0:
        return
    rng = np.random.default_rng(seed)
    e = 1 - (1 - min(1.0, dt / 0.25)) ** 3
    for _ in range(9):
        ang, d = rng.uniform(0, 2 * math.pi), rng.uniform(0, 22) * power
        c.drawCircle(x + math.cos(ang) * d * e, y + math.sin(ang) * d * e, rng.uniform(10, 24) * power * e,
                     paint(tone, 0.8, blur=1.5))
    for _ in range(int(22 * power)):
        ang, d = rng.uniform(0, 2 * math.pi), rng.uniform(50, 200) * power
        rr = rng.uniform(2.5, 9) * power
        stretch = rng.uniform(1.6, 3.2)
        c.save()
        c.translate(x + math.cos(ang) * d * e, y + math.sin(ang) * d * e)
        c.rotate(math.degrees(ang))
        c.drawOval(skia.Rect.MakeXYWH(-rr * stretch, -rr, rr * stretch * 2, rr * 2), paint(tone, 0.85, blur=0.8))
        c.restore()


# ---------------------------------------------------------------- 笔触

def brush_path(c: skia.Canvas, pts, width: float, p: float = 1.0, tone=INK, alpha: float = 0.9, taper: bool = True):
    """沿折线画一笔（连续的变宽墨带）：起笔略收、行笔饱满、收笔出锋；p 为从起点开始的绘制比例。"""
    pts = np.asarray(pts, float)
    if p <= 0 or len(pts) < 2:
        return
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    keep = np.concatenate([[True], seg > 1e-6])
    pts = pts[keep]
    if len(pts) < 2:
        return
    cum = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    stop = cum[-1] * min(1.0, p)
    n = int(np.searchsorted(cum, stop))
    pts = pts[: n + 1].copy()
    if n < len(cum) and cum[n] > stop and n > 0:
        r = (stop - cum[n - 1]) / (cum[n] - cum[n - 1])
        pts[n] = pts[n - 1] + (pts[n] - pts[n - 1]) * r
    if len(pts) < 2:
        return
    u = cum[: len(pts)] / max(cum[-1], 1e-6)
    if taper:
        wk = width * np.minimum(1.0, 0.45 + u * 6) * (1 - 0.82 * u ** 1.6)
    else:
        wk = np.full(len(pts), width)
    d = np.gradient(pts, axis=0)
    nrm = np.stack([-d[:, 1], d[:, 0]], axis=1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    left, right = pts + nrm * (wk[:, None] / 2), pts - nrm * (wk[:, None] / 2)
    path = skia.Path()
    path.moveTo(*left[0])
    for q in left[1:]:
        path.lineTo(*q)
    for q in right[::-1]:
        path.lineTo(*q)
    path.close()
    c.drawPath(path, paint(tone, alpha, blur=0.6))


def smooth(pts, n: int = 40) -> np.ndarray:
    """Catmull-Rom 插值，让手写控制点变成顺滑笔迹。"""
    pts = np.asarray(pts, float)
    out = []
    P = np.vstack([pts[0], pts, pts[-1]])
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, max(2, n // (len(pts) - 1)), endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return np.array(out)


# ---------------------------------------------------------------- 朱砂印

@functools.lru_cache(maxsize=64)
def _seal_image(text: str, size: int, round_: bool) -> skia.Image:
    """印面：1–3 字竖排一列（窄长印），4 字两列右起。"""
    img = _seal_square(text, size, round_)
    n = len(text)
    if round_ or n == 4 or n == 1:
        return img
    cell = (size - 4 * size * 0.04) / n
    w = int(cell + size * 0.2)
    return img.makeSubset(skia.IRect.MakeXYWH((size - w) // 2, 0, w, size)) or img


def _seal_square(text: str, size: int, round_: bool) -> skia.Image:
    rng = np.random.default_rng(sum(map(ord, text)))
    surf = skia.Surface(size, size)
    c = surf.getCanvas()
    c.clear(skia.Color(0, 0, 0, 0))
    m = size * 0.04
    if round_:
        c.drawCircle(size / 2, size / 2, size / 2 - m, paint(CINNABAR, 0.95))
    else:
        n = len(text)
        half = size / 2 if n in (1, 4) else ((size - 4 * m) / n + size * 0.2) / 2
        x0, x1 = size / 2 - half + m, size / 2 + half - m
        p = skia.Path()
        pts = []
        for side in range(4):
            for k in range(12):
                u = k / 12
                x, y = [(x0 + u * (x1 - x0), m), (x1, m + u * (size - 2 * m)),
                        (x1 - u * (x1 - x0), size - m), (x0, size - m - u * (size - 2 * m))][side]
                pts.append((x + rng.normal(0, size * 0.006), y + rng.normal(0, size * 0.006)))
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close()
        c.drawPath(p, paint(CINNABAR, 0.95))
    chars = list(text)
    n = len(chars)
    cols = 2 if n == 4 else 1
    rows = math.ceil(n / cols)
    cell = (size - 4 * m) / max(rows, cols)
    font = gfx.font("serif_black", cell * 0.86)
    order = [(col, row) for col in range(cols - 1, -1, -1) for row in range(rows)]
    for ch, (col, row) in zip(chars, order):
        cx = size / 2 + (col - (cols - 1) / 2) * cell
        cy = size / 2 + (row - (rows - 1) / 2) * cell
        wch = font.measureText(ch)
        c.drawString(ch, cx - wch / 2, cy + cell * 0.3, font, paint(PAPER, 1.0))
    for _ in range(int(size * 0.5)):
        c.drawCircle(rng.uniform(0, size), rng.uniform(0, size), rng.uniform(0.5, size * 0.012),
                     skia.Paint(Color=skia.Color(0, 0, 0, 255), BlendMode=skia.BlendMode.kDstOut, AntiAlias=True,
                                Alphaf=rng.uniform(0.3, 1.0)))
    return surf.makeImageSnapshot()


def seal(c: skia.Canvas, text: str, x: float, y: float, size: float, dt: float, rot: float = -4.0,
         round_: bool = False):
    """盖朱砂印：dt 为距落印时刻的秒数，0.12 秒内从 1.35 倍压到原大，落定后不动。"""
    if dt < -0.12:
        return
    k = gfx.clamp01((dt + 0.12) / 0.12)
    sc = 1.35 - 0.35 * gfx.ease_in(k)
    img = _seal_image(text, 256, round_)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(sc * size / 256, sc * size / 256)
    c.drawImage(img, -img.width() / 2, -128, gfx.SAMPLING, skia.Paint(Alphaf=k * 0.95))
    c.restore()


# ---------------------------------------------------------------- 竖排原文卡

def text_card(c: skia.Canvas, cols: list[str], x: float, y: float, p: float, size: float = 66,
              source: str = "", alpha: float = 1.0, tone=INK):
    """古籍竖排卡：右起竖排、界栏、朱砂边框；p 控制逐字显现（每字 0.15 秒级淡入）；以 (x, y) 为卡片中心。"""
    if alpha <= 0:
        return
    rows = max(len(col) for col in cols)
    cw, pad = size * 1.5, size * 0.7
    w = cw * len(cols) + pad * 2
    h = rows * size * 1.12 + pad * 2 + (size * 0.9 if source else 0)
    left, top = x - w / 2, y - h / 2
    open_ = gfx.ease_out(gfx.clamp01(p * 6))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x - w / 2 * open_ - 4, top - 10, w * open_ + 8, h + 20))
    c.drawRect(skia.Rect.MakeXYWH(left + 8, top + 10, w, h), paint((90, 70, 50), 0.16 * alpha, blur=14))
    c.drawRect(skia.Rect.MakeXYWH(left, top, w, h), paint((246, 239, 222), 0.97 * alpha))
    c.drawRect(skia.Rect.MakeXYWH(left + 12, top + 12, w - 24, h - 24), paint(CINNABAR, 0.7 * alpha, stroke=3))
    c.drawRect(skia.Rect.MakeXYWH(left + 20, top + 20, w - 40, h - 40), paint(CINNABAR, 0.45 * alpha, stroke=1.2))
    for k in range(1, len(cols)):
        xx = left + pad + k * cw
        c.drawLine(xx, top + 20, xx, top + h - 20 - (size * 0.9 if source else 0), paint(CINNABAR, 0.3 * alpha,
                                                                                         stroke=1.2))
    font = gfx.font("serif_black", size)
    n_all = sum(len(col) for col in cols)
    shown = p * n_all
    i = 0
    for k, col in enumerate(cols):
        cx = left + w - pad - (k + 0.5) * cw
        for r, ch in enumerate(col):
            a = gfx.clamp01((shown - i) * 1.5) * alpha
            i += 1
            if a <= 0:
                continue
            cy = top + pad + (r + 0.5) * size * 1.12
            wch = font.measureText(ch)
            c.drawString(ch, cx - wch / 2, cy + size * 0.36, font, paint(tone, a))
    if source:
        f2 = gfx.font("serif_medium", size * 0.4)
        sw = f2.measureText(source)
        c.drawString(source, left + w / 2 - sw / 2, top + h - pad * 0.6, f2, paint(OCHRE, alpha * gfx.clamp01(p * 3)))
    c.restore()


# ---------------------------------------------------------------- 灯火

def lamp(c: skia.Canvas, x: float, y: float, t: float, size: float = 1.0, alpha: float = 1.0, glow: float = 1.0):
    """油灯 / 烛火：暖光晕 + 摇曳火苗。"""
    if alpha <= 0:
        return
    fl = 1 + 0.06 * math.sin(t * 17) + 0.04 * math.sin(t * 29 + 1)
    c.drawCircle(x, y - 30 * size, 260 * size * fl * glow, paint((255, 196, 110), 0.16 * alpha * glow, blur=120 * size))
    c.drawCircle(x, y - 30 * size, 90 * size * fl, paint((255, 214, 140), 0.35 * alpha * glow, blur=40 * size))
    p = skia.Path()
    h = 46 * size * fl
    p.moveTo(x, y - h)
    p.cubicTo(x + 14 * size, y - h * 0.5, x + 12 * size, y - 6 * size, x, y)
    p.cubicTo(x - 12 * size, y - 6 * size, x - 14 * size, y - h * 0.5, x, y - h)
    c.drawPath(p, paint((255, 170, 70), 0.9 * alpha, blur=2))
    c.drawOval(skia.Rect.MakeXYWH(x - 4 * size, y - 20 * size, 8 * size, 16 * size), paint((255, 250, 220), alpha))
    c.drawLine(x, y, x, y + 8 * size, paint(INK, alpha, stroke=3 * size))
    c.drawOval(skia.Rect.MakeXYWH(x - 34 * size, y + 6 * size, 68 * size, 18 * size), paint(INK, 0.85 * alpha))


def label(c: skia.Canvas, text: str, x: float, y: float, size: float, tone=INK, alpha: float = 1.0,
          name: str = "serif_black", align: str = "center"):
    """普通文字（宋体），用于数字、标注；align = center / left / right。"""
    if alpha <= 0:
        return
    f = gfx.font(name, size)
    w = f.measureText(text)
    dx = {"center": -w / 2, "left": 0.0, "right": -w}[align]
    c.drawString(text, x + dx, y + size * 0.36, f, paint(tone, alpha))
