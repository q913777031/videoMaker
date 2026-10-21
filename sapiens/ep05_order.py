"""05 想象的秩序：为什么名校、大厂，能让人一眼高看？"""

from adler import kit as K
from adler.core import Card, Custom, Fig, Icon, Label, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#5865B8"
G = A.GROUND_Y
REFS = [BOOK]


def build():
    shots = [
        hook("名校 大厂|为什么 【自带光环】？", 104),
        loop("光环不在你身上|在大家的想象里"),
        Shot(4, "同样的能力|简历上多两个字就不一样", "情境演绎", [
            Fig(320, G, 300, at=0, mood="calm", hair="short"),
            Fig(760, G, 300, at=0, mood="calm", hair="long", color=K.OTHER),
            Label("普通学校", 320, 600, 38, at=2, fill=K.INK2, sfx="wood_low"),
            Label("名校 · 大厂", 760, 600, 38, at=4, fill=ACC, sfx="ding"),
            Spark(760, 600, at=4),
        ], draw=A.ground, note="同样两个人，标签不同"),
        drop("想象的秩序", "Imagined Order", "社会的等级|靠大家一起【相信】", 160),
        Shot(4, "约公元前1776年|汉谟拉比法典把人分了等级", "原书 · 例子", [
            Custom(lambda c, g, t, d: A.tablet(c, 0, 0, 380), x=540, y=780, at=0, enter="pop", sfx="wood_low"),
        ], note="石碑"),
        line("法典 说 【不平等】|宣言 说 【人人平等】", 88),
        Shot(4, "公元1776年|美国独立宣言说人人平等", "原书 · 例子", [
            Custom(lambda c, g, t, d: A.tablet(c, 0, 0, 300), x=300, y=780, at=0, enter="none"),
            Custom(lambda c, g, t, d: A.scroll(c, 0, 0, 300), x=780, y=780, at=2, enter="pop", sfx="ding"),
            Spark(780, 780, at=2),
        ], research=True, flashes=[2], note="二次钩子：两份文件"),
        Shot(4, "书里说：这两种秩序|都是想象出来的", "原书 · 大意", [
            Custom(lambda c, g, t, d: A.tablet(c, 0, 0, 300), x=300, y=780, at=0, enter="none"),
            Custom(lambda c, g, t, d: A.scroll(c, 0, 0, 300), x=780, y=780, at=0, enter="none"),
            Icon("cloud", 540, 520, 160, color=ACC, at=2, sfx="wood_high"),
        ], research=True, note="两者都是想象"),
        Shot(4, "想象的秩序|让几百万陌生人有序合作", "原书 · 大意", [
            Custom(A.crowd, x=540, y=G, at=0, enter="fade", n=14, s=150, spread=880, rows=3),
            Card("同一套规则", 540, 540, 50, at=2, sfx="wood_low"),
        ], draw=A.ground, note="一群人，一套规则"),
        slam("相信", "只要大家都信|它就是真的"),
        doubt("“一切秩序都是想象”|被批评过于简化"),
        tip("试试：看一个人时|先摘掉标签看一眼"),
        end_shot(REFS, "06 金钱：为什么手机里一串数字，能买到一切"),
    ]
    return episode(5, "order", "想象的秩序", "为什么名校、大厂，能让人一眼高看？", ACC, shots, REFS,
                   "名校大厂|为什么【自带光环】？",
                   ["“想象的秩序”与汉谟拉比法典（约公元前 1776 年）对比美国《独立宣言》（1776 年）的例子出自《人类简史》第 6 章。",
                    "名校大厂光环为情境演绎；“所有秩序皆为想象”的论断在学界有简化之嫌的批评。"])
