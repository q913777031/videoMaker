"""08 依恋：为什么有人一谈恋爱，就患得患失？"""

from adler import kit as K
from adler.core import Counter, Custom, Fig, Icon, Label, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#2F8F8A"
G = A.GROUND_Y
REFS = [BOOK, "Hazan & Shaver (1987). Romantic love conceptualized as an attachment process. JPSP."]


def build():
    shots = [
        hook("一 谈恋爱|就 【患得患失】？", 104),
        loop("可能和你小时候|怎么被爱有关", pose="sad", mood="worried", hair="long", color=A.HER),
        Shot(4, "他半天没回消息|你已经脑补了一出戏", "情境演绎", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="我（未读）", unread=False,
                   msgs=[(1, "在吗"), (4, "在忙吗？"), (7, "怎么不回？"), (10, "你是不是生气了")]),
        ], hits=[(1, "wood_high", 0.8, "消息"), (4, "wood_high", 0.8, "消息"), (7, "rim", 0.8, "消息"),
                 (10, "rim", 0.9, "消息")], note="自己连发消息"),
        drop("依恋", "Attachment", "早年被爱的方式|会影响你怎么【爱人】", 220),
        Shot(4, "安全型、回避型|和焦虑型", "原书 · 依恋类型", [
            Label("安全型", 540, 600, 50, at=0, fill=K.GREEN, sfx="wood_low"),
            Label("回避型：怕太亲密", 540, 760, 44, at=2, fill=K.INK2, sfx="wood_low"),
            Label("焦虑型：怕被抛弃", 540, 920, 44, at=4, fill=K.RED, sfx="rim"),
        ], note="三种依恋类型"),
        line("怕 被 抛弃|还是 怕 【太亲密】？", 100),
        Shot(4, "1987年一份报纸|刊登了“爱情测验”", "研究证据 · Hazan & Shaver 1987", [
            Counter(0, 620, 540, 660, 220, at=0, land=4, sub="份读者回答"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "约56%的人|属于安全型", "研究证据 · Hazan & Shaver 1987", [
            Counter(0, 56, 540, 680, 220, at=0, land=4, suffix="%", sub="安全型"),
        ], research=True, note="安全型占比"),
        Shot(4, "约25%回避型|约19%焦虑型", "研究证据 · Hazan & Shaver 1987", [
            Label("回避型 25%", 320, 760, 48, at=0, fill=K.INK2, sfx="wood_low"),
            Label("焦虑型 19%", 760, 760, 48, at=2, fill=K.RED, sfx="wood_low"),
        ], research=True, note="其余类型"),
        slam("安全感", "安全感|可以慢慢建立", size=150),
        doubt("依恋更像连续的维度|而且会随关系改变"),
        tip("试试：不安时直接说需要|别用试探", hair="long", color=A.HER),
        end_shot(REFS, "09 嫉妒：为什么他给别人点个赞，你就难受"),
    ]
    return episode(8, "attachment", "依恋", "为什么有人一谈恋爱，就患得患失？", ACC, shots, REFS,
                   "一谈恋爱|就【患得患失】？",
                   ["成人依恋为《亲密关系》第 1 章内容；书中采用“焦虑 × 回避”两个维度描述依恋。",
                    "Hazan & Shaver (1987)：报纸“爱情测验”前 620 份回答中，约 56% 安全型、25% 回避型、19% 焦虑矛盾型（比例据教材与综述转引）。",
                    "后续研究认为依恋是连续维度而非类型，并会随重要关系改变。"])
