"""03 孤独伤身（白板手绘版）：一个人住久了，为什么总睡不好？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（2026-10 观众反馈“动画切换太快，来不及看”后改为慢速讲解版）。
叙事：切身问题开局（一个人住出租屋半夜醒 → 白天上班犯困 → 抛问题）→ 亮书《孤独是可耻的》、卡乔波 →
drop：孤单久了，身体会被慢慢磨损 → 书中观点（作者团队比较孤独和不孤独的两群人：孤独的人睡得更浅、夜里更容易短暂醒来，
压力反应更大、血压更高；第六章“孤独的磨损”——一两天看不出来，日子久了才显出来；收成一张图）→
身边的例子（外派到新城市、周末两天没说话、老爸一个人在老家；最后连到同一个原因）→
具体做法（睡前跟人说说话 / 每周固定见一次人 / 先迈一小步）→ 评论区互动 + 下一讲预告。
书中观点为转述（Cacioppo & Patrick, Loneliness, 2008，第六章；中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社
2009）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, building, circle, clock,
                               desk, face, hands_at, join, marker, rect, stick, underline)
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#5B6FA8"
SQUARE_SHOT = 0

b = Board(size=(3600, 12800))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.6 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.6, 0.25 * len(s.replace(' ', ''))) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def E(k0, k1, x, y, w, h):
    b.erase(len(b.shots) - 1, k0, k1, x, y, w, h)


# ---------------------------------------------------------------- 本讲画法

def moon(x, y, r=70) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def phone(x, y, w=110, h=190) -> skia.Path:
    return join(rect(x, y, w, h, 16), P((x - 18, y + h / 2 - 22), (x + 18, y + h / 2 - 22)))


def bed(x, y, w=440) -> skia.Path:
    """床（侧视）：(x, y) 为床面中点。"""
    return join(P((x - w / 2, y - 120), (x - w / 2, y + 90)), P((x + w / 2, y - 40), (x + w / 2, y + 90)),
                P((x - w / 2, y + 40), (x + w / 2, y + 40)), rect(x - w / 2 + 80, y - 10, 110, 50, 20),
                P((x - w / 2 + 150, y + 10), (x - w / 2 + 170, y - 40), (x + w / 2, y - 40), (x + w / 2, y + 40)))


def head_on(x, y, w=440, awake=True) -> skia.Path:
    """躺在 bed(x, y, w) 枕头上的头；awake 时睁着眼。"""
    hx, hy = x - w / 2 + 80, y - 72
    p = circle(hx, hy, 38)
    if awake:
        p.addCircle(hx - 13, hy - 6, 5)
        p.addCircle(hx + 13, hy - 6, 5)
    else:
        p.moveTo(hx - 20, hy - 4)
        p.lineTo(hx - 6, hy - 4)
        p.moveTo(hx + 6, hy - 4)
        p.lineTo(hx + 20, hy - 4)
    return p


def window(x, y, w=220, h=180) -> skia.Path:
    return join(rect(x, y, w, h, 8), P((x, y - h / 2), (x, y + h / 2)), P((x - w / 2, y), (x + w / 2, y)))


def heart(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + 90 * s)
    p.cubicTo(x - 160 * s, y - 10 * s, x - 90 * s, y - 120 * s, x, y - 50 * s)
    p.cubicTo(x + 90 * s, y - 120 * s, x + 160 * s, y - 10 * s, x, y + 90 * s)
    return p


def house(x, y, w=360, h=260) -> skia.Path:
    """平房：(x, y) 为墙体中心。"""
    return join(rect(x, y, w, h, 6), P((x - w / 2 - 40, y - h / 2), (x, y - h / 2 - 170), (x + w / 2 + 40, y - h / 2)),
                P((x - 40, y + h / 2), (x - 40, y + h / 2 - 120), (x + 40, y + h / 2 - 120), (x + 40, y + h / 2)),
                rect(x + 110, y - 20, 70, 70, 4))


def arc(x, y, r, a0, sweep) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), a0, sweep)
    return p


def smooth(*pts) -> skia.Path:
    p = skia.Path()
    p.moveTo(*pts[0])
    for i in range(1, len(pts) - 1):
        mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
        p.quadTo(pts[i][0], pts[i][1], mx, my)
    p.lineTo(*pts[-1])
    return p


def needle(x, y, r, a_from, a_to):
    """压力表指针：从 a_from 度转到 a_to 度（屏幕角度，0 向右，180 向左）。"""

    def fn(c, k, t):
        a = math.radians(a_from + (a_to - a_from) * ease_out(clamp01(k)))
        ex, ey = x + r * math.cos(a), y + r * math.sin(a)
        c.drawPath(P((x, y), (ex, ey)), marker(RED, 11))
        c.drawCircle(x, y, 16, marker(RED, 10))
        return ex, ey

    return fn




# ---------------------------------------------------------------- 场景节奏
# 慢速讲解版：场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍，第 0–8 拍逐步画完、最后 4 拍停住），
# 场景 14 为 4 小节。元素一拍一个，起笔落在整数拍并配音效。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 开局（场景 1–2）

scene("一个人住，半夜又醒", "灵魂拷问", (950, 850, 0.85), bars=2)
L(rect(950, 900, 1100, 800, 30), 0, 0.9, BLACK, 9, sfx="wood_high")
L(join(window(650, 680), moon(650, 680, 55)), 1, 1.9, BLACK, 8, sfx="pop")
L(join(bed(800, 1150, 480), head_on(800, 1150, 480)), 2, 2.9, sfx="wood_high")
L(join(clock(1280, 700, 95), hands_at(1280, 700, 95, 3, 0)), 3, 3.9, sfx="pop")
T("出租屋", 950, 420, 72, k0=4, sfx="pop")
T("醒了", 760, 960, 66, RED, k0=5, k1=5.7, sfx="rim")

scene("白天犯困，怎么老睡不好", "灵魂拷问", (2650, 1350, 0.7))
T("下午 3 点", 2650, 800, 80, RED, k0=0, k1=1.0, sfx="rim")
L(desk(2900, 1150, 420), 1, 1.9, sfx="wood_high")
L(join(stick(2450, 1300, 0.8), face(2450, 1300, 0.8, "sad")), 2, 2.9, sfx="pop")
T("Zzz", 2560, 930, 64, BLUE, k0=3, k1=3.8)
T("？", 2650, 1600, 260, RED, k0=4, k1=4.8, sfx="rim")
T("怎么老睡不好", 2650, 1850, 100, k0=5, sfx="pop")
L(underline(2330, 2970, 1935, 12, 40), 7, 7.8, RED, 9, sfx="ding")

# ---------------------------------------------------------------- 亮书 + drop（场景 3–4）

scene("有本书比过两群人", "孤独是可耻的", (1050, 3000, 0.85))
L(book(750, 2800, 420, 280), 0, 0.9, sfx="wood_low")
T("孤独是可耻的", 750, 2550, 76, GREEN, k0=1, sfx="pop")
T("约翰 · 卡乔波", 750, 3040, 50, k0=2.5, k1=3.7)
L(join(*[stick(x, 3440, 0.45) for x in (600, 720, 840)]), 4, 4.8, BLUE, 8, sfx="wood_high")
T("孤独的人", 720, 3200, 54, BLUE, k0=4.8, k1=5.8)
L(join(*[stick(x, 3440, 0.45) for x in (1260, 1380, 1500)]), 6, 6.8, BLACK, 8, sfx="pop")
T("不孤独的人", 1380, 3200, 54, k0=6.8, k1=8.0)

scene("孤单久了，身体会被磨损", "drop · 孤独伤身", (2650, 3000, 0.85), shake=[0], flashes=[0])
T("孤单久了", 2650, 2620, 130, RED, k0=0, k1=1.0, sfx="kick")
L(stick(2550, 3250, 1.0), 1, 1.9, BLACK, 10, sfx="wood_high")
L(face(2550, 3250, 1.0, "sad"), 2, 2.6, BLACK, 9, sfx="pop")
L(arrow((2880, 2930), (2880, 3220), 0, 45), 3, 3.9, RED, 11, sfx="rim")
T("身体被慢慢磨损", 2650, 3420, 84, k0=4, sfx="pop")
L(underline(2350, 2950, 3485, 12, 40), 6, 6.8, RED, 9, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 5–7）


def wave_y(x):
    return 4410 + 34 * math.sin((x - 400) / 70)


WAVE = [(x, wave_y(x)) for x in range(400, 1521, 35)]
scene("睡得浅，还老醒", "书中观点 · 睡眠", (950, 4370, 0.8))
T("睡得浅", 950, 3950, 150, RED, k0=0, k1=0.8, sfx="rim")
L(P((400, 4600), (1500, 4600)), 1, 1.9, BLACK, 8, sfx="wood_high")
T("23:00", 450, 4680, 56, k0=2, k1=2.6, sfx="pop")
T("7:00", 1450, 4680, 56, k0=2.6, k1=3.0)
L(smooth(*WAVE), 3, 3.9, BLUE, 9, sfx="pop")
L(join(*[P((x, wave_y(x)), (x, 4180)) for x in (630, 880, 1140, 1370)]), 4, 4.9, RED, 10, sfx="rim")
T("夜里短暂醒来", 950, 4790, 58, RED, k0=6, sfx="pop")

GX, GY = 2350, 4500
scene("压力大，血压也高", "书中观点 · 压力与血压", (2650, 4370, 0.85))
L(join(arc(GX, GY, 210, 180, 180), P((GX - 210, GY), (GX + 210, GY))), 0, 0.9, BLACK, 9, sfx="wood_high")
b.custom(len(b.shots) - 1, 1, 2, needle(GX, GY, 170, 200, 330), sfx="rim")
T("压力大", GX, GY + 120, 72, RED, k0=2, sfx="pop")
L(heart(2950, GY - 70, 0.95), 3, 3.9, RED, 10, sfx="wood_high")
L(arrow((3170, GY + 50), (3170, GY - 190), 0, 40), 4, 4.8, RED, 10, sfx="rim")
T("血压高", 2950, GY + 120, 72, RED, k0=5, sfx="pop")

C = 5650                        # 一张图：电量格 = 身体
BAT = (1680, C - 200)
BARS = [BAT[0] + d for d in (-165, -55, 55, 165)]
scene("日子久了，都落在身上", "书中观点 · 一张图", (1800, C, 0.8))
T("第六章 孤独的磨损", 1800, C - 470, 64, GREEN, k0=0, k1=1.8, sfx="pop")
L(join(rect(*BAT, 480, 210, 24), rect(BAT[0] + 262, BAT[1], 44, 90, 10),
       *[rect(x, BAT[1], 90, 150, 10) for x in BARS]), 2, 2.9, BLACK, 9, sfx="wood_high")
for n, (w, col) in enumerate((("睡得浅", BLUE), ("压力大", RED), ("血压高", RED))):
    T(w, 2300, C - 330 + n * 130, 56, col, k0=3 + n, k1=3.75 + n, sfx="pop")
L(join(*[arrow((2200, C - 330 + n * 130), (1985, BAT[1]), 0, 30) for n in range(3)]), 6, 6.8, RED, 8,
  sfx="wood_high")
E(7, 7.6, BARS[3], BAT[1], 110, 175)
E(7, 7.6, BARS[2], BAT[1], 110, 175)
T("日子久了", 1680, C + 60, 80, RED, k0=7, k1=8.0, sfx="rim")

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

R1, R2 = 7000, 8400              # 两行卡片间距 1400，避免上一行的字漏进页眉
scene("外派，下班没人说话", "例子 · 外派", (950, R1 + 30, 0.85))
L(rect(950, R1, 1200, 860, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("外派到新城市", 950, R1 - 300, 72, BLUE, k0=1, sfx="pop")
L(building(650, R1 + 270), 3, 3.9, sfx="wood_high")
L(join(stick(1000, R1 + 320, 0.8, "hold"), face(1000, R1 + 320, 0.8, "sad")), 4, 4.9, sfx="pop")
L(rect(1270, R1 - 80, 260, 140, 40), 5, 5.5, BLACK, 8, sfx="rim")
T("……", 1270, R1 - 80, 60, k0=5.5, k1=6.0)
T("夜里醒 3 回", 1300, R1 + 80, 56, RED, k0=6, sfx="pop")

scene("周末没开口，夜里醒着", "例子 · 周末", (2650, R1 + 30, 0.85))
L(rect(2650, R1, 1200, 860, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
L(join(rect(2420, R1 - 190, 190, 190, 14), rect(2660, R1 - 190, 190, 190, 14)), 1, 1.9, BLACK, 8, sfx="pop")
T("六", 2420, R1 - 180, 80, k0=2, k1=2.4, sfx="pop")
T("日", 2660, R1 - 180, 80, k0=2.4, k1=2.8)
T("0 句话", 3000, R1 - 150, 76, RED, k0=3, k1=3.9, sfx="rim")
L(moon(3150, R1 + 80, 60), 4, 4.9, BLUE, 8, sfx="wood_high")
L(join(bed(2900, R1 + 280, 380), head_on(2900, R1 + 280, 380)), 5, 5.9, sfx="pop")
T("1:00 还醒着", 2830, R1 + 60, 52, RED, k0=6, sfx="rim")

scene("都少个说话的人", "身边的例子", (1800, R2 + 120, 0.8), shake=[6])
L(rect(1800, R2, 1200, 860, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
L(house(1570, R2 + 200), 1, 1.9, sfx="pop")
T("老家", 1570, R2 - 230, 64, k0=2, k1=2.6, sfx="pop")
L(join(stick(2030, R2 + 350, 0.8), face(2030, R2 + 350, 0.8, "flat"), P((2100, R2 + 200), (2120, R2 + 350))),
  3, 3.9, sfx="wood_high")
L(rect(2060, R2 - 250, 340, 120, 40), 4, 4.6, BLACK, 8, sfx="pop")
T("夜里老醒", 2060, R2 - 250, 56, k0=4.6, k1=5.6)
T("都少个说话的人", 1800, R2 + 600, 96, RED, k0=6, sfx="rim")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

P1, P2 = 9900, 11300
scene("睡前跟人说几句", "第一步 · 说说话", (950, P1 + 30, 0.85))
L(rect(950, P1, 1200, 860, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("① 睡前说说话", 950, P1 - 300, 76, BLUE, k0=1, sfx="pop")
L(phone(640, P1 + 10), 3, 3.8, BLACK, 9, sfx="pop")
L(rect(1030, P1 - 40, 420, 150, 40), 4, 4.6, BLUE, 8, sfx="wood_high")
T("今天咋样？", 1030, P1 - 40, 56, BLUE, k0=4.6, k1=5.85)
T("10 分钟就够", 950, P1 + 280, 64, RED, k0=6, sfx="rim")

scene("每周见一次人", "第二步 · 见人", (2650, P1 + 30, 0.85))
L(rect(2650, P1, 1200, 860, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("② 每周见一次人", 2650, P1 - 300, 72, BLUE, k0=1, sfx="pop")
L(join(*[rect(2290 + n * 120, P1 - 90, 100, 100, 10) for n in range(7)]), 3, 3.9, BLACK, 7, sfx="wood_high")
L(circle(2530, P1 - 90, 72), 4, 4.6, RED, 9, sfx="pop")
T("周三 午饭", 2650, P1 + 100, 60, RED, k0=4.6, k1=5.6)
L(join(stick(2460, P1 + 380, 0.55, "hold"), face(2460, P1 + 380, 0.55, "smile")), 6, 6.7, BLACK, 8, sfx="wood_high")
L(join(stick(2840, P1 + 380, 0.55, "hold"), face(2840, P1 + 380, 0.55, "smile")), 6.7, 7.4, BLUE, 8)
L(join(P((2530, P1 + 250), (2770, P1 + 250)), P((2570, P1 + 250), (2570, P1 + 380)),
       P((2730, P1 + 250), (2730, P1 + 380))), 7.4, 8.0, BLACK, 9)

scene("先迈一小步", "第三步 · 一小步", (1800, P2 + 30, 0.85))
L(rect(1800, P2, 1200, 860, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("③ 先迈一小步", 1800, P2 - 300, 72, BLUE, k0=1, sfx="pop")
L(stick(1500, P2 + 250, 0.8, "hold"), 3, 3.9, BLACK, 9, sfx="wood_high")
L(join(rect(1670, P2 + 100, 130, 110, 8), P((1605, P2 + 70), (1735, P2 + 70))), 4, 4.7, BLACK, 8, sfx="pop")
L(join(stick(2300, P2 + 370, 0.6), face(2300, P2 + 370, 0.6, "smile")), 5, 5.9, BLUE, 8, sfx="wood_high")
T("帮邻居收快递", 2000, P2 - 110, 60, k0=6, sfx="rim")

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：拉远看全板，再写评论区

CM = P2 + 780
scene("评论区聊聊", "评论区见", (1800, 10930, 0.3), bars=4)
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")
T("你一个人住多久了？", 1800, CM, 230, RED, k0=5, sfx="pop")
T("下一讲：越孤单，为什么越不想见人？", 1800, CM + 280, 150, k0=8, sfx="wood_high")
b.hit(len(b.shots) - 1, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "health", "孤独伤身", "一个人住久了，为什么总睡不好？", ACC, b.shots,
                 [f"{BOOK}第六章 · 孤独的磨损（转述）", "中译本：《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009"],
                 "一个人住久了|为什么总【睡不好】", 0,
                 ["书中观点均为转述：作者团队比较孤独与不孤独的人，发现孤独的人睡眠质量更差、夜里更容易短暂醒来，"
                  "压力反应和血压等指标更差；长期孤独让身体被慢慢磨损（第六章“孤独的磨损”）。上屏均为转述，不是逐字引文，"
                  "片中不给具体研究数字。出处：John T. Cacioppo & William Patrick, Loneliness: Human Nature and the Need for "
                  "Social Connection (W. W. Norton, 2008)，中译本《孤独是可耻的》（约翰·卡乔波、威廉·帕特里克著，焦梦津译，"
                  "中国人民大学出版社 2009）。",
                  "出租屋半夜醒、外派到新城市、周末两天没说话、老爸一个人在老家均为现实场景示意，"
                  "不指向任何具体公司或个人；片中钟点、醒来次数、电量格、压力表、睡眠曲线均为示意，不是数据。",
                  "三件事（睡前跟人说说话、每周固定见一次人、先迈一小步）为据书中思路整理的建议"
                  "（“先迈一小步”对应第十四章 EASE 中的 Extend yourself）。"],
                 tags="#睡眠 #健康")
    return b.attach(ep)
