"""渲染：多进程逐帧绘制并经 FFmpeg 编码（H.264 / yuv420p / 30 fps），单帧导出与封面绘制。"""

import dataclasses
import subprocess
from multiprocessing import get_context

import numpy as np
import skia

from engine import gfx

from . import draw as D
from . import story
from .scenes import Film
from .story import FPS, GOLD, INK, WHITE

_FILM: Film | None = None
_BUF = None
_SURF = None


def _init(film: Film):
    global _FILM
    _FILM = film


def _worker(f: int) -> bytes:
    global _BUF, _SURF
    L = _FILM.L
    if _SURF is None:
        _BUF = np.zeros((L.H, L.W, 4), np.uint8)
        _SURF = skia.Surface(_BUF)
    c = _SURF.getCanvas()
    c.save()
    _FILM.frame(c, f)
    c.restore()
    return _BUF.tobytes()


def still(film: Film, f: int) -> np.ndarray:
    _init(film)
    return np.frombuffer(_worker(f), np.uint8).reshape(film.L.H, film.L.W, 4).copy()


def render(film: Film, out: str, audio: str | None = None, workers: int = 4, frames: range | None = None):
    """逐帧渲染为 MP4；audio 为 None 时输出无音频流的画面预览。"""
    L = film.L
    frames = frames or range(film.tl.total_frames)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{L.W}x{L.H}",
           "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-i", audio]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS)]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", f"{len(frames) / FPS:.4f}"]
    cmd += ["-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    _init(film)
    try:
        with get_context("fork").Pool(workers) as pool:
            for buf in pool.imap(_worker, frames, chunksize=8):
                proc.stdin.write(buf)
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")


def cover(L: D.Layout, out: str):
    """封面（深夜卧室版）：床一半落在地板、一半压在跑步机上；人拿着已熄屏的手机；时钟 00:00。"""
    from .scenes import LIE, REST_HAND, with_arm
    buf = np.zeros((L.H, L.W, 4), np.uint8)
    surf = skia.Surface(buf)
    c = surf.getCanvas()
    D.background(c, L, warm=0.6)
    LL = dataclasses.replace(L, stage_x=-10, stage_y=640, stage_s=1.2)
    cam = (1.0, 470, 640)
    c.save()
    D.apply_camera(c, LL, cam, 0.55)
    D.blur_layer(c, 7)
    D.room_far_night(c, 0, 0.9, lamp=0.6)
    c.restore()
    c.restore()
    c.save()
    D.apply_camera(c, LL, cam)
    D.floor_line(c)
    split = 520
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(split, -2000, 3000, 3000))
    D.belt(c, 0, 37, 1.0, 0.6, 0, 230, 800)
    c.restore()
    D.nightstand(c)
    D.clock(c, "00:00", True, 1.0, glow=0.6)
    D.lamp(c, 0.6)
    D.bed_back(c)
    P = with_arm(dict(LIE), REST_HAND)
    D.person_back(c, P)
    D.blanket(c, P)
    D.person_front(c, P, hand_item=lambda c, h: D.icon_phone(c, h[0] + 6, h[1] - 18, 1.0, 1.0, lit=0.0))
    D.gold_line(c, [(split, 480), (split, 900)], 2.0, 0.9, glow=0.5)
    c.restore()
    title, sub = story.COVER["title"], story.COVER["subtitle"]
    tx, ty, maxw = 90, 300, 830
    rows = title.split("，")
    rows = [rows[0] + "，", rows[1]] if len(rows) == 2 else [title]
    size = min(120, maxw / max(gfx.text_width(r, 1, "black") for r in rows))
    for k, r in enumerate(rows):
        gfx.draw_text(c, r, tx, ty + k * size * 1.2, size, "black", WHITE, 1, "left", shadow=(0, 6, 10, "#000000"))
    yb = ty + (len(rows) - 1) * size * 1.2 + size * 0.85
    D.gold_line(c, [(tx, yb), (tx + 220, yb)], 2.4, 1)
    gfx.draw_text(c, sub, tx, yb + 80, 62, "bold", GOLD, 1, "left")
    surf.makeImageSnapshot().save(out, skia.kPNG)
