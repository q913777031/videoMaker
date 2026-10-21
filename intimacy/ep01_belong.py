"""01 归属需要：为什么一个人待久了，会莫名难受？"""

from adler import kit as K
from adler.core import Counter, Custom, Fig, Icon, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#D9593A"
G = A.GROUND_Y
REFS = [BOOK, "Holt-Lunstad, Smith & Layton (2010). Social relationships and mortality risk. PLoS Med."]


def build():
    shots = [
        hook("一个人 待 久了|为什么 会 【莫名难受】？", 92),
        loop("不是你矫情|是大脑在提醒你", pose="sad", mood="worried", hair="long", color=A.HER),
        Shot(4, "周末一个人在家|刷了一天手机，越刷越空", "情境演绎", [
            Fig(360, G, 320, at=0, pose="sit_sad", mood="sad", hair="long", color=A.HER),
            Icon("phone", 700, 640, 150, color=K.INK2, at=2, sfx="wood_low"),
            Custom(A.clock_digital, x=700, y=900, at=4, enter="pop", t0=21 * 60 + 50, t1=21 * 60 + 58, b0=4, w=300, h=120,
                   sfx="wood_high"),
        ], draw=A.ground, note="一个人刷手机到深夜"),
        drop("归属需要", "Need to Belong", "人天生需要|稳定的【亲密联结】", 180),
        Shot(4, "不是要很多朋友|是几段稳定、温暖的关系", "原书 · 大意", [
            Fig(400, G, 310, at=0, pose="hug", mood="happy", hair="short"),
            Fig(660, G, 300, at=0, pose="hug", mood="happy", hair="long", color=A.HER, face=-1),
            Icon("heart", 530, 560, 120, color=K.RED, at=2, sfx="ding"),
            Spark(530, 560, at=2),
        ], draw=A.ground, note="拥抱与爱心"),
        line("孤独 不是 矫情|是 身体 在 【报警】", 100),
        Shot(4, "一项元分析汇总了|148项追踪研究", "研究证据 · Holt-Lunstad 2010", [
            Counter(0, 148, 540, 660, 220, at=0, land=4, sub="项研究 · 30多万人"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "社会关系更紧密的人|存活几率高约50%", "研究证据 · Holt-Lunstad 2010", [
            Counter(0, 50, 540, 680, 220, at=0, land=4, suffix="%", sub="（比值比 1.5）"),
        ], research=True, note="数字落定"),
        Shot(4, "这个影响|可以和吸烟等风险相比", "研究证据 · Holt-Lunstad 2010", [
            Icon("scale", 540, 720, 230, color=ACC, at=0, sfx="wood_low"),
            Icon("heart", 380, 560, 90, color=K.RED, at=2, sfx="wood_high"),
            Icon("cross", 700, 560, 90, color=K.INK2, at=3, sfx="wood_high"),
        ], research=True, note="与吸烟等风险相当"),
        slam("必需品", "亲密关系不是奢侈品|是必需品", size=150),
        doubt("这是相关研究|不能直接证明因果"),
        tip("试试：今晚联系|一个很久没聊的人", hair="long", color=A.HER),
        end_shot(REFS, "02 接近性：为什么总会喜欢上身边的人"),
    ]
    return episode(1, "belong", "归属需要", "为什么一个人待久了，会莫名难受？", ACC, shots, REFS,
                   "一个人待久了|为什么会【莫名难受】？",
                   ["“归属需要”（Baumeister & Leary 1995）为《亲密关系》第 1 章核心概念。",
                    "Holt-Lunstad 等 (2010, PLoS Medicine)：148 项研究、308,849 人，社会关系更强者存活的比值比为 1.50；为观察性研究，不能证明因果。"])
