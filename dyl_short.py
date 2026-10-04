"""《设计你的人生》竖屏短视频：第二人称代入的情绪叙事 + 3D Emoji 人物 + 动效 + 配乐音效。

叙事线：标准答案人生的痛点 → 面具与深夜自问 → 转折遇见斯坦福课程 → 重新定义问题
→ 三个方法（好时光日志 / 奥德赛计划 / 最小原型）各配真实场景 → 情绪高潮 → 互动引导。

用法：python3 dyl_short.py [输出路径]       生成视频与封面
依赖资源：python3 fetch_assets.py
"""

import math
import sys
from pathlib import Path

import numpy as np
import skia

from engine.gfx import (W, H, aurora, battery, bubble, check, chip, circle, clamp01, confetti, draw_emoji,
                        draw_kinetic, draw_text, dust, ease_in, ease_in_out, ease_out, ease_out_back,
                        gradient_bg, lerp, light_rays, mix, plain, prog, rrect, shockwave, sparkles,
                        stroke_path, text_width, vignette, warp)
from engine.timeline import Event, Line, Scene, Video

ST = dict(stroke=("#0A0A18", 12), shadow=(0, 8, 12, "#000000"))
GOLD = dict(stroke=("#3A0A1E", 14), glow=("#FF8A3D", 40), gradient=["#FFFFFF", "#FFE45C"],
            shadow=(0, 10, 14, "#000000"))

PALETTES = {
    "night": dict(bg=["#05081A", "#0E1235", "#221650"], blobs=["#3A2E8F", "#1B4B8F", "#5A2A7A"],
                  dust="#9FC2FF", hi="#7FD8FF", aurora=0.28, vignette=0.55),
    "dusk": dict(bg=["#101A44", "#2C2766", "#5B3A7A"], blobs=["#6E4BC4", "#C2588A", "#2E6FB0"],
                 dust="#FFE3A3", hi="#FFE14D", aurora=0.3),
    "cold": dict(bg=["#07080C", "#14161D", "#22252F"], blobs=["#2C3140", "#3A3F52", "#1F2430"],
                 dust="#8A93A6", hi="#9FC8F0", aurora=0.25, vignette=0.65, dust_a=0.35),
    "black": dict(bg=["#000000", "#03030A", "#08081A"], blobs=["#101030", "#0A0A20", "#181040"],
                  dust="#FFFFFF", hi="#FFE14D", aurora=0.12, dust_a=0.2),
    "dawn": dict(bg=["#2A0F5C", "#B23A6E", "#FF8A4C"], blobs=["#FF5E7E", "#FFB347", "#8A4FFF"],
                 dust="#FFF1C1", hi="#FFE45C", aurora=0.35),
    "sky": dict(bg=["#0A1A4F", "#1E3F9A", "#3B76D9"], blobs=["#4CC9F0", "#7B5CFF", "#2A9DF4"],
                dust="#CFE8FF", hi="#FFE14D", aurora=0.3),
    "teal": dict(bg=["#04232A", "#0A4F55", "#0E8A72"], blobs=["#13C29A", "#1A7FB8", "#6BE38F"],
                 dust="#B8FFE0", hi="#7CFFB2"),
    "violet": dict(bg=["#120C38", "#2D1D7A", "#5B37B8"], blobs=["#8A5CFF", "#FF6FB5", "#3E7BFA"],
                   dust="#E2D6FF", hi="#FFD86B"),
    "amber": dict(bg=["#220B08", "#6A2516", "#C45A2A"], blobs=["#FF8C42", "#FF5E5B", "#FFC15E"],
                  dust="#FFE7C2", hi="#FFE08A"),
    "gold": dict(bg=["#1E0F3C", "#7A2E6A", "#F08A4B"], blobs=["#FFB347", "#FF6F91", "#FFD56B"],
                 dust="#FFF3C4", hi="#FFF1A8", aurora=0.35),
}


# ---------------------------------------------------------------- 通用动画元件

def w(x, i: int, word: str) -> float:
    """第 i 句读到 word 的估计时刻。"""
    idx = plain(x.s.lines[i].text).find(word)
    if idx < 0:
        raise ValueError(f"'{word}' not in line {i} of scene {x.s.name}")
    return x.at(i, idx)


def life(t: float, start: float, end: float | None = None, dur: float = 0.35) -> tuple[float, float]:
    """通用元素生命周期：返回 (透明度, 缩放)，入场弹出、退场淡出。"""
    if t < start:
        return 0.0, 0.0
    p = prog(t, start, dur)
    a, s = clamp01(p * 3), ease_out_back(p, 2.0)
    if end is not None:
        q = prog(t, end, 0.25)
        a *= 1 - q
        s *= 1 - 0.5 * ease_in(q)
    return a, s


def emo(x, name: str, px: float, py: float, size: float, start: float, end: float | None = None,
        enter: str = "pop", bob: float = 8.0, rot: float = 0.0, wiggle: float = 0.0, gray: float = 0.0,
        glow=None, shadow: float = 0.3, alpha: float = 1.0):
    """带入场（pop/drop/rise/left/right/fade）、待机浮动摆动与退场的 Emoji 角色。"""
    t = x.t
    if t < start:
        return
    p = prog(t, start, 0.45)
    s, dx, dy, a = 1.0, 0.0, 0.0, clamp01(p * 3)
    if enter == "pop":
        s = ease_out_back(p, 2.2)
    elif enter == "drop":
        dy = -(1 - ease_out_back(p, 1.2)) * 600
    elif enter == "rise":
        dy = (1 - ease_out(p)) * 500
    elif enter == "left":
        dx = -(1 - ease_out(p)) * 800
    elif enter == "right":
        dx = (1 - ease_out(p)) * 800
    elif enter == "fade":
        a = p
    if end is not None:
        q = prog(t, end, 0.25)
        if q >= 1:
            return
        s *= 1 - 0.6 * ease_in(q)
        a *= 1 - q
    idle = math.sin((t - start) * 2.4 + px * 0.013) * bob
    r = rot + wiggle * math.sin((t - start) * 3.1)
    draw_emoji(x.c, name, px + dx, py + dy + idle, size * s, a * alpha, r, gray=gray, glow=glow, shadow=shadow)


def stamp(c, text: str, px: float, py: float, size: float, p: float, color="#FF3B4E", rot: float = -10,
          alpha: float = 1.0):
    """砸下的印章字样。"""
    if p <= 0 or alpha <= 0:
        return
    s = 1 + 1.4 * (1 - ease_out(p))
    a = clamp01(p * 3) * alpha
    bw = text_width(text, size, "black") + size
    bh = size * 1.6
    c.save()
    c.translate(px, py)
    c.rotate(rot)
    c.scale(s, s)
    rrect(c, 0, 0, bw, bh, 14, None, a, stroke=(color, 8))
    rrect(c, 0, 0, bw - 22, bh - 22, 8, None, a * 0.8, stroke=(color, 3))
    draw_text(c, text, 0, 0, size, "black", color, a)
    c.restore()


def _zigzag(cx: float, cy: float, extent: float, side: int) -> skia.Path:
    """以竖向锯齿线为界的半平面，用于撕裂效果。"""
    path = skia.Path()
    path.moveTo(cx + side * 2000, cy - extent)
    k = 0
    y = cy - extent
    while y <= cy + extent:
        path.lineTo(cx + (18 if k % 2 else -18), y)
        y += 46
        k += 1
    path.lineTo(cx + side * 2000, cy + extent)
    path.close()
    return path


def torn(c, draw, cx: float, cy: float, f: float, extent: float = 700, spread: float = 300,
         fall: float = 1500, spin: float = 24):
    """把 draw() 画出的内容沿锯齿线撕成两半向两侧飞落；f 为撕开后经过的秒数。"""
    k = ease_out(min(max(f, 0) / 0.8, 1))
    a = 1 - prog(f, 0.6, 0.5)
    if a <= 0:
        return
    for side in (-1, 1):
        c.save()
        c.translate(cx + side * (24 + spread * k), cy + fall * max(f, 0) ** 2)
        c.rotate(side * spin * k)
        c.translate(-cx, -cy)
        c.clipPath(_zigzag(cx, cy, extent, side), skia.ClipOp.kIntersect, True)
        c.saveLayerAlpha(None, int(255 * a))
        draw()
        c.restore()
        c.restore()


def tool_title(x, num: str, title: str, en: str, emoji: str, end: float):
    """方法标题卡：大号序号砸入 + 标题逐字弹出 + 英文副标题 + 图标。"""
    c, t = x.c, x.t
    if t > end + 0.3:
        return
    a = 1 - prog(t, end, 0.25)
    acc = x.pal["hi"]
    draw_kinetic(c, num, 290, 560, 320, t, 0.0, "title", "slam", 0.08, 0.3, fill=acc, alpha=a,
                 stroke=("#0A0A18", 14), glow=(acc, 30))
    draw_kinetic(c, title, 540, 800, 132, t, x.cue(0) + 0.1, "title", "pop", 0.06, 0.4, alpha=a, **ST)
    draw_text(c, en, 540, 915, 46, "bold", acc, a * prog(t, x.cue(0) + 0.5, 0.4), stroke=("#0A0A18", 6))
    emo(x, emoji, 800, 540, 240, x.cue(0) + 0.2, end, wiggle=8)


def cubic(p0, p1, p2, p3, u: float) -> tuple[float, float]:
    v = 1 - u
    return (v ** 3 * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u ** 3 * p3[0],
            v ** 3 * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u ** 3 * p3[1])


def cubic_path(p0, p1, p2, p3) -> skia.Path:
    path = skia.Path()
    path.moveTo(*p0)
    path.cubicTo(*p1, *p2, *p3)
    return path


def steam(c, t: float, bx: float, by: float, alpha: float = 1.0):
    """碗或杯子上方袅袅升起的热气。"""
    for k in range(3):
        path = skia.Path()
        for j in range(12):
            yy = by - j * 14
            xx = bx + (k - 1) * 28 + 10 * math.sin(yy * 0.05 + t * 4 + k)
            path.lineTo(xx, yy) if j else path.moveTo(xx, yy)
        ph = (t * 0.8 + k * 0.33) % 1
        stroke_path(c, path, "#FFFFFF", 7, alpha * 0.45 * (1 - ph), glow=("#FFFFFF", 6))


# ---------------------------------------------------------------- 场景 1：钩子

def s_hook(x):
    c, t = x.c, x.t
    lift = ease_in_out(x.p(1, -0.15, 0.5))
    sz = lerp(205, 118, lift)
    y1, y2 = lerp(640, 300, lift), lerp(860, 430, lift)
    hook = dict(stroke=("#0A0A18", 14), glow=("#FF3D6E", 30), shadow=(0, 10, 12, "#000000"))
    t2 = w(x, 0, "也")
    draw_kinetic(c, "你是不是", 540, y1, sz, t, x.cue(0), "title", "slam", 0.06, 0.28, **hook)
    draw_kinetic(c, "也这样？", 540, y2, sz, t, t2, "title", "slam", 0.06, 0.28, **hook)
    shockwave(c, 540, 640, prog(t, x.cue(0) + 0.1, 0.7), "#FF7A9C", 650)
    shockwave(c, 540, 860, prog(t, t2 + 0.1, 0.7), "#FF7A9C", 650)
    ta = w(x, 1, "标准答案")
    emo(x, "Hundred points", 540, 860, 400, ta - 0.2, x.cue(2) - 0.05, wiggle=6)
    stamp(c, "标准答案", 540, 1100, 70, prog(t, ta + 0.25, 0.3), alpha=1 - prog(t, x.cue(2) - 0.05, 0.25))
    emo(x, "Smiling face with tear", 540, 900, 460, x.cue(2), enter="rise", bob=5, glow=("#7FD8FF", 30))


# ---------------------------------------------------------------- 场景 2：标准答案的人生流水线

MILESTONES = [("Books", 0.2), ("Graduation cap", 0.4), ("Briefcase", 0.6), ("House", 0.8)]


def s_track(x):
    c, t = x.c, x.t
    keys = [(x.cue(0), 0.2), (x.cue(1), 0.4), (x.cue(2), 0.6), (w(x, 3, "买房"), 0.8),
            (w(x, 3, "成家"), 0.88), (w(x, 3, "升职"), 0.95), (w(x, 4, "挺好"), 1.0)]
    v = 0.04
    for tk, val in keys:
        v = lerp(v, val, ease_out(prog(t, tk, 0.5)))
    ab = prog(t, 0, 0.4)
    draw_text(c, "人生进度", 120, 285, 42, "black", "#FFFFFF", ab, "left", stroke=("#0A0A18", 6))
    draw_text(c, f"{int(round(v * 100))}%", 960, 280, 64, "title", x.pal["hi"], ab, "right", stroke=("#0A0A18", 8))
    rrect(c, 540, 360, 840, 36, 18, "#FFFFFF", ab * 0.18)
    rrect(c, 120 + 420 * v, 360, 840 * v, 36, 18, alpha=ab, gradient=["#FFE14D", "#FF8A3D"])
    circle(c, 120 + 840 * v, 360, 26, "#FFE14D", ab * 0.7, blur=16, blend=skia.BlendMode.kPlus)
    for (name, pos), tk in zip(MILESTONES, (keys[0][0], keys[1][0], keys[2][0], keys[3][0])):
        mx = 120 + 840 * pos
        hit = t >= tk + 0.45
        draw_emoji(c, name, mx, 445, 78, ab * (1 if hit else 0.45), gray=0 if hit else 0.85, shadow=0)
        if hit:
            circle(c, mx + 32, 412, 17, "#3BE07A", ab)
            check(c, mx + 32, 412, 20, prog(t, tk + 0.45, 0.3), "#FFFFFF", 5, ab)

    e0, e1, e2, e3 = (x.cue(k) - 0.1 for k in (1, 2, 3, 4))
    emo(x, "Student", 540, 930, 380, x.cue(0) - 0.1, e0, bob=10)
    for k in range(3):
        emo(x, "Books", 805, 1090 - k * 72, 170, x.cue(0) + 0.05 + k * 0.22, e0, enter="drop", bob=0)
    emo(x, "Alarm clock", 280, 760, 170, x.cue(0), e0, bob=0, rot=12 * math.sin(t * 38))

    if x.cue(1) - 0.1 <= t < e1 + 0.3:
        jump = math.sin(math.pi * prog(t, x.cue(1) + 0.1, 0.6)) * 90
        emo(x, "Student", 540, 990 - jump, 360, x.cue(1) - 0.1, e1, enter="fade", bob=0)
        pc = ease_out(prog(t, x.cue(1) + 0.15, 0.7))
        emo(x, "Graduation cap", 540, lerp(880, 560, pc), 220, x.cue(1) + 0.1, e1, enter="fade", bob=0, rot=720 * pc)
        confetti(c, 540, 600, t - (x.cue(1) + 0.6), 80, seed=4)

    rise = ease_out(prog(t, x.cue(2), 0.6))
    if x.cue(2) - 0.1 <= t < e2 + 0.3:
        draw_emoji(c, "Office building", 770, 900 + (1 - rise) * 600, 380, 1 - prog(t, e2, 0.25))
    emo(x, "Office worker", 360, 960, 360, x.cue(2) - 0.1, e2, enter="left", bob=6)
    a, s = life(t, w(x, 2, "体面"), e2)
    chip(c, 540, 1200, "体面 · 稳定", 46, alpha=a, scale=s, emoji="Sparkles")

    for k, (name, word) in enumerate((("House", "买房"), ("Ring", "成家"), ("Chart increasing", "升职"))):
        tk = w(x, 3, word)
        emo(x, name, 270 + k * 270, 900, 230, tk - 0.05, e3, bob=6)
        a, s = life(t, tk + 0.25, e3)
        draw_emoji(c, "Check mark button", 270 + k * 270 + 88, 800, 92 * s, a, shadow=0)

    emo(x, "Smiling face with smiling eyes", 540, 930, 400, x.cue(4) - 0.1, bob=6)
    emo(x, "Thumbs up", 210, 1100, 190, x.cue(4) + 0.2, enter="left", wiggle=10)
    emo(x, "Clapping hands", 820, 1100, 180, x.cue(4) + 0.35, enter="right", wiggle=10)
    for k, (txt, bx, by, tail) in enumerate((("人生赢家！", 290, 620, "right"), ("真羡慕你", 790, 660, "left"),
                                             ("别人家的孩子", 540, 470, "down"))):
        a, s = life(t, x.cue(4) + 0.3 + k * 0.35)
        bubble(c, bx, by, txt, 42, a, s, tail=tail)


# ---------------------------------------------------------------- 场景 3：笑容面具碎裂

def _cracks(cx: float, cy: float, r: float) -> list[skia.Path]:
    rng = np.random.default_rng(21)
    out = []
    for k in range(7):
        ang = k * 2 * math.pi / 7 + rng.uniform(-0.3, 0.3)
        path = skia.Path()
        path.moveTo(cx + rng.uniform(-0.05, 0.05) * r, cy + rng.uniform(-0.05, 0.05) * r)
        for j in range(1, 6):
            d = r * j / 5 * 0.95
            a2 = ang + rng.uniform(-0.25, 0.25)
            path.lineTo(cx + d * math.cos(a2), cy + d * math.sin(a2))
        out.append(path)
    return out


def _smile_face(c, cx, cy, size, crack_p, gray):
    draw_emoji(c, "Smiling face with smiling eyes", cx, cy, size, 1.0, gray=gray)
    if crack_p > 0:
        for path in _cracks(cx, cy, size * 0.46):
            stroke_path(c, path, "#FFFFFF", 5, 0.95, crack_p, glow=("#BFE6FF", 6))


def s_mask(x):
    c, t = x.c, x.t
    cx, cy = 540, 860
    size = 520 * (1 + 0.06 * prog(t, 0, x.dur))
    t1, tf = w(x, 1, "笑容"), w(x, 1, "装")
    crack = 0.45 * ease_out(prog(t, t1, 0.5)) + 0.55 * ease_out(prog(t, tf - 0.35, 0.3))
    if t >= tf - 0.05:
        draw_emoji(c, "Pensive face", cx, cy, size, prog(t, tf, 0.6), gray=0.25)
    if t < tf:
        dx = 6 * math.sin(t * 60) * prog(t, tf - 0.35, 0.3)
        _smile_face(c, cx + dx, cy, size, crack, 0.35)
    else:
        torn(c, lambda: _smile_face(c, cx, cy, size, 1.0, 0.35), cx, cy, t - tf, extent=420, spread=260)


# ---------------------------------------------------------------- 场景 4：原地兜圈子 + 深夜自问

LOOP = [("Briefcase", "上班"), ("Metro", "下班"), ("Mobile phone", "刷手机"), ("Crescent moon", None)]


def s_night(x):
    c, t = x.c, x.t
    tb = x.cue(2) - 0.15
    if t < tb + 0.35:
        aw = 1 - prog(t, tb, 0.35)
        cx, cy, R = 540, 820, 280
        t1 = x.cue(1)
        th = 25 * t + (120 * (t - t1) ** 2 if t > t1 else 0)
        om = 25 + (240 * (t - t1) if t > t1 else 0)
        ring = skia.Path()
        ring.addCircle(cx, cy, R)
        stroke_path(c, ring, "#FFFFFF", 6, 0.25 * aw, dash=(26, 18, -th * 4))
        for k in range(4):
            ang = math.radians(th + k * 90 + 45)
            c.save()
            c.translate(cx + R * math.cos(ang), cy + R * math.sin(ang))
            c.rotate(math.degrees(ang) + 90)
            tri = skia.Path()
            tri.moveTo(14, 0)
            tri.lineTo(-10, -12)
            tri.lineTo(-10, 12)
            tri.close()
            c.drawPath(tri, skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(150 * aw))))
            c.restore()
        for k, (name, word) in enumerate(LOOP):
            st = w(x, 0, word) if word else x.end(0) - 0.1
            ang = math.radians(-90 + k * 90 + th)
            emo(x, name, cx + R * math.cos(ang), cy + R * math.sin(ang), 170, st, bob=0, alpha=aw)
            if t > t1 and t >= st:
                for j in range(1, 4):
                    aj = ang - math.radians(om * 0.025 * j)
                    draw_emoji(c, name, cx + R * math.cos(aj), cy + R * math.sin(aj), 170, aw * 0.22 / j, shadow=0)
        emo(x, "Face with spiral eyes", cx, cy, 230, x.cue(1) + 0.1, alpha=aw, wiggle=14)
    if t >= tb:
        ab = prog(t, tb, 0.4)
        sparkles(c, t, 540, 520, 1000, 640, 14, seed=8, alpha=ab * 0.8, size=18)
        draw_emoji(c, "Crescent moon", 850, 370, 190, ab, glow=("#FFF2B0", 30), shadow=0)
        clock = "02:17" if int(t * 2) % 2 == 0 else "02 17"
        draw_text(c, clock, 440, 380, 112, "title", "#9FE8FF", ab, glow=("#3FC8FF", 22), stroke=("#0A0A18", 8))
        emo(x, "Person in bed", 540, 1060, 470, tb, enter="fade", bob=2)
        emo(x, "Thought balloon", 560, 690, 470, x.cue(3), bob=6)
        draw_kinetic(c, "就这样了吗？", 560, 668, 54, t, x.cue(4) + 0.1, "black", "pop", 0.06, 0.3, fill="#1E2230")


def bg_night(x):
    tb = x.cue(2) - 0.15
    if x.t >= tb:
        flick = 0.22 + 0.08 * math.sin(x.t * 7) + 0.05 * math.sin(x.t * 23)
        circle(x.c, 600, 990, 330, "#4FA8FF", prog(x.t, tb, 0.4) * flick, blur=120, blend=skia.BlendMode.kPlus)


# ---------------------------------------------------------------- 场景 5：撕碎标准答案

def _paper(c, t, t0):
    rrect(c, 0, 0, 620, 780, 26, "#FBFBF7", 1.0, shadow=0.45)
    draw_text(c, "标准答案", 0, -300, 56, "black", "#1E2230")
    for r in range(5):
        y = -180 + r * 100
        rrect(c, -50, y, 380, 18, 9, "#D9DCE3")
        check(c, 210, y, 44, prog(t, t0 + 0.4 + r * 0.12, 0.25), "#FF3B4E", 9)
    c.save()
    c.translate(150, 290)
    c.rotate(-12)
    draw_text(c, "100", 0, 0, 150, "title", "#FF3B4E")
    c.restore()


def s_answer(x):
    c, t = x.c, x.t
    cx, cy = 540, 840
    tt = w(x, 1, "从来")
    if t >= tt + 0.2:
        draw_emoji(c, "Dotted line face", cx, cy, 420, 0.85 * prog(t, tt + 0.3, 0.8), gray=0.3)
    yin = (1 - ease_out(prog(t, 0, 0.6))) * 1200

    def paper():
        c.save()
        c.translate(cx, cy + yin)
        c.rotate(-4)
        _paper(c, t, 0)
        c.restore()

    if t < tt:
        paper()
        stamp(c, "标准答案", cx + 10, cy - 300 + yin, 50, prog(t, w(x, 0, "标准答案") + 0.1, 0.3), rot=-14)
    else:
        torn(c, paper, cx, cy, t - tt, extent=800)


# ---------------------------------------------------------------- 场景 6：转折

def s_turn0(x):
    c, t = x.c, x.t
    p = prog(t, 0, x.dur)
    warp(c, t, 540, 860, 0.2 + 0.8 * p * p)
    r = 30 + 520 * p ** 3
    circle(c, 540, 860, r, "#FFFFFF", 0.25 + 0.6 * p, blur=r * 0.6, blend=skia.BlendMode.kPlus)
    circle(c, 540, 860, 16 + 30 * p, "#FFFFFF", 0.95, blur=10, blend=skia.BlendMode.kPlus)
    c.save()
    c.translate(540, 1100)
    c.scale(1 + 0.12 * p, 1 + 0.12 * p)
    draw_kinetic(c, "直到我发现……", 0, 0, 96, t, x.cue(0), "title", "rise", 0.05, 0.4,
                 glow=("#FFFFFF", 16), stroke=("#000000", 8))
    c.restore()


def s_turn(x):
    c, t = x.c, x.t
    sparkles(c, t, 540, 800, 900, 900, 14, seed=12, alpha=0.9)
    e0 = x.cue(1) - 0.1
    emo(x, "Classical building", 540, 780, 330, 0.05, e0, enter="rise", glow=("#FFF3C4", 26), bob=4)
    a, s = life(t, 0.35, e0)
    chip(c, 540, 1010, "斯坦福大学 Stanford", 44, alpha=a, scale=s)
    tf = w(x, 0, "爆火")
    emo(x, "Fire", 820, 560, 170, tf - 0.05, e0, wiggle=8)
    a, s = life(t, tf, e0)
    if a > 0:
        c.save()
        c.translate(760, 690)
        c.rotate(-8)
        c.scale(s, s)
        draw_text(c, "爆火", 0, 0, 110, "title", "#FFE45C", a, stroke=("#C81E3A", 12), shadow=(0, 8, 10, "#000000"))
        c.restore()
    tt = w(x, 1, "设计")
    draw_kinetic(c, "设计你的人生", 540, 760, 170, t, tt - 0.1, "title", "slam", 0.07, 0.3, **GOLD)
    draw_text(c, "Designing Your Life", 540, 905, 52, "bold", "#FFF3C4", prog(t, tt + 0.5, 0.4),
              stroke=("#3A0A1E", 6))
    for k, (txt, emoji, yy, side) in enumerate((("斯坦福最受欢迎的课程之一", "Graduation cap", 1060, -1),
                                                ("纽约时报畅销书 No.1", "Open book", 1165, 1))):
        p = ease_out(prog(t, tt + 1.0 + 0.3 * k, 0.45))
        chip(c, 540 + side * (1 - p) * 760, yy, txt, 40, alpha=clamp01(p * 2), emoji=emoji)


def bg_turn(x):
    light_rays(x.c, 540, 780, x.t, "#FFE9A8", 0.22, 16)


# ---------------------------------------------------------------- 场景 7：重新定义问题

DOODLE_COLORS = ("#FF5E7E", "#3BCEAC", "#4CC9F0", "#FFB703", "#9B5DE5")


def _doodles() -> list[skia.Path]:
    paths = []
    sp = skia.Path()
    for j in range(60):
        a = j * 0.35
        r = 8 + j * 1.6
        px, py = -150 + r * math.cos(a), -120 + r * math.sin(a)
        sp.lineTo(px, py) if j else sp.moveTo(px, py)
    paths.append(sp)
    star = skia.Path()
    for k in range(11):
        ang = math.radians(-90 + k * 144)
        px, py = 140 + 90 * math.cos(ang), -130 + 90 * math.sin(ang)
        star.lineTo(px, py) if k else star.moveTo(px, py)
    paths.append(star)
    wave = skia.Path()
    for j in range(40):
        px = -230 + j * 12
        wave.lineTo(px, 60 + 30 * math.sin(j * 0.6)) if j else wave.moveTo(px, 60)
    paths.append(wave)
    house = skia.Path()
    for k, (px, py) in enumerate([(-170, 300), (-170, 190), (-100, 130), (-30, 190), (-30, 300), (-170, 300)]):
        house.lineTo(px, py) if k else house.moveTo(px, py)
    paths.append(house)
    heart = skia.Path()
    for j in range(64):
        a = j / 63 * math.tau
        px = 130 + 5.5 * 16 * math.sin(a) ** 3
        py = 230 - 5.5 * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        heart.lineTo(px, py) if j else heart.moveTo(px, py)
    paths.append(heart)
    return paths


def _exam_face(c):
    rrect(c, 0, 0, 560, 700, 26, "#FBFBF7", shadow=0.4)
    draw_text(c, "考  题", 0, -270, 56, "black", "#1E2230")
    for r in range(4):
        y = -150 + r * 95
        draw_text(c, f"{r + 1}.", -220, y, 36, "bold", "#8A90A2", align="left")
        rrect(c, 20, y, 360, 16, 8, "#D9DCE3")
    draw_text(c, "唯一正确答案：____", 0, 250, 38, "bold", "#C0392B")


def _sketch_face(c, t, t0):
    rrect(c, 0, 0, 560, 700, 26, "#FFF6E0", shadow=0.4)
    draw_text(c, "我的设计稿", 0, -280, 52, "title", "#FF7A3D")
    for k, path in enumerate(_doodles()):
        stroke_path(c, path, DOODLE_COLORS[k], 9, 1.0, ease_out(prog(t, t0 + 0.1 + k * 0.18, 0.7)))


def s_reframe(x):
    c, t = x.c, x.t
    ea = x.cue(2) - 0.1
    if t < ea + 0.3:
        aa = 1 - prog(t, ea, 0.3)
        tf = w(x, 1, "设计") - 0.25
        f = prog(t, tf, 0.5)
        sin_ = ease_out_back(prog(t, 0.05, 0.5))
        c.save()
        c.translate(540, 830)
        c.scale(max(abs(math.cos(math.pi * f)), 0.02) * sin_, sin_)
        if aa < 1:
            c.saveLayerAlpha(None, int(255 * aa))
        if f < 0.5:
            _exam_face(c)
        else:
            _sketch_face(c, t, tf + 0.25)
        if aa < 1:
            c.restore()
        c.restore()
        emo(x, "Artist palette", 270, 470, 170, tf + 0.5, ea, wiggle=10)
        emo(x, "Pencil", 820, 1190, 150, tf + 0.6, ea, wiggle=12)
        sparkles(c, t, 540, 830, 760, 860, 10, seed=13, alpha=aa * prog(t, tf + 0.5, 0.4))
    if t < ea:
        return
    emo(x, "Thinking face", 540, 560, 270, x.cue(2), wiggle=6)
    for k in range(3):
        a, s = life(t, x.cue(2) + 0.3 + k * 0.15)
        draw_text(c, "?", 300 + k * 240, 410 + 18 * math.sin(t * 3 + k), 120 * max(s, 0.01), "title", "#FFFFFF",
                  a * 0.85, stroke=("#0A0A18", 10))
    ts = w(x, 3, "人生") + 0.25
    a, s = life(t, x.cue(3))
    if a > 0:
        dim = 1 - 0.35 * prog(t, ts, 0.4)
        c.save()
        c.translate(540, 860)
        c.scale(s * (1 - 0.06 * prog(t, ts, 0.4)), s)
        rrect(c, 0, 0, 880, 170, 34, "#E9ECF5", a * dim, shadow=0.3)
        draw_text(c, "我该怎么找到正确的人生？", 0, 0, 46, "black", "#4A5068", a * dim)
        line = skia.Path()
        line.moveTo(-330, 0)
        line.lineTo(330, 0)
        stroke_path(c, line, "#FF3B4E", 9, a, ease_out(prog(t, ts, 0.35)))
        c.restore()
    emo(x, "Cross mark", 880, 790, 110, ts + 0.2, bob=0)
    a, s = life(t, x.cue(4))
    if a > 0:
        c.save()
        c.translate(540, 1110)
        c.scale(s, s)
        rrect(c, 0, 0, 880, 170, 34, alpha=a, gradient=["#FFF6B0", "#FFC94A"], shadow=0.35)
        draw_text(c, "我可以先试试哪几种可能？", 40, 0, 46, "black", "#3A2A00", a)
        c.restore()
    emo(x, "Light bulb", 165, 1100, 130, x.cue(4) + 0.15, bob=4, glow=("#FFE45C", 24 + 10 * math.sin(t * 5)))
    sparkles(c, t, 540, 1110, 900, 260, 8, seed=14, alpha=prog(t, w(x, 4, "可能"), 0.4))


def bg_reframe(x):
    a, _ = life(x.t, x.cue(4))
    if a > 0:
        circle(x.c, 540, 1110, 420, "#FFE45C", a * (0.12 + 0.1 * math.sin(x.t * 5)), blur=80,
               blend=skia.BlendMode.kPlus)


# ---------------------------------------------------------------- 场景 8：方法一 好时光日志

def _energy_row(c, y, emoji, text, level, status, a, s, dim=1.0):
    c.save()
    c.translate(540, y)
    c.scale(s, s)
    rrect(c, 0, 0, 880, 230, 36, "#FFFFFF", a * 0.14 * dim, stroke=("#FFFFFF", 2))
    draw_emoji(c, emoji, -320, 0, 170, a * dim, shadow=0)
    draw_text(c, text, -215, -48, 44, "black", "#FFFFFF", a * dim, "left", stroke=("#0A0A18", 6))
    battery(c, -55, 45, 320, 70, level, a * dim, bolt=level > 0.95)
    draw_emoji(c, status, 300, 0, 140, a * dim, shadow=0)
    c.restore()


def s_tool1(x):
    c, t = x.c, x.t
    tool_title(x, "01", "好时光日志", "Good Time Journal", "Memo", x.cue(1) - 0.1)
    sb, eb = x.cue(1) - 0.1, x.cue(2) - 0.1
    emo(x, "Memo", 540, 830, 380, sb, eb, wiggle=4)
    if sb <= t < eb + 0.3:
        emo(x, "Pencil", 650 + 60 * math.sin(t * 8), 760 + 30 * math.cos(t * 11), 150, sb + 0.2, eb, bob=0)
    emo(x, "Crescent moon", 830, 560, 150, sb + 0.2, eb, glow=("#FFF2B0", 20))
    a, s = life(t, w(x, 1, "两分钟") - 0.1, eb)
    chip(c, 540, 1130, "睡前 2 分钟", 46, alpha=a, scale=s, emoji="Alarm clock")

    ec = x.cue(3) - 0.1
    a, s = life(t, w(x, 2, "满电") - 0.1, ec)
    if a > 0:
        c.save()
        c.translate(300, 860)
        c.scale(s, s)
        battery(c, 0, 0, 300, 140, 0.25 + 0.75 * ((t * 0.7) % 1), a, bolt=True)
        c.restore()
        draw_text(c, "满电", 300, 1010, 76, "title", "#7CFFB2", a, stroke=("#0A0A18", 10))
    emo(x, "Star-struck", 300, 680, 150, w(x, 2, "满电"), ec, wiggle=8)
    a, s = life(t, w(x, 2, "掏空") - 0.1, ec)
    if a > 0:
        flick = 0.65 + 0.35 * (math.sin(t * 31) > -0.3)
        c.save()
        c.translate(780, 860)
        c.scale(s, s)
        battery(c, 0, 0, 300, 140, 1 - 0.95 * ((t * 0.7) % 1), a * flick)
        c.restore()
        draw_text(c, "掏空", 780, 1010, 76, "title", "#FF6B6B", a, stroke=("#0A0A18", 10))
    emo(x, "Melting face", 780, 680, 150, w(x, 2, "掏空"), ec, wiggle=6)

    if t < x.cue(3) - 0.1:
        return
    a1, s1 = life(t, x.cue(3) - 0.05)
    up = ease_out(prog(t, w(x, 3, "两眼") - 0.2, 1.0))
    _energy_row(c, 720, "Teacher", "给新人分享经验", 0.3 + 0.7 * up, "Star-struck", a1, s1)
    if up > 0.9:
        sparkles(c, t, 540, 720, 880, 230, 8, seed=16, alpha=a1)
    a2, s2 = life(t, x.cue(4) - 0.05)
    down = ease_out(prog(t, w(x, 4, "电量") - 0.2, 1.0))
    flick = 1.0 if down < 0.95 else 0.6 + 0.4 * (math.sin(t * 29) > 0)
    dim = 1 - 0.5 * prog(t, x.cue(5), 0.4)
    _energy_row(c, 1000, "Page facing up", "写周报 · 开没完的会", 0.9 - 0.84 * down, "Melting face",
                a2 * flick, s2, dim)
    if t >= x.cue(5) - 0.1:
        q = ease_out(prog(t, x.cue(5), 0.7))
        mx, my = lerp(980, 640, q), lerp(1260, 760, q)
        circle(c, mx - 30, my - 30, 120, "#FFFFFF", 0.12 * q, blur=30, blend=skia.BlendMode.kPlus)
        draw_emoji(c, "Magnifying glass tilted left", mx, my, 230, q)
        draw_kinetic(c, "满电时刻 = 热爱的线索", 540, 1200, 74, t, w(x, 5, "线索") - 0.3, "title", "pop", 0.04, 0.35,
                     fill=x.pal["hi"], glow=("#13C29A", 24), stroke=("#0A0A18", 10))


# ---------------------------------------------------------------- 场景 9：方法二 奥德赛计划

ROADS = [
    (((540, 1060), (540, 900), (220, 900), (220, 760)), (220, 640), "Chart increasing", "升职 · 带团队", "#FFD86B"),
    (((540, 1060), (540, 900), (540, 820), (540, 680)), (540, 560), "Teacher", "转行 · 做培训", "#4CC9F0"),
    (((540, 1060), (540, 900), (860, 900), (860, 760)), (860, 640), "Hot beverage", "开一家咖啡馆", "#FF6FB5"),
]


def s_tool2(x):
    c, t = x.c, x.t
    tool_title(x, "02", "奥德赛计划", "Odyssey Plans", "Compass", x.cue(1) - 0.1)
    if t < x.cue(1) - 0.1:
        return
    ab = prog(t, x.cue(1) - 0.1, 0.3)
    for k, (pts, (dx_, dy_), icon, label, colr) in enumerate(ROADS):
        path = cubic_path(*pts)
        stroke_path(c, path, "#FFFFFF", 22, 0.18 * ab, ease_out(prog(t, x.cue(1) + 0.2 + 0.15 * k, 0.9)),
                    dash=(30, 22, -t * 60))
        lk = w(x, 2 + k, "剧本")
        q = prog(t, lk, 0.7)
        if q > 0:
            stroke_path(c, path, colr, 14, 1.0, ease_out(q), glow=(colr, 16))
            for j in range(4):
                px, py = cubic(*pts, ((t * 0.45 + j / 4) % 1) * ease_out(q))
                circle(c, px, py, 9, "#FFFFFF", 0.9, blur=6, blend=skia.BlendMode.kPlus)
        emo(x, icon, dx_, dy_, 170, lk + 0.2, wiggle=6)
        a, s = life(t, lk)
        draw_text(c, f"剧本{'一二三'[k]}", dx_, dy_ - 128, 44 * max(s, 0.01), "title", colr, a, stroke=("#0A0A18", 8))
        a, s = life(t, lk + 0.35)
        chip(c, dx_, dy_ + 125, label, 34, alpha=a, scale=s)
    emo(x, "Person standing", 540, 1150, 300, x.cue(1) - 0.1, bob=4)
    tn, tsel = w(x, 5, "无路可走"), w(x, 5, "选择")
    a, s = life(t, tn - 0.1, tsel - 0.15)
    if a > 0:
        draw_text(c, "无路可走", 540, 300, 96 * max(s, 0.01), "title", "#C9C3E6", a, stroke=("#0A0A18", 10))
        line = skia.Path()
        line.moveTo(360, 300)
        line.lineTo(720, 300)
        stroke_path(c, line, "#FF3B4E", 10, a, ease_out(prog(t, tn + 0.5, 0.3)))
    draw_kinetic(c, "有了选择！", 540, 300, 124, t, tsel - 0.1, "title", "slam", 0.06, 0.3, **GOLD)
    confetti(c, 540, 1080, t - tsel, 90, seed=6)


# ---------------------------------------------------------------- 场景 10：方法三 最小原型

def _table(c, y: float, w_: float = 860):
    rrect(c, 540, y, w_, 46, 20, "#8B5A3C", shadow=0.35)
    rrect(c, 540, y - 17, w_, 14, 7, "#B07A52")


def s_tool3(x):
    c, t = x.c, x.t
    tool_title(x, "03", "最小原型", "Prototyping", "Test tube", x.cue(1) - 0.1)
    e = [x.cue(k) - 0.1 for k in range(1, 7)]

    if e[0] <= t < e[1] + 0.3:
        tz = w(x, 1, "辞职")
        run = ease_out(prog(t, x.cue(1), 1.2))
        back = ease_out(prog(t, tz, 0.4))
        px = lerp(150, 520, run) - 160 * back
        emo(x, "Person running", px, 1000, 300, e[0], e[1], enter="fade", bob=0, rot=6 * math.sin(t * 16))
        for j in range(4):
            ln = skia.Path()
            ln.moveTo(px - 320, 930 + j * 40)
            ln.lineTo(px - 200, 930 + j * 40)
            stroke_path(c, ln, "#FFFFFF", 6, 0.4 * (1 - back) * (1 - prog(t, e[1], 0.2)))
        a, _ = life(t, tz - 0.05, e[1])
        if a > 0:
            draw_emoji(c, "Stop sign", 640, 760, 330 * (1 + 1.2 * (1 - ease_out(prog(t, tz - 0.05, 0.3)))), a)
        draw_kinetic(c, "先别裸辞！", 540, 1180, 120, t, tz, "title", "slam", 0.06, 0.28, fill="#FFFFFF",
                     alpha=1 - prog(t, e[1], 0.25), stroke=("#B3001B", 14), shadow=(0, 8, 10, "#000000"))

    for label, start, end in (("原型对话 ①", e[1], e[2]), ("原型对话 ②", e[2], e[3]), ("原型体验", e[3], e[4])):
        a, s = life(t, start + 0.05, end)
        chip(c, 540, 320, label, 44, fill=x.pal["hi"], fg="#3A1A00", alpha=a, scale=s)

    if e[1] <= t < e[2] + 0.3:
        _table(c, 1110)
        emo(x, "Steaming bowl", 540, 1020, 190, e[1] + 0.1, e[2], bob=2)
        if t < e[2]:
            steam(c, t, 540, 930, prog(t, e[1] + 0.3, 0.5))
        emo(x, "Office worker", 230, 920, 270, e[1], e[2], enter="left", bob=5)
        emo(x, "Person with crown", 830, 920, 270, e[1] + 0.1, e[2], enter="right", bob=5)
        a, s = life(t, w(x, 2, "问问") - 0.1, e[2])
        bubble(c, 420, 620, "管理岗需要什么能力？", 40, a, s, tail="left")
        a, s = life(t, w(x, 2, "能力") + 0.2, e[2])
        bubble(c, 660, 745, "先学会带人和沟通", 38, a, s, tail="right", fill=x.pal["hi"])

    if e[2] <= t < e[3] + 0.3:
        _table(c, 1110, 620)
        emo(x, "Hot beverage", 430, 1030, 150, e[2] + 0.1, e[3], bob=2)
        emo(x, "Hot beverage", 650, 1030, 150, e[2] + 0.2, e[3], bob=2)
        if t < e[3]:
            steam(c, t, 430, 960, 0.8)
            steam(c, t, 650, 960, 0.8)
        emo(x, "Office worker", 220, 920, 260, e[2], e[3], enter="left", bob=5)
        emo(x, "Teacher", 840, 920, 260, e[2] + 0.1, e[3], enter="right", bob=5)
        a, s = life(t, w(x, 3, "咖啡") - 0.1, e[3])
        bubble(c, 400, 630, "做培训辛苦吗？", 40, a, s, tail="left")
        a, s = life(t, w(x, 3, "辛苦") - 0.1, e[3])
        bubble(c, 660, 750, "累，但很有成就感", 38, a, s, tail="right", fill=x.pal["hi"])

    if e[3] <= t < e[4] + 0.3:
        emo(x, "Cook", 540, 860, 340, e[3], e[4], bob=6)
        emo(x, "Hot beverage", 720, 1000, 140, e[3] + 0.2, e[4], bob=3)
        if t < e[4]:
            steam(c, t, 720, 930, 0.8)
        a, s = life(t, w(x, 4, "咖啡，") - 0.1, e[4])
        chip(c, 290, 1170, "咖啡", 44, alpha=a, scale=s, emoji="Hot beverage")
        a, s = life(t, w(x, 4, "还是") - 0.1, e[4])
        draw_text(c, "VS", 520, 1170, 80 * max(s, 0.01), "title", x.pal["hi"], a, stroke=("#0A0A18", 10))
        a, s = life(t, w(x, 4, "诗和远方") - 0.1, e[4])
        chip(c, 755, 1170, "诗和远方", 44, alpha=a, scale=s, emoji="National park")

    if t >= e[4]:
        emo(x, "Balance scale", 540, 620, 260, e[4] + 0.05, bob=4)
        a, s = life(t, e[4] + 0.1)
        draw_text(c, "小成本试错", 300, 820, 48 * max(s, 0.01), "black", "#7CFFB2", a, stroke=("#0A0A18", 8))
        for k, (txt, icon) in enumerate((("一顿饭", "Steaming bowl"), ("一杯咖啡", "Hot beverage"),
                                         ("一个周末", "Spiral calendar"))):
            a, s = life(t, w(x, 5, txt) - 0.05)
            chip(c, 300, 925 + k * 112, txt, 46, alpha=a, scale=s, emoji=icon)
        td = w(x, 6, "代价")
        a, s = life(t, td - 0.1)
        draw_text(c, "盲目裸辞", 780, 820, 48 * max(s, 0.01), "black", "#FF6B6B", a, stroke=("#0A0A18", 8))
        if t >= td:
            for k in range(3):
                fly = ((t - td) * 0.6 + k * 0.33) % 1
                draw_emoji(c, "Money with wings", 740 + 50 * k + 30 * math.sin(t * 3 + k), 1020 - 160 * fly, 120,
                           a * (1 - fly), shadow=0)
        a, s = life(t, td + 0.2)
        chip(c, 780, 1150, "时间 金钱 心态", 42, fill="#FF6B6B", fg="#FFFFFF", alpha=a, scale=s)


# ---------------------------------------------------------------- 场景 11：情绪高潮

BURST = [-168, -146, -124, -104, -84, -64, -44, -22, -6]


def s_climax(x):
    c, t = x.c, x.t
    tb = x.end(1) + 0.15
    dim = 1 - 0.65 * prog(t, x.cue(2) - 0.2, 0.6)
    oy = 990 + 60 * ease_in_out(prog(t, x.cue(2) - 0.2, 0.8))
    single = skia.Path()
    single.moveTo(540, oy)
    single.lineTo(540, oy - 620)
    stroke_path(c, single, "#FFFFFF", 10, 0.35 * dim * (1 - prog(t, tb, 0.4)))
    for k, ang in enumerate(BURST):
        q = prog(t, tb + k * 0.04, 0.6)
        if q <= 0:
            continue
        path = skia.Path()
        path.moveTo(540, oy)
        path.lineTo(540 + 1500 * math.cos(math.radians(ang)), oy + 1500 * math.sin(math.radians(ang)))
        colr = ("#FF5E7E", "#FFD23F", "#3BCEAC", "#4CC9F0", "#B388FF", "#FF9F1C")[k % 6]
        stroke_path(c, path, colr, 12, dim, ease_out(q), glow=(colr, 14))
    emo(x, "Person standing", 540, oy + 100, 340, 0.05, gray=0.85 * (1 - prog(t, tb, 0.8)), alpha=dim, bob=3)
    confetti(c, 540, oy, t - tb, 100, seed=7, power=1.1)
    draw_kinetic(c, "人生没有标准答案", 540, 430, 104, t, x.cue(2), "title", "rise", 0.05, 0.45, **ST)
    draw_kinetic(c, "但你，永远可以", 540, 610, 80, t, x.cue(3), "title", "rise", 0.04, 0.4, **ST)
    tr = w(x, 3, "重新设计")
    draw_kinetic(c, "重新设计它", 540, 800, 160, t, tr - 0.05, "title", "slam", 0.07, 0.3, **GOLD)
    sparkles(c, t, 540, 700, 900, 520, 12, seed=15, alpha=prog(t, tr, 0.5))


def bg_climax(x):
    t = x.t
    tb = x.end(1) + 0.15
    dim = 1 - 0.65 * prog(t, x.cue(2) - 0.2, 0.6)
    oy = 990 + 60 * ease_in_out(prog(t, x.cue(2) - 0.2, 0.8))
    circle(x.c, 540, oy + 110, 300 * ease_out(prog(t, tb, 0.8)), "#FFE9A8", 0.4 * dim, blur=90,
           blend=skia.BlendMode.kPlus)
    light_rays(x.c, 540, 760, t, "#FFE9A8", 0.25 * prog(t, x.cue(3), 0.6), 16)


# ---------------------------------------------------------------- 场景 12：互动引导

CHECKLIST = (("请老板吃顿饭", "Steaming bowl"), ("约朋友喝杯咖啡", "Hot beverage"), ("周末去打一天工", "Cook"))


def s_cta(x):
    c, t = x.c, x.t
    draw_kinetic(c, "从一个最小原型开始", 540, 470, 92, t, x.cue(0), "title", "pop", 0.05, 0.4, **ST)
    q = prog(t, w(x, 0, "开始") - 0.3, 1.6)
    if 0 < q < 1:
        ry = lerp(1300, -320, ease_in(q))
        rx = 540 + 30 * math.sin(q * 6)
        for j in range(12):
            circle(c, rx, ry + 110 + j * 38, 34 - j * 2, mix("#FFE45C", "#FF5E3A", j / 12), (1 - j / 12) * 0.75,
                   blur=14, blend=skia.BlendMode.kPlus)
        draw_emoji(c, "Rocket", rx, ry, 260, 1.0, rot=-45, shadow=0)
    a, s = life(t, x.cue(0) + 0.2, x.cue(1) - 0.1)
    if a > 0:
        c.save()
        c.translate(540, 870)
        c.scale(s, s)
        rrect(c, 0, 0, 780, 400, 40, "#FFFFFF", a * 0.96, shadow=0.35)
        draw_text(c, "本周原型清单", 0, -135, 46, "black", "#1E2230", a)
        for k, (txt, icon) in enumerate(CHECKLIST):
            y = -40 + k * 85
            rrect(c, -290, y, 50, 50, 12, None, a, stroke=("#9AA0B4", 4))
            check(c, -290, y, 40, prog(t, x.cue(0) + 0.6 + k * 0.45, 0.3), "#3BE07A", 9, a)
            draw_emoji(c, icon, -205, y, 64, a, shadow=0)
            draw_text(c, txt, -160, y, 40, "bold", "#1E2230", a, "left")
        c.restore()
    emo(x, "Speech balloon", 540, 870, 320, x.cue(1) - 0.05, bob=12)
    draw_kinetic(c, "评论区见", 540, 1100, 110, t, w(x, 1, "评论区") - 0.1, "title", "pop", 0.06, 0.35, **GOLD)
    a, s = life(t, w(x, 1, "告诉") - 0.1)
    draw_emoji(c, "Backhand index pointing down", 540, 1250 + 18 * abs(math.sin(t * 6)), 140 * s, a, shadow=0)
    if t >= x.cue(1):
        for j in range(7):
            ph = ((t - x.cue(1)) * 0.35 + j / 7) % 1
            draw_emoji(c, "Red heart" if j % 2 else "Star", 800 + 50 * math.sin(t * 2 + j), 1300 - ph * 900,
                       70, (1 - ph) * prog(t, x.cue(1), 0.4), shadow=0)


# ---------------------------------------------------------------- 剧本

def scene(name, palette, lines, draw, events=(), **kw) -> Scene:
    """events 元素为 (类型, 句序号, 关键词或 None, 偏移秒[, 增益[, 目标句]])，关键词定位到读到该词的时刻。"""
    evs = []
    for kind, i, word, off, *rest in events:
        char = plain(lines[i].text).find(word) if (word and i >= 0) else None
        if char is not None and char < 0:
            raise ValueError(f"'{word}' not in line {i} of scene {name}")
        evs.append(Event(kind, i, off, char, rest[0] if rest else 1.0, rest[1] if len(rest) > 1 else None))
    return Scene(name, lines, draw, palette, events=evs, **kw)


L = Line
SCENES = [
    scene("hook", "night", [
        L("你是不是也这样？", caption=False, pause=0.35),
        L("按【标准答案】活了三十年，", pause=0.12),
        L("却一点都【不快乐】。", speed=0.92, pause=0.55),
    ], s_hook, [("boom", 0, None, 0.0), ("boom", 0, "也", 0.0, 0.8), ("pop", 1, "标准答案", -0.2),
                ("boom", 1, "标准答案", 0.25, 0.5), ("swoosh", 2, None, -0.05), ("heart", 2, "快乐", 0.1)],
        lead=0.05),
    scene("track", "dusk", [
        L("从小拼命读书，", pause=0.12),
        L("考上一所好大学，", pause=0.12),
        L("找了一份体面的工作，", pause=0.12),
        L("然后买房、成家、升职加薪。", pause=0.2),
        L("在别人眼里，你的人生【挺好的】。", pause=0.35),
    ], s_track, [("whoosh", -1, None, 0.0), ("pop", 0, None, 0.05), ("pop", 0, None, 0.27), ("pop", 0, None, 0.49),
                 ("whoosh", 1, None, -0.35), ("shimmer", 1, "大学", 0.1), ("whoosh", 2, None, -0.35),
                 ("pop", 2, "体面", 0.0), ("ding", 3, "买房", 0.2, 0.6), ("ding", 3, "成家", 0.2, 0.6), ("ding", 3, "升职", 0.2, 0.6),
                 ("whoosh", 4, None, -0.35), ("pop", 4, None, 0.3), ("pop2", 4, None, 0.65), ("pop", 4, None, 1.0),
                 ("shimmer", 4, "挺好", 0.0)], transition="whip"),
    scene("mask", "cold", [
        L("可只有你自己知道，", speed=0.92, pause=0.45),
        L("那个笑容，是【装】出来的。", speed=0.9, pause=0.9),
    ], s_mask, [("heart", 0, None, 0.2), ("crack", 1, "笑容", 0.0), ("crack", 1, "装", -0.35),
                ("boom", 1, "装", 0.0, 0.6), ("heart", 1, "出来", 0.4)], lead=0.4),
    scene("night", "night", [
        L("每天上班、下班、刷手机，", pause=0.12),
        L("日子像在【原地兜圈子】。", pause=0.35),
        L("深夜躺在床上，", pause=0.15),
        L("你总忍不住问自己，", speed=0.94, pause=0.2),
        L("难道我的人生，【就这样了吗】？", speed=0.88, pause=0.9),
    ], s_night, [("pop", 0, "上班", 0.0), ("pop", 0, "下班", 0.0), ("pop", 0, "刷手机", 0.0), ("pop2", 1, None, 0.15),
                 ("whoosh", 1, "兜圈子", 0.6, 0.7), ("swoosh", 2, None, -0.15), ("pop", 3, None, 0.0),
                 ("glitch", 4, "就这样", 0.0), ("heart", 4, "了吗", 0.4)], transition="black", bg=bg_night),
    scene("answer", "cold", [
        L("我们拼命追求的【标准答案】，", pause=0.2),
        L("好像从来都不是【自己想要的】。", speed=0.9, pause=1.0),
    ], s_answer, [("whoosh", 0, None, -0.2), ("boom", 0, "标准答案", 0.1, 0.5), ("crack", 1, "从来", 0.0),
                  ("swoosh", 1, "从来", 0.05)], exit="black"),
    scene("turn0", "black", [
        L("直到我发现，", speed=0.98, pause=0.5, caption=False),
    ], s_turn0, [("riser", -1, None, 0.0, 0.9, -1)], lead=0.6),
    scene("turn", "dawn", [
        L("斯坦福有一门爆火的课，", pause=0.15),
        L("叫《【设计你的人生】》。", pause=0.7),
    ], s_turn, [("impact", -1, None, 0.0), ("pop", 0, "爆火", 0.0), ("whoosh", 1, None, -0.35),
                ("boom", 1, "设计", -0.1, 0.8), ("shimmer", 1, "人生", 0.2), ("pop2", 1, "人生", 0.9),
                ("pop2", 1, "人生", 1.2)], transition="flash", lead=0.2, bg=bg_turn),
    scene("reframe", "sky", [
        L("它告诉我，人生不是一道考题，", pause=0.15),
        L("而是一件可以不断修改的【设计作品】。", pause=0.35),
        L("你焦虑，是因为问错了问题。", pause=0.25),
        L("别再问，我该怎么找到【正确的人生】？", pause=0.2),
        L("试着问，我可以先试试【哪几种可能】？", pause=0.5),
    ], s_reframe, [("whoosh", -1, None, 0.0), ("swoosh", 1, "设计", -0.25), ("shimmer", 1, "作品", 0.0),
                   ("whoosh", 2, None, -0.35), ("pop2", 2, "问错", 0.0), ("pop", 3, None, 0.05),
                   ("buzz", 3, "人生", 0.4), ("pop", 4, None, 0.05), ("ding", 4, "可能", 0.0)], transition="whip",
        bg=bg_reframe),
    scene("tool1", "teal", [
        L("第一招，【好时光日志】。", pause=0.3),
        L("每天睡前花两分钟，记下今天做的事。", pause=0.2),
        L("哪件事让你满电？哪件事让你【掏空】？", pause=0.3),
        L("比如给新人分享经验时，你两眼放光；", pause=0.2),
        L("可一写周报、一开没完没了的会，电量直接【见底】。", pause=0.3),
        L("这些满电时刻，就是你热爱的【线索】。", pause=0.55),
    ], s_tool1, [("boom", -1, None, 0.0, 0.6), ("pop", 0, "好时光", 0.0), ("whoosh", 1, None, -0.35),
                 ("pop", 1, "两分钟", 0.0), ("whoosh", 2, None, -0.35), ("pop", 2, "满电", 0.0), ("down", 2, "掏空", 0.0),
                 ("whoosh", 3, None, -0.35), ("shimmer", 3, "两眼", 0.3), ("pop", 4, None, 0.0),
                 ("down", 4, "电量", 0.0), ("glitch", 4, "见底", 0.0), ("whoosh", 5, None, -0.3),
                 ("ding", 5, "线索", -0.1), ("shimmer", 5, "线索", 0.1)], transition="zoom"),
    scene("tool2", "violet", [
        L("第二招，【奥德赛计划】。", pause=0.3),
        L("给未来五年，写三个完全不同的剧本。", pause=0.25),
        L("剧本一，把现在的路走到极致；", pause=0.2),
        L("剧本二，如果这条路突然消失，你会做什么？", pause=0.2),
        L("剧本三，如果钱和面子都不重要，你最想过怎样的人生？", pause=0.3),
        L("手里有三个剧本，你就不再无路可走，而是有了【选择】。", pause=0.55),
    ], s_tool2, [("boom", -1, None, 0.0, 0.6), ("pop", 0, "奥德赛", 0.0), ("whoosh", 1, None, -0.3),
                 ("ding", 2, "剧本", 0.0), ("pop", 2, "极致", 0.0), ("ding", 3, "剧本", 0.0), ("pop", 3, "做什么", 0.0),
                 ("ding", 4, "剧本", 0.0), ("pop", 4, "人生", 0.0), ("buzz", 5, "无路可走", 0.5),
                 ("boom", 5, "选择", -0.1, 0.5), ("shimmer", 5, "选择", 0.1)], transition="zoom"),
    scene("tool3", "amber", [
        L("最后一招，叫做【最小原型】。", pause=0.3),
        L("想换条路？先别【一冲动就辞职】。", pause=0.3),
        L("请老板吃顿饭，问问他，管理岗到底需要什么能力？", pause=0.25),
        L("约个做培训的朋友喝杯咖啡，听听真实的辛苦。", pause=0.25),
        L("周末去咖啡馆打一天工，看看你爱的是咖啡，还是【诗和远方】。", pause=0.35),
        L("一顿饭、一杯咖啡、一个周末，", pause=0.15),
        L("就能帮你避开一次【代价巨大】的错误。", pause=0.55),
    ], s_tool3, [("boom", -1, None, 0.0, 0.6), ("pop", 0, "最小", 0.0), ("whoosh", 1, None, -0.35),
                 ("boom", 1, "辞职", -0.05, 0.8), ("whoosh", 2, None, -0.35), ("pop", 2, "问问", -0.1),
                 ("pop2", 2, "能力", 0.2), ("whoosh", 3, None, -0.35), ("pop", 3, "咖啡", -0.1),
                 ("pop2", 3, "辛苦", -0.1), ("whoosh", 4, None, -0.35), ("pop", 4, "咖啡，", -0.1),
                 ("pop2", 4, "诗和远方", -0.1), ("shimmer", 4, "远方", 0.1), ("whoosh", 5, None, -0.35),
                 ("pop", 5, "一顿饭", -0.05), ("pop", 5, "一杯咖啡", -0.05), ("pop", 5, "一个周末", -0.05),
                 ("boom", 6, "代价", -0.1, 0.6)], transition="zoom"),
    scene("climax", "gold", [
        L("焦虑，从来不是因为你不够努力，", speed=0.95, pause=0.2),
        L("而是因为你只看到了【一条路】。", speed=0.95, pause=0.55),
        L("人生没有标准答案，", speed=0.9, pause=0.3),
        L("但你，永远可以【重新设计】它。", speed=0.9, pause=1.1),
    ], s_climax, [("whoosh", -1, None, 0.0), ("heart", 0, None, 0.3), ("impact", 1, "。", 0.15),
                  ("shimmer", 2, None, 0.1), ("boom", 3, "重新设计", -0.05, 0.9), ("shimmer", 3, "设计", 0.25)],
        transition="black", bg=bg_climax),
    scene("cta", "gold", [
        L("这周，就从一个最小原型开始吧。", pause=0.3),
        L("你的第一个原型是什么？【评论区】告诉我。", pause=1.3),
    ], s_cta, [("pop", 0, None, 0.2), ("pop2", 0, None, 0.6), ("pop2", 0, None, 1.05), ("pop2", 0, None, 1.5),
               ("whoosh", 0, "开始", -0.3), ("pop", 1, "评论区", -0.1), ("pop2", 1, "告诉", -0.1),
               ("shimmer", 1, "告诉", 0.6)], transition="whip"),
]

MUSIC = [("hook", -1, "sad"), ("turn0", -1, "none"), ("turn", -1, "up"), ("climax", -1, "break"),
         ("climax", 3, "up"), ("cta", -1, "outro")]


def render_cover(path: str):
    """生成 1080×1920 封面图：大标题 + 表情 + 课程标签。"""
    info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surface = skia.Surface.MakeRaster(info)
    c = surface.getCanvas()
    pal = PALETTES["night"]
    gradient_bg(c, pal["bg"])
    aurora(c, 3.0, pal["blobs"], 0.32)
    dust(c, 2.0, pal["dust"], 50, seed=3)
    hook = dict(stroke=("#0A0A18", 14), glow=("#FF3D6E", 30), shadow=(0, 10, 14, "#000000"))
    draw_text(c, "按标准答案", 540, 470, 150, "title", "#FFFFFF", **hook)
    draw_text(c, "活了30年", 540, 650, 150, "title", "#FFFFFF", **hook)
    draw_text(c, "为什么还是不快乐？", 540, 850, 104, "title", "#FFE14D", stroke=("#0A0A18", 12),
              glow=("#FFB800", 24), shadow=(0, 10, 14, "#000000"))
    draw_emoji(c, "Smiling face with tear", 540, 1160, 400, glow=("#7FD8FF", 30))
    chip(c, 540, 1450, "斯坦福《设计你的人生》", 48, emoji="Graduation cap")
    vignette(c, 0.5)
    surface.makeImageSnapshot().save(path, skia.kPNG)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "out/designing_your_life_short.mp4"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    video = Video(SCENES, PALETTES, MUSIC, voice="zm_yunxi", base_speed=1.08)
    video.build()
    for s in SCENES:
        print(f"{s.name:8s} {s.t0:6.1f}s +{s.duration:5.1f}s")
    print(f"total {video.total:.1f}s")
    video.render(out)
    render_cover(str(Path(out).with_name("cover.png")))
    print(f"written: {out}")


if __name__ == "__main__":
    main()
