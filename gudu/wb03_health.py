"""03 孤独伤身（白板手绘版）：一个人住久了，为什么总睡不好？

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
SQUARE_SHOT = 2

b = Board(size=(3600, 10800))


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


# ---------------------------------------------------------------- 开局：一个人住，老睡不好（镜头 1–6）

b.shot("一个人住出租屋", "灵魂拷问", view=(950, 850, 0.85))
L(rect(950, 900, 1100, 800, 30), 0, 0.8, BLACK, 9, sfx="wood_high")
L(window(650, 680), 1, 1.4, BLACK, 8, sfx="pop")
L(bed(800, 1150, 480), 2, 2.7, sfx="wood_high")
L(stick(1250, 1280, 0.75), 2.7, 3.1)
T("出租屋", 950, 420, 72, k0=3, sfx="pop")

b.shot("半夜又醒了", "灵魂拷问", view=(950, 850, 0.85))
E(0, 0.6, 1250, 1130, 260, 330)
H(0, "shaker")
L(moon(650, 680, 55), 0.4, 0.9, BLUE, 8)
L(head_on(800, 1150, 480), 1, 1.3, BLACK, 9, sfx="pop")
L(clock(1280, 700, 95), 2, 2.6, sfx="wood_high")
L(hands_at(1280, 700, 95, 3, 0), 2.6, 2.8, RED, 10)
T("醒了", 760, 960, 66, RED, k0=3, sfx="rim")

b.shot("翻来覆去睡不着", "灵魂拷问", view=(950, 850, 0.85))
L(scribble(820, 1110, 480, 170, 7), 0, 0.6, RED, 7, sfx="shaker")
T("3:00", 1280, 850, 60, RED, k0=1, sfx="pop")
T("4:30 又醒", 1260, 1250, 54, RED, k0=2, sfx="pop")
H(3, "wood_low")

b.shot("白天上班犯困", "灵魂拷问", view=(2650, 850, 0.85))
L(desk(2760, 1050, 420), 0, 0.8, sfx="wood_high")
L(stick(2380, 1250, 0.8), 1, 1.5, sfx="pop")
L(face(2380, 1250, 0.8, "sad"), 1.5, 1.7)
T("Zzz", 2480, 840, 64, BLUE, k0=2, sfx="pop")
T("下午 3 点", 2650, 470, 72, RED, k0=3, k1=3.7, sfx="rim")

b.shot("周末补觉也累", "灵魂拷问", view=(950, 1800, 0.85))
L(bed(950, 1900, 560), 0, 0.8, sfx="wood_high")
L(head_on(950, 1900, 560, awake=False), 0.8, 1.0)
L(clock(1350, 1500, 95), 1, 1.5, sfx="pop")
L(hands_at(1350, 1500, 95, 12, 0), 1.5, 1.7, RED, 10)
T("睡到 12 点", 700, 1450, 60, k0=2, sfx="pop")
T("还是累", 1000, 2170, 76, RED, k0=3, sfx="rim")

b.shot("怎么老睡不好？", "灵魂拷问", view=(1800, 1330, 0.4), flashes=[0])
T("？", 2650, 1650, 520, RED, k0=0, k1=0.6, sfx="kick")
T("老睡不好", 2650, 2200, 130, k0=1.0, k1=2.0, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "孤独是可耻的", view=(1050, 3050, 0.9))
L(book(750, 3050, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 750, 2800, 76, GREEN, k0=1.0, sfx="pop")
T("约翰 · 卡乔波", 750, 3290, 50, k0=2.0, sfx="pop")

b.shot("他们比过两群人", "书中观点 · 两群人", view=(1050, 3300, 0.9))
for n, x in enumerate((600, 720, 840)):
    L(stick(x, 3690, 0.45), n * 0.25, n * 0.25 + 0.4, BLUE, 8, sfx="wood_high" if n == 0 else None)
T("孤独的人", 720, 3450, 54, BLUE, k0=1, sfx="pop")
for n, x in enumerate((1260, 1380, 1500)):
    L(stick(x, 3690, 0.45), 2 + n * 0.25, 2.4 + n * 0.25, BLACK, 8, sfx="wood_high" if n == 0 else None)
T("不孤独的人", 1380, 3450, 54, k0=3, k1=3.7, sfx="pop")


def wave_y(x):
    return 3260 + 34 * math.sin((x - 2100) / 70)


WAVE = [(x, wave_y(x)) for x in range(2100, 3221, 35)]
b.shot("孤独的人睡得浅", "书中观点 · 睡眠", view=(2650, 3150, 0.8), shake=[0], flashes=[0])
T("睡得浅", 2650, 2800, 150, RED, k0=0, k1=0.5, sfx="kick")
L(P((2100, 3450), (3200, 3450)), 1, 1.5, BLACK, 8, sfx="wood_high")
T("23:00", 2150, 3530, 56, k0=1.5, k1=1.9)
T("7:00", 3150, 3530, 56, k0=1.6, k1=2.0)
L(smooth(*WAVE), 2, 2.9, BLUE, 9, sfx="pop")
L(underline(2440, 2860, 2900), 3, 3.5, RED, 8, sfx="ding")

b.shot("夜里醒得更多", "书中观点 · 睡眠", view=(2650, 3150, 0.8))
for n, x in enumerate((2330, 2580, 2840, 3070)):
    L(P((x, wave_y(x)), (x, 3030)), n * 0.9, n * 0.9 + 0.3, RED, 10, sfx=("rim", "pop", "rim", None)[n])
T("短暂醒来", 2650, 3640, 58, RED, k0=3, sfx="pop")

GX, GY = 850, 4250
b.shot("压力反应更大", "书中观点 · 压力", view=(950, 4050, 0.85))
L(join(arc(GX, GY, 210, 180, 180), P((GX - 210, GY), (GX + 210, GY))), 0, 0.8, BLACK, 9, sfx="wood_high")
L(arc(GX, GY, 185, 300, 60), 0.8, 1.0, RED, 14)
T("压力反应", GX, 4340, 60, k0=1, sfx="pop")
b.custom(len(b.shots) - 1, 2, 2.8, needle(GX, GY, 170, 200, 330), sfx="rim")
T("偏大", 1300, 4150, 72, RED, k0=3, sfx="pop")

b.shot("血压也更高", "书中观点 · 血压", view=(2650, 4050, 0.85))
L(heart(2550, 4150, 1.05), 0, 0.8, RED, 10, sfx="wood_high")
T("血压", 2550, 4370, 60, k0=1, sfx="pop")
L(arrow((2930, 4330), (2930, 3990), 0, 44), 2, 2.4, RED, 10, sfx="rim")
T("偏高", 3120, 4160, 72, RED, k0=3, sfx="pop")

BAT = (1750, 4620)
BARS = [1555, 1685, 1815, 1945]
b.shot("身体慢慢被磨损", "书中观点 · 磨损", view=(1800, 4750, 0.85))
T("第六章 孤独的磨损", 1800, 4330, 62, GREEN, k0=0, k1=1.4, sfx="pop")
L(join(rect(*BAT, 560, 240, 24), rect(BAT[0] + 305, BAT[1], 50, 100, 10)), 1, 1.7, BLACK, 9, sfx="wood_high")
for n, x in enumerate(BARS):
    L(rect(x, BAT[1], 100, 180, 10), 2 + n * 0.2, 2.2 + n * 0.2, GREEN, 9, sfx="pop" if n == 0 else None)
T("身体", 1330, 4625, 62, k0=3, sfx="pop")

b.shot("一两天看不出来", "书中观点 · 磨损", view=(1800, 4750, 0.85))
T("一两天：没事", 1700, 4960, 60, k0=0, sfx="pop")
L(check(2030, 4950, 40), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("日子久了才显出来", "书中观点 · 磨损", view=(1800, 4750, 0.85))
E(0, 0.5, BARS[3], BAT[1], 120, 205)
H(0, "shaker")
E(1, 1.5, BARS[2], BAT[1], 120, 205)
H(1, "shaker")
T("日子久了", 1700, 5110, 66, RED, k0=2, sfx="rim")
L(rect(BARS[1], BAT[1], 100, 180, 10), 3, 3.3, RED, 10, sfx="pop")

b.shot("这三样一起磨", "书中观点 · 一张图", view=(1850, 3950, 0.36))
L(arrow((2350, 3600), (2000, 4470), 0.08, 50), 0, 0.6, RED, 11, sfx="wood_high")
L(arrow((1100, 4290), (1440, 4560), -0.1, 50), 1, 1.6, RED, 11, sfx="wood_high")
L(arrow((2470, 4330), (2120, 4540), 0.1, 50), 2, 2.6, RED, 11, sfx="wood_high")
H(3, "ding", 0.6)

b.shot("最后都落在身上", "书中观点 · 一张图", view=(1850, 3950, 0.36), shake=[0])
T("长期孤独", 1720, 3980, 150, RED, k0=0, k1=0.6, sfx="kick")
L(arrow((1720, 4070), (1720, 4280), 0, 40), 1, 1.3, RED, 10, sfx="pop")
L(rect(1790, 4620, 760, 340, 60), 2, 2.8, RED, 10, sfx="rim")
H(3, "ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5980), (2650, 5980), (950, 6930), (2650, 6930)]
b.shot("身边也常见", "身边的例子", view=(1800, 6450, 0.355))
T("身边的例子", 1800, 5450, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("外派到新城市", "例子 · 外派", view=(950, 5980, 0.85))
L(building(650, 6250), 0, 0.8, sfx="wood_high")
L(stick(1000, 6300, 0.8, "hold"), 1, 1.5, sfx="pop")
L(rect(1120, 6225, 90, 110, 10), 1.5, 1.8)
T("外派", 950, 5680, 72, BLUE, k0=2, sfx="pop")
T("新城市", 650, 5830, 54, k0=3, sfx="pop")

b.shot("下班回去没人说话", "例子 · 外派", view=(950, 5980, 0.85))
L(rect(1270, 5900, 260, 140, 40), 0, 0.5, BLACK, 8, sfx="wood_high")
T("……", 1270, 5900, 60, k0=1, sfx="pop")
L(face(1000, 6300, 0.8, "sad"), 1.5, 1.7, BLACK, 8)
T("夜里醒 3 回", 660, 6345, 56, RED, k0=2, sfx="rim")

b.shot("周末两天没说话", "例子 · 周末", view=(2650, 5980, 0.85))
L(join(rect(2420, 5790, 190, 190, 14), rect(2660, 5790, 190, 190, 14)), 0, 0.8, BLACK, 8, sfx="wood_high")
T("六", 2420, 5800, 80, k0=1, k1=1.3, sfx="pop")
T("日", 2660, 5800, 80, k0=1.3, k1=1.6)
T("0 句话", 3000, 5830, 76, RED, k0=2, sfx="pop")
L(stick(2400, 6360, 0.7), 3, 3.4, sfx="wood_high")
L(face(2400, 6360, 0.7, "flat"), 3.4, 3.6)

b.shot("周日晚上睡不着", "例子 · 周末", view=(2650, 5980, 0.85))
L(moon(3150, 6060, 60), 0, 0.5, BLUE, 8, sfx="wood_high")
L(bed(2900, 6260, 380), 1, 1.7, sfx="pop")
L(head_on(2900, 6260, 380), 1.7, 1.9)
T("1:00 还醒着", 2830, 6040, 52, RED, k0=2, sfx="rim")

b.shot("加班推掉了饭局", "例子 · 加班", view=(950, 6930, 0.85))
L(desk(820, 7080, 360), 0, 0.6, sfx="wood_high")
L(stick(520, 7270, 0.75), 0.6, 0.95)
L(rect(1000, 6690, 400, 130, 40), 1, 1.4, BLUE, 8, sfx="pop")
T("周五吃饭？", 1000, 6690, 54, BLUE, k0=1.4, k1=1.9)
L(cross(1000, 6690, 80), 2, 2.3, RED, 12, sfx="rim")
T("不去了", 1250, 6870, 54, k0=3, sfx="pop")

b.shot("好久没见朋友了", "例子 · 加班", view=(950, 6930, 0.85))
T("3 个月没见", 950, 7320, 60, RED, k0=0, sfx="pop")
T("Zzz", 640, 6920, 58, BLUE, k0=1, sfx="pop")
L(face(520, 7270, 0.75, "sad"), 2, 2.3, BLACK, 8, sfx="wood_high")

b.shot("老爸一个人在老家", "例子 · 老家", view=(2650, 6930, 0.85))
L(house(2420, 7130), 0, 0.9, sfx="wood_high")
L(stick(2880, 7280, 0.8), 1, 1.5, sfx="pop")
L(join(face(2880, 7280, 0.8, "flat"), P((2950, 7130), (2970, 7280))), 1.5, 1.8)
T("老家", 2420, 6720, 62, k0=2, sfx="pop")

b.shot("电话里说老醒", "例子 · 老家", view=(2650, 6930, 0.85))
L(phone(3150, 6760, 90, 150), 0, 0.4, BLUE, 8, sfx="pop")
L(rect(2880, 6640, 340, 120, 40), 0.4, 0.8, BLACK, 8)
T("夜里老醒", 2880, 6640, 56, k0=1, sfx="pop")
T("血压又高", 2950, 6860, 56, RED, k0=2, sfx="rim")

b.shot("都少个说话的人", "身边的例子", view=(1800, 6450, 0.355))
for n, (x, y) in enumerate(((1370, 5650), (3070, 5650), (1370, 6600), (2380, 6590))):
    T("孤单", x, y, 100, RED, k0=n, sfx="pop")

b.shot("睡不好跟着来", "身边的例子", view=(1800, 6450, 0.355), shake=[0])
T("孤单 → 睡不好", 1800, 7500, 170, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 8530), (2650, 8530), (950, 9480), (2650, 9480)]
b.shot("想睡踏实，这样做", "具体做法", view=(1800, 9000, 0.355))
T("想睡踏实：四件事", 1800, 8000, 125, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 860, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("睡前说说话", "第一步 · 说说话", view=(950, 8530, 0.85))
T("① 睡前说说话", 950, 8230, 76, BLUE, k0=0, sfx="pop")
L(phone(640, 8540), 1, 1.4, BLACK, 9, sfx="wood_high")
L(rect(1030, 8490, 420, 150, 40), 2, 2.5, BLUE, 8, sfx="pop")
T("今天咋样？", 1030, 8490, 56, BLUE, k0=2.5, k1=3.2)

b.shot("给老妈打个电话", "第一步 · 说说话", view=(950, 8580, 0.85))
T("打给：老妈 / 老同学", 950, 8750, 56, k0=0, k1=1.5, sfx="pop")
L(check(1320, 8740, 40), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("聊几句就挂也行", "第一步 · 说说话", view=(950, 8580, 0.85))
T("10 分钟就够", 950, 8880, 60, RED, k0=0, sfx="pop")
L(underline(780, 1120, 8930, 10, 30), 2, 2.4, RED, 8, sfx="ding")

b.shot("作息固定下来", "第二步 · 作息", view=(2650, 8530, 0.85))
T("② 作息固定", 2650, 8230, 76, BLUE, k0=0, sfx="pop")
L(clock(2380, 8540, 140), 1, 1.6, sfx="wood_high")
L(hands_at(2380, 8540, 140, 11, 0), 1.6, 1.8, RED, 11)
T("23:00 上床", 2900, 8480, 58, k0=2, sfx="pop")

b.shot("早上同一点起", "第二步 · 作息", view=(2650, 8580, 0.85))
T("7:30 起床", 2900, 8600, 58, k0=0, sfx="pop")
L(check(3170, 8590, 40), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("周末也别睡到中午", "第二步 · 作息", view=(2650, 8580, 0.85))
T("周末：睡到 12 点", 2650, 8790, 54, k0=0, k1=1.2, sfx="pop")
L(P((2440, 8790), (2880, 8790)), 2, 2.3, RED, 10, sfx="rim")
T("→ 8 点起", 2650, 8900, 58, RED, k0=3, k1=3.6, sfx="pop")

b.shot("每周见一次人", "第三步 · 见人", view=(950, 9480, 0.85))
T("③ 每周见一次人", 950, 9180, 72, BLUE, k0=0, k1=0.9, sfx="pop")
DAYS = "一二三四五六日"
L(join(*[rect(590 + n * 120, 9390, 100, 100, 10) for n in range(7)]), 1, 1.6, BLACK, 7, sfx="wood_high")
for n, d in enumerate(DAYS):
    T(d, 590 + n * 120, 9400, 50, k0=1.7 + n * 0.08, k1=1.85 + n * 0.08)
L(circle(830, 9390, 72), 3, 3.4, RED, 9, sfx="pop")
H(2, "wood_low", 0.6)

b.shot("约同事吃顿饭", "第三步 · 见人", view=(950, 9550, 0.85))
T("周三 午饭", 950, 9580, 60, RED, k0=0, sfx="pop")
L(join(stick(760, 9860, 0.55, "hold"), face(760, 9860, 0.55, "smile")), 1, 1.5, BLACK, 8, sfx="wood_high")
L(join(stick(1140, 9860, 0.55, "hold"), face(1140, 9860, 0.55, "smile")), 1.5, 2.0, BLUE, 8)
L(join(P((830, 9730), (1070, 9730)), P((870, 9730), (870, 9860)), P((1030, 9730), (1030, 9860))), 2, 2.4, BLACK, 9, sfx="pop")

b.shot("先迈一小步", "第四步 · 一小步", view=(2650, 9480, 0.85))
T("④ 先迈一小步", 2650, 9180, 72, BLUE, k0=0, k1=0.9, sfx="pop")
L(stick(2350, 9730, 0.8, "hold"), 1, 1.5, BLACK, 9, sfx="wood_high")
L(join(rect(2520, 9580, 130, 110, 8), P((2455, 9550), (2585, 9550))), 2, 2.4, BLACK, 8, sfx="pop")
T("帮邻居收快递", 2900, 9370, 56, k0=3, k1=3.7, sfx="pop")

b.shot("跟门卫打声招呼", "第四步 · 一小步", view=(2650, 9530, 0.85))
L(rect(2840, 9580, 200, 120, 40), 0, 0.4, BLACK, 8, sfx="wood_high")
T("早！", 2840, 9580, 66, RED, k0=0.4, k1=0.8)
L(join(stick(3150, 9850, 0.6), face(3150, 9850, 0.6, "smile")), 1, 1.5, BLUE, 8, sfx="pop")
L(check(2850, 9770, 40), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("一样一样来", "具体做法", view=(1800, 9000, 0.355))
for n, (x, y) in enumerate(SOL):
    L(check(x + 500, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 else "pop")

b.shot("孤单，身体记着", "一句话", view=(1800, 5800, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 10300, 0.8))
T("你一个人住多久了？", 1800, 10210, 80, RED, k0=0.5, k1=1.8)
T("下一讲：越孤单，为什么越不想见人？", 1800, 10370, 48, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "health", "孤独伤身", "一个人住久了，为什么总睡不好？", ACC, b.shots,
                 [f"{BOOK}第六章 · 孤独的磨损（转述）", "中译本：《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009"],
                 "一个人住久了|为什么总【睡不好】", 2,
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
