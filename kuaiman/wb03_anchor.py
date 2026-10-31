"""03 锚定效应（白板手绘版）：先报的数字，为什么能带偏你？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（I 数字故事，几组数字讲完一讲）：谈薪开局（HR 问期望薪资 → 谁先开口谁定调）→
书中实验（幸运转盘停在 10 / 65，再估非洲国家在联合国里的占比，两组答案 25% / 45%，drop 时指针咔哒停住、答案砸下）→
亮书（这叫锚定；快快、慢慢再画一遍）→ 书中观点（快快被锚提示，答案被锚链拽过去；慢慢从锚边挪几步就停，调整不够）→
书中例子（法官掷过 3 / 9 的骰子，判的刑期约 5 个月 / 8 个月）→ 身边的例子（划线原价、“两天能做完吧”的排期）→
三个做法（先写好底价 / 不接离谱价 / 想想它为啥不对）→ 评论区互动。
书中观点为转述（丹尼尔·卡尼曼《思考，快与慢》第 11 章 锚定效应在生活中随处可见（Anchors）；
中译本胡晓姣、李爱民、何梦莹译，中信出版社 2012）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross, face,
                               join, rect, stick, underline)
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode, kuai, man

ACC = "#2E8B6A"
SQUARE_SHOT = 3                 # 场景 4：转盘停在 10 / 65，答案 25% / 45% 砸下，快快在旁边看

b = Board(size=(3600, 10000))


def S(text, tag, view, bars=3, **kw):
    """新场景：默认 3 小节（场景 1 为 2 小节、场景 14 为 4 小节）。"""
    return b.shot(text, tag, view=view, bars=bars, **kw)


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


# ---------------------------------------------------------------- 本讲画法

def anchor(x, y, s=1.0) -> skia.Path:
    """船锚：(x, y) 为顶上圆环中心，总高约 260·s。"""
    arms = skia.Path()
    arms.moveTo(x - 130 * s, y + 130 * s)
    arms.quadTo(x - 110 * s, y + 235 * s, x, y + 240 * s)
    arms.quadTo(x + 110 * s, y + 235 * s, x + 130 * s, y + 130 * s)
    return join(circle(x, y, 22 * s), P((x, y + 22 * s), (x, y + 240 * s)),
                P((x - 65 * s, y + 60 * s), (x + 65 * s, y + 60 * s)), arms,
                P((x - 160 * s, y + 150 * s), (x - 130 * s, y + 130 * s), (x - 118 * s, y + 168 * s)),
                P((x + 160 * s, y + 150 * s), (x + 130 * s, y + 130 * s), (x + 118 * s, y + 168 * s)))


def chain(a, c, sag=90, n=11, r=13) -> skia.Path:
    """锚链：从 a 到 c 下垂的一串小圆环。"""
    (x0, y0), (x1, y1) = a, c
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag * 2
    parts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * x0 + 2 * t * (1 - t) * mx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * t * (1 - t) * my + t * t * y1
        o = skia.Path()
        if i % 2 == 0:
            o.addOval(skia.Rect.MakeXYWH(x - r * 1.5, y - r, r * 3, r * 2))
        else:
            o.addOval(skia.Rect.MakeXYWH(x - r, y - r * 1.5, r * 2, r * 3))
        parts.append(o)
    return join(*parts)


def wheel(x, y, r) -> skia.Path:
    """转盘：外圈 + 十等分刻线 + 底座。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.93)]
    for i in range(10):
        a = i / 10 * 2 * math.pi
        parts.append(P((x + math.sin(a) * r * 0.2, y - math.cos(a) * r * 0.2),
                       (x + math.sin(a) * r * 0.93, y - math.cos(a) * r * 0.93)))
    return join(*parts)


def at_value(x, y, r, v):
    """转盘上数值 v（0–100，顺时针，0 在正上方）在半径 r 处的坐标。"""
    a = v / 100 * 2 * math.pi
    return x + math.sin(a) * r, y - math.cos(a) * r


def table(x, y, w=380) -> skia.Path:
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 30, y), (x - w / 2 + 30, y + 110)),
                P((x + w / 2 - 30, y), (x + w / 2 - 30, y + 110)))


def sit_man(x, y, s=1.0) -> skia.Path:
    """慢慢坐在小凳上：(x, y) 为地面上凳子中点；头心在 y-300·s（配 face(x, y-10·s, s)）。"""
    hy = y - 300 * s
    hip = (x, y - 130 * s)
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), hip),
                P(hip, (x + 80 * s, y - 130 * s), (x + 80 * s, y)),
                P((x - 55 * s, y - 145 * s), (x, hy + 85 * s), (x + 65 * s, y - 150 * s)),
                P((x - 60 * s, y - 120 * s), (x + 60 * s, y - 120 * s)),
                P((x - 50 * s, y - 120 * s), (x - 50 * s, y)), P((x + 50 * s, y - 120 * s), (x + 50 * s, y)),
                circle(x - 16 * s, hy - 8 * s, 13 * s), circle(x + 16 * s, hy - 8 * s, 13 * s),
                P((x - 3 * s, hy - 10 * s), (x + 3 * s, hy - 10 * s)))


def foot(x, y, s=1.0) -> skia.Path:
    o = skia.Path()
    o.addOval(skia.Rect.MakeXYWH(x - 18 * s, y - 30 * s, 36 * s, 60 * s))
    return join(o, circle(x - 10 * s, y - 44 * s, 7 * s), circle(x + 8 * s, y - 46 * s, 7 * s))


def flag(x, y, h=230) -> skia.Path:
    """小旗：(x, y) 为旗杆底端，旗面朝左。"""
    return join(P((x, y), (x, y - h)), P((x, y - h), (x - 130, y - h + 40), (x, y - h + 80)))


def both_arrow(x0, x1, y, head=34) -> skia.Path:
    return join(P((x0, y), (x1, y)), P((x0 + head, y - head * 0.7), (x0, y), (x0 + head, y + head * 0.7)),
                P((x1 - head, y - head * 0.7), (x1, y), (x1 - head, y + head * 0.7)))


def judge(x, y, s=1.0) -> skia.Path:
    """法官：小人举法槌 + 面前的审判台。(x, y) 为脚底。"""
    hy = y - 290 * s
    hx, hh = x + 120 * s, hy + 60 * s
    return join(stick(x, y, s, "point", tie=True),
                P((hx, hh), (hx + 50 * s, hh - 70 * s)),
                rect(hx + 55 * s, hh - 85 * s, 90 * s, 40 * s, 8 * s),
                rect(x, y - 70 * s, 300 * s, 140 * s, 10 * s))


def die(x, y, w=110) -> skia.Path:
    return join(rect(x, y, w, w, 18), rect(x + 8, y - 8, w - 26, w - 26, 12))


def tag(x, y, w=520, h=300) -> skia.Path:
    """价签：左端尖、带孔和吊绳。(x, y) 为价签中心。"""
    return join(P((x - w / 2, y), (x - w / 2 + 90, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2),
                  (x - w / 2 + 90, y + h / 2), close=True),
                circle(x - w / 2 + 75, y, 16), P((x - w / 2 + 70, y - 16), (x - w / 2 + 10, y - h / 2 - 60)))


def sparkle(x, y, r=40) -> skia.Path:
    return join(P((x, y - r), (x, y + r)), P((x - r, y), (x + r, y)),
                P((x - r * 0.5, y - r * 0.5), (x + r * 0.5, y + r * 0.5)),
                P((x + r * 0.5, y - r * 0.5), (x - r * 0.5, y + r * 0.5)))


CAL = (1150, 5980, 480, 300)    # 排期日历：中心 x, y, 宽, 高（5 列 × 2 行）


def calendar(x, y, w, h) -> skia.Path:
    parts = [rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 70), (x + w / 2, y - h / 2 + 70)),
             P((x - w / 4, y - h / 2 - 25), (x - w / 4, y - h / 2 + 25)),
             P((x + w / 4, y - h / 2 - 25), (x + w / 4, y - h / 2 + 25))]
    for i in range(1, 5):
        xx = x - w / 2 + w * i / 5
        parts.append(P((xx, y - h / 2 + 70), (xx, y + h / 2)))
    parts.append(P((x - w / 2, y + 35), (x + w / 2, y + 35)))
    return join(*parts)


def cell(col, row):
    x, y, w, h = CAL
    return x - w / 2 + w * (col + 0.5) / 5, y - h / 2 + 70 + (h - 70) * (row + 0.5) / 2


def loop(x, y, w, h) -> skia.Path:
    """手绘圈：略微不闭合的椭圆。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), -100, 340)
    p.lineTo(x - w * 0.05, y - h / 2 - 18)
    return p


def note(x, y, w=360, h=300) -> skia.Path:
    """便利贴：右下角折起。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 60),
                  (x + w / 2 - 60, y + h / 2), (x - w / 2, y + h / 2), close=True),
                P((x + w / 2, y + h / 2 - 60), (x + w / 2 - 60, y + h / 2 - 60), (x + w / 2 - 60, y + h / 2)))


def lens(x, y, r=80) -> skia.Path:
    """放大镜：镜片中心 (x, y)，手柄朝右下。"""
    return join(circle(x, y, r), circle(x, y, r * 0.8), P((x + r * 0.72, y + r * 0.72), (x + r * 1.7, y + r * 1.7)))


def slam_fn(s, x, y, size, color=RED):
    """数字砸下：从 1.7 倍大缩到原大、由淡变实（配 kick）。"""

    def fn(c, k, t):
        f = ease_out(clamp01(k))
        K.text(c, s, x, y, size * (1.7 - 0.7 * f), "hand", color, 0.25 + 0.75 * f)
        return None

    return fn


# ---------------------------------------------------------------- 开局：谈薪（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

HR, ME = (600, 1400), (1300, 1400)
S("期望薪资多少？", "开场 · 谈薪", view=(950, 1000, 0.85), bars=2)
L(table(950, 1250), 0, 0.9, sfx="wood_low")
L(stick(*HR, 0.8, "down", tie=True), 1, 1.8, sfx="wood_high")
L(face(*HR, 0.8, "smile"), 1.8, 2.0)
L(bubble(640, 830, 340, 140, -1), 2, 2.6, BLACK, 8, sfx="pop")
T("期望多少？", 640, 830, 56, k0=2.6, k1=3.85)
L(stick(*ME, 0.8, "down"), 4, 4.8, sfx="wood_high")
L(face(*ME, 0.8, "flat"), 4.8, 5.0)
T("？？？", 1330, 900, 80, RED, k0=5, k1=5.8, sfx="pop")

S("谁先开口，谁定调", "开场 · 谁先开口", view=(950, 1050, 0.85))
b.erase(J(), 0, 1.0, 990, 870, 1120, 270)
H(0, "shaker")
L(bubble(640, 830, 340, 140, -1), 1, 1.6, BLACK, 8, sfx="pop")
T("一般给 8千", 640, 830, 54, k0=1.6, k1=2.8)
L(bubble(1260, 830, 340, 140, 1), 3, 3.6, BLUE, 8, sfx="pop")
T("那 9千？", 1260, 830, 54, BLUE, k0=3.6, k1=4.8)
L(arrow((800, 740), (1100, 740), -0.3, 36), 5, 5.8, RED, 9, sfx="wood_high")
T("先开口 = 定调", 950, 1540, 76, RED, k0=6, k1=7.75, sfx="kick")

# ---------------------------------------------------------------- 书中实验：幸运转盘（场景 3–4）

WX, WY, WR = 2650, 880, 230
S("先转个转盘", "书中实验 · 幸运转盘", view=(2650, 1000, 0.85))
J3 = J()
L(wheel(WX, WY, WR), 0, 0.9, sfx="wood_high")
for n, v in enumerate((0, 25, 50, 75)):
    T(str(v), *at_value(WX, WY, WR + 62, v), 50, k0=1 + n * 0.25, k1=1.6 + n * 0.25, sfx="pop" if n == 0 else None)


def pointer_fn(c, k, t):
    """转盘指针：场景 3 画出；场景 4 第 0 拍飞转、第 1 拍停在 10，第 4 拍再转、第 5 拍停在 65。"""
    s0, s1, s2, s3 = (b.t_of(J4, kk) for kk in (0, 1, 4, 5))
    if t < s0:
        v = 0.0
    elif t < s1:
        v = 210 * ease_out((t - s0) / (s1 - s0))
    elif t < s2:
        v = 10.0
    elif t < s3:
        v = 10 + 255 * ease_out((t - s2) / (s3 - s2))
    else:
        v = 65.0
    a = v / 100 * 2 * math.pi
    L0 = WR * 0.8 * (0.2 + 0.8 * clamp01(k))
    tx, ty = WX + math.sin(a) * L0, WY - math.cos(a) * L0
    p = P((WX, WY), (tx, ty))
    for d in (0.5, -0.5):
        p.moveTo(tx, ty)
        p.lineTo(tx - 46 * math.sin(a + d), ty + 46 * math.cos(a + d))
    c.drawPath(p, wb.marker(BLACK, 12))
    c.drawPath(circle(WX, WY, 26), wb.marker(RED, 10))
    return None


b.custom(J3, 2, 2.8, pointer_fn, sfx="rim")
KQ = (2150, 1310)               # 快快在转盘左下看着
L(kuai(*KQ, 0.6, "down"), 3, 3.9, RED, 9, sfx="wood_high")
L(face(*KQ, 0.6, "smile"), 3.9, 4.0, RED, 7)
T("联合国里，", 2650, 1270, 60, k0=4, k1=5.25, sfx="pop")
T("非洲国家占几成？", 2650, 1360, 60, k0=6, k1=8, sfx="pop")

S("转到几，就往几猜", "书中实验 · 两组答案", view=(2650, 1100, 0.75), shake=[0, 3, 7], flashes=[0])
J4 = J()
H(0, "kick", 0.9)
T("10", *at_value(WX, WY, WR + 62, 10), 54, RED, k0=1, k1=1.8, sfx="rim")
T("10 →", 2170, 1560, 80, k0=2, k1=2.8, sfx="pop")
b.custom(J4, 3, 3.4, slam_fn("25%", 2440, 1560, 110), sfx="kick")
H(4, "shaker", 0.7)
T("65", *at_value(WX, WY, WR + 62, 65), 54, RED, k0=5, k1=5.8, sfx="rim")
T("65 →", 2870, 1560, 80, k0=6, k1=6.8, sfx="pop")
b.custom(J4, 7, 7.4, slam_fn("45%", 3140, 1560, 110), sfx="kick")

# ---------------------------------------------------------------- 亮书 + 书中观点（场景 5–7）

S("这叫锚定", "思考，快与慢 · 书中观点", view=(2650, 2600, 0.85))
L(book(2400, 2470, 360, 240), 0, 0.9, sfx="wood_low")
T("思考，快与慢", 2400, 2250, 62, GREEN, k0=1, k1=2.5, sfx="pop")
L(kuai(2850, 2760, 0.7), 3, 3.9, RED, 9, sfx="wood_high")
L(face(2850, 2760, 0.7, "smile"), 3.9, 4.0, RED, 7)
L(man(3100, 2760, 0.7), 4, 4.9, BLUE, 9, sfx="wood_high")
L(face(3100, 2760, 0.7, "flat"), 4.9, 5.0, BLUE, 7)
L(anchor(2400, 2690, 0.9), 5, 5.9, BLACK, 10, sfx="wood_low")
T("锚定效应", 2960, 2960, 84, RED, k0=6, k1=7, sfx="ding")

AN = (500, 2460)
S("明知无关，也被拽走", "书中观点 · 被锚拽走", view=(950, 2600, 0.85))
L(anchor(*AN, 1.1), 0, 0.9, BLACK, 10, sfx="wood_low")
T("65", AN[0], 2340, 90, RED, k0=1, k1=1.8, sfx="pop")
KK = (1000, 2950)
L(kuai(*KK, 0.75), 2, 2.9, RED, 9, sfx="wood_high")
L(face(*KK, 0.75, "smile"), 2.9, 3.0, RED, 7)
L(bubble(1240, 2340, 380, 140, -1), 3, 3.6, BLACK, 8, sfx="pop")
T("大概 45%", 1240, 2340, 56, k0=3.6, k1=4.8)
L(chain((AN[0] + 24, AN[1]), (1045, 2380), 70), 5, 5.9, BLACK, 6, sfx="rim")
T("随便转的数", AN[0], 2880, 56, k0=6, k1=7.25, sfx="pop")

S("慢慢挪几步就停", "书中观点 · 调整不够", view=(950, 4200, 0.85))
LY = 4450
L(join(P((380, LY), (1520, LY)), anchor(440, LY - 180, 0.6)), 0, 0.9, BLACK, 9, sfx="wood_low")
L(flag(1460, LY), 1, 1.8, GREEN, 9, sfx="wood_high")
T("正确答案", 1430, LY - 290, 54, GREEN, k0=2, k1=3, sfx="pop")
L(foot(560, LY - 40, 0.9), 3, 3.5, BLUE, 7, sfx="pop")
L(foot(670, LY - 60, 0.9), 3.5, 4.0, BLUE, 7)
L(foot(780, LY - 40, 0.9), 4, 4.5, BLUE, 7, sfx="pop")
L(sit_man(890, LY, 0.7), 5, 5.9, BLUE, 9, sfx="wood_high")
L(face(890, LY - 7, 0.7, "flat"), 5.9, 6.0, BLUE, 7)
L(bubble(1010, 3990, 280, 120, -1), 6, 6.5, BLACK, 8, sfx="pop")
T("够了吧", 1010, 3990, 54, k0=6.5, k1=7.3)
L(both_arrow(990, 1420, LY + 90), 7, 7.8, RED, 9, sfx="rim")

# ---------------------------------------------------------------- 书中例子：法官（场景 8）

S("法官也会被带", "书中例子 · 法官", view=(2650, 4200, 0.85))
L(judge(2650, 4020, 0.6), 0, 0.9, BLACK, 9, sfx="wood_high")
RA, RB, BX = 4230, 4470, 2340
L(die(2210, RA), 1, 1.5, BLACK, 8, sfx="pop")
T("3", 2210, RA, 64, RED, k0=1.5, k1=2.3)
L(rect(BX + 225, RA, 450, 110, 14), 2, 2.8, BLACK, 9, sfx="wood_low")
T("约5个月", BX + 225, RA, 56, k0=2.8, k1=3.8)
L(die(2210, RB), 4, 4.5, BLACK, 8, sfx="pop")
T("9", 2210, RB, 64, RED, k0=4.5, k1=5.3)
L(rect(BX + 360, RB, 720, 110, 14), 5, 5.9, RED, 9, sfx="wood_low")
T("约8个月", BX + 360, RB, 56, RED, k0=5.9, k1=6.9)
L(underline(BX + 230, BX + 490, RB + 80, 10, 36), 7, 7.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 9–10）

S("划掉的原价也是锚", "例子 · 划线价", view=(2650, 5800, 0.85))
TG = (2480, 5700)
L(tag(*TG), 0, 0.9, BLACK, 9, sfx="wood_high")
T("¥999", TG[0] + 40, TG[1] - 70, 86, k0=1, k1=1.9, sfx="pop")
L(P((TG[0] - 110, TG[1] - 60), (TG[0] + 190, TG[1] - 80)), 2, 2.6, RED, 10, sfx="rim")
T("¥399", TG[0] + 40, TG[1] + 70, 110, RED, k0=3, k1=4, sfx="pop")
KP = (3050, 6150)
L(kuai(*KP, 0.7), 5, 5.9, RED, 9, sfx="wood_high")
L(face(*KP, 0.7, "smile"), 5.9, 6.0, RED, 7)
L(join(sparkle(KP[0] - 75, KP[1] - 230, 30), sparkle(KP[0] + 80, KP[1] - 240, 34)), 6, 6.8, RED, 7, sfx="ding")

S("一句两天，定了排期", "例子 · 排期", view=(950, 5800, 0.85))
BS = (460, 6150)
L(stick(*BS, 0.7, "point", tie=True), 0, 0.9, sfx="wood_high")
L(face(*BS, 0.7, "smile"), 0.9, 1.0)
L(bubble(800, 5600, 580, 150, -1), 1, 1.6, BLACK, 8, sfx="pop")
T("这个两天能做完吧？", 800, 5600, 54, k0=1.6, k1=3.8)
L(calendar(*CAL), 4, 4.9, BLACK, 8, sfx="wood_low")
(c0x, c0y), (c1x, _) = cell(0, 0), cell(1, 0)
L(loop((c0x + c1x) / 2, c0y, 230, 120), 5, 5.8, RED, 9, sfx="rim")
T("排期：2天", 1150, 6230, 64, RED, k0=6, k1=7.25, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

S("先写下自己的数", "做法① · 先写底价", view=(950, 7400, 0.85))
T("① 谈之前写好底价", 950, 7010, 72, BLUE, k0=0, k1=2.25, sfx="pop")
L(note(800, 7400), 3, 3.8, BLACK, 9, sfx="wood_high")
T("底价：1万", 790, 7380, 64, k0=4, k1=5.25, sfx="pop")
L(stick(1280, 7720, 0.7, "hold"), 6, 6.8, BLACK, 10, sfx="wood_high")
L(face(1280, 7720, 0.7, "smile"), 6.8, 6.9)
L(check(800, 7480, 40), 7, 7.6, GREEN, 10, sfx="ding")

S("离谱的数，别接着砍", "做法② · 不接离谱价", view=(2650, 7400, 0.85))
T("② 不接离谱价", 2650, 7010, 72, BLUE, k0=0, k1=1.5, sfx="pop")
OP, MY = (2280, 7800), (3060, 7800)
L(join(stick(*OP, 0.7, "point"), stick(*MY, 0.7, "down")), 2, 2.9, BLACK, 10, sfx="wood_high")
L(join(face(*OP, 0.7, "smile"), face(*MY, 0.7, "flat")), 2.9, 3.0)
L(bubble(2330, 7340, 380, 140, -1), 3, 3.6, BLACK, 8, sfx="pop")
T("就给 3千", 2330, 7340, 56, k0=3.6, k1=4.6)
L(cross(2330, 7340, 90), 5, 5.8, RED, 12, sfx="rim")
L(bubble(2960, 7340, 400, 140, 1), 6, 6.4, BLUE, 8, sfx="pop")
T("这个数没法谈", 2960, 7340, 50, BLUE, k0=6.4, k1=7.9)

S("反着找理由", "做法③ · 反着想", view=(2650, 9000, 0.85))
T("③ 想想它为啥不对", 2650, 8610, 72, BLUE, k0=0, k1=2.0, sfx="pop")
AQ = (2330, 8830)
L(anchor(*AQ, 0.8), 2, 2.9, BLACK, 10, sfx="wood_low")
T("3千", AQ[0], AQ[1] - 80, 64, RED, k0=3, k1=3.8, sfx="pop")
MQ = (3020, 9330)
L(man(*MQ, 0.75, "point"), 4, 4.9, BLUE, 9, sfx="wood_high")
L(face(*MQ, 0.75, "flat"), 4.9, 5.0, BLUE, 7)
L(lens(2650, 8950, 85), 5, 5.8, BLUE, 9, sfx="pop")
T("行情不止这个数", AQ[0] + 40, 9280, 56, k0=6, k1=7.75, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 6150, 0.14)
NEAR = (950, 9000, 0.8)
S("评论区聊聊", "评论区见", view=FAR, bars=4)
b.move(J(), 4, NEAR, 1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(kuai(650, 9300, 0.7, "up"), 5, 5.8, RED, 9, sfx="pop")
L(face(650, 9300, 0.7, "smile"), 5.8, 5.9, RED, 7)
L(man(1250, 9300, 0.7), 6, 6.8, BLUE, 9, sfx="wood_high")
L(face(1250, 9300, 0.7, "smile"), 6.8, 6.9, BLUE, 7)
T("你被哪个数字带偏过？", 950, 8700, 72, RED, k0=7, k1=9.5, sfx="pop")
T("下一讲：组里每个人，都觉得自己干得最多？", 950, 9460, 46, k0=10, k1=15, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "anchor", "锚定效应", "先报的数字，为什么能带偏你？", ACC, b.shots,
                 [f"{BOOK}第11章 锚定效应在生活中随处可见（Anchors）（转述）",
                  "中译本：胡晓姣、李爱民、何梦莹译，中信出版社 2012"],
                 "先报的数字|为什么能【带偏】你", SQUARE_SHOT,
                 ["书中观点均为转述（第 11 章）：先看到一个随机数字（幸运转盘停在 10 或 65），再估非洲国家在联合国里的"
                  "占比，两组的平均答案为 25% 和 45%；锚定有两条来路——系统2 从锚出发往外调整，调得不够就停下，"
                  "系统1 被锚提示，先想起和它相符的信息；有经验的德国法官掷过做过手脚的骰子（3 或 9）之后，"
                  "判的刑期也跟着变；谈判时对方报出离谱的数，书中建议别在这个数上还价，可以表明这样谈不下去，"
                  "主动想想这个锚为什么不对，能减弱它的影响。上屏均为转述，不是逐字引文。",
                  "书中数据：转盘 10 / 65、答案 25% / 45%；骰子 3 / 9、刑期约 5 个月 / 8 个月。",
                  "转盘指针飞转、答案被锚链拽走、慢慢从锚边挪几步就坐下等画面，为对书中观点的通俗化示意。",
                  "谈薪（8千 / 9千、3千 / 1万）、划线价（¥999 / ¥399）、“两天能做完吧”的排期均为现实场景示意，"
                  "数字为示意，不是数据，不指向任何具体公司或个人。",
                  "三个做法（谈之前写好底价；不接离谱价；想想它为啥不对）中，后两条据书中建议转述，"
                  "“先写好底价”为据书中思路整理的建议。"],
                 tags="#谈判 #锚定效应")
    return b.attach(ep)
