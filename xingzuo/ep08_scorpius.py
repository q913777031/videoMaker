"""08 天蝎座：天蝎座，天上到底长什么样？"""

import math

import skia

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Custom, Label, Shot, Txt

from . import kit_xz as X
from .series import episode

AB = "Sco"
SCORP = "#A9443C"
ORION = "#56698F"
HORIZON = 260


def scorpion(c, x, y, s, t, alpha=1.0):
    """蝎子剪影（朝右）：一串体节、两只钳子、向上卷起的尾巴和毒刺。"""
    with K.at(c, x, y, 0, s / 300):
        with K.paper(c, alpha, 0.9):
            for i in range(5):
                K.dot(c, 40 - i * 34, 0, 34 - i * 2, SCORP)
            for side in (-1, 1):
                K.seg(c, 60, side * 14, 120, side * 50, K.shade(SCORP, 0.15), 14)
                K.dot(c, 138, side * 54, 22, K.shade(SCORP, 0.1))
                for j in range(3):
                    K.seg(c, 20 - j * 34, side * 20, -5 - j * 34, side * 62, K.shade(SCORP, 0.25), 7)
            px, py = -110, 0
            for i in range(6):
                ang = math.radians(200 - i * 32 + 6 * math.sin(t * 3))
                nx, ny = px + 34 * math.cos(ang), py + 34 * math.sin(ang)
                K.seg(c, px, py, nx, ny, SCORP, 26 - i * 2)
                px, py = nx, ny
            K.poly(c, [(px, py - 12), (px + 34, py + 4), (px, py + 14)], K.shade(SCORP, 0.35))


def opposite(c, g, t, d):
    """地平线上：天蝎从左边（东方）升起，猎户在右边（西方）同时落下。"""
    k = ease_in_out(clamp01(g.t / max(0.1, g.b(10))))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(-540, -500, 540, HORIZON))
    scorpion(c, -250, HORIZON + 80 - 330 * k, 300, g.t)
    K.figure(c, 260, HORIZON + 30 + 250 * k, 330, "fist", ORION, mood="angry", face=-1, lift=0.8)
    c.restore()
    K.seg(c, -500, HORIZON, 500, HORIZON, K.INK3, 5)
    K.text(c, "东", -420, HORIZON + 50, 36, "serif_black", K.INK2)
    K.text(c, "西", 420, HORIZON + 50, 36, "serif_black", K.INK2)
    for sx, arrow in ((-250, -1), (260, 1)):
        a = clamp01(g.since(2) / 0.4)
        if a > 0:
            y0, y1 = (HORIZON + 30, HORIZON - 70) if arrow < 0 else (HORIZON - 70, HORIZON + 30)
            K.arrow(c, (sx + 160 * (1 if arrow < 0 else -1), y0), (sx + 160 * (1 if arrow < 0 else -1), y1), K.INK3, 7,
                    a * 0.8, a, 0, 22)


def great_fire(c, g, t, d):
    """星图：心宿二发光，标“大火”；第 2 拍一支箭头指向西边地平线（西沉）。"""
    named = {n["en"]: n for n in X.sign(AB)["named"]}
    st = named["Antares"]

    def extra(c, P):
        px, py = P(st["ra"], st["dec"])
        k = clamp01(g.since(0) / 0.4)
        K.spotlight(c, px, py, 130 * k, "#FF7A50", 0.6 * k)
        K.dot(c, px, py, 12, "#FFB28F", k)
        K.text(c, "大火", px - 60, py - 70, 54, "serif_black", "#FFC9B8", k, "right")
        K.text(c, "心宿二", px - 60, py - 14, 32, "sans_medium", "#FFC9B8", k, "right")
        a = clamp01(g.since(2) / 0.5)
        if a > 0:
            K.arrow(c, (px + 60, py + 20), (px + 260, py + 200), "#FFC9B8", 8, a, a, -0.2, 28)
            K.text(c, "向西沉落", px + 270, py + 250, 32, "sans_medium", "#FFC9B8", a, "center")
    X.sky_card(c, 0, 0, 900, 660, AB, 1, g.t, 1, line_color=X.FAINT, margin=110, extra=extra)


def seven_days(c, g, t, d):
    """黄道条：天蝎座一段只有 7 天，紧接着蛇夫座 18 天。"""
    a, b, n = X.DATA["sun"][AB]
    oa, ob, on = X.DATA["sun"]["Oph"]
    X.ecliptic_strip(c, 0, -40, 960, 130, (AB,) + (("Oph",) if g.since(3) >= 0 else ()), (a, b),
                     clamp01(g.since(1) / 0.4), None, 1, True, 0.0, 26, f"{n} 天")
    k = clamp01(g.since(3) / 0.4)
    if k > 0:
        K.text(c, f"天蝎座 {n} 天 → 蛇夫座 {on} 天", 0, 140, 44, "serif_black", g.acc, k)
        K.text(c, f"{X.mmdd(oa)}–{X.mmdd(ob)}，太阳在蛇夫座", 0, 210, 30, "sans_medium", K.INK2, k)


def build():
    mid = [
        Shot(3, "天蝎和猎户，|一个升起，一个落下。", "希腊神话", [
            Custom(opposite, x=540, y=760, at=0, enter="fade"),
            Label("天蝎", 290, 520, 32, at=4, fill=SCORP, sfx="wood_low", note="天蝎升起"),
            Label("猎户", 800, 520, 32, at=5, fill=ORION, sfx="wood_high", note="猎户落下"),
            Txt("中国也有“参商”：杜甫“人生不相见，动如参与商”", 540, 1240, 28, at=8, font="sans_medium",
                color=K.INK2),
        ], hits=[(2, "shaker", 0.7, "一升一落开始"), (8, "rim", 0.8, "参商诗句出现")],
            note="地平线上，天蝎从东方升起、猎户在西方落下；底部小字引杜甫“动如参与商”"),
        Shot(2, "“七月流火”：|是大火星西沉，不是天热。", "中国星官", [
            Custom(great_fire, x=540, y=800, at=0, enter="fade"),
        ], hits=[(0, "wood_high", 0.8, "心宿二发光"), (2, "wood_low", 0.8, "箭头指向西边")], text_beat=0,
            note="天蝎座星图：心宿二发红光，标“大火”，箭头指向西方（西沉）"),
        Shot(2, "太阳只待 7 天，|就进蛇夫座。", "天文观测", [
            Custom(seven_days, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "rim", 0.9, "括号标出 7 天"), (3, "bongo_high", 0.85, "蛇夫座亮起")], text_beat=0,
            note="黄道条上天蝎座只有短短一段（7 天），紧接着蛇夫座（18 天）亮起"),
    ]
    return episode(
        8, AB, "天蝎座：|一条弯弯的蝎子尾巴。", mid,
        refs=["奥维德《岁时记》第 5 卷", "《诗经·豳风·七月》；杜甫《赠卫八处士》"],
        notes=[
            "神话版本不一：一说大地女神派蝎子杀死夸口的猎人俄里翁，两者被放到天空两侧，此升彼落、永不相见。天文上天蝎座与猎户座"
            "赤经相差约 11 小时，确实一个升起时另一个落下。",
            "中国古代的“参商”：参宿属猎户座，商星即心宿（天蝎座），此出彼没。杜甫诗句“人生不相见，动如参与商”。",
            "心宿二（Antares）古称“大火”。《诗经·豳风·七月》“七月流火，九月授衣”：七月（夏历）黄昏时大火星向西沉落，"
            "预示暑去秋来，并非形容天气炎热。",
            f"按 IAU 边界计算（2026 年），太阳在天蝎座只停留 {X.DATA['sun'][AB][2]} 天（{X.mmdd(X.DATA['sun'][AB][0])}–"
            f"{X.mmdd(X.DATA['sun'][AB][1])}），是黄道星座中最短的，随后进入蛇夫座。",
        ],
        hashtags="#天蝎座 #星座 #天文 #科普 #七月流火",
        cover_title="生日在天蝎座，|太阳却在【天秤座】？", cover_sub="天蝎座：天上到底长什么样")
