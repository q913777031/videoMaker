"""04 越孤单越戒备（白板手绘版）：越孤单，为什么越不想见人？

叙事：打工人切身问题开局（同事消息已读两小时没回，心里嘀咕“他烦我了？”；周六聚餐的邀请回了句“有事”，
一个人在家看群里晒合照）→ 书中观点（亮书《孤独是可耻的》、卡乔波；祖先离群就危险，所以孤单的人对冷脸格外警觉；
孤单久了警报更灵，一点冷脸被放大；画成一个圈：孤单 → 往坏处想 → 戒备躲人 → 别人疏远 → 更孤单，往坏处想这一环能拆）→
身边的例子（职场：领导开会皱眉，以为在说自己，一句没说；生活：群里约爬山没人接，撤回再也不发；家庭：妈妈打电话
问近况，听着像催，草草挂掉；生活：电梯里邻居打招呼，低头装没看见，下回他也不打了；四件都在这个圈里）→
具体做法（先打个问号 / 核对事实 / 先递个小善意 / 往好处想一步，圈就反着转）→ 评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, 2008；
中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               doc, face, hands_at, join, marker, rect, stick, underline)
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#5A6FA8"
SQUARE_SHOT = 16

b = Board(size=(3600, 9400))


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
    return join(rect(x, y, w, h, 12), P((x - 12, y + h / 2 - 16), (x + 12, y + h / 2 - 16)))


def big_phone(x, y, w=420, h=620) -> skia.Path:
    """大手机屏（聊天界面框）。"""
    return join(rect(x, y, w, h, 40), P((x - w / 2, y - h / 2 + 80), (x + w / 2, y - h / 2 + 80)),
                P((x - 40, y + h / 2 - 34), (x + 40, y + h / 2 - 34)))


def thought(x, y, w, h) -> skia.Path:
    """想法泡泡：圆角框 + 往左下的三个小圆。"""
    return join(rect(x, y, w, h, 60), circle(x - w * 0.32, y + h / 2 + 40, 20), circle(x - w * 0.42, y + h / 2 + 90, 13))


def sofa(x, y, w=460) -> skia.Path:
    """沙发（正视）：(x, y) 为坐垫中点。"""
    return join(rect(x, y - 110, w - 80, 150, 30), rect(x, y + 20, w, 110, 30),
                P((x - w / 2 + 30, y + 75), (x - w / 2 + 30, y + 130)), P((x + w / 2 - 30, y + 75), (x + w / 2 - 30, y + 130)))


def cup(x, y, s=1.0) -> skia.Path:
    body = P((x - 60 * s, y - 75 * s), (x - 48 * s, y + 75 * s), (x + 48 * s, y + 75 * s), (x + 60 * s, y - 75 * s),
             close=True)
    handle = skia.Path()
    handle.addArc(skia.Rect.MakeXYWH(x + 30 * s, y - 45 * s, 60 * s, 70 * s), -90, 180)
    st = skia.Path()
    st.moveTo(x, y - 95 * s)
    st.quadTo(x - 22 * s, y - 125 * s, x, y - 150 * s)
    return join(body, handle, P((x - 57 * s, y - 45 * s), (x + 57 * s, y - 45 * s)), st)


def magnifier(x, y, r=80) -> skia.Path:
    return join(circle(x, y, r), P((x + r * 0.7, y + r * 0.7), (x + r * 1.6, y + r * 1.6)))


def elevator(x, y, w=620, h=620) -> skia.Path:
    """电梯厢：(x, y) 为中心，带楼层显示框。"""
    return join(rect(x, y, w, h, 16), P((x, y - h / 2 + 90), (x, y + h / 2)), rect(x, y - h / 2 + 45, 140, 60, 10))


def ring(x, y, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    return p


def heart(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + 60 * s)
    p.cubicTo(x - 110 * s, y - 10 * s, x - 60 * s, y - 90 * s, x, y - 35 * s)
    p.cubicTo(x + 60 * s, y - 90 * s, x + 110 * s, y - 10 * s, x, y + 60 * s)
    return p


def loop_arrow(x, y, r, head=40, cw=True) -> skia.Path:
    """循环箭头（约 300 度）；cw=False 时逆时针。"""
    p = skia.Path()
    if cw:
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -60, 300)
        a = math.radians(240)
        tang = a + math.pi / 2
    else:
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -120, -300)
        a = math.radians(-60)
        tang = a - math.pi / 2
    ex, ey = x + r * math.cos(a), y + r * math.sin(a)
    for d in (0.5, -0.5):
        p.moveTo(ex, ey)
        p.lineTo(ex - head * math.cos(tang + d), ey - head * math.sin(tang + d))
    return p


def alarm_fn(x, y, j):
    """警报：镜头 j 第 0 拍起，三圈红色弧线从头部往外扩散，反复两轮。"""

    def fn(c, k, t):
        t0 = b.t_of(j, 0)
        dt = t - t0
        for i in range(3):
            ph = (dt * 1.1 - i * 0.22) % 1.0 if dt < 2.2 else 0.4 + i * 0.22
            r = 110 + 170 * ease_out(clamp01(ph))
            a = 1.0 - 0.6 * clamp01(ph)
            for side in (-1, 1):
                arc = skia.Path()
                start = -40 if side > 0 else 140
                arc.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), start, 80)
                c.drawPath(arc, marker(RED, 9, a))
        return None

    return fn


# ---------------------------------------------------------------- 开局：消息没回，聚会推了（镜头 1–6）

b.shot("同事没回消息", "灵魂拷问", view=(950, 850, 0.85))
L(stick(650, 1250, 0.9, "hold"), 0, 0.6, sfx="wood_high")
L(face(650, 1250, 0.9, "flat"), 0.6, 0.75)
L(phone(775, 1040), 0.75, 1.0, BLUE, 8)
L(bubble(1150, 640, 460, 130), 1, 1.5, BLACK, 8, sfx="pop")
T("方案发你了", 1150, 640, 58, k0=1.5)
T("10:02", 1150, 800, 50, k0=1.8, k1=2.2)
T("已读", 1330, 800, 50, RED, k0=2.2, k1=2.6, sfx="rim")
H(3, "wood_low", 0.6)

b.shot("两小时还没回", "灵魂拷问", view=(950, 850, 0.85))
L(clock(1250, 1080, 110), 0, 0.6, sfx="wood_high")
L(hands_at(1250, 1080, 110, 12, 0), 0.6, 0.8, RED, 10)
T("12:00", 1250, 1250, 56, RED, k0=1, sfx="pop")
T("还没回", 1250, 1350, 60, RED, k0=2, sfx="rim")

b.shot("他是不是烦我", "灵魂拷问", view=(2650, 850, 0.85))
L(stick(2350, 1250, 0.9, "down"), 0, 0.6, sfx="wood_high")
L(face(2350, 1250, 0.9, "sad"), 0.6, 0.75)
L(thought(2800, 640, 520, 160), 1, 1.6, BLACK, 8, sfx="pop")
T("他烦我了？", 2800, 640, 64, RED, k0=1.6)
T("上周哪句说错了", 2800, 960, 54, k0=2, k1=3.0, sfx="rim")

b.shot("周六聚餐想推掉", "灵魂拷问", view=(950, 1750, 0.85))
L(doc(650, 1700, 360, 260, 0), 0, 0.6, sfx="wood_high")
T("周六聚餐", 650, 1660, 60, k0=0.6)
T("来吗？", 650, 1760, 54, k0=1, sfx="pop")
L(stick(1200, 2150, 0.9, "hold"), 1.4, 1.9)
L(phone(1325, 1940), 1.9, 2.1, BLUE, 8)
T("回：有事", 1250, 1460, 64, BLUE, k0=2, k1=2.7, sfx="pop")
H(3, "wood_low", 0.6)

b.shot("周六一个人在家", "灵魂拷问", view=(2650, 1750, 0.85))
L(sofa(2450, 2020), 0, 0.8, sfx="wood_high")
L(stick(2450, 2040, 0.6, "hold"), 0.8, 1.2)
L(face(2450, 2040, 0.6, "sad"), 1.2, 1.35)
T("群里在晒合照", 2850, 1500, 58, BLUE, k0=1, k1=2, sfx="pop")
T("我在家", 2900, 1650, 60, RED, k0=2, k1=2.6, sfx="rim")
H(3, "wood_low", 0.6)

b.shot("怎么越来越躲人？", "灵魂拷问", view=(1800, 1300, 0.42), flashes=[0])
T("？", 1800, 1300, 380, RED, k0=0, k1=0.6, sfx="kick")
T("越孤单，越不想见人", 1800, 2320, 90, k0=1.0, k1=2.2, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "孤独是可耻的", view=(1050, 2980, 0.9))
L(book(750, 2980, 420, 280), 0, 1.0, sfx="wood_low")
T("《孤独是可耻的》", 800, 2740, 66, GREEN, k0=1.0, k1=2.0, sfx="pop")
T("卡乔波 · 帕特里克", 750, 3210, 48, k0=2.0, k1=2.9, sfx="pop")
H(3, "wood_high", 0.6)

GROUP = (420, 570, 720)
LONE = (1230, 3980)
b.shot("祖先离了群", "书中观点 · 离群", view=(900, 3700, 0.85))
for n, x in enumerate(GROUP):
    L(stick(x, 3980, 0.55), n * 0.3, n * 0.3 + 0.5, sfx="wood_high" if n == 0 else None)
L(stick(*LONE, 0.6), 1, 1.5, BLUE, sfx="pop")
L(arrow((830, 3900), (1080, 3900), 0, 36), 1.6, 1.9, GREEN, 8)
T("离群 = 危险", 600, 3460, 70, RED, k0=2, sfx="rim")
H(3, "wood_low", 0.6)

j_drop = b.shot("处处都得提防", "书中观点 · 警觉", view=(900, 3700, 0.85), shake=[0], flashes=[0])
b.custom(j_drop, 0, 4, alarm_fn(LONE[0], LONE[1] - 0.6 * 290, j_drop), sfx="kick")
T("警觉！", 1230, 3480, 100, RED, k0=1, k1=1.4, sfx="tom")
H(2, "tom", 0.7)
H(3, "pop", 0.6)

b.shot("孤单久了更警觉", "书中观点 · 警觉", view=(900, 3750, 0.85))
T("孤单久了", 1230, 4080, 52, k0=0, sfx="pop")
T("警报更灵", 1230, 4170, 58, RED, k0=1, sfx="pop")
L(underline(1100, 1360, 4210, 10, 30), 2, 2.4, RED, 7, sfx="ding")

b.shot("冷脸会被放大", "书中观点 · 往坏处想", view=(900, 3700, 0.85))
L(face(GROUP[1], 3980, 0.55, "flat"), 0, 0.3, BLACK, 8, sfx="pop")
L(magnifier(GROUP[1], 3980 - 0.55 * 290, 75), 1, 1.6, BLACK, 9, sfx="wood_high")
T("冷脸 ×10", 570, 3630, 60, RED, k0=2, sfx="rim")

CX, CY = 2680, 3300                                     # 回路图中心
NODES = {"top": (CX, 2860), "right": (CX + 420, CY), "bottom": (CX, 3740), "left": (CX - 420, CY)}
VIEW_LOOP = (CX, CY + 100, 0.78)
LABEL = {"top": "孤单", "right": "往坏处想", "bottom": "戒备躲人", "left": "别人疏远"}


def node_box(key, color=BLACK):
    x, y = NODES[key]
    return rect(x, y, 300 if key != "top" else 220, 120, 30)


b.shot("先是心里孤单", "书中观点 · 一个圈", view=VIEW_LOOP)
L(stick(CX, CY + 110, 0.55), 0, 0.5, BLUE, 9, sfx="wood_high")
L(face(CX, CY + 110, 0.55, "sad"), 0.5, 0.65, BLUE, 7)
L(node_box("top"), 1, 1.5, BLACK, 8, sfx="pop")
T(LABEL["top"], *NODES["top"], 62, BLUE, k0=2, sfx="pop")

ARROWS = [((CX + 120, 2880), (CX + 380, 3225)), ((CX + 380, 3375), (CX + 120, 3720)),
          ((CX - 120, 3720), (CX - 380, 3375)), ((CX - 380, 3225), (CX - 120, 2880))]

b.shot("把人往坏处想", "书中观点 · 往坏处想", view=VIEW_LOOP)
L(arrow(*ARROWS[0], -0.22, 44), 0, 0.5, BLACK, 8, sfx="wood_high")
L(node_box("right"), 1, 1.5, BLACK, 8, sfx="pop")
T(LABEL["right"], *NODES["right"], 58, RED, k0=2, sfx="pop")

b.shot("越来越戒备", "书中观点 · 戒备", view=VIEW_LOOP)
L(arrow(*ARROWS[1], -0.22, 44), 0, 0.5, BLACK, 8, sfx="wood_high")
L(node_box("bottom"), 1, 1.5, BLACK, 8, sfx="pop")
T(LABEL["bottom"], *NODES["bottom"], 58, RED, k0=2, sfx="pop")

b.shot("别人也走远了", "书中观点 · 疏远", view=VIEW_LOOP)
L(arrow(*ARROWS[2], -0.22, 44), 0, 0.5, BLACK, 8, sfx="wood_high")
L(node_box("left"), 1, 1.5, BLACK, 8, sfx="pop")
T(LABEL["left"], *NODES["left"], 58, k0=2, sfx="pop")

b.shot("又更孤单了", "书中观点 · 越转越紧", view=VIEW_LOOP, shake=[0])
L(arrow(*ARROWS[3], -0.22, 44), 0, 0.5, RED, 9, sfx="kick")
L(loop_arrow(CX, CY, 235, 44), 1, 1.8, RED, 9, sfx="wood_high")
T("越转越孤单", CX, 3900, 64, RED, k0=2, sfx="pop")
H(3, "ding", 0.6)

b.shot("这一环能拆", "书中观点 · 拆一环", view=VIEW_LOOP)
L(ring(*NODES["right"], 210, 110), 0, 0.6, GREEN, 9, sfx="wood_high")
T("能改", NODES["right"][0], 3470, 60, GREEN, k0=1, sfx="pop")
L(check(NODES["right"][0] + 110, 3460, 36), 2, 2.3, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 4950), (2650, 4950), (950, 5900), (2650, 5900)]
VIEW_EX = (1800, 5430, 0.355)
b.shot("身边也常见", "身边的例子", view=VIEW_EX)
T("身边的例子", 1800, 4410, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("开会时领导皱眉", "例子 · 职场", view=(950, 4950, 0.85))
L(stick(550, 5320, 0.75, "point", tie=True), 0, 0.6, sfx="wood_high")
L(face(550, 5320, 0.75, "sad"), 0.6, 0.75)
L(stick(1250, 5320, 0.75, "down"), 1, 1.5, BLUE, sfx="pop")
L(thought(1250, 4700, 340, 120), 2, 2.5, BLACK, 7, sfx="pop")
T("说我吧？", 1250, 4700, 56, RED, k0=2.5)

b.shot("一句都没说", "例子 · 职场", view=(950, 4950, 0.85))
T("我有个想法", 620, 4660, 54, k0=0, sfx="pop")
L(P((480, 4660), (760, 4660)), 1, 1.3, RED, 10, sfx="rim")
T("一整场没开口", 880, 4920, 58, RED, k0=2, k1=3, sfx="pop")

b.shot("群里约爬山", "例子 · 生活", view=(2650, 4950, 0.85))
L(big_phone(2650, 4980), 0, 0.8, sfx="wood_high")
L(bubble(2700, 4870, 320, 100, 1), 1, 1.4, BLUE, 7, sfx="pop")
T("周末爬山？", 2700, 4870, 50, BLUE, k0=1.4)
T("……", 2560, 5090, 60, k0=1.6, k1=1.9)
T("没人接", 3060, 4760, 56, RED, k0=2, k1=2.6, sfx="rim")
H(3, "wood_low", 0.6)

b.shot("撤回了，不再发", "例子 · 生活", view=(2650, 4950, 0.85))
L(cross(2700, 4870, 90), 0, 0.4, RED, 11, sfx="rim")
T("已撤回", 2650, 5180, 50, k0=1, sfx="pop")
T("下次不发了", 3060, 5150, 54, RED, k0=2, k1=2.9, sfx="pop")

b.shot("妈妈打电话来", "例子 · 家庭", view=(950, 5900, 0.85))
L(stick(600, 6250, 0.8, "hold", hair=True), 0, 0.6, sfx="wood_high")
L(face(600, 6250, 0.8, "smile"), 0.6, 0.75)
L(phone(710, 6060), 0.75, 1.0, BLUE, 8)
L(bubble(850, 5630, 380, 120, -1), 1, 1.4, BLACK, 7, sfx="pop")
T("最近咋样？", 850, 5630, 52, k0=1.4)
L(stick(1250, 6250, 0.8, "hold"), 2, 2.5, BLUE, sfx="pop")

b.shot("听着像催，挂了", "例子 · 家庭", view=(950, 5900, 0.85))
L(face(1250, 6250, 0.8, "sad"), 0, 0.3, BLUE, 8, sfx="pop")
T("又要催我", 1270, 5640, 56, RED, k0=1, sfx="pop")
T("3 分钟挂了", 930, 5860, 54, RED, k0=2, k1=2.9, sfx="rim")

b.shot("电梯里邻居问好", "例子 · 生活", view=(2650, 5900, 0.85))
L(elevator(2650, 5990, 580, 500), 0, 0.8, sfx="wood_high")
L(stick(2500, 6200, 0.65), 1, 1.4, sfx="pop")
L(stick(2800, 6200, 0.65, "up"), 1.4, 1.8, BLUE)
T("早！", 2860, 5880, 64, BLUE, k0=2, sfx="pop")

b.shot("低头装没看见", "例子 · 生活", view=(2650, 5900, 0.85))
L(phone(2560, 6050, 60, 100), 0, 0.3, BLACK, 7, sfx="pop")
L(face(2500, 6200, 0.65, "flat"), 0.3, 0.45, BLACK, 7)
T("下回他也不打了", 2650, 5610, 54, RED, k0=2, k1=3.2, sfx="rim")
H(1, "wood_low", 0.6)

b.shot("全在这个圈里", "身边的例子", view=VIEW_EX)
for n, (x, y) in enumerate(CARDS):
    L(loop_arrow(x + 480, y - 320, 70, 26), n * 0.8, n * 0.8 + 0.5, RED, 9, sfx="pop" if n % 2 == 0 else None)

b.shot("越躲越孤单", "身边的例子", view=VIEW_EX, shake=[0])
T("越躲，越孤单", 1800, 6470, 140, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 7380), (2650, 7380), (950, 8330), (2650, 8330)]
b.shot("想躲人时试试", "具体做法", view=(1800, 7850, 0.355))
T("想躲人时，这样做", 1800, 6830, 120, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 860, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先打个问号", "第一步 · 打问号", view=(950, 7380, 0.85))
T("① 先打个问号", 950, 7080, 76, BLUE, k0=0, sfx="pop")
T("他烦我", 820, 7330, 80, RED, k0=1, sfx="pop")
T("？", 1060, 7330, 130, RED, k0=2, k1=2.3, sfx="ding")

b.shot("也可能在忙", "第一步 · 打问号", view=(950, 7400, 0.85))
for n, w in enumerate(("在开会", "没看见", "在路上")):
    T(w, 600 + n * 350, 7520, 58, k0=n, sfx="pop")

b.shot("先别下结论", "第一步 · 打问号", view=(950, 7400, 0.85))
L(P((680, 7330), (960, 7330)), 0, 0.4, BLACK, 9, sfx="rim")
T("结论：晚点再下", 950, 7680, 56, GREEN, k0=1, sfx="pop")
L(check(1290, 7670, 36), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("核对一下事实", "第二步 · 对事实", view=(2650, 7380, 0.85))
T("② 核对事实", 2650, 7080, 76, BLUE, k0=0, sfx="pop")
T("看到的", 2380, 7220, 56, k0=1, sfx="pop")
T("猜的", 2920, 7220, 56, RED, k0=2, sfx="pop")
L(P((2650, 7170), (2650, 7380)), 3, 3.3, BLACK, 6)

b.shot("看到的只有没回", "第二步 · 对事实", view=(2650, 7380, 0.85))
T("没回消息", 2380, 7320, 56, k0=0, sfx="pop")
T("讨厌我", 2920, 7320, 56, RED, k0=1, sfx="pop")
L(P((2820, 7320), (3020, 7320)), 2, 2.3, RED, 10, sfx="rim")

b.shot("问一句就清楚", "第二步 · 对事实", view=(2650, 7450, 0.85))
L(bubble(2500, 7510, 400, 110, -1), 0, 0.5, BLACK, 7, sfx="pop")
T("下午聊两句？", 2500, 7510, 50, k0=0.5)
T("刚在开会！", 2850, 7700, 56, GREEN, k0=2, sfx="pop")
L(check(3110, 7690, 34), 3, 3.3, GREEN, 9, sfx="ding")

b.shot("先递个小善意", "第三步 · 小善意", view=(950, 8330, 0.85))
T("③ 先递个小善意", 950, 8030, 76, BLUE, k0=0, k1=1.2, sfx="pop")
L(heart(1300, 8190, 0.8), 2, 2.6, RED, 9, sfx="wood_high")

b.shot("顺手带杯咖啡", "第三步 · 小善意", view=(950, 8380, 0.85))
L(cup(560, 8350, 0.8), 0, 0.7, BLACK, 9, sfx="pop")
T("给同事带一杯", 950, 8350, 56, k0=1, sfx="pop")
L(check(1260, 8345, 34), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("聚餐先答应", "第三步 · 小善意", view=(950, 8400, 0.85))
T("周六聚餐：去！", 950, 8540, 60, GREEN, k0=0, k1=1.0, sfx="pop")
T("坐一小时也行", 950, 8650, 50, k0=2, sfx="pop")

b.shot("往好处想一步", "第四步 · 往好处想", view=(2650, 8330, 0.85))
T("④ 往好处想", 2650, 8030, 76, BLUE, k0=0, sfx="pop")
T("他大概在忙", 2650, 8200, 60, GREEN, k0=1, sfx="pop")
L(underline(2510, 2790, 8245, 10, 30), 2, 2.4, GREEN, 7, sfx="ding")

b.shot("圈就反着转", "第四步 · 往好处想", view=(2650, 8380, 0.85), shake=[0])
L(loop_arrow(2650, 8490, 170, 36, cw=False), 0, 0.8, GREEN, 9, sfx="kick")
T("靠近", 2650, 8490, 58, GREEN, k0=1, sfx="pop")
T("别人也靠近", 3050, 8330, 50, k0=2, sfx="pop")

b.shot("先打问号，再靠近", "一句话", view=(1800, 4100, 0.225))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 9150, 0.8))
T("你最近推掉过哪次聚会？", 1800, 9070, 72, RED, k0=0.5, k1=1.8)
T("下一讲：一个人的晚上，为什么管不住嘴？", 1800, 9230, 48, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "guard", "越孤单越戒备", "越孤单，为什么越不想见人？", ACC, b.shots,
                 [f"{BOOK}（转述）", "中译本：焦梦津译，中国人民大学出版社 2009",
                  "相关章节：第一部分 可耻的孤独（2 你所面临的潜危险、5 假象背后的真相 等）；第 14 章 个体困境的解药"],
                 "越孤单|越【不想见人】", 16,
                 ["书中观点均为转述：孤独是进化留下的信号，祖先离群就危险；长期孤独让人对社交威胁更警觉，更容易把别人往坏处想，"
                  "于是更戒备、更退缩，别人也就更疏远他，形成越转越孤独的循环；书末第 14 章的办法里有一条是往好处预期别人"
                  "（Expect the best），孤独的人容易先把人往坏处想。出处：John T. Cacioppo & William Patrick, Loneliness: "
                  "Human Nature and the Need for Social Connection (W. W. Norton, 2008)，中译本《孤独是可耻的》"
                  "（约翰·卡乔波、威廉·帕特里克著，焦梦津译，中国人民大学出版社 2009）。上屏均为转述，不是逐字引文。",
                  "同事已读不回、聚餐推掉、领导开会皱眉、群里约爬山没人接、妈妈打电话问近况、电梯里邻居问好均为现实场景示意，"
                  "不指向任何具体公司或个人；“祖先离群”“警报”“冷脸 ×10”与回路图为对书中观点的通俗化示意，时间与数字为示意，不是数据。",
                  "四步做法（先打个问号、核对事实、先递个小善意、往好处想一步）为据书中思路（含第 14 章 EASE 中的 "
                  "Extend yourself 与 Expect the best）整理的建议。"],
                 tags="#社恐 #人际关系")
    return b.attach(ep)
