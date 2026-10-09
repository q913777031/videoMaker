"""复古插画风知识短视频引擎：Skia 逐帧绘制 → FFmpeg 编码，输出无声 9:16 竖屏视频。

一期视频 = 若干 Shot（镜头）；每个 Shot 带若干条字幕（即口播文案），字幕时长按字数自动排时，
镜头的画面函数以 G 对象读取"镜头内时间 / 第 k 条字幕已出现多久"来锚定动画。
"""

import math
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache
from multiprocessing import get_context
from pathlib import Path
from typing import Callable

import cv2
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

# 统一配色：米白纸张、墨色轮廓、暖金光线，少量红蓝强调
PAPER = "#F4EBD8"
INK = "#2B2420"
RED = "#C8452E"
BLUE = "#2E6AA7"
GOLD = "#E6A63A"
SKIN = "#F1C79E"
KRAFT = "#D8BF98"
CREAM = "#FBF5E6"
PALEGOLD = "#F7E2A6"
PALEBLUE = "#BCD2E3"
PALERED = "#EFC0AE"
GRAY = "#8D7F70"
LGRAY = "#CFC3AE"

STAGE_CX, STAGE_CY = 540, 880      # 画面主体区中心（上方留给标题，下方留给字幕与界面遮挡区）
CAPTION_Y = 1440                   # 字幕首行基线
TRANSITION = 0.45


# ------------------------------------------------------------------ 基础工具

def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def lerp(a: float, b: float, x: float) -> float:
    return a + (b - a) * x


def ease_out(x: float) -> float:
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in(x: float) -> float:
    x = clamp01(x)
    return x * x * x


def ease_io(x: float) -> float:
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_back(x: float, s: float = 1.7) -> float:
    x = clamp01(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def prog(t: float, start: float, dur: float = 0.5) -> float:
    return clamp01((t - start) / dur) if dur > 0 else float(t >= start)


@lru_cache(maxsize=None)
def rgb(c: str) -> tuple:
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def mix(c1: str, c2: str, x: float) -> str:
    a, b = rgb(c1), rgb(c2)
    return "#%02X%02X%02X" % tuple(int(lerp(a[i], b[i], x)) for i in range(3))


def col(c: str, a: float = 1.0) -> int:
    r, g, b = rgb(c)
    return skia.ColorSetARGB(int(255 * clamp01(a)), r, g, b)


class State:
    boil = 0          # 手绘抖动种子，约 7 次/秒变化


STATE = State()


# ------------------------------------------------------------------ 绘图原语

def _paint(color, a=1.0, stroke=False, w=0.0, blur=0.0):
    p = skia.Paint(AntiAlias=True, Color=col(color, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(w)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def _rough(p: skia.Paint, path: skia.Path, rough):
    if not rough:
        return
    b = path.getBounds()
    size = max(b.width(), b.height())
    if size < 16:
        return
    if rough is True:
        seg = min(22.0, max(8.0, size / 7))
        dev = min(2.0, max(0.7, size / 70))
    else:
        seg, dev = rough
    p.setPathEffect(skia.DiscretePathEffect.Make(seg, dev, STATE.boil))


def shape(c, path, fill=None, line=INK, lw=6.0, a=1.0, rough=True):
    """填充 + 墨色描边，描边带手绘抖动。"""
    if fill:
        p = _paint(fill, a)
        _rough(p, path, rough)
        c.drawPath(path, p)
    if line and lw > 0:
        p = _paint(line, a, True, lw)
        _rough(p, path, rough)
        c.drawPath(path, p)


def circ(c, x, y, r, fill=None, line=INK, lw=6.0, a=1.0, rough=True):
    if r <= 0:
        return
    shape(c, skia.Path.Circle(x, y, r), fill, line, lw, a, rough)


def oval(c, x, y, rx, ry, fill=None, line=INK, lw=6.0, a=1.0, rough=True):
    if rx <= 0 or ry <= 0:
        return
    shape(c, skia.Path.Oval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry)), fill, line, lw, a, rough)


def rect(c, x, y, w, h, r=0.0, fill=None, line=INK, lw=6.0, a=1.0, rough=True):
    """左上角 (x, y) 的圆角矩形。"""
    if w <= 0 or h <= 0:
        return
    rc = skia.Rect.MakeXYWH(x, y, w, h)
    path = skia.Path.RRect(rc, r, r) if r > 0 else skia.Path.Rect(rc)
    shape(c, path, fill, line, lw, a, rough)


def crect(c, cx, cy, w, h, r=0.0, fill=None, line=INK, lw=6.0, a=1.0, rough=True):
    """以中心定位的圆角矩形。"""
    rect(c, cx - w / 2, cy - h / 2, w, h, r, fill, line, lw, a, rough)


def poly(c, pts, fill=None, line=INK, lw=6.0, a=1.0, close=True, rough=True):
    path = skia.Path()
    path.moveTo(*pts[0])
    for q in pts[1:]:
        path.lineTo(*q)
    if close:
        path.close()
    shape(c, path, fill, line, lw, a, rough)


def stroke(c, pts, color=INK, lw=6.0, a=1.0, rough=False, smooth=False):
    """折线 / 平滑曲线描边（不填充）。"""
    if len(pts) < 2:
        return
    path = skia.Path()
    path.moveTo(*pts[0])
    if smooth and len(pts) > 2:
        for i in range(1, len(pts) - 1):
            mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
            path.quadTo(pts[i][0], pts[i][1], mx, my)
        path.lineTo(*pts[-1])
    else:
        for q in pts[1:]:
            path.lineTo(*q)
    p = _paint(color, a, True, lw)
    _rough(p, path, rough)
    c.drawPath(path, p)


def dline(c, p0, p1, color=INK, lw=6.0, a=1.0, dash=(18, 14)):
    p = _paint(color, a, True, lw)
    p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
    path = skia.Path()
    path.moveTo(*p0)
    path.lineTo(*p1)
    c.drawPath(path, p)


def partial_stroke(c, pts, p, color=INK, lw=6.0, a=1.0, smooth=True):
    """按进度 p∈[0,1] 描出折线的前一部分（用于画曲线 / 箭头动画）。"""
    if p <= 0 or len(pts) < 2:
        return
    path = skia.Path()
    path.moveTo(*pts[0])
    if smooth and len(pts) > 2:
        for i in range(1, len(pts) - 1):
            mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
            path.quadTo(pts[i][0], pts[i][1], mx, my)
        path.lineTo(*pts[-1])
    else:
        for q in pts[1:]:
            path.lineTo(*q)
    pm = skia.PathMeasure(path, False)
    seg = skia.Path()
    pm.getSegment(0, pm.getLength() * clamp01(p), seg, True)
    c.drawPath(seg, _paint(color, a, True, lw))


def arrow(c, p0, p1, color=INK, lw=8.0, a=1.0, head=26, p=1.0):
    """从 p0 指向 p1 的箭头，p 为画出进度。"""
    if p <= 0:
        return
    x0, y0 = p0
    x1 = x0 + (p1[0] - x0) * p
    y1 = y0 + (p1[1] - y0) * p
    stroke(c, [(x0, y0), (x1, y1)], color, lw, a)
    if p > 0.85:
        ang = math.atan2(p1[1] - y0, p1[0] - x0)
        for s in (-1, 1):
            stroke(c, [(x1, y1), (x1 - head * math.cos(ang + s * 0.5), y1 - head * math.sin(ang + s * 0.5))],
                   color, lw, a)


def glow(c, x, y, r, color=GOLD, a=0.5):
    """暖金色柔光。"""
    if r <= 0 or a <= 0:
        return
    sh = skia.GradientShader.MakeRadial((x, y), r, [col(color, a), col(color, 0)], [0, 1])
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=sh))


def shadow(c, x, y, rx, ry, a=0.22):
    """地面软阴影。"""
    p = _paint(INK, a, blur=10)
    c.drawOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry), p)


def drop_shadow(c, path, dx=6, dy=12, blur=9, a=0.22):
    c.save()
    c.translate(dx, dy)
    c.drawPath(path, _paint(INK, a, blur=blur))
    c.restore()


@contextmanager
def xf(c, x=0.0, y=0.0, rot=0.0, sx=1.0, sy=None):
    c.save()
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    c.scale(sx, sx if sy is None else sy)
    try:
        yield
    finally:
        c.restore()


@contextmanager
def layer(c, alpha=1.0):
    if alpha >= 0.999:
        yield
        return
    c.saveLayerAlpha(None, int(255 * clamp01(alpha)))
    try:
        yield
    finally:
        c.restore()


# ------------------------------------------------------------------ 文字

_FONT_FILES = {
    "serif": ["NotoSerifCJKsc-Bold.otf"],
    "black": ["NotoSerifCJKsc-Black.otf", "NotoSerifCJKsc-Bold.otf"],
    "sans": ["NotoSansCJKsc-Bold.otf"],
}


@lru_cache(maxsize=None)
def _typeface(name: str) -> skia.Typeface:
    for f in _FONT_FILES[name]:
        p = FONT_DIR / f
        if p.exists():
            tf = skia.Typeface.MakeFromFile(str(p))
            if tf:
                return tf
    tf = skia.Typeface.MakeFromFile("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
    if tf is None:
        raise RuntimeError("找不到中文字体，请先运行 python3 fetch_assets.py")
    return tf


@lru_cache(maxsize=256)
def get_font(name: str, size: float) -> skia.Font:
    f = skia.Font(_typeface(name), size)
    f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
    f.setSubpixel(True)
    return f


def text_w(s: str, size: float, font: str = "serif") -> float:
    return get_font(font, size).measureText(s)


def text(c, s, x, y, size, color=INK, font="serif", align="c", a=1.0, halo=None, halo_w=0.0):
    """y 为基线。halo 为描边色（用于压在插图上的文字）。"""
    if not s or a <= 0:
        return
    f = get_font(font, size)
    wid = f.measureText(s)
    if align == "c":
        x -= wid / 2
    elif align == "r":
        x -= wid
    if halo and halo_w > 0:
        p = _paint(halo, a, True, halo_w)
        c.drawString(s, x, y, f, p)
    c.drawString(s, x, y, f, _paint(color, a))


def parse_marks(s: str) -> list[tuple[str, bool]]:
    """把 "普通【高亮】普通" 拆成 [(文字, 是否高亮)]。"""
    out, cur, hi = [], "", False
    for ch in s:
        if ch == "【":
            if cur:
                out.append((cur, hi))
            cur, hi = "", True
        elif ch == "】":
            if cur:
                out.append((cur, hi))
            cur, hi = "", False
        else:
            cur += ch
    if cur:
        out.append((cur, hi))
    return out


def plain(s: str) -> str:
    return s.replace("【", "").replace("】", "").replace("|", "")


_NO_LINE_START = set("，。！？、；：”’）》】…,.!?;:)")


def wrap(s: str, size: float, maxw: float, font: str = "serif") -> list[list[tuple[str, bool]]]:
    """折行：文案里的 | 为手动换行；否则优先在标点后断开、两行尽量等宽，标点不出现在行首。"""
    if "|" in s:
        return [ln for part in s.split("|") for ln in wrap(part, size, maxw, font)]
    chars = [(ch, hi) for seg, hi in parse_marks(s) for ch in seg]
    f = get_font(font, size)
    widths = [f.measureText(ch) for ch, _ in chars]
    total = sum(widths)
    cuts: list[int] = []
    if total > maxw:
        if total <= 2 * maxw:
            best, acc, inq = None, 0.0, False
            for i in range(1, len(chars)):
                acc += widths[i - 1]
                if chars[i - 1][0] == "“":
                    inq = True
                elif chars[i - 1][0] == "”":
                    inq = False
                if acc > maxw or total - acc > maxw or chars[i][0] in _NO_LINE_START:
                    continue
                score = abs(acc - (total - acc))
                if chars[i - 1][0] in "，。！？、；：”）…":
                    score -= 140
                if inq:
                    score += 260
                if best is None or score < best[0]:
                    best = (score, i)
            if best:
                cuts = [best[1]]
        if not cuts:
            n = max(2, math.ceil(total / maxw))
            target, cw = total / n, 0.0
            for i, w in enumerate(widths):
                if cw > 0 and cw + w > min(maxw, target * 1.12) and chars[i][0] not in _NO_LINE_START and len(cuts) < n - 1:
                    cuts.append(i)
                    cw = 0.0
                cw += w
    lines, prev = [], 0
    for ct in cuts + [len(chars)]:
        lines.append(chars[prev:ct])
        prev = ct
    out = []
    for ln in lines:
        segs = []
        for ch, hi in ln:
            if segs and segs[-1][1] == hi:
                segs[-1] = (segs[-1][0] + ch, hi)
            else:
                segs.append((ch, hi))
        out.append(segs)
    return out


def rich_line(c, segs, cx, y, size, color=INK, hi=RED, font="serif", a=1.0, halo=None, halo_w=0.0):
    f = get_font(font, size)
    total = sum(f.measureText(t) for t, _ in segs)
    x = cx - total / 2
    for t, h in segs:
        if halo:
            c.drawString(t, x, y, f, _paint(halo, a, True, halo_w))
        c.drawString(t, x, y, f, _paint(hi if h else color, a))
        x += f.measureText(t)


def rich(c, s, cx, y, size, lh=None, color=INK, hi=RED, font="serif", a=1.0, maxw=900, halo=None, halo_w=0.0):
    lines = wrap(s, size, maxw, font)
    lh = lh or size * 1.4
    for i, segs in enumerate(lines):
        rich_line(c, segs, cx, y + i * lh, size, color, hi, font, a, halo, halo_w)
    return len(lines)


# ------------------------------------------------------------------ 时间轴数据模型

@dataclass
class Shot:
    cues: list                      # 字幕（口播）列表，元素为 str 或 (str, 秒数)
    draw: Callable                  # draw(g: G)
    tag: str = ""                   # 左上角小标签，例如"教学改编 · 虚构名单"
    pre: float = 0.0                # 第一条字幕前的留白
    tail: float = 0.5               # 最后一条字幕后的停留
    zoom: tuple = (1.0, 1.035)      # 镜头缓推
    focus: tuple = (STAGE_CX, STAGE_CY)
    # 以下由 Episode.build 填充
    start: float = 0.0
    end: float = 0.0
    cue_t: list = field(default_factory=list)


@dataclass
class Episode:
    name: str
    shots: list
    gap: float = 0.2
    sec_per_char: float = 0.205
    base: float = 0.65
    lead: float = 0.35              # 开头第一条字幕出现前的间隔
    total: float = 0.0
    cues: list = field(default_factory=list)   # [(start, end, text)]

    def build(self):
        t = 0.0
        self.cues = []
        for i, s in enumerate(self.shots):
            s.start = t
            t += s.pre + (self.lead if i == 0 else 0)
            s.cue_t = []
            for cue in s.cues:
                text_, dur = (cue, None) if isinstance(cue, str) else cue
                n = sum(1 for ch in plain(text_) if ch not in "，。！？、；：“”‘’…— ")
                d = dur if dur else self.base + self.sec_per_char * n
                if len(wrap(text_, 56, 900)) > 2:
                    print(f"警告：字幕超过两行：{plain(text_)}", file=sys.stderr)
                s.cue_t.append(t)
                self.cues.append((t, t + d, text_))
                t += d + self.gap
            t += s.tail - self.gap
            s.end = t
        self.total = t
        return self

    def chars(self) -> int:
        return sum(len(plain(t)) for _, _, t in self.cues)


class G:
    """画面函数拿到的上下文：t 为镜头内时间。"""

    def __init__(self, c, t, shot: Shot):
        self.c, self.t, self.shot = c, t, shot
        self.dur = shot.end - shot.start

    def cue(self, k: int) -> float:
        """第 k 条字幕已出现多少秒（尚未出现时为负）。"""
        return self.t - (self.shot.cue_t[k] - self.shot.start)

    def p(self, start, dur=0.5, ease=ease_out) -> float:
        return ease(prog(self.t, start, dur))

    def pop(self, start, dur=0.5) -> float:
        return ease_back(prog(self.t, start, dur))

    def pc(self, k, off=0.0, dur=0.5, ease=ease_out) -> float:
        """以第 k 条字幕出现为起点的进度。"""
        return ease(prog(self.cue(k), off, dur))

    def popc(self, k, off=0.0, dur=0.5) -> float:
        return ease_back(prog(self.cue(k), off, dur))


# ------------------------------------------------------------------ 背景

def _make_paper() -> skia.Image:
    rng = np.random.default_rng(7)
    img = np.ones((H, W, 3), np.float32) * np.array([244, 235, 216], np.float32)
    low = rng.normal(0, 1, (40, 23)).astype(np.float32)
    up = cv2.resize(low, (W, H), interpolation=cv2.INTER_CUBIC)
    img += up[..., None] * np.array([2.6, 2.6, 3.2], np.float32)
    img += (rng.normal(0, 1, (H, W)) * 1.5).astype(np.float32)[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W / 2) / (W * 0.78), (yy - H / 2) / (H * 0.66))
    vig = np.clip(r - 0.5, 0, 1) ** 1.5
    img -= vig[..., None] * np.array([46, 62, 88], np.float32)
    gl = np.exp(-(((xx - W * 0.8) / (W * 0.65)) ** 2 + ((yy - H * 0.24) / (H * 0.26)) ** 2))
    img += gl[..., None] * np.array([9, 3, -16], np.float32)
    rgba = np.dstack([np.clip(img, 0, 255).astype(np.uint8), np.full((H, W), 255, np.uint8)])
    return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)


_BG = None


def bg_image() -> skia.Image:
    global _BG
    if _BG is None:
        _BG = _make_paper()
    return _BG


# ------------------------------------------------------------------ 合成

def _shot_at(ep: Episode, T: float) -> int:
    for i, s in enumerate(ep.shots):
        if T < s.end:
            return i
    return len(ep.shots) - 1


def _draw_shot(c, ep, k, local_t):
    s = ep.shots[k]
    dur = s.end - s.start
    z = lerp(s.zoom[0], s.zoom[1], clamp01(local_t / dur))
    c.save()
    c.translate(s.focus[0], s.focus[1])
    c.scale(z, z)
    c.translate(-s.focus[0], -s.focus[1])
    s.draw(G(c, local_t, s))
    c.restore()


def _draw_caption(c, ep: Episode, T: float):
    for (a, b, txt) in ep.cues:
        if a - 0.01 <= T < b + ep.gap:
            fin = ease_out(prog(T, a, 0.22))
            fout = 1 - ease_in(prog(T, b - 0.05, 0.2 + ep.gap)) if T > b - 0.05 else 1.0
            alpha = fin * fout
            lines = wrap(txt, 56, 900)
            n = len(lines)
            y0 = CAPTION_Y + (0 if n >= 2 else 38) + (1 - fin) * 16
            for i, segs in enumerate(lines):
                rich_line(c, segs, W / 2, y0 + i * 80, 56, INK, RED, "serif", alpha, PAPER, 12)


def _draw_tag(c, s: Shot, T: float):
    if not s.tag:
        return
    a = ease_out(prog(T - s.start, 0.1, 0.4))
    f = get_font("sans", 30)
    wid = f.measureText(s.tag) + 44
    with layer(c, a):
        rect(c, 56, 150, wid, 56, 28, CREAM, INK, 4, rough=False)
        text(c, s.tag, 56 + 22, 190, 30, INK, "sans", "l")


def render_frame(ep: Episode, surface: skia.Surface, frame: int):
    T = frame / FPS
    c = surface.getCanvas()
    c.restoreToCount(1)
    c.resetMatrix()
    STATE.boil = int(T * 7)
    c.drawImage(bg_image(), 0, 0)
    k = _shot_at(ep, T)
    s = ep.shots[k]
    lt = T - s.start
    if k > 0 and lt < TRANSITION:
        a = ease_io(lt / TRANSITION)
        prev = ep.shots[k - 1]
        with layer(c, 1 - a):
            c.save()
            c.translate(-70 * a, 0)
            _draw_shot(c, ep, k - 1, (prev.end - prev.start) + lt)
            c.restore()
        with layer(c, a):
            c.save()
            c.translate(70 * (1 - a), 0)
            _draw_shot(c, ep, k, lt)
            c.restore()
    else:
        _draw_shot(c, ep, k, lt)
    _draw_tag(c, s, T)
    _draw_caption(c, ep, T)


# ------------------------------------------------------------------ 输出

_EP = None
_SURF = None
_ARR = None


def _worker(frame: int) -> bytes:
    global _SURF, _ARR
    if _SURF is None:
        _ARR = np.zeros((H, W, 4), np.uint8)
        _SURF = skia.Surface(_ARR)
    render_frame(_EP, _SURF, frame)
    return _ARR.tobytes()


def render(ep: Episode, out_path: str, workers: int = 4):
    """逐帧渲染并以 libx264 编码为无音轨 MP4。"""
    global _EP
    _EP = ep
    n = int(math.ceil(ep.total * FPS))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-maxrate", "2200k", "-bufsize", "4400k",
           "-tune", "animation",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        with get_context("fork").Pool(workers) as pool:
            for i, buf in enumerate(pool.imap(_worker, range(n), chunksize=6)):
                proc.stdin.write(buf)
                if i % 300 == 0:
                    print(f"  {ep.name}: {i}/{n}", file=sys.stderr, flush=True)
    finally:
        proc.stdin.close()
        rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg exited with code {rc}")


def still(ep: Episode, T: float, path: str):
    """导出某一时刻的静帧，用于逐镜检查。"""
    arr = np.zeros((H, W, 4), np.uint8)
    surf = skia.Surface(arr)
    render_frame(ep, surf, int(round(T * FPS)))
    import PIL.Image as I
    I.fromarray(arr).convert("RGB").save(path)
