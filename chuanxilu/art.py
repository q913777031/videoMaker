"""《传习录》系列小景：古人（王阳明、徐爱）与今人剪影、竹、亭、山洞、树与根、手机收藏夹、花盆、实验室、书卷、旌旗。

人物为水墨剪影（浓墨身形 + 淡墨衣褶），局部坐标以脚底 / 座底中心为原点，s 为缩放。
"""

import math

import numpy as np
import skia

from engine import gfx

from .ink import CINNABAR, INK, OCHRE, PAPER, brush_path, color, paint, smooth


def _poly(pts, close=True) -> skia.Path:
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def _curve(pts, n=60, close=True) -> skia.Path:
    return _poly([tuple(q) for q in smooth(pts, n)], close)


def _fig(c, x, y, s, alpha, flip=False):
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    return alpha


# ---------------------------------------------------------------- 古人

def _wash(c, pts, alpha, tone=INK, blur=2.5):
    """淡墨晕染的身形块面。"""
    c.drawPath(_curve(pts), paint(tone, alpha, blur=blur))


def _contour(c, pts, w, alpha, tone=INK):
    """浓墨轮廓线：起笔重、收笔尖。"""
    brush_path(c, smooth(pts, 30), w, tone=tone, alpha=alpha)


def _head(c, x, y, r, alpha, tone=INK, bun=True):
    """头：浓墨圆点；古人加发髻与簪。"""
    c.drawCircle(x, y, r, paint(tone, alpha, blur=0.8))
    if bun:
        c.drawCircle(x - r * 0.15, y - r * 1.05, r * 0.42, paint(tone, alpha))
        c.drawLine(x - r * 0.85, y - r * 1.05, x + r * 0.6, y - r * 1.15, paint(tone, alpha * 0.9, stroke=r * 0.12))


def scholar_seated(c: skia.Canvas, x: float, y: float, s: float = 1.0, alpha: float = 0.9, tone=INK, t: float = 0.0):
    """盘腿静坐的文人（王阳明）：宽袍淡墨、衣纹几笔浓墨、发髻；轻微呼吸起伏。"""
    if alpha <= 0:
        return
    _fig(c, x, y, s, alpha)
    c.scale(1, 1 + 0.008 * math.sin(t * 1.6))
    _wash(c, [(-160, -6), (-125, -60), (-80, -120), (-58, -200), (-30, -236), (30, -236), (58, -200), (80, -120),
              (125, -60), (160, -6), (0, 6)], alpha * 0.55, tone)
    _wash(c, [(-120, -30), (-60, -95), (0, -88), (60, -95), (120, -30), (0, -14)], alpha * 0.35, tone)
    _contour(c, [(-30, -232), (-62, -190), (-82, -118), (-130, -52), (-165, -8)], 9, alpha, tone)
    _contour(c, [(30, -232), (62, -192), (84, -120), (132, -54), (166, -8)], 8, alpha * 0.9, tone)
    _contour(c, [(-128, -10), (-60, -2), (0, 0), (70, -4), (140, -12)], 6, alpha * 0.8, tone)
    _contour(c, [(-62, -110), (-20, -96), (20, -96), (62, -110)], 6, alpha * 0.85, tone)
    _contour(c, [(-8, -226), (-14, -180), (-4, -140)], 4, alpha * 0.6, tone)
    _head(c, 0, -268, 30, alpha, tone)
    c.restore()


def scholar_standing(c: skia.Canvas, x: float, y: float, s: float = 1.0, alpha: float = 0.9, tone=INK,
                     bow: float = 0.0, flip: bool = False):
    """站立文人：长袍垂袖；bow ∈ [0, 1] 时上身前倾、双手拱于胸前（徐爱发问）。"""
    if alpha <= 0:
        return
    _fig(c, x, y, s, alpha, flip)
    lean = 18 * bow
    _wash(c, [(-62, 0), (-54, -110), (-46, -230), (-34 + lean, -318), (0 + lean, -336), (34 + lean, -318),
              (48, -230), (58, -110), (70, 0), (0, 6)], alpha * 0.55, tone)
    _contour(c, [(-30 + lean, -320), (-46, -230), (-54, -110), (-66, 0)], 8, alpha, tone)
    _contour(c, [(32 + lean, -320), (48, -228), (58, -110), (72, 0)], 7, alpha * 0.85, tone)
    _contour(c, [(-58, -4), (0, 2), (70, -4)], 5, alpha * 0.7, tone)
    if bow > 0.05:
        sx, sy = 30 + 34 * bow, -250 + 10 * bow
        _wash(c, [(-20 + lean, -300), (sx + 40, sy - 20), (sx + 56, sy + 20), (sx + 30, sy + 70), (-10, sy + 60),
                  (-30, -260)], alpha * 0.7, tone)
        _contour(c, [(-14 + lean, -298), (sx + 40, sy - 18), (sx + 56, sy + 22), (sx + 28, sy + 70)], 7, alpha, tone)
    else:
        _wash(c, [(-36, -300), (-70, -220), (-78, -140), (-50, -120), (-30, -200)], alpha * 0.6, tone)
        _contour(c, [(-34, -300), (-68, -222), (-78, -140), (-52, -118)], 6, alpha * 0.9, tone)
    _head(c, 4 + lean * 1.5, -366, 30, alpha, tone)
    c.restore()


def figure_fallen(c: skia.Canvas, x: float, y: float, s: float, alpha: float, tone=INK):
    """伏在矮几上病倒的人。"""
    if alpha <= 0:
        return
    _fig(c, x, y, s, alpha)
    _contour(c, [(-130, -66), (0, -70), (130, -66)], 9, alpha * 0.85, tone)
    _contour(c, [(-110, -64), (-112, 0)], 6, alpha * 0.7, tone)
    _contour(c, [(110, -64), (112, 0)], 6, alpha * 0.7, tone)
    _wash(c, [(-170, 0), (-150, -60), (-100, -100), (-20, -112), (40, -86), (50, -72), (-20, -66), (-80, -30),
              (-100, 0)], alpha * 0.55, tone)
    _contour(c, [(-165, -4), (-148, -60), (-98, -102), (-20, -112), (40, -88)], 8, alpha, tone)
    _head(c, 62, -88, 26, alpha, tone)
    c.restore()


# ---------------------------------------------------------------- 今人

def modern_bed_phone(c: skia.Canvas, x: float, y: float, s: float = 1.0, alpha: float = 0.9, glow: float = 1.0,
                     t: float = 0.0):
    """深夜半躺在床上刷手机的人：被子、枕头、手机冷光照脸。"""
    if alpha <= 0:
        return
    _fig(c, x, y, s, alpha)
    _wash(c, [(-240, 0), (-230, -50), (240, -50), (240, 0)], alpha * 0.22, INK, blur=1)
    _wash(c, [(-230, -50), (-170, -140), (-60, -165), (60, -138), (170, -118), (236, -60)], alpha * 0.3, INK)
    _contour(c, [(-226, -52), (-160, -140), (-60, -166), (60, -140), (170, -118), (236, -60)], 6, alpha * 0.7)
    _wash(c, [(-200, -150), (-160, -215), (-120, -275), (-80, -292), (-50, -255), (-40, -190), (-70, -150)],
          alpha * 0.6, INK)
    _contour(c, [(-196, -152), (-158, -215), (-118, -276), (-82, -292)], 7, alpha)
    _contour(c, [(-70, -248), (-25, -268), (-8, -300)], 10, alpha * 0.9)
    _head(c, -96, -326, 30, alpha, bun=False)
    c.drawPath(_curve([(-126, -338), (-110, -362), (-80, -360), (-66, -340), (-96, -350)]), paint(INK, alpha))
    if glow > 0:
        c.drawCircle(-40, -322, 170, paint((170, 205, 235), 0.32 * glow * alpha, blur=60))
    c.save()
    c.translate(-14, -326)
    c.rotate(-20)
    c.drawRoundRect(skia.Rect.MakeXYWH(-14, -26, 28, 52), 5, 5, paint(INK, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(-11, -22, 22, 44), 3, 3, paint((205, 228, 245), alpha * max(glow, 0.15)))
    c.restore()
    c.restore()


def modern_desk(c: skia.Canvas, x: float, y: float, s: float = 1.0, alpha: float = 0.9, glow: float = 1.0,
                frown: float = 0.0):
    """深夜坐在电脑前的人（侧身）：椅子、桌、笔记本屏幕冷光。"""
    if alpha <= 0:
        return
    _fig(c, x, y, s, alpha)
    _contour(c, [(-30, -190), (120, -192), (270, -190)], 10, alpha * 0.85)
    _contour(c, [(250, -188), (252, 0)], 7, alpha * 0.7)
    c.drawPath(_poly([(120, -194), (200, -194), (226, -300), (148, -300)]), paint(INK, alpha * 0.85))
    if glow > 0:
        c.drawCircle(150, -260, 160, paint((170, 205, 235), 0.3 * glow * alpha, blur=60))
    _wash(c, [(-120, 0), (-112, -100), (-96, -190), (-84, -290), (-44, -318), (-6, -292), (20, -232), (60, -206),
              (104, -200), (40, -176), (-20, -166), (-40, -90), (-34, 0)], alpha * 0.55, INK)
    _contour(c, [(-118, -4), (-110, -100), (-94, -190), (-82, -290), (-44, -318)], 8, alpha)
    _contour(c, [(-30, -270), (20, -232), (60, -206), (106, -200)], 7, alpha * 0.9)
    _head(c, -34 + 6 * frown, -350, 30, alpha, bun=False)
    c.drawPath(_curve([(-64, -362), (-50, -386), (-18, -384), (-4, -362), (-34, -372)]), paint(INK, alpha))
    _contour(c, [(-160, -150), (-60, -150)], 9, alpha * 0.6)
    _contour(c, [(-156, -148), (-158, 0)], 6, alpha * 0.55)
    c.restore()


# ---------------------------------------------------------------- 竹、亭、山洞

def bamboo(c: skia.Canvas, x: float, y_bottom: float, height: float, seed: int, t: float = 0.0,
           alpha: float = 0.85, width: float = 22, grow: float = 1.0):
    """一竿竹：竹节分段、节处浓墨、顶部竹叶簇随风轻摆；grow 从下往上长出。"""
    if alpha <= 0 or grow <= 0:
        return
    rng = np.random.default_rng(seed)
    sway = math.sin(t * 0.9 + seed) * 0.6
    n = 7
    seg = height / n
    lean = rng.uniform(-0.06, 0.06)
    pts = []
    for k in range(n + 1):
        u = k / n
        pts.append((x + lean * height * u + sway * 8 * u * u, y_bottom - seg * k))
    top_k = grow * n
    for k in range(n):
        if k >= top_k:
            break
        a, b = pts[k], pts[k + 1]
        part = min(1.0, top_k - k)
        bx, by = a[0] + (b[0] - a[0]) * part, a[1] + (b[1] - a[1]) * part
        w = width * (1 - 0.35 * k / n)
        tone = 0.55 + 0.25 * rng.random()
        c.drawLine(a[0], a[1] - 4, bx, by + 4, paint(INK, alpha * tone, stroke=w, cap=skia.Paint.kButt_Cap))
        if part >= 1:
            c.drawLine(b[0] - w * 0.7, b[1], b[0] + w * 0.7, b[1], paint(INK, alpha, stroke=4))
    if grow < 0.98:
        return
    for k in range(3, n + 1):
        if rng.random() < 0.55:
            continue
        bx, by = pts[k]
        side = rng.choice([-1, 1])
        for j in range(rng.integers(3, 6)):
            ang = math.radians(side * rng.uniform(15, 70) + 90 + sway * 6) + math.sin(t * 1.3 + j) * 0.03
            ln = rng.uniform(70, 130)
            leaf(c, bx, by, ang, ln, alpha * rng.uniform(0.55, 0.95))


def leaf(c: skia.Canvas, x: float, y: float, ang: float, ln: float, alpha: float):
    """竹叶：一笔下压再提起的狭长叶形。ang 为弧度（0 指向右，π/2 指向下）。"""
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(ang) - 90)
    p = skia.Path()
    p.moveTo(0, 0)
    p.cubicTo(ln * 0.12, ln * 0.25, ln * 0.1, ln * 0.7, 0, ln)
    p.cubicTo(-ln * 0.06, ln * 0.65, -ln * 0.09, ln * 0.25, 0, 0)
    c.drawPath(p, paint(INK, alpha))
    c.restore()


def pavilion(c: skia.Canvas, x: float, y: float, s: float = 1.0, alpha: float = 0.85):
    """亭子剪影：飞檐、两柱、台基。(x, y) 为台基中心。"""
    if alpha <= 0:
        return
    _fig(c, x, y, s, alpha)
    c.drawRect(skia.Rect.MakeXYWH(-170, -24, 340, 24), paint(INK, alpha * 0.7))
    for px in (-120, 120):
        c.drawLine(px, -24, px, -260, paint(INK, alpha * 0.85, stroke=16))
    c.drawLine(-140, -200, 140, -200, paint(INK, alpha * 0.6, stroke=6))
    roof = _curve([(-230, -250), (-150, -270), (-80, -310), (0, -380), (80, -310), (150, -270), (230, -250),
                   (240, -268), (160, -300), (0, -400), (-160, -300), (-240, -268)])
    c.drawPath(roof, paint(INK, alpha))
    c.drawLine(0, -400, 0, -440, paint(INK, alpha, stroke=8))
    c.restore()


def cave(c: skia.Canvas, x: float, y: float, w: float, h: float, alpha: float = 0.9, depth: float = 1.0):
    """山崖上的山洞：岩体淡墨层层叠染、几道顺势的长皴，洞口浓墨由外向里加深。(x, y) 为洞口底部中心。"""
    if alpha <= 0:
        return
    cliff = [(x - w * 2.4, y + 40), (x - w * 2.0, y - h * 0.7), (x - w * 1.3, y - h * 1.5), (x - w * 0.4, y - h * 1.95),
             (x + w * 0.6, y - h * 1.75), (x + w * 1.5, y - h * 1.1), (x + w * 2.3, y - h * 0.4), (x + w * 2.6, y + 40)]
    c.drawPath(_curve(cliff), paint((128, 126, 116), alpha * 0.4, blur=6))
    inner = [(x - w * 1.6, y + 30), (x - w * 1.3, y - h * 0.9), (x - w * 0.6, y - h * 1.45), (x + w * 0.4, y - h * 1.3),
             (x + w * 1.2, y - h * 0.7), (x + w * 1.7, y + 30)]
    c.drawPath(_curve(inner), paint((110, 108, 100), alpha * 0.3, blur=10))
    brush_path(c, smooth(cliff[1:-1], 60), 12, alpha=alpha * 0.8)
    for k, off in enumerate((0.25, 0.5, 0.75)):
        pts = [(px + (x - px) * off * 0.5, py + (y - py) * off * 0.45) for px, py in cliff[1:5]]
        brush_path(c, smooth(pts, 30), 7 - k, alpha=alpha * (0.5 - 0.1 * k))
    mouth = _curve([(x - w * 0.55, y), (x - w * 0.6, y - h * 0.6), (x - w * 0.32, y - h * 0.97), (x, y - h),
                    (x + w * 0.34, y - h * 0.94), (x + w * 0.58, y - h * 0.56), (x + w * 0.55, y)])
    shader = skia.GradientShader.MakeRadial((x, y - h * 0.4), w * 0.8,
                                            [color(INK, alpha * 0.96 * depth), color(INK, alpha * 0.72 * depth)])
    c.drawPath(mouth, skia.Paint(Shader=shader, AntiAlias=True))
    brush_path(c, smooth([(x - w * 0.58, y), (x - w * 0.6, y - h * 0.6), (x - w * 0.3, y - h * 0.98), (x + w * 0.1,
                                                                                                      y - h)], 30),
               9, alpha=alpha)


# ---------------------------------------------------------------- 树与根

def _branches(seed: int, x: float, y: float, ang: float, ln: float, depth: int, sign: int, out: list, t0=0.0):
    rng = np.random.default_rng(seed)
    ex, ey = x + math.cos(ang) * ln, y + sign * -math.sin(ang) * ln
    out.append((x, y, ex, ey, max(2.0, depth * 5.5), t0, depth))
    if depth <= 1:
        return
    for k in range(2 if depth > 2 else 3):
        da = rng.uniform(0.25, 0.7) * (1 if k % 2 == 0 else -1)
        _branches(seed * 7 + k + 1, ex, ey, ang + da, ln * rng.uniform(0.62, 0.8), depth - 1, sign, out, t0 + 1)


def tree(c: skia.Canvas, x: float, ground: float, s: float, roots: float, branches: float, leaves: float,
         alpha: float = 0.9, wither: float = 0.0):
    """树：roots / branches / leaves ∈ [0, 1] 分别控制根、枝、叶的生长进度；地面线以下为根。"""
    segs_up, segs_down = [], []
    _branches(3, x, ground, math.pi / 2, 210 * s, 6, 1, segs_up)
    _branches(9, x, ground, math.pi / 2, 120 * s, 5, -1, segs_down)
    c.drawLine(x - 380 * s, ground, x + 380 * s, ground, paint(INK, alpha * 0.5, stroke=3))
    for segs, prog_ in ((segs_down, roots), (segs_up, branches)):
        maxd = max(sg[5] for sg in segs) + 1
        for x0, y0, x1, y1, w, t0, _ in segs:
            q = gfx.clamp01(prog_ * maxd - t0)
            if q <= 0:
                continue
            tone = alpha * (0.85 if segs is segs_up else 0.55) * (1 - 0.6 * wither)
            c.drawLine(x0, y0, x0 + (x1 - x0) * q, y0 + (y1 - y0) * q, paint(INK, tone, stroke=w * s))
    if leaves > 0:
        rng = np.random.default_rng(4)
        tips = [sg for sg in segs_up if sg[6] == 1]
        for k, (_, _, x1, y1, _, _, _) in enumerate(tips):
            a = gfx.clamp01(leaves * len(tips) / 6 - k / 6) * alpha * (1 - wither)
            for j in range(3):
                c.drawCircle(x1 + rng.normal(0, 14 * s), y1 + rng.normal(0, 14 * s) + wither * 60, rng.uniform(9, 16) * s,
                             paint((70, 90, 70), a * 0.6, blur=2))


# ---------------------------------------------------------------- 手机、收藏卡、花盆

def phone(c: skia.Canvas, x: float, y: float, s: float, alpha: float = 1.0, glow: float = 0.6):
    """手机（以屏幕中心为原点，屏幕 300×560），返回屏幕内容区矩形。"""
    w, h = 320 * s, 600 * s
    if glow > 0:
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 30, y - h / 2 - 30, w + 60, h + 60), 60, 60,
                        paint((170, 205, 235), 0.25 * glow * alpha, blur=40))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 40 * s, 40 * s, paint(INK, alpha))
    inner = skia.Rect.MakeXYWH(x - w / 2 + 12 * s, y - h / 2 + 14 * s, w - 24 * s, h - 28 * s)
    c.drawRoundRect(inner, 30 * s, 30 * s, paint((244, 238, 226), alpha))
    return inner


def fav_card(c: skia.Canvas, x: float, y: float, w: float, title: str, alpha: float = 1.0, rot: float = 0.0,
             tone=INK, star: bool = True):
    """收藏夹里的一条“干货”：卡片 + 星标 + 标题 + 两行灰线。"""
    if alpha <= 0:
        return
    h = w * 0.26
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 12, 12, paint((255, 252, 244), alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 12, 12, paint(tone, alpha * 0.35, stroke=2))
    if star:
        star_path = skia.Path()
        r = h * 0.18
        for k in range(10):
            rr = r if k % 2 == 0 else r * 0.45
            a = -math.pi / 2 + k * math.pi / 5
            (star_path.moveTo if k == 0 else star_path.lineTo)(-w / 2 + h * 0.42 + math.cos(a) * rr,
                                                               -h * 0.12 + math.sin(a) * rr)
        star_path.close()
        c.drawPath(star_path, paint(CINNABAR, alpha * 0.9))
    f = gfx.font("serif_black", h * 0.28)
    c.drawString(title, -w / 2 + h * 0.8, -h * 0.02, f, paint(tone, alpha * 0.9))
    for k in range(2):
        c.drawLine(-w / 2 + h * 0.8, h * 0.18 + k * h * 0.17, w / 2 - h * (0.4 + 0.9 * k), h * 0.18 + k * h * 0.17,
                   paint(tone, alpha * 0.2, stroke=h * 0.07))
    c.restore()


def pot(c: skia.Canvas, x: float, y: float, s: float, alpha: float = 0.9):
    """空花盆（(x, y) 为盆口中心）。"""
    c.drawPath(_poly([(x - 150 * s, y), (x + 150 * s, y), (x + 110 * s, y + 190 * s), (x - 110 * s, y + 190 * s)]),
               paint(OCHRE, alpha * 0.75))
    c.drawRect(skia.Rect.MakeXYWH(x - 165 * s, y - 24 * s, 330 * s, 30 * s), paint(OCHRE, alpha * 0.95))
    c.drawOval(skia.Rect.MakeXYWH(x - 140 * s, y - 20 * s, 280 * s, 26 * s), paint(INK, alpha * 0.55))


# ---------------------------------------------------------------- 实验室、书卷、旌旗

def puzzle_cube(c: skia.Canvas, x: float, y: float, s: float, alpha: float = 1.0, tone=INK):
    """等轴测小方块拼图。"""
    for dx, dy in ((0, 0), (1, 0), (0, 1)):
        px, py = x + (dx - dy) * 26 * s, y + (dx + dy) * 15 * s
        top = _poly([(px, py - 30 * s), (px + 26 * s, py - 15 * s), (px, py), (px - 26 * s, py - 15 * s)])
        c.drawPath(top, paint(tone, alpha * 0.35))
        c.drawPath(_poly([(px - 26 * s, py - 15 * s), (px, py), (px, py + 30 * s), (px - 26 * s, py + 15 * s)]),
                   paint(tone, alpha * 0.75))
        c.drawPath(_poly([(px, py), (px + 26 * s, py - 15 * s), (px + 26 * s, py + 15 * s), (px, py + 30 * s)]),
                   paint(tone, alpha * 0.55))


def student_at_table(c: skia.Canvas, x: float, y: float, s: float, alpha: float, playing: float,
                     t: float = 0.0, coin: float = 0.0):
    """实验中的大学生：坐在桌前，playing ∈ [0, 1] 时手伸向桌上的拼图；coin > 0 时桌角出现铜钱。"""
    if alpha <= 0:
        return
    c.drawRect(skia.Rect.MakeXYWH(x - 130 * s, y - 120 * s, 260 * s, 12 * s), paint(INK, alpha * 0.8))
    c.drawLine(x - 110 * s, y - 108 * s, x - 110 * s, y, paint(INK, alpha * 0.6, stroke=8 * s))
    c.drawLine(x + 110 * s, y - 108 * s, x + 110 * s, y, paint(INK, alpha * 0.6, stroke=8 * s))
    puzzle_cube(c, x + 30 * s, y - 165 * s, 0.9 * s, alpha)
    lean = 0.4 + 0.6 * playing
    body = _curve([(x - 190 * s, y), (x - 185 * s, y - 120 * s), (x - 170 * s, y - 230 * s), (x - 140 * s, y - 250 * s),
                   (x - 110 * s, y - 220 * s), (x - 100 * s, y - 150 * s), (x - 140 * s, y - 100 * s), (x - 150 * s, y)])
    c.drawPath(body, paint(INK, alpha * 0.85))
    c.drawCircle(x - 145 * s + 18 * lean * s, y - 285 * s, 30 * s, paint(INK, alpha))
    hand_x = x - 110 * s + (110 * playing) * s + math.sin(t * 6) * 6 * playing
    c.drawLine(x - 120 * s, y - 210 * s, hand_x, y - 150 * s, paint(INK, alpha * 0.85, stroke=14 * s))
    if coin > 0:
        for k in range(3):
            cx, cy = x + 95 * s, y - 132 * s - k * 9 * s
            c.drawOval(skia.Rect.MakeXYWH(cx - 22 * s, cy - 7 * s, 44 * s, 14 * s), paint(OCHRE, coin * alpha))
            c.drawRect(skia.Rect.MakeXYWH(cx - 5 * s, cy - 3 * s, 10 * s, 6 * s), paint(INK, coin * alpha * 0.7))


def door(c: skia.Canvas, x: float, y: float, s: float, open_: float, alpha: float = 0.9):
    """门框与门扇：open_ ∈ [0, 1]。(x, y) 为门底中心。"""
    w, h = 150 * s, 320 * s
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2 - 10, y - h - 10, w + 20, h + 10), paint(INK, alpha * 0.8, stroke=8))
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h, w, h), paint(INK, alpha * 0.85))
    leaf_w = w * (1 - 0.8 * open_)
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h, leaf_w, h), paint(OCHRE, alpha * 0.9))
    c.drawCircle(x - w / 2 + leaf_w - 16 * s, y - h / 2, 6 * s, paint(INK, alpha))


def books(c: skia.Canvas, x: float, y: float, s: float, n: int = 4, alpha: float = 0.9, dust: float = 0.0,
          t: float = 0.0):
    """线装书一摞；dust 为落灰程度。"""
    for k in range(n):
        by = y - k * 34 * s
        c.drawRect(skia.Rect.MakeXYWH(x - 140 * s + (k % 2) * 10 * s, by - 30 * s, 280 * s, 30 * s),
                   paint((95, 110, 120), alpha * 0.85))
        for j in range(4):
            c.drawLine(x - 120 * s + j * 30 * s, by - 30 * s, x - 120 * s + j * 30 * s, by, paint(PAPER, alpha * 0.6,
                                                                                                    stroke=2))
        c.drawRect(skia.Rect.MakeXYWH(x + 60 * s, by - 26 * s, 44 * s, 22 * s), paint(PAPER, alpha * 0.8))
    if dust > 0:
        rng = np.random.default_rng(2)
        top = y - n * 34 * s
        c.drawRect(skia.Rect.MakeXYWH(x - 140 * s, top - 6 * s, 290 * s, 10 * s), paint((200, 190, 170), dust * alpha))
        for _ in range(40):
            px = x + rng.uniform(-200, 200) * s
            py = top - rng.uniform(0, 260) * s + (t * 20 * rng.uniform(0.5, 1.5)) % (260 * s)
            c.drawCircle(px, py, rng.uniform(1, 3) * s, paint((170, 160, 140), dust * alpha * 0.6))


def banner(c: skia.Canvas, x: float, y: float, s: float, t: float, alpha: float = 0.9, char: str = "王"):
    """旌旗：旗杆 + 飘动的三角旗，旗上一个字。(x, y) 为杆底。"""
    c.drawLine(x, y, x, y - 520 * s, paint(INK, alpha, stroke=10 * s))
    c.drawPath(_poly([(x - 14 * s, y - 520 * s), (x + 14 * s, y - 520 * s), (x, y - 570 * s)]), paint(INK, alpha))
    pts = []
    for k in range(9):
        u = k / 8
        pts.append((x + u * 300 * s, y - 500 * s + math.sin(t * 3 + u * 4) * 18 * s * u))
    for k in range(8, -1, -1):
        u = k / 8
        pts.append((x + u * 300 * s * (1 - 0.15 * u), y - 300 * s - u * 120 * s + math.sin(t * 3 + u * 4) * 18 * s * u))
    c.drawPath(_poly(pts), paint(CINNABAR, alpha * 0.9))
    f = gfx.font("serif_black", 110 * s)
    wch = f.measureText(char)
    c.drawString(char, x + 130 * s - wch / 2, y - 365 * s, f, paint(PAPER, alpha))


def lectern(c: skia.Canvas, x: float, y: float, s: float, alpha: float = 0.9):
    """讲学：先生立于案后，前面坐着三名学生。"""
    scholar_standing(c, x, y, s, alpha)
    c.drawRect(skia.Rect.MakeXYWH(x - 110 * s, y - 180 * s, 220 * s, 14 * s), paint(INK, alpha * 0.8))
    for k in range(3):
        scholar_seated(c, x + (k - 1) * 190 * s, y + 230 * s, 0.55 * s, alpha * 0.75)


# ---------------------------------------------------------------- 第 01 讲第七版新增小景

def coffin(c: skia.Canvas, x: float, y: float, s: float = 1.0, alpha: float = 0.9):
    """石棺（侧视）：石板盖、棺身皴擦。(x, y) 为底边中心。"""
    if alpha <= 0:
        return
    body = _poly([(x - 170 * s, y), (x + 170 * s, y), (x + 150 * s, y - 95 * s), (x - 160 * s, y - 95 * s)])
    c.drawPath(body, paint((120, 118, 108), alpha * 0.75, blur=1.5))
    c.drawPath(_poly([(x - 180 * s, y - 92 * s), (x + 165 * s, y - 92 * s), (x + 150 * s, y - 122 * s),
                      (x - 172 * s, y - 120 * s)]), paint((95, 93, 85), alpha * 0.9))
    brush_path(c, [(x - 170 * s, y), (x + 170 * s, y)], 6 * s, alpha=alpha)
    brush_path(c, [(x - 180 * s, y - 92 * s), (x + 165 * s, y - 92 * s)], 5 * s, alpha=alpha * 0.9)
    rng = np.random.default_rng(8)
    for _ in range(7):
        px = x + rng.uniform(-140, 130) * s
        py = y - rng.uniform(15, 80) * s
        brush_path(c, [(px, py), (px + rng.uniform(20, 50) * s, py + rng.uniform(-6, 6) * s)], 3 * s,
                   alpha=alpha * 0.45)


def courier(c: skia.Canvas, x: float, y: float, s: float = 1.0, alpha: float = 0.9, climb: float = 0.0,
            t: float = 0.0):
    """外卖骑手：头盔、外卖箱；climb > 0 时做爬楼梯的抬腿动作。(x, y) 为脚底中心。"""
    if alpha <= 0:
        return
    _fig(c, x, y, s, alpha)
    step = math.sin(t * 8) * 18 * climb
    _contour(c, [(-16, -150), (-24, -70), (-30 + step, 0)], 24, alpha * 0.9, )
    _contour(c, [(16, -150), (22, -70), (30 - step, -10 * climb)], 24, alpha * 0.9)
    _wash(c, [(-46, -150), (-40, -270), (0, -292), (40, -270), (46, -150), (0, -140)], alpha * 0.7)
    _contour(c, [(-44, -150), (-40, -270), (0, -290)], 7, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(-112, -290, 76, 80), 8, 8, paint((214, 160, 40), alpha * 0.95))
    c.drawRect(skia.Rect.MakeXYWH(-112, -262, 76, 8), paint(INK, alpha * 0.4))
    _head(c, 4, -322, 28, alpha, bun=False)
    c.drawPath(_curve([(-30, -322), (-26, -356), (4, -366), (34, -352), (36, -322), (4, -334)]),
               paint((214, 160, 40), alpha))
    c.restore()


def stairs(c: skia.Canvas, x: float, y: float, s: float, n: int, alpha: float = 0.8):
    """楼梯折线（右上方向）。(x, y) 为第一级左下角。"""
    pts = [(x, y)]
    for k in range(n):
        px, py = pts[-1]
        pts += [(px, py - 50 * s), (px + 70 * s, py - 50 * s)]
    brush_path(c, pts, 6 * s, alpha=alpha, taper=False)
    brush_path(c, [(x - 20 * s, y + 10 * s), (pts[-1][0] + 40 * s, pts[-1][1] + 10 * s)], 4 * s, alpha=alpha * 0.5,
               taper=False)


def cig_box(c: skia.Canvas, x: float, y: float, s: float, rows: int, p: float, alpha: float = 1.0,
            rot: float = -6.0, seed: int = 0):
    """烟盒背面的手写诗行：只画抽象的手写笔迹（不写具体诗句，避免虚构引文），p 控制逐行写出。"""
    if alpha <= 0:
        return
    rng = np.random.default_rng(seed)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.drawRoundRect(skia.Rect.MakeXYWH(-130 * s, -190 * s, 260 * s, 380 * s), 10, 10, paint((240, 232, 214), alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(-130 * s, -190 * s, 260 * s, 380 * s), 10, 10,
                    paint(OCHRE, alpha * 0.6, stroke=3))
    c.drawRect(skia.Rect.MakeXYWH(-130 * s, -190 * s, 260 * s, 60 * s), paint(CINNABAR, alpha * 0.55))
    for k in range(rows):
        q = max(0.0, min(1.0, p * rows - k))
        if q <= 0:
            break
        ln = rng.uniform(140, 210) * s
        y0 = -90 * s + k * 52 * s
        pts = [(-105 * s + u * ln, y0 + math.sin(u * 40 + k) * 6 * s + rng.normal(0, 1.5) * s)
               for u in np.linspace(0, 1, 40)]
        brush_path(c, pts, 4 * s, p=q, alpha=alpha * 0.85, taper=False)
    c.restore()


def book_cover(c: skia.Canvas, x: float, y: float, s: float, title: str, sub: str, alpha: float = 1.0):
    """诗集书封：竖排书名。"""
    if alpha <= 0:
        return
    w, h = 300 * s, 430 * s
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 12, y - h / 2 + 14, w, h), paint((90, 70, 50), 0.2 * alpha, blur=12))
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), paint((236, 226, 204), alpha))
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, 22 * s, h), paint(CINNABAR, alpha * 0.85))
    f = gfx.font("serif_black", 50 * s)
    for k, ch in enumerate(title):
        wch = f.measureText(ch)
        c.drawString(ch, x + 40 * s - wch / 2, y - h / 2 + 80 * s + k * 58 * s, f, paint(INK, alpha))
    f2 = gfx.font("serif_medium", 24 * s)
    for k, ch in enumerate(sub):
        wch = f2.measureText(ch)
        c.drawString(ch, x - 60 * s - wch / 2, y - h / 2 + 90 * s + k * 30 * s, f2, paint(OCHRE, alpha))


def window(c: skia.Canvas, x: float, y: float, s: float, open_: float, alpha: float = 0.9, light: float = 0.0):
    """窗与窗帘：open_ ∈ [0, 1] 拉开程度，light 为窗外晨光强度。(x, y) 为窗中心。"""
    w, h = 360 * s, 460 * s
    rect = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    if light > 0:
        c.drawCircle(x, y, 520 * s, paint((255, 214, 150), 0.35 * light * alpha, blur=120))
    c.drawRect(rect, paint((250, 236, 205) if light > 0 else (200, 205, 210), alpha * (0.6 + 0.4 * light)))
    c.drawRect(rect, paint(INK, alpha * 0.8, stroke=8))
    c.drawLine(x, y - h / 2, x, y + h / 2, paint(INK, alpha * 0.6, stroke=5))
    cw = w / 2 * (1 - 0.82 * open_)
    for side in (-1, 1):
        cx = x + side * (w / 2 - cw / 2)
        c.drawRect(skia.Rect.MakeXYWH(cx - cw / 2, y - h / 2 - 20, cw, h + 40), paint((120, 96, 80), alpha * 0.85))
        for k in range(3):
            fx = cx - cw / 2 + cw * (k + 1) / 4
            c.drawLine(fx, y - h / 2 - 20, fx, y + h / 2 + 20, paint(INK, alpha * 0.25, stroke=3))


def progress_bar(c: skia.Canvas, x: float, y: float, w: float, frac: float, label: str, alpha: float = 1.0):
    """网课进度条：标题 + 细条 + 百分比。"""
    if alpha <= 0:
        return
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 30, y - 70, w + 60, 150), 20, 20, paint((255, 252, 244), alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 30, y - 70, w + 60, 150), 20, 20, paint(INK, alpha * 0.3, stroke=2))
    f = gfx.font("serif_black", 34)
    c.drawString(label, x - w / 2, y - 18, f, paint(INK, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y + 20, w, 18), 9, 9, paint(INK, alpha * 0.15))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y + 20, w * frac, 18), 9, 9, paint(CINNABAR, alpha * 0.85))


def subway(c: skia.Canvas, x: float, y: float, s: float, alpha: float = 0.9, t: float = 0.0):
    """地铁车厢里站着低头刷手机的人：扶手横杆 + 吊环 + 车窗。(x, y) 为脚底中心。"""
    if alpha <= 0:
        return
    sway = math.sin(t * 1.3) * 4
    c.drawLine(x - 380 * s, y - 560 * s, x + 380 * s, y - 560 * s, paint(INK, alpha * 0.7, stroke=8 * s))
    for k in range(5):
        hx = x - 300 * s + k * 150 * s + sway
        c.drawLine(hx, y - 560 * s, hx, y - 500 * s, paint(INK, alpha * 0.6, stroke=4 * s))
        c.drawOval(skia.Rect.MakeXYWH(hx - 18 * s, y - 500 * s, 36 * s, 40 * s), paint(INK, alpha * 0.6, stroke=5 * s))
    for k in range(2):
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 380 * s + k * 420 * s, y - 470 * s, 340 * s, 170 * s), 20, 20,
                        paint((150, 170, 185), alpha * 0.25))
    _fig(c, x + 60 * s, y, s, alpha)
    _contour(c, [(-16, -150), (-20, -70), (-24, 0)], 24, alpha * 0.9)
    _contour(c, [(16, -150), (20, -70), (26, 0)], 24, alpha * 0.9)
    _wash(c, [(-48, -150), (-44, -280), (0, -300), (44, -280), (48, -150), (0, -140)], alpha * 0.65)
    _contour(c, [(40, -280), (60, -380), (64, -470)], 9, alpha * 0.9)
    _contour(c, [(-36, -270), (-6, -230), (20, -236)], 9, alpha * 0.9)
    _head(c, -4, -330, 28, alpha, bun=False)
    c.drawRoundRect(skia.Rect.MakeXYWH(14, -262, 26, 46), 5, 5, paint(INK, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(17, -259, 20, 40), 3, 3, paint((205, 228, 245), alpha))
    c.drawCircle(27, -250, 70, paint((170, 205, 235), 0.25 * alpha, blur=30))
    c.restore()


def congee_pot(c: skia.Canvas, x: float, y: float, s: float, t: float, alpha: float = 0.9):
    """柴火上煮粥的陶罐，冒热气。(x, y) 为火堆中心。"""
    if alpha <= 0:
        return
    for k in range(5):
        a = -0.6 + k * 0.3
        brush_path(c, [(x + math.sin(a) * 70 * s, y + 10 * s), (x - math.sin(a) * 50 * s, y - 30 * s)], 9 * s,
                   tone=(110, 80, 50), alpha=alpha)
    fl = 1 + 0.1 * math.sin(t * 14)
    c.drawCircle(x, y - 20 * s, 60 * s * fl, paint((255, 170, 80), 0.5 * alpha, blur=26 * s))
    c.drawPath(_curve([(x - 80 * s, y - 50 * s), (x - 90 * s, y - 120 * s), (x - 60 * s, y - 170 * s),
                       (x + 60 * s, y - 170 * s), (x + 90 * s, y - 120 * s), (x + 80 * s, y - 50 * s)]),
               paint((90, 70, 55), alpha))
    for k in range(3):
        sx = x + (k - 1) * 30 * s
        pts = [(sx + math.sin(t * 2 + k + j * 0.8) * 12 * s, y - 180 * s - j * 30 * s) for j in range(6)]
        brush_path(c, smooth(pts, 20), 7 * s, tone=(180, 175, 165), alpha=alpha * 0.45)
