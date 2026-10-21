"""《稀缺》4 讲：复用阿德勒系列引擎（adler.core / adler.build）与光效层（adler.fx）。

用法与 adler.build 相同，例如：
    python3 -m scarcity.build                # 渲染全部 4 讲到 out/scarcity/epXX/
    python3 -m scarcity.build 01 --sheet     # 逐镜联系表
    python3 -m scarcity.build --verify       # 核验成片
    python3 -m scarcity.build --publish      # 交付到 videos/scarcity/
"""

from adler import build as B
from adler import core

core.SERIES.update(name="稀缺", count="4讲", prefix="稀缺")
B.PKG = "scarcity"
B.OUT = B.ROOT / "out" / "scarcity"
B.MODS = {"01": "ep01_bandwidth", "02": "ep02_tunneling", "03": "ep03_trap", "04": "ep04_slack"}

if __name__ == "__main__":
    B.main()
