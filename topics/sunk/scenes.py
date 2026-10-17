"""《项目明明没希望，为什么还舍不得停》15 个镜头的场景绘制（舞台 1000×1000 单位，撞击时刻一律读 cue）。"""

import math

import skia

from kepu import draw as d
from kepu.config import GOLD
from kepu.props import (balance, dead_end, jar, pedestal, pendant_talk, review_merge, seats)

FLOOR = 760
PILE_X = 300
FIG_X = 520
WALL_X = 820


def _path(c, k, a=1.0, x0=FIG_X + 60, x1=WALL_X - 60):
    """通往墙的进度路径：已走部分实线，余下虚线。"""
    c.drawLine(x0, FLOOR - 4, x1, FLOOR - 4, d.stroke(GOLD, 2, 0.35 * a, dash=((10, 8), 0)))
    xe = x0 + (x1 - x0) * k
    c.drawLine(x0, FLOOR - 4, xe, FLOOR - 4, d.stroke(GOLD, 6, a))
    c.drawCircle(xe, FLOOR - 4, 9, d.fill(GOLD, a))


def _drop_card(c, x, top, t, at, w=150, dur=0.45):
    """一张投入卡从上方加速砸到 top 位置。"""
    if t >= at or t < at - dur:
        return
    k = d.ease_in(d.prog(t, at - dur, dur))
    y = d.lerp(-150, top - 23, k)
    c.drawRRect(d.rrect(x, y, w, 46, 8), d.fill(d.WHITE))
    c.drawCircle(x + w * 0.32, y, 9, d.fill(GOLD))


def yard(c, t, view, n=4.0, bar_k=0.5, pose=None, hollow=0.0, glow=0.0, shade=0.0, facing=1, path_a=1.0,
         wall=True):
    """沉没成本构图：左侧投入堆（n 层），中间人物，右侧通往一堵墙的进度路径（bar_k）。返回 (关节点, 堆顶 y)。"""
    d.room(c, view, floor_y=FLOOR, warm=(500, 380, 0.3))
    top = pedestal(c, PILE_X, FLOOR, n, hollow=hollow, solid_glow=glow, w=240, h=46)
    if shade > 0:
        p = skia.Path()
        p.moveTo(PILE_X + 120, top)
        p.lineTo(FIG_X + 160, FLOOR)
        p.lineTo(PILE_X + 120, FLOOR)
        p.close()
        c.drawPath(p, d.fill("#000000", 0.5 * shade, blur=20))
    if wall:
        dead_end(c, WALL_X, FLOOR, crack=0.6)
    _path(c, bar_k, a=path_a)
    d.floor_shadow(c, FIG_X, FLOOR + 6, 160, 0.5)
    j = d.figure(c, FIG_X, FLOOR - (d.SEG["th"] + d.SEG["sh"]), pose or d.SLUMP, facing=facing)
    return j, top


# ---------------------------------------------------------------- 镜头 01–05

def shot01(c, t, D, cue, view):
    on = t >= cue["add"] - 1e-6
    j, top = yard(c, t, view, n=4 + (1 if on else 0), bar_k=0.55, facing=-1)
    _drop_card(c, PILE_X, FLOOR - 4 * 52, t, cue["add"], w=240 - 4 * 18)
    d.glow(c, PILE_X, top, 180, GOLD, 0.6 * d.pulse(t, cue["add"], 0.6))


def shot02(c, t, D, cue, view):
    on = t >= cue["clock"] - 1e-6
    j, top = yard(c, t, view, n=5, bar_k=0.55, glow=1.0 if on else 0.0, facing=-1)
    d.glow(c, PILE_X, (top + FLOOR) / 2, 220, GOLD, 0.55 * d.pulse(t, cue["clock"], 0.6))


def shot03(c, t, D, cue, view):
    on = t >= cue["more"] - 1e-6
    first = cue["more"] - 0.9
    n = 5 + (1 if t >= first else 0) + (1 if on else 0)
    j, top = yard(c, t, view, n=n, bar_k=0.55 + (0.1 if t >= first else 0) + (0.15 if on else 0))
    _drop_card(c, PILE_X, FLOOR - 5 * 52, t, first, w=240 - 5 * 18)
    _drop_card(c, PILE_X, FLOOR - 6 * 52, t, cue["more"], w=240 - 6 * 18)
    d.glow(c, PILE_X, top, 200, GOLD, 0.6 * d.pulse(t, cue["more"], 0.6))


def shot04(c, t, D, cue, view):
    k = d.ease_in(d.prog(t, cue["tower"] - 0.6, 0.6))
    on = t >= cue["tower"] - 1e-6
    yard(c, t, view, n=7 + 2 * k, bar_k=0.8, shade=1.0 if on else 0.4 * k, pose=d.blend(d.SLUMP, d.LOWER, k))
    d.glow(c, PILE_X, FLOOR - 9 * 52, 200, GOLD, 0.55 * d.pulse(t, cue["tower"], 0.6))


def shot05(c, t, D, cue, view):
    k = d.ease_io(d.prog(t, cue["halt"], 1.0))
    yard(c, t, view, n=9, bar_k=0.8, glow=0.5 * k)
    # 前方箭头（未来）
    a = k
    c.drawLine(FIG_X + 80, 420, FIG_X + 280, 420, d.stroke(GOLD, 5, a))
    c.drawLine(FIG_X + 255, 400, FIG_X + 280, 420, d.stroke(GOLD, 5, a))
    c.drawLine(FIG_X + 255, 440, FIG_X + 280, 420, d.stroke(GOLD, 5, a))


# ---------------------------------------------------------------- 镜头 06–10

def shot06(c, t, D, cue, view):
    review_merge(c, t, cue["merge"], view)


def _ticket(c, x, y, wide, a=1.0):
    d.paper(c, x, y, 220 if wide else 150, 90, lift=0.6, a=a)
    c.drawLine(x - 50, y - 15, x + 40, y - 15, d.stroke("#8F897F", 5, a))
    for i in range(3 if wide else 1):
        c.drawCircle(x - 40 + i * 30, y + 18, 9, d.fill(GOLD, a))


def shot07(c, t, D, cue, view):
    d.backdrop(c, view)
    lo = t >= cue["cheap"] - 1e-6
    hi = t >= cue["full"] - 1e-6
    _ticket(c, 300, 250, False)
    _ticket(c, 700, 250, True)
    seats(c, 300, 420, 12, 3 if lo else 0, cols=4, s=1.2)
    seats(c, 700, 420, 12, 9 if hi else 0, cols=4, s=1.2)
    d.glow(c, 300, 470, 180, GOLD, 0.5 * d.pulse(t, cue["cheap"], 0.5))
    d.glow(c, 700, 470, 180, GOLD, 0.5 * d.pulse(t, cue["full"], 0.5))


def shot08(c, t, D, cue, view):
    on = t >= cue["name"] - 1e-6
    yard(c, t, view, n=9, bar_k=0.8, glow=1.0 if on else 0.0)
    y = 0 if on else d.lerp(-600, 0, d.ease_in(d.prog(t, cue["name"] - 0.5, 0.5)))
    c.drawRRect(d.rrect(PILE_X, FLOOR - 250 + y, 300, 520, 18), d.stroke(GOLD, 4))
    d.glow(c, PILE_X, FLOOR - 250, 260, GOLD, 0.55 * d.pulse(t, cue["name"], 0.6))


def _bin(c, x, y, a=1.0):
    p = skia.Path()
    p.moveTo(x - 55, y - 70)
    p.lineTo(x + 55, y - 70)
    p.lineTo(x + 42, y + 60)
    p.lineTo(x - 42, y + 60)
    p.close()
    c.drawPath(p, d.fill("#24252A", a))
    c.drawPath(p, d.stroke(GOLD, 2.5, a))
    for i in range(3):
        c.drawLine(x - 25 + i * 25, y - 45, x - 20 + i * 20, y + 45, d.stroke("#3A3833", 3, a))


def shot09(c, t, D, cue, view):
    k = d.ease_in(d.prog(t, cue["reach"], cue["block"] - cue["reach"]))
    on = t >= cue["block"] - 1e-6
    d.room(c, view, floor_y=FLOOR, warm=(500, 380, 0.3))
    pedestal(c, PILE_X, FLOOR, 8, w=240, h=46)
    _bin(c, 760, FLOOR - 60)
    x = d.lerp(470, 640, k)
    pose = d.REACH if on else d.walk(t * 2 * math.pi / 0.8) if t > cue["reach"] else d.STAND
    d.floor_shadow(c, x, FLOOR + 6, 150, 0.5)
    d.figure(c, x, FLOOR - (d.SEG["th"] + d.SEG["sh"]), pose, facing=-1 if on else 1)
    d.glow(c, 700, FLOOR - 120, 180, GOLD, 0.55 * d.pulse(t, cue["block"], 0.5))


def shot10(c, t, D, cue, view):
    d.backdrop(c, view)
    pedestal(c, 300, 760, 7, w=200, h=40)
    on = t >= cue["inflate"] - 1e-6
    k = d.ease_in(d.prog(t, cue["inflate"] - 0.6, 0.6))
    jar(c, 700, 540, 0.35 + 0.5 * k, s=1.6, dashed=True)
    jar(c, 700, 540, 0.35, s=1.6, a=0.0)
    c.drawLine(590, 540 + 136 - 272 * 0.35, 810, 540 + 136 - 272 * 0.35,
               d.stroke("#CFE0F0", 2.5, 0.8 if on else 0.0, dash=((8, 6), 0)))
    d.glow(c, 700, 420, 180, GOLD, 0.55 * d.pulse(t, cue["inflate"], 0.5))


# ---------------------------------------------------------------- 镜头 11–15

def shot11(c, t, D, cue, view):
    on = t >= cue["reset"] - 1e-6
    yard(c, t, view, n=9, bar_k=0.0 if on else 0.8, hollow=1.0 if on else 0.0, pose=d.STAND)
    d.glow(c, FIG_X, 500, 220, "#FFF1D2", 0.5 * d.pulse(t, cue["reset"], 0.5))


def _cost(c, x, y):
    c.drawRRect(d.rrect(x, y, 90, 60, 8), d.fill("#3A3631"))
    c.drawLine(x - 20, y - 12, x + 20, y + 12, d.stroke("#E8C987", 4))
    c.drawLine(x + 20, y - 12, x - 20, y + 12, d.stroke("#E8C987", 4))


def _gain(c, x, y):
    jar(c, x, y - 20, 0.7, s=0.55)


def shot12(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["weigh"] - 1e-6
    tilt = 6.0 * math.sin((t - cue["weigh"]) * 8) * math.exp(-(t - cue["weigh"]) * 2.5) if on else 0.0
    balance(c, 500, 330, tilt=tilt, left=_cost if on else None, right=_gain if on else None)
    pedestal(c, 140, 760, 6, hollow=1.0, w=160, h=34)
    d.glow(c, 500, 430, 260, GOLD, 0.5 * d.pulse(t, cue["weigh"], 0.5))


def shot13(c, t, D, cue, view):
    pendant_talk(c, t, cue["lamp"], view, floor=FLOOR)


def shot14(c, t, D, cue, view):
    on = t >= cue["turn"] - 1e-6
    d.room(c, view, floor_y=FLOOR, warm=(200, 380, 0.6 if on else 0.2))
    dead_end(c, WALL_X, FLOOR, crack=0.6)
    pedestal(c, 640, FLOOR, 7, w=200, h=40, hollow=0.6)
    if on:
        g = skia.GradientShader.MakeLinear([(0, 0), (FIG_X, 0)], [d.col("#F2D59A", 0.28), d.col("#F2D59A", 0.0)])
        c.drawRect(skia.Rect.MakeLTRB(-400, 300, FIG_X, FLOOR), skia.Paint(Shader=g))
        c.drawLine(-400, FLOOR - 4, FIG_X - 40, FLOOR - 4, d.stroke(GOLD, 6))
    d.floor_shadow(c, FIG_X, FLOOR + 6, 160, 0.5)
    d.figure(c, FIG_X, FLOOR - (d.SEG["th"] + d.SEG["sh"]), d.STAND if on else d.SLUMP, facing=-1 if on else 1)
    d.glow(c, FIG_X - 150, 560, 240, "#FFF1D2", 0.5 * d.pulse(t, cue["turn"], 0.5))


def shot15(c, t, D, cue, view):
    shot14(c, 6.0, D, {"turn": 1.0}, view)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
