"""08 找替代品（白板手绘版）：越孤单，为什么越爱跟猫说话？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
叙事：切身场景开局（到家先跟猫唠一晚上、给扫地机器人起名字、综艺开着当背景音、关了电视屋里一下静了）→
书中观点（亮书；孤单时心里空出一块，人会找替代品；研究：越孤单的人越容易把宠物当人看；对着剧里人物投入感情也一样；
替代品能缓一缓，填不满；画成“孤单 → 替代品 → 缓一缓”，最后连到人）→ 身边的例子（工位午饭对着剧吃、睡前跟音箱道晚安、
爸妈给狗起名“老三”、周末开着直播听人聊天；每样都能缓一缓，心里还缺个人）→ 具体做法（先当个过渡 / 借它连到人：
遛狗认识邻居、追剧拉个群 / 跟猫说的话挑一句发给朋友 / 每周见个人）→ 评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, 2008；
中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009）；例子与做法为现实场景示意与据书中思路整理的建议。
语气温和：养宠物、追剧本身没问题，本讲只讲它们能做什么、做不到什么。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               desk, face, hands_at, join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#C2703D"
SQUARE_SHOT = 5

b = Board(size=(3600, 10100))


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

def cat(x, y, s=1.0) -> skia.Path:
    """坐着的猫（正面）：(x, y) 为底边中点。"""
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - 75 * s, y - 170 * s, 150 * s, 170 * s))
    hx, hy = x, y - 205 * s
    p.addCircle(hx, hy, 58 * s)
    for d in (-1, 1):
        p.moveTo(hx + d * 50 * s, hy - 28 * s)
        p.lineTo(hx + d * 44 * s, hy - 88 * s)
        p.lineTo(hx + d * 14 * s, hy - 56 * s)
        p.addCircle(hx + d * 20 * s, hy - 6 * s, 5 * s)
        for k in (-1, 1):
            p.moveTo(hx + d * 28 * s, hy + 16 * s)
            p.lineTo(hx + d * 78 * s, hy + (16 + k * 12) * s)
    p.moveTo(hx - 8 * s, hy + 14 * s)
    p.lineTo(hx + 8 * s, hy + 14 * s)
    p.moveTo(x + 70 * s, y - 25 * s)
    p.quadTo(x + 175 * s, y - 25 * s, x + 145 * s, y - 130 * s)
    return p


def dog(x, y, s=1.0, flip=False) -> skia.Path:
    """站着的狗（侧面，默认朝右）：(x, y) 为地面中点。"""
    d = -1 if flip else 1

    def q(px, py):
        return x + d * px * s, y + py * s

    parts = [P(q(-90, -150), q(70, -150), q(70, -85), q(-90, -85), close=True)]
    for lx in (-75, -45, 40, 60):
        parts.append(P(q(lx, -85), q(lx, 0)))
    hx, hy = q(105, -185)
    parts.append(circle(hx, hy, 45 * s))
    parts.append(P(q(85, -222), q(62, -160), q(95, -172)))
    parts.append(circle(*q(118, -195), 4 * s))
    parts.append(P(q(-90, -140), q(-140, -205)))
    return join(*parts)


def vacuum(x, y, s=1.0) -> skia.Path:
    """扫地机器人（斜俯视）：(x, y) 为机身中心。"""
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - 150 * s, y - 55 * s, 300 * s, 110 * s))
    p.addOval(skia.Rect.MakeXYWH(x - 45 * s, y - 30 * s, 90 * s, 34 * s))
    p.moveTo(x - 150 * s, y)
    p.lineTo(x - 150 * s, y + 30 * s)
    p.quadTo(x, y + 105 * s, x + 150 * s, y + 30 * s)
    p.lineTo(x + 150 * s, y)
    return p


def tv(x, y, w=460, h=300) -> skia.Path:
    return join(rect(x, y, w, h, 18), rect(x, y, w - 50, h - 50, 10),
                P((x - 60, y + h / 2), (x - 95, y + h / 2 + 60)), P((x + 60, y + h / 2), (x + 95, y + h / 2 + 60)),
                P((x - 70, y - h / 2 - 90), (x, y - h / 2), (x + 70, y - h / 2 - 90)))


def sofa(x, y, w=440) -> skia.Path:
    """沙发（正面）：(x, y) 为坐垫中点。"""
    return join(rect(x, y - 110, w - 80, 150, 24), rect(x, y, w - 80, 80, 16), rect(x - w / 2 + 25, y - 30, 70, 170, 24),
                rect(x + w / 2 - 25, y - 30, 70, 170, 24), P((x - w / 2 + 40, y + 55), (x - w / 2 + 40, y + 100)),
                P((x + w / 2 - 40, y + 55), (x + w / 2 - 40, y + 100)))


def speaker(x, y) -> skia.Path:
    """智能音箱：(x, y) 为中心。"""
    parts = [rect(x, y, 120, 190, 40), circle(x, y - 60, 12)]
    for i in range(3):
        parts.append(P((x - 40, y + i * 34), (x + 40, y + i * 34)))
    return join(*parts)


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12), P((x - 12, y + h / 2 - 16), (x + 12, y + h / 2 - 16)))


def moon(x, y, r=80) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def bowl(x, y, s=1.0) -> skia.Path:
    """一碗饭 + 筷子：(x, y) 为碗口中点。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - 80 * s, y - 70 * s, 160 * s, 140 * s), 0, 180)
    p.moveTo(x - 80 * s, y)
    p.lineTo(x + 80 * s, y)
    p.moveTo(x + 20 * s, y - 10 * s)
    p.lineTo(x + 110 * s, y - 110 * s)
    p.moveTo(x + 40 * s, y - 5 * s)
    p.lineTo(x + 130 * s, y - 95 * s)
    return p


def waves(x, y, n=3, d=1) -> skia.Path:
    """声波：从 (x, y) 向 d 方向（1 右 / -1 左）的几道弧。"""
    p = skia.Path()
    for i in range(n):
        r = 40 + i * 38
        start = -40 if d > 0 else 140
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), start, 80)
    return p


def calendar(x, y, w=300, h=280) -> skia.Path:
    parts = [rect(x, y, w, h, 16), P((x - w / 2, y - h / 2 + 60), (x + w / 2, y - h / 2 + 60)),
             P((x - w / 4, y - h / 2 - 20), (x - w / 4, y - h / 2 + 25)),
             P((x + w / 4, y - h / 2 - 20), (x + w / 4, y - h / 2 + 25))]
    for i in range(1, 4):
        xx = x - w / 2 + i * w / 4
        parts.append(P((xx, y - h / 2 + 60), (xx, y + h / 2)))
    for i in range(1, 3):
        yy = y - h / 2 + 60 + i * (h - 60) / 3
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
    return join(*parts)


# 心形：参数方程 x = 16 sin³t，y = 13cos t − 5cos 2t − 2cos 3t − cos 4t；t∈[0, π] 为右半，[π, 2π] 为左半
def _heart_pt(t, x, y, s):
    return (x + 16 * math.sin(t) ** 3 * s,
            y - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * s)


def heart_half(x, y, s, right=False, n=60) -> skia.Path:
    """半边心：左半从顶部凹口画到底尖；right=True 为右半。"""
    ts = [math.pi * i / n for i in range(n + 1)] if right else [2 * math.pi - math.pi * i / n for i in range(n + 1)]
    return P(*[_heart_pt(t, x, y, s) for t in ts])


def heart(x, y, s) -> skia.Path:
    return join(heart_half(x, y, s), heart_half(x, y, s, True))


def heart_dashed(x, y, s, n=36) -> skia.Path:
    """右半边心画成虚线（缺的那一块）。"""
    pts = [_heart_pt(math.pi * i / (2 * n), x, y, s) for i in range(2 * n + 1)]
    parts = [P(pts[i], pts[i + 1]) for i in range(0, 2 * n, 2)]
    return join(*parts)


def heart_fill(x, y, s, frac, gap=22) -> skia.Path:
    """右半边心从底尖往上画横向填充线，填到整体高度的 frac。"""
    pts = [_heart_pt(math.pi * i / 400, x, y, s) for i in range(401)]
    top, tip = min(p[1] for p in pts), max(p[1] for p in pts)
    lines = []
    yy = tip - 18
    while yy > tip - (tip - top) * frac:
        xs = [pts[i][0] + (pts[i + 1][0] - pts[i][0]) * (yy - pts[i][1]) / (pts[i + 1][1] - pts[i][1])
              for i in range(400) if (pts[i][1] - yy) * (pts[i + 1][1] - yy) < 0]
        if xs and max(xs) - x > 30:
            lines.append(P((x + 12, yy), (max(xs) - 14, yy)))
        yy -= gap
    return join(*lines)


# ---------------------------------------------------------------- 开局：屋里挺热闹（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("到家先跟猫唠一晚", "灵魂拷问", (950, 850, 0.85))
L(stick(650, 1250, 0.95, "hold"), 0, 0.6, sfx="wood_high")
L(face(650, 1250, 0.95, "smile"), 0.6, 0.75)
L(cat(1200, 1250, 1.0), 1, 1.8, BLACK, 9, sfx="pop")
L(bubble(700, 720, 440, 130), 2, 2.4, BLUE, 8, sfx="pop")
T("老板又改需求", 700, 720, 56, k0=2.4, k1=3.5)
L(clock(1260, 560, 105), 4, 4.5, sfx="wood_high")
L(hands_at(1260, 560, 105, 11, 0), 4.5, 4.7, RED, 11)
T("23:00", 1260, 730, 52, RED, k0=4.7, k1=4.95)
T("喵", 1360, 900, 70, RED, k0=5, k1=5.4, sfx="pop")

scene("给扫地机起名字", "灵魂拷问", (2650, 850, 0.85))
L(vacuum(2450, 1170, 1.2), 0, 0.8, BLACK, 9, sfx="wood_high")
L(rect(2450, 940, 220, 100, 20), 1, 1.3, BLUE, 7, sfx="pop")
T("小圆", 2450, 940, 60, BLUE, k0=1.3, k1=1.8)
L(stick(2950, 1250, 0.9, "hold"), 2, 2.6, sfx="wood_high")
L(face(2950, 1250, 0.9, "smile"), 2.6, 2.75)
L(bubble(2950, 690, 400, 130), 3, 3.3, BLUE, 8, sfx="pop")
T("辛苦了", 2950, 690, 56, k0=3.3, k1=3.9)

scene("电视一关，屋里好静", "灵魂拷问", (1800, 2100, 0.7), flashes=[3])
L(tv(1300, 1760, 440, 280), 0, 0.7, BLACK, 10, sfx="wood_high")
T("哈哈哈", 1300, 1760, 76, RED, k0=1, k1=1.5, sfx="pop")
L(cross(1300, 1760, 140), 2, 2.3, RED, 14, sfx="rim")
T("？", 1800, 1800, 260, RED, k0=3, k1=3.6, sfx="kick")
T("越孤单，越爱跟猫聊", 1800, 1470, 100, k0=4, k1=5, sfx="pop")
L(stick(2200, 2000, 0.9), 5, 5.4, sfx="wood_low")
L(face(2200, 2000, 0.9, "sad"), 5.4, 5.5)
T("好静", 2410, 1700, 90, BLUE, k0=5.5, k1=5.9)

# ---------------------------------------------------------------- 书中观点（场景 4–9）

HX, HY, HS = 1380, 2960, 11          # 心形中心与缩放

scene("书里说心里会空一块", "孤独是可耻的", (1050, 2950, 0.85))
L(book(750, 2950, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 750, 2710, 72, GREEN, k0=1.0, k1=2.0, sfx="pop")
T("卡乔波 · 帕特里克", 750, 3180, 46, k0=2.0, k1=2.9, sfx="pop")
L(heart_half(HX, HY, HS), 3, 3.7, RED, 10, sfx="wood_high")
L(heart_dashed(HX, HY, HS), 4, 4.5, RED, 7, sfx="pop")
T("缺一块", HX, 2740, 56, k0=5, k1=5.5, sfx="pop")

scene("就找个替代品", "书中观点 · 替代品", (1050, 3150, 0.85), shake=[0], flashes=[0])
T("替代品", 1050, 3400, 160, RED, k0=0, k1=0.6, sfx="kick")
L(arrow((1300, 3330), (1375, 3175), 0.05, 40), 2, 2.4, RED, 9, sfx="wood_high")
L(underline(810, 1290, 3490), 4, 4.4, RED, 8, sfx="tom")

scene("越孤单，越把猫当人", "书中观点 · 研究", (2650, 2950, 0.85))
T("书中研究", 2650, 2480, 70, BLUE, k0=0, k1=0.7, sfx="pop")
T("Epley、卡乔波等 2008", 2650, 2575, 46, k0=0.7, k1=0.95)
L(stick(2200, 3300, 0.75, "hold"), 1, 1.5, sfx="wood_high")
L(face(2200, 3300, 0.75, "flat"), 1.5, 1.65)
L(cat(2400, 3300, 0.6), 2, 2.6, BLACK, 8, sfx="pop")
L(bubble(2410, 2950, 250, 110), 3, 3.3, BLUE, 7, sfx="pop")
T("它懂我", 2410, 2950, 50, k0=3.3, k1=3.8)
L(P((2620, 2700), (2620, 3250), (3230, 3250)), 4, 4.5, BLACK, 8, sfx="wood_high")
L(P((2680, 3200), (2860, 3090), (3040, 2920), (3180, 2780)), 5, 5.5, RED, 9, sfx="pop")
T("当人看 ↑", 2790, 2690, 50, RED, k0=5.5, k1=5.95)

scene("追剧也一样", "书中观点 · 剧里的人", (950, 4450, 0.85))
L(tv(800, 4320, 440, 290), 0, 0.8, BLACK, 9, sfx="wood_high")
L(stick(800, 4425, 0.45, "up"), 1, 1.4, BLUE, 7, sfx="pop")
L(heart(1310, 4160, 4), 2, 2.5, RED, 8, sfx="pop")
T("像老朋友", 1310, 4340, 56, RED, k0=3, k1=3.7, sfx="pop")

scene("能缓一缓，填不满", "书中观点 · 填不满", (1050, 3060, 0.85))
L(heart_fill(HX, HY, HS, 0.58, 20), 0, 1.2, BLUE, 7, sfx="shaker")
T("缓一缓", 1150, 3260, 56, BLUE, k0=2, k1=2.5, sfx="pop")
T("？", 1465, 2885, 80, RED, k0=3, k1=3.3, sfx="rim")
T("填不满", 1520, 3260, 56, RED, k0=4, k1=4.5, sfx="pop")

FLOW = [("孤单", 2250), ("替代品", 2650), ("缓一缓", 3050)]
FY = 3620
scene("最后还得连到人", "书中观点 · 连到人", (2650, 3930, 0.85), shake=[4])
for n, (w, x) in enumerate(FLOW):
    L(rect(x, FY, 260, 130, 24), n, n + 0.4, BLUE if n == 2 else BLACK, 8, sfx="pop")
    T(w, x, FY, 56, BLUE if n == 2 else BLACK, k0=n + 0.4, k1=n + 0.8)
    if n:
        L(arrow((x - 400 + 130 + 8, FY), (x - 130 - 8, FY), 0, 30), n + 0.8, n + 1.0, GREEN, 7)
L(arrow((2250, FY + 80), (2470, FY + 460), 0.15, 40), 3, 3.5, RED, 9, sfx="wood_high")
L(join(stick(2560, FY + 760, 0.55), stick(2730, FY + 760, 0.55)), 4, 4.6, RED, 9, sfx="kick")
L(P((2600, FY + 625), (2690, FY + 625)), 4.6, 4.8, RED, 8)
T("能填满的是人", 3050, FY + 600, 60, RED, k0=5, k1=5.9, sfx="pop")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 5400), (2650, 5400), (950, 6350), (2650, 6350)]
scene("身边也常见", "身边的例子", (1800, 5880, 0.355))
T("身边的例子", 1800, 4740, 100, k0=0, k1=0.9, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 1 + n, 1.5 + n, GREEN, 8, sfx="wood_high")

scene("剧里人比同事熟", "例子 · 工位午饭", (950, 5420, 0.85))
L(desk(900, 5470, 540), 0, 0.7, sfx="wood_high")
L(stick(500, 5600, 1.0), 0.7, 0.95)
L(face(500, 5600, 1.0, "flat"), 0.95, 1.0)
L(bowl(740, 5430, 0.75), 1, 1.4, BLACK, 8, sfx="pop")
L(phone(1090, 5400, 80, 130), 1.4, 1.7, BLUE, 8)
T("同事：点个头", 950, 5660, 54, k0=2, k1=3, sfx="pop")
L(heart(1300, 5250, 3), 3, 3.4, RED, 7, sfx="wood_high")
T("剧里的人：最熟", 950, 5760, 54, RED, k0=4, k1=5.2, sfx="pop")

scene("睡前跟音箱道晚安", "例子 · 智能音箱", (2650, 5420, 0.85))
L(speaker(2950, 5450), 0, 0.6, BLACK, 9, sfx="wood_high")
L(stick(2350, 5650, 0.85, "hold"), 1, 1.6, sfx="pop")
L(face(2350, 5650, 0.85, "smile"), 1.6, 1.75)
L(bubble(2350, 5150, 260, 110), 2, 2.3, BLUE, 7, sfx="pop")
T("晚安", 2350, 5150, 56, k0=2.3, k1=2.8)
L(moon(2630, 5080, 65), 3, 3.4, BLACK, 8, sfx="wood_high")
L(bubble(2950, 5180, 340, 110, 1), 4, 4.3, BLACK, 7, sfx="pop")
T("晚安，主人", 2950, 5180, 52, k0=4.3, k1=4.9)
T("然后就静了", 2650, 5760, 56, RED, k0=5, k1=5.9, sfx="rim")

scene("爸妈喊狗叫老三", "例子 · 爸妈家", (950, 6370, 0.85))
L(stick(550, 6650, 0.8, hair=True), 0, 0.5, sfx="wood_high")
L(stick(800, 6650, 0.85), 0.5, 0.9)
L(join(face(550, 6650, 0.8, "smile"), face(800, 6650, 0.85, "smile")), 0.9, 1.0)
L(dog(1170, 6650, 1.0), 1, 1.7, BLACK, 9, sfx="pop")
T("孩子在外地", 950, 6080, 56, k0=2, k1=2.9, sfx="pop")
L(bubble(620, 6210, 360, 110), 3, 3.3, BLUE, 7, sfx="pop")
T("老三，吃饭！", 620, 6210, 52, k0=3.3, k1=4.2)
T("老三", 1290, 6360, 54, RED, k0=5, k1=5.4, sfx="pop")

scene("开着直播听人聊", "例子 · 周末", (2650, 6370, 0.85))
L(phone(2950, 6320, 200, 340), 0, 0.6, BLACK, 9, sfx="wood_high")
L(stick(2950, 6440, 0.4, "up"), 1, 1.4, BLUE, 7, sfx="pop")
T("直播", 2950, 6085, 54, k0=1.4, k1=1.9)
L(stick(2380, 6700, 0.85, "hold"), 2, 2.6, sfx="pop")
L(face(2380, 6700, 0.85, "smile"), 2.6, 2.75)
L(waves(2820, 6380, 3, -1), 3, 3.6, BLUE, 7, sfx="shaker")
T("开一下午", 2420, 6150, 56, RED, k0=4, k1=4.8, sfx="pop")

scene("能缓一缓，还缺个人", "身边的例子", (1800, 5880, 0.355), shake=[4])
for n, (x, y) in enumerate(CARDS):
    L(check(x + 480, y - 330, 55), n, n + 0.3, GREEN, 11, sfx="ding" if n % 2 else "pop")
T("心里还缺个人", 1800, 6980, 150, RED, k0=4, k1=4.9, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 7950), (2650, 7950), (950, 8900), (2650, 8900)]

scene("先当个过渡", "第一步 · 当过渡", (950, 7970, 0.85))
L(rect(950, 7950, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("① 当个过渡", 950, 7650, 76, BLUE, k0=0, k1=0.9, sfx="pop")
L(cat(620, 8060, 0.75), 1, 1.6, BLACK, 8, sfx="wood_high")
L(arrow((800, 7950), (1130, 7950), 0.08, 40), 2, 2.4, GREEN, 8, sfx="pop")
L(stick(1260, 8080, 0.6), 2.4, 2.9, BLUE, 8)
T("今晚：跟猫说", 900, 8185, 52, k0=3, k1=3.9, sfx="pop")
L(check(1110, 8180, 36), 3.9, 4.1, GREEN, 9)
T("明天：找人说一句", 900, 8290, 52, RED, k0=4, k1=5.2, sfx="pop")
L(check(1165, 8285, 36), 5.2, 5.4, GREEN, 9)

scene("遛狗也能认识邻居", "第二步 · 借它连到人", (2650, 7970, 0.85))
L(rect(2650, 7950, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("② 借它连到人", 2650, 7650, 76, BLUE, k0=0, k1=1.0, sfx="pop")
L(stick(2220, 8150, 0.7, "hold"), 1, 1.5, sfx="wood_high")
L(dog(2510, 8150, 0.7), 2, 2.5, BLACK, 8, sfx="pop")
L(P((2297, 8011), (2410, 8068), (2540, 8046)), 2.5, 2.7, BLACK, 6)
L(stick(3080, 8150, 0.7, "hold"), 3, 3.4, BLUE, sfx="wood_high")
L(dog(2860, 8150, 0.7, flip=True), 3.4, 3.9, BLUE, 8)
L(bubble(2980, 7820, 360, 100), 4, 4.3, BLUE, 7, sfx="pop")
T("你家狗几岁？", 2980, 7820, 46, k0=4.3, k1=4.9)
T("追剧：拉个剧友群", 2600, 8300, 54, RED, k0=5, k1=5.9, sfx="pop")

scene("挑一句发给朋友", "第三步 · 说给人听", (950, 8920, 0.85))
L(rect(950, 8900, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("③ 说给人听", 950, 8600, 76, BLUE, k0=0, k1=0.9, sfx="pop")
L(cat(600, 9030, 0.7), 1, 1.6, BLACK, 8, sfx="wood_high")
L(bubble(1000, 8820, 380, 110), 2, 2.3, BLUE, 7, sfx="pop")
T("今天被夸了", 1000, 8820, 52, k0=2.3, k1=3.0)
L(phone(1270, 9110, 120, 200), 3, 3.5, BLACK, 8, sfx="wood_high")
L(arrow((1120, 8890), (1250, 8990), 0.1, 30), 4, 4.3, GREEN, 8, sfx="pop")
T("发给朋友", 930, 9230, 56, RED, k0=5, k1=5.7, sfx="pop")

scene("每周见个人", "第四步 · 约个人", (2650, 8920, 0.85))
L(rect(2650, 8900, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("④ 每周见个人", 2650, 8600, 76, BLUE, k0=0, k1=1.0, sfx="pop")
L(calendar(2400, 8930), 1, 1.8, BLACK, 8, sfx="wood_high")
L(circle(2512, 9033, 32), 2, 2.3, RED, 8, sfx="pop")
T("周六 12:00", 2950, 8830, 60, RED, k0=3, k1=3.8, sfx="pop")
L(join(P((2885, 9150), (3045, 9150)), bowl(2965, 9110, 0.5)), 4, 4.4, BLACK, 8, sfx="pop")
L(join(stick(2830, 9250, 0.6), stick(3100, 9250, 0.6)), 5, 5.6, sfx="wood_high")

scene("先缓一缓，再找人", "一句话", (1800, 5600, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 9750, 0.8))
H(0, "cymbal", 0.5)
T("你给啥起过名字？", 1800, 9660, 80, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：想交朋友，第一步迈哪？", 1800, 9820, 46, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")


def rest(x, y):
    """画完把手挪到画面右下角空白处停着，不挡刚写完的字（只移动手，不画东西）。"""

    def fn(c, k, t):
        return (x, y) if k < 1 else None

    return fn


for j, (cx, cy, z) in enumerate(b.views):
    if z > 0.5:
        b.custom(j, 6, 6.4, rest(cx + 430 / z, cy + 330 / z))


def build():
    ep = episode(8, "pet", "找替代品", "越孤单，为什么越爱跟猫说话？", ACC, b.shots,
                 [f"{BOOK}第一部分相关章节（转述）", "中译本：焦梦津译，中国人民大学出版社 2009",
                  "Epley、Cacioppo 等 2008 年关于孤独与拟人化的研究（书中讨论，转述）"],
                 "越孤单|越爱跟【猫】说话", SQUARE_SHOT,
                 ["书中观点均为转述：人在孤单时会找替代品——把宠物、物件当人看，对着电视剧里的人物投入感情；"
                  "书中提到 Epley、Cacioppo 等人 2008 年的研究：越孤独的人越容易把宠物拟人化。替代品能让人缓一缓，"
                  "填不满对真人联系的需要；孤独感本身是提醒人去修复与别人联系的信号。出处：John T. Cacioppo & "
                  "William Patrick, Loneliness: Human Nature and the Need for Social Connection (W. W. Norton, 2008)，"
                  "中译本《孤独是可耻的》（约翰·卡乔波、威廉·帕特里克著，焦梦津译，中国人民大学出版社 2009）。"
                  "上屏均为转述，不是逐字引文；研究只写了方向，没有引用具体数字。",
                  "到家跟猫唠、给扫地机器人起名、综艺当背景音、工位午饭对着剧吃、睡前跟音箱道晚安、爸妈给狗起名“老三”、"
                  "周末开着直播均为生活场景示意，不指向具体个人或产品；时间、名字均为示意。“孤单 → 替代品 → 缓一缓 → 连到人”"
                  "图为对书中思路的通俗化示意。",
                  "四步做法（先当个过渡、借它连到人、跟猫说的话挑一句发给朋友、每周见个人）为据书中思路整理的建议；"
                  "养宠物、追剧本身没有问题，本讲不作否定。"],
                 tags="#养猫 #独居")
    return b.attach(ep)
