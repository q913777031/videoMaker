"""07 人是社会动物（白板手绘版）：被同事晾在一边，为什么那么难受？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
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
                               desk, face, hands_at, join, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#C0603A"
SQUARE_SHOT = 6

b = Board(size=(3600, 13000))


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


# ---------------------------------------------------------------- 开局：被晾在一边（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("午饭没人叫我", "灵魂拷问", (1400, 900, 0.58))
L(clock(700, 640, 120), 0, 0.6, sfx="wood_high")
L(hands_at(700, 640, 120, 12, 0), 0.6, 0.8, RED, 12)
T("12:00", 700, 850, 64, RED, k0=0.8, k1=1.0)
L(desk(950, 1100, 360), 1, 1.5, sfx="wood_high")
L(stick(1250, 1300, 0.75), 1.5, 1.9)
for n, x in enumerate((1600, 1760, 1920)):
    L(stick(x, 1250, 0.6), 2 + n * 0.25, 2.4 + n * 0.25, sfx="pop" if n == 0 else None)
    L(face(x, 1250, 0.6, "smile"), 2.4 + n * 0.25, 2.5 + n * 0.25)
L(bubble(1760, 700, 440, 150, -1), 3, 3.3, BLACK, 8, sfx="pop")
T("走，吃饭去", 1760, 700, 60, k0=3.3, k1=4.0)
L(arrow((2020, 1100), (2150, 1100), 0.05, 36), 4, 4.4, GREEN, 9, sfx="wood_high")
T("没叫我", 700, 1250, 72, RED, k0=5, k1=5.6, sfx="rim")
L(face(1250, 1300, 0.75, "sad"), 5.6, 5.9, BLUE, 9)

scene("群里发话没人回", "灵魂拷问", (2800, 2000, 0.85))
L(phone(2750, 2020, 560, 760), 0, 0.8, BLACK, 9, sfx="wood_high")
T("工作群", 2750, 1730, 52, k0=0.8, k1=1.0)
L(bubble(2800, 1920, 440, 120, 1), 1, 1.4, BLUE, 8, sfx="pop")
T("方案改好了", 2800, 1920, 56, BLUE, k0=1.4, k1=2.0)
T("15:00", 3200, 1760, 56, RED, k0=2, k1=2.6, sfx="pop")
T("……", 2750, 2130, 70, k0=3, k1=3.5, sfx="wood_high")
T("0 条回复", 2750, 2240, 60, RED, k0=4, k1=4.8, sfx="pop")
L(P((3120, 1760), (3280, 1760)), 5, 5.3, RED, 7, sfx="rim")
T("17:00", 3200, 1860, 56, RED, k0=5.3, k1=5.9)

scene("怎么这么难受", "灵魂拷问", (1800, 1400, 0.36), flashes=[0])
T("？", 1300, 1850, 420, RED, k0=0, k1=0.6, sfx="kick")
T("怎么这么难受", 1300, 2350, 160, k0=2, k1=3.2, sfx="pop")
H(4, "ding")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

GROUP = (1730, 1870, 2250, 2390)
scene("书里说祖先靠抱团", "孤独是可耻的 · 书中观点", (1650, 3800, 0.58))
L(book(1100, 3650, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 1100, 3410, 76, GREEN, k0=1, k1=2.0, sfx="pop")
T("约翰 · 卡乔波", 1100, 3890, 50, k0=2, k1=2.8, sfx="pop")
L(fire(2060, 3950, 1.0), 3, 3.8, RED, 9, sfx="wood_high")
for n, x in enumerate(GROUP):
    L(stick(x, 4000, 0.55), 4 + n * 0.25, 4.4 + n * 0.25, sfx="pop" if n == 0 else None)
T("祖先", 2060, 3350, 70, k0=5, k1=5.5, sfx="pop")

scene("落单危险，人离不开人", "书中观点 · 社会动物", (2250, 3800, 0.7), shake=[0], flashes=[0])
T("危险！", 2680, 3400, 150, RED, k0=0, k1=0.5, sfx="kick")
L(stick(2720, 4000, 0.55), 1, 1.4, BLUE, 9, sfx="wood_high")
L(face(2720, 4000, 0.55, "sad"), 1.4, 1.5, BLUE, 8)
for n, (ex, ey) in enumerate(((2900, 3660), (2920, 3830))):
    b.custom(J(), 2 + n, 2.3 + n, spot_fn(ex - 22, ey, 12, RED, 1.0), sfx="tom")
    b.custom(J(), 2 + n, 2.3 + n, spot_fn(ex + 22, ey, 12, RED, 1.0))
T("人 = 社会动物", 2250, 4260, 84, RED, k0=4, k1=5.0, sfx="pop")
L(underline(1970, 2530, 4330), 5, 5.5, RED, 8, sfx="ding")

MON = (1050, 5050)
STK = {"A": (1050, 4910), "B": (760, 5300), "C": (1340, 5300)}
SS = 0.55
j_ball = scene("有个传球实验", "书中提到 · 网络传球", (1050, 5000, 0.85))
L(rect(*MON, 1100, 800, 30), 0, 0.8, BLACK, 9, sfx="wood_high")
T("网络传球游戏", 1050, 4570, 66, k0=1, k1=2.0, sfx="pop")
for n, key in enumerate("ABC"):
    x, y = STK[key]
    L(stick(x, y, SS), 2 + n * 0.3, 2.3 + n * 0.3, BLUE if key == "C" else BLACK, 9, sfx="pop" if n == 0 else None)
T("你", 1200, 5390, 56, BLUE, k0=3, k1=3.5, sfx="wood_high")


def _hold(key):
    x, y = STK[key]
    hy = y - 290 * SS
    dx = {"A": 0, "B": 55, "C": -55}[key]
    return x + dx, hy + 130 * SS


# 每一传：(场景, 接住的拍, 从, 到)。接球落在整数拍，配音效。
PASSES = [(j_ball, 4, "A", "B"), (j_ball, 5, "B", "C"), (j_ball, 6, "C", "A"), (j_ball, 7, "A", "C"),
          (j_ball + 1, 0, "C", "A"), (j_ball + 1, 1, "A", "B"), (j_ball + 1, 2, "B", "A"), (j_ball + 1, 3, "A", "B"),
          (j_ball + 1, 4, "B", "A")]
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


b.custom(j_ball, 3.5, 3.7, ball_fn)
for n, (jj, kk, _, _) in enumerate(PASSES):
    if jj == j_ball:
        b.hit(jj, kk, "pop" if n % 2 == 0 else "wood_high", 0.7)

scene("渐渐不传给你了", "书中提到 · 网络传球", (1050, 5000, 0.85))
for n, (jj, kk, _, _) in enumerate(PASSES):
    if jj == J():
        H(kk, "pop" if n % 2 == 0 else "wood_high", 0.7)
T("没你的份", 1350, 4760, 52, RED, k0=3.2, k1=3.9)
L(face(*STK["C"], SS, "sad"), 5, 5.2, BLUE, 8, sfx="rim")
T("……", 1340, 5040, 60, BLUE, k0=5.3, k1=5.9)

BR = (2650, 5000)
V1, V2 = (2510, 5470, 200), (2790, 5470, 200)
scene("冷落的疼跟身体疼重叠", "书中观点 · 大脑", (2650, 5300, 0.85))
L(brain(*BR, 150), 0, 0.8, BLACK, 9, sfx="wood_high")
b.custom(J(), 1, 1.5, spot_fn(2720, 4960, 60), sfx="pop")
T("疼！", 3020, 4870, 70, RED, k0=1.5, k1=2.0)
L(circle(*V1), 2, 2.6, BLUE, 9, sfx="wood_high")
T("被冷落", V1[0] - 80, V1[1], 48, BLUE, k0=2.6, k1=3.1)
L(circle(*V2), 3, 3.6, BLACK, 9, sfx="wood_high")
T("身体疼", V2[0] + 80, V2[1], 48, k0=3.6, k1=4.1)
b.custom(J(), 4, 4.6, overlap_fn(V1, V2), sfx="ding")
T("重叠", 2650, 5760, 56, RED, k0=5, k1=5.5, sfx="pop")

scene("疼在喊你回人群", "书中观点 · 一张图", (1800, 4550, 0.38))
L(arrow((1640, 4900), (2250, 5130), -0.15, 50), 0, 0.6, GREEN, 10, sfx="wood_high")
T("被晾 → 疼 → 回到人群里", 1250, 5600, 90, RED, k0=1, k1=2.6, sfx="pop")
H(3, "ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 7600), (2650, 7600), (950, 8900), (2650, 8900)]
scene("身边也常碰到", "身边的例子", (1800, 8250, 0.355))
T("身边的例子", 1800, 7050, 110, k0=0, k1=1.2, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 2 + n, 2.45 + n, GREEN, 8, sfx="wood_high" if n % 2 == 0 else "pop")

scene("开会唯独跳过你", "例子 · 开会", (880, 7650, 0.85))
L(stick(560, 7930, 0.75, "point", tie=True), 0, 0.6, sfx="wood_high")
for n, x in enumerate((870, 1070, 1270)):
    L(stick(x, 7930, 0.55, hair=n == 1), 0.6 + n * 0.15, 0.9 + n * 0.15, BLUE if n == 2 else BLACK, 9)
T("好！", 870, 7440, 64, RED, k0=1, k1=1.5, sfx="pop")
T("好！", 1070, 7440, 64, RED, k0=2, k1=2.5, sfx="pop")
L(arrow((900, 7360), (1300, 7360), -0.15, 36), 3, 3.5, RED, 8, sfx="wood_high")
L(face(1270, 7930, 0.55, "sad"), 4, 4.3, BLUE, 8, sfx="pop")
T("跳过", 1270, 7440, 64, BLUE, k0=5, k1=5.5, sfx="rim")

scene("聚会照片里没有我", "例子 · 聚会", (2720, 7650, 0.85))
L(phone(2500, 7620, 460, 640), 0, 0.7, BLACK, 9, sfx="wood_high")
L(rect(2500, 7560, 360, 300, 10), 0.7, 0.9, BLACK, 7)
for n, x in enumerate((2400, 2500, 2600)):
    L(stick(x, 7680, 0.35, "up"), 1 + n * 0.2, 1.3 + n * 0.2, BLACK, 7, sfx="pop" if n == 0 else None)
T("周末聚会", 2500, 7360, 52, k0=2, k1=2.7, sfx="pop")
L(stick(3000, 7930, 0.6, "hold"), 3, 3.5, BLUE, 9, sfx="wood_high")
L(face(3000, 7930, 0.6, "sad"), 3.5, 3.6, BLUE, 8)
T("没叫我", 3000, 7400, 64, RED, k0=4, k1=4.5, sfx="rim")
T("？", 3170, 7540, 90, RED, k0=5, k1=5.5, sfx="pop")

scene("年夜饭插不上嘴", "例子 · 家庭", (880, 9000, 0.85))
L(join(P((520, 9175), (1060, 9175)), P((560, 9175), (560, 9280)), P((1020, 9175), (1020, 9280))), 0, 0.4, BLACK, 10,
  sfx="wood_high")
for n, x in enumerate((600, 780, 960)):
    L(stick(x, 9230, 0.5), 0.4 + n * 0.15, 0.7 + n * 0.15, BLACK, 9)
T("哈哈", 600, 8960, 56, k0=1, k1=1.5, sfx="pop")
T("哈哈哈", 900, 8900, 56, k0=2, k1=2.6, sfx="pop")
L(stick(1300, 9230, 0.5), 3, 3.4, BLUE, 9, sfx="wood_high")
L(face(1300, 9230, 0.5, "flat"), 3.4, 3.5, BLUE, 8)
L(bubble(1340, 8900, 220, 110, -1), 4, 4.3, BLUE, 7, sfx="pop")
T("我…", 1340, 8900, 56, BLUE, k0=4.3, k1=4.8)
L(cross(1340, 8900, 60), 5, 5.3, RED, 10, sfx="rim")

scene("孩子被冷落发脾气", "例子 · 孩子", (2720, 9000, 0.85))
for n, x in enumerate((2250, 2400, 2550)):
    L(stick(x, 9150, 0.42, "up"), n * 0.2, n * 0.2 + 0.3, BLACK, 8, sfx="wood_high" if n == 0 else None)
L(stick(3000, 9150, 0.42), 1, 1.3, BLUE, 8, sfx="pop")
L(face(3000, 9150, 0.42, "sad"), 1.3, 1.4, BLUE, 7)
T("课间", 2400, 8760, 56, k0=2, k1=2.5, sfx="pop")
L(scribble(3000, 8920, 200, 80, 7), 3, 3.5, RED, 7, sfx="shaker")
T("哼！", 3190, 8770, 70, RED, k0=4, k1=4.5, sfx="rim")
L(rect(2790, 9190, 110, 130, 8), 5, 5.4, BLACK, 8, sfx="wood_high")
T("书包一扔", 2790, 9060, 48, k0=5.4, k1=6.0)

scene("都是被晾，一样的疼", "身边的例子", (1800, 8250, 0.355), shake=[4])
for n, (x, y) in enumerate(CARDS):
    T("被晾", x + 430, y - 320, 100, RED, k0=n, k1=n + 0.5, sfx="pop")
T("疼起来都一样", 1800, 9450, 150, RED, k0=4, k1=4.8, sfx="kick")
H(6, "ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 10550), (2650, 10550), (950, 11950), (2650, 11950)]
scene("先认下，别硬憋", "第一步 · 认下来", (950, 10600, 0.85))
L(rect(*SOL[0], 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("① 难受很正常", 950, 10250, 76, BLUE, k0=0.5, k1=1.0)
L(stick(650, 10880, 0.65), 1, 1.4, sfx="pop")
L(face(650, 10880, 0.65, "sad"), 1.4, 1.5)
L(bubble(1080, 10450, 380, 120, -1), 2, 2.3, BLACK, 8, sfx="pop")
T("有点难受", 1080, 10450, 56, k0=2.3, k1=3.0)
T("装没事", 1100, 10670, 56, k0=3, k1=3.5, sfx="pop")
L(P((1000, 10670), (1200, 10670)), 3.6, 3.9, RED, 10)
T("跟朋友说一句", 1060, 10810, 52, GREEN, k0=4, k1=5.0, sfx="pop")
L(check(1290, 10800, 36), 5, 5.3, GREEN, 9, sfx="ding")

scene("找件事一起干", "第二步 · 一起干", (2650, 10600, 0.85))
L(rect(*SOL[1], 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("② 找件事一起干", 2650, 10250, 72, BLUE, k0=0.5, k1=1.0)
L(box(2650, 10460, 300, 140), 1, 1.5, BLACK, 9, sfx="wood_high")
L(stick(2520, 10730, 0.6, "up"), 2, 2.4, BLACK, 9, sfx="pop")
L(stick(2780, 10730, 0.6, "up"), 2.4, 2.8, BLUE, 9)
for n, w in enumerate(("周末打球", "一起拼饭", "项目组队")):
    T(w, 2280 + n * 370, 10850, 50, k0=3 + n, k1=3.7 + n, sfx="pop")
L(face(2520, 10730, 0.6, "smile"), 5.7, 5.85, BLACK, 8)
L(face(2780, 10730, 0.6, "smile"), 5.85, 6.0, BLUE, 8)

scene("顺手帮个小忙", "第三步 · 帮小忙", (950, 12000, 0.85))
L(rect(*SOL[2], 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("③ 先帮个小忙", 950, 11650, 76, BLUE, k0=0.5, k1=1.0)
L(stick(620, 12280, 0.65, "hold"), 1, 1.5, BLUE, 9, sfx="wood_high")
L(face(620, 12280, 0.65, "smile"), 1.5, 1.6, BLUE, 8)
L(stick(1300, 12280, 0.65), 2, 2.5, BLACK, 9, sfx="pop")
L(cup(950, 12030, 0.6), 3, 3.6, BLACK, 8, sfx="pop")
T("顺手带一杯", 950, 11810, 52, k0=4, k1=4.9, sfx="pop")
L(face(1300, 12280, 0.65, "smile"), 5, 5.2, BLACK, 8, sfx="ding")
T("谢谢！", 1300, 11850, 56, RED, k0=5.3, k1=5.8)

scene("往好处猜，下回你约", "第四步 · 往好处想", (2650, 12000, 0.85))
L(rect(*SOL[3], 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("④ 往好处猜", 2650, 11650, 76, BLUE, k0=0.5, k1=1.0)
L(stick(2350, 12280, 0.65), 1, 1.4, BLUE, 9, sfx="wood_high")
L(face(2350, 12280, 0.65, "smile"), 1.4, 1.5, BLUE, 8)
L(bubble(2820, 11870, 480, 130, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("可能忘叫我了", 2820, 11870, 54, k0=2.4, k1=3.0)
T("明天一起吃？", 2760, 12100, 56, RED, k0=3, k1=4.0, sfx="pop")
L(check(3100, 12090, 40), 4, 4.3, GREEN, 10, sfx="ding")
T("好呀", 2760, 12220, 54, GREEN, k0=5, k1=5.5, sfx="pop")

scene("疼了就往人堆走", "一句话", (1800, 9700, 0.2))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 12700, 0.8))
H(0, "cymbal", 0.5)
T("你被晾过吗？", 1800, 12620, 80, RED, k0=1, k1=2.2)
H(1, "pop")
T("下一讲：越孤单，为什么越爱跟猫说话？", 1800, 12780, 50, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "social", "人是社会动物", "被同事晾在一边，为什么那么难受？", ACC, b.shots,
                 [f"{BOOK}第二部分“从自私的基因到社会动物”、第 11 章“协作是人类进化的王道”（转述）",
                  "书中讨论的网络传球实验：Eisenberger, Lieberman & Williams (2003), Science",
                  "中译本：焦梦津译，中国人民大学出版社 2009"],
                 "被同事晾着|为什么【这么疼】", 8,
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
