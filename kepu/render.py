"""时间轴构建（叙事基准或按原曲校准）、逐帧合成（场景 + 字幕 + 角标）、多进程渲染与封面。"""

import subprocess
from dataclasses import dataclass, field, replace
from multiprocessing import get_context

import numpy as np
import skia

from . import draw as d
from .config import BG, FPS, GOLD, WHITE, Layout, Shot
from .topic import Topic

TRANS = 0.3            # 场景层交叉匹配转场时长（不影响字幕阅读窗口）
TEXT_IN = 0.4
TEXT_OUT = 0.4


@dataclass
class Timeline:
    shots: list[Shot]
    total: float
    cues: dict            # 镜头号 → {键: 镜头内秒}
    events: list[dict]    # 音效事件（视频绝对时间）
    calibrated: bool
    boundaries: list = field(default_factory=list)   # 每条边界的 (Beat, 原因)，无原曲时为 None
    topic: Topic | None = None


POS_NAME = {1: "小节重拍（第1拍）", 3: "次强拍（第3拍）", 2: "普通拍（第2拍）", 4: "普通拍（第4拍）"}


def _fit_boundaries(sh, an) -> tuple[list[float], list]:
    """镜头边界贴拍：±1.0s 内有段落起点则贴段落起点，否则依次尝试 ±0.45s 内的小节重拍、±0.45s 内的第 3 拍、±0.3s 内任意拍。

    每次移动后核对两侧镜头的阅读窗口（时长 - 0.8s ≥ 预算需求且时长 ≥ 5s），不满足就退回下一级候选。
    """
    from . import music
    need = {s.no: s.need for s in sh}
    bounds = [0.0] + [s.start for s in sh[1:]] + [an.total]
    info = [None] * len(bounds)
    for i in range(1, len(sh)):
        b = sh[i].start
        tries = []
        sec = [x for x in an.sections if abs(x - b) <= 1.0]
        if sec:
            bt = music.nearest_beat(an, min(sec, key=lambda x: abs(x - b)), 0, an.total, {1})
            tries.append((bt, "段落起点重拍"))
        tries.append((music.nearest_beat(an, b, b - 0.45, b + 0.45, {1}), "小节重拍"))
        tries.append((music.nearest_beat(an, b, b - 0.45, b + 0.45, {3}), "次强拍"))
        tries.append((music.nearest_beat(an, b, b - 0.3, b + 0.3), "最近拍"))
        for bt, why in tries:
            if bt is None:
                continue
            nb = round(bt.t * FPS) / FPS
            left, right = nb - bounds[i - 1], bounds[i + 1] - nb
            if left >= max(5.0, need[sh[i - 1].no] + 0.8) and right >= max(5.0, need[sh[i].no] + 0.8):
                bounds[i], info[i] = nb, (bt, why)
                break
    return bounds, info


def build_timeline(topic: Topic, analysis=None) -> Timeline:
    """无原曲时使用叙事基准；有原曲时边界贴拍、关键撞击贴小节重拍、移动类动作贴普通拍。"""
    from . import music
    an = analysis
    sh = topic.shots()
    total = (sh[-1].start + sh[-1].dur) if an is None else an.total
    bounds, binfo = ([s.start for s in sh] + [total], [None] * (len(sh) + 1)) if an is None \
        else _fit_boundaries(sh, an)
    for i, s in enumerate(sh):
        s.start, s.dur = bounds[i], bounds[i + 1] - bounds[i]
    cues, events = {}, []
    for s in sh:
        cues[s.no] = {}
        prev, prev_base = 0.0, 0.0
        for cu in s.cues:
            base = max(cu.t, prev + (cu.t - prev_base)) if prev_base else cu.t   # 前一事件被推后时保持原间隔
            prev_base = cu.t
            row = {"shot": s.no, "key": cu.key, "sound": cu.sound, "action": cu.action, "gain": cu.gain,
                   "base": s.start + base, "strength": None, "conf": "未确认", "method": "", "mix": "",
                   "beat": None, "music_t": None}
            exact = None
            if an is not None:
                g0 = s.start + base
                lo = s.start + max(0.8 if cu.sound and cu.snap else 0.45, prev + 0.35)   # 避开入场转场
                hi = s.start + s.dur - 0.6
                if cu.window is not None:
                    lo, hi = s.start + cu.window[0], s.start + cu.window[1]
                if cu.sound and cu.snap:
                    tries = [(music.nearest_beat(an, g0, max(lo, g0 - 1.1), min(hi, g0 + 1.1), {1}), "高"),
                             (music.nearest_beat(an, g0, max(lo, g0 - 1.7), min(hi, g0 + 1.7), {1}), "高"),
                             (music.nearest_beat(an, g0, max(lo, g0 - 0.6), min(hi, g0 + 0.6), {3}), "中"),
                             (music.nearest_beat(an, g0, max(lo, g0 - 0.3), min(hi, g0 + 0.3)), "中")]
                else:
                    tries = [(music.nearest_beat(an, g0, max(lo, g0 - 0.3), min(hi, g0 + 0.3)), "中")]
                bt, conf = next(((b, c) for b, c in tries if b is not None), (None, "无合适拍点"))
                if bt is not None:
                    exact = bt.t
                    row.update(strength=round(bt.strength, 3), beat=bt, music_t=bt.t,
                               conf=conf if bt.strength >= 0.5 else "低",
                               method=f"节拍网格 {an.grid_info['bpm']} BPM，{POS_NAME[bt.pos]}；自动分析，未人工试听")
                else:
                    row.update(method="窗口内无合适拍点，保持叙事位置（柔和动作）")
                    row["action"] += "（柔和动作，未贴拍）"
                if cu.sound == "kick" and exact is not None:
                    lowr = music.low_energy_at(an, exact)
                    if lowr > 0.5:
                        row["gain"], row["mix"] = 0.0, f"原曲此拍低频占比 {lowr:.2f}，取消低鼓叠加"
                    elif lowr > 0.3:
                        row["gain"], row["mix"] = cu.gain * 0.5, f"原曲此拍低频占比 {lowr:.2f}，低鼓减半"
            else:
                row["method"] = "未检测：原曲缺失，按叙事基准放置"
            local = round(((exact - s.start) if exact is not None else base) * FPS) / FPS
            cues[s.no][cu.key] = local
            prev = local
            row["t"] = s.start + local
            row["sfx_t"] = exact if exact is not None else row["t"]
            if cu.sound and row["gain"] <= 0:
                row["sound"] = ""
            events.append(row)
    if topic.post_cues is not None:
        topic.post_cues(cues, sh)
    tl = Timeline(sh, total, cues, events, an is not None, binfo, topic)
    return tl


# ---------------------------------------------------------------- 逐帧

class Frame:
    def __init__(self, tl: Timeline, L: Layout):
        self.tl, self.L, self.topic = tl, L, tl.topic
        s = L.stage_scale
        v = ((0 - L.stage_ox) / s, (0 - L.stage_oy) / s, (L.w - L.stage_ox) / s, (L.h - L.stage_oy) / s)
        z = L.zoom
        self.view = tuple((x - c0 * (1 - z)) / z for x, c0 in zip(v, (500, 560, 500, 560)))
        self.starts = [x.start for x in tl.shots]

    def locate(self, gt):
        k = max(0, min(len(self.starts) - 1, int(np.searchsorted(self.starts, gt + 1e-9, "right")) - 1))
        sh = self.tl.shots[k]
        return k, sh, gt - sh.start

    def _scene(self, c, sh, t):
        c.save()
        c.translate(self.L.stage_ox, self.L.stage_oy)
        c.scale(self.L.stage_scale, self.L.stage_scale)
        z = self.L.zoom
        c.translate(500 * (1 - z), 560 * (1 - z))
        c.scale(z, z)
        self.topic.scenes[sh.no](c, t, sh.dur, self.tl.cues[sh.no], self.view)
        c.restore()

    def draw(self, c: skia.Canvas, frame: int):
        gt = frame / FPS
        k, sh, t = self.locate(gt)
        c.clear(d.col(BG))
        if k > 0 and t < TRANS:
            prev = self.tl.shots[k - 1]
            self._scene(c, prev, prev.dur)
            c.saveLayerAlpha(None, int(255 * d.ease_io(t / TRANS)))
            self._scene(c, sh, t)
            c.restore()
        else:
            self._scene(c, sh, t)
        self._scrim(c)
        self._tag(c, sh, t, k)
        if sh.credit:
            self._credit(c, sh, t, k)
        else:
            self._caption(c, sh, t, k)
        end = d.prog(gt, self.tl.total - TEXT_OUT, TEXT_OUT)
        if end > 0:
            c.drawPaint(skia.Paint(Color=d.col("#000000", end)))

    def _scrim(self, c):
        L = self.L
        if L.name == "vertical":
            g = skia.GradientShader.MakeLinear([(0, 0), (0, 660)], [d.col(BG, 0.88), d.col(BG, 0.7), d.col(BG, 0)],
                                               [0, 0.6, 1])
            c.drawRect(skia.Rect.MakeLTRB(0, 0, L.w, 660), skia.Paint(Shader=g))
        else:
            g = skia.GradientShader.MakeLinear([(0, 0), (1000, 0)], [d.col(BG, 0.9), d.col(BG, 0.75), d.col(BG, 0)],
                                               [0, 0.62, 1])
            c.drawRect(skia.Rect.MakeLTRB(0, 0, 1000, L.h), skia.Paint(Shader=g))

    def _text_alpha(self, sh, t, k):
        if k == 0:
            a_in, rise = 1.0, 0.0
        else:
            x = d.prog(t, 0, TEXT_IN)
            a_in, rise = d.ease_out(x), 16 * (1 - d.ease_out(x))
        a_out = 1 - d.prog(t, sh.dur - TEXT_OUT, TEXT_OUT) if not sh.credit else 1.0
        return a_in * a_out, rise

    def _tag(self, c, sh, t, k):
        L = self.L
        a, _ = self._text_alpha(sh, t, k)
        f = d.font("sans", L.tag_size)
        w = f.measureText(sh.tag) + L.tag_size * 1.1
        h = L.tag_size * 1.6
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(L.tag_x, L.tag_y - h / 2, w, h), h / 2, h / 2)
        c.drawRRect(r, d.fill("#000000", 0.45 * a))
        c.drawRRect(r, d.stroke(GOLD, 1.6, 0.85 * a))
        d.draw_text(c, sh.tag, L.tag_x + w / 2, L.tag_y, L.tag_size, GOLD, a, name="sans", shadow=False)

    def _caption(self, c, sh, t, k):
        L = self.L
        a, rise = self._text_alpha(sh, t, k)
        if a <= 0:
            return
        lines = sh.lines
        y0 = L.text_y
        if L.name == "horizontal":
            y0 = L.text_y - (len(lines) - 1) * L.text_line_gap / 2
            c.drawLine(L.text_x, y0 - L.text_size * 1.15, L.text_x + 70, y0 - L.text_size * 1.15,
                       d.stroke(GOLD, 3, a))
        else:
            c.drawLine(L.text_x - 35, y0 - L.text_size * 1.1, L.text_x + 35, y0 - L.text_size * 1.1,
                       d.stroke(GOLD, 3, a))
        for i, ln in enumerate(lines):
            d.draw_text(c, ln, L.text_x, y0 + i * L.text_line_gap + rise, L.text_size, WHITE, a,
                        align=L.text_align)

    def _credit(self, c, sh, t, k):
        L = self.L
        a, rise = self._text_alpha(sh, t, k)
        cx, cy = L.w / 2, L.h / 2 - (60 if L.name == "vertical" else 0)
        w = max(d.text_width(x, "serif", L.ref_size) for x in sh.lines) + L.ref_size * 2.4
        h = L.ref_size * 4.6
        land = d.ease_in(d.prog(t, 0, next(iter(self.tl.cues[sh.no].values()), TEXT_IN)))
        a = land
        c.save()
        c.translate(cx, cy + 30 * (1 - land))
        c.drawRRect(d.rrect(8, 18, w, h, 14), d.fill("#000000", 0.7 * a, blur=22))
        c.drawRRect(d.rrect(0, 0, w, h, 14), d.fill("#121317", a))
        c.drawRRect(d.rrect(0, 0, w - 18, h - 18, 10), d.stroke(GOLD, 1.6, 0.8 * a))
        gap = L.ref_size * 1.45
        for i, ln in enumerate(sh.lines):
            d.draw_text(c, ln, 0, (i - 0.5) * gap, L.ref_size, WHITE if i else GOLD, a)
        c.restore()


_FRAME: Frame | None = None
_BUF = None
_SURF = None


def _worker(frame: int) -> bytes:
    global _BUF, _SURF
    if _SURF is None:
        _BUF = np.zeros((_FRAME.L.h, _FRAME.L.w, 4), np.uint8)
        _SURF = skia.Surface(_BUF)
    _FRAME.draw(_SURF.getCanvas(), frame)
    return _BUF.tobytes()


def still(tl: Timeline, L: Layout, frame: int) -> np.ndarray:
    global _FRAME, _BUF, _SURF
    _FRAME, _BUF, _SURF = Frame(tl, L), None, None
    return np.frombuffer(_worker(frame), np.uint8).reshape(L.h, L.w, 4).copy()


def render(tl: Timeline, L: Layout, out_mp4: str, wav: str, workers: int = 4, frames=None):
    """逐帧渲染 → H.264 yuv420p 30fps，音频 AAC 48 kHz。"""
    global _FRAME, _BUF, _SURF
    _FRAME, _BUF, _SURF = Frame(tl, L), None, None
    n = int(round(tl.total * FPS)) if frames is None else frames
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{L.w}x{L.h}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{n / FPS:.3f}", "-movflags", "+faststart", out_mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        with get_context("fork").Pool(workers) as pool:
            for buf in pool.imap(_worker, range(n), chunksize=8):
                proc.stdin.write(buf)
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")


# ---------------------------------------------------------------- 封面

def cover(L: Layout, topic: Topic) -> np.ndarray:
    """封面：题材提供的主体画面 + 主标题（一到两行）+ 单独一行副标题。"""
    buf = np.zeros((L.h, L.w, 4), np.uint8)
    surf = skia.Surface(buf)
    c = surf.getCanvas()
    c.clear(d.col(BG))
    Lc = replace(L, stage_oy=L.stage_oy + 150) if L.name == "vertical" else replace(L, stage_ox=L.stage_ox - 40)
    fr = Frame(build_timeline(topic), Lc)
    c.save()
    c.translate(Lc.stage_ox, Lc.stage_oy)
    c.scale(Lc.stage_scale, Lc.stage_scale)
    z = Lc.zoom
    c.translate(500 * (1 - z), 560 * (1 - z))
    c.scale(z, z)
    topic.cover_scene(c, fr.view)
    c.restore()
    fr._scrim(c)
    if L.name == "vertical":
        ts, x, y, align = 118, L.w / 2, 330, "center"
        for i, ln in enumerate(topic.cover_title):
            d.draw_text(c, ln, x, y + i * 150, ts, WHITE, align=align)
        c.drawLine(x - 50, y + 270, x + 50, y + 270, d.stroke(GOLD, 3))
        d.draw_text(c, topic.cover_subtitle, x, y + 345, 62, GOLD, name="serif_semi", align=align)
    else:
        ts, x, y = 104, 120, 350
        for i, ln in enumerate(topic.cover_title):
            d.draw_text(c, ln, x, y + i * 138, ts, WHITE, align="left")
        c.drawLine(x, y + 245, x + 90, y + 245, d.stroke(GOLD, 3))
        d.draw_text(c, topic.cover_subtitle, x, y + 320, 56, GOLD, name="serif_semi", align="left")
    return buf.copy()
