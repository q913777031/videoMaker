"""02 自卑感：觉得自己不如别人，是坏事吗？"""

import math

import skia

from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, ease_out_back, lerp

from . import kit as K
from .core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

ACC = "#D9962B"
GROUND = 1130
GRAY = "#A4A2AF"          # 自卑感：小灰云
SEA = "#86A9B6"
SAND = "#E6D3B0"
ROBE = "#D6C6A6"
STAGE = skia.Rect.MakeLTRB(60, 330, 1020, 1262)


def ground(g):
    K.ground(g.c, GROUND)


# ---------------------------------------------------------------- 通用小件

def pose_geo(s, p, face=1.0, bob=0.0):
    """按 kit.figure 的骨架算出脚底原点坐标系下的近侧手、头、肩、髋位置（用于挂道具）。"""
    d = K.pose(p)
    u = s
    thigh, shin, upper, fore = 0.235 * u, 0.225 * u, 0.19 * u, 0.18 * u

    def leg_extent(a1, a2):
        (_, ey), (_, fy) = K._limb(0, 0, a1, a2, thigh, shin, 1)
        return max(ey, fy)

    hip_y = -d["seat"] * u if d["seat"] > 0 else -max(leg_extent(d["ll1"], d["ll2"]), leg_extent(d["rl1"], d["rl2"]))
    hip_y -= bob * u
    lean = math.radians(d["lean"])
    sh_x = face * 0.30 * u * math.sin(lean)
    sh_y = hip_y - 0.30 * u * math.cos(lean)
    _, hand = K._limb(sh_x + 0.06 * u * face, sh_y + 0.03 * u, d["la1"], d["la2"], upper, fore, face)
    hd = math.radians(d["head"])
    head = (sh_x + face * 0.15 * u * math.sin(lean + hd * 0.5), sh_y - 0.15 * u * math.cos(lean + hd * 0.5))
    return dict(hand=hand, head=head, sh=(sh_x, sh_y), hip=(0.0, hip_y), r=0.16 * u)


def fig_plus(c, g, el_t, d):
    """人物 + 附件：under(c, g, geo, d) 画在人物之下，attach(c, g, geo, d) 画在人物之上。"""
    s, p, face = d["s"], d.get("pose", "stand"), d.get("face", 1)
    bob = 0.006 * math.sin(g.t * 2.6 + d["x"] * 0.02)
    geo = pose_geo(s, p, face, bob)
    if d.get("under"):
        d["under"](c, g, geo, d)
    K.figure(c, 0, 0, s, p, d.get("color", K.HERO), K.SKIN, 1, face, d.get("mood", "calm"), d.get("hair"),
             d.get("hair_color"), bob, d.get("lift", 1.0), d.get("look", 0.0))
    if d.get("attach"):
        d["attach"](c, g, geo, d)


def FigPlus(x, y, s, **kw):
    kw.setdefault("enter", "rise")
    return Custom(fig_plus, x=x, y=y, s=s, **kw)


def gcloud(c, x, y, s, alpha=1.0, color=GRAY, lift=0.6):
    K.icon(c, "cloud", x, y, s, color, alpha, lift)


def cloud_el(c, g, el_t, d):
    gcloud(c, 0, 0, d.get("cs", 110))


# ---------------------------------------------------------------- 镜 1：身边的人都在长高

GROWERS = [  # x, 原身高, 长高后, 颜色, 发型, 朝向, 拍, 音效, 增益, 长处
    (180, 285, 370, K.OTHER, "bun", 1, 2, "wood_low", 0.85, "成绩好"),
    (348, 280, 355, K.OTHER2, None, 1, 3, "wood_high", 0.75, "人缘好"),
    (748, 285, 385, K.OTHER3, "long", -1, 4, "wood_low", 0.8, "会画画"),
    (918, 280, 362, "#9C8FB0", "cap", -1, 5, None, 1.0, "跑得快"),
]


# ---------------------------------------------------------------- 镜 2：镜子里更小更灰的自己

def mirror(c, g, el_t, d):
    k = d.get("shrink", 0.0)
    w, h = 300, 540
    cy = -70 - h / 2
    for sgn in (-1, 1):
        K.seg(c, sgn * 110, 0, sgn * 46, cy + h * 0.32, K.shade(K.DARK, 0.1), 14)
    oval = skia.Rect.MakeXYWH(-w / 2, cy - h / 2, w, h)
    with K.paper(c, 1, 0.9):
        c.drawOval(skia.Rect.MakeXYWH(-w / 2 - 18, cy - h / 2 - 18, w + 36, h + 36), K.paint(K.DARK))
        c.drawOval(oval, K.paint(K.mix(K.tint(ACC, 0.82), "#DCE3E6", 0.5)))
    c.save()
    path = skia.Path()
    path.addOval(oval)
    c.clipPath(path, doAntiAlias=True)
    K.rr(c, 0, cy + h / 2 - 40, w, 80, 0, K.mix("#CBD3D6", K.INK3, 0.2), 0.7)
    col = K.mix(K.HERO, "#9D9BA7", k)
    s = lerp(290, 185, ease_in_out(k))
    p = K.blend("stand", "sad", k)
    K.figure(c, 0, cy + h / 2 - 60, s, p, col, K.mix(K.SKIN, "#C9C3BC", k), 1, -1,
             "sad" if k > 0.5 else "calm", "short", None, 0, 0.3, -0.4 * k)
    c.restore()
    for dx, dy, L in ((-0.3, -0.2, 0.16), (-0.18, -0.32, 0.1)):
        K.seg(c, w * dx, cy + h * dy, w * (dx + L), cy + h * (dy - L * 1.3), K.PAPER, 9, 0.55)


# ---------------------------------------------------------------- 镜 5–6：门把手、巨人与箱子

DOOR_X = 820
HANDLE_Y = GROUND - 335


def door(c, g, el_t, d):
    o = clamp01(d.get("open", 0.0))
    w, h = 280, 640
    with K.paper(c, 1, 0.8):
        K.rr(c, 0, -h / 2 - 10, w + 36, h + 20, 8, K.shade(K.DARK, 0.12))
        K.rr(c, 0, -h / 2, w, h, 4, K.GOLD if o > 0 else K.DARK)
        pw = w * (1 - 0.82 * ease_in_out(o))
        c.drawRect(skia.Rect.MakeXYWH(w / 2 - pw, -h, pw, h), K.paint(K.mix(K.DARK, K.HERO, 0.35)))
        for yy in (-h * 0.78, -h * 0.36):
            K.rr_stroke(c, w / 2 - pw / 2, yy, pw * 0.7, h * 0.3, 6, K.shade(K.mix(K.DARK, K.HERO, 0.35), 0.18), 5)
        hx = w / 2 - pw + 32
        K.rr(c, hx + 10, HANDLE_Y - GROUND, 46, 16, 8, K.GOLD)
        K.dot(c, hx, HANDLE_Y - GROUND, 12, K.shade(K.GOLD, 0.2))
    if o > 0:
        K.spotlight(c, 0, -h * 0.45, 520, K.GOLD, 0.45 * o)


def giant(c, g, el_t, d):
    """大人：只看得见腿和腰（画面裁在舞台上沿）；从左边走进来，第 2 拍落下最后一步。"""
    s = 1250
    k = g.span(0, 2)
    x = lerp(-360, d["gx"], k)
    walking = 0 < k < 1
    p = K.walk((x + 360) / (0.28 * s), math.sin(math.pi * k) if walking else 0.0)
    k2 = g.span(9, 11) if d.get("leave") else 0.0
    if k2 > 0:
        x = lerp(d["gx"], 1400, k2)
        p = K.walk((x - d["gx"]) / (0.28 * s), math.sin(math.pi * k2))
    c.save()
    c.clipRect(STAGE)
    K.figure(c, x, GROUND, s, p, K.OTHER2, K.OTHER2, 1, 1, "calm", None, None, 0, 0.7)
    c.restore()


def box(c, g, el_t, d):
    K.seat(c, 0, 0, 170, 130, "#B88A5E")
    for dx in (-40, 40):
        K.seg(c, dx, -110, dx, -14, K.shade("#B88A5E", 0.12), 5, 0.6)


# ---------------------------------------------------------------- 镜 7：病床上的孩子 → 医生

def sickbed(c, w, h):
    """回忆照片里的小场景：窗下的病床，瘦小的孩子躺着发烧。"""
    fl = h / 2 - 14
    K.rr(c, 0, fl + 2, w, 26, 0, "#B7A386")
    K.rr(c, w * 0.22, -h * 0.22, 120, 96, 6, K.tint("#9FB8C4", 0.3))
    K.seg(c, w * 0.22, -h * 0.22 - 48, w * 0.22, -h * 0.22 + 48, "#B7A386", 6)
    K.seg(c, w * 0.22 - 60, -h * 0.22, w * 0.22 + 60, -h * 0.22, "#B7A386", 6)
    bx0, bx1 = -w * 0.42, w * 0.3
    K.rr(c, bx0 + 10, fl - 70, 22, 140, 6, "#7B6652")
    K.rr(c, bx1 - 10, fl - 44, 20, 88, 6, "#7B6652")
    K.rr(c, (bx0 + bx1) / 2, fl - 40, bx1 - bx0 - 20, 30, 8, "#8C7660")
    K.rr(c, bx0 + 62, fl - 70, 80, 30, 14, K.PAPER)
    fx = bx0 + 62 + 0.91 * 190
    with K.at(c, fx, fl - 62, -90):
        K.figure(c, 0, 0, 190, "stand", K.mix(K.HERO, "#9D9BA7", 0.3), K.SKIN, 1, 1, "sad", "short", None, 0, 0.2)
    K.rr(c, (bx0 + 100 + fx + 14) / 2, fl - 62, fx + 14 - bx0 - 100, 44, 18, K.tint(ACC, 0.4))
    K.rr(c, bx0 + 62, fl - 96, 46, 14, 7, K.PAPER)
    for i in range(3):
        K.seg(c, bx0 + 30 + i * 22, fl - 128 - i * 4, bx0 + 38 + i * 22, fl - 146 - i * 4, K.RED, 4, 0.6)
    K.rr(c, w * 0.4, fl - 34, 50, 68, 6, "#9C8466")
    K.rr(c, w * 0.4, fl - 84, 20, 32, 6, K.tint(K.RED, 0.3))


def med_bag(c, g, geo, d):
    hx, hy = geo["hand"]
    K.seg(c, hx, hy, hx, hy + 22, K.DARK, 6)
    with K.paper(c, 1, 0.5):
        K.rr(c, hx, hy + 62, 120, 84, 14, "#6A4434")
        K.rr(c, hx, hy + 30, 120, 18, 8, K.shade("#6A4434", 0.2))
        K.rr(c, hx, hy + 66, 34, 10, 3, K.PAPER)
        K.rr(c, hx, hy + 66, 10, 34, 3, K.PAPER)


# ---------------------------------------------------------------- 镜 8–10：牵着灰云

BALLOON = (60, -600)


def balloon(c, g, geo, d):
    hx, hy = geo["hand"]
    tx, ty = BALLOON
    path = skia.Path()
    path.moveTo(hx, hy)
    path.quadTo((hx + tx) / 2 + 26 * math.sin(g.t * 1.7), (hy + ty) / 2, tx, ty + 62)
    c.drawPath(path, K.paint(K.INK2, 1, 3))
    gcloud(c, tx, ty + 5 * math.sin(g.t * 1.9), 190)


def wind_cloud(c, g, el_t, d):
    """有表情的灰云：第 2 拍鼓起腮帮吹风。"""
    puff = d.get("puff", 0.0)
    gcloud(c, 0, 0, 230 * (1 + 0.08 * puff))
    for sx in (-34, 6):
        if puff > 0.5:
            K.seg(c, sx - 10, -10, sx + 10, -10, K.INK, 5)
        else:
            K.dot(c, sx, -10, 7, K.INK)
    K.ring(c, 60, 16, 10 + 6 * puff, K.INK, 5)
    k = g.since(2)
    if k > 0:
        for i in range(6):
            ph = (k * 1.4 + i / 6) % 1.0
            y = -40 + i * 22
            x0 = 110 + ph * 480
            a = math.sin(ph * math.pi) * min(1, k * 3)
            K.seg(c, x0, y + ph * 140, x0 + 90, y + ph * 140 + 24, K.tint(ACC, 0.2), 7, a)


def signpost(c, g, el_t, d):
    txt, dr = d["text"], d["dir"]
    with K.paper(c, 1, 0.7):
        K.rr(c, 0, -170, 20, 340, 6, "#8C6E52")
        w, h = 250, 84
        y = -300
        pts = [(-w / 2, y - h / 2), (w / 2, y - h / 2), (w / 2 + 34, y), (w / 2, y + h / 2), (-w / 2, y + h / 2)]
        if dr < 0:
            pts = [(-x_, y_) for x_, y_ in pts]
        K.poly(c, pts, d.get("fill", ACC))
        K.text(c, txt, dr * 10, y, 42, "serif", K.PAPER)


# ---------------------------------------------------------------- 镜 11–12：海边的德摩斯梯尼

def seaside(g):
    c, t = g.c, g.t
    panel = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(72, 830, 1008, 1196), 28, 28)
    with K.paper(c, 1, 0.5):
        c.drawRRect(panel, K.paint(K.mix(SEA, K.BG, 0.25)))
    c.save()
    c.clipRRect(panel, doAntiAlias=True)
    # 远处的海与浪
    for i in range(4):
        y = 880 + i * 62
        path = skia.Path()
        path.moveTo(60, y)
        for x in range(60, 1030, 20):
            path.lineTo(x, y + 7 * math.sin(x * 0.02 + t * (1.6 + 0.3 * i) + i))
        c.drawPath(path, K.paint(K.tint(SEA, 0.55), 0.7, 5))
    # 沙滩
    path = skia.Path()
    path.moveTo(60, 1110)
    path.quadTo(540, 1070, 1020, 1120)
    path.lineTo(1020, 1200)
    path.lineTo(60, 1200)
    path.close()
    c.drawPath(path, K.paint(SAND))
    c.restore()
    # 石柱
    with K.paper(c, 1, 0.8):
        x0 = 140
        K.rr(c, x0, 1110, 130, 26, 4, "#D8CCB6")
        K.rr(c, x0, 835, 92, 530, 2, "#E4DAC6")
        for dx in (-30, -10, 10, 30):
            K.seg(c, x0 + dx, 590, x0 + dx, 1080, "#CFC2AA", 5)
        K.rr(c, x0, 560, 140, 30, 4, "#D8CCB6")
        K.rr(c, x0, 538, 110, 18, 4, "#CFC2AA")
    # 礁石
    with K.paper(c, 1, 0.6):
        rock = skia.Path()
        rock.moveTo(220, 1120)
        rock.quadTo(250, 1060, 330, 1058)
        rock.quadTo(420, 1056, 450, 1120)
        rock.close()
        c.drawPath(rock, K.paint("#8E8576"))


def splash(c, g, el_t, d):
    """浪花拍岸：在给定拍点上涌起一团白沫和水滴。"""
    for b, big in d["at_beats"]:
        dt = g.since(b)
        if dt < 0 or dt > 0.9:
            continue
        k = ease_out(dt / 0.5)
        a = 1 - clamp01((dt - 0.3) / 0.6)
        for i in range(9):
            ang = math.radians(-160 + i * 17)
            r = (60 + 120 * big) * k
            K.dot(c, math.cos(ang) * r, math.sin(ang) * r * 1.3 + 40 * dt * dt * 9, 10 + 6 * big, K.PAPER, a)
        K.dot(c, 0, 10, 50 * k * (0.6 + big * 0.6), K.tint(SEA, 0.7), a * 0.8)


def robe_under(c, g, geo, d):
    s = d["s"]
    sx, sy = geo["sh"]
    path = skia.Path()
    path.moveTo(sx - 0.14 * s, sy + 0.03 * s)
    path.lineTo(sx + 0.14 * s, sy + 0.03 * s)
    path.lineTo(0.2 * s, -0.08 * s)
    path.quadTo(0, -0.04 * s, -0.2 * s, -0.08 * s)
    path.close()
    c.drawPath(path, K.paint(ROBE))


def robe_over(c, g, geo, d):
    s = d["s"]
    sx, sy = geo["sh"]
    hx, hy = geo["hip"]
    f = d.get("face", 1)
    K.seg(c, sx + 0.08 * s * f, sy + 0.04 * s, hx - 0.1 * s * f, hy + 0.04 * s, ACC, 0.05 * s)
    voice = d.get("voice", 0.0)
    if voice > 0:
        x0, y0 = geo["head"][0] + 0.2 * s * f, geo["head"][1] + 0.04 * s
        for i in range(3):
            ph = (g.t * 1.6 + i / 3) % 1.0
            r = (40 + 150 * ph) * (0.5 + voice)
            path = skia.Path()
            path.addArc(skia.Rect.MakeXYWH(x0 - r, y0 - r, 2 * r, 2 * r), -40 if f > 0 else 140, 80)
            c.drawPath(path, K.paint(ACC, (1 - ph) * min(1, voice * 1.5), 6 + 8 * voice))


def pebble(c, g, el_t, d):
    c.drawOval(skia.Rect.MakeXYWH(-13, -9, 26, 18), K.paint("#77706A"))
    K.dot(c, -4, -3, 3, "#A39C95")


def crowd_cheer(c, g, el_t, d):
    k = g.p(d["cheer"], 0.3)
    people = [(640, K.OTHER, "bun", 225), (750, K.OTHER3, None, 245), (860, K.OTHER2, "short", 235),
              (960, "#9C8FB0", "long", 215)]
    for i, (x, col, hair, s) in enumerate(people):
        ph = g.t * 9 + i * 1.3
        p = K.blend("stand", "cheer", k * (0.85 + 0.15 * math.sin(ph))) if k > 0 else "stand"
        K.figure(c, x - d["x"], 1175 - d["y"] - (8 * abs(math.sin(ph)) if k > 0 else 0), s, p, col, K.SKIN, 1, -1,
                 "happy" if k > 0 else "calm", hair, None, 0.006 * math.sin(g.t * 2.4 + i), 0.6)
    if k > 0:
        c.save()
        c.clipRect(STAGE)
        K.confetti(c, 800, 900, g.since(d["cheer"]), [ACC, K.HERO, K.RED, K.GREEN], 30, 7)
        c.restore()


# ---------------------------------------------------------------- 镜 13：笔记卡

def typed(c, s, x, y, size, k, color=K.INK, font="serif"):
    n = len(s)
    m = int(round(n * clamp01(k)))
    if m <= 0:
        return
    w = K.text_w(s, size, font)
    K.text(c, s[:m], x - w / 2, y, size, font, color, 1, "left")


def notebook(c, g, el_t, d):
    rows = [("不敢当众说话", "多练习表达", 2, 6), ("身体总是很弱", "坚持去锻炼", 8, 12)]

    def draw(c, w, h):
        K.text(c, "让我自卑的事", -215, -205, 38, "serif", ACC)
        K.text(c, "我想变好的地方", 215, -205, 38, "serif", ACC)
        K.seg(c, -400, -160, 400, -160, K.LINE, 4)
        K.seg(c, 0, -140, 0, 240, K.LINE, 4)
        for i, (a, b, k0, k1) in enumerate(rows):
            y = -60 + i * 170
            K.seg(c, -380, y + 50, -50, y + 50, K.LINE, 3)
            K.seg(c, 50, y + 50, 380, y + 50, K.LINE, 3)
            typed(c, a, -215, y, 40, g.since(k0) / 0.5, K.INK2)
            pa = clamp01(g.since(k0 + 1) / 0.4)
            if pa > 0:
                K.arrow(c, (-40, y), (60, y), ACC, 8, 1, pa, 0, 24)
            typed(c, b, 215, y, 40, g.since(k0 + 2) / 0.5, K.INK)
            pc = clamp01(g.since(k1) / 0.35)
            if pc > 0:
                K.dot(c, 375, y, 30 * ease_out_back(pc, 2), K.GREEN)
                path = skia.Path()
                path.moveTo(361, y)
                path.lineTo(372, y + 11)
                path.lineTo(391, y - 10)
                c.drawPath(path, K.paint(K.PAPER, 1, 6))

    K.card(c, 0, 0, 880, 560, K.PAPER, 1, 22, 1.0, -1, 1, ACC, draw)


# ---------------------------------------------------------------- 镜 14：起跑线

def track(g):
    c = g.c
    K.rr(c, 540, GROUND + 40, 960, 80, 10, K.tint("#C77E5E", 0.35))
    K.seg(c, 70, GROUND + 2, 1010, GROUND + 2, K.PAPER, 4, 0.8)
    K.seg(c, 70, GROUND + 78, 1010, GROUND + 78, K.PAPER, 4, 0.8)
    K.rr(c, 390, GROUND + 40, 16, 80, 3, K.PAPER)


# ---------------------------------------------------------------- 分镜

def build() -> Episode:
    shots = [
        # 1：身边的人一个个“长高”，主角缩肩
        Shot(3, "身边的人|好像都比我强。", "情境演绎", [
            *[Fig(x, GROUND, s0, at=0, color=col, hair=hair, face=f, mood="calm",
                  moves=[(b, dict(s=s1, pose="proud", mood="smile" if b < 5 else "happy", dur=0.32, ease="out",
                                  sfx=sfx, gain=gn, note=f"{lab}的人长高" if sfx else ""))])
              for x, s0, s1, col, hair, f, b, sfx, gn, lab in GROWERS],
            *[Label(lab, x, GROUND - s1 * 1.08 - 46, 30, at=b, fill=ACC if b % 2 == 0 else K.INK2)
              for x, s0, s1, col, hair, f, b, sfx, gn, lab in GROWERS],
            Fig(540, GROUND, 320, at=0, hair="short", mood="calm",
                moves=[(6, dict(look=1.0, mood="open")),
                       (8, dict(pose="sad", mood="sad", s=290, look=-0.6, sfx="tom", gain=0.9,
                                note="主角缩肩、低头"))]),
        ], draw=ground,
            note="主角站在中间，身边四个人按拍依次“长高”，头顶各弹出一个长处；主角抬头看了看，缩肩低头"),

        # 2：镜子里更小更灰的自己
        Shot(3, "“我不够好”的感觉，|你也有过吗？", "情境演绎", [
            Custom(mirror, x=760, y=GROUND, at=1, enter="pop", shrink=0.0, sfx="wood_low", gain=0.8,
                   note="落地镜出现",
                   moves=[(2, dict(shrink=1.0, dur=0.9, sfx="shaker", note="镜中的倒影变小、变灰"))]),
            Fig(320, GROUND, 340, at=0, hair="short", mood="calm",
                moves=[(2, dict(mood="worried")),
                       (8, dict(pose="sad", mood="sad", look=-0.5, sfx="rim", gain=0.8, note="主角垂下头"))]),
            Bubble("我不够好", 330, 590, 48, at=4, tail=(0.1, 1), think=True, sfx="bongo_high", gain=0.8,
                   note="思考气泡：我不够好"),
        ], draw=ground, note="主角照镜子，镜中的倒影越来越小、越来越灰；头顶冒出“我不够好”"),

        # 3：一排人，头顶依次冒出小灰云
        Shot(2, "阿德勒说：|人人都有。", "阿德勒原著", [
            *[Fig(x, GROUND, s, at=0, color=col, hair=hair, face=f, mood=m,
                  moves=[(5, dict(pose="shrug", mood="flat" if m != "smile" else "smile", look=0.6))])
              for x, s, col, hair, f, m in [
                  (120, 250, K.OTHER, "bun", 1, "calm"), (255, 290, K.OTHER3, "short", 1, "calm"),
                  (392, 205, K.OTHER2, None, 1, "smile"), (540, 300, K.HERO, "short", 1, "calm"),
                  (690, 270, "#9C8FB0", "long", -1, "calm"), (830, 235, K.OTHER, "cap", -1, "smile"),
                  (960, 285, K.OTHER3, None, -1, "calm")]],
            *[Custom(cloud_el, x=x, y=GROUND - s * 1.08 - 72, at=b, enter="pop", cs=104,
                     sfx=sfx, gain=gn, note=f"第 {i + 1} 个人头顶冒出小灰云" if sfx else "")
              for i, (x, s, b, sfx, gn) in enumerate([
                  (120, 250, 1, "wood_high", 0.7), (255, 290, 1.5, None, 1), (392, 205, 2, "wood_low", 0.75),
                  (540, 300, 2.5, None, 1), (690, 270, 3, "wood_high", 0.7), (830, 235, 3.5, None, 1),
                  (960, 285, 4, "bongo_low", 0.8)])],
        ], draw=ground, text_beat=0, note="一排七个不同的人，头顶按拍依次冒出小灰云；随后大家一起耸耸肩"),

        # 4：drop——“自卑感”
        Shot(3, "“身为人，|就意味着感到自卑。”", "阿德勒原著", [
            Big("自卑感", 540, 520, 160, at=0, sfx="kick", sub="inferiority feeling", note="概念落版（音乐 drop）"),
            Fig(250, GROUND, 290, at=2, color=K.OTHER3, hair="bun", mood="calm"),
            Fig(540, GROUND, 320, at=2, hair="short", mood="calm"),
            Fig(830, GROUND, 290, at=2, color=K.OTHER2, face=-1, mood="calm"),
            Custom(cloud_el, x=540, y=GROUND - 320 * 1.08 - 70, at=4, enter="pop", cs=120, sfx="wood_low",
                   note="主角头顶的小灰云"),
            Custom(cloud_el, x=250, y=GROUND - 290 * 1.08 - 70, at=6, enter="pop", cs=110, sfx="wood_high", gain=0.8,
                   note="两边的人头顶也有小灰云"),
            Custom(cloud_el, x=830, y=GROUND - 290 * 1.08 - 70, at=6, enter="pop", cs=110),
            Icon("book", 330, 1232, 56, color=K.HERO, at=8, enter="pop", sfx="shaker", note="出处浮现"),
            Txt("阿德勒《生命的意义》1933", 560, 1234, 28, at=8, font="sans_medium", color=K.INK2),
        ], draw=ground, note="drop 处“自卑感”砸下；三个人站起，头顶各有一朵小灰云；底部标出处"),

        # 5：小孩够不着门把手，大人的腿走过
        Shot(3, "每个人都曾是|大人世界里最小的那个。", "阿德勒原著 · 大意", [
            Custom(door, x=DOOR_X, y=GROUND, at=0, enter="fade", open=0.0),
            Custom(giant, at=0, enter="none", gx=330),
            Fig(630, GROUND, 190, at=0, hair="short", mood="calm", look=0.8,
                moves=[(4, dict(pose="reach", y=GROUND - 90, mood="open", dur=0.22, ease="out", sfx="bongo_high",
                                note="小孩跳起去够门把手")),
                       (4.6, dict(y=GROUND, dur=0.25)),
                       (6, dict(pose="sad", mood="sad", look=0.4, sfx="wood_low", note="没够着，垂下手"))]),
        ], draw=ground, hits=[(2, "tom", 0.8, "大人的腿落下最后一步")],
            note="门把手高高在上；巨大的大人腿从身旁走过，小孩跳起来也够不着"),

        # 6：推箱子、爬上去、够到门把手
        Shot(3, "够不着，|所以想长高、想学会。", "阿德勒原著 · 大意", [
            Custom(door, x=DOOR_X, y=GROUND, at=0, enter="fade", open=0.0,
                   moves=[(8, dict(open=1.0, dur=0.5, sfx="clap", note="够到把手，门打开，光照进来"))]),
            Custom(box, x=300, y=GROUND, at=0, enter="fade", moves=[(0.15, dict(x=640, dur=0.95))]),
            Fig(185, GROUND, 190, at=0, enter="fade", pose="push", hair="short", mood="calm",
                moves=[(0.15, dict(x=525, dur=0.95)),
                       (4, dict(x=640, y=GROUND - 130, pose="climb", mood="open", dur=0.35, sfx="bongo_low",
                                note="小孩爬上箱子")),
                       (5, dict(pose="stand", look=0.8)),
                       (6, dict(pose="reach", look=1.0)),
                       (8, dict(pose="cheer", mood="happy", look=0.3))]),
        ], draw=ground, hits=[(2, "wood_low", 0.85, "箱子推到门下")],
            note="小孩推来箱子、爬上去，终于够到门把手，门打开"),

        # 7：阿德勒：病床上的孩子 → 医生
        Shot(3, "阿德勒小时候体弱多病，|后来立志学医。", "阿德勒的经历", [
            Custom(lambda c, g, t, d: K.memory(c, 0, 0, 460, 360, sickbed, 1, -3, 1, "童年"),
                   x=330, y=590, at=0, enter="pop", sfx="wood_low", gain=0.8, note="回忆照片：病床上的瘦小孩子"),
            Txt("佝偻病、险死于肺炎（据传记）", 540, 1234, 28, at=2, font="sans_medium", color=K.INK2),
            Arrow((420, 800), (650, 1000), at=4, color=ACC, width=12, bend=0.25, sfx="shaker",
                  note="时间箭头：长大"),
            FigPlus(800, GROUND, 340, at=6, color=K.OTHER2, hair="short", mood="calm", attach=med_bag,
                    sfx="wood_high", gain=0.8, note="长大的医生拎着医药箱出现",
                    moves=[(8, dict(pose="proud", mood="happy", sfx="bongo_high", gain=0.8, note="医生挺胸微笑"))]),
        ], draw=ground, note="回忆照片里病床上的孩子 → 时间箭头 → 拎着医药箱的医生"),

        # 8：小灰云旁弹出“正常”
        Shot(2, "自卑感本身，|不是病。", "阿德勒原著 · 大意", [
            FigPlus(330, GROUND, 330, at=0, pose="wave", hair="short", mood="worried", attach=balloon,
                    moves=[(5, dict(mood="smile"))]),
            Icon("check", 770, 720, 170, color=K.GREEN, at=2, enter="pop", sfx="rim", gain=0.85,
                 p=lambda g, t: clamp01(t / 0.4), note="对勾弹出"),
            Label("正常", 770, 880, 44, at=4, fill=K.GREEN, sfx="wood_high", gain=0.8, note="“正常”标签"),
        ], draw=ground, text_beat=0, note="主角像牵气球一样牵着小灰云；旁边弹出“正常”对勾，主角松了口气"),

        # 9：灰云吹风，把主角往前推
        Shot(2, "它可以是|向前的推力。", "阿德勒原著 · 大意", [
            Custom(wind_cloud, x=210, y=620, at=0, enter="pop", puff=0.0,
                   moves=[(2, dict(puff=1.0, dur=0.25, sfx="shaker", note="灰云鼓起腮帮吹风"))]),
            Fig(330, GROUND, 320, at=0, enter="none", hair="short", mood="calm",
                moves=[(2, dict(x=700, mood="open", dur=1.15)),
                       (6, dict(pose="cheer", mood="happy", sfx="bongo_high", gain=0.85, note="主角被推到前面，举手"))]),
            Arrow((420, 1205), (900, 1205), at=4, color=ACC, width=14, sfx="wood_low", gain=0.8, note="向前的箭头"),
        ], draw=ground, text_beat=0, note="小灰云鼓起腮帮吹出一阵风，把主角往前推"),

        # 10：牵着灰云，面前两块路牌
        Shot(3, "关键在于：|你拿它来做什么。", "情境演绎", [
            Icon("house", 175, 1035, 190, color=K.INK3, accent=K.INK2, p=0, at=3, enter="pop"),
            Custom(signpost, x=290, y=GROUND, at=2, enter="pop", text="躲起来", dir=-1, fill=K.INK3,
                   sfx="wood_low", note="左边路牌：躲起来"),
            Custom(lambda c, g, t, d: K.stairs(c, 0, 0, 4, 50, 46, ACC, 1, 0.8, clamp01(t / 0.6)),
                   x=800, y=GROUND, at=5, enter="none"),
            Custom(signpost, x=780, y=GROUND, at=4, enter="pop", text="去练习", dir=1, fill=ACC,
                   sfx="wood_high", note="右边路牌：去练习"),
            FigPlus(540, GROUND, 320, at=0, pose="wave", hair="short", mood="calm", attach=balloon,
                    moves=[(6, dict(face=-1, mood="worried")),
                           (8, dict(face=1, pose="point", mood="open", sfx="rim", gain=0.8, note="主角转向“去练习”"))]),
        ], draw=ground, note="主角牵着小灰云站在岔路口：左边“躲起来”（房子），右边“去练习”（台阶）"),

        # 11：海边的德摩斯梯尼，声音又小又弱
        Shot(3, "相传德摩斯梯尼|说话声弱、口齿不清，", "传说 · 普鲁塔克记载", [
            FigPlus(330, 1062, 300, at=1, color=ROBE, hair="short", hair_color="#5B4636", mood="worried",
                    under=robe_under, attach=robe_over, voice=0.0,
                    moves=[(4, dict(pose="point", mood="open")), (8, dict(pose="sad", mood="sad"))]),
            Bubble("……", 590, 700, 30, at=4, tail=(-0.7, 1), alpha=0.55, sfx="wood_high", gain=0.6,
                   note="又小又淡的说话气泡",
                   moves=[(8, dict(alpha=0.35, size=26))]),
            Custom(splash, x=500, y=1080, at=0, enter="none", at_beats=[(2, 0.4), (8, 1.0)]),
        ], draw=seaside, hits=[(2, "shaker", 0.8, "海浪拍岸"), (8, "frame", 0.8, "大浪盖过他的声音")],
            note="海边的古希腊人，开口只有一个又小又淡的“……”，被海浪声盖过"),

        # 12：含石子对海浪苦练 → 众人鼓掌
        Shot(4, "他含石子、对海浪苦练，|终成著名演说家。", "传说 · 普鲁塔克记载", [
            FigPlus(330, 1062, 300, at=0, enter="none", color=ROBE, hair="short", hair_color="#5B4636",
                    mood="calm", under=robe_under, attach=robe_over, voice=0.0,
                    moves=[(1, dict(mood="open")),
                           (4, dict(pose="point", voice=0.25)),
                           (8, dict(voice=0.6, mood="open", sfx="bongo_low", gain=0.85, note="声音变大")),
                           (10, dict(pose="wave", voice=1.0, mood="smile")),
                           (12, dict(pose="cheer", mood="happy"))]),
            *[Custom(pebble, x=362, y=774, at=b, out=b + 0.12, enter="drop", dur=0.4,
                     sfx="wood_high" if b == 1 else None, gain=0.7, note="小石子落进嘴里" if b == 1 else "")
              for b in (1, 2, 3)],
            Custom(splash, x=500, y=1080, at=0, enter="none", at_beats=[(4, 1.0), (6, 0.5)]),
            Custom(crowd_cheer, x=0, y=0, at=10, enter="rise", cheer=12),
        ], draw=seaside, hits=[(4, "frame", 0.75, "海浪拍岸，他迎着浪喊"), (12, "clap", 1.0, "众人鼓掌")],
            note="小石子一颗颗落进嘴里；他迎着海浪练习，声音一圈比一圈大，最后岸上的人群鼓掌"),

        # 13：小练习——笔记卡两栏
        Shot(4, "写下一件让你自卑的事，|再写：它让我想怎样变好？", "小练习", [
            Custom(notebook, x=540, y=720, at=0, enter="pop"),
        ], hits=[(2, "wood_low", 0.8, "写下第一件事"), (6, "rim", 0.8, "第一行打勾"),
                 (8, "wood_high", 0.7, "写下第二件事"), (12, "bongo_high", 0.85, "第二行打勾")],
            note="笔记卡两栏：“让我自卑的事 → 我想变好的地方”，按拍写下、画箭头、打勾"),

        # 14：起跑线
        Shot(2, "自卑感不是终点，|是起点。", "阿德勒的视角", [
            Label("起点", 390, 1228, 32, at=1, fill=ACC),
            Icon("flag", 130, 900, 190, accent=ACC, at=0, enter="pop", rot=-20,
                 p=lambda g, t: t * 0.8,
                 moves=[(2, dict(rot=25, dur=0.2, ease="out", sfx="wood_high", note="发令旗挥下"))]),
            Fig(310, GROUND, 320, at=0, enter="rise", pose="crouch", hair="short", mood="calm",
                moves=[(3, dict(pose="stand", mood="smile", dur=0.4)),
                       (4, dict(x=860, dur=1.1, stride=1.5, sfx="tom", gain=0.85, note="主角起跑")),
                       (6.2, dict(pose="cheer", mood="happy"))]),
        ], draw=track, note="主角蹲在起跑线后，发令旗挥下，他冲了出去"),

        end_shot(["Adler, A. (1933). Der Sinn des Lebens.（《生命的意义》）",
                  "Adler, A. (1927). Menschenkenntnis.（中译《理解人性》）",
                  "Plutarch.《德摩斯梯尼传》第11章"], "03 自卑情结：“要不是因为……，我早就……”"),
    ]
    return Episode(2, "inferiority", "自卑感", "觉得自己不如别人，是坏事吗？", ACC, shots,
                   refs=["Adler, A. (1933). Der Sinn des Lebens.（《生命的意义》）",
                         "Adler, A. (1927). Menschenkenntnis.（中译《理解人性》）",
                         "Plutarch.《德摩斯梯尼传》第11章"],
                   publish_title="觉得自己不如别人，是坏事吗？｜阿德勒心理学02 自卑感",
                   hashtags="#阿德勒 #心理学 #自卑 #自我成长 #被讨厌的勇气",
                   cover_title="觉得自己【不如别人】，|是坏事吗？", cover_sub="阿德勒谈自卑感", cover_shot=0, cover_t=5.6,
                   notes=[
                       "“身为人，就意味着感到自卑”出自 Der Sinn des Lebens（1933）：“Mensch sein heißt: sich minderwertig "
                       "fühlen.” 不是《自卑与超越》。",
                       "“自卑感本身不是病，是进步的动力”为阿德勒原意大意（Ansbacher 1956 引：“Inferiority feelings are not in "
                       "themselves abnormal. They are the cause of all improvements in the position of mankind.”）。",
                       "阿德勒童年佝偻病、约五岁险死于肺炎、此后立志学医，据 Bottome (1939) 与 Hoffman (1994) 传记，细节各来源不一，"
                       "片中只写概括。",
                       "德摩斯梯尼的故事据普鲁塔克《德摩斯梯尼传》第 11 章（转述法勒鲁姆的德米特里乌斯），原文为声弱、发音不清、气短，"
                       "片中按“相传”处理，不写“口吃”。",
                   ]).build()
