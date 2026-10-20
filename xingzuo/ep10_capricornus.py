"""10 摩羯座：摩羯座，天上到底长什么样？"""

import math

import skia

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Custom, Label, Shot

from . import kit_xz as X
from .series import episode

AB = "Cap"
GOAT = "#8A7A66"
FISH = "#4C8C9C"
RIVER = "#5B8FB0"


def waves(c, t, y0, n=4, x0=-520, x1=520, amp=10):
    for i in range(n):
        wy = y0 + i * 26
        path = skia.Path()
        path.moveTo(x0, wy)
        for j in range(int((x1 - x0) / 40) + 1):
            px = x0 + j * 40
            path.lineTo(px, wy + amp * math.sin(j * 0.9 + t * 2 + i))
        c.drawPath(path, K.paint(K.mix(RIVER, K.PAPER, 0.25 + 0.15 * i), 1, 6))


def typhon(c, x, y, s, t, alpha=1.0):
    """怪物提丰：翻滚的乌云，两只发光的眼睛。"""
    with K.fade(c, alpha):
        with K.paper(c, 1, 1.0):
            for i, (dx, dy, r) in enumerate(((-60, 10, 70), (0, -30, 85), (70, 0, 72), (20, 40, 66), (-90, 50, 50))):
                K.dot(c, x + dx * s + 6 * math.sin(t * 2 + i), y + dy * s, r * s, "#4A4F63")
        for dx in (-22, 22):
            K.dot(c, x + dx * s, y - 20 * s, 9 * s, "#FFB84D")


def sea_goat(c, x, y, s, t, alpha=1.0):
    """海山羊：前半身是长角的山羊，后半身是鱼尾（以身体中心为原点，朝右）。"""
    with K.at(c, x, y, 0, s / 300):
        with K.paper(c, alpha, 1.0):
            sway = 14 * math.sin(t * 3)
            tail = skia.Path()
            tail.moveTo(-40, -40)
            tail.cubicTo(-140, -50, -190, 20 + sway, -250, 10 + sway)
            tail.lineTo(-240, 50 + sway)
            tail.cubicTo(-180, 60 + sway, -120, 50, -40, 40)
            tail.close()
            c.drawPath(tail, K.paint(FISH))
            K.poly(c, [(-245, 30 + sway), (-310, -20 + sway), (-290, 30 + sway), (-310, 80 + sway)], K.shade(FISH, 0.2))
            for i in range(4):
                K.ring(c, -70 - 40 * i, 4, 22, K.mix(FISH, K.PAPER, 0.35), 4, 0.8, 0.5, 200)
            K.dot(c, 10, 0, 70, GOAT)
            for i, dx in enumerate((10, 50)):
                leg = 8 * math.sin(t * 6 + i)
                K.seg(c, dx, 40, dx + 20 + leg, 110, K.shade(GOAT, 0.3), 16)
            K.dot(c, 90, -60, 46, K.mix(GOAT, K.PAPER, 0.2))
            K.poly(c, [(120, -40), (150, -20), (118, -10)], K.mix(GOAT, K.PAPER, 0.2))
            K.dot(c, 104, -66, 6, K.INK)
            path = skia.Path()
            path.moveTo(70, -95)
            path.cubicTo(40, -150, 0, -150, -10, -110)
            c.drawPath(path, K.paint(K.shade(GOAT, 0.35), 1, 14))
            K.poly(c, [(118, -36), (126, 0), (108, -30)], K.shade(GOAT, 0.3))


def pan_river(c, g, t, d):
    """潘在河边被提丰追赶（第 2 拍乌云出现），第 4 拍跳进河里溅起水花，第 6 拍化作海山羊游出。"""
    waves(c, g.t, 250)
    k_ty = clamp01(g.since(2) / 0.4)
    if k_ty > 0:
        typhon(c, -330, -180, 1.2, g.t, k_ty)
    jump = g.since(4)
    if jump < 0:
        x = lerp_run = -80 + 200 * ease_in_out(clamp01(g.t / max(0.1, g.b(4))))
        K.figure(c, lerp_run, 210, 260, "reach" if g.since(2) >= 0 else "stand", K.OTHER3, mood="surprised"
                 if g.since(2) >= 0 else "calm", hair="short", lift=0.8)
        for dx in (-14, 14):
            K.seg(c, x + dx + 8, 210 - 248, x + dx * 2.2 + 8, 210 - 290, K.shade(GOAT, 0.3), 8)
    else:
        sp = clamp01(jump / 0.5)
        if sp < 1:
            for i in range(9):
                a = -math.pi * (0.15 + 0.7 * i / 8)
                r = 40 + 140 * ease_out(sp)
                K.dot(c, 120 + r * math.cos(a), 250 + r * math.sin(a), 12 * (1 - sp), K.mix(RIVER, K.PAPER, 0.3))
        k_g = clamp01(g.since(6) / 0.5)
        if k_g > 0:
            sea_goat(c, 120 + 120 * ease_out(clamp01(g.since(6) / 2.5)), 190 - 50 * ease_out(k_g), 330, g.t, k_g)


def tropic(c, g, t, d):
    """地球与南回归线：第 1 拍虚线南回归线画出，第 3 拍太阳光直射到它上面。"""
    R, cx, cy = 220, 60, 40
    sh = skia.GradientShader.MakeRadial((cx - 80, cy - 90), R * 1.4, [K.col("#7FB6D9"), K.col("#3D6E92")], [0, 1])
    with K.paper(c, 1, 1.0):
        c.drawCircle(cx, cy, R, skia.Paint(AntiAlias=True, Shader=sh))
    for lx, ly, r in ((-20, -110, 54), (90, 40, 44), (0, 100, 28)):
        K.dot(c, cx + lx, cy + ly, r, "#6FA06A", 0.9)
    K.seg(c, cx - R, cy, cx + R, cy, K.PAPER, 4, 0.8)
    K.text(c, "赤道", cx + R + 16, cy, 26, "sans_medium", K.INK3, 1, "left")
    ty = cy + R * math.sin(math.radians(23.4))
    half = R * math.cos(math.radians(23.4))
    k = ease_out(clamp01(g.since(1) / 0.5))
    if k > 0:
        dash = skia.Paint(AntiAlias=True, Color=K.col(K.RED), StrokeWidth=7, Style=skia.Paint.kStroke_Style,
                          PathEffect=skia.DashPathEffect.Make([22, 14], 0))
        c.drawLine(cx - half, ty, cx - half + 2 * half * k, ty, dash)
        K.text(c, "南回归线", cx, cy + R + 60, 40, "serif_black", K.RED, k)
        K.text(c, "Tropic of Capricorn", cx, cy + R + 112, 30, "sans_medium", K.INK2, k)
        K.seg(c, cx + half * 0.5, ty + 8, cx + 40, cy + R + 28, K.RED, 3, k * 0.7)
    ks = clamp01(g.since(3) / 0.4)
    if ks > 0:
        K.spotlight(c, -360, ty - 40, 120, K.GOLD, 0.5 * ks)
        K.dot(c, -360, ty - 40, 44, K.GOLD, ks)
        for i in range(3):
            yy = ty - 70 + i * 30
            K.arrow(c, (-300, yy), (cx - half - 20, ty + (i - 1) * 6), K.GOLD, 6, ks, ks, 0, 20)
    for i, (txt, col) in enumerate((("古希腊时：冬至太阳在摩羯座", g.acc), ("如今：冬至太阳在人马座", X.SKY))):
        kk = clamp01(g.since(4 + 2 * i) / 0.35)
        if kk > 0:
            K.pill(c, 0, -360 + i * 76, txt, 32, col, K.PAPER, kk)


def niu_xiu(c, g, t, d):
    """牛宿一亮起并标名；第 4 拍右上角弹出“牛郎星在天鹰座”提示卡。"""
    named = {n["en"]: i for i, n in enumerate(X.sign(AB)["named"])}
    X.sky_card(c, 0, 60, 880, 560, AB, 1, g.t, 1, named["Dabih"], clamp01(g.since(1) / 0.35), "牛宿一|β Cap Dabih",
               clamp01(g.since(2) / 0.35), line_color=X.FAINT)
    k = clamp01(g.since(4) / 0.35)
    if k > 0:
        K.text_card(c, 230, -330, ["牛郎星＝河鼓二", "在【天鹰座】"], 34, 360, K.PAPER, K.INK, g.acc, k, 3,
                    0.4 + 0.6 * K.ease_out_back(k, 1.8), g.acc, "serif", 0.8)


def build():
    mid = [
        Shot(3, "希腊神话里，潘跳进河里，|下半身变成了鱼尾。", "希腊神话", [
            Custom(pan_river, x=540, y=760, at=0, enter="fade"),
            Label("潘", 620, 560, 32, at=1, fill=K.OTHER3, sfx="wood_high", note="牧神潘"),
            Label("怪物提丰", 210, 400, 32, at=2, fill=K.DARK, sfx="tom", note="提丰追来"),
        ], hits=[(4, "frame", 0.8, "跳进河里，水花溅起"), (6, "cymbal", 0.6, "化作海山羊游出")],
            note="牧神潘在河边被怪物提丰（乌云）追赶，第 4 拍跳进河里溅起水花，第 6 拍化作羊头鱼尾的海山羊游出"),
        Shot(2, "南回归线，英文叫|“摩羯座回归线”。", "天文观测", [
            Custom(tropic, x=540, y=820, at=0, enter="fade"),
        ], hits=[(1, "wood_low", 0.8, "南回归线画出"), (3, "rim", 0.9, "太阳光直射"), (4, "wood_high", 0.7, "古希腊时的说明"),
                 (6, "bongo_high", 0.7, "如今的说明")], text_beat=0,
            note="地球上画出红色虚线南回归线（Tropic of Capricorn），太阳光直射；标注古希腊时冬至太阳在摩羯座、如今在人马座"),
        Shot(2, "这里有“牛宿”，|牛郎星却不在这儿。", "中国星官", [
            Custom(niu_xiu, x=540, y=830, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.8, "牛宿一亮起"), (4, "bongo_low", 0.8, "“牛郎星在天鹰座”提示卡")], text_beat=0,
            note="摩羯座星图上牛宿一（β Cap）发光并标名，右上弹出提示卡：牛郎星是天鹰座的河鼓二"),
    ]
    return episode(
        10, AB, "摩羯座：|一个大大的三角形。", mid,
        refs=["奥维德《岁时记》；海吉努斯《天文的诗篇》"],
        notes=[
            "海山羊的来历：常见说法是牧神潘为躲避怪物提丰跳进尼罗河，入水的下半身变成鱼尾，上半身仍是山羊；也有说法认为摩羯座就是"
            "哺育宙斯的山羊阿玛尔忒亚。神话版本不一。",
            "南回归线的英文名 Tropic of Capricorn 来自古希腊罗马时代：那时冬至的太阳位于摩羯座。按 IAU 边界与岁差速度（约 72 年 1°）推算，"
            "冬至点约在公元前 130 年前后移入人马座，如今冬至太阳在人马座（射手座）。",
            "牛宿是二十八宿之一，牛宿一即摩羯座 β（Dabih）。民间说的“牛郎星”是天鹰座的河鼓二（Altair），并不在牛宿；"
            "古代“牵牛”一名在不同时期所指不同。",
            "片中摩羯座最亮的星为垒壁阵四（Deneb Algedi，δ Cap）。",
        ],
        hashtags="#摩羯座 #星座 #天文 #科普 #星空",
        cover_title="生日在摩羯座，|太阳却在【射手座】？", cover_sub="摩羯座：天上到底长什么样")
