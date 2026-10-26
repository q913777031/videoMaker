"""原创角色与场景：绵绵（小羊，背上的沙袋 = 睡眠压力）、钟大爷（闹钟肚子的公鸡 = 生物钟）、卧室。

角色在局部坐标中绘制：原点为双脚着地点，朝左；调用方用 canvas 变换摆放与缩放。
姿态参数都是 0–1 的连续量，便于逐帧插值。
"""

import math

import skia

from engine.gfx import draw_text

from .toon import (INK, burst, cloud, ellipse_pts, fill, glow, hose, ink, shape, smooth, speed_lines, wash)

WOOL, WOOL_SH = "#F4EDDD", "#D6C8AE"
FACE, FACE_SH, MUZZLE = "#4A3E3B", "#33292A", "#6E5E59"
LEG = "#3E3330"
SACK, SACK_SH = "#CDA367", "#9A7442"
GLOVE = "#FFFDF6"
RED, ORANGE, YELLOW, TEAL, BRASS, CREAM = "#D9412F", "#EC7A3C", "#F4C443", "#2E8C8A", "#E2AE3A", "#FFF6E2"


def glove(c, x, y, r: float = 26, rot: float = 0.0, boil: int = 0, seed: int = 0):
    """经典四指白手套（简化为圆掌 + 拇指）。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    shape(c, ellipse_pts(r * 0.55, -r * 0.3, r * 0.42, r * 0.3, 8), GLOVE, 6, boil, 0.6, seed + 1)
    shape(c, ellipse_pts(0, 0, r, r * 0.85, 12), GLOVE, 6, boil, 0.6, seed, shade=("#D9D2C2", 6, 8))
    for k in (-1, 1):
        p = skia.Path()
        p.moveTo(-r * 0.2, k * r * 0.25)
        p.lineTo(-r * 0.75, k * r * 0.3)
        ink(c, p, 4)
    c.restore()


def sheep(c, boil: int = 0, bend: float = 0.6, lid: float = 0.55, yawn: float = 0.0, sack: float = 1.0,
          look: float = 0.0):
    """绵绵。bend：被沙袋压弯的程度；lid：眼皮下垂程度；yawn：哈欠张嘴；sack：沙袋大小（0 时不画）；look：眼珠左右。"""
    fill(c, smooth(ellipse_pts(0, 0, 170, 22, 12)), "#000000", 0.28)
    for (hx, kx, fx), seed in (((40, 70, 62), 11), ((-60, -90, -95), 12)):
        hose(c, [(hx, -140), (kx, -80 + 10 * bend), (fx, -18)], 26, LEG, boil, 1.0, seed)
        shape(c, ellipse_pts(fx - 8, -12, 34, 18, 10), "#2A2220", 6, boil, 0.6, seed + 5)
    c.save()
    c.translate(0, -130)
    c.rotate(-20 * bend)
    c.translate(0, 130)
    # 沙袋在身后，先画
    if sack > 0:
        c.save()
        c.translate(95, -330)
        c.scale(sack, sack)
        sack_pts = [(-110, 40), (-130, -40), (-100, -130), (-40, -175), (10, -190), (60, -170),
                    (120, -110), (140, -20), (120, 60), (40, 100), (-60, 95)]
        shape(c, sack_pts, SACK, 8, boil, 1.4, 21, shade=(SACK_SH, -22, 18))
        shape(c, [(-10, -185), (-30, -235), (5, -225), (30, -250), (40, -200)], SACK, 7, boil, 1.0, 22)
        rope = skia.Path()
        rope.moveTo(-25, -190)
        rope.quadTo(10, -175, 45, -192)
        ink(c, rope, 9, "#6B4A28")
        ink(c, rope, 3)
        for k in range(6):
            st = skia.Path()
            st.moveTo(-70 + k * 25, 50 + 6 * math.sin(k))
            st.lineTo(-62 + k * 25, 62 + 6 * math.sin(k))
            ink(c, st, 3, "#7A5630")
        draw_text(c, "睡意", 5, -30, 74, "serif_black", "#6B4A28", 0.9)
        c.restore()
        strap = [(-80, -260), (-10, -330), (60, -350)]
        hose(c, strap, 10, "#7A5630", boil, 0.8, 23)
    cloud(c, [(-90, -205, 80), (-20, -245, 95), (60, -220, 85), (110, -170, 66), (-110, -150, 66),
              (-30, -150, 86), (50, -140, 80)], WOOL, 7, boil, 1.0, 30, shade=WOOL_SH)
    # 手臂垂着，手套
    hose(c, [(-95, -215), (-140, -160), (-150, -105)], 20, LEG, boil, 1.0, 40)
    glove(c, -152, -92, 26, 80, boil, 41)
    # 头：随压弯程度下沉
    c.save()
    c.translate(-185, -265 + 45 * bend)
    c.rotate(-10 - 12 * bend)
    for side, seed in ((-1, 50), (1, 51)):
        ear = [(side * 40, -30), (side * 95, -8 + 30 * bend), (side * 120, 10 + 40 * bend), (side * 70, 12)]
        shape(c, ear, FACE, 6, boil, 0.8, seed, shade=(FACE_SH, 0, 8))
    head = shape(c, ellipse_pts(0, 0, 66, 82, 14), FACE, 7, boil, 0.8, 52, shade=(FACE_SH, 10, 14))
    _ = head
    shape(c, ellipse_pts(-6, 42, 44, 30, 12), MUZZLE, 5, boil, 0.6, 53)
    for nx in (-20, 6):
        fill(c, smooth(ellipse_pts(nx, 36, 6, 4, 8)), INK)
    cloud(c, [(-30, -80, 28), (5, -92, 30), (38, -78, 26), (-50, -60, 22)], WOOL, 6, boil, 0.8, 54, shade=WOOL_SH)
    # 睡帽
    cap = [(-55, -95), (0, -120), (45, -100), (90, -60), (130, 10), (110, 18), (70, -40)]
    shape(c, cap, "#4F6BC9", 7, boil, 1.0, 55, shade=("#3A4F98", 6, 8))
    for k in range(3):
        sp = skia.Path()
        sp.moveTo(-30 + 40 * k, -110 + 18 * k)
        sp.lineTo(-10 + 40 * k, -80 + 18 * k)
        ink(c, sp, 10, "#FFFFFF")
    cloud(c, [(122, 22, 20)], "#FFFFFF", 5, boil, 0.6, 56)
    # 眼睛 + 下垂眼皮
    for ex, seed in ((-28, 60), (22, 61)):
        eye = smooth(ellipse_pts(ex, -12, 22, 28, 12), True, boil, 0.5, seed)
        fill(c, eye, "#FFFFFF")
        c.save()
        c.clipPath(eye, doAntiAlias=True)
        fill(c, smooth(ellipse_pts(ex - 6 + 8 * look, -2, 9, 12, 10)), INK)
        lid_y = -40 + 56 * lid
        fill(c, smooth([(ex - 40, -60), (ex + 40, -60), (ex + 40, lid_y), (ex, lid_y + 6), (ex - 40, lid_y)]), FACE)
        lp = skia.Path()
        lp.moveTo(ex - 24, lid_y)
        lp.quadTo(ex, lid_y + 8, ex + 24, lid_y)
        ink(c, lp, 5)
        c.restore()
        ink(c, eye, 5)
    if yawn > 0:
        shape(c, ellipse_pts(-8, 64, 18 * yawn + 4, 26 * yawn + 3, 10), "#7A1E24", 5, boil, 0.5, 62)
        fill(c, smooth(ellipse_pts(-8, 64 + 14 * yawn, 10 * yawn, 8 * yawn, 8)), "#E46C7A")
    else:
        mp = skia.Path()
        mp.moveTo(-26, 62)
        mp.quadTo(-8, 54, 10, 62)
        ink(c, mp, 5)
    c.restore()
    # 汗滴
    drop = [(-300, -360 + 40 * bend), (-288, -330 + 40 * bend), (-300, -318 + 40 * bend), (-312, -330 + 40 * bend)]
    shape(c, drop, "#9ED7F5", 4, boil, 0.4, 63)
    c.restore()


def rooster(c, hour: float, boil: int = 0, crash: float = 1.0, shout: float = 1.0):
    """钟大爷。hour：肚子闹钟的钟点；crash：0 为双镲合拢，1 为刚撞开；shout：张嘴大叫程度。"""
    fill(c, smooth(ellipse_pts(0, 0, 90, 14, 10)), "#000000", 0.25)
    for lx, seed in ((-28, 100), (28, 101)):
        hose(c, [(lx * 0.8, -60), (lx, -28), (lx, -6)], 10, ORANGE, boil, 0.6, seed)
        for dx in (-22, 0, 22):
            p = skia.Path()
            p.moveTo(lx, -6)
            p.lineTo(lx + dx, 4)
            ink(c, p, 9, ORANGE)
    # 尾羽
    for k, (color, ang) in enumerate(((TEAL, -0.9), ("#1F5F6A", -0.55), (ORANGE, -0.25))):
        a = ang
        pts = [(70, -150), (70 + 90 * math.cos(a - 0.5), -150 + 120 * math.sin(a - 0.5)),
               (70 + 170 * math.cos(a), -150 + 170 * math.sin(a)), (95 + 130 * math.cos(a), -120 + 130 * math.sin(a))]
        shape(c, pts, color, 6, boil, 0.8, 110 + k)
    # 闹钟铃 + 锤
    for bx, seed in ((-62, 120), (62, 121)):
        shape(c, ellipse_pts(bx, -258, 40, 30, 10), BRASS, 6, boil, 0.6, seed, shade=("#B5841E", 6, 6))
    # 闹钟肚子
    shape(c, ellipse_pts(0, -150, 108, 108, 18), RED, 8, boil, 0.8, 130, shade=("#A42D20", 12, 14))
    face = shape(c, ellipse_pts(0, -150, 84, 84, 18), CREAM, 5, boil, 0.5, 131)
    _ = face
    for k in range(12):
        a = math.radians(k * 30 - 90)
        r0 = 64 if k % 3 else 56
        p = skia.Path()
        p.moveTo(70 * math.cos(a), -150 + 70 * math.sin(a))
        p.lineTo(r0 * math.cos(a), -150 + r0 * math.sin(a))
        ink(c, p, 6 if k % 3 == 0 else 4)
    for ang, length, wdt in (((hour % 12) * 30, 38, 10), ((hour % 1) * 360, 58, 6)):
        a = math.radians(ang - 90)
        p = skia.Path()
        p.moveTo(0, -150)
        p.lineTo(length * math.cos(a), -150 + length * math.sin(a))
        ink(c, p, wdt)
    fill(c, smooth(ellipse_pts(0, -150, 9, 9, 8)), RED)
    # 头
    c.save()
    c.translate(0, -300)
    c.rotate(-8 * shout)
    shape(c, [(-18, -40), (-10, -78), (8, -60), (18, -90), (32, -62), (50, -78), (48, -38)], RED, 6, boil, 0.8, 140)
    shape(c, ellipse_pts(0, 0, 50, 48, 14), ORANGE, 7, boil, 0.8, 141, shade=("#C45A22", 8, 10))
    beak_open = 8 + 26 * shout
    shape(c, [(-44, -6), (-96, 2 - beak_open * 0.3), (-44, 10)], YELLOW, 5, boil, 0.4, 142)
    shape(c, [(-44, 14), (-86, 18 + beak_open * 0.6), (-40, 26)], YELLOW, 5, boil, 0.4, 143)
    shape(c, [(-36, 24), (-50, 52), (-26, 50)], RED, 5, boil, 0.5, 144)
    eye = smooth(ellipse_pts(-12, -10, 15, 18, 10), True, boil, 0.4, 145)
    fill(c, eye, "#FFFFFF")
    fill(c, smooth(ellipse_pts(-18, -8, 7, 9, 8)), INK)
    ink(c, eye, 4)
    brow = skia.Path()
    brow.moveTo(-34, -34)
    brow.lineTo(4, -24)
    ink(c, brow, 8)
    c.restore()
    # 翅膀手臂与镲
    spread = 120 + 90 * crash
    for side, seed in ((-1, 150), (1, 151)):
        hand = (side * spread, -215 - 20 * crash)
        hose(c, [(side * 80, -200), (side * (60 + spread * 0.4), -260), hand], 18, ORANGE, boil, 0.8, seed)
        c.save()
        c.translate(hand[0] + side * 26, hand[1])
        c.rotate(side * (70 - 25 * crash))
        shape(c, ellipse_pts(0, 0, 74, 20, 16), BRASS, 6, boil, 0.5, seed + 10, shade=("#B5841E", 0, 8))
        fill(c, smooth(ellipse_pts(0, -2, 16, 6, 8)), "#C99525")
        ink(c, smooth(ellipse_pts(0, -2, 16, 6, 8)), 4)
        c.restore()
        glove(c, hand[0], hand[1], 22, side * 30, boil, seed + 20)
        if crash > 0.3:
            speed_lines(c, hand[0] + side * 60, hand[1] - 20, -math.pi / 2 + side * 0.9, 4, 70 * crash, 0.35, 5, seed, boil)


def bedroom(c, boil: int = 0, lamp: float = 1.0, dawn: float = 0.0):
    """卧室：左上窗户（月亮、星星；dawn>0 时天边泛白、月亮淡去），右侧床与床头板；1080×1920 全幅。"""
    wash(c, (0, 0, 1080, 1420), "#232C5E", "#3B4280", seed=1, streaks=24)
    for k in range(9):
        p = skia.Path()
        p.moveTo(0, 1420 + k * 64)
        p.lineTo(1080, 1420 + k * 64 + 6)
        _ = p
    wash(c, (0, 1400, 1080, 1920), "#5A3B57", "#2C1E33", seed=2, streaks=14)
    for k in range(1, 8):
        p = skia.Path()
        p.moveTo(0, 1400 + k * k * 9)
        p.lineTo(1080, 1400 + k * k * 9)
        ink(c, p, 3, "#1E1424", 0.5)
    base = skia.Path()
    base.moveTo(0, 1400)
    base.lineTo(1080, 1400)
    ink(c, base, 8)
    # 窗
    shape(c, [(110, 330), (540, 330), (540, 830), (110, 830)], "#6E4B38", 8, boil, 0.8, 300)
    from engine.gfx import col, mix
    top, bot = mix("#0D1740", "#5B6FB8", dawn), mix("#283C86", "#FFB878", dawn)
    sky = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([(0, 360), (0, 800)], [col(top), col(bot)]))
    c.drawRect(skia.Rect.MakeLTRB(140, 360, 510, 800), sky)
    if dawn > 0:
        glow(c, 330, 820, 260, "#FFD27A", 0.6 * dawn)
    glow(c, 420, 470, 160, "#FFF1C2", 0.35 * (1 - dawn))
    moon = skia.Op(smooth(ellipse_pts(420, 470, 62, 62, 16)), smooth(ellipse_pts(450, 448, 56, 56, 16)),
                   skia.PathOp.kDifference_PathOp)
    fill(c, moon, "#FFF1C2", 1 - 0.6 * dawn)
    ink(c, moon, 5, alpha=1 - 0.6 * dawn)
    for sx, sy, r in ((210, 420, 10), (300, 560, 7), (220, 700, 9), (470, 650, 6), (360, 400, 5)):
        st = skia.Path()
        for k in range(8):
            a = math.pi * k / 4
            rr = r if k % 2 == 0 else r * 0.35
            q = (sx + rr * math.cos(a), sy + rr * math.sin(a))
            st.lineTo(*q) if k else st.moveTo(*q)
        st.close()
        fill(c, st, "#FFF6D6", 1 - dawn)
    for p0, p1 in (((325, 360), (325, 800)), ((140, 580), (510, 580))):
        bar = skia.Path()
        bar.moveTo(*p0)
        bar.lineTo(*p1)
        ink(c, bar, 22, "#6E4B38")
        ink(c, bar, 3)
    sill = [(90, 820), (560, 820), (560, 860), (90, 860)]
    shape(c, sill, "#7E5640", 7, boil, 0.6, 301)
    rod = skia.Path()
    rod.moveTo(50, 300)
    rod.lineTo(600, 300)
    ink(c, rod, 14, "#4A2C1B")
    ink(c, rod, 3)
    for kx in (50, 600):
        shape(c, ellipse_pts(kx, 300, 16, 16, 10), BRASS, 5, boil, 0.4, 305 + kx)
    for x0, x1, seed in ((60, 175, 310), (475, 590, 311)):
        cur = [(x0, 305), (x1, 305), (x1 - 20, 520), (x1 + 8, 760), (x1 - 10, 930), ((x0 + x1) / 2, 945), (x0 + 6, 930),
               (x0 - 6, 620)]
        shape(c, cur, "#8C3A5E", 7, boil, 1.0, seed, shade=("#6A2846", 14, 0))
        for k in (1, 2):
            fold = skia.Path()
            fx = x0 + (x1 - x0) * k / 3
            fold.moveTo(fx, 330)
            fold.quadTo(fx + 10, 640, fx - 4, 920)
            ink(c, fold, 4, "#5A1E3A")
    # 台灯光晕
    if lamp > 0:
        glow(c, 1000, 1150, 420, "#FFB45A", 0.22 * lamp)
    # 床头板 + 床
    shape(c, [(670, 1260), (670, 1010), (720, 950), (860, 925), (1000, 950), (1050, 1010), (1050, 1260)], "#8A5A3A", 8,
          boil, 0.8, 320, shade=("#5C3824", 14, 12))
    for x in (760, 860, 960):
        p = skia.Path()
        p.moveTo(x, 990)
        p.lineTo(x, 1230)
        ink(c, p, 5, "#4A2C1B")
    for px_, seed in ((650, 323), (1070, 324)):
        shape(c, [(px_ - 22, 1270), (px_ - 22, 960), (px_ + 22, 960), (px_ + 22, 1270)], "#6E4428", 7, boil, 0.6, seed)
        shape(c, ellipse_pts(px_, 940, 30, 30, 12), "#6E4428", 7, boil, 0.6, seed + 10, shade=("#4A2C1B", 8, 8))
    shape(c, ellipse_pts(860, 1240, 150, 55, 14), "#FFFDF4", 7, boil, 0.8, 321, shade=("#D9D3C1", 0, 12))
    quilt = [(560, 1290), (1090, 1270), (1090, 1460), (560, 1470)]
    shape(c, quilt, "#D9A04A", 8, boil, 1.0, 322, shade=("#B87F2E", 0, 16))
    for k in range(1, 5):
        p = skia.Path()
        p.moveTo(560 + k * 110, 1290 - k * 4)
        p.lineTo(560 + k * 110, 1468 - k * 2)
        ink(c, p, 4, "#9C5A2A")
    p = skia.Path()
    p.moveTo(560, 1380)
    p.lineTo(1090, 1365)
    ink(c, p, 4, "#9C5A2A")


def sfx_word(c, text: str, x: float, y: float, size: float, boil: int = 0, rot: float = -8):
    """拟声字：锯齿爆炸框 + 描边大字。"""
    burst(c, x, y, size * 1.25, 11, "#FFD84A", boil, 400, rot=math.radians(rot))
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    draw_text(c, text, 0, 0, size, "serif_black", RED, stroke=(INK, 12))
    c.restore()
