"""07 人是社会动物（白板手绘版）：被同事晾在一边，为什么那么难受？

叙事：打工人切身问题开局（中午同事约好去吃饭没叫你 → 下午在工作群里发了句话半天没人接 → 心里堵）→
书中观点（亮书《孤独是可耻的》；祖先靠抱团过日子，落单就危险，人是社会动物；书中讨论的“网络传球”实验：
三个人在屏幕上传球，渐渐不再传给其中一个人；被冷落的痛和身体疼痛在大脑里有重叠；画成一张图：被晾 → 疼 → 提醒你回到人群）→
身边的例子（开会挨个夸人唯独跳过你、朋友聚会的照片才知道没叫你、年夜饭亲戚聊得热闹你插不上嘴、孩子被同学冷落回家发脾气）→
具体做法（认下难受别硬憋 / 找件事一起干 / 先帮别人个小忙 / 往好处猜，下回你来约）→ 评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, 2008，
第二部分“从自私的基因到社会动物”，第 11 章“协作是人类进化的王道”等；书中讨论的艾森伯格等 2003 年“网络传球”实验；
中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               desk, doc, face, hands_at, join, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#C0603A"
SQUARE_SHOT = 13

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


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12 if w < 200 else 40), P((x - w * 0.17, y + h / 2 - h * 0.13),
                                                           (x + w * 0.17, y + h / 2 - h * 0.13)))


def cup(x, y, s=1.0) -> skia.Path:
    """咖啡杯：(x, y) 为杯身中心。"""
    body = P((x - 60 * s, y - 75 * s), (x - 48 * s, y + 75 * s), (x + 48 * s, y + 75 * s), (x + 60 * s, y - 75 * s),
             close=True)
    handle = skia.Path()
    handle.addArc(skia.Rect.MakeXYWH(x + 30 * s, y - 45 * s, 60 * s, 70 * s), -90, 180)
    parts = [body, handle, P((x - 57 * s, y - 45 * s), (x + 57 * s, y - 45 * s))]
    for dx in (-22, 22):
        st = skia.Path()
        st.moveTo(x + dx * s, y - 95 * s)
        st.quadTo(x + (dx - 22) * s, y - 125 * s, x + dx * s, y - 150 * s)
        st.quadTo(x + (dx + 22) * s, y - 175 * s, x + dx * s, y - 200 * s)
        parts.append(st)
    return join(*parts)


def fire(x, y, s=1.0) -> skia.Path:
    """篝火：两根交叉的柴 + 三簇火苗，(x, y) 为地面中点。"""
    logs = join(P((x - 110 * s, y), (x + 110 * s, y - 50 * s)), P((x + 110 * s, y), (x - 110 * s, y - 50 * s)))
    parts = [logs]
    for dx, h in ((-45, 150), (0, 220), (45, 140)):
        f = skia.Path()
        f.moveTo(x + (dx - 35) * s, y - 40 * s)
        f.quadTo(x + (dx - 45) * s, y - (40 + h * 0.6) * s, x + dx * s, y - (40 + h) * s)
        f.quadTo(x + (dx + 45) * s, y - (40 + h * 0.6) * s, x + (dx + 35) * s, y - 40 * s)
        parts.append(f)
    return join(*parts)


def brain(x, y, r=160) -> skia.Path:
    """大脑：起伏的轮廓 + 中线 + 几道褶。"""
    pts = []
    for i in range(48):
        a = i / 48 * 2 * math.pi
        rr = r * (1 + 0.07 * math.sin(a * 9))
        pts.append((x + rr * math.cos(a) * 1.2, y + rr * math.sin(a) * 0.82))
    out = P(*pts, close=True)
    mid = skia.Path()
    mid.moveTo(x, y - r * 0.78)
    mid.quadTo(x - 25, y, x, y + r * 0.78)
    folds = []
    for sx in (-1, 1):
        f = skia.Path()
        f.moveTo(x + sx * r * 0.25, y - r * 0.35)
        f.quadTo(x + sx * r * 0.7, y - r * 0.5, x + sx * r * 0.85, y - r * 0.1)
        folds.append(f)
        g = skia.Path()
        g.moveTo(x + sx * r * 0.3, y + r * 0.35)
        g.quadTo(x + sx * r * 0.6, y + r * 0.1, x + sx * r * 0.9, y + r * 0.3)
        folds.append(g)
    return join(out, mid, *folds)


def box(x, y, w=260, h=150) -> skia.Path:
    return join(rect(x, y, w, h, 8), P((x - w / 2, y - h / 2 + 40), (x + w / 2, y - h / 2 + 40)))


def spot_fn(x, y, r, color=RED, alpha=0.45):
    def fn(c, k, t):
        K.dot(c, x, y, r * k, color, alpha)
        return None

    return fn


def overlap_fn(c1, c2, color=RED, alpha=0.4):
    """两圆重叠部分慢慢填色。c1、c2 为 (x, y, r)。"""

    def fn(c, k, t):
        c.save()
        c.clipPath(circle(*c1), skia.ClipOp.kIntersect, True)
        c.drawPath(circle(*c2), K.paint(color, alpha * k))
        c.restore()
        return None

    return fn


# ---------------------------------------------------------------- 开局：被晾在一边（镜头 1–6）

b.shot("中午十二点", "灵魂拷问", view=(950, 850, 0.85))
L(clock(560, 640, 120), 0, 0.6, sfx="wood_high")
L(hands_at(560, 640, 120, 12, 0), 0.6, 0.8, RED, 12)
T("12:00", 560, 850, 64, RED, k0=1, sfx="pop")
L(desk(950, 1100, 360), 2, 2.6, sfx="wood_high")
L(stick(1250, 1300, 0.75), 2.6, 3.0)

b.shot("同事约着去吃饭", "灵魂拷问", view=(2650, 850, 0.85))
for n, x in enumerate((2300, 2520, 2740)):
    L(stick(x, 1250, 0.7), n * 0.25, n * 0.25 + 0.5, sfx="wood_high" if n == 0 else None)
    L(face(x, 1250, 0.7, "smile"), n * 0.25 + 0.5, n * 0.25 + 0.6)
L(bubble(2520, 640, 520, 150, -1), 1, 1.5, BLACK, 8, sfx="pop")
T("走，吃饭去", 2520, 640, 64, k0=1.5)
L(arrow((2900, 1100), (3250, 1100), 0.05, 40), 2, 2.4, GREEN, 9, sfx="wood_high")
H(3, "pop", 0.6)

b.shot("没人叫上你", "灵魂拷问", view=(950, 850, 0.85))
L(face(1250, 1300, 0.75, "sad"), 0, 0.3, BLUE, 9, sfx="pop")
T("……", 1250, 940, 70, k0=1, sfx="wood_high")
T("没叫我", 700, 1250, 72, RED, k0=2, sfx="rim")

b.shot("下午群里发了句话", "灵魂拷问", view=(950, 1800, 0.85))
L(phone(950, 1820, 560, 760), 0, 0.8, BLACK, 9, sfx="wood_high")
T("工作群", 950, 1530, 52, k0=0.8)
L(bubble(1000, 1720, 440, 120, 1), 1, 1.4, BLUE, 8, sfx="pop")
T("方案改好了", 1000, 1720, 56, BLUE, k0=1.4)
T("15:00", 1400, 1560, 56, RED, k0=2, sfx="pop")

b.shot("半天没人接", "灵魂拷问", view=(950, 1800, 0.85))
T("……", 950, 1930, 70, k0=0, sfx="wood_high")
T("0 条回复", 950, 2040, 60, RED, k0=1, sfx="pop")
L(P((1320, 1560), (1480, 1560)), 2, 2.3, RED, 7, sfx="rim")
T("17:00", 1400, 1660, 56, RED, k0=3, sfx="pop")

b.shot("怎么这么难受？", "灵魂拷问", view=(1800, 1350, 0.42), flashes=[0])
T("？", 2650, 1750, 520, RED, k0=0, k1=0.6, sfx="kick")
T("怎么这么难受", 1800, 2280, 120, k0=1.0, k1=2.0, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "孤独是可耻的", view=(1050, 2950, 0.9))
L(book(750, 2950, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 750, 2710, 76, GREEN, k0=1.0, sfx="pop")
T("约翰 · 卡乔波", 750, 3190, 50, k0=2.0, sfx="pop")

GROUP = (2130, 2270, 2650, 2790)
b.shot("祖先成群过日子", "书中观点 · 抱团", view=(2650, 2980, 0.85))
L(fire(2460, 3250, 1.0), 0, 0.8, RED, 9, sfx="wood_high")
for n, x in enumerate(GROUP):
    L(stick(x, 3300, 0.55), 1 + n * 0.25, 1.4 + n * 0.25, sfx="pop" if n == 0 else None)
T("祖先", 2460, 2650, 70, k0=2, sfx="pop")

b.shot("落单就危险", "书中观点 · 落单", view=(2750, 2980, 0.85), shake=[0], flashes=[0])
T("危险！", 3080, 2700, 150, RED, k0=0, k1=0.5, sfx="kick")
L(stick(3120, 3300, 0.55), 1, 1.4, BLUE, 9, sfx="wood_high")
L(face(3120, 3300, 0.55, "sad"), 1.4, 1.5, BLUE, 8)
for n, (ex, ey) in enumerate(((3300, 2960), (3320, 3130))):
    b.custom(J(), 2 + n, 2.3 + n, spot_fn(ex - 22, ey, 12, RED, 1.0), sfx="tom")
    b.custom(J(), 2 + n, 2.3 + n, spot_fn(ex + 22, ey, 12, RED, 1.0))

b.shot("人离不开人", "书中观点 · 社会动物", view=(2650, 3150, 0.85))
T("人 = 社会动物", 2650, 3560, 84, RED, k0=0, k1=1.2, sfx="pop")
L(underline(2370, 2930, 3630), 2, 2.5, RED, 8, sfx="ding")

MON = (1050, 4350)
STK = {"A": (1050, 4210), "B": (760, 4600), "C": (1340, 4600)}
SS = 0.55
b.shot("有个传球实验", "书中提到 · 网络传球", view=(1050, 4300, 0.85))
L(rect(*MON, 1100, 800, 30), 0, 0.8, BLACK, 9, sfx="wood_high")
T("网络传球游戏", 1050, 3870, 66, k0=1, sfx="pop")
for n, key in enumerate("ABC"):
    x, y = STK[key]
    L(stick(x, y, SS), 2 + n * 0.3, 2.3 + n * 0.3, BLUE if key == "C" else BLACK, 9, sfx="pop" if n == 0 else None)
T("你", 1340, 4680, 56, BLUE, k0=3)
j_ball = J()


def _hold(key):
    x, y = STK[key]
    hy = y - 290 * SS
    dx = {"A": 0, "B": 55, "C": -55}[key]
    return x + dx, hy + 130 * SS


# 每一传：(镜头, 接住的拍, 从, 到)。接球落在整数拍，配音效。
PASSES = [(j_ball + 1, 0, "A", "B"), (j_ball + 1, 1, "B", "C"), (j_ball + 1, 2, "C", "A"), (j_ball + 1, 3, "A", "C"),
          (j_ball + 2, 0, "C", "A"), (j_ball + 2, 1, "A", "B"), (j_ball + 2, 2, "B", "A"), (j_ball + 2, 3, "A", "B"),
          (j_ball + 3, 0, "B", "A"), (j_ball + 3, 1, "A", "B"), (j_ball + 3, 2, "B", "A"), (j_ball + 3, 3, "A", "B")]
FLY = 0.32                      # 球在空中的秒数


def ball_fn(c, k, t):
    pos = _hold("A")
    for jj, kk, src, dst in PASSES:
        tc = b.t_of(jj, kk)
        ts = tc - FLY
        if t < ts:
            break
        (x0, y0), (x1, y1) = _hold(src), _hold(dst)
        if t >= tc:
            pos = (x1, y1)
            continue
        f = clamp01((t - ts) / FLY)
        pos = (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f - 150 * 4 * f * (1 - f))
        trail = skia.Path()
        trail.moveTo(x0, y0)
        for i in range(1, 13):
            g = f * i / 12
            trail.lineTo(x0 + (x1 - x0) * g, y0 + (y1 - y0) * g - 150 * 4 * g * (1 - g))
        c.drawPath(trail, K.paint(BLACK, 0.25, 5))
        break
    K.dot(c, pos[0], pos[1], 28, "#E07B24")
    c.drawCircle(pos[0], pos[1], 28, K.paint(BLACK, 1, 5))
    return None


b.custom(j_ball, 3, 3.2, ball_fn)

b.shot("三个人传来传去", "书中提到 · 网络传球", view=(1050, 4300, 0.85))
for kk in range(4):
    H(kk, "pop" if kk % 2 == 0 else "wood_high", 0.7)

b.shot("渐渐不传给你了", "书中提到 · 网络传球", view=(1050, 4300, 0.85))
for kk in range(4):
    H(kk, "pop" if kk % 2 == 0 else "wood_high", 0.7)
T("没你的份", 1350, 4060, 52, RED, k0=3.2)

b.shot("你只能干看着", "书中提到 · 网络传球", view=(1050, 4300, 0.85))
H(0, "pop", 0.6)
H(1, "wood_high", 0.6)
L(face(*STK["C"], SS, "sad"), 2, 2.2, BLUE, 8, sfx="rim")
T("……", 1340, 4340, 60, BLUE, k0=3, sfx="pop")

BR = (2650, 4000)
V1, V2 = (2510, 4470, 200), (2790, 4470, 200)
b.shot("脑子里也会疼", "书中观点 · 大脑", view=(2650, 4300, 0.85))
L(brain(*BR, 150), 0, 0.8, BLACK, 9, sfx="wood_high")
b.custom(J(), 1, 1.5, spot_fn(2720, 3960, 60), sfx="pop")
T("疼！", 3020, 3870, 70, RED, k0=2, sfx="rim")

b.shot("跟身体疼有重叠", "书中观点 · 重叠", view=(2650, 4300, 0.85))
L(circle(*V1), 0, 0.6, BLUE, 9, sfx="wood_high")
T("被冷落", V1[0] - 80, V1[1], 48, BLUE, k0=0.6)
L(circle(*V2), 1, 1.6, BLACK, 9, sfx="wood_high")
T("身体疼", V2[0] + 80, V2[1], 48, k0=1.6)
b.custom(J(), 2, 2.6, overlap_fn(V1, V2), sfx="ding")
T("重叠", 2650, 4760, 56, RED, k0=3, sfx="pop")

b.shot("疼在喊你回人群", "书中观点 · 一张图", view=(1800, 3950, 0.38))
L(arrow((1640, 4200), (2250, 4330), -0.15, 50), 0, 0.6, GREEN, 10, sfx="wood_high")
T("被晾 → 疼 → 回到人群里", 1800, 4850, 100, RED, k0=1, k1=2.6, sfx="pop")
H(3, "ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5800), (2650, 5800), (950, 6700), (2650, 6700)]
b.shot("身边也常碰到", "身边的例子", view=(1800, 6250, 0.355))
T("身边的例子", 1800, 5250, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("开会挨个夸人", "例子 · 开会", view=(950, 5800, 0.85))
L(stick(560, 6130, 0.75, "point", tie=True), 0, 0.6, sfx="wood_high")
for n, x in enumerate((870, 1070, 1270)):
    L(stick(x, 6130, 0.55, hair=n == 1), 0.6 + n * 0.15, 0.9 + n * 0.15, BLUE if n == 2 else BLACK, 9)
T("好！", 870, 5640, 64, RED, k0=1, sfx="pop")
T("好！", 1070, 5640, 64, RED, k0=2, sfx="pop")

b.shot("唯独跳过了你", "例子 · 开会", view=(950, 5800, 0.85))
L(face(1270, 6130, 0.55, "sad"), 0, 0.3, BLUE, 8, sfx="pop")
L(arrow((900, 5560), (1300, 5560), -0.15, 36), 1, 1.5, RED, 8, sfx="wood_high")
T("跳过", 1270, 5640, 64, BLUE, k0=2, sfx="rim")

b.shot("刷到聚会照片", "例子 · 聚会", view=(2650, 5800, 0.85))
L(phone(2500, 5820, 460, 640), 0, 0.7, BLACK, 9, sfx="wood_high")
L(rect(2500, 5760, 360, 300, 10), 0.8, 1.0, BLACK, 7)
for n, x in enumerate((2400, 2500, 2600)):
    L(stick(x, 5880, 0.35, "up"), 1 + n * 0.2, 1.3 + n * 0.2, BLACK, 7, sfx="pop" if n == 0 else None)
T("周末聚会", 2500, 5560, 52, k0=2, sfx="pop")

b.shot("才知道没叫我", "例子 · 聚会", view=(2650, 5800, 0.85))
L(stick(3000, 6130, 0.6, "hold"), 0, 0.5, BLUE, 9, sfx="wood_high")
L(face(3000, 6130, 0.6, "sad"), 0.5, 0.6, BLUE, 8)
T("没叫我", 3000, 5600, 64, RED, k0=1, sfx="rim")
T("？", 3170, 5740, 90, RED, k0=2, sfx="pop")

b.shot("年夜饭聊得热闹", "例子 · 家庭", view=(950, 6700, 0.85))
L(join(P((520, 6975), (1060, 6975)), P((560, 6975), (560, 7080)), P((1020, 6975), (1020, 7080))), 0, 0.4, BLACK, 10,
  sfx="wood_high")
for n, x in enumerate((600, 780, 960)):
    L(stick(x, 7030, 0.5), 0.4 + n * 0.15, 0.7 + n * 0.15, BLACK, 9)
T("哈哈", 600, 6760, 56, k0=1, sfx="pop")
T("哈哈哈", 900, 6700, 56, k0=2, sfx="pop")

b.shot("你一句插不上", "例子 · 家庭", view=(950, 6700, 0.85))
L(stick(1300, 7030, 0.5), 0, 0.4, BLUE, 9, sfx="wood_high")
L(face(1300, 7030, 0.5, "flat"), 0.4, 0.5, BLUE, 8)
L(bubble(1340, 6700, 220, 110, -1), 1, 1.3, BLUE, 7, sfx="pop")
T("我…", 1340, 6700, 56, BLUE, k0=1.3)
L(cross(1340, 6700, 60), 2, 2.3, RED, 10, sfx="rim")

b.shot("孩子被同学冷落", "例子 · 孩子", view=(2650, 6700, 0.85))
for n, x in enumerate((2250, 2400, 2550)):
    L(stick(x, 6950, 0.42, "up"), n * 0.2, n * 0.2 + 0.3, BLACK, 8, sfx="wood_high" if n == 0 else None)
L(stick(3000, 6950, 0.42), 1, 1.3, BLUE, 8, sfx="pop")
L(face(3000, 6950, 0.42, "sad"), 1.3, 1.4, BLUE, 7)
T("课间", 2400, 6560, 56, k0=2, sfx="pop")

b.shot("回家就发脾气", "例子 · 孩子", view=(2650, 6750, 0.85))
L(scribble(3000, 6720, 200, 80, 7), 0, 0.5, RED, 7, sfx="shaker")
T("哼！", 3190, 6570, 70, RED, k0=1, sfx="rim")
L(rect(2790, 6990, 110, 130, 8), 2, 2.4, BLACK, 8, sfx="wood_high")
T("书包一扔", 2790, 6860, 48, k0=2.5)

b.shot("每件都是被晾", "身边的例子", view=(1800, 6250, 0.355))
for n, (x, y) in enumerate(CARDS):
    T("被晾", x + 430, y - 320, 100, RED, k0=n, sfx="pop")

b.shot("疼起来一个样", "身边的例子", view=(1800, 6250, 0.355), shake=[0])
T("疼起来都一样", 1800, 7250, 150, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 8350), (2650, 8350), (950, 9250), (2650, 9250)]
b.shot("被晾了这样办", "具体做法", view=(1800, 8800, 0.355))
T("被晾了，这样做", 1800, 7780, 130, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先认下这份难受", "第一步 · 认下来", view=(950, 8350, 0.85))
T("① 难受很正常", 950, 8050, 76, BLUE, k0=0, sfx="pop")
L(stick(650, 8680, 0.65), 1, 1.5, sfx="wood_high")
L(face(650, 8680, 0.65, "sad"), 1.5, 1.6)
L(bubble(1080, 8250, 380, 120, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("有点难受", 1080, 8250, 56, k0=2.4)

b.shot("别硬憋着装没事", "第一步 · 认下来", view=(950, 8400, 0.85))
T("装没事", 1100, 8470, 56, k0=0, sfx="pop")
L(P((1000, 8470), (1200, 8470)), 1, 1.3, RED, 10, sfx="rim")
T("跟朋友说一句", 1060, 8610, 52, GREEN, k0=2, sfx="pop")
L(check(1290, 8600, 36), 3, 3.3, GREEN, 9, sfx="ding")

b.shot("找件事一起干", "第二步 · 一起干", view=(2650, 8350, 0.85))
T("② 找件事一起干", 2650, 8050, 72, BLUE, k0=0, sfx="pop")
L(box(2650, 8260, 300, 140), 1, 1.5, BLACK, 9, sfx="wood_high")
L(stick(2520, 8530, 0.6, "up"), 2, 2.4, BLACK, 9, sfx="pop")
L(stick(2780, 8530, 0.6, "up"), 2.4, 2.8, BLUE, 9)

b.shot("打球拼饭都行", "第二步 · 一起干", view=(2650, 8400, 0.85))
for n, w in enumerate(("周末打球", "一起拼饭", "项目组队")):
    T(w, 2280 + n * 370, 8650, 50, k0=n, sfx="pop")

b.shot("干着活话就多了", "第二步 · 一起干", view=(2650, 8350, 0.85))
L(bubble(2330, 8110, 220, 90, 1), 0, 0.3, BLACK, 7, sfx="wood_high")
T("递我", 2330, 8110, 48, k0=0.3)
L(face(2520, 8530, 0.6, "smile"), 1, 1.2, BLACK, 8, sfx="pop")
L(face(2780, 8530, 0.6, "smile"), 1.2, 1.4, BLUE, 8)
L(underline(2200, 3100, 8730, 10, 30), 2, 2.5, RED, 7, sfx="ding")

b.shot("先帮个小忙", "第三步 · 帮小忙", view=(950, 9250, 0.85))
T("③ 先帮个小忙", 950, 8950, 76, BLUE, k0=0, sfx="pop")
L(stick(620, 9580, 0.65, "hold"), 1, 1.5, BLUE, 9, sfx="wood_high")
L(face(620, 9580, 0.65, "smile"), 1.5, 1.6, BLUE, 8)
L(stick(1300, 9580, 0.65), 2, 2.5, BLACK, 9, sfx="pop")

b.shot("顺手带杯咖啡", "第三步 · 帮小忙", view=(950, 9250, 0.85))
L(cup(950, 9330, 0.6), 0, 0.6, BLACK, 8, sfx="pop")
T("顺手带一杯", 950, 9110, 52, k0=1, sfx="pop")
L(face(1300, 9580, 0.65, "smile"), 2, 2.2, BLACK, 8, sfx="ding")

b.shot("帮新人看个报错", "第三步 · 帮小忙", view=(950, 9250, 0.85))
b.erase(J(), 0, 0.5, 950, 9250, 380, 420)
H(0, "shaker")
L(doc(950, 9350, 130, 160, 3), 0.6, 0.95, BLACK, 8)
L(cross(950, 9350, 40), 1, 1.2, RED, 8, sfx="rim")
T("帮看报错", 950, 9130, 52, k0=1.3)
L(check(950, 9350, 50), 2, 2.3, GREEN, 10, sfx="ding")
T("谢谢！", 1300, 9150, 56, RED, k0=3, sfx="pop")

b.shot("先往好处猜", "第四步 · 往好处想", view=(2650, 9250, 0.85))
T("④ 往好处猜", 2650, 8950, 76, BLUE, k0=0, sfx="pop")
L(stick(2350, 9580, 0.65), 1, 1.5, BLUE, 9, sfx="wood_high")
L(face(2350, 9580, 0.65, "flat"), 1.5, 1.6, BLUE, 8)
L(bubble(2820, 9170, 480, 130, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("可能忘叫我了", 2820, 9170, 54, k0=2.4)

b.shot("下回你来约饭", "第四步 · 往好处想", view=(2650, 9300, 0.85))
L(face(2350, 9580, 0.65, "smile"), 0, 0.2, BLUE, 8, sfx="pop")
T("明天一起吃？", 2760, 9400, 56, RED, k0=1, sfx="pop")
L(check(3100, 9390, 40), 2, 2.3, GREEN, 10, sfx="ding")
T("好呀", 2760, 9520, 54, GREEN, k0=3, sfx="pop")

b.shot("照着做就行", "具体做法", view=(1800, 8800, 0.355))
for n, (x, y) in enumerate(SOL):
    L(check(x + 500, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 else "pop")

b.shot("疼了就往人堆走", "一句话", view=(1800, 5150, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 10000, 0.8))
T("你被晾过吗？", 1800, 9920, 80, RED, k0=0.5, k1=1.6)
T("下一讲：越孤单，为什么越爱跟猫说话？", 1800, 10080, 50, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "social", "人是社会动物", "被同事晾在一边，为什么那么难受？", ACC, b.shots,
                 [f"{BOOK}第二部分“从自私的基因到社会动物”、第 11 章“协作是人类进化的王道”（转述）",
                  "书中讨论的网络传球实验：Eisenberger, Lieberman & Williams (2003), Science",
                  "中译本：焦梦津译，中国人民大学出版社 2009"],
                 "被同事晾着|为什么【这么疼】", 16,
                 ["书中观点均为转述：人类祖先靠合作和群居活下来、繁荣起来，离群是危险的，人是社会动物（第二部分“从自私的基因到"
                  "社会动物”，第 7–11 章）；书中讨论了艾森伯格等人 2003 年的“网络传球”实验——受试者在电脑上和另外两名“玩家”"
                  "传球，渐渐不再收到球，被排斥时的大脑活动与身体疼痛相关的区域有重叠；被冷落的痛像信号，提醒人修复与他人的联系。"
                  "出处：John T. Cacioppo & William Patrick, Loneliness: Human Nature and the Need for Social Connection "
                  "(W. W. Norton, 2008)，中译本《孤独是可耻的》（焦梦津译，中国人民大学出版社 2009）。上屏均为转述，不是逐字引文。",
                  "午饭没被叫上、工作群没人回、开会被跳过、聚会照片、年夜饭插不上话、孩子被同学冷落均为现实场景示意，不指向任何具体"
                  "公司或个人；时间与“0 条回复”为示意；传球画面、大脑与重叠图为对实验与结论的通俗化示意，不是实验数据。",
                  "四步做法（认下难受别硬憋、找件事一起干、先帮别人个小忙、往好处猜并主动约）为据书中思路（含第 14 章 EASE："
                  "先迈一小步、往好处预期别人）整理的建议。"],
                 tags="#职场 #人际关系")
    return b.attach(ep)
