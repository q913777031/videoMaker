"""03 调节回路（白板手绘版）：减肥为什么总会反弹？

叙事：打工人切身问题开局（过完年胖了十斤，不吃晚饭一个月瘦八斤，项目一忙奶茶夜宵全回来，两个月胖回原样）→
书中观点（恒温器：冷了就烧暖气、到了就停；热咖啡凉到室温，差距越小降得越慢；画成一张调节回路图：现状和目标一比，
有差距就动手；想稳在新水平，得改回路的目标）→ 身边的例子（工位周一收拾周五堆满、六点起床三天就破功、
爸妈一走孩子就停笔、删了短视频三天又装回来；每次都在硬扛，目标一个没改）→ 具体做法（找到自己的设定值 /
把线往下挪 / 一次只挪一点 / 天天看现状）→ 评论区互动。
书中观点为转述（Meadows, Thinking in Systems, 2008；中译本《系统之美》，邱昭良译，浙江人民出版社 2012）；
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, clock, cross, desk, doc,
                               face, hands_at, join, marker, node, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#3E8A6E"
SQUARE_SHOT = 16

b = Board(size=(3600, 10000))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲小画法

def dash(x0, x1, y, seg=46, gap=26) -> skia.Path:
    parts, x = [], x0
    while x < x1:
        parts.append(P((x, y), (min(x + seg, x1), y)))
        x += seg + gap
    return join(*parts)


def wave_up(x, y0, y1, amp=16, n=3) -> skia.Path:
    """竖向波浪线（热气、暖气），从 y0 画到 y1。"""
    p = skia.Path()
    p.moveTo(x, y0)
    step = (y1 - y0) / (n * 2)
    for i in range(n * 2):
        yy = y0 + step * i
        p.quadTo(x + (amp if i % 2 == 0 else -amp), yy + step / 2, x, yy + step)
    return p


def wave_side(x0, x1, y, amp=14, n=3) -> skia.Path:
    """横向波浪线（冷风）。"""
    p = skia.Path()
    p.moveTo(x0, y)
    step = (x1 - x0) / (n * 2)
    for i in range(n * 2):
        xx = x0 + step * i
        p.quadTo(xx + step / 2, y + (amp if i % 2 == 0 else -amp), xx + step, y)
    return p


def scale_pad(x, y, w=320, h=70) -> skia.Path:
    """体重秤：(x, y) 为秤面中点。"""
    return join(rect(x, y, w, h, 16), rect(x, y, w * 0.34, h * 0.55, 6))


def bowl(x, y, w=300) -> skia.Path:
    """饭碗 + 筷子：(x, y) 为碗口中点。"""
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.cubicTo(x - w / 2, y + w * 0.45, x + w / 2, y + w * 0.45, x + w / 2, y)
    return join(P((x - w / 2 - 10, y), (x + w / 2 + 10, y)), p, P((x - 40, y + w * 0.34), (x + 40, y + w * 0.34)),
                P((x + 20, y - 10), (x + 150, y - 150)), P((x + 50, y - 5), (x + 175, y - 135)))


def thermostat(x, y) -> skia.Path:
    return join(rect(x, y, 300, 380, 30), rect(x, y - 70, 220, 120, 12), circle(x - 50, y + 150, 18),
                circle(x + 50, y + 150, 18))


def radiator(x, y, w=260, h=180) -> skia.Path:
    parts = [rect(x, y, w, h, 18)]
    for i in range(1, 5):
        xx = x - w / 2 + w * i / 5
        parts.append(P((xx, y - h / 2 + 22), (xx, y + h / 2 - 22)))
    parts += [P((x - w / 2 + 30, y + h / 2), (x - w / 2 + 30, y + h / 2 + 30)),
              P((x + w / 2 - 30, y + h / 2), (x + w / 2 - 30, y + h / 2 + 30))]
    return join(*parts)


def cup(x, y) -> skia.Path:
    """咖啡杯：(x, y) 为杯身中点。"""
    return join(P((x - 110, y - 120), (x - 80, y + 130), (x + 80, y + 130), (x + 110, y - 120), close=True),
                P((x - 100, y - 60), (x - 160, y - 50), (x - 160, y + 40), (x - 90, y + 60)),
                P((x - 160, y + 155), (x + 160, y + 155)))


def cool_curve(x0=2470, x1=3230, top=2650, room=3150) -> skia.Path:
    pts = []
    for i in range(41):
        x = x0 + (x1 - x0) * i / 40
        pts.append((x, room - (room - top) * math.exp(-4 * i / 40)))
    return P(*pts)


def phone(x, y, w=240, h=420) -> skia.Path:
    return join(rect(x, y, w, h, 30), P((x - 30, y + h / 2 - 30), (x + 30, y + h / 2 - 30)))


def app_icon(x, y, s=90) -> skia.Path:
    return join(rect(x, y, s, s, 20), P((x - s * 0.15, y - s * 0.22), (x + s * 0.25, y), (x - s * 0.15, y + s * 0.22),
                                        close=True))


def eye(x, y, w=200, h=100) -> skia.Path:
    up, lo = skia.Path(), skia.Path()
    up.moveTo(x - w / 2, y)
    up.quadTo(x, y - h, x + w / 2, y)
    lo.moveTo(x - w / 2, y)
    lo.quadTo(x, y + h, x + w / 2, y)
    return join(up, lo, circle(x, y, h * 0.3))


def stairs(x, y, n=4, w=115, h=95) -> skia.Path:
    pts = [(x, y)]
    for i in range(n):
        pts += [(x + w * (i + 1), y + h * i), (x + w * (i + 1), y + h * (i + 1))]
    return P(*pts)


def reading_fn(x, y, j_drop, j_back):
    """恒温器读数：平时 22 度；第 9 镜开窗骤降到 16 度；第 10 镜两拍内升回 22 度。"""

    def fn(c, k, t):
        if t < b.t_of(j_drop, 0):
            v, col = 22, BLACK
        elif t < b.t_of(j_back, 0):
            v, col = 16, BLUE
        else:
            f = clamp01((t - b.t_of(j_back, 0)) / (b.t_of(j_back, 2) - b.t_of(j_back, 0)))
            v = round(16 + 6 * ease_out(f))
            col = BLUE if v < 22 else GREEN
        K.text(c, f"{v}度", x, y, 84, "hand", col)
        return None

    return fn


def label_box(x, y, s, size, w, h):
    """白底红框便签，弹出后写着大红字。"""

    def fn(c, k, t):
        q = ease_out(clamp01(k))
        if q <= 0:
            return None
        K.rr(c, x, y, w * q, h * q, 30, "#FBFBF9")
        c.drawPath(rect(x, y, w * q, h * q, 30), marker(RED, 9))
        K.text(c, s, x, y, size * q, "hand", RED)
        return None

    return fn


# ---------------------------------------------------------------- 开局：减肥反弹（镜头 1–6）

b.shot("过完年胖了十斤", "灵魂拷问", view=(950, 1000, 0.85))
L(stick(750, 1285, 0.85, "down"), 0, 0.6, sfx="wood_high")
L(face(750, 1285, 0.85, "sad"), 0.6, 0.75)
L(scale_pad(750, 1320), 0.75, 1.0)
T("过完年", 1250, 850, 64, k0=1, sfx="pop")
T("150斤", 1250, 1000, 110, RED, k0=2, sfx="pop")
L(arrow((1150, 1080), (900, 1290), 0.15, 36), 3, 3.4, RED, 8)

b.shot("晚饭不吃了", "灵魂拷问", view=(950, 1000, 0.85))
L(bowl(1250, 1290), 0, 0.7, sfx="wood_high")
L(cross(1250, 1340, 110), 1, 1.35, RED, 12, sfx="rim")
T("饿着睡", 1250, 1180, 60, k0=2, sfx="pop")

b.shot("一个月瘦了八斤", "灵魂拷问", view=(2650, 1000, 0.85))
L(P((2150, 620), (2150, 1350), (3250, 1350)), 0, 0.6, sfx="wood_low")
T("150", 2220, 690, 54, k0=0.6, k1=0.9)
down = skia.Path()
down.moveTo(2220, 750)
down.cubicTo(2350, 760, 2500, 1150, 2650, 1150)
L(down, 1, 1.8, GREEN, 10, sfx="wood_high")
T("瘦了8斤", 2420, 1110, 58, GREEN, k0=2, sfx="pop")
T("142", 2650, 1220, 60, GREEN, k0=2.9, k1=3.3)

b.shot("项目一忙就破功", "灵魂拷问", view=(2650, 1050, 0.85))
for n, w in enumerate(("奶茶", "夜宵", "火锅")):
    T(w, 2350 + n * 300, 1460, 62, RED, k0=n, sfx="pop")

b.shot("两个月全胖回来", "灵魂拷问", view=(2650, 1000, 0.85), shake=[2])
up = skia.Path()
up.moveTo(2650, 1150)
up.cubicTo(2800, 1150, 2950, 720, 3150, 700)
L(up, 0, 1.6, RED, 11, sfx="shaker")
T("151", 3190, 630, 64, RED, k0=2, sfx="tom")

b.shot("怎么又弹回来了", "灵魂拷问", view=(1800, 1250, 0.42), flashes=[0])
T("？", 1800, 1480, 360, RED, k0=0, k1=0.6, sfx="kick")
T("又弹回来了", 1800, 1790, 110, k0=1, k1=2, sfx="pop")
b.hit(J(), 2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "系统之美", view=(800, 2850, 0.9))
L(book(520, 2850, 380, 260), 0, 1.0, sfx="wood_low")
T("系统之美", 520, 2620, 76, GREEN, k0=1, sfx="pop")
T("德内拉 · 梅多斯", 520, 3090, 46, k0=2, sfx="pop")

j_set = b.shot("家里的恒温器", "书中例子 · 恒温器", view=(1200, 2880, 0.85))
L(thermostat(1150, 2800), 0, 0.8, sfx="wood_high")
b.custom(j_set, 1, 12, reading_fn(1150, 2730, j_set + 1, j_set + 2), sfx="pop")
T("设定 22度", 1150, 2880, 48, k0=2, sfx="pop")
L(radiator(1550, 3080), 3, 3.7, BLACK, 8)

j_drop = b.shot("一冷，它就烧暖气", "书中例子 · 恒温器", view=(1200, 2880, 0.85), shake=[0], flashes=[0])
b.hit(j_drop, 0, "kick", 1.0, "骤冷")
for n in range(3):
    L(wave_side(760, 960, 2660 + n * 80), n * 0.12, n * 0.12 + 0.4, BLUE, 7)
T("冷！", 860, 2560, 90, BLUE, k0=0, k1=0.3)
for n in range(3):
    L(wave_up(1480 + n * 70, 2960, 2820), 1 + n * 0.12, 1.4 + n * 0.12, RED, 7, sfx="tom" if n == 0 else None)
T("加热", 1550, 3240, 60, RED, k0=2, sfx="pop")

j_back = b.shot("到了就自己停", "书中例子 · 恒温器", view=(1200, 2880, 0.85))
b.hit(j_back, 0, "shaker", 0.6, "升温")
b.hit(j_back, 1, "shaker", 0.6, "升温")
L(check(1370, 2700, 40), 2, 2.3, GREEN, 10, sfx="ding")
b.erase(j_back, 2.4, 3.0, 1550, 2890, 280, 190)

b.shot("热咖啡放桌上", "书中例子 · 咖啡", view=(2650, 2900, 0.85))
L(cup(2250, 3020), 0, 0.8, sfx="wood_high")
for n in range(3):
    L(wave_up(2200 + n * 50, 2870, 2720, 12), 1 + n * 0.15, 1.4 + n * 0.15, BLACK, 6, sfx="shaker" if n == 0 else None)
T("80度", 2250, 2640, 70, RED, k0=2, sfx="pop")

b.shot("慢慢凉到室温", "书中例子 · 咖啡", view=(2650, 2900, 0.85))
L(P((2450, 2620), (2450, 3300), (3250, 3300)), 0, 0.5, sfx="wood_low")
L(dash(2450, 3250, 3150), 1, 1.4, BLUE, 6, sfx="pop")
T("室温", 3150, 3225, 48, BLUE, k0=1.4, k1=1.8)
L(cool_curve(), 2, 3.8, RED, 10, sfx="shaker")

b.shot("差距越小越慢", "书中例子 · 咖啡", view=(2650, 2900, 0.85))
L(arrow((2560, 2862), (2560, 3132), 0, 30), 0, 0.4, RED, 8, sfx="pop")
T("差距大", 2720, 2780, 50, RED, k0=0.5)
T("降得快", 2720, 2845, 50, k0=1.1)
L(P((3000, 3124), (3000, 3146)), 2, 2.2, RED, 10, sfx="pop")
T("差距小", 3080, 2960, 50, RED, k0=2.3)
T("降得慢", 3080, 3025, 50, k0=2.9)

LOOP = dict(goal=(2200, 3480), now=(1400, 3820), gap=(2200, 3820), act=(1800, 4230))
LV = (1780, 3900, 0.8)
b.shot("这就是调节回路", "书中观点 · 调节回路", view=LV)
T("调节回路", 1450, 3480, 90, GREEN, k0=0, sfx="pop")
L(node(*LOOP["now"], 90), 1, 1.4, sfx="wood_high")
T("现状", *LOOP["now"], 56, k0=1.4, k1=1.8)
L(node(*LOOP["goal"], 90), 2, 2.4, RED, 10, sfx="wood_high")
T("目标", *LOOP["goal"], 56, RED, k0=2.4, k1=2.8)
T("22度", 1960, 3480, 56, k0=3.0, k1=3.4)

b.shot("比比现状和目标", "书中观点 · 调节回路", view=LV)
L(arrow((1500, 3820), (2100, 3820), 0.06, 40), 0, 0.5, BLACK, 8, sfx="wood_high")
L(arrow((2200, 3580), (2200, 3725), 0, 34), 0.5, 0.8, RED, 8)
L(node(*LOOP["gap"], 90), 1, 1.4, sfx="pop")
T("差距", *LOOP["gap"], 56, RED, k0=1.4, k1=1.8)
L(circle(*LOOP["gap"], 118), 2, 2.4, RED, 7, sfx="ding")

b.shot("有差距就动手", "书中观点 · 调节回路", view=LV)
L(arrow((2140, 3900), (1880, 4160), 0.08, 40), 0, 0.5, BLACK, 8, sfx="wood_high")
L(node(*LOOP["act"], 90), 1, 1.4, sfx="pop")
T("行动", *LOOP["act"], 56, k0=1.4, k1=1.8)
L(arrow((1720, 4160), (1460, 3900), 0.08, 40), 2, 2.5, GREEN, 9, sfx="wood_high")
T("拉回目标", 1800, 3990, 52, GREEN, k0=2.8, k1=3.5)

b.shot("要换水平，改目标", "书中观点 · 改目标", view=LV, shake=[1])
L(P((1888, 3480), (2032, 3480)), 0, 0.3, RED, 10, sfx="rim")
T("26度", 1960, 3610, 64, RED, k0=1, k1=1.4, sfx="kick")
L(stick(1235, 4390, 0.7, "point"), 2, 2.6, BLACK, 9, sfx="wood_high")
L(face(1235, 4390, 0.7, "smile"), 2.6, 2.75, BLACK, 7)

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5250), (2650, 5250), (950, 6250), (2650, 6250)]
b.shot("身边全是这种回路", "身边的例子", view=(1800, 5550, 0.42))
T("身边的回路", 1800, 4680, 120, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("周一收拾好工位", "例子 · 工位", view=(950, 5250, 0.85))
L(desk(780, 5330, 380), 0, 0.7, sfx="wood_high")
T("周一：整整齐齐", 950, 4980, 66, k0=1, sfx="pop")
L(check(1300, 5200, 50), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("周五又堆满了", "例子 · 工位", view=(950, 5250, 0.85))
for n in range(3):
    L(doc(660 + n * 90, 5245 - n * 20, 110, 140, 3), n * 0.2, n * 0.2 + 0.25, BLACK, 7, sfx="shaker" if n == 0 else None)
T("周五：又堆满", 950, 5560, 66, RED, k0=1, sfx="pop")
T("找不到才收", 1300, 5330, 52, k0=2, sfx="pop")

b.shot("定了六点起床", "例子 · 早起", view=(2650, 5250, 0.85))
L(clock(2350, 5230, 170), 0, 0.7, sfx="wood_low")
L(hands_at(2350, 5230, 170, 6, 0), 1, 1.3, RED, 12, sfx="pop")
T("6:00 起床", 2950, 5100, 70, k0=2, sfx="pop")

b.shot("三天后起不来", "例子 · 早起", view=(2650, 5250, 0.85))
T("还是一点睡", 2950, 5280, 60, RED, k0=0, sfx="pop")
L(P((2770, 5100), (3130, 5100)), 1, 1.3, RED, 10, sfx="rim")
T("8:30 才起", 2950, 5450, 60, k0=2, sfx="pop")

b.shot("盯着孩子写作业", "例子 · 写作业", view=(950, 6250, 0.85))
L(stick(600, 6560, 0.8, "point"), 0, 0.6, sfx="wood_high")
L(face(600, 6560, 0.8, "flat"), 0.6, 0.75)
L(stick(1000, 6560, 0.55), 1, 1.4, BLUE, 9, sfx="pop")
L(desk(1230, 6430, 240), 1.4, 1.9, BLACK, 8)
T("写作业", 1050, 5980, 66, k0=2, sfx="pop")

b.shot("一走开就停笔", "例子 · 写作业", view=(950, 6250, 0.85))
L(cross(600, 6400, 100), 0, 0.35, RED, 12, sfx="rim")
T("停", 1230, 6240, 80, RED, k0=1, sfx="pop")
T("爸妈一走就停", 950, 6640, 56, k0=2, sfx="pop")

b.shot("删了短视频", "例子 · 删软件", view=(2650, 6250, 0.85))
L(phone(2350, 6280), 0, 0.6, sfx="wood_high")
L(app_icon(2350, 6200), 1, 1.3, RED, 8, sfx="pop")
L(cross(2350, 6200, 75), 2, 2.3, RED, 11, sfx="rim")

b.shot("三天又装回来", "例子 · 删软件", view=(2650, 6250, 0.85))
L(arrow((2510, 6200), (2790, 6200), 0.1, 36), 0, 0.4, GREEN, 8, sfx="pop")
T("三天后", 2650, 6100, 52, k0=0.4)
L(join(phone(2950, 6280), app_icon(2950, 6200)), 1, 1.6, BLACK, 9, sfx="wood_high")
T("无聊就想刷", 2650, 6620, 56, k0=2, sfx="pop")

b.shot("每次都在硬扛", "身边的例子", view=(1800, 5850, 0.42))
T("每次都在硬扛", 1800, 6870, 110, k0=0, sfx="pop")
L(underline(1480, 2120, 6940), 2, 2.5, RED, 8, sfx="wood_low")

b.shot("目标一个没改", "身边的例子", view=(1800, 5850, 0.42), shake=[0])
b.custom(J(), 0, 0.35, label_box(1800, 5750, "目标没改", 130, 640, 200), sfx="kick", gain=1.0)
for n, (x, y) in enumerate(CARDS):
    dx, dy = x - 1800, y - 5750
    L(arrow((1800 + dx * 0.35, 5750 + dy * 0.35), (1800 + dx * 0.6, 5750 + dy * 0.6), 0.1, 40), 1 + n * 0.5,
      1.4 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 7850), (2650, 7850), (950, 8800), (2650, 8800)]
b.shot("想不反弹，这样做", "具体做法", view=(1800, 8300, 0.42))
T("想不反弹，这样做", 1800, 7300, 110, k0=0, k1=1.6, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1500, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先找你的设定值", "第一步 · 找设定值", view=(950, 7850, 0.85))
T("① 找设定值", 950, 7560, 80, BLUE, k0=0, sfx="pop")
L(P((450, 8120), (650, 7950), (800, 7808), (900, 7900), (1000, 7808), (1100, 7890), (1200, 7808), (1330, 7870)), 1,
  1.8, BLACK, 9, sfx="wood_high")
L(dash(450, 1330, 7800), 2, 2.4, RED, 7, sfx="pop")
T("150斤", 1450, 7800, 50, RED, k0=2.4, k1=2.8)

b.shot("到哪儿才着急", "第一步 · 找设定值", view=(950, 7900, 0.85))
T("到多少斤才着急？", 1010, 8030, 56, k0=0, sfx="pop")
T("这条线就是设定值", 1010, 8160, 56, RED, k0=2, sfx="pop")

b.shot("把线往下挪", "第二步 · 改设定值", view=(2650, 7850, 0.85))
T("② 改设定值", 2650, 7560, 80, BLUE, k0=0, sfx="pop")
L(dash(2200, 3000, 7760), 1, 1.4, BLACK, 7, sfx="wood_high")
T("150", 3100, 7760, 50, k0=1.4, k1=1.7)
L(dash(2200, 3000, 7880), 2, 2.4, RED, 8, sfx="pop")
T("145", 3100, 7880, 50, RED, k0=2.4, k1=2.7)
L(arrow((2140, 7760), (2140, 7880), 0, 28), 2.8, 3.1, GREEN, 8)

b.shot("超线就停夜宵", "第二步 · 改设定值", view=(2650, 7950, 0.85))
T("超过145斤：停夜宵", 2650, 8030, 60, k0=0, sfx="pop")
L(check(3040, 8030, 40), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("工位也这么定", "第二步 · 改设定值", view=(2650, 8000, 0.85))
T("桌上超三样：就收", 2650, 8160, 56, k0=0, sfx="pop")
L(check(3000, 8160, 40), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("一次只挪一点", "第三步 · 慢慢挪", view=(950, 8800, 0.85))
T("③ 一次挪一点", 950, 8510, 80, BLUE, k0=0, sfx="pop")
L(stairs(430, 8650), 1, 1.7, BLACK, 9, sfx="wood_high")
T("差距小，好坚持", 1250, 8680, 54, k0=2, sfx="pop")

b.shot("每月只减两斤", "第三步 · 慢慢挪", view=(950, 8850, 0.85))
T("每月减2斤", 1250, 8830, 60, k0=0, sfx="pop")
L(check(1480, 8830, 36), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("每周早睡十分钟", "第三步 · 慢慢挪", view=(950, 8900, 0.85))
T("每周早睡10分钟", 1230, 8980, 54, k0=0, sfx="pop")
L(check(1480, 8980, 36), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("天天看一眼现状", "第四步 · 看现状", view=(2650, 8800, 0.85))
T("④ 天天看现状", 2650, 8510, 80, BLUE, k0=0, sfx="pop")
L(eye(2330, 8680), 1, 1.6, BLACK, 9, sfx="wood_high")
T("差距早发现", 2850, 8680, 56, k0=2, sfx="pop")

b.shot("早上称一下", "第四步 · 看现状", view=(2650, 8850, 0.85))
L(scale_pad(2330, 8870, 240, 60), 0, 0.5, BLACK, 9, sfx="wood_high")
T("每天早上称", 2850, 8860, 56, k0=1, sfx="pop")
L(check(3060, 8860, 35), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("睡前定个提醒", "第四步 · 看现状", view=(2650, 8900, 0.85))
T("23:00 提醒睡觉", 2850, 9060, 54, k0=0, sfx="pop")
L(phone(2330, 9070, 100, 160), 1, 1.4, BLACK, 8, sfx="wood_high")
L(check(3110, 9060, 35), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("改目标，别硬扛", "一句话", view=(1800, 5300, 0.235))
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 9650, 0.8))
T("你被什么拉回去过？", 1800, 9560, 80, RED, k0=0.5, k1=1.8)
T("下一讲：为什么有人越学越快？", 1800, 9720, 46, k0=2.0, k1=3.2)
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 1, "pop")
b.hit(J(), 2, "wood_high", 0.7)
b.hit(J(), 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "balancing", "调节回路", "减肥为什么总会反弹？", ACC, b.shots,
                 [f"{BOOK}第一章 调节回路、热咖啡变凉（转述）", f"{BOOK}第二章 恒温器（转述）",
                  "中译本：邱昭良译，浙江人民出版社 2012"],
                 "减肥总反弹|是回路在【往回拉】", 16,
                 ["书中观点均为转述，不是原文引文：调节回路（平衡反馈回路）比较现状与目标，出现差距就采取行动缩小差距，"
                  "让系统稳在目标附近；书中例子有房间恒温器（低于设定温度就加热，到了就停）和一杯热咖啡凉到室温"
                  "（差距越小，变化越慢）；想让系统稳定在新的水平，要改回路的目标（设定值），光靠一次次用力推作用有限。"
                  "出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)，中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                  "减肥反弹、工位周一收拾周五堆满、六点起床三天破功、爸妈一走孩子停笔、删了短视频又装回来均为现实场景示意，"
                  "不指向具体个人或公司；体重曲线、温度读数、斤数均为示意数字，不代表真实数据。用调节回路解释减肥反弹是借书中概念打的比方，"
                  "不是医学结论；四步做法为据书中思路整理的建议，不构成减肥或医疗建议。"],
                 tags="#减肥 #习惯")
    return b.attach(ep)
