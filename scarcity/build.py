"""《稀缺》8 讲：复用阿德勒系列引擎（adler.core / adler.build）与光效层（adler.fx）。

用法与 adler.build 相同，例如：
    python3 -m scarcity.build                # 渲染全部 8 讲到 out/scarcity/epXX/
    python3 -m scarcity.build 01 --sheet     # 逐镜联系表
    python3 -m scarcity.build --verify       # 核验成片
    python3 -m scarcity.build --publish      # 交付到 videos/scarcity/
"""

from adler import build as B
from adler import core

core.RULES.update(core.LEGACY)       # 旧系列：保持 2026-10 之前的慢节奏规则，成片不变

core.SERIES.update(name="稀缺", count="8讲", prefix="稀缺", tagline="为什么越缺，越忙越乱")
B.PKG = "scarcity"
B.OUT = B.ROOT / "out" / "scarcity"
B.MODS = {"01": "ep01_mindset", "02": "ep02_focus", "03": "ep03_tunneling", "04": "ep04_bandwidth",
          "05": "ep05_borrowing", "06": "ep06_trap", "07": "ep07_slack", "08": "ep08_design"}

if __name__ == "__main__":
    B.main()
