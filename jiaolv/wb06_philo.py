"""06 哲学（白板手绘版）：别人一句话，为什么能堵你一整天？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
叙事：打工人切身问题开局（周一开会领导一句“这方案不行” → 一整天脑子里都在转；年夜饭亲戚一句“这么大还没结婚”
→ 饭都不香了）→ 书中观点（亮书《身份的焦虑》+ 德波顿；身份就是别人眼里你值几分，一句差评分就掉；书中的哲学家
（苏格拉底、叔本华、尚福尔等）主张拿理性审视别人的评价：说得对就改，说得不对就放下，别让别人的评价给自己定价；
别人的话只是意见，不算判决）→ 身边的例子（同事说你太较真、朋友圈照片被评显胖、妈说你乱花钱、
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
SQUARE_SHOT = 7

b = Board(size=(3600, 13800))


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


G_X, G_Y, G_W, G_H = 1850, 3760, 110, 520


def level_fn(j8, j9, j16):
    """“别人眼里的分”的刻度：j8 场景第 4.5 拍起升满，j9 场景第 0 拍被砸掉，j16 场景第 2 拍回升。"""

    def fn(c, k, t):
        a0, a1 = b.t_of(j8, 4.5), b.t_of(j8, 5.8)
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


# ---------------------------------------------------------------- 开局：一句话堵一整天（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("领导说方案不行", "灵魂拷问", (950, 850, 0.85))
L(table(950, 1100, 460), 0, 0.6, sfx="wood_high")
L(stick(560, 1250, 0.75, "point", tie=True), 1, 1.6, sfx="pop")
L(stick(1330, 1250, 0.75), 2, 2.4, BLUE, 9, sfx="wood_high")
L(face(1330, 1250, 0.75, "smile"), 2.4, 2.5, BLUE, 8)
L(bubble(780, 700, 420, 130, -1), 3, 3.4, BLACK, 8, sfx="pop")
T("这方案不行", 780, 700, 56, k0=3.4, k1=4.3)
L(doc(950, 970, 150, 190), 4, 4.4, BLACK, 8, sfx="wood_high")
L(cross(950, 970, 70), 5, 5.3, RED, 12, sfx="rim")
L(face(1330, 1250, 0.75, "sad"), 5.4, 5.6, BLUE, 8)

j = scene("一整天都在想", "灵魂拷问", (950, 2200, 0.85))
L(clock(620, 2150, 150), 0, 0.6, sfx="wood_low")
b.custom(j, 1, 4, clock_fn(620, 2150, 150, j, 1, 4), sfx="wood_high")
L(stick(1250, 2550, 0.75), 2, 2.4, BLUE, 9, sfx="pop")
L(face(1250, 2550, 0.75, "sad"), 2.4, 2.5, BLUE, 8)
T("不行…", 1030, 2160, 56, RED, k0=3, sfx="pop")
T("不行…", 1420, 2040, 56, RED, k0=3.6)
T("18:00", 620, 2360, 60, RED, k0=5, sfx="pop")

scene("一句话，堵一整天？", "灵魂拷问", (2650, 850, 0.85), flashes=[5])
L(table(2650, 1100, 900), 0, 0.5, sfx="wood_high")
T("年夜饭", 2650, 560, 64, k0=0.5, k1=1.0)
for n, x in enumerate((2280, 2460, 2640)):
    L(stick(x, 1150, 0.6, hair=n == 1), 1 + n * 0.2, 1.4 + n * 0.2, BLACK, 9, sfx="pop" if n == 0 else None)
L(stick(2980, 1150, 0.6), 2, 2.4, BLUE, 9, sfx="wood_high")
L(face(2980, 1150, 0.6, "smile"), 2.4, 2.5, BLUE, 8)
L(bubble(2580, 720, 520, 130, -1), 3, 3.3, BLACK, 8, sfx="pop")
T("这么大还没结婚？", 2580, 720, 50, k0=3.3, k1=4.2)
L(face(2980, 1150, 0.6, "sad"), 4, 4.2, BLUE, 8, sfx="rim")
T("饭都不香了", 2650, 1300, 54, k0=4.3, k1=5.0)
T("？", 3180, 820, 200, RED, k0=5, k1=5.5, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

BOOKV = (1225, 3680, 0.72)
STK = (1450, 4030, 0.85)
j4 = scene("有本书专讲这事", "身份的焦虑", BOOKV)
L(book(750, 3580, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 750, 3340, 76, GREEN, k0=1, sfx="pop")
T("阿兰 · 德波顿", 750, 3820, 50, k0=2, k1=3, sfx="pop")
T("身份 = 别人眼里的分", 1600, 3340, 60, k0=3, k1=4.4, sfx="pop")
L(gauge(G_X, G_Y, G_W, G_H), 4, 4.5, BLACK, 9, sfx="wood_high")
L(stick(*STK), 5, 5.5, BLUE, 9, sfx="pop")
L(face(*STK, "smile"), 5.5, 5.6, BLUE, 8)
j5 = j4 + 1
j9 = j4 + 5
b.custom(j4, 4.5, 4.6, level_fn(j4, j5, j9))
b.custom(j4, 7.6, 7.7, fall_fn("不行", 150, RED, STK[0], 2900, 3675, j5, 0))

scene("一句差评，分就掉", "书中观点 · 身份", BOOKV, shake=[0], flashes=[0])
H(0, "kick", 1.0)
H(0, "cymbal", 0.4)
L(face(*STK, "sad"), 1, 1.2, BLUE, 8, sfx="pop")
T("堵！", 1150, 3760, 90, RED, k0=2, sfx="tom")
T("分掉了", G_X, 4100, 52, RED, k0=3, sfx="pop")

PV = (1050, 5450, 0.7)
SV = (1100, 5430)
BIN_L, BIN_R = (850, 6000), (1400, 6000)
scene("先拿理性筛一筛", "书中观点 · 哲学", PV)
T("书里的哲学家", 1050, 4840, 64, k0=0, sfx="pop")
T("苏格拉底", 700, 5000, 58, k0=1, sfx="pop")
T("叔本华", 1100, 5000, 58, k0=2, sfx="pop")
T("尚福尔", 1450, 5000, 58, k0=3, sfx="pop")
L(sieve(*SV, 640), 4, 4.9, BLACK, 9, sfx="wood_high")
T("理性", 1100, 5660, 60, RED, k0=5, sfx="pop")

j7 = scene("说得对，就改", "书中观点 · 筛子", PV)
L(stick(450, 5930, 0.7, "point"), 0, 0.5, BLUE, 9, sfx="wood_high")
L(join(bin_(*BIN_L), bin_(*BIN_R)), 1, 1.6, BLACK, 9, sfx="wood_high")
T("改", BIN_L[0], 6070, 60, GREEN, k0=2, sfx="pop")
T("放下", BIN_R[0], 6070, 60, RED, k0=2.4)
b.custom(j7, 3, 3.2, mover("错别字多", 52, BLACK, [(j7, 3, 1100, 5160), (j7, 3.8, 1100, 5390), (j7, 4.1, 1100, 5390),
                                                 (j7, 4.9, BIN_L[0], 5910)], wiggle=(j7, 4)), sfx="pop")
H(4, "shaker")
L(check(BIN_L[0], 5820, 45), 5, 5.3, GREEN, 10, sfx="ding")

j8 = scene("说得不对，就放下", "书中观点 · 筛子", PV)
b.custom(j8, 0, 0.2, mover("你这人不行", 52, RED, [(j8, 0, 1100, 5160), (j8, 0.8, 1100, 5380), (j8, 1.1, 1100, 5380),
                                                 (j8, 1.5, 1450, 5340), (j8, 1.95, BIN_R[0], 5910)],
                           wiggle=(j8, 1)), sfx="pop")
H(1, "wood_high")
H(2, "tom")
L(cross(BIN_R[0], 5910, 70), 3, 3.3, RED, 10, sfx="rim")
L(face(450, 5930, 0.7, "smile"), 4, 4.2, BLUE, 8, sfx="pop")

scene("别人的话只是意见", "书中观点 · 自己打分", BOOKV)
b.erase(J(), 0, 0.4, STK[0], 3710, 320, 260)
H(0, "shaker")
hy = STK[1] - 290 * STK[2]
L(join(circle(STK[0], hy, 45 * STK[2]), P((STK[0], hy + 45 * STK[2]), (STK[0], 3855))), 1, 1.3, BLUE, 9,
  sfx="wood_high")
L(face(*STK, "smile"), 1.3, 1.4, BLUE, 8)
b.erase(J(), 2, 2.3, 1150, 3760, 220, 130)
b.erase(J(), 2, 2.3, G_X, 4100, 220, 90)
H(2, "ding")
T("松了", 1150, 3760, 80, GREEN, k0=3, sfx="pop")
T("意见，不算判决", 1225, 4220, 64, RED, k0=4, k1=5.3, sfx="pop")
L(underline(1000, 1450, 4280), 5.4, 5.8, RED, 8)

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

# 两行卡片上下拉开 1300，免得上一行的字漏进下一行场景的页眉；“全当成了判决”写在两行之间。
CARDS = [(950, 7950), (2650, 7950), (950, 9250), (2650, 9250)]
OVER = (1800, 8600, 0.355)
scene("身边也常碰到", "身边的例子", OVER)
for n, ((x, y), w) in enumerate(zip(CARDS, ("职场", "朋友圈", "家里", "孩子"))):
    L(rect(x, y, 1200, 820, 40), n, n + 0.5, GREEN, 8, sfx="wood_high" if n % 2 == 0 else "pop")
    T(w, x - 600 + 40 + 40 * len(w), y - 340, 64, BLUE, k0=n + 0.5, k1=n + 1.0)
H(4, "ding", 0.6)

scene("被说太较真，闷一下午", "例子 · 职场", (950, 7950, 0.85))
L(stick(650, 8280, 0.7), 0, 0.5, BLUE, 9, sfx="wood_high")
L(stick(1250, 8280, 0.7), 0.5, 1.0, BLACK, 9)
L(face(1250, 8280, 0.7, "flat"), 1.0, 1.1, BLACK, 8)
L(bubble(1100, 7750, 420, 130, 1), 1, 1.4, BLACK, 8, sfx="pop")
T("你也太较真了", 1100, 7750, 50, k0=1.4, k1=2.5)
L(face(650, 8280, 0.7, "sad"), 3, 3.2, BLUE, 8, sfx="pop")
L(clock(560, 7770, 90), 4, 4.5, sfx="wood_high")
L(hands_at(560, 7770, 90, 5, 0), 4.5, 4.7, RED, 9)
T("一下午", 790, 7870, 50, RED, k0=5, sfx="pop")

scene("照片被说显胖，删了", "例子 · 生活", (2650, 7950, 0.85))
L(rect(2500, 7970, 460, 640, 40), 0, 0.6, BLACK, 9, sfx="wood_high")
L(rect(2500, 7900, 360, 300, 10), 0.6, 0.8, BLACK, 7)
L(stick(2500, 8020, 0.33, "up"), 1, 1.3, BLACK, 7, sfx="pop")
L(face(2500, 8020, 0.33, "smile"), 1.3, 1.4, BLACK, 6)
T("周末出去玩", 2500, 7700, 48, k0=2, sfx="pop")
L(stick(3000, 8280, 0.6), 3, 3.4, BLUE, 9, sfx="wood_high")
T("显胖", 2500, 8160, 56, RED, k0=4, sfx="pop")
L(face(3000, 8280, 0.6, "sad"), 4.5, 4.7, BLUE, 8)
L(cross(2500, 7900, 120), 5, 5.3, RED, 10, sfx="rim")
T("删了", 3000, 7850, 60, RED, k0=5.4, k1=5.9)

scene("妈说你乱花钱", "例子 · 家里", (950, 9250, 0.85))
L(stick(620, 9580, 0.65, "point", hair=True), 0, 0.5, BLACK, 9, sfx="wood_high")
L(bubble(830, 9000, 380, 120, -1), 1, 1.4, BLACK, 8, sfx="pop")
T("又乱花钱！", 830, 9000, 52, k0=1.4, k1=2.3)
L(rect(1050, 9500, 160, 150, 10), 2.4, 2.8, BLACK, 8)
T("快递", 1050, 9500, 48, k0=2.8, k1=3.2)
L(stick(1250, 9580, 0.65), 3, 3.4, BLUE, 9, sfx="wood_high")
L(face(1250, 9580, 0.65, "flat"), 3.4, 3.5, BLUE, 8)
L(scribble(1250, 9280, 140, 60, 6), 4, 4.4, RED, 6, sfx="shaker")
L(rect(1450, 9420, 140, 300, 8), 4.5, 4.9, BLACK, 9)
T("砰！", 1400, 9170, 70, RED, k0=5, sfx="rim")

scene("被说画丑，就不画了", "例子 · 孩子", (2650, 9250, 0.85))
L(stick(2300, 9520, 0.45), 0, 0.4, BLUE, 8, sfx="wood_high")
L(join(rect(2620, 9350, 240, 190, 8), circle(2560, 9310, 30), P((2520, 9410), (2600, 9370), (2700, 9410))), 0.5,
  0.9, BLACK, 7)
L(stick(3000, 9520, 0.45), 1, 1.4, BLACK, 8, sfx="pop")
L(bubble(3000, 9110, 240, 110, 1), 2, 2.3, BLACK, 7, sfx="pop")
T("好丑", 3000, 9110, 52, k0=2.3, k1=2.8)
L(face(2300, 9520, 0.45, "sad"), 3, 3.2, BLUE, 7, sfx="wood_low")
L(cross(2620, 9350, 100), 4, 4.3, RED, 10, sfx="rim")
T("不画了", 2330, 9170, 56, BLUE, k0=5, sfx="pop")

scene("每次都当成了判决", "身边的例子", OVER, shake=[4])
for n, (x, y) in enumerate(CARDS):
    T("一句话", x + 400, y - 345, 80, RED, k0=n, sfx="pop")
T("全当成了判决", 1800, 8600, 150, RED, k0=4, k1=4.8, sfx="kick")
H(5, "ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）
# 两行做法卡上下拉开，免得上一行的字漏进下一行场景的页眉。

R1, R2 = 10650, 12050
SOL = [(950, R1), (2650, R1), (950, R2), (2650, R2)]
scene("先把那句话写下来", "第一步 · 写下来", (950, R1, 0.85))
L(rect(*SOL[0], 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("① 写下来", 950, R1 - 300, 76, BLUE, k0=1, sfx="pop")
L(rect(1010, R1 + 50, 640, 360, 14), 2, 2.5, BLACK, 8, sfx="wood_high")
T("这方案不行", 1010, R1 - 30, 60, k0=3, sfx="pop")
T("领导 · 周一上午", 1010, R1 + 90, 50, k0=4, k1=5.0, sfx="pop")
L(stick(480, R1 + 350, 0.5, "hold"), 5, 5.4, BLUE, 8, sfx="wood_high")
L(face(480, R1 + 350, 0.5, "flat"), 5.4, 5.5, BLUE, 7)

QY = (R1 - 100, R1 + 50, R1 + 200)
scene("再问自己三句", "第二步 · 问三句", (2650, R1, 0.85))
L(rect(*SOL[1], 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("② 问三句", 2650, R1 - 300, 76, BLUE, k0=0.5, k1=1.3)
L(stick(2190, R1 + 350, 0.55, "point"), 1, 1.4, BLUE, 8, sfx="pop")
L(join(*(rect(2370, y, 54, 54, 8) for y in QY)), 2, 2.6, BLACK, 7, sfx="wood_high")
for n, q in enumerate(("是事实吗？", "他了解吗？", "对我有用吗？")):
    T(q, 2650, QY[n], 54, k0=3 + n, k1=3.9 + n, sfx="pop")

scene("有用的，就改", "第三步 · 有用的改", (950, R2, 0.85))
L(rect(*SOL[2], 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("③ 有用的改", 950, R2 - 300, 76, BLUE, k0=0.5, k1=1.5)
L(doc(700, R2 + 50, 200, 260, 4), 1, 1.4, BLACK, 8, sfx="pop")
L(arrow((840, R2 + 50), (1060, R2 + 50), 0.1, 36), 2, 2.4, GREEN, 8, sfx="wood_high")
L(doc(1220, R2 + 50, 200, 260, 2), 3, 3.4, BLACK, 8, sfx="pop")
L(join(P((1160, R2 + 150), (1160, R2 + 80)), P((1220, R2 + 150), (1220, R2 + 40)), P((1280, R2 + 150), (1280, R2))), 4,
  4.5, BLUE, 14, sfx="wood_high")
T("补数据", 1220, R2 + 280, 50, k0=4.5, k1=5.0)
L(check(1220, R2 - 140, 50), 5, 5.3, GREEN, 10, sfx="ding")
T("过了", 1420, R2 - 140, 56, RED, k0=5.3, k1=5.8)

scene("没用的，划掉", "第四步 · 没用的划掉", (2650, R2, 0.85))
L(rect(*SOL[3], 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
T("④ 没用的划掉", 2650, R2 - 300, 76, BLUE, k0=0.5, k1=1.5)
T("这么大还没结婚", 2650, R2 - 70, 60, k0=1.5, k1=2.8)
L(stick(2350, R2 + 390, 0.6), 2, 2.4, BLUE, 9, sfx="pop")
L(P((2420, R2 - 70), (2880, R2 - 70)), 3, 3.4, RED, 12, sfx="rim")
L(bubble(2720, R2 + 150, 320, 110, -1), 4, 4.3, BLACK, 8, sfx="pop")
T("不着急", 2720, R2 + 150, 54, k0=4.3, k1=4.85)
L(face(2350, R2 + 390, 0.6, "smile"), 4.85, 5.0, BLUE, 8)
T("翻篇", 3080, R2 + 150, 64, GREEN, k0=5, sfx="ding")

# ---------------------------------------------------------------- 收尾（场景 20–21）

scene("对的改，不对的放下", "一句话", (1800, 6600, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

CY = 13460
scene("评论区聊聊", "评论区见", (1800, CY, 0.8))
H(0, "cymbal", 0.5)
T("哪句话堵你最久？", 1800, CY - 80, 80, RED, k0=1, k1=2.6, sfx="pop")
T("下一讲：为什么看部电影，心里就松了？", 1800, CY + 80, 50, k0=3, k1=4.5, sfx="wood_high")
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")

def build():
    ep = episode(6, "philo", "哲学", "别人一句话，为什么能堵你一整天？", ACC, b.shots,
                 [f"{BOOK}第二部分“解决方法”第一章“哲学”（转述）",
                  "中译本：《身份的焦虑》，阿兰·德波顿著，陈广兴、南治国译，上海译文出版社"],
                 "别人一句话|堵你【一整天】", 7,
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
