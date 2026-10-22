"""01 虚构的故事：为什么你为公司拼命，却从没见过“它”？（重做版：互动开场、每 3 秒一变、结论直给）"""

from adler import kit as K
from adler.core import Bubble, Card, Counter, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop2, redo, slam2, tip2

ACC = "#C8553D"
G = A.GROUND_Y
REFS = [BOOK]
CARDS = [("sun", "河流", False), ("brief", "公司", True), ("sprout", "大树", False),
         ("flag", "国界", True), ("heart", "狮子", False), ("book", "法律", True)]


def build():
    shots = [
        ask("下面 哪些|离开 人类 就 【不存在】？", [
            Custom(A.pick_cards, x=540, y=950, at=0, enter="none", cards=CARDS, b0=3),
        ], hits=[(3, "pop", 0.6, "卡"), (4, "pop", 0.6, "卡"), (5, "pop", 0.6, "卡"), (6, "pop", 0.6, "卡")],
            note="互动：选出虚构之物"),
        Shot(4, "倒计时3秒|你选了哪几个？", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.pick_cards, x=540, y=950, at=0, enter="none", cards=CARDS, b0=-9, reveal=8),
            Label("公司、国界、法律", 540, 1262, 44, at=11, fill=ACC, sfx="ding"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (8, "ding", 0.9, "揭晓")], flashes=[6], shake=[(6, 12.0)], punch=0.025, note="倒计时，揭晓三个“虚构”"),
        Shot(2, "它们只存在于|所有人共同的相信里", "互动小游戏", [
            Pops("你 拼命 的|也是 一个 【故事】", 540, 760, 100, at=0, step=1),
        ], text_beat=0, note="揭晓"),
        drop2("虚构的故事", "Fiction", "智人能一起相信|【不存在】的东西", "公司 国家 法律", size=160),
        Shot(4, "每天打卡、开会、领工资|几千人为同一家公司忙", "情境演绎", [
            Custom(A.crowd, x=540, y=G, at=0, enter="fade", n=7, s=220, spread=760),
            Custom(lambda c, g, t, d: A.badge(c, 0, 0, 170, ACC), x=540, y=560, at=2, enter="pop", sfx="wood_low"),
            Label("某某科技有限公司", 540, 760, 40, at=6, fill=ACC, sfx="wood_high"),
            Icon("question", 820, 500, 100, color=K.RED, at=10, sfx="rim"),
            Spark(820, 500, at=10),
        ], draw=A.ground, note="一群人与一张工牌"),
        Shot(4, "", "一句话", [
            Pops("猴子 不信|天堂 里 有 【香蕉】", 540, 780, 110, at=0, step=2),
        ], punch=0.02, flashes=[6], note="书中名句改写：只有人会为想象中的回报合作"),
        Shot(4, "书里的例子：标致汽车|工厂拆了、员工换光了", "原书 · 例子", [
            Card("标致 Peugeot", 540, 560, 56, at=0, sfx="wood_low"),
            Icon("house", 360, 860, 150, color=K.INK2, at=2, sfx="wood_low"),
            Icon("cross", 360, 860, 120, color=K.RED, at=4, sfx="rim"),
            Custom(A.crowd, x=760, y=G, at=6, enter="fade", n=3, s=170, spread=260, rows=1),
            Icon("cross", 760, 900, 120, color=K.RED, at=9, sfx="rim"),
        ], draw=A.ground, research=True, punch=0.02, flashes=[0], note="二次钩子：标致公司"),
        Shot(4, "公司照样存在|它是法律意义上的“法人”", "原书 · 例子", [
            Card("法人", 540, 700, 100, at=0, sfx="ding"),
            Spark(540, 700, at=0),
            Bubble("一个大家都认的故事", 540, 960, 40, at=5, sfx="wood_high"),
            Icon("check", 820, 560, 100, color=K.GREEN, at=10, sfx="ding"),
        ], research=True, note="法人：共同相信的故事"),
        Shot(4, "约7万年前|智人开始会讲这样的故事", "原书 · 认知革命", [
            Counter(0, 70000, 540, 620, 180, at=0, land=4, fmt="{:,.0f}", sub="年前 · 认知革命"),
            Fig(320, G, 280, at=6, pose="point", mood="open", hair="short", color=K.OTHER3, sfx="wood_low"),
            Bubble("从前有个神…", 520, 900, 40, at=8, sfx="wood_high"),
            Custom(A.crowd, x=780, y=G, at=11, enter="fade", n=4, s=170, spread=280, rows=1),
        ], draw=A.ground, research=True, note="数字落定，讲故事"),
        slam2("合作", "故事 让 陌生人|【合作】", "智人赢在|会讲故事"),
        Shot(4, "第一招：遇到规则|先问“这是谁定的”", "小方法", [
            Custom(A.checklist, x=540, y=800, at=0, enter="pop", b0=2, step=3, title="是事实还是共识？",
                   items=[("太阳东升", True), ("公司制度", False), ("考勤规定", False), ("万有引力", True)]),
        ], hits=[(2, "wood_high", 0.8, "事实"), (5, "rim", 0.8, "共识"), (8, "rim", 0.8, "共识"), (11, "ding", 0.9, "事实")],
            note="分清事实与共识"),
        tip2("第二招：共识能改|别被它困住", "共识 可以 【改】", 120),
        end_shot(REFS, "02 八卦：为什么同事的八卦停不下来"),
    ]
    return redo(1, "fiction", "虚构的故事", "为什么你为公司拼命，却从没见过“它”？", ACC, shots, REFS,
                "你为公司拼命|可公司【在哪儿】？",
                ["“虚构的故事”、标致公司（法人）与约 7 万年前的认知革命出自《人类简史》第 2 章；选卡片小游戏为情境演绎，两招为方法建议。"])
