"""《忙了一整周，为什么只记得最崩的那晚》15 个镜头的场景绘制（舞台 1000×1000 单位，撞击时刻一律读 cue）。"""

import skia

from kepu import draw as d
from kepu.config import GOLD
from kepu.props import bar, mood_curve, pendant_talk, pin, review_merge

X0, X1, CY = 175, 825, 420
PTS = [(0.0, 0.1), (0.14, 0.32), (0.28, 0.05), (0.42, 0.3), (0.58, -0.95), (0.7, 0.15), (0.84, 0.25), (1.0, -0.45)]
WORST = 0.58
CARD = (500, 760)


def _at(samples, u):
    i = min(len(samples) - 1, int(round(u * (len(samples) - 1))))
    return samples[i]


def memory_card(c, shade=0.0, pins_only=False, full=False, a=1.0, samples=None, flash=0.0):
    """记忆卡：像一张照片，里面是对这一周的“印象”。pins_only 时只画最难处与结尾两点，full 时画全程缩略。"""
    x, y = CARD
    w, h = 380, 200
    d.soft_shadow(c, x, y, w, h, lift=1.0, a=0.6 * a)
    c.drawRRect(d.rrect(x, y, w, h, 12), d.fill(d.mix(d.WHITE, "#2A2724", shade), a))
    c.drawRRect(d.rrect(x, y, w - 20, h - 20, 8), d.stroke(GOLD, 2, 0.7 * a))
    if samples:
        sx0, sx1 = x - w * 0.4, x + w * 0.4
        mx = lambda px: sx0 + (px - X0) / (X1 - X0) * (sx1 - sx0)
        my = lambda py: y + (py - CY) * 0.35
        if full:
            p = skia.Path()
            for i, (px, py) in enumerate(samples):
                (p.moveTo if i == 0 else p.lineTo)(mx(px), my(py))
            c.drawPath(p, d.stroke(GOLD, 3, a))
        else:
            wx, wy = _at(samples, WORST)
            ex, ey = samples[-1]
            c.drawCircle(mx(wx), my(wy), 10, d.fill("#8A6E3A" if shade else GOLD, a))
            if pins_only:
                c.drawCircle(mx(ex), my(ey), 10, d.fill(GOLD, a))
                c.drawLine(mx(wx), my(wy), mx(ex), my(ey), d.stroke(GOLD, 2, 0.6 * a, dash=((8, 6), 0)))
    if flash > 0:
        c.drawRRect(d.rrect(x, y, w, h, 12), d.fill("#FFFFFF", 0.6 * flash))


def week(c, t, view, upto=1.0, lit=1.0, snap_k=0.0, shade=0.0, pins_only=False, full=False, warm_end=0.0,
         calm=0.0, dim_mid=0.0):
    """一周的体验曲线（不标刻度）+ 下方记忆卡。返回采样点。"""
    d.backdrop(c, view)
    samples = mood_curve(c, X0, X1, CY, PTS, upto=upto, lit=lit, warm_end=warm_end)
    if calm > 0:
        for u0, u1 in ((0.05, 0.22), (0.3, 0.45), (0.68, 0.88)):
            seg = [p for p in samples if X0 + (X1 - X0) * u0 <= p[0] <= X0 + (X1 - X0) * u1]
            if len(seg) > 1:
                path = skia.Path()
                path.moveTo(*seg[0])
                for p in seg[1:]:
                    path.lineTo(*p)
                c.drawPath(path, d.stroke("#FFF1D2", 8, 0.6 * calm))
    if dim_mid > 0:
        c.drawRect(skia.Rect.MakeLTRB(X0 - 10, CY - 200, X0 + (X1 - X0) * (WORST - 0.06), CY + 200),
                   d.fill(d.BG, 0.75 * dim_mid))
        c.drawRect(skia.Rect.MakeLTRB(X0 + (X1 - X0) * (WORST + 0.06), CY - 200, X0 + (X1 - X0) * 0.94, CY + 200),
                   d.fill(d.BG, 0.75 * dim_mid))
    memory_card(c, shade=shade, pins_only=pins_only, full=full, samples=samples, flash=0.0)
    if snap_k > 0:
        wx, wy = _at(samples, WORST)
        c.drawLine(CARD[0], CARD[1] - 100, wx, wy, d.stroke(GOLD, 2, 0.6 * snap_k, dash=((8, 6), 0)))
    return samples


# ---------------------------------------------------------------- 镜头 01–05

def shot01(c, t, D, cue, view):
    on = t >= cue["snap"] - 1e-6
    s = week(c, t, view, snap_k=1.0 if on else 0.0)
    wx, wy = _at(s, WORST)
    d.glow(c, wx, wy, 160, "#FFF1D2", 0.7 * d.pulse(t, cue["snap"], 0.5))
    memory_card(c, samples=s, flash=d.pulse(t, cue["snap"], 0.35))


def shot02(c, t, D, cue, view):
    on = t >= cue["calm"] - 1e-6
    week(c, t, view, calm=1.0 if on else 0.0)
    d.glow(c, 500, CY, 380, "#FFF1D2", 0.35 * d.pulse(t, cue["calm"], 0.5))


def shot03(c, t, D, cue, view):
    on = t >= cue["stamp"] - 1e-6
    week(c, t, view, shade=1.0 if on else 0.0, lit=0.6)
    d.glow(c, *CARD, 240, "#E8C987", 0.5 * d.pulse(t, cue["stamp"], 0.5))


def shot04(c, t, D, cue, view):
    on = t >= cue["pins"] - 1e-6
    k = d.ease_in(d.prog(t, cue["pins"] - 0.4, 0.4))
    s = week(c, t, view, dim_mid=1.0 if on else 0.0, pins_only=on, shade=0.6)
    wx, wy = _at(s, WORST)
    ex, ey = s[-1]
    off = (1 - k) * -300
    pin(c, wx, wy + off, k)
    pin(c, ex, ey + off, k)
    d.glow(c, wx, wy, 140, GOLD, 0.6 * d.pulse(t, cue["pins"], 0.5))
    d.glow(c, ex, ey, 140, GOLD, 0.6 * d.pulse(t, cue["pins"], 0.5))


def shot05(c, t, D, cue, view):
    k = d.ease_io(d.prog(t, cue["halt"], 0.8))
    s = week(c, t, view, pins_only=True, shade=0.6, dim_mid=0.5)
    ex, ey = s[-1]
    c.drawOval(d.rect(ex - 40, ey, 200, 160), d.stroke(GOLD, 3, k, dash=((10, 8), 0)))


# ---------------------------------------------------------------- 镜头 06–10

def shot06(c, t, D, cue, view):
    review_merge(c, t, cue["merge"], view)


COLD = "#7FA6C9"
MILD = "#C9D6E2"


def _drop(c, x, y, color, a=1.0):
    p = skia.Path()
    p.moveTo(x, y - 26)
    p.cubicTo(x + 18, y - 4, x + 18, y + 18, x, y + 18)
    p.cubicTo(x - 18, y + 18, x - 18, y - 4, x, y - 26)
    c.drawPath(p, d.fill(color, a))


def _trials(c, t, short_on, long_on, check=0.0):
    x0, x1 = 220, 620
    _drop(c, 150, 380, COLD, 1.0 if short_on else 0.3)
    _drop(c, 150, 580, COLD, 1.0 if long_on else 0.3)
    if short_on:
        bar(c, x0, x1, 380, h=56, color=COLD, a=0.95)
    if long_on:
        bar(c, x0, x1, 580, h=56, color=COLD, a=0.95)
        bar(c, x1 - 20, x1 + 200, 580, h=56, color=MILD, a=0.95)
    if check > 0:
        c.drawLine(880, 580, 900, 604, d.stroke(GOLD, 8, check))
        c.drawLine(900, 604, 944, 548, d.stroke(GOLD, 8, check))


def shot07(c, t, D, cue, view):
    d.backdrop(c, view)
    _trials(c, t, t >= cue["short"] - 1e-6, t >= cue["long"] - 1e-6)
    d.glow(c, 420, 380, 220, COLD, 0.5 * d.pulse(t, cue["short"], 0.5))
    d.glow(c, 720, 580, 220, MILD, 0.5 * d.pulse(t, cue["long"], 0.5))


def shot08(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["pick"] - 1e-6
    _trials(c, t, True, True, check=1.0 if on else 0.0)
    if on:
        c.drawRRect(d.rrect(560, 580, 760, 110, 18), d.stroke(GOLD, 3))
    d.glow(c, 910, 580, 160, GOLD, 0.6 * d.pulse(t, cue["pick"], 0.5))


def shot09(c, t, D, cue, view):
    k = d.ease_in(d.prog(t, cue["fade"], cue["card"] - cue["fade"]))
    on = t >= cue["card"] - 1e-6
    s = week(c, t, view, dim_mid=k, pins_only=on, shade=0.0)
    pin(c, *_at(s, WORST), 1.0)
    pin(c, *s[-1], 1.0)
    d.glow(c, *CARD, 240, GOLD, 0.55 * d.pulse(t, cue["card"], 0.5))


def shot10(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["squeeze"] - 1e-6
    sq = 0.45 if on else 1.0
    c.save()
    c.translate(X1, 0)
    c.scale(sq, 1.0)
    c.translate(-X1, 0)
    s = mood_curve(c, X0, X1, CY, PTS)
    c.restore()
    wx, wy = _at(s, WORST)
    ex, ey = s[-1]
    wx = X1 + (wx - X1) * sq
    pin(c, wx, wy, 1.0)
    pin(c, ex, ey, 1.0)
    memory_card(c, pins_only=True, samples=s)
    d.glow(c, (X0 + X1) / 2 + (X1 - X0) * (1 - sq) / 2, CY, 260, GOLD, 0.5 * d.pulse(t, cue["squeeze"], 0.5))


# ---------------------------------------------------------------- 镜头 11–15

def _tick(c, x, y, k):
    if k > 0:
        c.drawLine(x - 14, y, x - 4, y + 12, d.stroke(GOLD, 6, k))
        c.drawLine(x - 4, y + 12, x + 18, y - 14, d.stroke(GOLD, 6, k))


def shot11(c, t, D, cue, view):
    s = week(c, t, view, calm=1.0, pins_only=True)
    for n, u in enumerate((0.14, 0.42, 0.84)):
        at = cue["count"] - (2 - n) * 0.5
        x, y = _at(s, u)
        _tick(c, x, y - 60, 1.0 if t >= at - 1e-6 else 0.0)
        d.glow(c, x, y - 60, 70, GOLD, 0.5 * d.pulse(t, at, 0.5))


def shot12(c, t, D, cue, view):
    on = t >= cue["lift"] - 1e-6
    s = week(c, t, view, warm_end=1.0 if on else 0.0, pins_only=True)
    d.glow(c, *s[-1], 180, "#FFF1D2", 0.6 * d.pulse(t, cue["lift"], 0.5))


def shot13(c, t, D, cue, view):
    pendant_talk(c, t, cue["lamp"], view, floor=760)


def shot14(c, t, D, cue, view):
    on = t >= cue["whole"] - 1e-6
    week(c, t, view, full=on, calm=1.0 if on else 0.0, warm_end=0.6, pins_only=not on)
    d.glow(c, 500, CY, 420, "#FFF1D2", 0.45 * d.pulse(t, cue["whole"], 0.5))


def shot15(c, t, D, cue, view):
    week(c, 6.0, view, full=True, calm=1.0, warm_end=0.6)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
