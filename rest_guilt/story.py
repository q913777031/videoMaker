"""分镜、主卡文字、角标与候选音效：全片唯一数据源。

时间均为叙事基准（未按原曲校准）。events 中的 at 为镜头内局部秒数，win 为按原曲校准时允许搜索重音的局部窗口，
tier 为该动作需要的重音等级：strong = 关键撞击，需真实强重音；soft = 柔和动作，可贴普通拍点；none = 不找拍点。
"""

import re
from dataclasses import dataclass, field

FPS = 30
BASE_TOTAL = 90.0
SHOT_LEN = 6.0
INK = "#090A0C"
GOLD = "#D6B879"
WHITE = "#F5F0E8"

TAGS = ("情境演绎", "研究示意", "机制示意", "反思练习", "参考资料")


@dataclass
class Ev:
    """镜头内的一个音画事件。sfx 为空表示只有画面动作、不加音效。"""
    name: str
    at: float
    sfx: str | None = None
    tier: str = "soft"
    win: tuple[float, float] = (0.0, 0.0)
    gain_db: float = 0.0


@dataclass
class Shot:
    idx: int
    text: tuple[str, ...]
    tag: str
    action: str
    sfx_note: str
    events: list[Ev] = field(default_factory=list)
    hi: tuple[str, ...] = ()
    research: bool = False
    source: bool = False


SHOTS: list[Shot] = [
    Shot(1, ("今天什么都没干，", "怎么还是不轻松？"), "情境演绎",
         "人物刚坐下，沙发底部却露出传送带；镜头停住，让矛盾清楚可见。", "低音鼓",
         [Ev("reveal", 0.6, "low_drum", "strong", (0.25, 1.5))], hi=("不轻松",)),
    Shot(2, ("人躺下了，", "脑子还在赶进度。"), "情境演绎",
         "身体静止，身后无文字任务卡沿轨道奔跑；由沙发扶手匹配转场为轨道。", "沙锤",
         [Ev("run", 0.9, "shaker", "soft", (0.4, 2.4))], hi=("赶进度",)),
    Shot(3, ("再学一点？", "再做一点？"), "情境演绎",
         "两张催促卡在不同拍点靠近；不增加其他气泡。手机被主角反扣。", "木块",
         [Ev("card1", 0.8, "woodblock", "soft", (0.4, 1.5)),
          Ev("card2", 2.0, "woodblock", "soft", (1.4, 2.9), -1.5),
          Ev("phone", 3.4, None, "soft", (3.0, 4.2))]),
    Shot(4, ("没人催你，", "为什么还不敢停？"), "情境演绎",
         "镜头拉远，房间没有旁人；跑步机仍动，保留驱动力悬念。", "无新增音效",
         [Ev("pull", 0.5, None, "soft", (0.2, 1.2))], hi=("不敢停",)),
    Shot(5, ("2021年的研究，", "问了一个问题。"), "研究示意",
         "跑步机带卷成论文页；出现阅读材料、看视频、填写反馈三个无字图标。", "框鼓",
         [Ev("roll", 0.5, "frame_drum", "strong", (0.2, 1.4)),
          Ev("icon1", 1.7, None, "soft", (1.4, 2.0)),
          Ev("icon2", 2.5, None, "soft", (2.2, 2.8)),
          Ev("icon3", 3.3, None, "soft", (3.0, 3.6))], research=True),
    Shot(6, ("先读不同材料，", "再看同一段视频。"), "研究示意",
         "两侧材料封面不同，同一猫咪轮廓短片分别播放；不使用原视频版权素材。", "木块",
         [Ev("covers", 0.8, "woodblock", "soft", (0.4, 1.6)),
          Ev("play", 2.6, None, "soft", (2.2, 3.2))], hi=("同一段",), research=True),
    Shot(7, ("把休闲视为浪费，", "可能更难享受它。"), "研究示意",
         "两侧相同屏幕保持，阅读材料的框架卡覆盖其中一侧；不用数值表情量表。", "军鼓边击",
         [Ev("cover", 1.0, "snare_rim", "strong", (0.5, 2.2))], hi=("视为浪费",), research=True),
    Shot(8, ("你是否也在要求：", "休息必须有用？"), "机制示意",
         "回到房间，揭示传送带由主角手中的评价卡驱动；只作视觉比喻。", "低音鼓",
         [Ev("reveal", 1.0, "low_drum", "strong", (0.5, 2.4))], hi=("必须有用",)),
    Shot(9, ("放松，也变成了", "另一项考核。"), "机制示意",
         "沙发旁长出打卡框，主角伸手准备勾选又停下；镜头轻退。", "木块",
         [Ev("box", 0.8, "woodblock", "soft", (0.4, 1.7)),
          Ev("reach", 1.9, None, "soft", (1.6, 2.6))], hi=("考核",)),
    Shot(10, ("但现实的压力，", "也需要被看见。"), "情境演绎",
         "账单和工作通知以无字图标放在桌上，没有被一键抹除；角色认真整理。", "低音通鼓",
         [Ev("items", 0.7, "low_tom", "soft", (0.3, 1.7)),
          Ev("tidy", 2.2, None, "soft", (1.9, 2.8))]),
    Shot(11, ("想一件你喜欢、", "却不必产出的事。"), "反思练习",
         "桌上出现散步鞋、茶杯、朋友合照三个物体；只保留主字幕。", "邦戈鼓",
         [Ev("obj1", 0.8, "bongo_hi", "soft", (0.4, 1.3)),
          Ev("obj2", 1.6, "bongo_lo", "soft", (1.3, 2.1), -1.0),
          Ev("obj3", 2.4, "bongo_hi", "soft", (2.1, 2.9), -2.0)], hi=("不必产出",)),
    Shot(12, ("给它留一点时间，", "先不评分。"), "反思练习",
         "选择茶杯，评价卡暂时放入抽屉；保持动作后静止供观众思考。", "无新增音效",
         [Ev("choose", 0.8, None, "soft", (0.4, 1.4)),
          Ev("drawer", 2.0, None, "soft", (1.6, 2.6))], hi=("先不评分",)),
    Shot(13, ("这不是另一份", "必须完成的任务。"), "情境演绎",
         "打卡框退成普通相框，传送带逐渐停住，不出现满血恢复的夸张变化。", "轻柔吊镲",
         [Ev("settle", 0.6, "cymbal", "soft", (0.3, 1.8), -3.0)]),
    Shot(14, ("休息之前，", "一定要先证明自己吗？"), "反思练习",
         "回到首帧构图：同一人坐在真正的沙发上，杯中热气缓升。", "克制低音鼓",
         [Ev("return", 0.0, "low_drum", "strong", (0.0, 0.9), -6.0)], hi=("证明自己",)),
    Shot(15, ("参考：Tonietto等，2021", "休闲信念与享受研究"), "参考资料",
         "沙发剪影保持，署名独立稳定显示；所有声音平滑收尾。", "轻柔吊镲",
         [Ev("end", 0.3, "cymbal", "soft", (0.0, 1.2), -6.0)], research=True, source=True),
]

SFX_LABEL = {
    "low_drum": "低音鼓", "snare_rim": "军鼓边击", "woodblock": "木块", "shaker": "沙锤",
    "frame_drum": "框鼓", "low_tom": "低音通鼓", "bongo_hi": "邦戈鼓（高）", "bongo_lo": "邦戈鼓（低）",
    "cymbal": "轻柔吊镲",
}
# 七类音色：框鼓与低音通鼓同属一类，邦戈鼓高低两音同属一类
SFX_CATEGORY = {
    "low_drum": "低音鼓", "snare_rim": "军鼓边击", "woodblock": "木块", "shaker": "沙锤",
    "frame_drum": "框鼓/低音通鼓", "low_tom": "框鼓/低音通鼓", "bongo_hi": "邦戈鼓", "bongo_lo": "邦戈鼓",
    "cymbal": "轻柔吊镲",
}

COVER = {"title": "为什么休息也内疚？", "subtitle": "没人催你，你却不敢停"}
PUBLISH_TITLE = "《为什么明明在休息，你却一点也不轻松？》"
HASHTAGS = "#知识科普 #心理学 #休息内疚 #上班族 #自我理解"

REFERENCE = (
    "Gabriela N. Tonietto, Selin A. Malkoc, Rebecca Walker Reczek, Michael I. Norton (2021). "
    "Viewing leisure as wasteful undermines enjoyment. Journal of Experimental Social Psychology, 97, 104198. "
    "DOI: 10.1016/j.jesp.2021.104198"
)
PAPER_URL = "https://www.business.rutgers.edu/sites/default/files/documents/tonietto-viewing-leisure-as-wasteful-undermines-enjoyment.pdf"

_HAN = re.compile(r"[一-鿿]")


def han_count(s: str) -> int:
    return len(_HAN.findall(s))


def shot_han(shot: Shot) -> int:
    return sum(han_count(t) for t in shot.text)


def read_budget(shot: Shot) -> float:
    """阅读预算（秒）：max(2, 汉字数/4.5)；含数字、英文或来源的卡另加 1 秒；重要句至少 3 秒，研究段与署名约 5 秒。"""
    n = shot_han(shot)
    base = max(2.0, n / 4.5)
    if any(ch.isdigit() or ch.isascii() and ch.isalpha() for t in shot.text for ch in t):
        base += 1.0
    need = max(base, 3.0)
    if shot.research:
        need = max(need, 4.8)
    return need
