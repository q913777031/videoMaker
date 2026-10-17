"""时间轴构建（叙事基准或按原曲校准）、逐帧合成（场景 + 字幕 + 角标）、多进程渲染与封面。"""

import math
import subprocess
from dataclasses import dataclass
from multiprocessing import get_context

import numpy as np
import skia

from . import draw as d
from . import scenes
from .config import BG, FPS, GOLD, WHITE, Layout, Shot, shots

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


def build_timeline(analysis=None) -> Timeline:
    """无原曲时使用叙事基准；有原曲时在相邻镜头间小幅移动边界、把候选事件贴到真实起音。"""
    from . import music
    sh = shots()
    total = 90.0 if analysis is None else analysis.total
    bounds = [s.start for s in sh] + [total]
    if analysis is not None:
        for i in range(1, len(sh)):
            b = bounds[i] * total / 90.0
            nt, strength, _ = music.snap(analysis, b, b - 0.3, b + 0.3, min_strength=0.6)
            bounds[i] = round((nt if strength else b) * FPS) / FPS
    for i, s in enumerate(sh):
        s.start, s.dur = bounds[i], bounds[i + 1] - bounds[i]
    cues, events = {}, []
    for s in sh:
        cues[s.no] = {}
        for cu in s.cues:
            base = cu.t
            row = {"shot": s.no, "key": cu.key, "sound": cu.sound, "action": cu.action, "gain": cu.gain,
                   "base": s.start + base, "strength": None, "conf": "未确认", "method": "", "mix": ""}
            local = base
            if analysis is not None:
                lo, hi = s.start + max(0.25, base - 0.4), s.start + min(s.dur - 0.5, base + 0.4)
                thr = 0.45 if cu.snap else 0.25
                nt, strength, conf = music.snap(analysis, s.start + base, lo, hi, min_strength=thr)
                local = nt - s.start
                row.update(strength=round(strength, 3), conf=conf,
                           method="谱通量起音检测（自动，未人工试听）" if strength else "窗口内无合适重音，保持叙事位置")
                if not strength:
                    row["action"] += "（柔和动作，未贴拍）"
                if cu.sound == "kick":
                    low = music.low_energy_at(analysis, nt)
                    if low > 0.5:
                        row["gain"], row["mix"] = 0.0, f"原曲低频占比 {low:.2f}，取消低鼓叠加"
                    elif low > 0.3:
                        row["gain"], row["mix"] = cu.gain * 0.5, f"原曲低频占比 {low:.2f}，低鼓减半"
            else:
                row["method"] = "未检测：原曲缺失，按叙事基准放置"
            local = round(local * FPS) / FPS
            cues[s.no][cu.key] = local
            row["t"] = s.start + local
            if cu.sound and row["gain"] > 0:
                events.append(row)
            elif cu.sound:
                row["sound"] = ""
                events.append(row)
            else:
                events.append(row)
    # 镜头 05 承接镜头 04 结尾的轨道角度
    cues[5]["_t4"] = sh[3].dur - cues[4]["lap"]
    return Timeline(sh, total, cues, events, analysis is not None)


# ---------------------------------------------------------------- 逐帧

class Frame:
    def __init__(self, tl: Timeline, L: Layout):
        self.tl, self.L = tl, L
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
        scenes.SCENES[sh.no](c, t, sh.dur, self.tl.cues[sh.no], self.view)
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
        if sh.no == 15:
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
        a_out = 1 - d.prog(t, sh.dur - TEXT_OUT, TEXT_OUT) if sh.no != 15 else 1.0
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
        land = d.ease_in(d.prog(t, 0, self.tl.cues[15]["credit"]))
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

def cover(L: Layout) -> np.ndarray:
    """封面：床边一张小卡片投射出巨大的城市阴影；主标题两行、副标题一行。"""
    buf = np.zeros((L.h, L.w, 4), np.uint8)
    surf = skia.Surface(buf)
    c = surf.getCanvas()
    c.clear(d.col(BG))
    from dataclasses import replace
    Lc = replace(L, stage_oy=L.stage_oy + 150) if L.name == "vertical" else replace(L, stage_ox=L.stage_ox - 40)
    fr = Frame(build_timeline(None), Lc)
    c.save()
    c.translate(Lc.stage_ox, Lc.stage_oy)
    c.scale(Lc.stage_scale, Lc.stage_scale)
    z = Lc.zoom
    c.translate(500 * (1 - z), 560 * (1 - z))
    c.scale(z, z)
    scenes.bedroom(c, 0, fr.view, 3.3, city=1.0, card_rot=-12)
    c.restore()
    fr._scrim(c)
    if L.name == "vertical":
        ts, x, y, align = 118, L.w / 2, 330, "center"
        for i, ln in enumerate(("一到晚上，", "就否定人生？")):
            d.draw_text(c, ln, x, y + i * 150, ts, WHITE, align=align)
        c.drawLine(x - 50, y + 270, x + 50, y + 270, d.stroke(GOLD, 3))
        d.draw_text(c, "一件小事，怎么变成全部", x, y + 345, 62, GOLD, name="serif_semi", align=align)
    else:
        ts, x, y = 104, 120, 350
        for i, ln in enumerate(("一到晚上，", "就否定人生？")):
            d.draw_text(c, ln, x, y + i * 138, ts, WHITE, align="left")
        c.drawLine(x, y + 245, x + 90, y + 245, d.stroke(GOLD, 3))
        d.draw_text(c, "一件小事，怎么变成全部", x, y + 320, 56, GOLD, name="serif_semi", align="left")
    return buf.copy()
