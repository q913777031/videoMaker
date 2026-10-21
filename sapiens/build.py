"""《人类简史》10 讲：复用阿德勒系列引擎（adler.core / adler.build）与光效层（adler.fx）。

用法与 adler.build 相同，例如：
    python3 -m sapiens.build                # 渲染全部 10 讲到 out/sapiens/epXX/
    python3 -m sapiens.build 01 --sheet     # 逐镜联系表
    python3 -m sapiens.build --verify       # 核验成片
    python3 -m sapiens.build --publish      # 交付到 videos/sapiens/
"""

from adler import build as B
from adler import core

core.RULES.update(core.LEGACY)       # 旧系列：保持 2026-10 之前的慢节奏规则，成片不变

core.SERIES.update(name="人类简史", count="10讲", prefix="人类简史", tagline="你今天的烦恼，七万年前就埋下了")
B.PKG = "sapiens"
B.OUT = B.ROOT / "out" / "sapiens"
B.MODS = {"01": "ep01_fiction", "02": "ep02_gossip", "03": "ep03_farming", "04": "ep04_luxury", "05": "ep05_order",
          "06": "ep06_money", "07": "ep07_credit", "08": "ep08_ignorance", "09": "ep09_happiness", "10": "ep10_gods"}

if __name__ == "__main__":
    B.main()
