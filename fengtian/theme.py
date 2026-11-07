"""《丰田模式》每讲一个样式：主题色、纸张底色与纹理、页眉风格、开场钩子、切屏转场。

分镜模块只需声明本讲 THEME（见 THEMES；第 02 讲起传给 Lesson(theme=...)，第 01 讲在模块里写 THEME = theme.get("01")），
build.py 按 M.THEME 画纸张、页眉、字幕条、封面，并在画白板内容时把线条色换成本讲纸张上看得清的颜色：
- 浅色纸：原先在白板上对比度不到 4.5 的墨色（红、蓝、绿、橙、灰）不动；够 4.5 的保证换纸后仍 ≥ 4.5（不够就压暗），
  填充色（衣服、帽子、白卡片）不动；纸色 #FBFBF9 的遮挡块换成本讲纸色。
- 深色底（黑板、蓝图）：按明度反相——黑线变粉笔白、白色填充（头、卡片）变底色、浅色填充变暗色调，
  彩色线条提亮到对比度 ≥ 4.5，人物线稿一样看得清。
转场（THEME["move"]）：在原来 1.3 秒缓入缓出的基础上换不同走法，都不硬切：
  ease 直线缓移 / pullpush 拉远再推近 / pan 先横移再落下 / drop 先竖向下移再横向、轻微回弹 / tilt 移动中轻微旋转 /
  arc 弧线走位 / swing 到位后轻微回弹 / wipe 翻页式擦除（换区块时新一页从右边盖过来，同区块内仍缓移）。
"""

import colorsys
import functools
import math
import random

import skia

from engine import gfx
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp

OLD_PAPER = (251, 251, 249)

# 每讲一套；相邻两讲纸色、纹理、主题色、页眉、开场、转场都不同
THEMES = {
    "01": dict(name="米白横线本", acc="#C8102E", paper="#F8F1E2", pattern="ruled", pat="#B9CBE0", margin="#E8A0A0",
               header="pill", hook="stamp3", move="pullpush", move_s=1.4),
    "02": dict(name="浅灰蓝点阵", acc="#2556A6", paper="#E5ECF3", pattern="dots", pat="#9FB1C6",
               header="tab", hook="pile", move="pan", move_s=1.35),
    "03": dict(name="淡黄格子纸", acc="#C2410C", paper="#FBF1C8", pattern="grid", pat="#E3CF86",
               header="circle", hook="curve", move="tilt", move_s=1.4),
    "04": dict(name="牛皮纸", acc="#7A2E12", paper="#E2CBA2", pattern="kraft", pat="#B99A6B",
               header="stamp", hook="bars", move="drop", move_s=1.3),
    "05": dict(name="浅绿方格", acc="#1F7044", paper="#E3F0E1", pattern="grid", pat="#A9CDA7", grid=60,
               header="bar", hook="checklist", move="wipe", move_s=1.0),
    "06": dict(name="墨绿黑板", acc="#F2C94C", paper="#22382F", pattern="chalk", pat="#FFFFFF", dark=True,
               header="pill", hook="sticky", move="arc", move_s=1.45),
    "07": dict(name="淡粉信纸", acc="#9C2F63", paper="#F8E6E4", pattern="ruled", pat="#E8B9B5", margin=None,
               header="circle", hook="doorsign", move="swing", move_s=1.25),
    "08": dict(name="薰衣草点阵", acc="#5537A0", paper="#ECE7F6", pattern="dots", pat="#B7A9D8",
               header="stamp", hook="mole", move="pullpush", move_s=1.4),
    "09": dict(name="蓝图纸", acc="#7FD8F2", paper="#1C2C4A", pattern="blueprint", pat="#6E8FC4", dark=True,
               header="tab", hook="reject", move="wipe", move_s=1.05),
    "10": dict(name="暖杏方格", acc="#0F6E6E", paper="#F6E3CC", pattern="grid", pat="#E2BF98", grid=100,
               header="bar", hook="treadmill", move="tilt", move_s=1.4),
    "11": dict(name="浅橙点阵", acc="#1E4B7A", paper="#FCE6D0", pattern="dots", pat="#E8B088", grid=56,
               header="stamp", hook="clock8", move="swing", move_s=1.3),
    "12": dict(name="方眼本", acc="#A8401A", paper="#E4EFEC", pattern="graph", pat="#9EC3BA", grid=44,
               header="circle", hook="desktop", move="arc", move_s=1.45),
    "13": dict(name="石墨板", acc="#FFB23F", paper="#272B33", pattern="dots", pat="#5A6372", grid=80, dark=True,
               header="tab", hook="mailfly", move="pan", move_s=1.25),
    "14": dict(name="天蓝横线", acc="#D9480F", paper="#D6E8F6", pattern="ruled", pat="#9DBFDD", margin=None,
               header="pill", hook="startlights", move="pullpush", move_s=1.35),
    "15": dict(name="白色工程纸", acc="#C62828", paper="#F6F8FB", pattern="grid", pat="#B9CCE6", grid=60,
               header="stamp", hook="slides", move="wipe", move_s=1.0),
    "16": dict(name="深褐黑板", acc="#7ED6A0", paper="#3A2B22", pattern="chalk", pat="#FFFFFF", dark=True,
               header="bar", hook="qmarks", move="drop", move_s=1.3),
}

DEFAULT = dict(name="白板", acc="#C8102E", paper="#FBFBF9", pattern="plain", pat="#E9ECEF", header="pill",
               hook="title", move="ease", move_s=1.3)


def get(nn):
    t = dict(DEFAULT)
    t.update(THEMES.get(nn, {}))
    return finish(t)


def finish(t):
    """补齐派生色：页眉/字幕条用的墨色、次要字色、分隔线、外框、横屏封面衬底。"""
    t = dict(DEFAULT, **t)
    p = gfx.rgb(t["paper"])
    if t.get("dark"):
        t.setdefault("ink", "#F1EEE4")
        t.setdefault("ink2", "#C9CCC4")
        t.setdefault("line", hexc(mix(p, (255, 255, 255), 0.22)))
        t.setdefault("band", hexc(mix(p, (0, 0, 0), 0.25)))
        t.setdefault("outside", hexc(mix(p, (0, 0, 0), 0.35)))
        t.setdefault("mat", hexc(mix(p, (0, 0, 0), 0.18)))
        t.setdefault("badge_ink", "#1B1B1F")
    else:
        t.setdefault("ink", "#24293B")
        t.setdefault("ink2", "#5E6475")
        t.setdefault("line", hexc(mix(p, (0, 0, 0), 0.13)))
        t.setdefault("band", hexc(mix(p, (255, 255, 255), 0.55)))
        t.setdefault("outside", hexc(mix(p, (60, 60, 70), 0.14)))
        t.setdefault("mat", hexc(mix(p, (120, 100, 80), 0.10)))
        t.setdefault("badge_ink", "#FFFFFF")
    t.setdefault("chalk", "#EDEBE3")
    return t


# ================================================================ 颜色

def mix(a, b, k):
    a, b = gfx.rgb(a), gfx.rgb(b)
    return tuple(int(round(x + (y - x) * k)) for x, y in zip(a, b))


def hexc(c):
    return "#%02X%02X%02X" % tuple(gfx.rgb(c))


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = gfx.rgb(c)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _hls(c):
    r, g, b = (v / 255 for v in gfx.rgb(c))
    return colorsys.rgb_to_hls(r, g, b)


def _rgb(h, l, s):
    return tuple(int(round(v * 255)) for v in colorsys.hls_to_rgb(h, clamp01(l), clamp01(s)))


def _yellowish(h, s):
    return 38 / 360 <= h <= 70 / 360 and s > 0.5


def remap_light(c, paper):
    """浅色纸：墨色保证对比度不低于在原白板上的水平（最高要求 4.5）；填充色不动。"""
    c = gfx.rgb(c)
    if c == OLD_PAPER:
        return gfx.rgb(paper)
    h, l, s = _hls(c)
    if l >= 0.62 or _yellowish(h, s):
        return c
    need = min(4.5, contrast(c, OLD_PAPER))
    out = c
    for _ in range(40):
        if contrast(out, paper) >= need - 1e-3:
            break
        l *= 0.94
        out = _rgb(h, l, s)
    return out


def remap_dark(c, paper, chalk):
    """深色底：明度反相（白→底色、黑→粉笔白），墨色提亮到对比度 ≥ 4.5，浅色填充变成暗色调。"""
    c = gfx.rgb(c)
    if c == OLD_PAPER:
        return gfx.rgb(paper)
    h, l, s = _hls(c)
    if s < 0.15 or l > 0.97 or l < 0.03:
        return mix(paper, chalk, clamp01((1 - l) / 0.87))
    lb = _hls(paper)[1]
    ink = l < 0.62
    l2 = lb + (1 - l) * (0.92 - lb)
    s2 = min(s, 0.72)
    if ink:
        l2 = max(l2, 0.70)
    out = _rgb(h, l2, s2)
    if ink:
        for _ in range(30):
            if contrast(out, paper) >= 4.6:
                break
            l2 += 0.02
            out = _rgb(h, l2, s2)
    return out


class Recolor:
    """with Recolor(theme): 块内所有经 engine.gfx.col 的颜色（白板线条、填充、字）换成本讲纸张上的颜色。"""

    def __init__(self, t):
        self.t = t
        self.on = t["paper"].upper() != "#FBFBF9"
        paper, chalk = gfx.rgb(t["paper"]), gfx.rgb(t["chalk"])
        dark = t.get("dark")
        keep = {gfx.rgb(t["acc"])}            # 本讲主题色（开场大字、强调）按原色画

        @functools.lru_cache(maxsize=None)
        def f(c):
            if c in keep:
                return c
            return remap_dark(c, paper, chalk) if dark else remap_light(c, paper)
        self.f = f

    def __enter__(self):
        if self.on:
            self.saved = gfx.col
            f, rgb = self.f, gfx.rgb

            def col(c, a=1.0):
                r, g, b = f(tuple(rgb(c)))
                return skia.Color(r, g, b, int(255 * clamp01(a)))
            gfx.col = col
        return self

    def __exit__(self, *a):
        if self.on:
            gfx.col = self.saved


# ================================================================ 纸张

@functools.lru_cache(maxsize=8)
def _speckles(bw, bh, n, seed):
    rng = random.Random(seed)
    return [(rng.uniform(0, bw), rng.uniform(0, bh), rng.uniform(0.6, 1.0)) for _ in range(n)]


def _paint(c, a=1.0, w=0.0, blur=0.0):
    r, g, b = gfx.rgb(c)
    p = skia.Paint(AntiAlias=True, Color=skia.Color(r, g, b, int(255 * clamp01(a))))
    if w:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(w)
        p.setStrokeCap(skia.Paint.kRound_Cap)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def board_bg(c, board, t):
    """白板底：纸色 + 纹理（在白板坐标里画，跟着镜头走）。替换 whiteboard.engine._board_bg。"""
    BW, BH = board.BW, board.BH
    c.drawColor(skia.Color(*gfx.rgb(t["outside"])))
    c.drawRect(skia.Rect.MakeWH(BW, BH), _paint(t["paper"]))
    pat, pc = t["pattern"], t["pat"]
    if pat == "ruled":
        for y in range(160, BH, 96):
            c.drawLine(0, y, BW, y, _paint(pc, 0.55, 3))
        if t.get("margin"):
            for x0 in range(220, BW, 1600):
                c.drawLine(x0, 0, x0, BH, _paint(t["margin"], 0.45, 4))
    elif pat in ("grid", "blueprint"):
        g = t.get("grid", 80)
        a = 0.5 if pat == "grid" else 0.32
        pts_v = [skia.Point(x, yy) for x in range(0, BW, g) for yy in (0, BH)]
        pts_h = [skia.Point(xx, y) for y in range(0, BH, g) for xx in (0, BW)]
        p = _paint(pc, a, 2.2)
        c.drawPoints(skia.Canvas.kLines_PointMode, pts_v, p)
        c.drawPoints(skia.Canvas.kLines_PointMode, pts_h, p)
        if pat == "blueprint":
            big = g * 5
            p2 = _paint(pc, 0.55, 3.5)
            c.drawPoints(skia.Canvas.kLines_PointMode,
                         [skia.Point(x, yy) for x in range(0, BW, big) for yy in (0, BH)], p2)
            c.drawPoints(skia.Canvas.kLines_PointMode,
                         [skia.Point(xx, y) for y in range(0, BH, big) for xx in (0, BW)], p2)
    elif pat == "graph":                      # 方眼本：细方格，每 5 格一条粗线
        g = t.get("grid", 44)
        for step, a, w in ((g, 0.38, 1.6), (g * 5, 0.6, 3.2)):
            p = _paint(pc, a, w)
            c.drawPoints(skia.Canvas.kLines_PointMode, [skia.Point(x, yy) for x in range(0, BW, step) for yy in (0, BH)], p)
            c.drawPoints(skia.Canvas.kLines_PointMode, [skia.Point(xx, y) for y in range(0, BH, step) for xx in (0, BW)], p)
    elif pat == "dots":
        g = t.get("grid", 70)
        p = _paint(pc, 0.75, 7)
        c.drawPoints(skia.Canvas.kPoints_PointMode,
                     [skia.Point(x, y) for x in range(35, BW, g) for y in range(35, BH, g)], p)
    elif pat == "kraft":
        sp = _speckles(BW, BH, 9000, 4)
        for alpha, sel in ((0.35, sp[::2]), (0.22, sp[1::2])):
            c.drawPoints(skia.Canvas.kPoints_PointMode, [skia.Point(x, y) for x, y, _ in sel], _paint(pc, alpha, 5))
        for x0, y0, r in ((900, 1500, 700), (3600, 4200, 900), (1400, 7600, 800), (3800, 9800, 700)):
            c.drawCircle(x0, y0, r, _paint("#FFFFFF", 0.16, blur=180))
    elif pat == "chalk":
        for x0, y0, r in ((700, 1700, 500), (2600, 3800, 700), (1200, 5000, 500), (2800, 300, 400), (900, 6600, 600),
                          (3900, 8200, 700), (1800, 10200, 600)):
            c.drawCircle(x0, y0, r, _paint(pc, 0.045, blur=160))
        sp = _speckles(BW, BH, 5000, 9)
        c.drawPoints(skia.Canvas.kPoints_PointMode, [skia.Point(x, y) for x, y, _ in sp], _paint(pc, 0.07, 4))
    else:
        for x0, y0, r in ((700, 1700, 500), (2600, 3800, 700), (1200, 5000, 500), (2800, 300, 400), (900, 6600, 600)):
            c.drawCircle(x0, y0, r, _paint("#E9ECEF", 0.6, blur=120))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, BW, BH), _paint(mix(t["outside"], (0, 0, 0), 0.08), 1, 30))


# ================================================================ 转场

def _mixv(a, z, k):
    return lerp(a[0], z[0], k), lerp(a[1], z[1], k), math.exp(lerp(math.log(a[2]), math.log(z[2]), k))


def transition(prev, cur, t, style, dur, j=0):
    """切屏镜头：从上一屏终了视角 prev 到本屏视角 cur，镜头开始后 t 秒的 (视角, 旋转角)。"""
    if prev == cur or style == "wipe":
        return cur, 0.0
    k = clamp01(t / dur)
    e = ease_in_out(k)
    if style == "pullpush":
        cx, cy, z = _mixv(prev, cur, e)
        return (cx, cy, z * (1 - 0.30 * math.sin(math.pi * k))), 0.0
    if style == "pan":
        ex, ey = ease_in_out(clamp01(k * 1.45)), ease_in_out(clamp01(k * 1.45 - 0.45))
        z = math.exp(lerp(math.log(prev[2]), math.log(cur[2]), e)) * (1 - 0.08 * math.sin(math.pi * k))
        return (lerp(prev[0], cur[0], ex), lerp(prev[1], cur[1], ey), z), 0.0
    if style == "drop":
        ey = ease_out_back(clamp01(k * 1.3)) if k < 1 else 1.0
        ey = lerp(ease_in_out(clamp01(k * 1.3)), ey, 0.45)
        ex = ease_in_out(clamp01(k * 1.4 - 0.4))
        z = math.exp(lerp(math.log(prev[2]), math.log(cur[2]), e))
        return (lerp(prev[0], cur[0], ex), lerp(prev[1], cur[1], ey), z), 0.0
    if style == "tilt":
        sgn = 1 if j % 2 else -1
        cx, cy, z = _mixv(prev, cur, e)
        return (cx, cy, z * (1 - 0.06 * math.sin(math.pi * k))), sgn * 3.2 * math.sin(math.pi * k)
    if style == "arc":
        dx, dy = cur[0] - prev[0], cur[1] - prev[1]
        d = math.hypot(dx, dy) or 1.0
        sgn = 1 if j % 2 else -1
        bx, by = -dy / d * d * 0.32 * sgn, dx / d * d * 0.32 * sgn
        mx, my = (prev[0] + cur[0]) / 2 + bx, (prev[1] + cur[1]) / 2 + by
        u = e
        x = (1 - u) ** 2 * prev[0] + 2 * (1 - u) * u * mx + u * u * cur[0]
        y = (1 - u) ** 2 * prev[1] + 2 * (1 - u) * u * my + u * u * cur[1]
        z = math.exp(lerp(math.log(prev[2]), math.log(cur[2]), e)) * (1 - 0.12 * math.sin(math.pi * k))
        return (x, y, z), 0.0
    if style == "swing":
        es = ease_out_back(clamp01(k)) if k < 1 else 1.0
        es = lerp(e, es, 0.55)
        cx, cy = lerp(prev[0], cur[0], es), lerp(prev[1], cur[1], es)
        z = math.exp(lerp(math.log(prev[2]), math.log(cur[2]), e))
        return (cx, cy, z), 0.0
    return _mixv(prev, cur, e), 0.0


def keep_on_board(view, board, base=None):
    """转场途中（拉远、弧线、回弹）不让镜头拍到白板外：把中心收回到白板里。base 为本屏原视角，原视角本身就越界时不管。"""
    cx, cy, z = view
    lo_x, hi_x = 600 / z, board.BW - 600 / z
    lo_y, hi_y = 470 / z, board.BH - 900 / z
    if lo_x < hi_x:
        cx = min(max(cx, lo_x), hi_x)
    if lo_y < hi_y:
        cy = min(max(cy, lo_y), hi_y)
    return cx, cy, z


def rot_at(board, T, style, dur):
    """本帧画布旋转角（只有 tilt 转场有）。"""
    if style != "tilt":
        return 0.0
    ep = board.ep
    j = ep.shot_at(T)
    if j == 0:
        return 0.0
    prev, cur = board.end_view(j - 1), board.views[j]
    return transition(prev, cur, T - ep.shots[j].t0, style, dur, j)[1]


def wipe_at(board, T, groups, dur):
    """翻页式擦除：换区块的切屏开始后 dur 秒内返回翻页边位置 0–1（1 = 刚开始，整屏还是旧页），否则 None。"""
    ep = board.ep
    j = ep.shot_at(T)
    if j == 0 or groups[j] == groups[j - 1]:
        return None
    t = T - ep.shots[j].t0
    if t >= dur:
        return None
    return 1 - ease_in_out(clamp01(t / dur))


def camera_fn(lesson_like, style, dur, base_z=1.0):
    """供分镜模块 camera() 用：返回 (board, T) -> (cx, cy, z, sx, sy)。lesson_like 只要求有 core 拍点（用 board.ep）。"""
    from adler import core

    def camera(board, T):
        ep_ = board.ep
        j_ = ep_.shot_at(T)
        s_ = ep_.shots[j_]
        t_ = T - s_.t0
        cur = board.views[j_]
        prev = board.end_view(j_ - 1) if j_ > 0 else cur
        view, _ = transition(prev, cur, t_, style, dur, j_)
        if 0 < t_ < dur and prev != cur:
            view = keep_on_board(view, board)
        for kb_, target, d in board.moves.get(j_, []):
            t0_ = board.t_of(j_, kb_)
            if T < t0_:
                break
            view = _mixv(view, target, ease_in_out(clamp01((T - t0_) / d)))
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
    return camera


def report(t):
    """主题对比度摘要（--sheet 打印）。"""
    p = t["paper"]
    rows = [f"样式「{t['name']}」纸 {hexc(p)} 主题色 {t['acc']} 开场 {t['hook']} 转场 {t['move']}"]
    rows.append(f"  对比度：页眉字 {contrast(t['ink'], p):.1f}  主题色/纸 {contrast(t['acc'], p):.1f}  "
                f"期号字/主题色 {contrast(t['badge_ink'], t['acc']):.1f}  字幕字/字幕条 {contrast(t['ink'], t['band']):.1f}")
    rc = Recolor(t)
    inks = {"黑线": "#1E1E24", "红": "#D23A2E", "蓝": "#2F62B8", "绿": "#2E8A57", "橙": "#E07B24", "灰": "#6B6B6B"}
    rows.append("  白板墨色/纸：" + "  ".join(f"{k} {contrast(rc.f(gfx.rgb(v)) if rc.on else gfx.rgb(v), p):.1f}"
                                         for k, v in inks.items()))
    return "\n".join(rows)
