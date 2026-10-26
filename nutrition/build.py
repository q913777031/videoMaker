"""《动物为什么吃不胖》8 讲：复用阿德勒系列引擎（adler.core / adler.build）。

用法与 adler.build 相同，例如：
    python3 -m nutrition.build                # 渲染全部 8 讲到 out/nutrition/epXX/
    python3 -m nutrition.build 03 --sheet     # 逐镜联系表
    python3 -m nutrition.build --verify       # 核验成片
    python3 -m nutrition.build --publish      # 交付到 videos/nutrition/
"""

from adler import build as B
from adler import core

core.RULES.update(core.LEGACY)       # 旧系列：保持 2026-10 之前的慢节奏规则，成片不变

core.SERIES.update(name="动物为什么吃不胖", count="8讲", prefix="吃不胖")
B.PKG = "nutrition"
B.OUT = B.ROOT / "out" / "nutrition"
B.MODS = {"01": "ep01_target", "02": "ep02_geometry", "03": "ep03_appetites", "04": "ep04_balance",
          "05": "ep05_leverage", "06": "ep06_tradeoff", "07": "ep07_processed", "08": "ep08_practice"}

if __name__ == "__main__":
    B.main()
