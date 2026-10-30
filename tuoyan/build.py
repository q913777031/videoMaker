"""《拖延心理学》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，慢速讲解节奏
（14 个场景，小节 2 / 3×12 / 4，每屏 ≈6.4 秒，画完停 4 拍；第 4 个场景对上音乐 drop）。规划见 tuoyan/PLAN.md。

用法：
    python3 -m tuoyan.build 01 --sheet     # 逐镜联系表
    python3 -m tuoyan.build 01             # 渲染到 out/tuoyan/ep01/
    python3 -m tuoyan.build --verify       # 核验成片
    python3 -m tuoyan.build --publish      # 交付到 videos/tuoyan/（接频道片尾；每讲带横屏封面；另出合集图与系列横屏封面）
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)
core.RULES.update(wb.SLOW_RULES)        # 慢速讲解节奏：14 个场景，每个 3 小节（≈6.4 秒），画完停 4 拍（见 CLAUDE.md「白板手绘节奏」）
wb.HOLD_BEATS = 4

core.SERIES.update(name="拖延心理学", count="10讲", prefix="拖延", tagline="为什么总拖到最后一刻，拖的时候心里在怕什么")
B.PKG = "tuoyan"
B.OUT = B.ROOT / "out" / "tuoyan"
B.MODS = {"01": "wb01_cycle", "02": "wb02_failure", "03": "wb03_success", "04": "wb04_control",
          "05": "wb05_distance", "06": "wb06_time", "07": "wb07_brain", "08": "wb08_check",
          "09": "wb09_goal", "10": "wb10_less"}

# 系列规划：(期号, 概念, 片名)
PLAN = [
    ("01", "拖延的圈", "说好早点开始，又拖到半夜"),
    ("02", "怕做砸", "拖到最后，是给自己留台阶"),
    ("03", "怕做好", "做得太好，怕以后都得这么好"),
    ("04", "跟催的人较劲", "领导越催，我越不想动"),
    ("05", "怕靠近怕分开", "有人拖着等人帮，有人拖着躲人"),
    ("06", "两种时间", "明明还有三天，怎么一眨眼没了"),
    ("07", "大脑在躲", "一打开文档，脑子就想跑"),
    ("08", "拖延的心里话", "这几句心里话，你中了几句"),
    ("09", "能动手的目标", "目标定成这样，才动得起来"),
    ("10", "少拖一点", "拖延改不干净，那就少拖一点"),
]

if __name__ == "__main__":
    B.main()
