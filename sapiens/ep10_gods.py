"""10 从动物到上帝：人类越来越强，为什么越来越焦虑？"""

from adler import kit as K
from adler.core import Card, Custom, Fig, Icon, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#8E5BA8"
G = A.GROUND_Y
REFS = [BOOK, "Hallpike, C. R. (2017). Review of Sapiens.（批评性书评）"]


def build():
    shots = [
        hook("人类 越来越 强|为什么 越来越 【焦虑】？", 92),
        loop("这本书的最后|留下了一个问题", icon="bulb", pose="think", mood="open"),
        Shot(4, "外卖、导航、AI|我们几乎无所不能", "情境演绎", [
            Fig(260, G, 300, at=0, pose="point", mood="smile", hair="short"),
            Icon("phone", 600, 620, 150, color=ACC, at=1, sfx="wood_high"),
            Icon("target", 880, 560, 130, color=K.RED, at=3, sfx="wood_high"),
            Custom(A.laptop, x=640, y=930, at=5, enter="pop", w=380, p0=0.4, p1=1.0, b0=5, b1=12, title="AI 助手", sfx="wood_low"),
        ], draw=A.ground, note="手机、导航、AI"),
        drop("从动物到上帝", "From Animals into Gods", "智人正变成|【神】一样的物种", 130),
        Shot(4, "七万年、一万多年、五百年|三场革命走到今天", "原书 · 全书回顾", [
            Custom(A.timeline, x=540, y=760, at=0, enter="none", b0=0, step=3, w=720,
                   points=[("7万年前", "认知革命"), ("1.2万年前", "农业革命"), ("500年前", "科学革命")]),
        ], hits=[(0, "wood_low", 0.8, "认知革命"), (3, "wood_low", 0.8, "农业革命"), (6, "ding", 0.9, "科学革命")],
            note="三场革命时间轴"),
        line("能力 越来越 大|却 不知道 【想要什么】", 92),
        Shot(4, "书的结尾问：有什么比|不知足的神更危险？", "原书 · 结尾", [
            Card("不知足|也不知道想要什么", 540, 720, 56, at=0, sfx="ding"),
            Spark(540, 720, at=0),
        ], research=True, flashes=[0], note="二次钩子：结尾之问"),
        Shot(4, "我们能改造世界|却说不清自己想要什么", "原书 · 大意", [
            Fig(540, G, 330, at=0, pose="shrug", mood="worried", hair="short"),
            Icon("question", 540, 500, 120, color=K.RED, at=2, sfx="rim"),
        ], draw=A.ground, research=True, note="主角困惑"),
        Shot(4, "", "十讲回顾", [
            Pops("故事 八卦 农业 奢侈|秩序 金钱 信用 无知|幸福 【未来】", 540, 780, 72, at=0, step=1, gap=18),
        ], research=True, punch=0.02, note="十讲关键词逐个弹出"),
        slam("想要什么", "最难的问题|是我们想要什么", size=130),
        doubt("《人类简史》被学者批评|部分说法过于简化"),
        tip("十讲走完|问问自己：我想要什么？"),
        end_shot(REFS, None),
    ]
    return episode(10, "gods", "从动物到上帝", "人类越来越强，为什么越来越焦虑？", ACC, shots, REFS,
                   "人类越来越强|为什么越来越【焦虑】？",
                   ["三场革命（约 7 万年前认知革命、约 1.2 万年前农业革命、约 500 年前科学革命）与结尾之问出自《人类简史》。",
                    "人类学家 Hallpike (2017) 等批评该书部分说法缺乏证据或过于简化。"])
