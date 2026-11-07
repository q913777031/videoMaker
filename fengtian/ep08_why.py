"""《丰田模式》08 五问：问题修好了，为什么又回来了？（白板手绘 + AI 旁白，竖屏 2:3）

经典问答：大野耐一“机器停了”的五个为什么，一问一答，每问一句画面往下挖一层，挖到底装上过滤网。
2026-11 结构：先问题（痛点 + 身边的例子）→ 书中做法 → 三步办法 → 鼓励。
- 0–3 秒：系列开场钩子，缓推到打地鼠：小李抡锤砸下一个、旁边又冒一个，逐拍三下，“又回来了”砸下；
- 身边的例子（drop）：一排小地鼠冒头；客户投诉发货慢（道歉、催仓库），drop 时下个月“发货慢！”又来，“照样慢”；
  往下挖：订单过三张桌子，每张桌上一个沙漏；五个闹钟叫不醒 → 往下挖：凌晨一点的手机光；
- 书中做法：五张“为什么？”卡片一级级往下排，“五个为什么”砸下；
- 一问一答（屏 6–12 共用一块画面，一根竖井往下挖）：地面上一台机器、大野耐一和车间员工；
  每一问：地下挖开一层，大野耐一顺梯子下到这一层问“为什么？”，这一层画出答案（保险丝 / 轴承 / 油泵 / 泵轴 / 进油口），
  “答”卡片落下，红箭头把上一层的答案连到这一层；第五问铁屑掉进没装网的进油口，红圈；
  修到根：装上过滤网、打勾，镜头拉远看整口井，五层从下往上一层层变绿，机器重新转起来；
- 只问一次：员工换根保险丝就走，日历翻过几天，机器又冒烟；
- 书中观点：杂草剪掉叶子，根还在，换个样子长回来；
- 说回我们：手指指人（打叉）换成指流程（打勾），“问事，不问人”；
- 三步做法 → 锤子放下、洞一个个盖上 → 评论区 + 下一讲预告。
办公室里的同事小王用本模块的 draw_wang（短发、白衬衫、蓝工牌，不戴安全帽，与第 06 讲同一造型）；
安全帽造型（common.draw_worker）只用于车间员工。
文案见 fengtian/PLAN.md「### 08 五问」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, draw_ohno, draw_worker,
                             pop_scale, rest_hands, wobble)
from whiteboard import engine as wb
from whiteboard.engine import P, arrow, check, circle, cross, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "身边的例子", 2),
    ([4], "身边的例子", 3),
    ([5, 6], "身边的例子", 4),
    ([7], "丰田模式 · 书中做法", 5),
    ([8], "经典问答", 6),
    ([9], "五问 · 第一问", 6),
    ([10], "五问 · 第二问", 6),
    ([11], "五问 · 第三问", 6),
    ([12], "五问 · 第四问", 6),
    ([13], "五问 · 第五问", 6),
    ([14], "五问 · 修到根", 6),
    ([15, 16], "只问一次会怎样", 7),
    ([17, 18], "书中观点", 8),
    ([19, 20], "说回我们自己", 9),
    ([21, 22], "做法一 · 示意", 10),
    ([23], "做法二 · 示意", 11),
    ([24], "做法三 · 示意", 12),
    ([25], "不再打地鼠", 13),
    ([26, 27, 28, 29], "评论区见", 14),
]

THEME = FT.get("08")          # 本讲样式（fengtian/theme.py）：薰衣草点阵、开场 mole、转场 pullpush
L = C.Lesson("08", SCREENS, drop_screen=2, board_size=(5400, 16000), extra_hold={1: 0.4, 12: 2.6}, theme=THEME)
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt
Z = 0.72

# 竖井（屏 6–12）：地面 y=G，第 n 层（1–5）中心 CY(n)，层距 D
X, G, D = 2600, 7600, 700
# 其余各屏的区块中心
# 2026-11 新顺序：左列自上而下是问题段（屏 1–4）和书中做法开头（屏 5），右移进竖井（屏 6–12），
# 竖井拉远后进右列（屏 13–16），再沿底部往左（屏 17–18）、往下（屏 19–20）。
R = {0: (2600, 800), 1: (900, 900), 2: (900, 2500), 3: (900, 4100), 4: (900, 5700), 5: (900, 7300),
     13: (4300, 7300), 14: (4300, 8900), 15: (4300, 10500), 16: (4300, 12100), 17: (2600, 12100), 18: (900, 12100),
     19: (900, 13700), 20: (2600, 13700)}

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：书中“持续解决根本问题”部分的根因分析——连问五个为什么，找到根上的原因再动手；"
    "机器停机的五问例子出自大野耐一《丰田生产方式》（保险丝烧断 → 轴承润滑不够 → 润滑泵抽不上油 → 泵轴磨损松动 → 没装过滤网、铁屑进入）。",
    "竖井、梯子、各层画面为示意；小李、小王、员工为虚构人物，发货审批、闹钟等为示意。",
]


def CY(n):
    return G + (n - 0.5) * D


def nbeats(j):
    return L.BOUNDS[j][1] - L.BOUNDS[j][0]


def kq(j, t_local, lo=0):
    """kb，但 lo 超出本屏时夹到最后一拍（防止排期变短时报错）。"""
    return kb(j, t_local, lo=min(lo, nbeats(j) - 1))


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
def at_pop(c, x, y, sc, rot=0.0):
    c.save()
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    c.scale(sc, sc)
    c.translate(-x, -y)
    try:
        yield
    finally:
        c.restore()


def label(j, k0, s, x, y, size=64, color=BLACK, sfx=None):
    b.text(j, k0, k0 + 0.1 + 0.12 * len(s), s, x, y, size, color, sfx=sfx)


def is_int(k):
    return abs(k - round(k)) < 1e-9


def stage_clip(c):
    """把后面的绘制裁在画面的白板舞台内（字幕带以下、页眉以上不画），用于铺满的大块底色。"""
    inv = skia.Matrix()
    if c.getTotalMatrix().invert(inv):
        c.clipRect(inv.mapRect(skia.Rect.MakeLTRB(0, 282, 1080, 1186)))


def fade(T, t0, dur=0.25):
    return clamp01((T - t0) / dur)


# ================================================================ 办公室里的小王（不戴安全帽，与第 06 讲同一造型）

WANG_SHIRT, HAIR = "#FFFFFF", "#2E2A28"


def draw_wang(c, x, y, s, lh=None, rh=None, mood="flat", head_dx=0.0, alpha=1.0):
    """同事小王（办公室）：齐耳短发 + 橙色发卡、白衬衫蓝描边、蓝工牌、蓝色四肢；不戴安全帽。"""
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


# ================================================================ 道具

GRAY = "#9AA0AC"
SOIL, SOIL_LINE, CAVE = "#EAD9BA", "#A9875A", "#FFFDF7"
GREEN_FILL, RED_FILL, NOTE_FILL = "#DCEFD9", "#F6C3BE", "#FFE58A"
MOLE, WOOD = "#9C6B43", "#8A6A3E"
METAL = "#7D8592"


def hole(c, x, y, w=200, h=56, alpha=1.0, lid=0.0):
    """地洞（椭圆）：lid 0–1 时盖子从上方落下盖住。"""
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawOval(r, K.paint("#3B3330", alpha))
    c.drawOval(r, wb.marker(BLACK, 6, alpha))
    if lid > 0:
        dy = (1 - ease_out(lid)) * -120
        lr = skia.Rect.MakeXYWH(x - w / 2 - 8, y - h / 2 - 6 + dy, w + 16, h + 12)
        c.drawOval(lr, K.paint(BOARD_C, alpha * clamp01(lid * 3)))
        c.drawOval(lr, wb.marker(WOOD, 6, alpha * clamp01(lid * 3)))
        c.drawLine(x - w * 0.3, y + dy, x + w * 0.3, y + dy, wb.marker(WOOD, 4, alpha * clamp01(lid * 3)))


BOARD_C = C.BOARD_C


def mole(c, x, y, up, alpha=1.0, r=58, squash=1.0):
    """地鼠：(x, y) 为洞中心；up 0–1 为探出高度；squash<1 被砸扁。"""
    if up <= 0:
        return
    w = 200
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x - w, y - 600, x + w, y))
    c.translate(x, y)
    c.scale(1.0 + (1 - squash) * 0.6, squash)
    c.translate(-x, -y)
    hy = y + r * 1.1 - up * r * 2.3
    body = skia.Rect.MakeLTRB(x - r * 0.95, hy, x + r * 0.95, y + 30)
    c.drawRoundRect(body, r * 0.9, r * 0.9, K.paint(MOLE, alpha))
    c.drawRoundRect(body, r * 0.9, r * 0.9, wb.marker(BLACK, 6, alpha))
    for sgn in (-1, 1):
        c.drawCircle(x + sgn * r * 0.7, hy - r * 0.55, r * 0.25, K.paint(MOLE, alpha))
        c.drawCircle(x + sgn * r * 0.7, hy - r * 0.55, r * 0.25, wb.marker(BLACK, 5, alpha))
    c.drawCircle(x, hy, r, K.paint(MOLE, alpha))
    c.drawCircle(x, hy, r, wb.marker(BLACK, 6, alpha))
    for sgn in (-1, 1):
        c.drawCircle(x + sgn * r * 0.33, hy - r * 0.12, r * 0.1, K.paint(BLACK, alpha))
    c.drawOval(skia.Rect.MakeXYWH(x - r * 0.2, hy + r * 0.15, r * 0.4, r * 0.26), K.paint("#F2A7B0", alpha))
    for sgn in (-1, 1):
        c.drawLine(x + sgn * r * 0.3, hy + r * 0.3, x + sgn * r * 0.85, hy + r * 0.22, wb.marker(BLACK, 3, alpha))
    c.restore()
    front = skia.Path()
    front.addArc(skia.Rect.MakeXYWH(x - w / 2, y - 28, w, 56), 0, 180)
    c.drawPath(front, wb.marker(BLACK, 6, alpha))


def hammer(c, px, py, ang, ln=210, alpha=1.0, s=1.0):
    """玩具锤：手握处 (px, py)，ang 为锤柄方向（度，屏幕坐标）。"""
    a = math.radians(ang)
    ex, ey = px + ln * s * math.cos(a), py + ln * s * math.sin(a)
    c.drawLine(px, py, ex, ey, wb.marker(WOOD, 14 * s, alpha))
    with K.at(c, ex, ey, ang):
        r = skia.Rect.MakeXYWH(-34 * s, -62 * s, 68 * s, 124 * s)
        c.drawRoundRect(r, 14 * s, 14 * s, K.paint(RED, alpha))
        c.drawRoundRect(r, 14 * s, 14 * s, wb.marker(BLACK, 6, alpha))
        c.drawLine(-34 * s, -40 * s, 34 * s, -40 * s, wb.marker("#FFFFFF", 5, alpha * 0.8))
    return ex, ey


def stars(c, x, y, dt, n=6, rmax=110):
    """撞击后的小星星（0.4 秒）。"""
    if not 0 <= dt < 0.4:
        return
    k = ease_out(dt / 0.4)
    for i in range(n):
        a = math.radians(-160 + i * 140 / (n - 1))
        r0, r1 = 40 + rmax * k * 0.5, 40 + rmax * k
        c.drawLine(x + r0 * math.cos(a), y + r0 * math.sin(a), x + r1 * math.cos(a), y + r1 * math.sin(a),
                   wb.marker(ORANGE if i % 2 else YELLOW, 8, 1 - k * 0.8))


def calendar(c, x, y, old, new, f, w=200, h=210, alpha=1.0):
    """台历：f 0–1 为翻页进度（旧页从下往上翻起）。"""
    top = y - h / 2
    body = skia.Rect.MakeXYWH(x - w / 2, top, w, h)
    c.drawRoundRect(body, 14, 14, K.paint("#FFFFFF", alpha))
    c.drawRoundRect(body, 14, 14, wb.marker(BLACK, 7, alpha))
    K.text(c, new, x, y + 25, 96 if len(new) < 3 else 66, "hand", BLACK, alpha)
    if f < 1:
        sy = 1 - ease_in_out(f)
        pg = skia.Rect.MakeXYWH(x - w / 2 + 4, top + 50, w - 8, (h - 54) * sy)
        c.drawRect(pg, K.paint("#FFFFFF" if f == 0 else "#F3F3F3", alpha))
        if sy > 0.15:
            with K.at(c, x, top + 50 + (h - 54) * sy / 2, 0, 1.0, sy):
                K.text(c, old, 0, 0, 96 if len(old) < 3 else 66, "hand", BLACK, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, top, w, 50), 14, 14, K.paint(RED, alpha))
    for dx in (-50, 50):
        c.drawLine(x + dx, top - 18, x + dx, top + 16, wb.marker(BLACK, 8, alpha))


def machine(c, x, yb, ang, lamp_c, alpha=1.0, w=320, h=300):
    """机器（正视）：(x, yb) 为底边中点；ang 为齿轮转角；lamp_c 为指示灯颜色。"""
    body = skia.Rect.MakeXYWH(x - w / 2, yb - h, w, h - 20)
    c.drawRoundRect(body, 18, 18, K.paint("#E4EDFA", alpha))
    c.drawRoundRect(body, 18, 18, wb.marker(BLACK, 8, alpha))
    for dx in (-w / 2 + 40, w / 2 - 40):
        c.drawRect(skia.Rect.MakeXYWH(x + dx - 22, yb - 22, 44, 22), K.paint(BLACK, alpha))
    gx, gy, gr = x - 50, yb - h / 2 - 10, 82
    gear = skia.Path()
    for i in range(10):
        a0 = math.radians(ang + i * 36)
        a1 = math.radians(ang + i * 36 + 14)
        a2 = math.radians(ang + i * 36 + 22)
        a3 = math.radians(ang + i * 36 + 36)
        pts = [(gr, a0), (gr + 22, a0 + 0.06), (gr + 22, a1), (gr, a2 - 0.02), (gr, a3)]
        for m, (rr_, aa) in enumerate(pts):
            px, py = gx + rr_ * math.cos(aa), gy + rr_ * math.sin(aa)
            if i == 0 and m == 0:
                gear.moveTo(px, py)
            else:
                gear.lineTo(px, py)
    gear.close()
    c.drawPath(gear, K.paint("#C9CED6", alpha))
    c.drawPath(gear, wb.marker(BLACK, 6, alpha))
    c.drawCircle(gx, gy, 24, K.paint("#FFFFFF", alpha))
    c.drawCircle(gx, gy, 24, wb.marker(BLACK, 5, alpha))
    a = math.radians(ang)
    c.drawLine(gx, gy, gx + 60 * math.cos(a), gy + 60 * math.sin(a), wb.marker(BLACK, 5, alpha))
    lx, ly = x + 95, yb - h + 70
    if lamp_c != GRAY:
        c.drawCircle(lx, ly, 52, K.paint(lamp_c, 0.25 * alpha, blur=14))
    c.drawCircle(lx, ly, 26, K.paint(lamp_c, alpha))
    c.drawCircle(lx, ly, 26, wb.marker(BLACK, 5, alpha))
    for i in range(3):
        yy = yb - h + 140 + i * 30
        c.drawLine(lx - 30, yy, lx + 30, yy, wb.marker(GRAY, 5, alpha))


def smoke(c, x, y, dt, alpha=1.0, n=4, rise=200):
    """冒烟：(x, y) 为烟口；dt 为冒烟以来的秒数。"""
    if dt < 0:
        return
    a0 = clamp01(dt / 0.25) * alpha
    for i in range(n):
        t = (dt * 0.7 + i / n) % 1.0
        px = x + 26 * math.sin(i * 2.1 + t * 4)
        py = y - rise * t
        r = 22 + 34 * t
        c.drawCircle(px, py, r, K.paint("#B9BDC4", a0 * (1 - t) * 0.85))
        c.drawCircle(px, py, r, wb.marker("#6B6B6B", 3, a0 * (1 - t) * 0.6))


def answer_card(c, x, y, s, alpha=1.0, size=56, color=BLUE):
    """“答”卡片：白底蓝框，左边蓝色圆章“答”。"""
    w = K.text_w(s, size, "hand") + 150
    h = size + 44
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(r, h / 2, h / 2, K.paint("#FFFFFF", alpha))
    c.drawRoundRect(r, h / 2, h / 2, wb.marker(color, 7, alpha))
    c.drawCircle(x - w / 2 + 48, y, 32, K.paint(color, alpha))
    K.text(c, "答", x - w / 2 + 48, y, 38, "black", "#FFFFFF", alpha)
    K.text(c, s, x + 34, y, size, "hand", BLACK, alpha)


def pill(c, x, y, s, color=RED, size=46, alpha=1.0, fill="#FFFFFF", tcolor=None):
    w = K.text_w(s, size, "hand") + 50
    h = size + 26
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(r, h / 2, h / 2, K.paint(fill, alpha))
    c.drawRoundRect(r, h / 2, h / 2, wb.marker(color, 6, alpha))
    K.text(c, s, x, y, size, "hand", tcolor or color, alpha)


def why_card(c, x, y, s="为什么？", w=250, h=92, color=RED, alpha=1.0, size=52):
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(r, 16, 16, K.paint("#FFFFFF", alpha))
    c.drawRoundRect(r, 16, 16, wb.marker(color, 7, alpha))
    K.text(c, s, x, y, size, "hand", color, alpha)


def bubble_txt(c, s, x, y, size=60, color=BLACK, tail=-1, alpha=1.0, w=None, h=None):
    w = w or K.text_w(s, size, "hand") + 80
    h = h or size + 60
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 40, 40, K.paint("#FFFFFF", alpha))
    c.drawPath(wb.bubble(x, y, w, h, tail), wb.marker(BLACK, 7, alpha))
    K.text(c, s, x, y, size, "hand", color, alpha)


def book_icon(c, x, y, w=220, h=160, title="丰田模式", alpha=1.0):
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(r, 10, 10, K.paint("#F6E7C8", alpha))
    c.drawRoundRect(r, 10, 10, wb.marker(BLACK, 7, alpha))
    c.drawLine(x - w / 2 + 26, y - h / 2, x - w / 2 + 26, y + h / 2, wb.marker(BLACK, 5, alpha))
    K.text(c, title, x + 12, y, 40, "hand", RED, alpha)


def drop_shape(x, y, r=34):
    p = skia.Path()
    p.moveTo(x, y - r * 1.9)
    p.cubicTo(x + r * 0.4, y - r * 1.1, x + r, y - r * 0.6, x + r, y)
    p.arcTo(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 0, 180, False)
    p.cubicTo(x - r, y - r * 0.6, x - r * 0.4, y - r * 1.1, x, y - r * 1.9)
    p.close()
    return p


def empty_drop(c, x, y, alpha=1.0, r=34):
    """空油滴：虚线轮廓 + 红斜杠。"""
    pth = drop_shape(x, y, r)
    pt = wb.marker(SOIL_LINE, 6, alpha)
    pt.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
    c.drawPath(pth, pt)
    c.drawLine(x - r * 1.2, y + r * 0.9, x + r * 1.2, y - r * 1.6, wb.marker(RED, 8, alpha))


def flow_box(c, x, y, s, w=200, h=96, color=BLACK, fill="#FFFFFF", alpha=1.0, size=48):
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(r, 14, 14, K.paint(fill, alpha))
    c.drawRoundRect(r, 14, 14, wb.marker(color, 7, alpha))
    K.text(c, s, x, y, size, "hand", BLACK, alpha)


def alarm_clock(c, x, y, r=62, ring=0.0, alpha=1.0):
    """闹钟：ring>0 时左右抖动并画震动线。"""
    rot = 12 * math.sin(ring * 40) * (1 if ring > 0 else 0)
    with K.at(c, x, y, rot):
        for sgn in (-1, 1):
            c.drawCircle(sgn * r * 0.62, -r * 0.9, r * 0.32, K.paint(RED, alpha))
            c.drawCircle(sgn * r * 0.62, -r * 0.9, r * 0.32, wb.marker(BLACK, 5, alpha))
            c.drawLine(sgn * r * 0.55, r * 0.8, sgn * r * 0.8, r * 1.1, wb.marker(BLACK, 6, alpha))
        c.drawCircle(0, 0, r, K.paint("#FFFFFF", alpha))
        c.drawCircle(0, 0, r, wb.marker(BLACK, 7, alpha))
        c.drawLine(0, 0, 0, -r * 0.62, wb.marker(BLACK, 6, alpha))
        c.drawLine(0, 0, r * 0.42, r * 0.1, wb.marker(BLACK, 6, alpha))
    if ring > 0:
        for sgn in (-1, 1):
            for i in range(2):
                rr_ = r + 22 + i * 20
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(x - rr_, y - rr_, 2 * rr_, 2 * rr_), (-30 if sgn > 0 else 150), 60)
                c.drawPath(arc, wb.marker(ORANGE, 5, alpha * 0.8))


def hourglass(c, x, y, f, rot=0.0, s=1.0, alpha=1.0):
    """沙漏：(x, y) 为中心；f 0–1 为上半沙子流走的比例。"""
    w, h = 60 * s, 90 * s
    with K.at(c, x, y, rot):
        c.drawLine(-w - 8, -h, w + 8, -h, wb.marker(WOOD, 9, alpha))
        c.drawLine(-w - 8, h, w + 8, h, wb.marker(WOOD, 9, alpha))
        glass = P((-w, -h), (w, -h), (6 * s, 0), (w, h), (-w, h), (-6 * s, 0), close=True)
        c.drawPath(glass, K.paint("#F4F8FC", alpha))
        top = P((-w * (1 - f) * 0.9, -h * (1 - f) * 0.85), (w * (1 - f) * 0.9, -h * (1 - f) * 0.85), (0, -4 * s),
                close=True)
        c.drawPath(top, K.paint(YELLOW, alpha))
        hh = h * (0.15 + 0.6 * f)
        bot = P((-w * 0.9, h - 2), (w * 0.9, h - 2), (0, h - hh), close=True)
        c.drawPath(bot, K.paint(YELLOW, alpha))
        c.drawLine(0, -4 * s, 0, h - hh, wb.marker(YELLOW, 4, alpha))
        c.drawPath(glass, wb.marker(BLACK, 6, alpha))


def footprint(c, x, y, rot, alpha=1.0, s=1.0):
    with K.at(c, x, y, rot):
        c.drawOval(skia.Rect.MakeXYWH(-16 * s, -30 * s, 32 * s, 48 * s), K.paint(BLACK, alpha * 0.8))
        c.drawOval(skia.Rect.MakeXYWH(-13 * s, 22 * s, 26 * s, 20 * s), K.paint(BLACK, alpha * 0.8))


def factory(c, x, y, w=260, h=180, alpha=1.0):
    """车间（锯齿屋顶）：(x, y) 为底边中点。"""
    roof = [(x - w / 2, y - h * 0.6)]
    for i in range(3):
        x0 = x - w / 2 + i * w / 3
        roof += [(x0 + w / 3, y - h), (x0 + w / 3, y - h * 0.6)]
    pth = P((x - w / 2, y), *roof, (x + w / 2, y), close=True)
    c.drawPath(pth, K.paint("#F1ECE2", alpha))
    c.drawPath(pth, wb.marker(BLACK, 7, alpha))
    c.drawRect(skia.Rect.MakeXYWH(x - 30, y - 80, 60, 80), K.paint(BOARD_C, alpha))
    c.drawRect(skia.Rect.MakeXYWH(x - 30, y - 80, 60, 80), wb.marker(BLACK, 5, alpha))


def wrench(c, x, y, rot, s=1.0, alpha=1.0):
    with K.at(c, x, y, rot, s):
        c.drawLine(0, 0, 0, 150, wb.marker(METAL, 22, alpha))
        c.drawLine(0, 0, 0, 150, wb.marker(BLACK, 4, alpha))
        head = skia.Path()
        head.addArc(skia.Rect.MakeXYWH(-40, -50, 80, 80), 120, 300)
        c.drawPath(head, wb.marker(METAL, 22, alpha))


def phone_icon(c, x, y, s=1.0, alpha=1.0, glow=False):
    w, h = 90 * s, 160 * s
    if glow:
        c.drawCircle(x, y, 150 * s, K.paint("#BFD5F2", 0.55 * alpha, blur=30))
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(r, 16 * s, 16 * s, K.paint("#DCE8F7" if glow else "#FFFFFF", alpha))
    c.drawRoundRect(r, 16 * s, 16 * s, wb.marker(BLACK, 6, alpha))
    c.drawCircle(x, y + h / 2 - 14 * s, 5 * s, K.paint(BLACK, alpha))


# ================================================================ 屏 0：系列开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：打地鼠——砸下一个，旁边又冒一个，“又回来了”
cx, cy = R[1]
j = L.scene(1, (cx, cy + 20, Z))
GY1 = cy + 440
HOLES1 = [cx - 300, cx + 20, cx + 340]
b.path(j, 0, 0.6, P((cx - 580, GY1), (cx + 580, GY1)), BLACK, 6, sfx="wood_high", gain=0.6)
k_li1 = 1
k_m1 = kq(j, wt(0, 0, 0.8), lo=2)
k_s1 = kq(j, wt(0, 1, 0.7), lo=k_m1 + 1)
k_cal1 = kq(j, wt(0, 2, 0.1), lo=k_s1 + 1)
k_m2 = kq(j, wt(0, 2, 0.85), lo=k_cal1 + 1)
k_a1 = kq(j, wt(1, 1, 0.2), lo=k_m2 + 1)
# 地鼠：(洞, 冒头拍, 被砸拍)；锤子：(砸的拍, 洞)
MOLES1 = [(0, k_m1, k_s1), (0, k_m2, k_a1), (1, k_a1 + 0.5, k_a1 + 1), (2, k_a1 + 1.5, k_a1 + 2), (0, k_a1 + 2.5, None)]
SMASH1 = [(k_s1, 0), (k_a1, 0), (k_a1 + 1, 1), (k_a1 + 2, 2)]
k_back1 = k_a1 + 3


def holes1(c, kk, T):
    sc = pop_scale(T - tb(1, 0))
    for hx in HOLES1:
        with at_pop(c, hx, GY1, sc):
            hole(c, hx, GY1)
    for h_, ku, kd in MOLES1:
        tu = tb(1, ku)
        if T < tu:
            continue
        hx = HOLES1[h_]
        if kd is not None and T >= tb(1, kd):
            dt = T - tb(1, kd)
            if dt < 0.18:
                mole(c, hx, GY1, 1 - dt / 0.18, squash=0.55)
            continue
        mole(c, hx, GY1, ease_out(clamp01((T - tu) / 0.16)))
    return None


b.custom(j, 0, 0.3, holes1)
for _, ku, _ in MOLES1:
    if is_int(ku):
        b.hit(j, ku, "pop", 0.55, "地鼠冒头")


def li_x1(T):
    """小李站在目标洞左边；砸之前 0.3 秒挪过去。"""
    x = HOLES1[0] - 165
    for ks, h_ in SMASH1:
        t = tb(1, ks)
        tx = HOLES1[h_] - 165
        f = clamp01((T - (t - 0.36)) / 0.24)
        x = lerp(x, tx, ease_in_out(f))
    return x


def hammer_ang(T):
    """锤柄角度：平时举在右上方（-65°），砸的拍前 0.1 秒挥下（55°），停 0.2 秒再抬回。"""
    ang = -65.0
    for ks, _ in SMASH1:
        t = tb(1, ks)
        if t - 0.1 <= T < t:
            return lerp(-65, 55, ease_in_out((T - (t - 0.1)) / 0.1) ** 1.5)
        if t <= T < t + 0.2:
            return 55.0
        if t + 0.2 <= T < t + 0.4:
            return lerp(55, -65, ease_in_out((T - t - 0.2) / 0.2))
    return ang


def li1(c, kk, T):
    sc = pop_scale(T - tb(1, k_li1))
    if sc <= 0:
        return None
    x, s = li_x1(T), 0.85
    hy = GY1 - 290 * s
    ang = hammer_ang(T)
    hand = (x + 70 * s, hy + 110 * s)
    tired = T >= tb(1, k_a1 + 2)
    with at_pop(c, x, GY1, sc):
        draw_li(c, x, GY1, s, "sad" if tired else "flat", rh=hand, lh=(hand[0] - 20, hand[1] + 30))
        hammer(c, hand[0], hand[1], ang, ln=200)
        if tired:
            for i, (dx, dy) in enumerate(((-60, -70), (55, -85))):
                dd = 8 * ((T * 1.6 + i * 0.5) % 1.0)
                c.drawPath(P((x + dx - 10, hy + dy + dd), (x + dx, hy + dy - 24 + dd), (x + dx + 10, hy + dy + dd)),
                           K.paint("#BFD5F2"))
                c.drawCircle(x + dx, hy + dy + 4 + dd, 10, K.paint("#BFD5F2"))
        K.text(c, "小李", x, GY1 + 80, 60, "hand", BLACK)
    for ks, h_ in SMASH1:
        stars(c, HOLES1[h_], GY1 - 60, T - tb(1, ks))
    return None


L.note("小李")
b.custom(j, k_li1, k_li1 + 0.3, li1, sfx="wood_low", gain=0.6)
for ks, _ in SMASH1:
    b.hit(j, ks, "kick" if ks == k_s1 else "tom", 0.8, "锤子砸下")


def cal1(c, sc, T):
    cx, cy = R[1]
    x, y = cx + 360, cy - 330
    f = clamp01((T - tb(1, k_cal1 + 1)) / 0.3)
    with at_pop(c, x, y, sc):
        calendar(c, x, y, "1日", "15日", f)


L.note("1日", "15日")
b.custom(j, k_cal1, k_cal1 + 0.3, pop_fn(j, k_cal1, cal1), sfx="pop", gain=0.55)
b.hit(j, k_cal1 + 1, "shaker", 0.6, "日历翻过两周")
b.custom(j, k_back1, k_back1 + 0.3, L.stamp("又回来了", cx - 130, cy - 330, 110, j, k_back1), sfx="kick", gain=0.9)
b.shots[j].shake = [(k_s1, 8.0), (k_back1, 12.0)]

# ================================================================ 屏 2（drop）：身边的例子——投诉发货慢：道歉、催仓库，下个月照样慢，drop 时“发货慢！”又来
cx, cy = R[2]
j = L.scene(2, (cx, cy + 20, Z))
MH12 = [cx - 300, cx, cx + 300]
MY12 = cy - 430
k_mh = kq(j, wt(2, 0, 0.5), lo=0)
k_mm = kq(j, wt(2, 1, 0.3), lo=k_mh + 1)


def moles12(c, kk, T):
    sc = pop_scale(T - tb(2, k_mh))
    if sc <= 0:
        return None
    for i, hx in enumerate(MH12):
        with at_pop(c, hx, MY12, sc):
            hole(c, hx, MY12, 150, 40)
        t_i = tb(2, k_mm + i)
        if T >= t_i:
            mole(c, hx, MY12, ease_out(clamp01((T - t_i) / 0.16)), r=40)
    return None


b.custom(j, k_mh, k_mh + 0.3, moles12, sfx="wood_high", gain=0.55)
for i in range(3):
    b.hit(j, k_mm + i, ("bongo_high", "bongo_low", "bongo_high")[i], 0.6, "小地鼠冒头")
LI12 = (cx - 140, cy + 440, 0.85)
k_cp = kq(j, wt(3, 0, 0.55), lo=k_mm + 3)
k_bow = kq(j, wt(3, 1, 0.4), lo=k_cp + 1)
k_wh = kq(j, wt(3, 2, 0.35), lo=k_bow + 1)
k_nx = kq(j, wt(3, 3, 0.2), lo=k_wh + 1)
k_cp2 = L.drop_k()                                   # drop：下个月“发货慢！”又来
PH12 = (cx - 450, cy - 170)


def phone12(c, sc, T):
    with at_pop(c, *PH12, sc):
        phone_icon(c, *PH12, 0.9)


b.custom(j, k_cp, k_cp + 0.3, pop_fn(j, k_cp, phone12), sfx="wood_low", gain=0.55)
L.note("发货慢！", "对不起", "快点发", "仓库", "下个月")
b.custom(j, k_cp, k_cp + 0.3, L.pop_bubble("发货慢！", cx - 190, cy - 250, j, k_cp, size=60, color=RED, tail=-1,
                                            until=(2, k_wh)), sfx="rim", gain=0.6)


def li12(c, kk, T):
    x, y, s = LI12
    sc = pop_scale(T - tb(2, 1))
    if sc <= 0:
        return None
    t_b, t_w = tb(2, k_bow), tb(2, k_wh)
    bow = ease_in_out(clamp01((T - t_b) / 0.25)) * (1 - ease_in_out(clamp01((T - t_w + 0.2) / 0.25)))
    hy = y - 290 * s
    rh = (x + 40 * s, hy + 10 * s) if T >= t_w else None
    with at_pop(c, x, y, sc):
        c.save()
        c.translate(x, y - 120 * s)
        c.rotate(28 * bow)
        c.translate(-x, -(y - 120 * s))
        draw_li(c, x, y, s, "sad" if T >= tb(2, k_cp2) else "flat", rh=rh)
        c.restore()
        if T >= t_w:
            phone_icon(c, x + 55 * s, hy + 5 * s, 0.45)
    K.text(c, "小李", x, y + 75, 56, "hand", BLACK, clamp01(sc * 2))
    return None


b.custom(j, 1, 1.3, li12, sfx="pop", gain=0.55)
b.custom(j, k_bow, k_bow + 0.3, L.pop_bubble("对不起", cx + 120, cy + 70, j, k_bow, size=56, tail=-1, until=(2, k_wh)),
         sfx="wood_low", gain=0.6)
b.custom(j, k_wh, k_wh + 0.3, L.pop_bubble("快点发", cx + 120, cy + 70, j, k_wh, size=56, tail=-1), sfx="pop", gain=0.6)


def ware12(c, sc, T):
    cx, cy = R[2]
    x, y = cx + 390, cy + 440
    with at_pop(c, x, y, sc):
        for i, (dx, dy) in enumerate(((-60, 0), (60, 0), (0, -110))):
            c.drawPath(C.box_path(x + dx, y + dy, 120, 100), K.paint("#E6CFA8"))
            c.drawPath(C.box_path(x + dx, y + dy, 120, 100), wb.marker(WOOD, 6))
        K.text(c, "仓库", x, y + 70, 54, "hand", BLACK)


b.custom(j, k_wh, k_wh + 0.3, pop_fn(j, k_wh, ware12))


def cal12(c, sc, T):
    cx, cy = R[2]
    x, y = cx + 380, cy - 180
    with at_pop(c, x, y, sc):
        calendar(c, x, y, "", "下个月", 1.0, w=250)


b.custom(j, k_nx, k_nx + 0.3, pop_fn(j, k_nx, cal12), sfx="shaker", gain=0.6)
b.custom(j, k_cp2, k_cp2 + 0.3, L.pop_bubble("发货慢！", cx - 190, cy - 250, j, k_cp2, size=60, color=RED, tail=-1),
         sfx="kick", gain=0.95)
b.custom(j, k_cp2, k_cp2 + 0.3, L.stamp("照样慢", cx + 425, cy + 115, 76, j, k_cp2, rot=6))
b.shots[j].shake, b.shots[j].flashes = [(k_cp2, 16.0)], [(k_cp2, 0.45)]

# ================================================================ 屏 3：往下挖——订单过三张桌子，每张桌上一个沙漏
cx, cy = R[3]
j = L.scene(3, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_bubble("发货慢！", cx, cy - 500, j, 0, size=54, color=RED, tail=-1), sfx="pop", gain=0.55)
k_w13 = kq(j, wt(4, 0, 0.3), lo=1)
for i in range(2):
    k_ = k_w13 + i
    y_ = cy - 330 + i * 150

    def w13(c, sc, T, y_=y_):
        cx, cy = R[3]
        with at_pop(c, cx, y_, sc):
            c.drawPath(arrow((cx, y_ - 105), (cx, y_ - 50), 0.0, 18), wb.marker(RED, 5))
            why_card(c, cx, y_, w=230, h=80, size=46)
    b.custom(j, k_, k_ + 0.3, pop_fn(j, k_, w13), sfx=("wood_high", "wood_low")[i], gain=0.6)
DESK_X = [cx - 380, cx, cx + 380]
DESK_Y = cy + 330
k_d13 = kq(j, wt(4, 2, 0.15), lo=k_w13 + 2)
k_h13 = kq(j, wt(4, 3, 0.2), lo=k_d13 + 2)
L.note("订单")
for i, x in enumerate(DESK_X):
    k_ = k_d13 + i * 0.5

    def desk13(c, sc, T, x=x, i=i):
        with at_pop(c, x, DESK_Y, sc):
            sx = x - 95
            c.drawPath(wb.stick(sx, DESK_Y + 60, 0.62), wb.marker(BLACK, 8))
            c.drawPath(wb.face(sx, DESK_Y + 60, 0.62, "flat"), wb.marker(BLACK, 5))
            top = skia.Rect.MakeXYWH(x - 160, DESK_Y, 320, 26)
            c.drawRect(top, K.paint(BOARD_C))
            c.drawRect(top, wb.marker(BLACK, 6))
            for dx in (-140, 140):
                c.drawLine(x + dx, DESK_Y + 26, x + dx, DESK_Y + 170, wb.marker(BLACK, 7))
    b.custom(j, k_, k_ + 0.3, pop_fn(j, k_, desk13), sfx="wood_low" if is_int(k_) else None, gain=0.6)


def hg13(c, kk, T):
    for i, x in enumerate(DESK_X):
        t_i = tb(3, k_h13 + i)
        sc = pop_scale(T - t_i)
        if sc <= 0:
            continue
        f = clamp01((T - t_i) / 4.0)
        with at_pop(c, x + 100, DESK_Y - 70, sc):
            hourglass(c, x + 100, DESK_Y - 70, f, s=0.75)
    return None


b.custom(j, k_h13, k_h13 + 0.3, hg13)
for i in range(3):
    b.hit(j, k_h13 + i, "wood_high" if i % 2 == 0 else "pop", 0.6, "沙漏")


def order13(c, kk, T):
    t0 = tb(3, k_d13)
    if T < t0 + 0.2:
        return None
    t1 = tb(3, k_h13 + 2.5)
    f = clamp01((T - t0 - 0.2) / max(0.1, t1 - t0 - 0.2))
    seg = min(2.0, f * 2.0)
    i0 = int(min(1, math.floor(seg)))
    u = ease_in_out(seg - i0)
    x = lerp(DESK_X[i0], DESK_X[i0 + 1], u) - 5
    y = DESK_Y - 50 - 110 * math.sin(math.pi * u)
    with K.at(c, x, y, -6):
        c.drawPath(wb.doc(0, 0, 84, 96, 2), K.paint("#FFFFFF"))
        c.drawPath(wb.doc(0, 0, 84, 96, 2), wb.marker(BLUE, 5))
        K.text(c, "订单", 0, -14, 28, "hand", BLUE)
    return None


b.custom(j, k_d13, k_d13 + 0.3, order13)

# ================================================================ 屏 4：五个闹钟叫不醒——往下挖：凌晨一点的手机光
cx, cy = R[4]
j = L.scene(4, (cx, cy + 20, Z))
BED = (cx - 60, cy - 40)
k_cl = kq(j, wt(5, 1, 0.15), lo=2)
k_hide = kq(j, wt(5, 2, 0.5), lo=k_cl + 3)
k_dig14 = kq(j, wt(6, 0, 0.3), lo=k_hide + 1)
k_nt = kq(j, wt(6, 1, 0.2), lo=k_dig14 + 1)
k_one = kq(j, wt(6, 1, 0.8), lo=k_nt + 1)
CLK = [(cx - 400 + 200 * i, cy - 410 + (i % 2) * 30) for i in range(5)]


def bed14(c, kk, T):
    sc = pop_scale(T - tb(4, 1))
    if sc <= 0:
        return None
    x, y = BED
    hide = ease_in_out(clamp01((T - tb(4, k_hide)) / 0.3))
    with at_pop(c, x, y, sc):
        frame = skia.Rect.MakeLTRB(x - 420, y, x + 380, y + 50)
        c.drawRect(frame, K.paint(BOARD_C))
        c.drawRect(frame, wb.marker(BLACK, 7))
        c.drawRect(skia.Rect.MakeLTRB(x - 440, y - 150, x - 400, y + 130), K.paint(WOOD))
        for xx in (x - 400, x + 360):
            c.drawLine(xx, y + 50, xx, y + 130, wb.marker(BLACK, 8))
        c.drawRoundRect(skia.Rect.MakeLTRB(x - 390, y - 70, x - 230, y), 24, 24, K.paint("#FFFFFF"))
        c.drawRoundRect(skia.Rect.MakeLTRB(x - 390, y - 70, x - 230, y), 24, 24, wb.marker(BLACK, 5))
        hx, hy = x - 300, y - 70
        if hide < 1:
            c.drawCircle(hx, hy, 50, K.paint("#FFFFFF"))
            c.drawCircle(hx, hy, 50, wb.marker(BLACK, 8))
            hair = skia.Path()
            hair.addArc(skia.Rect.MakeXYWH(hx - 50, hy - 50, 100, 100), 190, 160)
            c.drawPath(hair, wb.marker(BLACK, 14))
            for dx in (-18, 18):
                c.drawLine(hx + dx - 9, hy + 2, hx + dx + 9, hy + 2, wb.marker(BLACK, 5))
        bl = lerp(x - 250, x - 380, hide)
        blanket = skia.Path()
        blanket.moveTo(bl, y - 110 + 30 * (1 - hide))
        blanket.quadTo(x + 50, y - 150, x + 370, y - 90)
        blanket.lineTo(x + 370, y)
        blanket.lineTo(bl - 20, y)
        blanket.close()
        c.drawPath(blanket, K.paint("#BFD5F2"))
        c.drawPath(blanket, wb.marker(BLUE, 7))
        if hide > 0:
            for i in range(3):
                ph = ((T - tb(4, k_hide)) * 0.8 + i / 3) % 1.0
                K.text(c, "Z", x - 250 + 60 * ph + i * 10, y - 180 - 70 * ph, 40 + 20 * i, "hand", BLUE,
                       (1 - ph) * hide)
    return None


L.note("Z")
b.custom(j, 1, 1.3, bed14, sfx="wood_low", gain=0.6)
b.hit(j, k_hide, "wood_low", 0.6, "蒙头")


def clocks14(c, kk, T):
    t_h = tb(4, k_hide)
    for i, (x, y) in enumerate(CLK):
        t_i = tb(4, k_cl + i * 0.5)
        sc = pop_scale(T - t_i)
        if sc <= 0:
            continue
        ring = (T - t_i) if T - t_i > 0.2 else 0.0
        with at_pop(c, x, y, sc):
            alarm_clock(c, x, y, 58, ring=ring if T < t_h + 2.0 else 0.0)
    return None


b.custom(j, k_cl, k_cl + 0.3, clocks14)
for i in range(5):
    k_ = k_cl + i * 0.5
    if is_int(k_):
        b.hit(j, k_, "bongo_high" if i % 4 == 0 else "bongo_low", 0.6, "闹钟")
b.path(j, k_dig14, k_dig14 + 0.5, arrow((cx, cy + 130), (cx, cy + 215), 0.0, 26), RED, 8, sfx="tom", gain=0.75)
b.custom(j, k_dig14, k_dig14 + 0.3, L.pop_text("问到底", cx + 210, cy + 170, 60, RED, j, k_dig14))
L.note("1:00")


def night14(c, kk, T):
    cx, cy = R[4]
    t0 = tb(4, k_nt)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx, cy + 410
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - 360, y - 170, 720, 340)
        c.drawRoundRect(r, 30, 30, K.paint("#26314A"))
        c.drawRoundRect(r, 30, 30, wb.marker(BLACK, 7))
        c.drawCircle(x + 270, y - 100, 36, K.paint("#F6E7A6"))
        c.drawCircle(x + 286, y - 112, 32, K.paint("#26314A"))
        hx, hy = x - 120, y + 10
        c.drawCircle(hx, hy, 60, K.paint("#DCE8F7"))
        c.drawCircle(hx, hy, 60, wb.marker(BLACK, 7))
        hair = skia.Path()
        hair.addArc(skia.Rect.MakeXYWH(hx - 60, hy - 60, 120, 120), 190, 160)
        c.drawPath(hair, wb.marker(BLACK, 14))
        for dx in (-20, 20):
            c.drawCircle(hx + dx, hy + 2, 6, K.paint(BLACK))
        phone_icon(c, x + 20, y + 40, 0.9, glow=True)
        if T >= tb(4, k_one):
            a = fade(T, tb(4, k_one), 0.15)
            pill(c, x + 200, y + 40, "1:00", RED, 54, a)
    return None


b.custom(j, k_nt, k_nt + 0.3, night14, sfx="pop", gain=0.6)
b.hit(j, k_one, "ding", 0.6, "凌晨一点")

# ================================================================ 屏 5：五张“为什么？”一级级往下排，“五个为什么”砸下
cx, cy = R[5]
j = L.scene(5, (cx, cy + 20, Z))
k_book2 = kq(j, wt(7, 0, 0.35), lo=1)
k_c2 = max(kq(j, wt(7, 1, 0.1), lo=k_book2 + 1), k_book2 + 1)
KD = kq(j, wt(7, 1, 0.95), lo=k_c2 + 3)              # “五个为什么”砸下（2026-11 起 drop 移到屏 2）
b.shots[j].shake = [(KD, 12.0)]
CARDS2 = [(cx - 270 + 135 * i, cy - 240 + 145 * i) for i in range(5)]


def book2(c, sc, T):
    cx, cy = R[5]
    x, y = cx - 360, cy + 260
    with at_pop(c, x, y, sc, rot=-6):
        book_icon(c, x, y)


L.note("丰田模式")
b.custom(j, k_book2, k_book2 + 0.3, pop_fn(j, k_book2, book2), sfx="wood_low", gain=0.7)
L.note("为什么？")
for i, (x, y) in enumerate(CARDS2):
    k_ = k_c2 + i if k_c2 + 4 < KD else k_c2 + i * 0.5

    def card2(c, sc, T, x=x, y=y, i=i):
        with at_pop(c, x, y, sc):
            why_card(c, x, y)
            K.text(c, str(i + 1), x - 150, y, 50, "black", RED)
            if i < 4:
                c.drawPath(arrow((x + 40, y + 50), (x + 110, y + 100), 0.0, 22), wb.marker(RED, 5))
    b.custom(j, k_, k_ + 0.3, pop_fn(j, k_, card2), sfx="pop" if is_int(k_) else None, gain=0.6)
L.note("1", "2", "3", "4", "5")
b.custom(j, KD, KD + 0.3, L.slam_text("五个为什么", cx, cy - 470, 140, RED, j, KD, font="black"), sfx="kick", gain=0.95)

# ================================================================ 屏 6–12：竖井——一问一答，每问往下挖一层
j = L.scene(6, (X, G - 300, Z))
J3 = j
# 每层挖开的时刻 (屏, 拍)；修到根时各层变绿的时刻 (屏, 拍)
DIG = {}
GREEN_AT = {}
STOP_AT = [None]
RESTART_AT = [None]


def dig_t(n):
    return tb(*DIG[n]) if n in DIG else 1e9


def shaft_top(n):
    return G - 70 if n == 1 else CY(n - 1) + 310


def column(c, kk, T):
    """土层 + 已挖开的各层（矩形洞室 + 左边的竖井和梯子）；修到根后由下往上变绿。"""
    stage_clip(c)
    c.drawRect(skia.Rect.MakeLTRB(X - 620, G, X + 620, G + 5 * D + 80), K.paint(SOIL))
    for i in range(70):
        px = X - 590 + (i * 173) % 1180
        py = G + 40 + (i * 397) % (5 * D)
        c.drawCircle(px, py, 6 + (i % 3) * 3, K.paint(SOIL_LINE, 0.35))
    for n in range(1, 6):
        t0 = dig_t(n)
        if T < t0:
            continue
        f = ease_out(clamp01((T - t0) / 0.45))
        g = n in GREEN_AT and T >= tb(*GREEN_AT[n])
        top, bot = CY(n) - 310, CY(n) + 310
        cur = top + (bot - top) * f
        st = shaft_top(n)
        s_cur = st + (top - st) * clamp01(f * 3)
        c.drawRect(skia.Rect.MakeLTRB(X - 530, st, X - 410, s_cur), K.paint(CAVE))
        r = skia.Rect.MakeLTRB(X - 545, top, X + 545, cur)
        c.drawRoundRect(r, 24, 24, K.paint(GREEN_FILL if g else CAVE))
        c.drawRoundRect(r, 24, 24, wb.marker(GREEN if g else SOIL_LINE, 7))
        for xx in (X - 530, X - 410):
            c.drawLine(xx, st, xx, min(s_cur, top), wb.marker(SOIL_LINE, 6))
        # 梯子
        lb = st - (40 if n == 1 else 0)
        le = lb + (CY(n) + 300 - lb) * f
        for xx in (X - 505, X - 435):
            c.drawLine(xx, lb, xx, le, wb.marker(WOOD, 7))
        yy = lb + 30
        while yy < le:
            c.drawLine(X - 505, yy, X - 435, yy, wb.marker(WOOD, 6))
            yy += 56
    return None


b.custom(j, 0, 0.1, column)
b.path(j, 0, 0.7, P((X - 620, G), (X + 620, G)), BLACK, 9, sfx="wood_high", gain=0.6)

MX = X + 180          # 机器中心 x


def machine_fn(c, kk, T):
    sc = pop_scale(T - tb(6, 1))
    if sc <= 0:
        return None
    ts = tb(*STOP_AT[0]) if STOP_AT[0] else 1e9
    tr = tb(*RESTART_AT[0]) if RESTART_AT[0] else 1e9
    running = T < ts or T >= tr
    ang = 140 * T if running else 140 * ts
    shake = wobble(T - ts, 5, 40, 6) if T < tr else 0.0
    with at_pop(c, MX, G, sc):
        machine(c, MX + shake, G, ang, GREEN if running else RED)
        if not running:
            smoke(c, MX + 120, G - 300, T - ts)
        if running and T >= tr:
            K.ripple(c, MX + 95, G - 230, T - tr, GREEN, 140, 7, 0.9, 0.6)
    return None


b.custom(j, 1, 1.3, machine_fn, sfx="wood_low", gain=0.6)

OH_S = 0.65
k_oh3 = kq(j, wt(8, 0, 0.15), lo=2)
k_wk3 = k_oh3 + 1
k_q3 = kq(j, wt(8, 1, 0.25), lo=k_wk3 + 1)
k_a3 = k_q3 + 1
ASK = []              # Ohno 问话（抬手指）的时段 [(屏, 拍起, 屏, 拍止)]


def ohno_pos(T):
    """大野耐一的位置：地面 → 每挖开一层，1.6 拍内走到梯子、爬下去、走到这一层的站位。返回 (x, y, 是否在爬)。"""
    x0, y0 = X - 380, G
    for n in range(1, 6):
        if n not in DIG:
            break
        jn, kn = DIG[n]
        t0 = tb(jn, kn)
        if T < t0:
            break
        t1 = tb(jn, kn + 1.6)
        f = clamp01((T - t0) / (t1 - t0))
        yn = CY(n) + 290
        if f >= 1:
            x0, y0 = X - 380, yn
            continue
        if f < 0.2:
            return lerp(X - 380, X - 470, ease_in_out(f / 0.2)), y0, False
        if f < 0.8:
            return X - 470, lerp(y0, yn, ease_in_out((f - 0.2) / 0.6)), True
        return lerp(X - 470, X - 380, ease_in_out((f - 0.8) / 0.2)), yn, False
    return x0, y0, False


def ohno_fn(c, kk, T):
    sc = pop_scale(T - tb(6, k_oh3))
    if sc <= 0:
        return None
    x, y, climbing = ohno_pos(T)
    s = OH_S
    hy = y - 290 * s
    lh = rh = None
    if climbing:
        ph = math.sin(T * 14)
        lh = (x - 40 * s, hy - 30 * s + 25 * s * ph)
        rh = (x + 40 * s, hy - 30 * s - 25 * s * ph)
    else:
        for ja, ka, jb, kb_ in ASK:
            if tb(ja, ka) <= T < tb(jb, kb_):
                rh = (x + 115 * s, hy + 10 * s)
                break
    mood = "smile" if RESTART_AT[0] and T >= tb(*RESTART_AT[0]) - 1.0 else "flat"
    with at_pop(c, x, y, sc):
        draw_ohno(c, x, y, s, lh=lh, rh=rh, mood=mood)
    if 1 not in DIG or T < dig_t(1):
        K.text(c, "大野耐一", X - 380, G + 62, 50, "hand", BLACK, clamp01(sc * 2))
    return None


L.note("大野耐一")
b.custom(j, k_oh3, k_oh3 + 0.3, ohno_fn, sfx="pop", gain=0.6)
WK = (X + 480, G, OH_S)
b.custom(j, k_wk3, k_wk3 + 0.3, L.figure(draw_worker, j, k_wk3, *WK,
                                         mood=lambda T: "o" if STOP_AT[0] and tb(*STOP_AT[0]) <= T < tb(8, 0) else "flat"),
         sfx="pop", gain=0.55)
L.note("员工")
b.custom(j, k_wk3, k_wk3 + 0.3, pop_fn(j, k_wk3, lambda c, sc, T: K.text(c, "员工", WK[0], G + 62, 50, "hand", BLUE,
                                                                         clamp01(sc * 2) * (T < dig_t(1)))))
ASK.append((6, k_q3, 7, 0))
b.custom(j, k_q3, k_q3 + 0.3, L.pop_bubble("为什么？", X - 240, G - 380, j, k_q3, size=56, color=RED, tail=-1,
                                            until=(7, 0)), sfx="pop", gain=0.65)
b.custom(j, k_a3, k_a3 + 0.3, L.pop_bubble("因为……", X + 380, G - 430, j, k_a3, size=56, color=BLUE, tail=1,
                                            until=(7, 0)), sfx="wood_high", gain=0.6)

# ---------------------------------------------------------------- 每一层的画面（(ox, oy) 为画面中心）


def fuse_obj(c, ox, oy, T, t0):
    """烧断的保险丝：玻璃管 + 两端金属帽，中间熔丝断开、发黑，冒一缕烟。"""
    w, h = 300, 84
    r = skia.Rect.MakeXYWH(ox - w / 2, oy - h / 2, w, h)
    c.drawRoundRect(r, h / 2, h / 2, K.paint("#EAF3FB"))
    c.drawRoundRect(r, h / 2, h / 2, wb.marker(BLACK, 6))
    for sgn in (-1, 1):
        cap = skia.Rect.MakeXYWH(ox + sgn * (w / 2 - 30) - 32, oy - h / 2 - 6, 64, h + 12)
        c.drawRoundRect(cap, 10, 10, K.paint("#C9CED6"))
        c.drawRoundRect(cap, 10, 10, wb.marker(BLACK, 6))
    c.drawPath(P((ox - 88, oy), (ox - 60, oy - 10), (ox - 34, oy + 10), (ox - 18, oy)), wb.marker(BLACK, 5))
    c.drawPath(P((ox + 88, oy), (ox + 60, oy + 10), (ox + 34, oy - 10), (ox + 18, oy)), wb.marker(BLACK, 5))
    c.drawCircle(ox, oy, 24, K.paint("#3B3330", 0.55, blur=6))
    smoke(c, ox, oy - 50, T - t0, alpha=0.8, n=3, rise=110)
    if T - t0 < 0.5:
        K.ripple(c, ox, oy, T - t0, ORANGE, 120, 6, 0.9, 0.5)


def bearing_obj(c, ox, oy, T, t0):
    """轴承（干转、冒火星）+ 旁边一个空油滴。"""
    bx, by = ox - 40, oy
    c.drawCircle(bx, by, 118, K.paint("#E1E4EA"))
    c.drawCircle(bx, by, 118, wb.marker(BLACK, 7))
    c.drawCircle(bx, by, 62, K.paint("#FFFFFF"))
    c.drawCircle(bx, by, 62, wb.marker(BLACK, 7))
    ang = 30 * (T - t0)
    for i in range(8):
        a = math.radians(ang + i * 45)
        px, py = bx + 90 * math.cos(a), by + 90 * math.sin(a)
        c.drawCircle(px, py, 20, K.paint("#C9CED6"))
        c.drawCircle(px, py, 20, wb.marker(BLACK, 4))
    c.drawCircle(bx, by, 26, K.paint(METAL))
    if T >= t0:
        ph = ((T - t0) * 2.0) % 1.0
        if ph < 0.35:
            for i in range(3):
                a = math.radians(-50 + i * 25)
                c.drawLine(bx + 125 * math.cos(a), by + 125 * math.sin(a), bx + (150 + 60 * ph) * math.cos(a),
                           by + (150 + 60 * ph) * math.sin(a), wb.marker(ORANGE, 6, 1 - ph / 0.35))
    empty_drop(c, ox + 160, oy + 10, alpha=clamp01((T - t0 - 0.3) / 0.25))


def pump_obj(c, ox, oy, T, t0):
    """油泵：手柄一下下压，出油口只滴出空油滴；右边油罐，管子里空的。"""
    px, py = ox - 70, oy + 20
    body = skia.Rect.MakeXYWH(px - 75, py - 70, 150, 150)
    pipe_y = py + 50
    for yy in (pipe_y - 14, pipe_y + 14):
        c.drawLine(px + 75, yy, ox + 140, yy, wb.marker(BLACK, 6))
    for i in range(3):
        xx = px + 100 + i * 55 + ((T - t0) * 30) % 20
        c.drawCircle(xx, pipe_y, 6, wb.marker(GRAY, 3))
    tank = skia.Rect.MakeXYWH(ox + 120, oy - 40, 120, 150)
    c.drawRoundRect(tank, 16, 16, K.paint("#FFFFFF"))
    c.drawRect(skia.Rect.MakeLTRB(ox + 124, oy + 86, ox + 236, oy + 106), K.paint(YELLOW, 0.8))
    c.drawRoundRect(tank, 16, 16, wb.marker(BLACK, 7))
    c.drawRoundRect(body, 14, 14, K.paint("#E4EDFA"))
    c.drawRoundRect(body, 14, 14, wb.marker(BLACK, 7))
    bp = L.beat_pos(T) - L.beat_pos(t0)
    pump = math.exp(-((bp % 1.0) * 6)) if bp >= 0 else 0.0
    a = math.radians(-35 + 28 * pump)
    pv = (px + 40, py - 70)
    c.drawLine(pv[0], pv[1], pv[0] - 130 * math.cos(a), pv[1] + 130 * math.sin(a), wb.marker(BLACK, 10))
    c.drawCircle(pv[0] - 130 * math.cos(a), pv[1] + 130 * math.sin(a), 14, K.paint(RED))
    c.drawLine(px - 75, py - 20, px - 130, py - 20, wb.marker(BLACK, 12))
    c.drawLine(px - 130, py - 20, px - 130, py + 10, wb.marker(BLACK, 12))
    empty_drop(c, px - 130, py + 75, alpha=clamp01((T - t0 - 0.3) / 0.25), r=26)


def shaft_obj(c, ox, oy, T, t0, t_wob=None):
    """泵轴：两只支座，轴歪着，“晃来晃去”时来回晃，磨坏处红色锯齿。"""
    for sgn in (-1, 1):
        blk = skia.Rect.MakeXYWH(ox + sgn * 130 - 30, oy - 20, 60, 110)
        c.drawRect(blk, K.paint("#E1E4EA"))
        c.drawRect(blk, wb.marker(BLACK, 6))
    c.drawLine(ox - 220, oy + 90, ox + 220, oy + 90, wb.marker(BLACK, 7))
    wob = 0.0
    if t_wob is not None and T >= t_wob:
        wob = 7 * math.sin((T - t_wob) * 9) * (0.6 + 0.4 * math.cos((T - t_wob) * 2))
    with K.at(c, ox, oy, 6 + wob):
        c.drawLine(-210, 0, 210, 0, wb.marker(METAL, 26))
        c.drawLine(-210, 0, 210, 0, wb.marker(BLACK, 3))
        c.drawPath(P((60, -16), (72, 12), (84, -14), (96, 12), (108, -14)), wb.marker(RED, 6))
    if t_wob is not None and T >= t_wob:
        a = clamp01((T - t_wob) / 0.2)
        for sgn in (-1, 1):
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(ox + sgn * 230 - 40, oy - 60, 80, 120), -60 if sgn > 0 else 120, 120)
            c.drawPath(arc, wb.marker(ORANGE, 6, a))


OIL5 = None   # 第 5 层的进油口位置（下面填）


def inlet_obj(c, ox, oy, T, t0, t_chips=None, t_filter=None):
    """油箱进油口：没装网，铁屑一粒粒掉进去；装网后铁屑落在网上。"""
    tank = skia.Rect.MakeXYWH(ox - 140, oy + 10, 280, 130)
    c.drawRoundRect(tank, 16, 16, K.paint("#FFFFFF"))
    c.drawRect(skia.Rect.MakeLTRB(ox - 136, oy + 80, ox + 136, oy + 136), K.paint(YELLOW, 0.75))
    c.drawRoundRect(tank, 16, 16, wb.marker(BLACK, 7))
    for sgn in (-1, 1):
        c.drawLine(ox + sgn * 38, oy - 50, ox + sgn * 38, oy + 10, wb.marker(BLACK, 7))
        c.drawLine(ox + sgn * 38, oy - 50, ox + sgn * 62, oy - 70, wb.marker(BLACK, 7))
    if t_chips is not None and T >= t_chips:
        caught = t_filter is not None and T >= t_filter
        for i in range(6):
            t_i = t_chips + i * 0.22
            if T < t_i:
                continue
            dx = ((i * 37) % 7 - 3) * 9
            ph = ((T - t_i) / 0.6) % 1.0 if not caught else min(1.0, (T - t_i) / 0.6)
            if caught and t_i < t_filter:
                ph = 1.0
            y = lerp(oy - 200, oy - 52 if caught else oy + 70, ph)
            if caught:
                y = min(y, oy - 76)
            with K.at(c, ox + dx, y, i * 47 + (T - t_i) * 200 * (0 if caught else 1)):
                c.drawPath(P((-9, -6), (8, -9), (10, 5), (-4, 9), close=True), K.paint("#4A4F58"))


def filter_mesh(c, ox, oy, T, t_f):
    """过滤网：从左边滑进来，盖在进油口上。"""
    f = ease_out(clamp01((T - t_f) / 0.35))
    if f <= 0:
        return
    x = lerp(ox - 360, ox, f)
    y = oy - 72
    r = skia.Rect.MakeXYWH(x - 90, y - 12, 180, 24)
    c.drawRect(r, K.paint("#FFFFFF"))
    for i in range(9):
        xx = x - 80 + i * 20
        c.drawLine(xx, y - 12, xx + 10, y + 12, wb.marker(GREEN, 3))
        c.drawLine(xx + 10, y - 12, xx, y + 12, wb.marker(GREEN, 3))
    c.drawRect(r, wb.marker(GREEN, 6))


ANSWERS = {1: "保险丝烧断", 2: "轴承缺油", 3: "油泵抽不上油", 4: "泵轴磨坏", 5: "没装过滤网"}
L.note(*ANSWERS.values(), "答", *[f"第{n}问" for n in range(1, 6)], "铁屑")


def obj_center(n):
    return X + 170, CY(n) - 60


def layer(n, j, k_dig, k_obj, k_card, obj, extra=None):
    """第 n 层：挖开（tom）+ 红箭头从上一层的答案往下钻 + “第n问”；k_obj 画出答案画面；k_card 落下“答”卡片。"""
    DIG[n] = (j, k_dig)
    ox, oy = obj_center(n)
    y0 = G + 10 if n == 1 else CY(n - 1) + 265
    b.path(j, k_dig + 0.15, k_dig + 0.75, arrow((ox, y0), (ox, CY(n) - 215), 0.0, 36), RED, 8)
    b.hit(j, k_dig, "tom", 0.85, f"挖开第 {n} 层")

    def tag(c, sc, T):
        x, y = X + 450, CY(n) - 255
        with at_pop(c, x, y, sc):
            pill(c, x, y, f"第{n}问", RED, 44)
    b.custom(j, k_dig + 0.5, k_dig + 0.8, pop_fn(j, k_dig + 0.5, tag))

    def o_fn(c, kk, T):
        t0 = tb(j, k_obj)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        with at_pop(c, ox, oy, sc):
            obj(c, ox, oy, T, t0)
        return None
    b.custom(j, k_obj, k_obj + 0.3, o_fn, sfx="wood_high", gain=0.65)

    def card(c, kk, T):
        t0 = tb(j, k_card)
        sc = C.slam_scale(T - t0)
        if sc <= 0:
            return None
        x, y = X + 170, CY(n) + 210
        with K.at(c, x, y, 0, sc):
            c.translate(-x, -y)
            answer_card(c, x, y, ANSWERS[n], clamp01((T - t0) / 0.06))
        return None
    b.custom(j, k_card, k_card + 0.3, card, sfx="rim", gain=0.75)


def ask(n, j, k, until):
    """大野耐一在第 n 层（n=0 为地面）问“为什么？”。"""
    if n == 0:
        x, y = X - 250, G - 362
    else:
        x, y = X - 290, CY(n) - 40
    ASK.append((j, k, *until))
    b.custom(j, k, k + 0.3, L.pop_bubble("为什么？", x, y, j, k, size=56, color=RED, tail=-1, until=until),
             sfx="pop", gain=0.65)


def view_n(n):
    return X, CY(n) - 100, Z


# ---------------------------------------------------------------- 屏 7：第一问——机器停了；为什么？保险丝烧断
j = L.scene(7, (X, G + 200, Z))
k_stop4 = kq(j, wt(9, 0, 0.6), lo=1)
STOP_AT[0] = (7, k_stop4)
b.hit(j, k_stop4, "kick", 0.85, "机器停转")
b.shots[j].shake = [(k_stop4, 10.0)]
k_q4 = kq(j, wt(9, 1, 0.1), lo=k_stop4 + 1)
k_dig4 = k_q4 + 1
ask(0, j, k_q4, (7, k_dig4))
k_obj4 = kq(j, wt(9, 1, 0.8), lo=k_dig4 + 1)
k_card4 = kq(j, wt(9, 2, 0.6), lo=k_obj4 + 1)
layer(1, j, k_dig4, k_obj4, k_card4, fuse_obj)

# ---------------------------------------------------------------- 屏 8–11：第二到第五问


def why_screen(n, li, f_obj, f_card, obj, ci_card=0):
    j = L.scene(6 + n, view_n(n))
    k_ask = kq(j, wt(li, 0, 0.25), lo=2)
    k_obj = kq(j, wt(li, 0, f_obj), lo=k_ask + 1)
    k_card = kq(j, wt(li, ci_card, f_card), lo=k_obj + 1)
    ask(n, j, k_ask, (j + 1, 0))
    layer(n, j, 0, k_obj, k_card, obj)
    return j, k_obj, k_card


why_screen(2, 10, 0.66, 0.93, bearing_obj)
why_screen(3, 11, 0.55, 0.92, pump_obj)

T_WOB = [None]
j4, _, _ = why_screen(4, 12, 0.6, 0.97, lambda c, ox, oy, T, t0: shaft_obj(c, ox, oy, T, t0, T_WOB[0]))
k_wob = kq(j4, wt(12, 1, 0.2), lo=4)
T_WOB[0] = tb(j4, k_wob)
b.hit(j4, k_wob, "shaker", 0.7, "泵轴晃来晃去")

CH = [None, None]          # 铁屑开始掉、装上网的时刻
j5, k_obj5, k_card5 = why_screen(5, 13, 0.6, 0.97,
                                 lambda c, ox, oy, T, t0: inlet_obj(c, ox, oy, T, t0, CH[0], CH[1]))
k_chip = kq(j5, wt(13, 1, 0.15), lo=k_card5 + 1)
k_circ = kq(j5, wt(13, 1, 0.85), lo=k_chip + 1)
CH[0] = tb(j5, k_chip)
b.hit(j5, k_chip, "shaker", 0.7, "铁屑掉进去")
OX5, OY5 = obj_center(5)


def chips_lbl(c, kk, T):
    a = fade(T, tb(j5, k_chip))
    if a > 0:
        K.text(c, "铁屑", OX5 - 150, OY5 - 150, 50, "hand", BLACK, a)
        c.drawPath(arrow((OX5 - 100, OY5 - 150), (OX5 - 30, OY5 - 150), 0.0, 16), wb.marker(BLACK, 4, a))
    return None


b.custom(j5, k_chip, k_chip + 0.1, chips_lbl)


def circ5(c, kk, T):
    t0 = tb(j5, k_circ)
    if T < t0:
        return None
    f = clamp01((T - t0) / 0.3)
    pth = skia.Path()
    pth.addArc(skia.Rect.MakeXYWH(OX5 - 105, OY5 - 175, 210, 150), -90, 360 * f)
    c.drawPath(pth, wb.marker(RED, 9))
    return None


b.custom(j5, k_circ, k_circ + 0.3, circ5, sfx="rim", gain=0.8)

# ---------------------------------------------------------------- 屏 12：修到根——装上过滤网、打勾，拉远看整口井，五层从下往上变绿，机器重新转
j = L.scene(12, view_n(5))
k_f9 = kq(j, wt(14, 0, 0.45), lo=1)
k_ck9 = k_f9 + 1
CH[1] = tb(j, k_f9)
b.custom(j, k_f9, k_f9 + 0.3, lambda c, kk, T: filter_mesh(c, OX5, OY5, T, tb(12, k_f9)), sfx="wood_high", gain=0.7)
b.path(j, k_ck9, k_ck9 + 0.4, check(X + 430, CY(5) - 70, 70), GREEN, 14, sfx="ding", gain=0.7)
k_mv9 = k_ck9 + 0.5
ZOOM = (X, G + 1640, 0.22)
b.move(j, k_mv9, ZOOM, dur=1.0)
k_g9 = k_ck9 + 2
for n in range(5, 0, -1):
    k_ = k_g9 + (5 - n) * 0.5
    GREEN_AT[n] = (12, k_)
    if is_int(k_):
        b.hit(j, k_, "wood_high", 0.6, f"第 {n} 层变绿")
RESTART_AT[0] = (12, k_g9 + 3)
b.hit(j, k_g9 + 3, "clap", 0.7, "机器重新转起来")
L.note("真的修好")


def done9(c, kk, T):
    """拉远后井的左边竖排大字“真的修好”，随机器重新转起来逐字弹出。"""
    t0 = tb(12, k_g9 + 3)
    for i, ch in enumerate("真的修好"):
        sc = pop_scale(T - t0 - 0.1 * i)
        if sc > 0:
            with K.at(c, X - 1250, G + 1000 + 380 * i, 0, sc):
                K.text(c, ch, 0, 0, 330, "hand", GREEN)
    return None


b.custom(j, k_g9 + 3, k_g9 + 3.4, done9)

# ================================================================ 屏 13：只问一次——员工换根保险丝；日历翻过几天，机器又冒烟
cx, cy = R[13]
j = L.scene(13, (cx, cy + 20, Z))
M10 = (cx + 200, cy + 440)
WK10 = (cx - 330, cy + 440, 0.9)
k_once = kq(j, wt(15, 0, 0.5), lo=1)
k_fuse = kq(j, wt(15, 1, 0.45), lo=k_once + 1)
k_ok10 = k_fuse + 1
k_cal10 = kq(j, wt(16, 0, 0.2), lo=k_ok10 + 1)
k_stop10 = max(kq(j, wt(16, 1, 0.6), lo=k_cal10 + 1), k_cal10 + 2)


def machine10(c, kk, T):
    sc = pop_scale(T - tb(13, 0))
    if sc <= 0:
        return None
    t_on, t_off = tb(13, k_fuse), tb(13, k_stop10)
    running = t_on <= T < t_off
    ang = 140 * (min(T, t_off) - t_on) if T >= t_on else 0
    with at_pop(c, M10[0], M10[1], sc):
        machine(c, M10[0] + (wobble(T - t_off, 6, 40, 6) if T >= t_off else 0), M10[1], ang,
                GREEN if running else RED)
        if T < t_on:
            smoke(c, M10[0] + 120, M10[1] - 300, T - tb(13, 0), alpha=0.6)
        if T >= t_off:
            smoke(c, M10[0] + 120, M10[1] - 300, T - t_off)
    return None


b.custom(j, 0, 0.3, machine10, sfx="wood_low", gain=0.6)


def worker10(c, kk, T):
    x, y, s = WK10
    sc = pop_scale(T - tb(13, 1))
    if sc <= 0:
        return None
    hy = y - 290 * s
    t_f = tb(13, k_fuse)
    f = ease_in_out(clamp01((T - (t_f - 0.45)) / 0.45))
    back = ease_in_out(clamp01((T - (t_f + 0.3)) / 0.4))
    hx = lerp(x + 120 * s, M10[0] - 150, f * (1 - back)) if T < t_f + 0.7 else x + 70 * s
    hyy = lerp(hy + 120 * s, M10[1] - 160, f * (1 - back)) if T < t_f + 0.7 else hy + 170 * s
    with at_pop(c, x, y, sc):
        draw_worker(c, x, y, s, rh=(hx, hyy), mood="o" if T >= tb(13, k_stop10) else "smile")
        if T < t_f:
            fuse_mini(c, hx + 20, hyy)
    K.text(c, "员工", x, y + 70, 54, "hand", BLUE, clamp01(sc * 2))
    return None


def fuse_mini(c, x, y):
    r = skia.Rect.MakeXYWH(x - 50, y - 16, 100, 32)
    c.drawRoundRect(r, 16, 16, K.paint("#EAF3FB"))
    c.drawRoundRect(r, 16, 16, wb.marker(BLACK, 5))
    for sgn in (-1, 1):
        c.drawRect(skia.Rect.MakeXYWH(x + sgn * 38 - 12, y - 18, 24, 36), K.paint("#C9CED6"))
    c.drawLine(x - 26, y, x + 26, y, wb.marker(BLACK, 3))


b.custom(j, 1, 1.3, worker10, sfx="pop", gain=0.55)
b.hit(j, k_fuse, "wood_high", 0.7, "换上保险丝")
L.note("只问一次")
b.custom(j, k_once, k_once + 0.3, L.pop_text("只问一次", cx - 230, cy - 480, 96, RED, j, k_once), sfx="pop", gain=0.6)
b.custom(j, k_once, k_once + 0.3, pop_fn(j, k_once, lambda c, sc, T: why_card(c, R[13][0] + 210, R[13][1] - 480,
                                                                                alpha=clamp01(sc * 2))))
b.path(j, k_ok10, k_ok10 + 0.4, check(cx - 150, cy - 210, 60), GREEN, 12, sfx="ding", gain=0.6)


def cal10(c, sc, T):
    cx, cy = R[13]
    x, y = cx + 380, cy - 220
    f = clamp01((T - tb(13, k_cal10 + 1)) / 0.3)
    with at_pop(c, x, y, sc):
        calendar(c, x, y, "1日", "5日", f)


L.note("5日")
b.custom(j, k_cal10, k_cal10 + 0.3, pop_fn(j, k_cal10, cal10), sfx="pop", gain=0.55)
b.hit(j, k_cal10 + 1, "shaker", 0.6, "过了几天")
b.custom(j, k_stop10, k_stop10 + 0.3, L.stamp("又停了", cx - 150, cy - 210, 100, j, k_stop10), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_stop10, 12.0)]

# ================================================================ 屏 14：书中观点——杂草：剪掉叶子，根还在，换个样子长回来
cx, cy = R[14]
j = L.scene(14, (cx, cy + 20, Z))
GY11 = cy + 60
WX = cx + 40
b.path(j, 0, 0.6, P((cx - 580, GY11), (cx + 580, GY11)), WOOD, 9, sfx="wood_high", gain=0.6)


def soil11(c, kk, T):
    cx, cy = R[14]
    a = fade(T, tb(14, 0), 0.4)
    c.drawRect(skia.Rect.MakeLTRB(cx - 580, GY11 + 6, cx + 580, cy + 560), K.paint(SOIL, a))
    return None


b.custom(j, 0, 0.1, soil11)
k_book11 = kq(j, wt(17, 0, 0.5), lo=1)
k_root = kq(j, wt(17, 2, 0.6), lo=k_book11 + 1)
k_surf = kq(j, wt(17, 3, 0.7), lo=k_root + 1)
k_cut = kq(j, wt(18, 0, 0.6), lo=k_surf + 1)
k_grow = kq(j, wt(18, 1, 0.75), lo=k_cut + 1)


def leaves(c, x, y, sc, kind=0, alpha=1.0, rot=0.0, dy=0.0):
    with K.at(c, x, y + dy, rot, sc):
        c.drawLine(0, 0, 0, -220, wb.marker(GREEN, 9, alpha))
        specs = [(-1, -70, 110), (1, -120, 100), (-1, -170, 80), (1, -210, 60)]
        for sgn, ly, ln in specs:
            p = skia.Path()
            if kind == 0:
                p.moveTo(0, ly)
                p.quadTo(sgn * ln * 0.6, ly - ln * 0.6, sgn * ln, ly - ln * 0.3)
                p.quadTo(sgn * ln * 0.5, ly + 10, 0, ly)
            else:
                p.moveTo(0, ly)
                for i in range(4):
                    p.lineTo(sgn * ln * (i + 0.5) / 4, ly - 40 - (i % 2) * 20)
                    p.lineTo(sgn * ln * (i + 1) / 4, ly - 10)
                p.lineTo(0, ly + 6)
            p.close()
            c.drawPath(p, K.paint("#9ED39B" if kind == 0 else "#7CC0A0", alpha))
            c.drawPath(p, wb.marker(GREEN, 5, alpha))
        if kind == 1:
            c.drawCircle(0, -240, 26, K.paint(YELLOW, alpha))
            c.drawCircle(0, -240, 26, wb.marker(ORANGE, 5, alpha))


def weed11(c, kk, T):
    t_cut = tb(14, k_cut)
    sc = pop_scale(T - tb(14, 1))
    if sc <= 0:
        return None
    if T < t_cut:
        leaves(c, WX, GY11, sc)
    else:
        dt = T - t_cut
        if dt < 0.9:
            leaves(c, WX + 60 * dt, GY11 - 40, 1.0, alpha=1 - dt / 0.9, rot=40 * dt, dy=500 * dt * dt)
        c.drawLine(WX, GY11, WX, GY11 - 30, wb.marker(GREEN, 9))
        sg = pop_scale(T - tb(14, k_grow))
        if sg > 0:
            leaves(c, WX, GY11, sg, kind=1)
    return None


b.custom(j, 1, 1.3, weed11, sfx="pop", gain=0.6)


def roots11(c, kk, T):
    t0 = tb(14, k_root)
    f = clamp01((T - t0) / 0.6)
    if f <= 0:
        return None
    pts = [[(0, 0), (-30, 120), (-120, 220), (-200, 330)], [(0, 0), (20, 140), (90, 260), (180, 380)],
           [(0, 0), (0, 160), (-20, 300), (10, 440)], [(-30, 120), (40, 200), (60, 280)]]
    for ps in pts:
        p = P(*[(WX + x_, GY11 + y_) for x_, y_ in ps])
        part, _ = wb.partial(p, f)
        c.drawPath(part, wb.marker(WOOD, 9))
    return None


b.custom(j, k_root, k_root + 0.6, roots11, sfx="tom", gain=0.75)
L.note("根", "表面")
b.custom(j, k_root, k_root + 0.3, L.pop_text("根", WX + 300, GY11 + 260, 110, RED, j, k_root))
b.custom(j, k_surf, k_surf + 0.3, L.pop_text("表面", WX - 330, GY11 - 150, 84, BLUE, j, k_surf), sfx="pop", gain=0.6)


def book11(c, sc, T):
    cx, cy = R[14]
    x, y = cx - 360, cy - 470
    with at_pop(c, x, y, sc, rot=-5):
        book_icon(c, x, y, 200, 140)


b.custom(j, k_book11, k_book11 + 0.3, pop_fn(j, k_book11, book11), sfx="wood_low", gain=0.6)


def scissors11(c, kk, T):
    t0 = tb(14, k_cut)
    if T < t0 - 0.5 or T > t0 + 0.8:
        return None
    a = clamp01((T - (t0 - 0.5)) / 0.2) * (1 - clamp01((T - t0 - 0.5) / 0.3))
    open_ = 0.0 if T >= t0 else 22 * (1 - (T - (t0 - 0.5)) / 0.5)
    x, y = WX + 130, GY11 - 30
    for sgn in (-1, 1):
        with K.at(c, x, y, sgn * open_):
            c.drawLine(0, 0, -150, 0, wb.marker(METAL, 12, a))
            c.drawCircle(60, sgn * 18, 26, wb.marker(RED, 9, a))
    c.drawCircle(x, y, 7, K.paint(BLACK, a))
    return None


b.custom(j, k_cut - 1, k_cut - 0.9, scissors11)
b.hit(j, k_cut, "clap", 0.8, "剪掉叶子")
b.hit(j, k_grow, "pop", 0.7, "换个样子长回来")
b.shots[j].shake = [(k_cut, 6.0)]

# ================================================================ 屏 15：手指指人（打叉）→ 指流程（打勾）；“问事，不问人”
cx, cy = R[15]
j = L.scene(15, (cx, cy + 20, Z))
LI15 = (cx - 410, cy + 440, 0.85)
WG15 = (cx + 410, cy + 440, 0.85)
k_pt = kq(j, wt(19, 2, 0.75), lo=3)
k_x15 = k_pt + 1
k_fl = kq(j, wt(20, 0, 0.5), lo=k_x15 + 1)
k_ck15 = kq(j, wt(20, 1, 0.6), lo=k_fl + 1)
k_sl = kq(j, wt(20, 2, 0.5), lo=k_ck15 + 1)
FLOW15 = [("下单", cx - 270), ("审批", cx), ("发货", cx + 270)]
FY15 = cy - 220


def li15_rh(T):
    x, y, s = LI15
    hy = y - 290 * s
    if T >= tb(15, k_fl):
        return x + 110 * s, hy - 70 * s
    if T >= tb(15, k_pt):
        return x + 170 * s, hy + 60 * s
    return None


b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI15, rh=li15_rh,
                             mood=lambda T: "smile" if T >= tb(15, k_ck15) else "flat"), sfx="pop", gain=0.55)
label(j, 1.4, "小李", LI15[0], LI15[1] + 80, 60)
b.custom(j, 2, 2.3, L.figure(draw_wang, j, 2, *WG15,
                             mood=lambda T: "sad" if tb(15, k_pt) <= T < tb(15, k_fl) else "smile"),
         sfx="pop", gain=0.55)
label(j, 2.4, "小王", WG15[0], WG15[1] + 80, 60, BLUE)


def point15(c, kk, T):
    t0, t1 = tb(15, k_pt), tb(15, k_fl)
    if T < t0:
        return None
    a = fade(T, t0, 0.2) * (1 - fade(T, t1 - 0.1, 0.3))
    if a <= 0:
        return None
    x, y, s = LI15
    hy = y - 290 * s
    p0 = (x + 170 * s + 20, hy + 60 * s)
    p1 = (WG15[0] - 90, WG15[1] - 290 * WG15[2])
    pt = wb.marker(RED, 7, a)
    pt.setPathEffect(skia.DashPathEffect.Make([24, 16], 0))
    c.drawLine(*p0, *p1, pt)
    if T >= tb(15, k_x15):
        xx, yy = lerp(p0[0], p1[0], 0.5), lerp(p0[1], p1[1], 0.5)
        sc = C.slam_scale(T - tb(15, k_x15))
        with K.at(c, xx, yy, 0, sc):
            c.drawPath(cross(0, 0, 70), wb.marker(RED, 14, a))
    return None


b.custom(j, k_pt, k_pt + 0.3, point15, sfx="wood_high", gain=0.6)
b.hit(j, k_x15, "rim", 0.8, "打叉：别指人")
L.note(*[t_ for t_, _ in FLOW15])


def flow15(c, kk, T):
    t0 = tb(15, k_fl)
    for i, (t_, x) in enumerate(FLOW15):
        sc = pop_scale(T - t0 - 0.12 * i)
        if sc <= 0:
            continue
        with at_pop(c, x, FY15, sc):
            flow_box(c, x, FY15, t_, w=190, color=BLUE)
        if i < 2 and sc >= 1:
            c.drawPath(arrow((x + 100, FY15), (x + 168, FY15), 0.0, 18), wb.marker(BLUE, 5))
    return None


b.custom(j, k_fl, k_fl + 0.3, flow15, sfx="wood_high", gain=0.65)
b.path(j, k_ck15, k_ck15 + 0.4, check(cx + 470, FY15 - 10, 55), GREEN, 13, sfx="ding", gain=0.65)
L.note("问事，不问人")
b.custom(j, k_sl, k_sl + 0.3, L.slam_text("问事，不问人", cx, cy - 470, 110, RED, j, k_sl, font="black"), sfx="kick",
         gain=0.9)
b.shots[j].shake = [(k_sl, 12.0)]

# ================================================================ 屏 16：“三步”；做法一——写成一句话：哪里 / 什么时候 / 差多少
cx, cy = R[16]
j = L.scene(16, (cx, cy + 20, Z))
k_m16 = kq(j, wt(21, 0, 0.5), lo=1)
k_three = kq(j, wt(21, 1, 0.6), lo=k_m16 + 1)
k_h16 = kq(j, wt(22, 1, 0.3), lo=k_three + 1)
k_r = [kq(j, wt(22, 2, 0.25), lo=k_h16 + 1)]
k_r.append(kq(j, wt(22, 2, 0.55), lo=k_r[0] + 1))
k_r.append(kq(j, wt(22, 2, 0.9), lo=k_r[1] + 1))


def mole16(c, kk, T):
    cx, cy = R[16]
    t0 = tb(16, k_m16)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 420, cy - 380
    a = 1 - fade(T, tb(16, k_three), 0.3)
    if a <= 0:
        return None
    with at_pop(c, x, y, sc):
        hole(c, x, y, 150, 40, alpha=a)
        mole(c, x, y, ease_out(clamp01((T - t0) / 0.16)), r=40, alpha=a)
    return None


b.custom(j, k_m16, k_m16 + 0.3, mole16, sfx="pop", gain=0.6)
b.custom(j, k_three, k_three + 0.3, L.slam_text("三步", cx, cy - 440, 200, RED, j, k_three, rot=-4, font="black"),
         sfx="kick", gain=0.9)
b.shots[j].shake = [(k_three, 12.0)]
L.note("① 写成一句话")
b.custom(j, k_h16, k_h16 + 0.3, L.pop_text("① 写成一句话", cx, cy - 250, 80, BLUE, j, k_h16), sfx="pop", gain=0.6)
CARD16 = (cx + 100, cy + 150, 720, 460)
ROWS16 = ["哪里", "什么时候", "差多少"]
L.note(*ROWS16)
LI16 = (cx - 440, cy + 440, 0.8)


def card16(c, kk, T):
    x, y, w, h = CARD16
    sc = pop_scale(T - tb(16, k_h16))
    if sc <= 0:
        return None
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
        c.drawRoundRect(r, 20, 20, K.paint("#FFFDF2"))
        c.drawRoundRect(r, 20, 20, wb.marker(BLACK, 7))
        for i, t_ in enumerate(ROWS16):
            t_i = tb(16, k_r[i])
            yy = y - h / 2 + 90 + i * 140
            rs = pop_scale(T - t_i)
            if rs <= 0:
                continue
            ix = x - w / 2 + 80
            with at_pop(c, ix, yy, rs):
                if i == 0:
                    with K.at(c, ix, yy - 12, 180):
                        c.drawPath(drop_shape(0, 0, 24), K.paint(RED))
                        c.drawCircle(0, 0, 9, K.paint("#FFFFFF"))
                elif i == 1:
                    c.drawPath(wb.clock(ix, yy, 30), wb.marker(BLACK, 5))
                    c.drawPath(wb.hands_at(ix, yy, 30, 3, 0), wb.marker(BLACK, 5))
                else:
                    c.drawRect(skia.Rect.MakeXYWH(ix - 34, yy - 14, 68, 28), K.paint(YELLOW))
                    for m in range(5):
                        c.drawLine(ix - 26 + m * 13, yy - 14, ix - 26 + m * 13, yy - 2, wb.marker(BLACK, 3))
                    c.drawRect(skia.Rect.MakeXYWH(ix - 34, yy - 14, 68, 28), wb.marker(BLACK, 4))
            tw = K.text(c, t_, ix + 60, yy, 60, "hand", BLACK, clamp01(rs * 2), "left")
            pt = wb.marker(GRAY, 4, clamp01(rs * 2))
            c.drawLine(ix + 90 + tw, yy + 26, x + w / 2 - 50, yy + 26, pt)
    return None


b.custom(j, k_h16, k_h16 + 0.3, card16)
for i in range(3):
    b.hit(j, k_r[i], "wood_high" if i != 1 else "wood_low", 0.6, f"写下：{ROWS16[i]}")


def li16(c, kk, T):
    x, y, s = LI16
    sc = pop_scale(T - tb(16, k_h16))
    if sc <= 0:
        return None
    hy = y - 290 * s
    wr = any(tb(16, k_) <= T < tb(16, k_) + 0.5 for k_ in k_r)
    rh = (x + 150 + (10 * math.sin(T * 30) if wr else 0), hy + 80 + (6 * math.cos(T * 30) if wr else 0))
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "flat", rh=rh)
        c.drawLine(rh[0], rh[1], rh[0] + 30, rh[1] - 50, wb.marker(BLUE, 8))
    K.text(c, "小李", x, y + 75, 56, "hand", BLACK, clamp01(sc * 2))
    return None


b.custom(j, k_h16, k_h16 + 0.3, li16)

# ================================================================ 屏 17：做法二——连问几个为什么，每个答案去现场核对（脚印 + 打勾）
cx, cy = R[17]
j = L.scene(17, (cx, cy + 20, Z))
L.note("② 去现场核对", "现场")
b.custom(j, 1, 1.3, L.pop_text("② 去现场核对", cx, cy - 480, 84, BLUE, j, 1), sfx="pop", gain=0.6)
k_c17 = kq(j, wt(23, 1, 0.1), lo=2)
k_fp = kq(j, wt(23, 2, 0.25), lo=k_c17 + 3)
k_site = k_fp
k_ck17 = kq(j, wt(23, 2, 0.9), lo=k_fp + 2)
WC17 = [(cx - 300, cy - 280 + 220 * i) for i in range(3)]
for i, (x, y) in enumerate(WC17):
    k_ = k_c17 + i

    def wc17(c, sc, T, x=x, y=y, i=i):
        with at_pop(c, x, y, sc):
            why_card(c, x, y, w=250, h=90, size=50)
            if i < 2:
                c.drawPath(arrow((x, y + 52), (x, y + 165), 0.0, 20), wb.marker(RED, 5))
    b.custom(j, k_, k_ + 0.3, pop_fn(j, k_, wc17), sfx="pop", gain=0.55)
SITE = (cx + 340, cy + 330)


def site17(c, sc, T):
    with at_pop(c, SITE[0], SITE[1], sc):
        factory(c, SITE[0], SITE[1])
        K.text(c, "现场", SITE[0], SITE[1] + 60, 56, "hand", BLACK)


b.custom(j, k_site, k_site + 0.3, pop_fn(j, k_site, site17), sfx="wood_low", gain=0.6)
FP = [(cx - 90 + 45 * i, cy - 150 + 60 * i + (16 if i % 2 else -16)) for i in range(6)]
LI17 = (cx - 480, cx + 80, cy + 440, 0.7)


def li17(c, kk, T):
    x0, x1, y, s = LI17
    sc = pop_scale(T - tb(17, 1))
    if sc <= 0:
        return None
    t0 = tb(17, k_fp)
    x, dy, moving = C.walk(T, t0, tb(17, k_fp + 2) - t0, x0, x1)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y + dy, s, "smile" if T >= tb(17, k_ck17) else "flat")
    return None


b.custom(j, 1, 1.3, li17)


def steps17(c, kk, T):
    t0 = tb(17, k_fp)
    for i, (x, y) in enumerate(FP):
        t_i = t0 + i * (tb(17, k_fp + 2) - t0) / len(FP)
        if T >= t_i:
            footprint(c, x, y, 145, fade(T, t_i, 0.12), 0.9)
    return None


b.custom(j, k_fp, k_fp + 0.3, steps17)
for i in range(2):
    b.hit(j, k_fp + i, "shaker", 0.55, "脚印")


def checks17(c, kk, T):
    t0 = tb(17, k_ck17)
    for i, (x, y) in enumerate(WC17):
        f = clamp01((T - t0 - 0.12 * i) / 0.3)
        if f > 0:
            part, _ = wb.partial(check(x + 175, y, 34), f)
            c.drawPath(part, wb.marker(GREEN, 10))
    return None


b.custom(j, k_ck17, k_ck17 + 0.6, checks17, sfx="ding", gain=0.6)

# ================================================================ 屏 18：做法三——挖到能动手的那一层停下，扳手改流程；“都怪你”打叉
cx, cy = R[18]
j = L.scene(18, (cx, cy + 20, Z))
L.note("③ 改流程", "停", "都怪你！")
b.custom(j, 1, 1.3, L.pop_text("③ 改流程", cx, cy - 480, 84, BLUE, j, 1), sfx="pop", gain=0.6)
COLX = cx - 330
LAY = [cy - 300 + 150 * i for i in range(4)]


def col18(c, kk, T):
    a = fade(T, tb(18, 1), 0.3)
    for i, y in enumerate(LAY):
        r = skia.Rect.MakeXYWH(COLX - 150, y - 60, 300, 120)
        c.drawRoundRect(r, 14, 14, K.paint(SOIL, a))
        c.drawRoundRect(r, 14, 14, wb.marker(SOIL_LINE, 5, a))
    return None


b.custom(j, 1, 1.1, col18)
k_l18 = kq(j, wt(24, 1, 0.15), lo=2)
k_stop18 = max(kq(j, wt(24, 2, 0.3), lo=k_l18 + 2), k_l18 + 2)
k_fix = kq(j, wt(24, 3, 0.5), lo=k_stop18 + 1)
k_no = kq(j, wt(24, 4, 0.4), lo=k_fix + 1)


def dig18(c, kk, T):
    """红色标记一层层往下，到第三层停下。"""
    for i in range(3):
        t_i = tb(18, k_l18 + i * 0.5 if i < 2 else k_stop18)
        if T < t_i:
            break
        a = fade(T, t_i, 0.15)
        y = LAY[i]
        r = skia.Rect.MakeXYWH(COLX - 150, y - 60, 300, 120)
        c.drawRoundRect(r, 14, 14, K.paint(CAVE, a))
        c.drawRoundRect(r, 14, 14, wb.marker(RED if i == 2 else SOIL_LINE, 7 if i == 2 else 5, a))
        if i < 2:
            K.text(c, "?", COLX, y, 60, "black", RED, a)
        else:
            wrench(c, COLX - 30, y - 40, -40, 0.55, a)
    return None


b.custom(j, k_l18, k_l18 + 0.3, dig18, sfx="tom", gain=0.7)
b.hit(j, k_l18 + 1, "tom", 0.6, "再往下一层")
b.custom(j, k_stop18, k_stop18 + 0.3, L.stamp("停", COLX + 225, LAY[2], 60, j, k_stop18, rot=8), sfx="rim", gain=0.8)
FX18 = cx + 240
FYS = [cy - 300, cy - 130, cy + 40]


def flow18(c, kk, T):
    sc = pop_scale(T - tb(18, 2))
    if sc <= 0:
        return None
    t_fix = tb(18, k_fix)
    fixed = T >= t_fix
    for i, y in enumerate(FYS):
        with at_pop(c, FX18, y, sc):
            bad = i == 1 and not fixed
            flow_box(c, FX18, y, "", w=230, h=100, color=RED if bad else (GREEN if i == 1 else BLUE),
                     fill=RED_FILL if bad else (GREEN_FILL if i == 1 else "#FFFFFF"))
            for m in range(2):
                c.drawLine(FX18 - 70, y - 15 + m * 30, FX18 + 70 - m * 40, y - 15 + m * 30, wb.marker(GRAY, 4))
            if i < 2:
                c.drawPath(arrow((FX18, y + 54), (FX18, y + 116), 0.0, 16), wb.marker(BLUE, 5))
    if t_fix - 0.4 <= T < t_fix + 0.6:
        rot = lerp(-60, 20, ease_in_out(clamp01((T - t_fix + 0.4) / 0.4)))
        wrench(c, FX18 + 170, FYS[1] - 10, rot, 0.8, 1 - fade(T, t_fix + 0.3, 0.3))
    if fixed:
        K.ripple(c, FX18, FYS[1], T - t_fix, GREEN, 160, 7, 0.9, 0.6)
    return None


b.custom(j, 2, 2.3, flow18, sfx="wood_high", gain=0.6)
b.hit(j, k_fix, "wood_high", 0.75, "扳手改流程")
BS18 = (cx + 470, cy + 440, 0.72)
b.custom(j, 2, 2.3, L.figure(draw_boss, j, 2, *BS18,
                                            rh=lambda T: (BS18[0] - 120, BS18[1] - 290 * BS18[2] + 40),
                                            mood=lambda T: "sad" if T >= tb(18, k_no + 1) else "flat"))
b.custom(j, k_no, k_no + 0.3, L.pop_bubble("都怪你！", cx + 130, cy + 300, j, k_no, size=58, color=RED, tail=1),
         sfx="pop", gain=0.6)
b.path(j, k_no + 1, k_no + 1.4, cross(cx + 130, cy + 300, 90), RED, 14, sfx="rim", gain=0.8)

# ================================================================ 屏 19：锤子放下，洞一个个盖上，小李伸懒腰
cx, cy = R[19]
j = L.scene(19, (cx, cy + 20, Z))
GY19 = cy + 440
HOLES19 = [cx - 200, cx + 90, cx + 380]
LI19 = (cx - 470, GY19, 0.85)
k_fix19 = kq(j, wt(25, 0, 0.3), lo=1)
k_put = kq(j, wt(25, 0, 0.85), lo=k_fix19 + 1)
k_lid = kq(j, wt(25, 1, 0.3), lo=k_put + 1)
k_st = k_lid + 3
b.path(j, 0, 0.6, P((cx - 580, GY19), (cx + 580, GY19)), BLACK, 6, sfx="wood_high", gain=0.55)


def holes19(c, kk, T):
    sc = pop_scale(T - tb(19, 0))
    for i, hx in enumerate(HOLES19):
        lid = clamp01((T - tb(19, k_lid + i) + 0.15) / 0.15)
        with at_pop(c, hx, GY19, sc):
            hole(c, hx, GY19, lid=lid)
    return None


b.custom(j, 0, 0.3, holes19)
for i in range(3):
    b.hit(j, k_lid + i, "wood_high" if i % 2 == 0 else "wood_low", 0.65, "盖上洞")


def li19(c, kk, T):
    x, y, s = LI19
    sc = pop_scale(T - tb(19, 1))
    if sc <= 0:
        return None
    hy = y - 290 * s
    t_p = tb(19, k_put)
    t_s = tb(19, k_st)
    stretch = ease_out(clamp01((T - t_s) / 0.3))
    if T < t_p:
        rh = (x + 70 * s, hy + 110 * s)
        lh = None
    else:
        rh = (lerp(x + 70 * s, x + 90 * s, stretch), lerp(hy + 170 * s, hy - 60 * s, stretch))
        lh = (lerp(x - 70 * s, x - 90 * s, stretch), lerp(hy + 170 * s, hy - 60 * s, stretch))
    with at_pop(c, x, y, sc):
        if T < t_p - 0.2:
            hammer(c, rh[0], rh[1], -60, ln=190)
        draw_li(c, x, y, s, "smile" if T >= t_p else "flat", rh=rh, lh=lh)
    if T >= t_p - 0.2:
        f = ease_out(clamp01((T - t_p + 0.2) / 0.2))
        hx0, hy0 = x + 50, lerp(y - 200, y - 16, f)
        hammer(c, hx0, hy0, lerp(-60, -180, f), ln=150)
    K.text(c, "小李", x, y + 75, 56, "hand", BLACK, clamp01(sc * 2))
    if stretch > 0:
        for i in range(5):
            a_ = math.radians(-150 + i * 30)
            r0, r1 = 120, 120 + 50 * stretch
            c.drawLine(x + r0 * math.cos(a_), hy - 60 + r0 * math.sin(a_), x + r1 * math.cos(a_),
                       hy - 60 + r1 * math.sin(a_), wb.marker(YELLOW, 7, stretch))
    return None


b.custom(j, 1, 1.3, li19, sfx="pop", gain=0.55)
b.hit(j, k_put, "wood_low", 0.75, "锤子放下")
L.note("根上修好了")
b.custom(j, k_fix19, k_fix19 + 0.3, L.stamp("根上修好了", cx + 60, cy - 330, 90, j, k_fix19, color=GREEN, rot=-6),
         sfx="kick", gain=0.75)
b.hit(j, k_st, "ding", 0.6, "伸懒腰")

# ================================================================ 屏 20：评论区见 + 下一讲预告
cx, cy = R[20]
j = L.scene(20, (cx, cy + 20, Z))
LI20 = (cx - 430, cy + 120, 0.7)
k_q20 = kq(j, wt(26, 1, 0.5), lo=1)
k_type = kq(j, wt(27, 0, 0.3), lo=k_q20 + 1)
k_rep = kq(j, wt(27, 1, 0.3), lo=k_type + 1)
INP = (cx + 110, cy - 460, 760, 110)
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI20, mood="flat",
                             rh=lambda T: (LI20[0] + 110, LI20[1] - 290 * LI20[2] + 40) if T >= tb(20, k_type) else None),
         sfx="pop", gain=0.6)
b.custom(j, k_q20, k_q20 + 0.3, L.slam_text("?", LI20[0] + 90, LI20[1] - 330, 110, RED, j, k_q20, font="black"),
         sfx="rim", gain=0.7)
L.note("?", "打印机老卡纸", "发送")


def input20(c, kk, T):
    x, y, w, h = INP
    sc = pop_scale(T - tb(20, k_type))
    if sc <= 0:
        return None
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
        c.drawRoundRect(r, h / 2, h / 2, K.paint("#FFFFFF"))
        c.drawRoundRect(r, h / 2, h / 2, wb.marker(BLUE, 7))
        msg = "打印机老卡纸"
        n = min(len(msg), int((T - tb(20, k_type)) / 0.14) + 1)
        tw = K.text(c, msg[:n], x - w / 2 + 40, y, 52, "hand", BLACK, 1, "left")
        if (T * 2) % 1 < 0.5:
            c.drawLine(x - w / 2 + 48 + tw, y - 28, x - w / 2 + 48 + tw, y + 28, wb.marker(BLUE, 5))
        c.drawRoundRect(skia.Rect.MakeXYWH(x + w / 2 - 150, y - 36, 130, 72), 36, 36, K.paint(BLUE))
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
    return None


b.custom(j, k_type, k_type + 0.3, input20, sfx="wood_high", gain=0.6)
for i in range(3):
    k_ = k_rep + i
    x_, y_ = cx + 80 + (i % 2) * 120, cy - 300 + 125 * i

    def rep20(c, sc, T, x_=x_, y_=y_):
        with at_pop(c, x_, y_, sc):
            bubble_txt(c, "为什么？", x_, y_, 48, RED, tail=-1, h=96)
    b.custom(j, k_, k_ + 0.3, pop_fn(j, k_, rep20), sfx="pop", gain=0.55)
# 2026-11 收尾鼓励（第 28 句）：镜头下移；地下画出根，小李从地洞里爬出来，洞口长出小草；预告卡整体下移 DY
DY = 730
k_e = kq(j, wt(28, 0, 0.0), lo=k_rep + 3)
b.move(j, k_e, (cx, cy + 860, Z), 1.1)
k_e1 = k_e + 2
k_root = kq(j, wt(28, 0, 0.7), lo=k_e1 + 1)
k_up = kq(j, wt(28, 1, 0.25), lo=k_root + 1)
k_grass = kq(j, wt(28, 1, 0.85), lo=k_up + 1)
GY20 = cy + 760
HX20 = cx - 120
ROOT20 = wb.join(P((HX20, GY20 + 32), (HX20 - 10, GY20 + 90), (HX20 + 10, GY20 + 150)),
              P((HX20 - 10, GY20 + 90), (HX20 - 60, GY20 + 135)), P((HX20 + 2, GY20 + 120), (HX20 + 55, GY20 + 165)))


def climb20(c, kk, T):
    """地洞里只露出脑袋的小李 → 爬出来站到洞边，笑；洞口冒出小草。"""
    sc = pop_scale(T - tb(20, k_e1))
    if sc <= 0:
        return None
    s = 0.8
    with at_pop(c, HX20, GY20, sc):
        c.drawLine(cx - 520, GY20, cx + 520, GY20, wb.marker("#8A5A2B", 7))
        hole(c, HX20, GY20, 240, 64)
        f = ease_in_out(clamp01((T - tb(20, k_up)) / 0.6))
        x = lerp(HX20, HX20 + 240, ease_in_out(clamp01((T - tb(20, k_up) - 0.3) / 0.5)))
        y = lerp(GY20 + 170, GY20, f)
        c.save()
        if f < 1:
            c.clipRect(skia.Rect.MakeLTRB(x - 300, y - 400, x + 300, GY20 + 8))
        draw_li(c, x, y, s, "smile" if f >= 1 else "sad")
        c.restore()
        g = ease_out(clamp01((T - tb(20, k_grass)) / 0.4))
        if g > 0:
            for n, dx in enumerate((-60, -20, 20, 60)):
                h = (50 + 25 * (n % 2)) * g
                c.drawPath(P((HX20 + dx, GY20 - 6), (HX20 + dx + (8 if n % 2 else -8), GY20 - 6 - h)), wb.marker(GREEN, 8))
    return None


b.custom(j, k_e1, k_e1 + 0.3, climb20, sfx="pop", gain=0.6)
b.path(j, k_root, k_root + 0.5, ROOT20, "#8A5A2B", 7, sfx="wood_low", gain=0.6)
b.custom(j, k_root, k_root + 0.3, L.pop_text("根", HX20 + 110, GY20 + 130, 54, "#8A5A2B", j, k_root))
b.hit(j, k_up, "wood_high", 0.7, "小李爬出地洞")
b.custom(j, k_grass, k_grass + 0.3, L.pop_text("不再被困住", cx, cy + 390, 70, BLUE, j, k_grass), sfx="ding", gain=0.7)
k_n20 = kq(j, wt(29, 0, 0.15), lo=k_grass + 1)
L.note("下一讲", "方案挺好，为什么一开会就被否？", "否")
b.path(j, k_n20, k_n20 + 0.6, rect(cx, cy + 390 + DY, 1060, 260, 24), BLUE, 8, sfx="wood_high")
b.text(j, k_n20 + 0.5, k_n20 + 0.8, "下一讲", cx - 120, cy + 310 + DY, 50, BLUE)
b.text(j, k_n20 + 0.8, k_n20 + 2.2, "方案挺好，为什么一开会就被否？", cx - 70, cy + 400 + DY, 54, BLACK)


def plan20(c, kk, T):
    cx, cy = R[20]
    t0 = tb(20, k_n20 + 2.2)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 420, cy + 420 + DY
    with at_pop(c, x, y, sc, rot=6):
        c.drawPath(wb.doc(x, y, 110, 140, 3), K.paint("#FFFFFF"))
        c.drawPath(wb.doc(x, y, 110, 140, 3), wb.marker(BLACK, 5))
        for i in range(3):
            st = C.slam_scale(T - t0 - 0.3 - 0.25 * i)
            if st > 0:
                with K.at(c, x - 30 + 30 * i, y - 30 + 30 * i, -12, st * 0.9):
                    c.drawCircle(0, 0, 26, wb.marker(RED, 5))
                    K.text(c, "否", 0, 0, 30, "hand", RED)
    return None


b.custom(j, k_n20 + 2.2, k_n20 + 2.5, plan20)

# ================================================================ 收尾
def _clipped(fn):
    def g(c, kk, T):
        stage_clip(c)
        return fn(c, kk, T)
    return g


for _it in b.items:                 # 所有自定义项裁在白板舞台内（页眉、字幕带以下不画）
    if _it["kind"] == "custom":
        _it["fn"] = _clipped(_it["fn"])

L.finish(cover_shot=1, square_shot=10)
L.export(globals())
