"""10 自性化：怎样成为完整的自己？"""

import math

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#6B4E8E"
GROUND = A.GROUND_Y
REFS = ["Jung, C. G. (1930/1931). The Stages of Life. CW 8.",
        "Jung, C. G. (1928). The Relations between the Ego and the Unconscious. CW 7.",
        "Jung, C. G. (1962). Memories, Dreams, Reflections.（中译《回忆·梦·思考》）"]


def sun_arc(c, g, el_t, d):
    """人生如一天：太阳沿弧线升到正午，再进入下午。"""
    p = ease_in_out(clamp01(el_t / 3.4)) * d.get("to", 0.7)
    K.ring(c, 0, 220, 380, K.LINE, 6, 1, 0.5, 180)
    for s, x, y in (("清晨", -380, 270), ("正午", 0, -210), ("下午", 380, 270)):
        K.text(c, s, x, y, 34, "serif_black", K.INK2)
    a = math.radians(180 + 180 * p)
    K.dot(c, math.cos(a) * 380, 220 + math.sin(a) * 380, 56, K.GOLD)
    K.seg(c, -460, 220, 460, 220, K.INK, 5)


def unmask(c, g, el_t, d):
    """人物摘下面具：面具从脸前移到手边。"""
    k = ease_in_out(clamp01(g.since(d.get("b1", 2)) / 1.0))
    K.figure(c, 0, 0, 330, "give" if k > 0.5 else "stand", K.HERO, K.SKIN, 1, 1, "calm" if k > 0.5 else "flat", "short")
    A.mask(c, 30 + 150 * k, -300 + 100 * k, 120, K.PAPER, "smile", 1, -12 * k)


def claim(c, g, el_t, d):
    """认领阴影：影子由远处的他人身上收回到自己脚下。"""
    k = ease_out(clamp01(g.since(d.get("b1", 2)) / 1.2))
    A.shadow_self(c, 0, 0, 330, k, 1)
    K.figure(c, 0, 0, 330, "hug" if k > 0.7 else "stand", K.HERO, K.SKIN, 1, 1, "calm", "short")


def build() -> Episode:
    shots = [
        Shot(3, "人到中年|有人突然问：我是谁？", "情境演绎", [
            Fig(420, GROUND, 330, at=0, pose="stand", mood="flat", hair="short",
                moves=[(4, dict(pose="think", mood="worried"))]),
            Icon("brief", 720, 1060, 120, color=K.INK2, at=0, sfx="wood_low"),
            Bubble("我是谁？", 560, 620, 42, at=4, think=True, sfx="rim", note="冒出问题"),
        ], draw=A.ground, note="事业有成的中年人停下来问自己"),
        Shot(3, "荣格说|人生的下午有不同的任务", "荣格原著 · 大意", [
            Custom(sun_arc, x=540, y=640, at=0, sfx="wood_low"),
            Txt("《人生的阶段》，1930", 540, 1000, 32, at=4, font="sans_medium", color=K.INK2),
        ], hits=[(6, "tom", 0.7, "太阳过了正午")], note="太阳越过正午进入下午"),
        Shot(2, "向内走的这条路|叫作——", "荣格的视角", [
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 260, g.t, ease_out(clamp01(t / 1.6)), ACC), x=540, y=760, at=0),
        ], text_beat=0, hits=[(4, "rim", 0.8, "曼陀罗展开")], note="曼陀罗展开蓄势"),
        Shot(4, "成为完整的|你自己", "荣格原著 · 大意", [
            Big("自性化", 540, 600, 160, at=0, sfx="kick", sub="Individuation", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 170, g.t, 1, ACC, alpha=0.4), x=540, y=960, at=0, enter="none"),
        ], note="drop 处“自性化”砸下"),
        Shot(4, "第一步：看见面具|它不是全部的你", "机制示意", [
            Custom(unmask, x=540, y=GROUND, at=0, enter="rise", b1=2),
            Label("人格面具", 760, 560, 34, at=4, fill=A.TEAL, sfx="wood_high"),
        ], draw=A.ground, hits=[(2, "wood_low", 0.8, "摘下面具")], note="人物把面具从脸上拿开（回顾第 03 讲）"),
        Shot(4, "第二步：认领阴影|不再全推给别人", "机制示意", [
            Custom(claim, x=420, y=GROUND, at=0, enter="none", b1=2),
            Fig(860, GROUND, 300, at=0, color=K.OTHER3, mood="calm", face=-1),
            Arrow((780, 820), (520, 860), at=2, color=ACC, width=12, bend=0.2, sfx="rim", note="投射收回"),
        ], draw=A.ground, note="投射到别人身上的阴影被收回到自己脚下（回顾第 04 讲）"),
        Shot(4, "第三步：和心里的|“另一半”对话", "机制示意", [
            Custom(lambda c, g, t, d: A.sun_moon(c, 0, 0, 100, ease_in_out(clamp01(g.since(2) / 1.6))), x=540, y=760, at=0,
                   sfx="wood_low"),
        ], hits=[(2, "tom", 0.7, "日月靠拢")], note="日与月慢慢靠拢（回顾第 05 讲）"),
        Shot(2, "中心是“自性”|整个心灵的核心", "荣格原著 · 大意", [
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 230, g.t, 1, ACC), x=540, y=760, at=0, sfx="wood_high"),
            Custom(lambda c, g, t, d: K.spotlight(c, 0, 0, 140, K.GOLD, 0.6 * clamp01(t / 0.5)), x=540, y=760, at=1, enter="none"),
            Label("自性 Self", 540, 1060, 34, at=2, fill=ACC),
        ], text_beat=0, hits=[(1, "rim", 0.7, "中心亮起")], note="曼陀罗中心亮起"),
        Shot(2, "荣格常画曼陀罗|来表现它", "荣格自述", [
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 260, g.t, ease_out(clamp01(t / 1.2)), ACC, accent=K.RED),
                   x=540, y=760, at=0, sfx="wood_low"),
        ], text_beat=0, note="荣格自述 1916 年起开始画曼陀罗"),
        Shot(3, "这不是变完美|而是变完整", "荣格的视角", [
            Card("完美", 300, 720, 50, at=0, rot=-3, sfx="wood_low"),
            Icon("cross", 300, 900, 90, color=K.RED, at=2, sfx="rim"),
            Card("完整", 780, 720, 50, at=4, rot=2, accent=ACC, sfx="wood_low"),
            Icon("check", 780, 900, 90, color=K.GREEN, at=6, sfx="clap"),
        ], note="“完美”打叉，“完整”打勾"),
        Shot(3, "它没有终点|是一辈子的过程", "荣格原著 · 大意", [
            Custom(A.hero_loop, x=540, y=760, at=0, acc=ACC, sfx="wood_low"),
        ], hits=[(8, "wood_high", 0.7, "回到起点")], note="小人沿环形路走一圈"),
        Shot(2, "它难以实证|更像一张心灵地图", "常见质疑", [
            Icon("flag", 540, 760, 220, color=ACC, at=0, sfx="wood_low"),
            Icon("question", 740, 580, 90, color=K.RED, at=2, sfx="rim"),
        ], text_beat=0, note="地图上的旗子与问号"),
        Shot(2, "试试：今天|哪一面没被你看见？", "小练习", [
            Icon("mirror", 540, 760, 240, color=ACC, at=0, sfx="wood_high"),
        ], text_beat=0, note="镜子"),
        Shot(2, "十讲走完|愿你更认识自己", "荣格的视角", [
            Custom(lambda c, g, t, d: A.mandala(c, 0, 0, 220, g.t, ease_out(clamp01(t / 2)), ACC, alpha=0.5), x=540, y=700, at=0),
            Fig(300, GROUND, 280, at=0, color=K.OTHER, pose="hug", mood="smile"),
            Fig(540, GROUND, 280, at=1, color=K.HERO, pose="hug", mood="smile", hair="short"),
            Fig(780, GROUND, 280, at=2, color=K.OTHER2, pose="hug", mood="smile", hair="bun", face=-1),
        ], draw=A.ground, text_beat=0, hits=[(6, "cymbal", 0.5, "系列收尾")], note="系列收尾：三个人与曼陀罗"),
        end_shot(REFS, None),
    ]
    return Episode(10, "individuation", "自性化", "怎样成为完整的自己？", ACC, shots, refs=REFS,
                   publish_title="怎样成为完整的自己？｜荣格心理学10 自性化",
                   hashtags="#荣格 #心理学 #自性化 #自我成长 #中年",
                   cover_title="怎样成为|【完整】的自己？", cover_sub="荣格的自性化", cover_shot=7, cover_t=3.0,
                   notes=["“人生的下午”见荣格《人生的阶段》（1930 年演讲，1931 年发表，CW 8）。",
                          "自性化与自性见《自我与无意识的关系》（1928，CW 7）等；片中“面具—阴影—阿尼玛 / 阿尼姆斯”三步是常见的通俗概括，"
                          "荣格本人并未把它写成固定步骤。",
                          "荣格在《回忆·梦·思考》中自述 1916 年起画曼陀罗，并把它看作自性的表现。",
                          "自性化等概念难以实证检验，片中第 12 镜列出这一质疑。"]).build()
