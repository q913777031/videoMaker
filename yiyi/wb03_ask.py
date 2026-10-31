"""03 生活在发问（白板手绘版）：别再问图啥，生活在问你。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（H 对话改写：原话 → 改写后的问法）：半夜刷到“人生有什么意义”，阿宁问自己“我天天上班图啥”，一根大问号箭头从他
指向“生活”，罗盘乱转 → 亮书：书里说这个问题方向反了 → drop：箭头整根调头，从“生活”指回阿宁，“生活在问你”，罗盘停下 →
书中故事（营里两个人都说对生活没指望了：一个有孩子在国外等，一个有一套书没写完；这件事只有他能做）→ 书中比喻
（问哪步棋最好，要看这一盘）→ 三组改写（上班 / 家里 / 倒霉事：原话划掉，写下新问法，最后三组连到同一个罗盘）→
三步做法（早上换个问法 / 答案写成一个动作 / 晚上看答了没）→ 拉远看全板 → 评论区。
书中观点为转述（Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010；
视角翻转与两个人的故事见第一部分〈在集中营的经历〉，棋局比喻与“人是被生活提问的人”见第二部分〈生命之意义〉）；
改写与做法为示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, face,
                               hands_at, join, partial, rect, stick, underline)

from .common import BOOK, episode

ACC = "#8A5A9E"
SQUARE_SHOT = 3                 # 场景 4：调头的大问号箭头 + 阿宁 + “生活在问你”

GRAY = "#80858E"                # 营里的场景用灰线
PAPER = "#FBFBF9"
NOTE = "#F7DC6F"

b = Board(size=(3600, 9700))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = J() if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def mirror(path, x0) -> skia.Path:
    """左右镜像（以 x=x0 为轴），用来让小人朝左拿东西。"""
    p = skia.Path(path)
    m = skia.Matrix()
    m.setScale(-1, 1, x0, 0)
    p.transform(m)
    return p


def moon(x, y, r=80) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def phone(x, y, w=300, h=400) -> skia.Path:
    return join(rect(x, y, w, h, 30), P((x - 40, y + h / 2 - 34), (x + 40, y + h / 2 - 34)))


def compass(x, y, r=50) -> skia.Path:
    """系列视觉角色：小罗盘（圆框 + 顶上小环 + 四个刻度）。"""
    parts = [circle(x, y, r), circle(x, y - r - r * 0.28, r * 0.22)]
    for a in range(4):
        ang = a * math.pi / 2
        parts.append(P((x + math.cos(ang) * r * 0.72, y + math.sin(ang) * r * 0.72),
                       (x + math.cos(ang) * r * 0.9, y + math.sin(ang) * r * 0.9)))
    return join(*parts)


def compass_fn(x, y, r, color=BLACK, width=8):
    """罗盘描出来：先铺白底（盖住身后的线），再逐段描框，返回笔尖。"""
    path = compass(x, y, r)

    def fn(c, k, t):
        c.drawCircle(x, y, r, K.paint(PAPER, clamp01(k * 3)))
        part, tip = partial(path, k)
        c.drawPath(part, K.paint(color, 1, width))
        return tip

    return fn


def draw_needle(c, x, y, r, a):
    ca, sa = math.cos(a), math.sin(a)
    ln, w = r * 0.78, r * 0.2
    tip, tail = (x + ca * ln, y + sa * ln), (x - ca * ln, y - sa * ln)
    s1, s2 = (x - sa * w, y + ca * w), (x + sa * w, y - ca * w)
    K.poly(c, [tip, s1, s2], RED)
    K.poly(c, [tail, s1, s2], BLACK)
    K.dot(c, x, y, r * 0.1, PAPER)


def needle_fn(x, y, r, plan, a0=1.2):
    """罗盘指针，按绝对时间走：plan 为 [(镜头, 拍, 动作, 目标角)]，动作 spin = 乱转、stop = “叮”一声停在目标角。"""

    def angle(t):
        a, t_prev, mode = a0, None, "rest"
        for jj, kk, act, aim in plan:
            tk = b.t_of(jj, kk)
            if t < tk:
                break
            if mode == "spin":                     # 上一段在乱转：停下时接住当时的角度
                a = a + 7.5 * (tk - t_prev) + 0.9 * math.sin(6.1 * (tk - t_prev))
            t_prev, mode = tk, act
            if act == "stop":
                a = aim
        if t_prev is None:
            return a0
        dt = t - t_prev
        if mode == "spin":
            return a + 7.5 * dt + 0.9 * math.sin(6.1 * dt)
        return a + 0.45 * math.exp(-6 * dt) * math.sin(22 * dt)

    def fn(c, k, t):
        if k > 0:
            draw_needle(c, x, y, r * min(1.0, 0.4 + k), angle(t))
        return None

    return fn


def big_arrow_fn(a, z, bend, flip_at, dur=0.55):
    """大问号箭头：从 a 描到 z；到 flip_at=(镜头, 拍) 时绕中点整根转半圈调头，颜色变红。"""
    path = arrow(a, z, bend, 60)
    mx, my = (a[0] + z[0]) / 2, (a[1] + z[1]) / 2

    def fn(c, k, t):
        tf = b.t_of(*flip_at)
        f = ease_in_out(clamp01((t - tf) / dur)) if t >= tf else 0.0
        part, tip = partial(path, k)
        if f > 0:
            m = skia.Matrix()
            m.setRotate(180 * f, mx, my)
            part = skia.Path(part)
            part.transform(m)
        color = RED if f > 0.5 else BLACK
        c.drawPath(part, K.paint(color, 1, 12))
        c.drawPath(part, K.paint(color, 0.22, 5, blur=1.2))
        return tip

    return fn


def fill_fn(path, color, alpha=0.3):
    def fn(c, k, t):
        c.drawPath(path, K.paint(color, alpha * k))
        return None

    return fn


def note_fn(x, y, w, h):
    """黄便签：底色渐显 + 描边 + 一条胶带，返回笔尖。"""
    edge = rect(x, y, w, h, 6)

    def fn(c, k, t):
        c.drawPath(edge, K.paint(NOTE, 0.9 * clamp01(k * 2)))
        part, tip = partial(edge, k)
        c.drawPath(part, K.paint("#B8962A", 1, 6))
        if k >= 1:
            K.rr(c, x, y - h / 2, 150, 44, 4, "#D9D4C7", 0.8)
        return tip

    return fn


def person_shape(x, y, s=1.0) -> skia.Path:
    """拼图块上的人形：头 + 肩身，(x, y) 为格子中心。"""
    return join(circle(x, y - 45 * s, 32 * s), rect(x, y + 25 * s, 100 * s, 80 * s, 30 * s))


def piece_fn(x0, y0, x1, y1, slide):
    """阿宁形状的拼图块：在 (x0, y0) 描出来，slide=(镜头, 拍0, 拍1) 时滑进 (x1, y1) 的空位。"""
    shape = person_shape(0, 0)

    def fn(c, k, t):
        ta, tb = b.t_of(slide[0], slide[1]), b.t_of(slide[0], slide[2])
        f = ease_in_out(clamp01((t - ta) / max(1e-3, tb - ta)))
        x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        p = skia.Path(shape)
        p.offset(x, y)
        c.drawPath(p, K.paint(BLUE, 0.3 * k))
        part, tip = partial(p, k)
        c.drawPath(part, K.paint(BLUE, 1, 8))
        return tip

    return fn


def books(x, y) -> skia.Path:
    """一摞书：(x, y) 为最下面一本的中心。"""
    parts = []
    for i, (dx, w) in enumerate(((0, 220), (12, 200), (-8, 210))):
        cy = y - i * 56
        parts += [rect(x + dx, cy, w, 50, 6), P((x + dx - w / 2 + 24, cy - 25), (x + dx - w / 2 + 24, cy + 25))]
    return join(*parts)


def chessboard(x, y, n=4, cell=125) -> skia.Path:
    half = n * cell / 2
    parts = [rect(x, y, n * cell, n * cell, 4)]
    for i in range(1, n):
        parts.append(P((x - half + i * cell, y - half), (x - half + i * cell, y + half)))
        parts.append(P((x - half, y - half + i * cell), (x + half, y - half + i * cell)))
    return join(*parts)


def checker(x, y, n=4, cell=125) -> skia.Path:
    half = n * cell / 2
    p = skia.Path()
    for r in range(n):
        for col in range(n):
            if (r + col) % 2:
                p.addRect(skia.Rect.MakeXYWH(x - half + col * cell, y - half + r * cell, cell, cell))
    return p


def pawn(x, y, s=1.0) -> skia.Path:
    """棋子：圆头 + 梯形身子 + 底座，(x, y) 为格子中心。"""
    return join(circle(x, y - 28 * s, 18 * s), P((x - 14 * s, y - 10 * s), (x - 26 * s, y + 26 * s),
                                                  (x + 26 * s, y + 26 * s), (x + 14 * s, y - 10 * s)),
                P((x - 36 * s, y + 38 * s), (x + 36 * s, y + 38 * s)))


def alarm(x, y, r=130) -> skia.Path:
    """闹钟：表盘 + 指针 07:30 + 两只铃 + 两条腿。"""
    bells = []
    for sx in (-1, 1):
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(x + sx * r * 0.62 - r * 0.32, y - r * 1.0 - r * 0.2, r * 0.64, r * 0.64), 180, 180)
        p.close()
        bells.append(p)
    return join(clock(x, y, r), hands_at(x, y, r, 7, 30), *bells,
                P((x - r * 0.6, y + r * 0.8), (x - r * 0.85, y + r * 1.15)),
                P((x + r * 0.6, y + r * 0.8), (x + r * 0.85, y + r * 1.15)))


def strike(x, w, y) -> skia.Path:
    return underline(x - w / 2, x + w / 2, y, 8, 50)


# ---------------------------------------------------------------- 开局：半夜一问（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

NING = (1000, 1450, 0.9)                 # 阿宁：脚底与比例
CHEST = (1000, 1300, 42)                 # 胸前罗盘
ARR_A, ARR_Z, BEND = (1040, 1100), (1810, 880), -0.4
BOX = (1960, 880)

scene("半夜刷到这句", "深夜一问", (820, 1080, 0.85), bars=2)
L(moon(450, 720, 80), 0, 0.9, BLACK, 9, sfx="wood_high")
T("00:40", 450, 900, 60, k0=1, k1=2, sfx="pop")
L(phone(760, 1230), 2, 2.9, BLACK, 9, sfx="wood_high")
T("人生有什么", 760, 1180, 52, k0=3, k1=4.2, sfx="pop")
T("意义？", 760, 1270, 52, k0=4.2, k1=5)
L(mirror(stick(*NING, "hold"), NING[0]), 5, 5.7, BLUE, 10, sfx="wood_low")
L(face(*NING, "flat"), 5.7, 6.0, BLUE, 8)

J_ASK = scene("我图啥？答不上", "深夜一问", (1380, 1080, 0.68))
J_DROP = J_ASK + 2
C(0, 0.9, big_arrow_fn(ARR_A, ARR_Z, BEND, (J_DROP, 0)), sfx="wood_high")
T("图啥？", 1380, 700, 80, RED, k0=1.5, k1=2.5)
H(2, "pop")
L(rect(*BOX, 280, 160, 20), 3, 3.7, BLACK, 9, sfx="wood_low")
T("生活", BOX[0], BOX[1], 80, k0=4, k1=4.8, sfx="pop")
C(5, 5.9, compass_fn(*CHEST, BLUE, 7), sfx="wood_high")
C(6, 6.4, needle_fn(*CHEST, [(J_ASK, 6, "spin", 0), (J_ASK, 11, "rest", 0), (J_DROP, 2, "spin", 0),
                              (J_DROP, 3, "stop", 0.0)]), sfx="shaker")

# ---------------------------------------------------------------- 书中观点（场景 3–7）

scene("书里说问反了", "活出生命的意义 · 书中观点", (1380, 1100, 0.68))
L(book(1920, 1330, 340, 230), 0, 0.9, sfx="wood_low")
T("活出生命的意义", 1920, 1110, 60, GREEN, k0=1, k1=2.75, sfx="pop")
T("弗兰克尔", 1920, 1530, 58, k0=3, k1=4, sfx="pop")
L(join(P((1250, 645), (1510, 755)), P((1510, 645), (1250, 755))), 5, 5.7, RED, 11, sfx="rim")
T("问反了", 1620, 680, 66, RED, k0=6, k1=6.9, sfx="ding")

scene("生活在问你", "书中观点 · 被问的人", (1380, 1150, 0.68), shake=[0], flashes=[0])
b.hit(J(), 0, "kick", 1.0, "箭头调头")
T("生活在问你", 1470, 1290, 84, RED, k0=1, k1=2.25, sfx="pop")
H(3, "ding")                                                  # 罗盘指针停下，指向“生活在问你”
T("！", 945, 1050, 90, BLUE, k0=4, k1=4.8, sfx="pop")
T("你用行动回答", 1470, 1420, 66, k0=5, k1=6.5, sfx="pop")
L(underline(1270, 1670, 1350, 10, 40), 7, 7.8, RED, 7, sfx="wood_high")

M1, M2 = (850, 2950), (1450, 2950)
scene("有人在等，有书没写", "书中观点 · 营里的两个人", (1150, 2700, 0.65))
L(join(stick(*M1, 0.8), stick(*M2, 0.8)), 0, 0.9, GRAY, 9, sfx="wood_high")
L(join(face(*M1, 0.8, "sad"), face(*M2, 0.8, "sad")), 0.9, 1.0, GRAY, 7)
T("都说没指望了", 1150, 2450, 70, GRAY, k0=1, k1=2.5, sfx="pop")
L(stick(540, 2850, 0.42, hair=True), 3, 3.8, RED, 8, sfx="wood_high")
T("孩子在等", 540, 2620, 62, RED, k0=4, k1=5, sfx="pop")
L(books(1750, 2910), 5, 5.8, RED, 8, sfx="wood_low")
T("书没写完", 1750, 2650, 62, RED, k0=6, k1=7, sfx="pop")

PZ = (2600, 2650)                       # 拼图中心：3×2 格，每格 200
HOLE = (2800, 2550)                     # 右上格空着，留出一个人形
CELLS = [(2400, 2550), (2600, 2550), (2400, 2750), (2600, 2750), (2800, 2750)]
scene("这事只有你能做", "书中观点 · 替不了", (2780, 2700, 0.8))
L(join(rect(*PZ, 600, 400, 8), P((2500, 2450), (2500, 2850)), P((2700, 2450), (2700, 2850)),
       P((2300, 2650), (2900, 2650))), 0, 0.9, BLACK, 9, sfx="wood_high")
cells = skia.Path()
for cx, cy in CELLS:
    cells.addRect(skia.Rect.MakeXYWH(cx - 100, cy - 100, 200, 200))
C(1, 1.8, fill_fn(cells, GRAY, 0.22), sfx="pop")
L(person_shape(*HOLE), 2, 2.8, BLACK, 6, sfx="wood_low")
L(rect(3200, 2950, 180, 180, 8), 3, 3.7, GRAY, 8, sfx="wood_high")
T("别人", 3200, 2950, 56, GRAY, k0=3.7, k1=4.5)
L(join(P((3120, 2870), (3280, 3030)), P((3280, 2870), (3120, 3030))), 5, 5.6, RED, 10, sfx="rim")
C(6, 6.6, piece_fn(3200, 2560, HOLE[0], HOLE[1], (J(), 6.6, 7.0)), sfx="pop")
H(7, "ding")
T("只有你能做", 2600, 3030, 76, RED, k0=7, k1=8)

CB = (950, 3920)
scene("要看这一盘", "书中观点 · 这一盘", (1100, 3960, 0.8))
T("世上哪步棋最好？", 1100, 3500, 70, k0=0, k1=2, sfx="pop")
L(chessboard(*CB), 2, 2.9, BLACK, 8, sfx="wood_high")
C(2.9, 3.0, fill_fn(checker(*CB), GRAY, 0.18))
L(join(pawn(762, 3732), pawn(1012, 3732), pawn(1137, 3857), pawn(762, 4107)), 3, 3.8, GRAY, 7, sfx="pop")
L(pawn(887, 3982, 1.15), 4, 4.8, RED, 9, sfx="wood_low")
L(arrow((905, 3940), (1120, 3745), -0.2, 34), 5, 5.7, RED, 8, sfx="wood_high")
T("这一步", 1440, 3740, 70, RED, k0=6, k1=6.8, sfx="ding")

# ---------------------------------------------------------------- 三组改写（场景 8–10）：原话划掉 → 新问法

CARDS = [(1250, 5100), (2450, 5100), (1250, 6200)]
CMP = (2450, 6200, 190)                 # 三组改写连到的罗盘


def card(n, label, old, new, size=60):
    """改写卡片（z≈0.85 版）：框 → 标签 → 原话泡泡 → 划掉 → 箭头 → 新问法。"""
    x, y = CARDS[n]
    L(rect(x, y, 900, 800, 30), 0, 0.7, GRAY, 6, sfx="wood_high")
    T(label, x, y - 300, 64, BLUE, k0=1, sfx="pop")
    L(bubble(x, y - 110, 720, 150, -1), 2, 2.6, BLACK, 8, sfx="wood_low")
    T(old, x, y - 110, size, GRAY, k0=2.6, k1=4.6)
    L(strike(x, 0.95 * len(old) * size, y - 110), 5, 5.4, RED, 9, sfx="rim")
    L(arrow((x, y - 10), (x, y + 70), 0, 30), 5.4, 5.9, RED, 8)
    T(new, x, y + 150, 64, RED, k0=6, k1=8, sfx="pop")


scene("谁在等这张单", "改写① · 上班", (1250, 5100, 0.85))
card(0, "改写① · 上班", "这破工作有啥意义", "今天这张单，谁在等？")

scene("今天谁需要我", "改写② · 家里", (2450, 5100, 0.85))
card(1, "改写② · 家里", "我混成这样有啥用", "今天家里谁需要我？")

J_LINK = scene("落到我头上，怎么接", "改写③ · 倒霉事", (1800, 5810, 0.45))
x3, y3 = CARDS[2]
L(rect(x3, y3, 900, 800, 30), 0, 0.7, GRAY, 6, sfx="wood_high")
T("改写③ · 倒霉事", x3, y3 - 310, 80, BLUE, k0=1, k1=2, sfx="pop")
L(bubble(x3, y3 - 130, 640, 170, -1), 2, 2.5, BLACK, 8, sfx="wood_low")
T("凭什么是我", x3, y3 - 130, 88, GRAY, k0=2.5, k1=3.7)
L(strike(x3, 470, y3 - 130), 4, 4.4, RED, 10, sfx="rim")
T("落到我头上", x3, y3 + 120, 88, RED, k0=5, k1=6, sfx="pop")
T("我怎么接？", x3, y3 + 240, 88, RED, k0=6, k1=7)
L(join(arrow((1700, 5420), (2300, 6040), 0.1, 50), arrow((2450, 5500), (2450, 5920), 0, 50),
       arrow((1700, 6200), (2230, 6200), 0, 50)), 7, 7.7, GREEN, 10, sfx="wood_high")
C(7.7, 8.0, compass_fn(*CMP, BLACK, 10))
C(8, 8.2, needle_fn(*CMP, [(J_LINK, 8, "spin", 0), (J_LINK, 9, "stop", math.pi)]))
H(9, "ding")

# ---------------------------------------------------------------- 三步做法（场景 11–13）

scene("早上换个问法", "做法① · 早上", (1000, 7600, 0.85))
T("① 早上换个问法", 1000, 7150, 72, BLUE, k0=0, k1=2, sfx="pop")
L(alarm(680, 7600), 2, 2.9, BLACK, 9, sfx="wood_high")
T("07:30", 680, 7850, 60, k0=3, k1=4, sfx="pop")
C(4, 4.8, note_fn(1250, 7600, 440, 380), sfx="wood_low")
T("今天", 1250, 7530, 64, k0=5, k1=5.8, sfx="pop")
T("谁在等我？", 1250, 7650, 64, RED, k0=5.8, k1=7.05)

scene("答案写成动作", "做法② · 写成动作", (2600, 7600, 0.85))
T("② 答案写成动作", 2600, 7150, 72, BLUE, k0=0, k1=2, sfx="pop")
T("多上点心", 2250, 7400, 60, GRAY, k0=2, k1=3, sfx="pop")
L(strike(2250, 250, 7400), 3, 3.4, RED, 9, sfx="rim")
L(arrow((2300, 7470), (2490, 7640), 0.1, 30), 3.4, 3.9, GREEN, 8)
C(4, 4.8, note_fn(2780, 7700, 520, 380), sfx="wood_low")
T("10:00", 2780, 7630, 80, RED, k0=5, k1=6.25, sfx="pop")
T("回完客户", 2780, 7770, 64, k0=6.25, k1=7.25)

ME = (2200, 9150, 0.7)
scene("晚上看答了没", "做法③ · 晚上", (2600, 8800, 0.85))
T("③ 晚上看一眼", 2600, 8350, 72, BLUE, k0=0, k1=1.6, sfx="pop")
L(moon(2150, 8580, 70), 1.6, 2.4, BLACK, 8)
C(2, 2.8, note_fn(2750, 8800, 520, 380), sfx="wood_low")
T("10:00", 2750, 8730, 80, RED, k0=3, k1=4, sfx="pop")
T("回完客户", 2750, 8870, 64, k0=4, k1=4.9)
L(check(2950, 8930, 70), 5, 5.6, GREEN, 14, sfx="ding")
L(stick(*ME), 6, 6.7, BLUE, 9, sfx="wood_high")
L(face(*ME, "smile"), 6.7, 6.9, BLUE, 7)
C(7, 7.6, compass_fn(2200, 9000, 34, BLUE, 6))
C(7.6, 7.8, needle_fn(2200, 9000, 34, [(J(), 7.6, "spin", 0), (J(), 8, "stop", -0.35)]))
H(8, "ding", 0.6)

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：拉远看全板 → 推到评论区

FAR = (1800, 4880, 0.108)
END = (1000, 8950, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, END, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("今天生活问了你什么？", 1000, 8850, 76, RED, k0=6, k1=8.5, sfx="pop")
T("下一讲：意义从哪来？书里给了三条路", 1000, 9030, 50, k0=9, k1=13, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "ask", "生活在发问", "别再问图啥，生活在问你", ACC, b.shots,
                 [f"{BOOK}第一部分 在集中营的经历；第二部分 意义疗法·生命之意义（转述）",
                  "Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010"],
                 "别再问图啥|生活在【问你】", SQUARE_SHOT,
                 ["书中观点为转述：视角的翻转——要紧的在于生活对我们有什么期待，我们是被生活提问的一方，要用行动来回答；"
                  "营里两个人都说对生活没什么指望了，作者提醒他们，一个人有孩子在国外等他，另一个人有一套书还没写完，"
                  "这件事只有他能做、别人替不了。以上见第一部分〈在集中营的经历〉。意义因人、因时而不同，问人生的意义像问棋手"
                  "世上最好的一步棋，要看这一盘、这一刻；人是被生活提问的人。见第二部分〈生命之意义〉。上屏均为转述，不是逐字引文。"
                  "出处：Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010。",
                  "营里两个人只画灰线小人、远处的孩子和一摞书，不画营地细节；“对生活没指望了”为转述，上屏不出现相关敏感词。",
                  "深夜刷手机、问号箭头调头、拼图、棋盘为示意画法；三组改写（上班、家里、倒霉事）为示意，不指向任何具体公司"
                  "或个人；“00:40”“07:30”“10:00 回完客户”为示意时间，不是数据。",
                  "三步做法（早上换一个具体问题问自己、把答案写成一个动作、晚上看一眼答了没）为据书中思路整理的建议。"],
                 tags="#人生意义 #自我成长")
    return b.attach(ep)
