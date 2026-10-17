"""题材：《外卖翻了半小时，为什么还是点不下去》（选择过载：Iyengar 与 Lepper 2000；Scheibehenne 等 2010 元分析）。"""

from kepu.topic import Topic

from .scenes import SCENES, couch
from .shots import shots

REFERENCES = """参考资料

Sheena S. Iyengar, Mark R. Lepper (2000).
When choice is demotivating: Can one desire too much of a good thing?
Journal of Personality and Social Psychology, 79(6), 995–1006.

Benjamin Scheibehenne, Rainer Greifeneder, Peter M. Todd (2010).
Can there ever be too many options? A meta-analytic review of choice overload.
Journal of Consumer Research, 37(3), 409–425.
DOI: 10.1086/651235

核验范围
- 制作环境的网络策略拒绝直接访问期刊与数据库站点；书目信息与以下结论经网络搜索结果（论文摘要、学会与大学页面）
  核对，未通读全文。
- 片中使用的结论仅限：Iyengar 与 Lepper (2000) 发现，在高档超市的果酱试吃摊，摆出 6 种时比摆出 24 种时顾客更可能购买；
  在巧克力与选做作文作业中，有限的 6 个选项比 24 或 30 个选项更可能让人行动。Scheibehenne 等 (2010) 汇总 50 个实验
  （63 个条件、5036 名参与者）的元分析发现，选择过载的平均效应接近零，但不同研究之间差异很大；找到一些可能的前提条件，
  但没有找到充分条件。
- 本片因此不主张“选项多一定让人选不出”。未核验、未进片：果酱实验的具体购买比例与人数。
- 镜头 07 购物袋的多少只是“更可能购买”的示意；镜头 09–10 的散点只是“平均接近零、差异很大”的示意，不代表真实数据。
- “先定标准 / 差不多好就下单”属于反思练习，不替代专业帮助。年份为文献发表年份。
"""


def _cover(c, view):
    """手机里的店铺卡片无穷无尽，人卡在沙发上。"""
    couch(c, 1.0, view, n=24, scroll=0.4)


TOPIC = Topic(
    slug="choice",
    title="《外卖翻了半小时，为什么还是点不下去》",
    shots=shots,
    scenes=SCENES,
    cover_scene=_cover,
    cover_title=("翻了半小时，", "还是点不下去？"),
    cover_subtitle="选项多，未必就是问题",
    publish_title="《外卖翻了半小时还是点不下去？选项太多真的会让人选不出吗》",
    hashtags="#知识科普 #心理学 #选择过载 #决策 #上班族",
    references=REFERENCES,
    motion="max",
)
