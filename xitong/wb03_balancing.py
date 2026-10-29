"""03 调节回路（白板手绘版）：减肥为什么总会反弹？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
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
SQUARE_SHOT = 8

b = Board(size=(3600, 11900))


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


def reading_fn(x, y, j):
    """恒温器读数：平时 22 度；场景 j 第 0 拍开窗骤降到 16 度，第 3–5 拍升回 22 度。"""

    def fn(c, k, t):
        if t < b.t_of(j, 0):
            v, col = 22, BLACK
        elif t < b.t_of(j, 3):
            v, col = 16, BLUE
        else:
            f = clamp01((t - b.t_of(j, 3)) / (b.t_of(j, 5) - b.t_of(j, 3)))
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


# ---------------------------------------------------------------- 开局：减肥反弹（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("胖了十斤，晚饭不吃", "灵魂拷问", (950, 1050, 0.85))
L(stick(750, 1285, 0.85, "down"), 0, 0.6, sfx="wood_high")
L(face(750, 1285, 0.85, "sad"), 0.6, 0.75)
L(scale_pad(750, 1320), 0.75, 1.0)
T("过完年", 1250, 850, 64, k0=1, k1=1.5, sfx="pop")
T("150斤", 1250, 1000, 110, RED, k0=2, k1=2.7, sfx="pop")
L(bowl(1250, 1290), 3, 3.7, sfx="wood_high")
L(cross(1250, 1340, 110), 4, 4.35, RED, 12, sfx="rim")
T("饿着睡", 1250, 1180, 60, k0=5, k1=5.6, sfx="pop")

GV = (2650, 1150, 0.72)
scene("瘦了八斤，又破功", "灵魂拷问", GV)
L(P((2150, 620), (2150, 1350), (3250, 1350)), 0, 0.6, sfx="wood_low")
T("150", 2230, 690, 60, k0=0.6, k1=0.9)
down = skia.Path()
down.moveTo(2220, 750)
down.cubicTo(2350, 760, 2500, 1150, 2650, 1150)
L(down, 1, 1.8, GREEN, 10, sfx="wood_high")
T("瘦了8斤", 2420, 1100, 62, GREEN, k0=2, k1=2.6, sfx="pop")
T("142", 2650, 1225, 64, GREEN, k0=2.6, k1=2.9)
for n, w in enumerate(("奶茶", "夜宵", "火锅")):
    T(w, 2250 + n * 250, 1480, 70, RED, k0=3 + n, k1=3.5 + n, sfx="pop")
L(P((2150, 1545), (2850, 1545)), 5.5, 5.9, RED, 6)

scene("两个月，又胖回来了", "灵魂拷问", GV, shake=[3], flashes=[3])
up = skia.Path()
up.moveTo(2650, 1150)
up.cubicTo(2800, 1150, 2950, 720, 3150, 700)
L(up, 0, 1.6, RED, 11, sfx="shaker")
T("151", 3190, 630, 70, RED, k0=2, k1=2.5, sfx="tom")
T("怎么又弹回来了？", 2500, 1700, 96, RED, k0=3, k1=4.4, sfx="kick")
L(circle(3190, 630, 85), 5, 5.5, RED, 7, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

TV = (1000, 2900, 0.74)
j_set = scene("书里讲了恒温器", "系统之美 · 书中例子", TV)
L(book(500, 2850, 320, 230), 0, 1.0, sfx="wood_low")
T("系统之美", 500, 2650, 70, GREEN, k0=1, k1=1.7, sfx="pop")
T("德内拉 · 梅多斯", 500, 3050, 42, k0=1.8, k1=2.6)
L(thermostat(1150, 2800), 3, 3.8, sfx="wood_high")
b.custom(j_set, 4, 16, reading_fn(1150, 2730, j_set + 1), sfx="pop")
T("设定 22度", 1150, 2880, 48, k0=5, k1=5.8, sfx="ding")

j_drop = scene("冷了就烧，到了就停", "书中例子 · 恒温器", TV, shake=[0], flashes=[0])
b.hit(j_drop, 0, "kick", 1.0, "骤冷 · drop")
for n in range(3):
    L(wave_side(720, 920, 2700 + n * 80), n * 0.12, n * 0.12 + 0.4, BLUE, 7)
T("冷！", 820, 2600, 90, BLUE, k0=0.5, k1=0.8)
L(radiator(1550, 3080), 1, 1.7, BLACK, 8, sfx="wood_high")
for n in range(3):
    L(wave_up(1480 + n * 70, 2960, 2820), 2 + n * 0.12, 2.4 + n * 0.12, RED, 7, sfx="tom" if n == 0 else None)
b.hit(j_drop, 3, "shaker", 0.6, "升温")
b.hit(j_drop, 4, "shaker", 0.6, "升温")
L(check(1370, 2700, 40), 5, 5.3, GREEN, 10, sfx="ding")
b.erase(j_drop, 5.3, 5.9, 1550, 2890, 280, 190)

scene("差距越小，凉得越慢", "书中例子 · 咖啡", (2650, 2950, 0.85))
L(cup(2250, 3020), 0, 0.8, sfx="wood_high")
for n in range(3):
    L(wave_up(2200 + n * 50, 2870, 2720, 12), 0.8 + n * 0.1, 1.1 + n * 0.1, BLACK, 6)
L(P((2450, 2620), (2450, 3300), (3250, 3300)), 1, 1.5, sfx="wood_low")
L(dash(2450, 3250, 3150), 1.5, 1.9, BLUE, 6)
T("室温", 3150, 3225, 48, BLUE, k0=1.9, k1=2.2)
L(cool_curve(), 2, 3.4, RED, 10, sfx="shaker")
L(arrow((2560, 2862), (2560, 3132), 0, 30), 3.5, 3.9, RED, 8)
T("差距大", 2720, 2780, 50, RED, k0=4, k1=4.4, sfx="pop")
T("降得快", 2720, 2845, 50, k0=4.4, k1=4.9)
L(P((3000, 3124), (3000, 3146)), 4.9, 5.0, RED, 10)
T("差距小", 3080, 2960, 50, RED, k0=5, k1=5.4, sfx="pop")
T("降得慢", 3080, 3025, 50, k0=5.4, k1=5.9)

LOOP = dict(goal=(2200, 3780), now=(1400, 4120), gap=(2200, 4120), act=(1800, 4530))
LV = (1780, 4200, 0.85)
scene("现状和目标一比", "书中观点 · 调节回路", LV)
T("调节回路", 1450, 3780, 90, GREEN, k0=0, k1=0.8, sfx="pop")
L(node(*LOOP["now"], 90), 1, 1.4, sfx="wood_high")
T("现状", *LOOP["now"], 56, k0=1.4, k1=1.8)
L(node(*LOOP["goal"], 90), 2, 2.4, RED, 10, sfx="wood_high")
T("目标", *LOOP["goal"], 56, RED, k0=2.4, k1=2.8)
T("22度", 1960, 3780, 56, k0=2.8, k1=3.0)
L(arrow((1500, 4120), (2100, 4120), 0.06, 40), 3, 3.5, BLACK, 8, sfx="wood_high")
L(arrow((2200, 3880), (2200, 4025), 0, 34), 3.5, 3.8, RED, 8)
L(node(*LOOP["gap"], 90), 4, 4.4, sfx="pop")
T("差距", *LOOP["gap"], 56, RED, k0=4.4, k1=4.8)
L(circle(*LOOP["gap"], 118), 5, 5.4, RED, 7, sfx="ding")

scene("有差距就动手", "书中观点 · 调节回路", LV)
L(arrow((2140, 4200), (1880, 4460), 0.08, 40), 0, 0.6, BLACK, 8, sfx="wood_high")
L(node(*LOOP["act"], 90), 2, 2.4, sfx="pop")
T("行动", *LOOP["act"], 56, k0=2.4, k1=2.8)
L(arrow((1720, 4460), (1460, 4200), 0.08, 40), 4, 4.6, GREEN, 9, sfx="wood_high")
T("拉回目标", 1800, 4290, 52, GREEN, k0=5, k1=5.7, sfx="ding")

scene("想换水平，改目标", "书中观点 · 改目标", LV, shake=[1])
L(P((1888, 3780), (2032, 3780)), 0, 0.3, RED, 10, sfx="rim")
T("26度", 1960, 3910, 64, RED, k0=1, k1=1.4, sfx="kick")
L(stick(1290, 4560, 0.6, "point"), 2, 2.6, BLACK, 9, sfx="wood_high")
L(face(1290, 4560, 0.6, "smile"), 2.6, 2.75, BLACK, 7)
L(circle(1960, 3910, 95), 4, 4.5, RED, 7, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 5860), (2650, 5860), (950, 7260), (2650, 7260)]
CV = (1800, 6560, 0.42)
scene("身边全是这种回路", "身边的例子", CV)
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1500, 900, 40), n, n + 0.6, GREEN, 8, sfx="wood_high" if n % 2 == 0 else None)
for n, ((x, y), w) in enumerate(zip(CARDS, ("工位", "早起", "作业", "手机"))):
    T(w, x - 530, y - 350, 70, BLUE, k0=4 + n * 0.5, k1=4.4 + n * 0.5, sfx="pop" if n % 2 == 0 else None)

scene("工位收了又乱", "例子 · 工位", (950, 5890, 0.85))
L(desk(780, 5940, 380), 0, 0.7, sfx="wood_high")
T("周一：整整齐齐", 950, 5590, 66, k0=1, k1=2, sfx="pop")
L(check(1300, 5810, 50), 2, 2.3, GREEN, 10, sfx="ding")
for n in range(3):
    L(doc(660 + n * 90, 5855 - n * 20, 110, 140, 3), 3 + n * 0.2, 3.25 + n * 0.2, BLACK, 7, sfx="shaker" if n == 0 else None)
T("周五：又堆满", 950, 6170, 66, RED, k0=4, k1=4.9, sfx="pop")
T("找不到才收", 1300, 5940, 52, k0=5, k1=5.8, sfx="wood_high")

scene("六点起床，三天破功", "例子 · 早起", (2650, 5880, 0.85))
L(clock(2350, 5840, 170), 0, 0.7, sfx="wood_low")
L(hands_at(2350, 5840, 170, 6, 0), 0.7, 1.0, RED, 12)
T("6:00 起床", 2950, 5710, 70, k0=1, k1=1.9, sfx="pop")
T("还是一点睡", 2950, 5890, 60, RED, k0=2.5, k1=3.4)
L(P((2770, 5710), (3130, 5710)), 4, 4.3, RED, 10, sfx="rim")
T("8:30 才起", 2950, 6060, 60, k0=5, k1=5.8, sfx="pop")
b.hit(J(), 3, "tom", 0.6)

scene("爸妈一走就停笔", "例子 · 写作业", (950, 7270, 0.85))
L(stick(600, 7570, 0.8, "point"), 0, 0.6, sfx="wood_high")
L(face(600, 7570, 0.8, "flat"), 0.6, 0.75)
L(stick(1000, 7570, 0.55), 1, 1.4, BLUE, 9, sfx="pop")
L(desk(1230, 7440, 240), 1.4, 1.9, BLACK, 8)
T("写作业", 1050, 6990, 66, k0=2, k1=2.6, sfx="pop")
L(cross(600, 7410, 100), 3.5, 3.85, RED, 12)
b.hit(J(), 4, "rim")
T("停", 1230, 7250, 80, RED, k0=4, k1=4.3)
T("爸妈一走就停", 950, 7650, 56, k0=5, k1=5.9, sfx="pop")

scene("删了又装回来", "例子 · 删软件", (2650, 7270, 0.85))
L(phone(2350, 7290), 0, 0.6, sfx="wood_high")
L(app_icon(2350, 7210), 0.7, 1.0, RED, 8)
L(cross(2350, 7210, 75), 1, 1.3, RED, 11, sfx="rim")
L(arrow((2510, 7210), (2790, 7210), 0.1, 36), 2, 2.4, GREEN, 8, sfx="pop")
T("三天后", 2650, 7110, 52, k0=2.4, k1=2.9)
L(join(phone(2950, 7290), app_icon(2950, 7210)), 3, 3.6, BLACK, 9, sfx="wood_high")
T("无聊就想刷", 2650, 7630, 56, k0=4.5, k1=5.4)
b.hit(J(), 5, "pop")

scene("每次硬扛，目标没改", "身边的例子", CV, shake=[0])
b.custom(J(), 0, 0.35, label_box(1800, 6560, "目标没改", 110, 560, 180), sfx="kick", gain=1.0)
for n, (x, y) in enumerate(CARDS):
    dx, dy = x - 1800, y - 6560
    L(arrow((1800 + dx * 0.36, 6560 + dy * 0.36), (1800 + dx * 0.6, 6560 + dy * 0.6), 0.1, 40), 1 + n * 0.5,
      1.4 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)
for n, (x, y) in enumerate(CARDS):
    T("硬扛", x + 350, y + 330, 64, RED, k0=4 + n * 0.4, k1=4.35 + n * 0.4, sfx="pop" if n == 0 else None)

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 8640), (2650, 8640), (950, 9970), (2650, 9970)]
scene("先找你的设定值", "第一步 · 找设定值", (950, 8670, 0.85))
L(rect(950, 8640, 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("① 找设定值", 950, 8350, 80, BLUE, k0=1, k1=1.8, sfx="pop")
L(P((450, 8910), (650, 8740), (800, 8598), (900, 8690), (1000, 8598), (1100, 8680), (1200, 8598), (1330, 8660)), 2,
  2.8, BLACK, 9, sfx="wood_high")
L(dash(450, 1330, 8590), 3, 3.4, RED, 7, sfx="pop")
T("150斤", 1450, 8590, 50, RED, k0=3.4, k1=3.8)
T("到多少斤才着急？", 1010, 8890, 60, k0=4, k1=5.4, sfx="ding")

scene("把线往下挪", "第二步 · 改设定值", (2650, 8670, 0.85))
L(rect(2650, 8640, 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("② 改设定值", 2650, 8350, 80, BLUE, k0=1, k1=1.8, sfx="pop")
L(dash(2200, 3000, 8550), 2, 2.4, BLACK, 7, sfx="wood_high")
T("150", 3100, 8550, 50, k0=2.4, k1=2.7)
L(dash(2200, 3000, 8670), 3, 3.4, RED, 8, sfx="pop")
T("145", 3100, 8670, 50, RED, k0=3.4, k1=3.7)
L(arrow((2140, 8550), (2140, 8670), 0, 28), 3.7, 4.0, GREEN, 8)
T("超过145斤：停夜宵", 2650, 8840, 60, k0=4, k1=5.3, sfx="pop")
L(check(3040, 8840, 40), 5.4, 5.7, GREEN, 10)

scene("一次只挪一点", "第三步 · 慢慢挪", (950, 10000, 0.85))
L(rect(950, 9970, 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("③ 一次挪一点", 950, 9680, 80, BLUE, k0=1, k1=1.9, sfx="pop")
L(stairs(430, 9820), 2, 2.7, BLACK, 9, sfx="wood_high")
T("差距小，好坚持", 1250, 9850, 54, k0=3, k1=4.1, sfx="pop")
T("每月减2斤", 1250, 10050, 60, k0=4.3, k1=5.0)
L(check(1480, 10050, 36), 5, 5.3, GREEN, 10, sfx="ding")

scene("天天看一眼现状", "第四步 · 看现状", (2650, 10000, 0.85))
L(rect(2650, 9970, 1500, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("④ 天天看现状", 2650, 9680, 80, BLUE, k0=1, k1=1.9, sfx="pop")
L(eye(2330, 9850), 2, 2.6, BLACK, 9, sfx="wood_high")
T("差距早发现", 2850, 9850, 56, k0=2.6, k1=3.4)
L(scale_pad(2330, 10070, 240, 60), 3.5, 3.9, BLACK, 9)
T("每天早上称", 2850, 10060, 56, k0=4, k1=4.8, sfx="pop")
L(check(3060, 10060, 35), 5, 5.3, GREEN, 10, sfx="ding")

scene("改目标，别硬扛", "一句话", (1800, 5700, 0.235))
b.hit(J(), 0, "cymbal", 0.5)
b.hit(J(), 2, "wood_high", 0.6)
b.hit(J(), 4, "ding")

scene("评论区聊聊", "评论区见", (1800, 11400, 0.8))
b.hit(J(), 0, "cymbal", 0.5)
T("你被什么拉回去过？", 1800, 11310, 80, RED, k0=1, k1=2.6)
b.hit(J(), 1, "pop")
T("下一讲：为什么有人越学越快？", 1800, 11470, 46, k0=3, k1=4.5)
b.hit(J(), 3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "balancing", "调节回路", "减肥为什么总会反弹？", ACC, b.shots,
                 [f"{BOOK}第一章 调节回路、热咖啡变凉（转述）", f"{BOOK}第二章 恒温器（转述）",
                  "中译本：邱昭良译，浙江人民出版社 2012"],
                 "减肥总反弹|是回路在【往回拉】", 8,
                 ["书中观点均为转述，不是原文引文：调节回路（平衡反馈回路）比较现状与目标，出现差距就采取行动缩小差距，"
                  "让系统稳在目标附近；书中例子有房间恒温器（低于设定温度就加热，到了就停）和一杯热咖啡凉到室温"
                  "（差距越小，变化越慢）；想让系统稳定在新的水平，要改回路的目标（设定值），光靠一次次用力推作用有限。"
                  "出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)，中译本《系统之美》（邱昭良译，浙江人民出版社 2012）。",
                  "减肥反弹、工位周一收拾周五堆满、六点起床三天破功、爸妈一走孩子停笔、删了短视频又装回来均为现实场景示意，"
                  "不指向具体个人或公司；体重曲线、温度读数、斤数均为示意数字，不代表真实数据。用调节回路解释减肥反弹是借书中概念打的比方，"
                  "不是医学结论；四步做法为据书中思路整理的建议，不构成减肥或医疗建议。"],
                 tags="#减肥 #习惯")
    return b.attach(ep)
