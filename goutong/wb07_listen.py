"""07 倾听（白板手绘版）：朋友吐槽，你接的哪句？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
形式：E 自测清单。朋友坐在路边说“我今天被裁了”→ 屏上出一张四个空格的清单（快去改简历吧 / 我也被裁过 /
塞翁失马嘛 / 赔了几个月？），请观众对照自己平时会怎么接 → drop：清单勾满，红印章“推远了”砸下，朋友往后退一步
（书中观点：急着给建议、安慰、讲自己，就没在听）→ 亮书，四格卡点亮“感受”“需要”，小泡长出耳朵 →
逐条拆开四种接法（简历飞过去盖住朋友的话 / 我的泡泡越变越大挤掉他的 / 一块黑板挡在中间 / 问号像雨点落下）→
解读：手比耳朵快 → 做法：先陪着坐下，听他的感受和需要；说出听到的，小泡的刺一根根缩回去，朋友点头；
问一句还有没有想说的，朋友的小泡又冒出一串点点 → 评论区互动。
书中观点为转述（马歇尔·卢森堡《非暴力沟通》第七章 用全身心倾听；清单用词按英文版转述，中译用词需核实）；
被裁员的朋友、清单项与改写都是示意，据书中思路整理；清单不设分数。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, doc, face, join, rect,
                               stick)

from .common import BOOK, episode

ACC = "#6E8B2F"                 # 本讲主色：橄榄绿（倾听，系列内与其他讲区分）
SQUARE_SHOT = 3                 # 场景 4：勾满的清单 + 红印章，朋友往后退一步

b = Board(size=(3600, 8900))


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


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 时间与动画工具（渲染时才求值，此时 ep 已挂上）

def tb(j, k):
    return b.t_of(j, k)


def ramp(T_, j, k, dur=0.4):
    t0, t1 = tb(j, k), tb(j, k + dur)
    return clamp01((T_ - t0) / max(1e-3, t1 - t0))


def keyed(T_, start, keys):
    """按关键帧缓动：keys = [(镜头, 拍, 目标值, 时长拍)]，依次生效。"""
    v = start
    for j, k, val, dur in keys:
        f = ramp(T_, j, k, dur)
        if f <= 0:
            break
        v = v + (val - v) * ease_in_out(f)
    return v


def stroke(c, path, color, width):
    c.drawPath(path, wb.marker(color, width))
    c.drawPath(path, K.paint(color, 0.22, width * 0.45, blur=1.2))


def reveal_text(c, s, x, y, size, color, f):
    """像引擎写字一样从左到右显现；返回笔尖。"""
    if f <= 0:
        return None
    w = K.text_w(s, size, "hand")
    x0 = x - w / 2
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0 - 20, y - size, x0 + w * f + 4, y + size))
    K.text(c, s, x, y, size, "hand", color)
    c.restore()
    return (x0 + w * f, y + size * 0.25 * math.sin(f * 40)) if f < 1 else None


def _xf(pt, ax, ay, sc, dx, dy=0.0):
    if pt is None:
        return None
    return ax + (pt[0] - ax) * sc + dx, ay + (pt[1] - ay) * sc + dy


# ---------------------------------------------------------------- 本讲画法

def sit_body(x, y, s=1.0) -> skia.Path:
    """正面坐着的小人（不含头）：(x, y) 为臀部中点，脚落在 y + 170·s。"""
    hy = y - 235 * s
    return join(P((x, hy + 45 * s), (x, y)), P((x - 38 * s, y), (x + 38 * s, y)),
                P((x - 38 * s, y), (x - 82 * s, y + 50 * s), (x - 62 * s, y + 170 * s), (x - 92 * s, y + 170 * s)),
                P((x + 38 * s, y), (x + 82 * s, y + 50 * s), (x + 62 * s, y + 170 * s), (x + 92 * s, y + 170 * s)),
                P((x - 76 * s, y + 44 * s), (x - 34 * s, hy + 110 * s), (x, hy + 85 * s), (x + 34 * s, hy + 110 * s),
                  (x + 76 * s, y + 44 * s)))


def sit(x, y, s=1.0) -> skia.Path:
    return join(circle(x, y - 235 * s, 45 * s), sit_body(x, y, s))


def sit_face(x, y, s=1.0, mood="sad") -> skia.Path:
    return face(x, y + 55 * s, s, mood)


def curb(x0, x1, y, ground) -> skia.Path:
    """路边台阶：台面 + 前脸 + 地面线。"""
    return join(rect((x0 + x1) / 2, y + 35, x1 - x0, 70, 8), P((x0 - 40, ground), (x1 + 60, ground)))


def carton(x, y, w=200, h=170) -> skia.Path:
    """纸箱：(x, y) 为箱底中点，带两片翻开的盖子和一盆小绿植。"""
    top = y - h
    leaf = skia.Path()
    leaf.moveTo(x - 20, top - 50)
    leaf.quadTo(x - 70, top - 80, x - 60, top - 30)
    leaf.quadTo(x - 40, top - 40, x - 20, top - 50)
    return join(rect(x, y - h / 2, w, h, 6), P((x - w / 2, top), (x - w / 2 - 40, top - 40)),
                P((x + w / 2, top), (x + w / 2 + 40, top - 40)), P((x - 20, top), (x - 20, top - 70)), leaf)


def heart(x, y, r=50) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def eye_icon(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 50 * s, y)
    p.quadTo(x, y - 45 * s, x + 50 * s, y)
    p.quadTo(x, y + 45 * s, x - 50 * s, y)
    return join(p, circle(x, y, 14 * s))


def battery(x, y, s=1.0, bars=1) -> skia.Path:
    parts = [rect(x, y, 96 * s, 52 * s, 8 * s), rect(x + 55 * s, y, 12 * s, 22 * s, 3 * s)]
    for i in range(bars):
        xx = x - 32 * s + i * 22 * s
        parts.append(P((xx, y - 14 * s), (xx, y + 14 * s)))
    return join(*parts)


def palm(x, y, s=1.0) -> skia.Path:
    """张开的手：(x, y) 为手心中点。"""
    parts = [rect(x, y + 20 * s, 72 * s, 74 * s, 20 * s)]
    for i in range(4):
        xx = x - 27 * s + 18 * i * s
        parts.append(P((xx, y - 17 * s), (xx, y - 62 * s + (abs(i - 1.5) * 8) * s)))
    parts.append(P((x - 36 * s, y + 25 * s), (x - 66 * s, y - 8 * s)))
    return join(*parts)


def ear(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - 50 * s, y - 75 * s, 100 * s, 120 * s), 150, 250)
    p.quadTo(x + 30 * s, y + 70 * s, x + 2 * s, y + 80 * s)
    q = skia.Path()
    q.addArc(skia.Rect.MakeXYWH(x - 22 * s, y - 42 * s, 44 * s, 48 * s), 170, 220)
    return join(p, q)


CELL = 140


def fourcard(x, y) -> skia.Path:
    """四格卡：眼睛（观察）、心（感受）、电池（需要）、手（请求）。(x, y) 为卡片中心。"""
    w, h = CELL * 4, 190
    parts = [rect(x, y, w, h, 14)]
    for i in (1, 2, 3):
        xx = x - w / 2 + CELL * i
        parts.append(P((xx, y - h / 2), (xx, y + h / 2)))
    cx = [x - w / 2 + CELL * (i + 0.5) for i in range(4)]
    parts += [eye_icon(cx[0], y - 30, 0.8), heart(cx[1], y - 30, 34), battery(cx[2], y - 30, 0.8),
              palm(cx[3], y - 34, 0.75)]
    return join(*parts)


def fourcard_labels(x, y, j, k_on):
    w = CELL * 4

    def fn(c, k, T_):
        a = ramp(T_, j, k_on, 0.5)
        for i, s in enumerate(("观察", "感受", "需要", "请求")):
            K.text(c, s, x - w / 2 + CELL * (i + 0.5), y + 55, 46, "hand", BLACK, alpha=a)
        return None

    return fn


def fill_fn(rects, color, alpha=0.25):
    def fn(c, k, T_):
        for (x, y, w, h) in rects:
            c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w * k, h), K.paint(color, alpha))
        return None

    return fn


def pao_path(x, y, w, h, tip) -> skia.Path:
    """小泡的轮廓：圆角气泡 + 指向说话人的尾巴。"""
    p = rect(x, y, w, h, min(60, h / 2 - 10))
    tx, ty = tip
    bx = min(max(tx, x - w / 2 + 70), x + w / 2 - 110)
    p.moveTo(bx - 28, y + h / 2)
    p.lineTo(tx, ty)
    p.lineTo(bx + 28, y + h / 2)
    return p


def spike_list(x, y, w, h, tip, n=16):
    """气泡轮廓上的等距刺：[(基点, 切向, 外法向)]，避开尾巴。"""
    body = rect(x, y, w, h, min(60, h / 2 - 10))
    pm = skia.PathMeasure(body, False)
    total = pm.getLength()
    bx = min(max(tip[0], x - w / 2 + 70), x + w / 2 - 110)
    out = []
    for i in range(n):
        pos, tan = pm.getPosTan(total * (i + 0.5) / n)
        px, py, tx, ty = pos.x(), pos.y(), tan.x(), tan.y()
        if py > y + h / 2 - 8 and abs(px - bx) < 80:
            continue
        nx, ny = ty, -tx
        if (px + nx - x) * (px - x) / (w * w) + (py + ny - y) * (py - y) / (h * h) < \
                (px - x) ** 2 / (w * w) + (py - y) ** 2 / (h * h):
            nx, ny = -nx, -ny
        out.append((px, py, tx, ty, nx, ny))
    return out


def pao_face(c, fx, fy, mood, color, s=1.0):
    K.dot(c, fx - 20 * s, fy - 14 * s, 7 * s, color)
    K.dot(c, fx + 20 * s, fy - 14 * s, 7 * s, color)
    m = skia.Path()
    if mood == "smile":
        m.addArc(skia.Rect.MakeXYWH(fx - 22 * s, fy - 8 * s, 44 * s, 30 * s), 20, 140)
    else:
        m.addArc(skia.Rect.MakeXYWH(fx - 20 * s, fy + 8 * s, 40 * s, 26 * s), 200, 140)
    c.drawPath(m, wb.marker(color, 6 * s))


def pao(j, k, x, y, w, h, tip, color=BLACK, lines=(), spikes=(), scale=(), anchor=None, offset=(), mood=None,
        face_at=None, face_s=1.0, dots=(), dur=0.6, sfx=None):
    """系列角色“小泡”：先描轮廓，再写字；刺（spikes 关键帧，0–1）长出时嘴往下撇，缩回时嘴角上扬。
    lines = [(字, x, y, 字号, 颜色, 镜头, 起拍, 止拍)]；scale / offset 为关键帧（见 keyed）。"""
    path = pao_path(x, y, w, h, tip)
    sp_list = spike_list(x, y, w, h, tip)
    n = len(sp_list)
    order = [(i * 7) % n for i in range(n)]
    ax, ay = anchor or (x, y)
    fx, fy = face_at or (x + w / 2 - 75, y)

    def fn(c, kk, T_):
        f = ramp(T_, j, k, dur)
        sc = keyed(T_, 1.0, scale)
        sp = keyed(T_, 0.0, spikes)
        dx = keyed(T_, 0.0, offset)
        c.save()
        c.translate(dx, 0)
        c.translate(ax, ay)
        c.scale(sc, sc)
        c.translate(-ax, -ay)
        if sp > 0.001:
            for i, (px, py, tx, ty, nx, ny) in enumerate(sp_list):
                g = clamp01(sp * n - order[i])
                if g <= 0:
                    continue
                ln = 50 * g
                tri = P((px - tx * 17, py - ty * 17), (px + nx * ln, py + ny * ln), (px + tx * 17, py + ty * 17),
                        close=True)
                c.drawPath(tri, K.paint(RED, 0.9))
                c.drawPath(tri, wb.marker(RED, 5))
        part, tip_ = partial_path(path, f)
        stroke(c, part, color, 8)
        if f >= 1:
            md = mood or ("sad" if sp > 0.35 else "smile")
            pao_face(c, fx, fy, md, color, face_s)
            for jj, kb in dots:
                g = ramp(T_, jj, kb, 0.25)
                if g > 0:
                    i = dots.index((jj, kb))
                    K.dot(c, x - w / 2 + 90 + i * 70, y, 17 * ease_out(g), color)
        for (s, lx, ly, size, col, jj, k0, k1) in lines:
            g = clamp01((T_ - tb(jj, k0)) / max(1e-3, tb(jj, k1) - tb(jj, k0)))
            t = reveal_text(c, s, lx, ly, size, col, g)
            if t:
                tip_ = t
        c.restore()
        return _xf(tip_, ax, ay, sc, dx) if f < 1 or tip_ else None

    b.custom(j, k, k + dur, fn, sfx=sfx)


def partial_path(path, f):
    if f <= 0:
        return skia.Path(), None
    return wb.partial(path, f)


def person(j, k, x, y, s=1.0, mood0="sad", moods=(), offset=(), nods=(), sfx=None):
    """会动的坐姿小人：描出后可整体平移（offset）、换表情（moods）、点头（nods）。"""
    head = circle(x, y - 235 * s, 45 * s)
    body = sit_body(x, y, s)

    def fn(c, kk, T_):
        f = ramp(T_, j, k, 0.9)
        dx = keyed(T_, 0.0, offset)
        mood = mood0
        for jj, kb, m in moods:
            if T_ >= tb(jj, kb):
                mood = m
        dy = 0.0
        for jj, kb in nods:
            t0, t1 = tb(jj, kb), tb(jj, kb + 1.5)
            if t0 <= T_ < t1:
                dy = 20 * abs(math.sin(2 * math.pi * (T_ - t0) / (t1 - t0)))
        c.save()
        c.translate(dx, 0)
        tip = None
        c.save()
        c.translate(0, dy)
        hp, t = partial_path(head, clamp01(f * 3))
        stroke(c, hp, BLACK, 10)
        if f >= 1:
            stroke(c, sit_face(x, y, s, mood), BLACK, 10)
        c.restore()
        tip = t or tip
        bp, t = partial_path(body, clamp01(f * 1.5 - 0.5))
        stroke(c, bp, BLACK, 10)
        tip = t or tip
        c.restore()
        return (tip[0] + dx, tip[1]) if tip and f < 1 else None

    b.custom(j, k, k + 0.9, fn, sfx=sfx)


# ---------------------------------------------------------------- 开局：路边台阶（场景 1）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

FR = (760, 1150)                # 朋友坐的位置（臀部）
FB = (1150, 700, 560, 200)      # 朋友的小泡
SHIFT = [(3, 4, -130, 0.8)]     # drop 场景第 4 拍：朋友往后退一步
ROWS = [850, 1020, 1190, 1360]  # 清单四行
BOX_X = 1800

scene("我今天被裁了", "开局 · 路边", (950, 1050, 0.85), bars=2)
L(curb(420, 1180, 1150, 1325), 0, 0.9, BLACK, 9, sfx="wood_low")
person(0, 1, *FR, 1.0, "sad", offset=SHIFT, sfx="wood_high")
L(carton(1340, 1325), 2, 2.8, BLACK, 9, sfx="pop")
pao(0, 3, *FB, tip=(800, 860), lines=[("我今天被裁了", 1105, 700, 60, BLACK, 0, 4, 5.5)], offset=SHIFT, mood="sad",
    sfx="pop")
H(4, "pop")

# ---------------------------------------------------------------- 自测清单（场景 2–3）

VL = (2100, 1060, 0.85)
scene("你会怎么接", "自测清单", VL)
L(join(rect(2100, 1070, 820, 960, 16), rect(2100, 590, 170, 44, 10)), 0, 0.9, BLACK, 9, sfx="wood_low")
T("你会怎么接？", 2100, 700, 66, k0=1, k1=2.5, sfx="pop")
for n, yy in enumerate(ROWS):
    L(rect(BOX_X, yy, 76, 76, 10), 3 + n, 3.7 + n, BLACK, 8, sfx="wood_high")

OPTS = ["快去改简历吧", "我也被裁过", "塞翁失马嘛", "赔了几个月？"]
scene("对着勾一勾", "自测清单 · 你平时会说", VL)
for n, (s, yy) in enumerate(zip(OPTS, ROWS)):
    T(s, 2170, yy, 58, k0=2 * n, k1=2 * n + 1.5, sfx="pop")


def hover_fn(c, k, T_):
    """笔悬在格子边上，一行一行犹豫着往下挪（不出笔画）。"""
    row = min(3, int(k * 4))
    return BOX_X + 30, ROWS[row] - 14 + 14 * math.sin(T_ * 9)


C(8, 11.8, hover_fn)
H(9, "shaker", 0.4)
H(11, "shaker", 0.4)

# ---------------------------------------------------------------- drop：清单勾满，印章砸下（场景 4）

scene("这些话推远了", "书中观点 · 第七章", (1500, 1100, 0.52), shake=[0, (2, 10.0)], flashes=[0])


def ticks_fn(c, k, T_):
    for n, yy in enumerate(ROWS):
        g = ramp(T_, 3, 0.08 * n, 0.2)
        if g > 0:
            part, _ = wb.partial(check(BOX_X, yy - 4, 44), g)
            stroke(c, part, RED, 13)
    return None


C(0, 0.5, ticks_fn, sfx="kick")


def stamp_fn(c, k, T_):
    g = ease_out(ramp(T_, 3, 2, 0.3))
    if g <= 0:
        return None
    with K.at(c, 2100, 1110, -12, 2.2 - 1.2 * g):
        a = 0.9 * g
        c.drawRoundRect(skia.Rect.MakeXYWH(-250, -100, 500, 200), 26, 26, K.paint(RED, a, 12))
        c.drawRoundRect(skia.Rect.MakeXYWH(-226, -78, 452, 156), 18, 18, K.paint(RED, a * 0.6, 5))
        K.text(c, "推远了", 0, 0, 120, "hand", RED, alpha=a)
    return None


C(2, 2.4, stamp_fn, sfx="tom")
H(4, "shaker", 0.7)
L(arrow((800, 1430), (520, 1430), 0.05, 40), 5, 5.8, RED, 10, sfx="wood_high")
T("急着接话，就没在听", 1500, 1720, 82, RED, k0=6, k1=8, sfx="pop")

# ---------------------------------------------------------------- 亮书（场景 5）

scene("有本书讲过", "书中观点 · 亮书", (950, 2750, 0.85))
L(book(640, 2700, 400, 270), 0, 0.9, BLACK, 10, sfx="wood_low")
T("《非暴力沟通》", 640, 2440, 62, GREEN, k0=1, k1=2.75, sfx="pop")
CARD = (1230, 2500)
L(fourcard(*CARD), 3, 3.9, BLACK, 7, sfx="wood_high")
C(3.9, 4.0, fourcard_labels(*CARD, J(), 3.9))
C(4, 4.6, fill_fn([(CARD[0] - CELL / 2, CARD[1], CELL - 8, 182), (CARD[0] + CELL / 2, CARD[1], CELL - 8, 182)], BLUE),
  sfx="ding")
T("卢森堡 著", 640, 2965, 50, k0=5, k1=6.25, sfx="pop")
pao(4, 6, 1230, 2880, 330, 190, tip=(1180, 3040), color=BLUE, mood="smile", face_at=(1230, 2880), face_s=1.5,
    dur=0.8, sfx="wood_high")
_le = skia.Path()
_le.addArc(skia.Rect.MakeXYWH(1015, 2830, 80, 110), 90, 180)
_li = skia.Path()
_li.addArc(skia.Rect.MakeXYWH(1040, 2860, 40, 55), 90, 180)
_re = skia.Path()
_re.addArc(skia.Rect.MakeXYWH(1365, 2830, 80, 110), -90, 180)
_ri = skia.Path()
_ri.addArc(skia.Rect.MakeXYWH(1380, 2860, 40, 55), -90, 180)
L(join(_le, _li, _re, _ri), 7, 7.8, BLUE, 9, sfx="pop")

# ---------------------------------------------------------------- 逐条拆开（场景 6–9）：朋友坐左边，你站右边


def duo(cx, cy, me_mood="flat", k_friend=0, k_me=None):
    """台阶 + 坐着的朋友（第 k_friend 拍）+ 站着的你（第 k_me 拍）。"""
    L(join(curb(cx - 560, cx - 80, cy + 170, cy + 320), sit(cx - 320, cy + 170, 0.85)), k_friend, k_friend + 0.9,
      BLACK, 9, sfx="wood_low")
    L(sit_face(cx - 320, cy + 170, 0.85, "sad"), k_friend + 0.9, k_friend + 1.0, BLACK, 8)
    if k_me is not None:
        L(stick(cx + 330, cy + 320, 0.85), k_me, k_me + 0.8, BLUE, 9, sfx="wood_high")
        L(face(cx + 330, cy + 320, 0.85, me_mood), k_me + 0.8, k_me + 1.0, BLUE, 8)


def my_pao(j, k, cx, cy, lines, w=560, h=190, spike_k=None, **kw):
    x, y = cx + 200, cy - 330
    tx = x - 45
    ls = []
    for n, (s, size, k0) in enumerate(lines):
        ly = y if len(lines) == 1 else y - 45 + 90 * n
        ls.append((s, tx, ly, size, RED, j, k0, k0 + max(0.8, 0.25 * len(s))))
    sp = [(j, spike_k, 1.0, 0.4)] if spike_k is not None else []
    pao(j, k, x, y, w, h, tip=(cx + 330, cy + 10), lines=ls, spikes=sp, dur=0.5, sfx="pop", **kw)
    if spike_k is not None:
        b.hit(j, spike_k, "rim", 0.8)


def friend_pao(j, k, cx, cy, text, k0, **kw):
    x, y = cx - 330, cy - 260
    pao(j, k, x, y, 360, 150, tip=(cx - 320, cy - 90), lines=[(text, x - 40, y, 48, BLACK, j, k0, k0 + 1.0)],
        mood="sad", dur=0.5, sfx="pop", **kw)


C1 = (950, 4000)
scene("给建议", "清单第一项 · 给建议", (C1[0], C1[1], 0.85))
duo(*C1, k_friend=0, k_me=3)
friend_pao(J(), 1, *C1, "我心里……", 1.5)
my_pao(J(), 4, *C1, [("快去改简历吧！", 52, 4.5)], spike_k=6)


def resume_fn(cx, cy, j, k):
    x0, y0, x1, y1 = cx + 200, cy - 330, cx - 330, cy - 250

    def fn(c, kk, T_):
        g = ease_out(ramp(T_, j, k, 0.7))
        if g <= 0:
            return None
        x, y = lerp(x0, x1, g), lerp(y0, y1, g) - 220 * 4 * g * (1 - g)
        with K.at(c, x, y, lerp(-30, -8, g), lerp(0.4, 1.0, g)):
            pth = doc(0, 0, 270, 310, 4)
            c.drawPath(pth, K.paint("#FFFFFF"))
            stroke(c, pth, BLACK, 7)
            K.text(c, "简历", -20, -110, 48, "hand", BLACK)
        return None

    return fn


C(7, 7.7, resume_fn(*C1, J(), 7), sfx="kick")

C2 = (2650, 4000)
scene("讲自己", "清单第二项 · 讲自己", (C2[0], C2[1], 0.85))
duo(*C2, me_mood="smile", k_friend=0, k_me=3)
GROW = [(J(), 7, 1.3, 1.0)]
friend_pao(J(), 1, *C2, "我好慌", 1.5, scale=[(J(), 7, 0.5, 1.0)], anchor=(C2[0] - 330, C2[1] - 185))
my_pao(J(), 4, *C2, [("我也被裁过，更惨！", 46, 4.5)], w=600, spike_k=6, scale=GROW,
       anchor=(C2[0] + 330, C2[1] - 235))
H(7, "tom")

C3 = (2650, 5300)
scene("讲道理", "清单第三项 · 讲道理", (C3[0], C3[1], 0.85), shake=[(6, 10.0)])
duo(*C3, k_friend=0, k_me=1)
my_pao(J(), 2, *C3, [("塞翁失马，焉知非福", 46, 2.5)], w=600, spike_k=5)


def blackboard_fn(cx, cy, j, k):
    def fn(c, kk, T_):
        g = ramp(T_, j, k, 0.4)
        if g <= 0:
            return None
        fall = g * g
        bounce = 18 * math.sin(math.pi * clamp01((g - 0.8) / 0.2)) if g > 0.8 else 0
        y = lerp(cy - 800, cy + 60, min(1.0, fall)) - bounce
        x = cx + 10
        for sx in (-110, 110):
            c.drawPath(P((x + sx, y + 170), (x + sx * 1.2, y + 260)), wb.marker("#6B4B2A", 10))
        K.rr(c, x, y, 300, 340, 14, "#2E4A3E")
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 150, y - 170, 300, 340), 14, 14, K.paint("#6B4B2A", 1, 12))
        f2 = clamp01((T_ - tb(j, k + 1)) / max(1e-3, tb(j, k + 1.8) - tb(j, k + 1)))
        reveal_text(c, "想开点", x, y - 20, 64, "#F4F1E8", f2)
        if f2 > 0:
            c.drawPath(P((x - 90, y + 50), (x - 90 + 180 * f2, y + 50)), K.paint("#F4F1E8", 1, 6))
        return None

    return fn


C(6, 6.4, blackboard_fn(*C3, J(), 6), sfx="kick")
H(7, "pop")

C4 = (950, 5300)
scene("追问细节", "清单第四项 · 追问", (C4[0], C4[1], 0.85))
duo(*C4, k_friend=0, k_me=1)
my_pao(J(), 2, *C4, [("赔偿给了几个月？", 50, 2.5), ("签字了没？", 50, 5)], h=240, spike_k=4)
H(5, "pop")

QS = [(-470, -200, 100, -10), (-200, -210, 90, 8), (-340, -330, 110, 4), (-500, -20, 80, 12), (-150, -60, 80, -6),
      (-260, -470, 85, -12)]


def rain_fn(cx, cy, j, k):
    def fn(c, kk, T_):
        for i, (dx, dy, size, rot) in enumerate(QS):
            g = ramp(T_, j, k + 0.15 * i, 0.35)
            if g <= 0:
                continue
            y = lerp(cy - 700, cy + dy, g * g)
            with K.at(c, cx + dx, y, rot):
                K.text(c, "？", 0, 0, size, "hand", RED)
        return None

    return fn


C(7, 8.0, rain_fn(*C4, J(), 7), sfx="shaker")

# ---------------------------------------------------------------- 解读：手比耳朵快（场景 10）

D = (950, 6600)
LANE1, LANE2 = 6420, 6760
scene("手比耳朵快", "解读 · 急着做点什么", (D[0], D[1], 0.85))
L(join(P((450, LANE1), (1430, LANE1)), P((450, LANE2), (1430, LANE2)), P((470, 6230), (470, 6790)),
       P((1430, 6220), (1430, 6800)), P((1430, 6220), (1530, 6258), (1430, 6296))), 0, 0.9, BLACK, 8,
  sfx="wood_low")


def racer_fn(path, x0, x1, y, color, j, k_draw, k_go, dur, width=9):
    def fn(c, kk, T_):
        f = ramp(T_, j, k_draw, 0.8)
        g = ease_in_out(ramp(T_, j, k_go, dur))
        dx = (x1 - x0) * g
        c.save()
        c.translate(dx, 0)
        part, tip = partial_path(path, f)
        stroke(c, part, color, width)
        c.restore()
        if g > 0.05 and x1 - x0 > 300:
            for i, oy in enumerate((-50, 0, 50)):
                a = 0.8 * (1 - 0.5 * g)
                c.drawPath(P((x0 + dx - 120 - 30 * i, y + oy), (x0 + dx - 260 - 30 * i, y + oy)),
                           K.paint(color, a, 7))
        return (tip[0] + dx, tip[1]) if tip and f < 1 else None

    return fn


C(1, 1.8, racer_fn(palm(560, 6310, 1.6), 560, 1290, 6310, RED, J(), 1, 3, 0.7, 10), sfx="wood_high")
C(2, 2.8, racer_fn(ear(560, 6650, 1.3), 560, 650, 6650, BLUE, J(), 2, 3, 2.5), sfx="pop")
H(3, "kick")
T("急着做点什么", 950, 6510, 60, RED, k0=5, k1=6.5, sfx="pop")
T("没顾上听", 1000, 6855, 60, BLUE, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 做法：坐下来，听，说出来，再问一句（场景 11–13）

E = (2650, 6700, 0.75)
FR2, ME2 = (2480, 7000), (2840, 7000)
scene("先陪着坐会儿", "书中观点 · 先听", E)
L(curb(2250, 3150, 7000, 7180), 0, 0.9, BLACK, 9, sfx="wood_low")
J11 = J()
person(J11, 1, *FR2, 1.0, "sad", moods=[(J11 + 1, 7, "smile")], nods=[(J11 + 1, 7)], sfx="wood_high")
L(sit(*ME2, 1.0), 2, 2.8, BLUE, 10, sfx="pop")
L(sit_face(*ME2, 1.0, "flat"), 2.8, 3.0, BLUE, 9)
L(heart(2120, 6560, 48), 4, 4.5, RED, 9, sfx="pop")
T("他的感受", 2120, 6670, 54, RED, k0=4.5, k1=5.5)
L(battery(2120, 6800, 1.1, 1), 6, 6.5, GREEN, 9, sfx="wood_high")
T("他的需要", 2120, 6910, 54, GREEN, k0=6.5, k1=7.5)

MYB = (2860, 6330, 820, 260)
scene("说出你听到的", "做法 · 据书中思路", E)
pao(J(), 0, *MYB, tip=(2840, 6700), color=BLUE,
    lines=[("是不是又慌又委屈？", 2820, 6280, 54, BLUE, J(), 1, 3.25),
           ("想有人知道你干得不差？", 2820, 6380, 54, BLUE, J(), 4, 6.75)],
    spikes=[(J(), 0, 1.0, 0.6), (J(), 2, 0.0, 4.5)], dur=0.8, sfx="wood_high")
H(1, "pop")
H(4, "pop")
H(5, "pop", 0.6)
H(7, "ding")

scene("还有想说的吗", "书中观点 · 问一句", E)
b.erase(J(), 0, 0.8, MYB[0], MYB[1], MYB[2] + 60, MYB[3] + 110)
H(0, "shaker", 0.6)
pao(J(), 1, 2900, 6340, 600, 190, tip=(2840, 6700), color=BLUE,
    lines=[("还有想说的吗？", 2855, 6340, 54, BLUE, J(), 1.6, 3.35)], mood="smile", sfx="pop")
pao(J(), 4, 2230, 6340, 380, 190, tip=(2430, 6690), color=BLACK, mood="smile", face_at=(2350, 6340),
    dots=[(J(), 5), (J(), 6), (J(), 7)], sfx="pop")
H(5, "pop")
H(6, "pop")
H(7, "pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1840, 3500, 0.25)
CV = (1800, 8100, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, CV, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(join(rect(1800, 8150, 1060, 440, 26), circle(1360, 7990, 34), P((1420, 7990), (1600, 7990))), 6, 6.8, BLACK, 8,
  sfx="wood_low")
T("你最常勾的是哪一个？", 1800, 8080, 72, RED, k0=7, k1=9.5, sfx="pop")
T("下一讲：搞砸一件事，骂自己有用吗？", 1800, 8260, 50, k0=10, k1=14, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "listen", "倾听", "朋友吐槽，你接的哪句？", ACC, b.shots,
                 [f"{BOOK}第七章 用全身心倾听（转述）",
                  "中译本：阮胤华译，华夏出版社"],
                 "朋友吐槽|你接的【哪句】", SQUARE_SHOT,
                 ["书中观点均为转述（第七章 用全身心倾听）：倾听时把注意力放在对方的感受和需要上，先别急着给建议、"
                  "安慰、讲自己的经历、讲道理；可以说出自己听到的感受和需要，请对方确认；不确定对方说完没有，可以问一句"
                  "还有没有要说的。妨碍倾听的清单用词按英文版转述，中译用词需核实。上屏均为转述，不是逐字引文。",
                  "被裁员的朋友、自测清单四项（快去改简历吧 / 我也被裁过 / 塞翁失马嘛 / 赔了几个月？）、"
                  "“是不是又慌又委屈？想有人知道你干得不差？”的说法，均为示意，据书中思路整理；清单不设分数、不分等级。",
                  "“手比耳朵快”赛跑图、印章“推远了”、黑板挡在中间等画面，为对书中观点的通俗化示意。",
                  "人物均为火柴人，不指向任何具体公司或个人；卢森堡只写名字，不画肖像。"],
                 tags="#朋友 #情商")
    return b.attach(ep)
