"""01 为什么而活（白板手绘版）：累到想辞职，靠什么撑下去？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（经典：问题 → 书中观点 → 身边例子 → 做法）：周三晚上十点还在工位、辞职信写了又关 → 抛问题“靠什么撑下去？”→
亮书（作者是精神科医生，二战时被关进集中营，活下来写了这本书）→ drop：天平上一摞“怎么”压着，红色“为什么”砸进另一边，
天平翻过来（书中引尼采：知道为什么而活，几乎扛得住任何怎么活），阿宁胸前的小罗盘第一次出现 →
有盼头的人撑得住 → 他在雪地里想着以后的讲台 → 一张图“先找为什么”→
身边的例子（加班改版知道为谁改、熬夜考证为了离家近、半夜冲奶知道为了谁；拉远连到同一个罗盘）→
做法（写一张便签“为了___” / 撑不住那天先看一眼 / 找不到就问“这事做成了，谁会好一点”）→ 拉远全板 → 评论区。
书中观点为转述（Viktor E. Frankl, Man's Search for Meaning，第一部分 在集中营的经历；
中译本《活出生命的意义》，吕娜译，华夏出版社 2010）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, circle, clock, desk, doc,
                               face, hands_at, join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#B5643C"
SQUARE_SHOT = 3                 # 场景 4：天平 + 阿宁 + 胸前罗盘
GRAY = "#8A8F98"                # 营里的场景用灰色细线
YELLOW = "#D9A21B"

b = Board(size=(3600, 11200))


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

def compass(x, y, r=60) -> skia.Path:
    """系列视觉角色：小罗盘（圆框 + 顶上小环 + 四个刻度），指针另用 needle_fn 画。"""
    parts = [circle(x, y, r), circle(x, y - r - 14, 12)]
    for a in range(4):
        ang = a * math.pi / 2
        parts.append(P((x + math.cos(ang) * r * 0.72, y + math.sin(ang) * r * 0.72),
                       (x + math.cos(ang) * r * 0.9, y + math.sin(ang) * r * 0.9)))
    return join(*parts)


def needle_fn(x, y, r, aim, turns=2.5):
    """罗盘指针：k<1 时乱转（越转越慢、带抖动），k=1 停在指向 aim=(ax, ay) 的方向，之后一直停着。"""
    final = math.atan2(aim[1] - y, aim[0] - x)

    def fn(c, k, t):
        e = ease_in_out(k)
        a = final + (1 - e) * turns * 2 * math.pi + (0.5 * math.sin(k * 23) * (1 - k) if k < 1 else 0)
        ca, sa = math.cos(a), math.sin(a)
        L_, w = r * 0.78, r * 0.2
        tip, tail = (x + ca * L_, y + sa * L_), (x - ca * L_, y - sa * L_)
        s1, s2 = (x - sa * w, y + ca * w), (x + sa * w, y - ca * w)
        K.poly(c, [tip, s1, s2], RED)
        K.poly(c, [tail, s1, s2], BLACK)
        K.dot(c, x, y, r * 0.1, "#FBFBF9")
        return None

    return fn


def fill_fn(path, color, alpha=0.35):
    """把一块区域淡淡填色（便签底色），随 k 渐显。"""
    def fn(c, k, t):
        c.drawPath(path, K.paint(color, alpha * k))
        return None

    return fn


def huts(x, y, n=3, w=150, h=90, gap=40) -> skia.Path:
    """简笔木棚屋剪影：一排矮屋，(x, y) 为第一间的地面中点。"""
    parts = []
    for i in range(n):
        cx = x + i * (w + gap)
        parts.append(P((cx - w / 2, y), (cx - w / 2, y - h), (cx, y - h - 45), (cx + w / 2, y - h), (cx + w / 2, y)))
    return join(*parts)


def flag(x, y, h=200) -> skia.Path:
    """小旗：(x, y) 为旗杆底部。"""
    return join(P((x, y), (x, y - h)), P((x, y - h), (x + 90, y - h + 35), (x, y - h + 70)))


def podium(x, y, s=1.0) -> skia.Path:
    """讲台：(x, y) 为台面中点，下方梯形台身 + 台后一个小人头。"""
    return join(P((x - 70 * s, y), (x + 70 * s, y)), P((x - 55 * s, y), (x - 40 * s, y + 110 * s),
                                                      (x + 40 * s, y + 110 * s), (x + 55 * s, y)),
                circle(x, y - 55 * s, 26 * s), P((x, y - 29 * s), (x, y)))


def desk_lamp(x, y, s=1.0) -> skia.Path:
    """台灯：(x, y) 为底座中点；灯罩朝右下，带两道光线。"""
    return join(P((x - 50 * s, y), (x + 50 * s, y)), P((x, y), (x - 30 * s, y - 120 * s), (x + 40 * s, y - 200 * s)),
                P((x + 10 * s, y - 230 * s), (x + 110 * s, y - 150 * s), (x + 30 * s, y - 130 * s), close=True),
                P((x + 90 * s, y - 110 * s), (x + 120 * s, y - 60 * s)), P((x + 60 * s, y - 100 * s), (x + 70 * s, y - 45 * s)))


def map_sheet(x, y, w=420, h=320) -> skia.Path:
    """折叠地图：外框 + 两道折痕。"""
    return join(P((x - w / 2, y - h / 2), (x - w / 6, y - h / 2 + 20), (x + w / 6, y - h / 2), (x + w / 2, y - h / 2 + 20),
                  (x + w / 2, y + h / 2 + 20), (x + w / 6, y + h / 2), (x - w / 6, y + h / 2 + 20), (x - w / 2, y + h / 2),
                  close=True),
                P((x - w / 6, y - h / 2 + 20), (x - w / 6, y + h / 2 + 20)), P((x + w / 6, y - h / 2), (x + w / 6, y + h / 2)))


def moon(x, y, r=80) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def bottle(x, y, s=1.0) -> skia.Path:
    """奶瓶：(x, y) 为瓶身中心；瓶身 + 瓶盖 + 奶嘴 + 刻度。"""
    nip = skia.Path()
    nip.moveTo(x - 22 * s, y - 120 * s)
    nip.quadTo(x - 25 * s, y - 175 * s, x, y - 180 * s)
    nip.quadTo(x + 25 * s, y - 175 * s, x + 22 * s, y - 120 * s)
    return join(rect(x, y, 110 * s, 200 * s, 26 * s), rect(x, y - 110 * s, 90 * s, 28 * s, 8 * s), nip,
                P((x + 20 * s, y - 50 * s), (x + 50 * s, y - 50 * s)), P((x + 20 * s, y), (x + 50 * s, y)),
                P((x + 20 * s, y + 50 * s), (x + 50 * s, y + 50 * s)))


def monitor(x, y, w=760, h=480) -> skia.Path:
    """大屏幕：(x, y) 为屏幕中心，带支架和底座。"""
    return join(rect(x, y, w, h, 18), P((x, y + h / 2), (x, y + h / 2 + 70)), P((x - 120, y + h / 2 + 70), (x + 120, y + h / 2 + 70)))


def qmark(x, y, s=1.0) -> skia.Path:
    """手绘大问号：(x, y) 为问号中心。"""
    p = skia.Path()
    p.moveTo(x - 70 * s, y - 70 * s)
    p.cubicTo(x - 70 * s, y - 170 * s, x + 80 * s, y - 170 * s, x + 80 * s, y - 80 * s)
    p.cubicTo(x + 80 * s, y - 20 * s, x, y - 10 * s, x, y + 50 * s)
    return join(p, circle(x, y + 115 * s, 12 * s))


# ---------------------------------------------------------------- 开局：十点还在工位（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("十点了，还在工位", "灵魂拷问", (950, 900, 0.85), bars=2)
L(desk(1000, 1060, 460), 0, 0.9, sfx="wood_high")
L(join(clock(1280, 560, 90), hands_at(1280, 560, 90, 10, 0)), 1, 1.9, BLACK, 9, sfx="pop")
T("22:00", 1280, 720, 64, RED, k0=2, k1=3.2, sfx="pop")
L(stick(690, 1300, 0.8, "hold"), 3, 3.8, BLUE, 10, sfx="wood_high")
L(face(690, 1300, 0.8, "flat"), 3.8, 4.0, BLUE, 9)
T("阿宁", 690, 1370, 50, BLUE, k0=5, k1=5.8, sfx="pop")

SCR = (2650, 820)
scene("辞职信写了又关", "灵魂拷问", (2650, 900, 0.85))
L(monitor(*SCR), 0, 0.9, sfx="wood_high")
T("辞职信", SCR[0], 660, 64, k0=1, k1=1.8, sfx="pop")
L(doc(SCR[0], 860, 300, 210, 4), 2, 2.8, BLACK, 7, sfx="wood_low")
L(join(P((SCR[0] - 220, 640), (SCR[0] + 220, 1000)), P((SCR[0] + 220, 640), (SCR[0] - 220, 1000))), 3, 3.8, RED, 12,
  sfx="rim")
b.erase(J(), 4, 4.9, SCR[0], SCR[1], 720, 440)
H(4, "shaker")
T("又关了", SCR[0], 820, 56, GRAY, k0=5, k1=5.8, sfx="pop")
T("靠什么撑下去？", SCR[0], 1300, 90, RED, k0=6, k1=8, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 3–7）

scene("他在营里活了下来", "活出生命的意义 · 书中观点", (950, 2300, 0.85))
L(book(720, 2200, 400, 270), 0, 0.9, sfx="wood_low")
T("活出生命的意义", 720, 1960, 60, GREEN, k0=1, k1=2.75, sfx="pop")
T("弗兰克尔", 720, 2440, 64, k0=3, k1=4, sfx="pop")
T("精神科医生", 720, 2530, 48, k0=4, k1=5.0, sfx="pop")
L(join(underline(1080, 1560, 2420, amp=8, step=60), huts(1170, 2420, 3, 110, 70, 30)), 5, 6, GRAY, 7, sfx="wood_high")
T("活了下来", 1320, 2560, 56, k0=7, k1=8, sfx="pop")

# drop 前一拍：镜头先移到天平那一屏，天平和那摞“怎么”提前画好，第 0 拍“为什么”砸下去
V4 = (2650, 2300, 0.8)
b.move(J(), 10.0, V4, dur=0.75)

PIV = (2500, 2120)               # 天平支点
ARM, HANG = 380, 260             # 半臂长、吊绳长
TILT = math.radians(15)
NAN = (3130, 2650)               # 阿宁脚底
COMP4 = (3130, 2525, 46)         # 阿宁胸前罗盘


def _pan_pos(side, a):
    """side=-1 左盘、+1 右盘；a>0 左低右高。返回盘口中点。"""
    ex = PIV[0] + side * ARM * math.cos(a)
    ey = PIV[1] - side * ARM * math.sin(a)
    return ex, ey, ex, ey + HANG


def _tilt_at(t):
    t_imp = b.t_of(J4, 0)
    if t < t_imp:
        return TILT
    f = clamp01((t - t_imp) / 0.32)
    over = 1 - (1 - f) ** 3 * (1 - 2.6 * f) if f < 1 else 1     # 回弹一下再停
    return TILT - 2 * TILT * min(1.12, over) if f < 1 else -TILT


def balance_fn(c, k, t):
    alpha = clamp01(k * 1.6)
    a = _tilt_at(t)
    ink = K.paint(BLACK, alpha, 9)
    lx, ly = PIV[0] - ARM * math.cos(a), PIV[1] + ARM * math.sin(a)
    rx, ry = PIV[0] + ARM * math.cos(a), PIV[1] - ARM * math.sin(a)
    c.drawPath(P((lx, ly), (rx, ry)), ink)
    c.drawCircle(PIV[0], PIV[1], 14, K.paint(BLACK, alpha))
    for side in (-1, 1):
        ex, ey, px, py = _pan_pos(side, a)
        pan = skia.Path()
        pan.addArc(skia.Rect.MakeXYWH(px - 120, py - 40, 240, 80), 0, 180)
        c.drawPath(join(P((px - 120, py), (ex, ey), (px + 120, py)), pan, P((px - 120, py), (px + 120, py))), ink)
    _, _, px, py = _pan_pos(-1, a)
    for i in range(3):                                   # 左盘：一摞“怎么”
        by = py - 34 - i * 64
        c.drawPath(rect(px, by, 170, 60, 8), K.paint(BLACK, alpha, 6))
        K.text(c, "怎么", px, by, 50, "hand", BLACK, alpha)
    t_imp = b.t_of(J4, 0)
    if t >= t_imp:                                       # 右盘：红色“为什么”砸进来
        f = clamp01((t - t_imp) / 0.22)
        s = 1 + 0.7 * (1 - f) ** 2
        _, _, px, py = _pan_pos(1, a)
        by = py - 60
        c.save()
        c.translate(px, by)
        c.scale(s, s)
        c.drawPath(rect(0, 0, 250, 110, 12), K.paint(RED, 1, 9))
        K.text(c, "为什么", 0, 0, 76, "hand", RED)
        c.restore()
    return None


scene("知道为什么，就扛得住", "活出生命的意义 · 书中观点", V4, shake=[0], flashes=[0])
J4 = J()
L(join(P(PIV, (PIV[0], 2650)), P((PIV[0] - 160, 2650), (PIV[0] + 160, 2650))), -1.5, -0.9, BLACK, 9)
b.custom(J4, -0.9, -0.2, balance_fn)
H(0, "kick")
T("知道为什么而活", 2650, 1790, 64, RED, k0=2, k1=3.75, sfx="pop")
T("就扛得住怎么活", 2650, 1890, 64, k0=4, k1=5.75, sfx="pop")
L(stick(*NAN, 0.75, "down"), 6, 6.7, BLUE, 9, sfx="wood_high")
L(face(*NAN, 0.75, "smile"), 6.7, 6.9, BLUE, 8)
L(compass(*COMP4), 7, 7.5, BLACK, 7, sfx="pop")
_, _, RPX, RPY = _pan_pos(1, -TILT)
b.custom(J4, 7.5, 8.0, needle_fn(*COMP4, (RPX, RPY - 60), turns=1.5))
H(8, "ding")

scene("有盼头的人撑得住", "书中观点 · 盼头", (2650, 3700, 0.85))
HZ = 3260
L(join(P((2080, HZ), (3220, HZ)), P((2130, 4000), (2390, HZ)), P((2520, 4000), (2430, HZ))), 0, 0.9, BLACK, 9,
  sfx="wood_low")
L(join(P((2780, 4000), (2880, HZ)), P((3170, 4000), (2920, HZ))), 1, 1.8, BLACK, 9, sfx="wood_high")
L(flag(2900, HZ, 170), 2, 2.8, RED, 9, sfx="ding")
L(join(stick(2330, 3960, 0.4, "down"), stick(2970, 3960, 0.4, "down")), 3, 3.8, GRAY, 7, sfx="pop")
T("没指望", 2320, 4110, 56, GRAY, k0=5, k1=5.8, sfx="pop")
T("有盼头", 2980, 4110, 56, RED, k0=6, k1=6.8, sfx="pop")
T("撑得住", 2980, 3080, 50, RED, k0=7, k1=7.8, sfx="wood_high")

scene("他想着以后的讲台", "书中故事 · 雪地", (950, 3700, 0.85))
L(underline(380, 1520, 4150, amp=10, step=70), 0, 0.9, GRAY, 7, sfx="wood_low")
L(stick(560, 4150, 0.7, "down"), 1, 1.8, GRAY, 8, sfx="wood_high")
L(join(circle(640, 3860, 14), circle(700, 3790, 20), circle(770, 3715, 26)), 2, 2.6, BLACK, 7, sfx="pop")
L(rect(1080, 3420, 820, 460, 200), 3, 3.9, BLACK, 8, sfx="wood_high")
L(podium(1080, 3440, 1.0), 4, 4.8, RED, 8, sfx="pop")
L(join(*[circle(780 + i * 75, 3600, 16) for i in range(9)]), 5, 5.8, RED, 7, sfx="pop")
T("战后的讲台", 1080, 3290, 50, k0=6, k1=7.25, sfx="pop")

ROW1, ROW2 = 4800, 5050
COMP7 = (950, 5420, 100)
scene("先找为什么", "书中观点 · 一张图", (950, 5100, 0.85))
T("只有怎么 → 耗光", 860, ROW1, 70, GRAY, k0=0, k1=2, sfx="pop")
L(join(rect(1390, ROW1, 130, 64, 10), rect(1470, ROW1, 14, 26, 3)), 2, 2.8, GRAY, 7, sfx="wood_low")
T("有为什么 → 撑得住", 860, ROW2, 70, RED, k0=3, k1=5, sfx="pop")
L(compass(*COMP7), 5, 5.8, BLACK, 8, sfx="wood_high")
b.custom(J(), 5.8, 7.0, needle_fn(*COMP7, (640, ROW2 + 10), turns=2.5))
H(6, "shaker", 0.6)
H(7, "ding")

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

QX = [2700, 2800, 2900, 3000, 3100]
scene("知道这版为谁改", "例子 · 加班改版", (2650, 5100, 0.85))
L(desk(2350, 5060, 420), 0, 0.9, sfx="wood_high")
T("改版", 2390, 5000, 46, k0=1, k1=1.8, sfx="pop")
L(join(*[stick(x, 5350, 0.4, "down") for x in QX]), 2, 2.9, BLACK, 7, sfx="wood_high")
T("客户在排队", 2860, 5120, 50, k0=3, k1=4.25, sfx="pop")
b.erase(J(), 5, 5.8, 3010, 5290, 290, 190)
H(5, "shaker")
T("这版上线，队短了", 2650, 4780, 58, RED, k0=6, k1=8, sfx="ding")

scene("为了离家近一点", "例子 · 熬夜考证", (950, 6500, 0.85))
L(desk(820, 6450, 380), 0, 0.9, sfx="wood_high")
L(desk_lamp(700, 6450, 1.0), 1, 1.8, BLACK, 8, sfx="pop")
T("深夜考证", 800, 6110, 58, k0=2, k1=3, sfx="pop")
L(map_sheet(1220, 6560, 400, 300), 3, 3.8, BLACK, 8, sfx="wood_low")
L(join(circle(1110, 6630, 16), circle(1330, 6480, 16)), 4, 4.5, RED, 9, sfx="pop")
T("家", 1330, 6400, 52, RED, k0=5, k1=5.8, sfx="pop")
L(arrow((1125, 6615), (1310, 6495), 0.15, 30), 6, 6.8, RED, 8, sfx="wood_high")
T("离家近一点", 1220, 6830, 52, k0=7, k1=8, sfx="pop")

VFAR10 = (1800, 5850, 0.42)
scene("都知道为了谁", "例子 · 半夜冲奶", (2650, 6500, 0.85))
L(moon(2950, 6150, 80), 0, 0.9, BLACK, 9, sfx="wood_low")
L(bottle(2520, 6520, 1.0), 1, 1.9, BLACK, 9, sfx="pop")
L(stick(2280, 6800, 0.7, "hold"), 2, 2.8, BLUE, 9, sfx="wood_high")
b.move(J(), 3, VFAR10, dur=1.1)
H(3, "shaker", 0.6)
for n, (a, z) in enumerate((((2150, 5150), (1080, 5420)), ((960, 6040), (955, 5555)),
                            ((2200, 6330), (1070, 5500)))):
    L(arrow(a, z, 0.08 if n != 1 else 0.0, 60), 4 + n, 4.8 + n, GREEN, 14, sfx="wood_high")
T("都为了谁", 1800, 6560, 110, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

NOTE = (1230, 7800, 260, 260)
scene("写下为了谁", "做法① · 写便签", (950, 7900, 0.85))
T("① 写一张便签", 950, 7450, 72, BLUE, k0=0, k1=1.75, sfx="pop")
L(monitor(790, 7850, 480, 320), 2, 2.8, BLACK, 9, sfx="wood_high")
b.custom(J(), 3, 3.6, fill_fn(rect(*NOTE, 10), YELLOW))
L(rect(*NOTE, 10), 3, 3.8, YELLOW, 8, sfx="pop")
T("为了", NOTE[0], 7735, 52, k0=4, k1=4.8, sfx="pop")
T("客户少等", NOTE[0], 7835, 52, RED, k0=5, k1=6, sfx="pop")
L(underline(1120, 1340, 7885, amp=6, step=36), 7, 7.8, RED, 7, sfx="ding")

NOTE12 = (2930, 7800, 260, 200)
COMP12 = (2400, 8125, 44)
scene("难受时看一眼", "做法② · 看一眼", (2650, 7900, 0.85))
T("② 撑不住那天", 2650, 7450, 72, BLUE, k0=0, k1=1.75, sfx="pop")
L(stick(2400, 8250, 0.8, "hold"), 2, 2.8, BLUE, 10, sfx="wood_high")
L(face(2400, 8250, 0.8, "flat"), 2.8, 3.0, BLUE, 9)
b.custom(J(), 3, 3.6, fill_fn(rect(*NOTE12, 10), YELLOW))
L(rect(*NOTE12, 10), 3, 3.8, YELLOW, 8, sfx="pop")
T("客户少等", NOTE12[0], 7800, 52, RED, k0=4, k1=5, sfx="pop")
L(compass(*COMP12), 5, 5.6, BLACK, 7, sfx="wood_high")
b.custom(J(), 5.6, 7.0, needle_fn(*COMP12, (NOTE12[0], NOTE12[1]), turns=2))
H(6, "shaker", 0.5)
H(7, "ding")
T("看完再决定", 2700, 8420, 56, k0=7, k1=8)

QM = (750, 9400)
scene("谁会好一点", "做法③ · 换个问法", (950, 9300, 0.85))
T("③ 找不到为什么", 950, 8850, 70, BLUE, k0=0, k1=2, sfx="pop")
T("就问：这事做成了，谁会好一点？", 950, 8990, 54, k0=2, k1=5, sfx="pop")
L(qmark(*QM, 1.0), 5, 5.8, BLACK, 12, sfx="wood_high")
b.erase(J(), 5.8, 6.0, QM[0], QM[1] - 20, 260, 340)
L(stick(QM[0], 9580, 0.7, "up"), 6, 6.7, BLUE, 9, sfx="pop")
L(face(QM[0], 9580, 0.7, "smile"), 6.7, 6.9, BLUE, 8)
T("会好一点", 1150, 9420, 60, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5400, 0.16)
CMT = (1800, 10450, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(bubble(1800, 10330, 1000, 220, -1), 5, 5.8, BLACK, 8)
T("你在为什么撑着？", 1800, 10330, 76, RED, k0=6, k1=8, sfx="pop")
T("下一讲：事情改不了，心情能自己定吗？", 1800, 10620, 50, k0=9, k1=13.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "why", "为什么而活", "累到想辞职，靠什么撑下去？", ACC, b.shots,
                 [f"{BOOK}第一部分 在集中营的经历（转述）",
                  "Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010"],
                 "累到想辞职|靠什么【撑下去】", SQUARE_SHOT,
                 ["书中观点为转述，均见第一部分 在集中营的经历：作者是精神科医生，二战时被关进集中营，几年后活了下来；"
                  "书中引尼采的话，大意是知道为什么而活的人，几乎能忍受任何怎么活；作者观察到对将来失去指望的人往往最先撑不住，"
                  "有盼头的人更能撑；他在最难的时候想象自己战后站在讲台上讲集中营心理学。上屏均为转述，不是逐字引文。",
                  "天平、“怎么 / 为什么”方块、两条路与小旗、“只有怎么 → 耗光 / 有为什么 → 撑得住”一图，为对书中观点的通俗化示意；"
                  "营里的画面只画灰线雪地、木棚屋剪影和小人，不画作者肖像。",
                  "周三晚上十点在工位、辞职信、加班改版、熬夜考证、半夜冲奶均为现实场景示意，不指向任何具体公司或个人；"
                  "阿宁为示意角色；时间为示意，不是数据。",
                  "三步做法（写一张“为了___”的便签；撑不住那天先看一眼再决定；找不到就问“这事做成了，谁会好一点”）"
                  "为据书中思路整理的建议。"],
                 tags="#工作意义 #打工人日常")
    return b.attach(ep)
