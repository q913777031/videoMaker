"""《人类简史》10 讲共用：留存骨架里固定段落的镜头模板与 Episode 构造。

每讲镜头小节数固定为 2,2,4,4 | 4,4 | 4,4,4,2 | 4,2,2（共 42 小节）：
钩子 → 先说结论 → 日常情境 → drop 概念 → 机制 → 金句 → 二次钩子/证据×3 → 重击 → 质疑 → 小练习 → 片尾。
"""

from adler import kit as K
from adler.core import Big, Episode, Fig, Glow, Icon, Pops, Rays, Shot, Spark

from .art import GROUND_Y, ground

BOOK = "Harari, Y. N. (2014). Sapiens: A Brief History of Humankind."
TAGS = "#人类简史 #赫拉利 #历史 #读书 #打工人"


def hook(words, size=100):
    """0–4 秒钩子：问题逐词弹出 + 闪白。"""
    return Shot(2, "", "灵魂拷问", [Glow(540, 760, 520, at=0, alpha=0.3), Pops(words, 540, 760, size, at=0, step=1)],
                punch=0.025, flashes=[0], note="钩子：问题逐词弹出")


def loop(text, icon="question", pose="shrug", mood="surprised", **fig):
    """4–8 秒：一句话点明主题、替观众开脱，并留悬念。"""
    fig.setdefault("hair", "short")
    return Shot(2, text, "先说结论", [Fig(540, GROUND_Y, 330, at=0, pose=pose, mood=mood, **fig),
                                     Icon(icon, 760, 520, 110, color=K.RED if icon == "question" else K.GOLD, at=1, sfx="rim"),
                                     Spark(760, 520, at=1)], draw=ground, text_beat=0, note="一句话点题")


def drop(concept, sub, text, size=180):
    """17.14 秒音乐 drop：概念名砸下，光束 + 光晕 + 扫光 + 星光 + 闪白 + 抖动。"""
    return Shot(4, text, "原书 · 核心概念", [Big(concept, 540, 700, size, at=0, sfx="kick", sub=sub, rays=True, glow=True,
                                                  shine=True, spark=True, note="概念落版（音乐 drop）")],
                punch=0.035, flashes=[0], shake=[0], note="drop 处概念砸下")


def line(words, size=96, flash=6, gap=26):
    """金句：纯逐词弹出，字幕留空。"""
    return Shot(4, "", "一句话", [Glow(540, 780, 560, at=0, alpha=0.26), Pops(words, 540, 780, size, at=0, step=1, gap=gap)],
                punch=0.02, flashes=[flash], note="金句逐词弹出")


def slam(word, text, tag="原书 · 大意", size=160):
    """2 小节重击：一个词砸下。"""
    return Shot(2, text, tag, [Big(word, 540, 760, size, at=0, sfx="kick", glow=True)], text_beat=0, punch=0.03,
                shake=[0], note=f"{word}砸下")


def doubt(text, tag="常见质疑", icon="scale"):
    """质疑与边界。"""
    return Shot(4, text, tag, [Icon(icon, 540, 720, 230, color=K.INK2, at=0, sfx="wood_low"),
                               Icon("question", 780, 560, 100, color=K.RED, at=4, sfx="rim")], note="质疑与边界")


def tip(text, tag="小练习", pose="cheer", **fig):
    """回报：今晚就能做的小动作。"""
    fig.setdefault("hair", "short")
    return Shot(2, text, tag, [Rays(540, 760, 520, at=0, alpha=0.18),
                               Fig(540, GROUND_Y, 330, at=0, pose=pose, mood="happy", **fig),
                               Spark(540, 560, at=1, sfx="clap")], draw=ground, text_beat=0, punch=0.02, note="回报")


def episode(no, key, concept, title, acc, shots, refs, cover_title, notes, tags="", land_shot=2, beat_punch=0.0) -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"人类简史 · {concept}",
                   cover_shot=3, cover_t=1.6, notes=notes, land_shot=land_shot, beat_punch=beat_punch).build()


# 重做版骨架镜头（与《稀缺》重做版相同）：互动提问 · 倒计时游戏 · 揭晓 | drop · 机制 · 机制 | 证据×3 · 重击 | 第一招 · 第二招 · 片尾
from scarcity.common import ask, slam as slam2, tip2  # noqa: E402,F401
from scarcity.common import drop as drop2  # noqa: E402,F401


def redo(no, key, concept, title, acc, shots, refs, cover_title, notes, tags="") -> Episode:
    """重做版：开启节拍推镜，横屏封面取第 3 镜（游戏揭晓）。"""
    return episode(no, key, concept, title, acc, shots, refs, cover_title, notes, tags, land_shot=2, beat_punch=0.022)
