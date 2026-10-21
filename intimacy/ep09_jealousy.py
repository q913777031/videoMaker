"""09 嫉妒：为什么他给别人点个赞，你就难受？"""

from adler import kit as K
from adler.core import Card, Counter, Custom, Fig, Icon, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#9C5B3A"
G = A.GROUND_Y
REFS = [BOOK, "Muise, Christofides & Desmarais (2009). More information than you ever wanted. CyberPsychol Behav."]


def build():
    shots = [
        hook("他 给别人 点个赞|你 就 【难受】？", 100),
        loop("不是你小气|是嫉妒在“报警”", hair="long", color=A.HER),
        Shot(4, "深夜刷到|他给前任点了个赞", "情境演绎", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="朋友圈",
                   msgs=[(1, "他赞了她的照片"), (4, "他评论：好看"), (7, "她回复：谢谢~"), (10, "共同好友 3 人")]),
        ], hits=[(1, "rim", 0.8, "点赞"), (4, "wood_high", 0.8, "评论"), (7, "wood_high", 0.8, "回复"), (10, "rim", 0.9, "共同好友")],
            note="朋友圈动态弹出"),
        drop("嫉妒", "Jealousy", "害怕失去一段关系|带来的【不安】", 220),
        Shot(4, "对真实威胁的反应|和凭空的怀疑", "原书 · 大意", [
            Card("反应性嫉妒|（有事实）", 300, 760, 46, at=0, rot=-3, fill=K.INK2, color=K.PAPER, sfx="wood_low"),
            Card("怀疑性嫉妒|（凭猜测）", 780, 760, 46, at=3, rot=3, fill=K.RED, color=K.PAPER, sfx="rim"),
        ], note="两种嫉妒"),
        line("越 刷|越 【酸】", 120),
        Shot(4, "研究调查了308名|使用社交网络的大学生", "研究证据 · Muise 等 2009", [
            Counter(0, 308, 540, 660, 220, at=0, land=4, sub="名大学生"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "在社交网络上花的时间越长|嫉妒越强", "研究证据 · Muise 等 2009", [
            Icon("phone", 420, 740, 180, color=K.INK2, at=0, sfx="wood_low"),
            Icon("heart", 700, 740, 160, color=K.RED, at=2, sfx="rim"),
            Icon("cross", 700, 740, 90, color=K.INK, at=3, sfx="rim"),
        ], research=True, note="刷得多更嫉妒"),
        Shot(4, "嫉妒→去查看→看到更多|→更嫉妒", "研究证据 · Muise 等 2009", [
            Custom(A.cycle, x=540, y=780, at=0, enter="none", labels=["嫉妒", "去查看", "看到更多"], R=260, b0=0, step=2,
                   hi=0, spin_at=7),
        ], hits=[(0, "wood_low", 0.8, "嫉妒"), (2, "wood_low", 0.8, "去查看"), (4, "rim", 0.9, "看到更多"),
                 (7, "ding", 0.8, "循环")], research=True, note="嫉妒循环"),
        slam("循环", "越查|越不安"),
        doubt("这是相关研究|后续研究效应通常很小"),
        tip("试试：少刷动态|有疑问直接问他", hair="long", color=A.HER),
        end_shot(REFS, "10 积极回应：对方报喜时，你只回了句“哦”"),
    ]
    return episode(9, "jealousy", "嫉妒", "为什么他给别人点个赞，你就难受？", ACC, shots, REFS,
                   "他给别人点个赞|你就【难受】？",
                   ["反应性嫉妒与怀疑性嫉妒为《亲密关系》第 10 章内容。",
                    "Muise 等 (2009)：308 名大学生，使用 Facebook 时间与嫉妒显著相关，作者提出“嫉妒—查看—更多信息”的反馈循环；后续研究效应通常较小、结论不一。"])
