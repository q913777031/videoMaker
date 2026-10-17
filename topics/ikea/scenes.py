"""《自己做的方案，为什么怎么看都比别人好》15 个镜头的场景绘制（舞台 1000×1000 单位，撞击时刻一律读 cue）。"""

import numpy as np
import skia

from kepu import draw as d
from kepu.config import GOLD
from kepu.props import (bust, cell, heart, pendant_talk, price_tag, review_merge, slide, speech_bubble,
                        thought_bubble)

FLOOR = 760
ME = (270, 640)
OWN = (580, 430)            # 自己的方案（画板上）
TAG_X, TAG_BASE = 805, 700


def studio(c, t, view, halo=0.0, value=0.4, comment=0.0, effort=0.0, pose=None, other=0.0, warm=0.35, own_scale=1.0):
    """方案构图：左侧人物坐着，中间画板上是自己的方案，右侧是价值条；other>0 时右下出现一位旁观同事。"""
    d.room(c, view, floor_y=FLOOR, warm=(OWN[0], 380, warm))
    # 画板
    c.drawLine(OWN[0] - 120, FLOOR, OWN[0] - 60, OWN[1] + 60, d.stroke("#3A3833", 6))
    c.drawLine(OWN[0] + 120, FLOOR, OWN[0] + 60, OWN[1] + 60, d.stroke("#3A3833", 6))
    if halo > 0:
        d.glow(c, *OWN, 330 * own_scale, GOLD, 0.45 * halo)
        c.drawRRect(d.rrect(*OWN, 400 * own_scale, 250 * own_scale, 16), d.stroke(GOLD, 4, halo))
    slide(c, *OWN, 360 * own_scale, 210 * own_scale, mark_k=0.0)
    if effort > 0:
        for i in range(5):
            y = 640 - i * 30
            c.drawRRect(d.rrect(430, y, 120, 26, 6), d.fill("#F5E7C4", effort))
            c.drawCircle(470, y, 7, d.fill(GOLD, effort))
        c.drawLine(490, 520, OWN[0] - 150, OWN[1] + 60, d.stroke(GOLD, 3, effort))
    if comment > 0:
        speech_bubble(c, OWN[0] + 60, OWN[1] - 150 * comment - 20, 200, 70, side=1, a=min(1.0, comment * 2))
    price_tag(c, TAG_X, TAG_BASE, 60 + 380 * value)
    if other > 0:
        bust(c, 740, 920 - 260 * other, look=0.0, scale=0.85, a=min(1.0, other * 2))
    c.drawRect(skia.Rect.MakeLTRB(ME[0] - 60, ME[1] + 10, ME[0] + 60, ME[1] + 22), d.fill("#1D1C19"))
    c.drawRect(skia.Rect.MakeLTRB(ME[0] - 66, 520, ME[0] - 54, FLOOR), d.fill("#1D1C19"))
    return d.figure(c, *ME, pose or d.SIT_EASE, facing=1)


# ---------------------------------------------------------------- 镜头 01–05

def shot01(c, t, D, cue, view):
    on = t >= cue["halo"] - 1e-6
    studio(c, t, view, halo=1.0 if on else 0.0, value=0.55)
    # 远处同事的方案，平平无奇
    slide(c, 250, 250, 150, 90, a=0.5)
    d.sparks(c, *OWN, t, cue["halo"], n=18, r=280, seed=12)


def shot02(c, t, D, cue, view):
    k = d.ease_in(d.prog(t, cue["comment"] - 0.5, 0.5))
    on = t >= cue["comment"] - 1e-6
    studio(c, t, view, halo=1.0, value=0.55, comment=k, pose=d.SIT if on else d.SIT_EASE)
    d.glow(c, OWN[0] + 60, OWN[1] - 170, 150, "#E8C987", 0.55 * d.pulse(t, cue["comment"], 0.5))


def shot03(c, t, D, cue, view):
    on = t >= cue["effort"] - 1e-6
    studio(c, t, view, halo=1.0, value=0.6, effort=1.0 if on else 0.0)
    d.glow(c, 470, 580, 180, GOLD, 0.55 * d.pulse(t, cue["effort"], 0.5))


def shot04(c, t, D, cue, view):
    k = d.ease_in(d.prog(t, cue["value"] - 0.5, 0.5))
    studio(c, t, view, halo=1.0, value=0.6 + 0.35 * k, effort=1.0)
    d.glow(c, TAG_X, TAG_BASE - 440, 160, GOLD, 0.55 * d.pulse(t, cue["value"], 0.5))


def shot05(c, t, D, cue, view):
    k = d.ease_out(d.prog(t, cue["halt"], 0.8))
    studio(c, t, view, halo=1.0 - 0.5 * k, value=0.95, other=k)


# ---------------------------------------------------------------- 镜头 06–10

def shot06(c, t, D, cue, view):
    review_merge(c, t, cue["merge"], view)


def crane(c, x, y, s=1.0, neat=True, a=1.0):
    """折纸鹤：neat=False 时边角歪斜（业余作品）。"""
    j = 0.0 if neat else 1.0
    p = skia.Path()
    pts = [(-90, 10 + 14 * j), (-20, -10), (0, -70 - 10 * j), (24, -8), (100, -40 + 18 * j), (40, 20), (0, 40 - 8 * j)]
    p.moveTo(x + pts[0][0] * s, y + pts[0][1] * s)
    for px, py in pts[1:]:
        p.lineTo(x + px * s, y + py * s)
    p.close()
    c.drawPath(p, d.fill(d.WHITE if neat else "#EDE3CF", a))
    c.drawPath(p, d.stroke(GOLD, 2, 0.7 * a))
    c.drawLine(x, y - 70 * s, x, y + 40 * s, d.stroke("#C9C0AE", 2, a))


def shot07(c, t, D, cue, view):
    d.backdrop(c, view)
    ko = d.ease_in(d.prog(t, cue["own"] - 0.5, 0.5))
    kp = d.ease_in(d.prog(t, cue["pro"] - 0.5, 0.5))
    crane(c, 290, 640, 1.2, neat=False)
    crane(c, 690, 640, 1.2, neat=True)
    price_tag(c, 290, 520, 40 + 260 * ko)
    price_tag(c, 690, 520, 40 + 260 * kp)
    if t >= cue["pro"] - 1e-6:
        c.drawLine(230, 520 - 300, 750, 520 - 300, d.stroke(GOLD, 2, 0.8, dash=((10, 8), 0)))
    d.glow(c, 290, 260, 140, GOLD, 0.55 * d.pulse(t, cue["own"], 0.5))
    d.glow(c, 690, 260, 140, GOLD, 0.55 * d.pulse(t, cue["pro"], 0.5))


def shot08(c, t, D, cue, view):
    d.backdrop(c, view)
    crane(c, 260, 660, 1.0, neat=False)
    price_tag(c, 260, 560, 300)
    on = t >= cue["others"] - 1e-6
    for x in (560, 780):
        bust(c, x, 690, look=0.0, scale=0.9)
        if on:
            thought_bubble(c, x, 360, 170, 230, tail=(0.0, 1))
            price_tag(c, x, 440, 120, a=1.0)
    d.glow(c, 670, 360, 220, GOLD, 0.55 * d.pulse(t, cue["others"], 0.5))


def cabinet(c, x, y, k=1.0, a=1.0, t=0.0, scatter=0.0):
    """组装柜：k 为组装完成度；scatter>0 时散成零件。"""
    rng = np.random.default_rng(3)
    parts = [(-90, -110, 180, 16), (-90, 94, 180, 16), (-98, -110, 16, 220), (82, -110, 16, 220),
             (-82, -10, 164, 12), (-70, 20, 60, 60), (10, 20, 60, 60)]
    for i, (px, py, w, h) in enumerate(parts):
        on = min(1.0, max(0.0, k * len(parts) - i))
        if on <= 0:
            continue
        ox = scatter * rng.uniform(-260, 260)
        oy = scatter * rng.uniform(40, 180)
        rot = scatter * rng.uniform(-70, 70)
        c.save()
        c.translate(x + px + w / 2 + ox, y + py + h / 2 + oy)
        c.rotate(rot)
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), d.fill("#C9A86A" if i < 5 else "#8A6E3A", a * on))
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), d.stroke(GOLD, 1.5, a * on))
        c.restore()


def shot09(c, t, D, cue, view):
    d.room(c, view, floor_y=FLOOR, warm=(500, 380, 0.5))
    cabinet(c, 500, 640, k=1.0)
    on = t >= cue["name"] - 1e-6
    y = 470 if on else d.lerp(100, 470, d.ease_in(d.prog(t, cue["name"] - 0.5, 0.5)))
    heart(c, 500, y, s=1.6, k=1.0)
    d.glow(c, 500, 480, 260, GOLD, 0.6 * d.pulse(t, cue["name"], 0.5))
    d.figure(c, 260, FLOOR - (d.SEG["th"] + d.SEG["sh"]), d.STAND, facing=1)


def shot10(c, t, D, cue, view):
    d.room(c, view, floor_y=FLOOR, warm=(500, 380, 0.4))
    on = t >= cue["undo"] - 1e-6
    sc = d.ease_out(d.prog(t, cue["undo"], 0.5)) if on else 0.0
    cabinet(c, 460, 600, k=1.0, scatter=sc)
    price_tag(c, 820, 700, 360 if not on else d.lerp(360, 80, d.ease_out(d.prog(t, cue["undo"], 0.4))))
    if not on:
        heart(c, 460, 440, s=1.2, k=1.0)
    d.glow(c, 460, 600, 260, "#E8C987", 0.55 * d.pulse(t, cue["undo"], 0.5))


# ---------------------------------------------------------------- 镜头 11–15

def shot11(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["rate"] - 1e-6
    slide(c, 500, 230, 300, 170)
    price_tag(c, 330, 740, 280, dashed=True)
    bust(c, 720, 690, look=0.0, scale=0.85)
    if on:
        price_tag(c, 580, 740, 170)
    d.glow(c, 580, 560, 150, GOLD, 0.55 * d.pulse(t, cue["rate"], 0.5))


def shot12(c, t, D, cue, view):
    d.backdrop(c, view)
    cell(c, 300, 540, "act", w=300, h=380)
    cell(c, 700, 540, "fact", w=300, h=380)
    hover = d.ease_out(d.prog(t, 0.3, 0.8))
    drop = d.ease_in(d.prog(t, cue["sort"] - 3 / 30, 3 / 30))
    for i in range(3):
        y = d.lerp(330 + i * 34, 520 + i * 34, drop)
        c.drawRRect(d.rrect(300, y, 120, 26, 6), d.fill("#F5E7C4", hover))
        c.drawCircle(340, y, 7, d.fill(GOLD, hover))
    slide(c, 700, d.lerp(330, 560, drop), 200, 120, a=hover)
    d.glow(c, 500, 560, 260, GOLD, 0.55 * d.pulse(t, cue["sort"], 0.5))


def shot13(c, t, D, cue, view):
    pendant_talk(c, t, cue["lamp"], view, floor=FLOOR)


def shot14(c, t, D, cue, view):
    on = t >= cue["settle"] - 1e-6
    studio(c, t, view, halo=0.3, value=0.55 if on else 0.95, effort=1.0, warm=0.6)
    hy = d.lerp(TAG_BASE - 480, 300, d.ease_out(d.prog(t, cue["settle"], 0.6))) if on else TAG_BASE - 480
    hx = d.lerp(TAG_X, 470, d.ease_out(d.prog(t, cue["settle"], 0.6))) if on else TAG_X
    heart(c, hx, hy, s=1.0, k=1.0)
    d.glow(c, TAG_X, TAG_BASE - 260, 170, GOLD, 0.55 * d.pulse(t, cue["settle"], 0.5))


def shot15(c, t, D, cue, view):
    shot14(c, 6.0, D, {"settle": 1.0}, view)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
