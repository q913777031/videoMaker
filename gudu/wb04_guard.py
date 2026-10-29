"""04 越孤单越戒备（白板手绘版）：越孤单，为什么越不想见人？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒。
叙事：打工人切身问题开局（同事消息已读两小时没回，心里嘀咕“他烦我了？”；周六聚餐的邀请回了句“有事”，
一个人在家看群里晒合照）→ 书中观点（亮书《孤独是可耻的》、卡乔波；祖先离群就危险，所以孤单的人对冷脸格外警觉；
孤单久了警报更灵，一点冷脸被放大；画成一个圈：孤单 → 往坏处想 → 戒备躲人 → 别人疏远 → 更孤单，往坏处想这一环能拆）→
身边的例子（职场：领导开会皱眉，以为在说自己，一句没说；家庭：妈妈打电话问近况，听着像催，草草挂掉；
生活：电梯里邻居打招呼，低头装没看见；三件都是先往坏处想）→
具体做法（先打个问号、往好处想 / 核对事实 / 先递个小善意，圈就反着转）→ 评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, 2008；
中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               doc, face, hands_at, join, marker, rect, stick, underline)
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#5A6FA8"
SQUARE_SHOT = 6

b = Board(size=(3600, 12000))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
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


# ---------------------------------------------------------------- 开局：消息没回，聚会推了（场景 1–2）
# 慢速讲解节奏：场景 1 = 2 小节（第 0–6 拍画完），场景 2–13 = 3 小节（第 0–8 拍画完，最后 4 拍停住），场景 14 = 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


scene("已读不回，他烦我了？", "灵魂拷问", (950, 900, 0.85), bars=2)
L(stick(650, 1250, 0.9, "hold"), 0, 0.8, sfx="wood_high")
L(face(650, 1250, 0.9, "flat"), 0.8, 1.0)
L(bubble(1150, 640, 460, 130), 1, 1.7, BLACK, 8, sfx="pop")
T("方案发你了", 1150, 640, 58, k0=1.7, k1=2.9)
T("已读", 1300, 790, 54, RED, k0=3, k1=3.6, sfx="rim")
L(thought(620, 680, 400, 140), 4, 4.7, BLACK, 8, sfx="pop")
T("他烦我了？", 620, 680, 60, RED, k0=4.7, k1=5.9)

scene("推了聚餐，越来越躲人", "灵魂拷问", (2650, 900, 0.85))
L(doc(2320, 620, 360, 240, 0), 0, 0.9, sfx="wood_high")
T("周六聚餐", 2320, 590, 58, k0=1, k1=2.0, sfx="pop")
T("来吗？", 2320, 680, 52, k0=2, k1=2.75)
T("回：有事", 2320, 860, 64, BLUE, k0=3, k1=4.0, sfx="pop")
L(sofa(2960, 980, 420), 4, 4.9, sfx="wood_high")
L(stick(2960, 1000, 0.6, "hold"), 5, 5.6)
L(face(2960, 1000, 0.6, "sad"), 5.6, 5.8)
T("越孤单，", 2340, 1150, 76, RED, k0=6, k1=7.0, sfx="kick")
T("越不想见人？", 2400, 1260, 76, RED, k0=7, k1=8.0)

# ---------------------------------------------------------------- 书中观点（场景 3–7）

GROUP = (420, 570, 720)
LONE = (1230, 3980)
VIEW_BOOK = (1050, 3480, 0.72)
scene("书里说，离群就危险", "孤独是可耻的 · 书中观点", VIEW_BOOK)
L(book(640, 3010, 360, 240), 0, 1.0, sfx="wood_low")
T("《孤独是可耻的》", 1200, 2960, 58, GREEN, k0=1, k1=3.0, sfx="pop")
for n, x in enumerate(GROUP):
    L(stick(x, 3980, 0.55), 3 + n * 0.5, 3.8 + n * 0.5, sfx="wood_high" if n == 0 else None)
L(stick(*LONE, 0.6), 5, 5.9, BLUE, sfx="pop")
L(arrow((830, 3900), (1080, 3900), 0, 36), 6, 6.8, GREEN, 8)
T("离群 = 危险", 560, 3460, 70, RED, k0=7, k1=8.0, sfx="rim")

VIEW_ALARM = (1050, 3500, 0.74)
j_drop = scene("孤单久了，警报更灵", "书中观点 · 警觉", VIEW_ALARM, shake=[0], flashes=[0])
b.custom(j_drop, 0, 4, alarm_fn(LONE[0], LONE[1] - 0.6 * 290, j_drop), sfx="kick")
T("孤单久了，警报更灵", 920, 4090, 56, k0=1, k1=3.2, sfx="pop")
L(underline(940, 1190, 4130, 10, 30), 3.3, 4.0, RED, 7)
L(face(GROUP[1], 3980, 0.55, "flat"), 4, 4.8, BLACK, 8, sfx="pop")
L(magnifier(GROUP[1], 3980 - 0.55 * 290, 75), 5, 6.0, BLACK, 9, sfx="wood_high")
T("冷脸 ×10", 570, 3630, 60, RED, k0=6, k1=7.5, sfx="rim")

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
L(stick(CX, CY + 110, 0.55), 0, 0.8, BLUE, 9, sfx="wood_high")
L(face(CX, CY + 110, 0.55, "sad"), 0.8, 1.0, BLUE, 7)
L(node_box("top"), 1, 1.8, BLACK, 8, sfx="pop")
T(LABEL["top"], *NODES["top"], 62, BLUE, k0=1.8, k1=2.6)
L(arrow(*ARROWS[0], -0.22, 44), 3, 3.8, BLACK, 8, sfx="wood_high")
L(node_box("right"), 4, 4.8, BLACK, 8, sfx="pop")
T(LABEL["right"], *NODES["right"], 58, RED, k0=4.8, k1=5.8)

scene("一躲，别人就走远", "书中观点 · 越转越紧", VIEW_LOOP, shake=[6])
L(arrow(*ARROWS[1], -0.22, 44), 0, 0.8, BLACK, 8, sfx="wood_high")
L(node_box("bottom"), 1, 1.8, BLACK, 8, sfx="pop")
T(LABEL["bottom"], *NODES["bottom"], 58, RED, k0=1.8, k1=2.8)
L(arrow(*ARROWS[2], -0.22, 44), 3, 3.8, BLACK, 8, sfx="wood_high")
L(node_box("left"), 4, 4.8, BLACK, 8, sfx="pop")
T(LABEL["left"], *NODES["left"], 58, k0=4.8, k1=5.8)
L(arrow(*ARROWS[3], -0.22, 44), 6, 6.8, RED, 9, sfx="kick")

scene("往坏处想，这环能拆", "书中观点 · 拆一环", VIEW_LOOP)
L(loop_arrow(CX, CY, 235, 44), 0, 1.0, RED, 9, sfx="wood_high")
T("越转越孤单", CX, 3900, 64, RED, k0=1, k1=2.3, sfx="pop")
L(ring(*NODES["right"], 210, 110), 3, 3.9, GREEN, 9, sfx="wood_high")
T("能改", NODES["right"][0], 3470, 60, GREEN, k0=4, k1=4.8, sfx="pop")
L(check(NODES["right"][0] + 110, 3460, 36), 5, 5.8, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

scene("领导一皱眉，我闭嘴了", "例子 · 职场", (950, 5200, 0.85))
L(stick(550, 5570, 0.75, "point", tie=True), 0, 0.8, sfx="wood_high")
L(face(550, 5570, 0.75, "sad"), 0.8, 1.0)
L(stick(1130, 5570, 0.75, "down"), 1, 1.8, BLUE, sfx="pop")
L(thought(1200, 4950, 340, 120), 2, 2.7, BLACK, 7, sfx="pop")
T("说我吧？", 1200, 4950, 56, RED, k0=2.7, k1=3.7)
T("我有个想法", 620, 4910, 54, k0=4, k1=5.25, sfx="pop")
L(P((480, 4910), (760, 4910)), 6, 6.8, RED, 10, sfx="rim")

scene("妈妈问近况，听着像催", "例子 · 家庭", (950, 6550, 0.85))
L(stick(600, 6900, 0.8, "hold", hair=True), 0, 0.8, sfx="wood_high")
L(face(600, 6900, 0.8, "smile"), 0.8, 1.0)
L(phone(710, 6710), 1, 1.6, BLUE, 8)
L(bubble(850, 6280, 380, 120, -1), 2, 2.7, BLACK, 7, sfx="pop")
T("最近咋样？", 850, 6280, 52, k0=2.7, k1=3.9)
L(stick(1130, 6900, 0.8, "hold"), 4, 4.7, BLUE, sfx="pop")
L(face(1130, 6900, 0.8, "sad"), 4.7, 4.9, BLUE, 8)
T("又要催我", 1270, 6290, 56, RED, k0=5, k1=6.0, sfx="pop")
T("三分钟就挂了", 930, 6510, 54, RED, k0=6, k1=7.5, sfx="rim")

scene("邻居问好，我低头", "例子 · 生活", (2650, 6150, 0.85), shake=[5])
L(elevator(2650, 6240, 580, 500), 0, 0.9, sfx="wood_high")
L(stick(2800, 6450, 0.65, "up"), 1, 1.8, BLUE, sfx="pop")
T("早！", 2860, 6130, 64, BLUE, k0=2, k1=2.8, sfx="pop")
L(stick(2500, 6450, 0.65), 3, 3.6, sfx="wood_high")
L(phone(2560, 6300, 60, 100), 3.6, 3.9, BLACK, 7)
L(face(2500, 6450, 0.65, "flat"), 3.9, 4.1, BLACK, 7)
T("都是先往坏处想", 2650, 6640, 76, RED, k0=5, k1=6.75, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

SOL = [(950, 7850), (2650, 7850), (950, 9180)]

scene("先打个问号，往好处想", "第一步 · 打问号", (950, 7870, 0.85))
L(rect(*SOL[0], 1200, 860, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("① 先打个问号", 950, 7550, 76, BLUE, k0=1, k1=2.5, sfx="pop")
T("他烦我？", 950, 7750, 80, RED, k0=3, k1=4.0, sfx="pop")
T("在开会", 700, 7960, 58, k0=4, k1=4.8, sfx="pop")
T("没看见", 1200, 7960, 58, k0=5, k1=5.8, sfx="pop")
T("他大概在忙", 950, 8160, 64, GREEN, k0=6, k1=7.25, sfx="ding")

scene("分清看到的和猜的", "第二步 · 对事实", (2650, 7870, 0.85))
L(rect(*SOL[1], 1200, 860, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("② 核对事实", 2650, 7550, 76, BLUE, k0=1, k1=2.25, sfx="pop")
T("看到的：没回消息", 2650, 7730, 58, k0=3, k1=4.8, sfx="pop")
T("猜的：讨厌我", 2650, 7870, 58, RED, k0=5, k1=6.4, sfx="rim")
T("刚在开会！", 2650, 8080, 66, GREEN, k0=7, k1=8.0, sfx="ding")

scene("先递个小善意，圈反着转", "第三步 · 小善意", (950, 9250, 0.85), shake=[7])
L(rect(*SOL[2], 1200, 860, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("③ 先递个小善意", 950, 8880, 76, BLUE, k0=1, k1=2.75, sfx="pop")
T("周六聚餐：去！", 820, 9090, 62, GREEN, k0=3, k1=4.75, sfx="pop")
T("坐一小时也行", 820, 9230, 52, k0=5, k1=6.5, sfx="ding")
L(loop_arrow(1280, 9420, 130, 34, cw=False), 7, 8.0, GREEN, 9, sfx="kick")

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：先拉远看全板，再推到评论区

VIEW_FULL = (1800, 5500, 0.11)
VIEW_COMMENT = (1800, 10650, 0.8)
_now = [0.0]                                            # 相机取景时刻（build() 里由 ep.shot_at 记录）


class _PullPush(tuple):
    """收尾场景的相机：第 0–4 拍停在全板，第 4 拍起用 1.1 秒推到评论区；本身的值为评论区视角。"""

    def __getitem__(self, i):
        j = len(b.shots) - 1
        t0 = b.t_of(j, 4)
        f = ease_in_out(clamp01((_now[0] - t0) / 1.1))
        if i == 2:
            return math.exp(lerp(math.log(VIEW_FULL[2]), math.log(VIEW_COMMENT[2]), f))
        return lerp(VIEW_FULL[i], VIEW_COMMENT[i], f)


scene("先打问号，再靠近", "评论区见", _PullPush(VIEW_COMMENT), bars=4)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你最近推掉过哪次聚会？", 1800, 10570, 72, RED, k0=7, k1=9.75, sfx="pop")
T("下一讲：一个人的晚上，为什么管不住嘴？", 1800, 10730, 48, k0=10, k1=14.5, sfx="wood_high")
b.hit(len(b.shots) - 1, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "guard", "越孤单越戒备", "越孤单，为什么越不想见人？", ACC, b.shots,
                 [f"{BOOK}（转述）", "中译本：焦梦津译，中国人民大学出版社 2009",
                  "相关章节：第一部分 可耻的孤独（2 你所面临的潜危险、5 假象背后的真相 等）；第 14 章 个体困境的解药"],
                 "越孤单|越【不想见人】", 6,
                 ["书中观点均为转述：孤独是进化留下的信号，祖先离群就危险；长期孤独让人对社交威胁更警觉，更容易把别人往坏处想，"
                  "于是更戒备、更退缩，别人也就更疏远他，形成越转越孤独的循环；书末第 14 章的办法里有一条是往好处预期别人"
                  "（Expect the best），孤独的人容易先把人往坏处想。出处：John T. Cacioppo & William Patrick, Loneliness: "
                  "Human Nature and the Need for Social Connection (W. W. Norton, 2008)，中译本《孤独是可耻的》"
                  "（约翰·卡乔波、威廉·帕特里克著，焦梦津译，中国人民大学出版社 2009）。上屏均为转述，不是逐字引文。",
                  "同事已读不回、聚餐推掉、领导开会皱眉、妈妈打电话问近况、电梯里邻居问好均为现实场景示意，"
                  "不指向任何具体公司或个人；“祖先离群”“警报”“冷脸 ×10”与回路图为对书中观点的通俗化示意，时间与数字为示意，不是数据。",
                  "三步做法（先打个问号、往好处想一步；核对事实；先递个小善意）为据书中思路（含第 14 章 EASE 中的 "
                  "Extend yourself 与 Expect the best）整理的建议。"],
                 tags="#社恐 #人际关系")
    ep = b.attach(ep)
    shot_at = ep.shot_at

    def timed_shot_at(T):
        _now[0] = T                                     # 记下取景时刻，供收尾场景的拉远—推近相机使用
        return shot_at(T)

    ep.shot_at = timed_shot_at
    return ep
