"""控糖革命 12 讲：系列常量与片尾。"""

from adler import kit as K
from adler.core import end_shot

GROUND = 1130
SERIES = dict(series="控糖革命", series_count=12, file_prefix="控糖")
BOOK = "杰西·安佐斯佩《控糖革命》（Glucose Revolution，2022；张艳娟译，浙江科学技术出版社 2024）"
DISCLAIMER = "本片为科普，不构成医疗建议；糖尿病患者调整饮食与用药请遵医嘱"
TITLES = {
    1: "血糖曲线，是什么样的？", 2: "血糖尖峰，真的那么可怕吗？", 3: "同一顿饭，换个顺序吃？",
    4: "饭前先吃一盘菜，有什么用？", 5: "热量一样，效果也一样吗？", 6: "早餐，为什么别吃太甜？",
    7: "蜂蜜，比白糖更健康吗？", 8: "想吃甜的，什么时候吃？", 9: "饭前一勺醋，有用吗？",
    10: "吃完饭，要不要走走？", 11: "饿了，零食怎么选？", 12: "吃碳水，怎么吃更稳？",
}


def ground(g):
    K.ground(g.c, GROUND)


def refs(*items) -> list:
    """参考资料：本期出处 + 原书 + 免责提示（片尾卡与文档共用）。"""
    return list(items) + [BOOK, DISCLAIMER]


def ending(no: int, items: list):
    nxt = TITLES.get(no + 1)
    return end_shot(items, nxt and f"{no + 1:02d} {nxt}")
