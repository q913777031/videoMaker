"""10 波希米亚（白板手绘版）：不想卷了，能换个活法吗？（系列最后一讲）

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。

叙事：打工人切身问题开局（加班到第五年，升职名单上还是没有自己 → 想去小城开家咖啡馆 → 又怕亲戚说没出息 →
一拖又是一年）→ 书中观点（亮书《身份的焦虑》+ 德波顿，第二部分“解决方法”第五章“波希米亚”；
波希米亚式的人不认主流那把尺子，自己挑一群看重别的东西的人当“观众”；书中提到梭罗在瓦尔登湖过简单日子：
能放下的东西越多，人就越富有；画成一张图：换观众 + 换尺子 → 没那么慌）→
身边的例子（公司只看职级、跑团只问跑多远；亲戚说开店可惜、熟客夸咖啡好喝；老爸在单位不起眼、在钓鱼群里是师傅；
朋友卖了车改骑车、省下的钱去学画）→ 具体做法（找一群同好 / 列一张能放下的清单 / 周末摆摊小步试 / 留好退路）→
系列收尾（评论区问题 + 这一季讲完了）。不鼓吹辞职裸辞，讲“给自己换一群观众、换一把尺子”。
书中观点为转述（Alain de Botton, Status Anxiety, Hamish Hamilton / Pantheon, 2004；中译本《身份的焦虑》，
陈广兴、南治国译，上海译文出版社）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               desk, doc, face, hands_at, join, partial, marker, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#7B4FA0"
SQUARE_SHOT = 5

b = Board(size=(3600, 13250))


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

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def shop(x, y, w=440, h=300) -> skia.Path:
    """小店：(x, y) 为底边中点；墙、条纹雨棚、招牌、门和橱窗。"""
    top = y - h
    parts = [P((x - w / 2, y), (x - w / 2, top), (x + w / 2, top), (x + w / 2, y))]
    aw = P((x - w / 2 - 30, top), (x - w / 2 - 30, top - 70), (x + w / 2 + 30, top - 70), (x + w / 2 + 30, top))
    parts.append(aw)
    n = 6
    sc = skia.Path()
    sc.moveTo(x - w / 2 - 30, top)
    step = (w + 60) / n
    for i in range(n):
        x0 = x - w / 2 - 30 + i * step
        sc.quadTo(x0 + step / 2, top + 45, x0 + step, top)
    parts.append(sc)
    for i in range(1, n):
        x0 = x - w / 2 - 30 + i * step
        parts.append(P((x0, top - 70), (x0, top)))
    parts.append(rect(x, top - 125, w * 0.6, 90, 10))
    parts.append(P((x + w / 4 - 45, y), (x + w / 4 - 45, y - h * 0.6), (x + w / 4 + 45, y - h * 0.6), (x + w / 4 + 45, y)))
    parts.append(rect(x - w / 5, y - h * 0.45, w * 0.3, h * 0.3, 6))
    return join(*parts)


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


def stairs(x0, y0, n=4, w=250, h=150) -> skia.Path:
    pts = [(x0 - 50, y0)]
    x, y = x0, y0
    for _ in range(n):
        x += w
        pts.append((x, y))
        y -= h
        pts.append((x, y))
    pts.append((x + w, y))
    return P(*pts)


def hut(x, y, w=260, h=200) -> skia.Path:
    """小木屋：(x, y) 为底边中点。"""
    walls = P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y))
    roof = P((x - w / 2 - 35, y - h), (x, y - h - 130), (x + w / 2 + 35, y - h), close=True)
    door = P((x - 35, y), (x - 35, y - 110), (x + 35, y - 110), (x + 35, y))
    win = rect(x + w / 4 + 5, y - h * 0.6, 60, 50, 4)
    return join(walls, roof, door, win)


def lake(x, y, w=480, h=170) -> skia.Path:
    return join(oval(x, y, w, h), P((x - w * 0.25, y - 10), (x - w * 0.08, y - 10)),
                P((x + w * 0.02, y + 30), (x + w * 0.2, y + 30)))


def heart(x, y, r=50) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r)
    p.cubicTo(x - r * 1.6, y - r * 0.2, x - r * 0.7, y - r * 1.4, x, y - r * 0.45)
    p.cubicTo(x + r * 0.7, y - r * 1.4, x + r * 1.6, y - r * 0.2, x, y + r)
    return p


def car(x, y) -> skia.Path:
    """小汽车（侧视）：(x, y) 为地面中点。"""
    body = P((x - 170, y - 40), (x - 170, y - 110), (x - 90, y - 110), (x - 50, y - 180), (x + 80, y - 180),
             (x + 120, y - 110), (x + 170, y - 110), (x + 170, y - 40), close=True)
    return join(body, circle(x - 100, y - 35, 35), circle(x + 100, y - 35, 35), P((x - 40, y - 110), (x + 100, y - 110)))


def bike(x, y) -> skia.Path:
    """自行车：(x, y) 为地面中点。"""
    return join(circle(x - 90, y - 55, 55), circle(x + 90, y - 55, 55),
                P((x - 90, y - 55), (x - 20, y - 150), (x + 60, y - 150), (x + 90, y - 55)),
                P((x - 20, y - 150), (x, y - 55), (x - 90, y - 55)), P((x - 45, y - 172), (x - 5, y - 172)),
                P((x - 20, y - 150), (x - 25, y - 172)), P((x + 60, y - 150), (x + 70, y - 190), (x + 100, y - 190)))


def easel(x, y) -> skia.Path:
    """画架：(x, y) 为画布中心。"""
    return join(rect(x, y, 260, 200, 6), P((x - 90, y + 100), (x - 130, y + 220)), P((x + 90, y + 100), (x + 130, y + 220)),
                P((x, y - 100), (x, y - 140)))


def rod(x0, y0, x1, y1, drop=230) -> skia.Path:
    """钓竿 + 鱼线 + 小鱼。"""
    fish = join(oval(x1 + 10, y1 + drop + 30, 80, 40), P((x1 + 50, y1 + drop + 30), (x1 + 75, y1 + drop + 10),
                                                       (x1 + 75, y1 + drop + 50), close=True))
    return join(P((x0, y0), (x1, y1)), P((x1, y1), (x1, y1 + drop)), fish)


def stall(x, y, w=360) -> skia.Path:
    """周末小摊：(x, y) 为地面中点；桌子、前挡板、两根杆、棚子。"""
    return join(P((x - w / 2, y - 120), (x + w / 2, y - 120)), rect(x, y - 60, w, 120, 6),
                P((x - w / 2 + 10, y - 120), (x - w / 2 + 10, y - 330)), P((x + w / 2 - 10, y - 120), (x + w / 2 - 10, y - 330)),
                P((x - w / 2 - 30, y - 330), (x + w / 2 + 30, y - 330), (x + w / 2, y - 400), (x - w / 2, y - 400), close=True))


def calendar(x, y, w=220, h=200) -> skia.Path:
    return join(rect(x, y, w, h, 10), P((x - w / 2, y - h / 2 + 50), (x + w / 2, y - h / 2 + 50)),
                P((x - w / 4, y - h / 2 - 20), (x - w / 4, y - h / 2 + 15)),
                P((x + w / 4, y - h / 2 - 20), (x + w / 4, y - h / 2 + 15)))


def jar(x, y) -> skia.Path:
    """存钱罐（玻璃罐）：(x, y) 为罐身中心。"""
    return join(P((x - 90, y - 120), (x - 110, y + 120), (x + 110, y + 120), (x + 90, y - 120)), rect(x, y - 140, 210, 40, 8))


def coins_fn(x, y):
    def fn(c, k, t):
        for i in range(5):
            f = clamp01(k * 5 - i)
            if f <= 0:
                break
            cy = y + 90 - i * 42
            K.dot(c, x - 40 + (i % 2) * 70, cy - (1 - ease_out(f)) * 160, 30, "#E0B43A")
            c.drawCircle(x - 40 + (i % 2) * 70, cy - (1 - ease_out(f)) * 160, 30, K.paint(BLACK, 1, 5))
        return None

    return fn



# ---------------------------------------------------------------- 折尺（场景 4 画出，场景 5 drop 折断）

RX, RY, RL, RH = 1800, 3120, 900, 110
RULER_LABELS = [(-1, "工资", RX - 340), (-1, "房子", RX - 130), (1, "头衔", RX + 130), (1, "车子", RX + 340)]


def _ruler_half(side) -> skia.Path:
    xo = RX + side * RL / 2
    zz = [(RX + side * (8 if i % 2 else -8), RY - RH / 2 + i * RH / 4) for i in range(5)]
    parts = [P((xo, RY - RH / 2), (RX - side * 8, RY - RH / 2)), P(*zz), P((RX - side * 8, RY + RH / 2), (xo, RY + RH / 2)),
             P((xo, RY - RH / 2), (xo, RY + RH / 2))]
    for i in range(1, 10):
        tx = RX + side * i * RL / 20
        parts.append(P((tx, RY - RH / 2), (tx, RY - RH / 2 + (30 if i % 2 else 18))))
    return join(*parts)


RULER_FULL = join(_ruler_half(-1), _ruler_half(1))


def _snap_f(t, j_snap):
    rel = b.t_of(j_snap, 0)
    if t < rel:
        return 0.0
    dt = t - rel
    return ease_out(clamp01(dt / 0.25)) + 0.12 * math.sin(dt * 18) * math.exp(-dt * 5) * (dt > 0.25)


def _xform(c, side, f):
    xo = RX + side * RL / 2
    c.translate(side * 45 * f, 0)
    c.rotate(-side * 14 * f, xo, RY)          # 两半绕各自外端下折，断口往下掉


def ruler_fn(j_snap):
    def fn(c, k, t):
        f = _snap_f(t, j_snap)
        if f == 0:
            part, tip = partial(RULER_FULL, k)
            c.drawPath(part, marker(BLACK, 9))
            return tip if k < 1 else None
        for side in (-1, 1):
            c.save()
            _xform(c, side, f)
            c.drawPath(_ruler_half(side), marker(BLACK, 9))
            c.restore()
        rel = b.t_of(j_snap, 0)
        a = math.exp(-(t - rel) * 4)
        if a > 0.03:
            for n in range(7):
                ang = n / 7 * 2 * math.pi + 0.4
                r0, r1 = 60, 60 + 120 * ease_out(clamp01((t - rel) / 0.3))
                cx, cy = RX, RY + 110
                c.drawLine(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang), cx + r1 * math.cos(ang),
                           cy + r1 * math.sin(ang), K.paint(RED, a, 8))
        return None

    return fn


def ruler_labels_fn(j_snap):
    def fn(c, k, t):
        f = _snap_f(t, j_snap)
        for side, s, x in RULER_LABELS:
            c.save()
            _xform(c, side, f)
            K.text(c, s, x, RY + 12, 50, "hand", BLACK, clamp01(k * 1.5))
            c.restore()
        return None

    return fn


# ---------------------------------------------------------------- 开局：卷不动了（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("加班五年，没升上去", "灵魂拷问", (1100, 880, 0.85))
T("第5年", 710, 450, 90, RED, k0=0, sfx="pop")
L(clock(710, 700, 110), 1, 1.5, sfx="wood_low")
L(hands_at(710, 700, 110, 10, 0), 1.5, 1.7, RED, 12)
T("晚上十点", 710, 880, 52, k0=1.8, k1=2.5)
L(stairs(910, 1300, 3, 200, 150), 3, 3.5, sfx="wood_high")
L(stick(1410, 1000, 0.5, "up"), 3.5, 3.7)
L(stick(1610, 850, 0.5, "up"), 3.7, 3.9)
T("升职", 1610, 560, 64, RED, k0=4, k1=4.4, sfx="pop")
L(join(stick(1010, 1300, 0.5), face(1010, 1300, 0.5, "sad")), 5, 5.5, BLUE, 9, sfx="rim")
T("我", 900, 1150, 52, BLUE, k0=5.5, k1=5.8)

scene("想开店，又怕人说", "灵魂拷问", (2550, 880, 0.85))
L(shop(2250, 1100, 380, 260), 0, 0.9, sfx="wood_high")
T("小城咖啡馆", 2250, 560, 60, GREEN, k0=1, k1=1.9, sfx="pop")
L(stick(3030, 1300, 0.6), 2, 2.4, BLUE, 9, sfx="wood_high")
L(bubble(2800, 760, 340, 110, 1), 3, 3.3, BLACK, 8, sfx="pop")
T("没出息", 2800, 760, 56, RED, k0=3.3, k1=3.8)
L(bubble(2780, 960, 400, 110, 1), 4, 4.3, BLACK, 8, sfx="pop")
T("好好的班不上", 2780, 960, 50, k0=4.3, k1=4.9)
L(face(3030, 1300, 0.6, "sad"), 5, 5.2, BLUE, 8, sfx="rim")

scene("能换个活法吗？", "灵魂拷问", (1800, 1200, 0.42), shake=[3], flashes=[3])
L(P((640, 455), (780, 445)), 0, 0.4, RED, 10, sfx="rim")
T("第6年", 930, 450, 90, RED, k0=1, k1=1.5, sfx="pop")
T("？", 1800, 1400, 400, RED, k0=3, k1=3.6, sfx="kick")
T("能换个活法吗", 1800, 1740, 110, k0=4, k1=5.1, sfx="pop")
H(5, "ding")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

FIG = (2010, 2170, 2330)
j_ruler = scene("书里有群波希米亚人", "身份的焦虑 · 波希米亚", (1800, 2950, 0.7))
j_snap = j_ruler + 1
L(book(1300, 2720, 360, 240), 0, 0.8, sfx="wood_low")
T("身份的焦虑", 1300, 2520, 64, GREEN, k0=1, k1=1.8, sfx="pop")
T("阿兰 · 德波顿", 1300, 2920, 44, k0=1.9, k1=2.6)
for n, x in enumerate(FIG):
    L(stick(x, 2950, 0.55, hair=True), 2 + n * 0.3, 2.3 + n * 0.3, ACC, 9, sfx="wood_high" if n == 0 else None)
T("第五章 波希米亚", 2170, 2600, 60, ACC, k0=3, k1=3.9, sfx="pop")
b.custom(j_ruler, 4, 4.8, ruler_fn(j_snap), sfx="wood_high")
b.custom(j_ruler, 5, 5.4, ruler_labels_fn(j_snap), sfx="pop")
T("主流的尺子", 1750, 3000, 44, k0=5.4, k1=5.9)

scene("他们不认这把尺", "书中观点 · 不认主流", (1800, 2950, 0.7), shake=[0], flashes=[0])
b.hit(j_snap, 0, "kick", 1.0, "折尺")
H(0, "shaker", 0.6)
for n, x in enumerate(FIG):
    L(face(x, 2950, 0.55, "smile"), 1 + n * 0.25, 1.2 + n * 0.25, ACC, 8, sfx="pop" if n == 0 else None)
T("不比这些", 1800, 3380, 72, RED, k0=3, k1=3.7, sfx="tom")
L(underline(1640, 1960, 3440), 5, 5.4, RED, 8, sfx="ding")

MAIN = (700, 4620)
AUD = (1060, 1200, 1340)
scene("自己挑一群观众", "书中观点 · 换观众", (1050, 4330, 0.85))
L(join(stick(*MAIN, 0.7, "up", hair=True), face(*MAIN, 0.7, "smile")), 0, 0.7, ACC, 9, sfx="wood_high")
for n, x in enumerate(AUD):
    L(stick(x, 4650, 0.45), 1 + n * 0.25, 1.3 + n * 0.25, BLACK, 8, sfx="pop" if n == 0 else None)
T("我的观众", 1200, 4250, 60, GREEN, k0=2, k1=2.7, sfx="pop")
L(rect(1200, 4500, 480, 380, 60), 3, 3.5, GREEN, 7, sfx="wood_high")
for n, (w, x, y) in enumerate((("手艺", 1000, 3990), ("好玩", 1200, 3930), ("自在", 1400, 3990))):
    T(w, x, y, 58, ACC, k0=4 + n * 0.3, k1=4.3 + n * 0.3, sfx="pop" if n == 0 else None)
L(heart(700, 4180, 48), 5, 5.4, RED, 9, sfx="ding")

scene("梭罗住在湖边小屋", "书中提到 · 梭罗", (2650, 4330, 0.85))
T("梭罗 · 瓦尔登湖", 2650, 3930, 66, GREEN, k0=0, k1=1.0, sfx="pop")
L(lake(2950, 4560, 480, 170), 1, 1.6, BLUE, 9, sfx="wood_high")
L(hut(2330, 4520, 240, 190), 2, 2.8, BLACK, 9, sfx="wood_high")
L(stick(2600, 4600, 0.55), 3, 3.4, BLACK, 9, sfx="pop")
T("小木屋", 2330, 4650, 52, k0=3.4, k1=3.9)
for n in range(3):
    yy = 4140 + n * 70
    L(join(P((2860, yy), (3160, yy)), *[circle(2890 + m * 60, yy - 18, 10) for m in range(5)]), 4 + n * 0.3,
      4.3 + n * 0.3, GREEN, 7, sfx="wood_high" if n == 0 else None)
T("种豆子", 3010, 4030, 52, GREEN, k0=5, k1=5.5, sfx="pop")
L(face(2600, 4600, 0.55, "smile"), 5.5, 5.7, BLACK, 8)

LIST = [("大房子", 5260), ("一堆家具", 5380), ("体面衣服", 5500)]
scene("放下越多越富有", "书中观点 · 梭罗", (1050, 5510, 0.85), shake=[5])
for n, (w, y) in enumerate(LIST):
    T(w, 1050, y, 64, k0=n * 0.3, k1=n * 0.3 + 0.3, sfx="pop" if n == 0 else None)
for n, (w, y) in enumerate(LIST):
    hw = len(w) * 34 + 20
    L(P((1050 - hw, y + 4), (1050 + hw, y - 4)), n + 1, n + 1.3, RED, 10, sfx="rim")
T("能放下的越多", 1050, 5680, 72, RED, k0=4, k1=4.9, sfx="pop")
T("越富有", 1050, 5820, 110, RED, k0=5, k1=5.5, sfx="kick")
L(underline(860, 1240, 5900), 5.55, 5.95, RED, 8)

N1, N2 = (2330, 5310), (2970, 5310)
scene("换掉观众和尺子", "书中观点 · 一张图", (2650, 5510, 0.85))
L(circle(*N1, 125), 0, 0.5, ACC, 9, sfx="wood_high")
T("换观众", N1[0], N1[1], 54, ACC, k0=1, k1=1.5, sfx="pop")
L(circle(*N2, 125), 2, 2.5, ACC, 9, sfx="wood_high")
T("换尺子", N2[0], N2[1], 54, ACC, k0=2.5, k1=3.0)
L(join(arrow((N1[0] + 40, N1[1] + 140), (2590, 5640), 0.1, 40), arrow((N2[0] - 40, N2[1] + 140), (2710, 5640), -0.1, 40)),
  3, 3.6, GREEN, 9, sfx="wood_high")
T("没那么慌", 2650, 5740, 76, RED, k0=4, k1=4.7, sfx="pop")
T("解法⑤：波希米亚", 2650, 5080, 60, RED, k0=5, k1=5.9, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 7900), (2650, 7900), (950, 8800), (2650, 8800)]
scene("身边就有例子", "身边的例子", (1800, 8350, 0.34))
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), n, n + 0.6, GREEN, 8, sfx="wood_high")
H(4, "ding")

scene("公司比职级，跑团比里程", "例子 · 职场", (950, 7900, 0.85))
L(P((950, 7580), (950, 8230)), 0, 0.3, GREEN, 5)
T("公司", 650, 7600, 56, k0=0, k1=0.4, sfx="pop")
for n, w in enumerate(("总监", "经理", "专员")):
    L(rect(650, 7750 + n * 115, 240, 85, 10), 1 + n * 0.4, 1.2 + n * 0.4, BLACK, 7, sfx="wood_high" if n == 0 else None)
    T(w, 650, 7750 + n * 115, 46, k0=1.2 + n * 0.4, k1=1.4 + n * 0.4)
L(stick(650, 8250, 0.42), 2.2, 2.5, BLUE, 8)
L(rect(650, 7980, 290, 125, 14), 2.5, 2.8, RED, 8)
b.hit(J(), 2, "pop")
T("跑团", 1250, 7600, 56, k0=3, k1=3.36, sfx="pop")
L(join(stick(1130, 8250, 0.45, "up"), stick(1370, 8250, 0.45, "up")), 3.4, 3.9, BLACK, 8)
L(bubble(1250, 7780, 360, 110, -1), 4, 4.3, BLACK, 7, sfx="wood_high")
T("今天跑多远？", 1250, 7780, 46, k0=4.3, k1=4.9)
T("没人问几级", 1250, 7980, 48, GREEN, k0=5, k1=5.6, sfx="pop")

scene("亲戚说可惜，熟客说好喝", "例子 · 生活", (2650, 7900, 0.85))
L(P((2650, 7580), (2650, 8230)), 0, 0.3, GREEN, 5)
T("亲戚", 2350, 7600, 56, k0=0, k1=0.4, sfx="pop")
L(join(stick(2250, 8250, 0.5), stick(2450, 8250, 0.5)), 1, 1.5, BLACK, 8, sfx="wood_high")
L(bubble(2350, 7770, 400, 110, 1), 2, 2.3, BLACK, 7, sfx="pop")
T("开店？可惜了", 2350, 7770, 50, RED, k0=2.3, k1=2.9)
L(join(face(2250, 8250, 0.5, "flat"), face(2450, 8250, 0.5, "flat")), 3, 3.2, BLACK, 7, sfx="rim")
T("熟客", 2950, 7600, 56, k0=3.3, k1=3.7)
L(cup(2850, 8080, 0.6), 4, 4.4, BLACK, 8, sfx="pop")
L(bubble(2950, 7780, 300, 110, 1), 4.4, 4.7, BLACK, 7)
T("好喝！", 2950, 7780, 56, RED, k0=5, k1=5.4, sfx="pop")
L(join(stick(3130, 8250, 0.5), face(3130, 8250, 0.5, "smile")), 5.4, 5.9, BLACK, 8)

scene("老爸在钓鱼群是师傅", "例子 · 家庭", (950, 8800, 0.85))
L(P((950, 8480), (950, 9130)), 0, 0.3, GREEN, 5)
T("单位", 650, 8500, 56, k0=0, k1=0.4, sfx="pop")
L(desk(700, 8920, 280), 1, 1.5, BLACK, 8, sfx="wood_high")
L(join(stick(470, 9150, 0.55), face(470, 9150, 0.55, "flat")), 2, 2.5, BLUE, 9, sfx="wood_low")
T("钓鱼群", 1250, 8500, 56, k0=3, k1=3.5, sfx="pop")
L(join(stick(1100, 9150, 0.55, "point"), face(1100, 9150, 0.55, "smile")), 4, 4.5, BLUE, 9, sfx="wood_high")
L(rod(1166, 9023, 1340, 8750, 250), 4.5, 5.0, BLACK, 7)
T("师傅！", 1440, 8660, 60, RED, k0=5, k1=5.4, sfx="ding")
L(stick(1470, 9150, 0.42, "up"), 5.4, 5.8, BLACK, 8)

scene("她卖了车去学画", "例子 · 生活", (2650, 8800, 0.85))
L(P((2650, 8480), (2650, 9130)), 0, 0.3, GREEN, 5)
T("卖车", 2350, 8500, 56, k0=0, k1=0.4, sfx="pop")
L(car(2350, 8800), 1, 1.6, BLACK, 8, sfx="wood_high")
L(cross(2350, 8710, 95), 2, 2.3, RED, 11, sfx="rim")
L(bike(2350, 9140), 3, 3.6, BLUE, 8, sfx="pop")
T("学画", 2950, 8500, 56, GREEN, k0=3.6, k1=4.0)
L(easel(2900, 8800), 4, 4.6, BLACK, 8, sfx="wood_high")
L(join(stick(3150, 9100, 0.45, "point"), face(3150, 9100, 0.45, "smile")), 4.6, 5.0, BLUE, 8)
L(P((2800, 8860), (2870, 8760), (2930, 8830), (2990, 8740), (3010, 8860)), 5, 5.4, ACC, 8, sfx="ding")

scene("换群人看你，心就松了", "身边的例子", (1800, 8350, 0.34), shake=[4])
for n, (x, y) in enumerate(((1250, 7980), (2950, 7980), (1300, 8900), (2950, 8880))):
    L(circle(x, y, 270), n, n + 0.4, RED, 9, sfx="pop")
T("换一群人看你，心就松了", 1800, 9420, 130, RED, k0=4, k1=5.0, sfx="kick")
H(5, "ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 10400), (2650, 10400), (950, 11600), (2650, 11600)]
FR = (650, 950, 1250)
scene("先找一群同好", "第一步 · 找同好", (950, 10480, 0.85))
T("① 找同好", 950, 10100, 76, BLUE, k0=0, k1=0.8, sfx="pop")
for n, x in enumerate(FR):
    L(stick(x, 10700, 0.55), 1 + n * 0.3, 1.3 + n * 0.3, BLACK, 9, sfx="wood_high" if n == 0 else None)
L(heart(950, 10390, 46), 2, 2.4, RED, 9, sfx="pop")
L(join(*[face(x, 10700, 0.55, "smile") for x in FR]), 3, 3.4, BLACK, 8, sfx="ding")
for n, w in enumerate(("读书会", "跑团", "手作课")):
    T(w, FR[n], 10770, 50, GREEN, k0=4 + n * 0.3, k1=4.3 + n * 0.3, sfx="pop" if n == 0 else None)
T("没人问工资", 620, 10290, 50, GREEN, k0=5, k1=5.6, sfx="pop")

scene("列张能放下的单", "第二步 · 列清单", (2650, 10480, 0.85))
T("② 列放下清单", 2650, 10100, 72, BLUE, k0=0, k1=1.0, sfx="pop")
T("开销", 2350, 10280, 60, k0=1, k1=1.4, sfx="pop")
T("面子", 2950, 10280, 60, k0=1.5, k1=1.9)
L(P((2650, 10240), (2650, 10600)), 2, 2.3, GREEN, 6, sfx="wood_high")
T("换新车", 2350, 10410, 52, k0=2.4, k1=2.9)
T("撑场面的饭局", 2950, 10410, 48, k0=3, k1=3.7, sfx="pop")
L(P((2260, 10414), (2440, 10406)), 4, 4.3, RED, 9, sfx="rim")
L(P((2790, 10414), (3110, 10406)), 4.4, 4.7, RED, 9)
T("每月省一笔", 2650, 10600, 56, GREEN, k0=5, k1=5.6, sfx="ding")

scene("周末摆摊试三个月", "第三步 · 小步试", (950, 11600, 0.85))
T("③ 小步试", 950, 11300, 76, BLUE, k0=0, k1=0.8, sfx="pop")
L(stall(760, 11930, 360), 1, 1.7, BLACK, 9, sfx="wood_high")
T("咖啡", 760, 11872, 50, k0=1.7, k1=2.0)
L(stick(480, 11930, 0.5), 2, 2.4, BLUE, 9, sfx="wood_high")
L(cup(740, 11760, 0.32), 2.4, 2.7, BLACK, 6)
L(stick(1080, 11930, 0.5, "hold"), 3, 3.4, BLACK, 9, sfx="pop")
T("周六卖出12杯", 1220, 11450, 48, RED, k0=3.4, k1=3.9)
L(calendar(1350, 11770, 220, 200), 4, 4.5, BLACK, 8, sfx="wood_high")
T("3个月", 1350, 11800, 50, RED, k0=5, k1=5.4, sfx="pop")
L(check(1490, 11650, 36), 5.5, 5.8, GREEN, 9)

scene("留好退路再动身", "第四步 · 留退路", (2650, 11600, 0.85))
T("④ 留退路", 2650, 11300, 76, BLUE, k0=0, k1=0.8, sfx="pop")
L(jar(2400, 11770), 1, 1.5, BLACK, 9, sfx="wood_high")
b.custom(J(), 2, 2.8, coins_fn(2400, 11770), sfx="pop")
T("够花半年", 2400, 11960, 52, RED, k0=3, k1=3.6, sfx="pop")
L(join(stick(2760, 11930, 0.55), face(2760, 11930, 0.55, "smile")), 4, 4.5, BLUE, 9, sfx="wood_high")
L(arrow((2830, 11780), (2990, 11780), 0.05, 34), 4.5, 4.8, GREEN, 8)
L(shop(3080, 11930, 200, 150), 5, 5.6, BLACK, 7, sfx="wood_high")
L(check(3080, 11490, 40), 5.6, 5.9, GREEN, 9)

# ---------------------------------------------------------------- 收尾（场景 20–21）

scene("用自己的尺子过", "一句话", (1800, 6300, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("这一季讲完了", "评论区见", (1800, 12950, 0.8))
H(0, "cymbal", 0.5)
T("你最想放下哪一样？", 1800, 12860, 80, RED, k0=1, k1=2.6)
H(1, "pop")
T("《身份的焦虑》这一季讲完了，谢谢你一路陪着看", 1800, 13020, 46, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "bohemia", "波希米亚", "不想卷了，能换个活法吗？", ACC, b.shots,
                 [f"{BOOK}第二部分“解决方法”第五章“波希米亚”（转述）",
                  "原书：Alain de Botton, Status Anxiety, Hamish Hamilton / Pantheon, 2004",
                  "中译本：《身份的焦虑》，陈广兴、南治国译，上海译文出版社"],
                 "不想卷了|换个【活法】", 4,
                 ["书中观点均为转述：波希米亚式的人拒绝主流社会的成功标准，自己选一群看重别的东西的人做自己的“观众”；"
                  "书中提到梭罗在瓦尔登湖边过简单的生活，意思是人能放下的东西越多就越富有（转述，非逐字引文）。"
                  "出处：Alain de Botton, Status Anxiety (Hamish Hamilton / Pantheon, 2004)，第二部分“解决方法”第五章“波希米亚”；"
                  "中译本《身份的焦虑》（阿兰·德波顿著，陈广兴、南治国译，上海译文出版社）。",
                  "折尺上的“工资、房子、头衔、车子”、“手艺、好玩、自在”、“换观众 + 换尺子 → 没那么慌”的图，"
                  "以及小木屋、种豆子、“大房子、一堆家具、体面衣服”的划掉清单，均为对书中观点的通俗化示意；"
                  "梭罗自建小屋、种豆为《瓦尔登湖》里广为人知的细节，画面不画真实人物肖像。",
                  "开局（加班第五年没升上去、想去小城开咖啡馆、怕人说没出息）、公司看职级与跑团、亲戚与熟客、老爸在单位与钓鱼群、"
                  "卖车学画均为现实场景示意，不指向任何具体公司或个人；“周六卖出12杯”“试3个月”“够花半年”等数字为示意。",
                  "四步做法（找一群同好、列一张能放下的清单、周末摆摊小步试、留好退路再动身）为据书中思路整理的建议，"
                  "不鼓励辞职或裸辞。"],
                 tags="#躺平 #生活方式")
    return b.attach(ep)
