"""07 四种功能：你先想，还是先感受？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#8A6A2A"
GROUND = A.GROUND_Y
REFS = ["Jung, C. G. (1921). Psychologische Typen（Psychological Types）, ch. 10. CW 6.",
        "Pittenger, D. J. (1993). Measuring the MBTI… and coming up short. Journal of Career Planning and Employment, 54(1)."]


def comp(c, g, el_t, d):
    """功能罗盘：d['seq'] 为 [(拍, 高亮序号)]，按拍切换高亮；d['weak'] 标出劣势功能。"""
    hi = None
    for k, i in d.get("seq", ()):
        if g.since(k) >= 0:
            hi = i
    A.compass(c, 0, 0, d.get("r", 220), hi=hi, p=ease_out(clamp01(el_t / 1.0)) if d.get("grow") else 1, accent=ACC)
    w = d.get("weak")
    if w is not None and g.since(d.get("weak_at", 0)) >= 0:
        dx, dy = ((0, -1), (0, 1), (-1, 0), (1, 0))[w]
        r = d.get("r", 220)
        K.ring(c, dx * r, dy * r, 84, K.RED, 6, ease_out(clamp01(g.since(d.get("weak_at", 0)) / 0.4)))


def build() -> Episode:
    shots = [
        Shot(3, "同一件事|有人先分析，有人先感受", "情境演绎", [
            Fig(260, GROUND, 320, at=0, pose="think", mood="calm", hair="short"),
            Fig(820, GROUND, 320, at=0, pose="sad", mood="worried", color=K.OTHER2, hair="bun", face=-1),
            Icon("puzzle", 540, 900, 130, color=ACC, at=0, sfx="wood_low", note="同一件事"),
            Bubble("原因是什么？", 280, 620, 38, at=2, sfx="wood_high", note="左：先分析"),
            Bubble("好难受……", 800, 620, 38, at=4, sfx="wood_high", note="右：先感受"),
        ], draw=A.ground, note="同一件事，两个人的第一反应不同"),
        Shot(3, "荣格认为|人认识世界有几种基本方式", "荣格的视角", [
            Custom(comp, x=540, y=760, at=0, grow=True, sfx="wood_low", note="罗盘展开"),
            Txt("《心理类型》，1921", 540, 1080, 32, at=4, font="sans_medium", color=K.INK2),
        ], hits=[(6, "rim", 0.7, "罗盘定格")], note="四种功能罗盘"),
        Shot(2, "他把它们叫作——", "荣格的视角", [
            Custom(comp, x=540, y=760, at=0, enter="none", seq=[(0, 0), (1, 3), (2, 1), (3, 2)]),
        ], text_beat=0, hits=[(1, "wood_high", 0.6, "高亮转动"), (2, "wood_high", 0.6, "高亮转动"), (3, "wood_high", 0.6, "高亮转动")], note="高亮依次转一圈蓄势"),
        Shot(4, "思维、情感|感觉、直觉", "荣格原著 · 大意", [
            Big("四种功能", 540, 560, 150, at=0, sfx="kick", sub="Psychological Functions", note="概念落版（音乐 drop）"),
            Custom(comp, x=540, y=980, at=2, enter="fade", r=160),
        ], note="drop 处“四种功能”砸下"),
        Shot(4, "感觉：这里有什么|直觉：可能会怎样", "荣格原著 · 大意", [
            Custom(comp, x=540, y=760, at=0, enter="none", seq=[(0, 2), (4, 3)]),
            Label("接收信息", 540, 1060, 34, at=0, fill=ACC),
        ], hits=[(0, "wood_high", 0.8, "高亮感觉"), (4, "wood_high", 0.8, "高亮直觉")], note="左右一对：感觉与直觉，是接收信息的两种方式"),
        Shot(4, "思维：这是什么道理|情感：它值不值得", "荣格原著 · 大意", [
            Custom(comp, x=540, y=760, at=0, enter="none", seq=[(0, 0), (4, 1)]),
            Label("做出判断", 540, 1060, 34, at=0, fill=ACC),
        ], hits=[(0, "wood_low", 0.8, "高亮思维"), (4, "wood_low", 0.8, "高亮情感")],
            note="上下一对：思维与情感，是做判断的两种方式；“情感”指评价价值，不是情绪"),
        Shot(4, "四种人人都有|但往往一种最发达", "荣格原著 · 大意", [
            Custom(comp, x=540, y=760, at=0, enter="none", seq=[(2, 0)]),
            Label("主导功能", 540, 430, 34, at=2, fill=ACC, sfx="tom", note="主导功能亮起"),
        ], note="思维被高亮为主导功能（示意）"),
        Shot(2, "和它相对的那一种|往往最弱", "荣格原著 · 大意", [
            Custom(comp, x=540, y=760, at=0, enter="none", seq=[(0, 0)], weak=1, weak_at=1),
        ], text_beat=0, hits=[(1, "rim", 0.8, "劣势功能被圈出")], note="相对位置的情感被红圈标出：劣势功能"),
        Shot(2, "再配上内倾、外倾|就是八种类型", "荣格原著 · 大意", [
            Card("4 种功能 × 2 种态度", 540, 700, 42, at=0, accent=ACC, sfx="wood_low"),
            Big("8", 540, 900, 150, at=2, sfx="clap"),
        ], text_beat=0, note="四种功能乘两种态度"),
        Shot(3, "后来有人据此|编出了 MBTI 测试", "当代理解", [
            Card("MBTI", 540, 720, 60, at=0, accent=ACC, sfx="wood_high", note="MBTI 卡片"),
            Txt("迈尔斯与布里格斯母女，1940 年代起编制", 540, 880, 30, at=2, font="sans_medium", color=K.INK2),
        ], note="MBTI 由迈尔斯与布里格斯在荣格类型学基础上编制，不是荣格本人的测验"),
        Shot(3, "研究发现：几周后重测|不少人类型就变了", "研究证据", [
            Card("第一次：内倾 · 思维", 540, 660, 40, at=0, rot=-2, sfx="wood_low"),
            Arrow((540, 740), (540, 840), at=4, color=K.RED, width=10, sfx="rim"),
            Card("几周后：外倾 · 思维", 540, 920, 40, at=6, rot=2, accent=K.RED, sfx="wood_low"),
        ], note="同一个人重测结果改变（示意）；Pittenger（1993）综述约半数人五周后类型改变"),
        Shot(2, "类型是一面镜子|不是一张标签", "常见误区", [
            Icon("mirror", 400, 760, 200, color=ACC, at=0, sfx="wood_low"),
            Label("标签", 720, 760, 40, at=2, fill=K.INK2),
            Icon("cross", 800, 690, 90, color=K.RED, at=4, sfx="rim"),
        ], text_beat=0, note="镜子保留，标签打叉"),
        Shot(2, "试试：遇到难题|你先想，还是先感受？", "小练习", [
            Custom(comp, x=540, y=760, at=0, seq=[(0, 0), (2, 1)], r=190, sfx="wood_high"),
        ], text_beat=0, note="罗盘在思维与情感之间切换"),
        Shot(2, "下一讲：|为什么一句话就能点着你", "下一讲", [
            Custom(lambda c, g, t, d: A.stopwatch(c, 0, 0, 260, g.t), x=540, y=760, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 08 讲：情结"),
        end_shot(REFS, "08 情结：为什么一句话就能把你点着？"),
    ]
    return Episode(7, "functions", "四种功能", "你先想，还是先感受？", ACC, shots, refs=REFS,
                   publish_title="你先想，还是先感受？｜荣格心理学07 四种功能",
                   hashtags="#荣格 #心理学 #MBTI #心理类型",
                   cover_title="遇到事，你先|【想】还是先【感受】？", cover_sub="荣格的四种心理功能", cover_shot=4, cover_t=6.0,
                   notes=["四种功能与“主导 / 劣势功能”见荣格《心理类型》（1921，CW 6）第 10 章；感觉与直觉为“非理性（感知）功能”，"
                          "思维与情感为“理性（判断）功能”。片中“情感”指评价好坏、价值的功能，不等于情绪。",
                          "MBTI 由凯瑟琳·布里格斯与伊莎贝尔·迈尔斯母女在荣格类型学基础上编制，并非荣格本人的测验。",
                          "重测不稳定：Pittenger（1993）综述指出，约半数受测者在五周后重测时得到不同类型；片中第 11 镜为示意，未写具体数字。"]).build()
