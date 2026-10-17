"""《为什么一到晚上，就觉得自己的人生不行了》制作参数：画幅、配色、分镜、字幕与候选音效事件。

分镜时间是 90 秒叙事基准，不是检测到的卡点；实际原曲到位后由 music.py 校准。
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


@dataclass
class Shot:
    no: int
    text: str            # 用 "／" 分行，原文照录
    tag: str
    cues: list[Cue] = field(default_factory=list)
    start: float = 0.0
    dur: float = 6.0

    @property
    def lines(self) -> list[str]:
        return self.text.split("／")

    @property
    def han(self) -> int:
        return sum(1 for ch in self.text if "一" <= ch <= "鿿")


def shots() -> list[Shot]:
    """15 个镜头的叙事基准（每镜 6 秒）。"""
    s = [
        Shot(1, "白天只是出了错，／晚上怎么否定了人生？", "情境演绎",
             [Cue("surge", 0.6, "kick", "卡片微倾，墙上城市阴影猛然扩张")]),
        Shot(2, "一份方案没做好。", "情境演绎",
             [Cue("frame", 1.2, "woodblock", "金色框线锁定局部待修改标记")]),
        Shot(3, "怎么变成了：／我什么都做不好？", "情境演绎",
             [Cue("cover", 2.4, "rim", "膨胀的修改卡盖住最后一张工作记录"),
              Cue("pull", 3.4, "shaker", "镜头随阴影后退，露出卡片城市", 0.8, snap=False)]),
        Shot(4, "越想，／越像已经有了结论。", "机制示意",
             [Cue("lap", 1.6, "tom", "卡片完成第一圈，颜色加深一级")]),
        Shot(5, "反复想，／等于在解决吗？", "反思练习",
             [Cue("halt", 0.5, "", "轨道停一拍，短路径开始延伸", snap=False)]),
        Shot(6, "2008年综述：／反刍与反思并不相同。", "研究示意",
             [Cue("merge", 2.6, "framedrum", "多篇论文缩略页汇合成一本综述")]),
        Shot(7, "反刍：／围着痛苦反复打转。", "机制示意",
             [Cue("walk", 0.6, "shaker", "人物开始绕问题卡走圈", 0.7, snap=False),
              Cue("door", 3.2, "woodblock", "人物经过关闭的新信息入口，门仍不开")]),
        Shot(8, "反思可以走向／具体信息和下一步。", "机制示意",
             [Cue("fact", 1.8, "bongo_lo", "文件分出事实格"),
              Cue("act", 2.6, "bongo_hi", "文件分出行动格")]),
        Shot(9, "今晚的判断，／有哪些事实支持？", "反思练习",
             [Cue("fold", 1.6, "rim", "巨大人生卡折回一张纸"),
              Cue("pick", 3.0, "shaker", "从纸中抽出真实修改标记", 0.7, snap=False)]),
        Shot(10, "先写下：／究竟发生了什么。", "反思练习",
             [Cue("place", 1.2, "woodblock", "实际事件图标落入第一格"),
              Cue("slide", 2.8, "shaker", "模糊标签移到纸边", 0.6, snap=False)]),
        Shot(11, "再问一句：／下一步能做什么？", "反思练习",
             [Cue("point", 1.8, "bongo_hi", "箭头只指向一个可修改段落")]),
        Shot(12, "没有新增信息，／可以先暂停这轮审判。", "反思练习",
             [Cue("down", 1.0, "", "人物放下纸张，轨道淡出", snap=False)]),
        Shot(13, "难受持续影响生活，／也值得寻求支持。", "生活提示",
             [Cue("lamp", 1.2, "cymbal", "邻近的灯亮起")]),
        Shot(14, "今晚出了点问题，／不等于人生已被判定。", "情境演绎",
             [Cue("settle", 1.0, "kick", "问题卡恢复真实大小，阴影收回", 0.6)]),
        Shot(15, "参考：2008年／《重新思考反刍》综述", "参考资料",
             [Cue("credit", 0.4, "cymbal", "来源卡落定", 0.8)]),
    ]
    for i, sh in enumerate(s):
        sh.start = i * 6.0
    return s


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
