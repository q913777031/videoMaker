"""15 个镜头的场景绘制。每个函数签名 (c, t, D, cue, view)：

c 为已映射到舞台单位的画布；t 为镜头内时间；D 为镜头时长；cue 为本镜事件时刻表（键 → 镜头内秒），
撞击动作一律读 cue，保证音效校准后画面同步移动；view 为可见舞台范围 (l, t, r, b)。
"""

import math

F = 1 / 30           # 一帧：撞击动作从事件帧起即可见

import numpy as np
import skia

from . import draw as d
from .config import GOLD, WHITE


# ---------------------------------------------------------------- 共用构图

BED_TOP = 640
LAMP_X = 800
HIP = (400, 628)


def _card_in_hands(j):
    hx = (j["hand_f"][0] + j["hand_b"][0]) / 2 + 26
    hy = (j["hand_f"][1] + j["hand_b"][1]) / 2 - 30
    return hx, hy


def bedroom(c, t, view, shadow_scale, city, card_rot=-8.0, pose=d.SIT, city_alpha=1.0, lamp_on=1.0):
    """床边构图：人物坐床沿、手持修改卡，台灯在右；卡片在墙上投出阴影（city=1 为城市剪影，0 为卡片真实形状）。"""
    d.room(c, view, floor_y=760, warm=(LAMP_X, 420, lamp_on))
    j = d.figure_joints(*HIP, pose, facing=1)
    cx, cy = _card_in_hands(j)
    lx, ly = LAMP_X, BED_TOP - 90
    # 投影：从光源经卡片投向背墙（左上方），尺寸随 shadow_scale
    sx, sy = lerp_pt((cx, cy), (cx - (lx - cx) * 1.3, cy - 120), min(1, shadow_scale / 3))
    if city > 0:
        width, height = 980 * shadow_scale / 2.4, 560 * shadow_scale / 2.4
        base = 700
        path = d.skyline_path(sx - width * 0.62, base, width, height, seed=7)
        c.save()
        c.drawPath(path, d.fill("#050506", 0.85 * city * city_alpha, blur=5))
        c.drawPath(path, d.stroke(GOLD, 1.4, 0.10 * city * city_alpha))
        c.restore()
    if city < 1:
        w = 130 * (0.6 + 0.4 * shadow_scale)
        c.save()
        c.translate(sx + 40, sy + 10)
        c.rotate(card_rot * 0.6)
        c.drawRRect(d.rrect(0, 0, w, w * 0.68, 8), d.fill("#050506", 0.75 * (1 - city), blur=8))
        c.restore()
    d.bed(c, 40, 470, BED_TOP)
    d.lamp(c, LAMP_X, BED_TOP, on=lamp_on)
    d.floor_shadow(c, 560, 770, 220, 0.45)
    j = d.figure(c, *HIP, pose, facing=1)
    cx, cy = _card_in_hands(j)
    d.mark_card(c, cx, cy, rot=card_rot, lift=0.6)
    return j, (cx, cy)


def lerp_pt(a, b, x):
    return a[0] + (b[0] - a[0]) * x, a[1] + (b[1] - a[1]) * x


# ---------------------------------------------------------------- 镜头 01

def shot01(c, t, D, cue, view):
    s = 2.4 + 0.75 * d.ease_out(d.prog(t, cue["surge"] - F, 0.3)) + 0.08 * t / D
    c.save()
    k = 1 + 0.03 * t / D
    c.translate(500, 560)
    c.scale(k, k)
    c.translate(-500, -560)
    j, pos = bedroom(c, t, view, s, city=1.0, card_rot=-8 - 4 * d.ease_out(d.prog(t, cue["surge"] - F, 0.3)))
    d.glow(c, pos[0], pos[1], 90, GOLD, 0.25 * d.pulse(t, cue["surge"], 0.6))
    c.restore()


# ---------------------------------------------------------------- 镜头 02

DOC_W, DOC_H = 460, 600
DOC_C = (500, 470)
MARK_ROW = 6


def desk(c, view):
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#0E0F12"))
    g = skia.GradientShader.MakeRadial(skia.Point(500, 520), 760, [d.col("#2C2822", 0.9), d.col("#0E0F12", 0)])
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), skia.Paint(Shader=g))
    # 桌面木纹细线（透视）
    for i in range(9):
        y = 120 + i * 110
        c.drawLine(l, y, r, y + 30, d.stroke("#1A1915", 2, 0.7))


def doc_on_desk(c, scale=1.0, frame_k=0.0, tick_k=0.0, mark_a=1.0, hide_mark=False):
    """透视桌面上的方案文件；frame_k 控制金色框线锁定局部，tick_k 控制其余段落的正常勾选。"""
    quad = d.tilt_quad(DOC_C[0], DOC_C[1], DOC_W, DOC_H, tilt=0.18, scale=scale)
    c.save()
    c.concat(d.quad_matrix(DOC_W, DOC_H, quad))
    n = 11
    d.paper(c, 0, 0, DOC_W, DOC_H, lines=n, mark=None if hide_mark else (MARK_ROW, mark_a), lift=0.8,
            line_seed=4, ticks=int(round(tick_k * 5)))
    gap = DOC_H * 0.72 / n
    y = -DOC_H / 2 + DOC_H * 0.16 + MARK_ROW * gap
    if frame_k > 0:
        s = 1 + 0.25 * (1 - d.ease_back(frame_k, 2.0))
        hw, hh = DOC_W * 0.47 * s, gap * 0.95 * s
        a = d.clamp01(frame_k * 3)
        L = 26
        p = d.stroke(GOLD, 4, a)
        for sx in (-1, 1):
            for sy in (-1, 1):
                x0, y0 = sx * hw - DOC_W * 0.02, y + sy * hh
                c.drawLine(x0, y0, x0 - sx * L, y0, p)
                c.drawLine(x0, y0, x0, y0 - sy * L, p)
        c.drawRect(skia.Rect.MakeLTRB(-DOC_W / 2, -DOC_H / 2, DOC_W / 2, y - hh), d.fill("#000000", 0.0))
    c.restore()
    return quad


def mark_pos_on_doc(scale=1.0):
    n = 11
    gap = DOC_H * 0.72 / n
    y = -DOC_H / 2 + DOC_H * 0.16 + MARK_ROW * gap
    m = d.quad_matrix(DOC_W, DOC_H, d.tilt_quad(DOC_C[0], DOC_C[1], DOC_W, DOC_H, tilt=0.18, scale=scale))
    p = m.mapXY(-DOC_W * 0.12, y)
    return p.x(), p.y()


def shot02(c, t, D, cue, view):
    desk(c, view)
    grow = d.ease_out(d.prog(t, 0, 0.6))
    scale = 0.45 + 0.55 * grow
    doc_on_desk(c, scale=scale, frame_k=d.prog(t, cue["frame"] - F, 0.35),
                tick_k=d.prog(t, cue["frame"] + 0.5, 1.2))
    if t > cue["frame"]:
        x, y = mark_pos_on_doc()
        d.glow(c, x, y, 120, GOLD, 0.22 * d.pulse(t, cue["frame"], 0.6))


# ---------------------------------------------------------------- 镜头 03

REC = [(x, y) for y in (230, 400, 570, 740) for x in (190, 400, 610, 820)]


def shot03(c, t, D, cue, view):
    desk(c, view)
    pull = d.ease_io(d.prog(t, cue["pull"], D - 0.4 - cue["pull"]))
    zoom = 1 - 0.55 * pull
    c.save()
    c.translate(500, 480)
    c.scale(zoom, zoom)
    c.translate(-500, -480 - 260 * pull)
    # 其余工作记录：小卡片 + 正常勾选
    grow = d.ease_in(d.prog(t, 0.3, cue["cover"] - 0.3))
    mx, my = 500, 485
    R = 60 + grow * 820
    for i, (x, y) in enumerate(REC):
        dist = math.hypot(x - mx, y - my)
        covered = d.clamp01((R * 0.62 - dist + 60) / 60)
        if covered >= 1:
            continue
        d.paper(c, x, y, 150, 110, rot=(i * 37 % 9) - 4, lines=3, ticks=3, lift=0.5, line_seed=i,
                a=1 - covered * 0.6)
    # 膨胀的修改卡
    scale = 1 + grow * 6.2
    d.mark_card(c, mx, my, w=130 * scale, h=88 * scale, rot=-3 * (1 - grow), lift=1 + grow * 3,
                shade=0.35 * grow)
    c.restore()
    # 后退后显露的卡片城市（楼宇由叠放的纸卡构成）
    if pull > 0:
        city(c, view, pull)
    d.glow(c, 500, 560, 260, GOLD, 0.15 * d.pulse(t, cue["cover"], 0.5))


def city(c, view, k):
    """被巨大卡片阴影笼罩的城市：深色楼体、纸卡色的零星窗格，自下而上升起。"""
    l, t_, r, b = view
    rise = (1 - d.ease_out(k)) * 500
    base = 960 + rise
    rng = np.random.default_rng(11)
    path = d.skyline_path(l - 40, base, (r - l) + 80, 520, seed=5)
    c.drawPath(path, d.fill("#08090B", d.clamp01(k * 2)))
    c.drawPath(path, d.stroke(GOLD, 1.3, 0.25 * k))
    for x0, w, h in d.skyline_rects(5):
        X = l - 40 + x0 * ((r - l) + 80)
        Wd = w * ((r - l) + 80)
        top = base - h * 520
        for yy in np.arange(top + 30, base - 20, 42):
            for xx in np.arange(X + 10, X + Wd - 14, 26):
                if rng.random() < 0.18:
                    c.drawRect(skia.Rect.MakeXYWH(xx, yy, 12, 16), d.fill("#B9A98A", 0.28 * k))
    # 巨大卡片在城市上空投下的阴影
    sh = skia.Path()
    sh.moveTo(l, base - 520)
    sh.lineTo(r, base - 620)
    sh.lineTo(r, base + 20)
    sh.lineTo(l, base + 20)
    sh.close()
    c.drawPath(sh, d.fill("#000000", 0.35 * k, blur=30))


# ---------------------------------------------------------------- 镜头 04 / 05

RING = (500, 560, 330, 118)
PERIOD = 1.6


def ring_angle(t):
    return math.pi / 2 + 2 * math.pi * t / PERIOD


def ring_card(c, ang, shade, ring=RING, size=1.0, a=1.0):
    cx, cy, rx, ry = ring
    x, y = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
    depth = 0.72 + 0.28 * (math.sin(ang) + 1) / 2
    d.mark_card(c, x, y - 70 * depth * size, w=130 * depth * size, h=88 * depth * size,
                rot=-6 * math.cos(ang), shade=shade, lift=0.6 * depth, a=a)
    return x, y


def ring_floor(c, ring=RING, a=1.0, glow_k=0.0):
    cx, cy, rx, ry = ring
    c.drawPath(d.ellipse_path(cx, cy, rx, ry), d.stroke(GOLD, 2.2, (0.55 + 0.4 * glow_k) * a))
    c.drawPath(d.ellipse_path(cx, cy, rx, ry), d.stroke(GOLD, 10, 0.08 * a, blur=6))
    c.drawPath(d.ellipse_path(cx, cy, rx * 0.25, ry * 0.25), d.fill("#141519", a))
    c.drawPath(d.ellipse_path(cx, cy, rx * 0.25, ry * 0.25), d.stroke(GOLD, 1.2, 0.3 * a))


def inlet(c, x, y, a=1.0):
    """“新材料”入口：空托盘的虚线轮廓与向下箭头，始终没有东西进入。"""
    c.drawRRect(d.rrect(x, y, 120, 80, 10), d.stroke("#8C8574", 2, 0.6 * a, dash=((10, 8), 0)))
    c.drawLine(x, y - 110, x, y - 58, d.stroke("#8C8574", 2, 0.5 * a, dash=((6, 6), 0)))
    c.drawLine(x - 10, y - 70, x, y - 58, d.stroke("#8C8574", 2, 0.5 * a))
    c.drawLine(x + 10, y - 70, x, y - 58, d.stroke("#8C8574", 2, 0.5 * a))


def lap_shade(t, laps_at):
    k = sum(d.ease_out(d.prog(t, la, 0.25)) for la in laps_at)
    return min(0.9, 0.12 + 0.26 * k)


def shot04(c, t, D, cue, view):
    d.backdrop(c, view)
    laps = [cue["lap"], cue["lap"] + PERIOD, cue["lap"] + 2 * PERIOD]
    tt = t - cue["lap"]
    ang = math.pi / 2 + 2 * math.pi * tt / PERIOD
    shade = lap_shade(t, laps)
    inlet(c, 900, 360)
    ring_floor(c, glow_k=max(d.pulse(t, la, 0.4) for la in laps))
    # 拖影：前若干时刻的位置，颜色同当前
    for k in range(5, 0, -1):
        a2 = ang - k * 0.16
        cx, cy, rx, ry = RING
        c.drawCircle(cx + rx * math.cos(a2), cy + ry * math.sin(a2) - 60, 4, d.fill(GOLD, 0.08 * (6 - k)))
    behind = math.sin(ang) < 0
    if behind:
        ring_card(c, ang, shade)
        c.drawPath(d.ellipse_path(*RING[:2], RING[2] * 0.25, RING[3] * 0.25), d.fill("#141519"))
    else:
        ring_card(c, ang, shade)
    x, y = RING[0], RING[1] + RING[3]
    d.glow(c, x, y - 60, 120, GOLD, 0.25 * max(d.pulse(t, la, 0.5) for la in laps))


def shot05(c, t, D, cue, view):
    d.backdrop(c, view)
    # 承接镜头 04 结尾位置，0.5 秒内减速停下
    t4 = cue["_t4"]                          # 镜头 04 结束时距其首圈的时间，由渲染器注入
    halt = cue["halt"]
    tau = min(t, halt) - (min(t, halt) ** 2) / (2 * halt)
    ang = math.pi / 2 + 2 * math.pi * (t4 + tau) / PERIOD
    shift = d.ease_io(d.prog(t, halt, 0.8))
    ring = (500 - 230 * shift, 560, 330 * (1 - 0.32 * shift), 118 * (1 - 0.32 * shift))
    ring_floor(c, ring=ring)
    ring_card(c, ang, 0.9 - 0.0 * shift, ring=ring, size=1 - 0.25 * shift)
    # 通向桌面的短路径
    k = d.ease_out(d.prog(t, halt + 0.4, 1.2))
    if k > 0:
        x0, y0 = ring[0] + ring[2] + 20, 560
        x1 = x0 + (790 - x0) * k
        c.drawLine(x0, y0, x1, y0, d.stroke(GOLD, 3, 0.85, dash=((16, 10), 0)))
        if k > 0.95:
            c.drawLine(x1 - 16, y0 - 12, x1, y0, d.stroke(GOLD, 3))
            c.drawLine(x1 - 16, y0 + 12, x1, y0, d.stroke(GOLD, 3))
        a = d.prog(t, halt + 1.2, 0.6)
        if a > 0:
            c.drawRect(skia.Rect.MakeLTRB(800, 590, 960, 606), d.fill("#2A2824", a))
            c.drawLine(800, 590, 960, 590, d.stroke(GOLD, 1.5, 0.5 * a))
            c.drawRect(skia.Rect.MakeLTRB(815, 606, 825, 690), d.fill("#1F1E1B", a))
            c.drawRect(skia.Rect.MakeLTRB(935, 606, 945, 690), d.fill("#1F1E1B", a))
            d.paper(c, 880, 560, 92, 60, rot=-4, lines=3, lift=0.3, a=a, line_seed=2)


# ---------------------------------------------------------------- 镜头 06

def thumbs():
    rng = np.random.default_rng(21)
    out = []
    for i in range(10):
        ang = i / 10 * 2 * math.pi + rng.uniform(-0.2, 0.2)
        r = rng.uniform(330, 470)
        out.append((500 + r * math.cos(ang), 520 + r * 0.85 * math.sin(ang), rng.uniform(-14, 14),
                    rng.uniform(0.7, 1.15), rng.uniform(0, 0.6)))
    return out


THUMBS = thumbs()


def book(c, x, y, s=1.0, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    d.soft_shadow(c, 0, 0, 250, 330, r=10, lift=1.6, a=0.7)
    for k in range(5, 0, -1):          # 书页厚度
        c.drawRRect(d.rrect(k * 3, k * 3, 250, 330, 8), d.fill(d.mix(WHITE, "#000000", 0.25 + 0.06 * k)))
    c.drawRRect(d.rrect(0, 0, 250, 330, 8), d.fill("#1C1D21"))
    c.drawRect(skia.Rect.MakeLTRB(-125, -165, -100, 165), d.fill("#141518"))
    c.drawRRect(d.rrect(0, 0, 226, 306, 6), d.stroke(GOLD, 1.5, 0.7))
    c.drawLine(-60, -70, 80, -70, d.stroke(GOLD, 4, 0.85))
    c.drawLine(-60, -40, 50, -40, d.stroke(GOLD, 2, 0.6))
    for i in range(4):
        c.drawLine(-60, 20 + i * 26, 70, 20 + i * 26, d.stroke("#5E594F", 2))
    if a < 1:
        c.restore()
    c.restore()


def shot06(c, t, D, cue, view):
    d.backdrop(c, view)
    m = cue["merge"]
    for i, (x, y, rot, depth, delay) in enumerate(THUMBS):
        k = d.ease_in(d.prog(t, 0.2 + delay, m - 0.2 - delay))
        if k >= 1:
            continue
        px, py = d.lerp(x, 500, k), d.lerp(y, 520, k)
        s = depth * (1 - 0.5 * k)
        blur_far = depth < 0.85
        c.save()
        if blur_far:
            c.saveLayerAlpha(None, 200)
        d.paper(c, px, py + 8 * math.sin(t * 1.3 + i), 110 * s, 145 * s, rot=rot * (1 - k), lines=6,
                lift=0.6 * s, line_seed=i)
        if blur_far:
            c.restore()
        c.restore()
    if t >= m - 0.05:
        pop = d.ease_back(d.prog(t, m - 0.05, 0.35), 2.2)
        book(c, 500, 520, s=0.9 + 0.1 * pop, a=d.clamp01(pop * 1.5))
        d.sparks(c, 500, 520, t, m, n=18, r=260, seed=6)
        d.glow(c, 500, 520, 300, GOLD, 0.22 * d.pulse(t, m, 0.7))


# ---------------------------------------------------------------- 镜头 07 / 08

LOOP = (420, 660, 290, 92)
DOOR = (875, 520)


def loop_floor(c, a=1.0, ring=LOOP):
    c.drawPath(d.ellipse_path(*ring), d.stroke(GOLD, 2, 0.45 * a, dash=((14, 10), 0)))


def problem_card(c, x=LOOP[0], y=LOOP[1], shade=0.8, a=1.0):
    c.drawRect(skia.Rect.MakeLTRB(x - 4, y - 70, x + 4, y), d.fill("#2B2925", a))
    d.mark_card(c, x, y - 130, w=150, h=104, shade=shade, lift=0.8, a=a)


def door(c, x, y, glint=0.0, a=1.0):
    """关闭的新信息入口：门框、门板、金色门把，门缝下一线微光。"""
    c.drawRect(skia.Rect.MakeLTRB(x - 72, y - 250, x + 72, y + 140), d.fill("#141519", a))
    c.drawRect(skia.Rect.MakeLTRB(x - 72, y - 250, x + 72, y + 140), d.stroke(GOLD, 2, 0.45 * a))
    c.drawRect(skia.Rect.MakeLTRB(x - 60, y - 238, x + 60, y + 140), d.fill("#1E2025", a))
    c.drawLine(x - 60, y + 139, x + 60, y + 139, d.stroke("#E6CF9C", 2, (0.25 + 0.3 * glint) * a))
    c.drawCircle(x + 38, y - 40, 7, d.fill(GOLD, a))
    if glint > 0:
        d.glow(c, x + 38, y - 40, 40, GOLD, 0.5 * glint)


def walker(c, t, start, t_door, period=3.0, ring=LOOP, scale=0.72):
    """绕圈行走：t_door 时刻位于圆环最右侧（最接近门）。返回 (角度, 是否在后方, 绘制函数)。"""
    tt = max(t, start)
    ang = 2 * math.pi * (tt - t_door) / period
    cx, cy, rx, ry = ring
    x, y = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
    dx = -math.sin(ang)
    facing = 1 if dx >= 0 else -1
    depth = 0.8 + 0.2 * (math.sin(ang) + 1) / 2
    moving = t >= start
    phase = (tt - start) * 2 * math.pi / 0.75
    pose = d.walk(phase) if moving else d.SLUMP
    s = scale * depth

    def paint():
        d.floor_shadow(c, x, y + 2, 110 * s, 0.5)
        d.figure(c, x, y - (d.SEG["th"] + d.SEG["sh"]) * s, pose, facing=facing, scale=s)

    return ang, math.sin(ang) < 0, paint


def shot07(c, t, D, cue, view):
    d.room(c, view, floor_y=600)
    loop_floor(c)
    door(c, *DOOR, glint=d.pulse(t, cue["door"], 0.6))
    ang, behind, paint = walker(c, t, cue["walk"], cue["door"])
    if behind:
        paint()
        problem_card(c)
    else:
        problem_card(c)
        paint()


def shot08(c, t, D, cue, view):
    d.room(c, view, floor_y=600)
    fade = d.ease_io(d.prog(t, 0, 0.8))
    loop = (LOOP[0] - 170 * fade, LOOP[1], LOOP[2] * (1 - 0.45 * fade), LOOP[3] * (1 - 0.45 * fade))
    loop_floor(c, ring=loop, a=1 - 0.4 * fade)
    problem_card(c, x=loop[0], y=loop[1], a=1 - 0.5 * fade)
    # 分叉的另一条路径
    k = d.ease_out(d.prog(t, 0.4, cue["fact"] - 0.6))
    x0, y0 = loop[0] + loop[2], loop[1]
    x1 = 640
    c.drawLine(x0, y0, d.lerp(x0, x1, k), d.lerp(y0, 470, k), d.stroke(GOLD, 3, 0.9))
    if k > 0:
        c.drawCircle(d.lerp(x0, x1, k), d.lerp(y0, 470, k), 6, d.fill(GOLD))
    # 文件分成事实格与行动格（只用图形）
    fk = d.ease_back(d.prog(t, cue["fact"], 0.4), 1.6)
    ak = d.ease_back(d.prog(t, cue["act"], 0.4), 1.6)
    base_a = d.prog(t, 0.6, 0.5)
    if fk <= 0:
        d.paper(c, 790, 470, 230, 300, lines=8, lift=0.8, a=base_a, line_seed=8)
    else:
        lx = d.lerp(790, 700, fk)
        cell(c, lx, 470, "fact", a=1.0)
        if ak <= 0:
            d.paper(c, d.lerp(790, 860, fk), 470, 140, 220, lines=5, lift=0.6, line_seed=9)
        else:
            cell(c, d.lerp(860, 880, ak), 470, "act", a=1.0)
        d.glow(c, 700, 470, 120, GOLD, 0.25 * d.pulse(t, cue["fact"], 0.5))
        d.glow(c, 880, 470, 120, GOLD, 0.25 * d.pulse(t, cue["act"], 0.5))


def cell(c, x, y, kind, a=1.0, w=160, h=200):
    """事实格（小文件 + 一个圆圈标记）或行动格（向右箭头），只用图形不写字。"""
    d.paper(c, x, y, w, h, lift=0.7, a=a)
    c.drawRRect(d.rrect(x, y, w - 22, h - 22, 8), d.stroke(GOLD, 1.6, 0.6 * a))
    if kind == "fact":
        d.paper(c, x, y, 70, 90, lines=4, lift=0.2, edge=False, line_seed=3, a=a, mark=(1, 1.0))
    else:
        c.drawLine(x - 40, y, x + 36, y, d.stroke(GOLD, 6, a))
        c.drawLine(x + 14, y - 22, x + 38, y, d.stroke(GOLD, 6, a))
        c.drawLine(x + 14, y + 22, x + 38, y, d.stroke(GOLD, 6, a))


# ---------------------------------------------------------------- 镜头 09

FIG9 = (800, 640)


def shot09(c, t, D, cue, view):
    d.room(c, view, floor_y=760)
    f = d.ease_io(d.prog(t, 0.1, cue["fold"] - 0.1))
    # 手风琴式折叠：面板数 4 → 1，宽高同时收拢，颜色由暗转亮
    W0, H0 = 1100, 900
    W1, H1 = 300, 400
    w, h = d.lerp(W0, W1, f), d.lerp(H0, H1, f)
    cx, cy = d.lerp(500, 400, f), d.lerp(470, 470, f)
    shade = 0.85 * (1 - f)
    panels = 4
    d.soft_shadow(c, cx, cy, w, h, lift=1.5, a=0.7)
    for i in range(panels):
        y0 = cy - h / 2 + i * h / panels
        tone = d.mix(d.mix(WHITE, d.PAPER_DIM, shade), "#000000", (0.18 if i % 2 else 0.0) * math.sin(f * math.pi))
        c.drawRect(skia.Rect.MakeLTRB(cx - w / 2, y0, cx + w / 2, y0 + h / panels + 1), d.fill(tone))
    c.drawRect(skia.Rect.MakeLTRB(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), d.stroke(GOLD, 2, 0.5))
    if f < 1:
        path = d.skyline_path(cx - w / 2, cy + h / 2, w, h * 0.55, seed=7)
        c.drawPath(path, d.fill("#000000", 0.5 * (1 - f)))
    else:
        for i in range(7):
            yy = cy - h / 2 + 60 + i * 44
            c.drawLine(cx - w * 0.36, yy, cx + w * (0.2 if i % 3 == 2 else 0.34), yy, d.stroke("#9A948A", 4))
    d.glow(c, cx, cy, 240, GOLD, 0.25 * d.pulse(t, cue["fold"], 0.5))
    # 人物从右侧伸手，抽出真实修改标记
    pk = d.ease_io(d.prog(t, cue["pick"] - 0.5, 0.9))
    pose = d.blend(d.HOLD, d.REACH, d.prog(t, cue["pick"] - 0.9, 0.5)) if t < cue["pick"] + 0.6 else \
        d.blend(d.REACH, d.HOLD, d.prog(t, cue["pick"] + 0.6, 0.6))
    a_fig = d.prog(t, 0.6, 0.5)
    d.floor_shadow(c, FIG9[0], 770, 160, 0.5 * a_fig)
    j = d.figure(c, FIG9[0], FIG9[1] - (d.SEG["th"] + d.SEG["sh"]) + 140, pose, facing=-1, a=a_fig)
    if f >= 1:
        sx, sy = cx - 10, cy + 10
        hx, hy = j["hand_f"]
        mx, my = d.lerp(sx, hx - 50, pk), d.lerp(sy, hy - 20, pk)
        d.mark_card(c, mx, my, w=120, h=80, rot=-6 * pk, lift=0.4 + 0.8 * pk)


# ---------------------------------------------------------------- 镜头 10 / 11

SHEET = (500, 500, 760, 470)
C1 = (325, 500)
C2 = (675, 500)


def sheet(c, a=1.0):
    x, y, w, h = SHEET
    d.paper(c, x, y, w, h, lift=1.0, a=a)
    for cx, cy in (C1, C2):
        c.drawRRect(d.rrect(cx, cy, 310, 380, 12), d.stroke("#8C8574", 2, 0.8 * a, dash=((12, 8), 0)))
    c.drawLine(x, y - 190, x, y + 190, d.stroke("#C9C0AE", 1.5, 0.8 * a))


def event_icon(c, x, y, s=1.0, a=1.0):
    d.paper(c, x, y, 120 * s, 150 * s, lines=5, mark=(2, 1.0), lift=0.4, line_seed=3, a=a)


def vague_label(c, x, y, rot=0.0, a=1.0):
    """模糊的自我标签：灰色便签上一团看不清的涂抹（不可读，不加字）。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    d.soft_shadow(c, 0, 0, 200, 70, lift=0.6, a=0.5 * a)
    c.drawRRect(d.rrect(0, 0, 200, 70, 10), d.fill("#57534D", a))
    p = skia.Path()
    p.moveTo(-70, 0)
    for i in range(14):
        p.quadTo(-62 + i * 10, -18 if i % 2 else 18, -55 + i * 10, 0)
    c.drawPath(p, d.stroke("#2A2825", 7, 0.9 * a, blur=3.5))
    c.restore()


def shot10(c, t, D, cue, view):
    desk(c, view)
    sheet(c)
    # 图标先在格子上方淡入悬停，事件帧落入第一格，格子金框同时点亮
    appear = d.ease_out(d.prog(t, cue["place"] - 0.9, 0.5))
    drop = d.ease_in(d.prog(t, cue["place"] - 3 * F, 3 * F))
    event_icon(c, C1[0], C1[1] - 46 * (1 - drop) - 20 * (1 - appear), s=1.08 - 0.08 * drop, a=appear)
    lit = d.pulse(t, cue["place"], 1.2)
    if lit > 0:
        c.drawRRect(d.rrect(*C1, 310, 380, 12), d.stroke(GOLD, 4, 0.9 * lit))
    d.glow(c, *C1, 200, GOLD, 0.35 * lit)
    s = d.ease_io(d.prog(t, cue["slide"] - 0.5, 0.9))
    vague_label(c, d.lerp(500, 820, s), d.lerp(470, 740, s), rot=d.lerp(-4, 9, s), a=d.lerp(0.95, 0.75, s))


def paragraph(c, x, y, hi=0.0, cursor=0.0):
    """可修改段落：三行字迹，中间一行被金色虚线框选，光标闪烁。"""
    for i, ln in enumerate((170, 210, 140)):
        yy = y - 50 + i * 50
        c.drawLine(x - 110, yy, x - 110 + ln, yy, d.stroke("#8F897F", 5))
    if hi > 0:
        c.drawRRect(d.rrect(x - 4, y, 240, 38, 6), d.stroke(GOLD, 2.2, hi, dash=((10, 6), 0)))
    if cursor > 0:
        c.drawLine(x + 104, y - 15, x + 104, y + 15, d.stroke(GOLD, 3, cursor))


def shot11(c, t, D, cue, view):
    desk(c, view)
    sheet(c)
    event_icon(c, *C1)
    vague_label(c, 820, 740, rot=9, a=0.75)
    a = d.prog(t, 0.2, 0.5)
    paragraph(c, C2[0], C2[1], hi=d.prog(t, cue["point"], 0.3),
              cursor=a * (1 if (t * 2) % 2 < 1.2 else 0.15) if t > cue["point"] else 0)
    # 箭头：从事实格出发，只指向一个段落
    k = d.ease_io(d.prog(t, cue["point"] - 0.9, 0.9))
    if k > 0:
        p = skia.Path()
        p.moveTo(C1[0] + 70, C1[1] - 100)
        p.quadTo(500, 300, C2[0] - 140, C2[1])
        meas = skia.PathMeasure(p, False)
        L = meas.getLength()
        seg = skia.Path()
        meas.getSegment(0, L * k, seg, True)
        c.drawPath(seg, d.stroke(GOLD, 4))
        if k >= 1:
            pos, tan = meas.getPosTan(L)
            ex, ey = pos.x(), pos.y()
            ang = math.atan2(tan.y(), tan.x())
            for s in (-1, 1):
                c.drawLine(ex, ey, ex - 22 * math.cos(ang + s * 0.5), ey - 22 * math.sin(ang + s * 0.5),
                           d.stroke(GOLD, 4))
    d.glow(c, C2[0] - 4, C2[1], 140, GOLD, 0.22 * d.pulse(t, cue["point"], 0.5))


# ---------------------------------------------------------------- 镜头 12

def shot12(c, t, D, cue, view):
    d.room(c, view, floor_y=760, warm=(760, 420, 0.6))
    # 背后的环形轨道淡出
    ra = 1 - d.ease_io(d.prog(t, cue["down"], 2.5))
    if ra > 0:
        ring_floor(c, ring=(470, 800, 360, 70), a=ra)
    # 小桌
    c.drawRect(skia.Rect.MakeLTRB(560, 600, 820, 618), d.fill("#2A2824"))
    c.drawLine(560, 600, 820, 600, d.stroke(GOLD, 1.5, 0.5))
    c.drawRect(skia.Rect.MakeLTRB(580, 618, 594, 760), d.fill("#1D1C19"))
    c.drawRect(skia.Rect.MakeLTRB(786, 618, 800, 760), d.fill("#1D1C19"))
    k = d.ease_io(d.prog(t, cue["down"], 1.2))
    relax = d.ease_io(d.prog(t, cue["down"] + 1.4, 1.2))
    pose = d.blend(d.HOLD, d.LOWER, k) if k < 1 else d.blend(d.LOWER, d.STAND, relax)
    d.floor_shadow(c, 430, 770, 170, 0.5)
    j = d.figure(c, 430, 760 - (d.SEG["th"] + d.SEG["sh"]), pose, facing=1)
    hx, hy = (j["hand_f"][0] + j["hand_b"][0]) / 2, (j["hand_f"][1] + j["hand_b"][1]) / 2
    px, py = d.lerp(hx + 40, 690, k), d.lerp(hy - 40, 590, k)
    d.paper(c, px, py, 150, 110, rot=d.lerp(-6, 0, k), lines=4, mark=(1, 1.0), lift=d.lerp(0.8, 0.15, k),
            line_seed=5)


# ---------------------------------------------------------------- 镜头 13

def window(c, x0, y0, x1, y1, on, a=1.0):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), d.fill(d.mix("#121318", "#3D3426", on), a))
    if on > 0:
        g = skia.GradientShader.MakeRadial(skia.Point((x0 + x1) / 2, y1 - 60), (x1 - x0) * 0.8,
                                           [d.col("#F2D59A", 0.55 * on), d.col("#F2D59A", 0)])
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), skia.Paint(Shader=g))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), d.stroke(GOLD, 2, 0.5 * a))


def shot13(c, t, D, cue, view):
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#08090B"))
    # 夜色中的两栋楼：左边是主角的房间，右边是邻近的一扇窗
    c.drawRect(skia.Rect.MakeLTRB(l, 260, 470, b), d.fill("#111216"))
    c.drawRect(skia.Rect.MakeLTRB(560, 300, r, b), d.fill("#111216"))
    on = d.ease_out(d.prog(t, cue["lamp"], 0.5))
    window(c, 90, 380, 400, 700, 0.35)
    window(c, 620, 400, 900, 700, on)
    # 左窗：主角坐在小灯旁；右窗：一个中性剪影
    j = d.figure(c, 230, 690 - 40, d.SIT_EASE, facing=1, scale=0.62, rim=0.8)
    if on > 0:
        c.saveLayerAlpha(None, int(255 * on))
        d.figure(c, 800, 690 - 40, d.SIT_EASE, facing=-1, scale=0.6, rim=1.0)
        c.restore()
        d.glow(c, 700, 520, 90, "#FFF1D2", 0.5 * on)
    # 两扇窗之间的光桥
    br = d.ease_out(d.prog(t, cue["lamp"] + 0.4, 1.4))
    if br > 0:
        g = skia.GradientShader.MakeLinear([(400, 0), (620, 0)], [d.col("#E8C987", 0.0), d.col("#E8C987", 0.28 * br),
                                                                  d.col("#E8C987", 0.0)], [0, 0.5, 1])
        c.drawRect(skia.Rect.MakeLTRB(400, 560, 620, 700), skia.Paint(Shader=g, MaskFilter=skia.MaskFilter.MakeBlur(
            skia.kNormal_BlurStyle, 20)))
    rng = np.random.default_rng(13)
    for i in range(16):        # 灯下少量浮尘，仅局部
        x = 640 + rng.uniform(0, 240)
        y = 420 + ((rng.uniform(0, 260) - t * rng.uniform(6, 14)) % 260)
        c.drawCircle(x, y, rng.uniform(1.2, 2.4), d.fill("#F6E2B5", 0.35 * on * rng.uniform(0.4, 1)))


# ---------------------------------------------------------------- 镜头 14 / 15

def shot14(c, t, D, cue, view):
    # 事件帧瞬间收回：城市阴影换成卡片的真实影子，随后轻微回弹落定
    after = t >= cue["settle"] - 1e-6
    city = 0.0 if after else 1.0
    s = 1.0 + 0.15 * (1 - d.ease_out(d.prog(t, cue["settle"], 0.4))) if after else 2.6
    bedroom(c, t, view, s, city=city, card_rot=-6, pose=d.blend(d.SIT, d.SIT_EASE, d.prog(t, cue["settle"], 1.6)),
            city_alpha=0.75)


def shot15(c, t, D, cue, view):
    c.save()
    bedroom(c, 6.0, view, 1.0, city=0.0, card_rot=-6, pose=d.SIT_EASE)
    c.restore()
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62 * d.ease_out(d.prog(t, 0, 0.4))))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
