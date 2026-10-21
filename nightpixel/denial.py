"""《我们为什么假装不会死》（夜色像素风，依据欧内斯特·贝克尔《拒斥死亡》）：时间表与混音。

用法：
    python3 -m nightpixel.denial --plan <episode目录>                     # 写 timeline.json
    python3 -m nightpixel.denial --mix <无声成片.mp4> <输出目录> <episode目录>  # 混音 + 封装 + 卡点表 + 核验
"""

import sys
from pathlib import Path

from .kit import BT, Plan, bidx, finish

END = 89.0
NAME = "我们为什么假装不会死"


def plan() -> Plan:
    p = Plan(END)
    c = p.cue
    # 1 开场聊天窗「深夜树洞」
    c("s1", 0.0)
    c("chat_b1", 1.18, "wood_high", 0.9, "气泡：如果明天是最后一天")
    c("cap1", 1.7)
    c("chat_b2", 3.85, "wood_high", 0.8, "气泡：去见想见的人")
    c("chat_b3", 5.98, "wood_high", 0.8, "气泡：没敢想过")
    c("typing", 6.9)
    # 2 书的主张
    c("s2", 8.63, "tom", 0.6, "信笺糊化进入")
    c("card1_write", 9.2)
    c("cap2", 12.9)
    # 3 drop：办法一，不去想
    c("s3", 17.14, "kick", 1.0, "音乐 drop：硬切到雪夜街景")
    c("cap3b", 21.4)
    # 4 心里话：红笔批改
    c("s4", 23.7, "wood_low", 0.8, "信笺糊化进入")
    c("card2_write", 24.3)
    c("card2_mark", 26.4, "rim", 0.8, "红圈：怕死")
    c("card2_note", 27.4, "wood_low", 0.7, "红字批注")
    c("card2_strike", 27.9, "rim", 0.7, "划掉")
    c("card2_redo", 28.95)
    c("card2_stamp", 30.55, "clap", 0.9, "通过章：说了实话")
    c("cap4", 31.0)
    # 5 办法二：不朽方案，6 刀加速硬切，止于高潮前 2 拍
    hit = bidx(42.64)
    p.relay_cuts(BT[hit - 2], [4, 4, 3, 3, 2, 2], "不朽方案硬切")
    p.cues["s5"] = p.relay[0]["at"]
    # 6 高潮：雪落在句号上，「终点。」变「终点？」
    c("s6", BT[hit - 2])
    c("swap", BT[hit], "kick", 1.0, "高潮：雪落改标点")
    c("swap_cym", BT[hit], "cymbal", 0.8, "高潮吊镲")
    c("cap6", 44.3)
    # 7 文化是一项不朽工程
    c("s7", 47.5, "tom", 0.5, "街景远景")
    # 8 恐惧管理理论
    c("s8", 51.15, "tom", 0.7, "房间：恐惧管理理论")
    c("cap8", 52.0)
    # 9 实验与重复实验
    c("s9", 59.6, "wood_low", 0.8, "实验卡 1")
    c("cap9", 60.6)
    c("s9b", 63.8, "wood_low", 0.7, "实验卡 2")
    c("s9c", 68.1, "wood_low", 0.7, "重复实验卡")
    c("s9c_stamp", 70.3, "rim", 0.8, "存疑章")
    # 10 收尾聊天窗
    c("s10", 72.41, "tom", 0.6, "收尾聊天窗")
    c("end_b1", 73.5, "wood_high", 0.8, "气泡：那该怎么办")
    c("end_b2", 76.2, "wood_high", 0.8, "气泡：不用假装不怕")
    c("end_b3", 78.9, "wood_high", 0.9, "气泡：把怕变成好好活的理由")
    c("cap10", 80.9)
    # 11 片尾题字
    c("s11", 85.15, "cymbal", 0.5, "片尾题字")
    return p


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--plan":
        plan().dump(Path(a[1]))
    elif a and a[0] == "--mix":
        finish(Path(a[1]), Path(a[2]), Path(a[3]), NAME)
    else:
        print(__doc__)
