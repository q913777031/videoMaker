"""05 专注（白板手绘版）：忙了一整天，正事一件没干？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 G 倒叙）：先给结局（晚上十点工位灯还亮着，报告只写了个标题）→ 挂钟倒转、时间线往回拉到早上九点 →
drop：一整天开着二十个窗口、三个群 → 回放（九点刚写一行就点开群；两点人在会议室心在外卖）→
书中观点（亮书；身心合一：身体在做什么，注意力就在什么上；做 A 时只做 A，做 B 时只做 B；身体感受是回到当下的入口；
想不出先放下，回头常有思路）→ 用书里的办法把这一天重来一遍（上午关群写报告、下午集中回消息）→
晚上六点报告写完，宝宝的舵上多一道握痕 → 评论区互动。
书中观点为转述（周岭《认知觉醒》第四章 专注力：第一节 情绪专注、第二节 学习专注）；
小林的一天、关掉消息、双手放桌上数三次呼吸、卡住就去倒杯水均为示意，据书中思路整理。
"""

import math
import random

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, circle, clock, cross, desk,
                               doc, face, hands_at, join, marker, partial, rect, stick, underline)

from .common import BOOK, episode

ACC = "#3E7CB1"
SQUARE_SHOT = 3                 # 场景 4：晚上十点的屏幕，一堆窗口压着，报告只有标题

b = Board(size=(3600, 11700))


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

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def desk_lamp(x, y, s=1.0) -> skia.Path:
    """台灯：(x, y) 为底座中点（桌面上）。"""
    shade = P((x + 110 * s, y - 380 * s), (x + 230 * s, y - 330 * s), (x + 300 * s, y - 190 * s),
              (x + 120 * s, y - 250 * s), close=True)
    return join(rect(x, y - 15 * s, 170 * s, 30 * s, 10 * s),
                P((x, y - 30 * s), (x + 70 * s, y - 230 * s), (x + 165 * s, y - 315 * s)), circle(x + 70 * s, y - 230 * s, 12 * s),
                shade)


def lamp_rays(x, y, s=1.0) -> skia.Path:
    return join(*[P((x + a * s, y - 170 * s), (x + c * s, y - 60 * s)) for a, c in ((200, 230), (250, 320), (150, 140))])


def glow_fn(x, y, r, color="#F2C14E", alpha=0.35):
    def fn(c, k, t):
        K.dot(c, x, y, r * ease_out(k), color, alpha)
        return None
    return fn


def monitor(x, y, w, h) -> skia.Path:
    """显示器：(x, y) 为屏幕中心，带支架与底座。"""
    return join(rect(x, y, w, h, 18), P((x, y + h / 2), (x, y + h / 2 + 90)),
                P((x - 150, y + h / 2 + 95), (x + 150, y + h / 2 + 95)))


def cursor_fn(x, y, h=56):
    def fn(c, k, t):
        if int(t * 2.4) % 2 == 0:
            c.drawPath(P((x, y - h / 2), (x, y + h / 2)), marker(BLUE, 7))
        return None
    return fn


def spin_fn(x, y, r, h0=22.0, h1=9.0):
    """挂钟指针倒转：从 h0 点逆时针转到 h1 点，转动时分针后面拖一道残影。"""
    def fn(c, k, t):
        e = ease_in_out(k)
        hrs = h0 + (h1 - h0) * e
        hh, mm = int(hrs), (hrs - int(hrs)) * 60
        if 0 < k < 1:
            a = -90 + mm / 60 * 360
            trail = skia.Path()
            trail.addArc(skia.Rect.MakeXYWH(x - r * 0.62, y - r * 0.62, r * 1.24, r * 1.24), a, 70)
            c.drawPath(trail, K.paint(RED, 0.35, 10))
        c.drawPath(hands_at(x, y, r, hh, mm), marker(BLACK, 12))
        K.dot(c, x, y, 12, BLACK)
        return None
    return fn


def rewind(x, y, s=1.0) -> skia.Path:
    return join(P((x, y - 60 * s), (x - 80 * s, y), (x, y + 60 * s), close=True),
                P((x + 85 * s, y - 60 * s), (x + 5 * s, y), (x + 85 * s, y + 60 * s), close=True))


def window_box(c, x, y, w, h, col, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    K.rr(c, 0, 0, w, h, 10, "#FFFFFF")
    K.rr(c, 0, -h / 2 + 20, w - 6, 34, 8, col, 0.28)
    c.drawPath(rect(0, 0, w, h, 10), marker(BLACK, 6))
    c.drawPath(P((-w / 2, -h / 2 + 40), (w / 2, -h / 2 + 40)), marker(BLACK, 4))
    for i in range(3):
        K.dot(c, -w / 2 + 22 + i * 22, -h / 2 + 20, 6, col)
    for i in range(2):
        yy = -h / 2 + 75 + i * 40
        c.drawPath(P((-w / 2 + 25, yy), (w / 2 - 40 - i * 40, yy)), marker(BLACK, 3, 0.5))
    c.restore()


_rng = random.Random(5)
WINS = []
for i in range(20):
    w, h = _rng.uniform(230, 330), _rng.uniform(150, 210)
    WINS.append((_rng.uniform(1990, 3110), _rng.uniform(700 + h / 2, 1210 - h / 2 * 0.3), w, h,
                 (BLUE, RED, GREEN, BLACK)[i % 4]))


def windows_fn(c, k, t):
    """二十个窗口依次“砸”上屏幕：每个窗口从 1.35 倍落到原大。"""
    n = len(WINS)
    for i, (x, y, w, h, col) in enumerate(WINS):
        a = i / n * 0.92
        if k < a:
            break
        f = clamp01((k - a) / 0.08)
        window_box(c, x, y, w, h, col, 1 + 0.35 * (1 - ease_out(f)))
    return None


GROUPS = [(3160, 760), (3160, 930), (3160, 1100)]


def groups_fn(c, k, t):
    """三个群的消息气泡（白底，压在窗口上）。"""
    for i, (x, y) in enumerate(GROUPS):
        if k < i / 3:
            break
        p = bubble(x, y, 200, 120, 1)
        c.drawPath(p, K.paint("#FFFFFF"))
        c.drawPath(p, marker(BLACK, 6))
        K.text(c, "群", x - 20, y + 16, 52, "hand", BLACK)
        K.dot(c, x + 80, y - 55, 22, RED)
    return None


def thought(x, y, w, h, fx, fy) -> skia.Path:
    """想法泡泡：云朵 (x, y, w, h) + 两个小圆点连到 (fx, fy)。"""
    p = oval(x, y, w, h)
    parts = [p]
    for f, r in ((0.35, 14), (0.65, 20)):
        parts.append(circle(fx + (x - w * 0.3 - fx) * f, fy + (y + h * 0.35 - fy) * f, r))
    return join(*parts)


def noodles(x, y, r=55) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r * 0.9, 2 * r, 1.8 * r), 0, 180)
    return join(p, P((x - r - 10, y), (x + r + 10, y)), P((x + 10, y - 10), (x + 70, y - 90)),
                P((x + 30, y - 6), (x + 92, y - 78)))


def bust(x, y, r=40) -> skia.Path:
    """会议桌后的半身：(x, y) 为头心。"""
    sh = skia.Path()
    sh.addArc(skia.Rect.MakeXYWH(x - r * 2.2, y + r * 1.1, r * 4.4, r * 3), 180, 180)
    return join(circle(x, y, r), sh)


def dashed_fn(path, color=BLUE, width=9):
    """虚线描出的路径（飘走的“心”），返回笔尖。"""
    def fn(c, k, t):
        part, tip = partial(path, k)
        pt = marker(color, width)
        pt.setPathEffect(skia.DashPathEffect.Make([24, 18], 0))
        c.drawPath(part, pt)
        return tip
    return fn


def stretch(a, z, n=9, amp=26) -> skia.Path:
    """两点之间一根被拉长的波浪线。"""
    (x0, y0), (x1, y1) = a, z
    dx, dy = x1 - x0, y1 - y0
    ln = (dx * dx + dy * dy) ** 0.5
    nx, ny = -dy / ln, dx / ln
    p = skia.Path()
    p.moveTo(x0, y0)
    for i in range(n):
        f0, f1 = (i + 0.5) / n, (i + 1) / n
        s = amp if i % 2 == 0 else -amp
        p.quadTo(x0 + dx * f0 + nx * s, y0 + dy * f0 + ny * s, x0 + dx * f1, y0 + dy * f1)
    return p


def phone(x, y, w=90, h=150) -> skia.Path:
    return join(rect(x, y, w, h, 14), P((x - 14, y + h / 2 - 20), (x + 14, y + h / 2 - 20)))


def rudder(x, y, r=140) -> skia.Path:
    """船舵：轮圈 + 轮毂 + 八根辐条伸出把手。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.22)]
    for i in range(8):
        a = i / 8 * 2 * math.pi
        parts.append(P((x + math.cos(a) * r * 0.22, y + math.sin(a) * r * 0.22),
                       (x + math.cos(a) * r * 1.28, y + math.sin(a) * r * 1.28)))
        parts.append(circle(x + math.cos(a) * r * 1.33, y + math.sin(a) * r * 1.33, r * 0.07))
    return join(*parts)


def grips(x, y, r, idx) -> skia.Path:
    """舵圈上的握痕：idx 为第几道（从 0 起），每道是轮圈外侧一小段短横。"""
    parts = []
    for i in idx:
        a = (-90 + 22.5 + i * 45) / 180 * math.pi
        for d in (-0.12, 0.0, 0.12):
            b0 = a + d
            parts.append(P((x + math.cos(b0) * r * 0.86, y + math.sin(b0) * r * 0.86),
                           (x + math.cos(b0) * r * 1.14, y + math.sin(b0) * r * 1.14)))
    return join(*parts)


def palm(x, y, s=1.0, side=1) -> skia.Path:
    """平放在桌上的手（俯视）：掌心 + 四指 + 拇指，side=1 拇指朝右。"""
    parts = [rect(x, y + 30 * s, 120 * s, 130 * s, 45 * s)]
    for i in range(4):
        fx = x - 42 * s + i * 28 * s
        parts.append(P((fx, y - 35 * s), (fx, y - 115 * s + abs(i - 1.5) * 14 * s)))
    parts.append(P((x + side * 60 * s, y + 40 * s), (x + side * 115 * s, y - 20 * s)))
    return join(*parts)


def breath(x, y, r=55) -> skia.Path:
    return join(circle(x, y, r), circle(x, y, r * 0.5))


def dispenser(x, y) -> skia.Path:
    """饮水机：(x, y) 为地面中点。"""
    return join(rect(x, y - 190, 170, 380, 16), rect(x, y - 470, 110, 160, 34), P((x - 30, y - 390), (x + 30, y - 390)),
                P((x - 20, y - 250), (x + 20, y - 250)), P((x, y - 250), (x, y - 220)))


def cup(x, y, s=1.0) -> skia.Path:
    return P((x - 30 * s, y - 40 * s), (x - 22 * s, y + 40 * s), (x + 22 * s, y + 40 * s), (x + 30 * s, y - 40 * s))


def bulb(x, y, r=55) -> skia.Path:
    parts = [circle(x, y, r), P((x - r * 0.45, y + r * 1.0), (x + r * 0.45, y + r * 1.0)),
             P((x - r * 0.35, y + r * 1.25), (x + r * 0.35, y + r * 1.25)),
             P((x - r * 0.3, y + r * 0.2), (x, y - r * 0.25), (x + r * 0.3, y + r * 0.2))]
    for i in range(5):
        a = (-170 + i * 40) / 180 * math.pi
        parts.append(P((x + math.cos(a) * r * 1.35, y + math.sin(a) * r * 1.35),
                       (x + math.cos(a) * r * 1.8, y + math.sin(a) * r * 1.8)))
    return join(*parts)


def chat_icon(x, y, w=240, h=120) -> skia.Path:
    return join(bubble(x, y, w, h, -1), circle(x - 50, y, 9), circle(x, y, 9), circle(x + 50, y, 9))


def brothers(x, y) -> skia.Path:
    """脑内三兄弟里的两个哥哥：老大（拐杖）、老二（耳机）。x 为老大脚底横坐标，y 为脚底线；返回 (老大, 老二)。"""
    s = 0.55
    elder = join(stick(x, y, s, "down"), P((x + 30 * s * 2, y - 150 * s), (x + 70 * s, y)))
    ux = x + 190
    hy = y - 290 * s
    phones = skia.Path()
    phones.addArc(skia.Rect.MakeXYWH(ux - 55 * s, hy - 60 * s, 110 * s, 110 * s), 180, 180)
    uncle = join(stick(ux, y, s, "down"), phones, rect(ux - 55 * s, hy + 1 * s, 16 * s, 34 * s, 6 * s),
                 rect(ux + 55 * s, hy + 1 * s, 16 * s, 34 * s, 6 * s))
    return elder, uncle


# ---------------------------------------------------------------- 倒叙开局：先看结局（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("晚上十点", "倒叙 · 先看结局", (1000, 850, 0.85), bars=2)
L(P((420, 1150), (1580, 1150)), 0, 0.9, BLACK, 10, sfx="wood_high")
L(desk_lamp(620, 1150), 1, 1.9, BLACK, 9, sfx="wood_low")
L(clock(1250, 560, 150), 2, 2.8, BLACK, 9, sfx="wood_high")
L(hands_at(1250, 560, 150, 10, 0), 2.8, 3.3, BLACK, 11)
T("22:00", 1250, 800, 80, RED, k0=4, k1=5.25, sfx="pop")
b.custom(J(), 5, 5.8, glow_fn(860, 1000, 210), sfx="ding")
L(lamp_rays(620, 1150), 5, 5.8, "#E0A526", 7)

MON = (2550, 820, 1000, 620)
scene("报告还是空的", "倒叙 · 先看结局", (2550, 850, 0.85))
L(monitor(*MON), 0, 0.9, BLACK, 10, sfx="wood_high")
T("本周工作报告", 2550, 600, 64, k0=1, k1=2.5, sfx="pop")
L(P((2120, 650), (2980, 650)), 2.5, 3.0, BLACK, 5)
b.custom(J(), 3, 3.3, cursor_fn(2120, 720), sfx="pop")
T("正文：0 字", 2550, 1340, 66, RED, k0=4, k1=5.5, sfx="rim")
L(underline(2340, 2760, 1385, 10, 36), 6, 6.8, RED, 7, sfx="ding")

# ---------------------------------------------------------------- 倒带（场景 3）

CLK = (1850, 2350, 270)
scene("倒回早上九点", "倒叙 · 倒带", (1800, 2700, 0.52))
L(clock(*CLK), 0, 0.9, BLACK, 10, sfx="wood_low")
b.custom(J(), 1, 6, spin_fn(*CLK), sfx="rim")
H(2, "shaker")
H(3, "shaker", 0.6)
L(rewind(1100, 2350, 1.2), 2, 2.8, RED, 10)
L(arrow((2780, 3150), (850, 3150), 0.0, 60), 3, 4.4, BLACK, 10, sfx="wood_high")
T("22:00", 2700, 3290, 90, k0=4.4, k1=5.6)
T("14:00", 1900, 3290, 90, k0=5.6, k1=6.8)
T("9:00", 950, 3290, 96, RED, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- drop：一整天的屏幕（场景 4）

scene("二十个窗口", "回放 · 这一整天", (2550, 900, 0.72), shake=[0], flashes=[0])
b.custom(J(), 0, 2.6, windows_fn, sfx="kick")
H(1, "pop")
H(2, "pop")
T("20 个窗口", 2300, 420, 96, RED, k0=3, k1=4.5, sfx="pop")
b.custom(J(), 5, 5.9, groups_fn, sfx="wood_high")
T("3 个群", 3080, 420, 84, RED, k0=6, k1=7, sfx="pop")
L(underline(2080, 2520, 480, 12, 40), 7, 7.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 回放：上午、下午（场景 5–6）

scene("九点：写一行看群", "回放 · 上午九点", (950, 3550, 0.85))
L(arrow((950, 3345), (950, 3450), 0.0, 30), 0, 0.6, RED, 9, sfx="wood_high")
L(doc(700, 3700, 260, 320, 1), 1, 1.9, BLACK, 9, sfx="wood_low")
T("写了一行", 700, 3950, 58, k0=2, k1=3, sfx="pop")
L(bubble(1150, 3640, 250, 150, -1), 4, 4.7, BLACK, 9, sfx="pop")
T("工作群", 1150, 3660, 58, k0=4.7, k1=5.5)
T("99+", 1220, 3505, 54, RED, k0=6, k1=6.8, sfx="rim")
L(arrow((845, 3740), (1020, 3680), 0.25, 34), 7, 7.8, RED, 9, sfx="wood_high")

scene("两点：开会想外卖", "回放 · 下午两点", (1935, 3550, 0.85))
L(arrow((1900, 3345), (1900, 3450), 0.0, 30), 0, 0.6, RED, 9, sfx="wood_high")
L(oval(1900, 3860, 560, 130), 1, 1.8, BLACK, 9, sfx="wood_low")
L(join(bust(1690, 3720, 36), bust(2110, 3720, 36)), 2, 2.9, BLACK, 8, sfx="pop")
L(bust(1900, 3690, 44), 3, 3.8, BLUE, 9, sfx="wood_high")
T("开会中", 1900, 4010, 60, k0=4, k1=4.8, sfx="pop")
L(thought(2330, 3510, 290, 170, 1950, 3640), 5, 5.8, BLACK, 8, sfx="pop")
L(noodles(2310, 3520, 50), 6, 6.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 7–11）

scene("人在这，心在那", "书中观点 · 身心合一", (1000, 4950, 0.85))
L(desk(850, 5200, 360), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(650, 5360, 0.7, "down"), 1, 1.8, BLACK, 10, sfx="pop")
L(face(650, 5360, 0.7, "flat"), 1.8, 2.0, BLACK, 8)
T("身体在这", 560, 4850, 60, k0=2, k1=3, sfx="pop")
b.custom(J(), 3, 3.9, dashed_fn(stick(1350, 4950, 0.6, "up")), sfx="wood_high")
L(stretch((690, 5140), (1310, 4800)), 4, 4.9, RED, 7, sfx="rim")
L(phone(1520, 5150), 5, 5.7, RED, 9, sfx="pop")
T("心在那", 1380, 4565, 60, BLUE, k0=6, k1=6.8, sfx="pop")

scene("有本书讲过", "亮书 · 认知觉醒", (2600, 4950, 0.85))
L(book(2350, 5000, 440, 300), 0, 0.9, BLACK, 9, sfx="wood_low")
T("《认知觉醒》", 2350, 4720, 72, GREEN, k0=1, k1=2.5, sfx="pop")
T("周岭", 2350, 5270, 56, k0=3, k1=3.8, sfx="pop")
L(rudder(3000, 4930, 130), 4, 4.9, GREEN, 8, sfx="wood_high")
T("05", 3000, 5220, 80, RED, k0=5, k1=5.8, sfx="ding")
T("第四章 专注力", 2600, 4500, 56, k0=6, k1=7.5, sfx="pop")

scene("做这个只做这个", "书中观点 · 做A只做A", (1050, 6300, 0.85))
T("做 A 时只做 A", 1050, 5880, 72, BLUE, k0=0, k1=1.5, sfx="pop")
L(rect(750, 6320, 480, 460, 20), 2, 2.8, BLACK, 9, sfx="wood_high")
L(doc(780, 6360, 220, 280, 4), 3, 3.8, BLACK, 8, sfx="pop")
T("A", 575, 6165, 84, BLUE, k0=4, k1=4.8, sfx="pop")
L(rect(1370, 6320, 480, 460, 20), 5, 5.8, BLACK, 9, sfx="wood_high")
L(join(oval(1370, 6420, 300, 90), bust(1290, 6300, 30), bust(1450, 6300, 30)), 6, 6.8, BLACK, 8, sfx="pop")
T("B", 1195, 6165, 84, BLUE, k0=7, k1=7.8, sfx="pop")

scene("先摸摸桌子", "书中观点 · 回到当下", (2600, 6300, 0.85))
T("双手放桌上", 2600, 5870, 70, BLUE, k0=0, k1=1.25, sfx="pop")
L(rect(2600, 6250, 1000, 320, 24), 2, 2.8, BLACK, 9, sfx="wood_low")
L(join(palm(2380, 6250, 1.0, 1), palm(2820, 6250, 1.0, -1)), 3, 3.9, BLACK, 8, sfx="wood_high")
T("数三下呼吸", 2600, 6560, 64, k0=4, k1=5.0, sfx="pop")
for n in range(3):
    L(breath(2350 + n * 250, 6740), 5 + n, 5.8 + n, GREEN, 8, sfx="shaker")

scene("卡住就去倒水", "书中观点 · 先放下", (1050, 7650, 0.85))
T("卡住了", 560, 7250, 64, RED, k0=0, k1=0.8, sfx="pop")
L(dispenser(520, 8000), 1, 1.9, BLACK, 9, sfx="wood_high")
L(join(stick(760, 8000, 0.65, "hold"), cup(845, 7840, 0.8)), 2, 2.9, BLACK, 9, sfx="pop")
L(arrow((900, 7640), (1140, 7640), -0.25, 36), 3, 3.8, BLUE, 9, sfx="wood_low")
L(join(desk(1420, 7820, 340), stick(1230, 8000, 0.65, "down")), 4, 4.9, BLACK, 9, sfx="wood_high")
L(bulb(1230, 7560, 50), 6, 6.8, "#E0A526", 9, sfx="ding")
T("有思路了", 1480, 7400, 58, GREEN, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 重来这一天（场景 12–13）

scene("重来这一天", "做法 · 重来一天", (2600, 7650, 0.85))
L(arrow((2050, 7750), (3170, 7750), 0.0, 40), 0, 0.9, BLACK, 9, sfx="wood_high")
L(rect(2320, 7550, 480, 170, 18), 1, 1.7, BLUE, 9, sfx="wood_low")
T("上午写报告", 2320, 7570, 56, BLUE, k0=1.7, k1=2.95)
L(chat_icon(2320, 7240), 4, 4.7, BLACK, 8, sfx="wood_high")
L(cross(2320, 7240, 75), 5, 5.5, RED, 11, sfx="rim")
L(rect(2900, 7550, 420, 170, 18), 6, 6.6, GREEN, 9, sfx="wood_low")
T("下午回消息", 2900, 7570, 56, GREEN, k0=6.6, k1=7.85)

scene("六点关电脑", "重来 · 晚上六点", (1790, 9300, 0.6))
L(monitor(1340, 9000, 720, 470), 0, 0.9, BLACK, 10, sfx="wood_high")
L(join(P((1050, 8850), (1630, 8850)), *[P((1040, 8920 + i * 50), (1640 - (i % 3) * 60, 8920 + i * 50)) for i in range(6)]),
  1, 1.9, BLUE, 7, sfx="pop")
L(join(clock(1170, 9650, 130), hands_at(1170, 9650, 130, 6, 0)), 2, 2.9, BLACK, 9, sfx="wood_low")
T("18:00", 1500, 9670, 84, RED, k0=3, k1=4.25, sfx="pop")
L(join(circle(2250, 9150, 360), P((2170, 9510), (2170, 9580), (1980, 9640)), P((2330, 9510), (2330, 9580), (2520, 9640))),
  4, 4.9, BLACK, 9, sfx="wood_high")
ELDER, UNCLE = brothers(2030, 9440)
L(join(ELDER, UNCLE), 5, 5.6, BLACK, 7, sfx="pop")
L(stick(2385, 9440, 0.36, "hold"), 5.6, 5.95, BLUE, 7)
L(rudder(2480, 9300, 58), 6, 6.8, GREEN, 6, sfx="wood_low")
L(grips(2480, 9300, 58, range(4)), 7, 7.4, GREEN, 5, sfx="ding")
L(grips(2480, 9300, 58, [4]), 7.4, 7.8, RED, 7)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 5850, 0.085)
COMMENT = (1800, 10950, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
L(join(rect(1800, 10900, 1250, 480, 40), P((1500, 11140), (1440, 11230), (1600, 11140))), 5, 5.9, BLACK, 9,
  sfx="wood_high")
T("你一天最容易被啥拽走？", 1800, 10830, 66, RED, k0=6, k1=8.75, sfx="pop")
T("下一讲：天天在练，怎么还在原地？", 1800, 11010, 50, k0=9, k1=13, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "focus", "专注", "忙了一整天，正事一件没干？", ACC, b.shots,
                 [f"{BOOK}第四章 专注力——情绪和智慧的交叉地带：第一节 情绪专注、第二节 学习专注（转述）"],
                 "忙了一整天|正事【一件没干】", SQUARE_SHOT,
                 ["书中观点均为转述，不是逐字引文：专注要身心合一，身体在做什么，注意力就在什么上；身体感受是回到当下的入口；"
                  "做 A 的时候只做 A，做 B 的时候只做 B；难题想不出时先放下、去做别的事，回头可能就有思路（酝酿效应）。"
                  "见第四章 专注力（第一节 情绪专注、第二节 学习专注）。第四章第一节标题里的“一招”具体指什么未核实，本讲不用。",
                  "小林的一天（晚上十点报告只有标题、九点写一行就看群、两点开会想外卖）为现实场景示意，不指向任何具体公司或个人；"
                  "“20 个窗口”“3 个群”“99+”“正文 0 字”等数字均为示意，不是数据。",
                  "双手放桌上数三下呼吸、卡住就去倒杯水、上午关群写报告下午集中回消息，均为据书中思路整理的做法示意。",
                  "脑内三兄弟（本能脑、情绪脑、理智脑宝宝）与船舵握痕为系列视觉角色，据第一章“三重大脑”与第三章“思维舵手”的比喻。"],
                 tags="#专注力 #效率")
    return b.attach(ep)
