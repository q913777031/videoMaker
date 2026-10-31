"""07 苦难的意义（白板手绘版）：躲不开的难事，怎么扛过去？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（倒叙：先给结局，再回放那一个问题）：结局先放——一位老医生走出诊室，握了握手 → ◀◀ 倒回去：
妻子走了两年，他一直走不出来 → 他去找弗兰克尔，作者没劝，只问了一句 → drop：红色大问句砸下来
“要是你先走了，她会怎样？”，两把椅子换过来想 → 两轮对话：她会非常难受 / 这份难受她免了，是你替她扛着 →
天平两盘持平（他的痛 ↔ 她免了），老医生胸前的小罗盘停在“替她扛”（这一屏就挨着开头的结局）→
书中观点：躲不开的苦，一旦找到意义，就不再只是苦 / 能改的先改、能躲的先躲，白扛的苦不算英勇 →
两个倒着看的例子（现在陪爸复查不慌了 ◀◀ 当初爸查出病请假陪护；现在带新人讲那次失败 ◀◀ 当初项目黄了背了锅）→
做法（先分能改的 / 改不了的；改不了的问一句“我替谁扛着”；讲给一个信得过的人听，扛不住找专业帮助）→
拉远全板 → 评论区。
构图：前六屏在白板上半部先往上倒（结局在下、诊室在上），再从 drop 往下走回结局旁边，倒叙在板面上走成一个来回。
书中观点为转述（Viktor E. Frankl, Man's Search for Meaning，第二部分 意义疗法〈苦难之意义〉；
中译本《活出生命的意义》，吕娜译，华夏出版社 2010）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, bubble, check, circle, cross, doc, face,
                               join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#7A5BA6"                 # 本讲主色：暮紫
SQUARE_SHOT = 5                 # 场景 6：天平 + 老医生 + 红心 + 罗盘
GRAY = "#8A8F98"
YELLOW = "#D9A21B"

b = Board(size=(3600, 11200))


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


def slam_fn(lines, j, k_imp=0):
    """drop：几行红色大字在第 k_imp 拍从放大 1.7 倍砸到原位（lines=[(字, x, y, 字号)]）。"""
    def fn(c, k, t):
        t_imp = b.t_of(j, k_imp)
        if t < t_imp:
            return None
        f = clamp01((t - t_imp) / 0.22)
        s = 1 + 0.7 * (1 - f) ** 2
        for s_, x, y, size in lines:
            c.save()
            c.translate(x, y)
            c.scale(s, s)
            K.text(c, s_, 0, 0, size, "hand", RED, clamp01(f * 3))
            c.restore()
        return None

    return fn


def rewind(x, y, s=1.0) -> skia.Path:
    """倒带符号 ◀◀：(x, y) 为中心。"""
    return join(P((x - 100 * s, y), (x, y - 60 * s), (x, y + 60 * s), close=True),
                P((x, y), (x + 100 * s, y - 60 * s), (x + 100 * s, y + 60 * s), close=True))


def door(x, y, w=280, h=520) -> skia.Path:
    """诊室门：(x, y) 为门中心，门框 + 门板 + 把手。"""
    return join(rect(x, y, w + 40, h + 30, 6), rect(x, y + 15, w, h, 4), circle(x + w / 2 - 40, y + 30, 14))


def handshake(x, y, s=1.0) -> skia.Path:
    """两只握着的手：左右两截袖口伸过来，在 (x, y) 握在一起。"""
    parts = []
    for d in (-1, 1):
        parts += [P((x + d * 300 * s, y + 20 * s), (x + d * 110 * s, y - 10 * s)),
                  P((x + d * 300 * s, y + 120 * s), (x + d * 110 * s, y + 90 * s)),
                  P((x + d * 220 * s, y + 6 * s), (x + d * 225 * s, y + 108 * s))]
    parts.append(rect(x, y + 40 * s, 230 * s, 110 * s, 48 * s))
    for i in range(3):
        fx = x - 45 * s + i * 40 * s
        parts.append(P((fx, y - 12 * s), (fx + 8 * s, y + 30 * s)))
    thumb = skia.Path()
    thumb.moveTo(x - 40 * s, y - 12 * s)
    thumb.quadTo(x + 10 * s, y - 50 * s, x + 60 * s, y - 20 * s)
    parts.append(thumb)
    return join(*parts)


def chair(x, y, facing=1, s=1.0) -> skia.Path:
    """侧面的椅子：(x, y) 为椅子靠背那条腿的着地点，facing=1 朝右坐。"""
    f = facing
    return join(P((x, y), (x, y - 330 * s)), P((x, y - 130 * s), (x + f * 160 * s, y - 130 * s)),
                P((x + f * 160 * s, y - 130 * s), (x + f * 160 * s, y)))


def seated(x, y, facing=1, s=1.0) -> skia.Path:
    """坐在 chair(x, y, facing, s) 上的简笔小人。"""
    f = facing
    hip = (x + f * 40 * s, y - 145 * s)
    sh = (x + f * 40 * s, y - 300 * s)
    knee = (x + f * 160 * s, y - 145 * s)
    return join(circle(sh[0], sh[1] - 60 * s, 45 * s), P(hip, (sh[0], sh[1] - 15 * s)), P(hip, knee, (knee[0], y)),
                P((sh[0], sh[1] + 10 * s), (x + f * 140 * s, y - 175 * s)))


def seated_face(x, y, facing=1, s=1.0, mood="flat") -> skia.Path:
    sx = x + facing * 40 * s
    return face(sx, y - 300 * s - 60 * s + 290 * s, s, mood)


def calendar(x, y, w=300, h=280) -> skia.Path:
    return join(rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 70), (x + w / 2, y - h / 2 + 70)),
                circle(x - w / 4, y - h / 2, 12), circle(x + w / 4, y - h / 2, 12))


def heart(x, y, r=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def rock(x, y, w=300, h=180) -> skia.Path:
    """一块石头：(x, y) 为中心。"""
    pts = [(-0.5, 0.45), (-0.47, 0.0), (-0.3, -0.35), (0.0, -0.5), (0.3, -0.42), (0.5, -0.05), (0.45, 0.45)]
    return join(P(*[(x + a * w, y + c * h) for a, c in pts], close=True),
                P((x - 0.15 * w, y - 0.2 * h), (x - 0.02 * w, y - 0.05 * h)))


def dashes(x0, x1, y, n=6) -> skia.Path:
    step = (x1 - x0) / n
    return join(*[P((x0 + i * step, y), (x0 + (i + 0.55) * step, y)) for i in range(n)])


def bed(x, y, w=400) -> skia.Path:
    """病床侧面：(x, y) 为床面中点。"""
    return join(rect(x, y + 20, w, 40, 8), P((x - w / 2, y - 110), (x - w / 2, y + 120)),
                P((x + w / 2, y - 40), (x + w / 2, y + 120)), rect(x - w / 2 + 70, y - 25, 100, 50, 18),
                P((x - w / 2 + 130, y - 50), (x + w / 2 - 20, y - 50)))


def walking_pair(x, y, s=0.5) -> skia.Path:
    """两个并排走的小人（女儿扶着爸爸）：(x, y) 为两人中间的地面点。"""
    return join(stick(x - 70, y, s, "hold"), stick(x + 70, y, s * 0.95, "down"), P((x - 92, y - 150), (x + 60, y - 150)))


def teaching(x, y, s=0.45) -> skia.Path:
    """带新人：一个小人指着小黑板，旁边两个小圆脑袋。"""
    return join(stick(x - 140, y, s, "point"), rect(x + 30, y - 190, 200, 130, 8),
                P((x - 10, y - 200), (x + 70, y - 170), (x + 130, y - 200)),
                circle(x + 0, y - 20, 26), circle(x + 80, y - 20, 26))


def phone(x, y, w=90, h=150) -> skia.Path:
    return join(rect(x, y, w, h, 14), P((x - 14, y + h / 2 - 18), (x + 14, y + h / 2 - 18)))


# ---------------------------------------------------------------- 开局：结局先放（场景 1），倒回去（场景 2–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。
# 前三屏在左栏往上走：结局（y≈3700）→ 两年前（y≈2300）→ 诊室（y≈900）。

scene("他握手走了", "先看结局", (950, 3700, 0.85), bars=2)
T("先看结局", 950, 3230, 60, RED, k0=0, k1=1.0, sfx="pop")
L(door(620, 3720), 1, 1.9, BLACK, 9, sfx="wood_high")
T("诊室", 620, 3410, 50, k0=2, k1=2.8, sfx="pop")
L(handshake(1200, 3560, 0.85), 3, 3.9, BLACK, 9, sfx="wood_low")
L(stick(1080, 4180, 0.6, "down"), 4, 4.7, BLACK, 8, sfx="wood_high")
L(face(1080, 4180, 0.6, "flat"), 4.7, 4.9, BLACK, 7)
L(arrow((1180, 4090), (1420, 4090), 0.0, 36), 5, 5.8, GRAY, 8, sfx="pop")

scene("两年没走出来", "倒回去", (950, 2300, 0.85))
L(rewind(560, 1950, 0.9), 0, 0.8, RED, 10, sfx="tom")
T("倒回去", 1050, 1950, 64, RED, k0=1, k1=2, sfx="pop")
L(calendar(560, 2340), 2, 2.9, BLACK, 9, sfx="wood_low")
T("两年", 560, 2390, 80, k0=3, k1=4, sfx="pop")
L(chair(1100, 2560, -1, 1.0), 4, 4.8, GRAY, 9, sfx="wood_high")
T("妻子走后", 1000, 2700, 52, GRAY, k0=5, k1=6, sfx="pop")
T("他一直走不出来", 1000, 2800, 52, k0=6, k1=7.75, sfx="pop")

CH3L, CH3R = (560, 1260), (1340, 1260)
scene("只问了一个问题", "倒回去 · 诊室", (950, 900, 0.85))
T("他去找弗兰克尔", 950, 430, 60, k0=0, k1=1.75, sfx="pop")
L(join(chair(*CH3L, 1), seated(*CH3L, 1)), 2, 2.9, BLACK, 9, sfx="wood_high")
L(seated_face(*CH3L, 1, 1.0, "frown"), 2.9, 3.0, BLACK, 8)
L(join(chair(*CH3R, -1), seated(*CH3R, -1)), 3, 3.9, BLACK, 9, sfx="wood_low")
T("老医生", CH3L[0] + 40, 800, 50, k0=4, k1=4.8, sfx="pop")
T("弗兰克尔", CH3R[0] - 40, 800, 50, k0=5, k1=6, sfx="pop")
T("没劝，只问一句", 950, 1370, 56, RED, k0=6, k1=7.75, sfx="ding")

# drop 前：镜头先移到右栏那一屏，两把椅子提前画好，第 0 拍红色大问句砸下来
V4 = (2650, 900, 0.8)
b.move(J(), 10.0, V4, dur=0.75)

CH4L, CH4R = (2260, 1380), (3040, 1380)
scene("要是你先走了呢", "书中故事 · 一个问题", V4, shake=[0], flashes=[0])
J4 = J()
L(join(chair(*CH4L, 1), seated(*CH4L, 1)), -1.6, -0.9, BLACK, 9)
L(chair(*CH4R, -1), -0.9, -0.3, BLACK, 9)
b.custom(J4, 0, 0.3, slam_fn([("要是你先走了，", 2650, 470, 92), ("她会怎样？", 2650, 600, 92)], J4), sfx="kick")
L(dashes(2460, 2840, 1300), 2, 2.8, GRAY, 8, sfx="wood_low")
T("他", CH4L[0] + 40, 900, 60, k0=3, k1=3.8, sfx="pop")
T("她", CH4R[0] - 40, 900, 64, RED, k0=4, k1=4.8, sfx="pop")
L(arrow((2960, 1110), (2340, 1110), 0.22, 40), 5, 5.8, RED, 8, sfx="wood_high")
T("换过来想", 2650, 1450, 56, k0=6, k1=7, sfx="pop")
H(8, "ding")

scene("是你替她扛着", "书中故事 · 两轮对话", (2650, 2300, 0.85))
L(bubble(2400, 1960, 660, 170, -1), 0, 0.7, BLACK, 8, sfx="wood_high")
T("他：她会非常难受", 2400, 1960, 54, k0=1, k1=3, sfx="pop")
L(bubble(2880, 2260, 720, 170, 1), 3, 3.7, BLACK, 8, sfx="wood_low")
T("作者：这份难受她免了", 2880, 2260, 52, k0=4, k1=6, sfx="pop")
T("是你替她扛着", 2650, 2600, 76, RED, k0=6, k1=7.5, sfx="ding")
L(underline(2420, 2880, 2660, amp=6, step=40), 7.5, 8.0, RED, 7)

# 天平这一屏就挨着开头的结局（左边 x≈950 那屏）
PIV = (2810, 3420)
ARM6, HANG6 = 300, 170
COMP6 = (2230, 4075, 34)
scene("这份苦有了意义", "书中观点 · 天平", (2650, 3700, 0.85))
pans = []
for side in (-1, 1):
    px = PIV[0] + side * ARM6
    py = PIV[1] + HANG6
    pan = skia.Path()
    pan.addArc(skia.Rect.MakeXYWH(px - 120, py - 40, 240, 80), 0, 180)
    pans += [P((px - 120, py), (px, PIV[1]), (px + 120, py)), pan, P((px - 120, py), (px + 120, py))]
L(join(P((PIV[0], PIV[1]), (PIV[0], 3980)), P((PIV[0] - 150, 3980), (PIV[0] + 150, 3980)),
       P((PIV[0] - ARM6, PIV[1]), (PIV[0] + ARM6, PIV[1])), circle(PIV[0], PIV[1], 14), *pans), 0, 1.0, BLACK, 9,
  sfx="wood_low")
L(rock(PIV[0] - ARM6, PIV[1] + HANG6 - 55, 170, 100), 1, 1.7, GRAY, 9, sfx="wood_high")
T("他的痛", PIV[0] - ARM6, 3730, 50, k0=2, k1=2.8, sfx="pop")
L(heart(PIV[0] + ARM6, PIV[1] + HANG6 - 50, 50), 3, 3.7, RED, 9, sfx="pop")
T("她免了", PIV[0] + ARM6, 3730, 50, RED, k0=4, k1=4.8, sfx="pop")
T("替她扛", PIV[0], 3270, 64, RED, k0=5, k1=5.8, sfx="ding")
L(stick(2230, 4200, 0.85, "down"), 6, 6.7, BLACK, 9, sfx="wood_high")
L(face(2230, 4200, 0.85, "flat"), 6.7, 6.9, BLACK, 8)
L(compass(*COMP6), 7, 7.4, BLACK, 6, sfx="pop")
b.custom(J(), 7.4, 8.0, needle_fn(*COMP6, (PIV[0], 3250), turns=1.2))
H(8, "ding")

# ---------------------------------------------------------------- 书中观点（场景 7–8）

scene("找到意义，苦就变了", "活出生命的意义 · 书中观点", (950, 5100, 0.85))
T("躲不开的苦", 950, 4680, 66, k0=0, k1=1.25, sfx="pop")
L(rock(950, 4930, 320, 190), 1, 1.9, BLACK, 9, sfx="wood_low")
T("一旦找到意义", 950, 5200, 66, k0=2, k1=3.5, sfx="pop")
L(heart(950, 4945, 42), 4, 4.6, RED, 9, sfx="ding")
T("就不再只是苦", 950, 5390, 72, RED, k0=5, k1=6.5, sfx="pop")
L(underline(720, 1180, 5450, amp=8, step=50), 7, 7.8, RED, 8, sfx="wood_high")

scene("能躲的先躲", "活出生命的意义 · 书中观点", (2650, 5100, 0.85))
L(P((2650, 4640), (2650, 5300)), 0, 0.7, BLACK, 8, sfx="wood_low")
T("能躲的", 2330, 4700, 64, k0=1, k1=1.8, sfx="pop")
T("躲不开的", 2970, 4700, 64, k0=2, k1=3, sfx="pop")
T("先改，先躲", 2330, 4900, 56, k0=3, k1=4.25, sfx="pop")
L(check(2330, 5100, 60), 4.3, 5.0, GREEN, 10)
T("再找意义", 2970, 4900, 56, RED, k0=5, k1=6, sfx="pop")
T("白扛的苦，不算英勇", 2650, 5450, 58, k0=6, k1=8, sfx="rim")

# ---------------------------------------------------------------- 身边的例子：倒着看（场景 9–10）

scene("她现在不慌了", "例子 · 倒着看", (950, 6500, 0.85))
L(walking_pair(600, 6420, 0.55), 0, 0.9, BLACK, 8, sfx="wood_high")
T("现在陪爸复查", 600, 6560, 52, k0=1, k1=2.5, sfx="pop")
T("不慌了", 600, 6680, 62, RED, k0=3, k1=3.8, sfx="ding")
L(rewind(950, 6300, 0.6), 4, 4.6, RED, 9, sfx="tom")
L(bed(1300, 6330, 380), 5, 5.8, BLACK, 8, sfx="wood_low")
T("当初爸查出病", 1300, 6560, 52, k0=6, k1=7.5, sfx="pop")
T("她请假陪护", 1300, 6680, 52, k0=7.5, k1=8.0)

scene("那次失败讲给新人", "例子 · 倒着看", (2650, 6500, 0.85))
L(teaching(2330, 6420, 0.5), 0, 0.9, BLACK, 8, sfx="wood_high")
T("现在带新人", 2300, 6560, 52, k0=1, k1=2.25, sfx="pop")
T("讲那次失败", 2300, 6680, 58, RED, k0=3, k1=4.0, sfx="ding")
L(rewind(2650, 6300, 0.6), 4, 4.6, RED, 9, sfx="tom")
L(join(doc(3000, 6290, 150, 190, 4), cross(3000, 6290, 80)), 5, 5.8, BLACK, 8, sfx="rim")
T("当初项目黄了", 3000, 6560, 52, k0=6, k1=7.5, sfx="pop")
T("他背了锅", 3000, 6680, 52, k0=7.5, k1=8.0)

# ---------------------------------------------------------------- 具体做法（场景 11–13）

NOTE = (950, 7960, 760, 500)
scene("先分能改不能改", "做法① · 分两栏", (950, 7900, 0.85))
T("① 先分两栏", 950, 7450, 72, BLUE, k0=0, k1=1.5, sfx="pop")
b.custom(J(), 2, 2.6, fill_fn(rect(*NOTE, 12), YELLOW))
L(rect(*NOTE, 12), 2, 2.8, YELLOW, 8, sfx="pop")
L(P((NOTE[0], 7740), (NOTE[0], 8180)), 3, 3.7, BLACK, 7, sfx="wood_low")
T("能改的", 760, 7790, 54, k0=4, k1=4.8, sfx="pop")
T("改不了的", 1140, 7790, 54, k0=5, k1=6, sfx="pop")
T("下一步", 760, 7980, 50, k0=6, k1=6.8, sfx="wood_high")
T("已经发生的", 1140, 7980, 50, GRAY, k0=7, k1=8)

COMP12 = (2350, 8220, 28)
scene("我替谁扛着", "做法② · 问一句", (2650, 7900, 0.85))
T("② 改不了的", 2650, 7450, 72, BLUE, k0=0, k1=1.5, sfx="pop")
L(stick(2350, 8320, 0.8, "up"), 2, 2.8, BLUE, 10, sfx="wood_high")
L(face(2350, 8320, 0.8, "flat"), 2.8, 3.0, BLUE, 9)
L(rock(2350, 7990, 220, 110), 3, 3.7, GRAY, 9, sfx="wood_low")
L(bubble(2900, 7800, 600, 180, -1), 4, 4.7, BLACK, 8, sfx="pop")
T("我替谁扛着？", 2900, 7800, 60, RED, k0=5, k1=6.5, sfx="pop")
T("阿宁", 2350, 8400, 50, BLUE, k0=6.5, k1=7.3)
L(compass(*COMP12), 7, 7.4, BLACK, 6, sfx="wood_high")
b.custom(J(), 7.4, 8.0, needle_fn(*COMP12, (2900, 7800), turns=1.5))
H(8, "ding")

scene("讲给一个人听", "做法③ · 说出来", (950, 9300, 0.85))
T("③ 讲给信得过的人", 950, 8850, 66, BLUE, k0=0, k1=2, sfx="pop")
L(join(stick(640, 9380, 0.7, "down"), stick(1000, 9380, 0.7, "down")), 2, 2.8, BLACK, 9, sfx="wood_high")
L(join(face(640, 9380, 0.7, "flat"), face(1000, 9380, 0.7, "smile")), 2.8, 3.0, BLACK, 8)
L(bubble(560, 9020, 260, 110, 1), 3, 3.6, BLACK, 7, sfx="wood_low")
T("那件事", 560, 9020, 48, k0=3.6, k1=4.4)
L(phone(1330, 9240), 5, 5.6, BLACK, 8, sfx="pop")
T("扛不住，找专业帮助", 950, 9560, 56, RED, k0=6, k1=8, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5300, 0.16)
CMT = (1800, 10600, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(bubble(1800, 10480, 1120, 220, -1), 5, 5.8, BLACK, 8)
T("你扛过的难事，后来怎样了？", 1800, 10480, 66, RED, k0=6, k1=9, sfx="pop")
T("下一讲：越怕紧张，为什么越紧张？", 1800, 10770, 50, k0=10, k1=14, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "suffer", "苦难的意义", "躲不开的难事，怎么扛过去？", ACC, b.shots,
                 [f"{BOOK}第二部分 意义疗法〈苦难之意义〉（转述）",
                  "Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010"],
                 "躲不开的难事|怎么【扛过去】", SQUARE_SHOT,
                 ["书中观点为转述，见第二部分 意义疗法〈苦难之意义〉：一位年长的全科医生，妻子去世两年仍走不出来；"
                  "作者问他：要是你先走了，她会怎样？他说她会非常痛苦；作者说，这份痛苦她免了，是你替她扛着，"
                  "代价是你还活着思念她；他握了握作者的手，离开了。“两年”为书中所写。书中观点：苦难一旦找到意义，就不再只是苦难；"
                  "能避免的苦要先避免，没必要的受苦算不上英勇。上屏均为转述，不是逐字引文。",
                  "倒叙结构（先放握手离开的结局，再倒回那一个问题）为本讲的讲法；诊室门、两把椅子、“换过来想”的箭头、"
                  "天平（他的痛 ↔ 她免了）为对书中故事与观点的通俗化示意；不画作者肖像，只写名字“弗兰克尔”。",
                  "陪爸复查、请假陪护、带新人讲失败、项目黄了背锅均为现实场景示意，不指向任何具体公司或个人；"
                  "阿宁为示意角色。",
                  "三步做法（先分能改的 / 改不了的；改不了的问一句“我替谁扛着”；讲给一个信得过的人听）"
                  "为据书中思路整理的建议；“扛不住就找专业帮助”为本系列补充建议。"],
                 tags="#失去 #心理学")
    return b.attach(ep)
