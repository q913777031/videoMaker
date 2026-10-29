"""01 孤独是信号（白板手绘版）：一个人吃饭，心里为什么发空？

叙事：打工人切身问题开局（下班回出租屋、一个人吃外卖、边吃边刷手机、周末一整天一句话没说 → 心里发空）→
书中观点（亮书；饿、渴、疼都在提醒身体缺了什么，孤独也是这样一种信号，催人回到别人身边；它是进化留下来的：
祖先落单就危险，怕落单、赶紧回到人群的人更容易活下来；画成“饿 → 吃饭 / 渴 → 喝水 / 孤独 → 找人”一张图）→
身边的例子（午饭各吃各的、刚到新城市、爸妈在老家、带娃一整天；最后连到同一个信号）→
具体做法（认出信号 / 别骂自己也别硬扛 / 当天联系一个人，说件具体的事 / 约顿饭）→ 评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, 2008；
中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, building, check, circle, clock,
                               cross, desk, face, hands_at, join, rect, scribble, stick, underline)

from .common import BOOK, episode

ACC = "#C2603A"
SQUARE_SHOT = 15                # 镜头 16：小人 + “饿 / 渴 / 孤独”信号图

b = Board(size=(3600, 9700))


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

def moon(x, y, r=90) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12), P((x - 12, y + h / 2 - 16), (x + 12, y + h / 2 - 16)))


def takeout(x, y, s=1.0) -> skia.Path:
    """外卖盒 + 一双筷子：(x, y) 为盒身中心。"""
    return join(P((x - 80 * s, y - 40 * s), (x - 60 * s, y + 50 * s), (x + 60 * s, y + 50 * s), (x + 80 * s, y - 40 * s),
                  close=True),
                P((x - 92 * s, y - 40 * s), (x - 70 * s, y - 62 * s), (x + 70 * s, y - 62 * s), (x + 92 * s, y - 40 * s)),
                P((x + 10 * s, y - 70 * s), (x + 110 * s, y - 160 * s)), P((x + 35 * s, y - 66 * s), (x + 130 * s, y - 145 * s)))


def heart(x, y, r=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def calendar(x, y, w=260, h=240) -> skia.Path:
    return join(rect(x, y, w, h, 16), P((x - w / 2, y - h / 2 + 60), (x + w / 2, y - h / 2 + 60)),
                P((x - w / 4, y - h / 2 - 25), (x - w / 4, y - h / 2 + 20)),
                P((x + w / 4, y - h / 2 - 25), (x + w / 4, y - h / 2 + 20)))


def bowl(x, y, r=90, steam=True) -> skia.Path:
    """碗：(x, y) 为碗口中点。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r * 0.9, 2 * r, 1.8 * r), 0, 180)
    parts = [p, P((x - r - 12, y), (x + r + 12, y)), P((x - r * 0.35, y + r * 0.95), (x + r * 0.35, y + r * 0.95))]
    if steam:
        for dx in (-r * 0.3, r * 0.3):
            st = skia.Path()
            st.moveTo(x + dx, y - 20)
            st.quadTo(x + dx - 20, y - 50, x + dx, y - 80)
            st.quadTo(x + dx + 20, y - 110, x + dx, y - 140)
            parts.append(st)
    return join(*parts)


def glass(x, y, s=1.0) -> skia.Path:
    return join(P((x - 45 * s, y - 70 * s), (x - 35 * s, y + 70 * s), (x + 35 * s, y + 70 * s), (x + 45 * s, y - 70 * s)),
                P((x - 41 * s, y - 25 * s), (x + 41 * s, y - 25 * s)))


def bolt(x, y, s=1.0) -> skia.Path:
    return P((x + 25 * s, y - 80 * s), (x - 30 * s, y + 5 * s), (x + 12 * s, y + 5 * s), (x - 22 * s, y + 80 * s))


def lamp(x, y, s=1.0) -> skia.Path:
    """信号灯：圆顶警示灯 + 底座 + 光芒 + 叹号。(x, y) 为灯罩中心。"""
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeXYWH(x - 55 * s, y - 60 * s, 110 * s, 120 * s), 180, 180)
    parts = [dome, P((x - 55 * s, y), (x - 55 * s, y + 30 * s)), P((x + 55 * s, y), (x + 55 * s, y + 30 * s)),
             rect(x, y + 45 * s, 150 * s, 30 * s, 8 * s),
             P((x, y - 38 * s), (x, y - 2 * s)), circle(x, y + 14 * s, 4 * s)]
    for dx, dy, ex, ey in ((0, -80, 0, -120), (-62, -58, -92, -88), (62, -58, 92, -88), (-80, -10, -120, -10),
                           (80, -10, 120, -10)):
        parts.append(P((x + dx * s, y + dy * s), (x + ex * s, y + ey * s)))
    return join(*parts)


def fire(x, y, s=1.0) -> skia.Path:
    """篝火：两根交叉的柴 + 火苗。(x, y) 为柴堆中心。"""
    fl = skia.Path()
    fl.moveTo(x, y - 170 * s)
    fl.quadTo(x + 85 * s, y - 70 * s, x + 35 * s, y)
    fl.lineTo(x - 35 * s, y)
    fl.quadTo(x - 85 * s, y - 70 * s, x, y - 170 * s)
    inner = skia.Path()
    inner.moveTo(x, y - 90 * s)
    inner.quadTo(x + 35 * s, y - 40 * s, x, y - 5 * s)
    inner.quadTo(x - 35 * s, y - 40 * s, x, y - 90 * s)
    return join(fl, inner, P((x - 100 * s, y + 35 * s), (x + 100 * s, y - 5 * s)),
                P((x - 100 * s, y - 5 * s), (x + 100 * s, y + 35 * s)))


def eyes(x, y, s=1.0) -> skia.Path:
    """暗处的一双眼睛（野兽）。"""
    parts = []
    for dx in (-45, 45):
        p = skia.Path()
        p.addOval(skia.Rect.MakeXYWH(x + (dx - 24) * s, y - 11 * s, 48 * s, 22 * s))
        parts += [p, circle(x + dx * s, y, 5 * s)]
    parts += [P((x - 75 * s, y - 40 * s), (x - 20 * s, y - 20 * s)), P((x + 75 * s, y - 40 * s), (x + 20 * s, y - 20 * s))]
    return join(*parts)


def suitcase(x, y, s=1.0) -> skia.Path:
    return join(rect(x, y, 120 * s, 100 * s, 12 * s),
                P((x - 25 * s, y - 50 * s), (x - 25 * s, y - 75 * s), (x + 25 * s, y - 75 * s), (x + 25 * s, y - 50 * s)),
                P((x - 60 * s, y), (x + 60 * s, y)))


def house(x, y, w=280, h=230) -> skia.Path:
    """平房：(x, y) 为地面中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 35, y - h), (x, y - h - 150), (x + w / 2 + 35, y - h)),
                P((x - 35, y), (x - 35, y - 110), (x + 35, y - 110), (x + 35, y)), rect(x + w / 4 + 10, y - h + 70, 60, 60, 4))


def contacts(x, y, w=230, n=3) -> skia.Path:
    parts = []
    for i in range(n):
        yy = y + i * 90
        parts += [circle(x - w / 2 + 50, yy, 22), P((x - w / 2 + 90, yy), (x + w / 2 - 30, yy))]
    return join(*parts)


def rays(x, y, w, h) -> skia.Path:
    """字周围的爆点短线。"""
    parts = []
    for dx, dy, ex, ey in ((-1, -1, -1.25, -1.5), (0, -1.15, 0, -1.6), (1, -1, 1.25, -1.5)):
        parts.append(P((x + dx * w / 2, y + dy * h / 2), (x + ex * w / 2, y + ey * h / 2)))
    return join(*parts)


# ---------------------------------------------------------------- 开局：一个人吃饭（镜头 1–6）

b.shot("下班回到出租屋", "灵魂拷问", view=(950, 850, 0.85))
L(building(650, 1150), 0, 0.8, sfx="wood_high")
T("出租屋", 650, 1225, 54, k0=0.8)
L(moon(1250, 520, 80), 1, 1.4, BLACK, 9, sfx="pop")
T("21:30", 1250, 700, 70, RED, k0=1.4, k1=1.9)
L(stick(1080, 1250, 0.8, "down"), 2, 2.5, sfx="wood_high")
L(face(1080, 1250, 0.8, "flat"), 2.5, 2.65)

b.shot("一个人吃外卖", "灵魂拷问", view=(2650, 850, 0.85))
L(desk(2620, 1050, 420), 0, 0.7, sfx="wood_high")
L(takeout(2490, 1000), 1, 1.4, BLACK, 9, sfx="pop")
L(stick(2250, 1250, 0.8, "hold"), 1.4, 1.8)
L(face(2250, 1250, 0.8, "flat"), 1.8, 1.9)
T("外卖 × 1", 2900, 600, 70, RED, k0=2, k1=2.7, sfx="pop")

b.shot("边吃边刷手机", "灵魂拷问", view=(2650, 850, 0.85))
L(phone(2365, 1050), 0, 0.3, BLUE, 8, sfx="pop")
for n in range(3):
    L(P((2420, 1010 + n * 35), (2480, 1010 + n * 35)), 1 + n * 0.2, 1.15 + n * 0.2, BLUE, 6,
      sfx="shaker" if n == 0 else None)
T("屋里没人说话", 2650, 1360, 60, k0=2, sfx="pop")

b.shot("周末一整天", "灵魂拷问", view=(950, 1750, 0.85))
L(calendar(650, 1700), 0, 0.6, sfx="wood_high")
T("周六", 650, 1735, 70, RED, k0=0.6, k1=1.0)
L(clock(1200, 1680, 130), 1, 1.5, sfx="wood_high")
L(hands_at(1200, 1680, 130, 9, 0), 1.5, 1.7, RED, 10)
T("9:00 → 23:00", 950, 2080, 64, k0=2, k1=2.9, sfx="pop")

b.shot("一句话都没说", "灵魂拷问", view=(2650, 1750, 0.85))
L(stick(2380, 2150, 0.85, "down"), 0, 0.5, sfx="wood_high")
L(face(2380, 2150, 0.85, "flat"), 0.5, 0.65)
L(bubble(2820, 1520, 320, 180, -1), 1, 1.5, BLACK, 9, sfx="pop")
L(cross(2820, 1520, 70), 2, 2.3, RED, 12, sfx="rim")
T("说话：0 句", 2850, 1930, 66, RED, k0=2.3, k1=2.9)

b.shot("心里怎么发空？", "灵魂拷问", view=(1800, 1300, 0.42), flashes=[0])
L(heart(1800, 1330, 190), 0, 0.6, RED, 12, sfx="kick")
T("？", 1800, 1280, 200, RED, k0=1, k1=1.4, sfx="pop")
T("心里发空", 1800, 2380, 110, k0=2, k1=2.8, sfx="pop")
H(3, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲这个", "孤独是可耻的", view=(1050, 3000, 0.9))
L(book(750, 3000, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 750, 2760, 72, GREEN, k0=1.0, sfx="pop")
T("约翰 · 卡乔波", 750, 3230, 46, k0=2.0, sfx="pop")

b.shot("饿渴疼都在报信", "书中观点 · 身体的信号", view=(1050, 3000, 0.9))
L(bowl(1300, 2800, 70), 0, 0.5, BLACK, 9, sfx="pop")
T("饿", 1480, 2810, 70, RED, k0=0.5)
L(glass(1300, 3030, 0.9), 1, 1.4, BLACK, 9, sfx="pop")
T("渴", 1480, 3030, 70, RED, k0=1.4)
L(bolt(1300, 3260), 2, 2.3, RED, 10, sfx="rim")
T("疼", 1480, 3260, 70, RED, k0=2.3)

b.shot("孤独也是信号", "书中观点 · 孤独是信号", view=(1050, 3150, 0.9), shake=[0], flashes=[0])
T("孤独 = 信号", 1000, 3430, 120, RED, k0=0, k1=0.5, sfx="kick")
L(rays(1000, 3430, 760, 150), 1, 1.3, RED, 8, sfx="pop")
L(underline(680, 1320, 3525), 2, 2.5, RED, 9, sfx="ding")
H(3, "tom", 0.7)

b.shot("这是老祖宗留的", "书中观点 · 进化", view=(2650, 3050, 0.8))
T("几万年前", 2600, 2620, 70, k0=0, sfx="pop")
L(fire(2550, 3250), 1, 1.6, BLACK, 9, sfx="wood_high")
L(stick(2330, 3400, 0.6, "down"), 2, 2.4, BLACK, 8, sfx="pop")
L(stick(2770, 3400, 0.6, "down"), 2.4, 2.8, BLACK, 8)
H(3, "wood_low", 0.6)

b.shot("落单就有危险", "书中观点 · 进化", view=(2650, 3050, 0.8))
L(stick(3120, 3400, 0.5, "shrug"), 0, 0.5, BLUE, 8, sfx="wood_high")
L(eyes(3110, 2900), 1, 1.3, BLACK, 7, sfx="pop")
T("危险", 3110, 2760, 70, RED, k0=2, sfx="rim")

b.shot("赶紧回到火边", "书中观点 · 进化", view=(2650, 3050, 0.8))
L(arrow((3050, 3300), (2880, 3300), 0.25, 40), 0, 0.5, GREEN, 9, sfx="wood_high")
T("回到火边", 2600, 3520, 60, GREEN, k0=1, sfx="pop")
L(check(2900, 3515, 40), 2, 2.3, GREEN, 10, sfx="ding")

ME = (1620, 4450)               # 今天的“我们”
b.shot("这份怕传到今天", "书中观点 · 进化", view=(2200, 3820, 0.7))
T("活下来的人", 2640, 3640, 50, k0=0, sfx="pop")
L(arrow((2450, 3600), (1720, 4130), 0.1, 44), 1, 1.5, GREEN, 9, sfx="wood_high")
L(stick(*ME, 0.75, "down"), 2, 2.4, BLACK, 10, sfx="pop")
L(face(*ME, 0.75, "flat"), 2.4, 2.5)
T("今天的我们", ME[0], ME[1] + 60, 50, k0=2.5, k1=3.0)

RX = 2350
ROWS = [("饿 → 吃饭", 3910, BLACK), ("渴 → 喝水", 4110, BLACK), ("孤独 → 找人", 4310, RED)]
VI = (2150, 4120, 0.8)
b.shot("画成一张图", "书中观点 · 一张图", view=VI)
for n in range(2):
    T(ROWS[n][0], RX, ROWS[n][1], 72, ROWS[n][2], k0=n, sfx="pop")

b.shot("孤独就去找人", "书中观点 · 一张图", view=VI)
T(ROWS[2][0], RX, ROWS[2][1], 72, ROWS[2][2], k0=0, sfx="pop")
L(underline(RX - 220, RX + 220, 4375, 10, 30), 2, 2.5, RED, 8, sfx="ding")

b.shot("心空，是想人了", "书中观点 · 一张图", view=VI)
L(heart(ME[0], 4320, 38), 0, 0.3, RED, 8, sfx="pop")
T("想人了", ME[0], 4110, 60, RED, k0=1, sfx="pop")
L(arrow((ME[0] + 80, 4320), (RX - 250, 4315), 0.05, 34), 2, 2.4, RED, 8, sfx="wood_high")

b.shot("饿了不丢人", "书中观点 · 一张图", view=(2100, 4170, 0.8))
T("孤独也一样", RX, 4540, 64, k0=0, sfx="pop")
L(check(RX + 260, 4535, 40), 2, 2.3, GREEN, 10, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5300), (2650, 5300), (950, 6250), (2650, 6250)]
OVER = (1800, 5780, 0.355)
b.shot("这种时候很多", "身边的例子", view=OVER)
T("身边的例子", 1800, 4760, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("午饭各吃各的", "例子 · 工位午饭", view=(950, 5300, 0.85))
L(desk(800, 5400, 320), 0, 0.5, sfx="wood_high")
L(desk(1270, 5400, 320), 0.5, 1.0)
L(takeout(690, 5350, 0.6), 1, 1.3, BLACK, 8, sfx="pop")
L(takeout(1160, 5350, 0.6), 1.3, 1.6, BLACK, 8)
L(stick(560, 5600, 0.6, "down"), 2, 2.3, sfx="wood_high")
L(stick(1035, 5600, 0.6, "down"), 2.3, 2.6)
T("12:00", 1150, 4980, 60, RED, k0=2.6, k1=2.95)

b.shot("想约人又不好意思", "例子 · 工位午饭", view=(950, 5300, 0.85))
L(bubble(780, 5090, 280, 140, -1), 0, 0.5, BLACK, 8, sfx="pop")
T("一起吃？", 780, 5090, 54, k0=0.5)
L(scribble(780, 5090, 280, 140, 7), 2, 2.5, RED, 7, sfx="shaker")
T("算了", 1060, 5090, 56, BLUE, k0=2.5, k1=2.9)

b.shot("刚到新城市", "例子 · 新城市", view=(2650, 5300, 0.85))
L(building(2330, 5600, 200, 300), 0, 0.5, sfx="wood_high")
L(building(2540, 5600, 180, 400), 0.5, 1.0)
L(stick(2780, 5650, 0.7, "down"), 1, 1.5, BLUE, 9, sfx="pop")
L(suitcase(2900, 5600, 0.9), 1.5, 1.8, BLUE, 8)
T("新城市", 2600, 5000, 70, k0=2, sfx="pop")

b.shot("通讯录没人能约", "例子 · 新城市", view=(2650, 5300, 0.85))
L(rect(3090, 5270, 230, 400, 24), 0, 0.5, BLACK, 9, sfx="wood_high")
L(contacts(3090, 5170), 1, 1.5, BLACK, 7, sfx="pop")
T("能约谁？", 3090, 4980, 56, RED, k0=2, sfx="rim")

b.shot("爸妈在老家", "例子 · 爸妈", view=(950, 6250, 0.85))
L(house(600, 6560), 0, 0.8, sfx="wood_high")
L(stick(850, 6600, 0.55, "down"), 1, 1.4, BLACK, 8, sfx="pop")
L(stick(960, 6600, 0.55, "down", hair=True), 1.4, 1.8, BLACK, 8)
T("1200 公里", 860, 5990, 56, RED, k0=2, sfx="pop")

b.shot("视频只问吃了没", "例子 · 爸妈", view=(950, 6250, 0.85))
L(phone(1300, 6460, 90, 150), 0, 0.3, BLUE, 8, sfx="pop")
L(bubble(1300, 6190, 260, 130, -1), 1, 1.4, BLACK, 8, sfx="pop")
T("吃了没", 1300, 6190, 52, k0=1.4)
T("嗯，挂了", 1300, 6650, 50, k0=2, sfx="pop")

b.shot("带娃一整天", "例子 · 带娃", view=(2650, 6250, 0.85))
L(stick(2450, 6600, 0.75, "hold"), 0, 0.5, sfx="wood_high")
L(stick(2650, 6600, 0.4, "up"), 1, 1.3, BLUE, 8, sfx="pop")
T("喂饭 哄睡 洗澡", 2750, 6000, 52, k0=2, k1=3, sfx="pop")

b.shot("没跟大人说上话", "例子 · 带娃", view=(2650, 6250, 0.85))
L(bubble(2850, 6230, 260, 130, -1), 0, 0.4, BLACK, 8, sfx="pop")
T("乖，张嘴", 2850, 6230, 48, k0=0.4)
T("没大人可聊", 2950, 6480, 56, RED, k0=2, sfx="rim")

b.shot("都在发同一个信号", "身边的例子", view=OVER)
for n, (x, y) in enumerate(CARDS):
    L(lamp(x - 460, y - 310, 1.0), n, n + 0.4, RED, 9, sfx="ding" if n % 2 else "pop")

b.shot("别装没听见", "身边的例子", view=OVER, shake=[0])
T("该去找人了", 1800, 6830, 120, RED, k0=0, k1=0.6, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 7700), (2650, 7700), (950, 8650), (2650, 8650)]
b.shot("空了怎么办", "具体做法", view=(1800, 8180, 0.355))
T("心里空了，这样做", 1800, 7160, 120, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 860, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先认出这个信号", "第一步 · 认出信号", view=(950, 7700, 0.85))
T("① 认出信号", 950, 7400, 76, BLUE, k0=0, sfx="pop")
L(lamp(640, 7720, 1.1), 1, 1.6, RED, 9, sfx="wood_high")
L(stick(1150, 8050, 0.7, "down"), 2, 2.5, sfx="pop")
L(face(1150, 8050, 0.7, "flat"), 2.5, 2.65)

b.shot("跟自己说一句", "第一步 · 认出信号", view=(950, 7700, 0.85))
L(bubble(1150, 7640, 330, 140, -1), 0, 0.4, BLACK, 8, sfx="pop")
T("我想人了", 1150, 7640, 54, k0=0.4)
L(underline(1030, 1270, 7700, 8, 30), 2, 2.4, RED, 7, sfx="ding")

b.shot("别骂自己矫情", "第一步 · 认出信号", view=(950, 7750, 0.85))
T("矫情", 600, 8030, 60, k0=0, sfx="pop")
L(cross(600, 8030, 70), 1, 1.3, RED, 12, sfx="rim")
T("正常", 830, 8030, 60, GREEN, k0=2, sfx="pop")

b.shot("也别硬扛", "第二步 · 别硬扛", view=(2650, 7700, 0.85))
T("② 别硬扛", 2650, 7400, 76, BLUE, k0=0, sfx="pop")
L(phone(2450, 7740, 120, 200), 1, 1.4, BLUE, 9, sfx="pop")
T("2:00", 2450, 7990, 60, RED, k0=2, sfx="pop")

b.shot("刷到半夜还是空", "第二步 · 别硬扛", view=(2650, 7700, 0.85))
L(heart(2900, 7750, 90), 0, 0.5, BLACK, 9, sfx="wood_high")
T("还是空", 2900, 7990, 56, RED, k0=1, sfx="pop")
L(arrow((2540, 7740), (2770, 7740), 0.05, 34), 2, 2.4, BLACK, 8, sfx="wood_high")

b.shot("今天联系一个人", "第三步 · 联系一个人", view=(950, 8650, 0.85))
T("③ 今天联系一个人", 950, 8350, 66, BLUE, k0=0, k1=1.4, sfx="pop")
L(phone(620, 8720, 160, 280), 2, 2.5, BLACK, 9, sfx="wood_high")

b.shot("给老朋友发消息", "第三步 · 联系一个人", view=(950, 8650, 0.85))
L(bubble(1080, 8600, 430, 140, -1), 0, 0.5, BLUE, 8, sfx="pop")
T("那家面馆还开吗？", 1080, 8600, 46, k0=1, k1=2, sfx="pop")
H(3, "ding", 0.6)

b.shot("别只发在吗", "第三步 · 联系一个人", view=(950, 8700, 0.85))
T("在吗？", 1080, 8850, 58, k0=0, sfx="pop")
L(cross(1080, 8850, 60), 1, 1.3, RED, 10, sfx="rim")
L(check(1350, 8600, 40), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("约同事吃午饭", "第四步 · 约顿饭", view=(2650, 8650, 0.85))
T("④ 约顿饭", 2650, 8350, 76, BLUE, k0=0, sfx="pop")
L(stick(2350, 8950, 0.7, "point"), 1, 1.5, sfx="wood_high")
L(stick(2950, 8950, 0.7, "down"), 1.5, 2.0, BLUE, 9)
T("明天中午？", 2650, 8560, 54, k0=2, sfx="pop")

b.shot("楼下吃碗面就行", "第四步 · 约顿饭", view=(2650, 8700, 0.85))
L(bowl(2650, 8860, 80), 0, 0.6, BLACK, 9, sfx="wood_high")
T("12:10 楼下", 2650, 9030, 54, k0=1, sfx="pop")
H(2, "ding", 0.6)

b.shot("做完一件就算数", "具体做法", view=(1800, 8180, 0.355))
for n, (x, y) in enumerate(SOL):
    L(check(x + 500, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 else "pop")

b.shot("空了，就找个人", "一句话", view=(1800, 4850, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 9400, 0.8))
T("你今天想联系谁？", 1800, 9320, 76, RED, k0=0.5, k1=1.8)
T("下一讲：群里几百人，为什么还是孤单？", 1800, 9480, 46, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "signal", "孤独是信号", "一个人吃饭，心里为什么发空？", ACC, b.shots,
                 [f"{BOOK}第一部分 可耻的孤独、第二部分 从自私的基因到社会动物（转述）",
                  "中译本：焦梦津译，中国人民大学出版社 2009"],
                 "一个人吃饭|心里为什么【发空】", 15,
                 ["书中观点均为转述：孤独像饥饿、口渴、疼痛一样，是一种信号，提醒人去修复和别人的联系；这种感受是进化"
                  "留下来的——人类祖先离开群体就危险，对落单敏感、会赶紧回到群体的人更容易活下来。相关内容见第一部分"
                  "“可耻的孤独”与第二部分“从自私的基因到社会动物”。出处：John T. Cacioppo & William Patrick, "
                  "Loneliness: Human Nature and the Need for Social Connection (W. W. Norton, 2008)，中译本《孤独是可耻的》"
                  "（约翰·卡乔波、威廉·帕特里克著，焦梦津译，中国人民大学出版社 2009）。上屏均为转述，不是逐字引文；"
                  "书名中的“可耻”不用作对任何人的评价。",
                  "“几万年前”篝火、落单遇险的画面，以及“饿 → 吃饭 / 渴 → 喝水 / 孤独 → 找人”一图，为对书中观点的通俗化示意。",
                  "下班一个人吃外卖、周末一整天没开口、工位各吃各的午饭、刚到新城市、爸妈在老家视频、带娃一整天均为现实场景"
                  "示意，不指向任何具体公司或个人；时间、距离、句数为示意，不是数据。",
                  "四步做法（认出信号、别骂自己也别硬扛、当天联系一个人并说件具体的事、约顿饭）为据书中思路整理的建议。"],
                 tags="#独处")
    return b.attach(ep)
