"""02 最后的自由（白板手绘版）：事情改不了，心情能自己定吗？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，场景 4 对上音乐 drop）。
叙事（F 两人对比）：周一早会，做了一个月的方案被砍 → 同一件事落在阿杰、阿宁两个人头上，竖线分屏 →
分屏下方一条路分成两叉，岔口一个问号：事情改不了，还剩什么能选？阿宁手里的小罗盘乱转 →
drop：岔口砸下红字“态度”，工牌、方案、钱包一一划掉，罗盘停在“态度”上（书中观点：人的一切都能被拿走，
只剩最后一样自由——在任何处境下选择自己的态度）→ 书中写到：营里有人把最后一块面包分给别人；
他和朋友约好每天编一个笑话，也会停下来看晚霞 → 一张图“处境改不了 / 态度自己定” →
阿杰这一天（骂、刷手机、喝闷酒）对照阿宁这一天（难受半小时、挑出能用的一页、拿给另一个组）→
一周后两条线分岔（示意）→ 做法（分两栏写 / 换个说法 / 找一个笑点或做好一件小事）→ 拉远看全板 → 评论区。
书中观点为转述（Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010，
第一部分 在集中营的经历）；例子为示意，做法据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, bubble, check, circle, clock, cross,
                               doc, face, hands_at, join, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#3E7C8C"
SQUARE_SHOT = 3                 # 场景 4：分岔路 + 阿杰、阿宁 + 红字“态度” + 罗盘
GREY = "#8C929B"                # 营里的场景、改不了的东西用灰色细线
PAPER = "#FBFBF9"

b = Board(size=(3600, 12400))


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

def screen(x, y, w=640, h=360) -> skia.Path:
    """会议室投影幕：幕布 + 顶杆 + 吊绳。"""
    return join(rect(x, y, w, h, 10), P((x - w / 2 - 30, y - h / 2 - 20), (x + w / 2 + 30, y - h / 2 - 20)),
                P((x, y - h / 2 - 20), (x, y - h / 2 - 70)))


def meeting(x, y, w=900) -> skia.Path:
    """会议桌（俯视成一条长桌边）+ 桌边三个圆脑袋。"""
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 40, y), (x - w / 2 + 40, y + 90)),
                P((x + w / 2 - 40, y), (x + w / 2 - 40, y + 90)),
                circle(x - w / 3, y - 70, 42), circle(x, y - 70, 42), circle(x + w / 3, y - 70, 42))


def road(cx, y0, y1, half=35) -> skia.Path:
    """直路段：两条平行线。"""
    return join(P((cx - half, y0), (cx - half, y1)), P((cx + half, y0), (cx + half, y1)))


def branch(cx, y, sign, half=35, dx=400, dy=320) -> skia.Path:
    """岔路一支：sign=-1 往左下，1 往右下。外线从路边出发，内线从岔口尖出发。"""
    outer = P((cx + sign * half, y), (cx + sign * (half + dx), y + dy))
    inner = P((cx, y + 70), (cx + sign * (dx - 10), y + dy + 60))
    return join(outer, inner)


def compass(x, y, r=50) -> skia.Path:
    """系列视觉角色：小罗盘的框（圆框 + 顶上小环 + 四个刻度）；指针由 needle_fn 画。"""
    parts = [circle(x, y, r), circle(x, y - r - 13, 12)]
    for i in range(4):
        a = i * math.pi / 2
        parts.append(P((x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72),
                       (x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9)))
    return join(*parts)


def needle_fn(x, y, r, a_stop, stop_at, spin=1.4):
    """罗盘指针：stop_at=(镜头, 拍) 之前一直乱转，到点“叮”地停在 a_stop（弧度，屏幕坐标），停下后轻轻晃两下。"""

    def fn(c, k, t):
        ts = b.t_of(*stop_at)
        if t < ts:
            dt = ts - t
            a = a_stop - 2 * math.pi * (spin * dt + 0.5 * dt * dt) + 0.6 * math.sin(dt * 5)
        else:
            dt = t - ts
            a = a_stop + 0.32 * math.exp(-7 * dt) * math.sin(dt * 26)
        c.drawCircle(x, y, r * 0.8, K.paint(PAPER))
        ln, w = r * 0.72, r * 0.2
        ca, sa = math.cos(a), math.sin(a)
        tip = (x + ca * ln, y + sa * ln)
        tail = (x - ca * ln * 0.8, y - sa * ln * 0.8)
        s1, s2 = (x - sa * w, y + ca * w), (x + sa * w, y - ca * w)
        K.poly(c, [tip, s1, s2], RED)
        half = skia.Path()
        half.moveTo(*tail)
        half.lineTo(*s1)
        half.lineTo(*s2)
        half.close()
        c.drawPath(half, K.paint(BLACK, 1, 4))
        K.dot(c, x, y, r * 0.09, BLACK)
        return None

    return fn


def slam_fn(s, x, y, size, color, cover=None):
    """大字砸下：从 1.6 倍缩到原大并淡入；cover=(x, y, w, h) 时先用白板底色盖住原来的字。"""

    def fn(c, k, t):
        if cover:
            K.rr(c, *cover, 0, PAPER)
        e = 1 - (1 - k) ** 3
        sc = 1 + 0.6 * (1 - e)
        c.save()
        c.translate(x, y)
        c.scale(sc, sc)
        K.text(c, s, 0, 0, size, "hand", color, min(1.0, k * 3))
        c.restore()
        return None

    return fn


def badge(x, y, s=1.0) -> skia.Path:
    """工牌：卡片 + 照片框 + 两行字 + 挂绳。"""
    return join(rect(x, y, 130 * s, 170 * s, 12 * s), rect(x, y - 30 * s, 60 * s, 60 * s, 6 * s),
                P((x - 40 * s, y + 30 * s), (x + 40 * s, y + 30 * s)), P((x - 30 * s, y + 55 * s), (x + 30 * s, y + 55 * s)),
                P((x - 25 * s, y - 85 * s), (x - 60 * s, y - 160 * s)), P((x + 25 * s, y - 85 * s), (x + 60 * s, y - 160 * s)))


def wallet(x, y, s=1.0) -> skia.Path:
    """钱包：外壳 + 翻盖 + 扣子。"""
    return join(rect(x, y, 170 * s, 110 * s, 14 * s), P((x + 85 * s, y - 25 * s), (x + 20 * s, y - 25 * s),
                                                         (x + 20 * s, y + 25 * s), (x + 85 * s, y + 25 * s)),
                circle(x + 45 * s, y, 8 * s))


def hut(x, y, w=380, h=150) -> skia.Path:
    """简笔木棚屋剪影：(x, y) 为地面中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 20, y - h), (x - w / 2 + 40, y - h - 60), (x + w / 2 - 40, y - h - 60), (x + w / 2 + 20, y - h)),
                P((x - 30, y), (x - 30, y - 85), (x + 30, y - 85), (x + 30, y)))


def snow_ground(x0, x1, y) -> skia.Path:
    parts = [P((x0, y), (x1, y))]
    for i in range(7):
        sx = x0 + 60 + i * (x1 - x0 - 120) / 6
        parts.append(circle(sx, y - 230 - (i % 3) * 55, 6))
    return join(*parts)


def give_hand(x, y, s=1.0) -> skia.Path:
    """从右边伸过来、掌心朝上的一只手（只画手和袖口）。(x, y) 为掌心。"""
    sleeve = join(P((x + 360 * s, y - 40 * s), (x + 140 * s, y - 30 * s)), P((x + 360 * s, y + 60 * s), (x + 140 * s, y + 55 * s)),
                  P((x + 140 * s, y - 30 * s), (x + 140 * s, y + 55 * s)))
    palm = skia.Path()
    palm.moveTo(x + 140 * s, y + 50 * s)
    palm.quadTo(x, y + 75 * s, x - 120 * s, y + 20 * s)
    palm.quadTo(x - 135 * s, y + 5 * s, x - 110 * s, y)
    palm.quadTo(x - 40 * s, y + 5 * s, x + 30 * s, y + 5 * s)
    thumb = skia.Path()
    thumb.moveTo(x + 140 * s, y - 20 * s)
    thumb.quadTo(x + 70 * s, y - 60 * s, x + 25 * s, y - 35 * s)
    return join(sleeve, palm, thumb)


def bread(x, y, s=1.0) -> skia.Path:
    """半块面包：圆顶 + 参差的掰口 + 两道刀口。(x, y) 为底边中点。"""
    p = skia.Path()
    p.moveTo(x - 100 * s, y)
    p.quadTo(x - 105 * s, y - 95 * s, x - 10 * s, y - 95 * s)
    p.quadTo(x + 60 * s, y - 95 * s, x + 80 * s, y - 55 * s)
    for dx, dy in ((68, -40), (86, -28), (70, -16), (84, -4), (76, 0)):
        p.lineTo(x + dx * s, y + dy * s)
    p.close()
    return join(p, P((x - 60 * s, y - 70 * s), (x - 40 * s, y - 40 * s)), P((x - 15 * s, y - 78 * s), (x + 5 * s, y - 48 * s)))


def heart(x, y, r=60) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def half_sun(x, y, r=150) -> skia.Path:
    """地平线上的半个太阳 + 几道光。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 180, 180)
    parts = [p]
    for i in range(5):
        a = math.pi + (i + 1) * math.pi / 6
        parts.append(P((x + math.cos(a) * (r + 30), y + math.sin(a) * (r + 30)),
                       (x + math.cos(a) * (r + 85), y + math.sin(a) * (r + 85))))
    return join(*parts)


def phone(x, y, w=80, h=130) -> skia.Path:
    return join(rect(x, y, w, h, 12), P((x - 12, y + h / 2 - 16), (x + 12, y + h / 2 - 16)))


def tumbler(x, y, s=1.0) -> skia.Path:
    """酒杯：矮杯身 + 酒面一道线。"""
    return join(P((x - 50 * s, y - 60 * s), (x - 40 * s, y + 60 * s), (x + 40 * s, y + 60 * s), (x + 50 * s, y - 60 * s)),
                P((x - 46 * s, y - 10 * s), (x + 46 * s, y - 10 * s)))


def smiley(x, y, r=130) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.55, y - r * 0.2, r * 1.1, r * 0.75), 20, 140)
    return join(circle(x, y, r), circle(x - r * 0.35, y - r * 0.25, r * 0.07), circle(x + r * 0.35, y - r * 0.25, r * 0.07), p)


def pair(x, y, s=0.3) -> skia.Path:
    """另一个组：两个小人并排。"""
    return join(stick(x - 45, y, s), stick(x + 45, y, s))


# ---------------------------------------------------------------- 开局：方案被砍（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("方案被砍了", "周一早会", (1800, 850, 0.85), bars=2)
L(screen(1800, 640), 0, 0.9, BLACK, 9, sfx="wood_high")
T("方案", 1800, 600, 76, k0=1, k1=1.8, sfx="pop")
L(join(P((1640, 690), (1960, 690)), P((1640, 740), (1900, 740))), 1.8, 2.0, BLACK, 7)
L(meeting(1800, 1010), 2, 2.9, BLACK, 9, sfx="wood_low")
T("做了一个月", 1800, 1150, 60, k0=3, k1=4.0, sfx="pop")
L(cross(1800, 640, 170), 4, 4.6, RED, 14, sfx="rim")
T("砍了", 2250, 430, 90, RED, k0=5, k1=5.8, sfx="kick")

DOC2 = (1800, 1560)
JIE, NING = (1450, 2330), (2150, 2330)         # 阿杰、阿宁脚底
S = 0.75
scene("同一件事，两个人", "两个人 · 同一件事", (1800, 2000, 0.85))
L(doc(*DOC2, 150, 190, 4), 0, 0.9, BLACK, 8, sfx="wood_high")
L(cross(*DOC2, 80), 1, 1.6, RED, 12, sfx="rim")
L(P((1800, 1700), (1800, 2440)), 2, 2.8, GREY, 7, sfx="wood_low")
L(stick(*JIE, S), 3, 3.8, BLACK, 10, sfx="pop")
L(face(*JIE, S, "flat"), 3.8, 4.0, BLACK, 8)
T("阿杰", JIE[0], 2420, 60, k0=4, k1=4.8, sfx="pop")
L(stick(*NING, S, "hold"), 5, 5.8, BLUE, 10, sfx="wood_high")
L(face(*NING, S, "flat"), 5.8, 6.0, BLUE, 8)
T("阿宁", NING[0], 2420, 60, BLUE, k0=6, k1=6.8, sfx="pop")
L(join(arrow((1720, 1640), (1500, 2040), 0.12, 34), arrow((1880, 1640), (2100, 2040), -0.12, 34)), 7, 7.9, RED, 8,
  sfx="tom")

FORK = (1800, 2700)                            # 岔口（路边分开处）
QM = (1800, 3000)                              # 岔口问号 → drop 时换成“态度”
CMP = (2275, 2230, 46)                         # 阿宁手里的罗盘
J_FORK = scene("还剩什么能选", "灵魂拷问", (1800, 2700, 0.72))
L(road(FORK[0], 2480, FORK[1]), 0, 0.9, BLACK, 8, sfx="wood_high")
L(branch(*FORK, -1), 1, 1.8, BLACK, 8, sfx="wood_low")
L(branch(*FORK, 1), 2, 2.8, BLACK, 8, sfx="wood_low")
T("？", *QM, 130, RED, k0=3, k1=3.8, sfx="pop")
L(compass(*CMP), 4, 4.8, BLACK, 7, sfx="wood_high")
J_DROP = J_FORK + 1
A_TAIDU = math.atan2(QM[1] - CMP[1], QM[0] - CMP[0])
b.custom(J(), 5, 5.5, needle_fn(*CMP, A_TAIDU, (J_DROP, 7)), sfx="shaker")
T("还剩什么能选？", 1800, 3170, 84, k0=6, k1=7.75, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 4–7）

scene("只剩一样能选", "活出生命的意义 · 书中观点", (1800, 2660, 0.78), shake=[0], flashes=[0])
b.custom(J(), 0, 0.4, slam_fn("态度", QM[0], QM[1] - 10, 150, RED, cover=(QM[0], QM[1], 150, 160)), sfx="kick")
OBJ = [(1290, 2720), (2330, 2640), (2350, 2950)]
L(badge(*OBJ[0], 0.95), 1, 1.8, GREY, 8, sfx="wood_high")
L(doc(*OBJ[1], 150, 180, 4), 2, 2.8, GREY, 8, sfx="wood_high")
L(wallet(*OBJ[2]), 3, 3.8, GREY, 8, sfx="wood_high")
for n, (ox, oy) in enumerate(OBJ):
    L(cross(ox, oy, 85), 4 + n, 4.6 + n, RED, 11, sfx="rim")
L(underline(1660, 1940, 3080, 10, 35), 7, 7.8, RED, 8)
H(7, "ding", 0.9, "罗盘停在“态度”")

GROUND = 4150
scene("有人把面包分出去", "书中写到 · 一块面包", (1100, 4250, 0.85))
L(snow_ground(520, 1680, GROUND), 0, 0.9, GREY, 6, sfx="wood_low")
L(hut(800, GROUND), 1, 1.8, GREY, 7, sfx="wood_high")
L(hut(1360, GROUND, 340, 130), 2, 2.8, GREY, 7, sfx="wood_high")
L(give_hand(1050, 4500, 1.1), 3, 3.9, BLACK, 8, sfx="wood_low")
L(bread(1010, 4500, 0.9), 4, 4.8, BLACK, 8, sfx="pop")
L(heart(1000, 4320, 40), 5, 5.8, RED, 8, sfx="ding")
T("最后一块面包", 1100, 4700, 66, k0=6, k1=7.5, sfx="pop")

HORIZON = 4420
scene("每天编一个笑话", "书中写到 · 笑话和晚霞", (2500, 4250, 0.85))
L(P((1960, HORIZON), (3060, HORIZON)), 0, 0.9, GREY, 7, sfx="wood_low")
L(half_sun(2780, HORIZON, 140), 1, 1.9, BLACK, 8, sfx="wood_high")
L(join(stick(2230, 4690, 0.5), stick(2390, 4690, 0.5)), 2, 2.9, GREY, 7, sfx="pop")
L(bubble(2180, 4170, 200, 120, 1), 3, 3.8, BLACK, 7, sfx="wood_high")
T("哈", 2180, 4170, 70, RED, k0=4, k1=4.8, sfx="pop")
T("每天编一个笑话", 2500, 3880, 66, k0=5, k1=6.75, sfx="tom")
T("也看晚霞", 2780, 4560, 60, k0=7, k1=8.0, sfx="pop")

CMP7 = (2075, 5740, 95)
scene("态度自己定", "书中观点 · 一张图", (1800, 5600, 0.85))
L(join(rect(1800, 5620, 1100, 760, 30), P((1800, 5270), (1800, 5970))), 0, 0.9, BLACK, 8, sfx="wood_high")
T("处境改不了", 1525, 5360, 64, GREY, k0=1, k1=2.25, sfx="pop")
T("方案被砍", 1525, 5640, 60, GREY, k0=3, k1=4.0, sfx="wood_low")
T("态度自己定", 2075, 5360, 64, RED, k0=4, k1=5.25, sfx="pop")
L(compass(*CMP7), 5.3, 5.9, BLACK, 8)
b.custom(J(), 5.9, 6.3, needle_fn(*CMP7, -math.pi / 2, (J(), 7), spin=1.0))
H(7, "ding", 0.9, "罗盘停在“态度自己定”")

# ---------------------------------------------------------------- 两个人的一天（场景 8–10，示意）

ROWS = (6550, 6800, 7050)
scene("阿杰骂了一天", "阿杰的一天", (1100, 6900, 0.85))
L(stick(620, 7250, 0.7), 0, 0.9, BLACK, 10, sfx="wood_high")
L(join(bubble(950, ROWS[0], 210, 120, -1), scribble(950, ROWS[0], 130, 60, 6)), 1, 1.8, BLACK, 7, sfx="rim")
T("骂了一上午", 1380, ROWS[0], 60, k0=1.8, k1=3.0)
L(phone(950, ROWS[1]), 3, 3.8, BLACK, 8, sfx="wood_high")
T("刷了一下午", 1380, ROWS[1], 60, k0=3.8, k1=5.0)
L(tumbler(950, ROWS[2]), 5, 5.8, BLACK, 8, sfx="pop")
T("下班喝闷酒", 1380, ROWS[2], 60, k0=5.8, k1=7.0)
L(face(620, 7250, 0.7, "sad"), 7, 7.6, BLACK, 8, sfx="wood_low")

scene("阿宁挑出能用的", "阿宁的一天", (2500, 6900, 0.85))
L(stick(3000, 7250, 0.7), 0, 0.9, BLUE, 10, sfx="wood_high")
L(join(clock(2150, ROWS[0], 60), hands_at(2150, ROWS[0], 60, 2, 30)), 1, 1.8, BLACK, 7, sfx="wood_low")
T("难受半小时", 2570, ROWS[0], 60, k0=1.8, k1=3.0)
L(join(doc(2150, ROWS[1], 110, 140, 3), check(2190, ROWS[1] + 20, 40)), 3, 3.8, GREEN, 8, sfx="pop")
T("挑出能用的", 2570, ROWS[1], 60, k0=3.8, k1=5.0)
L(pair(2150, ROWS[2] + 70), 5, 5.8, BLACK, 7, sfx="wood_high")
T("给另一个组", 2570, ROWS[2], 60, k0=6, k1=7.25, sfx="pop")
L(face(3000, 7250, 0.7, "smile"), 7.3, 7.8, BLUE, 8)

START = (1250, 8150)
scene("一周后，差远了", "一周后 · 示意", (1800, 8150, 0.8))
L(circle(*START, 16), 0, 0.4, BLACK, 9, sfx="wood_high")
T("那天", START[0], START[1] + 100, 56, k0=0.4, k1=1.0)
jie_line = skia.Path()
jie_line.moveTo(START[0] + 16, START[1])
jie_line.quadTo(1750, 8180, 2200, 8420)
L(jie_line, 1, 1.9, BLACK, 9, sfx="wood_low")
T("阿杰", 2330, 8440, 60, k0=2, k1=2.8, sfx="pop")
ning_line = skia.Path()
ning_line.moveTo(START[0] + 16, START[1])
ning_line.quadTo(1750, 8120, 2110, 7790)
L(ning_line, 3, 3.9, BLUE, 9, sfx="wood_high")
T("阿宁", 1760, 7900, 60, BLUE, k0=4, k1=4.8, sfx="pop")
L(rect(2250, 7720, 280, 120, 20), 5, 5.6, RED, 8, sfx="wood_high")
T("新项目", 2250, 7720, 58, RED, k0=5.6, k1=6.4)
T("一周后", 1450, 7690, 64, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 11–13，据书中思路整理）

scene("分两栏写", "第一步 · 分两栏", (1100, 9400, 0.85))
T("① 分两栏写", 1100, 8990, 76, BLUE, k0=0, k1=1.5, sfx="pop")
L(join(rect(1100, 9400, 1000, 620, 24), P((1100, 9110), (1100, 9690))), 2, 2.9, ORANGE, 8, sfx="wood_high")
T("改不了的", 850, 9200, 60, k0=3, k1=4.0, sfx="pop")
T("我能定的", 1350, 9200, 60, BLUE, k0=4, k1=5.0, sfx="pop")
T("方案没了", 850, 9400, 56, GREY, k0=5, k1=6.0, sfx="wood_low")
T("下一步做啥", 1350, 9400, 56, k0=6, k1=7.0, sfx="pop")
L(check(1350, 9560, 45), 7, 7.6, GREEN, 10, sfx="ding")

scene("换个说法", "第二步 · 换说法", (2550, 9400, 0.85))
T("② 换个说法", 2550, 8990, 76, BLUE, k0=0, k1=1.5, sfx="pop")
L(stick(2150, 9800, 0.65), 2, 2.8, BLUE, 10, sfx="wood_high")
L(face(2150, 9800, 0.65, "flat"), 2.8, 3.0, BLUE, 8)
L(bubble(2700, 9200, 460, 130, -1), 3, 3.8, BLACK, 8, sfx="pop")
T("方案白做了", 2700, 9200, 58, k0=3.8, k1=5.0)
L(P((2500, 9205), (2900, 9195)), 5, 5.6, RED, 10, sfx="rim")
T("方案没了，", 2700, 9420, 62, k0=6, k1=7.0, sfx="pop")
T("调研留下了", 2700, 9550, 62, RED, k0=7, k1=8.0, sfx="ding")

scene("找一个笑点", "第三步 · 找笑点", (1800, 10600, 0.85))
T("③ 找一个笑点", 1800, 10180, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(smiley(1430, 10520, 130), 2, 2.9, BLACK, 9, sfx="wood_high")
T("今天的笑点", 1430, 10770, 56, k0=3, k1=4.0, sfx="pop")
T("或", 1800, 10540, 64, k0=4, k1=4.8, sfx="wood_low")
L(rect(2170, 10540, 440, 200, 20), 5, 5.6, BLACK, 8, sfx="wood_high")
T("做好一件小事", 2170, 10540, 56, k0=5.6, k1=7.0)
L(check(2170, 10760, 45), 7, 7.6, GREEN, 10, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 6300, 0.1)                 # 第 0–4 拍：全板
TALK = (1800, 11700, 0.8)               # 第 4 拍起：评论区
J_END = scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J_END, 4, TALK, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("哪件改不了的事", 1800, 11520, 76, RED, k0=6, k1=7.75, sfx="pop")
T("你换了个态度？", 1800, 11650, 76, RED, k0=8, k1=9.75, sfx="pop")
T("下一讲：别再问图啥，生活在问你", 1800, 11830, 52, k0=10, k1=13.75, sfx="wood_high")
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "choice", "最后的自由", "事情改不了，心情能自己定吗？", ACC, b.shots,
                 [f"{BOOK}第一部分 在集中营的经历（转述）",
                  "中译本《活出生命的意义》，吕娜译，华夏出版社 2010"],
                 "事情改不了|心情能【自己定】", SQUARE_SHOT,
                 ["书中观点为转述（第一部分 在集中营的经历）：营里有人走过一间间棚屋去安慰别人，把最后一块面包分给别人；"
                  "由此作者说，人的一切都能被拿走，只剩最后一样自由——在任何处境下选择自己的态度。作者写到他和一个朋友约好"
                  "每天编一个笑话，营里的人也会停下来看晚霞。上屏均为转述，不是逐字引文。出处：Viktor E. Frankl, "
                  "Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010。",
                  "营里的画面只画雪地、灰线棚屋、一只递面包的手和地平线上的晚霞，为对书中段落的克制示意；"
                  "不画作者肖像，不画人物原型。",
                  "周一早会方案被砍、阿杰与阿宁各自的一天均为示意，不指向任何具体公司或个人；"
                  "“一周后两条线分岔”“新项目”为示意，不是数据；工牌、方案、钱包被划掉为对“一切都能被拿走”的示意。",
                  "三步做法（分两栏写“改不了的 / 我能定的”、给这件事换个说法、今天找一个笑点或做好一件小事）"
                  "为据书中思路整理的建议。"],
                 tags="#情绪管理 #职场")
    return b.attach(ep)
