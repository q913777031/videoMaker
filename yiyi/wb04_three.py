"""04 三条路（白板手绘版）：意义从哪来？书里给了三条路

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（形式 J：一个比喻贯穿）：整讲是一张三岔路口的地图，阿宁手里的小罗盘带路。
开局阿宁站在路口发懵、罗盘乱转 → 别人立的路牌（赚大钱、出名、躺平）罗盘都没反应 → 亮书，路面裂出三条线 →
drop：三块红路牌一起砸下（做一件事 / 爱一个人 / 扛住难事），罗盘指针分成三叉 →
沿三条路各走两站：路牌（书中观点）+ 身边例子（修好打印机、陪妈逛菜市场、爸住院每天问清医生一件事）→
拉远看全图：三条路汇到远处同一面旗 → 做法（三条路各走一小步 / 一条堵了换一条，罗盘跟着转）→ 评论区。
书中观点为转述：意义的三条途径见第二部分〈生命之意义〉，第二条里的“爱一个人”见〈爱之意义〉
（Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010）；
例子为示意，做法据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import ease_out
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, face,
                               join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#3F7D74"
SQUARE_SHOT = 10                # 场景 11：三条路全图 + 阿宁 + 罗盘
GRAY = "#7D828C"

b = Board(size=(3600, 9000))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def TL(s, xl, y, size=60, color=BLACK, k0=0.0, k1=None, sfx=None):
    """左对齐写字：xl 为左端。"""
    T(s, xl + K.text_w(s, size, "hand") / 2, y, size, color, k0, k1, sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


# ---------------------------------------------------------------- 本讲画法

def road(x, y0, y1, w=110) -> skia.Path:
    """一段竖直的路：两条路边 + 中间几道虚线。y0 为近端（下），y1 为远端（上）。"""
    parts = [P((x - w / 2, y0), (x - w / 2, y1)), P((x + w / 2, y0), (x + w / 2, y1))]
    n = int(abs(y0 - y1) // 160)
    for i in range(n):
        yy = y0 - 60 - i * 160
        parts.append(P((x, yy), (x, yy - 60)))
    return join(*parts)


def road_curve(a, z, w=110) -> skia.Path:
    """连接两段路的弯路（两条路边），起止都竖直。"""
    (x0, y0), (x1, y1) = a, z
    my = (y0 + y1) / 2
    parts = []
    for d in (-w / 2, w / 2):
        p = skia.Path()
        p.moveTo(x0 + d, y0)
        p.cubicTo(x0 + d, my, x1 + d, my, x1 + d, y1)
        parts.append(p)
    return join(*parts)


def sign(x, y, ground, w=300, h=110) -> skia.Path:
    """路牌：牌面 (x, y) + 立柱到地面 ground。"""
    return join(rect(x, y, w, h, 14), P((x, y + h / 2), (x, ground)))


def compass(x, y, r=50) -> skia.Path:
    """系列视觉角色·小罗盘：圆框 + 内圈 + 四个刻度 + 顶上小环（指针另由 needle_fn 画）。"""
    parts = [circle(x, y, r), circle(x, y - r - r * 0.24, r * 0.24)]
    for a in range(4):
        ang = a * math.pi / 2
        parts.append(P((x + math.cos(ang) * r * 0.86, y + math.sin(ang) * r * 0.86),
                       (x + math.cos(ang) * r * 0.68, y + math.sin(ang) * r * 0.68)))
    return join(*parts)


def crack(a, z, n=7, amp=16) -> skia.Path:
    """路面裂开的折线。"""
    (x0, y0), (x1, y1) = a, z
    L_ = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L_, (x1 - x0) / L_
    pts = [(x0, y0)]
    for i in range(1, n):
        f = i / n
        s = amp * (1 if i % 2 else -1)
        pts.append((x0 + (x1 - x0) * f + nx * s, y0 + (y1 - y0) * f + ny * s))
    pts.append((x1, y1))
    return P(*pts)


def wrench(x, y, s=1.0) -> skia.Path:
    """扳手：开口朝右上的扳手头 + 斜向左下的手柄（带挂孔）。"""
    hx, hy, r = x + 70 * s, y - 70 * s, 55 * s
    head = skia.Path()
    head.addArc(skia.Rect.MakeXYWH(hx - r, hy - r, 2 * r, 2 * r), -5, 280)
    ang = math.radians(135)
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy * 20 * s, ux * 20 * s
    sx, sy = hx + ux * r * 0.95, hy + uy * r * 0.95
    ex, ey = hx + ux * 260 * s, hy + uy * 260 * s
    handle = join(P((sx + px, sy + py), (ex + px, ey + py)), P((sx - px, sy - py), (ex - px, ey - py)),
                  P((ex + px, ey + py), (ex - px, ey - py)))
    return join(head, handle, circle(ex - ux * 30 * s, ey - uy * 30 * s, 8 * s))


def heart(x, y, r=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def sunset(x, y, r=70) -> skia.Path:
    """晚霞：地平线 + 半个太阳 + 几道光。(x, y) 为太阳圆心（落在地平线上）。"""
    sun = skia.Path()
    sun.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 180, 180)
    parts = [P((x - r * 2.3, y), (x + r * 2.3, y)), sun]
    for a in (200, 240, 270, 300, 340):
        ang = math.radians(a)
        parts.append(P((x + math.cos(ang) * r * 1.3, y + math.sin(ang) * r * 1.3),
                       (x + math.cos(ang) * r * 1.75, y + math.sin(ang) * r * 1.75)))
    parts.append(P((x - r * 1.6, y + 30), (x - r * 0.4, y + 30)))
    parts.append(P((x + r * 0.3, y + 55), (x + r * 1.5, y + 55)))
    return join(*parts)


def printer(x, y, w=300, h=150) -> skia.Path:
    """打印机：机身 + 顶上进纸 + 前面出纸 + 按钮。"""
    return join(rect(x, y, w, h, 16), P((x - w * 0.3, y - h / 2), (x - w * 0.22, y - h / 2 - 80),
                                         (x + w * 0.22, y - h / 2 - 80), (x + w * 0.3, y - h / 2)),
                P((x - w * 0.38, y + h * 0.15), (x + w * 0.38, y + h * 0.15)),
                P((x - w * 0.28, y + h * 0.15), (x - w * 0.28, y + h / 2 + 50), (x + w * 0.28, y + h / 2 + 50),
                  (x + w * 0.28, y + h * 0.15)),
                circle(x + w * 0.38, y - h * 0.22, 10))


def papers(x, y, n=4, w=200) -> skia.Path:
    """一摞纸：n 张错开叠放。(x, y) 为最上一张中心。"""
    parts = []
    for i in range(n):
        yy = y + i * 26
        parts.append(P((x - w / 2 + i * 6, yy), (x + w / 2 + i * 6, yy)))
    parts.append(rect(x, y - 50, w, 100, 6))
    return join(*parts)


def stall(x, y, w=360) -> skia.Path:
    """菜摊：波浪边雨棚 + 两根柱 + 桌面 + 几个菜。(x, y) 为桌面中点。"""
    top = y - 260
    aw = skia.Path()
    aw.moveTo(x - w / 2, top)
    aw.lineTo(x + w / 2, top)
    aw.lineTo(x + w / 2, top + 50)
    n = 5
    for i in range(n):
        xa = x + w / 2 - i * w / n
        aw.quadTo(xa - w / n / 2, top + 95, xa - w / n, top + 50)
    aw.close()
    parts = [aw, P((x - w / 2 + 20, top + 50), (x - w / 2 + 20, y + 120)),
             P((x + w / 2 - 20, top + 50), (x + w / 2 - 20, y + 120)), P((x - w / 2 - 10, y), (x + w / 2 + 10, y))]
    for dx, r in ((-110, 34), (-40, 30), (40, 36), (115, 30)):
        parts.append(circle(x + dx, y - r, r))
    parts.append(P((x - 40, y - 60), (x - 30, y - 85)))
    return join(*parts)


def rock(x, y, w=220, h=120) -> skia.Path:
    return P((x - w / 2, y + h * 0.2), (x - w * 0.38, y - h * 0.35), (x - w * 0.05, y - h / 2), (x + w * 0.3, y - h * 0.4),
             (x + w / 2, y), (x + w * 0.38, y + h / 2), (x - w * 0.3, y + h / 2), close=True)


def bed(x, y, w=340) -> skia.Path:
    """病床：床头 + 床面 + 床腿 + 枕头 + 躺着的人（头 + 被子）。(x, y) 为床面中点。"""
    l, r = x - w / 2, x + w / 2
    blanket = skia.Path()
    blanket.moveTo(l + 90, y)
    blanket.quadTo(l + 120, y - 70, l + 200, y - 60)
    blanket.quadTo(r - 40, y - 60, r - 10, y)
    return join(P((l, y - 150), (l, y + 110)), P((l, y), (r, y), (r, y + 110)), P((r, y - 60), (r, y)),
                rect(l + 60, y - 22, 80, 36, 14), circle(l + 60, y - 72, 32), blanket)


def note(x, y, w=300, h=220) -> skia.Path:
    """便签：右下角折起。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2),
                  (x - w / 2, y + h / 2), close=True),
                P((x + w / 2, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2)))


def barrier(x, y, w=170, h=50) -> skia.Path:
    """路障：横板 + 三道斜纹 + 两条腿。"""
    parts = [rect(x, y, w, h, 6), P((x - w / 2 + 20, y + h / 2), (x - w / 2 + 10, y + h / 2 + 50)),
             P((x + w / 2 - 20, y + h / 2), (x + w / 2 - 10, y + h / 2 + 50))]
    for i in range(3):
        x0 = x - w / 2 + 30 + i * 50
        parts.append(P((x0, y + h / 2), (x0 + 40, y - h / 2)))
    return join(*parts)


def flag(x, y, h=300) -> skia.Path:
    """旗：(x, y) 为旗杆底。"""
    return join(P((x, y), (x, y - h)), P((x, y - h), (x + 190, y - h + 55), (x, y - h + 110)))


# ---------------------------------------------------------------- 动态：罗盘指针、红路牌砸下

def _settle(u):
    return 1 - math.exp(-7 * u) * math.cos(12 * u)


def needle_fn(x, y, r, keys):
    """罗盘指针。keys：[(镜头, 拍, "spin", 每秒圈数) | (镜头, 拍, "point", [角度…])]；
    spin 乱转，point 叮一声带回弹停到目标（多个角度 = 指针分叉）。角度为屏幕坐标弧度（正上方 -π/2）。"""

    def angles(T):
        cur = [-math.pi / 2]
        times = [b.t_of(j, k) for j, k, _, _ in keys]
        for i, (_, _, kind, val) in enumerate(keys):
            t0 = times[i]
            if T < t0:
                break
            te = min(T, times[i + 1]) if i + 1 < len(times) else T
            u = te - t0
            if kind == "spin":
                cur = [cur[0] + 2 * math.pi * val * u + 0.8 * math.sin(5 * u)]
            else:
                out = []
                for n, tg in enumerate(val):
                    base = cur[min(n, len(cur) - 1)]
                    tg = base + (tg - base + math.pi) % (2 * math.pi) - math.pi
                    out.append(base + (tg - base) * _settle(u))
                cur = out
        return cur

    def fn(c, k, T):
        angs = angles(T)
        for a in angs:
            ca, sa = math.cos(a), math.sin(a)
            px, py = -sa * r * 0.17, ca * r * 0.17
            tip = (x + ca * r * 0.74, y + sa * r * 0.74)
            c.drawPath(P(tip, (x + px, y + py), (x - px, y - py), close=True), K.paint(RED))
            if len(angs) == 1:
                tail = (x - ca * r * 0.5, y - sa * r * 0.5)
                c.drawPath(P(tail, (x + px, y + py), (x - px, y - py), close=True), K.paint(BLACK))
        K.dot(c, x, y, r * 0.1, BLACK)
        return None

    return fn


def slam_fn(signs, w=360, h=150, size=58):
    """红路牌从大到小砸下，盖住原来的灰路牌。signs：[(x, y, 字)]。"""

    def fn(c, k, T):
        e = ease_out(k)
        sc, a = 1.7 - 0.7 * e, min(1.0, k * 2.5)
        for x, y, s in signs:
            c.save()
            c.translate(x, y)
            c.scale(sc, sc)
            K.rr(c, 0, 0, w, h, 18, "#FBFBF9", a)
            c.drawPath(rect(0, 0, w, h, 18), K.paint(RED, a, 10))
            K.text(c, s, 0, 0, size, "hand", RED, a)
            c.restore()
        return None

    return fn


# ---------------------------------------------------------------- 路口（场景 1–4）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


NING = (1800, 5500)             # 阿宁站在路口（脚底）
CP = (1945, 5320)               # 阿宁手里的罗盘
SIGNS = [(1350, 4760, 4960), (1800, 4630, 4890), (2250, 4760, 4960)]   # 三块路牌：(x, y, 立柱落地)
CRACKS = [((1640, 5470), (1350, 4960)), ((1800, 5215), (1800, 4890)), ((2020, 5470), (2250, 4960))]


def _ang(p):
    return math.atan2(p[1] - CP[1], p[0] - CP[0])


scene("站在路口发懵", "路口 · 往哪走", (1800, 5180, 0.85), bars=2)
J1 = J()
L(join(P((1720, 5760), (1720, 5570), (1600, 5480)), P((1880, 5760), (1880, 5570), (2000, 5480))), 0, 0.9, GRAY, 9,
  sfx="wood_low")
L(stick(*NING, 0.75, "hold"), 1, 1.8, BLUE, 10, sfx="pop")
L(face(*NING, 0.75, "flat"), 1.8, 2.0, BLUE, 8)
L(compass(*CP, 50), 3, 3.8, BLACK, 7, sfx="wood_high")
b.custom(J1, 4, 4.6, needle_fn(*CP, 50, [(J1, 4, "spin", 1.5),
                                          (J1 + 3, 0, "point", [_ang((x, y)) for x, y, _ in SIGNS])]), sfx="shaker")
T("往哪走？", 1330, 5300, 72, RED, k0=5, k1=6.0, sfx="pop")

scene("路牌都不对", "路口 · 别人的路牌", (1800, 4900, 0.8))
for n, (x, y, g) in enumerate(SIGNS):
    L(sign(x, y, g), 2 * n, 2 * n + 0.8, GRAY, 8, sfx="wood_high")
    T(["赚大钱", "出名", "躺平"][n], x - 20, y, 56, GRAY, k0=2 * n + 0.8, k1=2 * n + 1.6)
for n, (x, y, _) in enumerate(SIGNS):
    T("？", x + 128, y - 40, 60, RED, k0=6 + n * 0.6, k1=6.4 + n * 0.6, sfx="rim" if n < 2 else None)
H(8, "shaker", 0.6, "罗盘还在乱转")

scene("书里给了三条路", "活出生命的意义 · 书中观点", (1850, 5080, 0.8))
L(book(2360, 5410, 260, 170), 0, 0.9, BLACK, 9, sfx="wood_low")
T("弗兰克尔", 2360, 5160, 46, k0=1, k1=2.0, sfx="pop")
T("活出生命的意义", 2360, 5235, 46, GREEN, k0=2, k1=3.75, sfx="pop")
for n, (a, z) in enumerate(CRACKS):
    L(crack(a, z), 5 + n, 5.8 + n, BLACK, 6, sfx=["wood_high", "wood_low", "wood_high"][n])

scene("三条路，都通", "书中观点 · 三条路", (1810, 4980, 0.76), shake=[0], flashes=[0])
J4 = J()
b.custom(J4, 0, 0.4, slam_fn([(x, y, s) for (x, y, _), s in zip(SIGNS, ("①做一件事", "②爱一个人", "③扛住难事"))]),
         sfx="kick", gain=1.0)
L(P((1170, 5300), (1490, 5300)), 2, 2.6, RED, 9, sfx="rim")
T("三条路都通", 1330, 5410, 58, RED, k0=3, k1=4.25, sfx="pop")
L(underline(1190, 1470, 5465, 10, 36), 5, 5.7, RED, 7, sfx="wood_high")
L(circle(*CP, 82), 6, 6.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 三条路各走两站（场景 5–10，沿地图蛇形走）

C1, C2, C3 = 650, 1800, 2950
RA, RB = 3850, 2450             # 近处一排（离路口近）、远处一排
RH = 460                        # 每段路半长


def seg(x, y):
    L(road(x, y + RH, y - RH), 0, 0.9, GRAY, 9, sfx="wood_low")


scene("做成一件事", "书中观点 · 第一条路", (C1, RA, 0.85))
seg(C1, RA)
L(sign(390, 3620, 3900), 1, 1.8, RED, 8, sfx="wood_high")
T("①做一件事", 390, 3620, 50, RED, k0=2, k1=3.25, sfx="pop")
L(wrench(900, 3720, 1.0), 4, 4.9, BLACK, 9, sfx="wood_high")
T("做出一样东西", 920, 3980, 48, k0=5, k1=6.5, sfx="pop")
L(stick(C1, 4260, 0.55, "down"), 7, 7.8, BLUE, 8, sfx="pop")
L(face(C1, 4260, 0.55, "smile"), 7.8, 8.0, BLUE, 7)

scene("修好打印机", "例子 · 第一条路", (C1, RB, 0.85))
seg(C1, RB)
L(printer(380, 2400), 1, 1.9, BLACK, 9, sfx="wood_high")
L(stick(380, 2860, 0.55, "up"), 2, 2.8, BLUE, 8, sfx="pop")
L(face(380, 2860, 0.55, "smile"), 2.8, 3.0, BLUE, 7)
L(papers(920, 2420), 4, 4.8, BLACK, 8, sfx="pop")
T("全组按时交", 920, 2200, 52, k0=5, k1=6.25, sfx="pop")
L(check(920, 2680, 60), 7, 7.7, GREEN, 11, sfx="ding")

scene("看见一个人", "书中观点 · 第二条路", (C2, RB, 0.85))
seg(C2, RB)
L(sign(1540, 2200, 2500), 1, 1.8, RED, 8, sfx="wood_high")
T("②爱一个人", 1540, 2200, 50, RED, k0=2, k1=3.25, sfx="pop")
L(heart(2060, 2260, 80), 4, 4.8, RED, 9, sfx="ding")
T("看一场晚霞", 2060, 2800, 48, k0=5, k1=6.25, sfx="pop")
L(sunset(2060, 2620, 64), 7, 7.9, ORANGE, 8, sfx="wood_high")

scene("陪妈逛菜市场", "例子 · 第二条路", (C2, RA, 0.85))
seg(C2, RA)
L(stall(1530, 3900), 1, 1.9, BLACK, 8, sfx="wood_high")
T("菜", 1530, 3622, 50, GREEN, k0=2, k1=2.8, sfx="pop")
L(stick(2010, 4170, 0.6, "point", hair=True), 3, 3.8, BLACK, 9, sfx="pop")
L(face(2010, 4170, 0.6, "smile"), 3.8, 4.0, BLACK, 7)
L(stick(2200, 4170, 0.6, "down"), 4, 4.8, BLUE, 9, sfx="wood_high")
L(face(2200, 4170, 0.6, "smile"), 4.8, 5.0, BLUE, 7)
L(bubble(2060, 3720, 300, 120, -1), 5, 5.6, BLACK, 7, sfx="pop")
T("便宜点呗", 2060, 3720, 48, k0=5.6, k1=6.6)
L(heart(2105, 3920, 28), 7, 7.6, RED, 7, sfx="ding")

scene("扛住躲不开的难", "书中观点 · 第三条路", (C3, RA, 0.85))
seg(C3, RA)
L(sign(2690, 3620, 3900), 1, 1.8, RED, 8, sfx="wood_high")
T("③扛住难事", 2690, 3620, 50, RED, k0=2, k1=3.25, sfx="pop")
L(stick(C3, 4260, 0.6, "up"), 4, 4.8, BLUE, 9, sfx="pop")
L(face(C3, 4260, 0.6, "flat"), 4.8, 5.0, BLUE, 7)
L(rock(C3, 3990), 5, 5.8, BLACK, 10, sfx="tom")
T("选怎么面对", 3240, 3700, 50, k0=6, k1=7.25, sfx="pop")
T("第7讲细讲", 3240, 3800, 46, GRAY, k0=7.3, k1=8.0)
H(7, "wood_high", 0.6)

scene("每天问清一件事", "例子 · 第三条路", (C3, RB, 0.85))
seg(C3, RB)
L(bed(2690, 2620), 1, 1.9, BLACK, 9, sfx="wood_high")
T("爸住院", 2690, 2330, 56, k0=2, k1=2.8, sfx="pop")
L(stick(3220, 2830, 0.6, "hold"), 3, 3.8, BLUE, 9, sfx="pop")
L(face(3220, 2830, 0.6, "flat"), 3.8, 4.0, BLUE, 7)
L(note(3230, 2320), 4, 4.7, ORANGE, 8, sfx="wood_high")
T("今天问医生", 3230, 2270, 46, k0=5, k1=6.25, sfx="pop")
T("能吃什么？", 3230, 2360, 50, RED, k0=6.4, k1=7.6)
H(6, "pop", 0.6)

# ---------------------------------------------------------------- 拉远：同一张地图（场景 11）

FLAG = (1800, 1760)
scene("一张地图三条路", "一张地图", (1800, 3600, 0.21))
for n, (sx, sy) in enumerate([(1350, 4685), (1800, 4555), (2250, 4685)]):
    cx = (C1, C2, C3)[n]
    L(join(road_curve((sx, sy), (cx, RA + RH)), road_curve((cx, RA - RH), (cx, RB + RH)),
           road_curve((cx, RB - RH), (FLAG[0] + (n - 1) * 110, FLAG[1]))), n, n + 0.9, BLACK, 12, sfx="wood_high")
L(flag(*FLAG), 3, 3.8, RED, 14, sfx="ding")
T("意义", 2250, 1520, 190, RED, k0=4, k1=4.8, sfx="pop")
T("罗盘都能指", 3010, 5300, 180, BLUE, k0=5, k1=6.25, sfx="pop")
L(arrow((2560, 5180), (2080, 5250), 0.15, 70), 7, 7.8, BLUE, 16, sfx="wood_high")

# ---------------------------------------------------------------- 做法（场景 12–13）

scene("每条走一小步", "做法 · 每条走一步", (1100, 6950, 0.85))
T("① 每条路走一步", 1100, 6580, 70, BLUE, k0=0, k1=1.75, sfx="pop")
ROWS = [(6790, "做完一件事", lambda y: wrench(800, y + 20, 0.42)),
        (6990, "陪一个人", lambda y: heart(820, y, 42)),
        (7190, "扛住一件难事", lambda y: rock(820, y, 130, 80))]
for n, (y, s, icon) in enumerate(ROWS):
    L(icon(y), 2 + 2 * n, 2.6 + 2 * n, RED if n == 1 else BLACK, 8, sfx="wood_high")
    TL(s, 920, y, 58, k0=2.6 + 2 * n, k1=min(8.0, 2.6 + 2 * n + 0.25 * len(s)))

J13 = None
FORK = (2450, 7260)
BR = [(2130, 6800), (2450, 6740), (2770, 6800)]
CP2 = (2450, 7345)
scene("堵了换一条", "做法 · 堵了换一条", (2450, 6950, 0.85))
J13 = J()
T("② 堵了换一条", 2450, 6560, 70, BLUE, k0=0, k1=1.0, sfx="pop")
L(join(*[P(FORK, e) for e in BR]), 1, 1.9, GRAY, 10, sfx="wood_high")
L(barrier(2270, 7010), 2, 2.8, RED, 8, sfx="rim")
L(compass(*CP2, 55), 3, 3.7, BLACK, 7, sfx="wood_low")
b.custom(J13, 3.7, 3.9, needle_fn(*CP2, 55, [(J13, 3.7, "point", [math.atan2(BR[0][1] - CP2[1], BR[0][0] - CP2[0])]),
                                              (J13, 5, "point", [-math.pi / 2])]))
H(5, "ding", 0.8, "罗盘转向另一条")
L(arrow((2330, 7110), (2440, 6900), -0.35, 34), 6, 6.7, GREEN, 9, sfx="wood_high")
T("换这条走", 2760, 7120, 56, GREEN, k0=7, k1=8.0, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 4500, 0.155)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, (1800, 8400, 0.8), dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你最近走的是哪条？", 1800, 8330, 76, RED, k0=6, k1=8.25, sfx="pop")
T("下一讲：周日晚上，为什么特别没劲？", 1800, 8490, 46, k0=9, k1=13.25, sfx="wood_high")
H(16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "three", "三条路", "意义从哪来？书里给了三条路", ACC, b.shots,
                 [f"{BOOK}第二部分〈生命之意义〉（意义的三条途径）、〈爱之意义〉（转述）",
                  "Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010"],
                 "意义从哪来|书里给了【三条路】", 3,
                 ["书中观点为转述：意义可以从三条途径找到——做一件事、创造一样东西；体验一件事或爱一个人；面对躲不开的苦难时"
                  "选择的态度（第二部分〈生命之意义〉）；第二条里的“爱一个人”见〈爱之意义〉。第三条在第 7 讲细讲。"
                  "出处：Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010。"
                  "上屏均为转述，不是逐字引文。",
                  "三岔路口、路牌、罗盘、汇到一面旗的地图为贯穿全讲的比喻示意；“赚大钱、出名、躺平”路牌为常见说法示意，"
                  "不是书中内容。",
                  "修好全组的打印机、周末陪妈逛菜市场、爸住院下班去陪护并每天问清医生一件事均为现实场景示意，"
                  "不指向任何具体公司或个人。",
                  "两条做法（三条路今天各走一小步；一条路堵了换另一条）为据书中思路整理的建议。"],
                 tags="#人生意义 #读书笔记")
    return b.attach(ep)
