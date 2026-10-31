"""10 睡得着就好（白板手绘版）：管钱的办法，睡得着就够了（系列最后一讲）。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（2026-10 观众反馈“切太快看不清”后改为慢速讲解版）。
叙事（A 经典）：打工人切身问题开局（半夜两点躺在床上刷账户，数字一跳心就一紧；床头贴满“最优方案”，小猪罐冒汗）→
drop：一把剪刀剪掉锯齿线，换成一条平缓的线，窗里的月亮变成 zZ →
书中观点（亮书；第 11 章：合乎情理胜过绝对理性，选自己拿得住的方案；马科维茨谈自己的安排，想的是将来少后悔；
第 14 章：人是会变的，三个年纪的小王心愿各不相同；第 20 章：作者家的目标是睡得踏实，白板角写明“作者自己的选择，不是给你的建议”）→
身边的例子（同事上班偷看手机盯着涨跌，报表又出错）→
具体做法（任何方案先过一道门“我晚上能睡着吗？” / 给将来的自己留一格空白）→
把这一季串起来（小猪罐身边依次弹出前九讲的样子）→ 拉远看全板 → 评论区互动，小猪罐睡着。
书中观点为转述（Morgan Housel, The Psychology of Money, Harriman House, 2020；中译本《金钱心理学》，李青宗译，
民主与建设出版社 / 后浪 2023，第 11、14、20 章）；例子与做法为现实场景示意与据书中思路整理的建议，不构成投资建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_out
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, clock,
                               cross, doc, face, hands_at, join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#3B4A8C"                 # 本讲主色：夜里的靛蓝
SQUARE_SHOT = 3                 # 场景 4（drop）：床上的小王 + 剪掉锯齿线换成平线 + 月亮变 zZ

b = Board(size=(3600, 9600))


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

def pig(x, y, s=1.0, mood="smile") -> skia.Path:
    """小猪罐（侧身朝右）：(x, y) 为身子中心。mood：smile / sad / shock / sleep。"""
    rx, ry = 150 * s, 110 * s
    body = skia.Path()
    body.addOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    snout = skia.Path()
    snout.addOval(skia.Rect.MakeXYWH(x + rx - 22 * s, y - 35 * s, 50 * s, 70 * s))
    parts = [body, snout, circle(x + rx + 3 * s, y - 12 * s, 5 * s), circle(x + rx + 3 * s, y + 12 * s, 5 * s),
             P((x + 20 * s, y - 109 * s), (x + 50 * s, y - 165 * s), (x + 80 * s, y - 93 * s)),
             P((x + 78 * s, y - 94 * s), (x + 115 * s, y - 140 * s), (x + 120 * s, y - 66 * s)),
             rect(x - 40 * s, y - 80 * s, 80 * s, 14 * s, 6 * s)]
    for dx in (-95, -45, 45, 95):
        yb = y + ry * math.sqrt(1 - (dx / 150) ** 2)
        parts.append(P((x + dx * s, yb - 4 * s), (x + dx * s, yb + 40 * s)))
    tail = skia.Path()
    tail.moveTo(x - rx, y - 10 * s)
    tail.quadTo(x - rx - 45 * s, y - 20 * s, x - rx - 35 * s, y - 55 * s)
    tail.quadTo(x - rx - 20 * s, y - 75 * s, x - rx - 15 * s, y - 45 * s)
    parts.append(tail)
    eye = skia.Path()
    if mood == "sleep":
        eye.addArc(skia.Rect.MakeXYWH(x + 66 * s, y - 50 * s, 28 * s, 18 * s), 0, 180)
    else:
        eye.addCircle(x + 80 * s, y - 40 * s, 7 * s)
    parts.append(eye)
    m = skia.Path()
    if mood == "sad":
        m.addArc(skia.Rect.MakeXYWH(x + 78 * s, y + 42 * s, 40 * s, 26 * s), 200, 140)
    elif mood == "shock":
        m.addCircle(x + 98 * s, y + 45 * s, 10 * s)
    else:
        m.addArc(skia.Rect.MakeXYWH(x + 78 * s, y + 25 * s, 40 * s, 26 * s), 20, 140)
    parts.append(m)
    return join(*parts)


def sweat(x, y, s=1.0) -> skia.Path:
    """小猪罐额前两滴汗：(x, y) 为小猪身子中心。"""
    parts = []
    for cx, cy in ((x + 150 * s, y - 120 * s), (x + 185 * s, y - 70 * s)):
        d = skia.Path()
        d.moveTo(cx, cy - 26 * s)
        d.quadTo(cx + 18 * s, cy, cx, cy + 12 * s)
        d.quadTo(cx - 18 * s, cy, cx, cy - 26 * s)
        parts.append(d)
    return join(*parts)


def moon(x, y, r=80) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def bed() -> skia.Path:
    """场景 1 的床：床头在左（x≈420），床尾在 x≈1150，床面 y≈1150。"""
    blanket = skia.Path()
    blanket.moveTo(650, 1150)
    blanket.quadTo(640, 1090, 700, 1080)
    blanket.lineTo(1150, 1075)
    return join(P((420, 1250), (420, 900), (500, 900), (500, 1150)), P((420, 1150), (1150, 1150)),
                P((1150, 1060), (1150, 1250)), P((500, 1210), (1150, 1210)), rect(575, 1115, 130, 50, 20), blanket)


def lying_head(x, y, r=46) -> skia.Path:
    """躺在枕头上的小王：头 + 睁大的眼睛 + 一字嘴。"""
    return join(circle(x, y, r), circle(x - 16, y - 8, 8), circle(x + 16, y - 8, 8), P((x - 14, y + 20), (x + 14, y + 20)))


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12 if w < 200 else 40),
                P((x - w * 0.17, y + h / 2 - h * 0.13), (x + w * 0.17, y + h / 2 - h * 0.13)))


def glow(x, y) -> skia.Path:
    """手机屏光：从 (x, y) 往左下照到脸上的三道光。"""
    return join(P((x - 20, y + 60), (x - 80, y + 105)), P((x, y + 65), (x - 40, y + 120)),
                P((x + 20, y + 60), (x + 5, y + 120)))


def jagged(x0, x1, y, amp=150) -> skia.Path:
    """账户曲线：忽上忽下的锯齿线。"""
    ys = (0.2, -0.7, 0.5, -0.2, 0.9, -0.9, 0.3, -0.5, 0.8, -0.3)
    n = len(ys)
    return P(*[(x0 + (x1 - x0) * i / (n - 1), y + amp * v) for i, v in enumerate(ys)])


def heart(x, y, r=40) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def beating_heart(x, y, r, j, beats):
    """描出一颗心，之后在第 j 个镜头的 beats 拍上各跳一下（离开该镜头后静止）。"""
    def fn(c, k, t):
        sc = 1.0
        if t < b.t_of(j, 4 * b.shots[j].bars):
            for kb in reversed(beats):
                t0 = b.t_of(j, kb)
                if t >= t0:
                    sc = 1 + 0.28 * math.exp(-(t - t0) * 9)
                    break
        path = heart(x, y, r * sc)
        part, tip = wb.partial(path, k)
        if k >= 1:
            c.drawPath(path, K.paint(RED, 0.3))
        c.drawPath(part, wb.marker(RED, 9))
        return tip

    return fn


def scissors(x, y, s=1.0) -> skia.Path:
    """剪刀：手柄在左，刀尖朝右（刀尖在 x+130·s）。"""
    return join(circle(x - 95 * s, y - 38 * s, 30 * s), circle(x - 95 * s, y + 38 * s, 30 * s),
                P((x - 70 * s, y - 25 * s), (x + 130 * s, y + 20 * s)), P((x - 70 * s, y + 25 * s), (x + 130 * s, y - 20 * s)),
                circle(x + 41 * s, y, 6 * s))


def note(x, y, w=230, h=120) -> skia.Path:
    """便签：方块 + 顶上一截胶带。"""
    return join(rect(x, y, w, h, 6), P((x - 40, y - h / 2 - 12), (x + 40, y - h / 2 + 8)))


def steep(x0, y0) -> skia.Path:
    """陡坡：几乎竖直往上的折线（纸面最优）。"""
    return P((x0, y0), (x0 + 90, y0 - 300), (x0 + 140, y0 - 260), (x0 + 250, y0 - 600), (x0 + 300, y0 - 560),
             (x0 + 400, y0 - 720))


def stairs(x0, y0, n=5, w=100, h=60) -> skia.Path:
    """缓台阶（拿得住的方案）。"""
    pts = [(x0, y0)]
    for i in range(n):
        pts += [(x0 + (i + 1) * w, y0 - i * h), (x0 + (i + 1) * w, y0 - (i + 1) * h)]
    pts.append((x0 + (n + 1) * w + 20, y0 - n * h))
    return P(*pts)


def medal(x, y, r=26) -> skia.Path:
    return join(P((x - 30, y - 55), (x, y - r), (x + 30, y - 55)), circle(x, y, r))


def house(x, y, w=560, h=360) -> skia.Path:
    """平房外框（无门窗，里面画睡觉的人）：(x, y) 为地面中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 60, y), (x + w / 2 + 40, y)),
                P((x - w / 2 - 35, y - h), (x, y - h - 150), (x + w / 2 + 35, y - h)))


def sleepers(x, y) -> skia.Path:
    """床上并排睡着的两个人：(x, y) 为床面左端。"""
    parts = [P((x, y), (x + 380, y)), P((x, y + 50), (x, y - 80)), P((x + 380, y + 50), (x + 380, y - 20))]
    for hx in (x + 55, x + 140):
        parts.append(circle(hx, y - 40, 32))
        for ex in (-11, 11):
            e = skia.Path()
            e.addArc(skia.Rect.MakeXYWH(hx + ex - 8, y - 50, 16, 10), 0, 180)
            parts.append(e)
    bl = skia.Path()
    bl.moveTo(x + 185, y)
    bl.quadTo(x + 180, y - 45, x + 230, y - 45)
    bl.lineTo(x + 370, y - 40)
    parts.append(bl)
    return join(*parts)


def desk_monitor(x0, x1, y, mx) -> skia.Path:
    return join(P((x0, y), (x1, y)), P((x0 + 30, y), (x0 + 30, y + 130)), P((x1 - 30, y), (x1 - 30, y + 130)),
                rect(mx, y - 190, 340, 230, 10), P((mx, y - 75), (mx, y)))


def gate(x, y, w=500, h=600) -> skia.Path:
    """一道门：(x, y) 为门槛中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h)), P((x + w / 2, y), (x + w / 2, y - h)),
                P((x - w / 2 - 40, y - h), (x + w / 2 + 40, y - h)), P((x - w / 2 - 40, y), (x - w / 2 + 40, y)),
                P((x + w / 2 - 40, y), (x + w / 2 + 40, y)))


def pop_word(s, x, y, size, color, j, k):
    """贴纸式弹出一个词：第 j 镜第 k 拍起 0.25 秒内放大到 1.15 再落回 1。"""
    def fn(c, kk, t):
        dt = t - b.t_of(j, k)
        if dt < 0:
            return None
        f = clamp01(dt / 0.25)
        sc = ease_out(f) * (1 + 0.15 * math.sin(math.pi * f))
        if sc > 0.05:
            K.text(c, s, x, y, size * sc, "hand", color)
        return None

    return fn


# ---------------------------------------------------------------- 开局：半夜睡不着（场景 1–4）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


MOON = (1300, 560)
scene("半夜还在看账户", "灵魂拷问", (900, 900, 0.85), bars=2)
L(bed(), 0, 0.9, sfx="wood_high")
L(lying_head(590, 1045), 1, 1.8, sfx="pop")
L(join(phone(700, 900, 60, 100), glow(700, 900)), 2, 2.8, BLUE, 8, sfx="pop")
L(join(rect(*MOON, 300, 300, 8), moon(*MOON, 80)), 3, 3.9, BLACK, 9, sfx="wood_high")
L(clock(520, 520, 75), 4, 4.7, BLACK, 8, sfx="wood_low")
L(hands_at(520, 520, 75, 2, 0), 4.7, 5.0, BLACK, 8)
T("2:00", 520, 680, 70, RED, k0=5, k1=6, sfx="pop")

PH = (1930, 900)                # 大手机（账户）
HEART = (2350, 1140)            # 小王心口
scene("数字一跳，心就一紧", "灵魂拷问", (2100, 900, 0.85))
J2 = J()
L(phone(*PH, 420, 700), 0, 0.9, BLACK, 9, sfx="wood_high")
L(jagged(1770, 2090, 900), 1, 1.9, RED, 9, sfx="rim")
L(stick(2350, 1300, 0.85, "down"), 2, 2.8, sfx="pop")
L(face(2350, 1300, 0.85, "sad"), 2.8, 3.0)
L(arrow((2160, 900), (2300, 1100), -0.2, 36), 3, 3.8, RED, 8, sfx="wood_high")
b.custom(J2, 4, 4.8, beating_heart(*HEART, 38, J2, (5, 6, 7, 8, 9, 10, 11)), sfx="tom")
H(5, "tom", 0.55)
T("心一紧", 2330, 830, 70, RED, k0=6, k1=6.8, sfx="pop")

PIG3 = (1300, 1180, 0.65)
scene("方法挺对，就是睡不着", "灵魂拷问", (850, 820, 0.9))
for n, (x, y) in enumerate(((740, 470), (990, 540), (820, 700))):
    L(note(x, y), 2 * n, 2 * n + 0.8, BLACK, 8, sfx="wood_high" if n != 1 else "pop")
    T("最优方案", x, y + 8, 48, k0=2 * n + 0.8, k1=2 * n + 1.8)
L(pig(*PIG3, "sad"), 6, 6.9, BLACK, 8, sfx="pop")
L(sweat(*PIG3), 7, 7.8, BLUE, 8, sfx="rim")

# drop：从床边拉远到整间卧室 + 大手机
scene("换个能睡着的", "换个思路", (1420, 880, 0.52), shake=[0], flashes=[0])
L(scissors(1610, 900, 1.0), 0, 0.9, BLACK, 10, sfx="kick")
b.erase(J(), 1, 1.8, PH[0], PH[1], 360, 480)
H(1, "rim")
L(underline(1780, 2080, 900, amp=12, step=100), 2, 2.9, GREEN, 11, sfx="wood_high")
b.erase(J(), 3, 3.6, MOON[0], MOON[1], 210, 210)
H(3, "shaker", 0.6)
T("zZ", MOON[0], MOON[1] + 10, 120, BLUE, k0=4, k1=4.8, sfx="pop")
T("换个能睡着的", 1450, 230, 120, RED, k0=5, k1=6.5, sfx="ding")
L(underline(1100, 1800, 320, amp=16, step=60), 7, 7.8, RED, 10, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 5–9）

PIG5 = (1220, 2700, 0.8)
scene("翻开《金钱心理学》", "金钱心理学 · 亮书", (900, 2400, 0.85))
L(book(700, 2430, 420, 280), 0, 0.9, sfx="wood_low")
T("金钱心理学", 700, 2180, 72, GREEN, k0=1, k1=2.25, sfx="pop")
L(rect(1200, 2250, 440, 110, 20), 3, 3.8, BLUE, 8, sfx="wood_high")
T("摩根·豪泽尔", 1200, 2255, 60, k0=3.8, k1=5.3)
L(pig(*PIG5, "smile"), 6, 6.9, BLACK, 9, sfx="pop")
T("第11、14、20章", 700, 2700, 54, BLUE, k0=7, k1=8, sfx="wood_high")

scene("合情合理，胜过最优", "书中观点 · 第11章", (2650, 2400, 0.85))
T("纸面最优", 2350, 1980, 60, RED, k0=0, k1=1, sfx="pop")
L(steep(2150, 2800), 1, 1.9, RED, 9, sfx="wood_high")
L(stick(2430, 2800, 0.45, "shrug"), 2, 2.8, BLACK, 8, sfx="pop")
L(face(2430, 2800, 0.45, "sad"), 2.8, 3.0, BLACK, 7)
T("拿得住", 2980, 2330, 60, GREEN, k0=4, k1=4.8, sfx="pop")
L(stairs(2680, 2800), 5, 5.9, GREEN, 9, sfx="wood_high")
L(stick(3050, 2620, 0.45, "up"), 6, 6.8, BLACK, 8, sfx="pop")
L(face(3050, 2620, 0.45, "smile"), 6.8, 7.0, BLACK, 7)
L(check(3200, 2400, 50), 7, 7.8, GREEN, 11, sfx="ding")

MK = (2350, 4000)
scene("拿奖的人也怕后悔", "书中故事 · 第11章", (2650, 3650, 0.85))
L(stick(*MK, 0.85, "down"), 0, 0.9, sfx="wood_high")
L(face(*MK, 0.85, "flat"), 0.9, 1.0)
L(rect(MK[0], 4100, 300, 90, 16), 1, 1.8, BLUE, 8, sfx="pop")
T("马科维茨", MK[0], 4104, 54, k0=1.8, k1=2.8)
L(medal(MK[0], 3870), 3, 3.8, ORANGE, 8, sfx="wood_high")
T("诺奖得主", MK[0], 3560, 54, ORANGE, k0=4, k1=5, sfx="pop")
L(bubble(2880, 3520, 520, 170, -1), 5, 5.8, BLACK, 8, sfx="pop")
T("将来少后悔", 2880, 3524, 60, BLUE, k0=5.8, k1=7.05)

scene("人是会变的", "书中观点 · 第14章", (950, 3650, 0.85))
L(arrow((380, 4130), (1500, 4130), 0.0, 40), 0, 0.9, BLACK, 8, sfx="wood_high")
L(stick(480, 4050, 0.45), 1, 1.7, BLACK, 8, sfx="pop")
L(face(480, 4050, 0.45, "smile"), 1.7, 1.9, BLACK, 7)
L(bubble(480, 3760, 280, 110, -1), 2, 2.4, BLACK, 7, sfx="pop")
T("当宇航员", 480, 3764, 50, k0=2.4, k1=3.4)
L(join(stick(900, 4050, 0.65), face(900, 4050, 0.65, "smile")), 3.4, 4.0, BLACK, 8)
L(bubble(900, 3620, 260, 110, -1), 4, 4.4, BLACK, 7, sfx="pop")
T("买跑车", 900, 3624, 50, RED, k0=4.4, k1=5.2)
L(join(stick(1340, 4050, 0.85), face(1340, 4050, 0.85, "smile")), 6, 6.7, BLUE, 9, sfx="wood_high")
L(bubble(1340, 3480, 300, 110, -1), 6.7, 7.0, BLUE, 7)
T("早点回家", 1340, 3484, 50, BLUE, k0=7, k1=8, sfx="pop")

scene("作者家：能睡踏实", "书中故事 · 第20章", (950, 5000, 0.85))
L(house(800, 5330), 0, 0.9, sfx="wood_high")
L(sleepers(610, 5250), 1, 1.9, BLACK, 8, sfx="pop")
T("目标：睡得踏实", 800, 4580, 72, GREEN, k0=2, k1=3.75, sfx="pop")
L(rect(1350, 5100, 420, 240, 16), 4, 4.8, RED, 7, sfx="rim")
T("作者自己的选择", 1350, 5050, 46, RED, k0=5, k1=6.5, sfx="pop")
T("不是给你的建议", 1350, 5150, 46, RED, k0=6.5, k1=8)

CO = (2330, 5330)               # 盯盘的同事（示意）
scene("同事天天盯盘", "例子 · 上班盯盘", (2650, 5000, 0.85))
L(desk_monitor(2600, 3180, 5150, 2900), 0, 0.9, sfx="wood_high")
L(stick(*CO, 0.8, "hold"), 1, 1.8, sfx="pop")
L(face(*CO, 0.8, "flat"), 1.8, 2.0)
L(join(phone(2430, 5120, 60, 100), P((2405, 5130), (2420, 5100), (2435, 5125), (2455, 5090))), 2, 2.8, BLUE, 7,
  sfx="wood_high")
L(cross(2900, 4960, 60), 4, 4.8, RED, 12, sfx="rim")
T("报表又错了", 2900, 4700, 60, RED, k0=5, k1=6.25, sfx="pop")

# ---------------------------------------------------------------- 具体做法（场景 11–12）

scene("先问能不能睡着", "第一步 · 先过一道门", (950, 6350, 0.85))
T("① 先过一道门", 950, 5900, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(gate(950, 6750), 2, 2.9, BLACK, 10, sfx="wood_high")
T("我晚上能睡着吗？", 950, 6070, 54, RED, k0=3, k1=5, sfx="pop")
L(doc(450, 6500, 150, 190), 5, 5.8, BLACK, 8, sfx="wood_high")
L(arrow((540, 6500), (680, 6500), 0.0, 30), 6, 6.8, BLACK, 8, sfx="pop")
L(pig(950, 6560, 0.8, "smile"), 7, 7.9, GREEN, 9, sfx="ding")

scene("给将来的自己留余地", "第二步 · 留一格空白", (2650, 6350, 0.85))
T("② 给将来留余地", 2650, 5900, 72, BLUE, k0=0, k1=1.75, sfx="pop")
L(join(*(rect(x, 6400, 340, 480, 16) for x in (2250, 2650, 3050))), 2, 2.9, BLACK, 8, sfx="wood_high")
L(join(stick(2250, 6580, 0.55), face(2250, 6580, 0.55, "smile")), 3, 3.8, BLACK, 8, sfx="pop")
L(join(stick(2650, 6580, 0.7), face(2650, 6580, 0.7, "smile")), 4, 4.8, BLACK, 8, sfx="wood_high")
T("？", 3050, 6400, 120, RED, k0=5, k1=5.8, sfx="pop")
T("现在", 2250, 6720, 50, k0=6, k1=6.8, sfx="pop")
T("留白", 3050, 6720, 50, GREEN, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 把这一季串起来（场景 13）

PIG13 = (1800, 7560, 1.2)
SEASON = [("两格罐", 1370, 7250), ("备用金", 1370, 7500), ("钉住终点", 1370, 7750), ("冰川", 1600, 7950),
          ("稳底座", 2000, 7950), ("闹钟", 2230, 7750), ("空车位", 2230, 7500), ("不为啥", 2230, 7250),
          ("车距", 1800, 7150)]
scene("把这季串起来", "这一季 · 小猪罐", (1800, 7550, 0.85))
J13 = J()
L(pig(*PIG13, "smile"), 0, 0.9, BLACK, 10, sfx="wood_high")
for n, (w, x, y) in enumerate(SEASON):
    color = GREEN if n % 2 == 0 else BLACK
    b.custom(J13, n, n + 0.3, pop_word(w, x, y, 54, color, J13, n), sfx=None if n == 0 else ("pop" if n % 2 else "wood_high"))
H(8, "ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FULL = (1800, 4700, 0.11)
END = (1800, 8800, 0.85)
scene("哪一讲最戳你？", "评论区见", FULL, bars=4)
J14 = J()
b.move(J14, 4, END, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("哪一讲最戳你？", 1800, 8400, 84, RED, k0=6, k1=7.75, sfx="pop")
L(pig(1450, 8900, 0.9, "sleep"), 8, 8.9, BLACK, 9, sfx="wood_high")
T("zZ", 1720, 8680, 72, BLUE, k0=9, k1=9.8, sfx="pop")
T("这一季讲完了", 2200, 8950, 64, GREEN, k0=10, k1=11.5, sfx="ding")
b.hit(J14, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "sleep", "睡得着就好", "管钱的办法，睡得着就够了", ACC, b.shots,
                 [f"{BOOK}第 11 章“合乎情理胜过绝对理性”、第 14 章“人是会变的”、第 20 章“我的理财方案”（转述）",
                  "中译本：李青宗译，民主与建设出版社 / 后浪 2023"],
                 "管钱的办法|【睡得着】就够了", SQUARE_SHOT,
                 ["书中观点（转述）：第 11 章“合乎情理胜过绝对理性”——一个能坚持下去、合乎情理的方案，比理论上的最优方案更好；"
                  "诺贝尔奖得主马科维茨谈到自己的安排时说，他考虑的是将来少后悔（上屏不写任何比例）。第 14 章“人是会变的”——"
                  "人总低估自己将来会变多少（书中引用心理学家丹尼尔·吉尔伯特所说的“历史终结错觉”），做长期计划要给将来的自己留余地。"
                  "第 20 章“我的理财方案”——作者说他家的目标是独立、晚上睡得踏实，并承认有些做法从纸面上看不一定最优；"
                  "上屏只讲“目标是睡踏实”这一层，不讲作者买了什么、怎么配置，白板上写明“作者自己的选择，不是给你的建议”。"
                  "出处：Morgan Housel, The Psychology of Money (Harriman House, 2020)；中译本《金钱心理学》（摩根·豪泽尔著，"
                  "李青宗译，民主与建设出版社 / 后浪 2023）第 11、14、20 章（转述）。上屏均为转述，不是逐字引文。",
                  "半夜两点刷账户、床头贴满“最优方案”、同事上班偷看手机盯涨跌导致报表出错，均为现实场景示意，"
                  "不指向任何具体公司或个人；“2:00”为示意时间；陡坡与缓台阶、三个年纪的心愿为对书中观点的通俗化示意。",
                  "两步做法（任何方案先过一道门“我晚上能睡着吗？”；给将来的自己留一格空白）为示意 / 据书中思路整理的建议。",
                  "本讲不出现任何具体股票、基金、理财产品、平台或公司名，不构成投资建议。",
                  "场景 13 的九个词为本系列前九讲里小猪罐的样子（两格罐、备用金、钉住的终点线、冰川、稳底座、闹钟、空车位、"
                  "不为啥标签、车距），用于收尾回顾。"],
                 tags="#理财 #焦虑")
    return b.attach(ep)
