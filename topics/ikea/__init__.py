"""题材：《自己做的方案，为什么怎么看都比别人好》（宜家效应，Norton、Mochon、Ariely 2012）。"""

from kepu.topic import Topic

from .scenes import SCENES, studio
from .shots import shots

REFERENCES = """参考资料

Michael I. Norton, Daniel Mochon, Dan Ariely (2012).
The IKEA effect: When labor leads to love.
Journal of Consumer Psychology, 22(3), 453–460.
DOI: 10.1016/j.jcps.2011.08.002

核验范围
- 制作环境的网络策略拒绝直接访问出版社与数据库站点；书目信息与以下结论经网络搜索结果（作者机构公开的摘要、
  文献数据库条目）核对，未通读全文。
- 片中使用的结论仅限：在组装宜家家具、折纸、拼乐高的研究中，人们对自己动手做的产品估价更高（“宜家效应”）；
  参与者认为自己业余的作品与专家作品价值相近，并以为别人也会这么看；只有劳动带来完成，才会带来喜爱，
  亲手做的东西被拆掉或没有做完时，这份加成消失；这一效应在 DIY 爱好者和新手中都出现。
- 未核验、未进片：各研究的具体估价数值。
- 片中价签与价值条的高度只是“估价更高”的示意，不代表论文数据；加班做方案为情境演绎。
- “请没参与的人打分 / 把付出与质量分开看”属于反思练习，不替代专业帮助。年份 2012 为文献发表年份。
"""


def _cover(c, view):
    """自己的方案被金色光环笼罩，价签高高顶起。"""
    studio(c, 0.0, view, halo=1.0, value=0.9)


TOPIC = Topic(
    slug="ikea",
    title="《自己做的方案，为什么怎么看都比别人好》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("自己做的，", "就是最好的？"),
    cover_subtitle="付出会变成喜爱，也会遮住眼睛",
    publish_title="《自己熬夜做的方案，为什么怎么看都比别人的好？》",
    hashtags="#知识科普 #心理学 #宜家效应 #职场 #上班族",
    references=REFERENCES,
    motion="max",
)
