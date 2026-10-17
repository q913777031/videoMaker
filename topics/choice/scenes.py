"""《外卖翻了半小时，为什么还是点不下去》15 个镜头的场景绘制（舞台 1000×1000 单位，撞击时刻一律读 cue）。"""

import math

import numpy as np
import skia

from kepu import draw as d
from kepu.config import GOLD
from kepu.props import balance, funnel, jar, menu_card, pendant_talk, review_merge, scatter

FLOOR = 760
ME = (280, 640)
PHONE = (630, 470, 340, 540)        # 手机中心 x、y、宽、高


def phone(c, n=8, scroll=0.0, lit=(), lines=0.0, dim=0.0, frame4=0.0, a=1.0):
    """放大的手机屏幕：两列店铺卡片（n 张），scroll 为滚动位置；lit 为高亮卡片序号；lines 为比较连线程度。"""
    x, y, w, h = PHONE
    c.drawRRect(d.rrect(x, y, w + 24, h + 24, 40), d.fill("#141519", a))
    c.drawRRect(d.rrect(x, y, w + 24, h + 24, 40), d.stroke(GOLD, 2.5, 0.7 * a))
    body = d.rrect(x, y, w, h, 30)
    c.save()
    c.clipRRect(body, doAntiAlias=True)
    c.drawRRect(body, d.fill("#1C1D22", a))
    pos = []
    cols = 2 if n <= 12 else 3
    cw = (w - 40) / cols
    ch = cw * 0.72
    for i in range(n):
        cx = x - w / 2 + 20 + cw * (i % cols + 0.5)
        cy = y - h / 2 + 30 + ch * 0.6 + (i // cols) * (ch + 12) - scroll * h
        top = y - h / 2 - ch
        cy = top + ((cy - top) % (h + ch * 2))
        pos.append((cx, cy))
        menu_card(c, cx, cy, w=cw - 14, h=ch, seed=i, a=a, lit=1.0 if i in lit else 0.0)
    if lines > 0 and n > 1:
        for i in range(n):
            for j in range(i + 1, n):
                if (i * 7 + j * 3) % 4 == 0:
                    c.drawLine(*pos[i], *pos[j], d.stroke(GOLD, 1.5, 0.5 * lines))
    if dim > 0:
        c.drawRRect(body, d.fill("#000000", 0.55 * dim))
    if frame4 > 0:
        c.drawRRect(d.rrect(x, y - h / 2 + 30 + ch * 0.6 + (ch + 12) / 2, w - 20, ch * 2 + 40, 14), d.stroke(GOLD, 4, frame4))
    c.restore()
    return pos


def couch(c, t, view, n=8, scroll=0.0, lit=(), lines=0.0, dim=0.0, pose=None, frame4=0.0, warm=0.3):
    """沙发构图：左侧人物坐着握手机，右侧是放大的手机屏幕。"""
    d.room(c, view, floor_y=FLOOR, warm=(PHONE[0], 380, warm))
    c.drawRRect(d.rrect(ME[0], ME[1] + 30, 260, 70, 20), d.fill("#24252A"))
    c.drawRRect(d.rrect(ME[0] - 120, ME[1] - 20, 40, 150, 14), d.fill("#24252A"))
    j = d.figure(c, *ME, pose or d.SIT, facing=1)
    hx, hy = j["hand_f"]
    c.drawRRect(d.rrect(hx + 10, hy - 20, 26, 44, 6), d.fill("#2A2C33"))
    c.drawLine(hx + 24, hy - 20, PHONE[0] - PHONE[2] / 2, PHONE[1] - 100, d.stroke(GOLD, 1.2, 0.25))
    return phone(c, n=n, scroll=scroll, lit=lit, lines=lines, dim=dim, frame4=frame4)


# ---------------------------------------------------------------- 镜头 01–05

def shot01(c, t, D, cue, view):
    on = t >= cue["stuck"] - 1e-6
    couch(c, t, view, n=12 if on else 8, scroll=0.35 * t / D)
    d.glow(c, PHONE[0], PHONE[1], 260, GOLD, 0.5 * d.pulse(t, cue["stuck"], 0.5))


def shot02(c, t, D, cue, view):
    on = t >= cue["compare"] - 1e-6
    couch(c, t, view, n=12, scroll=0.35 + 0.05 * t / D, dim=0.5 if on else 0.0)
    if on:
        k = d.ease_out(d.prog(t, cue["compare"], 0.3))
        for i, side in enumerate((-1, 1)):
            menu_card(c, PHONE[0] + side * 110 * k, PHONE[1], w=200, h=150, seed=i + 2, lit=1.0)
    d.glow(c, PHONE[0], PHONE[1], 220, GOLD, 0.5 * d.pulse(t, cue["compare"], 0.5))


def shot03(c, t, D, cue, view):
    on = t >= cue["fear"] - 1e-6
    couch(c, t, view, n=24 if on else 12, scroll=0.4 + 0.05 * t / D, pose=d.SIT if not on else d.SLUMP)
    d.glow(c, PHONE[0], PHONE[1], 300, "#E8C987", 0.5 * d.pulse(t, cue["fear"], 0.5))


def shot04(c, t, D, cue, view):
    on = t >= cue["lines"] - 1e-6
    couch(c, t, view, n=24, scroll=0.45, lines=1.0 if on else 0.0, pose=d.SLUMP)
    d.glow(c, PHONE[0], PHONE[1], 300, GOLD, 0.5 * d.pulse(t, cue["lines"], 0.5))


def shot05(c, t, D, cue, view):
    k = d.ease_io(d.prog(t, cue["halt"], 1.0))
    couch(c, t, view, n=24, scroll=0.45, lines=1.0 - 0.7 * k, dim=0.4 * k, pose=d.SLUMP)


# ---------------------------------------------------------------- 镜头 06–10

def shot06(c, t, D, cue, view):
    review_merge(c, t, cue["merge"], view)


def _jam(c, x, y, s=1.0, seed=0):
    colors = ("#8C2F39", "#C9A86A", "#6B3E5E", "#D9822B", "#5E7A3A")
    jar(c, x, y, 0.8, s=s)
    c.drawRRect(d.rrect(x, y + 10 * s, 90 * s, 110 * s, 18 * s), d.fill(colors[seed % len(colors)], 0.6))


def _bag(c, x, y, a=1.0):
    c.drawRRect(d.rrect(x, y, 70, 80, 8), d.fill("#F5E7C4", a))
    c.drawRRect(d.rrect(x, y, 70, 80, 8), d.stroke(GOLD, 2, a))
    p = skia.Path()
    p.addArc(skia.Rect.MakeLTRB(x - 20, y - 64, x + 20, y - 24), 180, 180)
    c.drawPath(p, d.stroke(GOLD, 3, a))


def _stall(c, x, n, bags, on, t, at):
    c.drawRect(skia.Rect.MakeLTRB(x - 190, 640, x + 190, 656), d.fill("#2A2824"))
    c.drawLine(x - 190, 640, x + 190, 640, d.stroke(GOLD, 1.5, 0.6))
    cols = 6 if n > 6 else 3
    s = 0.3 if n > 6 else 0.55
    span = 250 if n > 6 else 300
    for i in range(n):
        _jam(c, x - span / 2 + (i % cols) * (span / max(cols - 1, 1)),
             620 - (i // cols) * 70 * (s / 0.32), s=s, seed=i)
    if on:
        for b in range(bags):
            _bag(c, x - 70 * (bags - 1) / 2 + b * 70, 300)
    d.glow(c, x, 320, 160, GOLD, 0.5 * d.pulse(t, at, 0.5))


def shot07(c, t, D, cue, view):
    d.backdrop(c, view)
    _stall(c, 310, 24, 1, t >= cue["many"] - 1e-6, t, cue["many"])
    _stall(c, 720, 6, 3, t >= cue["few"] - 1e-6, t, cue["few"])


def _pile(c, x, y):
    for i in range(6):
        menu_card(c, x - 40 + (i % 3) * 40, y - (i // 3) * 30, w=90, h=60, seed=i)


def shot08(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["name"] - 1e-6
    tilt = 10.0 * d.ease_out(d.prog(t, cue["name"], 0.4)) if on else 0.0
    balance(c, 500, 330, tilt=-tilt, left=_pile if on else None,
            right=lambda c_, x, y: menu_card(c_, x, y, w=90, h=60, seed=1))
    if not on:
        k = d.ease_in(d.prog(t, cue["name"] - 0.5, 0.5))
        _pile(c, 280, d.lerp(-100, 430, k))
    d.glow(c, 280, 470, 200, GOLD, 0.55 * d.pulse(t, cue["name"], 0.5))


def shot09(c, t, D, cue, view):
    d.backdrop(c, view)
    k = d.ease_out(d.prog(t, cue["dots"], 0.8))
    n = int(round(24 * d.prog(t, cue["dots"], cue["zero"] - cue["dots"])))
    if n > 0:
        scatter(c, 200, 200 + 600 * n / 24, 520, n, k=k)
    on = t >= cue["zero"] - 1e-6
    if on:
        c.drawLine(180, 520, 820, 520, d.stroke("#FFF1D2", 6))
    d.glow(c, 500, 520, 300, GOLD, 0.55 * d.pulse(t, cue["zero"], 0.5))


def shot10(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["split"] - 1e-6
    scatter(c, 200, 800, 520, 24, k=1.0 + (0.9 if on else 0.0) * d.ease_out(d.prog(t, cue["split"], 0.4)))
    c.drawLine(180, 520, 820, 520, d.stroke("#FFF1D2", 4))
    d.glow(c, 500, 520, 320, GOLD, 0.5 * d.pulse(t, cue["split"], 0.5))


# ---------------------------------------------------------------- 镜头 11–15

def shot11(c, t, D, cue, view):
    d.backdrop(c, view)
    funnel(c, 500, 480, w=520, h=320)
    on = t >= cue["filter"] - 1e-6
    rng = np.random.default_rng(4)
    for i in range(14):
        x = 300 + rng.uniform(0, 400)
        k = d.ease_in(d.prog(t, cue["filter"] - 0.4, 0.4))
        y = 250 + 30 * math.sin(t * 2 + i) + 240 * k
        xx = d.lerp(x, 500, k)
        if not on:
            menu_card(c, xx, y, w=80 * (1 - 0.6 * k), h=56 * (1 - 0.6 * k), seed=i, a=0.9)
    if on:
        for i in range(3):
            menu_card(c, 420 + i * 80, 720, w=80, h=56, seed=i, lit=1.0)
    d.glow(c, 500, 700, 200, GOLD, 0.55 * d.pulse(t, cue["filter"], 0.5))


def shot12(c, t, D, cue, view):
    d.backdrop(c, view)
    for i in range(3):
        menu_card(c, 300 + i * 160, 330, w=130, h=90, seed=i, lit=1.0 if i == 1 else 0.0)
    _bag(c, 540, 680)
    drop = d.ease_in(d.prog(t, cue["pick"] - 3 / 30, 3 / 30))
    if t > 0.3:
        menu_card(c, d.lerp(460, 540, drop), d.lerp(330, 660, drop), w=100, h=70, seed=1, lit=1.0)
    d.glow(c, 540, 680, 180, GOLD, 0.55 * d.pulse(t, cue["pick"], 0.5))


def shot13(c, t, D, cue, view):
    pendant_talk(c, t, cue["lamp"], view, floor=FLOOR)


def shot14(c, t, D, cue, view):
    on = t >= cue["settle"] - 1e-6
    couch(c, t, view, n=4 if on else 24, scroll=0.0 if on else 0.45, frame4=1.0 if on else 0.0,
          pose=d.blend(d.SLUMP, d.SIT_EASE, d.ease_out(d.prog(t, cue["settle"], 1.0))), warm=0.6)
    d.glow(c, PHONE[0], PHONE[1] - 150, 220, GOLD, 0.55 * d.pulse(t, cue["settle"], 0.5))


def shot15(c, t, D, cue, view):
    shot14(c, 6.0, D, {"settle": 1.0}, view)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
