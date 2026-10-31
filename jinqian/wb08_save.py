"""08 存钱（白板手绘版）：没想好买什么，也要存钱？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（形式 D 误区对照）：开局三张便签，三句常听的话都打着问号 →
误区一 ✗「工资低，存不下」/ 书里说 ✓ 收入和回报管不全，存多少归你管（小猪罐点头）→
drop：书中石油危机的例子——1970 年代之后，省下来的油比新找到的油更多（左边油井两桶，右边省油车四桶）→
亮书 → 省下的就是赚到的：油桶换成硬币落进小猪罐 →
误区二 ✗「存钱要有用途」/ 书里说 ✓ 不用为哪样东西存，为说不准的明天存 → 存下的是选择（三条岔路：换工作、等一等、说不）→
误区三 ✗「钱多了自然存得下」→ 书里说：收入过了某条线，多出来的花销多半为面子 →
三个做法（发薪先存再花 / 存一笔没名目的钱 / 购物单划掉一项面子开销）→ 拉远看全板三对 ✗ / ✓ → 评论区互动。
书中观点为转述（Morgan Housel, The Psychology of Money, Harriman House, 2020；中译本《金钱心理学》，
摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023，第 10 章“存钱”）；三张便签上的说法、例子与做法为示意 / 据书中思路整理。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, check, circle, cross, join,
                               marker, partial, rect)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#B8862B"
SQUARE_SHOT = 8                  # 场景 9：小猪罐长出三条岔路（角色 + 核心示意）

b = Board(size=(3600, 14400))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = J() if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def tilt(path: skia.Path, deg, x, y) -> skia.Path:
    out = skia.Path(path)
    out.transform(skia.Matrix.RotateDeg(deg, skia.Point(x, y)))
    return out


def note(x, y, w=420, h=380, deg=0.0) -> skia.Path:
    """便签：右下角折角 + 顶上一条胶带。"""
    f = 60
    body = P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - f), (x + w / 2 - f, y + h / 2),
             (x - w / 2, y + h / 2), close=True)
    fold = P((x + w / 2, y + h / 2 - f), (x + w / 2 - f, y + h / 2 - f), (x + w / 2 - f, y + h / 2))
    tape = rect(x, y - h / 2, 130, 44, 6)
    return tilt(join(body, fold, tape), deg, x, y)


def coin(x, y, r=50) -> skia.Path:
    return join(circle(x, y, r), P((x, y - r * 0.5), (x, y + r * 0.5)))


def barrel(x, y, w=120, h=140) -> skia.Path:
    """油桶：(x, y) 为桶底中点。"""
    return join(rect(x, y - h / 2, w, h, 14), P((x - w / 2, y - h * 0.3), (x + w / 2, y - h * 0.3)),
                P((x - w / 2, y - h * 0.7), (x + w / 2, y - h * 0.7)))


def barrels(x, y, n, w=120, h=140) -> skia.Path:
    return join(*[barrel(x, y - i * h, w, h) for i in range(n)])


def derrick(x, y, s=1.0) -> skia.Path:
    """油井架：(x, y) 为地面中点。"""
    H0, W0, W1 = 460 * s, 130 * s, 28 * s

    def hw(h):
        return W0 - (W0 - W1) * h / H0

    parts = [P((x - W0, y), (x - W1, y - H0)), P((x + W0, y), (x + W1, y - H0)),
             P((x - W1 - 30 * s, y - H0), (x + W1 + 30 * s, y - H0)), P((x, y - H0), (x, y - H0 - 50 * s)),
             P((x - W0 - 10 * s, y), (x + W0 + 40 * s, y))]
    levels = [0, 150 * s, 290 * s, 400 * s]
    for h1, h2 in zip(levels, levels[1:]):
        parts += [P((x - hw(h1), y - h1), (x + hw(h2), y - h2)), P((x + hw(h1), y - h1), (x - hw(h2), y - h2))]
    return join(*parts)


def car(x, y, s=1.0) -> skia.Path:
    """小车（侧视）：(x, y) 为地面中点。"""
    body = P((x - 170 * s, y - 45 * s), (x - 170 * s, y - 105 * s), (x - 95 * s, y - 110 * s), (x - 50 * s, y - 175 * s),
             (x + 60 * s, y - 175 * s), (x + 115 * s, y - 108 * s), (x + 170 * s, y - 100 * s), (x + 170 * s, y - 45 * s),
             close=True)
    win = P((x - 35 * s, y - 160 * s), (x - 70 * s, y - 112 * s), (x + 95 * s, y - 112 * s), (x + 52 * s, y - 160 * s),
            close=True)
    return join(body, win, circle(x - 100 * s, y - 40 * s, 38 * s), circle(x + 100 * s, y - 40 * s, 38 * s))


def calendar(x, y, w=260, h=240) -> skia.Path:
    return join(rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 60), (x + w / 2, y - h / 2 + 60)),
                P((x - w / 4, y - h / 2 - 25), (x - w / 4, y - h / 2 + 20)),
                P((x + w / 4, y - h / 2 - 25), (x + w / 4, y - h / 2 + 20)))


def dashed(x0, x1, y, seg=50, gap=30) -> skia.Path:
    parts, x = [], x0
    while x < x1:
        parts.append(P((x, y), (min(x1, x + seg), y)))
        x += seg + gap
    return join(*parts)


def tag(x, y, w=230, h=110, fx=None, fy=None) -> skia.Path:
    """吊牌：左端打孔，一根绳连到 (fx, fy)。"""
    parts = [P((x - w / 2 + 40, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2 + 40, y + h / 2),
               (x - w / 2, y), close=True), circle(x - w / 2 + 40, y, 10)]
    if fx is not None:
        s = skia.Path()
        s.moveTo(fx, fy)
        s.quadTo((fx + x - w / 2 + 40) / 2, fy + 60, x - w / 2 + 40, y)
        parts.append(s)
    return join(*parts)


def spend_bars(x0, base, hs, line_h, w=100, gap=50):
    """花销柱：返回（柱子与底线、过线部分、过线的虚线）。"""
    low, high = [P((x0 - 50, base), (x0 + len(hs) * (w + gap), base))], []
    for i, h in enumerate(hs):
        x = x0 + i * (w + gap)
        hh = min(h, line_h)
        low.append(P((x, base), (x, base - hh), (x + w, base - hh), (x + w, base)))
        if h > line_h:
            high.append(P((x, base - line_h), (x, base - h), (x + w, base - h), (x + w, base - line_h)))
    return join(*low), join(*high), dashed(x0 - 50, x0 + len(hs) * (w + gap), base - line_h)


def pig_unit(mood="smile") -> skia.Path:
    """小猪罐（单位尺寸，身体中心在原点，脚底 y=155）。mood：smile / sad / sweat / shock。"""
    tail = skia.Path()
    tail.moveTo(-150, -10)
    tail.quadTo(-190, -45, -196, -8)
    tail.quadTo(-198, 25, -176, 16)
    tail.quadTo(-160, 6, -178, -6)
    parts = [oval(0, 0, 300, 220), oval(155, -8, 52, 78), circle(148, -10, 5), circle(163, -10, 5),
             P((25, -103), (45, -165), (85, -95)), P((-30, -108), (-15, -168), (20, -108)),
             circle(95, -42, 7), rect(-25, -110, 90, 18, 8), tail,
             P((-95, 90), (-95, 150)), P((-45, 105), (-45, 155)), P((45, 105), (45, 155)), P((95, 90), (95, 150))]
    m = skia.Path()
    if mood == "smile":
        m.addArc(skia.Rect.MakeXYWH(78, 22, 52, 34), 20, 140)
    elif mood == "sad":
        m.addArc(skia.Rect.MakeXYWH(80, 42, 46, 28), 200, 140)
    elif mood == "shock":
        m.addCircle(102, 48, 12)
    else:
        m.moveTo(82, 46)
        m.lineTo(118, 46)
        d = skia.Path()
        d.moveTo(195, -135)
        d.quadTo(215, -100, 195, -88)
        d.quadTo(175, -100, 195, -135)
        parts.append(d)
    parts.append(m)
    return join(*parts)


class Pig:
    """系列角色小猪罐：描出来、点头、胖一圈、换表情。所有动作按拍点排在当前镜头。"""

    def __init__(self, x, y, s=1.0, mood="smile", color=BLACK):
        self.x, self.y, self.s, self.color = x, y, s, color
        self.mood0 = mood
        self.events = []

    @property
    def slot(self):
        return self.x + 20 * self.s, self.y - 110 * self.s

    def draw(self, k0, k1=None, sfx="wood_high"):
        b.custom(J(), k0, k0 + 0.9 if k1 is None else k1, self.fn, sfx=sfx)
        return self

    def grow(self, k, f=1.1, sfx=None, j=None):
        self.events.append((J() if j is None else j, k, "grow", f))
        if sfx:
            H(k, sfx)
        return self

    def nod(self, k, sfx=None):
        self.events.append((J(), k, "nod", 0))
        if sfx:
            H(k, sfx)
        return self

    def mood(self, k, m, sfx=None):
        self.events.append((J(), k, "mood", m))
        if sfx:
            H(k, sfx)
        return self

    def fn(self, c, k, T):
        sc, ang, mood = self.s, 0.0, self.mood0
        for j, kb, kind, v in self.events:
            dt = T - b.t_of(j, kb)
            if dt < 0:
                continue
            if kind == "grow":
                sc *= v ** ease_out(clamp01(dt / 0.35))
            elif kind == "nod" and dt < 0.8:
                ang += 9 * math.sin(dt / 0.4 * 2 * math.pi) * (1 - dt / 0.8)
            elif kind == "mood":
                mood = v
        part, tip = partial(pig_unit(mood), k)
        fy = self.y + 155 * self.s
        c.save()
        c.translate(self.x, fy)
        c.rotate(ang)
        c.scale(sc, sc)
        c.translate(0, -155)
        c.drawPath(oval(0, 0, 300, 220), K.paint("#F4C7CE", 0.45 * clamp01(k * 1.5)))
        c.drawPath(part, marker(self.color, 9 / sc))
        c.drawPath(part, K.paint(self.color, 0.22, 4 / sc, blur=1.2))
        c.restore()
        if tip and k < 1:
            return self.x + tip[0] * sc, fy + (tip[1] - 155) * sc
        return None


def _coin_at(c, x, y, r, a=1.0):
    c.drawCircle(x, y, r, K.paint(GREEN, 0.18 * a))
    c.drawPath(coin(x, y, r), K.paint(GREEN, a, 8))


def coin_fly(k_show, k_land, x0, y0, pig, r=44, fly=0.5, sfx_show=None, sfx_land="ding", grow=1.08, appear=True):
    """一枚硬币：第 k_show 拍出现在 (x0, y0)，划一道弧落进小猪罐投币口，第 k_land 拍入罐（音效 + 小猪胖一圈）。"""
    j = J()

    def fn(c, k, T):
        tl = b.t_of(j, k_land)
        if T >= tl:
            return None
        x1, y1 = pig.slot
        ts = tl - fly
        if T < ts:
            _coin_at(c, x0, y0, r * (ease_out(k) if appear else 1.0))
            return None
        f = ease_in_out(clamp01((T - ts) / fly))
        x, y = lerp(x0, x1, f), lerp(y0, y1, f) - 160 * math.sin(math.pi * f)
        _coin_at(c, x, y, r * (1 - 0.45 * f))
        return None

    b.custom(j, k_show, k_show + 0.6, fn, sfx=sfx_show)
    H(k_land, sfx_land)
    pig.grow(k_land, grow)


# ---------------------------------------------------------------- 开局：三张便签（场景 1）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag_, view, bars=3, **kw):
    return b.shot(text, tag_, view=view, bars=bars, **kw)


NOTES = [(1150, 900, -4), (1800, 880, 3), (2450, 900, -2)]
scene("这三句你听过吧", "常听的三句话", (1800, 850, 0.55), bars=2)
for n, (x, y, d) in enumerate(NOTES):
    L(note(x, y, 380, 360, d), n, n + 0.8, ORANGE, 10, sfx="wood_high")
for n, (x, y, d) in enumerate(NOTES):
    T("？", x, y + 20, 200, RED, k0=3 + n, k1=3.8 + n, sfx="pop")

# ---------------------------------------------------------------- 第一对：工资低，存不下 ✗ / 存多少归你管 ✓（场景 2–3）

Y1 = 2400
scene("工资低，存不下", "误区一 · 工资低", (950, Y1, 0.85))
T("误区一", 950, Y1 - 440, 70, RED, k0=0, sfx="pop")
L(note(950, Y1, 760, 480), 1, 1.9, BLACK, 10, sfx="wood_high")
T("工资低", 950, Y1 - 70, 110, k0=2, sfx="pop")
T("存不下", 950, Y1 + 80, 110, k0=3, sfx="pop")
L(rect(950, Y1, 860, 580, 30), 4, 4.9, RED, 10, sfx="wood_low")
L(cross(1330, Y1 - 270, 60), 5, 5.8, RED, 14, sfx="rim")

scene("存钱率你能管", "书里说 · 存钱率", (2650, Y1, 0.85))
T("书里说", 2650, Y1 - 440, 70, BLUE, k0=0, sfx="pop")
L(rect(2650, Y1 + 20, 860, 660, 30), 1, 1.9, GREEN, 10, sfx="wood_high")
T("收入、回报管不全", 2650, Y1 - 200, 60, k0=2, sfx="pop")
T("存多少，你说了算", 2650, Y1 - 60, 80, GREEN, k0=4, sfx="pop")
pig1 = Pig(2470, Y1 + 170, 0.62).draw(6)
L(check(2860, Y1 + 190, 75), 7, 7.8, GREEN, 14, sfx="ding")
pig1.nod(9, "wood_low")

# ---------------------------------------------------------------- drop：省下的油比找到的多（场景 4）

Y4 = 3950
scene("省下的油比找到的多", "书中例子 · 石油危机", (1770, Y4, 0.7), shake=[0], flashes=[0])
T("1970年代", 1770, Y4 - 560, 110, RED, k0=0, k1=1.5, sfx="kick")
L(derrick(1260, Y4 + 150), 2, 2.9, BLACK, 10, sfx="wood_high")
L(car(2050, Y4 + 150), 3, 3.9, BLACK, 10, sfx="wood_high")
L(barrels(1520, Y4 + 150, 2), 4, 4.8, BLACK, 9, sfx="pop")
L(barrels(2340, Y4 + 150, 4), 5, 5.9, GREEN, 9, sfx="pop")
T("找到的", 1380, Y4 + 290, 64, k0=6, sfx="pop")
T("省下的", 2200, Y4 + 290, 64, GREEN, k0=7, sfx="ding")

# ---------------------------------------------------------------- 亮书 + 省下的就是赚到的（场景 5–6）

Y5 = 5250
scene("出自《金钱心理学》", "金钱心理学 · 第十章", (1300, Y5, 0.85))
L(book(1100, Y5 - 120, 440, 290), 0, 0.9, BLACK, 10, sfx="wood_low")
T("金钱心理学", 1100, Y5 - 420, 84, GREEN, k0=1, sfx="pop")
T("摩根·豪泽尔 著", 1100, Y5 + 150, 56, k0=3, k1=5, sfx="pop")
T("第十章 · 存钱", 1100, Y5 + 290, 64, BLUE, k0=5, sfx="pop")
Pig(1650, Y5 - 80, 0.7).draw(7)

scene("省下的，就是赚到的", "书中观点 · 少花就是多赚", (2550, Y5, 0.85))
L(barrel(2150, Y5 - 270), 0, 0.9, GREEN, 9, sfx="wood_high")
T("省下的油", 2150, Y5 - 190, 56, k0=1, sfx="pop")
L(arrow((2270, Y5 - 350), (2560, Y5 - 350), 0.0, 40), 2, 2.8, GREEN, 9, sfx="wood_low")
L(coin(2700, Y5 - 350, 60), 3, 3.8, GREEN, 9, sfx="pop")
pig6 = Pig(2600, Y5 + 150, 1.0).draw(4)
T("= 多一份收入", 2500, Y5 + 420, 72, GREEN, k0=5, sfx="pop")
coin_fly(6, 7, 2700, Y5 - 350, pig6, r=60, appear=False)
coin_fly(7, 8, 2700, Y5 - 350, pig6, r=60, appear=False)

# ---------------------------------------------------------------- 第二对：存钱要有用途 ✗ / 不用理由 ✓ → 存下的是选择（场景 7–9）

Y7 = 6700
scene("没目标，存了没用", "误区二 · 要有用途", (950, Y7, 0.85))
T("误区二", 950, Y7 - 440, 70, RED, k0=0, sfx="pop")
L(note(950, Y7, 760, 480), 1, 1.9, BLACK, 10, sfx="wood_high")
T("存钱", 950, Y7 - 70, 110, k0=2, sfx="pop")
T("要有用途", 950, Y7 + 80, 110, k0=3, sfx="pop")
L(rect(950, Y7, 860, 580, 30), 4, 4.9, RED, 10, sfx="wood_low")
L(cross(1330, Y7 - 270, 60), 5, 5.8, RED, 14, sfx="rim")

scene("存钱不用理由", "书里说 · 不用理由", (2650, Y7, 0.85))
T("书里说", 2650, Y7 - 440, 70, BLUE, k0=0, sfx="pop")
L(rect(2650, Y7 + 20, 860, 660, 30), 1, 1.9, GREEN, 10, sfx="wood_high")
T("为说不准的明天", 2650, Y7 - 150, 84, GREEN, k0=2, sfx="pop")
L(calendar(2470, Y7 + 150), 4, 4.9, BLACK, 9, sfx="wood_low")
T("？", 2470, Y7 + 180, 110, RED, k0=5, sfx="pop")
L(check(2860, Y7 + 150, 75), 6, 6.8, GREEN, 14, sfx="ding")

Y9 = 8150
scene("存下的是选择", "书中观点 · 存下选择", (1780, Y9, 0.75))
pig9 = Pig(1390, Y9, 1.1).draw(0)
BR = [((1630, Y9 - 80), (1980, Y9 - 440), 0.12, "能换工作", (2250, Y9 - 450)),
      ((1650, Y9), (2020, Y9), 0.0, "能等一等", (2280, Y9)),
      ((1630, Y9 + 80), (1980, Y9 + 440), -0.12, "能说不", (2230, Y9 + 450))]
for n, (a, z, bend, s, (tx, ty)) in enumerate(BR):
    L(arrow(a, z, bend, 44), 1 + 2 * n, 1.8 + 2 * n, GREEN, 9, sfx="wood_high")
    T(s, tx, ty, 64, GREEN, k0=2 + 2 * n, sfx="pop")
pig9.nod(7)
T("看不见的回报", 1390, Y9 + 330, 60, GREEN, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 第三对：钱多了自然存得下 ✗ → 多出来的多半为面子（场景 10）

Y10 = 9800
scene("多花的，多半为面子", "误区三 · 钱多了", (1800, Y10, 0.7))
T("误区三", 1350, Y10 - 580, 72, RED, k0=0, sfx="pop")
L(note(1350, Y10 - 180, 560, 420), 1, 1.9, BLACK, 10, sfx="wood_high")
T("钱多了", 1350, Y10 - 240, 72, k0=2, sfx="pop")
T("自然存得下", 1350, Y10 - 110, 72, k0=3, sfx="pop")
L(cross(1580, Y10 - 360, 55), 5, 5.8, RED, 13, sfx="rim")
LOW, HIGH, LINE = spend_bars(1900, Y10 + 200, (200, 300, 430, 560), 300)
L(join(LOW, LINE), 6, 6.6, BLACK, 9, sfx="wood_high")
L(HIGH, 6.6, 7.0, RED, 10)
T("多半为面子", 2180, Y10 - 480, 64, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 三个做法（场景 11–13）

Y11 = 10980
scene("先存，再花", "做法一 · 先存", (950, Y11, 0.85))
T("① 先存，再花", 950, Y11 - 440, 76, BLUE, k0=0, sfx="pop")
L(calendar(600, Y11 - 60), 2, 2.9, BLACK, 9, sfx="wood_high")
T("发薪日", 600, Y11 - 30, 54, RED, k0=3, sfx="pop")
L(arrow((760, Y11 - 60), (1060, Y11 - 60), 0.0, 40), 4, 4.8, GREEN, 9, sfx="wood_low")
pig11 = Pig(1290, Y11 + 20, 0.8).draw(5)
T("存 → 花", 950, Y11 + 330, 90, GREEN, k0=6, sfx="ding")
coin_fly(7, 9, 600, Y11 - 270, pig11, r=40, sfx_show="pop", sfx_land="ding", grow=1.12)

scene("存个没名目的钱", "做法二 · 没名目", (2650, Y11, 0.85))
T("② 没名目的钱", 2650, Y11 - 440, 76, BLUE, k0=0, sfx="pop")
pig12 = Pig(2560, Y11 + 30, 1.3).draw(2)
L(tag(3010, Y11 - 150, 250, 110, 2660, Y11 - 60), 3, 3.8, BLACK, 8, sfx="wood_low")
T("不为啥", 3040, Y11 - 150, 56, GREEN, k0=4, sfx="pop")
coin_fly(5, 6, 2250, Y11 - 300, pig12, r=40, sfx_show="shaker", grow=1.07)
coin_fly(6, 7, 2250, Y11 - 300, pig12, r=40, grow=1.07)

Y13 = 12400
scene("少一样面子开销", "做法三 · 少一样", (1800, Y13, 0.8))
T("③ 划掉一项", 1800, Y13 - 480, 76, BLUE, k0=0, sfx="pop")
pig13 = Pig(2230, Y13 + 40, 0.9).draw(1)
L(rect(1500, Y13 + 50, 460, 560, 18), 2, 2.8, BLACK, 9, sfx="wood_high")
ITEMS = [("房租", Y13 - 110), ("买菜", Y13 + 50), ("换新手机", Y13 + 210)]
for n, (s, yy) in enumerate(ITEMS):
    T(s, 1500, yy, 64, k0=3 + n, sfx="pop")
L(P((1340, Y13 + 215), (1660, Y13 + 205)), 6, 6.6, RED, 12, sfx="rim")
coin_fly(7, 9, 1830, Y13 + 210, pig13, r=40, sfx_show="pop", grow=1.12)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FULL = (1800, 7000, 0.135)
Y14 = 13780
J_END = scene("评论区：你为啥存钱？", "评论区见", FULL, bars=4)
b.move(J_END, 4, (1800, Y14, 0.8))
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你为啥存钱？", 1800, Y14 - 80, 80, RED, k0=6, k1=7.5, sfx="pop")
T("下一讲：计划总被打乱，钱怎么留余地？", 1800, Y14 + 100, 46, k0=9, k1=13.5, sfx="wood_high")
Pig(1800, Y14 + 360, 0.6).draw(14, sfx="pop").nod(15)
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "save", "存钱", "没想好买什么，也要存钱？", ACC, b.shots,
                 [f"{BOOK}第 10 章“存钱”（转述）",
                  "中译本：《金钱心理学》，摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023"],
                 "没想好买什么|也要【存钱】？", SQUARE_SHOT,
                 ["书中观点（转述）：存钱率比收入和投资回报更在自己掌控之中；上世纪 70 年代石油危机之后，美国靠提高能源"
                  "效率省下的能源，比新开采出来的更多；存钱不需要具体理由，存款带来灵活和选择，这份回报看不见；收入超过"
                  "一定水平后，多出来的花销多半跟自我和面子有关（转述，非原话）。出处：Morgan Housel, The Psychology of "
                  "Money (Harriman House, 2020)；中译本《金钱心理学》（摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 "
                  "2023）第 10 章“存钱”（转述）。",
                  "石油危机一屏的油井、省油车与油桶数量为示意，只表达“省下的比找到的多”这个方向，不代表任何数据；"
                  "油桶换成硬币落进小猪罐为通俗化示意。",
                  "三张便签上的说法（工资低存不下、存钱要有用途、钱多了自然存得下）为常见说法示意；花销柱与“某条线”"
                  "为示意，不是数据。",
                  "三个做法（发薪日先存再花、存一笔没名目的钱、购物单划掉一项面子开销）为示意 / 据书中思路整理；"
                  "不涉及任何理财产品与投资建议。"],
                 tags="#存钱 #储蓄")
    return b.attach(ep)
