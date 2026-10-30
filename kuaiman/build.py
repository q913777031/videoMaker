"""《思考，快与慢》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，慢速讲解节奏（14 个场景，画完停住）。

规划见 kuaiman/PLAN.md（每讲的叙事形式、14 个场景大纲、书中出处）。

用法：
    python3 -m kuaiman.build 01 --sheet     # 逐镜联系表
    python3 -m kuaiman.build 01             # 渲染到 out/kuaiman/ep01/
    python3 -m kuaiman.build --verify       # 核验成片
    python3 -m kuaiman.build --publish      # 交付到 videos/kuaiman/（接频道片尾；每讲带横屏封面；另出合集图与系列横屏封面）
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)
core.RULES.update(wb.SLOW_RULES)        # 慢速讲解节奏：14 个场景，每个 3 小节（≈6.4 秒），画完停 4 拍（见 CLAUDE.md「白板手绘节奏」）
wb.HOLD_BEATS = 4

core.SERIES.update(name="思考，快与慢", count="10讲", prefix="快与慢", tagline="脑子里一快一慢两个小人，谁在替你拿主意")
B.PKG = "kuaiman"
B.OUT = B.ROOT / "out" / "kuaiman"
B.MODS = {"01": "wb01_bat", "02": "wb02_halo", "03": "wb03_anchor", "04": "wb04_avail",
          "05": "wb05_linda", "06": "wb06_regress", "07": "wb07_plan", "08": "wb08_loss",
          "09": "wb09_frame", "10": "wb10_peak"}

# 系列规划：(期号, 概念, 片名)；每讲叙事形式不同，见 PLAN.md
PLAN = [
    ("01", "快与慢", "球拍和球，你算对了吗？"),
    ("02", "光环效应", "先听到的那句，为什么最管用？"),
    ("03", "锚定效应", "先报的数字，为什么能带偏你？"),
    ("04", "可得性", "组里每个人，都觉得自己干得最多？"),
    ("05", "琳达问题", "细节越多，为什么越容易信错？"),
    ("06", "回归平均", "被骂完就变好，真是骂的功劳？"),
    ("07", "规划谬误", "排期两周，为什么总拖成一个月？"),
    ("08", "损失厌恶", "赢150输100，你敢赌吗？"),
    ("09", "框架效应", "同一件事，换个说法就变了？"),
    ("10", "峰终定律", "一段经历，只记住最高点和结尾？"),
]

if __name__ == "__main__":
    B.main()
