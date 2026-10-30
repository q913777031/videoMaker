"""10 少拖一点（白板手绘版）：拖延改不干净，那就少拖一点。系列最后一讲。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：最后 4 拍不出新笔画）。
叙事（A 经典）：打工人问题开局（收藏夹里一堆防拖延技巧，一个没用上 → 还是拖，开始烦自己，小周和顶天立地的明天怪兽对视）→
书中观点（亮书《拖延心理学》，博克和袁，这一季的小图标排成一行：圈、等式、两种时间、台阶；drop：怪兽“噗”地缩到手掌大，
小周把它揣进兜里——拖延很少一下根除，能变小；目标是少拖一点、知道自己在躲什么；拖了就骂自己只会拖更久，换成一杯热水）→
身边的例子（项目连轴转那周拖得最凶 / 消息群聊一直弹 / 谁找都说好，自己的事排最后）→
具体做法（找个人一起开工 / 额外的事先说“这周排不进” / 睡够、动一动）→
拉远看全板，绿箭头串起各块，再推回兜里，小怪兽探头 → 评论区：这季哪一讲最戳你，“这一季讲完了”。
书中观点为转述（Jane B. Burka & Lenora M. Yuen, Procrastination: Why You Do It, What to Do About It Now, 2008 修订版，
全书态度与第14、15、17章大意；中译本《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009）；
例子与做法为示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, bubble, book, check, circle, clock,
                               cross, desk, doc, face, hands_at, join, podium_list, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#3E8E7E"
SQUARE_SHOT = 3                 # 场景 4（drop）：怪兽缩进小周的兜里

b = Board(size=(3600, 9100))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def badge(x, y, s=1.0) -> skia.Path:
    """配合 stick 的工牌（挂绳 + 卡片）：(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 22 * s, hy + 45 * s), (x + 18 * s, hy + 130 * s), (x + 30 * s, hy + 45 * s)),
                rect(x + 18 * s, hy + 155 * s, 38 * s, 50 * s, 5 * s))


def zhou(x, y, s=0.75, arms="down", mood="flat") -> skia.Path:
    """小周：火柴人 + 胸前工牌。"""
    return join(stick(x, y, s, arms), face(x, y, s, mood), badge(x, y, s))


def monster(x, y, r, side=1, cal=True) -> skia.Path:
    """明天怪兽：毛茸茸的一团 + 两只圆眼 + 一只小手攥着日历页（side 为日历在哪一侧；“明天”二字另写）。"""
    pts = []
    n = 44
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = r * (1.12 if i % 2 else 1.0)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    parts = [P(*pts, close=True)]
    for dx in (-0.33, 0.33):
        parts += [circle(x + dx * r, y - 0.3 * r, 0.2 * r), circle(x + dx * r + 0.04 * r, y - 0.28 * r, 0.07 * r)]
    parts.append(P((x - side * 1.05 * r, y + 0.1 * r), (x - side * 1.35 * r, y - 0.2 * r)))
    if cal:
        parts += [P((x + side * 1.05 * r, y + 0.1 * r), (x + side * 1.3 * r, y - 0.05 * r)),
                  rect(x + side * 1.8 * r, y - 0.15 * r, 0.5 * r, 0.6 * r, 6),
                  P((x + side * 1.55 * r, y - 0.33 * r), (x + side * 2.05 * r, y - 0.33 * r))]
    return join(*parts)


def belly_text(c, x, y, r, k=1.0):
    """怪兽肚皮上的红字“明天”，k 为写出的比例。返回笔尖。"""
    size, ty = 0.48 * r, y + 0.4 * r
    w = K.text_w("明天", size, "hand")
    x0 = x - w / 2
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0 - 20, ty - size, x0 + w * k + 4, ty + size))
    K.text(c, "明天", x, ty, size, "hand", RED)
    c.restore()
    return x0 + w * k, ty


def pocket(x, y, w=120, h=100) -> skia.Path:
    """上沿敞口的口袋。"""
    return join(P((x - w / 2, y - h / 2), (x - w / 2, y + h / 2), (x + w / 2, y + h / 2), (x + w / 2, y - h / 2)),
                P((x - w / 2 - 8, y - h / 2), (x + w / 2 + 8, y - h / 2)))


def whip(x, y) -> skia.Path:
    """鞭子：(x, y) 为握把下端。"""
    p = skia.Path()
    p.moveTo(x + 66, y - 116)
    p.cubicTo(x + 160, y - 260, x + 280, y - 230, x + 300, y - 160)
    return join(P((x, y), (x + 66, y - 116)), P((x - 12, y - 8), (x + 12, y + 8)), p)


def cup(x, y) -> skia.Path:
    """一杯热水：杯身 + 把手 + 三缕热气。(x, y) 为杯身中心。"""
    h = skia.Path()
    h.addArc(skia.Rect.MakeXYWH(x + 50, y - 40, 70, 70), -90, 180)
    parts = [P((x - 75, y - 85), (x - 60, y + 85), (x + 60, y + 85), (x + 75, y - 85), close=True), h]
    for dx in (-35, 0, 35):
        s = skia.Path()
        s.moveTo(x + dx, y - 110)
        s.cubicTo(x + dx - 20, y - 140, x + dx + 20, y - 165, x + dx, y - 195)
        parts.append(s)
    return join(*parts)


def bed(x, y) -> skia.Path:
    """床：(x, y) 为床面中点。床头板 + 床垫 + 枕头 + 被子。"""
    return join(P((x - 230, y - 150), (x - 230, y + 90)), P((x - 230, y), (x + 230, y), (x + 230, y + 90)),
                rect(x - 160, y - 35, 110, 50, 20), P((x - 90, y - 15), (x - 60, y - 70), (x + 225, y - 70), (x + 230, y)))


def shoe(x, y) -> skia.Path:
    """跑鞋（侧视）：(x, y) 为鞋底中点。"""
    return join(P((x - 130, y), (x - 130, y - 70), (x - 70, y - 90), (x - 20, y - 60), (x + 60, y - 45),
                  (x + 130, y - 15), (x + 130, y), close=True),
                P((x - 135, y + 18), (x + 135, y + 18)), P((x - 50, y - 75), (x - 25, y - 55)), P((x - 30, y - 82), (x - 5, y - 62)))


def stairs(x, y, n=3, w=50, h=45) -> skia.Path:
    pts = [(x - n * w / 2, y + n * h / 2)]
    for i in range(n):
        cx, cy = pts[-1]
        pts += [(cx, cy - h), (cx + w, cy - h)]
    return P(*pts)


def loop_arrow(x, y, r=45) -> skia.Path:
    """转一圈的箭头（拖延的圈）。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -60, 300)
    ex, ey = x + r * math.cos(math.radians(240)), y + r * math.sin(math.radians(240))
    return join(p, P((ex - 28, ey - 6), (ex, ey), (ex + 6, ey - 30)))


def eq_sign(x, y, w=70) -> skia.Path:
    return join(P((x - w / 2, y - 16), (x + w / 2, y - 16)), P((x - w / 2, y + 16), (x + w / 2, y + 16)))


def shake_lines(x, y, side=1) -> skia.Path:
    """手机震动的两道弧线。"""
    return join(P((x, y - 60), (x + side * 22, y), (x, y + 60)), P((x + side * 34, y - 85), (x + side * 60, y), (x + side * 34, y + 85)))


def dot_fn(x, y, r, color=RED):
    """实心红点长出来（消息提醒）。"""

    def fn(c, k, t):
        K.dot(c, x, y, r * ease_out(k), color, 1.0)
        return None

    return fn


def knob_fn(x0, x1, y, r=34):
    """滑块从“全拖”滑到“少拖”，停在半路。"""

    def fn(c, k, t):
        x = lerp(x0, x1, ease_in_out(k))
        K.dot(c, x, y, r, BLUE, 1.0)
        c.drawCircle(x, y, r, wb.marker(BLACK, 7))
        return None

    return fn


def note_fn(x, y, w, h):
    """黄便利贴底色。"""

    def fn(c, k, t):
        K.rr(c, x, y, w, h, 8, "#FFE27A", 0.9 * k)
        return None

    return fn


def puff_fn(x, y, r):
    """“噗”：几圈烟从怪兽原来的位置散开、淡掉。"""

    def fn(c, k, t):
        if k >= 1:
            return None
        for i in range(6):
            a = math.radians(i * 60 + 15)
            d = r * (0.3 + 0.9 * ease_out(k))
            c.drawCircle(x + d * math.cos(a), y + d * math.sin(a), r * 0.22 * (1 - 0.5 * k),
                         K.paint("#9AA3AE", 0.55 * (1 - k), 8))
        return None

    return fn


# ---------------------------------------------------------------- 明天怪兽：从顶天立地到揣进兜里（全讲一个对象）

BIG = (2400, 1000, 360)          # 场景 2：顶天立地
HOVER = (1760, 880, 60)          # 场景 4：缩成手掌大，飘在小周旁边
ZX, ZY, ZS = 1400, 1500, 1.5     # 小周（大号），左手插在兜里
PX, PY = 1310, 1270              # 口袋中心（口袋上沿 y=1220）
PEEK_Y = 1215                    # 揣进兜里后只露出上半截
J2 = J4 = J13 = 0                # 场景序号，建镜后赋值


def big_monster_fn(c, k, T):
    """场景 2：描出巨大的怪兽；到 drop 那一拍就不画了（交给 shrink_fn）。"""
    if T >= b.t_of(J4, 0):
        return None
    part, tip = wb.partial(monster(*BIG, side=-1), k)
    c.drawPath(part, wb.marker(BLACK, 12))
    return tip if k < 1 else None


def big_belly_fn(c, k, T):
    if T >= b.t_of(J4, 0):
        return None
    tip = belly_text(c, *BIG, k)
    return tip if k < 1 else None


def shrink_fn(c, k, T):
    """场景 4 第 0–4 拍：“噗”地缩到手掌大 → 飘一会儿 → 落进兜里；之后一直在兜里探头（场景 13 再探一下）。"""
    bx, by, br = BIG
    hx, hy, hr = HOVER
    in_pocket = k >= 0.75
    if k < 0.3:
        e = ease_in_out(k / 0.3)
        x, y = lerp(bx, hx, e), lerp(by, hy, e)
        r = math.exp(lerp(math.log(br), math.log(hr), e))
    elif k < 0.75:
        x, y, r = hx, hy + 14 * math.sin((k - 0.3) * 30), hr
    else:
        e = ease_in_out(clamp01((k - 0.75) / 0.25))
        x = lerp(hx, PX, e)
        y = lerp(hy, PEEK_Y, e) - 90 * math.sin(math.pi * e)
        r = hr
    if k >= 1:
        t0, t1 = b.t_of(J13, 6), b.t_of(J13, 8)
        f = clamp01((T - t0) / max(1e-3, t1 - t0))
        y -= 32 * math.sin(math.pi * f)
        x += 10 * math.sin(f * 18) * math.sin(math.pi * f)
    c.save()
    if in_pocket:
        c.clipRect(skia.Rect.MakeLTRB(0, 0, b.BW, PY - 48))
    w = lerp(7, 12, clamp01((r - hr) / (br - hr)))
    c.drawPath(monster(x, y, r, side=-1, cal=not in_pocket), wb.marker(BLACK, w))
    belly_text(c, x, y, r)
    c.restore()
    return None


# ---------------------------------------------------------------- 开局：技巧收藏一大堆（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

b.shot("技巧收藏一大堆", "开局 · 收藏夹", (820, 1080, 0.85), bars=2)
L(join(rect(780, 1100, 420, 700, 40), P((955, 820), (955, 1400)), rect(955, 830, 16, 40, 6)), 0, 0.9, sfx="wood_high")
T("收藏夹", 760, 870, 64, k0=1, k1=1.8, sfx="pop")
L(podium_list(760, 1010, 3, 320, 90), 2, 2.8, BLACK, 8, sfx="wood_high")
T("番茄钟", 760, 1010, 54, k0=3, k1=3.8, sfx="pop")
T("早起法", 760, 1116, 54, k0=4, k1=4.8, sfx="pop")
T("清单术", 760, 1222, 54, k0=5, k1=5.8, sfx="pop")

VBIG = (1950, 1100, 0.62)
b.shot("还是拖，更烦了", "开局 · 越学越拖", VBIG, bars=3)
J2 = J()
L(zhou(ZX, ZY, ZS, "hold", "frown"), 0, 0.9, sfx="wood_high")
b.custom(J(), 1, 1.9, big_monster_fn, sfx="wood_low")
b.custom(J(), 2, 2.8, big_belly_fn, sfx="pop")
L(bubble(ZX, 800, 460, 130, 1), 3, 3.6, BLACK, 9, sfx="pop")
T("我怎么又拖了", ZX, 800, 64, k0=3.6, k1=5.1)
T("越学越拖", ZX, 590, 80, RED, k0=6, k1=7, sfx="ding")
L(underline(ZX - 160, ZX + 160, 650, 10, 32), 7, 7.8, RED, 8, sfx="rim")

# ---------------------------------------------------------------- 书中观点（场景 3–6）

b.shot("书里怎么看", "拖延心理学 · 书中观点", (1800, 2450, 0.75), bars=3)
L(book(1250, 2150, 320, 210), 0, 0.9, sfx="wood_low")
T("《拖延心理学》", 1950, 2120, 68, GREEN, k0=1, k1=2.75, sfx="pop")
T("博克和袁", 1950, 2230, 56, k0=2.75, k1=3.75)
L(loop_arrow(1250, 2600, 62), 4, 4.8, BLACK, 9, sfx="wood_high")
L(join(rect(1600, 2600, 170, 130, 16), eq_sign(1600, 2600, 90)), 5, 5.8, BLACK, 9, sfx="wood_high")
L(join(clock(1950, 2600, 68), hands_at(1950, 2600, 68, 11, 50)), 6, 6.8, BLACK, 9, sfx="wood_high")
L(stairs(2300, 2600, 3, 55, 45), 7, 7.8, BLACK, 9, sfx="pop")

b.shot("它会变小", "书中观点 · 怪兽变小", VBIG, shake=[0], flashes=[0], bars=3)
J4 = J()
b.custom(J(), 0, 4, shrink_fn, sfx="kick")
b.custom(J(), 0, 1.2, puff_fn(*BIG))
T("噗", BIG[0], 820, 220, ORANGE, k0=1, k1=1.8, sfx="pop")
L(pocket(PX, PY), 2, 2.6, BLUE, 9, sfx="wood_high")
H(3, "tom")
T("能变小", 1850, 1450, 84, RED, k0=5, k1=5.8, sfx="pop")
L(underline(1710, 1990, 1510, 10, 32), 6, 6.8, RED, 8, sfx="ding")

b.shot("少拖就算赢", "书中观点 · 少拖一点", (900, 3500, 0.85), bars=3)
L(join(P((400, 3400), (1400, 3400)), P((400, 3370), (400, 3430)), P((1400, 3370), (1400, 3430))), 0, 0.9, sfx="wood_high")
T("全拖", 400, 3510, 60, k0=1, k1=1.8, sfx="pop")
T("零", 1400, 3510, 60, k0=2, k1=2.8, sfx="pop")
T("少拖", 1120, 3510, 60, BLUE, k0=3, k1=3.8, sfx="pop")
b.custom(J(), 4, 4.9, knob_fn(400, 1120, 3400), sfx="shaker")
L(arrow((430, 3300), (1090, 3300), -0.12, 34), 5, 5.8, GREEN, 9, sfx="wood_high")
T("知道自己在躲什么", 900, 3720, 60, k0=6, k1=8, sfx="pop")

b.shot("别跟自己死磕", "书中观点 · 别骂自己", (2700, 3500, 0.85), bars=3)
L(zhou(2400, 3800, 0.8, "up", "frown"), 0, 0.9, sfx="wood_high")
L(whip(2464, 3536), 1, 1.9, BLACK, 9, sfx="wood_low")
L(bubble(2300, 3180, 300, 120, 1), 2, 2.6, BLACK, 8, sfx="pop")
T("我真没用", 2300, 3180, 56, k0=2.6, k1=3.6)
T("越骂越拖", 2850, 3140, 56, RED, k0=4, k1=5, sfx="pop")
L(cross(2620, 3400, 90), 5, 5.6, RED, 12, sfx="rim")
L(cup(3050, 3680), 6, 6.9, ORANGE, 9, sfx="wood_high")
T("喝口热水", 3050, 3880, 56, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 身边的例子（场景 7–9）

b.shot("加班到半夜那周", "例子 · 连轴转", (900, 4750, 0.85), bars=3)
L(desk(980, 4900, 420), 0, 0.9, sfx="wood_high")
L(zhou(620, 5150, 0.8, "down", "frown"), 1, 1.9, sfx="wood_high")
L(join(clock(1250, 4480, 85), hands_at(1250, 4480, 85, 23, 50)), 2, 2.8, BLACK, 9, sfx="wood_high")
T("23:50", 1250, 4640, 56, RED, k0=3, k1=3.8, sfx="pop")
T("连轴转一周", 600, 4500, 60, k0=4, k1=5, sfx="pop")
L(join(P((690, 4845), (702, 4880)), P((715, 4880), (727, 4915))), 5, 5.6, BLUE, 7, sfx="shaker")
T("这周拖得最凶", 900, 5120, 60, RED, k0=6, k1=7.5, sfx="ding")

b.shot("消息一直在响", "例子 · 消息不停", (2700, 4750, 0.85), bars=3)
L(rect(2700, 4760, 380, 620, 40), 0, 0.9, sfx="wood_high")
L(podium_list(2680, 4620, 3, 280, 80), 1, 1.8, BLACK, 8, sfx="pop")
b.custom(J(), 2, 2.4, dot_fn(2810, 4585, 22), sfx="pop")
b.custom(J(), 3, 3.4, dot_fn(2810, 4681, 22), sfx="pop")
b.custom(J(), 3.5, 3.9, dot_fn(2810, 4777, 22))
T("99+", 2880, 4450, 56, RED, k0=4, k1=4.8, sfx="pop")
L(join(shake_lines(2470, 4760, -1), shake_lines(2930, 4760, 1)), 5, 5.7, BLUE, 7, sfx="shaker")
T("一件事做不完", 2700, 5170, 60, k0=6, k1=7.5, sfx="pop")

b.shot("什么都答应", "例子 · 谁找都说好", (900, 6000, 0.85), bars=3)
L(zhou(800, 6350, 0.8, "up", "frown"), 0, 0.9, sfx="wood_high")
L(podium_list(800, 5830, 3, 320, 70), 1, 1.9, BLACK, 8, sfx="wood_low")
T("别人的", 800, 5916, 50, k0=2, k1=2.8, sfx="pop")
L(bubble(1250, 5800, 300, 120, -1), 3, 3.6, BLACK, 8, sfx="pop")
T("好的好的", 1250, 5800, 56, k0=3.6, k1=4.6)
b.custom(J(), 5, 5.5, note_fn(1250, 6280, 240, 150))
L(rect(1250, 6280, 240, 150, 8), 5, 5.7, ORANGE, 7, sfx="wood_high")
T("我的事", 1250, 6280, 54, k0=5.7, k1=6.5)
T("排最后", 1250, 6440, 56, RED, k0=7, k1=7.8, sfx="rim")

# ---------------------------------------------------------------- 具体做法（场景 10–12）

b.shot("找个人陪你做", "做法一 · 找人一起开工", (2700, 6000, 0.85), bars=3)
L(join(P((2280, 6300), (3120, 6300)), P((2310, 6300), (2310, 6420)), P((3090, 6300), (3090, 6420))), 0, 0.9,
  sfx="wood_high")
L(zhou(2450, 6450, 0.75), 1, 1.9, sfx="wood_high")
L(join(stick(2950, 6450, 0.75), face(2950, 6450, 0.75, "smile")), 2, 2.9, BLUE, 9, sfx="wood_high")
L(bubble(2450, 5990, 300, 110, 1), 3, 3.6, BLACK, 8, sfx="pop")
T("我开始了", 2450, 5990, 54, k0=3.6, k1=4.6)
L(bubble(2950, 5990, 260, 110, -1), 5, 5.6, BLUE, 8, sfx="pop")
T("我也是", 2950, 5990, 54, BLUE, k0=5.6, k1=6.4)
L(check(2700, 6200, 45), 7, 7.6, GREEN, 10, sfx="ding")

b.shot("学会说不", "做法二 · 说这周排不进", (900, 7250, 0.85), bars=3)
L(zhou(600, 7550, 0.8, "point"), 0, 0.9, sfx="wood_high")
L(join(doc(1220, 7380, 150, 190, 3), doc(1250, 7340, 150, 190, 3), doc(1280, 7300, 150, 190, 3)), 1, 1.9,
  BLACK, 8, sfx="wood_low")
L(arrow((1150, 7420), (900, 7420), 0, 30), 2, 2.7, ORANGE, 9, sfx="pop")
L(bubble(650, 7050, 380, 120, -1), 3, 3.6, BLACK, 8, sfx="pop")
T("这周排不进", 650, 7050, 56, k0=3.6, k1=4.85)
L(P((830, 7220), (830, 7580)), 5, 5.6, BLUE, 14, sfx="wood_high")
L(cross(1000, 7420, 40), 6, 6.5, RED, 10, sfx="rim")
T("说不也行", 1150, 7660, 60, RED, k0=7, k1=8, sfx="ding")

b.shot("睡够，动一动", "做法三 · 身体", (2700, 7250, 0.85), bars=3)
L(bed(2420, 7380), 0, 0.9, sfx="wood_high")
T("睡够", 2420, 7560, 60, k0=1, k1=1.8, sfx="pop")
L(shoe(3050, 7420), 2, 2.9, BLUE, 9, sfx="wood_high")
T("动一动", 3050, 7560, 60, BLUE, k0=3, k1=3.8, sfx="pop")
L(join(P((2740, 7400), (2820, 7400)), P((2780, 7360), (2780, 7440))), 4, 4.5, GREEN, 10, sfx="pop")
T("会影响拖不拖", 2700, 7020, 64, k0=5, k1=6.5, sfx="pop")
L(underline(2510, 2890, 7070, 10, 32), 7, 7.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 收尾：全板 + 兜里的小怪兽（场景 13）

FAR = (1800, 4550, 0.11)
POCKV = (1450, 1100, 0.85)
b.shot("这一季的白板", "收尾 · 全板", FAR, bars=3)
J13 = J()
for n, (a, z) in enumerate((((1950, 1560), (1950, 1980)), ((1300, 2720), (900, 3220)), ((1520, 3560), (2150, 3560)),
                            ((2500, 4000), (1100, 4380)), ((2700, 5260), (1000, 5720)))):
    L(arrow(a, z, 0.1, 150), n, n + 0.8, GREEN, 40, sfx="wood_high")
b.move(J(), 5, POCKV, dur=1.2)
H(5, "shaker")
H(6, "tom")
T("还在兜里", 1820, 1000, 64, BLUE, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

COMMENT = (1800, 8600, 0.8)
b.shot("这季哪讲最戳你", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("这季哪一讲最戳你？", 1800, 8500, 72, RED, k0=6, k1=8.25, sfx="pop")
T("这一季讲完了", 1800, 8660, 60, k0=9, k1=10.5, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "less", "少拖一点", "拖延改不干净，那就少拖一点", ACC, b.shots,
                 [f"{BOOK}全书态度（拖延很少一下根除，目标是少拖一点，转述）",
                  f"{BOOK}第14章（中译本“作战方法B：学会‘接受’和‘拒绝’”，大意）、第15章（“作战方法C：利用你的身体减轻拖延”，大意）、"
                  "第17章（“巧妙应对造成拖延的文化压力”，大意）",
                  "中译本：《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009；原书 Da Capo Lifelong Books 2008 修订版"],
                 "拖延改不干净|那就【少拖一点】", SQUARE_SHOT,
                 ["书中观点为转述：拖延很少一下子根除，目标是少拖一点，拖的时候知道自己在躲什么，对自己别那么狠"
                  "（据书中思路整理）；找人支持、开口求助，也学会对额外的事说不（第14章，大意）；睡眠、运动、减压会影响拖不拖"
                  "（第15章，大意）；节奏快、信息多也会把人推向拖延（第17章，大意）。第14、15、17章细节需核实，上屏只用大意。"
                  "上屏句子均为口语转述，不是逐字引文。",
                  "“拖了就骂自己只会拖更久”为据书中思路整理。",
                  "收藏夹里的防拖延技巧、连轴转那周、23:50、消息红点与“99+”、谁找都说好、“这周排不进”均为现实场景示意，"
                  "不指向任何具体公司或个人；时间与数字为示意，不是数据。",
                  "三步做法（找个人一起开工、额外的事先说“这周排不进”、睡够动一动）为据书中思路整理的建议。",
                  "明天怪兽、鞭子与热水、滑块、口袋等为本系列的画面比喻；场景 3 的小图标回顾本季前几讲（圈、等式、两种时间、台阶）。"],
                 tags="#拖延症 #自我接纳")
    return b.attach(ep)
