"""《熬夜欠的觉》专用元件：调色板、指针时钟、睡眠账本、模型曲线图表。

视觉风格“夜光实验室”：深夜蓝底；睡眠压力 S 琥珀色、生物钟（入睡线）青色、困意紫色；
道具用 3D Emoji，数据用发光描线。所有函数是时间的纯函数。
"""

import math

import numpy as np
import skia

from engine.gfx import chip, circle, clamp01, col, draw_text, ease_out, ease_out_back, mix, prog, rrect, stroke_path

from . import model

S_COL = "#FFB547"
C_COL = "#5CE1E6"
GAP_COL = "#A78BFA"
OK_COL = "#5BE49B"
BAD_COL = "#FF6B6B"
INK = "#0A0F2A"
GLASS = "#DDE6FF"

PALETTES = {
    "night": dict(bg=["#03061A", "#0A1238", "#1A1A55"], blobs=["#2B2F8F", "#14407A", "#4A2A7A"],
                  dust="#BFD4FF", hi=S_COL, aurora=0.22, vignette=0.6, dust_a=0.45),
    "noon": dict(bg=["#1A1033", "#5A2E5E", "#C8724A"], blobs=["#FF9F5A", "#E0607E", "#FFD27A"],
                 dust="#FFF1D0", hi="#FFE08A", aurora=0.3),
    "lab": dict(bg=["#040817", "#0A1830", "#0F2546"], blobs=["#123E66", "#1B2F6B", "#0E4A5A"],
                dust="#9FD8FF", hi=S_COL, aurora=0.18, vignette=0.55, dust_a=0.35),
}
NOON_BG = PALETTES["noon"]["bg"]


def clock(c: skia.Canvas, x: float, y: float, r: float, hour: float, alpha: float = 1.0, glow=C_COL):
    """玻璃质感指针时钟；hour 为一天中的小时数（可带小数），下方不带数字（数字另画）。"""
    if alpha <= 0:
        return
    circle(c, x, y, r * 1.08, glow, 0.25 * alpha, blur=r * 0.25, blend=skia.BlendMode.kPlus)
    circle(c, x, y, r, "#0E1640", 0.85 * alpha)
    ring = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.06,
                      Color=col(GLASS, 0.9 * alpha))
    c.drawCircle(x, y, r, ring)
    for k in range(60):
        a = math.radians(k * 6 - 90)
        major = k % 5 == 0
        r0 = r * (0.80 if major else 0.87)
        p = skia.Paint(AntiAlias=True, StrokeWidth=r * (0.035 if major else 0.012), StrokeCap=skia.Paint.kRound_Cap,
                       Color=col(GLASS, (0.95 if major else 0.4) * alpha))
        c.drawLine(x + r0 * math.cos(a), y + r0 * math.sin(a), x + r * 0.92 * math.cos(a), y + r * 0.92 * math.sin(a), p)
    h = hour % 12
    for ang, length, width, color in ((h * 30, 0.5, 0.07, "#FFFFFF"), ((hour % 1) * 360, 0.74, 0.04, S_COL)):
        a = math.radians(ang - 90)
        p = skia.Paint(AntiAlias=True, StrokeWidth=r * width, StrokeCap=skia.Paint.kRound_Cap, Color=col(color, alpha))
        c.drawLine(x - r * 0.1 * math.cos(a), y - r * 0.1 * math.sin(a),
                   x + r * length * math.cos(a), y + r * length * math.sin(a), p)
    circle(c, x, y, r * 0.06, S_COL, alpha)


def hhmm(hour: float) -> str:
    m = int(round(hour * 60)) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


def ledger(c: skia.Canvas, x: float, y: float, t: float, fill_at: float, split_at: float, ghost_at: float,
           alpha: float = 1.0, scale: float = 1.0):
    """睡眠账本卡片：fill_at 起红色“欠着”条涨满；split_at 起左半变绿“补回来了”，ghost_at 起右半变成虚线幽灵“感觉不到”。"""
    if alpha <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(scale, scale)
    rrect(c, 0, 0, 860, 300, 36, "#0E1640", 0.92 * alpha, stroke=(GLASS, 3), shadow=0.35)
    draw_text(c, "睡眠账本", -380, -102, 40, "bold", GLASS, alpha, align="left")
    chip(c, 330, -102, "示意", 26, fill="#26305E", fg=GLASS, alpha=alpha)
    bw, bh, by = 740, 96, 26
    rrect(c, 0, by, bw, bh, 22, "#1A2350", alpha)
    grow = ease_out(prog(t, fill_at, 0.9))
    sp = ease_out_back(prog(t, split_at, 0.5), 1.6)
    gp = prog(t, ghost_at, 0.6)
    half = bw / 2 - 8
    gap = 0.0
    if sp <= 0:
        if grow > 0:
            rrect(c, -bw / 2 + bw * grow / 2, by, bw * grow, bh, 22, BAD_COL, alpha)
    else:
        rrect(c, -bw / 2 + half / 2 - gap, by, half, bh, 22, mix(BAD_COL, OK_COL, clamp01(sp)), alpha)
        rx = bw / 2 - half / 2 + gap
        rrect(c, rx, by, half, bh, 22, BAD_COL, alpha * (1 - 0.82 * gp))
        if gp > 0:
            path = skia.Path()
            path.addRoundRect(skia.Rect.MakeXYWH(rx - half / 2, by - bh / 2, half, bh), 22, 22)
            stroke_path(c, path, BAD_COL, 5, alpha * gp, dash=(18, 12, t * 40))
    label_a = alpha * clamp01(grow * 3)
    if sp <= 0:
        draw_text(c, "欠着", 0, by, 48, "black", "#FFFFFF", label_a)
    else:
        draw_text(c, "补回来了", -bw / 4 - gap, by, 46, "black", INK, alpha * clamp01(sp))
        if gp > 0:
            q = 0.5 + 0.5 * math.sin(t * 5)
            draw_text(c, "感觉不到", bw / 4 + gap, by, 46, "black", BAD_COL, alpha * gp, glow=(BAD_COL, 10 * q))
        else:
            draw_text(c, "欠着", bw / 4 + gap, by, 46, "black", "#FFFFFF", alpha * clamp01(sp))
    c.restore()


# ---------------------------------------------------------------- 模型曲线图表

class Chart:
    """双过程模型图表：横轴为钟点（小时），纵轴为 S 的取值；数据来自 model.scenario，按 p（0–1）描线推进。"""

    def __init__(self, scenario: str, t0: float, t1: float, box=(110, 430, 970, 1170), y0: float = 0.0,
                 y1: float = 1.0):
        self.t, self.s, self.asleep = model.scenario(scenario)
        self.t0, self.t1, self.box, self.y0, self.y1 = t0, t1, box, y0, y1
        k = (self.t >= t0) & (self.t <= t1)
        self.tt, self.ss, self.zz = self.t[k], self.s[k], self.asleep[k]
        self.hh = model.upper(self.tt)

    def px(self, hour):
        l, _, r, _ = self.box
        return l + (np.asarray(hour) - self.t0) / (self.t1 - self.t0) * (r - l)

    def py(self, v):
        _, top, _, bot = self.box
        return bot - (np.asarray(v) - self.y0) / (self.y1 - self.y0) * (bot - top)

    def _path(self, ys, upto: int) -> skia.Path:
        path = skia.Path()
        xs, vs = self.px(self.tt[:upto:4]), self.py(ys[:upto:4])
        for i, (a, b) in enumerate(zip(xs, vs)):
            path.lineTo(a, b) if i else path.moveTo(a, b)
        return path

    def draw(self, c: skia.Canvas, p: float, alpha: float = 1.0, t: float = 0.0, band: bool = True,
             show_c: bool = True, labels: bool = True):
        """p 为描线进度；band 时在入睡线与 S 之间填充困意色带（S 越接近入睡线越亮）。"""
        if alpha <= 0:
            return
        l, top, r, bot = self.box
        rrect(c, (l + r) / 2, (top + bot) / 2 + 20, r - l + 80, bot - top + 150, 34, "#08102A", 0.75 * alpha,
              stroke=("#22305E", 3))
        for a, b in self._spans():
            rrect(c, (self.px(a) + self.px(b)) / 2, (top + bot) / 2, self.px(b) - self.px(a), bot - top, 0,
                  "#1B2A66", 0.55 * alpha)
            draw_text(c, "睡着", (self.px(a) + self.px(b)) / 2, top + 28, 28, "bold", "#8FA3E0", alpha)
        grid = skia.Paint(AntiAlias=True, StrokeWidth=1.5, Color=col("#2A3A70", alpha))
        for hr in range(math.ceil(self.t0 / 3) * 3, int(self.t1) + 1, 3):
            x = float(self.px(hr))
            c.drawLine(x, top, x, bot, grid)
            draw_text(c, f"{hr % 24}点", x, bot + 42, 28, "bold", "#8FA3E0", alpha)
        n = max(2, int(len(self.tt) * clamp01(p)))
        if band:
            poly = skia.Path()
            xs = self.px(self.tt[:n:4])
            ys_s, ys_h = self.py(self.ss[:n:4]), self.py(self.hh[:n:4])
            for i, (a, b) in enumerate(zip(xs, ys_h)):
                poly.lineTo(a, b) if i else poly.moveTo(a, b)
            for a, b in zip(xs[::-1], ys_s[::-1]):
                poly.lineTo(a, b)
            poly.close()
            fp = skia.Paint(AntiAlias=True, Color=col(GAP_COL, 0.28 * alpha))
            c.drawPath(poly, fp)
        if show_c:
            stroke_path(c, self._path(self.hh, n), C_COL, 8, alpha, glow=(C_COL, 14))
        stroke_path(c, self._path(self.ss, n), S_COL, 10, alpha, glow=(S_COL, 16))
        head_t, head_s = self.tt[n - 1], self.ss[n - 1]
        pulse = 0.5 + 0.5 * math.sin(t * 6)
        circle(c, float(self.px(head_t)), float(self.py(head_s)), 26 + 8 * pulse, S_COL, 0.35 * alpha, blur=10)
        circle(c, float(self.px(head_t)), float(self.py(head_s)), 14, "#FFFFFF", alpha)
        if labels:
            draw_text(c, "睡眠压力", l + 10, bot + 96, 34, "black", S_COL, alpha, align="left")
            draw_text(c, "入睡线（生物钟）", r - 10, bot + 96, 34, "black", C_COL, alpha, align="right")

    def _spans(self):
        out, start = [], None
        for hr, z in zip(self.tt, self.zz):
            if z and start is None:
                start = hr
            elif not z and start is not None:
                out.append((start, hr))
                start = None
        if start is not None:
            out.append((start, self.tt[-1]))
        return out


def sleepy_meter(c: skia.Canvas, x: float, y: float, value: float, alpha: float = 1.0):
    """困意读数条：value 为 model.sleepiness 的值，1 为该睡了，>1 为硬撑。"""
    if alpha <= 0:
        return
    w, h = 520, 44
    draw_text(c, "困意", x - w / 2 - 70, y, 36, "black", GAP_COL, alpha)
    rrect(c, x, y, w, h, h / 2, "#1A2350", alpha)
    v = clamp01(value / 1.5)
    if v > 0:
        rrect(c, x - w / 2 + w * v / 2, y, w * v, h, h / 2, GAP_COL if value <= 1 else BAD_COL, alpha)
    mark = x - w / 2 + w / 1.5
    p = skia.Paint(AntiAlias=True, StrokeWidth=4, Color=col("#FFFFFF", 0.8 * alpha))
    c.drawLine(mark, y - h * 0.8, mark, y + h * 0.8, p)
    draw_text(c, "该睡了", mark, y - h - 8, 26, "bold", GLASS, alpha)
