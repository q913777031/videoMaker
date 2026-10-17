"""黑金科普短片引擎的通用参数：帧率、采样率、配色、横竖屏排版，以及分镜（Shot）与候选事件（Cue）的数据结构。

具体题材的镜头表放在 topics/<slug>/shots.py；分镜时间是叙事基准，不是检测到的卡点，原曲到位后由 music.py 校准。
"""

from dataclasses import dataclass, field

FPS = 30
BASE_TOTAL = 90.0
SR = 48000

BG = "#090A0C"
GOLD = "#D6B879"
WHITE = "#F5F0E8"


@dataclass(frozen=True)
class Layout:
    """一种画幅的独立排版：画布尺寸、主字幕区、舞台区（场景以 1000×1000 舞台单位绘制后映射到此）。"""
    name: str
    w: int
    h: int
    # 舞台映射：屏幕 = 舞台单位 × scale + (ox, oy)
    stage_scale: float
    stage_ox: float
    stage_oy: float
    zoom: float             # 场景围绕舞台点 (500, 560) 的额外放大
    # 主字幕
    text_size: float
    text_line_gap: float
    text_x: float           # 居中对齐时为中心 x，左对齐时为左边界
    text_y: float           # 第一行视觉中线
    text_align: str         # "center" / "left"
    ref_size: float         # 来源卡字号
    tag_size: float
    tag_x: float
    tag_y: float
    safe: tuple             # 关键内容安全区 (l, t, r, b)


VERTICAL = Layout(
    name="vertical", w=1080, h=1920,
    stage_scale=0.83, stage_ox=90, stage_oy=690, zoom=1.2,
    text_size=80, text_line_gap=108, text_x=505, text_y=420, text_align="center",
    ref_size=60, tag_size=34, tag_x=90, tag_y=236,
    safe=(90, 180, 920, 1580),
)

HORIZONTAL = Layout(
    name="horizontal", w=1920, h=1080,
    stage_scale=0.90, stage_ox=900, stage_oy=140, zoom=1.0,
    text_size=72, text_line_gap=100, text_x=120, text_y=470, text_align="left",
    ref_size=54, tag_size=30, tag_x=120, tag_y=118,
    safe=(80, 80, 1840, 1000),
)

LAYOUTS = {"vertical": VERTICAL, "horizontal": HORIZONTAL}


@dataclass
class Cue:
    """一个候选音画事件：镜头内基准时刻、音色、视觉撞击动作。snap=False 表示柔和动作，不追重音。"""
    key: str
    t: float
    sound: str
    action: str
    gain: float = 1.0
    snap: bool = True
    window: tuple[float, float] | None = None   # 贴拍搜索窗口（镜头内秒），None 时按通用规则


@dataclass
class Shot:
    no: int
    text: str            # 用 "／" 分行，原文照录
    tag: str
    cues: list[Cue] = field(default_factory=list)
    extra: float = 0.0   # 额外阅读余量（研究段、陌生术语、来源卡等），含数字时另自动加 0.8 秒
    credit: bool = False  # 片尾来源卡：文字居中于卡片内、不做退场，卡片在本镜首个事件时刻落定
    start: float = 0.0
    dur: float = 6.0

    @property
    def lines(self) -> list[str]:
        return self.text.split("／")

    @property
    def han(self) -> int:
        return sum(1 for ch in self.text if "一" <= ch <= "鿿")

    @property
    def budget(self) -> float:
        """排版阅读预算 max(2, 汉字数/4.5) 秒（排版预算，不是心理学定律）。"""
        return max(2.0, self.han / 4.5)

    @property
    def need(self) -> float:
        """稳定窗口最低需求：预算 + 数字余量 + extra；重要句子至少 3 秒，来源卡至少 5 秒。"""
        digits = 0.8 if any(ch.isdigit() for ch in self.text) else 0.0
        return max(self.budget + digits + self.extra, 5.0 if self.credit else 3.0)


SOUNDS = {
    "kick": "低音鼓",
    "rim": "军鼓边击",
    "woodblock": "木块",
    "shaker": "沙锤",
    "framedrum": "框鼓",
    "tom": "低音通鼓",
    "bongo_lo": "邦戈鼓（低）",
    "bongo_hi": "邦戈鼓（高）",
    "cymbal": "轻柔吊镲",
}
