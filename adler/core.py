"""阿德勒系列引擎：实测拍点时间轴、声明式镜头元素、逐帧合成、配乐与打击乐混音、成片与文档输出。

时间轴全部建立在 bgm.detect() 检测到的真实拍点上：
- 镜头长度以“小节”（4 个实测拍点）为单位，镜头边界即实测强拍；
- 元素入场、姿势变化、音效都写成“镜头内第 k 拍”，直接取第 k 个实测拍点的时间，不假设恒定 BPM；
- 带音效的动作必须落在整数拍上（即实测拍点），音效峰值与画面撞击帧同帧或相邻帧。
"""

import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from multiprocessing import get_context
from pathlib import Path
from typing import Callable

import numpy as np
import skia
import soundfile as sf
from scipy import signal

from engine import audio, bgm, gfx, perc
from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, ease_out_back, lerp

from . import fx
from . import kit as K

FPS = 30
W, H = K.W, K.H
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "adler_beats.json"

STAGE_CX, STAGE_CY = 540, 800
CAP_Y = 1395            # 主字幕块中心
CAP_SIZE = 64
CAP_MAXW = 840
EXIT = 0.28             # 镜头末尾元素退场时长
SECTION_BARS = (8, 20, 24, 34, 38, 40)   # 原曲段落边界（小节），镜头边界应覆盖这些位置



# 系列标识（页眉、片尾、封面、文件名）；其他系列复用本引擎时覆盖这些值
SERIES = {"name": "阿德勒心理学", "count": "10讲", "prefix": "阿德勒"}

# ---------------------------------------------------------------- 实测拍点

def _detect() -> dict:
    """bgm.detect() 的磁盘缓存（以 BGM 文件内容哈希为键），避免每次检查静帧都重新分析 20 秒。"""
    digest = hashlib.sha1(bgm.DEFAULT_BGM.read_bytes()).hexdigest()
    if CACHE.exists():
        data = json.loads(CACHE.read_text())
        if data.get("sha1") == digest:
            return data["det"]
    det = bgm.detect()
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps({"sha1": digest, "det": det}))
    return det


DET = _detect()
BEATS = DET["beats"]
SECTIONS = DET["sections"]
N_BEATS = len(BEATS)
_BEAT_T = np.array([b["t"] for b in BEATS])
LAST_BAR = (N_BEATS - 1) // 4          # 最后一个完整小节线（原曲最后一击）
MUSIC_END = BEATS[LAST_BAR * 4]["t"] + 0.3
END = MUSIC_END + 2.9                  # 原曲在 90 秒处硬截断，之后接约 3 秒混响尾音


def bt(i: float) -> float:
    """第 i 个实测拍点的时间；i 为小数时在相邻拍点间线性插值（只用于无音效的画面动作）。"""
    if i <= 0:
        return BEATS[0]["t"] if i == 0 else BEATS[0]["t"] + i * (BEATS[1]["t"] - BEATS[0]["t"])
    if i >= N_BEATS - 1:
        return BEATS[-1]["t"] + (i - N_BEATS + 1) * (BEATS[-1]["t"] - BEATS[-2]["t"])
    k = int(i)
    return lerp(BEATS[k]["t"], BEATS[k + 1]["t"], i - k)


def accent(b: dict) -> float:
    return max(b["strength"], 0.9 * b["low"], 0.9 * b["high"])


# ---------------------------------------------------------------- 元素（声明式）

@dataclass
class El:
    """镜头内的一个画面元素。

    at：入场拍（镜头内第几拍）；out：退场拍（None 表示持续到镜头结束）；enter：入场方式；
    sfx：入场时的打击乐（必须是整数拍）；moves：[(拍, {属性: 新值})] 关键帧，属性在该拍起 0.45 秒内缓动过去；
    其余关键字参数作为元素自身属性（位置 x/y、尺寸 s、旋转 rot、透明度 alpha 及各类型专有属性）。
    """
    kind: str
    at: float = 0
    out: float | None = None
    enter: str = "pop"
    dur: float = 0.42
    sfx: str | None = None
    gain: float = 1.0
    note: str = ""
    moves: list = field(default_factory=list)
    props: dict = field(default_factory=dict)
    idle: bool = True

    def hits(self):
        out = []
        if self.sfx:
            out.append((self.at, self.sfx, self.gain, self.note or f"{self.kind} 入场"))
        for kf in self.moves:
            b, d = kf[0], kf[1]
            if d.get("sfx"):
                out.append((b, d["sfx"], d.get("gain", 1.0), d.get("note", f"{self.kind} 动作")))
        out.extend(self.props.get("extra_hits", ()))
        return out


def _el(kind, at=0, out=None, enter="pop", dur=0.42, sfx=None, gain=1.0, note="", moves=(), idle=True, **props):
    return El(kind, at, out, enter, dur, sfx, gain, note, list(moves), props, idle)


def Fig(x, y, s=300, **kw):
    """人物元素：pose / color / mood / face / hair / look / walk（移动时自动迈步）等见 kit.figure。"""
    kw.setdefault("enter", "rise")
    return _el("fig", x=x, y=y, s=s, **kw)


def Icon(name, x, y, s=140, **kw):
    return _el("icon", name=name, x=x, y=y, s=s, **kw)


def Card(lines, x, y, size=44, **kw):
    """文字纸卡：lines 为字符串（| 换行）或列表。"""
    if isinstance(lines, str):
        lines = lines.split("|")
    return _el("card", lines=list(lines), x=x, y=y, size=size, **kw)


def Bubble(s, x, y, size=42, **kw):
    return _el("bubble", text=s, x=x, y=y, size=size, **kw)


def Arrow(p0, p1, **kw):
    kw.setdefault("enter", "draw")
    kw.setdefault("dur", 0.5)
    return _el("arrow", p0=p0, p1=p1, x=0, y=0, **kw)


def Label(s, x, y, size=34, **kw):
    kw.setdefault("enter", "pop")
    return _el("label", text=s, x=x, y=y, size=size, **kw)


def Big(s, x, y, size=150, **kw):
    """大字（概念名落版）：默认以 slam 方式在该拍砸下。"""
    kw.setdefault("enter", "slam")
    kw.setdefault("dur", 0.24)
    return _el("big", text=s, x=x, y=y, size=size, **kw)


def Txt(s, x, y, size=40, **kw):
    kw.setdefault("enter", "fade")
    return _el("txt", text=s, x=x, y=y, size=size, **kw)


def Custom(fn, **kw):
    """自定义绘制：fn(c, g, el_t, props)，el_t 为元素入场后经过的秒数，props 已含关键帧插值。"""
    kw.setdefault("enter", "fade")
    kw.setdefault("x", 0)
    kw.setdefault("y", 0)
    return _el("custom", fn=fn, **kw)


# ---------------------------------------------------------------- 光效与动效元素（见 adler/fx.py）

def Pops(words, x, y, size=78, at=0, step=1, sfx="pop", hi_sfx="ding", gain=0.9, layout="row", gap=26,
         maxw=900, font="serif_black", sparks=True, **kw):
    """文字逐个弹出：words 为“词 词|【高亮词】”（空格分词、| 换行、词内【】拆成独立高亮词）或列表，第 i 个词在 at + i*step 拍弹出（过冲回弹 + 星光）。

    整数拍上的词各配一个音效（普通词 sfx、高亮词 hi_sfx）；step 为小数时落在半拍上的词不配音效（音效只放在实测拍点）。
    高亮词为强调色纸片，弹出时额外有放射线与星光。
    """
    ws, breaks = fx.parse_words(words)
    beats, k = [], -1
    for w, _ in ws:
        if not (fx._punct(w) and beats):      # 纯标点跟上一个词同拍出现，不占拍、不配音效
            k += 1
        beats.append(at + k * step)
    hits = []
    for i, ((w, h), b) in enumerate(zip(ws, beats)):
        name = hi_sfx if h else sfx
        if i and beats[i - 1] == b:
            continue
        if name and abs(b - round(b)) < 1e-9:
            hits.append((b, name, gain, f"弹出：{w}"))
    kw.setdefault("enter", "none")
    return _el("pops", at=at, x=x, y=y, words=ws, beats=beats, size=size, layout=layout, gap=gap, maxw=maxw,
               font=font, sparks=sparks, breaks=breaks, extra_hits=hits, **kw)


def Glow(x, y, r=420, at=0, color=None, alpha=0.32, pulse=0.5, **kw):
    """随节拍呼吸的径向光晕（放在主体元素之前，作为背光）；color 默认为第二强调色。"""
    kw.setdefault("enter", "fade")
    kw.setdefault("dur", 0.5)
    return _el("glow", at=at, x=x, y=y, r=r, color=color, glow_alpha=alpha, pulse=pulse, **kw)


def Rays(x, y, r=640, at=0, color=None, alpha=0.22, n=14, spin=10.0, **kw):
    """旋转光束（放在主体元素之前）；随强拍轻微增亮。"""
    kw.setdefault("enter", "grow")
    kw.setdefault("dur", 0.5)
    return _el("rays", at=at, x=x, y=y, r=r, color=color, ray_alpha=alpha, n=n, spin=spin, **kw)


def Spark(x, y, at=0, n=18, reach=300, size=20, colors=None, sfx=None, **kw):
    """星光粒子爆散（拍点即爆开，0.9 秒内消失）。"""
    kw.setdefault("enter", "none")
    return _el("spark", at=at, x=x, y=y, n=n, reach=reach, size=size, colors=colors, sfx=sfx, **kw)


def Counter(v0, v1, x, y, size=180, at=0, land=4, fmt="{:.0f}", suffix="", sfx="ding", gain=0.9, color=None,
            sub=None, **kw):
    """滚动数字：第 at 拍开始滚动，第 land 拍（整数拍）落定在 v1，落定时放音效、放射线与星光。"""
    hits = [(land, sfx, gain, f"数字落定：{fmt.format(v1)}{suffix}")] if sfx else []
    kw.setdefault("enter", "fade")
    kw.setdefault("dur", 0.2)
    return _el("counter", at=at, x=x, y=y, v0=v0, v1=v1, size=size, land=land, fmt=fmt, suffix=suffix, color=color,
               sub=sub, extra_hits=hits, **kw)


# 入场方式：start 型从该拍开始运动；land 型在该拍落定（撞击帧 = 拍点）
START_MODES = {"pop", "rise", "fade", "grow", "draw", "none", "unfold", "slam"}
LAND_MODES = {"drop", "slide_l", "slide_r", "slide_u"}


# ---------------------------------------------------------------- 镜头与一期

@dataclass
class Shot:
    bars: int
    text: str
    tag: str
    els: list = field(default_factory=list)
    draw: Callable | None = None        # draw(g)：在元素之下绘制的自定义层
    over: Callable | None = None        # over(g)：在元素之上绘制的自定义层
    text_beat: float = 1
    big: bool = False                   # 字幕作为大标题卡显示在画面中部
    note: str = ""                      # 画面说明（写入文档与卡点表）
    cam: tuple = (1.0, 1.035)
    focus: tuple = (STAGE_CX, STAGE_CY)
    cut: bool = False                   # 与上一镜硬切（上一镜不做退场），用于人物位置连续的镜头
    hits: list = field(default_factory=list)   # 额外音效：(拍, 音色, 增益, 说明)
    research: bool = False
    punch: float = 0.006                # 强拍推镜脉冲幅度（0.006 为原有力度，钩子/高潮镜头可加到 0.02–0.035）
    flashes: list = field(default_factory=list)   # 闪白拍：[拍] 或 [(拍, 峰值)]，撞击帧最亮
    shake: list = field(default_factory=list)     # 镜头抖动拍：[拍] 或 [(拍, 幅度像素)]
    # 由 Episode.build 填充
    b0: int = 0
    t0: float = 0.0
    t1: float = 0.0

    def all_hits(self):
        out = list(self.hits)
        for el in self.els:
            out.extend(el.hits())
        return out


@dataclass
class Episode:
    no: int
    key: str
    concept: str                # 系列内概念名，如“目的论”
    title: str                  # 片名（视频内标题、文件名）
    accent: str
    shots: list
    refs: list                  # 参考资料（片尾卡与文档）
    publish_title: str = ""
    hashtags: str = ""
    cover_title: str = ""
    cover_sub: str = ""
    cover_shot: int = 4
    cover_t: float = 3.0
    land_shot: int = 2          # 4:3 横屏封面右侧取景的镜头（默认第 3 镜“情境演绎”）
    notes: list = field(default_factory=list)     # 事实核查与表述说明（写入文档）
    accent2: str = K.GOLD
    beat_punch: float = 0.0     # >0 时：每个音效拍与每个强拍都轻推镜头（幅度，如 0.02），保证画面每 2 秒左右整体有动作
    total: float = 0.0
    events: list = field(default_factory=list)

    def build(self):
        b = 0
        for i, s in enumerate(self.shots):
            s.b0 = b
            s.t0 = 0.0 if i == 0 else bt(b)
            b += 4 * s.bars
            s.t1 = bt(b) if b < N_BEATS else END
        if b != LAST_BAR * 4:
            raise ValueError(f"ep{self.no:02d}: shots cover {b // 4} bars, music has {LAST_BAR}")
        self.shots[-1].t1 = END
        for k, s in enumerate(self.shots):
            for el in s.els:
                if el.enter in LAND_MODES and bt(s.b0 + el.at) - el.dur < s.t0 - 1e-6:
                    raise ValueError(f"ep{self.no:02d} shot {k + 1}: '{el.enter}' at beat {el.at} starts before the shot")
        bounds = {s.b0 // 4 for s in self.shots}
        missing = [x for x in SECTION_BARS if x not in bounds]
        if missing:
            print(f"  提示：ep{self.no:02d} 没有在段落边界小节 {missing} 切镜", file=sys.stderr)
        self.total = END
        self.events = []
        for k, s in enumerate(self.shots):
            for beat, sfx, gain, note in s.all_hits():
                if sfx and abs(beat - round(beat)) > 1e-9:
                    raise ValueError(f"ep{self.no:02d} shot {k + 1}: sfx at fractional beat {beat}")
                gi = s.b0 + int(round(beat))
                if gi >= N_BEATS:
                    raise ValueError(f"ep{self.no:02d} shot {k + 1}: beat {beat} beyond music")
                self.events.append(dict(shot=k + 1, beat=gi, t=BEATS[gi]["t"], sfx=sfx, gain=gain, note=note,
                                        b=BEATS[gi]))
        self.events.sort(key=lambda e: e["t"])
        return self

    def shot_at(self, T: float) -> int:
        for i, s in enumerate(self.shots):
            if T < s.t1:
                return i
        return len(self.shots) - 1


class G:
    """画面函数的上下文：t 为镜头内时间（秒）。"""

    def __init__(self, c, ep: Episode, shot: Shot, t: float):
        self.c, self.ep, self.shot, self.t = c, ep, shot, t
        self.acc = ep.accent
        self.acc2 = ep.accent2
        self.dur = shot.t1 - shot.t0

    def b(self, k: float) -> float:
        """镜头内第 k 拍相对镜头起点的时间。"""
        return bt(self.shot.b0 + k) - self.shot.t0

    def since(self, k: float) -> float:
        return self.t - self.b(k)

    def p(self, k: float, dur: float = 0.45, ease=ease_out) -> float:
        return ease(clamp01(self.since(k) / dur)) if dur > 0 else float(self.since(k) >= 0)

    def span(self, k0: float, k1: float, ease=ease_in_out) -> float:
        """从第 k0 拍到第 k1 拍的进度。"""
        a, b = self.b(k0), self.b(k1)
        return ease(clamp01((self.t - a) / max(1e-6, b - a)))

    def pulse(self, decay: float = 6.0, downbeat: bool = False) -> float:
        """节拍脉冲：最近一个实测拍（downbeat=True 时只看强拍）处为该拍重音值，之后按 exp(-decay·dt) 衰减。"""
        T = self.shot.t0 + self.t
        i = max(0, min(N_BEATS - 1, int(np.searchsorted(_BEAT_T, T, side="right")) - 1))
        while downbeat and i > 0 and BEATS[i]["bar_pos"] != 0:
            i -= 1
        b = BEATS[i]
        if T < b["t"] or (downbeat and b["bar_pos"] != 0):
            return 0.0
        return accent(b) * math.exp(-(T - b["t"]) * decay)

    @property
    def exit(self) -> float:
        """镜头末尾退场进度 0→1。"""
        nxt = self.ep.shots.index(self.shot) + 1
        if nxt < len(self.ep.shots) and self.ep.shots[nxt].cut:
            return 0.0
        return ease_in(clamp01((self.t - (self.dur - EXIT)) / EXIT)) if self.shot is not self.ep.shots[-1] else 0.0


# ---------------------------------------------------------------- 元素求值与绘制

def _resolve(el: El, g: G) -> dict:
    d = dict(el.props)
    prev_pose = d.get("pose", "stand")
    for kf in sorted(el.moves, key=lambda m: m[0]):
        b, new = kf[0], kf[1]
        dur = new.get("dur", 0.45)
        k = clamp01(g.since(b) / dur) if dur > 0 else float(g.since(b) >= 0)
        if k <= 0:
            break
        e = ease_in_out(k) if new.get("ease", "io") == "io" else ease_out(k)
        for key, v in new.items():
            if key in ("sfx", "gain", "note", "dur", "ease"):
                continue
            if key == "pose":
                d["pose"] = K.blend(prev_pose, v, e) if k < 1 else v
                prev_pose = v
            elif isinstance(v, (int, float)) and isinstance(d.get(key), (int, float)):
                d[key] = lerp(d[key], v, e)
            elif isinstance(v, tuple) and isinstance(d.get(key), tuple) and len(v) == len(d[key]):
                d[key] = tuple(lerp(a, b_, e) for a, b_ in zip(d[key], v))
            else:
                d[key] = v if k >= 0.5 else d.get(key, v)
        if el.kind == "fig" and "x" in new and d.get("walk", True) and 0 < k < 1:
            d["_walking"] = math.sin(math.pi * k)
    return d


def _enter(el: El, g: G) -> tuple[float, float, float, float, float] | None:
    """返回 (alpha, scale, dx, dy, progress)；未入场返回 None。"""
    t_at = g.b(el.at)
    if el.enter in LAND_MODES:
        k = clamp01((g.t - (t_at - el.dur)) / el.dur)
        if g.t < t_at - el.dur:
            return None
        if el.enter == "drop":
            return clamp01(k * 4), 1, 0, -420 * (1 - ease_in(k)) + (-14 * math.sin(min(1, (g.t - t_at) / 0.25) * math.pi) if g.t > t_at else 0), k
        sx = {"slide_l": -900, "slide_r": 900, "slide_u": 0}[el.enter]
        sy = 700 if el.enter == "slide_u" else 0
        e = ease_out(k)
        return clamp01(k * 2.5), 1, sx * (1 - e), sy * (1 - e), k
    if g.t < t_at:
        return None
    k = clamp01((g.t - t_at) / el.dur) if el.dur > 0 else 1.0
    if el.enter == "pop":
        return clamp01(k * 3), 0.2 + 0.8 * ease_out_back(k, 2.0), 0, 0, k
    if el.enter == "slam":
        # 拍点即撞击：第一帧就以 1.45 倍出现，0.2 秒内砸到原尺寸，随后轻微回弹
        dt = g.t - t_at
        sc = 1 + 0.45 * (1 - ease_out(clamp01(dt / 0.2))) - 0.05 * math.sin(clamp01((dt - 0.2) / 0.25) * math.pi)
        return clamp01(dt / 0.06), sc, 0, 0, k
    if el.enter == "rise":
        return clamp01(k * 2), 1, 0, 70 * (1 - ease_out(k)), k
    if el.enter == "grow":
        return clamp01(k * 4), ease_out_back(k, 1.4), 0, 0, k
    if el.enter == "unfold":
        return clamp01(k * 3), 1, 0, 0, k
    if el.enter in ("fade", "draw"):
        return ease_out(k), 1, 0, 0, k
    return 1, 1, 0, 0, 1


def draw_el(c, el: El, g: G):
    st = _enter(el, g)
    if st is None:
        return
    alpha, sc, dx, dy, k = st
    if el.out is not None:
        alpha *= 1 - ease_in(clamp01(g.since(el.out) / 0.3))
    if alpha <= 0.002:
        return
    d = _resolve(el, g)
    alpha *= d.get("alpha", 1.0)
    x, y = d["x"] + dx, d["y"] + dy
    s = d.get("s", 1.0)
    rot = d.get("rot", 0.0)
    el_t = g.since(el.at)
    if el.idle and el.kind in ("card", "icon", "bubble", "label"):
        y += 4 * math.sin(g.t * 1.6 + d["x"] * 0.01)
    kind = el.kind
    if kind == "fig":
        p = d.get("pose", "stand")
        bob = 0.006 * math.sin(g.t * 2.6 + d["x"] * 0.02) if el.idle else 0.0
        w = d.get("_walking", 0.0)
        if w > 0:
            p = K.walk(abs(d["x"] - el.props["x"]) / (0.28 * s), w * d.get("stride", 1.0), p if isinstance(p, str) else "stand")
            bob += 0.02 * abs(math.sin(abs(d["x"] - el.props["x"]) / (0.28 * s) * math.pi)) * w
        with K.at(c, x, y, rot, sc):
            K.figure(c, 0, 0, s, p, d.get("color", K.HERO), d.get("head_color", K.SKIN), alpha, d.get("face", 1),
                     d.get("mood", "calm"), d.get("hair"), d.get("hair_color"), bob, d.get("lift", 1.0),
                     d.get("look", 0.0), d.get("blink", False), d.get("scarf"), d.get("prop"))
    elif kind == "icon":
        pv = d.get("p", 1.0)
        if callable(pv):
            pv = pv(g, el_t)
        if el.enter == "grow":
            with K.at(c, x, y + s * 0.5, rot, 1, sc):
                K.icon(c, d["name"], 0, -s * 0.5, s, d.get("color", K.INK), alpha, d.get("lift", 0.8), 0, 1, pv,
                       d.get("accent", g.acc))
        else:
            K.icon(c, d["name"], x, y, s, d.get("color", K.INK), alpha, d.get("lift", 0.8), rot, sc, pv,
                   d.get("accent", g.acc))
    elif kind == "card":
        K.text_card(c, x, y, d["lines"], d.get("size", 44), d.get("w"), d.get("fill", K.PAPER), d.get("color", K.INK),
                    d.get("hi", g.acc), alpha, rot, sc, d.get("accent"), d.get("font", "serif"), d.get("lift", 1.0))
    elif kind == "bubble":
        K.bubble(c, x, y, d["text"], d.get("size", 42), d.get("tail", (0, 1)), alpha, sc, d.get("fill", K.PAPER),
                 d.get("color", K.INK), d.get("hi", g.acc), d.get("think", False), d.get("font", "serif"))
    elif kind == "arrow":
        p = k if el.enter == "draw" else 1.0
        K.arrow(c, d["p0"], d["p1"], d.get("color", K.INK), d.get("width", 10), alpha, p, d.get("bend", 0.0),
                d.get("head", 30), d.get("dash"))
    elif kind == "label":
        with K.at(c, x, y, rot, sc):
            K.pill(c, 0, 0, d["text"], d.get("size", 34), d.get("fill", g.acc), d.get("color", K.PAPER), alpha,
                   d.get("font", "sans_medium"))
    elif kind == "big":
        size = d.get("size", 150)
        dt = g.since(el.at)
        if d.get("rays"):
            fx.rays(c, x, y, size * 4.2, g.acc2, g.t, 16, (0.2 + 0.12 * g.pulse(5, True)) * alpha * clamp01(dt / 0.3))
        if d.get("glow"):
            fx.glow(c, x, y, size * 2.6, g.acc2, (0.3 + 0.15 * g.pulse(5)) * alpha)

        def _big():
            with K.at(c, x, y, rot, sc):
                K.text(c, d["text"], 0, 0, size, d.get("font", "serif_black"), d.get("color", g.acc), alpha,
                       shadow=(6, 10, 10, K.SHADOW) if d.get("shadow", True) else None)
                sub = d.get("sub")
                if sub:
                    K.text(c, sub, 0, size * 0.78, d.get("sub_size", 40), "sans_medium", K.INK2, alpha)

        if d.get("shine"):
            w = K.text_w(d["text"], size, d.get("font", "serif_black")) * 1.5 + 80
            fx.shine(c, skia.Rect.MakeXYWH(x - w / 2, y - size * 1.2, w, size * 2.4), clamp01((dt - 0.25) / 0.6), _big)
        else:
            _big()
        if d.get("spark") and 0 <= dt <= 1:
            fx.sparks(c, x, y, dt, [g.acc2, g.acc, K.PAPER], 20, 9, size * 2.4, size * 0.16)
        if d.get("burst", True) and 0 <= g.since(el.at) <= 0.4:
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(0, 330, W, 1270))     # 放射线不进入页眉与字幕区
            K.burst(c, x, y, g.since(el.at), g.acc2, d.get("size", 150) * 0.9, d.get("size", 150) * 2.2, 12, 9)
            c.restore()
    elif kind == "txt":
        with K.at(c, x, y, rot, sc):
            gfx.draw_rich(c, d["text"], 0, 0, d.get("size", 40), d.get("font", "serif"), d.get("color", K.INK),
                          d.get("hi", g.acc), alpha, d.get("align", "center"))
    elif kind == "custom":
        with K.at(c, x, y, rot, sc):
            with K.fade(c, alpha):
                d["fn"](c, g, el_t, d)
    elif kind == "glow":
        fx.glow(c, x, y, d["r"] * sc, d.get("color") or g.acc2, d["glow_alpha"] * alpha * (1 + d["pulse"] * g.pulse(5)))
    elif kind == "rays":
        fx.rays(c, x, y, d["r"] * sc, d.get("color") or g.acc2, g.t, d["n"], d["ray_alpha"] * alpha * (1 + 0.6 * g.pulse(5, True)),
                d["spin"])
    elif kind == "spark":
        fx.sparks(c, x, y, el_t, d.get("colors") or [g.acc2, g.acc, K.PAPER], d["n"], int(x + y) % 97, d["reach"], d["size"])
    elif kind == "pops":
        _draw_pops(c, d, g, x, y, alpha)
    elif kind == "counter":
        _draw_counter(c, el, d, g, x, y, alpha)


def _draw_pops(c, d, g: G, x, y, alpha):
    ws, size, font = d["words"], d["size"], d["font"]
    pos = fx.layout_words(ws, size, font, d["layout"], d["gap"], d["maxw"], d.get("breaks", ()))
    bounce = 1 + 0.035 * g.pulse(7)
    for (w, hi), (dx, dy), b in zip(ws, pos, d["beats"]):
        dt = g.since(b)
        st = fx.word_pop(dt)
        if st is None:
            continue
        a, s_, r_ = st
        px, py = x + dx, y + dy
        if hi and d["sparks"]:
            fx.glow(c, px, py, size * 1.9, g.acc2, 0.35 * alpha * clamp01(dt / 0.15) * (0.7 + 0.5 * g.pulse(5)))
        with K.at(c, px, py, r_ if hi else -r_ * 0.5, s_ * bounce):
            fx.draw_word(c, w, 0, 0, size, font, d.get("color", K.INK), d.get("hi_fill", g.acc), K.PAPER, a * alpha, hi)
        if d["sparks"]:
            if hi:
                c.save()
                c.clipRect(skia.Rect.MakeLTRB(0, 330, W, 1270))
                K.burst(c, px, py, dt, g.acc2, size * 0.9, size * 1.9, 10, 7)
                c.restore()
                fx.sparks(c, px, py, dt, [g.acc2, g.acc, K.PAPER], 12, int(px) % 31, size * 2.2, size * 0.2)
            else:
                fx.sparks(c, px, py - size * 0.4, dt, [g.acc2, K.PAPER], 6, int(px) % 29, size * 1.1, size * 0.13, dur=0.5)


def _draw_counter(c, el: El, d, g: G, x, y, alpha):
    t_land = g.b(d["land"]) - g.b(el.at)
    k = clamp01(g.since(el.at) / max(1e-6, t_land))
    v = fx.counter_value(d["v0"], d["v1"], k)
    dt = g.since(d["land"])
    sc = 1 + (0.22 * (1 - ease_out(clamp01(dt / 0.25))) if dt >= 0 else 0.03 * math.sin(g.t * 40))
    col = d.get("color") or g.acc
    size = d["size"]
    if dt >= 0:
        fx.glow(c, x, y, size * 2.2, g.acc2, (0.32 + 0.12 * g.pulse(5)) * alpha)
    with K.at(c, x, y, 0, sc):
        K.text(c, d["fmt"].format(v) + d["suffix"], 0, 0, size, "black", col, alpha, shadow=(5, 9, 10, K.SHADOW))
        if d.get("sub"):
            K.text(c, d["sub"], 0, size * 0.85, size * 0.24, "sans_medium", K.INK2, alpha)
    if 0 <= dt <= 1:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, 330, W, 1270))
        K.burst(c, x, y, dt, g.acc2, size * 0.9, size * 2.0, 12, 9)
        c.restore()
        fx.sparks(c, x, y, dt, [g.acc2, g.acc, K.PAPER], 18, 7, size * 2.2, size * 0.13)


# ---------------------------------------------------------------- 背景、字幕与界面

_BG_IMG: dict = {}


def bg_image(accent: str) -> skia.Image:
    """暖白纸底：低频纹理 + 细颗粒 + 极淡的强调色光斑与暗角（每期按强调色缓存一张）。"""
    if accent in _BG_IMG:
        return _BG_IMG[accent]
    import cv2

    rng = np.random.default_rng(11)
    base = np.array(gfx.rgb(K.BG), np.float32)
    img = np.ones((H, W, 3), np.float32) * base
    low = cv2.resize(rng.normal(0, 1, (30, 17)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img += low[..., None] * np.array([2.4, 2.2, 2.6], np.float32)
    fib = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.2) * 5
    img += fib[..., None]
    img += rng.normal(0, 1.4, (H, W)).astype(np.float32)[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    acc = np.array(gfx.rgb(accent), np.float32)
    blob = np.exp(-(((xx - W * 0.85) / (W * 0.6)) ** 2 + ((yy - H * 0.18) / (H * 0.22)) ** 2))
    img = img * (1 - 0.07 * blob[..., None]) + acc * 0.07 * blob[..., None]
    r = np.hypot((xx - W / 2) / (W * 0.8), (yy - H * 0.46) / (H * 0.62))
    vig = np.clip(r - 0.55, 0, 1) ** 1.6
    img -= vig[..., None] * np.array([40, 44, 52], np.float32)
    rgba = np.dstack([np.clip(img, 0, 255).astype(np.uint8), np.full((H, W), 255, np.uint8)])
    _BG_IMG[accent] = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    return _BG_IMG[accent]


TAG_COLORS = {
    "情境演绎": K.INK2, "机制示意": K.INK2, "小练习": K.GREEN, "常见误解": K.RED, "研究证据": "#3A5BA0",
    "参考资料": K.INK2,
}


def tag_color(tag: str, ep: Episode) -> str:
    for k, v in TAG_COLORS.items():
        if tag.startswith(k):
            return v
    return ep.accent


def _caption_lines(shot: Shot) -> list[str]:
    return K.wrap_lines(shot.text, CAP_SIZE if not shot.big else 92, CAP_MAXW, "serif")


def draw_caption(c, ep: Episode, shot: Shot, g: G):
    if not shot.text:
        return
    t_in = g.b(shot.text_beat)
    if g.t < t_in:
        return
    big = shot.big
    size = 92 if big else CAP_SIZE
    lines = _caption_lines(shot)
    n = len(lines)
    gap = size * 1.5
    y0 = (STAGE_CY if big else CAP_Y) - (n - 1) * gap / 2
    out = 1 - g.exit
    for i, ln in enumerate(lines):
        k = clamp01((g.t - t_in - i * 0.1) / 0.4)
        if k <= 0:
            continue
        a = clamp01(k * 2) * out
        dy = (1 - ease_out(k)) * 34 + g.exit * 18
        y = y0 + i * gap + dy
        segs = gfx.parse_marks(ln)
        total = sum(K.text_w(s, size, "serif") for s, _ in segs)
        x = W / 2 - total / 2
        for s, hi in segs:
            w = K.text_w(s, size, "serif")
            if hi:
                m = ease_out(clamp01((g.t - t_in - i * 0.1 - 0.25) / 0.35))
                if m > 0:
                    c.drawRoundRect(skia.Rect.MakeXYWH(x - 6, y + size * 0.08, (w + 12) * m, size * 0.36), 8, 8,
                                    K.paint(K.tint(g.acc, 0.55), a * 0.9))
            x += K.text(c, s, x, y, size, "serif", g.acc if hi and big else K.INK, a, "left")


def draw_header(c, ep: Episode, shot: Shot, T: float, g: G):
    a = clamp01((T - 0.3) / 0.6)
    if a <= 0:
        return
    K.text(c, f"{SERIES['name']} · {SERIES['count']}", 72, 196, 30, "sans_medium", K.INK2, a, "left")
    K.rr(c, 72 + 48, 246, 96, 50, 25, ep.accent, a)
    K.text(c, f"{ep.no:02d}", 72 + 48, 246, 32, "black", K.PAPER, a)
    K.text(c, ep.concept, 72 + 112, 246, 34, "serif_black", K.INK, a, "left")
    if shot.tag:
        k = ease_out(clamp01(g.t / 0.4))
        w = K.text_w(shot.tag, 28, "sans_medium") + 44
        with K.fade(c, a * k):
            K.rr(c, W - 72 - w / 2, 246, w, 50, 25, K.PAPER)
            K.rr_stroke(c, W - 72 - w / 2, 246, w, 50, 25, tag_color(shot.tag, ep), 3)
            K.text(c, shot.tag, W - 72 - w / 2, 246, 28, "sans_medium", tag_color(shot.tag, ep))


def draw_progress(c, ep: Episode, T: float):
    """顶部细进度条：每个实测强拍处的节点微微跳动。"""
    y = 300
    x0, x1 = 72, W - 72
    p = clamp01(T / MUSIC_END)
    K.seg(c, x0, y, x1, y, K.LINE, 4)
    K.seg(c, x0, y, lerp(x0, x1, p), y, ep.accent, 4)
    last = max((b for b in BEATS if b["t"] <= T), key=lambda b: b["t"], default=None)
    if last is not None:
        pulse = math.exp(-(T - last["t"]) * 7) * (1.0 if last["bar_pos"] == 0 else 0.45)
        K.dot(c, lerp(x0, x1, p), y, 6 + 6 * pulse, ep.accent)


# ---------------------------------------------------------------- 帧合成

def _draw_shot(c, ep: Episode, k: int, t: float):
    s = ep.shots[k]
    g = G(c, ep, s, t)
    dur = s.t1 - s.t0
    z = lerp(s.cam[0], s.cam[1], ease_in_out(clamp01(t / dur)))
    # 每个实测强拍处的轻微推镜脉冲
    gi = s.b0 + int(max(0, math.floor(_beat_index_local(g))))
    if 0 <= gi < N_BEATS:
        b = BEATS[gi]
        if b["bar_pos"] == 0:
            z *= 1 + s.punch * accent(b) * math.exp(-(t - (b["t"] - s.t0)) * 6)
    if ep.beat_punch > 0:
        T = s.t0 + t
        last = None
        for beat, sfx, _, _ in s.all_hits():
            if sfx and bt(s.b0 + beat) <= T and (last is None or bt(s.b0 + beat) > last):
                last = bt(s.b0 + beat)
        if 0 <= gi < N_BEATS and BEATS[gi]["bar_pos"] == 0 and (last is None or BEATS[gi]["t"] > last):
            last = BEATS[gi]["t"]
        if last is not None:
            z *= 1 + ep.beat_punch * math.exp(-(T - last) * 7)
    c.save()
    for it in s.shake:
        kb, amp = it if isinstance(it, tuple) else (it, 14.0)
        dx, dy = fx.shake_offset(g.since(kb), amp, seed=kb)
        c.translate(dx, dy)
    c.translate(*s.focus)
    c.scale(z, z)
    c.translate(-s.focus[0], -s.focus[1])
    ex = g.exit
    if ex > 0:
        c.translate(0, ex * 30)
        c.saveLayerAlpha(None, int(255 * (1 - ex)))
    if s.draw:
        s.draw(g)
    for el in s.els:
        draw_el(c, el, g)
    if s.over:
        s.over(g)
    if ex > 0:
        c.restore()
    c.restore()
    return g


def _beat_index_local(g: G) -> float:
    T = g.shot.t0 + g.t
    lo = g.shot.b0
    while lo + 1 < N_BEATS and BEATS[lo + 1]["t"] <= T:
        lo += 1
    return lo - g.shot.b0


def draw_frame(c, ep: Episode, T: float, caption=True, ui=True):
    c.drawImage(bg_image(ep.accent), 0, 0)
    k = ep.shot_at(T)
    s = ep.shots[k]
    g = _draw_shot(c, ep, k, T - s.t0)
    for it in s.flashes:
        kb, pk = it if isinstance(it, tuple) else (it, 0.55)
        fx.flash(c, fx.flash_alpha(g.since(kb), pk), K.PAPER)
    if caption:
        draw_caption(c, ep, s, g)
    if ui:
        draw_header(c, ep, s, T, g)
        draw_progress(c, ep, T)
    fin = 1 - clamp01(T / 0.4)
    fout = clamp01((T - (END - 1.2)) / 1.1)
    if fin > 0 or fout > 0:
        c.drawPaint(K.paint(K.BG, max(fin, fout)))


# ---------------------------------------------------------------- 片尾（参考资料）

def end_shot(ep_refs: list[str], next_title: str | None, bars: int = 2) -> Shot:
    """片尾：系列标识 + 参考资料 + 下一讲预告；最后一击落在原曲最后一个强拍。"""

    def draw(g: G):
        c = g.c
        a = g.p(0, 0.5)
        K.text(c, "参考资料", W / 2, 470, 48, "serif_black", K.INK, a)
        K.seg(c, W / 2 - 60, 526, W / 2 + 60, 526, g.acc, 6, a)
        y = 610
        for i, r in enumerate(ep_refs):
            ai = g.p(0.5 + i * 0.5, 0.5)
            parts = [r]
            if K.text_w(r, 34, "sans_medium") > 880 and "（" in r:     # 中译名整体换到下一行
                head, tail = r.split("（", 1)
                parts = [head, "（" + tail]
            for j, ln in enumerate(ln for part in parts for ln in K.wrap_lines(part, 34, 880, "sans_medium")):
                K.text(c, ln, W / 2, y, 34, "sans_medium", K.INK2, ai)
                y += 52
            y += 30
        ap = g.p(4, 0.5)
        if next_title:
            K.text(c, "下一讲", W / 2, 1120, 34, "sans_medium", K.INK3, ap)
            parts = [next_title]
            if K.text_w(next_title, 56, "serif_black") > 900 and "：" in next_title:   # 在冒号处分成“期号概念 / 片名”两行
                head, tail = next_title.split("：", 1)
                parts = [head, tail]
            for j, ln in enumerate(parts):
                size = min(56.0, 56 * 900 / max(1.0, K.text_w(ln, 56, "serif_black")))
                K.text(c, ln, W / 2, 1200 + j * 78, size, "serif_black", g.acc, ap)
        else:
            K.text(c, f"{SERIES['name']} · {SERIES['count']} 完", W / 2, 1180, 56, "serif_black", g.acc, ap)
            K.text(c, "感谢观看", W / 2, 1260, 36, "sans_medium", K.INK2, ap)

    return Shot(bars, "", "参考资料", [], draw=draw, note="参考资料与下一讲预告", hits=[(0, "cymbal", 0.5, "片尾落版"),
                                                                             (4 * bars, "kick", 0.55, "原曲最后一击")])


# ---------------------------------------------------------------- 渲染

_EP: Episode | None = None


def _render(frame: int) -> bytes:
    info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    draw_frame(surf.getCanvas(), _EP, frame / FPS)
    return surf.makeImageSnapshot().tobytes()


def still(ep: Episode, T: float, path: str, caption=True, ui=True):
    info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    draw_frame(surf.getCanvas(), ep, T, caption, ui)
    surf.makeImageSnapshot().save(path, skia.kPNG)


def render(ep: Episode, wav: str, out: str, workers: int = 4):
    """多进程逐帧渲染并与混音合成 MP4（H.264 / yuv420p / AAC）；任一环节失败抛出 RuntimeError。"""
    global _EP
    _EP = ep
    n = int(round(ep.total * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "21",
           "-maxrate", "6M", "-bufsize", "12M", "-tune", "animation", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        with get_context("fork").Pool(workers) as pool:
            for i, buf in enumerate(pool.imap(_render, range(n), chunksize=8)):
                proc.stdin.write(buf)
                if i % 600 == 0:
                    print(f"  ep{ep.no:02d}: {i}/{n}", file=sys.stderr, flush=True)
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")


# ---------------------------------------------------------------- 音频

SFX_LEVEL = {"kick": 0.5, "kick_light": 0.5, "rim": 0.34, "wood_high": 0.3, "wood_low": 0.3, "shaker": 0.24,
             "frame": 0.55, "tom": 0.48, "bongo_high": 0.34, "bongo_low": 0.36, "clap": 0.34, "cymbal": 0.3,
             "pop": 0.3, "ding": 0.26}
DUCK_DEPTH = {"kick": 0.22, "kick_light": 0.18, "rim": 0.12, "frame": 0.22, "tom": 0.18, "clap": 0.12, "cymbal": 0.08}


def resolve_sfx(name: str, b: dict) -> str:
    """原曲在该拍已有重底鼓（低频起音 ≥0.7）时，低音鼓改用高通版本，避免叠加过重低频。"""
    if name == "kick" and b["low"] >= 0.7:
        return "kick_light"
    return name


def music_track() -> np.ndarray:
    """配乐：原曲播放到最后一击后 0.3 秒，再接其混响尾音约 2.6 秒自然衰减到静音（原曲在 90 秒处硬截断）。"""
    sr = audio.SR
    x = bgm.load()
    n = int(END * sr)
    cut = int(MUSIC_END * sr)
    out = np.zeros((n, 2))
    body = x[:cut].copy()
    fo = int(0.25 * sr)
    body[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    out[:cut] = body
    seed = x[cut - int(1.2 * sr): cut]
    lead = int(0.12 * sr)
    length = n - cut + lead
    tail = np.zeros((length, 2))
    for ch, irs in enumerate((11, 23)):
        wet = signal.fftconvolve(seed[:, ch], audio.reverb_ir(2.4, irs))[len(seed) - lead:][:length]
        tail[: len(wet), ch] = wet
    ref = np.sqrt(np.mean(body[-int(0.6 * sr): -fo] ** 2))
    tail *= ref / (np.sqrt(np.mean(tail[: int(0.4 * sr)] ** 2)) + 1e-9) * 0.5
    r = int(0.08 * sr)
    tail[:r] *= np.linspace(0, 1, r)[:, None]
    out[cut - lead:] += tail
    fade_n = int(0.6 * sr)
    out[-fade_n:] *= np.linspace(1, 0, fade_n)[:, None]
    return out


_MUSIC = None


def build_audio(ep: Episode) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    """返回 (混音, 配乐分轨, 音效分轨, 音效清单)；两条分轨乘同一个总增益，相加即限幅前混音。"""
    import pyloudnorm

    global _MUSIC
    if _MUSIC is None:
        _MUSIC = music_track()
    sr = audio.SR
    n = int(END * sr)
    music = _MUSIC
    sfx = np.zeros((n, 2))
    duck = np.zeros(n)
    rel = np.exp(-np.arange(int(0.45 * sr)) / sr / 0.16)
    att = int(0.012 * sr)
    out = []
    for e in ep.events:
        name = resolve_sfx(e["sfx"], e["b"])
        clip = perc.sound(name) * SFX_LEVEL[name] * e["gain"]
        lead = perc.attack_ms(name) / 1000
        i = int(round((e["t"] - lead) * sr))
        seg = sfx[i: i + len(clip)]
        seg += audio.pan(clip[: len(seg)], 0)
        d = DUCK_DEPTH.get(name, 0.05) * e["gain"]
        a0 = max(0, i - att)
        duck[a0:i] = np.maximum(duck[a0:i], np.linspace(0, d, i - a0))
        tail = duck[i: i + len(rel)]
        duck[i: i + len(rel)] = np.maximum(tail, d * rel[: len(tail)])
        frame = int(round(e["t"] * FPS))
        peak_t = i / sr + lead
        out.append(dict(e, name=name, frame=frame, frame_err=round(peak_t * FPS - frame, 2)))
    duck = signal.lfilter([0.02], [1, -0.98], duck)
    music_d = music * (1 - np.clip(duck, 0, 0.3))[:, None]
    meter = pyloudnorm.Meter(sr)
    mix = music_d + sfx
    gain = 10 ** ((-14.0 - meter.integrated_loudness(mix)) / 20)
    music_d, sfx = music_d * gain, sfx * gain
    mix = music_d + sfx
    a = np.abs(mix)
    knee, ceil = 0.6, 0.84
    over = a > knee
    mix[over] = np.sign(mix[over]) * (knee + (ceil - knee) * np.tanh((a[over] - knee) / (ceil - knee)))
    return mix.astype(np.float32), music_d.astype(np.float32), sfx.astype(np.float32), out


# ---------------------------------------------------------------- 检查与文档

_HAN = re.compile(r"[一-鿿]")


def han(s: str) -> int:
    return len(_HAN.findall(s))


def read_check(ep: Episode) -> list[str]:
    """字幕阅读窗检查：稳定显示时长 ≥ max(2, 汉字/4.5)，含数字或英文另加 1 秒，研究卡至少 4.5 秒。"""
    warns = []
    for i, s in enumerate(ep.shots):
        if not s.text:
            continue
        g = G(None, ep, s, 0)
        stable = (s.t1 - s.t0 - EXIT) - (g.b(s.text_beat) + 0.4 + 0.1 * (len(_caption_lines(s)) - 1))
        n = han(gfx.plain(s.text))
        need = max(2.0, n / 4.5)
        if re.search(r"[0-9A-Za-z]", s.text):
            need += 1.0
        if s.research:
            need = max(need, 4.5)
        lines = _caption_lines(s)
        if len(lines) > 2 and not s.big:
            warns.append(f"镜头{i + 1}：字幕 {len(lines)} 行（上限 2 行）")
        if stable < need:
            warns.append(f"镜头{i + 1}：稳定显示 {stable:.2f}s < 预算 {need:.2f}s（{n} 字）")
    return warns


def tc(t: float) -> str:
    f = int(round(t * FPS))
    s = f // FPS
    return f"{s // 60:02d}:{s % 60:02d}:{f % FPS:02d}"


def write_docs(ep: Episode, out_dir: Path, events: list[dict]):
    """卡点表（CSV）与“文案与出处”（Markdown）。"""
    with open(out_dir / "cue_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["时间", "帧", "实测拍序号", "小节内位置", "重音值", "镜头", "动作", "音效", "音画偏差(帧)"])
        for e in events:
            w.writerow([f"{e['t']:.3f}", e["frame"], e["beat"], e["b"]["bar_pos"], f"{accent(e['b']):.2f}",
                        e["shot"], e["note"], perc.TIMBRES.get(e["name"], e["name"]), e["frame_err"]])
    lines = [f"# {ep.no:02d}｜{ep.title}", "",
             f"- 概念：{ep.concept}", f"- 发布标题：{ep.publish_title or ep.title}", f"- 话题：{ep.hashtags}",
             f"- 封面：{ep.cover_title} / {ep.cover_sub}",
             f"- 时长：{ep.total:.1f} 秒（1080×1920，30fps，配乐 music/bgm.m4a，镜头边界与音效全部落在实测拍点上）", "",
             "## 逐屏文案", "", "| # | 时间（分:秒:帧） | 角标 | 屏幕文字 | 画面 |", "|---|------|------|----------|------|"]
    for i, s in enumerate(ep.shots):
        pops = " ".join(w for el in s.els if el.kind == "pops" for w, _ in el.props["words"])
        txt = gfx.plain(s.text).replace("|", "／") if s.text else f"（弹字）{pops}" if pops else "（参考资料）"
        lines.append(f"| {i + 1} | {tc(s.t0)}–{tc(s.t1)} | {s.tag} | {txt} | {s.note} |")
    lines += ["", "## 参考资料", ""] + [f"- {r}" for r in ep.refs]
    if ep.notes:
        lines += ["", "## 事实核查与表述说明", ""] + [f"- {n}" for n in ep.notes]
    (out_dir / "文案与出处.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def cover(ep: Episode, path: str):
    """封面：取指定镜头的画面（不含字幕与界面），叠加大标题。"""
    info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    c = surf.getCanvas()
    s = ep.shots[ep.cover_shot]
    c.drawImage(bg_image(ep.accent), 0, 0)
    c.save()
    c.translate(0, 120)
    _draw_shot(c, ep, ep.cover_shot, min(ep.cover_t, s.t1 - s.t0 - EXIT - 0.05))
    c.restore()
    K.rr(c, 72 + 70, 230, 140, 70, 35, ep.accent)
    K.text(c, f"{ep.no:02d}", 72 + 70, 230, 46, "black", K.PAPER)
    K.text(c, SERIES["name"], 72 + 160, 230, 40, "sans_medium", K.INK2, 1, "left")
    lines = ep.cover_title.split("|")
    widest = max(K.text_w(gfx.plain(ln), 104, "serif_black") for ln in lines)
    size = min(104.0, 104 * 920 / widest)       # 长标题整体缩字号，保持手动断行
    for i, ln in enumerate(lines):
        y = 1450 + (i - (len(lines) - 1) / 2) * size * 1.35
        gfx.draw_rich(c, ln, W / 2, y, size, "serif_black", K.INK, ep.accent, 1.0)
    if ep.cover_sub:
        K.text(c, ep.cover_sub, W / 2, 1450 + len(lines) * 70 + 70, 44, "sans_medium", K.INK2)
    surf.makeImageSnapshot().save(path, skia.kPNG)


def cover_landscape(ep: Episode, path: str, w: int = 1440, h: int = 1080):
    """4:3 横屏封面：左侧系列期号、片名大字（【】高亮）与概念，右侧为情境镜头的舞台画面（不含字幕与界面），背后光束。"""
    shot = ep.shots[ep.land_shot]
    frame = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    fc = frame.getCanvas()
    fc.drawImage(bg_image(ep.accent), 0, 0)
    _draw_shot(fc, ep, ep.land_shot, max(0.5, shot.t1 - shot.t0 - EXIT - 0.15))
    stage = frame.makeImageSnapshot()

    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(w, h, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    c = surf.getCanvas()
    c.drawImageRect(bg_image(ep.accent), skia.Rect.MakeXYWH(0, (H - W * h / w) / 2, W, W * h / w), skia.Rect.MakeWH(w, h),
                    skia.SamplingOptions(skia.FilterMode.kLinear))
    from . import fx
    pw, ph = 620, 620 * 840 / W
    px, py = w - 60 - pw / 2, h / 2 + 10
    fx.rays(c, px, py, 760, ep.accent2, 0, 16, 0.22)
    fx.glow(c, px, py, 520, ep.accent2, 0.35)
    with K.at(c, px, py, 2.5):
        K.card(c, 0, 0, pw + 24, ph + 24, K.PAPER, 1, r=28)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), 20, 20), doAntiAlias=True)
        c.drawImageRect(stage, skia.Rect.MakeXYWH(0, 350, W, 840), skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph),
                        skia.SamplingOptions(skia.FilterMode.kLinear))
        c.restore()
    x0 = 80
    K.rr(c, x0 + 60, 150, 120, 64, 32, ep.accent)
    K.text(c, f"{ep.no:02d}", x0 + 60, 150, 42, "black", K.PAPER)
    K.text(c, f"{SERIES['name']} · {SERIES['count']}", x0 + 140, 150, 40, "sans_medium", K.INK2, 1, "left")
    lines = ep.cover_title.split("|")
    maxw = w - pw - 60 - 2 * x0 + 20
    widest = max(K.text_w(gfx.plain(ln), 120, "serif_black") for ln in lines)
    size = min(120.0, 120 * maxw / widest)
    y = h / 2 - (len(lines) - 1) * size * 0.68 - 20
    for i, ln in enumerate(lines):
        gfx.draw_rich(c, ln, x0, y + i * size * 1.36, size, "serif_black", K.INK, ep.accent, 1.0, "left",
                      shadow=(4, 7, 8, K.SHADOW))
    yb = y + (len(lines) - 1) * size * 1.36 + size * 0.9 + 40
    label = ep.concept
    lw = K.text_w(label, 44, "serif_black") + 60
    K.rr(c, x0 + lw / 2, yb, lw, 76, 38, ep.accent)
    K.text(c, label, x0 + lw / 2, yb, 44, "serif_black", K.PAPER)
    K.text(c, "Vibe知识大赏", x0, h - 90, 36, "sans_medium", K.INK2, 1, "left")
    surf.makeImageSnapshot().save(path, skia.kPNG)


def produce(ep: Episode, out_dir: Path, video: bool = True, workers: int = 4) -> Path | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for w_ in read_check(ep):
        print(f"  阅读窗警告 ep{ep.no:02d}：{w_}", file=sys.stderr)
    mix, music, sfx, events = build_audio(ep)
    sf.write(out_dir / "bgm_track.wav", music, audio.SR, subtype="PCM_16")
    sf.write(out_dir / "sfx_track.wav", sfx, audio.SR, subtype="PCM_16")
    write_docs(ep, out_dir, events)
    cover(ep, str(out_dir / "cover.png"))
    worst = max((abs(e["frame_err"]) for e in events), default=0.0)
    print(f"  ep{ep.no:02d}: {len(events)} 个音效，最大音画偏差 {worst:.2f} 帧，峰值 {np.max(np.abs(mix)):.3f}")
    if not video:
        return None
    out = out_dir / f"{SERIES['prefix']}{ep.no:02d}_{ep.concept}.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "mix.wav")
        sf.write(wav, mix, audio.SR)
        render(ep, wav, str(out), workers)
    return out
