"""06 舒适区边缘（白板手绘版）：天天在练，怎么还在原地？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 J 一个比喻贯穿：健身房的杠铃）：小林走进健身房，一排杠铃 → 天天举最轻的，一口气二十个，胳膊没变 →
一冲动换最重的，腿开始抖 → drop：重杠铃“砰”地砸地，小林被压趴，轻杠铃落满灰 → 亮书 →
书中观点（三副杠铃对上三个区：舒适区、拉伸区、困难区；太轻练不出东西，太重容易受挫放弃，
中间那副“大致看得懂、要动脑筋”）→ 杠铃换回打工人练的本事（练英语：背会的词 / 看原版剧 / 看带字幕的短片）→
练的四个要点挂在杠铃杆上（目标清楚、专心、有反馈、在拉伸区）→ 做法：举顺了再加一片，别一下加满 →
一个月后拉远：小林胳膊粗了一圈，宝宝的舵上多一道握痕 → 评论区互动。
书中观点为转述（周岭《认知觉醒》第五章 学习力：第一节 匹配，舒适区边缘；刻意练习的四个要点）；
杠铃是对书中观点的通俗比喻；小林练杠铃、练英语、一次只加一片均为示意，据书中思路整理。
"""

import math
import random

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, face, join, marker,
                               partial, rect, stick, underline)

from .common import BOOK, episode

ACC = "#3D8B6E"
SQUARE_SHOT = 5                 # 场景 6：三副杠铃一排，轻的落灰、重的砸地、中间那副被小林举起

b = Board(size=(3600, 11700))
DROP = 3                        # 场景 4（从 0 数）：重杠铃砸下


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(fn, k0, k1, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


def ink(c, path, color, width):
    """和引擎描线同样的马克笔笔触（custom 动画里用）。"""
    c.drawPath(path, marker(color, width))
    c.drawPath(path, K.paint(color, 0.22, width * 0.45, blur=1.2))


def shifted(path, dx=0.0, dy=0.0) -> skia.Path:
    p = skia.Path(path)
    p.offset(dx, dy)
    return p


# ---------------------------------------------------------------- 本讲画法：杠铃与举杠铃的人

LIGHT = dict(half=220, ph=90, pw=26, n=1)       # 最轻的：小铃片一片
MID = dict(half=260, ph=170, pw=34, n=2)        # 中间那副
HEAVY = dict(half=420, ph=320, pw=60, n=3)      # 最重的：大铃片三片


def barbell(x, y, half, ph, pw, n=1, extra=0) -> skia.Path:
    """杠铃：杆中心 (x, y)，杆半长 half；每边 n 片铃片（高 ph、厚 pw），从杆端往里排；extra 为再往里加的薄片数。"""
    parts = [P((x - half, y), (x + half, y))]
    for side in (-1, 1):
        off = half - 30 - pw / 2
        for i in range(n):
            parts.append(rect(x + side * off, y, pw, ph, 8))
            off -= pw + 8
        for i in range(extra):
            parts.append(rect(x + side * (off + pw / 2 - 15), y, 26, ph * 0.86, 6))
            off -= 34
        cx = x + side * (off + pw / 2 - 6)
        parts.append(P((cx, y - ph * 0.14), (cx, y + ph * 0.14)))
    return join(*parts)


def added_plates(x, y, half, ph, pw, n, i) -> skia.Path:
    """场景 12：第 i 次加上的一对薄片（与 barbell(extra=…) 同位置）。"""
    off = half - 30 - pw / 2 - n * (pw + 8) - i * 34
    return join(*[rect(x + side * (off + pw / 2 - 15), y, 26, ph * 0.86, 6) for side in (-1, 1)])


def body(x, y, s=1.0) -> skia.Path:
    """没画胳膊的小人：头、身子、腿。(x, y) 为脚底。"""
    hy = y - 290 * s
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)),
                P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)))


def arms(x, y, s, bar_y, spread=110, thick=False) -> skia.Path:
    """两只胳膊从肩膀伸到杠铃杆上 (x±spread, bar_y)；thick=True 画出鼓起来的二头肌。"""
    sh = y - 290 * s + 80 * s
    parts = []
    for side in (-1, 1):
        hx = x + side * spread * s
        ex = x + side * (spread + 45) * s
        ey = (sh + bar_y) / 2 + 15 * s
        parts.append(P((x, sh), (ex, ey), (hx, bar_y)))
        if thick:
            bump = skia.Path()
            bump.moveTo(x + side * 10 * s, sh + 4 * s)
            bump.quadTo(x + side * (spread * 0.5 + 60) * s, (sh + ey) / 2 + 30 * s, ex, ey)
            bump.moveTo(ex, ey)
            bump.quadTo(x + side * (spread + 75) * s, (ey + bar_y) / 2, hx, bar_y)
            parts.append(bump)
    return join(*parts)


def strain(x, y, s=1.0) -> skia.Path:
    """咬牙：眯眼两道 + 一排牙。"""
    hy = y - 290 * s
    return join(P((x - 24 * s, hy - 10 * s), (x - 8 * s, hy - 4 * s)), P((x + 24 * s, hy - 10 * s), (x + 8 * s, hy - 4 * s)),
                rect(x, hy + 18 * s, 40 * s, 16 * s, 4 * s), P((x, hy + 10 * s), (x, hy + 26 * s)))


def sweat(x, y, s=1.0) -> skia.Path:
    """三道汗：头两侧往外甩的水滴。(x, y) 为脚底。"""
    hy = y - 290 * s
    parts = []
    for dx, dy in ((-75, -35), (78, -20), (62, -78)):
        cx, cy = x + dx * s, hy + dy * s
        d = skia.Path()
        d.moveTo(cx, cy - 22 * s)
        d.quadTo(cx + 16 * s, cy + 2 * s, cx, cy + 12 * s)
        d.quadTo(cx - 16 * s, cy + 2 * s, cx, cy - 22 * s)
        parts.append(d)
    return join(*parts)


def tremble(x, y, s=1.0) -> skia.Path:
    """膝盖两侧的抖动折线。"""
    parts = []
    for side in (-1, 1):
        x0 = x + side * 90 * s
        parts.append(P((x0, y - 120 * s), (x0 + side * 14 * s, y - 100 * s), (x0, y - 80 * s), (x0 + side * 14 * s, y - 60 * s),
                       (x0, y - 40 * s)))
    return join(*parts)


_rng = random.Random(6)


def dust(x, y, w) -> skia.Path:
    """落灰：铃片上方一层波浪 + 散落的灰点。(x, y) 为灰层中线。"""
    parts = [underline(x - w / 2, x + w / 2, y, 8, 30)]
    for _ in range(9):
        parts.append(circle(x + _rng.uniform(-w / 2, w / 2), y - _rng.uniform(18, 60), _rng.uniform(4, 8)))
    return join(*parts)


def yawn(x, y, s=1.0) -> skia.Path:
    """打哈欠：眯眼 + 张大的嘴 + 头顶 Z。(x, y) 为脚底。"""
    hy = y - 290 * s
    return join(P((x - 24 * s, hy - 10 * s), (x - 8 * s, hy - 10 * s)), P((x + 8 * s, hy - 10 * s), (x + 24 * s, hy - 10 * s)),
                circle(x, hy + 18 * s, 12 * s),
                P((x + 70 * s, hy - 110 * s), (x + 110 * s, hy - 110 * s), (x + 70 * s, hy - 70 * s), (x + 110 * s, hy - 70 * s)),
                P((x + 130 * s, hy - 170 * s), (x + 155 * s, hy - 170 * s), (x + 130 * s, hy - 145 * s), (x + 155 * s, hy - 145 * s)))


def note(x, y, w=250, h=150) -> skia.Path:
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 34), (x + w / 2 - 34, y + h / 2),
                  (x - w / 2, y + h / 2), close=True),
                P((x + w / 2, y + h / 2 - 34), (x + w / 2 - 34, y + h / 2 - 34), (x + w / 2 - 34, y + h / 2)))


def wind(x, y) -> skia.Path:
    parts = []
    for i, (dx, ln) in enumerate(((0, 230), (40, 180), (-20, 200))):
        yy = y + i * 55
        p = skia.Path()
        p.moveTo(x + dx, yy)
        p.lineTo(x + dx + ln, yy)
        p.quadTo(x + dx + ln + 40, yy, x + dx + ln + 40, yy - 25)
        parts.append(p)
    return join(*parts)


def rack(x, y) -> skia.Path:
    """杠铃架：两根立柱 + 底脚 + 三层挂钩。(x, y) 为地面中点。"""
    parts = []
    for ux in (x - 100, x + 100):
        parts.append(P((ux, y), (ux, y - 730)))
        parts.append(P((ux - 50, y), (ux + 50, y)))
        for hy in (650, 430, 170):
            parts.append(P((ux, y - hy), (ux + (25 if ux > x else -25), y - hy), (ux + (25 if ux > x else -25), y - hy - 25)))
    return join(*parts)


def lying(x, y) -> skia.Path:
    """被压趴的小林：头朝左趴在地上，X 眼，两只手往上撑。(x, y) 为头心。"""
    e = skia.Path()
    for ex in (x - 14, x + 12):
        e.moveTo(ex - 8, y - 14)
        e.lineTo(ex + 8, y + 2)
        e.moveTo(ex + 8, y - 14)
        e.lineTo(ex - 8, y + 2)
    return join(circle(x, y, 38), e, P((x + 38, y + 10), (x + 210, y + 14)),
                P((x + 210, y + 14), (x + 300, y - 10)), P((x + 210, y + 14), (x + 305, y + 34)),
                P((x + 70, y + 12), (x + 40, y - 70)), P((x + 120, y + 12), (x + 150, y - 70)))


def impact(x, y) -> skia.Path:
    """砸地：地面裂纹 + 两侧冲击短线。"""
    parts = [P((x - 40, y), (x - 70, y + 20), (x - 50, y + 40)), P((x + 40, y), (x + 80, y + 18), (x + 60, y + 42))]
    for side in (-1, 1):
        for i, (dx, dy) in enumerate(((60, -30), (75, -90), (60, -150))):
            parts.append(P((x + side * (dx + 30), y + dy), (x + side * (dx + 100), y + dy - 20)))
    return join(*parts)


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def rudder(x, y, r=140) -> skia.Path:
    """船舵：轮圈 + 轮毂 + 八根辐条伸出把手。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.22)]
    for i in range(8):
        a = i / 8 * 2 * math.pi
        parts.append(P((x + math.cos(a) * r * 0.22, y + math.sin(a) * r * 0.22),
                       (x + math.cos(a) * r * 1.28, y + math.sin(a) * r * 1.28)))
        parts.append(circle(x + math.cos(a) * r * 1.33, y + math.sin(a) * r * 1.33, r * 0.07))
    return join(*parts)


def grips(x, y, r, idx) -> skia.Path:
    """舵圈上的握痕：idx 为第几道（从 0 起），每道是轮圈外侧三条短横。"""
    parts = []
    for i in idx:
        a = (-90 + 22.5 + i * 45) / 180 * math.pi
        for d in (-0.12, 0.0, 0.12):
            b0 = a + d
            parts.append(P((x + math.cos(b0) * r * 0.86, y + math.sin(b0) * r * 0.86),
                           (x + math.cos(b0) * r * 1.14, y + math.sin(b0) * r * 1.14)))
    return join(*parts)


def brothers(x, y):
    """脑内三兄弟里的两个哥哥：老大（拐杖）、老二（耳机）。x 为老大脚底横坐标，y 为脚底线；返回 (老大, 老二)。"""
    s = 0.55
    elder = join(stick(x, y, s, "down"), P((x + 30 * s * 2, y - 150 * s), (x + 70 * s, y)))
    ux = x + 190
    hy = y - 290 * s
    phones = skia.Path()
    phones.addArc(skia.Rect.MakeXYWH(ux - 55 * s, hy - 60 * s, 110 * s, 110 * s), 180, 180)
    uncle = join(stick(ux, y, s, "down"), phones, rect(ux - 55 * s, hy + 1 * s, 16 * s, 34 * s, 6 * s),
                 rect(ux + 55 * s, hy + 1 * s, 16 * s, 34 * s, 6 * s))
    return elder, uncle


# ---------------------------------------------------------------- 动画

def gone_t():
    """重杠铃砸下那一刻（场景 4 第 0 拍）：场景 3 里站着举重的小林从这一刻起换成趴下的样子。"""
    return b.t_of(DROP, 0)


def vanish_fn(path, color=BLACK, width=10, j=None, shake_k=None):
    """描出一条线，直到 drop 那一刻消失；shake_k 起左右发抖。"""
    def fn(c, k, t):
        if t >= gone_t():
            return None
        dx = 5 * math.sin(t * 70) if shake_k is not None and t >= b.t_of(j, shake_k) else 0.0
        part, tip = partial(path, k)
        c.save()
        c.translate(dx, 0)
        ink(c, part, color, width)
        c.restore()
        return (tip[0] + dx, tip[1]) if tip and k < 1 else None
    return fn


def vanish_text_fn(word, x, y, size, color):
    """边写边出的字（同引擎写字的从左到右揭开），到 drop 那一刻消失。"""
    def fn(c, k, t):
        if t >= gone_t():
            return None
        w = K.text_w(word, size, "hand")
        x0 = x - w / 2
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x0 - 20, y - size, x0 + w * k + 4, y + size))
        K.text(c, word, x, y, size, "hand", color)
        c.restore()
        return (x0 + w * k, y) if k < 1 else None
    return fn


def lift_fn(x, floor, s, kind, ys, count=None, thick=False):
    """举杠铃：胳膊连着杠铃杆，杆的高度按 ys(k) 走；count=(总数, x, y, 字号) 时旁边同步数个数。"""
    bar0 = barbell(0, 0, **kind)
    bar0.offset(x, 0)

    def fn(c, k, t):
        by = ys(k)
        ink(c, arms(x, floor, s, by, thick=thick), BLACK, 9)
        ink(c, shifted(bar0, 0, by), BLACK, 9)
        if count:
            n, cx, cy, size = count
            K.text(c, str(int(round(n * clamp01(k)))), cx, cy, size, "hand", RED)
        return None
    return fn


def pump(lo, hi, n):
    """上下举 n 次，最后停在头顶。"""
    return lambda k: lo + (hi - lo) * (1 - math.cos(math.pi * (2 * n - 1) * clamp01(k))) / 2


def raise_(lo, hi):
    return lambda k: lo + (hi - lo) * ease_in_out(clamp01(k))


def note_fly_fn(x0, y0, x1, y1, label):
    """便签“明天再来”：先弹出贴在杠铃上，后半段被风吹到右上角、转着落定。"""
    def fn(c, k, t):
        s = ease_out(clamp01(k / 0.12)) * (1 + 0.12 * math.sin(math.pi * clamp01(k / 0.12)))
        f = ease_in_out(clamp01((k - 0.4) / 0.6))
        x = x0 + (x1 - x0) * f
        y = y0 + (y1 - y0) * f - 120 * math.sin(math.pi * f)
        rot = 28 * f + 10 * math.sin(math.pi * 2 * f)
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(s, s)
        p = note(0, 0)
        c.drawPath(p, K.paint("#FFFFFF"))
        ink(c, p, BLACK, 7)
        K.text(c, label, -10, 4, 50, "hand", RED)
        c.restore()
        return None
    return fn


# ---------------------------------------------------------------- 开局：健身房里的三副杠铃（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

F1, RX = 1250, 800
scene("小林在健身房", "开局 · 健身房", (1000, 850, 0.85), bars=2)
L(join(P((380, F1), (1620, F1)), rack(RX, F1)), 0, 0.9, BLACK, 9, sfx="wood_high")
L(barbell(RX, F1 - 650, **LIGHT), 1, 1.8, BLACK, 9, sfx="pop")
L(barbell(RX, F1 - 430, **MID), 2, 2.8, BLACK, 9, sfx="pop")
L(barbell(RX, F1 - 170, **dict(HEAVY, half=380)), 3, 3.9, BLACK, 10, sfx="wood_low")
L(join(stick(1430, F1, 0.95, "down"), face(1430, F1, 0.95, "smile")), 4, 4.8, BLUE, 9, sfx="wood_high")
T("健身房", 1430, 640, 84, k0=5, k1=5.8, sfx="pop")

F2, X2 = 1250, 2450
HY2 = F2 - 290
scene("天天举最轻的", "开局 · 最轻那副", (2600, 850, 0.85))
L(P((2020, F2), (3180, F2)), 0, 0.9, BLACK, 9, sfx="wood_high")
L(join(body(X2, F2), face(X2, F2, 1.0, "flat")), 1, 1.8, BLUE, 9, sfx="wood_low")
C(lift_fn(X2, F2, 1.0, LIGHT, pump(HY2 + 70, HY2 - 110, 10), count=(20, 2990, 800, 160)), 2, 7.8, sfx="pop")
for k in (3, 4, 5):
    H(k, "shaker", 0.6)
T("一口气", 2990, 580, 64, k0=3, k1=3.8, sfx="pop")
L(arrow((2860, 1050), (2580, 960), 0.2, 34), 6, 6.7, RED, 8, sfx="rim")
T("胳膊没变", 2990, 1120, 62, RED, k0=7, k1=8)

F3, X3 = 2560, 2420
BAR3 = F3 - 180
scene("换最重的试试", "开局 · 最重那副", (2600, 2200, 0.85))
L(P((1990, F3), (3210, F3)), 0, 0.9, BLACK, 9, sfx="wood_high")
C(vanish_fn(barbell(X3, BAR3, **HEAVY), BLACK, 10, J(), 4), 1, 1.9, sfx="wood_low")
C(vanish_fn(join(body(X3, F3), arms(X3, F3, 1.0, BAR3), strain(X3, F3)), BLUE, 9, J(), 4), 2, 2.9, sfx="pop")
T("最重的", 2420, 1820, 80, RED, k0=3, k1=3.8, sfx="pop")
C(vanish_fn(tremble(X3, F3), RED, 7, J(), 4), 4, 4.6, sfx="shaker")
C(vanish_fn(sweat(X3, F3), BLUE, 6, J(), 4), 5, 5.6, sfx="pop")
C(vanish_text_fn("腿在抖", 2980, 1980, 64, RED), 6, 6.8, sfx="rim")
H(7, "shaker", 0.6)

# ---------------------------------------------------------------- drop：重杠铃砸地（场景 4）

BAR4 = F3 - HEAVY["ph"] / 2
LYING = lying(2270, F3 - 45)
HEAVY0 = barbell(X3, 0, **HEAVY)


def crash_fn(c, k, t):
    """杠铃从胸口砸到地上，小林被压趴。"""
    f = clamp01(k)
    ink(c, LYING, BLUE, 9)
    ink(c, shifted(HEAVY0, 0, BAR3 + (BAR4 - BAR3) * f * f), BLACK, 10)
    return None


LX4 = 3130
scene("一下就趴了", "比喻 · 太重了", (2560, 2250, 0.74), shake=[0], flashes=[0])
C(crash_fn, 0, 0.5, sfx="kick")
T("砰！", 2900, 1780, 150, RED, k0=1, k1=1.8, sfx="pop")
L(join(impact(X3 - 360, F3), impact(X3 + 360, F3)), 2, 2.8, BLACK, 7, sfx="wood_low")
L(barbell(LX4, F3 - LIGHT["ph"] / 2, **dict(LIGHT, half=140)), 3, 3.8, BLACK, 9, sfx="wood_high")
L(dust(LX4, F3 - LIGHT["ph"] - 12, 280), 4, 4.8, "#8A8A8A", 6, sfx="shaker")
L(arrow((3190, 2160), (3140, 2370), 0.2, 30), 5, 5.6, BLACK, 7, sfx="wood_high")
T("落满灰", 3130, 2090, 64, k0=6, k1=6.8, sfx="pop")

# ---------------------------------------------------------------- 亮书（场景 5）

scene("有本书讲过", "亮书 · 认知觉醒", (1000, 2200, 0.85))
L(book(750, 2250, 440, 300), 0, 0.9, BLACK, 9, sfx="wood_low")
T("《认知觉醒》", 750, 1970, 72, GREEN, k0=1, k1=2.5, sfx="pop")
T("周岭", 750, 2520, 56, k0=3, k1=3.8, sfx="pop")
L(rudder(1400, 2180, 130), 4, 4.9, GREEN, 8, sfx="wood_high")
T("06", 1400, 2470, 80, RED, k0=5, k1=5.8, sfx="ding")
T("第五章 学习力", 1000, 1760, 56, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 书中观点：三副杠铃三个区（场景 6，封面镜头）

F6 = 3900
scene("三副杠铃三个区", "书中观点 · 三个区", (1800, 3720, 0.66))
L(join(P((1080, F6), (2520, F6)), barbell(1280, F6 - 40, half=180, ph=80, pw=24, n=1),
       dust(1280, F6 - 92, 300)), 0, 0.9, BLACK, 9, sfx="wood_high")
L(barbell(2320, F6 - 150, half=190, ph=300, pw=44, n=3),
  1, 1.9, BLACK, 10, sfx="wood_low")
L(join(body(1800, F6, 0.9), strain(1800, F6, 0.9), arms(1800, F6, 0.9, F6 - 261 - 100, 100),
       barbell(1800, F6 - 261 - 100, half=220, ph=160, pw=32, n=2)), 2, 2.9, BLUE, 9, sfx="pop")
T("舒适区", 1280, 4030, 76, k0=3, k1=3.8, sfx="pop")
T("拉伸区", 1800, 4030, 76, GREEN, k0=4, k1=4.8, sfx="pop")
T("困难区", 2320, 4030, 76, RED, k0=5, k1=5.8, sfx="pop")
L(oval(1800, 3680, 560, 540), 6, 6.9, GREEN, 9, sfx="ding")
L(underline(1690, 1910, 4085, 8, 30), 7, 7.6, GREEN, 7, sfx="wood_high")

# ---------------------------------------------------------------- 书中观点：太轻、太重（场景 7–8）

F7 = 5300
scene("太轻，没长进", "书中观点 · 舒适区", (1000, 4950, 0.85))
T("舒适区", 1000, 4520, 84, k0=0, k1=0.8, sfx="pop")
L(join(P((420, F7), (1580, F7)), barbell(700, F7 - 45, **LIGHT)), 1, 1.9, BLACK, 9, sfx="wood_high")
L(dust(700, F7 - 102, 380), 2, 2.8, "#8A8A8A", 6, sfx="shaker")
L(stick(1250, F7, 0.95, "down"), 3, 3.8, BLUE, 9, sfx="wood_low")
L(yawn(1250, F7, 0.95), 4, 4.7, BLUE, 7, sfx="pop")
T("天天举，不长肌肉", 1000, 5430, 62, RED, k0=6, k1=8, sfx="rim")

F8, X8 = 5300, 2400
scene("太重，就放弃", "书中观点 · 困难区", (2600, 4950, 0.85))
T("困难区", 2450, 4520, 84, RED, k0=0, k1=0.8, sfx="pop")
L(join(P((2020, F8), (3180, F8)), barbell(X8, F8 - 160, **dict(HEAVY, half=330))), 1, 1.9, BLACK, 10, sfx="wood_high")
L(join(stick(2960, F8, 0.85, "down"), face(2960, F8, 0.85, "sad"), arrow((3030, 5150), (3170, 5150), 0.0, 30)),
  2, 2.9, BLUE, 9, sfx="wood_low")
C(note_fly_fn(X8, 5045, 2990, 4600, "明天再来"), 3, 8, sfx="pop")
L(wind(2060, 4800), 5, 5.8, "#8A8A8A", 7, sfx="shaker")
T("太难，容易放弃", 2600, 5430, 62, k0=6, k1=7.5, sfx="rim")

# ---------------------------------------------------------------- 书中观点：中间那副（场景 9）

F9, X9 = 6650, 2600
HY9 = F9 - 290
scene("咬一下牙刚好", "书中观点 · 拉伸区", (2600, 6300, 0.85))
T("拉伸区", 2600, 5870, 84, GREEN, k0=0, k1=0.8, sfx="pop")
L(join(P((2020, F9), (3180, F9)), body(X9, F9)), 1, 1.9, BLUE, 9, sfx="wood_high")
C(lift_fn(X9, F9, 1.0, MID, raise_(HY9 + 70, HY9 - 110)), 2, 3.5, sfx="wood_low")
L(strain(X9, F9), 4, 4.6, BLUE, 7, sfx="pop")
L(sweat(X9, F9), 5, 5.7, BLUE, 6, sfx="pop")
T("看得懂，得动脑", 2600, 6790, 64, k0=6, k1=7.75, sfx="pop")

# ---------------------------------------------------------------- 换成上班的事：练英语（场景 10）

XB = 640
scene("换成上班的事", "比喻 · 练英语", (1000, 6300, 0.85))
T("练英语", 1000, 5830, 72, k0=0, k1=0.8, sfx="pop")
L(barbell(XB, 6000, half=200, ph=80, pw=24, n=1), 1, 1.8, BLACK, 9, sfx="wood_high")
T("背会的词", 1250, 6020, 60, k0=2, k1=3, sfx="pop")
L(barbell(XB, 6330, half=260, ph=240, pw=44, n=3), 3, 3.9, RED, 9, sfx="wood_low")
T("看原版剧", 1250, 6350, 60, RED, k0=4, k1=5, sfx="pop")
L(barbell(XB, 6660, half=230, ph=150, pw=32, n=2), 5, 5.8, GREEN, 9, sfx="wood_high")
T("带字幕的短片", 1250, 6680, 60, GREEN, k0=6, k1=7.2, sfx="pop")
L(check(1490, 6560, 44), 7.2, 7.8, GREEN, 10)

# ---------------------------------------------------------------- 练的四个要点（场景 11）

PY = 7650
PX = [575, 858, 1142, 1425]
scene("练的四个要点", "书中观点 · 刻意练习", (1000, 7650, 0.85))
L(join(P((430, 7350), (1570, 7350)), rect(450, 7350, 30, 90, 6), rect(1550, 7350, 30, 90, 6)), 0, 0.8, BLACK, 10,
  sfx="wood_high")
for i, (word, col, k) in enumerate((("目标清楚", BLUE, 1), ("专心", BLUE, 2.5), ("有反馈", BLUE, 4), ("拉伸区", GREEN, 5.5))):
    snd = "wood_low" if k == int(k) else None
    L(join(P((PX[i], 7350), (PX[i], PY - 120)), circle(PX[i], PY, 120)), k, k + 0.5, col, 8, sfx=snd)
    T(word, PX[i], PY + 2, 48, col, k0=k + 0.5, k1=k + 0.5 + max(0.8, 0.25 * len(word)))
H(3, "pop")
H(6, "pop")
T("一样不能少", 1000, 7980, 70, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 做法：举顺了再加一片（场景 12）

F12, X12 = 8000, 2600
HY12 = F12 - 290
BAR12 = HY12 - 110
K12 = dict(half=360, ph=170, pw=34, n=2)
scene("举得轻松就加片", "做法 · 一次加一片", (2600, 7650, 0.85))
L(join(P((2020, F12), (3180, F12)), body(X12, F12), face(X12, F12, 1.0, "smile")), 0, 0.9, BLUE, 9, sfx="wood_high")
L(arms(X12, F12, 1.0, BAR12, 100), 1, 1.6, BLUE, 9, sfx="wood_low")
L(barbell(X12, BAR12, **K12), 2, 2.9, BLACK, 9, sfx="wood_high")
T("举顺了", 2600, 7220, 72, BLUE, k0=3, k1=3.8, sfx="pop")
for i in range(3):
    L(added_plates(X12, BAR12, i=i, **K12), 4 + i, 4.6 + i, GREEN, 8, sfx="pop")
T("一次只加一片", 2600, 7380, 64, GREEN, k0=6.6, k1=8)

# ---------------------------------------------------------------- 一个月后（场景 13）：拉远

F13, X13 = 9800, 1300
S13 = 1.1
BAR13 = F13 - 290 * S13 - 110
scene("一个月后", "一个月后 · 拉远", (1800, 9300, 0.6))
T("一个月后", 1300, 8720, 96, k0=0, k1=1, sfx="pop")
L(join(P((930, F13), (1680, F13)), body(X13, F13, S13), face(X13, F13, S13, "smile")), 1, 1.9, BLUE, 9, sfx="wood_high")
L(arms(X13, F13, S13, BAR13, 100, thick=True), 2, 2.9, BLUE, 9, sfx="wood_low")
L(barbell(X13, BAR13, half=330, ph=200, pw=36, n=4), 3, 3.9, BLACK, 9, sfx="wood_high")
L(join(circle(2250, 9150, 360), P((2170, 9510), (2170, 9580), (1980, 9640)), P((2330, 9510), (2330, 9580), (2520, 9640))),
  4, 4.9, BLACK, 9, sfx="wood_low")
ELDER, UNCLE = brothers(2030, 9440)
L(join(ELDER, UNCLE), 5, 5.6, BLACK, 7, sfx="pop")
L(stick(2385, 9440, 0.36, "hold"), 5.6, 5.95, BLUE, 7)
L(rudder(2480, 9300, 58), 6, 6.8, GREEN, 6, sfx="wood_high")
L(grips(2480, 9300, 58, range(5)), 7, 7.4, GREEN, 5, sfx="ding")
L(grips(2480, 9300, 58, [5]), 7.4, 7.8, RED, 7)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 5900, 0.11)
COMMENT = (1800, 10950, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
L(join(rect(1800, 10900, 1250, 480, 40), P((1500, 11140), (1440, 11230), (1600, 11140))), 5, 5.9, BLACK, 9,
  sfx="wood_high")
T("你现在在练哪副杠铃？", 1800, 10830, 66, RED, k0=6, k1=8.5, sfx="pop")
T("下一讲：打卡一百天，怎么没变化？", 1800, 11010, 50, k0=9, k1=13, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "edge", "舒适区边缘", "天天在练，怎么还在原地？", ACC, b.shots,
                 [f"{BOOK}第五章 学习力——学习不是一味地努力：第一节 匹配，舒适区边缘；刻意练习的四个要点（转述）"],
                 "天天在练|怎么还在【原地】", SQUARE_SHOT,
                 ["书中观点均为转述，不是逐字引文：舒适区里练不出东西，困难区里容易受挫放弃，成长最快在两者之间的拉伸区"
                  "（舒适区边缘）；练习要找“大致看得懂、要动脑筋”的难度；刻意练习要目标明确、极度专注、有效反馈、在拉伸区练。"
                  "见第五章 学习力（第一节 匹配）。",
                  "三副杠铃对应三个区是对书中观点的通俗比喻，书中没有这个例子；小林练杠铃、一口气二十个、一个月后胳膊粗了一圈"
                  "均为示意，数字不是数据。",
                  "练英语的三档（背会的词 / 看原版剧 / 看带字幕的短片）、举顺了一次只加一片，均为据书中思路整理的做法示意。",
                  "脑内三兄弟（本能脑、情绪脑、理智脑宝宝）与船舵握痕为系列视觉角色，据第一章“三重大脑”与第三章“思维舵手”的比喻。"],
                 tags="#刻意练习 #学习方法")
    return b.attach(ep)
