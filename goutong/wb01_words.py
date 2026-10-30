"""01 扎人的话（白板手绘版）：没骂人，话怎么也扎心？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：画完停 4 拍）。
叙事（形式 B：一个故事贯穿）：打工人小周平平常常的一天——早上对室友说“你真邋遢”（贴标签）、上午对实习生说
“你看看人家小李”（拿人比）→ drop：几句话的小泡都长了刺，滚成一个大刺球砸下 → 亮书《非暴力沟通》与空白四格卡 →
书中观点（第二章）：扎人的话分四类，四个抽屉依次拉开 → 下午“公司规定，我也没办法”（推责任，把“选择”这只球踢给规定）、
晚上“今晚必须来接我”（硬要求，叹号上挂着锁）→ 拉远回看：一天时间轴上四个带刺小泡，各贴一类标签（封面镜头）→
书中观点（第一章）：四步——观察、感受、需要、请求，四格卡逐格画出 → 早上那句、上午那句重说，小泡的刺一根根缩回去 →
回到时间轴，四个小泡都变圆 → 评论区互动。
系列视觉角色：会变形的话泡泡“小泡”（说扎人的话长红刺、嘴往下撇；好好说时刺缩回去，变成蓝色圆泡、嘴角上扬）；四格卡
（眼睛 / 心 / 电池 / 手）本讲第一次画出。
书中观点为转述：马歇尔·卢森堡《非暴力沟通》第一章“让爱融入生活”、第二章“是什么蒙蔽了爱？”、附录（华夏出版社，阮胤华译）；
小周的四句话、改写句与一天的情节均为示意，据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, circle, clock, hands_at, join, rect,
                               stick, face, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#C8503C"
SQUARE_SHOT = 8                 # 场景 9：一天时间轴上四个带刺小泡，各贴一类标签

b = Board(size=(3600, 9000))


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


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def mirror(path: skia.Path, x: float) -> skia.Path:
    """以竖线 x 为轴左右翻转（让 stick 的 point 手臂朝左）。"""
    p = skia.Path(path)
    m = skia.Matrix.Scale(-1, 1)
    m.postTranslate(2 * x, 0)
    p.transform(m)
    return p


def _ell(x, y, rx, ry, a):
    return x + rx * math.cos(a), y + ry * math.sin(a)


def pao_outline(x, y, rx, ry, tail=0) -> skia.Path:
    """小泡的轮廓：椭圆 + 底部小尾巴（tail=-1 尾巴偏左、1 偏右、0 无尾巴）。"""
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    if tail:
        a0 = math.pi / 2 - tail * 0.55
        b0, b1 = _ell(x, y, rx, ry, a0 - 0.16), _ell(x, y, rx, ry, a0 + 0.16)
        tip = (x + tail * rx * 0.62, y + ry + 70)
        p.moveTo(*b0)
        p.lineTo(*tip)
        p.lineTo(*b1)
    return p


def spike_angles(n, tail=0, rot=0.0):
    """n 根刺在轮廓上等距分布；有尾巴时跳过尾巴附近。"""
    out = []
    a_tail = math.pi / 2 - tail * 0.55
    i = 0
    while len(out) < n and i < 4 * n:
        a = rot - math.pi / 2 + i * 2 * math.pi / n
        i += 1
        if tail and abs(math.atan2(math.sin(a - a_tail), math.cos(a - a_tail))) < 0.45:
            a += 0.5
        out.append(a)
    return out


def spikes_path(x, y, rx, ry, lens, tail=0, rot=0.0) -> skia.Path:
    """在椭圆轮廓上等距加三角刺；lens 为每根刺的长度（0 = 缩回）。"""
    p = skia.Path()
    for a, ln in zip(spike_angles(len(lens), tail, rot), lens):
        if ln <= 1:
            continue
        d = 0.17 * min(1.0, 140 / max(rx, ry)) + 0.06
        b0, b1 = _ell(x, y, rx, ry, a - d), _ell(x, y, rx, ry, a + d)
        nx, ny = math.cos(a) / rx, math.sin(a) / ry
        nn = math.hypot(nx, ny)
        mx, my = _ell(x, y, rx, ry, a)
        tip = (mx + nx / nn * ln, my + ny / nn * ln)
        p.moveTo(*b0)
        p.lineTo(*tip)
        p.lineTo(*b1)
    return p


def pao_face(c, x, y, rx, ry, mood, color, txt=True, s=1.0):
    """小泡的脸：两点眼睛 + 小嘴。txt=True 时脸放上半部，下半部留给字。"""
    ey = y - ry * (0.55 if txt else 0.18)
    dx = rx * (0.13 if txt else 0.28)
    K.dot(c, x - dx, ey, 9 * s, color)
    K.dot(c, x + dx, ey, 9 * s, color)
    my = ey + (26 if txt else 42) * s
    w = (22 if txt else 34) * s
    m = skia.Path()
    m.moveTo(x - w, my)
    if mood == "smile":
        m.quadTo(x, my + 22 * s, x + w, my)
    elif mood == "frown":
        m.moveTo(x - w, my + 10 * s)
        m.quadTo(x, my - 14 * s, x + w, my + 10 * s)
    else:
        m.lineTo(x + w, my)
    c.drawPath(m, K.paint(color, 1, 7 * s))


def draw_pao(c, x, y, rx, ry, color, lens, mood, tail=0, rot=0.0, k=1.0, txt=True, width=9, s=1.0):
    """画一只小泡（k<1 时轮廓逐段描出，返回笔尖）。"""
    out = pao_outline(x, y, rx, ry, tail)
    if rot:
        m = skia.Matrix()
        m.setRotate(math.degrees(rot), x, y)
        out.transform(m)
    part, tip = wb.partial(out, k)
    c.drawPath(part, wb.marker(color, width))
    c.drawPath(part, K.paint(color, 0.22, width * 0.45, blur=1.2))
    if k >= 0.8:
        sp = spikes_path(x, y, rx, ry, lens, tail, rot)
        c.drawPath(sp, wb.marker(color, width * 0.85))
        pao_face(c, x, y, rx, ry, mood, color, txt, s)
    return tip


class Pao:
    """系列角色“小泡”：一个会长刺、缩刺的话泡泡。状态随时间变化：
    grow 之后长出红刺、嘴往下撇；retract 把指定的刺一根根缩回去，全部缩回后变成蓝色圆泡、嘴角上扬。"""

    def __init__(self, x, y, rx, ry, tail=0, n=12, L=46, base=BLACK, mood="smile", txt=True):
        self.x, self.y, self.rx, self.ry, self.tail = x, y, rx, ry, tail
        self.n, self.L, self.base, self.mood, self.txt = n, L, base, mood, txt
        self.grows = []         # (j, k, dur)
        self.retracts = []      # (j, k, dur, idx)

    def draw(self, j, k0, k1, sfx=None):
        b.custom(j, k0, k1, self.fn, sfx=sfx)
        return self

    def grow(self, j, k, dur=0.5, sfx="rim"):
        self.grows.append((j, k, dur))
        if sfx:
            b.hit(j, k, sfx, 0.8, "小泡长刺")
        return self

    def retract(self, j, k, idx, dur=0.5, sfx="pop"):
        self.retracts.append((j, k, dur, list(idx)))
        if sfx:
            b.hit(j, k, sfx, 0.8, "刺缩回去")
        return self

    def _f(self, T, j, k, dur):
        t0, t1 = b.t_of(j, k), b.t_of(j, k + dur)
        return clamp01((T - t0) / max(1e-3, t1 - t0))

    def lens(self, T):
        g = 0.0
        for j, k, dur in self.grows:
            f = self._f(T, j, k, dur)
            g = max(g, ease_out(f) * (1 + 0.25 * math.sin(math.pi * f)))
        out = [g * self.L] * self.n
        for j, k, dur, idx in self.retracts:
            f = ease_in_out(self._f(T, j, k, dur))
            for i in idx:
                out[i] *= 1 - f
        return out

    def state(self, T):
        lens = self.lens(T)
        spiky = max(lens) > self.L * 0.3
        calm = bool(self.retracts) and T >= b.t_of(self.retracts[0][0], self.retracts[0][1]) and not spiky
        if spiky:
            return lens, RED, "frown"
        if calm:
            return lens, BLUE, "smile"
        return lens, self.base, self.mood

    def fn(self, c, k, T):
        lens, color, mood = self.state(T)
        return draw_pao(c, self.x, self.y, self.rx, self.ry, color, lens, mood, self.tail, k=k, txt=self.txt)


def eye(x, y, s=1.0) -> skia.Path:
    w, h = 62 * s, 34 * s
    p = skia.Path()
    p.moveTo(x - w, y)
    p.quadTo(x, y - 2 * h, x + w, y)
    p.quadTo(x, y + 2 * h, x - w, y)
    p.addCircle(x, y, h * 0.75)
    p.addCircle(x, y, h * 0.22)
    return p


def heart(x, y, r=60) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def battery(x, y, s=1.0) -> skia.Path:
    """快没电的电池：外壳 + 正极 + 一格电。"""
    return join(rect(x - 8 * s, y, 120 * s, 64 * s, 10 * s), rect(x + 60 * s, y, 14 * s, 26 * s, 4 * s),
                rect(x - 50 * s, y, 18 * s, 38 * s, 3 * s))


def palm(x, y, s=1.0) -> skia.Path:
    """伸出来的手（掌心朝上，像在递东西 / 讨东西）：袖口 + 托起的手掌 + 拇指。"""
    cup = skia.Path()
    cup.moveTo(x - 40 * s, y - 18 * s)
    cup.cubicTo(x - 30 * s, y + 45 * s, x + 50 * s, y + 45 * s, x + 78 * s, y - 20 * s)
    cup.lineTo(x + 20 * s, y - 8 * s)
    thumb = skia.Path()
    thumb.moveTo(x - 30 * s, y - 16 * s)
    thumb.quadTo(x - 20 * s, y - 48 * s, x + 6 * s, y - 40 * s)
    return join(rect(x - 70 * s, y + 4 * s, 44 * s, 58 * s, 6 * s), cup, thumb)


ICONS = (eye, lambda x, y, s=1.0: heart(x, y + 8 * s, 50 * s), battery, palm)
LABELS = ("观察", "感受", "需要", "请求")


def card_frame(x, y, cell, h) -> skia.Path:
    parts = [rect(x, y, 4 * cell, h, 20)]
    for i in range(1, 4):
        xx = x - 2 * cell + i * cell
        parts.append(P((xx, y - h / 2 + 14), (xx, y + h / 2 - 14)))
    return join(*parts)


def cell_x(x, cell, i):
    return x - 1.5 * cell + i * cell


def fill_fn(x, y, w, h, color=BLUE, alpha=0.18):
    """四格卡某一格涂色（点亮）。"""
    def fn(c, k, t):
        c.drawPath(rect(x, y, w * (0.6 + 0.4 * ease_out(k)), h * (0.6 + 0.4 * ease_out(k)), 16),
                   K.paint(color, alpha * k))
        return None

    return fn


def clock_face(x, y, r) -> skia.Path:
    """闹钟：钟面 + 两个铃 + 两只脚。"""
    bell = skia.Path()
    bell.addArc(skia.Rect.MakeXYWH(x - r * 0.95 - 40, y - r * 1.05 - 40, 80, 80), 180, 180)
    bell2 = skia.Path()
    bell2.addArc(skia.Rect.MakeXYWH(x + r * 0.95 - 40, y - r * 1.05 - 40, 80, 80), 180, 180)
    return join(clock(x, y, r), bell, bell2, P((x - r * 0.6, y + r * 0.8), (x - r * 0.8, y + r * 1.1)),
                P((x + r * 0.6, y + r * 0.8), (x + r * 0.8, y + r * 1.1)))


def sink(x, y) -> skia.Path:
    """水池：台面 + 池子 + 龙头，池里摞着三只碗。(x, y) 为台面中点。"""
    parts = [P((x - 200, y), (x + 200, y)), P((x - 150, y), (x - 120, y + 100), (x + 120, y + 100), (x + 150, y)),
             P((x + 120, y), (x + 120, y - 110), (x + 50, y - 110), (x + 50, y - 85))]
    for n in range(3):
        bw = skia.Path()
        bw.addArc(skia.Rect.MakeXYWH(x - 120, y - 70 - n * 32, 150, 70), 0, 180)
        parts += [bw, P((x - 128, y - 35 - n * 32), (x + 38, y - 35 - n * 32))]
    return join(*parts)


def stink(x, y) -> skia.Path:
    parts = []
    for dx in (-40, 0, 40):
        p = skia.Path()
        p.moveTo(x + dx, y)
        p.quadTo(x + dx - 18, y - 25, x + dx, y - 50)
        p.quadTo(x + dx + 18, y - 75, x + dx, y - 100)
        parts.append(p)
    return join(*parts)


def cloud(x, y, w=170) -> skia.Path:
    """乌云 + 两道雨。"""
    p = skia.Path()
    p.moveTo(x - w / 2, y + 30)
    p.quadTo(x - w / 2 - 30, y - 20, x - w / 4, y - 25)
    p.quadTo(x - w / 6, y - 75, x + w / 8, y - 50)
    p.quadTo(x + w / 2, y - 70, x + w / 2, y - 5)
    p.quadTo(x + w / 2 + 25, y + 30, x + w / 3, y + 30)
    p.close()
    return join(p, P((x - 30, y + 50), (x - 42, y + 85)), P((x + 20, y + 50), (x + 8, y + 85)))


def sign(x, y) -> skia.Path:
    """路牌：立杆 + 牌面。(x, y) 为牌面中心。"""
    return join(rect(x, y, 260, 140, 14), P((x, y + 70), (x, y + 320)), P((x - 60, y + 320), (x + 60, y + 320)))


def phone(x, y, w=80, h=130) -> skia.Path:
    return join(rect(x, y, w, h, 14), P((x - 14, y + h / 2 - 18), (x + 14, y + h / 2 - 18)))


def bang(x, y) -> skia.Path:
    """大叹号（竖笔），点另外画。"""
    return P((x, y - 190), (x, y + 120))


def padlock(x, y) -> skia.Path:
    """挂在叹号上的小锁：链子 + 锁梁 + 锁身 + 锁孔。(x, y) 为锁身中心。"""
    sh = skia.Path()
    sh.addArc(skia.Rect.MakeXYWH(x - 30, y - 75, 60, 70), 180, 180)
    return join(P((x - 70, y - 120), (x - 20, y - 85)), sh, P((x - 30, y - 40), (x - 30, y - 35)),
                P((x + 30, y - 40), (x + 30, y - 35)), rect(x, y, 96, 76, 12), circle(x, y - 6, 9), P((x, y + 3), (x, y + 20)))


def sheet(x, y, w=380, h=260) -> skia.Path:
    """一张表：外框 + 三行三列格子。"""
    parts = [rect(x, y, w, h, 10)]
    for i in range(1, 3):
        parts.append(P((x - w / 2, y - h / 2 + i * h / 3), (x + w / 2, y - h / 2 + i * h / 3)))
        parts.append(P((x - w / 2 + i * w / 3, y - h / 2), (x - w / 2 + i * w / 3, y + h / 2)))
    return join(*parts)


def cell_of(x, y, w, h, r, cidx):
    return x - w / 2 + (cidx + 0.5) * w / 3, y - h / 2 + (r + 0.5) * h / 3


# ---------------------------------------------------------------- 开局：小周的一天（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

ZHOU = (900, 1400)
PAO1 = Pao(1250, 830, 230, 130, tail=-1, n=12, L=46)

scene("小周的一天", "小周的一天", (1000, 1000, 0.85), bars=2)
L(clock_face(560, 800, 110), 0, 0.9, BLACK, 9, sfx="wood_high")
L(hands_at(560, 800, 110, 7, 30), 1, 1.4, RED, 9, sfx="pop")
T("07:30", 560, 1000, 60, RED, k0=1.4, k1=2.2)
L(stick(*ZHOU, 0.85), 2, 2.8, BLACK, 10, sfx="wood_high")
L(face(*ZHOU, 0.85, "smile"), 2.8, 3.0)
T("小周 · 打工人", ZHOU[0], 1470, 54, k0=3, k1=4.5, sfx="pop")
PAO1.draw(J(), 5, 5.9, sfx="pop")

DOOR = (1830, 1210, 140, 420)
RM = (1585, 1420)
scene("早上：你真邋遢", "早上 · 小周的一天", (1350, 1000, 0.8), shake=[6])
L(sink(1300, 1300), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stink(1260, 1180), 1, 1.8, GREEN, 7, sfx="pop")
T("你真邋遢", PAO1.x, PAO1.y + 28, 60, RED, k0=2, k1=3, sfx="pop")
PAO1.grow(J(), 3, sfx="rim")


def door_fn(c, k, T):
    """室友 + 门：先画室友、再画开着的门；第 6 拍门“砰”地关上，室友出门不见了。"""
    x, y, w, h = DOOR
    slam = T >= b.t_of(J_DOOR, 6)
    tip = None
    man = join(stick(*RM, 0.7), face(*RM, 0.7, "frown"))
    frame = P((x - w / 2, y + h / 2), (x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2))
    leaf_open = join(P((x - w / 2, y - h / 2), (x - w / 2 - 80, y - h / 2 + 40), (x - w / 2 - 80, y + h / 2 - 30),
                       (x - w / 2, y + h / 2)), circle(x - w / 2 - 62, y + 10, 7))
    leaf_shut = join(rect(x, y + 4, w - 22, h - 14, 6), circle(x + w / 2 - 32, y + 10, 9))
    if not slam:
        part, tip = wb.partial(man, clamp01(k / 0.45))
        c.drawPath(part, wb.marker(BLACK, 9))
    if k > 0.55:
        f = clamp01((k - 0.55) / 0.45)
        part, t2 = wb.partial(join(frame, leaf_shut if slam else leaf_open), f)
        c.drawPath(part, wb.marker(BLACK, 9))
        tip = t2 or tip
    return tip


J_DOOR = J()
b.custom(J(), 4, 5.8, door_fn, sfx="wood_high")
H(5, "wood_low")
T("砰！", DOOR[0], 905, 84, RED, k0=6, k1=6.8, sfx="kick")

PAO2 = Pao(2520, 760, 250, 130, tail=-1, n=12, L=46)
scene("上午：你看看人家", "上午 · 小周的一天", (2750, 1000, 0.85))
L(stick(2300, 1420, 0.7, "point"), 0, 0.8, BLACK, 10, sfx="wood_high")
L(face(2300, 1420, 0.7, "flat"), 0.8, 1.0)
PAO2.draw(J(), 1, 1.9, sfx="pop")
T("看看人家小李", PAO2.x, PAO2.y + 28, 56, RED, k0=2, k1=3.5, sfx="pop")
PAO2.grow(J(), 4, sfx="rim")
L(join(stick(2930, 1420, 0.85), face(2930, 1420, 0.85, "smile"), stick(3240, 1420, 0.55),
       face(3240, 1420, 0.55, "frown")), 5, 5.9, BLACK, 9, sfx="wood_high")
L(P((3050, 1180), (3130, 1240), (3050, 1300)), 6, 6.6, RED, 12, sfx="tom")
L(cloud(3250, 1080, 170), 7, 7.8, BLUE, 8, sfx="shaker")

# ---------------------------------------------------------------- drop（场景 4）：几个带刺小泡滚成一个大刺球砸下

DROP_C = (2650, 2300)
MINIS = [(2150, 2060), (2480, 1990), (2820, 1990), (3150, 2060)]
GROUND = 2900
BIG_R = 160


def drop_fn(c, k, T):
    """第 0 拍四个带刺小泡蹦出来；1–2.6 拍往中间滚（边滚边转）；2.6–3 拍挤成一个大刺球；4.4–5 拍砸到地上，裂开几道缝。"""
    jj = J_DROP
    t = lambda kk: b.t_of(jj, kk)  # noqa: E731
    lens_m = [32] * 9
    if T < t(3):
        roll = ease_in_out(clamp01((T - t(1)) / (t(2.6) - t(1))))
        merge = clamp01((T - t(2.6)) / (t(3) - t(2.6)))
        pop = ease_out(clamp01((T - t(0)) / (t(0.4) - t(0))))
        for n, (x0, y0) in enumerate(MINIS):
            x, y = lerp(x0, DROP_C[0], roll), lerp(y0, DROP_C[1], roll)
            sc = pop * (1 - merge)
            if sc <= 0.02:
                continue
            rot = (x - x0) / 90
            draw_pao(c, x, y, 85 * sc, 85 * sc, RED, [l * sc for l in lens_m], "frown", rot=rot, txt=False, width=8,
                     s=max(0.4, sc * 0.75))
        if merge > 0:
            g = ease_out(merge)
            draw_pao(c, DROP_C[0], DROP_C[1], BIG_R * g, BIG_R * g, RED, [52 * g] * 14, "frown", txt=False, width=11,
                     s=max(0.4, 1.3 * g))
        return None
    fall = clamp01((T - t(4.4)) / (t(5) - t(4.4)))
    rest = GROUND - BIG_R - 52
    y = lerp(DROP_C[1], rest, fall * fall)
    squash = 0.0
    if T >= t(5):
        dt = T - t(5)
        squash = 0.12 * math.exp(-dt * 9) * math.cos(dt * 30)
    rot = 0.6 * fall
    draw_pao(c, DROP_C[0], y + BIG_R * squash, BIG_R * (1 + squash), BIG_R * (1 - squash), RED, [52] * 14, "frown",
             rot=rot, txt=False, width=11, s=1.3)
    if T >= t(5):
        f = ease_out(clamp01((T - t(5)) / (t(5.4) - t(5))))
        x0 = DROP_C[0]
        cr = join(P((x0 - 150, GROUND), (x0 - 210, GROUND + 25), (x0 - 300, GROUND + 15)),
                  P((x0 + 150, GROUND), (x0 + 220, GROUND + 28), (x0 + 310, GROUND + 12)),
                  P((x0 - 260, GROUND - 40), (x0 - 330, GROUND - 90)), P((x0 + 260, GROUND - 40), (x0 + 330, GROUND - 90)),
                  P((x0 - 220, GROUND - 120), (x0 - 300, GROUND - 190)), P((x0 + 220, GROUND - 120), (x0 + 300, GROUND - 190)))
        part, _ = wb.partial(cr, f)
        c.drawPath(part, wb.marker(RED, 8))
    return None


J_DROP = scene("没骂人，也扎人", "一天下来", (2650, 2450, 0.75), shake=[0, 5], flashes=[0])
b.custom(J(), 0, 0.4, drop_fn, sfx="kick")
H(1, "wood_high")
H(3, "tom")
L(P((2050, GROUND), (3250, GROUND)), 4, 4.6, BLACK, 10, sfx="wood_low")
H(5, "kick")
T("一个脏字都没有", 2650, 1950, 76, k0=6, k1=7.75, sfx="rim")

# ---------------------------------------------------------------- 书中观点（场景 5–6）

CARD_S = (1260, 2420, 110, 150)       # 书旁的小四格卡：中心、每格宽、高
scene("有本书讲过", "非暴力沟通 · 书中观点", (950, 2450, 0.85))
L(book(680, 2420, 420, 280), 0, 0.9, BLACK, 10, sfx="wood_low")
T("非暴力沟通", 680, 2180, 76, GREEN, k0=1, k1=2.25, sfx="pop")
T("马歇尔 · 卢森堡", 680, 2650, 54, k0=3, k1=4.75, sfx="pop")
L(card_frame(*CARD_S), 5, 5.9, BLACK, 8, sfx="wood_high")
T("四步，后面讲", CARD_S[0], 2560, 50, BLUE, k0=6, k1=7.5, sfx="pop")

CAB = (950, 3680, 620, 660)
SLOTS = [CAB[1] - CAB[3] / 2 + 30 + 75 + 150 * i for i in range(4)]
PULL = 170
KINDS = ("贴标签", "拿人比", "推责任", "硬要求")
scene("扎人的话分几类", "书中观点 · 第二章", (950, 3700, 0.85))
L(join(rect(CAB[0], CAB[1], CAB[2], CAB[3], 16), P((CAB[0] - 250, CAB[1] + CAB[3] / 2), (CAB[0] - 250, CAB[1] + CAB[3] / 2 + 60)),
       P((CAB[0] + 250, CAB[1] + CAB[3] / 2), (CAB[0] + 250, CAB[1] + CAB[3] / 2 + 60))), 0, 0.8, BLACK, 10,
  sfx="wood_low")
J_CAB = J()


def drawer_fn(i):
    def fn(c, k, T):
        """抽屉 i：第 0 拍随柜子画出，第 1+2i 拍往右拉开（露出两条侧板）。"""
        f = ease_out(clamp01((T - b.t_of(J_CAB, 1 + 2 * i)) / (b.t_of(J_CAB, 1.25 + 2 * i) - b.t_of(J_CAB, 1 + 2 * i))))
        x, y = CAB[0] + PULL * f, SLOTS[i]
        w, h = 560, 128
        front = join(rect(x, y, w, h, 10), rect(x + w / 2 - 50, y, 40, 14, 6))
        part, tip = wb.partial(front, k)
        c.drawPath(part, wb.marker(BLACK, 8))
        if f > 0:
            right = CAB[0] + CAB[2] / 2
            c.drawPath(join(P((right, y - h / 2), (x + w / 2, y - h / 2)), P((right, y + h / 2), (x + w / 2, y + h / 2))),
                       wb.marker(BLACK, 6))
        return tip

    return fn


for i in range(4):
    b.custom(J(), 0.2 * i, 0.2 * i + 0.6, drawer_fn(i))
    H(1 + 2 * i, "wood_low")
    T(KINDS[i], CAB[0] + PULL - 40, SLOTS[i], 60, RED, k0=1.2 + 2 * i, k1=2.0 + 2 * i)

# ---------------------------------------------------------------- 故事继续（场景 7–8）

PAO3 = Pao(2400, 3480, 250, 130, tail=1, n=12, L=46)
SIGN = (3050, 3760)
KICK_FROM, KICK_TO = (2610, 4080), (2965, 3770)
scene("下午：我也没办法", "下午 · 小周的一天", (2650, 3750, 0.85))
L(join(stick(2120, 4100, 0.65), face(2120, 4100, 0.65, "flat")), 0, 0.9, BLACK, 9, sfx="wood_high")
L(join(stick(2550, 4100, 0.75, "shrug"), face(2550, 4100, 0.75, "flat")), 1, 1.9, BLACK, 10, sfx="pop")
PAO3.draw(J(), 2, 2.9, sfx="wood_high")
T("规定的，没办法", PAO3.x, PAO3.y + 28, 56, RED, k0=3, k1=4.75, sfx="pop")
L(sign(*SIGN), 5, 5.8, BLACK, 9, sfx="wood_low")
T("规定", SIGN[0], SIGN[1], 70, k0=5.8, k1=6.6)
PAO3.grow(J(), 6, sfx="rim")
J_KICK = J()


def ball_fn(c, k, T):
    """写着“选择”的球：第 7 拍被踢起，第 8 拍撞到“规定”牌子，落在牌子下。"""
    t7, t8 = b.t_of(J_KICK, 7), b.t_of(J_KICK, 8)
    (x0, y0), (x1, y1) = KICK_FROM, KICK_TO
    if T < t8:
        f = clamp01((T - t7) / (t8 - t7))
        x, y = lerp(x0, x1, f), lerp(y0, y1, f) - 260 * 4 * f * (1 - f)
        if 0 < f < 1:
            tr = skia.Path()
            tr.moveTo(x0, y0)
            for i in range(1, 15):
                g = f * i / 14
                tr.lineTo(lerp(x0, x1, g), lerp(y0, y1, g) - 260 * 4 * g * (1 - g))
            c.drawPath(tr, K.paint(BLACK, 0.3, 5))
    else:
        f = ease_in_out(clamp01((T - t8) / (b.t_of(J_KICK, 9) - t8)))
        x, y = lerp(x1 - 10, SIGN[0] - 70, f), lerp(y1, SIGN[1] + 285, f * f)
    c.drawCircle(x, y, 46, K.paint("#FFFFFF"))
    c.drawCircle(x, y, 46, wb.marker(BLUE, 8))
    K.text(c, "选择", x, y, 32, "hand", BLUE)
    return None


b.custom(J(), 6.9, 7.0, ball_fn)
H(7, "wood_high")
H(8, "tom")

PAO4 = Pao(2650, 4810, 250, 130, tail=-1, n=12, L=46)
BANG = (3110, 4800)
scene("晚上：今晚必须来", "晚上 · 小周的一天", (2650, 5000, 0.85))
L(join(stick(2250, 5450, 0.75, "hold"), face(2250, 5450, 0.75, "flat")), 0, 0.9, BLACK, 10, sfx="wood_high")
L(phone(2370, 5265), 1, 1.8, BLUE, 8, sfx="pop")
PAO4.draw(J(), 2, 2.9, sfx="wood_high")
T("今晚必须来接我", PAO4.x, PAO4.y + 28, 54, RED, k0=3, k1=4.75, sfx="pop")
PAO4.grow(J(), 5, sfx="rim")
L(join(bang(*BANG), circle(BANG[0], BANG[1] + 200, 20)), 6, 6.8, RED, 22, sfx="tom")
L(padlock(BANG[0] + 120, BANG[1] + 10), 7, 7.8, BLACK, 8, sfx="wood_low")

# ---------------------------------------------------------------- 回看一天（场景 9，封面镜头）

LINE_Y = 5420
DOTS = [500, 830, 1160, 1490]
MINI = [Pao(x, 5175, 118, 82, tail=-1, n=9, L=34, txt=False) for x in DOTS]
scene("四句话，四根刺", "回看这一天", (1000, 5150, 0.8))
L(join(arrow((360, LINE_Y), (1650, LINE_Y), 0.0, 40), *[circle(x, LINE_Y, 14) for x in DOTS]), 0, 0.8, BLACK, 9,
  sfx="wood_low")
for i, p in enumerate(MINI):
    p.draw(J(), 2 * i, 2 * i + 0.6, sfx="tom" if i else None)
    p.grow(J(), 2 * i + 0.3, sfx=None)
    T(KINDS[i], DOTS[i], 5545, 58, RED, k0=1 + 2 * i, k1=1.8 + 2 * i, sfx="pop")

# ---------------------------------------------------------------- 书里的四步（场景 10）

CARD = (1000, 6480, 270, 300)
ICON_Y = CARD[1] - 40
LAB_Y = CARD[1] + 100
scene("书里给了四步", "书中观点 · 第一章", (1000, 6650, 0.85))
L(card_frame(*CARD), 0, 0.8, BLACK, 10, sfx="wood_low")
for i in range(4):
    L(ICONS[i](cell_x(CARD[0], CARD[2], i), ICON_Y, 1.0), 1 + i, 1.8 + i, BLACK, 8, sfx="pop")
for i in range(4):
    T(LABELS[i], cell_x(CARD[0], CARD[2], i), LAB_Y, 56, BLUE, k0=5 + 0.73 * i, k1=5.8 + 0.73 * i,
      sfx="pop" if i == 0 else None)

# ---------------------------------------------------------------- 重说（场景 11–12）

REWRITE = ("碗放两天了", "我有点烦", "想厨房干净点", "今晚能洗吗？")
PAO5 = Pao(1340, 6960, 165, 115, tail=-1, n=8, L=50, txt=False)
scene("早上那句，重说", "据书中思路 · 改写", (1000, 6900, 0.85))
PAO5.draw(J(), 0, 0.4)
PAO5.grow(J(), 0, dur=0.3, sfx="rim")
for i in range(4):
    b.custom(J(), 2 * i, 2 * i + 0.5, fill_fn(cell_x(CARD[0], CARD[2], i), CARD[1], CARD[2] - 24, CARD[3] - 24))
    T(REWRITE[i], 760, 6770 + i * 125, 58, BLUE, k0=2 * i, sfx="pop")
    PAO5.retract(J(), 1 + 2 * i, (i, i + 4), sfx="shaker" if i < 3 else "ding")

SH = (2650, 6880, 380, 260)
PAO6 = Pao(2650, 6520, 240, 115, tail=0, base=BLUE, mood="smile")
scene("上午那句，重说", "据书中思路 · 改写", (2650, 6950, 0.85))
T("你看看人家小李", 2650, 6520, 64, RED, k0=0, k1=1.75, sfx="pop")
b.erase(J(), 2, 2.8, 2650, 6520, 560, 120)
H(2, "shaker")
L(sheet(*SH), 3, 3.9, BLACK, 9, sfx="wood_high")
L(join(*[circle(*cell_of(*SH, r, cc), 32) for r, cc in ((0, 2), (1, 1), (2, 2))]), 4, 4.8, RED, 8, sfx="rim")
L(join(stick(2290, 7130, 0.7, "point"), face(2290, 7130, 0.7, "smile"),
       mirror(stick(3010, 7130, 0.6, "point"), 3010), face(3010, 7130, 0.6, "smile")), 5, 5.9, BLACK, 9, sfx="pop")
PAO6.draw(J(), 6, 6.5, sfx="pop")
T("一起看一遍？", PAO6.x, PAO6.y + 26, 56, BLUE, k0=6.5, k1=8.0)

# ---------------------------------------------------------------- 回到时间轴（场景 13）

scene("刺少了，话还在", "回看这一天", (1000, 5130, 0.72))
for i, p in enumerate(MINI):
    p.retract(J(), 1 + i, range(9), sfx="pop" if i < 3 else "ding")
T("同一天，换个说法", 1000, 4830, 72, BLUE, k0=5, k1=7, sfx="pop")
L(underline(720, 1280, 4900), 7, 7.8, BLUE, 8, sfx="wood_high")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：第 0 拍拉远看全板，第 4 拍推到评论区

COMMENT = (1800, 8250, 0.8)
PAO7 = Pao(1330, 7820, 120, 80, tail=1, base=BLUE, mood="smile", txt=False)
scene("评论区聊聊", "评论区见", (1800, 4500, 0.105), bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(rect(1800, 8250, 1160, 480, 30), 6, 6.8, BLACK, 9, sfx="wood_high")
PAO7.draw(J(), 6.8, 7.2)
T("你今天说过哪句带刺的话？", 1800, 8150, 62, RED, k0=7, k1=9.75, sfx="pop")
T("下一讲：“你总迟到”，为啥一说就炸？", 1800, 8340, 50, k0=10, k1=13.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "words", "扎人的话", "没骂人，话怎么也扎心？", ACC, b.shots,
                 [f"{BOOK}第一章“让爱融入生活”、第二章“是什么蒙蔽了爱？”、附录“非暴力沟通模式”（转述）",
                  "中译本：阮胤华译，华夏出版社"],
                 "没骂人|话怎么也【扎心】", SQUARE_SHOT,
                 ["书中观点均为转述：第二章把妨碍体谅的说话方式归为几类——道德评判（贴标签、批评、指责）、进行比较、"
                  "回避责任（用“不得不”“公司规定”这类说法把自己的选择推给别人或规定）、强人所难（提要求时暗含不照做就要受罚）；"
                  "第一章与附录讲非暴力沟通的四个要素：观察、感受、需要、请求。上屏均为转述，不是逐字引文。"
                  "出处：Marshall B. Rosenberg, Nonviolent Communication: A Language of Life；中译本《非暴力沟通》，"
                  "马歇尔·卢森堡著，阮胤华译，华夏出版社。",
                  "主角小周和他一天的四句话（“你真邋遢”“你看看人家小李”“公司规定，我也没办法”“今晚必须来接我”）、"
                  "室友、实习生、客户、女朋友均为示意，不指向任何具体公司或个人；时间为示意。",
                  "两句改写（“水池里的碗放两天了，我有点烦，想厨房干净点，今晚能洗掉吗？”“这张表有三处数字对不上，"
                  "我们一起看一遍？”）为示意，据书中思路整理。",
                  "话泡泡“小泡”长刺、缩刺，四个抽屉，“选择”球，四格卡（眼睛 / 心 / 电池 / 手）均为对书中观点的通俗化示意。"],
                 tags="#说话方式 #职场沟通")
    return b.attach(ep)
