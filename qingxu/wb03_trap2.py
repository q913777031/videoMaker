"""03 再五种想歪（白板手绘版）：心里难受，就说明事情糟？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，每个 3 小节场景第 0–8 拍画完、最后 4 拍停住）。
叙事：D 误区对照——开局一句红字砸出来（“我觉得很糟，所以事情很糟”）→ 接上一讲：角落放上一讲的清单，新开五行表格 →
⑥ 放大和缩小（我的小错 / 他的大功 → ★drop：两只望远镜，看错处正着看放大成巨大的红“错”，看长处倒着看缩成米粒大的“优点”
→ 一屏一对：左边乌云红字 ✗，右边白云蓝字 ✓）→ ⑦ 情绪化推理 → ⑧ 应该句式（“应该”像绳子勒住小周 → 对照）→
⑨ 乱贴标签（胸前挂牌“废物”被划掉）→ ⑩ 罪责归己（箭头全指向小周 → 箭头分散到预算、时间、客户）→
回到表格填满右栏 → 上一讲五种 + 这一讲五种拼成十种 → 做法：给常犯的那种起外号 → 评论区互动。
系列视觉角色：小周（戴工牌）+ 念头云（乌云红字 / 白云蓝字）。
书中观点为转述（David D. Burns, Feeling Good: The New Mood Therapy, 1980；中译本《伯恩斯新情绪疗法》，李亚萍译，
中国城市出版社 2011，第 3 章“破解情绪：思维决定情绪”）；例子为现实场景示意，“起外号”为据书中思路整理的做法。
"""

import math

import skia

from adler import kit as K
from whiteboard.engine import (BLACK, BLUE, ORANGE, RED, Board, P, arrow, check, circle, cross, doc, face, join, rect,
                               stick)

from .common import BOOK, episode

ACC = "#7A52B3"
SQUARE_SHOT = 3                 # 场景 4：望远镜，错处放大、长处缩小

b = Board(size=(3600, 13200))
X = 2000                        # 各种想歪的讲解区（中间一列，自上而下）
TX = 2200                       # 五行表格中心


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

def cloud(x, y, w, h, n=11, tail=None) -> skia.Path:
    """念头云：椭圆一圈鼓包；tail=(tx, ty) 时朝该点画两个小圆（想法泡的尾巴）。"""
    a, bb = w / 2, h / 2
    p = skia.Path()
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        px, py = x + a * math.cos(t), y + bb * math.sin(t)
        if i == 0:
            p.moveTo(px, py)
            continue
        tm = 2 * math.pi * (i - 0.5) / n
        p.quadTo(x + a * 1.22 * math.cos(tm), y + bb * 1.22 * math.sin(tm), px, py)
    if tail:
        tx, ty = tail
        for f, r in ((0.45, 16), (0.8, 10)):
            sx, sy = x + (tx - x) * 0.55, y + bb * 1.1
            p.addCircle(sx + (tx - sx) * f, sy + (ty - sy) * f, r)
    return p


def ring(x, y, w, h, n=46) -> skia.Path:
    """乌云的涂黑边：沿云内侧来回划的锯齿。"""
    a, bb = w / 2, h / 2
    p = skia.Path()
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        r = 1.0 if i % 2 == 0 else 0.86
        q = (x + a * r * math.cos(t), y + bb * r * math.sin(t))
        if i == 0:
            p.moveTo(*q)
        else:
            p.lineTo(*q)
    return p


def dark(x, y, w, h, tail=None) -> skia.Path:
    return join(cloud(x, y, w, h, tail=tail), ring(x, y, w, h))


def zhou(x, y, s=1.0, arms="down", badge=True) -> skia.Path:
    """小周：简笔小人 + 工牌（挂绳 + 胸前小卡）。(x, y) 为脚底。"""
    parts = [stick(x, y, s, arms)]
    if badge:
        hy = y - 290 * s
        parts += [P((x - 16 * s, hy + 46 * s), (x + 10 * s, hy + 100 * s), (x + 16 * s, hy + 46 * s)),
                  rect(x + 10 * s, hy + 122 * s, 36 * s, 44 * s, 5 * s)]
    return join(*parts)


def scope(x0, x1, y, r0, r1) -> skia.Path:
    """望远镜筒（侧视）：x0 端半径 r0，x1 端半径 r1，中间一道箍。"""
    def end(x, r):
        e = skia.Path()
        e.addOval(skia.Rect.MakeXYWH(x - r * 0.3, y - r, r * 0.6, 2 * r))
        return e

    xm, rm = (x0 + x1) / 2, (r0 + r1) / 2
    return join(P((x0, y - r0), (x1, y - r1)), P((x0, y + r0), (x1, y + r1)), end(x0, r0), end(x1, r1),
                P((xm, y - rm), (xm, y + rm)))


def eye(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 45 * s, y)
    p.quadTo(x, y - 40 * s, x + 45 * s, y)
    p.quadTo(x, y + 40 * s, x - 45 * s, y)
    return join(p, circle(x + 6 * s, y, 12 * s))


def star(x, y, r=40) -> skia.Path:
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return P(*pts, close=True)


def tag(x, y, w, h) -> skia.Path:
    """名牌：左端切角的吊牌 + 穿绳小孔。(x, y) 为牌中心。"""
    l, r, t, bt = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    return join(P((l + 40, t), (r, t), (r, bt), (l + 40, bt), (l, y), close=True), circle(l + 38, y, 10))


def fill_fn(x, y, w, h, r=10):
    """白底：先盖住后面的笔画（挂牌用）。"""
    def fn(c, k, t):
        K.rr(c, x, y, w, h, r, "#FBFBF9")
        return None

    return fn


def park(k0, a, z, k1=None):
    """画完后手挪到空白处停住，不挡字（动态项，不算笔画）。"""
    def fn(c, k, t):
        e = k * k * (3 - 2 * k)
        return (a[0] + (z[0] - a[0]) * e, a[1] + (z[1] - a[1]) * e)

    b.custom(J(), k0, k1 or k0 + 0.6, fn)


def pair(cy, title, bad, good, size=64):
    """一屏一对（D 误区对照）：左乌云红字 ✗，右白云蓝字 ✓。
    第 0 拍标题；第 2 拍乌云；第 3 拍红字，随后 ✗；第 5 拍白云，随后 ✓；第 6 拍蓝字（第 8 拍前写完）。"""
    lx, rx, w, h = X - 310, X + 310, 540, 300
    T(title, X, cy - 430, 64, k0=0, sfx="pop")
    L(dark(lx, cy + 20, w, h), 2, 2.8, BLACK, 6, sfx="wood_high")
    T(bad, lx, cy + 20, size, RED, k0=3, sfx="pop")
    kb = 3 + max(0.8, 0.25 * len(bad))
    L(cross(lx, cy - 250, 36), kb, kb + 0.4, RED, 11)
    L(cloud(rx, cy + 20, w, h), 5, 5.7, BLUE, 7, sfx="wood_high")
    L(check(rx, cy - 250, 40), 5.7, 6.0, BLUE, 11)
    T(good, rx, cy + 20, size, BLUE, k0=6, sfx="pop")


# ---------------------------------------------------------------- 开局（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("心里难受", "灵魂拷问", (X, 800, 0.85), bars=2, shake=[0])
T("我觉得很糟", X, 530, 96, RED, k0=0, sfx="kick")
T("所以事情很糟", X, 690, 96, RED, k0=2, sfx="pop")
L(dark(X, 610, 900, 400, tail=(X, 960)), 4, 4.9, BLACK, 7, sfx="wood_high")
L(zhou(X, 1270, 0.8), 5, 5.8, BLACK, 9, sfx="pop")
L(face(X, 1270, 0.8, "sad"), 5.8, 6.0, BLACK, 8)

ROWS = ["⑥放大缩小", "⑦情绪推理", "⑧应该句式", "⑨乱贴标签", "⑩罪责归己"]
FIXES = ["改一处就好", "只是感觉", "做完会更好", "这次迟到了", "分开算"]
RY = [2075 + 150 * i for i in range(5)]
CL, CR = TX - 275, TX + 300            # 左栏（红：套路名）、右栏（蓝：换个看法）中心

scene("再来五种", "接上一讲", (TX, 2250, 0.75))
card = [rect(1790, 1745, 360, 190, 18)]
for i in range(5):
    card += [rect(1650 + 70 * i, 1790, 46, 46, 6), check(1650 + 70 * i, 1790, 18)]
L(join(*card), 0, 0.8, BLACK, 6, sfx="wood_low")
T("上一讲", 1790, 1700, 52, k0=1, sfx="pop")
grid = [rect(TX, 2325, 1150, 850, 16), P((TX + 25, 1900), (TX + 25, 2750))]
grid += [P((TX - 575, 2000 + 150 * i), (TX + 575, 2000 + 150 * i)) for i in range(5)]
L(join(*grid), 2, 2.6, BLACK, 7, sfx="wood_high")
L(cross(CL, 1950, 30), 2.6, 2.8, RED, 10)
L(check(CR, 1950, 34), 2.8, 3.0, BLUE, 10)
for i, s in enumerate(ROWS):
    T(s, CL, RY[i], 58, RED, k0=3 + i, k1=4 + i, sfx="pop")

# ---------------------------------------------------------------- ⑥ 放大和缩小（场景 3–5）

CY = 3700
scene("我的小错，他的大功", "⑥ 放大缩小", (X, CY, 0.85))
T("⑥ 放大缩小", X, CY - 470, 64, k0=0, sfx="pop")
L(zhou(1650, CY + 400, 0.75, "hold"), 2, 2.8, BLACK, 9, sfx="wood_high")
L(face(1650, CY + 400, 0.75, "sad"), 2.8, 3.0, BLACK, 8)
L(doc(1810, CY + 120, 150, 190), 3, 3.6, BLACK, 8, sfx="pop")
L(circle(1830, CY + 100, 24), 3.6, 3.9, RED, 8)
T("我的小错", 1720, CY - 250, 62, RED, k0=4, k1=5, sfx="rim")
L(zhou(2300, CY + 400, 0.75, "hold"), 5, 5.8, BLUE, 9, sfx="wood_high")
L(face(2300, CY + 400, 0.75, "smile"), 5.8, 6.0, BLUE, 8)
L(join(doc(2460, CY + 120, 150, 190), star(2460, CY + 40, 34)), 6, 6.8, BLUE, 8, sfx="pop")
T("他的大功", 2330, CY - 250, 62, BLUE, k0=7, k1=8, sfx="ding")
park(8.0, (2390, CY - 250), (2560, CY + 470))

CY = 4950
R1, R2 = CY - 260, CY + 280
scene("两头看不一样", "⑥ 放大缩小 · 望远镜", (X, CY, 0.85), shake=[0], flashes=[0])
T("错", 2370, R1 + 10, 300, RED, k0=0, k1=0.8, sfx="kick")
L(join(eye(1480, R1), scope(1560, 2000, R1, 28, 78), P((2000, R1 - 78), (2190, R1 - 160)),
       P((2000, R1 + 78), (2190, R1 + 160))), 1, 1.9, BLACK, 8, sfx="wood_high")
T("看错处：放大", 1760, R1 - 175, 56, RED, k0=2, sfx="pop")
L(join(eye(1480, R2), scope(1560, 2000, R2, 78, 28), P((2000, R2 - 28), (2110, R2 - 10)),
       P((2000, R2 + 28), (2110, R2 + 10))), 4, 4.9, BLACK, 8, sfx="wood_high")
T("优点", 2170, R2, 46, BLUE, k0=5, sfx="pop")
T("看长处：缩小", 1760, R2 - 175, 56, BLUE, k0=6, sfx="pop")

CY = 6200
scene("改一处就好", "⑥ 放大缩小 · 对照", (X, CY, 0.85))
pair(CY, "⑥ 放大缩小", "这错要命了", "改一处就好")

# ---------------------------------------------------------------- ⑦ 情绪化推理（场景 6）

CY = 7450
scene("感觉当不了证据", "⑦ 情绪推理", (X, CY, 0.85))
pair(CY, "⑦ 情绪推理", "我觉得我很笨", "感觉不等于事实", size=62)

# ---------------------------------------------------------------- ⑧ 应该句式（场景 7–8）

CY = 8700
scene("「应该」勒住了你", "⑧ 应该句式", (X, CY, 0.85))
T("⑧ 应该句式", X, CY - 430, 64, k0=0, sfx="pop")
L(zhou(1600, CY + 400, 0.8), 2, 2.8, BLACK, 9, sfx="wood_high")
L(face(1600, CY + 400, 0.8, "sad"), 2.8, 3.0, BLACK, 8)
rope = skia.Path()
for dy in (250, 300):
    rope.addOval(skia.Rect.MakeXYWH(1600 - 85, CY + dy - 22, 170, 44))
rope.moveTo(1685, CY + 280)
rope.quadTo(1980, CY + 300, 2350, CY + 190)
L(join(rope, P((2350, CY + 160), (2350, CY + 400)), P((2280, CY + 400), (2420, CY + 400))), 3, 3.9, ORANGE, 9,
  sfx="wood_low")
T("应该", 2050, CY + 180, 64, RED, k0=4, sfx="pop")
L(dark(1900, CY - 170, 720, 270, tail=(1640, CY + 90)), 5, 5.8, BLACK, 6, sfx="wood_high")
T("我应该早就升职了", 1900, CY - 170, 58, RED, k0=6, k1=8, sfx="pop")

CY = 9950
scene("必须换成会更好", "⑧ 应该句式 · 对照", (X, CY, 0.85))
pair(CY, "⑧ 应该句式", "我必须做完", "做完会更好")

# ---------------------------------------------------------------- ⑨ 乱贴标签（场景 9）

CY = 11200
SX = 1660
scene("说那件事就行", "⑨ 乱贴标签", (X, CY, 0.85))
T("⑨ 乱贴标签", X, CY - 430, 64, k0=0, sfx="pop")
L(zhou(SX, CY + 420, 1.0, badge=False), 2, 2.8, BLACK, 10, sfx="wood_high")
L(face(SX, CY + 420, 1.0, "sad"), 2.8, 3.0, BLACK, 8)
b.custom(J(), 3, 3.1, fill_fn(SX, CY + 270, 230, 100))
L(join(rect(SX, CY + 270, 230, 100, 10), P((SX - 95, CY + 220), (SX, CY + 178), (SX + 95, CY + 220))), 3, 3.6,
  BLACK, 7, sfx="wood_low")
T("废物", SX, CY + 272, 64, RED, k0=4, sfx="pop")
L(cross(SX, CY + 270, 80), 5, 5.4, RED, 12, sfx="rim")
L(cloud(2290, CY + 20, 520, 270), 5.4, 6.0, BLUE, 7)
L(check(2290, CY - 200, 40), 7.3, 7.7, BLUE, 11)
T("这次迟到了", 2290, CY + 20, 64, BLUE, k0=6, sfx="pop")

# ---------------------------------------------------------------- ⑩ 罪责归己（场景 10）

CY = 12450
SX = 1600
scene("账别全算自己头上", "⑩ 罪责归己", (X, CY, 0.85))
T("⑩ 罪责归己", X, CY - 430, 64, k0=0, sfx="pop")
L(zhou(SX, CY + 420, 0.75), 2, 2.8, BLACK, 9, sfx="wood_high")
L(face(SX, CY + 420, 0.75, "sad"), 2.8, 3.0, BLACK, 8)
L(join(arrow((1400, CY - 60), (1530, CY + 130), 0.1, 34), arrow((1800, CY - 60), (1670, CY + 130), -0.1, 34),
       arrow((1380, CY + 330), (1510, CY + 290), 0.1, 30), arrow((1820, CY + 330), (1690, CY + 290), -0.1, 30)),
  3, 3.9, RED, 8, sfx="rim")
T("都怪我", SX, CY - 170, 64, RED, k0=4, sfx="pop")
O = (1960, CY + 150)
L(join(arrow(O, (2180, CY - 50), 0.08, 30), arrow(O, (2200, CY + 150), 0, 30), arrow(O, (2180, CY + 350), -0.08, 30)),
  5, 5.6, BLUE, 8, sfx="wood_high")
for n, w in enumerate(("预算", "时间", "客户")):
    T(w, 2310, CY - 50 + 200 * n, 60, BLUE, k0=5.6 + 0.8 * n, k1=6.4 + 0.8 * n)
park(8.0, (2370, CY + 350), (2450, CY + 520))

# ---------------------------------------------------------------- 收拢（场景 11–13）

scene("五对放一起", "回到表格", (TX, 2250, 0.75))
for i, (s, k0) in enumerate(zip(FIXES, (0, 2, 3, 5, 7))):
    T(s, CR, RY[i], 58, BLUE, k0=k0, sfx="pop")
park(7.85, (2560, RY[4]), (2900, 2820))

GX = [270 + 240 * i for i in range(5)]
scene("十种全齐了", "十种想歪", (750, 2250, 0.85))
L(join(*[cloud(x, 1960, 200, 130) for x in GX]), 0, 0.9, BLACK, 6, sfx="wood_high")
T("上一讲", 750, 1810, 56, k0=1, sfx="pop")
T("①　　　②　　　③　　　④　　　⑤", 750, 1962, 60, k0=2, k1=3, sfx="pop")
L(join(*[cloud(x, 2290, 200, 130) for x in GX]), 3, 3.9, RED, 6, sfx="wood_high")
T("这一讲", 750, 2140, 56, RED, k0=4, sfx="pop")
T("⑥　　　⑦　　　⑧　　　⑨　　　⑩", 750, 2292, 60, RED, k0=5, k1=6, sfx="pop")
T("一共十种", 750, 2560, 110, k0=6, k1=7, sfx="kick")

scene("认出来就松了", "做法 · 起外号", (750, 3500, 0.85))
T("给它起个外号", 750, 3060, 64, BLUE, k0=0, sfx="pop")
L(zhou(420, 3880, 0.8), 2, 2.8, BLACK, 9, sfx="wood_high")
L(dark(830, 3330, 640, 240, tail=(470, 3600)), 3, 3.7, BLACK, 6, sfx="wood_low")
T("我必须做完", 830, 3330, 60, RED, k0=4, sfx="pop")
L(join(tag(900, 3700, 500, 110), P((650, 3700), (700, 3450))), 5.3, 5.9, BLUE, 7)
T("又来了，应该", 930, 3702, 58, BLUE, k0=6, k1=7.5, sfx="pop")
L(face(420, 3880, 0.8, "smile"), 7.5, 7.9, BLACK, 8)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看十格清单，再推到评论区

FAR = (1500, 2250, 0.4)
END = (700, 4750, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, END)
H(0, "cymbal", 0.5)
H(2, "ding")
L(cloud(930, 5010, 600, 190), 5, 5.6, BLUE, 7, sfx="wood_low")
T("今天换掉一朵乌云", 930, 5012, 54, BLUE, k0=5.6, k1=7.6)
T("你最常用哪句应该？", 700, 4470, 76, RED, k0=8, sfx="pop")
T("下一讲：脑子里骂自己，怎么回嘴？", 700, 4640, 46, k0=11, k1=15, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "trap2", "再五种想歪", "心里难受，就说明事情糟？", ACC, b.shots,
                 [f"{BOOK}，第 3 章“破解情绪：思维决定情绪”（十种认知扭曲的后五种，转述）",
                  "中译本：中国城市出版社 2011（豆瓣 subject/5980113）"],
                 "心里难受|就说明事情【糟】", SQUARE_SHOT,
                 ["书中观点均为转述：心情很差时，脑子里的想法常常带着明显的扭曲，人却把它当成事实；第 3 章列出十种认知扭曲，"
                  "本讲讲后五种——放大和缩小（magnification / minimization）、情绪化推理（emotional reasoning，感觉不等于事实）、"
                  "应该句式（should statements）、乱贴标签（labeling and mislabeling）、罪责归己（personalization）。"
                  "中文叫法为通行译法的口语说法，李亚萍译本的原用词未逐字核实；上屏均为转述，不是逐字引文。",
                  "望远镜（看错处正着看、看长处倒着看）为对书中“放大和缩小”的画面比喻，书中是否用“望远镜”说法未核实。",
                  "报告错一个字、同事做成项目、想早点升职、迟到一次、团队没谈成单子（预算、时间、客户）均为现实场景示意，"
                  "不指向任何具体公司或个人；每一对“换个看法”为据书中思路整理的示意说法。",
                  "“给常犯的那种起个外号，冒出来就叫它名字”为据书中思路整理的做法。",
                  "本片为读书分享，不能替代诊断和治疗；情绪持续低落或有轻生念头，请尽快联系医生、心理咨询师或当地心理援助热线。"],
                 tags="#认知扭曲")
    return b.attach(ep)
