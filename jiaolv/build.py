"""《身份的焦虑》系列：白板手绘形式（whiteboard/engine.py），沿用阿德勒引擎时间轴与交付流程，快节奏规则（每镜 ≤3 秒）。

用法：
    python3 -m jiaolv.build 01 --sheet     # 逐镜联系表
    python3 -m jiaolv.build 01             # 渲染到 out/jiaolv/ep01/
    python3 -m jiaolv.build --verify       # 核验成片
    python3 -m jiaolv.build --publish      # 交付到 videos/jiaolv/（接频道片尾；每讲带横屏封面；另出合集图与系列横屏封面）
"""

from adler import build as B
from adler import core
from whiteboard import engine as wb

wb.install(B)

core.SERIES.update(name="身份的焦虑", count="10讲", prefix="身份的焦虑", tagline="怕落后、怕被看低，从哪来，怎么办")
B.PKG = "jiaolv"
B.OUT = B.ROOT / "out" / "jiaolv"
B.MODS = {"01": "wb01_love", "02": "wb02_snob", "03": "wb03_expect", "04": "wb04_merit",
          "05": "wb05_depend", "06": "wb06_philo", "07": "wb07_art", "08": "wb08_politics",
          "09": "wb09_scale", "10": "wb10_bohemia"}

# 系列规划：(期号, 概念, 片名)；前五讲对应书中“焦虑起因”五章，后五讲对应“解决方法”五章
PLAN = [
    ("01", "爱的渴求", "为什么那么在意别人怎么看你？"),
    ("02", "势利", "一换工作，亲戚的脸色怎么就变了？"),
    ("03", "过度期望", "工资比爸妈高，为什么还觉得穷？"),
    ("04", "精英崇拜", "混得不好，就怪自己不够努力？"),
    ("05", "制约因素", "工作干得好好的，为什么还怕被裁？"),
    ("06", "哲学", "别人一句话，为什么能堵你一整天？"),
    ("07", "艺术", "为什么看部电影，心里就松了？"),
    ("08", "政治", "什么样才算混得好，谁说了算？"),
    ("09", "换个尺度", "为什么去趟山里，烦心事就小了？"),
    ("10", "波希米亚", "不想卷了，能换个活法吗？"),
]

if __name__ == "__main__":
    B.main()
