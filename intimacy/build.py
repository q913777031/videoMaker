"""《亲密关系》10 讲：复用阿德勒系列引擎（adler.core / adler.build）与光效层（adler.fx）。

用法与 adler.build 相同，例如：
    python3 -m intimacy.build                # 渲染全部 10 讲到 out/intimacy/epXX/
    python3 -m intimacy.build 01 --sheet     # 逐镜联系表
    python3 -m intimacy.build --verify       # 核验成片
    python3 -m intimacy.build --publish      # 交付到 videos/intimacy/
"""

from adler import build as B
from adler import core

core.SERIES.update(name="亲密关系", count="10讲", prefix="亲密关系", tagline="不是不爱，是没读懂彼此")
B.PKG = "intimacy"
B.OUT = B.ROOT / "out" / "intimacy"
B.MODS = {"01": "ep01_belong", "02": "ep02_proximity", "03": "ep03_similarity", "04": "ep04_attribution",
          "05": "ep05_horsemen", "06": "ep06_investment", "07": "ep07_love", "08": "ep08_attachment",
          "09": "ep09_jealousy", "10": "ep10_capitalize"}

if __name__ == "__main__":
    B.main()
