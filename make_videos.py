"""渲染无声知识短视频：python3 make_videos.py [04 05 06 07 08]（缺省全部）"""
import importlib
import sys
import time
from pathlib import Path

from explainer.engine import render

MODS = {"04": "ep04_availability", "05": "ep05_base_rate", "06": "ep06_small_numbers",
        "07": "ep07_regression", "08": "ep08_correlation"}
OUT = Path(__file__).resolve().parent / "videos"

if __name__ == "__main__":
    for k in (sys.argv[1:] or list(MODS)):
        ep = importlib.import_module("explainer." + MODS[k]).build()
        out = OUT / f"{ep.name}.mp4"
        t0 = time.time()
        print(f"[{k}] {ep.name}：{ep.total:.1f}s，{ep.chars()} 字，{len(ep.shots)} 个镜头 → {out}", flush=True)
        render(ep, str(out))
        print(f"[{k}] 完成，用时 {time.time() - t0:.0f}s，{out.stat().st_size / 1e6:.1f}MB", flush=True)
