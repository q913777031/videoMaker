"""10 当作第二次活（白板手绘版）：要是能重来，今天你怎么过？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（误区对照：每屏左边 ✗ 常见说法、右边 ✓ 书里说的，一屏一对）：早上闹钟响，两张一模一样的日历页 →
抛问题“要是今天能重来，你会怎么过？”（倒带符号）→ 亮书 + 回看这一季：罗盘一圈九个字，第十格空着 →
drop：红字“第二次”砸下，阿宁身后出现一个虚线重影“第一次”（书中：就当你在活第二次，第一次你正要犯的错已经犯过了）→
五组误区对照（意义得是大目标 / 意义很具体；环境决定一切 / 态度能自己选；盯着开心才会开心 / 幸福追不到、投入之后自己来；
多想想自己 / 眼睛看外面才好用；自由就是想干嘛干嘛 / 东岸自由女神、西岸该配责任女神）→
回到早上：按“第二次”过一遍今天（时间线三处小改动）→
做法（做决定前问“第一次这么做，后悔了吗” / 今天挑一件事，做到重来也这么做，罗盘停住 / 拉远看这一季十个字全亮）→
拉远全板 → 评论区“你最想重来的是哪一天？”，这一季讲完了。
书中观点为转述（Viktor E. Frankl, Man's Search for Meaning，第二部分〈存在之本质〉〈生命之意义〉、第二部分谈自由与责任处、
1984 年版序言；中译本《活出生命的意义》，吕娜译，华夏出版社 2010）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               face, hands_at, join, marker, rect, stick)

from .common import BOOK, episode

ACC = "#3E7F86"                 # 本讲主色：青灰蓝
SQUARE_SHOT = 3                 # 场景 4：阿宁 + 身后虚线重影“第一次” + 红字“第二次”
GRAY = "#8A8F98"
YELLOW = "#D9A21B"
PAPER = "#FBFBF9"

b = Board(size=(3600, 11400))

# 这一季罗盘指过的字（第 1–10 讲各一个），第十个是本讲的“第二次”
WORDS = ["为什么", "态度", "谁在等", "三条路", "为谁做", "想着谁", "替她扛", "这件事", "粮仓", "第二次"]


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

def compass(x, y, r=60) -> skia.Path:
    """系列视觉角色：小罗盘（圆框 + 顶上小环 + 四个刻度），指针另用 needle_fn 画。"""
    parts = [circle(x, y, r), circle(x, y - r - 14, 12)]
    for a in range(4):
        ang = a * math.pi / 2
        parts.append(P((x + math.cos(ang) * r * 0.72, y + math.sin(ang) * r * 0.72),
                       (x + math.cos(ang) * r * 0.9, y + math.sin(ang) * r * 0.9)))
    return join(*parts)


def needle_fn(x, y, r, aim, turns=2.5):
    """罗盘指针：k<1 时乱转（越转越慢、带抖动），k=1 停在指向 aim=(ax, ay) 的方向，之后一直停着。"""
    final = math.atan2(aim[1] - y, aim[0] - x)

    def fn(c, k, t):
        e = ease_in_out(k)
        a = final + (1 - e) * turns * 2 * math.pi + (0.5 * math.sin(k * 23) * (1 - k) if k < 1 else 0)
        ca, sa = math.cos(a), math.sin(a)
        L_, w = r * 0.78, r * 0.2
        tip, tail = (x + ca * L_, y + sa * L_), (x - ca * L_, y - sa * L_)
        s1, s2 = (x - sa * w, y + ca * w), (x + sa * w, y - ca * w)
        K.poly(c, [tip, s1, s2], RED)
        K.poly(c, [tail, s1, s2], BLACK)
        K.dot(c, x, y, r * 0.1, PAPER)
        return None

    return fn


def ring_pos(cx, cy, R, i, n=10):
    a = math.radians(-90 + 360 * i / n)
    return cx + R * math.cos(a), cy + R * math.sin(a)


def ring_fn(cx, cy, R, words, size, color, last=None, last_color=RED):
    """罗盘外一圈小字：按 k 逐个浮现（每个字组淡入并轻微放大），返回当前字的位置给手。
    last：给最后一格单独上色（本讲的“第二次”）。"""
    n = len(words)

    def fn(c, k, t):
        tip = None
        for i, w in enumerate(words):
            f = clamp01(k * n - i)
            if f <= 0:
                break
            x, y = ring_pos(cx, cy, R, i)
            col = last_color if (last is not None and i == last) else color
            s = 1 + 0.25 * (1 - f)
            c.save()
            c.translate(x, y)
            c.scale(s, s)
            K.text(c, w, 0, 0, size, "hand", col, f)
            c.restore()
            if f < 1:
                tip = (x + size * 0.6, y + size * 0.3)
        return tip

    return fn


def alarm(x, y, r=100) -> skia.Path:
    """闹钟：钟面 + 7 点指针 + 顶上两只铃 + 两条腿。"""
    bell = []
    for sgn in (-1, 1):
        bx, by = x + sgn * r * 0.7, y - r * 0.85
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(bx - r * 0.38, by - r * 0.38, r * 0.76, r * 0.76), 180 if sgn < 0 else 270, 180)
        bell.append(p)
    legs = join(P((x - r * 0.6, y + r * 0.8), (x - r * 0.8, y + r * 1.1)), P((x + r * 0.6, y + r * 0.8), (x + r * 0.8, y + r * 1.1)))
    shake_ = join(P((x - r * 1.3, y - r * 0.9), (x - r * 1.5, y - r * 1.1)), P((x + r * 1.3, y - r * 0.9), (x + r * 1.5, y - r * 1.1)))
    return join(clock(x, y, r), hands_at(x, y, r, 7, 0), *bell, legs, shake_)


def cal_page(x, y, w=260, h=300) -> skia.Path:
    """日历页：外框 + 顶部两个装订环 + 页眉横线 + 三行事项。"""
    top = y - h / 2
    parts = [rect(x, y, w, h, 14), P((x - w / 2, top + 70), (x + w / 2, top + 70)),
             circle(x - w * 0.25, top, 12), circle(x + w * 0.25, top, 12)]
    for i in range(3):
        yy = top + 130 + i * 55
        parts.append(P((x - w * 0.35, yy), (x + w * 0.35, yy)))
    return join(*parts)


def rewind(x, y, s=1.0) -> skia.Path:
    """倒带符号：两个朝左的三角。"""
    def tri(cx):
        return P((cx + 60 * s, y - 70 * s), (cx - 60 * s, y), (cx + 60 * s, y + 70 * s), close=True)
    return join(tri(x - 50 * s), tri(x + 70 * s))


def playhead_fn(x0, x1, y):
    """进度条上的播放点：从右往左倒回去。"""
    def fn(c, k, t):
        e = ease_in_out(k)
        x = x1 + (x0 - x1) * e
        c.drawCircle(x, y, 26, K.paint(RED))
        c.drawPath(P((x1, y), (x, y)), marker(RED, 12, 0.35))
        return (x, y - 30) if k < 1 else None
    return fn


def ghost_fn(x, y, s):
    """虚线重影：一个灰色虚线小人（“第一次”的自己），随 k 淡入。"""
    path = stick(x, y, s, "down")

    def fn(c, k, t):
        p = marker(GRAY, 8, 0.85 * k)
        p.setPathEffect(skia.DashPathEffect.Make([22, 16], 0))
        c.drawPath(path, p)
        return None

    return fn


def slam_fn(j_ref, word, x, y, size, color=RED):
    """第 0 拍砸下的大字：从 1.7 倍迅速缩到原大，之后停住。"""
    def fn(c, k, t):
        t_imp = b.t_of(j_ref[0], 0)
        f = clamp01((t - t_imp) / 0.22)
        s = 1 + 0.7 * (1 - f) ** 2
        c.save()
        c.translate(x, y)
        c.scale(s, s)
        K.text(c, word, 0, 0, size, "hand", color, clamp01(0.4 + f))
        c.restore()
        return None
    return fn


def pair_frame(cx, cy):
    """误区对照版式：中间竖线；左上 ✗ 常见说法，右上 ✓ 书里说。第 0 拍一起画出。"""
    L(P((cx, cy - 500), (cx, cy + 480)), 0, 0.8, BLACK, 8, sfx="wood_high")
    L(cross(cx - 470, cy - 455, 26), 0, 0.5, RED, 9)
    L(check(cx + 170, cy - 455, 30), 0, 0.5, GREEN, 10)
    T("常见说法", cx - 290, cy - 455, 56, GRAY, k0=0.1, k1=0.9)
    T("书里说", cx + 330, cy - 455, 56, GREEN, k0=0.2, k1=0.95)


def pair_text(cx, cy, left, right, right_colors=(BLACK, BLACK)):
    """左右两句：左边第 1–3 拍写完、第 4 拍划掉（rim），右边第 5–7 拍写完；第 8 拍 ding。"""
    lx, rx = cx - 315, cx + 315
    T(left[0], lx, cy - 300, 54, BLACK, k0=1, k1=1.9, sfx="pop")
    T(left[1], lx, cy - 205, 54, BLACK, k0=2, k1=2.9, sfx="pop")
    zig = P((lx - 250, cy - 270), (lx + 250, cy - 290), (lx - 240, cy - 225), (lx + 250, cy - 235))
    L(zig, 4, 4.6, RED, 9, sfx="rim")
    T(right[0], rx, cy - 300, 50, right_colors[0], k0=5, k1=5.9, sfx="pop")
    T(right[1], rx, cy - 205, 50, right_colors[1], k0=6, k1=6.9, sfx="pop")
    H(8, "ding")


def mountain(x, y, w=440, h=330) -> skia.Path:
    """远处一座高山，峰顶一面很小的旗。"""
    px, py = x + w * 0.1, y - h
    return join(P((x - w / 2, y), (x - w * 0.18, y - h * 0.55), (x - w * 0.05, y - h * 0.4), (px, py), (x + w / 2, y)),
                P((px, py), (px, py - 80)), P((px, py - 80), (px + 45, py - 64), (px, py - 48)))


def cloud(x, y, w=320) -> skia.Path:
    p = skia.Path()
    h = w * 0.35
    p.moveTo(x - w / 2, y + h / 2)
    p.cubicTo(x - w * 0.7, y - h * 0.1, x - w * 0.35, y - h * 0.7, x - w * 0.12, y - h * 0.35)
    p.cubicTo(x - w * 0.05, y - h * 1.1, x + w * 0.4, y - h * 1.0, x + w * 0.3, y - h * 0.25)
    p.cubicTo(x + w * 0.65, y - h * 0.35, x + w * 0.65, y + h * 0.5, x + w / 2 - 20, y + h / 2)
    p.close()
    rain = [P((x + dx, y + h / 2 + 30), (x + dx - 20, y + h / 2 + 90)) for dx in (-100, -30, 40, 110)]
    return join(p, *rain)


def fork(x, y, h=330) -> skia.Path:
    """分岔小路：(x, y) 为路的起点（下方）。"""
    m = (x, y - h * 0.45)
    return join(P((x, y), m), P(m, (x - 150, y - h)), P(m, (x + 150, y - h)))


def butterfly(x, y, s=1.0, flap=0.0) -> skia.Path:
    """蝴蝶：两对翅膀 + 身子；flap∈[0,1] 让翅膀收拢一点。"""
    ww = 1 - 0.55 * flap
    p = skia.Path()
    for sgn in (-1, 1):
        p.moveTo(x, y)
        p.cubicTo(x + sgn * 70 * s * ww, y - 80 * s, x + sgn * 95 * s * ww, y - 10 * s, x, y)
        p.moveTo(x, y)
        p.cubicTo(x + sgn * 60 * s * ww, y + 15 * s, x + sgn * 55 * s * ww, y + 70 * s, x, y + 10 * s)
    p.moveTo(x, y - 30 * s)
    p.lineTo(x, y + 35 * s)
    return p


def fly_fn(a, z, s=0.7, color=None, wobble=40):
    """蝴蝶从 a 飞到 z（k 内），沿途上下扑腾；之后停在 z 原地慢慢扇翅。"""
    col = color or ACC

    def fn(c, k, t):
        e = ease_in_out(k)
        x = a[0] + (z[0] - a[0]) * e
        y = a[1] + (z[1] - a[1]) * e + wobble * math.sin(k * math.pi * 3) * (1 - k)
        flap = 0.5 + 0.5 * math.sin(t * (18 if k < 1 else 5))
        c.drawPath(butterfly(x, y, s, flap), marker(col, 7))
        return None

    return fn


def eye(x, y, w=200) -> skia.Path:
    h = w * 0.42
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.quadTo(x, y - h * 1.2, x + w / 2, y)
    p.quadTo(x, y + h * 1.2, x - w / 2, y)
    p.close()
    p.addCircle(x, y, h * 0.5)
    return p


def blur_eye_fn(x, y, w=200):
    """看自己的眼睛：两层错开的模糊描线，随 k 渐显。"""
    path = eye(x, y, w)

    def fn(c, k, t):
        for dx, dy in ((0, 0), (16, 10)):
            c.save()
            c.translate(dx, dy)
            c.drawPath(path, K.paint(BLACK, 0.55 * k, 10, blur=7))
            c.restore()
        return None

    return fn


def tree(x, y, s=1.0) -> skia.Path:
    """小树：(x, y) 为树根。"""
    crown = skia.Path()
    crown.addOval(skia.Rect.MakeXYWH(x - 85 * s, y - 280 * s, 170 * s, 170 * s))
    return join(P((x, y), (x, y - 120 * s)), P((x, y - 70 * s), (x + 40 * s, y - 110 * s)), crown)


def us_map(x, y, w=520, h=260) -> skia.Path:
    """很粗的美国本土简笔轮廓（只示意东西两岸）。"""
    pts = [(-0.50, -0.42), (-0.10, -0.48), (0.18, -0.40), (0.30, -0.30), (0.42, -0.46), (0.50, -0.30),
           (0.40, -0.05), (0.38, 0.12), (0.30, 0.25), (0.32, 0.50), (0.22, 0.30), (0.05, 0.28),
           (-0.10, 0.45), (-0.22, 0.25), (-0.38, 0.20), (-0.50, 0.02)]
    return P(*[(x + px * w, y + py * h) for px, py in pts], close=True)


def statue(x, y, s=1.0) -> skia.Path:
    """简笔雕像：底座 + 举一只手的小人（不画真实雕像细节）。"""
    hy = y - 200 * s
    return join(rect(x, y + 15 * s, 90 * s, 30 * s, 4), circle(x, hy, 26 * s), P((x, hy + 26 * s), (x, y - 60 * s)),
                P((x - 30 * s, y), (x, y - 60 * s), (x + 30 * s, y)),
                P((x - 40 * s, hy + 90 * s), (x, hy + 50 * s), (x + 40 * s, hy - 40 * s)),
                circle(x + 44 * s, hy - 56 * s, 12 * s))


# ---------------------------------------------------------------- 开局：又是一样的一天（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("又是一样的一天", "早上七点", (950, 900, 0.85), bars=2)
L(alarm(600, 640, 105), 0, 0.9, BLACK, 9, sfx="wood_high")
T("7:00", 600, 860, 64, RED, k0=1, k1=1.9, sfx="pop")
L(cal_page(1060, 720, 250, 300), 2, 2.8, BLACK, 8, sfx="wood_low")
L(cal_page(1370, 720, 250, 300), 3, 3.8, BLACK, 8, sfx="wood_low")
L(stick(640, 1390, 0.8, "shrug"), 4, 4.7, BLUE, 10, sfx="wood_high")
L(face(640, 1390, 0.8, "flat"), 4.7, 4.9, BLUE, 9)
T("复制粘贴的一天", 1215, 1060, 56, GRAY, k0=5, k1=6, sfx="pop")

TL = (2200, 3100, 860)            # 进度条：左端、右端、高度
scene("要是能重来", "灵魂拷问", (2650, 900, 0.85))
L(rewind(2650, 560, 1.0), 0, 0.9, RED, 10, sfx="wood_high")
L(join(P((TL[0], TL[2]), (TL[1], TL[2])), P((TL[0], TL[2] - 24), (TL[0], TL[2] + 24)),
       P((TL[1], TL[2] - 24), (TL[1], TL[2] + 24))), 1, 1.8, BLACK, 9, sfx="wood_low")
b.custom(J(), 2, 3.6, playhead_fn(TL[0] + 30, TL[1] - 10, TL[2]))
H(2, "shaker")
T("早上", TL[0], 950, 50, GRAY, k0=3, k1=3.8, sfx="pop")
T("要是今天能重来", 2650, 1130, 76, RED, k0=4, k1=5.75, sfx="kick")
T("你会怎么过？", 2650, 1260, 76, RED, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 亮书 + 回看这一季（场景 3）

CMP3 = (1230, 2230, 90)
RING3 = 290
scene("这一季最后一讲", "活出生命的意义 · 最后一讲", (950, 2300, 0.85))
L(book(600, 2080, 380, 250), 0, 0.9, BLACK, 9, sfx="wood_low")
T("活出生命的意义", 600, 1850, 56, GREEN, k0=1, k1=2.75, sfx="pop")
T("弗兰克尔", 600, 2310, 58, k0=3, k1=4, sfx="pop")
L(compass(*CMP3), 4, 4.8, BLACK, 8, sfx="wood_high")
b.custom(J(), 5, 7.0, ring_fn(CMP3[0], CMP3[1], RING3, WORDS[:9], 46, GRAY))
H(5, "pop")
H(6, "pop", 0.6)
Q3 = ring_pos(CMP3[0], CMP3[1], RING3, 9)
T("？", Q3[0], Q3[1], 60, RED, k0=7, k1=7.8, sfx="pop")
b.custom(J(), 6, 8.0, needle_fn(*CMP3, Q3, turns=2.5))
H(8, "ding")
T("前九讲", 600, 2450, 50, GRAY, k0=6, k1=6.8)

# ---------------------------------------------------------------- drop：就当第二次活（场景 4）

NAN4 = (2760, 2800)               # 阿宁脚底
GHO4 = (2560, 2770)               # 重影脚底
J4 = [0]
scene("就当第二次活", "活出生命的意义 · 书中观点", (2650, 2300, 0.85), shake=[0], flashes=[0])
J4[0] = J()
b.custom(J4[0], 0, 0.3, slam_fn(J4, "第二次", 2650, 1860, 150), sfx="kick")
L(stick(*NAN4, 0.9, "down"), 1, 1.8, BLUE, 10, sfx="wood_high")
L(face(*NAN4, 0.9, "smile"), 1.8, 2.0, BLUE, 9)
b.custom(J4[0], 2, 2.8, ghost_fn(*GHO4, 0.9), sfx="shaker")
T("第一次", 2330, 2470, 52, GRAY, k0=3, k1=3.8, sfx="pop")
T("就当你在活第二次", 2650, 2040, 62, k0=4, k1=5.9, sfx="pop")
T("第一次的错，犯过了", 2650, 2150, 62, RED, k0=6, k1=8, sfx="ding")

# ---------------------------------------------------------------- 五组误区对照（场景 5–9）

C5 = (2650, 3700)
scene("意义在这件事里", "误区① · 意义在哪", (*C5, 0.85))
pair_frame(*C5)
pair_text(*C5, ("意义得是", "一个大目标"), ("意义很具体", "在今天这件事里"), (BLACK, RED))
L(mountain(C5[0] - 315, C5[1] + 330, 440, 330), 3, 3.9, GRAY, 8, sfx="wood_low")
L(cal_page(C5[0] + 315, C5[1] + 120, 240, 290), 7, 7.6, BLACK, 8, sfx="wood_high")
L(rect(C5[0] + 315, C5[1] + 120 - 145 + 185, 220, 64, 32), 7.6, 8.0, RED, 8)

C6 = (950, 3700)
scene("态度能自己选", "误区② · 处境和态度", (*C6, 0.85))
pair_frame(*C6)
pair_text(*C6, ("环境决定", "一切"), ("处境再难", "态度能自己选"), (BLACK, RED))
L(join(cloud(C6[0] - 315, C6[1] - 10, 300), stick(C6[0] - 315, C6[1] + 360, 0.5, "shrug")), 3, 3.9, GRAY, 8,
  sfx="wood_low")
L(fork(C6[0] + 315, C6[1] + 370, 340), 7, 7.5, BLACK, 9, sfx="wood_high")
L(arrow((C6[0] + 330, C6[1] + 190), (C6[0] + 450, C6[1] + 60), 0.1, 36), 7.5, 8.0, RED, 10)

C7 = (950, 5100)
scene("幸福追不到", "误区③ · 幸福", (*C7, 0.85))
pair_frame(*C7)
pair_text(*C7, ("盯着开心", "才会开心"), ("投入一件事", "幸福自己会来"), (BLACK, RED))
L(stick(C7[0] - 400, C7[1] + 400, 0.55, "point"), 3, 3.7, BLACK, 9, sfx="wood_low")
b.custom(J(), 3.2, 4.4, fly_fn((C7[0] - 300, C7[1] + 160), (C7[0] - 130, C7[1] + 20), 0.7, wobble=50))
L(join(stick(C7[0] + 230, C7[1] + 400, 0.55, "hold"),
       P((C7[0] + 300, C7[1] + 290), (C7[0] + 520, C7[1] + 290)),
       P((C7[0] + 500, C7[1] + 290), (C7[0] + 500, C7[1] + 400))), 7, 7.7, BLACK, 9, sfx="wood_high")
b.custom(J(), 7.4, 8.6, fly_fn((C7[0] + 560, C7[1] + 30), (C7[0] + 262, C7[1] + 205), 0.55, wobble=40))

C8 = (2650, 5100)
scene("看向外面", "误区④ · 眼睛", (*C8, 0.85))
pair_frame(*C8)
pair_text(*C8, ("多想想自己", "就想明白了"), ("眼睛看外面才好用", "人投入外面才像自己"), (BLACK, RED))
b.custom(J(), 3, 3.6, blur_eye_fn(C8[0] - 315, C8[1] + 130, 220), sfx="wood_low")
L(arrow((C8[0] - 200, C8[1] + 190), (C8[0] - 300, C8[1] + 210), -1.2, 30), 3.4, 3.9, GRAY, 8)
L(eye(C8[0] + 190, C8[1] + 150, 160), 7, 7.5, BLACK, 9, sfx="wood_high")
L(join(arrow((C8[0] + 290, C8[1] + 150), (C8[0] + 420, C8[1] + 150), 0.0, 28), tree(C8[0] + 500, C8[1] + 300, 0.9)),
  7.5, 8.0, GREEN, 9)

C9 = (2650, 6500)
scene("自由配着责任", "误区⑤ · 自由", (*C9, 0.85))
pair_frame(*C9)
pair_text(*C9, ("自由就是", "想干嘛干嘛"), ("东岸有自由女神", "西岸该配责任女神"), (BLACK, RED))
SX = C9[0] - 315
L(join(stick(SX, C9[1] + 420, 0.55, "up"),
       *[arrow((SX + 140 * math.cos(a), C9[1] + 170 + 140 * math.sin(a)),
               (SX + 250 * math.cos(a), C9[1] + 170 + 250 * math.sin(a)), 0.2, 26)
         for a in (math.radians(d) for d in (-150, -30, 200, -20 + 360))]), 3, 3.9, GRAY, 8, sfx="wood_low")
L(us_map(C9[0] + 315, C9[1] + 190, 540, 280), 7, 7.5, BLACK, 8, sfx="wood_high")
L(statue(C9[0] + 500, C9[1] + 230, 0.6), 7.5, 7.8, BLUE, 7)
L(statue(C9[0] + 140, C9[1] + 230, 0.6), 7.7, 8.0, RED, 7)

# ---------------------------------------------------------------- 回到早上（场景 10）

AX = 6580
NODES = (520, 950, 1380)
scene("第二次这样过", "回到早上", (950, 6500, 0.85))
T("第二次的今天", 950, 6080, 72, BLUE, k0=0, k1=1.5, sfx="pop")
L(stick(NODES[0] - 60, 6980, 0.5, "down"), 1, 1.7, BLUE, 8, sfx="wood_high")
L(join(arrow((380, AX), (1540, AX), 0.0, 40), *[circle(x, AX, 18) for x in NODES]), 2, 2.8, BLACK, 9, sfx="wood_low")
T("路上抬头看看", NODES[0] + 30, AX - 110, 50, RED, k0=3, k1=4.5, sfx="pop")
T("开会先说重点", NODES[1], AX + 130, 50, RED, k0=5, k1=6.5, sfx="pop")
T("下班准点走", NODES[2] - 40, AX - 110, 50, RED, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

NOTE11 = (1080, 7860, 640, 330)
scene("先问后不后悔", "做法① · 先问一句", (950, 7900, 0.85))
T("① 做决定前", 950, 7440, 72, BLUE, k0=0, k1=1.5, sfx="pop")
b.custom(J(), 2, 2.6, lambda c, k, t: c.drawPath(rect(*NOTE11, 12), K.paint(YELLOW, 0.35 * k)))
L(rect(*NOTE11, 12), 2, 2.8, YELLOW, 8, sfx="wood_low")
T("第一次这么做", NOTE11[0], 7800, 56, k0=3, k1=4.5, sfx="pop")
T("后悔了吗？", NOTE11[0], 7920, 60, RED, k0=5, k1=6.25, sfx="pop")
L(stick(480, 8330, 0.75, "hold"), 7, 7.7, BLUE, 9, sfx="wood_high")
L(face(480, 8330, 0.75, "flat"), 7.7, 7.9, BLUE, 8)

CARD12 = (2500, 7820, 540, 190)
COMP12 = (2400, 8150, 40)
scene("重来也这么做", "做法② · 挑一件事", (2650, 7900, 0.85))
T("② 今天挑一件事", 2650, 7440, 72, BLUE, k0=0, k1=1.75, sfx="pop")
L(rect(*CARD12, 14), 2, 2.8, BLACK, 8, sfx="wood_low")
T("给家里打个电话", CARD12[0], CARD12[1], 56, k0=3, k1=4.75, sfx="pop")
L(check(2900, 7810, 60), 5, 5.6, RED, 12, sfx="rim")
L(stick(2400, 8330, 0.7, "down"), 6, 6.6, BLUE, 9, sfx="wood_high")
L(face(2400, 8330, 0.7, "smile"), 6.6, 6.8, BLUE, 8)
L(compass(*COMP12), 6.8, 7.2, BLACK, 6)
b.custom(J(), 7, 7.9, needle_fn(*COMP12, (CARD12[0], CARD12[1]), turns=1.5))
H(7, "shaker", 0.5)
H(8, "ding")
T("重来也这么做", 2900, 8150, 58, RED, k0=7, k1=8)

CMP13 = (1800, 9300, 140)
RING13 = 400
scene("十讲都在这里", "这一季 · 罗盘", (1800, 9330, 0.8))
L(compass(*CMP13), 0, 0.9, BLACK, 10, sfx="wood_high")
b.custom(J(), 1, 5.0, ring_fn(CMP13[0], CMP13[1], RING13, WORDS, 56, ACC, last=9))
H(1, "pop")
H(3, "pop", 0.7)
b.custom(J(), 5, 7.0, needle_fn(*CMP13, ring_pos(CMP13[0], CMP13[1], RING13, 9), turns=3))
H(5, "shaker", 0.6)
H(7, "ding")
T("十讲，十个字", 1800, 9850, 60, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5600, 0.16)
CMT = (1800, 10750, 0.8)
scene("这一季讲完了", "评论区见", FAR, bars=4)
b.move(J(), 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(bubble(1800, 10630, 1000, 220, -1), 5, 5.8, BLACK, 8)
T("你最想重来的是哪一天？", 1800, 10630, 74, RED, k0=6, k1=8.75, sfx="pop")
T("这一季讲完了，谢谢你看到这里", 1800, 10920, 52, k0=9, k1=12.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "twice", "当作第二次活", "要是能重来，今天你怎么过？", ACC, b.shots,
                 [f"{BOOK}第二部分〈存在之本质〉〈生命之意义〉、第二部分谈自由与责任处、1984 年版序言（转述）",
                  "Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010"],
                 "要是能重来|今天你【怎么过】", SQUARE_SHOT,
                 ["书中观点为转述，不是逐字引文：“就当你在活第二次，而且第一次你正要犯的错已经犯过了”与眼睛的比喻"
                  "（眼睛看见别的东西时才好用，人投入一件事或一个人时才最像人）见第二部分〈存在之本质〉；"
                  "意义因人、因时而不同、要看这一刻见第二部分〈生命之意义〉；处境再难也能选择态度见第一部分 在集中营的经历；"
                  "东海岸自由女神像、西海岸该配一座责任女神像见第二部分（具体小节需核实）；"
                  "成功和幸福追不到、是投入之后随之而来的见书中序言（1984 年版，中文对应位置需核实）。",
                  "误区对照里左边的“常见说法”为示意，不是书中引文；高山小旗、雨云、分岔路、蝴蝶、模糊与清楚的眼睛、"
                  "美国简笔轮廓与两座小雕像（不画真实雕像细节）、虚线重影均为对书中观点的通俗化示意。",
                  "罗盘一圈十个字回顾本系列十讲（为什么、态度、谁在等、三条路、为谁做、想着谁、替她扛、这件事、粮仓、第二次），"
                  "为本系列的视觉道具，不是书中内容。",
                  "早上闹钟、复制粘贴的日历页、时间线上的三处小改动、“给家里打个电话”均为现实场景示意，不指向任何具体公司或个人；"
                  "阿宁为示意角色；时间为示意，不是数据。",
                  "做法（做决定前问“第一次这么做，后悔了吗”；今天挑一件事，做到重来也这么做）为据书中思路整理的建议。"],
                 tags="#人生 #自律")
    return b.attach(ep)
