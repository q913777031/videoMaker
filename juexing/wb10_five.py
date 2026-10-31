"""10 人生五件套（白板手绘版）：下班后那两小时，怎么过？（系列最后一讲）

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事形式 B 一周故事 + 全季收尾：整讲的骨架是一张七格周日历——
开局一只大钟，晚上九点到十一点涂出一块扇形（下班吃完饭剩下的两小时，去哪了？）→
回看第一讲：扇形里塞满手机 → 小林试了一周，七格日历逐格描出 →
drop：闹钟、蒲团、书、笔、跑鞋五个图标一齐砸进日历（早起 / 冥想 / 阅读 / 写作 / 运动）→
亮书（《认知觉醒》+ 周岭，书旁一个舵写“10”）→ 一天一页：
周一早睡（月亮、被子 → 太阳、没响的闹钟）、周二坐五分钟（呼吸圈一胀一缩，飘走的念头被拉回）、
周三跟作者聊（书里探出一个小人和小林对话，书架像朋友圈）、周四讲给自己听（写一段，头顶小外行点头）、
周五跑一圈（跑道上追前面的人，跑完做难事）、周末复个盘（小本子三行：写经过、问为什么、留一个行动点）→
全季收尾：小林的脑袋剖面里一条小船，两个哥哥划桨，宝宝站在舵后掌舵，舵上十道握痕依次亮起（第 10 道为本讲新增）→
拉远：十讲各一个小图标串成一条航线 → 评论区：五件套你先试哪一件？这一季讲完了。
书中观点为转述（周岭《认知觉醒》第八章“早冥读写跑，人生五件套”、第七章第三节“游戏心态”、结语）；
小林的一周、每件事的时间安排与做法细节为示意，据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, clock,
                               cross, doc, hands_at, join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#B5476B"
SQUARE_SHOT = 3                 # 场景 4：五个图标砸进一周日历，小林站在日历前

b = Board(size=(3600, 14000))
PAPER = "#FBFBF9"


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(fn, k0, k1, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


def ink(c, path, color, width, alpha=1.0):
    """和引擎描线同样的马克笔笔触（custom 动画里用）。"""
    c.drawPath(path, wb.marker(color, width, alpha))
    c.drawPath(path, K.paint(color, 0.22 * alpha, width * 0.45, blur=1.2))


def moved(path, dx=0.0, dy=0.0, s=1.0, ax=0.0, ay=0.0) -> skia.Path:
    """以 (ax, ay) 为锚点缩放后再平移的路径副本。"""
    p = skia.Path(path)
    m = skia.Matrix()
    m.setTranslate(-ax, -ay)
    m.postScale(s, s)
    m.postTranslate(ax + dx, ay + dy)
    p.transform(m)
    return p


def pop_s(k):
    """弹出：0 → 1.15 → 1。"""
    return ease_out(clamp01(k * 1.6)) * (1 + 0.15 * math.sin(math.pi * clamp01(k)))


def park(x0, y0, x1, y1, k0, k1):
    """不画东西，只把笔从 (x0, y0) 挪到空白处 (x1, y1) 停住，免得停住的手挡住刚写完的字。"""

    def fn(c, k, Tm):
        if k >= 1:
            return None
        u = ease_in_out(k)
        return (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)

    C(fn, k0, k1)


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


# ---------------------------------------------------------------- 系列角色：三兄弟与船舵

def baby(x, y, s=1.0) -> skia.Path:
    """老三“理智脑”：大头、戴围嘴的小宝宝，右手往右上伸（握舵）。(x, y) 为脚底。"""
    hy = y - 150 * s
    r = 55 * s
    bib = skia.Path()
    bib.addArc(skia.Rect.MakeXYWH(x - 30 * s, hy + r - 22 * s, 60 * s, 50 * s), 0, 180)
    curl = skia.Path()
    curl.moveTo(x - 6 * s, hy - r)
    curl.quadTo(x + 4 * s, hy - r - 26 * s, x + 18 * s, hy - r - 12 * s)
    eyes = skia.Path()
    eyes.addCircle(x - 18 * s, hy - 4 * s, 3.5 * s)
    eyes.addCircle(x + 18 * s, hy - 4 * s, 3.5 * s)
    smile = skia.Path()
    smile.addArc(skia.Rect.MakeXYWH(x - 14 * s, hy + 6 * s, 28 * s, 22 * s), 20, 140)
    hands = join(P((x - 22 * s, hy + r + 12 * s), (x + 60 * s, hy + r - 10 * s), (x + 100 * s, hy - 40 * s)),
                 P((x + 22 * s, hy + r + 12 * s), (x + 110 * s, hy + r + 10 * s), (x + 150 * s, hy + 10 * s)))
    return join(circle(x, hy, r), curl, eyes, smile, bib,
                P((x, hy + r), (x, y - 50 * s)), P((x - 34 * s, y), (x, y - 50 * s), (x + 34 * s, y)), hands)


def rower(x, y, s=1.0, kind="grandpa") -> skia.Path:
    """坐在船里划桨的哥哥（只画上半身 + 桨）：(x, y) 为船舷高度上的腰部。kind：grandpa（白胡子）/ uncle（耳机）。"""
    hy = y - 210 * s
    r = 42 * s
    parts = [circle(x, hy, r), P((x, hy + r), (x - 8 * s, y + 10 * s)),
             P((x - 4 * s, hy + r + 40 * s), (x + 50 * s, hy + r + 90 * s), (x + 95 * s, y - 70 * s)),
             P((x - 4 * s, hy + r + 40 * s), (x + 30 * s, hy + r + 110 * s), (x + 85 * s, y - 40 * s))]
    oar = join(P((x + 110 * s, y - 95 * s), (x - 70 * s, y + 200 * s)), oval(x - 82 * s, y + 220 * s, 46 * s, 70 * s))
    parts.append(oar)
    if kind == "grandpa":
        parts.append(P((x - 34 * s, hy + 16 * s), (x, hy + 74 * s), (x + 34 * s, hy + 16 * s)))
    else:
        band = skia.Path()
        band.addArc(skia.Rect.MakeXYWH(x - 54 * s, hy - 58 * s, 108 * s, 108 * s), 180, 180)
        parts += [band, rect(x - 50 * s, hy, 20 * s, 40 * s, 7 * s), rect(x + 50 * s, hy, 20 * s, 40 * s, 7 * s)]
    return join(*parts)


def helm(x, y, r=90) -> skia.Path:
    """船舵：外圈 + 轴心 + 八根带把手的辐条。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.3)]
    for i in range(8):
        a = i / 8 * 2 * math.pi + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        parts.append(P((x + ca * r * 0.3, y + sa * r * 0.3), (x + ca * r * 1.32, y + sa * r * 1.32)))
        parts.append(circle(x + ca * r * 1.36, y + sa * r * 1.36, r * 0.07))
    return join(*parts)


def grip(x, y, r, i) -> skia.Path:
    """舵上第 i 道握痕（从 0 数）：系列第 N 讲舵上有 N 道，十道沿轮圈排一圈。"""
    a = math.radians(-90 + 36 * i)
    return join(*[P((x + math.cos(a + d) * r * 0.8, y + math.sin(a + d) * r * 0.8),
                    (x + math.cos(a + d) * r * 1.2, y + math.sin(a + d) * r * 1.2)) for d in (-0.07, 0.07)])


def grips(x, y, r, idx) -> skia.Path:
    return join(*[grip(x, y, r, i) for i in idx])


# ---------------------------------------------------------------- 五件套图标（约 140 见方，(x, y) 为中心）

def alarm(x, y, s=1.0) -> skia.Path:
    r = 50 * s
    bells = skia.Path()
    bells.addArc(skia.Rect.MakeXYWH(x - r - 14 * s, y - r - 22 * s, 44 * s, 44 * s), 180, 180)
    bells.addArc(skia.Rect.MakeXYWH(x + r - 30 * s, y - r - 22 * s, 44 * s, 44 * s), 180, 180)
    return join(circle(x, y, r), hands_at(x, y, r, 7, 0), bells,
                P((x - r * 0.6, y + r * 0.8), (x - r * 0.9, y + r * 1.25)),
                P((x + r * 0.6, y + r * 0.8), (x + r * 0.9, y + r * 1.25)))


def cushion(x, y, s=1.0) -> skia.Path:
    """蒲团：一个扁圆垫 + 中间一颗扣。"""
    side = join(P((x - 70 * s, y), (x - 70 * s, y + 30 * s)), P((x + 70 * s, y), (x + 70 * s, y + 30 * s)))
    bottom = skia.Path()
    bottom.addArc(skia.Rect.MakeXYWH(x - 70 * s, y + 5 * s, 140 * s, 50 * s), 0, 180)
    return join(oval(x, y, 140 * s, 50 * s), side, bottom, circle(x, y, 7 * s))


def pen(x, y, s=1.0) -> skia.Path:
    """斜放的笔：笔杆 + 笔尖 + 笔帽夹。"""
    a = math.radians(-45)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    L0, L1, w = -60 * s, 50 * s, 14 * s

    def pt(t, o):
        return (x + ux * t + nx * o, y + uy * t + ny * o)

    body = P(pt(L0, -w), pt(L1, -w), pt(L1, w), pt(L0, w), close=True)
    tip = P(pt(L0, -w), pt(L0 - 30 * s, 0), pt(L0, w))
    clip = P(pt(L1 - 10 * s, w), pt(L1 - 45 * s, w + 12 * s))
    return join(body, tip, clip)


def shoe(x, y, s=1.0) -> skia.Path:
    """跑鞋侧面：鞋身 + 鞋底 + 两道鞋带。"""
    body = P((x - 70 * s, y + 30 * s), (x - 70 * s, y - 40 * s), (x - 30 * s, y - 40 * s), (x - 10 * s, y - 8 * s),
             (x + 45 * s, y + 2 * s), (x + 72 * s, y + 30 * s), close=True)
    return join(body, P((x - 74 * s, y + 44 * s), (x + 76 * s, y + 44 * s)),
                P((x - 22 * s, y - 22 * s), (x - 6 * s, y - 34 * s)), P((x - 4 * s, y - 6 * s), (x + 12 * s, y - 18 * s)))


def mini_book(x, y, s=1.0) -> skia.Path:
    return book(x, y, 150 * s, 100 * s)


def notebook(x, y, w, h) -> skia.Path:
    """线圈本：外框 + 顶上一排线圈。"""
    rings = [circle(x - w / 2 + 70 + i * (w - 140) / 6, y - h / 2, 18) for i in range(7)]
    return join(rect(x, y, w, h, 20), *rings)


def moon(x, y, r=60) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def sun(x, y, r=56) -> skia.Path:
    parts = [circle(x, y, r)]
    for i in range(8):
        a = i / 8 * 2 * math.pi
        parts.append(P((x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3),
                       (x + math.cos(a) * r * 1.65, y + math.sin(a) * r * 1.65)))
    return join(*parts)


def bed(x, y) -> skia.Path:
    """床 + 盖着被子睡着的小人：(x, y) 为地面中点。"""
    p = skia.Path()
    p.moveTo(x - 140, y - 150)
    p.quadTo(x + 40, y - 210, x + 220, y - 150)
    return join(P((x - 230, y), (x - 230, y - 230)), P((x + 230, y), (x + 230, y - 140)),
                P((x - 230, y - 100), (x + 230, y - 100)), circle(x - 170, y - 150, 32), p,
                P((x - 186, y - 154), (x - 170, y - 150)), P((x - 160, y - 154), (x - 148, y - 150)))


def phone(x, y, w=44, h=76) -> skia.Path:
    return join(rect(x, y, w, h, max(6, w * 0.15)), P((x - w * 0.17, y + h / 2 - h * 0.12), (x + w * 0.17, y + h / 2 - h * 0.12)))


def day_tag(X, Y, label):
    """每天一页：左上角一格日历小牌，写着星期几（第 0 拍）。"""
    L(rect(X - 440, Y - 390, 210, 100, 16), 0, 0.5, BLACK, 8, sfx="pop")
    T(label, X - 440, Y - 388, 62, BLUE, k0=0.4, k1=1.0)


# ---------------------------------------------------------------- 下班后两小时（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

CK = (1750, 1050, 300)          # 大钟


def wedge_fn(j):
    """场景 1：从九点扫到十一点，涂出一块扇形。"""
    x, y, r = CK

    def fn(c, k, Tm):
        u = ease_in_out(k)
        p = skia.Path()
        p.moveTo(x, y)
        p.arcTo(skia.Rect.MakeXYWH(x - r * 0.96, y - r * 0.96, r * 1.92, r * 1.92), 180, 60 * u, False)
        p.close()
        c.drawPath(p, K.paint(ACC, 0.18))
        ink(c, p, ACC, 6)
        a = math.radians(180 + 60 * u)
        return (x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9) if k < 1 else None

    return fn


scene("下班后两小时", "下班以后", (1800, 1050, 0.85), bars=2)
L(clock(*CK), 0, 0.9, BLACK, 10, sfx="wood_low")
L(hands_at(CK[0], CK[1], CK[2], 9, 0), 1, 1.6, BLACK, 10, sfx="pop")
C(wedge_fn(J()), 2, 3.0, sfx="shaker")
T("21:00", CK[0] - CK[2] - 140, CK[1], 64, BLUE, k0=3, k1=4.0, sfx="pop")
T("23:00", CK[0] - 210, CK[1] - 390, 64, BLUE, k0=4, k1=5.0, sfx="pop")
T("去哪了？", CK[0], CK[1] + CK[2] + 120, 76, RED, k0=5, k1=6.0, sfx="tom")


def _wedge_pt(ang, rr):
    a = math.radians(ang)
    return CK[0] + math.cos(a) * CK[2] * rr, CK[1] + math.sin(a) * CK[2] * rr


scene("以前都刷没了", "回看第一讲", (1800, 1050, 0.85))
for n, (ang, rr) in enumerate(((196, 0.5), (224, 0.5), (190, 0.8), (230, 0.8))):
    L(phone(*_wedge_pt(ang, rr)), n, n + 0.6, RED, 7, sfx="pop")
arc = skia.Path()
arc.addArc(skia.Rect.MakeXYWH(CK[0] - 380, CK[1] - 380, 760, 760), 245, 40)
a1 = math.radians(285)
tipx, tipy = CK[0] + math.cos(a1) * 380, CK[1] + math.sin(a1) * 380
arc.moveTo(tipx, tipy)
arc.lineTo(tipx - 46, tipy - 18)
arc.moveTo(tipx, tipy)
arc.lineTo(tipx - 20, tipy + 40)
L(arc, 4, 4.8, RED, 9, sfx="wood_high")
T("全给了", 2260, 990, 72, RED, k0=5, k1=5.8, sfx="pop")
T("手机", 2260, 1090, 72, RED, k0=6, k1=6.8, sfx="pop")

# ---------------------------------------------------------------- 一周日历（场景 3–4）

CAL_Y0, CAL_Y1, HEAD_Y = 2220, 2580, 2300
CELL_X = [1800 + (i - 3) * 200 for i in range(7)]
DAYS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
ICONS = (alarm, cushion, mini_book, pen, shoe)
ICON_COL = (BLACK, BLUE, GREEN, BLACK, ORANGE)
NAMES = ("早起", "冥想", "阅读", "写作", "运动")

cal = [rect(1800, (CAL_Y0 + CAL_Y1) / 2, 1400, CAL_Y1 - CAL_Y0, 12), P((1100, HEAD_Y), (2500, HEAD_Y))]
cal += [P((1100 + 200 * i, CAL_Y0), (1100 + 200 * i, CAL_Y1)) for i in range(1, 7)]

scene("他试了一周", "小林的一周", (1800, 2650, 0.7))
L(join(*cal), 0, 1.6, BLACK, 9, sfx="wood_low")
for n, d in enumerate(DAYS):
    T(d, CELL_X[n], 2262, 56, k0=2 + n * 0.3, k1=2.3 + n * 0.3, sfx="pop" if n == 0 else None)
L(stick(1250, 3260, 0.8, "point"), 5, 5.9, BLACK, 10, sfx="wood_high")
T("小林的一周", 1800, 2110, 72, BLUE, k0=6, k1=7.25, sfx="pop")


def stamp_fn(paths):
    """五个图标一齐砸进格子：从 1.7 倍猛地压到原大，再轻轻弹一下。"""

    def fn(c, k, Tm):
        if k < 0.25:
            s = 1.7 - 0.7 * ease_out(k / 0.25)
        else:
            s = 1 + 0.08 * math.sin(math.pi * clamp01((k - 0.25) / 0.75))
        for path, col, (ax, ay) in paths:
            ink(c, moved(path, s=s, ax=ax, ay=ay), col, 8, min(1.0, 0.3 + k * 4))
        return None

    return fn


ICON_Y, NAME_Y = 2410, 2530
scene("五件事", "书中观点 · 五件套", (1800, 2650, 0.7), shake=[0], flashes=[0])
C(stamp_fn([(ICONS[n](CELL_X[n], ICON_Y, 0.85), ICON_COL[n], (CELL_X[n], ICON_Y)) for n in range(5)]), 0, 0.6,
  sfx="kick")
for n, nm in enumerate(NAMES):
    T(nm, CELL_X[n], NAME_Y, 56, ICON_COL[n] if ICON_COL[n] != BLACK else RED, k0=1 + n, k1=1.6 + n,
      sfx="pop" if n < 4 else "ding")
T("书中：早冥读写跑", 2020, 2850, 66, GREEN, k0=6, k1=8.0, sfx="pop")

# ---------------------------------------------------------------- 亮书（场景 5）

scene("有本书讲过", "认知觉醒 · 周岭", (1800, 4050, 0.85))
L(book(1600, 4050, 440, 300), 0, 0.9, BLACK, 10, sfx="wood_low")
T("认知觉醒", 1600, 3810, 76, GREEN, k0=1, k1=2, sfx="pop")
T("周岭 著", 1600, 4300, 56, k0=3, k1=3.9, sfx="pop")
L(join(helm(2200, 4010, 90), grips(2200, 4010, 90, range(9))), 4, 4.9, GREEN, 8, sfx="wood_high")
T("10", 2200, 4250, 64, GREEN, k0=5, k1=5.8, sfx="ding")

# ---------------------------------------------------------------- 一天一页（场景 6–11）：蛇形排在白板上

# 周一：早睡（X=950, Y=5450）
X, Y = 950, 5450
scene("周一：早睡", "书中观点 · 早起", (X, Y, 0.85))
day_tag(X, Y, "周一")
L(moon(X - 320, Y - 160, 70), 1, 1.7, BLUE, 9, sfx="wood_high")
L(bed(X - 250, Y + 260), 2, 2.9, BLUE, 9, sfx="wood_low")
L(arrow((X - 10, Y + 20), (X + 170, Y + 20), -0.2, 36), 3, 3.7, BLACK, 9, sfx="wood_high")
L(sun(X + 380, Y - 170, 56), 4, 4.8, ORANGE, 9, sfx="pop")
L(alarm(X + 380, Y + 160, 1.1), 5, 5.8, BLACK, 9, sfx="wood_low")
T("早起靠早睡", X, Y + 440, 76, GREEN, k0=6, k1=7.25, sfx="ding")
L(cross(X + 470, Y + 70, 34), 7, 7.5, RED, 10, sfx="rim")

# 周二：坐五分钟（X=2650, Y=5450）
X, Y = 2650, 5450
SEAT = Y + 250


def sitter(x, y, s=1.0) -> skia.Path:
    """盘腿坐着的小人：(x, y) 为坐垫面。"""
    hy = y - 230 * s
    p = skia.Path()
    p.moveTo(x - 18 * s, hy + 6 * s)
    p.lineTo(x - 6 * s, hy + 6 * s)
    p.moveTo(x + 6 * s, hy + 6 * s)
    p.lineTo(x + 18 * s, hy + 6 * s)
    return join(circle(x, hy, 45 * s), p, P((x, hy + 45 * s), (x, y - 20 * s)),
                P((x - 110 * s, y - 20 * s), (x - 70 * s, hy + 150 * s), (x, hy + 80 * s), (x + 70 * s, hy + 150 * s),
                  (x + 110 * s, y - 20 * s)),
                P((x - 150 * s, y), (x + 40 * s, y - 30 * s)), P((x + 150 * s, y), (x - 40 * s, y - 30 * s)))


def breath_fn(j, x, y):
    """呼吸圈：第 2–8 拍一胀一缩，之后停在中间大小。"""

    def fn(c, k, Tm):
        t0, t1 = b.t_of(j, 2), b.t_of(j, 8)
        u = clamp01((Tm - t0) / max(1e-3, t1 - t0))
        ph = 0.5 - 0.5 * math.cos(u * 3 * 2 * math.pi)
        rr = 230 + 70 * ph
        a = min(1.0, k * 3)
        ink(c, circle(x, y, rr), BLUE, 6, 0.55 * a)
        ink(c, circle(x, y, rr * 0.8), BLUE, 4, 0.35 * a)
        return None

    return fn


def cloud(x, y, s=1.0) -> skia.Path:
    return join(circle(x - 34 * s, y + 6 * s, 30 * s), circle(x, y - 14 * s, 38 * s), circle(x + 38 * s, y + 6 * s, 30 * s))


def drift_fn(j, x0, y0, x1, y1):
    """飘走的念头：第 4–5 拍从头顶飘出去，第 5–6 拍被拉回、缩没了。"""

    def fn(c, k, Tm):
        if k >= 1:
            return None
        u = ease_in_out(k / 0.5) if k < 0.5 else 1 - ease_in_out((k - 0.5) / 0.5)
        cx, cy = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u - 40 * math.sin(math.pi * u)
        sc = 0.5 + 0.5 * u
        line = skia.Path()
        line.moveTo(x0, y0)
        line.quadTo((x0 + cx) / 2 + 60, (y0 + cy) / 2 + 30, cx, cy + 30 * sc)
        ink(c, line, RED, 5, 0.7)
        ink(c, cloud(cx, cy, sc), RED, 7)
        return (cx, cy)

    return fn


scene("周二：坐五分钟", "书中观点 · 冥想", (X, Y, 0.85))
day_tag(X, Y, "周二")
L(join(cushion(X, SEAT + 30, 2.4), sitter(X, SEAT, 1.15)), 1, 1.9, BLACK, 9, sfx="wood_low")
C(breath_fn(J(), X, SEAT - 150), 2, 2.6, sfx="shaker")
T("5 分钟", X - 150, Y - 388, 62, k0=3, k1=4.0, sfx="pop")
C(drift_fn(J(), X + 40, SEAT - 300, X + 390, Y - 300), 4, 6, sfx="wood_high")
L(arrow((X + 400, Y - 230), (X + 90, SEAT - 280), -0.3, 36), 5, 5.8, BLUE, 9, sfx="tom")
T("走神就拉回", X, Y + 450, 76, GREEN, k0=6, k1=7.25, sfx="ding")

# 周三：跟作者聊（X=2650, Y=6900）
X, Y = 2650, 6900


def author_fn(x, y, s):
    """书里探出来的小人（写书的人，不画具体长相）。"""
    path = stick(x, y, s, "up")

    def fn(c, k, Tm):
        sc = pop_s(k)
        if sc > 0:
            ink(c, moved(path, s=sc, ax=x, ay=y), GREEN, 8)
        return None

    return fn


scene("周三：跟作者聊", "书中观点 · 阅读", (X, Y, 0.85))
day_tag(X, Y, "周三")
L(join(stick(X - 360, Y + 380, 0.95, "hold"), book(X - 90, Y + 190, 300, 170)), 1, 1.9, BLACK, 9, sfx="wood_high")
C(author_fn(X - 20, Y + 105, 0.45), 2, 2.7, sfx="pop")
L(bubble(X - 380, Y - 170, 280, 130, 1), 3, 3.5, BLACK, 8, sfx="pop")
T("为啥？", X - 380, Y - 170, 58, k0=3.5, k1=4.3)
L(bubble(X + 130, Y - 230, 330, 130, -1), 4, 4.5, GREEN, 8, sfx="pop")
T("我这么看", X + 130, Y - 230, 58, GREEN, k0=4.5, k1=5.5)
shelf = [P((X + 300, Y + 130), (X + 590, Y + 130)), P((X + 300, Y + 330), (X + 590, Y + 330))]
for i in range(4):
    bx = X + 330 + i * 70
    shelf.append(rect(bx, Y + 70, 46, 110, 6))
    shelf.append(circle(bx, Y - 10, 18))
    shelf.append(rect(bx, Y + 270, 46, 110, 6))
L(join(*shelf), 5, 5.9, BLACK, 7, sfx="wood_low")
T("书架像朋友圈", X + 150, Y + 460, 72, GREEN, k0=6, k1=7.5, sfx="ding")
park(X + 380, Y + 460, X + 540, Y + 540, 7.5, 8.2)

# 周四：讲给自己听（X=950, Y=6900）
X, Y = 950, 6900


def layman_fn(j, x, y, s):
    """头顶气泡里的小外行：第 4 拍弹出，第 5–7 拍点头。"""

    def fn(c, k, Tm):
        sc = pop_s(k)
        if sc <= 0:
            return None
        t0, t1 = b.t_of(j, 5), b.t_of(j, 7)
        u = clamp01((Tm - t0) / max(1e-3, t1 - t0))
        dy = 14 * s * abs(math.sin(u * 3 * math.pi))
        hy = y - 290 * s
        body = join(P((x, hy + 45 * s), (x, y - 120 * s)), P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)),
                    P((x - 70 * s, hy + 170 * s), (x, hy + 80 * s), (x + 70 * s, hy + 170 * s)))
        eyes = skia.Path()
        eyes.addCircle(x - 15 * s, hy - 8 * s + dy, 3 * s)
        eyes.addCircle(x + 15 * s, hy - 8 * s + dy, 3 * s)
        ink(c, moved(join(body, circle(x, hy + dy, 45 * s), eyes), s=sc, ax=x, ay=y), ORANGE, 7)
        return None

    return fn


scene("周四：讲给自己听", "书中观点 · 写作", (X, Y, 0.85))
day_tag(X, Y, "周四")
L(stick(X - 380, Y + 430, 0.95, "point"), 1, 1.9, BLACK, 10, sfx="wood_high")
L(doc(X + 90, Y + 230, 300, 340, 5), 2, 2.9, BLACK, 9, sfx="wood_low")
L(bubble(X - 140, Y - 160, 480, 290, -1), 3, 3.7, BLACK, 8, sfx="pop")
C(layman_fn(J(), X - 250, Y - 40, 0.5), 4, 4.6, sfx="pop")
T("外行", X - 30, Y - 120, 58, ORANGE, k0=4.6, k1=5.4)
L(check(X + 0, Y - 220, 40), 5, 5.5, GREEN, 10, sfx="ding")
T("讲到外行也懂", X + 120, Y + 470, 70, GREEN, k0=6, k1=7.5, sfx="pop")
park(X + 330, Y + 470, X + 500, Y + 545, 7.5, 8.2)

# 周五：跑一圈（X=950, Y=8350）
X, Y = 950, 8350
TR = (X, Y + 20, 900, 400)      # 跑道中心与外圈宽高


def runner(x, y, s, ph) -> skia.Path:
    """跑步的小人：(x, y) 为脚底，ph 为步伐相位。"""
    hy = y - 290 * s
    sw = math.sin(ph)
    return join(circle(x - 14 * s, hy, 45 * s), P((x - 10 * s, hy + 45 * s), (x + 4 * s, y - 120 * s)),
                P((x - 60 * s * sw, y), (x + 4 * s, y - 120 * s), (x + 60 * s * sw, y - 10 * s * abs(sw))),
                P((x + 70 * s * sw, hy + 150 * s), (x - 8 * s, hy + 80 * s), (x - 70 * s * sw, hy + 140 * s)))


def run_fn(j, lead, color, s=0.48):
    """跑道上追人：第 2–7 拍沿跑道跑大半圈，小林（后面那个）越追越近，最后停在跑道前沿。"""
    cx, cy, w, h = TR
    a, bb = (w - 70) / 2, (h - 70) / 2

    def fn(c, k, Tm):
        sc = pop_s(k)
        if sc <= 0:
            return None
        t0, t1 = b.t_of(j, 2), b.t_of(j, 7)
        u = clamp01((Tm - t0) / max(1e-3, t1 - t0))
        e = ease_in_out(u)
        gap = 1.0 - 0.6 * e
        th = math.pi / 2 + 0.3 - 1.6 * math.pi * (1 - e) - (0 if lead else gap)
        px, py = cx + a * math.cos(th), cy + bb * math.sin(th)
        ph = (Tm - t0) * 14 if u < 1 else 0.6
        ink(c, moved(runner(px, py, s, ph), s=sc, ax=px, ay=py), color, 7)
        return None

    return fn


scene("周五：跑一圈", "书中观点 · 运动", (X, Y, 0.85))
day_tag(X, Y, "周五")
L(join(oval(*TR), oval(TR[0], TR[1], TR[2] - 140, TR[3] - 140)), 1, 1.9, BLACK, 9, sfx="wood_low")
C(run_fn(J(), True, ORANGE), 2, 2.5, sfx="shaker")
C(run_fn(J(), False, BLUE), 3, 3.5, sfx="wood_high")
T("当成追人游戏", X + 80, Y - 390, 66, RED, k0=4, k1=5.5, sfx="pop")
T("跑完做难事", X - 80, Y + 450, 70, GREEN, k0=6, k1=7.25, sfx="ding")
L(mini_book(X + 330, Y + 450, 0.9), 7, 7.7, GREEN, 8, sfx="pop")
park(X + 330, Y + 410, X + 500, Y + 545, 7.7, 8.4)

# 周末：复个盘（X=2650, Y=8350）
X, Y = 2650, 8350
scene("周末：复个盘", "书中观点 · 复盘", (X, Y, 0.85))
day_tag(X, Y, "周末")
L(notebook(X + 60, Y + 80, 880, 640), 1, 1.9, BLACK, 9, sfx="wood_low")
for n, (s, k0, sfx) in enumerate((("写下经过", 2, "pop"), ("问几个为什么", 4, "pop"), ("留一个行动点", 6, "ding"))):
    yy = Y - 100 + n * 180
    L(circle(X - 270, yy, 38), k0, k0 + 0.4, BLUE, 7, sfx=sfx)
    T(str(n + 1), X - 270, yy + 2, 54, BLUE, k0=k0 + 0.3, k1=k0 + 0.6)
    T(s, X + 120, yy, 66, k0=k0 + 0.5, k1=k0 + 0.5 + 0.22 * len(s))
H(7, "wood_high", 0.5, "落笔")
park(X + 330, Y + 260, X + 470, Y + 360, 7.9, 8.5)

# ---------------------------------------------------------------- 全季收尾：宝宝掌舵（场景 12）

HX, HY, HR = 1800, 9800, 470
DECK, WATER = 9900, 10080
WH = (1650, 9765, 80)           # 舵


def grips_fn(x, y, r):
    """九道旧握痕依次亮起（每道约 0.1 拍）。"""

    def fn(c, k, Tm):
        n = k * 9
        for i in range(9):
            f = clamp01(n - i)
            if f > 0:
                ink(c, grip(x, y, r, i), GREEN, 9, f)
        return None

    return fn


hull = P((HX - 380, DECK), (HX + 380, DECK), (HX + 290, DECK + 140), (HX - 290, DECK + 140), close=True)
scene("宝宝会掌舵了", "全季收尾", (HX, HY + 50, 0.8))
L(join(circle(HX, HY, HR), P((HX - 80, HY + HR - 7), (HX - 80, HY + HR + 60), (HX - 380, HY + HR + 130)),
       P((HX + 80, HY + HR - 7), (HX + 80, HY + HR + 60), (HX + 380, HY + HR + 130))), 0, 0.9, BLACK, 10, sfx="wood_low")
L(join(hull, underline(HX - 360, HX + 360, WATER + 10, 12, 50)), 1, 1.9, BLACK, 9, sfx="wood_high")
L(rower(HX + 60, DECK, 0.75, "grandpa"), 2, 2.8, BLACK, 8, sfx="tom")
L(rower(HX + 250, DECK, 0.75, "uncle"), 3, 3.8, RED, 8, sfx="tom")
L(baby(WH[0] - 140, DECK, 0.85), 4, 4.8, BLUE, 8, sfx="pop")
L(join(helm(*WH), P((WH[0], WH[1] + WH[2] * 0.3), (WH[0], DECK))), 5, 5.8, GREEN, 8, sfx="wood_high")
C(grips_fn(*WH), 6, 6.9, sfx="shaker")
L(grip(*WH, 9), 7, 7.5, RED, 12, sfx="ding")

# ---------------------------------------------------------------- 十讲连起来（场景 13）

RY = 11800
STOPS = [(1000 + 400 * i, RY - 250) for i in range(5)] + [(2600 - 400 * i, RY + 250) for i in range(5)]


def ic_brain(x, y):
    return join(circle(x, y, 60), circle(x - 28, y + 8, 13), circle(x + 2, y + 8, 13), circle(x + 30, y + 14, 8))


def ic_balloons(x, y):
    return join(oval(x - 38, y - 30, 48, 60), oval(x, y - 46, 48, 60), oval(x + 38, y - 30, 48, 60),
                P((x - 38, y), (x, y + 60)), P((x, y - 16), (x, y + 60)), P((x + 38, y), (x, y + 60)))


def ic_curve(x, y):
    p = skia.Path()
    p.moveTo(x - 50, y + 40)
    p.quadTo(x + 30, y + 40, x + 55, y - 55)
    return join(P((x - 60, y - 60), (x - 60, y + 50), (x + 65, y + 50)), p)


def ic_hourglass(x, y):
    return join(P((x - 45, y - 60), (x + 45, y - 60)), P((x - 45, y + 60), (x + 45, y + 60)),
                P((x - 35, y - 60), (x - 5, y), (x - 35, y + 60)), P((x + 35, y - 60), (x + 5, y), (x + 35, y + 60)))


def ic_windows(x, y):
    return join(rect(x - 24, y - 24, 90, 66, 8), rect(x, y, 90, 66, 8), rect(x + 24, y + 24, 90, 66, 8))


def ic_barbell(x, y):
    return join(P((x - 70, y), (x + 70, y)), rect(x - 45, y, 22, 90, 5), rect(x + 45, y, 22, 90, 5),
                rect(x - 64, y, 16, 60, 4), rect(x + 64, y, 16, 60, 4))


def ic_card(x, y):
    return join(rect(x, y, 110, 90, 10), check(x, y, 30))


def ic_note(x, y):
    return join(rect(x, y, 110, 100, 8), P((x - 35, y - 18), (x + 35, y - 18)), P((x - 35, y + 14), (x + 20, y + 14)))


def ic_eye(x, y):
    p = skia.Path()
    p.moveTo(x - 55, y)
    p.quadTo(x, y - 45, x + 55, y)
    p.quadTo(x, y + 45, x - 55, y)
    parts = [p, circle(x, y, 14)]
    for i in range(6):
        a = i / 6 * 2 * math.pi + math.pi / 6
        parts.append(P((x + math.cos(a) * 70, y + math.sin(a) * 58), (x + math.cos(a) * 92, y + math.sin(a) * 76)))
    return join(*parts)


def ic_helm(x, y):
    return join(helm(x, y, 46), grips(x, y, 46, range(10)))


EP_ICONS = (ic_brain, ic_balloons, ic_curve, ic_hourglass, ic_windows, ic_barbell, ic_card, ic_note, ic_eye, ic_helm)

route = skia.Path()
route.moveTo(STOPS[0][0] - 160, STOPS[0][1])
for (x0, y0), (x1, y1) in zip(STOPS, STOPS[1:]):
    if y0 != y1:
        route.cubicTo(x0 + 200, y0, x1 + 200, y1, x1, y1)
    else:
        route.quadTo((x0 + x1) / 2, y0 + 50, x1, y1)
route.lineTo(STOPS[-1][0] - 150, STOPS[-1][1])
dots = [circle(x, y, 16) for x, y in STOPS]

scene("十讲连起来", "十讲一条线", (1800, RY, 0.55))
L(join(route, *dots), 0, 1.0, BLUE, 8, sfx="wood_low")
for n in range(10):
    x, y = STOPS[n]
    k0 = 1 + (n // 2) if n < 9 else 6
    k0 += 0.4 * (n % 2) if n < 9 else 0
    col = GREEN if n == 9 else BLACK
    L(EP_ICONS[n](x, y - 125), k0, k0 + 0.4, col, 7, sfx=("pop" if n % 2 == 0 and n < 9 else "ding" if n == 9 else None))
    T(f"{n + 1:02d}", x, y + 85, 74, RED if n == 9 else BLUE, k0=k0 + 0.3, k1=k0 + 0.6 if n < 9 else k0 + 1.1)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 7000, 0.068)
COMMENT = (1800, 13250, 0.8)
scene("这一季讲完了", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
L(join(rect(1800, 13200, 1250, 640, 40), P((1500, 13520), (1440, 13610), (1600, 13520))), 5, 5.9, BLACK, 9,
  sfx="wood_high")
T("五件套你先试哪一件？", 1800, 13000, 66, RED, k0=6, k1=8.5, sfx="pop")
for n in range(5):
    x = 1800 + (n - 2) * 220
    L(ICONS[n](x, 13180, 0.7), 9 + 0.3 * n, 9.5 + 0.3 * n, ICON_COL[n], 7, sfx="pop" if n == 0 else None)
T("这一季讲完了", 1800, 13380, 60, k0=11, k1=13, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "five", "人生五件套", "下班后那两小时，怎么过？", ACC, b.shots,
                 [f"{BOOK}第八章“早冥读写跑，人生五件套——成本最低的成长之道”（早起、冥想、阅读、写作、运动五节）、"
                  "第七章第三节“游戏心态”、结语“一流的生活不是富有，而是觉知”（转述）"],
                 "下班后那两小时|【怎么过】", SQUARE_SHOT,
                 ["书中观点均为转述，不是逐字引文：第八章讲早起、冥想、阅读、写作、运动五件事；早起靠早睡、不靠闹钟"
                  "（节名写着无闹钟、不参团、不打卡）；读书时像在和写书的人聊天，书架像朋友圈；写作用费曼的办法，"
                  "用自己的话讲到外行也能懂；运动后一两个小时里做费脑子的事；第七章第三节游戏心态：给一件事找另一种乐趣，"
                  "书里的例子是把跑步当成追逐游戏；结语讲每天复盘：写下经过、多问几个为什么、留一个改进的行动点。",
                  "冥想一屏的“坐五分钟、走神就拉回来”是据书中思路整理的入门做法示意，“5 分钟”不是书中给定时长；"
                  "开局“21:00–23:00 两小时”、小林的一周与每天的安排均为示意，据书中思路整理，时间不是数据；不指向任何具体公司或个人。",
                  "作者周岭只写名字，不画肖像；书里探出的小人代表“写书的人”，不画具体长相；费曼只在出处说明里提名字。",
                  "脑内三兄弟（拄拐老爷爷、戴耳机大叔、抱舵宝宝）与船舵握痕为系列视觉角色，据第一章“三重大脑”与第三章"
                  "“思维舵手”的比喻；舵上十道握痕表示系列进度（第 N 讲 N 道，红色那道为本讲新增），全季收尾时宝宝掌舵、"
                  "两个哥哥划桨为示意。十讲航线上的小图标分别对应本系列第 1–10 讲。"],
                 tags="#自律 #早起")
    return b.attach(ep)
