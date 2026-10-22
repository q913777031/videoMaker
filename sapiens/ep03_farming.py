"""03 农业革命：为什么越努力，日子反而越累？（重做版）"""

from adler import kit as K
from adler.core import Counter, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop2, redo, slam2, tip2

ACC = "#7F8A2E"
G = A.GROUND_Y
REFS = [BOOK, "Cohen & Armelagos (1984). Paleopathology at the Origins of Agriculture."]
LEFT = ("采集者", "打猎摘果", K.OTHER3)
RIGHT = ("早期农民", "天天种地", ACC)


def build():
    shots = [
        ask("一万多年前|谁 过得 【更健康】？", [
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=3, left=LEFT, right=RIGHT),
        ], hits=[(3, "wood_low", 0.8, "选项A"), (4, "wood_low", 0.8, "选项B")], note="互动：二选一"),
        Shot(4, "倒计时3秒|选一个", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=-9, pick=8, pick_side=0, left=LEFT, right=RIGHT),
            Label("答案：采集者", 540, 1260, 48, at=8, fill=K.GREEN, sfx="ding"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到")],
            flashes=[6], shake=[(6, 12.0)], punch=0.025, note="倒计时，揭晓采集者更健康"),
        Shot(2, "种地更辛苦|身体反而更差", "互动小游戏", [
            Pops("越 努力|越 【累】", 540, 760, 130, at=0, step=1),
            Spark(540, 760, at=4, sfx="rim"),
        ], text_beat=0, note="揭晓"),
        drop2("农业革命", "Agricultural Revolution", "书里说：这是史上|最大的【骗局】", "种地 定居 人口", size=170),
        Shot(4, "不是人驯化了小麦|是小麦驯化了人", "原书 · 大意", [
            Custom(A.field, x=540, y=G - 40, at=0, enter="none", n=9, s=230, grow=1.4),
            Fig(540, G + 10, 300, at=4, pose="crouch", mood="worried", hair="short", sfx="wood_low"),
            Label("弯腰 · 除草 · 挑水", 540, 560, 44, at=9, fill=ACC, sfx="wood_high"),
            Spark(540, 560, at=13),
        ], hits=[(0, "wood_low", 0.6, "麦田长出")], note="麦田里弯腰的人"),
        Shot(4, "加班换来了大房子|也换来了更多房贷", "情境演绎", [
            Fig(300, G, 320, at=0, pose="carry", mood="worried", hair="short"),
            Icon("house", 740, 640, 220, color=ACC, at=2, sfx="wood_low"),
            Custom(A.bill, x=760, y=960, at=6, enter="drop", rot=4, title="房贷", amount="30年", sfx="rim"),
            Label("越努力，越离不开", 540, 480, 44, at=11, fill=K.RED, sfx="rim"),
        ], draw=A.ground, note="现代版的小麦陷阱"),
        Shot(4, "考古发现：早期农民|个子变矮、病更多", "研究证据 · Cohen & Armelagos 1984", [
            Fig(360, G, 340, at=0, mood="calm", hair="short", color=K.OTHER3),
            Fig(720, G, 280, at=3, pose="sad", mood="sad", hair="short", color=ACC, sfx="rim"),
            Icon("cross", 720, 640, 90, color=K.RED, at=6, sfx="rim"),
            Label("矮了一截", 720, 500, 42, at=10, fill=K.RED, sfx="wood_high"),
        ], draw=A.ground, research=True, punch=0.02, flashes=[3], note="二次钩子：采集者与农民"),
        Shot(4, "21个转向农业的社会里|19个健康变差", "研究证据 · Cohen & Armelagos 1984", [
            Counter(0, 19, 540, 640, 220, at=0, land=4, suffix="/21", sub="个社会健康下降"),
            Icon("heart", 540, 960, 130, color=K.RED, at=7, sfx="rim"),
            Icon("cross", 640, 900, 80, color=K.RED, at=10, sfx="rim"),
        ], research=True, note="数字落定"),
        Shot(4, "可人口暴涨了：|物种赢了，个人更累了", "原书 · 大意", [
            Custom(A.crowd, x=540, y=G, at=0, enter="fade", n=14, s=150, spread=880, rows=3),
            Icon("sprout", 540, 520, 120, color=K.GREEN, at=3, sfx="wood_high"),
            Label("人更多了", 300, 640, 42, at=7, fill=K.GREEN, sfx="ding"),
            Label("人更累了", 780, 640, 42, at=11, fill=K.RED, sfx="rim"),
        ], draw=A.ground, note="人口变多"),
        slam2("回不去", "人口 靠 农田|【回不去】", "每一步都合理|合起来却是陷阱"),
        Shot(4, "第一招：每次加码前|先算清换来了什么", "小方法", [
            Custom(A.checklist, x=540, y=800, at=0, enter="pop", b0=2, step=3, title="这次加班换来…",
                   items=[("多一点钱", True), ("更多时间", False), ("更好身体", False), ("陪家人", False)]),
        ], hits=[(2, "wood_high", 0.8, "✓"), (5, "rim", 0.8, "✗"), (8, "rim", 0.8, "✗"), (11, "rim", 0.9, "✗")],
            note="加班账本"),
        tip2("第二招：多赚之前|先问值不值", "先 问 【值不值】", 120),
        end_shot(REFS, "04 奢侈品陷阱：为什么涨了工资，还是不够花"),
    ]
    return redo(3, "farming", "农业革命", "为什么越努力，日子反而越累？", ACC, shots, REFS,
                "为什么越努力|日子反而越【累】？",
                ["“农业革命是史上最大骗局”“小麦驯化了人”为《人类简史》第 5 章观点；二选一小游戏、房贷为情境演绎。",
                 "Cohen & Armelagos (1984) 汇总的研究中，21 个经历农业转型的社会有 19 个健康与营养状况下降。"])
