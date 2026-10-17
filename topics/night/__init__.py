"""题材：《为什么一到晚上，就觉得自己的人生不行了》（反刍与反思，参考 Nolen-Hoeksema 等 2008 综述）。"""

from kepu import props
from kepu.topic import Topic

from .scenes import SCENES
from .shots import shots

REFERENCES = """参考资料

Susan Nolen-Hoeksema, Blair E. Wisco, Sonja Lyubomirsky (2008).
Rethinking Rumination. Perspectives on Psychological Science, 3(5), 400–424.
DOI: 10.1111/j.1745-6924.2008.00088.x
期刊学会页面：https://www.psychologicalscience.org/journals/perspectives/j.1745-6924.2008.00088.x
论文摘要：https://pubmed.ncbi.nlm.nih.gov/26158958/

核验范围
- 本片依据制作提示词所附的书目信息与摘要范围制作。
- 制作环境的网络策略拒绝访问 PubMed、Crossref 等文献站点，本次未能在线复核摘要原文，也未查阅全文，
  未补充任何实验程序、样本或数据细节。
- 片中使用的结论仅限：该综述讨论反刍与负面思考、问题解决等的关系，并区分反刍与更有适应性的自我反思。
- 该综述不是专门验证“夜晚人生崩溃”的实验；片中“夜晚”只是故事场景，不主张夜间自我否定均由反刍造成。
- 年份 2008 为文献发表年份，不代表现象首次出现的年份。
- 片中的“写下事实 / 下一步”属于改编的反思练习工具，不是验证理论的正式实验，也不替代专业帮助。
"""


def _cover(c, view):
    """床边一张小卡片投射出巨大的城市阴影。"""
    props.bedroom(c, 0, view, 3.3, city=1.0, card_rot=-12)


def _post_cues(cues, sh):
    """镜头 05 的轨道承接镜头 04 结尾的角度：注入镜头 04 结束时距其首圈的时间。"""
    cues[5]["_t4"] = sh[3].dur - cues[4]["lap"]


TOPIC = Topic(
    slug="night",
    title="《为什么一到晚上，就觉得自己的人生不行了》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("一到晚上，", "就否定人生？"),
    cover_subtitle="一件小事，怎么变成全部",
    publish_title="《白天还能上班，晚上却觉得整个人生都不行？》",
    hashtags="#知识科普 #心理学 #反刍思维 #自我评价 #上班族",
    references=REFERENCES,
    post_cues=_post_cues,
)
