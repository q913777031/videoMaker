"""05 致富与守富（白板手绘版）：赚到了大钱，为什么又亏光了？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（G 倒叙）：先给结局（一个曾经很有钱的人站在空房间，口袋翻出来）→ 时钟倒转回到 1929 年 →
那年大家都在亏，他逆势大赚（drop）→ 亮书 → 赚到以后越押越大，脚边的台子越垒越高越细 → 台子塌了，全输了 →
书中观点（赚钱和守住钱是两门本事；守住钱要节俭，也要一点“怕”；对未来乐观，对路上的坑小心）→
身边的例子（年终奖全押进一个筐，筐底有洞）→ 两条做法（进门前问一句“输了还能回来吗”；先保住，再去赚）→ 评论区互动。
书中观点为转述（摩根·豪泽尔《金钱心理学》第 5 章“致富 vs. 守富”，李青宗译，民主与建设出版社 / 后浪 2023）；
利弗莫尔只讲“大赚—越押越大—全输了”，不讲做空等手法，不提结局；年终奖、门上那句问话为示意 / 据书中思路整理，不说买什么。
"""

import math

import skia

from adler import kit as K
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, check, circle, clock, cross,
                               face, join, rect, stick, underline)
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#B7791F"
SQUARE_SHOT = 3                 # 场景 4：一排红色向下箭头里，一根绿箭头冲上去，利弗莫尔举手

b = Board(size=(3600, 9500))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = J() if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def ink(c, path, color=BLACK, width=10, alpha=1.0):
    """动态项里按马克笔样式画一条路径（与引擎描线同样的笔触）。"""
    c.drawPath(path, wb.marker(color, width, alpha))
    c.drawPath(path, K.paint(color, 0.22 * alpha, width * 0.45, blur=1.2))


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def pig(x, y, s=1.0) -> skia.Path:
    """小猪罐（正面）：(x, y) 为身子中心；圆身子、背上投币口、两只耳朵、猪鼻子、点点眼睛、两条腿、卷尾巴。"""
    tail = skia.Path()
    tail.moveTo(x + 148 * s, y + 10 * s)
    tail.quadTo(x + 190 * s, y - 10 * s, x + 178 * s, y - 35 * s)
    tail.quadTo(x + 160 * s, y - 50 * s, x + 168 * s, y - 20 * s)
    return join(oval(x, y, 300 * s, 240 * s),
                P((x - 118 * s, y - 70 * s), (x - 105 * s, y - 150 * s), (x - 55 * s, y - 108 * s)),
                P((x + 118 * s, y - 70 * s), (x + 105 * s, y - 150 * s), (x + 55 * s, y - 108 * s)),
                P((x - 32 * s, y - 100 * s), (x + 32 * s, y - 100 * s)),
                circle(x - 45 * s, y - 40 * s, 6 * s), circle(x + 45 * s, y - 40 * s, 6 * s),
                oval(x, y + 12 * s, 92 * s, 58 * s), circle(x - 16 * s, y + 12 * s, 6 * s), circle(x + 16 * s, y + 12 * s, 6 * s),
                P((x - 70 * s, y + 110 * s), (x - 70 * s, y + 142 * s)), P((x + 70 * s, y + 110 * s), (x + 70 * s, y + 142 * s)),
                tail)


def pig_mouth(x, y, s=1.0, mood="smile") -> skia.Path:
    p = skia.Path()
    if mood == "smile":
        p.addArc(skia.Rect.MakeXYWH(x - 28 * s, y + 38 * s, 56 * s, 34 * s), 20, 140)
    elif mood == "flat":
        p.moveTo(x - 22 * s, y + 62 * s)
        p.lineTo(x + 22 * s, y + 62 * s)
    else:
        p.addArc(skia.Rect.MakeXYWH(x - 24 * s, y + 58 * s, 48 * s, 28 * s), 200, 140)
    return p


def pig_hug(x, y, s=1.0) -> skia.Path:
    """两只前蹄抱住自己的肚子。"""
    parts = []
    for d in (-1, 1):
        a = skia.Path()
        a.moveTo(x + d * 150 * s, y + 5 * s)
        a.quadTo(x + d * 110 * s, y + 118 * s, x + d * 22 * s, y + 96 * s)
        parts += [a, circle(x + d * 16 * s, y + 96 * s, 10 * s)]
    return join(*parts)


def sweat(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y - 34 * s)
    p.quadTo(x + 22 * s, y, x, y + 14 * s)
    p.quadTo(x - 22 * s, y, x, y - 34 * s)
    return p


def coin(x, y, r=30) -> skia.Path:
    return join(circle(x, y, r), P((x, y - r * 0.55), (x, y + r * 0.55)))


def plate(x, y, w, h=96) -> skia.Path:
    """名字牌：圆角框 + 两根挂绳。"""
    return join(rect(x, y, w, h, 14), P((x - w * 0.3, y - h / 2), (x, y - h / 2 - 50), (x + w * 0.3, y - h / 2)))


def room(x, y, w=560, h=420, d=170) -> skia.Path:
    """空房间（一点透视）：(x, y) 为后墙中心；后墙 + 四条墙角线。"""
    l, r, t, bt = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    return join(rect(x, y, w, h, 4), P((l, t), (l - d, t - d)), P((r, t), (r + d, t - d)),
                P((l, bt), (l - d, bt + d)), P((r, bt), (r + d, bt + d)))


def pockets(x, y, s=1.0) -> skia.Path:
    """翻出来的两只裤兜：(x, y) 为小人脚底。"""
    hy = y - 120 * s
    parts = []
    for d in (-1, 1):
        parts.append(P((x + d * 18 * s, hy - 10 * s), (x + d * 70 * s, hy - 4 * s), (x + d * 78 * s, hy + 42 * s),
                       (x + d * 30 * s, hy + 36 * s), close=True))
    return join(*parts)


def head_hold(x, y, s=1.0) -> skia.Path:
    """抱头的小人：(x, y) 为脚底。"""
    hy = y - 290 * s
    sh = hy + 80 * s
    arms = join(P((x - 40 * s, hy - 30 * s), (x - 85 * s, hy + 5 * s), (x, sh)),
                P((x + 40 * s, hy - 30 * s), (x + 85 * s, hy + 5 * s), (x, sh)))
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)), arms,
                P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)))


def rewind(x, y, s=1.0) -> skia.Path:
    """倒带键：两个朝左的三角。"""
    return join(P((x, y - 40 * s), (x - 60 * s, y), (x, y + 40 * s), close=True),
                P((x + 60 * s, y - 40 * s), (x, y), (x + 60 * s, y + 40 * s), close=True))


def ccw_arrow(x, y, r) -> skia.Path:
    """绕钟面上方逆时针走的弧形箭头。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -25, -130)
    a = math.radians(-155)
    ex, ey = x + r * math.cos(a), y + r * math.sin(a)
    tx, ty = math.sin(a), -math.cos(a)          # 逆时针方向的切线
    for d in (0.5, -0.5):
        ang = math.atan2(ty, tx) + math.pi + d
        p.moveTo(ex, ey)
        p.lineTo(ex + 50 * math.cos(ang), ey + 50 * math.sin(ang))
    return p


def key(x, y, s=1.0) -> skia.Path:
    """钥匙（竖放）：(x, y) 为钥匙中心。"""
    return join(circle(x, y - 110 * s, 62 * s), circle(x, y - 110 * s, 20 * s), P((x, y - 48 * s), (x, y + 150 * s)),
                P((x, y + 100 * s), (x + 45 * s, y + 100 * s)), P((x, y + 140 * s), (x + 55 * s, y + 140 * s)))


def rays(x, y, r0=60, r1=110, angs=(200, 160, 20, 340)) -> skia.Path:
    parts = []
    for a in angs:
        t = math.radians(a)
        parts.append(P((x + r0 * math.cos(t), y + r0 * math.sin(t)), (x + r1 * math.cos(t), y + r1 * math.sin(t))))
    return join(*parts)


def basket(x, y, w=340, h=270) -> skia.Path:
    """筐：(x, y) 为筐口中点；倒梯形 + 编织纹。"""
    bw = w * 0.7
    parts = [P((x - w / 2, y), (x - bw / 2, y + h), (x + bw / 2, y + h), (x + w / 2, y), close=True),
             P((x - w / 2 - 15, y), (x + w / 2 + 15, y))]
    for i in (1, 2):
        f = i / 3
        ww = lerp(w, bw, f)
        parts.append(P((x - ww / 2, y + h * f), (x + ww / 2, y + h * f)))
    for dx in (-0.25, 0.0, 0.25):
        parts.append(P((x + dx * w, y), (x + dx * bw, y + h)))
    return join(*parts)


def hole(x, y, w=130, h=46) -> skia.Path:
    pts = []
    for i in range(12):
        a = i / 12 * 2 * math.pi
        rr = 1.0 if i % 2 == 0 else 0.62
        pts.append((x + w / 2 * rr * math.cos(a), y + h / 2 * rr * math.sin(a)))
    return P(*pts, close=True)


def envelope(x, y, w=220, h=150) -> skia.Path:
    return join(rect(x, y, w, h, 10), P((x - w / 2, y - h / 2 + 10), (x, y - h / 2 + 55), (x + w / 2, y - h / 2 + 10)))


def door(x, y, w=460, h=720) -> skia.Path:
    return join(rect(x, y, w, h, 6), P((x - w / 2 - 40, y + h / 2), (x + w / 2 + 40, y + h / 2)),
                circle(x + w / 2 - 50, y + 40, 16))


def bubble(x, y, w, h, tail=1) -> skia.Path:
    p = rect(x, y, w, h, 40)
    p.moveTo(x + tail * w * 0.1, y + h / 2)
    p.lineTo(x + tail * w * 0.05, y + h / 2 + 60)
    p.lineTo(x + tail * w * 0.3, y + h / 2)
    return p


def base(x, y, top=500, bottom=720, h=170) -> skia.Path:
    """稳稳的底座：(x, y) 为底边中点。"""
    return P((x - bottom / 2, y), (x - top / 2, y - h), (x + top / 2, y - h), (x + bottom / 2, y), close=True)


def flag(x, y) -> skia.Path:
    """(x, y) 为旗杆底。"""
    return join(P((x, y), (x, y - 170)), P((x, y - 170), (x + 100, y - 140), (x, y - 110)))


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 开局：先给结局，再倒带（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("他曾经很有钱", "先看结局", (950, 850, 0.85), bars=2)
L(room(950, 780), 0, 0.9, BLACK, 9, sfx="wood_high")
MAN1 = (950, 1120, 0.85)
L(stick(*MAN1, "shrug"), 1, 1.8, sfx="pop")
L(face(*MAN1, "sad"), 1.8, 2.0)
L(pockets(*MAN1), 2, 2.7, RED, 8, sfx="rim")
L(plate(950, 660, 330), 3, 3.6, BLUE, 8, sfx="pop")
T("利弗莫尔", 950, 660, 64, BLUE, k0=3.6, k1=4.6)
T("一无所有", 950, 1265, 76, RED, k0=5, k1=6.0, sfx="ding")

CK = (2650, 830, 250)
scene("倒回去看看", "倒带", (2650, 850, 0.85))
L(clock(*CK), 0, 0.9, BLACK, 9, sfx="wood_high")
L(ccw_arrow(CK[0], CK[1], 310), 1, 1.9, RED, 10, sfx="pop")


def spin_fn(c, k, t):
    """时钟指针倒着转四圈，越转越慢，停在一点钟附近。"""
    x, y, r = CK
    e = ease_out(k)
    m = -math.pi / 2 - e * 4 * 2 * math.pi
    h = -math.pi / 2 + math.radians(30) - e * 4 / 12 * 2 * math.pi
    ink(c, join(P((x, y), (x + math.cos(m) * r * 0.75, y + math.sin(m) * r * 0.75)),
                P((x, y), (x + math.cos(h) * r * 0.5, y + math.sin(h) * r * 0.5))), BLACK, 11)
    K.dot(c, x, y, 12, BLACK)
    return None


b.custom(J(), 2, 8, spin_fn, sfx="shaker")
T("倒带", 2560, 430, 84, RED, k0=3, k1=3.8, sfx="pop")
L(rewind(2740, 430, 0.8), 4, 4.7, RED, 9, sfx="pop")
H(6, "wood_low")
T("回到 1929 年", 2650, 1195, 72, BLUE, k0=5, k1=7, sfx="pop")

# ---------------------------------------------------------------- 1929：大家都在亏，他大赚（场景 3–4）

scene("那年，大家都在亏", "书中故事 · 1929", (2650, 2200, 0.85))
T("1929", 2650, 1820, 150, RED, k0=0, k1=1, sfx="tom")
for n, x in enumerate((2260, 2650, 3040)):
    L(head_hold(x, 2500, 0.7), 2 + n, 2.8 + n, sfx="wood_high" if n % 2 == 0 else "pop")
    L(face(x, 2500, 0.7, "sad"), 2.8 + n, 3.0 + n)
FALL = P((2150, 1980), (2300, 2040), (2420, 2010), (2600, 2100), (2720, 2070), (2900, 2160), (3120, 2190))
L(join(FALL, P((3070, 2150), (3120, 2190), (3060, 2215))), 5, 5.9, RED, 10, sfx="rim")
T("大崩盘", 2650, 2620, 64, k0=6, k1=6.8, sfx="pop")

VD = (950, 2200, 0.85)
scene("他反而大赚一笔", "书中故事 · 逆势", VD, shake=[0], flashes=[0])
L(join(*[arrow((x, 1820), (x, 2120), 0.0, 40) for x in (470, 680, 1220, 1430)]), 0, 0.9, RED, 10, sfx="kick")


def glow_fn(c, k, t):
    K.dot(c, 950, 2080, 260 * ease_out(k), GREEN, 0.10)
    K.dot(c, 950, 1760, 110 * ease_out(k), GREEN, 0.12)
    return None


b.custom(J(), 1, 1.6, glow_fn)
L(arrow((950, 2420), (950, 1740), 0.0, 75), 1, 1.8, GREEN, 22, sfx="ding")
L(rays(950, 1760), 2, 2.6, GREEN, 9, sfx="pop")
T("大赚一笔", 1260, 2510, 92, GREEN, k0=3, k1=4.2, sfx="pop")
MAN4 = (620, 2610, 0.6)
L(stick(*MAN4, "up"), 5, 5.8, sfx="wood_high")
L(face(*MAN4, "smile"), 5.8, 6.0)
T("利弗莫尔", 620, 2672, 48, BLUE, k0=6, k1=7, sfx="pop")

# ---------------------------------------------------------------- 亮书 + 越押越大 + 全输了（场景 5–7）

scene("书里讲了他的故事", "金钱心理学 · 第五章", (950, 3550, 0.85))
L(book(950, 3520, 460, 300), 0, 0.9, BLACK, 10, sfx="wood_low")
T("金钱心理学", 950, 3260, 84, GREEN, k0=1, k1=2.25, sfx="pop")
T("摩根·豪泽尔", 950, 3790, 54, k0=3, k1=4.5, sfx="pop")
T("第5章 致富 vs. 守富", 950, 3895, 52, BLUE, k0=5, k1=7, sfx="pop")
PIG5 = (1385, 3600, 0.55)
L(join(pig(*PIG5), pig_mouth(*PIG5, "smile")), 7, 7.9, ORANGE, 8, sfx="wood_high")

G = 3980                        # 地面
TX = 2830                       # 台子中心
BLOCKS = [(380, 70), (310, 80), (250, 90), (190, 100), (140, 110), (100, 120)]
# 塌了以后每块落地的位置：(中心 x, 中心离地高度, 转角)
RUBBLE = [(2840, 35, 4), (2560, 40, -7), (3200, 125, 91), (2930, 118, -12), (2700, 125, 16), (3060, 62, 28)]
MAN6 = (2300, G, 0.7)

scene("赚到以后，胆子更大", "书中故事 · 越押越大", (2650, 3550, 0.85))
J6 = J()
L(join(P((2120, G), (3200, G)), stick(*MAN6, "point")), 0, 0.9, sfx="wood_high")


def man_face_fn(c, k, t):
    """台子塌之前笑，塌了以后嘴角往下。"""
    mood = "smile" if t < b.t_of(J6 + 1, 1) + 0.15 else "sad"
    ink(c, face(*MAN6, mood), BLACK, 10)
    return None


b.custom(J6, 0.9, 1.0, man_face_fn)


def _block_rest(i):
    """第 i 块在台子上的中心高度（离地）。"""
    return sum(h for _, h in BLOCKS[:i]) + BLOCKS[i][1] / 2


def _block(c, i, x, y, rot, alpha=1.0):
    w, h = BLOCKS[i]
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    ink(c, join(rect(0, 0, w, h, 6), coin(0, 0, min(w, h) * 0.3)), BLACK if i < 3 else RED, 9, alpha)
    c.restore()


def tower_fn(c, k, t):
    """场景 6：每拍落下一块，越往上越窄越高；场景 6 末尾开始晃；场景 7 第 1 拍塌掉，散在地上。"""
    tc = b.t_of(J6 + 1, 1)
    w0 = b.t_of(J6, 7)
    sway = 0.0
    if t >= w0:
        amp = min(1.0, (t - w0) / max(1e-3, tc - w0)) ** 2
        sway = amp * 5.0 * math.sin((t - w0) * 2 * math.pi * 1.6)
    for i, (w, h) in enumerate(BLOCKS):
        tl = b.t_of(J6, 1 + i)
        if t < tl - 0.22:
            break
        ry = G - _block_rest(i)
        if t < tl:                                   # 落下来
            f = (t - (tl - 0.22)) / 0.22
            ry -= 160 * (1 - f) ** 2
        lean = sway * (i + 1) / len(BLOCKS)
        x0, y0, r0 = TX + 9 * lean * (i + 1) / 2, ry, lean
        if t < tc:
            _block(c, i, x0, y0, r0)
            continue
        d = (len(BLOCKS) - 1 - i) * 0.05
        f = ease_in_out(clamp01((t - tc - d) / 0.75))
        ex, eh, er = RUBBLE[i]
        x = lerp(x0, ex, f)
        y = lerp(y0, G - eh, f) - 140 * 4 * f * (1 - f) * (i / len(BLOCKS))
        _block(c, i, x, y, lerp(r0, er, f))
    return None


b.custom(J6, 1, 1.2, tower_fn)
for n in range(6):
    H(1 + n, "wood_low" if n % 2 == 0 else "pop", 0.7 + 0.03 * n)
T("越押越大", 2330, 3400, 66, RED, k0=7, k1=8, sfx="pop")
L(arrow((2470, 3460), (2650, 3330), 0.15, 34), 7, 7.8, RED, 8)

COINS = [(2430, 0.30), (2620, 0.42), (2990, 0.36), (3130, 0.50), (3270, 0.44), (2760, 0.58)]
scene("后来全输了", "书中故事 · 输光", (2650, 3600, 0.8), shake=[(1, 22.0)])
H(0, "shaker")
H(1, "rim", 0.9)


def coins_fn(c, k, t):
    """台子塌的时候，硬币从顶上四散落地。"""
    tc = b.t_of(J6 + 1, 1)
    sx, sy = TX, G - 560
    for n, (ex, dur) in enumerate(COINS):
        f = clamp01((t - tc - 0.05 * n) / dur)
        if f <= 0:
            continue
        x = lerp(sx, ex, f)
        y = lerp(sy, G - 26, f) - 220 * 4 * f * (1 - f)
        ink(c, coin(x, y, 26), ORANGE, 8)
    return None


b.custom(J(), 1, 1.2, coins_fn)
H(2, "pop")
T("全输了", 3020, 3255, 104, RED, k0=3, k1=4, sfx="tom")
L(P((2180, 3398), (2480, 3398)), 5, 5.6, RED, 11, sfx="rim")
T("余额 0", 3020, 3405, 64, k0=6, k1=7, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 8–10）

scene("赚钱和守钱，两门本事", "书中观点 · 两门本事", (950, 4900, 0.85))
L(key(650, 4860), 0, 0.9, GREEN, 11, sfx="wood_high")
T("赚到", 650, 5130, 72, GREEN, k0=1, k1=1.8, sfx="pop")
L(key(1250, 4860), 2, 2.9, BLUE, 11, sfx="wood_high")
T("守住", 1250, 5130, 72, BLUE, k0=3, k1=3.8, sfx="pop")
L(join(P((900, 4840), (1000, 4840)), P((900, 4880), (1000, 4880))), 4, 4.6, BLACK, 11, sfx="wood_low")
L(cross(950, 4860, 62), 5, 5.8, RED, 12, sfx="rim")
T("两门本事", 950, 4510, 88, RED, k0=6, k1=7, sfx="ding")

PIG9 = (2650, 4980, 1.3)
scene("守住钱，要一点怕", "书中观点 · 守住钱", (2650, 4900, 0.85))
L(pig(*PIG9), 0, 0.9, ORANGE, 10, sfx="wood_high")
L(pig_hug(*PIG9), 1, 1.8, ORANGE, 10, sfx="pop")
L(join(pig_mouth(*PIG9, "flat"), sweat(PIG9[0] + 175, PIG9[1] - 150, 1.2)), 2, 2.7, BLUE, 8, sfx="pop")
T("节俭", 2230, 4560, 76, GREEN, k0=3, k1=3.8, sfx="pop")
T("怕输光", 3070, 4560, 76, RED, k0=4, k1=5, sfx="pop")
L(underline(2950, 3190, 4610, 10, 30), 5, 5.6, RED, 7, sfx="wood_low")
L(coin(2650, 4700, 34), 6, 6.6, ORANGE, 9, sfx="ding")

# 上坡路：A → B，路上两个坑；小人沿着路走，到坑边往上绕开
RA, RB = (2150, 6650), (3150, 5900)
UX, UY = (RB[0] - RA[0]) / 1250, (RB[1] - RA[1]) / 1250      # 路的方向
NX, NY = -UY, UX                                               # 法向（指向右下）
PITS = (0.35, 0.68)


def road_pt(t, off=0.0):
    return RA[0] + (RB[0] - RA[0]) * t + NX * off, RA[1] + (RB[1] - RA[1]) * t + NY * off


def route_off(t):
    return -70 * sum(math.exp(-((t - c) / 0.075) ** 2) for c in PITS)


scene("对未来乐观，对坑小心", "书中观点 · 路上有坑", (2650, 6250, 0.85))
J10 = J()
L(join(P(road_pt(0, -95), road_pt(1, -95)), P(road_pt(0, 95), road_pt(1, 95))), 0, 0.9, BLACK, 9, sfx="wood_high")
L(flag(3150, 5900), 1, 1.8, GREEN, 9, sfx="pop")
T("乐观", 2870, 5790, 66, GREEN, k0=2, k1=2.8, sfx="pop")
for n, tp in enumerate(PITS):
    x, y = road_pt(tp, 38)
    L(join(oval(x, y, 130, 64), P((x - 30, y - 6), (x + 25, y + 8))), 3 + n, 3.6 + n, RED, 9, sfx="rim")
T("小心坑", 2330, 6080, 66, RED, k0=5, k1=5.8, sfx="pop")


def walker_fn(c, k, t):
    """小人从坡底走到旗子下，经过坑时往上绕开；身后留下虚线脚印。"""
    tt = lerp(0.04, 0.93, ease_in_out(k))
    trail = skia.Path()
    for i in range(41):
        g = 0.04 + (tt - 0.04) * i / 40
        x, y = road_pt(g, route_off(g))
        trail.moveTo(x, y) if i == 0 else trail.lineTo(x, y)
    c.drawPath(trail, _dash(GREEN))
    x, y = road_pt(tt, route_off(tt))
    bounce = abs(math.sin(k * math.pi * 7)) * 10 if k < 1 else 0
    ink(c, stick(x, y - bounce, 0.38, "up" if k >= 1 else "down"), BLUE, 7)
    return None


def _dash(color):
    p = K.paint(color, 0.85, 6)
    p.setPathEffect(skia.DashPathEffect.Make([18, 16], 0))
    return p


b.custom(J10, 6, 8, walker_fn, sfx="shaker")
H(8, "ding")

# ---------------------------------------------------------------- 身边的例子：年终奖全押上（场景 11）

BX, BY = 1250, 6330             # 筐口中点
scene("年终奖全押上", "例子 · 年终奖", (950, 6250, 0.85))
MAN11 = (560, 6620, 0.8)
L(stick(*MAN11, "point"), 0, 0.9, sfx="wood_high")
L(face(*MAN11, "smile"), 0.9, 1.0)
L(envelope(850, 6270), 1, 1.7, RED, 9, sfx="pop")
T("年终奖", 850, 6300, 46, RED, k0=1.8, k1=2.6)
T("小王", 560, 6688, 50, k0=2.6, k1=3.0)
L(basket(BX, BY), 3, 3.9, BLACK, 9, sfx="wood_high")
L(arrow((975, 6235), (1120, 6300), -0.25, 32), 4, 4.6, BLACK, 8, sfx="pop")
T("全押", 1060, 6120, 58, k0=4.6, k1=5.4)
L(hole(BX, BY + 270), 6, 6.7, RED, 9, sfx="rim")
DROP = [(-70, 6740), (-5, 6745), (60, 6738), (115, 6748)]


def basket_coins_fn(c, k, t):
    """硬币先落进筐里，第 7 拍起从筐底的洞漏出去。"""
    t5, t7 = b.t_of(J11, 5), b.t_of(J11, 7)
    for n, (dx, fy) in enumerate(DROP):
        ix, iy = BX - 75 + n * 50, BY + 205 - (n % 2) * 40
        f_in = clamp01((t - t5 - 0.08 * n) / 0.3)
        if f_in <= 0:
            continue
        x, y = ix, lerp(BY - 140, iy, ease_out(f_in))
        f_out = clamp01((t - t7 - 0.12 * n) / 0.35)
        if f_out > 0:
            x = lerp(ix, BX + dx, f_out)
            y = lerp(iy, fy, f_out * f_out)
        ink(c, coin(x, y, 24), ORANGE, 7)
    return None


J11 = J()
b.custom(J11, 5, 5.3, basket_coins_fn, sfx="pop")
H(7, "shaker")

# ---------------------------------------------------------------- 两条做法（场景 12–13）

scene("别碰会让你出局的事", "做法一 · 进门先问", (950, 7600, 0.85))
L(door(950, 7600), 0, 0.9, BLACK, 10, sfx="wood_high")
T("输了", 950, 7400, 76, RED, k0=1, k1=1.8, sfx="pop")
T("还能回来吗？", 950, 7510, 60, k0=2, k1=3.5, sfx="pop")
MAN12 = (500, 7960, 0.7)
L(stick(*MAN12, "shrug"), 4, 4.8, sfx="wood_high")
L(face(*MAN12, "flat"), 4.8, 5.0)
L(bubble(470, 7590, 230, 110, -1), 5, 5.6, BLUE, 8, sfx="pop")
T("答不上", 470, 7590, 50, BLUE, k0=5.6, k1=6.4)
L(cross(950, 7790, 70), 6.5, 7.3, RED, 12)
T("就不进", 950, 7895, 54, RED, k0=7, k1=7.9, sfx="rim")
H(6, "wood_low")

PIG13 = (2650, 7623, 1.05)
scene("先保住，再去赚", "做法二 · 先保住", (2650, 7600, 0.85))
L(base(2650, 7940), 0, 0.9, BLACK, 10, sfx="wood_low")
T("先保住", 2650, 7865, 64, GREEN, k0=1, k1=1.9, sfx="pop")
L(join(pig(*PIG13), pig_mouth(*PIG13, "smile")), 2, 2.9, ORANGE, 10, sfx="wood_high")
L(coin(2650, 7400, 30), 3, 3.6, ORANGE, 9, sfx="ding")
L(arrow((2990, 7560), (3140, 7250), 0.12, 40), 4, 4.8, GREEN, 10, sfx="wood_high")
T("再去赚", 3110, 7175, 64, GREEN, k0=5, k1=5.8, sfx="pop")
L(check(2240, 7380, 80), 6, 6.8, GREEN, 14, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 4400, 0.12)
VC = (1800, 8800, 0.8)
scene("评论区：谁赚了又亏？", "评论区见", FAR, bars=4)
b.move(J(), 4, VC, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
PIG14 = (1800, 8545, 0.6)
L(join(pig(*PIG14), pig_mouth(*PIG14, "smile")), 5, 5.8, ORANGE, 8, sfx="pop")
T("你见过谁赚了又亏？", 1800, 8770, 76, RED, k0=6, k1=8.25, sfx="pop")
T("下一讲：钱最大的用处，是买回时间", 1800, 8920, 50, k0=9, k1=13, sfx="wood_high")
L(P((1400, 8970), (2200, 8970)), 13, 13.8, BLACK, 6)
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "keep", "致富与守富", "赚到了大钱，为什么又亏光了？", ACC, b.shots,
                 [f"{BOOK}第 5 章“致富 vs. 守富”（转述）",
                  "中译本：李青宗译，民主与建设出版社 / 后浪 2023"],
                 "赚到了大钱|为什么又【亏光了】？", SQUARE_SHOT,
                 ["书中观点（转述）：第 5 章“致富 vs. 守富”讲了杰西·利弗莫尔——1929 年大崩盘时很多人亏钱，他却大赚一笔；"
                  "之后他押得越来越大，最后全输光。作者借这个故事说，赚到钱和守住钱是两种不同的本事；守住钱需要节俭，"
                  "也需要一点“怕”，怕自己辛苦得来的东西被一下子拿走；对长期的未来保持乐观，同时对路上可能让你出局的事保持警惕，"
                  "做计划时要算上“计划会出岔子”。上屏均为转述，不是逐字引文。",
                  "利弗莫尔以火柴人 + 名字牌表示，不画肖像；只讲“大赚—越押越大—全输了”的心理过程，"
                  "不展开他赚钱的手法，不提他的结局。“回到 1929 年”“余额 0”、越垒越高的台子与硬币为示意画面。",
                  "年终奖全押进一个筐、筐底有洞为示意，不指向任何具体产品、平台或公司，不构成投资建议。",
                  "两条做法（进门前先问“输了还能回来吗”，答不上就不进；先保住，再去赚）为据书中思路整理。"],
                 tags="#守财 #风险")
    return b.attach(ep)
