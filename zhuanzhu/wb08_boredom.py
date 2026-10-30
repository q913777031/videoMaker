"""08 受得了无聊（白板手绘版）：排队两分钟，也要掏手机？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 zhuanzhu/build.py 的 SLOW_RULES）。
叙事（形式 B 一个故事贯穿，故事第一幕开局）：小周的一天——早上等电梯掏手机 → 中午排队掏手机 → 下午写方案五分钟
就坐不住 → 小红点一招手，脑袋“嗖”地扭过去，脖子拧成麻花（drop）→ 亮书：脑子被刺激惯坏了（书中观点在这个转折处点出：
一无聊就找刺激，专注的本事会退；习惯多任务的人更难挡开无关信息）→ 晚上回家照书改：上网时间提前写进表、走路时只想一个
问题、给一件事定个很紧的死线 → 第二天排队手插兜发会儿呆 → 昨天 / 今天两条时间线对比 → 评论区互动。
小红点这一讲：一无聊它就招手。
书中观点为转述（卡尔·纽波特《深度工作》准则2“拥抱无聊”：不要不断分心而要不断专注、像罗斯福一样工作、有成果的冥想；
书中引克利福德·纳斯关于多任务者的研究）；电梯、奶茶、45 分钟等为示意，三条办法为据书中思路整理。
"""

import math
import random

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, desk,
                               face, join, partial, rect, spring_path, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out, ease_out_back, lerp

from .common import BOOK, episode

ACC = "#7A4FB5"
SQUARE_SHOT = 3                 # 场景 4：小周脖子拧成麻花 + 招手的小红点

b = Board(size=(3600, 10200))
DARK_RED = "#9E2A20"


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def C(k0, k1, fn, sfx=None):
    b.custom(len(b.shots) - 1, k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """小周：火柴人 + 工牌（挂绳 + 小方牌）。(x, y) 为脚底。"""
    hy = y - 290 * s
    badge = join(P((x - 14 * s, hy + 45 * s), (x + 8 * s, hy + 105 * s), (x + 30 * s, hy + 45 * s)),
                 rect(x + 8 * s, hy + 125 * s, 34 * s, 42 * s, 5 * s))
    return join(stick(x, y, s, arms), badge)


def phone(x, y, w=60, h=100) -> skia.Path:
    return join(rect(x, y, w, h, 10), P((x - w * 0.2, y + h / 2 - 14), (x + w * 0.2, y + h / 2 - 14)))


def elevator(x, y, w=360, h=520) -> skia.Path:
    """电梯：门框 + 两扇门 + 楼层显示 + 呼叫按钮。(x, y) 为门中心。"""
    return join(rect(x, y, w + 40, h + 40, 6), P((x, y - h / 2), (x, y + h / 2)),
                rect(x, y - h / 2 - 70, 140, 60, 8), P((x - 15, y - h / 2 - 60), (x, y - h / 2 - 82), (x + 15, y - h / 2 - 60)),
                circle(x + w / 2 + 70, y, 22), P((x + w / 2 + 62, y + 5), (x + w / 2 + 70, y - 8), (x + w / 2 + 78, y + 5)))


def shop(x, y, w=400) -> skia.Path:
    """奶茶店：条纹遮阳棚 + 柜台 + 一杯奶茶。(x, y) 为遮阳棚下沿中点。"""
    parts = [P((x - w / 2, y), (x - w / 2 + 30, y - 110), (x + w / 2 - 30, y - 110), (x + w / 2, y))]
    n = 5
    for i in range(n):
        x0 = x - w / 2 + w * i / n
        x1 = x0 + w / n
        sc = skia.Path()
        sc.moveTo(x0, y)
        sc.quadTo((x0 + x1) / 2, y + 50, x1, y)
        parts.append(sc)
    parts += [P((x - w / 2 + 20, y + 30), (x - w / 2 + 20, y + 320)), P((x + w / 2 - 20, y + 30), (x + w / 2 - 20, y + 320)),
              P((x - w / 2 - 10, y + 200), (x + w / 2 + 10, y + 200)),
              P((x - 40, y + 200), (x - 30, y + 110), (x + 30, y + 110), (x + 40, y + 200)), P((x + 10, y + 110), (x + 30, y + 60))]
    return join(*parts)


def sitter(x, ys, s=1.0) -> skia.Path:
    """坐着、面朝左敲键盘的小周身子（不含头，头另画）：(x, ys) 为屁股。"""
    ny = ys - 125 * s
    body = P((x, ys), (x, ny))
    arms = P((x - 110 * s, ny + 70 * s), (x - 40 * s, ny + 65 * s), (x, ny + 30 * s))
    legs = P((x, ys), (x - 115 * s, ys), (x - 120 * s, ys + 125 * s), (x - 150 * s, ys + 125 * s))
    badge = join(P((x - 4 * s, ny + 8 * s), (x - 18 * s, ny + 48 * s)), rect(x - 20 * s, ny + 66 * s, 26 * s, 34 * s, 4 * s))
    return join(body, arms, legs, badge)


def brain_face(x, y, r=150) -> skia.Path:
    """圆滚滚的脑袋：起伏轮廓 + 中线 + 两只眯眼 + 张着的嘴 + 两颊的肉。"""
    pts = []
    for i in range(48):
        a = i / 48 * 2 * math.pi
        rr = r * (1 + 0.06 * math.sin(a * 9))
        pts.append((x + rr * math.cos(a) * 1.25, y + rr * math.sin(a) * 0.95))
    mid = skia.Path()
    mid.moveTo(x, y - r * 0.9)
    mid.quadTo(x - 20, y - r * 0.5, x, y - r * 0.25)
    eyes = join(P((x - 70, y - 10), (x - 45, y - 25), (x - 20, y - 10)), P((x + 20, y - 10), (x + 45, y - 25), (x + 70, y - 10)))
    mouth = skia.Path()
    mouth.addOval(skia.Rect.MakeXYWH(x - 30, y + 30, 60, 50))
    cheeks = join(P((x - 150, y + 40), (x - 125, y + 55)), P((x + 150, y + 40), (x + 125, y + 55)))
    return join(P(*pts, close=True), mid, eyes, mouth, cheeks)


def fulcrum(x, y) -> skia.Path:
    return join(P((x, y), (x - 90, y + 150), (x + 90, y + 150), close=True), P((x - 200, y + 150), (x + 200, y + 150)))


def noise(x, y, w, h, n=26, seed=8) -> skia.Path:
    """框里的一团杂乱线条（固定种子，每次一样）。"""
    rnd = random.Random(seed)
    p = skia.Path()
    for _ in range(n):
        x0, y0 = x + rnd.uniform(-w / 2, w / 2), y + rnd.uniform(-h / 2, h / 2)
        x1, y1 = x + rnd.uniform(-w / 2, w / 2), y + rnd.uniform(-h / 2, h / 2)
        p.moveTo(x0, y0)
        p.quadTo(x + rnd.uniform(-w / 2, w / 2), y + rnd.uniform(-h / 2, h / 2), x1, y1)
    return p


def lock(x, y, s=1.0) -> skia.Path:
    shackle = skia.Path()
    shackle.addArc(skia.Rect.MakeXYWH(x - 22 * s, y - 50 * s, 44 * s, 50 * s), 180, 180)
    return join(rect(x, y + 10 * s, 64 * s, 50 * s, 6 * s), shackle, P((x - 22 * s, y - 25 * s), (x - 22 * s, y - 15 * s)),
                P((x + 22 * s, y - 25 * s), (x + 22 * s, y - 15 * s)), circle(x, y + 8 * s, 5 * s))


def fridge(x, y, w=340, h=760) -> skia.Path:
    return join(rect(x, y, w, h, 26), P((x - w / 2, y - h / 2 + 260), (x + w / 2, y - h / 2 + 260)),
                P((x - w / 2 + 40, y - h / 2 + 140), (x - w / 2 + 40, y - h / 2 + 210)),
                P((x - w / 2 + 40, y - h / 2 + 320), (x - w / 2 + 40, y - h / 2 + 420)))


def grid(x, y, cols, rows, cw, ch) -> skia.Path:
    w, h = cols * cw, rows * ch
    parts = [rect(x, y, w, h, 8)]
    for i in range(1, cols):
        parts.append(P((x - w / 2 + i * cw, y - h / 2), (x - w / 2 + i * cw, y + h / 2)))
    for i in range(1, rows):
        parts.append(P((x - w / 2, y - h / 2 + i * ch), (x + w / 2, y - h / 2 + i * ch)))
    return join(*parts)


def cloud(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 120 * s, y + 30 * s)
    p.quadTo(x - 150 * s, y - 30 * s, x - 80 * s, y - 35 * s)
    p.quadTo(x - 60 * s, y - 95 * s, x, y - 70 * s)
    p.quadTo(x + 60 * s, y - 110 * s, x + 90 * s, y - 40 * s)
    p.quadTo(x + 160 * s, y - 30 * s, x + 120 * s, y + 30 * s)
    p.close()
    return p


def speed(x, y, n=3, ln=140, gap=40, dx=-1) -> skia.Path:
    return join(*[P((x, y + i * gap), (x + dx * (ln - i * 25), y + i * gap)) for i in range(n)])


def pops(k, n):
    """把 0–1 进度分成 n 段，返回已落定数量与当前一个的弹出比例。"""
    v = k * n
    return min(n, int(v)), v - int(v)


# ---------------------------------------------------------------- 小红点（系列角色）

def _dot(c, x, y, r, label, wave=0, T=0.0, alpha=1.0):
    """小红点：红色实心圆 + 白色数字 + 两条小短腿；wave=±1 时一只手朝那边招手。"""
    if r <= 1:
        return
    ink = K.paint(BLACK, alpha, max(4, r * 0.09))
    for sx in (-1, 1):
        c.drawPath(P((x + sx * 0.35 * r, y + 0.85 * r), (x + sx * 0.42 * r, y + 1.45 * r),
                     (x + sx * 0.7 * r, y + 1.45 * r)), ink)
    if wave:
        ang = math.radians(-55 + 28 * math.sin(T * 11))
        ax, ay = x + wave * 0.9 * r, y - 0.1 * r
        hx, hy = ax + wave * math.cos(ang) * 0.85 * r, ay + math.sin(ang) * 0.85 * r
        c.drawPath(P((ax, ay), (hx, hy)), ink)
        c.drawCircle(hx, hy, 0.14 * r, K.paint(BLACK, alpha))
    c.drawCircle(x, y, r, K.paint(RED, alpha))
    c.drawCircle(x, y, r, K.paint(DARK_RED, alpha, max(3, r * 0.07)))
    size = r * (1.15 if len(label) == 1 else 0.95 if len(label) == 2 else 0.72)
    K.text(c, label, x, y + r * 0.04, size, "black", "#FFFFFF", alpha)


def reddot(x, y, r=55, label="1", wave=0, grow=None, drift=None):
    """小红点的 custom 动画：k 为弹出进度；grow=(镜头, 拍, 新数字, 新半径) 到点后变大换数字。"""

    def fn(c, k, Tm):
        rr, lab = r, label
        if grow:
            t = b.t_of(grow[0], grow[1])
            if Tm >= t:
                f = ease_out_back(clamp01((Tm - t) / 0.28))
                rr, lab = lerp(r, grow[3], f), grow[2]
        _dot(c, x, y, rr * max(0.0, ease_out_back(k)), lab, wave, Tm)
        return None

    return fn


# ---------------------------------------------------------------- 开局：故事第一幕（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


scene("等电梯也刷", "小周的一天 · 早上", (950, 900, 0.85), bars=2)
L(elevator(650, 930), 0, 0.9, sfx="wood_high")
L(zhou(1150, 1250, 0.85, "hold"), 1, 1.9, BLACK, 10, sfx="wood_high")
L(face(1150, 1250, 0.85, "flat"), 1.9, 2.0)
L(phone(1262, 1065), 2, 2.8, BLUE, 8, sfx="pop")
C(3, 3.4, reddot(1360, 930, 46, "1", wave=1), sfx="ding")
T("8:50 等电梯", 950, 470, 72, k0=4, k1=6, sfx="pop")

QX = (2780, 2990, 3200)
scene("排队也刷", "小周的一天 · 中午", (2650, 900, 0.85))
L(shop(2330, 640), 0, 1.0, sfx="wood_high")
T("奶茶", 2330, 470, 64, k0=1, k1=1.8, sfx="pop")
L(join(*[stick(x, 1250, 0.68, "hold") for x in QX]), 2, 2.9, BLACK, 9, sfx="wood_high")
L(join(*[phone(x + 72, 1100, 40, 66) for x in QX]), 2.9, 3.5, BLUE, 7)
for n, (x, lab) in enumerate(zip(QX, ("1", "3", "9"))):
    C(3 + n, 3.4 + n, reddot(x, 950, 40, lab), sfx="ding" if n == 0 else "pop")
T("12:10 排队", 2600, 1420, 70, k0=6, k1=8, sfx="pop")

J3 = scene("坐不住了", "小周的一天 · 下午三点", (950, 2400, 0.85))
NECK = (1000, 2437)
HEAD_R = 40
L(desk(650, 2560, 400), 0, 0.9, sfx="wood_high")
L(join(rect(620, 2170, 230, 280, 10), P((540, 2225), (700, 2225)), P((540, 2275), (660, 2275))), 1, 1.8, BLACK, 8,
  sfx="pop")
T("方案", 620, 2095, 58, k0=1.8, k1=2.6)
L(sitter(1000, 2550, 0.9), 3, 3.8, BLACK, 10, sfx="wood_high")
J4 = J3 + 1


def head_fn(c, k, Tm):
    """小周的头：场景 3 坐不住时左右晃，场景 4 第 0 拍“嗖”地扭向右边的小红点，脖子拧成麻花。"""
    td = b.t_of(J4, 0)
    f = 0.0 if Tm < td else ease_out_back(clamp01((Tm - td) / 0.3), 2.2)
    jig = 6 * math.sin(Tm * 26) if b.t_of(J3, 6) <= Tm < td else 0.0
    nx, ny = NECK
    hx, hy = lerp(nx - 8 + jig, 1085, f), lerp(ny - HEAD_R, 2235, f)
    ink = K.paint(BLACK, 1, 10)
    top = (hx, hy + HEAD_R)
    if f <= 0:
        c.drawPath(P((nx, ny), (top[0], ny)), ink)
    else:
        w, turns = 16 * min(1.0, f), 3.2 * min(1.0, f)
        for ph in (0, math.pi):
            st = skia.Path()
            for i in range(41):
                u = i / 40
                px, py = lerp(nx, top[0], u), lerp(ny, top[1], u)
                dx, dy = top[0] - nx, top[1] - ny
                ln = math.hypot(dx, dy) or 1
                off = w * math.sin(u * turns * 2 * math.pi + ph)
                qx, qy = px - dy / ln * off, py + dx / ln * off
                st.moveTo(qx, qy) if i == 0 else st.lineTo(qx, qy)
            c.drawPath(st, K.paint(BLACK if ph == 0 else BLUE, 1, 8))
    part, tip = partial(circle(hx, hy, HEAD_R), k)
    c.drawPath(part, ink)
    if k >= 1:
        d = -1 if f < 0.5 else 1
        if f < 0.5:
            c.drawCircle(hx + d * 18, hy - 6, 4, K.paint(BLACK))
            c.drawPath(P((hx + d * 28, hy + 18), (hx + d * 12, hy + 18)), K.paint(BLACK, 1, 5))
        else:
            for ex in (6, 26):
                c.drawCircle(hx + ex, hy - 8, 9, K.paint(BLACK, 1, 4))
                c.drawCircle(hx + ex + 2, hy - 8, 3, K.paint(BLACK))
            c.drawCircle(hx + 20, hy + 20, 8, K.paint(BLACK, 1, 4))
    return tip if k < 1 else None


C(3.8, 4.2, head_fn)
L(spring_path(1000, 2575, 145, 110, 6), 4, 4.8, BLACK, 8, sfx="wood_low")
L(join(P((935, 2550), (1065, 2550)), P((930, 2720), (1070, 2720))), 4.8, 5.1, BLACK, 9)
T("才 5 分钟", 680, 2385, 58, RED, k0=5, k1=6.25, sfx="rim")
L(join(P((1110, 2600), (1135, 2625), (1110, 2650)), P((1135, 2590), (1160, 2625), (1135, 2660))), 6.25, 6.9, RED, 7)
H(6, "shaker", 0.7)
C(7, 7.4, reddot(1420, 2330, 58, "9", wave=-1, grow=(J4, 3, "99+", 82)), sfx="ding")

# ---------------------------------------------------------------- drop：一叫就扭头（场景 4）

scene("一叫就扭头", "小周的一天 · 一叫就扭头", (1090, 2370, 1.0), shake=[0], flashes=[0])
H(0, "kick", 0.9)
T("嗖！", 1240, 2120, 110, RED, k0=1, k1=1.8, sfx="pop")
L(join(arrow((930, 2330), (1010, 2190), -0.35, 0), arrow((900, 2280), (960, 2170), -0.35, 0)), 2, 2.6, BLACK, 7,
  sfx="wood_high")
H(3, "ding")
T("脖子拧成麻花", 1110, 1990, 76, RED, k0=5, k1=6.5, sfx="pop")
L(underline(870, 1350, 2050, 12, 40), 7, 7.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 5–7）

BRAIN = (2980, 2330)
scene("脑子被惯坏了", "《深度工作》 · 书中观点", (2650, 2400, 0.85))
L(book(2330, 2380, 400, 270), 0, 0.9, sfx="wood_low")
T("《深度工作》", 2330, 2130, 66, GREEN, k0=1, k1=2.5, sfx="pop")
T("卡尔 · 纽波特", 2330, 2620, 52, k0=2.6, k1=3.8)
L(brain_face(*BRAIN, 150), 4, 4.9, BLACK, 9, sfx="wood_high")
for n, (dx, dy) in enumerate(((-150, -260), (20, -300))):
    C(5 + n, 5.4 + n, reddot(BRAIN[0] + dx, BRAIN[1] + dy, 34, "1"), sfx="ding" if n == 0 else "pop")
L(arrow((BRAIN[0] + 60, BRAIN[1] - 240), (BRAIN[0] + 8, BRAIN[1] + 20), 0.25, 30), 6.4, 6.9, RED, 7)
T("被惯坏了", 2980, 2620, 64, RED, k0=7, k1=8, sfx="rim")

PIV = (950, 4100)
TILT = math.radians(15)
LANDS = (2, 3, 4)               # 刺激一个个落到左端的拍


def seesaw_fn(c, k, Tm):
    """跷跷板：红点（刺激）一个个落在左端，板子越压越斜，右端的“专注”盒子越翘越高。"""
    j = J6
    landed = sum(1 for kk in LANDS if Tm >= b.t_of(j, kk))
    ang = 0.0
    for i, kk in enumerate(LANDS):
        t = b.t_of(j, kk)
        if Tm >= t:
            ang += TILT / len(LANDS) * ease_out_back(clamp01((Tm - t) / 0.35))
    ca, sa = math.cos(ang), math.sin(ang)

    def at(u, h=0.0):
        """板上距支点 u（左负右正）、离板面 h 处的点。"""
        return PIV[0] + u * ca - h * sa, PIV[1] - u * sa - h * ca

    plank = P(at(-520), at(520))
    part, tip = partial(plank, k)
    c.drawPath(part, K.paint(BLACK, 1, 14))
    for i in range(landed):
        t = b.t_of(j, LANDS[i])
        fall = ease_out(clamp01((Tm - t + 0.15) / 0.3))
        x, y = at(-440 + i * 95, 45)
        _dot(c, x, y - 120 * (1 - fall), 40, "9" if i < 2 else "99+")
    tb = b.t_of(j, 6)
    if Tm >= tb:
        g = clamp01((Tm - tb) / 0.5)
        corners = [at(330, 0), at(330, 150), at(500, 150), at(500, 0)]
        box = P(*corners, close=True)
        bp, _ = partial(box, g)
        c.drawPath(bp, K.paint(BLUE, 1, 10))
    return tip if k < 1 else None


J6 = scene("越刷越坐不住", "书中观点 · 一无聊就找刺激", (950, 3900, 0.85))
L(fulcrum(*PIV), 0, 0.9, BLACK, 10, sfx="wood_high")
C(1, 1.8, seesaw_fn, sfx="wood_low")
H(2, "ding")
H(3, "pop")
H(4, "pop")
T("刺激", 520, 4340, 66, RED, k0=5, k1=5.8, sfx="pop")
H(6, "wood_high")
T("专注", 1300, 3700, 66, BLUE, k0=7, k1=7.8, sfx="pop")
L(arrow((1480, 3900), (1480, 3680), 0.0, 34), 7.8, 8.0, BLUE, 8)

FR = (2380, 3970)
scene("杂讯挡不住", "书中观点 · 纳斯的研究", (2650, 3900, 0.85))
L(rect(*FR, 600, 600, 12), 0, 0.9, BLACK, 9, sfx="wood_high")
L(circle(FR[0] + 90, FR[1] + 70, 46), 1, 1.6, BLUE, 9, sfx="pop")
L(noise(*FR, 540, 540), 2, 3.0, "#6B6B75", 5, sfx="shaker")
T("纳斯的研究", 2650, 3500, 64, k0=3, k1=4.25, sfx="pop")
MT = (3010, 4250)
L(stick(*MT, 0.7, "shrug"), 4, 4.8, BLACK, 9, sfx="wood_high")
T("爱切换的人", MT[0], MT[1] + 75, 54, k0=5, k1=6, sfx="pop")
L(join(phone(MT[0] - 110, MT[1] - 330, 54, 80), phone(MT[0] + 110, MT[1] - 330, 54, 80),
       rect(MT[0], MT[1] - 400, 90, 60, 8)), 6, 6.8, BLUE, 7, sfx="pop")
T("？", MT[0] + 160, MT[1] - 480, 96, RED, k0=7, k1=7.8, sfx="rim")

# ---------------------------------------------------------------- 晚上照书改（场景 8–11）

GX, GY, CW, CH = 950, 5360, 240, 130
NET = [(0, 0), (2, 1), (1, 3)]        # 提前写进表的三格上网时间（列, 行）


def cell(cx, rw):
    return GX - 1.5 * CW + (cx + 0.5) * CW, GY - 2 * CH + (rw + 0.5) * CH


scene("上网排进表", "书中办法 · 先排上网时间", (950, 5300, 0.85))
L(grid(GX, GY, 3, 4, CW, CH), 0, 0.9, BLACK, 8, sfx="wood_high")
T("上网时间，先写进表", 950, 4900, 66, k0=1, k1=3, sfx="pop")
for n, (cx, rw) in enumerate(NET):
    L(phone(*cell(cx, rw), 44, 80), 3 + n, 3.7 + n, BLUE, 8, sfx="pop")
LOCKS = [cell(cx, rw) for rw in range(4) for cx in range(3) if (cx, rw) not in NET]
L(join(*[lock(x, y, 0.85) for x, y in LOCKS]), 6, 7.6, "#6B6B75", 6, sfx="wood_low")

FG = (2960, 5380)
scene("晚上开始试", "小周的一天 · 晚上到家", (2650, 5300, 0.85))
L(fridge(*FG), 0, 1.0, BLACK, 9, sfx="wood_high")
T("19:30 到家", 2440, 4880, 66, k0=1, k1=3, sfx="pop")
L(grid(FG[0] + 10, FG[1] + 60, 3, 4, 60, 48), 3, 3.8, BLUE, 5, sfx="pop")
C(4, 4.4, lambda c, k, Tm: (K.dot(c, FG[0] + 10, FG[1] - 60, 16 * ease_out_back(k), RED), None)[1], sfx="ding")
L(zhou(2450, 5700, 0.8, "point"), 5, 5.8, BLACK, 10, sfx="wood_high")
L(face(2450, 5700, 0.8, "smile"), 5.8, 6.0)
L(bubble(2400, 5180, 320, 120, -1), 6, 6.6, BLACK, 8, sfx="pop")
T("先试一周", 2400, 5180, 56, k0=6.6, k1=7.6)

WK = (800, 7040)
QM = (900, 6430)
DOT10 = (1320, 6420)
J10 = None


def thought_fn(c, k, Tm):
    """头顶拴着的问号：第 5 拍被小红点勾走（走神），第 6 拍被一把拉回。"""
    j = J10
    t5, t6 = b.t_of(j, 5), b.t_of(j, 6)
    if Tm < t6:
        f = ease_out(clamp01((Tm - t5) / 0.5)) * 0.55
    else:
        f = 0.55 * (1 - ease_out_back(clamp01((Tm - t6) / 0.45)))
    s = ease_out_back(k)
    x, y = lerp(QM[0], DOT10[0] - 90, f), lerp(QM[1], DOT10[1] + 10, f)
    head = (WK[0], WK[1] - 290 * 0.85 - 40)
    st = skia.Path()
    st.moveTo(*head)
    st.quadTo((head[0] + x) / 2 + 40, (head[1] + y) / 2 + 30, x - 10, y + 55)
    c.drawPath(st, K.paint(BLACK, 1, 5))
    K.text(c, "？", x, y, 120 * s, "hand", BLUE)
    return None


J10 = scene("走路想一件事", "第二天 · 上班路上", (950, 6700, 0.85))
T("只想一个问题", 950, 6230, 70, k0=0, k1=1.5, sfx="pop")
L(P((420, 7050), (1480, 7050)), 1.5, 2.0, BLACK, 8)
L(zhou(*WK, 0.85), 2, 2.9, BLACK, 10, sfx="wood_high")
L(face(*WK, 0.85, "smile"), 2.9, 3.0)
C(3, 3.4, thought_fn, sfx="pop")
C(4, 4.4, reddot(*DOT10, 50, "9", wave=-1), sfx="ding")
H(5, "shaker", 0.7)
H(6, "tom")
L(arrow((1180, 6620), (980, 6560), -0.2, 34), 6, 6.8, GREEN, 8)
T("拉回来", 1160, 6720, 58, GREEN, k0=7, k1=7.8, sfx="pop")

CK = (2330, 6600)


def wedge_fn(c, k, Tm):
    """钟面上的 45 分钟：红色扇形从 12 点扫到 9 点。"""
    p = skia.Path()
    p.moveTo(*CK)
    p.arcTo(skia.Rect.MakeXYWH(CK[0] - 170, CK[1] - 170, 340, 340), -90, 270 * ease_out(k), False)
    p.close()
    c.drawPath(p, K.paint(RED, 0.35))
    return None


scene("定个死线冲", "书中办法 · 给一件事定死线", (2650, 6700, 0.85))
L(clock(*CK, 200), 0, 0.9, BLACK, 9, sfx="wood_high")
T("只给 45 分钟", 2330, 6260, 64, RED, k0=1, k1=2.5, sfx="pop")
C(2, 3.4, wedge_fn, sfx="rim")
L(zhou(2960, 6960, 0.75, "up"), 3, 3.8, BLACK, 10, sfx="wood_high")
L(face(2960, 6960, 0.75, "smile"), 3.8, 4.0)
L(speed(2800, 6720, 3, 160, 50), 4, 4.6, BLACK, 7, sfx="shaker")
L(rect(3170, 6540, 150, 190, 10), 5, 5.6, BLACK, 8, sfx="pop")
L(check(3170, 6540, 45), 5.6, 6.0, GREEN, 10)
T("像罗斯福一样工作", 2650, 7140, 62, k0=6, k1=8, sfx="ding")

# ---------------------------------------------------------------- 第二天排队 + 一天下来（场景 12–13）

scene("发会儿呆", "第二天 · 中午排队", (950, 8100, 0.85))
L(shop(620, 7750, 380), 0, 1.0, BLACK, 9, sfx="wood_high")
L(join(stick(880, 8400, 0.68, "hold"), phone(952, 8250, 40, 66)), 1, 1.9, BLACK, 9, sfx="pop")
C(2, 2.4, reddot(880, 8100, 40, "3"), sfx="ding")
ZQ = (1200, 8420)
L(join(zhou(*ZQ, 0.8), P((ZQ[0] - 56, ZQ[1] - 128), (ZQ[0] - 30, ZQ[1] - 110)),
       P((ZQ[0] + 56, ZQ[1] - 128), (ZQ[0] + 30, ZQ[1] - 110))), 3, 3.9, BLACK, 10, sfx="wood_high")
L(face(*ZQ, 0.8, "smile"), 3.9, 4.0)
L(cloud(1330, 7690, 0.9), 4, 4.8, BLUE, 8, sfx="pop")
C(5, 5.4, reddot(1440, 8250, 40, "1", wave=-1), sfx="ding")
T("手插兜，看看天", 900, 8600, 62, k0=6, k1=7.75, sfx="pop")

LX0, LX1 = 2330, 3230
Y1, Y2 = 7820, 8270
DOTS1 = (2400, 2560, 2720, 2900, 3080)


def day_fn(row):
    """时间线上的小红点：昨天一路叮了五回；今天只剩两格上网时间，中间一块蓝色专注块。"""

    def fn(c, k, Tm):
        if row == 1:
            n, f = pops(k, len(DOTS1))
            for i, x in enumerate(DOTS1[:n + 1]):
                s = 1.0 if i < n else ease_out_back(f)
                _dot(c, x, Y1 - 60, 34 * s, "9")
        else:
            n, f = pops(k, 3)
            for i, x in enumerate((2400, 3150)):
                if i < n or (i == n and n < 2):
                    s = 1.0 if i < n else ease_out_back(f)
                    _dot(c, x, Y2 - 60, 34 * s, "1")
            if n >= 2:
                g = 1.0 if n >= 3 else ease_out(f)
                K.rr(c, 2775, Y2 - 55, 420 * g, 80, 10, BLUE, 0.9)
                if g >= 1:
                    K.text(c, "专注", 2775, Y2 - 55, 50, "hand", "#FFFFFF")
        return None

    return fn


scene("一天下来", "小周的一天 · 昨天和今天", (2650, 8100, 0.85))
T("昨天", 2170, Y1, 64, k0=0, k1=0.8, sfx="pop")
L(P((LX0, Y1), (LX1, Y1)), 0.8, 1.6, BLACK, 8)
C(2, 3.4, day_fn(1), sfx="ding")
H(3, "shaker", 0.6)
T("今天", 2170, Y2, 64, k0=4, k1=4.8, sfx="pop")
L(P((LX0, Y2), (LX1, Y2)), 4.8, 5.6, BLACK, 8)
C(6, 7.4, day_fn(2), sfx="wood_high")
T("坐得住了", 2780, 8560, 70, BLUE, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：第 0 拍拉远看全板，第 4 拍推到评论区

FULL = (1800, 5100, 0.18)
END = (1800, 9500, 0.8)
J_END = scene("评论区聊聊", "评论区见", FULL, bars=4)
b.move(J_END, 4, END)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你今天第一次掏手机是几点？", 1800, 9400, 70, RED, k0=6, k1=8.5, sfx="pop")
T("下一讲：社交软件停三十天，会怎样？", 1800, 9580, 50, k0=9, k1=13, sfx="wood_high")
C(11, 11.4, reddot(2380, 9250, 44, "?", wave=-1), sfx="ding")
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "boredom", "受得了无聊", "排队两分钟，也要掏手机？", ACC, b.shots,
                 [f"{BOOK}第二部分 准则2“拥抱无聊”（含“不要不断分心，而要不断专注”“像罗斯福一样工作”"
                  "“有成果的冥想”三小节，转述）",
                  "中译本：《深度工作：如何有效使用每一点脑力》，宋伟译，江西人民出版社 · 后浪 2017；民主与建设出版社 · 后浪 2023",
                  "书中引用：克利福德·纳斯（斯坦福大学）关于习惯多任务者的研究（转述，不引数字）"],
                 "排队两分钟|也要【掏手机】", SQUARE_SHOT,
                 ["书中观点均为转述：准则2“拥抱无聊”——专注是要练的本事，一有空档就找刺激，大脑会习惯这种刺激，"
                  "真要沉下心时就坐不住；书中建议别在专注中间穿插分心，而是反过来，在分心的时间里安排专注："
                  "提前把上网时间写进时间表，其余时间不碰（“不要不断分心，而要不断专注”）；书中引克利福德·纳斯的研究："
                  "习惯多任务的人更难把无关信息挡在外面（只画方向，不写数字）。上屏避免“不要……而要……”写法，改说“上网排进表”。",
                  "“像罗斯福一样工作”（给一件事定个很紧的截止时间，集中冲刺）与“有成果的冥想”（走路、通勤时只想一个问题，"
                  "走神就拉回来）为书中办法，上屏只写名字与通俗化画面。",
                  "小周的一天（8:50 等电梯、12:10 排队买奶茶、下午三点写方案、19:30 到家、“才 5 分钟”“只给 45 分钟”）"
                  "均为示意，不是数据，不指向任何具体公司或个人；跷跷板、杂乱线条里找圆、脖子拧成麻花、昨天 / 今天两条时间线"
                  "为对书中观点的通俗化示意；小红点、小周为本系列虚构角色。",
                  "三条做法（上网时间先写进表、走路时只想一个问题、给一件事定个死线）及“先试一周”为据书中思路整理的建议。"],
                 tags="#手机")
    return b.attach(ep)
