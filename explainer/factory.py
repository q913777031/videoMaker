"""工厂与图表类元件：传送带、货箱、检测门、点阵、饼图、天平。"""

import math

import numpy as np
import skia

from .engine import (BLUE, CREAM, GOLD, GRAY, INK, KRAFT, LGRAY, PALEBLUE, PALEGOLD, PALERED, PAPER, RED, SKIN, circ,
                     clamp01, col, crect, glow, lerp, oval, poly, rect, shape, stroke, text, xf, _paint)

TAPE = "#E5D2AB"


def belt(c, x0, x1, y, t, speed=120.0, h=34):
    """传送带：y 为带面顶部，t 为时间（决定条纹滚动）。"""
    rect(c, x0, y, x1 - x0, h, h / 2, "#6B5F55", INK, 5, rough=False)
    off = (t * speed) % 44
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x0 + 14, y, x1 - x0 - 28, h))
    k = -44.0
    while k < x1 - x0 + 44:
        stroke(c, [(x0 + k + off, y + h - 6), (x0 + k + off + 18, y + 6)], "#8C7F73", 5)
        k += 44
    c.restore()
    for xr in (x0 + h / 2, x1 - h / 2):
        circ(c, xr, y + h / 2, h / 2 - 5, "#A99B8C", INK, 4, rough=False)


def crate(c, x, y, s=1.0, bad=False, flag=0.0, a=1.0, ghost=False):
    """货箱，(x, y) 为底边中点；bad 画裂纹，flag∈[0,1] 画红色警示圈。"""
    w, h = 74 * s, 62 * s
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    rect(c, x - w / 2, y - h, w, h, 6 * s, KRAFT, INK, max(2.5, 5 * s), rough=s > 0.8)
    rect(c, x - 8 * s, y - h, 16 * s, h, 0, TAPE, None, 0, rough=False)
    stroke(c, [(x - w / 2 + 4 * s, y - h), (x + w / 2 - 4 * s, y - h)], INK, max(2, 4 * s))
    if bad:
        stroke(c, [(x - 22 * s, y - h * 0.8), (x - 8 * s, y - h * 0.55), (x - 20 * s, y - h * 0.4),
                   (x + 2 * s, y - h * 0.2)], RED, max(3, 6 * s))
    if flag > 0:
        pr = 1 + 0.06 * math.sin(flag * 14)
        stroke(c, [(x - w / 2 - 8 * s, y - h - 8 * s), (x + w / 2 + 8 * s, y - h - 8 * s),
                   (x + w / 2 + 8 * s, y + 8 * s), (x - w / 2 - 8 * s, y + 8 * s), (x - w / 2 - 8 * s, y - h - 8 * s)],
               RED, max(3, 7 * s), clamp01(flag))
    if a < 1:
        c.restore()


def lamp(c, x, y, on=0.0, r=28, t=0.0):
    """警示灯：on∈[0,1]。"""
    if on > 0.01:
        glow(c, x, y, r * 4.2, RED, 0.55 * on)
        for i in range(8):
            ang = math.radians(i * 45 + t * 90)
            stroke(c, [(x + math.cos(ang) * r * 1.5, y + math.sin(ang) * r * 1.5),
                       (x + math.cos(ang) * r * 2.1, y + math.sin(ang) * r * 2.1)], RED, 6, on)
    rect(c, x - r * 0.9, y + r * 0.6, r * 1.8, r * 0.7, 6, GRAY, INK, 4, rough=False)
    circ(c, x, y, r, RED if on > 0.5 else "#B9A99A", INK, 5, rough=False)
    circ(c, x - r * 0.3, y - r * 0.3, r * 0.25, CREAM, None, 0, a=0.8)


def detector(c, x, y, s=1.0, on=0.0, t=0.0, label=True):
    """检测门：(x, y) 为地面中点，门洞宽约 200*s。"""
    with xf(c, x, y, sx=s):
        for sx in (-1, 1):
            rect(c, sx * 130 - 24, -250, 48, 250, 10, "#C9D4DC", INK, 6, rough=False)
        rect(c, -170, -300, 340, 90, 16, "#A9B9C6", INK, 6, rough=False)
        rect(c, -120, -282, 150, 54, 8, INK, None, 0, rough=False)
        stroke(c, [(-104, -255), (-60, -255)], "#7FD6A8" if on < 0.5 else RED, 6)
        stroke(c, [(-104, -240), (-20, -240)], "#7FD6A8" if on < 0.5 else RED, 5, 0.6)
        lamp(c, 100, -330, on, 28, t)
        if label:
            text(c, "检测器", 0, 54, 36, INK, "sans", "c")


_RNG = np.random.default_rng(20260509)
_PERM = _RNG.permutation(10000)
DEFECT_IDX = np.sort(_PERM[:100])                       # 100 件有缺陷
_GOOD_IDX = np.setdiff1d(np.arange(10000), DEFECT_IDX)  # 9900 件合格
FLAG_DEFECT = DEFECT_IDX[:90]                           # 检出 90 件
FLAG_GOOD = _RNG.permutation(_GOOD_IDX)[:495]           # 误报 495 件


def dot_grid(c, cx, cy, size, reveal=1.0, mark_defect=0.0, mark_flag=0.0, pulse=0.0):
    """10000 件产品的 100×100 点阵（教学示意）：reveal 为自左向右出现的比例。"""
    n = 100
    step = size / n
    x0, y0 = cx - size / 2, cy - size / 2
    cols = int(n * clamp01(reveal))
    if cols <= 0:
        return
    idx = np.arange(10000)
    xs = x0 + (idx % n) * step + step / 2
    ys = y0 + (idx // n) * step + step / 2
    vis = (idx % n) < cols
    isdef = np.zeros(10000, bool)
    isdef[DEFECT_IDX] = True
    flag = np.zeros(10000, bool)
    flag[FLAG_DEFECT] = True
    flag[FLAG_GOOD] = True

    def pts(mask):
        m = mask & vis
        return [skia.Point(float(a), float(b)) for a, b in zip(xs[m], ys[m])]

    dot = max(2.0, step * 0.62)

    def paint(color, w):
        return skia.Paint(AntiAlias=False, Color=col(color), StrokeWidth=w, Style=skia.Paint.kStroke_Style,
                          StrokeCap=skia.Paint.kSquare_Cap)

    base = ~isdef
    if mark_flag > 0:
        base = base & ~flag
    c.drawPoints(skia.Canvas.kPoints_PointMode, pts(base), paint("#B9AE9C", dot))
    if mark_flag > 0:
        gf = flag & ~isdef
        c.drawPoints(skia.Canvas.kPoints_PointMode, pts(gf), paint(GOLD, dot * (1 + 0.6 * mark_flag)))
    if mark_defect > 0 or mark_flag > 0:
        dm = isdef & ~(flag if mark_flag > 0 else np.zeros(10000, bool))
        c.drawPoints(skia.Canvas.kPoints_PointMode, pts(dm), paint(RED, dot * (1 + 0.7 * max(mark_defect, mark_flag))))
        if mark_flag > 0:
            c.drawPoints(skia.Canvas.kPoints_PointMode, pts(isdef & flag),
                         paint("#8F1F10", dot * (1 + 0.9 * mark_flag)))
    else:
        c.drawPoints(skia.Canvas.kPoints_PointMode, pts(isdef), paint(GRAY, dot))


def pie(c, cx, cy, r, frac, p=1.0, c1=RED, c2=GOLD, start=-90.0):
    """两色饼图：frac 为 c1 所占比例，p 为展开进度。"""
    sweep1 = 360.0 * frac * clamp01(p)
    sweep2 = 360.0 * (1 - frac) * clamp01(p)
    rc = skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r)
    for (a0, sw, colr) in ((start, sweep1, c1), (start + sweep1, sweep2, c2)):
        if sw <= 0.1:
            continue
        path = skia.Path()
        path.moveTo(cx, cy)
        path.arcTo(rc, a0, sw, False)
        path.close()
        shape(c, path, colr, INK, 6, rough=False)


def basket(c, cx, by, w, h, a=1.0):
    """敞口篮筐，by 为底边。"""
    path = skia.Path()
    path.moveTo(cx - w / 2, by - h)
    path.lineTo(cx - w / 2 + 14, by)
    path.lineTo(cx + w / 2 - 14, by)
    path.lineTo(cx + w / 2, by - h)
    shape(c, path, "#CDB68A", INK, 6, a, rough=False)
    for k in range(1, 4):
        yk = by - h + k * h / 4
        stroke(c, [(cx - w / 2 + k * 3.5 + 4, yk), (cx + w / 2 - k * 3.5 - 4, yk)], INK, 3, a * 0.6)


def scale(c, cx, cy, tilt, k=1.0):
    """天平：tilt 为横梁转角（度，正值右沉），k 为整体缩放；返回左右托盘中心。"""
    rect(c, cx - 14, cy, 28, 300 * k, 10, "#8C7F73", INK, 6, rough=False)
    rect(c, cx - 110, cy + 290 * k, 220, 36, 14, "#8C7F73", INK, 6, rough=False)
    arm = 360 * k
    ang = math.radians(tilt)
    lx, ly = cx - arm * math.cos(ang), cy - arm * math.sin(ang)
    rx, ry = cx + arm * math.cos(ang), cy + arm * math.sin(ang)
    stroke(c, [(lx, ly), (rx, ry)], INK, 18)
    stroke(c, [(lx, ly), (rx, ry)], "#CDB68A", 10)
    circ(c, cx, cy, 20, GOLD, INK, 5, rough=False)
    out = []
    for (px, py) in ((lx, ly), (rx, ry)):
        stroke(c, [(px, py), (px - 100 * k, py + 170 * k)], INK, 4)
        stroke(c, [(px, py), (px + 100 * k, py + 170 * k)], INK, 4)
        path = skia.Path()
        path.moveTo(px - 120 * k, py + 170 * k)
        path.quadTo(px, py + 260 * k, px + 120 * k, py + 170 * k)
        path.close()
        shape(c, path, "#CDB68A", INK, 6, rough=False)
        out.append((px, py + 170 * k))
    return out
