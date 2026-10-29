"""03 孤独伤身（白板手绘版）：一个人住久了，为什么总睡不好？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
叙事：切身问题开局（一个人住出租屋 → 半夜醒 → 翻来覆去 → 白天上班犯困 → 周末补觉也累 → 抛问题）→
书中观点（亮书《孤独是可耻的》、卡乔波；作者团队比较孤独和不孤独的两群人：孤独的人睡得更浅、夜里更容易短暂醒来，
压力反应更大、血压更高；第六章“孤独的磨损”——身体被慢慢磨损，一两天看不出来，日子久了才显出来；画成一张图）→
身边的例子（外派到新城市、周末两天没说话、加班推掉饭局、老爸一个人在老家；最后连到同一个原因）→
具体做法（睡前跟人说说话 / 作息固定 / 每周固定见一次人 / 先迈一小步）→ 评论区互动 + 下一讲预告。
书中观点为转述（Cacioppo & Patrick, Loneliness, 2008，第六章；中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社
2009）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, building, check, circle, clock, cross,
                               desk, face, hands_at, join, marker, rect, scribble, stick, underline)
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#5B6FA8"
SQUARE_SHOT = 0

b = Board(size=(3600, 14300))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def E(k0, k1, x, y, w, h):
    b.erase(len(b.shots) - 1, k0, k1, x, y, w, h)


# ---------------------------------------------------------------- 本讲画法

def moon(x, y, r=70) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def phone(x, y, w=110, h=190) -> skia.Path:
    return join(rect(x, y, w, h, 16), P((x - 18, y + h / 2 - 22), (x + 18, y + h / 2 - 22)))


def bed(x, y, w=440) -> skia.Path:
    """床（侧视）：(x, y) 为床面中点。"""
    return join(P((x - w / 2, y - 120), (x - w / 2, y + 90)), P((x + w / 2, y - 40), (x + w / 2, y + 90)),
                P((x - w / 2, y + 40), (x + w / 2, y + 40)), rect(x - w / 2 + 80, y - 10, 110, 50, 20),
                P((x - w / 2 + 150, y + 10), (x - w / 2 + 170, y - 40), (x + w / 2, y - 40), (x + w / 2, y + 40)))


def head_on(x, y, w=440, awake=True) -> skia.Path:
    """躺在 bed(x, y, w) 枕头上的头；awake 时睁着眼。"""
    hx, hy = x - w / 2 + 80, y - 72
    p = circle(hx, hy, 38)
    if awake:
        p.addCircle(hx - 13, hy - 6, 5)
        p.addCircle(hx + 13, hy - 6, 5)
    else:
        p.moveTo(hx - 20, hy - 4)
        p.lineTo(hx - 6, hy - 4)
        p.moveTo(hx + 6, hy - 4)
        p.lineTo(hx + 20, hy - 4)
    return p


def window(x, y, w=220, h=180) -> skia.Path:
    return join(rect(x, y, w, h, 8), P((x, y - h / 2), (x, y + h / 2)), P((x - w / 2, y), (x + w / 2, y)))


def heart(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + 90 * s)
    p.cubicTo(x - 160 * s, y - 10 * s, x - 90 * s, y - 120 * s, x, y - 50 * s)
    p.cubicTo(x + 90 * s, y - 120 * s, x + 160 * s, y - 10 * s, x, y + 90 * s)
    return p


def house(x, y, w=360, h=260) -> skia.Path:
    """平房：(x, y) 为墙体中心。"""
    return join(rect(x, y, w, h, 6), P((x - w / 2 - 40, y - h / 2), (x, y - h / 2 - 170), (x + w / 2 + 40, y - h / 2)),
                P((x - 40, y + h / 2), (x - 40, y + h / 2 - 120), (x + 40, y + h / 2 - 120), (x + 40, y + h / 2)),
                rect(x + 110, y - 20, 70, 70, 4))


def arc(x, y, r, a0, sweep) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), a0, sweep)
    return p


def smooth(*pts) -> skia.Path:
    p = skia.Path()
    p.moveTo(*pts[0])
    for i in range(1, len(pts) - 1):
        mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
        p.quadTo(pts[i][0], pts[i][1], mx, my)
    p.lineTo(*pts[-1])
    return p


def needle(x, y, r, a_from, a_to):
    """压力表指针：从 a_from 度转到 a_to 度（屏幕角度，0 向右，180 向左）。"""

    def fn(c, k, t):
        a = math.radians(a_from + (a_to - a_from) * ease_out(clamp01(k)))
        ex, ey = x + r * math.cos(a), y + r * math.sin(a)
        c.drawPath(P((x, y), (ex, ey)), marker(RED, 11))
        c.drawCircle(x, y, 16, marker(RED, 10))
        return ex, ey

    return fn


# ---------------------------------------------------------------- 开局：一个人住，老睡不好（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("一个人住，半夜又醒", "灵魂拷问", (950, 850, 0.85))
L(rect(950, 900, 1100, 800, 30), 0, 0.8, BLACK, 9, sfx="wood_high")
L(window(650, 680), 1, 1.4, BLACK, 8, sfx="pop")
L(moon(650, 680, 55), 1.4, 1.8, BLUE, 8)
L(bed(800, 1150, 480), 2, 2.7, sfx="wood_high")
L(head_on(800, 1150, 480), 2.7, 3.0, BLACK, 9)
T("出租屋", 950, 420, 72, k0=3, sfx="pop")
L(clock(1280, 700, 95), 4, 4.5, sfx="pop")
L(hands_at(1280, 700, 95, 3, 0), 4.5, 4.7, RED, 10)
L(scribble(900, 1100, 300, 110, 6), 5, 5.5, RED, 7, sfx="shaker")
T("醒了", 760, 960, 66, RED, k0=5.5, k1=6.0)

scene("白天犯困，补觉也累", "灵魂拷问", (2650, 1320, 0.62))
T("下午 3 点", 2650, 700, 80, RED, k0=0, k1=0.7, sfx="rim")
L(desk(2900, 1100, 420), 1, 1.8, sfx="wood_high")
L(stick(2450, 1250, 0.8), 2, 2.5, sfx="pop")
L(face(2450, 1250, 0.8, "sad"), 2.5, 2.7)
T("Zzz", 2560, 900, 64, BLUE, k0=2.7, k1=3.0)
L(bed(2700, 1750, 560), 3, 3.8, sfx="wood_high")
L(head_on(2700, 1750, 560, awake=False), 3.8, 4.0)
L(clock(3150, 1420, 95), 4, 4.5, sfx="pop")
L(hands_at(3150, 1420, 95, 12, 0), 4.5, 4.7, RED, 10)
T("睡到 12 点", 2450, 1420, 60, k0=4.7, k1=5.0)
T("还是累", 2750, 2010, 76, RED, k0=5, k1=5.6, sfx="rim")

scene("怎么老睡不好？", "灵魂拷问", (1820, 1350, 0.37), flashes=[0])
T("？", 950, 1800, 480, RED, k0=0, k1=0.6, sfx="kick")
T("老睡不好", 950, 2250, 130, k0=1.0, k1=2.0, sfx="pop")
L(underline(700, 1200, 2340, 14, 40), 3, 3.5, RED, 9, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

scene("有本书比过两群人", "孤独是可耻的", (1050, 3300, 0.85))
L(book(750, 3050, 420, 280), 0, 0.8, sfx="wood_low")
T("孤独是可耻的", 750, 2800, 76, GREEN, k0=1.0, sfx="pop")
T("约翰 · 卡乔波", 750, 3290, 50, k0=2.0, k1=2.9, sfx="pop")
for n, x in enumerate((600, 720, 840)):
    L(stick(x, 3690, 0.45), 3 + n * 0.25, 3.4 + n * 0.25, BLUE, 8, sfx="wood_high" if n == 0 else None)
T("孤独的人", 720, 3450, 54, BLUE, k0=3.9, k1=4.5)
for n, x in enumerate((1260, 1380, 1500)):
    L(stick(x, 3690, 0.45), 4.5 + n * 0.15, 4.85 + n * 0.15, BLACK, 8)
T("不孤独的人", 1380, 3450, 54, k0=5, k1=5.8, sfx="pop")


def wave_y(x):
    return 3260 + 34 * math.sin((x - 2100) / 70)


WAVE = [(x, wave_y(x)) for x in range(2100, 3221, 35)]
scene("睡得浅，还老醒", "书中观点 · 睡眠", (2650, 3150, 0.8), shake=[0], flashes=[0])
T("睡得浅", 2650, 2800, 150, RED, k0=0, k1=0.5, sfx="kick")
L(P((2100, 3450), (3200, 3450)), 1, 1.5, BLACK, 8, sfx="wood_high")
T("23:00", 2150, 3530, 56, k0=1.5, k1=1.9)
T("7:00", 3150, 3530, 56, k0=1.6, k1=2.0)
L(smooth(*WAVE), 2, 2.9, BLUE, 9, sfx="pop")
for n, x in enumerate((2330, 2580, 2840, 3070)):
    L(P((x, wave_y(x)), (x, 3030)), 3 + n * 0.5, 3.3 + n * 0.5, RED, 10, sfx="rim" if n % 2 == 0 else None)
T("夜里短暂醒来", 2650, 3640, 58, RED, k0=5, k1=5.9, sfx="pop")

GX, GY = 1500, 4600
scene("压力大，血压也高", "书中观点 · 压力与血压", (1800, 4650, 0.85))
L(join(arc(GX, GY, 210, 180, 180), P((GX - 210, GY), (GX + 210, GY))), 0, 0.8, BLACK, 9, sfx="wood_high")
L(arc(GX, GY, 185, 300, 60), 0.8, 1.0, RED, 14)
T("压力反应", GX, GY + 90, 60, k0=1, k1=1.7, sfx="pop")
b.custom(len(b.shots) - 1, 2, 2.8, needle(GX, GY, 170, 200, 330), sfx="rim")
T("偏大", GX, GY + 200, 72, RED, k0=3, k1=3.5, sfx="pop")
L(heart(2100, GY - 70, 0.95), 4, 4.6, RED, 10, sfx="wood_high")
T("血压", 2100, GY + 90, 60, k0=4.6, k1=5.0)
L(arrow((2320, GY + 50), (2320, GY - 190), 0, 40), 5, 5.3, RED, 10, sfx="rim")
T("偏高", 2100, GY + 200, 72, RED, k0=5.3, k1=5.8)

C = 5850                        # 磨损区块（场景 7–9 同一视角）
BAT = (1680, C - 250)
BARS = [BAT[0] + d for d in (-165, -55, 55, 165)]
scene("磨损，一两天看不出", "书中观点 · 磨损", (1800, C, 0.8))
T("第六章 孤独的磨损", 1800, C - 520, 60, GREEN, k0=0, k1=1.0, sfx="pop")
L(join(rect(*BAT, 480, 210, 24), rect(BAT[0] + 262, BAT[1], 44, 90, 10)), 1, 1.7, BLACK, 9, sfx="wood_high")
for n, x in enumerate(BARS):
    L(rect(x, BAT[1], 90, 150, 10), 2 + n * 0.2, 2.2 + n * 0.2, GREEN, 9, sfx="pop" if n == 0 else None)
T("身体", 1330, BAT[1], 60, k0=3, sfx="pop")
T("一两天：没事", 1550, C + 60, 60, k0=4, k1=4.9, sfx="pop")
L(check(1880, C + 50, 40), 5, 5.3, GREEN, 10, sfx="ding")

scene("日子久了才显出来", "书中观点 · 磨损", (1800, C, 0.8))
E(0, 0.5, BARS[3], BAT[1], 110, 175)
H(0, "shaker")
E(1, 1.5, BARS[2], BAT[1], 110, 175)
H(1, "shaker")
T("日子久了", 1550, C + 200, 66, RED, k0=2, sfx="rim")
L(rect(BARS[1], BAT[1], 90, 150, 10), 3, 3.3, RED, 10, sfx="pop")
L(underline(1410, 1690, C + 250, 10, 30), 4, 4.4, RED, 8, sfx="ding")

scene("最后都落在身上", "书中观点 · 一张图", (1800, C, 0.8), shake=[4])
for n, (w, col) in enumerate((("睡得浅", BLUE), ("压力大", RED), ("血压高", RED))):
    T(w, 2300, C - 380 + n * 130, 56, col, k0=n, k1=n + 0.6, sfx="pop")
L(join(*[arrow((2200, C - 380 + n * 130), (1985, BAT[1]), 0, 30) for n in range(3)]), 3, 3.6, RED, 8,
  sfx="wood_high")
T("长期孤独", 1800, C + 400, 110, RED, k0=4, k1=4.6, sfx="kick")
L(rect(1620, BAT[1], 760, 300, 50), 5, 5.6, RED, 10, sfx="rim")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

EC = 8610                       # 例子区中心；两行卡片间距 1150，避免上一行的字漏进页眉
R1, R2 = EC - 575, EC + 575
CARDS = [(950, R1), (2650, R1), (950, R2), (2650, R2)]
scene("身边也常见", "身边的例子", (1800, EC, 0.355))
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), n, n + 0.5, GREEN, 8, sfx="wood_high" if n % 2 == 0 else None)
T("身边的例子", 1800, EC, 110, k0=4, k1=5, sfx="pop")

scene("外派，下班没人说话", "例子 · 外派", (950, R1, 0.85))
E(0, 0.4, 1800, EC, 640, 150)              # 总览标题擦掉，免得漏进后面卡片镜头的画面边缘
L(building(650, R1 + 270), 0, 0.8, sfx="wood_high")
L(stick(1000, R1 + 320, 0.8, "hold"), 1, 1.5, sfx="pop")
L(rect(1120, R1 + 245, 90, 110, 10), 1.5, 1.8)
T("外派到新城市", 950, R1 - 300, 72, BLUE, k0=2, k1=2.9, sfx="pop")
L(rect(1270, R1 - 80, 260, 140, 40), 3, 3.4, BLACK, 8, sfx="wood_high")
T("……", 1270, R1 - 80, 60, k0=3.4, k1=3.9)
L(face(1000, R1 + 320, 0.8, "sad"), 4, 4.2, BLACK, 8, sfx="pop")
T("夜里醒 3 回", 1300, R1 + 80, 56, RED, k0=5, k1=5.9, sfx="rim")

scene("周末没开口，夜里醒着", "例子 · 周末", (2650, R1, 0.85))
L(join(rect(2420, R1 - 190, 190, 190, 14), rect(2660, R1 - 190, 190, 190, 14)), 0, 0.8, BLACK, 8, sfx="wood_high")
T("六", 2420, R1 - 180, 80, k0=1, k1=1.3, sfx="pop")
T("日", 2660, R1 - 180, 80, k0=1.3, k1=1.6)
T("0 句话", 3000, R1 - 150, 76, RED, k0=2, k1=2.7, sfx="pop")
L(moon(3150, R1 + 80, 60), 3, 3.5, BLUE, 8, sfx="wood_high")
L(bed(2900, R1 + 280, 380), 4, 4.6, sfx="pop")
L(head_on(2900, R1 + 280, 380), 4.6, 4.8)
T("1:00 还醒着", 2830, R1 + 60, 52, RED, k0=5, k1=5.9, sfx="rim")

scene("加班推掉了饭局", "例子 · 加班", (950, R2, 0.85))
L(desk(820, R2 + 150, 360), 0, 0.6, sfx="wood_high")
L(stick(520, R2 + 340, 0.75), 0.6, 0.95)
L(rect(1000, R2 - 240, 400, 130, 40), 1, 1.4, BLUE, 8, sfx="pop")
T("周五吃饭？", 1000, R2 - 240, 54, BLUE, k0=1.4, k1=1.9)
L(cross(1000, R2 - 240, 80), 2, 2.3, RED, 12, sfx="rim")
T("不去了", 1250, R2 - 60, 54, k0=3, sfx="pop")
L(face(520, R2 + 340, 0.75, "sad"), 4, 4.3, BLACK, 8, sfx="wood_high")
T("3 个月没见", 950, R2 + 330, 60, RED, k0=5, k1=5.9, sfx="pop")

scene("老爸在老家，夜里老醒", "例子 · 老家", (2650, R2, 0.85))
L(house(2420, R2 + 200), 0, 0.9, sfx="wood_high")
L(stick(2880, R2 + 350, 0.8), 1, 1.5, sfx="pop")
L(join(face(2880, R2 + 350, 0.8, "flat"), P((2950, R2 + 200), (2970, R2 + 350))), 1.5, 1.8)
T("老家", 2420, R2 - 210, 62, k0=2, sfx="pop")
L(phone(3150, R2 - 170, 90, 150), 3, 3.4, BLUE, 8, sfx="wood_high")
L(rect(2880, R2 - 290, 340, 120, 40), 3.4, 3.8, BLACK, 8)
T("夜里老醒", 2880, R2 - 290, 56, k0=4, k1=4.7, sfx="pop")
T("血压又高", 2950, R2 - 70, 56, RED, k0=5, k1=5.7, sfx="rim")

scene("都少个说话的人", "身边的例子", (1800, EC, 0.355), shake=[4])
for n, (x, y) in enumerate(((1370, R1 - 330), (3070, R1 - 330), (1370, R2 - 330), (2380, R2 - 340))):
    T("孤单", x, y, 100, RED, k0=n, k1=n + 0.6, sfx="pop")
T("孤单 → 睡不好", 1800, EC + 1150, 170, RED, k0=4, k1=4.8, sfx="kick")
H(5, "ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

P1 = 10810
P2 = P1 + 1350
SOL = [(950, P1), (2650, P1), (950, P2), (2650, P2)]
scene("睡前跟人说几句", "第一步 · 说说话", (950, P1 + 30, 0.85))
L(rect(*SOL[0], 1200, 860, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("① 睡前说说话", 950, P1 - 300, 76, BLUE, k0=0.5, k1=1.5)
L(phone(640, P1 + 10), 2, 2.4, BLACK, 9, sfx="pop")
L(rect(1030, P1 - 40, 420, 150, 40), 2.4, 2.8, BLUE, 8)
T("今天咋样？", 1030, P1 - 40, 56, BLUE, k0=2.8, k1=3.4)
T("打给：老妈 / 老同学", 950, P1 + 220, 56, k0=4, k1=4.9, sfx="pop")
T("10 分钟就够", 950, P1 + 350, 60, RED, k0=5, k1=5.8, sfx="rim")

scene("上床起床都定点", "第二步 · 作息", (2650, P1 + 30, 0.85))
L(rect(*SOL[1], 1200, 860, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("② 作息固定", 2650, P1 - 300, 76, BLUE, k0=0.5, k1=1.4)
L(clock(2380, P1 + 10, 140), 2, 2.5, sfx="wood_high")
L(hands_at(2380, P1 + 10, 140, 11, 0), 2.5, 2.7, RED, 11)
T("23:00 上床", 2900, P1 - 50, 58, k0=3, k1=3.7, sfx="pop")
T("7:30 起床", 2900, P1 + 70, 58, k0=4, k1=4.7, sfx="pop")
T("周末也 8 点起", 2650, P1 + 270, 58, RED, k0=5, k1=5.9, sfx="rim")

scene("每周见一次人", "第三步 · 见人", (950, P2 + 50, 0.85))
L(rect(*SOL[2], 1200, 860, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("③ 每周见一次人", 950, P2 - 300, 72, BLUE, k0=0.5, k1=1.4)
L(join(*[rect(590 + n * 120, P2 - 90, 100, 100, 10) for n in range(7)]), 1.5, 2.0, BLACK, 7)
for n, d in enumerate("一二三四五六日"):
    T(d, 590 + n * 120, P2 - 80, 50, k0=2 + n * 0.08, k1=2.15 + n * 0.08, sfx="pop" if n == 0 else None)
L(circle(830, P2 - 90, 72), 3, 3.3, RED, 9, sfx="pop")
T("周三 午饭", 950, P2 + 100, 60, RED, k0=3.3, k1=3.9)
L(join(stick(760, P2 + 380, 0.55, "hold"), face(760, P2 + 380, 0.55, "smile")), 4, 4.5, BLACK, 8, sfx="wood_high")
L(join(stick(1140, P2 + 380, 0.55, "hold"), face(1140, P2 + 380, 0.55, "smile")), 4.5, 5.0, BLUE, 8)
L(join(P((830, P2 + 250), (1070, P2 + 250)), P((870, P2 + 250), (870, P2 + 380)),
       P((1030, P2 + 250), (1030, P2 + 380))), 5, 5.4, BLACK, 9, sfx="pop")

scene("先迈一小步", "第四步 · 一小步", (2650, P2 + 50, 0.85))
L(rect(*SOL[3], 1200, 860, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("④ 先迈一小步", 2650, P2 - 300, 72, BLUE, k0=0.5, k1=1.4)
L(stick(2350, P2 + 250, 0.8, "hold"), 1.5, 2.0, BLACK, 9)
L(join(rect(2520, P2 + 100, 130, 110, 8), P((2455, P2 + 70), (2585, P2 + 70))), 2, 2.4, BLACK, 8, sfx="pop")
T("帮邻居收快递", 2900, P2 - 110, 56, k0=2.5, k1=3.4)
L(rect(2840, P2 + 100, 200, 120, 40), 4, 4.4, BLACK, 8, sfx="wood_high")
T("早！", 2840, P2 + 100, 66, RED, k0=4.4, k1=4.8)
L(join(stick(3150, P2 + 370, 0.6), face(3150, P2 + 370, 0.6, "smile")), 5, 5.5, BLUE, 8, sfx="pop")

scene("孤单，身体记着", "一句话", (1800, 9400, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

CM = P2 + 1350
scene("评论区聊聊", "评论区见", (1800, CM, 0.8))
H(0, "cymbal", 0.5)
T("你一个人住多久了？", 1800, CM - 90, 80, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：越孤单，为什么越不想见人？", 1800, CM + 70, 48, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "health", "孤独伤身", "一个人住久了，为什么总睡不好？", ACC, b.shots,
                 [f"{BOOK}第六章 · 孤独的磨损（转述）", "中译本：《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009"],
                 "一个人住久了|为什么总【睡不好】", 0,
                 ["书中观点均为转述：作者团队比较孤独与不孤独的人，发现孤独的人睡眠质量更差、夜里更容易短暂醒来，"
                  "压力反应和血压等指标更差；长期孤独让身体被慢慢磨损（第六章“孤独的磨损”）。上屏均为转述，不是逐字引文，"
                  "片中不给具体研究数字。出处：John T. Cacioppo & William Patrick, Loneliness: Human Nature and the Need for "
                  "Social Connection (W. W. Norton, 2008)，中译本《孤独是可耻的》（约翰·卡乔波、威廉·帕特里克著，焦梦津译，"
                  "中国人民大学出版社 2009）。",
                  "出租屋半夜醒、外派到新城市、周末两天没说话、加班推掉饭局、老爸一个人在老家均为现实场景示意，"
                  "不指向任何具体公司或个人；片中钟点、醒来次数、“3 个月”、电量格、压力表、睡眠曲线均为示意，不是数据。",
                  "四件事（睡前跟人说说话、作息固定、每周固定见一次人、先迈一小步）为据书中思路整理的建议"
                  "（“先迈一小步”对应第十四章 EASE 中的 Extend yourself）；作息固定为常见作息建议，示意。"],
                 tags="#睡眠 #健康")
    return b.attach(ep)
