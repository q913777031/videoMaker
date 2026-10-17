"""竖屏短视频《走出洞穴的人，为什么先想回头？》：梵高笔触风格，75 秒左右。

用法：python3 cave_short.py out/cave_allegory.mp4 [--still 秒数 ...]
同目录输出 cover.png（带标题）与 cover_clean.png（无字）。
画面：cave_draw 绘制底稿 → engine.paint 转为笔触（15fps 手绘节奏）→ 叠加字幕（30fps）。
声音：ZipVoice 旁白 + 程序化环境音效 + 大提琴长音 / 钢琴 / 弦乐配乐，-14 LUFS。
"""

import math
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from multiprocessing import get_context
from pathlib import Path

import cv2
import numpy as np
import skia
import soundfile as sf

import cave_draw as cd
from engine import audio, gfx
from engine import paint as pt
from engine.audio import SR, bandpass, highpass, hz, lowpass, place

W, H = pt.W, pt.H
FPS = 30
PAINT_EVERY = 2
VOICE, SPEED = "zv_yunxi", 0.75
CAPTION_Y = 1344
SERIF = gfx.FONT_DIR / "NotoSerifCJKsc-SemiBold.otf"


@dataclass
class Shot:
    draw: callable
    target: float
    lines: list[str]
    lead: float = 0.35
    label: str | None = None
    seed: int = 1
    t0: float = 0.0
    dur: float = 0.0
    starts: list[float] = field(default_factory=list)
    ends: list[float] = field(default_factory=list)


SHOTS = [
    Shot(cd.s1_phone, 7, ["一个信了很多年的看法，被人一句话戳破。", "你第一反应，是不是有点恼火？"], lead=0.1, seed=1),
    Shot(cd.s2_fire, 4, ["柏拉图在《理想国》里，讲过一个故事。"], seed=2),
    Shot(cd.s3_backs, 5, ["一群人从小被锁在洞里，只能面对石壁。"], seed=3),
    Shot(cd.s4_shadows, 9, ["身后有火，有人举着器物走过，墙上只有影子。", "他们便把影子当成真实。"], seed=4),
    Shot(cd.s5_turn, 4, ["后来，有个人被松开，被迫转过身。"], lead=0.25, seed=5),
    Shot(cd.s6_glare, 7, ["火光刺得眼睛生疼，他看不清那些器物，反而觉得，影子更真。"], seed=6),
    Shot(cd.s7_exit, 4, ["他被拉出洞口，阳光更刺眼。"], lead=0.25, seed=7),
    Shot(cd.s8_reflect, 8, ["只能先看影子，再看倒影，然后是实物，最后才能看向太阳。"], lead=0.6, seed=8),
    Shot(cd.s9_passage, 7, ["书里说，教育不是往里灌知识，而是让整个人转过身来。"], lead=0.5, seed=9),
    Shot(cd.s10_faces, 5, ["苏格拉底还说，这些囚徒，和我们一样。"], label="书中原意 · 转述", seed=10),
    Shot(cd.s11_dawn, 6, ["我会联想到刷到的信息、习惯的判断。", "这只是我的类比。"], label="创作者联想", seed=11),
    Shot(cd.s12_empty, 8.63, ["那份不舒服，也许是眼睛还在适应。", "下次被新看法刺到，你会转身，还是回头看墙？"], seed=12),
]
LINE_GAP = 0.5
REFERENCE = ["参考：柏拉图《理想国》卷七 514a–518d（斯特方码）", "本片为转述，非原文引用"]


# ---------------------------------------------------------------- 排时

def layout(shots: list[Shot]) -> tuple[float, list[tuple[float, np.ndarray]]]:
    """逐句合成旁白，按目标时长排布镜头；旁白放不下时镜头自动加长。返回 (总时长, [(开始秒, 音频)])。"""
    narrator = audio.Narrator(VOICE)
    clips, t0 = [], 0.0
    for s in shots:
        pos = s.lead
        s.starts, s.ends = [], []
        for ln in s.lines:
            x = narrator.generate(ln, SPEED)
            s.starts.append(pos)
            clips.append((t0 + pos, x))
            pos += len(x) / SR
            s.ends.append(pos)
            pos += LINE_GAP
        s.dur = round(max(s.target, s.ends[-1] + 0.7) * FPS) / FPS
        s.t0 = t0
        t0 += s.dur
    return t0, clips


def locate(shots: list[Shot], gt: float) -> tuple[int, float]:
    for k, s in enumerate(shots):
        if gt < s.t0 + s.dur or k == len(shots) - 1:
            return k, gt - s.t0
    raise ValueError(gt)


# ---------------------------------------------------------------- 字幕

def caption_chunks(text: str, start: float, end: float, max_len: int = 13) -> list[tuple[str, float, float]]:
    """把一句旁白切成单行字幕块（在逗号处断开，每块不超过 max_len 字），按字数比例分配时间。"""
    parts, buf = [], ""
    for ch in text:
        buf += ch
        if ch in "，、。？":
            parts.append(buf)
            buf = ""
    if buf:
        parts.append(buf)
    chunks: list[str] = []
    for p in parts:
        if chunks and len(chunks[-1]) + len(p) <= max_len:
            chunks[-1] += p
        else:
            chunks.append(p)
    total = sum(len(k) for k in chunks)
    out, t = [], start
    for k in chunks:
        d = (end - start) * len(k) / total
        out.append((k.rstrip("，、。"), t, t + d))
        t += d
    return out


_TF: skia.Typeface | None = None


def serif(size: float) -> skia.Font:
    global _TF
    if _TF is None:
        _TF = skia.Typeface.MakeFromFile(str(SERIF))
        if _TF is None:
            raise FileNotFoundError(SERIF)
    f = skia.Font(_TF, size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def draw_text(c: skia.Canvas, text: str, x: float, y: float, size: float, alpha: float = 1.0,
              align: str = "center", color=(255, 248, 232)):
    """衬线字幕：柔和投影 + 暖白字，不描边。"""
    if alpha <= 0:
        return
    f = serif(size)
    w = f.measureText(text)
    x0 = x - w / 2 if align == "center" else x
    sh = skia.Paint(AntiAlias=True, Color=skia.Color(10, 8, 20, int(230 * alpha)),
                    MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.14))
    c.drawString(text, x0 + 2, y + 3, f, sh)
    c.drawString(text, x0, y, f, sh)
    c.drawString(text, x0, y, f, skia.Paint(AntiAlias=True, Color=skia.Color(*color, int(255 * alpha))))


def overlay(c: skia.Canvas, shots: list[Shot], gt: float, total: float):
    k, t = locate(shots, gt)
    s = shots[k]
    for i, ln in enumerate(s.lines):
        chunks = caption_chunks(ln, s.starts[i], s.ends[i])
        for j, (text, a, b) in enumerate(chunks):
            first, last = j == 0, j == len(chunks) - 1
            on = a - 0.08
            off = b + 0.25 if last else chunks[j + 1][1] - 0.08
            if on <= t < off:
                alpha = gfx.clamp01((t - on) / 0.15) if first else 1.0
                if last:
                    alpha *= gfx.clamp01((off - t) / 0.15)
                draw_text(c, text, W / 2, CAPTION_Y, 58, alpha)
    if s.label:
        a = gfx.clamp01((t - 0.2) / 0.4) * gfx.clamp01((s.dur - t) / 0.3)
        f = serif(32)
        w = f.measureText(s.label)
        c.drawRoundRect(skia.Rect.MakeXYWH(56, 132, w + 40, 58), 29, 29,
                        skia.Paint(AntiAlias=True, Color=skia.Color(12, 12, 30, int(110 * a))))
        draw_text(c, s.label, 76, 172, 32, 0.8 * a, align="left")
    ref_t = total - 2.4
    if gt >= ref_t:
        a = gfx.clamp01((gt - ref_t) / 0.4)
        for j, line in enumerate(REFERENCE):
            draw_text(c, line, W / 2, 1650 + j * 52, 30, 0.85 * a)


# ---------------------------------------------------------------- 画面渲染

_SHOTS: list[Shot] = []
_TOTAL = 0.0
_STATE: dict = {}


def paint_frame(frame: int) -> np.ndarray:
    """绘制一帧笔触画面（不含字幕），返回 H×W×4 uint8。"""
    if not _STATE:
        _STATE["under"] = pt.Under()
    gt = frame / FPS
    k, t = locate(_SHOTS, gt)
    s = _SHOTS[k]
    u = _STATE["under"]
    c = u.begin()
    fld, fw, det = s.draw(c, t, s.dur)
    arr = u.to_array()
    buf = np.zeros((H, W, 4), np.uint8)
    surf = skia.Surface(buf)
    pt.paint(surf.getCanvas(), arr, fld, frame, s.seed, fw, det)
    pt.finish(buf)
    return buf


def _worker(pair: int) -> bytes:
    f0 = pair * PAINT_EVERY
    base = paint_frame(f0)
    out = []
    n = int(round(_TOTAL * FPS))
    for f in range(f0, min(f0 + PAINT_EVERY, n)):
        buf = base.copy()
        surf = skia.Surface(buf)
        overlay(surf.getCanvas(), _SHOTS, f / FPS, _TOTAL)
        out.append(buf.tobytes())
    return b"".join(out)


# ---------------------------------------------------------------- 音效（单声道，确定性）

def _t(d):
    return np.arange(int(d * SR)) / SR


def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def env_fade(x, fin=0.3, fout=0.3):
    x = x.copy()
    a, b = min(len(x), int(fin * SR)), min(len(x), int(fout * SR))
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def room_tone(d, seed=1):
    return env_fade(lowpass(_noise(int(d * SR), seed), 220) * 0.05)


def wind(d, seed=2, lo=180, hi=700, depth=0.6):
    t = _t(d)
    am = 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + seed) * np.sin(2 * np.pi * 0.05 * t))
    return env_fade(bandpass(_noise(len(t), seed), lo, hi) * am * 0.35, 0.8, 0.8)


def crackle(d, density=9.0, seed=3):
    """火：低频轰鸣 + 随机爆裂声。"""
    n = int(d * SR)
    rng = np.random.default_rng(seed)
    y = lowpass(_noise(n, seed), 260) * 0.25
    y *= 1 + 0.3 * np.sin(2 * np.pi * 0.7 * _t(d))
    for _ in range(int(d * density)):
        i = rng.integers(0, max(1, n - 3000))
        ln = rng.integers(200, 1400)
        click = highpass(_noise(ln, int(rng.integers(1e9))), 900) * np.exp(-np.arange(ln) / (ln / 5))
        y[i: i + ln] += click * rng.uniform(0.2, 0.9)
    return env_fade(y * 0.5)


def ignite(seed=4):
    d = 1.4
    t = _t(d)
    x = _noise(len(t), seed)
    y = audio._sweep_filter(x, np.geomspace(120, 1400, 40), 0.6) * np.minimum(1, t / 0.5) * np.exp(-t * 1.6)
    return y * 1.3


def drip(seed=5):
    t = _t(0.06)
    f = np.linspace(1700, 900, len(t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 70)
    return y * 0.5


def clink(seed=6, n=3, spread=0.12):
    """铁链轻碰：非谐波金属泛音，多次错开。"""
    rng = np.random.default_rng(seed)
    out = np.zeros(int((spread * n + 0.4) * SR))
    for k in range(n):
        t = _t(0.35)
        y = sum(a * np.sin(2 * np.pi * f * rng.uniform(0.97, 1.03) * t) * np.exp(-t * dcy)
                for f, a, dcy in ((2150, 0.5, 18), (3420, 0.35, 24), (5230, 0.25, 30), (7710, 0.12, 40)))
        place(out, y * rng.uniform(0.4, 1.0), k * spread * rng.uniform(0.6, 1.4))
    return out * 0.6


def chain_drop(seed=7):
    out = clink(seed, 7, 0.06) * 1.4
    thud = lowpass(_noise(int(0.3 * SR), seed), 180) * np.exp(-_t(0.3) * 14) * 1.2
    place(out, thud, 0.3)
    return out


def cloth(d=0.8, seed=8):
    t = _t(d)
    return bandpass(_noise(len(t), seed), 900, 4500) * np.sin(np.pi * t / d) ** 2 * 0.25


def tinnitus(d=3.0):
    t = _t(d)
    return np.sin(2 * np.pi * 7400 * t) * np.sin(np.pi * t / d) ** 2 * 0.035


def breath(d, rate=0.9, seed=9, level=0.18):
    t = _t(d)
    env = np.clip(np.sin(2 * np.pi * rate * t), 0, 1) ** 1.5
    return bandpass(_noise(len(t), seed), 350, 1800) * env * level


def gravel(d, seed=10):
    rng = np.random.default_rng(seed)
    n = int(d * SR)
    y = np.zeros(n)
    for _ in range(int(d * 40)):
        i = rng.integers(0, max(1, n - 2000))
        ln = rng.integers(300, 1500)
        y[i: i + ln] += lowpass(_noise(ln, int(rng.integers(1e9))), 3000) * np.exp(-np.arange(ln) / (ln / 4)) \
            * rng.uniform(0.1, 0.6)
    return y * 0.6


def footsteps(d, seed=11, rate=1.6):
    y = np.zeros(int(d * SR))
    for k in range(int(d * rate)):
        thump = lowpass(_noise(int(0.12 * SR), seed + k), 300) * np.exp(-_t(0.12) * 30)
        place(y, thump, k / rate + 0.1)
    return y * 0.35


def birds(d, seed=12, n=8):
    rng = np.random.default_rng(seed)
    y = np.zeros(int(d * SR))
    for _ in range(n):
        at = rng.uniform(0, d - 0.5)
        for j in range(rng.integers(2, 5)):
            ln = rng.uniform(0.05, 0.12)
            t = _t(ln)
            f0 = rng.uniform(2600, 4200)
            f = f0 + rng.uniform(-900, 900) * t / ln
            ch = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / ln) ** 2
            place(y, ch * rng.uniform(0.08, 0.2), at + j * rng.uniform(0.08, 0.16))
    return y


def stream(d, seed=13):
    t = _t(d)
    x = bandpass(_noise(len(t), seed), 350, 3200)
    am = 0.6 + 0.4 * lowpass(np.abs(_noise(len(t), seed + 1)), 12) * 3
    return env_fade(x * am * 0.16, 1.0, 1.0)


def traffic(d, seed=14):
    t = _t(d)
    return env_fade(lowpass(_noise(len(t), seed), 160) * (0.5 + 0.5 * np.sin(np.pi * t / d)) * 0.12, 1, 1)


def swipe(seed=15):
    t = _t(0.14)
    return bandpass(_noise(len(t), seed), 1800, 6000) * np.sin(np.pi * t / 0.14) * 0.12


def build_sfx(shots: list[Shot], total: float) -> np.ndarray:
    """按镜头布置环境声与动作音效（立体声）。"""
    n = int((total + 1) * SR)
    dry = np.zeros(n)
    cave = np.zeros(n)   # 需要洞穴混响的声音
    st = {i + 1: s.t0 for i, s in enumerate(shots)}
    du = {i + 1: s.dur for i, s in enumerate(shots)}

    def span(a, b):
        return st[a], st[b] + du[b] - st[a]

    # 1 深夜卧室
    place(dry, room_tone(du[1]), st[1])
    for k, at in enumerate((0.15, 0.55, 0.95)):
        place(dry, swipe(15 + k), st[1] + at, 0.9)
    # 2–6、10、12 洞穴：风与火
    a, d = span(2, 6)
    place(cave, wind(d, 2), a, 0.8)
    place(cave, ignite(), st[2] + 0.1, 0.9)
    place(cave, crackle(d - 0.4, 8, 3), a + 0.4, 0.9)
    for k, at in enumerate((st[3] + 1.2, st[3] + 3.6, st[4] + 2.5, st[4] + 6.8)):
        place(cave, drip(k), at, 0.5)
    place(cave, clink(21, 2), st[3] + 0.6, 0.35)
    place(cave, clink(22, 2), st[3] + 3.0, 0.3)
    place(cave, footsteps(du[4] - 1, 30), st[4] + 0.5, 0.5)
    place(cave, chain_drop(), st[5] + 0.15, 0.8)
    place(dry, cloth(0.9), st[5] + 0.5, 0.8)
    place(cave, crackle(du[6], 22, 41), st[6], 0.9)
    place(dry, tinnitus(3.2), st[6] + 0.4, 1.0)
    place(dry, breath(du[6] - 1.2, 1.4, 9, 0.16), st[6] + 0.6)
    # 7 出洞
    place(cave, gravel(2.6), st[7] + 0.1, 0.9)
    place(dry, wind(du[7] + 0.5, 3, 300, 2000, 0.3), st[7], 0.9)
    # 8 溪边
    place(dry, stream(du[8] + 0.5), st[8])
    place(dry, birds(du[8], 12, 7), st[8] + 0.5, 0.9)
    place(dry, breath(du[8] - 2, 0.45, 19, 0.08), st[8] + 1.0)
    # 9 通道
    place(cave, wind(du[9], 5, 120, 500, 0.4), st[9], 0.7)
    # 10 囚徒侧脸
    place(cave, crackle(du[10], 8, 51), st[10], 0.8)
    place(cave, wind(du[10], 6), st[10], 0.5)
    # 11 黎明卧室
    place(dry, room_tone(du[11], 61), st[11])
    place(dry, birds(du[11], 62, 4), st[11] + 0.3, 0.5)
    place(dry, traffic(du[11] - 0.5), st[11] + 0.3)
    # 12 空位
    place(cave, crackle(du[12] + 0.3, 8, 71), st[12], 0.85)
    place(cave, wind(du[12], 7), st[12], 0.5)
    place(cave, clink(72, 1), st[12] + 4.2, 0.4)
    tail = int((total - 0.6) * SR)
    out = audio.reverb(cave, 0.35, 2.6) + audio.pan(dry, 0)
    out[tail:] *= np.linspace(1, 0, len(out) - tail)[:, None]
    return out


# ---------------------------------------------------------------- 配乐

def cello(midi, d, vel=0.25, bright=520, seed=0):
    """大提琴长音：带颤音的锯齿波 + 弓噪，低通。"""
    t = _t(d + 1.5)
    vib = 0.004 * np.sin(2 * np.pi * 5.2 * t + seed) * np.minimum(1, t / 1.5)
    f = hz(midi) * (1 + vib)
    y = sum(((np.cumsum(f * k) / SR) % 1.0 * 2 - 1) / k for k in (1, 1.003))
    y = lowpass(y, bright, 2) + 0.04 * bandpass(_noise(len(t), seed), 1500, 4000)
    env = np.minimum(1, t / 1.2) * np.where(t < d, 1.0, np.exp(-(t - d) * 2.5))
    return y * env * vel


def score(shots: list[Shot], total: float) -> np.ndarray:
    n = int((total + 2) * SR)
    m = np.zeros(n)
    st = [s.t0 for s in shots]
    exit_cut = st[7] - 0.5   # 出洞白光：音乐抽空 0.5 秒
    # 0 → 出洞：D 小调长音铺底
    place(m, cello(38, exit_cut - 0.5, 0.3), 0.0)
    place(m, cello(45, exit_cut - st[2] - 0.5, 0.18, seed=1), st[2])
    place(m, cello(41, exit_cut - st[5], 0.14, 700, seed=2), st[5])
    seg_end = int(exit_cut * SR)
    m[seg_end:] = 0
    fade = int(0.4 * SR)
    m[seg_end - fade: seg_end] *= np.linspace(1, 0, fade)
    # 出洞后：钢琴单音 + 弦乐慢慢展开（D 大调）
    for k, (midi, at) in enumerate([(74, 0.0), (69, 2.2), (78, 4.4), (76, 6.6), (74, 9.0), (71, 11.6),
                                    (69, 14.2), (74, 17.0), (66, 20.0), (69, 23.0)]):
        place(m, audio._piano(hz(midi), 1.4, 0.28), st[7] + at)
    place(m, audio._pad((50, 57, 62, 66), st[10] - st[7] + 1, 900, 0.16), st[7] + 1.0)
    place(m, audio._pad((50, 57, 62), st[11] - st[9], 700, 0.12), st[9])
    # 结尾：单一长音，不收束
    place(m, cello(50, total - st[11] - 1.8, 0.2, 600, seed=3), st[11])
    end = int((total - 1.0) * SR)
    m[end:] = 0
    fade = int(1.6 * SR)
    m[end - fade: end] *= np.linspace(1, 0, fade)
    st_m = audio.reverb(m, 0.4, 3.0)
    return st_m / (np.max(np.abs(st_m)) + 1e-9) * 0.5


# ---------------------------------------------------------------- 封面

def cover_scene(c, t, d):
    """封面：通道中回头望向黑暗的人，半边火光、半边日光。"""
    mx, my = 560, 120
    cd.texture(c, cd.noise_img(131, 36, cd.NIGHT, cd.VIOLET, cd.PRUSSIAN))
    c.drawPaint(cd.paint_of(shader=cd.radial(mx, my, 1300, [gfx.mix(cd.CHROME, cd.LEAD, 0.5), cd.OCHRE,
                                                           ("#000000", 0.0)], [0, 0.3, 1]),
                            blend=skia.BlendMode.kScreen))
    c.drawPaint(cd.paint_of(shader=cd.radial(420, 2100, 900, [(cd.ORANGE, 0.75), (cd.VERMILION, 0.0)]),
                            blend=skia.BlendMode.kScreen))
    cd.glow(c, mx, my, 330, "#fffbe6", 1.0)
    x, y, s = 520, 1080, 640
    cd.torso_front(c, x, y + 0.34 * s, s, cloth=cd.LINEN, light=cd.ORANGE, light_a=0.8)
    cd.head_profile(c, x - 10, y, s, rot=0.18, light=("#f6c078", "#d08a60"), shadow="#3e4a72",
                    facing=-1, light_dir=1, brow=0.5, eye=0.8, beard=0.35)
    f = pt.blend_fields((pt.concentric_field(mx, my), 2.0 * cd.dist_weight(mx, my, 520) + 0.01),
                        (pt.swirl_field(0.0, 37), 1.0))
    return f, 0.6, cd.dist_weight(x, y, 330)


def render_cover(out_dir: Path):
    global _SHOTS
    u = pt.Under()
    c = u.begin()
    fld, fw, det = cover_scene(c, 0.0, 1.0)
    arr = u.to_array()
    buf = np.zeros((H, W, 4), np.uint8)
    pt.paint(skia.Surface(buf).getCanvas(), arr, fld, 0, 99, fw, det)
    pt.finish(buf)
    cv2.imwrite(str(out_dir / "cover_clean.png"), cv2.cvtColor(buf, cv2.COLOR_RGBA2BGR))
    cv = skia.Surface(buf).getCanvas()
    cv.drawRect(skia.Rect.MakeLTRB(0, 300, W, 760),
                skia.Paint(Shader=skia.GradientShader.MakeLinear(
                    [(0, 300), (0, 760)], [skia.Color(8, 10, 30, 0), skia.Color(8, 10, 30, 120),
                                           skia.Color(8, 10, 30, 0)])))
    draw_text(cv, "看清之前，", W / 2, 520, 112)
    draw_text(cv, "眼睛会先疼", W / 2, 670, 112)
    cv2.imwrite(str(out_dir / "cover.png"), cv2.cvtColor(buf, cv2.COLOR_RGBA2BGR))


# ---------------------------------------------------------------- 主流程

def main():
    global _SHOTS, _TOTAL
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "out/cave_allegory.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    _SHOTS = SHOTS
    _TOTAL, clips = layout(SHOTS)
    for i, s in enumerate(SHOTS, 1):
        print(f"镜头 {i:2d}  {s.t0:6.2f}s  时长 {s.dur:5.2f}s  旁白 {s.ends[-1] - s.starts[0]:5.2f}s")
    print(f"总时长 {_TOTAL:.2f}s")
    if "--still" in sys.argv:
        for v in sys.argv[sys.argv.index("--still") + 1:]:
            f = int(round(float(v) * FPS))
            buf = paint_frame(f)
            overlay(skia.Surface(buf).getCanvas(), SHOTS, f / FPS, _TOTAL)
            cv2.imwrite(str(out.parent / f"still_{float(v):05.1f}.png"), cv2.cvtColor(buf, cv2.COLOR_RGBA2BGR))
        return
    render_cover(out.parent)

    n = int((_TOTAL + 1) * SR)
    voice = np.zeros(n)
    for start, x in clips:
        place(voice, x, start)
    mix = audio.master(audio.process_voice(voice), score(SHOTS, _TOTAL), build_sfx(SHOTS, _TOTAL))
    mix = mix[: int(_TOTAL * SR)]

    n_frames = int(round(_TOTAL * FPS))
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "mix.wav")
        sf.write(wav, mix, SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "26",
               "-maxrate", "12M", "-bufsize", "24M",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
               str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        assert proc.stdin is not None
        pairs = math.ceil(n_frames / PAINT_EVERY)
        try:
            with get_context("fork").Pool(4) as pool:
                for k, data in enumerate(pool.imap(_worker, range(pairs), chunksize=2)):
                    proc.stdin.write(data)
                    if k % 75 == 0:
                        print(f"渲染 {k * PAINT_EVERY}/{n_frames}", flush=True)
        finally:
            proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")
    print("完成", out)


if __name__ == "__main__":
    main()
