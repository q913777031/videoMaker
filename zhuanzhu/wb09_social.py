"""09 挑工具（白板手绘版）：社交软件停三十天，会怎样？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，最后 4 拍不出新笔画）。
叙事（形式 C 复刻实验：照书里给读者的自测办法演一遍）：
开局让观众猜——手机连同小红点被锁进抽屉，停用三十天，会错过大事、朋友会急，还是没人发现？→
规矩：谁也不告诉，不发告别帖 →（drop）日历一页页撕到第 30 页，写着“没人发现”→
亮书：这是书里给的自测，不算科研实验 → 到期问两个问题：这三十天用着它会更好吗？有人在乎你不在吗？→
两个都是“没有”，抽屉锁死别装回来 → 书中观点：像手艺人挑工具，只把趁手的挂上墙 →
做法：先写下最要紧的几件事，对着它给每个工具打分，大帮才留、大坑就停；下班和周末提前想好做什么 →
拉远全板 → 评论区互动。
出处：卡尔·纽波特《深度工作》准则3“远离社交媒体”（转述）；中译本宋伟译，江西人民出版社 · 后浪 2017。
例子与做法为示意与据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross, doc,
                               face, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out

from .common import BOOK, episode

ACC = "#7B4FA8"
SQUARE_SHOT = 3                 # 场景 4：撕到第 30 页的日历 + 小周

GREY = "#8A8F98"
R1, R2, R3, R4, R5, R6, R7 = 900, 2800, 4100, 5400, 6700, 8000, 9400   # 各排白板区块的中心 y
b = Board(size=(3600, 10000))


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

def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """主角小周：火柴人 + 胸前工牌。(x, y) 为脚底。"""
    hy = y - 290 * s
    return join(stick(x, y, s, arms), P((x - 18 * s, hy + 45 * s), (x + 24 * s, hy + 100 * s)),
                rect(x + 26 * s, hy + 122 * s, 30 * s, 40 * s, 4 * s))


def reddot_fn(x, y, r, label, legs=True):
    """小红点：红色实心圆 + 白字数字 + 两条小短腿，弹一下出场。"""

    def fn(c, k, t):
        sc = clamp01(k / 0.6) * (1 + 0.25 * math.sin(math.pi * clamp01(k)))
        if legs and k > 0.3:
            for d in (-1, 1):
                K.seg(c, x + d * r * 0.35, y + r * 0.85, x + d * r * 0.45, y + r * 1.55, BLACK, max(3, r * 0.12))
                K.seg(c, x + d * r * 0.45, y + r * 1.55, x + d * r * 0.75, y + r * 1.55, BLACK, max(3, r * 0.12))
        K.dot(c, x, y, r * sc, RED)
        if sc > 0.7:
            K.text(c, label, x, y + r * 0.05, r * (0.85 if len(label) < 3 else 0.62), "black", "#FFFFFF")
        return None

    return fn


def apps(x, y, gap=100, s=60) -> skia.Path:
    """手机屏上 2×2 个方块（不画任何真实软件图标）。"""
    return join(*(rect(x + dx, y + dy, s, s, 14) for dx in (-gap / 2, gap / 2) for dy in (-gap / 2, gap / 2)))


def drawer_open(x, y, w=700, h=300) -> skia.Path:
    """拉开的抽屉（略俯视）：(x, y) 为前脸中心。"""
    top = y - h / 2
    return join(rect(x, y, w, h, 14),
                P((x - w / 2, top), (x - w / 2 + 100, top - 100), (x + w / 2 + 100, top - 100), (x + w / 2, top)),
                P((x + w / 2 + 100, top - 100), (x + w / 2 + 100, y + h / 2 - 100), (x + w / 2, y + h / 2)))


def padlock(x, y, s=1.0) -> skia.Path:
    """挂锁：(x, y) 为锁身中心。"""
    sh = skia.Path()
    sh.addArc(skia.Rect.MakeXYWH(x - 38 * s, y - 100 * s, 76 * s, 90 * s), 180, 180)
    return join(sh, P((x - 38 * s, y - 55 * s), (x - 38 * s, y - 40 * s)), P((x + 38 * s, y - 55 * s), (x + 38 * s, y - 40 * s)),
                rect(x, y, 120 * s, 90 * s, 14 * s), circle(x, y - 8 * s, 9 * s), P((x, y), (x, y + 22 * s)))


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12 if w < 200 else 30), P((x - w * 0.17, y + h / 2 - h * 0.1), (x + w * 0.17, y + h / 2 - h * 0.1)))


def zipper(x0, x1, y) -> skia.Path:
    """拉链嘴：一条线 + 细齿 + 拉头。"""
    parts = [P((x0, y), (x1, y))]
    n = int((x1 - x0) / 22)
    for i in range(1, n):
        xx = x0 + i * (x1 - x0) / n
        parts.append(P((xx, y - 12), (xx, y + 12)))
    parts.append(rect(x1 + 18, y + 22, 26, 44, 6))
    return join(*parts)


def calendar(x, y, w=560, h=640) -> skia.Path:
    """台历：外框 + 顶部装订条 + 两个圈。(x, y) 为中心。"""
    top = y - h / 2
    return join(rect(x, y, w, h, 18), P((x - w / 2, top + 100), (x + w / 2, top + 100)),
                rect(x - w * 0.22, top, 26, 80, 13), rect(x + w * 0.22, top, 26, 80, 13))


def scale(x, y, span=640) -> skia.Path:
    """天平：(x, y) 为横梁中点，左右各吊一个盘。"""
    parts = [P((x, y - 30), (x, y + 500)), P((x - 150, y + 500), (x + 150, y + 500)), P((x - span / 2, y), (x + span / 2, y)),
             circle(x, y - 45, 16)]
    for d in (-1, 1):
        px = x + d * span / 2
        parts += [P((px - 90, y + 180), (px, y), (px + 90, y + 180))]
        pan = skia.Path()
        pan.addArc(skia.Rect.MakeXYWH(px - 110, y + 120, 220, 120), 0, 180)
        parts += [pan, P((px - 110, y + 180), (px + 110, y + 180))]
    return join(*parts)


def dashed(path: skia.Path, on=24, off=20) -> skia.Path:
    """把路径切成虚线段（白板上的“空位”）。"""
    out = skia.Path()
    pm = skia.PathMeasure(path, False)
    while True:
        total, d = pm.getLength(), 0.0
        while d < total:
            seg = skia.Path()
            pm.getSegment(d, min(d + on, total), seg, True)
            out.addPath(seg)
            d += on + off
        if not pm.nextContour():
            break
    return out


def cup(x, y, s=1.0) -> skia.Path:
    return join(P((x - 22 * s, y - 30 * s), (x - 16 * s, y + 30 * s), (x + 16 * s, y + 30 * s), (x + 22 * s, y - 30 * s)),
                P((x - 8 * s, y - 45 * s), (x - 4 * s, y - 60 * s)), P((x + 8 * s, y - 45 * s), (x + 12 * s, y - 60 * s)))


def cabinet(x, y, w=700, h=380) -> skia.Path:
    """关上的抽屉柜：两层抽屉。(x, y) 为中心（两层之间的缝）。"""
    return join(rect(x, y, w, h, 16), P((x - w / 2, y), (x + w / 2, y)),
                P((x - w / 2 + 40, y + h / 2), (x - w / 2 + 40, y + h / 2 + 50)),
                P((x + w / 2 - 40, y + h / 2), (x + w / 2 - 40, y + h / 2 + 50)))


def pegboard(x, y, w=720, h=560) -> skia.Path:
    parts = [rect(x, y, w, h, 12)]
    for i in range(6):
        for jj in range(2):
            parts.append(circle(x - w / 2 + 70 + i * (w - 140) / 5, y + h / 2 - 60 - jj * 70, 6))
    return join(*parts)


def knife(x, y) -> skia.Path:
    """挂在钩子上的刀：(x, y) 为钩子位置。"""
    return join(circle(x, y, 12), rect(x, y + 75, 44, 110, 10),
                P((x - 22, y + 130), (x - 22, y + 330), (x + 24, y + 250), (x + 24, y + 130)))


def apron(x, y, s=1.0) -> skia.Path:
    hy = y - 290 * s
    return join(P((x - 30 * s, hy + 85 * s), (x + 30 * s, hy + 85 * s), (x + 48 * s, hy + 200 * s),
                  (x - 48 * s, hy + 200 * s), close=True), P((x - 30 * s, hy + 85 * s), (x, hy + 50 * s), (x + 30 * s, hy + 85 * s)))


def note(x, y, w=330, h=260, rot=0.0) -> skia.Path:
    """便签纸（略歪）+ 顶上一条胶带。"""
    a = math.radians(rot)

    def r(px, py):
        return x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)

    body = P(r(-w / 2, -h / 2), r(w / 2, -h / 2), r(w / 2, h / 2 - 40), r(w / 2 - 40, h / 2), r(-w / 2, h / 2), close=True)
    tape = P(r(-60, -h / 2 - 22), r(60, -h / 2 - 22), r(60, -h / 2 + 22), r(-60, -h / 2 + 22), close=True)
    return join(body, tape)


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


# ---------------------------------------------------------------- 开局：停三十天，先猜（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("停三十天", "一个实验", (1000, R1, 0.85), bars=2)
L(phone(900, 800, 220, 320), 0, 0.9, BLACK, 9, sfx="wood_high")
L(apps(900, 770), 1, 1.8, BLUE, 8, sfx="pop")
b.custom(J(), 2, 2.5, reddot_fn(1010, 640, 55, "99+"), sfx="ding")
L(drawer_open(900, 1150), 3, 3.9, BLACK, 9, sfx="wood_low")
L(padlock(900, 1175, 1.0), 4, 4.8, RED, 10, sfx="tom")
T("停用 30 天", 900, 470, 90, RED, k0=5, k1=6.0, sfx="pop")

scene("你猜会怎样", "先猜一猜", (2600, R1, 0.85))
L(zhou(3070, 1300, 0.75, "shrug"), 0, 0.8, BLACK, 9, sfx="wood_high")
L(face(3070, 1300, 0.75, "flat"), 0.8, 1.0)
T("你猜，会怎样？", 2550, 480, 84, RED, k0=1, k1=2.6, sfx="pop")
for n, (opt, k) in enumerate((("A  错过大事", 3), ("B  朋友急了", 5), ("C  没人发现", 7))):
    yy = 700 + n * 190
    L(rect(2120, yy, 70, 70, 10), k, k + 0.25, BLACK, 8, sfx="pop" if n == 2 else "wood_high")
    T(opt, 2440, yy, 68, k0=k + 0.25, k1=k + 1.0 if n == 2 else k + 1.3)

scene("谁也不说", "实验规矩", (1000, R2, 0.85))
T("规矩：谁也不告诉", 1000, 2360, 76, k0=0, k1=2, sfx="pop")
L(circle(720, 2850, 190), 2, 2.9, BLACK, 10, sfx="wood_high")
L(join(circle(655, 2800, 10), circle(785, 2800, 10), zipper(630, 790, 2920)), 3, 3.9, BLACK, 8, sfx="shaker")
L(bubble(1250, 2700, 540, 170, -1), 5, 5.5, BLUE, 8, sfx="pop")
T("告别帖：我先撤了", 1250, 2700, 50, BLUE, k0=5.5, k1=7.0)
L(cross(1250, 2700, 120), 7, 7.8, RED, 12, sfx="rim")

# ---------------------------------------------------------------- drop（场景 4）：日历哗哗撕到第 30 页

CAL = (2450, 2760)
J_CAL = scene("没人发现", "三十天后", (2600, R2, 0.8), shake=[0], flashes=[0])
L(calendar(*CAL), 0, 0.6, BLACK, 10, sfx="kick")
TEARS = [(1, 1, 8), (2, 8, 15), (3, 15, 22), (4, 22, 29), (5, 29, 30)]   # (拍, 撕前页码, 撕后页码)
FLY = 0.42                      # 撕下的一页飞走的秒数


def _tear_times():
    out = []
    for kb, v0, v1 in TEARS:
        t0, t1 = b.t_of(J_CAL, kb), b.t_of(J_CAL, kb + 1)
        n = v1 - v0
        for i in range(n):
            out.append((t0 + (t1 - t0) * 0.6 * i / max(1, n), v0 + i))
    return out


def _page(c, n, x, y, alpha=1.0, fill=False):
    if fill:
        K.rr(c, x, y, 520, 500, 12, "#FBFBF9", alpha)
        K.rr_stroke(c, x, y, 520, 500, 12, BLACK, 7, alpha)
    K.text(c, "第", x - 205, y - 40, 70, "hand", BLACK, alpha)
    K.text(c, str(n), x, y - 70, 230, "hand", RED if n == 30 else BLACK, alpha)
    K.text(c, "天", x + 205, y - 40, 70, "hand", BLACK, alpha)


def calendar_fn(c, k, t):
    """台历页：按拍点一叠叠撕，撕下的那页旋转飞走；停在第 30 页。"""
    tears = _tear_times()
    cur = 1
    for tt, v in tears:
        if t >= tt:
            cur = v + 1
    px, py = CAL[0], CAL[1] + 50
    _page(c, cur, px, py, k)
    for tt, v in tears:
        f = (t - tt) / FLY
        if 0 <= f < 1:
            with K.at(c, px + 620 * f, py - 260 * f + 520 * f * f, 40 * f):
                _page(c, v, 0, 0, 1 - f, fill=True)
    return None


b.custom(J_CAL, 0.6, 0.9, calendar_fn)
for kb, _, _ in TEARS:
    H(kb, "shaker" if kb < 5 else "tom", 0.75)
T("没人发现", CAL[0], CAL[1] + 230, 84, RED, k0=6, k1=7.0, sfx="ding")
L(zhou(3020, 3100, 0.7, "shrug"), 7, 7.7, BLUE, 9, sfx="wood_high")
L(face(3020, 3100, 0.7, "smile"), 7.7, 7.9, BLUE, 8)

# ---------------------------------------------------------------- 书里的自测与两个问题（场景 5–8）

scene("书里给的自测", "深度工作 · 书里的自测", (1000, R3, 0.85))
L(book(800, 4050, 440, 300), 0, 0.9, BLACK, 10, sfx="wood_low")
T("《深度工作》", 800, 3790, 72, GREEN, k0=1, k1=2.5, sfx="pop")
T("卡尔 · 纽波特", 800, 4320, 54, k0=3, k1=4.25, sfx="pop")
L(doc(1330, 4060, 260, 340, 5), 5, 5.8, BLUE, 9, sfx="wood_high")
T("自测本", 1330, 3810, 56, BLUE, k0=5.8, k1=6.6)
T("照着书，自己试一回", 1000, 4540, 60, k0=6.6, k1=8.0)

scene("用着会更好吗", "书中自测 · 第一问", (2600, R3, 0.85))
T("第一问", 2600, 3660, 80, RED, k0=0, k1=0.8, sfx="pop")
L(scale(2600, 3880), 1, 1.9, BLACK, 9, sfx="wood_high")
L(phone(2280, 3990, 70, 120), 2, 2.6, BLACK, 8, sfx="pop")
b.custom(J(), 3, 3.4, reddot_fn(2318, 3925, 24, "9", legs=False), sfx="ding")
T("有它", 2280, 4160, 56, k0=3.4, k1=4.2)
T("没它", 2920, 4160, 56, k0=4.2, k1=5.0)
H(4, "wood_high", 0.6)
T("这三十天，有它会更好吗？", 2600, 4520, 60, k0=5, k1=7.75, sfx="pop")

scene("有人在乎吗", "书中自测 · 第二问", (2600, R4, 0.85))
T("第二问", 2600, 4960, 80, RED, k0=0, k1=0.8, sfx="pop")
L(join(stick(2150, 5560, 0.6, "hold"), phone(2228, 5420, 40, 66)), 1, 1.8, BLACK, 9, sfx="wood_high")
L(join(stick(2480, 5560, 0.6, "hold"), cup(2552, 5440, 0.9)), 2, 2.8, BLACK, 9, sfx="pop")
L(join(stick(2810, 5560, 0.6, "hold"), doc(2885, 5440, 60, 80, 3)), 3, 3.8, BLACK, 9, sfx="wood_high")
L(dashed(stick(3120, 5560, 0.6, "down")), 4, 4.8, BLUE, 8, sfx="shaker")
T("你", 3120, 5640, 50, BLUE, k0=4.8, k1=5.6)
T("你不在，有人在乎吗？", 2600, 5840, 64, k0=6, k1=8.0, sfx="pop")

scene("那就别回", "书中自测 · 到期", (1000, R4, 0.85))
T("两问都是：没有", 1000, 4960, 72, k0=0, k1=1.75, sfx="pop")
L(cabinet(900, 5420), 2, 2.9, BLACK, 10, sfx="wood_low")
L(join(P((1085, 5422), (1078, 5480), (1058, 5482)), P((1115, 5422), (1122, 5480), (1142, 5482))), 3, 3.5, RED, 8, sfx="pop")
T("叮……", 1240, 5300, 50, GREY, k0=3.5, k1=4.3)
L(join(P((570, 5250), (1230, 5590)), P((1230, 5250), (570, 5590))), 4, 4.8, RED, 12, sfx="rim")
L(padlock(900, 5440, 1.0), 5, 5.8, BLACK, 10, sfx="tom")
T("别再装回来", 1000, 5840, 72, RED, k0=6, k1=7.25, sfx="ding")

# ---------------------------------------------------------------- 书中观点：手艺人挑工具（场景 9–12）

scene("像挑刀一样", "书中观点 · 手艺人挑工具", (1000, R5, 0.85))
T("像手艺人挑工具", 1000, 6260, 72, k0=0, k1=1.75, sfx="pop")
L(pegboard(820, 6720), 2, 2.8, BLACK, 9, sfx="wood_low")
L(knife(600, 6500), 3, 3.5, BLACK, 9, sfx="wood_high")
L(knife(820, 6500), 4, 4.5, BLACK, 9, sfx="pop")
L(knife(1040, 6500), 4.5, 5.0, BLACK, 9)
L(join(stick(1400, 7060, 0.7, "hold"), apron(1400, 7060, 0.7)), 5, 5.8, BLUE, 9, sfx="wood_high")
T("趁手的才上墙", 1000, 7160, 64, k0=6, k1=7.5, sfx="ding")

scene("先写目标", "做法 · 写下要紧的事", (2600, R5, 0.85))
T("先写下最要紧的事", 2600, 6260, 72, k0=0, k1=2, sfx="pop")
for n, (w, x, y, rot) in enumerate((("带好团队", 2190, 6640, -4), ("学会剪辑", 2600, 6700, 2), ("陪家人", 3010, 6640, -3))):
    L(note(x, y, rot=rot), 2 + 2 * n, 2.5 + 2 * n, BLACK, 8, sfx="wood_high" if n != 1 else "pop")
    T(w, x, y + 10, 58, BLUE, k0=2.5 + 2 * n, k1=3.5 + 2 * n if n < 2 else 7.25)

# 表格：工具 × 目标（只写类别，不写任何具体软件名）
GX0, GX1, GC = 2030, 3170, 2450                   # 表格左右边、第一列右边
COLS = (2560, 2810, 3060)
GY = (7680, 7820, 8000, 8180)
scene("帮还是坑", "做法 · 给工具打分", (2600, R6, 0.85))
T("对着目标打分", 2600, 7560, 72, k0=0, k1=1.5, sfx="pop")
L(join(rect((GX0 + GX1) / 2, (GY[0] + GY[3]) / 2, GX1 - GX0, GY[3] - GY[0], 10), P((GX0, GY[1]), (GX1, GY[1])),
       P((GX0, GY[2]), (GX1, GY[2])), P((GC, GY[0]), (GC, GY[3])), P((2685, GY[0]), (2685, GY[3])),
       P((2935, GY[0]), (2935, GY[3]))), 1, 1.8, BLACK, 7, sfx="wood_high")
T("团队　　　剪辑　　　家人", 2810, 7750, 50, k0=2, k1=3.5, sfx="pop")
T("工作群", 2240, 7910, 54, k0=4, k1=4.75, sfx="pop")
L(check(COLS[0], 7910, 40), 4.75, 5.0, GREEN, 10)
L(join(P((COLS[1] - 30, 7910), (COLS[1] + 30, 7910)), P((COLS[2] - 30, 7910), (COLS[2] + 30, 7910))), 5.0, 5.2, GREY, 8)
T("刷短视频", 2240, 8090, 54, k0=5.2, k1=6.0)
L(P((COLS[0] - 30, 8090), (COLS[0] + 30, 8090)), 6, 6.1, GREY, 8, sfx="rim")
L(join(cross(COLS[1], 8090, 34), cross(COLS[2], 8090, 34)), 6.1, 6.6, RED, 10)
L(rect((GX0 + GX1) / 2, 7910, GX1 - GX0 + 40, 150, 70), 7, 7.5, GREEN, 8, sfx="ding")
L(P((GX0 - 10, 8090), (GX1 + 10, 8090)), 7.5, 8.0, RED, 10)

scene("先想好做啥", "做法 · 想好怎么消遣", (1000, R6, 0.85))
T("周末清单", 1000, 7560, 76, k0=0, k1=1, sfx="pop")
L(rect(860, 7980, 600, 560, 20), 1, 1.9, BLACK, 9, sfx="wood_high")
for n, w in enumerate(("爬山", "读书", "做饭")):
    yy = 7830 + n * 160
    L(rect(660, yy, 60, 60, 8), 2 + n, 2.3 + n, BLACK, 8, sfx="pop")
    T(w, 880, yy, 64, k0=2.3 + n, k1=2.95 + n)
L(zhou(1400, 8300, 0.7, "up"), 5, 5.8, BLUE, 9, sfx="wood_high")
L(face(1400, 8300, 0.7, "smile"), 5.8, 6.0, BLUE, 8)
T("空出来就会被刷掉", 1000, 8460, 60, RED, k0=6, k1=8.0, sfx="pop")

# ---------------------------------------------------------------- 拉远全板（场景 13）

scene("停一停看看", "全板回看", (1800, 4752, 0.195))
L(oval(2620, 2790, 1260, 880), 1, 1.8, RED, 28, sfx="wood_high")
L(rect(2600, 4750, 1320, 2280, 120), 2, 2.8, RED, 28, sfx="pop")
L(oval(900, 5420, 1260, 1060), 3, 3.8, RED, 28, sfx="pop")
L(oval(900, 6700, 1300, 1080), 4, 4.8, RED, 28, sfx="ding")
L(arrow((2600, 3240), (2600, 3590), 0.0, 120), 5, 5.6, RED, 26, sfx="wood_high")
L(arrow((1930, 5420), (1540, 5420), 0.0, 120), 6, 6.6, RED, 26, sfx="wood_high")
L(arrow((900, 5960), (900, 6150), 0.0, 90), 6.6, 7.0, RED, 26)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 5050, 0.095)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, (1800, R7, 0.8), dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你最想停哪个软件？", 1800, 9300, 80, RED, k0=6, k1=8.25, sfx="pop")
T("下一讲：活一件没少，怎么准点下班？", 1800, 9480, 50, k0=9, k1=13.25, sfx="wood_high")
L(underline(1100, 2500, 9560), 13.25, 13.9, BLACK, 6)
b.custom(J(), 14, 14.5, reddot_fn(2520, 9150, 50, "1"), sfx="pop")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "social", "挑工具", "社交软件停三十天，会怎样？", ACC, b.shots,
                 [f"{BOOK}准则3“远离社交媒体”：在你的网络使用习惯中采用关键少数法则 / 戒掉社交媒体 / 不要用网络来消遣（转述）",
                  "中译本：宋伟译，江西人民出版社 · 后浪 2017（ISBN 9787210093213）；再版：民主与建设出版社 · 后浪 2023"],
                 "社交软件|停【三十天】会怎样", SQUARE_SHOT,
                 ["书中观点均为转述，不是逐字引文：准则3“远离社交媒体”中，作者主张像手艺人挑工具那样挑网络工具——"
                  "先找出生活和工作里最要紧的几个目标，只有当一个工具对这些目标的好处明显大过坏处时才用它（关键少数法则）；"
                  "作者建议读者停用社交媒体 30 天，期间不告诉任何人、不发告别帖，到期问自己两个问题：这 30 天用着它会不会"
                  "明显更好？有没有人在乎我不在？两个答案都是“没有”就别再回去；另建议别靠上网消遣，下班和周末的时间提前想好"
                  "怎么过（书中引阿诺德·本涅特的说法）。",
                  "这是书里给读者的自测办法，不是科研实验，片中也没有任何统计数据。日历撕到第 30 页写“没人发现”为示意结果，"
                  "不能说成书里的统计结论；书里提到的个人经历细节需核实中译本，未上屏。",
                  "开头的 A/B/C 三个选项、“告别帖：我先撤了”、“带好团队 / 学会剪辑 / 陪家人”三张便签、工具打分表"
                  "（工作群 / 刷短视频，以及 ✓ / ✗ 的打法）、周末清单“爬山 / 读书 / 做饭”均为示意；"
                  "片中不出现任何具体软件名称和图标，不指向任何公司。",
                  "“先写下要紧的事、对着它给工具打分、提前想好怎么消遣”为据书中思路整理的做法。书中章节名只写在出处里，不上屏。"],
                 tags="#社交媒体")
    return b.attach(ep)
