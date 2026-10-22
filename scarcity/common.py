"""《稀缺》8 讲共用：品牌标题、参考资料、Episode 构造。"""

from adler.core import Episode

BRAND = "Vibe知识大赏"
BOOK = "Mullainathan & Shafir (2013). Scarcity: Why Having Too Little Means So Much."
TAGS = "#稀缺 #行为经济学 #心理学 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, notes, tags="", land_shot=2) -> Episode:
    """统一发布标题（Vibe知识大赏｜片名）、话题与封面取景（drop 镜头）。"""
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"{BRAND}｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"稀缺 · {concept}",
                   cover_shot=3, cover_t=1.6, notes=notes, land_shot=land_shot, beat_punch=0.022).build()


# ---------------------------------------------------------------- 重做版留存骨架的固定镜头（见 ep01_mindset.py）
# 小节：互动提问 2 · 游戏进行 4 · 揭晓 2 | drop 4 · 机制 4 · 机制 4 | 证据 4 · 证据 4 · 证据 4 · 重击 2 | 第一招 4 · 第二招 2 · 片尾 2

from adler import kit as K  # noqa: E402
from adler.core import Big, Pops, Rays, Shot, Spark  # noqa: E402


def ask(words, els, hits=(), size=92, note="互动小游戏：抛出问题"):
    """0–4 秒：问题逐词砸出（上方），游戏道具同时登场（下方）。"""
    return Shot(2, "", "互动小游戏", [Pops(words, 540, 540, size, at=0, step=1)] + list(els),
                hits=[(0, "kick", 0.7, "开场")] + list(hits), punch=0.025, flashes=[0], note=note)


def drop(concept, sub, text, chips, size=170):
    """17.14 秒 drop：概念砸下（光束、光晕、扫光、星光），第 3 拍星光，第 6 拍起三个关键词逐个弹出。"""
    return Shot(4, text, "原书 · 核心概念", [
        Big(concept, 540, 600, size, at=0, sfx="kick", sub=sub, rays=True, glow=True, shine=True, spark=True,
            note="概念落版（音乐 drop）"),
        Spark(540, 600, at=3, sfx="wood_high"),
        Pops(chips, 540, 1000, 64, at=6, step=2, gap=30),
    ], punch=0.035, flashes=[0], shake=[0], note="drop：概念砸下，关键词弹出")


def slam(word, words, text):
    """2 小节重击：一个词砸下，第 3 拍起补一句短语。"""
    return Shot(2, text, "原书 · 大意", [Big(word, 540, 640, 200, at=0, sfx="kick", glow=True, spark=True),
                                       Pops(words, 540, 1000, 80, at=2, step=1)],
                text_beat=0, punch=0.03, shake=[0], note=f"{word}砸下")


def tip2(text, words, size=120):
    """第二招：口诀逐字砸出 + 光束 + 掌声星光。"""
    return Shot(2, text, "小方法", [Rays(540, 760, 520, at=0, alpha=0.2), Pops(words, 540, 760, size, at=0, step=1, gap=30),
                                   Spark(540, 760, at=5, sfx="clap")], text_beat=0, punch=0.025, note="第二招口诀")
