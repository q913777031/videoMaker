"""08 承认无知：为什么敢说“我不知道”的人，进步最快？（重做版）"""

from adler import kit as K
from adler.core import Bubble, Card, Custom, Fig, Icon, Label, Pops, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, ask, drop2, redo, slam2, tip2

ACC = "#2F8F8A"
G = A.GROUND_Y
REFS = [BOOK]


def _blank_map(c, g, t, d):
    A.world_map(c, 0, 0, 760, blank=True, label=d.get("label", ""))


def build():
    shots = [
        ask("地图 上 这块 空白|里面 【是什么】？", [
            Custom(_blank_map, x=540, y=960, at=2, enter="pop", sfx="wood_low"),
        ], note="互动：猜空白"),
        Shot(4, "倒计时3秒|猜一猜", "互动小游戏", [
            Custom(A.countdown, x=540, y=470, at=0, enter="none"),
            Custom(_blank_map, x=540, y=960, at=0, enter="none"),
            Label("不知道？", 540, 1260, 50, at=7, fill=K.RED, sfx="rim"),
            Label("这就对了！", 540, 1260, 50, at=11, fill=K.GREEN, sfx="ding"),
        ], hits=[(0, "wood_high", 0.9, "3"), (2, "wood_high", 0.9, "2"), (4, "rim", 1.0, "1"), (6, "kick", 0.9, "时间到")],
            flashes=[6], shake=[(6, 12.0)], punch=0.025, note="不知道就对了"),
        Shot(2, "五百年前|这块空白改变了世界", "互动小游戏", [
            Pops("敢 说|【我不知道】", 540, 760, 120, at=0, step=1),
            Spark(540, 760, at=4, sfx="ding"),
        ], text_beat=0, note="揭晓"),
        drop2("承认无知", "Discovery of Ignorance", "科学革命始于|承认【我不知道】", "提问 观察 实验", size=170),
        Shot(4, "以前的地图|画满了想象出来的岛和怪兽", "原书 · 例子", [
            Custom(lambda c, g, t, d: A.world_map(c, 0, 0, 640, label="以前：画满"), x=540, y=760, at=0, enter="pop",
                   sfx="wood_low"),
            Label("以为全知道", 540, 520, 44, at=6, fill=K.RED, sfx="rim"),
            Icon("cross", 820, 620, 100, color=K.RED, at=10, sfx="rim"),
        ], note="画满的地图（示意）"),
        Shot(4, "", "一句话", [
            Pops("地图 留了 白|才 有人 去 【探索】", 540, 780, 100, at=0, step=2),
        ], punch=0.02, flashes=[10], note="金句"),
        Shot(4, "约1525年的一张世界地图|把未知的地方留了白", "原书 · 例子", [
            Custom(lambda c, g, t, d: A.world_map(c, 0, 0, 640, blank=True, label="约1525年：留白"), x=540, y=760, at=0,
                   enter="pop", sfx="ding"),
            Label("承认不知道", 540, 520, 44, at=6, fill=K.GREEN, sfx="wood_high"),
            Spark(780, 790, at=10, sfx="ding"),
        ], research=True, punch=0.02, flashes=[0], note="二次钩子：留白地图（示意）"),
        Shot(4, "哥伦布到死|都以为自己到的是亚洲", "原书 · 例子", [
            Fig(360, G, 300, at=0, pose="proud", mood="smile", hair="short", color=K.OTHER3),
            Bubble("这是亚洲！", 380, 560, 44, at=3, sfx="wood_low"),
            Icon("cross", 760, 640, 140, color=K.RED, at=7, sfx="rim"),
            Label("错过了新大陆", 760, 860, 42, at=11, fill=K.RED, sfx="rim"),
        ], draw=A.ground, research=True, note="哥伦布"),
        Shot(4, "大陆最后以承认“这是新大陆”|的亚美利哥命名", "原书 · 例子", [
            Card("America", 540, 700, 90, at=0, sfx="ding"),
            Spark(540, 700, at=0),
            Fig(540, G, 260, at=5, pose="cheer", mood="happy", hair="short", color=ACC, sfx="wood_high"),
            Label("承认无知的人赢了", 540, 940, 42, at=10, fill=ACC, sfx="ding"),
        ], draw=A.ground, research=True, note="亚美利哥"),
        slam2("空白", "承认 【空白】|才会 去 填", "承认无知|才是进步的起点"),
        Shot(4, "第一招：开会时|敢说一次“我不确定”", "小方法", [
            Fig(240, G, 280, at=0, mood="flat", hair="long", color=K.OTHER),
            Fig(540, G, 300, at=0, pose="point", mood="calm", hair="short", color=K.OTHER3),
            Fig(840, G, 280, at=0, pose="wave", mood="open", hair="short"),
            Bubble("大家都懂了吧？", 540, 540, 42, at=2, sfx="wood_low"),
            Bubble("这里我不确定", 820, 700, 40, at=6, sfx="wood_high"),
            Icon("bulb", 540, 400, 100, color=K.GOLD, at=10, sfx="ding"),
        ], draw=A.ground, note="会上举手"),
        tip2("第二招：不懂就问|问完就懂", "不懂 就 【问】", 130),
        end_shot(REFS, "09 幸福：为什么日子越过越好，你却没更快乐"),
    ]
    return redo(8, "ignorance", "承认无知", "为什么敢说“我不知道”的人，进步最快？", ACC, shots, REFS,
                "敢说“我不知道”|反而进步【最快】？",
                ["“科学革命是一场承认无知的革命”、萨尔维亚蒂世界地图（约 1525 年）留白、哥伦布与亚美利哥的例子出自《人类简史》第 14、15 章；"
                 "地图为示意，两招为方法建议。"])
