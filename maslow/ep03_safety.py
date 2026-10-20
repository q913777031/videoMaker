"""03 安全需要：为什么人一不安就想抓紧？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#5E8C61"
GROUND = A.GROUND_Y
REFS = ["Maslow, A. H. (1943). A Theory of Human Motivation. Psychological Review, 50(4), 370–396.",
        "Maslow, A. H. (1962). Toward a Psychology of Being, ch. 4 Defense and Growth. Van Nostrand."]


def build() -> Episode:
    shots = [
        Shot(3, "刚换了新环境|心里总不踏实", "情境演绎", [
            Fig(380, GROUND, 330, at=0, pose="hug", mood="worried", hair="short"),
            Icon("cloud", 740, 520, 200, color=K.INK3, at=2, sfx="wood_low", note="乌云"),
            Icon("question", 760, 760, 100, color=K.INK2, at=6, sfx="rim"),
        ], draw=A.ground, note="新环境里抱着胳膊、心里没底"),
        Shot(3, "马斯洛说|吃饱之后，人要的是安全", "马斯洛原著 · 大意", [
            Custom(A.levels, x=540, y=760, at=0, seq=[(0, 0), (4, 1)], sfx="wood_low"),
        ], hits=[(4, "tom", 0.8, "高亮上移到安全")], note="高亮从生理上移到安全"),
        Shot(2, "这一层|叫作——", "马斯洛的视角", [
            Icon("shield", 540, 760, 260, color=ACC, at=0, sfx="rim"),
        ], text_beat=0, hits=[(4, "rim", 0.8, "盾牌定格")], note="盾牌"),
        Shot(4, "稳定、可预测|不被威胁", "马斯洛原著 · 大意", [
            Big("安全需要", 540, 600, 150, at=0, sfx="kick", sub="Safety Needs", note="概念落版（音乐 drop）"),
            Icon("shield", 540, 930, 140, color=ACC, at=2, enter="fade"),
        ], note="drop 处“安全需要”砸下"),
        Shot(4, "小孩喜欢固定的作息|规律让他安心", "马斯洛原著 · 大意", [
            Fig(400, GROUND, 220, at=0, pose="relax", mood="smile", color=K.OTHER3, hair="bun"),
            Icon("clock", 720, 700, 180, color=ACC, at=2, sfx="wood_low", note="时钟"),
            Icon("sun", 720, 470, 110, color=K.GOLD, at=4, sfx="wood_high"),
        ], draw=A.ground, note="孩子与固定作息的时钟"),
        Shot(4, "大人用存款、保险|和稳定的工作找安全", "马斯洛原著 · 大意", [
            Card("存款", 280, 760, 46, at=0, rot=-3, accent=K.GOLD, sfx="wood_low", note="存款"),
            Icon("shield", 540, 760, 150, color=ACC, at=2, sfx="wood_low", gain=0.85, note="保险"),
            Icon("brief", 800, 760, 150, color=K.DARK, at=4, sfx="wood_low", gain=0.75, note="工作"),
        ], note="存钱、保险、工作三个图标"),
        Shot(4, "安全感被拿走时|人会抓紧熟悉的东西", "机制示意", [
            Fig(420, GROUND, 330, at=0, pose="hug", mood="worried", hair="short"),
            Icon("house", 600, 1060, 130, color=ACC, at=2, sfx="wood_low"),
            Icon("cloud", 780, 520, 220, color=K.DARK, at=4, sfx="tom", note="乌云压来"),
        ], draw=A.ground, note="乌云压来，人抱紧熟悉的小房子"),
        Shot(2, "所以人在不安时|更容易求稳", "机制示意", [
            Icon("scale", 540, 760, 240, color=ACC, at=0, sfx="wood_low"),
        ], text_beat=0, note="天平偏向“稳”"),
        Shot(2, "安全是地基|不是全部", "马斯洛的视角", [
            Custom(A.levels, x=540, y=760, at=0, enter="none", fill=(1, 1, 0.2, 0.1, 0), fill_at=0),
        ], text_beat=0, hits=[(2, "rim", 0.7, "上层还空着")], note="下两层满了，上层还空着"),
        Shot(3, "太想安全|也会把人困在原地", "马斯洛的视角", [
            Fig(540, GROUND, 330, at=0, pose="sit_sad", mood="flat", hair="short"),
            Icon("house", 300, 1050, 160, color=ACC, at=0, enter="none"),
            Icon("door", 860, 880, 200, color=K.GOLD, at=4, sfx="wood_low", note="门开着没出去"),
        ], draw=A.ground, note="人缩在房子边，门开着却不出去"),
        Shot(3, "他说每一刻|都在安全与成长之间选择", "马斯洛原著 · 大意", [
            Fig(540, GROUND, 300, at=0, pose="think", mood="calm", hair="short"),
            Arrow((480, 860), (240, 760), at=2, color=ACC, width=12, sfx="wood_low"),
            Label("安全", 220, 680, 36, at=2, fill=ACC),
            Arrow((600, 860), (840, 760), at=4, color=K.GREEN, width=12, sfx="wood_high"),
            Label("成长", 860, 680, 36, at=4, fill=K.GREEN),
        ], draw=A.ground, note="岔路口：一边安全，一边成长"),
        Shot(2, "先给自己一点确定|才敢迈出一步", "马斯洛的视角", [
            Fig(540, GROUND, 320, at=0, pose="wave", mood="smile", hair="short"),
            Icon("shield", 380, 860, 110, color=ACC, at=1, sfx="wood_high"),
        ], draw=A.ground, text_beat=0, note="带着盾牌迈步"),
        Shot(2, "试试：什么|让你感到踏实？", "小练习", [
            Icon("house", 540, 760, 220, color=ACC, at=0, sfx="wood_high"),
        ], text_beat=0, note="小房子"),
        Shot(2, "下一讲：|为什么人怕孤单", "下一讲", [
            Icon("heart", 540, 760, 200, color="#C25B6A", at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 04 讲：归属与爱"),
        end_shot(REFS, "04 归属与爱：为什么一个人待久了会难受？"),
    ]
    return Episode(3, "safety", "安全需要", "为什么人一不安就想抓紧？", ACC, shots, refs=REFS,
                   publish_title="为什么人一不安就想抓紧？｜马斯洛心理学03 安全需要",
                   hashtags="#马斯洛 #心理学 #安全感",
                   cover_title="为什么一不安|就想【抓紧】？", cover_sub="马斯洛的安全需要", cover_shot=6, cover_t=6.0,
                   notes=["安全需要见马斯洛 1943 年论文：孩子偏爱不被打乱的作息与可预测的世界；成年人偏爱有保障的工作、存款和各种保险。",
                          "“每一刻都在安全与成长之间选择”为《存在心理学探索》（1962）第 4 章 Defense and Growth 中说法的大意。"]).build()
