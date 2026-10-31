"""01 快与慢（白板手绘版）：球拍和球，你算对了吗？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（C 复刻实验）：开局直接出题（球拍 + 球 = 1.10 元，球拍比球贵 1 元，球多少钱？）→ 闹钟走三格，让观众先说个数 →
快快（系统1）举手抢答“1毛！” → drop：红叉砸在“1毛”上，慢慢（系统2）推推眼镜验算 1.10 + 0.10 = 1.20，
正确答案“球 5分 · 球拍 1.05” → 亮书《思考，快与慢》：名校学生一半以上也答 1毛 →
书中观点（两个系统：快快自动、快、不费劲，慢慢要专心、费劲；快快的活：看脸知道生气、2 + 2 = 4；
慢慢的活：17 × 24 要停下来算，瞳孔放大；慢慢懒，常对快快的答案直接盖章放行）→
例子（报价单扫一眼就签、领导问“一天能做完吧”嘴比脑子快）→ 做法（写下来算一遍 / 晚点回复）→ 拉远看全板 → 评论区互动。
书中观点为转述：丹尼尔·卡尼曼《思考，快与慢》（Thinking, Fast and Slow，2011）第 1–3 章；
中译本胡晓姣、李爱民、何梦莹译，中信出版社 2012。例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               doc, face, hands_at, join, marker, rect, stick, underline)
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode, kuai, man

ACC = "#C2603A"
SQUARE_SHOT = 3                 # 场景 4：快快的“1毛”被红叉，慢慢验算

b = Board(size=(3600, 9300))

# 白板分区：左列 / 右列，每行相隔 1300（上一行的字不漏进页眉带）
XL, XR = 950, 2650
ROW = [850, 2150, 3450, 4750, 6050, 7350, 8650]


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

def racket(x, y, s=1.0) -> skia.Path:
    """球拍 + 球：(x, y) 为拍头中心。"""
    head = skia.Path()
    head.addOval(skia.Rect.MakeXYWH(x - 62 * s, y - 80 * s, 124 * s, 160 * s))
    parts = [head, P((x, y + 80 * s), (x, y + 200 * s)), rect(x, y + 215 * s, 26 * s, 50 * s, 8 * s)]
    for dx in (-25, 25):
        parts.append(P((x + dx * s, y - 72 * s), (x + dx * s, y + 72 * s)))
    for dy in (-30, 30):
        parts.append(P((x - 56 * s, y + dy * s), (x + 56 * s, y + dy * s)))
    parts.append(circle(x + 130 * s, y + 150 * s, 34 * s))
    return join(*parts)


def angry(x, y, r=170) -> skia.Path:
    """一张皱眉生气的脸。"""
    mouth = skia.Path()
    mouth.addArc(skia.Rect.MakeXYWH(x - 70, y + 50, 140, 90), 200, 140)
    return join(circle(x, y, r), P((x - 110, y - 85), (x - 30, y - 45)), P((x + 110, y - 85), (x + 30, y - 45)),
                circle(x - 60, y - 15, 12), circle(x + 60, y - 15, 12), mouth,
                P((x + 120, y - 150), (x + 150, y - 190)), P((x + 150, y - 120), (x + 195, y - 140)))


def sofa(x, y, w=620) -> skia.Path:
    """沙发：(x, y) 为坐垫上沿中点。"""
    return join(P((x - w / 2 + 40, y), (x - w / 2 + 40, y - 150), (x + w / 2 - 40, y - 150), (x + w / 2 - 40, y)),
                rect(x, y + 45, w, 90, 24), rect(x - w / 2, y - 10, 70, 160, 30), rect(x + w / 2, y - 10, 70, 160, 30),
                P((x - w / 2 + 30, y + 90), (x - w / 2 + 30, y + 140)), P((x + w / 2 - 30, y + 90), (x + w / 2 - 30, y + 140)))


def lying(x, y, s=1.0) -> skia.Path:
    """躺着的慢慢：头在右、脚在左，(x, y) 为头心。圆眼镜朝上。"""
    return join(circle(x, y, 45 * s), P((x - 45 * s, y + 10 * s), (x - 230 * s, y + 25 * s)),
                P((x - 340 * s, y - 15 * s), (x - 230 * s, y + 25 * s), (x - 350 * s, y + 40 * s)),
                P((x - 75 * s, y + 15 * s), (x - 135 * s, y - 30 * s), (x - 190 * s, y + 10 * s)),
                circle(x - 14 * s, y - 14 * s, 12 * s), circle(x + 16 * s, y - 14 * s, 12 * s),
                P((x - 2 * s, y - 16 * s), (x + 4 * s, y - 16 * s)))


def facepalm(x, y, s=1.0) -> skia.Path:
    """捂脸的慢慢：一只手按在脑门上，(x, y) 为脚底。"""
    hy = y - 290 * s
    sh = hy + 80 * s
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)),
                P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)),
                P((x - 70 * s, hy + 170 * s), (x, sh), (x + 60 * s, hy + 110 * s), (x + 25 * s, hy - 5 * s)),
                P((x + 5 * s, hy - 25 * s), (x + 45 * s, hy - 15 * s)),
                circle(x - 16 * s, hy - 8 * s, 13 * s), P((x - 3 * s, hy - 10 * s), (x + 3 * s, hy - 10 * s)),
                P((x - 15 * s, hy + 22 * s), (x + 10 * s, hy + 22 * s)))


def sweat(x, y, s=1.0) -> skia.Path:
    parts = []
    for dx, dy in ((0, 0), (-40, 60)):
        d = skia.Path()
        cx, cy = x + dx * s, y + dy * s
        d.moveTo(cx, cy - 28 * s)
        d.quadTo(cx + 20 * s, cy, cx, cy + 14 * s)
        d.quadTo(cx - 20 * s, cy, cx, cy - 28 * s)
        parts.append(d)
    return join(*parts)


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def eye(x, y, w=200) -> skia.Path:
    """放大镜里的一只眼睛（眼眶轮廓）。"""
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.quadTo(x, y - w * 0.55, x + w / 2, y)
    p.quadTo(x, y + w * 0.55, x - w / 2, y)
    return p


def nods(x, y) -> skia.Path:
    """点头的小弧线（头两侧）。"""
    parts = []
    for sx in (-1, 1):
        a = skia.Path()
        a.moveTo(x + sx * 60, y - 20)
        a.quadTo(x + sx * 80, y, x + sx * 60, y + 20)
        parts.append(a)
    return join(*parts)


def tick_fn(j, x, y, r, beats):
    """闹钟指针：在每个拍点咔哒走一格（30°），格与格之间 0.12 秒转过去。"""

    def fn(c, k, t):
        n = 0.0
        for kk in beats:
            n += clamp01((t - b.t_of(j, kk)) / 0.12)
        a = -math.pi / 2 + n * math.pi / 6
        c.drawLine(x, y, x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78, marker(RED, 11))
        K.dot(c, x, y, 14, RED)
        return None

    return fn


def pupil_fn(x, y, r0, r1):
    """瞳孔慢慢放大。"""

    def fn(c, k, t):
        K.dot(c, x, y, lerp(r0, r1, ease_in_out(k)), BLACK)
        K.dot(c, x - 0.35 * lerp(r0, r1, k), y - 0.35 * lerp(r0, r1, k), 7, "#FFFFFF")
        return None

    return fn


def stamp_fn(x, y, s="行", size=110):
    """红章砸下：从大到小落定。"""

    def fn(c, k, t):
        sc = 1.8 - 0.8 * ease_out(k)
        c.save()
        c.translate(x, y)
        c.rotate(-8)
        c.scale(sc, sc)
        K.rr_stroke(c, 0, 0, size * 1.45, size * 1.45, 18, RED, 9, min(1.0, k * 2.5))
        K.text(c, s, 0, 0, size, "hand", RED, min(1.0, k * 2.5))
        c.restore()
        return None

    return fn


# ---------------------------------------------------------------- 出题（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

y = ROW[0]
scene("先做一道题", "做道题", (XL, y, 0.85), bars=2)
L(racket(XL - 60, y - 410, 0.75), 0, 0.9, BLACK, 9, sfx="wood_high")
T("球拍 + 球 = 1.10 元", XL, y - 140, 80, k0=1, k1=2.9, sfx="pop")
T("球拍比球贵 1 元", XL, y + 40, 80, k0=3, k1=4.8, sfx="pop")
T("球多少钱？", XL, y + 240, 96, RED, k0=5, k1=6.0, sfx="ding")

scene("三秒，说个数", "先别往下看", (XR, y, 0.85))
CLK = (XR - 330, y + 60, 180)
L(clock(*CLK), 0, 0.9, BLACK, 10, sfx="wood_high")
T("3 秒", CLK[0], y - 230, 84, RED, k0=1, k1=1.8, sfx="pop")
b.custom(J(), 1.8, 2.0, tick_fn(J(), *CLK, (2, 3, 4)))
for kk in (2, 3, 4):
    H(kk, "wood_low", 0.8, "指针走一格")
T("球 = ？", XR + 300, y - 230, 76, k0=5, k1=6, sfx="pop")
L(rect(XR + 300, y + 60, 420, 320, 24), 6, 6.9, BLUE, 10, sfx="wood_high")
L(underline(XR + 160, XR + 440, y + 165, 8, 30), 7, 7.8, BLUE, 6, sfx="pop")

y = ROW[1]
KK = (XR + 300, y + 350, 0.85)          # 快快脚底
BUB = (XR - 250, y - 250, 400, 180)     # “1毛！”气泡
scene("先冒出一个数", "快快抢答", (XR, y, 0.85))
L(kuai(*KK, "up"), 0, 0.9, RED, 10, sfx="wood_high")
L(face(*KK, "smile"), 0.9, 1.0, RED, 9)
T("快快", KK[0], KK[1] + 70, 60, RED, k0=1, k1=1.8, sfx="pop")
L(bubble(*BUB, 1), 2, 2.8, BLACK, 9, sfx="pop")
T("1毛！", BUB[0], BUB[1], 96, RED, k0=3, k1=3.8, sfx="pop")
L(join(P((XR + 40, y - 460), (XR - 10, y - 360), (XR + 30, y - 360), (XR - 20, y - 250))), 4, 4.6, RED, 12, sfx="ding")

# ---------------------------------------------------------------- drop：一验算，就错了（场景 4）

V4 = (2350, ROW[1] + 150, 0.68)
MM = (1950, ROW[1] + 600, 0.8)          # 慢慢脚底
scene("一验算，就错了", "慢慢验算", V4, shake=[0], flashes=[0])
L(cross(BUB[0], BUB[1], 120), 0, 0.6, RED, 18, sfx="kick")
L(man(*MM, "hold"), 1, 1.9, BLUE, 10, sfx="wood_high")
L(face(*MM, "flat"), 1.9, 2.0, BLUE, 9)
T("1.10 + 0.10 = 1.20", 2430, ROW[1] + 170, 74, BLUE, k0=2, k1=4.4, sfx="pop")
T("球 5分 · 球拍 1.05", 2430, ROW[1] + 340, 74, GREEN, k0=5, k1=6.8, sfx="pop")
L(check(2780, ROW[1] + 470, 60), 7, 7.8, GREEN, 12, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 5–9）

y = ROW[2]
scene("书里的老题", "思考，快与慢 · 书中观点", (XL, y, 0.85))
L(book(XL - 280, y - 20, 420, 280), 0, 0.9, BLACK, 10, sfx="wood_low")
T("《思考，快与慢》", XL - 280, y - 260, 64, GREEN, k0=1, k1=3, sfx="pop")
T("丹尼尔·卡尼曼", XL - 280, y + 220, 54, k0=3, k1=4.75, sfx="pop")
T("名校学生", XL + 320, y - 170, 64, k0=5, k1=6, sfx="pop")
T("一半以上答", XL + 320, y - 40, 64, k0=6, k1=7.2, sfx="pop")
T("1毛", XL + 320, y + 130, 120, RED, k0=7, k1=7.8, sfx="ding")

KS, MS = (XR - 320, y + 250, 0.8), (XR + 320, y + 250, 0.8)
scene("一个快，一个慢", "书中观点 · 两个系统", (XR, y, 0.85))
L(kuai(*KS, "up"), 0, 0.9, RED, 10, sfx="wood_high")
L(face(*KS, "smile"), 0.9, 1.0, RED, 9)
T("快快 = 系统1", KS[0], y - 380, 60, RED, k0=1, k1=2.6, sfx="pop")
L(man(*MS, "down"), 3, 3.9, BLUE, 10, sfx="wood_high")
L(face(*MS, "flat"), 3.9, 4.0, BLUE, 9)
T("慢慢 = 系统2", MS[0], y - 380, 60, BLUE, k0=4, k1=5.6, sfx="pop")
T("自动 · 快 · 不费劲", KS[0], y + 340, 50, k0=6, k1=7, sfx="pop")
T("要专心 · 费劲", MS[0], y + 340, 50, k0=7, k1=8, sfx="pop")

y = ROW[3]
FK = (XL + 330, y + 300, 0.65)
scene("看脸就知道生气", "书中观点 · 快快的活", (XL, y, 0.85))
L(angry(XL - 250, y - 120), 0, 0.9, BLACK, 10, sfx="wood_high")
L(kuai(*FK, "up"), 1, 1.9, RED, 10, sfx="pop")
L(bubble(XL + 230, y - 300, 330, 140, 1), 2, 2.7, RED, 8, sfx="pop")
T("要发火！", XL + 230, y - 300, 60, RED, k0=3, k1=4, sfx="pop")
T("2 + 2 = 4", XL - 250, y + 230, 84, k0=5, k1=6.2, sfx="pop")
L(check(XL + 10, y + 225, 45), 7, 7.7, GREEN, 11, sfx="ding")

MB = (XR - 270, y + 400, 0.85)         # 慢慢脚底
EYE = (XR + 300, y + 50)
scene("这题得停下来算", "书中观点 · 慢慢的活", (XR, y, 0.85))
T("17 × 24 = ？", XR, y - 350, 92, k0=0, k1=2, sfx="pop")
L(man(*MB, "down"), 2, 2.9, BLUE, 10, sfx="wood_high")
L(face(*MB, "flat"), 2.9, 3.0, BLUE, 9)
L(join(circle(*EYE, 170), eye(*EYE, 210), P((MB[0] + 40, MB[1] - 305), (EYE[0] - 165, EYE[1] + 30))), 3, 3.9,
  BLACK, 9, sfx="wood_low")
b.custom(J(), 4, 6, pupil_fn(*EYE, 16, 52), sfx="tom")
T("瞳孔放大", EYE[0], EYE[1] + 240, 60, k0=6, k1=7, sfx="pop")
L(sweat(MB[0] - 75, MB[1] - 330), 7, 7.6, BLUE, 8, sfx="pop")

y = ROW[4]
SF = (XL + 80, y + 110)                 # 沙发坐垫中点
FK9 = (XL - 440, y + 290, 0.7)
DOC9 = (XL - 300, y - 70)
scene("慢慢懒得查", "书中观点 · 慢慢很懒", (XL, y, 0.85))
L(sofa(*SF, 640), 0, 0.9, BLACK, 9, sfx="wood_low")
L(lying(SF[0] + 210, SF[1] - 50, 0.9), 1, 1.9, BLUE, 10, sfx="wood_high")
L(kuai(*FK9, "hold"), 2, 2.9, RED, 10, sfx="pop")
L(rect(*DOC9, 170, 200, 10), 3, 3.6, BLACK, 8, sfx="pop")
T("1毛", DOC9[0], DOC9[1] - 30, 60, RED, k0=3.6, k1=4.4)
b.custom(J(), 5, 5.35, stamp_fn(DOC9[0] + 10, DOC9[1] + 40, "行", 64), sfx="rim")
T("呼……", SF[0] + 330, y - 160, 60, BLUE, k0=6, k1=7, sfx="pop")
T("懒得查", SF[0] + 120, y - 330, 76, RED, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–11）

QD = (XR - 170, y)
scene("报价单，扫一眼就签", "例子 · 报价单", (XR, y, 0.85))
L(rect(*QD, 500, 660, 16), 0, 0.9, BLACK, 9, sfx="wood_high")
T("报价单", QD[0], y - 240, 66, k0=1, k1=1.8, sfx="pop")
T("设计  3万", QD[0], y - 90, 60, k0=2, k1=2.9, sfx="pop")
T("开发  8万", QD[0], y + 40, 60, k0=3, k1=3.9, sfx="pop")
T("维护费 另计", QD[0], y + 190, 46, k0=4, k1=5.2, sfx="wood_low")
L(kuai(XR + 360, y + 300, 0.7, "up"), 5, 5.8, RED, 10, sfx="wood_high")
T("签！", XR + 360, y - 200, 90, RED, k0=6, k1=6.7, sfx="pop")
L(oval(QD[0], y + 190, 330, 100), 7, 7.8, RED, 9, sfx="rim")

y = ROW[5]
BOSS = (XL - 330, y + 300, 0.75)
FK11 = (XL + 150, y + 300, 0.75)
MP = (XL + 470, y + 360, 0.6)
scene("嘴比脑子快", "例子 · 领导问工期", (XL, y, 0.85))
L(stick(*BOSS, "point", tie=True), 0, 0.9, BLACK, 10, sfx="wood_high")
L(bubble(XL - 230, y - 290, 470, 150, -1), 1, 1.7, BLACK, 8, sfx="pop")
T("一天能做完吧？", XL - 230, y - 290, 54, k0=2, k1=3.75, sfx="pop")
L(kuai(*FK11, "up"), 4, 4.9, RED, 10, sfx="wood_high")
L(face(*FK11, "smile"), 4.9, 5.0, RED, 9)
T("能！", XL + 300, y - 180, 96, RED, k0=5, k1=5.7, sfx="pop")
L(facepalm(*MP), 6, 6.9, BLUE, 9, sfx="wood_low")
T("唉……", MP[0] + 30, y - 40, 54, BLUE, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- 具体做法（场景 12–13）

PAPER = (XR - 150, y + 60)
MM12 = (XR + 400, y + 360, 0.65)
scene("答得太顺，就验一遍", "做法一 · 验一遍", (XR, y, 0.85))
T("① 写下来，算一遍", XR, y - 400, 72, BLUE, k0=0, k1=2, sfx="pop")
L(rect(*PAPER, 500, 480, 12), 2, 2.9, BLACK, 9, sfx="wood_high")
T("0.05 + 1.05", PAPER[0], PAPER[1] - 90, 70, k0=3, k1=4.6, sfx="pop")
T("= 1.10", PAPER[0], PAPER[1] + 40, 70, GREEN, k0=5, k1=5.9, sfx="pop")
L(check(PAPER[0] + 130, PAPER[1] + 160, 50), 6, 6.7, GREEN, 12, sfx="ding")
L(man(*MM12, "hold"), 7, 7.9, BLUE, 10, sfx="wood_high")

y = ROW[6]
MM13 = (XL - 330, y + 330, 0.75)
CL13 = (XL + 340, y + 270, 100)
scene("先说，我算一下", "做法二 · 晚点回", (XL, y, 0.85))
T("② 晚点回复", XL, y - 400, 72, BLUE, k0=0, k1=1.5, sfx="pop")
L(man(*MM13, "down"), 2, 2.9, BLUE, 10, sfx="wood_high")
L(face(*MM13, "smile"), 2.9, 3.0, BLUE, 9)
L(bubble(XL + 120, y - 120, 600, 220, -1), 3, 3.7, BLUE, 8, sfx="pop")
T("我算一下，", XL + 120, y - 165, 56, k0=4, k1=5.25, sfx="pop")
T("半小时后回你", XL + 120, y - 75, 56, k0=5.25, k1=6.75)
L(join(clock(*CL13), hands_at(*CL13, 3, 30)), 7, 7.9, BLACK, 9, sfx="wood_low")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FULL = (1800, 3000, 0.176)
COMMENT = (XR, y, 0.85)
scene("你第一反应几毛？", "评论区见", FULL, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(rect(XR, y - 330, 900, 200, 40), 5, 5.8, RED, 8, sfx="pop")
T("你第一反应是几毛？", XR, y - 330, 76, RED, k0=6, k1=8.25, sfx="pop")
T("下一讲：先听到的那句，为什么最管用？", XR, y - 120, 48, k0=9, k1=13, sfx="wood_high")
KE, ME = (XR - 300, y + 380, 0.6), (XR + 300, y + 380, 0.6)
L(kuai(*KE, "up"), 13, 13.8, RED, 9, sfx="wood_high")
L(face(*KE, "smile"), 13.8, 14.0, RED, 8)
L(man(*ME, "down"), 14, 14.8, BLUE, 9, sfx="pop")
L(face(*ME, "smile"), 14.8, 15.0, BLUE, 8)
L(nods(ME[0], ME[1] - 174), 15, 15.6, BLUE, 7, sfx="ding")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "bat", "快与慢", "球拍和球，你算对了吗？", ACC, b.shots,
                 [f"{BOOK}第1章 一张愤怒的脸和一道乘法题（The Characters of the Story）（转述）",
                  f"{BOOK}第2章 电影的主角与配角（Attention and Effort）（转述）",
                  f"{BOOK}第3章 惰性思维与延迟满足的矛盾（The Lazy Controller）（转述）",
                  "中译本：胡晓姣、李爱民、何梦莹译，中信出版社 2012"],
                 "球拍和球|你算【对】了吗", SQUARE_SHOT,
                 ["书中观点（转述）：人脑有两种运作方式——系统1 自动、快速、几乎不费力，一眼看出一张脸在生气、"
                  "答出 2 + 2；系统2 需要集中注意力，做 17 × 24 这样的心算会费劲，书中提到做费劲的心算时瞳孔会放大"
                  "（第 1–2 章）。书里把两个系统当作故事里的两个角色，本系列画成“快快 / 慢慢”两个小人，为示意。",
                  "球拍和球（第 3 章）：直觉会先冒出 10 美分，正确答案是 5 美分；书中提到名校学生也有一半以上答 10 美分"
                  "（书中数据）。系统2 本可以花几秒验算，却常常懒得查，直接认可系统1 的答案。题目把美元换成人民币，数字不变；"
                  "“1.10 + 0.10 = 1.20”的验算过程、慢慢躺沙发盖章“行”为通俗化示意。上屏均为转述，不是逐字引文。",
                  "报价单扫一眼就签、领导问“一天能做完吧”为现实场景示意，金额与工期为示意数字，不指向任何具体公司或个人。",
                  "两条做法（答得太顺就写下来算一遍；先说“我算一下”，晚点回复）为据书中思路整理的建议。"],
                 tags="#思维 #决策")
    return b.attach(ep)
