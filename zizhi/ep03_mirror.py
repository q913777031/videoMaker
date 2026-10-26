"""03：节拍表见 zizhi/specs.py，构造器见 zizhi/story.py。"""

from .specs import EPS
from .story import build_episode


def build():
    nxt = EPS.get("04")
    return build_episode(EPS["03"], f"{nxt['no']:02d} {nxt['title']}" if nxt else "END")
