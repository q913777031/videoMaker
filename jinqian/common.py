"""《金钱心理学》系列共用：Episode 构造。"""

from adler.core import Episode

BOOK = "摩根·豪泽尔《金钱心理学》（The Psychology of Money）"
TAGS = "#金钱心理学 #理财 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"金钱心理学 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()
