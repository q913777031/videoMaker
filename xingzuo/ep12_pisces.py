"""12 双鱼座：双鱼座，天上到底长什么样？"""

import math

import skia

from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from adler import kit as K
from adler.core import Custom, Label, Shot

from . import kit_xz as X
from .series import episode

AB = "Psc"
FISH1 = "#E07A6B"
FISH2 = "#5B8FC7"
RIVER = "#5B8FB0"
EQUINOX = (-0.33, -0.14)      # 当前春分点在 J2000 坐标中的位置（黄经约 −0.36°）：赤经 −0.33°、赤纬 −0.14°


def fish(c, x, y, s, color, t, face=1, alpha=1.0):
    """一条鱼：椭圆身体 + 摆动的三角尾（以身体中心为原点）。"""
    sway = 0.35 * math.sin(t * 6)
    with K.at(c, x, y, 0, s / 200):
        c.save()
        c.scale(face, 1)
        with K.paper(c, alpha, 0.9):
            body = skia.Path()
            body.addOval(skia.Rect.MakeXYWH(-90, -48, 180, 96))
            c.drawPath(body, K.paint(color))
            K.poly(c, [(-80, 0), (-150, -50 + 30 * sway), (-150, 50 + 30 * sway)], K.shade(color, 0.15))
            K.poly(c, [(-10, -44), (30, -78), (40, -40)], K.shade(color, 0.15))
            K.dot(c, 50, -10, 9, K.PAPER)
            K.dot(c, 53, -10, 5, K.INK)
        c.restore()


def typhon(c, x, y, s, t, alpha=1.0):
    """怪物提丰：翻滚的乌云，两只发光的眼睛。"""
    with K.fade(c, alpha):
        with K.paper(c, 1, 1.0):
            for i, (dx, dy, r) in enumerate(((-60, 10, 70), (0, -30, 85), (70, 0, 72), (20, 40, 66), (-90, 50, 50))):
                K.dot(c, x + dx * s + 6 * math.sin(t * 2 + i), y + dy * s, r * s, "#4A4F63")
        for dx in (-22, 22):
            K.dot(c, x + dx * s, y - 20 * s, 9 * s, "#FFB84D")


def two_fish(c, g, t, d):
    """第 2 拍提丰出现；母子二人跳进河里（第 4 拍），化作两条鱼（第 6 拍），第 8 拍一根绳把两条鱼系在一起。"""
    wy0 = 120
    for i in range(4):
        wy = wy0 + i * 26
        path = skia.Path()
        path.moveTo(-520, wy)
        for j in range(27):
            px = -520 + j * 40
            path.lineTo(px, wy + 10 * math.sin(j * 0.9 + g.t * 2 + i))
        c.drawPath(path, K.paint(K.mix(RIVER, K.PAPER, 0.25 + 0.15 * i), 1, 6))
    k_ty = clamp01(g.since(2) / 0.4)
    if k_ty > 0:
        typhon(c, -330, -250, 1.1, g.t, k_ty)
    if g.since(4) < 0:
        run = ease_in_out(clamp01(g.t / max(0.1, g.b(4))))
        x = lerp(-120, 80, run)
        K.figure(c, x, wy0 - 10, 250, "reach" if g.since(2) >= 0 else "stand", "#B9768A", hair="long",
                 mood="surprised" if g.since(2) >= 0 else "calm", lift=0.8)
        K.figure(c, x + 110, wy0 - 10, 150, "stand", K.GOLD, hair="short", mood="worried" if g.since(2) >= 0
                 else "smile", lift=0.8)
        return
    sp = clamp01(g.since(4) / 0.5)
    if sp < 1:
        for i in range(10):
            a = -math.pi * (0.1 + 0.8 * i / 9)
            r = 40 + 160 * ease_out(sp)
            K.dot(c, 140 + r * math.cos(a), wy0 + r * math.sin(a), 12 * (1 - sp), K.mix(RIVER, K.PAPER, 0.3))
    kf = clamp01(g.since(6) / 0.5)
    if kf <= 0:
        return
    swim = g.since(6)
    p1 = (40 + 30 * swim, 250 + 10 * math.sin(g.t * 2.2))
    p2 = (-200 + 25 * swim, 370 + 10 * math.sin(g.t * 2.2 + 1))
    kc = ease_out(clamp01(g.since(8) / 0.5))
    if kc > 0:
        path = skia.Path()
        path.moveTo(p1[0] - 120, p1[1])
        path.cubicTo(p1[0] - 260, p1[1] + 40, p2[0] + 260, p2[1] - 120, p2[0] + 110, p2[1])
        meas = skia.PathMeasure(path, False)
        seg = skia.Path()
        meas.getSegment(0, meas.getLength() * kc, seg, True)
        c.drawPath(seg, K.paint(K.GOLD, kf, 6))
    fish(c, p1[0], p1[1], 170, FISH1, g.t, 1, kf)
    fish(c, p2[0], p2[1], 140, FISH2, g.t + 0.7, 1, kf)


def equinox(c, g, t, d):
    """双鱼座星图上的当前春分点：第 1 拍红色标记落下，第 3 拍箭头指向西边的宝瓶座并标“约 2597 年”。"""
    def extra(c, P):
        k = clamp01(g.since(1) / 0.35)
        if k <= 0:
            return
        px, py = P(*EQUINOX)
        K.ring(c, px, py, 26 + 20 * (1 - k), K.RED, 7, k)
        K.dot(c, px, py, 8, K.RED, k)
        K.text(c, "春分点（现在）", px - 30, py - 50, 32, "sans_medium", "#FFC9B8", k, "right")
        ka = clamp01(g.since(3) / 0.5)
        if ka > 0:
            K.arrow(c, (px + 30, py + 15), (px + 220, py + 55), "#FFC9B8", 6, ka, ka, -0.1, 22)
            K.text(c, "约 2597 年进入宝瓶座", px + 140, py + 100, 30, "sans_medium", "#FFC9B8", ka)
    X.sky_card(c, 0, 0, 900, 660, AB, 1, g.t, 1, margin=150, extra=extra)


def city_glow(c, g, t, d):
    """右更二标名后（第 1 拍），第 3 拍城市灯光从卡片底部升起，暗星一颗颗淹没。"""
    kg = ease_in_out(clamp01(g.since(3) / 1.2))

    def extra(c, P):
        if kg <= 0:
            return
        w, h = 900, 660
        top = h / 2 - h * 1.05 * kg
        sh = skia.GradientShader.MakeLinear([(0, h / 2), (0, top)], [K.col("#E8A25C", 0.92), K.col("#E8A25C", 0.0)],
                                            [0, 1])
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, top, w, h / 2 - top), skia.Paint(AntiAlias=True, Shader=sh))
        for i in range(9):
            bx = -w / 2 + 40 + i * 100
            bh = 60 + 70 * abs(math.sin(i * 2.1))
            K.rr(c, bx, h / 2 - bh / 2, 70, bh, 6, "#3A3346", kg)
            for j in range(int(bh // 30)):
                K.rr(c, bx - 12 + 24 * (j % 2), h / 2 - bh + 20 + 30 * (j // 2), 10, 12, 2, "#FFD27A", 0.8 * kg)
    X.sky_card(c, 0, 0, 900, 660, AB, 1, g.t, 1 - 0.55 * kg, 0, clamp01(g.since(0.5) / 0.35), "右更二|3.6 等",
               clamp01(g.since(1) / 0.35), extra=extra)


def build():
    mid = [
        Shot(3, "希腊神话里，母子俩|变成鱼，用绳子系在一起。", "希腊神话", [
            Custom(two_fish, x=540, y=760, at=0, enter="fade"),
            Label("阿佛洛狄忒与厄洛斯", 650, 560, 30, at=1, out=4, fill="#B9768A", sfx="wood_high", note="母子二人"),
            Label("怪物提丰", 210, 660, 30, at=2, fill=K.DARK, sfx="tom", note="提丰追来"),
        ], hits=[(4, "frame", 0.8, "跳进河里，水花溅起"), (6, "bongo_high", 0.8, "化作两条鱼"), (8, "shaker", 0.8, "绳子系住两条鱼")],
            note="阿佛洛狄忒与厄洛斯被提丰（乌云）追赶，第 4 拍跳进河里，第 6 拍化作两条鱼，第 8 拍一根金绳把两条鱼系在一起"),
        Shot(2, "现在的春分点，|就在双鱼座里。", "天文观测", [
            Custom(equinox, x=540, y=820, at=0, enter="fade"),
        ], hits=[(1, "rim", 0.9, "春分点标记落下"), (3, "wood_high", 0.8, "箭头指向宝瓶座")], text_beat=0,
            note="双鱼座星图上落下红色春分点标记，箭头指向西边的宝瓶座：约 2597 年进入"),
        Shot(2, "最亮的星也很暗，|城里几乎看不见。", "天文观测", [
            Custom(city_glow, x=540, y=820, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.8, "右更二标名"), (3, "bongo_low", 0.8, "城市灯光升起")], text_beat=0,
            note="右更二（3.6 等）标名后，城市灯光从底部升起，整片双鱼座被淹没"),
    ]
    return episode(
        12, AB, "双鱼座：|一个大V字连着两条鱼。", mid,
        refs=["奥维德《岁时记》；海吉努斯《天文的诗篇》"],
        notes=[
            "双鱼的来历：常见说法是爱神阿佛洛狄忒与儿子厄洛斯为躲避怪物提丰跳进河里，化作两条鱼，并用绳子系在一起以免失散；"
            "也有版本说是两条鱼驮着他们逃走。神话版本不一。",
            "当前春分点位于双鱼座。按 IAU 星座边界，春分点约公元前 68 年由白羊座移入双鱼座，约 2597 年才会移入宝瓶座"
            "（Jean Meeus 的计算，EarthSky 转述）；占星所说的“宝瓶座时代”起点说法不一，与天文边界不是一回事。",
            "双鱼座最亮的星是右更二（Alpherg，η Psc），视星等约 3.6；在光污染明显的城市里，3–4 等星已很难看见。片中城市灯光为示意。",
        ],
        hashtags="#双鱼座 #星座 #天文 #科普 #星空",
        cover_title="生日在双鱼座，|太阳却在【水瓶座】？", cover_sub="双鱼座：天上到底长什么样")
