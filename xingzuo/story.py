"""十二星座夸夸版的通用 42 镜故事模板（快节奏规则：每镜 1 小节、动画为主、字幕 ≤10 字）。

白羊座（ep01）为手写范例；其余各讲用 build_episode(sign_key, spec) 由一份星座专属文案表生成，
结构与白羊座一致：钩子 → 点题 → 日常情境 → drop → 星群与宫位 → 特质 → 金句 → 二次钩子 →
3 个加分项 → 误解翻转 → 互动 → 片尾。spec 字段见各 epNN 文件。
"""

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Counter, Custom, Fig, Glow, Icon, Label, Rays, Spark
from scarcity.art import checklist

from . import art as A
from .common import SIGNS, S, drop, episode, outro, pops, sign
from .specs import TITLES

G = A.GROUND_Y
HERO = dict(hair="short")


def short(name: str) -> str:
    return name[:-1] if name.endswith("座") else name


def elem(s, x, y, size, at, sfx=None, enter="pop"):
    """元素图标：火 = 火苗，土 = 嫩芽，风 = 云，水 = 水滴。"""
    if s.element == "火":
        return Custom(A.flame, x=x, y=y, at=at, enter=enter, s=size, sfx=sfx)
    name = {"土": "sprout", "风": "cloud", "水": "water"}[s.element]
    return Icon(name, x, y, size * 0.8, color=K.GREEN if s.element == "土" else "#5B9BD5", accent=K.GOLD, at=at,
                enter=enter, sfx=sfx)


def build_episode(key: str, sp: dict):
    s = sign(key)
    acc = sp["acc"]
    nxt = SIGNS[s.no] if s.no < 12 else None
    mas = A.mascot(key)
    sh = short(s.name)
    i1, i2, i3, mis = sp["item1"], sp["item2"], sp["item3"], sp["mis"]
    shots = [
        # 钩子 0–1
        pops(sp["hook"][0], tag=f"{s.name}请进", size=118, flash=0,
             extra=[Custom(mas, x=850, y=470, at=3, enter="pop", s=120, sfx="ding")]),
        pops(sp["hook"][1], tag=f"{s.name}请进", size=112, extra=[Spark(540, 780, at=2)]),
        # 点题 2–3
        S(sp["loop"][0], "先说结论", [
            Fig(540, G, 330, at=0, pose="proud", mood="happy", **HERO),
            elem(s, 300, 560, 150, 1, "rim"), elem(s, 780, 560, 150, 2, "rim"),
        ], draw=A.ground),
        S(sp["loop"][1], "先说结论", [
            Fig(540, G, 330, at=0, enter="none", pose="proud", mood="happy", **HERO,
                moves=[(0, dict(pose="fist", dur=0.25, sfx="kick"))]),
            elem(s, 540, 470, 220, 1, "ding"), Spark(540, 470, at=1), Rays(540, 600, 560, at=2, alpha=0.2),
        ], draw=A.ground, flashes=[0]),
        # 日常情境 4–7
        S(sp["scene"][0], "情境演绎", [
            Custom(A.phone_chat, x=540, y=780, at=0, enter="pop", w=480, h=700, who=sp["chat"][0],
                   msgs=[(i, m) for i, m in enumerate(sp["chat"][1])], unread=False),
        ], hits=[(0, "wood_high", 0.8, "消息"), (1, "wood_low", 0.6, "消息"), (2, "wood_low", 0.6, "消息"),
                 (3, "wood_low", 0.6, "消息")]),
        S(sp["scene"][1], "情境演绎", [
            Fig(260, G, 290, at=0, pose="sit_sad", mood="flat", color=K.OTHER, hair="bun"),
            Fig(540, G, 300, at=1, pose="shrug", mood="flat", color=K.OTHER2, sfx="wood_low"),
            Fig(820, G, 290, at=2, pose="cover", mood="worried", color=K.OTHER, hair="long", face=-1, sfx="wood_low"),
            Icon("question", 540, 470, 110, color=K.RED, at=3, sfx="rim"),
        ], draw=A.ground),
        S(sp["scene"][2], "情境演绎", [
            Fig(540, G, 330, at=0, pose="stand", mood="calm", **HERO,
                moves=[(1, dict(pose=sp.get("pose", "fist"), mood="happy", dur=0.25, sfx="kick"))]),
            Bubble(sp["say"], 760, 560, 56, at=1, enter="pop"),
            Spark(760, 560, at=1), Rays(540, 700, 600, at=1, alpha=0.18),
        ], draw=A.ground, flashes=[1], shake=[1]),
        S(sp["scene"][3], "情境演绎", [
            Custom(checklist, x=540, y=760, at=0, enter="pop", w=620, title=sp["todo"][0],
                   items=[(t, True) for t in sp["todo"][1]], b0=1, step=1),
        ], hits=[(0, "wood_high", 0.8, "清单"), (1, "ding", 0.7, "打勾"), (2, "ding", 0.7, "打勾"),
                 (3, "ding", 0.8, "打勾")]),
        # drop 8
        drop(s, mascot=mas),
        # 星群与宫位 9–11
        S(f"{s.element}象星座", f"黄道第{'一二三四五六七八九十'[s.no - 1] if s.no <= 10 else '十' + '一二'[s.no - 11]}宫", [
            Custom(A.glyph, x=540, y=540, at=0, enter="pop", sign=key, s=150),
            Custom(A.constellation, x=540, y=880, at=0, enter="none", b0=0, step=0.5, scale=0.85, sign=key),
        ], hits=[(0, "wood_high", 0.8, "星"), (1, "wood_high", 0.8, "星"), (2, "ding", 0.8, "星")]),
        S("", s.name, [
            Glow(540, 720, 420, at=0), elem(s, 540, 470, 150, 3, "ding"),
            Counter(0, s.no, 540, 760, 260, at=0, land=2, sub=f"黄道第 {s.no} 宫 · {s.dates}"),
        ], hits=[(0, "shaker", 0.8, "滚动")], flashes=[2]),
        S(sp["trait"][0], f"{sh} · 高光", [
            Fig(150, G, 320, at=0, pose="stand", mood="happy", **HERO,
                moves=[(0, dict(x=700, pose="reach", dur=1.2, sfx="wood_low"))]),
            Icon(sp["trait"][1], 880, 760, 200, color=acc, at=2, enter="grow", sfx="wood_high"),
            Spark(880, 760, at=3, sfx="ding"),
        ], draw=A.ground),
        # 特质对比 12–15
        S(sp["think"][0], f"{sh} · 高光", [
            Fig(300, G, 300, at=0, pose="think", mood="worried", color=K.OTHER, hair="bun"),
            Bubble(sp["think"][1], 300, 620, 42, at=1, enter="pop", think=True, sfx="wood_high"),
            Fig(760, G, 300, at=0, pose="think", mood="flat", color=K.OTHER2, face=-1),
            Bubble(sp["think"][2], 760, 620, 42, at=2, enter="pop", think=True, sfx="wood_high"),
        ], draw=A.ground),
        S(sp["you"][0], f"{sh} · 高光", [
            Fig(160, G, 320, at=0, pose="stand", mood="happy", **HERO,
                moves=[(0, dict(x=700, pose="cheer", dur=0.9, sfx="kick"))]),
            Arrow((200, 780), (640, 780), at=1, dur=0.4, color=acc, width=14, head=40, sfx="wood_high"),
            Icon(sp["you"][1], 880, 700, 190, color=acc, at=2, enter="grow", sfx="ding"), Spark(880, 700, at=2),
        ], draw=A.ground, shake=[0]),
        pops(sp["lines"][0], size=118, extra=[elem(s, 540, 520, 150, 3, "rim")]),
        pops(sp["lines"][1], size=112, flash=3),
        # 铺垫 16–19
        S(f"{sh}的好", "还不止", [
            Fig(540, G, 330, at=0, pose="wave", mood="happy", **HERO),
            Icon("heart", 300, 560, 100, color=K.RED, at=1, sfx="pop"),
            Icon("heart", 540, 470, 120, color=K.RED, at=2, sfx="pop"),
            Icon("heart", 780, 560, 100, color=K.RED, at=3, sfx="pop"),
        ], draw=A.ground),
        S("还不止这些", "还不止", [
            Icon("eye", 540, 720, 240, color=K.INK, at=0, sfx="wood_low"),
            Icon("question", 760, 520, 100, color=K.RED, at=2, sfx="rim"), Spark(760, 520, at=2),
        ]),
        S("还有三个", "重点来了", [
            Icon("gift", 280, 760, 170, color=acc, at=0, sfx="pop"),
            Icon("gift", 540, 760, 170, color=K.GOLD, at=1, sfx="pop"),
            Icon("gift", 800, 760, 170, color=K.GREEN, at=2, sfx="pop"),
        ]),
        S("隐藏加分项", "重点来了", [
            Icon("gift", 280, 760, 170, color=acc, at=0, enter="none", moves=[(0, dict(y=740, dur=0.2))]),
            Icon("gift", 540, 760, 170, color=K.GOLD, at=0, enter="none", moves=[(1, dict(y=740, dur=0.2))]),
            Icon("gift", 800, 760, 170, color=K.GREEN, at=0, enter="none", moves=[(2, dict(y=740, dur=0.2))]),
            Icon("question", 280, 560, 80, color=K.RED, at=0, sfx="wood_high"),
            Icon("question", 540, 560, 80, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 800, 560, 80, color=K.RED, at=2, sfx="wood_high"),
        ]),
        # 二次钩子 20
        S("", "重点来了", [
            Big("3", 540, 720, 260, at=0, sfx="kick", sub="个隐藏加分项", sub_size=50, rays=True, glow=True, shine=True,
                spark=True),
            Spark(540, 720, at=2, sfx="ding"),
        ], punch=0.03, flashes=[0], shake=[0]),
        # ① 21–23
        S(f"① {i1['name']}", "加分项 ①", [
            Fig(700, G, 300, at=0, pose="sad", mood="worried", color=K.OTHER, hair="long", face=-1),
            Bubble(i1["ask"], 700, 590, 42, at=1, enter="pop", sfx="rim"),
            Fig(360, G, 320, at=0, pose="stand", mood="happy", **HERO,
                moves=[(2, dict(pose="point", dur=0.3))]),
            Bubble(i1["ans"], 360, 590, 46, at=2, enter="pop", sfx="wood_high"),
        ], draw=A.ground),
        S(i1["capB"], "加分项 ①", [
            Fig(360, G, 320, at=0, enter="none", pose="point", mood="happy", **HERO,
                moves=[(1, dict(x=460, pose="hug", dur=0.5, sfx="wood_low"))]),
            Fig(700, G, 300, at=0, enter="none", pose="sad", mood="worried", color=K.OTHER, hair="long", face=-1,
                moves=[(1, dict(x=620, pose="hug", mood="happy", dur=0.5))]),
            Label(i1["label"], 540, 450, 42, at=0, sfx="wood_high"),
            Icon("heart", 540, 590, 120, color=K.RED, at=2, sfx="ding"), Spark(540, 590, at=2),
        ], draw=A.ground),
        S(i1["capC"], "加分项 ①", [
            Fig(400, G, 320, at=0, pose="cheer", mood="happy", **HERO),
            Fig(680, G, 300, at=0, pose="cheer", mood="happy", color=K.OTHER, hair="long", face=-1),
            Spark(540, 520, at=1, sfx="clap"), Label(i1["cheer"], 540, 440, 44, at=2, sfx="pop"),
        ], draw=A.ground),
        # ② 24–27
        S(f"② {i2['name']}", "加分项 ②", [
            Fig(800, G, 300, at=0, pose="sad", mood="sad", color=K.OTHER2, face=-1),
            Bubble(i2["ask"], 760, 590, 42, at=1, enter="pop", sfx="rim"),
            Icon("phone", 520, 640, 110, color=K.INK2, at=2, sfx="wood_high"),
        ], draw=A.ground),
        S(i2["capB"], "加分项 ②", [
            Fig(120, G, 320, at=0, pose="stand", mood="happy", **HERO,
                moves=[(0, dict(x=560, pose="reach", dur=1.2, sfx="wood_low"))]),
            Fig(800, G, 300, at=0, enter="none", pose="sad", mood="sad", color=K.OTHER2, face=-1),
            Label(i2["label"], 560, 470, 44, at=2, sfx="pop"),
        ], draw=A.ground),
        S(i2["capC"], "加分项 ②", [
            Fig(580, G, 320, at=0, enter="none", pose="give", mood="happy", **HERO),
            Fig(800, G, 300, at=0, enter="none", pose="sad", mood="sad", color=K.OTHER2, face=-1,
                moves=[(1, dict(pose="cheer", mood="happy", dur=0.4, sfx="wood_low"))]),
            Icon("heart", 690, 560, 110, color=K.RED, at=2, sfx="ding"), Spark(690, 560, at=2),
        ], draw=A.ground),
        S("", "加分项 ②", [
            Glow(540, 720, 400, at=0),
            Icon(i2["icon"], 540, 720, 260, color=acc, at=0, enter="grow", sfx="wood_low"),
            Label(i2["word"], 540, 940, 50, at=1, sfx="pop"), Spark(540, 720, at=2, sfx="ding"),
        ]),
        # ③ 28–31
        S(f"③ {i3['name']}", "加分项 ③", [
            Fig(380, G, 320, at=0, pose="point", mood="happy", **HERO),
            Bubble(i3["say"], 700, 600, 50, at=1, enter="pop", sfx="rim"),
            Icon("heart", 700, 440, 90, color=K.RED, at=2, sfx="ding"),
        ], draw=A.ground),
        pops(i3["pops"], tag="加分项 ③", size=104,
             extra=[Icon(i3["icon"], 540, 520, 130, color=acc, at=3, sfx="wood_high")]),
        S(i3["capC"], "加分项 ③", [
            Card(i3["cards"][0], 260, 760, 50, at=0, sfx="pop"),
            Arrow((420, 760), (660, 760), at=1, dur=0.3, color=acc, width=12, head=36, sfx="wood_high"),
            Card(i3["cards"][1], 820, 760, 50, at=2, sfx="pop"),
            Icon("check", 540, 560, 110, color=K.GREEN, at=3, sfx="ding"),
        ]),
        S("", "3 个加分项", [
            Label(f"① {i1['name']}", 540, 560, 56, at=0, sfx="pop"),
            Label(f"② {i2['name']}", 540, 720, 56, at=1, sfx="pop", fill=K.GOLD),
            Label(f"③ {i3['name']}", 540, 880, 56, at=2, sfx="pop", fill=K.GREEN),
            Spark(540, 720, at=3, sfx="clap"),
        ], flashes=[3]),
        # 误解与翻转 32–37
        S(f"有人说{sh}", "常见误解", [
            Fig(260, G, 290, at=0, pose="point", mood="flat", color=K.OTHER, hair="bun"),
            Fig(820, G, 290, at=0, pose="point", mood="flat", color=K.OTHER2, face=-1),
            Bubble(mis["say"], 540, 560, 50, at=1, enter="pop", sfx="rim"),
        ], draw=A.ground),
        S(mis["bad"], "常见误解", [
            Fig(540, G, 320, at=0, pose="shrug", mood="surprised", **HERO),
            Icon("question", 360, 520, 90, color=K.RED, at=1, sfx="wood_high"),
            Icon("question", 720, 500, 90, color=K.RED, at=2, sfx="wood_high"),
        ], draw=A.ground),
        S("其实那叫", "常见误解", [
            Big(mis["good"], 540, 760, 220, at=0, sfx="kick", glow=True, rays=True),
            Spark(540, 760, at=2, sfx="ding"),
        ], punch=0.03, shake=[0], flashes=[0]),
        S(mis["cap"], f"{sh} · 真相", [
            Glow(540, 740, 380, at=0),
            Icon(mis["icon"], 540, 740, 230, color=acc, at=0, enter="grow", sfx="wood_low"),
            elem(s, 300, 560, 120, 1, "wood_high"), elem(s, 780, 560, 120, 2, "wood_high"),
            Spark(540, 740, at=3, sfx="ding"),
        ]),
        pops(mis["pops"][0], tag=f"{sh} · 真相", size=104),
        pops(mis["pops"][1], tag=f"{sh} · 真相", size=150, flash=1,
             extra=[elem(s, 300, 520, 120, 2, "rim"), elem(s, 780, 520, 120, 3, "rim")]),
        # 互动 38–40
        S(f"转给身边的{sh}", "互动", [
            Rays(540, 760, 520, at=0, alpha=0.18),
            Fig(440, G, 330, at=0, pose="cheer", mood="happy", **HERO),
            Spark(440, 560, at=1, sfx="clap"),
            Custom(mas, x=780, y=620, at=2, enter="pop", s=150, sfx="pop"),
        ], draw=A.ground),
        S("或者你就是", "互动", [
            Icon("phone", 320, 720, 200, color=K.INK2, at=0, sfx="wood_high"),
            Arrow((420, 720), (680, 720), at=1, dur=0.3, color=acc, width=12, head=36, sfx="wood_low"),
            Custom(mas, x=800, y=720, at=2, enter="pop", s=170, sfx="ding", glow=True),
        ]),
        S(f"是{sh}就扣起来", "互动", [
            Bubble("1", 300, 640, 70, at=0, enter="pop", sfx="pop"),
            Bubble("1", 540, 560, 80, at=1, enter="pop", sfx="pop"),
            Bubble("1", 780, 640, 70, at=2, enter="pop", sfx="pop"),
            Spark(540, 560, at=3, sfx="clap"),
        ], flashes=[3]),
        # 片尾 41
        outro(s, nxt, TITLES.get(nxt.key, "") if nxt else "", f"是{s.name}的|评论区扣个 1", mascot=mas),
    ]
    notes = [f"星座性格为大众文化中的常见印象（{s.name}：{'、'.join([i1['name'], i2['name'], i3['name']])}等），娱乐向，不作科学结论；",
             "片中没有任何统计数字或研究引用；“3 个隐藏加分项”为叙事结构，不是数据；星群形状为示意画法。",
             f"{s.name}日期按常见划分 {s.dates}；{s.element}象星座，黄道第 {s.no} 宫。"]
    return episode(s, TITLES[key], acc, shots, sp["cover"], notes, tags=sp.get("tags", ""))
