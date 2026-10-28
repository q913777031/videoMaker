"""风格样片：用《系统之美》01 的钩子（镜头 1–4）与观点落版 + 弹簧（镜头 9–12）两段，按指定主题渲染约 17 秒样片。

用法：
    python3 -m themes.sample piying        # → out/themes/piying.mp4 与 4 张单帧
    python3 -m themes.sample anime --stills  # 只出单帧
"""

import importlib
import subprocess
import sys
import tempfile
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import skia
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
SEGMENTS = [(0, 4), (8, 12)]          # 镜头区间 [起, 止)
STILL_SHOTS = (0, 2, 8, 10)

_EP = None


def _frame(T: float) -> bytes:
    from adler import core

    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    core.draw_frame(surf.getCanvas(), _EP, T)
    return surf.makeImageSnapshot().tobytes()


def main():
    global _EP
    name = sys.argv[1]
    sys.argv = [sys.argv[0]]
    import xitong.build  # noqa: F401  系列配置（含水墨主题，主题模块会在其上覆盖）
    from adler import core
    from engine import audio
    from adler import build as B

    importlib.import_module(f"themes.{name}").install()
    ep = B.load("01")
    _EP = ep
    out = ROOT / "out" / "themes"
    out.mkdir(parents=True, exist_ok=True)
    for i in STILL_SHOTS:
        s = ep.shots[i]
        T = s.t1 - 0.2
        surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType,
                                                           skia.kPremul_AlphaType))
        core.draw_frame(surf.getCanvas(), ep, T)
        surf.makeImageSnapshot().save(str(out / f"{name}_{i:02d}.png"), skia.kPNG)
    if "--stills" in sys.argv[1:] or "--stills" in sys.orig_argv:
        return
    mix, *_ = core.build_audio(ep)
    times, chunks = [], []
    for a, b in SEGMENTS:
        t0, t1 = ep.shots[a].t0, ep.shots[b - 1].t1
        n = int(round((t1 - t0) * core.FPS))
        times += [t0 + k / core.FPS for k in range(n)]
        chunks.append(mix[int(t0 * audio.SR):int(t0 * audio.SR) + int(round(n / core.FPS * audio.SR))])
    clip = np.concatenate(chunks)
    fade = int(0.02 * audio.SR)
    clip[-fade:] *= np.linspace(1, 0, fade)[:, None] if clip.ndim == 2 else np.linspace(1, 0, fade)
    mp4 = out / f"{name}.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "a.wav")
        sf.write(wav, clip, audio.SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{core.W}x{core.H}",
               "-r", str(core.FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "21",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(mp4)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with get_context("fork").Pool(4) as pool:
            for buf in pool.imap(_frame, times, chunksize=6):
                proc.stdin.write(buf)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
    print(mp4)


if __name__ == "__main__":
    main()
