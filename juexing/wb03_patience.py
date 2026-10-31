"""03 耐心（白板手绘版）：学了三个月没起色，还学吗？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（形式 I：一条曲线讲完）：整讲画在一张大坐标纸上，横轴时间、纵轴本事，相机沿曲线从左往右走——
阿杰下班学剪视频 → 他心里那条斜直线 → 真实的红线三个月贴着地面爬 → drop：一把剪刀在拐点前剪断红线（多数人在这儿放弃）→
亮书 → 书中观点：复利曲线先慢后快，过了拐点才往上走 → 两条线中间的落差就是失望的来处（封面镜头）→
书中观点：耐心靠看得远，跟咬牙硬撑关系不大 → 平台期：放大镜下的曲线像台阶，走走停停 → 平的那段底下在攒 →
书中观点：成长的分量，改变 > 行动 > 思考 > 学习 → 做法（示意）：进度本，每周存一条回头比 →
拉远看全图：剪断处被绿线接上，脑袋里的宝宝又多握了一会儿舵 → 评论区互动。
书中观点为转述（周岭《认知觉醒》第一章第三节“耐心：得耐心者得天下”）；阿杰学剪视频、进度本等例子与做法为示意，据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, cross, face,
                               join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#7A4FA3"
SQUARE_SHOT = 6                 # 场景 7：直线与曲线分叉，中间一道缝，阿杰站在缝里

b = Board(size=(4800, 6600))
PAPER = "#FBFBF9"
GRAY = "#8E96A3"

# 坐标纸：原点、心里那条直线、真实曲线（复利：前慢后快）
OX, OY0 = 600, 3400
XEND, YTOP = 4450, 1250
LINE_END = (4000, 1700)
CUT_X = 3020                    # 剪刀剪断处
MONTH_X = 3100                  # “三个月”刻度
KNEE_X = 3500                   # 拐点
RED_END = 4150


def y_line(x):
    return OY0 - (OY0 - LINE_END[1]) * (x - OX) / (LINE_END[0] - OX)


def y_red(x):
    return OY0 - 0.273 * (math.exp((x - OX) / 400) - 1)


def red_path(x0, x1, step=20, wobble=0.0) -> skia.Path:
    n = max(2, int((x1 - x0) / step))
    pts = [(x0 + (x1 - x0) * i / n, y_red(x0 + (x1 - x0) * i / n) - wobble * math.sin(i * 1.3)) for i in range(n + 1)]
    return P(*pts)


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def J():
    return len(b.shots) - 1


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def axis_arrow(x0, y0, x1, y1, head=40) -> skia.Path:
    ang = math.atan2(y1 - y0, x1 - x0)
    parts = [P((x0, y0), (x1, y1))]
    for d in (0.5, -0.5):
        parts.append(P((x1, y1), (x1 - head * math.cos(ang + d), y1 - head * math.sin(ang + d))))
    return join(*parts)


def laptop(x, y, s=1.0) -> skia.Path:
    """笔记本电脑，屏幕上一个播放键和一条时间线（剪视频）。(x, y) 为底座中点。"""
    w, h = 190 * s, 120 * s
    sy = y - h / 2 - 8 * s
    return join(rect(x, sy, w, h, 8 * s), P((x - w / 2 - 20 * s, y), (x + w / 2 + 20 * s, y)),
                P((x - 20 * s, sy - 30 * s), (x - 20 * s, sy + 10 * s), (x + 18 * s, sy - 10 * s), close=True),
                P((x - w / 2 + 20 * s, sy + 35 * s), (x + w / 2 - 20 * s, sy + 35 * s)))


def star(x, y, r=60) -> skia.Path:
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return P(*pts, close=True)


def drop(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y - 30 * s)
    p.quadTo(x + 22 * s, y, x, y + 14 * s)
    p.quadTo(x - 22 * s, y, x, y - 30 * s)
    return p


def wheel(x, y, r=150, grips=0) -> skia.Path:
    """船舵：轮圈 + 轮毂 + 8 根辐条伸出把手；grips 为轮圈上的握痕数。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.22)]
    for i in range(8):
        a = i * math.pi / 4
        parts.append(P((x + math.cos(a) * r * 0.22, y + math.sin(a) * r * 0.22),
                       (x + math.cos(a) * r * 1.28, y + math.sin(a) * r * 1.28)))
    parts += [grip(x, y, r, g) for g in range(grips)]
    return join(*parts)


def grip(x, y, r, g) -> skia.Path:
    """舵上第 g 道握痕（从 0 数）：系列第 N 讲舵上有 N 道。"""
    a = -math.pi * 0.75 + g * 0.32
    return join(*[P((x + math.cos(a + dr) * r * 0.85, y + math.sin(a + dr) * r * 0.85),
                    (x + math.cos(a + dr) * r * 1.15, y + math.sin(a + dr) * r * 1.15)) for dr in (-0.1, 0.1)])


def double_arrow(x, y0, y1, head=34) -> skia.Path:
    return join(P((x, y0), (x, y1)), P((x - head * 0.7, y0 + head), (x, y0), (x + head * 0.7, y0 + head)),
                P((x - head * 0.7, y1 - head), (x, y1), (x + head * 0.7, y1 - head)))


def telescope(x0, y0, x1, y1, w0=26, w1=46) -> skia.Path:
    """望远镜：从目镜 (x0, y0) 到物镜 (x1, y1) 渐粗的镜筒 + 物镜圈。"""
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    body = P((x0 + nx * w0 / 2, y0 + ny * w0 / 2), (x1 + nx * w1 / 2, y1 + ny * w1 / 2),
             (x1 - nx * w1 / 2, y1 - ny * w1 / 2), (x0 - nx * w0 / 2, y0 - ny * w0 / 2), close=True)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ring = P((mx + nx * 22, my + ny * 22), (mx - nx * 22, my - ny * 22))
    return join(body, ring)


def magnifier(x, y, r=120) -> skia.Path:
    a = math.pi / 4
    return join(circle(x, y, r), P((x + r * math.cos(a), y + r * math.sin(a)),
                                    (x + r * 1.9 * math.cos(a), y + r * 1.9 * math.sin(a))))


def weight(x, bottom, w) -> skia.Path:
    """秤砣：梯形砣身 + 顶上提环。(x, bottom) 为底边中点，w 为底宽。"""
    h = w * 0.85
    top = bottom - h
    body = P((x - w / 2, bottom), (x - w * 0.32, top), (x + w * 0.32, top), (x + w / 2, bottom), close=True)
    return join(body, circle(x, top - w * 0.14, w * 0.14))


def gt(x, y, s=34) -> skia.Path:
    return P((x - s * 0.6, y - s), (x + s * 0.6, y), (x - s * 0.6, y + s))


def folder(x, y, w, h) -> skia.Path:
    l, t = x - w / 2, y - h / 2
    return join(rect(x, y, w, h, 20), P((l, t + 10), (l, t - 80), (l + 330, t - 80), (l + 380, t)))


def thumb(x, y, n) -> skia.Path:
    """进度本里的一条作品缩略图：n=0 最糙（乱线），n=3 最好（顺滑曲线 + 星）。"""
    parts = [rect(x, y, 200, 150, 10)]
    p = skia.Path()
    p.moveTo(x - 75, y + 20)
    amp = [42, 28, 14, 0][n]
    for i in range(1, 9):
        xx = x - 75 + i * 150 / 8
        yy = y + 20 - i * 6 + (amp if i % 2 else -amp)
        p.lineTo(xx, yy)
    if n == 3:
        p = skia.Path()
        p.moveTo(x - 75, y + 35)
        p.quadTo(x, y + 30, x + 70, y - 30)
        parts.append(star(x + 55, y - 45, 22))
    parts.append(p)
    return join(*parts)


def bricks(x0, y, n, w=78, h=40, off=0.0) -> skia.Path:
    return join(*[rect(x0 + off + w / 2 + i * w, y, w - 6, h - 6, 4) for i in range(n)])


def stairs() -> skia.Path:
    pts = [(3000, 4880), (3180, 4660), (3450, 4650), (3620, 4400), (3870, 4390), (4040, 4090)]
    p = skia.Path()
    p.moveTo(*pts[0])
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        p.quadTo((ax + bx) / 2 + (8 if ay == by else 0), (ay + by) / 2 + (10 if ay != by else -6), bx, by)
    return p


def elder(x, y, s=1.0) -> skia.Path:
    """老大“本能脑”：拄拐的老爷爷（弯腰 + 拐杖）。"""
    hy = y - 290 * s
    return join(stick(x, y, s, "down"), P((x + 70 * s, hy + 170 * s), (x + 85 * s, y)),
                P((x + 70 * s, hy + 170 * s), (x + 95 * s, hy + 150 * s)),
                P((x - 25 * s, hy + 30 * s), (x + 25 * s, hy + 30 * s)))


def uncle(x, y, s=1.0) -> skia.Path:
    """老二“情绪脑”：戴耳机、攥手机的大叔。"""
    hy = y - 290 * s
    ph = skia.Path()
    ph.addArc(skia.Rect.MakeXYWH(x - 55 * s, hy - 60 * s, 110 * s, 110 * s), 180, 180)
    return join(stick(x, y, s, "hold"), ph, rect(x - 52 * s, hy, 18 * s, 34 * s, 5 * s),
                rect(x + 52 * s, hy, 18 * s, 34 * s, 5 * s), rect(x + 120 * s, hy + 80 * s, 34 * s, 56 * s, 6 * s))


def baby(x, y, s=1.0) -> skia.Path:
    """老三“理智脑”：戴围嘴的小宝宝，大头小身子。"""
    hy = y - 200 * s
    bib = skia.Path()
    bib.addArc(skia.Rect.MakeXYWH(x - 28 * s, hy + 40 * s, 56 * s, 50 * s), 0, 180)
    return join(circle(x, hy, 55 * s), P((x, hy + 55 * s), (x, y - 70 * s)),
                P((x - 40 * s, y), (x, y - 70 * s), (x + 40 * s, y)),
                P((x - 50 * s, hy + 110 * s), (x, hy + 80 * s), (x + 60 * s, hy + 95 * s)), bib)


# ---- 动态项（custom：不算新笔画）

def grid_fn(c, k, t):
    """坐标纸：淡色方格逐行铺开。"""
    pt = K.paint("#C9D3E0", 0.55 * clamp01(k * 1.5), 2)
    for gx in range(OX + 200, XEND, 200):
        c.drawLine(gx, OY0, gx, OY0 - (OY0 - YTOP) * ease_out(k), pt)
    for gy in range(OY0 - 200, YTOP, -200):
        c.drawLine(OX, gy, OX + (XEND - OX) * ease_out(k), gy, pt)
    return None


def gap_fn(c, k, t):
    """心里那条直线与真实曲线之间的落差：浅灰填色淡入。"""
    xs = [OX + i * 20 for i in range(int((3990 - OX) / 20) + 1)]
    p = skia.Path()
    p.moveTo(OX, OY0)
    for x in xs:
        p.lineTo(x, y_line(x))
    for x in reversed(xs):
        p.lineTo(x, y_red(x) if x < CUT_X - 30 or x > CUT_X + 30 else y_red(x) - 2)
    p.close()
    c.drawPath(p, K.paint(GRAY, 0.22 * ease_in_out(k)))
    return None


def disc_fn(x, y, r):
    """白底圆片（放大镜头 / 脑袋剖面）：盖住后面的灰底与线条。"""
    def fn(c, k, t):
        c.drawCircle(x, y, r * ease_out(k), K.paint(PAPER))
        return None
    return fn


J_CUT = None


def scissors_fn(c, k, t):
    """剪刀：张口出现，一下合上把红线剪断；断口抹白。下一屏开头淡出。"""
    cx, cy = CUT_X, y_red(CUT_X)
    alpha = 1.0
    if b.ep is not None:
        t_end = b.t_of(J_CUT, 12)
        alpha = 1 - clamp01((t - t_end) / 0.4)
    if k > 0.85:
        c.drawRect(skia.Rect.MakeXYWH(cx - 28, cy - 22, 56, 44), K.paint(PAPER))
    if alpha <= 0:
        return None
    open_a = math.radians(32) * (1 - ease_in_out(k))
    px, py = cx + 70, cy - 70                 # 轴心
    base = math.atan2(cy - py, cx - px)       # 刀刃指向断口
    col = BLACK
    for sgn in (1, -1):
        a = base + sgn * open_a / 2
        tip = (px + math.cos(a) * 150, py + math.sin(a) * 150)
        ha = a + math.pi + sgn * math.radians(24)
        hc = (px + math.cos(ha) * 95, py + math.sin(ha) * 95)
        blade = P((px, py), tip)
        c.drawPath(blade, K.paint(col, alpha, 14))
        c.drawLine(px, py, px + math.cos(ha) * 60, py + math.sin(ha) * 60, K.paint(col, alpha, 10))
        c.drawCircle(hc[0], hc[1], 36, K.paint(RED, alpha, 10))
    c.drawCircle(px, py, 9, K.paint(col, alpha))
    return (cx, cy) if k < 1 else None


# ---------------------------------------------------------------- 开局：坐标纸铺开（场景 1–4）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

AJ = (1500, OY0)                # 阿杰
scene("阿杰学剪视频", "开局 · 一条曲线", (1250, 2900, 0.65), bars=2)
b.custom(J(), 0, 2.5, grid_fn)
L(axis_arrow(OX, OY0, XEND, OY0), 0, 0.9, BLACK, 11, sfx="wood_low")
L(axis_arrow(OX, OY0, OX, YTOP), 1, 1.8, BLACK, 11, sfx="wood_low")
T("本事", 740, 2350, 64, k0=2, k1=2.8, sfx="pop")
T("时间", 2000, 3490, 64, k0=2.8, k1=3.6)
L(stick(*AJ, 0.8, "hold"), 3, 3.8, BLUE, 10, sfx="wood_high")
L(face(*AJ, 0.8, "smile"), 3.8, 4.0, BLUE, 8)
L(laptop(1730, 3395), 4, 4.8, BLACK, 8, sfx="pop")
T("阿杰", AJ[0], 3060, 60, BLUE, k0=5, k1=5.8, sfx="pop")

scene("他心里那条线", "阿杰以为", (1700, 2750, 0.5))
L(bubble(1300, 2420, 560, 180, 1), 0, 0.8, BLACK, 9, sfx="wood_high")
T("每天进一点", 1300, 2420, 84, BLUE, k0=1, k1=2.25, sfx="pop")
L(P((OX, OY0), LINE_END), 2.5, 4.3, BLUE, 12, sfx="wood_high")
b.move(J(), 3, (3050, 2350, 0.5), dur=1.1)
L(star(*LINE_END, 70), 5, 5.8, ORANGE, 10, sfx="ding")
T("以为的", 2900, 2100, 84, BLUE, k0=6, k1=6.8, sfx="pop")

scene("三个月，还在地上", "真实情况", (1950, 2950, 0.4))
L(red_path(OX, 1800, wobble=4), 0, 0.9, RED, 12, sfx="wood_low")
L(red_path(1800, MONTH_X, wobble=4), 1, 1.9, RED, 12, sfx="wood_low")
L(P((MONTH_X, OY0 - 30), (MONTH_X, OY0 + 30)), 2, 2.3, BLACK, 10, sfx="pop")
T("三个月", MONTH_X, 3500, 98, RED, k0=2.3, k1=3.3)
T("剪得还很糙", 2350, 3570, 98, k0=4, k1=5.25, sfx="rim")
L(drop(1572, 3120, 1.3), 6, 6.6, BLUE, 8, sfx="pop")

J_CUT = scene("很多人在这剪断", "据书中思路", (3260, 3150, 0.8), shake=[0], flashes=[0])
b.custom(J_CUT, 0, 0.12, scissors_fn, sfx="kick")
T("咔！", 3440, 3010, 110, RED, k0=1, k1=1.8, sfx="rim")
T("多数人在这儿放弃", 3350, 2720, 80, k0=3, k1=5, sfx="pop")
L(underline(3060, 3640, 2790, 12, 40), 5, 5.8, RED, 8, sfx="ding")
L(P((CUT_X - 40, y_red(CUT_X) + 30), (CUT_X - 70, y_red(CUT_X) + 75)), 6, 6.4, RED, 8, sfx="pop")
L(P((CUT_X + 40, y_red(CUT_X) + 30), (CUT_X + 70, y_red(CUT_X) + 75)), 6.4, 6.8, RED, 8)

# ---------------------------------------------------------------- 书中观点：曲线后半段（场景 5–10）

scene("有本书讲过", "亮书", (1600, 1650, 0.85))
L(book(1300, 1700, 420, 280), 0, 0.9, BLACK, 10, sfx="wood_low")
T("《认知觉醒》", 1300, 1470, 72, GREEN, k0=1, k1=2.5, sfx="pop")
T("周岭", 1300, 1925, 60, k0=3, k1=3.8, sfx="pop")
L(wheel(1900, 1650, 150), 4, 4.9, GREEN, 9, sfx="wood_high")
T("03", 1900, 1905, 64, GREEN, k0=6, k1=6.8, sfx="ding")

scene("先慢后快", "书中观点 · 复利曲线", (3620, 2460, 0.48))
L(red_path(MONTH_X, 3700), 0, 0.9, RED, 12, sfx="wood_high")
L(red_path(3700, RED_END), 1, 1.9, RED, 12, sfx="wood_high")
L(circle(KNEE_X, y_red(KNEE_X), 75), 3, 3.7, BLACK, 9, sfx="ding")
T("拐点", KNEE_X, 3200, 89, k0=3.7, k1=4.5)
T("后面快", 4300, 2700, 89, RED, k0=5, k1=5.8, sfx="pop")
L(axis_arrow(4560, 2850, 4560, 2150, 44), 6, 6.8, GREEN, 10, sfx="wood_high")

AJ2 = (2720, y_red(2720))       # 站在缝里的阿杰
scene("中间这道缝", "落差", (2870, 2600, 0.45))
b.custom(J(), 0, 1.0, gap_fn, sfx="shaker")
L(stick(*AJ2, 0.9, "down"), 1, 1.8, BLUE, 10, sfx="wood_high")
L(face(*AJ2, 0.9, "sad"), 1.8, 2.0, BLUE, 8)
T("唉", 2560, 3020, 87, k0=3, k1=3.8, sfx="pop")
L(double_arrow(2350, y_line(2350) + 25, 3130), 4, 4.8, RED, 9, sfx="wood_high")
T("落差 = 失望", 1900, 2920, 87, RED, k0=5, k1=6.5, sfx="pop")

LENS = (3650, 2250, 210)
scene("往前看远一点", "书中观点 · 耐心", (2700, 2700, 0.46))
L(telescope(AJ2[0] + 40, AJ2[1] - 255, 2950, 2960), 0, 0.8, BLACK, 9, sfx="wood_high")
b.custom(J(), 1, 1.4, disc_fn(*LENS), sfx="pop")
L(circle(*LENS), 1.4, 2.2, BLACK, 9)
L(join(P((LENS[0] - 150, LENS[1] + 120), (LENS[0] - 20, LENS[1] + 100), (LENS[0] + 110, LENS[1] - 110)),
       star(LENS[0] + 115, LENS[1] - 125, 30)), 3, 3.8, RED, 10, sfx="wood_high")
T("咬牙硬撑", 1800, 2330, 84, k0=4, k1=5, sfx="pop")
L(P((1620, 2335), (1980, 2325)), 5, 5.5, RED, 10, sfx="rim")
T("看得远", 1800, 2480, 84, GREEN, k0=6, k1=6.8, sfx="pop")
L(check(2000, 2475, 42), 7, 7.6, GREEN, 11, sfx="ding")

MAG = (3990, y_red(3990) - 5, 120)
INSET = (3500, 4450, 1200, 1000)
scene("还会卡住几回", "书中观点 · 平台期", (3800, 2900, 0.5))
L(magnifier(*MAG), 0, 0.8, BLACK, 10, sfx="wood_high")
L(arrow((MAG[0] + 175, MAG[1] + 200), (3820, 3930), 0.12, 44), 1, 1.8, BLACK, 9, sfx="wood_low")
b.move(J(), 2, (3500, 4500, 0.85), dur=1.1)
L(rect(*INSET, 30), 3, 3.8, BLACK, 9, sfx="pop")
L(stairs(), 4, 5.0, RED, 12, sfx="wood_high")
T("平台期", 3170, 4080, 64, k0=5, k1=5.8, sfx="pop")
T("卡住", 3315, 4585, 54, RED, k0=6, k1=6.8, sfx="pop")
T("又卡住", 3745, 4325, 54, RED, k0=7, k1=7.8, sfx="pop")

scene("卡住也算数", "据书中思路", (3500, 4500, 0.85))
L(bricks(3195, 4915, 3), 0, 0.8, BLACK, 7, sfx="wood_low")
L(bricks(3195, 4865, 3, off=-6), 1, 1.8, BLACK, 7, sfx="wood_low")
L(bricks(3195, 4815, 3), 2, 2.8, BLACK, 7, sfx="wood_low")
T("表面没动", 3760, 4640, 64, k0=3, k1=4, sfx="pop")
T("底下在攒", 3760, 4790, 64, GREEN, k0=4.5, k1=5.5)
L(axis_arrow(3520, 4910, 3520, 4720, 30), 6, 6.7, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 分量与做法（场景 11–12）

WTS = [("改变", 1240, 300), ("行动", 1590, 240), ("思考", 1885, 190), ("学习", 2135, 150)]
scene("学完了，要改", "书中观点 · 成长分量", (1650, 4560, 0.85))
for n, (name, wx, ww) in enumerate(reversed(WTS)):
    k = n * 2
    shape = weight(wx, 4450, ww)
    if n:                                            # 每个大一号的秤砣右边画一个 >
        shape = join(shape, gt(wx + ww / 2 + 40, 4380))
    L(shape, k, k + 0.7, RED if name == "改变" else BLACK, 10, sfx="ding" if name == "改变" else "wood_high")
    T(name, wx, 4540, 64, RED if name == "改变" else BLACK, k0=k + 0.7, k1=k + 1.5)

scene("记一本进度本", "做法 · 示意", (1650, 5520, 0.85))
L(folder(1650, 5500, 1050, 600), 0, 0.9, BLACK, 10, sfx="wood_high")
T("进度本", 1290, 5165, 56, BLUE, k0=1, k1=1.8, sfx="pop")
for n in range(4):
    L(thumb(1290 + n * 240, 5430, n), 2 + n, 2.7 + n, BLUE if n == 3 else BLACK, 7, sfx="pop")
L(arrow((1220, 5590), (2080, 5590), 0.03, 36), 6, 6.6, GREEN, 9, sfx="wood_low")
T("回头比一比", 1650, 5700, 60, GREEN, k0=6.6, k1=7.85)

# ---------------------------------------------------------------- 回头看全图（场景 13）

BRAIN = (2540, 2770, 175)
scene("再看这条线", "回头看", (2500, 2700, 0.27))
L(red_path(CUT_X - 70, RED_END), 1, 2.2, GREEN, 18, sfx="wood_high")
b.move(J(), 3, (2560, 2830, 1.3), dur=1.1)
b.custom(J(), 4, 4.3, disc_fn(*BRAIN), sfx="pop")
L(join(circle(*BRAIN), circle(2660, 2985, 14), circle(2690, 3025, 9)), 4.3, 5.0, BLACK, 8)
L(join(elder(2440, 2890, 0.42), uncle(2550, 2890, 0.42)), 5, 5.8, BLACK, 7, sfx="wood_low")
L(baby(2650, 2890, 0.5), 5.8, 6.4, BLUE, 7)
L(wheel(2658, 2805, 36, grips=2), 6, 6.7, GREEN, 6, sfx="wood_high")
L(grip(2658, 2805, 36, 2), 7, 7.5, RED, 7, sfx="ding")          # 第 3 道握痕：本讲新增

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FULL = (2400, 3820, 0.19)
scene("评论区聊聊", "评论区见", FULL, bars=4)
H(0, "cymbal", 0.5)
H(2, "ding")
b.move(J(), 4, (3500, 5900, 0.8), dur=1.1)
H(4, "wood_high", 0.6)
L(join(rect(3500, 5900, 1220, 420, 30), circle(3010, 5790, 40)), 5, 5.8, BLACK, 8, sfx="wood_low")
T("你在哪件事上快剪断了？", 3540, 5800, 72, RED, k0=6, k1=8.75, sfx="pop")
T("下一讲：被说一句就上头，怎么刹住？", 3500, 5990, 48, k0=9, k1=13.25, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "patience", "耐心", "学了三个月没起色，还学吗？", ACC, b.shots,
                 [f"{BOOK}第一章第三节“耐心：得耐心者得天下”（转述）"],
                 "学了三个月|没起色还【学吗】", SQUARE_SHOT,
                 ["书中观点均为转述，不是逐字引文：耐心靠的是长远目光，跟毅力关系不大，缺乏耐心是人的天性；复利曲线前期"
                  "增长慢，过了拐点才快；学习有平台期，进步是波浪式上升、中间会停滞；成长的分量排序为改变 > 行动 > 思考 > 学习"
                  "（第一章第三节，据多篇读书笔记一致转述）。出处：周岭《认知觉醒：开启自我改变的原动力》（人民邮电出版社 2020）。",
                  "“多数人在拐点前放弃”“平台期底下在攒”为据书中思路的通俗化说法；坐标纸上的直线、曲线、拐点位置、台阶和砖块"
                  "都是示意图，不是数据。",
                  "阿杰下班学剪视频的三个月、进度本（每周存一条作品、回头对比）均为示意，据书中思路整理，不指向任何具体公司或个人。",
                  "脑内三兄弟（拄拐的本能脑、戴耳机的情绪脑、抱舵的理智脑宝宝）为本系列的视觉角色，据第一章“按年纪比”的比喻"
                  "与第三章“思维舵手”的说法设计；舵上三道握痕表示系列进度（第 N 讲 N 道，红色那道为本讲新增）。"],
                 tags="#坚持 #学习方法")
    return b.attach(ep)
