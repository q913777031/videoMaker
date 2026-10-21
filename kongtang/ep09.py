"""09 醋：饭前一勺醋，有用吗？（书中第 7 个方法：饭前来点醋）"""

import skia

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Icon, Shot, Txt

from . import kit_tang as T
from .common import GROUND, SERIES, TITLES, ending, ground, refs

ACC = "#7A5A3A"
REFS = refs("Shishehbor 等 2017，醋与餐后血糖荟萃分析，Diabetes Res Clin Pract 127:1–9")


def pop(g, k, dur=0.3):
    return clamp01(g.since(k) / dur)


def popscale(k):
    return 0.3 + 0.7 * K.ease_out_back(k, 1.8) if k > 0 else 0


def glass(c, x, y, s, level=0.8, tint=0.0, alpha=1.0):
    """一大杯水；tint 为醋的颜色深浅。"""
    with K.fade(c, alpha):
        col = K.mix("#D8ECF3", "#C99A5E", 0.45 * tint)
        K.poly(c, [(x - s * 0.32, y - s * 0.5), (x + s * 0.32, y - s * 0.5), (x + s * 0.26, y + s * 0.5),
                   (x - s * 0.26, y + s * 0.5)], "#EEF5F8")
        top = y + s * 0.5 - s * level
        k = (top - (y - s * 0.5)) / s
        K.poly(c, [(x - s * (0.32 - 0.06 * k), top), (x + s * (0.32 - 0.06 * k), top), (x + s * 0.26, y + s * 0.5),
                   (x - s * 0.26, y + s * 0.5)], col)
        K.seg(c, x - s * 0.32, y - s * 0.5, x - s * 0.26, y + s * 0.5, "#B9CCD4", 4)
        K.seg(c, x + s * 0.32, y - s * 0.5, x + s * 0.26, y + s * 0.5, "#B9CCD4", 4)


def spoon(c, x, y, s, rot=0.0, full=1.0, alpha=1.0):
    with K.at(c, x, y, rot, 1):
        with K.fade(c, alpha):
            K.rr(c, s * 0.55, 0, s * 0.8, s * 0.1, s * 0.05, "#B8B8B8")
            K.dot(c, 0, 0, s * 0.26, "#CFCFCF")
            if full > 0:
                K.dot(c, 0, 0, s * 0.2 * full, "#9C6A3A")


# ---------------------------------------------------------------- 1–2 钩子

def rumor(c, g, t, d):
    k = pop(g, 0, 0.4)
    T.food(c, "vinegar", 0, 0, 280, k, 0, popscale(k))
    k2 = pop(g, 4)
    if k2 > 0:
        K.icon(c, "megaphone", -260, -160, 140, ACC, k2, 0.6, -10, popscale(k2))
        K.text(c, "听说……", -260, -40, 34, "serif_black", K.INK2, k2)


def bottle_drink(c, g, t, d):
    T.food(c, "vinegar", 0, 0, 220, 1, -50 * ease_in_out(clamp01(g.since(0) / 0.6)))
    k = pop(g, 4, 0.25)
    if k > 0:
        K.seg(c, -170, -170, -170 + 340 * k, -170 + 340 * k, K.RED, 16)
        K.seg(c, 170, -170, 170 - 340 * k, -170 + 340 * k, K.RED, 16)


# ---------------------------------------------------------------- 5–6 书中做法

def mix_drink(c, g, t, d):
    """一勺醋倒进一大杯水：第 2 拍勺子倾斜，第 4 拍水变成淡琥珀色。"""
    tilt = ease_in_out(clamp01(g.since(2) / 0.5))
    spoon(c, -180, -230 + 60 * tilt, 260, -60 * tilt, 1 - tilt)
    pour = clamp01(g.since(2.5) / 0.6)
    if 0 < pour < 1:
        for i in range(5):
            u = (pour + i * 0.2) % 1
            K.dot(c, -110 + 40 * u, -180 + 200 * u, 8, "#9C6A3A")
    glass(c, 60, 80, 360, 0.8, ease_out(clamp01(g.since(4) / 0.6)))
    k = pop(g, 6)
    if k > 0:
        K.pill(c, -230, 160, "1 勺醋", 34, ACC, K.PAPER, k)
        K.pill(c, 330, 160, "1 大杯水", 34, "#5C8DB8", K.PAPER, k)


def before_meal(c, g, t, d):
    """时钟扇形：饭前 10–20 分钟，然后是一盘饭。"""
    k = pop(g, 0, 0.4)
    K.icon(c, "clock", -200, -20, 260, K.INK, k, 0.8, 0, popscale(k))
    sweep = 120 * ease_out(clamp01(g.since(2) / 0.8))
    if sweep > 0:
        p = skia.Path()
        p.moveTo(-200, -20)
        p.arcTo(skia.Rect.MakeLTRB(-320, -140, -80, 100), -90, sweep, False)
        p.close()
        c.drawPath(p, K.paint(ACC, 0.35))
    k2 = pop(g, 6)
    if k2 > 0:
        T.plate(c, 230, 0, 160, k2)
        T.food(c, "rice", 230, 0, 150, k2)
        K.arrow(c, (-50, -20), (60, -20), K.INK3, 8, k2, k2, 0, 22)
    K.text(c, "饭前 10–20 分钟", -200, 200, 36, "serif_black", ACC, pop(g, 4))


# ---------------------------------------------------------------- 7 机制

def slow_down(c, g, t, d):
    T.vessel(c, 0, 0, 880, 200)
    speed = 0.6 - 0.4 * ease_in_out(clamp01(g.since(4) / 1.0))
    n = 12 if g.since(4) < 0 else 7
    T.particles(c, -430, 0, 430, 0, g.t * speed / 0.6, n, 18, T.GLU, 1, 0.6)
    k = pop(g, 4)
    if k > 0:
        T.food(c, "vinegar", -330, -260, 140, k, 0, popscale(k))
        K.pill(c, 80, -260, "醋酸：可能让糖的吸收慢一点", 32, ACC, K.PAPER, k)


# ---------------------------------------------------------------- 8 研究证据

def meta(c, g, t, d):
    """荟萃分析示意：几项研究的小卡片汇成一条“下降”的结论。"""
    for i in range(5):
        k = pop(g, i * 0.5)
        if k <= 0:
            continue
        x = -340 + i * 170
        with K.at(c, x, -230, 0, popscale(k)):
            with K.paper(c, k, 0.7):
                K.rr(c, 0, 0, 130, 160, 14, K.PAPER)
            for j in range(3):
                K.rr(c, 0, -40 + j * 34, 90, 12, 6, K.LINE, k)
        if g.since(3) >= 0:
            kk = clamp01(g.since(3) / 0.5)
            K.arrow(c, (x, -140), (0, 20), K.INK3, 4, kk * 0.7, kk, 0, 16)
    k = pop(g, 5, 0.4)
    if k > 0:
        K.text_card(c, 0, 150, ["餐后血糖 ↓", "胰岛素 ↓"], 52, 520, K.PAPER, K.INK, ACC, k, 0, popscale(k), ACC,
                    "serif", 1.0)
    k2 = pop(g, 10)
    if k2 > 0:
        K.text(c, "效果中等 · 研究规模较小", 0, 360, 32, "sans_medium", K.INK2, k2)


# ---------------------------------------------------------------- 9–11 提醒

def tooth(c, g, t, d):
    """牙齿 + 食道：未稀释的醋会刺激它们。"""
    k = pop(g, 0, 0.4)
    with K.at(c, -200, 0, 0, popscale(k)):
        with K.paper(c, k, 0.8):
            K.dot(c, -40, -40, 70, "#FFFFFF")
            K.dot(c, 40, -40, 70, "#FFFFFF")
            K.rr(c, 0, 10, 180, 110, 40, "#FFFFFF")
            K.rr(c, -45, 100, 60, 120, 28, "#FFFFFF")
            K.rr(c, 45, 100, 60, 120, 28, "#FFFFFF")
    k2 = pop(g, 2)
    if k2 > 0:
        glass(c, 220, 30, 280, 0.8, 0.3, k2)
        K.icon(c, "check", 330, -130, 90, K.GREEN, pop(g, 6), 0.4)
        K.pill(c, 220, 220, "稀释后喝", 36, K.GREEN, K.PAPER, pop(g, 6))
    k3 = pop(g, 4, 0.25)
    if k3 > 0:
        K.seg(c, -330, -150, -330 + 260 * k3, 150 * (2 * k3 - 1), K.RED, 12)
        K.pill(c, -200, 240, "直接喝伤牙", 36, K.RED, K.PAPER, k3)


def ask_doctor(c, g, t, d):
    items = [("胃病", 0), ("胃食管反流", 2), ("正在用降糖药", 4)]
    for i, (lab, b) in enumerate(items):
        k = pop(g, b)
        if k > 0:
            with K.at(c, -240, -220 + i * 150, 0, popscale(k)):
                K.pill(c, 0, 0, lab, 40, K.INK2, K.PAPER, k)
    k = pop(g, 7)
    if k > 0:
        K.arrow(c, (-20, -70), (120, -70), K.INK3, 10, k, k, 0, 30)
    k2 = pop(g, 8)
    if k2 > 0:
        K.figure(c, 300, 230, 300, "point", "#E8EEF2", mood="smile", hair="short", face=-1, lift=0.7)
        K.dot(c, 300, 150, 16, K.RED, k2)
        K.text(c, "先问医生", 300, -200, 44, "serif_black", K.RED, k2)


def not_cure(c, g, t, d):
    k = pop(g, 0, 0.4)
    T.food(c, "vinegar", -200, 0, 240, k, 0, popscale(k))
    K.text(c, "≠", 0, 0, 120, "black", K.RED, pop(g, 4))
    k2 = pop(g, 6)
    if k2 > 0:
        with K.at(c, 220, 0, 0, popscale(k2)):
            with K.paper(c, k2, 0.8):
                K.rr(c, 0, 0, 200, 260, 24, K.PAPER)
            K.rr(c, 0, -60, 120, 30, 15, K.RED, k2)
            K.rr(c, 0, -60, 30, 120, 15, K.RED, k2)
            K.text(c, "治疗", 0, 70, 44, "serif_black", K.INK, k2)


# ---------------------------------------------------------------- 12 小练习

def cold_dish(c, g, t, d):
    T.plate(c, 0, 60, 260)
    T.food(c, "broccoli", -70, 50, 150, 1)
    T.food(c, "salad", 80, 60, 150, 1)
    tilt = ease_in_out(clamp01(g.since(4) / 0.5))
    T.food(c, "vinegar", 250, -250, 200, 1, -70 * tilt)
    if g.since(4.5) >= 0 and g.since(4.5) < 1.5:
        for i in range(6):
            u = ((g.since(4.5) * 1.4) + i / 6) % 1
            K.dot(c, 150 - 80 * u, -170 + 220 * u, 8, "#9C6A3A")
    k = pop(g, 10)
    if k > 0:
        K.pill(c, 0, 360, "凉拌菜加点醋", 40, ACC, K.PAPER, k)


def build() -> Episode:
    shots = [
        Shot(3, "听说饭前喝点醋，|能控血糖？", "情境演绎", [
            Custom(rumor, x=700, y=760, at=0, enter="none", sfx="wood_low", note="一瓶醋"),
            Fig(240, GROUND, 360, at=0, mood="surprised", hair="short",
                moves=[(4, dict(pose="think", sfx="bongo_high", note="主角听到传言"))]),
        ], draw=ground, note="一瓶醋，旁边喇叭传出“听说……”，主角若有所思"),
        Shot(3, "等等，|对着瓶子直接喝可不行。", "情境演绎", [
            Custom(bottle_drink, x=640, y=740, at=0, enter="fade"),
            Fig(260, GROUND, 360, at=0, enter="none", pose="reach", mood="happy", hair="short",
                moves=[(4, dict(pose="block", mood="surprised", sfx="rim", note="红叉：别直接喝"))]),
        ], draw=ground, hits=[(0, "shaker", 0.6, "瓶子倾斜")],
            note="主角举起醋瓶要喝，第 4 拍大红叉"),
        Shot(2, "书里是怎么做的？", "书中观点", [
            Icon("book", 540, 760, 300, color=ACC, at=0, enter="pop", sfx="wood_low", note="书"),
        ], text_beat=0, note="一本书弹出"),
        Shot(3, "醋：|饭前一大杯稀释醋水。", "书中观点", [
            Big("醋", 540, 470, 170, at=0, sfx="kick", sub="书中第 7 个方法", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: (glass(c, 0, 0, 300, 0.8, ease_out(clamp01(g.since(4) / 0.6))),
                                       T.food(c, "vinegar", -260, 20, 180, 1)),
                   x=540, y=930, at=0, enter="pop"),
        ], hits=[(4, "wood_high", 0.7, "水变成淡琥珀色")],
            note="drop 处“醋”砸下；一瓶醋旁边一大杯水，第 4 拍变成淡淡的琥珀色"),
        Shot(3, "书中做法：一勺醋，|兑一大杯水。", "书中观点", [
            Custom(mix_drink, x=540, y=800, at=0, enter="none"),
        ], hits=[(2, "shaker", 0.6, "勺子倾斜"), (4, "wood_low", 0.7, "水变色"), (6, "wood_high", 0.7, "标签")],
            note="一勺醋倒进一大杯水，标“1 勺醋”“1 大杯水”"),
        Shot(3, "饭前 10 到 20 分钟|喝完。", "书中观点", [
            Custom(before_meal, x=540, y=800, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "钟"), (2, "shaker", 0.7, "扇形扫过"), (6, "bongo_high", 0.7, "然后吃饭")],
            note="钟面扫出一段扇形（10–20 分钟），箭头指向一碗饭"),
        Shot(3, "醋酸可能让糖|吸收得慢一点。", "机制示意", [
            Custom(slow_down, x=540, y=820, at=0, enter="fade"),
        ], hits=[(4, "rim", 0.8, "醋出现，颗粒变慢")],
            note="血管里葡萄糖颗粒流动，第 4 拍醋出现，颗粒变少变慢（示意）"),
        Shot(4, "多项研究汇总：餐后血糖|和胰岛素有所下降。", "研究证据", [
            Custom(meta, x=540, y=800, at=0, enter="none"),
            Txt("Shishehbor 等，2017，荟萃分析", 540, 1225, 26, at=2, font="sans_medium", color=K.INK2),
        ], research=True, hits=[(0, "wood_high", 0.6, "研究卡片"), (3, "shaker", 0.6, "汇总箭头"),
                                (5, "rim", 0.8, "结论卡"), (10, "wood_low", 0.6, "“效果中等”")],
            note="五张研究小卡汇成一张结论卡：餐后血糖 ↓、胰岛素 ↓；注“效果中等 · 研究规模较小”"),
        Shot(3, "一定要稀释：|直接喝伤牙、伤食道。", "专家提醒", [
            Custom(tooth, x=540, y=800, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "牙齿"), (2, "wood_high", 0.6, "稀释的水"), (4, "rim", 0.8, "红线：直接喝伤牙"),
                 (6, "clap", 0.7, "打勾：稀释后喝")],
            note="左边牙齿被红线划过（直接喝伤牙），右边一大杯稀释醋水打勾"),
        Shot(3, "胃病、反流、用降糖药的人，|先问医生。", "专家提醒", [
            Custom(ask_doctor, x=540, y=800, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.6, "胃病"), (2, "wood_low", 0.6, "反流"), (4, "bongo_high", 0.6, "降糖药"),
                 (8, "rim", 0.8, "医生")],
            note="三个标签按拍出现：胃病、胃食管反流、正在用降糖药，箭头指向医生"),
        Shot(4, "醋只是锦上添花，|不能代替治疗。", "专家提醒", [
            Custom(not_cure, x=540, y=800, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.6, "醋"), (4, "rim", 0.8, "不等号"), (6, "wood_high", 0.7, "治疗")],
            note="醋 ≠ 治疗（医药箱）"),
        Shot(4, "小练习：凉拌菜里加点醋，|也是一种吃法。", "小练习", [
            Custom(cold_dish, x=540, y=780, at=0, enter="none"),
        ], hits=[(4, "shaker", 0.7, "醋倒进凉拌菜"), (10, "wood_high", 0.7, "标签")],
            note="一盘凉拌蔬菜，醋瓶倾斜倒醋，标“凉拌菜加点醋”"),
        Shot(2, "稀释、适量，|醋才是好帮手。", "书中观点", [
            Custom(lambda c, g, t, d: glass(c, 0, 0, 320, 0.8, 0.5), x=540, y=780, at=0, enter="pop", sfx="clap",
                   note="一大杯稀释醋水"),
        ], text_beat=0, note="一大杯淡琥珀色的稀释醋水"),
        ending(9, REFS),
    ]
    return Episode(9, "vinegar", "醋", TITLES[9], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[9]}｜控糖革命09 醋", hashtags="#控糖 #醋 #血糖 #控糖革命 #健康",
                   cover_title="饭前一勺醋，|到底【有没有用】？", cover_sub="控糖革命 · 醋",
                   cover_shot=7, cover_t=7.0,
                   notes=[
                       "“饭前来点醋”是书中第 7 个方法：饭前约 10–20 分钟，一汤匙醋兑一大杯水，用吸管喝。属书中做法，片中标注。",
                       "研究证据：Shishehbor 等（2017）荟萃分析，饭前或随餐摄入醋，餐后血糖和胰岛素曲线下面积有所降低；纳入研究规模小，"
                       "效果中等。另一项糖尿病人群的荟萃分析只在 30 分钟时点有显著差异，证据不够一致。",
                       "第 7 镜“醋酸可能让糖吸收得慢一点”为常见的机制解释（如延缓胃排空），标“可能”，画面为示意。",
                       "未稀释的醋会侵蚀牙釉质、刺激食道；有胃病、胃食管反流或正在使用降糖药的人应先咨询医生；醋不能替代治疗。",
                   ], **SERIES).build()
