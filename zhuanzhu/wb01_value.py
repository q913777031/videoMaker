"""01 专注值钱（白板手绘版）：加班到十点，活怎么还没干完？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 I 数字/曲线，一个问题开局）：整讲围着一个式子“成果 = 时间 × 专注”转。
开局问题（晚上十点工位还亮着 → 一天坐了十二小时 → 方案才写一页）→
drop：式子砸上白板，时间那格十二小时、专注那格是零，上面垒起来的“成果”塔哗地塌成 0 →
亮书（《深度工作》、卡尔·纽波特名牌）→ 书中观点（活分两种：专注的难活儿 / 浮活；浮活换谁都行，难活儿换人就难）→
回到式子（书里的式子：时间乘专注；时间画成长条，专注画成刻度盘）→
小红点每叮一下，蓝色专注块裂一刀，碎块拼不回 → 两根柱子：十二小时碎块 vs 四小时整块（示意）→
做法（日历上早上先留一整块 / 手机放进抽屉，小红点在里面干叫）→ 拉远看全板，护住专注 → 评论区互动。
书中观点为转述（卡尔·纽波特《深度工作》前言、第1章；中译本宋伟译）；例子、柱子高低与做法为示意 / 据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, circle, clock, doc, face,
                               hands_at, join, marker, partial, rect, stick, underline)

from .common import BOOK, episode

ACC = "#3B6FB6"
SQUARE_SHOT = 9                 # 场景 10：两根柱子对比 + 小周

b = Board(size=(6600, 9800))


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


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    return p


def badge(x, y, s=1.0) -> skia.Path:
    """小周的工牌：挂绳 + 小方牌。(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 20 * s, hy + 42 * s), (x, hy + 125 * s), (x + 20 * s, hy + 42 * s)),
                rect(x, hy + 152 * s, 46 * s, 56 * s, 6 * s))


def zhou(x, y, s, k0, arms="down", mood="flat", sfx="wood_high"):
    """主角小周：火柴人 + 五官 + 蓝色工牌，共 1 拍。"""
    L(stick(x, y, s, arms), k0, k0 + 0.7, BLACK, 10, sfx=sfx)
    L(face(x, y, s, mood), k0 + 0.7, k0 + 0.85, BLACK, 8)
    L(badge(x, y, s), k0 + 0.85, k0 + 1.0, BLUE, 7)


TOWER = dict(x=0.0, y0=0.0)


def tower(x, y, w=380, h=780, cols=3, rows=6):
    """写字楼：(x, y) 为底边中点；返回（路径，窗户中心函数）。"""
    def win(c, r):
        return x - w / 2 + 70 + c * (w - 140) / (cols - 1), y - h + 70 + r * 100

    parts = [P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y))]
    for r in range(rows):
        for c in range(cols):
            parts.append(rect(*win(c, r), 56, 56, 4))
    parts.append(P((x - 40, y), (x - 40, y - 80), (x + 40, y - 80), (x + 40, y)))
    return join(*parts), win


def fill_fn(path, color, alpha=0.9):
    """把一块区域慢慢涂满颜色。"""
    def fn(c, k, t):
        c.drawPath(path, K.paint(color, alpha * k))
        return None

    return fn


def dial(x, y, r=140) -> skia.Path:
    """刻度盘：上半圆 + 刻度 + 底边。(x, y) 为圆心。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 180, 180)
    parts = [p, P((x - r - 15, y), (x + r + 15, y))]
    for i in range(7):
        a = math.pi + i / 6 * math.pi
        parts.append(P((x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78),
                       (x + math.cos(a) * r * 0.95, y + math.sin(a) * r * 0.95)))
    return join(*parts)


def needle_fn(x, y, r, a1=-0.25):
    """刻度盘指针：从最左（零）甩到高处 a1（弧度，0 为最右）。"""
    def fn(c, k, t):
        a = math.pi + (2 * math.pi + a1 - math.pi) * ease_in_out(k)
        c.drawPath(P((x, y), (x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72)), marker(RED, 11))
        K.dot(c, x, y, 16, RED)
        return None

    return fn


def _ease_back(f):
    f = clamp01(f)
    return 1 + 2.4 * (f - 1) ** 3 + 1.4 * (f - 1) ** 2


def reddot_fn(keys, r=46, hop=90):
    """小红点：红色实心圆 + 白色数字 + 两条小短腿。keys=[(镜头, 拍, x, y, 数字)]，
    第一个关键帧弹出，之后每个关键帧前 0.3 秒跳过去，落地瞬间压扁一下、头顶冒“叮”。"""
    JUMP = 0.3

    def fn(c, k, T):
        ks = [(b.t_of(j, kk), x, y, n) for j, kk, x, y, n in keys]
        i = max(n for n, key in enumerate(ks) if key[0] <= T + 1e-6) if T >= ks[0][0] - 1e-6 else 0
        t_i, x, y, num = ks[i]
        lift = 0.0
        if i + 1 < len(ks) and T > ks[i + 1][0] - JUMP:
            f = clamp01((T - (ks[i + 1][0] - JUMP)) / JUMP)
            x = x + (ks[i + 1][1] - x) * f
            y = y + (ks[i + 1][2] - y) * f
            lift = hop * 4 * f * (1 - f)
        s = _ease_back((T - ks[0][0]) / 0.25)
        dt = T - t_i
        sq = 0.18 * math.exp(-dt * 18) if 0 <= dt and lift == 0 else 0.0
        sx, sy = s * (1 + sq), s * (1 - sq)
        y -= lift
        c.save()
        c.translate(x, y + r * 1.5)
        c.scale(sx, sy)
        c.translate(0, -r * 1.5)
        for d in (-1, 1):
            c.drawPath(P((d * r * 0.35, r * 0.8), (d * r * 0.42, r * 1.5), (d * r * 0.7, r * 1.5)), marker(BLACK, 7))
        c.drawCircle(0, 0, r, K.paint(RED))
        c.drawCircle(0, 0, r, K.paint("#9E2018", 1, 4))
        K.text(c, num, 0, 2, r * (1.05 if len(num) == 1 else 0.62), "black", "#FFFFFF")
        c.restore()
        if 0 <= dt < 0.5 and lift == 0:
            K.text(c, "叮", x + r * 1.3, y - r * 1.25, r * 0.95, "hand", RED, 1 - clamp01((dt - 0.3) / 0.2))
        return None

    return fn


def brick_fn(x, y, w, h, cuts, gap=24):
    """蓝色专注块：先描边，再填色；cuts=[(镜头, 拍, 位置 0–1)]，每到一刀就沿锯齿裂开，碎块往两边散。"""
    top, bot = y - h / 2, y + h / 2
    outline = rect(x, y, w, h, 8)

    def zig(fx):
        return [(x - w / 2 + fx * w + (16 if n % 2 else -16) * (0 if n in (0, 4) else 1), top + n * h / 4)
                for n in range(5)]

    def fn(c, k, T):
        if k < 1:
            part, tip = partial(outline, k)
            c.drawPath(part, marker(BLUE, 10))
            return tip
        act = sorted((fx, b.t_of(j, kk)) for j, kk, fx in cuts if T >= b.t_of(j, kk))
        edges = [[(x - w / 2, top), (x - w / 2, bot)]] + [zig(fx) for fx, _ in act] + [[(x + w / 2, top), (x + w / 2, bot)]]
        for i in range(len(edges) - 1):
            off = 0.0
            for m, (_, tm) in enumerate(act):
                off += (-1 if i <= m else 1) * gap * ease_in_out(clamp01((T - tm) / 0.25))
            drop = (8 if i % 2 else -6) * clamp01((T - act[-1][1]) / 0.3) if act else 0.0
            poly = P(*edges[i], *reversed(edges[i + 1]), close=True)
            poly.offset(off, drop)
            c.drawPath(poly, K.paint("#CFE0F7"))
            c.drawPath(poly, marker(BLUE, 10))
        for m, (fx, tm) in enumerate(act):
            a = 1 - clamp01((T - tm - 0.2) / 0.5)
            if a > 0:
                c.drawPath(P(*zig(fx)), marker(RED, 9, a))
        return None

    return fn


def tower_fn(x, base, crash, bw=230, bh=100, n=4):
    """“成果”塔：四块砖一块块垒上去；到 crash=(镜头, 拍) 那一刻哗地塌下来，散落在式子下方。"""
    rest = [(x - 300, 4770, -0.35), (x - 110, 4790, 0.55), (x + 120, 4775, -0.9), (x + 320, 4790, 0.25)]

    def fn(c, k, T):
        tc = b.t_of(*crash)
        for i in range(n):
            x0, y0 = x, base - bh / 2 - i * bh
            s = _ease_back((k * n - i) / 1.0)
            if s <= 0:
                continue
            px, py, ang = x0, y0, 0.0
            if T >= tc:
                f = clamp01((T - tc - i * 0.04) / 0.45)
                g = f * f
                tx, ty, ta = rest[i]
                px, py, ang = x0 + (tx - x0) * f, y0 + (ty - y0) * g, ta * f
            c.save()
            c.translate(px, py)
            c.rotate(math.degrees(ang))
            c.scale(s, s)
            blk = rect(0, 0, bw, bh, 8)
            c.drawPath(blk, K.paint("#F6D58E"))
            c.drawPath(blk, marker(BLACK, 9))
            c.restore()
        return None

    return fn


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 开局：晚上十点（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("十点还在工位", "灵魂拷问", (1150, 900, 0.85), bars=2)
TW, win = tower(750, 1330)
L(TW, 0, 0.9, BLACK, 9, sfx="wood_high")
WX, WY = win(2, 3)
C(1, 1.4, fill_fn(rect(WX, WY, 56, 56, 4), "#F5C542"), sfx="ding")
L(join(circle(1420, 820, 290), P((WX + 30, WY - 25), (1170, 690)), P((WX + 30, WY + 25), (1190, 990))),
  2, 2.9, BLACK, 8, sfx="wood_low")
zhou(1340, 1010, 0.6, 3, sfx="pop")
L(join(clock(1530, 690, 72), hands_at(1530, 690, 72, 10, 0)), 4, 4.8, RED, 8, sfx="wood_high")
T("晚上十点", 1420, 1200, 64, RED, k0=5, k1=6, sfx="pop")

scene("坐了一整天", "灵魂拷问", (2850, 900, 0.85))
AX0, AX1, AY = 2350, 3350, 800
T("9:00", AX0, AY - 100, 60, k0=0, k1=1, sfx="pop")
for n, (a, c_) in enumerate(((AX0, 2690), (2690, 3030), (3030, AX1))):
    L(join(P((a, AY), (c_, AY)), P((c_, AY - 22), (c_, AY + 22))), 1 + n, 1.9 + n, BLACK, 10,
      sfx="wood_high" if n % 2 == 0 else "wood_low")
T("21:00", AX1, AY - 100, 60, k0=4, k1=5, sfx="pop")
L(join(P((AX0, AY + 60), (AX0, AY + 100), (AX1, AY + 100), (AX1, AY + 60)), P((2850, AY + 100), (2850, AY + 140))),
  5, 5.9, RED, 8, sfx="wood_low")
T("12 小时", 2850, AY + 230, 96, RED, k0=6, k1=7.5, sfx="tom")

scene("方案才写一页", "灵魂拷问", (2850, 2300, 0.85))
L(doc(2700, 2300, 520, 680, lines=0), 0, 0.9, BLACK, 9, sfx="wood_high")
T("方案", 2700, 2060, 64, k0=1, k1=1.8, sfx="pop")
L(P((2510, 2180), (2890, 2180)), 2, 2.8, BLACK, 8, sfx="wood_low")
L(P((2510, 2260), (2780, 2260)), 3, 3.6, BLACK, 8, sfx="wood_low")
zhou(3260, 2620, 0.6, 4, arms="shrug", mood="sad")
T("1 页", 2700, 2480, 96, RED, k0=5, k1=5.8, sfx="pop")
L(oval(2700, 2480, 170, 95), 6, 6.9, RED, 9, sfx="rim")

# ---------------------------------------------------------------- drop：式子塌了（场景 4）

VF = (2000, 4500, 0.6)
FORM, FY, FS = "成果 = 时间 × 专注", 4300, 160
_fx0 = 2000 - K.text_w(FORM, FS, "hand") / 2


def _cx(word):
    i = FORM.index(word)
    return _fx0 + K.text_w(FORM[:i], FS, "hand") + K.text_w(word, FS, "hand") / 2


XG, XT, XZ = _cx("成果"), _cx("时间"), _cx("专注")
VY = 4560                       # 式子下方一格的数值行

j_drop = scene("专注是零", "一个式子", VF, shake=[0, 5], flashes=[0])
T(FORM, 2000, FY, FS, k0=0, k1=1.9, sfx="kick")
T("12 小时", XT, VY, 90, k0=2, k1=3, sfx="pop")
C(3, 3.8, tower_fn(XG, FY - 95, (j_drop, 5)), sfx="wood_low")
T("0", XZ, VY, 120, RED, k0=4, k1=4.8, sfx="rim")
H(5, "kick", 0.9)
T("0", XG, VY, 130, RED, k0=6, k1=6.8, sfx="tom")
L(circle(XZ, VY, 95), 7, 7.8, RED, 10, sfx="ding")

# ---------------------------------------------------------------- 亮书 + 书中观点：两种活（场景 5–7）

scene("一本讲专注的书", "《深度工作》", (5650, 4050, 0.85))
L(book(5450, 4060, 440, 300), 0, 0.9, BLACK, 9, sfx="wood_low")
T("《深度工作》", 5450, 3700, 72, GREEN, k0=1, k1=2.5, sfx="pop")
L(stick(6000, 4200, 0.7, "point"), 3, 3.8, BLACK, 9, sfx="wood_high")
L(rect(6000, 4330, 380, 90, 12), 4, 4.8, BLACK, 8, sfx="wood_low")
T("卡尔·纽波特", 6000, 4330, 54, k0=5, k1=6.5, sfx="pop")

VK = (5650, 5850, 0.62)
LX, RX = 5250, 6050
scene("活分两种", "书中观点 · 两种活", VK)
L(rect(LX, 5350, 460, 200, 10), 0, 0.9, BLUE, 12, sfx="wood_high")
T("难活儿", LX, 5350, 84, BLUE, k0=1, k1=1.8, sfx="pop")
T("写方案、学新技能", LX, 5560, 64, k0=2, k1=4, sfx="pop")
L(rect(RX, 5350, 460, 200, 10), 4, 4.8, BLACK, 9, sfx="wood_low")
T("浮活", RX, 5350, 84, k0=5, k1=5.8, sfx="pop")
T("回消息、填表", RX, 5560, 64, k0=6, k1=7.5, sfx="pop")

scene("难活儿难替代", "书中观点 · 难替代", VK)
for n, x in enumerate((RX - 170, RX, RX + 170)):
    L(stick(x, 6350, 0.5), n, n + 0.8, BLACK, 9, sfx="pop")
T("换谁都行", RX, 6460, 70, k0=3, k1=4, sfx="rim")
zhou(LX, 6350, 0.55, 4, mood="smile")
T("换人就难", LX, 6460, 70, BLUE, k0=5, k1=6, sfx="pop")
L(underline(LX - 150, LX + 150, 6515, 10, 30), 6, 6.8, BLUE, 8, sfx="ding")

# ---------------------------------------------------------------- 回到式子（场景 8）

scene("时间乘专注", "书中观点 · 式子", VF)
b.erase(J(), 0, 0.9, 2000, 4680, 1800, 440)
H(0, "shaker")
L(join(rect(XT, 4580, 420, 60, 10), *[P((XT - 180 + n * 60, 4555), (XT - 200 + n * 60, 4605)) for n in range(7)]),
  1, 1.9, BLACK, 8, sfx="wood_high")
T("坐多久", XT, 4700, 72, k0=2, k1=2.8, sfx="pop")
L(dial(XZ, 4660, 140), 3, 3.9, BLACK, 8, sfx="wood_low")
C(4, 4.8, needle_fn(XZ, 4660, 140), sfx="tom")
T("多投入", XZ, 4760, 72, k0=5, k1=5.8, sfx="pop")
T("书里给的式子", 2000, 3990, 80, GREEN, k0=6, k1=7.5, sfx="ding")

# ---------------------------------------------------------------- 小红点：一叮就碎（场景 9–10）

BX, BY, BW, BH = 1100, 6250, 760, 230
CUTS = (0.27, 0.52, 0.76)


def _land(fx):
    return BX - BW / 2 + fx * BW, BY - BH / 2 - 46 * 1.5 - 6


j_cut = scene("一叮就碎", "小红点来了", (1150, 6100, 0.85))
C(0, 0.9, brick_fn(BX, BY, BW, BH, [(j_cut, 3 + n, fx) for n, fx in enumerate(CUTS)]), sfx="wood_high")
T("专注块", BX, 5800, 64, BLUE, k0=1, k1=1.8, sfx="pop")
C(2, 2.4, reddot_fn([(j_cut, 2, 1620, 5860, "1")] + [(j_cut, 3 + n, *_land(fx), str(n + 1)) for n, fx in enumerate(CUTS)]),
  sfx="ding")
for n in range(3):
    H(3 + n, "ding")
    H(3 + n, "rim", 0.6)
T("拼不回", BX, 6500, 76, RED, k0=6, k1=7, sfx="tom")

BASE = 6450
scene("少坐也能多干", "示意 · 两根柱子", (2850, 6100, 0.85))
L(P((2250, BASE), (3380, BASE)), 0, 0.9, BLACK, 9, sfx="wood_low")
L(join(*[rect(2650 + (-14, 10, -6)[n], BASE - 45 - n * 82, 200 - n * 30, 66, 6) for n in range(3)]),
  1, 1.9, BLACK, 8, sfx="wood_high")
T("12 小时 碎块", 2650, BASE + 85, 50, k0=2, k1=3.5, sfx="pop")
TALL = rect(3120, BASE - 300, 200, 600, 8)
L(TALL, 3, 3.9, BLUE, 10, sfx="wood_high")
C(4, 4.8, fill_fn(TALL, "#CFE0F7", 1.0), sfx="tom")
T("4 小时 整块", 3120, BASE + 85, 50, BLUE, k0=5, k1=6.5, sfx="pop")
T("成果（示意）", 2850, 5710, 60, k0=6, k1=7.25, sfx="ding")
zhou(2350, BASE, 0.55, 7, arms="point", mood="smile")

# ---------------------------------------------------------------- 做法（场景 11–12）

CX, CW, H9 = 950, 360, 7290    # 日历：一天一列，每小时 80
scene("先留一整块", "做法一 · 留一整块", (1150, 7550, 0.85))
L(join(rect(CX, 7600, CW, 860, 12), P((CX - CW / 2, 7250), (CX + CW / 2, 7250))), 0, 0.9, BLACK, 9, sfx="wood_high")
L(join(*[P((CX - CW / 2, H9 + n * 80), (CX - CW / 2 + 40, H9 + n * 80)) for n in range(10)]), 1, 1.8, BLACK, 6,
  sfx="wood_low")
T("9:00", CX - CW / 2 - 85, H9, 46, k0=2, k1=2.8, sfx="pop")
BLK = rect(CX + 20, H9 + 80, CW - 70, 160, 10)
C(3, 3.8, fill_fn(BLK, "#9DBCEB", 0.85), sfx="tom")
L(BLK, 3, 3.9, BLUE, 10)
T("专注块", CX + 20, H9 + 80, 54, BLUE, k0=4, k1=4.8, sfx="pop")
T("9–11 点不看消息", 1460, 7130, 52, RED, k0=5, k1=6.75, sfx="pop")
L(arrow((1400, 7180), (CX + CW / 2 - 10, H9 + 60), -0.25, 36), 7, 7.8, RED, 8, sfx="wood_high")

DX, DY = 2700, 7800             # 柜子
scene("手机放远点", "做法二 · 手机放远", (2850, 7550, 0.85))
L(join(rect(DX, DY, 560, 400, 12), rect(DX, DY - 100, 500, 150, 8), circle(DX, DY - 100, 14),
       P((DX - 230, DY + 200), (DX - 230, DY + 240)), P((DX + 230, DY + 200), (DX + 230, DY + 240))),
  0, 0.9, BLACK, 9, sfx="wood_low")
L(join(rect(2380, 7250, 130, 220, 18), P((2360, 7330), (2400, 7330))), 1, 1.8, BLACK, 9, sfx="pop")
L(arrow((2470, 7250), (2640, 7640), -0.25, 36), 2, 2.8, BLACK, 8, sfx="wood_high")
C(3, 3.4, reddot_fn([(J(), 3, DX + 120, DY - 145, "99+"), (J(), 4, DX + 120, DY - 145, "99+"),
                     (J(), 5, DX + 120, DY - 145, "99+")], r=40, hop=40), sfx="ding")
H(4, "shaker", 0.6)
zhou(3270, 7720, 0.6, 5, arms="hold", mood="smile")
T("够不着，就不摸", 2850, 8110, 60, RED, k0=6, k1=7.75, sfx="pop")

# ---------------------------------------------------------------- 拉远看全板（场景 13）

scene("护住专注", "拉远看全板", (2454, 5990, 0.22))
H(0, "shaker")
L(oval(BX, BY, 500, 270), 2, 2.9, RED, 36, sfx="rim")
L(oval(CX + 20, H9 + 80, 280, 160), 3, 3.9, GREEN, 36, sfx="ding")
L(oval(XZ, FY, 220, 130), 4, 4.9, RED, 36, sfx="wood_high")
T("护住专注", 4200, 5900, 230, BLUE, k0=5, k1=6, sfx="pop")
L(underline(3740, 4660, 6040, 30, 80), 7, 7.8, BLUE, 30, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：从全板推到评论区

scene("评论区聊聊", "评论区见", (2000, 9000, 0.8), bars=4)
H(0, "cymbal", 0.5)
L(bubble(2000, 8800, 1000, 300, -1), 2, 2.9, BLACK, 9, sfx="wood_high")
T("你一天能有几小时", 2000, 8745, 72, RED, k0=4, k1=6, sfx="pop")
T("不被打断？", 2000, 8860, 72, RED, k0=6, k1=7.25, sfx="pop")
C(8, 8.4, reddot_fn([(J(), 8, 2560, 8530, "1")], r=40), sfx="ding")
T("下一讲：回条消息，怎么半天回不了神？", 2000, 9180, 46, k0=9, k1=13.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "value", "专注值钱", "加班到十点，活怎么还没干完？", ACC, b.shots,
                 [f"{BOOK}前言（两类工作的区分）、第1章“深度工作是有价值的”（高质量工作产出 = 时间 × 专注度），转述",
                  "中译本：《深度工作：如何有效使用每一点脑力》，宋伟译，江西人民出版社 · 后浪 2017；民主与建设出版社 · 后浪 2023"],
                 "加班到十点|活怎么还【没干完】", SQUARE_SHOT,
                 ["书中观点均为转述：前言把工作分成两类——不被打扰、专心做难事，能出新东西、能长本事、难被替代（书中称"
                  "深度工作）；不太费脑、常在分心状态下做的杂事，谁来做都差不多（书中称浮浅工作）。第1章给出式子"
                  "“高质量工作产出 = 时间 × 专注度”，上屏用白话写作“成果 = 时间 × 专注”。具体措辞以中译本为准；"
                  "上屏均为转述，不是逐字引文。章节名不上屏。",
                  "卡尔·纽波特只画火柴人 + 名牌，不画肖像。",
                  "晚上十点加班、一天坐十二小时、方案只写一页、“成果”塔塌成 0、专注块被小红点切碎，均为现实场景示意与对"
                  "书中式子的通俗化演示；“12 小时碎块 vs 4 小时整块”两根柱子的高低为示意，不是数据。",
                  "“早上先留一整块、9–11 点不看消息”“手机放进抽屉”为据书中思路整理的做法，时间点为示意。",
                  "不指向任何具体公司、软件或个人。"],
                 tags="#加班")
    return b.attach(ep)
