"""06 哲学（白板手绘版）：别人一句话，为什么能堵你一整天？

叙事：打工人切身问题开局（周一开会领导一句“这方案不行” → 一整天脑子里都在转；年夜饭亲戚一句“这么大还没结婚”
→ 饭都不香了）→ 书中观点（亮书《身份的焦虑》+ 德波顿；身份就是别人眼里你值几分，一句差评分就掉；书中的哲学家
（苏格拉底、叔本华、尚福尔等）主张拿理性审视别人的评价：说得对就改，说得不对就放下，别让别人的评价给自己定价；
画成一张图：一句话 → 筛一筛 → 改 / 放下）→ 身边的例子（同事说你太较真、朋友圈照片被评显胖、妈说你乱花钱、
孩子画画被同学说丑；每件都是一句话，都被当成了判决）→ 具体做法（把那句话写下来 / 问三句：是事实吗、他了解吗、
对我有用吗 / 有用的改 / 没用的划掉）→ 评论区互动。
书中观点为转述（Alain de Botton, Status Anxiety, 2004；中译本《身份的焦虑》，陈广兴、南治国译，上海译文出版社，
第二部分“解决方法”第一章“哲学”）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               doc, face, hands_at, join, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in, ease_in_out, ease_out

from .common import BOOK, episode

ACC = "#3F7F8C"
SQUARE_SHOT = 12

b = Board(size=(3600, 10500))


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

def table(x, y, w=600) -> skia.Path:
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 40, y), (x - w / 2 + 40, y + 110)),
                P((x + w / 2 - 40, y), (x + w / 2 - 40, y + 110)))


def sieve(x, y, w=640) -> skia.Path:
    """筛子：椭圆口 + 弧形筛底 + 网格 + 右侧把手；(x, y) 为筛口中心。"""
    h = w * 0.45
    rim = skia.Path()
    rim.addOval(skia.Rect.MakeXYWH(x - w / 2, y - 50, w, 100))
    bowl = skia.Path()
    bowl.moveTo(x - w / 2, y)
    bowl.quadTo(x, y + h, x + w / 2, y)
    parts = [rim, bowl]
    for i in range(-3, 4):
        xi = x + i * w / 8
        u = (xi - (x - w / 2)) / w
        top = y + 50 * math.sqrt(max(0.0, 1 - (2 * (xi - x) / w) ** 2))
        parts.append(P((xi, top), (xi, y + h * 2 * u * (1 - u))))
    for f in (0.45, 0.8):
        m = skia.Path()
        m.moveTo(x - w / 2 * (1 - f * 0.35), y + h * f * 0.25)
        m.quadTo(x, y + h * f * 0.95, x + w / 2 * (1 - f * 0.35), y + h * f * 0.25)
        parts.append(m)
    parts.append(P((x + w / 2, y), (x + w / 2 + 150, y - 30)))
    return join(*parts)


def bin_(x, y, w=400, h=240) -> skia.Path:
    """敞口的筐：(x, y) 为筐底中点。"""
    return P((x - w / 2, y - h), (x - w / 2 + 30, y), (x + w / 2 - 30, y), (x + w / 2, y - h))


def gauge(x, y, w=110, h=520) -> skia.Path:
    parts = [rect(x, y, w, h, 30)]
    for n in range(1, 4):
        yy = y + h / 2 - h * n / 4
        parts.append(P((x - w / 2, yy), (x - w / 2 + 30, yy)))
    return join(*parts)


def _at(keys, t):
    """keys: [(镜头, 拍, x, y)]，返回 t 时刻位置（段间缓动）。"""
    ts = [(b.t_of(j, k), x, y) for j, k, x, y in keys]
    if t <= ts[0][0]:
        return ts[0][1], ts[0][2]
    for (t0, x0, y0), (t1, x1, y1) in zip(ts, ts[1:]):
        if t < t1:
            f = ease_in_out(clamp01((t - t0) / max(1e-3, t1 - t0)))
            return x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
    return ts[-1][1], ts[-1][2]


def mover(s, size, color, keys, wiggle=None):
    """会移动的一句话（评价落进筛子）；wiggle=(镜头, 拍) 时在该拍附近左右抖两下。"""

    def fn(c, k, t):
        x, y = _at(keys, t)
        if wiggle:
            tw = b.t_of(*wiggle)
            if 0 <= t - tw < 0.4:
                x += 18 * math.sin((t - tw) * 50) * (1 - (t - tw) / 0.4)
        K.text(c, s, x, y, size, "hand", color)
        return None

    return fn


def fall_fn(s, size, color, x, y0, y1, j, k):
    """红字从上方加速砸下，在 (j, k) 拍落地，落地瞬间压扁一下。"""

    def fn(c, kk, t):
        tl = b.t_of(j, k)
        if t < tl:
            f = ease_in(clamp01(1 - (tl - t) / 0.35))
            K.text(c, s, x, y0 + (y1 - y0) * f, size, "hand", color)
        else:
            sq = 1 - 0.25 * math.exp(-(t - tl) * 12) * (1 if t - tl < 0.5 else 0)
            c.save()
            c.translate(x, y1 + size * 0.4)
            c.scale(1 / sq ** 0.5, sq)
            K.text(c, s, 0, -size * 0.4, size, "hand", color)
            c.restore()
        return None

    return fn


G_X, G_Y, G_W, G_H = 2950, 3000, 110, 520


def level_fn(j8, j9, j16):
    """“别人眼里的分”的刻度：镜头 8 升满，镜头 9 第 0 拍被砸掉，镜头 16 第 2 拍回升。"""

    def fn(c, k, t):
        a0, a1 = b.t_of(j8, 1), b.t_of(j8, 2.5)
        lv = 0.85 * ease_out(clamp01((t - a0) / (a1 - a0)))
        td = b.t_of(j9, 0)
        if t >= td:
            lv = 0.85 - 0.7 * ease_out(clamp01((t - td) / 0.25))
        tr = b.t_of(j16, 2)
        if t >= tr:
            lv = 0.15 + 0.6 * ease_out(clamp01((t - tr) / 0.6))
        hh = (G_H - 24) * lv
        K.rr(c, G_X, G_Y + G_H / 2 - 12 - hh / 2, G_W - 30, hh, 18, GREEN if lv > 0.45 else RED, 0.75)
        return None

    return fn


def clock_fn(x, y, r, j, k0, k1, h0=10, h1=18):
    """时钟指针从 h0 点转到 h1 点。"""

    def fn(c, k, t):
        f = ease_in_out(clamp01((t - b.t_of(j, k0)) / (b.t_of(j, k1) - b.t_of(j, k0))))
        hours = h0 + (h1 - h0) * f
        hh, mm = int(hours), (hours - int(hours)) * 60
        c.drawPath(hands_at(x, y, r, hh % 12, mm), K.paint(RED, 1, 12))
        return None

    return fn


# ---------------------------------------------------------------- 开局：一句话堵一整天（镜头 1–6）

b.shot("周一上午开会", "灵魂拷问", view=(950, 850, 0.85))
L(table(950, 1100, 460), 0, 0.6, sfx="wood_high")
L(stick(560, 1250, 0.75, "point", tie=True), 1, 1.6, sfx="pop")
L(stick(1330, 1250, 0.75), 2, 2.5, BLUE, 9, sfx="wood_high")
L(face(1330, 1250, 0.75, "smile"), 2.5, 2.6, BLUE, 8)
T("周一 10:00", 1180, 520, 60, k0=3, sfx="pop")

b.shot("领导说方案不行", "灵魂拷问", view=(950, 850, 0.85))
L(bubble(780, 700, 420, 130, -1), 0, 0.4, BLACK, 8, sfx="pop")
T("这方案不行", 780, 700, 56, k0=0.4)
L(doc(950, 970, 150, 190), 1, 1.4, BLACK, 8, sfx="wood_high")
L(cross(950, 970, 70), 2, 2.3, RED, 12, sfx="rim")
L(face(1330, 1250, 0.75, "sad"), 3, 3.2, BLUE, 8, sfx="pop")

j3 = b.shot("一整天都在想", "灵魂拷问", view=(950, 1800, 0.85))
L(clock(620, 1750, 150), 0, 0.6, sfx="wood_low")
b.custom(j3, 0.6, 3.6, clock_fn(620, 1750, 150, j3, 1, 3))
H(1, "wood_high", 0.6)
L(stick(1250, 2150, 0.75), 0.4, 0.9, BLUE, 9)
L(face(1250, 2150, 0.75, "sad"), 0.9, 1.0, BLUE, 8)
T("不行…", 1030, 1760, 56, RED, k0=2, sfx="pop")
T("不行…", 1420, 1640, 56, RED, k0=2.5)
T("18:00", 620, 1960, 60, RED, k0=3, sfx="pop")

b.shot("过年回家吃饭", "灵魂拷问", view=(2650, 850, 0.85))
L(table(2650, 1100, 900), 0, 0.5, sfx="wood_high")
for n, x in enumerate((2280, 2460, 2640)):
    L(stick(x, 1150, 0.6, hair=n == 1), 1 + n * 0.2, 1.4 + n * 0.2, BLACK, 9, sfx="pop" if n == 0 else None)
L(stick(2980, 1150, 0.6), 2, 2.4, BLUE, 9, sfx="wood_high")
L(face(2980, 1150, 0.6, "smile"), 2.4, 2.5, BLUE, 8)
T("年夜饭", 2650, 560, 64, k0=3, sfx="pop")

b.shot("这么大还没结婚？", "灵魂拷问", view=(2650, 850, 0.85))
L(bubble(2580, 720, 520, 130, -1), 0, 0.4, BLACK, 8, sfx="pop")
T("这么大还没结婚？", 2580, 720, 50, k0=0.4, k1=1.4)
L(face(2980, 1150, 0.6, "sad"), 2, 2.2, BLUE, 8, sfx="rim")
T("饭都不香了", 2650, 1300, 54, k0=3, sfx="pop")

b.shot("为啥能堵一整天？", "灵魂拷问", view=(1800, 1350, 0.42), flashes=[0])
T("？", 2650, 1850, 520, RED, k0=0, k1=0.6, sfx="kick")
T("一句话，堵一整天", 1800, 2300, 120, k0=1.0, k1=2.2, sfx="pop")
H(3, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "身份的焦虑", view=(1050, 2950, 0.9))
L(book(750, 2950, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 750, 2710, 76, GREEN, k0=1.0, sfx="pop")
T("阿兰 · 德波顿", 750, 3190, 50, k0=2.0, sfx="pop")
T("第二部分 · 哲学", 1350, 2950, 46, k0=3.0, sfx="pop")

STK = (2300, 3300, 0.85)
j8 = b.shot("别人眼里你值几分", "书中观点 · 身份", view=(2650, 2980, 0.85))
T("身份 = 别人眼里的分", 2750, 2560, 60, k0=0, k1=1.2, sfx="pop")
L(gauge(G_X, G_Y, G_W, G_H), 1, 1.6, BLACK, 9, sfx="wood_high")
L(stick(*STK), 2, 2.5, BLUE, 9, sfx="pop")
L(face(*STK, "smile"), 2.5, 2.6, BLUE, 8)
H(3, "ding", 0.6)
j9 = j8 + 1
j16 = j8 + 8
b.custom(j8, 1, 1.1, level_fn(j8, j9, j16))
b.custom(j8, 3.6, 3.7, fall_fn("不行", 150, RED, STK[0], 2380, 2945, j9, 0))

b.shot("一句差评，分就掉", "书中观点 · 身份", view=(2650, 2980, 0.85), shake=[0], flashes=[0])
H(0, "kick", 1.0)
H(0, "cymbal", 0.4)
L(face(*STK, "sad"), 1, 1.2, BLUE, 8, sfx="pop")
T("堵！", 2600, 2950, 90, RED, k0=2, sfx="tom")
T("分掉了", 2950, 3350, 52, RED, k0=3, sfx="pop")

b.shot("哲学家有个办法", "书中观点 · 哲学", view=(1050, 3800, 0.85))
T("书里的哲学家", 1050, 3560, 64, k0=0, sfx="pop")
T("苏格拉底", 700, 3720, 58, k0=1, sfx="pop")
T("叔本华", 1100, 3720, 58, k0=2, sfx="pop")
T("尚福尔", 1450, 3720, 58, k0=3, sfx="pop")

SV = (1100, 4150)
BIN_L, BIN_R = (850, 4800), (1400, 4800)
b.shot("先拿理性筛一筛", "书中观点 · 筛子", view=(1050, 4400, 0.85))
L(sieve(*SV, 640), 0, 0.9, BLACK, 9, sfx="wood_high")
T("理性", 1100, 4380, 60, RED, k0=1, sfx="pop")
L(stick(480, 4800, 0.75, "point"), 1.3, 1.8, BLUE, 9)
L(join(bin_(*BIN_L), bin_(*BIN_R)), 2, 2.6, BLACK, 9, sfx="wood_high")
T("改", BIN_L[0], 4880, 60, GREEN, k0=3, sfx="pop")
T("放下", BIN_R[0], 4880, 60, RED, k0=3.3)

j12 = b.shot("说得对，就改", "书中观点 · 筛子", view=(1050, 4400, 0.85))
b.custom(j12, 0, 0.2, mover("错别字多", 52, BLACK, [(j12, 0, 1100, 3880), (j12, 0.8, 1100, 4110), (j12, 1.1, 1100, 4110),
                                                   (j12, 1.9, BIN_L[0], 4700)], wiggle=(j12, 1)), sfx="pop")
H(1, "shaker")
H(2, "ding")
L(check(BIN_L[0], 4500, 45), 3, 3.3, GREEN, 10, sfx="pop")

j13 = b.shot("说得不对，就放下", "书中观点 · 筛子", view=(1050, 4400, 0.85))
b.custom(j13, 0, 0.2, mover("你这人不行", 52, RED, [(j13, 0, 1100, 3880), (j13, 0.8, 1100, 4100), (j13, 1.1, 1100, 4100),
                                                   (j13, 1.5, 1450, 4060), (j13, 1.95, BIN_R[0], 4700)],
                            wiggle=(j13, 1)), sfx="pop")
H(1, "wood_high")
H(2, "tom")
L(cross(BIN_R[0], 4700, 70), 3, 3.3, RED, 10, sfx="rim")

b.shot("分数自己来打", "书中观点 · 自己打分", view=(2650, 4300, 0.85))
T("我的分，我来打", 2650, 3950, 64, k0=0, sfx="pop")
L(stick(2350, 4700, 0.75, "hold"), 1, 1.5, BLUE, 9, sfx="wood_high")
L(face(2350, 4700, 0.75, "smile"), 1.5, 1.6, BLUE, 8)
L(rect(2850, 4330, 380, 440, 20), 2, 2.4, BLACK, 9, sfx="pop")
T("我的分", 2850, 4200, 56, k0=2.4)
L(check(2850, 4400, 70), 3, 3.3, GREEN, 12, sfx="ding")

b.shot("画成一张图", "书中观点 · 一张图", view=(1800, 3950, 0.38))
L(arrow((2050, 3320), (1500, 3980), 0.15, 50), 0, 0.6, GREEN, 10, sfx="wood_high")
T("一句话 → 筛一筛 → 改 / 放下", 1800, 5000, 96, RED, k0=1, k1=2.8, sfx="pop")
H(3, "ding")

b.shot("筛完，心里就轻了", "书中观点 · 筛完", view=(2650, 2980, 0.85))
b.erase(J(), 0, 0.4, STK[0], 3000, 380, 320)
H(0, "shaker")
hy = STK[1] - 290 * STK[2]
L(join(circle(STK[0], hy, 45 * STK[2]), P((STK[0], hy + 45 * STK[2]), (STK[0], 3170))), 1, 1.3, BLUE, 9,
  sfx="wood_high")
L(face(*STK, "smile"), 1.3, 1.4, BLUE, 8)
b.erase(J(), 2, 2.3, 2600, 2950, 220, 130)
b.erase(J(), 2, 2.3, 2950, 3350, 220, 90)
H(2, "ding")
T("松了", 2600, 2950, 80, GREEN, k0=3, sfx="pop")

b.shot("别人的话只是意见", "书中观点", view=(2650, 3200, 0.85))
T("别人的话", 2650, 3470, 76, k0=0, sfx="pop")
T("意见，不算判决", 2650, 3600, 80, RED, k0=1, sfx="pop")
L(underline(2370, 2930, 3670), 2, 2.5, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 6000), (2650, 6000), (950, 6900), (2650, 6900)]
b.shot("身边也常碰到", "身边的例子", view=(1800, 6450, 0.355))
T("身边的例子", 1800, 5450, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("同事说你太较真", "例子 · 职场", view=(950, 6000, 0.85))
L(stick(650, 6330, 0.7), 0, 0.5, BLUE, 9, sfx="wood_high")
L(stick(1250, 6330, 0.7), 0.5, 1.0, BLACK, 9)
L(bubble(1100, 5800, 420, 130, 1), 1, 1.4, BLACK, 8, sfx="pop")
T("你也太较真了", 1100, 5800, 50, k0=1.4)
L(face(1250, 6330, 0.7, "flat"), 2, 2.2, BLACK, 8, sfx="pop")

b.shot("你一下午没说话", "例子 · 职场", view=(950, 6000, 0.85))
L(face(650, 6330, 0.7, "sad"), 0, 0.2, BLUE, 8, sfx="pop")
L(clock(560, 5820, 90), 1, 1.5, sfx="wood_high")
L(hands_at(560, 5820, 90, 5, 0), 1.5, 1.7, RED, 9)
T("一下午", 790, 5920, 50, RED, k0=2, sfx="pop")
T("……", 650, 5980, 60, BLUE, k0=3, sfx="rim")

b.shot("朋友圈发张照片", "例子 · 生活", view=(2650, 6000, 0.85))
L(rect(2500, 6020, 460, 640, 40), 0, 0.7, BLACK, 9, sfx="wood_high")
L(rect(2500, 5950, 360, 300, 10), 0.8, 1.0, BLACK, 7)
L(stick(2500, 6070, 0.33, "up"), 1, 1.3, BLACK, 7, sfx="pop")
L(face(2500, 6070, 0.33, "smile"), 1.3, 1.4, BLACK, 6)
T("周末出去玩", 2500, 5750, 48, k0=2, sfx="pop")
L(stick(3000, 6330, 0.6), 3, 3.4, BLUE, 9, sfx="wood_high")

b.shot("有人评论显胖", "例子 · 生活", view=(2650, 6000, 0.85))
T("显胖", 2500, 6210, 56, RED, k0=0, sfx="pop")
L(face(3000, 6330, 0.6, "sad"), 1, 1.2, BLUE, 8, sfx="rim")
L(cross(2500, 5950, 120), 2, 2.3, RED, 10, sfx="rim")
T("删了", 3000, 5900, 60, RED, k0=3, sfx="pop")

b.shot("妈说你乱花钱", "例子 · 家里", view=(950, 6900, 0.85))
L(stick(620, 7230, 0.65, "point", hair=True), 0, 0.5, BLACK, 9, sfx="wood_high")
L(bubble(830, 6650, 380, 120, -1), 1, 1.4, BLACK, 8, sfx="pop")
T("又乱花钱！", 830, 6650, 52, k0=1.4)
L(rect(1050, 7150, 160, 150, 10), 2, 2.4, BLACK, 8, sfx="wood_high")
T("快递", 1050, 7150, 48, k0=2.4)

b.shot("你憋着火回屋", "例子 · 家里", view=(950, 6900, 0.85))
L(stick(1250, 7230, 0.65), 0, 0.4, BLUE, 9, sfx="wood_high")
L(face(1250, 7230, 0.65, "flat"), 0.4, 0.5, BLUE, 8)
L(scribble(1250, 6930, 140, 60, 6), 1, 1.4, RED, 6, sfx="shaker")
L(rect(1450, 7070, 140, 300, 8), 2, 2.4, BLACK, 9, sfx="wood_high")
T("砰！", 1400, 6820, 70, RED, k0=3, sfx="pop")

b.shot("同学说他画得丑", "例子 · 孩子", view=(2650, 6900, 0.85))
L(stick(2300, 7170, 0.45), 0, 0.4, BLUE, 8, sfx="wood_high")
L(join(rect(2620, 7000, 240, 190, 8), circle(2560, 6960, 30), P((2520, 7060), (2600, 7020), (2700, 7060))), 0.5,
  0.9, BLACK, 7)
L(stick(3000, 7170, 0.45), 1, 1.4, BLACK, 8, sfx="pop")
L(bubble(3000, 6760, 240, 110, 1), 2, 2.3, BLACK, 7, sfx="pop")
T("好丑", 3000, 6760, 52, k0=2.3)

b.shot("他就不再画了", "例子 · 孩子", view=(2650, 6900, 0.85))
L(face(2300, 7170, 0.45, "sad"), 0, 0.2, BLUE, 7, sfx="pop")
L(cross(2620, 7000, 100), 1, 1.3, RED, 10, sfx="rim")
T("不画了", 2330, 6820, 56, BLUE, k0=2, sfx="pop")
H(3, "wood_low", 0.6)

b.shot("每件都是一句话", "身边的例子", view=(1800, 6450, 0.355))
for n, (x, y) in enumerate(CARDS):
    T("一句话", x + 400, y - 345, 80, RED, k0=n, sfx="pop")

b.shot("全当成了判决", "身边的例子", view=(1800, 6450, 0.355), shake=[0])
T("全当成了判决", 1800, 7450, 150, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 8550), (2650, 8550), (950, 9450), (2650, 9450)]
b.shot("被一句话堵住", "具体做法", view=(1800, 9000, 0.355))
T("被一句话堵住，这样做", 1800, 7980, 110, k0=0, k1=1.6, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先把那句话写下来", "第一步 · 写下来", view=(950, 8550, 0.85))
T("① 写下来", 950, 8250, 76, BLUE, k0=0, sfx="pop")
L(rect(1010, 8600, 640, 360, 14), 1, 1.5, BLACK, 8, sfx="wood_high")
T("这方案不行", 1010, 8520, 60, k0=2, sfx="pop")
L(stick(480, 8900, 0.5, "hold"), 3, 3.4, BLUE, 8, sfx="wood_high")

b.shot("写清谁说的、哪天", "第一步 · 写下来", view=(950, 8550, 0.85))
T("领导 · 周一上午", 1010, 8640, 50, k0=0, sfx="pop")
L(underline(800, 1220, 8570, 10, 30), 1, 1.4, RED, 6, sfx="wood_high")
T("就这一句", 1010, 8740, 48, RED, k0=2, sfx="pop")
L(face(480, 8900, 0.5, "flat"), 3, 3.2, BLUE, 7, sfx="pop")

QY = (8450, 8600, 8750)
b.shot("再问自己三句", "第二步 · 问三句", view=(2650, 8550, 0.85))
T("② 问三句", 2650, 8250, 76, BLUE, k0=0, sfx="pop")
L(stick(2190, 8900, 0.55, "point"), 1, 1.4, BLUE, 8, sfx="wood_high")
L(join(*(rect(2370, y, 54, 54, 8) for y in QY)), 2, 2.6, BLACK, 7, sfx="wood_high")
H(3, "pop", 0.6)

for n, (q, a) in enumerate((("是事实吗？", "数据少了"), ("他了解吗？", "看过全稿"), ("对我有用吗？", "能改更好"))):
    b.shot(("说的是事实吗", "他了解情况吗", "对我有用吗")[n], "第二步 · 问三句", view=(2650, 8550, 0.85))
    T(q, 2620, QY[n], 54, k0=0, sfx="pop")
    T(a, 3020, QY[n], 46, GREEN, k0=1, sfx="pop")
    L(check(2375, QY[n] - 4, 30), 2, 2.3, GREEN, 9, sfx="ding")

b.shot("有用的就改", "第三步 · 有用的改", view=(950, 9450, 0.85))
T("③ 有用的改", 950, 9150, 76, BLUE, k0=0, sfx="pop")
L(doc(700, 9500, 200, 260, 4), 1, 1.4, BLACK, 8, sfx="wood_high")
L(arrow((840, 9500), (1060, 9500), 0.1, 36), 2, 2.4, GREEN, 8, sfx="pop")
L(doc(1220, 9500, 200, 260, 2), 3, 3.4, BLACK, 8, sfx="wood_high")

b.shot("补上两页数据", "第三步 · 有用的改", view=(950, 9450, 0.85))
L(join(P((1160, 9600), (1160, 9530)), P((1220, 9600), (1220, 9490)), P((1280, 9600), (1280, 9450))), 0, 0.5, BLUE,
  14, sfx="wood_high")
T("补数据", 1220, 9730, 50, k0=1, sfx="pop")
L(check(1220, 9310, 50), 2, 2.3, GREEN, 10, sfx="ding")
T("过了", 1420, 9310, 56, RED, k0=3, sfx="pop")

b.shot("没用的划掉", "第四步 · 没用的划掉", view=(2650, 9450, 0.85))
T("④ 没用的划掉", 2650, 9150, 76, BLUE, k0=0, sfx="pop")
T("这么大还没结婚", 2650, 9380, 60, k0=1, sfx="pop")
L(P((2420, 9380), (2880, 9380)), 2, 2.4, RED, 12, sfx="rim")
H(3, "wood_low", 0.6)

b.shot("笑笑说不着急", "第四步 · 没用的划掉", view=(2650, 9450, 0.85))
L(stick(2350, 9840, 0.6), 0, 0.4, BLUE, 9, sfx="wood_high")
L(face(2350, 9840, 0.6, "smile"), 0.4, 0.5, BLUE, 8)
L(bubble(2720, 9600, 320, 110, -1), 1, 1.3, BLACK, 8, sfx="pop")
T("不着急", 2720, 9600, 54, k0=1.3)
T("翻篇", 3000, 9780, 64, GREEN, k0=2, sfx="ding")
L(check(3150, 9770, 36), 3, 3.3, GREEN, 9, sfx="pop")

b.shot("照着做就行", "具体做法", view=(1800, 9000, 0.355))
for n, (x, y) in enumerate(SOL):
    L(check(x + 500, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 else "pop")

b.shot("对的改，不对的放下", "一句话", view=(1800, 5350, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 10200, 0.8))
T("哪句话堵你最久？", 1800, 10120, 80, RED, k0=0.5, k1=1.6)
T("下一讲：为什么看部电影，心里就松了？", 1800, 10280, 50, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "philo", "哲学", "别人一句话，为什么能堵你一整天？", ACC, b.shots,
                 [f"{BOOK}第二部分“解决方法”第一章“哲学”（转述）",
                  "中译本：《身份的焦虑》，阿兰·德波顿著，陈广兴、南治国译，上海译文出版社"],
                 "别人一句话|堵你【一整天】", 12,
                 ["书中观点均为转述：书中的“身份”指社会地位，即你在别人眼里值多少；哲学一章介绍苏格拉底、叔本华、尚福尔等"
                  "哲学家的主张——用理性审视公众意见与别人的批评，说得对就改，说得不对就放下，不必让别人的评价决定自己的价值。"
                  "出处：Alain de Botton, Status Anxiety (Hamish Hamilton / Pantheon, 2004)，中译本《身份的焦虑》"
                  "（陈广兴、南治国译，上海译文出版社），第二部分“解决方法”第一章“哲学”。上屏均为转述，不是逐字引文；"
                  "只写思想家名字，不画肖像。",
                  "刻度条“别人眼里的分”、红字砸下、筛子与两只筐为对书中观点的通俗化示意，不是书中图示或数据。",
                  "领导说方案不行、亲戚催婚、同事说太较真、朋友圈照片被评显胖、妈说乱花钱、孩子画画被同学说丑均为现实场景示意，"
                  "不指向任何具体公司或个人；时间为示意。",
                  "四步做法（把那句话写下来、问三句：是事实吗 / 他了解吗 / 对我有用吗、有用的改、没用的划掉）为据书中思路整理的建议。"],
                 tags="#情绪 #自我价值")
    return b.attach(ep)
