"""03 说出感受（白板手绘版）：“我觉得你不在乎”，算感受吗？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 D 误区对照）：一条消息开局（女朋友小周发的消息两小时没回 → 她打出“我觉得你不在乎” →
男朋友回“我哪有”，两个带刺泡泡对撞，越说越远）→ drop：大泡泡裂成两半，掉出一张“想法”标签
（书中观点：“我觉得你……”后面跟的常是对对方的看法）→ 亮书，四格卡点亮“心” →
一张从上往下的对照表，一屏一对，左栏红色带刺泡泡是常说的话，右栏蓝色圆泡泡是说出感受：
我觉得你不在乎 / 我有点失落；我被忽视了 / 我很委屈（这类词在说对方怎么对我）；
我觉得我很没用 / 我很沮丧；还行吧 / 我挺紧张（用具体的感受词）→
感受词抽屉（书里列了感受词清单，平时多攒几个）→ 做法：先挑一个最准的词，再说因为什么，小泡的刺缩回去 →
他回“抱歉在开会”，两个圆泡泡挨在一起 → 拉远看全板 → 评论区互动。
书中观点为转述（马歇尔·卢森堡《非暴力沟通》第四章 体会和表达感受；阮胤华译，华夏出版社）；
男女朋友的消息、四组对照句与做法均为示意，据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, clock, cross, face,
                               hands_at, join, marker, partial, rect, stick)

from .common import BOOK, episode

ACC = "#C84E74"
SQUARE_SHOT = 3                 # 场景 4：裂开的大泡泡 + 掉出来的“想法”标签
GRAY = "#8C9199"

b = Board(size=(3600, 15000))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def J():
    return len(b.shots) - 1


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法：话泡泡“小泡”

def pao(x, y, w, h, tail=-1, r=None) -> skia.Path:
    """小泡的轮廓：圆角气泡 + 小尾巴（tail=-1 尾巴在左下，+1 在右下）。"""
    r = h * 0.42 if r is None else r
    p = rect(x, y, w, h, r)
    p.moveTo(x + tail * w * 0.22, y + h / 2)
    p.lineTo(x + tail * w * 0.34, y + h / 2 + 60)
    p.lineTo(x + tail * w * 0.06, y + h / 2)
    return p


def _rim(x, y, w, h, n, r=None):
    """气泡轮廓上等距取 n 个点：(位置, 切向, 外法向)。"""
    r = h * 0.42 if r is None else r
    pm = skia.PathMeasure(rect(x, y, w, h, r), False)
    total = pm.getLength()
    out = []
    for i in range(n):
        pos, tan = pm.getPosTan(total * (i + 0.5) / n)
        px, py, tx, ty = pos.x(), pos.y(), tan.x(), tan.y()
        nx, ny = ty, -tx
        if nx * (px - x) + ny * (py - y) < 0:
            nx, ny = -nx, -ny
        out.append((px, py, tx, ty, nx, ny))
    return out


def spikes(x, y, w, h, tail=-1, length=36, n=None, hw=15, r=None) -> skia.Path:
    """红色锯齿刺：在气泡轮廓上等距加三角刺，尾巴那一段不加。"""
    n = n or max(14, int((w + h) * 2 / 80))
    lo, hi = sorted((x + tail * w * 0.02, x + tail * w * 0.40))
    parts = []
    for px, py, tx, ty, nx, ny in _rim(x, y, w, h, n, r):
        if py > y + h / 2 - 8 and lo - 10 <= px <= hi + 10:
            continue
        parts.append(P((px - tx * hw, py - ty * hw), (px + nx * length, py + ny * length), (px + tx * hw, py + ty * hw)))
    return join(*parts)


def pface(x, y, s=1.0, mood="sad", curve=None) -> skia.Path:
    """小泡的脸：两点眼睛 + 一张小嘴。(x, y) 为两眼中点；curve>0 嘴角上扬，<0 往下撇。"""
    c = (24 if mood == "smile" else -22) if curve is None else curve
    p = join(circle(x - 30 * s, y, 7 * s), circle(x + 30 * s, y, 7 * s))
    p.moveTo(x - 26 * s, y + 36 * s)
    p.quadTo(x, y + 36 * s + c * s, x + 26 * s, y + 36 * s)
    return p


def mix_color(a, c, k):
    return "#%02X%02X%02X" % tuple(int(round(lerp(u, v, k))) for u, v in zip(_rgb(a), _rgb(c)))


def _rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


# ---------------------------------------------------------------- 本讲画法：道具

def phone(x, y, w, h) -> skia.Path:
    return join(rect(x, y, w, h, 50), P((x - 50, y - h / 2 + 36), (x + 50, y - h / 2 + 36)),
                P((x - 70, y + h / 2 - 34), (x + 70, y + h / 2 - 34)))


def spiral(x, y, r0, r1, turns=2.0) -> skia.Path:
    """绕钟走两圈的箭头。"""
    pts = []
    n = int(60 * turns)
    for i in range(n + 1):
        t = i / n
        a = -math.pi / 2 + 2 * math.pi * turns * t
        r = lerp(r0, r1, t)
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    p = P(*pts)
    (x1, y1), (x0, y0) = pts[-1], pts[-4]
    ang = math.atan2(y1 - y0, x1 - x0)
    for d in (0.5, -0.5):
        p.moveTo(x1, y1)
        p.lineTo(x1 - 34 * math.cos(ang + d), y1 - 34 * math.sin(ang + d))
    return p


def sparks(x, y, r0=30, r1=95, n=8) -> skia.Path:
    parts = []
    for i in range(n):
        a = i / n * 2 * math.pi + 0.2
        rr = r1 if i % 2 == 0 else r1 * 0.7
        parts.append(P((x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + rr * math.cos(a), y + rr * math.sin(a))))
    return join(*parts)


def heart(x, y, r=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def eye(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 55 * s, y)
    p.quadTo(x, y - 48 * s, x + 55 * s, y)
    p.quadTo(x, y + 48 * s, x - 55 * s, y)
    return join(p, circle(x, y, 17 * s))


def battery(x, y, s=1.0) -> skia.Path:
    return join(rect(x - 6 * s, y, 96 * s, 52 * s, 8 * s), rect(x + 50 * s, y, 12 * s, 22 * s, 3 * s),
                P((x - 40 * s, y - 14 * s), (x - 40 * s, y + 14 * s)))


def palm(x, y, s=1.0) -> skia.Path:
    """伸出的手：手掌 + 四根手指 + 拇指。"""
    parts = [rect(x, y + 18 * s, 70 * s, 62 * s, 16 * s)]
    for i, hgt in enumerate((40, 50, 48, 38)):
        fx = x - 26 * s + i * 17 * s
        parts.append(P((fx, y - 12 * s), (fx, y - (12 + hgt) * s)))
    parts.append(P((x - 35 * s, y + 18 * s), (x - 62 * s, y - 6 * s)))
    return join(*parts)


def four_card(x, y, cell=180) -> skia.Path:
    """四格卡：眼睛（观察）、心（感受）、电池（需要）、伸出的手（请求）。"""
    w = cell * 4
    parts = [rect(x, y, w, cell, 20)]
    for i in (1, 2, 3):
        xx = x - w / 2 + i * cell
        parts.append(P((xx, y - cell / 2), (xx, y + cell / 2)))
    cx = [x - w / 2 + cell * (i + 0.5) for i in range(4)]
    parts += [eye(cx[0], y), heart(cx[1], y + 8, 40), battery(cx[2], y), palm(cx[3], y)]
    return join(*parts)


def stick_chest(x, y, s=1.0) -> skia.Path:
    """手按胸口的小人：(x, y) 为脚底。"""
    hy = y - 290 * s
    sh = hy + 80 * s
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)),
                P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)),
                P((x - 70 * s, hy + 170 * s), (x, sh)),
                P((x, sh), (x + 60 * s, sh + 55 * s), (x + 14 * s, hy + 112 * s)),
                face(x, y, s, "flat"))


def cloud(x, y, w, h) -> skia.Path:
    """一团灰雾：起伏的闭合轮廓 + 两道雾线。"""
    pts = []
    for i in range(72):
        a = i / 72 * 2 * math.pi
        k = 1 + 0.1 * abs(math.sin(a * 5))
        pts.append((x + w / 2 * k * math.cos(a), y + h / 2 * k * math.sin(a)))
    return join(P(*pts, close=True), P((x - w * 0.42, y + h * 0.68), (x + w * 0.1, y + h * 0.68)),
                P((x - w * 0.05, y + h * 0.82), (x + w * 0.45, y + h * 0.82)))


def drop(x, y, s=1.0) -> skia.Path:
    """一颗汗珠。"""
    p = skia.Path()
    p.moveTo(x, y - 34 * s)
    p.quadTo(x + 22 * s, y - 2 * s, x + 21 * s, y + 12 * s)
    p.cubicTo(x + 20 * s, y + 34 * s, x - 20 * s, y + 34 * s, x - 21 * s, y + 12 * s)
    p.quadTo(x - 22 * s, y - 2 * s, x, y - 34 * s)
    return p


def cabinet(x, y, w=480, h=200) -> skia.Path:
    return join(rect(x, y, w, h, 14), P((x - w / 2, y + h / 2), (x - w / 2, y + h / 2 + 40)),
                P((x + w / 2, y + h / 2), (x + w / 2, y + h / 2 + 40)))


def drawer(x, y, w=400, h=110) -> skia.Path:
    """拉开的抽屉：前面板 + 敞开的口。(x, y) 为前面板中心。"""
    return join(rect(x, y, w, h, 10), P((x - w / 2, y - h / 2), (x - w / 2 + 40, y - h / 2 - 70),
                                        (x + w / 2 - 40, y - h / 2 - 70), (x + w / 2, y - h / 2)))


def tag_shape(x, y, w=300, h=140) -> skia.Path:
    """标签：左端尖角 + 穿绳小孔。"""
    return join(P((x - w / 2, y), (x - w / 2 + 50, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2),
                  (x - w / 2 + 50, y + h / 2), close=True), circle(x - w / 2 + 50, y, 12))


def ellipse(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def card(c, x, y, word, s=1.0, color=BLUE):
    """一张感受词卡（动态项里画）。"""
    w, h = 250 * s, 120 * s
    K.rr(c, x, y, w, h, 18 * s, "#FFFFFF")
    c.drawPath(rect(x, y, w, h, 18 * s), marker(color, 8))
    K.text(c, word, x, y, 64 * s, "hand", BLACK)


# ---------------------------------------------------------------- 开局：消息没回（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

PH = (1000, 1000, 520, 820)
scene("消息两小时没回", "开局 · 一条消息", (950, 1000, 0.75), bars=2)
L(phone(*PH), 0, 0.9, BLACK, 10, sfx="wood_high")
L(pao(1060, 780, 360, 110, 1, 40), 1, 1.6, BLUE, 8, sfx="pop")
T("到家了吗？", 1060, 780, 56, BLUE, k0=1.6, k1=2.85)
L(join(clock(1460, 780, 95), hands_at(1460, 780, 95, 3, 0), spiral(1460, 780, 118, 140)), 3, 3.9, BLACK, 8,
  sfx="wood_low")
T("2 小时", 1460, 1000, 66, RED, k0=4, k1=4.8, sfx="pop")
L(stick(430, 1400, 0.95, "hold", hair=True), 5, 5.8, BLACK, 10, sfx="wood_high")
L(face(430, 1400, 0.95, "sad"), 5.8, 6.0, BLACK, 8)

scene("我觉得你不在乎", "开局 · 她发出去", (1000, 1000, 1.0))
L(pao(1000, 1100, 400, 290, 1), 0, 0.9, RED, 9, sfx="wood_high")
L(pface(1000, 1030, 1.0, "sad"), 1, 1.6, RED, 8, sfx="pop")
T("我觉得你不在乎", 1000, 1140, 50, RED, k0=2, k1=3.75, sfx="pop")
L(spikes(1000, 1100, 400, 290, 1, 30), 4, 4.9, RED, 7, sfx="rim")
T("已送达", 880, 1335, 44, k0=5, k1=5.8, sfx="wood_high")

scene("他回：我哪有", "开局 · 越说越远", (2700, 1000, 0.85), shake=[6])
L(join(stick(2250, 1480, 0.8, "down", hair=True), face(2250, 1480, 0.8, "sad"),
       stick(3150, 1480, 0.8, "shrug"), face(3150, 1480, 0.8, "sad")), 0, 0.9, BLACK, 9, sfx="wood_low")
L(join(pao(2420, 830, 400, 240, -1), pface(2420, 775, 0.8), spikes(2420, 830, 400, 240, -1, 30)), 1, 1.9, RED, 8,
  sfx="pop")
T("你不在乎", 2420, 880, 60, RED, k0=2, k1=3)
L(join(pao(2980, 830, 400, 240, 1), pface(2980, 775, 0.8), spikes(2980, 830, 400, 240, 1, 30)), 3, 3.9, RED, 8,
  sfx="rim")
T("我哪有！", 2980, 880, 60, RED, k0=4, k1=5, sfx="pop")
L(sparks(2700, 830), 6, 6.7, RED, 8, sfx="shaker")
T("越说越远", 2700, 1190, 72, RED, k0=7, k1=8, sfx="kick")

# ---------------------------------------------------------------- drop：大泡泡裂开，掉出“想法”（场景 4）

BX, BY, BW, BH = 2700, 2250, 800, 340
BIG = join(pao(BX, BY, BW, BH, -1), spikes(BX, BY, BW, BH, -1, 45), pface(BX, BY - 95, 1.4))
CRACK = [(BX, 1985), (BX - 30, 2060), (BX + 28, 2140), (BX - 26, 2220), (BX + 30, 2300), (BX - 24, 2380),
         (BX + 20, 2450), (BX, 2530)]
j_drop = scene("觉得后面是想法", "书中观点 · 第四章", (2700, 2550, 0.8), shake=[0, 5], flashes=[0])


def _side(sign):
    far = BX + sign * 900
    pts = [(far, CRACK[0][1])] + CRACK + [(far, CRACK[-1][1])]
    return P(*pts, close=True)


def split_fn(c, k, Tm):
    """第 0 拍弹出大泡泡，第 2 拍裂缝，第 3 拍裂成两半往两边歪，第 4–5 拍掉出“想法”标签。"""
    t = lambda kk: b.t_of(j_drop, kk)
    pop = ease_out(clamp01((Tm - t(0)) / 0.3))
    sc = 0.6 + 0.4 * pop + 0.08 * math.sin(math.pi * pop)
    crack = clamp01((Tm - t(2)) / max(1e-3, t(2.6) - t(2)))
    sp = ease_out(clamp01((Tm - t(3)) / max(1e-3, t(3.7) - t(3))))
    crack_path = P(*CRACK)
    tip = None

    def body(cc):
        cc.drawPath(BIG, marker(RED, 10))
        K.text(cc, "我觉得你不在乎", BX, BY + 50, 84, "hand", RED)
        if crack > 0:
            part, p = partial(crack_path, crack)
            cc.drawPath(part, marker(BLACK, 11))
            return p
        return None

    c.save()
    c.translate(BX, BY)
    c.scale(sc, sc)
    c.translate(-BX, -BY)
    if sp <= 0:
        tip = body(c)
    else:
        for sign in (-1, 1):
            c.save()
            c.translate(sign * 80 * sp, 20 * sp)
            c.rotate(sign * 6 * sp, BX, CRACK[-1][1])
            c.clipPath(_side(sign), skia.ClipOp.kIntersect, True)
            body(c)
            c.restore()
    c.restore()
    # 标签：第 4 拍从裂口掉出，第 5 拍落地（kick），落地后轻轻一弹
    if Tm >= t(4):
        f = clamp01((Tm - t(4)) / max(1e-3, t(5) - t(4)))
        y = lerp(BY, 2700, f * f)
        rot = -8 * f
        if Tm > t(5):
            d = Tm - t(5)
            y -= 26 * math.exp(-d * 9) * abs(math.sin(d * 18))
        with K.at(c, BX, y, rot):
            path = tag_shape(0, 0)
            c.drawPath(path, K.paint("#FFFFFF"))
            c.drawPath(path, marker(BLACK, 9))
            K.text(c, "想法", 25, 0, 90, "hand", RED)
    return tip if crack < 1 else None


b.custom(j_drop, 0, 5.5, split_fn, sfx="kick")
H(2, "rim")
H(3, "shaker")
H(5, "kick", 0.7)
T("这是对他的看法", 2700, 2930, 66, k0=6, k1=7.75, sfx="pop")

# ---------------------------------------------------------------- 亮书 + 四格卡（场景 5）

scene("有本书讲过", "非暴力沟通 · 书中观点", (1800, 3950, 0.85))
L(book(1450, 3800, 400, 270), 0, 0.9, BLACK, 10, sfx="wood_low")
T("非暴力沟通", 1450, 3600, 72, GREEN, k0=1, k1=2.25, sfx="pop")
L(four_card(1800, 4280), 3, 3.9, BLACK, 8, sfx="wood_high")
T("观察　　感受　　需要　　请求", 1800, 4430, 46, k0=4, k1=5.4, sfx="pop")


def lit_fn(c, k, Tm):
    K.rr(c, 1710, 4280, 176 * ease_out(k), 176, 18, ACC, 0.28)
    return None


b.custom(J(), 6, 6.5, lit_fn, sfx="ding")
L(heart(1710, 4288, 40), 6, 6.8, RED, 12)
L(check(1710, 4110, 38), 7, 7.6, GREEN, 11, sfx="pop")

# ---------------------------------------------------------------- 对照表：一屏一对（场景 6–9）

LX, RX = 1480, 2120              # 左栏（✗ 常说）与右栏（✓ 说感受）中心
PW, PHT = 520, 280


def bad(y, sfx="rim", k0=0):
    """左栏：红色带刺小泡。"""
    L(join(pao(LX, y, PW, PHT, -1), pface(LX, y - 70, 0.9), spikes(LX, y, PW, PHT, -1, 32)), k0, k0 + 0.9, RED, 8,
      sfx=sfx)


def good(y, k0, k1, sfx="pop", mood="smile"):
    """右栏：蓝色圆泡泡。"""
    L(join(pao(RX, y, PW, PHT, 1), pface(RX, y - 70, 0.9, mood)), k0, k1, BLUE, 8, sfx=sfx)


scene("换个说法", "对照一 · 说出感受", (1800, 5300, 0.85))
L(join(P((1800, 4820), (1800, 5760)), P((1200, 4950), (2400, 4950)), cross(1300, 4880, 28), check(1990, 4880, 32)),
  0, 0.9, BLACK, 8, sfx="wood_high")
T("常说", 1450, 4880, 64, RED, k0=1, k1=1.8, sfx="pop")
T("说感受", 2170, 4880, 64, BLUE, k0=2, k1=2.8, sfx="pop")
bad(5340, k0=3)
T("我觉得你不在乎", LX, 5380, 56, RED, k0=4, k1=5.75, sfx="pop")
good(5340, 6, 6.6, sfx="wood_high")
T("我有点失落", RX, 5380, 56, BLUE, k0=6.6, k1=7.85)

scene("被忽视，算哪种", "对照二 · 书中观点", (1800, 6700, 0.85))
bad(6500)
T("我被忽视了", LX, 6540, 56, RED, k0=1, k1=2.25, sfx="pop")
L(join(stick(1400, 7150, 0.62, "point"), face(1400, 7150, 0.62, "sad")), 3, 3.8, BLACK, 8, sfx="wood_high")
L(cross(1440, 6990, 120), 4, 4.6, RED, 12, sfx="rim")
L(join(stick_chest(2120, 7150, 0.62), heart(2129, 7002, 14)), 5, 5.9, BLUE, 8, sfx="wood_high")
good(6500, 6, 6.6)
T("我很委屈", RX, 6540, 56, BLUE, k0=6.6, k1=7.6)

scene("骂自己也一样", "对照三 · 说出感受", (1800, 8100, 0.85))
bad(7900)
T("我觉得我很没用", LX, 7940, 56, RED, k0=1, k1=2.75, sfx="pop")
L(join(stick(LX, 8560, 0.6, "down"), face(LX, 8560, 0.6, "sad")), 3, 3.9, BLACK, 8, sfx="wood_high")
T("没用", LX, 8290, 64, RED, k0=4, k1=4.6, sfx="pop")
b.erase(J(), 5, 5.7, LX, 8290, 210, 96)
H(5, "shaker")
good(7900, 6, 6.6)
T("我很沮丧", RX, 7940, 56, BLUE, k0=6.6, k1=7.6)

scene("还行，太笼统", "对照四 · 书中观点", (1800, 9500, 0.85))
L(cloud(LX, 9320, 500, 250), 0, 0.9, GRAY, 9, sfx="wood_low")
T("还行吧", LX, 9330, 64, "#5A5F68", k0=1, k1=1.8, sfx="pop")
L(cross(1250, 9180, 40), 3, 3.5, RED, 11, sfx="rim")
good(9320, 4, 4.6)
T("我挺紧张", RX, 9360, 56, BLUE, k0=4.6, k1=5.6)
L(drop(2235, 9235, 0.9), 6, 6.6, BLUE, 7, sfx="ding")
T("用具体的词", 1800, 9800, 64, GREEN, k0=6.7, k1=7.95)

# ---------------------------------------------------------------- 感受词抽屉（场景 10–11）

WORDS = [("紧张", 1350), ("委屈", 1650), ("踏实", 1950), ("心慌", 2250)]
ROW_Y = 10600
MOUTH = (1460, 11050)
PICK = (2120, 11180)
j_drawer = scene("感受词太少", "书中观点 · 感受词清单", (1800, 10900, 0.85))
L(cabinet(1460, 11230), 0, 0.9, BLACK, 9, sfx="wood_low")
L(drawer(1460, 11190), 1, 1.8, BLACK, 9, sfx="wood_high")
T("感受词清单", 1460, 11190, 52, k0=2, k1=3.25, sfx="pop")
j_pick = j_drawer + 1


def fly_fn(word, x, kland):
    def fn(c, k, Tm):
        if word == "心慌" and Tm >= b.t_of(j_pick, 0):
            return None                              # 交给下一屏：被手指抽出
        e = ease_out(k)
        cx, cy = lerp(MOUTH[0], x, e), lerp(MOUTH[1], ROW_Y, e) - 120 * math.sin(math.pi * e)
        card(c, cx, cy, word, lerp(0.5, 1.0, e))
        return None

    return fn


for n, (w, x) in enumerate(WORDS):
    kl = 3 + n
    b.custom(J(), kl - 0.5, kl, fly_fn(w, x, kl))
    H(kl, "pop")


scene("先挑一个词", "做法 · 据书中思路", (1800, 10900, 0.85))


def pick_fn(c, k, Tm):
    e = ease_in_out(k)
    x, y = lerp(WORDS[3][1], PICK[0], e), lerp(ROW_Y, PICK[1], e)
    s = lerp(1.0, 1.5, e)
    card(c, x, y, "心慌", s, RED if k >= 1 else BLUE)
    return (x + 60 * s, y + 40 * s) if k < 1 else None


b.custom(J(), 0, 1, pick_fn, sfx="wood_high")
H(1, "pop")
L(ellipse(*PICK, 470, 250), 2, 2.8, RED, 9, sfx="ding")
T("最准的一个", PICK[0], 11395, 60, BLUE, k0=3, k1=4.25, sfx="pop")

# ---------------------------------------------------------------- 再说因为什么：刺缩回去（场景 12）

QX, QY, QW, QH = 1800, 12150, 1000, 440
j_say = scene("再说因为什么", "做法 · 据书中思路", (1800, 12150, 0.85))


def retract_fn(c, k, Tm):
    """第 0 拍描出带刺小泡，第 5 拍刺一根根缩回去，红变蓝，嘴角上扬。"""
    t5 = b.t_of(j_say, 5)
    g = ease_in_out(clamp01((Tm - t5) / 0.55))
    col = mix_color(RED, BLUE, g)
    outline = join(pao(QX, QY, QW, QH, -1), pface(QX, QY - 120, 1.2, curve=lerp(-22, 26, g)))
    part, tip = partial(outline, k)
    c.drawPath(part, marker(col, 10))
    if k >= 1:
        n = 26
        for i, (px, py, tx, ty, nx, ny) in enumerate(_rim(QX, QY, QW, QH, n)):
            if py > QY + QH / 2 - 8 and QX - QW * 0.42 <= px <= QX + 10:
                continue
            gi = ease_in_out(clamp01((Tm - t5 - i * 0.012) / 0.4))      # 一根根缩回去
            ln = 42 * (1 - gi)
            if ln > 1:
                c.drawPath(P((px - tx * 16, py - ty * 16), (px + nx * ln, py + ny * ln), (px + tx * 16, py + ty * 16)),
                           marker(RED, 8))
    return tip


b.custom(J(), 0, 0.9, retract_fn, sfx="wood_high")
T("你两小时没回", QX, 12160, 70, k0=1, k1=2.5, sfx="pop")
T("我有点心慌", QX, 12280, 70, BLUE, k0=3, k1=4.25, sfx="pop")
H(5, "ding")
L(heart(2050, 12286, 26), 6, 6.8, RED, 8, sfx="pop")

# ---------------------------------------------------------------- 他回：在开会（场景 13）

scene("他回：在开会", "结果 · 示意", (1800, 12560, 0.7))
L(join(pao(2050, 12640, 760, 340, 1), pface(2050, 12530, 0.9, "smile")), 0, 0.9, BLUE, 9, sfx="wood_high")
T("抱歉在开会", 2050, 12630, 60, BLUE, k0=1, k1=2.25, sfx="pop")
T("散了马上打给你", 2050, 12730, 60, BLUE, k0=3, k1=4.75, sfx="pop")
L(heart(1420, 12660, 46), 5, 5.8, RED, 9, sfx="ding")
T("话接上了", 1800, 13030, 70, GREEN, k0=6, k1=7, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 6900, 0.075)
CV = (1800, 14300, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
H(0, "cymbal", 0.5)
H(2, "ding")
b.move(J(), 4, CV, dur=1.1)
H(4, "wood_high", 0.6)
L(join(rect(1800, 14250, 1100, 420, 30), circle(1330, 14130, 40)), 6, 6.9, BLACK, 8,
  sfx="wood_high")
T("用一个词，说说今天的感受", 1830, 14250, 60, RED, k0=7, k1=10, sfx="pop")
T("下一讲：挨了句批评，你会怎么接？", 1800, 14570, 50, k0=10, k1=14, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "feel", "说出感受", "“我觉得你不在乎”，算感受吗？", ACC, b.shots,
                 [f"{BOOK}第四章 体会和表达感受（转述）", "中译本：阮胤华译，华夏出版社"],
                 "“我觉得你不在乎”|算【感受】吗？", SQUARE_SHOT,
                 ["书中观点均为转述，不是逐字引文：第四章讲体会和表达感受——“我觉得……”后面常跟的是想法或判断，"
                  "说的是对对方的看法；“被忽视”“被误解”这类词说的是对方怎么对我，偏向解读；“还好”“不错”这类词太笼统；"
                  "书里列了感受词清单，建议多积累感受词。出处：马歇尔·卢森堡《非暴力沟通》（Marshall B. Rosenberg, "
                  "Nonviolent Communication: A Language of Life），阮胤华译，华夏出版社。",
                  "女朋友小周的消息两小时没回、男朋友小林回“我哪有”“抱歉在开会”均为示意情节，不指向任何具体个人。",
                  "四组对照句（我觉得你不在乎／我有点失落；我被忽视了／我很委屈；我觉得我很没用／我很沮丧；"
                  "还行吧／我挺紧张）为据书中思路整理的示意，不是书中原句。",
                  "抽屉里的四个感受词为示意，不是书中清单的原样摘录；“先挑一个最准的词，再说因为什么”为据书中思路整理的做法。"],
                 tags="#情绪 #恋爱")
    return b.attach(ep)
