"""分镜、主卡文字、角标与候选音效：全片唯一数据源。

时间均为叙事基准（未按原曲校准）。events 中的 at 为镜头内局部秒数，win 为按原曲校准时允许搜索重音的局部窗口，
tier 为该动作需要的重音等级：strong = 关键撞击，需真实强重音；soft = 柔和动作，可贴普通拍点；none = 不找拍点。
"""

import re
from dataclasses import dataclass, field

FPS = 30
BASE_TOTAL = 90.0
NOMINAL_BEAT = 0.5314  # 无原曲时的名义拍长（仅用于预览）
INK = "#090A0C"
GOLD = "#D6B879"
WHITE = "#F5F0E8"

TAGS = ("情境演绎", "研究示意", "机制示意", "反思练习", "参考资料")


@dataclass
class Ev:
    """镜头内的一个音画事件，位置以「拍」计：beat=0 为本镜开始的小节强拍（第 1 镜为曲中第一个强拍）。
    sfx 为空表示只有画面动作、不加音效。tier：strong 需要真实强重音（≥0.6），soft 贴普通起音即可。"""
    name: str
    beat: float
    sfx: str | None = None
    tier: str = "soft"
    gain_db: float = 0.0


@dataclass
class Shot:
    idx: int
    bars: int
    text: tuple[str, ...]
    tag: str
    action: str
    events: list[Ev] = field(default_factory=list)
    hi: tuple[str, ...] = ()
    research: bool = False
    source: bool = False


# 每镜长度以小节计，切点全部落在小节强拍；合计 39 小节 + 片尾来源卡（延续到曲终）
SHOTS: list[Shot] = [
    Shot(1, 2, ("今天什么都没干，", "为什么还这么累？"), "情境演绎",
         "凌晨，床头时钟从 23:59 翻到 00:00；人躺在床上睁着眼，床底露出传送带。",
         [Ev("flip", 0, "low_drum", "strong"), Ev("lurch", 4, "shaker")], hi=("这么累",)),
    Shot(2, 2, ("凌晨十二点，", "身体终于躺平了。"), "情境演绎",
         "人翻身躺平、拉好被子，伸手关掉台灯；传送带仍按拍走。",
         [Ev("settle", 0), Ev("lamp", 4, "snare_rim")], hi=("十二点",)),
    Shot(3, 2, ("脑子却还在加班：", "“明天得补回来。”"), "情境演绎",
         "床上方的金线轨道上，三张待办卡按拍挂上并开始奔跑。",
         [Ev("card1", 2, "woodblock"), Ev("card2", 4, "woodblock", gain_db=-1),
          Ev("card3", 6, "woodblock", gain_db=-2)], hi=("加班",)),
    Shot(4, 2, ("刷到别人在健身、", "考证、搞副业……"), "情境演绎",
         "举起手机，放大的屏幕里信息流逐拍滚动：哑铃、证书、笔记本电脑。",
         [Ev("phone", 0, "shaker"), Ev("feed2", 2), Ev("feed3", 4, "shaker", gain_db=-2), Ev("feed4", 6)]),
    Shot(5, 2, ("越刷越慌：", "我是不是又落后了？"), "情境演绎",
         "别人的小人沿轨道一个个超过自己，传送带加速。",
         [Ev("pass1", 0, "snare_rim", "strong"), Ev("pass2", 4, "snare_rim", gain_db=-2)], hi=("落后",)),
    Shot(6, 2, ("没人在催你，", "那是谁在催？"), "情境演绎",
         "镜头拉远，房间里只有一个人；传送带还在动，驱动力不明。",
         [Ev("pull", 0), Ev("empty", 4, "low_tom")], hi=("谁在催",)),
    Shot(7, 3, ("2021年，四位学者", "想弄清一个问题："), "研究示意",
         "传送带卷成论文页，四位作者名牌逐拍落下。",
         [Ev("roll", 0, "frame_drum", "strong"), Ev("name1", 4, "woodblock"), Ev("name2", 5, "woodblock", gain_db=-1),
          Ev("name3", 6, "woodblock", gain_db=-2), Ev("name4", 7, "woodblock", gain_db=-3)], research=True),
    Shot(8, 3, ("把休息当成浪费，", "还能好好享受吗？"), "研究示意",
         "左：沙漏（浪费）；右：热水与耳机（休闲）；中间的问号按拍落下。",
         [Ev("cards", 0, "frame_drum"), Ev("ask", 6, "snare_rim")], hi=("浪费",), research=True),
    Shot(9, 3, ("先读不同的说法，", "再看同一段视频。"), "研究示意",
         "两组材料封面翻入（一侧写着「休闲是浪费」），随后两块屏幕播放同一段原创猫咪短片。",
         [Ev("covers", 0, "snare_rim"), Ev("play", 4, "shaker")], hi=("同一段",), research=True),
    Shot(10, 3, ("答案：视为浪费的人，", "享受得更少。"), "研究示意",
         "「浪费」一侧的屏幕被框架卡遮住、变暗；另一侧保持明亮。无数值、无刻度。",
         [Ev("answer", 0, "snare_rim", "strong"), Ev("glow", 4, "cymbal", gain_db=-6)], hi=("享受得更少",), research=True),
    Shot(11, 2, ("原来催你的，", "是“休息必须有用”。"), "机制示意",
         "回到卧室：人手里的评价卡发光，金色驱动线连到传送带滚轮。",
         [Ev("reveal", 0, "low_drum", "strong"), Ev("line", 2)], hi=("休息必须有用",)),
    Shot(12, 2, ("所以躺着也累：", "连休息都要考核。"), "机制示意",
         "床尾长出打卡框，人伸手想去勾，停在半空。",
         [Ev("box", 0, "woodblock"), Ev("reach", 4)], hi=("考核",)),
    Shot(13, 2, ("现实压力是真的，", "不用假装看不见。"), "情境演绎",
         "人坐起来，账单和工作通知（无字图标）落在床头柜上，被认真叠好，没有被抹掉。",
         [Ev("items", 0, "low_tom"), Ev("tidy", 4)]),
    Shot(14, 2, ("今晚试一件事：", "做点不为产出的小事。"), "反思练习",
         "床头柜上按拍出现耳机、热水杯、朋友合照。",
         [Ev("obj1", 0, "bongo_hi"), Ev("obj2", 2, "bongo_lo", gain_db=-1), Ev("obj3", 4, "bongo_hi", gain_db=-2)],
         hi=("不为产出",)),
    Shot(15, 2, ("听首歌，喝口热水，", "先不给自己打分。"), "反思练习",
         "戴上耳机、捧起热水；评价卡被放进抽屉。保持静止，留出思考时间。",
         [Ev("choose", 0, "bongo_lo", gain_db=-2), Ev("drawer", 4)], hi=("先不给自己打分",)),
    Shot(16, 2, ("这不是新任务，", "做不到也没关系。"), "反思练习",
         "打卡框退成墙上的普通相框，传送带慢慢停住。",
         [Ev("settle", 0, "cymbal", gain_db=-3)]),
    Shot(17, 3, ("什么都没干的一天，", "也值得好好休息。"), "情境演绎",
         "回扣首帧构图：同一张床、同一个时钟，传送带不见了；人躺下闭眼，台灯熄灭。",
         [Ev("return", 0, "low_drum", "strong", -6.0), Ev("sleep", 4)], hi=("值得好好休息",)),
    Shot(18, 0, ("参考：Tonietto 等（2021）", "《视休闲为浪费会削弱享受》"), "参考资料",
         "卧室剪影保持，署名独立稳定显示；音乐 3 秒淡出。",
         [Ev("end", 0, "cymbal", gain_db=-6)], research=True, source=True),
]

AUTHORS = ("Gabriela N. Tonietto", "Selin A. Malkoc", "Rebecca Walker Reczek", "Michael I. Norton")

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

COVER = {"title": "什么都没干，为什么还累？", "subtitle": "凌晨十二点，你在被谁催？"}
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
