"""题材描述：一条片子 = 镜头表 + 场景绘制 + 封面与发布文案 + 参考资料。引擎只通过 Topic 读取题材内容。"""

import importlib
from dataclasses import dataclass
from typing import Callable

from .config import Shot


@dataclass
class Topic:
    slug: str                                  # 输出文件名前缀，如 night → night_vertical.mp4
    title: str                                 # 片名（逐屏文案标题）
    shots: Callable[[], list[Shot]]            # 返回叙事基准镜头表（每次调用返回新对象）
    scenes: dict[int, Callable]                # 镜头号 → 场景函数 (c, t, D, cue, view)
    cover_scene: Callable                      # (c, view) 在舞台坐标上画封面主体
    cover_title: tuple[str, ...]               # 封面主标题，一到两行
    cover_subtitle: str
    publish_title: str
    hashtags: str
    references: str                            # references.txt 全文（书目 + 核验范围）
    post_cues: Callable | None = None          # (cues, shots) 跨镜头衔接参数，例如承接上一镜的运动相位


def load(slug: str) -> Topic:
    """按名称加载 topics/<slug>/__init__.py 中的 TOPIC；找不到时抛出 ModuleNotFoundError。"""
    return importlib.import_module(f"topics.{slug}").TOPIC
