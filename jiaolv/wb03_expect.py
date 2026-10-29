"""03 过度期望（白板手绘版）：工资比爸妈高，为什么还觉得穷？

叙事：打工人切身问题开局（爸妈当年月薪几百，我现在是他们的十倍，外卖空调新手机都有 → 晚上刷到老同学新房到手 →
心里一下就慌）→ 书中观点（亮书《身份的焦虑》+ 德波顿；近两百年物质条件大大改善，焦虑却没少；我们只和自认为
同等的人比——同学、同事、邻居、亲戚，身边人一好就觉得自己差；书中引威廉·詹姆斯的公式：自尊 = 成就 ÷ 期望，
画成会动的分数：期望一涨自尊就掉，期望降下来自尊就回来；书中引卢梭：让人更富，可以多给钱，也可以减少他的欲望；
最后拉远画成一张图：身边人 → 期望 → 自尊）→ 身边的例子（同组同事升主管、朋友圈晒海边度假、过年饭桌上比表哥、
孩子要同款球鞋）→ 具体做法（看清在跟谁比 / 把想要的写下来逐条砍 / 跟去年的自己比 / 记下做成的事，让成就慢慢攒）
→ 评论区互动。
书中观点为转述（Alain de Botton, Status Anxiety, 2004，第一部分第三章“过度期望”；中译本《身份的焦虑》，
陈广兴、南治国译，上海译文出版社）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross, desk,
                               face, join, marker, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#C2872B"
SQUARE_SHOT = 11

b = Board(size=(3600, 9900))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12 if w < 200 else 40), P((x - w * 0.17, y + h / 2 - h * 0.13),
                                                           (x + w * 0.17, y + h / 2 - h * 0.13)))


def house(x, y, w=220, h=160) -> skia.Path:
    """小房子：(x, y) 为墙体中心。"""
    return join(rect(x, y, w, h, 6), P((x - w / 2 - 30, y - h / 2), (x, y - h / 2 - 110), (x + w / 2 + 30, y - h / 2)),
                P((x - 25, y + h / 2), (x - 25, y + h / 2 - 70), (x + 25, y + h / 2 - 70), (x + 25, y + h / 2)))


def zigzag(x0, x1, y, amp=28, n=10) -> skia.Path:
    pts = [(x0 + (x1 - x0) * i / n, y + (amp if i % 2 else -amp)) for i in range(n + 1)]
    return P(*pts)


def steps(x, y, n=3, w=150, h=100) -> skia.Path:
    """台阶：(x, y) 为最底层左下角，向右上升。"""
    pts = [(x, y)]
    for i in range(n):
        pts += [(x + i * w, y - (i + 1) * h), (x + (i + 1) * w, y - (i + 1) * h)]
    pts.append((x + n * w, y))
    return P(*pts, close=True)


def sun_sea(x, y, r=55) -> skia.Path:
    """太阳 + 两道浪：度假照。"""
    rays = [P((x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3), (x + math.cos(a) * r * 1.7,
                                                                       y + math.sin(a) * r * 1.7))
            for a in [i / 8 * 2 * math.pi for i in range(8)]]
    waves = []
    for dy in (150, 210):
        w = skia.Path()
        w.moveTo(x - 150, y + dy)
        for i in range(6):
            w.quadTo(x - 150 + i * 50 + 25, y + dy + (-20 if i % 2 == 0 else 20), x - 150 + (i + 1) * 50, y + dy)
        waves.append(w)
    return join(circle(x, y, r), *rays, *waves)


def sneaker(x, y, s=1.0) -> skia.Path:
    """球鞋（侧视）：(x, y) 为鞋底中点。"""
    body = P((x - 130 * s, y), (x - 130 * s, y - 90 * s), (x - 40 * s, y - 100 * s), (x + 10 * s, y - 50 * s),
             (x + 130 * s, y - 30 * s), (x + 140 * s, y), close=True)
    return join(body, P((x - 140 * s, y + 15 * s), (x + 150 * s, y + 15 * s)), P((x - 60 * s, y - 80 * s),
                                                                                (x - 20 * s, y - 60 * s)))


def table(x, y, w=560) -> skia.Path:
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 40, y), (x - w / 2 + 40, y + 110)),
                P((x + w / 2 - 40, y), (x + w / 2 - 40, y + 110)))


def notebook(x, y, w=380, h=440) -> skia.Path:
    rings = [circle(x - w / 2, y - h / 2 + 70 + i * 100, 16) for i in range(4)]
    return join(rect(x, y, w, h, 14), *rings)


def frac_fn(cx, cy, keys, size=80, prefix=True, bar=True):
    """会动的分数：成就 ÷ 期望（可带“自尊 =”前缀与右侧自尊柱）。

    keys：[(镜头, 拍, 成就倍数, 期望倍数, 自尊柱高度)]，每个关键帧从该拍起 0.35 秒缓动到位。
    出场按 k 依次显现：前缀 → 分子 → 分数线 → 分母 → 柱子。
    """

    def fn(c, k, t):
        num, den, lvl = 1.0, 1.0, 0.5
        for jj, kk, n2, d2, l2 in keys:
            f = ease_out(clamp01((t - b.t_of(jj, kk)) / 0.35))
            if f <= 0:
                break
            num, den, lvl = num + (n2 - num) * f, den + (d2 - den) * f, lvl + (l2 - lvl) * f

        def a(th):
            return clamp01((k - th) / 0.15)

        x0 = cx
        if prefix:
            K.text(c, "自尊", cx - 470, cy, size, "hand", BLUE, a(0.0))
            K.text(c, "=", cx - 320, cy, size, "hand", BLACK, a(0.15))
            x0 = cx + 10
        K.text(c, "成就", x0, cy - 30 - size * num * 0.55, size * num, "hand", GREEN, a(0.3))
        lw = max(150, size * 1.1 * max(num, den, 1.0))
        if a(0.45) > 0:
            c.drawPath(P((x0 - lw * a(0.45), cy), (x0 + lw * a(0.45), cy)), marker(BLACK, 9))
        K.text(c, "期望", x0, cy + 30 + size * den * 0.55, size * den, "hand", RED, a(0.6))
        if bar and a(0.8) > 0:
            bx, bh = cx + 420, 420
            K.rr(c, bx, cy + bh / 2 - bh * lvl / 2, 80, bh * lvl, 10, BLUE, 0.55 * a(0.8))
            c.drawRoundRect(skia.Rect.MakeXYWH(bx - 45, cy - bh / 2, 90, bh), 14, 14, marker(BLACK, 8, a(0.8)))
            K.text(c, "自尊", bx, cy + bh / 2 + 70, 52, "hand", BLUE, a(0.8))
        return None

    return fn


# ---------------------------------------------------------------- 开局：工资比爸妈高（镜头 1–6）

b.shot("爸妈当年挣这么多", "灵魂拷问", view=(950, 850, 0.85))
L(stick(650, 1180, 0.8, hair=True), 0, 0.6, sfx="wood_high")
L(face(650, 1180, 0.8, "smile"), 0.6, 0.7)
T("爸妈当年", 950, 520, 76, k0=1, sfx="pop")
T("月薪 ¥500", 1130, 860, 72, GREEN, k0=2, sfx="pop")
L(underline(950, 1310, 920), 3, 3.4, GREEN, 7, sfx="wood_high")

b.shot("我现在挣十倍", "灵魂拷问", view=(2650, 850, 0.85))
L(stick(2350, 1180, 0.8, "up"), 0, 0.6, BLUE, sfx="wood_high")
L(face(2350, 1180, 0.8, "smile"), 0.6, 0.7, BLUE)
T("我现在", 2650, 520, 76, k0=1, sfx="pop")
T("月薪 ¥5000", 2840, 860, 72, GREEN, k0=2, k1=2.8, sfx="pop")
T("×10", 2950, 1060, 100, RED, k0=3, k1=3.3, sfx="ding")

b.shot("日子比他们好多了", "灵魂拷问", view=(950, 1750, 0.85))
for n, w in enumerate(("外卖随时点", "空调开一夜", "手机换新的")):
    T(w, 900, 1560 + n * 170, 66, k0=n, sfx="pop")
    L(check(1250, 1550 + n * 170, 40), n + 0.6, n + 0.85, GREEN, 9)
L(underline(640, 1160, 1990), 3, 3.4, GREEN, 7, sfx="wood_high")

b.shot("晚上刷到老同学", "灵魂拷问", view=(2650, 1750, 0.85))
L(phone(2450, 1790, 480, 720), 0, 0.8, BLACK, 9, sfx="wood_high")
T("老同学", 2450, 1540, 56, k0=1, sfx="pop")
L(house(2450, 1770, 200, 140), 2, 2.6, BLACK, 8, sfx="pop")
T("新房到手！", 2450, 1950, 54, RED, k0=3, k1=3.3, sfx="pop")

b.shot("心里一下就慌了", "灵魂拷问", view=(2650, 1800, 0.85))
L(stick(3030, 2150, 0.7, "hold"), 0, 0.5, BLUE, 9, sfx="wood_high")
L(face(3030, 2150, 0.7, "sad"), 0.5, 0.6, BLUE, 8)
L(scribble(3030, 2010, 110, 70, 6), 1, 1.4, RED, 7, sfx="shaker")
T("慌", 3150, 1580, 120, RED, k0=2, k1=2.4, sfx="rim")
T("！", 3260, 1580, 100, RED, k0=3, k1=3.2, sfx="pop")

b.shot("钱多了，还觉得穷？", "灵魂拷问", view=(1800, 1350, 0.42), flashes=[0])
T("？", 1800, 1420, 560, RED, k0=0, k1=0.6, sfx="kick")
T("钱多了，还觉得穷", 1800, 2280, 100, k0=1.0, k1=2.2, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "身份的焦虑", view=(1000, 2950, 0.9))
L(book(750, 2950, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 750, 2710, 76, GREEN, k0=1.0, k1=1.5, sfx="pop")
T("阿兰 · 德波顿", 750, 3190, 52, k0=1.5, k1=1.95)
T("身份 = 社会地位", 1250, 3330, 52, RED, k0=2.0, k1=2.6, sfx="pop")
L(underline(1060, 1440, 3380, 10, 30), 3, 3.25, RED, 7, sfx="wood_high")

AX = (2030, 3250)
b.shot("这两百年变富了", "书中观点 · 变富", view=(2650, 2950, 0.85))
L(P((AX[0], 2560), AX, (3230, AX[1])), 0, 0.6, BLACK, 9, sfx="wood_high")
T("两百年前", 2170, 3330, 52, k0=1, sfx="pop")
T("现在", 3120, 3330, 52, k0=1.5)
L(P((2060, 3200), (2450, 3170), (2750, 3070), (2980, 2900), (3200, 2640)), 2, 2.5, GREEN, 11, sfx="wood_high")
T("吃穿住用", 2420, 2700, 60, GREEN, k0=2.5, k1=3.0)
H(3, "ding", 0.7)

b.shot("焦虑却没少", "书中观点 · 焦虑没少", view=(2650, 2950, 0.85), shake=[0], flashes=[0])
L(zigzag(2060, 3220, 2960, 30, 12), 0, 0.4, RED, 12, sfx="kick")
b.hit(J(), 0, "cymbal", 0.5)
T("焦虑", 3130, 2860, 60, RED, k0=1, sfx="tom")
T("一点没少！", 2650, 2440, 96, RED, k0=2, k1=2.6, sfx="rim")
H(3, "tom", 0.7)

ME = (950, 4200)
b.shot("我们只跟身边人比", "书中观点 · 跟谁比", view=(950, 3900, 0.85))
L(stick(*ME, 0.65), 0, 0.5, BLUE, 9, sfx="wood_high")
L(face(*ME, 0.65, "flat"), 0.5, 0.6, BLUE, 8)
for n, (w, x, y) in enumerate((("同学", 600, 3640), ("同事", 1300, 3640), ("邻居", 560, 4180), ("亲戚", 1340, 4180))):
    T(w, x, y, 62, k0=1 + n * 0.5, k1=1.4 + n * 0.5, sfx="pop" if n % 2 == 0 else None)
L(circle(950, 4000, 300), 3, 3.6, GREEN, 7, sfx="wood_high")

b.shot("同学过得好一点", "书中观点 · 跟谁比", view=(950, 3900, 0.85))
L(arrow((470, 3700), (470, 3540), 0, 36), 0, 0.4, GREEN, 9, sfx="wood_high")
T("买房", 620, 3540, 54, GREEN, k0=1, sfx="pop")
L(arrow((1170, 3700), (1170, 3540), 0, 36), 2, 2.4, GREEN, 9, sfx="wood_high")
T("升职", 1300, 3540, 54, GREEN, k0=3, k1=3.3, sfx="pop")

b.shot("我就觉得自己差", "书中观点 · 跟谁比", view=(950, 3900, 0.85))
L(face(*ME, 0.65, "sad"), 0, 0.3, BLUE, 8, sfx="pop")
T("差", 1130, 3880, 100, RED, k0=1, k1=1.4, sfx="rim")
L(arrow((780, 3820), (780, 4060), 0, 36), 2, 2.4, BLUE, 9, sfx="wood_high")
H(3, "tom", 0.6)

FR = (2650, 3950)
j_f = b.shot("书里引了个公式", "书中观点 · 詹姆斯", view=(2650, 3900, 0.85))
T("威廉 · 詹姆斯", 2650, 3480, 66, k0=0, sfx="pop")
T("心理学家", 2650, 3590, 52, k0=1, sfx="pop")
L(underline(2420, 2880, 3640, 10, 30), 2, 2.4, RED, 7, sfx="ding")
H(3, "wood_high", 0.6)

b.shot("成就除以期望", "书中观点 · 公式", view=(2650, 3900, 0.85))
b.custom(J(), 0, 2.6, frac_fn(*FR, [(j_f + 2, 0, 1.0, 1.8, 0.25), (j_f + 2, 2, 1.0, 2.0, 0.12),
                                     (j_f + 3, 0, 1.0, 0.75, 0.75), (j_f + 3, 2, 1.0, 0.75, 0.9)]), sfx="pop")
H(1, "wood_high", 0.7)
H(2, "pop", 0.7)
H(3, "ding", 0.6)

b.shot("期望一涨就难受", "书中观点 · 期望涨", view=(2650, 3950, 0.85), shake=[2])
H(0, "tom")
H(2, "kick", 0.7)
T("↓", 3170, 3780, 90, RED, k0=3, k1=3.3, sfx="rim")

b.shot("期望降下来也行", "书中观点 · 期望降", view=(2650, 3950, 0.85))
H(0, "pop")
b.erase(J(), 1.5, 1.9, 3170, 3780, 120, 150)
H(2, "ding")
T("↑", 3170, 3780, 90, GREEN, k0=3, k1=3.3, sfx="pop")

b.shot("少要点也是富", "书中观点 · 一张图", view=(1800, 3600, 0.355))
L(arrow((1420, 3950), (2060, 3950), -0.12, 50), 0, 0.6, GREEN, 10, sfx="wood_high")
T("卢梭：多挣钱，或者少想要", 1800, 4560, 120, k0=1, k1=2.6, sfx="pop")
L(underline(1000, 2600, 4650, 16, 50), 3, 3.5, RED, 9, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5600), (2650, 5600), (950, 6450), (2650, 6450)]
b.shot("身边天天都在比", "身边的例子", view=(1800, 6000, 0.355))
T("身边的例子", 1800, 5000, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 780, 40), 1 + n * 0.5, 1.4 + n * 0.5, GREEN, 8, sfx="wood_high" if n % 2 == 0 else None)

b.shot("同组同事升职了", "例子 · 职场", view=(950, 5600, 0.85))
L(steps(950, 5900, 3, 130, 90), 0, 0.6, BLACK, 9, sfx="wood_high")
L(stick(1280, 5630, 0.55, "up", tie=True), 1, 1.4, BLACK, 9, sfx="pop")
L(face(1280, 5630, 0.55, "smile"), 1.4, 1.5)
T("升主管", 1280, 5370, 60, GREEN, k0=2, sfx="pop")
H(3, "ding", 0.6)

b.shot("我涨薪也不香了", "例子 · 职场", view=(950, 5600, 0.85))
L(stick(600, 5900, 0.6), 0, 0.5, BLUE, 9, sfx="wood_high")
T("涨薪 +8%", 620, 5440, 58, GREEN, k0=1, sfx="pop")
L(face(600, 5900, 0.6, "sad"), 2, 2.2, BLUE, 8, sfx="rim")
T("唉", 770, 5600, 60, k0=3, sfx="pop")

b.shot("朋友圈晒度假", "例子 · 生活", view=(2650, 5600, 0.85))
L(phone(2400, 5610, 420, 640), 0, 0.7, BLACK, 9, sfx="wood_high")
L(sun_sea(2400, 5480, 45), 1, 1.6, BLACK, 7, sfx="pop")
T("海边度假", 2400, 5370 - 20, 50, k0=1.7)
T("赞 99+", 2400, 5800, 52, RED, k0=2, sfx="pop")
H(3, "pop", 0.6)

b.shot("我宅家就心虚", "例子 · 生活", view=(2650, 5600, 0.85))
L(stick(2830, 5900, 0.6), 0, 0.5, BLUE, 9, sfx="wood_high")
L(desk(3080, 5790, 260), 1, 1.5, BLACK, 8, sfx="pop")
T("周末宅家", 2980, 5320, 56, k0=2, sfx="pop")
L(face(2830, 5900, 0.6, "sad"), 3, 3.2, BLUE, 8, sfx="rim")

b.shot("过年饭桌上比", "例子 · 家庭", view=(950, 6450, 0.85))
L(table(870, 6730, 520), 0, 0.4, BLACK, 10, sfx="wood_high")
for n, x in enumerate((700, 880)):
    L(stick(x, 6720, 0.5, hair=n == 0), 1 + n * 0.3, 1.3 + n * 0.3, BLACK, 9, sfx="pop" if n == 0 else None)
L(bubble(800, 6230, 480, 120, -1), 2, 2.3, BLACK, 8, sfx="pop")
T("你看人家表哥", 800, 6230, 54, k0=2.3, k1=3.0)
H(3, "wood_high", 0.6)

b.shot("爸妈也跟着叹气", "例子 · 家庭", view=(950, 6450, 0.85))
L(stick(1250, 6720, 0.5), 0, 0.4, BLUE, 9, sfx="wood_high")
L(face(1250, 6720, 0.5, "sad"), 1, 1.2, BLUE, 8, sfx="rim")
for n, x in enumerate((700, 880)):
    L(face(x, 6720, 0.5, "sad"), 2 + n * 0.3, 2.2 + n * 0.3, BLACK, 8, sfx="pop" if n == 0 else None)
T("唉……", 780, 6440, 54, k0=3, k1=3.3, sfx="pop")

b.shot("孩子要同款球鞋", "例子 · 孩子", view=(2650, 6450, 0.85))
L(stick(2300, 6760, 0.42, "up"), 0, 0.4, BLACK, 8, sfx="wood_high")
L(sneaker(2700, 6560, 1.0), 1, 1.6, BLACK, 9, sfx="pop")
T("同款", 2700, 6340, 62, RED, k0=2, sfx="pop")
T("¥899", 3050, 6480, 58, RED, k0=3, k1=3.3, sfx="pop")

b.shot("说班上都有", "例子 · 孩子", view=(2650, 6450, 0.85))
L(bubble(2330, 6230, 380, 110, -1), 0, 0.3, BLUE, 8, sfx="pop")
T("班上都有！", 2330, 6230, 52, BLUE, k0=0.3)
L(stick(3080, 6800, 0.5, "shrug"), 1, 1.5, BLACK, 9, sfx="wood_high")
L(face(3080, 6800, 0.5, "flat"), 1.5, 1.6)
T("……", 3080, 6600, 56, k0=2, sfx="rim")
H(3, "pop", 0.6)

b.shot("比的都是身边人", "身边的例子", view=(1800, 6000, 0.355))
T("身边人", 1800, 6025, 120, RED, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(arrow((1800 + (x - 1800) * 0.2, 6025 + (y - 6025) * 0.2), (1800 + (x - 1800) * 0.36, 6025 + (y - 6025) * 0.36),
            0.1, 40), 1 + n * 0.5, 1.4 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)

b.shot("期望被越抬越高", "身边的例子", view=(1800, 6000, 0.355), shake=[0])
T("期望 ↑  自尊 ↓", 1800, 6980, 140, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 7850), (2650, 7850), (950, 8700), (2650, 8700)]
b.shot("觉得穷，这样办", "具体做法", view=(1800, 8250, 0.355))
T("觉得穷，这样做", 1800, 7250, 130, k0=0, k1=1.2, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 780, 40), 1.4 + n * 0.4, 1.75 + n * 0.4, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("先看在跟谁比", "第一步 · 跟谁比", view=(950, 7850, 0.85))
T("① 看清跟谁比", 950, 7560, 74, BLUE, k0=0, sfx="pop")
L(stick(620, 8180, 0.6), 1, 1.5, BLUE, 9, sfx="wood_high")
L(face(620, 8180, 0.6, "flat"), 1.5, 1.6, BLUE, 8)
L(bubble(1080, 7760, 440, 120, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("我在跟谁比？", 1080, 7760, 54, k0=2.4)

b.shot("写下让你慌的人", "第一步 · 跟谁比", view=(950, 7900, 0.85))
for n, w in enumerate(("老同学", "表哥", "隔壁组小王")):
    T(w, 1120, 7950 + n * 90, 54, k0=n, sfx="pop")
L(rect(1120, 8040, 380, 290, 30), 3, 3.3, RED, 7, sfx="ding")

b.shot("把想要的写下来", "第二步 · 写期望", view=(2650, 7850, 0.85))
T("② 写下想要的", 2650, 7560, 74, BLUE, k0=0, sfx="pop")
ITEMS = ("买套房子", "换辆新车", "出去旅游", "最新手机")
for n, w in enumerate(ITEMS):
    T(w, 2480, 7710 + n * 105, 56, k0=1 + n * 0.5, k1=1.4 + n * 0.5, sfx="pop" if n % 2 == 0 else None)

b.shot("一条条问自己", "第二步 · 写期望", view=(2650, 7850, 0.85))
T("真需要吗？", 3000, 7710, 58, RED, k0=0, sfx="pop")
L(check(2780, 7705, 34), 1, 1.25, GREEN, 9, sfx="ding")
L(check(2780, 7915, 34), 2, 2.25, GREEN, 9, sfx="ding")
H(3, "wood_high", 0.6)

b.shot("不需要就划掉", "第二步 · 写期望", view=(2650, 7850, 0.85))
L(P((2350, 7815), (2610, 7815)), 0, 0.3, RED, 10, sfx="rim")
L(P((2350, 8025), (2610, 8025)), 1, 1.3, RED, 10, sfx="rim")
T("期望 ↓", 3020, 7950, 64, RED, k0=2, sfx="pop")
T("自尊 ↑", 3020, 8070, 64, GREEN, k0=3, k1=3.3, sfx="ding")

b.shot("跟去年的自己比", "第三步 · 换个比法", view=(950, 8700, 0.85))
T("③ 跟去年的自己比", 950, 8410, 70, BLUE, k0=0, sfx="pop")
L(stick(620, 9020, 0.55), 1, 1.4, BLACK, 9, sfx="wood_high")
T("去年", 620, 8760, 52, k0=1.4)
L(stick(1280, 9020, 0.55, "up"), 2, 2.4, BLUE, 9, sfx="pop")
T("今年", 1280, 8760, 52, BLUE, k0=2.4)
L(arrow((760, 8930), (1140, 8930), -0.1, 36), 3, 3.4, GREEN, 8, sfx="wood_high")

b.shot("多存了一笔钱", "第三步 · 换个比法", view=(950, 8700, 0.85))
T("存款 +6000", 950, 8560, 58, GREEN, k0=0, sfx="pop")
L(check(1180, 8555, 32), 2, 2.25, GREEN, 9, sfx="ding")
H(3, "pop", 0.6)

b.shot("还学会了做饭", "第三步 · 换个比法", view=(950, 8700, 0.85))
T("会做三个菜", 950, 8660, 58, GREEN, k0=0, sfx="pop")
L(check(1180, 8655, 32), 1, 1.25, GREEN, 9, sfx="ding")
L(face(1280, 9020, 0.55, "smile"), 2, 2.2, BLUE, 8, sfx="pop")

b.shot("把做成的事记下", "第四步 · 记成就", view=(2650, 8700, 0.85))
T("④ 记下做成的事", 2650, 8410, 70, BLUE, k0=0, sfx="pop")
L(notebook(2470, 8800, 380, 420), 1, 1.6, BLACK, 8, sfx="wood_high")
for n, w in enumerate(("改完方案", "按时下班", "陪娃搭积木")):
    T(w, 2480, 8680 + n * 110, 50, k0=2 + n * 0.45, k1=2.3 + n * 0.45, sfx="pop" if n != 1 else None)

b.shot("一天记一两件", "第四步 · 记成就", view=(2650, 8700, 0.85))
for n in range(3):
    L(check(2730, 8675 + n * 110, 28), n, n + 0.25, GREEN, 8, sfx="ding" if n != 1 else "pop")

j_s = b.shot("成就慢慢攒起来", "第四步 · 记成就", view=(2650, 8700, 0.85))
b.custom(J(), 0, 0.8, frac_fn(3030, 8780, [(j_s, 1, 1.6, 1.0, 0.5)], size=56, prefix=False, bar=False), sfx="pop")
H(1, "ding")
T("自尊 ↑", 3030, 9010, 56, GREEN, k0=2, sfx="pop")

b.shot("少比一点，就松一点", "一句话", view=(1800, 4900, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 9550, 0.8))
T("你最常跟谁比？", 1800, 9470, 80, RED, k0=0.5, k1=1.8)
T("下一讲：混得不好，就怪自己不够努力？", 1800, 9630, 48, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(3, "expect", "过度期望", "工资比爸妈高，为什么还觉得穷？", ACC, b.shots,
                 [f"{BOOK}第一部分第三章“过度期望”（转述）",
                  "书中引用：威廉·詹姆斯的自尊公式（自尊 = 成就 ÷ 期望）；卢梭关于减少欲望也能使人富有的说法（均为转述）",
                  "中译本：《身份的焦虑》，阿兰·德波顿著，陈广兴、南治国译，上海译文出版社"],
                 "工资比爸妈高|为什么还【觉得穷】", SQUARE_SHOT,
                 ["书中观点均为转述：近两百年来物质条件大大改善，身份焦虑却没有减少；人只和自认为同等的人（同学、同事、邻居等）"
                  "比较，身边人过得好一点，自己就觉得差；书中引威廉·詹姆斯的公式：自尊 = 成就 ÷ 期望，提高成就或降低期望都能"
                  "让自尊上去；书中引卢梭：让一个人更富有，可以给他更多钱，也可以减少他的欲望。出处：Alain de Botton, Status "
                  "Anxiety (Hamish Hamilton / Pantheon, 2004)，第一部分第三章“过度期望”；中译本《身份的焦虑》（陈广兴、南治国译，"
                  "上海译文出版社）。上屏均为转述，不是逐字引文。",
                  "爸妈当年月薪 ¥500、我现在 ¥5000、涨薪 +8%、¥899 球鞋、存款 +6000 等数字均为示意；“两百年”曲线为对书中观点的"
                  "通俗化示意，不是统计数据；分数与自尊柱的变化为公式的动态示意。同事升主管、朋友圈度假照、过年饭桌比表哥、"
                  "孩子要同款球鞋均为现实场景示意，不指向任何具体公司或个人。",
                  "四步做法（看清在跟谁比、把想要的写下来逐条划掉不需要的、跟去年的自己比、记下做成的事让成就慢慢攒）为据书中"
                  "思路（自尊公式与卢梭的说法）整理的建议。"],
                 tags="#攀比 #消费")
    return b.attach(ep)
