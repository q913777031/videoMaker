"""10 从动物到上帝：人类越来越强，为什么越来越焦虑？（重做版）"""

from adler import kit as K
from adler.core import Card, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop2, redo, slam2, tip2

ACC = "#8E5BA8"
G = A.GROUND_Y
REFS = [BOOK]
MARKS = [(0.0, "0:00 认知革命", -9), (19.88, "19:53 农业", 8), (23.83, "23:50 科学", 11)]


def build():
    shots = [
        ask("人类史 压缩 成 一天|农业 出现 在 【几点】？", [
            Custom(A.day_clock, x=540, y=1020, at=0, enter="pop", R=240, marks=[(0.0, "0:00 认知革命", 3)]),
        ], hits=[(3, "wood_low", 0.8, "零点")], note="互动：人类史一天"),
        Shot(4, "倒计时3秒|猜一个时间", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.day_clock, x=540, y=1020, at=0, enter="none", R=240, marks=MARKS),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (8, "ding", 0.9, "19:53 农业"), (11, "rim", 0.9, "23:50 科学")], flashes=[6], shake=[(6, 12.0)], punch=0.025,
            note="指针扫到 19:53、23:50"),
        Shot(2, "最后10分钟|人类却改天换地", "互动小游戏", [
            Pops("最后 10 分钟|【改天换地】", 540, 760, 110, at=0, step=1),
        ], text_beat=0, note="揭晓"),
        drop2("从动物到上帝", "From Animals into Gods", "智人正变成|【神】一样的物种", "基因 AI 太空", size=130),
        Shot(4, "七万年、一万多年、五百年|三场革命走到今天", "原书 · 全书回顾", [
            Custom(A.timeline, x=540, y=760, at=0, enter="none", b0=0, step=4, w=720,
                   points=[("7万年前", "认知革命"), ("1.2万年前", "农业革命"), ("500年前", "科学革命")]),
            Label("越来越快", 540, 1000, 46, at=12, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_low", 0.8, "认知革命"), (4, "wood_low", 0.8, "农业革命"), (8, "ding", 0.9, "科学革命")],
            note="三场革命时间轴"),
        Shot(4, "", "一句话", [
            Pops("能力 越来越 大|却 不知道 【想要什么】", 540, 780, 92, at=0, step=2),
        ], punch=0.02, flashes=[10], note="金句"),
        Shot(4, "外卖、导航、AI|我们几乎无所不能", "情境演绎", [
            Fig(260, G, 300, at=0, pose="point", mood="smile", hair="short"),
            Icon("phone", 600, 560, 150, color=ACC, at=2, sfx="wood_high"),
            Icon("target", 880, 560, 130, color=K.RED, at=5, sfx="wood_high"),
            Custom(A.laptop, x=640, y=930, at=8, enter="pop", w=380, p0=0.4, p1=1.0, b0=8, b1=14, title="AI 助手",
                   sfx="wood_low"),
        ], draw=A.ground, research=True, punch=0.02, flashes=[2], note="二次钩子：无所不能"),
        Shot(4, "书的结尾问：有什么比|不知足的神更危险？", "原书 · 结尾", [
            Card("不知足|也不知道想要什么", 540, 720, 56, at=0, sfx="ding"),
            Spark(540, 720, at=0),
            Icon("question", 820, 520, 110, color=K.RED, at=6, sfx="rim"),
            Label("最危险", 540, 1000, 50, at=10, fill=K.RED, sfx="kick"),
        ], research=True, note="结尾之问"),
        Shot(4, "", "十讲回顾", [
            Pops("故事 八卦 农业 奢侈|秩序 金钱 信用 无知|幸福 【未来】", 540, 780, 72, at=0, step=1, gap=18),
        ], research=True, punch=0.02, note="十讲关键词逐个弹出"),
        slam2("想要什么", "最难 的 问题|【想要什么】", "能力越大|越要想清楚"),
        Shot(4, "第一招：写下|你真正想要的三件事", "小方法", [
            Custom(A.memo, x=540, y=820, at=0, enter="pop", title="我真正想要的", items=["________", "________", "________"], b0=2),
            Icon("bulb", 820, 1120, 110, color=K.GOLD, at=8, sfx="ding"),
            Spark(820, 1120, at=12, sfx="wood_high"),
        ], hits=[(2, "pop", 0.7, "1"), (3, "pop", 0.7, "2"), (4, "pop", 0.7, "3")], note="写下想要的"),
        tip2("十讲走完|问问自己想要什么", "我 想要 【什么】？", 120),
        end_shot(REFS, None),
    ]
    return redo(10, "gods", "从动物到上帝", "人类越来越强，为什么越来越焦虑？", ACC, shots, REFS,
                "人类越来越强|为什么越来越【焦虑】？",
                ["三场革命（约 7 万年前认知革命、约 1.2 万年前农业革命、约 500 年前科学革命）与结尾之问出自《人类简史》。",
                 "“压缩成一天”按 7 万年 = 24 小时换算：农业革命约在 19:53，科学革命约在 23:50。"])
