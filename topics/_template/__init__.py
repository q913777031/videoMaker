"""题材模板：复制为 topics/<slug>/ 后修改。片名、封面与发布文案、参考资料全部来自提示词原文。"""

from kepu import props
from kepu.topic import Topic

from .scenes import SCENES
from .shots import shots

REFERENCES = """参考资料

作者 (年份). 英文题名. 期刊, 卷(期), 页码.
DOI: 
论文摘要：

核验范围
- 写明实际核验到的范围（书目 / 摘要 / 全文），以及没能访问的站点。
- 写明片中允许使用的结论，以及明确不主张的延伸。
- 年份为文献发表年份，不代表现象首次出现的年份。
"""


def _cover(c, view):
    """封面主体：一个鲜明主体 + 一个视觉矛盾。"""
    props.bedroom(c, 0, view, 3.3, city=1.0, card_rot=-12)


TOPIC = Topic(
    slug="template",
    title="《片名》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("封面主标题，", "第二行？"),
    cover_subtitle="副标题单独一行",
    publish_title="《发布标题》",
    hashtags="#知识科普",
    references=REFERENCES,
)
