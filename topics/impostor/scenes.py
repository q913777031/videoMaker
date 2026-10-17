"""《升职了，为什么反而觉得自己是混进来的》15 个镜头的场景绘制（舞台 1000×1000 单位，撞击时刻一律读 cue）。"""

import math

import skia

from kepu import draw as d
from kepu.config import GOLD
from kepu.props import cell, die, mask, pedestal, pendant_talk, review_merge, thought_bubble

FLOOR = 760
PX = 470                         # 台座中心 x
DIE = (800, 700)


def _badge(c, j, k=1.0):
    """胸口的金色徽章。"""
    if k <= 0:
        return
    ux, uy = j["sh"][0] - j["hip"][0], j["sh"][1] - j["hip"][1]
    x, y = j["hip"][0] + ux * 0.72 + 8, j["hip"][1] + uy * 0.72
    c.drawCircle(x, y, 15 * k, d.fill(GOLD))
    c.drawCircle(x, y, 8 * k, d.fill("#8A6E3A"))


def podium(c, t, view, n=5.0, hollow=0.0, glow=0.0, pose_k=0.0, badge=1.0, sway=0.0, scale=1.0, x=PX, room=True):
    """台座构图：人物站在 n 层卡片台座上；hollow 为“纸板空壳”程度，pose_k 为缩肩程度，sway 为摇晃幅度（度）。"""
    if room:
        d.room(c, view, floor_y=FLOOR, warm=(x, 380, 0.35))
    top = pedestal(c, x, FLOOR, n, hollow=hollow, solid_glow=glow, w=260 * scale, h=46 * scale)
    c.save()
    c.translate(x, top)
    c.rotate(sway)
    c.translate(-x, -top)
    pose = d.blend(d.STAND, d.SLUMP, pose_k)
    j = d.figure(c, x, top - (d.SEG["th"] + d.SEG["sh"]) * scale, pose, facing=1, scale=scale)
    _badge(c, j, badge)
    c.restore()
    return j, top


# ---------------------------------------------------------------- 镜头 01–05

def shot01(c, t, D, cue, view):
    on = t >= cue["pin"] - 1e-6
    j, _ = podium(c, t, view, n=5, pose_k=d.ease_out(d.prog(t, cue["pin"], 0.8)), badge=1.0 if on else 0.0)
    if not on:
        k = d.ease_in(d.prog(t, cue["pin"] - 0.5, 0.5))
        c.drawCircle(d.lerp(820, j["sh"][0] + 8, k), d.lerp(150, j["sh"][1] + 40, k), 15, d.fill(GOLD))
    d.glow(c, j["sh"][0], j["sh"][1] + 40, 120, GOLD, 0.6 * d.pulse(t, cue["pin"], 0.6))


def _star_card(c, x, y, rot=0.0, a=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    d.paper(c, 0, 0, 110, 76, lift=0.5, a=a)
    p = skia.Path()
    for i in range(10):
        r = 24 if i % 2 == 0 else 10
        ang = -math.pi / 2 + i * math.pi / 5
        (p.moveTo if i == 0 else p.lineTo)(r * math.cos(ang), r * math.sin(ang))
    p.close()
    c.drawPath(p, d.fill(GOLD, a))
    c.restore()


def shot02(c, t, D, cue, view):
    podium(c, t, view, n=5, pose_k=0.6)
    die(c, *DIE, s=1.0)
    # 表扬卡：从左上飞来，在人物身前被拨开，最后加速落到骰子上
    land = cue["luck"]
    if t < land - 0.7:
        k = d.ease_out(d.prog(t, 0.2, land - 0.9))
        x, y = d.lerp(120, 560, k), d.lerp(160, 300, k)
    else:
        k = d.ease_in(d.prog(t, land - 0.7, 0.7))
        x, y = d.lerp(560, DIE[0], k), d.lerp(300, DIE[1] - 70, k)
    _star_card(c, x, y, rot=20 * d.prog(t, land - 0.7, 0.7))
    d.glow(c, DIE[0], DIE[1] - 40, 130, GOLD, 0.6 * d.pulse(t, land, 0.6))


def shot03(c, t, D, cue, view):
    after = t >= cue["hollow"] - 1e-6
    podium(c, t, view, n=5, hollow=1.0 if after else 0.0, pose_k=0.8)
    die(c, *DIE)
    d.glow(c, PX, 620, 260, "#E8C987", 0.5 * d.pulse(t, cue["hollow"], 0.6))


def shot04(c, t, D, cue, view):
    on = t >= cue["stack"] - 1e-6
    k = d.ease_in(d.prog(t, cue["stack"] - 0.5, 0.5))
    sway = 3.5 * math.sin((t - cue["stack"]) * 9) * math.exp(-(t - cue["stack"]) * 1.2) if on else 0.0
    podium(c, t, view, n=5 + (1 if on else 0), hollow=1.0, pose_k=1.0, sway=sway)
    if not on:
        y = d.lerp(-120, FLOOR - 5 * 52 - 23, k)
        c.drawRRect(d.rrect(PX, y, 260 - 5 * 18, 46, 8), d.stroke("#8C8574", 2.5, 1.0, dash=((12, 8), 0)))
    die(c, *DIE)
    d.glow(c, PX, FLOOR - 6 * 52, 160, GOLD, 0.55 * d.pulse(t, cue["stack"], 0.6))


def shot05(c, t, D, cue, view):
    k = d.ease_io(d.prog(t, cue["halt"], 1.2))
    podium(c, t, view, n=6, hollow=1.0, pose_k=1.0 - 0.4 * k)
    die(c, *DIE, a=1.0 - 0.6 * k)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.25 * k))


# ---------------------------------------------------------------- 镜头 06–10

def shot06(c, t, D, cue, view):
    review_merge(c, t, cue["merge"], view)


XS7 = (200, 400, 600, 800)


def _group(c, t, lit, masks):
    for i, x in enumerate(XS7):
        n = 4 + (i % 2)
        podium(c, t, None, n=n, glow=lit, pose_k=0.3, badge=0.0, scale=0.55, x=x, room=False)
        if masks > 0:
            top = FLOOR - n * (46 * 0.55 + 6)
            hy = top - 230 * 0.55 - 150
            thought_bubble(c, x, hy, 150, 92, a=masks, tail=(0.0, 1))
            mask(c, x, hy, s=0.75, a=masks)


def shot07(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["high"] - 1e-6
    _group(c, t, 1.0 if on else 0.0, 0.0)
    for x in XS7:
        d.glow(c, x, 640, 120, GOLD, 0.5 * d.pulse(t, cue["high"], 0.6))


def shot08(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["masks"] - 1e-6
    _group(c, t, 1.0, 1.0 if on else 0.0)
    for x in XS7:
        d.glow(c, x, 300, 110, GOLD, 0.5 * d.pulse(t, cue["masks"], 0.6))


def shot09(c, t, D, cue, view):
    j, top = podium(c, t, view, n=5, hollow=0.5, pose_k=0.7)
    die(c, *DIE, s=1.2)
    # 成绩卡一张接一张滑向骰子
    for i, t0 in enumerate((cue["fall"], cue["fall"] + 0.5, cue["fall"] + 1.0)):
        k = d.ease_in(d.prog(t, t0 - 0.6, 0.6))
        if 0 < k:
            x, y = d.lerp(260 + 40 * i, DIE[0], k), d.lerp(120, DIE[1] - 60, k)
            _star_card(c, x, y, rot=15 * k, a=1.0 - 0.7 * d.prog(t, t0, 0.4))
    on = t >= cue["empty"] - 1e-6
    w = 260 - 5 * 18
    c.drawRRect(d.rrect(PX, top - 23, w, 46, 8),
                d.stroke(GOLD, 3, 1.0 if on else 0.0, dash=((12, 8), 0)))
    d.glow(c, PX, top - 23, 150, GOLD, 0.55 * d.pulse(t, cue["empty"], 0.6))


def shot10(c, t, D, cue, view):
    on = t >= cue["solid"] - 1e-6
    z = d.lerp(1.25, 1.0, d.ease_in(d.prog(t, 0, cue["solid"])))
    c.save()
    c.translate(PX, 560)
    c.scale(z, z)
    c.translate(-PX, -560)
    podium(c, t, view, n=6, hollow=0.0 if on else 1.0, glow=1.0 if on else 0.0,
           pose_k=1.0 - d.ease_out(d.prog(t, cue["solid"], 1.2)))
    c.restore()
    d.glow(c, PX, 620, 300, GOLD, 0.6 * d.pulse(t, cue["solid"], 0.6))


# ---------------------------------------------------------------- 镜头 11–15

def _check(c, x, y, k):
    if k <= 0:
        return
    c.drawLine(x - 14, y, x - 4, y + 12, d.stroke(GOLD, 5, k))
    c.drawLine(x - 4, y + 12, x + 18, y - 14, d.stroke(GOLD, 5, k))


def shot11(c, t, D, cue, view):
    d.backdrop(c, view)
    d.paper(c, 500, 500, 520, 480, lift=1.2)
    for i in range(3):
        y = 380 + i * 120
        c.drawLine(380, y, 690, y, d.stroke("#8F897F", 6))
        at = cue["third"] - (2 - i) * 0.6
        _check(c, 330, y, 1.0 if t >= at - 1e-6 else 0.0)
        d.glow(c, 330, y, 70, GOLD, 0.5 * d.pulse(t, at, 0.5))


def shot12(c, t, D, cue, view):
    d.backdrop(c, view)
    cell(c, 300, 520, "act", w=300, h=380)
    cell(c, 700, 520, "fact", w=300, h=380)
    die(c, 300, 300, s=0.8)
    pedestal(c, 700, 330, 3, w=120, h=26)
    on = t >= cue["sort"] - 1e-6
    hover = d.ease_out(d.prog(t, 0.3, 0.8))
    drop = d.ease_in(d.prog(t, cue["sort"] - 3 / 30, 3 / 30))
    for i in range(5):
        tx = 300 if i == 0 else 700
        ty = 560 + (i % 3) * 22 - (0 if i == 0 else (i - 1) * 8)
        hx, hy = d.lerp(500, tx, hover), ty - 150
        x, y = hx, d.lerp(hy, ty, drop)
        _star_card(c, x + (i - 2) * 6, y, rot=(i - 2) * 6, a=hover)
    d.glow(c, 700, 560, 180, GOLD, 0.55 * d.pulse(t, cue["sort"], 0.6) if on else 0.0)


def shot13(c, t, D, cue, view):
    pendant_talk(c, t, cue["lamp"], view, floor=FLOOR)


STEPS = [(300, 2), (430, 3), (560, 4), (690, 5)]


def shot14(c, t, D, cue, view):
    d.room(c, view, floor_y=FLOOR, warm=(560, 380, 0.7))
    for x, n in STEPS:
        pedestal(c, x, FLOOR, n, solid_glow=0.6, w=130, h=46)
    k = d.ease_in(d.prog(t, cue["step"] - 0.6, 0.6))
    after = t >= cue["step"] - 1e-6
    x0, n0 = STEPS[2]
    x1, n1 = STEPS[3]
    x = d.lerp(x0, x1, k)
    top = FLOOR - d.lerp(n0, n1, k) * 52 - (0 if after else 30 * math.sin(math.pi * k))
    pose = d.walk(k * math.pi) if not after else d.blend(d.SLUMP, d.STAND, 1.0)
    j = d.figure(c, x, top - (d.SEG["th"] + d.SEG["sh"]) * 0.8, pose, facing=1, scale=0.8)
    _badge(c, j, 0.8)
    d.glow(c, x1, FLOOR - n1 * 52, 160, GOLD, 0.55 * d.pulse(t, cue["step"], 0.6))


def shot15(c, t, D, cue, view):
    shot14(c, 6.0, D, {"step": 1.0}, view)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
