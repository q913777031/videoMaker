"""05 四骑士：为什么一吵架就越说越僵？"""

from adler import kit as K
from adler.core import Bubble, Card, Custom, Fig, Icon, Label, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#8E5BA8"
G = A.GROUND_Y
REFS = [BOOK, "Gottman (1994). What Predicts Divorce?"]


def build():
    shots = [
        hook("一 吵架|就 越说 越 【僵】？", 110),
        loop("伤人的不是吵架|是吵架的方式"),
        Shot(4, "“你总是这样！”|“我哪有！”", "情境演绎", [
            Fig(340, G, 310, at=0, pose="point", mood="angry", hair="long", color=A.HER),
            Fig(740, G, 310, at=0, pose="block", mood="angry", hair="short", face=-1),
            Bubble("你总是这样！", 340, 540, 44, at=2, sfx="rim"),
            Bubble("我哪有！", 760, 540, 44, at=4, sfx="rim"),
        ], draw=A.ground, shake=[(4, 8.0)], note="争吵"),
        drop("四骑士", "Four Horsemen", "有四种说话方式|最伤【关系】", 220),
        Shot(4, "批评、蔑视、防御、冷战", "原书 · 戈特曼的研究", [
            Label("批评", 270, 660, 48, at=0, fill=K.RED, sfx="wood_low"),
            Label("蔑视", 810, 660, 48, at=2, fill=K.RED, sfx="wood_low"),
            Label("防御", 270, 900, 48, at=4, fill=K.INK2, sfx="wood_low"),
            Label("冷战", 810, 900, 48, at=6, fill=K.INK2, sfx="rim"),
        ], note="四骑士逐个弹出"),
        line("翻 白眼 的 那一下|最 【伤人】", 100),
        Shot(4, "戈特曼长期观察|大量夫妻的争吵", "研究证据 · Gottman", [
            Fig(340, G, 300, at=0, mood="flat", hair="long", color=A.HER),
            Fig(740, G, 300, at=0, mood="flat", hair="short", face=-1),
            Icon("eye", 540, 520, 130, color=ACC, at=2, sfx="ding"),
        ], draw=A.ground, research=True, flashes=[2], note="二次钩子：观察"),
        Shot(4, "其中“蔑视”|被认为最伤关系", "研究证据 · Gottman", [
            Card("蔑视", 540, 720, 100, at=0, fill=K.RED, color=K.PAPER, sfx="kick"),
            Spark(540, 720, at=0, colors=[K.RED, K.INK2]),
        ], research=True, shake=[0], note="蔑视"),
        Shot(4, "更好的说法：当你…|我感到…，我希望…", "原书 · 方法", [
            Card("当你|我感到|我希望", 540, 760, 56, at=0, fill=K.PAPER, sfx="ding"),
            Spark(540, 760, at=0),
        ], note="说事实、说感受、说需要"),
        slam("好好说", "吵架不可怕|可怕的是伤人"),
        doubt("“90%预测离婚”的说法|被批评难以复现"),
        tip("试试：用“我感到”|代替“你总是”", hair="long", color=A.HER),
        end_shot(REFS, "06 投资模型：为什么明明不满意，却还不分手"),
    ]
    return episode(5, "horsemen", "四骑士", "为什么一吵架，就越说越僵？", ACC, shots, REFS,
                   "一吵架|就越说越【僵】？",
                   ["戈特曼的“四骑士”（批评、蔑视、防御、冷战）与“当你…我感到…”式表达为《亲密关系》第 5、11 章内容。",
                    "戈特曼关于“高准确率预测离婚”的结论被批评为事后拟合、样本较小，具体数字难以复现；但这些行为与关系恶化相关的方向较稳健。"])
