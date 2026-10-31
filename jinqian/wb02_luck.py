"""02 运气与风险（白板手绘版）：一样努力，结果怎么差这么多？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（形式 B 一个故事贯穿）：1968 年一间教室、一台电脑开局 → 湖滨中学是当年少有的有电脑的学校 →
盖茨和好友肯特天天泡在电脑前 → drop：画面一劈两半，左边一条线冲上天（盖茨），右边一座山 + 断掉的绳子（肯特，
高中毕业前登山遇难；只画山和断绳，语气克制）→ 亮书（小猪罐出场）→ 书中观点：运气和风险是一枚硬币的两面，
都在个人控制之外（虚线圈“你管不了”，里面一小块“你能管”）→ 别光看结果夸人（领奖台背后的大影子）/
也别光看结果骂自己（小王被裁，“我不行”划掉）→ 落到小王身上：同一年入职、两种部门 → 做法（看一群人的规律 /
给运气差留备用金 / 结果好也留点谦虚）→ 评论区互动 + 下一讲。
书中观点为转述：摩根·豪泽尔《金钱心理学》第 2 章“运气与风险”；
例子（同年入职、被裁）与做法（备用金、谦虚）为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, circle, face, join, rect,
                               stick)

from .common import BOOK, episode

ACC = "#C9851E"                 # 本讲主色：琥珀金（第 1 讲为系列绿）
SQUARE_SHOT = 3                 # 场景 4：盖茨（火柴人 + 名字牌 + 冲天线）与肯特（山 + 断绳 + 名字牌）
GRAY = "#A3A8B0"

b = Board(size=(3600, 9800))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def E(k0, k1, x, y, w, h):
    b.erase(J(), k0, k1, x, y, w, h)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def pig(x, y, s=1.0) -> skia.Path:
    """系列角色小猪罐（不含嘴）：圆身子、背上投币口、两只耳朵、点点眼睛、鼻头、四条短腿、卷尾巴。(x, y) 为身子中心，朝右。"""
    body = skia.Path()
    body.addOval(skia.Rect.MakeXYWH(x - 150 * s, y - 110 * s, 300 * s, 220 * s))
    snout = skia.Path()
    snout.addOval(skia.Rect.MakeXYWH(x + 118 * s, y - 34 * s, 62 * s, 56 * s))
    tail = skia.Path()
    tail.moveTo(x - 150 * s, y - 10 * s)
    tail.quadTo(x - 200 * s, y - 40 * s, x - 185 * s, y - 70 * s)
    tail.quadTo(x - 165 * s, y - 90 * s, x - 178 * s, y - 50 * s)
    return join(body, snout, tail,
                circle(x + 140 * s, y - 6 * s, 5 * s), circle(x + 160 * s, y - 6 * s, 5 * s),
                circle(x + 70 * s, y - 45 * s, 7 * s),
                P((x - 40 * s, y - 72 * s), (x + 30 * s, y - 72 * s)),
                P((x + 10 * s, y - 104 * s), (x + 30 * s, y - 150 * s), (x + 62 * s, y - 96 * s)),
                P((x - 60 * s, y - 104 * s), (x - 45 * s, y - 150 * s), (x - 12 * s, y - 108 * s)),
                *[P((x + dx * s, y + 100 * s), (x + dx * s, y + 145 * s)) for dx in (-90, -40, 40, 90)])


def pig_mouth(x, y, s=1.0, mood="smile") -> skia.Path:
    mx, my = x + 95 * s, y + 42 * s
    p = skia.Path()
    if mood == "smile":
        p.addArc(skia.Rect.MakeXYWH(mx - 26 * s, my - 22 * s, 52 * s, 36 * s), 20, 140)
    else:
        p.addArc(skia.Rect.MakeXYWH(mx - 24 * s, my, 48 * s, 30 * s), 200, 140)
    return p


def sweat(x, y, s=1.0) -> skia.Path:
    """汗滴：(x, y) 为下端圆心。"""
    p = skia.Path()
    p.moveTo(x, y - 46 * s)
    p.quadTo(x + 22 * s, y - 10 * s, x + 18 * s, y + 4 * s)
    p.quadTo(x, y + 26 * s, x - 18 * s, y + 4 * s)
    p.quadTo(x - 22 * s, y - 10 * s, x, y - 46 * s)
    return p


def coin(x, y, r=130) -> skia.Path:
    return join(circle(x, y, r), circle(x, y, r * 0.82))


def terminal(x, y, s=1.0) -> skia.Path:
    """老式电脑终端：机身 + 屏幕 + 光标 + 键盘。(x, y) 为机身中心。"""
    return join(rect(x, y, 260 * s, 190 * s, 14 * s), rect(x, y - 15 * s, 190 * s, 120 * s, 8 * s),
                P((x - 70 * s, y - 40 * s), (x - 20 * s, y - 40 * s)), P((x - 70 * s, y - 5 * s), (x + 10 * s, y - 5 * s)),
                P((x - 150 * s, y + 95 * s), (x + 150 * s, y + 95 * s), (x + 175 * s, y + 150 * s),
                  (x - 175 * s, y + 150 * s), close=True),
                P((x - 120 * s, y + 122 * s), (x + 120 * s, y + 122 * s)))


def gate(x, y, w=400, h=450) -> skia.Path:
    """校门：两根门柱 + 横梁 + 门牌框。(x, y) 为地面中点；门牌框中心在 (x, y-h-50)。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h)), P((x - w / 2 + 40, y), (x - w / 2 + 40, y - h)),
                P((x + w / 2, y), (x + w / 2, y - h)), P((x + w / 2 - 40, y), (x + w / 2 - 40, y - h)),
                P((x - w / 2 - 30, y - h), (x + w / 2 + 30, y - h)), rect(x, y - h - 50, w - 20, 100, 10),
                P((x - w / 2 - 60, y), (x + w / 2 + 60, y)))


def school(x, y, w=220, h=320) -> skia.Path:
    """别的学校：小楼 + 尖顶 + 窗。(x, y) 为底边中点。"""
    parts = [P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
             P((x - w / 2 - 20, y - h), (x, y - h - 90), (x + w / 2 + 20, y - h))]
    for r in range(2):
        for c in (-1, 1):
            parts.append(rect(x + c * w / 4, y - h + 70 + r * 100, 44, 44, 4))
    parts.append(P((x - 30, y), (x - 30, y - 70), (x + 30, y - 70), (x + 30, y)))
    return join(*parts)


def plate(x, y, w=200, h=88) -> skia.Path:
    """名字牌：圆角框 + 两侧挂绳。"""
    return join(rect(x, y, w, h, 14), P((x - w / 2 + 20, y - h / 2), (x, y - h / 2 - 40), (x + w / 2 - 20, y - h / 2)))


def bulb(x, y, r=46) -> skia.Path:
    return join(circle(x, y, r), P((x - r * 0.45, y + r * 0.9), (x - r * 0.45, y + r * 1.4), (x + r * 0.45, y + r * 1.4),
                                   (x + r * 0.45, y + r * 0.9)),
                P((x, y - r - 18), (x, y - r - 48)), P((x - r - 18, y), (x - r - 48, y)), P((x + r + 18, y), (x + r + 48, y)))


def dashed_circle(x, y, r, n=28) -> skia.Path:
    p = skia.Path()
    step = 360 / n
    for i in range(n):
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -90 + i * step, step * 0.55)
    return p


def podium(x, y, w=240, hs=(140, 220, 100)) -> skia.Path:
    """三级领奖台：(x, y) 为地面中点，中间最高。"""
    return join(*[rect(x + (i - 1) * w, y - h / 2, w, h, 6) for i, h in enumerate(hs)])


def bow(x, y, s=1.0) -> skia.Path:
    """鞠躬的小人：(x, y) 为脚底，身子朝右前倾。"""
    hip = (x, y - 120 * s)
    sh = (x + 110 * s, y - 215 * s)
    return join(P((x - 50 * s, y), hip, (x + 50 * s, y)), P(hip, sh), circle(x + 165 * s, y - 200 * s, 45 * s),
                P(sh, (x + 125 * s, y - 95 * s)), P((x + 90 * s, y - 198 * s), (x + 95 * s, y - 85 * s)))


def star(x, y, r=60) -> skia.Path:
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return P(*pts, close=True)


def mirror(path: skia.Path, x) -> skia.Path:
    m = skia.Matrix()
    m.setScale(-1, 1, x, 0)
    out = skia.Path(path)
    out.transform(m)
    return out


def flip_coin_fn(x, y, r, label, color):
    """翻面的硬币：横向缩放来回转两下后停在正面，正面写字。"""
    def fn(c, k, t):
        sx = math.cos(1.5 * math.pi * (1 - k))
        c.save()
        c.translate(x, y)
        c.scale(max(0.02, abs(sx)), 1)
        c.drawCircle(0, 0, r, K.paint(color, 1, 10))
        c.drawCircle(0, 0, r * 0.82, K.paint(color, 1, 10))
        if sx > 0.15:
            K.text(c, label, 0, 0, 72, "hand", color)
        c.restore()
        return (x + r * abs(sx), y - r * 0.6) if k < 1 else None
    return fn


def shadow_fn(x, y, s):
    """领奖台背后的大影子：放大的灰色人形，逐渐显出来（画在领奖台和小人之前，压在下层）。"""
    path = stick(x, y, s, "up")

    def fn(c, k, t):
        c.drawPath(path, K.paint(GRAY, 0.28 * clamp01(k * 1.2), 70))
        return None
    return fn


def drop_coin_fn(x, y0, y1):
    """一枚硬币从上方落进投币口，落到时消失。"""
    def fn(c, k, t):
        if k >= 1:
            return None
        yy = y0 + (y1 - y0) * k * k
        c.drawCircle(x, yy, 34, K.paint(GREEN, 1, 8))
        c.drawLine(x, yy - 16, x, yy + 16, K.paint(GREEN, 1, 6))
        return None
    return fn


# ---------------------------------------------------------------- 开局：1968 年的教室（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("两个少年，一台电脑", "书中故事 · 1968", (950, 900, 0.85), bars=2)
T("1968", 950, 480, 130, RED, k0=0, k1=1.0, sfx="pop")
L(join(rect(700, 790, 440, 220, 10), P((540, 760), (700, 760)), P((540, 820), (640, 820))), 1, 1.9, BLACK, 9,
  sfx="wood_high")
L(terminal(1240, 1060), 2, 2.9, BLUE, 9, sfx="wood_low")
L(join(stick(640, 1400, 0.55), stick(850, 1400, 0.55)), 3, 3.9, BLACK, 9, sfx="pop")
L(join(face(640, 1400, 0.55), face(850, 1400, 0.55)), 3.9, 4.1, BLACK, 7)
T("一台电脑", 1240, 1300, 60, BLUE, k0=4.5, k1=5.5)
H(5, "ding")

scene("全美很少有学校有这个", "书中故事 · 湖滨中学", (2650, 900, 0.85))
L(gate(2650, 1300), 0, 0.9, BLACK, 10, sfx="wood_high")
T("湖滨中学", 2650, 800, 64, k0=1, k1=2, sfx="pop")
L(terminal(2650, 1110, 0.6), 2.3, 3.0, BLUE, 8)
H(3, "ding")
L(join(school(2200, 1300), school(3100, 1300)), 4, 4.9, GRAY, 9, sfx="wood_low")
L(P((2120, 1080), (2280, 1240)), 5, 5.3, RED, 12, sfx="rim")
L(P((2280, 1080), (2120, 1240)), 5.3, 5.6, RED, 12)
L(P((3020, 1080), (3180, 1240)), 6, 6.3, RED, 12, sfx="rim")
L(P((3180, 1080), (3020, 1240)), 6.3, 6.6, RED, 12)
T("有电脑", 2650, 990, 56, BLUE, k0=7, k1=7.8, sfx="pop")

S3 = (620, 1280)                # 盖茨、肯特的 x
scene("两个人天天泡在这", "书中故事 · 盖茨和肯特", (950, 2200, 0.85))
L(join(P((480, 2420), (1420, 2420)), P((520, 2420), (520, 2530)), P((1380, 2420), (1380, 2530)), terminal(950, 2300, 0.7)),
  0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(S3[0], 2620, 0.75, "hold"), 1, 1.8, BLACK, 10, sfx="pop")
L(face(S3[0], 2620, 0.75), 1.8, 2.0, BLACK, 7)
L(mirror(stick(S3[1], 2620, 0.75, "hold"), S3[1]), 2, 2.8, BLACK, 10, sfx="pop")
L(face(S3[1], 2620, 0.75), 2.8, 3.0, BLACK, 7)
L(plate(S3[0], 2160), 3, 3.4, BLUE, 7, sfx="wood_low")
T("盖茨", S3[0], 2160, 56, BLUE, k0=3.4, k1=4.2)
L(plate(S3[1], 2160), 4.4, 4.8, BLUE, 7)
T("肯特", S3[1], 2160, 56, BLUE, k0=4.8, k1=5.6)
H(5, "pop")
L(bulb(S3[0], 1930), 6, 6.8, ACC, 8, sfx="ding")
L(bulb(S3[1], 1930), 7, 7.8, ACC, 8, sfx="ding")

# ---------------------------------------------------------------- drop：一劈两半（场景 4）

scene("一个首富，一个没毕业", "书中故事 · 两种结局", (2650, 2200, 0.75), shake=[0], flashes=[0])
L(P((2650, 1640), (2650, 2790)), 0, 0.6, BLACK, 9, sfx="kick")
L(join(stick(2090, 2650, 0.45, "up"), face(2090, 2650, 0.45)), 0.7, 1.0, BLACK, 8)
L(join(P((2200, 2640), (2280, 2560), (2350, 2590), (2430, 2400), (2480, 2430), (2580, 1800)),
       P((2580, 1800), (2535, 1860)), P((2580, 1800), (2595, 1875))), 1, 1.9, GREEN, 11, sfx="wood_high")
L(plate(2160, 2745), 2, 2.4, BLUE, 7, sfx="pop")
T("盖茨", 2160, 2745, 56, BLUE, k0=2.4, k1=3.2)
L(P((2730, 2650), (2950, 2050), (3050, 2200), (3170, 1900), (3330, 2650), close=True), 4, 4.9, BLACK, 10,
  sfx="wood_low")
L(join(P((3170, 1900), (3200, 2050), (3190, 2180)), P((3205, 2265), (3225, 2400), (3215, 2520))), 5, 5.6, BLACK, 7,
  sfx="rim")
L(join(P((3165, 2205), (3220, 2195)), P((3175, 2245), (3230, 2240))), 5.6, 5.9, RED, 7)
L(plate(3030, 2745), 6, 6.4, BLUE, 7, sfx="pop")
T("肯特", 3030, 2745, 56, BLUE, k0=6.4, k1=7.2)

# ---------------------------------------------------------------- 书中观点（场景 5–9）

scene("《金钱心理学》这样讲", "金钱心理学 · 第2章", (950, 3600, 0.85))
L(book(800, 3550, 420, 280), 0, 0.9, BLACK, 9, sfx="wood_low")
T("金钱心理学", 800, 3290, 72, GREEN, k0=1, k1=2.25, sfx="pop")
L(plate(800, 3790, 400, 90), 2.4, 2.9, BLUE, 7)
T("摩根·豪泽尔", 800, 3790, 56, BLUE, k0=3, k1=4.5, sfx="pop")
L(pig(1310, 3560, 0.85), 5, 5.8, ACC, 8, sfx="wood_high")
L(pig_mouth(1310, 3560, 0.85), 5.8, 6.0, ACC, 7)
T("第2章 运气与风险", 950, 3990, 60, BLUE, k0=6, k1=8.0, sfx="pop")

CO = ((2460, 3500), (2840, 3500))
scene("运气和风险，是一对", "书中观点 · 一枚硬币", (2650, 3600, 0.85))
L(coin(*CO[0]), 0, 0.9, GREEN, 10, sfx="wood_high")
T("运气", *CO[0], 72, GREEN, k0=1, k1=1.8, sfx="pop")
L(arrow((2560, 3320), (2740, 3320), -0.45, 34), 3, 3.7, BLACK, 8, sfx="wood_low")
T("翻面", 2650, 3200, 52, k0=3.7, k1=4.5)
C(4, 5.5, flip_coin_fn(*CO[1], 130, "风险", RED), sfx="shaker")
H(5, "rim")
T("一枚硬币，两面", 2650, 3800, 72, k0=6, k1=7.75, sfx="pop")

scene("都不归你管", "书中观点 · 你管不了", (2650, 3745, 0.7))
E(0, 0.6, 2650, 3800, 620, 110)
H(0, "shaker", 0.6)
L(dashed_circle(2650, 3530, 460), 1, 1.9, RED, 9, sfx="wood_high")
T("你管不了", 2650, 4090, 72, RED, k0=3, k1=4, sfx="pop")
L(rect(2650, 3810, 280, 110, 20), 5, 5.6, GREEN, 9, sfx="ding")
T("你能管", 2650, 3810, 64, GREEN, k0=5.6, k1=6.6)
H(7, "pop", 0.6)

scene("别光看结果夸人", "书中观点 · 别只看结果", (950, 5000, 0.85))
C(3, 4.5, shadow_fn(950, 5130, 1.9), sfx="shaker")     # 先登记，压在领奖台和小人下层
L(podium(950, 5350), 0, 0.9, BLACK, 9, sfx="wood_low")
L(join(stick(950, 5130, 0.7, "up"), face(950, 5130, 0.7)), 1, 1.9, BLACK, 10, sfx="pop")
T("结果", 950, 5430, 56, k0=2, k1=2.8, sfx="pop")
T("运气", 1370, 4640, 80, BLUE, k0=5, k1=5.8, sfx="ding")
L(arrow((1300, 4710), (1150, 4830), 0.15, 30), 6, 6.6, BLUE, 8, sfx="wood_high")
T("看不见", 1370, 4760, 52, GRAY, k0=7, k1=7.8, sfx="pop")

WG = (2480, 5420)               # 小王脚底
scene("也别光看结果骂自己", "书中观点 · 别骂自己", (2650, 5000, 0.85))
L(join(stick(*WG, 0.8, "hold", tie=True), face(*WG, 0.8, "sad")), 0, 1.0, BLACK, 10, sfx="wood_high")
T("小王", WG[0], WG[1] + 60, 50, k0=1, k1=1.8)
L(rect(2640, 5250, 160, 120, 8), 2, 2.5, BLACK, 8, sfx="pop")
T("被裁", 2640, 5250, 52, RED, k0=2.5, k1=3.3)
T("我不行", WG[0], 4980, 80, k0=4, k1=4.8, sfx="pop")
L(P((2340, 4985), (2620, 4975)), 5, 5.4, RED, 12, sfx="rim")
T("有一部分是风险", 2700, 4790, 70, RED, k0=6, k1=7.75, sfx="pop")

# ---------------------------------------------------------------- 落到小王身上（场景 10）与做法（场景 11–13）

scene("同一年入职", "例子 · 同一年入职", (950, 6400, 0.85))
T("同一年入职", 950, 5960, 72, k0=0, k1=1.25, sfx="pop")
L(join(stick(680, 6880, 0.65, tie=True), stick(1220, 6880, 0.65, tie=True)), 2, 2.8, BLACK, 10, sfx="wood_high")
L(join(face(680, 6880, 0.65), face(1220, 6880, 0.65, "sad")), 2.8, 3.0, BLACK, 7)
T("部门扩张", 680, 6200, 60, GREEN, k0=3, k1=4, sfx="pop")
L(arrow((680, 6580), (680, 6290), 0.0, 40), 4, 4.8, GREEN, 10, sfx="ding")
L(arrow((1220, 6290), (1220, 6580), 0.0, 40), 5, 5.8, RED, 10, sfx="rim")
T("部门撤了", 1220, 6200, 60, RED, k0=6, k1=7, sfx="pop")

scene("看大多数人怎么样", "做法一 · 看一群人", (2650, 6400, 0.85))
L(join(stick(2250, 6650, 0.7, "up"), face(2250, 6650, 0.7)), 0, 0.9, BLACK, 10, sfx="wood_high")
L(star(2250, 6320, 55), 1, 1.7, ACC, 8, sfx="pop")
T("一个人的传奇", 2250, 6160, 56, k0=2, k1=3.5, sfx="pop")
L(arrow((2440, 6560), (2640, 6560), -0.2, 34), 4, 4.7, BLACK, 9, sfx="wood_high")
L(join(*[stick(2700 + i * 92, 6740, 0.34) for i in range(6)]), 5, 5.9, BLUE, 7, sfx="pop")
T("看大多数人", 2930, 6860, 64, BLUE, k0=6, k1=7.25, sfx="ding")

PG = (950, 7750, 1.6)           # 小猪罐
scene("给运气差留点余量", "做法二 · 备用金", (950, 7800, 0.85))
L(pig(*PG), 0, 1.0, ACC, 9, sfx="wood_high")
L(join(pig_mouth(*PG, "sad"), sweat(1200, 7560, 1.2)), 1, 1.6, BLUE, 8, sfx="shaker")
T("备用金", 900, 7790, 80, GREEN, k0=2, k1=2.8, sfx="pop")
C(3.4, 4, drop_coin_fn(PG[0] - 8, 7300, PG[1] - 72 * PG[2]))
H(4, "ding")
C(4.4, 5, drop_coin_fn(PG[0] - 8, 7300, PG[1] - 72 * PG[2]))
H(5, "ding")
E(5.2, 5.7, 1102, 7826, 110, 70)
E(5.2, 5.7, 1200, 7545, 70, 90)
L(pig_mouth(*PG, "smile"), 6, 6.5, ACC, 8, sfx="pop")
T("能撑一阵", 950, 8150, 64, GREEN, k0=7, k1=8.0, sfx="ding")

scene("结果好，也留点谦虚", "做法三 · 留点谦虚", (2650, 7800, 0.85))
L(rect(2450, 7990, 280, 220, 6), 0, 0.8, BLACK, 9, sfx="wood_low")
L(bow(2400, 7880, 0.8), 1, 1.8, BLACK, 10, sfx="pop")
T("结果好", 2450, 8000, 56, k0=2, k1=2.8, sfx="pop")
L(pig(3020, 8000, 0.6), 3, 3.8, ACC, 8, sfx="wood_high")
L(pig_mouth(3020, 8000, 0.6), 3.8, 4.0, ACC, 7)
L(bubble(2960, 7500, 360, 140, -1), 5, 5.6, GREEN, 8, sfx="wood_high")
T("也有运气", 2960, 7500, 64, GREEN, k0=6, k1=7, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5800, 0.14)
CMT = (1800, 9150, 0.8)
j_end = scene("哪次全靠运气？", "评论区见", FAR, bars=4)
b.move(j_end, 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你哪次全靠运气？", 1800, 8950, 84, RED, k0=6, k1=8, sfx="pop")
T("下一讲：工资涨了，为什么还是不够花？", 1800, 9130, 48, k0=9, k1=13.5, sfx="wood_high")
L(pig(1800, 9400, 0.55), 13.6, 14.4, ACC, 8)
L(pig_mouth(1800, 9400, 0.55), 14.4, 14.6, ACC, 7)
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "luck", "运气与风险", "一样努力，结果怎么差这么多？", ACC, b.shots,
                 [f"{BOOK}第2章“运气与风险”（转述）",
                  "Morgan Housel, The Psychology of Money (Harriman House, 2020)；中译本《金钱心理学》（摩根·豪泽尔著，"
                  "李青宗译，民主与建设出版社 / 后浪 2023）第2章“运气与风险”（转述）"],
                 "一样努力|结果怎么【差这么多】？", SQUARE_SHOT,
                 ["书中观点（转述）：第2章“运气与风险”——比尔·盖茨读的湖滨中学是当年极少数有电脑的中学；"
                  "他的好友肯特·埃文斯同样出色，却在高中毕业前死于登山事故。运气和风险是一对，都是个人控制不了的力量；"
                  "评判别人和自己都别只看结果，多看普遍规律，少盯个别人的传奇。上屏均为转述，不是逐字引文。",
                  "人物一律画成火柴人 + 名字牌，不画肖像；肯特的事故只画山和断绳，不画坠落。"
                  "“1968”为书中故事的年份；画面里的别的学校打叉为示意，不写比例。",
                  "“一枚硬币两面”“你管不了 / 你能管”、领奖台背后的影子，为对书中观点的通俗化示意。",
                  "小王被裁、同一年入职碰上部门扩张或撤销，均为现实场景示意，不指向任何具体公司或个人。",
                  "三条做法（看一群人的规律；给运气差留备用金；结果好也留点谦虚）为据书中思路整理的建议，"
                  "不构成任何投资建议。"],
                 tags="#运气 #比尔盖茨")
    return b.attach(ep)
