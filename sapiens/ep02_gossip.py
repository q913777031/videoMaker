"""02 八卦：为什么同事的八卦，总是停不下来？"""

from adler import kit as K
from adler.core import Bubble, Counter, Custom, Fig, Icon, Shot, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#B5487A"
G = A.GROUND_Y
REFS = [BOOK, "Dunbar (1996). Grooming, Gossip, and the Evolution of Language.",
        "Lindenfors, Wartel & Lind (2021). 'Dunbar's number' deconstructed. Biol Lett."]


def build():
    shots = [
        hook("同事 的 八卦|为什么 【停不下来】？", 100),
        loop("不是大家无聊|是祖先靠它活了下来", pose="think", mood="open", hair="long", color=K.OTHER),
        Shot(4, "工位小群里|消息一条接一条", "情境演绎", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="摸鱼小群",
                   msgs=[(1, "听说了吗…"), (4, "他要跳槽了"), (7, "领导好像知道了"), (10, "嘘，别外传")]),
        ], hits=[(1, "wood_high", 0.8, "消息"), (4, "wood_high", 0.8, "消息"), (7, "wood_high", 0.8, "消息"),
                 (10, "rim", 0.9, "消息")], note="小群消息逐条弹出"),
        drop("八卦理论", "Gossip Theory", "语言最重要的用途|可能是聊【别人】", 170),
        Shot(4, "谁靠谱、谁偷懒|一聊就知道", "原书 · 大意", [
            Fig(240, G, 280, at=0, mood="smile", hair="long", color=K.OTHER),
            Fig(540, G, 300, at=0, mood="open", hair="short"),
            Fig(840, G, 280, at=0, mood="flat", hair="bun", color=K.OTHER2),
            Bubble("他靠谱", 300, 560, 42, at=2, sfx="wood_high"),
            Bubble("她偷懒", 780, 560, 42, at=4, sfx="wood_high"),
        ], draw=A.ground, note="三人聊天"),
        line("不会 八卦|就 不知道 该 【信谁】"),
        Shot(4, "靠八卦维系的群体|上限大约150人", "研究证据 · 邓巴数", [
            Counter(0, 150, 540, 660, 220, at=0, land=4, sub="人 · 书中引用的“邓巴数”"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "人再多|光靠熟人关系就管不过来", "原书 · 大意", [
            Custom(A.crowd, x=540, y=G, at=0, enter="fade", n=12, s=170, spread=860, rows=3),
            Icon("question", 540, 520, 110, color=K.RED, at=4, sfx="rim"),
        ], draw=A.ground, note="一大群人"),
        Shot(4, "所以要靠故事和规则|让陌生人也能协作", "原书 · 大意", [
            Icon("book", 380, 760, 180, color=ACC, at=0, sfx="wood_low"),
            Icon("flag", 700, 760, 180, color=K.RED, at=2, sfx="wood_low"),
        ], note="规则与旗帜（呼应第 01 讲）"),
        slam("规则", "人一多|就得靠规则"),
        doubt("2021年新研究：|“150人上限”并不可靠", tag="常见质疑 · Lindenfors 2021"),
        tip("试试：听到八卦|先问一句“真的吗”", hair="long", color=K.OTHER),
        end_shot(REFS, "03 农业革命：为什么越努力，日子反而越累"),
    ]
    return episode(2, "gossip", "八卦", "为什么同事的八卦，总是停不下来？", ACC, shots, REFS,
                   "同事的八卦|为什么【停不下来】？",
                   ["八卦理论出自《人类简史》第 2 章，书中引用 Dunbar 的研究，认为靠八卦维系的群体上限约 150 人。",
                    "Lindenfors 等 (2021, Biology Letters) 重新分析后发现置信区间极宽（如 4–520），认为无法推出某个特定数字。"])
