"""01 想法管心情（白板手绘版）：领导没回消息，你慌什么？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍不出新笔画）。
叙事（A 经典）：打工人切身问题开局（晚上十点给领导发了方案，手机上显示“已读”，一小时没回 → 小周头顶第一次冒出乌云
「他嫌我做得差」）→ 书中观点（亮书；★drop：同一条已读未回分出三朵念头云、三张脸；“事情 → 想法 → 心情”三格链条，
中间那格管心情；心情差时想法会歪，人还当真）→ 身边的例子（开会被打断、朋友圈没人点赞、爸妈电话里叹气，三朵乌云
都连到“想法”这一格）→ 具体做法（抓住那句话抄到便签 / 找证据 / 写一个别的可能，乌云缩小）→ 预告十种歪法 → 评论区互动。
系列视觉角色：小周（戴工牌）+ 念头云（乌云红字 / 白云蓝字）。
书中观点为转述（David D. Burns, Feeling Good: The New Mood Therapy, 1980；中译本《伯恩斯新情绪疗法》，李亚萍译，
中国城市出版社 2011 / 科学技术文献出版社 2014；简介“思维决定情绪”、第3章“破解情绪：思维决定情绪”）；
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, check, circle, clock, face, join,
                               rect, stick, underline)

from .common import BOOK, episode

ACC = "#4A6FA5"
SQUARE_SHOT = 3                 # 场景 4：同一条已读未回 → 三朵念头云 → 三个小人三张脸

b = Board(size=(3800, 16300))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = J() if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(fn, k0, k1, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


# ---------------------------------------------------------------- 本讲画法

def cloud(x, y, w, h, n=9, tilt=0.0) -> skia.Path:
    """念头云：椭圆上一圈鼓包。(x, y) 为中心，外沿约 w × h。tilt 为旋转角度（度）。"""
    a, bb = w / 2 * 0.84, h / 2 * 0.74
    pts, ctr = [], []
    for i in range(n + 1):
        th = 2 * math.pi * i / n + 0.2
        pts.append((x + a * math.cos(th), y + bb * math.sin(th)))
        tm = th + math.pi / n
        ctr.append((x + a * 1.38 * math.cos(tm), y + bb * 1.5 * math.sin(tm)))
    p = skia.Path()
    p.moveTo(*pts[0])
    for i in range(n):
        p.quadTo(*ctr[i], *pts[i + 1])
    p.close()
    if tilt:
        m = skia.Matrix()
        m.setRotate(tilt, x, y)
        p.transform(m)
    return p


def dots(x0, y0, x1, y1) -> skia.Path:
    """念头云底下连到脑袋的三个小圆圈（由大到小）。"""
    return join(*[circle(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, r) for f, r in ((0.15, 20), (0.55, 14), (0.9, 9))])


def dark_fn(path):
    """乌云：把云涂暗，再加一圈深色毛边。"""
    def fn(c, k, t):
        c.drawPath(path, K.paint("#3A3F4A", 0.16 * k))
        c.drawPath(path, K.paint("#3A3F4A", 0.32 * k, 26))
        return None

    return fn


def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """小周：简笔小人 + 挂绳工牌。(x, y) 为脚底。"""
    hy = y - 290 * s
    return join(stick(x, y, s, arms),
                P((x - 22 * s, hy + 42 * s), (x - 4 * s, hy + 92 * s)), P((x + 22 * s, hy + 42 * s), (x + 4 * s, hy + 92 * s)),
                rect(x, hy + 118 * s, 40 * s, 50 * s, 6 * s))


def mouth_open(x, y, s=1.0) -> skia.Path:
    """张着嘴说话：两只眼 + 圆嘴。(x, y) 为该小人脚底。"""
    hy = y - 290 * s
    return join(circle(x - 15 * s, hy - 8 * s, 3 * s), circle(x + 15 * s, hy - 8 * s, 3 * s), circle(x, hy + 20 * s, 10 * s))


def tear(x, y, s=1.0) -> skia.Path:
    hy = y - 290 * s
    p = skia.Path()
    tx, ty = x - 20 * s, hy + 4 * s
    p.moveTo(tx, ty)
    p.quadTo(tx - 10 * s, ty + 22 * s, tx, ty + 26 * s)
    p.quadTo(tx + 10 * s, ty + 22 * s, tx, ty)
    return p


def phone(x, y, w, h) -> skia.Path:
    return join(rect(x, y, w, h, 36), P((x - 40, y - h / 2 + 30), (x + 40, y - h / 2 + 30)), circle(x, y + h / 2 - 34, 13))


def sent(x, y, w, h) -> skia.Path:
    """发出去的消息气泡（尾巴在右下）。"""
    p = rect(x, y, w, h, 30)
    p.moveTo(x + w / 2 - 40, y + h / 2)
    p.lineTo(x + w / 2 + 20, y + h / 2 + 30)
    p.lineTo(x + w / 2 - 10, y + h / 2 - 20)
    return p


def rays(x, y, w, h) -> skia.Path:
    parts = []
    for dx, dy, ex, ey in ((-1, -1, -1.25, -1.5), (0, -1.15, 0, -1.6), (1, -1, 1.25, -1.5)):
        parts.append(P((x + dx * w / 2, y + dy * h / 2), (x + ex * w / 2, y + ey * h / 2)))
    return join(*parts)


def heart(x, y, r=40) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def post(x, y) -> skia.Path:
    """朋友圈一条动态：头像 + 一行字 + 一张图（山和太阳）。(x, y) 为图片中心。"""
    return join(circle(x - 110, y - 190, 30), P((x - 60, y - 195), (x + 120, y - 195)),
                rect(x, y, 290, 200, 10), P((x - 130, y + 85), (x - 40, y - 20), (x + 20, y + 40), (x + 70, y), (x + 130, y + 85)),
                circle(x + 80, y - 50, 22))


def grab(x, y) -> skia.Path:
    """一只手从右边抓住东西：手掌 + 四根弯过来的手指。(x, y) 为指尖一侧中点。"""
    parts = [rect(x + 95, y, 110, 140, 44), P((x + 150, y + 70), (x + 200, y + 150))]
    for i in range(4):
        yy = y - 48 + i * 32
        parts.append(P((x + 45, yy), (x + 5, yy - 6), (x - 18, yy + 10)))
    return join(*parts)


def sticky(x, y, w, h) -> skia.Path:
    """便签：右下角折起。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 50), (x + w / 2 - 50, y + h / 2),
                  (x - w / 2, y + h / 2), close=True),
                P((x + w / 2, y + h / 2 - 50), (x + w / 2 - 50, y + h / 2 - 50), (x + w / 2 - 50, y + h / 2)))


def magnifier(x, y, r=90) -> skia.Path:
    return join(circle(x, y, r), P((x + r * 0.72, y + r * 0.72), (x + r * 1.7, y + r * 1.7)))


def zigzag(x0, y0, x1, y1) -> skia.Path:
    """打断：一道折线闪电。"""
    dx, dy = x1 - x0, y1 - y0
    return P((x0, y0), (x0 + dx * 0.4 - 30, y0 + dy * 0.35), (x0 + dx * 0.55 + 30, y0 + dy * 0.5), (x1, y1))


# ---------------------------------------------------------------- 开局：已读不回（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


PH = (800, 950)                 # 开局手机
scene("方案发过去了", "灵魂拷问", (950, 900, 0.85), bars=2, shake=[4])
L(phone(*PH, 420, 680), 0, 0.9, sfx="wood_high")
L(sent(PH[0], 830, 320, 120), 1, 1.8, BLUE, 8, sfx="pop")
T("方案终稿", PH[0], 830, 56, k0=1.8, k1=2.8)
T("22:00", PH[0], 690, 50, k0=3, k1=3.8, sfx="pop")
T("已读", 1310, 950, 150, RED, k0=4, k1=4.6, sfx="kick")
L(rays(1310, 950, 330, 170), 5, 5.8, RED, 8, sfx="pop")

ZA = (1800, 1560)               # 小周（开局）
CA = cloud(1800, 820, 560, 300)
scene("越等越慌", "灵魂拷问", (1350, 950, 0.7))
L(clock(1330, 1250, 110), 0, 0.9, BLACK, 9, sfx="wood_high")


def clock_fn(c, k, t):
    """时钟指针转一圈：22:00 → 23:00。"""
    x, y, r = 1330, 1250, 110
    am = -math.pi / 2 + 2 * math.pi * k
    ah = -math.pi / 2 + (10 + k) / 12 * 2 * math.pi
    pm = P((x, y), (x + math.cos(am) * r * 0.75, y + math.sin(am) * r * 0.75))
    ph = P((x, y), (x + math.cos(ah) * r * 0.5, y + math.sin(ah) * r * 0.5))
    c.drawPath(pm, wb.marker(BLACK, 8))
    c.drawPath(ph, wb.marker(BLACK, 11))
    return (x + math.cos(am) * r * 0.75, y + math.sin(am) * r * 0.75) if k < 1 else None


C(clock_fn, 1, 2.6, sfx="tom")
T("23:00", 1330, 1430, 60, RED, k0=3, k1=4, sfx="pop")
L(zhou(*ZA, 0.9), 4, 4.8, sfx="wood_high")
L(face(*ZA, 0.9, "sad"), 4.8, 5.0)
L(join(CA, dots(1800, 990, 1800, 1220)), 5, 5.9, BLACK, 9, sfx="wood_low")
C(dark_fn(CA), 5.9, 6.4)
T("他嫌我做得差", 1800, 820, 64, RED, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 3–6）

scene("这本书讲这个", "书中观点 · 亮书", (950, 2250, 0.85))
L(book(780, 2300, 460, 320), 0, 0.9, BLACK, 10, sfx="wood_low")
T("《伯恩斯新情绪疗法》", 950, 1950, 66, GREEN, k0=1, k1=3, sfx="pop")
L(underline(640, 1260, 2010), 3, 3.8, GREEN, 8, sfx="ding")
L(cloud(1290, 2230, 300, 160), 4, 4.8, BLUE, 8, sfx="wood_high")
T("想法", 1290, 2230, 56, BLUE, k0=4.8, k1=5.6)
T("伯恩斯 · 美国精神科医生", 950, 2660, 54, k0=6, k1=8, sfx="pop")

# ★ drop：同一条已读未回，三朵念头云，三张脸
XS = (1230, 1800, 2370)
CY4 = 3640
FEET4 = 4300
S4 = 0.75
C4 = [cloud(x, CY4, 500, 240) for x in XS]
scene("同一件事三种心情", "书中观点 · 同一件事", (1800, 3800, 0.62), shake=[0], flashes=[0])
L(sent(1800, 3150, 460, 140), 0, 0.6, RED, 9, sfx="kick")
T("方案 · 已读", 1800, 3150, 70, RED, k0=0.6, k1=1.0)
L(join(*[arrow((1800, 3245), (x, 3470), 0.0 if x == 1800 else (0.12 if x < 1800 else -0.12), 40) for x in XS]),
  1, 1.8, BLACK, 9, sfx="wood_high")
L(join(C4[0], dots(XS[0], 3775, XS[0], 4030)), 2, 2.8, BLACK, 9, sfx="pop")
L(join(C4[1], dots(XS[1], 3775, XS[1], 4030), C4[2], dots(XS[2], 3775, XS[2], 4030)), 2, 2.8, BLUE, 9)
C(dark_fn(C4[0]), 2.8, 3.2)
T("他嫌我差", XS[0], CY4, 66, RED, k0=3, k1=4, sfx="pop")
T("他睡了", XS[1], CY4, 66, BLUE, k0=4, k1=4.75, sfx="pop")
T("他在开会", XS[2], CY4, 66, BLUE, k0=5, k1=6, sfx="pop")
L(join(*[zhou(x, FEET4, S4) for x in XS]), 6, 6.8, BLACK, 9, sfx="wood_high")
L(join(face(XS[0], FEET4, S4, "sad"), tear(XS[0], FEET4, S4), face(XS[1], FEET4, S4, "flat"),
       face(XS[2], FEET4, S4, "smile")), 7, 7.8, BLACK, 8, sfx="ding")

scene("中间这格管心情", "书中观点 · 想法管心情", (1800, 5300, 0.72))
for n, (x, word) in enumerate(zip((1300, 1800, 2300), ("事情", "想法", "心情"))):
    L(rect(x, 5000, 340, 200, 20), 2 * n, 2 * n + 0.6, BLACK, 9, sfx="wood_high")
    T(word, x, 5000, 80, RED if n == 1 else BLACK, k0=2 * n + 0.6, k1=2 * n + 1.0)
    if n < 2:
        L(arrow((x + 185, 5000), (x + 315, 5000), 0.0, 36), 2 * n + 1, 2 * n + 1.5, BLACK, 9, sfx="pop")
L(rect(1800, 5000, 440, 290, 30), 5, 5.8, RED, 14, sfx="ding")
T("心情跟着想法走", 1800, 5330, 72, k0=6, k1=7.75, sfx="pop")

ZB = (1350, 6800)
CB = cloud(1950, 6150, 680, 320, tilt=-8)
scene("歪了还当真", "书中观点 · 想歪了", (1800, 6350, 0.8))
L(zhou(*ZB, 0.9), 0, 0.8, sfx="wood_high")
L(face(*ZB, 0.9, "sad"), 0.8, 1.0)
L(join(CB, dots(1720, 6330, 1420, 6500)), 1, 1.9, BLACK, 10, sfx="wood_low")
C(dark_fn(CB), 1.9, 2.3)
T("他嫌我做得差", 1950, 6150, 66, RED, k0=2, k1=3.5, sfx="pop")
L(join(P((2200, 6290), (2240, 6460)), rect(2250, 6530, 260, 110, 14)), 4, 4.8, RED, 9, sfx="wood_high")
T("当真了", 2250, 6530, 60, RED, k0=5, k1=5.75, sfx="pop")
T("心情差时，想法会歪", 1800, 5860, 62, k0=6, k1=8, sfx="pop")

# ---------------------------------------------------------------- 身边的例子（场景 7–9）：三格一排，最后拉远连到“想法”

EY = 9300                       # 例子一排的视图中心
CYE = 8930                      # 三朵乌云的中心高度（拉远时连箭头）
FEE = 9700                      # 小人脚底
SE = 0.75

CE1 = cloud(800, CYE, 600, 240)
scene("开会被打断", "例子 · 开会", (800, EY, 0.9))
L(join(P((420, 9560), (1180, 9560)), P((460, 9560), (460, 9700)), P((1140, 9560), (1140, 9700))), 0, 0.8,
  sfx="wood_high")
L(join(zhou(560, FEE, SE, "point"), mouth_open(560, FEE, SE)), 1, 1.8, BLACK, 9, sfx="pop")
L(join(stick(1060, FEE, SE, "up", tie=True), face(1060, FEE, SE, "flat")), 2, 2.8, BLACK, 9, sfx="wood_high")
L(sent(660, 9250, 300, 110), 3, 3.6, BLACK, 8, sfx="pop")
T("我觉得", 660, 9250, 56, k0=3.6, k1=4.0)
L(zigzag(1000, 9140, 760, 9360), 4, 4.6, RED, 11, sfx="rim")
L(join(CE1, dots(720, 9055, 600, 9135)), 5, 5.8, BLACK, 9, sfx="wood_low")
C(dark_fn(CE1), 5.8, 6.2)
T("我说的都是废话", 800, CYE, 60, RED, k0=6, k1=7.75, sfx="pop")

CE2 = cloud(2150, CYE, 520, 240)
scene("朋友圈没人点赞", "例子 · 朋友圈", (1900, EY, 0.9))
L(phone(1700, 9300, 380, 640), 0, 0.8, BLACK, 9, sfx="wood_high")
L(post(1700, 9240), 1, 1.9, BLACK, 7, sfx="pop")
L(heart(1600, 9470, 26), 2, 2.6, RED, 7, sfx="pop")
T("0", 1660, 9470, 60, RED, k0=2.6, k1=3.0)
L(zhou(2200, FEE + 100, SE), 3, 3.8, sfx="wood_high")
L(face(2200, FEE + 100, SE, "sad"), 3.8, 4.0)
L(join(CE2, dots(2180, 9060, 2200, 9520)), 4, 4.8, BLACK, 9, sfx="wood_low")
C(dark_fn(CE2), 4.8, 5.2)
T("没人在乎我", 2150, CYE, 64, RED, k0=5, k1=6.25, sfx="pop")

CE3 = cloud(3150, CYE, 600, 240)
BOX = (1900, 8100)              # 三朵乌云连到的“想法”格
OVER = (1900, 9000, 0.33)
scene("都卡在想法这格", "例子 · 爸妈电话", (3000, EY, 0.9))
L(phone(2750, 9380, 300, 500), 0, 0.7, BLACK, 9, sfx="wood_high")
T("妈妈", 2750, 9330, 56, k0=0.7, k1=1.0)
T("唉", 2750, 9760, 70, k0=1, k1=1.6, sfx="pop")
L(zhou(3250, FEE + 100, SE, "hold"), 2, 2.7, sfx="wood_high")
L(face(3250, FEE + 100, SE, "sad"), 2.7, 2.9)
L(join(CE3, dots(3220, 9060, 3250, 9520)), 3, 3.7, BLACK, 9, sfx="wood_low")
C(dark_fn(CE3), 3.7, 4.0)
T("又让他们失望了", 3150, CYE, 60, RED, k0=3.7, k1=5.2)
b.move(J(), 5.5, OVER, dur=1.0)
L(join(arrow((850, 8790), (BOX[0] - 120, BOX[1] + 140), -0.08, 60),
       arrow((2150, 8790), (BOX[0] + 40, BOX[1] + 140), 0.05, 60),
       arrow((3100, 8790), (BOX[0] + 180, BOX[1] + 140), 0.08, 60)), 6, 6.9, RED, 16, sfx="wood_high")
L(rect(*BOX, 520, 260, 26), 7, 7.5, RED, 18, sfx="ding")
T("想法", *BOX, 160, RED, k0=7.5, k1=8.0)

# ---------------------------------------------------------------- 具体做法（场景 10–12）

CD = cloud(750, 11150, 560, 260)
NOTE = (1420, 11620)
scene("先把那句话抓住", "第一步 · 抓住那句话", (1000, 11300, 0.85))
T("① 先抓住那句话", 960, 10850, 72, BLUE, k0=0, k1=1.75, sfx="pop")
L(CD, 2, 2.8, BLACK, 9, sfx="wood_low")
C(dark_fn(CD), 2.8, 3.2)
T("他嫌我做得差", 750, 11150, 60, RED, k0=2.8, k1=4.0)
L(grab(1010, 11180), 4, 4.8, BLACK, 9, sfx="shaker")
L(arrow((800, 11330), (NOTE[0] - 220, NOTE[1]), 0.18, 40), 5, 5.7, BLACK, 9, sfx="wood_high")
L(sticky(*NOTE, 400, 220), 6, 6.7, ORANGE, 9, sfx="pop")
T("他嫌我做得差", NOTE[0], NOTE[1] - 10, 52, k0=6.7, k1=8.0)

scene("找找证据", "第二步 · 找证据", (1800, 11700, 0.85))
T("② 证据呢？", 1900, 11250, 72, BLUE, k0=0, k1=1.25, sfx="pop")
L(magnifier(1530, 11590, 95), 1, 1.8, BLACK, 9, sfx="wood_high")
T("他已读了", 2080, 11560, 64, k0=2, k1=3, sfx="pop")
L(check(1860, 11560, 40), 3, 3.6, GREEN, 10, sfx="ding")
T("没说哪里差", 2080, 11730, 64, k0=4, k1=5.25, sfx="pop")
L(check(1860, 11730, 40), 6, 6.6, GREEN, 10, sfx="ding")
T("其余靠猜", 1940, 11950, 64, RED, k0=7, k1=8, sfx="pop")

DK = (1950, 12550)              # 第三步：缩小的乌云
DKP = cloud(*DK, 460, 230)
ZC = (2400, 13370)
scene("再写一个可能", "第三步 · 换个可能", (2300, 12800, 0.85))
J12 = J()


def shrink_fn(c, k, t):
    """乌云先画出来、写上字；第 6 拍缩到一半大小。"""
    t6 = b.t_of(J12, 6)
    s = 1 - 0.45 * ease_in_out(clamp01((t - t6) / 0.45))
    x, y = DK
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.translate(-x, -y)
    tip = None
    if k < 0.45:
        part, tip = wb.partial(DKP, k / 0.45)
        c.drawPath(part, wb.marker(BLACK, 9))
    else:
        dark_fn(DKP)(c, 1.0, t)
        c.drawPath(DKP, wb.marker(BLACK, 9))
        f = clamp01((k - 0.45) / 0.55)
        w = K.text_w("他嫌我做得差", 54, "hand")
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x - w / 2 - 20, y - 54, x - w / 2 + w * f + 4, y + 54))
        K.text(c, "他嫌我做得差", x, y, 54, "hand", RED)
        c.restore()
        if k < 1:
            tip = (x - w / 2 + w * f, y)
    c.restore()
    return tip


C(shrink_fn, 0, 1.8, sfx="wood_low")
CW = cloud(2350, 12850, 700, 300)
L(join(CW, dots(2380, 13020, 2400, 13110)), 2, 2.8, BLUE, 9, sfx="wood_high")
T("他可能还没看完", 2350, 12850, 60, BLUE, k0=3, k1=4.5, sfx="pop")
L(zhou(*ZC, 0.7), 5, 5.7, sfx="wood_high")
L(face(*ZC, 0.7, "smile"), 5.7, 5.9)
H(6, "rim")
T("心里松了点", 1990, 13250, 60, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 预告（场景 13）：十朵乌云排两行

COLS = (1200, 1500, 1800, 2100, 2400)
ROWS = (14100, 14360)
scene("歪法有套路", "下一讲预告", (1800, 14350, 0.7))
T("书里列了十种", 1800, 13800, 84, RED, k0=0, k1=1.5, sfx="pop")
SMALL = []
for n, x in enumerate(COLS):
    pair = [cloud(x, y, 250, 130, n=7) for y in ROWS]
    SMALL += pair
    L(join(*pair), 2 + n, 2.8 + n, BLACK, 8, sfx="wood_high" if n % 2 == 0 else "wood_low")


def ten_dark(c, k, t):
    for p in SMALL:
        dark_fn(p)(c, k, t)
    return None


C(ten_dark, 7, 7.6, sfx="shaker")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FULL = (1900, 7800, 0.095)
END = (1800, 15400, 0.8)
scene("难受久了找医生", "评论区见", FULL, bars=4)
J_END = J()
b.move(J_END, 4, END, dur=1.1)
H(0, "cymbal", 0.5)
L(cloud(2050, 15760, 620, 200), 1, 1.8, BLUE, 9, sfx="wood_high")
T("今天换掉一朵乌云", 2050, 15760, 56, BLUE, k0=1.8, k1=3.4)
T("一直低落、睡不好、不想活，去找医生聊聊", 1800, 15460, 50, GREEN, k0=2, k1=4, sfx="ding")
H(4, "wood_high", 0.6)
T("你最近一次心慌，", 1800, 15000, 74, RED, k0=5, k1=7, sfx="pop")
T("脑子里在想什么？", 1800, 15120, 74, RED, k0=7, k1=9, sfx="pop")
T("下一讲：这五种想法，你中了几个？", 1800, 15300, 52, k0=9, k1=12, sfx="wood_high")
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "mood", "想法管心情", "领导没回消息，你慌什么？", ACC, b.shots,
                 [f"{BOOK}，简介“思维决定情绪”、第一部分第3章“破解情绪：思维决定情绪”（转述）",
                  "中译本：李亚萍译，中国城市出版社 2011；科学技术文献出版社 2014"],
                 "领导没回消息|你【慌】什么", SQUARE_SHOT,
                 ["书中观点均为转述：让人难受的主要是你对一件事的想法，同一件事换个想法，心情就跟着变；心情很差时，"
                  "脑子里的想法常常是扭曲的，人却把它当成事实。见简介“思维决定情绪”与第3章“破解情绪：思维决定情绪”。"
                  "出处：David D. Burns, Feeling Good: The New Mood Therapy (William Morrow, 1980)，中译本《伯恩斯新情绪疗法》"
                  "（戴维·伯恩斯著，李亚萍译，中国城市出版社 2011；科学技术文献出版社 2014）。上屏均为转述，不是逐字引文。",
                  "“事情 → 想法 → 心情”三格链条与“同一条已读未回、三种想法、三张脸”一图，为对书中观点的通俗化示意。",
                  "深夜发方案显示已读、开会被打断、朋友圈没人点赞、爸妈电话里叹气均为现实场景示意，不取自书中病例，"
                  "不指向任何具体公司、个人或软件；时间“22:00 / 23:00”、点赞数“0”为示意，不是数据。",
                  "三步做法（抓住那句话写下来；找找证据；再写一个别的可能）为据书中思路整理的建议。“十种”指书中第3章列出的"
                  "十种认知扭曲，下一讲起分讲。",
                  "本片为读书分享，不能替代诊断和治疗；情绪持续低落或有轻生念头，请尽快联系医生、心理咨询师或当地心理援助热线。"],
                 tags="#情绪管理")
    return b.attach(ep)
