"""09 梦：梦在跟你说什么？"""

import math

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#3E5C8A"
GROUND = A.GROUND_Y
REFS = ["Jung, C. G. (1945/1948). On the Nature of Dreams. CW 8.",
        "Jung, C. G. (2009). The Red Book: Liber Novus. Ed. S. Shamdasani. W. W. Norton."]


def moon(c, g, el_t, d):
    """一弯月亮和几颗星，表示夜里与梦。"""
    k = ease_out(clamp01(el_t / 0.6))
    r = d.get("r", 90)
    K.dot(c, 0, 0, r * k, A.MOON)
    K.dot(c, r * 0.4, -r * 0.25, r * 0.85 * k, K.BG)
    for i, (sx, sy) in enumerate(((-180, -60), (150, 90), (-90, 120), (200, -120))):
        K.star(c, sx, sy, 18 * k * (0.8 + 0.2 * math.sin(g.t * 3 + i)), K.GOLD)


def balance(c, g, el_t, d):
    """补偿：白天（太阳一侧）的人挺胸逞强，梦里（月亮一侧）的同一个人在逃跑。"""
    K.rr(c, -230, 0, 440, 620, 24, K.mix(K.GOLD, K.BG, 0.75))
    K.rr(c, 230, 0, 440, 620, 24, K.mix(A.DEEP, K.BG, 0.35))
    K.dot(c, -340, -230, 40, K.GOLD)
    K.dot(c, 340, -230, 36, A.MOON)
    K.dot(c, 354, -240, 30, K.mix(A.DEEP, K.BG, 0.35))
    K.text(c, "白天", -230, -230, 36, "serif_black", K.INK)
    K.text(c, "梦里", 230, -230, 36, "serif_black", K.PAPER)
    K.figure(c, -230, 250, 260, "proud", K.HERO, K.SKIN, 1, 1, "happy", "short")
    k = ease_out(clamp01(g.since(d.get("b1", 4)) / 0.5))
    if k > 0:
        run = K.walk(g.t * 2.4)
        K.figure(c, 230 - 40 * math.sin(g.t * 2), 250, 260, run, K.HERO, K.SKIN, k, -1, "worried", "short")


def series(c, g, el_t, d):
    """一连串梦：几张卡片依次叠放。"""
    for i in range(4):
        k = ease_out(clamp01(g.since(i) / 0.4))
        if k <= 0:
            continue
        K.text_card(c, -270 + i * 180, -150 + i * 100, [f"梦 {i + 1}"], 40, w=180, rot=(-6 + i * 4), alpha=k)


def build() -> Episode:
    shots = [
        Shot(3, "昨晚的梦|是乱码，还是信息？", "情境演绎", [
            Fig(400, GROUND, 320, at=0, pose="think", mood="worried", hair="short"),
            Custom(moon, x=760, y=520, at=0, sfx="wood_high", note="月亮与星"),
            Bubble("？", 520, 640, 60, at=4, think=True, sfx="rim", note="醒来一头雾水"),
        ], draw=A.ground, note="醒来后对着昨晚的梦发呆"),
        Shot(3, "弗洛伊德认为|梦是伪装起来的愿望", "对照：弗洛伊德", [
            Icon("gift", 540, 720, 200, color=K.INK2, at=0, sfx="wood_low", note="包起来的礼物：伪装的愿望"),
            Label("伪装", 540, 900, 36, at=4, fill=K.INK2, sfx="wood_high"),
        ], note="对照：弗洛伊德把梦看作伪装的愿望满足"),
        Shot(2, "荣格不同意|他认为梦在——", "荣格的视角", [
            Custom(lambda c, g, t, d: A.sun_moon(c, 0, 0, 90, ease_out(clamp01(t / 1.6))), x=540, y=760, at=0),
        ], text_beat=0, hits=[(4, "rim", 0.8, "日月靠拢")], note="日与月慢慢靠拢"),
        Shot(4, "补上意识|缺了的那一面", "荣格原著 · 大意", [
            Big("补偿", 540, 600, 180, at=0, sfx="kick", sub="Compensation", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.sun_moon(c, 0, 0, 70, 1), x=540, y=930, at=2, enter="fade"),
        ], note="drop 处“补偿”砸下"),
        Shot(4, "白天太逞强|梦里可能一直在逃跑", "机制示意", [
            Custom(balance, x=540, y=760, at=0, enter="pop", sfx="wood_low", b1=4),
        ], hits=[(4, "tom", 0.8, "梦里的自己出现")], note="左：白天挺胸逞强；右：梦里同一个人在逃跑（示意）"),
        Shot(4, "梦说的是象征|不是密码", "荣格原著 · 大意", [
            Card("解梦大全", 360, 700, 44, at=0, rot=-3, sfx="wood_low", note="一本“解梦大全”"),
            Icon("cross", 360, 880, 90, color=K.RED, at=2, sfx="rim"),
            Icon("key", 760, 760, 180, color=ACC, at=4, sfx="wood_high", note="钥匙：要自己去解"),
        ], note="“解梦大全”打叉，钥匙在做梦的人手里"),
        Shot(4, "同一个象征|对不同的人意思不同", "荣格的视角", [
            Icon("water", 540, 560, 130, color=ACC, at=0, sfx="wood_low", note="同一个象征：水"),
            Fig(240, GROUND, 260, at=0, color=K.OTHER, mood="worried"),
            Fig(540, GROUND, 260, at=0, color=K.OTHER2, mood="calm", hair="bun"),
            Fig(840, GROUND, 260, at=0, color=K.OTHER3, mood="smile", face=-1),
            Bubble("危险", 240, 760, 36, at=2, sfx="wood_high"),
            Bubble("洗净", 540, 760, 36, at=4, sfx="wood_high", gain=0.85),
            Bubble("回家", 840, 760, 36, at=6, sfx="wood_high", gain=0.75),
        ], draw=A.ground, note="三个人对“水”的联想各不相同"),
        Shot(2, "所以要问做梦的人|你想到了什么", "荣格的视角", [
            Fig(540, GROUND, 320, at=0, pose="point", mood="open", hair="short"),
            Bubble("你想到了什么？", 640, 600, 38, at=1, sfx="wood_high"),
        ], draw=A.ground, text_beat=0, note="追问做梦者自己的联想"),
        Shot(2, "他也看一连串梦|而不只看一个", "荣格原著 · 大意", [
            Custom(series, x=540, y=760, at=0, enter="none"),
        ], text_beat=0, hits=[(0, "wood_low", 0.6, "梦 1"), (1, "wood_low", 0.6, "梦 2"), (2, "wood_low", 0.6, "梦 3"),
                              (3, "wood_low", 0.6, "梦 4")], note="四张“梦”卡片依次叠放"),
        Shot(3, "他还发明了“积极想象”|清醒地和意象对话", "荣格原著 · 大意", [
            Fig(360, GROUND, 320, at=0, pose="sit", mood="calm", hair="short"),
            Custom(moon, x=760, y=600, at=2, r=70),
            Bubble("你是谁？", 520, 640, 38, at=4, sfx="wood_high"),
        ], draw=A.ground, note="闭眼静坐，和浮现的意象对话"),
        Shot(3, "他自己的记录《红书》|2009 年才出版", "荣格自述", [
            Icon("book", 540, 720, 230, color=K.RED, at=0, sfx="wood_low", note="《红书》"),
            Txt("写于 1914–1930 年前后", 540, 900, 32, at=4, font="sans_medium", color=K.INK2),
        ], note="《红书》记录了荣格本人的积极想象，2009 年出版"),
        Shot(2, "这套解梦方法|很难被科学检验", "常见质疑", [
            Icon("scale", 540, 760, 240, color=K.INK2, at=0, sfx="wood_low"),
            Icon("question", 760, 560, 100, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="天平与问号"),
        Shot(2, "试试：醒来写下|梦里最强的画面", "小练习", [
            Icon("book", 540, 760, 200, color=ACC, at=0, sfx="wood_high"),
        ], text_beat=0, note="床头的本子"),
        Shot(2, "下一讲：|成为完整的自己", "下一讲", [
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 220, g.t, ease_out(clamp01(t / 1.6)), ACC), x=540, y=760, at=0,
                   sfx="wood_high"),
        ], text_beat=0, note="预告第 10 讲：自性化"),
        end_shot(REFS, "10 自性化：怎样成为完整的自己？"),
    ]
    return Episode(9, "dreams", "梦的补偿", "梦在跟你说什么？", ACC, shots, refs=REFS,
                   publish_title="梦在跟你说什么？｜荣格心理学09 梦的补偿",
                   hashtags="#荣格 #心理学 #梦 #解梦 #红书",
                   cover_title="你的梦|在跟你【说什么】？", cover_sub="荣格的梦的补偿", cover_shot=4, cover_t=6.0,
                   notes=["“梦的补偿作用”见荣格《论梦的本质》（CW 8）：梦常常补上意识态度中片面、缺失的一面。片中“白天逞强、梦里逃跑”为示意例子。",
                          "荣格反对固定的“象征词典”，主张结合做梦者本人的联想与一系列梦来理解；与弗洛伊德“伪装的愿望满足”的看法形成对照。",
                          "《红书》是荣格约 1914–1930 年间记录积极想象的手稿，2009 年由 Sonu Shamdasani 编辑出版。",
                          "荣格式释梦难以用实验检验，片中第 12 镜列出这一质疑。"]).build()
