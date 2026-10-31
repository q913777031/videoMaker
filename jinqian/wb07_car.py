"""07 豪车悖论（白板手绘版）：开豪车的人，你记住他了吗？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（形式 C：复刻作者的观察，先猜后揭晓）：一辆豪车停在酒店门口，车主下车，路边几个人回头 →
让观众先猜：路人心里想的是“车主真厉害”“这车真帅”还是“我要是有……” → 书中故事：作者年轻时在酒店门口当代客泊车员，
天天看这一幕 → drop 揭晓：车主在大家眼里淡成一圈虚线，路人想的全是“我开着它多酷”，第三张打勾 →
亮书（小猪罐出场）→ 书中观点：看豪车的人想的是自己；想被尊重，靠善良和谦逊（天平）；
看得见的是花掉的钱，没花出去的才是财富（停车场：空车位涂绿）→ 例子：同学会上大家只盯着一只包 →
三个做法（买前问一句“给自己用还是给别人看”、先对人好、把没买的记下来，小猪罐胖一圈）→ 拉远全板 → 评论区。
书中观点为转述：摩根·豪泽尔《金钱心理学》第 8 章“豪车悖论”、第 9 章“财富是你看不见的那些”
（后浪 2023 版，李青宗译）；选项卡、同学会、没买清单等为示意 / 据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, face, join,
                               rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out

from .common import BOOK, episode

ACC = "#B8862B"
SQUARE_SHOT = 3                 # 场景 4：车主淡成虚线，路人气泡里是“我开着它”，第三张卡打勾

b = Board(size=(3600, 8800))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(fn, k0, k1, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


# ---------------------------------------------------------------- 本讲画法

def ink(c, path, color=BLACK, width=9):
    """照引擎描线的笔触画一条路径（custom 动画里用）。"""
    c.drawPath(path, wb.marker(color, width))
    c.drawPath(path, K.paint(color, 0.22, width * 0.45, blur=1.2))


def pig(x, y, s=1.0, mood="smile") -> skia.Path:
    """系列角色小猪罐（朝右）：(x, y) 为身子中心；背上投币口、两只耳朵、鼻子、点点眼、一道嘴、四条小腿、卷尾巴。"""
    body = skia.Path()
    body.addOval(skia.Rect.MakeXYWH(x - 120 * s, y - 90 * s, 240 * s, 180 * s))
    slot = P((x - 30 * s, y - 72 * s), (x + 22 * s, y - 72 * s))
    ears = join(P((x + 18 * s, y - 84 * s), (x + 38 * s, y - 130 * s), (x + 62 * s, y - 76 * s)),
                P((x + 52 * s, y - 74 * s), (x + 82 * s, y - 116 * s), (x + 94 * s, y - 60 * s)))
    snout = skia.Path()
    snout.addOval(skia.Rect.MakeXYWH(x + 104 * s, y - 32 * s, 46 * s, 54 * s))
    parts = [body, slot, ears, snout, circle(x + 120 * s, y - 6 * s, 4 * s), circle(x + 135 * s, y - 6 * s, 4 * s),
             circle(x + 72 * s, y - 38 * s, 5 * s)]
    mouth = skia.Path()
    if mood == "smile":
        mouth.addArc(skia.Rect.MakeXYWH(x + 62 * s, y + 4 * s, 42 * s, 28 * s), 20, 140)
    elif mood == "sad":
        mouth.addArc(skia.Rect.MakeXYWH(x + 62 * s, y + 20 * s, 42 * s, 26 * s), 200, 140)
    else:
        mouth.addCircle(x + 84 * s, y + 26 * s, 10 * s)
    parts.append(mouth)
    if mood == "sweat":
        drop = skia.Path()
        drop.moveTo(x + 10 * s, y - 150 * s)
        drop.quadTo(x - 14 * s, y - 112 * s, x + 10 * s, y - 108 * s)
        drop.quadTo(x + 34 * s, y - 112 * s, x + 10 * s, y - 150 * s)
        parts.append(drop)
    for dx in (-70, -30, 35, 72):
        top = y + 90 * s * math.sqrt(max(0.0, 1 - (dx / 120) ** 2)) - 6 * s
        parts.append(P((x + dx * s, top), (x + dx * s, y + 115 * s)))
    tail = skia.Path()
    tail.moveTo(x - 118 * s, y - 15 * s)
    tail.quadTo(x - 160 * s, y - 45 * s, x - 150 * s, y - 8 * s)
    tail.quadTo(x - 142 * s, y + 14 * s, x - 168 * s, y + 4 * s)
    parts.append(tail)
    return join(*parts)


def pig_fn(x, y, s=1.0, mood="smile", grow_at=None, color=BLACK, width=9):
    """小猪罐逐笔画出；grow_at=(镜头, 拍) 时从那一拍起胖一圈（以脚底为中心放大）。"""
    path = pig(x, y, s, mood)
    foot = y + 115 * s

    def fn(c, k, t):
        part, tip = wb.partial(path, k)
        g = 1.0
        if grow_at is not None:
            t0 = b.t_of(*grow_at)
            g = 1 + 0.22 * ease_in_out(clamp01((t - t0) / 0.45))
        c.save()
        if g != 1.0:
            c.translate(x, foot)
            c.scale(g, g)
            c.translate(-x, -foot)
        ink(c, part, color, width)
        c.restore()
        return tip

    return fn


def coin(x, y, r=30) -> skia.Path:
    return join(circle(x, y, r), P((x, y - r * 0.55), (x, y + r * 0.55)))


def coin_drop_fn(x, y0, y1, r=28):
    """一枚硬币从 y0 落进 y1 的投币口，落进去就不见了。"""

    def fn(c, k, t):
        if k >= 1:
            return None
        y = y0 + (y1 - y0) * k * k
        K.dot(c, x, y, r, "#E8B83A", 0.9)
        ink(c, coin(x, y, r), BLACK, 6)
        return None

    return fn


def car(x, y, s=1.0) -> skia.Path:
    """跑车侧影（车头朝右，不画车标）：(x, y) 为地面中点，车长约 600·s。"""
    body = P((x - 300 * s, y - 45 * s), (x - 300 * s, y - 85 * s), (x - 260 * s, y - 115 * s), (x - 125 * s, y - 122 * s),
             (x - 60 * s, y - 185 * s), (x + 85 * s, y - 182 * s), (x + 190 * s, y - 122 * s), (x + 290 * s, y - 102 * s),
             (x + 305 * s, y - 62 * s), (x + 300 * s, y - 45 * s), close=True)
    window = P((x - 100 * s, y - 126 * s), (x - 48 * s, y - 170 * s), (x + 78 * s, y - 167 * s), (x + 150 * s, y - 126 * s),
               close=True)
    return join(body, window, P((x + 15 * s, y - 120 * s), (x + 15 * s, y - 55 * s)),
                circle(x - 180 * s, y - 45 * s, 46 * s), circle(x + 180 * s, y - 45 * s, 46 * s),
                circle(x - 180 * s, y - 45 * s, 14 * s), circle(x + 180 * s, y - 45 * s, 14 * s),
                P((x + 262 * s, y - 92 * s), (x + 292 * s, y - 86 * s)))


def car_top(x, y, s=1.0) -> skia.Path:
    """俯视的小车：(x, y) 为车身中心。"""
    wind = skia.Path()
    wind.moveTo(x - 55 * s, y - 40 * s)
    wind.quadTo(x, y - 62 * s, x + 55 * s, y - 40 * s)
    return join(rect(x, y, 140 * s, 220 * s, 46 * s), wind, P((x - 50 * s, y + 55 * s), (x + 50 * s, y + 55 * s)),
                P((x - 50 * s, y - 40 * s), (x - 50 * s, y + 55 * s)), P((x + 50 * s, y - 40 * s), (x + 50 * s, y + 55 * s)))


def hotel(x, y, w=420, h=600) -> skia.Path:
    """酒店门脸：(x, y) 为地面中点；上沿留出招牌位，中间一道波浪雨棚，下面双开门。"""
    awn = skia.Path()
    ay = y - h + 210
    awn.moveTo(x - w / 2 - 30, ay)
    xx = x - w / 2 - 30
    while xx < x + w / 2 + 30 - 1:
        awn.quadTo(xx + 30, ay + 40, xx + 60, ay)
        xx += 60
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)), awn,
                P((x - w / 2 - 30, ay), (x + w / 2 + 30, ay)),
                P((x - 85, y), (x - 85, y - 280), (x + 85, y - 280), (x + 85, y)), P((x, y), (x, y - 280)))


def key(x, y, s=1.0) -> skia.Path:
    return join(circle(x, y, 16 * s), P((x + 16 * s, y), (x + 62 * s, y)), P((x + 44 * s, y), (x + 44 * s, y + 15 * s)),
                P((x + 58 * s, y), (x + 58 * s, y + 12 * s)))


def thought(x, y, w, h, tx, ty) -> skia.Path:
    """想法气泡：圆角框 + 两颗小圆点连到 (tx, ty)（想事的人头顶）。"""
    bx, by = x + (tx - x) * 0.1, y + h / 2
    return join(rect(x, y, w, h, 70), circle(bx + (tx - bx) * 0.35, by + (ty - by) * 0.35, 20),
                circle(bx + (tx - bx) * 0.7, by + (ty - by) * 0.7, 12))


def dashed(path: skia.Path, on=26, off=20) -> skia.Path:
    """把一条路径切成虚线段（车主“淡出”用）。"""
    out = skia.Path()
    pm = skia.PathMeasure(path, False)
    while True:
        n, d = pm.getLength(), 0.0
        while d < n:
            seg = skia.Path()
            pm.getSegment(d, min(d + on, n), seg, True)
            out.addPath(seg)
            d += on + off
        if not pm.nextContour():
            break
    return out


def blink_fn(x, y, r, j, k0, k1):
    """问号后面一圈红光一闪一闪（只在第 j 镜第 k0–k1 拍）。"""

    def fn(c, k, t):
        if t > b.t_of(j, k1):
            return None
        a = 0.5 + 0.5 * math.sin((t - b.t_of(j, k0)) * 9)
        K.dot(c, x, y, r, RED, 0.12 + 0.18 * a)
        return None

    return fn


def scale(x, y, tilt=60, arm=300, r=110) -> skia.Path:
    """天平：底座 + 立柱 + 斜梁（右低）+ 两只秤盘。(x, y) 为底座中点。"""
    top = y - 300
    lx, ly, rx, ry = x - arm, top - tilt, x + arm, top + tilt
    parts = [P((x - 110, y), (x + 110, y)), P((x, y), (x, top)), circle(x, top, 12), P((lx, ly), (rx, ry))]
    for px, py in ((lx, ly), (rx, ry)):
        pan = skia.Path()
        pan.addArc(skia.Rect.MakeXYWH(px - r, py + 90, 2 * r, 80), 0, 180)
        parts += [P((px, py), (px - r, py + 130)), P((px, py), (px + r, py + 130)), pan,
                  P((px - r, py + 130), (px + r, py + 130))]
    return join(*parts)


def heart(x, y, r=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def bag(x, y, s=1.0) -> skia.Path:
    """手提包（不画任何标志）：(x, y) 为包底中点。"""
    handle = skia.Path()
    handle.addArc(skia.Rect.MakeXYWH(x - 40 * s, y - 150 * s, 80 * s, 100 * s), 180, 180)
    return join(P((x - 70 * s, y), (x - 55 * s, y - 100 * s), (x + 55 * s, y - 100 * s), (x + 70 * s, y), close=True),
                handle, P((x - 58 * s, y - 72 * s), (x + 58 * s, y - 72 * s)))


def cart() -> skia.Path:
    """购物车（场景 11 固定位置）：车筐 + 网格 + 车架 + 轮子 + 把手（伸到小王手里）。"""
    return join(P((2510, 5300), (2890, 5300), (2850, 5480), (2550, 5480), close=True),
                P((2637, 5300), (2650, 5480)), P((2763, 5300), (2750, 5480)), P((2530, 5390), (2870, 5390)),
                P((2550, 5480), (2565, 5525), (2860, 5525)), circle(2595, 5555, 28), circle(2830, 5555, 28),
                P((2510, 5300), (2440, 5300), (2400, 5415)))


def notebook(x, y, w=480, h=560) -> skia.Path:
    parts = [rect(x, y, w, h, 18)]
    for i in range(5):
        parts.append(circle(x - w / 2 + 80 + i * (w - 160) / 4, y - h / 2, 14))
    return join(*parts)


def fill_fn(x, y, w, h, color=GREEN, alpha=0.32):
    """一格车位从下往上涂满。"""

    def fn(c, k, t):
        K.rr(c, x, y + h / 2 - h * k / 2, w, h * k, 12, color, alpha)
        return None

    return fn


# ---------------------------------------------------------------- 开局：豪车停在酒店门口，先猜（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。
# 第一排（地面 y=1250）：酒店门脸 x≈600 · 作者 x=1000 · 跑车 x=1550 · 车主 x=1950 · 路人 x=2120–2380 · 选项卡 x≈2950。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


GROUND = 1250
CAR = (1550, GROUND)
OWNER = (1950, GROUND, 0.7)
FOLK = (2120, 2250, 2380)

scene("一辆豪车开过来", "先猜一猜", (1820, 950, 0.85), bars=2)
L(P((1180, GROUND + 12), (2460, GROUND + 12)), 0, 0.8, BLACK, 8, sfx="wood_low")
L(car(*CAR), 1, 1.9, BLACK, 10, sfx="wood_high")
L(join(P((1190, 1100), (1265, 1100)), P((1200, 1140), (1280, 1140)), P((1180, 1195), (1235, 1195))), 2, 2.6, BLUE, 8,
  sfx="pop")
L(stick(*OWNER, tie=True), 3, 3.8, BLACK, 9, sfx="wood_high")
L(face(*OWNER, "smile"), 3.8, 4.0, BLACK, 8)
L(join(*[stick(x, GROUND, 0.65) for x in FOLK]), 4, 4.9, BLACK, 9, sfx="pop")
for n, x in enumerate(FOLK):
    T("！", x + 52, 1000, 56, RED, k0=5 + n * 0.3, k1=5.3 + n * 0.3, sfx="pop" if n == 0 else None)

CARDS = [("车主真厉害", 700), ("这车真帅", 910), ("我要是有……", 1120)]
j_guess = scene("猜猜他们在想啥", "先猜一猜", (2950, 950, 0.85))
T("路人在想啥", 2880, 480, 72, k0=0, k1=1.25, sfx="pop")
T("？", 3200, 470, 120, RED, k0=1.25, k1=1.75)
for n, (s, y) in enumerate(CARDS):
    L(rect(2950, y, 700, 170, 26), 2 + 2 * n, 2.4 + 2 * n, BLUE if n < 2 else ACC, 8, sfx="wood_high" if n == 1 else "pop")
    T(s, 2920, y, 64, k0=2.4 + 2 * n, k1=3.8 + 2 * n if n < 2 else 7.9)
C(blink_fn(3200, 465, 95, j_guess, 8, 12), 8, 8.2)

scene("有人天天看这一幕", "书中故事 · 泊车员", (900, 950, 0.85))
L(hotel(600, GROUND), 0, 0.9, BLACK, 9, sfx="wood_low")
T("酒店", 600, 750, 76, k0=1, k1=1.8, sfx="pop")
L(stick(1000, GROUND, 0.75, "hold"), 2, 2.8, BLUE, 10, sfx="wood_high")
L(face(1000, GROUND, 0.75, "smile"), 2.8, 3.0, BLUE, 8)
L(rect(1000, 900, 180, 90, 14), 3, 3.4, BLACK, 7, sfx="pop")
T("作者", 1000, 900, 56, BLUE, k0=3.4, k1=4.2)
L(key(1085, 1112, 1.0), 4.2, 4.8, BLACK, 7)
T("年轻时当泊车员", 900, 520, 66, k0=5, k1=6.75, sfx="pop")
L(underline(660, 1140, 575), 7, 7.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 揭晓（场景 4，drop）：车主淡成虚线，路人想的全是自己

scene("没人记住车主", "揭晓", (2560, 790, 0.62), shake=[0], flashes=[0])
H(0, "kick", 0.9, "drop：车主淡出")
b.erase(J(), 0, 0.6, OWNER[0], 1108, 150, 290)
L(dashed(join(stick(*OWNER, tie=True), face(*OWNER, "flat"))), 1, 1.8, BLACK, 7, sfx="rim")
T("车主？", 1950, 900, 80, k0=2, k1=2.8, sfx="pop")
L(thought(2300, 650, 520, 400, 2250, 1020), 3, 3.9, BLACK, 9, sfx="wood_high")
L(join(car(2300, 800, 0.42), circle(2270, 690, 30)), 4, 4.8, BLACK, 8, sfx="pop")
L(face(2270, 690 + 290 * 0.65, 0.65, "smile"), 4.8, 5.0, BLACK, 6)
T("我", 2300, 545, 84, BLUE, k0=5, k1=5.8, sfx="pop")
T("我开着它，多酷！", 2300, 330, 88, RED, k0=6, k1=7.0, sfx="tom")
L(check(3240, 1110, 80), 7, 7.8, GREEN, 14, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 5–9）

scene("书里写过这一幕", "金钱心理学 · 书中观点", (950, 2400, 0.85))
L(book(750, 2450, 420, 280), 0, 0.9, BLACK, 10, sfx="wood_low")
T("金钱心理学", 750, 2190, 76, GREEN, k0=1, k1=2.25, sfx="pop")
T("摩根·豪泽尔", 750, 2700, 56, k0=3, k1=4.5, sfx="pop")
C(pig_fn(1300, 2560, 0.8), 5, 5.9, sfx="wood_high")
C(coin_drop_fn(1300, 2330, 2500), 7, 7.6, sfx="ding")

ONL = (2250, 2800, 0.8)
scene("大家想的是自己", "书中观点 · 豪车悖论", (2650, 2400, 0.85))
L(stick(*ONL), 0, 0.8, BLUE, 10, sfx="wood_high")
L(face(*ONL, "smile"), 0.8, 1.0, BLUE, 8)
L(car(2930, 2800, 0.55), 1, 1.9, BLACK, 9, sfx="pop")
L(arrow((2320, 2560), (2760, 2680), -0.12, 36), 2, 2.8, BLACK, 7, sfx="wood_high")
L(thought(2420, 2210, 620, 220, 2260, 2520), 3, 3.8, BLACK, 8, sfx="pop")
T("要是我开它……", 2420, 2210, 58, k0=4, k1=5.75)
T("别人会佩服我", 2650, 1980, 80, RED, k0=6, k1=7.5, sfx="ding")

scene("想被尊重，靠人品", "书中观点 · 尊重", (950, 3850, 0.85))
L(scale(950, 4250), 0, 0.9, BLACK, 9, sfx="wood_low")
L(car(650, 4015, 0.3), 1, 1.8, BLACK, 7, sfx="pop")
T("车", 650, 4150, 72, k0=2, k1=2.8, sfx="pop")
L(heart(1250, 4095, 40), 3, 3.8, RED, 9, sfx="wood_high")
T("人品", 1250, 4275, 72, RED, k0=4, k1=4.8, sfx="pop")
T("善良 · 谦逊", 950, 3500, 76, GREEN, k0=6, k1=7.5, sfx="ding")

STALL_W, STALL_H = 220, 260
COLS = [2320, 2540, 2760, 2980]
ROWS = [3590, 3910]
PARKED = [(0, 0), (0, 1), (0, 3), (1, 0), (1, 2), (1, 3)]      # (行, 列)；空着 (0, 2) 和 (1, 1)


def lot() -> skia.Path:
    parts = [P((2210, 3460), (3090, 3460)), P((2210, 4040), (3090, 4040))]
    for i in range(5):
        x = 2210 + STALL_W * i
        parts += [P((x, 3460), (x, 3720)), P((x, 3780), (x, 4040))]
    return join(*parts)


scene("看得见的是花掉的", "书中观点 · 看得见的钱", (2650, 3850, 0.85))
T("看得见的", 2650, 3375, 72, k0=0, k1=1.0, sfx="pop")
L(lot(), 1, 1.9, BLACK, 8, sfx="wood_low")
for r in range(2):
    L(join(*[car_top(COLS[c], ROWS[r], 0.8) for rr, c in PARKED if rr == r]), 2 + r, 2.8 + r, BLACK, 8, sfx="pop")
T("= 花掉的钱", 2650, 4150, 76, RED, k0=5, k1=6.5, sfx="rim")

scene("没花的，才是财富", "书中观点 · 看不见的钱", (2650, 3900, 0.78))
C(fill_fn(COLS[2], ROWS[0], 200, 240), 0, 0.6, sfx="ding")
C(fill_fn(COLS[1], ROWS[1], 200, 240), 1, 1.6, sfx="ding")
C(pig_fn(COLS[2], ROWS[0] - 5, 0.5, width=7), 2, 2.8, sfx="wood_high")
L(join(coin(2505, 3950), coin(2575, 3950), coin(2540, 3885)), 3, 3.8, GREEN, 7, sfx="pop")
T("没花出去的 = 财富", 2650, 4330, 72, GREEN, k0=5, k1=7.5, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10）

scene("同学会上都看包", "例子 · 同学会", (950, 5300, 0.85))
L(join(P((450, 5480), (1450, 5480)), P((500, 5480), (500, 5590)), P((1400, 5480), (1400, 5590))), 0, 0.9, BLACK, 10,
  sfx="wood_low")
L(join(*[join(stick(x, 5600, 0.7), face(x, 5600, 0.7, "smile")) for x in (560, 760, 960)]), 1, 1.9, BLACK, 9,
  sfx="pop")
L(join(stick(1280, 5600, 0.7, hair=True), face(1280, 5600, 0.7, "flat")), 2, 2.8, BLUE, 9, sfx="wood_high")
L(bag(1120, 5478), 3, 3.8, RED, 9, sfx="pop")
L(bubble(760, 5150, 480, 150, -1), 4, 4.4, BLACK, 8, sfx="pop")
T("这包多少钱？", 760, 5150, 58, k0=4.4, k1=5.9)
T("没人问她过得咋样", 950, 5760, 64, RED, k0=6, k1=8, sfx="rim")

# ---------------------------------------------------------------- 三个做法（场景 11–13）

scene("买之前问一句", "第一步 · 买前问", (2650, 5300, 0.85))
T("① 买前问一句", 2650, 4870, 72, BLUE, k0=0, k1=1.75, sfx="pop")
L(cart(), 2, 2.9, BLACK, 9, sfx="wood_high")
L(rect(2700, 5250, 160, 110, 10), 3, 3.6, RED, 8, sfx="pop")
L(join(stick(2300, 5600, 0.8, "point"), face(2300, 5600, 0.8, "flat")), 4, 4.8, BLUE, 9, sfx="wood_high")
L(bubble(2700, 5060, 560, 210, -1), 5, 5.4, BLACK, 8, sfx="pop")
T("给自己用？", 2700, 5010, 60, k0=5.4, k1=6.7)
T("给别人看？", 2700, 5110, 60, RED, k0=7, k1=8, sfx="rim")

scene("想被喜欢，先对人好", "第二步 · 对人好", (2650, 6750, 0.85))
T("② 先对人好", 2650, 6320, 72, BLUE, k0=0, k1=1.5, sfx="pop")
L(join(stick(2350, 7050, 0.8, "up"), face(2350, 7050, 0.8, "smile")), 2, 2.9, BLUE, 9, sfx="wood_high")
L(join(rect(2350, 6730, 220, 130, 8), P((2240, 6700), (2460, 6700))), 3, 3.8, BLACK, 9, sfx="pop")
L(join(stick(2900, 7050, 0.8, hair=True), face(2900, 7050, 0.8, "smile")), 4, 4.8, BLACK, 9, sfx="wood_high")
L(bubble(3060, 6480, 260, 120, -1), 5, 5.4, BLACK, 8, sfx="pop")
T("谢啦！", 3060, 6480, 60, k0=5.4, k1=6.2)
L(heart(2900, 6690, 38), 6, 6.8, RED, 9, sfx="ding")
T("记住的是你", 2650, 7190, 70, GREEN, k0=7, k1=8, sfx="pop")

j_note = scene("把没买的记下来", "第三步 · 没买清单", (950, 6750, 0.85))
T("③ 记下没买的", 950, 6320, 72, BLUE, k0=0, k1=1.75, sfx="pop")
L(notebook(700, 6800), 1, 1.8, BLACK, 8, sfx="wood_high")
T("这个月没买：", 700, 6630, 56, k0=2, k1=3, sfx="pop")
T("· 新外套", 700, 6760, 56, k0=3, k1=3.8)
T("· 新球鞋", 700, 6890, 56, k0=4, k1=4.8, sfx="pop")
C(pig_fn(1260, 6900, 0.9, grow_at=(j_note, 7)), 5, 5.9, sfx="wood_high")
C(coin_drop_fn(1260, 6600, 6835), 6, 6.6, sfx="ding")
H(7, "tom", 0.8, "小猪罐胖一圈")
T("胖了一圈", 1260, 7150, 64, GREEN, k0=7, k1=8)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FULL = (1800, 4400, 0.115)
END = (1800, 8200, 0.8)
scene("为面子买过啥？", "评论区见", FULL, bars=4)
J_END = J()
b.move(J_END, 4, END, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
C(pig_fn(1270, 8230, 0.8, "sweat"), 5, 5.8, sfx="pop")
T("你为面子买过啥？", 1900, 8130, 76, RED, k0=6, k1=8, sfx="pop")
T("下一讲：没想好买什么，也要存钱？", 1850, 8300, 50, k0=9, k1=13, sfx="wood_high")
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "car", "豪车悖论", "开豪车的人，你记住他了吗？", ACC, b.shots,
                 [f"{BOOK}第 8 章“豪车悖论”、第 9 章“财富是你看不见的那些”（转述）",
                  "中译本：《金钱心理学：财富、人性和幸福的永恒真相》，李青宗译，民主与建设出版社 · 后浪 2023"],
                 "开豪车的人|你【记住他】了吗？", SQUARE_SHOT,
                 ["书中观点（转述）：第 8 章“豪车悖论”——作者年轻时在酒店当代客泊车员，发现看到豪车的人，想的是自己要是开上它，"
                  "别人会多佩服自己，几乎没人留意开车的人；想被尊重和佩服，靠的是善良和谦逊，跟车没关系。第 9 章“财富是你看不见的"
                  "那些”——看得见的豪车、名表是花掉的钱，财富是没花出去、别人看不见的那部分。上屏均为转述，不当原话引用。",
                  "开局的豪车、路人、三个选项卡（车主真厉害 / 这车真帅 / 我要是有……）、天平、停车场与空车位均为示意；"
                  "车、包都不画任何品牌标志，不指向任何具体公司或个人。",
                  "同学会上大家只盯着一只包为示意；三个做法（买前问一句“给自己用还是给别人看”、先对人好、把没买的记下来）"
                  "为据书中思路整理，不是投资或消费建议。"],
                 tags="#消费 #面子")
    return b.attach(ep)
