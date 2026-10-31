"""04 四种接法（白板手绘版）：挨了句批评，你会怎么接？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 F 分岔：一句话四条路）：周五下午方案又被打回 → 领导一句“这做的什么东西”像石头飞过来 →
主角站在路口，四个方向空着 → drop：石头砸地裂成十字路口，四个路牌同时弹出 →
亮书（四格卡点亮“电池”）；书中观点（第五章）：听到不中听的话，有四种选择 →
每条路走一屏：怪自己（蹲墙角，半夜睡不着）／怪对方（冒火，第二天甩脸）／看看自己（手按胸口，缺了一格电：
两周的活想被看见）／听听对方（领导头顶一个闹钟和一节缺电的电池：明早上会，要一份能交的）→
拉远看四个结局（失眠／冷战／说出口／对上话）→ 书中观点：他的话是火柴，心里那股火来自自己的需要 →
两步做法（先停一下问自己缺了什么；再问他要什么，带刺的小泡把刺缩回去）→ 评论区互动。
书中观点为转述（马歇尔·卢森堡《非暴力沟通》第五章“感受的根源”，阮胤华译，华夏出版社）；
领导的话、四个结局与两步做法均为示意，据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               doc, face, hands_at, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, lerp

from .common import BOOK, episode

ACC = "#2F8F83"
SQUARE_SHOT = 9                 # 场景 10：十字路口四条路尽头的四个结局（人物 + 四条路）

b = Board(size=(3600, 8700))


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


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


# ---------------------------------------------------------------- 本讲画法

def spiky(x, y, w, h, spike, n=16, tail=-1) -> skia.Path:
    """话泡泡“小泡”的轮廓：圆角气泡 + 尾巴，spike>0 时外圈等距长出三角刺。"""
    base = rect(x, y, w, h, min(60, h / 2))
    out = skia.Path(base)
    if spike > 0.5:
        pm = skia.PathMeasure(base, False)
        total = pm.getLength()
        for i in range(n):
            pos, tan = pm.getPosTan(total * (i + 0.5) / n)
            px, py, tx, ty = pos.x(), pos.y(), tan.x(), tan.y()
            nx, ny = ty, -tx
            out.moveTo(px - tx * 18, py - ty * 18)
            out.lineTo(px + nx * spike, py + ny * spike)
            out.lineTo(px + tx * 18, py + ty * 18)
    out.moveTo(x + tail * w * 0.25, y + h / 2)
    out.lineTo(x + tail * w * 0.38, y + h / 2 + 60)
    out.lineTo(x + tail * w * 0.1, y + h / 2)
    return out


def pao_face(c, x, y, smile, color):
    """小泡的两点眼睛 + 小嘴：smile 0 = 嘴往下撇，1 = 嘴角上扬。"""
    for dx in (-22, 22):
        K.dot(c, x + dx, y - 16, 7, color)
    m = skia.Path()
    d = lerp(-1, 1, smile) * 16
    m.moveTo(x - 22, y + 22 - d * 0.4)
    m.quadTo(x, y + 22 + d, x + 22, y + 22 - d * 0.4)
    c.drawPath(m, K.paint(color, 1, 6))


def pao_fn(x, y, w, h, phase):
    """小泡动画：phase(k) -> (缩放, 刺长, 颜色混合 0 红→1 蓝, 嘴型 0→1)。"""

    def fn(c, k, t):
        s, spike, blue, smile = phase(k)
        if s <= 0.01:
            return None
        col = K.mix(RED, BLUE, blue)
        with K.at(c, x, y, 0, s):
            path = spiky(0, 0, w, h, spike)
            c.drawPath(rect(0, 0, w, h, min(60, h / 2)), K.paint("#FFFFFF"))
            c.drawPath(path, K.paint(col, 1, 8))
            pao_face(c, -w / 2 + 78, 0, smile, col)
        return None

    return fn


def rock(x, y, r, rot=0.0) -> skia.Path:
    pts = []
    for i, rr in enumerate((1.0, 0.82, 1.05, 0.9, 1.0, 0.78, 0.95)):
        a = rot + i / 7 * 2 * math.pi
        pts.append((x + r * rr * math.cos(a), y + r * rr * 0.8 * math.sin(a)))
    return P(*pts, close=True)


def draw_rock(c, x, y, r, rot=0.0, sy=1.0):
    with K.at(c, x, y, 0, 1.0, sy):
        p = rock(0, 0, r, rot)
        c.drawPath(p, K.paint("#9A9AA2"))
        c.drawPath(p, K.paint(BLACK, 1, 8))
        c.drawPath(join(P((-r * 0.35, -r * 0.2), (0, r * 0.05), (r * 0.25, -r * 0.3)),
                        P((r * 0.1, r * 0.3), (r * 0.4, r * 0.15))), K.paint(BLACK, 1, 5))


def stone_fly_fn(p0, p1, r=48, lift=260):
    """石头沿抛物线从 p0 飞到 p1（k=1 时撞上），撞上后留几道红色撞击线。"""

    def fn(c, k, t):
        f = ease_in_out(k) * 0.3 + k * 0.7
        x = lerp(p0[0], p1[0], f)
        y = lerp(p0[1], p1[1], f) - lift * 4 * f * (1 - f)
        if k < 1:
            for i in range(1, 4):
                g = max(0.0, f - i * 0.06)
                tx = lerp(p0[0], p1[0], g)
                ty = lerp(p0[1], p1[1], g) - lift * 4 * g * (1 - g)
                K.seg(c, tx, ty, x, y, BLACK, 4, 0.25)
        draw_rock(c, x, y, r, k * 4)
        if k >= 1:
            for a in (150, 185, 220):
                ar = math.radians(a)
                c.drawPath(P((x + math.cos(ar) * (r + 18), y + math.sin(ar) * (r + 18)),
                             (x + math.cos(ar) * (r + 60), y + math.sin(ar) * (r + 60))), K.paint(RED, 1, 7))
        return None

    return fn


def crouch(x, y, s=1.0) -> skia.Path:
    """蹲在地上抱膝的小人（朝右）：(x, y) 为脚底。"""
    hx, hy = x - 5 * s, y - 210 * s
    neck, hip = (x - 5 * s, y - 168 * s), (x - 50 * s, y - 50 * s)
    knee, foot = (x + 45 * s, y - 115 * s), (x + 50 * s, y)
    return join(circle(hx, hy, 42 * s), P(neck, hip), P(hip, knee, foot), P((x - 50 * s, y - 50 * s), (x - 30 * s, y)),
                P((x - 12 * s, y - 145 * s), (x + 38 * s, y - 100 * s)))


def crouch_face(x, y, s=1.0) -> skia.Path:
    hx, hy = x - 5 * s, y - 210 * s
    p = join(circle(hx + 4 * s, hy - 6 * s, 3 * s), circle(hx + 26 * s, hy - 6 * s, 3 * s))
    p.addArc(skia.Rect.MakeXYWH(hx - 2 * s, hy + 12 * s, 32 * s, 22 * s), 200, 140)
    return p


def akimbo(x, y, s=1.0) -> skia.Path:
    """叉腰小人：(x, y) 为脚底。"""
    hy = y - 290 * s
    sh, hip = hy + 80 * s, y - 150 * s
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)),
                P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)),
                P((x - 22 * s, hip), (x - 75 * s, sh + 40 * s), (x, sh)), P((x, sh), (x + 75 * s, sh + 40 * s), (x + 22 * s, hip)))


def chest(x, y, s=1.0, tie=False) -> skia.Path:
    """一只手按在胸口的小人：(x, y) 为脚底。"""
    hy = y - 290 * s
    sh = hy + 80 * s
    parts = [circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)), P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)),
             P((x - 70 * s, hy + 170 * s), (x, sh)), P((x, sh), (x + 60 * s, sh + 70 * s), (x + 12 * s, sh + 45 * s))]
    if tie:
        parts.append(P((x, hy + 50 * s), (x - 12 * s, hy + 100 * s), (x, hy + 120 * s), (x + 12 * s, hy + 100 * s), close=True))
    return join(*parts)


def away(x, y, s=1.0, d=-1) -> skia.Path:
    """扭头不看人的五官：d=-1 看左，1 看右；嘴往下撇。(x, y) 为脚底。"""
    hy = y - 290 * s
    cx = x + d * 18 * s
    p = join(circle(cx - 11 * s, hy - 8 * s, 3 * s), circle(cx + 11 * s, hy - 8 * s, 3 * s))
    p.addArc(skia.Rect.MakeXYWH(cx - 15 * s, hy + 12 * s, 30 * s, 20 * s), 200, 140)
    return p


def eyes_only(x, y, s=1.0) -> skia.Path:
    hy = y - 290 * s
    return join(circle(x - 15 * s, hy - 8 * s, 3 * s), circle(x + 15 * s, hy - 8 * s, 3 * s))


def calm(x, y, s=1.0) -> skia.Path:
    """闭眼深呼吸的五官。"""
    hy = y - 290 * s
    p = skia.Path()
    for dx in (-16, 16):
        p.addArc(skia.Rect.MakeXYWH(x + (dx - 9) * s, hy - 14 * s, 18 * s, 12 * s), 20, 140)
    p.addArc(skia.Rect.MakeXYWH(x - 14 * s, hy + 6 * s, 28 * s, 18 * s), 20, 140)
    return p


def cloud(x, y, w=320, h=130) -> skia.Path:
    p = skia.Path()
    r = w / 6
    p.moveTo(x - w / 2, y + h / 2)
    p.lineTo(x - w / 2, y)
    for i, (cx, cy) in enumerate(((x - w / 3, y), (x, y - h / 4), (x + w / 3, y))):
        p.arcTo(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), 180, 180, False)
    p.lineTo(x + w / 2, y + h / 2)
    p.close()
    return p


def rain(x, y, w=280, n=5) -> skia.Path:
    return join(*[P((x - w / 2 + i * w / (n - 1) + 10 * (j % 2), y + j * 70), (x - w / 2 + i * w / (n - 1) - 12 + 10 * (j % 2),
                                                                             y + j * 70 + 45))
                  for i in range(n) for j in range(2)])


def moon(x, y, r=60) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def flame(x, y, h=160) -> skia.Path:
    """火苗：(x, y) 为火苗底部。"""
    w = h * 0.42
    f = skia.Path()
    f.moveTo(x, y - h)
    f.quadTo(x + w * 1.4, y - h * 0.35, x + w * 0.6, y)
    f.lineTo(x - w * 0.6, y)
    f.quadTo(x - w * 1.4, y - h * 0.35, x, y - h)
    g = skia.Path()
    g.moveTo(x, y - h * 0.5)
    g.quadTo(x + w * 0.55, y - h * 0.2, x, y - 6)
    g.quadTo(x - w * 0.55, y - h * 0.2, x, y - h * 0.5)
    return join(f, g)


def heart(x, y, r=50) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def eye(x, y, w=110) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.quadTo(x, y - w * 0.55, x + w / 2, y)
    p.quadTo(x, y + w * 0.55, x - w / 2, y)
    return join(p, circle(x, y, w * 0.17))


def battery(x, y, w=240, h=110) -> skia.Path:
    return join(rect(x, y, w, h, 14), rect(x + w / 2 + 12, y, 22, h * 0.4, 5))


def cells(x, y, w, h, n=4):
    """电池里 n 个电量格的中心与大小。"""
    gap = 10
    cw = (w - 24 - gap * (n - 1)) / n
    return [(x - w / 2 + 12 + cw / 2 + i * (cw + gap), y, cw, h - 24) for i in range(n)]


def cells_fn(x, y, w, h, fill, n=4):
    """电量格逐格亮起：fill 为每格颜色（None 不画）。"""

    def fn(c, k, t):
        for i, (cx, cy, cw, ch) in enumerate(cells(x, y, w, h, n)):
            col = fill[i] if i < len(fill) else None
            f = clamp01(k * n - i)
            if col and f > 0:
                K.rr(c, cx, cy, cw, ch, 6, col, 0.85 * f)
        return None

    return fn


def empty_cell(x, y, w, h, i, n=4) -> skia.Path:
    cx, cy, cw, ch = cells(x, y, w, h, n)[i]
    return rect(cx, cy, cw, ch, 6)


def hand_icon(x, y, s=1.0) -> skia.Path:
    """伸出的手（掌心向上）：(x, y) 为掌心。"""
    return join(P((x - 70 * s, y + 10 * s), (x - 20 * s, y + 30 * s), (x + 50 * s, y + 25 * s)),
                P((x - 20 * s, y + 30 * s), (x - 40 * s, y - 5 * s)),
                *[P((x - 10 * s + i * 22 * s, y + 25 * s), (x + 10 * s + i * 22 * s, y - 25 * s)) for i in range(3)],
                P((x - 110 * s, y + 10 * s), (x - 70 * s, y + 10 * s)))


CARD = (2990, 2400, 260, 210)   # 四格卡：中心、单格宽高


def card_path() -> skia.Path:
    x, y, cw, ch = CARD
    parts = [rect(x, y, cw * 4, ch, 20)]
    for i in (1, 2, 3):
        xx = x - cw * 2 + i * cw
        parts.append(P((xx, y - ch / 2), (xx, y + ch / 2)))
    return join(*parts)


def card_cx(i):
    return CARD[0] - CARD[2] * 1.5 + i * CARD[2]


def card_icons() -> skia.Path:
    y = CARD[1] - 35
    return join(eye(card_cx(0), y, 110), heart(card_cx(1), y + 5, 34), battery(card_cx(2) - 8, y, 120, 60),
                hand_icon(card_cx(3) + 20, y, 0.85))


def glow_fn(x, y, w, h, color=GREEN, alpha=0.22):
    def fn(c, k, t):
        K.rr(c, x, y, w, h, 14, color, alpha * k)
        return None

    return fn


# 十字路口
CX, CY = 1800, 3200
RW = 70                          # 路面半宽
ARM = {"N": 2500, "W": 1150, "E": 2450, "S": 3950}


def roads() -> skia.Path:
    return join(P((CX - RW, CY - RW), (CX - RW, ARM["N"])), P((CX + RW, CY - RW), (CX + RW, ARM["N"])),
                P((CX - RW, CY - RW), (ARM["W"], CY - RW)), P((CX - RW, CY + RW), (ARM["W"], CY + RW)),
                P((CX + RW, CY - RW), (ARM["E"], CY - RW)), P((CX + RW, CY + RW), (ARM["E"], CY + RW)),
                P((CX - RW, CY + RW), (CX - RW, ARM["S"])), P((CX + RW, CY + RW), (CX + RW, ARM["S"])))


def zig(x0, y0, x1, y1, n=5, amp=26) -> skia.Path:
    pts = [(x0, y0)]
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln, dx / ln
    for i in range(1, n):
        f = i / n
        a = amp * (1 if i % 2 else -1)
        pts.append((x0 + dx * f + nx * a, y0 + dy * f + ny * a))
    pts.append((x1, y1))
    return P(*pts)


def cracks() -> skia.Path:
    r0, r1 = 100, 235
    return join(zig(CX, CY - r0, CX, CY - r1), zig(CX - r0, CY, CX - r1, CY), zig(CX + r0, CY, CX + r1, CY),
                zig(CX, CY + r0, CX, CY + r1), zig(CX + 70, CY - 70, CX + 150, CY - 140, 3, 16),
                zig(CX - 70, CY + 70, CX - 150, CY + 150, 3, 16))


SIGN_SIZE = 66
SIGNS = [("怪自己", 1470, 3010, "L", RED), ("怪对方", 2100, 2950, "U", RED),
         ("看看自己", 2100, 3390, "R", BLUE), ("听听对方", 2100, 3600, "D", BLUE)]


def _sign_geom(label, x, y, d):
    w = SIGN_SIZE * len(label) + 150
    left, right = x - w / 2, x + w / 2
    if d == "L":
        ar, tx = ((left + 105, y), (left + 30, y)), x + 40
    elif d == "R":
        ar, tx = ((right - 105, y), (right - 30, y)), x - 40
    elif d == "U":
        ar, tx = ((left + 62, y + 32), (left + 62, y - 32)), x + 40
    else:
        ar, tx = ((left + 62, y - 32), (left + 62, y + 32)), x + 40
    return w, ar, tx


def signs_fn(with_text):
    """四个路牌同时弹出（带回弹）；with_text=True 时只弹路牌上的字。"""

    def fn(c, k, t):
        s = 1.12 * math.sin(clamp01(k / 0.7) * math.pi / 2) if k < 0.7 else lerp(1.12, 1.0, (k - 0.7) / 0.3)
        for label, x, y, d, col in SIGNS:
            w, ar, tx = _sign_geom(label, x, y, d)
            with K.at(c, x, y + 120, 0, s):
                ox, oy = -x, -(y + 120)
                if not with_text:
                    c.drawPath(P((x + ox, y + 50 + oy), (x + ox, y + 120 + oy)), K.paint(BLACK, 1, 9))
                    c.drawPath(rect(x + ox, y + oy, w, 100, 14), K.paint("#FFFFFF"))
                    c.drawPath(rect(x + ox, y + oy, w, 100, 14), K.paint(BLACK, 1, 8))
                    (a0, a1) = ar
                    c.drawPath(arrow((a0[0] + ox, a0[1] + oy), (a1[0] + ox, a1[1] + oy), 0, 26), K.paint(col, 1, 7))
                else:
                    K.text(c, label, tx + ox, y + oy, SIGN_SIZE, "hand", col)
        return None

    return fn


def impact_fn(c, k, t):
    """drop：石头砸进路口，压扁后回弹，四周扬起尘土。"""
    sy = 1 - 0.35 * math.exp(-k * 5) * math.cos(k * 9)
    for i in range(8):
        a = i / 8 * 2 * math.pi + 0.3
        rr = 130 + 160 * k
        K.dot(c, CX + math.cos(a) * rr, CY + 40 + math.sin(a) * rr * 0.45, 26 * (1 - k), "#B9B9C0", 0.8 * (1 - k))
    if k < 0.5:
        for dx in (-50, 0, 50):
            K.seg(c, CX + dx, CY - 330, CX + dx, CY - 170, BLACK, 5, 0.5 * (1 - k * 2))
    draw_rock(c, CX, CY, 110, 0.4, sy)
    return None


def breath() -> skia.Path:
    parts = []
    for i, dy in enumerate((-30, 0, 30)):
        p = skia.Path()
        p.moveTo(2375, 5975 + dy)
        p.quadTo(2430, 5945 + dy, 2480, 5975 + dy)
        p.quadTo(2530, 6005 + dy, 2580 - i * 20, 5975 + dy)
        parts.append(p)
    return join(*parts)


def matchbox() -> skia.Path:
    return join(rect(650, 6200, 280, 130, 10), P((510, 6235), (790, 6235)), P((720, 6120), (975, 5775)),
                circle(990, 5755, 24))


# ---------------------------------------------------------------- 开局：方案被打回（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


LEAD = (700, 1150)
scene("方案又被打回", "开局 · 周五下午", (900, 820, 0.85), bars=2)
L(stick(*LEAD, 0.8, "point", tie=True), 0, 0.9, sfx="wood_high")
L(face(*LEAD, 0.8, "sad"), 0.9, 1.0)
L(doc(1100, 880, 300, 380, 5), 1, 1.9, BLACK, 9, sfx="wood_low")
T("方案", 1100, 630, 60, k0=2, k1=2.8, sfx="pop")
L(cross(1100, 880, 120), 3, 3.8, RED, 14, sfx="rim")
T("周五 下午", 680, 680, 60, k0=4, k1=5.25, sfx="pop")

ME = (2000, 1250)
PAO1 = (1150, 420, 640, 170)
scene("这做的什么东西", "开局 · 一句话飞来", (1400, 800, 0.68))
L(stick(*ME, 0.8), 0, 0.9, BLUE, 10, sfx="wood_high")
L(face(*ME, 0.8, "flat"), 0.9, 1.0, BLUE, 9)
C(1, 1.8, pao_fn(*PAO1, lambda k: (math.sin(clamp01(k) * math.pi / 2) * (1 + 0.1 * math.sin(k * math.pi)), 44, 0, 0)),
  sfx="wood_low")
T("这做的什么东西", 1190, 420, 58, RED, k0=2, sfx="pop")
C(5, 6, stone_fly_fn((1480, 470), (1945, 1105)), sfx="shaker")
H(6, "kick")
T("咚！", 2150, 850, 76, RED, k0=7, k1=7.8, sfx="pop")

ASK = (1530, 3640, 0.65)        # 站在路口的主角（左下角）
ARROWS = [((CX, CY - 250), (CX, CY - 420)), ((CX - 250, CY), (CX - 420, CY)), ((CX + 250, CY), (CX + 420, CY)),
          ((CX, CY + 250), (CX, CY + 400))]
QS = [(CX, CY - 490), (CX - 480, CY + 15), (CX + 480, CY + 15), (CX, CY + 470)]
scene("你会怎么接", "开局 · 站在路口", (1800, 3200, 0.65))
L(stick(*ASK, "shrug"), 0, 0.9, BLUE, 10, sfx="wood_high")
L(eyes_only(*ASK), 0.9, 1.0, BLUE, 9)
L(join(*[arrow(a, z, 0, 36) for a, z in ARROWS]), 1, 1.9, BLACK, 8, sfx="wood_low")
for n, (x, y) in enumerate(QS):
    T("？", x, y, 90, RED, k0=2 + n, k1=2.8 + n, sfx="pop" if n % 2 == 0 else "tom")
T("？", ASK[0], ASK[1] - 290 * ASK[2] - 120, 100, RED, k0=6, k1=6.8, sfx="ding")

# ---------------------------------------------------------------- drop：石头砸出十字路口（场景 4）+ 亮书（场景 5）

scene("一句话，四条路", "书中观点 · 四种选择", (1800, 3180, 0.6), shake=[0], flashes=[0])
C(0, 0.8, impact_fn, sfx="kick")
L(cracks(), 0, 0.8, RED, 8)
L(roads(), 1, 1.9, BLACK, 9, sfx="wood_low")
C(2, 2.6, signs_fn(False), sfx="pop")
C(3, 3.5, signs_fn(True), sfx="ding")
L(circle(ASK[0], ASK[1] - 290 * ASK[2] + 14, 9), 4, 4.4, BLUE, 7, sfx="tom")

BK = (2650, 1950)
scene("有本书讲过", "书中观点 · 第五章", (2950, 2200, 0.85))
L(book(*BK, 340, 230), 0, 0.9, BLACK, 9, sfx="wood_low")
T("非暴力沟通", 3180, 1880, 64, GREEN, k0=1, k1=2.25, sfx="pop")
L(card_path(), 3, 3.9, BLACK, 8, sfx="wood_high")
L(card_icons(), 4, 4.9, BLACK, 7, sfx="pop")
for n, w in enumerate(("观察", "感受", "需要", "请求")):
    T(w, card_cx(n), CARD[1] + 60, 46, GREEN if n == 2 else BLACK, k0=5 + n * 0.25, k1=5.6 + n * 0.25,
      sfx="pop" if n == 0 else None)
C(6, 6.6, glow_fn(card_cx(2), CARD[1], CARD[2] - 16, CARD[3] - 16), sfx="ding")
L(check(card_cx(2) + 95, CARD[1] - 70, 26), 6.6, 7.0, GREEN, 9)
T("第五章", 3180, 2010, 56, k0=7, k1=7.8, sfx="tom")

# ---------------------------------------------------------------- 四条路，一条一屏（场景 6–9）

W0 = (480, 3600)
scene("第一条：怪自己", "第一条路 · 怪自己", (640, 3300, 0.85))
L(P((260, 2900), (260, 3600), (1100, 3600)), 0, 0.9, BLACK, 10, sfx="wood_low")
L(crouch(*W0), 1, 1.9, BLUE, 10, sfx="wood_high")
L(crouch_face(*W0), 1.9, 2.0, BLUE, 8)
L(cloud(500, 3080), 2, 2.8, BLACK, 9, sfx="pop")
L(rain(500, 3180), 3, 3.8, BLUE, 7, sfx="shaker")
L(bubble(880, 2950, 380, 130, -1), 4, 4.8, BLACK, 8, sfx="wood_high")
T("我真没用", 880, 2950, 56, k0=5, k1=6, sfx="pop")
L(moon(930, 3280, 60), 6, 6.8, BLACK, 9, sfx="tom")
T("02:00", 930, 3450, 56, RED, k0=7, k1=8, sfx="pop")

N0, N1 = (1550, 2450, 0.9), (2080, 2450, 0.8)
scene("第二条：怪对方", "第二条路 · 怪对方", (1800, 2150, 0.85))
L(akimbo(*N0), 0, 0.9, BLUE, 10, sfx="wood_high")
L(away(*N0, -1), 0.9, 1.0, BLUE, 8)
L(flame(1550, 2130, 130), 1, 1.9, RED, 9, sfx="shaker")
L(bubble(1560, 1840, 480, 130, -1), 2, 2.8, BLACK, 8, sfx="wood_low")
T("他就是针对我", 1560, 1840, 54, k0=3, k1=4.5, sfx="pop")
L(stick(*N1, tie=True), 5, 5.8, BLACK, 10, sfx="wood_high")
L(away(*N1, 1), 5.8, 6.0, BLACK, 8)
T("第二天，甩脸", 2080, 1980, 56, RED, k0=6, k1=7.5, sfx="rim")

E0 = (2700, 3600, 0.9)
EB = (3200, 3330, 280, 130)
scene("第三条：看看自己", "第三条路 · 看看自己", (2950, 3300, 0.85))
L(chest(*E0), 0, 0.9, BLUE, 10, sfx="wood_high")
L(face(*E0, "flat"), 0.9, 1.0, BLUE, 8)
L(battery(*EB), 1, 1.9, BLACK, 9, sfx="wood_low")
C(2, 2.8, cells_fn(*EB, [GREEN, GREEN, GREEN]), sfx="pop")
L(empty_cell(*EB, 3), 3, 3.6, RED, 7, sfx="rim")
L(bubble(2780, 2950, 400, 130, -1), 4, 4.8, BLACK, 8, sfx="wood_high")
T("我有点难受", 2780, 2950, 56, k0=5, k1=6.25, sfx="pop")
T("两周的活被看见", 3200, 3480, 50, GREEN, k0=6.25, k1=7.9)
H(7, "ding")

S0, S1 = (1550, 4750, 0.9), (2180, 4750, 0.8)
SB = (1960, 4230, 230, 110)
scene("第四条：听听对方", "第四条路 · 听听对方", (1800, 4450, 0.85))
L(stick(*S0, tie=True), 0, 0.9, BLACK, 10, sfx="wood_high")
L(face(*S0, "flat"), 0.9, 1.0, BLACK, 8)
L(join(clock(1550, 4230, 85), hands_at(1550, 4230, 85, 9, 0)), 1, 1.9, BLACK, 8, sfx="wood_low")
T("明早上会", 1550, 4080, 52, k0=2, k1=3, sfx="pop")
L(battery(*SB), 3, 3.8, BLACK, 9, sfx="wood_high")
C(4, 4.4, cells_fn(*SB, [RED]), sfx="rim")
T("要一份能交的", 1960, 4080, 50, k0=5, k1=6.5, sfx="pop")
L(stick(*S1), 6.5, 7.2, BLUE, 10)
L(face(*S1, "smile"), 7.2, 7.4, BLUE, 8)
T("他急", 1300, 4430, 60, RED, k0=7, k1=7.8, sfx="tom")

# ---------------------------------------------------------------- 拉远：四个结局（场景 10，横屏封面）

scene("四条路，四个结局", "拉远 · 四个结局", (1800, 3380, 0.29))
H(0, "shaker", 0.6)
for n, (w, x, y, col, sfx) in enumerate((("失眠", 650, 3740, RED, "rim"), ("冷战", 2150, 2600, RED, "rim"),
                                         ("说出口", 2950, 3740, GREEN, "pop"), ("对上话", 1800, 4920, GREEN, "ding"))):
    T(w, x, y, 150, col, k0=1 + n * 2, k1=1.8 + n * 2, sfx=sfx)

# ---------------------------------------------------------------- 书中观点：火柴和火（场景 11）

scene("他的话是火柴", "书中观点 · 刺激和需要", (1000, 5850, 0.85))
L(matchbox(), 0, 0.9, BLACK, 9, sfx="wood_low")
T("他的话：刺激", 650, 6340, 60, k0=1, k1=2.5, sfx="pop")
L(flame(995, 5735, 170), 3, 3.8, RED, 9, sfx="shaker")
MB = (1380, 5760, 220, 110)
L(battery(*MB), 4, 4.8, BLACK, 9, sfx="wood_high")
C(4.8, 5.0, cells_fn(*MB, [RED]))
L(arrow((1255, 5735), (1085, 5660), 0.1, 32), 5, 5.6, RED, 8, sfx="pop")
T("需要", 1380, 5640, 56, GREEN, k0=5.6, k1=6.0)
T("火来自你的需要", 1000, 5400, 64, RED, k0=6, k1=7.75, sfx="ding")

# ---------------------------------------------------------------- 两步做法（场景 12–13）

P0 = (2300, 6250, 0.9)
PB = (2900, 6100, 260, 120)
scene("先停一下问自己", "做法 · 第一步", (2600, 5850, 0.85))
L(chest(*P0), 0, 0.9, BLUE, 10, sfx="wood_high")
L(calm(*P0), 0.9, 1.0, BLUE, 8)
L(breath(), 1, 1.8, BLUE, 7, sfx="shaker")
T("① 停一下", 2600, 5420, 70, BLUE, k0=2, k1=3.25, sfx="pop")
L(bubble(2850, 5700, 420, 130, -1), 4, 4.8, BLACK, 8, sfx="wood_low")
T("我缺了什么", 2850, 5700, 54, k0=5, k1=6.25, sfx="pop")
L(battery(*PB), 6.3, 7.0, BLACK, 9)
C(7, 7.8, cells_fn(*PB, [GREEN] * 4), sfx="ding")

Q0, Q1 = (1430, 7400, 0.85), (2170, 7400, 0.85)
PAO2 = (1520, 6640, 540, 210)


def _soften(k):
    """小泡：先带刺冒出来（红），第 4 拍起刺一根根缩回去，变成圆滚滚的蓝色气泡，嘴角上扬。"""
    grow = math.sin(clamp01(k / 0.25) * math.pi / 2)
    f = ease_in_out(clamp01((k - 0.5) / 0.3))
    return grow, 44 * (1 - f), f, f


scene("再问他要什么", "做法 · 第二步", (1800, 7000, 0.85))
L(join(doc(1800, 7000, 220, 280, 5), P((1560, 7150), (2040, 7150))), 0, 0.9, BLACK, 9, sfx="wood_low")
L(stick(*Q0), 1, 1.9, BLUE, 10, sfx="wood_high")
L(face(*Q0, "smile"), 1.9, 2.0, BLUE, 8)
L(stick(*Q1, tie=True), 2, 2.9, BLACK, 10, sfx="pop")
L(face(*Q1, "flat"), 2.9, 3.0, BLACK, 8)
C(3, 5, pao_fn(*PAO2, _soften), sfx="wood_low")
H(4, "ding")
T("明早要用？", 1570, 6595, 52, k0=5, k1=6.25, sfx="pop")
T("哪块先改？", 1570, 6685, 52, k0=6.3, k1=7.5)
L(check(1800, 6990, 55), 7, 7.6, GREEN, 12, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 4330, 0.11)
END = (1800, 7950, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, END, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(rect(1800, 7980, 1150, 440, 30), 6, 6.9, BLACK, 8, sfx="pop")
T("你最常走哪条路？", 1800, 7890, 76, RED, k0=7, k1=9, sfx="pop")
T("下一讲：“你又加班”，到底想说啥？", 1800, 8070, 46, k0=10, k1=14, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "choice", "四种接法", "挨了句批评，你会怎么接？", ACC, b.shots,
                 [f"{BOOK}第五章“感受的根源”（转述）", "中译本：阮胤华译，华夏出版社"],
                 "挨了句批评|你会【怎么接】", SQUARE_SHOT,
                 ["书中观点均为转述：听到不中听的话，有四种选择——责备自己、指责对方、体会自己的感受和需要、体会对方的"
                  "感受和需要；别人的言行是刺激，感受的根源在自己的需要（马歇尔·卢森堡《非暴力沟通》第五章“感受的根源”，"
                  "阮胤华译，华夏出版社）。上屏均为转述，不是逐字引文。",
                  "周五下午方案被打回、领导那句“这做的什么东西”、四条路各自的结局（失眠／冷战／说出口／对上话）均为示意，"
                  "不指向任何具体公司或个人；“02:00”“两周”“明早上会”为示意，不是数据。",
                  "“他的话是火柴、火来自你的需要”为对书中“刺激与根源”观点的通俗化比喻；两步做法（先停一下问自己缺了什么；"
                  "再问对方要什么，如“明早要用？哪块先改？”）为据书中思路整理的建议。",
                  "十字路口、石头、四格卡、话泡泡“小泡”为本系列视觉示意。"],
                 tags="#职场 #情绪管理")
    return b.attach(ep)
