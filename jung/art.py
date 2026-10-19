"""荣格系列的专用元件：曼陀罗、意识层次、人格面具、阴影、四种功能罗盘、计时秒表、梦中的房子、圣甲虫等。
在阿德勒系列的纸片剪影元件（adler.kit）之上组合，坐标以元素中心为原点。"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

INDIGO = "#3B4A8C"
PLUM = "#7A4A7E"
TEAL = "#2F7A78"
SEA = "#5D86A8"
DEEP = "#27345A"
MOON = "#E9E2CF"


def mandala(c, x, y, r, t=0.0, p=1.0, color=INDIGO, accent=K.GOLD, alpha=1.0):
    """曼陀罗：同心圆 + 两圈花瓣 + 四方位方框，p 为由内向外展开的进度。"""
    if p <= 0 or alpha <= 0:
        return
    with K.at(c, x, y, t * 6):
        K.ring(c, 0, 0, r, color, 6, alpha, clamp01(p * 1.4))
        if p > 0.15:
            K.ring(c, 0, 0, r * 0.78, accent, 4, alpha, clamp01((p - 0.15) * 1.6))
        n = 12
        for i in range(n):
            q = clamp01((p - 0.2 - i * 0.02) * 3)
            if q <= 0:
                continue
            a = i / n * math.tau
            px, py = math.cos(a) * r * 0.6, math.sin(a) * r * 0.6
            with K.at(c, px, py, math.degrees(a) + 90, q):
                K.poly(c, [(0, -r * 0.2), (r * 0.08, 0), (0, r * 0.2), (-r * 0.08, 0)], K.mix(color, K.PAPER, 0.35), alpha)
        if p > 0.5:
            q = clamp01((p - 0.5) * 2.5)
            with K.at(c, 0, 0, 45, q):
                K.rr_stroke(c, 0, 0, r * 0.62, r * 0.62, 6, color, 4, alpha)
            with K.at(c, 0, 0, 0, q):
                K.rr_stroke(c, 0, 0, r * 0.62, r * 0.62, 6, accent, 4, alpha)
        for i in range(8):
            q = clamp01((p - 0.35 - i * 0.03) * 3)
            a = i / 8 * math.tau + math.pi / 8
            K.dot(c, math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, 9 * q, accent, alpha)
        K.dot(c, 0, 0, r * 0.16 * clamp01(p * 2), accent, alpha)
        K.dot(c, 0, 0, r * 0.07 * clamp01(p * 2), K.PAPER, alpha)


def psyche_layers(c, w, h, p_personal=1.0, p_collective=1.0, t=0.0, labels=True, alpha=1.0):
    """意识层次示意：水面以上三座小岛（各人的意识），水下是个人无意识，最深处连成一片（集体无意识）。"""
    top, sea = -h / 2, -h / 2 + h * 0.28
    K.rr(c, 0, 0, w, h, 26, "#E8EEF2", alpha)
    sea_h = h / 2 - sea
    K.rr(c, 0, sea + sea_h / 2, w, sea_h, 0, K.mix(SEA, K.PAPER, 0.35), alpha * clamp01(p_personal * 1.5))
    deep_y = sea + sea_h * 0.55
    if p_collective > 0:
        K.rr(c, 0, deep_y + (h / 2 - deep_y) / 2, w, h / 2 - deep_y, 0, DEEP, alpha * clamp01(p_collective * 1.5))
    xs = (-w * 0.3, 0, w * 0.3)
    for i, ix in enumerate(xs):
        K.poly(c, [(ix - 70, sea), (ix - 20, sea - 80), (ix + 20, sea - 60), (ix + 70, sea)], K.mix(K.GREEN, K.PAPER, 0.2), alpha)
        if p_personal > 0:
            k = clamp01(p_personal * 1.6 - i * 0.2)
            K.poly(c, [(ix - 70, sea), (ix + 70, sea), (ix + 110 * k, sea + (deep_y - sea) * k), (ix - 110 * k, sea + (deep_y - sea) * k)],
                   K.mix(K.INK3, K.PAPER, 0.25), alpha * k)
    if p_collective > 0:
        k = ease_out(clamp01(p_collective))
        K.poly(c, [(-w * 0.45, h / 2), (-w * 0.42 * k, deep_y), (w * 0.42 * k, deep_y), (w * 0.45, h / 2)], K.mix(INDIGO, DEEP, 0.3), alpha * k)
    K.seg(c, -w / 2, sea, w / 2, sea, K.INK, 4, alpha)
    for i in range(3):
        xx = -w / 2 + ((t * 40 + i * w / 3) % w)
        K.seg(c, xx, sea + 6, xx + 40, sea + 6, K.PAPER, 3, alpha * 0.6)
    if labels:
        K.text(c, "意识", w / 2 - 90, top + 60, 34, "serif_black", K.INK, alpha)
        K.text(c, "个人无意识", w / 2 - 120, sea + 60, 32, "serif_black", K.PAPER, alpha * clamp01(p_personal * 2))
        K.text(c, "集体无意识", 0, h / 2 - 70, 40, "serif_black", K.GOLD, alpha * clamp01(p_collective * 2 - 0.5))


def mask(c, x, y, s, color=K.PAPER, mood="smile", alpha=1.0, rot=0.0, handle=True):
    """戏剧面具（persona 的本义）：椭圆面具、两个眼洞、笑或平的嘴，下方一根手柄。"""
    with K.at(c, x, y, rot):
        if handle:
            K.seg(c, s * 0.15, s * 0.45, s * 0.35, s * 1.1, K.mix(K.DARK, K.GOLD, 0.3), s * 0.07, alpha)
        path = skia.Path()
        path.addOval(skia.Rect.MakeXYWH(-s * 0.42, -s * 0.5, s * 0.84, s))
        c.drawPath(path, K.paint(color, alpha))
        c.drawPath(path, K.paint(K.INK, alpha, s * 0.03))
        for sx in (-1, 1):
            K.dot(c, sx * s * 0.16, -s * 0.1, s * 0.07, K.INK, alpha)
        m = skia.Path()
        if mood == "smile":
            m.moveTo(-s * 0.16, s * 0.18)
            m.quadTo(0, s * 0.32, s * 0.16, s * 0.18)
        else:
            m.moveTo(-s * 0.14, s * 0.24)
            m.lineTo(s * 0.14, s * 0.24)
        c.drawPath(m, K.paint(K.INK, alpha, s * 0.035))


def shadow_self(c, x, y, s, p=1.0, alpha=1.0, pose="stand", face=1):
    """影子：人物脚下拉长的深色剪影（朝右上方投出）。"""
    if p <= 0:
        return
    with K.at(c, x, y, 0, 1, 1):
        c.save()
        c.concat(skia.Matrix.MakeAll(1, -0.55 * p, 0, 0, -0.42 * p, 0, 0, 0, 1))
        K.figure(c, 0, 0, s, pose, K.SHADOW, K.SHADOW, 0.55 * alpha * p, face, "flat", None, None, 0, 0)
        c.restore()


def compass(c, x, y, r, labels=("思维", "情感", "感觉", "直觉"), hi=None, p=1.0, alpha=1.0, accent=K.GOLD):
    """四种心理功能罗盘：上下一对（思维—情感），左右一对（感觉—直觉）；hi 为高亮的序号。"""
    K.ring(c, x, y, r, K.INK, 5, alpha, p)
    K.seg(c, x, y - r * p, x, y + r * p, K.INK, 5, alpha)
    K.seg(c, x - r * p, y, x + r * p, y, K.INK, 5, alpha)
    pos = ((0, -1), (0, 1), (-1, 0), (1, 0))
    for i, (dx, dy) in enumerate(pos):
        a = clamp01(p * 2 - 0.6 - i * 0.1)
        col = accent if hi == i else K.PAPER
        K.dot(c, x + dx * r, y + dy * r, 70, col, alpha * a)
        K.ring(c, x + dx * r, y + dy * r, 70, K.INK, 4, alpha * a)
        K.text(c, labels[i], x + dx * r, y + dy * r, 36, "serif_black", K.INK, alpha * a)
    K.dot(c, x, y, 16, accent, alpha)


def stopwatch(c, x, y, s, t, run=True, alpha=1.0, color=K.INK, accent=K.RED):
    K.dot(c, x, y - s * 0.62, s * 0.1, color, alpha)
    K.dot(c, x, y, s * 0.5, K.PAPER, alpha)
    K.ring(c, x, y, s * 0.5, color, s * 0.06, alpha)
    for i in range(12):
        a = i / 12 * math.tau
        K.seg(c, x + math.cos(a) * s * 0.38, y + math.sin(a) * s * 0.38, x + math.cos(a) * s * 0.44, y + math.sin(a) * s * 0.44,
              color, s * 0.02, alpha)
    a = (t * 2 if run else 0) - math.pi / 2
    K.seg(c, x, y, x + math.cos(a) * s * 0.38, y + math.sin(a) * s * 0.38, accent, s * 0.035, alpha)
    K.dot(c, x, y, s * 0.04, color, alpha)


def dream_house(c, w, h, depth=1.0, alpha=1.0):
    """梦中的房子：两层楼（意识）、地下室（个人无意识）、地下室下的洞穴（更古老、集体性的层次）。depth 为向下揭开的进度。"""
    fl = h / 4
    rows = [("一楼", "#E8D9BC", "18 世纪的客厅"), ("底层", "#D7C3A0", "中世纪的房间"), ("地下室", "#B49D7C", "古罗马的砖墙"),
            ("洞穴", "#5E5240", "史前的骨骸与陶片")]
    K.poly(c, [(-w / 2 - 30, -h / 2), (0, -h / 2 - 140), (w / 2 + 30, -h / 2)], K.mix(K.RED, K.DARK, 0.3), alpha)
    for i, (_, col, desc) in enumerate(rows):
        k = clamp01(depth * 4 - i)
        if k <= 0:
            continue
        y0 = -h / 2 + i * fl
        K.rr(c, 0, y0 + fl / 2, w, fl, 0, col, alpha * k)
        K.seg(c, -w / 2, y0 + fl, w / 2, y0 + fl, K.INK, 4, alpha * k)
        K.text(c, desc, 0, y0 + fl / 2, 34, "sans_medium", K.PAPER if i == 3 else K.INK, alpha * k)
        if i < 3:
            for sx in range(5):
                K.seg(c, w / 2 - 70 - sx * 18, y0 + fl - sx * (fl / 5), w / 2 - 70 - (sx + 1) * 18, y0 + fl - sx * (fl / 5),
                      K.INK2, 4, alpha * k * 0.7)
    K.rr_stroke(c, 0, 0, w, h, 4, K.INK, 5, alpha)


def scarab(c, x, y, s, alpha=1.0, gold=K.GOLD):
    """圣甲虫（金色甲虫）。"""
    with K.at(c, x, y):
        for sx in (-1, 1):
            for k in range(3):
                K.seg(c, sx * s * 0.25, -s * 0.15 + k * s * 0.22, sx * s * 0.62, -s * 0.3 + k * s * 0.3, K.INK, s * 0.05, alpha)
        path = skia.Path()
        path.addOval(skia.Rect.MakeXYWH(-s * 0.32, -s * 0.38, s * 0.64, s * 0.82))
        c.drawPath(path, K.paint(gold, alpha))
        c.drawPath(path, K.paint(K.INK, alpha, s * 0.03))
        K.seg(c, 0, -s * 0.38, 0, s * 0.44, K.INK, s * 0.03, alpha)
        K.dot(c, 0, -s * 0.48, s * 0.16, K.mix(gold, K.INK, 0.4), alpha)


def sun_moon(c, x, y, r, k=1.0, alpha=1.0):
    """日与月相对：左太阳、右月亮，k 控制两者靠拢的程度（用于阿尼玛 / 阿尼姆斯）。"""
    d = lerp(r * 2.6, r * 1.1, k)
    K.dot(c, x - d / 2, y, r, K.GOLD, alpha)
    for i in range(10):
        a = i / 10 * math.tau
        K.seg(c, x - d / 2 + math.cos(a) * r * 1.2, y + math.sin(a) * r * 1.2, x - d / 2 + math.cos(a) * r * 1.45,
              y + math.sin(a) * r * 1.45, K.GOLD, 6, alpha)
    K.dot(c, x + d / 2, y, r, MOON, alpha)
    K.dot(c, x + d / 2 + r * 0.35, y - r * 0.2, r * 0.82, K.BG, alpha)
    K.ring(c, x + d / 2, y, r, K.INK3, 3, alpha)


GROUND_Y = 1130


def ground(g):
    K.ground(g.c, GROUND_Y)


def cookie_mold(c, g, el_t, d):
    """同一个星形模具压出不同花色的饼干（原型与原型意象的示意）。"""
    k = clamp01(el_t / 0.5)
    with K.at(c, 0, -230 + 40 * math.sin(min(el_t, 3) * 3), 0):
        K.star(c, 0, 0, 110, K.INK3, 1, 5, 0.5)
        K.star(c, 0, 0, 92, K.BG, 1, 5, 0.5)
    cols = (K.GOLD, K.RED, A_TEAL, K.HERO, "#9C8FB0")
    for i, col in enumerate(cols):
        q = ease_out(clamp01((g.since(d.get("b0", 2) + i) + 0.2) / 0.3))
        if q <= 0:
            continue
        x = -340 + i * 170
        K.star(c, x, 140, 70 * q, col, 1, 5, 0.5)
        K.dot(c, x, 140, 14 * q, K.PAPER)


A_TEAL = TEAL


def hero_loop(c, g, el_t, d):
    """英雄之旅示意：从家出发—考验—带着收获回家，一个圆环。"""
    p = ease_in_out(clamp01(el_t / 3.2))
    K.ring(c, 0, 0, 300, K.LINE, 26, 1)
    K.ring(c, 0, 0, 300, d.get("acc", INDIGO), 26, 1, p, 90)
    for a, name, ic in ((90, "家", "house"), (-30, "考验", "shield"), (210, "收获", "gift")):
        r = math.radians(a)
        K.icon(c, ic, math.cos(r) * 300, math.sin(r) * 300, 70, K.INK, 1, 0.8, 0, 1, 1, K.GOLD)
        K.text(c, name, math.cos(r) * 420, math.sin(r) * 380, 36, "serif_black", K.INK)
    a = math.radians(90 + 360 * p)
    K.figure(c, math.cos(a) * 300, math.sin(a) * 300 + 10, 110, "stand", K.HERO, K.SKIN, 1, 1, "smile", "short")


def cane(c, h):
    """手杖道具（Fig 的 prop）：从手部垂到地面。"""
    K.seg(c, h[0], h[1], h[0] + 14, h[1] + 230, K.mix(K.GOLD, K.DARK, 0.5), 12)
    K.dot(c, h[0], h[1] - 6, 12, K.mix(K.GOLD, K.DARK, 0.5))
