"""《身份的焦虑》系列共用：Episode 构造。"""

from adler.core import Episode

BOOK = "阿兰·德波顿《身份的焦虑》（Status Anxiety）"
TAGS = "#身份的焦虑 #焦虑 #德波顿 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"身份的焦虑 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()
