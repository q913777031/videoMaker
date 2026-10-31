"""03 知道够了（白板手绘版）：工资涨了，为什么还是不够花？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒。
叙事（J 一个比喻贯穿：会自己往前跑的终点线）：工资涨了，小猪罐胖一圈 → 小王在跑道上跑，路边换了房、换了车 →
房贷车贷一扣，小猪罐又瘪下去 → drop：小王冲到终点线，终点线“嗖”地往前挪一大截 → 亮书 →
书中故事：冯内古特和海勒在富豪派对上聊天，海勒说自己有一样东西那位富豪没有：够了 →
书中观点：最难的是让终点线停下（钉子钉住）/ 比较没有尽头（跑道前面永远还有人）/
有人已经很有钱还去冒险（古普塔，铁栏）/ 名声、自由、家人、朋友不拿去赌 →
做法：给自己写个够数，钉在终点线上；涨薪先存一半，小猪罐胖一圈 → 拉远看整条跑道，评论区互动。
书中观点为转述：Morgan Housel, The Psychology of Money (Harriman House, 2020)；中译本《金钱心理学》
（摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023）第 3 章“永不知足”。例子与做法为示意 / 据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, circle, face, join, rect,
                               stick, underline)
from whiteboard.engine import clamp01, ease_in_out, ease_out

from .common import BOOK, episode

ACC = "#C8902E"                 # 本讲主色：金色（终点线 / 够了）
SQUARE_SHOT = 3                 # 场景 4：小王冲到终点线，终点线往前跑了

b = Board(size=(3600, 9800))


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    return p


def pig(x, y, s=1.0, mood="smile") -> skia.Path:
    """小猪存钱罐（正面，同第 1 讲）：(x, y) 为身子中心，脚底在 y + 118·s。mood：smile / sad / sweat / shock。"""
    parts = [oval(x, y, 130 * s, 95 * s),
             P((x - 25 * s, y - 72 * s), (x + 25 * s, y - 72 * s)),
             P((x - 95 * s, y - 62 * s), (x - 85 * s, y - 120 * s), (x - 45 * s, y - 88 * s)),
             P((x + 95 * s, y - 62 * s), (x + 85 * s, y - 120 * s), (x + 45 * s, y - 88 * s)),
             circle(x - 40 * s, y - 25 * s, 5 * s), circle(x + 40 * s, y - 25 * s, 5 * s),
             oval(x, y + 12 * s, 36 * s, 24 * s), circle(x - 12 * s, y + 12 * s, 4 * s), circle(x + 12 * s, y + 12 * s, 4 * s)]
    for dx in (-75, -30, 30, 75):
        parts.append(P((x + dx * s, y + 88 * s), (x + dx * s, y + 118 * s)))
    tail = skia.Path()
    tail.moveTo(x + 128 * s, y)
    tail.quadTo(x + 165 * s, y - 25 * s, x + 150 * s, y + 5 * s)
    tail.quadTo(x + 140 * s, y + 25 * s, x + 170 * s, y + 15 * s)
    parts.append(tail)
    m = skia.Path()
    if mood == "shock":
        m.addCircle(x, y + 55 * s, 9 * s)
    elif mood in ("sad", "sweat"):
        m.addArc(skia.Rect.MakeXYWH(x - 20 * s, y + 46 * s, 40 * s, 24 * s), 200, 140)
    else:
        m.addArc(skia.Rect.MakeXYWH(x - 22 * s, y + 36 * s, 44 * s, 26 * s), 20, 140)
    parts.append(m)
    if mood == "sweat":
        d = skia.Path()
        d.moveTo(x + 108 * s, y - 95 * s)
        d.quadTo(x + 130 * s, y - 60 * s, x + 108 * s, y - 52 * s)
        d.quadTo(x + 86 * s, y - 60 * s, x + 108 * s, y - 95 * s)
        parts.append(d)
    return join(*parts)


def runner(x, y, s=1.0, mood="smile") -> skia.Path:
    """往右跑的火柴人：(x, y) 为脚底，身子前倾。"""
    hy = y - 290 * s
    hx = x + 25 * s
    parts = [circle(hx, hy, 45 * s),
             P((x + 18 * s, hy + 45 * s), (x - 5 * s, y - 125 * s)),
             P((x + 12 * s, hy + 85 * s), (x + 60 * s, hy + 120 * s), (x + 95 * s, hy + 70 * s)),
             P((x + 12 * s, hy + 85 * s), (x - 40 * s, hy + 125 * s), (x - 80 * s, hy + 95 * s)),
             P((x - 5 * s, y - 125 * s), (x + 50 * s, y - 70 * s), (x + 40 * s, y)),
             P((x - 5 * s, y - 125 * s), (x - 40 * s, y - 60 * s), (x - 100 * s, y - 35 * s)),
             circle(hx - 4 * s, hy - 8 * s, 3 * s), circle(hx + 24 * s, hy - 8 * s, 3 * s)]
    m = skia.Path()
    if mood == "shock":
        m.addCircle(hx + 10 * s, hy + 20 * s, 8 * s)
    elif mood == "sad":
        m.addArc(skia.Rect.MakeXYWH(hx - 8 * s, hy + 12 * s, 36 * s, 24 * s), 200, 140)
    else:
        m.addArc(skia.Rect.MakeXYWH(hx - 10 * s, hy - 5 * s, 40 * s, 28 * s), 20, 140)
    parts.append(m)
    return join(*parts)


def finish(x, top, y0, y1) -> skia.Path:
    """终点线：跑道上一道竖线（y0–y1）+ 旗杆和三角旗，旗杆顶在 top。"""
    parts = [P((x, y0), (x, y1)), P((x - 14, y0), (x - 14, y1)), P((x, y0), (x, top)),
             P((x, top), (x + 120, top + 38), (x, top + 76), close=True)]
    for i in range(3):
        yy = y0 + (y1 - y0) * (i + 0.5) / 3
        parts.append(P((x - 14, yy), (x, yy)))
    return join(*parts)


def track(x0, x1, y0, y1) -> skia.Path:
    """跑道：两条边线 + 起点线 + 中间一道虚线。"""
    parts = [P((x0, y0), (x1, y0)), P((x0, y1), (x1, y1)), P((x0 + 40, y0), (x0 + 40, y1))]
    ym = (y0 + y1) / 2
    x = x0 + 120
    while x + 60 < x1:
        parts.append(P((x, ym), (x + 60, ym)))
        x += 140
    return join(*parts)


def house(x, y, w=230, h=170) -> skia.Path:
    """房子：(x, y) 为地面中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 30, y - h), (x, y - h - 130), (x + w / 2 + 30, y - h)),
                P((x - 30, y), (x - 30, y - 95), (x + 30, y - 95), (x + 30, y)), rect(x + w / 4 + 8, y - h + 60, 50, 50, 4))


def car(x, y, s=1.0) -> skia.Path:
    """小轿车（侧视）：(x, y) 为地面中点。"""
    return join(P((x - 150 * s, y - 40 * s), (x - 150 * s, y - 95 * s), (x - 85 * s, y - 105 * s),
                  (x - 45 * s, y - 165 * s), (x + 60 * s, y - 165 * s), (x + 105 * s, y - 105 * s),
                  (x + 150 * s, y - 95 * s), (x + 150 * s, y - 40 * s), close=True),
                P((x - 35 * s, y - 150 * s), (x - 60 * s, y - 108 * s), (x + 80 * s, y - 108 * s), (x + 50 * s, y - 150 * s),
                  close=True),
                circle(x - 85 * s, y - 38 * s, 38 * s), circle(x + 85 * s, y - 38 * s, 38 * s))


def payslip(x, y, w=400, h=280) -> skia.Path:
    return join(rect(x, y, w, h, 14), P((x - w / 2 + 40, y + h / 2 - 50), (x + w / 2 - 40, y + h / 2 - 50)))


def coin(x, y, r=34) -> skia.Path:
    return join(circle(x, y, r), P((x, y - r * 0.5), (x, y + r * 0.5)))


def nail(x, y, s=1.0) -> skia.Path:
    """钉子：尖朝下，尖在 (x, y)。"""
    return join(rect(x, y - 170 * s, 110 * s, 26 * s, 6 * s),
                P((x - 16 * s, y - 157 * s), (x - 16 * s, y - 40 * s), (x, y), (x + 16 * s, y - 40 * s),
                  (x + 16 * s, y - 157 * s)))


def bang(x, y, r=60) -> skia.Path:
    """敲击的爆点短线（以 (x, y) 为中心向四周）。"""
    parts = []
    for a in (-150, -110, -70, -30):
        t = math.radians(a)
        parts.append(P((x + math.cos(t) * r, y + math.sin(t) * r), (x + math.cos(t) * r * 1.8, y + math.sin(t) * r * 1.8)))
    return join(*parts)


def pennants(x0, x1, y, n=7) -> skia.Path:
    """派对彩旗：一根绳上挂一串小三角。"""
    parts = []
    rope = skia.Path()
    rope.moveTo(x0, y)
    rope.quadTo((x0 + x1) / 2, y + 70, x1, y)
    parts.append(rope)
    for i in range(n):
        f = (i + 0.5) / n
        xx = x0 + (x1 - x0) * f
        yy = y + 70 * 4 * f * (1 - f) / 2
        parts.append(P((xx - 32, yy), (xx, yy + 70), (xx + 32, yy), close=True))
    return join(*parts)


def moneybag(x, y, s=1.0) -> skia.Path:
    """钱袋：(x, y) 为袋身中心。"""
    body = skia.Path()
    body.moveTo(x - 40 * s, y - 85 * s)
    body.cubicTo(x - 170 * s, y - 20 * s, x - 150 * s, y + 110 * s, x, y + 110 * s)
    body.cubicTo(x + 150 * s, y + 110 * s, x + 170 * s, y - 20 * s, x + 40 * s, y - 85 * s)
    return join(body, P((x - 40 * s, y - 85 * s), (x - 70 * s, y - 135 * s), (x + 70 * s, y - 135 * s), (x + 40 * s, y - 85 * s)),
                P((x - 50 * s, y - 85 * s), (x + 50 * s, y - 85 * s)),
                coin(x - 30 * s, y + 25 * s, 30 * s), coin(x + 35 * s, y + 40 * s, 30 * s))


def bars(x, y, w=300, h=420) -> skia.Path:
    """铁栏：方框 + 竖杆。(x, y) 为中心。"""
    parts = [rect(x, y, w, h, 6), P((x - w / 2, y - h / 2 + 40), (x + w / 2, y - h / 2 + 40))]
    for i in range(1, 5):
        xx = x - w / 2 + w * i / 5
        parts.append(P((xx, y - h / 2), (xx, y + h / 2)))
    return join(*parts)


def note(x, y, w=560, h=280) -> skia.Path:
    """便签纸，左上角钉一颗图钉。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 50), (x + w / 2 - 50, y + h / 2),
                  (x - w / 2, y + h / 2), close=True), circle(x - w / 2 + 40, y - h / 2 + 36, 12))


def _ink(c, path, color, width):
    c.drawPath(path, wb.marker(color, width))
    c.drawPath(path, wb.K.paint(color, 0.22, width * 0.45, blur=1.2))


class Actor:
    """会动的白板角色（动态 custom 项）：先按 k0–k1 描出来，之后按关键帧换位置、缩放（以脚底为轴）和表情。

    keys：(镜头, 拍, 时长拍, {"x": .., "f": .., "mood": ..})，表情在该拍立即切换，位置和缩放在时长内缓动。
    """

    def __init__(self, shape, x, y, s, mood, color=BLACK, width=9, foot=0.0, streak=False):
        self.shape, self.x, self.y, self.s, self.mood = shape, x, y, s, mood
        self.color, self.width, self.foot, self.streak = color, width, foot, streak
        self.keys = []

    def draw(self, k0, k1, sfx=None):
        b.custom(J(), k0, k1, self._fn, sfx=sfx)
        return self

    def key(self, k, dur, sfx=None, gain=0.8, **kw):
        self.keys.append((J(), k, dur, kw))
        if sfx:
            H(k, sfx, gain)
        return self

    def _state(self, t):
        x, f, mood, moving = self.x, 1.0, self.mood, None
        for j, k, dur, kw in self.keys:
            t0, t1 = b.t_of(j, k), b.t_of(j, k + dur)
            if t < t0:
                break
            g = ease_in_out(clamp01((t - t0) / max(1e-3, t1 - t0)))
            if "x" in kw:
                if g < 1:
                    moving = (x, kw["x"], g)
                x = x + (kw["x"] - x) * g
            if "f" in kw:
                f = f + (kw["f"] - f) * (ease_out(clamp01((t - t0) / max(1e-3, t1 - t0))))
            mood = kw.get("mood", mood)
        return x, f, mood, moving

    def _fn(self, c, k, t):
        x, f, mood, moving = self._state(t)
        path = self.shape(x, self.y, self.s, mood)
        fy = self.y + self.foot * self.s
        c.save()
        c.translate(x, fy)
        c.scale(f, f)
        c.translate(-x, -fy)
        part, tip = wb.partial(path, k)
        _ink(c, part, self.color, self.width)
        c.restore()
        if moving and self.streak:                  # 移动中拖出速度线
            xa, xb, g = moving
            d = 1 if xb > xa else -1
            for i, dy in enumerate((-200, -120, -40)):
                L0 = 220 + 60 * i
                a = 0.55 * (1 - g)
                c.drawPath(P((x - d * 90, self.y + dy * self.s), (x - d * (90 + L0), self.y + dy * self.s)),
                           wb.K.paint(self.color, a, 7))
        return tip if k < 1 else None


def coin_drop(x, y_from, y_to, r=34):
    """硬币从上方落进投币口，落进去后消失。"""

    def fn(c, k, t):
        if k >= 1:
            return None
        g = k * k
        _ink(c, coin(x, y_from + (y_to - y_from) * g, r), GREEN, 8)
        return None

    return fn


# ---------------------------------------------------------------- 开局：工资涨了（场景 1–4，同一条跑道）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

LANE = (1240, 1360)             # 跑道上下边线
FEET = 1335                     # 跑道上小王的脚底
PIG1 = (1000, 1060)
PIG = Actor(pig, *PIG1, 1.0, "smile", foot=118)
WANG = Actor(runner, 1420, FEET, 0.75, "smile", width=10, streak=True)
FIN = Actor(lambda x, y, s, m: finish(x, 990, *LANE), 2650, LANE[1], 1.0, "", width=11, streak=True)

scene("工资涨了", "灵魂拷问", (700, 1000, 0.85), bars=2)
L(payslip(480, 830), 0, 0.9, sfx="wood_high")
T("工资条", 480, 760, 60, k0=1, k1=1.8, sfx="pop")
T("+20%", 480, 880, 100, RED, k0=2, k1=3, sfx="pop")
PIG.draw(3, 3.9, sfx="wood_high")
L(arrow((700, 760), (930, 900), -0.25, 36), 4, 4.8, GREEN, 9, sfx="wood_low")
b.custom(J(), 5, 5.6, coin_drop(PIG1[0], PIG1[1] - 320, PIG1[1] - 72), sfx="ding")
PIG.key(5.6, 0.4, f=1.12)

scene("换了房，换了车", "灵魂拷问", (2000, 1050, 0.75))
L(track(1250, 3550, *LANE), 0, 0.9, BLACK, 8, sfx="wood_low")
WANG.draw(1, 1.9, sfx="wood_high")
L(house(1850, LANE[0]), 2, 2.9, BLACK, 9, sfx="pop")
T("新房", 1850, 860, 60, k0=3, k1=3.8, sfx="pop")
L(car(2330, LANE[0]), 4, 4.9, BLUE, 9, sfx="pop")
T("新车", 2330, 1010, 60, BLUE, k0=5, k1=5.8, sfx="pop")
FIN.draw(6, 6.9, sfx="wood_high")
T("终点", 2720, 930, 60, RED, k0=7, k1=7.8, sfx="pop")

scene("还是不够花", "灵魂拷问", (1000, 1050, 0.85))
L(arrow((900, 1200), (720, 1360), 0.15, 36), 0, 0.9, RED, 9, sfx="wood_high")
T("房贷", 650, 1425, 60, RED, k0=1, k1=1.8, sfx="pop")
L(arrow((1100, 1200), (1230, 1380), -0.15, 36), 2, 2.9, RED, 9, sfx="wood_high")
T("车贷", 1290, 1445, 60, RED, k0=3, k1=3.8, sfx="pop")
PIG.key(4, 0.8, sfx="tom", f=0.78, mood="sad")
PIG.key(6, 0.1, sfx="rim", mood="sweat")
T("不够花！", 1010, 720, 90, RED, k0=7, k1=8, sfx="kick")

# ---------------------------------------------------------------- drop：终点线跑了（场景 4）

scene("终点线跑了", "灵魂拷问", (2650, 1050, 0.6), shake=[0, 2], flashes=[0])
H(0, "kick", 1.0)
WANG.key(0, 0.8, x=2560)
FIN.key(2, 0.6, sfx="tom", x=3350)
L(join(*[P((2780, LANE[0] - h), (3200, LANE[0] - h)) for h in (60, 160, 260)]), 3, 3.8, BLACK, 7, sfx="shaker")
T("终点线跑了", 2650, 640, 100, RED, k0=4, k1=5.5, sfx="ding")
WANG.key(6, 0.1, sfx="rim", mood="shock")
T("？", 2500, 950, 90, RED, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- 书中故事：派对上的“够了”（场景 5–7）

scene("一本讲钱和人心的书", "书中观点 · 永不知足", (1000, 2600, 0.85))
L(book(880, 2620, 420, 280), 0, 0.9, BLACK, 10, sfx="wood_low")
T("金钱心理学", 880, 2390, 72, GREEN, k0=1, k1=2.25, sfx="pop")
L(rect(1390, 2560, 330, 100, 16), 3, 3.8, BLACK, 8, sfx="wood_high")
T("摩根·豪泽尔", 1390, 2578, 52, k0=3.8, k1=5)
L(stick(1390, 2930, 0.6, "point"), 5, 5.8, BLACK, 9, sfx="wood_high")
T("第3章 永不知足", 880, 2900, 60, BLUE, k0=6, k1=8, sfx="pop")

VP = (2650, 2700, 0.85)
VON, HEL = (2380, 3000), (2920, 3000)
scene("派对上的一句话", "书中故事 · 富豪的派对", VP)
L(pennants(2150, 3150, 2280), 0, 0.9, ACC, 8, sfx="wood_high")
T("富豪的派对", 2500, 2450, 64, k0=1, k1=2.25, sfx="pop")
L(join(stick(*VON, 0.7, "down"), stick(*HEL, 0.7, "shrug")), 3, 3.9, BLACK, 9, sfx="wood_high")
L(join(rect(VON[0], 3085, 250, 80, 12), rect(HEL[0], 3085, 170, 80, 12)), 4, 4.5, BLUE, 7, sfx="pop")
T("冯内古特", VON[0], 3098, 50, BLUE, k0=4.5, k1=5.4)
T("海勒", HEL[0], 3098, 50, BLUE, k0=5.4, k1=6.2)
L(bubble(2330, 2620, 280, 110, -1), 6, 6.6, BLACK, 8, sfx="pop")
T("他赚得多", 2330, 2635, 50, k0=6.6, k1=7.6)

scene("我有他没有的：够了", "书中故事 · 富豪的派对", VP)
L(bubble(3010, 2600, 340, 190, 1), 0, 0.9, BLACK, 9, sfx="wood_high")
T("够了", 3010, 2625, 110, RED, k0=1, k1=1.8, sfx="ding")
L(underline(2890, 3130, 2675, 10, 30), 2, 2.8, RED, 8, sfx="pop")
L(face(*HEL, 0.7, "smile"), 3, 3.5, BLACK, 7, sfx="pop")
L(face(*VON, 0.7, "flat"), 4, 4.5, BLACK, 7, sfx="wood_low")
T("知道够了", 2650, 3240, 80, GREEN, k0=5, k1=6, sfx="pop")
L(underline(2490, 2810, 3285, 10, 32), 7, 7.8, GREEN, 8, sfx="ding")

# ---------------------------------------------------------------- 书中观点：钉住终点线 / 比较没有尽头（场景 8–9）

L2 = (4350, 4470)
scene("终点线别再挪", "书中观点 · 终点线", (2650, 4300, 0.85), shake=[4])
L(track(2120, 3250, *L2), 0, 0.9, BLACK, 8, sfx="wood_low")
L(runner(2330, L2[1] - 25, 0.7), 1, 1.9, BLACK, 10, sfx="wood_high")
L(finish(2950, 4000, *L2), 2, 2.9, RED, 11, sfx="pop")
L(nail(3040, L2[0] + 40, 0.9), 3, 3.8, BLACK, 9, sfx="wood_high")
L(bang(3040, L2[0] - 120, 50), 4, 4.5, RED, 8, sfx="kick")
T("把终点线钉住", 2650, 3930, 84, RED, k0=5, k1=6.5, sfx="ding")
T("最难的一步", 2650, 4680, 60, BLUE, k0=7, k1=8, sfx="pop")

L3 = (4420, 4540)
scene("比较没有尽头", "书中观点 · 永远有人在前面", (1100, 4350, 0.7))
L(track(380, 1850, *L3), 0, 0.9, BLACK, 8, sfx="wood_low")
for n, xx in enumerate((800, 1100, 1400, 1700)):
    L(runner(xx, L3[1] - 25, 0.7), 1 + n, 1.9 + n, BLUE, 9, sfx="wood_high" if n % 2 == 0 else "pop")
T("总有人在你前面", 1100, 3960, 80, RED, k0=5, k1=6.75, sfx="pop")
L(runner(500, L3[1] - 25, 0.7, "sad"), 7, 7.9, BLACK, 10, sfx="rim")

# ---------------------------------------------------------------- 书中例子与观点：有人赌上了一切（场景 10–11）

GUP = (720, 6060)
scene("有人赌上了一切", "书中例子 · 古普塔", (1000, 5800, 0.85))
L(stick(*GUP, 0.8, "down", tie=True), 0, 0.9, BLACK, 10, sfx="wood_high")
L(rect(GUP[0], 6140, 230, 80, 12), 1, 1.5, BLUE, 7, sfx="pop")
T("古普塔", GUP[0], 6153, 50, BLUE, k0=1.5, k1=2.3)
L(moneybag(1180, 5880, 1.0), 3, 3.9, GREEN, 9, sfx="pop")
T("已经很有钱", 1180, 5640, 60, GREEN, k0=4, k1=5.25, sfx="pop")
T("还去碰内幕交易", 1180, 6200, 56, RED, k0=5.3, k1=7)
H(5, "wood_low")
L(bars(GUP[0], 5900, 300, 440), 7, 7.9, BLACK, 10, sfx="rim")

ME = (2650, 6010)
BOXES = [("名声", 2380, 5560), ("自由", 2920, 5560), ("家人", 2380, 6110), ("朋友", 2920, 6110)]
scene("这些别拿去赌", "书中观点 · 不值得冒的险", (2650, 5800, 0.85))
L(join(stick(*ME, 0.65, "down"), face(*ME, 0.65, "smile")), 0, 0.9, BLACK, 9, sfx="wood_high")
for n, (s, x, y) in enumerate(BOXES):
    L(rect(x, y, 220, 96, 14), 1 + n, 1.35 + n, BLUE, 8, sfx="pop")
    T(s, x, y + 16, 60, BLUE, k0=1.35 + n, k1=2.15 + n)
L(oval(2650, 5840, 580, 470), 5, 5.9, RED, 10, sfx="rim")
T("不赌", 2650, 5585, 80, RED, k0=6, k1=6.8, sfx="kick")

# ---------------------------------------------------------------- 做法（场景 12–13）

L4 = (7500, 7620)
scene("给自己写个够数", "做法一 · 写个够数", (2650, 7300, 0.85))
L(join(track(2120, 3250, *L4), finish(3020, 6950, *L4)), 0, 0.9, BLACK, 9, sfx="wood_low")
L(nail(3110, L4[0] + 40, 0.9), 1, 1.8, BLACK, 9, sfx="wood_high")
L(note(2450, 7130), 2, 2.8, ACC, 9, sfx="pop")
T("每月够用：", 2450, 7090, 60, k0=3, k1=4.25, sfx="pop")
L(P((2260, 7200), (2640, 7200)), 5, 5.6, BLACK, 7, sfx="wood_high")
L(arrow((2740, 7130), (2990, 7080), 0.1, 30), 6, 6.8, ACC, 8, sfx="pop")
L(join(stick(2300, L4[1] - 20, 0.55, "down"), face(2300, L4[1] - 20, 0.55, "smile")), 7, 7.8, BLACK, 9, sfx="wood_high")

PIG2 = (1250, 7470)
PIG_B = Actor(pig, *PIG2, 1.0, "smile", foot=118)
scene("涨薪先存一半", "做法二 · 涨薪先存一半", (1000, 7300, 0.85))
L(payslip(600, 7050, 380, 240), 0, 0.9, BLACK, 9, sfx="wood_high")
T("涨的钱", 600, 7040, 64, RED, k0=1, k1=1.8, sfx="pop")
PIG_B.draw(2, 2.9, sfx="wood_high")
L(arrow((800, 7110), (1100, 7370), -0.15, 34), 3, 3.8, GREEN, 9, sfx="pop")
T("一半存起来", 1110, 7150, 56, GREEN, k0=4, k1=5.25, sfx="pop")
b.custom(J(), 5.25, 5.8, coin_drop(PIG2[0], PIG2[1] - 300, PIG2[1] - 72))
PIG_B.key(6, 0.4, sfx="ding", f=1.2)
L(arrow((520, 7180), (480, 7440), 0.15, 34), 6, 6.8, BLACK, 8)
T("一半随意花", 520, 7510, 56, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看整条跑道，再推到评论区

FAR = (1800, 4500, 0.2)
NEAR = (1800, 8800, 0.8)
scene("评论区说说你的够数", "评论区见", FAR, bars=4)
b.move(J(), 4, NEAR, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你的够数是多少？", 1800, 8720, 80, RED, k0=6, k1=8, sfx="pop")
T("下一讲：攒钱这件事，为什么拼的是时间？", 1800, 8890, 50, k0=9, k1=13.75, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "enough", "知道够了", "工资涨了，为什么还是不够花？", ACC, b.shots,
                 [f"{BOOK}第 3 章“永不知足”（转述）",
                  "中译本：《金钱心理学：财富、人性和幸福的永恒真相》，李青宗译，民主与建设出版社 / 后浪 2023"],
                 "工资涨了|为什么还是【不够花】？", SQUARE_SHOT,
                 ["书中观点（转述）：第 3 章“永不知足”——作家冯内古特与约瑟夫·海勒在一位富豪的派对上聊天，冯内古特说"
                  "主人一天赚的比海勒那本小说赚的还多，海勒回答自己有一样东西那位富豪永远不会有：“够了”（画面为转述，"
                  "不是逐字引文）；古普塔这样已经很富有的人，仍去碰内幕交易、最后入狱；最难的理财本事是让目标别一直往前挪；"
                  "社会比较没有上限；名声、自由、家人、朋友等不值得拿去冒险。出处：Morgan Housel, The Psychology of Money "
                  "(Harriman House, 2020)；中译本《金钱心理学》（摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023）"
                  "第 3 章“永不知足”（转述）。",
                  "“会自己往前跑的终点线”跑道比喻、钉住终点线的钉子、跑道上前面永远还有人，为对书中观点的通俗化示意。",
                  "工资条“+20%”、新房新车、房贷车贷为现实场景示意，数字为示意，不是数据，不指向任何具体公司或个人。",
                  "“给自己写个够数”据书中思路整理；“涨薪先存一半”为示意做法，不是投资建议。"],
                 tags="#消费 #攀比")
    return b.attach(ep)
