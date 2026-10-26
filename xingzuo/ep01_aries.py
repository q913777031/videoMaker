"""01 白羊座：为什么大家都忍不住喜欢白羊座？（快节奏版：42 镜 × 1 小节，动画为主、字幕为辅）"""

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Counter, Custom, Fig, Glow, Icon, Label, Pops, Rays, Spark
from scarcity.art import checklist

from . import art as A
from .common import S, drop, episode, outro, pops, sign

ACC = "#E04A2A"
G = A.GROUND_Y
ARIES = sign("aries")
TAURUS = sign("taurus")
HERO = dict(hair="short")


def build():
    shots = [
        # ---- 钩子 0–1
        pops("为什么 大家 都", tag="白羊座请进", size=118, flash=0,
             extra=[Custom(A.ram, x=850, y=470, at=3, enter="pop", s=120, sfx="ding")]),
        pops("忍不住 喜欢 【白羊座】 ？", tag="白羊座请进", size=118,
             extra=[Spark(540, 780, at=2)]),
        # ---- 点题 2–3
        S("不是运气好", "先说结论", [
            Fig(540, G, 330, at=0, pose="proud", mood="happy", **HERO),
            Custom(A.flame, x=300, y=560, at=1, enter="pop", s=150, sfx="rim"),
            Custom(A.flame, x=780, y=560, at=2, enter="pop", s=150, sfx="rim"),
        ], draw=A.ground),
        S("是你身上有团火", "先说结论", [
            Fig(540, G, 330, at=0, enter="none", pose="proud", mood="happy", **HERO,
                moves=[(0, dict(pose="fist", dur=0.25, sfx="kick"))]),
            Custom(A.flame, x=540, y=470, at=1, enter="pop", s=220, sfx="ding"),
            Spark(540, 470, at=1), Rays(540, 600, 560, at=2, alpha=0.2),
        ], draw=A.ground, flashes=[0]),
        # ---- 情境 4–7
        S("项目群里", "情境演绎", [
            Custom(A.phone_chat, x=540, y=780, at=0, enter="pop", w=480, h=700, who="项目群",
                   msgs=[(0, "谁能顶一下？"), (1, "……"), (2, "……"), (3, "……")], unread=False),
        ], hits=[(0, "wood_high", 0.8, "消息"), (1, "wood_low", 0.6, "……"), (2, "wood_low", 0.6, "……"),
                 (3, "wood_low", 0.6, "……")]),
        S("没人说话", "情境演绎", [
            Fig(260, G, 290, at=0, pose="sit_sad", mood="flat", color=K.OTHER, hair="bun"),
            Fig(540, G, 300, at=1, pose="shrug", mood="flat", color=K.OTHER2, sfx="wood_low"),
            Fig(820, G, 290, at=2, pose="cover", mood="worried", color=K.OTHER, hair="long", face=-1, sfx="wood_low"),
            Icon("question", 540, 470, 110, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S("第一个喊“我来”", "情境演绎", [
            Fig(540, G, 330, at=0, pose="stand", mood="calm", **HERO,
                moves=[(1, dict(pose="fist", mood="happy", dur=0.25, sfx="kick", note="举手：我来"))]),
            Bubble("【我来】！", 760, 560, 60, at=1, enter="pop"),
            Spark(760, 560, at=1), Rays(540, 700, 600, at=1, alpha=0.18),
        ], draw=A.ground, flashes=[1], shake=[1]),
        S("总是你", "情境演绎", [
            Custom(checklist, x=540, y=760, at=0, enter="pop", w=620, title="今日待办",
                   items=[("方案", True), ("汇报", True), ("复盘", True)], b0=1, step=1),
        ], hits=[(0, "wood_high", 0.8, "清单"), (1, "ding", 0.7, "打勾"), (2, "ding", 0.7, "打勾"),
                 (3, "ding", 0.8, "打勾")]),
        # ---- drop 8
        drop(ARIES, mascot=A.ram),
        # ---- 第一宫 9–11
        S("黄道第一宫", "黄道第一宫", [
            Custom(A.glyph, x=540, y=560, at=0, enter="pop", sign="aries", s=150),
            Custom(A.constellation, x=540, y=880, at=0, enter="none", b0=0, step=1, scale=0.9),
        ], hits=[(0, "wood_high", 0.8, "星 1"), (1, "wood_high", 0.8, "星 2"), (2, "wood_high", 0.8, "星 3"),
                 (3, "ding", 0.8, "星 4")]),
        S("", "黄道第一宫", [
            Glow(540, 720, 420, at=0),
            Counter(12, 1, 540, 720, 300, at=0, land=3, sub="十二星座 · 排第一"),
        ], hits=[(0, "shaker", 0.8, "滚动")], flashes=[3]),
        S("天生冲在最前面", "黄道第一宫", [
            Fig(150, G, 320, at=0, pose="stand", mood="happy", **HERO,
                moves=[(0, dict(x=760, pose="reach", dur=1.3, sfx="wood_low", note="冲刺"))]),
            Icon("flag", 900, G - 90, 190, at=2, enter="grow", sfx="wood_high"),
            Spark(900, G - 150, at=3, sfx="ding"),
        ], draw=A.ground),
        # ---- 行动力 12–15
        S("别人还在想", "白羊 · 行动力", [
            Fig(300, G, 300, at=0, pose="think", mood="worried", color=K.OTHER, hair="bun"),
            Bubble("要不要…", 300, 620, 42, at=1, enter="pop", think=True, sfx="wood_high"),
            Fig(760, G, 300, at=0, pose="think", mood="flat", color=K.OTHER2, face=-1),
            Bubble("再想想…", 760, 620, 42, at=2, enter="pop", think=True, sfx="wood_high"),
        ], draw=A.ground),
        S("你已经出发了", "白羊 · 行动力", [
            Fig(160, G, 320, at=0, pose="stand", mood="happy", **HERO,
                moves=[(0, dict(x=820, pose="reach", dur=0.9, sfx="kick"))]),
            Arrow((200, 780), (880, 780), at=1, dur=0.4, color=ACC, width=14, head=40, sfx="wood_high"),
            Spark(880, 780, at=2, sfx="ding"),
        ], draw=A.ground, shake=[0]),
        pops("想到 就 做 ！", size=130, extra=[Custom(A.flame, x=540, y=520, at=3, enter="pop", s=160, sfx="rim")]),
        pops("是 白羊 的 【超能力】", size=118, flash=3),
        # ---- 铺垫 16–19
        S("白羊的好", "还不止", [
            Fig(540, G, 330, at=0, pose="wave", mood="happy", **HERO),
            Icon("heart", 300, 560, 100, color=K.RED, at=1, sfx="pop"),
            Icon("heart", 540, 470, 120, color=K.RED, at=2, sfx="pop"),
            Icon("heart", 780, 560, 100, color=K.RED, at=3, sfx="pop"),
        ], draw=A.ground),
        S("还不止这些", "还不止", [
            Icon("eye", 540, 720, 240, color=K.INK, at=0, sfx="wood_low"),
            Icon("question", 760, 520, 100, color=K.RED, at=2, sfx="rim"),
            Spark(760, 520, at=2),
        ]),
        S("还有三个", "重点来了", [
            Icon("gift", 280, 760, 170, color=ACC, at=0, sfx="pop"),
            Icon("gift", 540, 760, 170, color=K.GOLD, at=1, sfx="pop"),
            Icon("gift", 800, 760, 170, color=K.GREEN, at=2, sfx="pop"),
        ]),
        S("隐藏加分项", "重点来了", [
            Icon("gift", 280, 760, 170, color=ACC, at=0, enter="none", moves=[(0, dict(y=740, dur=0.2))]),
            Icon("gift", 540, 760, 170, color=K.GOLD, at=0, enter="none", moves=[(1, dict(y=740, dur=0.2))]),
            Icon("gift", 800, 760, 170, color=K.GREEN, at=0, enter="none", moves=[(2, dict(y=740, dur=0.2))]),
            Icon("question", 280, 560, 80, color=K.RED, at=0, sfx="wood_high"),
            Icon("question", 540, 560, 80, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 800, 560, 80, color=K.RED, at=2, sfx="wood_high"),
        ]),
        # ---- 二次钩子 20
        S("", "重点来了", [
            Big("3", 540, 720, 260, at=0, sfx="kick", sub="个隐藏加分项", sub_size=50, rays=True, glow=True, shine=True,
                spark=True),
            Spark(540, 720, at=2, sfx="ding"),
        ], punch=0.03, flashes=[0], shake=[0]),
        # ---- ① 不记仇 21–23
        S("① 不记仇", "加分项 ①", [
            Fig(380, G, 320, at=0, pose="point", mood="angry", **HERO),
            Bubble("哼！", 380, 600, 50, at=1, enter="pop", sfx="rim"),
            Fig(700, G, 300, at=0, pose="block", mood="angry", color=K.OTHER, hair="long", face=-1),
            Bubble("哼！", 700, 600, 50, at=2, enter="pop", sfx="rim"),
        ], draw=A.ground),
        S("三分钟后", "加分项 ①", [
            Fig(380, G, 320, at=0, enter="none", pose="point", mood="angry", **HERO,
                moves=[(1, dict(x=460, pose="hug", mood="happy", dur=0.5, sfx="wood_low"))]),
            Fig(700, G, 300, at=0, enter="none", pose="block", mood="angry", color=K.OTHER, hair="long", face=-1,
                moves=[(1, dict(x=620, pose="hug", mood="happy", dur=0.5))]),
            Label("3 分钟后", 540, 450, 40, at=0, sfx="wood_high"),
            Icon("heart", 540, 590, 120, color=K.RED, at=2, sfx="ding"), Spark(540, 590, at=2),
        ], draw=A.ground),
        S("照样一起吃饭", "加分项 ①", [
            Fig(400, G, 320, at=0, pose="cheer", mood="happy", **HERO),
            Fig(680, G, 300, at=0, pose="cheer", mood="happy", color=K.OTHER, hair="long", face=-1),
            Spark(540, 520, at=1, sfx="clap"),
            Label("干饭！", 540, 440, 44, at=2, sfx="pop"),
        ], draw=A.ground),
        # ---- ② 讲义气 24–27
        S("② 讲义气", "加分项 ②", [
            Fig(800, G, 300, at=0, pose="sad", mood="sad", color=K.OTHER, hair="long", face=-1),
            Bubble("能来一下吗…", 760, 590, 42, at=1, enter="pop", sfx="rim"),
            Icon("phone", 560, 640, 110, color=K.INK2, at=2, sfx="wood_high"),
        ], draw=A.ground),
        S("朋友一句话", "加分项 ②", [
            Fig(120, G, 320, at=0, pose="stand", mood="happy", **HERO,
                moves=[(0, dict(x=560, pose="reach", dur=1.2, sfx="wood_low"))]),
            Fig(800, G, 300, at=0, enter="none", pose="sad", mood="sad", color=K.OTHER, hair="long", face=-1),
            Label("马上到！", 560, 470, 44, at=2, sfx="pop"),
        ], draw=A.ground),
        S("你人已经到了", "加分项 ②", [
            Fig(580, G, 320, at=0, enter="none", pose="wave", mood="happy", **HERO),
            Fig(800, G, 300, at=0, enter="none", pose="sad", mood="sad", color=K.OTHER, hair="long", face=-1,
                moves=[(1, dict(pose="hug", mood="happy", dur=0.4, sfx="wood_low"))]),
            Icon("heart", 690, 560, 110, color=K.RED, at=2, sfx="ding"), Spark(690, 560, at=2),
        ], draw=A.ground),
        S("", "加分项 ②", [
            Glow(540, 720, 400, at=0),
            Icon("shield", 540, 720, 260, color=ACC, at=0, enter="grow", sfx="wood_low"),
            Label("靠谱", 540, 930, 50, at=1, sfx="pop"),
            Spark(540, 720, at=2, sfx="ding"),
        ]),
        # ---- ③ 真诚 28–31
        S("③ 真诚", "加分项 ③", [
            Fig(380, G, 320, at=0, pose="point", mood="happy", **HERO),
            Bubble("就是【喜欢】！", 700, 600, 54, at=1, enter="pop", sfx="rim"),
            Icon("heart", 700, 440, 90, color=K.RED, at=2, sfx="ding"),
        ], draw=A.ground),
        pops("有话 直说 不绕弯", tag="加分项 ③", size=110,
             extra=[Icon("megaphone", 540, 520, 130, color=ACC, at=3, sfx="wood_high")]),
        S("心里想的就是说的", "加分项 ③", [
            Card("心里想的", 260, 760, 50, at=0, sfx="pop"),
            Big("=", 540, 760, 120, at=1, sfx="wood_high", burst=False, shadow=False),
            Card("嘴上说的", 820, 760, 50, at=2, sfx="pop"),
            Icon("check", 540, 560, 110, color=K.GREEN, at=3, sfx="ding"),
        ]),
        S("", "3 个加分项", [
            Label("① 不记仇", 540, 560, 56, at=0, sfx="pop"),
            Label("② 讲义气", 540, 720, 56, at=1, sfx="pop", fill=K.GOLD),
            Label("③ 真诚", 540, 880, 56, at=2, sfx="pop", fill=K.GREEN),
            Spark(540, 720, at=3, sfx="clap"),
        ], flashes=[3]),
        # ---- 误解与翻转 32–37
        S("有人说白羊", "常见误解", [
            Fig(260, G, 290, at=0, pose="point", mood="flat", color=K.OTHER, hair="bun"),
            Fig(820, G, 290, at=0, pose="point", mood="flat", color=K.OTHER2, face=-1),
            Bubble("太冲动了吧", 540, 560, 50, at=1, enter="pop", sfx="rim"),
        ], draw=A.ground),
        S("太冲动", "常见误解", [
            Fig(540, G, 320, at=0, pose="shrug", mood="surprised", **HERO),
            Icon("question", 360, 520, 90, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 720, 500, 90, color=K.RED, at=2, sfx="wood_high"),
        ], draw=A.ground),
        S("其实那叫", "常见误解", [
            Big("不装", 540, 760, 220, at=0, sfx="kick", glow=True, rays=True),
            Spark(540, 760, at=2, sfx="ding"),
        ], punch=0.03, shake=[0], flashes=[0]),
        S("心里没有弯", "白羊 · 真相", [
            Arrow((180, 760), (900, 760), at=0, dur=0.5, color=K.INK3, width=8, bend=0.4, dash=(26, 20), head=0,
                  alpha=0.6),
            Arrow((180, 760), (900, 760), at=1, dur=0.4, color=ACC, width=16, head=44, sfx="wood_high"),
            Custom(A.flame, x=950, y=740, at=2, enter="pop", s=130, sfx="ding"), Spark(950, 740, at=2),
        ]),
        pops("你的快 不是 冲动", tag="白羊 · 真相", size=110),
        pops("是 【真】 ！", tag="白羊 · 真相", size=150, flash=1,
             extra=[Custom(A.flame, x=300, y=520, at=2, enter="pop", s=120, sfx="rim"),
                    Custom(A.flame, x=780, y=520, at=3, enter="pop", s=120, sfx="rim")]),
        # ---- 互动 38–40
        S("转给身边的白羊", "互动", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Fig(440, G, 330, at=0, pose="cheer", mood="happy", **HERO),
            Spark(440, 560, at=1, sfx="clap"),
            Custom(A.ram, x=780, y=620, at=2, enter="pop", s=150, sfx="pop"),
        ], draw=A.ground),
        S("或者你就是", "互动", [
            Icon("phone", 320, 720, 200, color=K.INK2, at=0, sfx="wood_high"),
            Arrow((420, 720), (680, 720), at=1, dur=0.3, color=ACC, width=12, head=36, sfx="wood_low"),
            Custom(A.ram, x=800, y=720, at=2, enter="pop", s=170, sfx="ding", glow=True),
        ]),
        S("是白羊就扣起来", "互动", [
            Bubble("1", 300, 640, 70, at=0, enter="pop", sfx="pop"),
            Bubble("1", 540, 560, 80, at=1, enter="pop", sfx="pop"),
            Bubble("1", 780, 640, 70, at=2, enter="pop", sfx="pop"),
            Spark(540, 560, at=3, sfx="clap"),
        ], flashes=[3]),
        # ---- 片尾 41
        outro(ARIES, TAURUS, "为什么金牛座，是最让人安心的存在？", "是白羊座的|评论区扣个 1", mascot=A.ram),
    ]
    return episode(ARIES, "为什么大家都忍不住喜欢白羊座？", ACC, shots, "为什么大家|都忍不住喜欢【白羊座】？",
                   ["星座性格为大众文化中的常见印象（白羊座：热情、直率、行动力强、不记仇、讲义气），娱乐向，不作科学结论；",
                    "片中没有任何统计数字或研究引用；“3 个隐藏加分项”为本讲的叙事结构，不是数据；“12→1”为黄道第一宫的排序。",
                    "白羊座日期按常见划分 3 月 21 日 – 4 月 19 日；黄道十二宫以白羊座为第一宫。"],
                   tags="#白羊座请举手 #火象星座")
