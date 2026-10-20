"""02 金牛座：金牛座，天上到底长什么样？"""

import math

import skia

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Custom, Label, Shot

from . import kit_xz as X
from .series import episode

AB = "Tau"
BULL = "#F4EEE2"
SEA = "#5B8FB0"
# 毕宿星团中心（J2000，度）
HYADES = (66.75, 15.87)
# 天关 = 金牛座 ζ；蟹状星云 M1（J2000，度）
TIANGUAN = (84.41, 21.14)
M1 = (83.63, 22.01)


def waves(c, t, y0=310, w=520):
    for i in range(4):
        wy = y0 + i * 26
        path = skia.Path()
        path.moveTo(-w, wy)
        for j in range(int(2 * w / 40) + 1):
            path.lineTo(-w + j * 40, wy + 10 * math.sin(j * 0.9 + t * 2 + i))
        c.drawPath(path, K.paint(K.mix(SEA, K.PAPER, 0.25 + 0.15 * i), 1, 6))


def bull(c, x, y, s, t, alpha=1.0):
    """白色公牛剪影（朝右游水）：身体、牛头、弯角、前腿划水。"""
    with K.at(c, x, y, 0, s / 300):
        with K.paper(c, alpha, 1.0):
            K.rr(c, -10, 0, 300, 140, 70, BULL)
            for i, dx in enumerate((-110, 90)):
                leg = 22 * math.sin(t * 6 + i * 2.1)
                K.seg(c, dx, 40, dx + 30 + leg, 120, K.shade(BULL, 0.18), 22)
            K.rr(c, 150, -55, 110, 90, 40, BULL)
            K.rr(c, 195, -30, 50, 44, 20, K.mix(BULL, "#E8C9B4", 0.6))
            for sgn in (-1, 1):
                p = skia.Path()
                p.moveTo(140 + 22 * sgn, -92)
                p.quadTo(130 + 50 * sgn, -150, 165 + 36 * sgn, -170)
                c.drawPath(p, K.paint("#D9C29A", 1, 12))
            K.dot(c, 178, -66, 6, K.INK)
            p = skia.Path()
            p.moveTo(-160, -10)
            p.quadTo(-210, -40, -220, 10)
            c.drawPath(p, K.paint(K.shade(BULL, 0.2), 1, 8))


def europa_bull(c, g, t, d):
    """白牛驮着欧罗巴游过大海；第 6 拍水花溅起。"""
    sw = ease_in_out(clamp01(g.t / max(0.1, g.dur - 0.3)))
    x = -200 + 340 * sw
    y = 140 + 10 * math.sin(g.t * 2.4)
    waves(c, g.t, 230)
    K.figure(c, x - 10, y - 86, 200, "sit", "#B4566E", hair="long", mood="surprised", lift=0.5)
    bull(c, x, y, 400, g.t)
    k = g.since(6)
    if 0 <= k < 0.7:
        for i in range(8):
            a = -math.pi * (0.15 + 0.7 * i / 7)
            r = 40 + 200 * k
            K.dot(c, x - 120 + r * math.cos(a), y + 60 + r * math.sin(a), 10 * (1 - k), SEA, 1 - k / 0.7)
    waves(c, g.t + 1, 330)


def hyades(c, g, t, d):
    """毕宿星团与昴星团圈出；毕宿五单独标近。"""
    s = X.sign(AB)
    named = {n["en"]: n for n in s["named"]}
    ald = named["Aldebaran"]
    alc = named["Alcyone"]

    def extra(c, P):
        k1 = clamp01(g.since(1) / 0.35)
        if k1 > 0:
            px, py = P(*HYADES)
            K.ring(c, px, py, 130, "#9FC3E8", 5, k1, k1)
            K.text(c, "毕宿星团 约150光年", px - 10, py + 165, 30, "sans_medium", "#C9DDF2", k1)
        k2 = clamp01(g.since(2) / 0.35)
        if k2 > 0:
            px, py = P(alc["ra"], alc["dec"])
            K.ring(c, px, py, 60, "#9FC3E8", 5, k2, k2)
            K.text(c, "昴星团", px, py - 85, 30, "sans_medium", "#C9DDF2", k2)
        k3 = clamp01(g.since(4) / 0.35)
        if k3 > 0:
            px, py = P(ald["ra"], ald["dec"])
            K.spotlight(c, px, py, 90 * k3, "#FFB98A", 0.6 * k3)
            K.dot(c, px, py, 11, "#FFD2B0", k3)
            K.text(c, "毕宿五", px - 150, py - 22, 36, "serif_black", "#FFD2B0", k3, "right")
            K.text(c, "约65光年", px - 150, py + 26, 30, "sans_medium", "#FFD2B0", k3, "right")
    X.sky_card(c, 0, 0, 900, 660, AB, 1, g.t, 1, line_color=X.FAINT, margin=80, extra=extra)


def guest_star(c, g, t, d):
    """天关旁边的客星：第 1 拍亮起，第 4 拍淡成蟹状星云。"""
    def extra(c, P):
        tx, ty = P(*TIANGUAN)
        K.ring(c, tx, ty, 22, "#9FC3E8", 4, 0.9)
        K.text(c, "天关", tx, ty + 60, 32, "serif_black", "#C9DDF2", 1)
        mx, my = P(*M1)
        k = clamp01(g.since(1) / 0.25)
        fade = clamp01(g.since(4) / 0.6)
        if k > 0:
            K.spotlight(c, mx, my, 160 * k * (1 - fade) + 10, "#FFF2C0", 0.8 * k * (1 - fade))
            K.dot(c, mx, my, 16 * k * (1 - fade) + 0.1, "#FFFFFF", (1 - fade))
            K.text(c, "1054 年 客星", mx + 10, my + 145, 34, "serif_black", "#FFE7A8", k * (1 - fade))
        if fade > 0:
            for i, (dx, dy, r) in enumerate(((0, 0, 30), (14, -8, 22), (-12, 10, 20), (8, 14, 16))):
                K.dot(c, mx + dx, my + dy, r, ("#E98A6A", "#F2C46B", "#8FB7E0", "#E98A6A")[i], 0.45 * fade)
            K.text(c, "蟹状星云 M1", mx + 10, my + 145, 34, "serif_black", "#FFC9B8", fade)
    X.sky_card(c, 0, 0, 900, 660, AB, 1, g.t, 1, line_color=X.FAINT, margin=130, extra=extra)


def build():
    mid = [
        Shot(3, "希腊神话里，宙斯|化作白牛驮走欧罗巴。", "希腊神话", [
            Custom(europa_bull, x=540, y=720, at=0, enter="fade"),
            Label("欧罗巴", 330, 500, 30, at=2, fill="#B4566E", sfx="wood_high", note="欧罗巴"),
            Label("宙斯化身的白牛", 760, 520, 30, at=3, fill=K.INK2, sfx="wood_low", note="白牛"),
        ], hits=[(6, "shaker", 0.7, "水花溅起")],
            note="白牛驮着欧罗巴从左向右游过大海，第 6 拍溅起水花"),
        Shot(2, "毕宿五看着在星团里，|其实近得多。", "天文观测", [
            Custom(hyades, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.8, "圈出毕宿星团"), (2, "wood_low", 0.8, "圈出昴星团"), (4, "rim", 0.9, "毕宿五单独亮起")],
            text_beat=0, note="星图上圈出毕宿星团（约 150 光年）和昴星团，毕宿五单独亮起并标“约 65 光年”"),
        Shot(2, "宋人记下的“客星”，|如今是蟹状星云。", "中国星官", [
            Custom(guest_star, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "cymbal", 0.7, "客星亮起"), (4, "rim", 0.8, "客星淡成星云")],
            text_beat=0, note="天关星旁，第 1 拍“1054 年客星”亮起，第 4 拍淡成彩色的蟹状星云 M1"),
    ]
    return episode(
        2, AB, "金牛座：|一个 V 字是牛脸。", mid,
        refs=["奥维德《变形记》第 2 卷；《宋史·天文志》（天关客星）"],
        notes=[
            "白牛与欧罗巴：宙斯化作白色公牛，驮着腓尼基公主欧罗巴渡海到克里特岛。神话版本不一。",
            "毕宿五（Aldebaran）看上去位于毕宿星团的 V 字上，实际距离约 65 光年，毕宿星团约 150 光年，它只是恰好在同一视线方向，"
            "不是星团成员。昴星团（Pleiades）也在金牛座。",
            "1054 年（宋至和元年），宋代史书记载天关星附近出现“客星”，白天都能看见，一年多后才消失；这次超新星爆发的遗迹即蟹状星云 M1"
            "（1942 年前后由奥尔特等人确认）。片中星云为示意图形。",
        ],
        hashtags="#金牛座 #星座 #天文 #科普 #星空",
        cover_title="生日在金牛座，|太阳却在【白羊座】？", cover_sub="金牛座：天上到底长什么样")
