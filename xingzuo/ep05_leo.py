"""05 狮子座：狮子座，天上到底长什么样？"""

import math

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Custom, Label, Shot

from . import kit_xz as X
from .series import episode

AB = "Leo"
GROUND = 1130
LION = "#D9A35A"
MANE = "#A8642F"
EPS = math.radians(23.44)
# 狮子座流星雨辐射点（J2000，度，约值）
RADIANT = (152.0, 22.0)


def ecl(lam_deg: float) -> tuple[float, float]:
    """黄经（黄纬 0）→ 赤经、赤纬（度）。"""
    lam = math.radians(lam_deg)
    ra = math.degrees(math.atan2(math.cos(EPS) * math.sin(lam), math.cos(lam))) % 360
    dec = math.degrees(math.asin(math.sin(EPS) * math.sin(lam)))
    return ra, dec


def lion(c, x, y, s, t, crouch=0.0, alpha=1.0):
    """狮子剪影（朝左）：身体、四腿、鬃毛圈、尾巴。"""
    with K.at(c, x, y, 0, s / 300):
        with K.paper(c, alpha, 1.0):
            for i, dx in enumerate((-90, -40, 60, 110)):
                K.seg(c, dx, 20, dx + 6 * math.sin(t * 3 + i), 120, K.shade(LION, 0.2), 26)
            K.rr(c, 10, 0, 280, 120 - 20 * crouch, 60, LION)
            p_tail = [(150, -10), (215, -40), (240, -90)]
            for a, b in zip(p_tail, p_tail[1:]):
                K.seg(c, *a, *b, LION, 12)
            K.dot(c, 240, -96, 16, MANE)
            for i in range(14):
                a = i / 14 * 2 * math.pi
                K.dot(c, -130 + 62 * math.cos(a), -60 + 62 * math.sin(a), 30, MANE)
            K.dot(c, -130, -60, 54, LION)
            K.dot(c, -152, -72, 6, K.INK)
            K.dot(c, -170, -46, 12, K.shade(LION, 0.35))


def nemean(c, g, t, d):
    """赫拉克勒斯与涅墨亚狮子：第 4 拍箭被弹开，第 8 拍徒手扑上去。"""
    grab = ease_in_out(clamp01(g.since(8) / 0.45))
    lion(c, 200, 160, 340, g.t, 0.4 * grab)
    hx = -260 + 220 * grab
    K.figure(c, hx, 330, 380, "hug" if grab > 0.5 else ("point" if g.since(2) >= 0 else "stand"), K.HERO,
             hair="short", mood="angry" if g.since(4) >= 0 else "calm", face=1)
    sa = g.since(2.5)
    if 0 <= sa < 1.5:
        q = clamp01(sa / 0.5)
        if g.since(4) < 0:
            ax = -150 + 230 * q
            K.arrow(c, (ax - 90, 90), (ax, 90), K.INK2, 7, 1, 1, 0, 22)
        else:
            b = g.since(4)
            K.burst(c, 90, 90, b, K.GOLD, 30, 120, 8, 6)
            ang = math.radians(-50 - 300 * b)
            K.seg(c, 90, 90 - 160 * b, 90 + 70 * math.cos(ang), 90 - 160 * b + 70 * math.sin(ang), K.INK2, 7,
                  clamp01(1 - b))


def regulus_moon(c, g, t, d):
    """黄道穿过轩辕十四：第 1 拍画出黄道，月亮沿黄道移过来，第 3 拍挡住轩辕十四。"""
    reg = next(n for n in X.sign(AB)["named"] if n["en"] == "Regulus")

    def extra(c, P):
        k = clamp01(g.since(1) / 0.6)
        pts = [P(*ecl(l)) for l in range(120, 196, 3)]
        n = max(2, int(len(pts) * k))
        for a, b in zip(pts[:n], pts[1:n]):
            K.seg(c, a[0], a[1], b[0], b[1], "#F0A070", 4, 0.9)
        if k > 0:
            ex, ey = min(pts, key=lambda q: abs(q[0] - 330))
            K.text(c, "黄道", ex, ey - 44, 30, "sans_medium", "#F0A070", k)
        rx, ry = P(reg["ra"], reg["dec"])
        K.dot(c, rx, ry, 9, "#FFFFFF", 1)
        K.text(c, "轩辕十四", rx + 20, ry + 50, 36, "serif_black", "#FFE7A8", 1, "left")
        u = ease_in_out(clamp01((g.t - g.b(1)) / max(0.1, g.b(3) - g.b(1))))
        lam = 165 - 15.2 * u + 3 * clamp01(g.since(3) / 1.5)
        mx, my = P(*ecl(lam))
        if g.since(1) >= 0:
            K.spotlight(c, mx, my, 70, "#FFFBEA", 0.35)
            K.dot(c, mx, my, 34, "#EDE6D3", 1)
            K.dot(c, mx - 9, my - 6, 7, "#D2C9B2", 1)
            K.dot(c, mx + 10, my + 9, 5, "#D2C9B2", 1)
    X.sky_card(c, 0, 0, 900, 680, AB, 1, g.t, 1, line_color=X.FAINT, margin=110, extra=extra)


def leonids(c, g, t, d):
    """流星从狮子头附近的辐射点向四周划出；第 3 拍标出 1833 年流星暴。"""
    def extra(c, P):
        rx, ry = P(*RADIANT)
        k = clamp01(g.since(0.5) / 0.4)
        for i in range(14):
            seed = i * 1.7
            start = 0.5 + (i * 0.37) % 3.2
            q = (g.since(start)) / 0.55
            if 0 <= q <= 1:
                a = seed * 2.39996
                r0, r1 = 60 + 80 * q, 60 + 80 * q + 160
                x0, y0 = rx + r0 * math.cos(a), ry + r0 * math.sin(a)
                x1, y1 = rx + r1 * math.cos(a), ry + r1 * math.sin(a)
                K.seg(c, x0, y0, x1, y1, "#FFF4D6", 4, (1 - q) * 0.9)
                K.dot(c, x1, y1, 4, "#FFFFFF", 1 - q)
        if k > 0:
            K.ring(c, rx, ry, 26, "#F0A070", 4, k * 0.8)
        k2 = clamp01(g.since(3) / 0.35)
        if k2 > 0:
            K.pill(c, 0, 250, "1833 年 · 流星暴", 36, "#F0A070", X.SKY, k2)
            K.text(c, "坦普尔-塔特尔彗星的碎屑", 0, 310, 28, "sans_medium", X.FAINT, k2)
    X.sky_card(c, 0, 0, 900, 700, AB, 1, g.t, 1, line_color=X.FAINT, margin=130, extra=extra)


def build():
    mid = [
        Shot(3, "赫拉克勒斯的第一项任务：|刀枪不入的涅墨亚狮子。", "希腊神话", [
            Custom(nemean, x=540, y=800, at=0, enter="fade"),
            Label("赫拉克勒斯", 300, 480, 30, at=1, fill=K.HERO, sfx="wood_high", note="赫拉克勒斯"),
            Label("涅墨亚狮子", 760, 480, 30, at=2, fill=MANE, sfx="wood_low", note="涅墨亚狮子"),
        ], draw=lambda g: K.ground(g.c, GROUND), hits=[(4, "rim", 0.9, "箭被狮皮弹开"), (8, "kick", 0.7, "徒手扑上去")],
            note="赫拉克勒斯射出的箭撞上狮皮被弹开（第 4 拍），第 8 拍他徒手扑上去"),
        Shot(2, "轩辕十四贴着黄道，|月亮常把它挡住。", "天文观测", [
            Custom(regulus_moon, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.7, "黄道画出"), (3, "rim", 0.9, "月亮挡住轩辕十四")],
            text_beat=0, note="星图上画出黄道，月亮沿黄道移动，第 3 拍盖住轩辕十四（掩星示意）"),
        Shot(2, "狮子座流星雨，|来自彗星的碎屑。", "天文观测", [
            Custom(leonids, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.7, "流星划出"), (3, "cymbal", 0.6, "1833 年流星暴")],
            text_beat=0, note="流星从狮子头附近的辐射点向外划出，第 3 拍标“1833 年 · 流星暴”"),
    ]
    return episode(
        5, AB, "狮子座：|一个反写的问号是狮头。", mid,
        refs=["阿波罗多洛斯《书库》第 2 卷（涅墨亚狮子）"],
        notes=[
            "狮子座西半部的“镰刀”星群像一个反写的问号，是狮子的头和鬃毛。",
            "涅墨亚狮子刀枪不入，赫拉克勒斯的箭伤不了它，最后徒手将它扼死，这是他十二项任务中的第一项。神话版本不一。",
            "轩辕十四（Regulus）几乎就在黄道上，月亮每月都从它附近经过，在一些年份会从它前面经过并把它挡住（掩星）。片中月亮位置为示意。",
            "狮子座流星雨每年 11 月出现，来自坦普尔-塔特尔彗星留下的碎屑；1833 年 11 月曾出现每小时数以万计的流星暴。辐射点与流星为示意。",
        ],
        hashtags="#狮子座 #星座 #天文 #科普 #流星雨",
        cover_title="生日在狮子座，|太阳却在【巨蟹座】？", cover_sub="狮子座：天上到底长什么样")
