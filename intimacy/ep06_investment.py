"""06 投资模型：为什么明明不满意，却还不分手？"""

from adler import kit as K
from adler.core import Bubble, Card, Counter, Fig, Icon, Label, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#3A6EA5"
G = A.GROUND_Y
REFS = [BOOK, "Le & Agnew (2003). Commitment and its theorized determinants: A meta-analysis. Pers Relat."]


def build():
    shots = [
        hook("明明 不满意|为什么 还 【不分手】？", 100),
        loop("满意度|只是答案的三分之一", pose="think", mood="worried", hair="long", color=A.HER),
        Shot(4, "在一起五年|吵了无数次，还是没走", "情境演绎", [
            Fig(380, G, 320, at=0, pose="sit_sad", mood="worried", hair="long", color=A.HER),
            Bubble("要不要分…", 400, 560, 44, at=2, think=True, sfx="wood_low"),
            Card("在一起|5 年", 780, 720, 56, at=4, rot=3, sfx="rim"),
        ], draw=A.ground, note="犹豫要不要分手"),
        drop("投资模型", "Investment Model", "决定你留不留的|不只是【满意】", 180),
        Shot(4, "满意度、替代选择|和已经投入的东西", "原书 · 鲁斯布特的投资模型", [
            Icon("heart", 260, 700, 150, color=K.RED, at=0, sfx="wood_low"),
            Label("满意度", 260, 860, 40, at=0, fill=K.RED),
            Icon("friends", 540, 700, 150, color=K.INK2, at=2, sfx="wood_low"),
            Label("替代选择", 540, 860, 40, at=2, fill=K.INK2),
            Icon("clock", 820, 700, 150, color=ACC, at=4, sfx="wood_low"),
            Label("已投入", 820, 860, 40, at=4, fill=ACC),
        ], note="三个因素"),
        line("投入 越多|越 【舍不得】 走", 104),
        Shot(4, "一项元分析汇总|52项研究、约1.1万人", "研究证据 · Le & Agnew 2003", [
            Counter(0, 52, 540, 660, 220, at=0, land=4, sub="项研究 · 约 11000 人"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "满意、替代选择、投入|都和“承诺”紧密相关", "研究证据 · Le & Agnew 2003", [
            Icon("scale", 540, 720, 230, color=ACC, at=0, sfx="wood_low"),
            Spark(540, 720, at=2, sfx="ding"),
        ], research=True, note="三者与承诺相关"),
        Shot(4, "所以条件再好的人|有更好的替代也会走", "原书 · 大意", [
            Fig(360, G, 300, at=0, mood="calm", hair="short"),
            Fig(760, G, 300, at=2, mood="smile", hair="bun", color=K.OTHER2, face=-1, sfx="wood_high"),
            Icon("question", 560, 520, 110, color=K.RED, at=4, sfx="rim"),
        ], draw=A.ground, note="替代选择"),
        slam("承诺", "留下来的理由|不只有爱"),
        doubt("留下不一定是爱|也可能只是沉没成本", tag="边界"),
        tip("试试：问问自己|是满意，还是舍不得？", hair="long", color=A.HER),
        end_shot(REFS, "07 激情之爱：热恋期一过，就没感觉了吗"),
    ]
    return episode(6, "investment", "投资模型", "为什么明明不满意，却还不分手？", ACC, shots, REFS,
                   "明明不满意|为什么还【不分手】？",
                   ["社会交换理论（比较水平、替代比较水平）与鲁斯布特投资模型为《亲密关系》第 6 章内容。",
                    "Le & Agnew (2003)：52 项研究、约 1.1 万人，满意度、替代选择质量与投入量均与承诺显著相关。"])
