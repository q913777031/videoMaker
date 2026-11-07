"""《丰田模式》07 现地现物：会开了三次，问题怎么还在？（白板手绘 + AI 旁白，竖屏 2:3）

倒叙：先给结果，再倒回去讲它是怎么来的。2026-11 结构：先问题（痛点 + 身边的例子），再书中做法，再办法，最后鼓励。
- 开场钩子 → 痛点：会议室门牌“第3次会”，“没解决”；三个人轮流发言，窗外的现场亮着红色警示，没人看；
- 身边的例子：围着截图猜了一下午（drop：第 2 屏门口的真用户砸出来，重击 + 震屏 + 闪白）；楼上改三版流程，
  楼下打包台贴错标签；孩子不想上学，空着一张小凳子；
- 书中做法（倒叙）：“丰田模式”书本 → 家用车剖面，杯子逐拍冒出来，“结果”印章 → 倒带键“◀◀ 倒回去”，杯子打问号；
  地图上美国、加拿大、墨西哥，小车跑一大圈；路上一家人在车里吃东西、他记在本子上 | 办公室里领导看报告，“看不到”；
- “现地现物”印章；脚印从办公楼走到车间；大野耐一在车间地上画圈，年轻员工站进去，太阳从左走到右，头顶灯泡亮；
- 传话：员工气泡里的大警示 → 组长气泡里变小变歪 → 会议室里只剩“那边有点问题”；听来的（耳朵 + 故事书）vs 看到的（眼睛 + 实物）；
- 跑一趟 = 划掉三个会；三步做法；会议时钟从一小时缩到十五分钟；评论区 + 下一讲预告（打地鼠）。
办公室里的同事小王用本模块的 draw_wang（短发、白衬衫、蓝工牌，不戴安全帽，与第 06 讲同一造型）；
安全帽造型（common.draw_worker）只用于车间员工。
文案见 fengtian/PLAN.md「### 07 现地现物」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_leader, draw_li, draw_ohno,
                             draw_worker, pop_scale, rest_hands, walk)
from whiteboard import engine as wb
from whiteboard.engine import P, book, check, circle, cross, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "身边的例子", 2),
    ([4], "身边的例子", 3),
    ([5], "身边的例子", 4),
    ([6], "倒叙 · 先看结果", 5),
    ([7, 8], "倒叙 · 倒回去", 6),
    ([9, 10], "倒叙 · 倒回去", 7),
    ([11, 12], "丰田模式 · 书中做法", 8),
    ([13, 14], "丰田模式 · 书中做法", 9),
    ([15, 16, 17], "为什么亲眼看", 10),
    ([18], "书中观点", 11),
    ([19, 20], "说回我们自己", 12),
    ([21, 22], "做法一 · 示意", 13),
    ([23], "做法二 · 示意", 14),
    ([24], "做法三 · 示意", 15),
    ([25], "更有底气", 16),
    ([26, 27, 28, 29], "评论区见", 17),
]

THEME = FT.get("07")          # 本讲样式（fengtian/theme.py）：淡粉信纸、开场 doorsign、转场 swing
L = C.Lesson("07", SCREENS, drop_screen=2, board_size=(5000, 13000), theme=THEME)
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

# 各屏在白板上的区块中心（相邻屏相距 1600，蛇形排列）
R = [(2600, 800), (900, 900), (900, 2500), (2500, 2500), (4100, 2500), (4100, 4100), (2500, 4100), (900, 4100),
     (900, 5700), (2500, 5700), (4100, 5700), (4100, 7300), (2500, 7300), (900, 7300), (900, 8900), (2500, 8900),
     (4100, 8900), (4100, 10500)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 12——亲临现场，彻底了解情况（现地现物 genchi genbutsu）。书中讲塞纳（Sienna）改款时，总工程师横谷雄二"
    "开车跑遍美国、加拿大和墨西哥，发现北美家庭常在车里吃喝，于是加了许多杯架等；大野耐一在车间地上画圈，让年轻工程师站在圈里看。",
    "车型剖面、地图轮廓、路线均为示意；小李、小王、组长、领导为虚构人物。",
]

GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL = "#8A8F99", "#ECEEF1", "#D3EDDC", "#F6C3BE", "#D5E3F7"
WOOD, NOTE_FILL, SKY = "#E3C9A0", "#FFF1A8", "#E4EEF8"


def nbeats(j):
    return L.BOUNDS[j][1] - L.BOUNDS[j][0]


def kq(j, t_local, lo=0):
    """kb，但 lo 超出本屏时夹到最后一拍（排期变短时不报错）。"""
    return kb(j, t_local, lo=min(lo, nbeats(j) - 1))


def nx(j, t_local, prev, gap=1):
    """离 t_local 最近、且至少在 prev 之后 gap 拍的拍号。"""
    return max(kq(j, t_local, prev + gap), prev + gap)


# ================================================================ 小工具

def pop_fn(j, k, draw, dur=0.32):
    """第 j 屏第 k 拍弹出：draw(c, sc, T)。"""
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k), dur)
        if sc > 0:
            draw(c, sc, T)
        return None
    return fn


@contextmanager
def at_pop(c, x, y, sc):
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    c.translate(-x, -y)
    try:
        yield
    finally:
        c.restore()


def ev(j, k, fn, sfx=None, gain=0.8, dur=0.3):
    b.custom(j, k, k + dur, fn, sfx=sfx, gain=gain)


def box(c, x, y, w, h, fill, line, width=6, r=14, alpha=1.0):
    rr = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(rr, r, r, K.paint(fill, alpha))
    c.drawRoundRect(rr, r, r, wb.marker(line, width, alpha))


def dashed(c, a, z, color, width, alpha=1.0, on=18, off=12):
    p = K.paint(color, alpha, width)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    c.drawLine(a[0], a[1], z[0], z[1], p)


def dashed_path(c, path, color, width, alpha=1.0, on=22, off=16):
    p = K.paint(color, alpha, width)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    c.drawPath(path, p)


def head_of(x, y, s):
    return x, y - 290 * s


def qmark(c, x, y, size, color, alpha=1.0):
    K.text(c, "？", x, y, size, "hand", color, alpha)


def label(j, k, s, x, y, size=60, color=BLACK, sfx=None, gain=0.6):
    """第 j 屏第 k 拍弹出一个小标签。"""
    b.custom(j, k, k + 0.3, L.pop_text(s, x, y, size, color, j, k), sfx=sfx, gain=gain)


def plate(c, x, y, s, color=BLACK, fill="#FFFFFF", w=300, h=110, size=64):
    """门牌：木框白底 + 字。"""
    box(c, x, y, w, h, fill, color, 7, 14)
    K.text(c, s, x, y + 2, size, "hand", color)


def cup(c, x, y, s=1.0, color=BLUE, fill="#DCEAFB"):
    """外带饮料杯（带盖和吸管）：(x, y) 为杯底中点。"""
    body = P((x - 26 * s, y - 80 * s), (x + 26 * s, y - 80 * s), (x + 19 * s, y), (x - 19 * s, y), close=True)
    c.drawPath(body, K.paint(fill))
    c.drawPath(body, wb.marker(color, 6))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 32 * s, y - 96 * s, 64 * s, 18 * s), 7, 7, K.paint("#FFFFFF"))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 32 * s, y - 96 * s, 64 * s, 18 * s), 7, 7, wb.marker(color, 5))
    C.line(c, (x + 4 * s, y - 96 * s), (x + 16 * s, y - 132 * s), RED, 6)


def burger(c, x, y, s=1.0):
    """汉堡：(x, y) 为中心。"""
    top = skia.Path()
    top.addArc(skia.Rect.MakeXYWH(x - 42 * s, y - 40 * s, 84 * s, 64 * s), 180, 180)
    top.close()
    c.drawPath(top, K.paint("#E9B060"))
    c.drawPath(top, wb.marker("#A9773E", 5))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 44 * s, y - 8 * s, 88 * s, 12 * s), 6, 6, K.paint("#6AA84F"))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 42 * s, y + 4 * s, 84 * s, 16 * s), 6, 6, K.paint("#7A4A2A"))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 40 * s, y + 20 * s, 80 * s, 16 * s), 8, 8, K.paint("#E9B060"))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 40 * s, y + 20 * s, 80 * s, 16 * s), 8, 8, wb.marker("#A9773E", 4))


def eye(c, x, y, s=1.0, color=BLUE, alpha=1.0, look=0.0):
    """一只大眼睛：(x, y) 为中心，宽约 200·s。"""
    p = skia.Path()
    p.moveTo(x - 100 * s, y)
    p.quadTo(x, y - 90 * s, x + 100 * s, y)
    p.quadTo(x, y + 90 * s, x - 100 * s, y)
    p.close()
    c.drawPath(p, K.paint("#FFFFFF", alpha))
    c.drawPath(p, wb.marker(color, 8, alpha))
    c.drawCircle(x + look * 30 * s, y, 34 * s, K.paint(color, alpha))
    c.drawCircle(x + look * 30 * s, y, 15 * s, K.paint(BLACK, alpha))
    c.drawCircle(x + look * 30 * s + 10 * s, y - 10 * s, 6 * s, K.paint("#FFFFFF", alpha))


def ear(c, x, y, s=1.0, color=ORANGE):
    """耳朵：(x, y) 为中心，高约 200·s。"""
    p = skia.Path()
    p.moveTo(x - 20 * s, y + 90 * s)
    p.cubicTo(x - 90 * s, y + 40 * s, x - 90 * s, y - 100 * s, x, y - 100 * s)
    p.cubicTo(x + 80 * s, y - 100 * s, x + 90 * s, y - 10 * s, x + 30 * s, y + 30 * s)
    p.cubicTo(x + 5 * s, y + 50 * s, x + 20 * s, y + 100 * s, x - 20 * s, y + 90 * s)
    c.drawPath(p, K.paint("#FBE3CF"))
    c.drawPath(p, wb.marker(color, 8))
    q = skia.Path()
    q.moveTo(x - 30 * s, y + 20 * s)
    q.cubicTo(x - 45 * s, y - 50 * s, x + 40 * s, y - 70 * s, x + 30 * s, y - 10 * s)
    c.drawPath(q, wb.marker(color, 6))


def foot(c, x, y, rot, s=1.0, color=GRAY, alpha=1.0):
    """一只脚印：(x, y) 为中心，rot 为朝向角度（0 = 朝上）。"""
    with K.at(c, x, y, rot):
        c.drawOval(skia.Rect.MakeXYWH(-17 * s, -18 * s, 34 * s, 48 * s), K.paint(color, alpha))
        c.drawOval(skia.Rect.MakeXYWH(-13 * s, -44 * s, 26 * s, 22 * s), K.paint(color, alpha))


def factory_path(x, y, w=300, h=230):
    """车间：锯齿屋顶 + 烟囱 + 大门。(x, y) 为底边中点。"""
    x0, x1 = x - w / 2, x + w / 2
    top = y - h
    pts = [(x0, y), (x0, top + 60)]
    n = 3
    for i in range(n):
        a = x0 + w * i / n
        pts += [(a + w / n, top), (a + w / n, top + 60)]
    pts += [(x1, y)]
    return wb.join(P(*pts), P((x1 - 70, top + 60 - 0), (x1 - 70, top - 70), (x1 - 30, top - 70), (x1 - 30, top + 20)),
                   P((x - 45, y), (x - 45, y - 100), (x + 45, y - 100), (x + 45, y)))


def warn(c, x, y, r, color=RED, rot=0.0, alpha=1.0):
    """警示三角（!）：(x, y) 为中心，r 为外接圆半径。"""
    with K.at(c, x, y, rot):
        p = P((0, -r), (r * 0.9, r * 0.6), (-r * 0.9, r * 0.6), close=True)
        c.drawPath(p, K.paint("#FFE2DE", alpha))
        c.drawPath(p, wb.marker(color, max(4, r * 0.09), alpha))
        K.text(c, "!", 0, r * 0.12, r * 0.95, "black", color, alpha)


def sparkle(c, x, y, dt, color=YELLOW, n=8, r0=40, r1=130):
    """放射短线（亮了 / 挺直），dt 为距触发的秒数。"""
    if dt < 0 or dt > 0.9:
        return
    f = ease_out(clamp01(dt / 0.5))
    a = 1 - clamp01((dt - 0.5) / 0.4)
    for i in range(n):
        ang = 2 * math.pi * i / n
        r_a, r_b = lerp(r0, r1 * 0.7, f), lerp(r0 + 20, r1, f)
        C.line(c, (x + math.cos(ang) * r_a, y + math.sin(ang) * r_a), (x + math.cos(ang) * r_b, y + math.sin(ang) * r_b),
               color, 7, a)


def bubble_box(c, x, y, w, h, tail=-1, alpha=1.0, fill="#FFFFFF"):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 40, 40, K.paint(fill, alpha))
    c.drawPath(wb.bubble(x, y, w, h, tail), wb.marker(BLACK, 7, alpha))


# ================================================================ 本讲人物

WANG_SHIRT, HAIR = "#FFFFFF", "#2E2A28"


def draw_wang(c, x, y, s, lh=None, rh=None, mood="flat", head_dx=0.0, alpha=1.0):
    """同事小王（办公室）：齐耳短发 + 橙色发卡、白衬衫蓝描边、蓝工牌、蓝色四肢；不戴安全帽（与第 06 讲同一造型）。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, ft, BLUE, 10, alpha)
    C.line(c, sh, lh, BLUE, 10, alpha)
    C.line(c, sh, rh, BLUE, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 42 * s, hy + 55 * s, x + 42 * s, y - 105 * s)
    c.drawRoundRect(torso, 18 * s, 18 * s, K.paint(WANG_SHIRT, alpha))
    c.drawRoundRect(torso, 18 * s, 18 * s, wb.marker(BLUE, 7, alpha))
    c.drawPath(P((x - 16 * s, hy + 58 * s), (x, hy + 82 * s), (x + 16 * s, hy + 58 * s)), wb.marker(BLUE, 5, alpha))
    badge = skia.Rect.MakeXYWH(x - 20 * s, hy + 110 * s, 40 * s, 30 * s)
    c.drawRoundRect(badge, 4, 4, K.paint("#DCE8F7", alpha))
    c.drawRoundRect(badge, 4, 4, wb.marker(BLUE, 4, alpha))
    hx = x + head_dx
    back = skia.Rect.MakeLTRB(hx - 54 * s, hy - 46 * s, hx + 54 * s, hy + 40 * s)
    c.drawRoundRect(back, 26 * s, 26 * s, K.paint(HAIR, alpha))
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(hx - 50 * s, hy - 52 * s, 100 * s, 72 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint(HAIR, alpha))
    c.drawCircle(hx + 36 * s, hy - 24 * s, 9 * s, K.paint(ORANGE, alpha))
    C._eyes_mouth(c, hx, hy + 4 * s, s, mood, alpha)


def eng_head(c, x, y, s, alpha=1.0, mood="smile"):
    """总工程师的头：绿色鸭舌帽（帽檐朝前）+ 灰鬓角。(x, y) 为头中心。"""
    c.drawCircle(x, y, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, y, 45 * s, wb.marker(BLACK, 9, alpha))
    C._eyes_mouth(c, x + 6 * s, y + 2 * s, s, mood, alpha)
    cap = skia.Path()
    cap.addArc(skia.Rect.MakeXYWH(x - 48 * s, y - 70 * s, 96 * s, 80 * s), 180, 180)
    cap.close()
    c.drawPath(cap, K.paint(GREEN, alpha))
    c.drawPath(cap, wb.marker(BLACK, 6, alpha))
    C.line(c, (x + 20 * s, y - 30 * s), (x + 82 * s, y - 24 * s), BLACK, 9, alpha)
    C.line(c, (x - 44 * s, y - 14 * s), (x - 40 * s, y + 10 * s), "#8A8F99", 8, alpha)


def car_side(c, x, y, w, T, color=RED, driver=True, alpha=1.0):
    """家用车侧视（朝右）：(x, y) 为地面中点；T 用来转轮子；driver=True 时驾驶座上是总工程师。"""
    s = w / 520
    h = 220 * s
    body = skia.Path()
    body.moveTo(x - w / 2, y - 40 * s)
    body.lineTo(x - w / 2, y - h + 30 * s)
    body.quadTo(x - w / 2, y - h, x - w / 2 + 40 * s, y - h)
    body.lineTo(x + w * 0.18, y - h)
    body.lineTo(x + w * 0.36, y - 120 * s)
    body.lineTo(x + w / 2 - 10 * s, y - 105 * s)
    body.quadTo(x + w / 2, y - 100 * s, x + w / 2, y - 80 * s)
    body.lineTo(x + w / 2, y - 40 * s)
    body.close()
    c.drawPath(body, K.paint(RED_FILL if color == RED else BLUE_FILL, alpha))
    c.drawPath(body, wb.marker(color, 8, alpha))
    win = P((x - w / 2 + 40 * s, y - h + 25 * s), (x + w * 0.16, y - h + 25 * s), (x + w * 0.31, y - 128 * s),
            (x - w / 2 + 40 * s, y - 128 * s), close=True)
    c.drawPath(win, K.paint(SKY, alpha))
    c.drawPath(win, wb.marker(color, 6, alpha))
    C.line(c, (x - w * 0.08, y - h + 25 * s), (x - w * 0.08, y - 128 * s), color, 6, alpha)
    if driver:
        c.save()
        c.clipPath(win, doAntiAlias=True)
        eng_head(c, x + w * 0.06, y - 180 * s, s * 0.95, alpha)
        c.restore()
        c.drawCircle(x + w * 0.2, y - 150 * s, 22 * s, wb.marker(BLACK, 6, alpha))
    for wx in (x - w * 0.3, x + w * 0.3):
        c.drawCircle(wx, y - 40 * s, 44 * s, K.paint("#3A3F48", alpha))
        c.drawCircle(wx, y - 40 * s, 20 * s, K.paint("#FFFFFF", alpha))
        a = T * 9
        for d in (0, math.pi / 2):
            C.line(c, (wx + math.cos(a + d) * 20 * s, y - 40 * s + math.sin(a + d) * 20 * s),
                   (wx - math.cos(a + d) * 20 * s, y - 40 * s - math.sin(a + d) * 20 * s), "#3A3F48", 4, alpha)


def draw_kid(c, x, y, s, alpha=1.0, droop=1.0):
    """背书包的孩子（低着头）：(x, y) 为脚底，身高约 330·s。droop 0–1 为低头程度。"""
    hy = y - 270 * s + 18 * s * droop
    hip = (x, y - 110 * s)
    sh = (x, y - 200 * s)
    bag = skia.Rect.MakeXYWH(x - 85 * s, y - 215 * s, 60 * s, 100 * s)
    c.drawRoundRect(bag, 14 * s, 14 * s, K.paint("#F6B26B", alpha))
    c.drawRoundRect(bag, 14 * s, 14 * s, wb.marker(ORANGE, 6, alpha))
    for ft in ((x - 40 * s, y), (x + 40 * s, y)):
        C.line(c, hip, ft, BLACK, 9, alpha)
    C.line(c, (x, hy + 45 * s), hip, BLACK, 9, alpha)
    C.line(c, sh, (x - 45 * s, y - 120 * s), BLACK, 9, alpha)
    C.line(c, sh, (x + 45 * s, y - 120 * s), BLACK, 9, alpha)
    C.line(c, (x - 30 * s, y - 195 * s), (x - 30 * s, y - 125 * s), ORANGE, 6, alpha)
    c.drawCircle(x, hy, 48 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 48 * s, wb.marker(BLACK, 8, alpha))
    for dx in (-15, 15):
        C.line(c, (x + dx * s - 7 * s, hy + 6 * s * droop), (x + dx * s + 7 * s, hy + 6 * s * droop), BLACK, 5, alpha)
    m = skia.Path()
    m.addArc(skia.Rect.MakeXYWH(x - 12 * s, hy + 20 * s, 24 * s, 16 * s), 200, 140)
    c.drawPath(m, wb.marker(BLACK, 5, alpha))
    tuft = P((x - 10 * s, hy - 46 * s), (x - 2 * s, hy - 70 * s), (x + 8 * s, hy - 48 * s))
    c.drawPath(tuft, wb.marker(BLACK, 6, alpha))


def draw_mom(c, x, y, s, lh=None, rh=None, mood="flat", alpha=1.0):
    """家长（妈妈）：长发 + 红色连衣裙。(x, y) 为脚底，身高约 330·s。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    for ft in ((x - 35 * s, y), (x + 35 * s, y)):
        C.line(c, (ft[0] * 0.6 + x * 0.4, y - 90 * s), ft, BLACK, 9, alpha)
    dress = P((x - 32 * s, hy + 55 * s), (x + 32 * s, hy + 55 * s), (x + 75 * s, y - 80 * s), (x - 75 * s, y - 80 * s),
              close=True)
    c.drawPath(dress, K.paint(RED_FILL, alpha))
    c.drawPath(dress, wb.marker(RED, 7, alpha))
    C.line(c, sh, lh, BLACK, 9, alpha)
    C.line(c, sh, rh, BLACK, 9, alpha)
    hair = skia.Rect.MakeLTRB(x - 55 * s, hy - 50 * s, x + 55 * s, hy + 75 * s)
    c.drawRoundRect(hair, 30 * s, 30 * s, K.paint(HAIR, alpha))
    c.drawCircle(x, hy, 44 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 44 * s, wb.marker(BLACK, 8, alpha))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(x - 48 * s, hy - 52 * s, 96 * s, 64 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint(HAIR, alpha))
    C._eyes_mouth(c, x, hy + 6 * s, s, mood, alpha)


def draw_user(c, x, y, s, scratch=0.0, alpha=1.0):
    """真用户：绿色卫衣 + 手机；scratch>0 时挠头（scratch 为挠头动作相位秒数）。"""
    d_lh, d_rh = rest_hands(x, y, s)
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, ft, "#3A3F48", 11, alpha)
    torso = skia.Rect.MakeLTRB(x - 46 * s, hy + 50 * s, x + 46 * s, y - 100 * s)
    c.drawRoundRect(torso, 20 * s, 20 * s, K.paint(GREEN_FILL, alpha))
    c.drawRoundRect(torso, 20 * s, 20 * s, wb.marker(GREEN, 7, alpha))
    rh = (x + 40 * s, hy - 40 * s + 8 * math.sin(scratch * 18)) if scratch > 0 else d_rh
    lh = (x - 60 * s, hy + 130 * s)
    C.line(c, sh, rh, GREEN, 10, alpha)
    C.line(c, sh, lh, GREEN, 10, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(lh[0] - 18 * s, lh[1] - 30 * s, 36 * s, 60 * s), 6, 6, K.paint("#3A3F48", alpha))
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    C._eyes_mouth(c, x, hy, s, "sad" if scratch > 0 else "flat", alpha)
    for dx in (-30, -10, 10, 30):
        C.line(c, (x + dx * s, hy - 44 * s), (x + dx * s * 1.2, hy - 62 * s), BLACK, 6, alpha)


# ================================================================ 屏 0：系列开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：会议室——门牌第 1 → 3 次会，“没解决”；三人轮流发言，窗外现场亮红灯没人看
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
PEOPLE1 = [(draw_li, cx - 300), (draw_boss, cx), (draw_wang, cx + 300)]
FY1, S1 = cy + 360, 0.75
k_ppl = 0
k_cnt = [kq(j, wt(0, 1, 0.0), 1)]
k_cnt += [k_cnt[0] + 1, k_cnt[0] + 2]
k_no = nx(j, wt(0, 2, 0.5), k_cnt[2])
k_bub = [nx(j, wt(1, 0, 0.0), k_no)]
k_bub += [k_bub[0] + 1, k_bub[0] + 2]
k_look = nx(j, wt(1, 1, 0.55), k_bub[2])
L.note("第1次会", "第2次会", "第3次会", "现场", "没人看")


def table1(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, FY1, sc):
        for i, (draw, x) in enumerate(PEOPLE1):
            hx, hy = head_of(x, FY1, S1)
            talking = tb(1, k_bub[i]) <= T < tb(1, k_bub[i]) + 1.4
            rh = (x + 90 * S1, hy + 20 * S1 + 10 * math.sin(T * 9)) if talking else None
            mood = "sad" if T >= tb(1, k_no) and not talking else "flat"
            draw(c, x, FY1, S1, rh=rh, mood=mood)
        tab = skia.Rect.MakeXYWH(cx - 430, FY1 - 130, 860, 170)
        c.drawOval(tab, K.paint(WOOD))
        c.drawOval(tab, wb.marker("#A9773E", 8))
        for i, x in enumerate((cx - 260, cx + 40, cx + 290)):
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 40, FY1 - 70, 80, 56), 6, 6, K.paint("#FFFFFF"))
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 40, FY1 - 70, 80, 56), 6, 6, wb.marker(GRAY, 4))
    return None


ev(j, k_ppl, pop_fn(j, k_ppl, table1), "wood_low", 0.7)


def plate1(c, kk, T, cx=cx, cy=cy):
    n = sum(1 for k_ in k_cnt if T >= tb(1, k_))
    if n == 0:
        return None
    dt = T - tb(1, k_cnt[n - 1])
    sc = C.slam_scale(dt) if n == 3 else pop_scale(dt, 0.22)
    with K.at(c, cx - 330, cy - 470, -3 if n == 3 else 0, sc):
        plate(c, 0, 0, f"第{n}次会", RED if n == 3 else BLACK)
    return None


ev(j, k_cnt[0], plate1, "wood_high", 0.7)
b.hit(j, k_cnt[1], "wood_high", 0.7, "门牌翻到第2次会")
b.hit(j, k_cnt[2], "rim", 0.85, "门牌砸到第3次会")
ev(j, k_no, L.stamp("没解决", cx - 300, cy - 300, 80, j, k_no, rot=-6), "kick", 0.9)
b.shots[j].shake = [(k_no, 9.0)]


def window1(c, kk, T, cx=cx, cy=cy):
    """右上角窗外的现场：小机器上的警示灯一直闪。"""
    sc = pop_scale(T - tb(1, k_ppl))
    if sc <= 0:
        return None
    x, y = cx + 330, cy - 400
    with at_pop(c, x, y, sc):
        box(c, x, y, 300, 220, SKY, BLACK, 8, 10)
        C.line(c, (x, y - 110), (x, y + 110), BLACK, 6)
        box(c, x - 10, y + 50, 150, 80, GRAY_FILL, GRAY, 5, 8)
        c.drawPath(factory_path(x + 90, y + 90, 90, 70), wb.marker(GRAY, 4))
        on = 0.5 + 0.5 * math.sin(T * 8)
        c.drawCircle(x - 10, y - 20, 22, K.paint(RED, 0.35 + 0.65 * on))
        c.drawCircle(x - 10, y - 20, 22, wb.marker(RED, 4))
        K.text(c, "现场", x - 200, y - 70, 48, "hand", GRAY)
    return None


b.custom(j, k_ppl, k_ppl + 0.3, window1)


def bubbles1(c, kk, T, cx=cx, cy=cy):
    for i, (_, x) in enumerate(PEOPLE1):
        sc = pop_scale(T - tb(1, k_bub[i]))
        if sc <= 0:
            continue
        y = cy - 60
        with at_pop(c, x, y, sc):
            bubble_box(c, x, y, 230, 130, -1 if i < 2 else 1)
            for r in range(3):
                C.line(c, (x - 75, y - 30 + r * 30), (x + 75 - (r % 2) * 40, y - 30 + r * 30), GRAY, 7)
    return None


ev(j, k_bub[0], bubbles1, "pop", 0.65)
b.hit(j, k_bub[1], "pop", 0.65, "领导的气泡")
b.hit(j, k_bub[2], "pop", 0.65, "小王的气泡")


def look1(c, kk, T, cx=cx, cy=cy):
    t0 = tb(1, k_look)
    if T < t0:
        return None
    x, y = cx + 330, cy - 225
    sc = C.slam_scale(T - t0)
    with K.at(c, x + 10, y - 0, 4, sc):
        K.text(c, "没人看", 0, 0, 74, "hand", RED)
    return None


ev(j, k_look, look1, "rim", 0.8)

# ================================================================ 屏 2（drop）：会议室围着截图猜了一下午；drop 时门口的真用户砸出来
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD2 = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD2, 16.0)], [(KD2, 0.45)]
FY9, S9 = cy + 430, 0.75
P9 = [(draw_li, cx - 420), (draw_wang, cx - 150), (draw_boss, cx + 120)]
k_ppl9 = [0, 1, 2]
k_q9 = min(nx(j, wt(3, 1, 0.1), 3), KD2 - 3)
k_shot = min(nx(j, wt(3, 0, 0.3), 2), k_q9 - 1)
k_user = KD2
L.note("真用户", "难用", "？")


def ppl9(i):
    draw, x = P9[i]

    def fn(c, sc, T, cx=cx, cy=cy):
        hx, hy = head_of(x, FY9, S9)
        guess = T >= tb(2, k_q9 + i * 0.0) and T >= tb(2, min(k_q9 + i, k_q9 + 2))
        rh = (hx + 40 * S9, hy - 30 * S9 + 6 * math.sin(T * 12 + i)) if guess else None
        with at_pop(c, x, FY9, sc):
            draw(c, x, FY9, S9, rh=rh, mood="sad" if guess else "flat")
            if guess:
                g = pop_scale(T - tb(2, k_q9 + i))
                with K.at(c, hx + 20, hy - 110, 0, g):
                    qmark(c, 0, 0, 90, BLUE)
        return None
    return fn


for i in range(3):
    ev(j, k_ppl9[i], pop_fn(j, k_ppl9[i], ppl9(i)), ("wood_low", "wood_high", "wood_low")[i], 0.6)


def screen9(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 150, cy - 330
    with at_pop(c, x, y, sc):
        box(c, x, y, 560, 330, "#2F3542", BLACK, 8, 14)
        box(c, x, y, 220, 280, "#FFFFFF", GRAY, 5, 20)
        for r in range(3):
            C.line(c, (x - 70, y - 80 + r * 40), (x + 70 - r * 20, y - 80 + r * 40), "#C9CED6", 8)
        box(c, x, y + 80, 140, 50, RED_FILL, RED, 5, 10)
        K.text(c, "难用", x + 200, y - 100, 52, "hand", RED)
    return None


ev(j, k_shot, pop_fn(j, k_shot, screen9), "pop", 0.7)


def clock9(c, kk, T, cx=cx, cy=cy):
    x, y = cx + 420, cy - 430
    sc = pop_scale(T - tb(2, 0))
    if sc <= 0:
        return None
    with K.at(c, x, y, 0, sc):
        c.drawCircle(0, 0, 80, K.paint("#FFFFFF"))
        c.drawCircle(0, 0, 80, wb.marker(BLACK, 8))
        spin = clamp01((T - tb(2, k_q9)) / (tb(2, k_q9 + 3) - tb(2, k_q9))) if T >= tb(2, k_q9) else 0.0
        a_m = -math.pi / 2 + spin * 2 * math.pi * 4
        a_h = -math.pi / 2 + math.pi / 6 * 2 + spin * math.pi * 2 / 3
        C.line(c, (0, 0), (math.cos(a_m) * 60, math.sin(a_m) * 60), BLACK, 6)
        C.line(c, (0, 0), (math.cos(a_h) * 40, math.sin(a_h) * 40), RED, 8)
    return None


b.custom(j, 0, 0.3, clock9)
for i in range(3):
    b.hit(j, k_q9 + i, ("pop", "pop", "wood_high")[i], 0.6, "头顶冒问号")


def door9(c, sc, T, cx=cx, cy=cy):
    x = cx + 420
    with at_pop(c, x, FY9, sc):
        box(c, x, FY9 - 200, 220, 400, "#F7F3EC", "#A9773E", 8, 6)
        dt = T - tb(2, k_user)
        draw_user(c, x, FY9 - 10, 0.72, scratch=dt + 0.01 if dt > 0.35 else 0.0)
        K.text(c, "真用户", x, FY9 - 470, 56, "hand", GREEN)
    return None


ev(j, k_user, pop_fn(j, k_user, door9), "kick", 0.95)

# ================================================================ 屏 3：楼上改三版流程（小王在白板前），楼下打包台贴错标签，没人下去看
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_pack = 0
k_wrong = nx(j, wt(4, 0, 0.6), k_pack)
k_v = [nx(j, wt(4, 1, 0.1), k_wrong)]
k_v += [k_v[0] + 1, k_v[0] + 2]
k_nogo = nx(j, wt(4, 2, 0.4), k_v[2])
WB10 = (cx + 90, cy - 330, 800, 330)
L.note("楼上", "楼下", "1版", "2版", "3版", "发错")


def floor10(c, kk, T, cx=cx, cy=cy):
    f = ease_out(clamp01((T - tb(3, k_pack)) / 0.4))
    if f <= 0:
        return None
    C.line(c, (cx - 600, cy - 70), (cx - 600 + 1200 * f, cy - 70), BLACK, 8)
    sc = pop_scale(T - tb(3, k_pack))
    with K.at(c, cx - 545, cy - 115, 0, sc):
        K.text(c, "楼上", 0, 0, 46, "hand", GRAY)
    with K.at(c, cx - 545, cy - 25, 0, sc):
        K.text(c, "楼下", 0, 0, 46, "hand", GRAY)
    return None


b.custom(j, k_pack, k_pack + 0.3, floor10)


def pack10(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 120, cy + 300
    with at_pop(c, x, y, sc):
        c.drawRect(skia.Rect.MakeXYWH(x - 330, y, 660, 34), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(x - 330, y, 660, 34), wb.marker("#A9773E", 6))
        for lx in (x - 300, x + 300):
            C.line(c, (lx, y + 34), (lx, y + 160), "#A9773E", 8)
        for i, bx in enumerate((x - 210, x, x + 210)):
            box(c, bx, y - 70, 170, 140, "#E6CFA8", "#A9773E", 6, 6)
            wrong = i == 1 and T >= tb(3, k_wrong)
            box(c, bx, y - 80, 90, 50, RED_FILL if wrong else "#FFFFFF", RED if wrong else GRAY, 4, 4)
            if wrong:
                f = clamp01((T - tb(3, k_wrong)) / 0.3)
                ring = skia.Path()
                ring.addOval(skia.Rect.MakeXYWH(bx - 90, y - 160, 180, 160))
                part, _ = wb.partial(ring, f)
                c.drawPath(part, wb.marker(RED, 8))
    return None


ev(j, k_pack, pop_fn(j, k_pack, pack10), "wood_low", 0.7)
b.hit(j, k_wrong, "rim", 0.8, "中间那箱标签贴错")
b.custom(j, k_wrong + 0.3, k_wrong + 0.6, L.pop_text("发错", cx - 120, cy + 510, 70, RED, j, k_wrong + 0.3))


def worker10(c, sc, T, cx=cx, cy=cy):
    x, y, s = cx + 380, cy + 440, 0.8
    hx, hy = head_of(x, y, s)
    with at_pop(c, x, y, sc):
        draw_worker(c, x, y, s, lh=(x - 120 * s, hy + 130 * s + 10 * math.sin(T * 7)), mood="sad")
    return None


ev(j, k_pack + 1, pop_fn(j, k_pack + 1, worker10), "pop", 0.6)


def wb10(c, kk, T, cx=cx, cy=cy):
    x, y, w, h = WB10
    sc = pop_scale(T - tb(3, k_v[0]))
    if sc <= 0:
        return None
    with at_pop(c, x, y, sc):
        box(c, x, y, w, h, "#FFFFFF", GRAY, 8, 10)
        for v in range(3):
            t0 = tb(3, k_v[v])
            if T < t0:
                continue
            vx = x - 260 + v * 260
            f = clamp01((T - t0) / 0.4)
            K.text(c, f"{v + 1}版", vx, y - 120, 46, "hand", BLUE)
            for r in range(3):
                if f * 3 > r:
                    box(c, vx, y - 50 + r * 75, 130, 46, BLUE_FILL, BLUE, 4, 8)
            if v < 2 and T >= tb(3, k_v[v + 1]):
                g = clamp01((T - tb(3, k_v[v + 1])) / 0.2)
                part, _ = wb.partial(cross(vx, y + 20, 80), g)
                c.drawPath(part, wb.marker(RED, 9))
    return None


ev(j, k_v[0], wb10, "wood_high", 0.6)
b.hit(j, k_v[1], "wood_high", 0.6, "第2版流程，第1版划掉")
b.hit(j, k_v[2], "wood_low", 0.6, "第3版流程，第2版划掉")


def wang10(c, sc, T, cx=cx, cy=cy):
    x, y, s = cx - 400, cy - 100, 0.6
    hx, hy = head_of(x, y, s)
    with at_pop(c, x, y, sc):
        draw_wang(c, x, y, s, rh=(x + 130 * s, hy + 10 * s + 20 * math.sin(T * 5)))
    return None


ev(j, k_v[0], pop_fn(j, k_v[0], wang10))


def nogo10(c, kk, T, cx=cx, cy=cy):
    t0 = tb(3, k_nogo)
    if T < t0:
        return None
    f = clamp01((T - t0) / 0.35)
    a, z = (cx + 90, cy - 150), (cx + 90, cy + 140)
    dashed(c, a, (a[0], lerp(a[1], z[1], f)), GRAY, 7)
    g = pop_scale(T - t0 - 0.2)
    if g > 0:
        with K.at(c, cx + 90, cy + 10, 0, g):
            c.drawPath(cross(0, 0, 42), wb.marker(RED, 10))
    return None


ev(j, k_nogo, nogo10, "kick", 0.8)
b.shots[j].shake = [(k_nogo, 8.0)]

# ================================================================ 屏 4：孩子不想上学；两个大人轮流讲道理；空着一张小凳子
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
KID = (cx - 40, cy + 430, 0.6)
STOOL = (cx + 150, cy + 430)
k_kid = 0
k_p1 = 1
k_p2 = 2
k_say = [nx(j, wt(5, 1, 0.0), k_p2)]
k_say += [k_say[0] + 1, k_say[0] + 2]
k_stool = nx(j, wt(5, 2, 0.6), k_say[2])
SAYS = [("要用功", cx - 330, cy - 120, -1), ("别贪玩", cx + 320, cy - 200, 1), ("听话", cx - 300, cy - 360, -1)]
L.note("要用功", "别贪玩", "听话", "空着")


def kid11(c, sc, T):
    x, y, s = KID
    with at_pop(c, x, y, sc):
        draw_kid(c, x, y, s, droop=1.0)
    return None


ev(j, k_kid, pop_fn(j, k_kid, kid11), "pop", 0.6)


def parent11(i):
    def fn(c, sc, T, cx=cx, cy=cy):
        x, y, s = (cx - 420, cy + 430, 0.85) if i == 0 else (cx + 420, cy + 430, 0.85)
        hx, hy = head_of(x, y, s)
        mine = [n for n, (_, _, _, side) in enumerate(SAYS) if (side < 0) == (i == 0)]
        active = any(tb(4, k_say[n]) <= T < tb(4, k_say[n]) + 0.9 for n in mine)
        sgn = 1 if i == 0 else -1
        hand = (x + sgn * 130 * s, hy + 10 * s + (12 * math.sin(T * 14) if active else 0))
        with at_pop(c, x, y, sc):
            if i == 0:
                draw_li(c, x, y, s, "flat", rh=hand)
            else:
                draw_mom(c, x, y, s, lh=hand)
        return None
    return fn


ev(j, k_p1, pop_fn(j, k_p1, parent11(0)), "wood_low", 0.6)
ev(j, k_p2, pop_fn(j, k_p2, parent11(1)), "wood_high", 0.6)
for n, (s_, x, y, side) in enumerate(SAYS):
    ev(j, k_say[n], L.pop_bubble(s_, x, y, j, k_say[n], 66, BLACK, tail=side), ("pop", "pop", "rim")[n], 0.7)


def stool11(c, kk, T, cx=cx, cy=cy):
    x, y = STOOL
    sc = pop_scale(T - tb(4, k_kid))
    if sc <= 0:
        return None
    hl = T >= tb(4, k_stool)
    col = GREEN if hl else "#A9773E"
    with at_pop(c, x, y, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 60, y - 110, 120, 24), 8, 8, K.paint(WOOD))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 60, y - 110, 120, 24), 8, 8, wb.marker(col, 6))
        for dx in (-45, 45):
            C.line(c, (x + dx, y - 86), (x + dx * 1.15, y), col, 8)
        if hl:
            f = clamp01((T - tb(4, k_stool)) / 0.35)
            ring = skia.Path()
            ring.addOval(skia.Rect.MakeXYWH(x - 110, y - 160, 220, 200))
            part, _ = wb.partial(ring, f)
            dashed_path(c, part, GREEN, 6)
            g = pop_scale(T - tb(4, k_stool) - 0.2)
            with K.at(c, x, y - 220, 0, g):
                K.text(c, "空着", 0, 0, 64, "hand", GREEN)
    return None


b.custom(j, k_kid, k_kid + 0.3, stool11)
b.hit(j, k_stool, "ding", 0.7, "小凳子圈出来")

# ================================================================ 屏 5：倒叙 · 先看结果——家用车剖面，杯子逐拍冒出来，说完“结果”砸下
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
VAN = (cx, cy + 300, 1000, 470)           # 底边中点 x, 地面 y, 宽, 高
b.path(j, 0, 0.6, book(cx - 420, cy - 450, 150, 100), GREEN, 7, sfx="wood_low")   # “丰田的做法不一样”
b.text(j, 0.6, 1.4, "丰田模式", cx - 160, cy - 450, 76, GREEN)
k_van = kq(j, wt(6, 0, 0.5), 2)           # 念到“先说一个结果”
k_seat = k_van + 1
k_tag = nx(j, wt(6, 1, 0.1), k_seat)      # “改版以后”
k_cup0 = nx(j, wt(6, 2, 0.0), k_tag)
CUPS = [(-330, 0), (-180, 1), (-20, 0), (130, 1), (290, 0), (-260, 2), (60, 2), (220, 2)]   # (dx, 位置类)
k_cups = [k_cup0 + i * 4 // len(CUPS) for i in range(len(CUPS))]
KD = nx(j, wt(6, 2, 1.0), k_cups[-1])     # 一句说完，“结果”印章砸下
b.shots[j].shake = [(KD, 14.0)]
L.note("改版后", "结果")


def van_path(cx_, gy, w, h):
    x0, x1 = cx_ - w / 2, cx_ + w / 2
    p = skia.Path()
    p.moveTo(x0, gy - 50)
    p.lineTo(x0, gy - h + 50)
    p.quadTo(x0, gy - h, x0 + 60, gy - h)
    p.lineTo(x1 - 260, gy - h)
    p.quadTo(x1 - 120, gy - h + 10, x1 - 40, gy - h * 0.5)
    p.lineTo(x1, gy - h * 0.42)
    p.lineTo(x1, gy - 50)
    p.close()
    return p


def van2(c, sc, T, cx=cx, cy=cy):
    x, gy, w, h = VAN
    with at_pop(c, x, gy, sc):
        body = van_path(x, gy, w, h)
        c.drawPath(body, K.paint("#F4F7FB"))
        c.drawPath(body, wb.marker(BLUE, 10))
        for wx in (x - w * 0.32, x + w * 0.3):
            c.drawCircle(wx, gy - 40, 62, K.paint("#3A3F48"))
            c.drawCircle(wx, gy - 40, 26, K.paint("#FFFFFF"))
        seats_on = T >= tb(5, k_seat)
        if seats_on:
            g = ease_out(clamp01((T - tb(5, k_seat)) / 0.4))
            for i, sx in enumerate((x - 330, x - 30, x + 230)):
                if g * 3 <= i:
                    break
                seat = P((sx - 90, gy - 120), (sx + 40, gy - 120), (sx + 40, gy - 170), (sx - 50, gy - 170),
                         (sx - 70, gy - 330), (sx - 110, gy - 330), close=True)
                c.drawPath(seat, K.paint("#C9D6E8"))
                c.drawPath(seat, wb.marker(BLUE, 6))
            C.line(c, (x + 380, gy - 300), (x + 440, gy - 230), BLACK, 8)
            c.drawCircle(x + 400, gy - 250, 30, wb.marker(BLACK, 7))
    return None


ev(j, k_van, pop_fn(j, k_van, van2), "wood_low", 0.8)
b.hit(j, k_seat, "wood_high", 0.6, "座椅一排排出现")
ev(j, k_tag, L.pop_text("改版后", cx - 330, cy - 260, 84, BLUE, j, k_tag), "wood_high", 0.6)


def cups2(c, kk, T, cx=cx, cy=cy):
    x, gy, w, h = VAN
    for i, (dx, kind) in enumerate(CUPS):
        dt = T - tb(5, k_cups[i]) - (0.12 if i and k_cups[i] == k_cups[i - 1] else 0.0)
        sc = pop_scale(dt)
        if sc <= 0:
            continue
        wig = C.wobble(T - tb(5, KD), 8, 26, 6) if T >= tb(5, KD) else 0.0
        yy = {0: gy - 120, 1: gy - 120, 2: gy - 200}[kind]
        with K.at(c, x + dx, yy, wig, sc):
            if kind == 2:
                C.line(c, (-45, 0), (45, 0), ORANGE, 8)
            cup(c, 0, 0, 0.8, ORANGE if i % 2 else BLUE, "#FDE3C8" if i % 2 else "#DCEAFB")
    return None


ev(j, k_cups[0], cups2, "pop", 0.7)
for i in range(1, len(CUPS)):
    if k_cups[i] != k_cups[i - 1]:
        b.hit(j, k_cups[i], ("pop", "wood_high")[i % 2], 0.65, "又冒出一个杯子")
ev(j, KD, L.stamp("结果", cx + 280, cy - 400, 110, j, KD, rot=-8), "kick", 0.95)

# ================================================================ 屏 6：倒带——“◀◀ 倒回去”，杯子打问号；地图上三个国家，小车跑一大圈
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_rw = 0
k_q3 = nx(j, wt(7, 1, 0.3), k_rw)
k_eng = nx(j, wt(8, 1, 0.1), k_q3)
k_us = nx(j, wt(8, 2, 0.35), k_eng)
k_ca = k_us + 1
k_mx = k_us + 2
k_route = k_mx + 1
L.note("倒回去", "总工程师", "美国", "加拿大", "墨西哥", "？")


def rewind3(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_rw)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx - 470, cy - 460
    with K.at(c, x, y, -4, sc):
        box(c, 0, 0, 170, 120, "#FFFFFF", RED, 8, 20)
        for dx in (-38, 18):
            p = P((dx + 34, -36), (dx + 34, 36), (dx - 22, 0), close=True)
            c.drawPath(p, K.paint(RED))
        K.text(c, "倒回去", 210, 4, 76, "hand", RED)
    return None


ev(j, k_rw, rewind3, "rim", 0.85)
b.shots[j].shake = [(k_rw, 7.0)]


def cupq3(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 420, cy - 130
    with at_pop(c, x, y, sc):
        cup(c, x, y + 70, 1.1, ORANGE, "#FDE3C8")
        K.text(c, "？", x + 95, y - 40, 110, "hand", RED)
    return None


ev(j, k_q3, pop_fn(j, k_q3, cupq3), "pop", 0.7)

MAP = {
    "加拿大": (P((cx - 20, cy - 250), (cx + 60, cy - 330), (cx + 200, cy - 345), (cx + 330, cy - 320), (cx + 470, cy - 335),
                (cx + 530, cy - 260), (cx + 470, cy - 200), (cx + 300, cy - 190), (cx + 120, cy - 195), close=True),
            (cx + 300, cy - 232), RED),
    "美国": (P((cx - 10, cy - 180), (cx + 120, cy - 185), (cx + 300, cy - 180), (cx + 470, cy - 190), (cx + 490, cy - 120),
               (cx + 430, cy - 40), (cx + 330, cy + 10), (cx + 180, cy + 20), (cx + 40, cy - 10), (cx - 20, cy - 90),
               close=True),
           (cx + 250, cy - 95), BLUE),
    "墨西哥": (P((cx + 40, cy + 0), (cx + 180, cy + 30), (cx + 260, cy + 60), (cx + 300, cy + 140), (cx + 250, cy + 210),
                (cx + 180, cy + 150), (cx + 110, cy + 90), (cx + 60, cy + 50), close=True),
            (cx + 420, cy + 130), GREEN),
}
for name, k_ in (("美国", k_us), ("加拿大", k_ca), ("墨西哥", k_mx)):
    path, (lx, ly), col = MAP[name]
    b.path(j, k_, k_ + 0.6, path, col, 8, sfx=("wood_low", "wood_high", "tom")[("美国", "加拿大", "墨西哥").index(name)],
           gain=0.7)
ROUTE3 = skia.Path()
ROUTE3.moveTo(cx + 70, cy - 100)
ROUTE3.cubicTo(cx + 40, cy - 260, cx + 120, cy - 315, cx + 280, cy - 315)
ROUTE3.cubicTo(cx + 420, cy - 315, cx + 480, cy - 220, cx + 440, cy - 130)
ROUTE3.cubicTo(cx + 400, cy - 20, cx + 290, cy + 160, cx + 240, cy + 170)
ROUTE3.cubicTo(cx + 170, cy + 120, cx + 80, cy + 40, cx + 70, cy - 100)


def route3(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_route)
    if T < t0:
        return None
    f = clamp01((T - t0) / (tb(6, k_route + 3) - t0))
    part, tip = wb.partial(ROUTE3, max(f, 0.001))
    dashed_path(c, part, BLACK, 6)
    if tip is None:
        tip = (cx + 70, cy - 100)
    with K.at(c, tip[0], tip[1] + 18, 0, 1.0):
        car_side(c, 0, 0, 110, T, RED, driver=False)
    return None


b.custom(j, k_route, k_route + 0.3, route3, sfx="shaker", gain=0.7)


def map_label(name, k_):
    """国名：白底小牌子，画在路线上面（路线从牌子下面穿过）。"""
    _, (lx, ly), col = MAP[name]
    w = K.text_w(name, 52, "hand") + 34

    def fn(c, kk, T):
        sc = pop_scale(T - tb(6, k_ + 0.5))
        if sc > 0:
            with K.at(c, lx, ly, 0, sc):
                box(c, 0, 0, w, 66, "#FFFFFF", col, 4, 33)
                K.text(c, name, 0, 2, 52, "hand", col)
        return None
    return fn


L.note(*MAP)
for name, k_ in (("美国", k_us), ("加拿大", k_ca), ("墨西哥", k_mx)):
    b.custom(j, k_ + 0.5, k_ + 0.8, map_label(name, k_))


def eng3(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 260, cy + 430
    bob = 4 * math.sin(T * 11)
    with at_pop(c, x, y, sc):
        dashed(c, (x - 330, y + 6), (x + 330, y + 6), GRAY, 6)
        c.save()
        c.translate(0, bob)
        car_side(c, x, y, 560, T, RED)
        c.restore()
        K.text(c, "总工程师", x - 20, y - 300, 60, "hand", GREEN)
        C.line(c, (x + 20, y - 262), (x + 30, y - 225), GREEN, 5)
    return None


ev(j, k_eng, pop_fn(j, k_eng, eng3), "wood_high", 0.7)

# ================================================================ 屏 7：路上 | 办公室——一家人在车里吃东西，他一路记；领导看报告，一片空白
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_hd4 = 0
k_win = 1
k_note = nx(j, wt(9, 1, 0.0), k_win)
k_food = nx(j, wt(9, 2, 0.75), k_note)
k_off = nx(j, wt(10, 0, 0.2), k_food)
k_rep = k_off + 1
k_cant = nx(j, wt(10, 1, 0.5), k_rep)
L.note("路上", "办公室", "吃东西", "报告", "看不到")


def head4(c, kk, T, cx=cx, cy=cy):
    f = ease_out(clamp01((T - tb(7, k_hd4)) / 0.5))
    if f <= 0:
        return None
    dashed(c, (cx, cy - 420), (cx, cy - 420 + 920 * f), GRAY, 5)
    for x, s, fill, line in ((cx - 300, "路上", GREEN_FILL, GREEN), (cx + 300, "办公室", GRAY_FILL, GRAY)):
        sc = pop_scale(T - tb(7, k_hd4) - (0 if x < cx else 0.12))
        if sc > 0:
            with K.at(c, x, cy - 480, 0, sc):
                box(c, 0, 0, 240, 86, fill, line, 6, 43)
                K.text(c, s, 0, 2, 54, "hand", line)
    return None


ev(j, k_hd4, head4, "wood_high", 0.6)


def win4(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 300, cy - 200
    with at_pop(c, x, y, sc):
        box(c, x, y, 520, 330, SKY, BLUE, 9, 60)
        heads = [(x - 160, y + 20, 0.8, "smile"), (x + 10, y + 40, 0.62, "smile"), (x + 160, y + 20, 0.78, "o")]
        for i, (hx, hy, s, mood) in enumerate(heads):
            c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF"))
            c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 8))
            C._eyes_mouth(c, hx, hy, s, mood, 1.0)
            C.line(c, (hx, hy + 45 * s), (hx, y + 165), BLACK, 9)
        g = pop_scale(T - tb(7, k_food))
        if g > 0:
            with K.at(c, x - 110, y + 90, 0, g):
                burger(c, 0, 0, 0.85)
            with K.at(c, x + 70, y + 110, 0, g):
                cup(c, 0, 20, 0.7, ORANGE, "#FDE3C8")
            with K.at(c, x + 220, y + 90, 0, g):
                burger(c, 0, 0, 0.75)
    return None


ev(j, k_win, pop_fn(j, k_win, win4), "pop", 0.7)
b.hit(j, k_food, "pop", 0.7, "汉堡、饮料冒出来")


def note4(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 300, cy + 260
    with at_pop(c, x, y, sc):
        with K.at(c, x, y, -4):
            box(c, 0, 0, 400, 300, NOTE_FILL, "#C9A227", 6, 10)
            for i in range(5):
                c.drawCircle(-150 + i * 75, -150, 12, wb.marker(BLACK, 5))
            n = clamp01((T - tb(7, k_note)) / (tb(7, k_note + 2) - tb(7, k_note)))
            for r in range(2):
                ln = clamp01(n * 2 - r)
                if ln > 0:
                    C.line(c, (-150, -80 + r * 55), (-150 + 300 * ln, -80 + r * 55), GRAY, 7)
            if T >= tb(7, k_food):
                g = pop_scale(T - tb(7, k_food) - 0.2)
                with K.at(c, 0, 80, 0, g):
                    K.text(c, "吃东西", 0, 0, 72, "hand", RED)
                    ring = skia.Path()
                    ring.addOval(skia.Rect.MakeXYWH(-150, -55, 300, 110))
                    part, _ = wb.partial(ring, clamp01((T - tb(7, k_food) - 0.4) / 0.3))
                    c.drawPath(part, wb.marker(RED, 6))
    return None


ev(j, k_note, pop_fn(j, k_note, note4), "wood_low", 0.7)


def office4(c, sc, T, cx=cx, cy=cy):
    x, fy, s = cx + 300, cy + 420, 0.85
    hx, hy = head_of(x, fy, s)
    reading = T >= tb(7, k_rep)
    with at_pop(c, x, fy, sc):
        draw_boss(c, x, fy, s, lh=(x - 80 * s, hy + 150 * s) if reading else None,
                  rh=(x + 80 * s, hy + 150 * s) if reading else None, mood="flat",
                  head_dy=6 * math.sin((T - tb(7, k_rep)) * 3) if reading else 0.0)
        c.drawPath(wb.desk(x, fy - 100, 420), wb.marker(BLACK, 8))
        if reading:
            g = pop_scale(T - tb(7, k_rep))
            with K.at(c, x, hy + 150 * s, 0, g):
                box(c, 0, 0, 230, 180, "#FFFFFF", BLACK, 6, 6)
                K.text(c, "报告", 0, -50, 48, "hand", BLACK)
                for r in range(2):
                    C.line(c, (-80, 10 + r * 40), (80, 10 + r * 40), "#E1E4E8", 6)
    return None


ev(j, k_off, pop_fn(j, k_off, office4), "wood_low", 0.7)
b.hit(j, k_rep, "wood_high", 0.6, "报告举起来")
ev(j, k_cant, L.slam_text("看不到", cx + 300, cy - 220, 92, RED, j, k_cant, rot=-5), "kick", 0.85)
b.shots[j].shake = [(k_cant, 9.0)]


def cloud4(c, kk, T, cx=cx, cy=cy):
    """领导头顶：一个空的想法泡泡，里面画个问号。"""
    sc = pop_scale(T - tb(7, k_cant) - 0.15)
    if sc <= 0:
        return None
    x, y = cx + 300, cy - 50
    with K.at(c, x, y, 0, sc):
        for dx, dy, r in ((-40, -6, 55), (10, -24, 62), (60, -4, 50), (10, 22, 52)):
            c.drawCircle(dx, dy, r, K.paint("#FFFFFF"))
        for dx, dy, r in ((-40, -6, 55), (10, -24, 62), (60, -4, 50), (10, 22, 52)):
            c.drawCircle(dx, dy, r, wb.marker(GRAY, 5))
        for dx, dy, r in ((-40, -6, 50), (10, -24, 57), (60, -4, 45), (10, 22, 47)):
            c.drawCircle(dx, dy, r, K.paint("#FFFFFF"))
        qmark(c, 10, 0, 80, GRAY)
    return None


b.custom(j, k_cant, k_cant + 0.3, cloud4)

# ================================================================ 屏 8：“现地现物”印章；脚印从办公楼走到车间，车间上方一只眼睛，再打勾“下结论”
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_bld = 0
k_st5 = nx(j, wt(11, 0, 0.8), k_bld)
k_fp = nx(j, wt(12, 0, 0.1), k_st5)
k_eye5 = nx(j, wt(12, 1, 0.1), k_fp + 1)
k_ok5 = nx(j, wt(12, 2, 0.2), k_eye5)
L.note("办公楼", "车间", "下结论")
b.path(j, k_bld, k_bld + 0.8, wb.building(cx - 380, cy + 420, 240, 320), GRAY, 8, sfx="wood_low", gain=0.7)
b.path(j, k_bld + 0.6, k_bld + 1.4, factory_path(cx + 370, cy + 420, 320, 240), BLUE, 8)
b.custom(j, k_bld + 1.0, k_bld + 1.3, L.pop_text("办公楼", cx - 380, cy + 490, 50, GRAY, j, k_bld + 1.0))
b.custom(j, k_bld + 1.4, k_bld + 1.7, L.pop_text("车间", cx + 370, cy + 490, 50, BLUE, j, k_bld + 1.4))
ev(j, k_st5, L.stamp("现地现物", cx, cy - 380, 120, j, k_st5, rot=-5), "kick", 0.95)
b.shots[j].shake = [(k_st5, 12.0)]
FEET5 = [(cx - 220 + i * 95, cy + 395 - (i % 2) * 34) for i in range(5)]


def feet5(c, kk, T, cx=cx, cy=cy):
    for i, (x, y) in enumerate(FEET5):
        t0 = tb(8, k_fp) + i * (tb(8, k_fp + 1) - tb(8, k_fp)) / 2.5
        a = clamp01((T - t0) / 0.12)
        if a > 0:
            foot(c, x, y, 90, 0.9, BLACK, a)
    return None


b.custom(j, k_fp, k_fp + 2, feet5, sfx="wood_low", gain=0.6)
b.hit(j, k_fp + 1, "wood_high", 0.5, "脚印走到车间")


def eye5(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 370, cy - 30
    with at_pop(c, x, y, sc):
        eye(c, x, y, 1.0, BLUE, look=0.3 * math.sin(T * 2))
        dashed(c, (x, y + 80), (x, y + 140), BLUE, 5)
    return None


ev(j, k_eye5, pop_fn(j, k_eye5, eye5), "pop", 0.7)


def ok5(c, kk, T, cx=cx, cy=cy):
    t0 = tb(8, k_ok5)
    if T < t0:
        return None
    f = clamp01((T - t0) / 0.35)
    part, _ = wb.partial(wb.arrow((cx + 240, cy - 30), (cx - 40, cy - 30), 0.0, 36), f)
    c.drawPath(part, wb.marker(GREEN, 8))
    sc = pop_scale(T - t0 - 0.2)
    if sc > 0:
        with K.at(c, cx - 250, cy - 30, 0, sc):
            box(c, 0, 0, 330, 120, GREEN_FILL, GREEN, 7, 20)
            c.drawPath(check(-110, 0, 34), wb.marker(GREEN, 9))
            K.text(c, "下结论", 40, 2, 64, "hand", GREEN)
    return None


ev(j, k_ok5, ok5, "clap", 0.75)

# ================================================================ 屏 9：大野耐一在车间地上画圈，年轻员工站进去；太阳从左走到右；灯泡亮
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
OH6 = (cx - 400, cy + 430, 0.85)
WK6 = (cx + 20, cy + 420, 0.75)
MC6 = (cx + 400, cy + 430)
k_oh = 0
k_mc = 1
k_ring = nx(j, wt(13, 0, 0.8), k_mc)
k_wk6 = nx(j, wt(13, 1, 0.3), k_ring)
k_sun = nx(j, wt(14, 0, 0.0), k_wk6)
k_half = k_sun + 2
k_bulb = nx(j, wt(14, 1, 0.6), k_half)
L.note("大野耐一", "大半天")


def ohno6(c, sc, T, cx=cx, cy=cy):
    x, y, s = OH6
    hx, hy = head_of(x, y, s)
    draw_t = tb(9, k_ring)
    if draw_t - 0.4 <= T < draw_t + 0.8:
        rh = (x + 150 * s, y - 60 * s + 15 * math.sin(T * 14))
    elif T >= tb(9, k_wk6):
        rh = (x + 160 * s, hy + 40 * s)
    else:
        rh = None
    with at_pop(c, x, y, sc):
        draw_ohno(c, x, y, s, rh=rh, mood="smile" if T >= tb(9, k_bulb) else "flat", head_dx=6 if rh else 0)
    return None


ev(j, k_oh, pop_fn(j, k_oh, ohno6), "wood_low", 0.7)
b.custom(j, k_oh + 0.4, k_oh + 0.7, L.pop_text("大野耐一", cx - 400, cy + 90, 54, BLACK, j, k_oh + 0.4))


def machine6(c, sc, T, cx=cx, cy=cy):
    x, y = MC6
    with at_pop(c, x, y, sc):
        box(c, x, y - 130, 220, 260, GRAY_FILL, BLACK, 7, 12)
        box(c, x, y - 190, 150, 70, "#FFFFFF", BLACK, 5, 8)
        a = T * 2.5
        for i in range(6):
            ang = a + i * math.pi / 3
            C.line(c, (x, y - 70), (x + math.cos(ang) * 50, y - 70 + math.sin(ang) * 50), BLACK, 8)
        c.drawCircle(x, y - 70, 22, K.paint("#FFFFFF"))
        c.drawCircle(x, y - 70, 22, wb.marker(BLACK, 6))
        if T >= tb(9, k_bulb):
            f = clamp01((T - tb(9, k_bulb)) / 0.3)
            ring = skia.Path()
            ring.addCircle(x + 70, y - 190, 48)
            part, _ = wb.partial(ring, f)
            c.drawPath(part, wb.marker(RED, 8))
        c.drawCircle(x + 70, y - 190, 10, K.paint(RED))
    return None


ev(j, k_mc, pop_fn(j, k_mc, machine6), "wood_high", 0.6)
b.path(j, 0, 0.6, P((cx - 600, cy + 432), (cx + 600, cy + 432)), GRAY, 6)
RING6 = skia.Path()
RING6.addOval(skia.Rect.MakeXYWH(WK6[0] - 190, WK6[1] - 45, 380, 90))
b.path(j, k_ring, k_ring + 0.9, RING6, ORANGE, 10, sfx="shaker", gain=0.8)


def worker6(c, sc, T, cx=cx, cy=cy):
    x, y, s = WK6
    with at_pop(c, x, y, sc):
        look = 0.0 if T < tb(9, k_sun) else 6 * math.sin((T - tb(9, k_sun)) * 1.5)
        draw_worker(c, x, y, s, head_dx=look, mood="o" if T >= tb(9, k_bulb) else "flat")
    return None


ev(j, k_wk6, pop_fn(j, k_wk6, worker6), "pop", 0.7)


def sun6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k_sun)
    if T < t0:
        return None
    f = ease_in_out(clamp01((T - t0) / (tb(9, k_half) - t0)))
    ang = math.pi * (1 - f)
    x = cx + math.cos(ang) * 470
    y = cy - 280 - math.sin(ang) * 200
    arc = skia.Path()
    arc.addArc(skia.Rect.MakeXYWH(cx - 470, cy - 480, 940, 400), 180, 180 * f)
    dashed_path(c, arc, YELLOW, 5)
    sc = pop_scale(T - t0)
    with K.at(c, x, y, f * 90, sc):
        c.drawCircle(0, 0, 50, K.paint("#FFE08A"))
        c.drawCircle(0, 0, 50, wb.marker(ORANGE, 7))
        for i in range(8):
            a = i * math.pi / 4
            C.line(c, (math.cos(a) * 66, math.sin(a) * 66), (math.cos(a) * 88, math.sin(a) * 88), ORANGE, 7)
    return None


b.custom(j, k_sun, k_sun + 0.3, sun6, sfx="wood_high", gain=0.6)
ev(j, k_half, L.pop_text("大半天", cx, cy - 280, 80, ORANGE, j, k_half), "clap", 0.7)


def bulb6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k_bulb)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = WK6[0] + 10, WK6[1] - 0.75 * 290 - 150
    sparkle(c, x, y, T - t0, YELLOW, 10, 60, 140)
    with K.at(c, x, y, 0, sc):
        c.drawCircle(0, 0, 46, K.paint("#FFF3B0"))
        c.drawPath(C.bulb_path(0, 0, 46), wb.marker(ORANGE, 7))
    return None


ev(j, k_bulb, bulb6, "ding", 0.8)

# ================================================================ 屏 10：传话——员工气泡里的大警示 → 组长气泡里变小变歪 → 会议室“那边有点问题”
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
FY7, S7 = cy + 400, 0.72
X7 = [cx - 420, cx - 120, cx + 330]
k_eye7 = 0
k_ppl7 = 1
k_b1 = nx(j, wt(16, 0, 0.2), k_ppl7)
k_b2 = k_b1 + 1
k_dist = nx(j, wt(16, 1, 0.4), k_b2)
k_room = nx(j, wt(17, 0, 0.2), k_dist)
k_b3 = nx(j, wt(17, 1, 0.5), k_room)
L.note("亲眼看", "走样", "会议室", "那边有点问题", "？")


def eye7(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 100, cy - 470
    with at_pop(c, x, y, sc):
        eye(c, x, y, 0.8, BLUE, look=0.4 * math.sin(T * 2.2))
        K.text(c, "亲眼看", x + 230, y + 4, 70, "hand", BLUE)
        K.text(c, "？", x + 400, y, 90, "hand", RED)
    return None


ev(j, k_eye7, pop_fn(j, k_eye7, eye7), "wood_high", 0.7)


def ppl7(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, FY7, sc):
        draw_worker(c, X7[0], FY7, S7, mood="o")
        draw_leader(c, X7[1], FY7, S7)
    return None


ev(j, k_ppl7, pop_fn(j, k_ppl7, ppl7), "pop", 0.6)


def bubbles7(c, kk, T, cx=cx, cy=cy):
    y = cy - 100
    for i, (x, k_, r, rot) in enumerate(((X7[0], k_b1, 72, 0.0), (X7[1], k_b2, 40, 18.0))):
        sc = pop_scale(T - tb(10, k_))
        if sc <= 0:
            continue
        with at_pop(c, x, y, sc):
            bubble_box(c, x, y, 240, 200, -1)
            wig = C.wobble(T - tb(10, k_dist), 10, 24, 5) if i == 1 else 0.0
            warn(c, x, y + 6, r, RED if i == 0 else ORANGE, rot + wig)
        if i == 1:
            f = clamp01((T - tb(10, k_)) / 0.3)
            part, _ = wb.partial(wb.arrow((X7[0] + 130, y - 60), (X7[1] - 130, y - 60), -0.25, 26), f)
            c.drawPath(part, wb.marker(GRAY, 6))
    return None


ev(j, k_b1, bubbles7, "pop", 0.7)
b.hit(j, k_b2, "pop", 0.6, "第二个气泡，警示变小变歪")
ev(j, k_dist, L.slam_text("走样", X7[1] + 80, cy + 100, 76, ORANGE, j, k_dist, rot=8), "rim", 0.8)


def room7(c, sc, T, cx=cx, cy=cy):
    x = X7[2]
    with at_pop(c, x, FY7, sc):
        box(c, x, FY7 - 190, 400, 420, "#F7F3EC", "#A9773E", 8, 16)
        K.text(c, "会议室", x, FY7 - 350, 48, "hand", "#A9773E")
        draw_boss(c, x, FY7, S7, mood="flat")
    return None


ev(j, k_room, pop_fn(j, k_room, room7), "wood_low", 0.7)


def bubble7c(c, kk, T, cx=cx, cy=cy):
    t0 = tb(10, k_b3)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = X7[2] - 20, cy - 110
    f = clamp01((T - t0) / 0.3)
    part, _ = wb.partial(wb.arrow((X7[1] + 130, cy - 160), (x - 190, cy - 160), -0.25, 26), f)
    c.drawPath(part, wb.marker(GRAY, 6))
    with at_pop(c, x, y, sc):
        bubble_box(c, x, y, 380, 130, 1)
        K.text(c, "那边有点问题", x, y + 2, 50, "hand", GRAY)
    return None


ev(j, k_b3, bubble7c, "pop", 0.65)

# ================================================================ 屏 11：听来的是故事（耳朵 + 故事书），看到的才是事实（眼睛 + 实物）
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_hd8 = 0
k_ear = nx(j, wt(18, 0, 0.1), k_hd8, 1)
k_book = k_ear + 1
k_eye8 = nx(j, wt(18, 1, 0.1), k_book)
k_obj = k_eye8 + 1
k_ck = nx(j, wt(18, 1, 0.9), k_obj)
L.note("听来的", "看到的", "故事", "事实")


def head8(c, kk, T, cx=cx, cy=cy):
    f = ease_out(clamp01((T - tb(11, k_hd8)) / 0.5))
    if f <= 0:
        return None
    dashed(c, (cx, cy - 420), (cx, cy - 420 + 900 * f), GRAY, 5)
    for x, s, fill, line in ((cx - 300, "听来的", GRAY_FILL, GRAY), (cx + 300, "看到的", GREEN_FILL, GREEN)):
        sc = pop_scale(T - tb(11, k_hd8) - (0 if x < cx else 0.12))
        if sc > 0:
            with K.at(c, x, cy - 480, 0, sc):
                box(c, 0, 0, 260, 86, fill, line, 6, 43)
                K.text(c, s, 0, 2, 54, "hand", line)
    return None


ev(j, k_hd8, head8, "wood_high", 0.6)
ev(j, k_ear, pop_fn(j, k_ear, lambda c, sc, T, cx=cx, cy=cy: _ear8(c, sc, T, cx, cy)), "pop", 0.7)


def _ear8(c, sc, T, cx, cy):
    x, y = cx - 300, cy - 230
    with at_pop(c, x, y, sc):
        ear(c, x, y, 1.0)
        for i in range(3):
            r = 50 + i * 35 + 10 * math.sin(T * 6 - i)
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(x - 120 - r, y - r, 2 * r, 2 * r), 140, 80)
            c.drawPath(arc, wb.marker(ORANGE, 5, 0.6))


def book8(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 300, cy + 170
    with at_pop(c, x, y, sc):
        for sg in (-1, 1):
            pg = P((x, y - 110), (x + sg * 200, y - 130), (x + sg * 200, y + 130), (x, y + 150), close=True)
            c.drawPath(pg, K.paint("#FFFFFF"))
            c.drawPath(pg, wb.marker(ORANGE, 8))
        K.text(c, "故事", x - 100, y + 10, 70, "hand", ORANGE)
        for i, (dx, dy) in enumerate(((60, -40), (130, -10))):
            star = skia.Path()
            for n in range(10):
                r = 22 if n % 2 == 0 else 10
                a = -math.pi / 2 + n * math.pi / 5
                (star.moveTo if n == 0 else star.lineTo)(x + dx + math.cos(a) * r, y + dy + math.sin(a) * r)
            star.close()
            c.drawPath(star, K.paint("#FFE08A"))
            c.drawPath(star, wb.marker(ORANGE, 4))
        cloud = skia.Path()
        cloud.addOval(skia.Rect.MakeXYWH(x + 50, y + 30, 120, 50))
        c.drawPath(cloud, wb.marker(BLUE, 5))
        if T >= tb(11, k_ck):
            g = pop_scale(T - tb(11, k_ck) - 0.15)
            with K.at(c, x + 170, y - 170, 0, g):
                qmark(c, 0, 0, 110, GRAY)
    return None


ev(j, k_book, pop_fn(j, k_book, book8), "wood_low", 0.7)


def eye8(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 300, cy - 230
    with at_pop(c, x, y, sc):
        eye(c, x, y, 1.0, GREEN, look=0.4)
    return None


ev(j, k_eye8, pop_fn(j, k_eye8, eye8), "pop", 0.7)


def obj8(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 300, cy + 170
    with at_pop(c, x, y, sc):
        box(c, x, y + 20, 300, 200, "#E6CFA8", "#A9773E", 8, 10)
        C.line(c, (x - 150, y - 30), (x + 150, y - 30), "#A9773E", 6)
        box(c, x + 60, y + 50, 120, 60, "#FFFFFF", RED, 5, 6)
        C.line(c, (x + 15, y + 50), (x + 105, y + 50), RED, 5)
        K.text(c, "事实", x - 60, y + 50, 60, "hand", GREEN)
        if T >= tb(11, k_ck):
            f = clamp01((T - tb(11, k_ck)) / 0.3)
            part, _ = wb.partial(check(x + 140, y - 170, 70), f)
            c.drawPath(part, wb.marker(GREEN, 16))
    return None


ev(j, k_obj, pop_fn(j, k_obj, obj8), "wood_high", 0.7)
b.hit(j, k_ck, "clap", 0.85, "实物打勾")

# ================================================================ 屏 12：小李看表犹豫；三个会排着；跑一趟 = 划掉三个会
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
LI12 = (cx - 380, cy + 440, 0.85)
k_li12 = 0
k_watch = nx(j, wt(19, 1, 0.2), k_li12)
k_m = [nx(j, wt(19, 2, 0.0), k_watch)]
k_m += [k_m[0] + 1, k_m[0] + 2]
k_run = nx(j, wt(20, 0, 0.1), k_m[2])
k_x = [nx(j, wt(20, 1, 0.3), k_run + 1)]
k_x += [k_x[0] + 1, k_x[0] + 2]
MT12 = [cx - 300, cx, cx + 300]
L.note("开会")


def li12(c, sc, T):
    x, y, s = LI12
    hx, hy = head_of(x, y, s)
    if T >= tb(12, k_run):
        x2, dy, moving = walk(T, tb(12, k_run), tb(12, k_run + 1) - tb(12, k_run), x, x + 300, 14, 3.5)
        with at_pop(c, x, y, sc):
            draw_li(c, x2, y + dy, s, "smile")
        return None
    watch = T >= tb(12, k_watch)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad" if watch else "flat", lh=(x - 20 * s, hy + 110 * s) if watch else None)
        if watch:
            c.drawCircle(x - 20 * s, hy + 110 * s, 16, K.paint("#FFFFFF"))
            c.drawCircle(x - 20 * s, hy + 110 * s, 16, wb.marker(BLUE, 5))
            g = pop_scale(T - tb(12, k_watch))
            with K.at(c, hx + 140, hy - 70, 0, g):
                c.drawPath(wb.clock(0, 0, 60), wb.marker(BLACK, 7))
                ang = (T - tb(12, k_watch)) * 4
                C.line(c, (0, 0), (math.cos(ang) * 45, math.sin(ang) * 45), RED, 6)
    return None


ev(j, k_li12, pop_fn(j, k_li12, li12), "pop", 0.6)
b.hit(j, k_watch, "wood_high", 0.6, "小李看表")


def meetings12(c, kk, T, cx=cx, cy=cy):
    for i, x in enumerate(MT12):
        sc = pop_scale(T - tb(12, k_m[i]))
        if sc <= 0:
            continue
        y = cy - 330
        with at_pop(c, x, y, sc):
            box(c, x, y, 250, 250, "#F7F3EC", "#A9773E", 7, 14)
            K.text(c, "开会", x, y - 80, 52, "hand", "#A9773E")
            tab = skia.Rect.MakeXYWH(x - 85, y + 20, 170, 60)
            c.drawOval(tab, K.paint(WOOD))
            c.drawOval(tab, wb.marker("#A9773E", 5))
            for dx in (-70, 0, 70):
                c.drawCircle(x + dx, y - 10, 20, wb.marker(BLACK, 5))
        if T >= tb(12, k_x[i]):
            f = clamp01((T - tb(12, k_x[i])) / 0.25)
            part, _ = wb.partial(cross(x, cy - 330, 110), f)
            c.drawPath(part, wb.marker(RED, 14))
    return None


ev(j, k_m[0], meetings12, "wood_low", 0.6)
b.hit(j, k_m[1], "wood_low", 0.6, "第二个会")
b.hit(j, k_m[2], "wood_low", 0.6, "第三个会")
for i in range(3):
    b.hit(j, k_x[i], ("rim", "rim", "kick")[i], 0.8, f"划掉第{i + 1}个会")
b.shots[j].shake = [(k_x[2], 10.0)]
FEET12 = [(cx - 200 + i * 90, cy + 420 - (i % 2) * 30) for i in range(5)]


def run12(c, kk, T, cx=cx, cy=cy):
    t0 = tb(12, k_run)
    if T < t0:
        return None
    for i, (x, y) in enumerate(FEET12):
        a = clamp01((T - t0 - i * 0.12) / 0.1)
        if a > 0:
            foot(c, x, y, 90, 0.85, GRAY, a)
    sc = pop_scale(T - t0 - 0.4)
    if sc > 0:
        with at_pop(c, cx + 380, cy + 430, sc):
            c.drawPath(factory_path(cx + 380, cy + 430, 260, 200), wb.marker(BLUE, 8))
    return None


ev(j, k_run, run12, "shaker", 0.7)

# ================================================================ 屏 13：先试试这三步——“三步”砸下；做法一：去现场看真数据、真用户、真流程
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_three = kq(j, wt(21, 1, 0.75), 1)
k_one = nx(j, wt(22, 0, 0.0), k_three)
k_ic = [nx(j, wt(22, 2, 0.45), k_one + 1)]
k_ic += [k_ic[0] + 1, k_ic[0] + 2]
L.note("三步", "真数据", "真用户", "真流程", "1", "2", "3")


def steps_row(jj, k0, active, sfx="wood_high"):
    """右上角三个步骤圆点：第 active 个（0 起）在 k0 拍变红放大。"""
    x0, y0 = R[jj][0] + 60, R[jj][1] - 440

    def fn(c, kk, T):
        for i in range(3):
            sc = pop_scale(T - tb(jj, 0 if jj != 13 else k_three) - i * 0.1)
            if sc <= 0:
                continue
            on = i == active and T >= tb(jj, k0)
            g = 1 + 0.25 * pop_scale(T - tb(jj, k0)) if on else 1.0
            x = x0 + 120 + i * 140
            with K.at(c, x, y0, 0, sc * g):
                c.drawCircle(0, 0, 50, K.paint(RED if on else "#FFFFFF"))
                c.drawCircle(0, 0, 50, wb.marker(RED if on else GRAY, 7))
                K.text(c, str(i + 1), 0, 4, 60, "hand", "#FFFFFF" if on else GRAY)
        return None
    b.custom(jj, k0, k0 + 0.3, fn, sfx=sfx, gain=0.7)


ev(j, k_three, L.slam_text("三步", cx - 330, cy - 440, 120, RED, j, k_three, rot=-5), "kick", 0.9)
b.shots[j].shake = [(k_three, 10.0)]
steps_row(j, k_one, 0)
LI13 = (cx - 420, cy + 450, 0.85)


def li13(c, kk, T, cx=cx, cy=cy):
    t0 = tb(13, k_one)
    if T < t0:
        return None
    x0, y, s = LI13
    x, dy, moving = walk(T, t0, 0.8, x0 - 260, x0, 14, 3.5)
    hx, hy = head_of(x, y, s)
    point = T >= tb(13, k_ic[0])
    draw_li(c, x, y + dy, s, "smile" if point else "flat", rh=(x + 130 * s, hy - 20 * s) if point else None)
    return None


b.custom(j, k_one, k_one + 0.3, li13)


def site13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_one) - 0.5)
    if sc <= 0:
        return None
    with at_pop(c, cx + 250, cy + 450, sc):
        c.drawPath(factory_path(cx + 250, cy + 450, 420, 260), wb.marker(BLUE, 8))
        K.text(c, "现场", cx + 250, cy + 290, 56, "hand", BLUE)
    return None


b.custom(j, k_one, k_one + 0.6, site13)
ICONS13 = ["真数据", "真用户", "真流程"]


def icon13(i):
    x, y = cx - 330 + i * 330, cy - 110

    def fn(c, sc, T):
        with at_pop(c, x, y, sc):
            box(c, x, y, 240, 220, "#FFFFFF", (BLUE, GREEN, ORANGE)[i], 7, 20)
            if i == 0:
                for n, hgt in enumerate((60, 110, 80, 140)):
                    c.drawRect(skia.Rect.MakeXYWH(x - 80 + n * 42, y + 70 - hgt, 30, hgt), K.paint(BLUE_FILL))
                    c.drawRect(skia.Rect.MakeXYWH(x - 80 + n * 42, y + 70 - hgt, 30, hgt), wb.marker(BLUE, 4))
            elif i == 1:
                c.drawCircle(x, y - 30, 40, wb.marker(GREEN, 7))
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(x - 70, y + 20, 140, 120), 180, 180)
                c.drawPath(arc, wb.marker(GREEN, 7))
            else:
                for n in range(3):
                    box(c, x - 60 + n * 60, y - 30 + n * 30, 50, 36, "#FDE3C8", ORANGE, 4, 6)
            K.text(c, ICONS13[i], x, y + 160, 54, "hand", (BLUE, GREEN, ORANGE)[i])
        return None
    return fn


for i in range(3):
    ev(j, k_ic[i], pop_fn(j, k_ic[i], icon13(i)), ("pop", "pop", "clap")[i], 0.7)

# ================================================================ 屏 14：做法二——站着看十五分钟，嘴上拉链，只看不说，本子上记
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
LI14 = (cx - 280, cy + 440, 0.95)
k_li14 = 0
steps_row(j, 0, 1)
k_tm = nx(j, wt(23, 1, 0.1), 0)
k_zip = nx(j, wt(23, 2, 0.2), k_tm)
k_wr = nx(j, wt(23, 3, 0.1), k_zip)
L.note("15分钟")


def li14(c, sc, T):
    x, y, s = LI14
    hx, hy = head_of(x, y, s)
    writing = T >= tb(14, k_wr)
    rh = (x + 110 * s + 10 * math.sin(T * 16), hy + 120 * s) if writing else (x + 110 * s, hy + 140 * s)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "flat", lh=(x - 30 * s, hy + 150 * s), rh=rh)
        with K.at(c, x + 40 * s, hy + 150 * s, -10):
            box(c, 0, 0, 120, 90, NOTE_FILL, "#C9A227", 5, 6)
        if T >= tb(14, k_zip):
            g = pop_scale(T - tb(14, k_zip))
            with K.at(c, hx, hy + 20 * s, 0, g):
                c.drawRoundRect(skia.Rect.MakeXYWH(-30, -7, 60, 14), 7, 7, K.paint("#C9CED6"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-30, -7, 60, 14), 7, 7, wb.marker(GRAY, 3))
                for n in range(6):
                    C.line(c, (-24 + n * 10, -3), (-19 + n * 10, 3), GRAY, 3)
                c.drawRoundRect(skia.Rect.MakeXYWH(28, -4, 22, 12), 3, 3, K.paint(GRAY))
                c.drawCircle(46, 2, 7, wb.marker(GRAY, 3))
    return None


ev(j, k_li14, pop_fn(j, k_li14, li14), "pop", 0.6)
b.hit(j, k_zip, "rim", 0.8, "嘴上拉上拉链")


def timer14(c, kk, T, cx=cx, cy=cy):
    t0 = tb(14, k_tm)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 250, cy - 130
    f = clamp01((T - t0) / (tb(14, k_wr + 2) - t0))
    with K.at(c, x, y, 0, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(-25, -205, 50, 34), 8, 8, K.paint(GRAY))
        c.drawCircle(0, 0, 170, K.paint("#FFFFFF"))
        c.drawCircle(0, 0, 170, wb.marker(BLACK, 10))
        pie = skia.Path()
        pie.moveTo(0, 0)
        pie.arcTo(skia.Rect.MakeXYWH(-140, -140, 280, 280), -90, 90 * f, False)
        pie.close()
        c.drawPath(pie, K.paint("#FDE3C8"))
        c.drawPath(pie, wb.marker(ORANGE, 5))
        K.text(c, "15分钟", 0, 230, 70, "hand", ORANGE)
    return None


ev(j, k_tm, timer14, "wood_high", 0.7)


def page14(c, kk, T, cx=cx, cy=cy):
    t0 = tb(14, k_wr)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 250, cy + 290
    with at_pop(c, x, y, sc):
        box(c, x, y, 380, 260, "#FFFFFF", BLACK, 6, 8)
        for r in range(4):
            f = clamp01((T - t0 - r * 0.4) / 0.4)
            if f > 0:
                C.line(c, (x - 140, y - 85 + r * 55), (x - 140 + (260 - (r % 2) * 60) * f, y - 85 + r * 55), BLUE, 7)
                c.drawCircle(x - 160, y - 85 + r * 55, 6, K.paint(BLUE))
    return None


ev(j, k_wr, page14, "wood_low", 0.7)
b.hit(j, k_wr + 1, "wood_low", 0.5, "本子上又记一行")

# ================================================================ 屏 15：做法三——会上小李先举起照片，再说想法；小王、领导点头
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
LI15 = (cx - 380, cy + 450, 0.9)
steps_row(j, 0, 2)
k_aud = 1
k_photo = nx(j, wt(24, 2, 0.2), k_aud)
k_idea = nx(j, wt(24, 3, 0.2), k_photo)
k_nod = k_idea + 1
L.note("先", "再")


def li15(c, sc, T):
    x, y, s = LI15
    hx, hy = head_of(x, y, s)
    up = T >= tb(15, k_photo)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if up else "flat", rh=(x + 130 * s, hy - 60 * s) if up else None)
    return None


ev(j, 0, pop_fn(j, 0, li15))


def photo15(c, kk, T, cx=cx, cy=cy):
    t0 = tb(15, k_photo)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx - 240, cy + 20
    with K.at(c, x, y, -6, sc):
        box(c, 0, 0, 280, 220, "#FFFFFF", BLACK, 7, 6)
        box(c, 0, -10, 240, 160, SKY, GRAY, 3, 2)
        box(c, -30, 20, 110, 70, "#E6CFA8", "#A9773E", 4, 4)
        box(c, -30, 12, 50, 26, RED_FILL, RED, 3, 3)
        C.line(c, (-120, 60), (120, 60), GRAY, 4)
        with K.at(c, -150, -120, 0, 1):
            c.drawCircle(0, 0, 46, K.paint(RED))
            K.text(c, "先", 0, 4, 56, "hand", "#FFFFFF")
    return None


ev(j, k_photo, photo15, "clap", 0.8)


def idea15(c, kk, T, cx=cx, cy=cy):
    t0 = tb(15, k_idea)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 120, cy - 200
    with at_pop(c, x, y, sc):
        bubble_box(c, x, y, 300, 190, -1)
        c.drawCircle(x, y - 10, 40, K.paint("#FFF3B0"))
        c.drawPath(C.bulb_path(x, y - 10, 40), wb.marker(ORANGE, 6))
        c.drawCircle(x + 130, y - 90, 40, K.paint(BLUE))
        K.text(c, "再", x + 130, y - 86, 50, "hand", "#FFFFFF")
    return None


ev(j, k_idea, idea15, "pop", 0.75)


def aud15(c, sc, T, cx=cx, cy=cy):
    nod = T >= tb(15, k_nod)
    dy = 8 * abs(math.sin((T - tb(15, k_nod)) * 6)) if nod else 0.0
    with at_pop(c, cx + 300, cy + 450, sc):
        draw_wang(c, cx + 170, cy + 450, 0.8, mood="smile" if nod else "flat")
        draw_boss(c, cx + 430, cy + 450, 0.8, mood="smile" if nod else "flat", head_dy=dy)
        tab = skia.Rect.MakeXYWH(cx + 60, cy + 300, 480, 90)
        c.drawOval(tab, K.paint(WOOD))
        c.drawOval(tab, wb.marker("#A9773E", 6))
        if nod:
            for n, x in enumerate((cx + 170, cx + 430)):
                g = pop_scale(T - tb(15, k_nod) - n * 0.12)
                with K.at(c, x + 50, cy + 450 - 0.8 * 290 - 90, 0, g):
                    c.drawPath(check(0, 0, 32), wb.marker(GREEN, 9))
    return None


ev(j, k_aud, pop_fn(j, k_aud, aud15), "wood_low", 0.6)
b.hit(j, k_nod, "wood_high", 0.7, "小王、领导点头")

# ================================================================ 屏 16：带着事实开会——会议时钟从一小时缩到十五分钟，小李挺直腰
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
LI16 = (cx - 330, cy + 450, 0.95)
k_li16 = 0
k_clk = 1
k_shrink = nx(j, wt(25, 1, 0.1), k_clk)
k_proud = nx(j, wt(25, 2, 0.3), k_shrink + 1)
L.note("1小时", "15分钟")


def li16(c, sc, T):
    x, y, s = LI16
    hx, hy = head_of(x, y, s)
    t0 = tb(16, k_proud)
    sq = lerp(0.9, 1.04, ease_out(clamp01((T - t0) / 0.3))) if T >= t0 else 0.9
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if T >= t0 else "flat", squash=sq, lh=(x - 120 * s, hy + 120 * s))
        with K.at(c, x - 130 * s, hy + 160 * s, 8):
            box(c, 0, 0, 120, 100, "#FFFFFF", BLACK, 5, 4)
            box(c, 0, -6, 96, 66, SKY, GRAY, 3, 2)
        sparkle(c, hx, hy - 20, T - t0, YELLOW, 10, 80, 170)
    return None


ev(j, k_li16, pop_fn(j, k_li16, li16), "pop", 0.6)
b.hit(j, k_proud, "clap", 0.85, "小李挺直腰")


def clock16(c, kk, T, cx=cx, cy=cy):
    t0 = tb(16, k_clk)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 220, cy - 160
    f = ease_in_out(clamp01((T - tb(16, k_shrink)) / 0.8)) if T >= tb(16, k_shrink) else 0.0
    sweep = lerp(359.9, 90, f)
    with K.at(c, x, y, 0, sc):
        c.drawCircle(0, 0, 220, K.paint("#FFFFFF"))
        pie = skia.Path()
        pie.moveTo(0, 0)
        pie.arcTo(skia.Rect.MakeXYWH(-200, -200, 400, 400), -90, sweep, False)
        pie.close()
        c.drawPath(pie, K.paint(RED_FILL if f < 0.99 else GREEN_FILL))
        c.drawPath(pie, wb.marker(RED if f < 0.99 else GREEN, 5))
        c.drawCircle(0, 0, 220, wb.marker(BLACK, 10))
        for i in range(12):
            a = i * math.pi / 6
            C.line(c, (math.cos(a) * 190, math.sin(a) * 190), (math.cos(a) * 212, math.sin(a) * 212), BLACK, 6)
        s_, col = ("1小时", RED) if f < 0.5 else ("15分钟", GREEN)
        g = pop_scale(T - tb(16, k_shrink) - 0.5) if f >= 0.5 else 1.0
        with K.at(c, 0, 290, 0, g):
            K.text(c, s_, 0, 0, 80, "hand", col)
    return None


ev(j, k_clk, clock16, "wood_high", 0.7)
b.hit(j, k_shrink, "kick", 0.85, "会议时钟缩到十五分钟")
b.shots[j].shake = [(k_shrink, 8.0)]

# ================================================================ 屏 17：评论区——最没用的会；几条吐槽；下一讲预告（打地鼠）
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
b.path(j, 0, 0.8, wb.bubble(cx, cy - 440, 1000, 200, -1), BLACK, 9, sfx="wood_high")
k_c1 = kq(j, wt(26, 0, 0.2), 1)
b.text(j, k_c1, k_c1 + 1.3, "你开过最没用的会？", cx, cy - 440, 64, RED, sfx="pop")
k_gr = nx(j, wt(27, 0, 0.1), k_c1 + 1)
GRIPES = [("又是这个会", cx - 280, cy - 160, -4), ("开了三小时", cx + 250, cy - 200, 3), ("没结论", cx + 60, cy - 10, -2)]
L.note(*[g[0] for g in GRIPES])
for n, (s_, x, y, rot) in enumerate(GRIPES):
    ev(j, k_gr + n, L.pop_bubble(s_, x, y, j, k_gr + n, 56, BLACK, tail=-1 if n % 2 == 0 else 1),
       ("pop", "pop", "wood_high")[n], 0.6)
# 2026-11 收尾鼓励（第 28 句）：镜头下移；一串脚印走到车间，小李手里的话筒变大；预告卡整体下移 DY
DY = 760
k_e = nx(j, wt(28, 0, 0.0), k_gr + 2)
b.move(j, k_e, (cx, cy + 800, Z), 1.1)
k_e1 = k_e + 2
k_walk = nx(j, wt(28, 0, 0.55), k_e1)
k_mic = nx(j, wt(28, 1, 0.3), k_walk + 1)
k_big = nx(j, wt(28, 2, 0.6), k_mic)
GY17 = cy + 760
X0_17, X1_17 = cx - 420, cx - 90
FEET17 = [(X0_17 + 30 + i * 70, GY17 + 30 - (i % 2) * 26) for i in range(5)]


def gemba17(c, kk, T, cx=cx, cy=cy):
    """小李从左边走到车间门口；脚印一个个留下；拿起话筒，话筒变大、冒声波。"""
    sc = pop_scale(T - tb(17, k_e1))
    if sc <= 0:
        return None
    with at_pop(c, cx, GY17 - 150, sc):
        c.drawPath(factory_path(cx + 330, GY17, 300, 250), K.paint("#FFFFFF"))
        c.drawPath(factory_path(cx + 330, GY17, 300, 250), wb.marker(BLACK, 7))
        K.text(c, "车间", cx + 330, GY17 + 50, 46, "hand", BLUE)
        t0 = tb(17, k_walk)
        tw = tb(17, k_walk + 2) - t0
        for i, (x, y) in enumerate(FEET17):
            a = clamp01((T - t0 - (i + 0.5) * tw / 5) / 0.12)
            if a > 0:
                foot(c, x, y, 90, 0.8, GRAY, a)
        x, dy, _ = walk(T, t0, tw, X0_17, X1_17, 12)
        s = 0.8
        hy = GY17 - 290 * s
        g = ease_out(clamp01((T - tb(17, k_big)) / 0.35))
        held = T >= tb(17, k_mic)
        rh = (x + 110 * s, hy + 70 * s) if held else None
        c.save()
        c.translate(0, dy)
        draw_li(c, x, GY17, s, "smile" if held else "flat", rh=rh)
        if held:
            ms = pop_scale(T - tb(17, k_mic)) * (1 + 0.7 * g)
            mx, my = rh[0] + 6, rh[1] - 30
            with K.at(c, mx, my, 20, ms):
                c.drawRoundRect(skia.Rect.MakeXYWH(-9, 0, 18, 70), 8, 8, K.paint(BLACK))
                c.drawCircle(0, -10, 24, K.paint("#9AA0AC"))
                c.drawCircle(0, -10, 24, wb.marker(BLACK, 5))
            if g > 0:
                for n in range(3):
                    r = 60 + n * 38 + 10 * math.sin(T * 6 + n)
                    arc = skia.Path()
                    arc.addArc(skia.Rect.MakeXYWH(mx - r + 20, my - 40 - r, 2 * r, 2 * r), -40, 50)
                    c.drawPath(arc, wb.marker(ORANGE, 7, g * (1 - n * 0.2)))
        c.restore()
    return None


ev(j, k_e1, gemba17, "pop", 0.6)
b.hit(j, k_walk, "wood_low", 0.6, "脚印走向车间")
b.hit(j, k_walk + 1, "wood_high", 0.5, "脚印走向车间")
b.hit(j, k_mic, "pop", 0.6, "拿起话筒")
ev(j, k_big, L.pop_text("说话更有分量", cx, cy + 300, 70, BLUE, j, k_big), "ding", 0.7)
k_n = nx(j, wt(29, 0, 0.15), k_big)
b.path(j, k_n, k_n + 0.6, rect(cx, cy + 300 + DY, 1000, 330, 24), BLUE, 8, sfx="wood_high")
b.text(j, k_n + 0.5, k_n + 0.8, "下一讲", cx, cy + 180 + DY, 52, BLUE)
b.text(j, k_n + 0.8, k_n + 1.6, "问题修好了", cx, cy + 265 + DY, 64, BLACK)
b.text(j, k_n + 1.6, k_n + 2.6, "为什么又回来了？", cx, cy + 350 + DY, 64, BLACK)


def moles17(c, kk, T, cx=cx, cy=cy):
    """预告卡两侧打地鼠：洞里的地鼠轮流冒头。"""
    t0 = tb(17, k_n + 1)
    if T < t0:
        return None
    for n, x in enumerate((cx - 400, cx + 400)):
        y = cy + 400 + DY
        c.drawOval(skia.Rect.MakeXYWH(x - 60, y - 14, 120, 30), K.paint("#3A3F48"))
        ph = (T - t0) * 1.6 + n * 0.5
        up = max(0.0, math.sin(ph * math.pi))
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x - 70, y - 200, x + 70, y))
        my = y + 60 - 110 * up
        c.drawCircle(x, my, 44, K.paint("#B07A44"))
        c.drawCircle(x, my, 44, wb.marker(BLACK, 6))
        for dx in (-14, 14):
            c.drawCircle(x + dx, my - 8, 5, K.paint(BLACK))
        c.drawCircle(x, my + 8, 8, K.paint("#E58A8A"))
        c.restore()
    return None


b.custom(j, k_n + 1, k_n + 1.3, moles17)

# ================================================================ 收尾
L.finish(cover_shot=1, square_shot=9, notes=NOTES)
L.export(globals())
