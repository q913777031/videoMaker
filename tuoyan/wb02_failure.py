"""02 怕做砸（白板手绘版）：拖到最后，是给自己留台阶。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：最后 4 拍不出新笔画）。
叙事（I 一个等式讲完）：白板正中只有一个等式，整讲往它上面加东西、划东西、拆开——
打工人开局（周日晚上十点才打开汇报 PPT → 周一讲得一般，一句“我昨晚才弄的”就过去了）→
书中观点（亮书《拖延心理学》，博克和袁；很多拖延的人心里有个等式“我 = 能力 = 这份方案”，drop 时红字逐块砸下；
反过来，方案差就等于我差，所以输不起；拖到最后，结果差可以怪没时间，能力没被真正比过，“本来能做好”的想法保住了）→
身边的例子（想考证总说准备好了再报；简历改了半年没投出去；两条绿箭头都连回中央等式）→
具体做法（划开两个等号，把“我这个人”和“这一次”分开看 / 先交七十分版，再改 / 复盘只说事，别说人）→
拉远看全板 → 评论区互动。明天怪兽在等号上探头、在考证例子里撕日历。
书中观点为转述（Jane B. Burka & Lenora M. Yuen, Procrastination: Why You Do It, What to Do About It Now, 2008 修订版，
第2章；中译本《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009，第2章“审问拖延：被架在审判席上的失败恐惧症”）；
例子与做法为示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, clock,
                               desk, doc, face, hands_at, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#C84B3C"
SQUARE_SHOT = 3                 # 场景 4（drop）：红字等式 + 小周举着方案

b = Board(size=(3600, 6600))


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


# ---------------------------------------------------------------- 本讲画法

def badge(x, y, s=1.0) -> skia.Path:
    """配合 stick 的工牌（挂绳 + 卡片）：(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 22 * s, hy + 45 * s), (x + 18 * s, hy + 130 * s), (x + 30 * s, hy + 45 * s)),
                rect(x + 18 * s, hy + 155 * s, 38 * s, 50 * s, 5 * s))


def zhou(x, y, s=0.75, arms="down", mood="flat") -> skia.Path:
    """小周：火柴人 + 胸前工牌。"""
    return join(stick(x, y, s, arms), face(x, y, s, mood), badge(x, y, s))


def monster(x, y, r) -> skia.Path:
    """明天怪兽：毛茸茸的一团 + 两只圆眼 + 小手攥着一张日历页（“明天”二字另写）。"""
    pts = []
    n = 44
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = r * (1.12 if i % 2 else 1.0)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    parts = [P(*pts, close=True)]
    for dx in (-0.33, 0.33):
        parts += [circle(x + dx * r, y - 0.3 * r, 0.2 * r), circle(x + dx * r + 0.04 * r, y - 0.28 * r, 0.07 * r)]
    parts += [P((x - 1.05 * r, y + 0.1 * r), (x - 1.35 * r, y - 0.2 * r)),
              P((x + 1.05 * r, y + 0.1 * r), (x + 1.3 * r, y - 0.05 * r)),
              rect(x + 1.55 * r, y - 0.15 * r, 0.5 * r, 0.6 * r, 6), P((x + 1.3 * r, y - 0.33 * r), (x + 1.8 * r, y - 0.33 * r))]
    return join(*parts)


def belly(x, y, r, k0, k1=None, sfx=None):
    T("明天", x, y + 0.4 * r, 0.48 * r, RED, k0=k0, k1=k1, sfx=sfx)


def eq_sign(x, y, w=70) -> skia.Path:
    return join(P((x - w / 2, y - 16), (x + w / 2, y - 16)), P((x - w / 2, y + 16), (x + w / 2, y + 16)))


def slash(x, y, h=150) -> skia.Path:
    return P((x - 45, y + h / 2), (x + 45, y - h / 2))


def plank(x, y, w=60, h=360) -> skia.Path:
    """挡板：竖着插进等式的一块木板（几道木纹）。"""
    return join(rect(x, y, w, h, 6), P((x - 10, y - h / 2 + 50), (x - 10, y - 30)), P((x + 12, y + 20), (x + 12, y + h / 2 - 40)))


def corners(x, y, w, h, d=60) -> skia.Path:
    """取景框四个角：白板正中留出的空位。"""
    l, r, t, bt = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    return join(P((l, t + d), (l, t), (l + d, t)), P((r - d, t), (r, t), (r, t + d)),
                P((r, bt - d), (r, bt), (r - d, bt)), P((l + d, bt), (l, bt), (l, bt - d)))


def envelope(x, y, w=260, h=170) -> skia.Path:
    return join(rect(x, y, w, h, 8), P((x - w / 2, y - h / 2), (x, y + 10), (x + w / 2, y - h / 2)))


def loop_arrow(x, y, r=45) -> skia.Path:
    """转一圈的箭头（再改一遍）。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -60, 300)
    ex, ey = x + r * math.cos(math.radians(240)), y + r * math.sin(math.radians(240))
    return join(p, P((ex - 28, ey - 6), (ex, ey), (ex + 6, ey - 30)))


def rays(x, y, r0, r1, n=8, a0=0) -> skia.Path:
    parts = []
    for i in range(n):
        a = math.radians(a0 + i * 360 / n)
        parts.append(P((x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))))
    return join(*parts)


def glow_fn(x, y, r, color="#F2C14E"):
    """气泡后面慢慢亮起来的一团光。"""

    def fn(c, k, t):
        c.drawCircle(x, y, r * (0.4 + 0.6 * ease_out(k)), K.paint(color, 0.55 * k, blur=50))
        return None

    return fn


def note_fn(x, y, w, h):
    """黄便利贴底色。"""

    def fn(c, k, t):
        K.rr(c, x, y, w, h, 8, "#FFE27A", 0.9 * k)
        return None

    return fn


def pages_fn(x0, y0, dests):
    """怪兽手里的日历页一张张被撕下，飘到地上。"""

    def fn(c, k, t):
        for i, (x1, y1, rot) in enumerate(dests):
            f = clamp01(k * len(dests) - i * 0.6)
            if f <= 0:
                continue
            e = ease_in_out(f)
            x = lerp(x0, x1, e)
            y = lerp(y0, y1, e) - 120 * math.sin(math.pi * e)
            c.save()
            c.translate(x, y)
            c.rotate(rot * e + 25 * math.sin(f * 9) * (1 - e))
            c.drawPath(rect(0, 0, 70, 84, 6), wb.marker(BLACK, 6))
            c.drawPath(P((-35, -26), (35, -26)), wb.marker(RED, 6))
            c.restore()
        return None

    return fn


# ---------------------------------------------------------------- 等式的位置（白板正中）

EQY = 2900
SIZE = 120
EQ = {}                          # 名称 → 中心 x
_x = 1830 - (120 + 240 + 480 + 2 * 70 + 4 * 60) / 2
for name, w in (("我", 120), ("=1", 70), ("能力", 240), ("=2", 70), ("这份方案", 480)):
    EQ[name] = _x + w / 2
    _x += w + 60
ZX, ZY = EQ["这份方案"], 3560     # 小周站在“这份方案”下面
MON = (EQ["=1"], 2650, 115)      # 明天怪兽蹲在第一个等号上
VEQ = (1830, 2930, 0.7)          # 看整个等式的视角

# ---------------------------------------------------------------- 开局：汇报前一晚（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

b.shot("汇报前一晚才动", "汇报前夜", (900, 850, 0.85), bars=2)
L(desk(900, 1050, 460), 0, 0.9, sfx="wood_high")
L(zhou(620, 1300, 0.8, "hold"), 1, 1.9, sfx="wood_high")
L(join(clock(1250, 520, 90), hands_at(1250, 520, 90, 22, 0)), 2, 2.8, sfx="pop")
T("22:00", 1250, 680, 64, RED, k0=3, k1=3.8, sfx="pop")
T("周日晚上", 600, 560, 64, k0=4, k1=5, sfx="pop")
b.custom(J(), 5, 5.4, note_fn(1300, 880, 230, 160))
L(rect(1300, 880, 230, 160, 8), 5, 5.5, ORANGE, 7, sfx="wood_high")
T("明早汇报", 1300, 880, 50, k0=5.2, k1=6)

b.shot("讲砸了还有理由", "汇报前夜", (2600, 850, 0.85))
L(join(rect(2760, 600, 500, 280, 10), P((2760, 740), (2760, 820)), P((2680, 820), (2840, 820))), 0, 0.9,
  sfx="wood_high")
T("周一汇报", 2760, 600, 64, k0=1, k1=2, sfx="pop")
L(zhou(2200, 1260, 0.75, "point"), 2, 2.9, sfx="wood_high")
L(bubble(2200, 870, 390, 130, 1), 3, 3.7, BLACK, 8, sfx="pop")
T("我昨晚才弄的", 2200, 870, 50, k0=3.7, k1=5.2)
L(join(stick(3000, 1260, 0.75, "down"), face(3000, 1260, 0.75, "smile")), 5.5, 6.4, BLUE, 9)
H(6, "wood_high")
L(join(P((3075, 1000), (3095, 1030)), P((3075, 1050), (3095, 1080))), 6.4, 6.9, BLUE, 7)
T("嗯嗯", 3150, 960, 56, BLUE, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- 书中观点：一个等式（场景 3–7）

b.shot("书里写了个等式", "拖延心理学 · 书中观点", (1800, 2650, 0.75))
L(book(1300, 2350, 340, 230), 0, 0.9, sfx="wood_low")
T("《拖延心理学》", 2050, 2330, 68, GREEN, k0=1, k1=2.75, sfx="pop")
T("博克和袁", 2050, 2440, 56, k0=3, k1=4, sfx="pop")
L(corners(1830, EQY, 1400, 280), 5, 5.9, BLUE, 8, sfx="wood_high")
L(join(*[P((EQ[n] - w / 2, EQY + 75), (EQ[n] + w / 2, EQY + 75)) for n, w in (("我", 120), ("能力", 240), ("这份方案", 480))]),
  6, 6.8, BLACK, 6, sfx="pop")
L(join(eq_sign(EQ["=1"], EQY), eq_sign(EQ["=2"], EQY)), 7, 7.6, BLACK, 7, sfx="wood_high")

b.shot("做得好就等于我好", "书中观点 · 心里的等式", VEQ, shake=[0], flashes=[0])
T("我", EQ["我"], EQY, SIZE, RED, k0=0, k1=0.8, sfx="kick")
L(eq_sign(EQ["=1"], EQY), 1, 1.6, RED, 14, sfx="pop")
T("能力", EQ["能力"], EQY, SIZE, RED, k0=2, k1=2.8, sfx="kick")
L(eq_sign(EQ["=2"], EQY), 3, 3.6, RED, 14, sfx="pop")
T("这份方案", EQ["这份方案"], EQY, SIZE, RED, k0=4, k1=5, sfx="kick")
L(zhou(ZX, ZY, 0.75, "up"), 5.2, 6.1)
H(5, "wood_high")
L(doc(ZX, 3215, 150, 120, 3), 6, 6.8, BLACK, 8, sfx="pop")
L(rays(ZX, 3215, 105, 140, 8, 22), 7, 7.8, RED, 7, sfx="ding")

b.shot("做砸就等于我不行", "书中观点 · 输不起", VEQ)
T("方案差", 1250, 3330, 76, k0=0, k1=0.8, sfx="pop")
L(arrow((1400, 3330), (1580, 3330), 0, 34), 1, 1.7, RED, 9, sfx="wood_high")
T("我差", 1680, 3330, 76, RED, k0=2, k1=2.8, sfx="pop")
L(monster(*MON), 4, 4.9, BLACK, 8, sfx="wood_low")
belly(*MON, k0=5, k1=5.8, sfx="pop")
T("输不起", 1450, 3520, 90, RED, k0=6, k1=6.8, sfx="ding")
L(underline(1320, 1580, 3580, 10, 30), 7, 7.8, RED, 7, sfx="rim")

b.shot("拖着就没真比过", "书中观点 · 拖到最后", (2000, 2930, 0.75))
L(plank(EQ["=2"], EQY), 0, 0.9, ORANGE, 10, sfx="wood_low")
T("没时间", EQ["=2"], 3150, 64, RED, k0=1, k1=1.8, sfx="pop")
L(join(clock(EQ["=2"], 2640, 75), hands_at(EQ["=2"], 2640, 75, 11, 55)), 2, 2.9, BLACK, 8, sfx="wood_high")
L(rays(EQ["=2"], 2640, 92, 120, 6, -90), 4, 4.7, RED, 6, sfx="shaker")
L(underline(EQ["=2"] - 100, EQ["=2"] + 100, 3195, 8, 25), 5, 5.7, RED, 7, sfx="ding")
T("结果差，怪时间", 1500, 2560, 56, BLUE, k0=6, k1=7.75, sfx="pop")

b.shot("我本来能做好", "书中观点 · 本来能行", (2150, 2850, 0.8))
b.custom(J(), 0, 1.5, glow_fn(2350, 2600, 230), sfx="ding")
L(bubble(2350, 2600, 360, 140, -1), 1, 1.8, BLUE, 8, sfx="pop")
T("本来能行", 2350, 2600, 64, BLUE, k0=2, k1=3, sfx="pop")
L(rays(2350, 2600, 215, 250, 10, 0), 4, 4.8, ORANGE, 6, sfx="wood_high")
L(P((EQ["能力"] - 140, EQY + 105), (EQ["能力"] + 140, EQY + 105)), 6, 6.6, BLUE, 8, sfx="pop")
T("没被考过", EQ["能力"], EQY + 160, 52, BLUE, k0=6.6, k1=7.6)

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

b.shot("证书一直不报名", "例子 · 考证", (900, 4650, 0.85))
L(rect(720, 4520, 440, 300, 14), 0, 0.9, BLACK, 9, sfx="wood_high")
T("考证报名", 720, 4430, 60, k0=1, k1=2, sfx="pop")
L(rect(720, 4590, 180, 70, 12), 2, 2.6, BLUE, 8, sfx="pop")
T("提交", 720, 4590, 46, BLUE, k0=2.6, k1=3.4)
L(zhou(1250, 5000, 0.75, "shrug"), 3, 3.9, sfx="wood_high")
L(bubble(1250, 4520, 380, 130, -1), 4, 4.7, BLACK, 8, sfx="pop")
T("准备好再报", 1250, 4520, 52, k0=4.7, k1=6)
MON8 = (560, 4950, 150)
L(monster(*MON8), 6, 6.9, BLACK, 9, sfx="wood_low")
belly(*MON8, k0=7, k1=7.8)
b.custom(J(), 7, 8.6, pages_fn(MON8[0] + 1.55 * 150, MON8[1] - 0.15 * 150,
                               [(880, 5130, -20), (970, 5110, 35), (1060, 5140, -50)]), sfx="shaker")

b.shot("简历一直不投", "例子 · 简历", (2700, 4650, 0.85))
L(doc(2450, 4700, 340, 440, 6), 0, 0.9, BLACK, 9, sfx="wood_high")
T("简历", 2450, 4410, 56, k0=1, k1=1.8, sfx="pop")
for n, (cx, cy) in enumerate(((2400, 4570), (2480, 4720), (2390, 4860))):
    L(circle(cx, cy, 42), 2 + n, 2.6 + n, RED, 7, sfx="pop" if n < 2 else "rim")
T("改了半年", 3000, 4500, 60, RED, k0=5, k1=6, sfx="pop")
L(envelope(3000, 4780), 6, 6.8, BLACK, 9, sfx="wood_high")
T("没寄出", 3000, 4960, 60, k0=7, k1=7.8, sfx="rim")

b.shot("背后是同一个等式", "例子 · 同一个等式", (1800, 3700, 0.33))
L(arrow((850, 4360), (1160, 3010), 0, 60), 1, 1.9, GREEN, 14, sfx="wood_high")
L(arrow((2600, 4380), (2480, 3010), 0, 60), 2, 2.9, GREEN, 14, sfx="wood_high")
T("同一个等式", 1800, 4200, 130, RED, k0=4, k1=5.25, sfx="pop")
L(underline(1480, 2120, 4300, 16, 50), 6, 6.8, RED, 12, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

b.shot("把等号划开", "第一步 · 划开等号", VEQ)
L(slash(EQ["=1"], EQY), 0, 0.5, RED, 14, sfx="rim")
L(slash(EQ["=2"], EQY, 130), 1, 1.5, RED, 14, sfx="rim")
L(rect(EQ["我"], EQY, 210, 200, 20), 2, 2.8, BLUE, 9, sfx="wood_high")
L(rect(EQ["这份方案"], EQY, 530, 200, 20), 3, 3.9, BLUE, 9, sfx="wood_high")
T("我这个人", EQ["我"], 3075, 56, BLUE, k0=4, k1=5, sfx="pop")
T("这一次", EQ["这份方案"], 3075, 56, BLUE, k0=5, k1=5.8, sfx="pop")
L(join(P((1590, 3300), (1770, 3360)), P((1590, 3360), (1770, 3300))), 6, 6.7, RED, 10, sfx="rim")

b.shot("先交个能用的", "第二步 · 先交再改", (2650, 3250, 0.7))
NX, NY = 2950, 3450
b.custom(J(), 0, 0.5, note_fn(NX, NY, 300, 220))
L(rect(NX, NY, 300, 220, 8), 0, 0.9, ORANGE, 8, sfx="wood_high")
T("先交", NX, NY - 50, 60, k0=1, k1=1.8, sfx="pop")
T("七十分版", NX, NY + 45, 60, RED, k0=2, k1=3, sfx="pop")
L(arrow((NX - 160, NY - 70), (ZX + 95, 3230), 0.1, 34), 4, 4.8, GREEN, 9, sfx="wood_high")
L(check(ZX, 3215, 40), 5, 5.6, GREEN, 10, sfx="ding")
L(loop_arrow(NX - 70, 3690), 6, 6.6, BLUE, 8, sfx="pop")
T("再改", NX + 40, 3690, 60, BLUE, k0=6.6, k1=7.4)

b.shot("说事别说人", "第三步 · 说事别说人", (700, 3100, 0.85))
L(rect(600, 3100, 440, 560, 14), 0, 0.9, BLACK, 9, sfx="wood_high")
T("复盘", 600, 2900, 64, k0=1, k1=1.8, sfx="pop")
T("我不行", 600, 3010, 64, k0=2, k1=2.8, sfx="pop")
L(join(P((490, 3000), (710, 3020)), P((490, 3025), (710, 3005))), 3, 3.6, RED, 10, sfx="rim")
T("第三页", 600, 3130, 64, BLUE, k0=4, k1=4.8, sfx="pop")
T("数据不对", 600, 3230, 64, BLUE, k0=5, k1=6, sfx="pop")
L(check(760, 3320, 36), 7, 7.6, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 3300, 0.15)
COMMENT = (1800, 5800, 0.8)
b.shot("你在拖哪件事", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你在拖哪件事？", 1800, 5700, 76, RED, k0=6, k1=8, sfx="pop")
T("下一讲：做得太好，怕以后都得这么好", 1800, 5860, 50, k0=9, k1=13.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "failure", "怕做砸", "拖到最后，是给自己留台阶", ACC, b.shots,
                 [f"{BOOK}第2章（中译本“审问拖延：被架在审判席上的失败恐惧症”，英文版 Fear of Failure，转述）",
                  "中译本：《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009；原书 Da Capo Lifelong Books 2008 修订版"],
                 "拖到最后|是给自己【留台阶】", SQUARE_SHOT,
                 ["书中观点为转述：很多拖延的人心里有个等式——自我价值 = 能力 = 表现，做出来的东西就等于“我这个人值多少”；"
                  "拖到最后再做，结果不好时可以归到时间不够上，能力就没被真正检验，“我本来能做好”的想法被保住了；"
                  "书里主张把自我价值和一次表现分开看（第2章）。上屏句子均为口语转述，不是逐字引文；"
                  "“我 = 能力 = 这份方案”是把书中等式套到汇报场景里的示意写法。",
                  "周日晚上赶汇报 PPT、“我昨晚才弄的”、考证总说准备好了再报、简历改了半年没投，均为现实场景示意，"
                  "不指向任何具体公司或个人；时间与“半年”为示意，不是数据。",
                  "三步做法（划开等号，把“我这个人”和“这一次”分开看；先交七十分版再改；复盘只说事、别说人）"
                  "为据书中思路整理的建议，“七十分”是示意，不是书中数字。",
                  "明天怪兽、挡板、发光气泡等为本系列的画面比喻。"],
                 tags="#完美主义 #害怕失败")
    return b.attach(ep)
