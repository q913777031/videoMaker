"""09 换个尺度（白板手绘版）：为什么去趟山里，烦心事就小了？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
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
SQUARE_SHOT = 4

b = Board(size=(3600, 17400))


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


# ---------------------------------------------------------------- 开局：一次排名焦虑一周（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("我排在了后半截", "灵魂拷问", (950, 850, 0.85))
T("绩效排名", 1050, 480, 70, k0=0, sfx="pop")
L(join(*[rect(1050, 620 + n * 96, 420, 80, 10) for n in range(5)]), 1, 1.8, BLACK, 8, sfx="wood_high")
for n in range(5):
    T(f"{n + 1}", 900, 620 + n * 96, 46, k0=1.8 + n * 0.15, k1=2.0 + n * 0.15)
L(stick(520, 1150, 0.75, "hold"), 2.5, 2.95, BLUE, 9)
L(rect(1050, 908, 460, 104, 14), 3, 3.5, RED, 9, sfx="rim")
T("你", 1150, 908, 56, RED, k0=3.5, k1=4.0)
L(face(520, 1150, 0.75, "sad"), 4, 4.2, BLUE, 8, sfx="wood_high")
T("倒数第二", 1050, 1130, 60, RED, k0=5, k1=5.8, sfx="pop")

DAYS = "一二三四五六日"
scene("焦虑了一整周", "灵魂拷问", (2650, 850, 0.85))
T("这一周", 2650, 480, 70, k0=0, sfx="pop")
L(join(*[rect(2650 + (n - 3) * 150, 720, 130, 130, 10) for n in range(7)]), 1, 1.6, BLACK, 8, sfx="wood_high")
for n, d in enumerate(DAYS):
    T(d, 2650 + (n - 3) * 150, 620, 46, k0=1.3 + n * 0.08, k1=1.5 + n * 0.08)
for n in range(7):
    L(scribble(2650 + (n - 3) * 150, 720, 90, 90, 6), 2 + n * 0.3, 2.2 + n * 0.3, RED, 6,
      sfx="shaker" if n == 0 else None)
L(clock(2450, 1080, 110), 4, 4.4, BLACK, 8, sfx="wood_low")
L(hands_at(2450, 1080, 110, 2, 0), 4.4, 4.6, RED, 9)
T("凌晨还在想", 2850, 1080, 56, RED, k0=5, k1=5.8, sfx="rim")

scene("去趟山里，事就小了？", "灵魂拷问", (1800, 1250, 0.38), flashes=[4])
L(peaks((420, 2150), (720, 1700), (850, 1820), (1050, 1480), (1300, 1850), (1480, 2150)), 0, 0.9, BLACK, 9,
  sfx="wood_low")
L(stick(650, 2150, 0.45, "up"), 1, 1.4, BLUE, 8, sfx="wood_high")
L(desk(2700, 1950, 320), 2, 2.4, BLACK, 9, sfx="wood_high")
L(stick(2400, 2080, 0.65), 2.4, 2.8, BLUE, 9)
L(rect(2950, 1680, 200, 130, 10), 2.8, 3.0, BLACK, 8)
L(face(2400, 2080, 0.65, "smile"), 3, 3.2, BLUE, 8, sfx="ding")
T("第7名", 2950, 1680, 46, RED, k0=3.2, k1=3.7)
T("？", 1800, 1300, 600, RED, k0=4, k1=4.6, sfx="kick")
T("排名没变，事怎么小了", 1800, 230, 110, k0=5, k1=5.9, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

scene("书里说，换个尺度", "身份的焦虑", (1450, 2750, 0.66))
L(book(950, 2750, 420, 280), 0, 1.0, sfx="wood_low")
T("《身份的焦虑》", 1900, 2600, 76, GREEN, k0=1, k1=2.2, sfx="pop")
T("阿兰 · 德波顿", 1900, 2710, 56, k0=3, k1=3.9, sfx="pop")
T("换个尺度", 1900, 2870, 110, RED, k0=5, k1=5.7, sfx="ding")

# 第 5 个场景（音乐 drop）：镜头从书猛地拉远到一整座城，工位就在中间那栋楼里
CITY = join(P((300, 6300), (3300, 6300)),
            P((1350, 6300), (1350, 5150), (2250, 5150), (2250, 6300)),
            P((1350, 5700), (2250, 5700)), P((1350, 5430), (2250, 5430)),
            *[rect(1450 + n * 140, 5300, 70, 70, 6) for n in range(6)],
            *[rect(1450 + n * 140, 5570, 70, 70, 6) for n in range(6)])
SIDE_L = join(*[P((x - w / 2, 6300), (x - w / 2, 6300 - h), (x + w / 2, 6300 - h), (x + w / 2, 6300))
                for x, w, h in ((600, 200, 500), (900, 220, 600), (1200, 200, 650))])
SIDE_R = join(*[P((x - w / 2, 6300), (x - w / 2, 6300 - h), (x + w / 2, 6300 - h), (x + w / 2, 6300))
                for x, w, h in ((2400, 200, 700), (2700, 220, 550), (3000, 200, 500))])
j_drop = scene("往后一拉，一整座城", "书中办法 · 拉远看", (1800, 5700, 0.42), shake=[0], flashes=[0])
L(CITY, 0, 0.6, BLACK, 10, sfx="kick")
L(desk(1800, 6050, 300), 0.6, 0.9, BLACK, 9)
L(stick(1560, 6170, 0.65, "hold"), 0.9, 1.2, BLUE, 9)
L(face(1560, 6170, 0.65, "sad"), 1.2, 1.3, BLUE, 8)
L(rect(2080, 5800, 200, 140, 10), 1.3, 1.5, BLACK, 8)
T("第7名", 2080, 5800, 52, RED, k0=2, k1=2.5, sfx="pop")
L(SIDE_L, 3, 3.5, BLACK, 9, sfx="wood_high")
L(SIDE_R, 4, 4.5, BLACK, 9, sfx="wood_high")
T("一整座城", 1800, 6480, 110, k0=5, k1=5.7, sfx="pop")

MOUNT = ((100, 6300), (700, 5300), (1100, 5600), (1800, 3900), (2500, 5500), (2900, 5200), (3500, 6300))
STARS = [[(350, 4000, 60), (1000, 3900, 45), (1250, 4450, 50)], [(2350, 3950, 55), (3350, 3950, 60), (2550, 4550, 45)],
         [(500, 4700, 40), (1500, 3750, 40), (3300, 4800, 45), (2450, 3650, 50)]]
WIDE = (1800, 5200, 0.3)
scene("再远，山和满天星", "书中办法 · 拉远看", WIDE)
L(peaks(*MOUNT), 0, 0.9, BLACK, 12, sfx="wood_low")
T("一座山", 2950, 4400, 150, k0=1, k1=1.6, sfx="pop")
for n, grp in enumerate(STARS):
    L(join(*[star(sx, sy, sr * 1.5) for sx, sy, sr in grp]), 2 + n, 2.4 + n, BLACK, 9, sfx="pop")
L(moon(3100, 3750, 110), 4.4, 4.8, BLACK, 10)
T("星空", 620, 4350, 160, k0=5, k1=5.5, sfx="wood_high")

scene("尺度一大，事就小了", "书中观点 · 一张图", WIDE, shake=[3])
L(circle(1830, 6000, 360), 0, 0.6, RED, 14, sfx="wood_high")
T("排名？", 3000, 6700, 200, RED, k0=1, k1=1.6, sfx="pop")
L(arrow((2700, 6620), (2200, 6250), 0.15, 70), 2, 2.4, RED, 12, sfx="wood_high")
T("尺度一大，烦恼就小", 1650, 6720, 140, RED, k0=3, k1=4.2, sfx="kick")
L(underline(1050, 2250, 6830, 20, 60), 5, 5.6, RED, 12, sfx="ding")

TEMPLE = (950, 8100)
scene("古城只剩几根柱子", "书中例子 · 古城", (950, 7880, 0.85))
L(temple(*TEMPLE), 0, 0.9, BLACK, 9, sfx="wood_high")
T("很久以前的大城", 950, 7380, 60, k0=0.9, k1=1.8)
L(stick(778, 8060, 0.42, tie=True), 2, 2.3, BLUE, 7, sfx="pop")
L(crown(778, 7880, 0.6), 2.3, 2.5, RED, 6)
L(stick(1122, 8060, 0.42), 2.5, 2.8, BLACK, 7)
b.erase(J(), 3, 3.6, 950, 7780, 900, 680)
H(3, "shaker")
L(ruins(*TEMPLE), 4, 4.6, BLACK, 9, sfx="wood_high")
L(join(grass(620, 8100), grass(1250, 8100, 3)), 4.6, 4.9, GREEN, 7)
T("只剩几根柱子", 950, 7620, 60, k0=5, k1=5.9, sfx="pop")

scene("到头来，高低都一样", "书中观点 · 终点", (2650, 7880, 0.85))
TALL = ((2200, "tie"), (2380, "crown"), (2560, "plain"), (2740, "hold"))
for n, (x, kind) in enumerate(TALL):
    L(stick(x, 8100, 0.6, "hold" if kind == "hold" else "down", tie=kind == "tie"), n * 0.2, n * 0.2 + 0.3,
      BLACK, 8, sfx="wood_high" if n == 0 else None)
L(crown(2380, 7880, 0.7), 1, 1.2, RED, 7, sfx="pop")
L(hourglass(3060, 7850, 300), 2, 2.6, BLACK, 9, sfx="wood_high")
T("到头来，人人一样", 2650, 8220, 60, k0=3, k1=3.9, sfx="pop")
b.custom(J(), 4, 5.6, shrink_fn("谁高谁低", 2500, 7500, 110, 46, RED), sfx="pop")
H(5, "tom")
L(circle(2500, 7500, 125), 5.6, 6, BLACK, 7)

# ---------------------------------------------------------------- 身边的例子（场景 10–15）
# 两排卡片拉开距离、近景视角略往下取，相邻区块的字不漏进页眉

CARDS = [(950, 10600), (2650, 10600), (950, 12140), (2650, 12140)]
EXC = (1800, 11370)
OVER = (1800, 11300, 0.33)
scene("身边也常碰到", "身边的例子", OVER)
T("身边的例子", 1800, 9700, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 1 + n, 1.45 + n, GREEN, 8, sfx="wood_high" if n % 2 == 0 else "pop")

x, y = CARDS[0]
scene("汇报卡壳，去江边坐坐", "例子 · 汇报", (x, y + 180, 0.85))
T("汇报卡壳", x - 300, y - 310, 56, k0=0, sfx="pop")
L(join(rect(x - 250, y - 120, 340, 220, 12), P((x - 380, y - 40), (x - 300, y - 90), (x - 230, y - 60),
                                              (x - 120, y - 170))), 1, 1.5, BLACK, 8, sfx="wood_high")
L(stick(x - 470, y + 330, 0.6, "point", tie=True), 1.5, 1.9, BLUE, 8)
L(bubble(x - 230, y + 130, 200, 90, -1), 2, 2.3, BLACK, 7, sfx="pop")
T("呃…", x - 230, y + 130, 50, k0=2.3, k1=2.7)
L(face(x - 470, y + 330, 0.6, "sad"), 2.7, 2.9, BLUE, 7)
T("下班去江边", x + 300, y - 310, 56, k0=3, k1=3.9, sfx="pop")
L(waves(x + 50, x + 560, y + 150), 4, 4.5, BLUE, 8, sfx="wood_high")
L(stick(x + 120, y + 60, 0.5), 4.5, 4.9, BLUE, 8)
T("江水照样流", x + 380, y - 130, 54, k0=5, k1=5.9, sfx="pop")

x, y = CARDS[1]
scene("同学晒新房，我看老碗", "例子 · 新房", (x, y + 180, 0.85))
T("朋友圈", x - 300, y - 310, 56, k0=0, sfx="pop")
L(phone(x - 300, y + 30, 320, 520), 1, 1.6, BLACK, 8, sfx="wood_high")
L(house(x - 300, y + 70, 170), 2, 2.4, BLACK, 7, sfx="pop")
T("心里一酸", x - 300, y + 340, 50, RED, k0=3, k1=3.7, sfx="rim")
T("博物馆", x + 300, y - 310, 56, k0=4, k1=4.5, sfx="pop")
L(vase(x + 300, y + 170, 0.9), 4.5, 5.0, BLACK, 8)
L(rect(x + 300, y + 30, 360, 380, 8), 5, 5.3, BLUE, 6, sfx="wood_high")
T("几千年前的碗", x + 300, y + 300, 48, k0=5.3, k1=5.95)

x, y = CARDS[2]
scene("当年的名次，早忘了", "例子 · 家庭", (x, y + 180, 0.85))
T("期中考", x - 300, y - 310, 56, k0=0, sfx="pop")
L(doc(x - 250, y - 20, 240, 300, 3), 1, 1.5, BLACK, 8, sfx="wood_high")
T("第20名", x - 250, y + 80, 50, RED, k0=1.5, k1=2.0)
L(stick(x - 480, y + 340, 0.55), 2, 2.4, BLUE, 8, sfx="pop")
L(face(x - 480, y + 340, 0.55, "sad"), 2.4, 2.6, BLUE, 7)
T("我当年的", x + 300, y - 310, 56, k0=3, k1=3.7, sfx="pop")
L(doc(x + 300, y - 30, 240, 300, 4), 4, 4.5, BLACK, 8, sfx="wood_high")
T("早忘了", x + 300, y + 230, 60, BLUE, k0=5, k1=5.6, sfx="ding")

x, y = CARDS[3]
scene("没升职，爬山往下看", "例子 · 升职", (x, y + 180, 0.85))
T("升职名单", x - 300, y - 310, 56, k0=0, sfx="pop")
L(join(*[rect(x - 300, y - 170 + n * 80, 300, 64, 8) for n in range(3)]), 1, 1.5, BLACK, 7, sfx="wood_high")
T("没有你", x - 300, y + 120, 54, RED, k0=2, k1=2.6, sfx="rim")
L(stick(x - 300, y + 380, 0.5), 2.6, 3.0, BLUE, 8)
T("周末爬山", x + 300, y - 310, 56, k0=3, k1=3.7, sfx="pop")
L(peaks((x + 30, y + 330), (x + 300, y - 60), (x + 570, y + 330), snow=False), 4, 4.6, BLACK, 9, sfx="wood_high")
L(stick(x + 300, y - 60, 0.35, "up"), 4.6, 4.9, BLUE, 7)
L(join(*[rect(x + 120 + n * 50, y + 300, 26, 40, 3) for n in range(8)]), 5, 5.3, BLACK, 5, sfx="pop")
T("楼像火柴盒", x + 300, y + 380, 46, k0=5.3, k1=5.95)

scene("都是把镜头拉远", "身边的例子", OVER, shake=[4])
for n, (x, y) in enumerate(CARDS):
    T("变小", x, y - 300, 100, RED, k0=n, k1=n + 0.5, sfx="pop")
T("拉远", EXC[0], EXC[1], 150, RED, k0=4, k1=4.5, sfx="kick")
for n, (x, y) in enumerate(CARDS):
    dx, dy = (x - EXC[0]) * 0.18, (y - EXC[1]) * 0.4
    L(arrow((EXC[0] + dx * 0.9, EXC[1] + dy * 0.45), (EXC[0] + dx * 1.35, EXC[1] + dy * 0.95), 0.0, 36),
      5 + n * 0.2, 5.25 + n * 0.2, RED, 9, sfx="wood_high" if n == 0 else None)

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 13700), (2650, 13700), (950, 15240), (2650, 15240)]

x, y = SOL[0]
scene("周末去看大东西", "第一步 · 看大的", (x, y + 180, 0.85))
L(rect(x, y, 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("① 周末去看大东西", x, y - 300, 70, BLUE, k0=1, k1=1.9, sfx="pop")
L(peaks((x - 520, y + 30), (x - 380, y - 150), (x - 300, y - 80), (x - 200, y - 190), (x - 80, y + 30), snow=False),
  2, 2.4, BLACK, 8, sfx="wood_high")
L(waves(x - 50, x + 230, y - 70, 3, 50), 2.4, 2.8, BLUE, 7)
L(join(star(x + 380, y - 120, 50), star(x + 490, y - 30, 35), moon(x + 520, y - 190, 45)), 3, 3.4, BLACK, 7,
  sfx="pop")
L(phone(x - 470, y + 240, 70, 120), 3.5, 3.9, BLACK, 8)
L(cross(x - 470, y + 240, 60), 4, 4.3, RED, 9, sfx="rim")
T("安静看半小时", x - 70, y + 360, 52, RED, k0=5, k1=5.9, sfx="pop")

x, y = SOL[1]
scene("十年后还记得吗？", "第二步 · 问一句", (x, y + 180, 0.85))
L(rect(x, y, 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("② 问自己一句", x, y - 300, 72, BLUE, k0=1, k1=1.9, sfx="pop")
L(stick(x - 380, y + 330, 0.6), 2, 2.4, BLUE, 8, sfx="wood_high")
L(bubble(x + 100, y - 100, 600, 150, -1), 2.4, 2.8, BLACK, 8)
T("十年后还记得吗？", x + 100, y - 100, 56, k0=3, k1=3.9, sfx="pop")
T("大概记不住", x + 60, y + 230, 54, k0=4, k1=4.8, sfx="pop")
L(face(x - 380, y + 330, 0.6, "smile"), 4.8, 5.0, BLUE, 7)
T("放下", x + 380, y + 230, 60, GREEN, k0=5, k1=5.4, sfx="ding")
L(check(x + 500, y + 225, 36), 5.4, 5.7, GREEN, 9)

x, y = SOL[2]
scene("写下来，跟大照片比", "第三步 · 比一比", (x, y + 180, 0.85))
L(rect(x, y, 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("③ 写下来比一比", x, y - 300, 72, BLUE, k0=1, k1=1.9, sfx="pop")
L(rect(x - 330, y + 30, 300, 200, 8), 2, 2.3, BLACK, 8, sfx="wood_high")
T("绩效排名", x - 330, y + 30, 54, RED, k0=2.3, k1=2.9)
L(frame(x + 250, y + 20, 520, 420), 3, 3.5, BLACK, 8, sfx="wood_high")
L(peaks((x + 30, y + 190), (x + 170, y - 40), (x + 250, y + 30), (x + 360, y - 100), (x + 470, y + 190),
        snow=False), 3.5, 3.8, BLACK, 7)
L(join(star(x + 120, y - 120, 30), star(x + 430, y - 140, 26)), 3.8, 3.95, BLACK, 6)
T("一比，就小了", x - 50, y + 330, 58, RED, k0=4, k1=4.9, sfx="pop")
H(5, "ding")

x, y = SOL[3]
scene("听老人讲当年的愁", "第四步 · 听老人讲", (x, y + 180, 0.85))
L(rect(x, y, 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("④ 听老人讲当年", x, y - 300, 72, BLUE, k0=1, k1=1.9, sfx="pop")
L(stick(x - 400, y + 340, 0.6, "hold"), 2, 2.3, BLACK, 8, sfx="wood_high")
L(P((x - 330, y + 210), (x - 310, y + 340)), 2.3, 2.4, BLACK, 8)
L(bubble(x + 120, y - 90, 580, 150, -1), 2.4, 2.8, BLACK, 8)
T("当年也愁得睡不着", x + 120, y - 90, 50, k0=3, k1=3.9, sfx="pop")
L(face(x - 400, y + 340, 0.6, "smile"), 4, 4.2, BLACK, 7, sfx="ding")
T("愁的事会变小", x + 120, y + 200, 54, GREEN, k0=5, k1=5.9, sfx="pop")

# ---------------------------------------------------------------- 收尾（场景 20–21）

scene("往大处看，心就宽", "一句话", (1800, 6100, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 16900, 0.8))
T("你去哪儿，心里最敞亮？", 1800, 16810, 76, RED, k0=1, k1=2.4)
T("下一讲：不想卷了，能换个活法吗？", 1800, 16970, 50, k0=3, k1=4.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(3, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "scale", "换个尺度", "为什么去趟山里，烦心事就小了？", ACC, b.shots,
                 [f"{BOOK}第二部分“解决方法”第四章“基督教”（转述，本讲用世俗说法“换个尺度”）",
                  "中译本：陈广兴、南治国译，上海译文出版社"],
                 "去趟山里|烦心事就【小了】", 5,
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
