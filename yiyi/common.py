"""《活出生命的意义》系列共用：Episode 构造。"""

from adler.core import Episode

BOOK = "维克多·E·弗兰克尔《活出生命的意义》（Man's Search for Meaning）"
TAGS = "#活出生命的意义 #弗兰克尔 #心理学 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"活出生命的意义 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()
