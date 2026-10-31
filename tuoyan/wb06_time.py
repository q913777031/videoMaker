"""06 两种时间（白板手绘版）：明明还有三天，怎么一眨眼没了。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：最后 4 拍不出新笔画）。
叙事（I 两条线）：白板中央一张坐标图，横轴周一到周四，竖着看还剩几天——
打工人开局（周一看着周四的截止日，便利贴写“还有三天”，伸个懒腰 → 撕页日历哗哗翻走三页，一抬头已是周四晚上）→
书中观点（亮书《拖延心理学》，博克和袁；书里说钟表的时间和心里感到的时间对不上；drop 时画出两条线：
蓝色“心里”平着走，黑色“钟表”一路往下“砰”地撞上红色截止线；拖延的人常按心里的时间过，觉得还早、来得及；
钟表时间不等人，三天、两天、一天往下掉）→
估时对照（估两小时、做了五小时的两根柱子，示意）→ 两条线之间空出的一大块就是被拖掉的时间，明天怪兽躺在里面 →
具体做法（记一周流水账 / 做之前写估时、做完写实际 / 按差距多留一截 / 在截止线前面画一条更早的“小截止”）→
蓝线被拉向黑线，空隙变窄，怪兽被挤出去 → 拉远看全板，绿色箭头把几个做法连回坐标图 → 评论区互动。
书中观点为转述（Jane B. Burka & Lenora M. Yuen, Procrastination: Why You Do It, What to Do About It Now, 2008 修订版，
第6章 Time、第13章；中译本《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009，第6章“拖延时钟：你知道现在几点吗”、
第13章“作战方法A：学会怎样判断时间”）；例子与做法为示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, check, circle, clock, desk,
                               face, hands_at, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in, ease_in_out, lerp

from .common import BOOK, episode

ACC = "#2F7FA8"
SQUARE_SHOT = 1                 # 场景 2：日历飞走露出“周四”，小周傻眼，明天怪兽出现

b = Board(size=(4400, 7600))
BG = "#FBFBF9"                  # 白板底色（怪兽、日历页用它填底，盖住下面的线）


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

def badge(x, y, s=1.0) -> skia.Path:
    """配合 stick 的工牌（挂绳 + 卡片）：(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 22 * s, hy + 45 * s), (x + 18 * s, hy + 130 * s), (x + 30 * s, hy + 45 * s)),
                rect(x + 18 * s, hy + 155 * s, 38 * s, 50 * s, 5 * s))


def zhou(x, y, s=0.75, arms="down", mood="flat") -> skia.Path:
    """小周：火柴人 + 胸前工牌。"""
    return join(stick(x, y, s, arms), face(x, y, s, mood), badge(x, y, s))


def monster_paths(x, y, r):
    """明天怪兽：（身体轮廓，整只的线稿）——毛茸茸的一团 + 两只圆眼 + 小手攥着一张日历页。"""
    pts = []
    n = 44
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = r * (1.12 if i % 2 else 1.0)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    body = P(*pts, close=True)
    parts = [body]
    for dx in (-0.33, 0.33):
        parts += [circle(x + dx * r, y - 0.3 * r, 0.2 * r), circle(x + dx * r + 0.04 * r, y - 0.28 * r, 0.07 * r)]
    parts += [P((x - 1.05 * r, y + 0.1 * r), (x - 1.35 * r, y - 0.2 * r)),
              P((x + 1.05 * r, y + 0.1 * r), (x + 1.3 * r, y - 0.05 * r)),
              rect(x + 1.55 * r, y - 0.15 * r, 0.5 * r, 0.6 * r, 6), P((x + 1.3 * r, y - 0.33 * r), (x + 1.8 * r, y - 0.33 * r))]
    return body, join(*parts)


def monster(x, y, r) -> skia.Path:
    return monster_paths(x, y, r)[1]


def belly(x, y, r, k0, k1=None, sfx=None):
    T("明天", x, y + 0.4 * r, 0.48 * r, RED, k0=k0, k1=k1, sfx=sfx)


def heart(x, y, s=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + 0.9 * s)
    p.cubicTo(x - 1.45 * s, y - 0.1 * s, x - 0.8 * s, y - 1.15 * s, x, y - 0.45 * s)
    p.cubicTo(x + 0.8 * s, y - 1.15 * s, x + 1.45 * s, y - 0.1 * s, x, y + 0.9 * s)
    return p


def dashed(x0, y0, x1, y1, dash=36, gap=24) -> skia.Path:
    """虚线：一串短线段（描线时逐段画出）。"""
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy)
    parts, d = [], 0.0
    while d < n:
        e = min(n, d + dash)
        parts.append(P((x0 + dx * d / n, y0 + dy * d / n), (x0 + dx * e / n, y0 + dy * e / n)))
        d = e + gap
    return join(*parts)


def burst(x, y, r0, r1, a_from=-175, a_to=-5, n=7) -> skia.Path:
    """撞击纹：只向上半圈放射的几道短线。"""
    parts = []
    for i in range(n):
        a = math.radians(lerp(a_from, a_to, i / (n - 1)))
        parts.append(P((x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))))
    return join(*parts)


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def note_fn(x, y, w, h):
    """黄便利贴底色。"""

    def fn(c, k, t):
        K.rr(c, x, y, w, h, 8, "#FFE27A", 0.9 * k)
        return None

    return fn


def reveal_text(c, s, x, y, size, color, k):
    """像 b.text 一样从左往右写出（供动态项使用），返回笔尖。"""
    w = K.text_w(s, size, "hand")
    x0 = x - w / 2
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0 - 20, y - size, x0 + w * k + 4, y + size))
    K.text(c, s, x, y, size, "hand", color)
    c.restore()
    return (x0 + w * k, y + size * 0.25 * math.sin(k * 40)) if k < 1 else None


def stroke(c, path, color, width):
    c.drawPath(path, wb.marker(color, width))
    c.drawPath(path, K.paint(color, 0.22, width * 0.45, blur=1.2))


# ---------------------------------------------------------------- 撕页日历（场景 1–2）

CX, CY = 1150, 880               # 日历页中心（页面 300×300，顶上一条装订夹）
PAGE = 300


def calendar() -> skia.Path:
    return join(rect(CX, CY - PAGE / 2 - 15, PAGE + 30, 50, 10), rect(CX, CY, PAGE, PAGE, 10),
                circle(CX - 75, CY - PAGE / 2 - 15, 13), circle(CX + 75, CY - PAGE / 2 - 15, 13))


def flip_fn(days=("周一", "周二", "周三"), last="周四"):
    """日历哗哗翻页：最上面三页依次掀起、甩向左上方飞走，露出底下的“周四”（红字）。"""

    def page(c, s, color, alpha=1.0):
        K.rr(c, 0, PAGE / 2, PAGE - 8, PAGE - 8, 10, BG, alpha)
        c.drawPath(rect(0, PAGE / 2, PAGE, PAGE, 10), wb.marker(BLACK, 10, alpha))
        K.text(c, s, 0, PAGE / 2 - 10, 110, "hand", color, alpha)

    def fn(c, k, t):
        top = CY - PAGE / 2
        c.save()
        c.translate(CX, top)
        page(c, last, RED)
        c.restore()
        for i in reversed(range(len(days))):
            f = clamp01(k * len(days) - i)
            if f >= 1:
                continue
            e = ease_in(f)
            c.save()
            c.translate(CX - 650 * e, top - 420 * e + 160 * math.sin(math.pi * e))
            c.rotate(-55 * e)
            c.scale(1, max(0.2, 1 - 0.7 * math.sin(math.pi * min(1, f * 1.6) / 2)))
            page(c, days[i], BLACK, 1 - clamp01((e - 0.55) / 0.45))
            c.restore()
        return None

    return fn


# ---------------------------------------------------------------- 坐标图（白板中央，场景 4–8、12–13）

OX, OY = 1130, 4300              # 原点；横轴周一到周四，竖着看还剩几天
DAYS = {"周一": 1260, "周二": 1590, "周三": 1920, "周四": 2250}
X0, X1 = DAYS["周一"], DAYS["周四"]
Y0 = 3550                        # 周一还剩三天的高度（每天 250）
S = (X0, Y0)
DL = X1                          # 截止线（周四）
MINI = DAYS["周二"]              # 小截止（周二）
PULL = 450                       # 场景 13：蓝线终点被拉低多少
VC = (1800, 3900, 0.75)          # 看整张图的视角


def black_y(x):
    return Y0 + (x - X0) * (OY - Y0) / (X1 - X0)


J_PULL = None                    # 场景 13 的镜头号（蓝线在它的第 2–4 拍被拉向黑线）


def pull(t):
    if J_PULL is None or b.ep is None:
        return 0.0
    t0, t1 = b.t_of(J_PULL, 2), b.t_of(J_PULL, 4)
    return ease_in_out(clamp01((t - t0) / (t1 - t0)))


def blue_y(x, t):
    return Y0 + (x - X0) / (X1 - X0) * PULL * pull(t)


def blue_fn(c, k, t):
    """心里的时间：从周一平着画到截止线；场景 13 里终点被拉低，贴向黑线。"""
    x = lerp(X0, X1, k)
    stroke(c, P(S, (x, blue_y(x, t))), BLUE, 12)
    return (x, blue_y(x, t)) if k < 1 else None


def drag_fn(c, k, t):
    """场景 13：手按住蓝线终点往下拉（不画东西，只给笔尖位置）。"""
    return (X1, blue_y(X1, t))


def blue_label_fn(c, k, t):
    """“心里”二字跟着蓝线终点走。"""
    return reveal_text(c, "心里", X1 + 120, blue_y(X1, t), 56, BLUE, k)


def hatch_fn(c, k, t):
    """两条线之间的斜纹阴影（被拖掉的时间）：从左往右铺开，蓝线被拉低后自动变窄。"""
    xs = [X0 + 40 + i * 42 for i in range(int((X1 - X0 - 50) / 42))]
    pen = K.paint(ORANGE, 0.55, 5)
    for i, x in enumerate(xs):
        if i >= k * len(xs):
            break
        y0, y1 = blue_y(x, t) + 14, black_y(x) - 14
        if y1 - y0 > 12:
            c.drawLine(x, y0, x + min(30, (y1 - y0) * 0.2), y1, pen)
    return None


MON = (1990, 3700, 108)          # 明天怪兽躺在两条线中间
MON_OUT = (2800, 3600)           # 场景 13 被挤到图外


def mon_pos(t):
    if J_PULL is None or b.ep is None:
        return MON[:2]
    f = ease_in_out(clamp01((t - b.t_of(J_PULL, 3)) / (b.t_of(J_PULL, 4.5) - b.t_of(J_PULL, 3))))
    return lerp(MON[0], MON_OUT[0], f), lerp(MON[1], MON_OUT[1], f) - 160 * math.sin(math.pi * f)


def monster_fn(c, k, t):
    """怪兽（白底盖住阴影）：先描轮廓，再写肚皮上的“明天”；位置随场景 13 被挤出去。"""
    x, y = mon_pos(t)
    r = MON[2]
    body, full = monster_paths(x, y, r)
    c.drawPath(body, K.paint(BG))
    part, tip = wb.partial(full, clamp01(k / 0.6))
    stroke(c, part, BLACK, 9)
    if k > 0.6:
        p = reveal_text(c, "明天", x, y + 0.4 * r, 0.48 * r, RED, clamp01((k - 0.6) / 0.4))
        tip = p or tip
    return tip if k < 1 else None


# ---------------------------------------------------------------- 其他区块

BAR = dict(base=4250, est=(3250, 3930), act=(3750, 3450), w=200)   # 估 / 实际 两根柱子（场景 7、11）
V7 = (3500, 3900, 0.85)
V9 = (1800, 5700, 0.85)          # 流水账
V10 = (3500, 5700, 0.85)         # 估 / 实际 便利贴

# ---------------------------------------------------------------- 开局：还有三天（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

b.shot("还有三天呢", "周一 · 还有三天", (800, 900, 0.85), bars=2)
L(desk(650, 1190, 460), 0, 0.9, sfx="wood_high")
L(zhou(370, 1300, 0.8, "up", "smile"), 1, 1.9, sfx="wood_high")
L(calendar(), 2, 2.9, sfx="wood_low")
T("周一", CX, CY - 10, 110, k0=3, k1=3.8, sfx="pop")
T("周四截止", CX, CY + PAGE / 2 + 70, 56, RED, k0=4, k1=5, sfx="pop")
b.custom(J(), 5, 5.4, note_fn(560, 760, 330, 170))
L(rect(560, 760, 330, 170, 8), 5, 5.5, ORANGE, 7, sfx="wood_high")
T("还有三天", 560, 760, 56, k0=5.2, k1=6)

b.shot("一眨眼周四了", "周四晚上", (1500, 900, 0.85), bars=3)
b.custom(J(), 0, 3, flip_fn(), sfx="shaker")
H(1, "shaker")
H(2, "shaker")
L(join(clock(1850, 600, 100), hands_at(1850, 600, 100, 21, 30)), 3, 3.9, sfx="wood_high")
L(zhou(1750, 1350, 0.75, "shrug", "sad"), 4, 4.9, sfx="wood_high")
L(burst(1750, 1350 - 0.75 * 290, 62, 100, -160, -20, 5), 5, 5.5, RED, 8, sfx="ding")
MON2 = (1330, 1290, 100)
L(monster(*MON2), 6, 6.9, BLACK, 9, sfx="wood_low")
belly(*MON2, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- 书中观点：两种时间（场景 3–8）

b.shot("书里分两种时间", "拖延心理学 · 书中观点", (2700, 2400, 0.8), bars=3)
L(book(2350, 2130, 340, 230), 0, 0.9, sfx="wood_low")
T("《拖延心理学》", 2950, 2100, 64, GREEN, k0=1, k1=2.75, sfx="pop")
T("博克和袁", 2950, 2210, 56, k0=3, k1=4, sfx="pop")
L(join(clock(2350, 2600, 110), hands_at(2350, 2600, 110, 10, 10)), 4, 4.9, sfx="wood_high")
T("钟表", 2350, 2420, 64, k0=5, k1=5.8, sfx="pop")
T("心里", 3050, 2420, 64, BLUE, k0=6, k1=6.8, sfx="pop")
L(heart(3050, 2600, 105), 7, 7.9, RED, 10, sfx="wood_high")

b.shot("一条线早就到底", "书中观点 · 两条线", VC, shake=[0, 6], flashes=[0, (6, 0.3)], bars=3)
L(P((DL, 3420), (DL, OY)), 0, 0.6, RED, 14, sfx="kick")
T("截止", DL, 3370, 60, RED, k0=0.6, k1=1.4)
L(join(arrow((OX, OY), (OX, 3400), 0, 36), arrow((OX, OY), (2520, OY), 0, 36),
       *[P((x, OY - 18), (x, OY + 18)) for x in DAYS.values()]), 1, 1.9, BLACK, 9, sfx="wood_high")
T("周一", DAYS["周一"], 4390, 56, k0=2, k1=2.8, sfx="pop")
T("周四", DAYS["周四"], 4390, 56, RED, k0=2.8, k1=3.6)
b.custom(J(), 3, 3.9, blue_fn, sfx="wood_high")
b.custom(J(), 4, 4.8, blue_label_fn, sfx="pop")
L(P(S, (X1, OY)), 5, 5.9, BLACK, 12, sfx="wood_low")
L(burst(DL, OY, 45, 115), 6, 6.5, RED, 9, sfx="kick")
T("钟表", X1 + 140, 4150, 56, k0=7, k1=7.8, sfx="pop")

b.shot("心里总觉得还早", "书中观点 · 心里的时间", (1760, 3820, 0.8), bars=3)
L(zhou(1245, Y0 - 5, 0.6, "down", "smile"), 0, 0.9, sfx="wood_high")
T("还早", 1450, 3490, 56, BLUE, k0=1, k1=1.8, sfx="pop")
T("来得及", 1720, 3490, 56, BLUE, k0=3, k1=3.75, sfx="pop")
T("zzz", 1340, 3300, 50, BLUE, k0=5, k1=5.8, sfx="pop")
L(oval(1450, 3490, 180, 92), 7, 7.7, RED, 7, sfx="ding")

b.shot("钟表一直在走", "书中观点 · 钟表的时间", VC, bars=3)
for n, (day, lab, dx) in enumerate((("周一", "3天", -60), ("周二", "2天", -80), ("周三", "1天", -80))):
    x = DAYS[day]
    L(circle(x, black_y(x), 14), 2 * n, 2 * n + 0.4, BLACK, 10, sfx="wood_high")
    T(lab, x + dx, black_y(x) + 80, 56, k0=2 * n + 0.4, k1=2 * n + 1.2)
    if n:
        T(day, x, 4390, 56, k0=2 * n + 1, k1=2 * n + 1.8, sfx="pop")
T("嘀嗒", 1700, 4200, 56, RED, k0=6, k1=6.8, sfx="pop")
L(arrow((1420, 3740), (1820, 4040), -0.08, 32), 7, 7.8, RED, 7, sfx="tom")

b.shot("估的总比实际短", "示意 · 估时", V7, bars=3)
ex, ey = BAR["est"]
ax, ay = BAR["act"]
w, base = BAR["w"], BAR["base"]
L(join(P((3050, base), (3950, base)), P((ex - w / 2, base), (ex - w / 2, ey), (ex + w / 2, ey), (ex + w / 2, base))),
  0, 0.9, BLACK, 10, sfx="wood_high")
T("估", ex, base + 80, 64, k0=1, k1=1.8, sfx="pop")
T("2小时", ex, ey - 50, 60, BLUE, k0=2, k1=2.8, sfx="pop")
L(P((ax - w / 2, base), (ax - w / 2, ay), (ax + w / 2, ay), (ax + w / 2, base)), 3, 3.9, BLACK, 10, sfx="wood_low")
T("实际", ax, base + 80, 64, k0=4, k1=4.8, sfx="pop")
T("5小时", ax, ay - 50, 60, RED, k0=5, k1=5.8, sfx="ding")
L(dashed(ex + w / 2, ey, ax - w / 2, ey), 6, 6.6, RED, 7, sfx="wood_high")
T("差3小时", (ex + ax) / 2, 3700, 56, RED, k0=7, k1=7.9, sfx="pop")

b.shot("中间空了一大块", "两条线之间", VC, bars=3)
b.custom(J(), 0, 1.5, hatch_fn, sfx="shaker")
b.custom(J(), 2, 3.6, monster_fn, sfx="wood_low")
H(3, "pop")
T("拖掉的时间", 1720, 3625, 52, RED, k0=5, k1=6.25, sfx="pop")
L(underline(1590, 1850, 3685, 10, 30), 7, 7.8, RED, 7, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 9–13）

b.shot("记一周流水账", "第一步 · 流水账", V9, bars=3)
TX, TY = 1800, 5680
L(join(rect(TX, TY, 760, 620, 16), P((TX - 340, 5520), (TX + 340, 5520))), 0, 0.9, BLACK, 9, sfx="wood_high")
T("时间　在干嘛", TX, 5450, 60, k0=1, k1=2.4, sfx="pop")
ROWS = (("9点　回消息", 5610), ("10点　刷手机", 5750), ("11点　刷手机", 5890))
T(ROWS[0][0], TX, ROWS[0][1], 60, k0=3, k1=4.2, sfx="pop")
T(ROWS[1][0], TX, ROWS[1][1], 60, k0=4.5, k1=5.7)
T(ROWS[2][0], TX, ROWS[2][1], 60, k0=6, k1=7.2, sfx="pop")
_w, _wr = K.text_w(ROWS[1][0], 60, "hand"), K.text_w("刷手机", 60, "hand")
_cx = TX + _w / 2 - _wr / 2
L(join(oval(_cx, ROWS[1][1], _wr + 60, 96), oval(_cx, ROWS[2][1], _wr + 60, 96)), 7, 7.9, RED, 7, sfx="ding")

b.shot("先估，再对一对", "第二步 · 先估再对", V10, bars=3)
NX, NY = 3500, 5640
b.custom(J(), 0, 0.5, note_fn(NX, NY, 700, 540))
L(rect(NX, NY, 700, 540, 10), 0, 0.9, ORANGE, 8, sfx="wood_high")
T("写周报", NX, 5440, 60, k0=1, k1=1.8, sfx="pop")
L(join(P((NX - 300, 5500), (NX + 300, 5500)), P((NX, 5520), (NX, 5870))), 2, 2.6, BLACK, 7, sfx="wood_high")
T("估", NX - 170, 5580, 60, k0=3, k1=3.8, sfx="pop")
T("实际", NX + 170, 5580, 60, k0=3.8, k1=4.6)
T("2小时", NX - 170, 5700, 64, BLUE, k0=5, k1=5.8, sfx="pop")
T("5小时", NX + 170, 5700, 64, RED, k0=6, k1=6.8, sfx="pop")
L(join(arrow((NX - 60, 5810), (NX - 250, 5810), 0, 28), arrow((NX + 60, 5810), (NX + 250, 5810), 0, 28)), 7, 7.8,
  GREEN, 8, sfx="ding")

b.shot("估完再加一截", "第三步 · 多留一截", V7, bars=3)
L(join(dashed(ex - w / 2, ey, ex - w / 2, ay + 10), dashed(ex - w / 2, ay + 10, ex + w / 2, ay + 10),
       dashed(ex + w / 2, ay + 10, ex + w / 2, ey)), 0, 0.9, BLUE, 8, sfx="wood_high")
T("多留一截", ex, ay - 60, 60, BLUE, k0=1, k1=2, sfx="pop")
L(dashed(ex + w / 2 + 20, ay + 10, ax - w / 2 - 20, ay + 10, 24, 18), 2, 2.6, GREEN, 7, sfx="wood_high")
L(zhou(3000, base, 0.7, "point", "smile"), 3, 3.9, sfx="wood_high")
L(check(3000, base - 0.7 * 290 - 110, 40), 5, 5.6, GREEN, 10, sfx="ding")

b.shot("把截止挪到眼前", "第四步 · 小截止", (1760, 3850, 0.8), bars=3)
L(P((MINI, 3420), (MINI, OY)), 0, 0.8, BLUE, 12, sfx="wood_high")
T("小截止", MINI, 3370, 56, BLUE, k0=1, k1=1.8, sfx="pop")
L(arrow((DL - 50, 3425), (MINI + 70, 3425), 0, 30), 2, 2.8, GREEN, 8, sfx="wood_high")
b.custom(J(), 3, 3.4, note_fn(1340, 4110, 300, 190))
L(rect(1340, 4110, 300, 190, 8), 3, 3.8, ORANGE, 7, sfx="wood_high")
T("周二", 1340, 4065, 52, k0=4, k1=4.8, sfx="pop")
T("先交初稿", 1340, 4150, 52, RED, k0=4.8, k1=5.8)
L(check(1530, 4020, 30), 6, 6.5, GREEN, 9, sfx="ding")

b.shot("两条线贴近了", "两条线贴近", VC, bars=3)
J_PULL = J()
L(P((1395, 3495), (1505, 3485)), 0, 0.4, RED, 9, sfx="rim")
L(P((1630, 3495), (1810, 3485)), 1, 1.4, RED, 9, sfx="rim")
b.custom(J(), 2, 4, drag_fn, sfx="wood_low")
H(3, "shaker")
T("空隙小了", 2050, 3640, 56, GREEN, k0=5, k1=6, sfx="pop")
L(check(2240, 3570, 34), 6, 6.6, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (2225, 3300, 0.165)
COMMENT = (1800, 7000, 0.8)
b.shot("你估时差多少", "评论区见", FAR, bars=4)
H(0, "cymbal", 0.5)
L(arrow((2250, 5650), (3080, 5650), -0.1, 120), 1, 1.8, GREEN, 30, sfx="wood_high")
L(arrow((3500, 5290), (3500, 4520), 0, 120), 2, 2.8, GREEN, 30, sfx="wood_high")
L(arrow((2980, 4100), (2580, 4100), 0, 120), 3, 3.8, GREEN, 30, sfx="wood_high")
b.move(J(), 4, COMMENT, dur=1.1)
H(4, "wood_high", 0.6)
T("你估时差多少？", 1800, 6900, 76, RED, k0=6, k1=8, sfx="pop")
T("下一讲：一打开文档，脑子就想跑", 1800, 7050, 54, k0=9, k1=13, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "time", "两种时间", "明明还有三天，怎么一眨眼没了", ACC, b.shots,
                 [f"{BOOK}第6章（中译本“拖延时钟：你知道现在几点吗”，英文版 Time）、第13章（中译本“作战方法A：学会怎样判断时间”），转述",
                  "中译本：《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009；原书 Da Capo Lifelong Books 2008 修订版"],
                 "明明还有三天|怎么一眨眼【没了】", SQUARE_SHOT,
                 ["书中观点为转述：钟表上的时间是客观的，心里感到的时间是主观的；拖延的人常按心里的时间过，"
                  "觉得“还早”“还有时间”，跟钟表对不上（第6章）；办法是观察自己的时间到底花在哪，先估再对照实际用了多久，"
                  "学着更准地判断时间（第13章）。上屏句子均为口语转述，不是逐字引文；“心里 / 钟表”两条线是本讲的示意画法，不是书中图表。",
                  "周一接到周四截止的任务、撕页日历翻到周四晚上、写周报，均为现实场景示意，不指向任何具体公司或个人。",
                  "“估两小时、做了五小时”“差3小时”、流水账里的时间和事项，都是示意，不是书中数据。",
                  "四步做法（记一周流水账；做之前写估时、做完写实际；按自己的差距多留一截；在截止前定一个更早的小截止）"
                  "中，流水账、先估再对为据书中思路整理；“多留一截”“小截止”为示意建议。",
                  "明天怪兽、两条线之间的阴影等为本系列的画面比喻。"],
                 tags="#时间管理 #deadline")
    return b.attach(ep)
