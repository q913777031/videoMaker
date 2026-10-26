"""《熬夜欠的觉，周末能补回来吗？》构建入口。

用法：
    python3 -m sleep.build --sample              # 10 秒示例（钩子段）→ out/sleep/sample.mp4
    python3 -m sleep.build --sample --stills 1.5,6  # 示例段静帧 → out/sleep/stills/
    python3 -m sleep.build --chart allnighter    # 模型曲线样张 → out/sleep/chart_allnighter.png
"""

import sys
from pathlib import Path

import numpy as np
import skia

from engine.gfx import H, W, gradient_bg, vignette
from engine.timeline import Video

from . import art, script

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "sleep"


def _save(arr: np.ndarray, path: Path):
    from PIL import Image
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr[:, :, :3]).save(path)


def chart_png(name: str, path: Path, t0: float = 18.0, t1: float = 40.0):
    """把一个模型场景画成整张样图，用来核对曲线形状与配色。"""
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    gradient_bg(c, art.PALETTES["lab"]["bg"])
    vignette(c, 0.5)
    chart = art.Chart(name, t0, t1)
    chart.draw(c, 1.0, t=0.3)
    _save(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType), path)


def main():
    args = sys.argv[1:]
    OUT.mkdir(parents=True, exist_ok=True)
    if "--chart" in args:
        name = args[args.index("--chart") + 1]
        chart_png(name, OUT / f"chart_{name}.png")
        return
    if "--sample" in args:
        video = Video(script.SAMPLE, art.PALETTES, voice="zv_yunxi")
        video.build()
        print(f"sample duration {video.total:.2f}s")
        if "--stills" in args:
            for s in args[args.index("--stills") + 1].split(","):
                _save(video.still(float(s)), OUT / "stills" / f"sample_{float(s):05.2f}.png")
            return
        video.render(str(OUT / "sample.mp4"))


if __name__ == "__main__":
    main()
