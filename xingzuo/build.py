"""《十二星座》系列：复用阿德勒系列引擎（adler.core / adler.build）与光效层（adler.fx）。

用法与 adler.build 相同，例如：
    python3 -m xingzuo.build                # 渲染已完成的各讲到 out/xingzuo/epXX/
    python3 -m xingzuo.build 01 --sheet     # 逐镜联系表
    python3 -m xingzuo.build --verify       # 核验成片
    python3 -m xingzuo.build --publish      # 交付到 videos/xingzuo/
"""

from adler import build as B
from adler import core

core.SERIES.update(name="十二星座", count="12讲", prefix="十二星座", tagline="你的星座，值得被好好夸一次")
B.PKG = "xingzuo"
B.OUT = B.ROOT / "out" / "xingzuo"
B.MODS = {"01": "ep01_aries", "02": "ep02_taurus", "03": "ep03_gemini", "04": "ep04_cancer", "05": "ep05_leo", "06": "ep06_virgo", "07": "ep07_libra", "08": "ep08_scorpio", "09": "ep09_sagittarius", "10": "ep10_capricorn", "11": "ep11_aquarius", "12": "ep12_pisces"}

if __name__ == "__main__":
    B.main()
