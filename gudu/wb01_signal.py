"""01 孤独是信号（白板手绘版）：一个人吃饭，心里为什么发空？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
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
SQUARE_SHOT = 8                 # 场景 9：小人 + “饿 / 渴 / 孤独”信号图

b = Board(size=(3600, 10250))
OY = 0                          # 身边的例子起整体下移，避免上一块的字漏进页眉


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y + OY, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    if OY:
        path = skia.Path(path)
        path.offset(0, OY)
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


# ---------------------------------------------------------------- 开局：一个人吃饭（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=(view[0], view[1] + OY, view[2]), bars=2, **kw)


scene("下班回到出租屋", "灵魂拷问", (950, 850, 0.85))
L(building(650, 1150), 0, 0.9, sfx="wood_high")
T("出租屋", 650, 1225, 54, k0=1, k1=1.6)
L(moon(1250, 500, 80), 2, 2.5, BLACK, 9, sfx="pop")
T("21:30", 1250, 680, 70, RED, k0=2.6, k1=3.2)
L(stick(1080, 1250, 0.8, "down"), 4, 4.6, sfx="wood_high")
L(face(1080, 1250, 0.8, "flat"), 4.6, 4.8)

scene("一个人吃外卖刷手机", "灵魂拷问", (2650, 850, 0.85))
L(desk(2620, 1050, 420), 0, 0.7, sfx="wood_high")
L(takeout(2490, 1000), 1, 1.4, BLACK, 9, sfx="pop")
L(stick(2250, 1250, 0.8, "hold"), 1.5, 1.9)
L(face(2250, 1250, 0.8, "flat"), 1.9, 2.0)
T("外卖 × 1", 2900, 600, 70, RED, k0=2.2, k1=2.8)
L(phone(2365, 1050), 3, 3.3, BLUE, 8, sfx="pop")
for n in range(3):
    L(P((2420, 1010 + n * 35), (2480, 1010 + n * 35)), 3.4 + n * 0.15, 3.5 + n * 0.15, BLUE, 6)
T("屋里没人说话", 2800, 1360, 60, k0=4, k1=5.1, sfx="pop")

scene("周末没说话，心里发空", "灵魂拷问", (1700, 1950, 0.7), shake=[4], flashes=[4])
L(calendar(1170, 1700), 0, 0.6, sfx="wood_high")
T("周六", 1170, 1735, 70, RED, k0=0.6, k1=1.0)
L(stick(1450, 2150, 0.85, "down"), 1, 1.5, sfx="wood_high")
L(face(1450, 2150, 0.85, "flat"), 1.5, 1.65)
L(bubble(2200, 1700, 320, 180, -1), 2, 2.5, BLACK, 9, sfx="pop")
L(cross(2200, 1700, 70), 3, 3.3, RED, 12, sfx="rim")
T("心里发空？", 1950, 2010, 110, RED, k0=4, k1=5.2, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

scene("饿渴疼，都在报信", "孤独是可耻的 · 书中观点", (1050, 3000, 0.9))
L(book(750, 3000, 420, 280), 0, 0.9, sfx="wood_low")
T("孤独是可耻的", 750, 2760, 72, GREEN, k0=1, k1=1.9, sfx="pop")
T("约翰 · 卡乔波", 750, 3230, 46, k0=2, k1=2.8)
L(bowl(1300, 2800, 70), 3, 3.4, BLACK, 9, sfx="pop")
T("饿", 1480, 2810, 70, RED, k0=3.4, k1=3.8)
L(glass(1300, 3030, 0.9), 4, 4.4, BLACK, 9, sfx="pop")
T("渴", 1480, 3030, 70, RED, k0=4.4, k1=4.8)
L(bolt(1300, 3260), 5, 5.3, RED, 10, sfx="rim")
T("疼", 1480, 3260, 70, RED, k0=5.3, k1=5.7)

scene("孤独也是信号", "书中观点 · 孤独是信号", (1050, 3150, 0.9), shake=[0], flashes=[0])
T("孤独 = 信号", 1000, 3430, 120, RED, k0=0, k1=0.8, sfx="kick")
L(rays(1000, 3430, 760, 150), 2, 2.4, RED, 8, sfx="pop")
L(underline(680, 1320, 3525), 3, 3.6, RED, 9, sfx="ding")
H(5, "tom", 0.7)

VA = (2650, 3150, 0.75)
scene("几万年前，落单就危险", "书中观点 · 进化", VA)
T("几万年前", 2600, 2560, 70, k0=0, k1=0.8, sfx="pop")
L(fire(2550, 3250), 1, 1.6, BLACK, 9, sfx="wood_high")
L(stick(2330, 3400, 0.6, "down"), 2, 2.4, BLACK, 8, sfx="pop")
L(stick(2770, 3400, 0.6, "down"), 2.4, 2.8, BLACK, 8)
L(stick(3120, 3400, 0.5, "shrug"), 3, 3.5, BLUE, 8, sfx="wood_high")
L(eyes(3110, 2940), 4, 4.3, BLACK, 7, sfx="pop")
T("危险", 3110, 3085, 64, RED, k0=5, k1=5.5, sfx="rim")

ME = (1750, 4450)               # 今天的“我们”
scene("怕落单，传到了今天", "书中观点 · 进化", (2520, 3800, 0.55))
L(arrow((3050, 3300), (2880, 3300), 0.25, 40), 0, 0.5, GREEN, 9, sfx="wood_high")
T("回到火边，活下来", 2550, 3620, 60, GREEN, k0=1, k1=2.4, sfx="pop")
L(arrow((2300, 3690), (1850, 4060), 0.1, 44), 3, 3.5, GREEN, 9, sfx="wood_high")
L(stick(*ME, 0.75, "down"), 4, 4.5, BLACK, 10, sfx="pop")
L(face(*ME, 0.75, "flat"), 4.5, 4.6)
T("今天的我们", ME[0], ME[1] + 60, 50, k0=5, k1=5.6, sfx="pop")

RX = 2450
ROWS = [("饿 → 吃饭", 3910, BLACK), ("渴 → 喝水", 4110, BLACK), ("孤独 → 找人", 4310, RED)]
VI = (2200, 4170, 0.8)
scene("孤独了，就去找人", "书中观点 · 一张图", VI)
for n in range(3):
    T(ROWS[n][0], RX, ROWS[n][1], 72, ROWS[n][2], k0=n * 1.2, k1=n * 1.2 + 0.9, sfx="pop")
L(underline(RX - 220, RX + 220, 4375, 10, 30), 4, 4.5, RED, 8, sfx="ding")

scene("心空是想人了，不丢人", "书中观点 · 一张图", VI)
L(heart(ME[0], 4320, 38), 0, 0.4, RED, 8, sfx="pop")
T("想人了", ME[0], 4110, 60, RED, k0=1, k1=1.6, sfx="pop")
L(arrow((ME[0] + 80, 4320), (RX - 250, 4315), 0.05, 34), 2, 2.5, RED, 8, sfx="wood_high")
T("孤独也一样", 2150, 4540, 64, k0=3, k1=4.0, sfx="pop")
L(check(2370, 4535, 40), 5, 5.3, GREEN, 10, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

OY = 550
CARDS = [(950, 5300), (2650, 5300), (950, 6250), (2650, 6250)]
OVER = (1800, 5780, 0.355)
scene("身边这种时候很多", "身边的例子", OVER)
T("身边的例子", 1800, 4760, 130, k0=0, k1=1.2, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 2 + n, 2.6 + n, GREEN, 8, sfx="wood_high" if n % 2 == 0 else None)

scene("想约饭，又不好意思", "例子 · 工位午饭", (840, 5300, 0.85))
L(desk(800, 5400, 320), 0, 0.5, sfx="wood_high")
L(desk(1270, 5400, 320), 0.5, 1.0)
L(takeout(690, 5350, 0.6), 1, 1.3, BLACK, 8, sfx="pop")
L(takeout(1160, 5350, 0.6), 1.3, 1.6, BLACK, 8)
L(stick(560, 5600, 0.6, "down"), 2, 2.3, sfx="wood_high")
L(stick(1035, 5600, 0.6, "down"), 2.3, 2.6)
L(bubble(780, 5090, 280, 140, -1), 3, 3.4, BLACK, 8, sfx="pop")
T("一起吃？", 780, 5090, 54, k0=3.4, k1=4.0)
L(scribble(780, 5090, 280, 140, 7), 4.2, 4.7, RED, 7)
T("算了", 1060, 5090, 56, BLUE, k0=5, k1=5.4, sfx="rim")

scene("刚到新城市，能约谁", "例子 · 新城市", (2760, 5300, 0.85))
L(building(2330, 5600, 200, 300), 0, 0.5, sfx="wood_high")
L(building(2540, 5600, 180, 400), 0.5, 1.0)
L(stick(2780, 5650, 0.7, "down"), 1, 1.5, BLUE, 9, sfx="pop")
L(suitcase(2900, 5600, 0.9), 1.5, 1.8, BLUE, 8)
T("新城市", 2600, 5000, 70, k0=2, k1=2.6, sfx="pop")
L(rect(3090, 5270, 230, 400, 24), 3, 3.4, BLACK, 9, sfx="wood_high")
L(contacts(3090, 5170), 4, 4.5, BLACK, 7, sfx="pop")
T("能约谁？", 3090, 4980, 56, RED, k0=5, k1=5.7, sfx="rim")

scene("爸妈视频只问吃了没", "例子 · 爸妈", (950, 6250, 0.85))
L(house(600, 6560), 0, 0.8, sfx="wood_high")
L(stick(850, 6600, 0.55, "down"), 1, 1.4, BLACK, 8, sfx="pop")
L(stick(960, 6600, 0.55, "down", hair=True), 1.4, 1.8, BLACK, 8)
T("1200 公里", 860, 5990, 56, RED, k0=2, k1=2.8, sfx="pop")
L(phone(1180, 6460, 90, 150), 3, 3.3, BLUE, 8, sfx="pop")
L(bubble(1180, 6190, 260, 130, -1), 3.4, 3.8, BLACK, 8)
T("吃了没", 1180, 6190, 52, k0=4, k1=4.6, sfx="pop")
T("嗯，挂了", 1420, 6440, 50, k0=5, k1=5.7, sfx="pop")

scene("带娃一天，没大人聊", "例子 · 带娃", (2650, 6250, 0.85))
L(stick(2450, 6600, 0.75, "hold"), 0, 0.5, sfx="wood_high")
L(stick(2650, 6600, 0.4, "up"), 1, 1.3, BLUE, 8, sfx="pop")
T("喂饭 哄睡 洗澡", 2750, 6000, 52, k0=2, k1=3, sfx="pop")
L(bubble(2850, 6230, 260, 130, -1), 3.2, 3.6, BLACK, 8)
T("乖，张嘴", 2850, 6230, 48, k0=4, k1=4.6, sfx="pop")
T("没大人可聊", 2950, 6480, 56, RED, k0=5, k1=5.9, sfx="rim")

scene("都在叫你去找人", "身边的例子", OVER, shake=[4])
for n, (x, y) in enumerate(CARDS):
    L(lamp(x - 460, y - 310, 1.0), n, n + 0.4, RED, 9, sfx="ding" if n % 2 else "pop")
T("该去找人了", 1800, 6830, 120, RED, k0=4, k1=4.8, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 7700), (2650, 7700), (950, 8650), (2650, 8650)]
scene("认出信号，别骂自己", "第一步 · 认出信号", (950, 7750, 0.85))
L(rect(*SOL[0], 1200, 860, 40), 0, 0.6, GREEN, 8)
T("① 认出信号", 950, 7400, 76, BLUE, k0=0.6, k1=1.5)
L(lamp(640, 7720, 1.1), 2, 2.5, RED, 9, sfx="wood_high")
L(bubble(1150, 7640, 330, 140, -1), 3, 3.3, BLACK, 8, sfx="pop")
T("我想人了", 1150, 7640, 54, k0=3.3, k1=3.9)
T("矫情", 700, 8020, 60, k0=4, k1=4.4, sfx="pop")
L(cross(700, 8020, 70), 4.5, 4.8, RED, 12)
T("正常", 1000, 8020, 60, GREEN, k0=5, k1=5.5, sfx="pop")
H(0, "wood_high", 0.6)

scene("刷到半夜，还是空", "第二步 · 别硬扛", (2650, 7750, 0.85))
L(rect(*SOL[1], 1200, 860, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("② 别硬扛", 2650, 7400, 76, BLUE, k0=0.6, k1=1.5)
L(phone(2450, 7740, 120, 200), 2, 2.4, BLUE, 9, sfx="pop")
T("2:00", 2450, 7990, 60, RED, k0=2.5, k1=2.9)
L(arrow((2540, 7740), (2770, 7740), 0.05, 34), 3, 3.4, BLACK, 8, sfx="wood_high")
L(heart(2900, 7750, 90), 4, 4.5, BLACK, 9, sfx="pop")
T("还是空", 2900, 7990, 56, RED, k0=5, k1=5.6, sfx="rim")

scene("联系一个人，说件具体事", "第三步 · 联系一个人", (950, 8810, 0.85))
L(rect(*SOL[2], 1200, 860, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("③ 今天联系一个人", 950, 8350, 66, BLUE, k0=0.5, k1=1.8)
L(phone(560, 8720, 160, 280), 2, 2.5, BLACK, 9, sfx="pop")
T("在吗？", 1080, 8850, 58, k0=3, k1=3.5, sfx="pop")
L(cross(1080, 8850, 60), 4, 4.3, RED, 10, sfx="rim")
L(bubble(1060, 8600, 430, 140, -1), 4.4, 4.8, BLUE, 8)
T("那家面馆还开吗？", 1060, 8600, 46, k0=5, k1=6, sfx="pop")

scene("约同事楼下吃碗面", "第四步 · 约顿饭", (2650, 8810, 0.85))
L(rect(*SOL[3], 1200, 860, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("④ 约顿饭", 2650, 8350, 76, BLUE, k0=0.5, k1=1.4)
L(stick(2350, 8950, 0.7, "point"), 2, 2.5, sfx="wood_high")
L(stick(2950, 8950, 0.7, "down"), 2.5, 2.9, BLUE, 9)
T("明天中午？", 2650, 8560, 54, k0=3, k1=3.8, sfx="pop")
L(bowl(2650, 8860, 80), 4, 4.5, BLACK, 9, sfx="wood_high")
T("12:10 楼下", 2650, 9030, 54, k0=5, k1=5.8, sfx="pop")

scene("空了，就找个人", "一句话", (1800, 4550, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 9400, 0.8))
H(0, "cymbal", 0.5)
T("你今天想联系谁？", 1800, 9320, 76, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：群里几百人，为什么还是孤单？", 1800, 9480, 46, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "signal", "孤独是信号", "一个人吃饭，心里为什么发空？", ACC, b.shots,
                 [f"{BOOK}第一部分 可耻的孤独、第二部分 从自私的基因到社会动物（转述）",
                  "中译本：焦梦津译，中国人民大学出版社 2009"],
                 "一个人吃饭|心里为什么【发空】", 8,
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
