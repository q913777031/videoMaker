"""02 八卦：为什么同事的八卦，总是停不下来？（重做版）"""

from adler import kit as K
from adler.core import Bubble, Counter, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop2, redo, slam2, tip2

ACC = "#B5487A"
G = A.GROUND_Y
REFS = [BOOK, "Dunbar (1996). Grooming, Gossip, and the Evolution of Language."]


def build():
    shots = [
        ask("群里 来了 条 八卦|忍住 3秒 【别点开】！", [
            Custom(A.phone_chat, x=540, y=1010, at=0, enter="pop", who="摸鱼小群", h=600,
                   msgs=[(3, "听说了吗…"), (5, "他要跳槽了")]),
        ], hits=[(3, "pop", 0.7, "消息"), (5, "pop", 0.7, "消息")], note="互动：忍住别点八卦"),
        Shot(4, "", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.phone_chat, x=540, y=1010, at=0, enter="none", who="摸鱼小群", h=600,
                   msgs=[(-9, "听说了吗…"), (-8, "他要跳槽了"), (1, "领导也知道了"), (3, "还有更劲爆的…")]),
            Pops("是不是 已经 想 【点开】 了？", 540, 640, 70, at=8, step=1),
        ], hits=[(0, "wood_high", 0.9, "3"), (1, "pop", 0.7, "消息"), (2, "wood_high", 0.9, "2"), (3, "pop", 0.7, "消息"),
                 (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到")], flashes=[6], shake=[(6, 12.0)], punch=0.025,
            note="倒计时里消息不断，追问想不想点"),
        Shot(2, "想知道很正常|祖先靠它活下来", "互动小游戏", [
            Pops("爱 八卦|是 【天性】", 540, 760, 120, at=0, step=1),
            Spark(540, 760, at=4, sfx="ding"),
        ], text_beat=0, note="揭晓"),
        drop2("八卦理论", "Gossip Theory", "语言最重要的用途|是聊【别人】", "谁可靠 谁偷懒 谁有料", size=170),
        Shot(4, "谁靠谱、谁偷懒|一聊就知道", "原书 · 大意", [
            Fig(240, G, 280, at=0, mood="smile", hair="long", color=K.OTHER),
            Fig(540, G, 300, at=0, mood="open", hair="short"),
            Fig(840, G, 280, at=0, mood="flat", hair="bun", color=K.OTHER2),
            Bubble("他靠谱", 300, 560, 42, at=2, sfx="wood_high"),
            Bubble("她偷懒", 780, 560, 42, at=6, sfx="wood_high"),
            Icon("check", 300, 420, 90, color=K.GREEN, at=10, sfx="ding"),
            Icon("cross", 780, 420, 90, color=K.RED, at=12, sfx="rim"),
        ], draw=A.ground, note="三人聊天，信息分类"),
        Shot(4, "", "一句话", [
            Pops("不会 八卦|就 不知道 该 【信谁】", 540, 780, 100, at=0, step=2),
        ], punch=0.02, flashes=[8], note="金句"),
        Shot(4, "靠八卦维系的群体|上限大约150人", "原书 · 邓巴数", [
            Counter(0, 150, 540, 620, 220, at=0, land=4, sub="人"),
            Custom(A.crowd, x=540, y=G, at=6, enter="fade", n=9, s=150, spread=820, rows=2),
            Label("都叫得出名字", 540, 900, 42, at=10, fill=ACC, sfx="ding"),
        ], draw=A.ground, research=True, punch=0.02, flashes=[4], note="二次钩子：150"),
        Shot(4, "人再多|熟人关系就管不过来", "原书 · 大意", [
            Custom(A.crowd, x=540, y=G, at=0, enter="fade", n=14, s=150, spread=880, rows=3),
            Icon("question", 360, 520, 100, color=K.RED, at=3, sfx="rim"),
            Icon("question", 720, 520, 100, color=K.RED, at=6, sfx="rim"),
            Label("你是谁？", 540, 640, 46, at=10, fill=K.RED, sfx="rim"),
        ], draw=A.ground, research=True, note="一大群陌生人"),
        Shot(4, "于是要靠故事和规则|让陌生人也能协作", "原书 · 大意", [
            Icon("book", 380, 760, 180, color=ACC, at=0, sfx="wood_low"),
            Icon("flag", 700, 760, 180, color=K.RED, at=4, sfx="wood_low"),
            Custom(A.crowd, x=540, y=G, at=6, enter="fade", n=7, s=150, spread=760, rows=1),
            Label("部门 · 制度 · 公司", 540, 1000, 44, at=9, fill=ACC, sfx="ding"),
        ], note="规则与旗帜"),
        slam2("规则", "人 多 了|靠 【规则】", "所以公司一大|就有了部门"),
        Shot(4, "第一招：听到八卦|先问“你亲眼看到的？”", "小方法", [
            Fig(360, G, 300, at=0, pose="think", mood="calm", hair="short"),
            Bubble("你亲眼看到的？", 400, 560, 42, at=2, sfx="wood_high"),
            Fig(760, G, 290, at=0, pose="shrug", mood="surprised", hair="long", color=K.OTHER, face=-1),
            Bubble("呃…听说的", 760, 640, 40, at=6, sfx="wood_low"),
            Icon("check", 540, 420, 100, color=K.GREEN, at=10, sfx="ding"),
        ], draw=A.ground, note="追问来源"),
        tip2("第二招：三不原则", "不传 不评 【不站队】", 110),
        end_shot(REFS, "03 农业革命：为什么越努力，日子反而越累"),
    ]
    return redo(2, "gossip", "八卦", "为什么同事的八卦，总是停不下来？", ACC, shots, REFS,
                "同事的八卦|为什么【停不下来】？",
                ["八卦理论与约 150 人的群体上限（引用 Dunbar 的研究）出自《人类简史》第 2 章；忍住不点开小游戏为情境演绎，两招为方法建议。"])
