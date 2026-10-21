"""01 虚构的故事：为什么你会为一家公司拼命，却从没见过“它”？"""

from adler import kit as K
from adler.core import Bubble, Card, Counter, Custom, Fig, Icon, Label, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#C8553D"
G = A.GROUND_Y
REFS = [BOOK, "McBrearty & Brooks (2000). The revolution that wasn't. J Hum Evol."]


def build():
    shots = [
        hook("你 每天 为 公司 拼命|可 公司 【在哪儿】？", 92),
        loop("它不在写字楼里|在所有人的脑子里"),
        Shot(4, "每天打卡、开会、领工资|几千人为同一家公司忙", "情境演绎", [
            Custom(A.crowd, x=540, y=G, at=0, enter="fade", n=7, s=220, spread=760),
            Custom(lambda c, g, t, d: A.badge(c, 0, 0, 170, ACC), x=540, y=560, at=2, enter="pop", sfx="wood_low"),
            Label("某某科技有限公司", 540, 760, 40, at=4, fill=ACC, sfx="wood_high"),
        ], draw=A.ground, note="一群人与一张工牌"),
        drop("虚构的故事", "Fiction", "智人能一起相信|【不存在】的东西", 160),
        Shot(4, "公司、国家、法律|都是大家共同相信的故事", "原书 · 大意", [
            Icon("brief", 270, 760, 170, color=ACC, at=0, sfx="wood_low"),
            Icon("flag", 540, 760, 170, color=K.RED, at=2, sfx="wood_low"),
            Icon("scale", 810, 760, 170, color=K.INK2, at=4, sfx="wood_low"),
            Spark(540, 760, at=6, sfx="rim"),
        ], note="公司、国家、法律"),
        line("只有 智人|会 为 一个 【故事】 合作"),
        Shot(4, "书里的例子：标致汽车|工厂拆了、员工换了", "原书 · 例子", [
            Card("标致 Peugeot", 540, 560, 56, at=0, sfx="wood_low"),
            Icon("house", 360, 860, 150, color=K.INK2, at=2, sfx="rim"),
            Icon("cross", 360, 860, 120, color=K.RED, at=3, sfx="rim"),
            Custom(A.crowd, x=760, y=G, at=4, enter="fade", n=3, s=170, spread=260, rows=1),
        ], draw=A.ground, research=True, flashes=[0], note="二次钩子：标致公司"),
        Shot(4, "公司却依然存在|它是法律意义上的“法人”", "原书 · 例子", [
            Card("法人", 540, 720, 90, at=0, sfx="ding"),
            Spark(540, 720, at=0),
            Bubble("一个大家都认的故事", 540, 960, 40, at=3, sfx="wood_high"),
        ], research=True, note="法人：共同相信的故事"),
        Shot(4, "书中说：约7万年前|智人开始会讲这样的故事", "原书 · 认知革命", [
            Counter(0, 70000, 540, 680, 180, at=0, land=4, fmt="{:,.0f}", sub="年前 · 认知革命"),
        ], research=True, note="数字落定"),
        slam("合作", "故事让陌生人|也能大规模合作"),
        doubt("“认知革命”是否突然发生|考古学界有争议"),
        tip("试试：数数今天|你相信了几个“故事”"),
        end_shot(REFS, "02 八卦：为什么同事的八卦停不下来"),
    ]
    return episode(1, "fiction", "虚构的故事", "为什么你为公司拼命，却从没见过“它”？", ACC, shots, REFS,
                   "你为公司拼命|可公司【在哪儿】？",
                   ["“虚构的故事”与标致公司（法人）的例子出自《人类简史》第 2 章；“约 7 万年前的认知革命”为书中说法。",
                    "McBrearty & Brooks (2000) 等认为现代人类行为是逐步积累形成，并非一场突然的“革命”。"])
