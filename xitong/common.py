"""《系统之美》系列共用：快节奏镜头模板（沿用《资治通鉴》《毛选》）、片尾与 Episode 构造。"""

from adler.core import Episode
from maoxuan.common import outro  # noqa: F401
from zizhi.common import S, pops  # noqa: F401

BOOK = "德内拉·梅多斯《系统之美》（Thinking in Systems）"
TAGS = "#系统之美 #系统思考 #读书 #思维模型 #职场"


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"系统之美 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()
