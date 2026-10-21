"""03 相似性：互补的人，真的更合适吗？"""

from adler import kit as K
from adler.core import Bubble, Counter, Fig, Icon, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#5865B8"
G = A.GROUND_Y
REFS = [BOOK, "Montoya, Horton & Kirchner (2008). Is actual similarity necessary for attraction? JSPR."]


def build():
    shots = [
        hook("互补 的 人|真的 【更合适】 吗？", 100),
        loop("研究给的答案|恰恰相反"),
        Shot(4, "都爱宅家、都爱火锅|一聊就停不下来", "情境演绎", [
            Fig(340, G, 310, at=0, mood="happy", hair="short"),
            Fig(740, G, 300, at=0, mood="happy", hair="long", color=A.HER, face=-1),
            Bubble("我也是！", 340, 560, 44, at=2, sfx="wood_high"),
            Bubble("真的假的！", 740, 560, 44, at=4, sfx="wood_high"),
            Icon("heart", 540, 460, 100, color=K.RED, at=6, sfx="ding"),
        ], draw=A.ground, note="两人聊得投机"),
        drop("相似性", "Similarity", "我们更容易喜欢|和自己【相似】的人", 200),
        Shot(4, "价值观、爱好、背景|越像越省力", "原书 · 大意", [
            Icon("heart", 270, 760, 160, color=K.RED, at=0, sfx="wood_low"),
            Icon("book", 540, 760, 160, color=ACC, at=2, sfx="wood_low"),
            Icon("house", 810, 760, 160, color=K.INK2, at=4, sfx="wood_low"),
        ], note="价值观、爱好、背景"),
        line("像 我 的 人|让 我 觉得 【被理解】", 96),
        Shot(4, "一项元分析汇总了|313项研究", "研究证据 · Montoya 等 2008", [
            Counter(0, 313, 540, 660, 220, at=0, land=4, sub="项研究"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子"),
        Shot(4, "真实的相似和“觉得像”|都和吸引力明显相关", "研究证据 · Montoya 等 2008", [
            Icon("check", 400, 760, 160, color=K.GREEN, at=0, sfx="rim"),
            Icon("check", 680, 760, 160, color=K.GREEN, at=2, sfx="rim"),
            Spark(540, 760, at=2),
        ], research=True, note="两者都相关"),
        Shot(4, "在已经开始的关系里|“觉得像”可能更重要", "研究证据", [
            Fig(400, G, 300, at=0, pose="hug", mood="happy", hair="short"),
            Fig(660, G, 290, at=0, pose="hug", mood="happy", hair="long", color=A.HER, face=-1),
            Icon("heart", 530, 560, 110, color=K.RED, at=2, sfx="ding"),
        ], draw=A.ground, research=True, note="情侣"),
        slam("合拍", "越像|越合拍"),
        doubt("相似不等于幸福|差异处理得好也能长久", tag="边界"),
        tip("试试：和对方|找出三个共同点"),
        end_shot(REFS, "04 归因：他迟到一次，你就觉得他不在乎你"),
    ]
    return episode(3, "similarity", "相似性", "互补的人，真的更合适吗？", ACC, shots, REFS,
                   "互补的人|真的【更合适】吗？",
                   ["相似性原则为《亲密关系》第 3 章内容；“互补更吸引”的说法缺乏有力证据。",
                    "Montoya 等 (2008)：313 项研究、460 个效应量，真实相似与感知相似都与吸引显著相关；后续研究认为在持续关系中感知相似更重要。"])
