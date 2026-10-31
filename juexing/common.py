"""《认知觉醒》系列共用：Episode 构造。"""

from adler.core import Episode

BOOK = "周岭《认知觉醒：开启自我改变的原动力》（人民邮电出版社 2020）"
TAGS = "#认知觉醒 #自我成长 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"认知觉醒 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()
