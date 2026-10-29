"""《孤独是可耻的》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，场景节奏（每个场景 2 小节、画完停住）。

用法：
    python3 -m gudu.build 01 --sheet     # 逐镜联系表
    python3 -m gudu.build 01             # 渲染到 out/gudu/ep01/
    python3 -m gudu.build --verify       # 核验成片
    python3 -m gudu.build --publish      # 交付到 videos/gudu/（接频道片尾；每讲带横屏封面；另出合集图与系列横屏封面）
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)
core.RULES.update(wb.SLOW_RULES)        # 慢速讲解节奏：14 个场景，每个 3 小节（≈6.4 秒），画完停 4 拍（见 CLAUDE.md「白板手绘节奏」）
wb.HOLD_BEATS = 4

core.SERIES.update(name="孤独是可耻的", count="10讲", prefix="孤独", tagline="孤单的时候，身体和脑子在发生什么")
B.PKG = "gudu"
B.OUT = B.ROOT / "out" / "gudu"
B.MODS = {"01": "wb01_signal", "02": "wb02_quality", "03": "wb03_health", "04": "wb04_guard",
          "05": "wb05_control", "06": "wb06_leash", "07": "wb07_social", "08": "wb08_pet",
          "09": "wb09_extend", "10": "wb10_expect"}

# 系列规划：(期号, 概念, 片名)
PLAN = [
    ("01", "孤独是信号", "一个人吃饭，心里为什么发空？"),
    ("02", "感觉不看人数", "群里几百人，为什么还是孤单？"),
    ("03", "孤独伤身", "一个人住久了，为什么总睡不好？"),
    ("04", "越孤单越戒备", "越孤单，为什么越不想见人？"),
    ("05", "孤独与自控", "一个人的晚上，为什么管不住嘴？"),
    ("06", "弹性的绳子", "有人独处挺好，有人一天都熬不住？"),
    ("07", "人是社会动物", "被同事晾在一边，为什么那么难受？"),
    ("08", "找替代品", "越孤单，为什么越爱跟猫说话？"),
    ("09", "迈出第一步", "想交朋友，第一步迈哪？"),
    ("10", "挑人与往好处想", "交朋友，该找谁、怎么想？"),
]

if __name__ == "__main__":
    B.main()
