"""05 怕靠近怕分开（白板手绘版）：有人拖着等人帮，有人拖着躲人。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：每屏第 0–8 拍画完，最后 4 拍停住）。
叙事（F 两人对比）：白板正中一条竖线，左边同事小林（蓝）、右边小周（黑，带工牌），同一份季度总结两人都拖着 →
两人头顶各一个问号，明天怪兽蹲在中线脚下 → 亮书《拖延心理学》，两人中间一把尺子：拖延也跟和人的距离有关 →
drop：两人各画出自己的安全圈，小林的圈紧紧圈住同事，小周的圈“砰”地推出去很远 →
左：没做完就有人来管来陪；独自做完就得一个人扛 → 右：交出去别人就能提要求；拖着别人就没法靠近（圈外一圈刺）→
中线对照：怕分开 / 怕靠近，怪兽骑在中线上 → 做法分两边：小林先自己写一段再找人；小周先挑一个信得过的人看半成品 →
两个圈各往中线挪一点 → 两份总结飞进同一个文件夹 → 拉远看全板 → 评论区 + 下一讲预告。
书中观点为转述（Jane B. Burka & Lenora M. Yuen, Procrastination: Why You Do It, What to Do About It Now, 2008 修订版，
第 5 章 Separation and Attachment；中译本《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009，
第 5 章“心理舒适区：对亲近与疏远的恐惧”）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, doc, face,
                               join, marker, rect, stick)

from .common import BOOK, episode

ACC = "#7A5BA6"
SQUARE_SHOT = 3                 # 场景 4（drop）：两人各自的安全圈，一个贴着同事，一个推得远远的

b = Board(size=(3600, 13800))
MID = 1800                      # 白板中线：左边小林，右边小周


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


# ---------------------------------------------------------------- 本讲画法

def badge(x, y, s=1.0) -> skia.Path:
    """小周的工牌：挂绳 + 胸前小卡。(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 18 * s, hy + 45 * s), (x + 20 * s, hy + 112 * s), (x + 30 * s, hy + 44 * s)),
                rect(x + 22 * s, hy + 135 * s, 36 * s, 46 * s, 5 * s))


def zhou(x, y, s=1.0, arms="down", mood="flat") -> skia.Path:
    """小周：带工牌的火柴人。"""
    return join(stick(x, y, s, arms), badge(x, y, s), face(x, y, s, mood))


def lin(x, y, s=1.0, arms="down", mood="flat") -> skia.Path:
    """小林：戴眼镜的火柴人。"""
    hy = y - 290 * s
    g = join(circle(x - 16 * s, hy - 8 * s, 13 * s), circle(x + 16 * s, hy - 8 * s, 13 * s),
             P((x - 3 * s, hy - 8 * s), (x + 3 * s, hy - 8 * s)))
    return join(stick(x, y, s, arms), g, face(x, y, s, mood))


def sheet(x, y, w=200, h=250) -> skia.Path:
    """一张空白纸（右上折角）。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2 - 45, y - h / 2), (x + w / 2, y - h / 2 + 45), (x + w / 2, y + h / 2),
                  (x - w / 2, y + h / 2), close=True),
                P((x + w / 2 - 45, y - h / 2), (x + w / 2 - 45, y - h / 2 + 45), (x + w / 2, y - h / 2 + 45)))


def monster(x, y, r=120) -> skia.Path:
    """明天怪兽：毛茸茸的圆 + 两只圆眼 + 小短腿 + 一只手攥着日历页。肚皮留给红字“明天”。"""
    pts = []
    n = 44
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = r * (1 + 0.075 * (1 if i % 2 == 0 else -1))
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    body = P(*pts, close=True)
    eyes = join(circle(x - 0.33 * r, y - 0.42 * r, 0.2 * r), circle(x + 0.33 * r, y - 0.42 * r, 0.2 * r),
                circle(x - 0.29 * r, y - 0.38 * r, 0.06 * r), circle(x + 0.37 * r, y - 0.38 * r, 0.06 * r))
    legs = join(P((x - 0.4 * r, y + 0.95 * r), (x - 0.45 * r, y + 1.3 * r), (x - 0.25 * r, y + 1.3 * r)),
                P((x + 0.4 * r, y + 0.95 * r), (x + 0.45 * r, y + 1.3 * r), (x + 0.65 * r, y + 1.3 * r)))
    arm = P((x + 0.95 * r, y - 0.05 * r), (x + 1.3 * r, y - 0.35 * r))
    cal = join(rect(x + 1.45 * r, y - 0.6 * r, 0.5 * r, 0.6 * r, 0.06 * r),
               P((x + 1.2 * r, y - 0.78 * r), (x + 1.7 * r, y - 0.78 * r)),
               P((x + 1.32 * r, y - 0.5 * r), (x + 1.58 * r, y - 0.5 * r)),
               P((x + 1.32 * r, y - 0.38 * r), (x + 1.58 * r, y - 0.38 * r)))
    return join(body, eyes, legs, arm, cal)


def heart(x, y, r=40) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def shiver(x, y, h=150, n=6, w=22) -> skia.Path:
    """打寒颤的抖动线（竖向锯齿）。"""
    pts = [(x + (w if i % 2 else -w), y - h / 2 + h * i / n) for i in range(n + 1)]
    return P(*pts)


def spikes(x, y, r0, r1, n=18) -> skia.Path:
    parts = []
    for i in range(n):
        a = i / n * 2 * math.pi + 0.08
        parts.append(P((x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))))
    return join(*parts)


def ruler(x, y, w=1000, h=70) -> skia.Path:
    parts = [rect(x, y, w, h, 8)]
    for i in range(1, 20):
        xx = x - w / 2 + w * i / 20
        parts.append(P((xx, y - h / 2), (xx, y - h / 2 + (30 if i % 5 == 0 else 16))))
    return join(*parts)


def door(x, y, w=220, h=440) -> skia.Path:
    """门框：(x, y) 为地面中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                circle(x + w / 2 - 30, y - h / 2, 8))


def folder(x, y, w=440, h=320) -> skia.Path:
    return join(P((x - w / 2, y - h / 2), (x - w / 2 + 130, y - h / 2), (x - w / 2 + 160, y - h / 2 + 30),
                  (x + w / 2, y - h / 2 + 30), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2), close=True),
                P((x - w / 2, y - h / 2 + 70), (x + w / 2, y - h / 2 + 70)))


def gap_circle(x, y, r, start=25, sweep=310) -> skia.Path:
    """开了一个口的圈（缺口朝右）。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), start, sweep)
    return p


def _arc(c, x, y, r, frac, color, width):
    """从 12 点钟方向顺时针画出 frac 比例的圆，返回笔尖。"""
    p = skia.Path()
    if frac >= 1:
        p.addCircle(x, y, r)
        c.drawPath(p, marker(color, width))
        return None
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -90, 360 * frac)
    c.drawPath(p, marker(color, width))
    a = math.radians(-90 + 360 * frac)
    return x + r * math.cos(a), y + r * math.sin(a)


def back_out(f):
    """略冲过头再回来的缓动。"""
    s = 1.8
    f -= 1
    return f * f * ((s + 1) * f + s) + 1


# ---------------------------------------------------------------- 开局：两个人都没交（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


LIN0, ZHOU0 = (1350, 1400), (2250, 1400)
scene("两个人都没交", "灵魂拷问", (MID, 1000, 0.55), bars=2)
L(P((MID, 560), (MID, 1380)), 0, 0.9, BLACK, 8, sfx="wood_high")
T("季度总结", MID, 330, 100, k0=1, k1=2, sfx="pop")
L(join(lin(*LIN0, 0.9), sheet(1000, 1250)), 2, 2.9, BLUE, 9, sfx="wood_high")
L(join(zhou(*ZHOU0, 0.9), sheet(2600, 1250)), 3, 3.9, BLACK, 9, sfx="wood_high")
T("小林", LIN0[0], 1520, 80, BLUE, k0=4, k1=4.5, sfx="pop")
T("小周", ZHOU0[0], 1520, 80, k0=4.5, k1=5)
T("没交", 1000, 1250, 80, RED, k0=5, k1=5.5, sfx="rim")
T("没交", 2600, 1250, 80, RED, k0=5.5, k1=6)

scene("拖的理由不一样", "灵魂拷问", (MID, 950, 0.58))
T("？", LIN0[0], 960, 200, BLUE, k0=0, k1=0.8, sfx="pop")
T("？", ZHOU0[0], 960, 200, RED, k0=1, k1=1.8, sfx="pop")
L(monster(MID, 1520, 110), 2, 3, BLACK, 8, sfx="wood_low")
T("明天", MID, 1555, 70, RED, k0=3, k1=3.8, sfx="pop")
T("都拖着，各有各的怕", MID, 480, 80, k0=5, k1=7.25, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 3–9）

scene("书里讲了距离", "拖延心理学 · 书中观点", (MID, 2800, 0.75))
L(book(MID, 2560, 420, 280), 0, 1, BLACK, 10, sfx="wood_low")
T("拖延心理学", MID, 2330, 80, GREEN, k0=1, k1=2.25, sfx="pop")
T("博克和袁", MID, 2780, 60, k0=3, k1=4, sfx="pop")
L(ruler(MID, 3010, 1000, 64), 4, 5, BLACK, 7, sfx="wood_high")
L(join(lin(1180, 3150, 0.6), zhou(2420, 3150, 0.6)), 5, 6, BLUE, 8, sfx="pop")
T("和人的距离", MID, 3260, 80, RED, k0=6, k1=7.25, sfx="ding")

J4 = scene("各有一个安全圈", "书中观点 · 安全圈", (MID, 4700, 0.5), shake=[0, (5, 12.0)], flashes=[0])
CL, CR = (1125, 4770, 260), (2350, 4770)
T("安全圈", MID, 3950, 150, RED, k0=0, k1=0.9, sfx="kick")
L(join(stick(1000, 4900, 0.8, hair=True), face(1000, 4900, 0.8, "smile")), 1, 1.5, BLACK, 9, sfx="wood_high")
L(lin(1250, 4900, 0.8, mood="smile"), 1.5, 2, BLUE, 9)
L(zhou(2350, 4900, 0.8), 2, 2.9, BLACK, 9, sfx="pop")
L(circle(*CL), 3, 3.9, BLUE, 12, sfx="wood_high")


def push_ring(c, k, t):
    """小周的圈：第 4 拍先贴身画一个小圈，第 5 拍“砰”地推出去很远。"""
    t4, t49, t5 = b.t_of(J4, 4), b.t_of(J4, 4.9), b.t_of(J4, 5)
    if t < t5:
        return _arc(c, *CR, 170, clamp01((t - t4) / (t49 - t4)), RED, 12)
    f = clamp01((t - t5) / 0.4)
    r = 170 + 300 * back_out(f)
    if f < 1:
        for i in range(10):
            a = i / 10 * 2 * math.pi
            c.drawPath(P((CR[0] + (r + 30) * math.cos(a), CR[1] + (r + 30) * math.sin(a)),
                         (CR[0] + (r + 90) * math.cos(a), CR[1] + (r + 90) * math.sin(a))),
                       K.paint(RED, 1 - f, 8))
    _arc(c, *CR, r, 1, RED, 12)
    return None


b.custom(J4, 4, 5.6, push_ring, sfx="pop")
H(5, "kick", 0.9)
T("贴着人", CL[0], 5130, 90, BLUE, k0=6, k1=6.8, sfx="pop")
T("离人远", CR[0], 5340, 90, RED, k0=7, k1=7.8, sfx="pop")

scene("小林等人来帮", "书中观点 · 拖着等人帮", (1150, 4850, 0.85))
L(bubble(950, 4430, 360, 130, 1), 0, 0.9, BLACK, 8, sfx="wood_high")
T("我帮你看看", 950, 4430, 56, k0=1, k1=2.25, sfx="pop")
L(doc(1580, 4800, 170, 220, 1), 3, 3.9, BLUE, 8, sfx="wood_high")
T("没写完", 1580, 4970, 56, RED, k0=4, k1=4.8, sfx="pop")
L(heart(1125, 4600, 30), 5, 5.8, RED, 8, sfx="ding")
T("有人管，有人陪", 1150, 5280, 66, BLUE, k0=6, k1=7.75, sfx="pop")

scene("怕自己一个人", "书中观点 · 怕分开", (1150, 6200, 0.85))
L(P((650, 6550), (1600, 6550)), 0, 0.9, BLACK, 8, sfx="wood_high")
L(lin(1150, 6550, 0.85, mood="sad"), 1, 2, BLUE, 9, sfx="pop")
L(join(shiver(980, 6300), shiver(1320, 6300)), 2, 2.8, BLUE, 7, sfx="shaker")
L(bubble(1150, 5960, 380, 130, -1), 3, 3.8, BLACK, 8, sfx="wood_high")
T("全得自己扛", 1150, 5960, 56, k0=4, k1=5.25, sfx="pop")
T("怕一个人", 1150, 6700, 90, RED, k0=6, k1=7, sfx="ding")

scene("小周怕被管住", "书中观点 · 怕被管", (2480, 4850, 0.85))
L(sheet(2440, 4790, 110, 140), 0, 0.9, BLACK, 8, sfx="wood_high")
for n, (y, ex) in enumerate(((4550, 2785), (4770, 2840), (4990, 2785))):
    L(arrow((3080, y), (ex, y), 0.0, 36), 1 + n, 1.8 + n, RED, 8, sfx=("wood_high", "wood_low", "wood_high")[n])
T("改这里", 2960, 4440, 60, RED, k0=5, k1=5.8, sfx="pop")
T("怕被管住", 2930, 5260, 76, RED, k0=6, k1=7, sfx="ding")

ZC = (2450, 6290, 290)
scene("不交就没人评", "书中观点 · 怕靠近", (2500, 6200, 0.85))
L(zhou(2450, 6450, 0.85), 0, 0.9, BLACK, 9, sfx="wood_high")
L(circle(*ZC), 1, 1.9, BLACK, 10, sfx="wood_low")
L(spikes(ZC[0], ZC[1], ZC[2] + 10, ZC[2] + 60), 2, 2.9, RED, 8, sfx="rim")
L(join(stick(3000, 6450, 0.6, "point", hair=True), face(3000, 6450, 0.6, "flat")), 3, 3.8, BLACK, 8, sfx="pop")
L(bubble(2960, 6080, 260, 120, -1), 4, 4.8, BLACK, 8, sfx="wood_high")
T("看看？", 2960, 6080, 56, k0=5, k1=5.8, sfx="pop")
T("没法靠近", ZC[0], 6710, 84, RED, k0=6, k1=7, sfx="ding")

scene("一样拖，原因相反", "书中观点 · 两边对照", (1850, 6950, 0.43))
L(P((MID, 5900), (MID, 7180)), 0, 0.9, BLACK, 9, sfx="wood_high")
T("怕分开", 1150, 6980, 110, BLUE, k0=1, k1=1.8, sfx="pop")
T("怕靠近", 2450, 6980, 110, RED, k0=2, k1=2.8, sfx="pop")
L(monster(MID, 6420, 150), 3, 4, BLACK, 9, sfx="wood_low")
T("明天", MID, 6470, 96, RED, k0=4, k1=4.8, sfx="pop")
T("一样拖，原因相反", MID, 7330, 96, k0=5, k1=7, sfx="ding")

# ---------------------------------------------------------------- 做法：两边各走一步（场景 10–13）

scene("小林先自己写一段", "做法 · 左边", (1150, 8300, 0.85))
T("① 先自己写一段", 1150, 7850, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(lin(820, 8650, 0.8, "hold", "smile"), 2, 2.9, BLUE, 9, sfx="wood_high")
L(doc(1150, 8420, 220, 280, 4), 3, 3.9, BLACK, 8, sfx="wood_high")
L(check(1150, 8640, 34), 4, 4.6, GREEN, 9, sfx="ding")
L(join(door(1580, 8650), stick(1580, 8640, 0.6), face(1580, 8640, 0.6, "smile")), 5, 5.9, BLACK, 8, sfx="wood_low")
T("写完再找我", 1580, 8150, 56, k0=6, k1=7.25, sfx="pop")

ZG = (2330, 8480, 300)
scene("小周先给一个人看", "做法 · 右边", (2480, 8300, 0.85))
T("② 先给一个人看", 2480, 7850, 76, RED, k0=0, k1=1.75, sfx="pop")
L(zhou(2330, 8650, 0.8, "hold"), 2, 2.9, BLACK, 9, sfx="wood_high")
L(gap_circle(*ZG), 3, 3.9, BLACK, 10, sfx="wood_low")
L(join(stick(2880, 8650, 0.6, hair=True), face(2880, 8650, 0.6, "smile")), 4, 4.8, BLUE, 8, sfx="pop")
L(arrow((3000, 8330), (2700, 8420), 0.15, 36), 5, 5.8, GREEN, 9, sfx="wood_high")
T("半成品也行", 2480, 8120, 60, GREEN, k0=6, k1=7.25, sfx="pop")

J12 = scene("圈慢慢挪一挪", "做法 · 各挪一点", (MID, 10000, 0.55))
RINGS = [("小林", BLUE, 1150, 1450, 0, lin), ("小周", RED, 2450, 2150, 1, zhou)]
RY, RR = 9950, 300


def ring_fn(name, color, x0, x1, k_draw, who):
    def fn(c, k, t):
        td0, td1 = b.t_of(J12, k_draw), b.t_of(J12, k_draw + 0.9)
        tm0, tm1 = b.t_of(J12, 3), b.t_of(J12, 5)
        x = lerp(x0, x1, ease_in_out(clamp01((t - tm0) / (tm1 - tm0))))
        tip = _arc(c, x, RY, RR, clamp01((t - td0) / (td1 - td0)), color, 11)
        if t >= td1:
            c.drawPath(who(x, RY + 140, 0.7, mood="smile"), marker(BLACK if who is zhou else BLUE, 8))
            K.text(c, name, x, RY - 190, 76, "hand", color)
        return tip

    return fn


for name, color, x0, x1, kd, who in RINGS:
    b.custom(J12, kd, 5, ring_fn(name, color, x0, x1, kd, who), sfx="wood_high")
L(P((MID, 9500), (MID, 10400)), 2, 2.8, BLACK, 8, sfx="pop")
H(3, "shaker")
L(join(arrow((1050, 10340), (1550, 10340), 0.0, 40), arrow((2550, 10340), (2050, 10340), 0.0, 40)), 5, 5.9, GREEN, 9,
  sfx="wood_high")
T("各挪一点就好", MID, 10500, 90, GREEN, k0=6, k1=7.5, sfx="pop")

J13 = scene("两个人都交了", "结果 · 都交了", (MID, 11550, 0.7))
FD = (MID, 11850)
L(folder(*FD), 0, 1, BLACK, 10, sfx="wood_low")
L(join(lin(1200, 12150, 0.65, "up", "smile"), zhou(2400, 12150, 0.65, "up", "smile")), 1, 2, BLUE, 8, sfx="pop")
T("季度总结", FD[0], 11930, 64, k0=2, k1=3, sfx="pop")


def fly_fn(x0, y0, x1, y1, k0, color, rot):
    def fn(c, k, t):
        ta, tb = b.t_of(J13, k0), b.t_of(J13, k0 + 1)
        f = ease_in_out(clamp01((t - ta) / (tb - ta)))
        x, y = lerp(x0, x1, f), lerp(y0, y1, f) - 320 * 4 * f * (1 - f)
        s = lerp(1.0, 0.62, f)
        c.save()
        c.translate(x, y)
        c.rotate(rot * f)
        c.scale(s, s)
        c.drawPath(doc(0, 0, 150, 190, 3), marker(color, 9 / s))
        c.restore()
        return None

    return fn


b.custom(J13, 3, 4, fly_fn(1250, 11780, 1745, 11760, 3, BLUE, -10), sfx="wood_high")
H(4, "ding")
b.custom(J13, 5, 6, fly_fn(2350, 11780, 1855, 11760, 5, BLACK, 10), sfx="wood_high")
H(6, "ding")
T("两份都交了", FD[0], 11250, 90, GREEN, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：拉远看全板 → 推到评论区

FULL = (MID, 6900, 0.075)
CMT = (MID, 13050, 0.8)
scene("你像小林还是小周", "评论区见", FULL, bars=4)
b.move(J(), 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你更像小林，还是小周？", MID, 12960, 76, RED, k0=6, k1=8.75, sfx="pop")
T("下一讲：明明还有三天，怎么一眨眼没了", MID, 13130, 52, k0=9, k1=13.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "distance", "怕靠近怕分开", "有人拖着等人帮，有人拖着躲人", ACC, b.shots,
                 [f"{BOOK}第 5 章“心理舒适区：对亲近与疏远的恐惧”（英文版 Separation and Attachment，转述）",
                  "中译本：蒋永强、陆正芳译，中国人民大学出版社（湛庐文化）2009"],
                 "有人拖着等人帮|有人拖着【躲人】", SQUARE_SHOT,
                 ["书中观点为转述，不是逐字引文：拖延可以用来拉近和别人的距离——事情一直没做完，就会有人来帮、来管、来陪，"
                  "免得独自一人、独自承担；也可以用来推开别人——不把东西交出去，别人就没法提要求、没法评判、没法靠近；"
                  "每个人都在找让自己安心的距离（心理舒适区）。见第 5 章（中译本“心理舒适区：对亲近与疏远的恐惧”，"
                  "英文版 Separation and Attachment）。出处：Jane B. Burka & Lenora M. Yuen, Procrastination: Why You Do It, "
                  "What to Do About It Now（Da Capo Lifelong Books, 2008 修订版）；中译本《拖延心理学》（简·博克、莱诺拉·袁著，"
                  "蒋永强、陆正芳译，中国人民大学出版社 2009）。",
                  "小林、小周两人、季度总结、“我帮你看看”“改这里”等对话均为示意，不指向任何具体公司或个人；"
                  "“安全圈”的大小、两个圈往中间挪的画面为对书中观点的通俗化示意。",
                  "两条做法（小林先独立写完第一段再去找人；小周先挑一个信得过的人看半成品）为据书中思路整理的建议。"],
                 tags="#人际关系 #心理舒适区")
    return b.attach(ep)
