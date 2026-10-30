"""04 跟催的人较劲（白板手绘版）：领导越催，我越不想动。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，画完停 4 拍）。
叙事（H 对话改写）：群里被艾特“今天下班前交”→ 手机一扣、抱着胳膊不动，明天怪兽陪着一起抱臂 →
亮书：书里说有人拿拖延争主导权 → drop：拔河绳“嘣”地绷直，领导一头、小周一头，绳结上一个红字“拖”→
心里那句“照他说的做就输了”→ 可越拖越得等人来拽，节奏在对方手里 →
白板分两栏：左栏“心里原话”（黑字，一句句划掉），右栏“改写后”（蓝字），中间一根绳子从上垂到底；
四组改写（几点做我自己定 / 先报个时间 / 有意见当面说 / 做完是我的活儿）各占一屏 →
绳子松了，两人各拿一头，绳上写“交付时间”→ 拉远看两栏 → 评论区。
书中观点为转述（简·博克、莱诺拉·袁《拖延心理学》第4章，控制权一章；中英章节对应需核实）；
群里催稿、四句改写等例子与做法为示意，据书中思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, clock,
                               desk, doc, face, hands_at, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#4F7A5A"
SQUARE_SHOT = 3                 # 场景 4：拔河绳绷直，领导一头、小周一头，绳结写“拖”

b = Board(size=(3200, 11700))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = J() if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def phone_big(x, y, w=420, h=720) -> skia.Path:
    """竖着拿的手机：外框 + 顶栏分隔线 + 底部横条。"""
    return join(rect(x, y, w, h, 50), P((x - w / 2, y - h / 2 + 140), (x + w / 2, y - h / 2 + 140)),
                P((x - 50, y + h / 2 - 40), (x + 50, y + h / 2 - 40)))


def buzz(x, y, w, h) -> skia.Path:
    """手机两侧的震动短线。"""
    parts = []
    for side in (-1, 1):
        for dy in (-60, 0, 60):
            parts.append(P((x + side * (w / 2 + 30), y + dy - 25), (x + side * (w / 2 + 60), y + dy),
                           (x + side * (w / 2 + 30), y + dy + 25)))
    return join(*parts)


def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """小周：简笔小人 + 胸前工牌。arms 额外支持 cross（抱臂）。"""
    hy = y - 290 * s
    sh = hy + 80 * s
    if arms == "cross":
        base = join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)),
                    P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)),
                    P((x, sh), (x - 55 * s, sh + 55 * s), (x + 50 * s, sh + 45 * s)),
                    P((x, sh), (x + 55 * s, sh + 55 * s), (x - 50 * s, sh + 30 * s)))
    else:
        base = stick(x, y, s, arms)
    return join(base, rect(x + 24 * s, y - 150 * s, 26 * s, 34 * s, 4 * s))


def monster(x, y, r=100, arms="cross") -> skia.Path:
    """明天怪兽：毛茸茸的圆（锯齿轮廓）+ 两只圆眼 + 皱眉 + 小脚；arms=cross 抱臂，hold 攥着一张日历页。
    肚皮上的“明天”另用红字写在 (x, y + 0.2r)。"""
    fur = skia.Path()
    n = 44
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        rr = r * (1.0 + (0.09 if i % 2 == 0 else -0.03))
        pt = (x + math.cos(a) * rr, y + math.sin(a) * rr)
        fur.moveTo(*pt) if i == 0 else fur.lineTo(*pt)
    parts = [fur]
    for dx in (-0.33, 0.33):
        parts += [circle(x + dx * r, y - 0.42 * r, 0.19 * r), circle(x + dx * r, y - 0.38 * r, 0.06 * r)]
    parts += [P((x - 0.52 * r, y - 0.72 * r), (x - 0.16 * r, y - 0.62 * r)),
              P((x + 0.52 * r, y - 0.72 * r), (x + 0.16 * r, y - 0.62 * r)),
              P((x - 0.45 * r, y + 0.98 * r), (x - 0.45 * r, y + 1.15 * r), (x - 0.25 * r, y + 1.15 * r)),
              P((x + 0.45 * r, y + 0.98 * r), (x + 0.45 * r, y + 1.15 * r), (x + 0.65 * r, y + 1.15 * r))]
    if arms == "cross":
        parts += [P((x - 0.95 * r, y + 0.42 * r), (x + 0.5 * r, y + 0.72 * r)),
                  P((x + 0.95 * r, y + 0.42 * r), (x - 0.5 * r, y + 0.72 * r))]
    else:
        cx, cy = x + 1.35 * r, y + 0.1 * r
        parts += [P((x + 0.95 * r, y + 0.15 * r), (cx - 0.3 * r, cy)), rect(cx, cy, 0.6 * r, 0.7 * r, 6),
                  P((cx - 0.3 * r, cy - 0.18 * r), (cx + 0.3 * r, cy - 0.18 * r))]
    return join(*parts)


def flat_phone(x, y) -> skia.Path:
    """扣在桌上的手机（侧看是一块扁片）+ 两道“啪”的短线。"""
    return join(rect(x, y, 140, 22, 6), P((x - 90, y - 30), (x - 110, y - 55)), P((x + 90, y - 30), (x + 110, y - 55)))


def cloud(x, y, w, h, tail) -> skia.Path:
    """想法云：圆角框 + 一串小圆点指向 tail=(x, y)。"""
    tx, ty = tail
    return join(rect(x, y, w, h, h / 2), circle(x + (tx - x) * 0.4, y + h / 2 + (ty - y - h / 2) * 0.22, 22),
                circle(x + (tx - x) * 0.62, y + h / 2 + (ty - y - h / 2) * 0.5, 13))


def flag(x, y) -> skia.Path:
    """白旗：(x, y) 为旗杆底端。"""
    return join(P((x, y), (x, y - 430)), P((x, y - 430), (x + 200, y - 400), (x + 180, y - 330), (x + 200, y - 290),
                                            (x, y - 310)))


def puller(x, y, s, d, hand, tie=False, badge=False):
    """拔河的人：(x, y) 为脚底，d=+1 面朝右（身子往左后仰），hand 为双手握绳处。返回（路径，头心）。"""
    hip = (x, y - 120 * s)
    neck = (x - d * 50 * s, y - 245 * s)
    head = (x - d * 63 * s, y - 290 * s)
    sh = (x - d * 42 * s, y - 220 * s)
    parts = [circle(*head, 45 * s), P(neck, hip), P((x + d * 55 * s, y), hip, (x - d * 75 * s, y)),
             P(sh, hand), P(sh, (hand[0] - d * 18 * s, hand[1] + 14 * s))]
    if tie:
        tx, ty = x - d * 44 * s, y - 225 * s
        parts.append(P((tx, ty), (tx - 10 * s, ty + 40 * s), (tx + d * 2 * s, ty + 60 * s), (tx + 12 * s, ty + 38 * s),
                       close=True))
    if badge:
        parts.append(rect(x - d * 4 * s, y - 165 * s, 24 * s, 32 * s, 4 * s))
    return join(*parts), head


def lean_face(head, s, mood="grit") -> skia.Path:
    """拔河人的五官：圆眼 + 皱眉；grit 咬牙（一条平线带竖纹），smile 笑。"""
    hx, hy = head
    p = join(circle(hx - 15 * s, hy - 6 * s, 3 * s), circle(hx + 15 * s, hy - 6 * s, 3 * s),
             P((hx - 26 * s, hy - 24 * s), (hx - 8 * s, hy - 16 * s)), P((hx + 26 * s, hy - 24 * s), (hx + 8 * s, hy - 16 * s)))
    if mood == "grit":
        p.addPath(join(P((hx - 16 * s, hy + 18 * s), (hx + 16 * s, hy + 18 * s)), P((hx, hy + 12 * s), (hx, hy + 24 * s))))
    else:
        p.addArc(skia.Rect.MakeXYWH(hx - 18 * s, hy + 2 * s, 36 * s, 26 * s), 20, 140)
    return p


def knot(x, y) -> skia.Path:
    return join(circle(x, y, 30), P((x - 18, y + 26), (x - 40, y + 70)), P((x + 18, y + 26), (x + 34, y + 72)))


def strain(x, y) -> skia.Path:
    """绳结两侧的紧绷短线。"""
    parts = []
    for side in (-1, 1):
        for dy in (-55, 55):
            parts.append(P((x + side * 70, y + dy), (x + side * 120, y + dy * 1.5)))
    return join(*parts)


def skid(x, y) -> skia.Path:
    """被拽着往前滑：脚后两道擦痕 + 两团小灰。"""
    return join(P((x + 40, y + 5), (x + 170, y + 5)), P((x + 60, y + 28), (x + 210, y + 28)),
                circle(x + 225, y - 10, 14), circle(x + 250, y + 18, 10))


def dashed_box(x, y, w, h, dash=34, gap=22) -> skia.Path:
    out = skia.Path()
    corners = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]
    for i in range(4):
        (x0, y0), (x1, y1) = corners[i], corners[(i + 1) % 4]
        n = math.hypot(x1 - x0, y1 - y0)
        t = 0.0
        while t < n:
            e = min(n, t + dash)
            out.moveTo(x0 + (x1 - x0) * t / n, y0 + (y1 - y0) * t / n)
            out.lineTo(x0 + (x1 - x0) * e / n, y0 + (y1 - y0) * e / n)
            t += dash + gap
    return out


def strike(x, y, w) -> skia.Path:
    """把一句话划掉：略斜的一道。"""
    return P((x - w / 2 - 20, y + 8), (x + w / 2 + 20, y - 12))


def sticky(x, y, w=200, h=170) -> skia.Path:
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2),
                  (x - w / 2, y + h / 2), close=True), P((x + w / 2, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2 - 40),
                                                         (x + w / 2 - 40, y + h / 2)))


def meeting(x, y) -> skia.Path:
    """小周和领导隔着一张桌子：(x, y) 为桌面中点。"""
    return join(P((x - 130, y), (x + 130, y)), P((x - 110, y), (x - 110, y + 100)), P((x + 110, y), (x + 110, y + 100)),
                stick(x - 230, y + 130, 0.5, "point", tie=True), stick(x + 230, y + 130, 0.5, "hold"),
                rect(x + 242, y + 55, 14, 18, 3))


def rope_path(a, b, off, n=48, ticks=True) -> skia.Path:
    """两点之间的绳子：off(u) 给出 u∈[0,1] 处的纵向偏移；ticks 画出绳子的拧纹。"""
    (x0, y0), (x1, y1) = a, b
    pts = [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n + off(i / n)) for i in range(n + 1)]
    p = P(*pts)
    if ticks:
        for i in range(2, n - 1, 3):
            px, py = pts[i]
            p.moveTo(px - 9, py - 9)
            p.lineTo(px + 9, py + 9)
    return p


# ---------------------------------------------------------------- 拔河绳（场景 3 描出，场景 4 第 0 拍绷直）

RA, RB = (1020, 2880), (1980, 2880)      # 两只手握绳处
SAG = 110


def tug_fn(j_draw, j_drop):
    def fn(c, k, T):
        t_drop = b.t_of(j_drop, 0)
        if T < t_drop:
            path = rope_path(RA, RB, lambda u: SAG * math.sin(math.pi * u))
            part, tip = wb.partial(path, k)
            c.drawPath(part, wb.marker(BLACK, 11))
            return tip
        dt = T - t_drop
        amp = 70 * math.exp(-dt * 5.5) * math.cos(dt * 2 * math.pi * 6)
        path = rope_path(RA, RB, lambda u: amp * math.sin(math.pi * u))
        c.drawPath(path, wb.marker(BLACK, 11))
        return None

    return fn


def pop_in_fn(paths, color=BLACK, width=10):
    """整幅一下子出现（配重击）：k 从 0 到 1 时由淡到实。"""

    def fn(c, k, T):
        for p in paths:
            c.drawPath(p, wb.marker(color, width, min(1.0, 0.25 + k)))
        return None

    return fn


def divider_fn(x, y0, y1):
    """中间那根绳子从上往下垂下来（双股拧在一起）；不跟手。"""
    s1, s2 = skia.Path(), skia.Path()
    n = int((y1 - y0) / 12)
    for i in range(n + 1):
        y = y0 + i * 12
        dx = 11 * math.sin(y / 34)
        (s1.moveTo if i == 0 else s1.lineTo)(x + dx, y)
        (s2.moveTo if i == 0 else s2.lineTo)(x - dx, y)

    def fn(c, k, T):
        for s in (s1, s2):
            part, _ = wb.partial(s, k)
            c.drawPath(part, wb.marker(BLACK, 7))
        return None

    return fn


def stamp_fn(x, y, r, label):
    """盖章：红圈 + 名字，从大到小“啪”地落下。"""

    def fn(c, k, T):
        sc = 1.0 + 0.5 * (1 - clamp01(k)) ** 2
        c.save()
        c.translate(x, y)
        c.rotate(-12)
        c.scale(sc, sc)
        c.drawPath(circle(0, 0, r), wb.marker(RED, 9, min(1.0, 0.3 + k)))
        K.text(c, label, 0, 0, 50, "hand", RED, min(1.0, 0.3 + k))
        c.restore()
        return None

    return fn


# ---------------------------------------------------------------- 开局：又被催了（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

PH = (1150, 820)
scene("又在群里催了", "灵魂拷问", (1150, 820, 0.9), bars=2)
L(phone_big(*PH), 0, 0.9, BLACK, 10, sfx="wood_high")
T("项目群", PH[0], 560, 50, k0=1, k1=1.8, sfx="pop")
L(bubble(PH[0], 820, 360, 220, -1), 2, 2.8, BLACK, 8, sfx="pop")
T("@小周", PH[0], 770, 56, BLUE, k0=3, k1=3.8, sfx="pop")
T("今天下班前交", PH[0], 865, 50, k0=4, k1=5.4, sfx="pop")
L(buzz(PH[0], 820, 420, 720), 5, 5.8, RED, 8, sfx="shaker")

scene("越催越不想写", "灵魂拷问", (1650, 1000, 0.7))
L(arrow((1300, 1190), (1500, 1255), -0.25, 34), 0, 0.8, BLACK, 8, sfx="wood_high")
L(flat_phone(1540, 1287), 0.8, 1.2, BLACK, 8)
L(desk(1650, 1300, 440), 2, 2.9, BLACK, 9, sfx="wood_low")
L(zhou(2000, 1480, 0.8, "cross"), 3, 3.9, BLACK, 9, sfx="wood_high")
L(face(2000, 1480, 0.8, "sad"), 3.9, 4.1)
L(monster(2270, 1350, 100, "cross"), 5, 5.9, BLACK, 8, sfx="wood_low")
T("明天", 2270, 1370, 48, RED, k0=6, k1=6.8, sfx="pop")
T("已读，不回", 1900, 1000, 66, RED, k0=7, k1=8, sfx="rim")

# ---------------------------------------------------------------- 书中观点：拿拖延较劲（场景 3–6）

j3 = scene("书里说这是较劲", "拖延心理学 · 书中观点", (1500, 2550, 0.7))
L(book(950, 2150, 360, 240), 0, 0.9, BLACK, 9, sfx="wood_low")
T("拖延心理学", 950, 2385, 60, GREEN, k0=1, k1=2.25, sfx="pop")
T("有人拿拖延", 1600, 2120, 62, k0=3, k1=4.25, sfx="pop")
T("争主导权", 1600, 2215, 62, RED, k0=5, k1=6, sfx="pop")
j4 = j3 + 1
b.custom(j3, 6, 6.9, tug_fn(j3, j4), sfx="wood_high")
T("谁说了算？", 1500, 3150, 70, RED, k0=7, k1=8, sfx="ding")

LEAD, LEAD_HEAD = puller(920, 3050, 0.9, 1, RA, tie=True)
ZHOU, ZHOU_HEAD = puller(2080, 3050, 0.9, -1, RB, badge=True)

scene("拖着就是不服", "书中观点 · 争主导权", (1500, 2660, 0.68), shake=[0], flashes=[0])
b.custom(J(), 0, 0.25, pop_in_fn([LEAD, ZHOU], BLACK, 10), sfx="kick")
L(knot(1500, 2880), 1, 1.6, BLACK, 9, sfx="tom")
T("拖", 1500, 2740, 120, RED, k0=2, k1=2.8, sfx="ding")
T("领导", 860, 2660, 56, k0=3, k1=3.8, sfx="pop")
T("小周", 2140, 2660, 56, BLUE, k0=4, k1=4.8, sfx="pop")
L(strain(1500, 2880), 5, 5.8, RED, 8, sfx="shaker")
L(lean_face(LEAD_HEAD, 0.9), 6, 6.6, BLACK, 7, sfx="wood_high")
L(lean_face(ZHOU_HEAD, 0.9), 6.6, 7.2, BLACK, 7)

scene("照做像认输", "书中观点 · 心里原话", (2450, 2550, 0.85))
T("心里原话", 2700, 2050, 52, k0=0, k1=1, sfx="pop")
L(cloud(2700, 2250, 560, 280, ZHOU_HEAD), 1, 1.9, BLACK, 8, sfx="wood_high")
T("照他说的做", 2700, 2210, 62, k0=2, k1=3.25, sfx="pop")
T("就输了", 2700, 2305, 62, RED, k0=4, k1=4.8, sfx="pop")
L(flag(2780, 3050), 5, 5.9, BLACK, 9, sfx="wood_low")
T("认输", 2900, 2880, 60, RED, k0=6, k1=6.8, sfx="rim")

scene("节奏还在他手里", "书中观点 · 被牵着走", (1500, 2660, 0.68))
L(skid(2080, 3050), 0, 0.7, BLACK, 7, sfx="shaker")
L(arrow((1900, 2790), (1660, 2790), 0.12, 34), 1, 1.8, RED, 9, sfx="wood_high")
L(clock(1180, 2650, 70), 2, 2.8, BLACK, 8, sfx="tom")
L(hands_at(1180, 2650, 70, 12, 50), 3, 3.4, RED, 8, sfx="pop")
T("节奏", 1180, 2785, 50, k0=4, k1=4.8, sfx="pop")
T("他拽一下，我挪一下", 1500, 3270, 60, RED, k0=5, k1=7.25, sfx="pop")

# ---------------------------------------------------------------- 改写：左栏原话，右栏改写（场景 7–11）

LX, RX, MX = 1150, 1850, 1500
R1, ROW = 5000, 1150
ROWS = [R1 + i * ROW for i in range(4)]
DIV = (MX, 3690, ROWS[-1] + 300)

scene("改一句话试试", "改写 · 换个说法", (1500, 4300, 0.8))
T("心里原话", LX, 3760, 64, k0=0, k1=1, sfx="pop")
L(underline(LX - 140, LX + 140, 3825, 10, 36), 1, 1.7, BLACK, 7, sfx="wood_high")
T("改写后", RX, 3760, 64, BLUE, k0=2, k1=2.8, sfx="pop")
L(underline(RX - 110, RX + 110, 3825, 10, 36), 3, 3.7, BLUE, 7, sfx="wood_high")
b.custom(J(), 4, 5, divider_fn(MX, DIV[1], R1 - 850), sfx="wood_low")   # 绳子分段往下垂：每屏只垂到本屏这一组
L(arrow((1220, 4030), (1600, 4030), -0.12, 40), 5, 5.8, GREEN, 10, sfx="ding")
L(dashed_box(RX + 40, 4030, 380, 150), 6, 6.8, BLUE, 7, sfx="pop")
T("？", RX + 40, 4030, 80, BLUE, k0=7, k1=7.8, sfx="pop")


def row(r, left, right, cap, tag):
    """一组改写的前半：左栏原话 → 红线划掉 → 绿箭头 → 右栏蓝字（right 可以是两行）。返回本镜序号。"""
    j = scene(cap, tag, (1500, r + 50, 0.8))
    b.custom(j, 0, 0.8, divider_fn(MX, r - 850, r + 300))
    T(left, LX, r - 300, 64, k0=0, sfx="pop")
    L(strike(LX, r - 300, K.text_w(left, 64, "hand")), 2, 2.6, RED, 10, sfx="rim")
    L(arrow((1370, r - 300), (1600, r - 300), -0.1, 30), 3, 3.7, GREEN, 9, sfx="wood_high")
    if isinstance(right, str):
        T(right, RX, r - 300, 58, BLUE, k0=4, k1=min(5.75, 4 + 0.25 * len(right)), sfx="pop")
    else:
        T(right[0], RX, r - 345, 58, BLUE, k0=4, k1=4 + min(1.75, 0.25 * len(right[0])), sfx="pop")
        T(right[1], RX, r - 250, 58, BLUE, k0=6, k1=6.9, sfx="pop")
    return j


r = ROWS[0]
row(r, "凭什么听他的", "几点做，我自己定", "什么时候做我定", "改写一 · 时间我定")
L(sticky(1990, r + 90), 6, 6.5, ORANGE, 9, sfx="wood_low")
T("15:00", 1985, r + 85, 56, k0=6.5, k1=7.3)
L(zhou(1700, r + 250, 0.6, "point"), 7, 7.8, BLACK, 8, sfx="wood_high")
L(face(1700, r + 250, 0.6, "smile"), 7.8, 8)

r = ROWS[1]
j9 = scene("先报个时间", "改写二 · 报时间", (1500, r + 50, 0.8))
b.custom(j9, 0, 0.8, divider_fn(MX, r - 850, r + 300))
T("别催了", LX, r - 300, 64, k0=0, k1=0.8, sfx="pop")
L(strike(LX, r - 300, K.text_w("别催了", 64, "hand")), 1, 1.6, RED, 10, sfx="rim")
L(arrow((1300, r - 300), (1570, r - 300), -0.1, 30), 2, 2.7, GREEN, 9, sfx="wood_high")
L(bubble(RX, r - 300, 470, 130, -1), 3, 3.8, BLUE, 8, sfx="pop")
T("下午四点给初稿", RX, r - 300, 52, k0=4, k1=5.75, sfx="pop")
L(clock(RX, r + 130, 120), 6, 6.8, BLACK, 9, sfx="wood_low")
L(hands_at(RX, r + 130, 120, 4, 0), 7, 7.6, RED, 9, sfx="ding")

r = ROWS[2]
row(r, "偏不按他的来", ("这个格式我想换", "理由是……"), "有意见当面说", "改写三 · 当面说")
L(meeting(RX, r + 100), 7, 7.9, BLACK, 8, sfx="wood_low")

r = ROWS[3]
j11 = row(r, "做完就是认输", "做完是我的活儿", "做完算我的", "改写四 · 我的活儿")
L(doc(1800, r + 80, 200, 250, 5), 6, 6.8, BLACK, 9, sfx="wood_low")
b.custom(j11, 7, 7.3, stamp_fn(1880, r + 160, 62, "小周"), sfx="kick")

# ---------------------------------------------------------------- 绳子松了 / 拉远看两栏（场景 12–13）

R5 = ROWS[-1] + ROW
scene("绳子松了", "改写之后", (1420, R5 + 50, 0.85))
L(stick(950, R5 + 300, 0.9, "down", tie=True), 0, 0.9, BLACK, 9, sfx="wood_high")
L(face(950, R5 + 300, 0.9, "smile"), 0.9, 1.1)
L(zhou(1650, R5 + 300, 0.9, "down"), 1, 1.9, BLACK, 9, sfx="wood_high")
L(face(1650, R5 + 300, 0.9, "smile"), 1.9, 2.1)
L(P((1013, R5 + 192), (1040, R5 + 285), (1100, R5 + 292), (1300, R5 + 288), (1500, R5 + 293), (1560, R5 + 286),
    (1587, R5 + 192)), 2, 2.9, BLACK, 11, sfx="wood_low")
T("交付时间 16:00", 1300, R5 + 210, 54, GREEN, k0=3, k1=4.5, sfx="pop")
T("不拽了", 1300, R5 - 230, 80, k0=5, k1=5.8, sfx="ding")
L(monster(1950, R5 + 180, 85, "cross"), 6, 6.8, BLACK, 8, sfx="wood_low")
T("明天", 1950, R5 + 196, 46, RED, k0=7, k1=7.8, sfx="pop")

COLS = (1500, (DIV[1] + DIV[2]) / 2, 0.176)
scene("四句放一起看", "两栏对照", COLS)
H(0, "shaker", 0.6)
for n, rr in enumerate(ROWS):
    L(check(2290, rr - 300, 120), 1 + n, 1.8 + n, GREEN, 20, sfx="ding" if n % 2 == 0 else "pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

R6 = R5 + 1300
FAR = (1600, 5900, 0.085)
CMT = (1500, R6, 0.8)
j_end = scene("你心里哪句最响", "评论区见", FAR, bars=4)
b.move(j_end, 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
L(bubble(1500, R6 - 120, 760, 190, -1), 4, 4.9, BLACK, 8, sfx="wood_high")
T("你心里哪句最响？", 1500, R6 - 120, 76, RED, k0=6, k1=8, sfx="pop")
T("下一讲：有人拖着等人帮，有人拖着躲人", 1500, R6 + 110, 50, k0=9, k1=12, sfx="wood_high")
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "control", "跟催的人较劲", "领导越催，我越不想动", ACC, b.shots,
                 [f"{BOOK}第4章（控制权一章，“为赢而战”，转述；中英章节对应需核实）",
                  "中译本：蒋永强、陆正芳译，中国人民大学出版社 2009"],
                 "领导越催|我越【不想动】", SQUARE_SHOT,
                 ["书中观点为转述：有人用拖延争控制权，拖着不办等于在说“我不受你摆布”，照别人的规矩来像是认输；"
                  "可这样一来，事情的节奏反倒绑在了对方的催促上。见简·博克、莱诺拉·袁《拖延心理学》第4章"
                  "（中译本：蒋永强、陆正芳译，中国人民大学出版社 2009；第4章中英标题对应需核实）。上屏均为转述，不是逐字引文。",
                  "群里被艾特催稿、拔河绳、白旗等画面为示意；不针对任何真实领导或公司。",
                  "四组改写（几点做我自己定 / 先报个时间 / 有意见当面说 / 做完是我的活儿）为示意，据书中思路整理；"
                  "“16:00”“15:00”等时间为示意，不是数据。"],
                 tags="#职场沟通 #拖延")
    return b.attach(ep)
