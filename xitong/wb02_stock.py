"""02 存量与流量（白板手绘版）：工资涨了，为什么还是存不下钱？

叙事：打工人切身问题开局（涨了工资，房租、外卖跟着涨，月底余额还是见底）→ 书中观点（作者画的浴缸：缸里的水是存量，
进水出水是流量；进多出少水涨、出多进少水落、进出一样水位不动；水位只能慢慢变；缸里有水就有缓冲；两头都能调）→
身边的例子（工单积压、节食两天秤不动、家里囤米超市关门不慌、本事每天攒一点）→ 具体做法（记一周花销 / 先关小出水口 /
发薪先转走 / 攒一缸应急金）→ 评论区互动。
书中观点为转述（Meadows, Thinking in Systems, 2008，第一章存量与流量、浴缸、动态平衡、存量的缓冲作用；
中译本《系统之美》，邱昭良译，浙江人民出版社 2012）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, clock, cross, doc, face,
                               join, marker, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#3E7FA8"
SQUARE_SHOT = 16

b = Board(size=(3600, 9000))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = J() if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


# ---------------------------------------------------------------- 小画法

def house(x, y, w=300, h=220):
    """房子：(x, y) 为底边中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 30, y - h), (x, y - h - 150), (x + w / 2 + 30, y - h)),
                P((x - 35, y), (x - 35, y - 110), (x + 35, y - 110), (x + 35, y)), rect(x + 90, y - 140, 60, 60, 4))


def bowl(x, y, w=260):
    """外卖碗：(x, y) 为碗口中点，带热气。"""
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.quadTo(x - w / 2, y + w * 0.55, x, y + w * 0.55)
    p.quadTo(x + w / 2, y + w * 0.55, x + w / 2, y)
    p.close()
    parts = [p, P((x - 50, y + w * 0.55), (x - 60, y + w * 0.65), (x + 60, y + w * 0.65), (x + 50, y + w * 0.55))]
    for dx in (-60, 0, 60):
        s = skia.Path()
        s.moveTo(x + dx, y - 30)
        s.quadTo(x + dx - 25, y - 70, x + dx, y - 110)
        s.quadTo(x + dx + 25, y - 150, x + dx, y - 190)
        parts.append(s)
    return join(*parts)


def phone(x, y, w=380, h=560):
    return join(rect(x, y, w, h, 46), P((x - 40, y - h / 2 + 36), (x + 40, y - h / 2 + 36)), circle(x, y + h / 2 - 50, 20))


def jar(x, y, w=260, h=320):
    """罐子：(x, y) 为罐底中点。"""
    return join(P((x - w / 2 + 20, y - h), (x - w / 2, y - h + 60), (x - w / 2, y), (x + w / 2, y),
                  (x + w / 2, y - h + 60), (x + w / 2 - 20, y - h)),
                P((x - w / 2 + 10, y - h - 20), (x + w / 2 - 10, y - h - 20)))


def bathscale(x, y):
    """体重秤：(x, y) 为秤面中点。"""
    return join(rect(x, y, 360, 300, 50), circle(x, y - 40, 80), P((x, y - 40), (x + 40, y - 95)),
                P((x - 90, y + 110), (x + 90, y + 110)))


def axes(x0, y0, w, h):
    """坐标轴：(x0, y0) 为原点。"""
    return join(P((x0, y0 - h), (x0, y0), (x0 + w, y0)), P((x0 - 20, y0 - h + 30), (x0, y0 - h), (x0 + 20, y0 - h + 30)),
                P((x0 + w - 30, y0 - 20), (x0 + w, y0), (x0 + w - 30, y0 + 20)))


def shop(x, y, w=380):
    """小超市：(x, y) 为底边中点，门口挂牌。"""
    return join(P((x - w / 2, y), (x - w / 2, y - 260), (x + w / 2, y - 260), (x + w / 2, y)),
                P((x - w / 2 - 30, y - 260), (x - w / 2, y - 360), (x + w / 2, y - 360), (x + w / 2 + 30, y - 260)),
                P((x - 70, y), (x - 70, y - 170), (x + 70, y - 170), (x + 70, y)))


def valve(x, y, r=70):
    """阀门手轮。"""
    return join(circle(x, y, r), P((x - r, y), (x + r, y)), P((x, y - r), (x, y + r)), circle(x, y, 14))


def notebook(x, y, w=420, h=440):
    parts = [rect(x, y, w, h, 16)]
    for i in range(6):
        parts.append(circle(x - w / 2 + 40, y - h / 2 + 50 + i * 70, 12))
    return join(*parts)


def bars(x0, y0, hs, w=70, gap=30):
    """柱状图：(x0, y0) 为最左柱底。"""
    return [rect(x0 + i * (w + gap) + w / 2, y0 - h / 2, w, h, 6) for i, h in enumerate(hs)]


def plate(x, y, w, h):
    """白底红框的牌子（盖在卡片交界处，给大字腾地方）。"""

    def fn(c, k, t):
        K.rr(c, x, y, w * (0.6 + 0.4 * k), h * (0.6 + 0.4 * k), 30, "#FBFBF9")
        c.drawPath(rect(x, y, w * (0.6 + 0.4 * k), h * (0.6 + 0.4 * k), 30), marker(RED, 9))
        return None

    return fn


# ---------------------------------------------------------------- 动态浴缸（书中例子）

TX0, TX1, TY0, TY1 = 2080, 2960, 2920, 3380        # 缸口左右、缸口高度、缸底
FX, FY = 2250, 2770                                 # 水龙头出水口
DRAIN = [(2830, 3380), (2830, 3470), (3100, 3470)]  # 下水管
KF = []                                            # (镜头, 拍, 水位 0–1, 进水 0–1, 出水 0–1)


def tub_path():
    p = skia.Path()
    p.moveTo(TX0, TY0)
    p.lineTo(TX0 + 50, TY1 - 90)
    p.quadTo(TX0 + 70, TY1, TX0 + 180, TY1)
    p.lineTo(TX1 - 180, TY1)
    p.quadTo(TX1 - 70, TY1, TX1 - 50, TY1 - 90)
    p.lineTo(TX1, TY0)
    return p


def tub_inner():
    p = tub_path()
    p.close()
    return p


def tub_outline():
    return join(tub_path(), P((TX0 - 40, TY0), (TX1 + 40, TY0)), P((TX0 + 160, TY1), (TX0 + 130, TY1 + 70)),
                P((TX1 - 160, TY1), (TX1 - 130, TY1 + 70)))


def faucet():
    return join(P((2010, 2680), (FX + 20, 2680), (FX + 20, FY - 10)), P((FX - 20, 2680), (FX - 20, FY - 10)),
                P((FX - 30, FY - 10), (FX + 30, FY - 10)), P((2120, 2680), (2120, 2620)), P((2080, 2620), (2160, 2620)))


def drain_pipe():
    return P(*DRAIN)


def tub_state(t):
    pts = [(b.t_of(j, k), lv, i, o) for j, k, lv, i, o in KF]
    if t <= pts[0][0]:
        return pts[0][1:]
    for (t0, *a), (t1, *c) in zip(pts, pts[1:]):
        if t <= t1:
            f = clamp01((t - t0) / max(1e-3, t1 - t0))
            return tuple(x + (y - x) * f for x, y in zip(a, c))
    return pts[-1][1:]


def water_fn(c, k, t):
    lv, inn, out = tub_state(t)
    ly = TY1 - 5 - lv * (TY1 - TY0 - 20)
    # 进水：水柱 + 下落的水滴
    if inn > 0.02:
        c.drawPath(P((FX, FY), (FX, ly)), marker(BLUE, 6 + 26 * inn, 0.55))
        for n in range(4):
            yy = FY + ((t * 700 + n * 120) % max(1, ly - FY))
            c.drawCircle(FX + 30 * math.sin(n * 2.1), yy, 6 + 8 * inn, K.paint(BLUE, 0.7))
        for d in (-1, 1):
            c.drawPath(P((FX + d * 30, ly - 10), (FX + d * (70 + 40 * inn), ly - 40 - 30 * inn * abs(math.sin(t * 9)))),
                       marker(BLUE, 5, 0.6))
    # 缸里的水
    c.save()
    c.clipPath(tub_inner(), skia.ClipOp.kIntersect, True)
    c.drawRect(skia.Rect.MakeLTRB(TX0 - 50, ly, TX1 + 50, TY1 + 20), K.paint(BLUE, 0.22))
    wave = skia.Path()
    amp = 6 + 10 * inn
    wave.moveTo(TX0 - 40, ly)
    for i in range(1, 46):
        x = TX0 - 40 + i * 22
        wave.lineTo(x, ly + amp * math.sin(i * 0.7 + t * 7))
    c.drawPath(wave, marker(BLUE, 7, 0.9))
    c.restore()
    # 出水：沿下水管流动的水珠 + 管口水流
    if out > 0.02:
        seg = [DRAIN[0], DRAIN[1], DRAIN[2]]
        total = 90 + 270
        for n in range(int(3 + 5 * out)):
            s = (t * 420 + n * total / (3 + 5 * out)) % total
            if s < 90:
                x, y = DRAIN[0][0], DRAIN[0][1] + s
            else:
                x, y = DRAIN[1][0] + (s - 90), DRAIN[1][1]
            c.drawCircle(x, y, 9 + 6 * out, K.paint(BLUE, 0.8))
        x2, y2 = seg[2]
        c.drawPath(P((x2 + 10, y2), (x2 + 30, y2 + 30), (x2 + 30, y2 + 40 + 90 * out)), marker(BLUE, 6 + 18 * out, 0.6))
    return None


# ---------------------------------------------------------------- 开局：涨了工资，余额照样见底（镜头 1–6）

b.shot("这个月涨工资了", "灵魂拷问", view=(1000, 820, 0.8))
L(stick(650, 1150, 0.95, "up"), 0, 0.8, sfx="wood_high")
L(face(650, 1150, 0.95, "smile"), 0.8, 1.0)
L(phone(1250, 800), 1, 1.8, sfx="wood_high")
T("工资", 1250, 690, 60, k0=2.0, sfx="pop")
T("+2000", 1250, 820, 90, GREEN, k0=2.5, k1=3.2)
b.hit(J(), 3, "ding")

b.shot("到月底又光了", "灵魂拷问", view=(2600, 820, 0.8))
L(stick(3000, 1150, 0.9, "shrug"), 0, 0.6, sfx="wood_high")
L(face(3000, 1150, 0.9, "sad"), 0.6, 0.8)
L(phone(2500, 800), 1, 1.8, sfx="wood_high")
T("月底余额", 2500, 690, 60, k0=2.0, sfx="pop")
T("¥326", 2500, 830, 100, RED, k0=3.0, k1=3.5, sfx="rim")

b.shot("房子换贵的了", "灵魂拷问", view=(1000, 1600, 0.8))
L(house(800, 1850), 0, 0.9, sfx="wood_high")
T("房租", 1300, 1560, 66, k0=1.0, sfx="pop")
T("+800", 1300, 1690, 90, RED, k0=2.0, k1=2.6, sfx="rim")

b.shot("外卖也换贵的", "灵魂拷问", view=(2600, 1600, 0.8))
L(bowl(2250, 1560), 0, 0.9, sfx="wood_high")
T("外卖", 2850, 1500, 66, k0=1.0, sfx="pop")
T("+300", 2850, 1630, 90, RED, k0=1.6, k1=2.0)
T("会员 打车 奶茶", 2700, 1850, 56, k0=2.0, k1=2.8, sfx="pop")

b.shot("存款还是那点", "灵魂拷问", view=(1800, 2150, 0.8))
T("收入", 1450, 2040, 76, GREEN, k0=0, sfx="pop")
L(arrow((1580, 2080), (1580, 1960), 0, 34), 0.5, 0.8, GREEN, 9)
T("开销", 2150, 2040, 76, RED, k0=1.0, sfx="pop")
L(arrow((2280, 2080), (2280, 1960), 0, 34), 1.5, 1.8, RED, 9)
T("存款：没动", 1800, 2230, 84, k0=2.0, k1=2.8, sfx="rim")
L(underline(1580, 2020, 2300), 3, 3.4, BLACK, 7, sfx="wood_low")

b.shot("钱到底去哪了？", "灵魂拷问", view=(1800, 1300, 0.36), flashes=[0])
T("？", 1850, 950, 400, RED, k0=0, k1=0.6, sfx="kick")
T("钱去哪了", 1850, 1270, 100, k0=1.0, k1=1.8, sfx="pop")
b.hit(J(), 2, "ding")

# ---------------------------------------------------------------- 书中观点：浴缸（镜头 7–17）

b.shot("有本书讲过这个", "系统之美", view=(1050, 3000, 0.9))
L(book(750, 3000, 420, 280), 0, 1.0, sfx="wood_low")
T("系统之美", 750, 2760, 80, GREEN, k0=1.0, sfx="pop")
T("德内拉 · 梅多斯", 750, 3230, 50, k0=2.0, sfx="pop")
L(arrow((1050, 3000), (1350, 3000), -0.15, 40), 3, 3.5, GREEN, 8)

b.shot("作者画了个浴缸", "书中例子 · 浴缸", view=(2620, 3100, 0.78))
L(tub_outline(), 0, 1.4, BLACK, 10, sfx="wood_low")
L(faucet(), 2, 2.8, BLACK, 9, sfx="wood_high")
L(drain_pipe(), 3, 3.5, BLACK, 12, sfx="wood_high")

j_drop = b.shot("水龙头一开", "书中例子 · 浴缸", view=(2620, 3100, 0.78), shake=[0], flashes=[0])
b.custom(j_drop, 0, 200, water_fn, sfx="kick", gain=1.0)
KF += [(j_drop, 0, 0.0, 0.0, 0.0), (j_drop, 0.05, 0.0, 1.0, 0.0), (j_drop, 4, 0.35, 1.0, 0.0)]
T("哗！", 2640, 2790, 90, BLUE, k0=1.0, k1=1.3, sfx="tom")
b.hit(j_drop, 2, "shaker", 0.7, "进水")
b.hit(j_drop, 3, "pop")

j = b.shot("缸里的水是存量", "书中观点 · 存量", view=(2620, 3100, 0.78))
KF += [(j, 4, 0.45, 1.0, 0.0)]
T("存量", 2520, 3290, 76, k0=0, sfx="pop")
L(underline(2420, 2620, 3345), 2, 2.4, BLACK, 7, sfx="ding")

j = b.shot("进出的水是流量", "书中观点 · 流量", view=(2620, 3100, 0.78))
KF += [(j, 0, 0.45, 1.0, 0.0), (j, 0.4, 0.46, 1.0, 0.5), (j, 4, 0.5, 1.0, 0.5)]
b.hit(j, 0, "pop", 0.8, "拔塞子")
T("流入", 2420, 2610, 66, BLUE, k0=1.0, sfx="pop")
T("流出", 2960, 3600, 66, BLUE, k0=2.0, sfx="pop")

RZ = (3150, 3000, 400, 700)                         # 浴缸右侧注释区（每镜擦掉重写）
j = b.shot("进多出少，水涨", "书中观点 · 流量", view=(2620, 3100, 0.78))
KF += [(j, 0, 0.5, 1.0, 0.4), (j, 4, 0.75, 1.0, 0.4)]
T("进>出", 3150, 2780, 70, k0=0, sfx="pop")
L(arrow((3150, 3200), (3150, 2900), 0, 50), 1, 1.6, GREEN, 12, sfx="wood_high")
b.hit(j, 3, "ding")

j = b.shot("出多进少，水落", "书中观点 · 流量", view=(2620, 3100, 0.78))
b.erase(j, 0, 0.4, *RZ)
KF += [(j, 0, 0.75, 0.3, 1.0), (j, 4, 0.42, 0.3, 1.0)]
T("出>进", 3150, 2780, 70, k0=1.0, sfx="pop")
L(arrow((3150, 2900), (3150, 3200), 0, 50), 2, 2.6, RED, 12, sfx="rim")

j = b.shot("进出一样，水不动", "书中观点 · 动态平衡", view=(2620, 3100, 0.78))
b.erase(j, 0, 0.4, *RZ)
KF += [(j, 0, 0.42, 0.6, 0.6), (j, 4, 0.42, 0.6, 0.6)]
T("进=出", 3150, 2780, 70, k0=1.0, sfx="pop")
T("动态", 3150, 2960, 76, RED, k0=2.0, sfx="pop")
T("平衡", 3150, 3070, 76, RED, k0=2.4, k1=2.8)
b.hit(j, 3, "ding")

j = b.shot("水位只能慢慢变", "书中观点 · 需要时间", view=(2620, 3100, 0.78))
b.erase(j, 0, 0.4, *RZ)
KF += [(j, 0, 0.42, 1.0, 0.6), (j, 4, 0.48, 1.0, 0.6)]
L(clock(3150, 2860, 110), 1, 1.6, BLACK, 9, sfx="wood_high")
L(P((3150, 2860), (3150, 2780)), 1.6, 1.8, RED, 9)
L(P((3150, 2860), (3210, 2880)), 1.8, 1.95, RED, 9)
T("要时间", 3150, 3070, 70, k0=2.0, sfx="pop")

j = b.shot("缸里有水，就有缓冲", "书中观点 · 缓冲", view=(2620, 3100, 0.78))
b.erase(j, 0, 0.4, *RZ)
KF += [(j, 0, 0.48, 1.0, 0.6), (j, 0.3, 0.48, 0.0, 0.6), (j, 4, 0.4, 0.0, 0.6)]
b.hit(j, 0, "rim", 0.8, "关水")
T("停水", 3150, 2780, 70, RED, k0=1.0, sfx="pop")
T("照样流", 3150, 2900, 66, k0=1.5, k1=2.0)
T("缓冲", 3150, 3070, 90, BLUE, k0=2.0, sfx="ding")

j = b.shot("两头都能调", "书中观点 · 两个口", view=(2620, 3100, 0.78))
b.erase(j, 0, 0.4, *RZ)
KF += [(j, 0, 0.4, 0.5, 0.6), (j, 0.5, 0.4, 1.0, 0.25), (j, 4, 0.6, 1.0, 0.25)]
T("开大", 3150, 2800, 76, GREEN, k0=1.0, sfx="pop")
T("进水", 3150, 2900, 76, GREEN, k0=1.3, k1=1.7)
T("关小", 3150, 3060, 76, RED, k0=2.0, sfx="pop")
T("出水", 3150, 3160, 76, RED, k0=2.3, k1=2.7)
b.hit(j, 3, "ding")
KF += [(j + 1, 4, 0.62, 0.6, 0.6)]                 # 之后保持动态平衡

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 4600), (2650, 4600), (950, 5600), (2650, 5600)]
b.shot("身边全是浴缸", "身边的例子", view=(1800, 5050, 0.32))
T("身边的例子", 1800, 4020, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("工单天天进来", "例子 · 工单", view=(950, 4600, 0.85))
T("每天进 20 单", 620, 4250, 56, GREEN, k0=0, sfx="pop")
L(arrow((420, 4340), (720, 4560), 0.15, 40), 1, 1.5, GREEN, 9, sfx="wood_high")
for n in range(3):
    L(doc(950 + n * 12, 4800 - n * 70, 220, 160, 3), 2 + n * 0.3, 2.3 + n * 0.3, BLACK, 8, sfx="pop" if n == 0 else None)

b.shot("积压越堆越高", "例子 · 工单", view=(950, 4600, 0.85))
T("只做完 15 单", 1290, 4250, 56, RED, k0=0, sfx="pop")
L(arrow((1150, 4560), (1450, 4340), 0.15, 40), 0.5, 0.9, RED, 9)
for n in range(3, 6):
    L(doc(950 + n * 12, 4800 - n * 70, 220, 160, 3), 1 + (n - 3) * 0.3, 1.3 + (n - 3) * 0.3, BLACK, 8,
      sfx="wood_high" if n == 3 else None)
T("积压", 1300, 4720, 76, RED, k0=2.0, sfx="rim")

b.shot("体重也是一缸水", "例子 · 体重", view=(2650, 4600, 0.85))
L(bathscale(2650, 4720), 0, 0.9, BLACK, 9, sfx="wood_high")
T("吃进去", 2250, 4330, 60, GREEN, k0=1.0, sfx="pop")
L(arrow((2250, 4390), (2470, 4560), 0.15, 36), 1.4, 1.8, GREEN, 8)
T("消耗掉", 3050, 4330, 60, RED, k0=2.0, sfx="pop")
L(arrow((2830, 4560), (3050, 4390), 0.15, 36), 2.4, 2.8, RED, 8)

b.shot("节食两天秤不动", "例子 · 体重", view=(2650, 4600, 0.85))
b.erase(J(), 0, 0.5, 2650, 4600, 1400, 800)
L(axes(2200, 4900, 900, 500), 1, 1.6, BLACK, 7, sfx="wood_high")
L(P((2200, 4560), (2450, 4565), (2700, 4575), (2950, 4590), (3080, 4600)), 2, 2.8, BLUE, 9, sfx="pop")
T("体重", 2350, 4380, 56, k0=1.6, k1=1.9)
T("第 2 天", 2450, 4960, 50, k0=3.0, sfx="pop")
T("几乎没变", 2850, 4480, 60, RED, k0=3.2, k1=3.8)

b.shot("家里囤着米和面", "例子 · 家里的米缸", view=(950, 5600, 0.85))
L(jar(700, 5900, 260, 340), 0, 0.8, BLACK, 9, sfx="wood_high")
T("米", 700, 5760, 90, k0=1.0, k1=1.3, sfx="pop")
L(jar(1000, 5900, 220, 280), 1.4, 1.9, BLACK, 9)
T("面", 1000, 5790, 80, k0=2.0, k1=2.3, sfx="pop")
L(P((520, 5905), (1180, 5905)), 2.5, 2.8, BLACK, 7)

b.shot("超市关门也不慌", "例子 · 家里的米缸", view=(950, 5600, 0.85))
L(shop(1300, 5600, 300), 0, 0.8, BLACK, 9, sfx="wood_high")
T("休息", 1300, 5180, 56, k0=0.8, k1=1.1)
L(cross(1300, 5420, 70), 1, 1.3, RED, 11, sfx="rim")
L(stick(400, 5900, 0.6, "down"), 2, 2.5, BLUE, 9, sfx="pop")
L(face(400, 5900, 0.6, "smile"), 2.5, 2.7, BLUE, 6)
b.hit(J(), 3, "ding")

b.shot("本事也是存量", "例子 · 本事", view=(2650, 5600, 0.85))
L(book(2350, 5560, 300, 200), 0, 0.8, BLACK, 9, sfx="wood_high")
T("本事", 2350, 5800, 70, k0=1.0, sfx="pop")
L(axes(2650, 5900, 600, 520), 2, 2.5, BLACK, 7, sfx="wood_high")

b.shot("每天学一点", "例子 · 本事", view=(2650, 5600, 0.85))
for n, p in enumerate(bars(2700, 5895, (60, 110, 170, 240, 320))):
    L(p, n * 0.5, n * 0.5 + 0.35, BLUE, 8, sfx="pop" if n % 2 == 0 else None)
T("每天 20 分钟", 3000, 5300, 54, GREEN, k0=3.0, k1=3.6)

b.shot("四个都是浴缸", "身边的例子", view=(1800, 5100, 0.32))
T("都有进，有出，有水位", 1800, 6200, 130, k0=0, k1=1.6, sfx="pop")
b.hit(J(), 2, "wood_low")
L(underline(1000, 2600, 6290), 2, 2.6, RED, 10)

b.shot("水位跟着进出走", "身边的例子", view=(1800, 5100, 0.32), shake=[0])
b.custom(J(), 0, 0.3, plate(1800, 5100, 640, 260), sfx="kick")
T("进 − 出", 1800, 5100, 140, RED, k0=0.2, k1=0.7)
for n, (x, y) in enumerate(CARDS):
    L(arrow((1800 + (x - 1800) * 0.15, 5100 + (y - 5100) * 0.25), (1800 + (x - 1800) * 0.55, 5100 + (y - 5100) * 0.55),
            0.1, 40), 1 + n * 0.5, 1.4 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 7100), (2650, 7100), (950, 8000), (2650, 8000)]
b.shot("存不下钱这样做", "具体做法", view=(1800, 7450, 0.32))
T("存不下钱，这样做", 1800, 6560, 110, k0=0, k1=1.6, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1500, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先记一周花销", "第一步 · 记流出", view=(950, 7100, 0.85))
T("① 记一周花销", 950, 6800, 76, BLUE, k0=0, sfx="pop")
L(notebook(700, 7180, 400, 460), 1, 1.6, BLACK, 8, sfx="wood_high")
for n, w in enumerate(("房租", "吃饭", "打车", "会员")):
    T(w, 740, 7030 + n * 100, 56, k0=2.0 + n * 0.4, k1=2.3 + n * 0.4, sfx="pop" if n == 0 else None)

b.shot("小钱漏得最多", "第一步 · 记流出", view=(950, 7150, 0.85))
L(rect(740, 7330, 200, 90, 45), 0, 0.5, RED, 8, sfx="rim")
T("会员 ×5", 1220, 7060, 60, k0=1.0, sfx="pop")
T("奶茶 ×12", 1220, 7180, 60, k0=1.5, k1=2.0)
T("一月 ¥600", 1220, 7330, 66, RED, k0=2.0, sfx="ding")

b.shot("先关小出水口", "第二步 · 关小出水", view=(2650, 7100, 0.85))
T("② 先关小出水", 2650, 6800, 76, BLUE, k0=0, sfx="pop")
L(valve(2300, 7100), 1, 1.6, BLACK, 9, sfx="wood_high")
T("退掉不用的会员", 2850, 7100, 56, k0=2.0, sfx="pop")

b.shot("外卖换成带饭", "第二步 · 关小出水", view=(2650, 7150, 0.85))
T("外卖", 2450, 7300, 66, k0=0, sfx="pop")
L(P((2370, 7300), (2530, 7300)), 1, 1.3, RED, 10, sfx="rim")
T("带饭 一周 3 天", 2900, 7300, 60, RED, k0=2.0, k1=2.9, sfx="pop")
L(check(3200, 7300, 40), 3, 3.3, GREEN, 9, sfx="ding")

b.shot("工资一到先转走", "第三步 · 先转走", view=(950, 8000, 0.85))
T("③ 发薪先转走", 950, 7700, 76, BLUE, k0=0, sfx="pop")
T("工资", 600, 7950, 76, GREEN, k0=1.0, sfx="pop")
L(arrow((700, 7950), (1060, 7950), -0.1, 40), 1.5, 1.9, GREEN, 9)
L(jar(1250, 8100, 220, 260), 2, 2.6, BLACK, 9, sfx="wood_high")
T("存款", 1250, 8000, 54, k0=2.6, k1=3.0)

b.shot("剩下的再花", "第三步 · 先转走", view=(950, 8000, 0.85))
T("剩下的才花", 700, 8240, 70, k0=0, sfx="pop")
L(underline(520, 880, 8300), 2, 2.4, RED, 8, sfx="ding")

b.shot("涨的那份也先存", "第三步 · 先转走", view=(950, 8000, 0.85))
b.erase(J(), 0, 0.5, 950, 8060, 1400, 600)
T("涨的 +2000", 650, 8050, 76, GREEN, k0=1.0, sfx="pop")
L(arrow((900, 8000), (1080, 7920), -0.1, 34), 1.8, 2.1, BLACK, 8)
L(arrow((900, 8100), (1080, 8180), 0.1, 34), 1.9, 2.2, BLACK, 8)
T("存 1000", 1270, 7920, 70, RED, k0=2.0, sfx="pop")
T("花 1000", 1270, 8180, 70, k0=3.0, sfx="pop")

b.shot("攒一缸应急金", "第四步 · 攒缓冲", view=(2650, 8000, 0.85))
T("④ 攒一缸缓冲", 2650, 7700, 76, BLUE, k0=0, sfx="pop")
L(jar(2300, 8250, 300, 400), 1, 1.6, BLACK, 9, sfx="wood_high")
for n in range(3):
    L(P((2170, 8200 - n * 100), (2430, 8200 - n * 100)), 2 + n * 0.3, 2.25 + n * 0.3, BLUE, 8,
      sfx="pop" if n == 0 else None)
T("够花 3 个月", 2300, 8320, 50, k0=3.0, k1=3.5)

b.shot("出事也不慌", "第四步 · 攒缓冲", view=(2650, 8000, 0.85))
for n, w in enumerate(("生病", "换工作", "修车")):
    T(w, 2850, 7900 + n * 110, 60, k0=n * 1.0, sfx="pop")
    L(check(3100, 7895 + n * 110, 36), n + 0.5, n + 0.75, GREEN, 8)
b.hit(J(), 3, "ding")

b.shot("别急，水位慢慢涨", "第四步 · 攒缓冲", view=(2650, 8000, 0.85))
b.erase(J(), 0, 0.5, 2650, 8070, 1400, 600)
L(axes(2150, 8300, 1000, 440), 1, 1.6, BLACK, 7, sfx="wood_high")
L(P((2150, 8280), (2400, 8240), (2650, 8170), (2900, 8070), (3100, 7950)), 2, 2.8, BLUE, 10, sfx="pop")
T("存款", 2280, 7860, 56, k0=1.6, k1=1.9)
T("一年", 3080, 8350, 54, k0=3.0, k1=3.3, sfx="pop")
T("别急", 2650, 7980, 70, RED, k0=3.3, k1=3.7)

b.shot("就这四件事", "具体做法", view=(1800, 7450, 0.32))
for n, (x, y) in enumerate(SOL):
    L(check(x + 560, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 == 0 else "pop")

b.shot("管好两个口", "一句话", view=(1800, 4500, 0.235))
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 8740, 0.8))
T("你最大的出水口是啥？", 1800, 8650, 76, RED, k0=0.5, k1=1.8)
T("下一讲：减肥为什么总会反弹？", 1800, 8800, 50, k0=2.0, k1=3.2)
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 1, "pop")
b.hit(J(), 2, "wood_high", 0.7)
b.hit(J(), 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "stock", "存量与流量", "工资涨了，为什么还是存不下钱？", ACC, b.shots,
                 [f"{BOOK}第一章：存量与流量、浴缸、动态平衡、存量的缓冲作用（转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                 "工资涨了|钱从【出水口】溜了", 16,
                 ["书中观点均为转述，不是原文引文：存量是系统里能看见、能计量的积累，流量是让存量随时间变化的流入与流出；"
                  "浴缸是书中例子：进水多于出水水位上升，出水多于进水水位下降，进出相等水位不变（动态平衡）；想提高水位既可加大流入，"
                  "也可减少流出；存量的变化需要时间，存量起缓冲作用，让流入流出可以暂时不一致。出处：Donella H. Meadows, "
                  "Thinking in Systems: A Primer (2008)，中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                  "涨薪、房租、外卖、余额，以及工单积压、节食与体重、家里囤米、每天学习等均为现实场景示意，画面数字与曲线不代表"
                  "真实数据，不指向任何具体公司或个人；四步存钱做法为据书中思路整理的建议。"],
                 tags="#存钱 #理财")
    return b.attach(ep)
