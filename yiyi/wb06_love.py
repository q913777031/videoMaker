"""06 想着一个人（白板手绘版）：撑不住的时候，你会想起谁？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（一个故事贯穿：阿宁难熬的一周，书中故事在转折处点出）：周五末班地铁，被骂了一整周 → 走出地铁口风很冷，
想全都不干了 → 掏出手机，屏保是家里人 → drop：书中故事，寒冷的清晨在雪地里走去干活，作者想起妻子，思维泡泡里的红心亮起，
那一刻明白爱是人能追求的最高目标 → 当时他不知道她是否还活着，书里说这不影响那份爱 →
书中观点：爱一个人，是看见他独特的地方和他能成为的样子 → 回到阿宁：周六爸说院子里柿子熟了、周一同事带了早饭、
周三他教了新人一遍（每屏末尾一颗小红心）→ 拉远回看这一周，三颗红心连到小罗盘 →
做法（想一个具体的人和他会说什么 / 今天跟他说件具体的事 / 把身边人的好说出来）→ 拉远全板 → 评论区。
书中观点为转述（Viktor E. Frankl, Man's Search for Meaning，第一部分 在集中营的经历、第二部分 爱之意义；
中译本《活出生命的意义》，吕娜译，华夏出版社 2010）；阿宁的一周与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, bubble, check, circle, cross, desk,
                               face, join, partial, rect, stick, underline)

from .common import BOOK, episode

ACC = "#C24A5A"
SQUARE_SHOT = 3                 # 场景 4：雪地里一列小人 + 思维泡泡里的红心
GRAY = "#8A8F98"                # 营里的场景用灰色细线
YELLOW = "#D9A21B"

b = Board(size=(3600, 12700))


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


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def compass(x, y, r=60) -> skia.Path:
    """系列视觉角色：小罗盘（圆框 + 顶上小环 + 四个刻度），指针另用 needle_fn 画。"""
    parts = [circle(x, y, r), circle(x, y - r - 14, 12)]
    for a in range(4):
        ang = a * math.pi / 2
        parts.append(P((x + math.cos(ang) * r * 0.72, y + math.sin(ang) * r * 0.72),
                       (x + math.cos(ang) * r * 0.9, y + math.sin(ang) * r * 0.9)))
    return join(*parts)


def needle_fn(x, y, r, aim, turns=2.5):
    """罗盘指针：k<1 时乱转（越转越慢、带抖动），k=1 停在指向 aim=(ax, ay) 的方向，之后一直停着。"""
    final = math.atan2(aim[1] - y, aim[0] - x)

    def fn(c, k, t):
        e = ease_in_out(k)
        a = final + (1 - e) * turns * 2 * math.pi + (0.5 * math.sin(k * 23) * (1 - k) if k < 1 else 0)
        ca, sa = math.cos(a), math.sin(a)
        L_, w = r * 0.78, r * 0.2
        tip, tail = (x + ca * L_, y + sa * L_), (x - ca * L_, y - sa * L_)
        s1, s2 = (x - sa * w, y + ca * w), (x + sa * w, y - ca * w)
        K.poly(c, [tip, s1, s2], RED)
        K.poly(c, [tail, s1, s2], BLACK)
        K.dot(c, x, y, r * 0.1, "#FBFBF9")
        return None

    return fn


def fill_fn(path, color, alpha=0.35):
    """把一块区域淡淡填色（便签底色），随 k 渐显。"""
    def fn(c, k, t):
        c.drawPath(path, K.paint(color, alpha * k))
        return None

    return fn


def heart(x, y, r=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def heart_pop_fn(x, y, r):
    """drop：红心从大到小“砸”进泡泡，实心红 + 描边。"""
    def fn(c, k, t):
        s = 1 + 0.7 * (1 - k) ** 2
        c.save()
        c.translate(x, y)
        c.scale(s, s)
        hp = heart(0, 0, r)
        c.drawPath(hp, K.paint(RED, 0.85 * clamp01(k * 2)))
        c.drawPath(hp, K.paint(RED, 1, 9 / s))
        c.restore()
        return None

    return fn


def glow_fn(x, y, r, color=RED, alpha=0.22):
    """心周围一圈柔光，随 k 渐显。"""
    def fn(c, k, t):
        c.drawCircle(x, y, r * (0.7 + 0.3 * k), K.paint(color, alpha * k, blur=40))
        return None

    return fn


def dots_fn(pts, color, r=20):
    """一组实心小圆点（柿子）逐个出现。pts 为 (x, y) 列表。"""
    def fn(c, k, t):
        n = len(pts)
        for i, (px, py) in enumerate(pts):
            f = clamp01(k * n - i)
            if f > 0:
                K.dot(c, px, py, r * f, color)
                c.drawCircle(px, py, r * f, K.paint(BLACK, 1, 4))
        return None

    return fn


def dashed_fn(path, color, width=8):
    """虚线小人（以后的他）：按 k 描出部分路径，虚线笔触，返回笔尖。"""
    def fn(c, k, t):
        part, tip = partial(path, k)
        pt = K.paint(color, 1, width)
        pt.setPathEffect(skia.DashPathEffect.Make([26, 18], 0))
        c.drawPath(part, pt)
        return tip if k < 1 else None

    return fn


def subway_car(x, y, w=1000, h=400) -> skia.Path:
    """地铁车厢（侧视）：车身 + 一排车窗 + 车轮。(x, y) 为车身中心。"""
    parts = [rect(x, y, w, h, 60), P((x - w / 2 + 30, y + h / 2 - 50), (x + w / 2 - 30, y + h / 2 - 50))]
    for i in range(4):
        parts.append(rect(x - w * 0.33 + i * w * 0.22, y - h / 2 + 80, w * 0.16, 90, 10))
    for dx in (-0.35, -0.25, 0.25, 0.35):
        parts.append(circle(x + dx * w, y + h / 2 + 22, 22))
    return join(*parts)


def subway_exit(x, y) -> skia.Path:
    """地铁口：两根立柱 + 顶棚招牌 + 往下走的台阶。(x, y) 为地面中点。"""
    parts = [P((x - 170, y), (x - 170, y - 330)), P((x + 170, y), (x + 170, y - 330)),
             rect(x, y - 380, 440, 100, 12)]
    for i in range(4):
        yy = y - 40 - i * 55
        parts.append(P((x - 130 + i * 20, yy), (x + 130 - i * 20, yy)))
    return join(*parts)


def wind(x, y, n=3, w=260) -> skia.Path:
    """风线：几道波浪短线，末端卷一下。"""
    parts = []
    for i in range(n):
        yy = y + i * 70
        p = skia.Path()
        p.moveTo(x, yy)
        p.cubicTo(x + w * 0.3, yy - 30, x + w * 0.6, yy + 30, x + w * 0.9, yy)
        p.quadTo(x + w * 1.05, yy - 20, x + w * 0.95, yy - 40)
        parts.append(p)
    return join(*parts)


def phone(x, y, w=70, h=120) -> skia.Path:
    r = 12 if w < 200 else 50
    return join(rect(x, y, w, h, r), P((x - w * 0.17, y + h / 2 - h * 0.07), (x + w * 0.17, y + h / 2 - h * 0.07)))


def waves(x, y, n=2) -> skia.Path:
    """电话声波：朝右的几道弧。"""
    parts = []
    for i in range(n):
        r = 30 + i * 28
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -40, 80)
        parts.append(p)
    return join(*parts)


def sun_half(x, y, r=70) -> skia.Path:
    """地平线上的半个太阳 + 几道短光。(x, y) 为太阳底边中点。"""
    arc = skia.Path()
    arc.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 180, 180)
    parts = [arc]
    for deg in (200, 240, 270, 300, 340):
        a = math.radians(deg)
        parts.append(P((x + math.cos(a) * (r + 18), y + math.sin(a) * (r + 18)),
                       (x + math.cos(a) * (r + 55), y + math.sin(a) * (r + 55))))
    return join(*parts)


def tree(x, y) -> skia.Path:
    """柿子树：树干 + 圆树冠。(x, y) 为树根中点。"""
    return join(P((x - 22, y), (x - 15, y - 170)), P((x + 22, y), (x + 15, y - 170)), circle(x, y - 290, 150),
                P((x, y - 170), (x - 60, y - 240)), P((x, y - 180), (x + 55, y - 250)))


def bun(x, y, s=1.0) -> skia.Path:
    """包子 + 两道热气：(x, y) 为包子底边中点。"""
    body = skia.Path()
    body.moveTo(x - 70 * s, y)
    body.cubicTo(x - 80 * s, y - 70 * s, x + 80 * s, y - 70 * s, x + 70 * s, y)
    body.close()
    parts = [body, P((x - 18 * s, y - 40 * s), (x, y - 56 * s), (x + 18 * s, y - 40 * s))]
    for dx in (-25, 25):
        st = skia.Path()
        st.moveTo(x + dx * s, y - 75 * s)
        st.quadTo(x + (dx - 18) * s, y - 100 * s, x + dx * s, y - 125 * s)
        st.quadTo(x + (dx + 18) * s, y - 150 * s, x + dx * s, y - 170 * s)
        parts.append(st)
    return join(*parts)


def grid(x, y, w=480, h=300, rows=3, cols=3) -> skia.Path:
    """报表：外框 + 表格线。"""
    parts = [rect(x, y, w, h, 8)]
    for i in range(1, rows):
        yy = y - h / 2 + h * i / rows
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
    for i in range(1, cols):
        xx = x - w / 2 + w * i / cols
        parts.append(P((xx, y - h / 2), (xx, y + h / 2)))
    return join(*parts)


# ---------------------------------------------------------------- 周五：末班地铁（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("被骂了一整周", "阿宁的一周 · 周五", (950, 900, 0.85), bars=2)
L(subway_car(950, 900), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(800, 1080, 0.6, "down"), 1, 1.8, BLUE, 9, sfx="wood_high")
L(face(800, 1080, 0.6, "sad"), 1.8, 2.0, BLUE, 8)
L(circle(600, 480, 70), 2, 2.6, BLACK, 8, sfx="pop")
L(P((600, 480), (600, 430), (600, 480), (640, 505)), 2.6, 2.9, BLACK, 7)
T("周五 23:40", 900, 485, 58, RED, k0=3, k1=4.5, sfx="pop")
L(bubble(1000, 930, 150, 90, -1), 5, 5.4, BLACK, 7, sfx="rim")
T("唉", 1000, 930, 54, k0=5.4, k1=6.0)

scene("想全都不干了", "阿宁的一周 · 周五", (2650, 900, 0.85))
L(join(subway_exit(2330, 1250), P((2060, 1250), (3240, 1250))), 0, 0.9, BLACK, 9, sfx="wood_low")
T("地铁", 2330, 870, 56, k0=1, k1=1.8, sfx="pop")
L(stick(2850, 1250, 0.8, "shrug"), 2, 2.8, BLUE, 10, sfx="wood_high")
L(face(2850, 1250, 0.8, "sad"), 2.8, 3.0, BLUE, 9)
L(wind(2980, 820), 4, 4.8, GRAY, 7, sfx="shaker")
T("不干了！", 2700, 600, 84, RED, k0=6, k1=7.0, sfx="kick")

scene("屏保上是家里人", "阿宁的一周 · 周五", (950, 2300, 0.85))
L(phone(950, 2250, 440, 760), 0, 0.9, BLACK, 9, sfx="wood_high")
T("23:55", 950, 1960, 56, k0=1, k1=2.25, sfx="pop")
L(rect(950, 2170, 340, 300, 10), 3, 3.6, BLACK, 7, sfx="pop")
L(join(stick(880, 2300, 0.32), stick(1020, 2300, 0.32, hair=True), stick(950, 2300, 0.22)), 3.6, 4.5, BLACK, 6)
L(heart(950, 2445, 40), 5, 5.6, RED, 8, sfx="ding")
L(stick(1400, 2650, 0.7, "hold"), 6, 6.8, BLUE, 9, sfx="wood_high")
L(face(1400, 2650, 0.7, "flat"), 6.8, 7.0, BLUE, 8)

# drop 前：最后两拍镜头先移到雪地那一屏（不出新笔画），第 0 拍红心砸进泡泡
V4 = (2650, 2300, 0.85)
b.move(J(), 10.0, V4, dur=0.75)

# ---------------------------------------------------------------- 书中故事（场景 4–6）

HEART4 = (2860, 1995, 92)
GROUND = 2650
scene("他想起了妻子", "活出生命的意义 · 书中故事", V4, shake=[0], flashes=[0])
L(rect(HEART4[0], HEART4[1], 520, 330, 160), 0, 0.4, BLACK, 8, sfx="kick")
b.custom(J(), 0, 0.35, heart_pop_fn(*HEART4))
L(underline(2080, 3220, GROUND, amp=10, step=70), 1, 1.9, GRAY, 7, sfx="wood_low")
L(join(*[stick(x, GROUND - 10, 0.45, "down") for x in (2200, 2330, 2460, 2590)]), 2, 2.9, GRAY, 7, sfx="wood_high")
L(sun_half(3120, GROUND, 70), 3, 3.8, GRAY, 7, sfx="pop")
L(join(circle(2500, 2420, 10), circle(2550, 2335, 14), circle(2610, 2250, 18)), 4, 4.6, BLACK, 6, sfx="pop")
T("寒冷的清晨", 2330, 1880, 54, GRAY, k0=5, k1=6.25, sfx="wood_high")
T("爱是最高的追求", 2330, 1990, 60, RED, k0=6, k1=7.75, sfx="ding")

scene("爱还在心里", "活出生命的意义 · 书中故事", (2650, 2450, 0.72))
T("不知她是否还在", 2650, 2800, 56, GRAY, k0=0, k1=1.75, sfx="pop")
L(join(P((3060, 2600), (2700, 2470)), P((3075, 2570), (2780, 2400)), P((3100, 2560), (2900, 2360))), 2, 2.9, ORANGE, 6,
  sfx="wood_high")
b.custom(J(), 3, 3.8, glow_fn(HEART4[0], HEART4[1], 190), sfx="shaker")
T("不影响那份爱", 2650, 2950, 72, RED, k0=5, k1=6.5, sfx="pop")
L(underline(2430, 2870, 3005, amp=8, step=44), 7, 7.8, RED, 8, sfx="ding")

FIG = (2950, 4300)
scene("看见他会成为谁", "活出生命的意义 · 书中观点", (2650, 3950, 0.85))
T("爱 = 看见他", 2650, 3560, 72, RED, k0=0, k1=1.5, sfx="pop")
L(stick(2350, 4300, 0.8, "down"), 2, 2.8, BLACK, 9, sfx="wood_high")
L(face(2350, 4300, 0.8, "smile"), 2.8, 3.0, BLACK, 8)
L(heart(2350, 4140, 26), 3, 3.5, RED, 7, sfx="pop")
T("独特的地方", 2350, 4390, 50, RED, k0=3.6, k1=4.85)
L(arrow((2480, 4150), (2790, 4150), 0.12, 34), 5, 5.8, GREEN, 8, sfx="wood_low")
b.custom(J(), 6, 6.9, dashed_fn(stick(*FIG, 0.92, "up"), BLUE, 8), sfx="wood_high")
T("以后的他", FIG[0], 4390, 50, BLUE, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 回到阿宁的一周（场景 7–10）

NAN7 = (600, 4350)
scene("爸说柿子熟了", "阿宁的一周 · 周六", (950, 3950, 0.85))
L(stick(*NAN7, 0.8, "hold"), 0, 0.8, BLUE, 10, sfx="wood_high")
L(face(*NAN7, 0.8, "smile"), 0.8, 1.0, BLUE, 9)
L(join(phone(705, 4150, 50, 90), waves(745, 4130)), 1, 1.7, BLUE, 7, sfx="pop")
L(bubble(1080, 3700, 560, 150, -1), 2, 2.6, BLACK, 8, sfx="wood_low")
T("院子里柿子熟了", 1080, 3700, 54, k0=3, k1=4.75, sfx="pop")
L(tree(1300, 4350), 5, 5.9, BLACK, 8, sfx="wood_high")
b.custom(J(), 6, 6.6, dots_fn([(1230, 4030), (1345, 4010), (1300, 4110), (1395, 4100), (1205, 4120)], ORANGE),
         sfx="pop")
L(heart(NAN7[0], 3960, 38), 7, 7.6, RED, 8, sfx="ding")

NOTE8 = (1150, 5240, 200, 120)
scene("同事带了早饭", "阿宁的一周 · 周一", (950, 5350, 0.85))
L(desk(950, 5450, 520), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(470, 5760, 0.7, "point"), 1, 1.8, BLACK, 9, sfx="wood_low")
L(face(470, 5760, 0.7, "smile"), 1.8, 2.0, BLACK, 8)
L(bun(790, 5448, 0.9), 2, 2.8, BLACK, 8, sfx="pop")
b.custom(J(), 3, 3.5, fill_fn(rect(*NOTE8, 10), YELLOW))
L(rect(*NOTE8, 10), 3, 3.6, YELLOW, 8, sfx="pop")
T("趁热", NOTE8[0], NOTE8[1], 54, RED, k0=4, k1=4.8, sfx="pop")
L(stick(1420, 5760, 0.7, "down"), 5, 5.8, BLUE, 9, sfx="wood_high")
L(face(1420, 5760, 0.7, "smile"), 5.8, 6.0, BLUE, 8)
L(heart(1420, 5440, 36), 7, 7.6, RED, 8, sfx="ding")

scene("他教了新人一遍", "阿宁的一周 · 周三", (2650, 5350, 0.85))
L(grid(2650, 5150, 480, 300), 0, 0.9, BLACK, 8, sfx="wood_high")
L(stick(3080, 5760, 0.65, "down"), 1, 1.8, BLACK, 9, sfx="pop")
L(face(3080, 5760, 0.65, "flat"), 1.8, 2.0, BLACK, 8)
T("？", 3080, 5430, 80, RED, k0=2, k1=2.8, sfx="rim")
L(stick(2230, 5760, 0.7, "point"), 3, 3.8, BLUE, 9, sfx="wood_high")
L(face(2230, 5760, 0.7, "smile"), 3.8, 4.0, BLUE, 8)
L(join(check(2570, 5050, 26), check(2730, 5150, 26), check(2810, 5250, 26)), 4, 4.8, GREEN, 8, sfx="pop")
b.erase(J(), 5, 5.5, 3080, 5430, 140, 130)
H(5, "shaker")
T("懂了！", 3080, 5430, 60, GREEN, k0=5.6, k1=6.4)
L(heart(2230, 5440, 36), 7, 7.6, RED, 8, sfx="ding")

TL = 6680
HEARTS = [(1350, "爸"), (1750, "同事"), (2150, "新人")]
COMP10 = (1750, 7190, 90)
scene("撑住他的三个人", "阿宁的一周 · 回看", (1800, 6900, 0.7))
L(join(arrow((1130, TL), (2480, TL), 0.0, 40), *[P((1150 + i * 200, TL - 22), (1150 + i * 200, TL + 22))
                                                for i in range(7)]), 0, 0.9, BLACK, 8, sfx="wood_high")
L(compass(*COMP10), 1, 1.7, BLACK, 8, sfx="wood_low")
b.custom(J(), 1.7, 8.0, needle_fn(*COMP10, (1750, TL), turns=4))
ENDS = [(1680, 7125), (1750, 7050), (1820, 7125)]
for n, (x, who) in enumerate(HEARTS):
    k = 2 + 2 * n
    L(join(heart(x, TL, 40), P((x, TL + 45), ENDS[n])), k, k + 0.9, RED, 8, sfx="pop")
    T(who, x, TL - 120, 60, RED, k0=k + 1, k1=k + 1.8)
H(8, "ding")

# ---------------------------------------------------------------- 做法（场景 11–13）

NAN11 = (620, 8800)
COMP11 = (752, 8655, 36)            # 阿宁手里的小罗盘
scene("想一个具体的人", "做法① · 想一个人", (950, 8400, 0.85))
T("① 想一个具体的人", 950, 7960, 66, BLUE, k0=0, k1=2, sfx="pop")
L(stick(*NAN11, 0.75, "hold"), 2, 2.8, BLUE, 9, sfx="wood_high")
L(face(*NAN11, 0.75, "flat"), 2.8, 3.0, BLUE, 8)
L(join(circle(700, 8505, 8), circle(742, 8468, 11), rect(1080, 8300, 600, 280, 120)), 3, 3.8, BLACK, 8,
  sfx="wood_low")
L(stick(900, 8410, 0.45, "down"), 4, 4.8, BLACK, 8, sfx="pop")
T("先吃饭", 1150, 8300, 64, RED, k0=5, k1=5.8, sfx="pop")
L(compass(*COMP11), 6, 6.6, BLACK, 6, sfx="wood_high")
b.custom(J(), 6.6, 7.6, needle_fn(*COMP11, (900, 8300), turns=2))
H(7, "shaker", 0.5)
H(8, "ding")

scene("跟他说件具体事", "做法② · 说件具体事", (2650, 8400, 0.85))
T("② 跟他说件具体事", 2650, 7960, 66, BLUE, k0=0, k1=2, sfx="pop")
L(phone(2650, 8470, 520, 700), 2, 2.9, BLACK, 9, sfx="wood_high")
L(bubble(2560, 8270, 260, 110, -1), 3, 3.4, GRAY, 7, sfx="pop")
T("在吗？", 2560, 8270, 56, GRAY, k0=3.4, k1=4.2)
L(cross(2560, 8270, 60), 5, 5.5, RED, 10, sfx="rim")
L(bubble(2690, 8530, 400, 120, 1), 6, 6.4, BLUE, 8, sfx="wood_low")
T("柿子寄两个来", 2690, 8530, 50, BLUE, k0=6.4, k1=7.9)

scene("把好的说出来", "做法③ · 说出来", (950, 9800, 0.85))
T("③ 说出他的好", 950, 9370, 66, BLUE, k0=0, k1=1.5, sfx="pop")
L(stick(1250, 10200, 0.75, "down"), 2, 2.8, BLACK, 9, sfx="wood_high")
L(face(1250, 10200, 0.75, "smile"), 2.8, 3.0, BLACK, 8)
L(stick(620, 10200, 0.75, "point"), 3, 3.8, BLUE, 9, sfx="pop")
L(face(620, 10200, 0.75, "smile"), 3.8, 4.0, BLUE, 8)
L(bubble(900, 9800, 520, 130, -1), 4, 4.6, BLACK, 8, sfx="wood_low")
T("你那张表做得清楚", 900, 9800, 50, k0=4.6, k1=6.6)
L(heart(1250, 9860, 36), 7, 7.6, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5500, 0.11)
CMT = (1800, 11200, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(bubble(1800, 11080, 1000, 220, -1), 5, 5.8, BLACK, 8)
T("撑不住的时候，你会想起谁？", 1800, 11080, 64, RED, k0=6, k1=9, sfx="pop")
T("下一讲：躲不开的难事，怎么扛过去？", 1800, 11380, 50, k0=9, k1=13.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "love", "想着一个人", "撑不住的时候，你会想起谁？", ACC, b.shots,
                 [f"{BOOK}第一部分 在集中营的经历、第二部分 爱之意义（转述）",
                  "Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010"],
                 "撑不住的时候|你会想起【谁】", SQUARE_SHOT,
                 ["书中观点为转述：寒冷的清晨在雪地里走去干活，作者想起妻子，那一刻明白爱是人能追求的最高目标；当时他不知道"
                  "她是否还活着，书中说这不影响那份爱（第一部分 在集中营的经历）；爱一个人，就是看见他身上独特的东西和他能成为的"
                  "样子（第二部分 爱之意义）。上屏均为转述，不是逐字引文，不编对话。",
                  "雪地、晨光、一列灰线小人与思维泡泡里的红心，“独特的地方 / 以后的他”虚线小人，为对书中故事与观点的通俗化示意；"
                  "营里的画面只画灰线雪地和小人，不画作者和他妻子的脸。",
                  "阿宁难熬的一周（周五末班地铁、地铁口、屏保、爸说柿子熟了、同事带早饭、教新人）均为现实场景示意，"
                  "不指向任何具体公司或个人；阿宁为示意角色；时间为示意，不是数据。",
                  "三步做法（难的时候想一个具体的人和他会说什么；今天跟他说一件具体的事；把身边人的好说出来）"
                  "为据书中思路整理的建议。"],
                 tags="#爱 #家人")
    return b.attach(ep)
