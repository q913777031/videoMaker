"""马斯洛心理学 10 讲：复用阿德勒系列引擎（adler.core / adler.build）。

用法与 adler.build 相同，例如：
    python3 -m maslow.build                # 渲染全部 10 期到 out/maslow/epXX/
    python3 -m maslow.build 03 --sheet     # 逐镜联系表
    python3 -m maslow.build --verify       # 核验成片
    python3 -m maslow.build --publish      # 交付到 videos/maslow/
"""

from adler import build as B
from adler import core

core.SERIES.update(name="马斯洛心理学", count="10讲", prefix="马斯洛")
B.PKG = "maslow"
B.OUT = B.ROOT / "out" / "maslow"
B.MODS = {"01": "ep01_hierarchy", "02": "ep02_deficiency", "03": "ep03_safety", "04": "ep04_belonging",
          "05": "ep05_esteem", "06": "ep06_actualization", "07": "ep07_peak", "08": "ep08_pyramid",
          "09": "ep09_jonah", "10": "ep10_transcendence"}

if __name__ == "__main__":
    B.main()
