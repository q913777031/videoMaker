"""09 迈出第一步（白板手绘版）：想交朋友，第一步迈哪？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
叙事：切身问题开局（搬到新城市第三年，下班回出租屋，周末没人约；刷到一个读书会，想去又怕尴尬）→ 书中观点（亮书；
书末一章给的办法拼成 EASE 四个字母，本讲讲前两个：E 先迈一小步——帮个小忙、做志愿；A 有个计划——先挑低风险的小场合，
大型聚会往后放；画成一级一级的台阶）→ 身边的例子（帮同事弄卡纸的打印机、借梯子给邻居、六个人的小读书会、
孩子转学先约一个同学来家）→ 具体做法（每天帮一个小忙 / 报一次志愿 / 列场合清单从最不怕的排起 / 定好时间和退路）
→ 评论区互动，预告下一讲（后两个字母）。
书中观点为转述：Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection (W. W. Norton, 2008)
第 14 章（中译本第三部分“14 个体困境的解药”）；中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009。
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, building, check, circle,
                               clock, cross, face, hands_at, join, marker, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#3E7D6B"
SQUARE_SHOT = 8

b = Board(size=(3600, 11700))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


# ---------------------------------------------------------------- 本讲画法

def suitcase(x, y, w=170, h=200) -> skia.Path:
    """行李箱：(x, y) 为箱体中心。"""
    return join(rect(x, y, w, h, 18), P((x - 35, y - h / 2), (x - 35, y - h / 2 - 50), (x + 35, y - h / 2 - 50),
                                        (x + 35, y - h / 2)),
                P((x - w / 2 + 40, y - h / 2 + 30), (x - w / 2 + 40, y + h / 2 - 30)),
                P((x + w / 2 - 40, y - h / 2 + 30), (x + w / 2 - 40, y + h / 2 - 30)))


def house(x, y, w=420, h=300) -> skia.Path:
    """小屋：(x, y) 为底边中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 40, y - h), (x, y - h - 190), (x + w / 2 + 40, y - h)),
                P((x - 45, y), (x - 45, y - 150), (x + 45, y - 150), (x + 45, y)),
                rect(x + w / 4 + 10, y - h + 90, 80, 70, 6))


def phone(x, y, w=240, h=400) -> skia.Path:
    return join(rect(x, y, w, h, 26), P((x - 25, y + h / 2 - 26), (x + 25, y + h / 2 - 26)))


def calendar(x, y, w=560, h=440) -> skia.Path:
    return join(rect(x, y, w, h, 16), P((x - w / 2, y - h / 2 + 100), (x + w / 2, y - h / 2 + 100)),
                P((x, y - h / 2 + 100), (x, y + h / 2)),
                P((x - w / 4, y - h / 2 - 30), (x - w / 4, y - h / 2 + 30)),
                P((x + w / 4, y - h / 2 - 30), (x + w / 4, y - h / 2 + 30)))


def bubble(x, y, w, h, tail=-1) -> skia.Path:
    p = rect(x, y, w, h, 40)
    p.moveTo(x + tail * w * 0.15, y + h / 2)
    p.lineTo(x + tail * w * 0.3, y + h / 2 + 60)
    p.lineTo(x + tail * w * 0.02, y + h / 2)
    return p


def heart(x, y, r=80) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r)
    p.cubicTo(x - r * 1.6, y - r * 0.1, x - r * 0.7, y - r * 1.3, x, y - r * 0.45)
    p.cubicTo(x + r * 0.7, y - r * 1.3, x + r * 1.6, y - r * 0.1, x, y + r)
    return p


def cup(x, y, s=1.0) -> skia.Path:
    body = P((x - 55 * s, y - 70 * s), (x - 44 * s, y + 70 * s), (x + 44 * s, y + 70 * s), (x + 55 * s, y - 70 * s),
             close=True)
    return join(body, P((x - 52 * s, y - 40 * s), (x + 52 * s, y - 40 * s)))


def ellipse(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def printer(x, y, w=300, h=190) -> skia.Path:
    return join(rect(x, y, w, h, 18), P((x - w / 2 + 50, y - h / 2), (x - w / 2 + 50, y - h / 2 - 70),
                                        (x + w / 2 - 50, y - h / 2 - 70), (x + w / 2 - 50, y - h / 2)),
                P((x - w / 2 + 40, y + 20), (x + w / 2 - 40, y + 20)), circle(x + w / 2 - 40, y - 40, 14))


def ladder(x, y, h=440, w=130) -> skia.Path:
    """梯子：(x, y) 为中心。"""
    parts = [P((x - w / 2, y + h / 2), (x - w / 2 + 20, y - h / 2)), P((x + w / 2, y + h / 2), (x + w / 2 - 20, y - h / 2))]
    for i in range(5):
        yy = y - h / 2 + 50 + i * (h - 80) / 4
        parts.append(P((x - w / 2 + 12, yy), (x + w / 2 - 12, yy)))
    return join(*parts)


def bag(x, y, w=150, h=140) -> skia.Path:
    return join(P((x - w / 2, y - h / 2), (x - w / 2 + 15, y + h / 2), (x + w / 2 - 15, y + h / 2), (x + w / 2, y - h / 2)),
                P((x - 30, y - h / 2), (x - 20, y - h / 2 - 50), (x + 20, y - h / 2 - 50), (x + 30, y - h / 2)))


def door(x, y, w=220, h=380) -> skia.Path:
    """门：(x, y) 为中心。"""
    return join(rect(x, y, w, h, 8), circle(x + w / 2 - 40, y + 10, 12))


def heads(pts, r=34) -> skia.Path:
    return join(*(circle(x, y, r) for x, y in pts))


def stairs(x0, y0, n, w, rise) -> skia.Path:
    """台阶：从 (x0, y0) 起，n 级，每级宽 w、高 rise，向右上。"""
    pts = [(x0, y0)]
    x, y = x0, y0
    for i in range(n):
        x += w
        pts.append((x, y))
        if i < n - 1:
            y -= rise
            pts.append((x, y))
    pts.append((x, y0))
    return P(*pts, close=True)


def slam(j, kb, s, x, y, size, color=RED):
    """字母砸下：起拍时放大 1.8 倍，0.15 秒落定。"""

    def fn(c, k, t):
        t0 = b.t_of(j, kb)
        if t < t0:
            return None
        sc = 1 + 0.8 * (1 - ease_out(clamp01((t - t0) / 0.15)))
        K.text(c, s, x, y, size * sc, "hand", color, clamp01((t - t0) / 0.06))
        return None

    return fn


def climber(j, spots, beats=(1, 3, 5), s=0.5):
    """小人沿台阶往上跳：在 beats 指定的拍点分别落到 spots[0..2]（脚底坐标）。"""

    def fn(c, k, t):
        ts = [b.t_of(j, kb) for kb in beats]
        if t < ts[0]:
            return None
        i = max(n for n in range(len(spots)) if t >= ts[n])
        x, y = spots[i]
        if i + 1 < len(spots):
            f = clamp01((t - (ts[i + 1] - 0.3)) / 0.3)
            if f > 0:
                (x0, y0), (x1, y1) = spots[i], spots[i + 1]
                x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f - math.sin(f * math.pi) * 90
        c.drawPath(stick(x, y, s, "up"), marker(BLUE, 8))
        c.drawPath(face(x, y, s, "smile"), marker(BLUE, 6))
        return None

    return fn


# ---------------------------------------------------------------- 开局：新城市第三年（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("搬来三年，下班就回家", "灵魂拷问", (950, 850, 0.85))
L(join(building(520, 1150, 220, 320), building(760, 1150, 180, 260)), 0, 0.8, sfx="wood_high")
L(suitcase(1240, 1080), 1, 1.5, sfx="pop")
L(stick(1050, 1200, 0.9), 1.5, 1.9)
T("搬来第三年", 950, 500, 72, RED, k0=2, sfx="pop")
L(clock(1420, 650, 90), 3, 3.5, sfx="wood_high")
L(hands_at(1420, 650, 90, 7, 0), 3.5, 3.7, RED, 10)
T("七点就到家", 1420, 800, 46, k0=4, sfx="pop")
L(face(1050, 1200, 0.9, "flat"), 5, 5.2, sfx="wood_low")

scene("周末没人约", "灵魂拷问", (2650, 850, 0.85))
L(calendar(2500, 760), 0, 0.8, sfx="wood_high")
T("周六", 2360, 610, 54, k0=1, sfx="pop")
T("周日", 2640, 610, 54, k0=1.5)
T("空", 2360, 850, 110, RED, k0=2, k1=2.3, sfx="rim")
T("空", 2640, 850, 110, RED, k0=2.5, k1=2.8)
L(phone(3050, 760, 240, 380), 3, 3.4, sfx="pop")
T("没有消息", 3050, 760, 44, k0=4, k1=4.8, sfx="wood_low")

scene("想去，又怕尴尬", "灵魂拷问", (2700, 1950, 0.85), shake=[4], flashes=[4])
L(phone(2350, 1760, 320, 520), 0, 0.6, sfx="wood_high")
T("周六读书会", 2350, 1620, 52, GREEN, k0=1, sfx="pop")
T("欢迎新人", 2350, 1730, 46, k0=1.9, k1=2.5)
L(stick(2880, 2150, 0.85, "hold"), 2, 2.5, sfx="wood_high")
L(face(2880, 2150, 0.85, "flat"), 2.5, 2.6)
L(bubble(3020, 1480, 400, 150), 3, 3.4, BLACK, 8, sfx="pop")
T("去了说啥？", 3020, 1480, 52, k0=3.4, k1=4.0)
T("？", 3200, 1980, 180, RED, k0=4, k1=4.4, sfx="kick")
T("第一步迈哪", 2700, 2280, 80, k0=4.6, k1=5.8)

# ---------------------------------------------------------------- 书中观点（场景 4–9）

scene("最后一章给了办法", "孤独是可耻的 · 第十四章", (1100, 3050, 0.9))
L(book(750, 3050, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 750, 2810, 70, GREEN, k0=1.0, sfx="pop")
T("卡乔波", 750, 3280, 50, k0=2.0, sfx="pop")
T("第十四章", 1390, 2880, 64, RED, k0=3, sfx="pop")
L(arrow((1000, 3050), (1230, 3050), 0, 40), 4, 4.3, GREEN, 8, sfx="wood_high")
T("走出孤单的办法", 1400, 3060, 50, k0=4.3, k1=5.0)
L(underline(1230, 1570, 3110, 10, 30), 5, 5.4, RED, 7, sfx="ding")

EASE = [("E", 2200), ("A", 2500), ("S", 2800), ("E", 3100)]
j_drop = scene("四步，拼成一个词", "书中观点 · 四个字母", (2650, 3150, 0.85), shake=[0], flashes=[0])
for n, (ch, x) in enumerate(EASE):
    b.custom(j_drop, n, n + 0.2, slam(j_drop, n, ch, x, 3000, 220),
             sfx=("kick", "tom", "tom", "kick")[n], gain=1.0 if n == 0 else 0.75)
H(0, "cymbal", 0.5)
L(circle(2200, 3000, 135), 4, 4.4, GREEN, 8, sfx="wood_high")
L(circle(2500, 3000, 135), 4.4, 4.8, GREEN, 8)
T("这一讲", 2350, 3260, 56, GREEN, k0=5, sfx="pop")
T("下一讲", 2950, 3260, 56, BLUE, k0=5.4, k1=5.9)

scene("先伸手，帮个小忙", "书中观点 · 先迈一小步", (1000, 4100, 0.85))
T("E · 先迈一小步", 950, 3620, 70, BLUE, k0=0, k1=1.0, sfx="pop")
L(stick(580, 4350, 0.8, "point"), 1, 1.6, sfx="wood_high")
L(face(580, 4350, 0.8, "smile"), 1.6, 1.7)
L(arrow((540, 4420), (820, 4420), -0.08, 34), 2, 2.4, GREEN, 8, sfx="pop")
L(cup(860, 4150, 0.6), 3, 3.4, BLACK, 8, sfx="pop")
L(stick(1250, 4350, 0.8, "hold"), 4, 4.6, BLUE, sfx="wood_high")
L(face(1250, 4350, 0.8, "smile"), 4.6, 4.7, BLUE)
T("帮个小忙", 1050, 3800, 60, RED, k0=5, sfx="ding")

scene("做志愿也算", "书中观点 · 先迈一小步", (1000, 4100, 0.85))
L(heart(700, 4520, 60), 0, 0.6, RED, 8, sfx="wood_high")
T("做志愿", 920, 4530, 60, k0=2, sfx="pop")
T("也算", 1150, 4530, 60, RED, k0=3, sfx="pop")
L(underline(820, 1230, 4590, 10, 30), 4, 4.4, RED, 6, sfx="ding")

CROWD = [(2850 + c_ * 64 + (r % 2) * 30, 4060 + r * 56) for r in range(4) for c_ in range(5)]
scene("先挑小场合", "书中观点 · 有个计划", (2650, 4100, 0.85))
T("A · 有个计划", 2650, 3620, 70, BLUE, k0=0, k1=1.0, sfx="pop")
L(ellipse(2330, 4250, 380, 120), 1, 1.5, BLACK, 8, sfx="wood_high")
L(heads([(2190, 4150), (2330, 4120), (2470, 4150)]), 1.5, 1.9, BLUE, 7)
T("小场合", 2330, 4420, 56, k0=2, sfx="pop")
L(check(2560, 4410, 36), 2.6, 2.85, GREEN, 9)
L(heads(CROWD, 22), 3, 3.8, BLACK, 5, sfx="shaker")
T("大型聚会", 3000, 3930, 56, k0=4, sfx="pop")
T("以后再说", 3000, 4300, 50, RED, k0=5, sfx="rim")

SX, SY, SW, SR = 1050, 5600, 500, 190
SPOTS = [(SX + SW * (i + 0.5), SY - SR * i) for i in range(3)]
j_st = scene("一级一级往上走", "书中观点 · 一张图", (1800, 5620, 0.65))
L(stairs(SX, SY, 3, SW, SR), 0, 0.8, BLACK, 9, sfx="wood_high")
b.custom(j_st, 1, 7, climber(j_st, SPOTS), sfx="pop")
H(3, "pop")
H(5, "ding")
for n, w in enumerate(("帮小忙", "小场合", "常来往")):
    T(w, SX + SW * (n + 0.5), SY + 75, 66, GREEN if n < 2 else BLUE, k0=2 * n + 1.1, k1=2 * n + 1.6)

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 6450), (2650, 6450), (950, 7400), (2650, 7400)]
ZV = (1800, 6900, 0.355)
scene("身边就有例子", "身边的例子", ZV)
T("身边的例子", 1800, 5920, 100, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1150, 860, 40), 1 + n, 1.5 + n, GREEN, 8, sfx="wood_high")

scene("帮一把，约上午饭", "例子 · 职场", (900, 6450, 0.85))
L(printer(1150, 6570), 0, 0.7, sfx="wood_high")
L(scribble(1150, 6410, 160, 90, 6), 1, 1.4, RED, 7, sfx="shaker")
T("卡纸！", 1150, 6200, 64, RED, k0=1.4, k1=1.9)
L(stick(720, 6800, 0.75, "shrug"), 2, 2.5, sfx="pop")
L(face(720, 6800, 0.75, "sad"), 2.5, 2.6)
L(stick(1390, 6800, 0.75, "point"), 3, 3.5, BLUE, sfx="wood_high")
L(check(1150, 6570, 50), 4, 4.3, GREEN, 10, sfx="ding")
L(bubble(720, 6210, 400, 130, tail=0.1), 5, 5.3, BLACK, 7, sfx="pop")
T("一起吃午饭？", 720, 6210, 48, k0=5.3, k1=5.9)

scene("借个梯子，认识了", "例子 · 生活", (2700, 6450, 0.85))
L(door(2350, 6600), 0, 0.6, sfx="wood_high")
L(stick(2620, 6800, 0.75, "point"), 1, 1.5, BLUE, sfx="pop")
L(face(2620, 6800, 0.75, "smile"), 1.5, 1.6, BLUE)
L(bubble(2700, 6200, 340, 120), 2, 2.4, BLACK, 7, sfx="pop")
T("有梯子吗？", 2700, 6200, 46, k0=2.4, k1=3.0)
L(ladder(3080, 6550), 3, 3.6, sfx="wood_high")
L(bag(2830, 6740), 4, 4.4, BLACK, 8, sfx="pop")
L(heads([(2790, 6635), (2860, 6625), (2825, 6575)], 30), 4.4, 4.8, ORANGE, 8)
T("认识了", 2350, 6300, 56, GREEN, k0=5, sfx="ding")

TABLE = (950, 7510)
SEATS = [(720, 7390), (850, 7355), (1050, 7355), (1180, 7390), (770, 7630), (1130, 7630)]
scene("小读书会，加俩好友", "例子 · 小场合", (950, 7400, 0.85))
L(ellipse(*TABLE, 520, 150), 0, 0.6, BLACK, 8, sfx="wood_high")
L(heads(SEATS), 1, 1.6, BLUE, 7, sfx="pop")
T("周六 · 六个人", 950, 7120, 60, k0=2, sfx="pop")
L(book(950, 7510, 140, 70), 3, 3.4, GREEN, 6, sfx="wood_high")
L(phone(1370, 7430, 140, 230), 4, 4.5, BLACK, 7, sfx="wood_high")
L(check(1370, 7430, 40), 4.5, 4.8, GREEN, 9)
T("+2 好友", 1370, 7210, 54, GREEN, k0=5, sfx="ding")

scene("孩子转学，先约一个", "例子 · 家庭", (2650, 7400, 0.85))
L(building(2950, 7700, 300, 380), 0, 0.8, sfx="wood_high")
T("新学校", 2950, 7230, 56, k0=1, sfx="pop")
L(stick(2350, 7660, 0.55), 2, 2.4, sfx="wood_high")
L(face(2350, 7660, 0.55, "sad"), 2.4, 2.5)
T("下课一个人", 2440, 7230, 52, RED, k0=3, sfx="rim")
L(stick(2570, 7660, 0.55), 4, 4.4, BLUE, sfx="pop")
L(face(2570, 7660, 0.55, "smile"), 4.4, 4.5, BLUE)
T("周末来家玩", 2460, 7750, 50, k0=4.5, k1=5.2)
L(heart(2460, 7410, 32), 5.3, 5.6, RED, 7)
H(5, "ding")

scene("都是小小一步", "身边的例子", ZV, shake=[4])
for n, (x, y) in enumerate(CARDS):
    T("小一步", x + 400, y - 340, 110, RED, k0=n, k1=n + 0.5, sfx="pop")
T("小忙 · 小场合", 1800, 8020, 125, RED, k0=4, k1=4.8, sfx="kick")
H(5, "ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

scene("每天帮一个小忙", "第一件 · 帮小忙", (950, 9000, 0.85))
L(rect(950, 8900, 1200, 860, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("① 每天帮个小忙", 950, 8590, 70, BLUE, k0=0.6, k1=1.6)
L(stick(640, 9220, 0.75, "hold"), 2, 2.5, sfx="pop")
L(face(640, 9220, 0.75, "smile"), 2.5, 2.6)
L(cup(745, 9050, 0.45), 2.6, 2.9, BLACK, 7)
T("帮带杯水", 1150, 8800, 56, k0=3, sfx="pop")
T("扶一下门", 1150, 8920, 56, k0=4, sfx="pop")
T("一天一件", 1150, 9040, 56, RED, k0=5, sfx="ding")

scene("报个志愿，有活干", "第二件 · 做志愿", (2650, 9000, 0.85))
L(rect(2650, 8900, 1200, 860, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("② 报一次志愿", 2650, 8590, 70, BLUE, k0=0.6, k1=1.6)
L(heart(2330, 8920, 85), 2, 2.5, RED, 8, sfx="wood_high")
T("社区图书馆", 2850, 8840, 56, k0=3, sfx="pop")
T("整理书架", 2850, 8950, 52, k0=4, sfx="wood_high")
T("有活干，不冷场", 2650, 9040, 52, GREEN, k0=5, k1=5.9, sfx="ding")

LIST = ("1 楼下打招呼", "2 小读书会", "3 同事聚餐", "4 大派对")
scene("从最不怕的排起", "第三件 · 列清单", (950, 9850, 0.85))
L(rect(950, 9850, 1200, 860, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("③ 列个场合清单", 950, 9550, 70, BLUE, k0=0.6, k1=1.6)
L(rect(620, 9920, 220, 300, 14), 2, 2.4, BLACK, 8, sfx="pop")
for n in range(4):
    L(P((550, 9830 + n * 60), (700, 9830 + n * 60)), 2.4 + n * 0.12, 2.5 + n * 0.12, BLACK, 6)
for n in range(4):
    T(LIST[n], 1000, 9730 + n * 110, 52, BLUE if n == 3 else BLACK, k0=3 + n * 0.5, k1=3.45 + n * 0.5,
      sfx="pop" if n % 2 == 0 else None)
L(arrow((1230, 9720), (1230, 10060), -0.1, 34), 5, 5.4, GREEN, 8, sfx="wood_high")
T("每周一格", 1390, 9900, 48, GREEN, k0=5.4, k1=5.9)

scene("定好时间，留条退路", "第四件 · 定时间", (2650, 9850, 0.85))
L(rect(2650, 9850, 1200, 860, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("④ 定好时间和退路", 2650, 9550, 66, BLUE, k0=0.6, k1=1.6)
L(clock(2350, 9840, 120), 2, 2.5, sfx="wood_high")
L(hands_at(2350, 9840, 120, 3, 0), 2.5, 2.7, RED, 10)
T("周六下午三点", 2350, 10040, 54, RED, k0=3, sfx="pop")
L(door(3020, 9880), 4, 4.5, sfx="wood_high")
T("待一小时", 2680, 9800, 50, k0=4.5, k1=5.0)
T("想走就走", 2680, 9910, 50, GREEN, k0=5, k1=5.6, sfx="pop")
L(arrow((2960, 10090), (3200, 10090), 0, 34), 5.6, 5.9, GREEN, 8)

scene("小步走，不着急", "一句话", (1800, 5450, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 11000, 0.8))
H(0, "cymbal", 0.5)
T("你这周先做哪件？", 1800, 10920, 80, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：交朋友，该找谁、怎么想？", 1800, 11080, 50, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "extend", "迈出第一步", "想交朋友，第一步迈哪？", ACC, b.shots,
                 [f"{BOOK}第 14 章 · EASE 中的 Extend yourself 与 Action plan（转述）",
                  "中译本：焦梦津译，中国人民大学出版社 2009（第三部分“14 个体困境的解药”）"],
                 "想交朋友|第一步【迈哪】", 8,
                 ["书中观点均为转述：书末第 14 章（中译本“个体困境的解药”）给出走出孤独的办法，作者用 EASE 四个字母概括；"
                  "本讲讲前两个——Extend yourself（先迈一小步，比如做志愿、帮别人一个小忙）和 Action plan（有个计划，"
                  "先从低风险的小场合开始，别一上来就去大型社交）；后两个 Selection、Expect the best 留到下一讲。"
                  "出处：John T. Cacioppo & William Patrick, Loneliness: Human Nature and the Need for Social Connection "
                  "(W. W. Norton, 2008)，中译本《孤独是可耻的》（约翰·卡乔波、威廉·帕特里克著，焦梦津译，中国人民大学出版社 "
                  "2009）。上屏均为转述，不是逐字引文。",
                  "搬到新城市三年、读书会、打印机卡纸、借梯子、六个人的读书会、孩子转学均为现实场景示意，不指向任何具体公司"
                  "或个人；台阶图为对书中“先小后大”思路的通俗化示意；人数、时间为示意，不是数据。",
                  "四件做法（每天帮一个小忙、报一次志愿、列场合清单从最不怕的排起、定好时间和退路）为据书中思路整理的建议。"],
                 tags="#交朋友 #社交")
    return b.attach(ep)
