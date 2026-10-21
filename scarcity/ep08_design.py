"""08 跳出稀缺：别靠意志力，靠设计（重做版）"""

from adler import kit as K
from adler.core import Card, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop, episode, slam, tip2

ACC = "#5865B8"
GROUND = A.GROUND_Y
REFS = [BOOK, "Karlan, McConnell, Mullainathan & Zinman (2016). Getting to the top of mind. Management Science.",
        "Shah, Shafir & Mullainathan (2015). Scarcity frames value. Psychological Science."]
TODO = ["交周报", "还信用卡", "给妈打电话", "取快递", "订明早会议室"]


def build():
    shots = [
        ask("3秒 记住|今天 的 【5件事】！", [
            Custom(A.memo, x=540, y=1000, at=0, enter="pop", items=TODO, b0=2),
        ], hits=[(2, "pop", 0.6, "1"), (3, "pop", 0.6, "2"), (4, "pop", 0.6, "3"), (5, "pop", 0.6, "4"), (6, "pop", 0.6, "5")],
            note="互动：记五件事"),
        Shot(4, "", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.memo, x=540, y=1000, at=0, enter="none", items=TODO, b0=-9, cover=6),
            Custom(A.toasts, x=0, y=0, at=0, enter="none", hold=3,
                   items=[(8, 300, 640, "老板：在吗？"), (10, 780, 1260, "群消息 99+")]),
            Label("想起来了吗？", 540, 615, 46, at=12, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (8, "pop", 0.7, "消息"), (10, "pop", 0.7, "消息")], flashes=[6], shake=[(6, 12.0)], punch=0.025,
            note="便签盖住，消息打岔，追问第 3 件"),
        Shot(2, "记不住很正常|靠的不该是脑子", "互动小游戏", [
            Card("3. 给妈打电话", 540, 760, 64, at=0, sfx="ding"),
            Spark(540, 760, at=0),
            Icon("bulb", 820, 560, 110, color=K.GOLD, at=4, sfx="wood_high"),
        ], text_beat=0, note="揭晓第 3 件"),
        drop("靠设计", "Design for Scarcity", "别靠记性|让环境替你记", "自动化 提醒 默认", size=200),
        Shot(4, "", "一句话", [
            Pops("自动 扣款|定时 提醒|门口 【挂钩】", 540, 780, 96, at=0, step=1, gap=28),
            Icon("phone", 200, 520, 110, color=K.INK2, at=8, sfx="wood_high"),
            Icon("check", 880, 1060, 110, color=K.GREEN, at=12, sfx="ding"),
        ], punch=0.02, flashes=[5], note="三个设计"),
        Shot(4, "一条提醒|就把事情拉回眼前", "机制示意", [
            Custom(A.phone_chat, x=540, y=790, at=0, enter="pop", who="提醒", unread=False,
                   msgs=[(2, "今天是存钱日"), (5, "出门带工牌"), (8, "给妈打电话")]),
            Icon("check", 820, 1150, 110, color=K.GREEN, at=12, sfx="ding"),
        ], hits=[(2, "ding", 0.8, "提醒"), (5, "ding", 0.8, "提醒"), (8, "ding", 0.8, "提醒")], note="提醒逐条弹出"),
        Shot(4, "科学家真的测过：|给储户定期发提醒短信", "研究证据 · Karlan 等 2016", [
            Fig(300, GROUND, 300, at=0, pose="point", mood="open", hair="short"),
            Icon("phone", 760, 620, 170, color=ACC, at=3, sfx="ding"),
            Spark(760, 620, at=3),
            Card("别忘了存钱哦", 760, 860, 44, at=7, sfx="wood_high"),
            Icon("check", 760, 1040, 100, color=K.GREEN, at=11, sfx="ding"),
        ], draw=A.ground, research=True, punch=0.02, flashes=[3], note="二次钩子：提醒实验"),
        Shot(4, "收到提醒的人|更容易存够目标", "研究证据 · Karlan 等 2016", [
            Icon("target", 540, 740, 240, color=ACC, at=0, sfx="wood_low"),
            Icon("check", 720, 580, 110, color=K.GREEN, at=4, sfx="rim"),
            Spark(720, 580, at=4),
            Label("提到目标的提醒最有效", 540, 1030, 42, at=9, fill=ACC, sfx="ding"),
        ], research=True, note="达成储蓄目标"),
        Shot(4, "缺钱的人更会算：|同一瓶酒不因店贵多付", "研究证据 · Shah 等 2015", [
            Card("同一瓶啤酒", 540, 540, 48, at=0, sfx="wood_low"),
            Label("高档酒店", 320, 760, 40, at=3, fill=K.GOLD, sfx="wood_high"),
            Label("街边小店", 760, 760, 40, at=5, fill=K.INK2, sfx="wood_high"),
            Icon("scale", 540, 980, 160, color=ACC, at=8, sfx="rim"),
            Spark(540, 980, at=11, sfx="ding"),
        ], research=True, note="稀缺让人更一致地衡量价值"),
        slam("设计", "让 环境 替你 【记】", "意志力会累|设计不会"),
        Shot(4, "第一招：能自动的|全部设成自动", "小方法", [
            Custom(A.checklist, x=540, y=800, at=0, enter="pop", b0=2, step=3, title="设成自动",
                   items=[("自动还款", True), ("自动存钱", True), ("固定日程提醒", True), ("续费前提醒", True)]),
        ], hits=[(2, "wood_high", 0.8, "✓"), (5, "wood_high", 0.8, "✓"), (8, "wood_high", 0.8, "✓"), (11, "ding", 0.9, "✓")],
            note="自动化清单"),
        tip2("八讲走完|今晚设一个自动提醒", "设 一个 【提醒】", 120),
        end_shot(REFS, None),
    ]
    return episode(8, "design", "跳出稀缺", "别靠意志力，靠设计", ACC, shots, REFS,
                   "跳出稀缺|别靠意志力，靠【设计】",
                   ["《稀缺》第三部分主张为稀缺设计环境；记五件事小游戏为情境演绎，两招为方法建议。",
                    "Karlan 等 (2016, Management Science)：提醒短信提高了储户达成储蓄目标的比例，提到目标与激励的提醒效果最好。",
                    "Shah, Shafir & Mullainathan (2015)：低收入者对同一瓶啤酒的出价不因店面高档与否而变。"])
