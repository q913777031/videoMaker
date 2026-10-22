"""09 幸福：为什么日子越过越好，你却没更快乐？（重做版）"""

from adler import kit as K
from adler.core import Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop2, redo, slam2, tip2

ACC = "#C79A2E"
G = A.GROUND_Y
REFS = [BOOK, "Killingsworth, Kahneman & Mellers (2023). Income and emotional well-being. PNAS."]
LEFT = ("你 50万", "同事都 80万", K.INK2)
RIGHT = ("你 40万", "同事都 30万", ACC)


def build():
    shots = [
        ask("年薪 二选一|你 选 【哪个】？", [
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=3, left=LEFT, right=RIGHT),
        ], hits=[(3, "wood_low", 0.8, "选项A"), (4, "wood_low", 0.8, "选项B")], note="互动：绝对还是相对"),
        Shot(4, "倒计时3秒|凭第一感觉", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=-9, pick=7, pick_side=1, left=LEFT, right=RIGHT),
            Label("钱少了，心里却更舒服？", 540, 1260, 42, at=10, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (7, "ding", 0.9, "选中右边")], flashes=[6], shake=[(6, 12.0)], punch=0.025, note="很多人选右边"),
        Shot(2, "让你难受的|常常不是钱，是比较", "互动小游戏", [
            Pops("快乐 来自|【比较】", 540, 760, 120, at=0, step=1),
            Spark(540, 760, at=4, sfx="ding"),
        ], text_beat=0, note="揭晓"),
        drop2("幸福", "Happiness", "快乐取决于|【期望】，不只是条件", "比较 期望 习惯", size=220),
        Shot(4, "比爸妈那代|有房有车有手机", "情境演绎", [
            Icon("house", 260, 760, 170, color=ACC, at=0, sfx="wood_low"),
            Icon("phone", 540, 760, 170, color=K.INK2, at=3, sfx="wood_low"),
            Icon("gift", 820, 760, 170, color=K.RED, at=6, sfx="wood_low"),
            Label("却没更快乐", 540, 1000, 46, at=10, fill=K.RED, sfx="rim"),
        ], note="条件变好"),
        Shot(4, "条件涨了|期望也跟着涨", "原书 · 大意", [
            Custom(A.two_lines, x=540, y=780, at=0, enter="fade", b0=0, b1=12),
            Label("差距没变", 540, 1100, 44, at=12, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_low", 0.7, "曲线上升"), (6, "wood_high", 0.6, "上升")], note="两条一起上升（示意）"),
        Shot(4, "2023年研究：对大多数人|钱越多，越开心", "研究证据 · Killingsworth 等 2023", [
            Icon("sun", 540, 640, 200, color=K.GOLD, at=0, sfx="ding"),
            Spark(540, 640, at=0),
            Label("钱有用", 540, 900, 48, at=5, fill=K.GREEN, sfx="wood_high"),
            Fig(540, G, 260, at=9, pose="cheer", mood="happy", hair="short", sfx="wood_low"),
        ], draw=A.ground, research=True, punch=0.02, flashes=[0], note="二次钩子：2023 研究"),
        Shot(4, "但最不快乐的那群人|收入再高也不再变开心", "研究证据 · Killingsworth 等 2023", [
            Fig(540, G, 300, at=0, pose="sad", mood="sad", hair="bun", color=K.OTHER2),
            Icon("cloud", 540, 520, 160, color=K.INK2, at=3, sfx="rim"),
            Label("钱买不来全部", 540, 760, 46, at=8, fill=K.RED, sfx="rim"),
        ], draw=A.ground, research=True, note="不快乐的人到顶"),
        Shot(4, "快乐取决于|你拿什么和自己比", "原书 · 大意", [
            Icon("scale", 540, 720, 230, color=ACC, at=0, sfx="wood_low"),
            Fig(240, G, 240, at=2, pose="think", mood="worried", hair="bun", color=K.OTHER2, sfx="wood_low"),
            Label("期望", 330, 960, 44, at=4, fill=K.RED, sfx="wood_high"),
            Label("现实", 750, 960, 44, at=7, fill=ACC, sfx="wood_high"),
            Spark(540, 720, at=11, sfx="ding"),
        ], draw=A.ground, note="期望与现实的天平"),
        slam2("期望", "钱 有用|期望 会 【追上来】", "管住期望|比追更多更有效"),
        Shot(4, "第一招：今晚写下|三件已经拥有的好事", "小方法", [
            Custom(A.memo, x=540, y=820, at=0, enter="pop", title="已经拥有的", items=["身体健康", "有人惦记", "今天按时下班"], b0=2),
            Icon("heart", 820, 1120, 110, color=K.RED, at=10, sfx="ding"),
        ], hits=[(2, "pop", 0.7, "1"), (3, "pop", 0.7, "2"), (4, "pop", 0.7, "3")], note="三件好事"),
        tip2("第二招：少比较|多知足", "少 比较|多 【知足】", 120),
        end_shot(REFS, "10 从动物到上帝：人类越来越强，为什么越来越焦虑"),
    ]
    return redo(9, "happiness", "幸福", "为什么日子越过越好，你却没更快乐？", ACC, shots, REFS,
                "日子越过越好|为什么没更【快乐】？",
                ["“幸福取决于客观条件与主观期望的关系”出自《人类简史》第 19 章；年薪二选一小游戏为情境演绎，曲线为示意，两招为方法建议。",
                 "Killingsworth、Kahneman & Mellers (2023, PNAS)：对多数人而言情绪幸福感随收入持续上升，只有最不快乐的一群人在高收入段出现平台。"])
