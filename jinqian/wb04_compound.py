"""04 复利靠时间（白板手绘版）：攒钱这件事，为什么拼的是时间？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 I：一条曲线讲完）：整讲只在一张图上画——一片雪落地没化（夏天）→ 一年叠一层 → 叠成冰川（书中故事）→
drop：冰川的轮廓“变成”一条财富曲线，前面贴着地，后面猛地翘起冲出画框 → 亮书 → 书中观点（小变化 × 很长时间）→
书中例子（巴菲特的钱大多来得晚、他从小就开始；西蒙斯回报更高但起步晚，终点矮一截）→
曲线前段平得让人想放弃（小王想砸小猪罐，曲线断了一截）→ 补上缺口：能拿得久比一时冲高强 →
具体做法（先开始，每月一枚硬币；给小猪罐画保护圈，不随便动）→ 拉远全板（雪 → 冰川 → 曲线）→ 评论区。
书中观点为转述（Morgan Housel, The Psychology of Money, Harriman House, 2020；中译本《金钱心理学》，
摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023，第 4 章“复利之谜”）；
小王、小猪罐、每月一枚硬币等为示意 / 据书中思路整理。曲线形状为示意，不是数据；不上屏金额、回报率与具体年龄。
"""

import math

import skia

from adler import kit as K
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               face, hands_at, join, rect, stick, underline)
from engine.gfx import clamp01, ease_in_out, lerp

from .common import BOOK, episode

ACC = "#3A7CA5"                 # 本讲主色：冰川蓝
SQUARE_SHOT = 3                 # 场景 4：冰川变成的曲线翘起 + 小猪罐

b = Board(size=(4600, 5500))

GY = 3000                       # 地面 / 横轴（年龄）
CX0, CX1 = 400, 3700            # 财富曲线横向范围
CA, CH = 5.0, 2900              # 曲线弯曲程度与总高度（终点冲出画框）
IX0, IX1, IH = 400, 2600, 900   # 冰川范围与高度
J_DROP = 3                      # 场景 4：冰川变曲线
GHOST = 0.16                    # 雪层、冰川在曲线出现后留下的淡影


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(len(b.shots) - 1, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def S(text, tag, view, bars=3, **kw):
    """新场景：默认 3 小节。"""
    return b.shot(text, tag, view=view, bars=bars, **kw)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def curve_y(x):
    """财富曲线：前面贴着地，越往后越陡（示意形状）。"""
    u = clamp01((x - CX0) / (CX1 - CX0))
    return GY - CH * (math.exp(CA * u) - 1) / (math.exp(CA) - 1)


def curve_pts(x0=CX0, x1=CX1, n=120):
    return [(x0 + (x1 - x0) * i / n, curve_y(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def ice_y(x, h=IH):
    u = (x - (IX0 + IX1) / 2) / ((IX1 - IX0) / 2)
    return GY - h * max(0.0, 1 - u * u) ** 0.6


def ice_pts(h=IH, n=120):
    return [(IX0 + (IX1 - IX0) * i / n, ice_y(IX0 + (IX1 - IX0) * i / n, h)) for i in range(n + 1)]


def poly(pts) -> skia.Path:
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    return p


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def pig(x, y, s=1.0, mood="smile") -> skia.Path:
    """小猪罐（系列视觉角色）：侧身朝右，(x, y) 为身体中心。mood：smile / sad / sweat / shock。"""
    parts = [oval(x, y, 300 * s, 210 * s),
             oval(x + 150 * s, y + 5 * s, 56 * s, 72 * s), circle(x + 150 * s, y - 8 * s, 5 * s),
             circle(x + 150 * s, y + 18 * s, 5 * s),
             P((x - 105 * s, y - 70 * s), (x - 90 * s, y - 135 * s), (x - 55 * s, y - 92 * s)),
             P((x + 45 * s, y - 95 * s), (x + 75 * s, y - 140 * s), (x + 90 * s, y - 80 * s)),
             P((x - 35 * s, y - 86 * s), (x + 15 * s, y - 86 * s)),
             P((x - 80 * s, y + 92 * s), (x - 80 * s, y + 140 * s)), P((x - 35 * s, y + 103 * s), (x - 35 * s, y + 145 * s)),
             P((x + 35 * s, y + 103 * s), (x + 35 * s, y + 145 * s)), P((x + 85 * s, y + 88 * s), (x + 85 * s, y + 135 * s))]
    tail = skia.Path()
    tail.moveTo(x - 150 * s, y - 5 * s)
    tail.quadTo(x - 195 * s, y - 15 * s, x - 180 * s, y - 45 * s)
    tail.quadTo(x - 165 * s, y - 60 * s, x - 175 * s, y - 25 * s)
    parts.append(tail)
    m = skia.Path()
    if mood == "shock":
        parts.append(circle(x + 80 * s, y - 40 * s, 12 * s))
        m.addCircle(x + 92 * s, y + 42 * s, 14 * s)
    else:
        parts.append(circle(x + 80 * s, y - 40 * s, 6 * s))
        if mood in ("sad", "sweat"):
            m.addArc(skia.Rect.MakeXYWH(x + 72 * s, y + 38 * s, 44 * s, 26 * s), 200, 140)
        else:
            m.addArc(skia.Rect.MakeXYWH(x + 70 * s, y + 20 * s, 48 * s, 32 * s), 20, 140)
    parts.append(m)
    if mood in ("sweat", "shock"):
        d = skia.Path()
        d.moveTo(x + 10 * s, y - 175 * s)
        d.quadTo(x - 18 * s, y - 135 * s, x + 10 * s, y - 128 * s)
        d.quadTo(x + 38 * s, y - 135 * s, x + 10 * s, y - 175 * s)
        parts.append(d)
    return join(*parts)


def flake(x, y, r=34) -> skia.Path:
    parts = []
    for i in range(3):
        a = i * math.pi / 3
        dx, dy = math.cos(a) * r, math.sin(a) * r
        parts.append(P((x - dx, y - dy), (x + dx, y + dy)))
        for sgn in (-1, 1):
            ex, ey = x + sgn * dx * 0.62, y + sgn * dy * 0.62
            for side in (-1, 1):
                b2 = a + side * math.pi / 4 + (math.pi if sgn < 0 else 0)
                parts.append(P((ex, ey), (ex + math.cos(b2) * r * 0.32, ey + math.sin(b2) * r * 0.32)))
    return join(*parts)


def sun(x, y, r=70) -> skia.Path:
    parts = [circle(x, y, r)]
    for i in range(8):
        a = i * math.pi / 4
        parts.append(P((x + math.cos(a) * (r + 22), y + math.sin(a) * (r + 22)),
                       (x + math.cos(a) * (r + 55), y + math.sin(a) * (r + 55))))
    return join(*parts)


def layer(n, x0=620, x1=1100, th=80) -> skia.Path:
    """第 n 层雪（n 从 1 起）：顶面微微起伏，两端竖边。"""
    top = GY - th * n
    pts = [(x0, top + th)] + [(x0 + (x1 - x0) * i / 12, top + 7 * math.sin(i * 1.3 + n)) for i in range(13)] + \
          [(x1, top + th)]
    return poly(pts)


def hammer(x, y, s=1.0) -> skia.Path:
    """锤子：(x, y) 为锤头中心，柄朝左下。"""
    return join(P((x - 55 * s, y - 32 * s), (x + 55 * s, y - 32 * s), (x + 55 * s, y + 32 * s), (x - 55 * s, y + 32 * s),
                  close=True),
                P((x - 10 * s, y + 32 * s), (x - 60 * s, y + 170 * s)), P((x + 10 * s, y + 32 * s), (x - 40 * s, y + 175 * s)))


def plus(x, y, r=30) -> skia.Path:
    return join(P((x - r, y), (x + r, y)), P((x, y - r), (x, y + r)))


def dashed_line(a, c, seg=40, gap=26) -> skia.Path:
    (x0, y0), (x1, y1) = a, c
    n = math.hypot(x1 - x0, y1 - y0)
    parts, d = [], 0.0
    while d < n:
        e = min(n, d + seg)
        parts.append(P((x0 + (x1 - x0) * d / n, y0 + (y1 - y0) * d / n), (x0 + (x1 - x0) * e / n, y0 + (y1 - y0) * e / n)))
        d = e + gap
    return join(*parts)


def dashed_circle(x, y, r, n=22) -> skia.Path:
    p = skia.Path()
    step = 360 / n
    for i in range(n):
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -90 + i * step, step * 0.62)
    return p


def rays(x, y, r=60) -> skia.Path:
    parts = []
    for a in (-150, -115, -90, -65, -30):
        t = math.radians(a)
        parts.append(P((x + math.cos(t) * r, y + math.sin(t) * r), (x + math.cos(t) * r * 1.7, y + math.sin(t) * r * 1.7)))
    return join(*parts)


def strip(x0=3000, x1=3690, depth=250, step=36) -> skia.Path:
    """曲线下方一条绿色斜线带：标出“大部分在这儿”。"""
    parts, x = [], x0
    while x <= x1:
        y = curve_y(x)
        parts.append(P((x, y + 12), (x, y + depth)))
        x += step
    return join(*parts)


def drop_t():
    return b.t_of(J_DROP, 0), b.t_of(J_DROP, 1.5)


def fade_alpha(T, ghost):
    t0, t1 = drop_t()
    return lerp(1.0, ghost, clamp01((T - t0) / max(1e-3, t1 - t0)))


def _stroke(c, path, color, width, alpha):
    if alpha <= 0.01:
        return
    c.drawPath(path, wb.marker(color, width, alpha))
    c.drawPath(path, K.paint(color, 0.22 * alpha, width * 0.45, blur=1.2))


def ghost_fn(path, color, width, ghost=GHOST):
    """描线：曲线出现时（场景 4）淡成 ghost 透明度，留下雪层 / 冰川的影子。"""
    def fn(c, k, T):
        part, tip = wb.partial(path, k)
        _stroke(c, part, color, width, fade_alpha(T, ghost))
        return tip if k < 1 else None
    return fn


def G(path, k0, k1, color=BLUE, width=9, sfx=None, ghost=GHOST):
    b.custom(J(), k0, k1, ghost_fn(path, color, width, ghost), sfx=sfx)


def FT(s, x, y, size, color=BLACK, k0=0.0, k1=None, sfx=None, ghost=0.0):
    """会淡出的白板字（雪、冰川阶段的标注）：写法同 T()，场景 4 起淡到 ghost。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1

    def fn(c, k, T):
        a = fade_alpha(T, ghost)
        w = K.text_w(s, size, "hand")
        x0 = x - w / 2
        if a > 0.01:
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(x0 - 20, y - size, x0 + w * k + 4, y + size))
            K.text(c, s, x, y, size, "hand", color, a)
            c.restore()
        return (x0 + w * k, y + size * 0.25 * math.sin(k * 40)) if k < 1 else None

    b.custom(J(), k0, k1, fn, sfx=sfx)


# ---------------------------------------------------------------- 开局：一片雪（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

FLAKE = (850, 2960)
S("一片雪，没化", "开场 · 一片雪", (950, 2650, 0.85), bars=2)
L(P((300, GY), (1600, GY)), 0, 0.9, BLACK, 10, sfx="wood_low")


def flake_fn(c, k, T):
    e = ease_in_out(k)
    x = FLAKE[0] + 40 * math.sin(k * 7) * (1 - k)
    y = lerp(2230, FLAKE[1], e)
    _stroke(c, flake(x, y), BLUE, 7, fade_alpha(T, GHOST))
    return None


b.custom(J(), 1, 2, flake_fn, sfx="shaker")
H(2, "ding")
G(sun(1300, 2330), 3, 3.9, RED, 8, sfx="wood_high", ghost=0.0)
FT("夏天", 1300, 2510, 56, RED, k0=4, k1=4.8, sfx="pop")
FT("没化", FLAKE[0], 2840, 60, BLUE, k0=5, k1=5.8, sfx="pop")

S("第二年，又没化", "一年又一年", (850, 2750, 0.85))
for n in range(3):
    G(layer(n + 1), 2 * n, 2 * n + 0.9, BLUE, 8, sfx="wood_high")
    FT(f"第{n + 1}年", 480, GY - 40 - 80 * n, 50, k0=2 * n + 1, k1=2 * n + 1.8, sfx="pop")
FT("一层叠一层", 860, 2600, 64, BLUE, k0=6, k1=7.25, sfx="ding")

ICE = poly(ice_pts())
S("后来成了冰川", "书中故事 · 冰川", (1500, 2550, 0.45))


def ice_fn(c, k, T):
    """冰川轮廓：场景 4 第 0 拍起交给 morph_fn 变成曲线。"""
    if T >= drop_t()[0]:
        return None
    part, tip = wb.partial(ICE, k)
    _stroke(c, part, BLUE, 12, 1.0)
    return tip if k < 1 else None


b.custom(J(), 0, 1.2, ice_fn, sfx="wood_low")
G(poly(ice_pts(IH * 0.66)), 2, 2.8, BLUE, 7, sfx="wood_high")
G(poly(ice_pts(IH * 0.33)), 3, 3.8, BLUE, 7, sfx="wood_high")
FT("冰川", 1500, 2560, 110, BLUE, k0=4, k1=4.8, sfx="pop", ghost=0.3)
FT("夏天没化完", 1500, 1800, 96, RED, k0=6, k1=7.25, sfx="pop")

# ---------------------------------------------------------------- drop：冰川变成曲线（场景 4）

S("曲线翘起来了", "一条曲线", (1950, 2000, 0.32), shake=[0], flashes=[0])
_ICE_P, _CUR_P = ice_pts(), curve_pts()


def morph_fn(c, k, T):
    e = ease_in_out(k)
    pts = [(lerp(a[0], q[0], e), lerp(a[1], q[1], e)) for a, q in zip(_ICE_P, _CUR_P)]
    p = poly(pts)
    _stroke(c, p, BLUE, lerp(12, 14, e), 1 - e)
    _stroke(c, p, GREEN, lerp(12, 14, e), e)
    return pts[-1] if k < 1 else None


b.custom(J(), 0, 1.5, morph_fn, sfx="kick")
L(arrow((1600, GY), (4100, GY), 0, 50), 2, 2.8, BLACK, 10, sfx="wood_high")
T("年龄", 3400, 3140, 124, k0=2.8, k1=3.6)
L(arrow((CX0, GY), (CX0, 720), 0, 50), 3, 3.8, BLACK, 10, sfx="wood_high")
T("钱", 560, 650, 124, GREEN, k0=3.8, k1=4.6)
L(pig(1900, 2725, 0.7, "shock"), 5, 5.9, BLACK, 8, sfx="pop")
T("前面贴着地", 1000, 2650, 124, k0=6, k1=7.0, sfx="pop")
T("后面翘上天", 2500, 1500, 124, GREEN, k0=7, k1=7.9, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 5–6）

S("《金钱心理学》讲复利", "金钱心理学 · 第4章", (1100, 1500, 0.85))
L(book(900, 1500, 420, 280), 0, 0.9, sfx="wood_low")
T("金钱心理学", 900, 1250, 72, GREEN, k0=1, k1=2.25, sfx="pop")
T("摩根·豪泽尔", 900, 1720, 50, k0=3, k1=4.5, sfx="pop")
L(pig(1450, 1640, 0.7, "smile"), 5, 5.9, BLACK, 8, sfx="wood_high")
T("第4章 复利之谜", 1420, 1330, 56, BLUE, k0=6, k1=7.75, sfx="pop")

S("小变化，加上很长时间", "书中观点 · 复利", (2200, 3000, 0.6))
L(arrow((1500, 3110), (2900, 3110), 0, 40), 0, 0.9, BLACK, 9, sfx="wood_high")
T("很长时间", 2200, 3200, 70, k0=1, k1=2, sfx="pop")
L(join(*[plus(x, curve_y(x) - 85) for x in (1640, 2250, 2560)]), 2, 2.9, GREEN, 8, sfx="wood_high")
T("小 × 久", 2200, 3380, 110, RED, k0=4, k1=5.25, sfx="pop")
L(underline(1990, 2410, 3460), 6, 6.8, RED, 9, sfx="ding")

# ---------------------------------------------------------------- 书中例子：巴菲特与西蒙斯（场景 7–9）

BUF = (3950, 2950)
S("巴菲特的钱，大多来得晚", "书中例子 · 巴菲特", (3150, 2250, 0.55))
L(stick(*BUF, 0.7, "point"), 0, 0.9, BLACK, 9, sfx="wood_high")
L(face(*BUF, 0.7, "smile"), 0.9, 1.0)
L(rect(BUF[0], 2620, 330, 120, 20), 1, 1.8, BLACK, 8, sfx="wood_high")
T("巴菲特", BUF[0], 2620, 80, k0=1.8, k1=2.6)
L(dashed_line((3000, GY), (3000, curve_y(3000) + 15)), 3, 3.8, RED, 8, sfx="wood_low")
T("晚年", 3000, 3075, 76, RED, k0=4, k1=4.8, sfx="pop")
L(strip(), 5, 5.9, GREEN, 6, sfx="wood_high")
T("大部分在这儿", 2650, 1800, 80, GREEN, k0=6, k1=7.2, sfx="pop")
L(arrow((2900, 1830), (3130, 1900), 0.15, 34), 7.2, 7.9, GREEN, 8)

KID = (520, 2990)
S("他从小就开始了", "书中例子 · 起步早", (950, 2620, 0.85))
L(stick(*KID, 0.45, "up"), 0, 0.9, BLUE, 8, sfx="wood_high")
L(face(*KID, 0.45, "smile"), 0.9, 1.0, BLUE, 6)
T("小时候", KID[0], 2770, 56, BLUE, k0=2, k1=2.8, sfx="pop")
L(join(clock(1400, 2300, 80), hands_at(1400, 2300, 80, 4, 0)), 3, 3.8, BLACK, 8, sfx="wood_high")
T("他的秘诀是时间", 850, 2300, 76, RED, k0=5, k1=6.75, sfx="pop")
L(underline(600, 1110, 2365), 7, 7.8, RED, 8, sfx="ding")

SIM0 = 2500


def sim_y(x):
    u = clamp01((x - SIM0) / (CX1 - SIM0))
    return GY - 1700 * (math.exp(3 * u) - 1) / (math.exp(3) - 1)


S("回报更高，起步晚", "书中例子 · 西蒙斯", (3000, 1550, 0.36))
L(poly([(SIM0 + (CX1 - SIM0) * i / 60, sim_y(SIM0 + (CX1 - SIM0) * i / 60)) for i in range(61)]), 0, 1.0, BLUE, 12,
  sfx="wood_high")
L(stick(4050, 1700, 0.6, "shrug"), 1, 1.9, BLUE, 9, sfx="wood_high")
T("西蒙斯", 4100, 1410, 110, BLUE, k0=2, k1=2.8, sfx="pop")
T("起步晚", 2700, 2720, 110, BLUE, k0=4, k1=4.8, sfx="pop")
L(join(arrow((3830, sim_y(CX1) - 30), (3830, 160), 0, 50), P((3770, sim_y(CX1)), (3890, sim_y(CX1)))), 6, 6.8, RED, 10,
  sfx="rim")
T("矮一截", 4150, 700, 110, RED, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 想放弃（场景 10–11）

WANG = (650, 3650)
PIG10 = (1150, 3560)
GAP = (1500, curve_y(1500))
S("前面平得让人想放弃", "最难熬的一段", (1000, 3150, 0.85))
L(stick(*WANG, 0.7, "shrug"), 0, 0.9, BLACK, 9, sfx="wood_high")
L(face(*WANG, 0.7, "flat"), 0.9, 1.0)
L(bubble(720, 3240, 300, 120, -1), 1, 1.8, BLACK, 8, sfx="pop")
T("好慢啊", 720, 3240, 56, k0=1.8, k1=2.6)
L(pig(*PIG10, 0.75, "sweat"), 3, 3.9, BLACK, 8, sfx="wood_high")
L(hammer(930, 3420, 0.8), 5, 5.8, RED, 9, sfx="pop")
b.erase(J(), 6, 7, GAP[0], GAP[1], 140, 110)
H(6, "rim")

S("能坚持，比一时冲高强", "拿得住", (1000, 3150, 0.85))
L(poly(curve_pts(GAP[0] - 85, GAP[0] + 85, 20)), 0, 0.9, GREEN, 16, sfx="ding")
L(cross(930, 3460, 75), 2, 2.8, RED, 12, sfx="rim")
L(rays(GAP[0], GAP[1] - 10, 55), 3, 3.8, GREEN, 7, sfx="wood_high")
T("冲得高", 1450, 3290, 60, k0=5, k1=5.8, sfx="pop")
L(P((1350, 3292), (1550, 3288)), 6, 6.6, RED, 9, sfx="rim")
T("拿得久", 1450, 3440, 60, GREEN, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 12–13）

PIG = (3100, 3950)
j_coin = S("先开始，金额小也行", "做法一 · 先开始", (3100, 3900, 0.85))
LAND = [3, 5, 7]                # 硬币落进罐子的拍


def pig_fn(c, k, T):
    """小猪罐：先描出来，之后每进一枚硬币胖一圈（落进去时轻轻一弹）。"""
    s = 1.0
    for kk in LAND:
        dt = T - b.t_of(j_coin, kk)
        if dt >= 0:
            s += 0.06 + 0.05 * math.exp(-dt * 9) * math.sin(dt * 30)
    path = pig(0, 0, 1.0, "smile")
    part, tip = wb.partial(path, k)
    c.save()
    c.translate(*PIG)
    c.scale(s, s)
    _stroke(c, part, BLACK, 9 / s, 1.0)
    c.restore()
    return (PIG[0] + tip[0] * s, PIG[1] + tip[1] * s) if tip and k < 1 else None


def coin_fn(c, k, T):
    if k >= 1:
        return None
    y = lerp(3430, PIG[1] - 95, k * k)
    K.dot(c, PIG[0], y, 34, "#F2D46B")
    _stroke(c, join(circle(PIG[0], y, 34), P((PIG[0], y - 18), (PIG[0], y + 18))), GREEN, 7, 1.0)
    return None


b.custom(J(), 0, 1.0, pig_fn, sfx="wood_high")
T("每月一枚", PIG[0], 4260, 64, GREEN, k0=1, k1=2, sfx="pop")
for kk in LAND:
    b.custom(J(), kk - 1, kk, coin_fn, sfx="pop")
    H(kk, "ding")

S("别轻易打断它", "做法二 · 不随便动", (3100, 3950, 0.8))
L(dashed_circle(PIG[0], PIG[1] + 10, 360), 0, 0.9, GREEN, 9, sfx="wood_high")
T("不随便动", PIG[0], 4420, 72, GREEN, k0=2, k1=3, sfx="pop")
L(hammer(2600, 3640, 0.8), 4, 4.8, RED, 9, sfx="wood_high")
L(cross(2580, 3690, 75), 5, 5.8, RED, 12, sfx="rim")
L(check(3560, 3620, 50), 6, 6.8, GREEN, 10, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (2300, 2650, 0.23)
CMT = (2000, 4850, 0.8)
j_end = S("评论区：你几岁开始攒钱？", "评论区见", FAR, bars=4)
H(0, "ding", 0.6)


def run_fn(c, k, T):
    """全板上一颗绿点沿曲线从头跑到尾。"""
    if k >= 1:
        return None
    x = lerp(CX0, CX1, ease_in_out(k))
    y = curve_y(x)
    c.drawCircle(x, y, 90, K.paint(GREEN, 0.25, blur=30))
    K.dot(c, x, y, 55, GREEN)
    return None


b.custom(J(), 1, 3.5, run_fn, sfx="shaker")
b.move(j_end, 4, CMT, 1.1)
H(4, "wood_high", 0.6)
L(pig(2000, 5150, 0.6, "smile"), 5, 5.8, BLACK, 8, sfx="pop")
T("你几岁开始攒钱？", 2000, 4740, 76, RED, k0=6, k1=8, sfx="pop")
T("下一讲：赚到了大钱，为什么又亏光了？", 2000, 4910, 50, k0=9, k1=13.5, sfx="wood_high")
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "compound", "复利靠时间", "攒钱这件事，为什么拼的是时间？", ACC, b.shots,
                 [f"{BOOK}第4章“复利之谜”（转述）",
                  "中译本：摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023"],
                 "攒钱这件事|为什么拼的是【时间】？", SQUARE_SHOT,
                 ["书中观点（转述）：第 4 章“复利之谜”——冰期的形成，靠的是夏天没把冬天的雪化完（冬天并不特别冷），"
                  "一年年叠起来成了冰盖：小变化加上很长时间；巴菲特的大部分财富是很晚才积累起来的，他从小就开始投资，"
                  "他的秘诀很大一部分是时间；另一位回报率更高、但起步晚的投资人（吉姆·西蒙斯）总财富反而少一截；"
                  "能长期坚持、不被打断，比追求一时最高更重要。出处：Morgan Housel, The Psychology of Money "
                  "(Harriman House, 2020)；中译本《金钱心理学》（摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023）"
                  "第 4 章“复利之谜”（转述）。上屏均为转述，不是逐字引文。",
                  "巴菲特、西蒙斯只讲时间长短的道理，不涉及他们投资什么；画面一律为火柴人 + 名字牌，不画肖像。"
                  "原文的具体金额、年龄与回报率未核对，上屏只写“晚年”“起步晚”“矮一截”，不写数字。",
                  "财富曲线、西蒙斯曲线与冰川的形状均为示意，不是数据，不代表任何收益率。",
                  "小王嫌慢想砸小猪罐、“冲得高 / 拿得久”、每月一枚硬币、给小猪罐画保护圈“不随便动”为示意 / "
                  "据书中思路整理的做法，不是投资建议，不涉及任何具体产品或平台。"],
                 tags="#复利 #长期主义")
    return b.attach(ep)
