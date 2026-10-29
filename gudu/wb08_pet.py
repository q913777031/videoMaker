"""08 找替代品（白板手绘版）：越孤单，为什么越爱跟猫说话？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（2026-10 观众反馈“切太快看不清”后改为慢速讲解版）。
叙事：切身场景开局（到家先跟猫唠一晚上、给扫地机器人起名字）→
书中观点（亮书；孤单时心里空出一块，人会找替代品——宠物、剧里的人；研究：越孤单的人越容易把宠物当人看；
替代品能缓一缓，填不满；画成“孤单 → 替代品 → 缓一缓”，最后连到人）→ 身边的例子（工位午饭对着剧吃、睡前跟音箱道晚安、
爸妈给狗起名“老三”；每样都能缓一缓，心里还缺个人）→ 具体做法（借它连到人：遛狗认识邻居 / 跟猫说的话挑一句发给朋友 /
每周见个人）→ 拉远看全板，评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, 2008；
中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009）；例子与做法为现实场景示意与据书中思路整理的建议。
语气温和：养宠物、追剧本身没问题，本讲只讲它们能做什么、做不到什么。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, circle, desk, face, join, rect, stick

from .common import BOOK, episode

ACC = "#C2703D"
SQUARE_SHOT = 4

b = Board(size=(3600, 10600))


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


# ---------------------------------------------------------------- 开局：屋里挺热闹（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐步画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


scene("到家先跟猫唠一晚", "灵魂拷问", (950, 1000, 0.85), bars=2)
L(stick(650, 1250, 0.95, "hold"), 0, 0.9, sfx="wood_high")
L(face(650, 1250, 0.95, "smile"), 0.9, 1.0)
L(cat(1200, 1250, 1.0), 1, 2.0, BLACK, 9, sfx="pop")
L(bubble(700, 720, 440, 130), 2, 2.8, BLUE, 8, sfx="pop")
T("老板又改需求", 700, 720, 56, k0=2.8, k1=4.3)
T("喵", 1360, 900, 70, RED, k0=5, k1=5.5, sfx="pop")

scene("扫地机也有名字", "灵魂拷问", (2650, 1080, 0.85))
L(vacuum(2450, 1170, 1.2), 0, 1.0, BLACK, 9, sfx="wood_high")
L(rect(2450, 940, 220, 100, 20), 1, 1.6, BLUE, 7, sfx="pop")
T("小圆", 2450, 940, 60, BLUE, k0=1.6, k1=2.2)
L(stick(2950, 1250, 0.9, "hold"), 3, 3.8, sfx="wood_high")
L(face(2950, 1250, 0.9, "smile"), 3.8, 4.0)
L(bubble(2950, 690, 400, 130), 4, 4.7, BLUE, 8, sfx="pop")
T("辛苦了", 2950, 690, 56, k0=4.7, k1=5.5)
T("越孤单，越爱跟它聊？", 2550, 1500, 80, RED, k0=6, k1=8, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 3–7）

HX, HY, HS = 1380, 2960, 11          # 心形中心与缩放

scene("书里说心里会空一块", "孤独是可耻的", (1050, 2950, 0.85))
L(book(750, 2950, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 750, 2710, 72, GREEN, k0=1.0, k1=2.5, sfx="pop")
T("卡乔波 · 帕特里克", 750, 3180, 46, k0=3, k1=4.2, sfx="pop")
L(heart_half(HX, HY, HS), 4.4, 5.3, RED, 10)
L(heart_dashed(HX, HY, HS), 5.5, 6.3, RED, 7, sfx="wood_high")
T("缺一块", HX, 2740, 56, k0=7, k1=7.8, sfx="pop")

scene("空了就找替代品", "书中观点 · 替代品", (1050, 3150, 0.85), shake=[0], flashes=[0])
T("替代品", 1050, 3400, 160, RED, k0=0, k1=0.9, sfx="kick")
L(arrow((1300, 3330), (1375, 3175), 0.05, 40), 2, 2.6, RED, 9, sfx="wood_high")
L(cat(1080, 3100, 0.45), 3, 3.9, BLACK, 7, sfx="pop")
L(tv(610, 3440, 210, 140), 4, 4.9, BLACK, 7, sfx="pop")
L(stick(610, 3440, 0.22, "up"), 5, 5.6, BLUE, 6, sfx="wood_high")

scene("越孤单，越把猫当人", "书中观点 · 研究", (2650, 2950, 0.85))
T("书中研究", 2650, 2480, 70, BLUE, k0=0, k1=1.0, sfx="pop")
T("Epley、卡乔波等 2008", 2650, 2575, 46, k0=1.0, k1=1.9)
L(stick(2200, 3300, 0.75, "hold"), 2, 2.8, sfx="wood_high")
L(face(2200, 3300, 0.75, "flat"), 2.8, 3.0)
L(cat(2400, 3300, 0.6), 3, 3.9, BLACK, 8, sfx="pop")
L(P((2620, 2700), (2620, 3250), (3230, 3250)), 4, 4.8, BLACK, 8, sfx="wood_high")
L(P((2680, 3200), (2860, 3090), (3040, 2920), (3180, 2780)), 5, 5.9, RED, 9, sfx="pop")
T("当人看 ↑", 2790, 2690, 50, RED, k0=6, k1=7, sfx="pop")

scene("能缓一缓，填不满", "书中观点 · 填不满", (1050, 3060, 0.85))
L(heart_fill(HX, HY, HS, 0.58, 20), 0, 2.0, BLUE, 7, sfx="shaker")
T("缓一缓", 1150, 3260, 56, BLUE, k0=3, k1=3.8, sfx="pop")
T("？", 1465, 2885, 80, RED, k0=5, k1=5.5, sfx="rim")
T("填不满", 1520, 3260, 56, RED, k0=6, k1=6.8, sfx="pop")

FLOW = [("孤单", 2250), ("替代品", 2650), ("缓一缓", 3050)]
FY = 3620
scene("最后还得连到人", "书中观点 · 连到人", (2650, 4060, 0.85), shake=[4])
for n, (w, x) in enumerate(FLOW):
    if n:
        L(arrow((x - 400 + 130 + 8, FY), (x - 130 - 8, FY), 0, 30), n, n + 0.25, GREEN, 7, sfx="pop")
    L(rect(x, FY, 260, 130, 24), n + 0.2 if n else 0, n + 0.6, BLUE if n == 2 else BLACK, 8,
      sfx=None if n else "pop")
    T(w, x, FY, 56, BLUE if n == 2 else BLACK, k0=n + 0.6, k1=n + 1.0)
L(arrow((2250, FY + 80), (2470, FY + 460), 0.15, 40), 3, 3.8, RED, 9, sfx="wood_high")
L(join(stick(2560, FY + 760, 0.55), stick(2730, FY + 760, 0.55)), 4, 4.9, RED, 9, sfx="kick")
L(P((2600, FY + 625), (2690, FY + 625)), 4.9, 5.1, RED, 8)
T("能填满的是人", 3050, FY + 600, 60, RED, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

scene("剧里人比同事熟", "例子 · 工位午饭", (950, 5420, 0.85))
L(rect(950, 5400, 1200, 860, 40), 0, 0.6, GREEN, 8)
L(desk(900, 5470, 540), 0, 0.9, sfx="wood_high")
L(stick(500, 5600, 1.0), 1, 1.8, sfx="pop")
L(face(500, 5600, 1.0, "flat"), 1.8, 2.0)
L(phone(1090, 5400, 80, 130), 2, 2.7, BLUE, 8, sfx="wood_high")
L(heart(1300, 5250, 3), 3, 3.8, RED, 7, sfx="pop")
T("同事：点个头", 950, 5660, 54, k0=4, k1=5.5, sfx="pop")
T("剧里的人：最熟", 950, 5760, 54, RED, k0=6, k1=7.75, sfx="pop")

scene("睡前跟音箱道晚安", "例子 · 智能音箱", (2650, 5420, 0.85))
L(rect(2650, 5400, 1200, 860, 40), 0, 0.6, GREEN, 8)
L(speaker(2950, 5450), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(2350, 5650, 0.85, "hold"), 1, 1.8, sfx="pop")
L(face(2350, 5650, 0.85, "smile"), 1.8, 2.0)
L(bubble(2350, 5150, 260, 110), 2, 2.6, BLUE, 7, sfx="pop")
T("晚安", 2350, 5150, 56, k0=2.6, k1=3.2)
L(bubble(2950, 5180, 340, 110, 1), 4, 4.6, BLACK, 7, sfx="pop")
T("晚安，主人", 2950, 5180, 52, k0=4.6, k1=5.8)
T("然后就静了", 2650, 5760, 56, RED, k0=6, k1=7.25, sfx="rim")

scene("能缓一缓，还缺个人", "例子 · 爸妈家", (950, 6600, 0.85), shake=[6])
L(rect(950, 6500, 1200, 860, 40), 0, 0.6, GREEN, 8)
L(stick(550, 6800, 0.8, hair=True), 0, 0.8, sfx="wood_high")
L(stick(800, 6800, 0.85), 1, 1.7, sfx="pop")
L(join(face(550, 6800, 0.8, "smile"), face(800, 6800, 0.85, "smile")), 1.7, 1.9)
L(dog(1170, 6800, 1.0), 2, 2.9, BLACK, 9, sfx="pop")
T("孩子在外地", 950, 6230, 56, k0=3, k1=4.25, sfx="pop")
L(bubble(620, 6360, 360, 110), 4.3, 4.8, BLUE, 7)
T("老三，吃饭！", 620, 6360, 52, k0=4.8, k1=5.9)
T("心里还缺个人", 860, 7040, 96, RED, k0=6, k1=7.5, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

scene("遛狗也能认识邻居", "第一步 · 借它连到人", (950, 7970, 0.85))
L(rect(950, 7950, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("① 借它连到人", 950, 7650, 76, BLUE, k0=0, k1=1.5, sfx="pop")
L(stick(520, 8150, 0.7, "hold"), 2, 2.8, sfx="wood_high")
L(dog(810, 8150, 0.7), 3, 3.8, BLACK, 8, sfx="pop")
L(P((597, 8011), (710, 8068), (840, 8046)), 3.8, 4.0, BLACK, 6)
L(stick(1380, 8150, 0.7, "hold"), 4, 4.8, BLUE, sfx="wood_high")
L(dog(1160, 8150, 0.7, flip=True), 4.8, 5.6, BLUE, 8)
L(bubble(1280, 7820, 360, 100), 6, 6.5, BLUE, 7, sfx="pop")
T("你家狗几岁？", 1280, 7820, 46, k0=6.5, k1=7.8)

scene("挑一句发给朋友", "第二步 · 说给人听", (950, 8920, 0.85))
L(rect(950, 8900, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("② 说给人听", 950, 8600, 76, BLUE, k0=0, k1=1.25, sfx="pop")
L(cat(600, 9030, 0.7), 2, 2.9, BLACK, 8, sfx="wood_high")
L(bubble(1000, 8820, 380, 110), 3, 3.6, BLUE, 7, sfx="pop")
T("今天被夸了", 1000, 8820, 52, k0=3.6, k1=4.85)
L(phone(1270, 9110, 120, 200), 5, 5.8, BLACK, 8, sfx="wood_high")
L(arrow((1120, 8890), (1250, 8990), 0.1, 30), 6, 6.5, GREEN, 8, sfx="pop")
T("发给朋友", 930, 9230, 56, RED, k0=7, k1=8, sfx="pop")

scene("每周见个人", "第三步 · 约个人", (2650, 8920, 0.85))
L(rect(2650, 8900, 1200, 860, 40), 0, 0.6, GREEN, 8)
T("③ 每周见个人", 2650, 8600, 76, BLUE, k0=0, k1=1.5, sfx="pop")
L(calendar(2400, 8930), 2, 2.9, BLACK, 8, sfx="wood_high")
L(circle(2512, 9033, 32), 3, 3.5, RED, 8, sfx="pop")
T("周六 12:00", 2950, 8830, 60, RED, k0=4, k1=5.2, sfx="pop")
L(join(P((2885, 9150), (3045, 9150)), bowl(2965, 9110, 0.5)), 5.5, 6.2, BLACK, 8)
L(join(stick(2830, 9250, 0.6), stick(3100, 9250, 0.6)), 6.5, 7.5)
H(6, "wood_high")
H(7, "pop", 0.6)

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：先拉远看全板，再推到评论区

OVER = (1800, 5650, 0.09)            # 第 0–4 拍：整块白板
scene("评论区聊聊", "评论区见", (1800, 10160, 0.9), bars=4)
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")
T("你给啥起过名字？", 1800, 9860, 80, RED, k0=6, k1=8, sfx="pop")
T("下一讲：想交朋友，第一步迈哪？", 1800, 10020, 46, k0=9, k1=12.5, sfx="wood_high")
b.hit(len(b.shots) - 1, 16, "kick", 0.55, "原曲最后一击")
LAST = len(b.shots) - 1


def _camera(board, T, _base=wb.camera):
    """片尾场景：前 4 拍从上一屏拉远到整块白板，第 4 拍起推到评论区（各 1.1 秒）；其余镜头照引擎默认。"""
    if board is not b or board.ep is None or board.ep.shot_at(T) != LAST:
        return _base(board, T)
    s = board.ep.shots[LAST]
    t4 = board.t_of(LAST, 4)
    if T < t4:
        a, c, k = b.views[LAST - 1], OVER, wb.ease_in_out(wb.clamp01((T - s.t0) / 1.1))
    else:
        a, c, k = OVER, b.views[LAST], wb.ease_in_out(wb.clamp01((T - t4) / 1.1))
    z = math.exp(wb.lerp(math.log(a[2]), math.log(c[2]), k))
    return wb.lerp(a[0], c[0], k), wb.lerp(a[1], c[1], k), z, 0.0, 0.0


wb.camera = _camera


def rest(x, y):
    """画完把手挪到画面右下角空白处停着，不挡刚写完的字（只移动手，不画东西）。"""

    def fn(c, k, t):
        return (x, y) if k < 1 else None

    return fn


for j, (cx, cy, z) in enumerate(b.views):
    if z > 0.5:
        k = 13 if j == LAST else 4 * b.shots[j].bars - (2 if b.shots[j].bars == 2 else 4)
        b.custom(j, k, k + 0.4, rest(cx + 430 / z, cy + 330 / z))


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
                  "到家跟猫唠、给扫地机器人起名、工位午饭对着剧吃、睡前跟音箱道晚安、爸妈给狗起名“老三”"
                  "均为生活场景示意，不指向具体个人或产品；时间、名字均为示意。“孤单 → 替代品 → 缓一缓 → 连到人”"
                  "图为对书中思路的通俗化示意。",
                  "三步做法（借它连到人、跟猫说的话挑一句发给朋友、每周见个人）为据书中思路整理的建议；"
                  "养宠物、追剧本身没有问题，本讲不作否定。"],
                 tags="#养猫 #独居")
    return b.attach(ep)
