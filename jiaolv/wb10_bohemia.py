"""10 波希米亚（白板手绘版）：不想卷了，能换个活法吗？（系列最后一讲）

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
SQUARE_SHOT = 10

b = Board(size=(3600, 11150))


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
    logs = [P((x - w / 2, y - h + k * 45), (x - 50, y - h + k * 45)) for k in (1, 2, 3)]
    return join(walls, roof, door, *logs)


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


# ---------------------------------------------------------------- 折尺（镜头 8 画出，镜头 9 drop 折断）

RX, RY, RL, RH = 2650, 2810, 1000, 110
RULER_LABELS = [(-1, "工资", RX - 380), (-1, "房子", RX - 150), (1, "头衔", RX + 150), (1, "车子", RX + 380)]


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


# ---------------------------------------------------------------- 开局：卷不动了（镜头 1–6）

b.shot("卷了五年", "灵魂拷问", view=(950, 850, 0.85))
L(desk(950, 1150, 380), 0, 0.6, sfx="wood_high")
L(stick(1280, 1350, 0.75, "hold"), 0.6, 1.0)
T("第5年", 560, 620, 80, RED, k0=1, sfx="pop")
L(clock(560, 880, 110), 2, 2.5, sfx="wood_low")
L(hands_at(560, 880, 110, 10, 0), 2.5, 2.7, RED, 12)
T("晚上十点", 560, 1060, 52, k0=3, sfx="pop")

b.shot("还是没升上去", "灵魂拷问", view=(2650, 850, 0.85))
L(stairs(2150, 1250), 0, 0.8, sfx="wood_high")
L(stick(2250, 1250, 0.5), 1, 1.4, BLUE, 9, sfx="pop")
L(stick(2775, 950, 0.5, "up"), 1.4, 1.8)
L(stick(3025, 800, 0.5, "up"), 1.7, 2.1)
T("升职", 3025, 540, 64, RED, k0=2, sfx="pop")
L(face(2250, 1250, 0.5, "sad"), 3, 3.2, BLUE, 8, sfx="rim")
T("我", 2250, 1340, 52, BLUE, k0=3.2)

b.shot("想去小城开咖啡馆", "灵魂拷问", view=(950, 1800, 0.85))
L(shop(800, 2150, 440, 300), 0, 0.9, sfx="wood_high")
T("小店", 800, 1725, 56, k0=1, sfx="pop")
L(cup(1300, 1990, 0.8), 2, 2.6, BLACK, 9, sfx="pop")
T("小城", 1300, 1700, 60, GREEN, k0=3, sfx="pop")

b.shot("又怕人说没出息", "灵魂拷问", view=(2650, 1800, 0.85))
L(stick(2300, 2150, 0.75), 0, 0.5, BLUE, 9, sfx="wood_high")
L(bubble(2850, 1600, 400, 120, -1), 1, 1.4, BLACK, 8, sfx="pop")
T("没出息", 2850, 1600, 56, RED, k0=1.4)
L(bubble(2900, 1880, 460, 120, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("好好的班不上", 2900, 1880, 52, k0=2.4)
L(face(2300, 2150, 0.75, "sad"), 3, 3.2, BLUE, 8, sfx="rim")

b.shot("一拖又是一年", "灵魂拷问", view=(950, 850, 0.85))
L(P((470, 625), (655, 615)), 0, 0.4, RED, 10, sfx="rim")
T("第6年", 900, 620, 80, RED, k0=1, sfx="pop")
L(face(1280, 1350, 0.75, "flat"), 2, 2.2, BLACK, 9, sfx="wood_high")
T("唉", 1280, 990, 64, k0=3, sfx="pop")

b.shot("能换个活法吗？", "灵魂拷问", view=(1800, 1350, 0.42), flashes=[0])
T("？", 1800, 1350, 520, RED, k0=0, k1=0.6, sfx="kick")
T("能换个活法吗", 1800, 2380, 120, k0=1.0, k1=2.0, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "身份的焦虑", view=(1050, 2950, 0.9))
L(book(750, 2950, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 750, 2710, 76, GREEN, k0=1.0, sfx="pop")
T("阿兰 · 德波顿", 750, 3190, 50, k0=2.0, sfx="pop")
T("第五招", 1350, 2860, 60, RED, k0=3, sfx="pop")
T("波希米亚", 1350, 2970, 60, ACC, k0=3.3)

b.shot("有群人叫波希米亚", "书中观点 · 波希米亚", view=(2650, 2950, 0.85))
j_ruler = J()
j_snap = j_ruler + 1
T("波希米亚", 2650, 2560, 76, ACC, k0=0, sfx="pop")
for n, x in enumerate((2300, 2470, 2640)):
    L(stick(x, 3350, 0.55, hair=True), 1 + n * 0.25, 1.4 + n * 0.25, ACC, 9, sfx="wood_high" if n == 0 else None)
b.custom(j_ruler, 2, 2.8, ruler_fn(j_snap), sfx="wood_high")
b.custom(j_ruler, 3, 3.4, ruler_labels_fn(j_snap), sfx="pop")
T("主流的尺子", 2650, 2680, 50, k0=3.4)

b.shot("他们不认这把尺", "书中观点 · 不认主流", view=(2650, 2950, 0.85), shake=[0], flashes=[0])
b.hit(j_snap, 0, "kick", 1.0, "折尺")
H(0, "shaker", 0.6)
for n, x in enumerate((2300, 2470, 2640)):
    L(face(x, 3350, 0.55, "smile"), 1 + n * 0.2, 1.2 + n * 0.2, ACC, 8, sfx="pop" if n == 0 else None)
T("不比这些", 3000, 3250, 64, RED, k0=2, sfx="tom")
H(3, "pop", 0.6)

MAIN = (700, 4620)
AUD = (1060, 1200, 1340)
b.shot("自己挑一群观众", "书中观点 · 换观众", view=(1050, 4300, 0.85))
L(stick(*MAIN, 0.7, "up", hair=True), 0, 0.6, ACC, 9, sfx="wood_high")
L(face(*MAIN, 0.7, "smile"), 0.6, 0.8, ACC, 8)
for n, x in enumerate(AUD):
    L(stick(x, 4650, 0.45), 1 + n * 0.2, 1.3 + n * 0.2, BLACK, 8, sfx="pop" if n == 0 else None)
T("我的观众", 1200, 4250, 60, GREEN, k0=2, sfx="pop")
L(rect(1200, 4525, 480, 400, 60), 3, 3.6, GREEN, 7, sfx="wood_high")

b.shot("他们看重别的", "书中观点 · 换观众", view=(1050, 4300, 0.85))
for n, (w, x, y) in enumerate((("手艺", 1000, 3990), ("好玩", 1200, 3930), ("自在", 1400, 3990))):
    T(w, x, y, 58, ACC, k0=n, sfx="pop")
L(heart(700, 4180, 48), 3, 3.4, RED, 9, sfx="ding")

b.shot("书里还写了梭罗", "书中提到 · 梭罗", view=(2650, 4300, 0.85))
T("梭罗 · 瓦尔登湖", 2650, 3900, 66, GREEN, k0=0, sfx="pop")
L(lake(2950, 4560, 480, 170), 1, 1.6, BLUE, 9, sfx="wood_high")
L(hut(2330, 4520, 240, 190), 2, 2.8, BLACK, 9, sfx="wood_high")
L(stick(2600, 4600, 0.55), 3, 3.4, BLACK, 9, sfx="pop")

b.shot("在湖边过简单日子", "书中提到 · 梭罗", view=(2650, 4300, 0.85))
T("小木屋", 2330, 4650, 52, k0=0, sfx="pop")
for n in range(3):
    yy = 4140 + n * 70
    L(join(P((2860, yy), (3160, yy)), *[circle(2890 + m * 60, yy - 18, 10) for m in range(5)]), 1 + n * 0.25,
      1.3 + n * 0.25, GREEN, 7, sfx="wood_high" if n == 0 else None)
T("种豆子", 3010, 4030, 52, GREEN, k0=2, sfx="pop")
L(face(2600, 4600, 0.55, "smile"), 3, 3.2, BLACK, 8, sfx="ding")

LIST = [("大房子", 5000), ("一堆家具", 5120), ("体面衣服", 5240)]
b.shot("东西减到最少", "书中提到 · 梭罗", view=(1050, 5250, 0.85))
for n, (w, y) in enumerate(LIST):
    T(w, 1050, y, 64, k0=n * 0.3, k1=n * 0.3 + 0.4, sfx="pop" if n == 0 else None)
for n, (w, y) in enumerate(LIST):
    hw = len(w) * 34 + 20
    L(P((1050 - hw, y + 4), (1050 + hw, y - 4)), n + 1, n + 1.3, RED, 10, sfx="rim")

b.shot("放下越多越富有", "书中观点 · 梭罗", view=(1050, 5250, 0.85), shake=[1])
T("能放下的越多", 1050, 5420, 72, RED, k0=0, sfx="pop")
T("越富有", 1050, 5560, 110, RED, k0=1, k1=1.5, sfx="kick")
L(underline(860, 1240, 5640), 2, 2.5, RED, 8, sfx="ding")
H(3, "pop", 0.6)

N1, N2 = (2330, 5050), (2970, 5050)
b.shot("换掉观众和尺子", "书中观点 · 一张图", view=(2650, 5250, 0.85))
L(circle(*N1, 125), 0, 0.5, ACC, 9, sfx="wood_high")
T("换观众", N1[0], N1[1], 54, ACC, k0=0.5)
L(circle(*N2, 125), 1, 1.5, ACC, 9, sfx="wood_high")
T("换尺子", N2[0], N2[1], 54, ACC, k0=1.5)
L(join(arrow((N1[0] + 40, N1[1] + 140), (2590, 5380), 0.1, 40), arrow((N2[0] - 40, N2[1] + 140), (2710, 5380), -0.1, 40)),
  2, 2.6, GREEN, 9, sfx="wood_high")
T("没那么慌", 2650, 5480, 76, RED, k0=3, sfx="pop")

b.shot("书里压轴的一招", "书中观点 · 第五招", view=(1800, 4150, 0.3), shake=[2])
for n, (a, c_) in enumerate((((1400, 3100), (1500, 4000)), ((2650, 3500), (2650, 3820)))):
    L(arrow(a, c_, 0.15, 50), n, n + 0.5, GREEN, 10, sfx="wood_high")
T("解法⑤：波希米亚", 1800, 5850, 120, RED, k0=2, k1=3.0, sfx="kick")
H(3, "ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 6800), (2650, 6800), (950, 7700), (2650, 7700)]
b.shot("身边就有例子", "身边的例子", view=(1800, 7250, 0.355))
T("身边的例子", 1800, 6250, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("公司里只看职级", "例子 · 职场", view=(950, 6800, 0.85))
L(P((950, 6480), (950, 7130)), 0, 0.3, GREEN, 5)
T("公司", 650, 6500, 56, k0=0, sfx="pop")
for n, w in enumerate(("总监", "经理", "专员")):
    L(rect(650, 6650 + n * 115, 240, 85, 10), 1 + n * 0.25, 1.25 + n * 0.25, BLACK, 7, sfx="wood_high" if n == 0 else None)
    T(w, 650, 6650 + n * 115, 46, k0=1.25 + n * 0.25, k1=1.45 + n * 0.25)
L(stick(650, 7150, 0.42), 2, 2.4, BLUE, 8, sfx="pop")
L(rect(650, 6880, 290, 125, 14), 3, 3.4, RED, 8, sfx="rim")

b.shot("跑团只问跑多远", "例子 · 职场", view=(950, 6800, 0.85))
T("跑团", 1250, 6500, 56, k0=0, sfx="pop")
L(join(stick(1130, 7150, 0.45, "up"), stick(1370, 7150, 0.45, "up")), 1, 1.6, BLACK, 8, sfx="wood_high")
L(bubble(1250, 6680, 360, 110, -1), 2, 2.3, BLACK, 7, sfx="pop")
T("今天跑多远？", 1250, 6680, 46, k0=2.3)
T("没人问几级", 1250, 6880, 48, GREEN, k0=3, sfx="pop")

b.shot("亲戚说开店可惜", "例子 · 生活", view=(2650, 6800, 0.85))
L(P((2650, 6480), (2650, 7130)), 0, 0.3, GREEN, 5)
T("亲戚", 2350, 6500, 56, k0=0, sfx="pop")
L(join(stick(2250, 7150, 0.5), stick(2450, 7150, 0.5)), 1, 1.6, BLACK, 8, sfx="wood_high")
L(bubble(2350, 6670, 400, 110, 1), 2, 2.3, BLACK, 7, sfx="pop")
T("开店？可惜了", 2350, 6670, 50, RED, k0=2.3)
L(join(face(2250, 7150, 0.5, "flat"), face(2450, 7150, 0.5, "flat")), 3, 3.2, BLACK, 7, sfx="rim")

b.shot("熟客夸咖啡好喝", "例子 · 生活", view=(2650, 6800, 0.85))
T("熟客", 2950, 6500, 56, k0=0, sfx="pop")
L(cup(2850, 6980, 0.6), 1, 1.5, BLACK, 8, sfx="pop")
L(bubble(2950, 6680, 300, 110, 1), 2, 2.3, BLACK, 7, sfx="pop")
T("好喝！", 2950, 6680, 56, RED, k0=2.3)
L(join(stick(3130, 7150, 0.5), face(3130, 7150, 0.5, "smile")), 3, 3.5, BLACK, 8, sfx="wood_high")

b.shot("老爸在单位不起眼", "例子 · 家庭", view=(950, 7700, 0.85))
L(P((950, 7380), (950, 8030)), 0, 0.3, GREEN, 5)
T("单位", 650, 7400, 56, k0=0, sfx="pop")
L(desk(700, 7820, 280), 1, 1.5, BLACK, 8, sfx="wood_high")
L(stick(470, 8050, 0.55), 2, 2.4, BLUE, 9, sfx="pop")
L(face(470, 8050, 0.55, "flat"), 3, 3.2, BLUE, 8, sfx="wood_low")

b.shot("钓鱼群里是师傅", "例子 · 家庭", view=(950, 7700, 0.85))
T("钓鱼群", 1250, 7400, 56, k0=0, sfx="pop")
L(join(stick(1100, 8050, 0.55, "point"), face(1100, 8050, 0.55, "smile")), 1, 1.5, BLUE, 9, sfx="wood_high")
L(rod(1166, 7923, 1340, 7650, 250), 1.5, 2.0, BLACK, 7)
L(stick(1470, 8050, 0.42, "up"), 2, 2.4, BLACK, 8, sfx="pop")
T("师傅！", 1440, 7560, 60, RED, k0=3, sfx="ding")

b.shot("她卖了车骑车", "例子 · 生活", view=(2650, 7700, 0.85))
L(P((2650, 7380), (2650, 8030)), 0, 0.3, GREEN, 5)
T("卖车", 2350, 7400, 56, k0=0, sfx="pop")
L(car(2350, 7700), 1, 1.6, BLACK, 8, sfx="wood_high")
L(cross(2350, 7610, 95), 2, 2.3, RED, 11, sfx="rim")
L(bike(2350, 8040), 3, 3.6, BLUE, 8, sfx="pop")

b.shot("省下的钱去学画", "例子 · 生活", view=(2650, 7700, 0.85))
T("学画", 2950, 7400, 56, GREEN, k0=0, sfx="pop")
L(easel(2900, 7700), 1, 1.6, BLACK, 8, sfx="wood_high")
L(join(stick(3150, 8000, 0.45, "point"), face(3150, 8000, 0.45, "smile")), 2, 2.5, BLUE, 8, sfx="pop")
L(P((2800, 7760), (2870, 7660), (2930, 7730), (2990, 7640), (3010, 7760)), 3, 3.4, ACC, 8, sfx="ding")

b.shot("看你的人换了", "身边的例子", view=(1800, 7250, 0.355))
for n, (x, y) in enumerate(((1250, 6880), (2950, 6880), (1300, 7800), (2950, 7780))):
    L(circle(x, y, 270), n, n + 0.4, RED, 9, sfx="pop")

b.shot("心就跟着松了", "身边的例子", view=(1800, 7250, 0.355), shake=[0])
T("换一群人看你，心就松了", 1800, 8290, 120, RED, k0=0, k1=1.0, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 9100), (2650, 9100), (950, 10000), (2650, 10000)]
b.shot("想换活法这样试", "具体做法", view=(1800, 9550, 0.355))
T("想换活法，分四步", 1800, 8560, 130, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

FR = (650, 950, 1250)
b.shot("先找一群同好", "第一步 · 找同好", view=(950, 9100, 0.85))
T("① 找同好", 950, 8800, 76, BLUE, k0=0, sfx="pop")
for n, x in enumerate(FR):
    L(stick(x, 9400, 0.55), 1 + n * 0.25, 1.35 + n * 0.25, BLACK, 9, sfx="wood_high" if n == 0 else None)
L(heart(950, 9090, 46), 2, 2.4, RED, 9, sfx="pop")
L(join(*[face(x, 9400, 0.55, "smile") for x in FR]), 3, 3.4, BLACK, 8, sfx="ding")

b.shot("读书会跑团都行", "第一步 · 找同好", view=(950, 9100, 0.85))
for n, w in enumerate(("读书会", "跑团", "手作课")):
    T(w, FR[n], 9470, 50, GREEN, k0=n, sfx="pop")

b.shot("去了只聊爱好", "第一步 · 找同好", view=(950, 9100, 0.85))
L(bubble(1270, 8980, 360, 100, -1), 0, 0.4, BLACK, 7, sfx="wood_high")
T("你拍得真好", 1270, 8980, 48, k0=0.4)
T("没人问工资", 620, 8990, 50, GREEN, k0=1, sfx="pop")
L(underline(490, 750, 9040, 10, 30), 2, 2.4, GREEN, 7, sfx="ding")

b.shot("列张能放下的单", "第二步 · 列清单", view=(2650, 9100, 0.85))
T("② 列放下清单", 2650, 8800, 72, BLUE, k0=0, sfx="pop")
T("开销", 2350, 8980, 60, k0=1, sfx="pop")
T("面子", 2950, 8980, 60, k0=2, sfx="pop")
L(P((2650, 8940), (2650, 9300)), 3, 3.3, GREEN, 6, sfx="wood_high")

b.shot("换车的钱先不花", "第二步 · 列清单", view=(2650, 9100, 0.85))
T("换新车", 2350, 9110, 52, k0=0, sfx="pop")
T("没去的健身卡", 2350, 9230, 48, k0=1, sfx="pop")
L(P((2260, 9114), (2440, 9106)), 2, 2.3, RED, 9, sfx="rim")
L(P((2190, 9234), (2510, 9226)), 3, 3.3, RED, 9, sfx="rim")

b.shot("撑面子的局少去", "第二步 · 列清单", view=(2650, 9100, 0.85))
T("撑场面的饭局", 2950, 9110, 48, k0=0, sfx="pop")
T("跟风买的包", 2950, 9230, 48, k0=1, sfx="pop")
L(join(P((2790, 9114), (3110, 9106)), P((2815, 9234), (3085, 9226))), 2, 2.5, RED, 9, sfx="rim")
T("每月省一笔", 2650, 9390, 56, GREEN, k0=3, sfx="ding")

b.shot("先小步试一试", "第三步 · 小步试", view=(950, 10000, 0.85))
T("③ 小步试", 950, 9700, 76, BLUE, k0=0, sfx="pop")
L(stall(760, 10330, 360), 1, 1.7, BLACK, 9, sfx="wood_high")
T("咖啡", 760, 10272, 50, k0=2, sfx="pop")
L(stick(480, 10330, 0.5), 3, 3.4, BLUE, 9, sfx="wood_high")

b.shot("周末摆个小摊", "第三步 · 小步试", view=(950, 10000, 0.85))
L(cup(740, 10160, 0.32), 0, 0.3, BLACK, 6, sfx="pop")
L(stick(1080, 10330, 0.5, "hold"), 1, 1.4, BLACK, 9, sfx="wood_high")
T("来一杯", 1080, 10080, 50, k0=2, sfx="pop")
T("周六卖出12杯", 1270, 9850, 48, RED, k0=3, sfx="pop")

b.shot("试三个月再定", "第三步 · 小步试", view=(950, 10000, 0.85))
L(calendar(1350, 10170, 220, 200), 0, 0.6, BLACK, 8, sfx="wood_high")
T("3个月", 1350, 10200, 50, RED, k0=1, sfx="pop")
T("再决定", 1350, 10340, 50, k0=2, sfx="pop")
L(check(1490, 10050, 36), 3, 3.3, GREEN, 9, sfx="ding")

b.shot("给自己留条退路", "第四步 · 留退路", view=(2650, 10000, 0.85))
T("④ 留退路", 2650, 9700, 76, BLUE, k0=0, sfx="pop")
L(jar(2400, 10170), 1, 1.5, BLACK, 9, sfx="wood_high")
b.custom(J(), 2, 2.8, coins_fn(2400, 10170), sfx="pop")
T("够花半年", 2400, 10360, 52, RED, k0=3, sfx="pop")

b.shot("攒够了再动身", "第四步 · 留退路", view=(2650, 10000, 0.85))
L(join(stick(2760, 10330, 0.55), face(2760, 10330, 0.55, "smile")), 0, 0.5, BLUE, 9, sfx="wood_high")
L(arrow((2830, 10180), (2990, 10180), 0.05, 34), 1, 1.3, GREEN, 8, sfx="pop")
L(shop(3120, 10330, 200, 150), 2, 2.7, BLACK, 7, sfx="wood_high")
L(check(3120, 9890, 40), 3, 3.3, GREEN, 9, sfx="ding")

b.shot("用自己的尺子过", "一句话", view=(1800, 5400, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("这一季讲完了", "评论区见", view=(1800, 10850, 0.8))
T("你最想放下哪一样？", 1800, 10760, 80, RED, k0=0.5, k1=1.8)
T("《身份的焦虑》这一季讲完了，谢谢你一路陪着看", 1800, 10920, 46, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "bohemia", "波希米亚", "不想卷了，能换个活法吗？", ACC, b.shots,
                 [f"{BOOK}第二部分“解决方法”第五章“波希米亚”（转述）",
                  "原书：Alain de Botton, Status Anxiety, Hamish Hamilton / Pantheon, 2004",
                  "中译本：《身份的焦虑》，陈广兴、南治国译，上海译文出版社"],
                 "不想卷了|换个【活法】", 8,
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
