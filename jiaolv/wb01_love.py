"""01 爱的渴求（白板手绘版）：为什么那么在意别人怎么看你？

叙事：打工人切身问题开局（周末爬山发朋友圈一个赞都没有 → 开会发言没人接 → 领导叫错你名字 → 晚上还在想）→
书中观点（亮书《身份的焦虑》、德波顿；先交代“身份”：你在别人眼里值多少，怕往下掉就是身份焦虑，人人都有；
第一章“爱的渴求”：人追求地位，图的是被看见、被重视、被善待；书中引亚当·斯密、威廉·詹姆斯：没人理睬比受罚还难受；
作者把自我比作一个漏气的气球，要靠外界的关注不断充气——画成会漏气、会鼓起来的动态气球）→
身边的例子（熬夜改完方案领导只夸别人、饭馆举手半天没人来、过年饭桌都在夸表哥、回家想说件事对方在刷手机；
每张卡里手上的小气球都瘪了）→ 具体做法（找几个稳定打气的人 / 一次冷场不算数 / 先去看见别人 / 发完就放下手机）→ 评论区互动。
书中观点为转述（Alain de Botton, Status Anxiety, 2004；中译本《身份的焦虑》，陈广兴、南治国译，上海译文出版社；
“界定”与第一部分第一章“爱的渴求”）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               face, hands_at, join, marker, partial, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out

from .common import BOOK, episode

ACC = "#D9573B"
SQUARE_SHOT = 15

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
    return join(rect(x, y, w, h, 12 if w < 200 else 40), P((x - w * 0.17, y + h / 2 - h * 0.08),
                                                           (x + w * 0.17, y + h / 2 - h * 0.08)))


def eye(x, y, w=360, h=150) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.quadTo(x, y - h, x + w / 2, y)
    p.quadTo(x, y + h, x - w / 2, y)
    return join(p, circle(x, y, h * 0.42), circle(x, y, h * 0.16))


def heart(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + 40 * s)
    p.cubicTo(x - 70 * s, y - 5 * s, x - 45 * s, y - 60 * s, x, y - 25 * s)
    p.cubicTo(x + 45 * s, y - 60 * s, x + 70 * s, y - 5 * s, x, y + 40 * s)
    return p


def mountains(x, y, w=380) -> skia.Path:
    return join(P((x - w / 2, y), (x - w / 6, y - 150), (x + w / 12, y - 50), (x + w / 4, y - 110), (x + w / 2, y)),
                circle(x + w / 3, y - 190, 30))


def ladder(x, y0, y1, w=200, step=110) -> skia.Path:
    parts = [P((x - w / 2, y0), (x - w / 2, y1)), P((x + w / 2, y0), (x + w / 2, y1))]
    yy = y0 - 60
    while yy > y1 + 20:
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
        yy -= step
    return join(*parts)


def table(x, y, w=420, leg=110) -> skia.Path:
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 30, y), (x - w / 2 + 30, y + leg)),
                P((x + w / 2 - 30, y), (x + w / 2 - 30, y + leg)))


def monitor_desk(x, y, w=440) -> skia.Path:
    """工位：桌面 + 桌腿 + 一块大屏（屏幕中心在 (x, y - 130)）。"""
    return join(table(x, y, w), rect(x, y - 130, 260, 170, 10), P((x, y - 45), (x, y)))


def hold_hand(x, y, s):
    """stick(..., arms="hold") 的右手位置。"""
    hy = y - 290 * s
    return x + 110 * s, hy + 90 * s


class Balloon:
    """会漏气、会鼓起来的气球：keys = [(镜头, 拍, 半径)]，相邻关键帧之间缓动变化；绳子拴在 hand 上。"""

    def __init__(self, x, y, keys, hand, label="", color=RED, width=9):
        self.x, self.y, self.keys, self.hand, self.label = x, y, keys, hand, label
        self.color, self.width = color, width

    def r(self, t):
        ks = [(b.t_of(j, k), r) for j, k, r in self.keys]
        if t <= ks[0][0]:
            return ks[0][1]
        for (t0, r0), (t1, r1) in zip(ks, ks[1:]):
            if t < t1:
                return r0 + (r1 - r0) * ease_in_out(clamp01((t - t0) / max(1e-3, t1 - t0)))
        return ks[-1][1]

    def path(self, r):
        x, y = self.x, self.y + (self.keys[0][2] - r) * 0.9       # 瘪下去时往下沉一点
        body = skia.Path()
        body.addOval(skia.Rect.MakeXYWH(x - 0.85 * r, y - 1.1 * r, 1.7 * r, 2.2 * r))
        ky = y + 1.1 * r
        kn = max(10.0, 0.12 * r)
        knot = P((x, ky), (x - kn, ky + kn * 1.2), (x + kn, ky + kn * 1.2), close=True)
        hx, hy = self.hand
        string = skia.Path()
        string.moveTo(x, ky + kn * 1.2)
        string.quadTo((x + hx) / 2 + 40, (ky + hy) / 2, hx, hy)
        return join(body, knot, string), (x, y)

    def fn(self):
        def draw(c, k, t):
            r = self.r(t)
            pth, (x, y) = self.path(r)
            if k >= 1:
                c.drawOval(skia.Rect.MakeXYWH(x - 0.85 * r, y - 1.1 * r, 1.7 * r, 2.2 * r), K.paint(self.color, 0.13))
            part, tip = partial(pth, k)
            c.drawPath(part, marker(self.color, self.width))
            if self.label and k >= 1:
                K.text(c, self.label, x, y, 0.55 * r, "hand", self.color)
            return tip if k < 1 else None

        return draw

    def knot(self, t):
        r = self.r(t)
        return self.x, self.y + (self.keys[0][2] - r) * 0.9 + 1.1 * r


def puff_fn(bal, j, beats):
    """漏气：每个拍点从气球口喷出一小股气。"""

    def fn(c, k, t):
        kx, ky = bal.knot(t)
        for kb in beats:
            dt = t - b.t_of(j, kb)
            if 0 <= dt < 0.6:
                a = 1 - dt / 0.6
                for n, ang in enumerate((-0.5, 0.0, 0.5)):
                    d0, d1 = 30 + dt * 120, 70 + dt * 220
                    dx, dy = math.sin(ang + 1.2), math.cos(ang + 1.2)
                    c.drawPath(P((kx + dx * d0, ky + dy * d0 * 0.4), (kx + dx * d1, ky + dy * d1 * 0.4)),
                               marker(BLUE, 6, a))
        return None

    return fn


def scale_fn(x, y, j, left, right, tilt_beat, half=330, tilt=14):
    """天平：横梁两端挂盘，拍点 1、2 写上两边的字，tilt_beat 拍往右边（更重）倒。"""

    def fn(c, k, t):
        f = ease_out(clamp01((t - b.t_of(j, tilt_beat)) / 0.35))
        wob = math.sin((t - b.t_of(j, tilt_beat)) * 18) * math.exp(-(t - b.t_of(j, tilt_beat)) * 5) * 3 if f > 0 else 0
        a = math.radians(tilt * f + wob)
        ends = [(x - half * math.cos(a), y - half * math.sin(a)), (x + half * math.cos(a), y + half * math.sin(a))]
        beam = P(ends[0], ends[1])
        parts = [beam]
        for ex, ey in ends:
            bowl = skia.Path()
            bowl.moveTo(ex - 120, ey + 150)
            bowl.quadTo(ex, ey + 230, ex + 120, ey + 150)
            bowl.close()
            parts += [P((ex, ey), (ex - 120, ey + 150)), P((ex, ey), (ex + 120, ey + 150)), bowl]
        pth = join(*parts)
        part, tip = partial(pth, clamp01(k * 1.0))
        c.drawPath(part, marker(BLACK, 9))
        for n, (s, col_, kb) in enumerate(((left, BLACK, 1), (right, RED, 2))):
            if t >= b.t_of(j, kb):
                ex, ey = ends[n]
                K.text(c, s, ex, ey + 260, 60, "hand", col_)
        return tip if k < 1 else None

    return fn


def clock_spin_fn(x, y, r, j, k0, k1, turns=1.0):
    """钟表分针转圈：表示时间过去。"""

    def fn(c, k, t):
        f = clamp01((t - b.t_of(j, k0)) / max(1e-3, b.t_of(j, k1) - b.t_of(j, k0)))
        a = -math.pi / 2 + f * turns * 2 * math.pi
        c.drawPath(P((x, y), (x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8)), marker(RED, 9))
        return None

    return fn


# ---------------------------------------------------------------- 开局：没人搭理（镜头 1–6）

b.shot("朋友圈发了张照片", "灵魂拷问", view=(950, 850, 0.85))
L(phone(950, 860, 560, 760), 0, 0.8, BLACK, 9, sfx="wood_high")
T("朋友圈", 950, 560, 52, k0=0.8)
L(rect(950, 780, 440, 300, 10), 1, 1.3, BLACK, 7, sfx="pop")
L(mountains(950, 900, 400), 1.3, 1.9, GREEN, 8)
T("周末爬山", 950, 1010, 56, k0=2, sfx="pop")
L(heart(780, 1120, 0.6), 3, 3.3, RED, 7, sfx="pop")

b.shot("一个赞都没有", "灵魂拷问", view=(950, 850, 0.85))
T("0", 870, 1120, 70, RED, k0=0, k1=0.3, sfx="pop")
L(arrow((1400, 640), (1400, 900), -0.6, 40), 1, 1.5, BLUE, 8, sfx="wood_high")
T("刷新", 1430, 980, 52, BLUE, k0=1.5)
T("还是 0", 1420, 1110, 60, RED, k0=2, sfx="rim")
H(3, "wood_low")

b.shot("开会发言没人接", "灵魂拷问", view=(2650, 850, 0.85))
L(table(2750, 1050, 760), 0, 0.5, BLACK, 10, sfx="wood_high")
L(stick(2200, 1250, 0.7, "point"), 0.5, 1.0, BLUE, 9)
L(bubble(2450, 560, 460, 130, -1), 1, 1.4, BLUE, 8, sfx="pop")
T("我建议……", 2450, 560, 60, BLUE, k0=1.4)
for n, x in enumerate((2620, 2850, 3080)):
    L(stick(x, 1250, 0.55), 2 + n * 0.2, 2.3 + n * 0.2, BLACK, 8, sfx="wood_high" if n == 0 else None)
    L(face(x, 1250, 0.55, "flat"), 2.3 + n * 0.2, 2.4 + n * 0.2, BLACK, 7)
T("……", 2850, 780, 70, k0=3, sfx="rim")

b.shot("领导叫错你名字", "灵魂拷问", view=(950, 1800, 0.85))
L(stick(650, 2150, 0.75, "point", tie=True), 0, 0.6, BLACK, 9, sfx="wood_high")
L(face(650, 2150, 0.75, "smile"), 0.6, 0.7)
L(bubble(800, 1500, 440, 130, -1), 1, 1.4, BLACK, 8, sfx="pop")
T("小……小刘？", 800, 1500, 60, k0=1.4)
L(stick(1250, 2150, 0.75), 2, 2.5, BLUE, 9, sfx="wood_high")
L(face(1250, 2150, 0.75, "flat"), 2.5, 2.6, BLUE, 8)
T("我姓周", 1250, 1780, 60, BLUE, k0=3, sfx="rim")

b.shot("晚上还在想", "灵魂拷问", view=(2650, 1800, 0.85))
L(clock(2300, 1500, 110), 0, 0.6, BLACK, 9, sfx="wood_low")
L(hands_at(2300, 1500, 110, 11, 30), 0.6, 0.8, RED, 10)
T("23:30", 2300, 1680, 56, RED, k0=1, sfx="pop")
L(stick(2400, 2150, 0.7), 1.5, 1.9, BLUE, 9)
L(face(2400, 2150, 0.7, "sad"), 1.9, 2.0, BLUE, 8)
L(bubble(2900, 1550, 520, 150, -1), 2, 2.4, BLACK, 8, sfx="wood_high")
T("是我不行吗", 2900, 1550, 64, k0=2.4)
L(scribble(2950, 1900, 300, 120, 7), 3, 3.4, RED, 7, sfx="shaker")

b.shot("为啥这么在意？", "灵魂拷问", view=(1800, 1350, 0.42), flashes=[0])
T("？", 1800, 1850, 460, RED, k0=0, k1=0.6, sfx="kick")
T("为什么这么在意", 1800, 2280, 120, k0=1.0, k1=2.2, sfx="pop")
H(3, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书专讲这个", "身份的焦虑", view=(1050, 2950, 0.9))
L(book(750, 2950, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 750, 2710, 80, GREEN, k0=1.0, sfx="pop")
T("阿兰 · 德波顿", 750, 3190, 52, k0=2.0, sfx="pop")

LAD_X = 2250
b.shot("在别人眼里值多少", "书中观点 · 身份", view=(2650, 2950, 0.85))
L(ladder(LAD_X, 3330, 2450), 0, 0.8, BLACK, 9, sfx="wood_high")
L(stick(LAD_X, 2830, 0.45, "up"), 1, 1.4, BLUE, 8, sfx="pop")
T("身份", 2850, 2560, 100, RED, k0=1.5)
T("= 你在别人眼里", 2850, 2730, 64, k0=2, sfx="pop")
T("值多少", 2850, 2850, 64, k0=3, sfx="pop")

b.shot("怕掉下去，就焦虑", "书中观点 · 界定", view=(2650, 2950, 0.85), shake=[0], flashes=[0])
T("身份焦虑", 2850, 3200, 150, RED, k0=0, k1=0.5, sfx="kick")
L(arrow((LAD_X + 160, 2780), (LAD_X + 160, 3200), 0.15, 40), 1, 1.4, RED, 10, sfx="tom")
L(face(LAD_X, 2830, 0.45, "sad"), 2, 2.2, BLUE, 7, sfx="rim")
L(underline(2420, 3280, 3300), 3, 3.4, RED, 8)
H(3, "tom", 0.6)

b.shot("人人都有一点", "书中观点 · 界定", view=(950, 3150, 0.85))
for n, x in enumerate((450, 650, 850, 1050, 1250, 1450)):
    L(stick(x, 3480, 0.4), n * 0.3, n * 0.3 + 0.4, BLACK, 7, sfx="wood_high" if n in (0, 3) else None)
for n, x in enumerate((450, 850, 1250)):
    T("？", x + 60, 3290, 60, RED, k0=2 + n * 0.4, k1=2.3 + n * 0.4, sfx="pop" if n == 0 else None)
H(3, "pop", 0.6)

EYE = (950, 3950)
b.shot("图的是被看见", "第一章 · 爱的渴求", view=(950, 4200, 0.85))
L(eye(*EYE, 380, 160), 0, 0.8, BLACK, 9, sfx="wood_high")
for n, (w, x) in enumerate((("被看见", 600), ("被重视", 950), ("被善待", 1300))):
    T(w, x, 4210, 66, RED if n == 0 else BLACK, k0=1 + n, sfx="pop")

b.shot("书里引了两个人", "书中提到", view=(950, 4200, 0.85))
b.erase(J(), 0, 0.5, 950, 4030, 1260, 480)
H(0, "shaker")
L(rect(650, 3680, 460, 120, 30), 1, 1.3, GREEN, 7, sfx="wood_high")
T("亚当 · 斯密", 650, 3680, 56, k0=1.3)
L(rect(1250, 3680, 460, 120, 30), 2, 2.3, GREEN, 7, sfx="wood_high")
T("威廉 · 詹姆斯", 1250, 3680, 56, k0=2.3)
T("都说过", 950, 3830, 56, k0=3, sfx="pop")

SC = (950, 4100)
b.shot("被无视比挨罚难受", "书中观点 · 没人理睬", view=(950, 4200, 0.85))
L(join(P((SC[0], SC[1]), (SC[0], 4710)), P((SC[0] - 140, 4710), (SC[0] + 140, 4710)), circle(SC[0], SC[1], 16)),
  0, 0.5, BLACK, 10, sfx="wood_high")
b.custom(J(), 0.5, 1.0, scale_fn(SC[0], SC[1], J(), "挨罚", "没人理", 3))
H(1, "pop")
H(2, "pop")
H(3, "kick", 0.9)

BAL_STICK = (2300, 4630, 0.8)
BAL_HAND = hold_hand(*BAL_STICK)
j_bal = len(b.shots)
BAL = Balloon(2700, 3980, [(j_bal, 1, 160), (j_bal + 1, 0, 160), (j_bal + 1, 3.2, 95), (j_bal + 2, 1, 95),
                           (j_bal + 2, 1.4, 130), (j_bal + 2, 2, 130), (j_bal + 2, 2.4, 170), (j_bal + 2, 3, 170),
                           (j_bal + 2, 3.4, 210), (j_bal + 3, 2, 210), (j_bal + 3, 2.6, 120)], BAL_HAND, "自我")

b.shot("自我像个气球", "书中比喻 · 气球", view=(2650, 4200, 0.85))
L(stick(*BAL_STICK, "hold"), 0, 0.6, BLUE, 9, sfx="wood_high")
L(face(*BAL_STICK, "smile"), 0.6, 0.7, BLUE, 8)
b.custom(J(), 1, 2, BAL.fn(), sfx="pop")
T("气球", 2330, 3950, 64, k0=2.5)
H(3, "ding", 0.6)

b.shot("可它一直在漏气", "书中比喻 · 漏气", view=(2650, 4200, 0.85))
b.custom(J(), 0, 4, puff_fn(BAL, J(), (0, 1, 2)), sfx="shaker")
H(1, "shaker", 0.6)
T("嘶……", 2980, 4450, 60, BLUE, k0=1.2)
L(face(*BAL_STICK, "sad"), 2, 2.2, BLUE, 8, sfx="rim")
H(3, "wood_low")

AIR = [("赞", 3130, 3710), ("夸你", 3130, 3950), ("记得你", 3130, 4190)]
b.shot("得靠别人来打气", "书中比喻 · 打气", view=(2650, 4200, 0.85))
for n, (w, x, y) in enumerate(AIR):
    T(w, x, y, 60, RED, k0=n, k1=n + 0.3, sfx="pop")
    L(arrow((x - 90, y + 40), (2930, 3980 + (n - 1) * 90), 0.1, 32), n + 0.3, n + 0.7, GREEN, 8)
L(face(*BAL_STICK, "smile"), 3, 3.2, BLUE, 8, sfx="ding")

b.shot("有人看就鼓起来", "书中观点 · 一张图", view=(1800, 4050, 0.38))
T("被关注 → 鼓起来", 1800, 4870, 100, GREEN, k0=0, k1=1.2, sfx="pop")
T("没人理 → 瘪下去", 1800, 5020, 100, RED, k0=2, k1=3.2, sfx="rim")
H(3, "ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5800), (2650, 5800), (950, 6700), (2650, 6700)]
YOU_S = 0.6
mini = []                    # 每张卡里你手上的小气球


def you_and_balloon(n, j_deflate):
    """卡片 n 左下角的你（蓝色）+ 手上的小气球；j_deflate 镜头第 2–3 拍瘪下去。"""
    x, y = CARDS[n]
    sx, sy = x - 400, y + 330
    L(stick(sx, sy, YOU_S, "hold"), 0, 0.5, BLUE, 9, sfx="wood_high")
    L(face(sx, sy, YOU_S, "smile"), 0.5, 0.6, BLUE, 8)
    bal = Balloon(x - 330, y - 150, [(J(), 1, 70), (j_deflate, 2, 70), (j_deflate, 3.3, 34)],
                  hold_hand(sx, sy, YOU_S), color=RED, width=7)
    b.custom(J(), 0.6, 1.2, bal.fn())
    mini.append(bal)
    return sx, sy


b.shot("身边也常碰到", "身边的例子", view=(1800, 6250, 0.355))
T("身边的例子", 1800, 5250, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

# 职场
b.shot("熬夜改完方案", "例子 · 职场", view=(950, 5800, 0.85))
you_and_balloon(0, J() + 1)
L(monitor_desk(1050, 6000, 460), 1, 1.6, BLACK, 9, sfx="wood_high")
T("1:00", 1050, 5870, 64, RED, k0=2, sfx="pop")
L(check(900, 5690, 40), 3, 3.3, GREEN, 9, sfx="ding")
T("改完了", 1060, 5690, 52, GREEN, k0=3.3)

b.shot("领导只夸了别人", "例子 · 职场", view=(950, 5800, 0.85))
L(stick(1380, 6160, 0.55, "point", tie=True), 0, 0.5, BLACK, 9, sfx="wood_high")
L(bubble(1250, 5480, 360, 110, 1), 1, 1.3, BLACK, 8, sfx="pop")
T("小王真棒！", 1250, 5480, 54, k0=1.3)
L(face(CARDS[0][0] - 400, CARDS[0][1] + 330, YOU_S, "flat"), 2, 2.2, BLUE, 8, sfx="rim")
H(3, "shaker", 0.7)

# 生活
b.shot("饭馆里喊点单", "例子 · 生活", view=(2650, 5800, 0.85))
you_and_balloon(1, J() + 1)
L(table(2800, 6050, 480), 1, 1.4, BLACK, 9, sfx="wood_high")
L(bubble(2560, 5660, 340, 110, -1), 2, 2.3, BLUE, 8, sfx="pop")
T("服务员！", 2560, 5660, 56, BLUE, k0=2.3)
T("菜单", 2800, 5990, 50, k0=3, sfx="pop")

b.shot("半天没人过来", "例子 · 生活", view=(2650, 5800, 0.85))
L(clock(3050, 5560, 80), 0, 0.5, BLACK, 8, sfx="wood_high")
b.custom(J(), 0, 3, clock_spin_fn(3050, 5560, 80, J(), 0, 3, 2))
T("二十分钟", 3050, 5720, 50, RED, k0=1, sfx="pop")
L(face(CARDS[1][0] - 400, CARDS[1][1] + 330, YOU_S, "sad"), 2, 2.2, BLUE, 8, sfx="rim")
H(3, "shaker", 0.7)

# 家庭
b.shot("过年饭桌夸表哥", "例子 · 家庭", view=(950, 6700, 0.85))
you_and_balloon(2, J() + 1)
L(table(1150, 6900, 620), 1, 1.3, BLACK, 9, sfx="wood_high")
for n, x in enumerate((960, 1150, 1340)):
    L(stick(x, 6990, 0.42, hair=n == 2), 1.3 + n * 0.2, 1.6 + n * 0.2, BLACK, 7)
L(bubble(1100, 6420, 440, 110, 1), 2, 2.3, BLACK, 8, sfx="pop")
T("表哥真出息！", 1100, 6420, 54, k0=2.3)
T("哈哈", 960, 6560, 50, k0=3, sfx="pop")

b.shot("没人问你咋样", "例子 · 家庭", view=(950, 6700, 0.85))
L(face(CARDS[2][0] - 400, CARDS[2][1] + 330, YOU_S, "flat"), 0, 0.2, BLUE, 8, sfx="pop")
T("我呢？", 760, 6800, 56, BLUE, k0=1, sfx="wood_high")
H(2, "rim")
H(3, "shaker", 0.7)

# 家里
b.shot("回家想说件事", "例子 · 家里", view=(2650, 6700, 0.85))
you_and_balloon(3, J() + 1)
L(stick(3000, 7030, 0.6, "hold"), 1, 1.5, BLACK, 9, sfx="wood_high")
L(bubble(2620, 6560, 400, 110, -1), 2, 2.3, BLUE, 8, sfx="pop")
T("今天我……", 2620, 6560, 56, BLUE, k0=2.3)
H(3, "pop", 0.6)

b.shot("对方在刷手机", "例子 · 家里", view=(2650, 6700, 0.85))
L(phone(3090, 6830, 70, 120), 0, 0.3, BLACK, 8, sfx="wood_high")
L(bubble(3060, 6420, 220, 100, -1), 1, 1.3, BLACK, 7, sfx="pop")
T("嗯嗯", 3060, 6420, 52, k0=1.3)
L(face(CARDS[3][0] - 400, CARDS[3][1] + 330, YOU_S, "sad"), 2, 2.2, BLUE, 8, sfx="rim")
H(3, "shaker", 0.7)

b.shot("气球都瘪了", "身边的例子", view=(1800, 6250, 0.355))
for n, (x, y) in enumerate(CARDS):
    T("瘪了", x - 120, y - 200, 100, RED, k0=n, sfx="pop")

b.shot("缺的都是被看见", "身边的例子", view=(1800, 6250, 0.355), shake=[0])
T("缺的都是被看见", 1800, 7250, 150, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 8350), (2650, 8350), (950, 9250), (2650, 9250)]
b.shot("气瘪了这样补", "具体做法", view=(1800, 8800, 0.355))
T("气瘪了，这样补", 1800, 7780, 130, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

# ① 找几个稳定打气的人
ME1 = (950, 8640, 0.6)
FR = [("爸妈", 520), ("老友", 720), ("搭子", 1380)]
j1 = len(b.shots)
b.shot("找几个打气的人", "第一步 · 打气的人", view=(950, 8350, 0.85))
T("① 找几个打气的人", 950, 8050, 66, BLUE, k0=0, sfx="pop")
L(stick(*ME1, "hold"), 1, 1.5, BLUE, 9, sfx="wood_high")
L(face(*ME1, "smile"), 1.5, 1.6, BLUE, 8)
for n, (w, x) in enumerate(FR):
    L(stick(x, 8640, 0.5), 2 + n * 0.25, 2.3 + n * 0.25, BLACK, 8, sfx="pop" if n == 0 else None)
BAL1 = Balloon(1080, 8270, [(j1, 3, 40), (j1 + 1, 3, 40), (j1 + 1, 3.4, 75)], hold_hand(*ME1), color=RED, width=7)
b.custom(j1, 3, 3.5, BAL1.fn(), sfx="wood_high")

b.shot("家人老友最稳", "第一步 · 打气的人", view=(950, 8350, 0.85))
for n, (w, x) in enumerate(FR):
    T(w, x, 8705, 48, k0=n, sfx="pop")
L(arrow((1290, 8380), (1160, 8300), 0.1, 30), 3, 3.3, GREEN, 8, sfx="ding")

b.shot("周末约老友吃饭", "第一步 · 打气的人", view=(950, 8350, 0.85))
T("周末约饭", 600, 8220, 56, RED, k0=0, sfx="pop")
T("打个视频", 600, 8330, 56, RED, k0=1, sfx="pop")
L(check(790, 8330, 34), 2, 2.3, GREEN, 9, sfx="ding")
H(3, "pop", 0.6)

# ② 一次冷场不算数
b.shot("一次冷场别当真", "第二步 · 不算数", view=(2650, 8350, 0.85))
T("② 一次冷场不算数", 2650, 8050, 66, BLUE, k0=0, sfx="pop")
L(phone(2330, 8400, 280, 380), 1, 1.6, BLACK, 9, sfx="wood_high")
T("0 赞", 2330, 8380, 64, RED, k0=2, sfx="pop")
H(3, "wood_low")

for n, w in enumerate(("在开会", "在带娃", "没刷到")):
    if n == 0:
        b.shot("大家可能在忙", "第二步 · 不算数", view=(2650, 8350, 0.85))
    L(bubble(2900, 8240 + n * 150, 300, 100, -1), n, n + 0.3, BLACK, 7, sfx="pop")
    T(w, 2900, 8240 + n * 150, 52, k0=n + 0.3)
H(3, "ding", 0.6)

b.shot("你还是那个你", "第二步 · 不算数", view=(2650, 8350, 0.85))
T("0 赞 ≠ 我不行", 2650, 8680, 66, RED, k0=0, sfx="pop")
L(underline(2400, 2900, 8730), 1, 1.5, RED, 7, sfx="wood_high")
L(check(3050, 8670, 40), 2, 2.3, GREEN, 10, sfx="ding")
H(3, "pop", 0.6)

# ③ 先去看见别人
ME3, CO3 = (650, 9580, 0.6), (1250, 9580, 0.6)
j3 = len(b.shots)
b.shot("先去看见别人", "第三步 · 看见别人", view=(950, 9250, 0.85))
T("③ 先去看见别人", 950, 8950, 66, BLUE, k0=0, sfx="pop")
L(eye(950, 9130, 260, 110), 1, 1.6, BLACK, 8, sfx="wood_high")
L(stick(*ME3), 2, 2.4, BLUE, 9, sfx="pop")
L(face(*ME3, "smile"), 2.4, 2.5, BLUE, 8)
L(stick(*CO3, "hold"), 3, 3.4, BLACK, 9, sfx="wood_high")
L(face(*CO3, "flat"), 3.4, 3.5, BLACK, 8)

b.shot("记住新同事名字", "第三步 · 看见别人", view=(950, 9250, 0.85))
b.erase(J(), 0, 0.4, 950, 9130, 420, 260)
H(0, "shaker")
L(bubble(850, 9150, 340, 110, -1), 1, 1.3, BLUE, 8, sfx="pop")
T("小林早！", 850, 9150, 56, BLUE, k0=1.3)
L(face(*CO3, "smile"), 2, 2.2, BLACK, 8, sfx="ding")
H(3, "pop", 0.6)

BAL3 = Balloon(1400, 9180, [(j3 + 2, 2, 40), (j3 + 2, 3, 40), (j3 + 2, 3.4, 70)], hold_hand(*CO3), color=RED, width=7)
b.shot("开会帮着接一句", "第三步 · 看见别人", view=(950, 9250, 0.85))
L(bubble(830, 9330, 400, 110, -1), 0, 0.3, BLUE, 8, sfx="pop")
T("这个点子好！", 830, 9330, 52, BLUE, k0=0.3)
b.custom(J(), 1, 1.6, BAL3.fn(), sfx="wood_high")
L(check(1100, 9330, 36), 2, 2.3, GREEN, 9, sfx="ding")
H(3, "pop", 0.7)

# ④ 发完就放下手机
b.shot("发完就放下手机", "第四步 · 放下手机", view=(2650, 9250, 0.85))
T("④ 发完就放下", 2650, 8950, 66, BLUE, k0=0, sfx="pop")
L(phone(2400, 9200, 220, 320), 1, 1.5, BLACK, 9, sfx="wood_high")
L(arrow((2400, 9400), (2400, 9530), 0, 34), 2, 2.3, GREEN, 8, sfx="wood_high")
L(join(P((2200, 9580), (2650, 9580)), rect(2420, 9555, 160, 40, 8)), 3, 3.4, BLACK, 9, sfx="pop")

b.shot("过一小时再看", "第四步 · 放下手机", view=(2650, 9250, 0.85))
L(clock(2950, 9220, 110), 0, 0.5, BLACK, 9, sfx="wood_high")
b.custom(J(), 0.5, 3, clock_spin_fn(2950, 9220, 110, J(), 0.5, 3, 1))
H(1, "wood_low", 0.6)
T("1 小时后", 2950, 9420, 56, RED, k0=2, sfx="pop")
L(check(3160, 9420, 32), 3, 3.3, GREEN, 9, sfx="ding")

b.shot("缺气了就找人打气", "一句话", view=(1800, 5150, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 10000, 0.8))
T("最近谁给你打过气？", 1800, 9920, 80, RED, k0=0.5, k1=1.8)
T("下一讲：一换工作，亲戚的脸色怎么就变了？", 1800, 10080, 50, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "love", "爱的渴求", "为什么那么在意别人怎么看你？", ACC, b.shots,
                 [f"{BOOK}“界定”、第一部分第一章“爱的渴求”（转述）",
                  "中译本：《身份的焦虑》，阿兰·德波顿著，陈广兴、南治国译，上海译文出版社"],
                 "别人怎么看你|为啥这么【在意】", SQUARE_SHOT,
                 ["书中观点均为转述：“界定”中，身份焦虑指担心自己达不到社会定义的成功、因而失去尊严和别人的尊重，"
                  "这种担心几乎人人都有；书里的“身份”指社会地位，即你在别人眼里值多少。第一部分第一章“爱的渴求”："
                  "人追求地位，很大程度是想被看见、被重视、被善待；书中引亚当·斯密、威廉·詹姆斯的说法，大意是没人理睬比受罚还难受；"
                  "作者把自我比作一个漏气的气球，要靠外界的关注不断充气。出处：Alain de Botton, Status Anxiety "
                  "(Hamish Hamilton / Pantheon, 2004)，中译本《身份的焦虑》（陈广兴、南治国译，上海译文出版社）。"
                  "上屏均为转述，不是逐字引文；画面中只写思想家名字，不画肖像。",
                  "朋友圈没人点赞、开会发言没人接、领导叫错名字、熬夜改方案只夸别人、饭馆半天没人来、过年饭桌夸表哥、"
                  "回家说事对方在刷手机均为现实场景示意，不指向任何具体公司或个人；时间、“0 赞”“二十分钟”等均为示意；"
                  "梯子、天平与气球的大小变化为对书中观点的通俗化示意。",
                  "四步做法（找几个稳定打气的人、一次冷场不算数、先去看见别人、发完就放下手机）为据书中思路整理的建议。"],
                 tags="#在意别人看法")
    return b.attach(ep)
