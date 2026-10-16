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
    """封面：一半沙发、一半跑步机，人物拿着已熄屏的手机；主标题一行、副标题单独一行。"""
    buf = np.zeros((L.H, L.W, 4), np.uint8)
    surf = skia.Surface(buf)
    c = surf.getCanvas()
    D.background(c, L)
    if L.horizontal:
        cam, sx, sy, ss = (1.0, 470, 640), 640, -120, 1.3
    else:
        cam, sx, sy, ss = (1.0, 470, 640), -230, 520, 1.5
    LL = dataclasses.replace(L, stage_x=sx, stage_y=sy, stage_s=ss)
    c.save()
    D.apply_camera(c, LL, cam, 0.55)
    D.blur_layer(c, 7)
    D.room_far(c, 0, 0.8)
    c.restore()
    c.restore()
    c.save()
    D.apply_camera(c, LL, cam)
    D.floor_line(c)
    # 右半：跑步机（裁切到分割线右侧）；左半：普通地面
    split = 420
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(split, -2000, 3000, 3000))
    D.belt(c, 0, 37, 1.0, 0.6)
    for k in range(4):
        D.line(c, split + 60 + k * 60, 820, split + 20 + k * 60, 820, D.stroke(GOLD, 2, 0.5 - k * 0.1))
    c.restore()
    D.sofa_back(c)
    P = dict(D.POSE_SIT)
    D.person_back(c, P)
    D.sofa_front(c)
    D.person_front(c, P, hand_item=lambda c, h: D.icon_phone(c, h[0] + 10, h[1] - 22, 1.0, 1.0, lit=0.0))
    D.gold_line(c, [(split, 380), (split, 900)], 2.0, 0.9, glow=0.5)
    c.restore()
    title, sub = story.COVER["title"], story.COVER["subtitle"]
    if L.horizontal:
        tx, ty, size, ssize, maxw = 80, 420, 108, 58, 760
    else:
        tx, ty, size, ssize, maxw = 90, 380, 104, 60, 830
    size = min(size, maxw / gfx.text_width(title, 1, "black"))
    gfx.draw_text(c, title, tx, ty, size, "black", WHITE, 1, "left", shadow=(0, 6, 10, "#000000"))
    D.gold_line(c, [(tx, ty + size * 0.85), (tx + 220, ty + size * 0.85)], 2.4, 1)
    gfx.draw_text(c, sub, tx, ty + size * 0.85 + ssize * 1.2, ssize, "bold", GOLD, 1, "left")
    surf.makeImageSnapshot().save(out, skia.kPNG)
