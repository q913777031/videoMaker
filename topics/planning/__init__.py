"""题材：《说好周五交，为什么又拖到下周》（计划谬误，Buehler、Griffin、Ross 1994）。"""

from kepu.topic import Topic

from .scenes import SCENES, office
from .shots import shots

REFERENCES = """参考资料

Roger Buehler, Dale Griffin, Michael Ross (1994).
Exploring the "planning fallacy": Why people underestimate their task completion times.
Journal of Personality and Social Psychology, 67(3), 366–381.
DOI: 10.1037/0022-3514.67.3.366

核验范围
- 制作环境的网络策略拒绝直接访问 APA、doi.org 等站点；书目信息与以下结论经网络搜索结果（论文 PDF 摘要片段、
  学会博客等）核对，未通读全文。
- 片中使用的结论仅限：人们对任务完成时间的预测偏乐观，学业与非学业任务都出现；预测时人们更多设想未来情景，
  较少使用相关的过往经验；研究 4 中被要求把相关过往经验与预测联系起来的参与者，乐观偏差消失。
- 未核验、未进片：荣誉论文实验的具体天数与比例（只见于二手转述）。
- 镜头 07 中各条长度只是“实际长于预测”的示意，不代表论文数据；片中办公场景为情境演绎。
- 年份 1994 为文献发表年份。“翻看上次记录 / 预留空白”属于反思练习，不是验证理论的实验，也不替代专业帮助。
"""


def _cover(c, view):
    """截止旗已被任务卡远远甩在身后。"""
    office(c, 1.0, view, flag=0.45, card=0.78, bar_end=0.82, slump=1.0)


TOPIC = Topic(
    slug="planning",
    title="《说好周五交，为什么又拖到下周》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("这次一定，", "能按时做完？"),
    cover_subtitle="你估的时间，为什么总不够",
    publish_title="《说好周五交，为什么每次都拖到下周？》",
    hashtags="#知识科普 #心理学 #计划谬误 #拖延 #上班族",
    references=REFERENCES,
)
