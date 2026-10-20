"""03 双子座：双子座，天上到底长什么样？"""

import math

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Custom, Label, Shot

from . import kit_xz as X
from .series import episode

AB = "Gem"
GROUND = 1130
# 1930 年冥王星位置示意：在双子座 δ（天樽二）东侧约 0.5°（J2000，度）
WASAT = (110.03, 21.98)


def twins(c, g, t, d):
    """一对兄弟手拉手；一团金光（永生）在两人之间来回传递。"""
    K.figure(c, -140, GROUND - 780, 420, "give", K.HERO, hair="short", mood="smile", face=1)
    K.figure(c, 140, GROUND - 780, 420, "give", "#3F7FA6", hair="short", mood="smile", face=-1)
    k = clamp01(g.since(4) / 0.4)
    if k > 0:
        u = 0.5 + 0.5 * math.sin((g.since(4)) * 2.2 - math.pi / 2)
        ox = -150 + 300 * ease_in_out(u)
        K.spotlight(c, ox, -140, 130 * k, K.GOLD, 0.6 * k)
        K.star(c, ox, -140, 34 * k, K.GOLD, k, 4, 0.4)


def brighter_beta(c, g, t, d):
    """北河二（α）与北河三（β）：第 1、2 拍依次亮起，北河三光晕更大。"""
    named = {n["en"]: n for n in X.sign(AB)["named"]}

    def extra(c, P):
        for i, (en, zh, lab, r, right) in enumerate((("Castor", "北河二", "α · 1.58 等", 70, True),
                                                      ("Pollux", "北河三", "β · 1.16 等", 110, False))):
            st = named[en]
            k = clamp01(g.since(1 + i) / 0.35)
            if k <= 0:
                continue
            px, py = P(st["ra"], st["dec"])
            K.spotlight(c, px, py, r * k, "#FFE7A8", 0.6 * k)
            K.dot(c, px, py, 9 + 3 * i, "#FFFFFF", k)
            lx = px + (40 if right else -40)
            al = "left" if right else "right"
            K.text(c, zh, lx, py - 20, 40, "serif_black", "#FFE7A8", k, al)
            K.text(c, lab, lx, py + 26, 30, "sans_medium", X.FAINT, k, al)
    X.sky_card(c, 0, 0, 900, 680, AB, 1, g.t, 1, line_color=X.FAINT, margin=180, extra=extra)


def pluto_plates(c, g, t, d):
    """冥王星的发现：天樽二旁一颗小光点在两张底片之间来回跳（示意），第 3 拍圈出并标名。"""
    def extra(c, P):
        wx, wy = P(*WASAT)
        K.ring(c, wx, wy, 24, "#9FC3E8", 4, 0.9)
        K.text(c, "天樽二", wx - 40, wy + 12, 32, "serif_black", "#C9DDF2", 1, "right")
        bx, by = P(WASAT[0] + 0.55, WASAT[1] - 0.05)
        jump = 14 if int(max(0.0, g.t) * 2.5) % 2 else 0
        a = 1.0 if g.since(1) >= 0 else 0.0
        if a > 0:
            K.dot(c, bx + jump, by, 6, "#FFD2B0", a)
        k = clamp01(g.since(3) / 0.35)
        if k > 0:
            K.ring(c, bx + 7, by, 34, K.RED, 5, k, k)
            K.text(c, "冥王星 · 1930", bx + 7, by - 60, 34, "serif_black", "#FFC9B8", k)
    X.sky_card(c, 0, 0, 900, 680, AB, 1, g.t, 1, line_color=X.FAINT, margin=110, extra=extra)


def build():
    mid = [
        Shot(3, "神话里的一对兄弟，|共享一份永生。", "希腊神话", [
            Custom(twins, x=540, y=780, at=0, enter="fade"),
            Label("卡斯托耳", 360, 480, 30, at=1, fill=K.HERO, sfx="wood_high", note="哥哥卡斯托耳"),
            Label("波吕丢刻斯", 740, 480, 30, at=2, fill="#3F7FA6", sfx="wood_low", note="弟弟波吕丢刻斯"),
        ], draw=lambda g: K.ground(g.c, GROUND), hits=[(4, "cymbal", 0.6, "永生的金光在兄弟间传递")],
            note="兄弟二人手拉手站立，第 4 拍一颗金星（永生）在两人之间来回传递"),
        Shot(2, "α 是北河二，|更亮的却是北河三。", "天文观测", [
            Custom(brighter_beta, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.8, "北河二亮起"), (2, "bongo_high", 0.9, "北河三亮起，光晕更大")],
            text_beat=0, note="星图上北河二（α，1.58 等）与北河三（β，1.16 等）依次亮起，北河三光晕更大"),
        Shot(2, "1930 年，冥王星|在这里被发现。", "天文观测", [
            Custom(pluto_plates, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_low", 0.7, "小光点出现"), (3, "rim", 0.9, "圈出冥王星")],
            text_beat=0, note="天樽二旁一个小光点来回跳动（两张底片比对的示意），第 3 拍红圈圈出“冥王星 · 1930”"),
    ]
    return episode(
        3, AB, "双子座：|两串星像手拉手的兄弟。", mid,
        refs=["阿波罗多洛斯《书库》第 3 卷；洛厄尔天文台 1930 年公告"],
        notes=[
            "双子兄弟卡斯托耳与波吕丢刻斯（Pollux）：波吕丢刻斯是宙斯之子、不死；卡斯托耳战死后，他请求与兄弟共享永生，"
            "两人从此轮流在天上与冥府度日。神话版本不一。",
            "拜耳命名大体按亮度排 α、β，但并不严格：北河二（Castor）是 α，视星等约 1.58；北河三（Pollux）是 β，视星等约 1.16，反而更亮。",
            "1930 年，汤博在比对双子座 δ 星（天樽二）附近的照相底片时发现了冥王星，3 月由洛厄尔天文台公布。片中光点位置与跳动为示意。",
        ],
        hashtags="#双子座 #星座 #天文 #科普 #冥王星",
        cover_title="生日在双子座，|太阳却在【金牛座】？", cover_sub="双子座：天上到底长什么样")
