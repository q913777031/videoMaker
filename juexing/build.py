"""《认知觉醒》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，慢速讲解节奏
（每讲 14 个场景：2 / 3×12 / 4 小节，每屏 ≈6.4 秒，画完停 4 拍）。选题与每讲分镜大纲见 juexing/PLAN.md。

用法：
    python3 -m juexing.build 01 --sheet     # 逐镜联系表
    python3 -m juexing.build 01             # 渲染到 out/juexing/ep01/
    python3 -m juexing.build --verify       # 核验成片
    python3 -m juexing.build --publish      # 交付到 videos/juexing/（接频道片尾；每讲带横屏封面；另出合集图与系列横屏封面）
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)
core.RULES.update(wb.SLOW_RULES)        # 慢速讲解节奏：14 个场景，每个 3 小节（≈6.4 秒），画完停 4 拍（见 CLAUDE.md「白板手绘节奏」）
wb.HOLD_BEATS = 4

core.SERIES.update(name="认知觉醒", count="10讲", prefix="觉醒", tagline="道理都懂却做不到，脑子里谁在拿主意")
B.PKG = "juexing"
B.OUT = B.ROOT / "out" / "juexing"
B.MODS = {"01": "wb01_brain", "02": "wb02_anxiety", "03": "wb03_patience", "04": "wb04_meta",
          "05": "wb05_focus", "06": "wb06_edge", "07": "wb07_feedback", "08": "wb08_clear",
          "09": "wb09_view", "10": "wb10_five"}

# 系列规划：(期号, 概念, 片名)
PLAN = [
    ("01", "三重大脑", "说好十一点睡，怎么又刷到一点？"),
    ("02", "焦虑的根源", "事一多就慌，到底在慌啥？"),
    ("03", "耐心", "学了三个月没起色，还学吗？"),
    ("04", "元认知", "被说一句就上头，怎么刹住？"),
    ("05", "专注", "忙了一整天，正事一件没干？"),
    ("06", "舒适区边缘", "天天在练，怎么还在原地？"),
    ("07", "反馈", "打卡一百天，怎么没变化？"),
    ("08", "清晰力", "道理都懂，为啥就是不动？"),
    ("09", "多个视角", "领导一句话，郁闷一整天？"),
    ("10", "人生五件套", "下班后那两小时，怎么过？"),
]

if __name__ == "__main__":
    B.main()
