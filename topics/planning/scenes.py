"""《说好周五交，为什么又拖到下周》15 个镜头的场景绘制（舞台 1000×1000 单位，撞击时刻一律读 cue）。"""

import skia

from kepu import draw as d
from kepu.config import GOLD
from kepu.props import bar, book, deadline_flag, pendant_talk, review_merge, schedule, shelf, thought_bubble

FLOOR = 760
S0, S1, SY = 140, 880, 250          # 日程条
BAR_Y = 320                          # 计划条
HIP = (330, 640)                     # 坐姿人物髋部


def _sx(k):
    return S0 + (S1 - S0) * k


def office(c, t, view, flag=0.55, flag_k=1.0, card=None, card_a=1.0, bar_end=None, bar_ghost=None, slump=0.0,
           pose=None, warm=0.3, backdrop_fn=None):
    """办公构图：人物坐在桌前，头顶是日程条（截止旗 flag）与计划条（bar_end，0–1）。

    card 为任务卡在日程条上的位置；bar_ghost 为实际用时的虚线条终点。
    """
    d.room(c, view, floor_y=FLOOR, warm=(500, 380, warm))
    if backdrop_fn is not None:
        backdrop_fn()
    schedule(c, S0, S1, SY, flag=flag, flag_k=flag_k)
    if bar_ghost is not None:
        bar(c, S0, _sx(bar_ghost), BAR_Y, dashed=True, a=0.8)
    if bar_end is not None:
        bar(c, S0, _sx(bar_end), BAR_Y, color=GOLD, a=0.9)
    if card is not None:
        d.mark_card(c, _sx(card), SY - 60, w=96, h=64, lift=0.5, a=card_a)
    # 桌椅与人物
    c.drawRect(skia.Rect.MakeLTRB(270, 650, 390, 662), d.fill("#1D1C19"))
    c.drawRect(skia.Rect.MakeLTRB(262, 520, 274, FLOOR), d.fill("#1D1C19"))
    c.drawRect(skia.Rect.MakeLTRB(430, 600, 760, 614), d.fill("#2A2824"))
    c.drawLine(430, 600, 760, 600, d.stroke(GOLD, 1.5, 0.5))
    c.drawRect(skia.Rect.MakeLTRB(450, 614, 462, FLOOR), d.fill("#1D1C19"))
    c.drawRect(skia.Rect.MakeLTRB(728, 614, 740, FLOOR), d.fill("#1D1C19"))
    c.drawLine(560, 600, 640, 600, d.stroke("#3A3833", 5))
    c.drawLine(640, 600, 652, 546, d.stroke("#3A3833", 5))
    d.glow(c, 640, 570, 70, "#CFE0F0", 0.15)
    p = pose if pose is not None else d.blend(d.SIT_EASE, d.SIT, slump)
    return d.figure(c, *HIP, p, facing=1)


# ---------------------------------------------------------------- 镜头 01–05

def shot01(c, t, D, cue, view):
    # 任务卡匀速前进，在 cue 帧越过截止旗
    v = 0.12
    k = 0.55 + v * (t - cue["pass"])
    office(c, t, view, flag=0.55, card=k, bar_end=min(k, 0.95), slump=d.prog(t, cue["pass"], 1.0))
    d.glow(c, _sx(0.55), SY - 60, 140, "#E8C987", 0.6 * d.pulse(t, cue["pass"], 0.6))


def shot02(c, t, D, cue, view):
    k = d.ease_in(d.prog(t, 0.3, cue["plan"] - 0.3))
    office(c, t, view, flag=0.7, bar_end=0.4 * k, pose=d.SIT_EASE)
    d.glow(c, _sx(0.4), BAR_Y, 110, GOLD, 0.5 * d.pulse(t, cue["plan"], 0.6))


def _hit_card(c, x, y_target, t, at, dur=0.45):
    """意外事件卡：从上方加速落到计划条末端。"""
    if t < at - dur:
        return
    k = d.ease_in(d.prog(t, at - dur, dur))
    y = d.lerp(-200, y_target, k)
    c.drawRRect(d.rrect(x, y, 90, 60, 8), d.fill("#3A3631"))
    c.drawRRect(d.rrect(x, y, 90, 60, 8), d.stroke(GOLD, 2, 0.7))
    c.drawLine(x - 20, y - 12, x + 20, y + 12, d.stroke("#E8C987", 4))
    c.drawLine(x + 20, y - 12, x - 20, y + 12, d.stroke("#E8C987", 4))


def shot03(c, t, D, cue, view):
    end = 0.4 + (0.15 if t >= cue["drop1"] else 0) + (0.3 if t >= cue["drop2"] else 0)
    office(c, t, view, flag=0.7, bar_end=end, slump=d.prog(t, cue["drop2"], 1.0))
    if t < cue["drop1"] + 0.3:
        _hit_card(c, _sx(0.48), BAR_Y - 50, t, cue["drop1"])
    if t < cue["drop2"] + 0.3:
        _hit_card(c, _sx(0.7), BAR_Y - 50, t, cue["drop2"])
    d.glow(c, _sx(0.85), BAR_Y, 160, "#E8C987", 0.55 * d.pulse(t, cue["drop2"], 0.6))


def shot04(c, t, D, cue, view):
    office(c, t, view, flag=0.7, bar_end=0.85, bar_ghost=None, slump=1.0)
    a = d.ease_out(d.prog(t, 0.1, 0.5))
    thought_bubble(c, 560, 470, 520, 190, a=a, tail=(-0.55, 1))
    # 气泡里：一条从起点直达旗子的直线
    k = d.ease_in(d.prog(t, 0.6, cue["dream"] - 0.6))
    if a > 0:
        c.drawLine(360, 470, d.lerp(360, 720, k), 470, d.stroke(GOLD, 5, a))
        c.drawLine(740, 470, 740, 410, d.stroke(GOLD, 3, a))
        p = skia.Path()
        p.moveTo(740, 410)
        p.lineTo(780, 422)
        p.lineTo(740, 434)
        p.close()
        c.drawPath(p, d.fill(GOLD, a))
    d.glow(c, 720, 470, 120, GOLD, 0.5 * d.pulse(t, cue["dream"], 0.6))


def shot05(c, t, D, cue, view):
    k = d.ease_io(d.prog(t, cue["halt"], 1.2))
    office(c, t, view, flag=0.7, bar_end=0.85, slump=1.0 - 0.5 * k,
           backdrop_fn=lambda: shelf(c, 40, 220, 520, n=4, a=0.25 + 0.6 * k, lit=1, lit_k=0.4 * k))


# ---------------------------------------------------------------- 镜头 06–10

def shot06(c, t, D, cue, view):
    review_merge(c, t, cue["merge"], view)


def _home(c, x, y, a=1.0):
    p = skia.Path()
    p.moveTo(x - 40, y + 30)
    p.lineTo(x - 40, y - 10)
    p.lineTo(x, y - 44)
    p.lineTo(x + 40, y - 10)
    p.lineTo(x + 40, y + 30)
    p.close()
    c.drawPath(p, d.fill("#2A2824", a))
    c.drawPath(p, d.stroke(GOLD, 2.5, a))
    c.drawRect(skia.Rect.MakeLTRB(x - 10, y + 2, x + 10, y + 30), d.fill(GOLD, 0.7 * a))


def _row(c, y, icon, t, at):
    """一行：左侧图标，右侧“预测”（虚线）与“实际”（实心，于 at 时刻伸长）两条。"""
    icon(c, 170, y)
    x0 = 280
    bar(c, x0, 560, y - 28, h=30, dashed=True)
    k = d.ease_in(d.prog(t, at - 0.5, 0.5))
    bar(c, x0, d.lerp(x0 + 10, 860, k), y + 28, h=30, color=GOLD, a=0.9)
    d.glow(c, 860, y + 28, 110, GOLD, 0.5 * d.pulse(t, at, 0.6))


def shot07(c, t, D, cue, view):
    d.backdrop(c, view)
    _row(c, 380, lambda c_, x, y: book(c_, x, y, s=0.32), t, cue["study"])
    _row(c, 640, _home, t, cue["chore"])


def shot08(c, t, D, cue, view):
    d.backdrop(c, view)
    schedule(c, S0, S1, 500)
    bar(c, S0, _sx(0.4), 570, color=GOLD, a=0.95)
    bar(c, S0, _sx(0.9), 630, dashed=True, a=0.7)
    on = t >= cue["name"] - 1e-6
    if not on:
        drop = d.ease_in(d.prog(t, cue["name"] - 0.5, 0.5))
        y = d.lerp(-300, 0, drop)
    else:
        y = 0
    c.save()
    c.translate(0, y)
    deadline_flag(c, _sx(0.4), 500)
    c.restore()
    d.glow(c, _sx(0.4), 450, 220, GOLD, 0.55 * d.pulse(t, cue["name"], 0.6))
    if on:
        d.sparks(c, _sx(0.4), 500, t, cue["name"], n=16, r=200, seed=8)


def shot09(c, t, D, cue, view):
    d.room(c, view, floor_y=FLOOR, warm=(700, 400, 0.3))
    shelf(c, 60, 300, 560, n=4, a=0.35)
    lit = t >= cue["future"] - 1e-6
    # 前方的理想路径
    c.drawLine(560, FLOOR - 2, 980, FLOOR - 2, d.stroke(GOLD, 6, 1.0 if lit else 0.2))
    if lit:
        g = skia.GradientShader.MakeLinear([(560, 0), (1000, 0)], [d.col("#F2D59A", 0.0), d.col("#F2D59A", 0.25)])
        c.drawRect(skia.Rect.MakeLTRB(560, 300, 1000, FLOOR), skia.Paint(Shader=g))
    turn = d.ease_out(d.prog(t, cue["gaze"], 0.6))
    pose = d.blend(d.STAND, d.Pose(torso=-2, head=-8), turn)
    d.floor_shadow(c, 470, FLOOR + 6, 160, 0.5)
    d.figure(c, 470, FLOOR - (d.SEG["th"] + d.SEG["sh"]), pose, facing=1)
    d.glow(c, 800, 600, 260, "#FFF1D2", 0.45 * d.pulse(t, cue["future"], 0.6))


def shot10(c, t, D, cue, view):
    d.backdrop(c, view)
    shelf(c, 80, 360, 700, n=4, lit=2, lit_k=1.0)
    schedule(c, 420, 920, 380, ticks=8, flag=0.9)
    x0 = 420
    k = d.ease_in(d.prog(t, cue["link"] - 0.5, 0.5))
    after = t >= cue["link"] - 1e-6
    end = 0.88 if after else 0.45
    bar(c, x0, x0 + 500 * end, 450, color=GOLD, a=0.95)
    bar(c, x0, x0 + 500 * 0.88, 510, dashed=True, a=0.6)
    # 连线：从被点亮的旧记录到计划条
    sx, sy = 80 + 280 / 4 * 2.5, 600
    ex, ey = d.lerp(sx, x0 + 20, k), d.lerp(sy, 450, k)
    c.drawLine(sx, sy, ex, ey, d.stroke(GOLD, 3, 0.9))
    d.glow(c, x0 + 500 * 0.88, 450, 150, GOLD, 0.55 * d.pulse(t, cue["link"], 0.6))


# ---------------------------------------------------------------- 镜头 11–15

def shot11(c, t, D, cue, view):
    k = d.ease_in(d.prog(t, cue["pull"] - 0.6, 0.6))
    office(c, t, view, flag=0.8, bar_end=0.4, pose=d.blend(d.SIT_EASE, d.REACH, 1 - k),
           backdrop_fn=lambda: shelf(c, 40, 230, 520, n=3, lit=1, lit_k=1.0 - k))
    x, y = d.lerp(135, 610, k), d.lerp(470, 560, k)
    c.drawRect(skia.Rect.MakeLTRB(x - 30, y - 45, x + 30, y + 45), d.fill("#F5E7C4"))
    c.drawRect(skia.Rect.MakeLTRB(x - 30, y - 45, x + 30, y + 45), d.stroke(GOLD, 2))
    d.glow(c, 610, 560, 110, GOLD, 0.5 * d.pulse(t, cue["pull"], 0.6))


def shot12(c, t, D, cue, view):
    office(c, t, view, flag=0.8, bar_end=0.5, pose=d.SIT_EASE)
    if t >= cue["buffer"] - 1e-6:
        bar(c, _sx(0.5) + 8, _sx(0.72), BAR_Y, dashed=True, a=1.0)
    d.glow(c, _sx(0.62), BAR_Y, 140, GOLD, 0.55 * d.pulse(t, cue["buffer"], 0.6))


def shot13(c, t, D, cue, view):
    pendant_talk(c, t, cue["lamp"], view, floor=FLOOR)


def shot14(c, t, D, cue, view):
    k = d.ease_in(d.prog(t, cue["settle"] - 0.6, 0.6))
    office(c, t, view, flag=0.82, card=d.lerp(0.4, 0.72, k), bar_end=0.6, bar_ghost=0.75,
           pose=d.blend(d.SIT, d.SIT_EASE, d.prog(t, cue["settle"], 1.0)), warm=0.6)
    d.glow(c, _sx(0.72), SY - 60, 140, GOLD, 0.55 * d.pulse(t, cue["settle"], 0.6))


def shot15(c, t, D, cue, view):
    office(c, 6.0, view, flag=0.82, card=0.72, bar_end=0.6, bar_ghost=0.75, pose=d.SIT_EASE, warm=0.6)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
