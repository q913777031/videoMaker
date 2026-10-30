"""《伯恩斯新情绪疗法》系列共用：Episode 构造。规划见 qingxu/PLAN.md。"""

from adler.core import Episode

BOOK = "戴维·伯恩斯《伯恩斯新情绪疗法》（Feeling Good: The New Mood Therapy），李亚萍译"
TAGS = "#伯恩斯新情绪疗法 #情绪 #认知行为疗法 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"新情绪疗法 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()
