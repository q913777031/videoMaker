"""07 大脑在躲（白板手绘版）：一打开文档，脑子就想跑。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：最后 4 拍不出新笔画）。
叙事（J 一个比喻贯穿）：小周的脑子画成一栋两层小楼——一楼门口一个保安（遇到难事就拉警报），二楼一个排班的
（管计划、开工、坚持）。整讲在这栋楼里进进出出——
打工人开局（打开一份空白文档，光标在闪，一个字没写 → 手伸向手机，明天怪兽在手机里招手）→
书中观点（亮书《拖延心理学》，博克和袁，书里有几章专讲大脑；drop：保安一看任务难，红灯闪满屏，门“砰”地关上；
觉得有威胁，脑子先想躲；楼上排班的管计划、开工、坚持；警报一大，楼上的排班表也被吹飞；楼会随练习变，加一道越走越熟的楼梯）→
具体做法（把门牌“难”改成“列标题” / 警报响了先停一下、慢慢呼气 / 把下一步写在便利贴上递给楼上）→
走熟了警报变小、小周顺着楼梯上楼 → 拉远看整栋楼，明天怪兽被关在门外 → 评论区互动。
书中观点为转述（Jane B. Burka & Lenora M. Yuen, Procrastination: Why You Do It, What to Do About It Now, 2008 修订版，
第7–8章；中译本《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009，第三部分“拖延 vs 大脑”）；
小楼、保安、排班的为本讲通俗化示意，不是书中比喻；例子与做法为示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, check, circle, cross, doc, face,
                               join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, lerp

from .common import BOOK, episode

ACC = "#3B7EA1"
SQUARE_SHOT = 3                 # 场景 4（drop）：保安拉警报、门“砰”关上，小周站在门外

b = Board(size=(3600, 5200))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 系列角色

def badge(x, y, s=1.0) -> skia.Path:
    """配合 stick 的工牌（挂绳 + 卡片）：(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 22 * s, hy + 45 * s), (x + 18 * s, hy + 130 * s), (x + 30 * s, hy + 45 * s)),
                rect(x + 18 * s, hy + 155 * s, 38 * s, 50 * s, 5 * s))


def zhou(x, y, s=0.75, arms="down", mood="flat") -> skia.Path:
    """小周：火柴人 + 胸前工牌。"""
    return join(stick(x, y, s, arms), face(x, y, s, mood), badge(x, y, s))


def monster(x, y, r) -> skia.Path:
    """明天怪兽：毛茸茸的一团 + 两只圆眼 + 小手攥着一张日历页（“明天”二字另写）。"""
    pts = []
    n = 44
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = r * (1.12 if i % 2 else 1.0)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    parts = [P(*pts, close=True)]
    for dx in (-0.33, 0.33):
        parts += [circle(x + dx * r, y - 0.3 * r, 0.2 * r), circle(x + dx * r + 0.04 * r, y - 0.28 * r, 0.07 * r)]
    parts += [P((x - 1.05 * r, y + 0.1 * r), (x - 1.35 * r, y - 0.2 * r)),
              P((x + 1.05 * r, y + 0.1 * r), (x + 1.3 * r, y - 0.05 * r)),
              rect(x + 1.55 * r, y - 0.15 * r, 0.5 * r, 0.6 * r, 6), P((x + 1.3 * r, y - 0.33 * r), (x + 1.8 * r, y - 0.33 * r))]
    return join(*parts)


def belly(x, y, r, size, k0, k1=None, sfx=None):
    T("明天", x, y + 0.4 * r, size, RED, k0=k0, k1=k1, sfx=sfx)


# ---------------------------------------------------------------- 本讲画法

def guard(x, y, s=0.75) -> skia.Path:
    """保安：火柴人 + 大檐帽 + 胸前哨子。(x, y) 为脚底。"""
    hy = y - 290 * s
    cap = skia.Path()
    cap.addArc(skia.Rect.MakeXYWH(x - 48 * s, hy - 75 * s, 96 * s, 70 * s), 180, 180)
    return join(stick(x, y, s, "down"), face(x, y, s, "flat"), cap,
                P((x - 62 * s, hy - 38 * s), (x + 62 * s, hy - 38 * s)),
                P((x, hy + 60 * s), (x + 22 * s, hy + 95 * s)), circle(x + 30 * s, hy + 102 * s, 9 * s))


def lamp(x, y, r=50) -> skia.Path:
    """警报灯：半圆灯罩 + 底座 + 一道反光。(x, y) 为灯罩底边中点。"""
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 180, 180)
    return join(dome, P((x - r, y), (x + r, y)), rect(x, y + 14, 2.6 * r, 24, 6),
                P((x - r * 0.45, y - r * 0.55), (x - r * 0.2, y - r * 0.8)))


def waves(x, y, radii, span=32) -> skia.Path:
    """警报灯两侧的声波弧（左右各几道）。"""
    parts = []
    for r in radii:
        for a0 in (-span, 180 - span):
            p = skia.Path()
            p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), a0, 2 * span)
            parts.append(p)
    return join(*parts)


def stairs(x0, y0, n, dx, dy) -> skia.Path:
    """楼梯：从 (x0, y0) 起 n 级，每级宽 dx、高 dy；下面一道斜梁。"""
    pts = [(x0, y0)]
    for i in range(n):
        pts += [(x0 + i * dx, y0 - (i + 1) * dy), (x0 + (i + 1) * dx, y0 - (i + 1) * dy)]
    return join(P(*pts), P((x0 + dx, y0), (x0 + (n + 0.6) * dx, y0 - n * dy + 30)))


def foot(x, y, w=30, h=16) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def dots(*pts) -> skia.Path:
    """念头气泡：一串由小到大的圆。"""
    return join(*[circle(x, y, r) for x, y, r in pts])


def heart(x, y, r=30) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def breath(x0, y0, x1, y1, n=3, amp=26) -> skia.Path:
    """一口长长的呼气：起伏的气流线。"""
    p = skia.Path()
    p.moveTo(x0, y0)
    for i in range(n):
        xa, ya = lerp(x0, x1, (i + 0.5) / n), lerp(y0, y1, (i + 0.5) / n) + (amp if i % 2 else -amp)
        xb, yb = lerp(x0, x1, (i + 1) / n), lerp(y0, y1, (i + 1) / n)
        p.quadTo(xa, ya, xb, yb)
    return p


def sweat(x, y) -> skia.Path:
    """两滴汗。"""
    parts = []
    for dx, dy in ((0, 0), (36, 30)):
        p = skia.Path()
        p.moveTo(x + dx, y + dy - 18)
        p.quadTo(x + dx + 12, y + dy + 4, x + dx, y + dy + 10)
        p.quadTo(x + dx - 12, y + dy + 4, x + dx, y + dy - 18)
        parts.append(p)
    return join(*parts)


# ---------------------------------------------------------------- 小楼的位置

HL, HR, HG, HM, HT = 1300, 2500, 3600, 3000, 2600      # 左墙、右墙、地面、二楼地板、屋檐
DL, DR, DT = 1450, 1650, 3250                          # 一楼门框
SIGN = (1550, 3170)                                    # 门牌（门框上方）
LAMP = (1850, 3110)                                    # 警报灯
GUARD = (1800, HG)
ZHOU = (1100, HG)                                      # 小周站在门外
BOSS = (1600, 2990)                                    # 二楼排班的
V1 = (1650, 3330, 0.85)                                # 一楼门口
V2 = (1900, 2780, 0.85)                                # 二楼


def house() -> skia.Path:
    return join(P((700, HG), (3100, HG)), P((HL, HG), (HL, HT), (HR, HT), (HR, HG)), P((HL, HM), (HR, HM)),
                P((HL - 70, HT), (1900, 2280), (HR + 70, HT)))


def note_fn(x, y, w, h):
    """黄便利贴底色。"""

    def fn(c, k, t):
        K.rr(c, x, y, w, h, 8, "#FFE27A", 0.9 * k)
        return None

    return fn


J_BOOK, J_DROP, J_SIGN, J_ALL = 2, 3, 8, 12           # 门的开关落在这几个场景


def door_fn(c, k, T):
    """一楼的门：场景 3 半开 → drop 第 3 拍“砰”地关上 → 改门牌后打开 → 场景 13 再关上，把怪兽关在门外。"""
    o = 1.0
    for j, kb, target, dur in ((J_DROP, 3, 0.0, 0.12), (J_SIGN, 5, 1.0, 0.5), (J_ALL, 2, 0.0, 0.15)):
        t0 = b.t_of(j, kb)
        if T >= t0:
            o += (target - o) * ease_in_out(clamp01((T - t0) / dur))
    w = DR - DL
    fx = DL + w * (1 - 0.75 * o)
    dy = 30 * o
    if o > 0.02:
        c.drawRect(skia.Rect.MakeLTRB(DL, DT, DR, HG), K.paint("#2B2B33", 0.18 * o * k))
    leaf = P((DL, DT), (fx, DT + dy), (fx, HG - dy * 0.4), (DL, HG), close=True)
    c.drawPath(leaf, K.paint("#F1E2C6", k))
    c.drawPath(leaf, wb.marker(BLACK, 8, k))
    c.drawCircle(fx - 22 * (1 - 0.6 * o), 3430, 9, K.paint(BLACK, k))
    return None


def alarm_fn(c, k, T):
    """drop：红灯一闪一闪，整块白板跟着泛红。"""
    if k >= 1:
        return None
    ph = 0.5 - 0.5 * math.cos(T * 2 * math.pi * 2.1)
    fade = 1 - k ** 3
    c.drawRect(skia.Rect.MakeXYWH(0, 0, b.BW, b.BH), K.paint(RED, 0.2 * ph * fade))
    c.drawCircle(LAMP[0], LAMP[1] - 25, 300, K.paint(RED, 0.55 * ph * fade, blur=70))
    c.drawCircle(LAMP[0], LAMP[1] - 25, 46, K.paint(RED, 0.9 * ph * fade))
    return None


def rings_fn(c, k, T):
    """警报声一圈圈往外扩，一直扩到二楼。"""
    if k >= 1:
        return None
    fade = 1 - k ** 3
    for i in range(3):
        f = (T * 1.3 + i / 3) % 1
        c.drawCircle(LAMP[0], LAMP[1] - 25, 90 + 560 * f, K.paint(RED, 0.75 * (1 - f) * fade, 9))
    return None


def pages_fn(x0, y0, dests):
    """排班表被吹散：纸片一张张飞出去，落在二楼地板上。"""

    def fn(c, k, t):
        for i, (x1, y1, rot) in enumerate(dests):
            f = clamp01(k * len(dests) - i * 0.6)
            if f <= 0:
                continue
            e = ease_in_out(f)
            x = lerp(x0, x1, e)
            y = lerp(y0, y1, e) - 160 * math.sin(math.pi * e)
            c.save()
            c.translate(x, y)
            c.rotate(rot * e + 40 * math.sin(f * 9) * (1 - e))
            c.drawPath(rect(0, 0, 60, 70, 6), wb.marker(BLACK, 6))
            c.drawPath(P((-20, -12), (20, -12)), wb.marker(BLUE, 5))
            c.drawPath(P((-20, 8), (14, 8)), wb.marker(BLUE, 5))
            c.restore()
        return None

    return fn


# ---------------------------------------------------------------- 开局：空白文档（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

b.shot("文档一打开", "空白文档", (1950, 1250, 1.0), bars=2)
L(rect(1950, 1200, 480, 320, 14), 0, 0.9, sfx="wood_high")
L(join(P((1950, 1360), (1950, 1425)), P((1870, 1425), (2030, 1425)), P((1640, 1445), (2300, 1445))), 1, 1.8,
  sfx="wood_low")
T("方案初稿", 1950, 1085, 50, k0=2, k1=3, sfx="pop")
L(P((1710, 1125), (2190, 1125)), 2.9, 3.0, BLACK, 6)


def cursor_fn(c, k, T):
    """空白文档里一闪一闪的光标。"""
    if int(T * 2.4) % 2 == 0:
        c.drawRect(skia.Rect.MakeXYWH(1752, 1150, 7, 62), K.paint(BLACK))
    return None


b.custom(J(), 3, 3.3, cursor_fn, sfx="pop")
T("一个字没写", 1950, 1300, 50, RED, k0=4, k1=5.25, sfx="pop")

b.shot("手就去摸手机", "空白文档", (1600, 1350, 0.75), bars=3)
L(zhou(1500, 1700, 0.9, "down"), 0, 0.9, sfx="wood_high")
L(join(rect(1150, 1250, 340, 480, 30), P((1110, 1465), (1190, 1465))), 1, 1.9, BLUE, 9, sfx="pop")
L(arrow((1415, 1560), (1335, 1420), 0.25, 34), 2, 2.7, RED, 9, sfx="wood_high")
MON2 = (1130, 1250, 95)
L(monster(*MON2), 3, 3.9, BLACK, 8, sfx="wood_low")
belly(*MON2, 56, k0=4, k1=4.8, sfx="pop")
T("三秒后", 1150, 960, 60, RED, k0=5, k1=5.8, sfx="pop")

# ---------------------------------------------------------------- 书中观点：脑子里的小楼（场景 3–8）

b.shot("书里讲了大脑", "拖延心理学 · 书中观点", (1550, 2950, 0.55), bars=3)
L(book(850, 2480, 340, 230), 0, 0.9, sfx="wood_low")
T("《拖延心理学》", 850, 2700, 80, GREEN, k0=1, k1=2.75, sfx="pop")
T("博克和袁", 850, 2820, 70, k0=2.8, k1=3.6)
L(zhou(*ZHOU, 0.7, "down"), 3.6, 4.4)
L(dots((1145, 3330, 10), (1175, 3240, 14), (1215, 3140, 18)), 4, 4.5, BLACK, 7, sfx="pop")
L(house(), 5, 6, BLACK, 10, sfx="wood_high")
L(P((DL, HG), (DL, DT), (DR, DT), (DR, HG)), 6, 6.5, BLACK, 9, sfx="wood_low")
b.custom(J(), 6.4, 6.9, door_fn)
T("小周的脑子", 1900, 2505, 80, BLUE, k0=7, k1=8, sfx="pop")

b.shot("门口警报响了", "书中观点 · 门口的保安", V1, shake=[0, 3], flashes=[0], bars=3)
L(lamp(*LAMP), 0, 0.8, RED, 9, sfx="kick")
b.custom(J(), 0, 10, alarm_fn)
L(guard(*GUARD), 1, 1.9, BLACK, 9, sfx="wood_high")
L(waves(*LAMP, (80, 125, 170)), 2, 2.8, RED, 8, sfx="shaker")
H(3, "kick")
T("砰", 1550, 3440, 90, RED, k0=3, k1=3.8)
T("呜呜", 2110, 3110, 60, RED, k0=5, k1=5.8, sfx="pop")
L(join(P((1660, 3300), (1700, 3280)), P((1660, 3380), (1705, 3380)), P((1660, 3460), (1700, 3480))), 6, 6.6, RED, 7,
  sfx="rim")

b.shot("遇到难事先躲", "书中观点 · 觉得危险就躲", V1, bars=3)
L(rect(*SIGN, 190, 90, 10), 0, 0.8, BLACK, 8, sfx="wood_high")
T("难", *SIGN, 64, RED, k0=1, k1=1.8, sfx="ding")
L(doc(1200, 3480, 110, 140, 0), 2, 2.7, BLACK, 8, sfx="pop")
T("方案", 1200, 3480, 46, k0=2.7, k1=3.5)
L(arrow((1440, 3300), (1275, 3300), 0.15, 34), 4, 4.7, RED, 9, sfx="rim")
T("先躲", 1180, 3020, 90, RED, k0=6, k1=6.8, sfx="pop")

b.shot("楼上的在排班", "书中观点 · 楼上排班的", V2, bars=3)
L(join(stick(*BOSS, 0.6, "hold"), face(*BOSS, 0.6, "smile")), 0, 0.9, BLACK, 9, sfx="wood_high")
L(rect(2080, 2880, 400, 190, 12), 1, 1.8, BLUE, 8, sfx="wood_low")
T("排班表", 2080, 2830, 50, BLUE, k0=2, k1=2.8, sfx="pop")
for n, w in enumerate(("计划", "开工", "坚持")):
    T(w, 1960 + n * 120, 2925, 50, k0=3 + n, k1=3.8 + n, sfx="pop")

b.shot("警报一响他就慌", "书中观点 · 楼上也乱了", (1900, 2950, 0.7), bars=3)
b.custom(J(), 0, 9, rings_fn, sfx="shaker")
b.erase(J(), 1, 2, 1890, 2877, 860, 235)
H(1, "tom")
b.custom(J(), 1.2, 4.5, pages_fn(2080, 2880, [(1860, 2950, -20), (2010, 2955, 30), (2160, 2945, -40), (2300, 2952, 15)]))
L(join(stick(*BOSS, 0.6, "up"), face(*BOSS, 0.6, "sad")), 3, 3.9, BLACK, 9, sfx="wood_high")
T("乱了", 2380, 2830, 70, RED, k0=5, k1=5.8, sfx="pop")
L(sweat(1660, 2790), 6, 6.6, BLUE, 6, sfx="pop")

b.shot("楼可以改", "书中观点 · 大脑会变", (2150, 3000, 0.6), bars=3)
L(stairs(2000, HG, 6, 75, 100), 0, 0.9, BLACK, 9, sfx="wood_high")
for n, (fx_, fy) in enumerate(((2112, 3388), (2187, 3288), (2262, 3188))):
    L(join(foot(fx_ - 14, fy), foot(fx_ + 14, fy - 4)), 2 + n, 2.6 + n, GREEN, 7, sfx="pop")
T("越走越熟", 2780, 3250, 80, GREEN, k0=6, k1=7, sfx="ding")
L(underline(2620, 2940, 3320, 10, 32), 7, 7.8, GREEN, 8)

# ---------------------------------------------------------------- 具体做法（场景 9–11）

b.shot("把门牌改小", "做法一 · 改门牌", V1, bars=3)
L(cross(*SIGN, 45), 0, 0.6, RED, 10, sfx="rim")
b.erase(J(), 1, 1.8, SIGN[0], SIGN[1], 210, 110)
H(1, "shaker")
L(rect(*SIGN, 190, 90, 10), 2, 2.8, BLUE, 8, sfx="wood_high")
T("列标题", *SIGN, 50, BLUE, k0=3, k1=3.8, sfx="pop")
H(5, "wood_low")
L(check(1695, 3175, 28), 6, 6.6, GREEN, 9, sfx="ding")

b.shot("警报响就喘口气", "做法二 · 先停一下", (1300, 3250, 0.85), bars=3)
L(cross(1180, 3020, 55), 0, 0.6, RED, 10, sfx="rim")
T("先停一下", 880, 3060, 60, BLUE, k0=1, k1=2, sfx="pop")
L(breath(1075, 3390, 850, 3300), 3, 3.9, BLUE, 8, sfx="shaker")
T("慢慢呼气", 880, 3175, 56, BLUE, k0=4, k1=5, sfx="pop")
L(heart(1100, 3480, 18), 6, 6.6, RED, 7, sfx="ding")

b.shot("给楼上递张单", "做法三 · 写下一步", (1700, 2950, 0.7), bars=3)
b.erase(J(), 0, 0.8, BOSS[0], 2880, 260, 230)
b.erase(J(), 0, 0.8, 2380, 2830, 180, 100)
H(0, "tom")
L(join(stick(*BOSS, 0.6, "hold"), face(*BOSS, 0.6, "smile")), 1, 1.9, BLACK, 9, sfx="wood_high")
b.custom(J(), 2, 2.5, note_fn(1900, 2840, 300, 150))
L(rect(1900, 2840, 300, 150, 8), 2, 2.8, ORANGE, 7, sfx="wood_high")
T("下一步", 1900, 2805, 50, k0=3, k1=3.8, sfx="pop")
T("写第二段", 1900, 2878, 50, BLUE, k0=4, k1=5, sfx="pop")
L(arrow((1140, 3330), (1745, 2925), -0.25, 36), 6, 6.8, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 走熟了（场景 12–13）

b.shot("走熟了就不响", "越走越熟", V1, bars=3)
b.erase(J(), 0, 0.8, LAMP[0] - 137, LAMP[1], 85, 200)
b.erase(J(), 0, 0.8, LAMP[0] + 137, LAMP[1], 85, 200)
H(0, "shaker")
L(join(P((2050, 3085), (2170, 3135)), P((2050, 3135), (2170, 3085))), 1, 1.6, RED, 8, sfx="rim")
b.erase(J(), 2, 2.8, 1055, 3436, 470, 312)
H(2, "tom")
L(join(*[foot(x, 3585 - (i % 2) * 14) for i, x in enumerate(range(1180, 1990, 90))],
       foot(2037, 3492), foot(2112, 3392)), 3, 3.9, GREEN, 6, sfx="wood_high")
L(zhou(2190, 3300, 0.5, "up", "smile"), 4, 4.9, BLACK, 8, sfx="pop")
T("呼噜", 1935, 3330, 50, BLUE, k0=6, k1=6.8, sfx="ding")

b.shot("整栋楼看一眼", "全楼一览", (1750, 3050, 0.45), bars=3)
MON13 = (950, 3450, 130)
L(monster(*MON13), 0, 0.9, BLACK, 9, sfx="wood_low")
belly(*MON13, 90, k0=1, k1=1.8, sfx="pop")
H(2, "kick")
T("保安", 1780, 3730, 90, k0=3, k1=3.8, sfx="pop")
T("排班的", 1600, 2690, 90, k0=4, k1=4.8, sfx="pop")
T("关在门外", 950, 3730, 90, RED, k0=5, k1=6, sfx="pop")
L(underline(780, 1120, 3800, 12, 40), 6, 6.8, RED, 9, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 2900, 0.24)
COMMENT = (1800, 4660, 0.8)
b.shot("你脑子在躲啥", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你一打开啥就想跑？", 1800, 4580, 76, RED, k0=6, k1=8.25, sfx="pop")
T("下一讲：这几句心里话，你中了几句", 1800, 4740, 50, k0=9, k1=13, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "brain", "大脑在躲", "一打开文档，脑子就想跑", ACC, b.shots,
                 [f"{BOOK}第7–8章（中译本第三部分“拖延 vs 大脑”：第7章 世界上存在“拖延基因”吗、第8章，转述）",
                  "中译本：《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009；原书 Da Capo Lifelong Books 2008 修订版"],
                 "一打开文档|脑子就【想跑】", SQUARE_SHOT,
                 ["书中观点为转述（大意，细节需核实）：遇到感觉有威胁的任务，脑子里管警报的部分会先反应，人就想躲；"
                  "负责计划、开工、坚持的是大脑的执行功能；大脑会随练习改变，习惯可以慢慢改（第7–8章）。"
                  "上屏不写脑区名称，句子均为口语转述，不是逐字引文。",
                  "两层小楼、一楼保安拉警报、二楼排班的、越走越熟的楼梯，是本讲的通俗化示意，不是书中比喻；"
                  "明天怪兽为本系列的画面角色。",
                  "打开空白文档、三秒后去摸手机为现实场景示意，“三秒”不是数据；不指向任何具体公司或个人。",
                  "三条做法（把“写方案”改成“列标题”这样的小任务；想跑时先停一下、慢慢呼气；把下一步写在便利贴上）"
                  "为据书中思路整理的建议，示意；呼气一条对应书中第15章“利用身体”的大意，需核实。"],
                 tags="#大脑 #心理学")
    return b.attach(ep)
