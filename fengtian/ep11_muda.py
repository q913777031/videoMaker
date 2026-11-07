"""《丰田模式》11 浪费：一天下来，有多少时间在白忙？（白板手绘 + AI 旁白，竖屏 2:3）

故事贯穿：跟着小李过一天。第 4–9 屏顶上挂着“小李的一天”时间轴（9 点—18 点）和右上角的浪费计数器，
每碰到一种浪费：先砸下它的名字，再飞出“+1”，计数器加一、时间轴上那一段涂灰；到第八种计数器停在 8。
- 0–3 秒：表盘切成八块，一块块变灰，“白忙”砸下，右上角计数器“0”；
- 打工人日常：下班路上回头看办公楼，“？”，空着的时间轴；
- 书中做法（drop）：顾客举着钱包看工位上的两步，愿意付钱的亮绿，“等签字”变灰，drop 砸下“浪费”；
  八个空格（前七格大野耐一、第八格“作者加的”），小李拿着本子准备记，计数器挂上；
- 小李的一天：九点等审批（沙漏）/ 十点文件在三个群里转 / 十一点领导要一句话、做了十页 / 下午三张表落灰、旧版本越堆越高 /
  傍晚鼠标在十几个文件夹里乱窜、报告一格红整份重做 / 第八种：灯泡亮了，嘴上贴胶布；
- 为什么要叫出名字：灰块混在忙碌的小人里，贴上名字，再一块块擦掉；
- 说回我们：五版方案只改几个字 / 挑电影挑半小时 / 管不了的和能管的，“三步”；三步做法；回家做顿饭；评论区与下一讲。
领导 common.draw_boss，大野耐一 common.draw_ohno，顾客、同事用本模块的小人；本讲没有车间员工。
文案见 fengtian/PLAN.md「### 11 浪费」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import core
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, draw_ohno, pop_scale,
                             rest_hands)
from whiteboard import engine as wb
from whiteboard.engine import P, check, circle, cross, join, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "丰田模式 · 书中做法", 2),
    ([4, 5], "丰田模式 · 书中做法", 3),
    ([6], "小李的一天 · 九点", 4),
    ([7], "小李的一天 · 十点", 5),
    ([8], "小李的一天 · 十一点", 6),
    ([9, 10], "小李的一天 · 下午", 7),
    ([11, 12], "小李的一天 · 傍晚", 8),
    ([13, 14], "小李的一天 · 第八种", 9),
    ([15, 16, 17], "为什么要叫出名字", 10),
    ([18, 19], "说回我们自己", 11),
    ([20], "说回我们自己", 12),
    ([21, 22], "说回我们自己", 13),
    ([23], "做法一 · 示意", 14),
    ([24], "做法二 · 示意", 15),
    ([25], "做法三 · 示意", 16),
    ([26], "早点回家", 17),
    ([27, 28, 29, 30], "评论区见", 18),
]

THEME = FT.get("11")          # 本讲样式（fengtian/theme.py）：浅橙点阵、开场 clock8、转场 swing
L = C.Lesson("11", SCREENS, drop_screen=2, board_size=(5000, 12600), theme=THEME)
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(17)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：第 3 章，丰田生产方式的核心是消除浪费；七种浪费出自大野耐一，第八种“员工没被用上的创造力”是作者加的。",
    "小李的一天、时长、计数器均为示意；小李、领导、顾客为虚构人物。",
]

GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL = "#8A8F99", "#D9DCE1", "#D3EDDC", "#F6C3BE", "#D5E3F7"
WOOD, NOTE_FILL, SKIN = "#E3C9A0", "#FFF1A8", "#FBE3CF"
WASTES = ["等待", "搬运", "过度加工", "过量生产", "库存", "多余的动作", "返工", "想法没用上"]
SLOTS = [(9, 10), (10, 11), (11, 12), (13.5, 14.5), (14.5, 15.5), (16, 17), (17, 18)]


_PUN = "，。：？！、；【】"


def wp(li, pi, frac=0.0):
    """第 li 句第 pi 段字幕念到 frac（0–1）处的本地秒（按字的位置换算）。"""
    pieces = L.LINES[li][1]
    n0 = sum(len([ch for ch in p_ if ch not in _PUN]) for p_ in pieces[:pi])
    n = len([ch for ch in pieces[pi] if ch not in _PUN])
    return L.char_time(li, min(n0 + int(frac * n), n0 + n - 1)) if frac < 1 else L.char_time(li, n0 + n - 1) + 0.2


def nbeats(j):
    return L.BOUNDS[j][1] - L.BOUNDS[j][0]


def kq(j, t_local, lo=0):
    """kb，但 lo 超出本屏时夹到最后一拍。"""
    return kb(j, t_local, lo=min(lo, nbeats(j) - 1))


def klast(j, tail=0.35):
    """本屏最后一个能放画面事件的拍：事件做完（tail 秒）后到切屏至少还停 1.6 秒。"""
    b0, b1 = L.BOUNDS[j]
    return max(k for k in range(b1 - b0) if core.bt(b0 + k) + tail <= core.bt(b1) - 1.6)


def cap(j, k, tail=0.35):
    return min(k, klast(j, tail))


def nx(j, t_local, prev, gap=1):
    """离 t_local 最近、且至少在 prev 之后 gap 拍的拍号（不超过本屏最后可用拍）。"""
    return cap(j, max(kq(j, t_local, prev + gap), prev + gap))


# ================================================================ 小工具

def pop_fn(j, k, draw, dur=0.32):
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


def head_of(x, y, s):
    return x, y - 290 * s


def sparkle(c, x, y, dt, color=YELLOW, n=8, r0=40, r1=130):
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


def doc_card(c, x, y, w=200, h=250, color=BLACK, rows=4, fill="#FFFFFF", rot=0.0):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, fill, color, 6, 8)
        for r in range(rows):
            yy = -h / 2 + 45 + r * (h - 80) / max(1, rows - 1)
            C.line(c, (-w / 2 + 26, yy), (w / 2 - 26 - (r % 2) * 36, yy), GRAY, 5)


def cursor(c, mx, my, s=1.0):
    p = P((mx, my), (mx, my + 56 * s), (mx + 14 * s, my + 42 * s), (mx + 26 * s, my + 66 * s), (mx + 36 * s, my + 60 * s),
          (mx + 24 * s, my + 38 * s), (mx + 42 * s, my + 36 * s), close=True)
    c.drawPath(p, K.paint("#FFFFFF"))
    c.drawPath(p, wb.marker(BLACK, 5))


def hourglass(c, x, y, s, f, rot=0.0):
    """沙漏：f 为上半沙子流下的比例 0–1。"""
    with K.at(c, x, y, rot, s):
        for sg in (-1, 1):
            C.line(c, (-70, sg * 110), (70, sg * 110), "#A9773E", 12)
        glass = P((-55, -100), (55, -100), (8, 0), (55, 100), (-55, 100), (-8, 0), close=True)
        c.drawPath(glass, K.paint("#FFFFFF"))
        top = P((-50 * (1 - f) - 6, -92 + 88 * f), (50 * (1 - f) + 6, -92 + 88 * f), (6, -4), (-6, -4), close=True)
        if f < 0.98:
            c.drawPath(top, K.paint(YELLOW))
        bot = P((-50, 92), (50, 92), (50 * (1 - f * 0.7), 92 - 70 * f), (-50 * (1 - f * 0.7), 92 - 70 * f), close=True)
        c.drawPath(bot, K.paint(YELLOW))
        C.line(c, (0, -4), (0, 90), YELLOW, 4)
        c.drawPath(glass, wb.marker(BLACK, 6))


def ohno_head(c, x, y, r=34):
    c.drawCircle(x, y, r, K.paint("#FFFFFF"))
    c.drawCircle(x, y, r, wb.marker(BLACK, 5))
    for sg in (-1, 1):
        c.drawCircle(x + sg * r * 0.4, y - r * 0.08, r * 0.3, wb.marker(BLACK, 3))
        side = skia.Path()
        side.addArc(skia.Rect.MakeXYWH(x - r * 1.12, y - r * 0.9, r * 2.24, r * 1.5), 180 if sg < 0 else 300, 60)
        c.drawPath(side, wb.marker(GRAY, 6))
    C.line(c, (x - r * 0.25, y + r * 0.5), (x + r * 0.25, y + r * 0.5), BLACK, 4)


def tape_mouth(c, hx, hy, s, alpha=1.0, rot=-8):
    with K.at(c, hx, hy + 20 * s, rot):
        c.drawRect(skia.Rect.MakeXYWH(-46 * s, -14 * s, 92 * s, 28 * s), K.paint("#E9E2CF", alpha))
        c.drawRect(skia.Rect.MakeXYWH(-46 * s, -14 * s, 92 * s, 28 * s), wb.marker(GRAY, 4, alpha))
        for i in range(-2, 3):
            C.line(c, (i * 18 * s, -10 * s), (i * 18 * s - 6 * s, 10 * s), GRAY, 2, alpha)


def draw_person(c, x, y, s, coat=BLUE_FILL, line=BLUE, hat=False, lh=None, rh=None, mood="flat", back=False, alpha=1.0):
    """路人 / 顾客：圆头、彩色外套；hat=True 戴一顶圆帽（顾客）。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    for ft in ((x - 48 * s, y), (x + 48 * s, y)):
        C.line(c, (x, y - 120 * s), ft, BLACK, 10, alpha)
    C.line(c, sh, lh, line, 10, alpha)
    C.line(c, sh, rh, line, 10, alpha)
    coat_p = P((x - 46 * s, hy + 58 * s), (x + 46 * s, hy + 58 * s), (x + 56 * s, y - 100 * s), (x - 56 * s, y - 100 * s),
               close=True)
    c.drawPath(coat_p, K.paint(coat, alpha))
    c.drawPath(coat_p, wb.marker(line, 7, alpha))
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    if back:
        c.drawPath(P((x - 40 * s, hy - 10 * s), (x - 20 * s, hy + 30 * s), (x + 20 * s, hy + 30 * s), (x + 40 * s, hy - 10 * s)),
                   wb.marker(BLACK, 6, alpha))
    else:
        C._eyes_mouth(c, x, hy, s, mood, alpha)
    if hat:
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 70 * s, hy - 52 * s, 140 * s, 18 * s), 9 * s, 9 * s, K.paint(line, alpha))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 40 * s, hy - 96 * s, 80 * s, 48 * s), 12 * s, 12 * s, K.paint(line, alpha))


def wallet(c, x, y, s=1.0, open_=0.0):
    with K.at(c, x, y, -8, s):
        box(c, 0, 0, 110, 76, "#C98B4B", "#7A4A1E", 5, 10)
        C.line(c, (-55, -10), (55, -10), "#7A4A1E", 4)
        if open_ > 0:
            for i in range(2):
                c.drawCircle(-14 + i * 30, -40 - 40 * open_ - i * 12, 18, K.paint(YELLOW))
                c.drawCircle(-14 + i * 30, -40 - 40 * open_ - i * 12, 18, wb.marker("#A9842A", 4))


def stamp_ev(j, k, s, x, y, size, rot=-6.0, sfx="kick", gain=0.85, color=RED):
    ev(j, k, L.stamp(s, x, y, size, j, k, color=color, rot=rot), sfx, gain)


# ================================================================ 小李的一天：顶部时间轴 + 计数器

X0D, X1D = -540, 230                    # 时间轴左右（相对 cx）
L.note("小李的一天", "9点", "12点", "18点", "浪费", "+1", *[str(i) for i in range(9)])


def hx_(cx, h):
    return cx + X0D + (h - 9) / 9 * (X1D - X0D)


def day(j, n0, adds, now=None, k0=0, sfx="wood_low", eighth=False):
    """时间轴 + 计数器。n0：已涂灰的块数；adds：[(拍, “+1”起点)]，每项让第 n0+i 块变灰、计数器加一；now：现在几点（小三角）。"""
    cx, cy = R[j]
    y = cy - 480
    xc, yc = cx + 410, y

    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k0))
        if sc <= 0:
            return None
        arrived = [tb(j, k_) + 0.45 for k_, _ in adds]
        n = n0 + sum(1 for t_ in arrived if T >= t_)
        with at_pop(c, cx - 150, y, sc):
            K.text(c, "小李的一天", cx + X0D + 120, y - 82, 40, "hand", GRAY)
            box(c, (hx_(cx, 9) + hx_(cx, 18)) / 2, y, X1D - X0D + 16, 64, "#FFFFFF", BLACK, 6, 10)
            for i in range(min(n, 7)):
                h0, h1 = SLOTS[i]
                dt = T - arrived[i - n0] if i >= n0 else 9.0
                g = C.slam_scale(dt) if dt < 0.6 else 1.0
                xa, xb = hx_(cx, h0) + 4, hx_(cx, h1) - 4
                with K.at(c, (xa + xb) / 2, y, 0, 1, g):
                    c.drawRect(skia.Rect.MakeXYWH(-(xb - xa) / 2, -26, xb - xa, 52), K.paint("#9AA0A8"))
            for h, s_ in ((9, "9点"), (12, "12点"), (18, "18点")):
                C.line(c, (hx_(cx, h), y + 32), (hx_(cx, h), y + 50), BLACK, 5)
                K.text(c, s_, hx_(cx, h), y + 76, 34, "sans_medium", GRAY)
            if now is not None:
                xn = hx_(cx, now)
                c.drawPath(P((xn, y - 36), (xn - 18, y - 66), (xn + 18, y - 66), close=True), K.paint(RED))
        with K.at(c, xc, yc, 3, sc):
            box(c, 0, 0, 220, 140, "#FFFFFF", RED if eighth and n >= 8 else BLACK, 8 if eighth and n >= 8 else 7, 18)
            K.text(c, "浪费", -48, 0, 44, "hand", GRAY)
            last = max([t_ for t_ in arrived if T >= t_], default=-9)
            with K.at(c, 58, 0, 0, C.slam_scale(T - last) if T - last < 0.6 else 1.0):
                K.text(c, str(n), 0, 2, 84, "hand", RED)
        for i, (k_, src) in enumerate(adds):        # “+1”从画面里飞向计数器
            t0 = tb(j, k_)
            if t0 <= T < t0 + 0.45:
                f = ease_in_out(clamp01((T - t0) / 0.45))
                px = lerp(src[0], xc + 58, f)
                py = lerp(src[1], yc, f) - math.sin(f * math.pi) * 110
                with K.at(c, px, py, 0, pop_scale(T - t0, 0.15) * lerp(1.0, 0.6, f)):
                    c.drawCircle(0, 0, 54, K.paint(RED))
                    K.text(c, "+1", 0, 3, 58, "black", "#FFFFFF")
        return None
    b.custom(j, k0, k0 + 0.3, fn, sfx=sfx, gain=0.6)
    for i, (k_, _) in enumerate(adds):
        b.hit(j, k_, "ding", 0.8, f"+1：{WASTES[n0 + i]}")


def waste_hit(j, li, ci, src, n0, name_xy, size=96, rot=-6.0, sfx="kick", frac=0.55, prev=0):
    """“这叫X”：砸下名字，下一拍“+1”飞向计数器。返回 (砸字拍, +1拍)。"""
    k_n = nx(j, wp(li, ci, frac), prev)
    k_p = cap(j, k_n + 1, 0.5)
    if k_p == k_n:
        k_n = max(prev + 1, k_n - 1)
    stamp_ev(j, k_n, WASTES[n0], name_xy[0], name_xy[1], size, rot, sfx)
    return k_n, (k_p, src)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：下班路上回头看办公楼，“？”；一条空着的时间轴
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 260
    BX = cx + 320
    k_li = 1
    k_clk = nx(j, wp(0, 1, 0.4), k_li)
    k_turn = nx(j, wp(0, 2, 0.3), k_clk)
    k_q = nx(j, wp(0, 3, 0.4), k_turn)
    k_line = nx(j, wp(1, 0, 0.3), k_q)
    k_what = nx(j, wp(1, 1, 0.6), k_line)
    L.note("？", "9点", "18点", "忙了什么？")
    b.path(j, 0, 0.8, join(wb.building(BX, GY, 340, 480), P((cx - 560, GY), (cx + 560, GY))), BLACK, 9, sfx="wood_low")

    def li(c, kk, T):
        sc = pop_scale(T - tb(j, k_li))
        if sc <= 0:
            return None
        x, dy, moving = C.walk(T, tb(j, k_li), tb(j, k_turn) - tb(j, k_li), cx + 60, cx - 280)
        s = 0.85
        turned = T >= tb(j, k_turn)
        with at_pop(c, x, GY, sc):
            c.save()
            if turned:                       # 回过身看楼
                c.translate(x, 0)
                c.scale(-1, 1)
                c.translate(-x, 0)
            draw_li(c, x, GY + dy, s, "sad" if T >= tb(j, k_q) else "flat", bag=True)
            c.restore()
        if turned:
            hx, hy = head_of(x, GY, s)
            g = pop_scale(T - tb(j, k_turn))
            with K.at(c, hx + 150, hy - 20, 0, g):
                c.drawPath(wb.arrow((-60, 30), (80, -20), -0.3, 26), wb.marker(BLUE, 6))
            gq = pop_scale(T - tb(j, k_q))
            if gq > 0:
                with K.at(c, hx, hy - 170, 6 * math.sin((T - tb(j, k_q)) * 3), gq):
                    K.text(c, "？", 0, 0, 220, "hand", RED)
        return None
    b.custom(j, k_li, k_li + 0.3, li, sfx="shaker", gain=0.6)
    b.hit(j, k_turn, "wood_high", 0.7, "小李回头看楼")
    b.hit(j, k_q, "rim", 0.8, "头顶大问号")

    def clk(c, sc, T):
        x, y = BX + 10, GY - 640
        with at_pop(c, x, y, sc):
            c.drawCircle(x, y, 80, K.paint("#FFFFFF"))
            c.drawPath(wb.clock(x, y, 80), wb.marker(BLACK, 7))
            c.drawPath(wb.hands_at(x, y, 80, 6, 0), wb.marker(RED, 8))
            # 月亮
            c.drawCircle(x - 220, y + 10, 50, K.paint(YELLOW))
            c.drawCircle(x - 196, y - 8, 46, K.paint("#FBFBF9"))
        return None
    ev(j, k_clk, pop_fn(j, k_clk, clk), "pop", 0.7)

    y = cy + 430

    def tl(c, kk, T):
        t0 = tb(j, k_line)
        if T < t0:
            return None
        f = ease_out(clamp01((T - t0) / 0.5))
        xa, xb = cx - 500, cx + 500
        box(c, lerp(xa, xb, 0.5 * f), y, (xb - xa) * f, 70, "#FFFFFF", BLACK, 6, 10)
        if f >= 1:
            for i in range(1, 9):
                C.line(c, (xa + i * 111, y - 35), (xa + i * 111, y + 35), GRAY_FILL, 4)
            K.text(c, "9点", xa, y + 80, 38, "sans_medium", GRAY)
            K.text(c, "18点", xb, y + 80, 38, "sans_medium", GRAY)
        g = pop_scale(T - tb(j, k_what))
        if g > 0:
            with K.at(c, cx, y, 0, g):
                K.text(c, "忙了什么？", 0, 2, 56, "hand", BLUE)
        return None
    ev(j, k_line, tl, "wood_high", 0.7)
    b.hit(j, k_what, "pop", 0.7, "时间轴上空空的")


screen1()


# ================================================================ 屏 2：顾客举钱包看工位上的两步：一步亮绿，“等签字”变灰；drop 砸下“浪费”
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    KD = L.drop_k()
    b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
    GY = cy + 470
    DY = cy + 170                          # 桌面
    A, B_ = (cx - 260, DY - 170), (cx + 60, DY - 170)
    k_cu = kq(j, wp(2, 0, 0.5), 1)
    k_q = nx(j, wp(2, 2, 0.3), k_cu)
    k_pay = nx(j, wp(2, 2, 0.9), k_q)
    k_gray = min(nx(j, wp(3, 0, 0.6), k_pay), KD - 1)
    L.note("写方案", "等签字", "愿意付钱吗？", "✓")
    b.path(j, 0, 0.7, join(P((cx - 520, DY), (cx + 240, DY)), P((cx - 480, DY), (cx - 480, GY)),
                           P((cx + 200, DY), (cx + 200, GY)), P((cx - 560, GY), (cx + 560, GY))), "#A9773E", 10,
           sfx="wood_low")

    def cards(c, kk, T):
        sc = pop_scale(T - tb(j, 0) - 0.3)
        if sc <= 0:
            return None
        paid = T >= tb(j, k_pay)
        gray = T >= tb(j, k_gray)
        for (x, y), s_, on, off in ((A, "写方案", paid, False), (B_, "等签字", False, gray)):
            g = 1 + 0.12 * pop_scale(T - tb(j, k_pay)) * (1 if on else 0)
            with K.at(c, x, y, 0, sc * g):
                fill = GREEN_FILL if on else (GRAY_FILL if off else "#FFFFFF")
                box(c, 0, 0, 270, 230, fill, GREEN if on else (GRAY if off else BLACK), 8, 16)
                K.text(c, s_, 0, -40, 56, "hand", GRAY if off else BLACK)
                if on:
                    c.drawPath(check(0, 50, 40), wb.marker(GREEN, 12))
                if off:
                    c.drawPath(cross(0, 50, 36), wb.marker(GRAY, 10))
        return None
    b.custom(j, 0, 0.3, cards)

    def cust(c, kk, T):
        sc = pop_scale(T - tb(j, k_cu))
        if sc <= 0:
            return None
        x, s = cx + 390, 0.95
        hx, hy = head_of(x, GY, s)
        up = clamp01((T - tb(j, k_cu) - 0.4) / 0.3)
        hand = (x - 120 * s, lerp(hy + 170 * s, hy - 20 * s, up))
        if T >= tb(j, k_pay):                    # 伸手把钱递向“写方案”
            f = ease_in_out(clamp01((T - tb(j, k_pay)) / 0.3))
            hand = (lerp(hand[0], x - 200 * s, f), lerp(hand[1], hy + 40 * s, f))
        with at_pop(c, x, GY, sc):
            draw_person(c, x, GY, s, coat=GREEN_FILL, line=GREEN, hat=True, lh=hand,
                        mood="smile" if T >= tb(j, k_pay) and T < tb(j, k_gray) else "flat")
            wallet(c, hand[0] - 20, hand[1] - 20, 1.0, clamp01((T - tb(j, k_pay)) / 0.3))
        if T >= tb(j, k_pay):
            dt = T - tb(j, k_pay)
            if dt < 0.6:
                f = ease_in_out(dt / 0.6)
                c.drawCircle(lerp(hand[0], A[0] + 100, f), lerp(hand[1] - 60, A[1] - 120, f) - math.sin(f * math.pi) * 90,
                             22, K.paint(YELLOW))
        return None
    b.custom(j, k_cu, k_cu + 0.3, cust, sfx="pop", gain=0.7)
    ev(j, k_q, L.pop_bubble("愿意付钱吗？", cx + 150, cy - 420, j, k_q, 60, BLACK, tail=1), "pop", 0.7)
    b.hit(j, k_pay, "ding", 0.8, "钱递给写方案")
    b.hit(j, k_gray, "tom", 0.75, "等签字变灰")
    stamp_ev(j, KD, "浪费", B_[0] + 60, DY + 130, 110, -8, "kick", 0.95)


screen2()


# ================================================================ 屏 3：八个空格（前七格大野耐一，第八格“作者加的”）；小李拿本子，计数器挂上
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 500
    Y8 = cy - 180
    xs = [cx - 490 + i * 140 for i in range(8)]
    k_box = 0
    k_oh = kq(j, wp(4, 1, 0.1), 1)
    k_heads = [k_oh + 1 + i // 3 for i in range(7)]
    k_8 = nx(j, wp(4, 2, 0.5), k_heads[-1])
    k_li = nx(j, wp(5, 0, 0.2), k_8)
    k_ctr = nx(j, wp(5, 1, 0.3), k_li)
    k_pen = nx(j, wp(5, 1, 0.9), k_ctr)
    L.note("八种", "作者加的", "浪费", "0", "记一笔")
    b.path(j, k_box, k_box + 0.8, join(*[rect(x, Y8, 120, 120, 14) for x in xs]), BLACK, 7, sfx="wood_high")
    b.text(j, 0.4, 0.9, "八种", cx, Y8 - 140, 72, BLACK)

    def heads(c, kk, T):
        for i in range(7):
            g = pop_scale(T - tb(j, k_heads[i]) - (i % 3) * 0.12)
            if g > 0:
                with K.at(c, xs[i], Y8, 0, g):
                    ohno_head(c, 0, 0, 38)
        g = pop_scale(T - tb(j, k_8))
        if g > 0:
            with K.at(c, xs[7], Y8, 0, g):
                box(c, 0, 0, 120, 120, NOTE_FILL, RED, 8, 14)
                K.text(c, "8", 0, 2, 72, "hand", RED)
            with K.at(c, xs[7] - 40, Y8 + 130, -4, g):
                K.text(c, "作者加的", 0, 0, 46, "hand", RED)
            C.line(c, (xs[7], Y8 + 70), (xs[7], Y8 + 96), RED, 5, clamp01(g))
        return None
    b.custom(j, k_heads[0], k_heads[0] + 0.3, heads)
    for k_ in sorted(set(k_heads)):
        b.hit(j, k_, "wood_high", 0.6, "七格贴上大野耐一")
    b.hit(j, k_8, "rim", 0.8, "第八格：作者加的")

    def oh(c, sc, T):
        x, s = cx - 380, 0.85
        hx, hy = head_of(x, GY, s)
        point = T >= tb(j, k_heads[0])
        with at_pop(c, x, GY, sc):
            draw_ohno(c, x, GY, s, rh=(x + 130 * s, hy - 40 * s) if point else None, mood="smile" if point else "flat")
        return None
    ev(j, k_oh, pop_fn(j, k_oh, oh), "pop", 0.7)

    def li(c, sc, T):
        x, s = cx + 150, 0.85
        hx, hy = head_of(x, GY, s)
        write = T >= tb(j, k_pen)
        pen = (x - 50 * s + (10 * math.sin(T * 18) if write else 0), hy + 130 * s)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile", lh=(x - 110 * s, hy + 150 * s), rh=pen)
            with K.at(c, x - 100 * s, hy + 150 * s, -10):
                box(c, 0, 0, 120, 150, NOTE_FILL, ORANGE, 5, 8)
                f = clamp01((T - tb(j, k_pen)) / 0.5)
                if f > 0:
                    C.line(c, (-40, -30), (-40 + 80 * f, -30), BLUE, 6)
                    if f >= 1:
                        C.line(c, (-40, 0), (-40 + 50 * clamp01((T - tb(j, k_pen) - 0.5) / 0.4), 0), BLUE, 6)
        return None
    ev(j, k_li, pop_fn(j, k_li, li), "pop", 0.7)

    def ctr(c, sc, T):
        x, y = cx + 410, cy - 480
        sw = C.wobble(T - tb(j, k_ctr), 8, 14, 4)
        with K.at(c, x, y - 60, 0, 1):
            C.line(c, (0, -70), (0, -10), GRAY, 5, clamp01(sc))
        with K.at(c, x, y, 3 + sw, sc):
            box(c, 0, 0, 220, 140, "#FFFFFF", BLACK, 7, 18)
            K.text(c, "浪费", -48, 0, 44, "hand", GRAY)
            K.text(c, "0", 58, 2, 84, "hand", RED)
        return None
    ev(j, k_ctr, pop_fn(j, k_ctr, ctr), "ding", 0.75)
    b.hit(j, k_pen, "wood_high", 0.6, "本子上记一笔")
    ev(j, k_pen, L.pop_text("记一笔", cx + 350, cy + 70, 60, BLUE, j, k_pen))


screen3()


# ================================================================ 屏 4：九点，等审批：流程里卡着沙漏；第一块灰，+1
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 500
    k_li = 1
    k_flow = kq(j, wp(6, 1, 0.2), 2)
    k_flip = nx(j, wp(6, 1, 0.8), k_flow)
    k_n, add = waste_hit(j, 6, 2, (cx + 230, cy - 230), 0, (cx + 200, cy + 150), prev=k_flip)
    day(j, 0, [add], now=9)
    L.note("提交", "审批中", "下一步", "等了一小时")
    FY = cy - 260
    nodes = [(cx - 420, "提交"), (cx - 30, "审批中"), (cx + 360, "下一步")]

    def flow(c, kk, T):
        t0 = tb(j, k_flow)
        if T < t0:
            return None
        for i, (x, s_) in enumerate(nodes):
            g = pop_scale(T - t0 - i * 0.12)
            if g <= 0:
                continue
            with K.at(c, x, FY, 0, g):
                box(c, 0, 0, 210, 100, BLUE_FILL if i == 1 else "#FFFFFF", BLUE if i == 1 else BLACK, 6, 14)
                K.text(c, s_, 0, 2, 46, "hand", BLUE if i == 1 else (GRAY if i == 2 else BLACK))
            if i:
                C.line(c, (nodes[i - 1][0] + 110, FY), (x - 120, FY), GRAY, 6, clamp01(g))
                c.drawPath(P((x - 140, FY - 16), (x - 116, FY), (x - 140, FY + 16)), wb.marker(GRAY, 6, clamp01(g)))
        # 沙漏：在“审批中”下面，第 k_flip 拍翻一次
        tf = tb(j, k_flip)
        rot = 0.0 if T < tf else 180 * ease_in_out(clamp01((T - tf) / 0.35))
        f = clamp01((T - t0) / 3.0) if T < tf else clamp01((T - tf - 0.35) / 4.0)
        hourglass(c, cx - 30, FY + 230, 0.9, f, rot if rot < 180 else 0)
        return None
    ev(j, k_flow, flow, "pop", 0.7)
    b.hit(j, k_flip, "tom", 0.75, "沙漏翻过来")

    def li(c, sc, T):
        x, s = cx - 330, 0.85
        hx, hy = head_of(x, GY, s)
        tap = math.sin(T * 14) * 8 if T >= tb(j, k_flow) else 0
        with at_pop(c, x, GY, sc):
            desk_y = GY - 130
            C.line(c, (x + 40, desk_y), (x + 380, desk_y), "#A9773E", 10)
            C.line(c, (x + 360, desk_y), (x + 360, GY), "#A9773E", 9)
            box(c, x + 240, desk_y - 70, 180, 120, "#FFFFFF", BLACK, 6, 10)
            draw_li(c, x, GY, s, "sad" if T >= tb(j, k_flip) else "flat", rh=(x + 120 * s, desk_y - 10 + tap))
        clk_x, clk_y = cx - 320, cy - 60
        c.drawCircle(clk_x, clk_y, 70, K.paint("#FFFFFF"))
        c.drawPath(wb.clock(clk_x, clk_y, 70), wb.marker(BLACK, 6))
        m = 0 if T < tb(j, k_flip) else 60 * clamp01((T - tb(j, k_flip)) / 1.2)
        c.drawPath(wb.hands_at(clk_x, clk_y, 70, 9, m), wb.marker(RED, 7))
        if m >= 60:
            K.text(c, "等了一小时", clk_x + 10, clk_y + 110, 44, "hand", RED)
        return None
    ev(j, k_li, pop_fn(j, k_li, li), "wood_low", 0.6)


screen4()


# ================================================================ 屏 5：十点，同一份文件在三个群之间来回飞
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    k_grp = 1
    k_fly = kq(j, wp(7, 1, 0.3), 2)
    k_fly2 = nx(j, wp(7, 1, 0.9), k_fly)
    k_n, add = waste_hit(j, 7, 2, (cx, cy - 60), 1, (cx + 240, cy + 260), prev=k_fly2)
    day(j, 1, [add], now=10)
    G = [(cx - 380, cy - 240, "项目群"), (cx + 330, cy - 240, "部门群"), (cx - 30, cy + 130, "客户群")]
    L.note(*[g[2] for g in G])

    def grp(c, kk, T):
        if T >= tb(j, k_fly):
            for n in range(3):
                C.line(c, (G[n][0], G[n][1]), (G[(n + 1) % 3][0], G[(n + 1) % 3][1]), GRAY_FILL, 5)
        for i, (x, y, s_) in enumerate(G):
            g = pop_scale(T - tb(j, k_grp) - i * 0.15)
            if g <= 0:
                continue
            with K.at(c, x, y, 0, g):
                box(c, 0, 0, 230, 170, "#FFFFFF", GREEN, 7, 30)
                c.drawPath(wb.bubble(0, -12, 130, 70, -1), wb.marker(GREEN, 6))
                K.text(c, s_, 0, 58, 40, "hand", BLACK)
        # 文件在三个群之间转
        t0 = tb(j, k_fly)
        if T >= t0:
            u = (T - t0) * (1.6 if T < tb(j, k_fly2) else 2.4)
            i = int(u) % 3
            f = ease_in_out(u - int(u))
            a, z = G[i], G[(i + 1) % 3]
            x = lerp(a[0], z[0], f)
            y = lerp(a[1], z[1], f) - math.sin(f * math.pi) * 120
            doc_card(c, x, y - 40, 110, 140, BLUE, 3, rot=20 * math.sin(u * 6))
        return None
    ev(j, k_grp, grp, "pop", 0.7)
    b.hit(j, k_fly, "shaker", 0.7, "文件开始在群里转")
    b.hit(j, k_fly2, "wood_high", 0.6, "越转越快")

    def li(c, sc, T):
        x, s = cx - 380, 0.8
        hx, hy = head_of(x, GY, s)
        dz = T >= tb(j, k_fly2)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "sad" if dz else "flat", rh=(x + 90 * s, hy + 40 * s))
            box(c, x + 80 * s, hy + 20 * s, 60, 100, BLACK, BLACK, 4, 10)
            if dz:
                for n in range(2):
                    r = 30 + n * 22
                    p = skia.Path()
                    p.addArc(skia.Rect.MakeXYWH(hx - r, hy - 110 - r * 0.3, 2 * r, r * 0.6), (T * 400 + n * 90) % 360, 260)
                    c.drawPath(p, wb.marker(BLUE, 5))
        return None
    ev(j, 0, pop_fn(j, 0, li))


screen5()


# ================================================================ 屏 6：十一点，领导“一句话就行”，小李身后十页闪着星星的幻灯片
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    k_boss = 1
    k_say = kq(j, wp(8, 1, 0.4), 2)
    k_sl = nx(j, wp(8, 2, 0.3), k_say)
    k_sl2 = nx(j, wp(8, 2, 0.9), k_sl)
    k_n, add = waste_hit(j, 8, 3, (cx + 260, cy - 200), 2, (cx + 290, cy + 400), size=88, prev=k_sl2)
    day(j, 2, [add], now=11)
    L.note("一句话就行", "10页", "★")

    def boss(c, sc, T):
        x, s = cx - 400, 0.9
        hx, hy = head_of(x, GY, s)
        with at_pop(c, x, GY, sc):
            draw_boss(c, x, GY, s, rh=(x + 110 * s, hy + 60 * s) if T >= tb(j, k_say) else None)
        return None
    ev(j, k_boss, pop_fn(j, k_boss, boss), "pop", 0.7)
    ev(j, k_say, L.pop_bubble("一句话就行", cx - 280, cy - 230, j, k_say, 58, BLACK, tail=-1), "pop", 0.75)

    def slides(c, kk, T):
        t0, t1 = tb(j, k_sl), tb(j, k_sl2)
        n = 0 if T < t0 else min(10, 1 + int((T - t0) / max(0.1, t1 - t0) * 9))
        for i in range(n):
            x = cx + 180 + (i % 5) * 26 - 50
            y = cy - 40 + (i // 5) * 26 - 20 - i * 8
            g = pop_scale(T - (t0 + i * max(0.1, t1 - t0) / 9), 0.2)
            with K.at(c, x, y, -6 + i * 1.5, g):
                box(c, 0, 0, 300, 200, "#FFFFFF", ORANGE if i % 2 else BLUE, 6, 10)
                C.line(c, (-110, -50), (60, -50), GRAY, 6)
                for q in range(3):
                    c.drawRect(skia.Rect.MakeXYWH(-100 + q * 70, 40 - q * 30, 46, 40 + q * 30), K.paint(BLUE_FILL))
        if n >= 10:
            dt = T - t1
            sparkle(c, cx + 300, cy - 200, dt, YELLOW, 10, 60, 160)
            for i, (dx, dy) in enumerate(((-140, -190), (200, -150), (240, 90))):
                tw = 1 + 0.25 * math.sin(T * 9 + i * 2)
                with K.at(c, cx + 230 + dx, cy - 40 + dy, 0, tw):
                    K.text(c, "★", 0, 0, 56, "black", YELLOW)
            K.text(c, "10页", cx + 360, cy + 160, 60, "hand", RED)
        return None
    ev(j, k_sl, slides, "wood_high", 0.6)
    b.hit(j, k_sl2, "rim", 0.7, "十页幻灯片做完")

    def li(c, sc, T):
        x, s = cx - 40, 0.85
        hx, hy = head_of(x, GY, s)
        typing = tb(j, k_sl) <= T < tb(j, k_sl2) + 0.2
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile", rh=(x + 100 * s, hy + 150 * s + (math.sin(T * 20) * 10 if typing else 0)),
                    lh=(x + 60 * s, hy + 160 * s))
            if typing:
                C.line(c, (hx + 70, hy - 60), (hx + 100, hy - 90), BLUE, 5)
                C.line(c, (hx + 90, hy - 40), (hx + 130, hy - 50), BLUE, 5)
        return None
    ev(j, 0, pop_fn(j, 0, li), "wood_low", 0.5)


screen6()


# ================================================================ 屏 7：下午，三张没人要的表落灰；旧版本越堆越高
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    SH = cy - 60                          # 架子
    k_tab = kq(j, wp(9, 0, 0.6), 1)
    k_dust = nx(j, wp(9, 1, 0.5), k_tab)
    k_n1, add1 = waste_hit(j, 9, 2, (cx - 260, SH - 150), 3, (cx - 260, SH + 120), size=84, prev=k_dust)
    k_fd = nx(j, wp(10, 0, 0.3), add1[0])
    k_pile = nx(j, wp(10, 1, 0.5), k_fd)
    k_n2, add2 = waste_hit(j, 10, 2, (cx + 300, cy - 230), 4, (cx + 330, cy + 440), size=96, rot=5, sfx="rim",
                           prev=k_pile)
    day(j, 3, [add1, add2], now=15)
    L.note("表", "没人要", "旧版本", "×36")

    def li(c, sc, T):
        x, s = cx - 470, 0.8
        hx, hy = head_of(x, GY, s)
        shrug = T >= tb(j, k_dust)
        with at_pop(c, x, GY, sc):
            if shrug:
                draw_li(c, x, GY, s, "sad", lh=(x - 80 * s, hy + 20 * s), rh=(x + 80 * s, hy + 20 * s))
            else:
                draw_li(c, x, GY, s, "smile", rh=(x + 120 * s, hy + 80 * s))
        return None
    ev(j, 0, pop_fn(j, 0, li), "wood_low", 0.6)
    b.path(j, 0.4, 1.0, join(P((cx - 420, SH), (cx - 60, SH)), P((cx - 400, SH), (cx - 400, SH + 40)),
                             P((cx - 80, SH), (cx - 80, SH + 40))), "#A9773E", 9)

    def tabs(c, kk, T):
        dust = clamp01((T - tb(j, k_dust)) / 0.6)
        for i in range(3):
            g = pop_scale(T - tb(j, k_tab) - i * 0.15)
            if g <= 0:
                continue
            x = cx - 360 + i * 110
            with K.at(c, x, SH - 85, -4 + i * 4, g):
                box(c, 0, 0, 120, 160, GRAY_FILL if dust > 0.5 else "#FFFFFF", BLACK, 5, 6)
                for r in range(3):
                    C.line(c, (-40, -40 + r * 40), (40, -40 + r * 40), GRAY, 4)
                K.text(c, "表", 0, -62, 30, "hand", BLUE)
            if dust > 0:
                for q in range(6):
                    c.drawCircle(x - 40 + q * 16, SH - 168 - (q % 2) * 8, 4, K.paint(GRAY, dust))
        if dust > 0:
            web = skia.Path()
            for r in (30, 55):
                web.addArc(skia.Rect.MakeXYWH(cx - 70 - r, SH - 220 - r, 2 * r, 2 * r), 90, 90)
            web.moveTo(cx - 70, SH - 220)
            web.lineTo(cx - 70 - 60, SH - 220 + 10)
            web.moveTo(cx - 70, SH - 220)
            web.lineTo(cx - 70 - 20, SH - 220 + 60)
            c.drawPath(web, wb.marker(GRAY, 3, dust))
            K.text(c, "没人要", cx - 250, SH + 60, 46, "hand", GRAY, dust) if T < tb(j, k_n1) else None
        return None
    ev(j, k_tab, tabs, "pop", 0.7)
    b.hit(j, k_dust, "shaker", 0.6, "表上落灰")

    def folder(c, kk, T):
        t0 = tb(j, k_fd)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        x, y = cx + 300, cy + 220
        t1 = tb(j, k_pile)
        n = int(lerp(1, 36, clamp01((T - t0) / max(0.2, t1 - t0 + 0.3))))
        with at_pop(c, x, y, sc):
            for i in range(min(n, 14)):
                doc_card(c, x - 60 + (i % 3) * 30, y - 120 - i * 26, 170, 120, GRAY, 2, rot=(i * 37 % 11) - 5)
            body = P((x - 170, y - 110), (x - 170, y + 90), (x + 170, y + 90), (x + 170, y - 110), (x + 20, y - 110),
                     (x - 10, y - 150), (x - 170, y - 150), close=True)
            c.drawPath(body, K.paint("#F6D98B"))
            c.drawPath(body, wb.marker("#A9842A", 7))
            K.text(c, "旧版本", x, y - 10, 50, "hand", BLACK)
            K.text(c, f"×{n}", x + 200, y - 170, 56, "hand", RED)
        return None
    L.note(*[f"×{n}" for n in range(1, 37)])
    ev(j, k_fd, folder, "wood_high", 0.6)
    b.hit(j, k_pile, "wood_high", 0.6, "旧版本堆高")


screen7()


# ================================================================ 屏 8：傍晚，鼠标在十几个文件夹里乱窜；报告一格红，整份重做
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    k_fd = 0
    k_run = kq(j, wp(11, 1, 0.2), 1)
    k_n1, add1 = waste_hit(j, 11, 2, (cx - 250, cy - 120), 5, (cx - 250, cy + 70), size=80, prev=k_run)
    k_rep = nx(j, wp(12, 0, 0.3), add1[0])
    k_red = nx(j, wp(12, 0, 0.85), k_rep)
    k_loop = nx(j, wp(12, 1, 0.5), k_red)
    k_n2, add2 = waste_hit(j, 12, 2, (cx + 260, cy + 60), 6, (cx + 270, cy + 470), size=100, rot=6, sfx="rim",
                           prev=k_loop)
    day(j, 5, [add1, add2], now=17.5)
    FX = [(cx - 470 + (i % 4) * 150, cy - 290 + (i // 4) * 120) for i in range(12)]
    L.note("报告", "重做")

    def folders(c, kk, T):
        for i, (x, y) in enumerate(FX):
            g = pop_scale(T - tb(j, k_fd) - i * 0.04, 0.2)
            if g <= 0:
                continue
            with K.at(c, x, y, 0, g):
                body = P((-55, -30), (-55, 40), (55, 40), (55, -30), (5, -30), (-5, -46), (-55, -46), close=True)
                c.drawPath(body, K.paint("#F6D98B"))
                c.drawPath(body, wb.marker("#A9842A", 5))
        t0 = tb(j, k_run)
        if T >= t0:
            u = (T - t0) * 4.0
            i0, i1 = int(u) % 12, (int(u) + 5) % 12
            f = ease_in_out(u - int(u))
            seq = [(i * 7) % 12 for i in range(12)]
            a, z = FX[seq[int(u) % 12]], FX[seq[(int(u) + 1) % 12]]
            mx, my = lerp(a[0], z[0], f), lerp(a[1], z[1], f)
            c.drawRoundRect(skia.Rect.MakeXYWH(a[0] - 66, a[1] - 56, 132, 106), 12, 12, wb.marker(BLUE, 5, 1 - f))
            cursor(c, mx + 10, my)
        return None
    ev(j, k_fd, folders, "wood_low", 0.6)
    b.hit(j, k_run, "shaker", 0.7, "鼠标在文件夹里乱窜")

    def rep(c, sc, T):
        x, y = cx + 260, cy + 190
        red = T >= tb(j, k_red)
        with at_pop(c, x, y, sc):
            box(c, x, y, 330, 380, "#FFFFFF", BLACK, 7, 10)
            K.text(c, "报告", x, y - 150, 50, "hand", BLACK)
            for r in range(4):
                for q in range(3):
                    cxx, cyy = x - 100 + q * 100, y - 70 + r * 62
                    hot = red and r == 2 and q == 1
                    c.drawRect(skia.Rect.MakeXYWH(cxx - 46, cyy - 26, 92, 52), K.paint(RED_FILL if hot else "#FFFFFF"))
                    c.drawRect(skia.Rect.MakeXYWH(cxx - 46, cyy - 26, 92, 52), wb.marker(RED if hot else GRAY, 6 if hot else 3))
            tl = tb(j, k_loop)
            if T >= tl:
                with K.at(c, x + 30, y + 10, (T - tl) * 260, pop_scale(T - tl)):
                    c.drawPath(C.loop_arrow(0, 0, 110), wb.marker(RED, 12))
                K.text(c, "重做", x - 240, y + 120, 56, "hand", RED, clamp01((T - tl) / 0.2))
        return None
    ev(j, k_rep, pop_fn(j, k_rep, rep), "wood_high", 0.6)
    b.hit(j, k_red, "pop", 0.75, "一格变红")
    b.hit(j, k_loop, "tom", 0.75, "整份打回重做")

    def li(c, sc, T):
        x, s = cx - 420, 0.82
        GY = cy + 560
        hx, hy = head_of(x, GY, s)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "sad", rh=(x + 30 * s, hy + 5 * s) if T >= tb(j, k_loop) else None)
            for n in range(2):
                ph = (T * 1.4 + n * 0.5) % 1
                c.drawCircle(hx + (60 if n else -60), hy - 20 + ph * 60, 9, K.paint(BLUE, 1 - ph))
        return None
    ev(j, k_rep, pop_fn(j, k_rep, li))


screen8()


# ================================================================ 屏 9：第八种——灯泡亮了，嘴上贴胶布；第八格亮，计数器 8
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    LX, s = cx - 60, 1.05
    hx, hy = head_of(LX, GY, s)
    k_li = 0
    k_bulb = kq(j, wp(13, 1, 0.5), 1)
    k_pass = nx(j, wp(13, 2, 0.2), k_bulb)
    k_tape = nx(j, wp(13, 2, 0.8), k_pass)
    k_n, add = waste_hit(j, 14, 1, (hx + 200, hy - 230), 7, (cx + 20, cy - 290), size=84, rot=-3, prev=k_tape)
    day(j, 7, [add], now=18, eighth=True)
    L.note("省事的点子")

    def li(c, sc, T):
        taped = T >= tb(j, k_tape)
        with at_pop(c, LX, GY, sc):
            draw_li(c, LX, GY, s, "flat" if taped else "smile", rh=(LX + 80 * s, hy + 60 * s) if not taped else None)
            if taped:
                dt = T - tb(j, k_tape)
                with K.at(c, hx, hy + 20 * s, 0, C.slam_scale(dt)):
                    tape_mouth(c, 0, -20 * s, s)
        tb_ = tb(j, k_bulb)
        if T >= tb_:
            g = pop_scale(T - tb_)
            bx, by = hx + 200, hy - 230
            with K.at(c, bx, by, 0, g):
                c.drawCircle(0, 0, 60, K.paint("#FFF1A8"))
                c.drawPath(C.bulb_path(0, 0, 60), wb.marker(ORANGE, 8))
            sparkle(c, bx, by, T - tb_, YELLOW, 10, 80, 160)
            c.drawPath(P((hx + 50, hy - 60), (hx + 90, hy - 110), (bx - 50, by + 60)), wb.marker(GRAY, 4))
            if T < tb(j, k_n):
                K.text(c, "省事的点子", bx + 10, by + 130, 44, "hand", ORANGE, clamp01((T - tb_) / 0.3))
        return None
    ev(j, k_li, pop_fn(j, k_li, li), "wood_low", 0.6)
    b.hit(j, k_bulb, "ding", 0.8, "灯泡亮了")
    b.hit(j, k_tape, "tom", 0.8, "嘴上贴胶布")

    def passers(c, kk, T):
        t0 = tb(j, k_pass)
        if T < t0:
            return None
        for n in range(2):
            x, dy, _ = C.walk(T, t0 + n * 0.25, 2.6, cx + 600, cx + 220 + n * 170)
            if x > cx + 560:
                continue
            draw_person(c, x, GY + dy, 0.75, coat=BLUE_FILL if n else "#F3D3E0", line=BLUE if n else "#B04A78", back=True)
        return None
    ev(j, k_pass, passers, "wood_high", 0.6)


screen9()


# ================================================================ 屏 10：灰块混在忙碌的小人里；贴上名字；一块块擦掉
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    Y = cy - 120
    xs = [cx - 480 + i * 120 for i in range(9)]
    grays = [1, 3, 4, 7]
    names = ["等待", "搬运", "返工", "库存"]
    k_row = 0
    k_run = 1
    k_q = kq(j, wp(15, 1, 0.4), 2)
    k_mix = nx(j, wp(16, 1, 0.5), k_q)
    k_tags = [nx(j, wp(17, 0, 0.3), k_mix)]
    k_tags.append(nx(j, wp(17, 1, 0.3), k_tags[0]))
    k_er = nx(j, wp(17, 2, 0.6), k_tags[1])
    L.note(*names, "都在干活？", "去掉")
    b.path(j, k_row, k_row + 0.8, join(*[rect(x, Y, 110, 150, 10) for x in xs]), BLACK, 6, sfx="wood_high")

    def row(c, kk, T):
        er = tb(j, k_er)
        for i, x in enumerate(xs):
            g = i in grays
            gone = g and T >= er + grays.index(i) * 0.2
            if g:
                a = 1.0 if not gone else 1 - clamp01((T - er - grays.index(i) * 0.2) / 0.25)
                c.drawRect(skia.Rect.MakeXYWH(x - 50, Y - 70, 100, 140), K.paint("#9AA0A8", a))
                if gone and a <= 0:
                    c.drawPath(check(x, Y + 10, 26), wb.marker(GREEN, 8))
            sc = pop_scale(T - tb(j, k_run) - i * 0.05, 0.2)
            if sc > 0 and not (gone and T > er + grays.index(i) * 0.2 + 0.25):
                ph = T * 10 + i
                with K.at(c, x, Y + 50, 0, sc * 0.42):
                    C.line(c, (0, -200), (0, -100), BLACK, 9)
                    c.drawCircle(0, -235, 34, K.paint("#FFFFFF"))
                    c.drawCircle(0, -235, 34, wb.marker(BLACK, 8))
                    for sg in (1, -1):
                        C.line(c, (0, -100), (sg * 40 * math.sin(ph), 0), BLACK, 9)
                        C.line(c, (0, -170), (-sg * 50 * math.sin(ph), -120), BLACK, 9)
        # 名字标签贴上灰块
        for n, i in enumerate(grays):
            kt = k_tags[n // 2]
            g = C.slam_scale(T - tb(j, kt) - (n % 2) * 0.27)
            gone = T >= er + n * 0.2
            if g > 0 and not gone:
                with K.at(c, xs[i], Y + 135, -8 + n * 5, g):
                    w = K.text_w(names[n], 40, "hand") + 30
                    box(c, 0, 0, w, 60, NOTE_FILL, RED, 5, 8)
                    K.text(c, names[n], 0, 2, 40, "hand", RED)
        return None
    ev(j, k_run, row, "pop", 0.6)
    ev(j, k_q, L.pop_bubble("都在干活？", cx + 160, cy - 420, j, k_q, 60, BLACK, tail=1), "pop", 0.7)

    def mix(c, kk, T):
        t0 = tb(j, k_mix)
        if T < t0 or T >= tb(j, k_tags[0]):
            return None
        g = pop_scale(T - t0)
        for i in grays:
            with K.at(c, xs[i], Y - 110, 0, g):
                K.text(c, "？", 0, 0, 60, "hand", GRAY)
        return None
    ev(j, k_mix, mix, "wood_low", 0.6)
    for kt in k_tags:
        b.hit(j, kt, "wood_high", 0.75, "贴上名字")

    def li(c, sc, T):
        s, GY = 0.85, cy + 540
        t0 = tb(j, k_er)
        f = ease_in_out(clamp01((T - t0) / (0.25 + 0.2 * len(grays))))
        ex = lerp(cx + 330, xs[grays[-1]] + 30, 0.0) if T < t0 else lerp(xs[grays[0]], xs[grays[-1]], f)
        ey = Y + 70 + (10 * math.sin(T * 30) if 0 < f < 1 else 0)
        x = ex + 90 if T >= t0 else cx + 360
        hx, hy = head_of(x, GY, s)
        hand = (x - 60 * s, hy + 60 * s)
        top = (ex, ey + 30) if T >= t0 else (x - 40, hy - 120)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile" if T >= t0 else "flat", rh=hand)
            C.line(c, hand, top, "#A9773E", 9)
            with K.at(c, top[0], top[1] - 30, -10 if T >= t0 else 0):
                box(c, 0, 0, 130, 60, BLUE_FILL, BLUE, 6, 10)
                c.drawRect(skia.Rect.MakeXYWH(-65, 10, 130, 22), K.paint(BLUE))
        if T >= t0 + 0.5:
            K.text(c, "去掉", cx - 200, cy + 300, 90, "hand", GREEN, clamp01((T - t0 - 0.5) / 0.2))
        return None
    ev(j, 0, pop_fn(j, 0, li))
    b.hit(j, k_er, "shaker", 0.8, "灰块一块块擦掉")


screen10()


# ================================================================ 屏 11：五版方案，后四版只改了几个字
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    k_li = 0
    k_cnt = kq(j, wp(18, 2, 0.4), 1)
    k_v = nx(j, wp(19, 0, 0.5), k_cnt)
    k_v2 = k_v + 1
    k_mag = nx(j, wp(19, 2, 0.3), k_v2)
    k_tag = nx(j, wp(19, 2, 0.9), k_mag)
    VS = ["第一版", "第二版", "第三版", "第四版", "第五版"]
    L.note(*VS, "几件？", "只改了两个字")
    xs = [cx - 440 + i * 220 for i in range(5)]
    VY = cy - 180

    def li(c, sc, T):
        x, s = cx - 330, 0.85
        hx, hy = head_of(x, GY, s)
        count = T >= tb(j, k_cnt)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "flat", rh=(x + 100 * s, hy - 10 * s) if count else None)
            if count:
                n = 1 + int((T - tb(j, k_cnt)) * 3) % 5
                with K.at(c, x + 100 * s, hy - 40 * s, 0, 1):
                    c.drawCircle(0, 0, 36, K.paint(SKIN))
                    c.drawCircle(0, 0, 36, wb.marker(BLACK, 5))
                    for q in range(n):
                        C.line(c, (-28 + q * 14, -30), (-30 + q * 14, -70), BLACK, 7)
        return None
    ev(j, k_li, pop_fn(j, k_li, li), "wood_low", 0.6)
    ev(j, k_cnt, L.pop_bubble("几件？", cx - 120, cy + 170, j, k_cnt, 64, BLUE, tail=-1), "pop", 0.7)

    def vers(c, kk, T):
        for i, x in enumerate(xs):
            g = pop_scale(T - tb(j, k_v if i < 3 else k_v2) - (i % 3) * 0.12)
            if g <= 0:
                continue
            with K.at(c, x, VY, 0, g):
                doc_card(c, 0, 0, 190, 250, BLACK, 5)
                K.text(c, VS[i], 0, -160, 44, "hand", BLACK if i == 0 else GRAY)
                if i and T >= tb(j, k_mag) + i * 0.15:
                    c.drawOval(skia.Rect.MakeXYWH(-30, 10, 70, 40), wb.marker(RED, 6))
        tm = tb(j, k_mag)
        if T >= tm:
            f = clamp01((T - tm) / 0.9)
            mx = lerp(xs[1], xs[4], f)
            with K.at(c, mx + 40, VY + 60, 0, 1):
                c.drawCircle(0, 0, 60, K.paint("#FFFFFF", 0.4))
                c.drawCircle(0, 0, 60, wb.marker(BLACK, 8))
                C.line(c, (42, 42), (100, 100), BLACK, 14)
        return None
    ev(j, k_v, vers, "pop", 0.7)
    b.hit(j, k_v2, "pop", 0.6, "第四、五版")
    b.hit(j, k_mag, "rim", 0.75, "放大镜扫过")
    ev(j, k_tag, L.slam_text("只改了两个字", cx + 240, cy + 70, 72, RED, j, k_tag, rot=-3), "kick", 0.8)


screen11()


# ================================================================ 屏 12：沙发上挑电影，片单一页页翻，时钟走过半小时
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 470
    TVX, TVY = cx + 160, cy - 260
    k_tv = 0
    k_li = 1
    k_flip = kq(j, wp(20, 1, 0.1), 2)
    k_half = nx(j, wp(20, 1, 0.9), k_flip + 1)
    k_zz = nx(j, wp(20, 2, 0.6), k_half)
    L.note("半小时", "Zzz", "片单")
    b.path(j, k_tv, k_tv + 0.7, join(rect(TVX, TVY, 560, 340, 18), P((TVX - 80, TVY + 170), (TVX - 120, TVY + 220)),
                                     P((TVX + 80, TVY + 170), (TVX + 120, TVY + 220))), BLACK, 9, sfx="wood_low")
    COLS = ["#F28C8C", "#7FB2E5", "#8FD19E", "#F2C14E", "#C3A6E8"]

    def tv(c, kk, T):
        t0 = tb(j, k_flip)
        zz = T >= tb(j, k_zz)
        if T >= t0 and not zz:
            n = int((T - t0) * 3)
            off = ((T - t0) * 3) % 1
            for q in range(4):
                x = TVX - 200 + q * 130 - ease_out(off) * 130
                if TVX - 260 < x < TVX + 260:
                    c.drawRoundRect(skia.Rect.MakeXYWH(x - 50, TVY - 90, 100, 150), 8, 8, K.paint(COLS[(n + q) % 5]))
            K.text(c, "片单", TVX - 200, TVY + 120, 34, "sans_medium", GRAY)
        elif zz:
            c.drawRect(skia.Rect.MakeXYWH(TVX - 270, TVY - 160, 540, 320), K.paint("#3A3F48"))
        # 时钟
        x, y = cx - 360, cy - 330
        c.drawCircle(x, y, 80, K.paint("#FFFFFF"))
        c.drawPath(wb.clock(x, y, 80), wb.marker(BLACK, 6))
        m = 0 if T < t0 else 30 * clamp01((T - t0) / max(0.3, tb(j, k_half) - t0))
        c.drawPath(wb.hands_at(x, y, 80, 8, m), wb.marker(RED, 7))
        if m > 0:
            p = skia.Path()
            p.moveTo(x, y)
            p.arcTo(skia.Rect.MakeXYWH(x - 70, y - 70, 140, 140), -90, m * 6, False)
            p.close()
            c.drawPath(p, K.paint(RED, 0.25))
        if T >= tb(j, k_half):
            K.text(c, "半小时", x, y + 130, 54, "hand", RED, clamp01((T - tb(j, k_half)) / 0.2))
        return None
    ev(j, 0.5, tv)

    def li(c, sc, T):
        x, s = cx - 160, 0.8
        hx, hy = head_of(x, GY - 40, s)
        zz = T >= tb(j, k_zz)
        with at_pop(c, x, GY, sc):
            sofa = rect(x + 20, GY - 110, 520, 120, 30)
            c.drawPath(sofa, K.paint("#E8C7A8"))
            c.drawPath(sofa, wb.marker("#A9773E", 7))
            back = rect(x + 20, GY - 210, 520, 120, 30)
            c.drawPath(back, K.paint("#F0D8BF"))
            c.drawPath(back, wb.marker("#A9773E", 7))
            press = (math.sin(T * 9) > 0.6) and T >= tb(j, k_flip) and not zz
            rh = (x + 120 * s, hy + 100 * s - (10 if press else 0))
            c.save()
            if zz:
                c.translate(x, GY - 40)
                c.rotate(-12)
                c.translate(-x, -(GY - 40))
            draw_li(c, x, GY - 40, s, "flat", rh=rh)
            box(c, rh[0] + 10, rh[1] - 20, 30, 70, "#3A3F48", BLACK, 3, 8)
            c.restore()
            if zz:
                for n in range(3):
                    ph = ((T - tb(j, k_zz)) * 0.8 + n * 0.33) % 1
                    K.text(c, "Zzz"[n], hx + 70 + n * 40 + ph * 30, hy - 60 - n * 40 - ph * 40, 50 + n * 10, "hand", BLUE,
                           1 - ph)
        return None
    ev(j, k_li, pop_fn(j, k_li, li), "pop", 0.7)
    b.hit(j, k_flip, "wood_high", 0.7, "片单一页页翻")
    b.hit(j, k_flip + 1, "wood_high", 0.6, "接着翻")
    b.hit(j, k_half, "ding", 0.75, "时钟走过半小时")
    b.hit(j, k_zz, "tom", 0.7, "一部也没看，睡着了")


screen12()


# ================================================================ 屏 13：管不了的放一边，能管的一小堆；“三步”
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    k_div = 0
    k_no = kq(j, wp(21, 1, 0.3), 1)
    k_li = nx(j, wp(22, 0, 0.3), k_no)
    k_pile = nx(j, wp(22, 0, 0.9), k_li)
    k_3 = nx(j, wp(22, 1, 0.6), k_pile)
    L.note("管不了", "能管的", "会议中", "三步")
    b.path(j, k_div, k_div + 0.8, P((cx - 20, cy - 480), (cx - 20, cy + 380)), GRAY, 6, sfx="wood_low")

    def left(c, sc, T):
        with at_pop(c, cx - 290, cy - 100, sc):
            hourglass(c, cx - 410, cy - 200, 0.8, clamp01((T - tb(j, k_no)) / 6))
            box(c, cx - 170, cy - 220, 200, 90, "#FFFFFF", GRAY, 6, 10)
            K.text(c, "会议中", cx - 170, cy - 218, 44, "hand", GRAY)
            c.drawRect(skia.Rect.MakeXYWH(cx - 540, cy - 360, 500, 330), K.paint("#FCE6D0", 0.35))
            K.text(c, "管不了", cx - 290, cy + 40, 66, "hand", GRAY)
        return None
    ev(j, k_no, pop_fn(j, k_no, left), "pop", 0.65)

    def right(c, sc, T):
        x, s = cx + 170, 0.85
        hx, hy = head_of(x, GY, s)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile", rh=(x + 150 * s, hy + 120 * s))
            for i in range(3):
                g = pop_scale(T - tb(j, k_pile) - i * 0.12)
                if g > 0:
                    with K.at(c, x + 290, GY - 60 - i * 70, (i - 1) * 6, g):
                        box(c, 0, 0, 200, 64, NOTE_FILL, ORANGE, 5, 8)
            if T >= tb(j, k_pile):
                K.text(c, "能管的", x + 290, GY - 300, 56, "hand", ORANGE, clamp01((T - tb(j, k_pile)) / 0.2))
        return None
    ev(j, k_li, pop_fn(j, k_li, right), "pop", 0.7)
    b.hit(j, k_pile, "wood_high", 0.7, "能管的一小堆")
    stamp_ev(j, k_3, "三步", cx + 260, cy - 250, 130, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen13()


# ================================================================ 三步做法：右上角三个圆点
def steps_row(jj, active, k0=0):
    x0, y0 = R[jj][0] + 60, R[jj][1] - 470
    L.note("1", "2", "3")

    def fn(c, kk, T):
        for i in range(3):
            sc = pop_scale(T - tb(jj, 0) - i * 0.1)
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
    b.custom(jj, 0, 0.3, fn, sfx="wood_high", gain=0.6)
    if k0:
        b.hit(jj, k0, "clap", 0.7, f"第 {active + 1} 步亮起")


# ================================================================ 屏 14：下班前三分钟，红笔圈出一块灰
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 530
    steps_row(j, 0, 1)
    k_clk = kq(j, wp(23, 0, 0.6), 2)
    k_tl = nx(j, wp(23, 1, 0.4), k_clk)
    k_ring = nx(j, wp(23, 2, 0.6), k_tl)
    L.note("3分钟", "白忙")
    Y = cy - 100
    blocks = [(9, 10.5), (11, 12), (14, 16), (17, 17.5)]

    def clk(c, sc, T):
        x, y = cx - 380, cy - 400
        with at_pop(c, x, y, sc):
            c.drawCircle(x, y, 75, K.paint("#FFFFFF"))
            c.drawPath(wb.clock(x, y, 75), wb.marker(BLACK, 6))
            m = 57 + 3 * clamp01((T - tb(j, k_clk)) / 3)
            c.drawPath(wb.hands_at(x, y, 75, 17, m), wb.marker(RED, 7))
            K.text(c, "3分钟", x + 170, y, 54, "hand", RED)
        return None
    ev(j, k_clk, pop_fn(j, k_clk, clk), "pop", 0.7)

    def tl(c, kk, T):
        t0 = tb(j, k_tl)
        if T < t0:
            return None
        g = pop_scale(T - t0)
        xa, xb = cx - 500, cx + 500
        with K.at(c, cx, Y, 0, g):
            c.translate(-cx, -Y)
            box(c, cx, Y, 1000, 90, "#FFFFFF", BLACK, 6, 10)
            for h0, h1 in blocks:
                a_, z_ = xa + (h0 - 9) / 9 * 1000, xa + (h1 - 9) / 9 * 1000
                c.drawRect(skia.Rect.MakeXYWH(a_ + 4, Y - 38, z_ - a_ - 8, 76), K.paint("#9AA0A8"))
            K.text(c, "9点", xa, Y + 90, 36, "sans_medium", GRAY)
            K.text(c, "18点", xb, Y + 90, 36, "sans_medium", GRAY)
        tr = tb(j, k_ring)
        if T >= tr:
            f = clamp01((T - tr) / 0.5)
            a_, z_ = xa + (14 - 9) / 9 * 1000, xa + (16 - 9) / 9 * 1000
            ring = skia.Path()
            ring.addArc(skia.Rect.MakeXYWH(a_ - 40, Y - 90, z_ - a_ + 80, 180), -100, 359 * f)
            c.drawPath(ring, wb.marker(RED, 10))
            if f >= 1:
                K.text(c, "白忙", (a_ + z_) / 2, Y - 140, 64, "hand", RED)
        return None
    ev(j, k_tl, tl, "wood_high", 0.7)

    def li(c, sc, T):
        x, s = cx + 100, 0.85
        hx, hy = head_of(x, GY, s)
        tr = tb(j, k_ring)
        pen = (x - 60 * s + 20 * math.sin(T * 12), hy - 40 * s) if T >= tr and T < tr + 0.6 else (x + 90 * s, hy + 70 * s)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "flat" if T < tr else "smile", rh=pen)
            C.line(c, pen, (pen[0] + 30, pen[1] - 60), RED, 10)
        return None
    ev(j, 0, pop_fn(j, 0, li))
    b.hit(j, k_ring, "rim", 0.8, "红笔圈出一块灰")


screen14()


# ================================================================ 屏 15：八个格子只点亮一格，“明天只盯它”
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    steps_row(j, 1, 1)
    k_grid = kq(j, wp(24, 0, 0.5), 2)
    k_pick = nx(j, wp(24, 1, 0.5), k_grid)
    k_eye = nx(j, wp(24, 2, 0.5), k_pick)
    L.note(*WASTES, "明天只盯它")
    cells = [(cx - 390 + (i % 4) * 260, cy - 260 + (i // 4) * 170) for i in range(8)]
    PICK = 0

    def grid(c, kk, T):
        t0 = tb(j, k_grid)
        picked = T >= tb(j, k_pick)
        for i, (x, y) in enumerate(cells):
            g = pop_scale(T - t0 - i * 0.06, 0.22)
            if g <= 0:
                continue
            on = picked and i == PICK
            gg = g * (1 + 0.15 * pop_scale(T - tb(j, k_pick)) if on else g)
            a = 0.5 if picked and not on else 1.0
            with K.at(c, x, y, 0, gg):
                box(c, 0, 0, 240, 130, NOTE_FILL if on else "#FFFFFF", RED if on else GRAY, 8 if on else 5, 14, a)
                nm = WASTES[i]
                K.text(c, nm, 0, 2, 50 if len(nm) <= 4 else 40, "hand", RED if on else BLACK, a)
        if picked:
            sparkle(c, cells[PICK][0], cells[PICK][1], T - tb(j, k_pick), YELLOW, 10, 110, 190)
        return None
    ev(j, k_grid, grid, "pop", 0.7)
    b.hit(j, k_pick, "ding", 0.85, "只点亮一格")

    def li(c, sc, T):
        x, s = cx - 300, 0.85
        hx, hy = head_of(x, GY, s)
        eye = T >= tb(j, k_eye)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile" if eye else "flat",
                    rh=(x + 40 * s, hy - 10 * s) if eye else (x + 130 * s, hy - 80 * s),
                    lh=(x - 40 * s, hy - 10 * s) if eye else None)
            if eye:
                for sg in (-1, 1):
                    c.drawCircle(hx + sg * 34, hy - 4, 26, K.paint("#3A3F48"))
                    c.drawCircle(hx + sg * 34, hy - 4, 26, wb.marker(BLACK, 5))
                c.drawPath(wb.arrow((hx + 70, hy - 40), (cells[PICK][0] - 60, cells[PICK][1] + 90), 0.2, 30),
                           wb.marker(RED, 7, clamp01((T - tb(j, k_eye)) / 0.3)))
        return None
    ev(j, 0, pop_fn(j, 0, li))
    ev(j, k_eye, L.slam_text("明天只盯它", cx + 200, cy + 230, 80, RED, j, k_eye, rot=-3), "kick", 0.8)


screen15()


# ================================================================ 屏 16：撕掉胶布，写下来，举手说出来
def screen16(j=16):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    steps_row(j, 2, 1)
    LX, s = cx - 220, 0.95
    hx, hy = head_of(LX, GY, s)
    k_rip = kq(j, wp(25, 0, 0.8), 2)
    k_wr = nx(j, wp(25, 1, 0.2), k_rip)
    k_say = nx(j, wp(25, 1, 0.75), k_wr)
    L.note("我有个点子", "点子")

    def li(c, sc, T):
        tr, tw, ts = tb(j, k_rip), tb(j, k_wr), tb(j, k_say)
        with at_pop(c, LX, GY, sc):
            if T < tr:
                draw_li(c, LX, GY, s, "flat", rh=(hx + 40 * s, hy + 20 * s))
                tape_mouth(c, hx, hy, s)
            elif T < ts:
                f = clamp01((T - tr) / 0.4)
                draw_li(c, LX, GY, s, "smile", rh=(LX + 150 * s, hy + 150 * s + 8 * math.sin(T * 18) * (T >= tw)))
                if f < 1:
                    with K.at(c, hx + 40 + 200 * f, hy + 20 * s - 80 * f, 60 * f):
                        tape_mouth(c, 0, -20 * s, s, 1 - f, 0)
            else:
                draw_li(c, LX, GY, s, "smile", rh=(LX + 60 * s, hy - 120 * s))
        bx, by = hx - 10, hy - 220
        c.drawCircle(bx, by, 52, K.paint("#FFF1A8"))
        c.drawPath(C.bulb_path(bx, by, 52), wb.marker(ORANGE, 7))
        sparkle(c, bx, by, T - tr, YELLOW, 10, 70, 150)
        if T >= tw:
            g = pop_scale(T - tw)
            with K.at(c, LX + 260, GY - 170, -5, g):
                box(c, 0, 0, 220, 200, NOTE_FILL, ORANGE, 6, 8)
                K.text(c, "点子", 0, -50, 50, "hand", ORANGE)
                f = clamp01((T - tw) / 0.8)
                for r in range(2):
                    C.line(c, (-70, 10 + r * 45), (-70 + 140 * clamp01(f * 2 - r), 10 + r * 45), BLUE, 6)
        return None
    ev(j, 0, pop_fn(j, 0, li), "wood_low", 0.6)
    b.hit(j, k_rip, "tom", 0.8, "撕掉胶布")
    b.hit(j, k_wr, "wood_high", 0.7, "写在便签上")
    ev(j, k_say, L.pop_bubble("我有个点子", cx + 120, cy - 330, j, k_say, 62, BLACK, tail=-1), "pop", 0.8)

    def boss(c, sc, T):
        x, s2 = cx + 380, 0.85
        nod = 8 * math.sin((T - tb(j, k_say)) * 10) * math.exp(-(T - tb(j, k_say)) * 1.5) if T > tb(j, k_say) else 0
        with at_pop(c, x, GY, sc):
            draw_boss(c, x, GY, s2, mood="smile" if T > tb(j, k_say) + 0.3 else "flat", head_dy=nod)
        return None
    ev(j, k_wr, pop_fn(j, k_wr, boss))


screen16()


# ================================================================ 屏 17：晚上厨房，小李炒菜，锅里冒热气
def screen17(j=17):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    k_k = 0
    k_li = 1
    k_moon = kq(j, wp(26, 1, 0.3), 2)
    k_toss = nx(j, wp(26, 2, 0.3), k_moon)
    k_dish = nx(j, wp(26, 2, 0.9), k_toss)
    L.note("做顿饭")
    SX = cx + 260
    b.path(j, k_k, k_k + 0.8, join(rect(SX, GY - 160, 360, 320, 12), P((SX - 180, GY - 320), (SX + 180, GY - 320)),
                                   rect(cx - 330, cy - 330, 300, 240, 10), P((cx - 330, cy - 450), (cx - 330, cy - 210)),
                                   P((cx - 480, cy - 330), (cx - 180, cy - 330))), BLACK, 8, sfx="wood_low")

    def scene_(c, kk, T):
        t0 = tb(j, k_moon)
        if T >= t0:
            c.drawRect(skia.Rect.MakeXYWH(cx - 476, cy - 446, 292, 232), K.paint("#3A4766", clamp01((T - t0) / 0.3)))
            C.line(c, (cx - 330, cy - 450), (cx - 330, cy - 210), BLACK, 8)
            C.line(c, (cx - 480, cy - 330), (cx - 180, cy - 330), BLACK, 8)
            g = pop_scale(T - t0)
            with K.at(c, cx - 400, cy - 390, 0, g):
                c.drawCircle(0, 0, 40, K.paint(YELLOW))
                c.drawCircle(16, -10, 36, K.paint("#3A4766"))
            for i, (dx, dy) in enumerate(((-230, -420), (-270, -280), (-410, -260))):
                K.text(c, "★", cx + dx, cy + dy, 30, "black", YELLOW, clamp01((T - t0 - i * 0.1) / 0.2))
        return None
    b.custom(j, k_moon, k_moon + 0.3, scene_, sfx="pop", gain=0.6)

    def cook(c, kk, T):
        sc = pop_scale(T - tb(j, k_li))
        if sc <= 0:
            return None
        x, s = cx - 140, 0.9
        hx, hy = head_of(x, GY, s)
        tt = tb(j, k_toss)
        toss = 0.0
        if T >= tt:
            ph = ((T - tt) * 1.9) % 1
            toss = math.sin(ph * math.pi) if ph < 0.5 else 0
        wx, wy = SX, GY - 360 - 30 * toss
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile", rh=(wx - 210, wy + 8))
            # 炉火
            for i in range(3):
                fl = 20 + 8 * math.sin(T * 14 + i)
                c.drawPath(P((wx - 40 + i * 40, GY - 322), (wx - 30 + i * 40, GY - 322 - fl), (wx - 20 + i * 40, GY - 322),
                             close=True), K.paint(ORANGE))
            wok = skia.Path()
            wok.addArc(skia.Rect.MakeXYWH(wx - 110, wy - 70, 220, 120), 0, 180)
            wok.close()
            c.drawPath(wok, K.paint("#3A3F48"))
            C.line(c, (wx - 110, wy - 10), (wx - 215, wy + 8), "#A9773E", 12)
            for i in range(4):
                c.drawCircle(wx - 50 + i * 34, wy - 20 - 120 * toss * (0.6 + 0.2 * (i % 2)), 14,
                             K.paint(GREEN if i % 2 else ORANGE))
            for n in range(3):
                ph = (T * 0.9 + n * 0.33) % 1
                p = P((wx - 60 + n * 60, wy - 80 - ph * 160), (wx - 40 + n * 60, wy - 120 - ph * 160),
                      (wx - 60 + n * 60, wy - 160 - ph * 160))
                c.drawPath(p, wb.marker(GRAY, 6, 1 - ph))
        td = tb(j, k_dish)
        if T >= td:
            g = pop_scale(T - td)
            with K.at(c, cx - 380, GY - 140, 0, g):
                c.drawOval(skia.Rect.MakeXYWH(-130, -30, 260, 70), K.paint("#FFFFFF"))
                c.drawOval(skia.Rect.MakeXYWH(-130, -30, 260, 70), wb.marker(BLUE, 6))
                for i in range(5):
                    c.drawCircle(-60 + i * 30, -10 - (i % 2) * 14, 16, K.paint(GREEN if i % 2 else ORANGE))
                K.text(c, "做顿饭", 0, -140, 64, "hand", RED)
        return None
    b.custom(j, k_li, k_li + 0.3, cook, sfx="pop", gain=0.6)
    b.hit(j, k_toss, "wood_high", 0.75, "颠锅")
    b.hit(j, k_dish, "ding", 0.8, "一盘菜端出来")


screen17()


# ================================================================ 屏 18：评论框写着八种浪费；刀刃闪光，力气小人跳上去；下一讲预告
def screen18(j=18):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z))
    k_cmt = 0
    k_chips = kq(j, wp(27, 1, 0.3), 1)
    k_wave = nx(j, wp(28, 1, 0.3), k_chips)
    k_knife = nx(j, wp(29, 1, 0.3), k_wave)
    k_jump = nx(j, wp(29, 3, 0.5), k_knife)
    k_next = nx(j, wp(30, 0, 0.3), k_jump)
    b.move(j, k_knife, (cx, cy + 420, Z), 1.1)
    L.note("你最大的白忙？", "下一讲", "找个文件", "为什么要翻十分钟？", "力气", "刀刃")
    BY = cy - 300

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 60, BY, 0, sc):
            bubble_box(c, 0, 0, 900, 380, -1)
            K.text(c, "你最大的白忙？", 0, -120, 64, "hand", RED)
            for i, nm in enumerate(WASTES):
                g = pop_scale(T - tb(j, k_chips) - i * 0.09, 0.22)
                if g <= 0:
                    continue
                x, y = -330 + (i % 4) * 220, -10 + (i // 4) * 95
                with K.at(c, x, y, 0, g):
                    w = K.text_w(nm, 38, "hand") + 34
                    K.rr(c, 0, 0, w, 66, 33, FT.hexc(FT.mix(BLUE_FILL, "#FFFFFF", 0.2)))
                    K.text(c, nm, 0, 2, 38, "hand", BLUE)
        return None
    ev(j, k_cmt, cmt, "pop", 0.7)
    b.hit(j, k_chips, "wood_high", 0.6, "八种浪费的名字一个个冒出来")

    def li(c, kk, T):
        sc = pop_scale(T - tb(j, k_wave))
        if sc <= 0:
            return None
        x, s, GY = cx - 330, 0.7, cy + 200
        hx, hy = head_of(x, GY, s)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile", rh=(x + 80 * s + math.sin(T * 8) * 30 * s, hy - 70 * s))
        return None
    b.custom(j, k_wave, k_wave + 0.3, li, sfx="pop", gain=0.6)

    KY = cy + 330

    def knife(c, kk, T):
        t0 = tb(j, k_knife)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        with K.at(c, cx + 40, KY, -6, sc):
            blade = P((-360, -40), (240, -60), (330, 10), (-360, 30), close=True)
            c.drawPath(blade, K.paint("#E4E8EE"))
            c.drawPath(blade, wb.marker(BLACK, 7))
            C.line(c, (-340, 24), (320, 6), BLUE, 6)
            box(c, -470, -5, 240, 80, "#A9773E", "#7A4A1E", 6, 20)
            K.text(c, "刀刃", 140, 70, 46, "hand", BLUE)
            tj = tb(j, k_jump)
            if T >= tj:
                f = clamp01((T - tj) / 0.6)
                gx = lerp(-200, 80, f)
                gy = lerp(140, -110, f) - math.sin(f * math.pi) * 160
                with K.at(c, gx, gy, 0, 1):
                    c.drawCircle(0, -40, 28, K.paint("#FFFFFF"))
                    c.drawCircle(0, -40, 28, wb.marker(RED, 6))
                    C.line(c, (0, -12), (0, 40), RED, 8)
                    C.line(c, (0, 0), (-40, -30), RED, 8)
                    C.line(c, (0, 0), (40, -30), RED, 8)
                    C.line(c, (0, 40), (-24, 80), RED, 8)
                    C.line(c, (0, 40), (24, 80), RED, 8)
                if f >= 1:
                    K.text(c, "力气", 80, -260, 52, "hand", RED)
            sparkle(c, cx * 0 + 300, -40, T - tj, YELLOW, 10, 40, 130)
        return None
    ev(j, k_knife, knife, "wood_high", 0.7)
    b.hit(j, k_jump, "ding", 0.85, "力气小人跳上刀刃，刀刃一闪")

    def nxt(c, kk, T):
        t0 = tb(j, k_next)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        x, y = cx + 20, cy + 650
        with K.at(c, x, y, -2, sc):
            box(c, 0, 0, 980, 230, "#FFFFFF", BLACK, 7, 18)
            K.rr(c, -380, -70, 170, 60, 30, RED)
            K.text(c, "下一讲", -380, -68, 38, "hand", "#FFFFFF")
            K.text(c, "找个文件", -110, -60, 58, "hand", BLACK)
            K.text(c, "为什么要翻十分钟？", -60, 40, 58, "hand", BLACK)
            with K.at(c, 360, 0, 0, 1):
                box(c, 0, 0, 200, 140, "#FFFFFF", BLACK, 5, 10)
                for i in range(15):
                    c.drawRect(skia.Rect.MakeXYWH(-85 + (i % 5) * 34, -55 + (i // 5) * 38, 24, 26),
                               K.paint(["#F2C14E", "#7FB2E5", "#F28C8C"][i % 3]))
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen18()

# ================================================================ 收尾
L.finish(cover_shot=9, square_shot=9, notes=NOTES)
L.export(globals())
