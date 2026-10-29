"""《系统之美》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，快节奏规则（每镜 ≤3 秒）。

用法：
    python3 -m xitong.build 01 --sheet     # 逐镜联系表
    python3 -m xitong.build 01             # 渲染到 out/xitong/ep01/
    python3 -m xitong.build --verify       # 核验成片
    python3 -m xitong.build --publish      # 交付到 videos/xitong/（每讲带 1080×1080 横屏封面；另出合集图与系列横屏封面）
    python3 -m xitong.build --square       # 只重出每讲横屏封面
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)                            # 2026-10-29 起改为白板手绘形式（10 讲均为白板分镜 wbNN_*.py）

core.SERIES.update(name="系统之美", count="10讲", prefix="系统之美", tagline="看懂背后的结构，问题就好解了")
B.PKG = "xitong"
B.OUT = B.ROOT / "out" / "xitong"
B.MODS = {"01": "wb01_system", "02": "wb02_stock", "03": "wb03_balancing", "04": "wb04_reinforcing",
          "05": "wb05_delay", "06": "wb06_limits", "07": "wb07_commons", "08": "wb08_drift",
          "09": "wb09_addiction", "10": "wb10_leverage"}

# 系列规划：(期号, 概念, 片名)
PLAN = [
    ("01", "系统是什么", "换了三份工作，烦心事怎么都一样？"),
    ("02", "存量与流量", "工资涨了，为什么还是存不下钱？"),
    ("03", "调节回路", "减肥为什么总会反弹？"),
    ("04", "增强回路", "为什么有人越学越快？"),
    ("05", "延迟", "为什么越着急，越容易出乱子？"),
    ("06", "增长的极限", "业绩为什么涨着涨着就不动了？"),
    ("07", "公地悲剧", "公司冰箱为什么总是乱糟糟？"),
    ("08", "目标侵蚀", "标准为什么越来越低？"),
    ("09", "上瘾", "为什么越熬夜越离不开咖啡？"),
    ("10", "杠杆点", "想改变，该从哪里下手？"),
]

if __name__ == "__main__":
    B.main()
