"""《金钱心理学》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，慢速讲解节奏（14 个场景，画完停住）。

规划见 jinqian/PLAN.md（每讲的叙事形式、14 个场景大纲、书中观点出处）。

用法：
    python3 -m jinqian.build 01 --sheet     # 逐镜联系表
    python3 -m jinqian.build 01             # 渲染到 out/jinqian/ep01/
    python3 -m jinqian.build --verify       # 核验成片
    python3 -m jinqian.build --publish      # 交付到 videos/jinqian/（接频道片尾；每讲带横屏封面；另出合集图与系列横屏封面）
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)
core.RULES.update(wb.SLOW_RULES)        # 慢速讲解节奏：14 个场景，每个 3 小节（≈6.4 秒），画完停 4 拍（见 CLAUDE.md「白板手绘节奏」）
wb.HOLD_BEATS = 4

core.SERIES.update(name="金钱心理学", count="10讲", prefix="金钱", tagline="攒钱、花钱、守住钱，难在人心")
B.PKG = "jinqian"
B.OUT = B.ROOT / "out" / "jinqian"
B.MODS = {"01": "wb01_story", "02": "wb02_luck", "03": "wb03_enough", "04": "wb04_compound",
          "05": "wb05_keep", "06": "wb06_freedom", "07": "wb07_car", "08": "wb08_save",
          "09": "wb09_margin", "10": "wb10_sleep"}

# 系列规划：(期号, 概念, 片名)
PLAN = [
    ("01", "经历定金钱观", "爸妈抠门我乱花，谁疯了？"),
    ("02", "运气与风险", "一样努力，结果怎么差这么多？"),
    ("03", "知道够了", "工资涨了，为什么还是不够花？"),
    ("04", "复利靠时间", "攒钱这件事，为什么拼的是时间？"),
    ("05", "致富与守富", "赚到了大钱，为什么又亏光了？"),
    ("06", "钱买自由", "钱最大的用处，是买回时间"),
    ("07", "豪车悖论", "开豪车的人，你记住他了吗？"),
    ("08", "存钱", "没想好买什么，也要存钱？"),
    ("09", "留出余地", "计划总被打乱，钱怎么留余地？"),
    ("10", "睡得着就好", "管钱的办法，睡得着就够了"),
]

if __name__ == "__main__":
    B.main()
