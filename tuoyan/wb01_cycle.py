"""01 拖延的圈（白板手绘版）：说好早点开始，又拖到半夜。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，最后 4 拍不出新笔画）。
叙事（B 一个故事贯穿）：小周周一接到“周五交方案”，一周的故事沿白板外圈顺时针走一圈——
周一拍胸口“早点开始”→ 周二周三刷手机、“还有四天”，明天怪兽第一次冒头 → 亮书《拖延心理学》，书里画了个圈 →
（drop）周四深夜一个字没写，明天怪兽一下顶到天花板 → 骂自己“我怎么回事”→ 岔路口：熬夜赶还是交白卷 →
周五凌晨交了，发誓“再也不拖了”→ 绿箭头沿白板左边绕回周一：下个任务又是“这次早点开始”。
外圈走完，白板正中画出书里的那个圈：七站（早点开始 → 得开始了 → 要是不开始 → 还有时间 → 我有毛病 → 做不做 →
再也不拖）；拖延替人挡着更怕的东西（怪兽张开手臂挡在小周和方案之间）；做法：卡住时先认出自己在哪站、
在“还有时间”那站先写个标题；圈被切开一个口，怪兽缩小一圈 → 拉远看全板 → 评论区：你常卡在哪站。
书中观点为转述（Jane B. Burka & Lenora M. Yuen, Procrastination: Why You Do It, What to Do About It Now, 2008 修订版，
第 1 章；中译本《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009）；小周的一周为示意，做法据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, clock,
                               cross, desk, doc, face, hands_at, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, lerp

from .common import BOOK, episode

ACC = "#C8553D"
SQUARE_SHOT = 10                # 场景 11：圈连好，小周站在圈里，怪兽蹲在“还有时间”那站

b = Board(size=(3600, 5800))


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


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def calendar(x0, y0, n=5, w=160, h=140) -> skia.Path:
    """一排日历格：左上角 (x0, y0)，顶上一条装订线。"""
    parts = [rect(x0 + n * w / 2, y0 + h / 2, n * w, h, 10), P((x0, y0 + 34), (x0 + n * w, y0 + 34))]
    for i in range(1, n):
        parts.append(P((x0 + i * w, y0), (x0 + i * w, y0 + h)))
    return join(*parts)


def phone(x, y, w=60, h=100) -> skia.Path:
    return join(rect(x, y, w, h, 10), P((x - 10, y + h / 2 - 14), (x + 10, y + h / 2 - 14)))


def badge(x, y) -> skia.Path:
    """工牌：挂绳 + 小卡片，(x, y) 为卡片中心。"""
    return join(P((x - 14, y - 50), (x, y - 26), (x + 14, y - 50)), rect(x, y, 38, 48, 6))


def note(x, y, w=320, h=170) -> skia.Path:
    """便利贴：右下角折一下。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 34), (x + w / 2 - 34, y + h / 2),
                  (x - w / 2, y + h / 2), close=True), P((x + w / 2, y + h / 2 - 34), (x + w / 2 - 34, y + h / 2 - 34),
                                                         (x + w / 2 - 34, y + h / 2)))


def ring_arc(x, y, r, start=-60, sweep=300) -> skia.Path:
    """带箭头的一段弧（书里那个圈的开头）。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), start, sweep)
    a = math.radians(start + sweep)
    ex, ey = x + r * math.cos(a), y + r * math.sin(a)
    tx, ty = -math.sin(a), math.cos(a)          # 顺时针切线方向
    for d in (0.5, -0.5):
        ca, sa = math.cos(d), math.sin(d)
        dx, dy = tx * ca - ty * sa, tx * sa + ty * ca
        p.moveTo(ex, ey)
        p.lineTo(ex - 50 * dx, ey - 50 * dy)
    return p


def cloud(x, y, w=460, h=220) -> skia.Path:
    """乌云：圆角底 + 三个鼓包取并集的外轮廓；字写在 (x, y + 0.2h) 附近。"""
    p = rect(x, y + 0.2 * h, w, 0.6 * h, 0.3 * h)
    for bx, by, br in ((-0.22, -0.02, 0.32), (0.08, -0.14, 0.42), (0.3, 0.04, 0.28)):
        p = skia.Op(p, circle(x + bx * w, y + by * h, br * h), skia.PathOp.kUnion_PathOp)
    return p


def rain(x, y, n=4, gap=70, length=90) -> skia.Path:
    return join(*[P((x - (n - 1) * gap / 2 + i * gap, y + (i % 2) * 20),
                    (x - (n - 1) * gap / 2 + i * gap - 22, y + length + (i % 2) * 20)) for i in range(n)])


def bolt(x, y, s=1.0) -> skia.Path:
    return P((x + 25 * s, y - 80 * s), (x - 30 * s, y + 5 * s), (x + 12 * s, y + 5 * s), (x - 22 * s, y + 80 * s))


def sweat(x, y, s=1.0) -> skia.Path:
    """头两边的慌张短线。"""
    return join(P((x - 70 * s, y), (x - 105 * s, y - 30 * s)), P((x - 75 * s, y + 40 * s), (x - 115 * s, y + 40 * s)),
                P((x + 70 * s, y), (x + 105 * s, y - 30 * s)), P((x + 75 * s, y + 40 * s), (x + 115 * s, y + 40 * s)))


def pin(x, y, r=34) -> skia.Path:
    """地图定位针：尖端在 (x, y)。"""
    cy = y - 2.4 * r
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, cy - r, 2 * r, 2 * r), 150, 240)
    p.moveTo(x + r * math.cos(math.radians(30)), cy + r * math.sin(math.radians(30)))
    p.lineTo(x, y)
    p.lineTo(x + r * math.cos(math.radians(150)), cy + r * math.sin(math.radians(150)))
    return join(p, circle(x, cy, r * 0.35))


def fork(x, y0, y1, dx=320, top=None) -> skia.Path:
    """岔路：从 (x, y0) 往上到分叉点 (x, y1)，再分向左上、右上。"""
    top = top if top is not None else y1 - 240
    return join(P((x, y0), (x, y1)), P((x, y1), (x - dx, top)), P((x, y1), (x + dx, top)))


# ---------------------------------------------------------------- 明天怪兽（系列角色）

def monster_path(x, y, s=1.0, arms="down") -> tuple[skia.Path, float, float, float]:
    """明天怪兽：毛茸茸的一团，两只圆眼，右手攥一张日历页。(x, y) 为脚底中点；返回（轮廓, 身体圆心 x, y, 半径）。"""
    R = 150 * s
    cx, cy = x, y - 1.06 * R
    body = skia.Path()
    n = 16
    body.moveTo(cx + R, cy)
    for i in range(n):
        a1, am = 2 * math.pi * (i + 1) / n, 2 * math.pi * (i + 0.5) / n
        body.quadTo(cx + 1.14 * R * math.cos(am), cy + 1.14 * R * math.sin(am), cx + R * math.cos(a1), cy + R * math.sin(a1))
    ey = cy - 0.35 * R
    parts = [body, circle(cx - 0.33 * R, ey, 0.17 * R), circle(cx + 0.33 * R, ey, 0.17 * R),
             P((cx - 0.5 * R, y + 0.02 * R), (cx - 0.2 * R, y + 0.02 * R)),
             P((cx + 0.2 * R, y + 0.02 * R), (cx + 0.5 * R, y + 0.02 * R))]
    if arms == "raise":
        hl, hr = (cx - 1.25 * R, cy - 0.6 * R), (cx + 1.12 * R, cy - 0.62 * R)
        parts += [P((cx - 0.98 * R, cy - 0.1 * R), hl), P((cx + 0.98 * R, cy - 0.15 * R), hr)]
    elif arms == "open":
        hl, hr = (cx - 1.5 * R, cy - 0.55 * R), (cx + 1.5 * R, cy - 0.55 * R)
        parts += [P((cx - 0.98 * R, cy - 0.1 * R), hl), P((cx + 0.98 * R, cy - 0.1 * R), hr)]
    else:
        hl, hr = (cx - 1.3 * R, cy + 0.55 * R), (cx + 1.28 * R, cy + 0.2 * R)
        parts += [P((cx - 0.95 * R, cy + 0.25 * R), hl), P((cx + 0.97 * R, cy + 0.05 * R), hr)]
    if arms == "raise":                                  # 举手慌叫时日历页不画
        return join(*parts), cx, cy, R
    px, py = (hr[0], hr[1] - 0.2 * R) if arms == "open" else (hr[0] + 0.25 * R, hr[1] - 0.12 * R)   # 日历页
    pw, ph = 0.42 * R, 0.5 * R
    parts += [rect(px, py, pw, ph, 0.05 * R), P((px - pw / 2, py - ph / 2 + 0.13 * R), (px + pw / 2, py - ph / 2 + 0.13 * R))]
    return join(*parts), cx, cy, R


def draw_monster(c, x, y, s=1.0, arms="down", k=1.0):
    """把明天怪兽画到白板上：k<1 时按进度描轮廓（返回笔尖），最后写上肚皮的红字“明天”。"""
    path, cx, cy, R = monster_path(x, y, s, arms)
    width = max(6.0, 9 * min(1.0, s)) + 3 * max(0.0, s - 1)
    part, tip = wb.partial(path, clamp01(k / 0.85))
    c.drawPath(part, wb.marker(BLACK, width))
    c.drawPath(part, K.paint(BLACK, 0.22, width * 0.45, blur=1.2))
    if k > 0.6:
        for dx in (-0.33, 0.33):
            K.dot(c, cx + dx * R + 0.04 * R, cy - 0.33 * R, 0.075 * R, BLACK)
    if k > 0.85:
        K.text(c, "明天", cx, cy + 0.3 * R, 0.55 * R, "hand", RED, clamp01((k - 0.85) / 0.15))
    return tip if k < 0.85 else None


def monster_fn(x, y, s=0.6, arms="down"):
    def fn(c, k, t):
        return draw_monster(c, x, y, s, arms, k)

    return fn


# ---------------------------------------------------------------- 外圈：小周的一周（场景 1–8，顺时针）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

ZS = (330, 1400)                # 小周（周一）
scene("这次早点开始", "周一上午 · 接活", (560, 900, 0.85), bars=2)
L(calendar(160, 470), 0, 0.9, sfx="wood_high")
T("周一", 240, 550, 50, k0=1, sfx="pop")
T("周五", 880, 550, 50, RED, k0=2, sfx="pop")
L(join(stick(*ZS, 0.85, "hold"), badge(ZS[0] + 2, ZS[1] - 135)), 3, 3.8, sfx="wood_high")
L(face(*ZS, 0.85, "smile"), 3.8, 4.0)
L(note(760, 1060, 340, 180), 4, 4.4, ORANGE, 9, sfx="pop")
T("早点开始", 750, 1050, 60, k0=4.4, k1=5.4)
L(oval(880, 545, 190, 170), 5.4, 5.9, RED, 8)

ZT = (1480, 1400)               # 小周（周二周三）
scene("还有四天呢", "周二周三 · 先忙别的", (1800, 900, 0.85))
L(desk(1880, 1150, 420), 0, 0.9, sfx="wood_high")
L(stick(*ZT, 0.8, "hold"), 1, 1.8, sfx="wood_high")
L(face(*ZT, 0.8, "smile"), 1.8, 2.0)
L(phone(ZT[0] + 108, ZT[1] - 180), 2, 2.6, BLUE, 8, sfx="pop")
L(bubble(1520, 800, 400, 150, -1), 3, 3.3, BLACK, 8, sfx="pop")
T("还有四天", 1520, 800, 60, k0=3.3, k1=4.3)
b.custom(J(), 5, 6, monster_fn(2240, 1400, 0.6), sfx="tom")
T("周二周三", 2120, 560, 56, k0=6, sfx="pop")
L(P((1990, 562), (2250, 552)), 7, 7.5, RED, 9, sfx="rim")

scene("书里画了个圈", "拖延心理学 · 书中观点", (3040, 900, 0.85))
L(book(2830, 860, 380, 260), 0, 0.9, sfx="wood_low")
T("拖延心理学", 2830, 640, 64, GREEN, k0=1, sfx="pop")
T("博克和袁", 2830, 1090, 52, k0=2.25, k1=3.25)
L(ring_arc(3290, 870, 170), 3, 3.9, BLACK, 10, sfx="wood_high")
T("圈", 3290, 870, 120, RED, k0=4, sfx="ding")
T("拖延的人在绕圈", 3040, 1290, 60, k0=5, sfx="pop")

# drop：周四深夜，明天怪兽一下顶到天花板
ROOM = dict(wall=2720, ceil=2370, floor=2980, right=3600)
MB = (3290, ROOM["floor"])      # 大怪兽脚底
ZN = (2830, ROOM["floor"])      # 缩在墙角的小周


def burst_fn(c, k, t):
    s = lerp(0.6, 1.9, 1 - (1 - k) ** 3)
    draw_monster(c, *MB, s, "raise", 1.0)
    return None


scene("周四夜里慌了", "周四深夜", (3080, 2580, 0.85), shake=[0, (2, 18.0)], flashes=[0])
L(join(P((ROOM["wall"], ROOM["floor"]), (ROOM["wall"], ROOM["ceil"]), (ROOM["right"], ROOM["ceil"])),
       P((ROOM["wall"], ROOM["floor"]), (ROOM["right"], ROOM["floor"]))), 0, 0.5, BLACK, 9)
b.custom(J(), 0, 2, burst_fn, sfx="kick")
H(2, "tom", 0.9)
L(join(clock(2820, 2470, 70), hands_at(2820, 2470, 70, 11, 0)), 3, 3.9, BLACK, 8, sfx="wood_high")
T("23:00", 2820, 2600, 56, RED, k0=4, sfx="pop")
L(stick(*ZN, 0.5, "shrug"), 5, 5.8, BLUE, 8, sfx="wood_low")
L(face(*ZN, 0.5, "sad"), 5.8, 6.0, BLUE, 7)
T("慌", 2810, 2710, 64, RED, k0=6, sfx="rim")
L(sweat(ZN[0], ZN[1] - 150, 0.6), 7, 7.6, BLUE, 7, sfx="pop")

ZC = (2950, 4520)               # 小周（骂自己）
scene("我怎么又这样", "周四深夜 · 骂自己", (3040, 4000, 0.85))
L(stick(*ZC, 0.85, "down"), 0, 0.9, sfx="wood_high")
L(face(*ZC, 0.85, "sad"), 0.9, 1.0)
L(cloud(2950, 3900, 480, 230), 1, 1.9, BLUE, 9, sfx="pop")
L(rain(2950, 4040), 2, 2.6, BLUE, 7, sfx="shaker")
T("我怎么回事", 2950, 3955, 58, k0=3, sfx="pop")
T("又拖了", 3330, 4250, 64, RED, k0=5, sfx="rim")
L(bolt(3240, 4100, 0.6), 6, 6.6, RED, 9, sfx="tom")

scene("做，还是不做", "周五凌晨 · 最后关头", (1800, 4000, 0.85))
L(fork(1800, 4280, 4100, 330, 3860), 0, 0.9, BLACK, 12, sfx="wood_high")
L(stick(1800, 4540, 0.6, "shrug"), 1, 1.8, sfx="wood_low")
L(face(1800, 4540, 0.6, "flat"), 1.8, 2.0)
T("熬夜赶", 1450, 3770, 64, k0=2, sfx="pop")
T("交白卷", 2150, 3770, 64, k0=3, sfx="pop")
L(oval(1450, 3800, 300, 190), 5, 5.8, RED, 9, sfx="ding")
L(P((2040, 3772), (2260, 3762)), 6, 6.5, RED, 10, sfx="rim")

ZF = (720, 4520)                # 小周（发誓）
scene("赶完发誓再也不拖", "周五凌晨 · 交了", (560, 4000, 0.85))
L(join(clock(300, 3610, 90), hands_at(300, 3610, 90, 4, 0)), 0, 0.9, BLACK, 8, sfx="wood_high")
T("周五凌晨", 300, 3800, 54, k0=1, sfx="pop")
L(doc(300, 4170, 180, 220), 3, 3.8, BLACK, 8, sfx="wood_low")
L(check(300, 4180, 60), 4, 4.5, GREEN, 11, sfx="ding")
L(stick(*ZF, 0.8, "up"), 5, 5.8, sfx="wood_high")
L(face(*ZF, 0.8, "smile"), 5.8, 6.0)
L(note(720, 3810, 400, 170), 6, 6.4, ORANGE, 9, sfx="pop")
T("再也不拖了", 715, 3800, 56, k0=6.4)

scene("下周又从头来", "下一个任务", (560, 2550, 0.55))
L(arrow((230, 3330), (230, 1730), 0.06, 80), 0, 1.0, GREEN, 14, sfx="wood_high")
L(doc(640, 2370, 220, 280), 2, 2.9, BLACK, 9, sfx="wood_low")
T("下个任务", 640, 2110, 90, k0=3, sfx="pop")
T("这次早点开始", 640, 2700, 86, BLUE, k0=5, sfx="pop")
L(underline(400, 880, 2775), 7, 7.8, RED, 9, sfx="rim")

# ---------------------------------------------------------------- 正中：书里的圈（场景 9–13）

C, RR = (1800, 2720), 450
STATIONS = ["早点开始", "得开始了", "要是不开始", "还有时间", "我有毛病", "做不做", "再也不拖"]
LS = 68                         # 站名字号（全圈视角 z≈0.62 时屏上 ≈42px）


def station(i):
    a = math.radians(-90 + i * 360 / 7)
    return a, C[0] + RR * math.cos(a), C[1] + RR * math.sin(a)


def label_pos(i):
    a, _, _ = station(i)
    w = K.text_w(STATIONS[i], LS, "hand")
    ax, ay = C[0] + (RR + 48) * math.cos(a), C[1] + (RR + 48) * math.sin(a)
    return ax + math.cos(a) * w / 2, ay + math.sin(a) * LS * 0.55


def big_ring() -> skia.Path:
    parts = [circle(*C, RR)]
    for i in range(7):
        _, x, y = station(i)
        parts.append(circle(x, y, 20))
        am = math.radians(-90 + (i + 0.5) * 360 / 7)          # 两站中间一个顺时针箭头
        mx, my = C[0] + RR * math.cos(am), C[1] + RR * math.sin(am)
        tx, ty = -math.sin(am), math.cos(am)
        for d in (0.55, -0.55):
            ca, sa = math.cos(d), math.sin(d)
            dx, dy = tx * ca - ty * sa, tx * sa + ty * ca
            parts.append(P((mx, my), (mx - 40 * dx, my - 40 * dy)))
    return join(*parts)


scene("圈上有七站", "书中观点 · 拖延的圈", (1830, 2740, 0.62))
L(big_ring(), 0, 1.0, BLACK, 10, sfx="wood_high")
for i, s in enumerate(STATIONS):
    x, y = label_pos(i)
    T(s, x, y, LS, BLUE if i == 3 else (RED if i == 6 else BLACK), k0=1 + i, sfx="ding" if i == 3 else "pop")

ZI = (1560, 3000)               # 圈里的小周
DOC = (2085, 2900)
M0, M1 = (1830, 3000), (2350, 3290)       # 怪兽：挡在中间 → 跳到“还有时间”那站


def guard_fn(c, k, t):
    """圈里的明天怪兽：场景 10 张开手臂挡着；场景 11 第 0–1 拍跳到“还有时间”那站；场景 13 第 2–3 拍缩小一圈。"""
    ta, tb = b.t_of(J_HERE, 0), b.t_of(J_HERE, 1)
    tc, td = b.t_of(J_CUT, 2), b.t_of(J_CUT, 3)
    if t < ta:
        x, y, s, arms = *M0, 0.72, "open"
    elif t < tb:
        f = ease_in_out(clamp01((t - ta) / (tb - ta)))
        x, y = lerp(M0[0], M1[0], f), lerp(M0[1], M1[1], f) - 260 * 4 * f * (1 - f)
        s, arms = lerp(0.72, 0.6, f), "down"
    elif t < tc:
        x, y, s, arms = *M1, 0.6, "down"
    else:
        f = ease_in_out(clamp01((t - tc) / (td - tc)))
        x, y, s, arms = *M1, lerp(0.6, 0.4, f), "down"
    return draw_monster(c, x, y, s, arms, k)


scene("拖着能躲一会儿", "书中观点 · 拖延在挡着", (1867, 2770, 0.7))
L(stick(*ZI, 0.6, "down"), 0, 0.9, sfx="wood_high")
L(face(*ZI, 0.6, "flat"), 0.9, 1.0)
L(join(doc(*DOC, 140, 180, lines=0), P((DOC[0] - 45, DOC[1] + 25), (DOC[0] + 45, DOC[1] + 25)),
       P((DOC[0] - 45, DOC[1] + 60), (DOC[0] + 30, DOC[1] + 60))), 1, 1.8, BLACK, 8, sfx="wood_low")
T("方案", DOC[0] - 5, DOC[1] - 30, 56, k0=2, sfx="pop")
b.custom(J(), 3, 4, guard_fn, sfx="tom")
T("替你挡着", 1800, 2485, 72, RED, k0=5, sfx="ding")

J_HERE = scene("先认出你在哪站", "做法一 · 认出在哪站", (1830, 2820, 0.64))
H(0, "wood_low")
H(1, "tom", 0.9)
L(arrow((1630, 3030), (1965, 3100), -0.12, 34), 2, 2.9, GREEN, 9, sfx="wood_high")
L(pin(ZI[0], 2765), 3, 3.8, RED, 9, sfx="pop")
T("你在这", ZI[0], 2595, 66, RED, k0=5, sfx="pop")
L(underline(ZI[0] - 95, ZI[0] + 95, 2640, 8, 30), 6, 6.6, RED, 7, sfx="ding")

ST4 = label_pos(3)
scene("在还有时间那站动", "做法二 · 先动一小块", (1830, 2820, 0.64))
L(oval(2200, ST4[1] - 10, 640, 270), 0, 0.9, RED, 9, sfx="ding")
L(arrow((2140, ST4[1] + 125), (2110, ST4[1] + 215), 0.2, 30), 1, 1.6, GREEN, 9, sfx="wood_high")
L(note(2100, ST4[1] + 290, 320, 140), 2, 2.4, ORANGE, 9, sfx="pop")
T("先写标题", 2090, ST4[1] + 280, 62, k0=2.4, k1=3.4)
L(check(2300, ST4[1] + 225, 40), 4, 4.5, GREEN, 10, sfx="pop")

GAP = (C[0], C[1] + RR)
J_CUT = scene("圈就松了一截", "做法二 · 圈断开了", (1830, 2820, 0.62))
b.erase(J(), 0, 0.6, GAP[0], GAP[1], 90, 80)
H(0, "shaker")
L(P((GAP[0] - 70, GAP[1] - 80), (GAP[0] + 70, GAP[1] + 80)), 1, 1.5, RED, 11, sfx="rim")
H(2, "tom", 0.7)
T("断开一个口", 1450, 3390, 66, RED, k0=4, sfx="pop")
L(arrow((1630, 3035), (GAP[0] + 10, GAP[1] + 120), -0.25, 34), 6, 6.9, GREEN, 9, sfx="wood_high")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 2480, 0.24)
CMT = (1800, 5150, 0.85)
J_END = scene("你常卡在哪站", "评论区见", FAR, bars=4)
b.move(J_END, 4, CMT, 1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(bubble(1800, 4960, 720, 170, -1), 5, 5.5, BLACK, 8, sfx="pop")
T("你常卡在哪站？", 1800, 4960, 80, RED, k0=6, sfx="pop")
T("下一讲：拖到最后，是给自己留台阶", 1800, 5200, 52, k0=9, k1=13.0, sfx="wood_high")
L(P((1390, 5250), (2210, 5250)), 13, 13.8, BLACK, 6)
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "cycle", "拖延的圈", "说好早点开始，又拖到半夜", ACC, b.shots,
                 [f"{BOOK}第 1 章（中译本“质疑拖延：是可恶的坏习惯还是应得的报应”）：拖延的圈、拖延的保护作用（转述）",
                  "中译本：《拖延心理学》，简·博克、莱诺拉·袁著，蒋永强、陆正芳译，中国人民大学出版社 2009"],
                 "说好早点开始|又拖到【半夜】", 3,
                 ["书中观点为转述：书里描述拖延者一遍遍走的一个圈——“这次我要早点开始”→“我得赶紧开始了”→"
                  "“要是我一直不开始呢”→“还有时间”→“我是不是有什么毛病”→最后关头做还是不做→赶完之后“我再也不拖了”，"
                  "下一次又从头来；书里也说拖延有它的用处，它在保护人，免得面对更怕的东西（第 1 章）。七站站名为口语转述，"
                  "中译本措辞未逐字核对。出处：Jane B. Burka & Lenora M. Yuen, Procrastination: Why You Do It, What to Do "
                  "About It Now (Da Capo Lifelong Books, 2008 修订版)；中译本《拖延心理学》（蒋永强、陆正芳译，"
                  "中国人民大学出版社 2009）。",
                  "小周周一接活、周二周三刷手机、周四深夜发慌、周五凌晨交差的一周为示意，不指向任何具体公司或个人；"
                  "钟点、天数为示意，不是数据。明天怪兽为系列视觉角色。",
                  "两条做法（卡住时先认出自己在哪一站；在“还有时间”那站先动一小块，比如先写标题）为据书中思路整理的建议。"],
                 tags="#拖延循环 #deadline")
    return b.attach(ep)
