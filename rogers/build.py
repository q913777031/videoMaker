"""罗杰斯心理学 10 讲：复用阿德勒系列引擎（adler.core / adler.build）。

用法与 adler.build 相同，例如：
    python3 -m rogers.build                # 渲染全部 10 期到 out/rogers/epXX/
    python3 -m rogers.build 03 --sheet     # 逐镜联系表
    python3 -m rogers.build --verify       # 核验成片
    python3 -m rogers.build --publish      # 交付到 videos/rogers/
"""

from adler import build as B
from adler import core

core.SERIES.update(name="罗杰斯心理学", count="10讲", prefix="罗杰斯")
B.PKG = "rogers"
B.OUT = B.ROOT / "out" / "rogers"
B.MODS = {"01": "ep01_client", "02": "ep02_actualizing", "03": "ep03_self", "04": "ep04_worth",
          "05": "ep05_regard", "06": "ep06_empathy", "07": "ep07_congruence", "08": "ep08_listening",
          "09": "ep09_fully", "10": "ep10_relationship"}

if __name__ == "__main__":
    B.main()
