"""《孤独是可耻的》系列共用：Episode 构造。"""

from adler.core import Episode

BOOK = "约翰·卡乔波、威廉·帕特里克《孤独是可耻的》（Loneliness: Human Nature and the Need for Social Connection）"
TAGS = "#孤独是可耻的 #孤独 #心理学 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"孤独是可耻的 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()
