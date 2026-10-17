"""《聊完天，为什么总觉得对方不太喜欢自己》15 个镜头的场景绘制（舞台 1000×1000 单位，撞击时刻一律读 cue）。"""

import math

import skia

from kepu import draw as d
from kepu.config import GOLD
from kepu.props import cell, jar, pendant_talk, review_merge, speech_bubble, thought_bubble, window

FLOOR = 760
ME = (300, 640)
YOU = (700, 640)


def _seat(c, x, f):
    c.drawRect(skia.Rect.MakeLTRB(x - 55, 650, x + 55, 662), d.fill("#1D1C19"))
    c.drawRect(skia.Rect.MakeLTRB(x - 55 * f - 6, 520, x - 55 * f + 6, FLOOR), d.fill("#1D1C19"))


def cafe(c, t, view, guess=None, guess_dash=True, bubble=0.0, me_pose=d.SIT_EASE, you_pose=d.SIT_EASE, you_a=1.0,
         warm=0.4):
    """咖啡桌构图：左侧主角、右侧对方；bubble>0 时主角头顶出现思维气泡，内装“自己猜的”光罐（guess 为液面）。"""
    d.room(c, view, floor_y=FLOOR, warm=(500, 380, warm))
    c.drawRect(skia.Rect.MakeLTRB(420, 610, 580, 624), d.fill("#2A2824"))
    c.drawLine(420, 610, 580, 610, d.stroke(GOLD, 1.5, 0.5))
    c.drawRect(skia.Rect.MakeLTRB(494, 624, 506, FLOOR), d.fill("#1D1C19"))
    for x in (470, 530):
        c.drawRRect(d.rrect(x, 596, 22, 26, 4), d.fill("#E8DCC6"))
    _seat(c, ME[0], 1)
    _seat(c, YOU[0], -1)
    j = d.figure(c, *ME, me_pose, facing=1)
    c.saveLayerAlpha(None, int(255 * d.clamp01(you_a)))
    d.figure(c, *YOU, you_pose, facing=-1)
    c.restore()
    if bubble > 0 and guess is not None:
        hx, hy = j["head"]
        thought_bubble(c, hx + 10, hy - 190, 190, 230, a=bubble, tail=(-0.1, 1))
        jar(c, hx + 10, hy - 190, guess, s=0.85, dashed=guess_dash, a=bubble)
    return j


# ---------------------------------------------------------------- 镜头 01–05

def shot01(c, t, D, cue, view):
    d.room(c, view, floor_y=FLOOR, warm=(700, 380, 0.25))
    window(c, 620, 260, 900, 560, 0.3)
    x = d.lerp(280, 460, d.prog(t, 0, D))
    j = d.figure(c, x, FLOOR - (d.SEG["th"] + d.SEG["sh"]), d.walk(t * 2 * math.pi / 0.9, d.SLUMP), facing=1)
    on = t >= cue["doubt"] - 1e-6
    if on:
        hx, hy = j["head"]
        pop = d.ease_out(d.prog(t, cue["doubt"], 0.3))
        thought_bubble(c, hx + 40, hy - 170, 190 * (0.8 + 0.2 * pop), 230 * (0.8 + 0.2 * pop), tail=(-0.2, 1))
        jar(c, hx + 40, hy - 170, 0.25, s=0.85, dashed=True)
        d.glow(c, hx + 40, hy - 170, 180, GOLD, 0.55 * d.pulse(t, cue["doubt"], 0.5))


REPLAY = [(-1, 0), (1, 0), (-1, 1), (1, 1), (-1, 2)]


def _replay(c, t, mark_i=-1, mark_k=0.0, warm_you=0.0, you_a=1.0, x0=200, y0=200):
    """对话回放：一列左右交替的气泡（左 = 自己，右 = 对方）。"""
    for i, (side, row) in enumerate(REPLAY):
        x = 380 if side < 0 else 620
        y = y0 + i * 110
        a = you_a if side > 0 else 1.0
        speech_bubble(c, x, y, 220, 76, side=-side, mark=mark_k if i == mark_i else 0.0, a=a,
                      warm=warm_you if side > 0 else 0.0)


def shot02(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["mark"] - 1e-6
    _replay(c, t, mark_i=2, mark_k=1.0 if on else 0.0, y0=240)
    d.glow(c, 380, 240 + 2 * 110, 150, GOLD, 0.55 * d.pulse(t, cue["mark"], 0.5))


def shot03(c, t, D, cue, view):
    after = t >= cue["drain"] - 1e-6
    lvl = 0.06 if after else d.lerp(0.4, 0.25, d.prog(t, 0, cue["drain"]))
    cafe(c, t, view, guess=lvl, bubble=1.0, me_pose=d.SIT, you_a=0.35)
    hx, hy = d.figure_joints(*ME, d.SIT, 1)["head"]
    d.glow(c, hx + 10, hy - 120, 150, "#E8C987", 0.55 * d.pulse(t, cue["drain"], 0.5))


def shot04(c, t, D, cue, view):
    d.backdrop(c, view)
    flash = d.pulse(t, cue["flash"], 0.8)
    # 自己的气泡被聚光照着；对方的暖色回应在暗处，撞击时一闪
    g = skia.GradientShader.MakeRadial(skia.Point(380, 440), 260, [d.col("#FFF1D2", 0.18), d.col("#FFF1D2", 0)])
    c.drawCircle(380, 440, 260, skia.Paint(Shader=g))
    _replay(c, t, warm_you=1.0, you_a=0.18 + 0.82 * flash, y0=220)
    for i, (side, _) in enumerate(REPLAY):
        if side > 0:
            d.glow(c, 620, 220 + i * 110, 120, GOLD, 0.5 * flash)


def shot05(c, t, D, cue, view):
    k = d.ease_io(d.prog(t, cue["halt"], 1.0))
    cafe(c, t, view, guess=0.06, bubble=1.0, me_pose=d.SIT, you_a=0.5)
    yx, yy = d.figure_joints(*YOU, d.SIT_EASE, -1)["head"]
    if k > 0:
        thought_bubble(c, yx - 10, yy - 190, 190, 230, a=k, tail=(0.1, 1))
        c.drawRRect(d.rrect(yx - 10, yy - 190, 102, 145, 20), d.fill("#2A2C33", k))
        c.drawRRect(d.rrect(yx - 10, yy - 190, 102, 145, 20), d.stroke(GOLD, 2, 0.6 * k))


# ---------------------------------------------------------------- 镜头 06–10

def shot06(c, t, D, cue, view):
    review_merge(c, t, cue["merge"], view)


def _pair(c, x, y, guess, actual, s=1.0, gap_k=0.0):
    jar(c, x - 80 * s, y, guess, s=s, dashed=True)
    jar(c, x + 80 * s, y, actual, s=s)
    if gap_k > 0:
        h = 170 * s
        yg = y + h / 2 - h * guess
        ya = y + h / 2 - h * actual
        bx = x + 160 * s
        c.drawLine(bx, ya, bx + 20 * s, ya, d.stroke(GOLD, 3, gap_k))
        c.drawLine(bx + 20 * s, ya, bx + 20 * s, yg, d.stroke(GOLD, 3, gap_k))
        c.drawLine(bx, yg, bx + 20 * s, yg, d.stroke(GOLD, 3, gap_k))
        c.drawLine(x - 80 * s, yg, bx, yg, d.stroke(GOLD, 1.5, 0.6 * gap_k, dash=((8, 6), 0)))


def shot07(c, t, D, cue, view):
    d.backdrop(c, view)
    g = d.ease_in(d.prog(t, cue["guess"] - 0.5, 0.5))
    a = d.ease_in(d.prog(t, cue["actual"] - 0.5, 0.5))
    _pair(c, 500, 520, 0.38 * g, 0.78 * a, s=1.6)
    d.glow(c, 372, 560, 150, GOLD, 0.5 * d.pulse(t, cue["guess"], 0.5))
    d.glow(c, 628, 500, 150, GOLD, 0.5 * d.pulse(t, cue["actual"], 0.5))


def shot08(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["gap"] - 1e-6
    _pair(c, 480, 520, 0.38, 0.78, s=1.6, gap_k=1.0 if on else 0.0)
    d.glow(c, 760, 500, 170, GOLD, 0.55 * d.pulse(t, cue["gap"], 0.5))


def _beaker(c, x, y, a=1.0):
    p = skia.Path()
    p.moveTo(x - 16, y - 40)
    p.lineTo(x + 16, y - 40)
    p.lineTo(x + 16, y - 10)
    p.lineTo(x + 40, y + 34)
    p.lineTo(x - 40, y + 34)
    p.lineTo(x - 16, y - 10)
    p.close()
    c.drawPath(p, d.stroke(GOLD, 3, a))
    c.drawRect(skia.Rect.MakeLTRB(x - 30, y + 14, x + 30, y + 32), d.fill(GOLD, 0.5 * a))


def _bunk(c, x, y, a=1.0):
    for k in (0, 1):
        c.drawRRect(d.rrect(x, y - 30 + k * 46, 90, 18, 6), d.fill("#3A3833", a))
        c.drawRRect(d.rrect(x - 30, y - 42 + k * 46, 24, 12, 5), d.fill(d.WHITE, a))
    c.drawLine(x - 45, y - 50, x - 45, y + 40, d.stroke(GOLD, 3, a))
    c.drawLine(x + 45, y - 50, x + 45, y + 40, d.stroke(GOLD, 3, a))


def _circle_chairs(c, x, y, a=1.0):
    for i in range(5):
        ang = -math.pi / 2 + i * 2 * math.pi / 5
        c.drawCircle(x + 36 * math.cos(ang), y + 26 * math.sin(ang), 10, d.fill(GOLD, a))
    c.drawCircle(x, y, 10, d.stroke(GOLD, 2, a))


def shot09(c, t, D, cue, view):
    d.backdrop(c, view)
    starts = (cue["first"], (cue["first"] + cue["third"]) / 2, cue["third"])
    for (x, icon), t0 in zip(((200, _beaker), (500, _bunk), (800, _circle_chairs)), starts):
        k = d.ease_in(d.prog(t, t0 - 0.4, 0.4))
        if k <= 0:
            continue
        icon(c, x, 320 - 30 * (1 - k), a=k)
        _pair(c, x, 560, 0.3 * k, 0.72 * k, s=0.75)
    d.glow(c, 800, 460, 180, GOLD, 0.55 * d.pulse(t, cue["third"], 0.5))


def _calendar(c, x, y, page, a=1.0):
    for i in range(3, -1, -1):
        off = i * 8
        c.drawRRect(d.rrect(x + off, y + off, 200, 220, 12), d.fill(d.mix(d.WHITE, "#000000", 0.08 * i), a))
    c.drawRRect(d.rrect(x, y - 82, 200, 40, 10), d.fill(GOLD, a))
    for r in range(3):
        for k in range(4):
            c.drawRect(skia.Rect.MakeXYWH(x - 80 + k * 42, y - 40 + r * 46, 28, 28),
                       d.fill("#C9C0AE" if (r * 4 + k) != page % 12 else GOLD, a))


def shot10(c, t, D, cue, view):
    d.backdrop(c, view)
    flips = int(max(0.0, t - 0.2) / 0.35) if t < cue["months"] else 12
    _calendar(c, 290, 470, flips)
    _pair(c, 700, 500, 0.32, 0.74, s=1.1, gap_k=1.0 if t >= cue["months"] - 1e-6 else 0.4)
    d.glow(c, 290, 470, 180, GOLD, 0.55 * d.pulse(t, cue["months"], 0.5))


# ---------------------------------------------------------------- 镜头 11–15

def _tick(c, x, y, k):
    if k > 0:
        c.drawLine(x - 12, y, x - 3, y + 11, d.stroke(GOLD, 5, k))
        c.drawLine(x - 3, y + 11, x + 16, y - 12, d.stroke(GOLD, 5, k))


def shot11(c, t, D, cue, view):
    d.backdrop(c, view)
    _replay(c, t, warm_you=1.0, you_a=1.0, y0=220)
    ys = [220 + i * 110 for i, (side, _) in enumerate(REPLAY) if side > 0]
    for n, y in enumerate(ys):
        at = cue["check"] - (len(ys) - 1 - n) * 0.5
        _tick(c, 770, y, 1.0 if t >= at - 1e-6 else 0.0)
        d.glow(c, 770, y, 70, GOLD, 0.5 * d.pulse(t, at, 0.5))


def shot12(c, t, D, cue, view):
    d.backdrop(c, view)
    cell(c, 300, 540, "fact", w=300, h=380)
    cell(c, 700, 540, "act", w=300, h=380)
    hover = d.ease_out(d.prog(t, 0.3, 0.8))
    drop = d.ease_in(d.prog(t, cue["sort"] - 3 / 30, 3 / 30))
    for i in range(3):
        ty = 480 + i * 50
        x, y = d.lerp(500, 700, hover), d.lerp(ty - 170, ty, drop)
        speech_bubble(c, x, y, 150, 56, side=1, warm=1.0, a=hover)
    d.glow(c, 700, 540, 190, GOLD, 0.55 * d.pulse(t, cue["sort"], 0.5))


def shot13(c, t, D, cue, view):
    pendant_talk(c, t, cue["lamp"], view, floor=FLOOR)


def shot14(c, t, D, cue, view):
    d.room(c, view, floor_y=FLOOR, warm=(500, 380, 0.6))
    window(c, 600, 250, 900, 560, 0.7)
    after = t >= cue["fill"] - 1e-6
    lvl = 0.72 if after else d.lerp(0.1, 0.2, d.prog(t, 0, cue["fill"]))
    pose = d.blend(d.SLUMP, d.STAND, d.ease_out(d.prog(t, cue["fill"], 1.0)))
    j = d.figure(c, 380, FLOOR - (d.SEG["th"] + d.SEG["sh"]), pose, facing=1)
    hx, hy = j["head"]
    thought_bubble(c, hx + 40, hy - 170, 190, 230, tail=(-0.2, 1))
    jar(c, hx + 40, hy - 170, lvl, s=0.85, dashed=not after)
    d.glow(c, hx + 40, hy - 170, 190, GOLD, 0.55 * d.pulse(t, cue["fill"], 0.5))


def shot15(c, t, D, cue, view):
    shot14(c, 6.0, D, {"fill": 1.0}, view)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
