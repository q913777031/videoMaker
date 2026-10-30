"""06 开工仪式（白板手绘版）：一坐下就想摸手机，怎么办？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（形式 J：一个比喻贯穿）：一个画面开局（小周打开文档，三秒后手就伸向手机；脑子里两个小人每次都要吵一架）→
画一间“专注小屋”，drop 时门“砰”地关上，小红点撞在门上压扁 → 亮书（书里讲给专注定规矩）→
一屏给小屋加一样东西：门口路牌（在哪做）、门上挂钟（做多久）、门上贴规矩（断网、手机进抽屉）、屋里放补给（咖啡、水、
坚果，窗外一条散步小路）→ 有时候要去更远的屋子（书例：罗琳住进酒店、尚克曼坐飞机写书，只写名字）→
打工人的小号做法（周六去咖啡馆，花一杯咖啡钱）→ 每次开工走同一套四步 → 拉远看整间小屋 → 评论区互动。
系列角色：小红点（全程被关在门外，压扁在门口；咖啡馆外也进不来）、小周（戴工牌的火柴人）、专注块（烟囱那块蓝砖）。
书中观点为转述（卡尔·纽波特《深度工作》，宋伟译，准则1 中讲给专注定规矩与花大代价换环境的两节）；
小屋比喻、90 分钟、会议室、咖啡馆为示意，四步开工流程为据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, building, check, circle, clock, desk,
                               face, hands_at, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#C4782A"
SQUARE_SHOT = 3                 # 场景 4：门关上、小红点压扁在门口，小周在窗里

b = Board(size=(4000, 7600))
BOARD_BG = "#FBFBF9"


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = J() if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def badge(x, y, s=1.0) -> skia.Path:
    """配合 stick 的工牌：挂绳 + 小方牌（(x, y) 为小人脚底）。"""
    hy = y - 290 * s
    return join(P((x - 14 * s, hy + 50 * s), (x + 22 * s, hy + 120 * s), (x + 34 * s, hy + 50 * s)),
                rect(x + 24 * s, hy + 145 * s, 40 * s, 50 * s, 5 * s))


def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """小周：戴工牌的火柴人。"""
    return join(stick(x, y, s, arms), badge(x, y, s))


def bust(x, y, s=1.0) -> skia.Path:
    """窗里的小周：头 + 肩 + 工牌（(x, y) 为头心）。"""
    sh = skia.Path()
    sh.moveTo(x - 80 * s, y + 150 * s)
    sh.quadTo(x - 75 * s, y + 60 * s, x, y + 55 * s)
    sh.quadTo(x + 75 * s, y + 60 * s, x + 80 * s, y + 150 * s)
    return join(circle(x, y, 40 * s), sh, rect(x + 30 * s, y + 110 * s, 30 * s, 38 * s, 4 * s))


def bust_smile(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.addCircle(x - 13 * s, y - 6 * s, 3 * s)
    p.addCircle(x + 13 * s, y - 6 * s, 3 * s)
    p.addArc(skia.Rect.MakeXYWH(x - 17 * s, y - 2 * s, 34 * s, 24 * s), 20, 140)
    return p


def phone(x, y, w=60, h=100) -> skia.Path:
    return join(rect(x, y, w, h, 10), P((x - w * 0.2, y + h / 2 - 14), (x + w * 0.2, y + h / 2 - 14)))


def cloud(x, y, w, h) -> skia.Path:
    """想法云：一圈小弧。"""
    pts = []
    for i in range(10):
        a = i / 10 * 2 * math.pi
        pts.append((x + w / 2 * math.cos(a), y + h / 2 * math.sin(a)))
    p = skia.Path()
    p.moveTo(*pts[0])
    for i in range(10):
        a0, a1 = pts[i], pts[(i + 1) % 10]
        mx, my = (a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2
        ox, oy = mx - x, my - y
        n = math.hypot(ox, oy) or 1
        p.quadTo(mx + ox / n * 70, my + oy / n * 70, *a1)
    return p


def bolt(x, y, s=1.0) -> skia.Path:
    return P((x + 25 * s, y - 80 * s), (x - 30 * s, y + 5 * s), (x + 12 * s, y + 5 * s), (x - 22 * s, y + 80 * s))


def say(x, y, w, h, tail=-1) -> skia.Path:
    """对话框，尾巴朝下。"""
    p = rect(x, y, w, h, 36)
    p.moveTo(x + tail * w * 0.12, y + h / 2)
    p.lineTo(x + tail * w * 0.22, y + h / 2 + 50)
    p.lineTo(x + tail * w * 0.02, y + h / 2)
    return p


def signboard(x, y, w=390, h=100) -> skia.Path:
    """箭头形路牌，朝右。"""
    return P((x - w / 2, y - h / 2), (x + w / 2 - 50, y - h / 2), (x + w / 2, y), (x + w / 2 - 50, y + h / 2),
             (x - w / 2, y + h / 2), close=True)


def cup(x, y, s=1.0, steam=True) -> skia.Path:
    """咖啡杯：(x, y) 为杯身中心。"""
    h = skia.Path()
    h.addArc(skia.Rect.MakeXYWH(x + 22 * s, y - 18 * s, 34 * s, 36 * s), -90, 180)
    parts = [P((x - 35 * s, y - 35 * s), (x - 28 * s, y + 35 * s), (x + 28 * s, y + 35 * s), (x + 35 * s, y - 35 * s)), h]
    if steam:
        st = skia.Path()
        st.moveTo(x - 5 * s, y - 50 * s)
        st.quadTo(x - 22 * s, y - 70 * s, x - 5 * s, y - 90 * s)
        st.quadTo(x + 12 * s, y - 110 * s, x - 5 * s, y - 130 * s)
        parts.append(st)
    return join(*parts)


def glass(x, y, s=1.0) -> skia.Path:
    return join(P((x - 28 * s, y - 50 * s), (x - 22 * s, y + 45 * s), (x + 22 * s, y + 45 * s), (x + 28 * s, y - 50 * s)),
                P((x - 25 * s, y - 15 * s), (x + 25 * s, y - 15 * s)))


def nuts(x, y, s=1.0) -> skia.Path:
    """一盘坚果：盘子 + 三颗小椭圆。"""
    parts = [P((x - 55 * s, y), (x - 40 * s, y + 22 * s), (x + 40 * s, y + 22 * s), (x + 55 * s, y))]
    for dx, dy in ((-22, -12), (0, -24), (22, -12)):
        o = skia.Path()
        o.addOval(skia.Rect.MakeXYWH(x + (dx - 15) * s, y + (dy - 11) * s, 30 * s, 22 * s))
        parts.append(o)
    return join(*parts)


def tree(x, y, s=1.0) -> skia.Path:
    """小树：(x, y) 为树根。"""
    return join(P((x, y), (x, y - 90 * s)), circle(x, y - 150 * s, 65 * s))


def dashes(p0, p1, p2, n=9) -> skia.Path:
    """沿二次曲线 p0→(控制点 p1)→p2 的虚线。"""
    out = skia.Path()

    def at(t):
        return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])

    for i in range(n):
        a, z = at(i / n), at((i + 0.55) / n)
        out.moveTo(*a)
        out.lineTo(*z)
    return out


def plane(x, y, s=1.0) -> skia.Path:
    """侧视小飞机，机头朝右。"""
    body = skia.Path()
    body.addRoundRect(skia.Rect.MakeXYWH(x - 150 * s, y - 28 * s, 300 * s, 56 * s), 28 * s, 28 * s)
    return join(body, P((x - 20 * s, y), (x - 70 * s, y + 95 * s), (x + 10 * s, y + 95 * s), (x + 50 * s, y)),
                P((x - 110 * s, y - 20 * s), (x - 150 * s, y - 85 * s), (x - 115 * s, y - 85 * s), (x - 70 * s, y - 25 * s)),
                *[circle(x + (40 + 40 * i) * s, y - 4 * s, 9 * s) for i in range(3)])


def drawer(x, y, w=200, h=110) -> skia.Path:
    return join(rect(x, y, w, h, 8), P((x - 30, y), (x + 30, y)))


def door_icon(x, y) -> skia.Path:
    return join(rect(x, y, 130, 190, 6), circle(x + 38, y + 10, 8))


def awning(x, y, w, n=6) -> skia.Path:
    """遮阳棚：上沿一条线 + 一排小弧。"""
    p = P((x - w / 2, y - 35), (x + w / 2, y - 35), (x + w / 2, y), (x - w / 2, y), close=True)
    step = w / n
    for i in range(n):
        p.moveTo(x - w / 2 + i * step, y)
        p.quadTo(x - w / 2 + (i + 0.5) * step, y + 45, x - w / 2 + (i + 1) * step, y)
    return p


def draw_dot(c, x, y, r, num, sx=1.0, sy=1.0, alpha=1.0, legs=True, xeyes=False):
    """小红点：红色实心圆 + 白色数字 + 两条小短腿。"""
    if alpha <= 0 or r <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(sx, sy)
    if legs:
        for d in (-1, 1):
            c.drawPath(P((d * r * 0.35, r * 0.85), (d * r * 0.42, r * 1.5), (d * r * 0.75, r * 1.5)),
                       K.paint(BLACK, alpha, 7))
    K.dot(c, 0, 0, r, RED, alpha)
    c.drawCircle(0, 0, r, K.paint(BLACK, alpha * 0.85, 5))
    if xeyes:
        for d in (-1, 1):
            ex = d * r * 0.42
            c.drawPath(join(P((ex - 12, -r * 0.45 - 12), (ex + 12, -r * 0.45 + 12)),
                            P((ex + 12, -r * 0.45 - 12), (ex - 12, -r * 0.45 + 12))), K.paint("#FFFFFF", alpha, 6))
    if num:
        K.text(c, num, 0, r * 0.12 if xeyes else 0, r * (1.0 if len(num) < 3 else 0.72), "hand", "#FFFFFF", alpha)
    c.restore()


def dot_pop_fn(x, y, r, num, bob=True):
    """原地冒出来的小红点（之后一直轻轻蹦）。"""

    def fn(c, k, t):
        s = ease_out(k)
        dy = -abs(math.sin(t * 7)) * 10 if bob else 0
        draw_dot(c, x, y + dy, r * s, num)
        return (x, y + r) if k < 1 else None

    return fn


# ---------------------------------------------------------------- 开局：一坐下就摸手机（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

ZH = (900, 1950, 0.8)           # 小周脚底
PH = (1450, 1712)               # 手机
scene("一坐下就摸", "灵魂拷问", (1100, 1500, 0.85), bars=2)
L(desk(1200, 1750, 440), 0, 0.9, sfx="wood_high")
L(zhou(*ZH, "hold"), 1, 1.9, BLACK, 10, sfx="pop")
T("文档", 1240, 1585, 52, k0=2, k1=2.8, sfx="pop")
L(phone(*PH), 3, 3.8, BLACK, 8, sfx="wood_high")
C(4, 4.5, dot_pop_fn(PH[0] + 40, PH[1] - 60, 30, "1"), sfx="ding")
SH = (ZH[0] + 55, ZH[1] - 290 * ZH[2] + 120 * ZH[2])
L(join(*[arrow(SH, (PH[0] - 40 - 50 * n, PH[1] + 10 - 40 * n), 0.12 + 0.06 * n, 26) for n in range(3)]),
  4.5, 5.0, "#8E95A3", 6)
T("3 秒", 1460, 1470, 76, RED, k0=5, k1=5.8, sfx="rim")

scene("每次都要吵", "灵魂拷问", (1100, 1350, 0.85))
L(join(circle(930, 1590, 14), circle(960, 1530, 20), cloud(1000, 1290, 640, 280)), 0, 0.9, BLACK, 8, sfx="wood_low")
L(stick(840, 1390, 0.4), 1, 1.8, BLUE, 8, sfx="pop")
L(say(800, 955, 280, 110, 1), 2, 2.4, BLUE, 7, sfx="pop")
T("先干活", 800, 955, 56, BLUE, k0=2.4, k1=3.2)
L(stick(1170, 1390, 0.4, "up"), 4, 4.8, RED, 8, sfx="wood_high")
L(say(1220, 955, 320, 110, -1), 5, 5.4, RED, 7, sfx="pop")
T("就看一眼", 1220, 955, 56, RED, k0=5.4, k1=6.4)
L(bolt(1005, 1290, 0.8), 7, 7.8, RED, 9, sfx="rim")

# ---------------------------------------------------------------- 专注小屋（场景 3–4）

GY = 3600                        # 地面
WL, WR, WT = 1200, 2400, 2850    # 墙
DL, DR, DT = 1430, 1770, 3100    # 门
WIN = (2150, 3190, 400, 260)     # 窗
HOUSE = join(P((450, GY), (3000, GY)), P((WL, GY), (WL, WT), (WR, WT), (WR, GY)))
ROOF = P((WL - 60, WT), (1800, 2450), (WR + 60, WT))

j3 = scene("给专注一间屋", "比喻 · 专注小屋", (1800, 3060, 0.72))
L(HOUSE, 0, 0.9, BLACK, 10, sfx="wood_low")
L(ROOF, 1, 1.9, BLACK, 10, sfx="wood_high")
L(P((DL, GY), (DL, DT), (DR, DT), (DR, GY)), 2, 2.8, BLACK, 10, sfx="wood_high")
L(join(rect(WIN[0], WIN[1], WIN[2], WIN[3], 8), P((WIN[0] - WIN[2] / 2 - 25, WIN[1] + WIN[3] / 2 + 14),
                                                  (WIN[0] + WIN[2] / 2 + 25, WIN[1] + WIN[3] / 2 + 14))),
  4, 4.8, BLACK, 9, sfx="wood_high")
L(zhou(1600, GY, 0.75), 5, 5.9, BLACK, 9, sfx="pop")
T("专注小屋", 1800, 2720, 70, GREEN, k0=6, k1=7, sfx="pop")
J4 = j3 + 1                      # drop 场景
DOT0, DOT_HIT, DOT_END = (2700, 3478), (1600, 3330), (1600, 3574)


def door_fn(c, k, t):
    """门板：场景 3 开着（向外翻开），drop 第 0 拍“砰”地关上（关门的最后一帧对齐 kick）。"""
    tc = b.t_of(J4, 0)
    g = clamp01((t - (tc - 0.16)) / 0.16)
    th = math.radians(118 * (1 - g * g))
    w = DR - DL
    fx = DL + w * math.cos(th)
    d = 46 * math.sin(th)
    panel = P((DL, DT), (fx, DT - d), (fx, GY + d * 0.25), (DL, GY), close=True)
    if k < 1:
        part, tip = wb.partial(panel, k)
        c.drawPath(part, wb.marker(BLACK, 10))
        return tip
    c.drawPath(panel, K.paint(BOARD_BG))
    c.drawPath(panel, wb.marker(BLACK, 10))
    kx = fx - 40 if fx > DL else fx + 30
    c.drawCircle(kx, (DT + GY) / 2 + 20, 11, K.paint(BLACK))
    return None


def dot_life(c, k, t):
    """门外的小红点：场景 3 跑来门口蹦；drop 第 1 拍起跳、第 2 拍拍在门上压扁、滑到门口，第 6 拍晕过去。"""
    t1, t2, t3, t6 = (b.t_of(J4, kk) for kk in (1, 2, 3, 6))
    r = 55
    if t < t1:
        s = ease_out(k)
        draw_dot(c, DOT0[0], DOT0[1] - abs(math.sin(t * 7)) * 14, r * s, "9")
        return (DOT0[0], DOT0[1] + r) if k < 1 else None
    if t < t2:
        f = (t - t1) / (t2 - t1)
        x = lerp(DOT0[0], DOT_HIT[0], f)
        y = lerp(DOT0[1], DOT_HIT[1], f) - 330 * 4 * f * (1 - f)
        draw_dot(c, x, y, r, "99+", 0.9, 1.12)
        return None
    f = ease_in_out(clamp01((t - t2 - 0.18) / max(0.1, t3 - t2 - 0.18)))
    y = lerp(DOT_HIT[1], DOT_END[1], f)
    draw_dot(c, DOT_HIT[0], y, r, "99+", lerp(1.75, 1.7, f), lerp(0.6, 0.48, f), legs=False, xeyes=t >= t6)
    return None


b.custom(j3, 3, 3.8, door_fn, sfx="pop")
b.custom(j3, 7, 7.6, dot_life, sfx="ding")

scene("门一关", "比喻 · 关门", (1800, 3060, 0.72), shake=[0], flashes=[0])
T("砰！", 1315, 3470, 90, RED, k0=0, k1=0.8, sfx="kick")
H(1, "shaker")
H(2, "tom")


def stars_fn(c, k, t):
    """压扁的小红点头上转圈的小星星（只在本场景和下一场景出现）。"""
    if t > b.t_of(J4 + 1, 12):
        return None
    for i in range(3):
        a = t * 4 + i * 2 * math.pi / 3
        x, y = DOT_END[0] + math.cos(a) * 80, DOT_END[1] - 70 + math.sin(a) * 18
        s = 14 * ease_out(k)
        c.drawPath(join(P((x - s, y), (x + s, y)), P((x, y - s), (x, y + s))), K.paint(ORANGE, 1, 6))
    return None


C(3, 3.6, stars_fn, sfx="ding")
BU = (WIN[0] - 120, WIN[1] - 20)
L(bust(*BU, 0.9), 5, 5.8, BLUE, 8, sfx="pop")
L(bust_smile(*BU, 0.9), 5.8, 6.0, BLUE, 7)
H(6, "rim")

# ---------------------------------------------------------------- 亮书（场景 5）

BK = (650, 2350)
scene("书里叫定规矩", "深度工作 · 书中观点", (820, 2560, 0.85))
L(book(*BK, 360, 230), 0, 0.9, BLACK, 10, sfx="wood_low")
T("《深度工作》", BK[0], 2165, 62, GREEN, k0=1, k1=2.75, sfx="pop")
T("卡尔 · 纽波特", BK[0], 2545, 52, k0=3, k1=4.5, sfx="pop")
L(arrow((850, 2350), (900, 2350), 0.0, 26), 5, 5.5, GREEN, 9, sfx="wood_high")
L(rect(1010, 2350, 210, 90, 10), 5.5, 6.0, RED, 8)
T("定规矩", 1010, 2350, 58, RED, k0=6, k1=6.8, sfx="pop")
L(join(*[rect(905 + 70 * i, 2450, 40, 40, 6) for i in range(4)]), 7, 7.8, BLACK, 6, sfx="ding")

# ---------------------------------------------------------------- 一屏加一样：在哪 / 多久 / 规矩 / 补给（场景 6–9）

SP = 950
scene("先定在哪", "定规矩 · 在哪做", (1100, 3380, 1.0))
L(P((SP - 170, GY), (SP - 170, 3060)), 0, 0.9, BLACK, 12, sfx="wood_low")
L(signboard(SP, 3170, 430), 1, 1.8, BLACK, 9, sfx="wood_high")
T("会议室", SP + 15, 3170, 56, k0=2, k1=2.8, sfx="pop")
L(signboard(SP, 3320, 430), 3, 3.8, BLACK, 9, sfx="wood_high")
T("图书馆角落", SP + 20, 3320, 52, k0=4, k1=5.25, sfx="pop")
L(zhou(640, GY, 0.6, "point"), 6, 6.9, BLACK, 9, sfx="pop")

CK = (1600, 3000, 70)
scene("再定多久", "定规矩 · 做多久", (1750, 3050, 0.9))
L(P((CK[0] - 40, CK[1] - CK[2] + 5), (CK[0], CK[1] - CK[2] - 35), (CK[0] + 40, CK[1] - CK[2] + 5)), 0, 0.8, BLACK, 7,
  sfx="wood_low")
L(clock(*CK), 1, 1.9, BLACK, 9, sfx="wood_high")


def timer_fn(c, k, t):
    """钟面：蓝色扇形转满一圈（一整块专注时间），分针跟着转。"""
    x, y, r = CK
    if k > 0:
        sec = skia.Path()
        sec.moveTo(x, y)
        sec.arcTo(skia.Rect.MakeXYWH(x - r * 0.8, y - r * 0.8, r * 1.6, r * 1.6), -90, 359.9 * k, False)
        sec.close()
        c.drawPath(sec, K.paint(BLUE, 0.35))
    a = -math.pi / 2 + 3 * math.pi * k
    c.drawPath(join(P((x, y), (x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72)),
                    P((x, y), (x + math.cos(-math.pi / 2 + k * 0.8) * r * 0.45,
                               y + math.sin(-math.pi / 2 + k * 0.8) * r * 0.45))), wb.marker(BLACK, 7))
    return None


C(2, 5, timer_fn, sfx="pop")
H(3, "shaker", 0.6)
T("90 分钟", 1330, 3000, 58, BLUE, k0=5, k1=6, sfx="pop")
L(underline(1230, 1430, 3045, 8, 30), 7, 7.7, BLUE, 7, sfx="ding")

DW = (1930, 3530, 200, 110)
scene("门口贴规矩", "定规矩 · 守什么", (1700, 3170, 0.95))
L(rect(1600, 3390, 300, 230, 6), 0, 0.8, BLACK, 8, sfx="wood_high")
T("断网", 1600, 3335, 60, RED, k0=1, k1=1.8, sfx="pop")
T("手机进抽屉", 1600, 3440, 48, k0=3, k1=4.25, sfx="pop")
L(drawer(*DW), 5, 5.8, BLACK, 9, sfx="wood_low")


def phone_drop_fn(c, k, t):
    """手机掉进抽屉：落下后下半截藏进抽屉里。"""
    x, w, h = DW[0], 70, 120
    y = lerp(3260, DW[1] - 25, ease_in_out(k) ** 1.6)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(DW[0] - DW[2] / 2 - 6, DW[1] - DW[3] / 2 - 2, DW[2] + 12, DW[3] + 12),
               skia.ClipOp.kDifference)
    c.drawPath(phone(x, y, w, h), K.paint(BOARD_BG))
    c.drawPath(phone(x, y, w, h), wb.marker(BLUE, 8))
    c.restore()
    return None


C(6, 6.8, phone_drop_fn, sfx="tom")
L(check(1745, 3335, 26), 7, 7.6, GREEN, 8, sfx="ding")

scene("屋里放补给", "定规矩 · 靠什么撑", (2560, 3250, 0.85))
L(cup(2150, 3262, 0.7), 0, 0.8, BLACK, 8, sfx="wood_high")
L(glass(2222, 3268, 0.7), 1, 1.7, BLUE, 8, sfx="pop")
L(nuts(2300, 3290, 0.7), 2, 2.8, BLACK, 7, sfx="wood_high")
T("咖啡 · 水 · 坚果", 2150, 3395, 46, k0=3, k1=4.5, sfx="pop")
L(dashes((WR, GY + 20), (2650, 3630), (2900, 3770), 9), 5, 5.8, GREEN, 9, sfx="wood_low")
L(join(tree(2780, 3640, 0.75), tree(3000, 3720, 0.6)), 6, 6.8, GREEN, 8, sfx="pop")
T("散步", 2600, 3735, 56, GREEN, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 大手笔：去更远的屋子（场景 10–11）

scene("换个地方写", "大手笔 · 换地方", (2950, 3150, 0.55))
L(P((3000, GY), (3900, GY)), 0, 0.8, BLACK, 10, sfx="wood_low")
L(building(3500, GY, 320, 560), 1, 1.9, BLACK, 10, sfx="wood_high")
T("酒店", 3500, 2985, 76, k0=2, k1=2.8, sfx="pop")
T("罗琳", 3500, 3700, 80, RED, k0=3, k1=3.8, sfx="pop")
L(plane(3050, 2600, 0.9), 4, 4.9, BLACK, 9, sfx="wood_high")
L(dashes((3220, 2560), (3500, 2420), (3850, 2480), 7), 5, 5.8, BLACK, 7)
T("尚克曼", 3050, 2790, 80, RED, k0=6, k1=6.9, sfx="pop")
H(5, "shaker", 0.6)

CF = (3000, 4800)
scene("花点小钱", "大手笔 · 小号版", (3000, 4750, 0.85))
L(join(rect(CF[0], CF[1], 640, 420, 6), awning(CF[0], 4600, 700)), 0, 0.9, BLACK, 9, sfx="wood_high")
T("咖啡馆", CF[0], 4470, 70, k0=1, k1=1.8, sfx="pop")
L(zhou(2850, 4980, 0.6, "hold"), 2, 2.9, BLACK, 9, sfx="wood_high")
L(join(P((2930, 4870), (3200, 4870)), P((3170, 4870), (3170, 4980)), rect(3030, 4830, 90, 60, 6),
       cup(3140, 4840, 0.45, steam=False)), 3, 3.8, BLACK, 8, sfx="pop")
T("周六", 2580, 4380, 64, BLUE, k0=4, k1=4.8, sfx="pop")
T("一杯咖啡钱", 3390, 4380, 60, RED, k0=5, k1=6.25, sfx="ding")
C(7, 7.5, dot_pop_fn(3460, 4930, 40, "1"), sfx="rim")
T("？", 3540, 4820, 64, RED, k0=7.5, k1=8.0)

# ---------------------------------------------------------------- 做法：每次开工走同一套（场景 12）

IC = {"door": (2450, 5650), "clock": (3150, 5650), "drawer": (3150, 6200), "cup": (2450, 6200)}
scene("每次走一遍", "做法 · 开工四步", (2800, 5950, 0.8))
L(door_icon(*IC["door"]), 0, 0.9, BLACK, 9, sfx="wood_high")
T("会议室", IC["door"][0], 5820, 56, k0=0.9, k1=1.7)
L(join(arrow((2560, 5650), (3040, 5650), 0.0, 34), clock(*IC["clock"], 80), hands_at(*IC["clock"], 80, 9, 0)),
  2, 2.9, BLACK, 9, sfx="pop")
T("定时", IC["clock"][0], 5820, 56, k0=2.9, k1=3.7)
L(join(arrow((3330, 5760), (3330, 6110), -0.1, 34), drawer(3150, 6230), phone(3150, 6140, 54, 90)),
  4, 4.9, BLACK, 9, sfx="wood_high")
T("手机进抽屉", IC["drawer"][0], 6370, 56, k0=4.9, k1=6.0)
L(join(arrow((3040, 6200), (2560, 6200), 0.0, 34), cup(2450, 6220, 0.9)), 6, 6.8, BLACK, 9, sfx="pop")
T("倒水", IC["cup"][0], 6370, 56, k0=6.8, k1=7.4)
L(arrow((2270, 6110), (2270, 5760), -0.1, 34), 7.4, 8.0, GREEN, 9)

# ---------------------------------------------------------------- 拉远：整间小屋（场景 13）

scene("一间小屋", "比喻 · 专注小屋", (1900, 3150, 0.47))
H(0, "cymbal", 0.5)
L(P((1400, 2692), (1400, 2540), (1500, 2540), (1500, 2632)), 1, 1.8, BLUE, 14, sfx="wood_high")


def brick_fn(c, k, t):
    """烟囱填成一块蓝色专注块。"""
    p = P((1400, 2692), (1400, 2540), (1500, 2540), (1500, 2632), close=True)
    c.drawPath(p, K.paint(BLUE, 0.55 * k))
    return None


C(2, 2.6, brick_fn, sfx="pop")
sm = skia.Path()
sm.moveTo(1450, 2510)
sm.quadTo(1400, 2460, 1450, 2420)
sm.quadTo(1500, 2380, 1450, 2340)
L(sm, 3, 3.7, "#8E95A3", 8, sfx="wood_low")
T("每天进一次", 2050, 2300, 100, RED, k0=4, k1=5.25, sfx="pop")
L(underline(1800, 2300, 2370, 12, 40), 6, 6.8, RED, 9, sfx="ding")

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：拉远看全板 → 推到评论区

FULL = (2000, 3800, 0.125)
CMT = (1200, 6900, 0.8)
j14 = scene("评论区聊聊", "评论区见", FULL, bars=4)
b.move(j14, 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你开工前第一件事是啥？", 1200, 6820, 72, RED, k0=6, k1=8.75, sfx="pop")
T("下一讲：下班了，脑子怎么还在上班？", 1200, 6980, 46, k0=10, k1=14.25, sfx="wood_high")
b.hit(j14, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "ritual", "开工仪式", "一坐下就想摸手机，怎么办？", ACC, b.shots,
                 [f"{BOOK}第二部分 准则1“工作要深入”：“习惯化”“要有大手笔”两节（转述）",
                  "中译本：宋伟译，江西人民出版社 · 后浪 2017；民主与建设出版社 · 后浪 2023"],
                 "一坐下|就想【摸手机】", SQUARE_SHOT,
                 ["书中观点均为转述：准则1“工作要深入”中的“习惯化”一节讲给专注定规矩——在哪儿做、做多久、做的时候守什么"
                  "规则（比如断网）、靠什么撑着（咖啡、吃的、走动）；“要有大手笔”一节讲换个地方、花点代价，逼自己把专注"
                  "当回事，书中例子有 J.K.罗琳写完结篇时住进爱丁堡一家酒店、作家彼得·尚克曼坐飞机往返东京在机上写书"
                  "（另有比尔·盖茨“思考周”，本讲未上屏）。上屏只写名字，不画肖像。出处：卡尔·纽波特《深度工作：如何有效"
                  "使用每一点脑力》（宋伟译）；原书 Cal Newport, Deep Work (Grand Central Publishing, 2016)。不是逐字引文。",
                  "“专注小屋”比喻、开门关门、小红点撞门压扁、脑子里两个小人吵架、窗里的小周均为示意；“3 秒”“90 分钟”"
                  "为示意，不是书中数据；会议室、图书馆角落、周六咖啡馆、一杯咖啡钱为现实场景示意，不指向具体公司或个人。",
                  "“咖啡 · 水 · 坚果”“散步小路”对应书中“靠什么撑着”的转述，具体物品为示意。",
                  "开工四步（去会议室 → 定时 → 手机进抽屉 → 倒水）与“每天进一次”为据书中思路整理的做法。"],
                 tags="#自律")
    return b.attach(ep)
