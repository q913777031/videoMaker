"""01 白羊座：为什么大家都忍不住喜欢白羊座？"""

from adler import kit as K
from adler.core import Arrow, Bubble, Custom, Fig, Icon, Label, Shot, Spark

from . import art as A
from .common import cta, drop, episode, hook, hook2, line, loop, outro, sign, slam

ACC = "#E04A2A"
G = A.GROUND_Y
ARIES = sign("aries")
TAURUS = sign("taurus")


def build():
    shots = [
        hook("为什么 大家|都 忍不住 喜欢|【白羊座】？", "白羊座请进", 100),
        loop("不是运气好|是你有股学不来的劲"),
        Shot(4, "群里没人说话时|第一个喊“我来”的，总是你", "情境演绎", [
            Custom(A.phone_chat, x=320, y=790, at=0, enter="pop", w=440, h=680, who="项目群",
                   msgs=[(0, "谁能顶一下？"), (1, "……"), (2, "……"), (3, "……")], unread=False),
            Fig(800, G, 320, at=0, pose="stand", mood="calm", hair="short",
                moves=[(4, dict(pose="fist", mood="happy", dur=0.3, sfx="kick", note="举手：我来"))]),
            Bubble("【我来】！", 800, 600, 46, at=4, enter="pop", tail=(0, 1)),
            Spark(800, 600, at=4),
        ], draw=A.ground, punch=0.015, flashes=[4], note="群里一片沉默，你第一个举手"),
        drop(ARIES, "十二星座排第一|天生就要【冲在最前面】", mascot=A.ram),
        Shot(4, "别人还在想要不要|你已经冲出去了", "白羊 · 行动力", [
            Fig(230, G, 290, at=0, pose="think", mood="worried", color=K.OTHER, hair="bun"),
            Bubble("要不要…", 230, 620, 38, at=1, enter="pop", think=True, sfx="wood_high"),
            Fig(430, G, 300, at=0, pose="shrug", mood="flat", color=K.OTHER2, hair=None),
            Fig(600, G, 320, at=0, pose="stand", mood="happy", hair="short",
                moves=[(2, dict(x=850, pose="reach", dur=1.0, sfx="wood_low", note="冲出去"))]),
            Icon("flag", 960, G - 90, 180, at=4, sfx="ding"),
            Spark(960, G - 120, at=4),
        ], draw=A.ground, note="别人在想，你已经冲到旗子前"),
        line("想到 就 做|是 白羊 的 【超能力】", 96),
        hook2("但白羊最让人上头的|是这3个隐藏加分项", 3, "个隐藏加分项"),
        Shot(4, "不记仇|吵完三分钟，又能一起吃饭", "加分项 ①", [
            Fig(380, G, 320, at=0, pose="point", mood="angry", hair="short",
                moves=[(4, dict(x=460, pose="hug", mood="happy", dur=0.6))]),
            Fig(700, G, 300, at=0, pose="block", mood="angry", color=K.OTHER, hair="long", face=-1,
                moves=[(4, dict(x=620, pose="hug", mood="happy", dur=0.6))]),
            Label("3 分钟后", 540, 470, 36, at=3, sfx="wood_high"),
            Icon("heart", 540, 600, 120, color=K.RED, at=4, sfx="ding"),
            Spark(540, 600, at=4),
        ], draw=A.ground, note="吵架到拥抱"),
        Shot(4, "讲义气|朋友一句话，你人已经到了", "加分项 ②", [
            Fig(820, G, 300, at=0, pose="sad", mood="sad", color=K.OTHER, hair="long", face=-1,
                moves=[(5, dict(pose="stand", mood="happy", dur=0.5))]),
            Bubble("有点事…|能来一下吗", 820, 590, 38, at=0, out=4, enter="pop", sfx="rim"),
            Fig(140, G, 320, at=1, pose="stand", mood="calm", hair="short",
                moves=[(2, dict(x=590, pose="wave", mood="happy", dur=1.1, sfx="wood_low", note="赶到"))]),
            Icon("heart", 705, 640, 110, color=K.RED, at=5, sfx="ding"),
            Spark(705, 640, at=5),
        ], draw=A.ground, note="朋友一句话，你已经赶到"),
        Shot(2, "真诚|喜欢就说，不绕弯", "加分项 ③", [
            Fig(400, G, 320, at=0, pose="point", mood="happy", hair="short"),
            Bubble("就是【喜欢】！", 720, 610, 46, at=1, enter="pop", sfx="rim"),
            Spark(720, 610, at=1),
        ], draw=A.ground, text_beat=0, note="有话直说"),
        slam("不装", "有人说白羊太冲动|其实那叫不装"),
        Shot(2, "你的快不是冲动|是心里没有弯", "白羊 · 真相", [
            Arrow((180, 760), (900, 760), at=0, dur=0.6, color=K.INK3, width=8, bend=0.35, dash=(26, 20), head=0),
            Arrow((180, 760), (900, 760), at=2, dur=0.5, color=ACC, width=16, head=44, sfx="wood_high"),
            Custom(A.flame, x=950, y=740, at=3, enter="pop", s=130, sfx="ding"),
            Spark(950, 740, at=3),
        ], note="弯路淡去，一条直线冲过去，尽头燃起火苗"),
        cta("转给你身边的白羊|或者，你自己就是", mascot=A.ram),
        outro(ARIES, TAURUS, "为什么金牛座，是最让人安心的存在？", "是白羊座的|评论区扣个 1", mascot=A.ram),
    ]
    return episode(ARIES, "为什么大家都忍不住喜欢白羊座？", ACC, shots, "为什么大家|都忍不住喜欢【白羊座】？",
                   ["星座性格为大众文化中的常见印象（白羊座：热情、直率、行动力强、不记仇、讲义气），娱乐向，不作科学结论；",
                    "片中没有任何统计数字或研究引用；“3 个隐藏加分项”为本讲的叙事结构，不是数据。",
                    "白羊座日期按常见划分 3 月 21 日 – 4 月 19 日；黄道十二宫以白羊座为第一宫。"],
                   tags="#白羊座请举手 #火象星座")
