"""08 情结：为什么一句话就能把你点着？"""

import math

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#9A4B3A"
GROUND = A.GROUND_Y
REFS = ["Jung, C. G. (1904–1907/1973). Studies in Word Association. CW 2.",
        "Jung, C. G. (1934). A Review of the Complex Theory. CW 8."]


def knot(c, g, el_t, d):
    """情结：一团缠绕的线；loose 为松开程度（0 紧 → 1 散开）。"""
    loose = d.get("loose", 0)
    loose = loose(g, el_t) if callable(loose) else loose
    r = d.get("r", 120)
    k = ease_out(clamp01(el_t / 0.6))
    for i in range(7):
        a = i / 7 * math.tau + g.t * 0.4
        off = r * (0.25 + 0.9 * loose)
        K.ring(c, math.cos(a) * off * 0.5, math.sin(a) * off * 0.4, r * (0.55 + 0.06 * i), ACC, 7, (1 - 0.6 * loose) * k)
    K.dot(c, 0, 0, r * 0.28 * (1 - loose), K.mix(ACC, K.DARK, 0.3), k)


def puppet(c, g, el_t, d):
    """情结像提线：线团悬在上方，几根线连到人物的手和头。"""
    knot(c, g, el_t, dict(r=90))
    pull = math.sin(g.t * 3) * 10
    for hx, hy in ((-70, 300 + pull), (70, 300 - pull), (0, 210)):
        K.seg(c, 0, 60, hx, hy, K.INK3, 3, ease_out(clamp01((el_t - 0.4) / 0.4)))
    K.figure(c, 0, 560, 300, "cheer" if math.sin(g.t * 3) > 0 else "point", K.HERO, K.SKIN, 1, 1, "worried", "short")


def word_rt(c, g, el_t, d):
    """字词联想：每个词配一根反应时间条，“母亲”一词明显更长。"""
    rows = (("桌子", 0.28, K.INK2), ("绿色", 0.32, K.INK2), ("母亲", 0.95, K.RED), ("跑步", 0.3, K.INK2))
    for i, (w, v, col) in enumerate(rows):
        k = ease_out(clamp01(g.since(i * 2) / 0.8))
        if k <= 0:
            continue
        y = -180 + i * 120
        K.text(c, w, -300, y, 42, "serif_black", K.INK, k)
        K.rr(c, -200 + 280 * v * k, y, 560 * v * k, 44, 10, col, k)
    K.text(c, "反应时间（示意）", 0, 330, 30, "sans_medium", K.INK3)


def build() -> Episode:
    shots = [
        Shot(3, "别人一句无心的话|你却突然炸了", "情境演绎", [
            Fig(260, GROUND, 320, at=0, pose="stand", mood="calm", hair="short",
                moves=[(6, dict(pose="fist", mood="angry"))]),
            Fig(800, GROUND, 320, at=0, color=K.OTHER2, mood="smile", hair="bun", face=-1,
                moves=[(7, dict(pose="block", mood="surprised"))]),
            Bubble("你跟你妈真像", 780, 620, 38, at=2, sfx="wood_high", note="一句随口的话"),
            Custom(lambda c, g, t, d: K.burst(c, 0, 0, t, K.RED), x=260, y=560, at=6, enter="none", sfx="clap", note="当场炸了"),
        ], draw=A.ground, note="一句随口的话让主角瞬间爆发"),
        Shot(3, "荣格年轻时|做过“字词联想”实验", "研究证据", [
            Icon("book", 540, 720, 200, color=ACC, at=0, sfx="wood_low"),
            Txt("苏黎世伯格霍尔茨利医院，1904–1907", 540, 900, 32, at=2, font="sans_medium", color=K.INK2),
        ], note="荣格在苏黎世伯格霍尔茨利医院的字词联想研究"),
        Shot(2, "念一个词|请对方说出第一个联想", "研究证据", [
            Custom(lambda c, g, t, d: A.stopwatch(c, 0, 0, 280, g.t * 3), x=540, y=760, at=0, sfx="rim"),
        ], text_beat=0, hits=[(4, "rim", 0.7, "秒表计时")], note="秒表计时"),
        Shot(4, "有些词让人卡住|背后是一团带情绪的心结", "荣格原著 · 大意", [
            Big("情结", 540, 600, 180, at=0, sfx="kick", sub="Complex", note="概念落版（音乐 drop）"),
            Custom(knot, x=540, y=930, at=2, enter="fade", r=100),
        ], note="drop 处“情结”砸下，下面是一团缠绕的线"),
        Shot(4, "反应变慢、脸红、忘词|都是被碰到的信号", "研究证据", [
            Custom(word_rt, x=600, y=760, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.7, "桌子"), (2, "wood_low", 0.7, "绿色"), (4, "tom", 0.9, "母亲：反应条明显更长"),
                 (6, "wood_low", 0.7, "跑步")], note="四个词的反应时间，“母亲”一条明显更长（示意）"),
        Shot(4, "情结像一个小人格|有自己的“意志”", "荣格原著 · 大意", [
            Custom(knot, x=540, y=700, at=0, r=140, sfx="wood_low"),
            Label("自主", 540, 960, 40, at=4, fill=ACC, sfx="wood_high"),
        ], note="线团自己转动：情结的自主性"),
        Shot(4, "荣格说：不是我们有情结|而是情结有我们", "荣格原著 · 大意", [
            Custom(puppet, x=540, y=420, at=0, sfx="tom", note="线团提着人物"),
        ], hits=[(4, "rim", 0.8, "人物被提起")], note="线团像提线，牵着人物的手和头"),
        Shot(2, "被戳中时|情绪大得不成比例", "机制示意", [
            Icon("scale", 540, 760, 240, color=ACC, at=0, sfx="wood_low"),
            Label("一句话", 380, 980, 32, at=1, fill=K.INK2),
            Label("一场火", 700, 980, 32, at=2, fill=K.RED, sfx="rim"),
        ], text_beat=0, note="天平两端：一句话 vs 一场火"),
        Shot(2, "情结人人都有|不等于有病", "常见误区", [
            Icon("check", 540, 760, 170, color=K.GREEN, at=0, sfx="clap"),
        ], text_beat=0, note="打勾"),
        Shot(3, "“情结”一词经荣格流行|阿德勒用它说“自卑情结”", "词源", [
            Card("情结 Complex", 360, 700, 42, at=0, rot=-2, accent=ACC, sfx="wood_low"),
            Arrow((480, 780), (640, 880), at=4, color=ACC, width=10, sfx="rim"),
            Card("自卑情结", 760, 940, 42, at=6, rot=2, sfx="wood_low"),
        ], note="“情结”一词经荣格推广，阿德勒提出“自卑情结”"),
        Shot(3, "被看见的情结|就没那么能摆布你", "荣格的视角", [
            Custom(knot, x=540, y=760, at=0, enter="none", r=140,
                   loose=lambda g, t: ease_out(clamp01(g.since(2) / 2.4))),
        ], hits=[(2, "wood_high", 0.7, "线团开始松开")], note="线团慢慢松开"),
        Shot(2, "试试：哪句话|最容易点着你？", "小练习", [
            Bubble("……", 540, 700, 60, at=0, sfx="wood_high"),
        ], text_beat=0, note="空白对话框"),
        Shot(2, "炸之前停一拍|问问它碰到了什么", "小练习", [
            Custom(lambda c, g, t, d: A.stopwatch(c, 0, 0, 260, 0, run=False), x=540, y=760, at=0, sfx="wood_low"),
        ], text_beat=0, note="秒表停住"),
        Shot(2, "下一讲：|梦在跟你说什么", "下一讲", [
            Custom(lambda c, g, t, d: A.sun_moon(c, 0, 0, 90, 0.6), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 09 讲：梦"),
        end_shot(REFS, "09 梦：梦在跟你说什么？"),
    ]
    return Episode(8, "complex", "情结", "为什么一句话就能把你点着？", ACC, shots, refs=REFS,
                   publish_title="为什么一句话就能把你点着？｜荣格心理学08 情结",
                   hashtags="#荣格 #心理学 #情结 #情绪",
                   cover_title="为什么【一句话】|就能把你点着？", cover_sub="荣格的情结理论", cover_shot=6, cover_t=5.0,
                   notes=["字词联想实验见荣格 1904–1907 年在苏黎世伯格霍尔茨利医院的研究（CW 2），反应变慢、重复刺激词、遗忘等被他视为“情结指标”；"
                          "片中反应时间条为示意，不是原始数据。",
                          "“不是我们有情结，而是情结有我们”为荣格 1934 年《情结理论评述》（CW 8）中说法的大意。",
                          "“自卑情结”是阿德勒的概念，借用了荣格推广的“情结”一词；片中如此表述。"]).build()
