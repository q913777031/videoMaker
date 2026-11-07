"""《丰田模式》第 14 讲起分镜模块共用的小工具与办公室人物（只被 ep14_changeover / ep15_a3 / ep16_teach 引用）。

不是分镜模块：import 它不会跑任何一讲。人物里小王（draw_wang）照抄第 06/07/09 讲的造型（短发、白衬衫、蓝工牌，不戴安全帽）；
新人小周（draw_zhou）为第 16 讲新角色：短卷发、圆框眼镜、绿色卫衣、挂“新人”工牌，同样不戴安全帽。
"""

import math
from contextlib import contextmanager

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, BOARD_C, pop_scale, rest_hands
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross, rect

GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL = "#8A8F99", "#ECEEF1", "#D3EDDC", "#F6C3BE", "#D5E3F7"
NOTE_FILL, ORANGE_FILL, WOOD, WOOD_LINE = "#FFF1A8", "#FDE3C8", "#E3C9A0", "#A9773E"
WANG_SHIRT, HAIR = "#FFFFFF", "#2E2A28"
ZHOU_TOP, ZHOU_LINE = "#BFE3C6", "#2E8A57"


class Kit:
    """绑定一讲的 Lesson：拍点挑选与常用的弹出项。"""

    def __init__(self, L):
        self.L, self.b = L, L.b

    def nbeats(self, j):
        return self.L.BOUNDS[j][1] - self.L.BOUNDS[j][0]

    def kq(self, j, t_local, lo=0):
        """kb，但 lo 超出本屏时夹到最后一拍。"""
        return self.L.kb(j, t_local, lo=min(lo, self.nbeats(j) - 1))

    def nx(self, j, t_local, prev, gap=1):
        """离 t_local 最近、且至少在 prev 之后 gap 拍的拍号。"""
        return max(self.kq(j, t_local, prev + gap), prev + gap)

    def seq(self, j, marks, first=0):
        """按旁白位置挑一串递增的拍：marks 为 [(句, 分句, 比例) 或 None（紧接上一拍）]；first 为第一个元素的拍号下限。"""
        out, prev = [], first - 1
        for m in marks:
            k = prev + 1 if m is None else self.nx(j, self.L.wt(*m), prev)
            out.append(k)
            prev = k
        return out

    def ev(self, j, k, fn, sfx=None, gain=0.8, dur=0.3):
        self.b.custom(j, k, k + dur, fn, sfx=sfx, gain=gain)

    def pop(self, j, k, x, y, draw, sfx=None, gain=0.75, slam=False, dur=0.32):
        """第 j 屏第 k 拍以 (x, y) 为中心弹出（slam=True 为砸下）：draw(c, T) 在白板坐标里画。"""
        L = self.L

        def fn(c, kk, T):
            dt = T - L.tb(j, k)
            sc = C.slam_scale(dt) if slam else pop_scale(dt, dur)
            if sc <= 0:
                return None
            with at_pop(c, x, y, sc):
                draw(c, T)
            return None
        self.ev(j, k, fn, sfx, gain)

    def since(self, j, k, T):
        """距第 j 屏第 k 拍的秒数（未到为负）。"""
        return T - self.L.tb(j, k)

    def grow(self, j, k, T, dur=0.4):
        """第 k 拍起 dur 秒内 0→1（缓出）。"""
        return ease_out(clamp01((T - self.L.tb(j, k)) / dur))


@contextmanager
def at_pop(c, x, y, sc):
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    c.translate(-x, -y)
    try:
        yield
    finally:
        c.restore()


# ================================================================ 小件

def box(c, x, y, w, h, fill, line, width=6, r=14, alpha=1.0):
    rr = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(rr, r, r, K.paint(fill, alpha))
    c.drawRoundRect(rr, r, r, wb.marker(line, width, alpha))


def dashed(c, a, z, color, width, alpha=1.0, on=18, off=12):
    p = K.paint(color, alpha, width)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    c.drawLine(a[0], a[1], z[0], z[1], p)


def dashed_rect(c, x, y, w, h, color, width, alpha=1.0, r=12, on=22, off=14):
    p = K.paint(color, alpha, width)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), r, r, p)


def head_of(x, y, s):
    return x, y - 290 * s


def bubble_box(c, x, y, w, h, tail=-1, alpha=1.0, fill="#FFFFFF"):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 40, 40, K.paint(fill, alpha))
    c.drawPath(wb.bubble(x, y, w, h, tail), wb.marker(BLACK, 7, alpha))


def bubble_text(c, s, x, y, size=62, color=BLACK, tail=-1, alpha=1.0):
    w = K.text_w(s, size, "hand") + 90
    bubble_box(c, x, y, w, size + 70, tail, alpha)
    K.text(c, s, x, y, size, "hand", color, alpha)


def sweat(c, x, y, s=1.0, alpha=1.0):
    p = skia.Path()
    p.moveTo(x, y - 26 * s)
    p.cubicTo(x + 4 * s, y - 14 * s, x + 16 * s, y - 2 * s, x + 16 * s, y + 8 * s)
    p.cubicTo(x + 16 * s, y + 18 * s, x + 8 * s, y + 24 * s, x, y + 24 * s)
    p.cubicTo(x - 8 * s, y + 24 * s, x - 16 * s, y + 18 * s, x - 16 * s, y + 8 * s)
    p.cubicTo(x - 16 * s, y - 2 * s, x - 4 * s, y - 14 * s, x, y - 26 * s)
    c.drawPath(p, K.paint("#CFE3F8", alpha))
    c.drawPath(p, wb.marker(BLUE, 4, alpha))


def sparkle(c, x, y, dt, color=YELLOW, n=8, r0=40, r1=130):
    if dt < 0 or dt > 0.9:
        return
    f = ease_out(clamp01(dt / 0.5))
    a = 1 - clamp01((dt - 0.5) / 0.4)
    for i in range(n):
        ang = 2 * math.pi * i / n
        r_a, r_b = lerp(r0, r1 * 0.7, f), lerp(r0 + 20, r1, f)
        C.line(c, (x + math.cos(ang) * r_a, y + math.sin(ang) * r_a), (x + math.cos(ang) * r_b, y + math.sin(ang) * r_b),
               color, 7, a)


def clock_face(c, x, y, r, frac=0.0, hand=None, color=GREEN, fill=GREEN_FILL, alpha=1.0):
    """钟面：从 12 点顺时针扫出 frac 的扇形；hand 给定时画一根指针（0–1 圈）。"""
    c.drawCircle(x, y, r, K.paint("#FFFFFF", alpha))
    if frac > 0.002:
        pie = skia.Path()
        pie.moveTo(x, y)
        pie.arcTo(skia.Rect.MakeXYWH(x - r * 0.9, y - r * 0.9, r * 1.8, r * 1.8), -90, 360 * min(frac, 0.9999), False)
        pie.close()
        c.drawPath(pie, K.paint(fill, alpha))
        c.drawPath(pie, wb.marker(color, max(3, r * 0.03), alpha))
    c.drawCircle(x, y, r, wb.marker(BLACK, max(5, r * 0.05), alpha))
    for i in range(12):
        a = i * math.pi / 6
        C.line(c, (x + math.cos(a) * r * 0.86, y + math.sin(a) * r * 0.86),
               (x + math.cos(a) * r * 0.96, y + math.sin(a) * r * 0.96), BLACK, max(3, r * 0.03), alpha)
    if hand is not None:
        a = -math.pi / 2 + 2 * math.pi * hand
        C.line(c, (x, y), (x + math.cos(a) * r * 0.75, y + math.sin(a) * r * 0.75), RED, max(5, r * 0.06), alpha)
        c.drawCircle(x, y, max(5, r * 0.07), K.paint(BLACK, alpha))


def hourglass(c, x, y, h, f, alpha=1.0):
    """沙漏：f 为已流下的比例。"""
    w = h * 0.55
    top = P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + 8, y), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2),
            (x - 8, y), close=True)
    c.drawPath(top, K.paint("#FFFFFF", alpha))
    sand = "#E0B04A"
    ht = (h / 2 - 12) * (1 - f)
    if ht > 2:
        wt = (w / 2 - 6) * ht / (h / 2)
        c.drawPath(P((x - wt, y - ht), (x + wt, y - ht), (x, y - 4), close=True), K.paint(sand, alpha))
    hb = (h / 2 - 12) * f
    if hb > 2:
        c.drawPath(P((x - (w / 2 - 6), y + h / 2 - 8), (x + (w / 2 - 6), y + h / 2 - 8),
                     (x + (w / 2 - 6) * (1 - hb / (h / 2)), y + h / 2 - 8 - hb),
                     (x - (w / 2 - 6) * (1 - hb / (h / 2)), y + h / 2 - 8 - hb), close=True), K.paint(sand, alpha))
    if 0 < f < 1:
        C.line(c, (x, y), (x, y + h / 2 - 8 - hb), sand, 4, alpha)
    c.drawPath(top, wb.marker(BLACK, 7, alpha))
    for yy in (y - h / 2, y + h / 2):
        C.line(c, (x - w / 2 - 20, yy), (x + w / 2 + 20, yy), WOOD_LINE, 12, alpha)


def laptop(c, x, y, s=1.0, screen="#FFFFFF", alpha=1.0, open_=1.0):
    """笔记本电脑：(x, y) 为底座中点；open_ 0–1 为屏幕打开程度。"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 150 * s, y - 16 * s, 300 * s, 22 * s), 8, 8, K.paint("#C9CED6", alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 150 * s, y - 16 * s, 300 * s, 22 * s), 8, 8, wb.marker(BLACK, 6, alpha))
    h = 190 * s * open_
    if h > 4:
        r = skia.Rect.MakeXYWH(x - 130 * s, y - 16 * s - h, 260 * s, h)
        c.drawRoundRect(r, 8, 8, K.paint(screen, alpha))
        c.drawRoundRect(r, 8, 8, wb.marker(BLACK, 6, alpha))


def desk(c, x, y, w=520, alpha=1.0):
    """桌子：(x, y) 为桌面中点。"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - 12, w, 26), 6, 6, K.paint(WOOD, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - 12, w, 26), 6, 6, wb.marker(WOOD_LINE, 6, alpha))
    for dx in (-w / 2 + 30, w / 2 - 30):
        C.line(c, (x + dx, y + 14), (x + dx, y + 200), WOOD_LINE, 9, alpha)


def paper(c, x, y, w, h, rows=4, alpha=1.0, rot=0.0, fill="#FFFFFF", line=BLACK, title=None, tsize=46):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, fill, line, 6, 8, alpha)
        top = -h / 2 + (h * 0.22 if title else h * 0.16)
        if title:
            K.text(c, title, 0, -h / 2 + h * 0.13, tsize, "hand", line, alpha)
        for r in range(rows):
            yy = top + r * (h * 0.7 / max(1, rows))
            C.line(c, (-w * 0.36, yy), (w * (0.36 if r % 3 != 2 else 0.1), yy), GRAY, 5, alpha)


def phone(c, x, y, w=190, h=340, alpha=1.0, screen="#FFFFFF"):
    box(c, x, y, w, h, "#3B3F48", BLACK, 6, 26, alpha)
    box(c, x, y, w - 26, h - 60, screen, GRAY, 3, 10, alpha)


def qmark(c, x, y, size, dt, color=RED):
    sc = pop_scale(dt)
    if sc > 0:
        with K.at(c, x, y, 8 * math.sin(dt * 6) * math.exp(-dt * 2), sc):
            K.text(c, "？", 0, 0, size, "black", color)


def tick(c, x, y, r, f, color=GREEN, width=14):
    if f > 0:
        part, _ = wb.partial(check(x, y, r), clamp01(f))
        c.drawPath(part, wb.marker(color, width))


def xmark(c, x, y, r, f, color=RED, width=16):
    if f > 0:
        part, _ = wb.partial(cross(x, y, r), clamp01(f))
        c.drawPath(part, wb.marker(color, width))


def heart(c, x, y, r, color=RED, fill="#F6C3BE", alpha=1.0):
    p = C.heart_path(x, y, r)
    c.drawPath(p, K.paint(fill, alpha))
    c.drawPath(p, wb.marker(color, 8, alpha))


def bag(c, x, y, s=1.0, alpha=1.0):
    """公文包：(x, y) 为底边中点。"""
    box(c, x, y - 60 * s, 170 * s, 120 * s, "#8C5A3C", BLACK, 6, 12, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 40 * s, y - 150 * s, 80 * s, 40 * s), 14, 14, wb.marker(BLACK, 6, alpha))


def comment_box(c, x, y, w, h, alpha=1.0):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 30, 30, K.paint("#FFFFFF", alpha))
    c.drawPath(wb.bubble(x, y, w, h, -1), wb.marker(BLACK, 8, alpha))


# ================================================================ 人物

def draw_wang(c, x, y, s, lh=None, rh=None, mood="flat", head_dx=0.0, alpha=1.0):
    """同事小王（办公室）：齐耳短发 + 橙色发卡、白衬衫蓝描边、蓝工牌、蓝色四肢；不戴安全帽（与第 06、07、09 讲同一造型）。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, ft, BLUE, 10, alpha)
    C.line(c, sh, lh, BLUE, 10, alpha)
    C.line(c, sh, rh, BLUE, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 42 * s, hy + 55 * s, x + 42 * s, y - 105 * s)
    c.drawRoundRect(torso, 18 * s, 18 * s, K.paint(WANG_SHIRT, alpha))
    c.drawRoundRect(torso, 18 * s, 18 * s, wb.marker(BLUE, 7, alpha))
    c.drawPath(P((x - 16 * s, hy + 58 * s), (x, hy + 82 * s), (x + 16 * s, hy + 58 * s)), wb.marker(BLUE, 5, alpha))
    badge_ = skia.Rect.MakeXYWH(x - 20 * s, hy + 110 * s, 40 * s, 30 * s)
    c.drawRoundRect(badge_, 4, 4, K.paint("#DCE8F7", alpha))
    c.drawRoundRect(badge_, 4, 4, wb.marker(BLUE, 4, alpha))
    hx = x + head_dx
    back = skia.Rect.MakeLTRB(hx - 54 * s, hy - 46 * s, hx + 54 * s, hy + 40 * s)
    c.drawRoundRect(back, 26 * s, 26 * s, K.paint(HAIR, alpha))
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(hx - 50 * s, hy - 52 * s, 100 * s, 72 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint(HAIR, alpha))
    c.drawCircle(hx + 36 * s, hy - 24 * s, 9 * s, K.paint(ORANGE, alpha))
    C._eyes_mouth(c, hx, hy + 4 * s, s, mood, alpha)


def draw_zhou(c, x, y, s, lh=None, rh=None, mood="flat", head_dx=0.0, alpha=1.0):
    """新人小周（办公室）：短卷发、圆框眼镜、绿色卫衣、胸前挂“新”字工牌、绿色四肢；不戴安全帽。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 48 * s, y), (x + 48 * s, y)):
        C.line(c, hip, ft, ZHOU_LINE, 10, alpha)
    C.line(c, sh, lh, ZHOU_LINE, 10, alpha)
    C.line(c, sh, rh, ZHOU_LINE, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 44 * s, hy + 55 * s, x + 44 * s, y - 100 * s)
    c.drawRoundRect(torso, 22 * s, 22 * s, K.paint(ZHOU_TOP, alpha))
    c.drawRoundRect(torso, 22 * s, 22 * s, wb.marker(ZHOU_LINE, 7, alpha))
    C.line(c, (x - 18 * s, hy + 58 * s), (x - 4 * s, hy + 110 * s), BLACK, 3, alpha)
    C.line(c, (x + 18 * s, hy + 58 * s), (x + 4 * s, hy + 110 * s), BLACK, 3, alpha)
    card = skia.Rect.MakeXYWH(x - 22 * s, hy + 110 * s, 44 * s, 40 * s)
    c.drawRoundRect(card, 4, 4, K.paint("#FFFFFF", alpha))
    c.drawRoundRect(card, 4, 4, wb.marker(ZHOU_LINE, 4, alpha))
    K.text(c, "新", x, hy + 131 * s, 28 * s, "hand", ZHOU_LINE, alpha)
    hx = x + head_dx
    for i in range(7):
        a = math.radians(200 + i * 23)
        c.drawCircle(hx + math.cos(a) * 42 * s, hy - 6 * s + math.sin(a) * 40 * s, 17 * s, K.paint("#5A3B28", alpha))
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    for i in range(4):
        a = math.radians(225 + i * 30)
        c.drawCircle(hx + math.cos(a) * 34 * s, hy - 8 * s + math.sin(a) * 34 * s, 13 * s, K.paint("#5A3B28", alpha))
    for dx in (-16, 16):
        c.drawCircle(hx + dx * s, hy - 2 * s, 13 * s, wb.marker(BLACK, 4, alpha))
    C.line(c, (hx - 3 * s, hy - 2 * s), (hx + 3 * s, hy - 2 * s), BLACK, 4, alpha)
    for dx in (-16, 16):
        c.drawCircle(hx + dx * s, hy - 2 * s, 3.5 * s, K.paint(BLACK, alpha))
    m = skia.Path()
    if mood == "smile":
        m.addArc(skia.Rect.MakeXYWH(hx - 15 * s, hy + 10 * s, 30 * s, 22 * s), 20, 140)
        c.drawPath(m, wb.marker(BLACK, 6, alpha))
    elif mood == "sad":
        m.addArc(skia.Rect.MakeXYWH(hx - 14 * s, hy + 22 * s, 28 * s, 16 * s), 200, 140)
        c.drawPath(m, wb.marker(BLACK, 6, alpha))
    elif mood == "o":
        c.drawCircle(hx, hy + 26 * s, 7 * s, wb.marker(BLACK, 5, alpha))
    else:
        C.line(c, (hx - 12 * s, hy + 26 * s), (hx + 12 * s, hy + 26 * s), BLACK, 6, alpha)


def draw_mom(c, x, y, s, lh=None, rh=None, mood="flat", alpha=1.0):
    """家里人（妈妈）：长发 + 红色连衣裙（与第 07、09 讲同一造型）。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    for ft in ((x - 35 * s, y), (x + 35 * s, y)):
        C.line(c, (ft[0] * 0.6 + x * 0.4, y - 90 * s), ft, BLACK, 9, alpha)
    dress = P((x - 32 * s, hy + 55 * s), (x + 32 * s, hy + 55 * s), (x + 75 * s, y - 80 * s), (x - 75 * s, y - 80 * s),
              close=True)
    c.drawPath(dress, K.paint(RED_FILL, alpha))
    c.drawPath(dress, wb.marker(RED, 7, alpha))
    C.line(c, sh, lh, BLACK, 9, alpha)
    C.line(c, sh, rh, BLACK, 9, alpha)
    hair = skia.Rect.MakeLTRB(x - 55 * s, hy - 50 * s, x + 55 * s, hy + 75 * s)
    c.drawRoundRect(hair, 30 * s, 30 * s, K.paint(HAIR, alpha))
    c.drawCircle(x, hy, 44 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 44 * s, wb.marker(BLACK, 8, alpha))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(x - 48 * s, hy - 52 * s, 96 * s, 64 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint(HAIR, alpha))
    C._eyes_mouth(c, x, hy + 6 * s, s, mood, alpha)


def draw_dad(c, x, y, s, lh=None, rh=None, mood="flat", alpha=1.0):
    """家里人（爸爸）：灰白短发、方框眼镜、棕色毛衣。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 52 * s, y), (x + 52 * s, y)):
        C.line(c, hip, ft, BLACK, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 48 * s, hy + 55 * s, x + 48 * s, y - 100 * s)
    c.drawRoundRect(torso, 20 * s, 20 * s, K.paint("#C9A27E", alpha))
    c.drawRoundRect(torso, 20 * s, 20 * s, wb.marker("#7A4E2D", 7, alpha))
    C.line(c, sh, lh, "#7A4E2D", 10, alpha)
    C.line(c, sh, rh, "#7A4E2D", 10, alpha)
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    cap = skia.Path()
    cap.addArc(skia.Rect.MakeXYWH(x - 46 * s, hy - 50 * s, 92 * s, 50 * s), 180, 180)
    cap.close()
    c.drawPath(cap, K.paint("#BFC3C8", alpha))
    for dx in (-17, 17):
        c.drawRoundRect(skia.Rect.MakeXYWH(x + dx * s - 13 * s, hy - 14 * s, 26 * s, 20 * s), 4, 4, wb.marker(BLACK, 4, alpha))
    C.line(c, (x - 4 * s, hy - 4 * s), (x + 4 * s, hy - 4 * s), BLACK, 4, alpha)
    C._eyes_mouth(c, x, hy + 4 * s, s, mood, alpha)


def draw_leader2(c, x, y, s, rh=None, lh=None, mood="frown", head_dx=0.0, alpha=1.0):
    """车间组长（老张）：红帽、夹板、红臂章——照 common.draw_leader（不跑步），另加 rh（右手）和 mood（"frown" / "smile"）。"""
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    C.line(c, (x, hy + 45 * s), hip, BLACK, 11, alpha)
    for sgn in (1, -1):
        C.line(c, hip, (x + sgn * 55 * s, y), BLACK, 11, alpha)
    clip_c = (x - 80 * s, hy + 150 * s)
    C.line(c, sh, lh or (clip_c[0] + 10 * s, clip_c[1]), BLACK, 11, alpha)
    rh = rh or (x + 70 * s, hy + 170 * s)
    C.line(c, sh, rh, BLACK, 11, alpha)
    if lh is None:
        clip = skia.Rect.MakeXYWH(clip_c[0] - 40 * s, clip_c[1] - 55 * s, 80 * s, 105 * s)
        c.drawRoundRect(clip, 6, 6, K.paint(BOARD_C, alpha))
        c.drawRoundRect(clip, 6, 6, wb.marker(BLACK, 6, alpha))
        for i in range(3):
            yy = clip_c[1] - 20 * s + i * 22 * s
            C.line(c, (clip_c[0] - 25 * s, yy), (clip_c[0] + 25 * s, yy), BLACK, 4, alpha)
    ax, ay = lerp(sh[0], rh[0], 0.4), lerp(sh[1], rh[1], 0.4)
    with K.at(c, ax, ay, math.degrees(math.atan2(rh[1] - sh[1], rh[0] - sh[0])) - math.degrees(math.atan2(90, 70))):
        c.drawRoundRect(skia.Rect.MakeXYWH(-30 * s, -15 * s, 60 * s, 30 * s), 6, 6, K.paint(RED, alpha))
    hx = x + head_dx
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    for dx in (-15, 15):
        c.drawCircle(hx + dx * s, hy - 4 * s, 4 * s, K.paint(BLACK, alpha))
    m = skia.Path()
    if mood == "smile":
        m.addArc(skia.Rect.MakeXYWH(hx - 18 * s, hy + 2 * s, 36 * s, 26 * s), 20, 140)
    else:
        m.addArc(skia.Rect.MakeXYWH(hx - 16 * s, hy + 12 * s, 32 * s, 18 * s), 200, 140)
    c.drawPath(m, wb.marker(BLACK, 6, alpha))
    cap = skia.Path()
    cap.addArc(skia.Rect.MakeXYWH(hx - 47 * s, hy - 70 * s, 94 * s, 70 * s), 180, 180)
    cap.close()
    c.drawPath(cap, K.paint(RED, alpha))
    c.drawPath(cap, wb.marker(BLACK, 6, alpha))
    C.line(c, (hx - 10 * s, hy - 35 * s), (hx - 80 * s, hy - 30 * s), BLACK, 10, alpha)
