"""01 经历定金钱观（白板手绘版）：爸妈抠门我乱花，谁疯了？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（F 两人对比）：家里饭桌开局——妈妈叠塑料袋、小王拿着奶茶，一道闪电；妈妈说“一杯奶茶 = 两斤肉”，
小王说“钱是赚来花的”，小猪罐夹在中间冒汗 → drop：桌子底下裂开，长出两条成长时间线（左：票证 / 下岗 / 存折；
右：外卖 / 网购 / 分期账单）→ 亮书《金钱心理学》；书中观点：人对钱的看法来自亲身经历，经历过的比读到的管用；
书中提到的研究：年轻时碰上的年景，影响一辈子的胆子大小；在各自的处境里，决定都讲得通（两条时间线各打一个绿勾）→
例子（爸妈囤货连到“缺过”、同事月月花光连到“看过裁员”）→ 做法（先问一句他那会儿缺过什么 / 再把自己怕什么说具体 /
小猪罐分两格：安心钱、开心钱）→ 拉远看全板 → 评论区互动。
书中观点为转述：Morgan Housel, The Psychology of Money (Harriman House, 2020)；中译本《金钱心理学》
（摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023）第 1 章“没有人真的对钱失去理智”。
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, desk, face,
                               join, rect, stick)
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#2E8B57"
SQUARE_SHOT = 3                 # 场景 4：饭桌裂开，两条时间线 + 妈妈和小王

b = Board(size=(4800, 6000))

CX = 2200                       # 饭桌中线
LX, RX = 1650, 2750             # 妈妈 / 小王 的时间线
MOM, WANG = (1450, 1250), (2950, 1250)   # 饭桌两边的小人（脚底）
TICKS = (1580, 1800, 2020)      # 时间线上的三个节点


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法（小猪罐为系列角色，各讲可复制）

def oval(x, y, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    return p


def pig(x, y, s=1.0, mood="smile") -> skia.Path:
    """小猪存钱罐（正面）：(x, y) 为身子中心。mood：smile / sad / sweat / shock，只改嘴和汗滴。"""
    parts = [oval(x, y, 130 * s, 95 * s),
             P((x - 25 * s, y - 72 * s), (x + 25 * s, y - 72 * s)),                         # 投币口
             P((x - 95 * s, y - 62 * s), (x - 85 * s, y - 120 * s), (x - 45 * s, y - 88 * s)),  # 耳朵
             P((x + 95 * s, y - 62 * s), (x + 85 * s, y - 120 * s), (x + 45 * s, y - 88 * s)),
             circle(x - 40 * s, y - 25 * s, 5 * s), circle(x + 40 * s, y - 25 * s, 5 * s),
             oval(x, y + 12 * s, 36 * s, 24 * s), circle(x - 12 * s, y + 12 * s, 4 * s), circle(x + 12 * s, y + 12 * s, 4 * s)]
    for dx in (-75, -30, 30, 75):
        parts.append(P((x + dx * s, y + 88 * s), (x + dx * s, y + 118 * s)))
    tail = skia.Path()
    tail.moveTo(x + 128 * s, y)
    tail.quadTo(x + 165 * s, y - 25 * s, x + 150 * s, y + 5 * s)
    tail.quadTo(x + 140 * s, y + 25 * s, x + 170 * s, y + 15 * s)
    parts.append(tail)
    m = skia.Path()
    if mood == "shock":
        m.addCircle(x, y + 55 * s, 9 * s)
    elif mood in ("sad", "sweat"):
        m.addArc(skia.Rect.MakeXYWH(x - 20 * s, y + 46 * s, 40 * s, 24 * s), 200, 140)
    else:
        m.addArc(skia.Rect.MakeXYWH(x - 22 * s, y + 36 * s, 44 * s, 26 * s), 20, 140)
    parts.append(m)
    if mood == "sweat":
        d = skia.Path()
        d.moveTo(x + 108 * s, y - 95 * s)
        d.quadTo(x + 130 * s, y - 60 * s, x + 108 * s, y - 52 * s)
        d.quadTo(x + 86 * s, y - 60 * s, x + 108 * s, y - 95 * s)
        parts.append(d)
    return join(*parts)


def pig_item(k0, k1, x, y, s=1.0, mood="smile", color=BLACK, width=9, sfx=None, wobble=None, grow=None):
    """小猪罐做成动态项：k0–k1 描出来；wobble=(起拍, 止拍) 左右摇摆（为难）；grow=拍 胖一圈。"""
    j = J()
    path = pig(x, y, s, mood)
    fy = y + 118 * s                            # 以脚底为轴

    def fn(c, k, t):
        ang, f = 0.0, 1.0
        if wobble:
            w0, w1 = b.t_of(j, wobble[0]), b.t_of(j, wobble[1])
            if w0 <= t < w1:
                ang = 8 * math.sin((t - w0) * 13) * (1 - (t - w0) / (w1 - w0))
        if grow is not None:
            f = 1 + 0.14 * ease_out(clamp01((t - b.t_of(j, grow)) / 0.35))
        c.save()
        c.translate(x, fy)
        c.rotate(ang)
        c.scale(f, f)
        c.translate(-x, -fy)
        part, tip = wb.partial(path, k)
        c.drawPath(part, wb.marker(color, width))
        c.drawPath(part, wb.K.paint(color, 0.22, width * 0.45, blur=1.2))
        c.restore()
        return tip if k < 1 else None

    b.custom(j, k0, k1, fn, sfx=sfx)


def bags(x, y, s=1.0) -> skia.Path:
    """叠成三角的塑料袋，一小摞。"""
    parts = []
    for dx, dy in ((-40, 20), (40, 20), (0, -40)):
        cx, cy = x + dx * s, y + dy * s
        parts += [P((cx - 42 * s, cy + 32 * s), (cx + 42 * s, cy + 32 * s), (cx, cy - 40 * s), close=True),
                  P((cx - 18 * s, cy + 32 * s), (cx, cy - 4 * s))]
    return join(*parts)


def milktea(x, y, s=1.0) -> skia.Path:
    """奶茶杯：杯身 + 杯盖 + 吸管 + 珍珠。(x, y) 为杯身中心。"""
    cup = P((x - 40 * s, y - 70 * s), (x - 30 * s, y + 70 * s), (x + 30 * s, y + 70 * s), (x + 40 * s, y - 70 * s))
    lid = skia.Path()
    lid.moveTo(x - 46 * s, y - 70 * s)
    lid.quadTo(x, y - 110 * s, x + 46 * s, y - 70 * s)
    lid.close()
    pearls = [circle(x + dx * s, y + 48 * s, 7 * s) for dx in (-14, 4, 18)]
    return join(cup, lid, P((x + 8 * s, y - 90 * s), (x + 30 * s, y - 165 * s)), *pearls)


def bolt(x, y, s=1.0) -> skia.Path:
    return P((x + 25 * s, y - 80 * s), (x - 30 * s, y + 5 * s), (x + 12 * s, y + 5 * s), (x - 22 * s, y + 80 * s))


def crack(x, y0, y1) -> skia.Path:
    pts, n = [], 7
    for i in range(n + 1):
        pts.append((x + (0 if i in (0, n) else (28 if i % 2 else -28)), y0 + (y1 - y0) * i / n))
    return join(P(*pts), P((x, y1), (LX, y1 + 70)), P((x, y1), (RX, y1 + 70)))


def timeline(x, y0, y1) -> skia.Path:
    parts = [arrow((x, y0), (x, y1), 0.0, 40)]
    for ty in TICKS:
        parts.append(circle(x, ty, 14))
    return join(*parts)


def table() -> skia.Path:
    return join(P((CX - 550, 1050), (CX + 550, 1050)), P((CX - 500, 1050), (CX - 500, 1160)),
                P((CX + 500, 1050), (CX + 500, 1160)))


def head(x, y, r=230) -> skia.Path:
    return join(circle(x, y, r), P((x - 70, y + r - 12), (x - 70, y + r + 50)), P((x + 70, y + r - 12), (x + 70, y + r + 50)))


def photo(x, y, w=120, h=95) -> skia.Path:
    return join(rect(x, y, w, h, 6), P((x - w / 2 + 12, y + h / 2 - 15), (x - 12, y - 8), (x + 8, y + 10),
                                       (x + 22, y - 2), (x + w / 2 - 12, y + h / 2 - 15)))


def sun(x, y, r=60) -> skia.Path:
    parts = [circle(x, y, r)]
    for i in range(8):
        a = i / 8 * 2 * math.pi
        parts.append(P((x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3), (x + math.cos(a) * r * 1.75, y + math.sin(a) * r * 1.75)))
    return join(*parts)


def cloud(x, y) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 110, y + 30)
    p.quadTo(x - 130, y - 30, x - 60, y - 30)
    p.quadTo(x - 30, y - 90, x + 30, y - 50)
    p.quadTo(x + 110, y - 70, x + 110, y + 30)
    p.close()
    rain = [P((x + dx, y + 55), (x + dx - 15, y + 100)) for dx in (-60, 0, 60)]
    return join(p, *rain)


def cabinet(x, y, w=420, h=560) -> skia.Path:
    top = y - h / 2
    return join(rect(x, y, w, h, 8), P((x - w / 2, top + h / 3), (x + w / 2, top + h / 3)),
                P((x - w / 2, top + 2 * h / 3), (x + w / 2, top + 2 * h / 3)),
                P((x - 60, y + h / 2), (x - 60, y + h / 2 + 30)), P((x + 60, y + h / 2), (x + 60, y + h / 2 + 30)))


def rolls(x, y) -> skia.Path:
    """一排卷纸（端面）。"""
    return join(*[join(circle(x + dx, y, 42), circle(x + dx, y, 13)) for dx in (-150, -50, 50, 150)])


def ricebags(x, y) -> skia.Path:
    parts = []
    for dx in (-130, 0, 130):
        cx = x + dx
        parts += [P((cx - 40, y - 70), (cx - 55, y + 70), (cx + 55, y + 70), (cx + 40, y - 70), close=True),
                  P((cx - 40, y - 70), (cx - 25, y - 85), (cx + 25, y - 85), (cx + 40, y - 70))]
    return join(*parts)


def cartons(x, y) -> skia.Path:
    return join(*[join(rect(x + dx, y, 110, 120, 4), P((x + dx - 55, y - 25), (x + dx + 55, y - 25)))
                  for dx in (-130, 0, 130)])


def bowl(x, y, r=70) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r * 0.9, 2 * r, 1.8 * r), 0, 180)
    noodles = skia.Path()
    noodles.moveTo(x - r * 0.6, y - 6)
    for i in range(6):
        noodles.quadTo(x - r * 0.6 + (i + 0.5) * r * 0.2, y - 30 if i % 2 == 0 else y + 10, x - r * 0.6 + (i + 1) * r * 0.2, y - 6)
    return join(p, P((x - r - 10, y), (x + r + 10, y)), noodles, P((x + 20, y - 10), (x + 90, y - 110)),
                P((x + 40, y - 8), (x + 110, y - 100)))


def uline_back(x0, x1, y, amp=14, step=40) -> skia.Path:
    """波浪下划线，从右往左画（收笔在左端，停住时手不挡右边的字）。"""
    p = skia.Path()
    p.moveTo(x1, y)
    x, k = x1, 0
    while x > x0:
        p.quadTo(x - step / 2, y + (amp if k % 2 == 0 else -amp), x - step, y)
        x -= step
        k += 1
    return p


def nods(x, y) -> skia.Path:
    """点头的两道动作线：(x, y) 为头顶。"""
    out = skia.Path()
    for dx in (-70, 70):
        out.addArc(skia.Rect.MakeXYWH(x + dx - 20, y - 10, 40, 60), 200 if dx < 0 else -40, 120)
    return out


# ---------------------------------------------------------------- 开局：饭桌上吵起来（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

scene("饭桌上又吵起来了", "饭桌吵架", (CX, 1000, 0.55), bars=2)
L(table(), 0, 0.9, sfx="wood_high")
L(stick(*MOM, 0.85, "hold", hair=True), 1, 1.8, sfx="pop")
L(face(*MOM, 0.85, "flat"), 1.8, 2.0)
L(bags(MOM[0] + 150, 1050, 0.8), 2, 2.8, BLACK, 8, sfx="wood_low")
L(stick(*WANG, 0.85, "hold"), 3, 3.8, BLUE, 10, sfx="pop")
L(face(*WANG, 0.85, "flat"), 3.8, 4.0, BLUE, 9)
L(milktea(WANG[0] + 135, 1020, 0.8), 4, 4.8, BLUE, 8, sfx="wood_high")
L(bolt(CX, 540, 1.7), 5, 5.8, RED, 12, sfx="rim")

scene("妈说我乱花钱", "妈妈这边", (1550, 800, 0.85))
T("妈妈", MOM[0], 1320, 60, k0=0, sfx="pop")
L(bubble(1550, 640, 600, 170, -1), 1, 1.8, BLACK, 8, sfx="wood_high")
T("一杯奶茶 = 两斤肉", 1550, 640, 56, k0=2, sfx="pop")
L(oval(1550, 640, 340, 120), 5, 5.9, RED, 8, sfx="ding")
T("乱花钱！", 1070, 880, 72, RED, k0=6, k1=7, sfx="rim")

scene("我说她太抠", "小王这边", (2600, 800, 0.85))
T("小王", WANG[0], 1320, 60, BLUE, k0=0, sfx="pop")
L(bubble(2850, 640, 480, 160, 1), 1, 1.8, BLUE, 8, sfx="wood_high")
T("钱是赚来花的", 2850, 640, 60, BLUE, k0=2, sfx="pop")
pig_item(4, 4.9, CX, 935, 0.95, "sweat", sfx="wood_high", wobble=(6, 8))
T("太抠了", 3075, 885, 64, RED, k0=5, k1=5.8, sfx="pop")
L(join(arrow((CX - 150, 860), (CX - 230, 800), 0.0, 26), arrow((CX + 175, 860), (CX + 255, 800), 0.0, 26)), 6, 6.8,
  RED, 7, sfx="shaker")
T("左右为难", CX, 740, 56, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- drop：两个人，两段经历（场景 4）

VT = (CX, 1400, 0.55)
scene("两个人，两段经历", "两段经历", VT, shake=[0], flashes=[0])
L(crack(CX, 1070, 1380), 0, 0.9, RED, 11, sfx="kick")
L(join(timeline(LX, 1450, 2180), timeline(RX, 1450, 2180)), 1, 1.9, BLACK, 10, sfx="wood_high")


def _left(s):
    return LX - 50 - len(s) * 42


def _right(s):
    return RX + 50 + len(s) * 42


for n, (side, s) in enumerate((("L", "票证"), ("R", "外卖"), ("L", "下岗"), ("R", "网购"), ("L", "存折"), ("R", "分期账单"))):
    x = _left(s) if side == "L" else _right(s)
    T(s, x, TICKS[n // 2], 84, BLACK if side == "L" else BLUE, k0=2 + n, k1=2.8 + n if n < 5 else 8, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 5–8）

scene("翻开《金钱心理学》", "金钱心理学 · 书中观点", (CX, 2850, 0.85))
L(book(2000, 2850, 440, 300), 0, 0.9, sfx="wood_low")
T("金钱心理学", 2000, 2620, 76, GREEN, k0=1, sfx="pop")
L(rect(2000, 3110, 420, 90, 20), 3, 3.6, BLACK, 7, sfx="pop")
T("摩根·豪泽尔", 2000, 3110, 56, k0=3.6, k1=5.1)
pig_item(5, 5.9, 2580, 2930, 0.8, "smile", sfx="wood_high")
L(rect(2000, 2860, 640, 680, 30), 6, 6.9, BLUE, 7, sfx="ding")

scene("经历过的，比读到的管用", "书中观点 · 第一章", (3800, 2850, 0.85))
L(head(3450, 2800), 0, 0.9, BLACK, 10, sfx="wood_high")
L(join(photo(3360, 2730), photo(3545, 2730), photo(3450, 2885, 140, 100)), 1, 1.9, BLACK, 7, sfx="pop")
T("经历过的", 3450, 3150, 72, GREEN, k0=2, k1=3, sfx="pop")
L(book(4150, 2800, 300, 200), 3, 3.8, BLACK, 8, sfx="wood_low")
T("读到的", 4150, 3150, 72, k0=4, k1=4.75, sfx="pop")
T(">", 3800, 2840, 170, RED, k0=5, k1=5.8, sfx="ding")
L(uline_back(3310, 3590, 3205), 6, 6.8, RED, 8, sfx="wood_high")

scene("年轻时的事，记一辈子", "书中提到的研究", (3800, 1750, 0.85))
L(sun(3450, 1590), 0, 0.9, ORANGE, 9, sfx="wood_high")
T("年景好", 3450, 1770, 56, k0=1, k1=1.8, sfx="pop")
L(join(arrow((3590, 1600), (3960, 1600), -0.1, 36), stick(4150, 1720, 0.6, "up")), 2, 2.9, GREEN, 9, sfx="wood_high")
T("胆子大", 4150, 1410, 60, GREEN, k0=3, k1=3.8, sfx="pop")
L(cloud(3450, 2010), 4, 4.9, BLUE, 9, sfx="wood_low")
T("年景差", 3450, 2200, 56, k0=5, k1=5.8, sfx="pop")
T("胆子小", 4150, 1890, 60, BLUE, k0=6, k1=6.8, sfx="pop")
L(join(arrow((3590, 2060), (3960, 2060), -0.1, 36), stick(4150, 2200, 0.6, "shrug")), 7, 7.9, BLUE, 9, sfx="wood_high")

scene("在他那儿，都讲得通", "书中观点 · 讲得通", VT)
L(check(LX + 160, 1610, 70), 0, 0.8, GREEN, 12, sfx="ding")
L(check(RX - 160, 1610, 70), 1, 1.8, GREEN, 12, sfx="ding")
T("在各自的处境里", CX, 1800, 76, k0=2, sfx="pop")
T("都讲得通", CX, 1990, 110, RED, k0=4, k1=5, sfx="pop")
L(uline_back(1970, 2430, 2070), 6, 6.8, GREEN, 9, sfx="wood_high")

# ---------------------------------------------------------------- 身边的例子（场景 9–10）

scene("爸妈囤货，因为缺过", "例子 · 爸妈", (950, 1750, 0.85))
L(cabinet(750, 1800), 0, 0.9, BLACK, 9, sfx="wood_high")
L(rolls(750, 1613), 1, 1.9, BLACK, 7, sfx="pop")
L(ricebags(750, 1810), 2, 2.9, BLACK, 7, sfx="pop")
L(cartons(750, 1990), 3, 3.8, BLACK, 7, sfx="wood_low")
T("缺过", 1180, 1450, 64, RED, k0=4, k1=4.8, sfx="pop")
L(arrow((1130, 1495), (985, 1585), 0.2, 30), 5, 5.8, RED, 8, sfx="wood_high")
T("囤着才安心", 750, 2190, 64, k0=6, k1=7.2, sfx="pop")
L(uline_back(590, 910, 2235), 7.2, 8.0, BLACK, 7)

scene("同事每月花光", "例子 · 同事", (950, 3020, 0.85))
L(desk(920, 3150, 440), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(600, 3330, 0.7), 1, 1.8, BLACK, 9, sfx="pop")
L(face(600, 3330, 0.7, "flat"), 1.8, 2.0)
L(bowl(800, 3130, 60), 2, 2.8, BLACK, 7, sfx="wood_low")
L(bubble(950, 2700, 480, 140, -1), 3, 3.6, BLACK, 8, sfx="pop")
T("明天的事明天说", 950, 2700, 52, k0=3.6)
T("看过裁员", 1300, 3450, 64, BLUE, k0=6, k1=7, sfx="pop")
L(arrow((1150, 3450), (720, 3390), 0.15, 32), 7, 7.8, BLUE, 8, sfx="wood_high")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

scene("先问他经历过什么", "做法一 · 先问", (950, 4300, 0.85))
T("① 先问一句", 950, 3830, 72, BLUE, k0=0, sfx="pop")
L(stick(600, 4400, 0.7, hair=True), 2, 2.8, BLACK, 9, sfx="wood_high")
L(face(600, 4400, 0.7, "flat"), 2.8, 3.0)
L(stick(1300, 4400, 0.7), 3, 3.8, BLUE, 9, sfx="pop")
L(face(1300, 4400, 0.7, "smile"), 3.8, 4.0, BLUE, 8)
L(bubble(1050, 4000, 560, 150, 1), 4, 4.6, BLUE, 8, sfx="wood_high")
T("你那会儿缺过什么？", 1050, 4000, 52, k0=4.6, k1=6.8)
T("？", 600, 3990, 180, RED, k0=7, k1=7.8, sfx="ding")

scene("再说自己怕什么", "做法二 · 说出担心", (CX, 4300, 0.85))
T("② 说出担心", CX, 3830, 72, BLUE, k0=0, sfx="pop")
L(stick(1900, 4400, 0.7), 1, 1.8, BLUE, 9, sfx="wood_high")
L(face(1900, 4400, 0.7, "flat"), 1.8, 2.0, BLUE, 8)
L(stick(2550, 4400, 0.7, hair=True), 2, 2.8, BLACK, 9, sfx="pop")
L(face(2550, 4400, 0.7, "flat"), 2.8, 3.0)
L(bubble(1950, 3995, 450, 140, -1), 3, 3.5, BLUE, 8, sfx="pop")
T("我怕活得太紧", 1950, 3995, 52, BLUE, k0=3.5, k1=5.0)
L(bubble(2480, 3995, 400, 140, 1), 5, 5.5, BLACK, 8, sfx="pop")
T("我怕又缺钱", 2480, 3995, 52, k0=5.5, k1=6.8)
T("怕的不一样", CX, 4500, 64, RED, k0=7, k1=7.6, sfx="ding")
L(uline_back(CX - 160, CX + 160, 4545), 7.6, 8.0, RED, 7)

scene("各存一份，各花一份", "做法三 · 分两格", (3800, 4300, 0.85))
T("③ 分两格", 3800, 3830, 72, BLUE, k0=0, sfx="pop")
pig_item(1, 2, 3800, 4200, 1.8, "smile", width=10, sfx="wood_high", grow=7)
L(join(P((3800, 4040), (3800, 4170)), P((3800, 4272), (3800, 4370))), 2, 2.6, BLACK, 8, sfx="wood_low")
T("安心钱", 3440, 4130, 60, GREEN, k0=3, k1=3.8, sfx="pop")
T("开心钱", 4220, 4060, 60, BLUE, k0=4, k1=4.8, sfx="pop")
L(join(stick(3350, 4600, 0.6, hair=True), face(3350, 4600, 0.6, "smile")), 5, 5.8, BLACK, 9, sfx="pop")
L(join(stick(4250, 4600, 0.6), face(4250, 4600, 0.6, "smile")), 6, 6.8, BLUE, 9, sfx="wood_high")
L(join(nods(3350, 4405), nods(4250, 4405)), 7, 7.8, GREEN, 7, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FULL = (2380, 2600, 0.21)
COMMENT = (CX, 5400, 0.85)
scene("评论区：你家谁管钱？", "评论区见", FULL, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(rect(CX, 5300, 900, 220, 40), 5, 5.8, RED, 8, sfx="pop")
T("你家谁管钱？", CX, 5300, 80, RED, k0=6, k1=7.5, sfx="pop")
pig_item(8, 8.8, 2900, 5320, 0.6, "smile", sfx="ding")
T("下一讲：一样努力，结果怎么差这么多？", CX, 5560, 50, k0=9, k1=13.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "story", "经历定金钱观", "爸妈抠门我乱花，谁疯了？", ACC, b.shots,
                 [f"{BOOK}第 1 章“没有人真的对钱失去理智”（转述）",
                  "Morgan Housel, The Psychology of Money (Harriman House, 2020)",
                  "中译本：李青宗译，民主与建设出版社 / 后浪 2023"],
                 "爸妈抠门我乱花|谁【疯了】？", SQUARE_SHOT,
                 ["书中观点（转述）：Morgan Housel, The Psychology of Money (Harriman House, 2020)；中译本《金钱心理学》"
                  "（摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023）第 1 章“没有人真的对钱失去理智”——"
                  "每个人对钱的看法由自己的亲身经历塑造，经历过的比读到的影响更深；在各自的处境里，看起来疯的决定也讲得通；"
                  "书中提到经济学家马尔门迪尔与纳格尔的研究：人年轻时经历的市场环境，会影响他一辈子的投资态度。"
                  "上屏均为转述，不是逐字引文；研究只画“年景好 / 年景差 → 胆子大 / 胆子小”的示意，不写数字。",
                  "饭桌吵架、“一杯奶茶 = 两斤肉”、“钱是赚来花的”、两条成长时间线（票证 / 下岗 / 存折；外卖 / 网购 / 分期账单）"
                  "为示意，不指向任何平台或公司；小王为示意人物。",
                  "爸妈囤货（缺过）、同事每月花光（看过裁员）均为现实场景示意。",
                  "三条做法（先问他那会儿缺过什么、把自己怕什么说具体、小猪罐分“安心钱 / 开心钱”两格）为据书中思路整理的建议，"
                  "不是投资建议。"],
                 tags="#金钱观 #代沟")
    return b.attach(ep)
