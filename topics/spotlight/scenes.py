"""《会上说错一句话，为什么觉得全场都记住了》15 个镜头的场景绘制。

每个函数签名 (c, t, D, cue, view)：舞台 1000×1000 单位；撞击动作一律读 cue，保证贴拍后画面同步移动。
"""

import math

import numpy as np
import skia

from kepu import draw as d
from kepu.config import GOLD
from kepu.props import F, bust, desk, laptop, meeting_table, slide, slider, spotlight

FLOOR = 760
TABLE = (70, 650, 600)                  # 会议桌 x0, x1, 桌面 y
SEATS = (150, 290, 430, 570)            # 同事座位 x
SEAT_Y = 560
PRESENTER = (810, FLOOR)                # 主角站位（脚底）
BEAM_TOP = (810, 90)


def _stand_y(scale=1.0):
    return FLOOR - (d.SEG["th"] + d.SEG["sh"]) * scale


def meeting(c, t, view, look=1.0, lit=0.0, beam_k=1.0, beam_w=280, pose=d.HOLD, cards=0.0, card_dash=False,
            own_beams=0.0, ambient=0.0, paper=True):
    """会议室构图：左侧四位同事坐在桌后，右侧主角站着、头顶一束聚光灯。

    look 为同事头部朝向（+1 看主角、0 看自己的电脑），lit 为同事被照亮程度，cards 为同事头顶回放卡的显现程度，
    own_beams 为每位同事头顶各自那束光的亮度，ambient 为普通室内光（0–1）。
    """
    l, t_, r, b = view
    d.room(c, view, floor_y=FLOOR, warm=(500, 380, 0.25 + 0.75 * ambient))
    if ambient > 0:
        c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#C9A86A", 0.05 * ambient))
    for x in SEATS:
        spotlight(c, x, 90, x, SEAT_Y - 30, 150, k=own_beams * 0.8)
    for i, x in enumerate(SEATS):
        bust(c, x, SEAT_Y, look=look, lit=max(lit, own_beams * 0.6), card=cards, card_dash=card_dash)
    meeting_table(c, *TABLE)
    for x in SEATS:
        laptop(c, x + 40, TABLE[2], glow_k=0.3 + 0.7 * own_beams)
    d.floor_shadow(c, PRESENTER[0], FLOOR + 6, 170, 0.5)
    j = d.figure(c, PRESENTER[0], _stand_y(), pose, facing=-1, rim=0.5 + 0.5 * beam_k)
    if paper:
        hx = (j["hand_f"][0] + j["hand_b"][0]) / 2 - 24
        hy = (j["hand_f"][1] + j["hand_b"][1]) / 2 - 26
        d.mark_card(c, hx, hy, w=92, h=64, rot=8, lift=0.4)
    spotlight(c, *BEAM_TOP, PRESENTER[0], FLOOR, beam_w, k=beam_k)
    return j


# ---------------------------------------------------------------- 镜头 01–05：会议现场

def shot01(c, t, D, cue, view):
    w = 280 + 60 * d.ease_out(d.prog(t, cue["light"] - F, 0.3))
    k = 0.85 + 0.15 * d.prog(t, cue["light"] - F, F)
    meeting(c, t, view, look=1.0, lit=0.15, beam_k=k, beam_w=w, pose=d.blend(d.HOLD, d.SLUMP, t / D))
    d.glow(c, PRESENTER[0], 520, 260, "#FFF1D2", 0.45 * d.pulse(t, cue["light"], 0.6))


def shot02(c, t, D, cue, view):
    desk(c, view)
    g = d.ease_out(d.prog(t, 0, 0.5))
    c.save()
    c.translate(500, 480)
    c.scale(0.5 + 0.5 * g, 0.5 + 0.5 * g)
    pos = slide(c, 0, 0, 640, 380, mark_k=d.prog(t, cue["mark"] - F, 0.3))
    d.glow(c, pos[0], pos[1], 140, GOLD, 0.4 * d.pulse(t, cue["mark"], 0.6))
    c.restore()


def shot03(c, t, D, cue, view):
    k = d.ease_in(d.prog(t, cue["flare"] - 0.6, 0.6))
    after = t >= cue["flare"] - 1e-6
    c.save()
    z = 1 + 0.05 * t / D
    c.translate(500, 560)
    c.scale(z, z)
    c.translate(-500, -560)
    meeting(c, t, view, look=1.0, lit=1.0 if after else 0.15, beam_k=1.0, beam_w=340 + 1300 * k, pose=d.SLUMP)
    c.restore()
    d.glow(c, 500, 480, 520, "#FFF1D2", 0.35 * d.pulse(t, cue["flare"], 0.7))


def _film_strip(c, x, y, a):
    """主角头顶的一串回放画面。"""
    for i in range(4):
        d.mark_card(c, x - 150 + i * 100, y, w=84, h=56, lift=0.3, a=a)
    c.drawLine(x - 200, y - 38, x + 200, y - 38, d.stroke(GOLD, 1.5, 0.5 * a))
    c.drawLine(x - 200, y + 38, x + 200, y + 38, d.stroke(GOLD, 1.5, 0.5 * a))


def shot04(c, t, D, cue, view):
    cards = d.ease_in(d.prog(t, cue["replay"] - 0.25, 0.25))
    meeting(c, t, view, look=1.0, lit=0.3, beam_k=1.0, beam_w=420, pose=d.SLUMP, cards=cards)
    _film_strip(c, 650, 250, d.ease_out(d.prog(t, 0.2, 0.6)))
    for x in SEATS:
        d.glow(c, x, SEAT_Y - 160, 90, GOLD, 0.35 * d.pulse(t, cue["replay"], 0.5))


def shot05(c, t, D, cue, view):
    dash = t >= cue["halt"]
    dim = d.ease_io(d.prog(t, cue["halt"], 1.2))
    meeting(c, t, view, look=1.0 - 0.6 * dim, lit=0.3 * (1 - dim), beam_k=1.0 - 0.25 * dim, beam_w=420,
            pose=d.SLUMP, cards=1.0, card_dash=dash)
    _film_strip(c, 650, 250, 1.0 - 0.5 * dim)


# ---------------------------------------------------------------- 镜头 06–09：研究与机制

ROOM6 = (480, 230, 940, 760)
SEATED6 = [(560 + 130 * i, 420 + 190 * r) for r in range(2) for i in range(3)]


def _emblem(c, j, k=1.0):
    """示意角色上衣的金色图案（显眼 T 恤）。"""
    mx = (j["hip"][0] + j["sh"][0]) / 2
    my = (j["hip"][1] + j["sh"][1]) / 2
    c.drawCircle(mx, my, 20 * k, d.fill(GOLD))
    c.drawCircle(mx, my, 11 * k, d.fill("#8A6E3A"))


def shot06(c, t, D, cue, view):
    d.backdrop(c, view)
    x0, y0, x1, y1 = ROOM6
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), d.fill("#111216"))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), d.stroke(GOLD, 2, 0.5))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 6, y1 - 250, x0 + 6, y1), d.fill(BG_DOOR))
    for x, y in SEATED6:
        bust(c, x, y, look=0.0, lit=0.25 * d.pulse(t, cue["enter"], 1.0), scale=0.7)
    c.drawLine(x0 - 400, FLOOR, x1, FLOOR, d.stroke(GOLD, 1.2, 0.2))
    walk = d.prog(t, 0.3, cue["enter"] - 0.3)
    x = d.lerp(130, 410, walk)
    pose = d.walk((t - 0.3) * 2 * math.pi / 0.8) if walk < 1 else d.STAND
    d.floor_shadow(c, x, FLOOR + 4, 120, 0.5)
    j = d.figure(c, x, _stand_y(0.8), pose, facing=1, scale=0.8)
    _emblem(c, j, 0.9)
    d.glow(c, (j["hip"][0] + j["sh"][0]) / 2, (j["hip"][1] + j["sh"][1]) / 2, 120, GOLD,
           0.6 * d.pulse(t, cue["enter"], 0.6))


BG_DOOR = "#2A2824"
GRID7 = [(i % 3 - 1, i // 3 - 1) for i in range(9)]
LIT_GUESS = {0, 1, 2, 3, 5, 6, 8}
LIT_ACTUAL = {1, 4, 6}


def _panel(c, cx, cy, dashed, lit_set, k):
    """研究示意面板：虚线框 = 穿的人的估计，实线框 = 实际记得的人；顶部小人穿着带图案的上衣。"""
    if dashed:
        c.drawRRect(d.rrect(cx, cy, 400, 520, 18), d.stroke(GOLD, 2.5, 0.8, dash=((16, 10), 0)))
    else:
        c.drawRRect(d.rrect(cx, cy, 400, 520, 18), d.stroke(GOLD, 2.5, 0.8))
    j = d.figure(c, cx, cy - 120, d.STAND, facing=1, scale=0.36, rim=0.6)
    _emblem(c, j, 0.45)
    for i, (gx, gy) in enumerate(GRID7):
        on = k if i in lit_set else 0.0
        bust(c, cx + gx * 110, cy + 90 + gy * 95, look=0.0, lit=on, scale=0.42)
        if on > 0:
            d.glow(c, cx + gx * 110, cy + 60 + gy * 95, 50, GOLD, 0.45 * on)


def shot07(c, t, D, cue, view):
    d.backdrop(c, view)
    g = t >= cue["guess"] - 1e-6
    a = t >= cue["actual"] - 1e-6
    _panel(c, 265, 520, True, LIT_GUESS, 1.0 if g else 0.0)
    _panel(c, 735, 520, False, LIT_ACTUAL, 1.0 if a else 0.0)
    d.glow(c, 265, 560, 260, GOLD, 0.35 * d.pulse(t, cue["guess"], 0.5))
    d.glow(c, 735, 560, 260, GOLD, 0.35 * d.pulse(t, cue["actual"], 0.5))


def shot08(c, t, D, cue, view):
    d.backdrop(c, view)
    on = t >= cue["name"] - 1e-6
    d.floor_shadow(c, 500, FLOOR + 6, 200, 0.5)
    d.figure(c, 500, _stand_y(), d.SLUMP if on else d.STAND, facing=1, rim=1.0 if on else 0.3)
    if on:
        w = 300 + 120 * (1 - d.ease_out(d.prog(t, cue["name"], 0.4)))
        spotlight(c, 500, 80, 500, FLOOR, w, k=1.0)
        d.sparks(c, 500, FLOOR, t, cue["name"], n=20, r=260, seed=4)
    d.glow(c, 500, 520, 380, "#FFF1D2", 0.45 * d.pulse(t, cue["name"], 0.6))


def shot09(c, t, D, cue, view):
    d.backdrop(c, view)
    x0, x1, y = 250, 730, 560
    # 左端：被自己的光照着的人；右端：三位他人
    spotlight(c, 150, 300, 150, 700, 150, k=0.9)
    d.figure(c, 150, 700 - (d.SEG["th"] + d.SEG["sh"]) * 0.55, d.STAND, facing=1, scale=0.55, rim=0.9)
    for i, (bx, by) in enumerate(((810, 520), (900, 600), (810, 680))):
        bust(c, bx, by, look=-1.0, scale=0.55)
    stop = 0.55
    k = stop * d.ease_in(d.prog(t, cue["slide"], cue["stop"] - cue["slide"]))
    slider(c, x0, x1, y, k, stop=stop, stop_k=d.prog(t, cue["stop"] - F, F))
    d.glow(c, x0 + (x1 - x0) * stop, y, 120, GOLD, 0.45 * d.pulse(t, cue["stop"], 0.5))


# ---------------------------------------------------------------- 镜头 10–15：拉开、反思、收束

def shot10(c, t, D, cue, view):
    z = d.lerp(1.7, 1.0, d.ease_in(d.prog(t, 0, cue["reveal"])))
    on = t >= cue["reveal"] - 1e-6
    c.save()
    c.translate(PRESENTER[0], 520)
    c.scale(z, z)
    c.translate(-PRESENTER[0], -520)
    meeting(c, t, view, look=0.0, lit=0.1, beam_k=0.9, beam_w=300, pose=d.SLUMP, own_beams=1.0 if on else 0.0)
    c.restore()
    for x in SEATS:
        d.glow(c, x, SEAT_Y - 60, 120, "#FFF1D2", 0.35 * d.pulse(t, cue["reveal"], 0.6))


def shot11(c, t, D, cue, view):
    after = t >= cue["ask"] - 1e-6
    fall = d.ease_out(d.prog(t, cue["ask"], 0.5))
    meeting(c, t, view, look=0.0, lit=0.1, beam_k=0.7, beam_w=300, pose=d.HOLD, own_beams=0.6,
            cards=0.25 if after else 1.0)
    if after and fall < 1:
        for x in SEATS:
            d.mark_card(c, x, SEAT_Y - 150 + 220 * fall, w=74, h=50, lift=0.3, a=0.7 * (1 - fall))
    d.glow(c, 360, SEAT_Y - 150, 300, GOLD, 0.25 * d.pulse(t, cue["ask"], 0.5))


def shot12(c, t, D, cue, view):
    desk(c, view)
    pos = slide(c, 500, 480, 640, 380, mark_k=1.0 - d.prog(t, cue["fix"], 0.3),
                fix_k=d.ease_out(d.prog(t, cue["fix"] - F, 0.3)))
    d.glow(c, pos[0], pos[1], 150, GOLD, 0.45 * d.pulse(t, cue["fix"], 0.6))


def shot13(c, t, D, cue, view):
    on = t >= cue["lamp"] - 1e-6
    d.room(c, view, floor_y=FLOOR, warm=(500, 420, 1.0 if on else 0.15))
    c.drawLine(500, view[1], 500, 300, d.stroke("#3A3833", 3))
    shade = skia.Path()
    shade.moveTo(470, 300)
    shade.lineTo(530, 300)
    shade.lineTo(560, 345)
    shade.lineTo(440, 345)
    shade.close()
    c.drawPath(shade, d.fill(d.mix("#3A352C", "#E8D2A0", 1.0 if on else 0.1)))
    if on:
        g = skia.GradientShader.MakeLinear([(500, 345), (500, FLOOR)], [d.col("#F2D59A", 0.30), d.col("#F2D59A", 0.0)])
        cone = skia.Path()
        cone.moveTo(440, 345)
        cone.lineTo(560, 345)
        cone.lineTo(760, FLOOR)
        cone.lineTo(240, FLOOR)
        cone.close()
        c.drawPath(cone, skia.Paint(Shader=g, AntiAlias=True))
    # 小圆桌与两把椅子
    c.drawRect(skia.Rect.MakeLTRB(410, 620, 590, 634), d.fill("#2A2824"))
    c.drawLine(410, 620, 590, 620, d.stroke(GOLD, 1.5, 0.5))
    c.drawRect(skia.Rect.MakeLTRB(494, 634, 506, FLOOR), d.fill("#1D1C19"))
    for x, f in ((300, 1), (700, -1)):
        c.drawRect(skia.Rect.MakeLTRB(x - 50, 650, x + 50, 662), d.fill("#1D1C19"))
        c.drawRect(skia.Rect.MakeLTRB(x - 50 * f - 6, 520, x - 50 * f + 6, FLOOR), d.fill("#1D1C19"))
        d.figure(c, x, 648, d.SIT_EASE, facing=f, scale=0.9, rim=1.0 if on else 0.4)
    for x in (470, 530):
        c.drawRRect(d.rrect(x, 606, 22, 26, 4), d.fill("#E8DCC6"))
    d.glow(c, 500, 330, 120, "#FFF1D2", (0.6 if on else 0.0) + 0.4 * d.pulse(t, cue["lamp"], 0.6))
    rng = np.random.default_rng(13)
    for _ in range(14):
        x = 380 + rng.uniform(0, 240)
        y = 360 + ((rng.uniform(0, 260) - t * rng.uniform(6, 14)) % 260)
        c.drawCircle(x, y, rng.uniform(1.2, 2.2), d.fill("#F6E2B5", (0.35 if on else 0.0) * rng.uniform(0.4, 1)))


def shot14(c, t, D, cue, view):
    after = t >= cue["settle"] - 1e-6
    calm = d.ease_out(d.prog(t, cue["settle"], 1.2))
    meeting(c, t, view, look=0.0, lit=0.0, beam_k=0.0 if after else 1.0, beam_w=300,
            pose=d.blend(d.SLUMP, d.STAND, calm), ambient=1.0 if after else 0.0)
    d.glow(c, PRESENTER[0], 520, 260, "#FFF1D2", 0.4 * d.pulse(t, cue["settle"], 0.5))


def shot15(c, t, D, cue, view):
    meeting(c, 6.0, view, look=0.0, beam_k=0.0, pose=d.STAND, ambient=1.0)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
