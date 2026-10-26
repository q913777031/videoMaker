"""《资治通鉴》系列：复用阿德勒纸片引擎（adler.core / adler.build），快节奏规则（每镜 ≤3 秒）。

用法：
    python3 -m zizhi.build 01 --sheet     # 逐镜联系表
    python3 -m zizhi.build 01             # 渲染到 out/zizhi/ep01/
    python3 -m zizhi.build --verify       # 核验成片
    python3 -m zizhi.build --publish      # 交付到 videos/zizhi/
"""

from adler import build as B
from adler import core

core.SERIES.update(name="资治通鉴", count="10讲", prefix="资治通鉴", tagline="两千年前的识人术，今天还管用")
B.PKG = "zizhi"
B.OUT = B.ROOT / "out" / "zizhi"
B.MODS = {"01": "ep01_talent_virtue"}

if __name__ == "__main__":
    B.main()
