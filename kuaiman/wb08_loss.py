"""08 损失厌恶（白板手绘版）：赢150输100，你敢赌吗？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（形式 C 复刻实验）：快快抛起一枚硬币 → 规则牌“正面赢 150 元、反面输 100 元” → 快快的手悬在“赌 / 不赌”
两个按钮上，倒数 3、2、1，先让观众自己决定 → drop：天平“输100”那头重重砸到底，“赢150”翘在天上，
“多数人：不赌” → 亮书（快快、慢慢出场，“损失厌恶”）→ 书中观点（一根尺：输 100，要赢 150–250 才肯赌）→
第二个实验（马克杯：拿着杯子的人要价高，想买的人出价低）→ 身边的例子（想跳槽又舍不得旧工位、做了一半的旧方案
舍不得换、外卖涨两块心疼半天，降两块没感觉）→ 做法（一百次一起看总账 / 少看账户，手机扣过来 /
假设没有它，还会买吗）→ 拉远看全板 → 评论区互动 + 下一讲。
书中观点为转述：丹尼尔·卡尼曼《思考，快与慢》第26章“更人性化的前景理论”（Prospect Theory，抛硬币赌局与损失
厌恶系数）、第27章“禀赋效应与市场交易”（The Endowment Effect，马克杯实验）、第31章“能带来长远收益的风险政策”
（Risk Policies，宽框架、少看投资账户）；中译本胡晓姣、李爱民、何梦莹译，中信出版社 2012。
例子与做法为现实场景示意与据书中思路整理的建议；题目把美元换成元。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_out
from whiteboard import engine as wb  # noqa: F401
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, doc,
                               face, join, partial, rect, stick, underline)

from .common import BOOK, episode, kuai, man

ACC = "#B8892A"                 # 本讲主色：硬币金
GOLD = ACC
SQUARE_SHOT = 3                 # 场景 4：天平“输100”砸到底 + 快快

b = Board(size=(3600, 9800))


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


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def mug(x, y, s=1.0) -> skia.Path:
    """马克杯：(x, y) 为杯身中心，把手在右。"""
    hd = skia.Path()
    hd.addArc(skia.Rect.MakeXYWH(x + 30 * s, y - 40 * s, 70 * s, 80 * s), -80, 160)
    return join(P((x - 60 * s, y - 70 * s), (x - 52 * s, y + 70 * s), (x + 52 * s, y + 70 * s), (x + 60 * s, y - 70 * s),
                  close=True), hd)


def price_tag(x, y, w=280, h=110) -> skia.Path:
    """价签：左端尖、带一个穿绳孔。"""
    l, r, t, btm = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    return join(P((l, y), (l + 45, t), (r, t), (r, btm), (l + 45, btm), close=True), circle(l + 40, y, 9))


def door(x, y, w=300, h=520) -> skia.Path:
    """门：(x, y) 为门底中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                circle(x + w / 2 - 45, y - h / 2, 14), P((x - w / 2 - 40, y), (x + w / 2 + 40, y)))


def plus(x, y, r=26) -> skia.Path:
    return join(P((x - r, y), (x + r, y)), P((x, y - r), (x, y + r)))


def minus(x, y, r=26) -> skia.Path:
    return P((x - r, y), (x + r, y))


def dashed(path: skia.Path, on=26.0, off=18.0) -> skia.Path:
    """把路径切成虚线段（每段一条轮廓，描线时逐段画出）。"""
    out = skia.Path()
    pm = skia.PathMeasure(path, False)
    while True:
        n, d = pm.getLength(), 0.0
        while d < n:
            seg = skia.Path()
            pm.getSegment(d, min(n, d + on), seg, True)
            out.addPath(seg)
            d += on + off
        if not pm.nextContour():
            break
    return out


def zigzag(x0, x1, y, amp=60, n=6) -> skia.Path:
    pts = [(x0 + (x1 - x0) * i / n, y + (amp if i % 2 else -amp) * (0.4 + 0.6 * ((i * 7) % 5) / 4)) for i in range(n + 1)]
    return P(*pts)


def fill_fn(x, y, w, h, color, alpha=0.3):
    """从左往右填一块半透明色（进度条、区间高亮）。"""

    def fn(c, k, t):
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w * k, h), K.paint(color, alpha))
        return (x - w / 2 + w * k, y) if k < 1 else None

    return fn


# ---------------------------------------------------------------- 开局：抛硬币，赌不赌（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

ox, oy = 950, 900
j_coin = scene("来抛个硬币", "灵魂拷问", (ox, oy, 0.85), bars=2)
KX, KY, KS = ox - 220, oy + 420, 0.75
L(join(kuai(KX, KY, KS, "up"), face(KX, KY, KS, "smile")), 0, 0.9, RED, 9, sfx="wood_high")
C0 = (KX + 60 * KS, KY - 290 * KS - 40 * KS)        # 抛出点：快快举起的右手
C1 = (ox + 200, oy - 170)                            # 硬币停在空中的位置
CR = 105


def coin_fn(c, k, t):
    """硬币从快快手里飞起，在空中翻三圈（正、反两面交替），最后正面朝前停在空中。"""
    f = ease_out(clamp01(k / 0.45))
    x = C0[0] + (C1[0] - C0[0]) * f
    y = C0[1] + (C1[1] - C0[1]) * f - 120 * math.sin(math.pi * f) * (1 - f)
    a = k * 3 * 2 * math.pi
    sx = math.cos(a)
    c.save()
    c.translate(x, y)
    c.scale(max(0.06, abs(sx)), 1)
    c.drawCircle(0, 0, CR, K.paint("#F6E7B8"))
    c.drawCircle(0, 0, CR, K.paint(GOLD, 1, 9))
    c.drawCircle(0, 0, CR * 0.78, K.paint(GOLD, 0.8, 5))
    if abs(sx) > 0.25:
        K.text(c, "正" if sx > 0 else "反", 0, 4, 88, "hand", BLACK)
    c.restore()
    return None


b.custom(j_coin, 1, 4, coin_fn, sfx="pop")
H(2, "shaker", 0.6)
H(3, "shaker", 0.6)
T("正面？反面？", ox + 200, oy - 400, 70, BLACK, k0=4, k1=5.4, sfx="pop")
spin = skia.Path()
spin.addArc(skia.Rect.MakeXYWH(C1[0] - 170, C1[1] - 150, 340, 300), 200, 60)
spin.addArc(skia.Rect.MakeXYWH(C1[0] - 170, C1[1] - 150, 340, 300), 20, 60)
L(spin, 5.5, 6.0, GOLD, 8)

ox, oy = 2650, 900
scene("赢多输少", "游戏规则", (ox, oy, 0.85))
L(rect(ox, oy + 30, 1040, 760, 30), 0, 0.9, BLACK, 9, sfx="wood_high")
T("规则", ox, oy - 250, 76, k0=1, k1=1.8, sfx="pop")
T("正面", ox - 270, oy - 40, 84, k0=2, k1=2.8, sfx="pop")
T("赢150元", ox + 150, oy - 40, 100, GREEN, k0=3, k1=4.5, sfx="ding")
T("反面", ox - 270, oy + 220, 84, k0=5, k1=5.8, sfx="pop")
T("输100元", ox + 150, oy + 220, 100, RED, k0=6, k1=7.5, sfx="rim")
L(P((ox - 430, oy + 90), (ox + 430, oy + 90)), 7.5, 8.0, BLACK, 5)

ox, oy = 2650, 2250
scene("赌不赌？", "你来选", (ox, oy, 0.85))
KX, KY, KS = ox - 300, oy + 420, 0.8
L(join(kuai(KX, KY, KS, "point"), face(KX, KY, KS, "flat")), 0, 0.9, RED, 9, sfx="wood_high")
B1, B2 = (ox + 20, oy + 220), (ox + 330, oy + 220)
L(rect(*B1, 240, 140, 30), 1, 1.6, GREEN, 9, sfx="pop")
T("赌", B1[0], B1[1], 84, GREEN, k0=1.6, k1=2.4)
L(rect(*B2, 240, 140, 30), 3, 3.6, RED, 9, sfx="pop")
T("不赌", B2[0], B2[1], 76, RED, k0=3.6, k1=4.4)
CK = (ox - 180, oy - 230)
L(clock(*CK, 110), 4.5, 5.0, BLACK, 8)
for n, s in enumerate("321"):
    T(s, ox + 60 + n * 150, oy - 230, 110 - n * 10, RED, k0=5 + n, k1=5.8 + n, sfx="tom")

# ---------------------------------------------------------------- drop：天平砸到底（场景 4）

ox, oy = 950, 2250
j_drop = scene("大多数人不赌", "多数人的选择", (ox, oy, 0.75), shake=[0, (4, 20.0)], flashes=[0])
T("多数人：不赌", ox, oy - 530, 104, RED, k0=0, k1=1.5, sfx="kick")
PV = (ox + 80, oy - 180)                     # 天平支点
BR, SL, PW = 480, 260, 260                   # 横梁半长、吊绳长、秤盘宽
TILT = math.radians(24)
L(join(P(PV, (PV[0], oy + 520)), P((PV[0] - 200, oy + 520), (PV[0], oy + 400), (PV[0] + 200, oy + 520), close=True),
       circle(*PV, 16)), 1, 1.9, BLACK, 10, sfx="wood_low")


def _scale_path(a):
    ca, sa = math.cos(a), math.sin(a)
    ends = [(PV[0] - BR * ca, PV[1] - BR * sa), (PV[0] + BR * ca, PV[1] + BR * sa)]
    parts = [P(*ends)]
    pans = []
    for ex, ey in ends:
        ry = ey + SL
        parts += [P((ex - PW / 2, ry), (ex, ey), (ex + PW / 2, ry))]
        bowl = skia.Path()
        bowl.addArc(skia.Rect.MakeXYWH(ex - PW / 2, ry - 60, PW, 120), 0, 180)
        parts += [bowl, P((ex - PW / 2 - 10, ry), (ex + PW / 2 + 10, ry))]
        pans.append((ex, ry))
    return join(*parts), pans


def scale_fn(c, k, t):
    """第 2 拍画出水平的横梁和秤盘，第 3 拍两只盘里弹出“赢150”“输100”，第 4 拍“输100”那头砸到底，回弹两下。"""
    t2, t3, t4 = (b.t_of(j_drop, kk) for kk in (2, 3, 4))
    d = clamp01((t - t2) / max(1e-3, (t3 - t2) * 0.9))
    if t < t4:
        a = 0.0
    else:
        u = t - t4
        a = TILT * (min(1.0, ease_out(u / 0.12)) + 0.1 * math.exp(-u * 9) * math.sin(u * 38))
    path, pans = _scale_path(a)
    part, tip = partial(path, d)
    c.drawPath(part, wb.marker(BLACK, 10))
    if t >= t3:
        g = ease_out(clamp01((t - t3) / 0.16))
        for (px, py), s, col in zip(pans, ("赢150", "输100"), (GREEN, RED)):
            K.text(c, s, px, py + 110, 70 * (0.6 + 0.4 * g), "hand", col, g)
    return tip


b.custom(j_drop, 2, 3, scale_fn, sfx="wood_high")
H(3, "pop")
H(4, "kick")
T("重！", ox + 250, oy + 300, 90, RED, k0=5, k1=5.8, sfx="rim")
KX, KY, KS = ox - 470, oy + 600, 0.55
L(join(kuai(KX, KY, KS, "shrug"), face(KX, KY, KS, "sad")), 6, 6.9, RED, 9, sfx="wood_high")
T("怕输", KX + 170, KY - 230, 60, RED, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 5–7）

ox, oy = 950, 3600
scene("输比赢更疼", "思考，快与慢 · 书中观点", (ox, oy, 0.85))
L(book(ox - 200, oy - 200, 420, 280), 0, 0.9, BLACK, 9, sfx="wood_low")
T("思考，快与慢", ox - 200, oy - 420, 66, GREEN, k0=1, k1=2.5, sfx="pop")
T("卡尼曼", ox - 200, oy + 10, 54, k0=3, k1=3.8, sfx="pop")
L(join(kuai(ox + 200, oy + 220, 0.6, "up"), face(ox + 200, oy + 220, 0.6, "sad")), 4, 4.9, RED, 9, sfx="wood_high")
L(join(man(ox + 450, oy + 220, 0.6), face(ox + 450, oy + 220, 0.6, "flat")), 5, 5.9, BLUE, 9, sfx="wood_low")
T("损失厌恶", ox, oy + 380, 100, RED, k0=6, k1=7.0, sfx="ding")
L(underline(ox - 220, ox + 220, oy + 450), 7, 7.8, RED, 8, sfx="rim")

ox, oy = 2650, 3600
scene("赢得多一倍，才肯赌", "书中观点 · 要赢多少", (ox, oy, 0.85))
T("输 100", ox - 330, oy - 380, 90, RED, k0=0, k1=1.25, sfx="rim")
RX0, RX1, RY = ox - 520, ox + 560, oy + 20


def vx(v):
    return ox - 400 + (v - 100) * 6.4      # 尺上 100 → 250 的位置


ruler = [P((RX0, RY), (RX1, RY))] + [P((vx(v), RY - 30), (vx(v), RY + 30)) for v in range(100, 275, 25)]
L(join(*ruler), 1, 1.9, BLACK, 9, sfx="wood_high")
for n, v in enumerate((100, 150, 250)):
    T(str(v), vx(v), RY + 100, 66, RED if v == 100 else GREEN, k0=2 + n, k1=2.8 + n, sfx="pop")
b.custom(J(), 5, 5.6, fill_fn((vx(150) + vx(250)) / 2, RY - 70, vx(250) - vx(150), 80, GREEN, 0.3), sfx="ding")
L(arrow((ox - 330, oy - 310), (vx(100), RY - 50), 0.1, 36), 5.6, 6.0, RED, 8)
T("赢这么多才肯赌", (vx(150) + vx(250)) / 2, oy - 180, 70, GREEN, k0=6, k1=7.75, sfx="pop")

ox, oy = 2650, 4950
scene("到手的杯子更值钱", "书中实验 · 马克杯", (ox, oy, 0.85))
AX, BX, SY, SS = ox - 360, ox + 360, oy + 400, 0.75
L(join(stick(AX, SY, SS, "hold"), face(AX, SY, SS, "smile")), 0, 0.9, BLACK, 9, sfx="wood_high")
L(mug(AX + 115 * SS + 30, SY - 290 * SS + 60 * SS, 0.7), 1, 1.8, GOLD, 9, sfx="pop")
L(join(stick(BX, SY, SS, "down"), face(BX, SY, SS, "flat")), 2, 2.9, BLUE, 9, sfx="wood_high")
TA, TB = (AX, oy - 330), (BX, oy - 130)
L(price_tag(*TA, 300, 120), 3, 3.6, RED, 8, sfx="pop")
T("要价高", TA[0] + 20, TA[1], 64, RED, k0=3.6, k1=4.4)
L(price_tag(*TB, 300, 120), 5, 5.6, BLUE, 8, sfx="pop")
T("出价低", TB[0] + 20, TB[1], 64, BLUE, k0=5.6, k1=6.4)
L(join(arrow((AX + 220, oy - 250), (AX + 220, oy - 470), 0, 34), arrow((BX - 220, oy - 210), (BX - 220, oy - 10), 0, 34)),
  7, 7.8, BLACK, 8, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

ox, oy = 950, 4950
scene("想跳，又舍不得", "例子 · 跳槽", (ox, oy, 0.85))
D1, D2, DY = ox - 350, ox + 350, oy + 300
L(door(D1, DY), 0, 0.9, BLACK, 9, sfx="wood_high")
T("旧工位", D1, DY - 600, 64, k0=1, k1=1.8, sfx="pop")
L(door(D2, DY), 2, 2.9, GREEN, 9, sfx="wood_high")
T("新公司", D2, DY - 600, 64, GREEN, k0=3, k1=3.8, sfx="pop")
for n in range(3):
    T("舍不得", D1 - 10, DY - 420 + n * 130, 50, RED, k0=4 + n, k1=4.8 + n, sfx="pop")
L(join(kuai(ox, oy + 440, 0.5, "shrug"), face(ox, oy + 440, 0.5, "flat")), 7, 7.9, RED, 9, sfx="wood_high")

ox, oy = 950, 6300
scene("旧方案舍不得换", "例子 · 旧方案", (ox, oy, 0.85))
DX = ox - 300
L(join(doc(DX + 40, oy - 140, 260, 320), doc(DX + 20, oy - 120, 260, 320), doc(DX, oy - 100, 260, 320)), 0, 0.9, BLACK, 8,
  sfx="wood_high")
T("做了一半", DX, oy - 400, 64, k0=1, k1=2.0, sfx="pop")
L(rect(DX, oy + 130, 300, 50, 12), 2, 2.8, BLACK, 7, sfx="wood_high")
b.custom(J(), 3, 3.6, fill_fn(DX - 75, oy + 130, 150, 50, BLUE, 0.45), sfx="pop")
L(doc(ox + 330, oy - 120, 260, 320), 4, 4.9, GREEN, 9, sfx="wood_high")
T("新方案", ox + 330, oy - 400, 64, GREEN, k0=5, k1=5.8, sfx="pop")
L(join(man(ox + 40, oy + 470, 0.55), face(ox + 40, oy + 470, 0.55, "flat")), 6, 6.8, BLUE, 9, sfx="wood_low")
T("舍不得", DX, oy + 270, 64, RED, k0=7, k1=7.8, sfx="rim")

ox, oy = 2650, 6300
scene("涨两块心疼半天", "例子 · 外卖", (ox, oy, 0.85))
PX = ox - 280
L(join(rect(PX, oy, 380, 700, 40), P((PX - 50, oy + 300), (PX + 50, oy + 300))), 0, 0.9, BLACK, 9, sfx="wood_high")
T("外卖", PX, oy - 250, 60, k0=1, k1=1.8, sfx="pop")
T("+2 元", PX, oy - 100, 88, RED, k0=2, k1=3.0, sfx="rim")
KX, KY = ox + 280, oy + 450
L(join(kuai(KX, KY, 0.6, "hold"), face(KX, KY, 0.6, "sad")), 3, 3.9, RED, 9, sfx="wood_high")
L(bubble(KX + 80, oy - 300, 260, 120, -1), 4, 4.6, RED, 8, sfx="tom")
T("心疼！", KX + 80, oy - 300, 60, RED, k0=4.6, k1=5.4)
T("-2 元", PX, oy + 70, 88, GREEN, k0=6, k1=7.0, sfx="pop")
T("没感觉", PX, oy + 190, 54, BLUE, k0=7, k1=7.8, sfx="wood_low")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

ox, oy = 2650, 7650
scene("合起来算总账", "做法一 · 合起来看", (ox, oy, 0.85))
T("① 一百次一起看", ox, oy - 420, 74, BLUE, k0=0, k1=1.8, sfx="pop")
XS = [ox - 400 + n * 200 for n in range(5)]
L(join(*[circle(x, oy - 200, 62) for x in XS]), 2, 2.9, GOLD, 8, sfx="wood_high")
L(join(*[plus(XS[n], oy - 200) for n in (0, 2, 3)]), 3, 3.6, GREEN, 9, sfx="pop")
L(join(*[minus(XS[n], oy - 200) for n in (1, 4)]), 4, 4.5, RED, 9, sfx="pop")
L(arrow((ox, oy - 110), (ox, oy + 30), 0, 36), 5, 5.6, BLACK, 8, sfx="wood_high")
T("总账：赚", ox, oy + 130, 90, GREEN, k0=6, k1=7.0, sfx="ding")
L(join(man(ox + 400, oy + 480, 0.5), face(ox + 400, oy + 480, 0.5, "smile")), 7, 7.8, BLUE, 9, sfx="wood_low")

ox, oy = 950, 7650
scene("少盯着看", "做法二 · 少看账户", (ox, oy, 0.85))
T("② 少看账户", ox, oy - 420, 76, BLUE, k0=0, k1=1.5, sfx="pop")
PX, PY = ox - 300, oy - 60
L(join(rect(PX, PY, 260, 420, 30), zigzag(PX - 90, PX + 90, PY - 20, 50, 6)), 2, 2.9, BLACK, 8, sfx="wood_high")
L(arrow((PX + 170, PY - 120), (ox + 170, oy + 60), -0.3, 36), 3, 3.8, BLUE, 8, sfx="wood_low")
L(join(P((ox + 30, oy + 170), (ox + 560, oy + 170)), rect(ox + 300, oy + 140, 360, 50, 14)), 4, 4.9, BLACK, 9,
  sfx="wood_high")
L(join(kuai(PX, oy + 480, 0.45, "down"), face(PX, oy + 480, 0.45, "smile")), 6, 6.8, RED, 9, sfx="pop")
L(check(ox + 300, oy - 60, 55), 7, 7.6, GREEN, 10, sfx="ding")

ox, oy = 950, 9000
scene("没到手，还会买吗", "做法三 · 假设没有它", (ox, oy, 0.85))
T("③ 假设没有它", ox, oy - 420, 74, BLUE, k0=0, k1=1.75, sfx="pop")
L(dashed(mug(ox + 260, oy + 20, 1.3)), 2, 2.9, GOLD, 9, sfx="wood_high")
MX, MY = ox - 330, oy + 470
L(join(man(MX, MY, 0.62), face(MX, MY, 0.62, "flat")), 3, 3.9, BLUE, 9, sfx="wood_low")
L(bubble(MX + 60, oy - 180, 400, 130, -1), 4, 4.6, BLUE, 8, sfx="pop")
T("现在会买吗？", MX + 60, oy - 180, 56, BLUE, k0=4.6, k1=6.0)
T("不会买，就放手", ox + 220, oy + 300, 62, RED, k0=6, k1=7.75, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 4900, 0.1)
CMT = (2650, 9000, 0.85)
ox, oy = CMT[:2]
j_end = scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(j_end, 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("这把你赌不赌？", ox, oy - 320, 84, RED, k0=6, k1=7.75, sfx="pop")
L(join(kuai(ox - 260, oy + 440, 0.6, "up"), face(ox - 260, oy + 440, 0.6, "smile")), 9, 9.8, RED, 9, sfx="wood_high")
L(join(man(ox + 260, oy + 440, 0.6), face(ox + 260, oy + 440, 0.6, "smile")), 10, 10.8, BLUE, 9, sfx="wood_low")
T("下一讲：同一件事，换个说法就变了？", ox, oy - 140, 46, k0=11, k1=15.25, sfx="pop")
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "loss", "损失厌恶", "赢150输100，你敢赌吗？", ACC, b.shots,
                 [f"{BOOK}第26章 更人性化的前景理论（Prospect Theory）（转述）",
                  f"{BOOK}第27章 禀赋效应与市场交易（The Endowment Effect）（转述）",
                  f"{BOOK}第31章 能带来长远收益的风险政策（Risk Policies）（转述）",
                  "中译本：胡晓姣、李爱民、何梦莹译，中信出版社 2012"],
                 "赢150输100|你敢【赌】吗", SQUARE_SHOT,
                 ["书中观点均为转述：抛硬币，反面输 100 美元、正面赢 150 美元，多数人不愿意赌；损失带来的难受比同样大小的"
                  "收获带来的高兴更强，书中提到损失厌恶系数大致在 1.5 到 2.5 之间（第 26 章）。题目把美元换成元，数字不变。"
                  "尺上“100 → 150 ~ 250”为书中数据换算（1.5 到 2.5 倍）；天平画面为通俗化示意。",
                  "马克杯实验：拿到杯子的人要价明显高于想买的人愿意出的价（禀赋效应，第 27 章）；价签只写高低，不写书中具体金额。",
                  "宽框架：把很多次小赌合起来看，比一次一次看更合理；少看投资账户能少受损失带来的难受（第 31 章）。"
                  "“一百次一起看”的硬币正负排列为示意，不是数据。",
                  "跳槽、做了一半的旧方案、外卖涨价两元为现实场景示意，不指向任何具体公司或个人。",
                  "三步做法中“一百次一起看”“少看账户”据书中第 31 章思路整理；“假设没有它，现在会买吗”据书中禀赋效应思路"
                  "整理的建议。"],
                 tags="#损失厌恶 #决策")
    return b.attach(ep)
