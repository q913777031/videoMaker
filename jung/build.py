"""荣格心理学 10 讲：复用阿德勒系列引擎（adler.core / adler.build），只替换系列标识、期目与输出目录。

用法与 adler.build 相同：
    python3 -m jung.build                   # 渲染全部 10 期到 out/jung/epXX/
    python3 -m jung.build 03 --sheet        # 逐镜联系表
    python3 -m jung.build --verify          # 核验
    python3 -m jung.build --publish         # 复制交付物到 videos/jung/
"""

from adler import build as B
from adler import core

core.SERIES.update(name="荣格心理学", count="10讲", prefix="荣格")
B.PKG = "jung"
B.OUT = B.ROOT / "out" / "jung"
B.MODS = {
    "01": "ep01_collective", "02": "ep02_archetype", "03": "ep03_persona", "04": "ep04_shadow",
    "05": "ep05_anima", "06": "ep06_attitude", "07": "ep07_functions", "08": "ep08_complex",
    "09": "ep09_dreams", "10": "ep10_individuation",
}

if __name__ == "__main__":
    B.main()
