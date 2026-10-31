"""06 回归平均（白板手绘版）：被骂完就变好，真是骂的功劳？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（形式 G：倒叙）：先给飞行教官的结论（骂完学员就飞好了、夸完反而砸了，于是“只骂不夸”）→
倒带：白板上一条虚线往左卷回去，铺成成绩图的中线 → drop：一排成绩点绕着中线起伏，最差那次后面自己弹回中线、
最好那次后面往下落 → 亮书（快快和慢慢；书里给空军教官讲课的那段）→ 书中观点（成绩 = 本事 + 运气；运气这回好、
下回一般，成绩往中间挪，叫回归平均值；高尔夫头天领先的人第二天往回落）→ 身边的例子（业绩垫底挨批后回升，快快抢着说
“骂管用”；最差的两个组，试了新办法的变好，没动的也变好）→ 三个做法（看平均 / 留对照组 / 该夸照样夸）→ 拉远看全板 →
评论区（快快举手、慢慢点头）。
系列角色：快快（红，头顶闪电，抢着下结论）、慢慢（蓝，圆眼镜）；本讲道具：戴大檐帽的教官、成绩点、虚线中线。
书中观点为转述（丹尼尔·卡尼曼《思考，快与慢》第17章“所有表现都会回归平均值”，胡晓姣、李爱民、何梦莹译，中信出版社 2012）；
业绩、两个组的例子为示意，“看平均”“该夸照样夸”为据书中思路整理的做法。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, face,
                               join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode, kuai, man

ACC = "#3A6FC2"
SQUARE_SHOT = 3                 # 场景 4：成绩点绕中线起伏 + 右边挠头的教官

b = Board(size=(3600, 10800))
GRAY = "#8E95A3"


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

def _body(x, y, s):
    """小人的头、身子、腿（不含胳膊），返回 (路径, 头心 y, 肩 y)。"""
    hy = y - 290 * s
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)),
                P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y))), hy, hy + 80 * s


def cap(x, y, s=1.0) -> skia.Path:
    """教官的大檐帽：(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 62 * s, hy - 32 * s), (x + 70 * s, hy - 32 * s)),
                P((x - 44 * s, hy - 34 * s), (x - 52 * s, hy - 78 * s), (x + 48 * s, hy - 78 * s), (x + 44 * s, hy - 34 * s)))


def coach(x, y, s=1.0, arms="hips") -> skia.Path:
    """教官：戴大檐帽的小人。arms：hips（叉腰）/ scratch（挠头）/ 其余同 stick。"""
    if arms not in ("hips", "scratch"):
        return join(stick(x, y, s, arms), cap(x, y, s))
    body, hy, sh = _body(x, y, s)
    if arms == "hips":
        a = P((x - 22 * s, hy + 175 * s), (x - 78 * s, hy + 125 * s), (x, sh), (x + 78 * s, hy + 125 * s),
              (x + 22 * s, hy + 175 * s))
    else:
        a = join(P((x - 70 * s, hy + 170 * s), (x, sh)), P((x, sh), (x + 80 * s, hy + 40 * s), (x + 50 * s, hy - 20 * s)))
    return join(body, a, cap(x, y, s))


def cadet(x, y, s=1.0) -> skia.Path:
    """敬礼的学员：右手举到额前。"""
    body, hy, sh = _body(x, y, s)
    return join(body, P((x - 70 * s, hy + 170 * s), (x, sh)), P((x, sh), (x + 75 * s, hy + 45 * s), (x + 38 * s, hy - 12 * s)))


def plane(x, y, s=1.0, ang=0.0) -> skia.Path:
    """小飞机（侧视，机头朝右）：(x, y) 为机身中心，ang 为顺时针转角（度）。"""
    p = join(P((x + 110 * s, y), (x + 70 * s, y - 20 * s), (x - 80 * s, y - 20 * s), (x - 112 * s, y - 62 * s),
               (x - 128 * s, y - 62 * s), (x - 112 * s, y + 4 * s), (x - 80 * s, y + 18 * s), (x + 70 * s, y + 18 * s),
               close=True),
             P((x + 15 * s, y + 4 * s), (x - 30 * s, y + 70 * s), (x - 58 * s, y + 70 * s), (x - 40 * s, y + 4 * s)),
             P((x + 72 * s, y - 14 * s), (x + 42 * s, y - 14 * s)))
    if ang:
        p.transform(skia.Matrix.RotateDeg(ang, skia.Point(x, y)))
    return p


def thumb(x, y, s=1.0) -> skia.Path:
    """竖大拇指：(x, y) 为拳头中心。"""
    parts = [rect(x + 10 * s, y + 10 * s, 120 * s, 110 * s, 24 * s),
             P((x - 42 * s, y - 45 * s), (x - 40 * s, y - 120 * s), (x - 18 * s, y - 145 * s), (x + 4 * s, y - 128 * s),
               (x + 6 * s, y - 45 * s))]
    for i in range(3):
        yy = y - 18 * s + i * 30 * s
        parts.append(P((x + 30 * s, yy), (x + 68 * s, yy)))
    return join(*parts)


def rewind(x, y, s=1.0) -> skia.Path:
    """倒带符号：两个朝左的三角。"""
    return join(P((x, y - 70 * s), (x - 105 * s, y), (x, y + 70 * s), close=True),
                P((x + 105 * s, y - 70 * s), (x, y), (x + 105 * s, y + 70 * s), close=True))


def dashes(x0, x1, y, dash=40, gap=26) -> skia.Path:
    parts = []
    x = x0
    while x < x1:
        parts.append(P((x, y), (min(x + dash, x1), y)))
        x += dash + gap
    return join(*parts)


def dice(x, y, n, w=150) -> skia.Path:
    """骰子：圆角方块 + 点数（n 取 2 或 6）。"""
    d = w * 0.27
    pips = {2: [(-d, -d), (d, d)], 6: [(-d, -d), (-d, 0), (-d, d), (d, -d), (d, 0), (d, d)]}[n]
    return join(rect(x, y, w, w, 26), *[circle(x + px, y + py, 10) for px, py in pips])


def flag(x, y, s=1.0) -> skia.Path:
    """高尔夫小旗：(x, y) 为球洞中心。"""
    hole = skia.Path()
    hole.addOval(skia.Rect.MakeXYWH(x - 60 * s, y - 14 * s, 120 * s, 28 * s))
    return join(hole, P((x, y), (x, y - 340 * s)), P((x, y - 340 * s), (x + 140 * s, y - 292 * s), (x, y - 244 * s)),
                P((x - 140 * s, y + 40 * s), (x + 150 * s, y + 40 * s)))


def brace(x, y0, y1, w=40) -> skia.Path:
    """右花括号 }。"""
    m = (y0 + y1) / 2
    p = skia.Path()
    p.moveTo(x, y0)
    p.quadTo(x + w, y0, x + w, y0 + w)
    p.lineTo(x + w, m - w)
    p.quadTo(x + w, m, x + 2 * w, m)
    p.quadTo(x + w, m, x + w, m + w)
    p.lineTo(x + w, y1 - w)
    p.quadTo(x + w, y1, x, y1)
    return p


def dots_path(pts, r=14) -> skia.Path:
    return join(*[circle(x, y, r) for x, y in pts])


def scroll_fn(x0, x1, y, slide=520, period=66, grow=0.25):
    """往左卷的虚线：先从右往左铺开，再整条往左滑（倒带），最后停住。"""

    def fn(c, k, t):
        g = ease_out(clamp01(k / grow))
        off = slide * ease_out(clamp01((k - grow) / (1 - grow)))
        xl = x1 - (x1 - x0) * g
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(xl - 2, y - 20, x1 + 2, y + 20))
        n = int((x1 - x0 + slide) / period) + 3
        for i in range(-1, n):
            xs = x0 + i * period - (off % period)
            c.drawLine(xs, y, xs + period * 0.58, y, K.paint(GRAY, 1, 9))
        c.restore()
        return (xl, y) if k < grow else None

    return fn


def score_dots_fn(pts, r=22, span=0.75):
    """成绩点一个接一个蹦出来，前后用浅灰线连起来。"""

    def fn(c, k, t):
        n = len(pts)
        tip = None
        for i, (x, y) in enumerate(pts):
            s = clamp01((k - i / n * span) / 0.12)
            if s <= 0:
                break
            if i > 0:
                px, py = pts[i - 1]
                c.drawLine(px, py, px + (x - px) * s, py + (y - py) * s, K.paint(GRAY, 0.7, 5))
            K.dot(c, x, y, r * ease_out(s) * (1 + 0.25 * math.sin(math.pi * s)), BLACK)
            tip = (x, y + r)
        return tip if k < 1 else None

    return fn


def press_fn(x0, x1, y, y_from, color=GREEN, width=16):
    """一条平线从上方压下来，落在 y 上。"""

    def fn(c, k, t):
        yy = y_from + (y - y_from) * ease_out(k)
        c.drawLine(x0, yy, x1, yy, K.paint(color, 1, width))
        return ((x0 + x1) / 2, yy) if k < 1 else None

    return fn


# ---------------------------------------------------------------- 开局：教官的结论（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

CO1 = (620, 1250, 0.85)
scene("骂完，就飞好了", "教官的结论", (950, 950, 0.85), bars=2)
L(coach(*CO1, "hips"), 0, 0.9, BLACK, 10, sfx="wood_high")
L(face(*CO1, "sad"), 0.9, 1.0, BLACK, 8)
L(bubble(720, 690, 330, 150, -1), 1, 1.5, BLACK, 8, sfx="pop")
T("重飞！", 720, 690, 66, RED, k0=1.5, k1=2.3)
L(cadet(1150, 1250, 0.75), 2, 2.8, BLUE, 10, sfx="wood_high")
L(plane(1230, 640, 0.9), 3, 3.8, BLACK, 9, sfx="pop")
T("飞好了", 1230, 800, 64, GREEN, k0=4, k1=4.8, sfx="ding")
L(check(1390, 790, 36), 5, 5.6, GREEN, 10, sfx="pop")

scene("夸完，反而砸了", "教官的结论", (2650, 950, 0.85))
L(join(rect(2360, 960, 520, 600, 20), rect(2940, 960, 520, 600, 20)), 0, 0.9, BLACK, 8, sfx="wood_high")
L(coach(2250, 1200, 0.6, "down"), 1, 1.8, BLACK, 9, sfx="pop")
L(face(2250, 1200, 0.6, "smile"), 1.8, 2.0, BLACK, 7)
L(thumb(2480, 880, 0.8), 2, 2.8, GREEN, 9, sfx="wood_high")
T("下一次", 2940, 730, 56, k0=3, k1=3.8, sfx="pop")
L(plane(2930, 1070, 0.85, 30), 4, 4.8, BLACK, 9, sfx="tom")
T("砸了", 3080, 880, 70, RED, k0=5, k1=5.8, sfx="rim")
T("只骂不夸", 2650, 1400, 90, RED, k0=6, k1=7, sfx="kick")
L(underline(2470, 2830, 1465), 7, 7.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 倒带 → 成绩图（场景 3–4）

V34 = (1800, 2580, 0.65)
MID_Y = 2600
OFF = [-60, 90, -30, 260, 40, -80, -250, -20, 70]          # 每次成绩离中线多远（往下为差）
PTS = [(1200 + i * 130, MID_Y + v) for i, v in enumerate(OFF)]
WORST, BEST = PTS[3], PTS[6]
CO3 = (2470, 2810, 0.55)

scene("倒回去看看", "倒带", V34)
L(rewind(1350, 2030), 0, 0.9, RED, 12, sfx="wood_high")
T("倒带", 1620, 2030, 84, RED, k0=1, k1=1.8, sfx="pop")
C(2, 8, scroll_fn(1080, 2330, MID_Y), sfx="wood_low")
H(3, "shaker", 0.7)
L(arrow((1080, 2930), (1080, 2240), 0, 40), 4, 4.8, BLACK, 9, sfx="wood_high")
T("成绩", 1080, 2175, 64, k0=5, k1=5.8, sfx="pop")
L(coach(*CO3, "scratch"), 6, 6.8, BLACK, 9, sfx="wood_high")
T("？", CO3[0], 2520, 84, RED, k0=7, k1=7.8, sfx="pop")

scene("本来就会往回落", "倒带 · 成绩图", V34, shake=[0], flashes=[0])
C(0, 1.6, score_dots_fn(PTS), sfx="kick")
L(circle(*WORST, 56), 2, 2.8, RED, 9, sfx="rim")
T("最差", WORST[0] - 140, WORST[1] + 10, 60, RED, k0=3, k1=3.8, sfx="pop")
L(arrow((WORST[0] + 10, WORST[1] - 60), (PTS[4][0] - 12, PTS[4][1] + 26), -0.45, 34), 4, 4.8, RED, 10, sfx="kick")
L(circle(*BEST, 56), 5, 5.8, BLUE, 9, sfx="pop")
L(arrow((BEST[0] + 40, BEST[1] + 40), (PTS[7][0] - 6, PTS[7][1] - 28), -0.45, 34), 6, 6.8, BLUE, 10, sfx="wood_low")
T("自己往回弹", 1700, 3100, 84, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 5–8）

scene("书里的飞行教官", "思考，快与慢 · 书中观点", (950, 4100, 0.85))
L(book(700, 4040, 380, 260), 0, 0.9, BLACK, 10, sfx="wood_low")
T("思考，快与慢", 700, 3820, 64, GREEN, k0=1, k1=2.5, sfx="pop")
L(kuai(1080, 4340, 0.6), 3, 3.8, RED, 9, sfx="pop")
L(face(1080, 4340, 0.6, "smile"), 3.8, 4.0, RED, 7)
L(man(1340, 4340, 0.6), 4, 4.8, BLUE, 9, sfx="wood_high")
L(face(1340, 4340, 0.6, "flat"), 4.8, 5.0, BLUE, 7)
L(plane(1210, 3830, 0.6, -10), 5, 5.8, BLACK, 8, sfx="wood_high")
T("空军教官的经验", 950, 4540, 64, k0=6, k1=7.75, sfx="pop")

scene("本事加运气", "书中观点 · 成绩", (2650, 4100, 0.85))
L(rect(2420, 4250, 260, 300, 14), 0, 0.9, BLUE, 10, sfx="wood_low")
T("本事", 2420, 4250, 64, BLUE, k0=1, k1=1.8, sfx="pop")
L(rect(2420, 3995, 260, 210, 14), 2, 2.8, ORANGE, 10, sfx="wood_high")
T("运气", 2420, 3995, 64, ORANGE, k0=3, k1=3.8, sfx="pop")
L(brace(2580, 3890, 4400, 40), 4, 4.8, RED, 9, sfx="wood_low")
T("成绩", 2800, 4150, 76, RED, k0=5, k1=5.8, sfx="pop")
T("成绩=本事+运气", 2650, 3700, 72, k0=6, k1=8, sfx="ding")

scene("运气不会一直好", "书中观点 · 回归平均", (950, 5600, 0.85))
L(dice(560, 5380, 6), 0, 0.9, RED, 9, sfx="wood_high")
L(dashes(820, 1380, 5600), 1, 1.8, GRAY, 8, sfx="wood_low")
T("平均", 1470, 5600, 54, GRAY, k0=1.8, k1=2.6)
L(circle(960, 5380, 20), 3, 3.6, RED, 16, sfx="pop")
L(dice(560, 5800, 2), 4, 4.8, BLUE, 9, sfx="wood_high")
L(circle(1250, 5575, 20), 5, 5.6, BLUE, 16, sfx="pop")
L(arrow((995, 5400), (1220, 5555), -0.25, 34), 6, 6.7, GRAY, 8, sfx="tom")
T("回归平均值", 950, 6030, 84, RED, k0=7, k1=8, sfx="ding")

scene("头天领先，次日回落", "书中例子 · 高尔夫", (2650, 5600, 0.85))
L(flag(2230, 5800), 0, 0.9, GREEN, 9, sfx="wood_high")
L(rect(2700, 5640, 170, 420, 10), 1, 1.8, BLUE, 10, sfx="pop")
T("头天", 2700, 5930, 56, k0=2, k1=2.8, sfx="pop")
L(rect(3020, 5720, 170, 260, 10), 3, 3.8, BLUE, 10, sfx="wood_high")
T("次日", 3020, 5930, 56, k0=4, k1=4.8, sfx="pop")
L(arrow((2750, 5395), (2990, 5555), -0.2, 36), 5, 5.8, RED, 9, sfx="tom")
T("领先的人往回落", 2780, 5230, 64, RED, k0=6, k1=7.75, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 9–10，示意）

scene("功劳记给了骂", "例子 · 业绩", (950, 7100, 0.85))
L(join(P((380, 7380), (1080, 7380)), rect(520, 7310, 150, 140, 8)), 0, 0.9, BLACK, 9, sfx="wood_low")
T("垫底", 520, 7180, 56, k0=1, k1=1.8, sfx="pop")
L(P((745, 6930), (700, 7010), (740, 7010), (695, 7090)), 2, 2.6, RED, 10, sfx="rim")
T("挨批", 720, 6840, 60, RED, k0=3, k1=3.8, sfx="pop")
L(rect(920, 7190, 150, 380, 8), 4, 4.8, GREEN, 9, sfx="wood_high")
L(kuai(1320, 7380, 0.6), 5, 5.8, RED, 9, sfx="pop")
L(face(1320, 7380, 0.6, "smile"), 5.8, 6.0, RED, 7)
T("骂管用！", 1320, 6930, 66, RED, k0=6, k1=7, sfx="kick")

scene("最差的组总会变好", "例子 · 新办法", (2650, 7100, 0.85))
T("最差的两个组", 2650, 6680, 70, k0=0, k1=1.5, sfx="pop")
L(join(rect(2360, 7130, 480, 560, 20), rect(2940, 7130, 480, 560, 20),
       circle(2360, 7350, 18), circle(2940, 7350, 18)), 2, 2.9, BLACK, 8, sfx="wood_high")
T("新办法", 2360, 6950, 56, GREEN, k0=3, k1=3.8, sfx="pop")
T("没动", 2940, 6950, 56, k0=4, k1=4.8, sfx="pop")
L(arrow((2360, 7320), (2360, 7060), 0, 40), 5, 5.7, GREEN, 10, sfx="tom")
L(arrow((2940, 7320), (2940, 7060), 0, 40), 6, 6.7, GREEN, 10, sfx="tom")
T("都变好了", 2650, 7560, 76, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 做法（场景 11–13，据书中思路整理）

ZIG = [(470 + i * 115, 8600 + v) for i, v in enumerate([-150, 120, -60, 200, 30, -180, 90, -40, 140])]
scene("看几个月的平均", "做法① · 看平均", (950, 8600, 0.85))
T("① 看平均", 950, 8170, 76, BLUE, k0=0, k1=1, sfx="pop")
L(dots_path(ZIG), 1, 1.9, BLACK, 12, sfx="wood_high")
L(P(*ZIG), 2, 2.8, GRAY, 5, sfx="wood_low")
C(3, 4, press_fn(420, 1390, 8605, 8330), sfx="tom")
T("平均", 1475, 8605, 54, GREEN, k0=5, k1=5.8, sfx="pop")
T("别只看一次", 950, 9010, 70, RED, k0=6, k1=7.25, sfx="rim")

scene("留一组不动的比", "做法② · 留对照组", (2650, 8600, 0.85))
T("② 留对照组", 2650, 8170, 76, BLUE, k0=0, k1=1, sfx="pop")
L(join(rect(2380, 8620, 440, 520, 20), rect(2920, 8620, 440, 520, 20)), 1, 1.9, BLACK, 8, sfx="wood_high")
T("新办法", 2380, 8440, 56, GREEN, k0=2, k1=2.8, sfx="pop")
T("不动", 2920, 8440, 56, k0=3, k1=3.8, sfx="pop")
L(arrow((2380, 8840), (2380, 8520), 0, 40), 4, 4.7, GREEN, 10, sfx="wood_high")
L(arrow((2920, 8840), (2920, 8680), 0, 40), 5, 5.7, GRAY, 10, sfx="wood_high")
L(join(dashes(2480, 2880, 8680, 24, 18), P((2440, 8520), (2480, 8520), (2480, 8680), (2440, 8680))), 6, 6.5, RED, 8,
  sfx="rim")
T("多出这截才算", 2650, 9020, 66, RED, k0=6.5, k1=8)

scene("该夸还是夸", "做法③ · 该夸就夸", (950, 10100, 0.85))
T("③ 夸了也别收回", 950, 9650, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(thumb(650, 10080, 1.2), 2, 2.9, GREEN, 10, sfx="wood_high")
L(cadet(1180, 10380, 0.65), 3, 3.8, BLUE, 9, sfx="pop")
L(face(1180, 10380, 0.65, "smile"), 3.8, 4.0, BLUE, 7)
T("回落很正常", 1180, 9880, 56, k0=4, k1=5.25, sfx="pop")
T("照样夸", 950, 10560, 84, RED, k0=6, k1=6.75, sfx="kick")
L(underline(800, 1100, 10620), 7, 7.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：拉远看全板 → 推到评论区

FULL = (1800, 5500, 0.1)
CMT = (2650, 10100, 0.8)
j14 = scene("评论区聊聊", "评论区见", FULL, bars=4)
b.move(j14, 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(kuai(2350, 10480, 0.6, "up"), 6, 6.8, RED, 9, sfx="pop")
L(face(2350, 10480, 0.6, "smile"), 6.8, 7.0, RED, 7)
L(man(2950, 10480, 0.6), 7, 7.8, BLUE, 9, sfx="wood_high")
L(face(2950, 10480, 0.6, "smile"), 7.8, 8.0, BLUE, 7)
T("你被“骂完就好”骗过吗？", 2650, 9830, 66, RED, k0=8, k1=10.75, sfx="pop")
T("下一讲：排期两周，为什么总拖成一个月？", 2650, 9990, 46, k0=11, k1=15.5, sfx="wood_high")
b.hit(j14, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "regress", "回归平均", "被骂完就变好，真是骂的功劳？", ACC, b.shots,
                 [f"{BOOK}第17章 所有表现都会回归平均值（Regression to the Mean）（转述）",
                  "中译本：胡晓姣、李爱民、何梦莹译，中信出版社 2012"],
                 "被骂完就变好|真是骂的【功劳】", SQUARE_SHOT,
                 ["书中观点均为转述：卡尼曼给以色列空军飞行教官讲课时，一位教官说学员飞得好被夸奖后，下一次常常变差，"
                  "飞得差被骂之后，下一次常常变好；卡尼曼解释这是回归平均——特别好或特别差的一次多半带着运气，下一次自然往"
                  "平均靠，跟夸或骂关系不大。成绩 = 本事 + 运气；高尔夫比赛第一天成绩特别好的人，第二天平均往回落。判断一个"
                  "办法有没有用要有对照组，不然回归平均会被当成办法的效果。见第17章“所有表现都会回归平均值”（Regression to "
                  "the Mean）。上屏均为转述，不是逐字引文。",
                  "开局教官骂学员“重飞”、夸完飞机歪着落地、“只骂不夸”为对书中这段对话的示意画面；成绩点、骰子点数 6 / 2、"
                  "头天与次日的成绩条为示意，不是书中数据。",
                  "业绩垫底挨批后回升、最差的两个组（试新办法的与没动的都变好）为现实场景示意，不指向任何具体公司或个人。",
                  "三个做法（看几个月的平均、留一组不动的对照、该夸照样夸）为据书中思路整理的建议。"],
                 tags="#管理 #反馈")
    return b.attach(ep)
