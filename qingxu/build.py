"""《伯恩斯新情绪疗法》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，
慢速讲解节奏（14 个场景：2 / 3×12 / 4 小节，每屏 ≈6.4 秒，画完停 4 拍）。每讲叙事形式不同，见 qingxu/PLAN.md。

用法：
    python3 -m qingxu.build 01 --sheet     # 逐镜联系表
    python3 -m qingxu.build 01             # 渲染到 out/qingxu/ep01/
    python3 -m qingxu.build --verify       # 核验成片
    python3 -m qingxu.build --publish      # 交付到 videos/qingxu/（接频道片尾；每讲带横屏封面；另出合集图与系列横屏封面）
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)
core.RULES.update(wb.SLOW_RULES)        # 慢速讲解节奏：14 个场景，每个 3 小节（≈6.4 秒），画完停 4 拍（见 CLAUDE.md「白板手绘节奏」）
wb.HOLD_BEATS = 4

core.SERIES.update(name="伯恩斯新情绪疗法", count="10讲", prefix="新情绪疗法", tagline="心情差的时候，先看看脑子里那句话")
B.PKG = "qingxu"
B.OUT = B.ROOT / "out" / "qingxu"
B.MODS = {"01": "wb01_mood", "02": "wb02_trap", "03": "wb03_trap2", "04": "wb04_column",
          "05": "wb05_action", "06": "wb06_critic", "07": "wb07_anger", "08": "wb08_worth",
          "09": "wb09_average", "10": "wb10_approval"}

# 系列规划：(期号, 概念, 片名)；详见 qingxu/PLAN.md（每讲叙事形式、14 个场景大纲、书中出处）
PLAN = [
    ("01", "想法管心情", "领导没回消息，你慌什么？"),
    ("02", "五种想歪", "这五种想法，你中了几个？"),
    ("03", "再五种想歪", "心里难受，就说明事情糟？"),
    ("04", "三栏法", "脑子里骂自己，怎么回嘴？"),
    ("05", "先动起来", "拖了一周的事，怎么开头？"),
    ("06", "被批评", "被领导当众批评，怎么接？"),
    ("07", "生气", "群里怼完同事，为什么又后悔？"),
    ("08", "价值不看业绩", "项目黄了，人就不值钱了？"),
    ("09", "敢于平凡", "非要做到满分，才敢交？"),
    ("10", "往下挖", "别人一不满意，你就慌？"),
]

if __name__ == "__main__":
    B.main()
