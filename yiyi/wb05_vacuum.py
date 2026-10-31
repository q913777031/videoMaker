"""05 存在的空虚（白板手绘版）：周日晚上，为什么特别没劲？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（白板手绘慢速讲解版）。
叙事（E 自测清单）：周日下午阿宁躺在沙发上、手机刷了三小时越刷越空 → 抛问题 →
对照一张自测清单逐条打勾（周末比上班还累、一闲下来就心慌）→ drop：往心里倒刷剧、外卖、购物车，
桶底漏了，倒进去全漏光 → 再勾三条（买完东西高兴不过一晚、不知道下周盼什么、一停就空）、数勾 →
揭晓：书里给这个起了名字（亮书）→ 书中观点：空虚多半表现为无聊，“星期天神经症”——一周忙完、闲下来发觉
日子没内容；空虚常拿钱、权、乐子来填，填不满 → 解读：勾得多，缺一件“为谁做”的事，罗盘乱转 →
做法（周日为别人做件小事 / 给下周定个盼头写进日历 / 先补桶底，罗盘停住）→ 拉远看全板 → 评论区互动。
书中观点为转述（Viktor E. Frankl, Man's Search for Meaning，第二部分〈存在之虚无〉；
中译本《活出生命的意义》，吕娜译，华夏出版社 2010）；自测清单、桶的比喻、例子为示意，做法据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, face,
                               hands_at, join, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#4E7A8C"
SQUARE_SHOT = 3                 # 场景 4：漏底的桶 + 阿宁

b = Board(size=(3600, 10000))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def TL(s, left, y, size=64, color=BLACK, k0=0.0, k1=None, sfx=None):
    """左对齐写字（清单条目）。"""
    T(s, left + K.text_w(s, size, "hand") / 2, y, size, color, k0, k1, sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(len(b.shots) - 1, k, sfx, gain, note)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def rot(path: skia.Path, deg, px, py) -> skia.Path:
    m = skia.Matrix()
    m.setRotate(deg, px, py)
    p = skia.Path(path)
    p.transform(m)
    return p


def sofa(x, y) -> skia.Path:
    """沙发：(x, y) 为坐垫中点。"""
    return join(rect(x, y - 130, 620, 170, 40), rect(x, y, 660, 90, 30), rect(x - 350, y - 40, 80, 210, 30),
                rect(x + 350, y - 40, 80, 210, 30), P((x - 290, y + 45), (x - 290, y + 110)),
                P((x + 290, y + 45), (x + 290, y + 110)))


def lying(fx, fy, s=0.7, mood="flat") -> skia.Path:
    """躺平的阿宁：脚在 (fx, fy)，头朝左。"""
    return rot(join(stick(fx, fy, s, "down"), face(fx, fy, s, mood)), -90, fx, fy)


def phone(x, y, w, h) -> skia.Path:
    return join(rect(x, y, w, h, 40), P((x - w * 0.15, y + h / 2 - 34), (x + w * 0.15, y + h / 2 - 34)))


def bars_down(x, y) -> skia.Path:
    """越来越矮的三根柱子 + 底线。(x, y) 为底线中点。"""
    parts = [P((x - 170, y), (x + 170, y))]
    for n, h in enumerate((200, 120, 45)):
        cx = x - 110 + n * 110
        parts.append(P((cx - 35, y), (cx - 35, y - h), (cx + 35, y - h), (cx + 35, y)))
    return join(*parts)


def bucket(x, y, w=560, h=540, crack=True) -> skia.Path:
    """水桶：(x, y) 为桶口中点；crack=True 时桶底中间留一道缺口。"""
    rim = skia.Path()
    rim.addOval(skia.Rect.MakeXYWH(x - w / 2, y - 55, w, 110))
    bw = w * 0.75
    parts = [rim, P((x - w / 2, y), (x - bw / 2, y + h)), P((x + w / 2, y), (x + bw / 2, y + h)),
             P((x - w / 2 + 30, y + h * 0.35), (x + w / 2 - 30, y + h * 0.35))]
    if crack:
        parts += [P((x - bw / 2, y + h), (x - 60, y + h)), P((x + 60, y + h), (x + bw / 2, y + h))]
    else:
        parts.append(P((x - bw / 2, y + h), (x + bw / 2, y + h)))
    return join(*parts)


def crack_mark(x, y) -> skia.Path:
    """桶底裂缝：(x, y) 为桶底中点。"""
    return join(P((x - 60, y), (x - 25, y - 50), (x + 5, y - 10), (x + 30, y - 60), (x + 60, y)),
                P((x - 20, y + 25), (x - 30, y + 70)), P((x + 15, y + 30), (x + 20, y + 85)))


def patch(x, y, w=200, h=90) -> skia.Path:
    parts = [rect(x, y, w, h, 10)]
    for n in range(4):
        sx = x - w / 2 + 30 + n * (w - 60) / 3
        parts.append(P((sx, y - h / 2 - 14), (sx, y - h / 2 + 18)))
        parts.append(P((sx, y + h / 2 - 18), (sx, y + h / 2 + 14)))
    return join(*parts)


def tv(x, y, s=1.0) -> skia.Path:
    tri = P((x - 18 * s, y - 25 * s), (x + 26 * s, y), (x - 18 * s, y + 25 * s), close=True)
    return join(rect(x, y, 150 * s, 100 * s, 14 * s), tri, P((x - 30 * s, y - 50 * s), (x - 55 * s, y - 85 * s)),
                P((x + 30 * s, y - 50 * s), (x + 55 * s, y - 85 * s)))


def takeout(x, y, s=1.0) -> skia.Path:
    return join(P((x - 70 * s, y - 35 * s), (x - 52 * s, y + 45 * s), (x + 52 * s, y + 45 * s), (x + 70 * s, y - 35 * s),
                  close=True),
                P((x - 80 * s, y - 35 * s), (x - 60 * s, y - 55 * s), (x + 60 * s, y - 55 * s), (x + 80 * s, y - 35 * s)),
                P((x + 10 * s, y - 62 * s), (x + 90 * s, y - 130 * s)))


def cart(x, y, s=1.0) -> skia.Path:
    return join(P((x - 95 * s, y - 55 * s), (x - 65 * s, y - 55 * s), (x - 40 * s, y + 25 * s), (x + 70 * s, y + 25 * s),
                  (x + 85 * s, y - 35 * s), (x - 55 * s, y - 35 * s)),
                circle(x - 25 * s, y + 50 * s, 13 * s), circle(x + 55 * s, y + 50 * s, 13 * s))


def clipboard(x, y, w=1000, h=1300) -> skia.Path:
    return join(rect(x, y, w, h, 30), rect(x, y - h / 2, 260, 70, 16))


def box(x, y, r=34) -> skia.Path:
    return rect(x, y, 2 * r, 2 * r, 8)


def week(x0, y, labels, cw=150, ch=150):
    """一排日历格：返回（格子路径，各格中心 x 列表）。"""
    n = len(labels)
    parts = [rect(x0 + n * cw / 2, y, n * cw, ch, 14)]
    for i in range(1, n):
        parts.append(P((x0 + i * cw, y - ch / 2), (x0 + i * cw, y + ch / 2)))
    return join(*parts), [x0 + cw / 2 + i * cw for i in range(n)]


def flag(x, y, s=1.0) -> skia.Path:
    """小旗：(x, y) 为旗杆底。"""
    return join(P((x, y), (x, y - 120 * s)), P((x, y - 120 * s), (x + 80 * s, y - 95 * s), (x, y - 70 * s)))


def parcel(x, y, s=1.0) -> skia.Path:
    w, h = 200 * s, 150 * s
    return join(rect(x, y, w, h, 8), P((x - w / 2, y - h / 2 + 30 * s), (x + w / 2, y - h / 2 + 30 * s)),
                P((x, y - h / 2), (x, y + h / 2)), P((x - 30 * s, y + 20 * s), (x + 30 * s, y + 20 * s)))


def bike(x, y, s=1.0) -> skia.Path:
    """自行车（侧视）：(x, y) 为地面中点。"""
    r = 70 * s
    a, c = (x - 120 * s, y - r), (x + 120 * s, y - r)
    seat, bar = (x - 40 * s, y - 175 * s), (x + 90 * s, y - 185 * s)
    mid = (x, y - r)
    return join(circle(*a, r), circle(*c, r), P(a, seat, mid, a), P(mid, (x + 75 * s, y - 165 * s), c),
                P(seat, (x + 75 * s, y - 165 * s)), P((x - 70 * s, y - 175 * s), (x - 10 * s, y - 175 * s)),
                P((x + 75 * s, y - 165 * s), bar, (x + 120 * s, y - 195 * s)))


def compass(x, y, r=70) -> skia.Path:
    """系列视觉角色·小罗盘：圆框 + 刻度 + 顶上小环（指针另画）。"""
    parts = [circle(x, y, r), circle(x, y - r - 14, 13), circle(x, y, 6)]
    for i in range(4):
        a = i * math.pi / 2
        parts.append(P((x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72),
                       (x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9)))
    return join(*parts)


def _needle(c, x, y, r, ang):
    L_, w = r * 0.78, r * 0.2
    ca, sa = math.cos(ang), math.sin(ang)
    tip, tail = (x + ca * L_, y + sa * L_), (x - ca * L_, y - sa * L_)
    l, rr = (x - sa * w, y + ca * w), (x + sa * w, y - ca * w)
    K.poly(c, [tip, l, (x, y), rr], RED)
    c.drawPath(P(tail, l, (x, y), rr, close=True), K.paint(BLACK, 1, 5))
    c.drawPath(P(tip, l, tail, rr, close=True), K.paint(BLACK, 1, 5))


def spin_fn(x, y, r, speed=7.0):
    """指针乱转：转速忽快忽慢、来回晃（不收笔尖，手停在原处）。"""

    def fn(c, k, t):
        _needle(c, x, y, r, t * speed + 1.6 * math.sin(t * 2.3))
        return None

    return fn


def settle_fn(x, y, r, final_deg, turns=2.5):
    """指针转几圈后慢下来，停在 final_deg（0° 朝右、90° 朝下）。"""

    def fn(c, k, t):
        f = 1 - (1 - clamp01(k)) ** 3
        _needle(c, x, y, r, math.radians(final_deg) + (1 - f) * turns * 2 * math.pi)
        return None

    return fn


def fall_fn(icon, start, top, end, label):
    """东西倒进桶：从阿宁手里抛到桶口（前 40%），再穿过漏底掉到地上（后 60%）。"""

    def fn(c, k, t):
        if k < 0.4:
            f = k / 0.4
            x = start[0] + (top[0] - start[0]) * f
            y = start[1] + (top[1] - start[1]) * f - 220 * 4 * f * (1 - f)
        else:
            f = ((k - 0.4) / 0.6) ** 2
            x = top[0] + (end[0] - top[0]) * f
            y = top[1] + (end[1] - top[1]) * f
        p = skia.Path(icon)
        p.offset(x, y)
        c.drawPath(p, wb.marker(BLACK, 8))
        K.text(c, label, x, y + 105, 48, "hand", BLUE)
        return None

    return fn


def scroll_fn(x, y, w, h):
    """手机里不停往上滑的卡片。"""

    def fn(c, k, t):
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(x - w / 2 + 14, y - h / 2 + 14, w - 28, h - 90))
        off = (t * 260) % 180
        for i in range(-1, 6):
            cy = y - h / 2 + 90 + i * 180 - off
            c.drawPath(rect(x, cy, w - 90, 140, 14), wb.marker(BLACK, 6))
            c.drawPath(P((x - w / 2 + 80, cy - 20), (x + w / 2 - 120, cy - 20)), wb.marker(BLACK, 5, 0.5))
            c.drawPath(P((x - w / 2 + 80, cy + 25), (x + 20, cy + 25)), wb.marker(BLACK, 5, 0.5))
        c.restore()
        return None

    return fn


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 开局：周日下午（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("周日下午躺着", "周日下午", (900, 900, 0.85), bars=2)
L(sofa(820, 1180), 0, 0.9, sfx="wood_high")
L(lying(1020, 1090, 0.7), 1, 1.9, BLUE, 9, sfx="pop")
L(join(clock(1250, 600, 95), hands_at(1250, 600, 95, 4, 0)), 2, 2.9, BLACK, 8, sfx="wood_high")
T("16:00", 1250, 780, 64, RED, k0=3, k1=4.2, sfx="pop")
T("周日", 560, 640, 96, k0=5, k1=5.8, sfx="pop")

PH = (1600, 1000, 420, 680)
scene("越刷越没劲", "周日下午", (1750, 900, 0.85))
L(phone(*PH), 0, 0.9, BLACK, 9, sfx="wood_high")
b.custom(J(), 1, 11.5, scroll_fn(*PH), sfx="shaker")
T("刷了 3 小时", 2130, 760, 60, RED, k0=2, k1=3.5, sfx="pop")
L(bars_down(2130, 1130), 4, 4.9, BLUE, 9, sfx="wood_high")
T("越刷越空", 2130, 1220, 56, BLUE, k0=5, k1=6, sfx="pop")
T("为什么特别没劲？", 1750, 470, 84, RED, k0=6, k1=8, sfx="kick")

# ---------------------------------------------------------------- 自测清单（场景 3–6），drop 在场景 4

CB = (900, 2650)
BX, LEFT = 510, 580
ROWS = [2340, 2520, 2700, 2880, 3060]
ITEMS = ["周末比上班还累", "一闲下来就心慌", "买完东西，高兴不过一晚", "不知道下周盼什么", "忙的时候还好，一停就空"]


def row(n, k, color=BLACK):
    """第 n 条：框（k 起 0.3 拍）+ 条目文字（之后约 2 拍），返回写完的拍。"""
    L(box(BX, ROWS[n]), k, k + 0.3, BLACK, 7, sfx="wood_high")
    end = k + 0.3 + min(2.4, max(0.8, 0.25 * len(ITEMS[n])))
    TL(ITEMS[n], LEFT, ROWS[n], 64, color, k0=k + 0.3, k1=end)
    return end


def tick(n, k):
    L(check(BX + 4, ROWS[n] - 6, 40), k, k + 0.5, RED, 10, sfx="pop")


scene("对照打个勾", "自测清单", (900, 2450, 0.8))
L(clipboard(*CB), 0, 0.9, BLACK, 9, sfx="wood_high")
T("周末自测", 900, 2150, 76, k0=1, k1=2, sfx="pop")
row(0, 2)
tick(0, 4)
row(1, 5)
tick(1, 7)

BK = (2650, 2380)               # 桶口中点
HOLD = (2230, 2650)             # 阿宁的手
scene("倒进去，全漏了", "往心里倒东西", (2650, 2650, 0.8), shake=[0], flashes=[0])
L(bucket(*BK), 0, 0.6, BLACK, 11, sfx="kick")
L(crack_mark(BK[0], BK[1] + 540), 0.6, 1.0, RED, 9)
L(stick(2170, 3000, 0.75, "hold"), 1, 1.8, BLUE, 9, sfx="wood_high")
L(face(2170, 3000, 0.75, "flat"), 1.8, 2.0, BLUE, 8)
ICONS = [(tv(0, 0, 0.9), 2550, "刷剧"), (takeout(0, 0, 0.95), 2790, "外卖"), (cart(0, 0, 0.95), 3020, "购物车")]
for n, (icon, ex, lab) in enumerate(ICONS):
    b.custom(J(), 2 + n, 3.4 + n, fall_fn(icon, HOLD, (BK[0], BK[1] - 20), (ex, 3060), lab),
             sfx="tom" if n == 2 else "pop")
T("还是空", 3150, 2620, 80, RED, k0=6, k1=7, sfx="rim")
L(underline(3020, 3280, 2700), 7, 7.8, RED, 8, sfx="ding")

V_LIST = (900, 2680, 0.62)
scene("再勾两条", "自测清单", V_LIST)
row(2, 0)
tick(2, 3)
row(3, 4)
tick(3, 7)

scene("一停就空", "自测清单", V_LIST)
row(4, 0)
tick(4, 3)
L(P((420, ROWS[0] - 40), (395, ROWS[0] - 40), (395, ROWS[4] + 40), (420, ROWS[4] + 40)), 4, 4.8, RED, 8,
  sfx="wood_low")
T("勾了 5 个", 720, 3210, 72, RED, k0=5, k1=6.5, sfx="ding")
T("你呢？", 1130, 3210, 72, BLUE, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- 揭晓：书里的说法（场景 7–9）

scene("书里有个名字", "活出生命的意义 · 书中观点", (1450, 4250, 0.8))
L(join(rect(1000, 4280, 230, 300, 16), rect(1000, 4130, 90, 30, 8),
       *[check(965, 4185 + i * 55, 16) for i in range(5)],
       *[P((1000, 4185 + i * 55), (1080, 4185 + i * 55)) for i in range(5)]), 0, 0.9, BLACK, 7, sfx="wood_high")
L(arrow((1150, 4280), (1380, 4270), -0.1, 36), 2, 2.8, BLACK, 8, sfx="wood_high")
L(book(1680, 4280, 440, 290), 3, 3.9, BLACK, 10, sfx="wood_low")
T("活出生命的意义", 1680, 4010, 64, GREEN, k0=4, k1=5.75, sfx="pop")
T("弗兰克尔", 1680, 4560, 56, k0=6, k1=7, sfx="pop")

WK = ["一", "二", "三", "四", "五", "六", "日"]
scene("星期天神经症", "书中观点 · 星期天神经症", (2900, 4250, 0.8))
T("星期天神经症", 2900, 3850, 88, RED, k0=0, k1=1.5, sfx="ding")
grid, xs = week(2375, 4230, WK)
L(grid, 2, 2.6, BLACK, 8, sfx="wood_high")
for i, (w, x) in enumerate(zip(WK, xs)):
    b.text(J(), 2.6 + i * 0.12, 2.72 + i * 0.12, w, x, 4080, 50, RED if w == "日" else BLACK)
L(join(*[scribble(x, 4230, 100, 100, 6) for x in xs[:6]]), 3, 3.9, BLACK, 6, sfx="shaker")
L(circle(xs[6], 4230, 50), 4, 4.7, RED, 9, sfx="rim")
T("一周忙完，闲下来发现日子空着", 2900, 4470, 50, k0=5, k1=7, sfx="pop")
T("多半是无聊", 2900, 4580, 58, BLUE, k0=7, k1=8)

BK2 = (2900, 5330)
scene("拿别的东西填", "书中观点 · 拿别的填", (2900, 5520, 0.8))
L(bucket(*BK2, 460, 420), 0, 0.9, BLACK, 10, sfx="wood_high")
for n, (w, x, y) in enumerate((("钱", 2420, 5110), ("权", 2900, 5060), ("乐子", 3380, 5110))):
    T(w, x, y, 72, RED, k0=2 + n, k1=2.5 + n + 0.3, sfx="pop")
    tx = BK2[0] + (x - BK2[0]) * 0.3
    L(arrow((x + (0 if n == 1 else (60 if n == 0 else -60)), y + 50), (tx, BK2[1] - 30), 0.08 if n == 0 else -0.08,
            30), 2.8 + n, 3.0 + n + 0.0, RED, 7)
L(join(crack_mark(BK2[0], BK2[1] + 420), P((2860, 5820), (2850, 5870)), P((2950, 5830), (2955, 5880))), 5, 5.8,
  BLUE, 8, sfx="rim")
T("填不满", 2900, 6000, 76, RED, k0=6, k1=7, sfx="ding")

# ---------------------------------------------------------------- 解读（场景 10）

AN = (760, 6000)
CP = (960, 5700)
scene("缺一件为谁做的事", "据书中思路 · 解读", (1150, 5550, 0.8))
L(stick(*AN, 0.85, "hold"), 0, 0.9, BLUE, 10, sfx="wood_high")
L(face(*AN, 0.85, "flat"), 0.9, 1.1, BLUE, 8)
L(compass(*CP, 75), 2, 2.8, BLACK, 8, sfx="pop")
b.custom(J(), 3, 11.8, spin_fn(*CP, 75), sfx="shaker")
L(rect(1450, 5500, 520, 170, 20), 5, 5.8, BLACK, 7, sfx="wood_high")
T("为了 ____", 1450, 5500, 64, k0=5.8, k1=6.8)
T("缺一件为谁做的事", 1250, 5130, 64, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 做法（场景 11–13）

scene("周日为谁做件事", "第一步 · 为谁做件事", (1150, 7000, 0.8))
T("① 为别人做件小事", 1150, 6550, 72, BLUE, k0=0, k1=2, sfx="pop")
L(parcel(820, 6950), 2, 2.9, BLACK, 9, sfx="wood_high")
T("寄给爸妈", 820, 7150, 56, k0=3, k1=4, sfx="pop")
L(bike(1480, 7040, 0.9), 5, 5.9, BLACK, 9, sfx="wood_high")
T("帮邻居打气", 1480, 7150, 56, k0=6, k1=7.25, sfx="pop")
L(check(1150, 7300, 40), 7.4, 7.9, GREEN, 10)

WK2 = ["日", "一", "二", "三", "四", "五", "六"]
scene("下周有个盼头", "第二步 · 定个盼头", (2900, 7000, 0.8))
T("② 给下周定个盼头", 2900, 6550, 72, BLUE, k0=0, k1=2, sfx="pop")
grid2, xs2 = week(2410, 6950, WK2, 140, 140)
L(join(grid2, P((2550, 6860), (2550, 7040))), 2, 2.7, BLACK, 8, sfx="wood_high")
for i, (w, x) in enumerate(zip(WK2, xs2)):
    b.text(J(), 2.7 + i * 0.12, 2.82 + i * 0.12, w, x, 6810, 48, BLACK)
L(flag(xs2[3] - 20, 7010, 0.75), 4, 4.7, RED, 9, sfx="pop")
T("约朋友爬山", xs2[3], 7140, 56, RED, k0=5, k1=6.25, sfx="pop")
L(arrow((xs2[0], 7040), (xs2[3] - 50, 7060), 0.25, 30), 7, 7.8, GREEN, 8, sfx="ding")

BK3 = (2600, 8180)
AN3 = (1950, 8800)
CP3 = (2090, 8420)
scene("先补桶底", "第三步 · 补桶底", (2300, 8400, 0.8))
L(stick(*AN3, 0.8, "hold"), 0, 0.9, BLUE, 10, sfx="wood_high")
L(face(*AN3, 0.8, "smile"), 0.9, 1.1, BLUE, 8)
L(compass(*CP3, 60), 1.2, 1.9, BLACK, 7)
L(bucket(*BK3, 460, 420), 2, 2.8, BLACK, 10, sfx="wood_low")
L(patch(BK3[0], BK3[1] + 420), 3, 3.8, RED, 9, sfx="pop")
T("为谁做的事", BK3[0], BK3[1] + 560, 56, GREEN, k0=4, k1=5.25, sfx="pop")
L(join(circle(2540, 8520, 40), rect(2650, 8520, 90, 70, 8), P((2470, 8570), (2730, 8570))), 6, 6.8, BLACK, 7,
  sfx="wood_high")
b.custom(J(), 6, 8, settle_fn(*CP3, 60, -25))
H(8, "ding", note="罗盘停住")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 4750, 0.18)
COMMENT = (1800, 9550, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(bubble(1800, 9470, 900, 170, -1), 5, 5.9, BLACK, 8, sfx="wood_low")
T("你勾了几条？", 1800, 9470, 80, RED, k0=6, k1=7.5, sfx="pop")
T("下一讲：撑不住的时候，你会想起谁？", 1800, 9690, 48, k0=9, k1=13, sfx="wood_high")
L(P((1400, 9750), (2200, 9750)), 13, 13.8, BLACK, 6)
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "vacuum", "存在的空虚", "周日晚上，为什么特别没劲？", ACC, b.shots,
                 [f"{BOOK}第二部分 意义疗法〈存在之虚无〉（转述）",
                  "Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010"],
                 "周日晚上|为什么【特别没劲】", SQUARE_SHOT,
                 ["书中观点为转述：空虚（存在之虚无）主要表现为无聊；“星期天神经症”——一周忙碌结束、闲下来时，"
                  "人发觉自己的生活没有内容；这种空虚常被权力、金钱、享乐等东西填补。见第二部分〈存在之虚无〉。"
                  "出处：Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010。"
                  "上屏均为转述，不是逐字引文。",
                  "自测清单五条为示意，不是量表，不做诊断；“勾了 5 个”“刷了 3 小时”“16:00”为示意，不是数据。",
                  "漏底的桶、往里倒刷剧外卖购物车、桶旁“钱 / 权 / 乐子”的画面为对书中观点的通俗化示意；"
                  "“勾得多，缺一件为谁做的事”为据书中思路（人主要的动力是找到意义）整理的解读。",
                  "阿宁为示意角色；寄东西给爸妈、帮邻居打气、约朋友爬山为现实场景示意，不指向具体个人。",
                  "三步做法（周日为别人做件小事；给下周定一个盼头写进日历；先补桶底再往里放东西）为据书中思路整理的建议。"],
                 tags="#周末 #情绪")
    return b.attach(ep)
