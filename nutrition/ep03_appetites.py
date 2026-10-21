"""03 五种食欲：为什么吃饱了还想来点咸的？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#8C5A3B"
GROUND = A.GROUND_Y
REFS = ["劳本海默、辛普森《动物为什么吃不胖？》（后浪，2023），第 4 章「Dance of the Appetites」。",
        "Simpson, S. J., Sword, G. A., Lorch, P. D., & Couzin, I. D. (2006). Cannibal crickets on a forced march for protein and salt. PNAS, 103(11), 4152–4156."]


def swarm(c, g, el_t, d):
    """一群摩门蟋蟀向右行进；d['eat'] 拍之后后排有一只扑向前一只。"""
    for i in range(14):
        row = i % 3
        x = -420 + (i * 67) % 860 + (g.t * 40) % 67
        y = -80 + row * 90
        A.cricket(c, x, y, 120 - row * 10, g.t + i)
    if d.get("eat") is not None and g.since(d["eat"]) >= 0:
        k = ease_out(clamp01(g.since(d["eat"]) / 0.4))
        K.burst(c, 60, 10, g.since(d["eat"]), K.RED)
        K.text(c, "啊！", 60, -120, 44, "serif_black", K.RED, k)


def build() -> Episode:
    shots = [
        Shot(3, "吃完一顿大餐|为什么还想来包薯片？", "情境演绎", [
            Fig(400, GROUND, 330, at=0, pose="relax", mood="calm", hair="short", moves=[(4, dict(pose="reach", mood="happy"))]),
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 200), x=780, y=860, at=4, sfx="wood_high", note="一包薯片"),
        ], draw=A.ground, note="饱了还伸手拿薯片"),
        Shot(3, "作者认为|人不只有一种“饿”", "原书 · 大意", [
            Icon("question", 540, 760, 200, color=ACC, at=0, sfx="wood_low"),
        ], note="问号"),
        Shot(2, "而是有好几种|各自独立的——", "原书 · 大意", [
            Custom(A.gauge_row, x=540, y=780, at=0, enter="none", b0=0, vals=(0.0, 0.0, 0.0, 0.0, 0.0)),
        ], text_beat=0, hits=[(4, "rim", 0.8, "五根空条定格")], note="五根空的食欲条"),
        Shot(4, "蛋白质、碳水、脂肪|还有钠和钙", "原书 · 大意", [
            Big("五种食欲", 540, 540, 150, at=0, sfx="kick", sub="Five Appetites", note="概念落版（音乐 drop）"),
            Custom(A.gauge_row, x=540, y=960, at=2, enter="fade", b0=2),
        ], note="drop 处“五种食欲”砸下"),
        Shot(4, "每一种|都有自己的“饱了”信号", "原书 · 大意", [
            Custom(A.gauge_row, x=540, y=760, at=0, enter="none", b0=-9, vals=(0.9, 0.9, 0.9, 0.3, 0.6), hi=3),
        ], hits=[(2, "rim", 0.7, "钠还没饱")], note="其他条都满了，钠还空着"),
        Shot(4, "其中蛋白质的食欲|最强，也最不肯让步", "原书 · 大意", [
            Custom(A.gauge_row, x=540, y=760, at=0, enter="none", b0=-9, vals=(0.5, 0.9, 0.9, 0.9, 0.9), hi=0),
            Label("最强", 180, 520, 40, at=2, fill=A.PROTEIN, sfx="tom"),
        ], note="高亮蛋白质条"),
        Shot(4, "美国西部的摩门蟋蟀|会成群地长途行军", "研究证据", [
            Custom(swarm, x=540, y=780, at=0, enter="fade", sfx="wood_low"),
            Txt("Simpson 等，PNAS，2006", 540, 1080, 30, at=4, font="sans_medium", color=K.INK2),
        ], note="一大群蟋蟀向前走"),
        Shot(2, "它们缺的|是蛋白质和盐", "研究证据", [
            Custom(A.gauge_row, x=540, y=760, at=0, enter="none", b0=-9, vals=(0.15, 0.8, 0.8, 0.1, 0.6)),
        ], text_beat=0, hits=[(1, "rim", 0.7, "两根空条")], note="蛋白质和钠两根条几乎是空的"),
        Shot(2, "缺得厉害时|甚至会吃掉同伴", "研究证据", [
            Custom(swarm, x=540, y=780, at=0, enter="none", eat=1),
        ], text_beat=0, hits=[(1, "clap", 0.8, "扑向同伴")], note="后排蟋蟀扑向前面的同伴"),
        Shot(3, "喂足蛋白质和盐|吃同伴的情况就少了", "研究证据", [
            Custom(A.gauge_row, x=540, y=760, at=0, enter="none", b0=-9, vals=(0.9, 0.8, 0.8, 0.9, 0.6)),
            Icon("check", 860, 520, 110, color=K.GREEN, at=4, sfx="clap"),
        ], note="补满两根条后打勾"),
        Shot(3, "食欲背后|是身体在找缺的营养", "原书 · 大意", [
            Icon("target", 540, 760, 240, color=ACC, at=0, sfx="wood_low"),
        ], note="靶心"),
        Shot(2, "薯片又咸又油|一口戳中两种食欲", "当代理解", [
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 220), x=420, y=760, at=0, sfx="wood_low"),
            Label("钠", 700, 680, 40, at=1, fill=A.SALT, sfx="wood_high"),
            Label("脂肪", 720, 840, 40, at=2, fill=A.FAT, sfx="wood_high"),
        ], text_beat=0, note="薯片与“钠”“脂肪”标签"),
        Shot(2, "试试：馋的时候|问问自己缺什么", "小练习", [
            Bubble("我缺的是……？", 540, 720, 46, at=0, think=True, sfx="wood_high"),
        ], text_beat=0, note="思考气泡"),
        Shot(2, "下一讲：|没有大脑的黏菌", "下一讲", [
            Custom(lambda c, g, t, d: A.slime(c, 0, 0, 300, ease_out(clamp01(t / 1.4)), g.t), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 04 讲"),
        end_shot(REFS, "04 动物也会配餐：黏菌没有大脑，却会挑食"),
    ]
    return Episode(3, "appetites", "五种食欲", "为什么吃饱了还想来点咸的？", ACC, shots, refs=REFS,
                   publish_title="为什么吃饱了还想来点咸的？｜动物为什么吃不胖03 五种食欲",
                   hashtags="#动物为什么吃不胖 #营养学 #食欲 #科普",
                   cover_title="吃饱了|为什么还想【来点咸的】？", cover_sub="动物为什么吃不胖 · 五种食欲", cover_shot=4, cover_t=6.0,
                   notes=["“五种食欲”（蛋白质、碳水、脂肪、钠、钙）是原书提出的框架（日文版即以 5 appetites 为副题）；片中食欲条为示意。",
                          "摩门蟋蟀实验见 Simpson 等（2006，PNAS）：行军中的蟋蟀缺蛋白质和盐，同类相食常见；补足蛋白质和盐后同类相食减少。",
                          "“薯片同时戳中钠和脂肪食欲”为片中示例，非原书原文。本系列不构成饮食或医疗建议。"]).build()
