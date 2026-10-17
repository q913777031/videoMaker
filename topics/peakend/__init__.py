"""题材：《忙了一整周，为什么只记得最崩的那晚》（峰终定律，Kahneman、Fredrickson、Schreiber、Redelmeier 1993）。"""

from kepu.topic import Topic

from .scenes import SCENES, week
from .shots import shots

REFERENCES = """参考资料

Daniel Kahneman, Barbara L. Fredrickson, Charles A. Schreiber, Donald A. Redelmeier (1993).
When more pain is preferred to less: Adding a better end.
Psychological Science, 4(6), 401–405.
DOI: 10.1111/j.1467-9280.1993.tb00589.x

核验范围
- 制作环境的网络策略拒绝直接访问期刊与数据库站点；书目信息与以下结论经网络搜索结果（期刊学会页面摘要、
  公开的论文 PDF 信息）核对，未通读全文。
- 片中使用的结论仅限：参与者一次把手放进 14℃ 冷水 60 秒；另一次同样 60 秒后再继续 30 秒，期间水温升到 15℃，
  仍然难受但程度减轻；之后让参与者选择重复哪一次，多数人选了更长的那一次；作者据此认为，时长对不愉快经历的
  回顾评价影响很小，评价主要受最难受的时刻和结尾左右。
- 未核验、未进片：选择更长一次的具体比例（只见于二手转述）。
- “峰终定律”是对这一结论的通用称呼；本片不主张时长对当下的实际感受不重要。加班一周的曲线为情境演绎，不代表数据。
- “数数顺利的日子 / 留个好结尾”属于反思练习，不替代专业帮助。年份 1993 为文献发表年份。
"""


def _cover(c, view):
    """一整周的体验曲线，只有最低点被记忆卡拍下。"""
    week(c, 0.0, view, snap_k=1.0)


TOPIC = Topic(
    slug="peakend",
    title="《忙了一整周，为什么只记得最崩的那晚》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("一整周，", "只记得那一晚？"),
    cover_subtitle="回忆会挑重点，也会漏掉很多",
    publish_title="《忙了一整周，为什么只记得最崩溃的那晚？》",
    hashtags="#知识科普 #心理学 #峰终定律 #记忆 #上班族",
    references=REFERENCES,
    motion="max",
)
