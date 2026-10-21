"""《稀缺》8 讲共用：品牌标题、参考资料、Episode 构造。"""

from adler.core import Episode

BRAND = "Vibe知识大赏"
BOOK = "Mullainathan & Shafir (2013). Scarcity: Why Having Too Little Means So Much."
TAGS = "#稀缺 #行为经济学 #心理学 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, notes, tags="", land_shot=2) -> Episode:
    """统一发布标题（Vibe知识大赏｜片名）、话题与封面取景（drop 镜头）。"""
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"{BRAND}｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"稀缺 · {concept}",
                   cover_shot=3, cover_t=1.6, notes=notes, land_shot=land_shot).build()
