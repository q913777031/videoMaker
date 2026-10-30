"""《活出生命的意义》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，
慢速讲解节奏（14 个场景：2 / 3×12 / 4 小节，每屏 ≈6.4 秒，画完停 4 拍）。分镜规划见 yiyi/PLAN.md。

用法：
    python3 -m yiyi.build 01 --sheet     # 逐镜联系表
    python3 -m yiyi.build 01             # 渲染到 out/yiyi/ep01/
    python3 -m yiyi.build --verify       # 核验成片
    python3 -m yiyi.build --publish      # 交付到 videos/yiyi/（接频道片尾；每讲带横屏封面；另出合集图与系列横屏封面）
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)
core.RULES.update(wb.SLOW_RULES)        # 慢速讲解节奏：14 个场景，每个 3 小节（≈6.4 秒），画完停 4 拍（见 CLAUDE.md「白板手绘节奏」）
wb.HOLD_BEATS = 4

core.SERIES.update(name="活出生命的意义", count="10讲", prefix="活出意义", tagline="累的时候，靠什么撑下去")
B.PKG = "yiyi"
B.OUT = B.ROOT / "out" / "yiyi"
B.MODS = {"01": "wb01_why", "02": "wb02_choice", "03": "wb03_ask", "04": "wb04_three",
          "05": "wb05_vacuum", "06": "wb06_love", "07": "wb07_suffer", "08": "wb08_paradox",
          "09": "wb09_granary", "10": "wb10_twice"}

# 系列规划：(期号, 概念, 片名)；每讲叙事形式见 PLAN.md（相邻两讲不重复）
PLAN = [
    ("01", "为什么而活", "累到想辞职，靠什么撑下去？"),
    ("02", "最后的自由", "事情改不了，心情能自己定吗？"),
    ("03", "生活在发问", "别再问图啥，生活在问你"),
    ("04", "三条路", "意义从哪来？书里给了三条路"),
    ("05", "存在的空虚", "周日晚上，为什么特别没劲？"),
    ("06", "想着一个人", "撑不住的时候，你会想起谁？"),
    ("07", "苦难的意义", "躲不开的难事，怎么扛过去？"),
    ("08", "矛盾意向", "越怕紧张，为什么越紧张？"),
    ("09", "过去的粮仓", "日子一天天过去，算白过吗？"),
    ("10", "当作第二次活", "要是能重来，今天你怎么过？"),
]

if __name__ == "__main__":
    B.main()
