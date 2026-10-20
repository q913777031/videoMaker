"""07 天秤座：天秤座，天上到底长什么样？"""

import math

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Custom, Shot

from . import kit_xz as X
from .series import ORDER, episode

AB = "Lib"
BRASS = "#C9A04A"


def balance(c, x, y, s, tilt, alpha=1.0):
    """一架天平：立柱、横梁（tilt 为倾角，度）、两只吊盘。"""
    with K.paper(c, alpha, 1.0):
        K.rr(c, x, y + s * 0.62, s * 0.7, s * 0.1, s * 0.04, K.shade(BRASS, 0.2))
        K.rr(c, x, y + s * 0.15, s * 0.07, s * 0.95, s * 0.03, BRASS)
        K.dot(c, x, y - s * 0.34, s * 0.07, K.shade(BRASS, 0.15))
    a = math.radians(tilt)
    L = s * 0.62
    for side in (-1, 1):
        ex, ey = x + side * L * math.cos(a), y - s * 0.3 + side * L * math.sin(a)
        K.seg(c, x, y - s * 0.3, ex, ey, BRASS, s * 0.045, alpha)
        for dx in (-0.16, 0.16):
            K.seg(c, ex, ey, ex + dx * s, ey + s * 0.42, K.INK3, 3, alpha)
        with K.paper(c, alpha, 0.8):
            K.poly(c, [(ex - s * 0.22, ey + s * 0.42), (ex + s * 0.22, ey + s * 0.42), (ex + s * 0.14, ey + s * 0.5),
                       (ex - s * 0.14, ey + s * 0.5)], BRASS)


def scales_scene(c, g, t, d):
    """天平左右摇摆后在第 4 拍归平；下方 12 个星座名牌，只有天秤座是“物件”，第 8 拍亮起。"""
    sw = math.sin(g.t * 3.2) * 14 * (1 - ease_in_out(clamp01(g.since(2) / (g.b(4) - g.b(2) + 1e-6))))
    balance(c, 0, -170, 420, sw)
    for i, ab in enumerate(ORDER):
        k = clamp01(g.since(5 + i * 0.15) / 0.3)
        if k <= 0:
            continue
        col, row = i % 6, i // 6
        px, py = -375 + col * 150, 240 + row * 90
        hit = ab == AB and g.since(8) >= 0
        fill = g.acc if hit else K.mix(K.INK3, K.PAPER, 0.35)
        with K.at(c, px, py, 0, (0.4 + 0.6 * K.ease_out_back(k, 1.8)) * (1.15 if hit else 1.0)):
            K.pill(c, 0, 0, X.NAMES[ab][:-1], 30, fill, K.PAPER, k)
    k = clamp01(g.since(8) / 0.35)
    if k > 0:
        K.text(c, "其余 11 个：人或动物", 0, 440, 30, "sans_medium", K.INK2, k)


def claws(c, g, t, d):
    """天秤座星图：两颗最亮星依次亮起，标“南钳 / 北钳”，并画出两只钳子的弧线。"""
    named = {n["en"]: n for n in X.sign(AB)["named"]}
    pairs = [(named["Zubenelgenubi"], "南边的钳子", 1, 1), (named["Zubeneschamali"], "北边的钳子", 3, -1)]

    def extra(c, P):
        for st, lab, b, side in pairs:
            k = clamp01(g.since(b) / 0.35)
            if k <= 0:
                continue
            px, py = P(st["ra"], st["dec"])
            K.spotlight(c, px, py, 90 * k, "#FFE7A8", 0.5 * k)
            K.ring(c, px, py, 26 + 12 * (1 - k), "#FF9F80", 5, k)
            al = "left" if side > 0 else "right"
            K.text(c, st["zh"], px + side * 46, py - 22, 44, "serif_black", "#FFE7A8", k, al)
            K.text(c, lab, px + side * 46, py + 30, 32, "sans_medium", "#FFC9B8", k, al)
    X.sky_card(c, 0, 0, 900, 660, AB, 1, g.t, 1, line_color=X.FAINT, margin=130, extra=extra)


def november(c, g, t, d):
    """黄道条：占星天秤座日期全落在室女座；太阳真正经过天秤座是 11 月。"""
    s = X.sign(AB)
    a, b, n = X.DATA["sun"][AB]
    X.ecliptic_strip(c, 0, -60, 960, 130, ("Vir",) if g.since(2) < 0 else (AB,), tuple(s["astro"]), 1,
                     None, 1, True, 0.0, 26)
    k = clamp01(g.since(2) / 0.4)
    if k > 0:
        da, db = X.doy(a), X.doy(b)
        x0 = -480 + 960 / 365 * da
        x1 = -480 + 960 / 365 * (db + 1)
        K.seg(c, x0, 30, x0 + (x1 - x0) * k, 30, g.acc, 8)
        K.text(c, f"太阳真正经过：{X.mmdd(a)}–{X.mmdd(b)}", 0, 160, 40, "serif_black", g.acc, k)


def build():
    mid = [
        Shot(3, "天平象征公正，|也是唯一的“物件”星座。", "希腊神话", [
            Custom(scales_scene, x=540, y=760, at=0, enter="fade"),
        ], hits=[(4, "wood_high", 0.85, "天平归平"), (5, "shaker", 0.6, "12 个名牌弹出"), (8, "rim", 0.9, "天秤座名牌亮起")],
            note="天平摇摆后归平；下方 12 个星座名牌，只有天秤座是物件，第 8 拍亮起"),
        Shot(2, "这些星，原本是|天蝎的两只钳子。", "天文观测", [
            Custom(claws, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_low", 0.8, "氐宿一：南边的钳子"), (3, "wood_high", 0.8, "氐宿四：北边的钳子")], text_beat=0,
            note="天秤座星图上氐宿一、氐宿四依次亮起，标出“南边的钳子 / 北边的钳子”"),
        Shot(2, "太阳经过天秤座，|在 11 月。", "天文观测", [
            Custom(november, x=540, y=800, at=0, enter="fade"),
        ], hits=[(2, "rim", 0.9, "11 月那一段亮起")], text_beat=0,
            note="黄道条：占星日期（9/23–10/23）全在室女座；第 2 拍天秤座那段亮起，标出 11 月 1 日–23 日"),
    ]
    return episode(
        7, AB, "天秤座：|一个歪斜的四边形。", mid,
        refs=["阿拉托斯《物象》", "奥维德《变形记》第 1 卷"],
        notes=[
            "神话版本不一：天秤常被看作正义女神阿斯特赖亚（或忒弥斯）手中的天平。黄道十二星座中只有天秤座不是人或动物。",
            "天秤座最亮的两颗星，阿拉伯名 Zubenelgenubi（氐宿一）意为“南边的钳子”，Zubeneschamali（氐宿四）意为“北边的钳子”："
            "古希腊人原本把它们算作天蝎座的两只钳子，后来才独立成天秤座。",
            "按 IAU 边界计算（2026 年），占星天秤座日期 9 月 23 日–10 月 23 日里太阳全部在室女座；太阳实际经过天秤座是 11 月 1 日–23 日，"
            "共 23 天。",
        ],
        hashtags="#天秤座 #星座 #天文 #科普 #星空",
        cover_title="生日在天秤座，|太阳却【一天】也不在？", cover_sub="天秤座：天上到底长什么样")
