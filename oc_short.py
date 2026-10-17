"""《机会成本》竖屏知识短视频（无声版）：按 scripts/opportunity_cost.md 的 14 镜分镜逐帧绘制。

复古插画风格：米白纸张底 + 墨线轮廓（逐帧轻微抖动模拟手绘）+ 暖金光 + 少量红蓝强调。
没有配音与音乐，口播以字幕呈现，镜头时间严格按分镜表。
用法：python3 oc_short.py [输出路径]       渲染成片（默认 out/opportunity_cost_silent.mp4）
      python3 oc_short.py --stills 目录   每镜导出关键帧 PNG 用于检查
"""

import functools
import math
import subprocess
import sys
from dataclasses import dataclass
from multiprocessing import get_context
from pathlib import Path

import cv2
import numpy as np
import skia

from engine import gfx
from engine.gfx import clamp01, col, ease_in_out, ease_out, ease_out_back, lerp, mix, prog

W, H, FPS = 1080, 1920, 30
gfx.FONT_FILES.update({"serif": "NotoSerifCJKsc-Black.otf", "serifb": "NotoSerifCJKsc-Bold.otf"})

PAPER, PAPER2, PAPER3 = "#F3EAD8", "#E9DDC4", "#DCCDB0"
INK, INK2 = "#2A2420", "#6E655B"
GOLD, RED, BLUE = "#E2A33A", "#C2413A", "#3A6AA5"
SKIN, MUSTARD, JEANS, BAG = "#F1CFAE", "#D9A23A", "#3E5478", "#D8C49C"
GREEN, BROWN, HAIR = "#4F6A48", "#7B5233", "#1F1B19"
AMBER, ROAD, WOOD = "#D88A2B", "#E6D6B2", "#E3C690"

TITLE_Y, CAP_Y = 330, 1500
_FRAME = 0  # 当前帧号，用于墨线"抖动"的随机种子


# ================================================================ 基础绘制

@functools.lru_cache(maxsize=256)
def _wobble(width: float, seed: int) -> skia.PathEffect:
    return skia.DiscretePathEffect.Make(max(8.0, width * 2.6), min(1.6, 0.25 + width * 0.22), seed)


def ink_paint(width: float = 5, color=INK, alpha: float = 1.0, wobble: bool = True) -> skia.Paint:
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width, Color=col(color, alpha),
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    if wobble:
        p.setPathEffect(_wobble(round(width), (_FRAME // 4) % 3 + 1))
    return p


def fill_paint(color, alpha: float = 1.0) -> skia.Paint:
    return skia.Paint(AntiAlias=True, Color=col(color, alpha))


def shape(c, path: skia.Path, fill=None, alpha: float = 1.0, w: float = 5, line=INK):
    """填充后描墨线；fill 为 None 时只描线，w 为 0 时只填充。"""
    if alpha <= 0:
        return
    if fill is not None:
        c.drawPath(path, fill_paint(fill, alpha))
    if w > 0:
        c.drawPath(path, ink_paint(w, line, alpha))


def rect_path(x, y, w, h, r=0.0) -> skia.Path:
    """左上角 (x, y) 的圆角矩形路径。"""
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r))
    return p


def circle_path(x, y, r) -> skia.Path:
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def oval_path(x, y, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry))
    return p


def poly(points, close=True) -> skia.Path:
    p = skia.Path()
    p.moveTo(*points[0])
    for q in points[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def line(c, x0, y0, x1, y1, w=5, color=INK, alpha=1.0, p: float = 1.0):
    if alpha <= 0 or p <= 0:
        return
    c.drawLine(x0, y0, lerp(x0, x1, p), lerp(y0, y1, p), ink_paint(w, color, alpha, wobble=False))


def text(c, s, x, y, size, name="bold", fill=INK, alpha=1.0, align="center", halo=True, hi=RED):
    """带纸色描边的文字，支持【】高亮。"""
    stroke = (PAPER, size * 0.22) if halo else None
    return gfx.draw_rich(c, s, x, y, size, name, fill, hi, alpha, align, stroke=stroke)


class cam:
    """以 (cx, cy) 为中心缩放 s 并平移 (dx, dy) 的镜头变换。"""

    def __init__(self, c, s=1.0, cx=W / 2, cy=H / 2, dx=0.0, dy=0.0, rot=0.0):
        self.c, self.a = c, (s, cx, cy, dx, dy, rot)

    def __enter__(self):
        s, cx, cy, dx, dy, rot = self.a
        self.c.save()
        self.c.translate(cx + dx, cy + dy)
        self.c.rotate(rot)
        self.c.scale(s, s)
        self.c.translate(-cx, -cy)

    def __exit__(self, *_):
        self.c.restore()


def layer(c, alpha=1.0, gray=0.0, blur_x=0.0):
    """开启一个带透明度 / 去色 / 横向模糊的图层，调用方负责 restore。"""
    p = skia.Paint(Alphaf=clamp01(alpha))
    if gray > 0:
        p.setColorFilter(gfx._gray_filter(round(clamp01(gray), 2)))
    if blur_x > 0:
        p.setImageFilter(skia.ImageFilters.Blur(blur_x, 0.1))
    c.saveLayer(None, p)


# ================================================================ 纸张底与颗粒

def _noise(shape_hw, scale, seed):
    rng = np.random.default_rng(seed)
    h, w = shape_hw
    small = rng.standard_normal((max(2, h // scale), max(2, w // scale))).astype(np.float32)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC)


@functools.lru_cache(maxsize=None)
def paper_image() -> skia.Image:
    base = np.array(gfx.rgb(PAPER), np.float32)
    n = _noise((H, W), 160, 1) * 5 + _noise((H, W), 24, 2) * 3 + _noise((H, W), 2, 3) * 3.5
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.46) / (H * 0.62)) ** 2)
    edge = np.clip(d - 0.55, 0, 1) ** 1.6 * 46
    img = base[None, None, :] + n[..., None] - edge[..., None] * np.array([0.8, 1.0, 1.35], np.float32)
    rgba = np.dstack([np.clip(img, 0, 255).astype(np.uint8), np.full((H, W), 255, np.uint8)])
    return skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType)


@functools.lru_cache(maxsize=None)
def grain_image(k: int) -> skia.Image:
    """叠加在最上层的胶片颗粒与纸纤维（正片叠底），3 张轮换。"""
    rng = np.random.default_rng(100 + k)
    g = rng.standard_normal((H, W)).astype(np.float32) * 10
    v = 255 - np.clip(np.abs(g), 0, 40)
    fib = np.zeros((H, W), np.uint8)
    for _ in range(140):
        x, y = int(rng.integers(0, W)), int(rng.integers(0, H))
        ang, ln = rng.uniform(0, math.pi), rng.uniform(10, 40)
        cv2.line(fib, (x, y), (int(x + ln * math.cos(ang)), int(y + ln * math.sin(ang))), 22, 1, cv2.LINE_AA)
    v = np.clip(v - fib, 0, 255).astype(np.uint8)
    rgba = np.dstack([v, v, (v * 0.985).astype(np.uint8), np.full((H, W), 255, np.uint8)])
    return skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType)


# ================================================================ 角色

def limb(c, x0, y0, a1, a2, l1, l2, width, color, s):
    """两段式手臂 / 腿；角度 0 指向正下方，90 指向右，180 指向上；返回末端坐标。"""
    r1, r2 = math.radians(a1), math.radians(a2)
    x1, y1 = x0 + l1 * math.sin(r1), y0 + l1 * math.cos(r1)
    x2, y2 = x1 + l2 * math.sin(r2), y1 + l2 * math.cos(r2)
    path = poly([(x0, y0), (x1, y1), (x2, y2)], close=False)
    c.drawPath(path, ink_paint(width + 9 * s, INK))
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width, Color=col(color),
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    c.drawPath(path, p)
    return x2, y2


LOOKS = {
    "lin": dict(top=MUSTARD, legs=JEANS, hair="lin", glasses=True, shoes="#5B4636", bag=True),
    "jie": dict(top=GREEN, legs="#4A4744", hair="jie", glasses=False, shoes="#F4F1EA", bag=False),
    "clerk": dict(top="#EFE6D3", legs="#4A4744", hair="clerk", glasses=False, shoes="#3B332D", bag=False,
                  apron=RED),
}


def person(c, x, y, s=1.0, who="lin", arms=((-8, -4), (8, 4)), look=0.0, mouth="smile", tilt=0.0,
           brow=0.0, blink=False, legs=(0, 0), alpha=1.0, hold=None):
    """正面卡通人物，(x, y) 为双脚中点。arms=((左肩角, 左肘角), (右肩角, 右肘角))；
    hold(c, hx, hy, side) 在手的位置画道具；返回 (左手, 右手) 坐标。"""
    if alpha <= 0:
        return (x, y), (x, y)
    lk = LOOKS[who]
    if alpha < 1:
        layer(c, alpha)
    hip, sh = y - 170 * s, y - 368 * s
    # 腿与鞋
    for side, a in ((-1, legs[0]), (1, legs[1])):
        lx = x + side * 30 * s
        ex, ey = limb(c, lx, hip, a, a * 0.6, 88 * s, 78 * s, 46 * s, lk["legs"], s)
        shape(c, oval_path(ex + side * 8 * s, ey + 4 * s, 32 * s, 15 * s), lk["shoes"], w=4 * s)
    # 兜帽（在头后）
    if who == "lin":
        shape(c, oval_path(x, sh + 8 * s, 70 * s, 34 * s), mix(MUSTARD, INK, 0.12), w=5 * s)
    # 躯干
    torso = skia.Path()
    torso.moveTo(x - 82 * s, sh + 10 * s)
    torso.quadTo(x, sh - 16 * s, x + 82 * s, sh + 10 * s)
    torso.lineTo(x + 74 * s, hip + 8 * s)
    torso.quadTo(x, hip + 22 * s, x - 74 * s, hip + 8 * s)
    torso.close()
    shape(c, torso, lk["top"], w=5.5 * s)
    if who == "lin":
        pocket = rect_path(x - 46 * s, hip - 70 * s, 92 * s, 52 * s, 16 * s)
        c.drawPath(pocket, ink_paint(3.5 * s, INK, 0.7))
        line(c, x - 16 * s, sh + 8 * s, x - 20 * s, sh + 58 * s, 3.5 * s)
        line(c, x + 16 * s, sh + 8 * s, x + 20 * s, sh + 58 * s, 3.5 * s)
    if who == "jie":
        shape(c, poly([(x - 34 * s, sh), (x, sh + 52 * s), (x + 34 * s, sh)]), "#F4EFE4", w=4 * s)
        line(c, x, sh + 52 * s, x, hip, 3.5 * s, INK, 0.7)
    if lk.get("apron"):
        shape(c, rect_path(x - 56 * s, sh + 60 * s, 112 * s, 150 * s, 14 * s), lk["apron"], w=4.5 * s)
    if lk["bag"]:
        strap = poly([(x - 66 * s, sh + 10 * s), (x + 58 * s, hip - 4 * s)], close=False)
        c.drawPath(strap, ink_paint(20 * s, INK))
        sp = ink_paint(13 * s, BAG, wobble=False)
        c.drawPath(strap, sp)
        shape(c, rect_path(x + 40 * s, hip - 40 * s, 66 * s, 58 * s, 10 * s), BAG, w=4.5 * s)
    # 头
    hx, hy = x + tilt * 6 * s, sh - 62 * s
    shape(c, rect_path(x - 15 * s, sh - 26 * s, 30 * s, 30 * s), SKIN, w=0)
    c.save()
    c.translate(hx, hy)
    c.rotate(tilt * 8)
    r = 64 * s
    for side in (-1, 1):
        shape(c, circle_path(side * r * 0.98, 8 * s, 13 * s), SKIN, w=4 * s)
    shape(c, circle_path(0, 0, r), SKIN, w=5.5 * s)
    lx = look * 15 * s
    # 头发
    if lk["hair"] == "lin":
        hp = skia.Path()
        hp.moveTo(-r * 1.04, 6 * s)
        hp.arcTo(skia.Rect.MakeLTRB(-r * 1.06, -r * 1.1, r * 1.06, r * 0.96), 175, 190, False)
        pts = [(r * 1.0, -4 * s)]
        for k in range(7):
            fx = lerp(r * 0.9, -r * 0.9, k / 6) + lx * 0.6
            pts.append((fx + 8 * s, -r * 0.42 + (k % 2) * 12 * s))
        for q in pts:
            hp.lineTo(*q)
        hp.close()
        shape(c, hp, HAIR, w=4 * s)
    elif lk["hair"] == "jie":
        for k in range(9):
            a = math.radians(170 + k * 25)
            shape(c, circle_path(math.cos(a) * r * 0.86, math.sin(a) * r * 0.86 - 4 * s, 23 * s), BROWN,
                  w=3.5 * s)
        shape(c, oval_path(0, -r * 0.55, r * 0.8, r * 0.42), BROWN, w=0)
    else:
        cap = skia.Path()
        cap.moveTo(-r * 0.98, -r * 0.2)
        cap.arcTo(skia.Rect.MakeLTRB(-r, -r * 1.05, r, r * 0.6), 180, 180, False)
        cap.close()
        shape(c, cap, RED, w=4 * s)
        shape(c, oval_path(r * 0.55, -r * 0.2, r * 0.6, 9 * s), RED, w=4 * s)
    # 五官
    ey = 6 * s
    for side in (-1, 1):
        ex = side * 26 * s + lx
        if blink:
            line(c, ex - 6 * s, ey, ex + 6 * s, ey, 4 * s)
        else:
            c.drawCircle(ex + look * 3 * s, ey, 5.5 * s, fill_paint(INK))
        by = ey - 22 * s - (brow * side * 5 * s if brow else 0)
        line(c, ex - 10 * s, by + brow * 4 * s * side, ex + 10 * s, by - brow * 4 * s * side, 4 * s)
        if lk["glasses"]:
            c.drawCircle(ex, ey, 19 * s, ink_paint(4 * s))
    if lk["glasses"]:
        line(c, -7 * s + lx, ey, 7 * s + lx, ey, 4 * s)
    my = 34 * s
    mp = skia.Path()
    if mouth == "smile":
        mp.arcTo(skia.Rect.MakeLTRB(lx - 16 * s, my - 18 * s, lx + 16 * s, my + 6 * s), 20, 140, True)
        c.drawPath(mp, ink_paint(4.5 * s))
    elif mouth == "big":
        mp.arcTo(skia.Rect.MakeLTRB(lx - 18 * s, my - 18 * s, lx + 18 * s, my + 14 * s), 0, 180, True)
        mp.close()
        shape(c, mp, "#9E3A33", w=4 * s)
    elif mouth == "o":
        shape(c, oval_path(lx, my, 7 * s, 9 * s), "#9E3A33", w=4 * s)
    elif mouth == "frown":
        mp.arcTo(skia.Rect.MakeLTRB(lx - 13 * s, my - 2 * s, lx + 13 * s, my + 16 * s), 200, 140, True)
        c.drawPath(mp, ink_paint(4.5 * s))
    else:
        line(c, lx - 10 * s, my, lx + 10 * s, my - (3 * s if mouth == "think" else 0), 4.5 * s)
    c.drawCircle(lx - 40 * s, 24 * s, 9 * s, fill_paint("#E8957F", 0.45))
    c.drawCircle(lx + 40 * s, 24 * s, 9 * s, fill_paint("#E8957F", 0.45))
    c.restore()
    # 手臂（画在躯干前）
    hands = []
    for side, (a1, a2) in ((-1, arms[0]), (1, arms[1])):
        hx2, hy2 = limb(c, x + side * 70 * s, sh + 22 * s, a1, a2, 98 * s, 92 * s, 40 * s, lk["top"], s)
        shape(c, circle_path(hx2, hy2, 19 * s), SKIN, w=4 * s)
        hands.append((hx2, hy2))
        if hold:
            hold(c, hx2, hy2, side)
    if alpha < 1:
        c.restore()
    return hands[0], hands[1]


def ghost(c, x, y, s=1.0, k=0, alpha=1.0, fill=PAPER2):
    """背景路人：浅色填充 + 细墨线的简化剪影。"""
    if alpha <= 0:
        return
    hgt = (1.0 + 0.08 * math.sin(k * 2.3)) * s
    shape(c, rect_path(x - 22 * s, y - 150 * hgt, 18 * s, 150 * hgt, 8 * s), mix(fill, INK2, 0.18), alpha,
          3 * s, INK2)
    shape(c, rect_path(x + 4 * s, y - 150 * hgt, 18 * s, 150 * hgt, 8 * s), mix(fill, INK2, 0.18), alpha,
          3 * s, INK2)
    shape(c, rect_path(x - 52 * s, y - 330 * hgt, 104 * s, 190 * hgt, 30 * s), fill, alpha, 3.5 * s, INK2)
    shape(c, circle_path(x, y - 380 * hgt, 50 * s), fill, alpha, 3.5 * s, INK2)
    if k % 3 == 0:
        shape(c, oval_path(x, y - 412 * hgt, 46 * s, 22 * s), mix(fill, INK2, 0.35), alpha, 3 * s, INK2)


# ================================================================ 道具

def coupon(c, x, y, s=1.0, rot=0.0, alpha=1.0):
    if alpha <= 0:
        return
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    w, h, n = 190, 104, 6
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2)]
    for k in range(1, 2 * n):
        pts.append((w / 2 - (10 if k % 2 else 0), -h / 2 + h * k / (2 * n)))
    pts += [(w / 2, h / 2), (-w / 2, h / 2)]
    for k in range(1, 2 * n):
        pts.append((-w / 2 + (10 if k % 2 else 0), h / 2 - h * k / (2 * n)))
    shape(c, poly(pts), "#F8F1E2", alpha, 4.5)
    dp = ink_paint(3, INK2, alpha * 0.7, wobble=False)
    dp.setPathEffect(skia.DashPathEffect.Make([10, 8], 0))
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 + 22, -h / 2 + 16, w / 2 - 22, h / 2 - 16), dp)
    line(c, -w / 2 + 40, -12, w / 2 - 70, -12, 6, INK2, alpha * 0.5)
    line(c, -w / 2 + 40, 12, w / 2 - 100, 12, 6, INK2, alpha * 0.5)
    c.drawCircle(w / 2 - 44, 20, 20, ink_paint(4.5, RED, alpha))
    c.drawCircle(w / 2 - 44, 20, 11, fill_paint(RED, alpha * 0.8))
    c.restore()


def drink(c, x, y, s=1.0, alpha=1.0, glow=0.0):
    """透明杯饮料，(x, y) 为杯底中心。"""
    if alpha <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if glow > 0:
        gfx.circle(c, 0, -90, 150, GOLD, 0.35 * glow * alpha, blur=60)
    straw = poly([(10, -150), (34, -250), (54, -250)], close=False)
    c.drawPath(straw, ink_paint(22, INK, alpha))
    c.drawPath(straw, ink_paint(14, RED, alpha, wobble=False))
    cup = poly([(-56, -170), (56, -170), (42, 0), (-42, 0)])
    liquid = poly([(-50, -128), (50, -128), (42, 0), (-42, 0)])
    c.drawPath(liquid, fill_paint(AMBER, alpha * 0.92))
    c.drawPath(cup, fill_paint("#FFFFFF", alpha * 0.28))
    for k in range(4):
        c.drawCircle(-22 + k * 14, -18 - (k % 2) * 16, 6, fill_paint("#6B3F17", alpha * 0.85))
    c.drawPath(cup, ink_paint(5, INK, alpha))
    lid = skia.Path()
    lid.moveTo(-62, -168)
    lid.quadTo(0, -214, 62, -168)
    lid.close()
    shape(c, lid, "#FFFFFF", alpha * 0.85, 5)
    line(c, -30, -110, -24, -30, 7, "#FFFFFF", alpha * 0.6)
    c.drawCircle(0, -70, 22, ink_paint(3.5, INK2, alpha * 0.6))
    c.restore()


def clock(c, x, y, r, hours, alpha=1.0, sec=None):
    if alpha <= 0:
        return
    shape(c, circle_path(x, y, r + 8), mix(WOOD, INK, 0.25), alpha, 5)
    shape(c, circle_path(x, y, r), "#FBF6EA", alpha, 4)
    for k in range(12):
        a = math.radians(k * 30)
        l0 = r * (0.78 if k % 3 == 0 else 0.86)
        line(c, x + l0 * math.sin(a), y - l0 * math.cos(a), x + r * 0.94 * math.sin(a),
             y - r * 0.94 * math.cos(a), 5 if k % 3 == 0 else 3, INK, alpha)
    ha = math.radians((hours % 12) * 30)
    ma = math.radians((hours % 1) * 360)
    line(c, x, y, x + r * 0.5 * math.sin(ha), y - r * 0.5 * math.cos(ha), 8, INK, alpha)
    line(c, x, y, x + r * 0.76 * math.sin(ma), y - r * 0.76 * math.cos(ma), 5, INK, alpha)
    if sec is not None:
        sa = math.radians(sec * 6)
        line(c, x, y, x + r * 0.82 * math.sin(sa), y - r * 0.82 * math.cos(sa), 2.5, RED, alpha)
    c.drawCircle(x, y, 6, fill_paint(INK, alpha))


def calendar(c, x, y, cw=150, ch=52, cells=None, labels=True, alpha=1.0, size=1.0):
    """竖向 8 格日历；(x, y) 为顶部中心。cells[i] = dict(a=显隐, gray=变灰, glow=金光)。"""
    if alpha <= 0:
        return
    cells = cells or [{}] * 8
    c.save()
    c.translate(x, y)
    c.scale(size, size)
    shape(c, rect_path(-cw / 2 - 14, -30, cw + 28, 8 * ch + 44, 14), "#EFE3C9", alpha, 4.5)
    for k in (-1, 1):
        shape(c, rect_path(k * cw * 0.28 - 7, -48, 14, 34, 7), INK2, alpha, 0)
    for i in range(8):
        st = cells[i]
        a = st.get("a", 1.0) * alpha
        if a <= 0:
            continue
        sc = st.get("s", 1.0)
        cy = i * ch + ch / 2
        fill = mix("#FBF5E6", "#A8A096", st.get("gray", 0))
        c.save()
        c.translate(0, cy)
        c.scale(sc, sc)
        if st.get("glow", 0) > 0:
            gfx.rrect(c, 0, 0, cw + 10, ch + 6, 10, GOLD, st["glow"] * a * 0.55)
        shape(c, rect_path(-cw / 2 + 6, -ch / 2 + 4, cw - 12, ch - 8, 8), fill, a, 3.5)
        c.restore()
    if labels:
        text(c, "14:00", -cw / 2 - 30, 0, 26, "bold", INK2, alpha, "right")
        text(c, "15:00", -cw / 2 - 30, 4 * ch, 26, "bold", INK2, alpha, "right")
        text(c, "16:00", -cw / 2 - 30, 8 * ch, 26, "bold", INK2, alpha, "right")
    c.restore()


def phone(c, x, y, w, h, alpha=1.0, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    shape(c, rect_path(-w / 2, -h / 2, w, h, 46), "#2F2A27", alpha, 5)
    shape(c, rect_path(-w / 2 + 18, -h / 2 + 50, w - 36, h - 100, 18), "#FBF6EA", alpha, 0)
    c.drawRoundRect(skia.Rect.MakeXYWH(-40, -h / 2 + 20, 80, 12), 6, 6, fill_paint("#1A1716", alpha))
    c.restore()


def chat(c, x, y, s, mine, alpha, scale=1.0, size=40):
    """聊天气泡；mine=True 为小林（右侧金色），否则阿杰（左侧白色带头像）。"""
    if alpha <= 0 or scale <= 0:
        return
    w = gfx.text_width(s, size, "bold") + size * 1.3
    h = size * 2.0
    c.save()
    c.translate(x, y)
    c.scale(scale, scale)
    bx = -w if mine else 0
    shape(c, rect_path(bx, -h / 2, w, h, 26), GOLD if mine else "#FFFFFF", alpha, 4)
    gfx.draw_text(c, s, bx + w / 2, 0, size, "bold", INK, alpha)
    if not mine:
        shape(c, circle_path(-48, 0, 32), "#F1CFAE", alpha, 3.5)
        for k in range(6):
            a = math.radians(190 + k * 32)
            c.drawCircle(-48 + 27 * math.cos(a), -6 + 24 * math.sin(a), 12, fill_paint(BROWN, alpha))
    c.restore()


def sign(c, x, y, s, label, alpha=1.0, gray=0.0, size=40, post=True):
    """木牌路标；(x, y) 为牌面中心。"""
    if alpha <= 0:
        return
    w = gfx.text_width(label, size, "bold") + size * 1.2
    h = size * 1.8
    fill = mix(WOOD, "#BDB6AC", gray)
    if post:
        shape(c, rect_path(x - 7 * s, y, 14 * s, 90 * s, 5), mix(BROWN, "#9A938A", gray), alpha, 3.5)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shape(c, rect_path(-w / 2, -h / 2, w, h, 12), fill, alpha, 4.5)
    gfx.draw_text(c, label, 0, 0, size, "bold", mix(INK, "#6F6860", gray), alpha)
    c.restore()


def stamp(c, x, y, label, p, size=46, color=RED, rot=-12, r=None):
    """印章落下：p 从 0 到 1，由大缩回原尺寸。"""
    if p <= 0:
        return
    sc = lerp(1.8, 1.0, ease_out(p))
    a = clamp01(p * 3)
    r = r or (gfx.text_width(label, size, "serif") / 2 + size * 0.55)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(sc, sc)
    c.drawCircle(0, 0, r, ink_paint(8, color, a))
    c.drawCircle(0, 0, r - 13, ink_paint(3, color, a))
    gfx.draw_text(c, label, 0, 0, size, "serif", color, a)
    c.restore()


def cross(c, x, y, r, p, color=RED, w=16, alpha=1.0):
    line(c, x - r, y - r, x + r, y + r, w, color, alpha, ease_out(clamp01(p * 2)))
    line(c, x + r, y - r, x - r, y + r, w, color, alpha, ease_out(clamp01(p * 2 - 1)))


def tick(c, x, y, r, p, color=BLUE, w=16, alpha=1.0):
    path = poly([(x - r, y), (x - r * 0.25, y + r * 0.7), (x + r, y - r * 0.8)], close=False)
    gfx.stroke_path(c, path, color, w, alpha, ease_out(p))


def sofa(c, x, y, s=1.0, alpha=1.0, sleeper=True, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shape(c, rect_path(-120, -70, 240, 70, 24), "#B5564A", alpha, 4.5)
    shape(c, rect_path(-140, -40, 40, 70, 16), "#A44B40", alpha, 4.5)
    shape(c, rect_path(100, -40, 40, 70, 16), "#A44B40", alpha, 4.5)
    shape(c, rect_path(-100, -20, 200, 48, 14), "#C76A5B", alpha, 4.5)
    if sleeper:
        shape(c, circle_path(-62, -38, 26), SKIN, alpha, 4)
        shape(c, oval_path(-70, -56, 24, 12), HAIR, alpha, 0)
        shape(c, rect_path(-40, -36, 120, 30, 14), MUSTARD, alpha, 4)
        for k in range(2):
            ph = (t * 0.6 + k * 0.5) % 1
            text(c, "z", -40 + k * 30 + ph * 30, -90 - ph * 60 - k * 16, 34 + k * 8, "serif", INK2,
                 alpha * (1 - ph), halo=False)
    c.restore()


def desk(c, x, y, s=1.0, alpha=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shape(c, rect_path(-130, -20, 260, 26, 8), mix(WOOD, BROWN, 0.35), alpha, 4.5)
    line(c, -110, 6, -110, 80, 8, INK, alpha)
    line(c, 110, 6, 110, 80, 8, INK, alpha)
    shape(c, poly([(-4, -30), (-96, -44), (-90, -86), (-4, -72)]), "#FBF6EA", alpha, 4)
    shape(c, poly([(4, -30), (96, -44), (90, -86), (4, -72)]), "#FBF6EA", alpha, 4)
    for k in range(3):
        line(c, -80, -54 - k * 8, -20, -46 - k * 8, 2.5, INK2, alpha * 0.6)
        line(c, 20, -46 - k * 8, 80, -54 - k * 8, 2.5, INK2, alpha * 0.6)
    shape(c, poly([(40, -30), (50, -30), (50, 4), (45, -4), (40, 4)]), RED, alpha, 0)
    c.restore()


def tree(c, x, y, s=1.0, alpha=1.0):
    shape(c, rect_path(x - 12 * s, y - 120 * s, 24 * s, 120 * s, 6), BROWN, alpha, 4)
    for dx, dy, r in ((0, -170, 70), (-50, -140, 50), (50, -140, 52), (0, -220, 50)):
        shape(c, circle_path(x + dx * s, y + dy * s, r * s), "#7E9A63", alpha, 4)


def bench(c, x, y, s=1.0, alpha=1.0):
    shape(c, rect_path(x - 110 * s, y - 60 * s, 220 * s, 18 * s, 6), mix(WOOD, BROWN, 0.4), alpha, 4)
    shape(c, rect_path(x - 110 * s, y - 100 * s, 220 * s, 16 * s, 6), mix(WOOD, BROWN, 0.4), alpha, 4)
    for k in (-90, 90):
        line(c, x + k * s, y - 42 * s, x + k * s, y, 7 * s, INK, alpha)


def walkers(c, x, y, s=1.0, alpha=1.0):
    """两个人并肩散步的小图标。"""
    for dx, top, hair in ((-30, MUSTARD, HAIR), (30, GREEN, BROWN)):
        shape(c, rect_path(x + (dx - 22) * s, y - 70 * s, 44 * s, 60 * s, 16 * s), top, alpha, 3.5 * s)
        shape(c, circle_path(x + dx * s, y - 92 * s, 22 * s), SKIN, alpha, 3.5 * s)
        shape(c, oval_path(x + dx * s, y - 106 * s, 20 * s, 10 * s), hair, alpha, 0)
        line(c, x + (dx - 10) * s, y - 10 * s, x + (dx - 16) * s, y + 20 * s, 7 * s, INK, alpha)
        line(c, x + (dx + 10) * s, y - 10 * s, x + (dx + 16) * s, y + 20 * s, 7 * s, INK, alpha)


def queue_icon(c, x, y, s=1.0, alpha=1.0):
    for k in range(3):
        shape(c, rect_path(x + (k * 34 - 50) * s, y - 56 * s, 30 * s, 50 * s, 12 * s), PAPER3, alpha, 3 * s)
        shape(c, circle_path(x + (k * 34 - 35) * s, y - 72 * s, 15 * s), PAPER3, alpha, 3 * s)


def shop(c, x, y, w=620, h=560, alpha=1.0, t=0.0, flags=False):
    """奶茶店门面；(x, y) 为地面左端。"""
    shape(c, rect_path(x, y - h, w, h, 6), "#EADBC0", alpha, 5)
    stripes = 8
    for k in range(stripes):
        sx = x - 20 + k * (w + 40) / stripes
        sw = (w + 40) / stripes
        p = skia.Path()
        p.moveTo(sx, y - h + 40)
        p.lineTo(sx + sw, y - h + 40)
        p.lineTo(sx + sw, y - h + 130)
        p.quadTo(sx + sw / 2, y - h + 170, sx, y - h + 130)
        p.close()
        shape(c, p, RED if k % 2 == 0 else "#F6EEDD", alpha, 4)
    shape(c, rect_path(x + 40, y - h + 200, w * 0.45, 210, 8), "#CFE0E4", alpha, 5)
    line(c, x + 40 + w * 0.22, y - h + 200, x + 40 + w * 0.22, y - h + 410, 4, INK, alpha)
    shape(c, rect_path(x + w * 0.62, y - h + 220, w * 0.28, h - 220, 8), mix(WOOD, BROWN, 0.45), alpha, 5)
    c.drawCircle(x + w * 0.66, y - h * 0.35, 7, fill_paint(GOLD, alpha))
    drink(c, x + 40 + w * 0.11, y - h + 390, 0.55, alpha * 0.9)
    drink(c, x + 40 + w * 0.34, y - h + 390, 0.55, alpha * 0.9)
    if flags:
        rope = skia.Path()
        rope.moveTo(x - 60, y - h + 10)
        rope.quadTo(x + w / 2, y - h + 90, x + w + 60, y - h + 10)
        c.drawPath(rope, ink_paint(3, INK, alpha))
        pm = skia.PathMeasure(rope, False)
        L = pm.getLength()
        for k in range(11):
            pos, _ = pm.getPosTan(L * (k + 0.5) / 11)
            px, py = pos.x(), pos.y()
            sway = math.sin(t * 2.4 + k) * 6
            colr = (RED, GOLD, BLUE)[k % 3]
            shape(c, poly([(px - 22, py), (px + 22, py), (px + sway, py + 52)]), colr, alpha, 3.5)


def hourglass(c, x, y, s, p, alpha=1.0):
    """沙漏；p 为上半部流走的比例。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shape(c, rect_path(-120, -200, 240, 26, 8), mix(WOOD, BROWN, 0.4), alpha, 4.5)
    shape(c, rect_path(-120, 174, 240, 26, 8), mix(WOOD, BROWN, 0.4), alpha, 4.5)
    glass = skia.Path()
    glass.moveTo(-90, -174)
    glass.lineTo(90, -174)
    glass.cubicTo(90, -60, 14, -30, 14, 0)
    glass.cubicTo(14, 30, 90, 60, 90, 174)
    glass.lineTo(-90, 174)
    glass.cubicTo(-90, 60, -14, 30, -14, 0)
    glass.cubicTo(-14, -30, -90, -60, -90, -174)
    glass.close()
    c.drawPath(glass, fill_paint("#FFFFFF", alpha * 0.35))
    c.save()
    c.clipPath(glass, doAntiAlias=True)
    top = lerp(-150, -10, p)
    c.drawRect(skia.Rect.MakeLTRB(-100, top, 100, -2), fill_paint(GOLD, alpha))
    pile = lerp(0, 120, p)
    if pile > 0:
        mound = skia.Path()
        mound.moveTo(-100, 174)
        mound.lineTo(-100, 174 - pile * 0.6)
        mound.quadTo(0, 174 - pile * 1.5, 100, 174 - pile * 0.6)
        mound.lineTo(100, 174)
        mound.close()
        c.drawPath(mound, fill_paint(GOLD, alpha))
    if 0 < p < 1:
        c.drawRect(skia.Rect.MakeLTRB(-3, 0, 3, 174 - pile), fill_paint(GOLD, alpha))
    c.restore()
    c.drawPath(glass, ink_paint(5, INK, alpha))
    c.restore()


def receipt(c, x, y, w, h, alpha=1.0):
    """顶部平直、底部锯齿的收据纸；(x, y) 为顶部中心。"""
    pts = [(x - w / 2, y), (x + w / 2, y), (x + w / 2, y + h)]
    n = int(w // 30)
    for k in range(1, 2 * n):
        pts.append((x + w / 2 - w * k / (2 * n), y + h - (14 if k % 2 else 0)))
    pts.append((x - w / 2, y + h))
    shape(c, poly(pts), "#FBF6EA", alpha, 4.5)


def time_chip(c, s, alpha=1.0, x=150, y=600):
    if alpha <= 0:
        return
    w = gfx.text_width(s, 40, "bold") + 52
    shape(c, rect_path(x - w / 2, y - 34, w, 68, 34), INK, alpha, 0)
    gfx.draw_text(c, s, x, y, 40, "bold", PAPER, alpha)


def rewind_icon(c, x, y, size, alpha=1.0, color=INK):
    for k in (0, 1):
        ox = x - k * size * 0.62
        c.drawPath(poly([(ox, y - size / 2), (ox, y + size / 2), (ox - size * 0.62, y)]), fill_paint(color, alpha))


def scratches(c, frame, amount):
    """老胶片划痕与闪烁颗粒。"""
    if amount <= 0:
        return
    rng = np.random.default_rng(frame * 31 + 7)
    for _ in range(int(rng.integers(2, 5))):
        x = float(rng.uniform(40, W - 40))
        c.drawLine(x, 0, x + float(rng.uniform(-30, 30)), H, ink_paint(float(rng.uniform(1.5, 3.5)), INK,
                                                                         0.25 * amount, wobble=False))
    for _ in range(14):
        c.drawCircle(float(rng.uniform(0, W)), float(rng.uniform(0, H)), float(rng.uniform(2, 6)),
                     fill_paint(INK, 0.3 * amount))


def headline(c, s, y, size, t, start, color=INK, alpha=1.0, name="serif", style="rise"):
    """标题区逐字入场的大字，带纸色描边。"""
    if t < start or alpha <= 0:
        return
    gfx.draw_kinetic(c, s, W / 2, y, size, t, start, name, style, 0.035, 0.35, color, RED, alpha,
                     stroke=(PAPER, size * 0.2))


def blink_at(t, seed=0.0):
    return ((t + seed) % 3.7) < 0.12


# ================================================================ 口播与字幕

NARRATION = [
    ("排两小时队，免费领一杯二十块的饮料。你觉得，【赚了吗】？", 0.15, 4.7),
    ("小林就这么想。周六新店开业，前一百名免费。一分钱没花，到手二十块，【稳赚】。", 0.1, 6.7),
    ("队伍挪得很慢。手机一震，是好久没见的老朋友阿杰：“下午出来走走？”小林回：“排队呢，下次吧。”", 0.1, 8.7),
    ("两小时后，饮料到手。他拍照发了条朋友圈：“【零成本】的快乐。”", 0.1, 5.6),
    ("等一下。我们把这个下午倒回去看看。", 0.8, 4.4),
    ("这两小时，小林还有别的路：在家睡个午觉，把那本书看完，或者赴阿杰的约。可时间【只有一份】，只能选一条。", 0.1, 9.2),
    ("对他来说，最想做、也【真做得到】的，是和老朋友散散步。那么这杯饮料真正的价钱，就是【那个下午的相处】。", 0.1, 9.2),
    ("价签上写着免费，账单记在【你的时间】里。", 0.6, 4.2),
    ("经济学管这叫【机会成本】：做选择时，你放弃的那个【最好的】可行选项。时间有限，用在这儿，就用不了在别处。", 0.1, 9.2),
    ("注意，只算【最好的那一个】，不把午觉、看书、散步全加起来。", 0.1, 5.8),
    ("也别拿月薪去折算这两小时，除非你【真能】用它加班挣钱。休息和陪伴，不必换成钱才算数。", 0.1, 7.3),
    ("所以，值不值？要是排队本身挺好玩，阿杰也没空，这就是个不错的下午。", 0.1, 6.8),
    ("要是排到一半才收到邀约，前面那一小时已经【回不来】，别让它绑住你；该比的，是【剩下的时间】怎么用。", 0.2, 8.6),
    ("下次遇到“免费”，先问自己一句：这段时间，我真正能做、也【最想做】的另一件事，是什么？", 0.8, 7.2),
]
PAUSE, STOP, QUIET = "，、：；", "。？！", "“”"
MAX_CAP = 15


def _weights(chars):
    return [0.0 if ch in QUIET else 0.7 if ch in PAUSE else 1.2 if ch in STOP else 1.0 for ch, _ in chars]


def _chars(marked):
    out, hi = [], False
    for ch in marked:
        if ch in "【】":
            hi = ch == "【"
        else:
            out.append((ch, hi))
    return out


def _markup(chars):
    s, hi = "", False
    for ch, h in chars:
        if h != hi:
            s += "【" if h else "】"
            hi = h
        s += ch
    return s + ("】" if hi else "")


@functools.lru_cache(maxsize=None)
def captions(i):
    """把第 i 镜口播切成字幕条，返回 [(本镜内开始时间, 带标记文本)]，时间按字数加标点停顿分配。"""
    marked, a, b = NARRATION[i]
    chars = _chars(marked)
    w = _weights(chars)
    total = sum(w)
    clauses, cur, quoted = [], [], False
    for k, (ch, h) in enumerate(chars):
        if ch in "，" and not cur:
            continue
        cur.append(k)
        quoted = (quoted or ch == "“") and ch != "”"
        nxt = chars[k + 1][0] if k + 1 < len(chars) else ""
        if (ch in PAUSE + STOP and not quoted and nxt != "”") or (ch == "”" and nxt in "，。"):
            clauses.append(cur)
            cur = []
        elif ch == "”":
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    merged = []
    for cl in clauses:
        if merged:
            prev = merged[-1]
            plen = len([k for k in prev if chars[k][0] not in QUIET])
            clen = len([k for k in cl if chars[k][0] not in QUIET])
            if chars[prev[-1]][0] not in STOP + "”" and plen + clen <= MAX_CAP and plen < 7:
                prev.extend(cl)
                continue
        merged.append(list(cl))
    out = []
    for cl in merged:
        t0 = a + (b - a) * sum(w[:cl[0]]) / total
        seg = [chars[k] for k in cl]
        while seg and seg[-1][0] in "，。；：、":
            seg.pop()
        seg = [q for j, q in enumerate(seg) if not (q[0] in "。，" and j + 1 < len(seg) and seg[j + 1][0] == "”")]
        while seg and seg[0][0] in "，。；：、":
            seg.pop(0)
        s = _markup(seg)
        if s.startswith("“") and s.count("“") > s.count("”"):
            s += "”"
        if s.endswith("”") and s.count("”") > s.count("“"):
            s = "“" + s
        out.append((t0, s))
    return out


@functools.lru_cache(maxsize=None)
def cue(i, kw, n=0):
    """第 i 镜口播中关键词 kw（第 n 次出现）开始被念到的本镜内时间。"""
    marked, a, b = NARRATION[i]
    chars = _chars(marked)
    plain = "".join(ch for ch, _ in chars)
    idx = -1
    for _ in range(n + 1):
        idx = plain.index(kw, idx + 1)
    w = _weights(chars)
    return a + (b - a) * sum(w[:idx]) / sum(w)


# ================================================================ 分镜

def s1(c, t):
    """镜 1：递券、回头看长队，挂钟开始走。"""
    push = ease_in_out(prog(t, 2.8, 2.2))
    with cam(c, 1 + 0.12 * push, 820, 700, -40 * push, 30 * push):
        shop(c, 520, 1330, 620, 640, t=t)
        clock(c, 820, 700, 64, 14 + t / 3600 * 60, sec=int(t) * 6 % 60 * 1.0 + int(t))
        for k in range(6):
            ghost(c, 150 - k * 70, 1250 - k * 28, 0.62 - k * 0.04, k, 0.9)
        p_give = ease_out(prog(t, 0.2, 0.9))
        turn = ease_in_out(prog(t, 2.0, 0.6)) - ease_in_out(prog(t, 3.8, 0.5))
        got = t > 1.25

        def clerk_hold(cc, hx, hy, side):
            if side == -1 and not got:
                coupon(cc, hx - 50, hy - 10, 0.75, -8)

        person(c, 730, 1330, 0.95, "clerk", arms=((lerp(-10, -70, p_give), lerp(-6, -85, p_give)), (10, 4)),
               look=-0.6, mouth="smile", blink=blink_at(t, 1), hold=clerk_hold)

        def lin_hold(cc, hx, hy, side):
            if side == 1 and got:
                coupon(cc, hx + 30, hy - 30, 0.75, 10 + 4 * math.sin(t * 3))

        reach = ease_out(prog(t, 0.6, 0.6))
        person(c, 390, 1330, 1.0, "lin",
               arms=((-10, -5), (lerp(10, 60, reach) - (20 if got else 0) * prog(t, 1.4, 0.5),
                                 lerp(4, 95, reach) - (40 if got else 0) * prog(t, 1.4, 0.5))),
               look=lerp(0.5, -1.0, turn), tilt=-0.4 * turn, mouth="smile" if t < 2 else "think",
               blink=blink_at(t, 0.4), hold=lin_hold)
    title_scale = 1 + 0.03 * math.sin(min(t, 1.0) * math.pi)
    a = 1 - prog(t, 4.6, 0.4)
    with cam(c, title_scale, W / 2, TITLE_Y):
        text(c, "排两小时队领免费饮料", W / 2, TITLE_Y - 62, 78, "serif", INK, a)
        text(c, "真的赚了吗？", W / 2, TITLE_Y + 62, 104, "serif", RED, a)


def s2(c, t):
    """镜 2：开业彩旗，举牌，小林看券，头顶账本算账并打勾。"""
    with cam(c, 1.0, W / 2, 1000, -20 * ease_in_out(prog(t, 0, 7))):
        shop(c, 200, 1340, 700, 660, t=t, flags=True)
        for k, (bx, colr) in enumerate(((150, RED), (190, GOLD), (960, BLUE), (920, RED))):
            by = 700 + 14 * math.sin(t * 1.6 + k)
            line(c, bx, by + 50, bx + (10 if k < 2 else -10), 1100, 2.5, INK2)
            shape(c, oval_path(bx, by, 40, 50), colr, 1, 4)
        # 店员举牌
        def sign_hold(cc, hx, hy, side):
            if side == 1:
                line(cc, hx, hy + 30, hx, hy - 210, 8, BROWN)
                shape(cc, rect_path(hx - 130, hy - 330, 260, 130, 12), "#FBF6EA", 1, 5)
                gfx.draw_text(cc, "前100名免费", hx, hy - 265, 40, "bold", RED, prog(t, 0.6, 0.3))

        person(c, 820, 1340, 0.9, "clerk", arms=((-8, -4), (150, 175)), look=-0.3, blink=blink_at(t, 2),
               hold=sign_hold)

        def lin_hold(cc, hx, hy, side):
            if side == 1:
                coupon(cc, hx - 30, hy - 40, 0.8, -14)

        person(c, 420, 1340, 1.05, "lin", arms=((-10, -5), (40, -40)), look=0.2, tilt=0.3,
               mouth="big" if t > cue(1, "稳赚") else "smile", blink=blink_at(t, 0.8), hold=lin_hold)
        # 账本
        pb = ease_out_back(prog(t, cue(1, "一分钱") - 0.4, 0.45))
        close = ease_in_out(prog(t, 6.6, 0.4))
        if pb > 0:
            bx, by = 420, 760
            c.save()
            c.translate(bx, by + 10 * math.sin(t * 2))
            c.scale(pb * (1 - 0.0 * close), pb)
            wl = 170 * (1 - close)
            shape(c, poly([(0, -110), (-wl - 20, -126), (-wl - 20, 110), (0, 126)]), "#FBF6EA", 1, 5)
            shape(c, poly([(0, -110), (wl + 20, -126), (wl + 20, 110), (0, 126)]), "#FBF6EA", 1, 5)
            if close < 0.3:
                a1 = prog(t, cue(1, "一分钱"), 0.3)
                a2 = prog(t, cue(1, "到手"), 0.3)
                gfx.draw_text(c, "花费", -95, -40, 38, "bold", INK2, a1)
                gfx.draw_text(c, "0元", -95, 30, 56, "serif", INK, a1)
                gfx.draw_text(c, "到手", 95, -40, 38, "bold", INK2, a2)
                gfx.draw_text(c, "20元", 95, 30, 56, "serif", RED, a2)
            c.restore()
            if close < 0.3:
                tick(c, 640, 640, 50, prog(t, cue(1, "稳赚"), 0.4), RED, 16)


def queue_scene(c, t, pan, lin_step=0.0, look=0.0, mouth="flat", gray_people=False, back=0.0):
    """镜 3/5/13 共用：侧面长队；pan 为横向平移量，back 为倒带位移。"""
    with cam(c, 1.0, W / 2, H / 2, -pan):
        for k in range(10):
            x = -250 + k * 190 + back * (k % 3 + 1) * 10
            if k == 5:
                continue
            ghost(c, x, 1330 - (k % 2) * 16, 0.86, k, 1.0)
        person(c, -250 + 5 * 190 + 40 * lin_step, 1330, 1.0, "lin", arms=((-10, -5), (40, -60)),
               look=look, mouth=mouth, blink=blink_at(t, 1.5),
               hold=lambda cc, hx, hy, side: side == 1 and phone(cc, hx - 10, hy - 40, 60, 110, 1, -10))
        line(c, -600, 1350, 2400, 1350, 4, INK2, 0.6)


def s3(c, t):
    """镜 3：队伍慢慢挪，手机来消息，小林回绝。"""
    step = ease_in_out(prog(t, 0.6, 0.8))
    zoom = ease_out(prog(t, 1.6, 0.5))
    queue_scene(c, t, 60 * t, step, look=0.3 * zoom, mouth="flat")
    if zoom > 0:
        c.drawPaint(fill_paint(PAPER, 0.55 * zoom))
        buzz = math.sin(t * 60) * 6 * (1 - prog(t, 1.8, 0.8))
        with cam(c, lerp(0.6, 1.0, zoom), W / 2, 960, buzz, (1 - zoom) * 200):
            phone(c, W / 2, 960, 520, 860)
            for k in range(3):
                a = (1 - prog(t, 1.8 + k * 0.1, 0.6)) * (t > 1.6)
                for sgn in (-1, 1):
                    line(c, W / 2 + sgn * (290 + k * 24), 760 + k * 20, W / 2 + sgn * (300 + k * 24),
                         820 + k * 20, 5, INK, a)
            gfx.draw_text(c, "阿杰", W / 2, 600, 34, "bold", INK2, 1)
            p1 = ease_out_back(prog(t, cue(2, "下午") - 0.2, 0.35))
            chat(c, W / 2 - 160, 760, "下午出来走走？", False, clamp01(p1 * 2), p1, 42)
            dots_a = prog(t, cue(2, "小林回") - 0.3, 0.2) * (1 - prog(t, cue(2, "排队呢") - 0.1, 0.1))
            for k in range(3):
                gfx.circle(c, W / 2 + 120 + k * 30, 920 + 6 * math.sin(t * 10 + k), 9, INK2, dots_a)
            p2 = ease_out_back(prog(t, cue(2, "排队呢") - 0.1, 0.35))
            chat(c, W / 2 + 200, 920, "排队呢，下次吧", True, clamp01(p2 * 2), p2, 42)
    ff = prog(t, 8.4, 0.6)
    hh = lerp(14 + 5 / 60, 16, ease_in_out(ff))
    time_chip(c, f"{int(hh):02d}:{int(round((hh % 1) * 60)) % 60:02d}")


def s4(c, t, frozen=False):
    """镜 4：举杯自拍，快门闪光，朋友圈动态滑入。"""
    shake = 0 if frozen else 1
    with cam(c, 1.0, W / 2, 1000, 5 * math.sin(t * 2.1) * shake, 4 * math.sin(t * 1.7) * shake):
        gfx.circle(c, 540, 820, 380, GOLD, 0.35, blur=120)
        for k in range(12):
            a = math.radians(k * 30 + t * 6)
            line(c, 540 + 260 * math.cos(a), 820 + 260 * math.sin(a), 540 + 420 * math.cos(a),
                 820 + 420 * math.sin(a), 6, GOLD, 0.25)

        def hold(cc, hx, hy, side):
            if side == 1:
                drink(cc, hx, hy + 30, 1.0, glow=0.6)
            else:
                phone(cc, hx, hy - 20, 110, 200, 1, -14)

        person(c, 540, 1650, 1.55, "lin", arms=((-140, -170), (150, 172)), look=-0.1, tilt=0.4,
               mouth="big", blink=blink_at(t, 2.2), hold=hold)
    time_chip(c, "16:00")
    if not frozen:
        flash = prog(t, cue(3, "他拍照"), 0.05) * (1 - prog(t, cue(3, "他拍照") + 0.05, 0.3))
        if flash > 0:
            c.drawPaint(fill_paint("#FFFFFF", 0.8 * flash))
    pc = ease_out(prog(t, cue(3, "零成本") - 0.4, 0.45))
    if pc > 0:
        y = lerp(1700, 1180, pc)
        shape(c, rect_path(150, y - 110, 780, 220, 26), "#FFFFFF", 0.97, 4.5)
        shape(c, circle_path(225, y - 40, 42), SKIN, 1, 4)
        shape(c, oval_path(225, y - 66, 38, 18), HAIR, 1, 0)
        gfx.draw_text(c, "小林", 290, y - 62, 32, "bold", BLUE, 1, "left")
        gfx.draw_text(c, "零成本的快乐", 290, y - 10, 46, "bold", INK, 1, "left")
        shape(c, rect_path(760, y - 80, 130, 160, 14), "#F2E3C4", 1, 3.5)
        drink(c, 825, y + 70, 0.62)


def s5(c, t):
    """镜 5：定格褪色 → 倒带回 14:00 → 镜头上升。"""
    if t < 1.4:
        g = ease_out(prog(t, 0.0, 0.35))
        layer(c, 1.0, g)
        s4(c, 6.0, frozen=True)
        c.restore()
        scratches(c, int(t * 30) + 2000, g)
        return
    rp = ease_in_out(prog(t, 1.6, 2.8))
    rise = ease_in_out(prog(t, 4.6, 0.9))
    jitter = math.sin(t * 90) * 4 * (0 < rp < 1)
    layer(c, 1.0, 0.85)
    with cam(c, 1 - 0.25 * rise, W / 2, 1000, jitter, -300 * rise):
        queue_scene(c, t, 0, 0, look=0, mouth="o", back=-3 * rp)
        clock(c, 830, 760, 90, 16 - 2 * rp)
    c.restore()
    scratches(c, int(t * 30) + 3000, 1 - rise)
    a = prog(t, 1.5, 0.3) * (1 - prog(t, 4.8, 0.4))
    rewind_icon(c, 330, TITLE_Y, 70, a, RED)
    text(c, f"倒回 {int(lerp(16, 14, rp) // 1):02d}:{int(round((lerp(16, 14, rp) % 1) * 60)) % 60:02d}",
         600, TITLE_Y, 84, "serif", INK, a)


# ---------------------------------------------------------------- 地图（镜 6、7 共用）

JUNCTION = (540, 1150)
DEST = {"nap": (230, 700), "book": (560, 610), "park": (850, 720)}


def _road(dest):
    x0, y0 = JUNCTION
    x1, y1 = DEST[dest]
    p = skia.Path()
    p.moveTo(x0, y0 - 40)
    p.cubicTo(x0 + (x1 - x0) * 0.1, y0 - 220, x1 + (x0 - x1) * 0.2, y1 + 260, x1, y1 + 110)
    return p


def map_scene(c, t6, t7):
    """t6 为镜 6 内时间，t7 为镜 7 内时间（未开始时为负）。"""
    reveal = {"nap": prog(t6, cue(5, "在家") - 0.2, 0.7), "book": prog(t6, cue(5, "把那本书") - 0.2, 0.7),
              "park": prog(t6, cue(5, "或者") - 0.1, 0.7)}
    fade = ease_in_out(prog(t7, cue(6, "最想做") - 0.2, 1.2)) if t7 > -1 else 0
    light = ease_out(prog(t7, cue(6, "是和老朋友") - 0.2, 0.8)) if t7 > -1 else 0
    push = ease_in_out(prog(t6, 7.6, 1.8)) if t7 < 0 else 1
    with cam(c, 1 + 0.06 * push, 760, 900, 0, 0):
        # 地面
        shape(c, rect_path(40, 470, 1000, 960, 40), "#E7DCC3", 1, 4.5)
        for k in range(16):
            gx, gy = 80 + (k * 137) % 920, 520 + (k * 211) % 880
            line(c, gx, gy, gx + 10, gy - 16, 3, "#8FA478", 0.6)
            line(c, gx + 12, gy, gx + 18, gy - 12, 3, "#8FA478", 0.6)
        if light > 0:
            gfx.stroke_path(c, _road("park"), GOLD, 110, 0.45 * light, 1.0, glow=(GOLD, 30))
        for d in ("nap", "book", "park"):
            g = fade if d != "park" else 0
            a = 1 - 0.55 * g
            road = _road(d)
            col_road = mix(ROAD, "#C9C3B9", g)
            gfx.stroke_path(c, road, INK, 82, a, reveal[d])
            gfx.stroke_path(c, road, col_road if d != "park" else mix(ROAD, "#F2D48A", light), 70, a, reveal[d])
            dp = ink_paint(4, INK2, 0.5 * a, wobble=False)
            dp.setPathEffect(skia.DashPathEffect.Make([18, 18], 0))
            if reveal[d] >= 1:
                c.drawPath(road, dp)
        # 目的地小岛
        for d in ("nap", "book", "park"):
            g = fade if d != "park" else 0
            pa = ease_out_back(prog(reveal[d], 0.6, 0.4) if reveal[d] < 1 else 1)
            if pa <= 0:
                continue
            x, y = DEST[d]
            layer(c, 1 - 0.6 * g, g)
            with cam(c, pa, x, y):
                shape(c, oval_path(x, y + 40, 150, 110), "#EFE6D1", 1, 4.5)
                if d == "nap":
                    sofa(c, x, y + 50, 0.85, t=t6)
                elif d == "book":
                    desk(c, x, y + 40, 0.85)
                else:
                    tree(c, x + 90, y + 70, 0.7)
                    bench(c, x - 30, y + 90, 0.8)
                    wave = math.sin(max(t7, 0) * 6) * 25 * light
                    person(c, x - 40, y + 110, 0.42, "jie", arms=((-8, -4), (150 + wave, 170 + wave)),
                           mouth="big" if light > 0.5 else "smile", blink=blink_at(t6, 0.3))
            c.restore()
        if light > 0:
            gfx.light_rays(c, DEST["park"][0], DEST["park"][1] + 40, t7, GOLD, 0.22 * light, 12, 260)
        # 路牌
        labels = {"nap": ("午睡", (300, 960)), "book": ("看完那本书", (560, 860)), "park": ("赴阿杰的约", (780, 980))}
        for d, (lab, (x, y)) in labels.items():
            g = fade if d != "park" else 0
            pa = ease_out_back(prog(reveal[d], 0.5, 0.5))
            if pa > 0:
                with cam(c, pa * (1 - 0.25 * g), x, y):
                    sign(c, x, y, 1.0, lab, 1 - 0.4 * g, g, 38)
        # 小林
        person(c, JUNCTION[0], JUNCTION[1] + 120, 0.5, "lin", arms=((-10, -5), (10, 5)),
               look=lerp(0, 0.8, light), mouth="smile" if light > 0.5 else "think", blink=blink_at(t6, 0.9))
        # 前景：券与日历
        coupon(c, 230, 1330, 1.05, -10)
        n_gone = 0.0
        if t7 > -1:
            n_gone = clamp01((t7 - cue(6, "就是") - 0.3) / 2.0) * 8
        cells = []
        for i in range(8):
            k = clamp01(n_gone - i)
            cells.append(dict(a=1 - ease_out(k), s=1 - 0.6 * ease_out(k)))
        calendar(c, 900, 1060, 120, 40, cells, labels=False)


def s6(c, t):
    map_scene(c, t, -10)
    a = prog(t, cue(5, "可时间") - 0.1, 0.3)
    if a > 0:
        headline(c, "时间【只有一份】", TITLE_Y - 30, 92, t, cue(5, "可时间") - 0.1)
        text(c, "14:00–16:00 · 8格 × 15分钟", W / 2, TITLE_Y + 80, 40, "bold", INK2, prog(t, cue(5, "可时间") + 0.3, 0.4))


def s7(c, t):
    map_scene(c, 9.5 + t, t)
    st = cue(6, "是和老朋友") + 0.2
    if t >= st:
        a = prog(t, st, 0.3)
        text(c, "最好的可行替代", W / 2, TITLE_Y - 50, 60, "serifb", INK2, a)
        gfx.draw_text(c, "和老朋友散步", W / 2, TITLE_Y + 50, 96, "serif", INK, a, stroke=(GOLD, 14),
                      glow=(GOLD, 20))


def s8(c, t):
    """镜 8：饮料价签特写 → 横移到日历，红笔圈住。"""
    pan = ease_in_out(prog(t, cue(7, "账单") - 0.5, 1.0))
    with cam(c, 1.0, W / 2, 1000, -880 * pan):
        shape(c, rect_path(-200, 1230, 2400, 300, 0), mix(WOOD, BROWN, 0.25), 1, 5)
        line(c, -200, 1260, 2200, 1260, 3, INK2, 0.5)
        gfx.circle(c, 540, 900, 300, GOLD, 0.3, blur=100)
        drink(c, 540, 1240, 2.3)
        line(c, 640, 860, 760, 960, 4, INK)
        c.save()
        c.translate(780, 1000)
        c.rotate(8 + 3 * math.sin(t * 2))
        shape(c, poly([(-70, -40), (60, -40), (90, 0), (60, 40), (-70, 40)]), "#FBF6EA", 1, 4.5)
        c.drawCircle(64, 0, 8, ink_paint(3))
        gfx.draw_text(c, "免费", -8, 0, 46, "serif", RED, prog(t, cue(7, "免费"), 0.3))
        c.restore()
        calendar(c, 1420, 760, 230, 56, labels=True, size=1.0)
        ring = skia.Path()
        ring.addOval(skia.Rect.MakeLTRB(1420 - 230, 700, 1420 + 230, 1300))
        gfx.stroke_path(c, ring, RED, 12, 1, ease_out(prog(t, cue(7, "记在") - 0.1, 0.8)))
    a = prog(t, cue(7, "价签"), 0.3) * (1 - pan)
    text(c, "价签：免费", W / 2, TITLE_Y, 84, "serif", INK, a)
    a2 = prog(t, cue(7, "账单") + 0.2, 0.3)
    if a2 > 0:
        text(c, "账单：【你的时间】", W / 2, TITLE_Y - 40, 84, "serif", INK, a2)
        text(c, "14:00–16:00", W / 2, TITLE_Y + 70, 60, "serifb", RED, a2)


def s9(c, t):
    """镜 9：名称卡 + 沙漏把时间倒给"排队"，"散步"那杯空着。"""
    st = cue(8, "机会成本") - 0.1
    headline(c, "机会成本", 300, 132, t, st, INK)
    if t > st + 0.3:
        gfx.draw_text(c, "Opportunity Cost", W / 2, 410, 44, "serifb", INK2, prog(t, st + 0.3, 0.4))
    d = prog(t, cue(8, "做选择时") - 0.1, 0.4)
    if d > 0:
        text(c, "做选择时，放弃的【最好可行选项】的价值", W / 2, 500, 46, "bold", INK, d)
    flow = ease_in_out(prog(t, 1.0, 7.5))
    hourglass(c, W / 2, 860, 0.9, flow)
    # 两只杯子
    for k, (x, lab) in enumerate(((330, "排队"), (750, "散步"))):
        dim = 0.45 * ease_out(prog(t, cue(8, "就用不了") - 0.2, 0.6)) if k == 1 else 0
        cup = poly([(x - 110, 1080), (x + 110, 1080), (x + 86, 1300), (x - 86, 1300)])
        if k == 0:
            c.save()
            c.clipPath(cup, doAntiAlias=True)
            lvl = lerp(1300, 1140, flow)
            c.drawRect(skia.Rect.MakeLTRB(x - 120, lvl, x + 120, 1310), fill_paint(GOLD))
            c.restore()
        shape(c, cup, None, 1 - dim, 5)
        if k == 0:
            queue_icon(c, x, 1060 - 10, 1.0, 1)
        else:
            walkers(c, x, 1050, 0.8, 1 - dim)
        sign(c, x, 1360, 1.0, lab, 1 - dim, dim * 2, 36, post=False)
    if 0 < flow < 1:
        stream = poly([(W / 2, 1030), (W / 2 - 60, 1060), (360, 1120)], close=False)
        gfx.stroke_path(c, stream, GOLD, 8, 0.9, 1.0, dash=(14, 10, -t * 80))
    e = prog(t, cue(8, "时间有限") - 0.1, 0.4)
    if e > 0:
        text(c, "时间有限：用在这儿，就用不了在别处", W / 2, 1430, 42, "bold", INK2, e)


def s10(c, t):
    """镜 10：左边三项叠加被打叉，右边只算最好的一项。"""
    pr = ease_out_back(prog(t, cue(9, "只算") - 0.1, 0.45))
    if pr > 0:
        with cam(c, pr, 790, 900):
            receipt(c, 790, 680, 300, 420)
            walkers(c, 790, 860, 1.1)
            line(c, 680, 960, 900, 960, 3, INK2, 0.5)
            tick(c, 790, 1010, 46, prog(t, cue(9, "那一个"), 0.4), BLUE, 16)
        text(c, "只算最好的那一个", 790, 1170, 42, "bold", BLUE, prog(t, cue(9, "那一个"), 0.3))
    items = (("午觉", cue(9, "午觉")), ("看书", cue(9, "看书")), ("散步", cue(9, "散步")))
    pl = ease_out(prog(t, items[0][1] - 0.4, 0.4))
    if pl > 0:
        receipt(c, 290, 560, 320, lerp(200, 760, pl))
        for k, (lab, ts) in enumerate(items):
            a = prog(t, ts - 0.1, 0.3)
            y = 680 + k * 220
            if k == 0:
                sofa(c, 290, y + 40, 0.5, a, sleeper=True, t=t)
            elif k == 1:
                desk(c, 290, y + 30, 0.55, a)
            else:
                walkers(c, 290, y + 50, 0.7, a)
            if k < 2:
                text(c, "+", 290, y + 115, 56, "serif", INK2, prog(t, items[k + 1][1] - 0.2, 0.2))
        pc = prog(t, cue(9, "全加起来"), 0.5)
        cross(c, 290, 950, 170, pc, RED, 22)
        text(c, "午睡＋看书＋散步", 290, 1400, 40, "bold", RED, pc)
    text(c, "机会成本只取一项", W / 2, TITLE_Y, 76, "serif", INK, prog(t, 0.0, 0.3))


def calculator(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shape(c, rect_path(-90, -130, 180, 260, 22), "#D9CDB4", 1, 5)
    shape(c, rect_path(-68, -108, 136, 56, 10), "#B9C7A6", 1, 4)
    for r in range(4):
        for k in range(3):
            shape(c, rect_path(-62 + k * 44, -30 + r * 38, 36, 28, 8), "#F3EAD8" if k < 2 else GOLD, 1, 3)
    c.restore()


def s11(c, t):
    """镜 11：月薪折算算式被划掉；休息与陪伴本身有价值。"""
    out = ease_in_out(prog(t, cue(10, "休息") - 0.15, 0.5))
    with cam(c, 1 - 0.3 * out, 540, 1500, 0, 300 * out):
        layer(c, 1 - out)
        frown = t < cue(10, "除非")

        def hold(cc, hx, hy, side):
            if side == 1:
                calculator(cc, hx - 40, hy - 90, 0.9)

        person(c, 540, 1600, 1.35, "lin", arms=((-10, -5), (30, -40)), look=0.3, mouth="frown" if frown else "flat",
               brow=0.8 if frown else 0, blink=blink_at(t, 0.2))
        c.restore()
    fa = prog(t, cue(10, "月薪") - 0.2, 0.3) * (1 - out)
    if fa > 0:
        text(c, "月薪 ÷ 工时 × 2小时", W / 2, 560, 66, "serif", INK, fa)
        line(c, 190, 590, 890, 576, 9, RED, fa, ease_out(prog(t, cue(10, "两小时"), 0.4)))
        text(c, "仅当这2小时真能用来加班挣钱", W / 2, 680, 46, "bold", RED, prog(t, cue(10, "除非") - 0.1, 0.3) * (1 - out))
    if out > 0:
        for k, x in enumerate((300, 780)):
            pa = ease_out_back(prog(t, cue(10, "休息") - 0.4 + k * 0.4, 0.5))
            if pa <= 0:
                continue
            with cam(c, pa, x, 980):
                shape(c, oval_path(x, 1010, 210, 190), "#EFE6D1", 1, 4.5)
                if k == 0:
                    sofa(c, x, 1060, 0.9, t=t)
                    text(c, "休息", x, 1270, 44, "bold", INK)
                else:
                    tree(c, x + 120, 1110, 0.6)
                    bench(c, x - 10, 1100, 0.9)
                    walkers(c, x - 10, 1060, 0.9)
                    text(c, "陪伴", x, 1270, 44, "bold", INK)
        text(c, "本身就有价值", W / 2, TITLE_Y + 260, 74, "serif", INK, prog(t, cue(10, "不必换成钱") - 0.1, 0.4))


def s12(c, t):
    """镜 12：上下分屏——排队本身好玩 / 朋友没空。"""
    headline(c, "值不值，看条件", TITLE_Y, 92, t, 0.1)
    for k, (y0, lab, key) in enumerate(((520, "排队本身好玩", "要是排队"), (980, "朋友没空", "阿杰也没空"))):
        pa = ease_out(prog(t, cue(11, key) - 0.5, 0.5))
        if pa <= 0:
            continue
        c.save()
        c.translate((1 - pa) * (W if k else -W), 0)
        panel = rect_path(60, y0, 960, 430, 26)
        shape(c, panel, "#F7EFDF", 1, 5)
        c.save()
        c.clipPath(panel, doAntiAlias=True)
        if k == 0:
            for j in range(3):
                ghost(c, 150 + j * 120, y0 + 430 + 30, 0.55, j)
            clap = abs(math.sin(t * 7))
            person(c, 560, y0 + 470, 0.72, "lin", arms=((lerp(-60, -25, clap), lerp(-130, -100, clap)),
                                                          (lerp(60, 25, clap), lerp(130, 100, clap))),
                   look=0.6, mouth="big", blink=blink_at(t, 0.5))

            def guitar(cc, hx, hy, side):
                if side == -1:
                    shape(cc, oval_path(hx + 60, hy + 20, 60, 44), mix(WOOD, BROWN, 0.5), 1, 4)
                    line(cc, hx + 60, hy + 10, hx + 200, hy - 70, 12, BROWN)

            person(c, 830, y0 + 470, 0.72, "jie" if False else "clerk", arms=((40, 70), (20, -60)),
                   look=-0.4, mouth="smile", blink=blink_at(t, 1.3), hold=guitar)
            for j in range(3):
                ph = (t * 0.5 + j / 3) % 1
                text(c, "♪", 720 + j * 40 + 20 * math.sin(ph * 6), y0 + 220 - ph * 160, 52, "black", INK2,
                     1 - ph, halo=False)
        else:
            shape(c, rect_path(260, y0 + 300, 560, 30, 8), mix(WOOD, BROWN, 0.4), 1, 4.5)
            shape(c, poly([(560, y0 + 300), (760, y0 + 300), (740, y0 + 190), (580, y0 + 190)]), "#BFC6CC", 1, 4.5)
            shake = math.sin(t * 9) * 0.6 * (prog(t, cue(11, "阿杰也没空"), 0.2))
            person(c, 420, y0 + 520, 0.78, "jie", arms=((-30, -150), (60, 160 + 20 * math.sin(t * 9))),
                   look=shake, tilt=shake * 0.5, mouth="frown", blink=blink_at(t, 0.7),
                   hold=lambda cc, hx, hy, side: side == -1 and phone(cc, hx, hy - 30, 50, 90, 1, 10))
        c.restore()
        ta = prog(t, cue(11, key) + 0.4, 0.3)
        tag_w = gfx.text_width(lab, 46, "bold") + 120
        shape(c, rect_path(1000 - tag_w, y0 + 24, tag_w, 80, 40), "#FBF6EA", ta, 4)
        gfx.draw_text(c, lab, 1000 - tag_w / 2 - 26, y0 + 64, 46, "bold", INK, ta)
        tick(c, 1000 - 52, y0 + 64, 22, prog(t, cue(11, key) + 0.5, 0.4), BLUE, 9)
        c.restore()


def s13(c, t):
    """镜 13：排到一半，前一小时成沉没成本，只比较剩下一小时。"""
    pull = ease_in_out(prog(t, 8.4, 0.8))
    with cam(c, 1 - 0.15 * pull, W / 2, 1000):
        with cam(c, 0.72, 330, 1340):
            queue_scene(c, t, 330, 0, look=0.4, mouth="think")
        clock(c, 170, 640, 70, 15.0, sec=(t * 6) % 60)
        gray = ease_in_out(prog(t, cue(12, "前面") - 0.1, 0.6))
        glow = ease_out(prog(t, cue(12, "剩下") - 0.2, 0.5))
        cells = [dict(gray=gray if i < 4 else 0, glow=glow if i >= 4 else 0) for i in range(8)]
        calendar(c, 860, 600, 190, 82, cells)
        stamp(c, 860, 600 + 2 * 82, "回不来", prog(t, cue(12, "回不来"), 0.35), 44)
        ta = prog(t, cue(12, "回不来") + 0.3, 0.3)
        text(c, "沉没成本", 860, 600 + 4 * 82 - 8, 40, "bold", RED, ta)
        text(c, "剩下 1 小时", 860, 600 + 8 * 82 + 60, 44, "bold", INK, glow)
        aa = ease_out(prog(t, cue(12, "该比的") - 0.2, 0.6))
        if aa > 0:
            p1 = skia.Path()
            p1.moveTo(440, 1000)
            p1.quadTo(560, 960, 640, 1060)
            gfx.stroke_path(c, p1, INK, 9, 1, aa)
            c.drawPath(poly([(640, 1060), (612, 1046), (646, 1030)]), fill_paint(INK, aa))
            text(c, "继续排", 640, 1110, 40, "bold", INK, aa)
            p2 = skia.Path()
            p2.moveTo(400, 900)
            p2.quadTo(430, 780, 560, 770)
            gfx.stroke_path(c, p2, GOLD, 11, 1, aa, glow=(GOLD, 10))
            c.drawPath(poly([(572, 770), (544, 752), (546, 790)]), fill_paint(GOLD, aa))
            text(c, "去找阿杰", 560, 710, 42, "bold", BROWN, aa)
    text(c, "排到一半才收到邀约", W / 2, TITLE_Y, 72, "serif", INK, prog(t, 0.1, 0.3))


def s14(c, t):
    """镜 14：回到开场构图，小林的手停在半空，定格提问。"""
    with cam(c, 1.0, W / 2, 1000):
        shop(c, 520, 1330, 620, 640, t=t)
        clock(c, 820, 700, 64, 14.0, sec=min(t, 1.0) * 6)
        for k in range(6):
            ghost(c, 150 - k * 70, 1250 - k * 28, 0.62 - k * 0.04, k, 0.9)

        def clerk_hold(cc, hx, hy, side):
            if side == -1:
                coupon(cc, hx - 50, hy - 10, 0.75, -8)

        p_give = ease_out(prog(t, 0.0, 0.8))
        person(c, 730, 1330, 0.95, "clerk", arms=((lerp(-10, -70, p_give), lerp(-6, -85, p_give)), (10, 4)),
               look=-0.6, mouth="smile", blink=blink_at(t, 1), hold=clerk_hold)
        reach = ease_out(prog(t, 0.5, 0.6)) * 0.7
        up = ease_in_out(prog(t, 1.4, 0.6))
        person(c, 390, 1330, 1.0, "lin", arms=((-10, -5), (lerp(10, 60, reach), lerp(4, 95, reach))),
               look=lerp(0.5, 0.1, up), tilt=-0.5 * up, mouth="think", brow=0.3 * up, blink=False)
        for k in range(3):
            gfx.circle(c, 470 + k * 34, 820 - k * 40, 10 + k * 6, "#FFFFFF", up * prog(t, 1.8 + k * 0.2, 0.3))
            c.drawCircle(470 + k * 34, 820 - k * 40, 10 + k * 6, ink_paint(3.5, INK, up * prog(t, 1.8 + k * 0.2, 0.3)))
    st = cue(13, "这段时间") - 0.2
    if t >= st:
        a = prog(t, st, 0.4)
        text(c, "这段时间，我真正能做、", W / 2, TITLE_Y - 70, 70, "serif", INK, a)
        text(c, "也【最想做】的另一件事，", W / 2, TITLE_Y + 20, 70, "serif", INK, prog(t, st + 1.2, 0.4))
        text(c, "是什么？", W / 2, TITLE_Y + 120, 96, "serif", RED, prog(t, cue(13, "是什么") - 0.1, 0.4))


@dataclass
class Shot:
    start: float
    end: float
    fn: object
    trans: str  # 进入下一镜的转场：cut / fade / whip / wipe / none


SHOTS = [
    Shot(0.0, 5.0, s1, "whip"), Shot(5.0, 12.0, s2, "fade"), Shot(12.0, 21.0, s3, "fade"),
    Shot(21.0, 27.0, s4, "cut"), Shot(27.0, 32.5, s5, "fade"), Shot(32.5, 42.0, s6, "cut"),
    Shot(42.0, 51.5, s7, "fade"), Shot(51.5, 56.0, s8, "wipe"), Shot(56.0, 65.5, s9, "fade"),
    Shot(65.5, 71.5, s10, "fade"), Shot(71.5, 79.0, s11, "fade"), Shot(79.0, 86.0, s12, "fade"),
    Shot(86.0, 95.0, s13, "fade"), Shot(95.0, 103.0, s14, "none"),
]
TOTAL = SHOTS[-1].end
TR = 0.4  # 转场时长，跨越镜头边界前后各一半

CAPS = [(SHOTS[i].start + t0, s) for i in range(len(SHOTS)) for t0, s in captions(i)]
CAP_END = {i: SHOTS[i].start + NARRATION[i][2] + 0.35 for i in range(len(SHOTS))}
CAP_SHOT = [i for i in range(len(SHOTS)) for _ in captions(i)]


def draw_captions(c, T):
    for k, (t0, s) in enumerate(CAPS):
        i = CAP_SHOT[k]
        t1 = CAPS[k + 1][0] if k + 1 < len(CAPS) and CAP_SHOT[k + 1] == i else CAP_END[i]
        if not (t0 <= T < t1):
            continue
        if i == 13 and "这段时间" in gfx.plain(s) or i == 13 and gfx.plain(s).startswith(("也", "是什么")):
            continue
        a = prog(T, t0, 0.12) * (1 - prog(T, t1 - 0.12, 0.12))
        gfx.draw_rich(c, s, W / 2, CAP_Y, 54, "bold", INK, RED, a, stroke=(PAPER, 14))


def draw_frame(c, frame):
    global _FRAME
    _FRAME = frame
    T = frame / FPS
    c.drawImage(paper_image(), 0, 0)
    for k, sh in enumerate(SHOTS):
        lo = sh.start - (TR / 2 if k and SHOTS[k - 1].trans in ("fade", "whip", "wipe") else 0)
        hi = sh.end + (TR / 2 if sh.trans in ("fade", "whip", "wipe") else 0)
        if not (lo <= T < hi):
            continue
        t = T - sh.start
        a, dx, blur = 1.0, 0.0, 0.0
        if T < sh.start and k:
            p = (T - lo) / (sh.start - lo)
            tr = SHOTS[k - 1].trans
            a = ease_in_out(p)
            if tr == "whip":
                dx, blur = (1 - ease_out(p)) * 500, 40 * (1 - p)
            if tr == "wipe":
                a = 1.0
        if T >= sh.end:
            p = (T - sh.end) / (hi - sh.end)
            if sh.trans == "whip":
                a, dx, blur = 1 - ease_in_out(p), -ease_in_out(p) * 500, 40 * p
            elif sh.trans == "wipe":
                a = 1.0
            else:
                a = 1.0
        clip = None
        if T < sh.start and k and SHOTS[k - 1].trans == "wipe":
            p = ease_in_out((T - lo) / (sh.start - lo))
            clip = skia.Rect.MakeLTRB(W * (1 - p), 0, W, H)
        c.save()
        if clip is not None:
            c.clipRect(clip)
            c.drawImage(paper_image(), 0, 0)
        if a < 1 or blur > 0:
            layer(c, a, 0, blur)
        c.translate(dx, 0)
        sh.fn(c, max(t, 0.0))
        if a < 1 or blur > 0:
            c.restore()
        c.restore()
        if clip is not None:
            c.drawLine(clip.left(), 0, clip.left(), H, ink_paint(6, INK, 0.5, wobble=False))
    draw_captions(c, T)
    end = prog(T, TOTAL - 0.6, 0.6)
    if end > 0:
        c.drawPaint(fill_paint(PAPER, end))
    gp = skia.Paint(BlendMode=skia.BlendMode.kMultiply, Alphaf=0.55)
    c.drawImage(grain_image((frame // 2) % 3), 0, 0, skia.SamplingOptions(), gp)


_BUF = None
_SURF = None


def _worker(frame):
    global _BUF, _SURF
    if _SURF is None:
        _BUF = np.zeros((H, W, 4), np.uint8)
        _SURF = skia.Surface(_BUF)
    c = _SURF.getCanvas()
    c.clear(col(PAPER))
    draw_frame(c, frame)
    return _BUF.tobytes()


def still(T):
    return np.frombuffer(_worker(int(round(T * FPS))), np.uint8).reshape(H, W, 4)


def render(out_path, workers=4):
    paper_image()
    for k in range(3):
        grain_image(k)
    n = int(round(TOTAL * FPS))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        with get_context("fork").Pool(workers) as pool:
            for k, buf in enumerate(pool.imap(_worker, range(n), chunksize=8)):
                proc.stdin.write(buf)
                if k % 300 == 0:
                    print(f"  {k}/{n}", flush=True)
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")
    cover = Path(out_path).with_name("opportunity_cost_cover.png")
    cv2.imwrite(str(cover), cv2.cvtColor(still(0.9), cv2.COLOR_RGBA2BGR))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--stills":
        d = Path(sys.argv[2])
        d.mkdir(parents=True, exist_ok=True)
        times = [float(x) for x in sys.argv[3:]] or [s.start + (s.end - s.start) * 0.75 for s in SHOTS]
        for T in times:
            cv2.imwrite(str(d / f"t{T:06.2f}.png"), cv2.cvtColor(still(T), cv2.COLOR_RGBA2BGR))
        print("stills:", len(times))
    else:
        render(sys.argv[1] if len(sys.argv) > 1 else "out/opportunity_cost_silent.mp4")
