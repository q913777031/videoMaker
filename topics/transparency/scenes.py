"""《紧张的时候，别人真能一眼看穿吗》15 个镜头的场景绘制（舞台 1000×1000 单位，撞击时刻一律读 cue）。"""

import math

import skia

from kepu import draw as d
from kepu.config import GOLD
from kepu.props import bust, heart, pendant_talk, review_merge, slide

FLOOR = 760
ME = (300, 640)                  # 面试者坐姿髋部
TABLE = (380, 700, 600)          # 桌子 x0, x1, 桌面 y
INTERVIEWER = (800, 560)


def glass_person(c, x, y, pose, facing=1, scale=1.0, glass=0.0, heart_k=0.5, storm=0.0, t=0.0, beat=0.0):
    """人物 + 胸口心形；glass 0–1 让身体变成半透明玻璃并露出内部翻涌（storm）。返回关节点。"""
    j = d.figure_joints(x, y, pose, facing, scale)
    c.saveLayerAlpha(None, int(255 * (1 - 0.72 * glass)))
    d.figure(c, x, y, pose, facing=facing, scale=scale, rim=0.5 + 0.5 * glass)
    c.restore()
    cx = j["hip"][0] + (j["sh"][0] - j["hip"][0]) * 0.65
    cy = j["hip"][1] + (j["sh"][1] - j["hip"][1]) * 0.65
    if glass > 0:
        # 玻璃轮廓与内部翻涌的波纹
        torso = skia.Path()
        torso.moveTo(*j["hip"])
        torso.lineTo(*j["sh"])
        c.drawPath(torso, d.stroke("#CFE0F0", 60 * scale, 0.08 * glass))
        c.drawCircle(*j["head"], 31 * scale, d.stroke("#CFE0F0", 2, 0.6 * glass))
        for k in range(3):
            p = skia.Path()
            yy = cy + (k - 1) * 26 * scale
            p.moveTo(cx - 24 * scale, yy)
            for i in range(6):
                p.quadTo(cx - 20 * scale + i * 8 * scale, yy + (10 if i % 2 else -10) * storm * scale * math.sin(t * 6 + k),
                         cx - 16 * scale + i * 8 * scale, yy)
            c.drawPath(p, d.stroke("#E8C987", 2.5, 0.8 * glass * storm))
    s = scale * (0.55 + 0.25 * beat)
    if heart_k > 0:
        heart(c, cx, cy, s=s, k=heart_k * (0.4 + 0.6 * glass))
    return j, (cx, cy)


Z = 1.35                         # 面试构图整体放大（围绕桌边中点）
ZC = (520, 640)


def _zp(p):
    return ZC[0] + (p[0] - ZC[0]) * Z, ZC[1] + (p[1] - ZC[1]) * Z


def interview(c, t, view, glass=0.0, heart_k=0.5, storm=0.0, beat=0.0, look=0.0, pose=None, lit=0.0):
    """面试构图：左侧面试者坐着，右侧面试官隔桌而坐（整体放大 Z 倍）。返回 (关节点, 心形位置)，均为放大后坐标。"""
    d.room(c, view, floor_y=FLOOR, warm=(500, 380, 0.4))
    c.save()
    c.translate(*ZC)
    c.scale(Z, Z)
    c.translate(-ZC[0], -ZC[1])
    bust(c, *INTERVIEWER, look=look, lit=lit)
    c.drawRect(skia.Rect.MakeLTRB(TABLE[0], TABLE[2], TABLE[1], TABLE[2] + 14), d.fill("#2A2824"))
    c.drawLine(TABLE[0], TABLE[2], TABLE[1], TABLE[2], d.stroke(GOLD, 1.5, 0.5))
    c.drawRect(skia.Rect.MakeLTRB(TABLE[0] + 20, TABLE[2] + 14, TABLE[0] + 32, FLOOR), d.fill("#1D1C19"))
    c.drawRect(skia.Rect.MakeLTRB(TABLE[1] - 32, TABLE[2] + 14, TABLE[1] - 20, FLOOR), d.fill("#1D1C19"))
    c.drawRect(skia.Rect.MakeLTRB(ME[0] - 60, ME[1] + 10, ME[0] + 60, ME[1] + 22), d.fill("#1D1C19"))
    c.drawRect(skia.Rect.MakeLTRB(ME[0] - 66, 520, ME[0] - 54, FLOOR), d.fill("#1D1C19"))
    j, hp = glass_person(c, *ME, pose or d.SIT, 1, 1.0, glass, heart_k, storm, t, beat)
    c.restore()
    jz = {k: (_zp(v) if isinstance(v, tuple) else v) for k, v in j.items()}
    return jz, _zp(hp)


# ---------------------------------------------------------------- 镜头 01–05

def shot01(c, t, D, cue, view):
    beat = d.pulse(t, cue["beat"], 0.4) + 0.3 * d.pulse((t - cue["beat"]) % 0.6, 0.0, 0.3) * (t > cue["beat"])
    j, hp = interview(c, t, view, glass=0.35, heart_k=0.8, storm=0.3, beat=beat)
    d.glow(c, *hp, 160, "#E8C987", 0.6 * d.pulse(t, cue["beat"], 0.5))


def _voice(c, x, y, jag, a=1.0):
    for i, r in enumerate((40, 70, 100)):
        p = skia.Path()
        for k in range(13):
            ang = -0.6 + 1.2 * k / 12
            rr = r + (6 if k % 2 else -6) * jag
            pt = (x + rr * math.cos(ang), y + rr * math.sin(ang))
            (p.moveTo if k == 0 else p.lineTo)(*pt)
        c.drawPath(p, d.stroke(GOLD, 3, a * (1 - i * 0.25)))


def shot02(c, t, D, cue, view):
    on = t >= cue["tremble"] - 1e-6
    j, hp = interview(c, t, view, glass=0.35, heart_k=0.8, storm=0.5)
    hx, hy = j["head"]
    _voice(c, hx + 40, hy + 10, 1.0 if on else 0.0, a=d.ease_out(d.prog(t, 0.3, 0.5)))
    for hand in (j["hand_f"], j["hand_b"]):
        if on:
            for k in range(3):
                c.drawLine(hand[0] - 14 + k * 14, hand[1] + 16, hand[0] - 10 + k * 14, hand[1] + 26,
                           d.stroke("#CFE0F0", 2.5, 0.8))
    d.glow(c, hx + 80, hy + 10, 130, GOLD, 0.55 * d.pulse(t, cue["tremble"], 0.5))


def shot03(c, t, D, cue, view):
    on = t >= cue["glass"] - 1e-6
    j, hp = interview(c, t, view, glass=1.0 if on else 0.35, heart_k=1.0, storm=1.0 if on else 0.4)
    d.glow(c, *hp, 220, "#CFE0F0", 0.55 * d.pulse(t, cue["glass"], 0.6))


def _rings(c, x, y, k, a=1.0):
    for i in range(3):
        r = 60 + (560 * k - i * 120)
        if r > 40:
            c.drawCircle(x, y, r, d.stroke("#E8C987", 3, a * max(0.0, 1 - r / 700)))


def shot04(c, t, D, cue, view):
    hit = t >= cue["reach"] - 1e-6
    j, hp = interview(c, t, view, glass=1.0, heart_k=1.0, storm=1.0, lit=1.0 if hit else 0.0)
    k = d.ease_in(d.prog(t, cue["reach"] - 0.9, 0.9))
    _rings(c, *hp, k if not hit else 1.0 + 0.4 * d.prog(t, cue["reach"], 1.5))
    d.glow(c, *_zp((INTERVIEWER[0], INTERVIEWER[1] - 60)), 180, GOLD, 0.6 * d.pulse(t, cue["reach"], 0.5))


def shot05(c, t, D, cue, view):
    k = d.ease_io(d.prog(t, cue["halt"], 1.2))
    interview(c, t, view, glass=1.0 - 0.3 * k, heart_k=1.0 - 0.3 * k, storm=1.0 - 0.5 * k)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.25 * k))


# ---------------------------------------------------------------- 镜头 06–10

def shot06(c, t, D, cue, view):
    review_merge(c, t, cue["merge"], view)


def _panel(c, cx, cy, dashed, glass, heart_k, on):
    r = d.rrect(cx, cy, 380, 540, 18)
    c.drawRRect(r, d.stroke(GOLD, 2.5, 0.8, dash=((16, 10), 0) if dashed else None))
    if on:
        glass_person(c, cx, cy + 40, d.STAND, 1, 0.8, glass, heart_k, 0.8 if dashed else 0.0, 0.0, 0.3)
    else:
        glass_person(c, cx, cy + 40, d.STAND, 1, 0.8, 0.0, 0.15, 0.0)


def shot07(c, t, D, cue, view):
    d.backdrop(c, view)
    _panel(c, 265, 500, True, 1.0, 1.0, t >= cue["self"] - 1e-6)
    _panel(c, 735, 500, False, 0.0, 0.3, t >= cue["other"] - 1e-6)
    d.glow(c, 265, 420, 200, GOLD, 0.5 * d.pulse(t, cue["self"], 0.5))
    d.glow(c, 735, 420, 200, GOLD, 0.5 * d.pulse(t, cue["other"], 0.5))


def shot08(c, t, D, cue, view):
    d.backdrop(c, view)
    glass_person(c, 500, FLOOR - (d.SEG["th"] + d.SEG["sh"]), d.STAND, 1, 1.0, 1.0, 1.0, 1.0, t, 0.3)
    on = t >= cue["name"] - 1e-6
    y = 0 if on else d.lerp(-500, 0, d.ease_in(d.prog(t, cue["name"] - 0.5, 0.5)))
    c.drawRRect(d.rrect(500, 470 + y, 360, 640, 20), d.stroke(GOLD, 4))
    d.glow(c, 500, 470, 320, GOLD, 0.5 * d.pulse(t, cue["name"], 0.6))


def _inner(c, x, y, r, t):
    """内心视角：明亮的心形与翻涌的波纹。"""
    c.drawCircle(x, y, r, d.fill("#1A1814"))
    for k in range(5):
        p = skia.Path()
        yy = y - r * 0.6 + k * r * 0.3
        p.moveTo(x - r, yy)
        for i in range(10):
            p.quadTo(x - r + (i + 0.5) * r * 0.2, yy + (24 if i % 2 else -24) * math.sin(t * 5 + k + i),
                     x - r + (i + 1) * r * 0.2, yy)
        c.drawPath(p, d.stroke("#E8C987", 3, 0.7))
    heart(c, x, y, s=2.6, k=1.0)


def _outer(c, x, y, r):
    """外人视角：平静的表面，只透出很淡的一点光。"""
    c.drawCircle(x, y, r, d.fill("#22252B"))
    g = skia.GradientShader.MakeRadial(skia.Point(x - r * 0.3, y - r * 0.3), r * 1.2,
                                       [d.col("#FFFFFF", 0.10), d.col("#FFFFFF", 0.0)])
    c.drawCircle(x, y, r, skia.Paint(Shader=g, AntiAlias=True))
    heart(c, x, y, s=1.0, k=0.12)


def shot09(c, t, D, cue, view):
    d.backdrop(c, view)
    x, y, r = 500, 500, 280
    k = d.ease_in(d.prog(t, cue["wipe"], cue["stop"] - cue["wipe"]))
    split = d.lerp(x + r, x, k)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(-2000, -2000, split, 3000))
    _inner(c, x, y, r, t)
    c.restore()
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(split, -2000, 3000, 3000))
    _outer(c, x, y, r)
    c.restore()
    c.drawCircle(x, y, r, d.stroke(GOLD, 2.5, 0.8))
    c.drawLine(split, y - r - 40, split, y + r + 40, d.stroke(GOLD, 3))
    d.glow(c, split, y, 180, GOLD, 0.55 * d.pulse(t, cue["stop"], 0.5))


def shot10(c, t, D, cue, view):
    on = t >= cue["pov"] - 1e-6
    z = d.lerp(1.0, 1.15, d.ease_in(d.prog(t, 0, cue["pov"])))
    c.save()
    c.translate(ME[0], 560)
    c.scale(z, z)
    c.translate(-ME[0], -560)
    interview(c, t, view, glass=0.0 if on else 1.0, heart_k=0.2 if on else 1.0, storm=1.0)
    c.restore()
    d.glow(c, *_zp((ME[0], 470)), 260, "#FFF1D2", 0.5 * d.pulse(t, cue["pov"], 0.6))


def shot11(c, t, D, cue, view):
    j, hp = interview(c, t, view, glass=0.0, heart_k=0.2)
    on = t >= cue["frame"] - 1e-6
    if on:
        hx, hy = j["head"]
        c.drawRRect(d.rrect(hx + 10, hy + 70, 200, 260, 16), d.stroke(GOLD, 3.5))
    d.glow(c, j["head"][0] + 10, j["head"][1] + 70, 180, GOLD, 0.55 * d.pulse(t, cue["frame"], 0.5))


def shot12(c, t, D, cue, view):
    on = t >= cue["focus"] - 1e-6
    calm = d.ease_out(d.prog(t, cue["focus"], 1.5))
    interview(c, t, view, glass=0.0, heart_k=0.6 - 0.4 * calm, pose=d.blend(d.SIT, d.SIT_EASE, calm))
    sx, sy = _zp((545, 560))
    slide(c, sx, sy, 200, 116, mark_k=1.0 if on else 0.0, row=0, col=0)
    d.glow(c, sx, sy, 150, GOLD, 0.55 * d.pulse(t, cue["focus"], 0.5) + (0.2 if on else 0.0))


def shot13(c, t, D, cue, view):
    pendant_talk(c, t, cue["lamp"], view, floor=FLOOR)


def shot14(c, t, D, cue, view):
    after = t >= cue["settle"] - 1e-6
    calm = d.ease_out(d.prog(t, cue["settle"], 1.0))
    j, hp = interview(c, t, view, glass=0.0 if after else 0.6, heart_k=0.25 if after else 0.9, storm=0.4,
                      pose=d.blend(d.SIT, d.SIT_EASE, calm))
    d.glow(c, *hp, 160, GOLD, 0.5 * d.pulse(t, cue["settle"], 0.5))


def shot15(c, t, D, cue, view):
    interview(c, 6.0, view, glass=0.0, heart_k=0.25, pose=d.SIT_EASE)
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
