"""逐笔书法：按 Make Me a Hanzi 的笔画轮廓与笔顺中线，一笔一笔写出汉字，带湿墨晕边与飞白。

数据：assets/hanzi/graphics.txt（Arphic Public License，源自 Arphic PL KaitiM GB / UKai 楷体）。
坐标：每字 1024 方格，y 轴向上，基线约 900；绘制时翻转为屏幕坐标。
"""

import functools
import json
import math
import re
from pathlib import Path

import numpy as np
import skia

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "hanzi" / "graphics.txt"
SUBSET = ROOT / ".cache" / "chuanxilu" / "hanzi_subset.json"
_TOKEN = re.compile(r"[MLQCZ]|-?\d+(?:\.\d+)?")


def _parse(d: str) -> skia.Path:
    """解析 Make Me a Hanzi 的 SVG 路径（只含 M/L/Q/C/Z 绝对坐标）。"""
    p, tok, i, cmd = skia.Path(), _TOKEN.findall(d), 0, ""
    while i < len(tok):
        if tok[i] in "MLQCZ":
            cmd, i = tok[i], i + 1
            if cmd == "Z":
                p.close()
            continue
        n = {"M": 2, "L": 2, "Q": 4, "C": 6}[cmd]
        v = [float(x) for x in tok[i:i + n]]
        i += n
        if cmd == "M":
            p.moveTo(*v)
        elif cmd == "L":
            p.lineTo(*v)
        elif cmd == "Q":
            p.quadTo(*v)
        else:
            p.cubicTo(*v)
    return p


@functools.lru_cache(maxsize=1)
def _table() -> dict:
    SUBSET.parent.mkdir(parents=True, exist_ok=True)
    return json.loads(SUBSET.read_text(encoding="utf-8")) if SUBSET.exists() else {}


def prepare(text: str):
    """把用到的字从 30MB 原始数据抽进小缓存（构建前调用一次）。缺字抛 KeyError，避免成片里出现空白字。"""
    need = {ch for ch in text if "一" <= ch <= "鿿"}
    table = dict(_table())
    missing = need - set(table)
    if missing:
        with DATA.open(encoding="utf-8") as f:
            for raw in f:
                ch = raw[14:15] if raw.startswith('{"character":"') else ""
                if ch in missing:
                    table[ch] = json.loads(raw)
        SUBSET.write_text(json.dumps(table, ensure_ascii=False), encoding="utf-8")
        _table.cache_clear()
        _glyph.cache_clear()
    lost = need - set(_table())
    if lost:
        raise KeyError(f"no stroke data for: {''.join(sorted(lost))}")


@functools.lru_cache(maxsize=512)
def _glyph(ch: str):
    g = _table()[ch]
    strokes = [_parse(d) for d in g["strokes"]]
    medians = [np.array(m, float) for m in g["medians"]]
    lens = [float(np.sum(np.linalg.norm(np.diff(m, axis=0), axis=1))) + 40 for m in medians]
    return strokes, medians, lens


def _partial_median(m: np.ndarray, q: float) -> skia.Path:
    seg = np.linalg.norm(np.diff(m, axis=0), axis=1)
    total, want = float(seg.sum()), float(seg.sum()) * q
    p = skia.Path()
    p.moveTo(*m[0])
    acc = 0.0
    for k, s in enumerate(seg):
        if acc + s >= want:
            r = (want - acc) / max(s, 1e-6)
            p.lineTo(*(m[k] + (m[k + 1] - m[k]) * r))
            break
        p.lineTo(*m[k + 1])
        acc += s
    if total < 1:
        p.lineTo(m[0][0] + 0.5, m[0][1])
    return p


_REVEAL = skia.Paint(Style=skia.Paint.kStroke_Style, StrokeWidth=170, StrokeCap=skia.Paint.kRound_Cap,
                     StrokeJoin=skia.Paint.kRound_Join)


@functools.lru_cache(maxsize=1)
def _grain() -> skia.Shader:
    """飞白纹理：沿笔锋方向的细长干笔丝，用作 DstOut 擦除。"""
    rng = np.random.default_rng(7)
    h, w = 256, 256
    a = np.zeros((h, w), np.float32)
    for _ in range(140):
        y = rng.integers(0, h)
        x0 = rng.integers(0, w)
        ln = rng.integers(20, 120)
        a[y, x0:x0 + ln] = rng.uniform(0.25, 0.9)
    a = np.clip(a + rng.random((h, w)) * 0.12, 0, 1)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 3] = (a * 255).astype(np.uint8)
    img = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    return img.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat)


def char_duration(ch: str) -> float:
    """一个字的相对书写长度（各笔中线长度之和，含起落笔停顿）。"""
    if not ("一" <= ch <= "鿿"):
        return 0.0
    return sum(_glyph(ch)[2])


def draw_char(c: skia.Canvas, ch: str, x: float, y: float, size: float, p: float, color=(30, 27, 24),
              alpha: float = 1.0, dry: float = 0.35, wet: float = 0.35):
    """在 (x, y) 为中心、边长 size 的方格内写字；p ∈ [0, 1] 为书写进度（按笔画长度分配时间）。"""
    if p <= 0 or alpha <= 0:
        return
    strokes, medians, lens = _glyph(ch)
    total = sum(lens)
    k = size / 1024
    c.save()
    c.translate(x - size / 2, y - size / 2)
    c.scale(k, -k)
    c.translate(0, -900)
    col = skia.Color(*color, int(255 * alpha))
    c.saveLayer()
    done = p * total
    acc = 0.0
    for path, med, ln in zip(strokes, medians, lens):
        if done <= acc:
            break
        q = min(1.0, (done - acc) / (ln - 40)) if ln > 40 else 1.0
        acc += ln
        shape = path
        if q < 1.0:
            reveal = skia.Path()
            _REVEAL.getFillPath(_partial_median(med, q), reveal)
            shape = skia.Op(path, reveal, skia.PathOp.kIntersect_PathOp) or skia.Path()
        if wet > 0:
            c.drawPath(shape, skia.Paint(Color=skia.Color(*color, int(255 * alpha * wet)), AntiAlias=True,
                                         MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10)))
        c.drawPath(shape, skia.Paint(Color=col, AntiAlias=True))
    if dry > 0:
        c.drawPaint(skia.Paint(Shader=_grain(), Alphaf=dry, BlendMode=skia.BlendMode.kDstOut))
    c.restore()
    c.restore()


def write(c: skia.Canvas, text: str, x: float, y: float, size: float, p: float, vertical: bool = False,
          gap: float = 0.08, **kw):
    """书写一串字（横排以 (x, y) 为整体中心；竖排以 (x, y) 为首字中心向下）。p 按全部笔画长度分配。"""
    chars = [ch for ch in text if not ch.isspace()]
    durs = [char_duration(ch) or 1.0 for ch in chars]
    total = sum(durs)
    step = size * (1 + gap)
    acc = 0.0
    for i, (ch, d) in enumerate(zip(chars, durs)):
        q = (p * total - acc) / d
        acc += d
        if vertical:
            cx, cy = x, y + i * step
        else:
            cx, cy = x + (i - (len(chars) - 1) / 2) * step, y
        draw_char(c, ch, cx, cy, size, max(0.0, min(1.0, q)), **kw)


def progress(t: float, start: float, dur: float) -> float:
    """书写进度：起笔稍慢、收笔稍慢的缓动。"""
    x = max(0.0, min(1.0, (t - start) / max(dur, 1e-6)))
    return 0.5 - 0.5 * math.cos(math.pi * x)
