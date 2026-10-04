"""时间线：场景 / 台词 / 事件模型，旁白排时，镜头与转场，字幕，多进程逐帧渲染与音视频合成。"""

import bisect
import math
import subprocess
import tempfile
from dataclasses import dataclass, field
from multiprocessing import get_context
from pathlib import Path
from typing import Callable

import cv2
import numpy as np
import skia
import soundfile as sf

from . import audio, gfx
from .gfx import H, W

FPS = 30
BG_SCALE = 4
CAPTION_Y = 1400
CAPTION_MAX_W = 820


@dataclass
class Line:
    """一句旁白。text 中用【】标记字幕高亮的关键词（朗读时自动去掉）。"""
    text: str
    speed: float = 1.0
    pause: float = 0.22
    caption: bool = True


@dataclass
class Event:
    """与旁白同步的音画事件。锚点为第 line 句开始（-1 为场景开始），char 给出时锚定到该句第 char 个字。"""
    kind: str
    line: int = 0
    offset: float = 0.0
    char: int | None = None
    gain: float = 1.0
    to_line: int | None = None


@dataclass
class Scene:
    name: str
    lines: list[Line]
    draw: Callable
    palette: str
    transition: str = "cut"
    events: list[Event] = field(default_factory=list)
    lead: float = 0.12
    tail: float = 0.3
    exit: str | None = None
    bg: Callable | None = None
    t0: float = 0.0
    duration: float = 0.0
    starts: list[float] = field(default_factory=list)
    ends: list[float] = field(default_factory=list)


# 事件 → 音效 (名称, 增益) 与画面效果（震屏 (时长, 幅度)、推镜强度、闪白时长、故障时长）
EVENT_FX = {
    "boom": {"sfx": ("boom", 0.8), "shake": (0.35, 24), "punch": 0.07},
    "impact": {"sfx": ("impact", 0.9), "shake": (0.5, 30), "punch": 0.1, "flash": 0.35},
    "pop": {"sfx": ("pop", 0.5)},
    "pop2": {"sfx": ("pop2", 0.45)},
    "ding": {"sfx": ("ding", 0.35)},
    "whoosh": {"sfx": ("whoosh", 0.45)},
    "swoosh": {"sfx": ("swoosh", 0.5)},
    "crack": {"sfx": ("crack", 0.8), "shake": (0.25, 10)},
    "heart": {"sfx": ("heart", 0.9), "punch": 0.025},
    "glitch": {"sfx": ("glitch", 0.45), "glitch": 0.35},
    "shimmer": {"sfx": ("shimmer", 0.4)},
    "down": {"sfx": ("down", 0.55)},
    "buzz": {"sfx": ("buzz", 0.45)},
    "type": {"sfx": ("type", 0.35)},
    "riser": {"sfx": ("riser", 0.7)},
    "flash": {"flash": 0.25},
    "shake": {"shake": (0.3, 16)},
}


class Ctx:
    """传给场景绘制函数的上下文：画布、场景内时间与旁白时间锚点。"""

    def __init__(self, c: skia.Canvas, scene: Scene, t: float, frame: int, pal: dict):
        self.c, self.s, self.t, self.frame, self.pal = c, scene, t, frame, pal
        self.dur = scene.duration

    def cue(self, i: int) -> float:
        return self.s.starts[i]

    def end(self, i: int) -> float:
        return self.s.ends[i]

    def at(self, i: int, char: int) -> float:
        """第 i 句读到第 char 个字的估计时刻（按字数线性插值）。"""
        n = max(1, len(gfx.plain(self.s.lines[i].text)))
        return self.s.starts[i] + (self.s.ends[i] - self.s.starts[i]) * min(char, n) / n

    def p(self, i: int, off: float = 0.0, dur: float = 0.4) -> float:
        return gfx.prog(self.t, self.cue(i) + off, dur)


def _event_local(s: Scene, ev: Event) -> float:
    if ev.line < 0:
        return ev.offset
    if ev.char is not None:
        n = max(1, len(gfx.plain(s.lines[ev.line].text)))
        base = s.starts[ev.line] + (s.ends[ev.line] - s.starts[ev.line]) * min(ev.char, n) / n
    else:
        base = s.starts[ev.line]
    return base + ev.offset


class Video:
    """一条短视频：场景列表 + 调色板 + 配乐段落表。build 负责旁白排时与音频，render 输出 MP4。"""

    def __init__(self, scenes: list[Scene], palettes: dict, music: list[tuple[str, int, str]],
                 voice: str = "zf_001", base_speed: float = 1.05):
        self.scenes, self.palettes, self.music_plan = scenes, palettes, music
        self.voice, self.base_speed = voice, base_speed
        self.total = 0.0
        self.shakes, self.punches, self.flashes, self.glitches = [], [], [], []
        self.audio: np.ndarray | None = None

    # ------------------------------------------------------------ 排时与音频

    def build(self, with_audio: bool = True):
        """逐句合成旁白并排时，解析事件，合成配乐与音效并完成混音。"""
        narrator = audio.Narrator(self.voice)
        clips = []
        t0 = 0.0
        for s in self.scenes:
            s.starts, s.ends = [], []
            pos = s.lead
            for ln in s.lines:
                x = narrator.generate(gfx.plain(ln.text), self.base_speed * ln.speed)
                s.starts.append(pos)
                clips.append((t0 + pos, x))
                pos += len(x) / audio.SR
                s.ends.append(pos)
                pos += ln.pause
            s.duration = round((s.ends[-1] + max(s.lines[-1].pause, s.tail)) * FPS) / FPS
            s.t0 = t0
            t0 += s.duration
        self.total = t0
        del narrator

        n = int(self.total * audio.SR) + audio.SR
        voice = np.zeros(n)
        for start, x in clips:
            audio.place(voice, x, start)
        sfx_track = np.zeros((n, 2))
        for s in self.scenes:
            for ev in s.events:
                fx = EVENT_FX[ev.kind]
                gt = s.t0 + _event_local(s, ev)
                if "sfx" in fx:
                    name, gain = fx["sfx"]
                    if name == "riser":
                        if ev.to_line == -1:
                            end = s.t0 + s.duration
                        elif ev.to_line is not None:
                            end = s.t0 + s.starts[ev.to_line]
                        else:
                            end = gt + 2.0
                        clip = audio.sfx("riser", round(max(0.3, end - gt), 2))
                    else:
                        clip = audio.sfx(name)
                    audio.place(sfx_track, audio.pan(clip, 0), gt, gain * ev.gain)
                if "shake" in fx:
                    self.shakes.append((gt, *fx["shake"]))
                if "punch" in fx:
                    self.punches.append((gt, fx["punch"]))
                if "flash" in fx:
                    self.flashes.append((gt, fx["flash"]))
                if "glitch" in fx:
                    self.glitches.append((gt, fx["glitch"]))
        if not with_audio:
            return
        by_name = {s.name: s for s in self.scenes}
        marks = [(by_name[name].t0 + (by_name[name].starts[i] if i >= 0 else 0), style)
                 for name, i, style in self.music_plan]
        sections = [(t, marks[k + 1][0] if k + 1 < len(marks) else self.total, style)
                    for k, (t, style) in enumerate(marks)]
        music = audio.compose(sections, self.total + 1)
        self.audio = audio.master(audio.process_voice(voice), music, sfx_track)[: int(self.total * audio.SR)]

    # ------------------------------------------------------------ 画面

    def _palette_at(self, k: int, t: float) -> dict:
        """当前场景调色板；场景开头 0.6 秒内从上一场景的调色板渐变过来。"""
        cur = self.palettes[self.scenes[k].palette]
        if k == 0 or t >= 0.6:
            return cur
        prev = self.palettes[self.scenes[k - 1].palette]
        x = gfx.ease_in_out(t / 0.6)
        out = dict(cur)
        for key in ("bg", "blobs"):
            out[key] = [gfx.mix(a, b, x) for a, b in zip(prev[key], cur[key])]
        out["dust"] = gfx.mix(prev["dust"], cur["dust"], x)
        return out

    def _camera(self, gt: float) -> tuple[float, float, float]:
        """镜头震动位移与推镜缩放：返回 (dx, dy, scale)。"""
        dx = dy = 0.0
        for t, dur, amp in self.shakes:
            if t <= gt < t + dur:
                k = (1 - (gt - t) / dur) ** 2 * amp
                dx += k * (math.sin(gt * 91.3) + 0.6 * math.sin(gt * 57.1 + 1.7))
                dy += k * (math.cos(gt * 77.7) + 0.6 * math.sin(gt * 43.3 + 0.4))
        sc = 1.0
        for t, strength in self.punches:
            if gt >= t:
                sc += strength * math.exp(-(gt - t) * 10) * gfx.clamp01((gt - t) / 0.05)
        return dx, dy, sc

    def _overlay_amount(self, items, gt: float) -> float:
        return max([1 - (gt - t) / d for t, d in items if t <= gt < t + d] or [0.0])

    def _locate(self, frame: int):
        gt = frame / FPS
        k = max(0, bisect.bisect_right([s.t0 for s in self.scenes], gt) - 1)
        s = self.scenes[k]
        t = gt - s.t0
        return gt, s, t, self._palette_at(k, t)

    def draw_background(self, c: skia.Canvas, frame: int):
        """在 1/BG_SCALE 分辨率画布上绘制平滑背景层：渐变、流光、场景背景光效与暗角。"""
        gt, s, t, pal = self._locate(frame)
        c.save()
        c.scale(1 / BG_SCALE, 1 / BG_SCALE)
        gfx.gradient_bg(c, pal["bg"])
        gfx.aurora(c, gt, pal["blobs"], pal.get("aurora", 0.3))
        if s.bg is not None:
            s.bg(Ctx(c, s, t, frame, pal))
        gfx.vignette(c, pal.get("vignette", 0.45))
        c.restore()

    def draw_foreground(self, c: skia.Canvas, frame: int) -> float:
        """在全分辨率画布上绘制粒子、场景内容、字幕与转场叠加，返回故障效果强度（由调用方在像素层面施加）。"""
        gt, s, t, pal = self._locate(frame)
        gfx.dust(c, gt, pal["dust"], pal.get("dust_n", 40), seed=3, alpha=pal.get("dust_a", 0.6))

        dx, dy, sc = self._camera(gt)
        sc *= 1 + 0.035 * (t / max(s.duration, 0.1))
        alpha = 1.0
        tr = s.transition
        if tr == "zoom":
            sc *= 1 + 0.35 * (1 - gfx.ease_out(gfx.prog(t, 0, 0.45)))
            alpha = gfx.prog(t, 0, 0.25)
        elif tr == "whip":
            dx += W * 0.9 * (1 - gfx.ease_out(gfx.prog(t, 0, 0.35)))
        elif tr == "pop":
            sc *= 0.75 + 0.25 * gfx.ease_out_back(gfx.prog(t, 0, 0.4))

        c.save()
        c.translate(W / 2 + dx, H / 2 + dy)
        c.scale(sc, sc)
        c.translate(-W / 2, -H / 2)
        if alpha < 1:
            c.saveLayerAlpha(None, int(255 * alpha))
        s.draw(Ctx(c, s, t, frame, pal))
        if alpha < 1:
            c.restore()
        c.restore()

        self._draw_caption(c, s, t, pal)

        flash = self._overlay_amount(self.flashes, gt)
        if tr == "flash":
            flash = max(flash, 1 - gfx.prog(t, 0, 0.3))
        if flash > 0:
            c.drawPaint(skia.Paint(Color=gfx.col("#FFFFFF", flash)))
        black = 0.0
        if tr == "black":
            black = 1 - gfx.prog(t, 0, 0.5)
        if s.exit == "black":
            black = max(black, gfx.prog(t, s.duration - 0.6, 0.55))
        if black > 0:
            c.drawPaint(skia.Paint(Color=gfx.col("#000000", black)))

        amount = self._overlay_amount(self.glitches, gt)
        if tr == "glitch":
            amount = max(amount, 1 - gfx.prog(t, 0, 0.3))
        return amount

    def _draw_caption(self, c: skia.Canvas, s: Scene, t: float, pal: dict):
        """抖音风格字幕：逐字点亮（已读字全亮、未读字半透明），关键词高亮，入场轻弹。"""
        for i, ln in enumerate(s.lines):
            st, en = s.starts[i], s.ends[i]
            nxt = s.starts[i + 1] if i + 1 < len(s.lines) else s.duration
            stop = min(en + 0.35, nxt - 0.02)
            if not ln.caption or not (st - 0.05 <= t <= stop):
                continue
            rows = _wrap_marks(ln.text, 56, CAPTION_MAX_W)
            pop = gfx.ease_out_back(gfx.prog(t, st - 0.05, 0.2), 2.0)
            a = gfx.prog(t, st - 0.05, 0.1) * (1 - gfx.prog(t, stop - 0.12, 0.12))
            spoken = gfx.clamp01((t - st) / max(en - st, 0.1)) * sum(len(gfx.plain(r)) for r in rows)
            c.save()
            c.translate(W / 2, CAPTION_Y)
            c.scale(0.9 + 0.1 * pop, 0.9 + 0.1 * pop)
            y0 = -(len(rows) - 1) * 38
            for r, row in enumerate(rows):
                y = y0 + r * 76
                n_row = len(gfx.plain(row))
                w = sum(gfx.text_width(seg, 56, "black") for seg, _ in gfx.parse_marks(row))
                style = dict(stroke=("#000000", 10), shadow=(0, 5, 6, "#000000"))
                gfx.draw_rich(c, row, 0, y, 56, "black", "#FFFFFF", pal["hi"], a * 0.5, **style)
                lit = min(n_row, spoken)
                spoken -= n_row
                if lit > 0:
                    cut = gfx.text_width(gfx.plain(row)[: int(math.ceil(lit))], 56, "black")
                    c.save()
                    c.clipRect(skia.Rect.MakeLTRB(-w / 2 - 20, y - 60, -w / 2 + cut, y + 60))
                    gfx.draw_rich(c, row, 0, y, 56, "black", "#FFFFFF", pal["hi"], a, **style)
                    c.restore()
            c.restore()
            return

    # ------------------------------------------------------------ 输出

    def render(self, out_path: str, workers: int = 4):
        """多进程逐帧渲染并与混音后的音频合成为 MP4。"""
        if self.audio is None:
            raise RuntimeError("build() must run with audio before render()")
        n_frames = int(round(self.total * FPS))
        global _VIDEO
        _VIDEO = self
        with tempfile.TemporaryDirectory() as tmp:
            wav = str(Path(tmp) / "mix.wav")
            sf.write(wav, self.audio, audio.SR)
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                   "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                   "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            assert proc.stdin is not None
            try:
                with get_context("fork").Pool(workers) as pool:
                    for buf in pool.imap(_render_worker, range(n_frames), chunksize=6):
                        proc.stdin.write(buf)
            finally:
                proc.stdin.close()
            if proc.wait() != 0:
                raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")

    def still(self, t: float) -> np.ndarray:
        """渲染单帧（RGBA 数组），用于检查画面。"""
        global _VIDEO
        _VIDEO = self
        return np.frombuffer(_render_worker(int(round(t * FPS))), np.uint8).reshape(H, W, 4)


def _wrap_marks(text: str, size: float, max_w: float) -> list[str]:
    """字幕折行：超宽时在接近中点的标点后断为两行，并保持【】标记成对。"""
    p = gfx.plain(text).rstrip("，。；")
    if gfx.text_width(p, size, "black") <= max_w:
        return [_slice_marks(text, 0, len(p))]
    mid = len(p) / 2
    cands = [i + 1 for i, ch in enumerate(p[:-1]) if ch in "，、？！：；"]
    cut = min(cands, key=lambda i: abs(i - mid)) if cands else int(math.ceil(mid))
    if abs(cut - mid) > len(p) * 0.3:
        cut = int(math.ceil(mid))
    return [_slice_marks(text, 0, cut), _slice_marks(text, cut, len(p))]


def _slice_marks(text: str, a: int, b: int) -> str:
    """按纯文本下标 [a, b) 截取带【】标记的文本，截断处自动补全标记。"""
    out, hi, k = "", False, 0
    for ch in text:
        if ch in "【】":
            hi = ch == "【"
            if a <= k < b:
                out += ch
            continue
        if a <= k < b:
            if k == a and hi:
                out += "【"
            out += ch
            if k == b - 1 and hi:
                out += "】"
        k += 1
    return out.replace("【】", "")


_VIDEO: Video | None = None
_BUF: np.ndarray | None = None
_SURF: skia.Surface | None = None
_SMALL: np.ndarray | None = None
_SSURF: skia.Surface | None = None


def _render_worker(frame: int) -> bytes:
    """渲染一帧：低分辨率背景经 OpenCV 放大后直接写入帧缓冲，再在其上绘制前景。"""
    global _BUF, _SURF, _SMALL, _SSURF
    if _SURF is None:
        _BUF = np.zeros((H, W, 4), np.uint8)
        _SURF = skia.Surface(_BUF)
        _SMALL = np.zeros((H // BG_SCALE, W // BG_SCALE, 4), np.uint8)
        _SSURF = skia.Surface(_SMALL)
    _VIDEO.draw_background(_SSURF.getCanvas(), frame)
    cv2.resize(_SMALL, (W, H), dst=_BUF, interpolation=cv2.INTER_LINEAR)
    amount = _VIDEO.draw_foreground(_SURF.getCanvas(), frame)
    out = gfx.glitch(_BUF, amount, frame) if amount > 0 else _BUF
    return out.tobytes()
