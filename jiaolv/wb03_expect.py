"""03 过度期望（白板手绘版）：工资比爸妈高，为什么还觉得穷？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
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
SQUARE_SHOT = 5

b = Board(size=(3600, 13550))


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


# ---------------------------------------------------------------- 开局：工资比爸妈高（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。
# 各区块上下留足间距，推近时上一区块的字不会漏进画面顶部和页眉。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("我挣的是爸妈十倍", "灵魂拷问", (1800, 760, 0.55))
L(stick(1250, 1100, 1.2, hair=True), 0, 0.6, sfx="wood_high")
L(face(1250, 1100, 1.2, "smile"), 0.6, 0.7)
T("爸妈当年", 1250, 340, 96, k0=1, sfx="pop")
T("月薪 ¥500", 1250, 520, 84, GREEN, k0=2, k1=2.8, sfx="pop")
L(stick(2250, 1100, 1.2, "up"), 3, 3.6, BLUE, sfx="wood_high")
L(face(2250, 1100, 1.2, "smile"), 3.6, 3.7, BLUE)
T("我现在", 2250, 340, 96, k0=3.7, k1=4.0)
T("月薪 ¥5000", 2250, 520, 84, GREEN, k0=4, k1=4.8, sfx="pop")
T("×10", 2640, 880, 140, RED, k0=5, k1=5.4, sfx="ding")

scene("日子比他们好多了", "灵魂拷问", (950, 2100, 0.85))
for n, w in enumerate(("外卖随时点", "空调开一夜", "手机换新的")):
    T(w, 900, 1910 + n * 170, 66, k0=n, sfx="pop")
    L(check(1250, 1900 + n * 170, 40), n + 0.6, n + 0.85, GREEN, 9)
L(underline(640, 1160, 2340), 3, 3.4, GREEN, 7, sfx="wood_high")
H(4, "ding", 0.6)

scene("刷到新房，心就慌了", "灵魂拷问", (2650, 2050, 0.85), shake=[5], flashes=[5])
L(phone(2450, 2040, 480, 720), 0, 0.8, BLACK, 9, sfx="wood_high")
T("老同学", 2450, 1790, 56, k0=1, sfx="pop")
L(house(2450, 2020, 200, 140), 2, 2.6, BLACK, 8, sfx="pop")
T("新房到手！", 2450, 2200, 54, RED, k0=2.6, k1=3.0)
L(stick(3030, 2400, 0.7, "hold"), 3, 3.5, BLUE, 9, sfx="wood_high")
L(face(3030, 2400, 0.7, "sad"), 3.5, 3.6, BLUE, 8)
L(scribble(3030, 2260, 110, 70, 6), 3.6, 4.0, RED, 7)
T("慌！", 3220, 2000, 110, RED, k0=4, k1=4.4, sfx="rim")
T("钱多了，怎么还觉得穷？", 2650, 1580, 72, RED, k0=5, k1=6, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

scene("有本书讲过这个", "身份的焦虑", (1000, 3600, 0.9))
L(book(750, 3600, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 750, 3360, 76, GREEN, k0=1, k1=1.8, sfx="pop")
T("阿兰 · 德波顿", 750, 3840, 52, k0=2, k1=2.8, sfx="wood_high")
T("身份 = 社会地位", 1330, 3570, 58, RED, k0=3, k1=3.9, sfx="pop")
L(underline(1110, 1550, 3625, 10, 30), 4, 4.3, RED, 7, sfx="ding")

AX = (2030, 3900)
scene("日子变富，焦虑没少", "书中观点 · 焦虑没少", (2650, 3600, 0.85), shake=[0], flashes=[0])
L(P((AX[0], 3210), AX, (3230, AX[1])), 0, 0.5, BLACK, 9, sfx="kick")
b.hit(J(), 0, "cymbal", 0.5)
T("两百年前", 2170, 3980, 52, k0=1, k1=1.5, sfx="pop")
T("现在", 3120, 3980, 52, k0=1.5, k1=1.8)
L(P((2060, 3850), (2450, 3820), (2750, 3720), (2980, 3550), (3200, 3290)), 2, 2.5, GREEN, 11, sfx="wood_high")
T("吃穿住用", 2420, 3350, 60, GREEN, k0=2.5, k1=3.0)
L(zigzag(2060, 3220, 3610, 30, 12), 3, 3.5, RED, 12, sfx="rim")
T("焦虑", 3130, 3510, 60, RED, k0=4, k1=4.4, sfx="tom")
T("一点没少！", 2650, 3090, 96, RED, k0=5, k1=5.6, sfx="rim")

ME = (950, 5130)
scene("身边人好，我就觉得差", "书中观点 · 跟谁比", (950, 4830, 0.85))
L(stick(*ME, 0.65), 0, 0.5, BLUE, 9, sfx="wood_high")
L(face(*ME, 0.65, "flat"), 0.5, 0.6, BLUE, 8)
for n, (w, x, y) in enumerate((("同学", 600, 4570), ("同事", 1300, 4570), ("邻居", 560, 5110), ("亲戚", 1340, 5110))):
    T(w, x, y, 62, k0=1 + n * 0.4, k1=1.3 + n * 0.4, sfx="pop" if n == 0 else None)
L(arrow((470, 4630), (470, 4470), 0, 36), 3, 3.3, GREEN, 9, sfx="wood_high")
T("买房", 620, 4470, 54, GREEN, k0=3.3, k1=3.7)
L(arrow((1170, 4630), (1170, 4470), 0, 36), 3.7, 4.0, GREEN, 9)
T("升职", 1300, 4470, 54, GREEN, k0=4, k1=4.3, sfx="pop")
L(arrow((780, 4750), (780, 4990), 0, 36), 4.5, 4.9, BLUE, 9)
T("差", 1130, 4810, 100, RED, k0=5, k1=5.4, sfx="rim")

FR = (2650, 5020)
j_f = scene("自尊看成就除以期望", "书中观点 · 詹姆斯的公式", (2650, 4970, 0.85))
T("威廉 · 詹姆斯", 2650, 4550, 66, k0=0, k1=1.0, sfx="pop")
T("心理学家", 2650, 4660, 52, k0=1, k1=1.6, sfx="wood_high")
L(underline(2420, 2880, 4710, 10, 30), 1.6, 1.9, RED, 7)
H(3, "wood_high", 0.6)
H(4, "ding", 0.6)

j_m = scene("期望越高，自尊越低", "书中观点 · 期望涨跌", (2650, 5000, 0.85), shake=[1])
b.custom(j_f, 2, 4.6, frac_fn(*FR, [(j_m, 0, 1.0, 1.8, 0.25), (j_m, 1, 1.0, 2.0, 0.12),
                                    (j_m, 3, 1.0, 0.75, 0.75), (j_m, 4, 1.0, 0.75, 0.9)]), sfx="pop")
H(0, "tom")
H(1, "kick", 0.7)
T("↓", 3170, 4850, 90, RED, k0=2, k1=2.3, sfx="rim")
H(3, "pop")
b.erase(J(), 3, 3.4, 3170, 4850, 120, 150)
H(4, "ding")
T("↑", 3170, 4850, 90, GREEN, k0=5, k1=5.3, sfx="pop")

scene("少想要，也算富", "书中观点 · 卢梭", (1800, 4500, 0.355))
L(arrow((1420, 4880), (2060, 5020), -0.12, 50), 0, 0.6, GREEN, 10, sfx="wood_high")
T("卢梭：多挣钱，或者少想要", 1800, 5440, 120, k0=1, k1=3.2, sfx="pop")
L(underline(1000, 2600, 5520, 16, 50), 4, 4.5, RED, 9, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 7720), (2650, 7720), (950, 8920), (2650, 8920)]
CY = 8320
VC = (1800, 8220, 0.3)
scene("身边天天都在比", "身边的例子", VC)
T("身边的例子", 1800, 6690, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 780, 40), 1 + n * 0.5, 1.4 + n * 0.5, GREEN, 8, sfx="wood_high" if n % 2 == 0 else None)
H(4, "ding", 0.6)

scene("同事升职，我涨薪不香", "例子 · 职场", (950, 7720, 0.85))
L(steps(950, 8020, 3, 130, 90), 0, 0.6, BLACK, 9, sfx="wood_high")
L(stick(1280, 7750, 0.55, "up", tie=True), 1, 1.4, BLACK, 9, sfx="pop")
L(face(1280, 7750, 0.55, "smile"), 1.4, 1.5)
T("升主管", 1280, 7490, 60, GREEN, k0=2, sfx="pop")
L(stick(600, 8020, 0.6), 3, 3.5, BLUE, 9, sfx="wood_high")
T("涨薪 +8%", 620, 7560, 58, GREEN, k0=4, sfx="pop")
T("唉", 770, 7720, 60, k0=4.6, k1=5.0)
L(face(600, 8020, 0.6, "sad"), 5, 5.2, BLUE, 8, sfx="rim")

scene("别人度假，我宅家心虚", "例子 · 生活", (2650, 7720, 0.85))
L(phone(2400, 7730, 420, 640), 0, 0.7, BLACK, 9, sfx="wood_high")
L(sun_sea(2400, 7600, 45), 1, 1.6, BLACK, 7, sfx="pop")
T("海边度假", 2400, 7470, 50, k0=1.6, k1=2.0)
T("赞 99+", 2400, 7920, 52, RED, k0=2, sfx="pop")
L(stick(2830, 8020, 0.6), 3, 3.5, BLUE, 9, sfx="wood_high")
L(desk(3080, 7910, 260), 3.5, 4.0, BLACK, 8)
T("周末宅家", 2980, 7440, 56, k0=4, sfx="pop")
L(face(2830, 8020, 0.6, "sad"), 5, 5.2, BLUE, 8, sfx="rim")

scene("过年饭桌上比表哥", "例子 · 家庭", (950, 8920, 0.85))
L(table(870, 9200, 520), 0, 0.4, BLACK, 10, sfx="wood_high")
for n, x in enumerate((700, 880)):
    L(stick(x, 9190, 0.5, hair=n == 0), 1 + n * 0.3, 1.3 + n * 0.3, BLACK, 9, sfx="pop" if n == 0 else None)
L(bubble(800, 8700, 480, 120, -1), 2, 2.3, BLACK, 8, sfx="pop")
T("你看人家表哥", 800, 8700, 54, k0=2.3, k1=3.0)
L(stick(1250, 9190, 0.5), 3, 3.4, BLUE, 9, sfx="wood_high")
for n, x in enumerate((700, 880)):
    L(face(x, 9190, 0.5, "sad"), 4 + n * 0.3, 4.2 + n * 0.3, BLACK, 8, sfx="pop" if n == 0 else None)
L(face(1250, 9190, 0.5, "sad"), 5, 5.2, BLUE, 8, sfx="rim")

scene("孩子要同款球鞋", "例子 · 孩子", (2650, 8920, 0.85))
L(stick(2300, 9230, 0.42, "up"), 0, 0.4, BLACK, 8, sfx="wood_high")
L(sneaker(2700, 9030, 1.0), 1, 1.6, BLACK, 9, sfx="pop")
T("同款", 2700, 8810, 62, RED, k0=2, k1=2.4, sfx="pop")
T("¥899", 3050, 8950, 58, RED, k0=2.5, k1=2.9)
L(bubble(2330, 8700, 380, 110, -1), 3, 3.3, BLUE, 8, sfx="pop")
T("班上都有！", 2330, 8700, 52, BLUE, k0=3.3, k1=4.0)
L(stick(3080, 9270, 0.5, "shrug"), 4, 4.5, BLACK, 9, sfx="wood_high")
L(face(3080, 9270, 0.5, "flat"), 4.5, 4.6)
T("……", 3080, 9020, 56, k0=5, k1=5.5, sfx="rim")

scene("比的都是身边人", "身边的例子", VC, shake=[4])
T("身边人", 1800, CY, 120, RED, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(arrow((1800 + (x - 1800) * 0.2, CY + (y - CY) * 0.25), (1800 + (x - 1800) * 0.36, CY + (y - CY) * 0.42),
            0.1, 40), 1 + n * 0.5, 1.4 + n * 0.5, RED, 9, sfx="wood_high" if n % 2 == 0 else None)
T("期望 ↑  自尊 ↓", 1800, 9500, 140, RED, k0=4, k1=4.8, sfx="kick")
H(5, "ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

Y1, Y2 = 10550, 11800
scene("先看清在跟谁比", "第一步 · 跟谁比", (950, Y1 + 30, 0.85))
L(rect(950, Y1, 1200, 780, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("① 看清跟谁比", 950, Y1 - 290, 74, BLUE, k0=1, k1=1.8, sfx="pop")
L(stick(620, Y1 + 330, 0.6), 1.8, 2.2, BLUE, 9)
L(face(620, Y1 + 330, 0.6, "flat"), 2.2, 2.3, BLUE, 8)
L(bubble(1080, Y1 - 90, 440, 120, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("我在跟谁比？", 1080, Y1 - 90, 54, k0=2.4, k1=3.0)
for n, w in enumerate(("老同学", "表哥", "隔壁组小王")):
    T(w, 1120, Y1 + 100 + n * 90, 54, k0=3 + n * 0.5, k1=3.4 + n * 0.5 + (0.3 if n == 2 else 0),
      sfx="pop" if n == 0 else None)
L(rect(1120, Y1 + 190, 380, 290, 30), 5, 5.4, RED, 7, sfx="ding")

ITEMS = ("买套房子", "换辆新车", "出去旅游", "最新手机")
scene("想要的，一条条划", "第二步 · 写期望", (2650, Y1 + 30, 0.85))
L(rect(2650, Y1, 1200, 780, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("② 写下想要的", 2650, Y1 - 290, 74, BLUE, k0=1, k1=1.9, sfx="pop")
for n, w in enumerate(ITEMS):
    T(w, 2480, Y1 - 140 + n * 105, 56, k0=2 + n * 0.35, k1=2.3 + n * 0.35, sfx="pop" if n == 0 else None)
T("真需要吗？", 3000, Y1 - 140, 58, RED, k0=3.5, k1=4.0)
L(check(2780, Y1 - 145, 34), 4, 4.25, GREEN, 9, sfx="ding")
L(check(2780, Y1 + 65, 34), 4.3, 4.55, GREEN, 9)
L(P((2350, Y1 - 35), (2610, Y1 - 35)), 5, 5.3, RED, 10, sfx="rim")
L(P((2350, Y1 + 175), (2610, Y1 + 175)), 5.3, 5.6, RED, 10)
T("期望 ↓", 3020, Y1 + 100, 64, RED, k0=5.6, k1=6.0)

scene("跟去年的自己比", "第三步 · 换个比法", (950, Y2 + 30, 0.85))
L(rect(950, Y2, 1200, 780, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("③ 跟去年的自己比", 950, Y2 - 290, 70, BLUE, k0=1, k1=2.0, sfx="pop")
T("存款 +6000", 950, Y2 - 140, 58, GREEN, k0=2, k1=2.6, sfx="pop")
T("会做三个菜", 950, Y2 - 40, 58, GREEN, k0=2.6, k1=3.2)
L(stick(620, Y2 + 320, 0.55), 3, 3.4, BLACK, 9, sfx="wood_high")
T("去年", 620, Y2 + 60, 52, k0=3.4, k1=3.8)
L(stick(1280, Y2 + 320, 0.55, "up"), 4, 4.4, BLUE, 9, sfx="pop")
L(face(1280, Y2 + 320, 0.55, "smile"), 4.4, 4.5, BLUE, 8)
T("今年", 1280, Y2 + 60, 52, BLUE, k0=4.5, k1=4.9)
L(arrow((760, Y2 + 230), (1140, Y2 + 230), -0.1, 36), 5, 5.4, GREEN, 8, sfx="ding")

j_s = scene("把做成的事记下来", "第四步 · 记成就", (2650, Y2 + 30, 0.85))
L(rect(2650, Y2, 1200, 780, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("④ 记下做成的事", 2650, Y2 - 290, 70, BLUE, k0=1, k1=2.0, sfx="pop")
L(notebook(2470, Y2 + 100, 380, 420), 2, 2.6, BLACK, 8, sfx="wood_high")
for n, w in enumerate(("改完方案", "按时下班", "陪娃搭积木")):
    T(w, 2480, Y2 - 20 + n * 110, 50, k0=3 + n * 0.3, k1=3.3 + n * 0.3 + (0.15 if n == 2 else 0),
      sfx="pop" if n == 0 else None)
for n in range(3):
    L(check(2730, Y2 - 25 + n * 110, 28), 4 + n * 0.25, 4.2 + n * 0.25, GREEN, 8, sfx="ding" if n == 0 else None)
b.custom(J(), 5, 5.6, frac_fn(3030, Y2 + 80, [(j_s, 5.6, 1.6, 1.0, 0.5)], size=56, prefix=False, bar=False), sfx="pop")
T("自尊 ↑", 3030, Y2 + 310, 56, GREEN, k0=5.6, k1=6.0)

# ---------------------------------------------------------------- 收尾（场景 20–21）

scene("少比一点，就松一点", "一句话", (1800, 7300, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 13200, 0.8))
H(0, "cymbal", 0.5)
T("你最常跟谁比？", 1800, 13120, 80, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：混得不好，就怪自己不够努力？", 1800, 13280, 48, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")


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
