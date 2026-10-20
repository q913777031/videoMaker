"""04 巨蟹座：巨蟹座，天上到底长什么样？"""

import math

import skia

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Custom, Label, Shot

from . import kit_xz as X
from .series import episode

AB = "Cnc"
GROUND = 1130
CRAB = "#D8674A"
HYDRA = "#5E8A6A"
# 鬼宿星团 M44 中心（J2000，度）
M44 = (130.1, 19.67)


def crab(c, x, y, s, squash=0.0, alpha=1.0):
    """小螃蟹：椭圆壳、两只大钳、六条腿；squash 0–1 被踩扁。"""
    with K.at(c, x, y + s * 0.25 * squash, 0, 1, 1 - 0.6 * squash):
        with K.paper(c, alpha, 0.8):
            for side in (-1, 1):
                for i in range(3):
                    K.seg(c, side * s * 0.3, s * 0.05 * i, side * s * (0.62 + 0.04 * i), s * (0.18 + 0.1 * i), CRAB, s * 0.06)
                K.seg(c, side * s * 0.3, -s * 0.12, side * s * 0.55, -s * 0.38, CRAB, s * 0.08)
                K.dot(c, side * s * 0.6, -s * 0.46, s * 0.14, CRAB)
            K.rr(c, 0, 0, s * 0.8, s * 0.48, s * 0.24, CRAB)
            for side in (-1, 1):
                K.dot(c, side * s * 0.12, -s * 0.28, s * 0.05, K.INK)


def hydra(c, x, y, s, t, alpha=1.0):
    """九头蛇剪影（简化为五个头）：身体一团，脖子弯曲摆动。"""
    with K.paper(c, alpha, 0.9):
        K.rr(c, x, y, s * 0.9, s * 0.45, s * 0.22, HYDRA)
        for i in range(5):
            a = -math.pi / 2 + (i - 2) * 0.42
            sw = 0.12 * math.sin(t * 2.6 + i)
            bx, by = x + (i - 2) * s * 0.12, y - s * 0.15
            hx = bx + math.cos(a + sw) * s * 0.75
            hy = by + math.sin(a + sw) * s * 0.75
            p = skia.Path()
            p.moveTo(bx, by)
            p.quadTo(bx + (hx - bx) * 0.3 + 30 * math.sin(i), by + (hy - by) * 0.6, hx, hy)
            c.drawPath(p, K.paint(HYDRA, 1, s * 0.07))
            K.dot(c, hx, hy, s * 0.08, HYDRA)
            K.dot(c, hx + 6, hy - 4, s * 0.015, K.PAPER)


def heracles_crab(c, g, t, d):
    """赫拉克勒斯与九头蛇对峙，第 3 拍螃蟹爬出来夹脚，第 6 拍被一脚踩扁。"""
    hydra(c, 190, 0, 320, g.t)
    stomp = clamp01(g.since(6) / 0.18)
    K.figure(c, -170, 300, 400, "block" if stomp <= 0 else "push", K.HERO, hair="short",
             mood="angry" if stomp > 0 else "worried", face=1)
    k = clamp01(g.since(3) / 0.5)
    if k > 0:
        cx = lerp_(-420, -110, ease_out(k))
        crab(c, cx, 270, 110, stomp)
        if stomp > 0 and g.since(6) < 0.5:
            K.burst(c, cx, 260, g.since(6), K.GOLD, 40, 130, 8, 6)


def lerp_(a, b, k):
    return a + (b - a) * k


def beehive(c, g, t, d):
    """鬼宿星团：第 1 拍一团模糊的光亮起，第 3 拍标出“积尸气”。"""
    def extra(c, P):
        mx, my = P(*M44)
        k = clamp01(g.since(1) / 0.5)
        if k > 0:
            K.spotlight(c, mx, my, 110 * k, "#DDE6FF", 0.55 * k)
            for i in range(26):
                a = i * 2.39996
                r = 52 * math.sqrt((i + 0.5) / 26)
                K.dot(c, mx + r * math.cos(a), my + r * math.sin(a), 2.6, "#FFFFFF", 0.7 * k)
        k2 = clamp01(g.since(3) / 0.35)
        if k2 > 0:
            K.text(c, "积尸气", mx + 90, my - 16, 46, "serif_black", "#FFE7A8", k2, "left")
            K.text(c, "鬼宿星团 M44", mx + 90, my + 34, 30, "sans_medium", X.FAINT, k2, "left")
    X.sky_card(c, 0, 0, 900, 680, AB, 1, g.t, 1, line_color=X.FAINT, margin=110, extra=extra)


def tropic(c, g, t, d):
    """地球与北回归线：第 1 拍红线绕出，第 3 拍标上英文名。"""
    R = 260
    sh = skia.GradientShader.MakeRadial((-80, -90), R * 1.5, [K.col("#7FB6D9"), K.col("#3D6E92")], [0, 1])
    with K.paper(c, 1, 1.0):
        c.drawCircle(0, 0, R, skia.Paint(AntiAlias=True, Shader=sh))
    for lx, ly, r in ((-90, -40, 70), (70, 50, 60), (20, -150, 40), (-40, 140, 50)):
        K.dot(c, lx, ly, r, "#6FA06A", 0.9)
    K.seg(c, -R, 0, R, 0, K.PAPER, 3, 0.7)
    K.text(c, "赤道", R + 20, 0, 28, "sans_medium", K.INK2, 1, "left")
    ty = -R * math.sin(math.radians(23.4))
    hw = R * math.cos(math.radians(23.4))
    k = ease_out(clamp01(g.since(1) / 0.5))
    if k > 0:
        K.seg(c, -hw, ty, -hw + 2 * hw * k, ty, K.RED, 7)
    k2 = clamp01(g.since(3) / 0.35)
    if k2 > 0:
        K.text(c, "北回归线 23.4°N", -hw - 20, ty - 4, 30, "sans_medium", K.RED, k2, "right")
        K.pill(c, 0, -R - 70, "Tropic of Cancer", 36, K.RED, K.PAPER, k2)


def build():
    mid = [
        Shot(3, "赫拉派来的螃蟹，|被赫拉克勒斯一脚踩扁。", "希腊神话", [
            Custom(heracles_crab, x=540, y=820, at=0, enter="fade"),
            Label("赫拉克勒斯", 330, 500, 30, at=1, fill=K.HERO, sfx="wood_high", note="赫拉克勒斯"),
            Label("九头蛇", 730, 900, 30, at=2, fill=HYDRA, sfx="wood_low", note="九头蛇"),
        ], draw=lambda g: K.ground(g.c, GROUND), hits=[(3, "shaker", 0.7, "螃蟹爬出来"), (6, "kick", 0.7, "一脚踩扁")],
            note="赫拉克勒斯与九头蛇对峙，第 3 拍螃蟹爬来夹脚，第 6 拍被踩扁"),
        Shot(2, "中间那团模糊的光，|古称“积尸气”。", "中国星官", [
            Custom(beehive, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "cymbal", 0.6, "星团亮起"), (3, "wood_high", 0.8, "标出“积尸气”")],
            text_beat=0, note="巨蟹座中间一团模糊的星光亮起，标“积尸气 / 鬼宿星团 M44”"),
        Shot(2, "北回归线，英文叫|“巨蟹座回归线”。", "天文观测", [
            Custom(tropic, x=540, y=820, at=0, enter="fade"),
        ], hits=[(1, "wood_low", 0.8, "北回归线绕出"), (3, "rim", 0.9, "Tropic of Cancer")],
            text_beat=0, note="地球上红色北回归线绕出，标“Tropic of Cancer”"),
    ]
    return episode(
        4, AB, "巨蟹座：|黄道星座里最暗的一个。", mid,
        refs=["阿波罗多洛斯《书库》第 2 卷（赫拉克勒斯与九头蛇）"],
        notes=[
            "巨蟹座最亮的星柳宿增十（β Cnc）视星等约 3.5，是十二个黄道星座里整体最暗的一个，城市里很难看见。",
            "赫拉克勒斯与九头蛇搏斗时，赫拉派一只螃蟹去夹他的脚，被他踩死，赫拉把它放上天空。神话版本不一。",
            "鬼宿星团（M44，Praesepe / Beehive）肉眼看是一团模糊的光，中国古称“积尸气”，属二十八宿的鬼宿。",
            "北回归线英文叫 Tropic of Cancer，因为两千多年前夏至时太阳位于巨蟹座；由于岁差，如今夏至太阳在金牛座。南回归线（Tropic of "
            "Capricorn）同理。片中地球为示意图形。",
        ],
        hashtags="#巨蟹座 #星座 #天文 #科普 #星空",
        cover_title="生日在巨蟹座，|太阳却在【双子座】？", cover_sub="巨蟹座：天上到底长什么样")
