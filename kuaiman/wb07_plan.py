"""07 规划谬误（白板手绘版）：排期两周，为什么总拖成一个月？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（E 自测清单）：领导问“两周够吗？”，快快抢答“够！”→ 观众对着“排期自测”清单打勾（按一切顺利算 / 没算请假和返工 /
没翻上回用了多久）→ drop：日历被红笔一页页划过去，“又延期！”砸下 → 亮书：作者自己也中招——卡尼曼团队编教材，估约两年；
请教有经验的成员，得知同类团队约四成没做完、做完的花了 7–10 年；最后做了 8 年 → 书中观点：规划谬误，按最好的情况估；
外部视角：快快只盯自己的计划，慢慢看一排过去的项目 → 例子：厨房装修，实际比预算长出一截 → 三招（查同类 / 事前验尸 /
先平均再微调）→ 拉远看全板 → 评论区互动。
书中观点为转述（丹尼尔·卡尼曼《思考，快与慢》第 23 章 The Outside View、第 24 章 The Engine of Capitalism；
中译本胡晓姣、李爱民、何梦莹译，中信出版社 2012）；开局排期、自测三条、装修条形、旧项目天数为示意，做法据书中思路整理。
"""

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, doc, face, join,
                               rect, scribble, stick)

from .common import BOOK, episode, kuai, man

ACC = "#2E8B6A"
SQUARE_SHOT = 3                 # 场景 4：日历被一页页划过去 + 快快冒汗 + “又延期！”

b = Board(size=(3600, 10300))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def TL(s, x0, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """左对齐写字：x0 为左端。"""
    T(s, x0 + K.text_w(s, size, "hand") / 2, y, size, color, k0, k1, sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def clipboard(x, y, w, h) -> skia.Path:
    """写字板：板身 + 顶上的夹子。(x, y) 为板身中心。"""
    top = y - h / 2
    return join(rect(x, y, w, h, 30), rect(x, top, 260, 70, 16), P((x - 60, top - 35), (x - 40, top - 70),
                                                                   (x + 40, top - 70), (x + 60, top - 35)))


def boxes(x, ys, r=40) -> skia.Path:
    return join(*[rect(x, y, 2 * r, 2 * r, 10) for y in ys])


def calendar(x, y, w, h) -> skia.Path:
    """台历外框：板身 + 表头分隔线 + 一排装订环。"""
    top = y - h / 2
    parts = [rect(x, y, w, h, 26), P((x - w / 2, top + 130), (x + w / 2, top + 130))]
    for i in range(4):
        rx = x - w * 0.3 + i * w * 0.2
        parts.append(circle(rx, top, 18))
    return join(*parts)


def sweat(x, y, s=1.0) -> skia.Path:
    """两滴汗：(x, y) 为第一滴顶端。"""
    parts = []
    for dx, dy in ((0, 0), (36 * s, 50 * s)):
        p = skia.Path()
        p.moveTo(x + dx, y + dy)
        p.quadTo(x + dx + 22 * s, y + dy + 40 * s, x + dx, y + dy + 52 * s)
        p.quadTo(x + dx - 22 * s, y + dy + 40 * s, x + dx, y + dy)
        parts.append(p)
    return join(*parts)


def squiggle(x0, x1, y, amp=90) -> skia.Path:
    """绕来绕去的实际路线：带两个回环的曲线。"""
    p = skia.Path()
    w = x1 - x0
    p.moveTo(x0, y)
    p.cubicTo(x0 + w * 0.15, y - amp, x0 + w * 0.3, y + amp, x0 + w * 0.25, y - amp * 0.2)
    p.cubicTo(x0 + w * 0.2, y - amp * 1.1, x0 + w * 0.45, y - amp * 0.8, x0 + w * 0.5, y + amp * 0.3)
    p.cubicTo(x0 + w * 0.55, y + amp * 1.3, x0 + w * 0.72, y + amp * 0.9, x0 + w * 0.7, y - amp * 0.1)
    p.cubicTo(x0 + w * 0.68, y - amp * 1.2, x0 + w * 0.9, y - amp * 0.6, x1, y)
    for d in (0.5, -0.5):
        p.moveTo(x1, y)
        p.lineTo(x1 - 45 * (0.9 if d > 0 else 0.9), y + 40 * d * 2)
    return p


def telescope(x0, y0, x1, y1, r0=16, r1=30) -> skia.Path:
    """望远镜：从 (x0, y0) 眼端到 (x1, y1) 镜口，粗细渐变。"""
    import math
    a = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
    ca, sa = math.cos(a), math.sin(a)
    return join(P((x0 + ca * r0, y0 + sa * r0), (x1 + ca * r1, y1 + sa * r1), (x1 - ca * r1, y1 - sa * r1),
                  (x0 - ca * r0, y0 - sa * r0), close=True),
                P((x1 + ca * (r1 + 8), y1 + sa * (r1 + 8)), (x1 - ca * (r1 + 8), y1 - sa * (r1 + 8))))


def kitchen(x, y) -> skia.Path:
    """厨房：吸油烟机 + 灶台柜 + 锅。(x, y) 为柜台面中点。"""
    return join(rect(x, y + 100, 380, 200, 8), P((x, y), (x, y + 200)), circle(x - 50, y + 100, 8), circle(x + 50, y + 100, 8),
                P((x - 210, y), (x + 210, y)),
                P((x - 110, y - 10), (x - 100, y - 70), (x + 10, y - 70), (x + 20, y - 10)),
                P((x - 125, y - 70), (x + 35, y - 70)),
                P((x - 90, y - 300), (x + 90, y - 300), (x + 150, y - 220), (x - 150, y - 220), close=True),
                P((x - 40, y - 300), (x - 40, y - 380)), P((x + 40, y - 300), (x + 40, y - 380)))


def tomb(x, y, w=420, h=520) -> skia.Path:
    """墓碑：圆拱顶 + 底座。(x, y) 为碑身中心。"""
    top = y - h / 2
    p = skia.Path()
    p.moveTo(x - w / 2, y + h / 2)
    p.lineTo(x - w / 2, top + w / 2)
    p.arcTo(skia.Rect.MakeXYWH(x - w / 2, top, w, w), 180, 180, False)
    p.lineTo(x + w / 2, y + h / 2)
    return join(p, P((x - w / 2 - 50, y + h / 2), (x + w / 2 + 50, y + h / 2)),
                P((x - w / 2 - 50, y + h / 2), (x - w / 2 - 50, y + h / 2 + 40), (x + w / 2 + 50, y + h / 2 + 40),
                  (x + w / 2 + 50, y + h / 2)))


def ruler(x0, x1, y, step=100) -> skia.Path:
    parts = [rect((x0 + x1) / 2, y, x1 - x0, 90, 10)]
    x = x0 + step
    n = 1
    while x < x1 - 1:
        parts.append(P((x, y - 45), (x, y - 45 + (40 if n % 5 == 0 else 22))))
        x += step
        n += 1
    return join(*parts)


def dust(x, y, w) -> skia.Path:
    """书上的灰：几道短线 + 小点。"""
    parts = []
    for i, (dx, dy) in enumerate(((-0.4, 0), (-0.15, -30), (0.1, 5), (0.35, -25))):
        parts.append(P((x + dx * w, y + dy), (x + dx * w + 40, y + dy - 10)))
        parts.append(circle(x + dx * w + 20, y + dy - 45 - (i % 2) * 20, 5))
    return join(*parts)


# ---------------------------------------------------------------- 开局：两周够吗（场景 1）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("两周，够吗？", "灵魂拷问", (950, 900, 0.85), bars=2)
L(stick(600, 1300, 0.8, "point", tie=True), 0, 0.9, sfx="wood_high")
L(face(600, 1300, 0.8, "flat"), 0.9, 1.0)
L(bubble(560, 830, 420, 150, -1), 1, 1.5, BLACK, 8, sfx="pop")
T("两周够吗？", 560, 830, 66, k0=1.5, k1=2.75)
L(kuai(1300, 1300, 0.8, "up"), 3, 3.8, RED, 10, sfx="wood_high")
L(face(1300, 1300, 0.8, "smile"), 3.8, 4.0, RED, 8)
L(bubble(1380, 830, 260, 150, -1), 4, 4.4, RED, 8, sfx="pop")
T("够！", 1380, 830, 84, RED, k0=4.4, k1=5.2)

# ---------------------------------------------------------------- 自测清单（场景 2–3）

CB = (900, 2350, 940, 1000)
BX = 520                                        # 勾选框中心 x
ROWS = [("按一切顺利算", 2190), ("没算请假和返工", 2420), ("没翻上回用了多久", 2650)]
VCB = (1090, 2350, 0.8)

scene("先自测一下", "自测 · 排期", VCB)
L(clipboard(*CB), 0, 0.9, BLACK, 10, sfx="wood_low")
T("排期自测", CB[0], 1990, 84, GREEN, k0=1, k1=2, sfx="pop")
L(boxes(BX, [y for _, y in ROWS]), 2, 2.8, BLACK, 8, sfx="wood_high")
TL(ROWS[0][0], BX + 70, ROWS[0][1], 62, k0=3, k1=4.4, sfx="pop")
TL(ROWS[1][0], BX + 70, ROWS[1][1], 62, k0=4.5, k1=6.0)
TL(ROWS[2][0], BX + 70, ROWS[2][1], 62, k0=6, k1=8.0, sfx="pop")

scene("中了几条？", "自测 · 排期", VCB)
for n, (_, y) in enumerate(ROWS):
    L(check(BX + 6, y - 6, 46), 2 * n, 2 * n + 0.6, RED, 12, sfx="pop")
L(kuai(1580, 2830, 0.65, "up"), 5, 5.8, RED, 9, sfx="wood_high")
L(face(1580, 2830, 0.65, "flat"), 5.8, 6.0, RED, 8)
L(bubble(1600, 2340, 250, 130, -1), 7, 7.3, RED, 8, sfx="pop")
T("全中…", 1600, 2340, 56, RED, k0=7.3, k1=8.0)

# ---------------------------------------------------------------- drop：日历一页页划过去（场景 4）

CAL = (2480, 2290, 700, 760)
PAGE_Y = CAL[1] + 65                            # 页面中心
PAGES = ["第2周", "第3周", "第4周", "第5周"]
FLIPS = (1, 2, 3)                               # 第 1/2/3 拍：红笔一划，翻到下一页

j_cal = scene("又拖成一个月", "自测 · 结果", (2650, 2350, 0.8), shake=[0, 6], flashes=[0])
L(calendar(*CAL), 0, 0.8, BLACK, 10, sfx="kick")


def _page(c, label, x, y, w, h, alpha=1.0, slash=0.0, circled=0.0):
    K.rr(c, x, y, w, h, 12, "#FBFBF9", alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 12, 12, K.paint(BLACK, alpha * 0.5, 4))
    K.text(c, label, x, y, 170, "hand", BLACK, alpha)
    tip = None
    if slash > 0:
        x0, y0, x1, y1 = x - 230, y + 150, x + 230, y - 150
        f = clamp01(slash)
        c.drawLine(x0, y0, x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, K.paint(RED, alpha, 14))
        tip = (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
    if circled > 0:
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(x - 240, y - 130, 480, 260), -90, 360 * clamp01(circled))
        c.drawPath(p, K.paint(RED, alpha, 12))
    return tip


def calendar_fn(c, k, t):
    """台历：表头“排期：两周”；红笔在当前页一划（第 1/2/3 拍），该页随即向上翻走露出下一页；第 4 拍红圈圈住“第5周”。"""
    x, w, h = CAL[0], CAL[2] - 60, CAL[3] - 190
    a = clamp01((t - b.t_of(j_cal, 0)) / max(1e-3, b.t_of(j_cal, 0.8) - b.t_of(j_cal, 0)))
    K.text(c, "排期：两周", x, CAL[1] - CAL[3] / 2 + 70, 60, "hand", BLUE, a)
    beat = b.t_of(j_cal, 1) - b.t_of(j_cal, 0)
    cur, tip = 0, None
    for n, kb in enumerate(FLIPS):
        if t >= b.t_of(j_cal, kb) + 0.75 * beat:
            cur = n + 1
    # 底下一页（翻页时露出）
    if cur + 1 < len(PAGES):
        tf = b.t_of(j_cal, FLIPS[cur])
        if t >= tf + 0.4 * beat:
            _page(c, PAGES[cur + 1], x, PAGE_Y, w, h)
    # 当前页：划一刀 → 向上翻走
    if cur < len(FLIPS):
        tf = b.t_of(j_cal, FLIPS[cur])
        sl = clamp01((t - tf) / (0.35 * beat)) if t >= tf else 0.0
        fl = ease_in_out(clamp01((t - tf - 0.4 * beat) / (0.35 * beat))) if t >= tf else 0.0
        top = PAGE_Y - h / 2
        with K.at(c, x, top, 0, 1.0, 1 - 0.92 * fl):
            tip = _page(c, PAGES[cur], 0, h / 2, w, h, a * (1 - 0.7 * fl), sl)
        if tip is not None and fl == 0:
            tip = (x + tip[0], top + (tip[1]))
        else:
            tip = None
    else:
        tc = b.t_of(j_cal, 4)
        circ = clamp01((t - tc) / (0.6 * beat)) if t >= tc else 0.0
        _page(c, PAGES[-1], x, PAGE_Y, w, h, 1.0, 0.0, circ)
        if 0 < circ < 1:
            import math
            ang = math.radians(-90 + 360 * circ)
            tip = (x + 240 * math.cos(ang), PAGE_Y + 130 * math.sin(ang))
    return tip


b.custom(j_cal, 0, 5, calendar_fn)
for kb in FLIPS:
    H(kb, "rim", 0.8, "红笔划掉一页")
H(4, "rim", 0.8, "红圈圈住第5周")
T("又延期！", 2480, 2840, 120, RED, k0=6, k1=7.0, sfx="kick")
L(kuai(3140, 2760, 0.65, "shrug"), 5, 5.8, RED, 9, sfx="wood_high")
L(face(3140, 2760, 0.65, "sad"), 5.8, 6.0, RED, 8)
L(sweat(3205, 2440, 1.0), 7.2, 7.8, BLUE, 7)

# ---------------------------------------------------------------- 书里的故事：编教材（场景 5–7）

scene("作者自己也中招", "思考，快与慢 · 书中观点", (1100, 3850, 0.8))
L(book(720, 3740, 420, 280), 0, 0.9, BLACK, 10, sfx="wood_low")
T("思考，快与慢", 720, 3500, 66, GREEN, k0=1, k1=2.4, sfx="pop")
T("卡尼曼编教材", 720, 3990, 58, k0=2.5, k1=3.9)
L(kuai(1250, 4220, 0.6, "up"), 4, 4.8, RED, 9, sfx="wood_high")
L(face(1250, 4220, 0.6, "smile"), 4.8, 5.0, RED, 8)
L(man(1560, 4220, 0.6, "down"), 5, 5.8, BLUE, 9, sfx="wood_high")
L(bubble(1380, 3660, 400, 140, -1), 6, 6.4, RED, 8, sfx="pop")
T("估：2 年左右", 1380, 3660, 56, RED, k0=6.4, k1=8.0)

scene("一问，吓一跳", "书中例子 · 编教材", (2650, 3850, 0.8))
L(stick(2150, 4300, 0.75, "point", hair=True), 0, 0.9, BLACK, 10, sfx="wood_high")
L(face(2150, 4300, 0.75, "flat"), 0.9, 1.0)
L(bubble(2800, 3720, 860, 400, -1), 1, 1.6, BLACK, 8, sfx="pop")
T("同类团队：", 2800, 3600, 56, k0=2, k1=3.25, sfx="pop")
T("约四成没做完", 2800, 3710, 66, RED, k0=3.5, k1=5.0)
T("做完的：7–10 年", 2800, 3825, 58, k0=5, k1=7.0, sfx="pop")
L(man(3150, 4300, 0.55, "shrug"), 7, 7.8, BLUE, 9, sfx="wood_high")

X0, YR = 2060, 5150                             # 时间轴起点、轴线 y
PER = 143.75                                    # 每年的长度
j_bar = scene("最后做了八年", "书中例子 · 编教材", (2650, 5250, 0.8))
L(join(P((X0, YR), (X0 + 8 * PER + 60, YR)),
       *[P((X0 + i * PER, YR), (X0 + i * PER, YR + (30 if i % 2 == 0 else 16))) for i in range(9)]),
  0, 0.9, BLACK, 9, sfx="wood_high")
T("估 2 年", X0 + 2 * PER, 4960, 56, BLUE, k0=1, k1=2, sfx="pop")
STEPS = (2, 3, 4, 5)                            # 第 2–5 拍：每拍长出两年


def bar_fn(c, k, t):
    beat = b.t_of(j_bar, 1) - b.t_of(j_bar, 0)
    yrs = 0.0
    for n, kb in enumerate(STEPS):
        t0 = b.t_of(j_bar, kb)
        if t >= t0:
            yrs = 2 * n + 2 * ease_out(clamp01((t - t0) / (0.6 * beat)))
    if yrs <= 0:
        return None
    xe = X0 + yrs * PER
    blue_end = X0 + min(yrs, 2) * PER
    K.rr(c, (X0 + blue_end) / 2, YR - 50, blue_end - X0, 70, 6, BLUE, 0.35)
    if yrs > 2:
        K.rr(c, (blue_end + xe) / 2, YR - 50, xe - blue_end, 70, 6, RED, 0.35)
    c.drawRoundRect(skia.Rect.MakeXYWH(X0, YR - 85, xe - X0, 70), 6, 6, K.paint(BLACK, 1, 6))
    return (xe, YR - 50) if yrs < 8 else None


b.custom(j_bar, 2, 6, bar_fn)
for kb in STEPS:
    H(kb, "tom", 0.7, "进度条长两年")
T("8 年", X0 + 8 * PER, 4960, 104, RED, k0=6, k1=6.8, sfx="ding")
L(join(book(2460, 5580, 300, 200), dust(2460, 5420, 300)), 7, 7.9, BLACK, 8, sfx="shaker")

# ---------------------------------------------------------------- 书中观点：规划谬误、外部视角（场景 8–9）

scene("只看自己，不看别人", "思考，快与慢 · 书中观点", (1000, 5250, 0.8))
T("规划谬误", 1000, 4800, 110, RED, k0=0, k1=1, sfx="tom")
T("按最好的情况估", 1000, 4990, 70, k0=2, k1=3.75, sfx="pop")
T("想的", 440, 5280, 56, GREEN, k0=4, k1=4.8, sfx="pop")
L(arrow((560, 5280), (1560, 5280), 0.0, 44), 5, 5.7, GREEN, 9, sfx="wood_high")
T("真的", 440, 5540, 56, RED, k0=6, k1=6.8, sfx="pop")
L(squiggle(560, 1560, 5540, 85), 7, 7.9, RED, 9, sfx="wood_low")

scene("往外看一眼", "书中观点 · 外部视角", (1000, 6650, 0.8))
L(join(kuai(480, 7000, 0.6, "hold"), telescope(520, 6815, 700, 6680)), 0, 0.9, RED, 9, sfx="wood_high")
L(doc(840, 6600, 150, 190), 1, 1.7, BLACK, 8, sfx="pop")
T("只看自己", 650, 6330, 60, RED, k0=2, k1=3, sfx="pop")
L(man(1270, 7000, 0.6, "point"), 4, 4.8, BLUE, 9, sfx="wood_high")
L(join(*[doc(1150 + i * 140, 6600, 110, 150, 3) for i in range(3)]), 5, 5.8, BLACK, 7, sfx="pop")
T("外部视角", 1290, 6390, 60, BLUE, k0=6, k1=7, sfx="pop")
L(check(1430, 6395, 30), 7.2, 7.7, GREEN, 8)

# ---------------------------------------------------------------- 例子：装修（场景 10）

BAR_X = 2240
scene("装修也一样", "例子 · 装修", (2650, 6650, 0.8))
L(kitchen(2300, 6430), 0, 0.9, BLACK, 9, sfx="wood_high")
T("厨房装修", 2900, 6300, 72, k0=1, k1=2, sfx="pop")
T("预算", 2140, 6830, 56, k0=2, k1=2.8, sfx="pop")
L(rect(BAR_X + 300, 6830, 600, 70, 6), 3, 3.6, BLUE, 9, sfx="wood_high")
T("实际", 2140, 7000, 56, k0=4, k1=4.8, sfx="pop")
L(rect(BAR_X + 500, 7000, 1000, 70, 6), 5, 5.8, RED, 9, sfx="wood_low")
L(join(P((BAR_X + 600, 6780), (BAR_X + 600, 7060)), scribble(BAR_X + 800, 7000, 380, 60, 6)), 6, 6.7, RED, 7,
  sfx="rim")
T("多出一截", BAR_X + 800, 7130, 60, RED, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 三招（场景 11–13）

CARDS = [(2200, "28 天"), (2650, "35 天"), (3100, "30 天")]
scene("翻翻上回用了多久", "第一招 · 查同类", (2650, 8050, 0.8))
T("① 查同类", 2650, 7560, 80, BLUE, k0=0, k1=1.25, sfx="pop")
L(join(*[join(rect(x, 7900, 360, 300, 20), P((x - 130, 7800), (x + 60, 7800)), P((x - 130, 7840), (x + 10, 7840)))
         for x, _ in CARDS]), 2, 2.9, BLACK, 8, sfx="wood_high")
for n, (x, s) in enumerate(CARDS):
    T(s, x, 7940, 80, RED, k0=3 + n, k1=3.8 + n, sfx="pop")
T("平均：约一个月", 2650, 8250, 68, k0=6, k1=7.75, sfx="ding")

scene("先想想会怎么砸", "第二招 · 事前验尸", (1000, 8050, 0.8))
T("② 事前验尸", 1000, 7560, 80, BLUE, k0=0, k1=1.4, sfx="pop")
L(tomb(1000, 8020, 400, 520), 2, 2.8, BLACK, 10, sfx="wood_low")
T("项目", 1000, 7920, 76, k0=3, k1=3.8, sfx="pop")
T("一年后", 1000, 8040, 56, k0=3.9, k1=4.7)
NOTES = [(530, 7820, "改需求"), (1470, 7820, "缺人手"), (1470, 8180, "没测试")]
L(join(*[rect(x, y, 230, 120, 6) for x, y, _ in NOTES]), 5, 5.5, ACC, 8, sfx="pop")
for n, (x, y, s) in enumerate(NOTES):
    T(s, x, y, 56, k0=5.5 + 0.8 * n, k1=6.3 + 0.8 * n)

scene("从平均数开始估", "第三招 · 先平均", (1000, 9450, 0.8))
T("③ 先平均，再微调", 1000, 8990, 76, BLUE, k0=0, k1=2, sfx="pop")
L(ruler(420, 1580, 9480), 2, 2.9, BLACK, 8, sfx="wood_high")
L(P((1000, 9360), (1000, 9600)), 3, 3.4, RED, 12, sfx="ding")
T("平均", 1000, 9670, 60, RED, k0=3.4, k1=4.2)
L(arrow((1000, 9330), (1180, 9330), -0.25, 30), 5, 5.6, BLUE, 9, sfx="wood_high")
T("按自己情况挪一点", 1090, 9220, 56, BLUE, k0=6, k1=8.0, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 5150, 0.175)
CV = (2650, 9480, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, CV, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你上回延期了多久？", 2650, 9250, 76, RED, k0=6, k1=8.25, sfx="pop")
L(kuai(2350, 9960, 0.6, "up"), 9, 9.8, RED, 9, sfx="wood_high")
L(face(2350, 9960, 0.6, "smile"), 9.8, 10.0, RED, 8)
L(man(2950, 9960, 0.6, "down"), 10, 10.8, BLUE, 9, sfx="wood_high")
L(face(2950, 9960, 0.6, "smile"), 10.8, 11.0, BLUE, 8)
T("下一讲：赢150输100，你敢赌吗？", 2650, 9420, 50, k0=11, k1=14.5, sfx="pop")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "plan", "规划谬误", "排期两周，为什么总拖成一个月？", ACC, b.shots,
                 [f"{BOOK}第23章 努力养成采纳外部意见的决策习惯（The Outside View）（转述）",
                  f"{BOOK}第24章 乐观主义是一柄双刃剑（The Engine of Capitalism）（转述）",
                  "中译本：胡晓姣、李爱民、何梦莹译，中信出版社 2012"],
                 "排期两周|总拖成【一个月】", SQUARE_SHOT,
                 ["书中观点均为转述：卡尼曼和同事给以色列教育部编一套教材，团队估计大约两年能完成；请教团队里有经验的成员后得知，"
                  "同类团队约四成没有做完，做完的花了 7–10 年；这套教材最后用了 8 年（第 23 章）。规划谬误：计划和预算按最好的"
                  "情况来估，不去看同类项目的实际结果；纠正办法是外部视角，也就是参照同类项目来预测（第 23 章）。"
                  "事前验尸由 Gary Klein 提出：做决定之前，假设一年后项目失败了，让每人写下失败的原因（第 24 章）。"
                  "白板上的“约两年”“四成”“7–10 年”“8 年”为书中数据。",
                  "书中提到装修超支属于规划谬误的常见情形；厨房装修的两条预算 / 实际条为示意，长度不是数据。",
                  "开局领导问排期、快快抢答“够！”、自测三条、日历“第2周→第5周”为示意；旧项目卡片上的天数（28 / 35 / 30 天）"
                  "与“平均约一个月”为示意，不是数据；事前验尸墓碑上的三条原因为示意。",
                  "三招中“查同类”“先平均，再微调”据书中外部视角 / 参照类预测的思路整理；“事前验尸”据第 24 章转述。"
                  "不指向任何具体公司或个人。"],
                 tags="#拖延 #项目管理")
    return b.attach(ep)
