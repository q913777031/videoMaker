"""02 势利（白板手绘版）：一换工作，亲戚的脸色怎么就变了？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
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
SQUARE_SHOT = 4

b = Board(size=(3600, 14300))


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


# ---------------------------------------------------------------- 开局：亲戚的脸色（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("进了大厂，亲戚都夸", "灵魂拷问", (950, 1150, 0.7))
L(building(450, 1000, 280, 380), 0, 0.8, sfx="wood_high")
T("大厂", 450, 540, 60, k0=0.8, k1=1.2)
L(stick(850, 1000, 0.75, "up", tie=True), 1, 1.6, BLUE, 9, sfx="wood_high")
L(face(850, 1000, 0.75, "smile"), 1.6, 1.8, BLUE, 8)
T("入职啦！", 1000, 560, 60, RED, k0=2, sfx="pop")
T("那年春节", 450, 1620, 54, k0=3, sfx="pop")
L(table(1150, 1600, 760), 3.3, 3.7)
for n, x in enumerate((900, 1150, 1400)):
    L(stick(x, 1750, 0.6), 3.7 + n * 0.3, 4.0 + n * 0.3, BLACK, 9, sfx="wood_high" if n == 0 else None)
    L(face(x, 1750, 0.6, "smile"), 4.0 + n * 0.3, 4.1 + n * 0.3, BLACK, 8)
L(bubble(1150, 1340, 440, 130, -1), 5, 5.3, BLACK, 8, sfx="pop")
T("有出息！", 1150, 1340, 60, RED, k0=5.3, k1=5.95)

scene("辞职了，饭桌就冷了", "灵魂拷问", (2650, 1150, 0.7))
L(building(2350, 1000, 280, 380), 0, 0.7, sfx="wood_high")
L(cross(2350, 800, 150), 1, 1.35, RED, 12, sfx="rim")
T("辞职", 2350, 540, 70, RED, k0=1.4, k1=1.9)
L(stick(2750, 1000, 0.75, "hold"), 2, 2.6, BLUE, 9, sfx="wood_high")
L(face(2750, 1000, 0.75, "flat"), 2.6, 2.7, BLUE, 8)
L(rect(2840, 850, 115, 85, 8), 2.7, 2.95, BLACK, 8)
T("今年春节", 2350, 1620, 54, k0=3, sfx="pop")
L(table(2850, 1600, 760), 3.3, 3.7)
for n, x in enumerate((2600, 2850, 3100)):
    L(stick(x, 1750, 0.6), 3.7 + n * 0.25, 4.0 + n * 0.25, BLACK, 9, sfx="wood_high" if n == 0 else None)
    L(face(x, 1750, 0.6, "flat"), 4.0 + n * 0.25, 4.1 + n * 0.25, BLACK, 8)
L(bubble(2850, 1340, 300, 120, -1), 4.6, 4.9, BLACK, 8)
T("哦。", 2850, 1340, 60, k0=5, k1=5.5, sfx="pop")
T("没人接话", 2350, 1340, 54, RED, k0=5.2, k1=5.9)

scene("脸色怎么就变了？", "灵魂拷问", (1800, 2650, 0.7), flashes=[4])
T("同学会", 1300, 2100, 60, k0=0, sfx="pop")
for n, x in enumerate((1250, 1450)):
    L(stick(x, 2950, 0.65), 1 + n * 0.3, 1.4 + n * 0.3, BLACK, 9, sfx="wood_high" if n == 0 else None)
    L(face(x, 2950, 0.65, "smile"), 1.4 + n * 0.3, 1.5 + n * 0.3, BLACK, 8)
L(stick(1900, 2950, 0.65), 1.8, 2.2, BLUE, 9)
L(face(1900, 2950, 0.65, "flat"), 2.2, 2.3, BLUE, 8)
L(bubble(1450, 2400, 460, 130, -1), 3, 3.3, BLACK, 8, sfx="pop")
T("在哪高就？", 1450, 2400, 60, k0=3.3, k1=3.9)
T("？", 2330, 2650, 380, RED, k0=4, k1=4.5, sfx="kick")
T("脸色怎么变了", 1950, 2100, 90, k0=5, k1=5.95, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

SNOB, YOU = (550, 4700), (1300, 4700)
scene("有本书专讲势利眼", "身份的焦虑", (950, 4050, 0.62))
L(book(800, 3650, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 800, 3420, 76, GREEN, k0=1, sfx="pop")
T("阿兰 · 德波顿", 800, 3900, 50, k0=2, k1=2.8)
T("第二章 · 势利", 1400, 3650, 56, RED, k0=3, sfx="pop")
L(stick(*SNOB, 0.8, "point", tie=True), 4, 4.6, BLACK, 10, sfx="wood_high")
L(face(*SNOB, 0.8, "flat"), 4.6, 4.75, BLACK, 8)
T("势利眼", 290, 4520, 56, RED, k0=4.8, k1=5.3)
L(magnifier(720, 4475, 45), 5, 5.4, BLACK, 9, sfx="pop")

scene("按头衔给人打分", "书中观点 · 打分", (950, 4050, 0.62), shake=[0], flashes=[0])
L(stick(*YOU, 0.8), 0, 0.5, BLUE, 10)
b.custom(J(), 0, 0.6, stamp_fn(1490, 4250, 110, "60分"), sfx="kick")
L(badge(1340, 4560, 150, 66), 1, 1.4, BLACK, 8, sfx="wood_high")
T("头衔", 1340, 4560, 46, RED, k0=1.4, k1=1.9)
L(arrow((790, 4520), (1220, 4560), 0.12, 36), 2, 2.4, RED, 8, sfx="wood_high")
L(face(*YOU, 0.8, "flat"), 3, 3.2, BLUE, 8, sfx="pop")
L(bubble(700, 4180, 440, 130, -1), 4, 4.4, BLACK, 8, sfx="wood_high")
T("你做什么工作？", 700, 4180, 46, k0=4.4, k1=5.4)
H(5, "tom", 0.7)

scene("好感跟着头衔走", "书中观点 · 好感", (2650, 4050, 0.7))
L(badge(2300, 3720, 220, 90), 0, 0.4, BLACK, 9, sfx="wood_high")
T("经理", 2300, 3720, 56, k0=0.4, k1=0.9)
L(arrow((2440, 3720), (2760, 3720), 0.05, 34), 1, 1.3, GREEN, 8, sfx="wood_high")
L(heart(2960, 3720, 130), 1.4, 1.9, RED, 11)
T("好感", 2960, 3480, 56, k0=2, sfx="pop")
L(cross(2300, 3720, 70), 3, 3.3, RED, 11, sfx="rim")
T("待业", 2300, 3900, 56, RED, k0=4, sfx="pop")
L(scribble(2960, 3710, 300, 240, 8), 5, 5.4, RED, 7, sfx="shaker")
L(heart(3220, 3920, 45), 5.4, 5.8, RED, 8)

LAD = (2350, 5400, 6300)
scene("势利也来自害怕", "书中观点 · 害怕", (2350, 5850, 0.7))
L(ladder(LAD[0], LAD[1], LAD[2], 400, 5), 0, 0.8, BLACK, 9, sfx="wood_high")
L(stick(2350, 5850, 0.5, tie=True), 1, 1.4, BLACK, 9, sfx="pop")
L(face(2350, 5850, 0.5, "sad"), 1.4, 1.5, BLACK, 7)
T("怕", 2810, 5720, 160, RED, k0=2, k1=2.4, sfx="tom")
b.custom(J(), 3, 3.6, drops_fn([(2410, 5665), (2425, 5715)]), sfx="pop")
L(stick(2350, 5490, 0.45), 4, 4.4, BLACK, 9, sfx="wood_high")
L(face(2350, 5490, 0.45, "flat"), 4.4, 4.5, BLACK, 7)
L(arrow((2260, 5415), (2280, 5705), 0.35, 30), 4.6, 4.9, RED, 8)
T("被看低", 1940, 5565, 56, RED, k0=5, sfx="pop")

scene("就忙着给人排位", "书中观点 · 排位", (2350, 5850, 0.7))
for n, x in enumerate((2260, 2440)):
    L(stick(x, 6210, 0.42), n * 0.3, n * 0.3 + 0.4, BLACK, 8, sfx="wood_high" if n == 0 else None)
L(arrow((2580, 5740), (2580, 5500), 0.25, 32), 1, 1.3, RED, 8, sfx="wood_high")
T("他比我高", 2850, 5450, 52, k0=1.4, k1=2.1)
L(arrow((2580, 5900), (2580, 6140), -0.25, 32), 3, 3.3, BLUE, 8, sfx="wood_high")
T("我比他强", 2850, 6160, 52, BLUE, k0=3.4, k1=4.1)
H(5, "tom", 0.6)

CHAIN = [("怕被看低", 1030), ("看头衔", 1675), ("打分", 2210), ("给脸色", 2745)]
CY = 6900
scene("越怕越爱给人打分", "书中观点 · 一张图", (1870, 6280, 0.47), shake=[3])
for n, (w, x) in enumerate(CHAIN[1:]):
    T(w, x, CY, 110, RED if n == 2 else BLACK, k0=n, k1=n + 0.5, sfx="pop")
    if n < 2:
        L(arrow((x + len(w) * 55 + 25, CY), (CHAIN[n + 2][1] - len(CHAIN[n + 2][0]) * 55 - 25, CY), 0, 34),
          n + 0.55, n + 0.9, GREEN, 8)
T(CHAIN[0][0], CHAIN[0][1], CY, 110, RED, k0=3, k1=3.6, sfx="kick")
L(arrow((1275, CY), (1485, CY), 0, 34), 3.6, 3.9, GREEN, 8)
L(ring(2810, 5720, 260, 260), 4, 4.4, RED, 8, sfx="wood_high")
L(underline(820, 1240, CY + 80), 5, 5.4, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 9050), (2650, 9050), (950, 9950), (2650, 9950)]
scene("身边也常碰到", "身边的例子", (1800, 9250, 0.355))
T("身边的例子", 1800, 8040, 130, k0=0, k1=1.2, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 2 + n * 0.8, 2.5 + n * 0.8, GREEN, 8, sfx="wood_high" if n in (0, 2) else None)

scene("升了组长，约饭变多", "例子 · 职场", (950, 9050, 0.85))
L(stick(560, 9400, 0.75, "up", tie=True), 0, 0.6, BLUE, 9, sfx="wood_high")
L(face(560, 9400, 0.75, "smile"), 0.6, 0.7, BLUE, 8)
T("组长", 560, 9060, 60, RED, k0=0.7, k1=1.0)
for n, x in enumerate((1250, 1420)):
    L(stick(x, 9400, 0.6), 1 + n * 0.25, 1.4 + n * 0.25, BLACK, 9, sfx="wood_high" if n == 0 else None)
    L(face(x, 9400, 0.6, "smile"), 1.4 + n * 0.25, 1.5 + n * 0.25, BLACK, 8)
L(bubble(1300, 8830, 380, 120, 1), 2, 2.3, BLACK, 8, sfx="pop")
T("组长好！", 1300, 8830, 56, k0=2.3, k1=2.9)
for n, w in enumerate(("周一 约饭", "周五 唱歌")):
    T(w, 930, 9080 + n * 110, 50, k0=3 + n, k1=3.8 + n, sfx="pop")
L(underline(800, 1060, 9240, 10, 30), 5, 5.4, RED, 7, sfx="ding")

scene("相亲先问月薪", "例子 · 相亲", (2650, 9050, 0.85))
T("相亲", 2420, 8730, 54, k0=0, sfx="pop")
L(table(2650, 9300, 620), 1, 1.4, BLACK, 9, sfx="wood_high")
L(stick(2280, 9420, 0.6), 1.4, 1.7, BLUE, 9)
L(stick(3020, 9420, 0.6, hair=True), 1.7, 2.0, BLACK, 9)
L(face(3020, 9420, 0.6, "flat"), 2.0, 2.1, BLACK, 8)
L(bubble(2860, 8890, 400, 120, 1), 2.2, 2.5, BLACK, 8)
T("月薪多少？", 2860, 8890, 56, k0=3, k1=3.8, sfx="pop")
for n, w in enumerate(("房？", "车？", "工作？")):
    T(w, 2650, 9060 + n * 85, 52, RED, k0=4 + n * 0.4, k1=4.35 + n * 0.4, sfx="pop" if n == 0 else None)
L(face(2280, 9420, 0.6, "flat"), 5, 5.2, BLUE, 8, sfx="rim")

KID1, KID2 = (1310, 10300), (590, 10300)
scene("过年只夸挣得多的", "例子 · 家庭", (950, 9950, 0.85))
L(stick(950, 10300, 0.6, "point"), 0, 0.5, BLACK, 9, sfx="wood_high")
L(face(950, 10300, 0.6, "smile"), 0.5, 0.6, BLACK, 8)
L(stick(*KID1, 0.5), 1, 1.3, BLACK, 8, sfx="pop")
T("月入2万", KID1[0], 10020, 50, RED, k0=1.3, k1=1.9)
L(stick(*KID2, 0.5), 2, 2.3, BLUE, 8, sfx="pop")
T("月入5千", KID2[0], 10020, 50, BLUE, k0=2.3, k1=2.9)
L(bubble(950, 9760, 440, 120, 1), 3, 3.3, BLACK, 8, sfx="wood_high")
T("多跟他学学！", 950, 9760, 50, k0=3.3, k1=3.9)
L(face(*KID1, 0.5, "smile"), 4, 4.2, BLACK, 7, sfx="pop")
L(face(*KID2, 0.5, "sad"), 5, 5.2, BLUE, 7, sfx="rim")

CLERK, BAG = (3060, 10300), (2700, 10190)
scene("拎了包才热情", "例子 · 逛店", (2650, 9950, 0.85))
L(join(P((2860, 10180), (3220, 10180)), P((2860, 10180), (2860, 10300)), P((3220, 10180), (3220, 10300))), 0, 0.5,
  BLACK, 9, sfx="wood_high")
L(stick(2250, 10300, 0.6), 1, 1.4, BLUE, 9, sfx="wood_high")
L(join(ring(2210, 10305, 60, 22), ring(2290, 10305, 60, 22)), 1.4, 1.6, BLUE, 6)
T("拖鞋", 2250, 9880, 54, k0=1.6, k1=2.0)
L(stick(*CLERK, 0.55), 2, 2.4, BLACK, 8, sfx="pop")
L(face(*CLERK, 0.55, "flat"), 2.4, 2.55, BLACK, 7)
L(stick(2620, 10300, 0.6, "hold"), 3, 3.4, BLACK, 9, sfx="wood_high")
L(bag(*BAG, 0.8), 3.4, 3.7, RED, 8)
L(bubble(2980, 9760, 380, 120, 1), 4, 4.3, BLACK, 8, sfx="pop")
T("里边请！", 2980, 9760, 56, RED, k0=4.3, k1=4.9)
H(5, "ding", 0.6)

scene("只认标签不看人", "身边的例子", (1800, 9250, 0.355), shake=[4])
for n, (x, y, w, h) in enumerate(((560, 9060, 200, 110), (2650, 9145, 200, 260), (1310, 10020, 270, 90),
                                  (BAG[0], BAG[1], 140, 120))):
    L(ring(x, y, w, h), n * 0.8, n * 0.8 + 0.35, RED, 9, sfx="pop" if n % 2 == 0 else None)
T("只认标签，不看人", 1800, 10580, 120, RED, k0=4, k1=4.8, sfx="kick")
L(underline(1300, 2300, 10670), 5, 5.5, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 11650), (2650, 11650), (950, 12550), (2650, 12550)]
scene("他只看了你的头衔", "第一步 · 认出来", (950, 11650, 0.85))
L(rect(950, 11650, 1200, 820, 40), 0, 0.6, GREEN, 8)
T("① 认出来", 950, 11350, 76, BLUE, k0=0, sfx="pop")
L(stick(600, 11980, 0.65, "point"), 1, 1.5, BLACK, 9, sfx="wood_high")
L(face(600, 11980, 0.65, "flat"), 1.5, 1.6, BLACK, 8)
L(magnifier(720, 11820, 38), 1.6, 1.9, BLACK, 8)
L(stick(1300, 11980, 0.65), 2, 2.4, BLUE, 9, sfx="pop")
L(badge(1330, 11890, 130, 60), 2.4, 2.7, BLACK, 7)
T("头衔", 1330, 11890, 46, RED, k0=2.7, k1=3.0)
L(ring(1330, 11900, 190, 90), 3, 3.35, RED, 8, sfx="rim")
T("冲头衔，不冲你", 950, 11610, 52, GREEN, k0=4, k1=4.9, sfx="pop")
L(face(1300, 11980, 0.65, "smile"), 5, 5.2, BLUE, 8, sfx="ding")

FRIEND = (2950, 11980)
scene("力气留给老朋友", "第二步 · 老朋友", (2650, 11650, 0.85))
L(rect(2650, 11650, 1200, 820, 40), 0, 0.6, GREEN, 8)
T("② 留给老朋友", 2650, 11350, 72, BLUE, k0=0, sfx="pop")
L(stick(2350, 11980, 0.65), 1, 1.4, BLUE, 9, sfx="wood_high")
L(stick(*FRIEND, 0.65, hair=True), 2, 2.4, BLACK, 9, sfx="pop")
L(face(*FRIEND, 0.65, "smile"), 2.4, 2.5, BLACK, 8)
L(bubble(2880, 11550, 420, 120, 1), 3, 3.3, BLACK, 8, sfx="wood_high")
T("出来吃碗面？", 2880, 11550, 50, k0=3.3, k1=3.9)
T("辞职那年", 2400, 11550, 52, RED, k0=4, sfx="pop")
L(face(2350, 11980, 0.65, "smile"), 5, 5.2, BLUE, 8, sfx="ding")

PAL = (1300, 12880)
scene("见面先问爱好", "第三步 · 别打分", (950, 12550, 0.85))
L(rect(950, 12550, 1200, 820, 40), 0, 0.6, GREEN, 8)
T("③ 自己别打分", 950, 12250, 76, BLUE, k0=0, sfx="pop")
L(stick(600, 12880, 0.65), 1, 1.4, BLUE, 9, sfx="wood_high")
L(face(600, 12880, 0.65, "smile"), 1.4, 1.5, BLUE, 8)
L(stick(*PAL, 0.65), 2, 2.4, BLACK, 9, sfx="pop")
L(bubble(860, 12450, 440, 120, -1), 3, 3.3, BLUE, 8, sfx="wood_high")
T("平时爱干点啥？", 860, 12450, 46, BLUE, k0=3.3, k1=4.0)
T("钓鱼！", PAL[0], 12610, 52, RED, k0=4, k1=4.5, sfx="pop")
L(face(*PAL, 0.65, "smile"), 5, 5.2, BLACK, 8, sfx="ding")

AUNT = (2950, 12880)
scene("被问起就笑笑带过", "第四步 · 带过", (2650, 12550, 0.85))
L(rect(2650, 12550, 1200, 820, 40), 0, 0.6, GREEN, 8)
T("④ 轻轻带过", 2650, 12250, 76, BLUE, k0=0, sfx="pop")
L(stick(2350, 12880, 0.65), 1, 1.4, BLUE, 9, sfx="wood_high")
L(stick(*AUNT, 0.65, hair=True), 1.4, 1.8, BLACK, 9)
L(bubble(2900, 12450, 400, 120, 1), 2, 2.3, BLACK, 8, sfx="pop")
T("在哪高就？", 2900, 12450, 50, k0=2.3, k1=2.9)
L(bubble(2450, 12530, 420, 110, -1), 3, 3.3, BLUE, 8, sfx="wood_high")
T("歇一阵，您呢？", 2450, 12530, 46, BLUE, k0=3.3, k1=4.0)
L(face(2350, 12880, 0.65, "smile"), 4, 4.2, BLUE, 8, sfx="pop")
L(face(*AUNT, 0.65, "smile"), 5, 5.2, BLACK, 8, sfx="ding")

scene("看人，别看标签", "一句话", (1800, 7400, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 13750, 0.8))
H(0, "cymbal", 0.5)
T("谁的脸色变得最快？", 1800, 13670, 80, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：工资比爸妈高，为什么还觉得穷？", 1800, 13830, 50, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "snob", "势利", "一换工作，亲戚的脸色怎么就变了？", ACC, b.shots,
                 [f"{BOOK}第一部分“焦虑起因”第二章“势利倾向”（转述）",
                  "中译本：阿兰·德波顿《身份的焦虑》，陈广兴、南治国译，上海译文出版社"],
                 "一换工作|亲戚就【换了脸色】", 4,
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
