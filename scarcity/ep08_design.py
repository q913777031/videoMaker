"""08 跳出稀缺：别靠意志力，靠设计"""

from adler import kit as K
from adler.core import Big, Card, Custom, Fig, Glow, Icon, Label, Pops, Rays, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, episode

ACC = "#5865B8"
GROUND = A.GROUND_Y
REFS = [BOOK, "Karlan, McConnell, Mullainathan & Zinman (2016). Getting to the top of mind. Management Science.",
        "Shah, Shafir & Mullainathan (2015). Scarcity frames value. Psychological Science."]


def build():
    shots = [
        Shot(2, "", "灵魂拷问", [
            Glow(540, 760, 520, at=0, alpha=0.3),
            Pops("光靠 意志力|【没用】？", 540, 760, 110, at=0, step=1),
        ], punch=0.025, flashes=[0], note="钩子：问题逐词弹出"),
        Shot(2, "因为意志力本身|也要占用带宽", "先说结论", [
            Fig(540, GROUND, 330, at=0, pose="think", mood="worried", hair="short"),
            Icon("bulb", 760, 520, 110, color=ACC, at=1, sfx="rim"),
            Spark(760, 520, at=1),
        ], draw=A.ground, text_beat=0, note="灯泡弹出"),
        Shot(4, "每天要记的事太多|总有几件会漏", "情境演绎", [
            Custom(A.checklist, x=540, y=800, at=0, enter="pop", b0=2, step=2, title="今天要做",
                   items=[("交周报", True), ("还信用卡", False), ("给妈打电话", False), ("存钱", False)]),
        ], hits=[(2, "wood_high", 0.8, "✓"), (4, "rim", 0.9, "✗"), (6, "rim", 0.9, "✗"), (8, "rim", 0.9, "✗")],
            note="待办清单漏了三件"),
        Shot(4, "别靠记性|让环境替你记", "原书 · 核心观点", [
            Big("靠设计", 540, 700, 200, at=0, sfx="kick", sub="Design for Scarcity", rays=True, glow=True, shine=True,
                spark=True, note="概念落版（音乐 drop）"),
        ], punch=0.035, flashes=[0], shake=[0], note="drop 处观点砸下"),
        Shot(4, "", "一句话", [
            Glow(540, 780, 560, at=0, alpha=0.26),
            Pops("自动 扣款|定时 提醒|门口 【挂钩】", 540, 780, 96, at=0, step=1, gap=28),
        ], punch=0.02, flashes=[5], note="三个设计逐词弹出"),
        Shot(4, "一条提醒|就能把事情拉回眼前", "机制示意", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="提醒", unread=False,
                   msgs=[(2, "今天是存钱日"), (5, "出门带工牌"), (8, "给妈打电话")]),
        ], hits=[(2, "ding", 0.8, "提醒 1"), (5, "ding", 0.8, "提醒 2"), (8, "ding", 0.8, "提醒 3")],
            note="手机提醒逐条弹出"),
        Shot(4, "研究者给储户|定期发提醒短信", "研究证据 · Karlan 等 2016", [
            Fig(330, GROUND, 300, at=0, pose="point", mood="open", hair="short"),
            Icon("phone", 740, 640, 170, color=ACC, at=2, sfx="ding"),
            Spark(740, 640, at=2),
        ], draw=A.ground, research=True, flashes=[2], note="二次钩子：提醒实验"),
        Shot(4, "收到提醒的人|更容易存够目标", "研究证据 · Karlan 等 2016", [
            Icon("target", 540, 740, 220, color=ACC, at=0, sfx="wood_low"),
            Icon("check", 700, 600, 100, color=K.GREEN, at=2, sfx="rim"),
            Spark(700, 600, at=2),
        ], research=True, note="达成储蓄目标"),
        Shot(4, "稀缺也有好处：缺钱的人|不会因店面高档多付钱", "研究证据 · Shah 等 2015", [
            Card("同一瓶啤酒", 540, 520, 46, at=0, sfx="wood_low"),
            Label("高档酒店", 330, 760, 38, at=2, fill=K.GOLD, sfx="wood_high"),
            Label("街边小店", 750, 760, 38, at=3, fill=K.INK2, sfx="wood_high"),
            Icon("scale", 540, 960, 150, color=ACC, at=5, sfx="rim"),
        ], research=True, note="稀缺让人更一致地衡量价值"),
        Shot(2, "因为每一分钱|都要拿来权衡", "原书 · 大意", [
            Big("权衡", 540, 760, 160, at=0, sfx="kick", glow=True),
        ], text_beat=0, punch=0.03, shake=[0], note="权衡二字砸下"),
        Shot(4, "书里部分结论|还在被检验和争论", "常见质疑", [
            Icon("book", 400, 740, 180, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 720, 640, 110, color=K.RED, at=4, sfx="rim"),
        ], note="复现与争议"),
        Shot(2, "八讲走完|愿你给生活留点余闲", "系列收尾", [
            Rays(540, 760, 520, at=0, alpha=0.2),
            Fig(540, GROUND, 330, at=0, pose="cheer", mood="happy", hair="short"),
            Spark(540, 560, at=1, sfx="clap"),
        ], draw=A.ground, text_beat=0, punch=0.02, note="系列收尾"),
        end_shot(REFS, None),
    ]
    return episode(8, "design", "跳出稀缺", "别靠意志力，靠设计", ACC, shots, REFS,
                   "跳出稀缺|别靠意志力，靠【设计】",
                   ["《稀缺》第三部分主张为稀缺设计环境（提醒、默认选项、自动化），而不是指望意志力。待办清单与提醒为情境演绎。",
                    "Karlan 等 (2016, Management Science)：提醒短信提高了储户达成储蓄目标的比例，同时提到目标与激励的提醒效果最好。",
                    "Shah, Shafir & Mullainathan (2015, Psychological Science)：低收入者对同一瓶啤酒的出价不因店面高档与否而变。",
                    "书中部分研究存在复现争议（见第 02、04、05 讲）。"])
