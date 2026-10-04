"""用 Pillow 逐帧绘制讲解动画，通过管道交给 FFmpeg 编码为 MP4。

用法：python3 dyl_video.py [输出路径]
"""

import subprocess
import sys
from dataclasses import dataclass
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FPS = 30
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

BG = (250, 246, 238)
INK = (34, 40, 49)
MUTED = (120, 124, 130)
ACCENT = (214, 93, 57)
COLORS = [(214, 93, 57), (56, 132, 160), (97, 155, 90), (226, 170, 60), (140, 98, 170)]

_font_cache: dict[int, ImageFont.FreeTypeFont] = {}


def font(size: int) -> ImageFont.FreeTypeFont:
    """按字号缓存字体对象，避免每帧重复加载。"""
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(FONT_PATH, size)
    return _font_cache[size]


def ease(x: float) -> float:
    """三次缓出，输入会被截断到 [0, 1]。"""
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def mix(c1: tuple, c2: tuple, a: float) -> tuple:
    """在两种颜色间线性插值，用于在纯色背景上模拟透明度。"""
    return tuple(int(p + (q - p) * a) for p, q in zip(c1, c2))


def appear(t: float, start: float, dur: float = 0.6) -> float:
    """返回元素从 start 秒开始、持续 dur 秒的入场进度。"""
    return ease((t - start) / dur)


def text(d: ImageDraw.ImageDraw, xy, s: str, size: int, color, a: float = 1.0,
         anchor: str = "la", rise: int = 30):
    """绘制带淡入与上浮效果的文字；a 为入场进度。"""
    if a <= 0:
        return
    x, y = xy
    d.text((x, y + (1 - a) * rise), s, font=font(size), fill=mix(BG, color, a), anchor=anchor)


@dataclass
class Scene:
    duration: float
    draw: Callable[[ImageDraw.ImageDraw, float], None]


def header(d, t, kicker: str, title: str):
    """场景通用标题：小标签 + 大标题 + 强调色短横线。"""
    text(d, (160, 130), kicker, 34, ACCENT, appear(t, 0.0))
    text(d, (160, 185), title, 76, INK, appear(t, 0.15))
    w = 120 * appear(t, 0.4)
    if w > 0:
        d.rectangle([160, 300, 160 + w, 308], fill=ACCENT)


def scene_title(d, t):
    a = appear(t, 0.2, 0.9)
    text(d, (W // 2, 380), "设计你的人生", 130, INK, a, "mm")
    text(d, (W // 2, 500), "Designing Your Life", 56, ACCENT, appear(t, 0.7), "mm")
    w = 360 * appear(t, 1.1)
    if w > 0:
        d.rectangle([W // 2 - w / 2, 570, W // 2 + w / 2, 576], fill=ACCENT)
    text(d, (W // 2, 650), "Stanford Life Design Lab · Bill Burnett & Dave Evans", 36, MUTED,
         appear(t, 1.4), "mm")


def scene_idea(d, t):
    header(d, t, "核心观点", "人生不是一道等待解开的题")
    text(d, (160, 420), "而是一件可以被设计的作品。", 60, INK, appear(t, 1.0))
    text(d, (160, 540), "像设计师一样：先理解自己，再大胆构想，", 44, MUTED, appear(t, 2.0))
    text(d, (160, 610), "然后做原型、去测试、不断迭代。", 44, MUTED, appear(t, 2.6))


def scene_mindsets(d, t):
    header(d, t, "五种设计思维", "Designer Mindsets")
    items = [("好奇心", "Curiosity", "对一切保持好奇"),
             ("行动导向", "Bias to Action", "先动手，别只空想"),
             ("重新定义问题", "Reframing", "换个问法，答案就变了"),
             ("觉察过程", "Awareness", "设计是一个过程，接受混乱"),
             ("深度合作", "Radical Collaboration", "寻求他人的帮助")]
    for i, (zh, en, desc) in enumerate(items):
        a = appear(t, 0.9 + i * 0.9)
        if a <= 0:
            continue
        y = 380 + i * 128
        r = 30 * a
        d.ellipse([190 - r, y + 30 - r, 190 + r, y + 30 + r], fill=COLORS[i])
        d.text((190, y + 30), str(i + 1), font=font(32), fill=BG, anchor="mm")
        text(d, (250, y), zh, 52, INK, a, rise=0)
        text(d, (620, y + 12), en, 34, COLORS[i], a, rise=0)
        text(d, (1080, y + 12), desc, 36, MUTED, a, rise=0)


def scene_journal(d, t):
    header(d, t, "工具一", "好时光日志 Good Time Journal")
    text(d, (160, 360), "每天记录：做了什么？有多投入？精力是增加还是消耗？", 40, MUTED, appear(t, 0.8))
    rows = [("带新人做项目", 0.9, 0.8), ("写周报", 0.3, -0.6), ("调试视觉算法", 0.85, 0.5),
            ("开跨部门会议", 0.35, -0.4), ("周末徒步", 0.8, 0.9)]
    text(d, (760, 450), "投入度", 32, INK, appear(t, 1.2), "ma")
    text(d, (1420, 450), "精力", 32, INK, appear(t, 1.2), "ma")
    for i, (name, engage, energy) in enumerate(rows):
        start = 1.5 + i * 0.5
        a = appear(t, start)
        if a <= 0:
            continue
        y = 520 + i * 90
        text(d, (160, y), name, 40, INK, a, rise=0)
        grow = appear(t, start + 0.2, 1.0)
        d.rectangle([520, y + 8, 1000, y + 44], fill=mix(BG, (225, 220, 210), a))
        d.rectangle([520, y + 8, 520 + 480 * engage * grow, y + 44], fill=COLORS[1])
        cx = 1420
        d.line([cx, y, cx, y + 52], fill=mix(BG, MUTED, a), width=3)
        color = COLORS[2] if energy > 0 else ACCENT
        end = cx + 280 * energy * grow
        d.rectangle([min(cx, end), y + 8, max(cx, end), y + 44], fill=color)
    text(d, (160, 990), "→ 找出让你投入、让你充电的事，那就是线索。", 40, ACCENT, appear(t, 5.0))


def scene_odyssey(d, t):
    header(d, t, "工具二", "奥德赛计划 Odyssey Plans")
    text(d, (160, 360), "为未来五年画出三种完全不同的人生版本：", 40, MUTED, appear(t, 0.8))
    plans = [("版本 A", "当前路径", "沿着现在的方向\n继续走下去"),
             ("版本 B", "备选人生", "如果现在这条路\n突然消失了"),
             ("版本 C", "疯狂想法", "如果钱和面子\n都不是问题")]
    for i, (tag, name, desc) in enumerate(plans):
        a = appear(t, 1.6 + i * 1.0, 0.8)
        if a <= 0:
            continue
        x = 160 + i * 540
        y = 470 + (1 - a) * 60
        d.rounded_rectangle([x, y, x + 480, y + 440], radius=28,
                            fill=mix(BG, (255, 255, 255), a), outline=mix(BG, COLORS[i], a), width=4)
        d.rectangle([x, y, x + 480, y + 16], fill=mix(BG, COLORS[i], a))
        d.text((x + 40, y + 60), tag, font=font(34), fill=mix(BG, COLORS[i], a))
        d.text((x + 40, y + 120), name, font=font(60), fill=mix(BG, INK, a))
        d.multiline_text((x + 40, y + 240), desc, font=font(40), fill=mix(BG, MUTED, a), spacing=20)


def scene_prototype(d, t):
    header(d, t, "工具三", "做原型，而不是空想")
    pairs = [("原型对话", "找正在过那种生活的人聊一聊，听真实故事"),
             ("原型体验", "花一天、一周去亲身试一试，代价很小")]
    for i, (name, desc) in enumerate(pairs):
        a = appear(t, 0.9 + i * 1.2)
        y = 420 + i * 170
        if a > 0:
            d.rectangle([160, y, 172, y + 110], fill=mix(BG, COLORS[i + 1], a))
        text(d, (210, y), name, 56, INK, a)
        text(d, (210, y + 72), desc, 38, MUTED, a)
    text(d, (160, 840), "低成本试错，用真实数据代替想象。", 48, ACCENT, appear(t, 3.4))


def scene_end(d, t):
    text(d, (W // 2, 420), "人生没有唯一正确答案", 84, INK, appear(t, 0.3, 0.9), "mm")
    text(d, (W // 2, 540), "只有不断迭代的版本", 84, ACCENT, appear(t, 1.2, 0.9), "mm")
    text(d, (W // 2, 760), "参考：《Designing Your Life》 Bill Burnett & Dave Evans", 34, MUTED,
         appear(t, 2.4), "mm")


SCENES = [
    Scene(4.5, scene_title),
    Scene(6.0, scene_idea),
    Scene(7.5, scene_mindsets),
    Scene(7.5, scene_journal),
    Scene(7.0, scene_odyssey),
    Scene(6.0, scene_prototype),
    Scene(5.0, scene_end),
]

FADE = 0.4


def render_frame(scene: Scene, t: float) -> bytes:
    """渲染单帧；场景首尾各 FADE 秒与背景色交叉淡化。"""
    img = Image.new("RGB", (W, H), BG)
    scene.draw(ImageDraw.Draw(img), t)
    fade = min(t / FADE, (scene.duration - t) / FADE, 1.0)
    if fade < 1.0:
        img = Image.blend(Image.new("RGB", (W, H), BG), img, max(fade, 0.0))
    return img.tobytes()


def main(out_path: str):
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for scene in SCENES:
            for i in range(int(scene.duration * FPS)):
                proc.stdin.write(render_frame(scene, i / FPS))
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")
    print(f"written: {out_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "designing_your_life.mp4")
