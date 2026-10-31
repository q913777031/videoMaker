"""09 留出余地（白板手绘版）：计划总被打乱，钱怎么留余地？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（形式 J：一个比喻贯穿——“跟车距离”，整讲都在马路上展开）：
前车一脚急刹 → 后车跟太紧追尾 → 小王的钱也贴太紧（账本车：房租 + 还款 + 花销 = 工资，剩 0）→
drop：前车挂着“裁员 / 生病 / 搬家”急刹，账本被撞散 →
书中观点（亮书；第 13 章：计划里最要紧的一条，是算上计划会出岔子；格雷厄姆的“安全边际”画成两车之间一段绿色空白；
第 12 章：影响最大的事多半以前没发生过，前方路面冒出问号路牌；单点故障：一根绳吊着一排箱子，绳一断全掉）→
例子（全家只靠一份工资，绳子那头只拴着一个人）→
做法（留几个月生活费的应急钱，车距拉开、小猪罐坐进空当 / 收入往少里算 / 多一根绳，断一根还撑得住）→
拉远看整条路 → 评论区互动。
出处：Morgan Housel, The Psychology of Money (Harriman House, 2020)；中译本《金钱心理学》（摩根·豪泽尔著，李青宗译，
民主与建设出版社 / 后浪 2023）第 13 章“容错空间”、第 12 章“意外！”（转述）。跟车比喻、单份收入、按八成算预算为示意 /
据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, cross, join,
                               rect, stick, underline)

from .common import BOOK, episode

ACC = "#D9622B"                 # 本讲主色：交通锥橙（与其他讲的琥珀、蓝、绿区分）
SQUARE_SHOT = 3                 # 场景 4：急刹撞散账本车 + 冒汗的小猪罐

b = Board(size=(3600, 9700))


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

def ink(c, path, color, width):
    """与引擎描线同样的马克笔笔触。"""
    c.drawPath(path, wb.marker(color, width))
    c.drawPath(path, K.paint(color, 0.22, width * 0.45, blur=1.2))


def draw_partial(c, path, k, color, width):
    part, tip = wb.partial(path, k)
    ink(c, part, color, width)
    return tip if k < 1 else None


def car(x, y, s=1.0) -> skia.Path:
    """侧面小汽车（车头朝右）：(x, y) 为车底中点（地面），宽约 380·s、高约 200·s。"""
    body = P((x - 190 * s, y - 45 * s), (x - 190 * s, y - 120 * s), (x - 120 * s, y - 130 * s), (x - 80 * s, y - 200 * s),
             (x + 60 * s, y - 200 * s), (x + 115 * s, y - 130 * s), (x + 185 * s, y - 118 * s), (x + 190 * s, y - 45 * s),
             close=True)
    return join(body, P((x - 10 * s, y - 200 * s), (x - 10 * s, y - 130 * s)),
                P((x - 120 * s, y - 130 * s), (x + 115 * s, y - 130 * s)),
                circle(x - 110 * s, y - 40 * s, 38 * s), circle(x + 110 * s, y - 40 * s, 38 * s))


def ledger_car(x, y, w=620, h=290) -> skia.Path:
    """账本车：一本摊开的账本装上两个轮子。(x, y) 为地面中点。"""
    top = y - 50 - h
    return join(rect(x, top + h / 2, w, h, 18), P((x - w / 2 + 40, top), (x - w / 2 + 40, top + h)),
                circle(x - w / 2 + 120, y - 40, 38), circle(x + w / 2 - 120, y - 40, 38))


def house(x, y, w=280, h=230) -> skia.Path:
    """平房：(x, y) 为地面中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 35, y - h), (x, y - h - 150), (x + w / 2 + 35, y - h)),
                P((x - 35, y), (x - 35, y - 110), (x + 35, y - 110), (x + 35, y)), rect(x + w / 4 + 10, y - h + 70, 60, 60, 4))


def road(x0, x1, y, dash=True) -> skia.Path:
    parts = [P((x0, y), (x1, y))]
    if dash:
        xx = x0 + 30
        while xx + 70 < x1:
            parts.append(P((xx, y + 70), (xx + 70, y + 70)))
            xx += 150
    return join(*parts)


def star(x, y, r) -> skia.Path:
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return P(*pts, close=True)


def burst(x, y, r0, r1, n=8, a0=0.0) -> skia.Path:
    parts = []
    for i in range(n):
        a = a0 + i * 2 * math.pi / n
        parts.append(P((x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))))
    return join(*parts)


def zigzag(x0, y0, x1, y1, n=4, amp=18) -> skia.Path:
    pts = [(x0, y0)]
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy) or 1
    nx, ny = -dy / ln, dx / ln
    for i in range(1, n):
        f = i / n
        sg = amp if i % 2 else -amp
        pts.append((x0 + dx * f + nx * sg, y0 + dy * f + ny * sg))
    pts.append((x1, y1))
    return P(*pts)


def rotated(path, deg, x, y) -> skia.Path:
    m = skia.Matrix()
    m.setRotate(deg, x, y)
    out = skia.Path(path)
    out.transform(m)
    return out


def sheet(x, y, deg, w=110, h=140) -> skia.Path:
    """飞出去的一页账：带两道横线，旋转 deg 度。"""
    p = join(rect(x, y, w, h, 6), P((x - w / 2 + 18, y - 20), (x + w / 2 - 18, y - 20)),
             P((x - w / 2 + 18, y + 18), (x + w / 2 - 28, y + 18)))
    return rotated(p, deg, x, y)


def sign(x, y, r, post) -> skia.Path:
    """菱形路牌：(x, y) 为牌心，post 为杆长。"""
    return join(P((x, y - r), (x + r, y), (x, y + r), (x - r, y), close=True), P((x, y + r), (x, y + r + post)))


def ceiling(x0, x1, y) -> skia.Path:
    parts = [P((x0, y), (x1, y))]
    xx = x0 + 20
    while xx < x1:
        parts.append(P((xx, y), (xx + 30, y - 30)))
        xx += 70
    return join(*parts)


def hanging(x0, x1, y, n=4, bw=130, bh=110) -> skia.Path:
    """一根横杆吊着一排箱子：y 为横杆高度。"""
    parts = [P((x0, y), (x1, y))]
    step = (x1 - x0 - 80) / (n - 1)
    for i in range(n):
        cx = x0 + 40 + i * step
        parts += [P((cx, y), (cx, y + 40)), rect(cx, y + 40 + bh / 2, bw, bh, 6),
                  P((cx - bw / 2, y + 40 + 32), (cx + bw / 2, y + 40 + 32))]
    return join(*parts)


def pig(x, y, s=1.0, mood="smile") -> skia.Path:
    """小猪罐（车头朝右的侧身）：(x, y) 为脚底中点。mood：smile / sad / sweat / shock。"""
    body = skia.Path()
    body.addOval(skia.Rect.MakeXYWH(x - 130 * s, y - 205 * s, 260 * s, 190 * s))
    snout = skia.Path()
    snout.addOval(skia.Rect.MakeXYWH(x + 112 * s, y - 145 * s, 46 * s, 62 * s))
    tail = skia.Path()
    tail.moveTo(x - 128 * s, y - 120 * s)
    tail.quadTo(x - 175 * s, y - 135 * s, x - 160 * s, y - 160 * s)
    tail.quadTo(x - 140 * s, y - 175 * s, x - 150 * s, y - 140 * s)
    parts = [body, snout, tail,
             P((x + 35 * s, y - 196 * s), (x + 60 * s, y - 245 * s), (x + 85 * s, y - 188 * s)),
             P((x - 5 * s, y - 203 * s), (x + 12 * s, y - 248 * s), (x + 35 * s, y - 202 * s)),
             P((x - 70 * s, y - 196 * s), (x - 25 * s, y - 203 * s)),                  # 投币口
             circle(x + 128 * s, y - 115 * s, 4 * s), circle(x + 142 * s, y - 115 * s, 4 * s),
             circle(x + 78 * s, y - 150 * s, 6 * s)]
    for dx in (-85, -45, 45, 85):
        parts.append(P((x + dx * s, y - 32 * s), (x + dx * s, y)))
    if mood == "smile":
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(x + 70 * s, y - 100 * s, 48 * s, 30 * s), 20, 140)
        parts.append(m)
    elif mood == "shock":
        parts.append(circle(x + 92 * s, y - 72 * s, 13 * s))
    else:
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(x + 70 * s, y - 82 * s, 46 * s, 26 * s), 200, 140)
        parts.append(m)
    if mood in ("sweat", "shock"):
        d = skia.Path()
        dx, dy = x + 120 * s, y - 235 * s
        d.moveTo(dx, dy - 30 * s)
        d.quadTo(dx + 22 * s, dy + 4 * s, dx, dy + 12 * s)
        d.quadTo(dx - 22 * s, dy + 4 * s, dx, dy - 30 * s)
        parts.append(d)
    return join(*parts)


def pig_item(j, k0, x, y, s, moods, color=BLACK, width=9, sfx=None):
    """小猪罐（动态）：第 k0 拍起描出来；moods=[(镜头, 拍, 表情)]，到点换表情。"""

    def fn(c, k, t):
        mood = moods[0][2]
        for jj, kk, md in moods:
            if t >= b.t_of(jj, kk):
                mood = md
        return draw_partial(c, pig(x, y, s, mood), k, color, width)

    b.custom(j, k0, k0 + 0.9, fn, sfx=sfx)


def car_item(j, k0, x0, y, s=1.0, color=BLACK, moves=(), width=9, sfx=None):
    """会开动的车：moves=[(镜头, 起拍, 止拍, 位移, 缓动)]。缓动 "in" 为一脚油门撞上，其余为平缓挪动。"""

    def fn(c, k, t):
        x, moving, sgn = x0, False, 1
        for jj, ka, kb, dx, ease in moves:
            ta, tb = b.t_of(jj, ka), b.t_of(jj, kb)
            f = clamp01((t - ta) / max(1e-3, tb - ta))
            x += dx * (f * f if ease == "in" else ease_in_out(f))
            if 0 < f < 1:
                moving, sgn = True, 1 if dx > 0 else -1
        if moving:                                   # 车尾的速度线
            for dy in (-150, -100, -60):
                xb = x - sgn * 200 * s
                c.drawPath(P((xb, y + dy * s), (xb - sgn * 90 * s, y + dy * s)), K.paint(BLACK, 0.5, 6))
        return draw_partial(c, car(x, y, s), k, color, width)

    b.custom(j, k0, k0 + 0.9, fn, sfx=sfx)


def glow_fn(x, y, r=24):
    """刹车灯亮起：红点 + 一圈光晕。"""

    def fn(c, k, t):
        K.dot(c, x, y, r * 2.2 * k, RED, 0.22)
        K.dot(c, x, y, r * k, RED, 0.95)
        return None

    return fn


def slam_fn(x, y, s=1.0, color=BLACK, width=10):
    """前车“砸”进画面：从大到小落定（drop 拍上）。"""

    def fn(c, k, t):
        g = 1 + 0.45 * (1 - ease_out(k))
        c.save()
        c.translate(x, y)
        c.scale(g, g)
        c.translate(-x, -y)
        ink(c, car(x, y, s), color, width)
        c.restore()
        return None

    return fn


def gap_fn(x0, x1, y0, y1, color=GREEN, alpha=0.22):
    """两车之间的空当从左往右铺满淡绿色。"""

    def fn(c, k, t):
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + (x1 - x0) * k, y1), K.paint(color, alpha))
        return None

    return fn


# ---------------------------------------------------------------- 开局：跟车太近（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

GY1 = 1280                      # 第一段马路的地面
scene("前车一脚急刹", "跟车距离", (1150, 1000, 0.85), bars=2)
L(road(560, 1740, GY1), 0, 0.9, sfx="wood_low")
L(car(1400, GY1), 1, 1.9, BLACK, 9, sfx="pop")
J1 = J()
car_item(J1, 2, 950, GY1, color=BLUE, moves=[(J1 + 1, 0, 1, 65, "in")], sfx="wood_high")
b.custom(J1, 3, 3.4, glow_fn(1214, 1170), sfx="tom")
L(burst(1214, 1170, 40, 75, 5, math.pi * 0.6), 3.4, 3.9, RED, 7)
L(P((1140, 1040), (1140, 1010), (1210, 1010), (1210, 1040)), 4, 4.5, RED, 8, sfx="pop")
T("太近！", 1175, 940, 64, RED, k0=4.5, k1=5.3)

scene("跟太紧，就撞上", "跟车距离", (1150, 1000, 0.95), shake=[1], flashes=[(1, 0.3)])
H(0, "shaker")
H(1, "rim")
L(burst(1205, 1140, 60, 120, 8, 0.2), 2, 2.8, RED, 8, sfx="pop")
L(join(star(1040, 1010, 40), star(1340, 1000, 34)), 3, 3.8, BLACK, 7, sfx="wood_high")
L(join(zigzag(1150, 1085, 1185, 1190, 4, 12), zigzag(1235, 1095, 1260, 1180, 3, 10)), 4, 4.6, RED, 8, sfx="rim")
T("追尾！", 1150, 790, 100, RED, k0=5, k1=5.9, sfx="ding")
L(underline(1010, 1290, 850), 6, 6.7, RED, 8, sfx="pop")

# ---------------------------------------------------------------- 小王的钱也贴着走（场景 3–4，场景 4 为 drop）

LX, GY3 = 2440, 1290
scene("小王的钱也贴太紧", "跟车距离 · 小王的账本", (2650, 1000, 0.85))
L(ledger_car(LX, GY3), 0, 0.9, BLUE, 9, sfx="wood_low")
T("房租+还款+花销", LX + 20, 1050, 58, k0=1, k1=2.75, sfx="pop")
T("= 工资", LX + 20, 1160, 64, k0=3, k1=3.8, sfx="pop")
T("剩：0", 2610, 790, 84, RED, k0=4, k1=4.8, sfx="rim")
L(circle(2610, 785, 105), 5, 5.7, RED, 7, sfx="pop")
J3 = J()
pig_item(J3, 6, 2265, 900, 0.8, [(J3, 6, "sweat"), (J3 + 1, 5, "shock")], sfx="ding")

FX = 2985                       # 前车（意外）位置
scene("一次意外，全乱了", "跟车距离 · 急刹", (2650, 1030, 0.75), shake=[0, 5], flashes=[0])
b.custom(J(), 0, 0.3, slam_fn(FX, GY3), sfx="kick")
b.custom(J(), 1, 1.4, glow_fn(FX - 188, GY3 - 110), sfx="tom")
L(join(rect(FX, 860, 420, 200, 14), P((FX, 960), (FX, GY3 - 200))), 2, 2.8, RED, 8, sfx="wood_high")
T("裁员", FX, 805, 58, RED, k0=3, k1=3.5, sfx="pop")
T("生病 / 搬家", FX, 905, 58, RED, k0=3.5, k1=4.75)
L(join(zigzag(2700, 1000, 2650, 1180, 4, 16), zigzag(2560, 960, 2470, 1100, 3, 14),
       burst(2770, 1130, 45, 95, 6, 1.0)), 5, 5.8, RED, 8, sfx="rim")
L(join(sheet(2120, 1420, -25), sheet(2330, 1480, 18), sheet(2560, 1440, -8),
       P((2190, 1340), (2240, 1300)), P((2400, 1390), (2440, 1350))), 7, 7.9, BLACK, 7, sfx="wood_high")
T("全乱了", 2880, 1470, 100, RED, k0=6, k1=6.9, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 5–9）

scene("翻开《金钱心理学》", "书中观点 · 第13章", (2650, 2600, 0.85))
L(book(2400, 2620, 460, 300), 0, 0.9, sfx="wood_low")
T("金钱心理学", 2400, 2360, 76, BLUE, k0=1, k1=2.25, sfx="pop")
L(stick(2960, 2790, 0.65, "point"), 3, 3.8, BLACK, 9, sfx="wood_high")
L(rect(2960, 2870, 380, 90, 16), 4, 4.6, BLUE, 7, sfx="pop")
T("摩根·豪泽尔", 2960, 2872, 54, k0=4.6, k1=6.1)
T("第13章 · 容错空间", 2650, 3010, 62, k0=6.2, k1=7.9)
H(7, "ding")

scene("计划会出岔子", "书中观点 · 第13章", (950, 2600, 0.85))
L(arrow((420, 2760), (1480, 2760), 0.0, 50), 0, 0.9, BLACK, 10, sfx="wood_low")
T("原计划", 560, 2680, 58, k0=1, k1=1.8, sfx="pop")
L(join(arrow((780, 2760), (1050, 3000), 0.15, 40), arrow((1120, 2760), (1360, 2560), -0.15, 40)), 2, 2.9, RED, 9,
  sfx="rim")
T("岔子", 1180, 3030, 64, RED, k0=3, k1=3.6, sfx="pop")
T("?", 1420, 2500, 80, RED, k0=4, k1=4.8, sfx="tom")
L(rect(950, 2290, 780, 150, 20), 5, 5.8, BLUE, 8, sfx="wood_high")
T("计划里，算上岔子", 950, 2295, 70, BLUE, k0=6, k1=8, sfx="ding")

GY7 = 4450
scene("这叫安全边际", "书中提到 · 安全边际", (950, 4200, 0.85))
L(join(road(380, 1520, GY7), car(1250, GY7)), 0, 0.9, BLACK, 9, sfx="wood_low")
L(car(600, GY7), 1, 1.9, BLUE, 9, sfx="wood_high")
b.custom(J(), 2, 2.8, gap_fn(795, 1055, GY7 - 200, GY7), sfx="ding")
L(join(P((800, GY7 - 230), (1050, GY7 - 230)), P((800, GY7 - 250), (800, GY7 - 210)),
       P((1050, GY7 - 250), (1050, GY7 - 210))), 3, 3.6, GREEN, 8, sfx="pop")
T("余地", 925, GY7 - 300, 66, GREEN, k0=3.6, k1=4.4)
T("安全边际", 950, 3850, 100, BLUE, k0=5, k1=6, sfx="tom")
T("格雷厄姆的说法", 950, 3980, 54, k0=6, k1=7.75, sfx="pop")

scene("世界总会出意外", "书中观点 · 第12章", (2650, 4200, 0.85))
L(join(P((2180, 4680), (2590, 3920)), P((3120, 4680), (2710, 3920)), P((2140, 3920), (3160, 3920))), 0, 0.9, BLACK,
  9, sfx="wood_low")
L(join(*[P((2650, y), (2650, y - ln)) for y, ln in ((4660, 90), (4500, 70), (4360, 54), (4240, 40), (4140, 28),
                                                      (4060, 20))]), 1, 1.7, BLACK, 8, sfx="wood_high")
L(sign(3010, 4180, 110, 260), 2, 2.8, RED, 9, sfx="pop")
T("?", 3010, 4185, 120, RED, k0=3, k1=3.6, sfx="tom")
L(sign(2310, 4140, 75, 170), 4, 4.7, RED, 8, sfx="pop")
T("?", 2310, 4145, 84, RED, k0=4.7, k1=5.2)
T("影响最大的，常是头一回", 2650, 3790, 64, k0=6, k1=8, sfx="ding")

RX = 2650
scene("别让一处断了全倒", "书中观点 · 单点故障", (2650, 5800, 0.85), shake=[5])
J9 = J()
L(join(ceiling(2250, 3050, 5370), P((2250, 6110), (3050, 6110))), 0, 0.9, BLACK, 9, sfx="wood_low")


def _drop(t):
    """横杆和箱子下落：第 4.3 拍绳断后开始掉，第 5 拍落地。返回 (位移, 是否落地)。"""
    ta, tb = b.t_of(J9, 4.3), b.t_of(J9, 5)
    if t < ta:
        return 0.0, False
    f = clamp01((t - ta) / (tb - ta))
    return 360 * f * f, t >= tb


def rope_fn(c, k, t):
    dy, landed = _drop(t)
    upper = P((RX, 5370), (RX, 5470))
    if b.t_of(J9, 4) > t:
        return draw_partial(c, P((RX, 5370), (RX, 5600)), k, BLACK, 9)
    ink(c, upper, BLACK, 9)
    if not landed:
        ink(c, P((RX, 5490 + dy), (RX, 5600 + dy)), BLACK, 9)
    return None


def boxes_fn(c, k, t):
    dy, landed = _drop(t)
    if landed:
        parts = [rotated(P((2290, 6100), (3010, 6100)), 3, 2650, 6100)]
        for i, (bx, deg) in enumerate(((2390, -14), (2580, 9), (2770, -6), (2950, 17))):
            parts.append(rotated(join(rect(bx, 6045, 130, 110, 6), P((bx - 65, 6022), (bx + 65, 6022))), deg, bx, 6045))
        ink(c, join(*parts), BLACK, 9)
        return None
    p = skia.Path(hanging(2300, 3000, 5600))
    p.offset(0, dy)
    return draw_partial(c, p, k, BLACK, 9)


b.custom(J9, 1, 1.8, rope_fn, sfx="pop")
b.custom(J9, 2, 2.9, boxes_fn, sfx="wood_high")
L(join(zigzag(RX - 40, 5465, RX + 40, 5495, 4, 10), burst(RX, 5480, 30, 60, 6)), 4, 4.3, RED, 8, sfx="rim")
H(5, "kick")
T("一处断，全倒", 2650, 6250, 76, RED, k0=6, k1=7.5, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10）

scene("只有一份收入", "例子 · 一份工资", (950, 5800, 0.85))
L(house(1250, 6150, 300, 220), 0, 0.9, BLACK, 9, sfx="wood_low")
T("一家开销", 1250, 6230, 56, k0=1, k1=2, sfx="pop")
L(stick(560, 6150, 0.8, "hold"), 3, 3.8, BLUE, 9, sfx="wood_high")
L(P((650, 5990), (860, 6010), (1100, 5990)), 4, 4.7, BLACK, 8, sfx="pop")
T("一份工资", 870, 5920, 56, BLUE, k0=5, k1=6, sfx="pop")
T("要是断了？", 950, 5480, 80, RED, k0=6.2, k1=7.45)
H(7, "rim")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

GY11 = 7650
scene("留够几个月生活费", "做法一 · 应急钱", (950, 7400, 0.85))
T("① 留几个月生活费", 950, 7000, 76, BLUE, k0=0, k1=2, sfx="pop")
L(join(road(380, 1520, GY11), car(1300, GY11)), 2, 2.9, BLACK, 9, sfx="wood_low")
J11 = J()
car_item(J11, 3, 860, GY11, color=BLUE, moves=[(J11, 4, 5, -260, "out")], sfx="wood_high")
H(4, "shaker")
pig_item(J11, 5, 950, GY11, 0.8, [(J11, 5, "smile")], GREEN, 9, sfx="ding")
T("应急钱", 950, 7385, 62, GREEN, k0=6, k1=6.8, sfx="pop")
L(check(1300, 7300, 50), 7, 7.6, GREEN, 9, sfx="ding")

scene("按少一点来算", "做法二 · 打个折", (2650, 7400, 0.85))
T("② 收入往少里算", 2650, 7000, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(join(rect(2650, 7420, 780, 480, 20), P((2300, 7180), (2300, 7660))), 2, 2.9, BLACK, 9, sfx="wood_low")
T("收入：全部工资", 2690, 7310, 66, k0=3, k1=4.75, sfx="pop")
L(P((2400, 7305), (2990, 7300)), 5, 5.5, RED, 9, sfx="rim")
T("按八成来算", 2690, 7480, 74, RED, k0=6, k1=7.5, sfx="ding")
L(underline(2510, 2870, 7540), 7.5, 8, RED, 7)

scene("多一条退路", "做法三 · 多一根绳", (2650, 9000, 0.85))
T("③ 多一条退路", 2650, 8580, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(join(ceiling(2250, 3050, 8700), P((2450, 8700), (2450, 8950)), hanging(2250, 3050, 8950)), 2, 2.8, BLACK, 9,
  sfx="wood_low")
T("工资", 2340, 8830, 54, k0=3, k1=3.8, sfx="pop")
L(P((2850, 8700), (2850, 8950)), 4, 4.5, GREEN, 11, sfx="ding")
T("存款", 2960, 8830, 54, GREEN, k0=4.5, k1=5.3)
L(join(zigzag(2420, 8860, 2480, 8890, 4, 10), cross(2450, 8875, 26)), 6, 6.5, RED, 8, sfx="rim")
T("还撑得住！", 2650, 9300, 76, GREEN, k0=6.6, k1=7.85)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看整条路，再推到评论区

FAR = (1800, 4000, 0.14)
COMMENT = (1000, 9060, 0.8)
scene("你留了多少余地？", "评论区见", FAR, bars=4)
J14 = J()
b.move(J14, 4, COMMENT)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你留了多少余地？", 1000, 8760, 80, RED, k0=6, k1=8, sfx="pop")
pig_item(J14, 8, 1000, 9480, 1.0, [(J14, 8, "smile")], GREEN, 9, sfx="ding")
T("下一讲：管钱的办法，睡得着就够了", 1000, 8930, 48, k0=9, k1=13, sfx="wood_high")
L(P((620, 8985), (1380, 8985)), 13, 13.6, BLACK, 6)
b.hit(J14, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "margin", "留出余地", "计划总被打乱，钱怎么留余地？", ACC, b.shots,
                 [f"{BOOK}第 13 章“容错空间”、第 12 章“意外！”（转述）",
                  "Morgan Housel, The Psychology of Money (Harriman House, 2020)",
                  "中译本：《金钱心理学》，李青宗译，民主与建设出版社 / 后浪 2023"],
                 "计划总被打乱|钱怎么【留余地】？", SQUARE_SHOT,
                 ["书中观点（转述）：第 13 章“容错空间”——计划里最要紧的一条，是承认计划可能出错；书中提到本杰明·格雷厄姆的"
                  "“安全边际”；要避开一处失败就全盘崩溃的“单点故障”；存款就是给意外留的余地。第 12 章“意外！”——历史上"
                  "影响最大的事多半以前没发生过，该从中学到的是世界会出意外。出处：Morgan Housel, The Psychology of Money "
                  "(Harriman House, 2020)；中译本《金钱心理学》（摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023）"
                  "第 13 章“容错空间”、第 12 章“意外！”（转述）。上屏均为转述，不是逐字引文。",
                  "跟车距离的比喻（急刹、追尾、两车之间的空当）为示意；“安全边际”画成两车之间的绿色空白、"
                  "“单点故障”画成一根绳吊一排箱子，均为对书中观点的通俗化示意。",
                  "小王的账本（房租 + 还款 + 花销 = 工资）、全家只靠一份工资为现实场景示意，不指向任何具体公司或个人。",
                  "三步做法（留几个月生活费作应急钱；做预算时收入按八成来算；多一份收入或存款作退路）为据书中思路整理的"
                  "示意，“八成”只是举例，不是书中数字；本讲不构成任何投资建议。"],
                 tags="#应急 #风险")
    return b.attach(ep)
