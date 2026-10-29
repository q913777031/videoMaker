"""新形式样片的共用时间轴：取《系统之美》01 的 8 个小节（镜头 1–4 钩子 + 镜头 9–12 观点落版与弹簧），
拼成约 17 秒的本地时间轴，给出每小节的实测拍点、文案与原片音效拍，并负责逐帧渲染与混音合成 mp4。

各形式只需实现 draw(c, t)：在 1080×1920 的 skia 画布上画出本地时刻 t 的一帧。
关键动作请落在 BARS[i]["beats"][k]（实测拍点）上，尤其是 BARS[i]["hits"] 列出的原片音效拍——音轨直接沿用原片混音。

用法（在各形式模块里）：
    from styles import seg
    if __name__ == "__main__":
        seg.main("phone", draw)            # → out/styles/phone.mp4，--stills 只出 8 张小节末单帧
"""

import subprocess
import sys
import tempfile
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import skia
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "styles"
W, H, FPS = 1080, 1920, 30
SHOTS = (0, 1, 2, 3, 8, 9, 10, 11)
TEXTS = ("新部门来了新领导", "团队也换了一半", "大家干劲十足", "三个月后",
         "不是人的问题，是结构", "书一开头，拿出弹簧", "手一松，它自己弹", "行为藏在结构里")
# 每小节的画面内容提要（各形式按自己的语言重新表现）
NOTES = (
    "新领导到岗，说“咱们重新出发！”",
    "工位上的人一个个换成新面孔",
    "大家举手欢呼、干劲十足",
    "时钟转过三个月（暗示：又回到老样子）",
    "观点落版：不是人的问题 / 是结构（音乐 drop，第 0、1 拍各一记重击）",
    "书中例子：一只手提起弹簧玩具",
    "手一松，弹簧自己上下弹（第 1 拍松手重击，第 2、3 拍回弹）",
    "金句：行为 藏在 结构 里（逐词弹出，“结构”高亮）",
)


def _load():
    sys_argv = sys.argv
    sys.argv = [sys.argv[0]]
    from adler import build as B
    from adler import core
    from themes import paper

    core.SERIES.update(name="系统之美", count="10讲", prefix="系统之美", tagline="看懂背后的结构，问题就好解了")
    B.PKG = "xitong"
    B.MODS = {"01": "ep01_system"}
    paper.install()
    ep = B.load("01")
    sys.argv = sys_argv
    bars, t = [], 0.0
    for n, i in enumerate(SHOTS):
        s = ep.shots[i]
        d = s.t1 - s.t0
        beats = [t + core.bt(s.b0 + k) - s.t0 for k in range(4)]
        hits = sorted({(b, sfx) for b, sfx, *_ in s.all_hits() if sfx})
        bars.append(dict(i=n, t0=t, t1=t + d, beats=beats, text=TEXTS[n], note=NOTES[n], hits=hits,
                         src=(s.t0, s.t1)))
        t += d
    return ep, core, bars


_EP, _CORE, BARS = _load()
TOTAL = BARS[-1]["t1"]


def bar_at(t: float) -> tuple[dict, float]:
    """本地时刻 t 所在小节与小节内时间。"""
    for b in BARS:
        if t < b["t1"]:
            return b, t - b["t0"]
    return BARS[-1], t - BARS[-1]["t0"]


def since(bar: dict, k: float, t: float) -> float:
    """距该小节第 k 拍（可为小数，按相邻拍线性插值）过去的秒数，负数表示还没到。"""
    beats = bar["beats"] + [bar["t1"]]
    i = int(k)
    frac = k - i
    tb = beats[i] + (beats[min(i + 1, 4)] - beats[i]) * frac
    return t - tb


def audio_clip() -> np.ndarray:
    """与本地时间轴对齐的原片混音（音乐 + 打击乐音效）。"""
    from engine import audio

    mix, *_ = _CORE.build_audio(_EP)
    chunks = []
    for b in BARS:
        a = int(round(b["src"][0] * audio.SR))
        n = int(round((b["t1"] - b["t0"]) * audio.SR))
        chunks.append(mix[a:a + n])
    clip = np.concatenate(chunks)
    fade = int(0.03 * audio.SR)
    clip[-fade:] *= np.linspace(1, 0, fade)[:, None] if clip.ndim == 2 else np.linspace(1, 0, fade)
    return clip


def mux(frames, name: str) -> Path:
    """frames：可迭代的 RGBA 字节串（W×H），按 FPS 编码并配上原片混音。"""
    from engine import audio

    OUT.mkdir(parents=True, exist_ok=True)
    mp4 = OUT / f"{name}.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "a.wav")
        sf.write(wav, audio_clip(), audio.SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(mp4)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for buf in frames:
            proc.stdin.write(buf)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
    return mp4


_DRAW = None


def _frame(t: float) -> bytes:
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    _DRAW(surf.getCanvas(), t)
    return surf.makeImageSnapshot().tobytes()


def still(draw, t: float, path: Path):
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    draw(surf.getCanvas(), t)
    surf.makeImageSnapshot().save(str(path), skia.kPNG)


def main(name: str, draw, workers: int = 4):
    """--stills：每小节末各出一张单帧（out/styles/<name>_N.png）；否则渲染整段 mp4。"""
    global _DRAW
    _DRAW = draw
    OUT.mkdir(parents=True, exist_ok=True)
    if "--stills" in sys.argv:
        for b in BARS:
            still(draw, b["t1"] - 0.12, OUT / f"{name}_{b['i']}.png")
        print(OUT / f"{name}_*.png")
        return
    n = int(round(TOTAL * FPS))
    times = [k / FPS for k in range(n)]
    with get_context("fork").Pool(workers) as pool:
        print(mux(pool.imap(_frame, times, chunksize=6), name))
