"""04 越孤单越戒备（白板手绘版）：越孤单，为什么越不想见人？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
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
SQUARE_SHOT = 8

b = Board(size=(3600, 9800))


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


# ---------------------------------------------------------------- 开局：消息没回，聚会推了（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("消息已读，没人回", "灵魂拷问", (950, 900, 0.85))
L(stick(650, 1250, 0.9, "hold"), 0, 0.6, sfx="wood_high")
L(face(650, 1250, 0.9, "flat"), 0.6, 0.75)
L(phone(775, 1040), 0.75, 1.0, BLUE, 8)
L(bubble(1150, 640, 460, 130), 1, 1.5, BLACK, 8, sfx="pop")
T("方案发你了", 1150, 640, 58, k0=1.5)
T("已读", 1300, 790, 54, RED, k0=2, k1=2.4, sfx="rim")
L(clock(1250, 1080, 110), 3, 3.6, sfx="wood_high")
L(hands_at(1250, 1080, 110, 12, 0), 3.6, 3.8, RED, 10)
T("两小时没回", 1250, 900, 56, RED, k0=4.5, k1=5.6, sfx="pop")

scene("他是不是烦我了", "灵魂拷问", (2650, 900, 0.85))
L(stick(2350, 1250, 0.9, "down"), 0, 0.6, sfx="wood_high")
L(face(2350, 1250, 0.9, "sad"), 0.6, 0.75)
L(thought(2800, 640, 520, 160), 1.5, 2.1, BLACK, 8, sfx="pop")
T("他烦我了？", 2800, 640, 64, RED, k0=2, k1=2.9, sfx="pop")
T("上周哪句说错了", 2800, 960, 54, k0=4, k1=5.3, sfx="rim")

scene("推了聚餐，越来越躲人", "灵魂拷问", (950, 2050, 0.85), flashes=[4])
L(doc(620, 1770, 360, 240, 0), 0, 0.6, sfx="wood_high")
T("周六聚餐", 620, 1740, 58, k0=0.6, k1=1.0)
T("来吗？", 620, 1830, 52, k0=1, k1=1.4, sfx="pop")
T("回：有事", 620, 2010, 64, BLUE, k0=2, k1=2.7, sfx="pop")
L(sofa(1260, 2130, 420), 2, 2.8, sfx="wood_high")
L(stick(1260, 2150, 0.6, "hold"), 2.8, 3.2)
L(face(1260, 2150, 0.6, "sad"), 3.2, 3.35)
T("群里在晒合照", 1260, 1810, 54, BLUE, k0=3, k1=3.9, sfx="pop")
T("越孤单，", 640, 2300, 76, RED, k0=4, k1=4.6, sfx="kick")
T("越不想见人？", 700, 2410, 76, RED, k0=4.6, k1=5.8)

# ---------------------------------------------------------------- 书中观点（场景 4–9）

GROUP = (420, 570, 720)
LONE = (1230, 3980)
VIEW_BOOK = (1050, 3480, 0.72)
scene("书里说，离群就危险", "孤独是可耻的 · 书中观点", VIEW_BOOK)
L(book(640, 3010, 360, 240), 0, 1.0, sfx="wood_low")
T("《孤独是可耻的》", 1200, 2960, 58, GREEN, k0=1, k1=2.2, sfx="pop")
T("卡乔波 · 帕特里克", 1200, 3070, 44, k0=2.2, k1=2.9)
for n, x in enumerate(GROUP):
    L(stick(x, 3980, 0.55), 3 + n * 0.3, 3.5 + n * 0.3, sfx="wood_high" if n == 0 else None)
L(stick(*LONE, 0.6), 4, 4.5, BLUE, sfx="pop")
L(arrow((830, 3900), (1080, 3900), 0, 36), 4.5, 4.8, GREEN, 8)
T("离群 = 危险", 560, 3460, 70, RED, k0=5, k1=5.9, sfx="rim")

VIEW_ALARM = (1050, 3500, 0.74)
j_drop = scene("孤单久了，警报更灵", "书中观点 · 警觉", VIEW_ALARM, shake=[0], flashes=[0])
b.custom(j_drop, 0, 4, alarm_fn(LONE[0], LONE[1] - 0.6 * 290, j_drop), sfx="kick")
T("警觉！", 1230, 3480, 100, RED, k0=1, k1=1.4, sfx="tom")
H(2, "tom", 0.7)
T("孤单久了，警报更灵", 920, 4090, 56, k0=3, k1=4.6, sfx="pop")
L(underline(1050, 1400, 4130, 10, 30), 5, 5.5, RED, 7, sfx="ding")

scene("一点冷脸，被放大", "书中观点 · 往坏处想", VIEW_ALARM)
L(face(GROUP[1], 3980, 0.55, "flat"), 0, 0.3, BLACK, 8, sfx="pop")
L(magnifier(GROUP[1], 3980 - 0.55 * 290, 75), 1, 1.6, BLACK, 9, sfx="wood_high")
T("冷脸 ×10", 570, 3630, 60, RED, k0=2.5, k1=3.4)
H(3, "rim")
L(underline(440, 700, 3670, 10, 30), 4, 4.4, RED, 7, sfx="ding")

CX, CY = 2680, 3300                                     # 回路图中心
NODES = {"top": (CX, 2860), "right": (CX + 420, CY), "bottom": (CX, 3740), "left": (CX - 420, CY)}
VIEW_LOOP = (CX + 60, CY + 100, 0.78)
LABEL = {"top": "孤单", "right": "往坏处想", "bottom": "戒备躲人", "left": "别人疏远"}
ARROWS = [((CX + 120, 2880), (CX + 380, 3225)), ((CX + 380, 3375), (CX + 120, 3720)),
          ((CX - 120, 3720), (CX - 380, 3375)), ((CX - 380, 3225), (CX - 120, 2880))]


def node_box(key):
    x, y = NODES[key]
    return rect(x, y, 300 if key != "top" else 220, 120, 30)


scene("孤单了，就往坏处想", "书中观点 · 一个圈", VIEW_LOOP)
L(stick(CX, CY + 110, 0.55), 0, 0.5, BLUE, 9, sfx="wood_high")
L(face(CX, CY + 110, 0.55, "sad"), 0.5, 0.65, BLUE, 7)
L(node_box("top"), 1, 1.4, BLACK, 8, sfx="pop")
T(LABEL["top"], *NODES["top"], 62, BLUE, k0=1.4, k1=1.9)
L(arrow(*ARROWS[0], -0.22, 44), 2, 2.5, BLACK, 8, sfx="wood_high")
L(node_box("right"), 3, 3.4, BLACK, 8, sfx="pop")
T(LABEL["right"], *NODES["right"], 58, RED, k0=3.4, k1=4.1)
L(arrow(*ARROWS[1], -0.22, 44), 4, 4.5, BLACK, 8, sfx="wood_high")
L(node_box("bottom"), 5, 5.3, BLACK, 8, sfx="pop")
T(LABEL["bottom"], *NODES["bottom"], 58, RED, k0=5.3, k1=5.9)

scene("别人走远，更孤单", "书中观点 · 越转越紧", VIEW_LOOP, shake=[2])
L(arrow(*ARROWS[2], -0.22, 44), 0, 0.5, BLACK, 8, sfx="wood_high")
L(node_box("left"), 1, 1.4, BLACK, 8, sfx="pop")
T(LABEL["left"], *NODES["left"], 58, k0=1.4, k1=2.0)
L(arrow(*ARROWS[3], -0.22, 44), 2, 2.5, RED, 9, sfx="kick")
L(loop_arrow(CX, CY, 235, 44), 3, 3.8, RED, 9, sfx="wood_high")
T("越转越孤单", CX, 3900, 64, RED, k0=4, k1=4.9, sfx="pop")
H(5, "ding", 0.6)

scene("往坏处想这环能拆", "书中观点 · 拆一环", VIEW_LOOP)
L(ring(*NODES["right"], 210, 110), 0, 0.6, GREEN, 9, sfx="wood_high")
T("能改", NODES["right"][0], 3470, 60, GREEN, k0=1.5, k1=2.0)
H(2, "pop")
L(check(NODES["right"][0] + 110, 3460, 36), 3, 3.3, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 5200), (2650, 5200), (950, 6150), (2650, 6150)]
VIEW_EX = (1800, 5980, 0.355)
scene("身边也常见", "身边的例子", VIEW_EX)
T("身边的例子", 1800, 4660, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 2 + n * 0.8, 2.5 + n * 0.8, GREEN, 8, sfx="wood_high" if n in (0, 2) else None)

scene("领导一皱眉，我闭嘴了", "例子 · 职场", (950, 5200, 0.85))
L(stick(550, 5570, 0.75, "point", tie=True), 0, 0.6, sfx="wood_high")
L(face(550, 5570, 0.75, "sad"), 0.6, 0.75)
L(stick(1130, 5570, 0.75, "down"), 1, 1.5, BLUE, sfx="pop")
L(thought(1200, 4950, 340, 120), 2, 2.5, BLACK, 7, sfx="pop")
T("说我吧？", 1200, 4950, 56, RED, k0=2.5, k1=3.0)
T("我有个想法", 620, 4910, 54, k0=3, k1=3.9, sfx="pop")
L(P((480, 4910), (760, 4910)), 4, 4.3, RED, 10, sfx="rim")
T("一整场没开口", 880, 5170, 58, RED, k0=5, k1=5.9, sfx="pop")

scene("约爬山没人接，撤了", "例子 · 生活", (2650, 5200, 0.85))
L(big_phone(2650, 5230), 0, 0.8, sfx="wood_high")
L(bubble(2700, 5120, 320, 100, 1), 1, 1.4, BLUE, 7, sfx="pop")
T("周末爬山？", 2700, 5120, 50, BLUE, k0=1.4, k1=1.9)
T("……", 2560, 5340, 60, k0=1.9, k1=2.1)
T("没人接", 3060, 5010, 56, RED, k0=2.5, k1=3.0)
H(3, "rim")
L(cross(2700, 5120, 90), 3, 3.4, RED, 11)
T("已撤回", 2650, 5430, 50, k0=4, k1=4.6, sfx="pop")
T("下次不发了", 3060, 5280, 54, RED, k0=5, k1=5.9, sfx="pop")

scene("妈妈问近况，听着像催", "例子 · 家庭", (950, 6150, 0.85))
L(stick(600, 6500, 0.8, "hold", hair=True), 0, 0.6, sfx="wood_high")
L(face(600, 6500, 0.8, "smile"), 0.6, 0.75)
L(phone(710, 6310), 0.75, 1.0, BLUE, 8)
L(bubble(850, 5880, 380, 120, -1), 1, 1.4, BLACK, 7, sfx="pop")
T("最近咋样？", 850, 5880, 52, k0=1.4, k1=1.9)
L(stick(1130, 6500, 0.8, "hold"), 2, 2.5, BLUE, sfx="pop")
L(face(1130, 6500, 0.8, "sad"), 2.5, 2.7, BLUE, 8)
T("又要催我", 1270, 5890, 56, RED, k0=3, k1=3.7, sfx="pop")
T("三分钟就挂了", 930, 6110, 54, RED, k0=4.5, k1=5.6)
H(5, "rim")

scene("邻居问好，我低头", "例子 · 生活", (2650, 6150, 0.85))
L(elevator(2650, 6240, 580, 500), 0, 0.8, sfx="wood_high")
L(stick(2500, 6450, 0.65), 1, 1.4, sfx="pop")
L(stick(2800, 6450, 0.65, "up"), 1.4, 1.8, BLUE)
T("早！", 2860, 6130, 64, BLUE, k0=2, k1=2.4, sfx="pop")
L(phone(2560, 6300, 60, 100), 3, 3.3, BLACK, 7, sfx="pop")
L(face(2500, 6450, 0.65, "flat"), 3.3, 3.45, BLACK, 7)
T("下回他也不打了", 2650, 5860, 54, RED, k0=4, k1=5.3, sfx="rim")

scene("四件事，都在圈里转", "身边的例子", VIEW_EX, shake=[4])
for n, (x, y) in enumerate(CARDS):
    L(loop_arrow(x + 480, y - 320, 70, 26), n, n + 0.5, RED, 9, sfx="pop" if n % 2 == 0 else "wood_high")
T("越躲，越孤单", 1800, 6720, 140, RED, k0=4, k1=4.8, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 7550), (2650, 7550), (950, 8650), (2650, 8650)]

scene("先打个问号，也许在忙", "第一步 · 打问号", (950, 7570, 0.85))
L(rect(*SOL[0], 1200, 860, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("① 先打个问号", 950, 7250, 76, BLUE, k0=0.6, k1=1.6)
T("他烦我", 820, 7470, 80, RED, k0=2, k1=2.5, sfx="pop")
T("？", 1060, 7470, 130, RED, k0=2.6, k1=2.9)
for n, w in enumerate(("在开会", "没看见", "在路上")):
    T(w, 600 + n * 350, 7690, 58, k0=3 + n * 0.5, k1=3.4 + n * 0.5, sfx="pop" if n == 0 else None)
L(P((680, 7470), (960, 7470)), 5, 5.4, BLACK, 9, sfx="rim")
T("结论晚点下", 950, 7850, 56, GREEN, k0=5.4, k1=6.0)

scene("分清看到的和猜的", "第二步 · 对事实", (2650, 7570, 0.85))
L(rect(*SOL[1], 1200, 860, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("② 核对事实", 2650, 7250, 76, BLUE, k0=0.6, k1=1.5)
T("看到的", 2380, 7390, 56, k0=1.5, k1=2.0)
T("猜的", 2920, 7390, 56, RED, k0=2, k1=2.4, sfx="pop")
L(P((2650, 7340), (2650, 7550)), 2.4, 2.7, BLACK, 6)
T("没回消息", 2380, 7490, 56, k0=3, k1=3.6, sfx="pop")
T("讨厌我", 2920, 7490, 56, RED, k0=3.6, k1=4.0)
L(P((2820, 7490), (3020, 7490)), 4, 4.3, RED, 10, sfx="rim")
L(bubble(2450, 7670, 380, 110, -1), 4.3, 4.8, BLACK, 7)
T("下午聊两句？", 2450, 7670, 50, k0=4.8, k1=5.4)
T("刚在开会！", 2830, 7790, 56, GREEN, k0=5, k1=5.8, sfx="ding")

scene("先递个小善意", "第三步 · 小善意", (950, 8720, 0.85))
L(rect(*SOL[2], 1200, 860, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("③ 先递个小善意", 950, 8350, 76, BLUE, k0=0.6, k1=1.8)
L(heart(1300, 8510, 0.8), 2, 2.5, RED, 9, sfx="pop")
L(cup(560, 8670, 0.8), 2.5, 3.0, BLACK, 9)
T("给同事带一杯", 950, 8670, 56, k0=3, k1=3.8, sfx="pop")
T("周六聚餐：去！", 950, 8860, 60, GREEN, k0=4, k1=4.8, sfx="pop")
T("坐一小时也行", 950, 8970, 50, k0=5, k1=5.8, sfx="ding")

scene("往好处想，圈就反着转", "第四步 · 往好处想", (2650, 8720, 0.85), shake=[3])
L(rect(*SOL[3], 1200, 860, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("④ 往好处想", 2650, 8350, 76, BLUE, k0=0.6, k1=1.5)
T("他大概在忙", 2650, 8520, 60, GREEN, k0=1.5, k1=2.3)
L(underline(2510, 2790, 8565, 10, 30), 2, 2.4, GREEN, 7, sfx="ding")
L(loop_arrow(2650, 8810, 170, 36, cw=False), 3, 3.8, GREEN, 9, sfx="kick")
T("靠近", 2650, 8810, 58, GREEN, k0=4, k1=4.5, sfx="pop")
T("别人也靠近", 3050, 8650, 50, k0=5, k1=5.8, sfx="pop")

scene("先打问号，再靠近", "一句话", (1800, 4150, 0.225))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 9500, 0.8))
H(0, "cymbal", 0.5)
T("你最近推掉过哪次聚会？", 1800, 9420, 72, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：一个人的晚上，为什么管不住嘴？", 1800, 9580, 48, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "guard", "越孤单越戒备", "越孤单，为什么越不想见人？", ACC, b.shots,
                 [f"{BOOK}（转述）", "中译本：焦梦津译，中国人民大学出版社 2009",
                  "相关章节：第一部分 可耻的孤独（2 你所面临的潜危险、5 假象背后的真相 等）；第 14 章 个体困境的解药"],
                 "越孤单|越【不想见人】", 8,
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
