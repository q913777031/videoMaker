"""《丰田模式》系列公共模块：第 02 讲起的分镜模块都用它（第 01 讲 ep01_andon.py 保留自己的副本，输出不变）。

一个分镜模块只需写四样东西：文案（PLAN.md 里的代码块，plan.load 读）、SCREENS、每屏的画面、少量调参。
其余——旁白合成与逗号停顿、配乐按实测拍点循环延长并排期、drop 卡点、拍点吸附、相机、字幕时间轴、
页眉/封面需要的模块变量——都由 Lesson 完成，build.py 不用改（只在 MODS 里注册）。

最小骨架（见 fengtian/ep02_pull.py）：

    from fengtian import common as C
    from fengtian.common import BLACK, RED, BLUE, GREEN, ORANGE
    from whiteboard.engine import P, arrow, check, circle, cross, doc, join, rect

    SCREENS = [                       # (旁白句序号, 页眉标签, 白板区块)；区块相同的屏共用画面（切屏时不清空）
        ([], "开场", 0),
        ([0, 1], "打工人日常", 1),
        ([2], "丰田模式 · 书中做法", 2),   # drop_screen：这一屏的旁白在音乐 drop 处说完
        ...
    ]
    L = C.Lesson("03", SCREENS, drop_screen=2)        # 读文案、合成旁白、排期、换上延长后的拍点表
    b = L.b                                           # 白板（whiteboard.engine.Board）

    j = L.scene(0, L.intro_view(2600, 800))           # 屏 0：系列开场“丰田模式”四字（固定写法）
    L.intro(j, 2600, 800)

    j = L.scene(1, (900, 900, 0.7))                   # 每屏一个视角 (cx, cy, z)：z≈0.7 时可视范围约 ±620 × ±640
    b.path(j, 0, 0.8, desk(...), sfx="wood_high")     # 画面事件放在拍上：j 屏第 k 拍（整数拍才能带音效）
    k = L.kb(j, L.wt(0, 1, 0.5), lo=2)                # 第 0 句第 1 个分句念到一半时最近的拍（不早于第 2 拍）
    b.custom(j, k, k + 0.3, L.pop_text("补", x, y, 80, GREEN, j, k), sfx="pop")
    ...
    L.finish(cover_shot=4)                            # 构造 Episode、挂到白板
    L.export(globals())                               # 把 build.py 要用的名字（b, ep, LINES, BOUNDS, captions…）放进本模块

时间单位：
- “拍” k：本屏第 k 个实测拍（0 = 本屏第一拍，可为小数，小数只用于无音效的动作）；L.tb(j, k) 换成绝对秒。
- L.wt(li, ci, frac)：第 li 句第 ci 个分句（按“，”切）念到 frac 处的本地秒；L.kb(j, t, lo) 把它吸附到本屏的拍。
- 自定义绘制 fn(c, k, T)：T 为绝对秒（与 L.tb 同一时基），k 为本项进度 0–1，返回笔尖坐标或 None。

节奏规则（与第 01 讲一致，Lesson 的参数可调）：每屏 ≥ min_beats 拍，旁白讲完、画面画完后至少再停 hold 秒，
切屏在实测半小节线上，切屏镜头 1.3 秒缓入缓出；drop_screen 的旁白在 drop 前 30ms 说完，该屏再停 4 拍。
画面里的字也要过 engine/wording.py（--sheet 会列出“文案警告”），字幕每条 ≤10 字。

开发时配音还没合成完：FT_DRAFT_TTS=1 python3 -m fengtian.build NN --sheet 用已缓存的句子 + 按字数估长的占位音频排版
（不会启动 IndexTTS2），正式渲染前去掉。
"""

import hashlib
import json
import math
import os
import sys

import numpy as np
import skia

from adler import core
from adler import kit as K
from engine import audio
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp
from fengtian import plan, voice
from fengtian import theme as FT
from whiteboard import engine as wb
from whiteboard.engine import BLACK, BLUE, GREEN, ORANGE, RED, Board, P, circle, face, join, rect, stick  # noqa: F401

ACC = "#C8102E"
YELLOW, HAT, SUIT, BOARD_C = "#E0A21B", "#F2B705", "#CFE0F5", "#C89B63"
BOSS_SUIT, OHNO_COAT, SKIN_LINE = "#3D4A63", "#E6DDC4", BLACK
_PUNCT = "，。：？！、；"

core.SERIES.update(name="丰田模式", count="第一季", prefix="丰田")


# ================================================================ 小工具（与时间轴无关）

def pop_scale(dt, dur=0.32):
    """弹出：dt<0 为 0，dur 秒内带回弹地放大到 1。"""
    return 0.0 if dt < 0 else ease_out_back(clamp01(dt / dur))


def slam_scale(dt):
    """砸字：0.1 秒内从 1.9 倍砸到 1，再小幅震荡。"""
    if dt < 0:
        return 0.0
    if dt < 0.1:
        return lerp(1.9, 1.0, ease_out(dt / 0.1))
    return 1.0 + 0.07 * math.exp(-(dt - 0.1) * 9) * math.sin((dt - 0.1) * 30)


def wobble(dt, amp=6.0, freq=22.0, decay=7.0):
    """撞击后的衰减抖动（角度或位移），dt<0 为 0。"""
    return 0.0 if dt < 0 else amp * math.exp(-dt * decay) * math.sin(dt * freq)


def walk(T, t0, dur, x0, x1, bob=12.0, steps_per_s=3.0):
    """从 t0 起用 dur 秒从 x0 走到 x1：返回 (x, 上下颠的位移, 是否在走)。"""
    f = clamp01((T - t0) / dur) if dur > 0 else 1.0
    moving = 0 < f < 1
    x = lerp(x0, x1, ease_in_out(f))
    dy = -abs(math.sin((T - t0) * math.pi * steps_per_s)) * bob if moving else 0.0
    return x, dy, moving


def line(c, a, z, color, w, alpha=1.0):
    c.drawLine(a[0], a[1], z[0], z[1], wb.marker(color, w, alpha))


def reveal(c, x, top, h, p, half_w=400):
    """自上而下逐渐显出（clip），返回笔尖位置（p<1 时）。调用前 c.save()。"""
    c.clipRect(skia.Rect.MakeLTRB(x - half_w, top - 10, x + half_w, top + h * p))
    return (x + 70, top + h * p) if p < 1 else None


def heart_path(x, y, r=60) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def bulb_path(x, y, r=50) -> skia.Path:
    """灯泡（想通了）：(x, y) 为玻璃球中心。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 140, 260)
    parts = [p, P((x - r * 0.5, y + r * 0.75), (x - r * 0.45, y + r * 1.25), (x + r * 0.45, y + r * 1.25),
                  (x + r * 0.5, y + r * 0.75)),
             P((x - r * 0.4, y + r * 1.0), (x + r * 0.4, y + r * 1.0))]
    for i in range(5):
        a = math.radians(-90 + (i - 2) * 40)
        parts.append(P((x + math.cos(a) * r * 1.35, y + math.sin(a) * r * 1.35),
                       (x + math.cos(a) * r * 1.75, y + math.sin(a) * r * 1.75)))
    return join(*parts)


def loop_arrow(x, y, r=60) -> skia.Path:
    """回形箭头（重做）：绕 (x, y) 转 300° 的箭头。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -60, 300)
    a = math.radians(240)
    ex, ey = x + r * math.cos(a), y + r * math.sin(a)
    tx, ty = -math.sin(a), math.cos(a)
    for d in (0.5, -0.5):
        p.moveTo(ex, ey)
        p.lineTo(ex - 32 * (tx * math.cos(d) - ty * math.sin(d)), ey - 32 * (tx * math.sin(d) + ty * math.cos(d)))
    return p


def box_path(x, y, w=150, h=110) -> skia.Path:
    """纸箱（正视，带封箱线）：(x, y) 为底边中点。"""
    return join(rect(x, y - h / 2, w, h, 8), P((x - w / 2, y - h + 26), (x + w / 2, y - h + 26)),
                P((x, y - h), (x, y - h + 26)))


# ================================================================ 角色（白板坐标；(x, y) 为脚底，s 为缩放，身高约 330·s）
# 区分方式：员工小王 = 黄安全帽 + 蓝工服 + 胸牌；组长老张 = 红帽 + 夹板 + 红臂章；打工人小李 = 黑线小人 + 头发 + 领带；
# 领导 = 深色西装 + 背头 + 红领带；大野耐一 = 圆眼镜 + 米色工作服 + 两鬓头发。

def rest_hands(x, y, s):
    hy = y - 290 * s
    return (x - 70 * s, hy + 170 * s), (x + 70 * s, hy + 170 * s)


def shoulder(x, y, s):
    return x, y - 290 * s + 80 * s


def _eyes_mouth(c, hx, hy, s, mood, alpha):
    for dx in (-15, 15):
        c.drawCircle(hx + dx * s, hy - 4 * s, 4 * s, K.paint(BLACK, alpha))
    if mood == "smile":
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(hx - 18 * s, hy + 2 * s, 36 * s, 26 * s), 20, 140)
        c.drawPath(m, wb.marker(BLACK, 6, alpha))
    elif mood == "sad":
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(hx - 16 * s, hy + 14 * s, 32 * s, 20 * s), 200, 140)
        c.drawPath(m, wb.marker(BLACK, 6, alpha))
    elif mood == "o":
        c.drawCircle(hx, hy + 22 * s, 8 * s, wb.marker(BLACK, 5, alpha))
    else:
        line(c, (hx - 14 * s, hy + 20 * s), (hx + 14 * s, hy + 20 * s), BLACK, 6, alpha)


def draw_worker(c, x, y, s, lh=None, rh=None, head_dx=0.0, alpha=1.0, mood="flat"):
    """员工（小王）：黄安全帽、蓝工服、胸牌。lh / rh 为左右手位置（默认垂手）。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    torso = skia.Rect.MakeLTRB(x - 42 * s, hy + 55 * s, x + 42 * s, y - 105 * s)
    c.drawRoundRect(torso, 18 * s, 18 * s, K.paint(SUIT, alpha))
    c.drawRoundRect(torso, 18 * s, 18 * s, wb.marker(BLUE, 8, alpha))
    for foot in ((x - 55 * s, y), (x + 55 * s, y)):
        line(c, hip, foot, BLUE, 10, alpha)
    line(c, sh, lh, BLUE, 10, alpha)
    line(c, sh, rh, BLUE, 10, alpha)
    hx = x + head_dx
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    _eyes_mouth(c, hx, hy, s, mood, alpha)
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeXYWH(hx - 50 * s, hy - 82 * s, 100 * s, 90 * s), 180, 180)
    dome.close()
    c.drawPath(dome, K.paint(HAT, alpha))
    c.drawPath(dome, wb.marker(BLACK, 7, alpha))
    line(c, (hx - 66 * s, hy - 37 * s), (hx + 66 * s, hy - 37 * s), BLACK, 9, alpha)
    badge = skia.Rect.MakeXYWH(x - 26 * s, hy + 88 * s, 52 * s, 30 * s)
    c.drawRoundRect(badge, 5, 5, K.paint("#FFFFFF", alpha))
    c.drawRoundRect(badge, 5, 5, wb.marker(BLUE, 4, alpha))


def draw_leader(c, x, y, s, phase=0.0, run=0.0, head_dx=0.0, alpha=1.0):
    """组长（老张）：红帽、夹板、红臂章；run>0 时跑步（phase 为步伐相位 0–1）。"""
    bob = -abs(math.sin(math.pi * phase)) * 16 * run
    y0 = y + bob
    hy = y0 - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y0 - 120 * s)
    sw = math.sin(2 * math.pi * phase) * run
    line(c, (x, hy + 45 * s), hip, BLACK, 11, alpha)
    for sgn in (1, -1):
        stand = (x + sgn * 55 * s, y)
        runp = (x + sgn * 75 * s * sw, y0 - 22 * s * max(0.0, -sgn * sw))
        line(c, hip, (lerp(stand[0], runp[0], run), lerp(stand[1], runp[1], run)), BLACK, 11, alpha)
    clip_c = (x - 80 * s, hy + 150 * s)
    line(c, sh, (clip_c[0] + 10 * s, clip_c[1]), BLACK, 11, alpha)
    rh = (x + 70 * s - 30 * sw * s, hy + 170 * s - 25 * abs(sw) * s)
    line(c, sh, rh, BLACK, 11, alpha)
    clip = skia.Rect.MakeXYWH(clip_c[0] - 40 * s, clip_c[1] - 55 * s, 80 * s, 105 * s)
    c.drawRoundRect(clip, 6, 6, K.paint(BOARD_C, alpha))
    c.drawRoundRect(clip, 6, 6, wb.marker(BLACK, 6, alpha))
    for i in range(3):
        yy = clip_c[1] - 20 * s + i * 22 * s
        line(c, (clip_c[0] - 25 * s, yy), (clip_c[0] + 25 * s, yy), BLACK, 4, alpha)
    ax, ay = lerp(sh[0], rh[0], 0.4), lerp(sh[1], rh[1], 0.4)
    c.drawRoundRect(skia.Rect.MakeXYWH(ax - 30 * s, ay - 15 * s, 60 * s, 30 * s), 6, 6, K.paint(RED, alpha))
    hx = x + head_dx
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    for dx in (-15, 15):
        c.drawCircle(hx + dx * s, hy - 4 * s, 4 * s, K.paint(BLACK, alpha))
    m = skia.Path()
    m.addArc(skia.Rect.MakeXYWH(hx - 16 * s, hy + 12 * s, 32 * s, 18 * s), 200, 140)
    c.drawPath(m, wb.marker(BLACK, 6, alpha))
    cap = skia.Path()
    cap.addArc(skia.Rect.MakeXYWH(hx - 47 * s, hy - 70 * s, 94 * s, 70 * s), 180, 180)
    cap.close()
    c.drawPath(cap, K.paint(RED, alpha))
    c.drawPath(cap, wb.marker(BLACK, 6, alpha))
    line(c, (hx - 10 * s, hy - 35 * s), (hx - 80 * s, hy - 30 * s), BLACK, 10, alpha)


def draw_li(c, x, y, s, mood="flat", back=False, squash=1.0, bag=False, alpha=1.0, lh=None, rh=None):
    """打工人小李：黑线小人 + 头发 + 领带；back=True 背过身；squash<1 被压扁；lh / rh 给定时画成这两只手的位置。"""
    c.save()
    c.translate(x, y)
    c.scale(1.0, squash)
    c.translate(-x, -y)
    hy = y - 290 * s
    sh = shoulder(x, y, s)
    d_lh, d_rh = rest_hands(x, y, s)
    parts = [circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)), P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)),
             P(lh or d_lh, sh), P(sh, rh or d_rh),
             P((x - 45 * s, hy - 5 * s), (x - 30 * s, hy - 45 * s), (x + 30 * s, hy - 45 * s), (x + 50 * s, hy + 10 * s))]
    if not back:
        parts.append(P((x, hy + 50 * s), (x - 12 * s, hy + 100 * s), (x, hy + 120 * s), (x + 12 * s, hy + 100 * s), close=True))
    if bag:
        parts.append(rect(x + 50 * s, y - 200 * s, 60 * s, 90 * s, 10 * s))
    c.drawPath(join(*parts), wb.marker(BLACK, 10, alpha))
    if back:
        c.drawPath(P((x - 40 * s, hy - 10 * s), (x - 20 * s, hy + 30 * s), (x + 20 * s, hy + 30 * s), (x + 40 * s, hy - 10 * s)),
                   wb.marker(BLACK, 7, alpha))
    else:
        c.drawPath(face(x, y, s, mood), wb.marker(BLACK, 7, alpha))
    c.restore()


def draw_boss(c, x, y, s, lh=None, rh=None, mood="flat", head_dy=0.0, alpha=1.0):
    """领导：深色西装（填色）+ 白衬衫 V 领 + 红领带 + 背头；head_dy 用来点头。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for foot in ((x - 50 * s, y), (x + 50 * s, y)):
        line(c, hip, foot, BOSS_SUIT, 12, alpha)
    torso = skia.Path()
    torso.moveTo(x - 50 * s, hy + 60 * s)
    torso.lineTo(x + 50 * s, hy + 60 * s)
    torso.lineTo(x + 46 * s, y - 100 * s)
    torso.lineTo(x - 46 * s, y - 100 * s)
    torso.close()
    c.drawPath(torso, K.paint(BOSS_SUIT, alpha))
    c.drawPath(P((x - 22 * s, hy + 60 * s), (x, hy + 120 * s), (x + 22 * s, hy + 60 * s), close=True), K.paint("#FFFFFF", alpha))
    c.drawPath(P((x, hy + 66 * s), (x - 9 * s, hy + 100 * s), (x, hy + 122 * s), (x + 9 * s, hy + 100 * s), close=True),
               K.paint(RED, alpha))
    line(c, sh, lh, BOSS_SUIT, 12, alpha)
    line(c, sh, rh, BOSS_SUIT, 12, alpha)
    hy += head_dy
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    _eyes_mouth(c, x, hy, s, mood, alpha)
    hair = skia.Path()
    hair.addArc(skia.Rect.MakeXYWH(x - 48 * s, hy - 50 * s, 96 * s, 70 * s), 180, 180)
    hair.close()
    c.drawPath(hair, K.paint(BLACK, alpha))
    line(c, (x - 20 * s, hy - 30 * s), (x + 30 * s, hy - 42 * s), "#FFFFFF", 4, alpha)


def draw_ohno(c, x, y, s, lh=None, rh=None, mood="flat", head_dx=0.0, alpha=1.0):
    """大野耐一：米色工作服、圆眼镜、头顶光、两鬓有头发。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for foot in ((x - 52 * s, y), (x + 52 * s, y)):
        line(c, hip, foot, BLACK, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 46 * s, hy + 55 * s, x + 46 * s, y - 95 * s)
    c.drawRoundRect(torso, 16 * s, 16 * s, K.paint(OHNO_COAT, alpha))
    c.drawRoundRect(torso, 16 * s, 16 * s, wb.marker(BLACK, 7, alpha))
    line(c, (x, hy + 60 * s), (x, y - 100 * s), BLACK, 4, alpha)
    for i in range(3):
        c.drawCircle(x + 10 * s, hy + 90 * s + i * 32 * s, 4 * s, K.paint(BLACK, alpha))
    line(c, sh, lh, BLACK, 10, alpha)
    line(c, sh, rh, BLACK, 10, alpha)
    hx = x + head_dx
    c.drawCircle(hx, hy, 46 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 46 * s, wb.marker(BLACK, 9, alpha))
    for sgn in (-1, 1):
        c.drawCircle(hx + sgn * 18 * s, hy - 4 * s, 15 * s, wb.marker(BLACK, 5, alpha))
        side = skia.Path()
        side.addArc(skia.Rect.MakeXYWH(hx - 52 * s, hy - 40 * s, 104 * s, 70 * s), 180 if sgn < 0 else 300, 60)
        c.drawPath(side, wb.marker("#6B6B6B", 10, alpha))
    line(c, (hx - 3 * s, hy - 4 * s), (hx + 3 * s, hy - 4 * s), BLACK, 4, alpha)
    for dx in (-18, 18):
        c.drawCircle(hx + dx * s, hy - 4 * s, 3.5 * s, K.paint(BLACK, alpha))
    if mood == "smile":
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(hx - 16 * s, hy + 10 * s, 32 * s, 22 * s), 20, 140)
        c.drawPath(m, wb.marker(BLACK, 6, alpha))
    else:
        line(c, (hx - 12 * s, hy + 24 * s), (hx + 12 * s, hy + 24 * s), BLACK, 6, alpha)


# ================================================================ 旁白：补逗号停顿

def stretch(x, text, target=0.25, max_gap=0.6):
    """逗号处补停顿到约 target 秒（预期位置 ±12% 内最安静的 30ms 切开），模型自带超过 max_gap 的停顿压到 max_gap。
    返回 (音频, 各分句起点秒)。target=0 只做压缩不补。与第 01 讲 stretch 相同。"""
    clauses = text.rstrip("。：？！；").split("，")
    hz = [sum(1 for ch in cl if ch not in "。：？！、；") for cl in clauses]
    total = sum(hz)
    hop = int(0.01 * audio.SR)
    starts, added, acc = [], 0, 0
    for ci in range(len(clauses) - 1):
        acc += hz[ci]
        n = len(x) // hop
        r = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1))
        r3 = np.convolve(r, np.ones(3) / 3, "same")
        orig_n = (len(x) - added) // hop
        center = int(acc / total * orig_n) + added // hop
        lo, hi = max(1, center - int(0.12 * orig_n)), min(n - 1, center + int(0.12 * orig_n))
        i = lo + int(np.argmin(r3[lo:hi]))
        quiet = r3 < r.max() * 10 ** (-32 / 20)
        a = i
        while a > 0 and quiet[a - 1]:
            a -= 1
        e = i
        while e < n and quiet[e]:
            e += 1
        have = (e - a) / 100 if quiet[i] else 0.0
        if target and have > max_gap:
            k0, k1 = (a * hop + int(max_gap / 2 * audio.SR)), (e * hop - int(max_gap / 2 * audio.SR))
            x = np.concatenate([x[:k0], x[k1:]])
            added -= k1 - k0
            i, have = a + int(max_gap * 50), max_gap
        add = int(max(0.0, target - have) * audio.SR)
        cut = i * hop
        f = int(0.008 * audio.SR)
        left, right = x[:cut].copy(), x[cut:].copy()
        left[-f:] *= np.linspace(1, 0, f)
        right[:f] *= np.linspace(0, 1, f)
        x = np.concatenate([left, np.zeros(add), right])
        added += add
        starts.append((cut + add) / audio.SR - min(0.05, have / 2))
    return x, [0.0] + starts


def _draft_clip(text, seed):
    """占位音频：每字 0.24 秒的低噪声，逗号处 0.12 秒静音（只用于配音没合成完时排版）。"""
    rng = np.random.default_rng(seed)
    out = []
    for cl in text.rstrip("。：？！；").split("，"):
        n = sum(1 for ch in cl if ch not in _PUNCT)
        out += [0.05 * rng.standard_normal(int(n * 0.24 * audio.SR)), np.zeros(int(0.12 * audio.SR))]
    return np.concatenate(out[:-1])


def synthesize(lines, mood, pinyin, groups=None):
    """fengtian.voice.synthesize（平淡叙述、同屏连读）；FT_DRAFT_TTS=1 时只读旧版逐句缓存排版，没缓存的句子用占位音频（不启动 IndexTTS2）。"""
    if not os.environ.get("FT_DRAFT_TTS"):
        return voice.synthesize(lines, mood, pinyin, groups=groups)
    nar = audio.Narrator(voice.VOICE)
    out, miss = [], 0
    for i, ((t, *_), m) in enumerate(zip(lines, mood)):
        e = audio._ix2_emo({"text": voice.EMO[m], "alpha": voice.ALPHA})
        raw = f"{nar._key}|{json.dumps(e, sort_keys=True, ensure_ascii=False)}|{1.0:.4f}|{voice.tts_text(t, pinyin)}"
        p = audio.CACHE_DIR / f"{hashlib.sha1(raw.encode()).hexdigest()}.npy"
        if p.exists():
            out.append(np.load(p))
        else:
            out.append(_draft_clip(t, i))
            miss += 1
    print(f"[FT_DRAFT_TTS] {miss}/{len(lines)} 句用占位音频（时长为估算），不要拿来出成片", file=sys.stderr)
    return out


# ================================================================ 一讲

class Lesson:
    """一讲的时间轴与画面工具。构造时完成：读文案 → 合成旁白 → 补逗号停顿 → 配乐延长 + 排期 → 换上虚拟拍点表 → 建白板。

    参数
      nn            讲号字符串，如 "02"（读 PLAN.md 的「### 02 …」代码块）
      screens       [(旁白句序号列表, 页眉标签, 白板区块)]；第 0 屏为系列开场（无旁白）
      drop_screen   哪一屏的旁白在音乐 drop 处说完（≥1；该屏一般放本讲第一个“砸”的画面，并在 drop 拍放重击/震屏/闪白）
      hold          每屏旁白讲完后至少再停的秒数（第 01 讲 1.55）
      min_beats     每屏至少几拍
      intro_beats   开场屏拍数（四字逐拍落定后停留，再缓推进入第 1 屏）
      extra_hold    {屏号: 额外停留秒}
      comma/max_gap 逗号停顿目标与上限（秒）
      natural_comma 不补逗号停顿的句序号集合
      board_size    白板尺寸
      acc           系列强调色（页眉期号、封面）；给了 theme 时用 theme["acc"]
      theme         本讲样式（fengtian.theme.THEMES 里的一套，或同样字段的 dict）：主题色、纸张底色与纹理、页眉风格、
                    开场钩子（hook，见 fengtian/hooks.py）、切屏转场（move / move_s）、开场屏拍数（intro_beats，默认 8）
    构造后可用的属性（export 会放进分镜模块）：NO KEY CONCEPT TITLE TAGS COVER_TITLE LINES LINE_MOOD PINYIN SCREENS GROUP
      RAW CLIPS CLAUSE_T DUR_L BOUNDS STARTS S END_LOCAL DROP SEAMS b ep；方法 captions() music_track()。
    """

    PRE_A, PRE_B = 16, 24          # drop 前可循环的前奏段（原曲拍号，8.6–12.9 秒）
    LOOP_A, LOOP_B = 96, 136       # drop 后可循环的中段（51.2–72.4 秒）
    DROP0 = 32                     # 原曲 drop 拍号
    XFADE = 0.04
    MOVE_S = 1.3                   # 切屏镜头移动秒数

    def __init__(self, nn, screens, *, drop_screen=2, hold=1.55, min_beats=10, intro_beats=6, extra_hold=None,
                 comma=0.25, max_gap=0.6, natural_comma=(), board_size=(4800, 10600), acc=ACC, theme=None):
        p = plan.load(nn)
        self.THEME = FT.finish(theme) if theme else FT.finish(dict(acc=acc))
        if theme:
            acc = self.THEME["acc"]
            intro_beats = self.THEME.get("intro_beats", 8)
        self.MOVE_S = self.THEME.get("move_s", self.MOVE_S)
        self.NO, self.KEY, self.CONCEPT = p["NO"], p["KEY"], p["CONCEPT"]
        self.TITLE, self.TAGS, self.COVER_TITLE = p["TITLE"], p["TAGS"], p["COVER_TITLE"]
        self.LINES, self.LINE_MOOD, self.PINYIN = p["LINES"], p["LINE_MOOD"], p["PINYIN"]
        self.ACC = acc
        self.SCREENS = screens
        self.GROUP = [s[2] for s in screens]
        self.HOLD, self.MIN_BEATS, self.INTRO_BEATS = hold, min_beats, intro_beats
        self.EXTRA_HOLD = extra_hold or {}
        self.COMMA, self.MAX_GAP = comma, max_gap
        self.drop_screen = drop_screen
        covered = sorted(li for s in screens for li in s[0])
        if covered != list(range(len(self.LINES))):
            raise ValueError(f"SCREENS 要按顺序覆盖全部 {len(self.LINES)} 句旁白，现在是 {covered}")
        if not 1 <= drop_screen < len(screens) or not screens[drop_screen][0]:
            raise ValueError("drop_screen 要指向第 1 屏之后、有旁白的一屏")

        self.RAW = synthesize(self.LINES, self.LINE_MOOD, self.PINYIN, groups=[sc[0] for sc in self.SCREENS if sc[0]])
        self.CLIPS, self.CLAUSE_T = zip(*[stretch(x, t, 0.0 if i in natural_comma else comma, max_gap)
                                          for i, (x, (t, _, _)) in enumerate(zip(self.RAW, self.LINES))])
        self.DUR_L = [len(x) / audio.SR for x in self.CLIPS]

        self.ORIG_BEATS = [dict(bt_) for bt_ in core.DET["beats"]]
        self.ORIG_T = np.array([bt_["t"] for bt_ in self.ORIG_BEATS])
        self._music_orig = None
        self.K_PRE, self.K_INS, self.SEQ, self.VT, (bounds, starts_abs) = self._search()
        self.DROP = self.DROP0 + self.K_PRE
        self.LAST = len(self.VT) - 1
        bounds[-1] = (bounds[-1][0], self.LAST)                     # 末屏延到原曲最后一击
        self.BOUNDS = bounds
        self._install_beats()
        self.S = core.bt(bounds[0][0]) - 0.15
        self.STARTS = [t - self.S for t in starts_abs]
        last_voice = self.STARTS[-1] + self.DUR_L[-1]
        self.END_LOCAL = min(core.END - self.S - 0.05, max(core.bt(self.LAST) - self.S + 1.2, last_voice + 2.0))
        self.SEAMS = []
        self.b = Board(size=board_size)
        self.ep = None
        self.TEXTS = []                 # 自定义项里画的字（pop_text / slam_text / stamp / pop_bubble / note），交给文案检查
        wb.camera = self.camera

    # ------------------------------------------------------------ 配乐延长与排期

    def _dur(self, o):
        T = self.ORIG_T
        return T[o + 1] - T[o] if o + 1 < len(T) else T[o] - T[o - 1]

    def _grid(self, k1, k2):
        """虚拟拍序列：前奏段插 k1 拍、中段插 k2 拍。返回 (原曲拍号序列, 虚拟拍点时刻)。"""
        seq = list(range(self.PRE_B)) + [self.PRE_A + i % (self.PRE_B - self.PRE_A) for i in range(k1)]
        seq += list(range(self.PRE_B, self.LOOP_B)) + [self.LOOP_A + i % (self.LOOP_B - self.LOOP_A) for i in range(k2)]
        seq += list(range(self.LOOP_B, len(self.ORIG_T)))
        ts = [self.ORIG_T[seq[0]]]
        for o in seq[:-1]:
            ts.append(ts[-1] + self._dur(o))
        return seq, np.array(ts)

    def _span(self, si, lead):
        """一屏旁白（含句间间隔）从屏起点算的长度。"""
        t = lead
        for k, li in enumerate(self.SCREENS[si][0]):
            t += (self.LINES[li][2] if k else 0.0) + self.DUR_L[li]
        return t

    def _schedule(self, T, drop):
        """返回 (每屏 [起拍, 止拍), 每句起点（配乐绝对秒）)；片头前拍不够返回 "pre"，结尾不够返回 None。"""
        L, SC, D = self.LINES, self.SCREENS, self.drop_screen
        st = [None] * len(L)
        # drop 屏：旁白在 drop 前 30ms 说完
        t_end = T[drop] - 0.03
        lines = SC[D][0]
        for k in range(len(lines) - 1, -1, -1):
            li = lines[k]
            st[li] = t_end - self.DUR_L[li]
            t_end = st[li] - (L[li][2] if k else 0.0)
        need = 0.4 + (T[drop] - 0.03 - st[lines[0]])
        sb = [None] * (D + 1)
        sb[D] = drop - self.MIN_BEATS
        while sb[D] >= 0 and T[drop] - T[sb[D]] < need:
            sb[D] -= 2
        # drop 之前的各屏倒着排
        for si in range(D - 1, 0, -1):
            lead = 0.2 if si == 1 else 0.3                 # 第 1 句在镜头从片头缓推向第 1 屏时进
            span = self._span(si, lead) + self.HOLD + self.EXTRA_HOLD.get(si, 0.0)
            s_ = sb[si + 1] - self.MIN_BEATS
            while s_ >= 0 and T[s_] + span > T[sb[si + 1]]:
                s_ -= 2
            sb[si] = s_
        if sb[1] is None or sb[1] - self.INTRO_BEATS < 0:
            return "pre"
        for si in range(1, D):
            t = T[sb[si]] + (0.2 if si == 1 else 0.3)
            for k, li in enumerate(SC[si][0]):
                if k:
                    t += L[li][2]
                st[li] = t
                t += self.DUR_L[li]
        bounds = [(sb[1] - self.INTRO_BEATS, sb[1])] + [(sb[i], sb[i + 1]) for i in range(1, D)] + [(sb[D], drop + 4)]
        b = drop + 4
        for si in range(D + 1, len(SC)):
            if b >= len(T) - 1:
                return None
            t = T[b] + 0.3
            for k, li in enumerate(SC[si][0]):
                if k:
                    t += L[li][2]
                st[li] = t
                t += self.DUR_L[li]
            i = int(np.searchsorted(T, t + self.HOLD + self.EXTRA_HOLD.get(si, 0.0) - 1e-6))
            e = max(b + self.MIN_BEATS, i + (i % 2))
            bounds.append((b, e))
            b = e
        return bounds, st

    def _search(self):
        for k1 in range(0, 80, 4):
            for k2 in range(0, 400, 4):
                seq, vt = self._grid(k1, k2)
                res = self._schedule(vt, self.DROP0 + k1)
                if res == "pre":
                    break
                if res is not None and res[0][-1][1] <= len(vt) - 1:
                    return k1, k2, seq, vt, res
        raise ValueError("排不下")

    def _install_beats(self):
        """把引擎的拍点表换成延长后的（只影响本进程）。"""
        vbeats = [dict(self.ORIG_BEATS[o], t=float(t)) for o, t in zip(self.SEQ, self.VT)]
        core.BEATS = vbeats
        core._BEAT_T = self.VT
        core.N_BEATS = len(vbeats)
        core.LAST_BAR = (core.N_BEATS - 1) // 4
        core.MUSIC_END = vbeats[core.LAST_BAR * 4]["t"] + 0.3
        core.END = core.MUSIC_END + 2.9

    def music_orig(self):
        """原版 core.music_track()（用原始拍点表算尾音），只算一次。"""
        if self._music_orig is None:
            saved = core.BEATS, core._BEAT_T, core.N_BEATS, core.LAST_BAR, core.MUSIC_END, core.END
            core.BEATS, core._BEAT_T, core.N_BEATS = self.ORIG_BEATS, self.ORIG_T, len(self.ORIG_BEATS)
            core.LAST_BAR = (core.N_BEATS - 1) // 4
            core.MUSIC_END = self.ORIG_BEATS[core.LAST_BAR * 4]["t"] + 0.3
            core.END = core.MUSIC_END + 2.9
            try:
                self._music_orig = core.music_track()
            finally:
                core.BEATS, core._BEAT_T, core.N_BEATS, core.LAST_BAR, core.MUSIC_END, core.END = saved
        return self._music_orig

    def music_track(self):
        """延长后的配乐：原曲按虚拟拍序列分段拼接（都在实测小节线上），接缝 40ms 等功率交叉淡化。"""
        sr = audio.SR
        src = self.music_orig()
        SEQ, VT, OT = self.SEQ, self.VT, self.ORIG_T
        runs = [(i, o) for i, o in enumerate(SEQ) if i == 0 or o != SEQ[i - 1] + 1]
        segs = []
        for r, (i, o) in enumerate(runs):
            if r + 1 < len(runs):
                last = SEQ[runs[r + 1][0] - 1]
                ln = OT[last] + self._dur(last) - OT[o]
            else:
                ln = len(src) / sr - OT[o]
            out0, src0 = (0.0, 0.0) if r == 0 else (VT[i], OT[o])
            if r == 0:
                ln += OT[o]
            segs.append((out0, src0, ln))
        n = int(round((segs[-1][0] + segs[-1][2]) * sr))
        out = np.zeros((n, 2))
        for o_, s_, ln in segs:
            i0, j0, m = int(round(o_ * sr)), int(round(s_ * sr)), int(round(ln * sr))
            m = min(m, len(src) - j0, n - i0)
            out[i0: i0 + m] = src[j0: j0 + m]
        h = int(self.XFADE * sr / 2)
        self.SEAMS.clear()
        for (o1, s1_, l1), (o2, s2_, _) in zip(segs, segs[1:]):
            j = int(round(o2 * sr))
            pe, ns = int(round((s1_ + l1) * sr)), int(round(s2_ * sr))
            w = np.linspace(0, 1, 2 * h)[:, None]
            a, bb = src[pe - h: pe + h], src[ns - h: ns + h]
            if len(a) == 2 * h and len(bb) == 2 * h:
                out[j - h: j + h] = a * np.cos(w * np.pi / 2) + bb * np.sin(w * np.pi / 2)
            self.SEAMS.append((o2 - self.S, f"原曲 {s1_ + l1:.2f}s → {s2_:.2f}s"))
        return out

    # ------------------------------------------------------------ 时间

    def tb(self, j, k):
        """第 j 屏第 k 拍的绝对秒（k 可为小数）。"""
        return self.b.t_of(j, k)

    def wt(self, li, ci=0, frac=0.0):
        """第 li 句第 ci 个分句（按“，”切）念到 frac（0–1）处的本地秒。"""
        ts = self.CLAUSE_T[li]
        a = ts[ci]
        z = ts[ci + 1] if ci + 1 < len(ts) else self.DUR_L[li]
        return self.STARTS[li] + a + (z - a) * frac

    def kb(self, j, t_local, lo=0, strong=False):
        """第 j 屏内离本地秒 t_local 最近的整数拍（不早于 lo；strong=True 只取小节第一拍）。"""
        b0, b1 = self.BOUNDS[j]
        T = self.S + t_local
        cands = [i for i in range(max(lo, 0), b1 - b0) if not strong or core.BEATS[b0 + i]["bar_pos"] == 0]
        return min(cands, key=lambda i: abs(core.BEATS[b0 + i]["t"] - T))

    @staticmethod
    def beat_pos(T):
        """绝对秒 T 换成连续拍号（可做按拍转动、走路相位）。"""
        bt_ = core._BEAT_T
        i = int(np.clip(np.searchsorted(bt_, T, side="right") - 1, 0, len(bt_) - 2))
        return i + (T - bt_[i]) / (bt_[i + 1] - bt_[i])

    def drop_k(self):
        """drop 在 drop_screen 屏内的拍号。"""
        return self.DROP - self.BOUNDS[self.drop_screen][0]

    # ------------------------------------------------------------ 白板项（返回给 b.custom 的绘制函数）

    def pop_text(self, s, x, y, size, color, j, k, font="hand"):
        """第 j 屏第 k 拍弹出一行字。"""
        self.TEXTS.append(s)

        def fn(c, kk, T):
            sc = pop_scale(T - self.tb(j, k))
            if sc > 0:
                with K.at(c, x, y, 0, sc):
                    K.text(c, s, 0, 0, size, font, color, clamp01(sc * 2))
            return None
        return fn

    def slam_text(self, s, x, y, size, color, j, k, font="hand", rot=0.0):
        """第 j 屏第 k 拍砸下一行字（配 kick / rim 与震屏）。"""
        self.TEXTS.append(s)

        def fn(c, kk, T):
            sc = slam_scale(T - self.tb(j, k))
            if sc > 0:
                with K.at(c, x, y, rot, sc):
                    K.text(c, s, 0, 0, size, font, color, clamp01((T - self.tb(j, k)) / 0.06))
            return None
        return fn

    def stamp(self, s, x, y, size, j, k, color=RED, rot=-8.0):
        """印章：红框 + 字，第 j 屏第 k 拍砸下。"""
        self.TEXTS.append(s)
        w = K.text_w(s, size, "hand") + size * 0.8
        h = size * 1.45

        def fn(c, kk, T):
            dt = T - self.tb(j, k)
            sc = slam_scale(dt)
            if sc <= 0:
                return None
            a = clamp01(dt / 0.06)
            with K.at(c, x, y, rot, sc):
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 14, 14, K.paint("#FFFFFF", 0.85 * a))
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 14, 14, wb.marker(color, 10, a))
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 12, -h / 2 + 12, w - 24, h - 24), 8, 8, wb.marker(color, 4, a))
                K.text(c, s, 0, 0, size, "hand", color, a)
            return None
        return fn

    def pop_path(self, path, x, y, color, width, j, k, fill=None):
        """第 j 屏第 k 拍以 (x, y) 为中心弹出一条路径（可填色）。"""
        def fn(c, kk, T):
            sc = pop_scale(T - self.tb(j, k))
            if sc > 0:
                with K.at(c, x, y, 0, sc):
                    c.translate(-x, -y)
                    if fill:
                        c.drawPath(path, K.paint(fill))
                    c.drawPath(path, wb.marker(color, width))
            return None
        return fn

    def pop_bubble(self, s, x, y, j, k, size=72, color=BLACK, tail=-1, w=None, h=None, until=None):
        """对话气泡（白底黑框，尾巴朝左下 tail=-1 / 右下 tail=1）+ 字；until=(j2, k2) 时到那一拍缩回消失。"""
        self.TEXTS.append(s)
        w = w or K.text_w(s, size, "hand") + 90
        h = h or size + 70

        def fn(c, kk, T):
            sc = pop_scale(T - self.tb(j, k))
            if until is not None:
                sc *= 1 - ease_in_out(clamp01((T - self.tb(*until)) / 0.25))
            if sc <= 0:
                return None
            with K.at(c, x, y, 0, sc):
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 40, 40, K.paint("#FFFFFF"))
                c.drawPath(wb.bubble(0, 0, w, h, tail), wb.marker(BLACK, 7))
                K.text(c, s, 0, 0, size, "hand", color)
            return None
        return fn

    def note(self, *texts):
        """自己写的绘制函数里画了字时，用它登记，--sheet 的文案检查会一并检查。"""
        self.TEXTS.extend(texts)

    def figure(self, draw, j, k, x, y, s, **kw):
        """第 j 屏第 k 拍弹出一个人物：draw 为 draw_li / draw_worker / draw_boss / draw_ohno 等；kw 可以是常量或 fn(T)。"""
        def fn(c, kk, T):
            sc = pop_scale(T - self.tb(j, k))
            if sc <= 0:
                return None
            args = {a: (v(T) if callable(v) else v) for a, v in kw.items()}
            with K.at(c, x, y, 0, sc):
                c.translate(-x, -y)
                draw(c, x, y, s, **args)
            return None
        return fn

    # ------------------------------------------------------------ 分镜

    def scene(self, j, view, bars=4):
        """新开第 j 屏（按 SCREENS 顺序），view=(cx, cy, z)。返回 j。"""
        jj = self.b.shot("", self.SCREENS[j][1], view=view, bars=bars)
        assert jj == j, (jj, j)
        return j

    @staticmethod
    def intro_view(cx, cy):
        return cx, cy - 40, 0.7

    def intro(self, j, cx, cy, sub="精益制造的14项原则"):
        """第 0 屏开场：按 THEME["hook"] 画本讲的痛点钩子（fengtian/hooks.py）；hook="title" 时为旧版“丰田模式”四字。"""
        hook = self.THEME.get("hook", "title")
        if hook != "title":
            from fengtian import hooks
            return hooks.HOOKS[hook](self, j, cx, cy, self.ACC)
        return self.intro_title(j, cx, cy, sub)

    def intro_title(self, j, cx, cy, sub="精益制造的14项原则"):
        """旧版系列开场（第 0 屏）：“丰田模式”四个大字逐拍落下（rim / clap / tom / kick），第四字轻震，画下划线，弹出副标。
        与第 01 讲一致；四字落定后停到 intro_beats 拍，再用 1.3 秒缓推到第 1 屏。"""
        b = self.b
        xs = [cx - 420 + 280 * i for i in range(4)]
        y = cy - 70

        def char(ch, x, k):
            def fn(c, kk, T):
                dt = T - self.tb(j, k)
                if dt < 0:
                    return None
                sc = lerp(1.5, 1.0, ease_out(clamp01(dt / 0.14))) if dt < 0.14 else \
                    1.0 + 0.04 * math.exp(-(dt - 0.14) * 7) * math.sin((dt - 0.14) * 22)
                sc *= 1 + 0.012 * math.sin((T - self.tb(j, 4)) * 2.6) if T > self.tb(j, 4) else 1
                with K.at(c, x, y, 0, sc):
                    K.text(c, ch, 0, 0, 250, "hand", RED, clamp01(dt / 0.08))
                return None
            return fn

        for i, (ch, x, sfx) in enumerate(zip("丰田模式", xs, ("rim", "clap", "tom", "kick"))):
            b.custom(j, i, i + 0.3, char(ch, x, i), sfx=sfx, gain=(0.8, 0.8, 0.8, 0.7)[i])
        b.shots[j].shake = [(3, 7.0)]
        b.path(j, 3.4, 4.6, wb.underline(cx - 520, cx + 520, cy + 100, 16, 50), RED, 12)
        b.custom(j, 4, 4.3, self.pop_text(sub, cx, cy + 210, 66, BLACK, j, 4, "sans_medium"), sfx="pop", gain=0.6)

    def camera(self, board, T):
        """切屏：从上一屏的终了视角按本讲转场（THEME["move"]，MOVE_S 秒）移到本屏视角；屏内 board.move 运镜；强拍震屏；
        全程极慢推近 1.2%。"""
        ep_ = board.ep
        j_ = ep_.shot_at(T)
        s_ = ep_.shots[j_]
        t_ = T - s_.t0
        cur = board.views[j_]
        prev = board.end_view(j_ - 1) if j_ > 0 else cur

        def mix(a, z, k):
            return lerp(a[0], z[0], k), lerp(a[1], z[1], k), math.exp(lerp(math.log(a[2]), math.log(z[2]), k))

        style = self.THEME.get("move", "ease")
        if style == "wipe" and j_ > 0 and self.GROUP[j_] == self.GROUP[j_ - 1]:
            style = "ease"                       # 同一区块内不翻页，照常缓移
        view, _ = FT.transition(prev, cur, t_, style, self.MOVE_S, j_)
        for kb_, target, dur in board.moves.get(j_, []):
            t0_ = board.t_of(j_, kb_)
            if T < t0_:
                break
            view = mix(view, target, ease_in_out(clamp01((T - t0_) / dur)))
        cx, cy, z = view
        z *= 1 + 0.012 * clamp01(t_ / max(0.1, s_.t1 - s_.t0))
        sx = sy = 0.0
        for it in s_.shake:
            kb_, amp = it if isinstance(it, tuple) else (it, 14.0)
            dt = T - core.bt(s_.b0 + kb_)
            if 0 <= dt < 0.3:
                a = amp * math.exp(-dt * 14)
                sx += a * math.sin(dt * 90)
                sy += a * math.cos(dt * 77)
        return cx, cy, z, sx, sy

    # ------------------------------------------------------------ 收尾

    def finish(self, cover_shot, square_shot=None, notes=()):
        """所有屏画完后调用：构造 Episode，按排期写入每屏起止，挂到白板。cover_shot / square_shot 为封面取景屏。"""
        b = self.b
        if len(b.shots) != len(self.SCREENS):
            raise ValueError(f"画了 {len(b.shots)} 屏，SCREENS 有 {len(self.SCREENS)} 屏")
        self.COVER_SHOT = cover_shot
        self.SQUARE_SHOT = cover_shot if square_shot is None else square_shot
        self.NOTES = list(notes)
        ep = core.Episode(self.NO, self.KEY, self.CONCEPT, self.TITLE, self.ACC, b.shots, refs=[],
                          publish_title=f"Vibe知识大赏｜{self.TITLE}", hashtags=self.TAGS, cover_title=self.COVER_TITLE,
                          cover_sub=f"丰田模式 · {self.CONCEPT}", cover_shot=cover_shot, notes=self.NOTES)
        for s, (k0, k1) in zip(b.shots, self.BOUNDS):
            s.b0, s.t0, s.t1 = k0, core.bt(k0), core.bt(k1)
            s.bars = (k1 - k0) // 4 + 2          # 名义小节数盖住全部实测拍（Board.t_of 超出名义长度会外推）
        b.shots[0].t0 = self.S
        b.shots[-1].t1 = self.S + self.END_LOCAL
        b.attach(ep)
        self.ep = ep
        return ep

    def char_time(self, li, idx):
        """第 li 句第 idx 个字（不计标点）的本地时刻：按分句起点与分句内字数比例换算。"""
        text = self.LINES[li][0].rstrip(_PUNCT)
        ts = self.CLAUSE_T[li]
        n = 0
        for ci, cl in enumerate(text.split("，")):
            chars = [ch for ch in cl if ch not in _PUNCT]
            if idx < n + len(chars):
                a = ts[ci]
                z = (ts[ci + 1] - self.COMMA) if ci + 1 < len(ts) else self.DUR_L[li]
                return self.STARTS[li] + a + (z - a) * (idx - n) / max(1, len(chars))
            n += len(chars)
        return self.STARTS[li] + self.DUR_L[li]

    def captions(self):
        """字幕表 [(起, 止, 文本)]：每句的字幕段按字的位置换算出现时刻，持续到下一段出现。"""
        caps = []
        for li, (text, pieces, _) in enumerate(self.LINES):
            plain = [ch for ch in text if ch not in _PUNCT]
            idx = 0
            for cap in pieces:
                body = [ch for ch in cap if ch not in _PUNCT + "【】"]
                if plain[idx: idx + len(body)] != body:
                    raise ValueError(f"字幕与旁白不一致：{text} / {cap}")
                caps.append([self.char_time(li, idx), None, cap.rstrip("，。；：")])
                idx += len(body)
            if idx != len(plain):
                raise ValueError(f"字幕没有覆盖整句：{text}")
        for i, cp in enumerate(caps):
            cp[1] = caps[i + 1][0] if i + 1 < len(caps) else None
        return caps

    EXPORTS = ("NO", "KEY", "CONCEPT", "TITLE", "TAGS", "COVER_TITLE", "ACC", "LINES", "LINE_MOOD", "PINYIN", "SCREENS",
               "GROUP", "RAW", "CLIPS", "CLAUSE_T", "DUR_L", "BOUNDS", "STARTS", "S", "END_LOCAL", "DROP", "SEAMS", "b", "ep",
               "COVER_SHOT", "SQUARE_SHOT", "NOTES", "TEXTS", "THEME", "MOVE_S")

    def export(self, ns):
        """把 build.py 需要的名字写进分镜模块的 globals()（SEAMS 是同一个列表，music_track 运行后填充）。"""
        if self.ep is None:
            raise RuntimeError("先调用 finish()")
        for name in self.EXPORTS:
            ns[name] = getattr(self, name)
        ns["SCREEN_TEXTS"] = self.TEXTS
        ns["captions"] = self.captions
        ns["music_track"] = self.music_track
        ns["build"] = lambda: self.ep
        ns["L"] = self
