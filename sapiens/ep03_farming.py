"""03 农业革命：为什么越努力，日子反而越累？"""

from adler import kit as K
from adler.core import Counter, Custom, Fig, Icon, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#7F8A2E"
G = A.GROUND_Y
REFS = [BOOK, "Cohen & Armelagos (1984). Paleopathology at the Origins of Agriculture.",
        "Marciniak et al. (2021). Height and health of early European farmers. PNAS."]


def build():
    shots = [
        hook("越 努力|日子 反而 越 【累】？", 108),
        loop("一万多年前|人类就掉进过这个坑", pose="sad", mood="worried"),
        Shot(4, "加班换来了大房子|也换来了更多房贷", "情境演绎", [
            Fig(300, G, 320, at=0, pose="carry", mood="worried", hair="short"),
            Icon("house", 740, 640, 220, color=ACC, at=2, sfx="wood_low"),
            Custom(A.bill, x=760, y=960, at=5, enter="drop", rot=4, title="房贷", amount="30年", sfx="rim"),
        ], draw=A.ground, note="房子与房贷"),
        drop("农业革命", "Agricultural Revolution", "书里说：这是史上|最大的【骗局】", 170),
        Shot(4, "不是人驯化了小麦|是小麦驯化了人", "原书 · 大意", [
            Custom(A.field, x=540, y=G - 40, at=0, enter="none", n=9, s=230, grow=1.4),
            Fig(540, G + 10, 300, at=2, pose="crouch", mood="worried", hair="short", sfx="wood_low"),
        ], hits=[(0, "wood_low", 0.6, "麦田长出")], note="麦田里弯腰的人"),
        line("弯腰 除草|挑水 【守着地】"),
        Shot(4, "考古发现：早期农民|个子变矮、病更多", "研究证据 · Cohen & Armelagos 1984", [
            Fig(360, G, 340, at=0, mood="calm", hair="short", color=K.OTHER3),
            Fig(720, G, 280, at=2, pose="sad", mood="sad", hair="short", color=ACC, sfx="rim"),
            Icon("cross", 720, 640, 90, color=K.RED, at=4, sfx="rim"),
        ], draw=A.ground, research=True, flashes=[2], note="二次钩子：采集者与农民对比"),
        Shot(4, "21个转向农业的社会里|19个健康变差", "研究证据 · Cohen & Armelagos 1984", [
            Counter(0, 19, 540, 680, 220, at=0, land=4, suffix="/21", sub="个社会健康下降"),
        ], research=True, note="数字落定"),
        Shot(4, "可人口暴涨了：|物种赢了，个人更累了", "原书 · 大意", [
            Custom(A.crowd, x=540, y=G, at=0, enter="fade", n=14, s=150, spread=880, rows=3),
            Icon("sprout", 540, 520, 120, color=K.GREEN, at=2, sfx="wood_high"),
        ], draw=A.ground, note="人口变多"),
        slam("回不去", "人口靠农田养活|回不去了", size=150),
        doubt("身高也受基因影响|“骗局”说法有争议", tag="常见质疑 · Marciniak 2021"),
        tip("试试：算算这次加班|到底换来了什么"),
        end_shot(REFS, "04 奢侈品陷阱：为什么涨了工资，还是不够花"),
    ]
    return episode(3, "farming", "农业革命", "为什么越努力，日子反而越累？", ACC, shots, REFS,
                   "为什么越努力|日子反而越【累】？",
                   ["“农业革命是史上最大骗局”“小麦驯化了人”为《人类简史》第 5 章的观点；书中称农业革命约始于 1.2 万年前。",
                    "Cohen & Armelagos (1984) 汇总的研究中，21 个经历农业转型的社会有 19 个健康与营养状况下降；后续综述（Mummert 等 2011）总体支持。",
                    "Marciniak 等 (2021) 指出身高受遗传与迁徙影响，单凭身高推断健康需谨慎；“骗局”的说法也被不少学者批评过于修辞化。"])
