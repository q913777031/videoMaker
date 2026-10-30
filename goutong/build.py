"""《非暴力沟通》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，慢速讲解节奏
（每讲 14 个场景：2 / 3×12 / 4 小节，每屏 ≈6.4 秒，画完停 4 拍）。选题与每讲分镜大纲见 goutong/PLAN.md。

用法：
    python3 -m goutong.build 01 --sheet     # 逐镜联系表
    python3 -m goutong.build 01             # 渲染到 out/goutong/ep01/
    python3 -m goutong.build --verify       # 核验成片
    python3 -m goutong.build --publish      # 交付到 videos/goutong/（接频道片尾；每讲带横屏封面；另出合集图与系列横屏封面）
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)
core.RULES.update(wb.SLOW_RULES)        # 慢速讲解节奏：14 个场景，每个 3 小节（≈6.4 秒），画完停 4 拍（见 CLAUDE.md「白板手绘节奏」）
wb.HOLD_BEATS = 4

core.SERIES.update(name="非暴力沟通", count="10讲", prefix="沟通", tagline="一句话，换个说法")
B.PKG = "goutong"
B.OUT = B.ROOT / "out" / "goutong"
B.MODS = {"01": "wb01_words", "02": "wb02_observe", "03": "wb03_feel", "04": "wb04_choice",
          "05": "wb05_needs", "06": "wb06_ask", "07": "wb07_listen", "08": "wb08_self",
          "09": "wb09_anger", "10": "wb10_thanks"}

# 系列规划：(期号, 概念, 片名)
PLAN = [
    ("01", "扎人的话", "没骂人，话怎么也扎心？"),
    ("02", "观察和评论", "“你总迟到”，为啥一说就炸？"),
    ("03", "说出感受", "“我觉得你不在乎”，算感受吗？"),
    ("04", "四种接法", "挨了句批评，你会怎么接？"),
    ("05", "听出需要", "“你又加班”，到底想说啥？"),
    ("06", "提请求", "说了“别总加班”，他报了球赛"),
    ("07", "倾听", "朋友吐槽，你接的哪句？"),
    ("08", "爱自己", "搞砸一件事，骂自己有用吗？"),
    ("09", "表达愤怒", "气到想摔门，先做哪一步？"),
    ("10", "表达感激", "夸人一句“真棒”，够了吗？"),
]

if __name__ == "__main__":
    B.main()
