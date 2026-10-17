"""逻辑训练竖屏短视频（全程静音、无音频轨）：三人·三城·三种运动的一一对应推理。

画面完全由 Skia 逐帧矢量绘制，中文、条件栏、答案表都是真实字体排版。
所有绘制函数都是时间 t 的纯函数，可多进程分段并行渲染。

用法：
    python3 logic/logic_short.py out/logic_short.mp4          渲染成片 + 封面
    python3 logic/logic_short.py --preview 1.5,20,45          只导出指定秒数的预览帧
依赖：skia-python、numpy、FFmpeg（libx264）；字体由 fetch_assets.py 下载到 assets/fonts/
"""

import math
import subprocess
import sys
import tempfile
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import skia

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"
W, H, FPS, DUR = 1080, 1920, 30, 90.0

# ---------------------------------------------------------------- 配色：黄/橙=正在使用，灰+叉=排除，绿+勾=已确定
BG = "#F7F3EA"
INK = "#1D2B4F"
SUB = "#5B6478"
RED = "#C8102E"
CROSS = "#D62828"
ORANGE = "#E07B00"
ORANGE_BG = "#FFF0D2"
GREEN = "#2B8A3E"
GREEN_BG = "#E2F3E6"
GRAY = "#9AA0AB"
GRAY_BG = "#E9E8E4"
LINE = "#C9CFDA"
CARD = "#FFFFFF"
BLUE = "#2F5D9E"
BLUE_BG = "#E7EEF8"

PEOPLE = ("甲", "乙", "丙")
CITIES = ("北京", "上海", "广州")
SPORTS = ("篮球", "足球", "排球")
COND = ("甲不来自广州", "乙不来自上海", "来自北京的人喜欢足球", "来自上海的人喜欢篮球", "乙不喜欢排球")
NUM = "①②③④⑤"
COMBOS = (("北京", "足球"), ("上海", "篮球"), ("广州", "排球"))   # 由③④及一一对应推出的城市—运动绑定
ANSWER = {"甲": ("上海", "篮球"), "乙": ("北京", "足球"), "丙": ("广州", "排球")}

# 字幕：(开始, 结束, 第一行, 第二行)。【依据…】【推出…】【满足】渲染为标签。
SUBS = [
    (0.5, 3.0, "先别猜，找能绑定的条件。", None),
    (3.3, 8.2, "每人对应一座城市、一种运动", "城市、运动均不重复"),
    (8.6, 15.6, "五条线索，先自己读一遍", "可暂停自测"),
    (15.6, 22.8, "想好答案再往下看", "下面开始一步步推理"),
    (23.2, 28.0, "先把城市和运动绑定", "③④直接给出两组"),
    (28.0, 30.4, "【依据③】北京的人喜欢足球", "【推出】北京—足球"),
    (30.4, 32.8, "【依据④】上海的人喜欢篮球", "【推出】上海—篮球"),
    (32.8, 36.0, "【依据】城市、运动各用一次", "【推出】剩下广州—排球"),
    (36.0, 39.2, "看乙：候选就是这三组", "逐个排除"),
    (39.2, 43.0, "【依据②】乙不来自上海", "【推出】划掉上海—篮球"),
    (43.0, 45.6, "【依据⑤】乙不喜欢排球", "先划掉排球这一半"),
    (45.6, 49.2, "排球只和广州绑定", "【推出】乙不来自广州"),
    (49.2, 52.0, "候选只剩一组", "【推出】乙＝北京—足球"),
    (52.0, 55.0, "乙填入答案表", "【推出】北京—足球已被占用"),
    (55.0, 58.0, "看甲：只剩两组", "上海—篮球、广州—排球"),
    (58.0, 61.5, "【依据①】甲不来自广州", "【推出】划掉广州—排球"),
    (61.5, 65.0, "候选只剩一组", "【推出】甲＝上海—篮球"),
    (65.0, 68.4, "北京、上海都已被占用", "【推出】丙＝广州—排球"),
    (68.4, 72.0, "答案表三行全部确定", "接下来逐条回代检查"),
    (72.0, 74.0, "①甲来自上海，不是广州", "【满足】"),
    (74.0, 76.0, "②乙来自北京，不是上海", "【满足】"),
    (76.0, 78.0, "③北京的人是乙，喜欢足球", "【满足】"),
    (78.0, 80.0, "④上海的人是甲，喜欢篮球", "【满足】"),
    (80.0, 82.0, "⑤乙喜欢足球，不是排球", "【满足】"),
    (82.2, 90.0, "先绑定，再排除，最后回代", "下次遇到配对题试试"),
]

STEPS = [
    (3.0, 8.4, "认识题目"),
    (8.4, 23.0, "题目"),
    (23.0, 36.0, "第1步｜绑定"),
    (36.0, 52.0, "第2步｜锁定乙"),
    (52.0, 64.6, "第3步｜锁定甲"),
    (64.6, 72.0, "第4步｜确定丙"),
    (72.0, 82.0, "第5步｜回代检查"),
    (82.0, 99.0, "方法总结"),
]

# 条件栏高亮时段：(条件下标, 开始, 结束)
COND_HL = [
    *[(i, 10.6 + 1.4 * i, 11.8 + 1.4 * i) for i in range(5)],
    (2, 24.0, 30.4), (3, 24.0, 28.0), (3, 30.4, 32.8),
    (1, 39.2, 43.0), (4, 43.0, 49.2), (0, 58.0, 61.5),
    *[(i, 72.0 + 2 * i, 74.0 + 2 * i) for i in range(5)],
]

# 每个人的推理时间表。cross：(候选下标, 叉在哪一半, 时刻)；label：(候选下标, 文字, 时刻)；gray：(候选下标, 时刻)
PERSON_PLAN = [
    dict(name="乙", row=1, t_in=36.2, winner=0, conv=49.2, fly=52.0, t_out=52.4,
         cross=[(1, "city", 39.8), (2, "sport", 43.6), (2, "city", 46.6)],
         label=[(1, "依据②", 40.2), (2, "依据⑤", 44.0), (2, "⑤+绑定", 46.9)],
         gray=[(1, 40.6), (2, 47.2)], arrow=(45.8, 47.2)),
    dict(name="甲", row=0, t_in=53.0, winner=1, conv=61.5, fly=63.4, t_out=63.8,
         cross=[(0, "both", 54.2), (2, "city", 58.6)],
         label=[(0, "乙已占用", 54.4), (2, "依据①", 58.9)],
         gray=[(0, 54.7), (2, 59.4)], arrow=None),
    dict(name="丙", row=2, t_in=64.8, winner=2, conv=67.2, fly=68.4, t_out=71.6,
         cross=[(0, "both", 65.9), (1, "both", 66.4)],
         label=[(0, "乙已占用", 66.0), (1, "甲已占用", 66.5)],
         gray=[(0, 66.2), (1, 66.7)], arrow=None),
]

# 回代：条件 → 答案表中被检查的单元格 (行, 列)，列 1=城市、2=运动
BACKCHECK = [[(0, 1)], [(1, 1)], [(1, 1), (1, 2)], [(0, 1), (0, 2)], [(1, 2)]]

# ---------------------------------------------------------------- 版面（1080 宽；内容区 x 60–940，避开右侧约 140px 与上下平台遮挡区）
X0, X1 = 60, 940
CXM = (X0 + X1) / 2
HEAD_Y = 182
BAR_Y = [272 + 64 * i for i in range(5)]          # 条件栏（顶部常驻）
PAGE_Y = [662 + 64 * i for i in range(5)]         # 题目页上的条件位置
STRIP_Y = 640                                     # 绑定参考条
STRIP = [(60, 330), (340, 610), (620, 940)]
FOCUS_Y = 860                                     # 人物候选区
AV_X = 140
CAND_X = (380, 590, 800)
WIN_X = 590
TAB_X = (60, 260, 600, 940)
TAB_TOP, TAB_HEAD, TAB_ROW = 1060, 64, 84
SUB_TOP, SUB_BOT = 1426, 1640

OVERFLOW: list[str] = []


# ---------------------------------------------------------------- 缓动与颜色

def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def lerp(a, b, x):
    return a + (b - a) * x


def seg(t, start, dur=0.4):
    return clamp01((t - start) / dur) if dur > 0 else float(t >= start)


def ease(x):
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out(x):
    return 1 - (1 - clamp01(x)) ** 3


def back(x, s=1.4):
    x = clamp01(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def rgb(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(v) for v in c)


def mix(c1, c2, x):
    a, b = rgb(c1), rgb(c2)
    return tuple(round(p + (q - p) * clamp01(x)) for p, q in zip(a, b))


def color(c, a=1.0):
    r, g, b = rgb(c)
    return skia.Color(r, g, b, round(255 * clamp01(a)))


def fill(c, a=1.0):
    return skia.Paint(Color=color(c, a), AntiAlias=True)


def stroke(c, w, a=1.0, cap=skia.Paint.kRound_Cap, dash=None):
    p = skia.Paint(Color=color(c, a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                   StrokeCap=cap, StrokeJoin=skia.Paint.kRound_Join)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(dash, 0))
    return p


# ---------------------------------------------------------------- 文字

_TF: dict = {}
_FONTS: dict = {}


def font(weight, size):
    key = (weight, round(size * 2) / 2)
    if key not in _FONTS:
        if weight not in _TF:
            _TF[weight] = skia.Typeface.MakeFromFile(str(FONT_DIR / f"NotoSansCJKsc-{weight}.otf"))
            if _TF[weight] is None:
                raise FileNotFoundError(f"font not found: NotoSansCJKsc-{weight}.otf，请先运行 fetch_assets.py")
        f = skia.Font(_TF[weight], key[1])
        f.setSubpixel(True)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        _FONTS[key] = f
    return _FONTS[key]


def text_w(s, size, weight="Bold"):
    return font(weight, size).measureText(s)


def text(c, s, x, y, size, col=INK, a=1.0, weight="Bold", align="center", limit=None, check=True):
    """在 (x, y) 绘制一行文字，y 为字面视觉中线。check 时超出画面内容区或 limit 宽度记录溢出（滑动中的卡片不检查）。"""
    if a <= 0.003 or not s:
        return 0.0
    f = font(weight, size)
    w = f.measureText(s)
    left = x - w / 2 if align == "center" else x - w if align == "right" else x
    if (limit is not None and w > limit + 0.5) or (check and (left < 20 or left + w > W - 20)):
        OVERFLOW.append(f"{s!r} size={size} w={w:.0f} left={left:.0f}")
    c.drawString(s, left, y + 0.36 * size, f, fill(col, a))
    return w


# ---------------------------------------------------------------- 图形元件

def rrect(c, x0, y0, x1, y1, r, fc=None, sc=None, sw=3, a=1.0, dash=None):
    rect = skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r)
    if fc is not None:
        c.drawRRect(rect, fill(fc, a))
    if sc is not None and sw > 0:
        c.drawRRect(rect, stroke(sc, sw, a, dash=dash))


def partial_path(c, path, p, paint):
    """按长度比例 p 描绘路径的前一段（连线描绘动画）。"""
    if p <= 0:
        return
    if p >= 1:
        c.drawPath(path, paint)
        return
    meas = skia.PathMeasure(path, False)
    out = skia.Path()
    meas.getSegment(0, meas.getLength() * p, out, True)
    c.drawPath(out, paint)


def line_path(x0, y0, x1, y1, bend=0.0):
    path = skia.Path()
    path.moveTo(x0, y0)
    if bend:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = -(y1 - y0), x1 - x0
        n = math.hypot(nx, ny) or 1
        path.quadTo(mx + nx / n * bend, my + ny / n * bend, x1, y1)
    else:
        path.lineTo(x1, y1)
    return path


def arrow_head(c, x, y, ang, size, col, a):
    path = skia.Path()
    path.moveTo(x, y)
    path.lineTo(x - size * math.cos(ang - 0.45), y - size * math.sin(ang - 0.45))
    path.lineTo(x - size * math.cos(ang + 0.45), y - size * math.sin(ang + 0.45))
    path.close()
    c.drawPath(path, fill(col, a))


def cross_mark(c, cx, cy, size, p, a=1.0, col=CROSS):
    """红色叉号，两笔依次划出。"""
    if p <= 0:
        return
    s = size / 2
    p1, p2 = clamp01(p * 2), clamp01(p * 2 - 1)
    pt = stroke(col, max(6, size * 0.12), a)
    c.drawLine(cx - s, cy - s, cx - s + 2 * s * p1, cy - s + 2 * s * p1, pt)
    if p2 > 0:
        c.drawLine(cx + s, cy - s, cx + s - 2 * s * p2, cy - s + 2 * s * p2, pt)


def check_mark(c, cx, cy, size, p, a=1.0, col=GREEN, w=None):
    if p <= 0:
        return
    path = skia.Path()
    path.moveTo(cx - size * 0.45, cy + size * 0.02)
    path.lineTo(cx - size * 0.12, cy + size * 0.32)
    path.lineTo(cx + size * 0.48, cy - size * 0.36)
    partial_path(c, path, p, stroke(col, w or max(5, size * 0.16), a))


def check_badge(c, cx, cy, r, p, a=1.0):
    if p <= 0:
        return
    s = back(p)
    c.drawCircle(cx, cy, r * s, fill(GREEN, a))
    check_mark(c, cx, cy, r * 1.1 * s, clamp01(p * 1.6 - 0.3), a, "#FFFFFF", w=r * 0.24)


def pause_icon(c, cx, cy, size, col, a):
    w, h = size * 0.22, size * 0.8
    for dx in (-size * 0.22, size * 0.22):
        rrect(c, cx + dx - w / 2, cy - h / 2, cx + dx + w / 2, cy + h / 2, w * 0.35, fc=col, a=a)


def pin_icon(c, cx, cy, size, col, a):
    """城市图标：定位针。"""
    r = size * 0.32
    top = cy - size * 0.16
    path = skia.Path()
    path.addCircle(cx, top, r)
    tri = skia.Path()
    tri.moveTo(cx - r * 0.86, top + r * 0.5)
    tri.lineTo(cx + r * 0.86, top + r * 0.5)
    tri.lineTo(cx, cy + size * 0.44)
    tri.close()
    c.drawPath(path, fill(col, a))
    c.drawPath(tri, fill(col, a))
    c.drawCircle(cx, top, r * 0.42, fill("#FFFFFF", a))


def ball(c, kind, cx, cy, r, a=1.0, gray=0.0):
    """运动图标：篮球=橙色+黑缝线，足球=白底黑五边形，排球=黄底蓝弧线。始终与文字标签同时出现。"""
    if a <= 0.003:
        return
    dark = mix("#2A2420", GRAY, gray)
    clip = skia.Path()
    clip.addCircle(cx, cy, r)
    if kind == "篮球":
        c.drawCircle(cx, cy, r, fill(mix("#E8742A", GRAY_BG, gray), a))
        c.save()
        c.clipPath(clip, doAntiAlias=True)
        pt = stroke(dark, r * 0.09, a)
        c.drawLine(cx, cy - r, cx, cy + r, pt)
        c.drawLine(cx - r, cy, cx + r, cy, pt)
        c.drawCircle(cx - r * 1.32, cy, r * 0.95, pt)
        c.drawCircle(cx + r * 1.32, cy, r * 0.95, pt)
        c.restore()
    elif kind == "足球":
        c.drawCircle(cx, cy, r, fill("#FFFFFF", a))
        c.save()
        c.clipPath(clip, doAntiAlias=True)

        def penta(px, py, pr, rot):
            path = skia.Path()
            for k in range(5):
                ang = rot + k * 2 * math.pi / 5
                (path.moveTo if k == 0 else path.lineTo)(px + pr * math.cos(ang), py + pr * math.sin(ang))
            path.close()
            return path

        c.drawPath(penta(cx, cy, r * 0.36, -math.pi / 2), fill(dark, a))
        for k in range(5):
            ang = -math.pi / 2 + k * 2 * math.pi / 5
            c.drawLine(cx + r * 0.36 * math.cos(ang), cy + r * 0.36 * math.sin(ang),
                       cx + r * 0.8 * math.cos(ang), cy + r * 0.8 * math.sin(ang), stroke(dark, r * 0.07, a))
            ang2 = ang + math.pi / 5
            c.drawPath(penta(cx + r * 1.02 * math.cos(ang2), cy + r * 1.02 * math.sin(ang2), r * 0.3, ang2),
                       fill(dark, a))
        c.restore()
    else:
        c.drawCircle(cx, cy, r, fill(mix("#FFD84D", GRAY_BG, gray), a))
        c.save()
        c.clipPath(clip, doAntiAlias=True)
        blue = mix("#2C5DA9", GRAY, gray)
        for k in range(3):
            ang = -math.pi / 2 + k * 2 * math.pi / 3
            path = skia.Path()
            path.moveTo(cx, cy)
            ex, ey = cx + r * 1.1 * math.cos(ang), cy + r * 1.1 * math.sin(ang)
            qx, qy = cx + r * 0.75 * math.cos(ang + 0.7), cy + r * 0.75 * math.sin(ang + 0.7)
            path.quadTo(qx, qy, ex, ey)
            c.drawPath(path, stroke(blue, r * 0.2, a))
        c.restore()
    c.drawCircle(cx, cy, r, stroke(dark, r * 0.08, a))


def avatar(c, name, cx, cy, r=70, a=1.0, focus=0.0):
    """人物卡：圆形头像 + 名字，三人同一中性配色，不暗示答案。"""
    if a <= 0.003:
        return
    c.drawCircle(cx, cy, r, fill("#E4E8F0", a))
    c.drawCircle(cx, cy, r, stroke(mix("#8A94A8", ORANGE, focus), 3 + 4 * focus, a))
    text(c, name, cx, cy, r * 1.0, INK, a, "Black", check=False)


def city_card(c, name, cx, cy, a=1.0, hl=0.0, w=200, h=100):
    if a <= 0.003:
        return
    rrect(c, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 18, fc=mix(CARD, ORANGE_BG, hl),
          sc=mix(LINE, ORANGE, hl), sw=3 + 3 * hl, a=a)
    pin_icon(c, cx - w / 2 + 44, cy, 46, BLUE, a)
    text(c, name, cx + 22, cy, 46, INK, a, check=False)


def sport_card(c, name, cx, cy, a=1.0, hl=0.0, w=200, h=100):
    if a <= 0.003:
        return
    rrect(c, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, h / 2, fc=mix(CARD, ORANGE_BG, hl),
          sc=mix(LINE, ORANGE, hl), sw=3 + 3 * hl, a=a)
    ball(c, name, cx - w / 2 + 46, cy, 24, a)
    text(c, name, cx + 22, cy, 46, INK, a, check=False)


def combo_chip(c, city, sport, cx, cy, s=1.0, a=1.0, dim=0.0, green=0.0, focus=0.0,
               x_city=0.0, x_sport=0.0, x_both=0.0, check=0.0):
    """候选组合卡：上半城市、下半运动（来自已推出的绑定）。叉号按半区划掉，变灰表示整组排除。"""
    if a <= 0.003:
        return
    w, h = 190 * s, 200 * s
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    bg = mix(mix(CARD, GRAY_BG, dim), GREEN_BG, green)
    bd = mix(mix(mix(LINE, GRAY, dim), ORANGE, focus), GREEN, green)
    rrect(c, x0, y0, x1, y1, 20 * s, fc=bg, sc=bd, sw=(3 + 3 * max(green, focus)) * s, a=a)
    c.drawLine(x0 + 16 * s, cy, x1 - 16 * s, cy, stroke(mix(LINE, GRAY, dim), 2 * s, a, dash=[8 * s, 8 * s]))
    ink = mix(INK, GRAY, dim * 0.8)
    pin_icon(c, x0 + 40 * s, cy - 50 * s, 40 * s, mix(BLUE, GRAY, dim), a)
    text(c, city, cx + 20 * s, cy - 50 * s, 44 * s, ink, a, check=False)
    ball(c, sport, x0 + 40 * s, cy + 50 * s, 21 * s, a, gray=dim)
    text(c, sport, cx + 20 * s, cy + 50 * s, 44 * s, ink, a, check=False)
    cross_mark(c, cx, cy - 50 * s, 70 * s, x_city, a)
    cross_mark(c, cx, cy + 50 * s, 70 * s, x_sport, a)
    cross_mark(c, cx, cy, 130 * s, x_both, a)
    check_badge(c, x1 - 6 * s, y0 + 6 * s, 26 * s, check, a)


def tag_pill(c, s, x, cy, size, fg, bg, a=1.0, check=True):
    """左对齐标签胶囊，返回宽度。"""
    w = text_w(s, size) + size * 0.7
    h = size * 1.35
    rrect(c, x, cy - h / 2, x + w, cy + h / 2, h / 2, fc=bg, a=a)
    text(c, s, x + w / 2, cy, size, fg, a, check=check)
    return w


# ---------------------------------------------------------------- 分区绘制

def draw_header(c, t):
    rrect(c, X0, HEAD_Y - 32, X0 + 200, HEAD_Y + 32, 12, fc=RED)
    text(c, "逻辑训练", X0 + 100, HEAD_Y, 40, "#FFFFFF", 1, "Black")
    for a0, a1, title in STEPS:
        al = seg(t, a0, 0.3) * (1 - seg(t, a1 - 0.25, 0.25))
        if al > 0:
            text(c, title, 290 + 20 * (1 - ease_out(seg(t, a0, 0.3))), HEAD_Y, 64, INK, al, "Black", "left",
                 limit=X1 - 290)


def draw_intro(c, t):
    """0–8.4 秒：问题钩子 → 人物、城市、运动依次滑入，说明一一对应。"""
    out = 1 - seg(t, 8.0, 0.4)
    if out <= 0:
        return
    ta = 1 - seg(t, 2.85, 0.35)
    if ta > 0:
        dy = -40 * ease(seg(t, 2.85, 0.35))
        text(c, "这道题，", CXM, 400 + dy, 80, INK, ta, "Black", limit=880)
        text(c, "你会先锁定谁？", CXM, 510 + dy, 80, RED, ta, "Black", limit=880)
    move = ease(seg(t, 3.0, 0.6))
    xs = (210, 500, 790)
    py, cy, sy = lerp(820, 640, move), lerp(1080, 900, move), 1160
    la = seg(t, 3.4, 0.4) * out
    text(c, "人物", X0, py - 112, 38, SUB, la, "Bold", "left")
    text(c, "城市", X0, cy - 82, 38, SUB, la, "Bold", "left")
    text(c, "运动", X0, sy - 82, 38, SUB, seg(t, 3.9, 0.4) * out, "Bold", "left")
    for i in range(3):
        p = ease_out(seg(t, 0.15 + 0.22 * i, 0.5))
        avatar(c, PEOPLE[i], lerp(-160, xs[i], p), py, 70, clamp01(p * 2) * out)
        p = ease_out(seg(t, 0.9 + 0.22 * i, 0.5))
        city_card(c, CITIES[i], lerp(W + 160, xs[i], p), cy, clamp01(p * 2) * out)
        p = ease_out(seg(t, 3.7 + 0.22 * i, 0.5))
        sport_card(c, SPORTS[i], xs[i], lerp(sy + 160, sy, p), clamp01(p * 2) * out)
    ia = seg(t, 3.2, 0.4) * out
    text(c, "三个人 · 三座城市 · 三种运动", CXM, 330, 52, INK, ia, "Bold", limit=880)
    text(c, "一一对应，不重复", CXM, 430, 64, RED, seg(t, 4.6, 0.4) * out, "Black", limit=880)


def draw_page(c, t):
    """8.4–23 秒：完整题目页（条件行由 draw_conditions 绘制），提示可暂停自测。"""
    a = seg(t, 8.4, 0.5) * (1 - seg(t, 22.5, 0.4))
    if a <= 0:
        return
    text(c, "甲、乙、丙三人分别来自北京、上海、广州，", X0, 268, 42, INK, a, "Regular", "left", limit=880)
    text(c, "喜欢的运动是篮球、足球、排球。", X0, 330, 42, INK, a, "Regular", "left", limit=880)
    rrect(c, X0, 376, X1, 540, 18, fc=BLUE_BG, a=a)
    tag_pill(c, "前提", X0 + 20, 420, 38, "#FFFFFF", BLUE, a)
    text(c, "每人对应一座城市、一种运动；", X0 + 140, 420, 42, INK, a, "Bold", "left", limit=780)
    text(c, "城市、运动均不重复。", X0 + 140, 494, 42, INK, a, "Bold", "left", limit=780)
    text(c, "已知：", X0, 596, 42, INK, a, "Bold", "left")
    qa = a * seg(t, 10.6, 0.4)
    text(c, "问：三人分别来自哪个城市，", X0, 1012, 44, RED, qa, "Bold", "left", limit=880)
    text(c, "喜欢什么运动？", X0, 1078, 44, RED, qa, "Bold", "left", limit=880)
    pa = a * seg(t, 11.0, 0.4)
    rrect(c, CXM - 180, 1150, CXM + 180, 1240, 45, fc=INK, a=pa)
    pause_icon(c, CXM - 118, 1195, 44, "#FFFFFF", pa)
    text(c, "可暂停自测", CXM + 22, 1195, 46, "#FFFFFF", pa, "Bold")


def cond_hl(i, t):
    v = 0.0
    for k, a0, a1 in COND_HL:
        if k == i:
            v = max(v, seg(t, a0, 0.3) * (1 - seg(t, a1 - 0.3, 0.3)))
    return v


def cond_ok(i, t):
    return seg(t, 72.9 + 2 * i, 0.4)


def draw_conditions(c, t):
    """五条条件：先在题目页逐条出现，23 秒后上移为常驻条件栏；使用中=橙色+“使用中”，回代满足=绿色+勾+“满足”。"""
    if t < 8.8:
        return
    up = ease(seg(t, 22.8, 0.7))
    bar = t >= 23.5
    for i in range(5):
        p = ease_out(seg(t, 9.0 + 0.35 * i, 0.4))
        if p <= 0:
            continue
        y = lerp(PAGE_Y[i], BAR_Y[i], up)
        dx = -40 * (1 - p)
        hl, ok = cond_hl(i, t), cond_ok(i, t)
        bg = mix(mix(CARD, ORANGE_BG, hl), GREEN_BG, ok)
        bd = mix(mix(LINE, ORANGE, hl), GREEN, ok)
        rrect(c, X0 + dx, y - 28, X1 + dx, y + 28, 14, fc=bg, sc=bd, sw=2 + 3 * max(hl, ok), a=p)
        text(c, NUM[i], X0 + 16 + dx, y, 42, mix(mix(INK, ORANGE, hl), GREEN, ok), p, "Bold", "left")
        text(c, COND[i], X0 + 72 + dx, y, 42, INK, p, "Bold", "left")
        if bar and hl > 0 and ok <= 0:
            tag_pill(c, "使用中", X1 - 140, y, 32, "#FFFFFF", ORANGE, hl)
        if ok > 0:
            check_mark(c, X1 - 118, y, 40, ok, 1.0)
            text(c, "满足", X1 - 58, y, 38, GREEN, ok, "Bold")


def draw_binding(c, t):
    """23–36 秒：城市、运动卡滑入 → ③④连线吸附 → 推出广州—排球 → 三组飞入绑定参考条。"""
    if t < 23.2 or t > 36.3:
        return
    fly = ease(seg(t, 35.3, 0.8))
    ga = 1 - seg(t, 35.7, 0.4)
    rows = (760, 940, 1120)
    city_x, dock_x, tag_x, sport_x = 190, 400, 570, 820
    # 每组：(城市行, 运动初始行, 条件下标或 None, 连线开始, 吸附开始, 标签时刻)
    links = [(0, 1, 2, 28.2, 28.9, 29.4), (1, 0, 3, 30.6, 31.3, 31.8), (2, 2, None, 33.0, 33.7, 34.2)]
    for k, (ci, si, cond, l0, d0, tg) in enumerate(links):
        enter_c = ease_out(seg(t, 23.4 + 0.18 * ci, 0.5))
        enter_s = ease_out(seg(t, 23.9 + 0.18 * si, 0.5))
        hl = seg(t, l0 - 0.2, 0.3) * (1 - seg(t, d0 + 0.5, 0.4))
        dock = ease(seg(t, d0, 0.5))
        sx = lerp(sport_x, dock_x, dock)
        sy = lerp(rows[si], rows[ci], dock)
        tx = lerp(0, STRIP[k][0] + 100 - city_x, fly)
        ty = lerp(0, STRIP_Y - rows[ci], fly)
        c.save()
        c.translate(tx, ty)
        if dock >= 1:
            gb = seg(t, tg, 0.3)
            rrect(c, city_x - 112, rows[ci] - 62, dock_x + 112, rows[ci] + 62, 24, sc=GREEN, sw=4, a=gb * ga)
        city_card(c, CITIES[ci], lerp(-160, city_x, enter_c), rows[ci], clamp01(enter_c * 2) * ga, hl)
        sport_card(c, SPORTS[si], lerp(W + 160, sx, enter_s) if dock == 0 else sx, sy,
                   clamp01(enter_s * 2) * ga, hl)
        lp = ease_out(seg(t, l0, 0.6))
        la = (1 - seg(t, d0, 0.3)) * ga
        if lp > 0 and la > 0:
            path = line_path(city_x + 100, rows[ci], sport_x - 100, rows[si])
            partial_path(c, path, lp, stroke(ORANGE, 7, la, dash=[16, 12] if cond is None else None))
        ta = seg(t, tg, 0.3) * ga
        if cond is not None:
            c.drawCircle(tag_x, rows[ci], 34, fill(GREEN, ta))
            text(c, NUM[cond], tag_x, rows[ci], 44, "#FFFFFF", ta, "Bold")
        else:
            tag_pill(c, "推出", tag_x - 46, rows[ci], 38, "#FFFFFF", BLUE, ta)
        c.restore()
    if t < 32.8:
        return
    na = seg(t, 34.4, 0.4) * ga
    text(c, "城市、运动各只用一次", 520, 1240, 42, SUB, na, "Bold", limit=760)
    text(c, "③④用掉北京、上海和足球、篮球", 500, 1312, 42, SUB, na, "Bold", limit=880)


def draw_strip(c, t, hl3=0.0):
    """绑定参考条：③北京—足球、④上海—篮球、推出 广州—排球，供后续逐人排除时查阅。"""
    a = seg(t, 35.8, 0.4) * (1 - seg(t, 71.8, 0.4))
    if a <= 0:
        return
    s = 1 + 0.15 * (1 - ease_out(seg(t, 35.8, 0.4)))
    for k, (x0, x1) in enumerate(STRIP):
        cx = (x0 + x1) / 2
        hl = hl3 if k == 2 else 0.0
        c.save()
        c.translate(cx, STRIP_Y)
        c.scale(s, s)
        rrect(c, x0 - cx, -42, x1 - cx, 42, 16, fc=mix(GREEN_BG, ORANGE_BG, hl), sc=mix(GREEN, ORANGE, hl),
              sw=3 + 3 * hl, a=a)
        city, sport = COMBOS[k]
        label = f"{city}—{sport}"
        if k < 2:
            c.drawCircle(x0 - cx + 34, 0, 22, fill(GREEN, a))
            text(c, NUM[2 + k], x0 - cx + 34, 0, 32, "#FFFFFF", a, "Bold", check=False)
            text(c, label, x0 - cx + 66, 0, 38, INK, a, "Bold", "left", limit=x1 - x0 - 76, check=False)
        else:
            pw = tag_pill(c, "推出", x0 - cx + 10, 0, 38, "#FFFFFF", BLUE, a, check=False)
            text(c, label, x0 - cx + 16 + pw, 0, 38, INK, a, "Bold", "left", limit=x1 - x0 - 26 - pw, check=False)
        c.restore()


def draw_person(c, t, plan):
    """对一个人逐个排除候选组合 → 收敛为唯一结果 → 飞入答案表。"""
    t_in, t_out = plan["t_in"], plan["t_out"]
    if t < t_in or t > t_out + 0.5:
        return 0.0
    out = 1 - seg(t, t_out, 0.4)
    p = ease_out(seg(t, t_in, 0.45))
    conv, fly, win = plan["conv"], plan["fly"], plan["winner"]
    focus = 1 - seg(t, conv + 0.6, 0.4)
    avatar(c, plan["name"], lerp(-120, AV_X, p), FOCUS_Y, 70, clamp01(p * 2) * out, focus)
    eq = seg(t, conv + 0.6, 0.3) * out * (1 - seg(t, fly, 0.35))
    text(c, "＝", 380, FOCUS_Y, 72, INK, eq, "Black")
    hl3 = 0.0
    for i in range(3):
        q = ease_out(seg(t, t_in + 0.2 + 0.15 * i, 0.55))
        if q <= 0:
            continue
        x = lerp((STRIP[i][0] + STRIP[i][1]) / 2, CAND_X[i], q)
        y = lerp(STRIP_Y, FOCUS_Y, q)
        s = lerp(0.5, 1.0, q)
        a = clamp01(q * 2) * out
        dim = max([seg(t, tg, 0.4) for k, tg in plan["gray"] if k == i] or [0.0])
        xs = {"city": 0.0, "sport": 0.0, "both": 0.0}
        for k, half, tc in plan["cross"]:
            if k == i:
                xs[half] = max(xs[half], seg(t, tc, 0.45))
        green = check = 0.0
        if i == win:
            m = ease(seg(t, conv, 0.6))
            x = lerp(x, WIN_X, m)
            s *= lerp(1.0, 1.1, m)
            green = seg(t, conv + 0.5, 0.4)
            check = seg(t, conv + 0.9, 0.4)
            a *= 1 - seg(t, fly, 0.35)
        else:
            a *= 1 - seg(t, conv, 0.5)
        combo_chip(c, *COMBOS[i], x, y, s, a, dim, green, 0.0, xs["city"], xs["sport"], xs["both"], check)
        labels = [(txt, tl) for k, txt, tl in plan["label"] if k == i and t >= tl]
        if labels:
            txt, tl = labels[-1]
            text(c, txt, x, FOCUS_Y + 140, 38, CROSS, seg(t, tl, 0.3) * a, "Bold", limit=200)
        if i == win:
            text(c, "唯一剩下", x, FOCUS_Y + 145, 38, GREEN, seg(t, conv + 0.9, 0.3) * a, "Bold")
    if plan["arrow"]:
        a0, a1 = plan["arrow"]
        hl3 = seg(t, a0 - 0.2, 0.3) * (1 - seg(t, a1, 0.4))
        ap = ease_out(seg(t, a0, 0.6))
        aa = 1 - seg(t, a1, 0.4)
        if ap > 0 and aa > 0:
            sx, sy, ex, ey = 780, STRIP_Y + 46, CAND_X[2], FOCUS_Y - 104
            partial_path(c, line_path(sx, sy, ex, ey), ap, stroke(ORANGE, 7, aa))
            if ap >= 1:
                arrow_head(c, ex, ey, math.atan2(ey - sy, ex - sx), 22, ORANGE, aa)
    # 结果飞入答案表
    fp = ease(seg(t, fly, 0.7))
    if 0 < fp < 1:
        city, sport = ANSWER[plan["name"]]
        ry = row_y(plan["row"])
        text(c, city, lerp(WIN_X + 20, cell_x(1), fp), lerp(FOCUS_Y - 55, ry, fp), 44, GREEN, 1, "Bold")
        text(c, sport, lerp(WIN_X + 20, cell_x(2), fp), lerp(FOCUS_Y + 55, ry, fp), 44, GREEN, 1, "Bold")
    return hl3


def row_y(r):
    return TAB_TOP + TAB_HEAD + TAB_ROW * r + TAB_ROW / 2


def cell_x(col):
    return (TAB_X[col] + TAB_X[col + 1]) / 2


def cell_hl(r, col, t):
    v = 0.0
    for i, cells in enumerate(BACKCHECK):
        if (r, col) in cells:
            s0 = 72.0 + 2 * i
            v = max(v, seg(t, s0 + 0.3, 0.3) * (1 - seg(t, s0 + 1.7, 0.3)))
    return v


def draw_table(c, t):
    """固定答案表：行序始终甲、乙、丙；未确定单元格显示灰色问号。"""
    a = seg(t, 36.8, 0.5)
    if a <= 0:
        return
    rrect(c, TAB_X[0], TAB_TOP, TAB_X[3], TAB_TOP + TAB_HEAD + 3 * TAB_ROW, 16, fc=CARD, sc=LINE, sw=3, a=a)
    rrect(c, TAB_X[0], TAB_TOP, TAB_X[3], TAB_TOP + TAB_HEAD, 16, fc=INK, a=a)
    c.drawRect(skia.Rect(TAB_X[0], TAB_TOP + TAB_HEAD - 16, TAB_X[3], TAB_TOP + TAB_HEAD), fill(INK, a))
    for col, h in enumerate(("人物", "来自城市", "喜欢的运动")):
        text(c, h, cell_x(col), TAB_TOP + TAB_HEAD / 2, 38, "#FFFFFF", a, "Bold")
    fills = {p["row"]: seg(t, p["fly"] + 0.7, 0.3) for p in PERSON_PLAN}
    for r, name in enumerate(PEOPLE):
        y0 = TAB_TOP + TAB_HEAD + TAB_ROW * r
        y = row_y(r)
        f = fills[r]
        if f > 0:
            c.drawRect(skia.Rect(TAB_X[0] + 2, y0 + 1, TAB_X[3] - 2, y0 + TAB_ROW - 1 - (2 if r == 2 else 0)),
                       fill(GREEN_BG, a * f))
        if r > 0:
            c.drawLine(TAB_X[0], y0, TAB_X[3], y0, stroke(LINE, 2, a, cap=skia.Paint.kButt_Cap))
        text(c, name, cell_x(0), y, 46, INK, a, "Black")
        city, sport = ANSWER[name]
        text(c, "？", cell_x(1), y, 44, GRAY, a * (1 - f))
        text(c, "？", cell_x(2), y, 44, GRAY, a * (1 - f))
        if f > 0:
            sc = 0.8 + 0.2 * back(f)
            text(c, city, cell_x(1), y, 44 * sc, INK, a * f, "Bold")
            ball(c, sport, cell_x(2) - 74, y, 21, a * f)
            text(c, sport, cell_x(2) + 18, y, 44 * sc, INK, a * f, "Bold")
        for col in (1, 2):
            h = cell_hl(r, col, t)
            if h > 0:
                rrect(c, TAB_X[col] + 8, y0 + 8, TAB_X[col + 1] - 8, y0 + TAB_ROW - 8, 12, sc=ORANGE, sw=5, a=h)
    for col in (1, 2):
        c.drawLine(TAB_X[col], TAB_TOP + TAB_HEAD, TAB_X[col], TAB_TOP + TAB_HEAD + 3 * TAB_ROW,
                   stroke(LINE, 2, a, cap=skia.Paint.kButt_Cap))


def draw_backcheck(c, t):
    """72–82 秒：条件逐条连线到答案表对应单元格并打勾。"""
    if t < 72.0 or t > 82.4:
        return
    for i, cells in enumerate(BACKCHECK):
        s0 = 72.0 + 2 * i
        lp = ease_out(seg(t, s0 + 0.15, 0.5))
        la = 1 - seg(t, s0 + 1.7, 0.3)
        if lp <= 0 or la <= 0:
            continue
        sx, sy = X1 - 8, BAR_Y[i]
        for r, col in cells:
            ex, ey = cell_x(col), row_y(r) - 30
            path = skia.Path()
            path.moveTo(sx, sy)
            path.cubicTo(965, sy + 260, ex + 60, ey - 300, ex, ey)
            partial_path(c, path, lp, stroke(ORANGE, 5, la))
            if lp >= 1:
                c.drawCircle(ex, ey, 9, fill(ORANGE, la))
    a = seg(t, 72.3, 0.4) * (1 - seg(t, 82.0, 0.3))
    n = sum(1 for i in range(5) if t >= 72.9 + 2 * i)
    text(c, "回代检查", 220, FOCUS_Y - 50, 52, INK, a, "Black")
    text(c, f"已满足 {n} / 5", 220, FOCUS_Y + 30, 48, GREEN if n else SUB, a, "Bold")


def draw_summary(c, t):
    """82–90 秒：方法总结“绑定 → 排除 → 回代”依次点亮。"""
    if t < 82.0:
        return
    steps = (("绑定", "③④锁组合"), ("排除", "逐人划候选"), ("回代", "五条全满足"))
    xs = (190, 500, 810)
    for k, (name, cap) in enumerate(steps):
        p = seg(t, 82.4 + 1.0 * k, 0.45)
        if p <= 0:
            continue
        s = 0.85 + 0.15 * back(p)
        w, h = 210 * s, 110 * s
        rrect(c, xs[k] - w / 2, FOCUS_Y - 30 - h / 2, xs[k] + w / 2, FOCUS_Y - 30 + h / 2, 55 * s, fc=INK,
              a=clamp01(p * 2))
        text(c, name, xs[k], FOCUS_Y - 30, 54 * s, "#FFFFFF", clamp01(p * 2), "Black")
        text(c, cap, xs[k], FOCUS_Y + 70, 38, SUB, clamp01(p * 2), "Bold", limit=290)
        if k < 2:
            ap = seg(t, 82.8 + 1.0 * k, 0.4)
            if ap > 0:
                ax = xs[k] + 112
                c.drawLine(ax, FOCUS_Y - 30, ax + 54 * ap, FOCUS_Y - 30, stroke(ORANGE, 7, 1))
                if ap >= 1:
                    arrow_head(c, ax + 64, FOCUS_Y - 30, 0, 22, ORANGE, 1)


def rich_line(c, s, cy, size, a):
    """字幕行：【xx】渲染为标签（依据=橙、推出=蓝、满足=绿），其余为正文，整体居中。"""
    parts, rest = [], s
    while "【" in rest:
        pre, _, tail = rest.partition("【")
        tag, _, rest = tail.partition("】")
        if pre:
            parts.append(("t", pre))
        parts.append(("g", tag))
    if rest:
        parts.append(("t", rest))
    gap = 14
    widths = [text_w(v, size) if k == "t" else text_w(v, size * 0.82) + size * 0.82 * 0.7 for k, v in parts]
    total = sum(widths) + gap * sum(1 for k, _ in parts if k == "g")
    if total > SUB_LIMIT:
        OVERFLOW.append(f"subtitle {s!r} w={total:.0f}")
    x = CXM - total / 2
    for (k, v), w in zip(parts, widths):
        if k == "t":
            text(c, v, x, cy, size, INK, a, "Bold", "left")
            x += w
        else:
            bg = ORANGE if v.startswith("依据") else GREEN if v == "满足" else BLUE
            tag_pill(c, v, x, cy, size * 0.82, "#FFFFFF", bg, a)
            if v == "满足":
                check_mark(c, x + w + gap + 26, cy, 44, a, a)
            x += w + gap


SUB_LIMIT = 840


def draw_subtitles(c, t):
    for a0, a1, l1, l2 in SUBS:
        a = seg(t, a0, 0.15) * (1 - seg(t, a1 - 0.15, 0.15)) if a1 < DUR else seg(t, a0, 0.15)
        if a <= 0:
            continue
        rrect(c, X0, SUB_TOP, X1, SUB_BOT, 28, fc=CARD, sc=LINE, sw=2, a=a * 0.96)
        if l2 is None:
            rich_line(c, l1, (SUB_TOP + SUB_BOT) / 2, 50, a)
        else:
            rich_line(c, l1, SUB_TOP + 68, 50, a)
            rich_line(c, l2, SUB_BOT - 68, 50, a)


def draw_frame(c, t):
    c.clear(color(BG))
    draw_header(c, t)
    draw_intro(c, t)
    draw_page(c, t)
    draw_conditions(c, t)
    draw_binding(c, t)
    draw_table(c, t)
    hl3 = 0.0
    for plan in PERSON_PLAN:
        hl3 = max(hl3, draw_person(c, t, plan))
    draw_strip(c, t, hl3)
    draw_backcheck(c, t)
    draw_summary(c, t)
    draw_subtitles(c, t)


# ---------------------------------------------------------------- 渲染

def render_frame(t):
    buf = np.zeros((H, W, 4), np.uint8)
    surf = skia.Surface(buf)
    draw_frame(surf.getCanvas(), t)
    return buf


def _render_segment(args):
    """渲染 [f0, f1) 帧为一个无音频的 H.264 分段。"""
    f0, f1, path = args
    buf = np.zeros((H, W, 4), np.uint8)
    surf = skia.Surface(buf)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-r", str(FPS), path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        draw_frame(surf.getCanvas(), f / FPS)
        proc.stdin.write(buf.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")
    return OVERFLOW[:]


def render(out_path, workers=4):
    n = int(round(DUR * FPS))
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        bounds = [round(n * k / workers) for k in range(workers + 1)]
        parts = [(bounds[k], bounds[k + 1], str(Path(tmp) / f"part{k}.mp4")) for k in range(workers)]
        with get_context("fork").Pool(workers) as pool:
            overflow = sorted({o for r in pool.map(_render_segment, parts) for o in r})
        if overflow:
            raise RuntimeError("文字超出版面：\n" + "\n".join(overflow))
        lst = Path(tmp) / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for _, _, p in parts))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-an", "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    save_png(render_frame(2.9), out.parent / "logic_cover.png")


def save_png(arr, path):
    img = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType)
    img.save(str(path), skia.kPNG)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--preview":
        d = ROOT / "out" / "preview"
        d.mkdir(parents=True, exist_ok=True)
        for s in args[1].split(","):
            save_png(render_frame(float(s)), d / f"t{float(s):05.1f}.png")
        if OVERFLOW:
            print("文字超出版面：\n" + "\n".join(sorted(set(OVERFLOW))))
        print(f"预览帧已写入 {d}")
    else:
        render(args[0] if args else str(ROOT / "out" / "logic_short.mp4"))
