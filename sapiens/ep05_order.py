"""05 想象的秩序：为什么名校、大厂，能让人一眼高看？（重做版）"""

from adler import kit as K
from adler.core import Card, Custom, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop2, redo, slam2, tip2

ACC = "#5865B8"
G = A.GROUND_Y
REFS = [BOOK]
LEFT = ("普通学校", "做过3个项目", K.INK2)
RIGHT = ("名校 · 大厂", "做过3个项目", ACC)


def build():
    shots = [
        ask("能力 一样|你 先 面试 【谁】？", [
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=3, left=LEFT, right=RIGHT),
        ], hits=[(3, "wood_low", 0.8, "简历A"), (4, "wood_low", 0.8, "简历B")], note="互动：先面试谁"),
        Shot(4, "倒计时3秒|选一份简历", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(A.choice, x=540, y=960, at=0, enter="none", b0=-9, pick=7, pick_side=1, left=LEFT, right=RIGHT),
            Label("内容一模一样", 540, 1260, 46, at=10, fill=K.RED, sfx="rim"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到"),
                 (7, "ding", 0.9, "选中名校")], flashes=[6], shake=[(6, 12.0)], punch=0.025, note="选中名校，揭示内容一样"),
        Shot(2, "光环不在简历上|在大家的想象里", "互动小游戏", [
            Pops("标签 先 【说话】", 540, 760, 120, at=0, step=1),
            Spark(540, 760, at=4, sfx="ding"),
        ], text_beat=0, note="揭晓"),
        drop2("想象的秩序", "Imagined Order", "社会的等级|靠大家一起【相信】", "学历 头衔 圈子", size=160),
        Shot(4, "约公元前1776年|汉谟拉比法典把人分成三等", "原书 · 例子", [
            Custom(lambda c, g, t, d: A.tablet(c, 0, 0, 380), x=540, y=780, at=0, enter="pop", sfx="wood_low"),
            Label("贵族", 260, 600, 42, at=4, fill=K.GOLD, sfx="wood_high"),
            Label("平民", 260, 780, 42, at=7, fill=K.INK2, sfx="wood_high"),
            Label("奴隶", 260, 960, 42, at=10, fill=K.INK3, sfx="rim"),
        ], note="石碑与三个等级"),
        Shot(4, "", "一句话", [
            Pops("法典 说 【不平等】|宣言 说 【人人平等】", 540, 780, 88, at=0, step=2),
        ], punch=0.02, flashes=[6], note="金句"),
        Shot(4, "公元1776年|美国独立宣言说人人平等", "原书 · 例子", [
            Custom(lambda c, g, t, d: A.tablet(c, 0, 0, 300), x=300, y=780, at=0, enter="none"),
            Custom(lambda c, g, t, d: A.scroll(c, 0, 0, 300), x=780, y=780, at=2, enter="pop", sfx="ding"),
            Spark(780, 780, at=2),
            Label("相隔3500多年", 540, 1120, 44, at=9, fill=ACC, sfx="wood_high"),
        ], research=True, punch=0.02, flashes=[2], note="二次钩子：两份文件"),
        Shot(4, "书里说：这两种秩序|都是想象出来的", "原书 · 大意", [
            Custom(lambda c, g, t, d: A.tablet(c, 0, 0, 300), x=300, y=780, at=0, enter="none"),
            Custom(lambda c, g, t, d: A.scroll(c, 0, 0, 300), x=780, y=780, at=0, enter="none"),
            Icon("cloud", 540, 500, 170, color=ACC, at=3, sfx="wood_high"),
            Label("都是想象", 540, 1120, 48, at=9, fill=ACC, sfx="ding"),
        ], research=True, note="两者都是想象"),
        Shot(4, "可只要大家都信|几百万陌生人就能有序合作", "原书 · 大意", [
            Custom(A.crowd, x=540, y=G, at=0, enter="fade", n=14, s=150, spread=880, rows=3),
            Card("同一套规则", 540, 540, 50, at=3, sfx="wood_low"),
            Icon("check", 820, 460, 100, color=K.GREEN, at=8, sfx="ding"),
            Label("秩序", 540, 700, 46, at=12, fill=ACC, sfx="rim"),
        ], draw=A.ground, note="一群人，一套规则"),
        slam2("相信", "大家 都 信|就 是 【真的】", "所以光环有用|但也能被改写"),
        Shot(4, "第一招：看人先看|他做过什么", "小方法", [
            Custom(A.checklist, x=540, y=800, at=0, enter="pop", b0=2, step=3, title="面试先看",
                   items=[("做过的项目", True), ("解决的问题", True), ("学校名字", False), ("前公司头衔", False)]),
        ], hits=[(2, "wood_high", 0.8, "✓"), (5, "wood_high", 0.8, "✓"), (8, "rim", 0.8, "✗"), (11, "rim", 0.9, "✗")],
            note="先看作品"),
        tip2("第二招：给自己|攒“作品”而不是标签", "看 作品|不看 【头衔】", 110),
        end_shot(REFS, "06 金钱：为什么手机里一串数字，能买到一切"),
    ]
    return redo(5, "order", "想象的秩序", "为什么名校、大厂，能让人一眼高看？", ACC, shots, REFS,
                "名校大厂|为什么【自带光环】？",
                ["“想象的秩序”与汉谟拉比法典（约公元前 1776 年）对比美国《独立宣言》（1776 年）的例子出自《人类简史》第 6 章；"
                 "简历小游戏为情境演绎，两招为方法建议。"])
