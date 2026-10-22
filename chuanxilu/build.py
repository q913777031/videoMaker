"""《传习录》系列构建。

python3 -m chuanxilu.build ep01 --sheet          # 估算排时（不需旁白），每镜一张静帧拼成联系表
python3 -m chuanxilu.build ep01 --still 12.5,40  # 估算排时下的单帧
python3 -m chuanxilu.build ep01                  # 完整成片（需先 python3 -m chuanxilu.voice ep01）
python3 -m chuanxilu.build ep01 --verify         # 核验已渲染成片
"""

import importlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import skia

from engine import gfx

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "chuanxilu"


def _video(ep: str):
    return importlib.import_module(f"chuanxilu.{ep}").video()


def _layout_estimate(v):
    cps = 4.6
    durs = []
    for s in v.scenes:
        d = s.lead + sum(len(gfx.plain(ln.text)) / (cps * ln.speed) + ln.pause for ln in s.lines) + s.tail
        durs.append(max(1.5, d))
    v.layout_fixed(durs, cps)


def _save(arr: np.ndarray, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType).save(str(path))


def sheet(ep: str, real: bool = False):
    """每个场景取 75% 处一帧，拼成 6 列联系表（缩小到 1/4）。"""
    v = _video(ep)
    v.build(with_audio=False) if real else _layout_estimate(v)
    import cv2
    tiles = []
    for s in v.scenes:
        img = v.still(s.t0 + s.duration * 0.75)
        small = cv2.resize(img, (gfx.W // 4, gfx.H // 4), interpolation=cv2.INTER_AREA)
        cv2.putText(small, s.name, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 200, 255), 2)
        tiles.append(small)
    cols = 6
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.concatenate(tiles[i:i + cols], axis=1) for i in range(0, len(tiles), cols)]
    out = OUT / ep / "sheet.png"
    _save(np.concatenate(rows, axis=0), out)
    print(out, f"total {v.total:.1f}s")


def stills(ep: str, times: list[float], real: bool = False):
    v = _video(ep)
    v.build(with_audio=False) if real else _layout_estimate(v)
    for t in times:
        out = OUT / ep / "stills" / f"{t:06.2f}.png"
        _save(v.still(t), out)
        print(out)


def render(ep: str):
    v = _video(ep)
    v.build()
    out = OUT / ep
    out.mkdir(parents=True, exist_ok=True)
    mp4 = out / f"{ep}.mp4"
    print(f"render {v.total:.1f}s → {mp4}")
    v.render(str(mp4))
    timing = [dict(scene=s.name, t0=round(s.t0, 3), dur=round(s.duration, 3),
                   lines=[dict(text=gfx.plain(ln.text), start=round(s.t0 + a, 3), end=round(s.t0 + b, 3))
                          for ln, a, b in zip(s.lines, s.starts, s.ends)]) for s in v.scenes]
    (out / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")
    print(verify(mp4))


def verify(mp4: Path) -> str:
    """时长、编码、分辨率与响度（EBU R128 积分响度、真峰值）。"""
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate",
                            "-show_entries", "format=duration", "-of", "json", str(mp4)], capture_output=True,
                           text=True, check=True).stdout
    loud = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    summary = loud[loud.rfind("Summary:"):]
    return probe + summary


if __name__ == "__main__":
    ep = sys.argv[1]
    args = sys.argv[2:]
    real = "--real" in args
    if "--sheet" in args:
        sheet(ep, real)
    elif "--still" in args:
        stills(ep, [float(x) for x in args[args.index("--still") + 1].split(",")], real)
    elif "--verify" in args:
        print(verify(OUT / ep / f"{ep}.mp4"))
    else:
        render(ep)
