"""MBTI 系列的专用绘图元件：字母牌、偏好量尺、分布曲线、测试卡、报告纸、电量、胸牌。

全部沿用 adler.kit 的纸片风格（暖白纸底、柔和投影、手绘感圆角），坐标以元件中心为原点。
"""

import math

import skia

from adler import kit as K
from engine import gfx
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

# 四个维度的配色：每对字母共用一个色相，左字母深、右字母浅
DIM = {
    "E": "#D9783F", "I": "#B8673A",
    "S": "#5E9A6A", "N": "#4C8577",
    "T": "#4E78A8", "F": "#C8566E",
    "J": "#C99A2E", "P": "#9A7BB0",
}
PAIRS = (("E", "I"), ("S", "N"), ("T", "F"), ("J", "P"))
PAIR_NAMES = {"E": "外向", "I": "内向", "S": "实感", "N": "直觉", "T": "思考", "F": "情感", "J": "判断", "P": "知觉"}


def tile(c, x, y, s, ch, color=None, alpha=1.0, flip=1.0, rot=0.0, scale=1.0, sub=None, glow=0.0):
    """字母牌：圆角纸片 + 大写字母；flip 为横向翻转系数（1 正面，0 侧面），sub 为牌下小字。"""
    if alpha <= 0 or scale <= 0:
        return
    color = color or DIM.get(ch, K.INK)
    if glow > 0:
        K.spotlight(c, x, y, s * 1.2, K.GOLD, 0.45 * glow * alpha)
    with K.at(c, x, y, rot, scale):
        c.save()
        c.scale(max(0.02, abs(flip)), 1)
        with K.paper(c, alpha, 0.9, skia.Rect.MakeXYWH(-s, -s, 2 * s, 2 * s)):
            K.rr(c, 0, 0, s, s, s * 0.18, color)
            K.rr(c, 0, -s * 0.36, s * 0.82, s * 0.06, s * 0.03, K.mix(color, K.PAPER, 0.35))
            if flip > 0:
                K.text(c, ch, 0, s * 0.04, s * 0.62, "black", K.PAPER)
        c.restore()
        if sub:
            K.text(c, sub, 0, s * 0.5 + max(26, s * 0.28) * 0.8, max(26, s * 0.28), "sans_medium", K.INK2, alpha)


def code(c, x, y, s, letters, alpha=1.0, gap=0.18, prog=None, subs=False, glow=None):
    """一排四字母牌；prog[i] 为每张牌的入场进度（0–1，弹出），glow[i] 为高亮。"""
    n = len(letters)
    w = n * s + (n - 1) * s * gap
    for i, ch in enumerate(letters):
        k = 1.0 if prog is None else prog[i]
        if k <= 0:
            continue
        px = x - w / 2 + s / 2 + i * s * (1 + gap)
        tile(c, px, y, s, ch, None, alpha * clamp01(k * 3), 1.0, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8),
             PAIR_NAMES.get(ch) if subs else None, glow[i] if glow else 0.0)


def scale_bar(c, x, y, w, left, right, pos, alpha=1.0, color=None, size=60, knob=True, ticks=True, names=True):
    """偏好量尺：两端字母牌，中间刻度线，滑块在 pos（-1 左端，1 右端）。"""
    lc, rc = DIM.get(left, K.INK2), DIM.get(right, K.INK2)
    half = w / 2
    with K.fade(c, alpha):
        K.seg(c, x - half + size * 0.8, y, x + half - size * 0.8, y, K.LINE, 12)
        if ticks:
            for i in range(-4, 5):
                tx = x + i * (half - size * 0.8) / 4
                K.seg(c, tx, y - (16 if i == 0 else 9), tx, y + (16 if i == 0 else 9), K.INK3 if i == 0 else K.LINE, 4)
        tile(c, x - half + size / 2, y, size, left, lc, 1, sub=PAIR_NAMES.get(left) if names else None)
        tile(c, x + half - size / 2, y, size, right, rc, 1, sub=PAIR_NAMES.get(right) if names else None)
        if knob:
            kx = x + pos * (half - size * 0.8)
            kc = K.mix(lc, rc, (pos + 1) / 2)
            with K.paper(c, 1, 0.9):
                K.dot(c, kx, y, size * 0.34, K.PAPER)
            K.ring(c, kx, y, size * 0.34, kc, 8)
            K.dot(c, kx, y, size * 0.13, kc)


def bell(c, x, y, w, h, p=1.0, color=K.HERO, alpha=1.0, mid=False, mid_p=1.0, fill=True, mu=0.0, sd=0.42, bars=0):
    """单峰钟形曲线：(x, y) 为底边中点；p 为从左到右的绘制进度；mid 画中线切分；bars>0 画直方柱。"""
    n = 80
    pts = []
    for i in range(n + 1):
        u = -1 + 2 * i / n
        v = math.exp(-((u - mu) / sd) ** 2 / 2)
        pts.append((x + u * w / 2, y - v * h))
    m = max(1, int(round(n * clamp01(p))))
    with K.fade(c, alpha):
        K.seg(c, x - w / 2 - 20, y, x + w / 2 + 20, y, K.INK3, 5)
        if bars:
            bw = w / bars
            for i in range(bars):
                u = -1 + (i + 0.5) * 2 / bars
                if (u + 1) / 2 > p:
                    break
                v = math.exp(-((u - mu) / sd) ** 2 / 2)
                K.rr(c, x - w / 2 + (i + 0.5) * bw, y - v * h / 2, bw * 0.8, max(1, v * h), 6, K.tint(color, 0.45))
        path = skia.Path()
        path.moveTo(*pts[0])
        for q in pts[1:m + 1]:
            path.lineTo(*q)
        if fill and not bars:
            fp = skia.Path(path)
            fp.lineTo(pts[m][0], y)
            fp.lineTo(pts[0][0], y)
            fp.close()
            c.drawPath(fp, K.paint(K.tint(color, 0.5), 0.55))
        c.drawPath(path, K.paint(color, 1, 9))
        if mid and mid_p > 0:
            top = y - h * 1.15
            K.seg(c, x, y + 20, x, lerp(y + 20, top, ease_out(clamp01(mid_p))), K.RED, 7, 1, 1)


def battery(c, x, y, s, level, color=K.GREEN, alpha=1.0):
    """电量：竖放电池，level 0–1；低电量变红。"""
    w, h = s * 0.55, s
    col = K.mix(K.RED, color, clamp01((level - 0.15) / 0.35))
    with K.paper(c, alpha, 0.9):
        K.rr(c, x, y, w, h, s * 0.08, K.DARK)
        K.rr(c, x, y - h / 2 - s * 0.04, w * 0.4, s * 0.1, s * 0.03, K.DARK)
    inner_h = (h - s * 0.12) * clamp01(level)
    if inner_h > 1:
        K.rr(c, x, y + (h - s * 0.12) / 2 - inner_h / 2, w - s * 0.12, inner_h, s * 0.05, col, alpha)


def quiz(c, x, y, w, question, options, checked=(), alpha=1.0, size=36, accent=K.HERO):
    """测试题卡：题干 + 若干选项；checked 为已勾选选项的 (下标, 进度)。"""
    lines = question.split("|")
    h = size * 1.5 * len(lines) + len(options) * size * 1.9 + size * 2.0

    def draw(c, w_, h_):
        top = -h_ / 2 + size * 1.5
        for i, ln in enumerate(lines):
            K.text(c, ln, -w_ / 2 + size * 0.9, top + i * size * 1.5, size, "serif_black", K.INK, 1, "left")
        oy = top + len(lines) * size * 1.5 + size * 0.5
        for i, op in enumerate(options):
            yy = oy + i * size * 1.9
            K.rr_stroke(c, -w_ / 2 + size * 1.3, yy, size * 0.9, size * 0.9, 8, K.INK3, 4)
            K.text(c, op, -w_ / 2 + size * 2.2, yy, size * 0.9, "sans_medium", K.INK2, 1, "left")
            for j, k in checked:
                if j == i and k > 0:
                    K.rr(c, -w_ / 2 + size * 1.3, yy, size * 0.62 * ease_out(k), size * 0.62 * ease_out(k), 6, accent)

    K.card(c, x, y, w, h, K.PAPER, alpha, 22, 1.0, 0, 1, accent, draw)
    return h


def report(c, x, y, w, lines, hi=(), alpha=1.0, size=34, title="你的人格报告", accent=K.HERO, nods=()):
    """报告纸：标题 + 若干行描述；hi 为 (行号, 高亮进度)；nods 为行尾打勾进度。"""
    h = size * 2.2 + len(lines) * size * 1.75 + size * 1.0

    def draw(c, w_, h_):
        top = -h_ / 2 + size * 1.3
        K.text(c, title, 0, top, size * 1.1, "serif_black", K.INK)
        K.seg(c, -w_ / 2 + 40, top + size * 0.9, w_ / 2 - 40, top + size * 0.9, K.LINE, 3)
        for i, ln in enumerate(lines):
            yy = top + size * 2.1 + i * size * 1.75
            for j, k in hi:
                if j == i and k > 0:
                    tw = K.text_w(ln, size, "serif")
                    K.rr(c, -w_ / 2 + 40 + tw * k / 2, yy + size * 0.12, tw * k + 10, size * 0.42, 8,
                         K.tint(accent, 0.55), 0.9)
            K.text(c, ln, -w_ / 2 + 40, yy, size, "serif", K.INK, 1, "left")
            for j, k in nods:
                if j == i and k > 0:
                    with K.at(c, w_ / 2 - 50, yy, 0, 0.3 + 0.7 * K.ease_out_back(k, 2)):
                        K.icon(c, "check", 0, 0, size * 1.1, K.GREEN, clamp01(k * 3), 0.4)

    K.card(c, x, y, w, h, K.PAPER, alpha, 22, 1.0, 0, 1, accent, draw)
    return h


def tag(c, x, y, s, text, color=K.HERO, alpha=1.0, rot=0.0, scale=1.0):
    """胸牌 / 标签贴纸：带小孔的圆角牌。"""
    if alpha <= 0 or scale <= 0:
        return
    w = K.text_w(text, s * 0.5, "black") + s * 0.7
    with K.at(c, x, y, rot, scale):
        with K.paper(c, alpha, 0.8):
            K.rr(c, 0, 0, w, s * 0.8, s * 0.16, color)
            K.dot(c, -w / 2 + s * 0.2, 0, s * 0.08, K.PAPER)
            K.text(c, text, s * 0.08, s * 0.02, s * 0.5, "black", K.PAPER)


def signature(c, x, y, w, wobble=0.0, p=1.0, color=K.INK, width=7, seed=1):
    """一笔签名：wobble 越大越歪扭（用来对比惯用手和非惯用手）。"""
    import numpy as np

    rng = np.random.default_rng(seed)
    n = 60
    path = skia.Path()
    m = max(2, int(n * clamp01(p)))
    for i in range(m):
        u = i / (n - 1)
        px = x - w / 2 + u * w
        py = y + math.sin(u * 14) * 26 * (1 - u * 0.3) + math.sin(u * 5 + 1) * 12
        if wobble:
            py += rng.normal(0, 9 * wobble)
            px += rng.normal(0, 5 * wobble)
        (path.moveTo if i == 0 else path.lineTo)(px, py)
    c.drawPath(path, K.paint(color, 1, width))


def stamp(c, x, y, s, text, color=K.RED, alpha=1.0, k=1.0, rot=-12):
    """年份印章：k 为盖下进度（1.6 倍 → 1 倍）。"""
    if k <= 0 or alpha <= 0:
        return
    sc = 1 + 0.6 * (1 - ease_out(clamp01(k)))
    a = alpha * clamp01(k * 3)
    with K.at(c, x, y, rot, sc):
        w = K.text_w(text, s * 0.42, "black") + s * 0.5
        K.rr_stroke(c, 0, 0, w, s * 0.7, s * 0.12, color, s * 0.06, a)
        K.text(c, text, 0, s * 0.02, s * 0.42, "black", color, a)


def wiggle(g, k0, settle, amp=1.0, f=7.0):
    """量尺滑块的犹豫：从第 k0 拍开始左右摆动，第 settle 拍停在目标位置；返回 (偏移, 是否已停)。"""
    t = g.since(k0)
    if t < 0:
        return 0.0, False
    if g.since(settle) >= 0:
        return 0.0, True
    return amp * math.sin(t * f) * math.exp(-t * 0.3), False


def book(c, x, y, s, title, color, alpha=1.0, sub=None, rot=0.0, scale=1.0):
    """一本书（封面朝外）：title 竖排或横排短书名。"""
    w, h = s * 0.72, s
    with K.at(c, x, y, rot, scale):
        with K.paper(c, alpha, 1.0):
            K.rr(c, 0, 0, w, h, s * 0.04, color)
            K.rr(c, -w / 2 + s * 0.05, 0, s * 0.06, h, 2, K.shade(color, 0.25))
            K.rr_stroke(c, s * 0.03, -h * 0.12, w * 0.7, h * 0.42, 6, K.mix(color, K.GOLD, 0.6), 4)
        lines = title.split("|")
        for i, ln in enumerate(lines):
            K.text(c, ln, s * 0.03, -h * 0.12 + (i - (len(lines) - 1) / 2) * s * 0.13, s * 0.11, "serif_black",
                   K.PAPER, alpha)
        if sub:
            K.text(c, sub, s * 0.03, h * 0.3, s * 0.065, "sans_medium", K.mix(color, K.PAPER, 0.7), alpha)


def pulse(g, beats, amt=0.12, dur=0.3):
    """在若干拍上的弹跳缩放系数。"""
    v = 1.0
    for b in beats:
        q = g.since(b)
        if 0 <= q < dur:
            v += amt * math.sin(q / dur * math.pi)
    return v


def appear(g, k, dur=0.35):
    """第 k 拍开始的弹出进度 0–1。"""
    return clamp01(g.since(k) / dur)


def rich(c, s, x, y, size, color=K.INK, hi=None, alpha=1.0, font="serif", align="center"):
    gfx.draw_rich(c, s, x, y, size, font, color, hi or K.RED, alpha, align)


__all__ = ["DIM", "PAIRS", "PAIR_NAMES", "tile", "code", "scale_bar", "bell", "battery", "quiz", "report", "tag",
           "signature", "stamp", "wiggle", "book", "pulse", "appear", "rich", "ease_in_out", "lerp"]
