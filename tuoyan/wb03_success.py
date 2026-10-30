"""03 怕做好（白板手绘版）：做得太好，怕以后都得这么好。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 G 倒叙）：开局先给结局——晋升名单出来，小周的位置是个问号 →
“倒带”：一条往左走的时间线，出名单 ← 前一晚凑了个凑合版 ← 三周前 →
亮书（《拖延心理学》，博克和袁；书里专门有一章讲怕成功）→
drop：奖杯后面“轰”地冒出一串越来越高的台阶，影子压到小周身上，明天怪兽蹲在最高一级 →
书中观点三站（活一摞摞叠高 / 隔板后冒出几双眼睛 / 小周一级级往上走，跟老同事之间的线越拉越长）→
拖着刚好卡在楼梯中间，怪兽当靠垫 → 拉远看全板：三条绿箭头连回开头那张名单，倒带看完 →
做法（写下“做好了会怎样” / 一条条打 ✓ ✗ 分真假 / 活多了拿分工表去谈）→ 换个结局：往前放，名单上有小周 →
拉远看全板，推到评论区互动。
书中观点为转述（简·博克、莱诺拉·袁《拖延心理学》第3章，英文版 Fear of Success）；
例子与做法为示意 / 据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross, face,
                               join, marker, rect, stick, underline)

from .common import BOOK, episode

ACC = "#B8862A"
SQUARE_SHOT = 3                 # 场景 4（drop）：奖杯 + 压下来的一串台阶 + 小周 + 明天怪兽

b = Board(size=(3600, 10500))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """小周：火柴人 + 胸前工牌。(x, y) 为脚底。"""
    hy = y - 290 * s
    return join(stick(x, y, s, arms), P((x, hy + 50 * s), (x + 26 * s, hy + 100 * s)),
                rect(x + 26 * s, hy + 125 * s, 36 * s, 46 * s, 5 * s))


def monster(x, y, r=110, side=1) -> skia.Path:
    """明天怪兽：毛茸茸的圆 + 两只圆眼 + 小脚，一只手攥着日历页（side=1 在左手边，-1 在右手边）。“明天”二字另写。"""
    fur = [(x + r * (1.0 if i % 2 == 0 else 1.13) * math.cos(i / 30 * 2 * math.pi),
            y + r * (1.0 if i % 2 == 0 else 1.13) * math.sin(i / 30 * 2 * math.pi)) for i in range(30)]
    parts = [P(*fur, close=True)]
    for dx in (-0.32, 0.32):
        parts += [circle(x + dx * r, y - 0.38 * r, 0.19 * r), circle(x + dx * r + 0.05 * r, y - 0.34 * r, 0.06 * r)]
    for dx in (-0.35, 0.35):
        parts.append(P((x + (dx - 0.16) * r, y + 1.02 * r), (x + dx * r, y + 1.12 * r), (x + (dx + 0.16) * r, y + 1.02 * r)))
    cx, cy = x - side * 1.45 * r, y - 0.3 * r
    parts += [P((x - side * 0.98 * r, y - 0.05 * r), (cx + side * 0.2 * r, cy + 0.1 * r)),
              rect(cx, cy, 0.45 * r, 0.55 * r, 6), P((cx - 0.225 * r, cy - 0.12 * r), (cx + 0.225 * r, cy - 0.12 * r)),
              P((cx - 0.1 * r, cy - 0.33 * r), (cx - 0.1 * r, cy - 0.22 * r)),
              P((cx + 0.1 * r, cy - 0.33 * r), (cx + 0.1 * r, cy - 0.22 * r))]
    return join(*parts)


def M(x, y, r, k0, side=1, sfx="wood_low"):
    """画明天怪兽（黑轮廓）再在肚皮上写红字“明天”。"""
    L(monster(x, y, r, side), k0, k0 + 0.9, BLACK, 9, sfx=sfx)
    T("明天", x, y + 0.32 * r, round(0.6 * r), RED, k0=k0 + 0.9, k1=k0 + 1.7)


def trophy(x, y, s=1.0) -> skia.Path:
    """奖杯：(x, y) 为杯身中心偏上，整体约 y-180·s … y+140·s。"""
    cup = skia.Path()
    cup.moveTo(x - 110 * s, y - 180 * s)
    cup.cubicTo(x - 110 * s, y - 40 * s, x - 50 * s, y + 10 * s, x, y + 10 * s)
    cup.cubicTo(x + 50 * s, y + 10 * s, x + 110 * s, y - 40 * s, x + 110 * s, y - 180 * s)
    cup.close()
    parts = [cup]
    for sx in (-1, 1):
        h = skia.Path()
        h.moveTo(x + sx * 105 * s, y - 150 * s)
        h.quadTo(x + sx * 175 * s, y - 145 * s, x + sx * 150 * s, y - 90 * s)
        h.quadTo(x + sx * 130 * s, y - 50 * s, x + sx * 75 * s, y - 55 * s)
        parts.append(h)
    star = [(x + (32 if i % 2 == 0 else 13) * s * math.cos(-math.pi / 2 + i * math.pi / 5),
             y - 95 * s + (32 if i % 2 == 0 else 13) * s * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    parts += [P(*star, close=True), P((x - 18 * s, y + 10 * s), (x - 18 * s, y + 90 * s)),
              P((x + 18 * s, y + 10 * s), (x + 18 * s, y + 90 * s)), rect(x, y + 115 * s, 180 * s, 50 * s, 8 * s)]
    return join(*parts)


def sparkle(x, y, r=40) -> skia.Path:
    return join(P((x - r, y), (x + r, y)), P((x, y - r), (x, y + r)))


def rewind(x, y, s=1.0) -> skia.Path:
    """倒带符号 ◀◀。"""
    return join(P((x, y - 60 * s), (x - 100 * s, y), (x, y + 60 * s), close=True),
                P((x + 100 * s, y - 60 * s), (x, y), (x + 100 * s, y + 60 * s), close=True))


def play(x, y, s=1.0) -> skia.Path:
    """播放符号 ▶。"""
    return P((x - 60 * s, y - 70 * s), (x + 70 * s, y), (x - 60 * s, y + 70 * s), close=True)


def table(x, y, w=700) -> skia.Path:
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 30, y), (x - w / 2 + 30, y + 110)),
                P((x + w / 2 - 30, y), (x + w / 2 - 30, y + 110)))


def stack(x, base, n, w=170, h=26) -> skia.Path:
    """一摞文件：n 张，从桌面 base 往上叠，左右略错开。"""
    return join(*[rect(x + (6 if i % 2 else -6), base - h / 2 - i * h, w, h, 4) for i in range(n)])


def eyes(x, y, s=1.0) -> skia.Path:
    """隔板后探出的一双眼睛 + 两道斜眉。"""
    parts = []
    for dx in (-45, 45):
        p = skia.Path()
        p.addOval(skia.Rect.MakeXYWH(x + (dx - 24) * s, y - 11 * s, 48 * s, 22 * s))
        parts += [p, circle(x + dx * s, y, 5 * s)]
    parts += [P((x - 75 * s, y - 40 * s), (x - 20 * s, y - 22 * s)), P((x + 75 * s, y - 40 * s), (x + 20 * s, y - 22 * s))]
    return join(*parts)


def sweat(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y - 30 * s)
    p.quadTo(x + 22 * s, y, x, y + 12 * s)
    p.quadTo(x - 22 * s, y, x, y - 30 * s)
    return join(p, P((x + 40 * s, y - 40 * s), (x + 55 * s, y - 60 * s)))


def steps_path(x0, base, n, w, h) -> skia.Path:
    """往右上走的楼梯外轮廓：n 级，每级宽 w、高 h，(x0, base) 为左下角。"""
    pts = [(x0, base)]
    for i in range(n):
        pts += [(x0 + i * w, base - (i + 1) * h), (x0 + (i + 1) * w, base - (i + 1) * h)]
    pts += [(x0 + n * w, base)]
    return P(*pts, close=True)


def sit(x, y, s=1.0) -> skia.Path:
    """坐着往后靠的小人：(x, y) 为臀部（坐面），腿朝左垂下。"""
    sh = (x + 25 * s, y - 115 * s)
    return join(circle(x + 40 * s, y - 200 * s, 45 * s), P((x, y), (x + 35 * s, y - 155 * s)),
                P((x, y), (x - 110 * s, y), (x - 110 * s, y + 120 * s)), P(sh, (x - 70 * s, y - 20 * s)),
                rect(x + 45 * s, y - 85 * s, 32 * s, 40 * s, 5 * s))


def sit_face(x, y, s=1.0) -> skia.Path:
    hx, hy = x + 40 * s, y - 200 * s
    p = skia.Path()
    p.addCircle(hx - 15 * s, hy - 8 * s, 3 * s)
    p.addCircle(hx + 15 * s, hy - 8 * s, 3 * s)
    p.addArc(skia.Rect.MakeXYWH(hx - 20 * s, hy - 5 * s, 40 * s, 28 * s), 20, 140)
    return p


def qarrow(a, ctrl, z, head=60) -> skia.Path:
    """二次曲线箭头：起点 a、控制点 ctrl、终点 z。"""
    p = skia.Path()
    p.moveTo(*a)
    p.quadTo(*ctrl, *z)
    ang = math.atan2(z[1] - ctrl[1], z[0] - ctrl[0])
    for d in (0.45, -0.45):
        p.moveTo(*z)
        p.lineTo(z[0] - head * math.cos(ang + d), z[1] - head * math.sin(ang + d))
    return p


def calendar(x, y, w=400, h=380) -> skia.Path:
    top = y - h / 2
    parts = [rect(x, y, w, h, 16), P((x - w / 2, top + 80), (x + w / 2, top + 80)),
             P((x - w * 0.4, top - 25), (x - w * 0.4, top + 20)), P((x + w * 0.4, top - 25), (x + w * 0.4, top + 20)),
             P((x - w / 2, top + 80 + (h - 80) / 2), (x + w / 2, top + 80 + (h - 80) / 2))]
    for i in (1, 2):
        parts.append(P((x - w / 2 + w * i / 3, top + 80), (x - w / 2 + w * i / 3, y + h / 2)))
    return join(*parts)


def ease_back(k):
    k = clamp01(k)
    c = 1.9
    return 1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2


# ---------------------------------------------------------------- 结局先放这（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("名单上没有他", "结局先放这", (950, 1000, 0.85), bars=2)
L(rect(980, 1030, 560, 640, 20), 0, 0.9, sfx="wood_high")
T("晋升名单", 980, 800, 70, k0=1, k1=2, sfx="pop")
T("小王", 940, 950, 62, k0=2, k1=2.8, sfx="pop")
T("小李", 940, 1090, 62, k0=3, k1=3.8, sfx="pop")
L(P((820, 1250), (1060, 1250)), 4, 4.5, BLACK, 8, sfx="rim")
T("？", 1180, 1225, 100, RED, k0=4.5, k1=5.0)
L(zhou(480, 1350, 0.8), 5, 5.8, BLUE, 9, sfx="wood_high")
L(face(480, 1350, 0.8, "sad"), 5.8, 6.0, BLUE, 8)

scene("材料拖到最后", "倒带 · 三周前", (2650, 1000, 0.85))
L(rewind(2330, 640), 0, 0.9, BLUE, 9, sfx="wood_high")
T("倒带", 2560, 640, 80, BLUE, k0=1, k1=1.8, sfx="pop")
L(join(arrow((3200, 900), (2120, 900), 0, 50), *[P((x, 870), (x, 930)) for x in (3100, 2650, 2250)]), 2, 3.0,
  BLACK, 9, sfx="wood_low")
T("出名单", 3100, 990, 60, k0=3, k1=3.8, sfx="pop")
T("前一晚", 2650, 990, 60, k0=4, k1=4.8, sfx="pop")
L(rect(2650, 1200, 160, 200, 8), 5, 5.5, BLACK, 8, sfx="wood_high")
L(join(*[P((2600, 1150 + i * 40), (2700 - (i % 2) * 30, 1150 + i * 40)) for i in range(3)]), 5.5, 5.9, BLACK, 6)
T("凑合版", 2650, 1380, 60, RED, k0=6, k1=6.8, sfx="rim")
T("三周前", 2250, 990, 64, RED, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 书中观点：怕成功（场景 3–8）

scene("他怕的是做好", "拖延心理学 · 书中观点", (950, 2450, 0.85))
L(book(720, 2420, 420, 280), 0, 0.9, sfx="wood_low")
T("拖延心理学", 720, 2170, 70, GREEN, k0=1, k1=2.25, sfx="pop")
T("博克和袁", 720, 2710, 56, k0=3, k1=4, sfx="pop")
L(trophy(1300, 2420), 4, 4.9, BLACK, 9, sfx="wood_high")
L(join(sparkle(1080, 2250, 30), sparkle(1520, 2230, 36), sparkle(1500, 2420, 24)), 5, 5.6, ACC, 7, sfx="pop")
T("怕做好", 1300, 2730, 80, RED, k0=6, k1=6.8, sfx="ding")
L(underline(1180, 1420, 2790), 7, 7.8, RED, 8, sfx="wood_high")

# drop：台阶从奖杯后面“轰”地冒出来，越来越高，影子压到小周身上
SX, SB, SW, SH = 1760, 2900, 110, 170          # 台阶左下角 x、地面 y、每级宽、每级高
j_drop = scene("做好了要一直好", "书中观点 · 怕成功", (1400, 2550, 0.6), shake=[0], flashes=[0])


def stairs_fn(c, k, t):
    t0 = b.t_of(j_drop, 0)
    for i in range(4):
        g = ease_back((t - t0 - 0.07 * i) / 0.28)
        if g <= 0:
            continue
        h = SH * (i + 1) * g
        r = skia.Rect.MakeLTRB(SX + i * SW, SB - h, SX + (i + 1) * SW, SB)
        c.drawRect(r, K.paint(RED, 0.10))
        c.drawRect(r, marker(BLACK, 9))
    a = clamp01((t - b.t_of(j_drop, 2)) / 0.5)
    if a > 0:                                   # 第 2 拍起，台阶的影子压过来
        sh = P((SX, SB - SH * 2), (SX, SB), (SX - 300, SB), (SX - 250, SB - SH * 1.6), close=True)
        c.drawPath(sh, K.paint(BLACK, 0.13 * a))
    burst = clamp01((t - t0) / 0.5)
    if burst < 1:                               # 冒出来那一下的爆点短线
        for dx, dy in ((-60, -40), (0, -70), (60, -40)):
            x0, y0 = SX + 2 * SW + dx * 2, SB - SH * 4 - 160 + dy
            c.drawLine(x0, y0, x0 + dx * burst, y0 + dy * burst, K.paint(RED, 1 - burst, 8))
    return None


C(0, 0.6, stairs_fn, sfx="kick")
L(zhou(1590, 2900, 0.75, "shrug"), 1, 1.8, BLUE, 9, sfx="wood_high")
L(face(1590, 2900, 0.75, "sad"), 1.8, 2.0, BLUE, 8)
H(2, "tom")
M(SX + 3.5 * SW, SB - 4 * SH - 1.12 * 110, 110, 3)
T("做好一次", 1250, 1950, 72, k0=5, k1=6, sfx="pop")
T("就得一直这么好", 1250, 2080, 84, RED, k0=6, k1=7.75, sfx="ding")

scene("活会越来越多", "书中观点 · 要求变高", (900, 4300, 0.85))
L(table(890, 4520, 740), 0, 0.9, sfx="wood_high")
for n, (x, cnt) in enumerate(((640, 3), (830, 6), (1030, 10))):
    L(stack(x, 4520, cnt), 1 + n, 1.8 + n, BLACK, 7, sfx="pop")
L(zhou(1380, 4680, 0.7, "shrug"), 4, 4.8, BLUE, 9, sfx="wood_high")
L(face(1380, 4680, 0.7, "sad"), 4.8, 5.0, BLUE, 8)
T("活更多", 700, 3960, 80, RED, k0=5, k1=5.8, sfx="pop")
L(bubble(1250, 4080, 400, 120, -1), 6, 6.4, BLACK, 8, sfx="pop")
T("这个也给你", 1250, 4080, 54, k0=6.4, k1=7.65)

scene("怕被人盯上", "书中观点 · 竞争眼红", (2700, 4300, 0.85))
L(join(*[rect(x, 4420, 330, 240, 10) for x in (2350, 2700, 3050)]), 0, 1.0, BLACK, 9, sfx="wood_high")
for n, x in enumerate((2350, 2700, 3050)):
    L(eyes(x, 4262), 1 + n, 1.7 + n, BLACK, 7, sfx="pop")
L(join(zhou(2700, 4880, 0.7, "hold"), trophy(2810, 4690, 0.35)), 4, 4.9, BLUE, 8, sfx="wood_high")
L(face(2700, 4880, 0.7, "sad"), 4.9, 5.1, BLUE, 8)
T("被盯上", 2700, 4050, 84, RED, k0=6, k1=6.8, sfx="rim")
L(sweat(2620, 4640, 0.9), 7, 7.6, BLUE, 6, sfx="pop")

# 小周一级级往上走，跟老同事之间的线越拉越长（动态 custom）
GX, GY = 1250, 6050                             # 老同事脚底
ZS = 0.65
ZPOS = [(1000, 6050), (790, 5930), (650, 5810), (510, 5690)]
j_far = scene("怕跟老朋友远了", "书中观点 · 拉开距离", (900, 5700, 0.85))
L(join(stick(GX, GY, ZS, hair=True), face(GX, GY, ZS, "smile")), 0, 0.9, BLACK, 9, sfx="wood_high")
L(join(P((860, 6050), (860, 5930), (720, 5930), (720, 5810), (580, 5810), (580, 5690), (440, 5690), (440, 6050)),
       P((440, 6050), (1420, 6050))), 1, 1.9, BLACK, 9, sfx="wood_low")


def climb_fn(c, k, t):
    pos = ZPOS[0]
    for n, kb in enumerate((3, 4, 5)):
        tb = b.t_of(j_far, kb)
        if t >= tb:
            pos = ZPOS[n + 1]
        elif t >= tb - 0.3:
            f = clamp01((t - tb + 0.3) / 0.3)
            (x0, y0), (x1, y1) = ZPOS[n], ZPOS[n + 1]
            pos = (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f - 70 * 4 * f * (1 - f))
            break
        else:
            break
    x, y = pos
    hy = y - 290 * ZS
    a = clamp01(k * 1.5)
    gx = GX - 70 * ZS
    gy = GY - 290 * ZS + 170 * ZS
    dist = math.hypot(gx - (x + 70 * ZS), gy - (hy + 170 * ZS))
    lp = K.paint(BLACK, 0.75 * a, max(3.0, 9 - dist / 120))
    lp.setPathEffect(skia.DashPathEffect.Make([28, 18], 0))
    c.drawLine(x + 70 * ZS, hy + 170 * ZS, gx, gy, lp)
    c.drawPath(zhou(x, y, ZS), K.paint(BLUE, a, 9))
    c.drawPath(face(x, y, ZS, "smile" if pos == ZPOS[0] else "flat"), K.paint(BLUE, a, 8))
    return None


C(2, 2.6, climb_fn, sfx="pop")
for kb in (3, 4, 5):
    H(kb, "tom", 0.7)
T("老同事", GX, 6130, 52, k0=6, k1=6.8, sfx="pop")
T("越走越远", 900, 5320, 80, RED, k0=7, k1=8, sfx="pop")

scene("拖着刚好卡中间", "书中观点 · 卡在中间", (2700, 5730, 0.85))
L(steps_path(2160, 6150, 6, 180, 140), 0, 1.0, BLACK, 9, sfx="wood_high")
M(2790, 5590 - 1.12 * 130, 130, 1, side=-1)
L(sit(2600, 5730, 0.75), 3, 3.8, BLUE, 9, sfx="pop")
L(sit_face(2600, 5730, 0.75), 3.8, 4.0, BLUE, 7)
T("上去：要一直好", 2400, 5290, 56, k0=4, k1=5.6, sfx="wood_high")
T("下来：不甘心", 3060, 5980, 56, k0=5.6, k1=7.0)
T("卡在中间", 2550, 6235, 84, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 倒带看完：拉远看全板，三条绿箭头连回名单（场景 9）

scene("倒带看完了", "倒带看完", (1800, 3530, 0.17))
L(qarrow((1720, 2150), (1700, 1500), (1300, 1320), 110), 0, 0.9, GREEN, 36, sfx="wood_high")
L(qarrow((2750, 3880), (2750, 1250), (1300, 1150), 110), 1, 1.9, GREEN, 36, sfx="wood_high")
L(qarrow((400, 5550), (120, 3500), (430, 1450), 110), 2, 2.9, GREEN, 36, sfx="wood_high")
L(circle(1180, 1225, 130), 3, 3.8, RED, 30, sfx="ding")
T("原因连上了", 1500, 3450, 240, GREEN, k0=4, k1=5.25, sfx="pop")
L(play(2360, 3450, 1.8), 6, 6.8, BLUE, 30, sfx="pop")

# ---------------------------------------------------------------- 做法（场景 10–12）

ROWS = [("① 活更多", 7220), ("② 被盯上", 7400), ("③ 跟人远了", 7580)]
scene("先写下你怕啥", "第一步 · 写下来", (950, 7300, 0.85))
L(rect(850, 7330, 760, 820, 18), 0, 0.9, BLACK, 9, sfx="wood_high")
T("做好了会怎样", 850, 7020, 62, BLUE, k0=1, k1=2.5, sfx="pop")
for n, (s, y) in enumerate(ROWS):
    T(s, 800, y, 64, k0=3 + n, k1=3.9 + n if n < 2 else 6.25, sfx="pop")
L(zhou(1380, 7700, 0.7), 7, 7.8, BLUE, 9, sfx="wood_high")
L(face(1380, 7700, 0.7, "flat"), 7.8, 8.0, BLUE, 8)

scene("一条条看真假", "第二步 · 分真假", (1000, 7420, 0.85))
L(check(1110, 7225, 40), 0, 0.6, GREEN, 10, sfx="ding")
L(cross(1110, 7400, 32), 1, 1.6, RED, 10, sfx="rim")
L(cross(1110, 7580, 32), 2, 2.6, RED, 10, sfx="rim")
L(check(480, 7860, 26), 4, 4.4, GREEN, 8, sfx="pop")
T("真会发生", 640, 7860, 56, GREEN, k0=4.4, k1=5.4)
L(cross(930, 7860, 22), 6, 6.3, RED, 8, sfx="pop")
T("想出来的", 1100, 7860, 56, RED, k0=6.3, k1=7.0)
L(rect(800, 7220, 420, 120, 50), 7, 7.7, GREEN, 7, sfx="ding")

scene("能谈的就去谈", "第三步 · 去谈", (2700, 7350, 0.85))
L(zhou(2300, 7750, 0.75, "point"), 0, 0.8, BLUE, 9, sfx="wood_high")
L(face(2300, 7750, 0.75, "smile"), 0.8, 1.0, BLUE, 8)
L(stick(3100, 7750, 0.75, tie=True), 1, 1.8, BLACK, 9, sfx="pop")
L(face(3100, 7750, 0.75, "smile"), 1.8, 2.0, BLACK, 8)
L(bubble(2350, 7130, 340, 120, -1), 2, 2.4, BLUE, 8, sfx="pop")
T("能分一下吗", 2350, 7130, 52, BLUE, k0=2.4, k1=3.65)
L(join(table(2700, 7650, 400), rect(2700, 7430, 320, 300, 10)), 4, 4.9, BLACK, 9, sfx="wood_high")
T("分工表", 2700, 7330, 54, GREEN, k0=5, k1=5.8, sfx="pop")
T("我：方案", 2700, 7440, 48, k0=6, k1=7, sfx="pop")
T("同事：数据", 2700, 7530, 48, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 换个结局（场景 13）

scene("这回不倒带", "换个结局", (1800, 8700, 0.85))
L(play(1380, 8270), 0, 0.8, GREEN, 9, sfx="wood_high")
T("往前放", 1620, 8270, 72, GREEN, k0=1, k1=1.8, sfx="pop")
L(calendar(1500, 8720), 2, 2.9, BLACK, 8, sfx="wood_low")
T("提前一周", 1500, 8572, 52, k0=3, k1=4, sfx="pop")
L(check(1500, 8760, 60), 4, 4.6, RED, 12, sfx="ding")
L(join(rect(2120, 8760, 440, 560, 18), P((1990, 8700), (2250, 8700)), P((1990, 8790), (2250, 8790))), 5, 5.9,
  BLACK, 8, sfx="wood_high")
T("晋升名单", 2120, 8570, 60, k0=6, k1=7, sfx="pop")
T("小周", 2120, 8910, 76, BLUE, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：第 0 拍拉远看全板，第 4 拍推到评论区

FAR = (1800, 5200, 0.09)
scene("你怕做好过吗", "评论区见", FAR, bars=4)
b.move(J(), 4, (1800, 9900, 0.8))
H(0, "cymbal", 0.5)
H(2, "ding")
L(bubble(1800, 9735, 1000, 300, -1), 5, 5.9, BLACK, 9, sfx="wood_high")
T("你怕做好过吗？", 1800, 9680, 76, RED, k0=6, k1=7.75, sfx="pop")
T("说说是哪件事", 1800, 9800, 60, k0=8, k1=9.5, sfx="pop")
T("下一讲：领导越催，我越不想动", 1800, 10080, 52, k0=10, k1=13.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "success", "怕做好", "做得太好，怕以后都得这么好", ACC, b.shots,
                 [f"{BOOK}第3章（中译本“对话拖延：拖延你好，成功再见”，英文版 Fear of Success），转述",
                  "中译本：《拖延心理学：向与生俱来的行为顽症宣战》，蒋永强、陆正芳译，中国人民大学出版社（湛庐文化）2009"],
                 "做得太好|怕以后【都得这么好】", SQUARE_SHOT,
                 ["书中观点为转述：有些拖延的人怕的是成功——做好一次，别人的要求就跟着变高，以后得一直这么好；成功可能"
                  "招来竞争和眼红，也可能让人跟身边亲近的人拉开距离；拖着，人就停在不上不下的位置（第3章）。上屏均为"
                  "转述，不是逐字引文。",
                  "晋升名单、答辩材料、“三周前 / 前一晚”的时间线、隔板后的眼睛、文件越叠越高、跟老同事越走越远、"
                  "楼梯中间坐着，均为示意；名单上的“小王”“小李”为虚构人名，不指向任何具体公司或个人。",
                  "三步做法（写下“做好了会怎样”、一条条分真假、能谈的就去谈分工和节奏）为据书中思路整理；"
                  "“提前一周交”“分工表”内容为示意。"],
                 tags="#害怕成功 #职场")
    return b.attach(ep)
