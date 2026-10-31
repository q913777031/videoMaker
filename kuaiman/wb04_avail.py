"""04 可得性（白板手绘版）：组里每个人，都觉得自己干得最多？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（B 一个故事贯穿）：小王、小李、小张三人的一次项目复盘，从周五复盘会一路讲到下周一——
周五 17:00 复盘会，三人各写自己的功劳占比（40% / 35% / 45%）→ 慢慢拿计算器一加 → drop：加起来 120%，红圈爆开，
三人愣住 → 亮书：书里的夫妻各估自己做了多少家务，加起来也超过 100% → 快快从脑袋抽屉里抽卡片：“我”的一大摞，
别人的就两张 → 书中观点：想得起来，就当作多 → 书中实验：列 6 件 / 列 12 件“我果断的事”，列 12 件的越列越心虚 →
故事续：小王坐地铁觉得亏，领导看绩效只记得最近一周 → 三个做法（先打个折 / 每天记一行 / 先问对方那块花了多久）→
拉远看全板 → 评论区互动。
书中观点为转述（丹尼尔·卡尼曼《思考，快与慢》第 12 章“科学地利用可得性启发法”（The Science of Availability）；
中译本胡晓姣、李爱民、何梦莹译，中信出版社 2012）；故事、人物与百分比为示意，做法据书中思路整理。
"""

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, desk,
                               doc, face, hands_at, join, rect, stick, underline)
from adler import kit as K

from .common import BOOK, episode, kuai, man

ACC = "#8A5BB0"
SQUARE_SHOT = 3                 # 场景 4（drop）：三人功劳加起来 120%，红圈爆开，慢慢拿着计算器

b = Board(size=(3600, 9800))
XL, XR = 900, 2700              # 左右两列的中心


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    return p


def rays_around(x, y, rx, ry, d0=30, d1=90, degs=(-55, -25, 0, 25, 55, 125, 155, 180, 205, 235)) -> skia.Path:
    """椭圆外一圈爆点短线（正上、正下留空，不压到上下的字）。"""
    import math
    parts = []
    for deg in degs:
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)
        parts.append(P((x + (rx + d0) * ca, y + (ry + d0) * sa), (x + (rx + d1) * ca, y + (ry + d1 * 0.7) * sa)))
    return join(*parts)


def burst_fn(x, y, r, color=RED):
    """爆开：一圈红环从小到大扩散并淡出（动态项，结束后不留痕）。"""
    def fn(c, k, t):
        if k >= 1:
            return None
        c.drawCircle(x, y, r * (0.5 + 1.1 * k), K.paint(color, 0.85 * (1 - k), 16))
        c.drawCircle(x, y, r * (0.4 + 0.9 * k), K.paint(color, 0.18 * (1 - k)))
        return None

    return fn


def highlight_fn(x, y, w, h, color="#F2C94C", alpha=0.5):
    """荧光笔从左往右涂一条：(x, y) 为中心。"""
    def fn(c, k, t):
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w * k, h), K.paint(color, alpha))
        return (x - w / 2 + w * k, y) if k < 1 else None

    return fn


def calculator(x, y, w=100, h=150) -> skia.Path:
    parts = [rect(x, y, w, h, 12), rect(x, y - h * 0.28, w * 0.72, h * 0.22, 4)]
    for r in range(2):
        for cc in range(3):
            parts.append(circle(x - w * 0.25 + cc * w * 0.25, y + h * 0.05 + r * h * 0.22, 6))
    return join(*parts)


def table(x, y, w=1000) -> skia.Path:
    """会议长桌：(x, y) 为桌面中点。"""
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 40, y), (x - w / 2 + 40, y + 120)),
                P((x + w / 2 - 40, y), (x + w / 2 - 40, y + 120)))


def cabinet(x, y, w=320, h=200) -> skia.Path:
    """记忆抽屉柜：两层抽屉，下层拉开一截。"""
    return join(rect(x, y, w, h, 10), P((x - w / 2, y), (x + w / 2, y)),
                P((x - 25, y - h / 4), (x + 25, y - h / 4)),
                P((x - w / 2 - 30, y + 20), (x - w / 2 - 30, y + h / 2 + 30), (x + w / 2 - 30, y + h / 2 + 30),
                  (x + w / 2 - 30, y + h / 2)),
                P((x - 55, y + h / 2 + 5), (x - 5, y + h / 2 + 5)))


def dots(pts) -> skia.Path:
    return join(*[circle(px, py, r) for px, py, r in pts])


def stack(x, y, n=7, w=210, h=120, d=14) -> skia.Path:
    """一摞卡片：最上面一张完整，下面每张露出一条边。"""
    parts = [rect(x, y, w, h, 10)]
    for i in range(1, n + 1):
        y0, y1 = y + h / 2 + (i - 1) * d, y + h / 2 + i * d
        parts.append(P((x - w / 2 + 4, y0), (x - w / 2 + 4, y1), (x + w / 2 - 4, y1), (x + w / 2 - 4, y0)))
    return join(*parts)


def cloud(x, y, w=220, h=90) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - w / 2, y + h / 2)
    p.quadTo(x - w / 2 - h * 0.5, y, x - w / 4, y - h * 0.3)
    p.quadTo(x - w / 6, y - h * 1.0, x + w / 8, y - h * 0.45)
    p.quadTo(x + w / 2.5, y - h * 0.9, x + w * 0.45, y - h * 0.1)
    p.quadTo(x + w / 2 + h * 0.4, y + h / 2, x + w / 2, y + h / 2)
    p.close()
    return p


def rain(x, y, w=200, n=5, l=40) -> skia.Path:
    return join(*[P((x - w / 2 + i * w / (n - 1), y), (x - w / 2 + i * w / (n - 1) - 12, y + l)) for i in range(n)])


def subway(x, y, w=1100, h=440) -> skia.Path:
    """地铁车厢（侧视）：两扇窗、一扇门、车轮。(x, y) 为车厢中心。"""
    return join(rect(x, y, w, h, 40), rect(x + w * 0.2, y - h * 0.2, 150, 110, 10), rect(x + w * 0.38, y - h * 0.2, 110, 110, 10),
                P((x - w * 0.02, y + h / 2), (x - w * 0.02, y - h * 0.38), (x + w * 0.1, y - h * 0.38), (x + w * 0.1, y + h / 2)),
                circle(x - w * 0.3, y + h / 2 + 30, 30), circle(x + w * 0.3, y + h / 2 + 30, 30))


def calendar(x, y, w=600, h=520, rows=4, cols=7) -> skia.Path:
    top = y - h / 2 + 90
    parts = [rect(x, y, w, h, 16), P((x - w / 2, top), (x + w / 2, top)),
             P((x - w / 4, y - h / 2 - 25), (x - w / 4, y - h / 2 + 25)), P((x + w / 4, y - h / 2 - 25), (x + w / 4, y - h / 2 + 25))]
    rh = (h - 90) / rows
    for r in range(1, rows):
        parts.append(P((x - w / 2, top + r * rh), (x + w / 2, top + r * rh)))
    for cc in range(1, cols):
        xx = x - w / 2 + cc * w / cols
        parts.append(P((xx, top), (xx, y + h / 2)))
    return join(*parts)


def notebook(x, y, w=620, h=560) -> skia.Path:
    parts = [rect(x, y, w, h, 14)]
    for i in range(6):
        parts.append(circle(x - w / 2, y - h / 2 + 60 + i * (h - 120) / 5, 16))
    return join(*parts)


def cup(x, y, s=1.0) -> skia.Path:
    """奶茶杯 + 吸管：(x, y) 为杯身中心。"""
    return join(P((x - 38 * s, y - 55 * s), (x - 28 * s, y + 55 * s), (x + 28 * s, y + 55 * s), (x + 38 * s, y - 55 * s), close=True),
                P((x - 44 * s, y - 55 * s), (x + 44 * s, y - 55 * s)), P((x + 8 * s, y - 55 * s), (x + 25 * s, y - 110 * s)),
                circle(x - 12 * s, y + 30 * s, 6 * s), circle(x + 10 * s, y + 18 * s, 6 * s))


def nod(x, y, s=1.0) -> skia.Path:
    """点头的动作线：头顶两侧两道小弧线。(x, y) 为小人脚底。"""
    hy = y - 290 * s
    a = skia.Path()
    a.addArc(skia.Rect.MakeXYWH(x - 75 * s, hy - 60 * s, 150 * s, 120 * s), 200, 40)
    c = skia.Path()
    c.addArc(skia.Rect.MakeXYWH(x - 75 * s, hy - 60 * s, 150 * s, 120 * s), 300, 40)
    return join(a, c)


# ---------------------------------------------------------------- 开局：周五复盘（场景 1–4）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("周五，项目复盘", "故事 · 周五复盘会", (XL, 900, 0.85), bars=2)
L(table(XL, 1130, 1000), 0, 0.9, sfx="wood_high")
L(join(stick(600, 1280, 0.65, "down"), stick(900, 1280, 0.65, "down", hair=True), stick(1200, 1280, 0.65, "down", tie=True)),
  1, 1.9, BLACK, 9, sfx="pop")
L(join(face(600, 1280, 0.65, "smile"), face(900, 1280, 0.65, "smile"), face(1200, 1280, 0.65, "smile")), 1.9, 2.4, BLACK, 7)
L(clock(1250, 520, 85), 3, 3.7, BLACK, 8, sfx="wood_low")
L(hands_at(1250, 520, 85, 5, 0), 3.7, 4.0, RED, 8)
T("17:00", 1250, 665, 50, RED, k0=4, k1=4.8)
T("周五 复盘会", 680, 530, 76, k0=5, k1=6, sfx="pop")

# 三人各举一张纸：小王 40%、小李 35%、小张 45%（示意数字）
PEOPLE = [("小王", 2300, "我 40%", False, False), ("小李", 2700, "我 35%", True, False), ("小张", 3100, "我 45%", False, True)]
scene("各写各的功劳", "故事 · 各报功劳", (XR, 900, 0.85))
for n, (name, x, pct, hair, tie) in enumerate(PEOPLE):
    L(join(stick(x, 1250, 0.65, "up", hair=hair, tie=tie), rect(x, 955, 300, 130, 10)), 2 * n, 2 * n + 0.9, BLACK, 9,
      sfx="wood_high")
    T(pct, x, 958, 64, RED, k0=2 * n + 1, k1=2 * n + 1.9, sfx="pop")
T("小王    小李    小张", XR, 1335, 52, k0=6, k1=7.5, sfx="pop")

SUM_X = 2600
scene("加一加", "故事 · 加一加", (XR, 2250, 0.85))
T("40", SUM_X + 30, 1910, 96, k0=0, k1=0.8, sfx="pop")
T("+35", SUM_X, 2040, 96, k0=1, k1=1.8, sfx="pop")
T("+45", SUM_X, 2170, 96, k0=2, k1=2.8, sfx="pop")
L(P((SUM_X - 150, 2240), (SUM_X + 150, 2240)), 3, 3.6, BLACK, 10, sfx="wood_high")
MAN = (3080, 2480, 0.7)
L(man(*MAN, arms="hold"), 4, 4.9, BLUE, 9, sfx="wood_low")
L(face(*MAN, "flat"), 4.9, 5.0, BLUE, 7)
L(calculator(3200, 2265), 5, 5.8, BLUE, 8, sfx="pop")
L(bubble(3060, 1950, 260, 120, -1), 6, 6.5, BLUE, 8, sfx="pop")
T("我来按", 3060, 1950, 54, BLUE, k0=6.5, k1=7.5)

# drop：加起来 120%，红圈爆开，三人愣住
TOT = (SUM_X - 40, 2410)
scene("加起来，超了", "故事 · 加起来", (XR, 2480, 0.75), shake=[0], flashes=[0])
T("= 120%", TOT[0], TOT[1], 150, RED, k0=0, k1=1.2, sfx="kick")
L(join(oval(TOT[0], TOT[1], 340, 130), rays_around(TOT[0], TOT[1], 340, 130)), 1, 1.9, RED, 10, sfx="rim")
b.custom(J(), 1, 1.9, burst_fn(TOT[0], TOT[1], 330))
T("多出 20%", TOT[0], 2640, 60, RED, k0=2, k1=3, sfx="ding")
TRIO = [(2250, False, False), (2560, True, False), (2870, False, True)]
L(join(*[stick(x, 3000, 0.5, "shrug", hair=h, tie=t) for x, h, t in TRIO]), 3, 3.9, BLACK, 8, sfx="wood_high")
L(join(*[face(x, 3000, 0.5, "frown") for x, _, _ in TRIO]), 3.9, 4.3, BLACK, 7)
for n, (x, _, _) in enumerate(TRIO):
    T("?", x, 2770, 72, k0=5 + n, k1=5.8 + n, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 5–8）

scene("书里的夫妻也这样", "思考，快与慢 · 书中观点", (XL, 2480, 0.85))
L(book(620, 2330, 400, 270), 0, 0.9, BLACK, 9, sfx="wood_low")
T("思考，快与慢", 620, 2100, 64, GREEN, k0=1, k1=2.5, sfx="pop")
L(kuai(1170, 2560, 0.6), 3, 3.7, RED, 9, sfx="wood_high")
L(face(1170, 2560, 0.6, "smile"), 3.7, 3.85, RED, 7)
L(man(1420, 2560, 0.6), 3.85, 4.6, BLUE, 9)
L(face(1420, 2560, 0.6, "flat"), 4.6, 4.75, BLUE, 7)
L(join(stick(470, 2950, 0.5, "down"), stick(720, 2950, 0.5, "down", hair=True)), 5, 5.8, BLACK, 8, sfx="pop")
T("各估家务", 595, 2635, 54, k0=5.8, k1=6.8)
T("加起来 > 100%", 1170, 2870, 64, RED, k0=7, k1=8, sfx="ding")

scene("自己干的，记得清", "书中观点 · 脑袋里的抽屉", (XL, 3800, 0.85))
KK = (520, 4250, 0.9)
L(kuai(*KK, arms="point"), 0, 0.9, RED, 10, sfx="wood_high")
L(face(*KK, "smile"), 0.9, 1.0, RED, 8)
L(join(dots([(640, 3830, 10), (720, 3730, 14), (800, 3630, 18)]), cabinet(1040, 3470)), 1, 1.9, BLACK, 8, sfx="wood_low")
L(stack(850, 3940, 7), 2, 3.6, BLACK, 8, sfx="shaker")
T("我", 850, 3945, 72, RED, k0=4, k1=4.8, sfx="pop")
L(stack(1280, 4010, 1), 5, 5.6, BLACK, 8, sfx="pop")
T("别人", 1280, 4015, 56, k0=5.6, k1=6.4)
T("一大摞", 850, 4200, 56, RED, k0=6, k1=6.8, sfx="pop")
T("就两张", 1280, 4200, 56, k0=7, k1=7.8, sfx="rim")

scene("好想起，就当多", "思考，快与慢 · 书中观点", (XR, 3800, 0.85))
T("想得起来 = 多", XR, 3400, 96, k0=0, k1=2, sfx="pop")
L(underline(2400, 3000, 3485), 2, 2.8, RED, 9, sfx="ding")
L(arrow((XR, 3530), (XR, 3790), 0.12, 40), 3, 3.8, BLACK, 9, sfx="wood_high")
L(rect(XR, 3900, 480, 140, 20), 4, 4.8, RED, 9, sfx="wood_low")
T("我干得多", XR, 3900, 80, RED, k0=5, k1=6, sfx="pop")
L(kuai(2250, 4300, 0.6, "up"), 6, 6.8, RED, 9, sfx="pop")
L(face(2250, 4300, 0.6, "smile"), 6.8, 6.95, RED, 7)
L(man(3150, 4300, 0.6, "shrug"), 7, 7.8, BLUE, 9, sfx="rim")
L(face(3150, 4300, 0.6, "flat"), 7.8, 7.95, BLUE, 7)

DA, DB = (2350, 5110), (2950, 5220)     # 列 6 件 / 列 12 件 两张清单
scene("列得越难，越不信", "思考，快与慢 · 书中实验", (XR, 5200, 0.85))
T("我很果断的事", XR, 4760, 64, k0=0, k1=1.5, sfx="pop")
T("列 6 件", DA[0], 4880, 54, k0=1.5, k1=2)
L(doc(*DA, 240, 300, 6), 2, 2.8, BLACK, 8, sfx="wood_high")
T("列 12 件", DB[0], 4880, 54, RED, k0=3, k1=3.8, sfx="pop")
L(rect(*DB, 240, 520, 6), 4, 4.3, BLACK, 8, sfx="wood_low")
for i in range(12):                     # 越往下写得越慢
    yy = DB[1] - 260 + 45 + i * 38
    a = 4.3 + sum(0.04 + 0.015 * n for n in range(i))
    L(P((DB[0] - 90, yy), (DB[0] + 90 - (i % 3) * 25, yy)), a, a + 0.04 + 0.015 * i, BLACK, 6)
L(join(stick(2350, 5560, 0.45, "up"), stick(3220, 5600, 0.45, "shrug")), 6, 6.6, BLACK, 8, sfx="rim")
L(join(face(2350, 5560, 0.45, "smile"), face(3220, 5600, 0.45, "frown")), 6.6, 6.9, BLACK, 7)
T("越列越心虚", XR, 5690, 60, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 故事续：下班路上、月底绩效（场景 9–10）

scene("小王觉得亏了", "故事 · 下班路上", (XL, 5200, 0.85))
L(subway(XL, 5420), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(650, 5600, 0.6, "down"), 1, 1.8, BLACK, 9, sfx="pop")
L(face(650, 5600, 0.6, "frown"), 1.8, 1.95, BLACK, 7)
T("小王", 800, 5520, 48, k0=2, k1=2.8)
L(cloud(650, 5290, 200, 80), 3, 3.8, BLUE, 8, sfx="wood_low")
L(rain(650, 5345, 150, 4, 30), 4, 4.6, BLUE, 6, sfx="shaker")
L(bubble(950, 4900, 520, 130, -1), 5, 5.6, BLACK, 8, sfx="pop")
T("没人看见我加班", 950, 4900, 54, k0=5.6, k1=7.4)

CAL = (1050, 6450, 600, 520)
scene("绩效只记得最近", "故事 · 月底绩效", (XL, 6500, 0.85))
L(calendar(*CAL), 0, 0.9, BLACK, 8, sfx="wood_high")
T("这个月", CAL[0], 6110, 60, k0=1, k1=1.8, sfx="pop")
L(stick(480, 6800, 0.65, "point", tie=True), 2, 2.8, BLACK, 9, sfx="pop")
L(face(480, 6800, 0.65, "smile"), 2.8, 2.95, BLACK, 7)
ROW_H = (CAL[3] - 90) / 4
b.custom(J(), 3, 3.8, highlight_fn(CAL[0], CAL[1] + CAL[3] / 2 - ROW_H / 2, CAL[2] - 16, ROW_H - 14), sfx="ding")
L(bubble(500, 6300, 320, 120, -1), 5, 5.5, BLACK, 8, sfx="pop")
T("最近不错", 500, 6300, 54, k0=5.5, k1=6.5)
T("前三周呢？", CAL[0], 6800, 56, RED, k0=7, k1=8, sfx="rim")

# ---------------------------------------------------------------- 三个做法（场景 11–13）

PAPER = (2500, 6450)
scene("人人都觉得自己多", "做法① · 先打个折", (XR, 6500, 0.85))
T("① 先打个折", XR, 6100, 76, BLUE, k0=0, k1=1.5, sfx="pop")
L(rect(*PAPER, 380, 220, 12), 2, 2.8, BLACK, 9, sfx="wood_high")
T("我 40%", *PAPER, 72, k0=3, k1=4, sfx="pop")
L(P((PAPER[0] - 20, PAPER[1] + 8), (PAPER[0] + 130, PAPER[1] - 12)), 4, 4.6, RED, 12, sfx="rim")
T("差不多", PAPER[0], 6625, 64, GREEN, k0=5, k1=5.8, sfx="ding")
T("小王", 3050, 6870, 48, k0=6, k1=6.8, sfx="pop")
L(stick(3050, 6800, 0.7, "down"), 7, 7.8, BLACK, 9, sfx="wood_low")
L(face(3050, 6800, 0.7, "smile"), 7.8, 7.95, BLACK, 7)

NB = (2600, 7820)
scene("每天记一行", "做法② · 记一行", (XR, 7800, 0.85))
T("② 记一行", XR, 7400, 76, BLUE, k0=0, k1=1.25, sfx="pop")
L(notebook(*NB), 2, 2.9, BLACK, 9, sfx="wood_high")
for n, line in enumerate(("周一 改方案", "周二 对接口", "周三 帮小李测")):
    T(line, NB[0] + 20, 7660 + n * 130, 56, k0=3 + n, k1=3.9 + n, sfx="pop")
L(stick(3150, 8150, 0.65, "hold"), 6, 6.8, BLACK, 9, sfx="wood_low")
L(face(3150, 8150, 0.65, "smile"), 6.8, 6.95, BLACK, 7)
L(check(NB[0] + 280, 7915, 30), 7, 7.5, GREEN, 9, sfx="ding")

scene("先问问别人那块", "做法③ · 先问对方", (XL, 7800, 0.85))
T("③ 先问对方", XL, 7400, 76, BLUE, k0=0, k1=1.25, sfx="pop")
L(stick(550, 8150, 0.7, "hold"), 1, 1.8, BLACK, 9, sfx="wood_high")
L(face(550, 8150, 0.7, "smile"), 1.8, 1.95, BLACK, 7)
T("小王", 550, 8225, 48, k0=2, k1=2.8)
L(cup(680, 7985, 0.9), 3, 3.7, ACC, 8, sfx="pop")
L(stick(1250, 8150, 0.7, "down", hair=True), 4, 4.8, BLACK, 9, sfx="wood_high")
L(face(1250, 8150, 0.7, "smile"), 4.8, 4.95, BLACK, 7)
T("小李", 1250, 8225, 48, k0=5, k1=5.6)
L(bubble(880, 7650, 520, 130, -1), 6, 6.4, BLACK, 8, sfx="pop")
T("你那块花了多久？", 880, 7650, 50, k0=6.4, k1=8)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FULL = (1800, 4900, 0.12)
COMMENT = (1800, 9200, 0.8)
scene("你们组超了吗", "评论区见", FULL, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
L(rect(1800, 9130, 1120, 380, 30), 4, 4.9, BLACK, 7, sfx="wood_high")
L(kuai(1450, 9700, 0.5, "up"), 5, 5.4, RED, 8, sfx="pop")
L(man(2150, 9700, 0.5), 5.4, 5.8, BLUE, 8)
L(nod(2150, 9700, 0.5), 5.8, 6.0, BLUE, 6)
T("你们组加起来超过一百吗？", 1800, 9050, 76, RED, k0=6, k1=8.75, sfx="pop")
T("下一讲：细节越多，为什么越容易信错？", 1800, 9220, 46, k0=9, k1=13.5, sfx="wood_high")
L(underline(1400, 1800, 9275, 10, 30), 14, 14.6, BLACK, 6, sfx="shaker")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "avail", "可得性", "组里每个人，都觉得自己干得最多？", ACC, b.shots,
                 [f"{BOOK}第12章 科学地利用可得性启发法（The Science of Availability）（转述）",
                  "中译本：胡晓姣、李爱民、何梦莹译，中信出版社 2012"],
                 "每个人都觉得|自己干得【最多】", SQUARE_SHOT,
                 ["书中观点均为转述：人常用“想起来容不容易”来估计一件事有多常见、有多少（可得性启发法）；"
                  "夫妻各自估计自己承担的家务比例，加起来超过 100%，团队成员也常觉得自己干得比别人多，"
                  "知道每个人都会这样想，有助于少起争执；Schwarz 等人的实验里，要求列出 12 件自己果断的事的人越列越难，"
                  "反而觉得自己没那么果断（列 6 件 / 列 12 件为书中实验条件）。见第 12 章“科学地利用可得性启发法”。",
                  "“想得起来 = 多”、脑袋里的抽屉与卡片为对书中观点的通俗化示意；“绩效只记得最近一周”为据书中思路"
                  "（最近发生的事更容易想起来）设计的示意场景。",
                  "小王、小李、小张三人的复盘故事、周五 17:00、40% / 35% / 45% / 120%、地铁、月历、奶茶均为示意，"
                  "不是数据，不指向任何具体公司或个人。",
                  "三个做法（先给自己的估计打个折；每天记一行自己做了什么；先问对方那块花了多久）为据书中思路整理的建议。"],
                 tags="#团队合作 #职场")
    return b.attach(ep)
