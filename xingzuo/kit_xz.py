"""星座系列的专用绘图元件：星图卡、黄道星座条、日历、岁差陀螺、夜空窗。

沿用 adler.kit 的纸片风格：纸面上嵌深蓝色“星图卡”，星点大小按星等，连线为金色并可按进度逐段画出。
星表来自 xingzuo/data/zodiac.json（d3-celestial，BSD-3-Clause），由 prep_data.py 生成。
"""

import json
import math
from functools import lru_cache
from pathlib import Path

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

DATA = json.loads((Path(__file__).resolve().parent / "data" / "zodiac.json").read_text(encoding="utf-8"))
SKY = "#1F2C47"
SKY2 = "#2C3D61"
STAR = "#FFF4D6"
GOLDLINE = "#E9C77B"
FAINT = "#7F8DAE"

# 通用中文名（占星常用名）与天文正式名不同的星座
NAMES = {"Ari": "白羊座", "Tau": "金牛座", "Gem": "双子座", "Cnc": "巨蟹座", "Leo": "狮子座", "Vir": "处女座",
         "Lib": "天秤座", "Sco": "天蝎座", "Sgr": "射手座", "Cap": "摩羯座", "Aqr": "水瓶座", "Psc": "双鱼座",
         "Oph": "蛇夫座"}
ASTRO_NAMES = {"Vir": "室女座", "Sgr": "人马座", "Aqr": "宝瓶座"}
SHORT = {k: v[:-1] for k, v in NAMES.items()}


def sign(ab: str) -> dict:
    return DATA["signs"][ab]


def mmdd(s: str) -> str:
    m, d = s.split("-")
    return f"{int(m)}月{int(d)}日"


def mmdd_short(s: str) -> str:
    m, d = s.split("-")
    return f"{int(m)}/{int(d)}"


def doy(s: str) -> int:
    """MM-DD → 年内第几天（2026，非闰年）。"""
    m, d = (int(x) for x in s.split("-"))
    return sum((31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[:m - 1]) + d - 1


# ---------------------------------------------------------------- 星图投影

@lru_cache(maxsize=None)
def _proj(ab: str, w: float, h: float, margin: float):
    """把星座连线外接框缩放进 w×h（以卡片中心为原点）；赤经向东为左（面朝南看天）。"""
    s = sign(ab)
    cra, cdec = s["center"]
    cosd = math.cos(math.radians(cdec))
    xs, ys = [], []
    for seg in s["lines"]:
        for r, d in seg:
            xs.append(-(r - cra) * cosd)
            ys.append(-(d - cdec))
    sx = (w - 2 * margin) / max(1e-6, max(xs) - min(xs))
    sy = (h - 2 * margin) / max(1e-6, max(ys) - min(ys))
    k = min(sx, sy)
    ox, oy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    return cra, cdec, cosd, k, ox, oy


def project(ab: str, ra: float, dec: float, w: float, h: float, margin: float = 70) -> tuple[float, float]:
    cra, cdec, cosd, k, ox, oy = _proj(ab, w, h, margin)
    r = cra + (ra - cra + 180) % 360 - 180
    return (-(r - cra) * cosd - ox) * k, (-(dec - cdec) - oy) * k


def star_r(mag: float, base: float = 1.0) -> float:
    return base * max(2.0, 10.5 - 1.9 * mag)


def twinkle(t: float, seed: float) -> float:
    return 0.78 + 0.22 * math.sin(t * 2.3 + seed * 12.9898) * math.sin(t * 1.1 + seed * 4.1)


def sky_card(c, x, y, w, h, ab, p=1.0, t=0.0, alpha=1.0, glow=None, glow_k=0.0, label=None, label_k=0.0,
             margin=80, bg=True, card=True, scale=1.0, line_color=GOLDLINE, extra=None):
    """星图卡：深蓝底 + 背景星 + 连线（p 为逐段绘制进度）+ 可选高亮星与标注。

    glow：named 列表下标（0 为最亮星）；label：标注文字（两行用 |）；extra(c, proj) 在星图坐标系上叠加绘制。
    """
    if alpha <= 0:
        return
    s = sign(ab)

    def P(ra, dec):
        return project(ab, ra, dec, w, h, margin)

    with K.at(c, x, y, 0, scale):
        if card:
            with K.paper(c, alpha, 1.0, skia.Rect.MakeXYWH(-w, -h, 2 * w, 2 * h)):
                K.rr(c, 0, 0, w, h, 34, SKY)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 34, 34), True)
        if card:
            sh = skia.GradientShader.MakeRadial((0, -h * 0.2), max(w, h) * 0.7, [K.col(SKY2, alpha), K.col(SKY, alpha)],
                                                [0, 1])
            c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.Paint(AntiAlias=True, Shader=sh))
        if bg:
            for i, (r, d, m) in enumerate(s["stars"]):
                px, py = P(r, d)
                if abs(px) > w / 2 + 10 or abs(py) > h / 2 + 10:
                    continue
                K.dot(c, px, py, star_r(m, 0.8), STAR, alpha * (0.85 if m < 4.5 else 0.6) * twinkle(t, i * 0.37))
        # 连线：按总长度逐段画出
        segs = []
        for seg in s["lines"]:
            for a, b in zip(seg, seg[1:]):
                p0, p1 = P(*a), P(*b)
                segs.append((p0, p1, math.hypot(p1[0] - p0[0], p1[1] - p0[1])))
        total = sum(L for _, _, L in segs) or 1
        drawn = total * clamp01(p)
        acc = 0.0
        for p0, p1, L in segs:
            if acc >= drawn:
                break
            q = clamp01((drawn - acc) / max(L, 1e-6))
            K.seg(c, p0[0], p0[1], lerp(p0[0], p1[0], q), lerp(p0[1], p1[1], q), line_color, 4.5, alpha * 0.85)
            acc += L
        # 连线顶点上的星
        for seg in s["lines"]:
            for r, d in seg:
                px, py = P(r, d)
                near = min(s["stars"], key=lambda q: (q[0] - r) ** 2 + (q[1] - d) ** 2) if s["stars"] else (r, d, 4)
                m = near[2] if abs(near[0] - r) + abs(near[1] - d) < 0.3 else 4.2
                K.dot(c, px, py, star_r(m, 1.2) * 2.2, STAR, alpha * 0.14)
                K.dot(c, px, py, star_r(m, 1.2), STAR, alpha)
        if glow is not None and glow_k > 0:
            st = s["named"][glow]
            px, py = P(st["ra"], st["dec"])
            K.spotlight(c, px, py, 120 * glow_k, "#FFE7A8", 0.55 * alpha * glow_k)
            K.ring(c, px, py, 30 + 6 * math.sin(t * 3), "#FFE7A8", 4, alpha * glow_k)
            K.dot(c, px, py, star_r(st["mag"], 1.3) * (1 + 0.15 * glow_k), "#FFFFFF", alpha)
            if label and label_k > 0:
                lines = label.split("|")
                lx = px + (36 if px < w * 0.15 else -36)
                al = "left" if px < w * 0.15 else "right"
                ly = py - 20 - 28 * (len(lines) - 1) if py > -h * 0.3 else py + 60
                for j, ln in enumerate(lines):
                    K.text(c, ln, lx, ly + j * 56, 44 if j == 0 else 32, "serif_black" if j == 0 else "sans_medium",
                           "#FFE7A8" if j == 0 else FAINT, alpha * label_k, al)
        if extra:
            extra(c, P)
        c.restore()


# ---------------------------------------------------------------- 黄道星座条

def ecliptic_strip(c, x, y, w, h=120, highlight=(), bracket=None, bracket_k=1.0, sun=None, alpha=1.0, labels=True,
                   shift=0.0, size=30, bracket_label="占星日期"):
    """太阳一年经过的 13 个星座，宽度按太阳实际停留天数；highlight 为要强调的星座缩写。

    bracket=(MM-DD, MM-DD) 在上方画占星日期范围；sun=MM-DD 画太阳位置；shift 为整体左移的天数（演示岁差）。
    条带从 1 月 1 日开始。
    """
    sun_d = DATA["sun"]
    day_w = w / 365
    x0 = x - w / 2
    with K.fade(c, alpha):
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(x0 - 4, y - h, w + 8, h * 3))
        for ab, (a, b, n) in sun_d.items():
            da = doy(a)
            for part in ((da, n),) if da + n <= 365 else ((da, 365 - da), (0, da + n - 365)):
                s0, ln = part
                px = x0 + (s0 - shift) * day_w
                col = SKY if ab in highlight else (K.mix(SKY, K.PAPER, 0.55) if ab != "Oph" else K.mix(K.RED, K.PAPER, 0.5))
                for off in (0, 365 * day_w, -365 * day_w):
                    K.rr(c, px + off + ln * day_w / 2, y, ln * day_w - 4, h, 10, col)
                    if labels and ln * day_w > size * 1.3:
                        name = SHORT[ab]
                        if ln * day_w < size * 2.1:
                            name = name[0]
                        K.text(c, name, px + off + ln * day_w / 2, y, size, "sans_medium",
                               K.PAPER if ab in highlight or ab == "Oph" else K.INK, 1)
        c.restore()
        for m in range(12):
            mx = x0 + doy(f"{m + 1:02d}-01") * day_w
            K.seg(c, mx, y + h / 2 + 6, mx, y + h / 2 + 22, K.INK3, 3)
            K.text(c, f"{m + 1}月", mx + 15 * day_w, y + h / 2 + 40, 24, "sans_medium", K.INK3, 1)
        if bracket and bracket_k > 0:
            a, b = doy(bracket[0]), doy(bracket[1])
            if b < a:
                b += 365
            bx0, bx1 = x0 + a * day_w, x0 + (b + 1) * day_w
            if bx1 > x0 + w:
                bx0, bx1 = bx0 - w, bx1 - w
            k = ease_out(clamp01(bracket_k))
            top = y - h / 2 - 26
            K.seg(c, bx0, top, lerp(bx0, bx1, k), top, K.RED, 6)
            K.seg(c, bx0, top, bx0, top + 16, K.RED, 6)
            if k > 0.98:
                K.seg(c, bx1, top, bx1, top + 16, K.RED, 6)
            K.text(c, bracket_label, (bx0 + bx1) / 2, top - 32, 28, "sans_medium", K.RED, k)
        if sun is not None:
            sx = x0 + sun * day_w if isinstance(sun, (int, float)) else x0 + doy(sun) * day_w
            K.spotlight(c, sx, y, 70, K.GOLD, 0.5)
            K.dot(c, sx, y, 22, K.GOLD)
            K.ring(c, sx, y, 30, K.GOLD, 4)


# ---------------------------------------------------------------- 日历

def calendar(c, x, y, s, a: str, b: str, alpha=1.0, k=1.0, accent=K.RED, rot=0.0, scale=1.0):
    """撕页日历：上方月份色条，中间写日期范围。"""
    w, h = s * 1.5, s * 1.1
    with K.at(c, x, y, rot, scale):
        with K.paper(c, alpha, 1.0):
            K.rr(c, 0, 0, w, h, 24, K.PAPER)
            c.save()
            c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 24, 24), True)
            c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h * 0.24), K.paint(accent))
            c.restore()
            for i in (-1, 1):
                K.rr(c, i * w * 0.25, -h / 2, s * 0.06, s * 0.2, s * 0.03, K.DARK)
        K.text(c, mmdd(a), 0, -h * 0.02, s * 0.2, "serif_black", K.INK, alpha)
        K.text(c, "至", 0, h * 0.17, s * 0.1, "sans_medium", K.INK3, alpha)
        K.text(c, mmdd(b), 0, h * 0.34, s * 0.2, "serif_black", K.INK, alpha * clamp01(k))


# ---------------------------------------------------------------- 岁差陀螺

def precession(c, x, y, s, phase, alpha=1.0, trail=1.0, label=True):
    """地球与倾斜的自转轴：轴的北端沿小圆画圈（phase 0–1 为一圈），trail 为圈的描出进度。"""
    tilt = math.radians(23.4)
    with K.fade(c, alpha):
        top_r = s * 0.48
        cy_top = y - s * 1.05
        K.ring(c, x, cy_top, top_r, K.INK3, 4, 0.8, clamp01(trail), -90)
        ang = phase * 2 * math.pi
        tx, ty = x + top_r * math.sin(ang), cy_top + top_r * 0.32 * math.cos(ang)
        # 地球
        sh = skia.GradientShader.MakeRadial((x - s * 0.18, y - s * 0.2), s * 0.75, [K.col("#7FB6D9"), K.col("#3D6E92")],
                                            [0, 1])
        with K.paper(c, 1, 1.0):
            c.drawCircle(x, y, s * 0.5, skia.Paint(AntiAlias=True, Shader=sh))
        for lx, ly, r in ((-0.15, -0.1, 0.18), (0.18, 0.12, 0.14), (0.05, -0.28, 0.09)):
            K.dot(c, x + lx * s, y + ly * s, r * s, "#6FA06A", 0.9)
        bx, by = 2 * x - tx, 2 * y - ty + (cy_top - y) * 0 + (y - cy_top) * 0
        bx, by = x - (tx - x) * 0.55, y + (y - cy_top) * 0.55
        K.seg(c, bx, by, tx, ty, K.RED, 7)
        K.dot(c, tx, ty, 10, K.RED)
        if label:
            K.text(c, "23.4°", x + s * 0.62, y - s * 0.62, 30, "sans_medium", K.INK2, 1, "left")
    return tilt


# ---------------------------------------------------------------- 夜空窗

def night_panel(c, x, y, w, h, ab, t, p=1.0, glow_k=0.0, alt_frac=0.55, alpha=1.0, compass="南", label=None,
                label_k=0.0, scale_frac=0.62):
    """夜空窗口：深蓝渐变天空 + 地平线剪影 + 方位字；星座按 alt_frac（0 地平线，1 窗顶）放在天空中。"""
    with K.paper(c, alpha, 1.0):
        K.rr(c, x, y, w, h, 34, SKY)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 34, 34), True)
    sh = skia.GradientShader.MakeLinear([(x, y - h / 2), (x, y + h / 2)], [K.col("#16213A", alpha), K.col("#3A4E78", alpha)],
                                        [0, 1])
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), skia.Paint(AntiAlias=True, Shader=sh))
    ground_y = y + h / 2 - h * 0.16
    cw, ch = w * scale_frac, h * scale_frac * 0.75
    cy = ground_y - (ground_y - (y - h / 2)) * alt_frac
    cy = min(max(cy, y - h / 2 + ch / 2 + 30), ground_y - ch / 2 - 10)
    sky_card(c, x, cy, cw, ch, ab, p, t, alpha, 0 if glow_k > 0 else None, glow_k, label, label_k, 40, True, False)
    path = skia.Path()
    path.moveTo(x - w / 2, ground_y + 10)
    for i in range(13):
        px = x - w / 2 + i * w / 12
        path.lineTo(px, ground_y - (18 + 26 * abs(math.sin(i * 1.7))) * (1 if i % 3 else 1.6))
    path.lineTo(x + w / 2, ground_y + 10)
    path.lineTo(x + w / 2, y + h / 2)
    path.lineTo(x - w / 2, y + h / 2)
    path.close()
    c.drawPath(path, K.paint("#141B2C", alpha))
    K.text(c, compass, x, ground_y + h * 0.08, 34, "serif_black", "#C9D2E6", alpha)
    c.restore()


def star_icon(c, x, y, r, color=K.GOLD, alpha=1.0):
    K.star(c, x, y, r, color, alpha, 4, 0.35)


__all__ = ["DATA", "SKY", "STAR", "GOLDLINE", "NAMES", "ASTRO_NAMES", "SHORT", "sign", "mmdd", "mmdd_short", "doy",
           "project", "sky_card", "ecliptic_strip", "calendar", "precession", "night_panel", "star_icon", "ease_in_out"]
