"""题材：《升职了，为什么反而觉得自己是混进来的》（冒名顶替现象，Clance 与 Imes 1978）。"""

from kepu.topic import Topic

from .scenes import SCENES, podium
from .shots import shots

REFERENCES = """参考资料

Pauline Rose Clance, Suzanne Ament Imes (1978).
The imposter phenomenon in high achieving women: Dynamics and therapeutic intervention.
Psychotherapy: Theory, Research & Practice, 15(3), 241–247.

核验范围
- 制作环境的网络策略拒绝直接访问 APA 与作者网站；书目信息与以下结论经网络搜索结果（作者网站 PDF 摘要、
  学术文献的引用描述）核对，未通读全文。
- 片中使用的结论仅限：作者用“冒名顶替现象”指一种觉得自己在智识上是冒牌货的内在体验，在一群高成就女性中
  观察到；尽管学业与职业成绩出色，她们仍坚信自己并不聪明、骗过了认为她们聪明的人。
- 该文基于作者的临床观察，没有量化数据；作者用“现象”而非“综合征”，本片不把它当作疾病诊断。
- 片中“成绩归给运气、底气攒不下来”是对这种体验的机制示意，不是论文的实验结论；“列三件事 / 分两栏记录”
  属于反思练习，不替代专业帮助。
- 片中人物为中性外形的示意角色；年份 1978 为文献发表年份。
"""


def _cover(c, view):
    """站在高高的卡片台座上，却觉得脚下全是纸板空壳。"""
    podium(c, 1.0, view, n=6, hollow=1.0, pose_k=1.0, badge=1.0)


TOPIC = Topic(
    slug="impostor",
    title="《升职了，为什么反而觉得自己是混进来的》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("升职了，", "却怕被拆穿？"),
    cover_subtitle="脚下每一层，都是你自己搭的",
    publish_title="《升职以后，总觉得自己是混进来的？》",
    hashtags="#知识科普 #心理学 #冒名顶替现象 #职场 #上班族",
    references=REFERENCES,
)
