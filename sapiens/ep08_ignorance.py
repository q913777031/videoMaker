"""08 承认无知：为什么敢说“我不知道”的人，进步最快？"""

from adler import kit as K
from adler.core import Bubble, Card, Custom, Fig, Icon, Shot, Spark, end_shot

from . import art as A
from .common import BOOK, doubt, drop, episode, hook, line, loop, slam, tip

ACC = "#2F8F8A"
G = A.GROUND_Y
REFS = [BOOK]


def build():
    shots = [
        hook("敢说 “我 不知道”|反而 进步 【最快】？", 92),
        loop("五百年前|这句话改变了世界", icon="bulb", pose="think", mood="open"),
        Shot(4, "开会时|没人敢说“我不懂”", "情境演绎", [
            Fig(240, G, 280, at=0, mood="flat", hair="long", color=K.OTHER),
            Fig(540, G, 300, at=0, pose="point", mood="calm", hair="short", color=K.OTHER3),
            Fig(840, G, 280, at=0, mood="worried", hair="short"),
            Bubble("大家都懂了吧？", 540, 540, 42, at=2, sfx="wood_low"),
            Bubble("（其实没懂…）", 820, 680, 36, at=5, think=True, sfx="wood_high"),
        ], draw=A.ground, note="会议上没人敢问"),
        drop("承认无知", "Discovery of Ignorance", "科学革命始于|承认【我不知道】", 170),
        Shot(4, "以前的地图|画满了想象出来的岛和怪兽", "原书 · 例子", [
            Custom(lambda c, g, t, d: A.world_map(c, 0, 0, 620, label="以前：画满"), x=540, y=760, at=0, enter="pop",
                   sfx="wood_low"),
        ], note="画满的地图（示意）"),
        line("地图 留了 白|才 有人 去 【探索】", 96),
        Shot(4, "约1525年的一张世界地图|把未知的地方留了白", "原书 · 例子", [
            Custom(lambda c, g, t, d: A.world_map(c, 0, 0, 620, blank=True, label="约1525年：留白"), x=540, y=760, at=0,
                   enter="pop", sfx="ding"),
        ], research=True, flashes=[0], note="二次钩子：留白地图（示意）"),
        Shot(4, "哥伦布到死|都以为自己到的是亚洲", "原书 · 例子", [
            Fig(360, G, 300, at=0, pose="proud", mood="smile", hair="short", color=K.OTHER3),
            Bubble("这是亚洲！", 380, 560, 44, at=2, sfx="wood_low"),
            Icon("cross", 760, 640, 140, color=K.RED, at=4, sfx="rim"),
        ], draw=A.ground, research=True, note="哥伦布"),
        Shot(4, "而大陆最后以一个|承认“这是新大陆”的人命名", "原书 · 例子", [
            Card("America", 540, 700, 80, at=0, sfx="ding"),
            Spark(540, 700, at=0),
        ], research=True, note="亚美利哥"),
        slam("空白", "承认空白|才会去填"),
        doubt("地图留白的意义|历史学家看法不一"),
        tip("试试：明天开会|说一次“我不确定”"),
        end_shot(REFS, "09 幸福：为什么日子越过越好，你却没更快乐"),
    ]
    return episode(8, "ignorance", "承认无知", "为什么敢说“我不知道”的人，进步最快？", ACC, shots, REFS,
                   "敢说“我不知道”|反而进步【最快】？",
                   ["“科学革命是一场承认无知的革命”、萨尔维亚蒂世界地图（约 1525 年）留白、哥伦布与亚美利哥的例子出自《人类简史》第 14、15 章。",
                    "片中地图为示意。地图留白的意义有历史学者不同意见（不少古地图同样有留白或装饰性填充）。"])
