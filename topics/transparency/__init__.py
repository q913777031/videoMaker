"""题材：《紧张的时候，别人真能一眼看穿吗》（透明度错觉，Gilovich、Savitsky、Medvec 1998）。"""

from kepu.topic import Topic

from .scenes import SCENES, interview
from .shots import shots

REFERENCES = """参考资料

Thomas Gilovich, Kenneth Savitsky, Victoria Husted Medvec (1998).
The illusion of transparency: Biased assessments of others' ability to read one's emotional states.
Journal of Personality and Social Psychology, 75(2), 332–346.

核验范围
- 制作环境的网络策略拒绝直接访问 APA、doi.org 等站点；书目信息与以下结论经网络搜索结果（学术机构文献页、
  综述与百科条目）核对，未读到摘要原文与全文。
- 片中使用的结论仅限：人们倾向于高估自己的内心状态（想法、感受）被他人看出的程度，即“透明度错觉”。
- 未核验、未进片：各子研究的具体程序与比例（如说谎实验中“自认被识破”与“实际被识破”的比例，只见于二手转述）。
- 片中面试场景为情境演绎；镜头 07 两框中心形的亮度只是“自己以为更明显”的示意，不代表论文数据。
- 本片不主张“别人完全看不出你紧张”。“先问证据 / 把注意力放回问题”属于反思练习，不替代专业帮助。
- 年份 1998 为文献发表年份。
"""


def _cover(c, view):
    """面试桌前，一个人觉得自己是透明的玻璃，心跳一览无余。"""
    interview(c, 0.0, view, glass=1.0, heart_k=1.0, storm=1.0)


TOPIC = Topic(
    slug="transparency",
    title="《紧张的时候，别人真能一眼看穿吗》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("紧张的时候，", "全写在脸上？"),
    cover_subtitle="你以为的透明，别人未必看见",
    publish_title="《面试时紧张到心跳加速，别人真能一眼看穿吗？》",
    hashtags="#知识科普 #心理学 #透明度错觉 #面试 #上班族",
    references=REFERENCES,
)
