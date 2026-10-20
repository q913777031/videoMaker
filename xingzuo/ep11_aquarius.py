"""11 水瓶座：水瓶座，天上到底长什么样？"""

import math

import skia

from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from adler import kit as K
from adler.core import Custom, Label, Shot

from . import kit_xz as X
from .series import episode

AB = "Aqr"
EAGLE = "#6B4E36"
WATER = "#6FB3D6"
HELIX = (337.41 - 360, -20.84)        # 螺旋星云 NGC 7293，J2000 赤经 337.41°、赤纬 −20.84°
ETA_AQR = (338.84 - 360, -0.12)       # 宝瓶座 η（流星雨辐射点附近），J2000


def eagle(c, x, y, s, t, alpha=1.0):
    """宙斯的神鹰：张开的双翼随时间扇动（以身体中心为原点，朝右）。"""
    flap = math.sin(t * 7) * 0.35
    with K.at(c, x, y, 0, s / 300):
        with K.paper(c, alpha, 1.0):
            for side, shade in ((-1, 0.25), (1, 0.1)):
                fy = 70 * flap
                pts = [(side * 10, -20), (side * 120, -150 + fy), (side * 200, -120 + fy), (side * 150, -90 + fy * 0.6),
                       (side * 180, -60 + fy * 0.4), (side * 90, -10)]
                K.poly(c, pts, K.shade(EAGLE, shade))
            K.dot(c, 0, 0, 56, EAGLE)
            K.poly(c, [(-50, -10), (-130, 20), (-120, 40), (-40, 20)], K.shade(EAGLE, 0.2))
            K.dot(c, 60, -36, 30, K.mix(EAGLE, K.PAPER, 0.75))
            K.poly(c, [(84, -40), (112, -26), (86, -22)], K.GOLD)
            K.dot(c, 70, -42, 5, K.INK)


def ganymede(c, g, t, d):
    """少年在原野放羊（第 0 拍），第 2 拍神鹰俯冲，第 4 拍把他带上天；第 8 拍少年举起水瓶，水流倾泻而下。"""
    gy = 300
    K.seg(c, -520, gy, 520, gy, K.LINE, 6)
    K.icon(c, "cloud", -330, gy - 60, 120, K.PAPER, 1, 0.6)
    lift = ease_in_out(clamp01(g.since(4) / max(0.1, g.b(8) - g.b(4))))
    fx = lerp(-60, 140, lift)
    fy = lerp(gy, -80, lift)
    pose = "stand" if g.since(4) < 0 else ("reach" if g.since(8) < 0 else "give")
    mood = "calm" if g.since(2) < 0 else ("surprised" if g.since(8) < 0 else "smile")
    K.figure(c, fx, fy, 230, pose, K.HERO, mood=mood, hair="short", lift=0.8)
    for i in range(2):
        sx = -300 + i * 120
        K.dot(c, sx, gy - 34, 34, "#F4EFE4")
        K.dot(c, sx + 32, gy - 44, 16, K.INK2)
        for dx in (-14, 14):
            K.seg(c, sx + dx, gy - 10, sx + dx, gy, K.INK2, 6)
    ke = clamp01(g.since(2) / 0.5)
    if ke > 0:
        ex = lerp(380, fx - 10, ease_out(ke))
        ey = lerp(-360, fy - 315, ease_out(ke))
        eagle(c, ex, ey, 260, g.t, ke)
    kw = clamp01(g.since(8) / 0.3)
    if kw > 0:
        jx, jy = fx + 95, fy - 165
        with K.at(c, jx, jy, -35):
            K.rr(c, 0, 0, 56, 74, 16, "#C9A47E")
            K.rr(c, 0, -42, 30, 16, 6, K.shade("#C9A47E", 0.25))
        flow = clamp01(g.since(8) / 0.8)
        for i in range(14):
            q = i / 13
            if q > flow:
                break
            wx = jx + 30 + 40 * q + 10 * math.sin(g.t * 8 + i)
            wy = jy - 10 + 380 * q * q + 160 * q
            K.dot(c, wx, wy, 12 - 4 * q, WATER, 0.85)


def meteors(c, g, t, d):
    """流星雨辐射点：第 1、2、3 拍各有一颗流星从辐射点向外划过；第 4 拍弹出“哈雷彗星的碎屑”。"""
    def extra(c, P):
        rx, ry = P(*ETA_AQR)
        kr = clamp01(g.since(0.5) / 0.4)
        K.spotlight(c, rx, ry, 90 * kr, "#FFE7A8", 0.4 * kr)
        K.ring(c, rx, ry, 22, "#FFE7A8", 3, kr)
        for i, (ang, beat) in enumerate(((210, 1), (300, 2), (250, 3), (160, 3.5), (330, 1.5))):
            dt = g.since(beat)
            if dt < 0:
                continue
            q = clamp01(dt / 0.6)
            a = math.radians(ang)
            r0, r1 = 50 + 300 * ease_out(q) - 160, 50 + 300 * ease_out(q)
            r0 = max(40, r0)
            fade = 1 - clamp01((dt - 0.6) / 0.5)
            if fade <= 0:
                continue
            K.seg(c, rx + r0 * math.cos(a), ry + r0 * math.sin(a), rx + r1 * math.cos(a), ry + r1 * math.sin(a),
                  "#FFF4D6", 4, fade)
            K.dot(c, rx + r1 * math.cos(a), ry + r1 * math.sin(a), 6, "#FFFFFF", fade)
        if g.since(2) >= 0:
            K.text(c, "宝瓶座 η 流星雨 · 每年 5 月初", rx, ry - 60, 32, "sans_medium", "#FFE7A8",
                   clamp01(g.since(2) / 0.4))
    X.sky_card(c, 0, 50, 900, 600, AB, 1, g.t, 1, line_color=X.FAINT, extra=extra)
    k = clamp01(g.since(4) / 0.35)
    if k > 0:
        K.pill(c, 0, -340, "来自哈雷彗星留下的碎屑", 34, X.SKY, K.PAPER, k)


def helix(c, g, t, d):
    """螺旋星云：第 1 拍在星图上放大出一个红蓝色的气体环，第 3 拍标名。"""
    def extra(c, P):
        hx, hy = P(*HELIX)
        k = ease_out(clamp01(g.since(1) / 0.5))
        if k <= 0:
            K.ring(c, hx, hy, 14, "#FFE7A8", 3, 0.6)
            return
        r = 26 + 90 * k
        sh = skia.GradientShader.MakeRadial((hx, hy), r * 1.25, [K.col("#7FD3E0", 0.0), K.col("#7FD3E0", 0.55 * k),
                                                                  K.col("#E0614F", 0.85 * k), K.col("#E0614F", 0.0)],
                                            [0, 0.45, 0.75, 1])
        c.drawCircle(hx, hy, r * 1.25, skia.Paint(AntiAlias=True, Shader=sh))
        for i in range(10):
            a = i / 10 * 2 * math.pi + g.t * 0.2
            K.dot(c, hx + r * 0.85 * math.cos(a), hy + r * 0.85 * math.sin(a), 6, "#FFB09A", 0.5 * k)
        K.dot(c, hx, hy, 5, "#FFFFFF", k)
        kl = clamp01(g.since(3) / 0.4)
        if kl > 0:
            K.text(c, "螺旋星云", hx + r + 30, hy - 20, 44, "serif_black", "#FFE7A8", kl, "left")
            K.text(c, "NGC 7293", hx + r + 30, hy + 30, 30, "sans_medium", X.FAINT, kl, "left")
    X.sky_card(c, 0, 0, 900, 660, AB, 1, g.t, 1, line_color=X.FAINT, extra=extra)


def build():
    mid = [
        Shot(3, "希腊神话里，他被神鹰|带上天，为众神斟酒。", "希腊神话", [
            Custom(ganymede, x=540, y=820, at=0, enter="fade"),
            Label("伽倪墨得斯", 470, 860, 30, at=1, out=4, fill=K.HERO, sfx="wood_high", note="放羊少年伽倪墨得斯"),
            Label("宙斯的鹰", 820, 420, 30, at=2, out=7, fill=EAGLE, sfx="tom", note="神鹰俯冲"),
        ], hits=[(4, "bongo_high", 0.8, "少年被带上天"), (8, "shaker", 0.8, "水瓶倾倒，水流泻下")],
            note="放羊少年伽倪墨得斯被宙斯的神鹰带上天，第 8 拍举起水瓶，水流倾泻而下"),
        Shot(2, "这里是一场流星雨的|“出发点”。", "天文观测", [
            Custom(meteors, x=540, y=830, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.7, "第一颗流星"), (2, "wood_low", 0.7, "第二颗流星"), (3, "bongo_high", 0.7, "第三颗流星"),
                 (4, "rim", 0.8, "“哈雷彗星的碎屑”")], text_beat=0,
            note="宝瓶座 η 星附近的辐射点，流星按拍向四周划出；弹出“来自哈雷彗星留下的碎屑”"),
        Shot(2, "螺旋星云：恒星晚年|抛出的一圈外壳。", "天文观测", [
            Custom(helix, x=540, y=820, at=0, enter="fade"),
        ], hits=[(1, "cymbal", 0.6, "螺旋星云展开"), (3, "wood_high", 0.8, "标名 NGC 7293")], text_beat=0,
            note="星图下方的螺旋星云（NGC 7293）从一个小点展开成红蓝色气体环，并标名"),
    ]
    return episode(
        11, AB, "水瓶座：|天文上叫“宝瓶座”。", mid,
        refs=["奥维德《变形记》第 10 卷；IMO 流星雨年历"],
        notes=[
            "伽倪墨得斯：特洛伊的美少年，被宙斯（化身或派出的神鹰）带到奥林匹斯山，成为众神的斟酒人；宝瓶座常被画成他倾倒水瓶。"
            "神话版本不一。“水瓶座”是常用名，天文学正式中文名为“宝瓶座”。",
            "宝瓶座 η 流星雨每年约 4 月下旬至 5 月下旬活动、5 月初达到极大，母体是哈雷彗星（国际流星组织 IMO 流星雨年历）；"
            "南半球与低纬度地区观看条件更好。片中流星为示意。",
            "螺旋星云（Helix Nebula，NGC 7293）位于宝瓶座，是离地球最近的明亮行星状星云之一，距离约 650 光年；"
            "行星状星云是类似太阳的恒星在晚年抛出的气体外壳，与行星无关。片中星云的形状与颜色为示意。",
            "片中水瓶座最亮的星为虚宿一（Sadalsuud，β Aqr）。",
        ],
        hashtags="#水瓶座 #星座 #天文 #科普 #星空",
        cover_title="生日在水瓶座，|太阳却在【摩羯座】？", cover_sub="水瓶座：天上到底长什么样")
