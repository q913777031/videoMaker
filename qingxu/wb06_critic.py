"""06 被批评（白板手绘版）：被领导当众批评，怎么接？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事：F 两人对比——周会上领导一句“这方案太粗了”，同一句话落到小周和小林两个人头上（同一朵乌云）→
亮书《伯恩斯新情绪疗法》第 6 章“语言柔道”（借力接住）→ ★drop：白板被一道红线劈成两半，两条路 →
左路小周：顶回去“我加班做的”，气氛僵住；或者当场认怂，回家乌云“我不行”越长越大 →
右路小林按书里三步接：先问清楚哪部分（预算那页）/ 说得对的先认下 / 说出自己的情况、商量怎么改 →
两条路的终点：左边冷场、右边排期定了 → 书中观点：批评说的是那一页，框不住这个人 →
做法：心里先问“他说的哪部分对”，用三栏卡（想法 / 哪种歪 / 换个说法）改写 → 三步收成三个词 → 拉远全板 → 评论区。
书中观点为转述（戴维·伯恩斯《伯恩斯新情绪疗法》第 6 章“语言柔道——学会反驳自我批评”，李亚萍译）；
“三步接”据第 6 章方法整理，对话、人物（小林为虚构）与例子为现实场景示意。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, doc, face,
                               join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#3E8E9C"
SQUARE_SHOT = 3                 # 场景 4：小周、小林 + 红线劈开的两条路

b = Board(size=(3600, 15200))
OX, OY = 0, 0                   # 当前场景的坐标原点（下面的坐标都相对它写）
GRAY = "#55555E"


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(len(b.shots) - 1, k0, k1, s, x + OX, y + OY, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    path = skia.Path(path)
    path.offset(OX, OY)
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(len(b.shots) - 1, k, sfx, gain, note)


def scene(text, tag, center, z=0.85, bars=3, anchor=None, **kw):
    """新场景：相机看向 center=(cx, cy)；之后的坐标相对 anchor（默认就是 center）。"""
    global OX, OY
    OX, OY = anchor or center
    return b.shot(text, tag, view=(center[0], center[1], z), bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def cloud(x, y, w, h, n=9) -> skia.Path:
    """念头云外轮廓：一圈向外鼓的弧。"""
    pts = [(x + w / 2 * math.cos(i / n * 2 * math.pi), y + h / 2 * math.sin(i / n * 2 * math.pi)) for i in range(n)]
    bump = min(w, h) * 0.2
    p = skia.Path()
    p.moveTo(*pts[0])
    for i in range(n):
        a0, a1 = pts[i], pts[(i + 1) % n]
        mx, my = (a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2
        ox, oy = mx - x, my - y
        d = math.hypot(ox, oy) or 1
        p.quadTo(mx + ox / d * bump, my + oy / d * bump, *a1)
    p.close()
    return p


def ring(x, y, w, h, n=44) -> skia.Path:
    """乌云的涂黑边：沿轮廓内侧来回涂的一圈锯齿。"""
    pts = []
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        r = 1.0 if i % 2 == 0 else 0.8
        pts.append((x + w / 2 * r * math.cos(a), y + h / 2 * r * math.sin(a)))
    return P(*pts)


def dark(x, y, w, h, k, words=None, size=60, sfx="tom"):
    """乌云：外轮廓 + 涂黑边，里面红字。第 k 拍起笔，轮廓 0.5 拍、黑边 0.4 拍，字随后写。"""
    L(cloud(x, y, w, h), k, k + 0.5, BLACK, 9, sfx=sfx)
    L(ring(x, y, w * 0.92, h * 0.86), k + 0.5, k + 0.9, GRAY, 5)
    if words:
        T(words, x, y, size, RED, k0=k + 0.9)


def badge(x, y, s=1.0) -> skia.Path:
    """工牌：挂绳 + 胸前小卡。(x, y) 为该小人的脚底。"""
    hy = y - 290 * s
    return join(P((x - 18 * s, hy + 115 * s), (x, hy + 50 * s), (x + 18 * s, hy + 115 * s)),
                rect(x, hy + 140 * s, 40 * s, 50 * s, 5 * s))


def worker(x, y, s=0.8, arms="down", hair=False) -> skia.Path:
    return join(stick(x, y, s, arms, hair=hair), badge(x, y, s))


def figure(x, y, s=0.8, side=1, tie=False, hair=False) -> skia.Path:
    """只画外侧一只手的小人（另一只手留给握手）。side=1 表示空着的手朝右。"""
    hy = y - 290 * s
    sh = hy + 80 * s
    parts = [circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)),
             P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)), P((x, sh), (x - side * 70 * s, hy + 170 * s))]
    if tie:
        parts.append(P((x, hy + 50 * s), (x - 12 * s, hy + 100 * s), (x, hy + 120 * s), (x + 12 * s, hy + 100 * s),
                       close=True))
    if hair:
        parts.append(P((x - 45 * s, hy - 5 * s), (x - 30 * s, hy - 45 * s), (x + 30 * s, hy - 45 * s),
                       (x + 50 * s, hy + 10 * s)))
    if not tie:
        parts.append(badge(x, y, s))
    return join(*parts)


def table(x, y, w=700) -> skia.Path:
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 40, y), (x - w / 2 + 40, y + 110)),
                P((x + w / 2 - 40, y), (x + w / 2 - 40, y + 110)))


def rays(x, y, w, h) -> skia.Path:
    parts = []
    for dx, dy, ex, ey in ((-1, -1, -1.2, -1.6), (0, -1.1, 0, -1.7), (1, -1, 1.2, -1.6),
                           (-1.08, 0.2, -1.3, 0.5), (1.08, 0.2, 1.3, 0.5)):
        parts.append(P((x + dx * w / 2, y + dy * h / 2), (x + ex * w / 2, y + ey * h / 2)))
    return join(*parts)


def crack(x, y0, y1, amp=26, step=110) -> skia.Path:
    """劈开白板的锯齿竖线。"""
    pts, y, k = [(x, y0)], y0, 0
    while y + step < y1:
        y += step
        k += 1
        pts.append((x + (amp if k % 2 else -amp), y))
    pts.append((x, y1))
    return P(*pts)


def burst(x, y, r0=40, r1=110, n=8) -> skia.Path:
    return join(*[P((x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a)))
                  for a in (i / n * 2 * math.pi + 0.2 for i in range(n))])


def zap(a, c, n=6, amp=26) -> skia.Path:
    """两人对瞪：横着的闪电线。"""
    (x0, y0), (x1, y1) = a, c
    return P(*[(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n + (0 if i in (0, n) else (amp if i % 2 else -amp)))
               for i in range(n + 1)])


def ice(x, y, s=150) -> skia.Path:
    """冰块：正面方块 + 顶面 + 侧面。"""
    d = s * 0.32
    h = s / 2
    return join(rect(x, y, s, s, 10),
                P((x - h, y - h), (x - h + d, y - h - d), (x + h + d, y - h - d), (x + h, y - h)),
                P((x + h + d, y - h - d), (x + h + d, y + h - d), (x + h, y + h)))


def moon(x, y, r=60) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def thrown(x, y, s=0.6, deg=100) -> skia.Path:
    """被借力摔起来的小人：整个人旋转着翻过去。(x, y) 为旋转中心。"""
    p = stick(0, 145 * s, s, "up")
    p.transform(skia.Matrix.RotateDeg(deg, skia.Point(0, 0)))
    p.offset(x, y)
    return p


def calendar(x, y, w=300, h=280) -> skia.Path:
    parts = [rect(x, y, w, h, 16), P((x - w / 2, y - h / 2 + 70), (x + w / 2, y - h / 2 + 70)),
             P((x - w / 4, y - h / 2 - 30), (x - w / 4, y - h / 2 + 20)),
             P((x + w / 4, y - h / 2 - 30), (x + w / 4, y - h / 2 + 20))]
    for r in range(2):
        for c in range(3):
            parts.append(rect(x - w / 3 + c * w / 3, y + 10 + r * 85, 50, 50, 6))
    return join(*parts)


def card3(x, y, w=1180, h=700, head=130) -> skia.Path:
    """三栏卡：外框 + 两条竖线 + 表头横线。"""
    return join(rect(x, y, w, h, 24), P((x - w / 6, y - h / 2), (x - w / 6, y + h / 2)),
                P((x + w / 6, y - h / 2), (x + w / 6, y + h / 2)),
                P((x - w / 2, y - h / 2 + head), (x + w / 2, y - h / 2 + head)))


# ---------------------------------------------------------------- 开局：同一句批评（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("方案太粗了", "灵魂拷问", (1800, 900), bars=2, shake=[3])
L(table(200, 290, 700), 0, 0.9, sfx="wood_high")
L(stick(-350, 500, 0.8, "point", tie=True), 1, 1.8, sfx="wood_low")
L(face(-350, 500, 0.8, "sad"), 1.8, 2.0)
L(doc(150, 178, 170, 210), 2, 2.8, BLACK, 8, sfx="pop")
T("这方案太粗了", 0, -330, 110, RED, k0=3, k1=4.5, sfx="kick")
L(rays(0, -330, 720, 140), 5, 5.8, RED, 8, sfx="rim")

S2 = (1800, 2250)
ZHOU, LIN = (-350, 400), (350, 400)
scene("两个人同一句", "同一句批评", S2)
L(join(arrow((0, -470), (-300, -260), 0.12, 40), arrow((0, -470), (300, -260), -0.12, 40)), 0, 0.9, RED, 8,
  sfx="wood_high")
L(worker(*ZHOU, 0.8), 1, 1.8, sfx="pop")
L(face(*ZHOU, 0.8, "flat"), 1.8, 2.0)
T("小周", ZHOU[0], 490, 56, k0=2, k1=2.8, sfx="pop")
L(worker(*LIN, 0.8, hair=True), 3, 3.8, BLUE, 10, sfx="wood_high")
L(face(*LIN, 0.8, "flat"), 3.8, 4.0, BLUE, 9)
T("小林", LIN[0], 490, 56, BLUE, k0=4, k1=4.8, sfx="pop")
L(join(cloud(-350, -110, 420, 230), cloud(350, -110, 420, 230)), 5, 5.5, BLACK, 9, sfx="tom")
L(join(ring(-350, -110, 386, 198), ring(350, -110, 386, 198)), 5.5, 5.9, GRAY, 5)
T("太粗了", -350, -110, 66, RED, k0=6, k1=6.8, sfx="rim")
T("太粗了", 350, -110, 66, RED, k0=7, k1=7.8, sfx="rim")

# ---------------------------------------------------------------- 书中观点：语言柔道（场景 3）

scene("借力接住", "伯恩斯新情绪疗法 · 第6章", (650, 1050))
L(book(-230, -60, 380, 260), 0, 0.9, sfx="wood_low")
T("伯恩斯新情绪疗法", 0, -400, 64, GREEN, k0=1, k1=3, sfx="pop")
L(stick(250, 330, 0.7, "hold"), 3, 3.8, sfx="wood_high")
L(face(250, 330, 0.7, "smile"), 3.8, 4.0)
L(thrown(250, 30, 0.6, 105), 4, 4.8, BLUE, 9, sfx="tom")
L(arrow((470, 40), (90, 250), -0.45, 40), 5, 5.8, RED, 8, sfx="rim")
T("第6章 语言柔道", 0, 470, 70, RED, k0=6, k1=8, sfx="pop")

# ---------------------------------------------------------------- ★drop：白板一劈两半（场景 4）

scene("一句话，两条路", "两条路", (1800, 2540), z=0.6, anchor=S2, shake=[0], flashes=[0])
L(crack(0, -470, 1060), 0, 0.7, RED, 14, sfx="kick")
L(burst(0, 640, 50, 130), 1, 1.6, RED, 8, sfx="rim")
T("顶回去", -460, 700, 84, RED, k0=2, k1=2.8, sfx="pop")
T("认怂", -460, 850, 84, RED, k0=3, k1=3.8, sfx="pop")
L(arrow((-460, 930), (-780, 1060), 0.15, 40), 4, 4.8, BLACK, 9, sfx="wood_low")
T("三步接住", 430, 760, 90, GREEN, k0=5, k1=6, sfx="pop")
L(check(730, 750, 50), 6, 6.6, GREEN, 11, sfx="ding")
L(arrow((430, 860), (780, 1060), -0.15, 40), 7, 7.8, BLACK, 9, sfx="wood_high")

# ---------------------------------------------------------------- 左路：小周（场景 5–6）

scene("顶回去，更僵了", "左 · 顶回去", (900, 4150))
L(worker(-280, 470, 0.75), 0, 0.8, sfx="wood_high")
L(face(-280, 470, 0.75, "sad"), 0.8, 1.0)
L(stick(300, 470, 0.75, tie=True), 1, 1.8, sfx="wood_low")
L(face(300, 470, 0.75, "sad"), 1.8, 2.0)
L(bubble(-200, -330, 470, 140, -1), 2, 2.6, BLACK, 8, sfx="pop")
T("我加班做的", -200, -330, 58, RED, k0=2.6, k1=3.85)
L(zap((-190, 250), (210, 250)), 4, 4.8, RED, 8, sfx="rim")
L(ice(290, -170, 160), 5, 5.9, BLUE, 9, sfx="shaker")
T("僵", 290, -170, 96, BLUE, k0=6, k1=6.8, sfx="tom")

scene("回家越想越难受", "左 · 认怂", (900, 5450), shake=[6])
L(moon(-480, -420, 60), 0, 0.8, BLACK, 9, sfx="wood_low")
L(worker(-420, 480, 0.75), 1, 1.8, sfx="wood_high")
L(face(-420, 480, 0.75, "sad"), 1.8, 2.0)
dark(-180, 230, 260, 140, 2, "我不行", 46)
dark(60, -20, 380, 200, 4, "我不行", 58)
dark(250, -330, 560, 280, 6, "我不行", 84, sfx="kick")

# ---------------------------------------------------------------- 右路：小林的三步（场景 7–9）

scene("先问哪里太粗", "右 · 第一步", (2700, 4150))
T("① 先问清楚", 0, -470, 72, BLUE, k0=0, k1=1.5, sfx="pop")
L(worker(-330, 480, 0.75, hair=True), 2, 2.8, BLUE, 10, sfx="wood_high")
L(face(-330, 480, 0.75, "flat"), 2.8, 3.0, BLUE, 9)
L(stick(330, 480, 0.75, tie=True), 3, 3.8, sfx="wood_low")
L(face(330, 480, 0.75, "flat"), 3.8, 4.0)
L(bubble(-200, -250, 480, 140, -1), 4, 4.6, BLUE, 8, sfx="pop")
T("哪部分太粗？", -200, -250, 56, BLUE, k0=4.6, k1=6)
L(bubble(250, 30, 380, 140, 1), 6, 6.6, BLACK, 8, sfx="pop")
T("预算那页", 250, 30, 58, k0=6.6, k1=7.6)

scene("对的先认下", "右 · 第二步", (2700, 5450))
T("② 先认下", 0, -470, 72, BLUE, k0=0, k1=1.0, sfx="pop")
L(worker(380, 480, 0.75, hair=True), 1, 1.8, BLUE, 10, sfx="wood_high")
L(face(380, 480, 0.75, "smile"), 1.8, 2.0, BLUE, 9)
L(doc(-330, 90, 280, 340, 5), 2, 2.8, BLACK, 9, sfx="wood_low")
T("预算", -330, -160, 62, k0=3, k1=3.8, sfx="pop")
L(check(-330, 90, 75), 4, 4.6, GREEN, 12, sfx="ding")
L(bubble(150, -230, 620, 150, 1), 5, 5.5, BLUE, 8, sfx="pop")
T("预算那页确实没拆细", 150, -230, 52, BLUE, k0=5.5, k1=7.75)

HS = (0, 340)                    # 握手的位置
scene("再商量怎么改", "右 · 第三步", (2700, 6750))
T("③ 再商量", 0, -470, 72, BLUE, k0=0, k1=1.25, sfx="pop")
L(figure(-180, 480, 0.8, side=-1, hair=True), 2, 2.8, BLUE, 10, sfx="wood_high")
L(face(-180, 480, 0.8, "smile"), 2.8, 3.0, BLUE, 9)
L(figure(180, 480, 0.8, side=1, tie=True), 3, 3.8, sfx="wood_low")
L(face(180, 480, 0.8, "smile"), 3.8, 4.0)
L(bubble(-130, -170, 640, 150, -1), 4, 4.5, BLUE, 8, sfx="pop")
T("周四前补上，可以吗？", -130, -170, 52, BLUE, k0=4.5, k1=7)
L(join(P((-180, 480 - 232 + 64), HS), P((180, 480 - 232 + 64), HS), circle(*HS, 20),
       burst(HS[0], HS[1] - 20, 45, 85, 5)), 7, 7.8, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 两条路的终点（场景 10）

scene("左边冷场，右边往前", "两条路 · 结果", (1800, 8750), z=0.45)
L(P((0, -1000), (0, 900)), 0, 0.8, GRAY, 9, sfx="wood_low")
L(arrow((-600, -1000), (-600, -560), 0, 60), 1, 1.8, BLACK, 12, sfx="wood_high")
dark(-600, -230, 640, 340, 2, "我不行", 100)
T("冷场", -600, 300, 140, k0=4, k1=4.8, sfx="rim")
L(arrow((600, -1000), (600, -560), 0, 60), 5, 5.8, BLACK, 12, sfx="wood_high")
L(calendar(600, -230, 380, 340), 6, 6.8, BLUE, 11, sfx="pop")
T("排期定了", 600, 300, 140, GREEN, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 书中观点：说的是一件事（场景 11）

scene("说的是那一页", "书中观点 · 批评", (1800, 10500))
L(rect(-230, 30, 640, 600, 20), 0, 0.9, RED, 11, sfx="wood_high")
T("批评", -230, -380, 76, RED, k0=1, k1=1.8, sfx="pop")
T("预算那页", -230, -170, 62, k0=2, k1=3, sfx="pop")
L(doc(-230, 130, 240, 260, 4), 3, 3.8, BLACK, 9, sfx="wood_low")
L(worker(380, 470, 0.8), 5, 5.8, sfx="wood_high")
L(face(380, 470, 0.8, "smile"), 5.8, 6.0)
T("人在框外", 380, -150, 72, BLUE, k0=6, k1=7, sfx="ding")

# ---------------------------------------------------------------- 做法：三栏卡（场景 12）

CW = 1180 / 3
scene("他说的哪部分对", "做法 · 三栏卡", (1800, 11800))
L(card3(0, 60), 0, 0.8, BLACK, 9, sfx="wood_high")
T("想法", -CW, -225, 56, k0=1, k1=1.8, sfx="pop")
T("哪种歪", 0, -225, 56, k0=2, k1=2.8, sfx="pop")
T("换个说法", CW, -225, 56, k0=3, k1=4, sfx="pop")
T("他看不起我", -CW, 80, 54, RED, k0=4, k1=5, sfx="pop")
dark(0, 80, 330, 190, 5, None)
T("读心术", 0, 80, 54, RED, k0=5.5, k1=6.3)
T("他说的是预算", CW, 80, 50, BLUE, k0=6.5, k1=8)

# ---------------------------------------------------------------- 三步收成三个词（场景 13）

scene("问清认对商量", "三步接住", (1800, 13100))
T("被批评时", 0, -330, 76, k0=0, k1=1.0, sfx="pop")
for n, (word, col) in enumerate((("问清", BLUE), ("认对", GREEN), ("商量", BLUE))):
    x = (n - 1) * 420
    L(rect(x, 0, 300, 170, 24), 1 + 2 * n, 1.5 + 2 * n, col, 10, sfx="wood_high")
    T(word, x, 0, 76, col, k0=1.5 + 2 * n, k1=2.3 + 2 * n)
    if n < 2:
        L(arrow((x + 160, 0), (x + 262, 0), 0, 30), 2.4 + 2 * n, 2.9 + 2 * n, BLACK, 9)
L(underline(-560, 560, 150), 7, 7.8, RED, 9, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 7600, 0.064)
END = (1800, 14450, 0.8)
j_end = scene("评论区聊聊", "评论区见", FAR[:2], z=FAR[2], bars=4, anchor=END[:2])
b.move(j_end, 4, END, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("最难接的一句批评是什么？", 0, -330, 72, RED, k0=6, k1=8.5, sfx="pop")
L(cloud(330, 390, 560, 200), 9, 9.5, BLUE, 9, sfx="ding")
T("今天换掉一朵乌云", 330, 390, 50, BLUE, k0=9.5, k1=11.5)
T("下一讲：群里怼完同事，为什么又后悔？", 0, -150, 50, k0=12, k1=15.6, sfx="wood_high")
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "critic", "被批评", "被领导当众批评，怎么接？", ACC, b.shots,
                 [f"{BOOK}，第 6 章“语言柔道——学会反驳自我批评”（转述）",
                  "中译本：中国城市出版社 2011（ISBN 9787507423655）；科学技术文献出版社 2014（ISBN 9787502395070）"],
                 "被领导当众批评|怎么【接】", SQUARE_SHOT,
                 ["书中观点均为转述：被批评时难受，是因为心里认定“他说我不好，我就真的不好”；书中给的应对是先共情"
                  "（问清对方具体指什么）、再找出对方说得对的部分先认下来，最后说出自己的情况、和对方商量。见第 6 章"
                  "“语言柔道”。上屏的“问清 / 认对 / 商量”与“三步接住”为据书中方法整理的口语叫法，李亚萍译本原用词未核实。",
                  "“批评说的是那一页，框不住这个人”为对书中观点的通俗化示意；三栏卡（想法 / 哪种歪 / 换个说法）与"
                  "“读心术”名牌沿用本系列第 02–04 讲的叫法（通行译法）。",
                  "周会上被说“方案太粗了”、小周顶回去或认怂、小林按三步接住，以及“预算那页”“周四前补上”等台词，"
                  "均为现实场景示意（小周、小林为虚构人物），不指向任何具体公司或个人；不是书中病例。",
                  "本片为读书分享，不能替代诊断和治疗；情绪持续低落或有轻生念头，请尽快联系医生、心理咨询师或当地心理援助热线。"],
                 tags="#职场沟通")
    return b.attach(ep)
