"""08 矛盾意向（白板手绘版）：越怕紧张，为什么越紧张？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（复刻病例：先让观众猜，再揭晓）：周五要上台汇报，阿宁手心冒汗 →
猜一：一直跟自己说“别出汗”，会怎样？A 少出点 / B 出得更多（停 4 拍让人猜）→
揭晓 B，亮书（越怕一件事，越容易把它招来）→ drop：红色循环圈一圈甩出“怕 → 出汗 → 更怕”，圈里是书中那位怕出汗的年轻医生 →
猜二：作者让他怎么做？A 深呼吸 / B 想点别的 / C 故意多出汗 → 擦掉 A、B，揭晓 C：下回心里说“让大家看看我能出多少汗”→
回到循环圈：剪刀剪断，汗滴消失，小人站直（这毛病很快松开了）→ 这招叫矛盾意向：拿自己开个玩笑，和怕拉开距离 →
猜三（示意）：开会怕脸红，“别红别红”划掉，换成“来，红给你们看”→ 怕打电话结巴，先说“我说话慢，您多担待”→
做法（把怕的事说出来、夸张到好笑 / 带点笑，罗盘指回要讲的事 / 长期睡不着、心慌就去看医生）→ 拉远全板 → 评论区。
书中观点为转述（Viktor E. Frankl, Man's Search for Meaning，第二部分 作为一项技术的意义疗法；
中译本《活出生命的意义》，吕娜译，华夏出版社 2010）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, face, join,
                               rect, scribble, stick, underline)

from .common import BOOK, episode

ACC = "#3E7C8C"
SQUARE_SHOT = 3                 # 场景 4：红色循环圈“怕 → 出汗 → 更怕” + 圈里冒汗的小人
GRAY = "#8A8F98"
YELLOW = "#D9A21B"

b = Board(size=(3600, 8800))


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
        K.dot(c, x, y, r * 0.1, "#FBFBF9")
        return None

    return fn


def fill_fn(path, color, alpha=0.35):
    """把一块区域淡淡填色（便签底色），随 k 渐显。"""
    def fn(c, k, t):
        c.drawPath(path, K.paint(color, alpha * k))
        return None

    return fn


def drop(x, y, s=1.0) -> skia.Path:
    """一滴汗：上尖下圆，(x, y) 为水滴中心。"""
    p = skia.Path()
    p.moveTo(x, y - 30 * s)
    p.cubicTo(x + 8 * s, y - 12 * s, x + 22 * s, y, x + 20 * s, y + 12 * s)
    p.cubicTo(x + 18 * s, y + 30 * s, x - 18 * s, y + 30 * s, x - 20 * s, y + 12 * s)
    p.cubicTo(x - 22 * s, y, x - 8 * s, y - 12 * s, x, y - 30 * s)
    return p


def lectern(x, y, s=1.0) -> skia.Path:
    """讲台（无人）：(x, y) 为台面中点；台面 + 梯形台身 + 一支话筒。"""
    mic = join(P((x + 30 * s, y), (x + 55 * s, y - 70 * s)), circle(x + 60 * s, y - 84 * s, 14 * s))
    return join(P((x - 130 * s, y), (x + 130 * s, y)),
                P((x - 110 * s, y), (x - 80 * s, y + 260 * s), (x + 80 * s, y + 260 * s), (x + 110 * s, y)),
                P((x - 70 * s, y + 80 * s), (x + 70 * s, y + 80 * s)), mic)


def cloud(x, y, w=340, h=200, n=8) -> skia.Path:
    """一团乌云：沿椭圆一圈鼓包。"""
    p = skia.Path()
    pts = [(x + w / 2 * math.cos(2 * math.pi * i / n), y + h / 2 * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    p.moveTo(*pts[0])
    for i in range(n):
        am = 2 * math.pi * (i + 0.5) / n
        p.quadTo(x + w / 2 * 1.45 * math.cos(am), y + h / 2 * 1.45 * math.sin(am), *pts[i + 1])
    return p


def scissors(x, y, s=1.0) -> skia.Path:
    """剪刀（刀尖朝左）：(x, y) 为转轴。"""
    return join(circle(x + 75 * s, y - 30 * s, 24 * s), circle(x + 75 * s, y + 30 * s, 24 * s),
                P((x + 55 * s, y - 18 * s), (x - 100 * s, y + 14 * s)), P((x + 55 * s, y + 18 * s), (x - 100 * s, y - 14 * s)),
                circle(x, y, 6 * s))


def wobble(x, y, s=1.0) -> skia.Path:
    """小人两侧的抖动线：(x, y) 为小人脚底。"""
    parts = []
    for side in (-1, 1):
        for i in range(2):
            x0 = x + side * (105 + i * 32) * s
            y0 = y - 260 * s + i * 40 * s
            parts.append(P((x0, y0), (x0 + side * 14 * s, y0 + 22 * s), (x0, y0 + 44 * s), (x0 + side * 14 * s, y0 + 66 * s)))
    return join(*parts)


def phone(x, y, w=220, h=380) -> skia.Path:
    return join(rect(x, y, w, h, 40), P((x - 35, y + h / 2 - 45), (x + 35, y + h / 2 - 45)),
                P((x - 25, y - h / 2 + 30), (x + 25, y - h / 2 + 30)))


def clinic(x, y, w=380, h=400) -> skia.Path:
    """诊所：(x, y) 为底边中点；楼身 + 平顶檐 + 门 + 两扇窗 + 门头招牌框（十字另画）。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 30, y - h), (x + w / 2 + 30, y - h)),
                P((x - 45, y), (x - 45, y - 130), (x + 45, y - 130), (x + 45, y)),
                rect(x - w / 2 + 75, y - 190, 70, 70, 6), rect(x + w / 2 - 75, y - 190, 70, 70, 6),
                rect(x, y - h + 95, 130, 130, 10))


def plus(x, y, r=40) -> skia.Path:
    return join(P((x - r, y), (x + r, y)), P((x, y - r), (x, y + r)))


# ---------------------------------------------------------------- 开局：明天要上台（场景 1）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

NAN1 = (700, 1300)
scene("明天要上台", "开场 · 上台前", (950, 900, 0.85), bars=2)
L(join(lectern(1230, 960, 1.0), P((960, 1225), (1500, 1225))), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(*NAN1, 0.8, "down"), 1, 1.8, BLUE, 10, sfx="pop")
L(face(*NAN1, 0.8, "frown"), 1.8, 2.0, BLUE, 9)
L(join(drop(610, 1040, 0.9), drop(800, 1020, 0.9), drop(790, 1110, 0.7)), 2, 2.8, BLUE, 6, sfx="pop")
T("周五上台汇报", 1000, 620, 72, RED, k0=3, k1=4.5, sfx="pop")
T("阿宁", NAN1[0], NAN1[1] + 70, 50, BLUE, k0=5, k1=5.8, sfx="pop")

# ---------------------------------------------------------------- 猜一（场景 2）→ 揭晓 + 书中观点（场景 3）

BOX_A, BOX_B = (2400, 1170), (2920, 1170)
scene("猜一猜会怎样", "猜一猜 · 第一题", (2650, 900, 0.85))
L(stick(2130, 850, 0.55, "down"), 0, 0.8, BLUE, 8, sfx="wood_high")
L(face(2130, 850, 0.55, "frown"), 0.8, 1.0, BLUE, 7)
L(bubble(2520, 560, 600, 150, -1), 1, 1.7, BLACK, 8, sfx="pop")
T("别出汗！别出汗！", 2520, 560, 52, k0=1.7, k1=3.0)
T("会怎样？", 2900, 780, 76, RED, k0=3, k1=4, sfx="pop")
L(rect(*BOX_A, 460, 150, 20), 4, 4.6, BLACK, 8, sfx="wood_high")
T("A 少出点", BOX_A[0], BOX_A[1], 60, k0=4.6, k1=5.8)
L(rect(*BOX_B, 460, 150, 20), 6, 6.6, BLACK, 8, sfx="wood_high")
T("B 出得更多", BOX_B[0], BOX_B[1], 60, k0=6.6, k1=8.0)

scene("越怕越来", "活出生命的意义 · 书中观点", (2650, 1640, 0.85))
L(rect(*BOX_B, 520, 200, 90), 0, 0.8, RED, 9, sfx="ding")
L(book(2330, 1700, 340, 230), 1, 1.9, BLACK, 9, sfx="wood_low")
T("活出生命的意义", 2330, 1900, 50, GREEN, k0=2, k1=3.75, sfx="pop")
T("越怕一件事", 2960, 1580, 66, k0=4, k1=5.25, sfx="pop")
T("越容易招来它", 2960, 1720, 66, RED, k0=6, k1=7.5, sfx="pop")

# drop 前一拍：镜头先移到循环圈那一屏，第 0 拍红圈甩出
V4 = (2650, 2850, 0.8)
b.move(J(), 10.0, V4, dur=0.75)

# ---------------------------------------------------------------- drop：绕成一个圈（场景 4）

LC, LR = (2650, 2900), 320
NODES = [(-90, "怕"), (30, "出汗"), (150, "更怕")]
DOC = (2650, 3040)               # 圈里年轻医生的脚底
CUT = -30                        # 场景 7 剪断的位置（度）


def _ang_pt(a, r=LR):
    return LC[0] + r * math.cos(math.radians(a)), LC[1] + r * math.sin(math.radians(a))


def loop_fn(c, k, t):
    """红色循环圈：k 内一圈甩出（带放大回落）；甩完后一颗红点一直绕圈跑；场景 7 剪断后停住、变灰、留一个缺口。"""
    t_cut = b.t_of(J7, 1.8)
    f_cut = clamp01((t - t_cut) / 0.4)
    sweep = 360 * ease_in_out(k)
    s = 1 + 0.18 * (1 - k) ** 2
    c.save()
    c.translate(*LC)
    c.scale(s, s)
    c.translate(-LC[0], -LC[1])
    rr = skia.Rect.MakeXYWH(LC[0] - LR, LC[1] - LR, 2 * LR, 2 * LR)
    for col, al in ((RED, 1 - f_cut), (GRAY, f_cut)):
        if al <= 0:
            continue
        ink = K.paint(col, al, 13)
        for i, (a0, _) in enumerate(NODES):
            a1 = NODES[(i + 1) % 3][0] + (360 if i == 2 else 0)
            st, en = a0 + 24, a1 - 24
            en = min(en, -90 + sweep)
            if en <= st:
                continue
            segs = [(st, en)]
            if f_cut > 0 and st < CUT < en:          # 剪断：留一个缺口
                segs = [(st, CUT - 9), (CUT + 9, en)]
            for s0, s1 in segs:
                p = skia.Path()
                p.addArc(rr, s0, s1 - s0)
                c.drawPath(p, ink)
            if en >= a1 - 24 - 1e-6:                # 箭头（顺时针）
                ex, ey = _ang_pt(en)
                tang = math.radians(en + 90)
                for d in (0.5, -0.5):
                    c.drawPath(P((ex, ey), (ex - 46 * math.cos(tang + d), ey - 46 * math.sin(tang + d))), ink)
        for a, lab in NODES:
            if -90 + sweep >= a - 1 or a == -90:
                K.text(c, lab, *_ang_pt(a), 70, "hand", col, al)
    c.restore()
    if k >= 1:                                       # 绕圈跑的红点（剪断后停在缺口前）
        t_end = b.t_of(J4, 0.6)
        run = (min(t, t_cut) - t_end) * 200
        a = -90 + 24 + run % 360
        if f_cut < 1:
            K.dot(c, *_ang_pt(a), 16, RED, 1 - f_cut)
    return None


def sweat_fn(c, k, t):
    """医生头边的汗滴：k 内冒出来；场景 7 第 3 拍起往下掉、淡掉。"""
    t_dry = b.t_of(J7, 3)
    f = clamp01((t - t_dry) / 0.5)
    if f >= 1:
        return None
    hy = DOC[1] - 290 * 0.55
    for dx, dy, s in ((-55, -5, 0.8), (58, -15, 0.8), (52, 45, 0.6)):
        path = drop(DOC[0] + dx, hy + dy + 60 * f, s * (0.4 + 0.6 * ease_in_out(k)))
        c.drawPath(path, K.paint(BLUE, 1 - f, 6))
    return None


scene("绕成一个圈", "书中病例 · 怕出汗", V4, shake=[0], flashes=[0])
J4 = J()
b.custom(J4, 0, 0.5, loop_fn, sfx="kick")
H(1, "shaker", 0.6)
L(stick(*DOC, 0.55, "down"), 2, 2.8, BLACK, 8, sfx="wood_high")
L(face(*DOC, 0.55, "frown"), 2.8, 3.0, BLACK, 7)
b.custom(J4, 3, 3.6, sweat_fn, sfx="pop")
T("怕出汗的年轻医生", 2650, 2330, 64, k0=5, k1=7, sfx="pop")
H(7, "ding", 0.6)

# ---------------------------------------------------------------- 猜二（场景 5）→ 揭晓 C（场景 6）

V5 = (2650, 4100, 0.85)
OPTS = [(3880, "A 深呼吸"), (4080, "B 想点别的"), (4280, "C 故意多出汗")]
scene("再猜一次", "猜一猜 · 第二题", V5)
T("作者让他怎么做？", 2650, 3650, 72, k0=0, k1=2, sfx="pop")
for n, (y, lab) in enumerate(OPTS):
    L(rect(2650, y, 620, 150, 20), 2 + 2 * n, 2.6 + 2 * n, BLACK, 8, sfx="wood_high")
    T(lab, 2650, y, 60, k0=2.6 + 2 * n, k1=3.8 + 2 * n if n < 2 else 8.0)

scene("故意多出点汗", "揭晓 · 书中病例", V5)
b.erase(J(), 0, 0.8, 2650, 3980, 760, 380)
H(0, "shaker")
L(check(3060, 4280, 45), 1, 1.6, RED, 11, sfx="ding")
L(stick(2160, 4150, 0.6, "up"), 2, 2.8, BLACK, 8, sfx="wood_high")
L(face(2160, 4150, 0.6, "smile"), 2.8, 3.0, BLACK, 7)
L(bubble(2730, 3920, 900, 170, -1), 3, 3.7, BLUE, 8, sfx="pop")
T("让大家看看我能出多少汗", 2730, 3920, 54, k0=4, k1=6.75, sfx="pop")

# ---------------------------------------------------------------- 回到循环圈：剪断（场景 7）

scene("这毛病松开了", "书中病例 · 后来", V4)
J7 = J()
L(scissors(_ang_pt(CUT)[0] + 120, _ang_pt(CUT)[1] - 20, 1.1), 1, 1.8, BLACK, 8, sfx="rim")
H(3, "shaker")
b.erase(J7, 4, 4.6, DOC[0], DOC[1] - 90, 170, 230)
L(stick(*DOC, 0.55, "up"), 5, 5.8, BLACK, 8, sfx="wood_high")
L(face(*DOC, 0.55, "smile"), 5.8, 6.0, BLACK, 7)
T("很快就松开了", 2650, 3330, 66, RED, k0=6, k1=7.5, sfx="ding")

# ---------------------------------------------------------------- 书中观点：矛盾意向（场景 8）

NAN8 = (600, 3150)
scene("拿自己开个玩笑", "活出生命的意义 · 书中观点", (950, 2850, 0.85))
T("矛盾意向", 950, 2430, 110, RED, k0=0, k1=1.2, sfx="tom")
L(stick(*NAN8, 0.7, "down"), 1, 1.8, BLUE, 9, sfx="wood_high")
L(face(*NAN8, 0.7, "smile"), 1.8, 2.0, BLUE, 8)
L(cloud(1250, 2850, 340, 190), 2, 2.9, GRAY, 9, sfx="pop")
T("怕", 1250, 2850, 76, GRAY, k0=3, k1=3.8, sfx="pop")
L(join(arrow((720, 3070), (1180, 3070), 0, 36), arrow((1180, 3070), (720, 3070), 0, 36)), 4, 4.8, GREEN, 8,
  sfx="wood_low")
T("拉开距离", 950, 3160, 52, GREEN, k0=5, k1=6, sfx="pop")
T("能拿自己开玩笑", 950, 3320, 64, k0=6, k1=7.75, sfx="ding")

# ---------------------------------------------------------------- 猜三与例子（场景 9–10）

NAN9 = (520, 4400)
scene("红就红给他们看", "猜一猜 · 第三题（示意）", (950, 4200, 0.85))
T("开会怕脸红", 950, 3730, 72, k0=0, k1=1.25, sfx="pop")
L(stick(*NAN9, 0.7, "down"), 1, 1.8, BLUE, 9, sfx="wood_high")
L(face(*NAN9, 0.7, "flat"), 1.8, 2.0, BLUE, 8)
_hy9 = NAN9[1] - 290 * 0.7
L(join(circle(NAN9[0] - 22, _hy9 + 10, 7), circle(NAN9[0] + 22, _hy9 + 10, 7)), 2, 2.5, RED, 8, sfx="pop")
L(bubble(1080, 3950, 560, 150, -1), 3, 3.6, BLACK, 8, sfx="pop")
T("别红别红", 1080, 3950, 56, k0=3.6, k1=4.6)
L(scribble(1080, 3950, 520, 120, 7), 5, 5.8, RED, 7, sfx="rim")
L(bubble(1080, 4250, 620, 150, -1), 6, 6.5, BLUE, 8, sfx="pop")
T("来，红给你们看", 1080, 4250, 56, BLUE, k0=6.5, k1=8.0)

scene("先把怕说出来", "例子 · 打电话（示意）", (950, 5500, 0.85))
T("怕打电话结巴", 950, 5030, 72, k0=0, k1=1.5, sfx="pop")
L(phone(560, 5480), 2, 2.8, BLACK, 9, sfx="wood_high")
L(bubble(1130, 5400, 640, 240, -1), 3, 3.6, BLUE, 8, sfx="pop")
T("我说话慢，", 1130, 5350, 56, k0=3.6, k1=4.8)
T("您多担待", 1130, 5450, 56, k0=5, k1=6, sfx="pop")
L(underline(1010, 1250, 5500, amp=6, step=40), 6, 6.8, RED, 7, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

NOTE = (2900, 5420, 520, 300)
NAN11 = (2250, 5800)
scene("夸张到好笑", "做法① · 说夸张点", (2650, 5500, 0.85))
T("① 说出来，夸张点", 2650, 5030, 72, BLUE, k0=0, k1=2, sfx="pop")
b.custom(J(), 2, 2.6, fill_fn(rect(*NOTE, 10), YELLOW))
L(rect(*NOTE, 10), 2, 2.8, YELLOW, 8, sfx="pop")
T("我要抖成筛子", NOTE[0], NOTE[1], 56, k0=3, k1=4.5, sfx="pop")
L(stick(*NAN11, 0.7, "shrug"), 5, 5.6, BLUE, 9, sfx="wood_high")
L(join(face(*NAN11, 0.7, "smile"), wobble(*NAN11, 0.7)), 5.6, 6.0, BLUE, 7)
T("哈哈", 2420, 5470, 60, RED, k0=6, k1=6.8, sfx="pop")

NAN12 = (2250, 7050)
COMP12 = (2250, 6925, 44)
CARD = (2900, 6760)
scene("注意力回到事上", "做法② · 回到事上", (2650, 6800, 0.85))
T("② 回到要讲的事", 2650, 6330, 72, BLUE, k0=0, k1=1.75, sfx="pop")
L(stick(*NAN12, 0.75, "down"), 2, 2.8, BLUE, 9, sfx="wood_high")
L(face(*NAN12, 0.75, "smile"), 2.8, 3.0, BLUE, 8)
L(compass(*COMP12), 3, 3.6, BLACK, 7, sfx="pop")
L(join(rect(*CARD, 480, 330, 18), *[P((CARD[0] - 170, y), (CARD[0] + 170 - 50 * (i % 2), y))
                                    for i, y in enumerate((CARD[1] + 20, CARD[1] + 80, CARD[1] + 135))]),
  4, 4.8, BLACK, 8, sfx="wood_high")
T("这件事", CARD[0], CARD[1] - 85, 64, RED, k0=5, k1=5.8, sfx="pop")
b.custom(J(), 6, 7.2, needle_fn(*COMP12, (CARD[0] - 240, CARD[1]), turns=2.5))
H(6, "shaker", 0.6)
H(7, "ding")

CL = (1200, 7100)
scene("严重了就看医生", "做法③ · 看医生", (950, 6800, 0.85))
T("③ 长期睡不着、心慌", 950, 6330, 66, BLUE, k0=0, k1=2.25, sfx="pop")
L(clinic(*CL), 3, 3.9, BLACK, 9, sfx="wood_high")
L(plus(CL[0], CL[1] - 305, 38), 4, 4.6, GREEN, 14, sfx="pop")
L(stick(620, 7100, 0.7, "down"), 5, 5.8, BLUE, 9, sfx="wood_high")
L(face(620, 7100, 0.7, "flat"), 5.8, 6.0, BLUE, 8)
L(arrow((720, 6960), (960, 6960), 0, 34), 6, 6.7, GREEN, 8, sfx="wood_low")
T("去看医生", 700, 6560, 64, GREEN, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 3800, 0.24)
CMT = (1800, 8000, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(bubble(1800, 7900, 1100, 220, -1), 5, 5.8, BLACK, 8)
T("你最怕的事，能开个玩笑吗？", 1800, 7900, 70, RED, k0=6, k1=9, sfx="pop")
T("下一讲：日子一天天过去，算白过吗？", 1800, 8190, 50, k0=9, k1=13.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "paradox", "矛盾意向", "越怕紧张，为什么越紧张？", ACC, b.shots,
                 [f"{BOOK}第二部分 作为一项技术的意义疗法（转述）",
                  "Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010"],
                 "越怕紧张|为什么【越紧张】", SQUARE_SHOT,
                 ["书中观点为转述，均见第二部分 作为一项技术的意义疗法：预期焦虑会把人害怕的事招来——越怕一件事发生，越容易发生；"
                  "书中一位怕出汗的年轻医生，越怕出汗越出汗；作者建议他下次心里对自己说要让大家看看自己能出多少汗，"
                  "这毛病很快就消失了；这种办法叫矛盾意向，靠的是人能拿自己开玩笑，和自己的害怕拉开距离。"
                  "上屏均为转述，不是逐字引文；不写书里的具体出汗量。",
                  "“猜一猜”的选项（A 少出点 / B 出得更多；A 深呼吸 / B 想点别的 / C 故意多出汗）为本讲设计的互动示意，"
                  "错误选项不是书中内容；红色循环圈“怕 → 出汗 → 更怕”、剪刀剪断、乌云与“拉开距离”为对书中观点的通俗化示意；"
                  "年轻医生只画简笔小人，不画真实人物。",
                  "周五上台汇报、开会怕脸红（“来，红给你们看”）、怕打电话结巴（“我说话慢，您多担待”）均为现实场景示意，"
                  "不指向任何具体公司或个人；阿宁为示意角色。",
                  "三步做法（把怕的事说出来、夸张到好笑；说的时候带点笑，注意力回到要讲的事；长期睡不着、心慌就去看医生）"
                  "为据书中思路整理的建议；第三步“看医生”为本系列补充建议，矛盾意向不能代替专业诊疗。"],
                 tags="#焦虑 #社恐")
    return b.attach(ep)
