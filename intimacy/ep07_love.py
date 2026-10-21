"""07 激情之爱：热恋期一过，就没感觉了吗？"""

from adler import kit as K
from adler.core import Counter, Custom, Fig, Icon, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#D9703A"
G = A.GROUND_Y
REFS = [BOOK, "Acevedo & Aron (2009). Does a long-term relationship kill romantic love? Rev Gen Psychol."]


def build():
    shots = [
        hook("热恋 一过|就 【没感觉】 了？", 108),
        loop("消退的可能|只是“上头”那部分", pose="shrug", hair="long", color=A.HER),
        Shot(4, "以前一天聊八百条|现在各自低头刷手机", "情境演绎", [
            Fig(400, G, 310, at=0, pose="hug", mood="happy", hair="short",
                moves=[(6, dict(x=280, pose="stand", mood="flat", dur=0.8, sfx="wood_low"))]),
            Fig(660, G, 300, at=0, pose="hug", mood="happy", hair="long", color=A.HER, face=-1,
                moves=[(6, dict(x=800, pose="stand", mood="flat", dur=0.8))]),
            Icon("phone", 280, 620, 90, color=K.INK2, at=8, sfx="wood_high"),
            Icon("phone", 800, 620, 90, color=K.INK2, at=9, sfx="wood_high"),
        ], draw=A.ground, note="从拥抱到各自玩手机"),
        drop("激情之爱", "Passionate Love", "心跳加速的激情|通常会慢慢【降温】", 180),
        Shot(4, "爱情有三个成分：|亲密、激情、承诺", "原书 · 斯滕伯格爱情三角", [
            Custom(A.triangle, x=540, y=760, at=0, enter="none", R=300, b0=0, step=2, dim=(1,), dim_at=10),
        ], hits=[(0, "wood_low", 0.8, "亲密"), (2, "wood_low", 0.8, "激情"), (4, "wood_low", 0.8, "承诺"),
                 (10, "rim", 0.8, "激情变淡")], note="三角逐点出现，激情变淡"),
        line("激情 会 退|亲密 可以 【加深】", 104),
        Shot(4, "一项元分析汇总了|25项研究、6070人", "研究证据 · Acevedo & Aron 2009", [
            Counter(0, 6070, 540, 660, 200, at=0, land=4, fmt="{:,.0f}", sub="人 · 25 项研究"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "长期关系里|浪漫之爱可以一直都在", "研究证据 · Acevedo & Aron 2009", [
            Fig(400, G, 310, at=0, pose="hug", mood="happy", hair="short", head_color=K.SKIN),
            Fig(660, G, 300, at=0, pose="hug", mood="happy", hair="bun", color=A.HER, face=-1),
            Icon("heart", 530, 560, 120, color=K.RED, at=2, sfx="ding"),
            Spark(530, 560, at=2),
        ], draw=A.ground, research=True, note="老夫老妻仍相爱"),
        Shot(4, "但患得患失的“痴迷”|在长期关系里反而有害", "研究证据 · Acevedo & Aron 2009", [
            Icon("chain", 540, 720, 200, color=K.RED, at=0, sfx="rim"),
        ], research=True, note="痴迷"),
        slam("长久", "热烈会退|长久要经营"),
        doubt("能保持浪漫的伴侣|并不是人人都能做到", tag="边界"),
        tip("试试：和对方|一起做一件新鲜事", hair="long", color=A.HER),
        end_shot(REFS, "08 依恋：为什么有人一谈恋爱就患得患失"),
    ]
    return episode(7, "love", "激情之爱", "热恋期一过，就没感觉了吗？", ACC, shots, REFS,
                   "热恋一过|就【没感觉】了？",
                   ["激情之爱与相伴之爱、斯滕伯格爱情三角理论为《亲密关系》第 8 章内容。",
                    "Acevedo & Aron (2009)：25 项研究、6070 人，长期关系中不含痴迷成分的浪漫之爱可以持续，痴迷成分在长期关系中与满意度负相关。",
                    "“一起做新鲜事”参考自我扩展理论，为建议。"])
