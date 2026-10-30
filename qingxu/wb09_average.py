"""09 敢于平凡（白板手绘版）：非要做到满分，才敢交？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事：J 一个比喻贯穿——跳高横杆。开局 PPT 改到第十二版还不敢发 → 横杆架在云上、写着「满分」，小周站在杆下
不跳，脚下长草（不交、不发、不开始）→ drop：横杆“哐”地掉到膝盖高，改写「一般就行」→
书中观点（亮书、第 14 章“敢于平凡”；给完美主义算账：好处一栏短、坏处一栏长）→ 按“一般”跨过去、先交 →
跳过之后杆子一点点升 → 身边的例子（写周报、做饭请朋友、健身第一天，底下连着同一根低杆）→
具体做法（给事情定时间、到点就交 / 交完记下“怕会怎样｜实际怎样”）→ 拉远看全板 → 评论区互动。
书中观点为转述（David D. Burns, Feeling Good: The New Mood Therapy，中译本《伯恩斯新情绪疗法》，李亚萍译，
第 14 章“敢于平凡——战胜完美主义的必杀技”）；跳高横杆是本系列的比喻，不是书中原比喻；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               doc, face, hands_at, join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#2E9A8C"
SQUARE_SHOT = 3                 # 场景 4：小周 + 横杆从云上掉到膝盖高「一般就行」

b = Board(size=(3600, 13800))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def J():
    return len(b.shots) - 1


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """小周：简笔小人 + 挂绳工牌。(x, y) 为脚底。"""
    hy = y - 290 * s
    badge = join(P((x - 14 * s, hy + 48 * s), (x + 20 * s, hy + 104 * s), (x + 40 * s, hy + 48 * s)),
                 rect(x + 20 * s, hy + 124 * s, 34 * s, 40 * s, 5 * s))
    return join(stick(x, y, s, arms), badge)


def cloud(x, y, w, h, bumps=9) -> skia.Path:
    """一圈鼓包的云朵外轮廓（天上的云、念头云共用）。"""
    p = skia.Path()
    n = 180
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        r = 0.86 + 0.14 * abs(math.sin(a * bumps / 2))
        q = (x + w / 2 * r * math.cos(a), y + h / 2 * r * math.sin(a))
        p.moveTo(*q) if i == 0 else p.lineTo(*q)
    return p


def cloud_edge(x, y, w, h) -> skia.Path:
    """乌云的涂黑边：沿云轮廓来回的锯齿。"""
    p = skia.Path()
    n = 90
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        r = 0.86 + 0.14 * abs(math.sin(a * 9 / 2))
        r *= 1.0 if i % 2 == 0 else 1.1
        q = (x + w / 2 * r * math.cos(a), y + h / 2 * r * math.sin(a))
        p.moveTo(*q) if i == 0 else p.lineTo(*q)
    return p


def puffs(x, y, n=3, gap=34, r=12) -> skia.Path:
    """念头云底下一串小圆点，连到头顶。"""
    return join(*[circle(x + i * gap * 0.4, y + i * gap, r - i * 3) for i in range(n)])


def posts(x0, x1, ground, top) -> skia.Path:
    """跳高架：两根立柱 + 底座。"""
    parts = []
    for x in (x0, x1):
        parts += [P((x, ground), (x, top)), P((x - 40, ground), (x + 40, ground))]
    return join(*parts)


def grass(x, y, w=260) -> skia.Path:
    """脚边几簇草。"""
    parts = []
    for i in range(6):
        gx = x - w / 2 + i * w / 5
        parts.append(P((gx - 18, y), (gx - 8, y - 46), (gx, y), (gx + 10, y - 58), (gx + 18, y)))
    return parts and join(*parts)


def strider(x, y, s=1.0) -> skia.Path:
    """跨步的小周：后脚踩地，前腿抬起跨过低杆，前手往前递文件。(x, y) 为后脚所在地面高度、身体中线。"""
    hy = y - 290 * s
    hip = (x, y - 120 * s)
    sh = (x, hy + 80 * s)
    badge = join(P((x - 14 * s, hy + 48 * s), (x + 20 * s, hy + 104 * s), (x + 40 * s, hy + 48 * s)),
                 rect(x + 20 * s, hy + 124 * s, 34 * s, 40 * s, 5 * s))
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), hip),
                P((x - 90 * s, y), (x - 40 * s, y - 60 * s), hip),
                P(hip, (x + 80 * s, y - 150 * s), (x + 150 * s, y - 120 * s)),
                P((x - 80 * s, hy + 160 * s), sh, (x + 110 * s, hy + 70 * s)), badge)


def tray(x, y, w=240, h=100) -> skia.Path:
    """收件筐：梯形筐身 + 一道筐沿。"""
    return join(P((x - w / 2, y - h / 2), (x - w / 2 + 30, y + h / 2), (x + w / 2 - 30, y + h / 2), (x + w / 2, y - h / 2)),
                P((x - w / 2 - 14, y - h / 2), (x + w / 2 + 14, y - h / 2)))


def pot(x, y, s=1.0) -> skia.Path:
    """锅：(x, y) 为锅身中心，带盖、两只把手、热气。"""
    body = skia.Path()
    body.addArc(skia.Rect.MakeXYWH(x - 150 * s, y - 110 * s, 300 * s, 220 * s), 0, 180)
    parts = [body, P((x - 150 * s, y), (x + 150 * s, y)),
             P((x - 150 * s, y + 10 * s), (x - 200 * s, y - 10 * s)), P((x + 150 * s, y + 10 * s), (x + 200 * s, y - 10 * s))]
    lid = skia.Path()
    lid.addArc(skia.Rect.MakeXYWH(x - 140 * s, y - 60 * s, 280 * s, 110 * s), 180, 180)
    parts += [lid, rect(x, y - 68 * s, 40 * s, 18 * s, 6 * s)]
    for dx in (-60, 0, 60):
        st = skia.Path()
        st.moveTo(x + dx * s, y - 95 * s)
        st.quadTo(x + (dx - 20) * s, y - 125 * s, x + dx * s, y - 155 * s)
        st.quadTo(x + (dx + 20) * s, y - 185 * s, x + dx * s, y - 215 * s)
        parts.append(st)
    return join(*parts)


def track(x, y, w=600, h=300) -> skia.Path:
    """操场跑道：外圈 + 内圈 + 一道起跑线。"""
    return join(rect(x, y, w, h, h / 2), rect(x, y, w - 180, h - 160, (h - 160) / 2),
                P((x, y + h / 2), (x, y + (h - 160) / 2)))


def bells(x, y, r) -> skia.Path:
    """闹钟的两只铃 + 两条腿。(x, y, r) 同 clock()。"""
    parts = []
    for sx in (-1, 1):
        a = skia.Path()
        cx, cy = x + sx * r * 0.62, y - r * 0.9
        a.addArc(skia.Rect.MakeXYWH(cx - r * 0.32, cy - r * 0.32, r * 0.64, r * 0.64), 180, 180)
        a.moveTo(cx - r * 0.32, cy)
        a.lineTo(cx + r * 0.32, cy)
        parts += [a, P((x + sx * r * 0.6, y + r * 0.8), (x + sx * r * 0.85, y + r * 1.12))]
    return join(*parts)


def hops(xs, hs, ground) -> skia.Path:
    """一串跳跃弧线：每根杆子跳一次，弧顶比杆高一截。"""
    p = skia.Path()
    for x, h in zip(xs, hs):
        p.moveTo(x - 100, ground - 6)
        p.quadTo(x, ground - h * 2 - 150, x + 100, ground - 6)
    return p


# ---------------------------------------------------------------- 开局：改到第十二版（场景 1）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("改了十二版，还不敢发", "灵魂拷问", (1800, 800, 0.85), bars=2)
L(join(rect(1800, 720, 1000, 620, 30), P((1300, 500), (2300, 500)), circle(1350, 455, 12), circle(1390, 455, 12)),
  0, 0.9, sfx="wood_high")
for n, name in enumerate(("方案 终版", "方案 终终版", "方案 真终版")):
    y = 600 + n * 130
    L(doc(1420, y, 70, 90, 2), 1 + n, 1.3 + n, BLACK, 7, sfx="pop")
    T(name, 1720, y + 18, 58, RED if n == 2 else BLACK, k0=1.3 + n, k1=1.95 + n)
L(rect(2120, 950, 220, 90, 20), 4, 4.5, BLUE, 8, sfx="wood_high")
T("发送", 2120, 968, 52, BLUE, k0=4.5, k1=5.0)
T("第 12 版", 1800, 1210, 84, RED, k0=5, k1=6.0, sfx="rim")

# ---------------------------------------------------------------- 比喻：跳高横杆（场景 2–4）

VJ = (1800, 2300, 0.78)
GROUND = 2780
PX0, PX1 = 1800, 2400            # 跳高架两根立柱
BAR_HI, BAR_LO = 1990, 2700      # 横杆：云上 / 膝盖高
ZX = 1400                        # 小周站的位置
ZS = 0.8
ZHY = GROUND - 290 * ZS          # 小周头部中心
FALL = 0.24                      # 横杆下落秒数（在 drop 那一拍落地）

scene("杆架在云上", "比喻 · 跳高横杆", VJ)
L(join(P((1150, GROUND), (2470, GROUND)), posts(PX0, PX1, GROUND, 1950)), 0, 0.9, BLACK, 10, sfx="wood_low")
J_BAR = J()


def bar_fn(c, k, t):
    """横杆：场景 2 先画出来（k），场景 4 第 0 拍从云上砸到膝盖高，落地后弹两下。"""
    y = BAR_HI
    streak = 0.0
    if b.ep is not None:
        td = b.t_of(J_DROP, 0)
        if t >= td:
            dt = t - td
            y = BAR_LO - 26 * math.exp(-dt * 10) * abs(math.sin(dt * 22))
        elif t > td - FALL:
            f = (t - (td - FALL)) / FALL
            y = BAR_HI + (BAR_LO - BAR_HI) * f * f
            streak = f
    x0 = PX0 - 30
    x1 = x0 + (PX1 + 30 - x0) * k
    if streak > 0:
        for dx in (0.15, 0.5, 0.85):
            xx = PX0 + (PX1 - PX0) * dx
            c.drawLine(xx, y - 40 - 260 * streak, xx, y - 40, K.paint(BLACK, 0.35, 5))
    c.drawLine(x0, y, x1, y, wb.marker(RED, 16))
    c.drawLine(x0, y, x1, y, K.paint(RED, 0.22, 7, blur=1.2))
    return (x1, y) if k < 1 else None


b.custom(J(), 1, 1.9, bar_fn, sfx="wood_high")
L(cloud(2100, 1950, 760, 230), 2, 2.9, BLUE, 8, sfx="pop")
T("满分", 2100, 1915, 66, RED, k0=3, k1=3.8, sfx="pop")
L(zhou(ZX, GROUND, ZS), 4, 4.9, BLACK, 10, sfx="wood_high")
L(face(ZX, GROUND, ZS, "flat"), 4.9, 5.2)
L(arrow((1620, GROUND - 40), (1620, 2060), 0.0, 40), 6, 6.8, BLUE, 7, sfx="pop")
L(arrow((1620, 2060), (1620, GROUND - 40), 0.0, 40), 6.8, 7.4, BLUE, 7)

scene("够不着，就干脆不跳", "比喻 · 站着不跳", VJ)
L(grass(ZX, GROUND), 0, 0.9, GREEN, 7, sfx="wood_high")
L(cloud(ZX, 2290, 440, 170), 1, 1.8, BLACK, 8, sfx="pop")
L(cloud_edge(ZX, 2290, 440, 170), 2, 2.8, BLACK, 5, sfx="shaker")
L(puffs(ZX + 20, 2410, 2, 40, 13), 2.8, 3.0, BLACK, 6)
T("不满分=零分", ZX, 2306, 50, RED, k0=3, k1=4.5, sfx="pop")
LABELS = [("不交", 2370), ("不发", 2490), ("不开始", 2610)]
for n, (s, y) in enumerate(LABELS):
    T(s, 2100, y, 60, k0=5 + n, k1=5.8 + n, sfx="pop")

scene("先把杆降下来", "比喻 · 降杆", VJ, shake=[0], flashes=[0])
J_DROP = J()
H(0, "kick", 0.9, "横杆砸到膝盖高")
L(join(P((PX0 + 20, GROUND - 10), (PX0 + 70, GROUND - 40)), P((PX1 - 20, GROUND - 10), (PX1 - 70, GROUND - 40)),
       P((PX0 + 30, GROUND + 25), (PX0 + 90, GROUND + 25)), P((PX1 - 30, GROUND + 25), (PX1 - 90, GROUND + 25))),
  0.3, 0.8, BLACK, 6)
b.erase(J(), 1, 1.8, 2100, 2490, 520, 360)
H(1, "shaker", 0.7, "擦掉不交不发不开始")
T("一般就行", 2100, 2630, 66, BLUE, k0=2, k1=3.0, sfx="pop")
L(cross(2100, 1905, 58), 3, 3.6, RED, 11, sfx="rim")
b.erase(J(), 4, 4.5, ZX, ZHY, 100, 100)
H(4, "ding", 0.8, "小周笑了")
L(join(circle(ZX, ZHY, 45 * ZS), P((ZX, ZHY + 36), (ZX, ZHY + 56))), 4.5, 5.1, BLACK, 10)
L(face(ZX, GROUND, ZS, "smile"), 5.1, 5.5, BLACK, 9)

# ---------------------------------------------------------------- 书中观点（场景 5–6）

scene("书里叫敢于平凡", "伯恩斯新情绪疗法 · 第十四章", (1800, 3650, 0.85))
L(book(1400, 3620, 460, 320), 0, 0.9, BLACK, 10, sfx="wood_low")
T("伯恩斯新情绪疗法", 1400, 3360, 58, GREEN, k0=1, k1=3.0, sfx="pop")
T("第 14 章", 2200, 3420, 60, k0=3, k1=4.0, sfx="pop")
T("敢于平凡", 2200, 3620, 110, RED, k0=4, k1=5.0, sfx="ding")
L(underline(1990, 2410, 3700), 5, 5.8, RED, 9, sfx="wood_high")
L(join(posts(2060, 2340, 3960, 3830), P((2030, 3900), (2370, 3900))), 6, 6.9, BLACK, 8, sfx="pop")
T("杆放低", 2200, 4020, 50, BLUE, k0=7, k1=7.8)

VL = (1800, 4900, 0.85)
scene("给完美主义算笔账", "书中做法 · 算账", VL)
L(join(P((1250, 4560), (2350, 4560)), P((1800, 4440), (1800, 5300))), 0, 0.9, BLACK, 9, sfx="wood_high")
T("好处", 1525, 4500, 66, GREEN, k0=1, k1=1.8, sfx="pop")
T("坏处", 2075, 4500, 66, RED, k0=2, k1=2.8, sfx="pop")
T("做得细", 1525, 4690, 58, k0=3, k1=3.8, sfx="pop")
for n, s in enumerate(("累", "慢", "怕错", "不敢开始")):
    T(s, 2075, 4690 + n * 145, 58, k0=4 + n, k1=4.8 + n if n < 3 else 8.0, sfx="wood_high" if n == 0 else "pop")

# ---------------------------------------------------------------- 跨过去（场景 7–8）

G7 = 6650
scene("按一般做，先跨过去", "比喻 · 先跨过去", (1800, 6200, 0.85))
L(join(P((1250, G7), (2400, G7)), posts(1690, 1990, G7, G7 - 90), P((1670, G7 - 70), (2010, G7 - 70))), 0, 0.9,
  BLACK, 9, sfx="wood_low")
L(strider(1650, G7, 0.9), 1, 1.9, BLACK, 10, sfx="wood_high")
L(face(1650, G7, 0.9, "smile"), 1.9, 2.0)
L(doc(1800, 6440, 90, 110, 3), 2, 2.8, BLACK, 7, sfx="pop")
L(arrow((1870, 6400), (2140, 6430), -0.2, 36), 3, 3.8, GREEN, 8, sfx="wood_high")
L(tray(2250, 6500), 4, 4.8, BLACK, 9, sfx="pop")
T("已交", 2250, 6380, 62, GREEN, k0=5, k1=5.8, sfx="ding")
L(cloud(1400, 6020, 460, 170), 6, 6.8, BLUE, 8, sfx="pop")
L(puffs(1480, 6140, 3, 38, 13), 6.8, 7.0, BLUE, 6)
T("先交一版", 1400, 6038, 56, BLUE, k0=7, k1=8.0, sfx="pop")

G8 = 7900
XS8, HS8 = (1210, 1440, 1670, 1900, 2130), (80, 170, 280, 410, 560)
scene("跳着跳着，杆就高了", "比喻 · 一点点往上", (1800, 7500, 0.85))
L(P((1080, G8), (2440, G8)), 0, 0.3, BLACK, 8, sfx="wood_high")
for n, (x, h) in enumerate(zip(XS8, HS8)):
    k = 0.3 if n == 0 else n
    L(join(posts(x - 70, x + 70, G8, G8 - h - 20), P((x - 85, G8 - h), (x + 85, G8 - h))), k, n + 0.9,
      RED if n == 0 else BLACK, 8, sfx=None if n == 0 else ("pop" if n % 2 else "wood_high"))
L(hops(XS8, HS8, G8), 5, 5.9, BLUE, 6, sfx="shaker")
T("一点点往上", 1650, 7200, 66, BLUE, k0=6, k1=7.25, sfx="pop")
L(zhou(2330, G8, 0.55, "up"), 7.3, 8.0, BLACK, 9)

# ---------------------------------------------------------------- 身边的例子（场景 9–11）：底下连着同一根低杆

RY = 8900                       # 这一排的视图中心
BY = 9300                       # 同一根低杆的高度
scene("周报，半小时就交", "例子 · 写周报", (700, RY, 0.85))
L(doc(600, 8800, 300, 380, 5), 0, 0.9, BLACK, 9, sfx="wood_high")
T("周报", 600, 8560, 64, k0=1, k1=1.8, sfx="pop")
L(clock(980, 8700, 120), 2, 2.9, BLACK, 9, sfx="wood_high")
L(hands_at(980, 8700, 120, 12, 30), 3, 3.5, RED, 9, sfx="pop")
T("半小时", 980, 8900, 56, RED, k0=3.5, k1=4.3)
L(join(P((300, BY + 100), (300, BY - 20)), P((260, BY + 100), (340, BY + 100)), P((280, BY), (1300, BY))), 5, 5.9,
  RED, 10, sfx="wood_low")
T("一般就行", 760, BY - 70, 60, BLUE, k0=6, k1=7.0, sfx="pop")
L(check(600, 8830, 80), 7, 7.7, GREEN, 12, sfx="ding")

scene("家常菜，朋友吃得香", "例子 · 请朋友吃饭", (1800, RY, 0.85))
L(pot(1600, 8880), 0, 0.9, BLACK, 9, sfx="wood_high")
T("家常菜", 1600, 8590, 64, k0=1, k1=1.8, sfx="pop")
L(stick(2080, 9200, 0.6, "down"), 2, 2.8, BLACK, 9, sfx="pop")
L(face(2080, 9200, 0.6, "smile"), 2.8, 3.0)
L(bubble(2080, 8790, 300, 120, -1), 3, 3.6, BLACK, 8, sfx="pop")
T("好吃！", 2080, 8806, 54, k0=3.6, k1=4.4)
L(join(P((1300, BY), (2400, BY)), P((1800, BY + 100), (1800, BY)), P((1760, BY + 100), (1840, BY + 100))), 5, 5.9,
  RED, 10, sfx="wood_low")
T("满汉全席", 2080, 8560, 52, k0=6, k1=7.0, sfx="pop")
L(P((1960, 8545), (2200, 8545)), 7, 7.6, RED, 10, sfx="rim")

scene("健身第一天，慢跑就行", "例子 · 健身第一天", (2900, RY, 0.85))
L(track(3000, 8800, 600, 300), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(2600, 9150, 0.6, "point"), 1, 1.8, BLACK, 9, sfx="pop")
L(face(2600, 9150, 0.6, "smile"), 1.8, 2.0)
T("慢跑", 3000, 8818, 60, GREEN, k0=2, k1=2.8, sfx="pop")
T("跑满", 3000, 8570, 56, k0=3, k1=3.8, sfx="pop")
L(P((2930, 8555), (3070, 8555)), 4, 4.6, RED, 10, sfx="rim")
L(join(P((2400, BY), (3300, BY)), P((3300, BY + 100), (3300, BY - 20)), P((3260, BY + 100), (3340, BY + 100))), 5, 5.9,
  RED, 10, sfx="wood_low")
T("同一根低杆", 2880, BY - 70, 56, BLUE, k0=6, k1=7.25, sfx="pop")
L(arrow((3200, BY + 60), (2500, BY + 60), 0.0, 34), 7.3, 8.0, BLUE, 7)

# ---------------------------------------------------------------- 具体做法（场景 12–13）

scene("定个时间，到点就交", "做法一 · 到点就交", (1800, 10450, 0.85))
T("① 定个时间", 1800, 10030, 76, BLUE, k0=0, k1=1.5, sfx="pop")
L(clock(1450, 10450, 190), 2, 2.9, BLACK, 10, sfx="wood_high")
L(hands_at(1450, 10450, 190, 6, 0), 3, 3.6, RED, 10, sfx="pop")
L(bells(1450, 10450, 190), 4, 4.8, BLACK, 9, sfx="tom")
T("到点就停", 2150, 10340, 76, RED, k0=5, k1=6.0, sfx="ding")
L(arrow((2150, 10420), (2150, 10620), 0.0, 36), 6, 6.8, BLACK, 8, sfx="wood_high")
L(tray(2150, 10720), 7, 7.8, BLACK, 9, sfx="pop")

scene("交完，记下实际怎样", "做法二 · 记下实际", (1800, 11700, 0.85))
L(join(rect(1800, 11760, 1100, 760, 30), P((1800, 11380), (1800, 12140)), P((1250, 11520), (2350, 11520))), 0, 0.9,
  BLACK, 9, sfx="wood_low")
T("怕会怎样", 1525, 11470, 60, RED, k0=1, k1=2.0, sfx="pop")
T("实际怎样", 2075, 11470, 60, GREEN, k0=2, k1=3.0, sfx="pop")
T("被说太粗", 1525, 11650, 56, k0=3, k1=4.0, sfx="pop")
T("要重做", 1525, 11800, 56, k0=4, k1=4.8, sfx="pop")
T("回了句：好", 2075, 11650, 56, k0=5, k1=6.25, sfx="pop")
T("下午很轻松", 2075, 11800, 56, k0=6.25, k1=7.5)
T("比想的好", 1800, 12020, 70, BLUE, k0=7, k1=8.0, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 6900, 0.072)
VC = (1800, 13000, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
b.move(J(), 4, VC, dur=1.1)
T("你改过最多版的东西是什么？", 1800, 12820, 66, RED, k0=5, sfx="pop")
T("下一讲：别人一不满意，你就慌？", 1800, 12990, 50, k0=9, sfx="wood_high")
L(cloud(2200, 13330, 500, 170), 13, 13.8, BLUE, 8, sfx="pop")
T("今天换掉一朵乌云", 2200, 13346, 46, BLUE, k0=13.8, k1=15.8)
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "average", "敢于平凡", "非要做到满分，才敢交？", ACC, b.shots,
                 [f"{BOOK}第 14 章“敢于平凡——战胜完美主义的必杀技”（转述）",
                  "中译本：中国城市出版社 2011（豆瓣 https://book.douban.com/subject/5980113/）"],
                 "非要做到满分|才敢【交】", SQUARE_SHOT,
                 ["书中观点均为转述：完美主义让人更累、更怕出错，也更难把事做好；可以把完美主义的好处和坏处写下来对比；"
                  "试着按“一般”的标准做一件事，再看看结果和心情；关注过程，给事情定时间上限。见第 14 章“敢于平凡——"
                  "战胜完美主义的必杀技”。出处：David D. Burns, Feeling Good: The New Mood Therapy，中译本《伯恩斯新情绪疗法》"
                  "（李亚萍译，中国城市出版社 2011）。上屏均为转述，不是逐字引文。",
                  "跳高横杆（杆架在云上、降到膝盖高、跳着跳着慢慢升高）是本系列用来讲书中观点的比喻，不是书中原比喻。",
                  "“第 12 版”“半小时”为示意；改 PPT、写周报、做饭请朋友、健身第一天均为现实场景示意，不指向任何具体公司或个人；"
                  "“好处｜坏处”两栏、“怕会怎样｜实际怎样”两栏里的内容为示意。",
                  "两步做法（给一件事定时间、到点就交；交完记下怕会怎样和实际怎样）为据第 14 章思路整理的建议。",
                  "本片为读书分享，不能替代诊断和治疗；情绪持续低落或有轻生念头，请尽快联系医生、心理咨询师或当地心理援助热线。"],
                 tags="#完美主义")
    return b.attach(ep)
