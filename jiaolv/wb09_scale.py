"""09 换个尺度（白板手绘版）：为什么去趟山里，烦心事就小了？

叙事：打工人切身问题开局（绩效排名出来，排在后半截 → 焦虑了一整周 → 周末去了趟山里 → 回来觉得没多大事 →
排名没变，事怎么小了）→ 书中观点（亮书《身份的焦虑》、德波顿；书中办法“换个尺度”：镜头从工位一路拉远到整座城、
山、星空，排名小得看不见；书里讲到古城废墟，当年的高低之争只剩几根柱子；走到最后人人一样，高低之争就显得小了；
画成一张图：尺度一大，烦恼就小）→ 身边的例子（汇报卡壳后去江边坐坐、同学晒新房后在博物馆看见老碗、孩子考第二十名
翻出自己的成绩单、升职名单没有你就爬到山顶往下看）→ 具体做法（周末去看大东西 / 问自己十年后还记得吗 /
把烦恼写纸上和大照片比一比 / 听老人讲当年）→ 评论区互动。
书中观点为转述，出自中译本第二部分“解决方法”第四章“基督教”：书中讲想想死亡、看看古城废墟、想想人人在终点平等，
地位之争就显得渺小，焦虑也跟着变小。本讲用世俗说法“换个尺度”转述这一章的思路，不涉及宗教主张；死亡话题只点到为止。
（Alain de Botton, Status Anxiety, Hamish Hamilton / Pantheon, 2004；中译本《身份的焦虑》，陈广兴、南治国译，
上海译文出版社）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross, desk,
                               doc, face, hands_at, clock, join, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#3E7C8C"
SQUARE_SHOT = 9

b = Board(size=(3600, 12800))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def peaks(*pts, snow=True) -> skia.Path:
    """山：折线轮廓；snow=True 时在最高峰下画一道雪线。"""
    parts = [P(*pts)]
    if snow:
        top = min(pts, key=lambda p: p[1])
        i = pts.index(top)
        (lx, ly), (rx, ry) = pts[i - 1], pts[i + 1]
        f = 0.22
        a = (top[0] + (lx - top[0]) * f, top[1] + (ly - top[1]) * f)
        c = (top[0] + (rx - top[0]) * f, top[1] + (ry - top[1]) * f)
        parts.append(P(a, (top[0] - (top[0] - a[0]) * 0.4, a[1] - (a[1] - top[1]) * 0.15),
                       (top[0], a[1] + (c[1] - top[1]) * 0.1), (top[0] + (c[0] - top[0]) * 0.5, c[1] - 10), c))
    return join(*parts)


def star(x, y, r) -> skia.Path:
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return P(*pts, close=True)


def moon(x, y, r) -> skia.Path:
    """弯月：外弧 + 内弧。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    q = skia.Path()
    q.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.85, 1.7 * r, 1.7 * r), 230, -150)
    return join(p, q)


def waves(x0, x1, y, rows=3, gap=70) -> skia.Path:
    return join(*[underline(x0 + n * 30, x1 - n * 30, y + n * gap, 16, 60) for n in range(rows)])


def house(x, y, w=200) -> skia.Path:
    """小房子：(x, y) 为底边中点。"""
    h = w * 0.7
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 20, y - h), (x, y - h - w * 0.5), (x + w / 2 + 20, y - h)),
                rect(x, y - h * 0.3, w * 0.25, h * 0.6, 4))


def vase(x, y, s=1.0) -> skia.Path:
    """陶碗 / 陶罐：(x, y) 为罐底中点。"""
    side = [(70, 0), (120, -60), (130, -130), (95, -200), (55, -230), (60, -260), (80, -275)]
    left = [(x - dx * s, y + dy * s) for dx, dy in side]
    right = [(x + dx * s, y + dy * s) for dx, dy in side]
    return join(P(*left), P(*right), P(left[0], right[0]), P((x - 115 * s, y - 120 * s), (x + 115 * s, y - 120 * s)),
                P((x - 60 * s, y - 155 * s), (x - 20 * s, y - 130 * s), (x + 20 * s, y - 155 * s),
                  (x + 60 * s, y - 130 * s)))


def temple(x, y, w=760, h=520) -> skia.Path:
    """古城神殿：(x, y) 为台阶底边中点，四根柱子 + 三角屋顶。"""
    parts = [P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 30, y - 40), (x + w / 2 - 30, y - 40)),
             P((x - w / 2 + 30, y), (x - w / 2 + 30, y - 40)), P((x + w / 2 - 30, y), (x + w / 2 - 30, y - 40))]
    top = y - h
    for n in range(4):
        cx = x - w * 0.34 + n * w * 0.68 / 3
        parts.append(P((cx - 30, y - 40), (cx - 30, top + 60)))
        parts.append(P((cx + 30, y - 40), (cx + 30, top + 60)))
    parts.append(P((x - w / 2 + 10, top + 60), (x + w / 2 - 10, top + 60)))
    parts.append(P((x - w / 2 + 10, top + 60), (x, top - 120), (x + w / 2 - 10, top + 60)))
    return join(*parts)


def ruins(x, y, w=760) -> skia.Path:
    """废墟：台阶 + 四根高矮不一的断柱 + 一块倒在地上的石头。"""
    parts = [P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 30, y - 40), (x + w / 2 - 30, y - 40))]
    for n, hh in enumerate((380, 160, 300, 90)):
        cx = x - w * 0.34 + n * w * 0.68 / 3
        tp = y - 40 - hh
        parts.append(P((cx - 30, y - 40), (cx - 30, tp + 12), (cx - 8, tp), (cx + 10, tp + 18), (cx + 30, tp + 4),
                       (cx + 30, y - 40)))
    parts.append(rect(x + w * 0.42, y - 25, 130, 50, 8))
    return join(*parts)


def grass(x, y, n=4) -> skia.Path:
    return join(*[P((x + i * 40 - 20, y), (x + i * 40, y - 45), (x + i * 40 + 10, y)) for i in range(n)])


def crown(x, y, s=1.0) -> skia.Path:
    """小皇冠：(x, y) 为底边中点。"""
    return P((x - 45 * s, y), (x - 45 * s, y - 50 * s), (x - 22 * s, y - 22 * s), (x, y - 60 * s),
             (x + 22 * s, y - 22 * s), (x + 45 * s, y - 50 * s), (x + 45 * s, y), close=True)


def hourglass(x, y, h=260) -> skia.Path:
    w = h * 0.6
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2)), P((x - w / 2, y + h / 2), (x + w / 2, y + h / 2)),
                P((x - w / 2 + 15, y - h / 2), (x - 12, y), (x - w / 2 + 15, y + h / 2)),
                P((x + w / 2 - 15, y - h / 2), (x + 12, y), (x + w / 2 - 15, y + h / 2)),
                P((x - w * 0.25, y + h / 2 - 10), (x, y + h * 0.22), (x + w * 0.25, y + h / 2 - 10)))


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12 if w < 200 else 40), P((x - w * 0.17, y + h / 2 - h * 0.13),
                                                           (x + w * 0.17, y + h / 2 - h * 0.13)))


def frame(x, y, w, h) -> skia.Path:
    return join(rect(x, y, w, h, 6), rect(x, y, w - 40, h - 40, 4))


def shrink_fn(s, x, y, s0, s1, color=BLACK):
    """一段字：前半段逐字写出（大号），后半段缩小到 s1。"""

    def fn(c, k, t):
        if k < 0.4:
            size = s0
            w = K.text_w(s, size, "hand")
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(x - w / 2 - 20, y - size, x - w / 2 + w * k / 0.4 + 4, y + size))
            K.text(c, s, x, y, size, "hand", color)
            c.restore()
            return (x - w / 2 + w * k / 0.4, y)
        f = ease_out(clamp01((k - 0.5) / 0.5))
        K.text(c, s, x, y, s0 + (s1 - s0) * f, "hand", color)
        return None

    return fn


# ---------------------------------------------------------------- 开局：一次排名焦虑一周（镜头 1–6）

b.shot("绩效排名出来了", "灵魂拷问", view=(950, 850, 0.85))
T("绩效排名", 1050, 480, 70, k0=0, sfx="pop")
L(join(*[rect(1050, 620 + n * 96, 420, 80, 10) for n in range(5)]), 1, 1.8, BLACK, 8, sfx="wood_high")
for n in range(5):
    T(f"{n + 1}", 900, 620 + n * 96, 46, k0=1.8 + n * 0.15, k1=2.0 + n * 0.15, sfx="pop" if n == 1 else None)
L(stick(520, 1150, 0.75, "hold"), 3, 3.5, BLUE, 9, sfx="wood_high")

b.shot("我排在后半截", "灵魂拷问", view=(950, 850, 0.85))
L(rect(1050, 908, 460, 104, 14), 0, 0.5, RED, 9, sfx="rim")
T("你", 1150, 908, 56, RED, k0=1, sfx="pop")
L(face(520, 1150, 0.75, "sad"), 2, 2.2, BLUE, 8, sfx="wood_high")
T("倒数第二", 1050, 1130, 60, RED, k0=3, sfx="pop")

DAYS = "一二三四五六日"
b.shot("焦虑了一整周", "灵魂拷问", view=(2650, 850, 0.85))
T("这一周", 2650, 480, 70, k0=0, sfx="pop")
L(join(*[rect(2650 + (n - 3) * 150, 720, 130, 130, 10) for n in range(7)]), 1, 1.6, BLACK, 8, sfx="wood_high")
for n, d in enumerate(DAYS):
    T(d, 2650 + (n - 3) * 150, 620, 46, k0=1.3 + n * 0.08, k1=1.5 + n * 0.08)
for n in range(7):
    L(scribble(2650 + (n - 3) * 150, 720, 90, 90, 6), 2 + n * 0.25, 2.2 + n * 0.25, RED, 6,
      sfx="shaker" if n in (0, 4) else None)
L(clock(2450, 1080, 110), 2.2, 2.6, BLACK, 8)
L(hands_at(2450, 1080, 110, 2, 0), 2.6, 2.8, RED, 9)
T("凌晨还在想", 2850, 1080, 56, RED, k0=3.3, k1=3.9)

b.shot("周末去了趟山里", "灵魂拷问", view=(950, 1800, 0.85))
L(peaks((420, 2150), (720, 1700), (850, 1820), (1050, 1480), (1300, 1850), (1480, 2150)), 0, 0.9, BLACK, 9,
  sfx="wood_low")
L(circle(1350, 1480, 60), 1, 1.4, RED, 8, sfx="pop")
L(stick(650, 2150, 0.45, "up"), 2, 2.4, BLUE, 8, sfx="wood_high")
T("周末 · 山里", 950, 2280, 60, k0=3, sfx="pop")

b.shot("回来就没那么慌", "灵魂拷问", view=(2650, 1800, 0.85))
L(desk(2700, 1950, 320), 0, 0.5, BLACK, 9, sfx="wood_high")
L(stick(2400, 2080, 0.65), 0.5, 0.9, BLUE, 9)
L(rect(2950, 1680, 200, 130, 10), 1, 1.3, BLACK, 8, sfx="pop")
T("第7名", 2950, 1680, 46, RED, k0=1.3)
T("好像也没多大事", 2650, 1430, 60, k0=2, sfx="pop")
L(face(2400, 2080, 0.65, "smile"), 3, 3.2, BLUE, 8, sfx="ding")

b.shot("事没变，怎么小了？", "灵魂拷问", view=(1800, 1350, 0.42), flashes=[0])
T("？", 1800, 1350, 420, RED, k0=0, k1=0.6, sfx="kick")
T("排名没变，事怎么小了", 1800, 2400, 110, k0=1.0, k1=2.4, sfx="pop")
H(3, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "身份的焦虑", view=(1550, 3000, 0.66))
L(book(950, 3000, 420, 280), 0, 1.0, sfx="wood_low")
T("《身份的焦虑》", 950, 2740, 76, GREEN, k0=1.0, sfx="pop")
T("阿兰 · 德波顿", 950, 3240, 60, k0=2.0, sfx="pop")
T("书里的办法", 1950, 2860, 64, k0=2.6, k1=3.0)
T("换个尺度", 1950, 3020, 110, RED, k0=3, k1=3.7, sfx="ding")

DESK = (1800, 6050)
b.shot("先看你的工位", "书中办法 · 换个尺度", view=(1800, 5950, 0.85))
L(desk(1800, 6050, 300), 0, 0.5, BLACK, 9, sfx="wood_high")
L(stick(1560, 6170, 0.65, "hold"), 1, 1.4, BLUE, 9, sfx="pop")
L(face(1560, 6170, 0.65, "sad"), 1.4, 1.5, BLUE, 8)
L(rect(2080, 5800, 200, 140, 10), 2, 2.3, BLACK, 8, sfx="pop")
T("第7名", 2080, 5800, 52, RED, k0=2.3)
L(scribble(1560, 5850, 120, 60, 6), 3, 3.3, RED, 6, sfx="shaker")

# 第 9 镜（音乐 drop）：镜头猛地拉远，工位在一栋大楼里，四周一座城
CITY = join(P((300, 6300), (3300, 6300)),
            P((1350, 6300), (1350, 5150), (2250, 5150), (2250, 6300)),
            P((1350, 5700), (2250, 5700)), P((1350, 5430), (2250, 5430)),
            *[rect(1450 + n * 140, 5300, 70, 70, 6) for n in range(6)],
            *[rect(1450 + n * 140, 5570, 70, 70, 6) for n in range(6)])
SIDE_L = join(*[P((x - w / 2, 6300), (x - w / 2, 6300 - h), (x + w / 2, 6300 - h), (x + w / 2, 6300))
                for x, w, h in ((600, 200, 500), (900, 220, 600), (1200, 200, 650))])
SIDE_R = join(*[P((x - w / 2, 6300), (x - w / 2, 6300 - h), (x + w / 2, 6300 - h), (x + w / 2, 6300))
                for x, w, h in ((2400, 200, 700), (2700, 220, 550), (3000, 200, 500))])
b.shot("镜头往后一拉", "书中办法 · 拉远看", view=(1800, 5700, 0.42), shake=[0], flashes=[0])
L(CITY, 0, 0.6, BLACK, 10, sfx="kick")
L(SIDE_L, 1, 1.5, BLACK, 9, sfx="wood_high")
L(SIDE_R, 2, 2.5, BLACK, 9, sfx="wood_high")
T("一整座城", 1800, 6480, 110, k0=3, sfx="pop")

MOUNT = ((100, 6300), (700, 5300), (1100, 5600), (1800, 3900), (2500, 5500), (2900, 5200), (3500, 6300))
b.shot("再远是一座山", "书中办法 · 拉远看", view=(1800, 5100, 0.3))
L(peaks(*MOUNT), 0, 1.2, BLACK, 12, sfx="wood_low")
H(1, "wood_high")
T("一座山", 2950, 4300, 150, k0=2, sfx="pop")

STARS = [[(350, 4000, 60), (1000, 3700, 45), (1250, 4450, 50)], [(2350, 3750, 55), (3350, 3950, 60), (2550, 4550, 45)],
         [(500, 4700, 40), (1500, 3500, 40), (3300, 4800, 45), (2100, 3450, 50)]]
b.shot("再远是满天星", "书中办法 · 拉远看", view=(1800, 5000, 0.235))
for n, grp in enumerate(STARS):
    L(join(*[star(*s) for s in grp]), n, n + 0.4, BLACK, 9, sfx="pop")
L(moon(3150, 3400, 110), 3, 3.4, BLACK, 10, sfx="wood_high")
T("星空", 650, 3500, 160, k0=3.3, k1=3.8)

b.shot("排名在哪呢", "书中办法 · 拉远看", view=(1800, 5000, 0.235))
L(circle(1830, 6000, 360), 0, 0.6, RED, 14, sfx="wood_high")
T("排名？", 3000, 6650, 150, RED, k0=1, sfx="pop")
L(arrow((2780, 6600), (2200, 6200), 0.15, 70), 2, 2.4, RED, 12, sfx="wood_high")
H(3, "ding")

TEMPLE = (950, 7600)
b.shot("书里讲到古城", "书中例子 · 古城", view=(950, 7300, 0.85))
L(temple(*TEMPLE), 0, 0.9, BLACK, 9, sfx="wood_high")
T("很久以前的大城", 950, 6930, 60, k0=1, sfx="pop")
L(stick(700, 7560, 0.32, tie=True), 2, 2.3, BLUE, 7, sfx="pop")
L(crown(700, 7380, 0.6), 2.3, 2.5, RED, 6)
L(stick(1200, 7560, 0.32), 3, 3.3, BLACK, 7, sfx="pop")
T("我大！", 760, 7280, 46, RED, k0=3.3)

b.shot("如今剩几根柱子", "书中例子 · 古城", view=(950, 7300, 0.85))
b.erase(J(), 0, 0.6, 950, 7300, 900, 640)
H(0, "shaker")
L(ruins(*TEMPLE), 1, 1.7, BLACK, 9, sfx="wood_high")
L(join(grass(620, 7600), grass(1250, 7600, 3)), 2, 2.3, GREEN, 7, sfx="pop")
T("只剩几根柱子", 950, 7120, 60, k0=3, sfx="pop")

b.shot("到最后人人一样", "书中观点 · 终点", view=(2650, 7300, 0.85))
TALL = ((2200, "tie"), (2380, "crown"), (2560, "plain"), (2740, "hold"))
for n, (x, kind) in enumerate(TALL):
    L(stick(x, 7600, 0.6, "hold" if kind == "hold" else "down", tie=kind == "tie"), n * 0.25, n * 0.25 + 0.45,
      BLACK, 8, sfx="wood_high" if n == 0 else None)
L(crown(2380, 7380, 0.7), 1, 1.2, RED, 7, sfx="pop")
L(hourglass(3100, 7350, 300), 2, 2.6, BLACK, 9, sfx="wood_high")
T("到头来，人人一样", 2650, 7720, 60, k0=3, sfx="pop")

b.shot("高低之争变小了", "书中观点 · 地位之争", view=(2650, 7300, 0.85))
b.custom(J(), 0, 2, shrink_fn("谁高谁低", 2500, 7000, 110, 44, RED), sfx="pop")
H(1, "tom")
L(circle(2500, 7000, 70), 2, 2.4, BLACK, 7, sfx="wood_high")
T("这么点儿", 2900, 7000, 56, k0=3, sfx="pop")

b.shot("尺度一大事就小", "书中观点 · 一张图", view=(1800, 5300, 0.3), shake=[0])
T("尺度一大，烦恼就小", 1650, 6720, 140, RED, k0=0, k1=1.2, sfx="kick")
L(underline(1050, 2250, 6830, 20, 60), 2, 2.6, RED, 12, sfx="ding")
H(3, "pop", 0.6)

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 8550), (2650, 8550), (950, 9450), (2650, 9450)]
b.shot("身边也常碰到", "身边的例子", view=(1800, 9000, 0.355))
T("身边的例子", 1800, 7980, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

x, y = CARDS[0]
b.shot("汇报时卡壳了", "例子 · 汇报", view=(x, y, 0.85))
T("汇报卡壳", x - 300, y - 310, 56, k0=0, sfx="pop")
L(rect(x - 250, y - 120, 340, 220, 12), 1, 1.5, BLACK, 8, sfx="wood_high")
L(stick(x - 470, y + 330, 0.6, "point", tie=True), 1.5, 1.9, BLUE, 8)
L(bubble(x - 230, y + 130, 200, 90, -1), 2, 2.3, BLACK, 7, sfx="pop")
T("呃…", x - 230, y + 130, 50, k0=2.3)
L(face(x - 470, y + 330, 0.6, "sad"), 3, 3.2, BLUE, 7, sfx="rim")

b.shot("去江边坐了会儿", "例子 · 汇报", view=(x, y, 0.85))
T("下班去江边", x + 300, y - 310, 56, k0=0, sfx="pop")
L(waves(x + 50, x + 560, y + 150), 1, 1.6, BLUE, 8, sfx="wood_high")
L(stick(x + 120, y + 60, 0.5), 2, 2.4, BLUE, 8, sfx="pop")
T("江水照样流", x + 330, y - 120, 54, k0=3, sfx="pop")

x, y = CARDS[1]
b.shot("同学晒了新房", "例子 · 新房", view=(x, y, 0.85))
T("朋友圈", x - 300, y - 310, 56, k0=0, sfx="pop")
L(phone(x - 300, y + 30, 320, 520), 1, 1.6, BLACK, 8, sfx="wood_high")
L(house(x - 300, y + 70, 170), 2, 2.4, BLACK, 7, sfx="pop")
T("心里一酸", x - 300, y + 340, 50, RED, k0=3, sfx="rim")

b.shot("博物馆看到老碗", "例子 · 新房", view=(x, y, 0.85))
T("博物馆", x + 300, y - 310, 56, k0=0, sfx="pop")
L(vase(x + 300, y + 170, 0.9), 1, 1.6, BLACK, 8, sfx="wood_high")
L(rect(x + 300, y + 30, 360, 380, 8), 2, 2.4, BLUE, 6, sfx="pop")
T("几千年前的碗", x + 300, y + 300, 48, k0=3, sfx="pop")

x, y = CARDS[2]
b.shot("孩子考了第二十", "例子 · 家庭", view=(x, y, 0.85))
T("期中考", x - 300, y - 310, 56, k0=0, sfx="pop")
L(doc(x - 250, y - 20, 240, 300, 3), 1, 1.5, BLACK, 8, sfx="wood_high")
T("第20名", x - 250, y + 80, 50, RED, k0=1.6)
L(stick(x - 480, y + 340, 0.55), 2, 2.4, BLUE, 8, sfx="pop")
L(face(x - 480, y + 340, 0.55, "sad"), 3, 3.2, BLUE, 7, sfx="rim")

b.shot("翻出我的成绩单", "例子 · 家庭", view=(x, y, 0.85))
T("我当年的", x + 300, y - 310, 56, k0=0, sfx="pop")
L(doc(x + 300, y - 30, 240, 300, 4), 1, 1.5, BLACK, 8, sfx="wood_high")
T("早忘了", x + 300, y + 230, 60, BLUE, k0=2, sfx="pop")
L(face(x - 480, y + 340, 0.55, "smile"), 3, 3.2, BLUE, 7, sfx="ding")

x, y = CARDS[3]
b.shot("升职名单没有你", "例子 · 升职", view=(x, y, 0.85))
T("升职名单", x - 300, y - 310, 56, k0=0, sfx="pop")
L(join(*[rect(x - 300, y - 170 + n * 80, 300, 64, 8) for n in range(3)]), 1, 1.5, BLACK, 7, sfx="wood_high")
T("没有你", x - 300, y + 120, 54, RED, k0=2, sfx="rim")
L(stick(x - 300, y + 380, 0.5), 3, 3.4, BLUE, 8, sfx="pop")

b.shot("爬到山顶往下看", "例子 · 升职", view=(x, y, 0.85))
T("周末爬山", x + 300, y - 310, 56, k0=0, sfx="pop")
L(peaks((x + 30, y + 330), (x + 300, y - 140), (x + 570, y + 330), snow=False), 1, 1.6, BLACK, 9, sfx="wood_high")
L(stick(x + 300, y - 140, 0.35, "up"), 2, 2.3, BLUE, 7, sfx="pop")
L(join(*[rect(x + 120 + n * 50, y + 300, 26, 40, 3) for n in range(8)]), 3, 3.3, BLACK, 5, sfx="pop")
T("楼像火柴盒", x + 300, y + 380, 46, k0=3.3)

b.shot("放远看都变小了", "身边的例子", view=(1800, 9000, 0.355))
for n, (x, y) in enumerate(CARDS):
    T("变小", x, y - 300, 100, RED, k0=n, sfx="pop")

b.shot("都是把镜头拉远", "身边的例子", view=(1800, 9000, 0.355), shake=[0])
T("拉远", 1800, 9000, 150, RED, k0=0, k1=0.5, sfx="kick")
for n, (x, y) in enumerate(CARDS):
    dx, dy = (x - 1800) * 0.18, (y - 9000) * 0.5
    L(arrow((1800 + dx * 0.9, 9000 + dy * 0.45), (1800 + dx * 1.35, 9000 + dy * 0.95), 0.0, 36), 1 + n * 0.5,
      1.3 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 10850), (2650, 10850), (950, 11750), (2650, 11750)]
b.shot("下回焦虑这样做", "具体做法", view=(1800, 11300, 0.355))
T("焦虑时，这样做", 1800, 10280, 130, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

x, y = SOL[0]
b.shot("周末去看大东西", "第一步 · 看大的", view=(x, y, 0.85))
T("① 周末去看大东西", x, y - 300, 70, BLUE, k0=0, k1=1.2, sfx="pop")
L(peaks((x - 520, y + 30), (x - 380, y - 150), (x - 300, y - 80), (x - 200, y - 190), (x - 80, y + 30), snow=False),
  1, 1.5, BLACK, 8, sfx="wood_high")
L(waves(x - 50, x + 230, y - 70, 3, 50), 2, 2.4, BLUE, 7, sfx="pop")
L(join(star(x + 380, y - 120, 50), star(x + 490, y - 30, 35), moon(x + 480, y - 160, 50)), 3, 3.4, BLACK, 7,
  sfx="pop")

b.shot("山海星星都行", "第一步 · 看大的", view=(x, y, 0.85))
T("爬山  看海  看星星", x, y + 110, 54, k0=0, sfx="pop")
L(vase(x + 380, y + 280, 0.45), 2, 2.4, BLACK, 7, sfx="wood_high")
T("博物馆也行", x + 30, y + 250, 52, k0=3, sfx="pop")

b.shot("手机先收起来", "第一步 · 看大的", view=(x, y, 0.85))
L(phone(x - 470, y + 240, 70, 120), 0, 0.4, BLACK, 8, sfx="wood_high")
L(cross(x - 470, y + 240, 60), 1, 1.3, RED, 9, sfx="rim")
T("安静看半小时", x - 70, y + 360, 52, RED, k0=2, sfx="pop")
L(underline(x - 240, x + 100, y + 400, 8, 30), 3, 3.4, RED, 6, sfx="ding")

x, y = SOL[1]
b.shot("问自己一句", "第二步 · 问一句", view=(x, y, 0.85))
T("② 问自己一句", x, y - 300, 72, BLUE, k0=0, sfx="pop")
L(stick(x - 380, y + 330, 0.6), 1, 1.4, BLUE, 8, sfx="wood_high")
L(bubble(x + 100, y - 100, 600, 150, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("十年后还记得吗？", x + 100, y - 100, 56, k0=2.4)

b.shot("十年后还记得吗", "第二步 · 问一句", view=(x, y, 0.85))
T("今年排名", x - 80, y + 90, 52, k0=0, sfx="pop")
L(arrow((x + 70, y + 90), (x + 240, y + 90), 0.0, 30), 1, 1.3, BLACK, 8, sfx="wood_high")
T("十年后", x + 360, y + 90, 52, RED, k0=2, sfx="pop")
T("？", x + 470, y + 90, 60, RED, k0=3, sfx="pop")

b.shot("记不住，就放下", "第二步 · 问一句", view=(x, y, 0.85))
T("大概记不住", x + 60, y + 230, 54, k0=0, sfx="pop")
L(face(x - 380, y + 330, 0.6, "smile"), 1, 1.2, BLUE, 7, sfx="wood_high")
T("放下", x + 380, y + 230, 60, GREEN, k0=2, sfx="pop")
L(check(x + 500, y + 225, 36), 3, 3.3, GREEN, 9, sfx="ding")

x, y = SOL[2]
b.shot("把烦恼写纸上", "第三步 · 比一比", view=(x, y, 0.85))
T("③ 写下来比一比", x, y - 300, 72, BLUE, k0=0, sfx="pop")
L(rect(x - 330, y + 30, 300, 200, 8), 1, 1.4, BLACK, 8, sfx="wood_high")
T("绩效排名", x - 330, y + 30, 54, RED, k0=2, sfx="pop")
L(scribble(x - 330, y + 210, 200, 40, 5), 3, 3.3, BLACK, 5, sfx="pop")

b.shot("放在大照片旁", "第三步 · 比一比", view=(x, y, 0.85))
L(frame(x + 250, y + 20, 520, 420), 0, 0.6, BLACK, 8, sfx="wood_high")
L(peaks((x + 30, y + 190), (x + 170, y - 40), (x + 250, y + 30), (x + 360, y - 100), (x + 470, y + 190),
        snow=False), 1, 1.4, BLACK, 7, sfx="pop")
L(join(star(x + 120, y - 120, 30), star(x + 430, y - 140, 26)), 1.4, 1.6, BLACK, 6)
T("一比，就小了", x - 50, y + 330, 58, RED, k0=2, sfx="pop")
H(3, "ding")

x, y = SOL[3]
b.shot("听老人讲当年", "第四步 · 听老人讲", view=(x, y, 0.85))
T("④ 听老人讲当年", x, y - 300, 72, BLUE, k0=0, sfx="pop")
L(stick(x - 400, y + 340, 0.6, "hold"), 1, 1.4, BLACK, 8, sfx="wood_high")
L(P((x - 330, y + 210), (x - 310, y + 340)), 1.4, 1.5, BLACK, 8)
L(bubble(x + 120, y - 90, 580, 150, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("当年也愁得睡不着", x + 120, y - 90, 50, k0=2.4)

b.shot("如今当笑话讲", "第四步 · 听老人讲", view=(x, y, 0.85))
L(face(x - 400, y + 340, 0.6, "smile"), 0, 0.2, BLACK, 7, sfx="pop")
T("哈哈，早过去了", x + 120, y + 110, 56, k0=1, sfx="pop")
L(underline(x - 100, x + 340, y + 160, 10, 30), 2, 2.4, RED, 7, sfx="ding")
T("愁的事会变小", x + 120, y + 290, 54, GREEN, k0=3, sfx="pop")

b.shot("照着试一回", "具体做法", view=(1800, 11300, 0.355))
for n, (x, y) in enumerate(SOL):
    L(check(x + 500, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 else "pop")

b.shot("往大处看，心就宽", "一句话", view=(1800, 6900, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 12500, 0.8))
T("你去哪儿，心里最敞亮？", 1800, 12410, 76, RED, k0=0.5, k1=1.8)
T("下一讲：不想卷了，能换个活法吗？", 1800, 12570, 50, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "scale", "换个尺度", "为什么去趟山里，烦心事就小了？", ACC, b.shots,
                 [f"{BOOK}第二部分“解决方法”第四章“基督教”（转述，本讲用世俗说法“换个尺度”）",
                  "中译本：陈广兴、南治国译，上海译文出版社"],
                 "去趟山里|烦心事就【小了】", 10,
                 ["书中观点均为转述，出自第二部分“解决方法”第四章“基督教”：书中讲想想死亡、看看古城废墟、想想人人在终点平等，"
                  "都会让地位之争显得渺小，身份焦虑也跟着变小。本讲用世俗说法“换个尺度”转述这一章的思路，不涉及宗教主张，"
                  "死亡话题只点到为止（“到头来，人人一样”）。出处：Alain de Botton, Status Anxiety (Hamish Hamilton / "
                  "Pantheon, 2004)，中译本《身份的焦虑》（阿兰·德波顿著，陈广兴、南治国译，上海译文出版社）。上屏均为转述，"
                  "不是逐字引文。",
                  "工位→城市→山→星空的拉远画面、古城神殿变废墟的画面为对书中思路的通俗化示意，不对应书中具体图片或具体古城；"
                  "绩效排名、汇报卡壳、同学晒新房、博物馆老碗、孩子考第二十名、升职名单均为现实场景示意，名次等数字为示意，"
                  "不指向任何具体公司或个人。",
                  "四步做法（周末去看山、海、星空或博物馆里的老物件；问自己“十年后还记得吗”；把烦恼写在纸上和大照片放一起比；"
                  "听老人讲当年的烦恼）为据书中思路整理的建议。"],
                 tags="#旅行 #放松")
    return b.attach(ep)
