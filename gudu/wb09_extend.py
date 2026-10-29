"""09 迈出第一步（白板手绘版）：想交朋友，第一步迈哪？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒。
叙事：切身问题开局（搬到新城市第三年，周末没人约；刷到一个读书会，想去又怕尴尬）→ 书中观点（亮书；
书末一章给的办法拼成 EASE 四个字母，本讲讲前两个：E 先迈一小步——帮个小忙、做志愿；A 有个计划——先挑低风险的小场合，
大型聚会往后放；画成一级一级的台阶）→ 身边的例子（帮同事弄卡纸的打印机、借梯子给邻居、六个人的小读书会）
→ 具体做法（每天帮一个小忙 / 列场合清单从最不怕的排起 / 定好时间和退路）
→ 评论区互动，预告下一讲（后两个字母）。
书中观点为转述：Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection (W. W. Norton, 2008)
第 14 章（中译本第三部分“14 个体困境的解药”）；中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009。
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, building, check, circle,
                               clock, cross, face, hands_at, join, marker, rect, scribble, stick, underline)
from whiteboard import engine as wb
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#3E7D6B"
SQUARE_SHOT = 6

b = Board(size=(3600, 11700))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


# ---------------------------------------------------------------- 本讲画法

def suitcase(x, y, w=170, h=200) -> skia.Path:
    """行李箱：(x, y) 为箱体中心。"""
    return join(rect(x, y, w, h, 18), P((x - 35, y - h / 2), (x - 35, y - h / 2 - 50), (x + 35, y - h / 2 - 50),
                                        (x + 35, y - h / 2)),
                P((x - w / 2 + 40, y - h / 2 + 30), (x - w / 2 + 40, y + h / 2 - 30)),
                P((x + w / 2 - 40, y - h / 2 + 30), (x + w / 2 - 40, y + h / 2 - 30)))


def house(x, y, w=420, h=300) -> skia.Path:
    """小屋：(x, y) 为底边中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 40, y - h), (x, y - h - 190), (x + w / 2 + 40, y - h)),
                P((x - 45, y), (x - 45, y - 150), (x + 45, y - 150), (x + 45, y)),
                rect(x + w / 4 + 10, y - h + 90, 80, 70, 6))


def phone(x, y, w=240, h=400) -> skia.Path:
    return join(rect(x, y, w, h, 26), P((x - 25, y + h / 2 - 26), (x + 25, y + h / 2 - 26)))


def calendar(x, y, w=560, h=440) -> skia.Path:
    return join(rect(x, y, w, h, 16), P((x - w / 2, y - h / 2 + 100), (x + w / 2, y - h / 2 + 100)),
                P((x, y - h / 2 + 100), (x, y + h / 2)),
                P((x - w / 4, y - h / 2 - 30), (x - w / 4, y - h / 2 + 30)),
                P((x + w / 4, y - h / 2 - 30), (x + w / 4, y - h / 2 + 30)))


def bubble(x, y, w, h, tail=-1) -> skia.Path:
    p = rect(x, y, w, h, 40)
    p.moveTo(x + tail * w * 0.15, y + h / 2)
    p.lineTo(x + tail * w * 0.3, y + h / 2 + 60)
    p.lineTo(x + tail * w * 0.02, y + h / 2)
    return p


def heart(x, y, r=80) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r)
    p.cubicTo(x - r * 1.6, y - r * 0.1, x - r * 0.7, y - r * 1.3, x, y - r * 0.45)
    p.cubicTo(x + r * 0.7, y - r * 1.3, x + r * 1.6, y - r * 0.1, x, y + r)
    return p


def cup(x, y, s=1.0) -> skia.Path:
    body = P((x - 55 * s, y - 70 * s), (x - 44 * s, y + 70 * s), (x + 44 * s, y + 70 * s), (x + 55 * s, y - 70 * s),
             close=True)
    return join(body, P((x - 52 * s, y - 40 * s), (x + 52 * s, y - 40 * s)))


def ellipse(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def printer(x, y, w=300, h=190) -> skia.Path:
    return join(rect(x, y, w, h, 18), P((x - w / 2 + 50, y - h / 2), (x - w / 2 + 50, y - h / 2 - 70),
                                        (x + w / 2 - 50, y - h / 2 - 70), (x + w / 2 - 50, y - h / 2)),
                P((x - w / 2 + 40, y + 20), (x + w / 2 - 40, y + 20)), circle(x + w / 2 - 40, y - 40, 14))


def ladder(x, y, h=440, w=130) -> skia.Path:
    """梯子：(x, y) 为中心。"""
    parts = [P((x - w / 2, y + h / 2), (x - w / 2 + 20, y - h / 2)), P((x + w / 2, y + h / 2), (x + w / 2 - 20, y - h / 2))]
    for i in range(5):
        yy = y - h / 2 + 50 + i * (h - 80) / 4
        parts.append(P((x - w / 2 + 12, yy), (x + w / 2 - 12, yy)))
    return join(*parts)


def bag(x, y, w=150, h=140) -> skia.Path:
    return join(P((x - w / 2, y - h / 2), (x - w / 2 + 15, y + h / 2), (x + w / 2 - 15, y + h / 2), (x + w / 2, y - h / 2)),
                P((x - 30, y - h / 2), (x - 20, y - h / 2 - 50), (x + 20, y - h / 2 - 50), (x + 30, y - h / 2)))


def door(x, y, w=220, h=380) -> skia.Path:
    """门：(x, y) 为中心。"""
    return join(rect(x, y, w, h, 8), circle(x + w / 2 - 40, y + 10, 12))


def heads(pts, r=34) -> skia.Path:
    return join(*(circle(x, y, r) for x, y in pts))


def stairs(x0, y0, n, w, rise) -> skia.Path:
    """台阶：从 (x0, y0) 起，n 级，每级宽 w、高 rise，向右上。"""
    pts = [(x0, y0)]
    x, y = x0, y0
    for i in range(n):
        x += w
        pts.append((x, y))
        if i < n - 1:
            y -= rise
            pts.append((x, y))
    pts.append((x, y0))
    return P(*pts, close=True)


def slam(j, kb, s, x, y, size, color=RED):
    """字母砸下：起拍时放大 1.8 倍，0.15 秒落定。"""

    def fn(c, k, t):
        t0 = b.t_of(j, kb)
        if t < t0:
            return None
        sc = 1 + 0.8 * (1 - ease_out(clamp01((t - t0) / 0.15)))
        K.text(c, s, x, y, size * sc, "hand", color, clamp01((t - t0) / 0.06))
        return None

    return fn


def climber(j, spots, beats=(1, 3, 5), s=0.5):
    """小人沿台阶往上跳：在 beats 指定的拍点分别落到 spots[0..2]（脚底坐标）。"""

    def fn(c, k, t):
        ts = [b.t_of(j, kb) for kb in beats]
        if t < ts[0]:
            return None
        i = max(n for n in range(len(spots)) if t >= ts[n])
        x, y = spots[i]
        if i + 1 < len(spots):
            f = clamp01((t - (ts[i + 1] - 0.3)) / 0.3)
            if f > 0:
                (x0, y0), (x1, y1) = spots[i], spots[i + 1]
                x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f - math.sin(f * math.pi) * 90
        c.drawPath(stick(x, y, s, "up"), marker(BLUE, 8))
        c.drawPath(face(x, y, s, "smile"), marker(BLUE, 6))
        return None

    return fn


# ---------------------------------------------------------------- 开局：新城市第三年（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


scene("搬来三年，周末没人约", "灵魂拷问", (950, 850, 0.85), bars=2)
L(join(building(520, 1150, 220, 320), building(760, 1150, 180, 260)), 0, 0.9, sfx="wood_high")
L(stick(1050, 1200, 0.9), 1, 1.8, sfx="pop")
L(face(1050, 1200, 0.9, "flat"), 1.8, 2.0)
L(suitcase(1260, 1080), 2, 2.8, sfx="pop")
T("搬来第三年", 950, 500, 72, RED, k0=3, k1=4.25, sfx="wood_high")
T("周末没人约", 1360, 720, 50, k0=5, k1=6.0, sfx="wood_low")

scene("想去又怕，第一步迈哪", "灵魂拷问", (950, 1950, 0.85), shake=[6], flashes=[6])
L(phone(600, 1800, 320, 520), 0, 1.0, sfx="wood_high")
T("周六读书会", 600, 1720, 52, GREEN, k0=1, k1=2.25, sfx="pop")
L(stick(1130, 2150, 0.85, "hold"), 2, 2.8, sfx="wood_high")
L(face(1130, 2150, 0.85, "flat"), 2.8, 3.0)
L(bubble(1250, 1640, 400, 150), 3, 3.8, BLACK, 8, sfx="pop")
T("去了说啥？", 1250, 1640, 52, k0=4, k1=5.25, sfx="wood_low")
T("第一步迈哪", 950, 2330, 80, RED, k0=6, k1=7.25, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 3–7）

scene("最后一章给了办法", "孤独是可耻的 · 第十四章", (1100, 3050, 0.9))
L(book(750, 3050, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 750, 2810, 70, GREEN, k0=1, k1=2.5, sfx="pop")
T("第十四章", 1390, 2880, 64, RED, k0=3, k1=4.0, sfx="pop")
L(arrow((1000, 3050), (1230, 3050), 0, 40), 4, 4.8, GREEN, 8, sfx="wood_high")
T("走出孤单的办法", 1400, 3060, 50, k0=5, k1=6.75, sfx="pop")
L(underline(1230, 1570, 3110, 10, 30), 7, 7.8, RED, 7, sfx="ding")

EASE = [("E", 2200), ("A", 2500), ("S", 2800), ("E", 3100)]
j_drop = scene("先迈一小步，有个计划", "书中观点 · 四个字母", (2650, 3150, 0.85), shake=[0], flashes=[0])
for n, (ch, x) in enumerate(EASE):
    b.custom(j_drop, n, n + 0.2, slam(j_drop, n, ch, x, 3000, 220),
             sfx=("kick", "tom", "tom", "kick")[n], gain=1.0 if n == 0 else 0.75)
H(0, "cymbal", 0.5)
L(circle(2200, 3000, 135), 4, 4.8, GREEN, 8, sfx="wood_high")
L(circle(2500, 3000, 135), 5, 5.8, GREEN, 8, sfx="wood_high")
T("先迈一小步", 2650, 3290, 60, GREEN, k0=6, k1=7.0, sfx="pop")
T("有个计划", 2650, 3400, 60, BLUE, k0=7, k1=8.0, sfx="pop")

scene("帮个小忙，做个志愿", "书中观点 · 先迈一小步", (1000, 4100, 0.85))
T("E · 先迈一小步", 1000, 3650, 70, BLUE, k0=0, k1=1.6, sfx="pop")
L(stick(580, 4400, 0.8, "point"), 2, 2.8, sfx="wood_high")
L(face(580, 4400, 0.8, "smile"), 2.8, 3.0)
L(cup(780, 4170, 0.6), 3, 3.8, BLACK, 8, sfx="pop")
T("帮个小忙", 660, 3860, 60, RED, k0=4, k1=5.0, sfx="pop")
L(heart(1300, 4130, 80), 5, 5.8, RED, 8, sfx="wood_high")
T("做志愿也算", 1300, 4380, 60, k0=6, k1=7.25, sfx="ding")

CROWD = [(2850 + c_ * 64 + (r % 2) * 30, 4060 + r * 56) for r in range(4) for c_ in range(5)]
scene("先挑小场合，大的往后放", "书中观点 · 有个计划", (2650, 4100, 0.85))
T("A · 有个计划", 2650, 3650, 70, BLUE, k0=0, k1=1.6, sfx="pop")
L(ellipse(2330, 4250, 380, 120), 2, 2.8, BLACK, 8, sfx="wood_high")
L(heads([(2190, 4150), (2330, 4120), (2470, 4150)]), 3, 3.8, BLUE, 7, sfx="pop")
T("小场合", 2330, 4420, 56, k0=4, k1=4.75, sfx="pop")
L(heads(CROWD, 22), 5, 5.9, BLACK, 5, sfx="shaker")
T("大型聚会", 3000, 3930, 56, k0=6, k1=7.0, sfx="pop")
T("以后再说", 3000, 4320, 50, RED, k0=7, k1=8.0, sfx="rim")

SX, SY, SW, SR = 1050, 5600, 500, 190
SPOTS = [(SX + SW * (i + 0.5), SY - SR * i) for i in range(3)]
j_st = scene("一级一级往上走", "书中观点 · 一张图", (1800, 5620, 0.65))
L(stairs(SX, SY, 3, SW, SR), 0, 1.0, BLACK, 9, sfx="wood_high")
b.custom(j_st, 2, 11, climber(j_st, SPOTS, beats=(2, 4, 6)), sfx="pop")
H(4, "pop")
H(6, "ding")
for n, w in enumerate(("帮小忙", "小场合", "常来往")):
    T(w, SX + SW * (n + 0.5), SY + 75, 66, GREEN if n < 2 else BLUE, k0=2 * n + 3, k1=2 * n + 3.8, sfx="wood_high")

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

scene("帮一把，约上午饭", "例子 · 职场", (900, 6450, 0.85))
L(printer(1150, 6570), 0, 1.0, sfx="wood_high")
T("卡纸！", 1150, 6250, 64, RED, k0=1, k1=1.8, sfx="shaker")
L(stick(720, 6800, 0.75, "shrug"), 2, 2.8, sfx="pop")
L(face(720, 6800, 0.75, "sad"), 2.8, 3.0)
L(stick(1400, 6800, 0.75, "point"), 3, 3.8, BLUE, sfx="wood_high")
L(face(1400, 6800, 0.75, "smile"), 3.8, 4.0, BLUE)
L(check(1150, 6570, 50), 4, 4.8, GREEN, 10, sfx="ding")
L(bubble(720, 6210, 400, 130, tail=0.1), 5, 5.8, BLACK, 7, sfx="pop")
T("一起吃午饭？", 720, 6210, 48, k0=6, k1=7.5, sfx="wood_low")

scene("借个梯子，认识了", "例子 · 生活", (2700, 6450, 0.85))
L(door(2350, 6600), 0, 1.0, sfx="wood_high")
L(stick(2620, 6800, 0.75, "point"), 1, 1.8, BLUE, sfx="pop")
L(face(2620, 6800, 0.75, "smile"), 1.8, 2.0, BLUE)
L(bubble(2700, 6200, 340, 120), 2, 2.8, BLACK, 7, sfx="pop")
T("有梯子吗？", 2700, 6200, 46, k0=3, k1=4.25, sfx="wood_low")
L(ladder(3080, 6550), 4, 4.9, sfx="wood_high")
L(bag(2830, 6740), 5, 5.8, BLACK, 8, sfx="pop")
L(heads([(2790, 6635), (2860, 6625), (2825, 6575)], 30), 5.8, 6.4, ORANGE, 8)
T("认识了", 2350, 6300, 56, GREEN, k0=7, k1=7.8, sfx="ding")

TABLE = (950, 7510)
SEATS = [(720, 7390), (850, 7355), (1050, 7355), (1180, 7390), (770, 7630), (1130, 7630)]
scene("都是小小一步", "例子 · 小场合", (950, 7400, 0.85), shake=[6])
L(ellipse(*TABLE, 520, 150), 0, 0.9, BLACK, 8, sfx="wood_high")
L(heads(SEATS), 1, 1.9, BLUE, 7, sfx="pop")
T("周六 · 六个人", 950, 7120, 60, k0=2, k1=3.4, sfx="pop")
L(phone(1430, 7430, 140, 230), 3.5, 4.0, BLACK, 7)
T("+2 好友", 1430, 7210, 54, GREEN, k0=4, k1=5.0, sfx="ding")
T("都是小小一步", 950, 7850, 80, RED, k0=6, k1=7.5, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

scene("每天帮一个小忙", "第一件 · 帮小忙", (950, 9000, 0.85))
T("① 每天帮个小忙", 950, 8590, 70, BLUE, k0=0, k1=1.6, sfx="pop")
L(stick(640, 9220, 0.75, "hold"), 2, 2.8, sfx="pop")
L(face(640, 9220, 0.75, "smile"), 2.8, 3.0)
L(cup(745, 9050, 0.45), 3, 3.8, BLACK, 7, sfx="wood_high")
T("帮带杯水", 1150, 8860, 60, k0=4, k1=5.0, sfx="pop")
T("一天一件", 1150, 9010, 60, RED, k0=6, k1=7.0, sfx="ding")

LIST = ("楼下打招呼", "小读书会", "大派对")
scene("从最不怕的排起", "第二件 · 列清单", (950, 9850, 0.85))
T("② 列个场合清单", 950, 9450, 70, BLUE, k0=0, k1=1.6, sfx="pop")
L(arrow((560, 9640), (560, 10080), 0, 34), 2, 2.8, GREEN, 8, sfx="wood_high")
T(LIST[0], 950, 9680, 60, k0=3, k1=4.25, sfx="pop")
T(LIST[1], 950, 9860, 60, k0=4.5, k1=5.5)
T(LIST[2], 950, 10040, 60, BLUE, k0=6, k1=6.8, sfx="rim")
L(check(1260, 9670, 40), 7, 7.6, GREEN, 9, sfx="ding")

scene("定好时间，留条退路", "第三件 · 定时间", (2650, 9850, 0.85))
T("③ 定好时间和退路", 2650, 9450, 66, BLUE, k0=0, k1=1.8, sfx="pop")
L(clock(2350, 9840, 120), 2, 2.8, sfx="wood_high")
L(hands_at(2350, 9840, 120, 3, 0), 2.8, 3.0, RED, 10)
T("待一小时", 2350, 10060, 56, k0=3, k1=4.0, sfx="pop")
L(door(2980, 9840), 4, 4.8, sfx="wood_high")
T("想走就走", 2980, 10120, 56, GREEN, k0=6, k1=7.0, sfx="ding")

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：先看全板，再推到评论区

FULL = (1800, 4900, 0.17)
TALK = (1800, 11000, 0.8)
j_end = scene("评论区聊聊", "评论区见", FULL, bars=4)
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")
T("你这周先做哪件？", 1800, 10920, 80, RED, k0=6, k1=8.0, sfx="pop")
T("下一讲：交朋友，该找谁、怎么想？", 1800, 11080, 50, k0=9, k1=11.5, sfx="wood_high")
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")

_camera = wb.camera


def _end_camera(board, T):
    """最后一个场景：第 0–4 拍看全板，第 4 拍起 1.1 秒推到评论区（只作用于本讲白板）。"""
    if board is not b or board.ep is None or board.ep.shot_at(T) != j_end:
        return _camera(board, T)
    t4 = b.t_of(j_end, 4)
    if T < t4:
        return _camera(board, T)
    cx0, cy0, z0, _, _ = _camera(board, t4)
    k = ease_in_out(clamp01((T - t4) / 1.1))
    return (lerp(cx0, TALK[0], k), lerp(cy0, TALK[1], k),
            math.exp(lerp(math.log(z0), math.log(TALK[2]), k)), 0.0, 0.0)


wb.camera = _end_camera


def build():
    ep = episode(9, "extend", "迈出第一步", "想交朋友，第一步迈哪？", ACC, b.shots,
                 [f"{BOOK}第 14 章 · EASE 中的 Extend yourself 与 Action plan（转述）",
                  "中译本：焦梦津译，中国人民大学出版社 2009（第三部分“14 个体困境的解药”）"],
                 "想交朋友|第一步【迈哪】", 6,
                 ["书中观点均为转述：书末第 14 章（中译本“个体困境的解药”）给出走出孤独的办法，作者用 EASE 四个字母概括；"
                  "本讲讲前两个——Extend yourself（先迈一小步，比如做志愿、帮别人一个小忙）和 Action plan（有个计划，"
                  "先从低风险的小场合开始，别一上来就去大型社交）；后两个 Selection、Expect the best 留到下一讲。"
                  "出处：John T. Cacioppo & William Patrick, Loneliness: Human Nature and the Need for Social Connection "
                  "(W. W. Norton, 2008)，中译本《孤独是可耻的》（约翰·卡乔波、威廉·帕特里克著，焦梦津译，中国人民大学出版社 "
                  "2009）。上屏均为转述，不是逐字引文。",
                  "搬到新城市三年、读书会、打印机卡纸、借梯子、六个人的读书会均为现实场景示意，不指向任何具体公司"
                  "或个人；台阶图为对书中“先小后大”思路的通俗化示意；人数、时间为示意，不是数据。",
                  "三件做法（每天帮一个小忙、列场合清单从最不怕的排起、定好时间和退路）为据书中思路整理的建议。"],
                 tags="#交朋友 #社交")
    return b.attach(ep)
