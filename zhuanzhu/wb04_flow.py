"""04 沉进去才痛快（白板手绘版）：刷了一晚手机，怎么更累了？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 zhuanzhu/build.py）。
叙事（形式 F 两人对比，开局“两个人并排”）：白板中线一分为二，左边小周、右边阿杰，同一个周五晚上同步推进——
小周躺沙发刷手机，被一串小红点越堆越高；阿杰蹲下修那辆没修完的自行车，手机扣着静音 →
drop：右栏除了车和人全被擦掉，钟面指针飞转三圈 → 十二点两人的脸：一个更累，一个真痛快 →
亮书 → 书中观点（注意力放在哪，日子就是什么样；投入有点难的事时人最满足；工作时反而更常进入这种状态；
手艺人把一件活做好本身就有意义）→ 做法（周末留一件要动手的事；上班先挑一件难活）→ 拉回两栏看两种周五 → 评论区。
书中观点为转述（卡尔·纽波特《深度工作》第一部分第3章，宋伟译）；两人周五、修自行车、难度—本事带子、上班/休闲火苗图
为示意；做法为据书中思路整理。
"""

import math

import skia

from adler import kit as K
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, check, circle, clock, ease_out,
                               hands_at, join, marker, podium_list, rect, stick, underline)

from .common import BOOK, episode

ACC = "#6C4FB0"
SQUARE_SHOT = 4                 # 场景 5：两栏全景，小周“更累”、阿杰“真痛快”

b = Board(size=(3600, 8300))
LX, RX, MID = 1250, 2350, 1800  # 上方两栏：左小周、右阿杰
HEAD_Y = 630                    # 两人半身像的头部中心


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def bust(x, y, badge=False, stripes=False) -> skia.Path:
    """半身像：头 + 肩 + 两只眼；badge 为小周的工牌，stripes 为阿杰的条纹衫。(x, y) 为头部中心。"""
    sh = skia.Path()
    sh.moveTo(x - 140, y + 200)
    sh.quadTo(x - 125, y + 95, x, y + 90)
    sh.quadTo(x + 125, y + 95, x + 140, y + 200)
    parts = [circle(x, y, 70), sh, P((x, y + 70), (x, y + 90)), circle(x - 24, y - 10, 5), circle(x + 24, y - 10, 5)]
    if badge:
        parts += [P((x - 32, y + 92), (x, y + 140), (x + 32, y + 92)), rect(x, y + 160, 40, 46, 6)]
    if stripes:
        parts += [P((x - 95, y + 135), (x + 95, y + 135)), P((x - 110, y + 168), (x + 110, y + 168))]
    return join(*parts)


def sofa(x, y, w=700) -> skia.Path:
    """沙发：(x, y) 为地面中点。"""
    l, r = x - w / 2, x + w / 2
    return join(P((l + 70, y - 150), (l + 70, y - 300), (r - 70, y - 300), (r - 70, y - 150)),
                rect(x, y - 105, w - 140, 90, 14), rect(l + 35, y - 120, 70, 200, 20), rect(r - 35, y - 120, 70, 200, 20),
                P((l + 40, y - 20), (l + 40, y + 30)), P((r - 40, y - 20), (r - 40, y + 30)))


def lying(x, y) -> skia.Path:
    """躺着举手机的小人：(x, y) 为头部中心，身体向右平躺。"""
    return join(circle(x, y, 42), P((x + 42, y + 12), (x + 260, y + 28)),
                P((x + 445, y + 2), (x + 260, y + 28), (x + 445, y + 52)),
                P((x + 80, y + 18), (x + 115, y - 55), (x + 85, y - 115)),
                circle(x - 12, y - 14, 4), circle(x + 14, y - 16, 4))


def phone(x, y, w=64, h=108) -> skia.Path:
    return join(rect(x, y, w, h, 12), P((x - 12, y + h / 2 - 14), (x + 12, y + h / 2 - 14)))


def glow(x, y, r=70) -> skia.Path:
    return join(*[P((x + math.cos(a) * r, y + math.sin(a) * r), (x + math.cos(a) * (r + 40), y + math.sin(a) * (r + 40)))
                  for a in (math.radians(d) for d in (-150, -110, -70, -30))])


def bike(x, y, s=1.0) -> skia.Path:
    """自行车（侧视）：(x, y) 为地面中点。"""
    rw, fw, hy = (x - 190 * s, y - 110 * s), (x + 190 * s, y - 110 * s), y - 110 * s
    crank, seat, head = (x - 20 * s, hy), (x - 70 * s, y - 280 * s), (x + 130 * s, y - 290 * s)
    return join(circle(*rw, 105 * s), circle(*fw, 105 * s), P(rw, crank, seat, close=True), P(crank, head, fw),
                P(seat, head), P((x - 115 * s, y - 300 * s), (x - 25 * s, y - 300 * s)), P(seat, (x - 70 * s, y - 300 * s)),
                P(head, (x + 112 * s, y - 350 * s), (x + 172 * s, y - 362 * s)), circle(*crank, 22 * s))


def squat(x, y) -> skia.Path:
    """蹲着干活的阿杰（条纹衫，面朝右）：(x, y) 为脚底。"""
    hip, neck, sh = (x - 40, y - 100), (x + 10, y - 230), (x + 2, y - 205)
    parts = [circle(x + 32, y - 275, 45), P(hip, neck), P(hip, (x + 45, y - 150), (x + 35, y)),
             P(hip, (x + 5, y - 125), (x - 15, y)), P(sh, (x + 80, y - 165), (x + 150, y - 150)),
             circle(x + 48, y - 283, 4), circle(x + 66, y - 283, 4)]
    dx, dy = 50, -130
    n = math.hypot(dx, dy)
    px, py = -dy / n * 26, dx / n * 26
    for t in (0.35, 0.6, 0.82):
        cx, cy = hip[0] + dx * t, hip[1] + dy * t
        parts.append(P((cx - px, cy - py), (cx + px, cy + py)))
    return join(*parts)


def wrench(x, y, s=1.0) -> skia.Path:
    head = skia.Path()
    head.addArc(skia.Rect.MakeXYWH(x + 40 * s, y - 62 * s, 48 * s, 48 * s), 60, 270)
    return join(P((x - 40 * s, y + 26 * s), (x + 48 * s, y - 28 * s)), head)


def tools(x, y) -> skia.Path:
    """地上摊开的工具：螺丝刀 + 几颗螺丝。"""
    return join(rect(x - 110, y, 70, 30, 10), P((x - 75, y), (x + 20, y)), circle(x + 90, y, 12), circle(x + 135, y + 8, 12),
                circle(x + 175, y - 4, 12))


def oval(x, y, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    return p


def eyebags(x, y) -> skia.Path:
    """熬夜脸：眼下黑眼圈 + 下撇的嘴。(x, y) 为半身像头部中心。"""
    parts = []
    for ex in (x - 24, x + 24):
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(ex - 16, y - 12, 32, 22), 20, 140)
        parts.append(p)
    m = skia.Path()
    m.addArc(skia.Rect.MakeXYWH(x - 22, y + 28, 44, 26), 200, 140)
    return join(*parts, m)


def grin(x, y) -> skia.Path:
    m = skia.Path()
    m.addArc(skia.Rect.MakeXYWH(x - 34, y + 2, 68, 44), 10, 160)
    return join(m, P((x - 33, y + 22), (x + 33, y + 22)))


def drop(x, y, s=1.0) -> skia.Path:
    """汗珠。"""
    p = skia.Path()
    p.moveTo(x, y - 26 * s)
    p.quadTo(x + 18 * s, y, x, y + 12 * s)
    p.quadTo(x - 18 * s, y, x, y - 26 * s)
    return p


def lens(x, y, r=160) -> skia.Path:
    """放大镜：(x, y) 为镜片中心，手柄朝右下。"""
    a = r * 0.72
    return join(circle(x, y, r), circle(x, y, r - 14), P((x + a, y + a), (x + a + 120, y + a + 120)),
                P((x + a + 14, y + a - 6), (x + a + 128, y + a + 104)))


def flame(x, y, s=1.0) -> skia.Path:
    """小火苗：(x, y) 为火苗底部中点。"""
    fl = skia.Path()
    fl.moveTo(x, y - 170 * s)
    fl.quadTo(x + 85 * s, y - 70 * s, x + 35 * s, y)
    fl.lineTo(x - 35 * s, y)
    fl.quadTo(x - 85 * s, y - 70 * s, x, y - 170 * s)
    inner = skia.Path()
    inner.moveTo(x, y - 90 * s)
    inner.quadTo(x + 35 * s, y - 40 * s, x, y - 5 * s)
    inner.quadTo(x - 35 * s, y - 40 * s, x, y - 90 * s)
    return join(fl, inner)


def stool(x, y) -> skia.Path:
    """做好的木凳：(x, y) 为地面中点。"""
    return join(rect(x, y - 190, 360, 40, 8), P((x - 140, y - 170), (x - 165, y)), P((x + 140, y - 170), (x + 165, y)),
                P((x - 152, y - 80), (x + 152, y - 80)))


def hammer(x, y) -> skia.Path:
    """锤子：(x, y) 为手柄末端（握手处）。"""
    return join(P((x, y), (x + 40, y - 160)), rect(x + 44, y - 178, 110, 44, 8))


def sparkle(x, y, r=40) -> skia.Path:
    return join(P((x - r, y), (x + r, y)), P((x, y - r), (x, y + r)))


def reddot_fn(x, y, r, num):
    """系列角色小红点：红色实心圆 + 白色数字 + 两条小短腿，从小弹到大。"""

    def fn(c, k, t):
        s = ease_out(k)
        if s <= 0:
            return None
        rr = r * (s + 0.15 * math.sin(math.pi * k))
        for d in (-1, 1):
            c.drawPath(P((x + d * rr * 0.35, y + rr * 0.85), (x + d * rr * 0.45, y + rr * 1.45),
                         (x + d * rr * 0.7, y + rr * 1.45)), marker(RED, max(4.0, r * 0.12)))
        K.dot(c, x, y, rr, RED)
        size = rr * (1.05 if len(num) == 1 else 0.78 if len(num) == 2 else 0.6)
        K.text(c, num, x, y, size, "black", "#FFFFFF")
        return None

    return fn


CLK = (2250, 1500, 140)         # 阿杰头顶的钟


def spin_fn(c, k, t):
    """钟面指针飞转三圈：分针转三圈，时针从 9 点走到 12 点。"""
    x, y, r = CLK
    e = 1 - (1 - k) ** 1.6
    minute = 180 * e
    trail = skia.Path()
    a1 = -math.pi / 2 + minute / 60 * 2 * math.pi
    for i in range(14):
        a = a1 - i * 0.12
        pt = (x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72)
        trail.moveTo(*pt) if i == 0 else trail.lineTo(*pt)
    if k < 1:
        c.drawPath(trail, K.paint(BLUE, 0.35, 10))
    c.drawPath(hands_at(x, y, r, 9 + 3 * e, minute % 60), marker(BLACK, 10))
    K.dot(c, x, y, 10, BLACK)
    return None


# ---------------------------------------------------------------- 开局：两个人并排（场景 1–5，上方两栏）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("同一个周五", "两个人的周五", (MID, 1000, 0.55), bars=2)
T("周五晚上", MID, 1030, 80, k0=0, k1=1, sfx="pop")
L(P((MID, 1290), (MID, 2380)), 1, 1.8, BLACK, 7, sfx="wood_low")
L(bust(LX, HEAD_Y, badge=True), 2, 2.8, BLACK, 9, sfx="pop")
T("小周", LX, 880, 72, BLUE, k0=2.8, k1=3.6)
L(bust(RX, HEAD_Y, stripes=True), 4, 4.8, BLACK, 9, sfx="pop")
T("阿杰", RX, 880, 72, GREEN, k0=4.8, k1=5.6)
H(5, "wood_high", 0.6, "两人就位")

scene("躺着刷", "左边 · 小周", (LX, 1850, 0.85))
L(sofa(1150, 2250), 0, 0.9, BLACK, 9, sfx="wood_low")
L(lying(915, 2045), 1, 1.9, BLACK, 9, sfx="wood_high")
L(join(phone(985, 1880), glow(985, 1880)), 2, 2.8, BLUE, 8, sfx="pop")
for n, (x, y, r, num) in enumerate(((1120, 1745, 45, "1"), (1300, 1595, 58, "9"), (1480, 1445, 74, "99+"))):
    b.custom(J(), 3 + n, 3.5 + n, reddot_fn(x, y, r, num), sfx="ding")
L(join(rect(800, 1680, 300, 130, 40), P((740, 1745), (760, 1810), (800, 1745))), 6, 6.8, BLACK, 8, sfx="pop")
T("再刷一个", 800, 1680, 56, k0=6.8, k1=7.8)

scene("修车去了", "右边 · 阿杰", (RX, 1850, 0.85))
L(join(bike(2480, 2250, 0.95), P((1900, 2252), (2950, 2252))), 0, 1.0, BLACK, 9, sfx="wood_low")
L(squat(2080, 2250), 1, 1.9, GREEN, 9, sfx="wood_high")
L(wrench(2240, 2110), 2, 2.7, BLACK, 8, sfx="pop")
L(tools(2700, 2330), 3, 3.8, BLACK, 8, sfx="wood_high")
T("没修完的车", 2450, 1450, 64, k0=4, sfx="pop")
L(join(rect(2860, 1700, 150, 80, 12), circle(2905, 1700, 8)), 6, 6.8, BLACK, 9, sfx="wood_low")
T("静音", 2860, 1810, 56, BLUE, k0=7, k1=7.8, sfx="pop")

scene("时间飞了", "右边 · 阿杰沉进去了", (RX, 1850, 0.85), shake=[0], flashes=[0])
H(0, "kick", 0.9, "drop：擦掉车以外的一切")
b.erase(J(), 0, 0.7, 2450, 1450, 400, 120)
b.erase(J(), 0.7, 1.4, 2860, 1755, 280, 230)
L(oval(2290, 2070, 470, 270), 2, 2.9, BLUE, 8, sfx="ding")
L(clock(*CLK), 3, 3.8, BLACK, 9, sfx="wood_high")
b.custom(J(), 4, 7, spin_fn, sfx="shaker")
H(5, "tom", 0.7, "指针第二圈")
H(6, "tom", 0.8, "指针第三圈")
T("时间飞了", 2720, 1500, 84, RED, k0=7, k1=8, sfx="pop")

scene("一个累一个爽", "两个人 · 十二点", (MID, 1450, 0.5))
T("00:00", MID, 1170, 84, RED, k0=0, k1=1.25, sfx="pop")
L(eyebags(LX, HEAD_Y), 2, 2.8, BLACK, 7, sfx="wood_high")
T("更累", LX + 240, HEAD_Y, 84, BLUE, k0=3, k1=3.8, sfx="pop")
L(grin(RX, HEAD_Y), 4, 4.8, BLACK, 7, sfx="wood_high")
L(join(drop(RX + 92, HEAD_Y - 46), drop(RX - 96, HEAD_Y - 30, 0.8)), 5, 5.6, BLUE, 6, sfx="pop")
T("真痛快", RX + 270, HEAD_Y, 84, GREEN, k0=6, k1=6.8, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 6–10，下方格子：左列往下，再从右列往上）

scene("书里讲过", "深度工作 · 书中观点", (900, 3300, 0.85))
L(book(750, 3300, 420, 280), 0, 0.9, BLACK, 9, sfx="wood_low")
T("《深度工作》", 750, 3020, 64, GREEN, k0=1, sfx="pop")
L(stick(1250, 3500, 0.7), 3, 3.8, BLACK, 9, sfx="wood_high")
L(rect(1250, 3590, 320, 80, 14), 4, 4.6, BLACK, 7, sfx="pop")
T("卡尔·纽波特", 1250, 3590, 50, k0=4.6)
T("第三章", 750, 3530, 56, k0=7, k1=7.8, sfx="pop")

scene("盯着啥，过成啥", "书中观点 · 注意力", (900, 4700, 0.85))
L(lens(600, 4600), 0, 0.9, BLACK, 9, sfx="wood_high")
for n, (x, y, r, num) in enumerate(((545, 4560, 36, "99+"), (680, 4570, 30, "9"), (610, 4680, 26, "1"))):
    b.custom(J(), 1 + n * 0.25, 1.5 + n * 0.25, reddot_fn(x, y, r, num), sfx="ding" if n == 0 else None)
T("全是红点", 560, 5000, 56, RED, k0=2, k1=3, sfx="pop")
L(lens(1200, 4600), 3, 3.9, BLACK, 9, sfx="wood_high")
L(bike(1200, 4690, 0.4), 4, 4.8, GREEN, 6, sfx="pop")
T("全是车", 1160, 5000, 56, GREEN, k0=5, k1=5.8, sfx="pop")
T("盯着啥，过成啥", 900, 4290, 80, k0=6, k1=7.75, sfx="ding")

AX = (420, 6500)                # 难度—本事图的原点
scene("有点难最上头", "书中观点 · 投入难事", (900, 6100, 0.85))
L(P((AX[0], 5720), AX, (1450, AX[1])), 0, 0.9, BLACK, 9, sfx="wood_low")
T("难度", AX[0], 5660, 56, k0=1, k1=1.8, sfx="pop")
T("本事", 1440, 6570, 56, k0=2, k1=2.8, sfx="pop")
L(join(P((480, 6380), (1300, 5720)), P((600, 6460), (1420, 5800))), 3, 3.9, BLUE, 9, sfx="wood_high")
L(stick(960, 6118, 0.36, "up"), 4, 4.8, GREEN, 7, sfx="pop")
T("太难", 650, 5900, 60, RED, k0=5, k1=5.8, sfx="pop")
T("太容易", 1200, 6380, 60, k0=6, k1=6.8, sfx="pop")
T("刚好", 1430, 5700, 56, GREEN, k0=7, k1=7.8, sfx="ding")

scene("上班也能爽", "书中观点 · 上班和休闲", (900, 7500, 0.85))
L(rect(620, 7560, 460, 400, 20), 0, 0.9, BLACK, 9, sfx="wood_low")
T("上班", 620, 7300, 64, k0=1, k1=1.8, sfx="pop")
L(rect(1180, 7560, 460, 400, 20), 2, 2.9, BLACK, 9, sfx="wood_low")
T("休闲", 1180, 7300, 64, k0=3, k1=3.8, sfx="pop")
L(join(flame(520, 7680, 0.55), flame(620, 7620, 0.7), flame(720, 7680, 0.55)), 4, 4.9, ORANGE, 8, sfx="ding")
L(join(phone(1110, 7600, 70, 120), flame(1270, 7680, 0.4)), 5, 5.8, ORANGE, 8, sfx="pop")
T("更容易沉进去", 900, 7900, 64, RED, k0=6, sfx="pop")

scene("把活做好", "书中观点 · 手艺人", (2700, 7500, 0.85))
L(stool(2860, 7800), 0, 0.9, BLACK, 9, sfx="wood_low")
L(stick(2350, 7800, 0.75, "hold"), 1, 1.8, BLACK, 9, sfx="wood_high")
L(hammer(2432, 7650), 2, 2.7, BLACK, 9, sfx="pop")
L(join(sparkle(2640, 7480), sparkle(3080, 7470, 32), sparkle(3110, 7700, 26)), 3, 3.6, ORANGE, 7, sfx="pop")
T("一件活，做到好", 2700, 7150, 72, k0=4, sfx="pop")
L(check(3170, 7330, 50), 6, 6.6, GREEN, 11, sfx="ding")
T("有意义", 2860, 7900, 64, GREEN, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- 做法（场景 11–12，右列往上）

scene("留件动手的事", "做法一 · 周末", (2700, 6100, 0.85))
L(join(stick(2330, 6450, 0.75, "point"), rect(2330, 6345, 28, 36, 5)), 0, 0.8, BLUE, 9, sfx="wood_high")
L(join(rect(2880, 6150, 540, 640, 20), rect(2880, 5830, 160, 50, 10)), 1, 1.8, BLACK, 9, sfx="wood_low")
T("周末留一件", 2880, 5945, 60, RED, k0=1.8)
for n, s in enumerate(("拼模型", "做顿饭", "修个东西")):
    y = 6075 + n * 140
    L(rect(2690, y, 50, 50, 6), 3 + n, 3.2 + n, BLACK, 7, sfx="pop")
    T(s, 2910, y, 60, k0=3.2 + n)
L(check(2695, 6075, 34), 7, 7.6, GREEN, 10, sfx="ding")

scene("难活放前面", "做法二 · 上班", (2700, 4700, 0.85))
L(podium_list(2550, 4480, n=3, w=440, h=100), 0, 0.9, BLACK, 8, sfx="wood_low")
for n, (s, col) in enumerate((("回消息", BLACK), ("填表格", BLACK), ("写方案", RED))):
    T(s, 2550, 4480 + n * 116, 56, col, k0=1 + n, k1=1.8 + n, sfx="pop")
L(arrow((2800, 4712), (2800, 4330), -0.45, 40), 4, 4.8, RED, 8, sfx="wood_high")
L(rect(2550, 4320, 440, 100, 10), 5, 5.8, RED, 10, sfx="pop")
T("写方案 · 难", 2550, 4320, 56, RED, k0=5.8, k1=6.8)
T("先干它", 3070, 4320, 64, RED, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 收束（场景 13：回到上方两栏）

scene("两种周五", "两个人的周五", (MID, 1560, 0.47))
L(underline(880, 1650, 2410), 0, 0.9, BLUE, 9, sfx="wood_low")
T("刷了一晚", LX, 2510, 88, BLUE, k0=1, k1=2, sfx="pop")
L(underline(1950, 2720, 2410), 3, 3.9, GREEN, 9, sfx="wood_low")
T("修了一晚", RX, 2510, 88, GREEN, k0=4, k1=5, sfx="pop")
L(oval(LX + 240, HEAD_Y, 120, 80), 6, 6.8, BLUE, 8, sfx="rim")
L(oval(RX + 270, HEAD_Y, 160, 80), 7, 7.8, GREEN, 8, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FULL = (1800, 4150, 0.18)
COMMENT = (2700, 3400, 0.85)
scene("评论区聊聊", "评论区见", FULL, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(rect(2700, 3330, 1000, 300, 40), 5, 5.8, RED, 8, sfx="pop")
T("上次干活忘了时间", 2700, 3270, 76, RED, k0=6, k1=8, sfx="pop")
T("是啥时候？", 2700, 3390, 76, RED, k0=8, k1=9.25)
b.custom(J(), 9, 9.5, reddot_fn(3150, 3080, 50, "?"), sfx="ding")
T("下一讲：没有整块时间，还能专注吗？", 2700, 3620, 50, k0=10, k1=14.25, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "flow", "沉进去才痛快", "刷了一晚手机，怎么更累了？", ACC, b.shots,
                 [f"{BOOK}第一部分 第3章“深度工作是有意义的”（转述）",
                  "中译本：《深度工作：如何有效使用每一点脑力》，宋伟译，江西人民出版社 · 后浪 2017"],
                 "刷了一晚手机|怎么【更累了】", SQUARE_SHOT,
                 ["书中观点均为转述（第一部分第3章“深度工作是有意义的”）：作者引作家威妮弗雷德·加拉格尔的经历与著作 Rapt，"
                  "说明你把注意力放在哪里，你的日子就过成什么样（加拉格尔的患病经历只写在这里，不上屏）；"
                  "引心理学家米哈里·契克森米哈赖的心流研究，人在投入一件有挑战、需要全力去够的事时最满足；"
                  "书中提到他的经验抽样研究发现，人在工作时比在休闲时更容易进入这种状态（上屏只画“上班格火苗更多”，"
                  "不写数字；具体表述待对照中译本核实）；另引哲学家德雷福斯与凯利讲手艺人，认真把一样活做好本身就有意义。"
                  "上屏均为转述，不是逐字引文；书中章节名不上屏。",
                  "小周与阿杰的同一个周五（刷手机 / 修自行车）、小红点 1 → 9 → 99+、钟面三圈、“00:00”、"
                  "放大镜、“难度—本事”带子（“太难 / 太容易 / 刚好”）、上班与休闲的火苗格、木凳与锤子均为示意，不是数据，"
                  "不指向任何具体公司或个人；书里人物只写名字，作者以火柴人 + 名牌表示，不画肖像。",
                  "两条做法（周末留一件要动手的事：拼模型 / 做顿饭 / 修个东西；上班先挑一件难活先干）为据书中思路整理的建议。"],
                 tags="#心流")
    return b.attach(ep)
