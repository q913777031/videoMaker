"""可复用的场景道具与构图（舞台单位 1000×1000）：床边、透视桌面与文件、卡片城市、环形轨道、
综述书本、绕圈步行、关闭的门、事实/行动格、反思纸、窗与灯。

撞击类动作的时刻一律由调用方传入（来自事件时刻表），道具本身不持有时间轴。
"""

import math

import numpy as np
import skia

from . import draw as d
from .config import GOLD, WHITE

F = 1 / 30           # 一帧：撞击动作从事件帧起即可见


# ---------------------------------------------------------------- 床边构图（人物坐床沿、台灯、墙上投影）

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
    lx = LAMP_X
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


# ---------------------------------------------------------------- 透视桌面与方案文件

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


# ---------------------------------------------------------------- 卡片城市

REC = [(x, y) for y in (230, 400, 570, 740) for x in (190, 400, 610, 820)]


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


# ---------------------------------------------------------------- 环形轨道与新材料入口

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


# ---------------------------------------------------------------- 论文缩略页与综述书本

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


# ---------------------------------------------------------------- 绕圈步行、问题卡、关闭的门、事实/行动格

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


# ---------------------------------------------------------------- 人物站位

FIG9 = (800, 640)


# ---------------------------------------------------------------- 反思纸、事件图标、模糊标签、可修改段落

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


def paragraph(c, x, y, hi=0.0, cursor=0.0):
    """可修改段落：三行字迹，中间一行被金色虚线框选，光标闪烁。"""
    for i, ln in enumerate((170, 210, 140)):
        yy = y - 50 + i * 50
        c.drawLine(x - 110, yy, x - 110 + ln, yy, d.stroke("#8F897F", 5))
    if hi > 0:
        c.drawRRect(d.rrect(x - 4, y, 240, 38, 6), d.stroke(GOLD, 2.2, hi, dash=((10, 6), 0)))
    if cursor > 0:
        c.drawLine(x + 104, y - 15, x + 104, y + 15, d.stroke(GOLD, 3, cursor))


# ---------------------------------------------------------------- 夜景窗户

def window(c, x0, y0, x1, y1, on, a=1.0):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), d.fill(d.mix("#121318", "#3D3426", on), a))
    if on > 0:
        g = skia.GradientShader.MakeRadial(skia.Point((x0 + x1) / 2, y1 - 60), (x1 - x0) * 0.8,
                                           [d.col("#F2D59A", 0.55 * on), d.col("#F2D59A", 0)])
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), skia.Paint(Shader=g))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), d.stroke(GOLD, 2, 0.5 * a))
