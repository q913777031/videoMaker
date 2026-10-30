"""《拖延心理学》系列共用：Episode 构造。"""

from adler.core import Episode

BOOK = "简·博克、莱诺拉·袁《拖延心理学》（Procrastination: Why You Do It, What to Do About It Now）"
TAGS = "#拖延心理学 #拖延症 #心理学 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"拖延心理学 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()
