"""题材：《聊完天，为什么总觉得对方不太喜欢自己》（喜欢差距，Boothby、Cooney、Sandstrom、Clark 2018）。"""

from kepu.topic import Topic

from .scenes import SCENES, cafe
from .shots import shots

REFERENCES = """参考资料

Erica J. Boothby, Gus Cooney, Gillian M. Sandstrom, Margaret S. Clark (2018).
The liking gap in conversations: Do people like us more than we think?
Psychological Science, 29(11), 1742–1756.
DOI: 10.1177/0956797618783714

核验范围
- 制作环境的网络策略拒绝直接访问 SAGE、APS 等站点；书目信息与以下结论经网络搜索结果（期刊与学会页面的摘要、
  作者机构公开的 PDF 信息）核对，未通读全文。
- 片中使用的结论仅限：对话结束后，人们系统性地低估了对方有多喜欢自己、多享受与自己相处，作者称之为“喜欢差距”；
  这一差距出现在实验室里的陌生人、刚认识的大一室友、个人成长工作坊的参与者中；在不同长度的对话中都存在，
  并在室友关系中持续了数月。
- 未核验、未进片：旁观者评价等细节（只见于二手转述）、各研究的具体数值。
- 片中罐子的液面高低只是“低估”的示意，不代表论文数据；咖啡馆与回家复盘为情境演绎。
- “回想对方的反应 / 记下对方的回应”属于反思练习，不替代专业帮助。年份 2018 为文献发表年份。
"""


def _cover(c, view):
    """两人对坐，一人头顶的光罐几乎是空的。"""
    cafe(c, 0.0, view, guess=0.15, bubble=1.0)


TOPIC = Topic(
    slug="liking",
    title="《聊完天，为什么总觉得对方不太喜欢自己》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("聊完天，", "对方嫌我无聊？"),
    cover_subtitle="别人可能比你以为的更喜欢你",
    publish_title="《聊完天总在复盘，觉得对方不太喜欢自己？》",
    hashtags="#知识科普 #心理学 #喜欢差距 #社交 #上班族",
    references=REFERENCES,
)
