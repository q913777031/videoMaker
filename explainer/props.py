"""复古插画风通用元件：角色、气泡、手机、卡片、对勾叉号等。所有元件都以墨线 + 平涂色绘制。"""

import math
from dataclasses import dataclass

import skia

from .engine import (BLUE, CREAM, GOLD, GRAY, INK, KRAFT, LGRAY, PALEBLUE, PALEGOLD, PALERED, PAPER, RED, SKIN,
                     circ, clamp01, crect, ease_back, ease_out, get_font, glow, lerp, oval, poly, prog, rect,
                     shadow, shape, stroke, text, text_w, xf, _paint)


# ------------------------------------------------------------------ 角色

@dataclass
class Char:
    shirt: str = BLUE
    hair: str = "short"            # short / cap / tophat / bald / band
    hair_color: str = "#3A2E28"
    glasses: bool = False
    extra: tuple = ()              # sideburns / mustache / bowtie / whistle / scarf
    skin: str = SKIN
    trim: str = ""                 # 衣领 / 帽檐辅助色


LIN = Char(shirt=BLUE, hair="short", glasses=True, extra=("collar",))
COACH = Char(shirt=RED, hair="cap", hair_color=RED, extra=("whistle",), trim="#8F2D1D")
PLAYER = Char(shirt=GOLD, hair="band", hair_color="#4A3426", extra=("collar",), trim=BLUE)
HOST = Char(shirt="#4A3A5C", hair="short", hair_color="#2B2420", extra=("bowtie",), trim=RED)
GALTON = Char(shirt="#3B3530", hair="tophat", hair_color="#C8BFB0", extra=("sideburns", "mustache", "cravat"),
              trim="#F3EEE4", skin="#EFC4A0")
OWNER = Char(shirt="#E7D6B2", hair="bald", hair_color="#3A2E28", extra=("apron", "mustache"), trim=RED)


def _hair(c, ch: Char):
    hc = ch.hair_color
    if ch.hair == "short":
        path = skia.Path()
        path.moveTo(-88, 0)
        path.cubicTo(-108, -96, -46, -124, 0, -122)
        path.cubicTo(52, -124, 108, -96, 88, 0)
        path.quadTo(70, -34, 40, -50)
        path.quadTo(14, -26, -14, -52)
        path.quadTo(-46, -36, -66, -26)
        path.close()
        shape(c, path, hc, INK, 6, rough=False)
    elif ch.hair == "band":
        path = skia.Path()
        path.moveTo(-88, -8)
        path.cubicTo(-104, -100, -40, -126, 6, -124)
        path.cubicTo(56, -124, 104, -90, 88, -8)
        path.quadTo(50, -48, 0, -52)
        path.quadTo(-50, -48, -88, -8)
        path.close()
        shape(c, path, hc, INK, 6, rough=False)
        rect(c, -90, -52, 180, 24, 6, ch.trim or RED, INK, 5, rough=False)
    elif ch.hair == "cap":
        path = skia.Path()
        path.moveTo(-90, -14)
        path.cubicTo(-100, -110, -40, -132, 0, -130)
        path.cubicTo(50, -132, 100, -110, 90, -14)
        path.quadTo(0, -34, -90, -14)
        path.close()
        shape(c, path, hc, INK, 6, rough=False)
        brim = skia.Path()
        brim.moveTo(-96, -22)
        brim.quadTo(-10, -52, 124, -26)
        brim.quadTo(60, -4, -96, -22)
        brim.close()
        shape(c, brim, ch.trim or hc, INK, 6, rough=False)
    elif ch.hair == "tophat":
        # 两侧鬓发
        for sx in (-1, 1):
            oval(c, sx * 78, -26, 22, 40, hc, INK, 5, rough=False)
        rect(c, -66, -214, 132, 126, 12, "#2B2825", INK, 6, rough=False)
        rect(c, -112, -100, 224, 26, 12, "#2B2825", INK, 6, rough=False)
        rect(c, -66, -122, 132, 20, 0, RED, INK, 4, rough=False)
    elif ch.hair == "bald":
        for sx in (-1, 1):
            oval(c, sx * 80, -8, 14, 30, ch.hair_color, INK, 5, rough=False)


def _face(c, ch: Char, face: str, t: float, look, talk: float):
    blink = ((t + 1.7) % 3.6) < 0.12
    ey = 6
    ex = 31
    big = 1.35 if face in ("surprise", "cheer") else 1.0
    lx, ly = look
    for sx in (-1, 1):
        if blink or face == "cheer_closed":
            stroke(c, [(sx * ex - 11, ey), (sx * ex + 11, ey)], INK, 5)
        elif face == "happy":
            stroke(c, [(sx * ex - 11, ey + 4), (sx * ex, ey - 7), (sx * ex + 11, ey + 4)], INK, 5, smooth=True)
        else:
            circ(c, sx * ex + lx, ey + ly, 7.5 * big, INK, None, 0)
            circ(c, sx * ex + lx + 2.5, ey + ly - 2.5, 2.2 * big, CREAM, None, 0)
    # 眉毛
    br = {"smile": (0, -26, 0), "open": (0, -28, 0), "worry": (14, -28, 4), "surprise": (0, -40, 0),
          "flat": (0, -26, 0), "cheer": (0, -38, 0), "think": (0, -28, 0), "happy": (0, -30, 0),
          "sad": (18, -28, 5), "angry": (-18, -26, -3)}.get(face, (0, -26, 0))
    tilt, by, dy = br
    for sx in (-1, 1):
        extra = -8 if (face == "think" and sx == 1) else 0
        stroke(c, [(sx * ex - 13, by + 10 - sx * tilt * 0.5 + extra * 0 + (dy if sx == 1 else 0)),
                   (sx * ex + 13, by + 10 + sx * tilt * 0.5 + extra)], INK, 5)
    # 脸颊
    for sx in (-1, 1):
        circ(c, sx * 56, 36, 13, RED, None, 0, a=0.22)
    # 嘴
    my = 48
    if face in ("smile", "happy"):
        stroke(c, [(-18, my - 2), (0, my + 12), (18, my - 2)], INK, 5, smooth=True)
    elif face == "open":
        h = 8 + 14 * talk
        oval(c, 0, my + 4, 15, h, "#7A2E26", INK, 4, rough=False)
    elif face == "worry":
        stroke(c, [(-16, my + 8), (-6, my + 1), (6, my + 8), (16, my + 1)], INK, 5, smooth=True)
    elif face == "sad":
        stroke(c, [(-16, my + 10), (0, my - 2), (16, my + 10)], INK, 5, smooth=True)
    elif face == "surprise":
        oval(c, 0, my + 6, 12, 15, "#7A2E26", INK, 4, rough=False)
    elif face == "flat":
        stroke(c, [(-14, my + 4), (14, my + 4)], INK, 5)
    elif face == "angry":
        oval(c, 0, my + 6, 20, 13 + 6 * talk, "#7A2E26", INK, 4, rough=False)
    elif face == "cheer":
        path = skia.Path()
        path.moveTo(-24, my - 4)
        path.quadTo(0, my + 2, 24, my - 4)
        path.quadTo(18, my + 34, 0, my + 34)
        path.quadTo(-18, my + 34, -24, my - 4)
        path.close()
        shape(c, path, "#7A2E26", INK, 4, rough=False)
        oval(c, 0, my + 26, 11, 6, PALERED, None, 0)
    elif face == "think":
        stroke(c, [(-10, my + 4), (4, my + 8), (16, my)], INK, 5, smooth=True)
    if "mustache" in ch.extra:
        col = ch.hair_color if ch.hair != "bald" else "#3A2E28"
        for sx in (-1, 1):
            path = skia.Path()
            path.moveTo(0, my - 8)
            path.quadTo(sx * 22, my - 20, sx * 46, my - 4)
            path.quadTo(sx * 24, my + 2, 0, my - 2)
            path.close()
            shape(c, path, col, INK, 4, rough=False)
    if ch.glasses:
        for sx in (-1, 1):
            circ(c, sx * ex + lx * 0.4, ey + ly * 0.4, 25, None, INK, 5, rough=False)
        stroke(c, [(-ex + 25, ey - 2), (ex - 25, ey - 2)], INK, 4)


def person(c, ch: Char, x: float, y: float, s: float = 1.0, *, face: str = "smile", t: float = 0.0,
           armL=(100, 96), armR=(80, 84), look=(0, 0), talk: float = 0.0, tilt: float = 0.0, bob: float = 0.0,
           flip: bool = False, alpha: float = 1.0) -> dict:
    """腰部中点为 (x, y) 的半身角色。arm 为 (上臂角, 前臂角)，屏幕角度：0 向右、90 向下、180 向左、-90 向上。
    返回手与头的全局坐标，供调用方在手上放道具。"""
    out = {}
    y += bob
    sxm = -1 if flip else 1
    c.save()
    if alpha < 1:
        c.saveLayerAlpha(None, int(255 * alpha))
    c.translate(x, y)
    c.scale(s * sxm, s)
    # 躯干
    body = skia.Path.RRect(skia.Rect.MakeXYWH(-98, -232, 196, 250), 64, 64)
    shape(c, body, ch.shirt, INK, 6)
    if "apron" in ch.extra:
        rect(c, -70, -150, 140, 168, 20, CREAM, INK, 5, rough=False)
    if "collar" in ch.extra:
        poly(c, [(-34, -236), (0, -196), (34, -236)], CREAM, INK, 5, rough=False)
    if "cravat" in ch.extra:
        poly(c, [(-30, -236), (0, -192), (30, -236)], ch.trim, INK, 5, rough=False)
        circ(c, 0, -200, 10, RED, INK, 4, rough=False)
    if "bowtie" in ch.extra:
        poly(c, [(0, -214), (-34, -234), (-34, -194)], ch.trim, INK, 5, rough=False)
        poly(c, [(0, -214), (34, -234), (34, -194)], ch.trim, INK, 5, rough=False)
        circ(c, 0, -214, 9, ch.trim, INK, 4, rough=False)
    if "whistle" in ch.extra:
        stroke(c, [(-26, -234), (0, -170), (26, -234)], INK, 4)
        oval(c, 0, -166, 16, 11, GOLD, INK, 4, rough=False)
    # 两臂
    hands = []
    for side, (a1, a2) in ((-1, armL), (1, armR)):
        sh = (side * 84, -204)
        e = (sh[0] + 104 * math.cos(math.radians(a1)), sh[1] + 104 * math.sin(math.radians(a1)))
        h = (e[0] + 92 * math.cos(math.radians(a2)), e[1] + 92 * math.sin(math.radians(a2)))
        stroke(c, [sh, e], INK, 46)
        stroke(c, [e, h], INK, 38)
        stroke(c, [sh, e], ch.shirt, 34)
        stroke(c, [e, h], ch.skin, 26)
        circ(c, h[0], h[1], 21, ch.skin, INK, 5, rough=False)
        hands.append(h)
    # 头
    hx, hy = 0, -318
    c.save()
    c.translate(0, -236)
    c.rotate(tilt)
    c.translate(0, 236)
    rect(c, -18, -250, 36, 30, 0, ch.skin, INK, 5, rough=False)
    for sx in (-1, 1):
        circ(c, sx * 84, hy + 16, 17, ch.skin, INK, 5, rough=False)
    oval(c, hx, hy, 86, 90, ch.skin, INK, 6)
    c.save()
    c.translate(hx, hy)
    _face(c, ch, face, t, look, talk)
    if "sideburns" in ch.extra:
        for sx in (-1, 1):
            path = skia.Path()
            path.moveTo(sx * 70, -30)
            path.quadTo(sx * 98, 20, sx * 62, 66)
            path.quadTo(sx * 56, 30, sx * 56, -14)
            path.close()
            shape(c, path, ch.hair_color, INK, 4, rough=False)
    _hair(c, ch)
    c.restore()
    c.restore()
    if alpha < 1:
        c.restore()
    # 全局坐标
    for i, h in enumerate(hands):
        out["handL" if i == 0 else "handR"] = (x + h[0] * s * sxm, y + h[1] * s)
    out["head"] = (x, y + hy * s)
    c.restore()
    return out


# ------------------------------------------------------------------ 气泡

def bubble(c, cx, cy, w, h, label="", size=40, tail=(0, 1), fill=CREAM, color=INK, font="serif", a=1.0, scale=1.0,
           tail_to=None, rich_hi=None):
    """对话气泡；tail_to=(x, y) 为尾巴指向的全局点。"""
    if scale <= 0 or a <= 0:
        return
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    if tail_to is not None:
        tx, ty = (tail_to[0] - cx) / scale, (tail_to[1] - cy) / scale
        bx = max(-w / 2 + 50, min(w / 2 - 50, tx * 0.4))
        side = 1 if ty > 0 else -1
        poly(c, [(bx - 24, side * h / 2 - side * 4), (tx, ty), (bx + 24, side * h / 2 - side * 4)],
             fill, INK, 5, rough=False)
    crect(c, 0, 0, w, h, min(40, h / 2), fill, INK, 5, rough=False)
    if tail_to is not None:
        poly(c, [(bx - 20, side * h / 2 - side * 2), (bx + 20, side * h / 2 - side * 2),
                 (bx + 20, side * h / 2 + side * 3), (bx - 20, side * h / 2 + side * 3)], fill, None, 0, rough=False)
    if label:
        text(c, label, 0, size * 0.35, size, color, font, "c")
    if a < 1:
        c.restore()
    c.restore()


def thought(c, cx, cy, w, h, label="", size=40, fill=CREAM, a=1.0, scale=1.0, dots_to=None, font="serif", color=INK):
    """云朵形想法气泡，dots_to 为小圆点链指向的点。"""
    if scale <= 0 or a <= 0:
        return
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    if dots_to is not None:
        tx, ty = (dots_to[0] - cx) / scale, (dots_to[1] - cy) / scale
        for i, r in enumerate((16, 11, 7)):
            f = 0.62 + i * 0.16
            sy = h / 2 + 4 if ty > 0 else -h / 2 - 4
            circ(c, lerp(0, tx, f), lerp(sy, ty, f), r, fill, INK, 4, rough=False)
    crect(c, 0, 0, w, h, h / 2, fill, INK, 5)
    if label:
        text(c, label, 0, size * 0.35, size, color, font, "c")
    if a < 1:
        c.restore()
    c.restore()


# ------------------------------------------------------------------ 小图标

def check(c, x, y, size, p=1.0, color=BLUE, lw=14):
    if p <= 0:
        return
    pts = [(x - size * 0.5, y + size * 0.02), (x - size * 0.14, y + size * 0.4), (x + size * 0.52, y - size * 0.4)]
    path = skia.Path()
    path.moveTo(*pts[0])
    path.lineTo(*pts[1])
    path.lineTo(*pts[2])
    pm = skia.PathMeasure(path, False)
    seg = skia.Path()
    pm.getSegment(0, pm.getLength() * clamp01(p), seg, True)
    c.drawPath(seg, _paint(INK, 1, True, lw + 8))
    c.drawPath(seg, _paint(color, 1, True, lw))


def cross(c, x, y, size, p=1.0, color=RED, lw=14):
    if p <= 0:
        return
    a, b = clamp01(p * 2), clamp01(p * 2 - 1)
    h = size * 0.45
    for (p0, p1, q) in (((x - h, y - h), (x + h, y + h), a), ((x + h, y - h), (x - h, y + h), b)):
        if q <= 0:
            continue
        e = (p0[0] + (p1[0] - p0[0]) * q, p0[1] + (p1[1] - p0[1]) * q)
        stroke(c, [p0, e], INK, lw + 8)
        stroke(c, [p0, e], color, lw)


def sparkle(c, x, y, r, color=GOLD, a=1.0, rot=0.0):
    if r <= 0 or a <= 0:
        return
    pts = []
    for i in range(8):
        ang = math.radians(rot + i * 45)
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    poly(c, pts, color, INK, 3, a=a, rough=False)


def exclaim(c, x, y, size=60, color=RED, a=1.0):
    """惊叹号标记。"""
    text(c, "!", x, y, size, color, "black", "c", a, PAPER, 10)


def burst(c, x, y, r, fill=PALEGOLD, a=1.0, spikes=12, rot=0.0):
    """爆炸星形底。"""
    pts = []
    for i in range(spikes * 2):
        ang = math.radians(rot + i * 180 / spikes)
        rr = r if i % 2 == 0 else r * 0.78
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    poly(c, pts, fill, INK, 5, a=a)


def motion_lines(c, x, y, n=3, length=60, gap=18, ang=0.0, a=0.8, lw=6):
    for i in range(n):
        off = (i - (n - 1) / 2) * gap
        ox, oy = -math.sin(math.radians(ang)) * off, math.cos(math.radians(ang)) * off
        dx, dy = math.cos(math.radians(ang)) * length, math.sin(math.radians(ang)) * length
        stroke(c, [(x + ox, y + oy), (x + ox + dx, y + oy + dy)], INK, lw, a)


# ------------------------------------------------------------------ 手机与卡片

def phone(c, cx, cy, w, h, a=1.0):
    """返回屏幕区域 (x, y, w, h)。"""
    body = skia.Path.RRect(skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h), 44, 44)
    from .engine import drop_shadow
    drop_shadow(c, body, 8, 14, 12, 0.25 * a)
    rect(c, cx - w / 2, cy - h / 2, w, h, 44, INK, INK, 4, a=a, rough=False)
    sx, sy, sw, sh = cx - w / 2 + 14, cy - h / 2 + 18, w - 28, h - 36
    rect(c, sx, sy, sw, sh, 32, CREAM, None, 0, a=a, rough=False)
    crect(c, cx, cy - h / 2 + 12, 70, 10, 5, "#4A403A", None, 0, a=a, rough=False)
    return sx, sy, sw, sh


def card(c, cx, cy, w, h, fill=CREAM, rot=0.0, scale=1.0, a=1.0, lw=5, shadowed=True):
    """纸卡：返回 None，内容由调用方在 xf 内自行绘制。使用方式：with card_ctx(...)。"""
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(scale, scale)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    if shadowed:
        from .engine import drop_shadow
        drop_shadow(c, skia.Path.RRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 18, 18), 6, 10, 8, 0.22)
    rect(c, -w / 2, -h / 2, w, h, 18, fill, INK, lw)


def card_end(c, a=1.0):
    if a < 1:
        c.restore()
    c.restore()


def pin(c, x, y, color=RED):
    circ(c, x, y, 13, color, INK, 4, rough=False)
    circ(c, x - 4, y - 4, 4, CREAM, None, 0)


# ------------------------------------------------------------------ 文字块与图标

def pill(c, cx, cy, label, size=36, fill=CREAM, color=INK, font="sans", padx=26, a=1.0, scale=1.0, lw=5):
    """胶囊标签，以中心定位。"""
    if a <= 0 or scale <= 0:
        return
    w = text_w(label, size, font) + padx * 2
    h = size * 1.7
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    crect(c, 0, 0, w, h, h / 2, fill, INK, lw, rough=False)
    text(c, label, 0, size * 0.36, size, color, font, "c")
    if a < 1:
        c.restore()
    c.restore()


def big_title(c, lines, cy, t, size=96, start=0.0, hi=RED, gap=1.22, a=1.0):
    """屏幕大标题：逐行落入，可用【】高亮。cy 为第一行基线。"""
    from .engine import rich_line, parse_marks
    for i, ln in enumerate(lines):
        p = ease_out(prog(t, start + i * 0.18, 0.45))
        if p <= 0:
            continue
        segs = parse_marks(ln)
        rich_line(c, segs, 540, cy + i * size * gap - (1 - p) * 60, size, INK, hi, "black", p * a, PAPER, 16)


def doodle(c, kind, x, y, s=1.0, a=1.0):
    """小插图：卡片上的鲜活内容。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    if kind == "star":
        pts = []
        for i in range(10):
            ang = math.radians(-90 + i * 36)
            r = 44 if i % 2 == 0 else 19
            pts.append((r * math.cos(ang), r * math.sin(ang)))
        poly(c, pts, GOLD, INK, 5, rough=False)
    elif kind == "cat":
        poly(c, [(-38, -18), (-34, -58), (-8, -34)], KRAFT, INK, 5, rough=False)
        poly(c, [(38, -18), (34, -58), (8, -34)], KRAFT, INK, 5, rough=False)
        circ(c, 0, 0, 42, KRAFT, INK, 5, rough=False)
        for sx in (-1, 1):
            circ(c, sx * 16, -4, 5, INK, None, 0)
            stroke(c, [(sx * 26, 12), (sx * 52, 8)], INK, 3)
            stroke(c, [(sx * 26, 18), (sx * 52, 22)], INK, 3)
        poly(c, [(-5, 8), (5, 8), (0, 14)], RED, INK, 2, rough=False)
    elif kind == "bolt":
        poly(c, [(8, -50), (-26, 6), (-2, 6), (-12, 50), (28, -10), (4, -10)], GOLD, INK, 5, rough=False)
    elif kind == "flower":
        for i in range(5):
            ang = math.radians(-90 + i * 72)
            circ(c, 26 * math.cos(ang), 26 * math.sin(ang), 18, RED, INK, 4, rough=False)
        circ(c, 0, 0, 14, GOLD, INK, 4, rough=False)
    elif kind == "fish":
        oval(c, -4, 0, 40, 24, BLUE, INK, 5, rough=False)
        poly(c, [(32, 0), (58, -20), (58, 20)], BLUE, INK, 5, rough=False)
        circ(c, -22, -5, 5, CREAM, INK, 2, rough=False)
    elif kind == "balloon":
        stroke(c, [(0, 34), (6, 58), (-4, 74)], INK, 3)
        oval(c, 0, -4, 32, 40, RED, INK, 5, rough=False)
        poly(c, [(-6, 36), (6, 36), (0, 30)], RED, INK, 3, rough=False)
    elif kind == "heart":
        path = skia.Path()
        path.moveTo(0, 40)
        path.cubicTo(-70, -6, -34, -56, 0, -20)
        path.cubicTo(34, -56, 70, -6, 0, 40)
        shape(c, path, RED, INK, 5, rough=False)
    elif kind == "key":
        circ(c, -22, -10, 22, GOLD, INK, 5, rough=False)
        circ(c, -22, -10, 8, CREAM, INK, 3, rough=False)
        stroke(c, [(-2, 4), (44, 38)], INK, 14)
        stroke(c, [(-2, 4), (44, 38)], GOLD, 7)
    elif kind == "warn":
        poly(c, [(0, -48), (46, 34), (-46, 34)], RED, INK, 5, rough=False)
        rect(c, -4, -18, 8, 28, 3, CREAM, None, 0)
        circ(c, 0, 22, 5, CREAM, None, 0)
    if a < 1:
        c.restore()
    c.restore()


def magnifier(c, x, y, r=60, a=1.0, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    stroke(c, [(r * 0.7, r * 0.7), (r * 1.7, r * 1.7)], INK, 20)
    stroke(c, [(r * 0.7, r * 0.7), (r * 1.7, r * 1.7)], RED, 10)
    circ(c, 0, 0, r, "#FFFFFF", INK, 8, a=1.0, rough=False)
    circ(c, 0, 0, r, PALEBLUE, None, 0, a=0.35)
    if a < 1:
        c.restore()
    c.restore()


def bulb(c, x, y, r=40, on=1.0):
    glow(c, x, y, r * 2.6, GOLD, 0.5 * on)
    circ(c, x, y, r, mix_c(CREAM, GOLD, on), INK, 5, rough=False)
    rect(c, x - r * 0.45, y + r * 0.85, r * 0.9, r * 0.5, 4, GRAY, INK, 4, rough=False)
    stroke(c, [(x - r * 0.3, y + r * 0.2), (x, y - r * 0.2), (x + r * 0.3, y + r * 0.2)], INK, 3)


def mix_c(a, b, x):
    from .engine import mix
    return mix(a, b, x)


def squiggle(c, x0, x1, y, amp=6, n=5, color=INK, lw=5, a=1.0, p=1.0):
    pts = []
    steps = n * 6
    for i in range(steps + 1):
        u = i / steps
        pts.append((lerp(x0, x1, u), y + amp * math.sin(u * n * math.pi * 2)))
    from .engine import partial_stroke
    partial_stroke(c, pts, p, color, lw, a, smooth=False)
