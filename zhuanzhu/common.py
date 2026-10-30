"""《深度工作》系列共用：Episode 构造。"""

from adler.core import Episode

BOOK = "卡尔·纽波特《深度工作》（Deep Work: Rules for Focused Success in a Distracted World）"
TAGS = "#深度工作 #专注 #效率 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"深度工作 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()
