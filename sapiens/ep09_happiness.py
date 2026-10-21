"""09 幸福：为什么日子越过越好，你却没更快乐？"""

from adler import kit as K
from adler.core import Counter, Custom, Icon, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#C79A2E"
G = A.GROUND_Y
REFS = [BOOK, "Kahneman & Deaton (2010). High income improves evaluation of life. PNAS.",
        "Killingsworth, Kahneman & Mellers (2023). Income and emotional well-being. PNAS."]


def build():
    shots = [
        hook("日子 越过 越 好|为什么 没 更 【快乐】？", 92),
        loop("书里给的答案|有点扎心", pose="sad", mood="worried", hair="bun", color=K.OTHER2),
        Shot(4, "比爸妈那代|有车有房有手机", "情境演绎", [
            Icon("house", 260, 760, 170, color=ACC, at=0, sfx="wood_low"),
            Icon("phone", 540, 760, 170, color=K.INK2, at=2, sfx="wood_low"),
            Icon("gift", 820, 760, 170, color=K.RED, at=4, sfx="wood_low"),
            Spark(540, 760, at=6, sfx="rim"),
        ], note="有房有手机有礼物"),
        drop("幸福", "Happiness", "快乐取决于|【期望】，不只是条件", 220),
        Shot(4, "条件涨了|期望也跟着涨了", "原书 · 大意", [
            Custom(A.two_lines, x=540, y=780, at=0, enter="fade", b0=0, b1=12),
        ], hits=[(0, "wood_low", 0.7, "曲线上升")], note="两条一起上升的曲线（示意）"),
        line("条件 涨了|期望 也 【涨了】", 104),
        Shot(4, "2010年研究：收入过某点|好心情不再涨", "研究证据 · Kahneman & Deaton 2010", [
            Counter(0, 75000, 540, 660, 170, at=0, land=4, fmt="${:,.0f}", sub="美元年收入（2008–09 年美国数据）"),
        ], research=True, punch=0.02, flashes=[4], note="二次钩子：数字落定"),
        Shot(4, "2021年新研究却发现|收入越高，平均越开心", "研究证据 · Killingsworth 2021", [
            Custom(A.two_lines, x=540, y=780, at=0, enter="fade", b0=-12, b1=0),
            Icon("question", 820, 520, 100, color=K.RED, at=2, sfx="rim"),
        ], research=True, note="结论相反"),
        Shot(4, "2023年双方合作：只有|最不快乐的人会“到顶”", "研究证据 · Killingsworth 等 2023", [
            Icon("scale", 540, 720, 230, color=ACC, at=0, sfx="wood_low"),
            Spark(540, 720, at=2, sfx="ding"),
        ], research=True, note="对抗性合作"),
        slam("期望", "钱有用|但期望会追上来"),
        doubt("幸福很难测量|结论还在不断更新"),
        tip("试试：今晚写下|三件已经拥有的好事", hair="bun", color=K.OTHER2),
        end_shot(REFS, "10 从动物到上帝：人类越来越强，为什么越来越焦虑"),
    ]
    return episode(9, "happiness", "幸福", "为什么日子越过越好，你却没更快乐？", ACC, shots, REFS,
                   "日子越过越好|为什么没更【快乐】？",
                   ["“幸福取决于客观条件与主观期望的关系”出自《人类简史》第 19 章。",
                    "Kahneman & Deaton (2010)：年收入约 7.5 万美元后情绪幸福感趋平；Killingsworth (2021) 发现持续上升；"
                    "Killingsworth、Kahneman & Mellers (2023) 对抗性合作：只有最不快乐的一群人在高收入段出现平台。",
                    "曲线为示意；写三件好事为常见建议，非书中内容。"])
