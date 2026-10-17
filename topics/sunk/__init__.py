"""题材：《项目明明没希望，为什么还舍不得停》（沉没成本效应，Arkes 与 Blumer 1985）。"""

from kepu.topic import Topic

from .scenes import SCENES, yard
from .shots import shots

REFERENCES = """参考资料

Hal R. Arkes, Catherine Blumer (1985).
The psychology of sunk cost.
Organizational Behavior and Human Decision Processes, 35, 124–140.

核验范围
- 制作环境的网络策略拒绝直接访问出版社与数据库站点；书目信息与以下结论经网络搜索结果（论文 PDF 的摘要、
  课程与学术博客引用）核对，未通读全文。
- 片中使用的结论仅限（均见于摘要）：一旦在金钱、精力或时间上有了投入，人们更倾向于继续这件事（沉没成本效应）；
  作者给出的证据表明，其心理依据是不想显得浪费；在一项剧院季票实验中，最初为季票付钱更多的观众，在接下来 6 个月
  里去看的演出更多；有沉没成本的人比没有的人更高估同一项目成功的可能。
- 未核验、未进片：季票实验的具体票价、人数与场次（各二手来源说法不一）。
- 镜头 07 亮起的座位数只是“付得越多、去得越多”的示意，不代表论文数据；办公场景为情境演绎。
- “假如今天才开始 / 只比较接下来的代价与收获”属于反思练习，不替代专业帮助。年份 1985 为文献发表年份。
"""


def _cover(c, view):
    """人物背着高高的投入堆，前面是一堵墙。"""
    yard(c, 0.0, view, n=7, bar_k=0.85)


TOPIC = Topic(
    slug="sunk",
    title="《项目明明没希望，为什么还舍不得停》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("都投了这么多，", "现在停太亏？"),
    cover_subtitle="让你停不下的，可能是过去",
    publish_title="《项目明明没希望，为什么还舍不得停？》",
    hashtags="#知识科普 #心理学 #沉没成本 #职场 #上班族",
    references=REFERENCES,
    motion="max",
)
