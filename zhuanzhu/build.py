"""《深度工作》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，慢速讲解节奏。

规划见 zhuanzhu/PLAN.md（每讲叙事形式、14 个场景大纲、书中出处）。

用法：
    python3 -m zhuanzhu.build 01 --sheet     # 逐镜联系表
    python3 -m zhuanzhu.build 01             # 渲染到 out/zhuanzhu/ep01/
    python3 -m zhuanzhu.build --verify       # 核验成片
    python3 -m zhuanzhu.build --publish      # 交付到 videos/zhuanzhu/（接频道片尾；每讲带横屏封面；另出合集图与系列横屏封面）
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)
core.RULES.update(wb.SLOW_RULES)        # 慢速讲解节奏：14 个场景，每个 3 小节（≈6.4 秒），画完停 4 拍（见 CLAUDE.md「白板手绘节奏」）
wb.HOLD_BEATS = 4

core.SERIES.update(name="深度工作", count="10讲", prefix="专注", tagline="消息叮个不停，怎么沉下心干活")
B.PKG = "zhuanzhu"
B.OUT = B.ROOT / "out" / "zhuanzhu"
B.MODS = {"01": "wb01_value", "02": "wb02_residue", "03": "wb03_busy", "04": "wb04_flow",
          "05": "wb05_style", "06": "wb06_ritual", "07": "wb07_shutdown", "08": "wb08_boredom",
          "09": "wb09_social", "10": "wb10_shallow"}

# 系列规划：(期号, 概念, 片名)；01–04 对应书中第一部分“理论”，05–10 对应第二部分四条“准则”
PLAN = [
    ("01", "专注值钱", "加班到十点，活怎么还没干完？"),
    ("02", "注意力残留", "回条消息，怎么半天回不了神？"),
    ("03", "看起来很忙", "忙了一整天，干成了啥？"),
    ("04", "沉进去才痛快", "刷了一晚手机，怎么更累了？"),
    ("05", "选对专注法", "没有整块时间，还能专注吗？"),
    ("06", "开工仪式", "一坐下就想摸手机，怎么办？"),
    ("07", "收工仪式", "下班了，脑子怎么还在上班？"),
    ("08", "受得了无聊", "排队两分钟，也要掏手机？"),
    ("09", "挑工具", "社交软件停三十天，会怎样？"),
    ("10", "少干浮活", "活一件没少，怎么准点下班？"),
]

if __name__ == "__main__":
    B.main()
