"""题材：《会上说错一句话，为什么觉得全场都记住了》（聚光灯效应，Gilovich、Medvec、Savitsky 2000）。"""

from kepu.topic import Topic

from .scenes import SCENES, meeting
from .shots import shots

REFERENCES = """参考资料

Thomas Gilovich, Victoria Husted Medvec, Kenneth Savitsky (2000).
The spotlight effect in social judgment: An egocentric bias in estimates of the salience of one's own actions
and appearance. Journal of Personality and Social Psychology, 78(2), 211–222.
DOI: 10.1037/0022-3514.78.2.211

核验范围
- 制作环境的网络策略拒绝直接访问 APA PsycNet、doi.org、PubMed、Semantic Scholar 等站点；书目信息与以下结论
  经网络搜索结果（Semantic Scholar 摘要概述、学术机构的文献列表页）核对，未读到摘要原文与全文。
- 片中使用的结论仅限：人们高估自己的行为和外表被他人注意的程度（“聚光灯效应”）；研究 1、2 中，穿印有讨好或
  可能令人尴尬图像 T 恤的参与者，高估了能回忆出 T 恤图案的观察者人数；作者的后续研究支持“锚定于自身体验、
  向他人视角调整不足”的解释。
- 未核验、未进片：具体比例（“约两倍”“一半对四分之一”只见于博客转述）、会议讨论子研究的细节、研究总数。
- 镜头 07 左右两框亮起的人数只是“估计多于实际”的示意，不代表论文数据。
- 片中会议场景为情境演绎，不是论文中的实验；本片不主张“别人根本不会注意你”，也不主张出错没有后果。
- 年份 2000 为文献发表年份。片中“谁真的会记住 / 补一句更正”属于反思练习，不是验证理论的实验，也不替代专业帮助。
"""


def _cover(c, view):
    """会议桌旁，一束巨大的聚光灯只照着一个人。"""
    meeting(c, 0, view, look=1.0, lit=0.15, beam_k=1.0, beam_w=420)


TOPIC = Topic(
    slug="spotlight",
    title="《会上说错一句话，为什么觉得全场都记住了》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("说错一句话，", "全场都记住了？"),
    cover_subtitle="那束光，其实没那么亮",
    publish_title="《会上说错一句话，真的所有人都记得吗？》",
    hashtags="#知识科普 #心理学 #聚光灯效应 #职场 #上班族",
    references=REFERENCES,
)
