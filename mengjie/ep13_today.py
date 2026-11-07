"""《梦的解析》13 今天再看：一百多年过去，梦的解析还靠得住吗？（白板手绘 + AI 旁白，竖屏 2:3；系列收尾）

经典问答 + 系列收尾：拿今天的研究对一对弗洛伊德的说法，最后把十三讲串起来。
- 开场：一本《梦的解析》、一条时间箭头指向“今天”、放大镜里一个问号，配音“还靠得住吗”逐字砸下；
- 痛点：小李想“几句是真的？”；弗洛伊德头上一顶皇冠“大师”，旁边一个“瞎猜”印章和骰子；
- 网上的说法（drop 在第 2 屏）：手机里的帖子乱成一团；水晶球“预言”砸下；大脑乱放电、电视雪花“乱码”；
- 1953 年：睡着的人、眼球左右快速转动、脑电图、叫醒说“在做梦”；一夜好几段，大多记不住；
- 七十年代：随机放电的火花被硬编成一本故事书，和弗洛伊德对着干；
- 后来的研究：白天的生活和梦里同一个人用红线连着；大脑把白天的书理上书架，梦是露出来的一角；
- 今天怎么看：“每个梦都是愿望”打叉，“梦和你的生活有关”打勾；预言没有证据，乱码说过头；
- 留下来的一句：弗洛伊德说“认真对待自己的梦”，盖章“和你有关”；
- 三步：床头纸笔记三个词、找白天的影子、问感受不查词典；评论区、十三讲小旗排成一排、小李在日出里醒来。
文案与出处见 mengjie/PLAN.md「### 13」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, NOTE_FILL, PAPER_W, WOOD, at_pop, bed, box, brain, draw_freud, dream_cloud, moon,
                         sleeper, sparkle, star, sun)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross

EPISODES = ["梦的解析", "愿望的满足", "伪装", "梦的材料", "凝缩", "移置", "变成画面", "二次修饰", "典型的梦", "守护睡眠",
            "噩梦", "拆梦", "今天再看"]
FLAG_COLORS = ["#F6C3BE", "#FFF1A8", "#D3EDDC", "#CFE0F5", "#E4E2F6"]


# ================================================================ 本讲小元件

def book(c, x, y, s=1.0, rot=0.0, sub=None):
    with K.at(c, x, y, rot, s):
        box(c, 0, 0, 220, 290, NIGHT, BLACK, 6, 10)
        K.text(c, "梦的", 0, -50, 54, "serif_black", "#FFE39A")
        K.text(c, "解析", 0, 20, 54, "serif_black", "#FFE39A")
        if sub:
            K.text(c, sub, 0, 100, 36, "sans_medium", "#FFE39A")
        else:
            moon(c, 0, 100, 28)


def phone(c, x, y, s=1.0):
    with K.at(c, x, y, 0, s):
        box(c, 0, 0, 150, 260, "#2E2A28", BLACK, 5, 22)
        box(c, 0, -6, 128, 210, "#CFE0F5", BLUE, 3, 10)


def crystal(c, x, y, r=150, glow=0.0):
    """水晶球：(x, y) 为球心。"""
    if glow > 0:
        c.drawCircle(x, y, r * 1.3, K.paint("#E4E2F6", 0.6 * glow))
    c.drawPath(P((x - r * 0.8, y + r * 1.25), (x - r * 0.6, y + r * 0.85), (x + r * 0.6, y + r * 0.85), (x + r * 0.8, y + r * 1.25),
                 close=True), K.paint(WOOD))
    c.drawPath(P((x - r * 0.8, y + r * 1.25), (x - r * 0.6, y + r * 0.85), (x + r * 0.6, y + r * 0.85), (x + r * 0.8, y + r * 1.25),
                 close=True), wb.marker("#A9773E", 7))
    c.drawCircle(x, y, r, K.paint("#D9D3F5"))
    c.drawCircle(x, y, r, wb.marker(NIGHT, 9))
    C.line(c, (x - r * 0.5, y - r * 0.45), (x - r * 0.25, y - r * 0.65), PAPER_W, 12)


def tv(c, x, y, T, w=300, h=230):
    box(c, x, y, w, h, "#2E2A28", BLACK, 7, 18)
    scr = skia.Rect.MakeXYWH(x - w / 2 + 22, y - h / 2 + 22, w - 44, h - 64)
    c.drawRect(scr, K.paint("#C9CCD3"))
    c.save()
    c.clipRect(scr)
    seed = int(T * 20)
    for i in range(60):
        v = (i * 7919 + seed * 104729) % 9973
        px = scr.left() + (v % 997) / 997 * scr.width()
        py = scr.top() + ((v // 7) % 991) / 991 * scr.height()
        c.drawRect(skia.Rect.MakeXYWH(px, py, 14, 6), K.paint(BLACK if i % 2 else PAPER_W))
    c.restore()
    for sg in (-1, 1):
        C.line(c, (x + sg * 30, y - h / 2), (x + sg * 80, y - h / 2 - 60), BLACK, 6)


def bolt(c, x, y, s=1.0, color=YELLOW, alpha=1.0):
    with K.at(c, x, y, 0, s):
        p = P((-10, -40), (14, -6), (-2, -4), (12, 40), (-16, 2), (0, 0), close=True)
        c.drawPath(p, K.paint("#FFE39A", alpha))
        c.drawPath(p, wb.marker(color, 5, alpha))


def sparks(c, x, y, T, t0, rad=180, n=7):
    """大脑周围随机冒火花（每 0.18 秒换一批位置）。"""
    if T < t0:
        return
    seed = int((T - t0) / 0.18)
    for i in range(n):
        v = (i * 2654435761 + seed * 40503) % 100000
        a = (v % 628) / 100
        r = rad * (0.8 + ((v // 628) % 40) / 100)
        bolt(c, x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 0.9, 0.9 + (v % 3) * 0.2)


def eeg(c, x0, y, w, T, t0, amp=40, color=RED):
    """脑电图：t0 起从左往右画出来，锯齿忽大忽小。"""
    if T < t0:
        return
    f = clamp01((T - t0) / 0.8)
    p = skia.Path()
    p.moveTo(x0, y)
    n = int(40 * f)
    for i in range(1, n + 1):
        a = amp * (1.0 if (i // 8) % 2 else 0.35)
        p.lineTo(x0 + w * i / 40, y + (a if i % 2 else -a) * (0.6 + 0.4 * math.sin(i * 1.7)))
    c.drawPath(p, wb.marker(color, 5))


def eye(c, x, y, r, T, t0):
    """眼睛特写：t0 起眼珠左右快速来回转。"""
    c.drawOval(skia.Rect.MakeXYWH(x - r * 1.5, y - r * 0.8, r * 3, r * 1.6), K.paint(PAPER_W))
    c.drawOval(skia.Rect.MakeXYWH(x - r * 1.5, y - r * 0.8, r * 3, r * 1.6), wb.marker(BLACK, 7))
    dx = r * 0.7 * math.sin((T - t0) * 18) if T >= t0 else 0.0
    c.drawCircle(x + dx, y, r * 0.55, K.paint("#5A3A2A"))
    c.drawCircle(x + dx, y, r * 0.25, K.paint(BLACK))
    if T >= t0:
        for sg in (-1, 1):
            C.line(c, (x + sg * r * 1.75, y - 20), (x + sg * r * 2.05, y - 20), GRAY, 5)
            C.line(c, (x + sg * r * 1.75, y + 20), (x + sg * r * 2.05, y + 20), GRAY, 5)


def storybook(c, x, y, s=1.0):
    with K.at(c, x, y, 0, s):
        for sg in (-1, 1):
            pg = P((0, -110), (sg * 190, -130), (sg * 190, 110), (0, 130), close=True)
            c.drawPath(pg, K.paint(PAPER_W))
            c.drawPath(pg, wb.marker(BLACK, 6))
            for r_ in range(4):
                C.line(c, (sg * 30, -60 + r_ * 45), (sg * 160, -70 + r_ * 45), GRAY, 5)


def scientist(c, x, y, s, mood="flat", alpha=1.0):
    hy = y - 290 * s
    coat = P((x - 48 * s, hy + 60 * s), (x + 48 * s, hy + 60 * s), (x + 62 * s, y - 70 * s), (x - 62 * s, y - 70 * s), close=True)
    c.drawPath(coat, K.paint(PAPER_W, alpha))
    c.drawPath(coat, wb.marker(GRAY, 5, alpha))
    draw_li(c, x, y, s, mood, alpha=alpha)
    for sg in (-1, 1):
        c.drawCircle(x + sg * 16 * s, hy - 6 * s, 13 * s, wb.marker(BLACK, 4, alpha))


def chip(c, x, y, s_, color=BLACK, fill=PAPER_W, size=50):
    w = K.text_w(s_, size, "hand") + 50
    box(c, x, y, w, size + 40, fill, color, 5, 40)
    K.text(c, s_, x, y + 2, size, "hand", color)


def flag(c, x, y, i, hi=False):
    """第 i 讲小旗（竖条燕尾旗）：(x, y) 为旗面中心，上方挂在绳上；期号在上，概念竖排。"""
    w, h = 136, 280
    fill = FLAG_COLORS[i % len(FLAG_COLORS)]
    col = L.ACC if hi else BLACK
    p = P((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (0, h / 2 - 34), (-w / 2, h / 2), close=True)
    c.drawPath(p, K.paint(fill))
    c.drawPath(p, wb.marker(col, 9 if hi else 5))
    K.text(c, f"{i + 1:02d}", 0 + x, y - h / 2 + 34, 40, "black", col)
    s_ = EPISODES[i]
    size = min(42, 160 / len(s_))
    top = y - h / 2 + 76 + size / 2
    for n, ch in enumerate(s_):
        K.text(c, ch, x, top + n * size * 1.0, size, "hand", BLACK)


# ================================================================ 开场

def _hook(H, j, cx, cy, acc):
    """开场：一本《梦的解析》→ 时间箭头指到“今天” → 放大镜里一个问号；随后“还靠得住吗”逐字砸下。"""
    b = H.b
    H.note("1899", "今天", "？")

    def bk(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc > 0:
            with K.at(c, cx - 360, cy - 220, -6, sc * 0.95):
                book(c, 0, 0, 1.0, 0, "1899")
        return None
    b.custom(j, 0, 0.3, bk, sfx="wood_low", gain=0.7)

    def arr(c, kk, T):
        dt = T - H.tb(j, 1)
        if dt < 0:
            return None
        f = ease_out(clamp01(dt / 0.35))
        c.drawPath(wb.arrow((cx - 220, cy - 220), (lerp(cx - 220, cx + 100, f), cy - 220), -0.1, 34), wb.marker(GRAY, 8))
        g = pop_scale(dt - 0.2)
        if g > 0:
            with K.at(c, cx - 50, cy - 340, 0, g):
                box(c, 0, 0, 170, 76, PAPER_W, BLUE, 5, 30)
                K.text(c, "今天", 0, 2, 46, "hand", BLUE)
        return None
    b.custom(j, 1, 1.3, arr, sfx="tom", gain=0.75)

    def mag(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        with K.at(c, cx + 330, cy - 220, 0, pop_scale(dt)):
            C.line(c, (90, 90), (180, 180), "#A9773E", 22)
            c.drawCircle(0, 0, 130, K.paint(PAPER_W))
            c.drawCircle(0, 0, 130, wb.marker(BLACK, 10))
            K.text(c, "？", 0, 6, 150, "hand", RED)
        sparkle(c, cx + 330, cy - 220, dt, YELLOW, 10, 140, 230)
        return None
    b.custom(j, 2, 2.3, mag, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("13", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）；本讲讲今天的研究怎么看这本书，并收住整季。",
    "研究：1953 年阿瑟林斯基与克莱特曼发现快速眼动睡眠；1977 年霍布森与麦卡利提出“激活—合成”假说；梦与清醒生活的连续性；睡眠参与记忆整理。",
    "现在的研究不支持“每个梦都是愿望的满足”，也没有证据表明梦能预言。小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：小李想“几句是真的？”；弗洛伊德头上皇冠“大师”，一边“瞎猜”印章和骰子
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_li = 0
k_fr = nx(j, wt(0, 0, 0.5), k_li)
k_q1 = nx(j, wt(0, 1, 0.3), k_fr)
k_crown = nx(j, wt(1, 0, 0.5), k_q1)
k_guess = nx(j, wt(1, 1, 0.6), k_crown)
GY1 = cy + 440
FR1 = (cx + 120, GY1)
L.note("几句是真的？", "大师", "瞎猜")


def li1(c, sc, T, cx=cx, cy=cy):
    x = cx - 380
    with at_pop(c, x, GY1, sc):
        C.line(c, (cx - 540, GY1), (cx + 540, GY1), BLACK, 6)
        draw_li(c, x, GY1, 0.85, "flat", rh=(x + 40, GY1 - 290 * 0.85 + 10))
    return None


ev(j, k_li, pop_fn(j, k_li, li1), "wood_low", 0.7)


def fr1(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, FR1[0], GY1, sc):
        draw_freud(c, FR1[0], GY1, 1.0, "flat")
    return None


ev(j, k_fr, pop_fn(j, k_fr, fr1), "wood_high", 0.7)


def q1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_q1))
    x, y = cx - 250, cy - 330
    if dream_cloud(c, x, y, 500, 210, sc, tail_to=(cx - 380, GY1 - 300)):
        with at_pop(c, x, y, sc):
            K.text(c, "几句是真的？", x, y + 4, 56, "hand", NIGHT)
    return None


ev(j, k_q1, q1, "pop", 0.7)


def crown1(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(1, k_crown))
    if g <= 0:
        return None
    hy = GY1 - 290
    x, y = FR1[0], hy - 90
    with K.at(c, x, y, -6, g):
        p = P((-70, 30), (-80, -40), (-38, -5), (0, -60), (38, -5), (80, -40), (70, 30), close=True)
        c.drawPath(p, K.paint("#FFD27A"))
        c.drawPath(p, wb.marker(ORANGE, 7))
        K.text(c, "大师", 0, -120, 60, "hand", GREEN)
    sparkle(c, x, y, T - tb(1, k_crown), YELLOW, 8, 90, 160)
    return None


ev(j, k_crown, crown1, "ding", 0.75)


def dice1(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(1, k_guess))
    if g <= 0:
        return None
    for i, (dx, dy, r) in enumerate(((0, 0, -12), (120, 40, 18))):
        with K.at(c, cx + 380 + dx, cy + 40 + dy, r + 200 * (1 - g), g):
            box(c, 0, 0, 100, 100, PAPER_W, BLACK, 6, 16)
            for px, py in ((-25, -25), (25, 25), (0, 0)) if i == 0 else ((-25, -25), (25, -25), (-25, 25), (25, 25)):
                c.drawCircle(px, py, 9, K.paint(RED if i == 0 else BLACK))
    return None


ev(j, k_guess, dice1, None)
ev(j, k_guess, L.stamp("瞎猜", cx + 400, cy - 170, 70, j, k_guess, rot=8), "rim", 0.85)

# ================================================================ 屏 2：网上的说法——手机里的帖子乱成一团；drop：水晶球“预言”砸下
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_ph = 1
k_posts = max(k_ph + 1, min(kq(j, wt(2, 1, 0.4), k_ph + 1), KD - 1))
k_then = min(KT.klast(j), KD + max(2, kq(j, wt(3, 2, 0.3), KD + 1) - KD))
POSTS = [("梦见蛇", -20), ("梦见掉牙", 30), ("梦见考试", -10), ("梦见下雨", 20)]
L.note(*[p_ for p_, _ in POSTS], "预言", "明天")


def ph2(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 330, cy + 300
    with at_pop(c, x, y, sc):
        with K.at(c, x, y, -6, 1.5):
            phone(c, 0, 0)
    return None


ev(j, k_ph, pop_fn(j, k_ph, ph2), "wood_low", 0.7)


def posts2(c, kk, T, cx=cx, cy=cy):
    for i, (s_, r) in enumerate(POSTS):
        g = pop_scale(T - tb(2, k_posts) - i * 0.08)
        if g <= 0:
            continue
        x, y = cx - 330 + (i % 2) * 90 - 40, cy - 330 + i * 110
        with K.at(c, x, y, r * 0.3, g):
            c.drawRoundRect(skia.Rect.MakeXYWH(-140, -42, 280, 84), 30, 30, K.paint(PAPER_W))
            c.drawPath(wb.bubble(0, 0, 280, 84, -1 if i % 2 else 1), wb.marker((BLACK, BLUE, RED, GREEN)[i], 6))
            K.text(c, s_, 0, 2, 46, "hand", (BLACK, BLUE, RED, GREEN)[i])
    return None


ev(j, k_posts, posts2, "pop", 0.7)


def ball2(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(2, KD)
    g = C.slam_scale(dt)
    if g <= 0:
        return None
    x, y = cx + 250, cy - 170
    with K.at(c, x, y, 0, g):
        crystal(c, 0, 0, 170, 0.6 + 0.4 * math.sin(T * 4))
        dream_cloud(c, 0, -10, 180, 120, 1.0)
        star(c, 0, -10, 30)
    sparkle(c, x, y, dt, NIGHT, 12, 190, 300)
    return None


ev(j, KD, ball2, "kick", 0.95)
ev(j, KD, L.slam_text("预言", cx + 250, cy + 170, 120, NIGHT, j, KD, rot=-5), None)


def then2(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(2, k_then))
    if g <= 0:
        return None
    with K.at(c, cx + 250, cy + 400, 4, g):
        box(c, 0, 0, 240, 150, PAPER_W, BLACK, 6, 12)
        c.drawRect(skia.Rect.MakeXYWH(-120, -75, 240, 50), K.paint(RED))
        K.text(c, "明天", 0, 20, 56, "hand", BLACK)
        c.drawPath(check(90, 20, 30), wb.marker(GREEN, 8))
    return None


if k_then > KD:
    ev(j, k_then, then2, "ding", 0.7)

# ================================================================ 屏 3：大脑乱放电，电视雪花“乱码”
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_br = kq(j, wt(4, 0, 0.5), 0)
k_sp = nx(j, wt(4, 1, 0.5), k_br)
k_tv = nx(j, wt(4, 2, 0.4), k_sp)
L.note("乱放电", "乱码", "？？")


def br3(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 180, cy - 220
    with at_pop(c, x, y, sc):
        brain(c, x, y, 170)
        if T >= tb(3, k_sp):
            K.text(c, "乱放电", x, y + 250, 64, "hand", ORANGE)
    sparks(c, x, y, T, tb(3, k_sp), 230, 8)
    return None


ev(j, k_br, pop_fn(j, k_br, br3), "wood_low", 0.7)
b.hit(j, k_sp, "shaker", 0.75, "火花乱冒")


def tv3(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(3, k_tv))
    if g <= 0:
        return None
    x, y = cx + 250, cy + 240
    with at_pop(c, x, y, g):
        tv(c, x, y, T, 380, 290)
        K.text(c, "乱码", x, y + 220, 64, "hand", GRAY)
        K.text(c, "？？", x + 260, y - 160, 70, "hand", RED)
    return None


ev(j, k_tv, tv3, "rim", 0.8)

# ================================================================ 屏 4：1953 年——睡着的人、眼球快速转动、脑电图；叫醒说在做梦；一夜好几段，大多记不住
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_bed4 = 0
k_yr = nx(j, wt(6, 0, 0.4), k_bed4)
k_eye = nx(j, wt(6, 3, 0.3), k_yr)
k_wake = nx(j, wt(6, 4, 0.5), k_eye)
k_night = nx(j, wt(7, 0, 0.5), k_wake)
k_forget = nx(j, wt(7, 2, 0.5), k_night)
BED4 = (cx - 520, cy + 400)
HIP4 = (BED4[0] + 230, BED4[1] - 20)
L.note("1953", "在做梦", "一夜", "记不住", "做梦")


def bed4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_bed4))
    if sc <= 0:
        return None
    with at_pop(c, cx - 260, BED4[1], sc):
        bed(c, *BED4, 520)
        sleeper(c, *HIP4, 0.75, T, tb(4, k_wake), "smile")
    return None


ev(j, k_bed4, bed4, "wood_low", 0.7)


def yr4(c, kk, T, cx=cx, cy=cy):
    g = C.slam_scale(T - tb(4, k_yr))
    if g <= 0:
        return None
    with K.at(c, cx - 380, cy - 440, -5, g):
        box(c, 0, 0, 260, 120, NOTE_FILL, ORANGE, 7, 12)
        K.text(c, "1953", 0, 2, 76, "black", ORANGE)
    return None


ev(j, k_yr, yr4, "tom", 0.8)


def lab4(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(4, k_eye))
    if g <= 0:
        return None
    ex, ey = cx + 20, cy - 420
    with at_pop(c, ex, ey, g):
        c.drawCircle(ex, ey, 130, K.paint("#FFF4D6"))
        c.drawCircle(ex, ey, 130, wb.marker(ORANGE, 7))
        eye(c, ex, ey, 60, T, tb(4, k_eye))
    mx, my = cx + 380, cy - 420
    with at_pop(c, mx, my, g):
        box(c, mx, my, 320, 230, "#2E2A28", BLACK, 7, 16)
        c.drawRect(skia.Rect.MakeXYWH(mx - 140, my - 95, 280, 170), K.paint("#10301C"))
        eeg(c, mx - 130, my - 30, 260, T, tb(4, k_eye), 26, "#7CFC9A")
        eeg(c, mx - 130, my + 40, 260, T, tb(4, k_eye) + 0.2, 16, "#FFE39A")
    return None


ev(j, k_eye, lab4, "shaker", 0.75)
ev(j, k_wake, L.pop_bubble("在做梦", cx - 220, cy + 120, j, k_wake, 56, NIGHT, tail=-1), "ding", 0.8)


def night4(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(4, k_night))
    if g <= 0:
        return None
    x0, x1, y = cx - 520, cx + 520, cy - 150
    forget = T >= tb(4, k_forget)
    with at_pop(c, cx, y, g):
        K.text(c, "一夜", x0 + 60, y - 70, 50, "hand", NIGHT)
        moon(c, x0 + 170, y - 74, 26)
        C.line(c, (x0, y), (x1, y), NIGHT, 7)
        for i, (a, w_) in enumerate(((0.18, 0.06), (0.38, 0.08), (0.58, 0.1), (0.8, 0.13))):
            xa = lerp(x0, x1, a)
            box(c, xa + lerp(0, x1 - x0, w_) / 2, y - 30, lerp(0, x1 - x0, w_), 50, "#E4E2F6", NIGHT, 5, 8)
            if forget:
                dream_cloud(c, xa + lerp(0, x1 - x0, w_) / 2, y - 110, 100, 60, 1.0, alpha=0.25 if i < 3 else 1.0)
    if forget:
        g2 = pop_scale(T - tb(4, k_forget))
        with K.at(c, cx + 260, y + 120, -4, g2):
            K.text(c, "记不住", 0, 0, 64, "hand", RED)
    return None


ev(j, k_night, night4, "pop", 0.7)
b.hit(j, k_forget, "rim", 0.75, "大多记不住")

# ================================================================ 屏 5：七十年代——火花被硬编成故事书；和弗洛伊德对着干
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_tag = kq(j, wt(8, 0, 0.4), 0)
k_spark = nx(j, wt(8, 1, 0.6), k_tag)
k_story = nx(j, wt(8, 2, 0.5), k_spark)
k_vs = nx(j, wt(9, 1, 0.4), k_story)
GY5 = cy + 440
L.note("70年代", "故事", "对着干")


def tag5(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 380, cy - 450, sc):
        with K.at(c, cx - 380, cy - 450, -5):
            box(c, 0, 0, 290, 110, NOTE_FILL, ORANGE, 7, 12)
            K.text(c, "70年代", 0, 2, 64, "hand", ORANGE)
    return None


ev(j, k_tag, pop_fn(j, k_tag, tag5), "tom", 0.75)


def brain5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_spark))
    if sc <= 0:
        return None
    x, y = cx - 260, cy - 180
    with at_pop(c, x, y, sc):
        brain(c, x, y, 130)
    sparks(c, x, y, T, tb(5, k_spark), 170, 6)
    if T >= tb(5, k_story):
        f = ease_in_out(clamp01((T - tb(5, k_story)) / 0.6))
        for i in range(5):
            sx, sy = x + 150, y - 120 + i * 60
            bolt(c, lerp(sx, cx + 250, f), lerp(sy, cy - 200, f), 0.9 * (1 - f) + 0.3, YELLOW, 1 - f * 0.8)
    return None


ev(j, k_spark, brain5, "shaker", 0.75)


def story5(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(5, k_story) - 0.4)
    if g <= 0:
        return None
    with K.at(c, cx + 270, cy - 200, -4, g):
        storybook(c, 0, 0, 1.0)
        K.text(c, "故事", 0, -190, 64, "hand", NIGHT)
    return None


ev(j, k_story, story5, "pop", 0.7)


def vs5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_story) - 0.6)
    if sc <= 0:
        return None
    clash = T >= tb(5, k_vs)
    with at_pop(c, cx, GY5, sc):
        C.line(c, (cx - 540, GY5), (cx + 540, GY5), BLACK, 6)
        draw_freud(c, cx - 380, GY5, 0.85, "flat")
        scientist(c, cx + 380, GY5, 0.85, "flat")
    if clash:
        f = ease_out(clamp01((T - tb(5, k_vs)) / 0.25))
        y = GY5 - 180
        c.drawPath(wb.arrow((cx - 280, y), (lerp(cx - 280, cx - 30, f), y), 0.0, 40), wb.marker(NIGHT, 10))
        c.drawPath(wb.arrow((cx + 280, y), (lerp(cx + 280, cx + 30, f), y), 0.0, 40), wb.marker(ORANGE, 10))
        sparkle(c, cx, y, T - tb(5, k_vs), RED, 10, 60, 150)
    return None


b.custom(j, k_story, k_story + 0.3, vs5)
ev(j, k_vs, L.slam_text("对着干", cx, cy + 90, 100, RED, j, k_vs, rot=-4), "kick", 0.85)
b.shots[j].shake = [(k_vs, 7.0)]

# ================================================================ 屏 6：后来的研究——白天和梦里用红线连着；大脑整理书架，梦是露出来的一角
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_day = kq(j, wt(10, 0, 0.5), 0)
k_link = nx(j, wt(10, 1, 0.5), k_day)
k_shelf = nx(j, wt(11, 0, 0.6), k_link)
k_corner = nx(j, wt(11, 1, 0.6), k_shelf)
L.note("白天", "梦里", "整理", "一角")


def day6(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 290, cy - 290
    with at_pop(c, x, y, sc):
        box(c, x, y, 440, 380, "#FFF4D6", ORANGE, 7, 16)
        K.text(c, "白天", x - 140, y - 150, 46, "hand", ORANGE)
        sun(c, x + 150, y - 110, 36)
        c.drawRect(skia.Rect.MakeXYWH(x - 180, y + 70, 360, 22), K.paint(WOOD))
        draw_li(c, x - 70, y + 170, 0.5, "flat")
        draw_boss(c, x + 100, y + 170, 0.5, mood="flat")
    return None


ev(j, k_day, pop_fn(j, k_day, day6), "wood_low", 0.7)


def link6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_day) - 0.3)
    x, y = cx + 280, cy - 290
    if dream_cloud(c, x, y, 440, 380, sc):
        with at_pop(c, x, y, sc):
            K.text(c, "梦里", x - 120, y - 120, 46, "hand", NIGHT)
            draw_boss(c, x + 10, y + 140, 0.5, mood="smile")
            moon(c, x + 140, y - 100, 30)
    if T >= tb(6, k_link):
        f = ease_out(clamp01((T - tb(6, k_link)) / 0.5))
        a, z = (cx - 190, cy - 290), (cx + 280, cy - 290)
        p = skia.Path()
        p.moveTo(*a)
        p.quadTo((a[0] + z[0]) / 2, a[1] - 160, lerp(a[0], z[0], f), lerp(a[1], z[1], f) - 160 * 4 * f * (1 - f) * 0.5)
        c.drawPath(p, wb.marker(RED, 8))
        c.drawPath(C.heart_path((a[0] + z[0]) / 2, a[1] - 90, 26), K.paint("#F6C3BE", f))
    return None


ev(j, k_day, link6, None)
b.hit(j, k_link, "ding", 0.75, "红线连着")


def shelf6(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(6, k_shelf))
    if g <= 0:
        return None
    bx, by = cx - 300, cy + 280
    sx, sy = cx + 160, cy + 280
    with at_pop(c, cx, cy + 280, g):
        brain(c, bx, by, 130)
        K.text(c, "整理", bx, by - 160, 56, "hand", RED)
        box(c, sx, sy, 380, 380, WOOD, "#A9773E", 7, 8)
        for r_ in range(3):
            y_ = sy - 130 + r_ * 125
            c.drawRect(skia.Rect.MakeXYWH(sx - 180, y_ + 50, 360, 12), K.paint("#A9773E"))
            n = 6
            for m in range(n):
                f = clamp01((T - tb(6, k_shelf) - (r_ * n + m) * 0.04) / 0.2)
                if f > 0:
                    col = ("#F6C3BE", "#CFE0F5", "#D3EDDC", "#FFF1A8")[(r_ + m) % 4]
                    rr = skia.Rect.MakeXYWH(sx - 160 + m * 52, y_ - 40 + (1 - f) * -60, 40, 90)
                    c.drawRect(rr, K.paint(col))
                    c.drawRect(rr, wb.marker(BLACK, 4))
        c.drawPath(wb.arrow((bx + 160, by), (sx - 210, sy), 0.15, 30), wb.marker(GRAY, 6))
    return None


ev(j, k_shelf, shelf6, "wood_high", 0.7)


def corner6(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(6, k_corner))
    if g <= 0:
        return None
    x, y = cx + 300, cy + 70
    with at_pop(c, x, y, g):
        dream_cloud(c, x, y, 200, 130, 1.0)
        star(c, x, y, 28)
        K.text(c, "一角", x + 160, y + 60, 54, "hand", NIGHT)
    return None


ev(j, k_corner, corner6, "pop", 0.75)

# ================================================================ 屏 7：今天怎么看——“每个梦都是愿望”打叉、“梦和你的生活有关”打勾；预言没证据、乱码说过头
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_c1 = kq(j, wt(12, 0, 0.6), 0)
k_x1 = nx(j, wt(12, 1, 0.3), k_c1)
k_c2 = nx(j, wt(12, 1, 0.8), k_x1)
k_ok = nx(j, wt(12, 2, 0.5), k_c2)
k_pre = nx(j, wt(13, 1, 0.3), k_ok)
k_over = nx(j, wt(13, 2, 0.4), k_pre)
L.note("每个梦都是愿望", "梦和你的生活有关", "预言", "没证据", "乱码", "过头了")


def cards7(c, kk, T, cx=cx, cy=cy):
    for i, (s_, k_, col) in enumerate((("每个梦都是愿望", k_c1, GRAY), ("梦和你的生活有关", k_c2, GREEN))):
        g = pop_scale(T - tb(7, k_))
        if g <= 0:
            continue
        y = cy - 410 + i * 240
        with K.at(c, cx - 40, y, (-2, 2)[i], g):
            box(c, 0, 0, 900, 170, "#D3EDDC" if i and T >= tb(7, k_ok) else PAPER_W, col, 7, 20)
            K.text(c, s_, -20, 4, 72, "hand", BLACK)
    if T >= tb(7, k_x1):
        f = clamp01((T - tb(7, k_x1)) / 0.25)
        c.drawPath(wb.partial(cross(cx + 440, cy - 410, 70), f)[0], wb.marker(RED, 14))
        C.line(c, (cx - 430, cy - 406), (lerp(cx - 430, cx + 340, f), cy - 406), RED, 7)
    if T >= tb(7, k_ok):
        g = C.slam_scale(T - tb(7, k_ok))
        with K.at(c, cx + 440, cy - 170, 0, g):
            c.drawPath(check(0, 0, 80), wb.marker(GREEN, 16))
    return None


ev(j, k_c1, cards7, "wood_low", 0.7)
b.hit(j, k_x1, "rim", 0.85, "这一句站不住")
b.hit(j, k_c2, "wood_high", 0.7, "第二张卡")
b.hit(j, k_ok, "kick", 0.9, "这一句站得住")
b.shots[j].shake = [(k_ok, 7.0)]


def bottom7(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(7, k_pre))
    if g <= 0:
        return None
    x, y = cx - 280, cy + 230
    with at_pop(c, x, y, g):
        crystal(c, x, y - 20, 100)
        c.drawPath(cross(x, y - 20, 90), wb.marker(RED, 12))
        K.text(c, "预言", x, y + 170, 54, "hand", NIGHT)
        K.text(c, "没证据", x, y + 250, 54, "hand", RED)
    if T >= tb(7, k_over):
        g2 = pop_scale(T - tb(7, k_over))
        x2 = cx + 280
        with at_pop(c, x2, y, g2):
            tv(c, x2, y - 20, T, 260, 200)
            K.text(c, "乱码", x2, y + 170, 54, "hand", GRAY)
            K.text(c, "过头了", x2, y + 250, 54, "hand", ORANGE)
    return None


ev(j, k_pre, bottom7, "pop", 0.7)
b.hit(j, k_over, "tom", 0.75, "说过头了")

# ================================================================ 屏 8：留下来的一句——弗洛伊德：“认真对待自己的梦”；小李和梦连着，盖章“和你有关”
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_fr8 = kq(j, wt(14, 0, 0.4), 0)
k_say = nx(j, wt(14, 1, 0.6), k_fr8)
k_you = nx(j, wt(14, 2, 0.4), k_say)
GY8 = cy + 440
L.note("认真对待自己的梦", "和你有关")


def fr8(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, GY8, sc):
        C.line(c, (cx - 540, GY8), (cx + 540, GY8), BLACK, 6)
        draw_freud(c, cx - 330, GY8, 1.05, "smile")
        draw_li(c, cx + 330, GY8, 0.95, "smile")
        dream_cloud(c, cx + 260, cy - 120, 380, 240, 1.0, tail_to=(cx + 330, GY8 - 330))
        moon(c, cx + 200, cy - 120, 46)
        star(c, cx + 330, cy - 130, 36)
    return None


ev(j, k_fr8, pop_fn(j, k_fr8, fr8), "wood_low", 0.7)
ev(j, k_say, L.pop_bubble("认真对待自己的梦", cx - 140, cy - 420, j, k_say, 58, NIGHT, tail=-1), "pop", 0.75)


def you8(c, kk, T, cx=cx, cy=cy):
    t0 = tb(8, k_you)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.4))
    p = skia.Path()
    p.moveTo(cx + 120, cy - 60)
    p.quadTo(cx + 40, cy + 40, lerp(cx + 120, cx + 290, f), lerp(cy - 60, GY8 - 330, f))
    c.drawPath(p, wb.marker(RED, 7))
    c.drawPath(C.heart_path(cx + 60, cy + 30, 34), K.paint("#F6C3BE", f))
    c.drawPath(C.heart_path(cx + 60, cy + 30, 34), wb.marker(RED, 5, f))
    return None


ev(j, k_you, you8, None)
ev(j, k_you, L.stamp("和你有关", cx + 10, cy + 230, 66, j, k_you, rot=-6), "kick", 0.85)
b.shots[j].shake = [(k_you, 6.0)]

# ================================================================ 屏 9：这一季讲到这儿——合上的书；小李；“三步”
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_bk9 = kq(j, wt(15, 0, 0.4), 0)
k_li9 = nx(j, wt(15, 1, 0.3), k_bk9)
k_3 = nx(j, wt(15, 2, 0.4), k_li9)
GY9 = cy + 430
L.note("第一季", "三步")


def bk9(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 300, cy - 280, sc):
        book(c, cx - 300, cy - 280, 1.1, -6, "第一季")
    return None


ev(j, k_bk9, pop_fn(j, k_bk9, bk9), "wood_low", 0.7)


def li9(c, sc, T, cx=cx, cy=cy):
    x = cx - 250
    with at_pop(c, x, GY9, sc):
        C.line(c, (x - 300, GY9), (x + 300, GY9), BLACK, 7)
        hy = GY9 - 290 * 0.95
        draw_li(c, x, GY9, 0.95, "smile", rh=(x + 110, hy - 10))
    return None


ev(j, k_li9, pop_fn(j, k_li9, li9), "pop", 0.7)


def three9(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(9, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 270, cy - 30, -4, sc):
        c.drawCircle(0, 0, 190, K.paint("#E4E2F6"))
        c.drawCircle(0, 0, 190, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 130, "hand", L.ACC)
    return None


ev(j, k_3, three9, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 10：第一步——床头放纸笔，醒来先记三个词
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_h10 = kq(j, wt(16, 0, 0.3), 0)
k_pad = nx(j, wt(16, 1, 0.5), k_h10)
k_w = [nx(j, wt(16, 2, 0.5), k_pad)]
k_w += [cap(j, k_w[0] + 1), cap(j, k_w[0] + 2)]
WORDS10 = ["海边", "迟到", "老同学"]
BED10 = (cx - 540, cy + 380)
L.note("第一", "床头放纸笔", *WORDS10)


def h10(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 470, sc):
        K.text(c, "第一", cx - 380, cy - 470, 70, "hand", L.ACC)
        K.text(c, "床头放纸笔", cx - 40, cy - 470, 60, "hand", BLACK)
    with at_pop(c, cx - 200, BED10[1], sc):
        bed(c, *BED10, 520)
        sleeper(c, BED10[0] + 230, BED10[1] - 20, 0.75, T, tb(10, k_w[0]) - 0.4, "smile")
    return None


ev(j, k_h10, pop_fn(j, k_h10, h10), "wood_low", 0.7)


def pad10(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(10, k_pad))
    if g <= 0:
        return None
    x, y = cx + 300, cy + 20
    with at_pop(c, x, y + 300, g):
        box(c, x, y + 300, 300, 200, WOOD, "#A9773E", 7, 8)
        with K.at(c, x - 10, y - 30, 3):
            box(c, 0, 0, 380, 420, NOTE_FILL, ORANGE, 7, 10)
            for i, w in enumerate(WORDS10):
                yy = -120 + i * 120
                C.line(c, (-150, yy + 40), (150, yy + 40), "#E3C79A", 4)
                gg = pop_scale(T - tb(10, k_w[i]))
                if gg > 0:
                    with K.at(c, 0, yy, 0, gg):
                        K.text(c, w, 0, 0, 68, "hand", BLACK)
        A.pen(c, x + 190, y + 200, -40, 1.0)
    return None


ev(j, k_pad, pad10, "wood_high", 0.7)
for i, k_ in enumerate(k_w):
    b.hit(j, k_, "pop", 0.7, f"记下：{WORDS10[i]}")

# ================================================================ 屏 11：第二步——找白天的影子：梦里迟到 → 周一例会
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_h11 = kq(j, wt(17, 0, 0.3), 0)
k_shadow = nx(j, wt(17, 1, 0.6), k_h11)
k_like = nx(j, wt(17, 2, 0.4), k_shadow)
L.note("第二", "白天的影子", "梦里迟到", "周一", "例会", "像")


def cl11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_h11))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy - 470, sc):
        K.text(c, "第二", cx - 380, cy - 470, 70, "hand", L.ACC)
        K.text(c, "白天的影子", cx - 40, cy - 470, 60, "hand", BLACK)
    x, y = cx - 200, cy - 180
    if dream_cloud(c, x, y, 560, 380, sc):
        with at_pop(c, x, y, sc):
            ph = T * 9
            draw_li(c, x - 40, y + 130, 0.55, "sad", lh=(x - 90, y + 40 + 10 * math.sin(ph)), rh=(x + 10, y + 40 - 10 * math.sin(ph)))
            for i in range(3):
                C.line(c, (x - 130 - i * 10, y - 20 + i * 40), (x - 190 - i * 10, y - 20 + i * 40), GRAY, 5)
            c.drawCircle(x + 140, y - 30, 56, K.paint(PAPER_W))
            c.drawCircle(x + 140, y - 30, 56, wb.marker(RED, 7))
            C.line(c, (x + 140, y - 30), (x + 140, y - 66), BLACK, 6)
            C.line(c, (x + 140, y - 30), (x + 168, y - 30), BLACK, 6)
            K.text(c, "梦里迟到", x, y + 175, 46, "hand", NIGHT)
    return None


ev(j, k_h11, cl11, "pop", 0.7)


def shadow11(c, kk, T, cx=cx, cy=cy):
    t0 = tb(11, k_shadow)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.5))
    x, y = cx + 250, cy + 270
    sh = skia.Path()
    sh.addOval(skia.Rect.MakeXYWH(cx - 420, cy + 130, 440 * f, 90))
    c.drawPath(sh, K.paint("#9AA6B8", 0.45))
    c.drawPath(wb.arrow((cx - 60, cy + 40), (lerp(cx - 60, x - 180, f), lerp(cy + 40, y - 40, f)), 0.2, 30), wb.marker(NIGHT, 7))
    g = pop_scale(T - t0 - 0.2)
    if g > 0:
        with K.at(c, x, y, 4, g):
            box(c, 0, 0, 340, 300, PAPER_W, BLACK, 7, 12)
            c.drawRect(skia.Rect.MakeXYWH(-170, -150, 340, 80), K.paint(RED))
            K.text(c, "周一", 0, -110, 52, "hand", "#FFFFFF")
            K.text(c, "例会", 0, 30, 76, "hand", BLACK)
            K.text(c, "9:00", 0, 105, 46, "black", RED)
    return None


L.note("9:00")
ev(j, k_shadow, shadow11, "wood_high", 0.75)
ev(j, k_like, L.stamp("像", cx + 420, cy - 40, 90, j, k_like, rot=10), "kick", 0.85)

# ================================================================ 屏 12：第三步——问感受：词典打叉；着急、委屈、开心；最近在哪？
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_h12 = kq(j, wt(18, 0, 0.3), 0)
k_dict = nx(j, wt(18, 1, 0.5), k_h12)
k_feel = [nx(j, wt(18, 2, 0.3), k_dict)]
k_feel += [cap(j, k_feel[0] + 1), cap(j, k_feel[0] + 2)]
k_where = nx(j, wt(18, 3, 0.4), k_feel[2])
FEELS = [("着急", "o", ORANGE), ("委屈", "sad", BLUE), ("开心", "smile", GREEN)]
L.note("第三", "问感受", "解梦词典", "最近在哪？", *[f_ for f_, _, _ in FEELS])


def h12(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 470, sc):
        K.text(c, "第三", cx - 380, cy - 470, 70, "hand", L.ACC)
        K.text(c, "问感受", cx - 80, cy - 470, 60, "hand", BLACK)
    return None


ev(j, k_h12, pop_fn(j, k_h12, h12), "wood_low", 0.6)


def dict12(c, kk, T, cx=cx, cy=cy):
    g = pop_scale(T - tb(12, k_dict))
    if g <= 0:
        return None
    x, y = cx + 320, cy - 230
    with K.at(c, x, y, 6, g):
        box(c, 0, 0, 230, 290, "#8E2C2C", BLACK, 6, 10)
        K.text(c, "解梦", 0, -50, 50, "serif_black", "#FFE39A")
        K.text(c, "词典", 0, 20, 50, "serif_black", "#FFE39A")
        f = clamp01((T - tb(12, k_dict) - 0.25) / 0.25)
        if f > 0:
            c.drawPath(wb.partial(cross(0, 0, 130), f)[0], wb.marker(RED, 16))
    return None


ev(j, k_dict, dict12, "rim", 0.8)


def feels12(c, kk, T, cx=cx, cy=cy):
    for i, (s_, mood, col) in enumerate(FEELS):
        g = pop_scale(T - tb(12, k_feel[i]))
        if g <= 0:
            continue
        x, y = cx - 360, cy - 290 + i * 190
        with K.at(c, x, y, 0, g):
            c.drawCircle(-90, 0, 70, K.paint(PAPER_W))
            c.drawCircle(-90, 0, 70, wb.marker(col, 8))
            for dx in (-22, 22):
                c.drawCircle(-90 + dx, -12, 7, K.paint(BLACK))
            m = skia.Path()
            if mood == "smile":
                m.addArc(skia.Rect.MakeXYWH(-120, 0, 60, 36), 20, 140)
            elif mood == "sad":
                m.addArc(skia.Rect.MakeXYWH(-115, 18, 50, 30), 200, 140)
            else:
                m.addCircle(-90, 26, 13)
            c.drawPath(m, wb.marker(BLACK, 6))
            if mood == "o":
                A._sweat(c, -20, -50)
            K.text(c, s_, 70, 2, 70, "hand", col)
    return None


ev(j, k_feel[0], feels12, "pop", 0.7)
b.hit(j, k_feel[1], "pop", 0.65, "委屈")
b.hit(j, k_feel[2], "pop", 0.65, "开心")


def where12(c, kk, T, cx=cx, cy=cy):
    g = C.slam_scale(T - tb(12, k_where))
    if g <= 0:
        return None
    for i in range(3):
        y = cy - 290 + i * 190
        c.drawPath(wb.arrow((cx - 190, y), (cx - 10, cy + 330), 0.1 * (1 - i), 26), wb.marker(GRAY, 5, clamp01(g)))
    with K.at(c, cx + 170, cy + 380, -3, g):
        box(c, 0, 0, 420, 150, "#E4E2F6", NIGHT, 8, 30)
        K.text(c, "最近在哪？", 0, 2, 70, "hand", NIGHT)
    return None


ev(j, k_where, where12, "kick", 0.85)

# ================================================================ 屏 13：评论区——“我想先试第五讲”；十三讲小旗排成一排；小李在日出里醒来
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_box = kq(j, wt(19, 0, 0.3), 0)
k_type = nx(j, wt(19, 1, 0.3), k_box)
k_likes = nx(j, wt(20, 0, 0.3), k_type)
k_flags = nx(j, wt(20, 1, 0.2), k_likes)
k_mv = nx(j, wt(21, 0, 0.3), k_flags)
k_sun = nx(j, wt(21, 2, 0.3), k_mv)
L.note("评论区", "我想先试第五讲", "发送", "+1", "听一听", *EPISODES)
FLAG_ROWS = [(cy - 60, range(0, 7)), (cy + 260, range(7, 13))]


def input13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_box))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 440, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(13, k_type):
            s_ = "我想先试第五讲"
            g = clamp01((T - tb(13, k_type)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], x - w / 2 + 40, y + 2, 58, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, L.ACC)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
        for i in range(6):
            g = pop_scale(T - tb(13, k_likes) - i * 0.15) * (1 - clamp01((T - tb(13, k_mv)) / 0.4))
            if g > 0:
                with K.at(c, x - 330 + i * 120, y + 140, 0, g):
                    K.rr(c, 0, 0, 100, 60, 30, "#E4E2F6")
                    K.text(c, "+1", 0, 2, 40, "hand", L.ACC)
    return None


ev(j, k_box, input13, "wood_high", 0.7)
b.hit(j, k_type, "pop", 0.6, "打字")
b.hit(j, k_likes, "clap", 0.75, "好多人加一")


def flags13(c, kk, T, cx=cx, cy=cy):
    t0 = tb(13, k_flags)
    if T < t0:
        return None
    n = 0
    for y, idx in FLAG_ROWS:
        idx = list(idx)
        xs = [cx + (m - (len(idx) - 1) / 2) * 152 for m in range(len(idx))]
        f = clamp01((T - t0 - n * 0.05) / 0.3)
        rope = skia.Path()
        rope.moveTo(xs[0] - 90, y - 160)
        rope.quadTo(cx, y - 130, xs[-1] + 90, y - 160)
        c.drawPath(rope, wb.marker(GRAY, 4, f))
        for m, i in enumerate(idx):
            g = pop_scale(T - t0 - (n + m) * 0.06)
            if g <= 0:
                continue
            sway = 3 * math.sin(T * 2 + i)
            with K.at(c, xs[m], y, sway, g):
                flag(c, 0, 0, i, hi=(i == 0))
        n += len(idx)
    return None


ev(j, k_flags, flags13, "shaker", 0.75)
if k_flags + 1 < k_mv:
    b.hit(j, k_flags + 1, "ding", 0.7, "第一讲小旗")
b.move(j, k_mv, (cx, cy + 330, Z), dur=1.0)


def sunrise13(c, kk, T, cx=cx, cy=cy):
    t0 = tb(13, k_mv) + 0.6
    if T < t0:
        return None
    g = pop_scale(T - t0)
    rise = ease_out(clamp01((T - tb(13, k_sun)) / 0.8)) if T >= tb(13, k_sun) else 0.0
    y0 = cy + 820
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(cx - 560, cy + 420, cx + 560, y0))
    sun(c, cx + 300, lerp(y0 + 40, cy + 580, rise), 80)
    c.restore()
    C.line(c, (cx - 540, y0), (cx + 540, y0), ORANGE, 7, clamp01(g))
    with at_pop(c, cx - 250, y0, g):
        bed(c, cx - 520, y0 - 110, 520)
        sleeper(c, cx - 290, y0 - 130, 0.7, T, tb(13, k_sun), "smile")
    if rise > 0:
        with K.at(c, cx + 20, cy + 480, -3, pop_scale(T - tb(13, k_sun))):
            K.text(c, "听一听", 0, 0, 80, "hand", L.ACC)
    return None


b.custom(j, k_mv, k_mv + 0.3, sunrise13)
b.hit(j, k_sun, "ding", 0.8, "日出醒来")

# ================================================================ 收尾
L.finish(cover_shot=7, square_shot=4, notes=NOTES)
L.export(globals())
