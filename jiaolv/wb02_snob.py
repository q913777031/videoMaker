"""02 势利（白板手绘版）：一换工作，亲戚的脸色怎么就变了？

叙事：打工人切身问题开局（那年进了大厂，过年亲戚围着夸 → 后来辞职了，今年饭桌上没人接话 → 同学会一见面先问
“在哪高就”）→ 书中观点（亮书《身份的焦虑》、德波顿；势利的人按地位给人打分，见面先问你做什么工作；好感跟着头衔走，
头衔一换脸色就换；势利也来自害怕：怕自己被看低，所以忙着给别人排位；画成一张图：怕被看低 → 看头衔 → 打分 → 给脸色）→
身边的例子（升了组长约饭变多、相亲先问房车工作、过年饭桌只夸挣得多的孩子、穿拖鞋进店没人理、拎着包进来马上热情）→
具体做法（认出来：他只看了一个标签 / 把力气留给不看标签的老朋友 / 自己别当势利眼：先问爱好再问工作 / 被问起就轻轻带过）
→ 评论区互动。
书中观点为转述（Alain de Botton, Status Anxiety, 2004，第一部分“焦虑起因”第二章“势利倾向”；中译本《身份的焦虑》，
陈广兴、南治国译，上海译文出版社）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, building, check, circle, cross,
                               face, join, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#B8562E"
SQUARE_SHOT = 9

b = Board(size=(3600, 11700))


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

def heart(x, y, r=100) -> skia.Path:
    """爱心：(x, y) 为中心，r 约为半宽。"""
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.4, y - r * 0.1, x - r * 0.6, y - r * 1.1, x, y - r * 0.4)
    p.cubicTo(x + r * 0.6, y - r * 1.1, x + r * 1.4, y - r * 0.1, x, y + r * 0.9)
    return p


def magnifier(x, y, r=45) -> skia.Path:
    """放大镜：(x, y) 为镜片中心，手柄朝左下。"""
    return join(circle(x, y, r), P((x - r * 0.7, y + r * 0.7), (x - r * 1.6, y + r * 1.6)))


def badge(x, y, w=150, h=66) -> skia.Path:
    """胸牌：方牌 + 挂绳。"""
    return join(rect(x, y, w, h, 10), P((x - w * 0.3, y - h / 2), (x, y - h / 2 - 50), (x + w * 0.3, y - h / 2)))


def ladder(x, top, bottom, w=400, rungs=5) -> skia.Path:
    parts = [P((x - w / 2, top), (x - w / 2, bottom)), P((x + w / 2, top), (x + w / 2, bottom))]
    for i in range(rungs):
        yy = top + (bottom - top) * (i + 0.5) / rungs
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
    return join(*parts)


def ring(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def table(x, y, w=760) -> skia.Path:
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 40, y), (x - w / 2 + 40, y + 110)),
                P((x + w / 2 - 40, y), (x + w / 2 - 40, y + 110)))


def bag(x, y, s=1.0) -> skia.Path:
    """手提包：(x, y) 为包身中心。"""
    h = skia.Path()
    h.addArc(skia.Rect.MakeXYWH(x - 30 * s, y - 75 * s, 60 * s, 60 * s), 180, 180)
    return join(rect(x, y, 110 * s, 80 * s, 10), h)


def stamp_fn(x, y, r, label, color=RED):
    """红色评分章：从大到小砸下来，落定后轻微回弹。"""

    def fn(c, k, t):
        s = 1 + 1.6 * (1 - ease_out(clamp01(k / 0.35)))
        a = clamp01(k / 0.15)
        c.save()
        c.translate(x, y)
        c.scale(s, s)
        c.rotate(-12)
        c.drawCircle(0, 0, r, K.paint(color, a, 12))
        c.drawCircle(0, 0, r * 0.82, K.paint(color, a * 0.6, 5))
        K.text(c, label, 0, 0, r * 0.75, "hand", color, a)
        c.restore()
        return None

    return fn


def drops_fn(pts, color=BLUE):
    """冒汗：几滴小水珠依次出现。"""

    def fn(c, k, t):
        for n, (x, y) in enumerate(pts):
            f = clamp01(k * len(pts) - n)
            if f > 0:
                K.dot(c, x, y + 20 * f, 11, color, f)
        return None

    return fn


# ---------------------------------------------------------------- 开局：亲戚的脸色（镜头 1–6）

b.shot("那年进了大厂", "灵魂拷问", view=(950, 900, 0.85))
L(building(650, 1300, 300, 420), 0, 0.8, sfx="wood_high")
T("大厂", 650, 820, 60, k0=0.8)
L(stick(1150, 1300, 0.8, "up", tie=True), 1, 1.6, BLUE, 9, sfx="wood_high")
L(face(1150, 1300, 0.8, "smile"), 1.6, 1.8, BLUE, 8)
T("入职啦！", 1150, 900, 64, RED, k0=2, sfx="pop")
H(3, "ding", 0.6)

REL = (2330, 2520, 2710)
b.shot("过年亲戚都夸你", "灵魂拷问", view=(2650, 900, 0.85))
T("那年春节", 2650, 440, 54, k0=0, sfx="pop")
L(table(2600, 1150, 860), 0.5, 0.9)
for n, x in enumerate(REL):
    L(stick(x, 1300, 0.6), 1 + n * 0.2, 1.4 + n * 0.2, BLACK, 9, sfx="wood_high" if n == 0 else None)
    L(face(x, 1300, 0.6, "smile"), 1.4 + n * 0.2, 1.5 + n * 0.2, BLACK, 8)
L(stick(2950, 1300, 0.6, tie=True), 1.6, 2.0, BLUE, 9)
L(face(2950, 1300, 0.6, "smile"), 2.0, 2.1, BLUE, 8)
L(bubble(2520, 680, 460, 130, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("有出息！", 2520, 680, 60, RED, k0=2.4)
H(3, "ding", 0.6)

b.shot("后来你辞职了", "灵魂拷问", view=(950, 1850, 0.85))
L(building(650, 2250, 300, 420), 0, 0.7, sfx="wood_high")
L(cross(650, 2040, 150), 1, 1.35, RED, 12, sfx="rim")
T("辞职", 650, 1700, 70, RED, k0=1.4)
L(stick(1150, 2250, 0.8, "hold"), 2, 2.6, BLUE, 9, sfx="wood_high")
L(face(1150, 2250, 0.8, "flat"), 2.6, 2.7, BLUE, 8)
L(rect(1245, 2090, 120, 90, 8), 2.7, 2.95, BLACK, 8)
H(3, "wood_low", 0.6)

b.shot("今年饭桌冷了", "灵魂拷问", view=(2650, 1850, 0.85))
T("今年春节", 2650, 1390, 54, k0=0, sfx="pop")
L(table(2600, 2100, 860), 0.5, 0.9)
for n, x in enumerate(REL):
    L(stick(x, 2250, 0.6), 1 + n * 0.15, 1.35 + n * 0.15, BLACK, 9, sfx="wood_high" if n == 0 else None)
    L(face(x, 2250, 0.6, "flat"), 1.35 + n * 0.15, 1.45 + n * 0.15, BLACK, 8)
L(stick(2950, 2250, 0.6), 1.6, 2.0, BLUE, 9)
L(face(2950, 2250, 0.6, "sad"), 2.0, 2.1, BLUE, 8)
L(bubble(2520, 1620, 300, 120, -1), 2, 2.3, BLACK, 8, sfx="pop")
T("哦。", 2520, 1620, 60, k0=2.3)
T("没人接话", 3000, 1760, 50, RED, k0=3, sfx="rim")

b.shot("同学会先问这个", "灵魂拷问", view=(1800, 2800, 0.85))
T("同学会", 1800, 2320, 54, k0=0, sfx="pop")
for n, x in enumerate((1420, 1620)):
    L(stick(x, 3200, 0.65), 1 + n * 0.25, 1.4 + n * 0.25, BLACK, 9, sfx="wood_high" if n == 0 else None)
    L(face(x, 3200, 0.65, "smile"), 1.4 + n * 0.25, 1.5 + n * 0.25, BLACK, 8)
L(stick(2150, 3200, 0.65), 1.5, 1.9, BLUE, 9)
L(face(2150, 3200, 0.65, "flat"), 1.9, 2.0, BLUE, 8)
L(bubble(1620, 2580, 460, 130, -1), 2, 2.3, BLACK, 8, sfx="pop")
T("在哪高就？", 1620, 2580, 60, k0=2.3)
H(3, "wood_low", 0.6)

b.shot("脸色怎么变了？", "灵魂拷问", view=(1800, 1800, 0.355), flashes=[0])
T("？", 2900, 2700, 520, RED, k0=0, k1=0.6, sfx="kick")
T("脸色怎么变了", 780, 2760, 120, k0=1.0, k1=2.0, sfx="pop")
H(2, "ding")
H(3, "rim", 0.6)

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "身份的焦虑", view=(1050, 3800, 0.9))
L(book(750, 3800, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 750, 3560, 76, GREEN, k0=1.0, sfx="pop")
T("阿兰 · 德波顿", 750, 4050, 50, k0=2.0, sfx="pop")
T("第二章 · 势利", 1310, 3800, 52, RED, k0=3.0, sfx="pop")

SNOB, YOU = (2250, 4200), (2950, 4200)
b.shot("书里说到势利眼", "书中观点 · 势利", view=(2650, 3800, 0.85))
L(stick(*SNOB, 0.8, "point", tie=True), 0, 0.6, BLACK, 10, sfx="wood_high")
L(face(*SNOB, 0.8, "flat"), 0.6, 0.75, BLACK, 8)
T("势利眼", 2250, 3460, 72, RED, k0=0.8)
L(magnifier(2420, 3975, 45), 1, 1.4, BLACK, 9, sfx="pop")
L(stick(*YOU, 0.8), 2, 2.6, BLUE, 10, sfx="wood_high")
H(3, "wood_low", 0.6)

b.shot("按地位给人打分", "书中观点 · 打分", view=(2650, 3800, 0.85), shake=[0], flashes=[0])
b.custom(J(), 0, 0.6, stamp_fn(2950, 3660, 120, "60分"), sfx="kick")
L(arrow((2480, 3940), (2860, 3990), 0.12, 36), 1, 1.4, RED, 8, sfx="wood_high")
L(badge(2990, 4050, 150, 66), 1.4, 1.8, BLACK, 8)
T("头衔", 2990, 4050, 46, RED, k0=2, sfx="pop")
H(3, "tom", 0.7)

b.shot("先问你做啥工作", "书中观点 · 先问工作", view=(2650, 3800, 0.85))
L(bubble(2450, 3650, 420, 130, -1), 0, 0.4, BLACK, 8, sfx="wood_high")
T("你做什么工作？", 2450, 3650, 46, k0=1, sfx="pop")
L(face(*YOU, 0.8, "flat"), 2, 2.2, BLUE, 8, sfx="pop")
H(3, "wood_low", 0.6)

b.shot("好感跟着头衔走", "书中观点 · 好感", view=(950, 4900, 0.85))
L(badge(650, 4650, 220, 90), 0, 0.4, BLACK, 9, sfx="wood_high")
T("经理", 650, 4650, 56, k0=0.4)
T("好感", 1250, 4430, 56, k0=0.5, k1=0.9)
L(arrow((790, 4650), (1060, 4650), 0.05, 34), 0.6, 0.9, GREEN, 8)
L(heart(1200, 4650, 110), 1, 1.5, RED, 11, sfx="pop")
L(badge(650, 5080, 220, 90), 2, 2.4, BLACK, 9, sfx="wood_high")
T("职员", 650, 5080, 56, k0=2.4)
L(arrow((790, 5080), (1100, 5080), 0.05, 34), 2.6, 2.9, GREEN, 8)
L(heart(1200, 5080, 45), 3, 3.3, RED, 8, sfx="pop")

b.shot("头衔一换就变脸", "书中观点 · 变脸", view=(950, 4900, 0.85))
L(cross(650, 4650, 70), 0, 0.3, RED, 11, sfx="rim")
T("待业", 650, 4790, 52, RED, k0=1, sfx="pop")
L(scribble(1200, 4630, 240, 200, 8), 2, 2.4, RED, 7, sfx="shaker")
L(heart(1440, 4680, 40), 3, 3.3, RED, 8, sfx="pop")

LAD = (2650, 4450, 5400)
b.shot("势利也来自害怕", "书中观点 · 害怕", view=(2650, 4900, 0.85))
L(ladder(LAD[0], LAD[1], LAD[2], 400, 5), 0, 0.8, BLACK, 9, sfx="wood_high")
L(stick(2650, 4925, 0.5, tie=True), 1, 1.4, BLACK, 9, sfx="pop")
L(face(2650, 4925, 0.5, "sad"), 1.4, 1.5, BLACK, 7)
T("怕", 3110, 4800, 160, RED, k0=2, k1=2.4, sfx="tom")
b.custom(J(), 3, 3.6, drops_fn([(2710, 4740), (2725, 4790)]), sfx="pop")

b.shot("怕自己被看低", "书中观点 · 被看低", view=(2650, 4900, 0.85))
L(stick(2650, 4545, 0.45), 0, 0.4, BLACK, 9, sfx="wood_high")
L(face(2650, 4545, 0.45, "flat"), 0.4, 0.5, BLACK, 7)
L(arrow((2560, 4470), (2580, 4760), 0.35, 30), 1, 1.4, RED, 8, sfx="wood_high")
T("被看低", 2240, 4620, 56, RED, k0=2, sfx="pop")
H(3, "rim", 0.6)

b.shot("就忙着给人排位", "书中观点 · 排位", view=(2650, 4900, 0.85))
for n, x in enumerate((2560, 2740)):
    L(stick(x, 5305, 0.42), n * 0.3, n * 0.3 + 0.4, BLACK, 8, sfx="wood_high" if n == 0 else None)
T("他比我高", 3120, 4500, 52, k0=1, sfx="pop")
L(arrow((2880, 4860), (2880, 5240), -0.25, 32), 1.5, 1.9, BLUE, 8)
T("我比他强", 3120, 5200, 52, BLUE, k0=2, sfx="pop")
H(3, "tom", 0.6)

CHAIN = [("怕被看低", 1000), ("看头衔", 1645), ("打分", 2180), ("给脸色", 2715)]
CY = 5600
b.shot("画成一张图", "书中观点 · 一张图", view=(1880, 4450, 0.38))
for n, (w, x) in enumerate(CHAIN[1:]):
    T(w, x, CY, 110, RED if n == 2 else BLACK, k0=n, k1=n + 0.5, sfx="pop")
    if n < 2:
        L(arrow((x + len(w) * 55 + 25, CY), (CHAIN[n + 2][1] - len(CHAIN[n + 2][0]) * 55 - 25, CY), 0, 34),
          n + 0.55, n + 0.9, GREEN, 8)
L(underline(2550, 2880, CY + 80), 3, 3.4, RED, 8, sfx="ding")

b.shot("越怕的人越爱打分", "书中观点 · 一张图", view=(1880, 4450, 0.38), shake=[0])
T(CHAIN[0][0], CHAIN[0][1], CY, 110, RED, k0=0, k1=0.6, sfx="kick")
L(arrow((1245, CY), (1455, CY), 0, 34), 1, 1.3, GREEN, 8, sfx="wood_high")
L(ring(3110, 4800, 230, 230), 2, 2.4, RED, 8, sfx="wood_high")
L(underline(790, 1210, CY + 80), 2.5, 2.9, RED, 8)
H(3, "ding", 0.6)

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 6650), (2650, 6650), (950, 7550), (2650, 7550)]
b.shot("身边也常碰到", "身边的例子", view=(1800, 7100, 0.355))
T("身边的例子", 1800, 6050, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("你升了组长", "例子 · 职场", view=(950, 6650, 0.85))
L(stick(560, 7000, 0.75, "up", tie=True), 0, 0.6, BLUE, 9, sfx="wood_high")
L(face(560, 7000, 0.75, "smile"), 0.6, 0.7, BLUE, 8)
T("组长", 560, 6660, 60, RED, k0=0.7, k1=1.0)
for n, x in enumerate((1250, 1420)):
    L(stick(x, 7000, 0.6), 1 + n * 0.25, 1.4 + n * 0.25, BLACK, 9, sfx="wood_high" if n == 0 else None)
    L(face(x, 7000, 0.6, "smile"), 1.4 + n * 0.25, 1.5 + n * 0.25, BLACK, 8)
L(bubble(1300, 6430, 380, 120, 1), 2, 2.3, BLACK, 8, sfx="pop")
T("组长好！", 1300, 6430, 56, k0=2.3)
H(3, "ding", 0.6)

b.shot("约饭一下变多", "例子 · 职场", view=(950, 6650, 0.85))
for n, w in enumerate(("周一 约饭", "周三 喝茶", "周五 唱歌")):
    T(w, 930, 6680 + n * 110, 50, k0=n, sfx="pop")
L(underline(800, 1060, 6950, 10, 30), 3, 3.4, RED, 7, sfx="ding")

b.shot("相亲先问收入", "例子 · 相亲", view=(2650, 6650, 0.85))
T("相亲", 2420, 6330, 54, k0=0, sfx="pop")
L(table(2650, 6900, 620), 1, 1.4, BLACK, 9, sfx="wood_high")
L(stick(2280, 7020, 0.6), 1.2, 1.4, BLUE, 9)
L(face(2280, 7020, 0.6, "smile"), 1.4, 1.5, BLUE, 8)
L(stick(3020, 7020, 0.6, hair=True), 1.5, 1.9, BLACK, 9)
L(bubble(2860, 6490, 400, 120, 1), 2, 2.3, BLACK, 8, sfx="pop")
T("月薪多少？", 2860, 6490, 56, k0=2.3)
H(3, "wood_low", 0.6)

b.shot("问的全是条件", "例子 · 相亲", view=(2650, 6650, 0.85))
for n, w in enumerate(("房？", "车？", "工作？")):
    T(w, 2650, 6640 + n * 85, 52, RED, k0=n, sfx="pop")
L(face(2280, 7020, 0.6, "flat"), 3, 3.2, BLUE, 8, sfx="rim")

KID1, KID2 = (1310, 7900), (590, 7900)
b.shot("过年比谁家孩子", "例子 · 家庭", view=(950, 7550, 0.85))
L(stick(950, 7900, 0.6, "point"), 0, 0.5, BLACK, 9, sfx="wood_high")
L(face(950, 7900, 0.6, "smile"), 0.5, 0.6, BLACK, 8)
L(stick(*KID1, 0.5), 1, 1.3, BLACK, 8, sfx="pop")
T("月入2万", KID1[0], 7620, 50, RED, k0=1.3)
L(stick(*KID2, 0.5), 2, 2.3, BLUE, 8, sfx="pop")
T("月入5千", KID2[0], 7620, 50, BLUE, k0=2.3)

b.shot("只夸挣得多的", "例子 · 家庭", view=(950, 7550, 0.85))
L(bubble(950, 7360, 440, 120, 1), 0, 0.3, BLACK, 8, sfx="wood_high")
T("多跟他学学！", 950, 7360, 50, k0=0.3)
L(face(*KID1, 0.5, "smile"), 1, 1.2, BLACK, 7, sfx="pop")
L(face(*KID2, 0.5, "sad"), 2, 2.2, BLUE, 7, sfx="rim")
T("……", KID2[0] + 110, 7740, 50, BLUE, k0=3, sfx="pop")

CLERK = (3060, 7900)
b.shot("穿拖鞋进店", "例子 · 逛店", view=(2650, 7550, 0.85))
L(join(P((2860, 7780), (3220, 7780)), P((2860, 7780), (2860, 7900)), P((3220, 7780), (3220, 7900))), 0, 0.5,
  BLACK, 9, sfx="wood_high")
L(stick(*CLERK, 0.55), 1, 1.4, BLACK, 8, sfx="pop")
L(stick(2330, 7900, 0.6), 2, 2.4, BLUE, 9, sfx="wood_high")
L(join(ring(2290, 7905, 60, 22), ring(2370, 7905, 60, 22)), 2.4, 2.6, BLUE, 6)
T("拖鞋", 2330, 7480, 54, k0=3, sfx="pop")

b.shot("拎个包就热情了", "例子 · 逛店", view=(2650, 7550, 0.85))
L(face(*CLERK, 0.55, "flat"), 0, 0.2, BLACK, 7, sfx="rim")
L(stick(2620, 7900, 0.6, "hold"), 1, 1.4, BLACK, 9, sfx="wood_high")
L(bag(2700, 7790, 0.8), 1.4, 1.7, RED, 8)
L(face(*CLERK, 0.55, "smile"), 2, 2.2, RED, 7, sfx="pop")
L(bubble(2980, 7360, 380, 120, 1), 2.1, 2.4, BLACK, 8)
T("里边请！", 2980, 7360, 56, RED, k0=2.4)
H(3, "ding", 0.6)

b.shot("四件事一个样", "身边的例子", view=(1800, 7100, 0.355))
for n, (x, y, w, h) in enumerate(((560, 6660, 200, 110), (2650, 6725, 200, 260), (1310, 7620, 270, 90),
                                  (2700, 7790, 140, 120))):
    L(ring(x, y, w, h), n, n + 0.35, RED, 9, sfx="pop" if n % 2 == 0 else "ding")

b.shot("只认标签不看人", "身边的例子", view=(1800, 7100, 0.355), shake=[0])
T("只认标签，不看人", 1800, 8180, 120, RED, k0=0, k1=0.8, sfx="kick")
L(underline(1300, 2300, 8270), 2, 2.5, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 9250), (2650, 9250), (950, 10150), (2650, 10150)]
b.shot("被看低了这样办", "具体做法", view=(1800, 9650, 0.355))
T("被看低了，这样做", 1800, 8640, 120, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先认出他在打分", "第一步 · 认出来", view=(950, 9250, 0.85))
T("① 认出来", 950, 8950, 76, BLUE, k0=0, sfx="pop")
L(stick(600, 9580, 0.65, "point"), 1, 1.5, BLACK, 9, sfx="wood_high")
L(stick(1300, 9580, 0.65), 2, 2.4, BLUE, 9, sfx="pop")
L(badge(1330, 9465, 130, 60), 2.4, 2.7, BLACK, 7)
T("头衔", 1330, 9465, 46, RED, k0=2.7, k1=3.0)
H(3, "wood_low", 0.6)

b.shot("他只看见标签", "第一步 · 认出来", view=(950, 9250, 0.85))
L(magnifier(720, 9420, 38), 0, 0.4, BLACK, 8, sfx="wood_high")
L(ring(1330, 9465, 190, 110), 1, 1.35, RED, 8, sfx="rim")
T("只看了这一样", 950, 9110, 52, k0=2, sfx="pop")

b.shot("冷脸冲着头衔去", "第一步 · 认出来", view=(950, 9250, 0.85))
L(face(600, 9580, 0.65, "flat"), 0, 0.2, BLACK, 8, sfx="pop")
T("冲头衔，不冲你", 950, 9210, 52, GREEN, k0=1, sfx="pop")
L(face(1300, 9580, 0.65, "smile"), 2, 2.2, BLUE, 8, sfx="ding")
L(check(1250, 9210, 30), 3, 3.3, GREEN, 9, sfx="pop")

FRIEND = (2950, 9580)
b.shot("力气留给老朋友", "第二步 · 老朋友", view=(2650, 9250, 0.85))
T("② 留给老朋友", 2650, 8950, 72, BLUE, k0=0, sfx="pop")
L(stick(2350, 9580, 0.65), 1, 1.4, BLUE, 9, sfx="wood_high")
L(stick(*FRIEND, 0.65, hair=True), 2, 2.4, BLACK, 9, sfx="pop")
L(face(*FRIEND, 0.65, "smile"), 2.4, 2.5, BLACK, 8)

b.shot("辞职那年谁还在", "第二步 · 老朋友", view=(2650, 9250, 0.85))
L(bubble(2880, 9150, 420, 120, 1), 0, 0.3, BLACK, 8, sfx="wood_high")
T("出来吃碗面？", 2880, 9150, 50, k0=0.3)
T("辞职那年", 2400, 9150, 52, RED, k0=1, sfx="pop")
L(face(2350, 9580, 0.65, "smile"), 2, 2.2, BLUE, 8, sfx="ding")

b.shot("多约这样的人", "第二步 · 老朋友", view=(2650, 9250, 0.85))
T("周六 吃面", 2650, 9380, 46, k0=0, sfx="pop")
T("周日 爬山", 2650, 9480, 46, k0=1, sfx="pop")
L(check(2650, 9580, 36), 2, 2.3, GREEN, 9, sfx="ding")
H(3, "wood_high", 0.6)

PAL = (1300, 10480)
b.shot("自己别当势利眼", "第三步 · 别打分", view=(950, 10150, 0.85))
T("③ 自己别打分", 950, 9850, 76, BLUE, k0=0, sfx="pop")
L(stick(600, 10480, 0.65), 1, 1.4, BLUE, 9, sfx="wood_high")
L(face(600, 10480, 0.65, "smile"), 1.4, 1.5, BLUE, 8)
L(stick(*PAL, 0.65), 2, 2.4, BLACK, 9, sfx="pop")
T("新朋友", 1470, 10420, 46, k0=3, sfx="pop")

b.shot("见面先别问工作", "第三步 · 别打分", view=(950, 10150, 0.85))
L(bubble(860, 10050, 440, 120, -1), 0, 0.3, BLACK, 8, sfx="wood_high")
T("你做什么工作？", 860, 10050, 46, k0=0.3)
L(cross(860, 10050, 60), 1, 1.3, RED, 10, sfx="rim")
H(2, "wood_low", 0.6)

b.shot("问他爱干点啥", "第三步 · 别打分", view=(950, 10150, 0.85))
b.erase(J(), 0, 0.5, 860, 10075, 460, 210)
H(0, "shaker")
L(bubble(860, 10050, 440, 120, -1), 0.6, 0.95, BLUE, 8)
T("平时爱干点啥？", 860, 10050, 46, BLUE, k0=1, sfx="pop")
T("钓鱼！", PAL[0], 10210, 52, RED, k0=2, sfx="pop")
L(face(*PAL, 0.65, "smile"), 3, 3.2, BLACK, 8, sfx="ding")

AUNT = (2950, 10480)
b.shot("被问就轻轻带过", "第四步 · 带过", view=(2650, 10150, 0.85))
T("④ 轻轻带过", 2650, 9850, 76, BLUE, k0=0, sfx="pop")
L(stick(2350, 10480, 0.65), 1, 1.4, BLUE, 9, sfx="wood_high")
L(stick(*AUNT, 0.65, hair=True), 1.4, 1.8, BLACK, 9)
L(bubble(2900, 10050, 400, 120, 1), 2, 2.3, BLACK, 8, sfx="pop")
T("在哪高就？", 2900, 10050, 50, k0=2.3)

b.shot("笑笑聊点别的", "第四步 · 带过", view=(2650, 10150, 0.85))
L(bubble(2450, 10170, 420, 110, -1), 0, 0.3, BLUE, 8, sfx="wood_high")
T("歇一阵，您呢？", 2450, 10170, 46, BLUE, k0=0.3)
L(face(2350, 10480, 0.65, "smile"), 1, 1.2, BLUE, 8, sfx="pop")
L(face(*AUNT, 0.65, "smile"), 2, 2.2, BLACK, 8, sfx="ding")

b.shot("看人，别看标签", "一句话", view=(1800, 5600, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 11000, 0.8))
T("谁的脸色变得最快？", 1800, 10920, 80, RED, k0=0.5, k1=1.8)
T("下一讲：工资比爸妈高，为什么还觉得穷？", 1800, 11080, 50, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "snob", "势利", "一换工作，亲戚的脸色怎么就变了？", ACC, b.shots,
                 [f"{BOOK}第一部分“焦虑起因”第二章“势利倾向”（转述）",
                  "中译本：阿兰·德波顿《身份的焦虑》，陈广兴、南治国译，上海译文出版社"],
                 "一换工作|亲戚就【换了脸色】", 8,
                 ["书中观点均为转述：势利的人按社会地位给人打分，一见面先问“你做什么工作”；他们的好感跟着你的头衔走，"
                  "地位一变，态度就跟着变；势利本身也来自害怕——怕自己被看低，所以忙着给别人排位。“怕被看低 → 看头衔 → 打分 → "
                  "给脸色”一图为据书中思路的通俗化整理。出处：Alain de Botton, Status Anxiety (Hamish Hamilton / Pantheon, 2004)，"
                  "第一部分“焦虑起因”第二章“势利倾向”；中译本《身份的焦虑》（阿兰·德波顿著，陈广兴、南治国译，上海译文出版社）。"
                  "上屏均为转述，不是逐字引文。",
                  "进大厂与辞职后的春节饭桌、同学会、升组长后约饭变多、相亲问收入、过年比孩子、穿拖鞋进店均为现实场景示意，"
                  "不指向任何具体公司或个人；“60分”“月入2万/5千”等数字为示意，不是数据；不评价任何职业和收入水平。",
                  "四步做法（认出他只看了一个标签、把力气留给不看标签的老朋友、自己别当势利眼先问爱好、被问起就轻轻带过）"
                  "为据书中思路整理的建议。"],
                 tags="#人情世故 #过年")
    return b.attach(ep)
