"""真 3D 微缩场景样片：three.js 黏土小岛（styles/miniature3d_web/），复用 ac3d 的 Playwright 逐帧渲染器。

用法：
    python3 -m styles.miniature3d --stills 1.0,9.2,14.0   # 静帧 → out/styles/miniature3d_stills/
    python3 -m styles.miniature3d                         # → out/styles/miniature3d.mp4（配原片混音）
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from styles import seg

ROOT = seg.ROOT
WEB = ROOT / "styles" / "miniature3d_web"
PAGE = "styles/miniature3d_web/index.html"
RENDER = ROOT / "ac3d" / "render.cjs"


def write_timeline():
    data = dict(end=seg.TOTAL, bars=[dict(t0=b["t0"], t1=b["t1"], beats=b["beats"], hits=b["hits"], text=b["text"])
                                     for b in seg.BARS])
    (WEB / "timeline.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def frames_from(mp4: Path):
    """把无声 mp4 解码成 RGBA 字节流，交给 seg.mux 配音轨。"""
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", str(mp4), "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                         stdout=subprocess.PIPE)
    n = seg.W * seg.H * 4
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield buf
    p.wait()


def main():
    write_timeline()
    args = sys.argv[1:]
    if args and args[0] == "--stills":
        out = seg.OUT / "miniature3d_stills"
        subprocess.run(["node", str(RENDER), "--page", PAGE, "--stills", str(out), args[1]], check=True)
        return
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        silent = Path(tmp) / "silent.mp4"
        subprocess.run(["node", str(RENDER), "--page", PAGE, "--video", str(silent), "--workers", "3"], check=True)
        out = seg.mux(frames_from(silent), "miniature3d")
    print(out, f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
