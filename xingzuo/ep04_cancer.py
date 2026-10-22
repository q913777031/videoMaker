"""04 cancer：由通用 42 镜故事模板（xingzuo/story.py）与星座专属文案（xingzuo/specs.py）生成。"""

from .specs import SPECS
from .story import build_episode


def build():
    return build_episode("cancer", SPECS["cancer"])
