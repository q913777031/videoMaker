"""05 判断与知觉：做计划的人，一定更自律吗？"""

import math

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Icon, Shot, end_shot

from . import kit_mbti as M

ACC = "#B8862A"
GROUND = 1130
SERIES = dict(series="MBTI 科普", file_prefix="MBTI")
JC, PC = M.DIM["J"], M.DIM["P"]
SHE, HE = K.OTHER3, K.HERO
REFS = ["Myers, I. B. & Myers, P. B. (1980). Gifts Differing.（中译《天生不同》）",
        "The Myers-Briggs Company. Myers-Briggs history（官网时间线）",
        "Jung, C. G. (1921). Psychologische Typen.（英译 Psychological Types, 1923）"]


def ground(g):
    K.ground(g.c, GROUND)


def progress(c, x, y, w, v, color, alpha=1.0, label=None):
    """横向进度条：v 为 0–1。"""
    K.rr(c, x, y, w, 34, 17, K.LINE, alpha)
    if v > 0.005:
        fw = max(34, w * clamp01(v))
        K.rr(c, x - w / 2 + fw / 2, y, fw, 34, 17, color, alpha)
    if label:
        K.text(c, label, x - w / 2, y - 52, 36, "sans_medium", K.INK2, alpha, "left")


def steps(g, beats, dur=0.35):
    """按拍逐级上升：返回 0–len(beats) 的连续值。"""
    return sum(ease_out(clamp01(g.since(b) / dur)) for b in beats)


# ---------------------------------------------------------------- 1 行程表

ROWS = ["周一 · 博物馆 9:00", "周二 · 海边 10:30", "周三 · 老街 14:00", "周四 · 返程 18:20"]


def itinerary(c, g, t, d):
    """一张行程表：四行按拍逐行填上并打勾。"""
    w, h = 560, 470

    def draw(c, w_, h_):
        K.text(c, "旅行计划表", 0, -h_ / 2 + 56, 40, "serif_black", K.INK)
        for i, row in enumerate(ROWS):
            y = -h_ / 2 + 140 + i * 82
            K.seg(c, -w_ / 2 + 30, y + 38, w_ / 2 - 30, y + 38, K.LINE, 3)
            k = M.appear(g, 2 + 2 * i, 0.3)
            if k > 0:
                K.text(c, row, -w_ / 2 + 44, y, 32, "sans_medium", K.INK, k, "left")
                with K.at(c, w_ / 2 - 52, y, 0, 0.3 + 0.7 * K.ease_out_back(k, 2)):
                    K.icon(c, "check", 0, 0, 40, K.GREEN, k, 0.4)

    K.card(c, 0, 0, w, h, K.PAPER, 1, 22, 1, -2, 1, JC, draw)


# ---------------------------------------------------------------- 2 机票

def ticket(c, g, t, d):
    w, h = 520, 230

    def draw(c, w_, h_):
        K.text(c, "机票", -w_ / 2 + 50, -h_ / 2 + 52, 38, "serif_black", K.INK, 1, "left")
        K.text(c, "出发 → 海边城市", -w_ / 2 + 50, 10, 32, "sans_medium", K.INK2, 1, "left")
        K.text(c, "其余：到了再说", -w_ / 2 + 50, 66, 30, "sans_medium", K.INK3, 1, "left")
        for i in range(8):
            K.dot(c, w_ / 2 - 120, -h_ / 2 + 20 + i * 27, 4, K.LINE)
        K.dot(c, w_ / 2 - 60, 0, 26, PC)

    K.card(c, 0, 0, w, h, K.PAPER, 1, 22, 1, 4, 1, PC, draw)


# ---------------------------------------------------------------- 3 谁更自律

def judge_scale(c, g, t, d):
    """天平：第 2 拍倒向行程表一侧。"""
    tilt = -12 * ease_in_out(clamp01(g.since(2) / 0.45))
    c.save()
    c.scale(1.25, 1.25)
    K.seg(c, 0, 0, 0, 250, K.DARK, 14)
    K.rr(c, 0, 255, 160, 22, 10, K.DARK)
    with K.at(c, 0, 0, tilt):
        K.seg(c, -230, 0, 230, 0, K.DARK, 12)
        for sx, col, lab in ((-230, JC, "行程表"), (230, PC, "一张机票")):
            K.seg(c, sx, 0, sx, 110, K.INK3, 4)
            with K.at(c, sx, 130, -tilt):
                K.rr(c, 0, 0, 200, 26, 12, col)
                K.text(c, lab, 0, -42, 36, "sans_medium", K.INK2)
    K.dot(c, 0, 0, 16, K.GOLD)
    c.restore()


# ---------------------------------------------------------------- 4 drop

def jp_tiles(c, g, t, d):
    for x, ch, b in ((-220, "J", 4), (220, "P", 6)):
        k = M.appear(g, b, 0.25)
        if k > 0:
            M.tile(c, x, 0, 200, ch, None, clamp01(k * 3), 1, 0, 1 + 0.4 * (1 - ease_out(k)), M.PAIR_NAMES[ch])
    k = M.appear(g, 8, 0.4)
    if k > 0:
        K.text(c, "对待外部世界的方式", 0, 300, 48, "serif_black", K.INK, k)


# ---------------------------------------------------------------- 5 J：定下来

def j_calendar(c, g, t, d):
    """J：日历上的空格按拍被填满并钉上图钉。"""
    M.tile(c, -330, -250, 120, "J")
    w, h = 640, 440
    K.card(c, 40, 30, w, h, K.PAPER, 1, 22, 1, 0, 1, JC)
    for i in range(6):
        cx, cy = 40 - w / 2 + 110 + (i % 3) * 210, 30 - 60 + (i // 3) * 170
        K.rr_stroke(c, cx, cy, 170, 130, 14, K.LINE, 4)
        k = M.appear(g, 2 + i, 0.25)
        if k > 0:
            K.rr(c, cx, cy, 150 * ease_out(k), 110, 12, K.tint(JC, 0.55), k)
            K.dot(c, cx, cy - 55, 12, K.RED, k)
    k = M.appear(g, 9, 0.4)
    if k > 0:
        K.text(c, "定了，心里才踏实", 40, 330, 40, "serif_black", JC, k)


# ---------------------------------------------------------------- 6 P：保持开放

def p_paths(c, g, t, d):
    """P：一条路分出多条岔路，每条按拍亮起一个选项，没有一条被钉死。"""
    M.tile(c, -330, -250, 120, "P")
    opts = [("看海", -300), ("爬山", -100), ("逛老街", 100), ("再看看", 300)]
    k0 = M.appear(g, 0, 0.5)
    K.seg(c, 0, 380, 0, 200, K.LINE, 28, k0)
    for i, (lab, x) in enumerate(opts):
        k = M.appear(g, 2 + 2 * i, 0.4)
        if k > 0:
            K.arrow(c, (0, 200), (x, -40), K.tint(PC, 0.2), 14, 1, k, 0.15 if x < 0 else -0.15, 34)
            with K.at(c, x, -110, 0, 0.3 + 0.7 * K.ease_out_back(k, 2)):
                K.pill(c, 0, 0, lab, 34, PC, K.PAPER, clamp01(k * 3))


# ---------------------------------------------------------------- 7 母女加上的维度

def added_pair(c, g, t, d):
    """前三对字母立在荣格的书旁；第 6 拍 J/P 这一对从上方落下，发光。"""
    M.book(c, -300, 0, 300, "心理|类型", "#6B4A3A", 1, "Jung · 1921", -3)
    for i, (a, b) in enumerate(M.PAIRS[:3]):
        x = -40 + i * 150
        M.tile(c, x, -80, 110, a)
        M.tile(c, x, 60, 110, b)
    dt = g.since(6)
    if dt > -0.3:
        dy = -380 * (1 - ease_out(clamp01((dt + 0.3) / 0.3))) if dt < 0 else -10 * math.sin(clamp01(dt / 0.25) * math.pi)
        glow = clamp01(dt / 0.4) if dt > 0 else 0
        M.tile(c, 410, -80 + dy, 110, "J", glow=glow)
        M.tile(c, 410, 60 + dy, 110, "P", glow=glow)


# ---------------------------------------------------------------- 8 误解

def crossed(c, g, t, d):
    for x, ch, word, b in ((-220, "J", "= 自律", 2), (220, "P", "= 拖延", 4)):
        M.tile(c, x - 110, 0, 160, ch)
        K.text(c, word, x + 80, 0, 64, "serif_black", K.INK2, 1)
        k = M.appear(g, b, 0.3)
        if k > 0:
            K.seg(c, x - 10, 12, x - 10 + 200 * ease_out(k), -12, K.RED, 11)
            with K.at(c, x + 80, -130, 0, 0.3 + 0.7 * K.ease_out_back(k, 2)):
                K.icon(c, "cross", 0, 0, 80, K.RED, k, 0.4)


# ---------------------------------------------------------------- 9 两条进度曲线

def two_curves(c, g, t, d):
    """同一个截止日期：J 的进度均匀上升，P 前段平缓、最后陡升；两条线同时到顶。"""
    w, h = 720, 420
    K.seg(c, -w / 2, h / 2, w / 2, h / 2, K.INK3, 5)
    K.seg(c, -w / 2, h / 2, -w / 2, -h / 2, K.INK3, 5)
    K.seg(c, w / 2, h / 2, w / 2, -h / 2 - 20, K.RED, 5)
    K.text(c, "截止", w / 2, -h / 2 - 50, 30, "sans_medium", K.RED)
    p = clamp01(g.since(0) / max(0.1, g.b(7) - g.b(0)))
    for col, fn in ((JC, lambda u: u), (PC, lambda u: u ** 3.2)):
        pts = [(-w / 2 + u * w, h / 2 - fn(u) * h) for u in [i / 60 * p for i in range(61)]]
        for a, b in zip(pts, pts[1:]):
            K.seg(c, a[0], a[1], b[0], b[1], col, 10)
    K.pill(c, -w / 2 + 70, -h / 2 + 10, "J", 32, JC)
    K.pill(c, -w / 2 + 150, -h / 2 + 10, "P", 32, PC)


# ---------------------------------------------------------------- 10/11 写报告

def desk(g):
    """凳子在人物身下，书桌在右侧。"""
    ground(g)
    c = g.c
    K.seat(c, 470, GROUND, 150, 89, K.mix(K.OTHER, K.PAPER, 0.4))
    wood = K.mix(K.OTHER, K.INK, 0.15)
    with K.paper(c, 1, 0.7):
        K.rr(c, 720, GROUND - 200, 380, 26, 10, wood)
        for lx in (560, 880):
            K.rr(c, lx, GROUND - 100, 20, 200, 6, wood)
        K.rr(c, 700, GROUND - 228, 150, 30, 6, K.PAPER)
        K.rr(c, 820, GROUND - 260, 50, 90, 8, K.tint(ACC, 0.3))


def j_progress(c, g, t, d):
    v = steps(g, (2, 4, 6, 8)) / 4
    progress(c, 0, 0, 640, v, JC, 1, "报告进度")
    for i, lab in enumerate(("第 1 天", "第 2 天", "第 3 天", "第 4 天")):
        k = M.appear(g, 2 + 2 * i)
        if k > 0:
            K.text(c, lab, -320 + 80 + i * 160, 70, 34, "sans_medium", K.INK2, k)


def p_progress(c, g, t, d):
    v = 0.08 * M.appear(g, 2) + 0.06 * M.appear(g, 4) + 0.43 * M.appear(g, 8) + 0.43 * M.appear(g, 10)
    progress(c, 0, 0, 640, v, PC, 1, "报告进度")


# ---------------------------------------------------------------- 12 都交了

def both_done(c, g, t, d):
    for x, col, ch in ((-230, JC, "J"), (230, PC, "P")):
        M.tile(c, x, -150, 120, ch)
        progress(c, x, 0, 360, 1.0, col)
        k = M.appear(g, 4 if ch == "J" else 6, 0.3)
        if k > 0:
            with K.at(c, x, 110, 0, 0.3 + 0.7 * K.ease_out_back(k, 2)):
                K.icon(c, "check", 0, 0, 110, K.GREEN, k, 0.5)


# ---------------------------------------------------------------- 13 小练习

CHOICES = [("周末安排", -230, -260), ("旅行住宿", 230, -230), ("晚饭吃什么", -230, 0), ("下周工作", 230, 30)]


def pick_one(c, g, t, d):
    """四张便签漂浮犹豫；第 8 拍其中一张被钉住、放大，其余淡出。"""
    pin = M.appear(g, 8, 0.35)
    for i, (lab, x, y) in enumerate(CHOICES):
        k = M.appear(g, i, 0.35)
        if k <= 0:
            continue
        chosen = i == 1
        bob = 12 * math.sin(g.t * 2 + i * 1.3) * (1 - pin if chosen else 1)
        a = clamp01(k * 3) * (1 - 0.6 * pin if not chosen else 1)
        sc = (0.3 + 0.7 * K.ease_out_back(k, 1.8)) * (1 + 0.18 * pin if chosen else 1)
        K.text_card(c, x, y + bob, [lab], 44, 360, K.PAPER, K.INK, ACC, a, 3 * math.sin(i + g.t), sc,
                    JC if chosen and pin > 0 else None, "serif", 0.8)
        if chosen and pin > 0:
            K.dot(c, x, y - 60, 16, K.RED, pin)


# ---------------------------------------------------------------- 14 没有对错

def balance(c, g, t, d):
    M.tile(c, -200, 0, 170, "J", sub="判断")
    M.tile(c, 200, 0, 170, "P", sub="知觉")
    k = M.appear(g, 2, 0.4)
    if k > 0:
        K.text(c, "=", 0, 0, 120, "black", ACC, k)


def build() -> Episode:
    shots = [
        # 1
        Shot(3, "出发前一周，|她的行程已经排满。", "情境演绎", [
            Fig(230, GROUND, 340, at=0, mood="happy", hair="bun", color=SHE, pose="point",
                moves=[(10, dict(pose="proud", sfx="clap", note="她满意地叉腰"))]),
            Custom(itinerary, x=680, y=760, at=0, enter="pop"),
        ], draw=ground, hits=[(2, "wood_high", 0.8, "第一行填上"), (4, "wood_low", 0.8, "第二行"),
                              (6, "wood_high", 0.8, "第三行"), (8, "wood_low", 0.8, "第四行")],
            note="她指着一张旅行计划表，四行行程按拍逐行填上、打勾"),
        # 2
        Shot(3, "他呢？|只订了一张机票。", "情境演绎", [
            Fig(820, GROUND, 340, at=0, mood="smile", hair="short", color=HE, face=-1,
                moves=[(6, dict(pose="shrug", mood="happy", sfx="bongo_low", note="他耸耸肩：到了再说"))]),
            Custom(ticket, x=400, y=760, at=2, enter="pop", sfx="wood_high", note="一张机票弹出"),
        ], draw=ground, note="他手里只有一张机票，耸耸肩：其余到了再说"),
        # 3
        Shot(2, "谁更自律？|好像一眼就能看出来。", "情境演绎", [
            Custom(judge_scale, x=540, y=700, at=0, enter="pop"),
        ], hits=[(2, "rim", 0.9, "天平倒向行程表")], note="天平两端：行程表和一张机票；天平倒向行程表"),
        # 4  drop
        Shot(3, "J/P 问的是：|你怎样对待外部世界？", "机制示意", [
            Big("判断与知觉", 540, 470, 140, at=0, sfx="kick", sub="Judging / Perceiving", note="概念落版（音乐 drop）"),
            Custom(jp_tiles, x=540, y=880, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.9, "J 牌落下"), (6, "wood_low", 0.9, "P 牌落下"),
                 (8, "shaker", 0.7, "副标题：对待外部世界的方式")],
            note="drop 处“判断与知觉”砸下；J、P 两张牌按拍落下，下方出现“对待外部世界的方式”"),
        # 5
        Shot(3, "J 倾向尽快定下来：|决定了，心里才踏实。", "机制示意", [
            Custom(j_calendar, x=540, y=800, at=0, enter="pop"),
        ], hits=[(2, "wood_high", 0.7, "第 1 格钉上"), (4, "wood_low", 0.7, "第 3 格"), (6, "wood_high", 0.7, "第 5 格"),
                 (9, "bongo_high", 0.8, "“定了，心里才踏实”")],
            note="日历六个空格按拍被填满、钉上图钉"),
        # 6
        Shot(3, "P 倾向保持开放：|多留几个选项，再看看。", "机制示意", [
            Custom(p_paths, x=540, y=820, at=0, enter="pop"),
        ], hits=[(2, "wood_high", 0.7, "岔路：看海"), (4, "wood_low", 0.7, "岔路：爬山"),
                 (6, "bongo_high", 0.7, "岔路：逛老街"), (8, "bongo_low", 0.7, "岔路：再看看")],
            note="一条路分出四条岔路，按拍亮起四个选项，没有一条被钉死"),
        # 7
        Shot(3, "这一对字母，|是迈尔斯母女加上的。", "机制示意", [
            Custom(added_pair, x=540, y=820, at=0, enter="pop"),
        ], hits=[(6, "frame", 0.9, "J/P 一对落到最右边")],
            note="荣格的书旁立着 E/I、S/N、T/F 三对字母；第 6 拍 J/P 从上方落下、发光"),
        # 8
        Shot(2, "J 不等于自律，|P 不等于拖延。", "常见误解", [
            Custom(crossed, x=540, y=800, at=0, enter="pop"),
        ], hits=[(2, "rim", 0.9, "“J = 自律”被划掉"), (4, "rim", 0.9, "“P = 拖延”被划掉")], text_beat=0,
            note="“J = 自律”“P = 拖延”两个等式按拍被红线划掉"),
        # 9
        Shot(2, "同一个截止日期，|两种节奏：", "情境演绎", [
            Custom(two_curves, x=540, y=820, at=0, enter="fade"),
        ], hits=[(0, "shaker", 0.6, "两条进度线开始画"), (7, "wood_high", 0.8, "两条线同时到顶")], text_beat=0,
            note="同一个截止日期：J 的进度线匀速上升，P 先平后陡，两条线同时到顶"),
        # 10
        Shot(3, "她提前一周，|每天写一点；", "情境演绎", [
            Fig(470, GROUND, 330, at=0, enter="none", pose="sit", mood="calm", hair="bun", color=SHE),
            Custom(j_progress, x=540, y=560, at=0, enter="fade"),
        ], draw=desk, hits=[(2, "wood_low", 0.7, "第 1 天"), (4, "wood_low", 0.7, "第 2 天"),
                            (6, "wood_low", 0.7, "第 3 天"), (8, "wood_high", 0.8, "第 4 天写完")],
            note="她坐在桌前，进度条每天涨一格，第 8 拍写满"),
        # 11
        Shot(3, "他先四处找灵感，|最后两天一口气写完。", "情境演绎", [
            Fig(470, GROUND, 330, at=0, enter="none", pose="sit", mood="calm", hair="short", color=HE,
                moves=[(8, dict(mood="surprised", pose="push", sfx="tom", note="他开始冲刺"))]),
            Custom(p_progress, x=540, y=560, at=0, enter="fade"),
            Icon("book", 230, 760, 100, color=PC, at=2, enter="pop", out=8, sfx="wood_high", note="翻书找资料"),
            Icon("bulb", 370, 700, 100, at=4, enter="pop", out=8, sfx="wood_low", note="灵感"),
            Icon("puzzle", 850, 760, 100, color=PC, at=6, enter="pop", out=8, sfx="shaker", note="拼想法"),
        ], draw=desk, hits=[(10, "bongo_high", 0.9, "一口气写完")],
            note="他先翻书、等灵感、拼想法，进度几乎不动；第 8 拍开始冲刺，第 10 拍写满"),
        # 12
        Shot(4, "两份报告都交了，|只是节奏不同。", "机制示意", [
            Custom(both_done, x=540, y=650, at=0, enter="pop"),
            Fig(310, GROUND, 300, at=0, mood="smile", hair="bun", color=SHE,
                moves=[(8, dict(pose="cheer", mood="happy", sfx="clap", note="两人都欢呼"))]),
            Fig(770, GROUND, 300, at=0, mood="smile", hair="short", color=HE, face=-1,
                moves=[(8, dict(pose="cheer", mood="happy"))]),
        ], draw=ground, hits=[(4, "wood_high", 0.8, "J 的报告打勾"), (6, "wood_low", 0.8, "P 的报告打勾")],
            note="两条满格进度条按拍打勾，两人一起欢呼"),
        # 13
        Shot(4, "找出你“必须|先定下来”的那件事。", "小练习", [
            Custom(pick_one, x=540, y=820, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.6, "便签：周末安排"), (2, "wood_low", 0.6, "便签：晚饭吃什么"),
                 (8, "frame", 0.9, "“旅行住宿”被钉住")],
            note="四张便签漂浮犹豫，第 8 拍“旅行住宿”被图钉钉住、放大，其余淡出"),
        # 14
        Shot(2, "偏好不同，|没有对错。", "机制示意", [
            Custom(balance, x=540, y=580, at=0, enter="pop", sfx="wood_high", note="J、P 两张牌并排"),
            Fig(340, GROUND, 280, at=0, mood="smile", hair="bun", color=SHE),
            Fig(740, GROUND, 280, at=0, mood="smile", hair="short", color=HE, face=-1),
        ], draw=ground, hits=[(2, "bongo_high", 0.8, "等号出现")], note="J、P 两张牌并排，中间出现等号"),
        end_shot(REFS, "06 16型：16 种人格，是怎么拼出来的？"),
    ]
    return Episode(5, "jp", "判断与知觉", "做计划的人，一定更自律吗？", ACC, shots, refs=REFS,
                   publish_title="做计划的人，一定更自律吗？｜MBTI科普05 判断与知觉",
                   hashtags="#MBTI #心理学 #J人 #P人 #人格类型",
                   cover_title="做计划的人，|一定更【自律】吗？", cover_sub="MBTI 的 J 与 P", cover_shot=8, cover_t=2.5,
                   notes=[
                       "J/P 描述的是对待外部世界的倾向：更想尽快定下来，还是保持开放；不是自律程度或能力的高低。",
                       "J/P 作为独立的第四个维度是迈尔斯母女在荣格基础上的扩展，这是通行说法（只找到二手来源）；荣格本人区分过判断功能与知觉功能，但没有把它单列为一对偏好。",
                       "第 1–3 镜、第 9–12 镜为情境演绎，两种节奏的进度曲线是示意，不是研究数据。",
                       "MBTI、Myers-Briggs Type Indicator 是 The Myers-Briggs Company 的注册商标。",
                   ], **SERIES).build()
