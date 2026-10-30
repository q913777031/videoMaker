"""03 看起来很忙（白板手绘版）：忙了一整天，干成了啥？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事形式 D 误区对照：一句常见说法开局（下班前小周喊“忙死了！”，日报却一行没写）→
好像很忙（开了四个会、回了一百条消息，小红点 99+）→ 正事没动（项目进度条五格专注块一格没亮）→
drop：小红点被当成“勤奋勋章”一个个挂满小周胸前，旁边进度条一格没动 →
亮书（《深度工作》+ 卡尔·纽波特名牌，书里讲了专注越来越少见的三个坑）→
三行误区对照，每行左边 ✗ 常见说法、右边 ✓ 书里怎么说，再配一屏例子：
  坑① ✗ 秒回才靠谱 / ✓ 分心的代价没人算（度量黑洞）→ 例：周报表里各栏都有数，“打断”这栏空着；
  坑② ✗ 群里喊一声最省事 / ✓ 人总挑眼下最省事的做法（最小阻力）→ 例：一个 @所有人，一屋子人头上冒红点；
  坑③ ✗ 忙就是干得多 / ✓ 说不清成果，就拿看得见的忙充数 → 天平：一堆消息泡泡比不过一份成品 →
做法（日报只写做完的事；先别 @所有人，攒到下午集中对一次）→ 拉远看三行对照 → 评论区互动。
书中观点为转述（卡尔·纽波特《深度工作》第一部分第2章“深度工作是少见的”：度量黑洞、最小阻力原则、
忙碌代表生产力）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               desk, doc, face, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#B8452F"
SQUARE_SHOT = 3                 # 场景 4：小周胸前挂满小红点勋章 + 一格没动的进度条

b = Board(size=(3600, 11400))


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

def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """小周：戴工牌的火柴人（(x, y) 为脚底）。"""
    hy = y - 290 * s
    return join(stick(x, y, s, arms),
                P((x - 22 * s, hy + 48 * s), (x + 18 * s, hy + 118 * s)), rect(x + 26 * s, hy + 145 * s, 44 * s, 54 * s, 6 * s))


def reddot(x, y, r, label, legs=True):
    """小红点：红色实心圆 + 白字数字 + 两条小短腿，弹出来。"""

    def fn(c, k, t):
        s = ease_out(clamp01(k * 1.4)) * (1 + 0.22 * math.sin(math.pi * clamp01(k)))
        if s <= 0:
            return None
        if legs:
            lw = max(4.0, r * 0.12)
            for dx in (-0.35, 0.35):
                x0 = x + dx * r
                c.drawPath(P((x0, y + r * 0.85), (x0, y + r * 1.45), (x0 + dx * r * 0.7, y + r * 1.45)),
                           K.paint(BLACK, clamp01(k * 2), lw))
        K.dot(c, x, y, r * s, RED)
        c.drawCircle(x, y, r * s, K.paint("#9E2219", 1, max(3.0, r * 0.08)))
        size = r * (1.05 if len(label) <= 1 else 0.85 if len(label) == 2 else 0.62) * s
        K.text(c, label, x, y, size, "black", "#FFFFFF")
        return None

    return fn


def medal(x, y, neck) -> skia.Path:
    """勋章挂带：从领口两侧拉到勋章顶上的 V 形带子。"""
    nx, ny = neck
    return join(P((nx - 18, ny), (x - 14, y - 30)), P((nx + 18, ny), (x + 14, y - 30)))


def block_row(x0, y, n=5, w=130, h=110, gap=14) -> skia.Path:
    """进度条：一排专注块空格。"""
    return join(*[rect(x0 + w / 2 + i * (w + gap), y, w, h, 10) for i in range(n)])


def fill_fn(x, y, w, h, color=BLUE, alpha=0.35):
    """方块从左往右涂满。"""

    def fn(c, k, t):
        K.rr(c, x - w / 2 + w * k / 2, y, w * k, h, 10, color, alpha)
        return None

    return fn


def meeting(x, y) -> skia.Path:
    """会议桌：长桌 + 三个人头。"""
    parts = [rect(x, y + 40, 300, 70, 30)]
    for dx in (-100, 0, 100):
        parts += [circle(x + dx, y - 40, 30), P((x + dx - 40, y + 5), (x + dx - 30, y - 5), (x + dx + 30, y - 5),
                                                (x + dx + 40, y + 5))]
    return join(*parts)


def phone(x, y, w=150, h=250) -> skia.Path:
    return join(rect(x, y, w, h, 20), P((x - w * 0.17, y + h / 2 - 26), (x + w * 0.17, y + h / 2 - 26)))


def spiral(x, y, r=170, turns=3.2) -> skia.Path:
    """黑洞：由外往里的螺旋。"""
    pts = []
    n = 120
    for i in range(n + 1):
        f = i / n
        a = f * turns * 2 * math.pi
        rr = r * (1 - f * 0.92)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a) * 0.7))
    return P(*pts)


def msg(x, y, w=58, h=34) -> skia.Path:
    """小消息泡：圆角框 + 小尾巴。"""
    return join(rect(x, y, w, h, 12), P((x - w * 0.2, y + h / 2), (x - w * 0.3, y + h / 2 + 12), (x - w * 0.05, y + h / 2)))


def hill(x0, y0, x1, y1) -> skia.Path:
    """下坡：从左上弯到右下的坡面 + 地面。"""
    p = skia.Path()
    p.moveTo(x0, y0)
    p.cubicTo(x0 + (x1 - x0) * 0.35, y0, x0 + (x1 - x0) * 0.55, y1, x1, y1)
    p.lineTo(x1 + 60, y1)
    return join(p, P((x0, y0), (x0, y1), (x1 + 60, y1)))


def hill_pt(x0, y0, x1, y1, f):
    """坡面上 f（0–1）处的点（与 hill 的三次曲线一致）。"""
    ax, bx, cx_, dx = x0, x0 + (x1 - x0) * 0.35, x0 + (x1 - x0) * 0.55, x1
    ay, by, cy, dy = y0, y0, y1, y1
    u = 1 - f
    return (u ** 3 * ax + 3 * u * u * f * bx + 3 * u * f * f * cx_ + f ** 3 * dx,
            u ** 3 * ay + 3 * u * u * f * by + 3 * u * f * f * cy + f ** 3 * dy)


def ball_fn(hl, r=34):
    def fn(c, k, t):
        f = k * k
        x, y = hill_pt(*hl, f)
        K.dot(c, x, y - r, r, "#E07B24")
        c.drawCircle(x, y - r, r, K.paint(BLACK, 1, 5))
        return None

    return fn


def scale(x, y, tilt=60, arm=200, r=90) -> skia.Path:
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


# ---------------------------------------------------------------- 开局：一句常见说法（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


scene("今天干啥了", "一句常见话", (1000, 900, 0.85), bars=2)
L(bubble(760, 640, 420, 150, -1), 0, 0.5, BLACK, 8, sfx="pop")
T("忙死了！", 760, 640, 72, RED, k0=0.5, k1=1.5)
L(zhou(640, 1290, 0.8), 2, 2.8, BLACK, 10, sfx="wood_high")
L(face(640, 1290, 0.8, "flat"), 2.8, 3.0)
L(doc(1160, 1060, 260, 330, 0), 3, 3.8, BLACK, 9, sfx="wood_high")
T("日报", 1160, 980, 60, k0=3.8, k1=4.6)
T("干了啥？", 1160, 1150, 60, RED, k0=5, k1=6, sfx="rim")

scene("好像很忙", "一句常见话", (2500, 900, 0.85))
L(meeting(2180, 650), 0, 0.9, BLACK, 9, sfx="wood_high")
T("开会 × 4", 2720, 650, 72, k0=1, k1=2.5, sfx="pop")
L(phone(2180, 1030), 3, 3.8, BLACK, 9, sfx="wood_high")
T("消息 × 100", 2740, 1030, 72, k0=4, k1=5.5, sfx="pop")
C(reddot(2265, 915, 46, "99+"), 6, 6.6, sfx="ding")
T("好忙！", 2500, 1330, 90, RED, k0=7, k1=7.9, sfx="pop")

ZHOU = (1250, 2900, 1.3)         # 场景 3–4 的小周：脚底 (x, y)、缩放
BAR = (1580, 2470)               # 进度条左端、中线
scene("正事没动", "一句常见话", (1700, 2550, 0.85))
L(zhou(*ZHOU), 0, 0.9, BLACK, 10, sfx="wood_high")
L(face(*ZHOU, "sad"), 0.9, 1.1)
T("项目进度", 1945, 2270, 64, k0=2, k1=3, sfx="pop")
L(block_row(*BAR), 3, 4.2, BLUE, 9, sfx="wood_low")
T("0%", 1945, 2680, 120, RED, k0=5, k1=5.9, sfx="pop")
L(circle(1945, 2680, 120), 6, 6.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- drop：勤奋勋章（场景 4）

NECK = (ZHOU[0], ZHOU[1] - 290 * ZHOU[2] + 50)
MEDALS = [(1185, 2660, "4"), (1315, 2660, "9"), (1250, 2745, "99+"), (1160, 2790, "1"), (1340, 2790, "5")]
scene("忙成了勋章", "小红点 · 勤奋勋章", (1640, 2560, 0.78), shake=[0], flashes=[0])
for n, (mx, my, lab) in enumerate(MEDALS):
    L(medal(mx, my, NECK), n, n + 0.4, RED, 6, sfx="kick" if n == 0 else "ding" if n % 2 else "pop")
    C(reddot(mx, my, 40 if lab != "99+" else 50, lab, legs=False), n + 0.3, n + 0.8)
T("勤奋勋章", 1250, 2380, 76, RED, k0=5, k1=6, sfx="pop")
T("一格没动", 1945, 2900, 72, k0=6, k1=7, sfx="rim")
L(underline(1790, 2100, 2960, 10, 34), 7, 7.8, RED, 7, sfx="tom")

# ---------------------------------------------------------------- 亮书（场景 5）

scene("书里说三个坑", "《深度工作》· 书中观点", (1700, 3800, 0.85))
L(book(1360, 3720, 420, 280), 0, 0.9, BLACK, 10, sfx="wood_low")
T("《深度工作》", 1360, 3440, 72, GREEN, k0=1, k1=2.5, sfx="pop")
L(rect(1360, 4040, 360, 90, 16), 3, 3.4, BLACK, 7, sfx="wood_high")
T("卡尔 · 纽波特", 1360, 4040, 54, k0=3.4, k1=4.6)
for n in range(3):
    L(rect(2060, 3470 + n * 230, 340, 170, 18), 5 + n * 0.5, 5.4 + n * 0.5, RED, 8, sfx="pop" if n == 0 else None)
    T(f"坑 {'①②③'[n]}", 2060, 3470 + n * 230, 64, RED, k0=5.4 + n * 0.5, k1=5.9 + n * 0.5)
H(6, "wood_high")

# ---------------------------------------------------------------- 三行误区对照（场景 6–10）
# 每行左边 ✗ 常见说法（x 520–1080），右边 ✓ 书里怎么说（x 1120–1700）；例子放在同一行右侧（x≈2600）。

ROWS = [5200, 6500, 7800]


def pair(ry, saying, sfx_draw):
    """一行对照的框架：中线 + 左边红叉与常见说法气泡 + 右边绿勾与“书里说”。返回绘制顺序的起点拍。"""
    L(P((1100, ry - 400), (1100, ry + 400)), 0, 0.5, BLACK, 6, sfx="wood_low")
    L(cross(600, ry - 300, 44), 0.5, 0.9, RED, 10)
    L(bubble(800, ry - 30, 500, 170, -1), 1, 1.4, BLACK, 8, sfx="pop")
    T(saying, 800, ry - 30, 58, k0=1.4)
    L(check(1190, ry - 300, 40), 3, 3.4, GREEN, 10, sfx="ding")
    T("书里说", 1340, ry - 300, 56, GREEN, k0=3.4, k1=4.0)


R1 = ROWS[0]
scene("代价没人算", "坑① · 度量黑洞", (1100, R1, 0.85))
pair(R1, "秒回才靠谱", None)
L(spiral(1410, R1 - 20, 170), 4, 4.9, BLACK, 8, sfx="tom")
T("度量黑洞", 1410, R1 + 150, 56, k0=5, k1=6, sfx="pop")
T("代价没人算", 1410, R1 + 290, 66, RED, k0=6, k1=7.25, sfx="pop")

TBL = (2600, R1 + 60)
scene("表里没这一栏", "坑① · 例子", (2600, R1, 0.85))
T("周报表（示意）", 2600, R1 - 380, 60, k0=0, k1=1.5, sfx="pop")
L(join(rect(*TBL, 1080, 420, 12), P((2060, TBL[1] - 70), (3140, TBL[1] - 70)),
       *[P((2060 + i * 270, TBL[1] - 210), (2060 + i * 270, TBL[1] + 210)) for i in (1, 2, 3)]), 2, 2.9, BLACK, 8,
  sfx="wood_high")
for n, (hd, val) in enumerate((("工时", "10h"), ("会议", "4"), ("消息", "100"))):
    x = 2195 + n * 270
    T(hd, x, TBL[1] - 140, 54, k0=3 + n * 0.4, k1=3.4 + n * 0.4, sfx="pop" if n == 0 else None)
    T(val, x, TBL[1] + 70, 64, BLUE, k0=4.4 + n * 0.4, k1=4.8 + n * 0.4, sfx="wood_high" if n == 0 else None)
T("打断", 3005, TBL[1] - 140, 54, RED, k0=6, k1=6.8, sfx="rim")
T("？", 3005, TBL[1] + 70, 90, RED, k0=7, k1=7.6, sfx="ding")

R2 = ROWS[1]
HILL = (1170, R2 - 160, 1600, R2 + 170)
scene("人爱走下坡", "坑② · 最小阻力", (1100, R2, 0.85))
pair(R2, "喊一声最省事", None)
L(hill(*HILL), 4, 4.8, BLACK, 8, sfx="wood_high")
T("随手@人", 1590, R2 + 250, 52, RED, k0=5, k1=6, sfx="pop")
C(ball_fn(HILL), 6, 7, sfx="shaker")
T("挑最省事的", 1390, R2 + 370, 60, RED, k0=6, k1=7.25)
H(7, "tom", 0.7, "球滚到坡底")

HEADS = [2180 + i * 210 for i in range(5)]
scene("一喊全停", "坑② · 例子", (2600, R2, 0.85))
T("@所有人", 2600, R2 - 380, 80, RED, k0=0, k1=1.2, sfx="pop")
L(arrow((2600, R2 - 320), (2600, R2 - 160), 0, 36), 1.4, 1.9, RED, 8)
for n, x in enumerate(HEADS):
    L(stick(x, R2 + 300, 0.5), 2 + n * 0.3, 2.3 + n * 0.3, BLACK, 8, sfx="wood_high" if n == 0 else None)
for n, x in enumerate(HEADS):
    C(reddot(x + 40, R2 - 30, 30, "1", legs=False), 4 + n * 0.5, 4.4 + n * 0.5, sfx="ding" if n % 2 == 0 else None)
T("全停下", 2600, R2 + 390, 72, k0=7, k1=7.8, sfx="rim")

R3 = ROWS[2]
SC = (1420, R3 + 200)
scene("忙拿来充数", "坑③ · 拿忙充数", (1100, R3, 0.85))
pair(R3, "忙就是干得多", None)
L(scale(*SC, 60), 4, 4.9, BLACK, 8, sfx="wood_high")
LP, RP = (SC[0] - 200, SC[1] - 300 - 60), (SC[0] + 200, SC[1] - 300 + 60)
L(join(msg(LP[0] - 34, LP[1] + 108), msg(LP[0] + 34, LP[1] + 108), msg(LP[0], LP[1] + 66)), 5, 5.6, BLUE, 6, sfx="pop")
L(doc(RP[0], RP[1] + 78, 70, 90, 2), 6, 6.5, GREEN, 7, sfx="ding")
T("拿忙充数", 1420, R3 + 330, 64, RED, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 做法（场景 11–12）

DR = (2600, R3 + 20)
scene("只写做完的", "做法 · 日报", (2600, R3, 0.85))
L(doc(*DR, 820, 760, 0), 0, 0.9, BLACK, 9, sfx="wood_high")
T("今天做完了什么？", 2560, R3 - 250, 58, k0=1, k1=3, sfx="pop")
T("开会 × 4", 2420, R3 - 100, 54, k0=3, k1=3.8, sfx="pop")
T("回消息 × 100", 2490, R3 + 20, 54, k0=3.9, k1=4.9)
L(join(P((2290, R3 - 100), (2560, R3 - 100)), P((2290, R3 + 20), (2700, R3 + 20))), 5, 5.6, RED, 9, sfx="rim")
L(rect(2390, R3 + 200, 150, 110, 10), 6, 6.5, BLUE, 9, sfx="wood_low")
C(fill_fn(2390, R3 + 200, 150, 110), 6.5, 7.0)
T("方案第一节", 2700, R3 + 200, 58, GREEN, k0=7, k1=8, sfx="ding")

Y12 = 9050
scene("攒到一起说", "做法 · 先别@所有人", (2600, Y12, 0.85))
L(rect(2600, Y12 + 20, 1000, 860, 36), 0, 0.9, BLACK, 9, sfx="wood_high")
L(bubble(2560, Y12 - 230, 520, 140, -1), 1, 1.5, BLACK, 8, sfx="pop")
T("@所有人 在吗", 2560, Y12 - 230, 54, k0=1.5, k1=2.8)
L(cross(2560, Y12 - 230, 90), 3, 3.6, RED, 11, sfx="rim")
L(arrow((2560, Y12 - 120), (2560, Y12 + 30), 0, 34), 4, 4.5, BLACK, 8, sfx="wood_high")
L(bubble(2560, Y12 + 140, 640, 150, -1), 5, 5.4, GREEN, 8, sfx="pop")
T("下午四点一起对", 2560, Y12 + 140, 58, GREEN, k0=5.4, k1=7.0)
L(join(clock(2960, Y12 + 330, 60), P((2960, Y12 + 330), (2960, Y12 + 290)), P((2960, Y12 + 330), (2990, Y12 + 345))),
  7, 7.8, BLACK, 7, sfx="ding")

# ---------------------------------------------------------------- 拉远：三行对照一起看（场景 13）

scene("三个坑", "三个坑", (1800, 6500, 0.277))
for n, ry in enumerate(ROWS):
    L(circle(290, ry, 120), n, n + 0.6, RED, 14, sfx="pop")
    T("①②③"[n], 290, ry, 150, RED, k0=n + 0.6, k1=n + 1.0)
for n, ry in enumerate(ROWS):
    L(underline(1170, 1680, ry + 380, 18, 50), 4 + n, 4.8 + n, RED, 14, sfx="ding" if n != 1 else "tom")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FULL = (1800, 5700, 0.085)
END = (1800, 10300, 0.8)
scene("评论区聊聊", "评论区见", FULL, bars=4)
J_END = J()
b.move(J_END, 4, END, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("今天哪件事最像瞎忙？", 1800, 10220, 74, RED, k0=6, k1=8.5, sfx="pop")
C(reddot(2280, 10095, 36, "1"), 7, 7.6)
T("下一讲：刷了一晚手机，怎么更累了？", 1800, 10380, 50, k0=9, k1=13.25, sfx="wood_high")
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "busy", "看起来很忙", "忙了一整天，干成了啥？", ACC, b.shots,
                 [f"{BOOK}第一部分第2章“深度工作是少见的”：度量黑洞、最小阻力原则、忙碌代表生产力（转述）",
                  "中译本：宋伟译，江西人民出版社 · 后浪 2017；民主与建设出版社 · 后浪 2023"],
                 "忙了一整天|到底【干成了啥】", SQUARE_SHOT,
                 ["书中观点均为转述（第一部分第2章“深度工作是少见的”）：分心对工作的损害很难算清，公司也就不去算"
                  "（“度量黑洞”）；没有清楚反馈时，人会挑眼下最省事的做法，比如随时发消息、随时回消息（“最小阻力原则”）；"
                  "说不清什么算干得好，人就用看得见的忙碌来表现自己在干活（“忙碌代表生产力”）。上屏均为转述，不是逐字引文。",
                  "下班前喊“忙死了”、开会 4 次、消息 100 条、99+ 红点、进度条 0%、周报表各栏数字、@所有人一屋子人停下、"
                  "天平一图均为现实场景示意与通俗化示意，不是数据；不指向任何具体公司、个人或软件。",
                  "两条做法（日报只写今天做完的事；先别随手 @所有人，把要对的事攒到下午集中对一次）为据书中思路整理的建议。",
                  "书中章节名不上屏，只写在出处里。"],
                 tags="#职场")
    return b.attach(ep)
