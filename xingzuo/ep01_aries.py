"""01 白羊座：白羊座，天上到底长什么样？"""

import math

import skia

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Custom, Label, Shot

from . import kit_xz as X
from .series import episode

AB = "Ari"
GOLDEN = "#E3B04B"


def ram(c, x, y, s, t, alpha=1.0):
    """金毛公羊剪影：卷毛身体、弯角、细腿（以身体中心为原点，朝右）。"""
    with K.at(c, x, y, 0, s / 300):
        with K.paper(c, alpha, 1.0):
            for dx, dy, r in ((-80, -10, 70), (-20, -30, 74), (40, -16, 70), (0, 30, 66), (-70, 34, 56), (60, 30, 58)):
                K.dot(c, dx, dy, r, GOLDEN)
            for i, (dx, dy) in enumerate(((-110, 50), (-60, 60), (40, 62), (90, 52))):
                leg = 10 * math.sin(t * 9 + i * 1.7)
                K.seg(c, dx, dy, dx + leg, dy + 90, K.shade(GOLDEN, 0.35), 18)
            K.dot(c, 120, -60, 48, K.mix(GOLDEN, K.PAPER, 0.25))
            K.dot(c, 150, -48, 30, K.mix(GOLDEN, K.PAPER, 0.35))
            K.ring(c, 104, -84, 30, K.shade(GOLDEN, 0.3), 14, 1, 0.85, 200)
            K.dot(c, 134, -66, 6, K.INK)
        for i in range(5):
            a = t * 2 + i
            K.dot(c, -140 - 20 * i, 60 + 10 * math.sin(a), 8 - i, GOLDEN, 0.5 * alpha)


def golden_ram(c, g, t, d):
    """金毛公羊驮着两个孩子飞过大海；第 6 拍身后闪出金光。"""
    fly = ease_in_out(clamp01(g.t / max(0.1, g.dur - 0.3)))
    x = -260 + 420 * fly
    y = -40 * math.sin(fly * math.pi) + 12 * math.sin(g.t * 3)
    for i in range(4):
        wy = 310 + i * 26
        path = skia.Path()
        path.moveTo(-520, wy)
        for j in range(27):
            px = -520 + j * 40
            path.lineTo(px, wy + 10 * math.sin(j * 0.9 + g.t * 2 + i))
        c.drawPath(path, K.paint(K.mix("#5B8FB0", K.PAPER, 0.25 + 0.15 * i), 1, 6))
    k = clamp01(g.since(6) / 0.5)
    if k > 0:
        K.spotlight(c, x, y, 360 * k, K.GOLD, 0.35 * (1 - 0.4 * k))
    K.figure(c, x - 40, y - 50, 120, "sit", K.HERO, hair="short", mood="happy", lift=0.5)
    K.figure(c, x + 20, y - 52, 112, "sit", K.OTHER3, hair="long", mood="worried", lift=0.5)
    ram(c, x, y, 330, g.t)


def first_point(c, g, t, d):
    """白羊座星图 + 古希腊时期春分点：第 2 拍红色标记落下。

    约公元前 100 年的春分点，在 J2000 坐标里黄经约 29.3°（2100 年 × 每年 50.3″），换算为赤经 27.2°、赤纬 +11.2°。
    """
    def extra(c, P):
        k = clamp01(g.since(2) / 0.35)
        if k <= 0:
            return
        px, py = P(27.2, 11.2)
        K.ring(c, px, py, 26 + 20 * (1 - k), K.RED, 7, k)
        K.dot(c, px, py, 8, K.RED, k)
        K.text(c, "古希腊时期的春分点", px, py + 60, 30, "sans_medium", "#FFC9B8", k)
    X.sky_card(c, 0, 0, 900, 640, AB, 1, g.t, 1, margin=170, extra=extra)


def lou_xiu(c, g, t, d):
    """娄宿：白羊座最亮的三颗星依次亮起，连成中国星官“娄宿”。"""
    named = {n["en"]: n for n in X.sign(AB)["named"]}
    trio = [named.get("Hamal"), named.get("Sheratan"), named.get("Mesarthim")]

    def extra(c, P):
        pts = []
        for i, st in enumerate(trio):
            if not st:
                continue
            k = clamp01(g.since(1 + i) / 0.3)
            px, py = P(st["ra"], st["dec"])
            pts.append((px, py))
            if k > 0:
                K.spotlight(c, px, py, 70 * k, "#FFE7A8", 0.5 * k)
                K.dot(c, px, py, 9, "#FFFFFF", k)
        if len(pts) >= 2 and g.since(4) >= 0:
            kk = clamp01(g.since(4) / 0.4)
            for a, b in zip(pts, pts[1:]):
                K.seg(c, a[0], a[1], a[0] + (b[0] - a[0]) * kk, a[1] + (b[1] - a[1]) * kk, "#FF9F80", 6, 1)
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            K.text(c, "娄宿", cx + 40, cy - 110, 52, "serif_black", "#FFC9B8", kk)
    X.sky_card(c, 0, 0, 900, 640, AB, 1, g.t, 1, line_color=X.FAINT, extra=extra)


def build():
    mid = [
        Shot(3, "希腊神话里，|它是驮人飞走的金毛公羊。", "希腊神话", [
            Custom(golden_ram, x=540, y=760, at=0, enter="fade"),
            Label("佛里克索斯", 250, 450, 30, at=2, fill=K.HERO, sfx="wood_high", note="哥哥佛里克索斯"),
            Label("赫勒", 820, 450, 30, at=3, fill=K.OTHER3, sfx="wood_low", note="妹妹赫勒"),
        ], hits=[(6, "cymbal", 0.6, "金羊毛闪光")],
            note="金毛公羊驮着兄妹二人飞越大海，第 6 拍身后闪出金光（金羊毛）"),
        Shot(2, "春分点，至今仍叫|“白羊座第一点”。", "天文观测", [
            Custom(first_point, x=540, y=800, at=0, enter="fade"),
        ], hits=[(2, "rim", 0.9, "春分点标记落下")], text_beat=0,
            note="白羊座星图边上落下红色春分点标记：古希腊时代春分点在白羊座附近"),
        Shot(2, "最亮的三颗星，|在中国叫“娄宿”。", "中国星官", [
            Custom(lou_xiu, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.8, "娄宿三亮起"), (2, "wood_low", 0.8, "娄宿一亮起"), (3, "bongo_high", 0.8, "娄宿二亮起")],
            text_beat=0, note="白羊座最亮的三颗星按拍依次亮起，连成一条短线，标“娄宿”"),
    ]
    return episode(
        1, AB, "白羊座：|几颗星连成一条弯线。", mid,
        refs=["阿波罗多洛斯《书库》第 1 卷（佛里克索斯与金羊毛）"],
        notes=[
            "金毛公羊的故事：佛里克索斯和赫勒为躲避继母伊诺，骑会飞的金毛公羊出逃，赫勒途中落海（赫勒斯滂海峡因此得名），"
            "公羊的金羊毛后来成为伊阿宋寻找的宝物。神话版本不一。",
            "春分点的英文名 First Point of Aries（白羊座第一点）沿用自古希腊时代；按 IAU 边界，春分点约在公元前 68 年移入双鱼座，"
            "约 2597 年移入宝瓶座（Meeus 的计算，EarthSky 转述）。",
            "娄宿是二十八宿之一，娄宿一、二、三即白羊座 β、γ、α。",
        ],
        hashtags="#白羊座 #星座 #天文 #科普 #星空",
        cover_title="生日在白羊座，|太阳却在【双鱼座】？", cover_sub="白羊座：天上到底长什么样")
