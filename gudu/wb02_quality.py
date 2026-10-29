"""02 感觉不看人数（白板手绘版）：群里几百人，为什么还是孤单？

叙事：打工人切身问题开局（工作群几百人、消息刷不停、聚餐坐满一桌、朋友圈点赞很多，回家心里还是空）→ 书中观点
（亮书《孤独是可耻的》、卡乔波；书里先问“人多就不孤单？”——对不上；孤独看的是心里的感觉、跟谁合得来，和人多人少、
独处多久是两回事；研究里孤单的人和不孤单的人，社交时间、长相、聪明程度差别都不大；画成“感觉 / 关系 / 人数 / 时长”
一张图）→ 身边的例子（工位挨着各刷各的手机、周末饭局散场更空、过年一大家子没人问累不累、一个人住每周和闺蜜长聊反倒
不孤单；最后连到“差在有没有深聊”）→ 具体做法（找一两个说得上话的人 / 把一次饭局换成一次深聊 / 点赞换成一句留言 /
定个固定时间打电话）→ 评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, W. W. Norton,
2008；中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009，第一部分）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, bubble, book, check, circle, clock, cross,
                               desk, face, hands_at, join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#C0574A"
SQUARE_SHOT = 10

b = Board(size=(3600, 10300))


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

def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, max(12, w * 0.1)), P((x - w * 0.12, y + h / 2 - h * 0.08), (x + w * 0.12, y + h / 2 - h * 0.08)))


def heart(x, y, r=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r)
    p.cubicTo(x - 1.7 * r, y - 0.1 * r, x - 0.7 * r, y - 1.3 * r, x, y - 0.45 * r)
    p.cubicTo(x + 0.7 * r, y - 1.3 * r, x + 1.7 * r, y - 0.1 * r, x, y + r)
    return p


def bust(x, y, r=40) -> skia.Path:
    """头 + 肩（围坐的人）：(x, y) 为头心。"""
    p = skia.Path()
    p.moveTo(x - 1.7 * r, y + 2.6 * r)
    p.quadTo(x - 1.6 * r, y + 1.2 * r, x, y + 1.15 * r)
    p.quadTo(x + 1.6 * r, y + 1.2 * r, x + 1.7 * r, y + 2.6 * r)
    return join(circle(x, y, r), p)


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def eq(x, y, w=70, neq=False, approx=False) -> skia.Path:
    """等号 / 不等号 / 约等号（画出来，手写字体没有这几个符号）。"""
    parts = []
    for dy in (-16, 16):
        if approx:
            q = skia.Path()
            q.moveTo(x - w / 2, y + dy + 4)
            q.quadTo(x - w / 4, y + dy - 18, x, y + dy)
            q.quadTo(x + w / 4, y + dy + 18, x + w / 2, y + dy - 4)
            parts.append(q)
        else:
            parts.append(P((x - w / 2, y + dy), (x + w / 2, y + dy)))
    if neq:
        parts.append(P((x + w * 0.25, y - 45), (x - w * 0.25, y + 45)))
    return join(*parts)


def cup(x, y, s=1.0) -> skia.Path:
    body = P((x - 40 * s, y - 50 * s), (x - 32 * s, y + 50 * s), (x + 32 * s, y + 50 * s), (x + 40 * s, y - 50 * s),
             close=True)
    handle = skia.Path()
    handle.addArc(skia.Rect.MakeXYWH(x + 20 * s, y - 30 * s, 40 * s, 46 * s), -90, 180)
    st = skia.Path()
    st.moveTo(x, y - 65 * s)
    st.quadTo(x - 15 * s, y - 85 * s, x, y - 100 * s)
    st.quadTo(x + 15 * s, y - 115 * s, x, y - 130 * s)
    return join(body, handle, st)


def calendar(x, y, w=300, h=260) -> skia.Path:
    parts = [rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 60), (x + w / 2, y - h / 2 + 60)),
             P((x - w / 4, y - h / 2 - 25), (x - w / 4, y - h / 2 + 25)),
             P((x + w / 4, y - h / 2 - 25), (x + w / 4, y - h / 2 + 25))]
    for i in range(1, 3):
        yy = y - h / 2 + 60 + i * (h - 60) / 3
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
    for i in range(1, 4):
        xx = x - w / 2 + i * w / 4
        parts.append(P((xx, y - h / 2 + 60), (xx, y + h / 2)))
    return join(*parts)


def waves(x, y, n=3) -> skia.Path:
    """声波（打电话）：向右的三道弧。"""
    p = skia.Path()
    for i in range(n):
        r = 30 + i * 28
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -45, 90)
    return p


def room(x, y, w=600, h=500) -> skia.Path:
    """屋子：墙 + 屋顶 + 一扇窗。(x, y) 为墙体中心。"""
    return join(P((x - w / 2, y - h / 2), (x - w / 2, y + h / 2), (x + w / 2, y + h / 2), (x + w / 2, y - h / 2)),
                P((x - w / 2 - 40, y - h / 2 + 10), (x, y - h / 2 - 150), (x + w / 2 + 40, y - h / 2 + 10)),
                rect(x - w / 4, y - h / 6, 130, 110, 8), P((x - w / 4, y - h / 6 - 55), (x - w / 4, y - h / 6 + 55)))


# ---------------------------------------------------------------- 开局：人很多，心里空（镜头 1–6）

b.shot("工作群几百人", "灵魂拷问", view=(950, 880, 0.85))
L(phone(850, 900, 440, 700), 0, 0.8, BLACK, 10, sfx="wood_high")
T("工作群", 850, 630, 52, k0=1, sfx="pop")
T("498 人", 1330, 640, 70, RED, k0=2, sfx="pop")
L(underline(1220, 1440, 700, 10, 30), 3, 3.4, RED, 7, sfx="wood_high")

b.shot("消息刷个不停", "灵魂拷问", view=(950, 900, 0.85))
for n, (x, y) in enumerate(((750, 770), (950, 900), (750, 1030), (950, 1160))):
    L(bubble(x, y, 200, 70, -1 if x < 850 else 1), n * 0.7, n * 0.7 + 0.35, BLUE if x > 850 else BLACK, 7,
      sfx="pop" if n in (0, 2) else None)
T("99+", 1330, 900, 90, RED, k0=3, sfx="rim")

b.shot("聚餐坐满一桌", "灵魂拷问", view=(2650, 900, 0.85))
L(oval(2650, 1010, 640, 200), 0, 0.7, BLACK, 9, sfx="wood_high")
L(join(*[bust(x, 790, 40) for x in (2450, 2650, 2850)], bust(2250, 1000, 40)), 1, 1.8, BLACK, 8, sfx="pop")
L(bust(3060, 1000, 40), 2, 2.4, BLUE, 8, sfx="pop")
L(face(3060, 1000 + 290 * 0.9, 0.9, "flat"), 2.4, 2.6, BLUE, 6)
T("坐满一桌", 2650, 560, 64, k0=3, sfx="pop")

b.shot("朋友圈点赞很多", "灵魂拷问", view=(950, 1830, 0.85))
L(phone(850, 1850, 440, 700), 0, 0.8, BLACK, 10, sfx="wood_high")
L(join(rect(850, 1700, 340, 240, 10), P((700, 1800), (790, 1700), (850, 1760), (930, 1660), (1000, 1800))), 1, 1.7,
  BLACK, 8, sfx="pop")
L(heart(720, 1960, 34), 2, 2.3, RED, 8, sfx="pop")
T("86", 810, 1975, 60, RED, k0=2.3, k1=2.7)
L(join(P((690, 2060), (1000, 2060)), P((690, 2120), (940, 2120))), 3, 3.4, BLACK, 6, sfx="wood_high")

b.shot("回家心里还是空", "灵魂拷问", view=(2650, 1830, 0.85))
L(room(2600, 1900, 640, 520), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(2700, 2130, 0.7, "down"), 1, 1.5, BLUE, 9, sfx="pop")
L(face(2700, 2130, 0.7, "sad"), 1.5, 1.7, BLUE, 6)
T("空", 3060, 1700, 170, RED, k0=2, k1=2.4, sfx="rim")
T("23:00", 2440, 1490, 52, k0=3, sfx="pop")

b.shot("人不少，咋还孤单？", "灵魂拷问", view=(1800, 1350, 0.4), flashes=[0])
T("？", 1800, 1400, 520, RED, k0=0, k1=0.6, sfx="kick")
T("几百人，还孤单", 1800, 2440, 130, k0=1.0, k1=2.2, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "孤独是可耻的", view=(1050, 3050, 0.9))
L(book(750, 3050, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 750, 2810, 76, GREEN, k0=1.0, sfx="pop")
T("卡乔波", 750, 3280, 52, k0=2.0, sfx="pop")

b.shot("人多就不孤单？", "书中观点", view=(1050, 3300, 0.9))
T("人多", 800, 3500, 90, k0=0, sfx="pop")
L(eq(990, 3490, 70), 1, 1.3, BLACK, 9, sfx="wood_high")
T("不孤单？", 1250, 3500, 90, k0=2, sfx="pop")
H(3, "wood_low", 0.6)

b.shot("书里说，对不上", "书中观点", view=(1050, 3350, 0.9), shake=[0], flashes=[0])
L(join(P((650, 3410), (1460, 3590)), P((1460, 3410), (650, 3590))), 0, 0.35, RED, 16, sfx="kick")
T("对不上", 1050, 3720, 120, RED, k0=1, k1=1.5, sfx="tom")
H(2, "ding")

DX = 2680                         # 示意图中心
b.shot("孤单看心里感觉", "书中观点 · 感觉", view=(DX, 3120, 0.8))
L(heart(DX, 2700, 110), 0, 0.7, RED, 10, sfx="pop")
T("心里的感觉", DX, 2930, 64, RED, k0=1, sfx="pop")
L(underline(2510, 2850, 2985, 10, 30), 2, 2.4, RED, 7, sfx="ding")

b.shot("跟谁合得来", "书中观点 · 关系", view=(DX, 3150, 0.8))
L(join(stick(2420, 3430, 0.65, "point"), stick(2940, 3430, 0.65, "up")), 0, 0.8, BLACK, 9, sfx="wood_high")
L(join(face(2420, 3430, 0.65, "smile"), face(2940, 3430, 0.65, "smile")), 0.8, 1.0, BLACK, 6)
L(join(arrow((2530, 3245), (2830, 3245), -0.1, 34), arrow((2830, 3295), (2530, 3295), -0.1, 34)), 1, 1.6, GREEN, 8,
  sfx="pop")
T("说得上话", DX, 3140, 58, GREEN, k0=1.6)
T("关系好不好", DX, 3510, 56, BLUE, k0=2, sfx="pop")
H(3, "ding", 0.6)

b.shot("人多人少另一回事", "书中观点 · 人数", view=(DX, 3720, 0.8))
L(join(*[circle(2290 + c * 90, 3740 + r * 80, 26) for r in range(2) for c in range(3)]), 0, 0.7, BLACK, 7,
  sfx="pop")
T("人数", 2380, 3920, 56, k0=1, sfx="wood_high")
L(eq(2290, 4020, 60, neq=True), 2, 2.3, RED, 8, sfx="rim")
T("孤单", 2430, 4030, 56, RED, k0=2.3)

b.shot("独处长短也一样", "书中观点 · 独处", view=(DX, 3720, 0.8))
L(clock(2980, 3780, 80), 0, 0.6, BLACK, 9, sfx="wood_high")
L(hands_at(2980, 3780, 80, 9, 0), 0.6, 0.8, RED, 9)
T("独处多久", 2980, 3920, 56, k0=1, sfx="pop")
L(eq(2890, 4020, 60, neq=True), 2, 2.3, RED, 8, sfx="rim")
T("孤单", 3030, 4030, 56, RED, k0=2.3)

b.shot("研究比了两拨人", "书中研究 · 两拨人", view=(1050, 4380, 0.85))
T("孤单的人", 750, 4080, 54, BLUE, k0=0, sfx="pop")
L(join(stick(690, 4330, 0.45), stick(810, 4330, 0.45)), 1, 1.5, BLUE, 8, sfx="wood_high")
T("不孤单的人", 1350, 4080, 54, k0=2, sfx="pop")
L(join(stick(1290, 4330, 0.45), stick(1410, 4330, 0.45)), 3, 3.5, BLACK, 8, sfx="wood_high")

b.shot("社交时间差不多", "书中研究 · 社交时间", view=(1050, 4400, 0.85))
L(rect(750, 4540, 120, 230, 8), 0, 0.5, BLUE, 9, sfx="wood_high")
L(rect(1350, 4545, 120, 220, 8), 1, 1.5, BLACK, 9, sfx="wood_high")
T("社交时间", 1050, 4740, 56, k0=2, sfx="pop")
L(eq(1050, 4540, 90, approx=True), 3, 3.3, RED, 9, sfx="ding")

b.shot("长相聪明也差不多", "书中研究 · 差别不大", view=(1050, 4520, 0.85))
T("长相", 700, 4880, 60, k0=0, sfx="pop")
L(eq(820, 4870, 60, approx=True), 0.5, 0.7, RED, 8)
T("聪明", 1300, 4880, 60, k0=1, sfx="pop")
L(eq(1420, 4870, 60, approx=True), 1.5, 1.7, RED, 8)
H(2, "ding", 0.6)

b.shot("差在关系上", "书中观点 · 一张图", view=(1800, 3720, 0.4))
L(rect(DX, 3360, 780, 600, 30), 0, 0.7, RED, 10, sfx="kick")
L(check(3230, 3590, 50), 1, 1.3, GREEN, 11, sfx="ding")
L(join(cross(2380, 3740, 130), cross(2980, 3780, 130)), 2, 2.5, RED, 9, sfx="rim")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5650), (2650, 5650), (950, 6600), (2650, 6600)]
b.shot("身边也常见", "身边的例子", view=(1800, 6130, 0.355))
T("身边的例子", 1800, 5110, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("同事天天见", "例子 · 工位", view=(950, 5650, 0.85))
L(join(desk(700, 5840, 300), desk(1200, 5840, 300)), 0, 0.8, BLACK, 9, sfx="wood_high")
L(join(stick(560, 5990, 0.7, "hold"), stick(1060, 5990, 0.7, "hold")), 1, 1.6, BLACK, 9, sfx="pop")
T("工位挨着", 950, 5340, 64, k0=2, sfx="pop")

b.shot("午饭各刷手机", "例子 · 工位", view=(950, 5650, 0.85))
hy = 5990 - 290 * 0.7
L(join(phone(560 + 85, hy + 50, 50, 85), phone(1060 + 85, hy + 50, 50, 85)), 0, 0.5, BLUE, 7, sfx="pop")
L(join(face(560, 5990, 0.7, "flat"), face(1060, 5990, 0.7, "flat")), 0.5, 0.7, BLACK, 6)
T("午饭：各刷各的", 950, 5470, 56, RED, k0=1, sfx="pop")
L(underline(800, 1100, 5510, 10, 30), 2, 2.4, RED, 7, sfx="rim")

b.shot("周末饭局到半夜", "例子 · 饭局", view=(2650, 5650, 0.85))
L(oval(2650, 5770, 520, 160), 0, 0.6, BLACK, 9, sfx="wood_high")
L(join(*[bust(x, 5590, 36) for x in (2490, 2650, 2810)], *[bust(x, 5900, 36) for x in (2530, 2770)]), 1, 1.8,
  BLACK, 7, sfx="pop")
T("23:30", 2650, 5360, 64, RED, k0=2, sfx="pop")
T("干杯！", 3060, 5460, 56, k0=3, sfx="pop")

b.shot("散场回家更空", "例子 · 饭局", view=(2650, 5650, 0.85))
b.erase(len(b.shots) - 1, 0, 0.8, 2650, 5780, 900, 540)
H(0, "shaker")
L(stick(2650, 6020, 0.65, "down"), 1, 1.5, BLUE, 9, sfx="pop")
L(face(2650, 6020, 0.65, "sad"), 1.5, 1.7, BLUE, 6)
T("更空了", 2650, 5600, 70, RED, k0=2, sfx="rim")

b.shot("过年一大家子", "例子 · 过年", view=(950, 6600, 0.85))
L(join(*[stick(x, 6820, 0.5) for x in (600, 740, 880)]), 0, 0.7, BLACK, 8, sfx="wood_high")
L(join(*[stick(x, 6820, 0.5) for x in (1020, 1160)]), 1, 1.5, BLACK, 8, sfx="pop")
L(stick(1320, 6820, 0.5), 1.5, 1.8, BLUE, 8)
T("过年：十几口人", 950, 6300, 60, k0=2, sfx="pop")

b.shot("没人问你累不累", "例子 · 过年", view=(950, 6620, 0.85))
T("工资多少？", 680, 6470, 50, k0=0, sfx="pop")
T("啥时结婚？", 1100, 6470, 50, k0=1, sfx="pop")
L(face(1320, 6820, 0.5, "sad"), 2, 2.2, BLUE, 6, sfx="rim")
T("没人问累不累", 950, 6930, 54, RED, k0=3, sfx="pop")

b.shot("她一个人住", "例子 · 独居", view=(2650, 6620, 0.85))
L(room(2480, 6720, 560, 440), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(2560, 6920, 0.6, "hold", hair=True), 1, 1.5, BLUE, 9, sfx="pop")
L(face(2560, 6920, 0.6, "smile"), 1.5, 1.7, BLUE, 6)
T("一个人住", 2650, 6300, 60, k0=2, sfx="pop")

b.shot("每周和闺蜜长聊", "例子 · 独居", view=(2650, 6620, 0.85))
hy2 = 6920 - 290 * 0.6
L(phone(2560 + 70, hy2 + 40, 44, 76), 0, 0.4, BLUE, 7, sfx="pop")
L(waves(2680, hy2 + 30), 0.4, 0.8, BLUE, 6)
T("每周一小时", 3010, 6560, 50, k0=1, sfx="pop")
T("不孤单", 3010, 6860, 64, GREEN, k0=2, sfx="ding")

b.shot("人多的反倒孤单", "身边的例子", view=(1800, 6130, 0.355))
for n, (x, y) in enumerate(CARDS):
    T("人少" if n == 3 else "人多", x + 430, y - 330, 90, GREEN if n == 3 else RED, k0=n, sfx="pop")

b.shot("差在有没有深聊", "身边的例子", view=(1800, 6130, 0.355), shake=[0])
T("差在有没有深聊", 1800, 7180, 120, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 8250), (2650, 8250), (950, 9200), (2650, 9200)]
b.shot("那该怎么办", "具体做法", view=(1800, 8730, 0.355))
T("孤单时这样试", 1800, 7600, 130, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 860, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先找一两个人", "第一步 · 找人", view=(950, 8250, 0.85))
T("① 找一两个人", 950, 7950, 72, BLUE, k0=0, sfx="pop")
L(join(stick(830, 8500, 0.55), stick(1070, 8500, 0.55)), 1, 1.5, BLACK, 8, sfx="wood_high")
L(circle(950, 8390, 180), 2, 2.6, RED, 8, sfx="ding")

b.shot("老同学，前同事", "第一步 · 找人", view=(950, 8250, 0.85))
T("老同学", 580, 8350, 56, k0=0, sfx="pop")
T("前同事", 1320, 8350, 56, k0=1, sfx="pop")
T("聊得来就行", 950, 8630, 50, GREEN, k0=2, sfx="pop")
L(join(face(830, 8500, 0.55, "smile"), face(1070, 8500, 0.55, "smile")), 3, 3.2, BLACK, 6, sfx="wood_high")

b.shot("饭局换成深聊", "第二步 · 深聊", view=(2650, 8250, 0.85))
T("② 换成深聊", 2650, 7950, 72, BLUE, k0=0, sfx="pop")
L(join(oval(2400, 8400, 300, 100), *[circle(x, 8295, 30) for x in (2290, 2400, 2510)],
       *[circle(x, 8505, 30) for x in (2290, 2400, 2510)]), 1, 1.7, BLACK, 8, sfx="wood_high")
L(cross(2400, 8400, 140), 2, 2.4, RED, 11, sfx="rim")

b.shot("约一个人喝咖啡", "第二步 · 深聊", view=(2650, 8250, 0.85))
L(join(stick(2830, 8590, 0.55), stick(3110, 8590, 0.55)), 0, 0.6, BLUE, 8, sfx="wood_high")
L(cup(2970, 8480, 0.7), 1, 1.5, BLACK, 7, sfx="pop")
T("就两个人", 2970, 8180, 56, k0=2, sfx="pop")

b.shot("聊最近在烦啥", "第二步 · 深聊", view=(2650, 8250, 0.85))
b.erase(len(b.shots) - 1, 0, 0.7, 2400, 8400, 460, 380)
H(0, "shaker")
L(bubble(2420, 8360, 380, 120, -1), 1, 1.5, BLACK, 8, sfx="pop")
T("最近在烦啥？", 2420, 8360, 50, k0=1.5, k1=2.2)
T("聊一小时", 2420, 8590, 54, RED, k0=2.4, k1=3.0)
H(3, "ding", 0.6)

b.shot("点赞换成一句话", "第三步 · 留言", view=(950, 9200, 0.85))
T("③ 点赞换留言", 950, 8900, 72, BLUE, k0=0, sfx="pop")
L(heart(670, 9210, 60), 1, 1.4, RED, 9, sfx="pop")
L(arrow((780, 9210), (930, 9210), 0.05, 36), 2, 2.4, GREEN, 8, sfx="wood_high")
L(bubble(1170, 9200, 360, 120, -1), 3, 3.5, BLACK, 8, sfx="pop")

b.shot("问一句店在哪", "第三步 · 留言", view=(950, 9200, 0.85))
T("这店在哪？", 1170, 9200, 50, k0=0, sfx="pop")
T("他回了一大段", 950, 9470, 56, GREEN, k0=2, sfx="ding")

b.shot("定个固定时间", "第四步 · 固定", view=(2650, 9200, 0.85))
T("④ 定个时间", 2650, 8900, 72, BLUE, k0=0, sfx="pop")
L(calendar(2420, 9240, 300, 260), 1, 1.8, BLACK, 7, sfx="wood_high")
L(circle(2495, 9327, 34), 2, 2.4, RED, 8, sfx="ding")

b.shot("每周打一通电话", "第四步 · 固定", view=(2650, 9200, 0.85))
L(phone(2930, 9220, 110, 190), 0, 0.5, BLUE, 8, sfx="pop")
L(waves(3010, 9150), 0.5, 0.8, BLUE, 6)
T("周日 20:00", 2900, 9430, 52, RED, k0=1, sfx="pop")
L(check(3170, 9425, 34), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("爸妈那边也打", "第四步 · 固定", view=(2650, 9250, 0.85))
T("老友", 2450, 9570, 56, k0=0, sfx="pop")
T("爸妈", 2850, 9570, 56, k0=1, sfx="pop")
L(heart(3080, 9560, 30), 2, 2.3, RED, 8, sfx="ding")

b.shot("照着做就行", "具体做法", view=(1800, 8730, 0.355))
for n, (x, y) in enumerate(SOL):
    L(check(x + 500, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 else "pop")

b.shot("一两个知心就够", "一句话", view=(1800, 6300, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 10040, 0.8))
T("你能深聊的有几个？", 1800, 9950, 76, RED, k0=0.5, k1=1.8)
T("下一讲：一个人住久了，为什么总睡不好？", 1800, 10110, 44, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "quality", "感觉不看人数", "群里几百人，为什么还是孤单？", ACC, b.shots,
                 [f"{BOOK}第一部分 可耻的孤独（第 1–6 章，转述）",
                  "中译本：焦梦津译，中国人民大学出版社 2009；原书 W. W. Norton, 2008"],
                 "群里几百人|为什么还是【孤单】", 10,
                 ["书中观点均为转述：孤独看的是主观感受——和别人的关系质量、合不合心意，和身边人多人少、独处时间长短"
                  "不是一回事；作者团队的研究里，孤独的人和不孤独的人在外貌、聪明程度、社交时间上差别不大。出处：John T. "
                  "Cacioppo & William Patrick, Loneliness: Human Nature and the Need for Social Connection (W. W. Norton, "
                  "2008)，中译本《孤独是可耻的》（焦梦津译，中国人民大学出版社 2009），第一部分。上屏均为转述，不是逐字引文；"
                  "柱状图与“≈”只表示“差别不大”，不是研究数据。",
                  "工作群 498 人、消息 99+、聚餐、朋友圈点赞 86、工位午饭、周末饭局、过年亲戚、独居女生每周和闺蜜长聊均为"
                  "现实场景示意，数字与时间为示意，不指向任何具体公司或个人。",
                  "四步做法（找一两个说得上话的人 / 把一次饭局换成一次深聊 / 点赞换成一句留言 / 定个固定时间打电话）为据书中"
                  "思路整理的建议，对应书末第 14 章 EASE 中“Selection：重质量不重数量”与“Extend yourself：先迈一小步”。"],
                 tags="#社交 #职场")
    return b.attach(ep)
