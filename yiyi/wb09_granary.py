"""09 过去的粮仓（白板手绘版）：日子一天天过去，算白过吗？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（数字 / 曲线故事：一张坐标图贯穿，横轴月份，两条线）：十二月的晚上，墙上的撕页日历只剩几页 →
阿宁翻相册，胸前罗盘乱晃：一年算白过吗？→ 画坐标轴，灰线从 365 页滑到 0（墙上的日历越来越薄）→
drop：红线从底部冲上来，和灰线交叉成 X（书中：悲观的人盯着日历变薄；另一个人每撕一页，就在背面记几句，收好）→
红线尽头画一座粮仓：做过的事、爱过的人、扛过的难存进去 → 拉远：一张张日历纸飞进粮仓，仓里慢慢满了，谁也拿不走 →
书中：上了年纪的人不用羡慕年轻人 → 算一笔账：一天一张 ×365，年底一摞 →
身边的例子（这周修好三个 bug / 周日陪爸下了盘棋）→
做法（今晚写一张 / 攒满一周，周日翻一遍 / 难熬那天也记一句“今天扛住了”，罗盘停住）→ 拉远全板 → 评论区。
书中观点为转述（Viktor E. Frankl, Man's Search for Meaning，第二部分 意义疗法〈生命之短暂〉；
中译本《活出生命的意义》，吕娜译，华夏出版社 2010）；曲线与 365 为示意，例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, lerp
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, doc, face, join,
                               rect, stick, underline)

from .common import BOOK, episode

ACC = "#C28E2C"                 # 本讲主色：粮仓金
SQUARE_SHOT = 5                 # 场景 6：两条曲线 + 粮仓 + 阿宁（胸前罗盘）
GRAY = "#8A8F98"
YELLOW = "#D9A21B"
PAPER = "#FBFBF9"

b = Board(size=(3600, 10300))


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
    """系列视觉角色：小罗盘（圆框 + 顶上小环 + 四个刻度），指针另用 needle_fn / wobble_fn 画。"""
    parts = [circle(x, y, r), circle(x, y - r - 14, 12)]
    for a in range(4):
        ang = a * math.pi / 2
        parts.append(P((x + math.cos(ang) * r * 0.72, y + math.sin(ang) * r * 0.72),
                       (x + math.cos(ang) * r * 0.9, y + math.sin(ang) * r * 0.9)))
    return join(*parts)


def _needle(c, x, y, r, a, alpha=1.0):
    ca, sa = math.cos(a), math.sin(a)
    L_, w = r * 0.78, r * 0.2
    tip, tail = (x + ca * L_, y + sa * L_), (x - ca * L_, y - sa * L_)
    s1, s2 = (x - sa * w, y + ca * w), (x + sa * w, y - ca * w)
    K.poly(c, [tip, s1, s2], RED, alpha)
    K.poly(c, [tail, s1, s2], BLACK, alpha)
    K.dot(c, x, y, r * 0.1, PAPER, alpha)


def needle_fn(x, y, r, aim, turns=2.5):
    """罗盘指针：k<1 时乱转（越转越慢、带抖动），k=1 停在指向 aim=(ax, ay) 的方向，之后一直停着。"""
    final = math.atan2(aim[1] - y, aim[0] - x)

    def fn(c, k, t):
        e = ease_in_out(k)
        a = final + (1 - e) * turns * 2 * math.pi + (0.5 * math.sin(k * 23) * (1 - k) if k < 1 else 0)
        _needle(c, x, y, r, a)
        return None

    return fn


def wobble_fn(x, y, r):
    """迷茫时的罗盘：指针一直来回乱晃，停不下来。"""
    def fn(c, k, t):
        a = -math.pi / 2 + 1.6 * math.sin(t * 2.3) + 0.7 * math.sin(t * 5.1 + 1.0)
        _needle(c, x, y, r, a, clamp01(k * 3))
        return None

    return fn


def fill_fn(path, color, alpha=0.35):
    """把一块区域淡淡填色（便签底色），随 k 渐显。"""
    def fn(c, k, t):
        c.drawPath(path, K.paint(color, alpha * k))
        return None

    return fn


def granary(x, y, w=460, h=400, door=False) -> skia.Path:
    """粮仓：(x, y) 为底边中点；方仓身 + 出檐的人字顶，顶上一个小气窗，可带一扇门。"""
    roof_h = w * 0.42
    parts = [P((x - w / 2, y - h), (x - w / 2, y), (x + w / 2, y), (x + w / 2, y - h)),
             P((x - w / 2 - 45, y - h + 10), (x, y - h - roof_h), (x + w / 2 + 45, y - h + 10)),
             P((x - w / 2, y - h), (x + w / 2, y - h)),
             circle(x, y - h - roof_h * 0.45, w * 0.06)]
    if door:
        dw, dh = w * 0.34, h * 0.5
        parts += [P((x - dw / 2, y), (x - dw / 2, y - dh), (x + dw / 2, y - dh), (x + dw / 2, y)),
                  P((x - dw / 2, y - dh), (x + dw / 2, y)), P((x + dw / 2, y - dh), (x - dw / 2, y))]
    return join(*parts)


def day_pad(x, y, w=420, h=420) -> skia.Path:
    """墙上的撕页日历：(x, y) 为纸面中心；顶上装订条 + 挂钉，纸面下沿只剩薄薄三层。"""
    top = y - h / 2
    parts = [rect(x, top - 30, w + 40, 60, 10), rect(x, y, w, h, 6),
             P((x, top - 60), (x, top - 110)), circle(x, top - 122, 12)]
    for i in range(3):
        yy = y + h / 2 + 14 + i * 13
        parts.append(P((x - w / 2 + 8 + i * 6, yy), (x + w / 2 - 8 - i * 6, yy)))
    return join(*parts)


def window_moon(x, y, s=300) -> skia.Path:
    """窗户 + 窗外一弯月亮：(x, y) 为窗中心。"""
    r = s * 0.17
    m = skia.Path()
    m.addArc(skia.Rect.MakeXYWH(x + s * 0.12 - r, y - s * 0.2 - r, 2 * r, 2 * r), 60, 240)
    m.addArc(skia.Rect.MakeXYWH(x + s * 0.12 - r * 0.45, y - s * 0.2 - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return join(rect(x, y, s, s, 10), P((x, y - s / 2), (x, y + s / 2)), P((x - s / 2, y), (x + s / 2, y)), m)


def album(x, y, w=560, h=360) -> skia.Path:
    """打开的相册：两页，每页一张照片（照片里画一座小山和太阳）。"""
    parts = [book(x, y, w, h)]
    for side in (-1, 1):
        px, py = x + side * w / 4, y - 10
        pw, ph = w * 0.34, h * 0.42
        parts += [rect(px, py, pw, ph, 6),
                  P((px - pw / 2 + 10, py + ph / 2 - 10), (px - pw / 8, py - ph / 8), (px + pw / 8, py + ph / 6),
                    (px + pw / 3, py), (px + pw / 2 - 10, py + ph / 2 - 10)),
                  circle(px + pw / 4, py - ph / 4, 12)]
    return join(*parts)


def paper_stack(x, y, w=280, n=12, step=22) -> skia.Path:
    """一摞纸：(x, y) 为最底下一张的中心，往上叠，每张略微错开。"""
    parts = []
    for i in range(n):
        dx = 10 * math.sin(i * 1.7)
        parts.append(rect(x + dx, y - i * step, w, step + 4, 4))
    return join(*parts)


def torn_page(x, y, w=900, h=760) -> skia.Path:
    """撕下来的日历纸（翻到背面）：顶边是撕口锯齿，(x, y) 为纸面中心。"""
    top = y - h / 2
    pts = [(x - w / 2, y + h / 2), (x - w / 2, top)]
    n = 14
    for i in range(1, n + 1):
        pts.append((x - w / 2 + w * i / n, top + (14 if i % 2 else -10)))
    pts += [(x + w / 2, y + h / 2)]
    return P(*pts, close=True)


def chessboard(x, y, s=340, n=4) -> skia.Path:
    parts = [rect(x, y, s, s, 6)]
    for i in range(1, n):
        o = -s / 2 + s * i / n
        parts += [P((x + o, y - s / 2), (x + o, y + s / 2)), P((x - s / 2, y + o), (x + s / 2, y + o))]
    return join(*parts)


def cane(x, y, s=1.0) -> skia.Path:
    """拐杖：(x, y) 为杖底，杖头朝左弯。"""
    p = skia.Path()
    p.moveTo(x, y)
    p.lineTo(x - 16 * s, y - 120 * s)
    p.quadTo(x - 20 * s, y - 150 * s, x - 45 * s, y - 140 * s)
    return p


def rain_cloud(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 150 * s, y + 40 * s)
    p.cubicTo(x - 220 * s, y + 40 * s, x - 200 * s, y - 60 * s, x - 120 * s, y - 40 * s)
    p.cubicTo(x - 110 * s, y - 120 * s, x + 20 * s, y - 130 * s, x + 40 * s, y - 60 * s)
    p.cubicTo(x + 120 * s, y - 110 * s, x + 220 * s, y - 30 * s, x + 150 * s, y + 40 * s)
    p.close()
    drops = [P((x + dx * s, y + 80 * s), (x + (dx - 18) * s, y + 150 * s)) for dx in (-110, -40, 30, 100)]
    return join(p, *drops)


# ---------------------------------------------------------------- 开局：十二月的晚上（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

PAD = (780, 840)
scene("日历快撕完了", "十二月的晚上", (950, 900, 0.85), bars=2)
L(day_pad(*PAD), 0, 0.9, BLACK, 9, sfx="wood_high")
T("12月", PAD[0], PAD[1] - 120, 60, k0=1, k1=1.8, sfx="pop")
T("28", PAD[0], PAD[1] + 40, 160, RED, k0=2, k1=2.8, sfx="pop")
L(window_moon(1330, 720, 300), 3, 3.8, BLACK, 8, sfx="wood_low")
T("只剩几页", 950, 1220, 64, k0=4, k1=5.2, sfx="pop")
H(5, "shaker", 0.5)

AN2 = (2230, 1230)
COMP2 = (2230, 1097, 40)
scene("一年算白过吗", "一个问题", (2650, 900, 0.85))
L(album(2830, 800), 0, 0.9, BLACK, 8, sfx="wood_low")
L(stick(*AN2, 0.8, "hold"), 1, 1.8, BLUE, 10, sfx="wood_high")
L(face(*AN2, 0.8, "flat"), 1.8, 2.0, BLUE, 9)
L(compass(*COMP2), 2, 2.6, BLACK, 7, sfx="pop")
b.custom(J(), 2.6, 3.2, wobble_fn(*COMP2))
H(3, "shaker", 0.6)
T("又一年", 2830, 560, 56, GRAY, k0=4, k1=4.8, sfx="pop")
T("算白过吗？", 2840, 1150, 96, RED, k0=5, k1=6.5, sfx="kick")

# ---------------------------------------------------------------- 一张坐标图（场景 3–6）

CY = 2700
O = (1330, CY + 370)                    # 坐标原点
X1, Y1 = 2380, CY - 360                 # 横轴右端、纵轴顶端
G0, G1 = (1380, CY - 340), (2330, CY + 350)     # 灰线：墙上的日历，365 页滑到 0
R0, R1 = (1380, CY + 350), (2330, CY - 340)     # 红线：背面记下的，越攒越多
XC = (1855, CY + 5)                     # 两线交叉点
V3 = (1850, CY, 0.85)


def gray_curve() -> skia.Path:
    p = skia.Path()
    p.moveTo(*G0)
    p.quadTo(1760, CY - 120, G1[0], G1[1])
    return p


scene("日历越来越薄", "一张图 · 日历线", V3)
L(join(P((O[0], Y1), O, (X1, O[1])), P((O[0] - 18, Y1 + 30), (O[0], Y1), (O[0] + 18, Y1 + 30)),
       P((X1 - 30, O[1] - 18), (X1, O[1]), (X1 - 30, O[1] + 18))), 0, 0.9, BLACK, 9, sfx="wood_high")
T("1月", 1390, CY + 440, 50, k0=1, k1=1.5, sfx="pop")
T("12月", 2320, CY + 440, 50, k0=1.5, k1=2.0)
T("365", 1262, G0[1], 48, GRAY, k0=2, k1=2.8, sfx="pop")
L(gray_curve(), 3, 3.9, GRAY, 12, sfx="wood_low")
T("0", 2410, CY + 310, 56, GRAY, k0=4, k1=4.8, sfx="pop")
T("墙上的日历", 1880, CY - 250, 56, GRAY, k0=5, k1=6.25, sfx="pop")

scene("撕下来，记几句", "活出生命的意义 · 书中观点", V3, shake=[0], flashes=[0])
L(P(R0, (1700, CY + 150), (2000, CY - 90), R1), 0, 0.6, RED, 14, sfx="kick")
L(circle(*XC, 46), 1, 1.8, RED, 8, sfx="ding")
T("盯着它变薄", 1855, CY + 268, 52, GRAY, k0=2, k1=3.25, sfx="pop")
T("另一个人：撕一页，记几句", 1790, CY - 470, 56, RED, k0=4, k1=6.75, sfx="pop")
L(doc(R1[0], CY - 452, 100, 124, 3), 7, 7.8, RED, 6, sfx="wood_high")

GX, GY, GW, GH = 2900, CY + 300, 460, 400    # 粮仓：底边中点、宽、高
scene("存进了粮仓", "书中观点 · 粮仓", (2650, CY, 0.85))
L(arrow((R1[0] + 40, R1[1] + 20), (GX - GW / 2 - 30, GY - GH - 20), -0.2, 40), 0, 0.9, RED, 9, sfx="wood_high")
L(granary(GX, GY, GW, GH), 1, 1.9, BLACK, 10, sfx="wood_low")
T("做过的事", GX, GY - GH + 90, 52, k0=3, k1=3.9, sfx="pop")
T("爱过的人", GX, GY - GH + 190, 52, RED, k0=4, k1=4.9, sfx="pop")
T("扛过的难", GX, GY - GH + 290, 52, k0=5, k1=5.9, sfx="pop")
T("过去的粮仓", GX, GY + 110, 64, RED, k0=6, k1=7.25, sfx="ding")
H(2, "shaker", 0.5)

DEST = (GX, GY - GH - 60)


def flying_pages(c, k, t):
    """一张张日历纸从灰线上飞起来，沿弧线落进粮仓顶上的气窗，边飞边转、越飞越小。"""
    n = 9
    for i in range(n):
        f = clamp01((k - i * 0.08) / 0.36)
        if f <= 0 or f >= 1:
            continue
        u = 0.08 + 0.1 * i
        sx, sy = lerp(G0[0], G1[0], u), lerp(G0[1], G1[1], u) - 40
        cx, cy = (sx + DEST[0]) / 2, min(sy, DEST[1]) - 420
        e = ease_in_out(f)
        x = (1 - e) ** 2 * sx + 2 * (1 - e) * e * cx + e ** 2 * DEST[0]
        y = (1 - e) ** 2 * sy + 2 * (1 - e) * e * cy + e ** 2 * DEST[1]
        s = 1 - 0.6 * f ** 3
        a = 1 if f < 0.85 else (1 - f) / 0.15
        c.save()
        c.translate(x, y)
        c.rotate(25 * math.sin(f * 9 + i))
        c.scale(s, s)
        c.drawPath(rect(0, 0, 80, 100, 6), K.paint(PAPER, a))
        c.drawPath(rect(0, 0, 80, 100, 6), K.paint(BLACK, a, 5))
        for yy in (-18, 6, 28):
            c.drawPath(P((-24, yy), (24, yy)), K.paint(RED, a, 4))
        c.restore()
    return None


def grain_fill(c, k, t):
    """仓里慢慢满起来：从仓底往上铺一层淡金色。"""
    h = (GH - 30) * ease_in_out(k)
    c.drawRect(skia.Rect.MakeLTRB(GX - GW / 2 + 8, GY - 6 - h, GX + GW / 2 - 8, GY - 6), K.paint(YELLOW, 0.3))
    return None


AN6 = (2330, CY + 920)
COMP6 = (AN6[0], AN6[1] - 140, 44)
scene("谁也拿不走", "书中观点 · 拿不走", (2220, CY + 80, 0.52))
b.custom(J(), 0, 6, flying_pages, sfx="shaker")
b.custom(J(), 1, 7, grain_fill, sfx="wood_low")
L(stick(*AN6, 0.85, "point"), 2, 2.8, BLUE, 11, sfx="wood_high")
L(face(*AN6, 0.85, "smile"), 2.8, 3.0, BLUE, 10)
L(compass(*COMP6), 3, 3.6, BLACK, 8, sfx="pop")
b.custom(J(), 3.6, 5.0, needle_fn(*COMP6, (GX, GY - GH / 2), turns=1.5))
H(5, "ding")
T("谁也拿不走", 1640, CY + 720, 100, RED, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 书中观点 · 算一笔账（场景 7–8）

C7 = 4400
scene("做过的都算数", "书中观点 · 老人", (950, C7, 0.85))
L(granary(600, C7 + 10, 260, 220, door=True), 0, 0.9, BLACK, 8, sfx="wood_low")
L(join(stick(780, C7 + 330, 0.7, "down"), cane(840, C7 + 330, 0.9)), 1, 1.8, BLACK, 9, sfx="wood_high")
L(face(780, C7 + 330, 0.7, "smile"), 1.8, 2.0, BLACK, 8)
L(stick(1240, C7 + 330, 0.7, "down", hair=True), 2, 2.8, BLUE, 9, sfx="wood_high")
L(face(1240, C7 + 330, 0.7, "flat"), 2.8, 3.0, BLUE, 8)
T("老人不用羡慕年轻人", 950, C7 - 430, 60, k0=3, k1=5.25, sfx="pop")
T("他手里有做成的事", 950, C7 + 470, 60, RED, k0=6, k1=8, sfx="ding")

scene("年底一摞", "算一笔账", (2650, C7, 0.85))
T("一天撕一张", 2650, C7 - 430, 64, k0=0, k1=1.25, sfx="pop")
L(doc(2280, C7 - 60, 200, 250, 4), 2, 2.8, BLACK, 8, sfx="wood_low")
T("背面一句", 2280, C7 + 140, 48, k0=3, k1=3.8, sfx="pop")
T("×365", 2640, C7 - 60, 96, RED, k0=4, k1=4.9, sfx="pop")
L(paper_stack(3010, C7 + 110, 280, 12, 22), 5, 5.9, BLACK, 6, sfx="wood_high")
T("年底一摞", 2650, C7 + 400, 76, RED, k0=6, k1=7.0, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 9–10）

C9 = 5700
scene("修好了三个问题", "例子 · 工作", (950, C9, 0.85))
L(torn_page(950, C9 + 20, 900, 760), 0, 0.9, BLACK, 9, sfx="wood_low")
T("周五 · 背面", 700, C9 - 250, 48, GRAY, k0=1, k1=2.0, sfx="pop")
T("这周修了 3 个 bug", 950, C9 - 80, 70, k0=2, k1=4.75, sfx="pop")
T("上线没出事", 950, C9 + 100, 64, RED, k0=5, k1=6.25, sfx="pop")
L(check(1240, C9 + 260, 60), 7, 7.7, GREEN, 12, sfx="ding")

scene("陪爸下了盘棋", "例子 · 家里", (2650, C9, 0.85))
L(chessboard(2650, C9 + 60, 340), 0, 0.9, BLACK, 7, sfx="wood_high")
L(stick(2250, C9 + 360, 0.75, "hold"), 1, 1.8, BLUE, 9, sfx="wood_high")
L(face(2250, C9 + 360, 0.75, "smile"), 1.8, 2.0, BLUE, 8)
L(stick(3050, C9 + 360, 0.75, "down"), 2, 2.8, BLACK, 9, sfx="wood_low")
L(face(3050, C9 + 360, 0.75, "smile"), 2.8, 3.0, BLACK, 8)
T("爸", 3050, C9 + 430, 50, k0=3, k1=3.8, sfx="pop")
L(join(circle(2565, C9 - 25, 22), circle(2735, C9 + 60, 22), circle(2650, C9 + 145, 22)), 4, 4.6, RED, 8,
  sfx="pop")
T("周日陪爸下了盘棋", 2650, C9 - 400, 66, RED, k0=5, k1=7, sfx="pop")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

C11 = 7000
NOTE11 = (950, C11 + 20, 600, 420)
scene("今晚写一张", "做法① · 写一张", (950, C11, 0.85))
T("① 今晚写一张", 950, C11 - 440, 72, BLUE, k0=0, k1=1.75, sfx="pop")
b.custom(J(), 2, 2.6, fill_fn(rect(*NOTE11, 10), YELLOW))
L(rect(*NOTE11, 10), 2, 2.8, YELLOW, 8, sfx="wood_high")
L(join(P((1380, C11 + 330), (1500, C11 + 150)), P((1360, C11 + 300), (1400, C11 + 340)),
       P((1480, C11 + 120), (1530, C11 + 160))), 3, 3.6, BLACK, 10, sfx="wood_low")
T("今天做成了：", 950, C11 - 70, 56, k0=4, k1=5.5, sfx="pop")
T("报表交了", 950, C11 + 70, 66, RED, k0=6, k1=6.9, sfx="pop")
L(underline(830, 1070, C11 + 120, amp=6, step=40), 7, 7.8, RED, 7, sfx="ding")

NOTE_X = [2650 + (i - 3) * 165 for i in range(7)]
NY = C11 - 120
DAYS = "一二三四五六日"
scene("周日翻一翻", "做法② · 翻一翻", (2650, C11, 0.85))
T("② 攒满一周", 2650, C11 - 440, 72, BLUE, k0=0, k1=1.5, sfx="pop")
b.custom(J(), 1, 1.6, fill_fn(join(*[rect(x, NY, 140, 150, 8) for x in NOTE_X]), YELLOW))
L(join(*[rect(x, NY, 140, 150, 8) for x in NOTE_X]), 1, 1.9, YELLOW, 7, sfx="wood_high")
for i, (x, d) in enumerate(zip(NOTE_X, DAYS)):
    b.text(J(), 2 + 0.4 * i, 2.4 + 0.4 * i, d, x, NY, 60, RED if d == "日" else BLACK, sfx="pop" if i == 0 else None)
L(arrow((NOTE_X[0], NY + 110), (NOTE_X[-1], NY + 110), -0.12, 40), 5, 5.9, BLACK, 8, sfx="wood_low")
T("周日翻一遍", 2650, C11 + 300, 72, RED, k0=6, k1=7.25, sfx="ding")

C13 = 8300
AN13 = (600, C13 + 360)
COMP13 = (600, C13 + 360 - 117, 38)
NOTE13 = (1200, C13 + 60, 500, 260)
scene("难的日子也记", "做法③ · 难的日子", (950, C13, 0.85))
T("③ 难熬的那天", 950, C13 - 440, 72, BLUE, k0=0, k1=1.75, sfx="pop")
L(rain_cloud(600, C13 - 210, 0.9), 2, 2.9, GRAY, 8, sfx="wood_low")
L(stick(*AN13, 0.7, "down"), 3, 3.8, BLUE, 10, sfx="wood_high")
L(face(*AN13, 0.7, "flat"), 3.8, 4.0, BLUE, 9)
b.custom(J(), 4, 4.6, fill_fn(rect(*NOTE13, 10), YELLOW))
L(rect(*NOTE13, 10), 4, 4.8, YELLOW, 8, sfx="pop")
T("今天扛住了", NOTE13[0], NOTE13[1], 66, RED, k0=5, k1=6.25, sfx="pop")
L(compass(*COMP13), 6.3, 6.9, BLACK, 6)
b.custom(J(), 6.9, 8.0, needle_fn(*COMP13, (NOTE13[0] - 120, NOTE13[1]), turns=2))
H(7, "shaker", 0.5)
H(8, "ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 4600, 0.115)
CMT = (1800, 9600, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(bubble(1800, 9480, 1150, 240, -1), 5, 5.8, BLACK, 8)
T("今年最想存进粮仓的一天？", 1800, 9480, 70, RED, k0=6, k1=9, sfx="pop")
T("下一讲：要是能重来，今天你怎么过？", 1800, 9790, 50, k0=10, k1=14, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "granary", "过去的粮仓", "日子一天天过去，算白过吗？", ACC, b.shots,
                 [f"{BOOK}第二部分 意义疗法〈生命之短暂〉（转述）",
                  "Viktor E. Frankl, Man's Search for Meaning；中译本《活出生命的意义》，吕娜译，华夏出版社 2010"],
                 "日子一天天过去|算【白过】吗", SQUARE_SHOT,
                 ["书中观点为转述，均见第二部分 意义疗法〈生命之短暂〉：悲观的人像盯着墙上的日历一天天变薄；"
                  "另一个人每撕下一页，就在背面记几句，整齐收好；过去做过的事、爱过的人、受过的苦存进了过去的粮仓，谁也拿不走；"
                  "上了年纪的人不必羡慕年轻人。上屏均为转述，不是逐字引文。",
                  "坐标图、灰线（墙上的日历从 365 页到 0）与红线（背面记下的越攒越多）、日历纸飞进粮仓、"
                  "“一天一张 ×365，年底一摞”为对书中比喻的通俗化示意；365 为一年的天数，曲线形状不是数据。",
                  "十二月的晚上与撕页日历、翻相册、这周修了 3 个 bug、周日陪爸下棋均为现实场景示意，不指向任何具体公司或个人；"
                  "阿宁为示意角色；日期为示意。",
                  "三步做法（今晚写一张记今天做成的事；攒满一周，周日翻一遍；难熬那天也记一句“今天扛住了”）"
                  "为据书中思路整理的建议。"],
                 tags="#年终 #生活")
    return b.attach(ep)
