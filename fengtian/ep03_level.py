"""《丰田模式》03 均衡：为什么总是忙一阵闲一阵？（白板手绘 + AI 旁白，竖屏 2:3）

曲线故事：一条“忙闲曲线”贯穿全片。
- 0–3 秒：系列开场“丰田模式”四字，缓推到小李的月初 / 月底，上方一条过山车轨道，小李坐车起起落落；
- drop：第 2 屏每天的工作量柱子忽高忽低，“不均衡”红印章砸下（重击 + 震屏 + 闪白）；
- 书中做法：三种浪费三张卡片 → 前两张变灰、第三张是“根” → 周一全是蓝车、周五全是橙车（打叉）
  → 车子飞起来重新掺着排，每天一样高，拉一条平线；
- 龟兔赛跑：兔子猛冲后睡觉，插着“丰田”小旗的乌龟一直在走；
- 为什么更快：同一条曲线，镜头先停在尖峰（累了出错返工），再移到低谷（人和机器干等），拉远两头各盖一个“亏”；
- 说回我们：小李的一年曲线先全景，再沿曲线依次推到三个尖峰（报销、项目、健身）→ 冲上山顶出错受伤
  → 领导派活、三级台阶 → 三步做法 → 新曲线变平，小李在线上走 → 评论区比曲线 + 下一讲预告。
文案见 fengtian/PLAN.md「### 03 均衡」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import numpy as np
import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, draw_worker, pop_scale,
                             walk, wobble)
from whiteboard import engine as wb
from whiteboard.engine import P, book, check, circle, cross, join, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)；区块相同的屏共用画面
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "丰田模式 · 书中做法", 2),
    ([3], "丰田模式 · 书中做法", 3),
    ([4], "丰田模式 · 书中做法", 3),
    ([5, 6], "丰田模式 · 书中做法", 4),
    ([7], "丰田模式 · 书中做法", 4),
    ([8, 9], "书中比方", 5),
    ([10, 11], "为什么排平更快", 6),
    ([12, 13], "为什么排平更快", 6),
    ([14, 15], "说回我们自己", 7),
    ([16], "说回我们自己", 7),
    ([17], "说回我们自己", 7),
    ([18, 19], "说回我们自己", 8),
    ([20, 21], "说回我们自己", 9),
    ([22], "做法一 · 示意", 10),
    ([23], "做法二 · 示意", 11),
    ([24], "做法三 · 示意", 12),
    ([25], "不再崩溃", 13),
    ([26, 27, 28], "评论区见", 14),
]

L = C.Lesson("03", SCREENS, drop_screen=2, board_size=(5000, 11800), extra_hold={1: 1.0, 14: 0.9})
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

Z = 0.72
# 各区块中心（区块 6、7 是横向的长曲线，另有专门坐标）
R = {0: (2600, 800), 1: (900, 900), 2: (900, 2500), 3: (2500, 2500), 4: (4100, 2500), 5: (4100, 4100),
     8: (4100, 7700), 9: (2500, 7700), 10: (900, 7700), 11: (900, 9300), 12: (2500, 9300), 13: (4100, 9300),
     14: (4100, 10900)}

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 4——使工作负荷均衡（平准化 heijunka）；书中把浪费分为 muda（无附加价值）、muri（人员设备超负荷）、"
    "mura（不均衡），并指出只盯 muda 会让另两种更严重；平准化排产把几种车型混着排，每天的量差不多；书中用龟兔赛跑作比。",
    "车型用蓝、橙、绿三色小车示意；小李、小王、领导为虚构人物，日历、“半小时”“五分钟”为示意。",
]

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
def at_pop(c, x, y, sc, sy=None):
    """以 (x, y) 为中心缩放（里面照常用白板绝对坐标画）。"""
    c.save()
    c.translate(x, y)
    c.scale(sc, sc if sy is None else sy)
    c.translate(-x, -y)
    try:
        yield
    finally:
        c.restore()


def label(j, k0, s, x, y, size=70, color=BLACK, sfx=None):
    b.text(j, k0, k0 + 0.1 + 0.12 * len(s), s, x, y, size, color, sfx=sfx)


def smooth(pts) -> skia.Path:
    """过各点的平滑曲线（Catmull-Rom 转三次贝塞尔）。"""
    p = skia.Path()
    p.moveTo(*pts[0])
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else pts[i + 1]
        p.cubicTo(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                  p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1])
    return p


def moon(c, x, y, r=50, alpha=1.0):
    m = skia.Path()
    m.addCircle(x, y, r)
    m2 = skia.Path()
    m2.addCircle(x + r * 0.5, y - r * 0.3, r * 0.87)
    mp = skia.Op(m, m2, skia.PathOp.kDifference_PathOp)
    c.drawPath(mp, K.paint("#FFE08A", alpha))
    c.drawPath(mp, wb.marker(ORANGE, 6, alpha))


def sweat(c, x, y, s=1.0, alpha=1.0):
    p = skia.Path()
    p.moveTo(x, y - 22 * s)
    p.quadTo(x + 15 * s, y, x, y + 10 * s)
    p.quadTo(x - 15 * s, y, x, y - 22 * s)
    c.drawPath(p, K.paint("#BFD5F2", alpha))
    c.drawPath(p, wb.marker(BLUE, 4, alpha))


def paper(c, x, y, w, h, alpha=1.0, rot=0.0, lines=3, fill="#FFFFFF", color=BLACK):
    with K.at(c, x, y, rot):
        c.drawPath(wb.doc(0, 0, w, h, lines), K.paint(fill, alpha))
        c.drawPath(wb.doc(0, 0, w, h, lines), wb.marker(color, 6, alpha))


def box(c, x, yb, w=120, h=90, alpha=1.0, fill="#F1DDB8", color="#A9773E", rot=0.0):
    """纸箱：(x, yb) 为底边中点。"""
    with K.at(c, x, yb - h / 2, rot):
        r = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
        c.drawRoundRect(r, 8, 8, K.paint(fill, alpha))
        c.drawRoundRect(r, 8, 8, wb.marker(color, 6, alpha))
        c.drawLine(-w / 2, -h / 2 + 20, w / 2, -h / 2 + 20, wb.marker(color, 4, alpha))


CAR = {"A": ("#D5E3F7", BLUE), "B": ("#FBE0C6", ORANGE), "C": ("#D3EDDC", GREEN)}


def car(c, x, yb, kind, alpha=1.0, rot=0.0):
    """小车（侧视）：(x, yb) 为车轮底部中点，宽 150、高 60。"""
    fill, col = CAR[kind]
    with K.at(c, x, yb, rot):
        cab = P((-42, -38), (-24, -60), (30, -60), (48, -38), close=True)
        c.drawPath(cab, K.paint(fill, alpha))
        c.drawPath(cab, wb.marker(col, 5, alpha))
        body = skia.Rect.MakeXYWH(-70, -40, 140, 28)
        c.drawRoundRect(body, 10, 10, K.paint(fill, alpha))
        c.drawRoundRect(body, 10, 10, wb.marker(col, 6, alpha))
        for dx in (-38, 38):
            c.drawCircle(dx, -12, 12, K.paint("#FFFFFF", alpha))
            c.drawCircle(dx, -12, 12, wb.marker(BLACK, 5, alpha))


def machine(c, x, yb, s=1.0, alpha=1.0, gear_rot=0.0, idle=False):
    """机器：(x, yb) 为底边中点；齿轮可转。"""
    col = "#8A8F99" if idle else BLACK
    r = skia.Rect.MakeXYWH(x - 120 * s, yb - 200 * s, 240 * s, 200 * s)
    c.drawRoundRect(r, 14, 14, K.paint("#EEF1F5", alpha))
    c.drawRoundRect(r, 14, 14, wb.marker(col, 7, alpha))
    gx, gy = x - 40 * s, yb - 110 * s
    with K.at(c, gx, gy, gear_rot):
        for i in range(8):
            a = i * math.pi / 4
            c.drawLine(math.cos(a) * 30 * s, math.sin(a) * 30 * s, math.cos(a) * 52 * s, math.sin(a) * 52 * s,
                       wb.marker(col, 9, alpha))
        c.drawCircle(0, 0, 36 * s, K.paint("#FFFFFF", alpha))
        c.drawCircle(0, 0, 36 * s, wb.marker(col, 6, alpha))
        c.drawCircle(0, 0, 10 * s, K.paint(col, alpha))
    c.drawCircle(x + 70 * s, yb - 150 * s, 14 * s, K.paint(RED if not idle else "#C9CED6", alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x + 45 * s, yb - 100 * s, 50 * s, 60 * s), 6, 6, wb.marker(col, 5, alpha))


def stack_pts(fn, x0, x1, step=20):
    return [(x, fn(x)) for x in np.arange(x0, x1 + 0.1, step)]


# ================================================================ 屏 0：系列开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：月初刷手机，月底熬夜；一年像坐过山车
cx, cy = R[1]
j = L.scene(1, (cx, cy - 20, 0.8))
SOFA = (cx - 270, cy + 330)
DESK1 = (cx + 290, cy + 250)


def sofa1(c, sc, T):
    x, y = SOFA
    with at_pop(c, x, y, sc):
        for r in ((x - 215, y - 130, 430, 115), (x - 215, y - 25, 430, 75), (x - 255, y - 85, 50, 135),
                  (x + 205, y - 85, 50, 135)):
            rr = skia.Rect.MakeXYWH(*r)
            c.drawRoundRect(rr, 18, 18, K.paint("#CFE0F5"))
            c.drawRoundRect(rr, 18, 18, wb.marker(BLUE, 7))
        for dx in (-200, 200):
            c.drawLine(x + dx, y + 50, x + dx, y + 85, wb.marker(BLACK, 8))


b.custom(j, 0, 0.3, pop_fn(j, 0, sofa1), sfx="wood_high")
k_early = kb(j, wt(0, 0, 0.55), lo=1)
k_late = kb(j, wt(0, 1, 0.1), lo=k_early + 2)


def li_sofa(c, sc, T):
    """月初：小李躺在沙发上刷手机（头在左），手指上下划。"""
    s = 0.8
    x, y = SOFA[0] + 160, SOFA[1] - 32
    flick = 10 * math.sin((T - tb(1, k_early)) * 9)
    with at_pop(c, SOFA[0], SOFA[1], sc):
        with K.at(c, x, y, -90):
            hy = -290 * s
            phone = (80 * s, hy + 30 * s)
            draw_li(c, 0, 0, s, "smile", rh=(phone[0] - 10 * s, phone[1] + 30 * s + flick * 0.3),
                    lh=(70 * s, hy + 120 * s))
            c.drawRoundRect(skia.Rect.MakeXYWH(phone[0] - 14 * s, phone[1] - 26 * s, 28 * s, 52 * s), 6, 6,
                            K.paint("#2E3440"))
            c.drawCircle(phone[0] + 34 * s, phone[1], 30 * s, K.paint("#9CC3F5", 0.35, blur=12))


b.custom(j, k_early, k_early + 0.3, pop_fn(j, k_early, li_sofa), sfx="pop")
b.custom(j, k_early, k_early + 0.3, L.pop_text("月初", SOFA[0], cy - 40, 80, BLUE, j, k_early))


def li_desk(c, sc, T):
    """月底：小李在台灯下熬夜，满头汗。"""
    x, y, s = DESK1[0] + 30, DESK1[1] + 120, 0.82
    with at_pop(c, DESK1[0], DESK1[1], sc):
        hy = y - 290 * s
        tap = 10 * math.sin((T - tb(1, k_late)) * 16)
        draw_li(c, x, y, s, "sad", lh=(x - 90 * s, DESK1[1] - 20 + tap), rh=(x + 90 * s, DESK1[1] - 20 - tap))
        sweat(c, x + 60 * s, hy - 10 * s, 1.0)
        front = skia.Rect.MakeXYWH(DESK1[0] - 200, DESK1[1], 400, 125)
        c.drawRect(front, K.paint("#EAD7B5"))
        c.drawRect(front, wb.marker("#A9773E", 7))
        top = skia.Rect.MakeXYWH(DESK1[0] - 215, DESK1[1] - 12, 430, 24)
        c.drawRoundRect(top, 8, 8, K.paint("#C89B63"))
        c.drawRoundRect(top, 8, 8, wb.marker("#8A5A2B", 6))
        lx, ly = DESK1[0] - 150, DESK1[1]
        cone = P((lx + 40, ly - 150), (lx + 200, ly - 4), (lx - 10, ly - 4), close=True)
        c.drawPath(cone, K.paint("#FFE9A8", 0.6))
        c.drawPath(P((lx - 30, ly), (lx, ly - 100), (lx + 40, ly - 150)), wb.marker(BLACK, 8))
        c.drawPath(P((lx + 10, ly - 180), (lx + 75, ly - 140), (lx + 40, ly - 120), close=True), K.paint(BLACK))
        moon(c, DESK1[0] + 170, DESK1[1] - 330, 42)


b.custom(j, k_late, k_late + 0.3, pop_fn(j, k_late, li_desk), sfx="pop")
b.custom(j, k_late, k_late + 0.3, L.pop_text("月底", DESK1[0] - 60, cy - 40, 80, RED, j, k_late))
b.hit(j, k_late + 1, "wood_low", 0.6, "月底熬夜敲键盘")

# 过山车轨道
TRACK_PTS = [(cx - 500, cy - 230), (cx - 320, cy - 450), (cx - 110, cy - 170), (cx + 100, cy - 480), (cx + 310, cy - 180),
             (cx + 470, cy - 380)]
TRACK = smooth(TRACK_PTS)
TM = skia.PathMeasure(TRACK, False)
TLEN = TM.getLength()
k_track = kb(j, wt(1, 0, 0.1), lo=k_late + 2)
k_ride = k_track + 1
b.path(j, k_track, k_track + 1, TRACK, ORANGE, 11, sfx="shaker")
# 轨道各极值点的弧长位置
_ext = []
for (px, py) in TRACK_PTS[1:-1]:
    best = min(range(0, int(TLEN), 4), key=lambda d: (TM.getPosTan(d)[0].x() - px) ** 2 + (TM.getPosTan(d)[0].y() - py) ** 2)
    _ext.append(best)
RIDE_D = [0.0] + _ext + [TLEN - 70]


def cart(c, kk, T):
    """小李坐在过山车里：每一拍到达一个高点或低点。"""
    t0 = tb(1, k_ride)
    if T < t0 - 0.3:
        return None
    a = clamp01((T - t0 + 0.3) / 0.3)
    pos = L.beat_pos(T) - L.beat_pos(t0)
    if pos <= 0:
        d = 0.0
    else:
        i = min(int(pos), len(RIDE_D) - 2)
        f = clamp01(pos - i)
        d = lerp(RIDE_D[i], RIDE_D[i + 1], ease_in_out(f))
    pt, tan = TM.getPosTan(d)
    ang = math.degrees(math.atan2(tan.y(), tan.x()))
    with K.at(c, pt.x(), pt.y(), ang, a):
        c.translate(0, -8)
        s = 0.5
        draw_li(c, -5, -18, s, "sad" if tan.y() > 0.3 else "smile",
                lh=(-60 * s, -18 - 380 * s), rh=(60 * s, -18 - 380 * s))
        body = P((-70, -60), (-60, 0), (60, 0), (75, -60), close=True)
        c.drawPath(body, K.paint("#F6C3BE"))
        c.drawPath(body, wb.marker(RED, 7))
        for dx in (-40, 40):
            c.drawCircle(dx, 4, 12, K.paint("#FFFFFF"))
            c.drawCircle(dx, 4, 12, wb.marker(BLACK, 5))
    return None


b.custom(j, k_ride, k_ride + 0.3, cart, sfx="bongo_low")
for i in range(1, len(RIDE_D) - 1):
    b.hit(j, k_ride + i, ("wood_high", "tom")[i % 2], 0.55, "过山车到高点 / 低点")
L.note("月初", "月底")

# ================================================================ 屏 2：每天的量忽高忽低，drop 时“不均衡”印章砸下
cx, cy = R[2]
j = L.scene(2, (cx, cy + 20, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
b.path(j, 0, 0.6, book(cx - 420, cy - 450, 150, 100), GREEN, 7, sfx="wood_low")
b.text(j, 0.6, 1.4, "丰田模式", cx - 160, cy - 450, 76, GREEN)
AX2 = (cx - 450, cy + 360)
b.path(j, 1, 1.8, join(P((AX2[0], AX2[1] - 560), (AX2[0], AX2[1]), (cx + 470, AX2[1])),
                       P((cx + 440, AX2[1] - 18), (cx + 470, AX2[1]), (cx + 440, AX2[1] + 18))), BLACK, 9,
       sfx="wood_high")
HEIGHTS = [420, 90, 360, 60, 470, 130]
BAR_X = [cx - 360 + i * 160 for i in range(6)]
k_bar0 = 2
for i in range(6):
    b.hit(j, k_bar0 + i, ("wood_low", "wood_high")[i % 2], 0.6, "一天的工作量柱子长出来")


def bars2(c, kk, T):
    for i, (x, h) in enumerate(zip(BAR_X, HEIGHTS)):
        g = ease_out(clamp01((T - tb(2, k_bar0 + i)) / 0.25))
        if g <= 0:
            continue
        hh = h * g
        tall = h > 300
        r = skia.Rect.MakeXYWH(x - 50, AX2[1] - hh, 100, hh)
        c.drawRoundRect(r, 8, 8, K.paint("#F6C3BE" if tall else "#D5E3F7"))
        c.drawRoundRect(r, 8, 8, wb.marker(RED if tall else BLUE, 7))
    return None


b.custom(j, k_bar0, k_bar0 + 0.3, bars2)
k_wave = kb(j, wt(2, 0, 0.6), lo=k_bar0 + 6)
WAVE2 = smooth([(BAR_X[0] - 60, AX2[1] - HEIGHTS[0] + 40)] + [(x, AX2[1] - h - 30) for x, h in zip(BAR_X, HEIGHTS)] +
               [(BAR_X[-1] + 70, AX2[1] - HEIGHTS[-1] + 30)])
b.path(j, k_wave, k_wave + 1, WAVE2, ORANGE, 10, sfx="shaker")
b.custom(j, KD, KD + 0.3, L.stamp("不均衡", cx + 60, cy - 260, 116, j, KD), sfx="kick", gain=0.95)

# ================================================================ 屏 3：浪费有三种——白做的、累垮的、忽多忽少的
cx, cy = R[3]
j = L.scene(3, (cx, cy + 20, Z))
b.path(j, 0, 0.6, book(cx - 420, cy - 450, 150, 100), GREEN, 7, sfx="wood_low")
CARD_X = [cx - 330, cx, cx + 330]
CARD_Y = cy - 30
k_title3 = kb(j, wt(3, 1, 0.25), lo=1)
k_ic = [kb(j, wt(3, 1, 0.8), lo=k_title3 + 1)]
k_ic.append(kb(j, wt(3, 2, 0.4), lo=k_ic[0] + 1))
k_ic.append(kb(j, wt(3, 3, 0.5), lo=k_ic[1] + 1))
b.custom(j, k_title3, k_title3 + 0.3, L.pop_text("三种浪费", cx + 40, cy - 450, 96, RED, j, k_title3), sfx="pop")
S34 = {}


def card_bg(c, x, y, gray, hot):
    r = skia.Rect.MakeXYWH(x - 145, y - 160, 290, 320)
    c.drawRoundRect(r, 22, 22, K.paint("#FFFFFF"))
    c.drawRoundRect(r, 22, 22, wb.marker(RED if hot else BLACK, 10 if hot else 7))


def icon_waste(c, x, y, T):
    """白做的：一张纸掉进垃圾桶。"""
    paper(c, x - 20, y - 60, 110, 130, rot=-14, lines=3)
    bx, by = x + 10, y + 120
    c.drawPath(P((bx - 70, by - 120), (bx - 55, by), (bx + 55, by), (bx + 70, by - 120)), wb.marker(BLACK, 8))
    c.drawLine(bx - 85, by - 120, bx + 85, by - 120, wb.marker(BLACK, 8))
    for dx in (-25, 0, 25):
        c.drawLine(bx + dx, by - 95, bx + dx * 0.8, by - 18, wb.marker(BLACK, 5))


def icon_tired(c, x, y, T):
    """累垮的：小王顶着一摞箱子，被压矮，冒汗。"""
    s = 0.48
    fy = y + 140
    with at_pop(c, x, fy, 1.0, 0.82 + 0.02 * math.sin(T * 5)):
        draw_worker(c, x, fy, s, mood="sad", lh=(x - 50, fy - 290 * s - 40), rh=(x + 50, fy - 290 * s - 40))
    top = fy - 290 * s * 0.82 - 60
    for i in range(3):
        box(c, x + (i % 2) * 8 - 4, top - i * 46, 110, 46)
    sweat(c, x + 52, fy - 210, 0.9)


def icon_wave(c, x, y, T):
    """忽多忽少：一条忽高忽低的线 + 上下箭头。"""
    pts = [(x - 120, y + 20), (x - 75, y - 90), (x - 30, y + 80), (x + 15, y - 110), (x + 60, y + 60), (x + 115, y - 60)]
    c.drawPath(smooth(pts), wb.marker(ORANGE, 11))
    c.drawPath(wb.arrow((x - 100, y + 130), (x - 100, y + 70), 0, 20), wb.marker(BLACK, 6))
    c.drawPath(wb.arrow((x + 100, y + 70), (x + 100, y + 130), 0, 20), wb.marker(BLACK, 6))


ICONS = [icon_waste, icon_tired, icon_wave]
NAMES = ["白做的", "累垮的", "忽多忽少"]
L.note(*NAMES)


def card_fn(i):
    def fn(c, kk, T):
        sc = pop_scale(T - tb(3, k_ic[i]))
        if sc <= 0:
            return None
        x = CARD_X[i]
        gray = "gray" in S34 and T >= tb(4, S34["gray"]) and i < 2
        hot = "root" in S34 and T >= tb(4, S34["root"]) and i == 2
        grow = 1.0 + (0.1 * ease_out_back_c(clamp01((T - tb(4, S34["root"])) / 0.35)) if hot else 0.0)
        with at_pop(c, x, CARD_Y, sc * grow):
            card_bg(c, x, CARD_Y, gray, hot)
            ICONS[i](c, x, CARD_Y - 20, T)
            if gray:
                g = clamp01((T - tb(4, S34["gray"])) / 0.3)
                c.drawRoundRect(skia.Rect.MakeXYWH(x - 145, CARD_Y - 160, 290, 320), 22, 22, K.paint("#E3E6EA", 0.72 * g))
        a = clamp01(sc)
        col = "#9AA0AC" if gray else (RED if i == 2 else BLACK)
        K.text(c, NAMES[i], x, CARD_Y + 220, 64 if i < 2 else 60, "hand", col, a)
        return None
    return fn


def ease_out_back_c(x):
    from engine.gfx import ease_out_back
    return ease_out_back(x)


for i in range(3):
    b.custom(j, k_ic[i], k_ic[i] + 0.3, card_fn(i), sfx=("wood_high", "tom", "rim")[i])

# ================================================================ 屏 4：很多公司只盯第一种；第三种才是根
j = L.scene(4, (cx, cy + 40, Z))
k_look = kb(j, wt(4, 0, 0.5), lo=1)
S34["gray"] = kb(j, wt(4, 1, 0.4), lo=k_look + 1)
S34["root"] = kb(j, wt(4, 2, 0.55), lo=S34["gray"] + 1)


def magnifier4(c, sc, T):
    x, y = CARD_X[0] + 60, CARD_Y - 90
    bob = 8 * math.sin((T - tb(4, k_look)) * 4)
    fade = 1 - 0.6 * clamp01((T - tb(4, S34["gray"])) / 0.3)
    with at_pop(c, x, y + bob, sc):
        c.drawCircle(x, y + bob, 78, K.paint("#E4EDFA", 0.35 * fade))
        c.drawCircle(x, y + bob, 78, wb.marker(BLUE, 10, fade))
        c.drawLine(x + 56, y + bob + 56, x + 125, y + bob + 125, wb.marker(BLUE, 18, fade))
    return None


b.custom(j, k_look, k_look + 0.3, pop_fn(j, k_look, magnifier4), sfx="pop")
b.custom(j, k_look, k_look + 0.3, L.pop_text("只盯这个", CARD_X[0], cy - 330, 66, BLUE, j, k_look))
b.hit(j, S34["gray"], "wood_low", 0.7, "前两张卡片变灰")
b.hit(j, S34["root"], "tom", 0.8, "第三张卡片放大、描红")
k_gen = S34["root"] + 1
b.custom(j, k_gen, k_gen + 0.3, L.stamp("根", CARD_X[2], cy + 410, 120, j, k_gen, rot=6), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_gen, 12.0)]

# ================================================================ 屏 5：排得很平——它不会周一全做 A、周五全做 B（打叉）
cx, cy = R[4]
j = L.scene(5, (cx, cy - 30, 0.8))
GY = cy + 330
DAYS_X = [cx - 400 + i * 200 for i in range(5)]
CH = 66
k_flat_t = kb(j, wt(5, 0, 0.75), lo=0)
b.custom(j, k_flat_t, k_flat_t + 0.3, L.pop_text("排得很平", cx, cy - 470, 96, RED, j, k_flat_t), sfx="pop")
b.path(j, 1 if k_flat_t != 1 else 2, (1 if k_flat_t != 1 else 2) + 0.8,
       P((cx - 520, GY), (cx + 520, GY)), BLACK, 9, sfx="wood_high")
for i, d in enumerate(("周一", "周二", "周三", "周四", "周五")):
    b.text(j, 2.2 + i * 0.12, 2.4 + i * 0.12, d, DAYS_X[i], GY + 60, 54, BLACK)
kA = kb(j, wt(6, 0, 0.3), lo=3)
kB = kb(j, wt(6, 1, 0.15), lo=kA + 2)
kC = kA + 1
kX = kb(j, wt(6, 1, 0.95), lo=kB + 1)
INIT = [("A", 0, i) for i in range(6)] + [("C", 2, i) for i in range(3)] + [("B", 4, i) for i in range(6)]
FINAL_DAYS = ["ABC", "ABA", "BCA", "BAB", "CAB"]
# 每辆车的终点：同型号按出场顺序依次分配
_pool = {t: [n for n, (kind, _, _) in enumerate(INIT) if kind == t] for t in "ABC"}
FINAL = [None] * len(INIT)
for dI, s_ in enumerate(FINAL_DAYS):
    for lvl, t in enumerate(s_):
        FINAL[_pool[t].pop()] = (dI, lvl)
S56 = {}


def car_start(n):
    kind, d, lvl = INIT[n]
    k0 = {"A": kA, "C": kC, "B": kB}[kind]
    return tb(5, k0) + lvl * 0.09


def cars56(c, kk, T):
    t_mix = tb(6, S56["mix"]) if "mix" in S56 else 1e9
    t_land = tb(6, S56["mix"] + 1) if "mix" in S56 else 1e9
    for n, (kind, d, lvl) in enumerate(INIT):
        f = pop_scale(T - car_start(n), 0.22)
        if f <= 0:
            continue
        x0, y0 = DAYS_X[d], GY - lvl * CH
        x1, y1 = DAYS_X[FINAL[n][0]], GY - FINAL[n][1] * CH
        st = t_mix + (n % 5) * 0.03
        g = ease_in_out(clamp01((T - st) / max(0.05, t_land - st)))
        x, y = lerp(x0, x1, g), lerp(y0, y1, g) - math.sin(g * math.pi) * 160
        rot = math.sin(g * math.pi) * (8 if n % 2 else -8)
        with at_pop(c, x, y, f):
            car(c, x, y - 2, kind, rot=rot)
    return None


b.custom(j, kA, kA + 0.3, cars56, sfx="wood_low")
b.hit(j, kC, "wood_high", 0.6, "周三几辆绿车")
b.hit(j, kB, "wood_low", 0.7, "周五一摞橙车")
L.note("排得很平")


def cross5(c, kk, T):
    t0 = tb(5, kX)
    f = clamp01((T - t0) / 0.35)
    fade = 1 - clamp01((T - (tb(6, S56["mix"]) - 0.3)) / 0.3) if "mix" in S56 else 1
    part, tip = wb.partial(cross(DAYS_X[2], GY - 220, 260), f)
    c.drawPath(part, wb.marker(RED, 16, fade))
    return tip


b.custom(j, kX, kX + 0.35, cross5, sfx="kick", gain=0.8)
b.shots[j].shake = [(kX, 10.0)]

# ================================================================ 屏 6：几种车掺着排，每天一样高——拉一条平线
j = L.scene(6, (cx, cy - 30, 0.8))
S56["mix"] = kb(j, wt(7, 0, 0.25), lo=1)
b.hit(j, S56["mix"], "shaker", 0.8, "车子飞起来重新排")
b.hit(j, S56["mix"] + 1, "wood_low", 0.85, "车子落定，每天三辆")
k_line6 = kb(j, wt(7, 1, 0.55), lo=S56["mix"] + 2)
LINE6_Y = GY - 3 * CH - 30
b.path(j, k_line6, k_line6 + 0.8, P((cx - 520, LINE6_Y), (cx + 520, LINE6_Y)), GREEN, 10, sfx="ding")
b.path(j, k_line6 + 1, k_line6 + 1.4, check(cx + 470, LINE6_Y - 90, 40), GREEN, 12, sfx="pop", gain=0.7)
b.custom(j, k_line6 + 1, k_line6 + 1.3, L.pop_text("每天差不多", cx - 120, LINE6_Y - 110, 72, GREEN, j, k_line6 + 1))

# ================================================================ 屏 7：龟兔赛跑——兔子猛冲又睡觉，插“丰田”旗的乌龟一直在走
cx, cy = R[5]
j = L.scene(7, (cx, cy + 20, Z))
b.path(j, 0, 0.6, book(cx - 420, cy - 450, 150, 100), GREEN, 7, sfx="wood_low")
HARE_Y, TURT_Y = cy + 20, cy + 380
X0, FIN = cx - 400, cx + 450
b.path(j, 1, 1.8, join(P((cx - 510, HARE_Y), (cx + 510, HARE_Y)), P((cx - 510, TURT_Y), (cx + 510, TURT_Y)),
                       P((FIN, HARE_Y - 200), (FIN, TURT_Y + 20))), BLACK, 8, sfx="wood_high")
k_rt = kb(j, wt(8, 0, 0.75), lo=2)
b.custom(j, k_rt, k_rt + 0.3, L.pop_text("龟兔赛跑", cx + 40, cy - 450, 100, BLACK, j, k_rt), sfx="pop")
k_flag = kb(j, wt(8, 1, 0.65), lo=k_rt + 1)
k_dash = kb(j, wt(9, 0, 0.2), lo=k_flag + 1)
k_sleep = kb(j, wt(9, 1, 0.2), lo=k_dash + 1)
k_on = kb(j, wt(9, 2, 0.3), lo=k_sleep + 1)
HARE_STOP = cx + 60


def draw_hare(c, x, y, s, run=0.0, sleep=0.0, phase=0.0):
    """兔子（侧视，朝右）：(x, y) 为地面中点。"""
    lay = sleep
    by = y - lerp(70, 40, lay) * s
    with K.at(c, x, by, -8 * run):
        body = skia.Rect.MakeXYWH(-75 * s, -40 * s, 150 * s, lerp(80, 70, lay) * s)
        c.drawOval(body, K.paint("#FFFFFF"))
        c.drawOval(body, wb.marker(BLACK, 7))
        c.drawCircle(-78 * s, -10 * s, 18 * s, K.paint("#FFFFFF"))
        c.drawCircle(-78 * s, -10 * s, 18 * s, wb.marker(BLACK, 5))
        hx, hy = 70 * s, lerp(-55, -15, lay) * s
        for i, ang in enumerate((-15, 8)):
            a = ang + lerp(0, 70, lay)
            with K.at(c, hx - 10 * s + i * 14 * s, hy - 25 * s, a):
                ear = skia.Rect.MakeXYWH(-13 * s, -95 * s, 26 * s, 95 * s)
                c.drawOval(ear, K.paint("#FFFFFF"))
                c.drawOval(ear, wb.marker(BLACK, 6))
                c.drawOval(skia.Rect.MakeXYWH(-6 * s, -80 * s, 12 * s, 65 * s), K.paint("#F8D3CF"))
        c.drawCircle(hx, hy, 36 * s, K.paint("#FFFFFF"))
        c.drawCircle(hx, hy, 36 * s, wb.marker(BLACK, 7))
        if lay > 0.5:
            c.drawLine(hx + 4 * s, hy - 6 * s, hx + 20 * s, hy - 6 * s, wb.marker(BLACK, 5))
        else:
            c.drawCircle(hx + 12 * s, hy - 8 * s, 5 * s, K.paint(BLACK))
        c.drawCircle(hx + 34 * s, hy + 4 * s, 6 * s, K.paint("#F28B82"))
        if lay < 0.5:
            sw = math.sin(phase * 2 * math.pi) * run
            for dx, sgn in ((-45, 1), (40, -1)):
                c.drawLine(dx * s, 30 * s, (dx + 30 * sw * sgn) * s, 70 * s, wb.marker(BLACK, 8))


def draw_turtle(c, x, y, s, phase=0.0, flag=0.0):
    """乌龟（侧视，朝右）：(x, y) 为地面中点；flag>0 时背上插“丰田”小旗。"""
    for i, dx in enumerate((-55, -25, 25, 55)):
        sw = 12 * math.sin(phase * 2 * math.pi + (i % 2) * math.pi)
        c.drawLine(x + dx * s, y - 28 * s, x + dx * s + sw * s, y, wb.marker(GREEN, 10))
    hx, hy = x + 100 * s, y - 50 * s
    c.drawLine(x + 70 * s, y - 35 * s, hx, hy, wb.marker(GREEN, 14))
    c.drawCircle(hx, hy, 26 * s, K.paint("#CDEBD7"))
    c.drawCircle(hx, hy, 26 * s, wb.marker(GREEN, 6))
    c.drawCircle(hx + 9 * s, hy - 6 * s, 4.5 * s, K.paint(BLACK))
    shell = skia.Path()
    shell.addArc(skia.Rect.MakeXYWH(x - 90 * s, y - 130 * s, 180 * s, 200 * s), 180, 180)
    shell.close()
    c.drawPath(shell, K.paint("#A8D8B9"))
    c.drawPath(shell, wb.marker(GREEN, 8))
    for dx in (-40, 0, 40):
        c.drawLine(x + dx * s, y - 30 * s, x + dx * 0.6 * s, y - 100 * s, wb.marker(GREEN, 4))
    if flag > 0:
        fx, fy = x - 10 * s, y - 128 * s
        with K.at(c, fx, fy, 0, flag):
            c.drawLine(0, 0, 0, -120 * s, wb.marker(BLACK, 6))
            r = skia.Rect.MakeXYWH(0, -120 * s, 120 * s, 64 * s)
            c.drawRect(r, K.paint("#FFFFFF"))
            c.drawRect(r, wb.marker(RED, 6))
            K.text(c, "丰田", 60 * s, -88 * s, 40 * s, "hand", RED)


L.note("丰田", "Zz")


def hare_x(T):
    t0 = tb(7, k_dash)
    return lerp(X0, HARE_STOP, ease_out(clamp01((T - t0) / 0.55)))


def hare7(c, kk, T):
    sc = pop_scale(T - tb(7, 2))
    if sc <= 0:
        return None
    t0, ts = tb(7, k_dash), tb(7, k_sleep)
    run = 1.0 if t0 <= T < t0 + 0.6 else 0.0
    sleep = ease_in_out(clamp01((T - ts) / 0.3))
    x = hare_x(T)
    with at_pop(c, x, HARE_Y, sc):
        if run:
            for i in range(3):
                yy = HARE_Y - 50 - i * 30
                c.drawLine(x - 110 - i * 12, yy, x - 210 - i * 12, yy, wb.marker(BLACK, 6, 0.7))
        draw_hare(c, x, HARE_Y, 1.3, run=run, sleep=sleep, phase=(T - t0) * 4)
    if T >= ts:
        for i in range(2):
            a = clamp01((T - ts - 0.2 - i * 0.25) / 0.2)
            dy = 10 * math.sin((T - ts) * 3 + i)
            K.text(c, "Z", x + 150 + i * 55, HARE_Y - 170 - i * 60 + dy, 60 + i * 18, "hand", BLUE, a)
    return None


def turtle_x(T):
    t0, t1 = tb(7, k_flag) + 0.3, tb(7, k_on) + 1.2
    return X0 + 680 * clamp01((T - t0) / (t1 - t0))


def turtle7(c, kk, T):
    sc = pop_scale(T - tb(7, 2) - 0.12)
    if sc <= 0:
        return None
    x = turtle_x(T)
    moving = tb(7, k_flag) + 0.3 < T < tb(7, k_on) + 1.2
    flag = pop_scale(T - tb(7, k_flag))
    with at_pop(c, x, TURT_Y, sc):
        draw_turtle(c, x, TURT_Y, 1.25, phase=(T * 1.6) if moving else 0.0, flag=flag)
    return None


b.custom(j, 2, 2.3, hare7, sfx="pop")
b.custom(j, 2, 2.3, turtle7)
b.text(j, 2.4, 2.7, "兔子", cx - 440, HARE_Y + 60, 54, BLACK)
b.text(j, 2.7, 3.0, "乌龟", cx - 440, TURT_Y + 60, 54, GREEN)
b.hit(j, k_flag, "ding", 0.8, "乌龟背上插“丰田”旗")
b.hit(j, k_dash, "bongo_high", 0.85, "兔子猛冲")
b.hit(j, k_sleep, "pop", 0.7, "兔子躺下睡觉")
for kk_ in range(k_sleep + 1, k_on + 3, 2):
    b.hit(j, kk_, "wood_low", 0.45, "乌龟一步一步往前")

# ================================================================ 屏 8–9：同一条曲线，尖峰（累了出错返工）→ 低谷（干等）→ 拉远两头都亏
PK = (1500, 4100)
VL = (2500, 4100)
cyc = PK[1]
CURVE8 = smooth([(PK[0] - 620, cyc - 110), (PK[0] - 330, cyc - 210), (PK[0], cyc - 420), (PK[0] + 300, cyc - 250),
                 (PK[0] + 520, cyc - 100), (VL[0] - 220, cyc - 40), (VL[0], cyc - 20), (VL[0] + 260, cyc - 70),
                 (VL[0] + 600, cyc - 300)])
j = L.scene(8, (PK[0], cyc + 20, Z))
b.path(j, 0, 1.5, CURVE8, RED, 11, sfx="shaker")
k_q8 = kb(j, wt(10, 1, 0.2), lo=2)
b.custom(j, k_q8, k_q8 + 0.3, L.slam_text("反而更快？", PK[0], cyc - 520, 96, RED, j, k_q8), sfx="rim")
k_busy = kb(j, wt(11, 0, 0.5), lo=k_q8 + 1)
k_drop = kb(j, wt(11, 1, 0.65), lo=k_busy + 1)
k_redo = kb(j, wt(11, 2, 0.6), lo=k_drop + 1)
WK8 = (PK[0] - 60, cyc + 400, 0.95)
DROP8 = (PK[0] + 190, cyc + 400)


def worker8(c, sc, T):
    x, y, s = WK8
    hy = y - 290 * s
    t_d = tb(8, k_drop)
    shake = 5 * math.sin(T * 13)
    with at_pop(c, x, y, sc):
        draw_worker(c, x + shake * 0.3, y, s, mood="sad", lh=(x + 40 * s, hy + 150 * s), rh=(x + 150 * s, hy + 150 * s))
        n = 4 if T < t_d - 0.35 else 3
        for i in range(n):
            box(c, x + 95 * s + (i % 2) * 6, hy + 150 * s - i * 62, 120, 62)
        for i in range(2):
            ph = ((T - tb(8, k_busy)) * 1.4 + i * 0.5) % 1.0
            sweat(c, x - 70 * s - i * 20, hy - 30 * s + ph * 60, 0.9, 1 - ph)
    if T >= t_d - 0.35:
        g = clamp01((T - (t_d - 0.35)) / 0.35)
        x0, y0 = x + 100 * s, hy + 150 * s - 3 * 62
        bx = lerp(x0, DROP8[0], g)
        by = lerp(y0, DROP8[1], g * g)
        box(c, bx, by, 120, 62, rot=lerp(0, 25, g) + wobble(T - t_d, 6, 25, 8))
    return None


b.custom(j, k_busy, k_busy + 0.3, pop_fn(j, k_busy, worker8), sfx="pop")
b.custom(j, k_busy, k_busy + 0.3, L.pop_text("忙", PK[0] - 270, cyc - 120, 90, RED, j, k_busy))
b.hit(j, k_drop, "tom", 0.9, "箱子摔到地上")
b.path(j, k_drop + 0.2, k_drop + 0.6, cross(DROP8[0] + 10, DROP8[1] - 140, 46), RED, 12)
b.shots[j].shake = [(k_drop, 10.0)]
b.path(j, k_redo, k_redo + 0.6, C.loop_arrow(PK[0] + 330, cyc + 40, 56), ORANGE, 11, sfx="wood_low")
b.custom(j, k_redo + 0.5, k_redo + 0.8, L.pop_text("返工", PK[0] + 330, cyc + 160, 72, ORANGE, j, k_redo + 0.5))

j = L.scene(9, (VL[0], cyc + 20, Z))
k_idle = kb(j, wt(12, 0, 0.4), lo=1)
k_wait = kb(j, wt(12, 1, 0.5), lo=k_idle + 1)
MC9 = (VL[0] - 220, cyc + 400)
WK9 = (VL[0] + 180, cyc + 400, 0.95)
CLK9 = (VL[0] + 330, cyc + 50, 80)


def machine9(c, sc, T):
    with at_pop(c, MC9[0], MC9[1], sc):
        machine(c, MC9[0], MC9[1], 1.0, idle=True)
    return None


b.custom(j, k_idle, k_idle + 0.3, pop_fn(j, k_idle, machine9), sfx="wood_high")
b.custom(j, k_idle, k_idle + 0.3, L.pop_text("闲", VL[0] - 330, cyc - 170, 90, BLUE, j, k_idle))
b.custom(j, k_wait, k_wait + 0.3, L.figure(draw_worker, j, k_wait, *WK9, mood="flat",
                                           head_dx=lambda T: 8 * math.sin(T * 1.5),
                                           lh=lambda T: (WK9[0] - 40, WK9[1] - 290 * WK9[2] + 150),
                                           rh=lambda T: (WK9[0] + 40, WK9[1] - 290 * WK9[2] + 150)), sfx="pop")


def clock9(c, sc, T):
    x, y, r = CLK9
    m = (T - tb(9, k_wait)) * 240
    with at_pop(c, x, y, sc):
        c.drawCircle(x, y, r, K.paint("#FFFFFF"))
        c.drawPath(wb.clock(x, y, r), wb.marker(BLACK, 7))
        c.drawPath(wb.hands_at(x, y, r, (3 + m / 60) % 12, m % 60), wb.marker(BLUE, 7))
    return None


b.custom(j, k_wait + 1, k_wait + 1.3, pop_fn(j, k_wait + 1, clock9), sfx="wood_low", gain=0.6)
k_zoom = kb(j, wt(13, 0, 0.0), lo=k_wait + 2)
b.move(j, k_zoom, (PK[0] + 470, cyc - 40, 0.44), 0.9)
k_k1 = max(kb(j, wt(13, 1, 0.3), lo=k_zoom + 2), k_zoom + 2)
b.custom(j, k_k1, k_k1 + 0.3, L.stamp("亏", PK[0] - 380, cyc - 440, 130, j, k_k1, rot=-8), sfx="kick", gain=0.85)
b.custom(j, k_k1 + 1, k_k1 + 1.3, L.stamp("亏", VL[0], cyc - 260, 130, j, k_k1 + 1, rot=7), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_k1, 10.0), (k_k1 + 1, 10.0)]

# ================================================================ 屏 10–12：小李的一年曲线（全景 → 沿曲线推到三个尖峰：报销、项目、健身）
YC = 5900
YB = YC + 180
PEAKS = [1200, 2400, 3600]
PH = [560, 650, 520]


def year_y(x):
    return YB - sum(h * math.exp(-((x - p) / 190) ** 2) for p, h in zip(PEAKS, PH)) + 18 * math.sin(x / 140)


YEAR = smooth(stack_pts(year_y, 470, 4300, 30))
AXY = YB + 130
j = L.scene(10, (2330, YC - 380, 0.21))
b.path(j, 0, 0.8, join(P((330, YB - 820), (330, AXY), (4330, AXY)), P((4290, AXY - 30), (4330, AXY), (4290, AXY + 30)),
                       P((300, YB - 790), (330, YB - 820), (360, YB - 790))), BLACK, 14, sfx="wood_high")
b.text(j, 0.8, 1.0, "忙", 455, YB - 780, 150, RED)
b.text(j, 1.0, 1.3, "1月", 455, AXY + 140, 120, BLACK)
b.text(j, 1.3, 1.7, "12月", 4150, AXY + 140, 120, BLACK)
k_cv = kb(j, wt(14, 1, 0.05), lo=2)
b.path(j, k_cv, k_cv + 2, YEAR, RED, 18, sfx="shaker")
b.hit(j, k_cv + 1, "wood_low", 0.5, "曲线爬过第一个尖峰")
b.custom(j, k_cv + 2, k_cv + 2.3, L.pop_text("小李的一年", 2330, YB - 1110, 240, BLACK, j, k_cv + 2), sfx="pop")
k_mv = kb(j, wt(15, 0, 0.0), lo=k_cv + 3)
b.move(j, k_mv, (PEAKS[0] + 20, YC - 100, Z), 1.0)
P1 = PEAKS[0]
k_bx = k_mv + 2
k_rc = kb(j, wt(15, 0, 0.75), lo=k_bx)
if k_rc == k_bx:
    k_rc = k_bx + 1
k_night = kb(j, wt(15, 1, 0.2), lo=k_rc + 1)
k_wrong = kb(j, wt(15, 1, 0.85), lo=k_night + 1)
b.custom(j, k_bx, k_bx + 0.3, L.pop_text("报销", P1, YB - PH[0] - 120, 96, RED, j, k_bx), sfx="pop")
RC = (P1 - 340, year_y(P1 - 340) - 10)


def receipts(c, kk, T):
    for i in range(6):
        t0 = tb(10, k_rc) + i * 0.09
        f = pop_scale(T - t0, 0.2)
        if f <= 0:
            continue
        y = RC[1] - i * 30
        with K.at(c, RC[0] + ((i * 37) % 23 - 11), y - 15 - (1 - f) * 40, (i % 3 - 1) * 5, 1.0):
            r = skia.Rect.MakeXYWH(-80, -15, 160, 30)
            c.drawRect(r, K.paint("#FFFFFF", clamp01(f * 2)))
            c.drawRect(r, wb.marker(BLACK, 5, clamp01(f * 2)))
            c.drawLine(-60, 0, 30, 0, wb.marker("#9AA0AC", 3, clamp01(f * 2)))
    return None


b.custom(j, k_rc, k_rc + 0.4, receipts, sfx="wood_low")
LI10 = (P1 + 330, year_y(P1 + 330), 0.85)


def li10(c, sc, T):
    x, y, s = LI10
    hy = y - 290 * s
    scratch = 10 * math.sin((T - tb(10, k_night)) * 12)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad", rh=(x + 60 * s, hy - 40 * s + scratch), lh=(x - 80 * s, hy + 160 * s))
        sweat(c, x - 60 * s, hy - 20 * s)
    moon(c, P1 - 330, YB - 560, 48, clamp01(sc))
    return None


b.custom(j, k_night, k_night + 0.3, pop_fn(j, k_night, li10), sfx="ding", gain=0.7)
b.custom(j, k_wrong, k_wrong + 0.3, L.pop_text("对不上", RC[0], RC[1] - 260, 72, RED, j, k_wrong), sfx="rim")

# 屏 11：第二个尖峰——项目：前两周慢慢聊，最后三天通宵
P2 = PEAKS[1]
j = L.scene(11, (P2 - 60, YC - 100, Z))
b.custom(j, 0, 0.3, L.pop_text("项目", P2, YB - PH[1] - 120, 96, RED, j, 0), sfx="pop")
CAL = (P2 - 600, YB - 300)          # 日历左上角（整块在曲线左侧平地上方）
CELL = 48
k_cal = kb(j, wt(16, 0, 0.15), lo=1)
k_chat = kb(j, wt(16, 0, 0.7), lo=k_cal + 1)
k_red = kb(j, wt(16, 1, 0.3), lo=k_chat + 1)
cal_parts = []
for r in range(2):
    for i in range(7):
        cal_parts.append(rect(CAL[0] + CELL / 2 + i * CELL, CAL[1] + CELL / 2 + r * CELL, CELL - 8, CELL - 8, 6))
b.path(j, k_cal, k_cal + 0.9, join(*cal_parts), "#9AA0AC", 5, sfx="wood_high")


def chat11(c, sc, T):
    for i, (dx, dy) in enumerate(((60, -110), (250, -150))):
        f = pop_scale(T - tb(11, k_chat) - i * 0.25)
        if f <= 0:
            continue
        x, y = CAL[0] + dx, CAL[1] + dy
        with K.at(c, x, y, 0, f):
            c.drawRoundRect(skia.Rect.MakeXYWH(-70, -38, 140, 76), 30, 30, K.paint("#FFFFFF"))
            c.drawPath(wb.bubble(0, 0, 140, 76, -1 if i == 0 else 1), wb.marker(BLACK, 5))
            for k_ in range(3):
                c.drawCircle(-32 + k_ * 32, 0, 7, K.paint(BLACK))
    return None


b.custom(j, k_chat, k_chat + 0.3, pop_fn(j, k_chat, chat11), sfx="pop", gain=0.6)


def red11(c, kk, T):
    for i in range(3):
        f = C.slam_scale(T - tb(11, k_red + i))
        if f <= 0:
            continue
        x, y = CAL[0] + CELL / 2 + (4 + i) * CELL, CAL[1] + CELL / 2 + 2 * CELL
        with K.at(c, x, y, 0, f):
            c.drawRoundRect(skia.Rect.MakeXYWH(-20, -20, 40, 40), 6, 6, K.paint("#F6C3BE"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-20, -20, 40, 40), 6, 6, wb.marker(RED, 5))
            moon(c, 0, 0, 12)
    return None


b.custom(j, k_red, k_red + 0.3, red11, sfx="rim")
b.hit(j, k_red + 1, "rim", 0.8, "第二个通宵")
b.hit(j, k_red + 2, "kick", 0.8, "第三个通宵")
LI11 = (P2 + 340, year_y(P2 + 340), 0.85)
b.custom(j, k_red, k_red + 0.3, L.figure(draw_li, j, k_red, *LI11, mood="sad",
                                         lh=lambda T: (LI11[0] - 90, LI11[1] - 150 + 10 * math.sin(T * 18)),
                                         rh=lambda T: (LI11[0] + 90, LI11[1] - 150 - 10 * math.sin(T * 18))))
b.custom(j, k_red + 2, k_red + 2.3, L.pop_text("通宵", LI11[0], LI11[1] - 400, 72, RED, j, k_red + 2))

# 屏 12：第三个尖峰——健身：一周不去，周末练到腿软
P3 = PEAKS[2]
j = L.scene(12, (P3 - 60, YC - 100, Z))
b.custom(j, 0, 0.3, L.pop_text("健身", P3, YB - PH[2] - 120, 96, RED, j, 0), sfx="pop")
k_dots = kb(j, wt(17, 1, 0.2), lo=1)
k_lift = kb(j, wt(17, 2, 0.1), lo=k_dots + 1)
k_soft = kb(j, wt(17, 2, 0.75), lo=k_lift + 1)
DOTS = [(P3 - 560 + i * 62, YB - 260) for i in range(5)]


def dots12(c, kk, T):
    for i, (x, y) in enumerate(DOTS):
        f = pop_scale(T - tb(12, k_dots) - i * 0.08)
        if f <= 0:
            continue
        with K.at(c, x, y, 0, f):
            c.drawCircle(0, 0, 24, K.paint("#E3E6EA"))
            c.drawCircle(0, 0, 24, wb.marker("#8A8F99", 5))
            c.drawLine(-12, -12, 12, 12, wb.marker("#8A8F99", 5))
            c.drawLine(12, -12, -12, 12, wb.marker("#8A8F99", 5))
    return None


b.custom(j, k_dots, k_dots + 0.3, dots12, sfx="shaker")
b.custom(j, k_dots, k_dots + 0.3, L.pop_text("一周没去", P3 - 436, YB - 360, 56, "#6B7080", j, k_dots))
LI12 = (P3 + 330, year_y(P3 + 330), 0.85)


def li12(c, sc, T):
    x, y, s = LI12
    soft = ease_out(clamp01((T - tb(12, k_soft)) / 0.25))
    sq = lerp(1.0, 0.72, soft)
    hy = y - 290 * s * sq
    shake = 6 * math.sin(T * 30) * soft
    if soft < 0.5:
        lh, rh = (x - 95 * s, hy - 60 * s), (x + 95 * s, hy - 60 * s)
    else:
        lh, rh = (x - 95 * s, hy + 120 * s), (x + 95 * s, hy + 120 * s)
    with at_pop(c, x, y, sc):
        c.save()
        c.translate(shake, 0)
        draw_li(c, x, y, s, "sad" if soft > 0.5 else "flat", squash=sq,
                lh=(lh[0], y - (y - lh[1]) / sq), rh=(rh[0], y - (y - rh[1]) / sq))
        c.restore()
        bar_y = lh[1] - 4
        c.drawLine(lh[0] - 40, bar_y, rh[0] + 40, bar_y, wb.marker(BLACK, 9))
        for xx in (lh[0] - 34, rh[0] + 34):
            c.drawRoundRect(skia.Rect.MakeXYWH(xx - 14, bar_y - 40, 28, 80), 6, 6, K.paint(BLACK))
        if soft > 0:
            for i in range(2):
                c.drawLine(x - 70 - i * 20, y - 30 - i * 26, x - 95 - i * 20, y - 30 - i * 26, wb.marker(BLACK, 5, soft))
                c.drawLine(x + 70 + i * 20, y - 30 - i * 26, x + 95 + i * 20, y - 30 - i * 26, wb.marker(BLACK, 5, soft))
    return None


b.custom(j, k_lift, k_lift + 0.3, pop_fn(j, k_lift, li12), sfx="tom")
b.hit(j, k_soft, "wood_low", 0.8, "小李腿一软蹲下")
b.custom(j, k_soft + 1, k_soft + 1.3, L.pop_text("腿软", LI12[0] - 10, LI12[1] - 400, 80, RED, j, k_soft + 1), sfx="pop")

# ================================================================ 屏 13：总想最后冲一把——冲上山顶，出错、伤身
cx, cy = R[8]
j = L.scene(13, (cx, cy + 20, Z))
MT_PTS = [(cx - 540, cy + 420), (cx - 300, cy + 330), (cx - 60, cy + 120), (cx + 160, cy - 230), (cx + 260, cy - 300),
          (cx + 380, cy - 120), (cx + 540, cy + 300)]
MT = smooth(MT_PTS)
MTM = skia.PathMeasure(MT, False)
b.path(j, 0, 1.2, MT, RED, 11, sfx="wood_high")
k_think = kb(j, wt(18, 1, 0.1), lo=2)
k_run = k_think + 1
k_err13 = kb(j, wt(19, 1, 0.5), lo=k_run + 3)
k_hurt = kb(j, wt(19, 2, 0.55), lo=k_err13 + 1)
b.custom(j, k_think, k_think + 0.3, L.pop_bubble("冲一把就行", cx - 220, cy - 330, j, k_think, 72, BLUE, tail=-1),
         sfx="pop")
TOP_D = None
_best = min(range(0, int(MTM.getLength()), 4), key=lambda d: MTM.getPosTan(d)[0].y())
TOP_D = _best


def li13(c, kk, T):
    t0 = tb(13, k_run)
    if T < tb(13, k_think):
        return None
    sc = pop_scale(T - tb(13, k_think))
    t_top = tb(13, k_err13) - 0.15
    g = clamp01((T - t0) / max(0.3, t_top - t0))
    d = lerp(MTM.getLength() * 0.08, TOP_D - 60, ease_in_out(g))
    pt, tan = MTM.getPosTan(d)
    x, y = pt.x(), pt.y()
    hurt = T >= tb(13, k_hurt)
    run = 0 < g < 1
    bob = -abs(math.sin((T - t0) * 9)) * 12 if run else 0.0
    s = 0.72
    hy = y - 290 * s
    with at_pop(c, x, y, sc):
        c.translate(0, bob)
        draw_li(c, x, y, s, "sad" if hurt else "flat", back=True,
                lh=(x - 80 * s, hy + (90 if run else 160) * s + 20 * math.sin(T * 9) * run),
                rh=(x + 80 * s, hy + (90 if run else 160) * s - 20 * math.sin(T * 9) * run))
        if hurt:
            f = pop_scale(T - tb(13, k_hurt))
            with K.at(c, x + 30 * s, hy - 10 * s, 35, f):
                c.drawRoundRect(skia.Rect.MakeXYWH(-40, -14, 80, 28), 12, 12, K.paint("#F6D9B8"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-40, -14, 80, 28), 12, 12, wb.marker("#B07A44", 4))
                for dx in (-8, 8):
                    c.drawCircle(dx, 0, 3, K.paint("#B07A44"))
    return None


b.custom(j, k_think, k_think + 0.3, li13)
b.hit(j, k_run, "bongo_low", 0.8, "小李往山顶冲")
TOPP = MTM.getPosTan(TOP_D)[0]
b.path(j, k_err13, k_err13 + 0.4, cross(TOPP.x() + 150, TOPP.y() - 120, 60), RED, 14, sfx="kick", gain=0.85)
b.custom(j, k_err13 + 0.3, k_err13 + 0.6, L.pop_text("出错", TOPP.x() + 150, TOPP.y() - 230, 72, RED, j, k_err13 + 0.3))
b.shots[j].shake = [(k_err13, 12.0)]
b.hit(j, k_hurt, "rim", 0.8, "小李头上贴创可贴")
b.custom(j, k_hurt, k_hurt + 0.3, L.pop_text("伤身体", cx - 330, cy + 120, 72, RED, j, k_hurt))

# ================================================================ 屏 14：很多忙由不得你——领导派活，小李点头；能排平的部分，试试这三步
cx, cy = R[9]
j = L.scene(14, (cx, cy + 20, Z))
DK14 = (cx - 200, cy + 200)
LI14 = (cx - 330, cy + 360, 0.9)
BO14 = (cx + 380, cy + 360, 0.95)
k_li14 = 1
k_boss14 = kb(j, wt(20, 1, 0.2), lo=2)
k_give14 = kb(j, wt(20, 2, 0.55), lo=k_boss14 + 1)
k_nod14 = k_give14 + 1
k_three = kb(j, wt(21, 1, 0.45), lo=k_nod14 + 1)


def li14(c, sc, T):
    x, y, s = LI14
    nod = 0.94 + 0.06 * math.cos(clamp01((T - tb(14, k_nod14)) / 0.6) * math.pi * 2) if T >= tb(14, k_nod14) else 1.0
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "flat", squash=nod)
        c.drawRect(skia.Rect.MakeXYWH(DK14[0] - 50, DK14[1], 350, 140), K.paint("#FBFBF9"))
        c.drawPath(join(P((DK14[0] - 60, DK14[1]), (DK14[0] + 300, DK14[1])),
                        P((DK14[0] - 40, DK14[1]), (DK14[0] - 40, DK14[1] + 140)),
                        P((DK14[0] + 280, DK14[1]), (DK14[0] + 280, DK14[1] + 140))), wb.marker(BLACK, 9))
    return None


b.custom(j, k_li14, k_li14 + 0.3, pop_fn(j, k_li14, li14), sfx="wood_high")
b.text(j, 1.4, 1.7, "小李", LI14[0] - 20, LI14[1] + 85, 64, BLACK)
b.custom(j, k_boss14, k_boss14 + 0.3, L.figure(draw_boss, j, k_boss14, *BO14, mood="flat",
                                               lh=lambda T: (BO14[0] - 130, BO14[1] - 290 * BO14[2] + 120)
                                               if tb(14, k_give14) - 0.5 <= T < tb(14, k_give14) + 0.3
                                               else (BO14[0] - 70, BO14[1] - 120 * BO14[2])), sfx="wood_low")
b.text(j, k_boss14 + 0.4, k_boss14 + 0.7, "领导", BO14[0], BO14[1] + 85, 64, BLACK)
TASKS14 = [(DK14[0] + 130 + (i % 2) * 14, DK14[1] - 30 - i * 38) for i in range(3)]


def tasks14(c, kk, T):
    t1 = tb(14, k_give14)
    for i, (x1, y1) in enumerate(TASKS14):
        st = t1 - 0.45 + i * 0.0
        g = ease_in_out(clamp01((T - st) / 0.45))
        if T < st:
            continue
        x0, y0 = BO14[0] - 150, BO14[1] - 290 * BO14[2] + 100 - i * 38
        x, y = lerp(x0, x1, g), lerp(y0, y1, g) - math.sin(g * math.pi) * 110
        with K.at(c, x, y, lerp(-10, (i - 1) * 4, g)):
            r = skia.Rect.MakeXYWH(-90, -18, 180, 36)
            c.drawRoundRect(r, 6, 6, K.paint("#FFFFFF"))
            c.drawRoundRect(r, 6, 6, wb.marker(BLACK, 5))
            c.drawLine(-60, 0, 40, 0, wb.marker("#9AA0AC", 3))
    return None


b.custom(j, k_give14 - 1, k_give14 - 0.7, tasks14)
b.hit(j, k_give14, "wood_low", 0.8, "任务落到小李桌上")
b.hit(j, k_nod14, "pop", 0.6, "小李点头")
STAIRS = (cx - 270, cy - 30)
SW, SH = 180, 90


def stairs_path():
    x, y = STAIRS
    pts = [(x, y)]
    for i in range(3):
        pts += [(x + i * SW, y - i * SH - SH), (x + (i + 1) * SW, y - i * SH - SH)]
    pts.append((x + 3 * SW, y))
    return P(*pts, close=True)


b.custom(j, k_three, k_three + 0.3, L.slam_text("试试这三步", cx, cy - 480, 100, RED, j, k_three), sfx="kick", gain=0.8)
b.path(j, k_three + 0.3, k_three + 1.0, stairs_path(), BLUE, 9)
for i in range(3):
    kk_ = k_three + 1 + i
    b.custom(j, kk_, kk_ + 0.3, L.pop_text(str(i + 1), STAIRS[0] + SW / 2 + i * SW, STAIRS[1] - i * SH - SH / 2, 70, BLUE, j, kk_),
             sfx="pop", gain=0.6)

# ================================================================ 屏 15：第一，大活拆小块，每天做一点
cx, cy = R[10]
j = L.scene(15, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("① 大活拆小块", cx, cy - 470, 92, BLUE, j, 0), sfx="pop")
GY15 = cy + 340
DX15 = [cx - 400 + i * 200 for i in range(5)]
b.path(j, 1, 1.7, P((cx - 520, GY15), (cx + 520, GY15)), BLACK, 9, sfx="wood_high")
for i, d in enumerate(("周一", "周二", "周三", "周四", "周五")):
    b.text(j, 1.7 + i * 0.12, 1.9 + i * 0.12, d, DX15[i], GY15 + 60, 54, BLACK)
k_big = kb(j, wt(22, 1, 0.1), lo=2)
k_cut = kb(j, wt(22, 1, 0.8), lo=k_big + 1)
k_fall = kb(j, wt(22, 2, 0.3), lo=k_cut + 1)
BRICK = (cx, cy - 170, 800, 150)


def brick15(c, kk, T):
    sc = C.slam_scale(T - tb(15, k_big))
    if sc <= 0:
        return None
    x, y, w, h = BRICK
    split = ease_out(clamp01((T - tb(15, k_cut)) / 0.3))
    for i in range(5):
        st = tb(15, k_fall) + i * 0.27
        g = ease_in_out(clamp01((T - st + 0.4) / 0.4))
        px = x - w / 2 + w / 10 + i * w / 5 + (i - 2) * 22 * split
        py = y
        tx, ty = DX15[i], GY15 - 60
        bx, by = lerp(px, tx, g), lerp(py, ty, g) - math.sin(g * math.pi) * 60
        pw, ph = lerp(w / 5 - 4, 150, g), lerp(h, 120, g)
        with K.at(c, x, y, 0, sc):
            c.translate(-x, -y)
            r = skia.Rect.MakeXYWH(bx - pw / 2, by - ph / 2, pw, ph)
            c.drawRoundRect(r, 10, 10, K.paint("#FBE0C6"))
            c.drawRoundRect(r, 10, 10, wb.marker(ORANGE, 7))
    if 0 < split < 1 or (T >= tb(15, k_cut) and T < tb(15, k_cut) + 0.4):
        for i in range(1, 5):
            cxx = x - w / 2 + i * w / 5
            p = K.paint(RED, 1 - split, 5)
            p.setPathEffect(skia.DashPathEffect.Make([16, 10], 0))
            c.drawLine(cxx, y - h / 2 - 30, cxx, y + h / 2 + 30, p)
    return None


b.custom(j, k_big, k_big + 0.3, brick15, sfx="tom")
b.hit(j, k_cut, "rim", 0.8, "大块切成五小块")
b.hit(j, k_fall, "wood_low", 0.7, "小块落到周一")
b.hit(j, k_fall + 1, "wood_high", 0.6, "小块落到周三")
b.hit(j, k_fall + 2, "wood_low", 0.6, "小块落到周五")
k_ok15 = kb(j, wt(22, 3, 0.6), lo=k_fall + 3)
b.path(j, k_ok15, k_ok15 + 0.4, check(cx + 420, cy - 170, 50), GREEN, 13, sfx="ding")
b.custom(j, k_ok15, k_ok15 + 0.3, L.pop_text("每天一点", cx - 40, cy - 170, 80, GREEN, j, k_ok15))

# ================================================================ 屏 16：第二，每天留半小时，接临时插进来的事
cx, cy = R[11]
j = L.scene(16, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("② 每天留半小时", cx, cy - 470, 88, BLUE, j, 0), sfx="pop")
SCH = (cx - 200, cy + 30, 380, 560)
SLOTS = [SCH[1] - SCH[3] / 2 + 60 + i * 110 for i in range(5)]
EMPTY = 3
k_sch = 1
k_slot = kb(j, wt(23, 1, 0.6), lo=2)
k_boss16 = kb(j, wt(23, 2, 0.1), lo=k_slot + 1)
k_in = k_boss16 + 1
BO16 = (cx + 360, cy + 380, 0.95)


def sched16(c, kk, T):
    x, y, w, h = SCH
    sc = pop_scale(T - tb(16, k_sch))
    if sc <= 0:
        return None
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
        c.drawRoundRect(r, 18, 18, K.paint("#FFFFFF"))
        c.drawRoundRect(r, 18, 18, wb.marker(BLACK, 8))
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 4, y - h / 2 + 4, w - 8, 36), K.paint("#BFD5F2"))
        for i, sy in enumerate(SLOTS):
            if i == EMPTY:
                continue
            f = pop_scale(T - tb(16, k_sch) - 0.2 - i * 0.12, 0.2)
            if f > 0:
                with K.at(c, x, sy + 10, 0, f):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 30, -38, w - 60, 76), 10, 10, K.paint("#D5E3F7"))
                    c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 30, -38, w - 60, 76), 10, 10, wb.marker(BLUE, 5))
        t_s = tb(16, k_slot)
        if T >= t_s:
            a = clamp01((T - t_s) / 0.2)
            p = K.paint(GREEN, a, 6)
            p.setPathEffect(skia.DashPathEffect.Make([16, 10], 0))
            c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 + 30, SLOTS[EMPTY] + 10 - 38, w - 60, 76), 10, 10, p)
            if T < tb(16, k_in):
                K.text(c, "半小时", x, SLOTS[EMPTY] + 10, 50, "hand", GREEN, a)
    return None


L.note("半小时")
b.custom(j, k_sch, k_sch + 0.3, sched16, sfx="wood_high")
b.hit(j, k_slot, "pop", 0.8, "空出一格")
b.custom(j, k_boss16, k_boss16 + 0.3, L.figure(draw_boss, j, k_boss16, *BO16, mood="flat",
                                               rh=lambda T: (BO16[0] + 60, BO16[1] - 290 * BO16[2] + 170),
                                               lh=lambda T: (BO16[0] - 120, BO16[1] - 290 * BO16[2] + 40)
                                               if T < tb(16, k_in) + 0.2 else (BO16[0] - 60, BO16[1] - 120 * BO16[2])),
         sfx="wood_low")
b.text(j, k_boss16 + 0.4, k_boss16 + 0.7, "领导", BO16[0], BO16[1] + 85, 64, BLACK)


def card16(c, kk, T):
    t1 = tb(16, k_in)
    st = t1 - 0.45
    if T < st - 0.2:
        return None
    g = ease_in_out(clamp01((T - st) / 0.45))
    x0, y0 = BO16[0] - 140, BO16[1] - 290 * BO16[2] + 10
    x1, y1 = SCH[0], SLOTS[EMPTY] + 10
    x, y = lerp(x0, x1, g), lerp(y0, y1, g) - math.sin(g * math.pi) * 160
    w = lerp(150, SCH[2] - 60, g)
    with K.at(c, x, y, lerp(12, 0, g), pop_scale(T - (st - 0.2))):
        c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -38, w, 76), 10, 10, K.paint("#F6C3BE"))
        c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -38, w, 76), 10, 10, wb.marker(RED, 6))
        K.text(c, "临时", 0, 0, 46, "hand", RED)
    if T >= t1:
        K.ripple(c, x1, y1, T - t1, GREEN, 200, 6, 0.8, 0.45)
    return None


L.note("临时")
b.custom(j, k_in - 1, k_in - 0.7, card16)
b.hit(j, k_in, "clap", 0.8, "临时任务落进空格")
b.path(j, k_in + 1, k_in + 1.4, check(SCH[0] + 250, SLOTS[EMPTY] + 10, 40), GREEN, 12, sfx="ding", gain=0.7)

# ================================================================ 屏 17：第三，周五花五分钟看下周，哪天挤就提前挪开
cx, cy = R[12]
j = L.scene(17, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("③ 周五看下周", cx, cy - 470, 92, BLUE, j, 0), sfx="pop")
LI17 = (cx - 400, cy + 380, 0.85)
GY17 = cy + 300
DX17 = [cx - 150 + i * 140 for i in range(5)]
COUNT17 = [2, 2, 5, 2, 1]
k_li17 = 1
k_timer = kb(j, wt(24, 1, 0.3), lo=2)
k_wk = kb(j, wt(24, 2, 0.2), lo=k_timer + 1)
k_jam = kb(j, wt(24, 2, 0.8), lo=k_wk + 1)
k_mv17 = kb(j, wt(24, 3, 0.4), lo=k_jam + 1)
b.custom(j, k_li17, k_li17 + 0.3, L.figure(draw_li, j, k_li17, *LI17,
                                           mood=lambda T: "smile" if T >= tb(17, k_mv17) else "flat",
                                           rh=lambda T: (LI17[0] + 130, LI17[1] - 290 * LI17[2] + 100)), sfx="wood_high")
b.text(j, 1.4, 1.7, "小李", LI17[0], LI17[1] + 85, 64, BLACK)


TIMER17 = (LI17[0] + 20, cy - 180, 80)


def timer17(c, sc, T):
    x, y, r = TIMER17
    f = clamp01((T - tb(17, k_timer)) / 2.5)
    with at_pop(c, x, y, sc):
        c.drawCircle(x, y, r, K.paint("#FFFFFF"))
        c.drawArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -90, 360 * f * 5 / 60, True, K.paint("#FFE9A8"))
        c.drawPath(wb.clock(x, y, r), wb.marker(BLACK, 7))
        a = -math.pi / 2 + 2 * math.pi * f * 5 / 60
        c.drawLine(x, y, x + math.cos(a) * r * 0.75, y + math.sin(a) * r * 0.75, wb.marker(RED, 7))
        K.text(c, "5分钟", x, y + r + 50, 50, "hand", BLACK)
    return None


L.note("5分钟")
b.custom(j, k_timer, k_timer + 0.3, pop_fn(j, k_timer, timer17), sfx="ding", gain=0.6)
b.path(j, k_wk - 0.9 if k_wk - 0.9 > k_timer + 0.3 else k_wk, (k_wk - 0.9 if k_wk - 0.9 > k_timer + 0.3 else k_wk) + 0.6,
       P((DX17[0] - 80, GY17), (DX17[-1] + 80, GY17)), BLACK, 8)
MOVE17 = {3: 1, 4: 3}         # 周三最上面两块：一块挪到周二、一块挪到周五


def week17(c, kk, T):
    t_w, t_j, t_m = tb(17, k_wk), tb(17, k_jam), tb(17, k_mv17)
    for d in range(5):
        a = pop_scale(T - t_w - d * 0.07, 0.25)
        if a <= 0:
            continue
        K.text(c, "一二三四五"[d], DX17[d], GY17 + 55, 50, "hand", BLACK, clamp01(a))
        for lvl in range(COUNT17[d]):
            x, y = DX17[d], GY17 - 30 - lvl * 62
            if d == 2 and lvl in MOVE17:
                td = MOVE17[lvl]
                tl = COUNT17[td] + (0 if lvl == 3 else 0)
                g = ease_in_out(clamp01((T - t_m - (lvl - 3) * 0.2) / 0.5))
                x = lerp(x, DX17[td], g)
                y = lerp(y, GY17 - 30 - tl * 62, g) - math.sin(g * math.pi) * 80
            jam = d == 2 and t_j <= T < t_m + 0.5
            with K.at(c, x, y, 0, a):
                r = skia.Rect.MakeXYWH(-55, -26, 110, 52)
                c.drawRoundRect(r, 8, 8, K.paint("#F6C3BE" if jam else "#D5E3F7"))
                c.drawRoundRect(r, 8, 8, wb.marker(RED if jam else BLUE, 5))
    return None


L.note("一", "二", "三", "四", "五")
b.custom(j, k_wk, k_wk + 0.3, week17, sfx="wood_low")
b.custom(j, k_jam, k_jam + 0.3, L.pop_text("挤", DX17[2] + 100, GY17 - 400, 90, RED, j, k_jam), sfx="rim")
b.hit(j, k_mv17, "shaker", 0.7, "周三的两块挪开")
b.path(j, k_mv17 + 1, k_mv17 + 1.4, check(DX17[2], GY17 - 250, 40), GREEN, 12, sfx="ding", gain=0.7)

# ================================================================ 屏 18：每天差不多忙——新曲线变平，小李在线上走
cx, cy = R[13]
j = L.scene(18, (cx, cy + 20, Z))
OLD18 = smooth([(x_, cy - 150 + (y_ - cy) * 0.8) for x_, y_ in
                [(cx - 520, cy + 60), (cx - 380, cy - 20), (cx - 270, cy - 330), (cx - 160, cy + 40), (cx + 20, cy + 70),
                 (cx + 140, cy - 380), (cx + 260, cy + 50), (cx + 400, cy - 260), (cx + 520, cy + 40)]])
NEW_Y = cy + 330
k_new = kb(j, wt(25, 0, 0.3), lo=1)
k_walk18 = k_new + 1
k_fade = kb(j, wt(25, 1, 0.55), lo=k_walk18 + 1)


def old18(c, kk, T):
    f = clamp01(kk)
    fade = 1 - 0.75 * clamp01((T - tb(18, k_fade)) / 0.4)
    part, tip = wb.partial(OLD18, f)
    c.drawPath(part, wb.marker("#9AA0AC", 9, fade))
    return tip


b.custom(j, 0, 1.0, old18, sfx="wood_low")
b.path(j, k_new, k_new + 1, P((cx - 520, NEW_Y), (cx + 520, NEW_Y)), GREEN, 12, sfx="ding")


def li18(c, kk, T):
    t0 = tb(18, k_walk18)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, dy, _ = walk(T, t0, tb(18, k_fade) + 0.8 - t0, R[13][0] - 420, R[13][0] + 300, 12, 2.4)
    s = 0.85
    with at_pop(c, x, NEW_Y, sc):
        c.translate(0, dy)
        draw_li(c, x, NEW_Y, s, "smile", bag=True)
    return None


b.custom(j, k_walk18, k_walk18 + 0.3, li18, sfx="bongo_low")
b.hit(j, k_fade, "shaker", 0.6, "旧曲线淡掉")
b.custom(j, k_fade + 1, k_fade + 1.3, L.pop_text("不再崩溃", cx, NEW_Y + 120, 96, GREEN, j, k_fade + 1), sfx="pop")

# ================================================================ 屏 19：评论区比曲线 + 下一讲预告
cx, cy = R[14]
j = L.scene(19, (cx, cy + 20, Z))
b.path(j, 0, 0.8, wb.bubble(cx, cy - 440, 1000, 240, -1), BLACK, 9, sfx="wood_high")
k_c1 = kb(j, wt(26, 0, 0.2), lo=1)
b.text(j, k_c1, k_c1 + 1.3, "你一年里最忙的是哪几天？", cx, cy - 440, 64, RED, sfx="pop")
k_cv19 = kb(j, wt(27, 1, 0.1), lo=k_c1 + 2)
THUMBS = [(cx - 330, 0.35), (cx, 0.7), (cx + 330, 1.0)]


def thumb(i):
    x, amp = THUMBS[i]

    def draw(c, sc, T):
        y = cy - 120
        with at_pop(c, x, y, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 140, y - 100, 280, 200), 16, 16, K.paint("#FFFFFF"))
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 140, y - 100, 280, 200), 16, 16, wb.marker(BLACK, 6))
            pts = [(x - 115 + n * 23, y + 60 - (amp * 140 if n in (3, 7) else amp * 25 * (n % 2))) for n in range(11)]
            c.drawPath(smooth(pts), wb.marker((GREEN, ORANGE, RED)[i], 8))
    return draw


for i in range(3):
    b.custom(j, k_cv19 + i, k_cv19 + i + 0.3, pop_fn(j, k_cv19 + i, thumb(i)), sfx=("pop", "pop", "pop")[i], gain=0.6)
k_steep = k_cv19 + 3
b.custom(j, k_steep, k_steep + 0.3, L.pop_text("最陡？", THUMBS[2][0], cy - 270, 64, RED, j, k_steep), sfx="ding",
         gain=0.7)
k_n = kb(j, wt(28, 0, 0.15), lo=k_steep + 1)
b.path(j, k_n, k_n + 0.6, rect(cx, cy + 330, 1000, 380, 24), BLUE, 8, sfx="wood_high")
b.text(j, k_n + 0.5, k_n + 0.8, "下一讲", cx, cy + 190, 52, BLUE)
b.text(j, k_n + 0.8, k_n + 1.6, "手上一堆事", cx, cy + 275, 64, BLACK)
b.text(j, k_n + 1.6, k_n + 2.6, "为什么一件也没做完？", cx, cy + 360, 64, BLACK)


def bars19(c, kk, T):
    for i in range(4):
        x = cx - 330 + i * 220
        y = cy + 455
        f = clamp01((T - tb(19, k_n + 2.6) - i * 0.12) / 0.4)
        if f <= 0:
            continue
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 90, y - 14, 180, 28), 14, 14, wb.marker("#9AA0AC", 4))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 88, y - 12, 176 * 0.5 * f, 24), 12, 12, K.paint(ORANGE))
    return None


b.custom(j, k_n + 2.6, k_n + 3.2, bars19)

# ================================================================ 收尾
L.finish(cover_shot=10, notes=NOTES)
L.export(globals())
