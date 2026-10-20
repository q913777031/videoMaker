"""09 射手座：射手座，天上到底长什么样？"""

import math

import skia

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Custom, Label, Shot, Txt

from . import kit_xz as X
from .series import GROUND, episode

AB = "Sgr"
HORSE = "#8C6A4A"
# 南斗六星（J2000 赤经、赤纬，度）：μ、λ、φ、σ、τ、ζ Sgr
NANDOU = [(273.44, -21.06), (276.99, -25.42), (281.41, -26.99), (283.82, -26.30), (286.74, -27.67), (285.65, -29.88)]
SGR_A = (266.42, -29.01)       # 银心黑洞人马座 A*
# 银道面上的几个点（银经 25°、10°、0°、-10°，换算为 J2000 赤经、赤纬）
GAL_PLANE = [(279.22, -7.05), (271.94, -20.29), (266.40, -28.94), (259.87, -37.31)]


def centaur(c, x, y, s, t, draw_k=1.0, alpha=1.0):
    """半人马弓箭手（朝右）：马身、四条腿、人的上半身拉弓；draw_k 为拉弓程度。"""
    for i, (dx, ph) in enumerate(((-0.42, 0.0), (-0.3, 1.6), (0.22, 0.8), (0.34, 2.4))):
        sw = 0.05 * math.sin(t * 4 + ph)
        K.seg(c, x + dx * s, y - 0.3 * s, x + (dx + sw) * s, y, K.shade(HORSE, 0.3), 0.07 * s, alpha)
    K.seg(c, x - 0.5 * s, y - 0.42 * s, x - 0.72 * s, y - 0.22 * s + 0.04 * s * math.sin(t * 3), K.shade(HORSE, 0.4),
          0.06 * s, alpha)
    K.figure(c, x + 0.28 * s, y - 0.32 * s, 0.95 * s, "point", K.HERO, mood="flat", face=1, hair="short", lift=0.8,
             alpha=alpha)
    with K.paper(c, alpha, 0.9):
        K.rr(c, x - 0.04 * s, y - 0.38 * s, 1.0 * s, 0.38 * s, 0.17 * s, HORSE)
    hx, hy = x + 0.28 * s + 0.43 * s, y - 0.32 * s - 0.6 * s
    bend = 0.18 * s
    path = skia.Path()
    path.moveTo(hx - 0.05 * s, hy - 0.3 * s)
    path.quadTo(hx + bend, hy, hx - 0.05 * s, hy + 0.3 * s)
    c.drawPath(path, K.paint(K.shade(HORSE, 0.45), alpha, 0.03 * s))
    pull = 0.16 * s * draw_k
    K.seg(c, hx - 0.05 * s, hy - 0.3 * s, hx - 0.05 * s - pull, hy, K.INK3, 3, alpha)
    K.seg(c, hx - 0.05 * s, hy + 0.3 * s, hx - 0.05 * s - pull, hy, K.INK3, 3, alpha)
    K.arrow(c, (hx - 0.05 * s - pull, hy), (hx + 0.32 * s, hy), K.INK, 6, alpha, 1, 0, 18)


def archer(c, g, t, d):
    """半人马拉满弓（第 4 拍拉满），箭头指向右边的“天蝎之心”。"""
    k = ease_out(clamp01(g.since(2) / (g.b(4) - g.b(2) + 1e-6)))
    centaur(c, -60, 330, 420, g.t, k)
    q = clamp01(g.since(6) / 0.35)
    if q > 0:
        K.spotlight(c, 400, -60, 120 * q, "#FF7A50", 0.5 * q)
        K.heart(c, 400, -60, 90 * (0.4 + 0.6 * K.ease_out_back(q, 1.8)), "#C9473C", q)
        K.text(c, "天蝎之心 · 心宿二", 380, -170, 30, "sans_medium", K.INK2, q)


def ground(g):
    K.ground(g.c, GROUND)


def nandou(c, g, t, d):
    """射手座星图：南斗六星按拍逐颗亮起并连成勺子形。"""
    def extra(c, P):
        pts = [P(*q) for q in NANDOU]
        for i, (px, py) in enumerate(pts):
            k = clamp01(g.since(0.5 + i * 0.5) / 0.25)
            if k > 0:
                K.spotlight(c, px, py, 60 * k, "#FFE7A8", 0.5 * k)
                K.dot(c, px, py, 9, "#FFFFFF", k)
        kk = clamp01(g.since(4) / 0.4)
        if kk > 0:
            for a, b in zip(pts, pts[1:]):
                K.seg(c, a[0], a[1], a[0] + (b[0] - a[0]) * kk, a[1] + (b[1] - a[1]) * kk, "#FF9F80", 6)
            cx = sum(p[0] for p in pts) / len(pts)
            cy = min(p[1] for p in pts)
            K.text(c, "南斗六星", cx, cy - 70, 48, "serif_black", "#FFC9B8", kk)
    X.sky_card(c, 0, 0, 900, 660, AB, 1, g.t, 1, line_color=X.FAINT, margin=110, extra=extra)


def galactic_center(c, g, t, d):
    """星图上淡淡的银河带穿过射手座西侧；第 1 拍标出银心，第 2 拍弹出黑洞照片示意（2022）。"""
    def extra(c, P):
        pts = [P(*q) for q in GAL_PLANE]
        path = skia.Path()
        path.moveTo(*pts[0])
        for q in pts[1:]:
            path.lineTo(*q)
        p = K.paint("#D8D2F0", 0.22, 150)
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 40))
        p.setStrokeCap(skia.Paint.kRound_Cap)
        c.drawPath(path, p)
        px, py = P(*SGR_A)
        k = clamp01(g.since(1) / 0.3)
        if k > 0:
            K.ring(c, px, py, 24 + 12 * (1 - k), "#FF9F80", 5, k)
            K.text(c, "银河系中心", px, py - 56, 32, "sans_medium", "#FFC9B8", k)
        q = clamp01(g.since(2) / 0.4)
        if q > 0:
            ix, iy = 300, 175
            K.seg(c, px, py, px + (ix - px) * q, py + (iy - py) * q, "#FF9F80", 3, q)
            with K.at(c, ix, iy, 0, 0.8 * (0.3 + 0.7 * K.ease_out_back(q, 1.6))):
                K.dot(c, 0, 0, 110, "#0B0B12", q)
                sh = skia.GradientShader.MakeSweep(0, 0, [K.col("#FFB347", q), K.col("#8A2B0E", q), K.col("#FFD27A", q),
                                                          K.col("#FFB347", q)], [0, 0.4, 0.75, 1])
                pp = skia.Paint(AntiAlias=True, Shader=sh, Style=skia.Paint.kStroke_Style, StrokeWidth=30)
                pp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8))
                c.drawCircle(0, 0, 60, pp)
                K.dot(c, 0, 0, 40, "#050508", q)
                K.text(c, "人马座 A* · 2022", 0, 140, 32, "sans_medium", "#FFC9B8", q)
    X.sky_card(c, 0, 0, 900, 660, AB, 1, g.t, 1, line_color=X.FAINT, margin=170, extra=extra)


def build():
    mid = [
        Shot(3, "神话里，半人马拉满弓，|瞄准天蝎的心脏。", "希腊神话", [
            Custom(archer, x=540, y=760, at=0, enter="fade"),
            Label("半人马弓箭手", 300, 470, 32, at=1, fill=HORSE, sfx="wood_high", note="名字标签"),
        ], draw=ground, hits=[(4, "rim", 0.9, "弓拉满"), (6, "bongo_low", 0.85, "天蝎之心亮起")],
            note="半人马弓箭手慢慢拉满弓，第 6 拍右边亮起“天蝎之心”（心宿二）"),
        Shot(2, "“南斗六星”，|就在射手座。", "中国星官", [
            Custom(nandou, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.7, "南斗第二颗亮起"), (3, "wood_low", 0.7, "南斗第六颗亮起"),
                 (4, "rim", 0.85, "连成勺子")], text_beat=0,
            note="射手座星图：南斗六星（μ、λ、φ、σ、τ、ζ）逐颗亮起，第 4 拍连成勺子形"),
        Shot(2, "射手座方向，|就是银河系中心。", "天文观测", [
            Custom(galactic_center, x=540, y=800, at=0, enter="fade"),
            Txt("2022 年，人类拍到了这里的黑洞", 540, 1240, 28, at=2, font="sans_medium", color=K.INK2),
        ], hits=[(1, "wood_low", 0.8, "银心圈出"), (2, "bongo_high", 0.85, "黑洞照片示意弹出")], text_beat=0,
            note="淡淡的银河带穿过射手座西侧，圈出银河系中心，弹出人马座 A* 黑洞照片示意（2022）"),
    ]
    return episode(
        9, AB, "射手座：|最好认的是一把“茶壶”。", mid,
        refs=["阿拉托斯《物象》", "EHT 合作组（2022），ApJL 930, L12"],
        notes=[
            "按 IAU 边界计算（2026 年），占星射手座日期 11 月 22 日前后至 12 月 21 日里，太阳在蛇夫座 18 天、天蝎座 7 天、"
            "射手座只有 3 天；蛇夫座是太阳每年都会经过、但不在占星十二宫里的星座。",
            "神话版本不一：射手座通常画成拉弓的半人马，箭指天蝎座的心脏（心宿二）；有的说法认作喀戎，有的认作羊人克洛托斯。",
            "射手座最好认的部分是由八颗星组成的“茶壶”星群；天文学正式中文名为“人马座”。",
            "南斗六星即斗宿六星，对应射手座 μ、λ、φ、σ、τ、ζ。",
            "银河系中心位于射手座方向，距离约 2.6 万光年。2022 年 5 月，事件视界望远镜（EHT）发布银心黑洞人马座 A* 的第一张照片。"
            "片中光环为示意画，不是原始图像。",
        ],
        hashtags="#射手座 #星座 #天文 #科普 #银河系",
        cover_title="生日在射手座，|太阳却在【蛇夫座】？", cover_sub="射手座：天上到底长什么样")
