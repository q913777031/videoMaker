"""《亲密关系》10 讲共用：沿用 sapiens.common 的留存骨架镜头模板，只换书目、话题与封面副标题。"""

from adler.core import Episode
from sapiens.common import doubt, drop, hook, line, loop, slam, tip  # noqa: F401

BOOK = "Miller, R. S. Intimate Relationships（《亲密关系》）."
TAGS = "#亲密关系 #恋爱心理学 #心理学 #读书 #情侣"


def episode(no, key, concept, title, acc, shots, refs, cover_title, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"亲密关系 · {concept}",
                   cover_shot=3, cover_t=1.6, notes=notes).build()
