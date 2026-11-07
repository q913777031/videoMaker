"""《丰田模式》12 整理整顿：找个文件，为什么要翻十分钟？（白板手绘 + AI 旁白，竖屏 2:3）

复刻实验：同一张电脑桌面，找同一份合同，计时两次。第 2–3 屏和第 8–9 屏右上角挂着“实验”秒表：
第一次在乱桌面上找（drop 时秒表砸到“十分钟”），中间照丰田车间的头两步（整理、整顿）收拾一遍，第二次“十秒”。
- 0–3 秒：电脑桌面图标逐拍堆满，弹出“最终版二”，“找不到”砸下；
- 打工人日常：小李在桌面、聊天、邮箱三个窗口之间来回点，领导抱着胳膊、手表在走；
- 实验：桌面放大成白板，“合同”藏在里面；第一次：一百多个图标，三个“最终版”逐个亮，秒表到十分钟（drop）；
- 书中做法：车间五级台阶，前两级“整理”“整顿”亮起；整理（留下 / 拿走）；整顿（工具墙画好轮廓，少一把红圈一闪）；
  后三级（打扫 / 定规矩 / 一直保持），“大扫除”打叉，地上冒出问题小红点；
- 第二次：收拾后的桌面，十秒；为什么：两个秒表对比，顾客钱包合上，东西各回各家；
- 说回我们：出门找钥匙、地铁走了 / 聊天记录往上划 / 四十个标签页 / 等闲下来的日历，“三步”；三步做法；热咖啡；评论区与下一讲。
车间员工戴安全帽（common.draw_worker），领导 common.draw_boss，小李 common.draw_li；顾客、同事用本模块的小人。
文案见 fengtian/PLAN.md「### 12 整理整顿」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import core
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, draw_worker, pop_scale,
                             rest_hands)
from whiteboard import engine as wb
from whiteboard.engine import P, check, circle, cross, join, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "小实验", 2),
    ([3, 4], "小实验 · 第一次", 3),
    ([5, 6], "丰田模式 · 书中做法", 4),
    ([7], "整理 · 示意", 5),
    ([8, 9], "整顿 · 示意", 6),
    ([10, 11], "书中观点", 7),
    ([12], "小实验 · 第二次", 8),
    ([13, 14, 15], "为什么差这么多", 9),
    ([16, 17], "说回我们自己", 10),
    ([18], "说回我们自己", 11),
    ([19], "说回我们自己", 12),
    ([20, 21], "说回我们自己", 13),
    ([22], "做法一 · 示意", 14),
    ([23], "做法二 · 示意", 15),
    ([24], "做法三 · 示意", 16),
    ([25], "省下的十分钟", 17),
    ([26, 27, 28, 29], "评论区见", 18),
]

THEME = FT.get("12")          # 本讲样式（fengtian/theme.py）：方眼本、开场 desktop、转场 arc
L = C.Lesson("12", SCREENS, drop_screen=3, board_size=(5000, 12600), theme=THEME)
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(17)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 7 一章里的五 S（整理、整顿、清扫、清洁、素养）；书中提醒五 S 不能当成大扫除，要让问题露出来。"
    "工具墙画轮廓是常见做法。",
    "十分钟、十秒、一百多个图标均为示意；小李、领导、同事为虚构人物。",
]

GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL = "#8A8F99", "#D9DCE1", "#D3EDDC", "#F6C3BE", "#D5E3F7"
WOOD, NOTE_FILL, SKIN = "#E3C9A0", "#FFF1A8", "#FBE3CF"


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



ICON_COLS = ["#F2C14E", "#7FB2E5", "#F28C8C", "#8FD19E"]
STEPS5 = ["整理", "整顿", "打扫", "定规矩", "一直保持"]


def monitor(c, x, y, w, h, alpha=1.0):
    """显示器：(x, y) 为屏幕中心。"""
    box(c, x, y, w, h, "#FFFFFF", BLACK, 9, 20, alpha)
    C.line(c, (x, y + h / 2), (x, y + h / 2 + 60), BLACK, 10, alpha)
    C.line(c, (x - 140, y + h / 2 + 64), (x + 140, y + h / 2 + 64), BLACK, 10, alpha)


def icon(c, x, y, col, s=1.0, alpha=1.0, name=None, size=30, name_col=BLACK):
    with K.at(c, x, y, 0, s):
        c.drawRoundRect(skia.Rect.MakeXYWH(-30, -36, 60, 54), 8, 8, K.paint(col, alpha))
        c.drawRoundRect(skia.Rect.MakeXYWH(-30, -36, 60, 54), 8, 8, wb.marker(BLACK, 4, alpha))
        if name:
            K.text(c, name, 0, 44, size, "hand", name_col, alpha)
        else:
            C.line(c, (-24, 34), (24, 34), GRAY, 5, alpha)


def folder_icon(c, x, y, s=1.0, name=None, fill="#F6D98B", line="#A9842A", size=40, alpha=1.0):
    with K.at(c, x, y, 0, s):
        body = P((-70, -40), (-70, 50), (70, 50), (70, -40), (8, -40), (-4, -58), (-70, -58), close=True)
        c.drawPath(body, K.paint(fill, alpha))
        c.drawPath(body, wb.marker(line, 6, alpha))
        if name:
            K.text(c, name, 0, 90, size, "hand", BLACK, alpha)


def stopwatch(c, x, y, r, frac, label=None, color=RED, label_size=56):
    """秒表：frac 为指针转过的圈数比例；label 写在表盘下方。"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 22, y - r - 46, 44, 30), 8, 8, K.paint(BLACK))
    C.line(c, (x + r * 0.72, y - r * 0.72), (x + r * 0.9, y - r * 0.9), BLACK, 12)
    c.drawCircle(x, y, r, K.paint("#FFFFFF"))
    if frac > 0:
        p = skia.Path()
        p.moveTo(x, y)
        p.arcTo(skia.Rect.MakeXYWH(x - r * 0.86, y - r * 0.86, r * 1.72, r * 1.72), -90, min(359.0, 360 * frac), False)
        p.close()
        c.drawPath(p, K.paint(color, 0.22))
    c.drawPath(wb.clock(x, y, r), wb.marker(BLACK, 7))
    a = math.radians(-90 + 360 * frac)
    C.line(c, (x, y), (x + r * 0.8 * math.cos(a), y + r * 0.8 * math.sin(a)), color, 8)
    c.drawCircle(x, y, 9, K.paint(BLACK))
    if label:
        K.text(c, label, x, y + r + 60, label_size, "hand", color)


def tool_shape(kind, x, y, s=1.0) -> skia.Path:
    """工具轮廓：wrench 扳手、hammer 锤子、driver 螺丝刀、pliers 钳子。(x, y) 为中心。"""
    if kind == "wrench":
        return join(rect(x, y + 40 * s, 30 * s, 180 * s, 12 * s), circle(x, y - 80 * s, 42 * s))
    if kind == "hammer":
        return join(rect(x, y + 30 * s, 26 * s, 200 * s, 10 * s), rect(x, y - 90 * s, 130 * s, 50 * s, 10 * s))
    if kind == "driver":
        return join(rect(x, y - 60 * s, 46 * s, 100 * s, 16 * s), rect(x, y + 60 * s, 14 * s, 140 * s, 4 * s))
    return join(P((x - 40 * s, y - 100 * s), (x, y), (x - 50 * s, y + 110 * s)),
                P((x + 40 * s, y - 100 * s), (x, y), (x + 50 * s, y + 110 * s)), circle(x, y, 12 * s))


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


def stairs(c, x0, y0, lit, dt_lit=None, w=200, h=90, labels=True):
    """五级台阶：(x0, y0) 为最下一级左下角；lit 为亮起的级数集合；dt_lit {级: 亮起后秒数} 用来弹一下。"""
    for i in range(5):
        x, y = x0 + i * w, y0 - (i + 1) * h
        on = i in lit
        g = 1.0
        if dt_lit and i in dt_lit:
            g = 1 + 0.15 * math.exp(-max(0, dt_lit[i]) * 6) if dt_lit[i] >= 0 else 1.0
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, (i + 1) * h), K.paint(NOTE_FILL if on else "#F1F2F4"))
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, (i + 1) * h), wb.marker(BLACK, 6))
        if labels:
            nm = STEPS5[i]
            with K.at(c, x + w / 2, y + 45, 0, g):
                K.text(c, nm, 0, 0, 46 if len(nm) <= 3 else 36, "hand", RED if on else GRAY)


L.note(*STEPS5)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：小李在三个窗口之间来回点，领导抱着胳膊，手表在走
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    k_win = 0
    k_li = 1
    k_boss = kq(j, wp(1, 0, 0.3), 2)
    k_watch = nx(j, wp(1, 0, 0.9), k_boss)
    k_sweat = nx(j, wp(1, 1, 0.5), k_watch)
    W3 = [(cx - 380, cy - 330, "桌面"), (cx - 40, cy - 380, "聊天"), (cx + 290, cy - 330, "邮箱")]
    L.note(*[w[2] for w in W3])

    def wins(c, kk, T):
        for i, (x, y, s_) in enumerate(W3):
            g = pop_scale(T - tb(j, k_win) - i * 0.15)
            if g <= 0:
                continue
            u = max(0.0, T - tb(j, k_li)) * 2.2
            act = int(u) % 3 == i and T >= tb(j, k_li)
            with K.at(c, x, y, (i - 1) * 4, g * (1.08 if act else 1.0)):
                box(c, 0, 0, 280, 200, "#FFFFFF", RED if act else BLACK, 8 if act else 6, 14)
                c.drawRect(skia.Rect.MakeXYWH(-140, -100, 280, 40), K.paint(BLUE_FILL))
                K.text(c, s_, 0, -78, 32, "sans_medium", BLACK)
                for r in range(3):
                    C.line(c, (-100, -20 + r * 40), (100 - r * 30, -20 + r * 40), GRAY, 5)
        if T >= tb(j, k_li):
            u = (T - tb(j, k_li)) * 2.2
            i = int(u) % 3
            f = ease_in_out(clamp01((u - int(u)) * 2.5))
            a, z = W3[(i - 1) % 3], W3[i]
            cursor(c, lerp(a[0], z[0], f) + 30, lerp(a[1], z[1], f) + 20)
        return None
    ev(j, k_win, wins, "pop", 0.6)

    def li(c, sc, T):
        x, s = cx - 220, 0.85
        hx, hy = head_of(x, GY, s)
        u = (T - tb(j, k_li)) * 2.2
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "sad" if T >= tb(j, k_sweat) else "flat",
                    rh=(x + 110 * s, hy + 120 * s + 15 * math.sin(u * math.pi * 2)))
            if T >= tb(j, k_sweat):
                for n in range(3):
                    ph = ((T - tb(j, k_sweat)) * 1.6 + n * 0.33) % 1
                    c.drawCircle(hx + (-70 if n % 2 else 70), hy - 20 + ph * 80, 10, K.paint(BLUE, 1 - ph))
        return None
    ev(j, k_li, pop_fn(j, k_li, li), "shaker", 0.6)

    def boss(c, sc, T):
        x, s = cx + 300, 0.95
        hx, hy = head_of(x, GY, s)
        arms = (x - 30 * s, hy + 150 * s), (x + 30 * s, hy + 150 * s)
        tap = 10 * max(0, math.sin((T - tb(j, k_boss)) * 8)) if T >= tb(j, k_watch) else 0
        with at_pop(c, x, GY, sc):
            draw_boss(c, x, GY, s, lh=arms[1], rh=arms[0], mood="flat")
            C.line(c, (x - 40 * s, hy + 150 * s), (x + 40 * s, hy + 150 * s), "#3D4A63", 14)
            C.line(c, (x + 40 * s, GY - 30 + 0), (x + 70 * s, GY - 30 - tap), BLACK, 6)
        if T >= tb(j, k_watch):
            g = pop_scale(T - tb(j, k_watch))
            wx, wy = x + 150, hy - 60
            with K.at(c, wx, wy, 0, g):
                c.drawCircle(0, 0, 62, K.paint("#FFFFFF"))
                c.drawPath(wb.clock(0, 0, 62), wb.marker(BLACK, 6))
                a = math.radians(-90 + (T - tb(j, k_watch)) * 240)
                C.line(c, (0, 0), (50 * math.cos(a), 50 * math.sin(a)), RED, 6)
        return None
    ev(j, k_boss, pop_fn(j, k_boss, boss), "pop", 0.7)
    b.hit(j, k_watch, "wood_high", 0.7, "手表在走")
    b.hit(j, k_sweat, "tom", 0.7, "越找越慌")


screen1()


# ================================================================ 屏 2：桌面放大成白板，“合同”藏在里面；小李拿着秒表
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    MX, MY = cx + 60, cy - 170
    k_tag = kq(j, wp(2, 0, 0.3), 1)
    k_li = nx(j, wp(2, 1, 0.3), k_tag)
    k_hid = nx(j, wp(2, 2, 0.4), k_li)
    k_sw = nx(j, wp(2, 2, 0.95), k_hid)
    L.note("实验", "合同", "同一张桌面")
    b.path(j, 0, 0.8, join(rect(MX, MY, 800, 520, 20), P((MX, MY + 260), (MX, MY + 320)), P((MX - 140, MY + 324),
                                                                                           (MX + 140, MY + 324))),
           BLACK, 9, sfx="wood_low")
    cells = [(MX - 330 + (i % 8) * 94, MY - 190 + (i // 8) * 100) for i in range(32)]
    HID = 19

    def desk_(c, kk, T):
        for i, (x, y) in enumerate(cells):
            g = pop_scale(T - tb(j, 0) - 0.4 - (i % 8) * 0.04, 0.2)
            if g <= 0:
                continue
            if i == HID and T >= tb(j, k_hid):
                icon(c, x, y, "#FFFFFF", 0.9 * (1 + 0.2 * pop_scale(T - tb(j, k_hid))), name="合同", size=26, name_col=RED)
                ring = skia.Path()
                ring.addOval(skia.Rect.MakeXYWH(x - 60, y - 60, 120, 140))
                c.drawPath(ring, wb.marker(RED, 7))
            else:
                icon(c, x, y, ICON_COLS[(i * 7) % 4], 0.9 * g)
        return None
    b.custom(j, 0.4, 0.7, desk_)

    def tag(c, sc, T):
        with at_pop(c, cx - 400, cy - 520, sc):
            K.rr(c, cx - 400, cy - 520, 170, 80, 16, RED)
            K.text(c, "实验", cx - 400, cy - 518, 52, "hand", "#FFFFFF")
        K.text(c, "同一张桌面", cx + 150, cy - 520, 50, "hand", GRAY, clamp01(sc))
        return None
    ev(j, k_tag, pop_fn(j, k_tag, tag), "rim", 0.7)
    b.hit(j, k_hid, "ding", 0.8, "合同藏在里面")

    def li(c, sc, T):
        x, s = cx - 330, 0.85
        hx, hy = head_of(x, GY, s)
        hold = T >= tb(j, k_sw)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile", rh=(x + 110 * s, hy + 30 * s) if hold else None)
            if hold:
                g = pop_scale(T - tb(j, k_sw))
                with K.at(c, x + 110 * s + 50, hy + 30 * s - 50, 0, g):
                    stopwatch(c, 0, 0, 60, 0.0)
        return None
    ev(j, k_li, pop_fn(j, k_li, li), "pop", 0.7)
    b.hit(j, k_sw, "wood_high", 0.75, "按下秒表")


screen2()


# ================================================================ 屏 3：第一次——一百多个图标挤满屏，三个“最终版”逐个亮；drop 秒表砸到十分钟
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    KD = L.drop_k()
    b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
    GY = cy + 540
    MX, MY = cx + 60, cy - 220
    k_fill = kq(j, wp(3, 1, 0.2), 1)
    k_fill2 = nx(j, wp(3, 1, 0.9), k_fill)
    k_n = [nx(j, wp(3, 2, 0.5), k_fill2)]
    k_n.append(nx(j, wp(3, 3, 0.5), k_n[0]))
    k_n.append(nx(j, wp(3, 4, 0.5), k_n[1]))
    k_open = min(nx(j, wp(4, 0, 0.4), k_n[2]), KD - 1)
    NAMES = ["最终版", "最终版二", "真的最终版"]
    L.note(*NAMES, "十分钟", "×100")
    b.path(j, 0, 0.8, join(rect(MX, MY, 820, 500, 20), P((MX, MY + 250), (MX, MY + 310)),
                           P((MX - 140, MY + 314), (MX + 140, MY + 314))), BLACK, 9, sfx="wood_low")
    cells = [(MX - 360 + (i % 12) * 65, MY - 200 + (i // 12) * 66) for i in range(84)]
    order = sorted(range(len(cells)), key=lambda i: (i * 7919) % 101)
    SP = {order[5]: 0, order[30]: 1, order[60]: 2}

    def fill(c, kk, T):
        n = 0
        if T >= tb(j, k_fill):
            n = 40
        if T >= tb(j, k_fill2):
            n = 84
        for m, i in enumerate(order[:n]):
            k_ = k_fill if m < 40 else k_fill2
            g = pop_scale(T - tb(j, k_) - (m % 10) * 0.03, 0.2)
            if g <= 0:
                continue
            x, y = cells[i]
            icon(c, x, y, ICON_COLS[i % 4], 0.62 * g)
        for i, q in SP.items():                 # 三个“最终版”逐个亮
            t0 = tb(j, k_n[q])
            if T < t0:
                continue
            x, y = cells[i]
            g = pop_scale(T - t0)
            with K.at(c, x, y - 10, 0, g):
                w = K.text_w(NAMES[q], 40, "hand") + 30
                box(c, 0, 0, w, 64, NOTE_FILL, RED, 5, 10)
                K.text(c, NAMES[q], 0, 2, 40, "hand", RED)
        to = tb(j, k_open)
        if T >= to:
            for q in range(7):
                g = pop_scale(T - to - q * 0.12, 0.2)
                if g > 0:
                    with K.at(c, MX - 250 + q * 70, MY - 120 + q * 40, 0, g):
                        box(c, 0, 0, 260, 170, "#FFFFFF", GRAY, 5, 10)
                        c.drawRect(skia.Rect.MakeXYWH(-130, -85, 260, 30), K.paint(GRAY_FILL))
            cursor(c, MX + 230 + 20 * math.sin(T * 9), MY + 140)
        return None
    ev(j, k_fill, fill, "pop", 0.7)
    b.hit(j, k_fill2, "wood_high", 0.7, "图标挤满屏")
    for q, k_ in enumerate(k_n):
        b.hit(j, k_, "pop" if q < 2 else "rim", 0.75, f"文件名亮：{NAMES[q]}")
    b.hit(j, k_open, "shaker", 0.7, "点开七八个")

    def sw(c, kk, T):
        x, y = cx - 400, cy + 330
        t0 = tb(j, k_fill)
        frac = clamp01((T - t0) / max(0.3, tb(j, KD) - t0)) * 0.999
        lab = "十分钟" if T >= tb(j, KD) else None
        g = C.slam_scale(T - tb(j, KD)) if T >= tb(j, KD) else 1.0
        with K.at(c, x, y, 0, g):
            stopwatch(c, 0, 0, 100, frac, lab, RED, 70)
        return None
    ev(j, 0, sw, None)

    def li(c, sc, T):
        x, s = cx + 330, 0.85
        hx, hy = head_of(x, GY, s)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "sad" if T >= tb(j, k_open) else "flat",
                    rh=(x - 90 * s, hy + 100 * s + 10 * math.sin(T * 14)))
            if T >= tb(j, k_open):
                for n in range(3):
                    ph = (T * 1.6 + n * 0.33) % 1
                    c.drawCircle(hx + (-70 if n % 2 else 70), hy - 20 + ph * 80, 10, K.paint(BLUE, 1 - ph))
        return None
    ev(j, 1, pop_fn(j, 1, li))
    b.hit(j, KD, "kick", 0.95, "drop：秒表砸到十分钟")


screen3()


# ================================================================ 屏 4：车间五级台阶，前两级“整理”“整顿”亮起
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 480
    X0 = cx - 520
    k_li = kq(j, wp(5, 1, 0.3), 1)
    k_broom = nx(j, wp(5, 2, 0.4), k_li)
    k_st = nx(j, wp(6, 0, 0.4), k_broom)
    k_5 = nx(j, wp(6, 1, 0.5), k_st)
    k_a = nx(j, wp(6, 2, 0.45), k_5)
    k_b = cap(j, k_a + 1)
    L.note("五个步骤", "车间")

    def st(c, kk, T):
        t0 = tb(j, k_st)
        if T < t0:
            return None
        g = ease_out(clamp01((T - t0) / 0.4))
        lit = {i for i, k_ in ((0, k_a), (1, k_b)) if T >= tb(j, k_)}
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(X0 - 10, GY - 520, X0 - 10 + 1040 * g, GY + 10))
        stairs(c, X0, GY, lit, {0: T - tb(j, k_a), 1: T - tb(j, k_b)}, labels=T >= tb(j, k_a) - 0.01 or True)
        c.restore()
        if T >= tb(j, k_5):
            gg = pop_scale(T - tb(j, k_5))
            with K.at(c, cx + 230, cy - 400, -4, gg):
                K.rr(c, 0, 0, 320, 90, 20, BLUE)
                K.text(c, "五个步骤", 0, 2, 54, "hand", "#FFFFFF")
        return None
    ev(j, k_st, st, "wood_high", 0.7)
    b.hit(j, k_5, "pop", 0.7, "五个步骤")
    b.hit(j, k_a, "rim", 0.8, "整理亮起")
    b.hit(j, k_b, "kick", 0.8, "整顿亮起")

    def wk(c, kk, T):
        if T < tb(j, k_a):
            return None
        sc = pop_scale(T - tb(j, k_a))
        x0_, x1_ = X0 + 100, X0 + 300
        f = ease_in_out(clamp01((T - tb(j, k_b)) / 0.45))
        x = lerp(x0_, x1_, f)
        y = lerp(GY - 90, GY - 180, f) - math.sin(f * math.pi) * 40
        with at_pop(c, x, y, sc):
            draw_worker(c, x, y, 0.62, mood="smile", rh=(x + 50, y - 230))
        return None
    b.custom(j, k_a, k_a + 0.3, wk)

    def li(c, sc, T):
        x, s = cx + 330, 0.8
        hx, hy = head_of(x, cy + 30, s)
        sweep = T >= tb(j, k_broom)
        with at_pop(c, x, cy + 30, sc):
            ang = 15 * math.sin((T - tb(j, k_broom)) * 7) if sweep else 0
            hand = (x - 70 * s, hy + 140 * s)
            draw_li(c, x, cy + 30, s, "smile", rh=hand, lh=(x - 40 * s, hy + 110 * s))
            if sweep:
                with K.at(c, hand[0], hand[1], ang):
                    C.line(c, (0, -60), (-60, 120), "#A9773E", 9)
                    c.drawPath(P((-90, 110), (-30, 130), (-60, 190), (-120, 170), close=True), K.paint(YELLOW))
        return None
    ev(j, k_li, pop_fn(j, k_li, li), "pop", 0.7)
    b.hit(j, k_broom, "shaker", 0.7, "小李拿起扫帚")


screen4()


# ================================================================ 屏 5：整理——一堆东西分两边：要用的留下，用不上的装箱搬走
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 500
    PX, PY = cx - 40, cy - 120
    k_pile = 0
    k_keep = kq(j, wp(7, 1, 0.5), 1)
    k_out = nx(j, wp(7, 2, 0.5), k_keep)
    k_away = nx(j, wp(7, 3, 0.3), k_out)
    L.note("留下", "拿走", "整理")
    things = [("doc", BLUE), ("mug", ORANGE), ("doc", GRAY), ("tool", BLACK), ("doc", GRAY), ("cup", GRAY),
              ("tool", GRAY), ("box", GRAY)]
    keep = {0, 1, 3}
    KX, BXX = cx - 380, cx + 260

    def draw_thing(c, kind, col, x, y, rot):
        with K.at(c, x, y, rot):
            if kind == "doc":
                box(c, 0, 0, 90, 115, "#FFFFFF", col, 5, 6)
                C.line(c, (-28, -20), (28, -20), col, 4)
                C.line(c, (-28, 10), (18, 10), col, 4)
            elif kind in ("mug", "cup"):
                box(c, 0, 0, 80, 90, "#FFFFFF", col, 5, 10)
                c.drawArc(skia.Rect.MakeXYWH(30, -20, 40, 40), -90, 180, False, wb.marker(col, 5))
            elif kind == "tool":
                c.drawPath(tool_shape("wrench", 0, 0, 0.5), wb.marker(col, 6))
            else:
                box(c, 0, 0, 100, 80, "#E8D2B0", col, 5, 6)

    def pile(c, kk, T):
        sc = pop_scale(T - tb(j, k_pile))
        if sc <= 0:
            return None
        tk, to = tb(j, k_keep), tb(j, k_out)
        for i, (kind, col) in enumerate(things):
            x0, y0 = PX + ((i * 53) % 220) - 110, PY + ((i * 37) % 120) - 60 - i * 6
            if i in keep:
                f = ease_in_out(clamp01((T - tk - (i % 3) * 0.08) / 0.4))
                x, y = lerp(x0, KX + (sorted(keep).index(i) - 1) * 120, f), lerp(y0, cy + 170, f)
            else:
                f = ease_in_out(clamp01((T - to - (i % 3) * 0.08) / 0.4))
                x, y = lerp(x0, BXX, f), lerp(y0, cy + 120, f) - math.sin(f * math.pi) * 120
                if f >= 1:
                    continue
            with at_pop(c, x0, y0, sc):
                draw_thing(c, kind, col, x, y, ((i * 29) % 30) - 15 if f < 1 else 0)
        return None
    ev(j, k_pile, pile, "wood_low", 0.6)
    b.text(j, 0.5, 1.0, "整理", cx, cy - 430, 80, RED)

    def sides(c, kk, T):
        tk = tb(j, k_keep)
        if T >= tk:
            g = pop_scale(T - tk)
            with K.at(c, KX, cy + 290, 0, g):
                K.text(c, "留下", 0, 0, 60, "hand", GREEN)
                c.drawPath(check(110, -10, 30), wb.marker(GREEN, 9))
        return None
    ev(j, k_keep, sides, "pop", 0.7)

    def carry(c, kk, T):
        to, ta = tb(j, k_out), tb(j, k_away)
        if T < to - 0.2:
            return None
        sc = pop_scale(T - to + 0.2)
        x, dy, _ = C.walk(T, ta, 2.0, BXX + 40, BXX + 260)
        s = 0.8
        hx, hy = head_of(x, GY, s)
        with at_pop(c, x, GY, sc):
            draw_worker(c, x, GY + dy, s, lh=(x - 70 * s, hy + 150 * s + dy), rh=(x + 50 * s, hy + 150 * s + dy),
                        mood="smile")
            with K.at(c, x - 20, hy + 140 * s + dy, 0, 1):
                c.drawPath(C.box_path(0, 60, 170, 120), K.paint("#E8D2B0"))
                c.drawPath(C.box_path(0, 60, 170, 120), wb.marker("#7A4A1E", 6))
        if T >= ta:
            K.text(c, "拿走", BXX + 120, cy + 0, 60, "hand", ORANGE, clamp01((T - ta) / 0.2))
            c.drawPath(wb.arrow((BXX - 30, cy + 60), (BXX + 260, cy + 60), 0.0, 30), wb.marker(ORANGE, 7,
                                                                                             clamp01((T - ta) / 0.2)))
        return None
    b.custom(j, k_out, k_out + 0.3, carry, sfx="wood_high", gain=0.7)
    b.hit(j, k_away, "tom", 0.75, "装箱搬走")


screen5()


# ================================================================ 屏 6：整顿——工具墙画好轮廓，少一把时红圈一闪
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    BX, BY = cx - 80, cy - 140
    KINDS = ["wrench", "hammer", "driver", "pliers", "wrench"]
    xs = [BX - 300 + i * 150 for i in range(5)]
    k_board = 0
    k_out = kq(j, wp(8, 2, 0.4), 1)
    k_hang = nx(j, wp(8, 3, 0.2), k_out)
    k_lab = nx(j, wp(9, 1, 0.5), k_hang)
    k_take = nx(j, wp(9, 2, 0.4), k_lab)
    k_ring = nx(j, wp(9, 3, 0.5), k_take)
    L.note("整顿", "标清楚", "扳手", "锤子", "螺丝刀", "钳子")
    b.path(j, k_board, k_board + 0.8, rect(BX, BY, 820, 520, 16), "#A9773E", 12, sfx="wood_low")
    b.text(j, 0.5, 1.0, "整顿", cx - 360, cy - 470, 76, RED)
    NM = {"wrench": "扳手", "hammer": "锤子", "driver": "螺丝刀", "pliers": "钳子"}

    def board(c, kk, T):
        c.drawRect(skia.Rect.MakeXYWH(BX - 404, BY - 254, 808, 508), K.paint("#F3E3C7"))
        for i in range(8):
            for q in range(5):
                c.drawCircle(BX - 360 + i * 103, BY - 210 + q * 105, 5, K.paint("#C9A87A"))
        to = tb(j, k_out)
        for i, kd in enumerate(KINDS):
            x = xs[i]
            sh = tool_shape(kd, x, BY - 20, 0.9)
            if T >= to:
                a = clamp01((T - to - i * 0.08) / 0.2)
                p = K.paint(BLACK, a, 5)
                p.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
                c.drawPath(sh, p)
            missing = i == 2 and T >= tb(j, k_take)
            th = tb(j, k_hang) + i * 0.12
            if T >= th and not missing:
                f = ease_out(clamp01((T - th) / 0.25))
                with K.at(c, 0, -60 * (1 - f), 0, 1):
                    c.drawPath(sh, K.paint(GRAY_FILL if kd != "hammer" else "#E3C9A0"))
                    c.drawPath(sh, wb.marker(BLACK, 6))
            if T >= tb(j, k_lab):
                g = pop_scale(T - tb(j, k_lab) - i * 0.06, 0.2)
                with K.at(c, x, BY + 200, 0, g):
                    K.rr(c, 0, 0, 120, 44, 8, "#FFFFFF")
                    K.text(c, NM[kd], 0, 2, 30, "hand", BLUE)
        tr = tb(j, k_ring)
        if T >= tr:
            ring = skia.Path()
            ring.addOval(skia.Rect.MakeXYWH(xs[2] - 90, BY - 170, 180, 300))
            blink = 1 if int((T - tr) * 4) % 2 == 0 or T - tr > 1.2 else 0.3
            c.drawPath(ring, wb.marker(RED, 10, blink))
            K.text(c, "少了一把", xs[2] + 10, BY - 210, 50, "hand", RED, clamp01((T - tr) / 0.2))
        return None
    b.custom(j, 0.3, 0.6, board)
    b.hit(j, k_out, "pop", 0.7, "画好轮廓")
    b.hit(j, k_hang, "wood_high", 0.75, "工具挂进轮廓")
    b.hit(j, k_lab, "pop", 0.6, "标清楚")
    b.hit(j, k_ring, "rim", 0.85, "空着的轮廓红圈一闪")
    L.note("少了一把")

    def wk(c, kk, T):
        tt = tb(j, k_take)
        sc = pop_scale(T - tb(j, 0))
        x, dy, _ = C.walk(T, tt, 1.6, cx + 350, cx + 420)
        s = 0.8
        hx, hy = head_of(x, GY, s)
        took = T >= tt
        with at_pop(c, x, GY, sc):
            draw_worker(c, x, GY + dy, s, rh=(x + 80 * s, hy + 100 * s + dy) if took else None, mood="flat")
            if took:
                with K.at(c, x + 90 * s, hy + 60 * s + dy, 20, 0.6):
                    c.drawPath(tool_shape("driver", 0, 0, 1), K.paint(GRAY_FILL))
                    c.drawPath(tool_shape("driver", 0, 0, 1), wb.marker(BLACK, 6))
        return None
    b.custom(j, 0, 0.3, wk)
    b.hit(j, k_take, "wood_high", 0.6, "有人拿走一把")


screen6()


# ================================================================ 屏 7：后三级亮起（扫帚、规矩牌、日历）；“大扫除”打叉；问题小红点浮出来
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 120
    X0 = cx - 520
    k_l = [kq(j, wp(10, 1, 0.15), 1)]
    k_l.append(k_l[0] + 1)
    k_l.append(k_l[0] + 2)
    k_bs = nx(j, wp(11, 2, 0.4), k_l[2])
    k_dot = nx(j, wp(11, 3, 0.5), k_bs)
    L.note("大扫除", "问题", "规矩", "每天")

    def st(c, kk, T):
        lit = {0, 1} | {2 + i for i, k_ in enumerate(k_l) if T >= tb(j, k_)}
        stairs(c, X0, GY, lit, {2 + i: T - tb(j, k_) for i, k_ in enumerate(k_l)})
        for i, k_ in enumerate(k_l):
            g = pop_scale(T - tb(j, k_))
            if g <= 0:
                continue
            x, y = X0 + (2 + i) * 200 + 100, GY - (3 + i) * 90 - 120
            with K.at(c, x, y, 0, g):
                if i == 0:
                    C.line(c, (30, -70), (-10, 30), "#A9773E", 8)
                    c.drawPath(P((-50, 20), (20, 40), (0, 80), (-70, 70), close=True), K.paint(YELLOW))
                elif i == 1:
                    box(c, 0, 0, 120, 90, "#FFFFFF", BLUE, 5, 8)
                    K.text(c, "规矩", 0, 2, 40, "hand", BLUE)
                else:
                    box(c, 0, 0, 110, 100, "#FFFFFF", BLACK, 5, 8)
                    c.drawRect(skia.Rect.MakeXYWH(-55, -50, 110, 28), K.paint(RED))
                    K.text(c, "每天", 0, 18, 36, "hand", BLACK)
        return None
    b.custom(j, 0, 0.3, st, sfx="wood_low", gain=0.6)
    for i, k_ in enumerate(k_l):
        b.hit(j, k_, "pop", 0.7, f"第 {3 + i} 级亮起")

    def big(c, kk, T):
        t0 = tb(j, k_bs)
        if T < t0:
            return None
        g = pop_scale(T - t0)
        x, y = cx - 300, cy + 360
        with K.at(c, x, y, 0, g):
            C.line(c, (60, -110), (-20, 60), "#A9773E", 10)
            c.drawPath(P((-80, 40), (30, 70), (0, 130), (-110, 110), close=True), K.paint(YELLOW))
            K.text(c, "大扫除", 0, 200, 56, "hand", BLACK)
        if T >= t0 + 0.25:
            c.drawPath(cross(x - 10, y + 60, 120), wb.marker(RED, 12, clamp01((T - t0 - 0.25) / 0.15)))
        return None
    ev(j, k_bs, big, "tom", 0.8)

    def dots(c, kk, T):
        t0 = tb(j, k_dot)
        if T < t0:
            return None
        for i in range(4):
            f = ease_out(clamp01((T - t0 - i * 0.12) / 0.5))
            x, y = cx + 100 + i * 120, cy + 480 - 150 * f
            c.drawCircle(x, y, 26, K.paint(RED, f))
            K.text(c, "！", x, y + 2, 34, "black", "#FFFFFF", f)
        K.text(c, "问题", cx + 280, cy + 230, 60, "hand", RED, clamp01((T - t0 - 0.3) / 0.2))
        return None
    ev(j, k_dot, dots, "ding", 0.85)

    def wk(c, sc, T):
        x, s = cx + 400, 0.62
        y = GY - 5 * 90
        with at_pop(c, x, y, sc):
            draw_worker(c, x, y, s, mood="smile", rh=(x + 60, y - 240) if T >= tb(j, k_dot) else None)
        return None
    ev(j, 0, pop_fn(j, 0, wk))


screen7()


# ================================================================ 屏 8：第二次——收拾后的桌面只剩几个文件夹；秒表“十秒”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    MX, MY = cx + 60, cy - 220
    k_fd = 1
    k_click = kq(j, wp(12, 1, 0.5), 2)
    k_ten = nx(j, wp(12, 2, 0.5), k_click)
    FD = ["合同", "报表", "图片", "归档"]
    L.note(*FD, "十秒")
    b.path(j, 0, 0.8, join(rect(MX, MY, 820, 500, 20), P((MX, MY + 250), (MX, MY + 310)),
                           P((MX - 140, MY + 314), (MX + 140, MY + 314))), BLACK, 9, sfx="wood_low")

    def fds(c, kk, T):
        tc = tb(j, k_click)
        for i, nm in enumerate(FD):
            g = pop_scale(T - tb(j, k_fd) - i * 0.12)
            if g <= 0:
                continue
            x, y = MX - 270 + i * 180, MY - 60
            hot = i == 0 and T >= tc
            with K.at(c, x, y, 0, g * (1.12 if hot else 1)):
                folder_icon(c, 0, 0, 0.9, nm, fill="#FFE39A" if hot else "#F6D98B")
                if hot:
                    c.drawRoundRect(skia.Rect.MakeXYWH(-90, -80, 180, 210), 16, 16, wb.marker(RED, 7))
        if T >= tc - 0.5:
            f = ease_in_out(clamp01((T - tc + 0.5) / 0.5))
            cursor(c, lerp(MX + 300, MX - 250, f), lerp(MY + 180, MY - 40, f))
        return None
    ev(j, k_fd, fds, "pop", 0.7)
    b.hit(j, k_click, "wood_high", 0.8, "一下点中合同")

    def sw(c, kk, T):
        x, y = cx - 400, cy + 330
        t0 = tb(j, k_fd)
        te = tb(j, k_ten)
        frac = 0.017 * clamp01((T - t0) / max(0.2, te - t0))
        if T >= te:
            with K.at(c, x, y, 0, C.slam_scale(T - te)):
                stopwatch(c, 0, 0, 100, 0.017, "十秒", GREEN, 70)
        else:
            stopwatch(c, x, y, 100, frac)
        return None
    ev(j, 0, sw)
    b.hit(j, k_ten, "kick", 0.85, "秒表：十秒")

    def li(c, sc, T):
        x, s = cx + 330, 0.85
        hx, hy = head_of(x, GY, s)
        ok = T >= tb(j, k_ten)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile" if ok else "flat", rh=(x + 80 * s, hy - 60 * s) if ok else (x - 90 * s, hy + 100 * s))
            if ok:
                sparkle(c, hx, hy, T - tb(j, k_ten), YELLOW, 10, 70, 150)
        return None
    ev(j, 0, pop_fn(j, 0, li))


screen8()


# ================================================================ 屏 9：两个秒表并排；顾客钱包合上；东西各回各家
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    k_a = 0
    k_b = 1
    k_cu = kq(j, wp(14, 1, 0.3), 2)
    k_shut = nx(j, wp(14, 1, 0.9), k_cu)
    k_eat = nx(j, wp(14, 2, 0.5), k_shut)
    k_home = nx(j, wp(15, 1, 0.3), k_eat)
    k_ok = nx(j, wp(15, 2, 0.5), k_home)
    L.note("十分钟", "十秒", "家", "吃时间")

    def sws(c, kk, T):
        for i, (x, frac, lab, col, k_) in enumerate(((cx - 360, 0.999, "十分钟", RED, k_a),
                                                      (cx - 80, 0.017, "十秒", GREEN, k_b))):
            g = pop_scale(T - tb(j, k_))
            if g > 0:
                with K.at(c, x, cy - 330, 0, g):
                    stopwatch(c, 0, 0, 90, frac, lab, col, 56)
        K.text(c, "vs", cx - 220, cy - 330, 50, "black", GRAY, clamp01((T - tb(j, k_b)) / 0.2))
        return None
    ev(j, k_a, sws, "rim", 0.7)
    b.hit(j, k_b, "pop", 0.7, "十秒的秒表")

    def cust(c, kk, T):
        sc = pop_scale(T - tb(j, k_cu))
        if sc <= 0:
            return None
        x, s = cx + 330, 0.9
        hx, hy = head_of(x, GY - 300, s)
        shut = T >= tb(j, k_shut)
        with at_pop(c, x, GY - 300, sc):
            draw_person(c, x, GY - 300, s, coat=GREEN_FILL, line=GREEN, hat=True, mood="flat",
                        lh=(x - 110 * s, hy + 110 * s))
            wallet(c, x - 130 * s, hy + 90 * s, 1.0, 0.0 if shut else 0.7)
            if shut:
                c.drawPath(cross(x - 130 * s, hy + 90 * s, 60), wb.marker(RED, 9, clamp01((T - tb(j, k_shut)) / 0.15)))
        return None
    b.custom(j, k_cu, k_cu + 0.3, cust, sfx="pop", gain=0.7)
    b.hit(j, k_shut, "tom", 0.75, "钱包合上")

    def eat(c, kk, T):
        t0 = tb(j, k_eat)
        if T < t0:
            return None
        g = pop_scale(T - t0)
        x, y = cx + 360, cy - 400
        with K.at(c, x, y, 0, g):
            c.drawCircle(0, 0, 70, K.paint("#FFFFFF"))
            c.drawPath(wb.clock(0, 0, 70), wb.marker(BLACK, 6))
            bite = 25 + 15 * math.sin((T - t0) * 12)
            c.drawPath(P((70, 0), (70 - bite, -bite * 0.6), (70 - bite, bite * 0.6), close=True), K.paint("#E4EFEC"))
            K.text(c, "吃时间", 0, 110, 44, "hand", RED)
        return None
    ev(j, k_eat, eat, "wood_high", 0.7)

    SY = cy + 300

    def home(c, kk, T):
        t0 = tb(j, k_home)
        sc = pop_scale(T - tb(j, k_a) - 0.3)
        if sc <= 0:
            return None
        spots = [(cx - 400, "key"), (cx - 230, "mug"), (cx - 60, "doc")]
        C.line(c, (cx - 500, SY + 70), (cx + 40, SY + 70), "#A9773E", 10)
        for i, (x, kind) in enumerate(spots):
            p = K.paint(GRAY, 1, 4)
            p.setPathEffect(skia.DashPathEffect.Make([12, 8], 0))
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 60, SY - 60, 120, 120), 10, 10, p)
            K.text(c, "家", x, SY + 110, 34, "hand", GRAY)
            f = ease_out(clamp01((T - t0 - i * 0.15) / 0.35))
            ox, oy = x + (i - 1) * 160 + 80, SY + 200
            xx, yy = lerp(ox, x, f), lerp(oy, SY, f) - math.sin(f * math.pi) * 100
            if T < t0:
                xx, yy = ox, oy
            with K.at(c, xx, yy, 0, 0.8):
                if kind == "key":
                    c.drawCircle(-20, 0, 26, wb.marker(ORANGE, 8))
                    C.line(c, (6, 0), (60, 0), ORANGE, 8)
                    C.line(c, (44, 0), (44, 20), ORANGE, 8)
                elif kind == "mug":
                    box(c, 0, 0, 80, 90, "#FFFFFF", BLUE, 6, 10)
                else:
                    doc_card(c, 0, 0, 80, 100, BLACK, 2)
        if T >= tb(j, k_ok):
            c.drawPath(check(cx - 230, SY - 140, 40), wb.marker(GREEN, 10, clamp01((T - tb(j, k_ok)) / 0.2)))
        return None
    ev(j, k_home, home, "wood_high", 0.7)
    b.hit(j, k_ok, "ding", 0.8, "各回各家")


screen9()


# ================================================================ 屏 10：门口翻包找钥匙；窗外地铁开走
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    k_door = 0
    k_dig = kq(j, wp(16, 1, 0.3), 1)
    k_dig2 = nx(j, wp(17, 0, 0.5), k_dig)
    k_key = nx(j, wp(17, 1, 0.3), k_dig2)
    k_train = nx(j, wp(17, 2, 0.2), k_key)
    k_gone = nx(j, wp(17, 2, 0.8), k_train)
    L.note("走了", "地铁")
    DX = cx - 380
    b.path(j, k_door, k_door + 0.8, join(rect(DX, GY - 280, 260, 560, 10), circle(DX + 90, GY - 270, 14),
                                         rect(cx + 260, cy - 300, 480, 300, 14)), BLACK, 9, sfx="wood_low")

    def li(c, kk, T):
        sc = pop_scale(T - tb(j, k_dig) + 0.6)
        if sc <= 0:
            return None
        x, s = cx - 50, 0.9
        hx, hy = head_of(x, GY, s)
        dig = tb(j, k_dig) <= T < tb(j, k_key)
        found = T >= tb(j, k_key)
        with at_pop(c, x, GY, sc):
            hand = (x + 110 * s, hy + 160 * s + (math.sin(T * 16) * 18 if dig else 0))
            if found:
                hand = (x + 120 * s, hy - 40 * s)
            draw_li(c, x, GY, s, "sad" if T >= tb(j, k_gone) else ("o" if dig else "flat"), rh=hand,
                    lh=(x + 60 * s, hy + 190 * s))
            bagp = P((x + 40, GY - 160), (x + 220, GY - 160), (x + 200, GY - 40), (x + 60, GY - 40), close=True)
            c.drawPath(bagp, K.paint("#C98B4B"))
            c.drawPath(bagp, wb.marker("#7A4A1E", 6))
            if dig:
                for n in range(4):
                    ph = ((T - tb(j, k_dig)) * 1.8 + n * 0.25) % 1
                    ox = x + 130 + (n - 1.5) * 70 * ph
                    oy = GY - 170 - math.sin(ph * math.pi) * 160
                    with K.at(c, ox, oy, ph * 300, 1):
                        if n % 2:
                            box(c, 0, 0, 50, 70, "#FFFFFF", GRAY, 4, 6)
                        else:
                            c.drawCircle(0, 0, 22, K.paint([ORANGE, BLUE][n // 2 % 2]))
            if found:
                g = pop_scale(T - tb(j, k_key))
                with K.at(c, hand[0] + 20, hand[1] - 40, 0, g):
                    c.drawCircle(-20, 0, 24, wb.marker(ORANGE, 8))
                    C.line(c, (4, 0), (56, 0), ORANGE, 8)
                    C.line(c, (40, 0), (40, 18), ORANGE, 8)
        return None
    b.custom(j, k_dig, k_dig + 0.3, li, sfx="shaker", gain=0.7)
    b.hit(j, k_dig2, "wood_high", 0.6, "还在翻")
    b.hit(j, k_key, "ding", 0.8, "找到钥匙")

    def train(c, kk, T):
        wx, wy = cx + 260, cy - 300
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(wx - 236, wy - 146, 472, 292))
        c.drawRect(skia.Rect.MakeXYWH(wx - 236, wy - 146, 472, 292), K.paint(BLUE_FILL))
        C.line(c, (wx - 240, wy + 90), (wx + 240, wy + 90), GRAY, 6)
        t0, t1 = tb(j, k_train), tb(j, k_gone)
        if T >= t0:
            f = ease_in_out(clamp01((T - t1) / 0.9)) if T >= t1 else 0.0
            x = lerp(wx - 120, wx + 600, f)
            box(c, x, wy + 30, 520, 110, "#FFFFFF", GREEN, 7, 30)
            for q in range(4):
                c.drawRect(skia.Rect.MakeXYWH(x - 220 + q * 120, wy + 0, 70, 40), K.paint(BLUE_FILL))
            K.text(c, "地铁", x + 150, wy + 60, 34, "hand", GREEN)
        c.restore()
        if T >= tb(j, k_gone) + 0.5:
            K.text(c, "走了", wx, wy + 220, 70, "hand", RED, clamp01((T - tb(j, k_gone) - 0.5) / 0.2))
        return None
    ev(j, 0.4, train)
    b.hit(j, k_train, "pop", 0.6, "地铁进站")
    b.hit(j, k_gone, "tom", 0.8, "地铁开走")


screen10()


# ================================================================ 屏 11：同事要上个月的数据，聊天记录一页页往上划
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    PX, PY = cx + 80, cy - 100
    k_ph = 0
    k_ask = kq(j, wp(18, 0, 0.5), 1)
    k_sw = nx(j, wp(18, 2, 0.2), k_ask)
    k_sw2 = cap(j, k_sw + 2)
    k_ache = nx(j, wp(18, 3, 0.6), k_sw2)
    L.note("上个月的数据？", "酸")

    def phone(c, kk, T):
        sc = pop_scale(T - tb(j, k_ph))
        if sc <= 0:
            return None
        with at_pop(c, PX, PY, sc):
            box(c, PX, PY, 380, 680, "#FFFFFF", BLACK, 10, 40)
            c.save()
            c.clipRect(skia.Rect.MakeXYWH(PX - 170, PY - 300, 340, 600))
            t0 = tb(j, k_sw)
            off = 0.0 if T < t0 else (T - t0) * 520
            for i in range(30):
                y = PY - 250 + i * 110 - 30 * 110 + 600 + off
                y = PY + 260 - i * 110 + off
                if y < PY - 330 or y > PY + 330:
                    continue
                left = i % 3 != 1
                w = 160 + (i * 37) % 100
                xx = PX - 150 + w / 2 if left else PX + 150 - w / 2
                c.drawRoundRect(skia.Rect.MakeXYWH(xx - w / 2, y - 30, w, 60), 20, 20,
                                K.paint("#FFFFFF" if left else "#CDEBC2"))
                c.drawRoundRect(skia.Rect.MakeXYWH(xx - w / 2, y - 30, w, 60), 20, 20, wb.marker(GRAY, 4))
            c.restore()
        return None
    ev(j, k_ph, phone, "wood_low", 0.6)

    def hand(c, kk, T):
        t0 = tb(j, k_sw)
        if T < t0:
            return None
        ph = ((T - t0) * 2.2) % 1
        y = PY + 180 - 300 * ease_in_out(ph)
        x = PX + 40
        with K.at(c, x, y, 0, 1):
            c.drawRoundRect(skia.Rect.MakeXYWH(-24, -10, 48, 150), 24, 24, K.paint(SKIN))
            c.drawRoundRect(skia.Rect.MakeXYWH(-24, -10, 48, 150), 24, 24, wb.marker(ORANGE, 5))
        if T >= tb(j, k_ache):
            g = pop_scale(T - tb(j, k_ache))
            with K.at(c, PX + 260, PY + 120, 0, g):
                K.text(c, "酸", 0, 0, 80, "hand", RED)
                for n in range(3):
                    C.line(c, (-60 + n * 20, -60), (-70 + n * 20, -90), RED, 5)
        return None
    ev(j, k_sw, hand, "shaker", 0.7)
    b.hit(j, k_sw2, "shaker", 0.6, "接着往上划")
    b.hit(j, k_ache, "tom", 0.75, "手指划到发酸")

    def wang(c, sc, T):
        x, s = cx - 390, 0.85
        with at_pop(c, x, GY, sc):
            draw_person(c, x, GY, s, coat="#F3D3E0", line="#B04A78", mood="flat",
                        rh=(x + 100 * s, GY - 290 * s + 60 * s))
        return None
    ev(j, k_ask, pop_fn(j, k_ask, wang), "pop", 0.7)
    ev(j, k_ask, L.pop_bubble("上个月的数据？", cx - 260, cy - 420, j, k_ask, 54, BLACK, tail=-1))


screen11()


# ================================================================ 屏 12：浏览器顶上一排挤成细条的标签页，想关又舍不得
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    BX, BY = cx, cy - 170
    k_win = 0
    k_tab = kq(j, wp(19, 0, 0.3), 1)
    k_tab2 = nx(j, wp(19, 1, 0.5), k_tab)
    k_hov = nx(j, wp(19, 2, 0.2), k_tab2)
    k_no = nx(j, wp(19, 3, 0.5), k_hov)
    L.note("40", "舍不得", "×")
    b.path(j, k_win, k_win + 0.8, rect(BX, BY, 1000, 560, 18), BLACK, 9, sfx="wood_low")

    def tabs(c, kk, T):
        t1, t2 = tb(j, k_tab), tb(j, k_tab2)
        n = 0 if T < t1 else (12 if T < t2 else 40)
        w = 960 / max(1, n)
        for i in range(n):
            g = pop_scale(T - (t1 if i < 12 else t2) - (i % 12) * 0.03, 0.2)
            x = BX - 480 + w * i + w / 2
            with K.at(c, x, BY - 240, 0, g):
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 2, -26, w - 4, 52), 8, 8,
                                K.paint(["#F2C14E", "#7FB2E5", "#F28C8C", "#8FD19E"][i % 4], 0.8))
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 2, -26, w - 4, 52), 8, 8, wb.marker(BLACK, 3))
        if n:
            C.line(c, (BX - 500, BY - 205), (BX + 500, BY - 205), BLACK, 5)
            for r in range(5):
                C.line(c, (BX - 400, BY - 120 + r * 70), (BX + 300 - (r % 2) * 120, BY - 120 + r * 70), GRAY_FILL, 12)
        if n == 40:
            K.text(c, "40", BX + 380, BY + 160, 110, "hand", RED, clamp01((T - t2) / 0.2))
        th = tb(j, k_hov)
        if T >= th:
            back = T >= tb(j, k_no)
            f = ease_in_out(clamp01((T - th) / 0.4))
            if back:
                f = 1 - ease_in_out(clamp01((T - tb(j, k_no)) / 0.4))
            mx = lerp(BX + 100, BX + 140, f) + (4 * math.sin(T * 40) if f > 0.9 else 0)
            my = lerp(BY + 100, BY - 230, f)
            K.text(c, "×", BX + 150, BY - 236, 30, "black", RED, clamp01((T - th) / 0.2))
            cursor(c, mx, my, 1.1)
        return None
    ev(j, k_tab, tabs, "pop", 0.7)
    b.hit(j, k_tab2, "wood_high", 0.75, "标签页挤成细条")
    b.hit(j, k_hov, "pop", 0.6, "鼠标挪到关闭键")

    def li(c, sc, T):
        x, s = cx - 330, 0.85
        hx, hy = head_of(x, GY, s)
        no = T >= tb(j, k_no)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "sad" if no else "flat", rh=(x + 30 * s, hy + 60 * s) if no else (x + 110 * s, hy + 110 * s),
                    lh=(x - 30 * s, hy + 60 * s) if no else None)
        return None
    ev(j, 0, pop_fn(j, 0, li))
    ev(j, k_no, L.slam_text("舍不得", cx + 150, cy + 300, 90, RED, j, k_no, rot=-4), "tom", 0.8)


screen12()


# ================================================================ 屏 13：“等闲下来”的便签被日历一页页往后推；“三步”
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    CX_, CY_ = cx - 260, cy - 220
    k_cal = 0
    k_fl = [kq(j, wp(20, 2, 0.2), 1)]
    k_fl += [k_fl[0] + 1, k_fl[0] + 2]
    k_never = nx(j, wp(20, 3, 0.5), k_fl[2])
    k_broom = nx(j, wp(21, 0, 0.5), k_never)
    k_ten = nx(j, wp(21, 1, 0.5), k_broom)
    k_3 = nx(j, wp(21, 2, 0.6), k_ten)
    MONTHS = ["这周", "下周", "下个月", "明年"]
    L.note(*MONTHS, "等闲下来", "每天十分钟", "三步", "大扫除")

    def cal(c, kk, T):
        sc = pop_scale(T - tb(j, k_cal))
        if sc <= 0:
            return None
        n = sum(1 for k_ in k_fl if T >= tb(j, k_))
        with K.at(c, CX_, CY_, 0, sc):
            box(c, 0, 20, 360, 340, "#FFFFFF", BLACK, 8, 14)
            c.drawRect(skia.Rect.MakeXYWH(-180, -150, 360, 80), K.paint(RED))
            for dx in (-100, 0, 100):
                c.drawCircle(dx, -150, 12, K.paint(BLACK))
            K.text(c, MONTHS[n], 0, -108, 50, "hand", "#FFFFFF")
            if n:
                dt = T - tb(j, k_fl[n - 1])
                if dt < 0.3:
                    with K.at(c, 0, -70, 0, 1.0, max(0.02, 1 - dt / 0.3)):
                        c.drawRect(skia.Rect.MakeXYWH(-175, 0, 350, 260), K.paint("#FFFFFF"))
                        c.drawRect(skia.Rect.MakeXYWH(-175, 0, 350, 260), wb.marker(GRAY, 4))
            with K.at(c, 30, 60, -5 + 3 * n, 1):
                box(c, 0, 0, 260, 100, NOTE_FILL, ORANGE, 5, 8)
                K.text(c, "等闲下来", 0, 2, 48, "hand", ORANGE)
        return None
    ev(j, k_cal, cal, "wood_low", 0.6)
    for k_ in k_fl:
        b.hit(j, k_, "wood_high", 0.65, "日历往后翻")

    def li(c, sc, T):
        x, s = cx + 330, 0.85
        hx, hy = head_of(x, GY - 300, s)
        nv = T >= tb(j, k_never)
        with at_pop(c, x, GY - 300, sc):
            draw_li(c, x, GY - 300, s, "sad" if nv else "flat", rh=(x - 120 * s, hy + 60 * s))
            if nv:
                for n in range(3):
                    ph = ((T - tb(j, k_never)) * 1.6 + n * 0.33) % 1
                    c.drawCircle(hx + (-70 if n % 2 else 70), hy - 20 + ph * 80, 10, K.paint(BLUE, 1 - ph))
        return None
    ev(j, 0, pop_fn(j, 0, li))
    b.hit(j, k_never, "tom", 0.7, "一直闲不下来")

    def bottom(c, kk, T):
        tbm = tb(j, k_broom)
        if T >= tbm:
            g = pop_scale(T - tbm)
            x, y = cx - 360, cy + 330
            with K.at(c, x, y, 0, g * 0.8):
                C.line(c, (60, -110), (-20, 60), "#A9773E", 10)
                c.drawPath(P((-80, 40), (30, 70), (0, 130), (-110, 110), close=True), K.paint(YELLOW))
                c.drawPath(cross(-10, 40, 110), wb.marker(RED, 12))
                K.text(c, "大扫除", 0, 190, 52, "hand", GRAY)
        tt = tb(j, k_ten)
        if T >= tt:
            g = pop_scale(T - tt)
            with K.at(c, cx - 50, cy + 330, 0, g):
                stopwatch(c, 0, 0, 80, 1 / 6, "每天十分钟", GREEN, 46)
        return None
    ev(j, k_broom, bottom, "pop", 0.7)
    b.hit(j, k_ten, "ding", 0.75, "每天十分钟")
    stamp_ev(j, k_3, "三步", cx + 330, cy + 360, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]


screen13()


# ================================================================ 屏 14：做法一——桌面图标被一把扫进“归档”文件夹
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    steps_row(j, 0, 1)
    MX, MY = cx, cy - 80
    k_ic = 2
    k_fd = kq(j, wp(22, 2, 0.2), k_ic + 1)
    k_sw = nx(j, wp(22, 2, 0.7), k_fd)
    k_ok = nx(j, wp(22, 3, 0.7), k_sw)
    L.note("归档", "一个月没打开")
    cells = [(MX - 380 + (i % 9) * 85, MY - 200 + (i // 9) * 90) for i in range(36)]
    old = {i for i in range(36) if (i * 7) % 5 != 0}

    def scr(c, kk, T):
        monitor(c, MX, MY, 880, 540)
        t0, ts = tb(j, k_ic), tb(j, k_sw)
        fx, fy = MX + 330, MY + 180
        for i, (x, y) in enumerate(cells):
            g = pop_scale(T - t0 - (i % 9) * 0.03, 0.2)
            if g <= 0:
                continue
            if i in old and T >= ts:
                f = ease_in_out(clamp01((T - ts - (i % 9) * 0.04) / 0.45))
                if f >= 1:
                    continue
                x, y = lerp(x, fx, f), lerp(y, fy, f)
                g *= 1 - 0.6 * f
            icon(c, x, y, GRAY_FILL if i in old else ICON_COLS[i % 4], 0.7 * g)
        if T >= tb(j, k_fd):
            g = pop_scale(T - tb(j, k_fd))
            bump = 1 + 0.12 * math.exp(-max(0, T - ts - 0.45) * 8) if T >= ts + 0.45 else 1
            with K.at(c, fx, fy, 0, g * bump):
                folder_icon(c, 0, -10, 1.0, None)
                K.text(c, "归档", 0, 10, 44, "hand", BLACK)
            K.text(c, "一个月没打开", MX - 200, MY + 330, 44, "hand", GRAY, clamp01((T - tb(j, k_fd)) / 0.2))
        if T >= tb(j, k_ok):
            g = pop_scale(T - tb(j, k_ok))
            with K.at(c, MX - 100, MY + 60, 0, g):
                p = K.paint(GREEN, 1, 6)
                p.setPathEffect(skia.DashPathEffect.Make([16, 12], 0))
                c.drawRoundRect(skia.Rect.MakeXYWH(-260, -130, 520, 260), 20, 20, p)
                c.drawPath(check(0, 0, 60), wb.marker(GREEN, 12))
        return None
    ev(j, k_ic, scr, "pop", 0.7)
    b.hit(j, k_fd, "wood_high", 0.7, "归档文件夹")
    b.hit(j, k_sw, "shaker", 0.8, "一把扫进去")
    b.hit(j, k_ok, "ding", 0.8, "桌面空出一大块")

    def li(c, sc, T):
        x, s, GY = cx - 400, 0.7, cy + 560
        hx, hy = head_of(x, GY, s)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile" if T >= tb(j, k_ok) else "flat",
                    rh=(x + 100 * s, hy + (40 if T >= tb(j, k_sw) else 120) * s))
        return None
    ev(j, 0, pop_fn(j, 0, li))


screen14()


# ================================================================ 屏 15：做法二——“最终版二”划掉，改成“日期 + 合同”
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    steps_row(j, 1, 1)
    k_old = 2
    k_new = kq(j, wp(23, 1, 0.5), k_old + 1)
    k_new2 = cap(j, k_new + 1)
    k_x = nx(j, wp(23, 2, 0.5), k_new2)
    L.note("最终版二.doc", "1107合同.doc", "日期", "内容")

    def files(c, kk, T):
        x, y = cx - 100, cy - 230
        g = pop_scale(T - tb(j, k_old))
        if g > 0:
            with K.at(c, x, y, 0, g):
                icon(c, -250, 0, "#7FB2E5", 1.3)
                K.text(c, "最终版二.doc", 60, 0, 62, "hand", BLACK)
                if T >= tb(j, k_x):
                    f = clamp01((T - tb(j, k_x)) / 0.25)
                    C.line(c, (-110, -4), (-110 + 360 * f, 4), RED, 12)
        if T >= tb(j, k_new):
            y2 = y + 260
            g = pop_scale(T - tb(j, k_new))
            with K.at(c, x, y2, 0, g):
                icon(c, -250, 0, "#8FD19E", 1.3)
                s_ = "1107合同.doc"
                n = len(s_) if T >= tb(j, k_new2) else min(len(s_), int((T - tb(j, k_new)) / 0.08))
                K.text(c, s_[:n], -110, 0, 62, "hand", GREEN, 1, "left")
                if T >= tb(j, k_new2):
                    for (a_, z_, lab) in ((-110, 20, "日期"), (30, 200, "内容")):
                        C.line(c, (a_, 44), (z_, 44), ORANGE, 6)
                        K.text(c, lab, (a_ + z_) / 2, 90, 40, "hand", ORANGE)
        return None
    ev(j, k_old, files, "pop", 0.7)
    b.hit(j, k_new, "wood_high", 0.7, "敲新文件名")
    b.hit(j, k_new2, "pop", 0.7, "日期加内容")
    b.hit(j, k_x, "rim", 0.85, "最终版二划掉")

    def li(c, sc, T):
        x, s = cx - 50, 0.85
        hx, hy = head_of(x, GY, s)
        typing = tb(j, k_new) <= T < tb(j, k_new2) + 0.3
        with at_pop(c, x, GY, sc):
            C.line(c, (x - 300, GY - 130), (x + 120, GY - 130), "#A9773E", 10)
            box(c, x - 180, GY - 150, 200, 30, "#FFFFFF", BLACK, 5, 6)
            draw_li(c, x, GY, s, "smile", rh=(x - 120 * s, GY - 160 + (math.sin(T * 24) * 8 if typing else 0)),
                    lh=(x - 200 * s, GY - 160))
        return None
    ev(j, 0, pop_fn(j, 0, li))


screen15()


# ================================================================ 屏 16：做法三——门口墙上的小钩子，钥匙和充电器各有画好的位置
def screen16(j=16):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    steps_row(j, 2, 1)
    PX, PY = cx - 180, cy - 160
    k_board = 2
    k_key = kq(j, wp(24, 2, 0.5), k_board + 1)
    k_chg = cap(j, k_key + 1)
    k_loop = nx(j, wp(24, 3, 0.5), k_chg)
    L.note("钥匙", "充电器", "用完放回去")
    b.path(j, k_board, k_board + 0.7, join(rect(PX, PY, 520, 320, 16), circle(PX - 120, PY - 60, 12),
                                           circle(PX + 120, PY - 60, 12)), "#A9773E", 10, sfx="wood_low")

    def spots(c, kk, T):
        if T < tb(j, k_board) + 0.4:
            return None
        p = K.paint(GRAY, 1, 4)
        p.setPathEffect(skia.DashPathEffect.Make([12, 8], 0))
        c.drawCircle(PX - 120, PY + 10, 40, p)
        c.drawRoundRect(skia.Rect.MakeXYWH(PX + 80, PY - 30, 80, 120), 10, 10, p)
        K.text(c, "钥匙", PX - 120, PY + 110, 38, "hand", GRAY)
        K.text(c, "充电器", PX + 120, PY + 130, 38, "hand", GRAY)
        for (k_, kind, tx, ty) in ((k_key, "key", PX - 120, PY + 10), (k_chg, "chg", PX + 120, PY + 30)):
            t0 = tb(j, k_)
            f = ease_out(clamp01((T - t0 + 0.35) / 0.35)) if T >= t0 - 0.35 else 0
            if f <= 0:
                continue
            sx, sy = cx + 260, cy + 200
            x, y = lerp(sx, tx, f), lerp(sy, ty, f) - math.sin(f * math.pi) * 120
            if kind == "key":
                c.drawCircle(x, y, 32, wb.marker(ORANGE, 9))
                C.line(c, (x, y + 32), (x, y + 100), ORANGE, 9)
                C.line(c, (x, y + 80), (x + 20, y + 80), ORANGE, 9)
            else:
                box(c, x, y, 70, 110, "#FFFFFF", BLACK, 6, 10)
                C.line(c, (x, y + 55), (x - 30, y + 160), BLACK, 5)
        tl = tb(j, k_loop)
        if T >= tl:
            g = pop_scale(T - tl)
            with K.at(c, cx + 300, cy - 220, (T - tl) * 120, g):
                c.drawPath(C.loop_arrow(0, 0, 70), wb.marker(GREEN, 10))
            K.text(c, "用完放回去", cx + 280, cy - 90, 52, "hand", GREEN, clamp01((T - tl) / 0.2))
        return None
    b.custom(j, k_board, k_board + 0.3, spots)
    b.hit(j, k_key, "wood_high", 0.75, "钥匙挂上")
    b.hit(j, k_chg, "pop", 0.7, "充电器放好")
    b.hit(j, k_loop, "ding", 0.8, "用完放回去")

    def li(c, sc, T):
        x, s = cx + 300, 0.85
        hx, hy = head_of(x, GY, s)
        throw = tb(j, k_key) - 0.4 <= T < tb(j, k_chg) + 0.2
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile", rh=(x - 120 * s, hy - 40 * s) if throw else (x - 60 * s, hy + 150 * s))
        return None
    ev(j, 0, pop_fn(j, 0, li))


screen16()


# ================================================================ 屏 17：端着冒热气的咖啡，靠在椅子上
def screen17(j=17):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 500
    k_chair = 0
    k_clk = kq(j, wp(25, 0, 0.6), 1)
    k_cup = nx(j, wp(25, 1, 0.3), k_clk)
    k_sip = nx(j, wp(25, 1, 0.9), k_cup)
    L.note("十分钟", "热咖啡")
    X = cx - 60

    def chair(c, kk, T):
        sc = pop_scale(T - tb(j, k_chair))
        if sc <= 0:
            return None
        sip = T >= tb(j, k_sip)
        s = 0.95
        with at_pop(c, X, GY, sc):
            seat = rect(X + 10, GY - 150, 300, 50, 16)
            c.drawPath(seat, K.paint("#E8C7A8"))
            c.drawPath(seat, wb.marker("#A9773E", 7))
            back = P((X + 160, GY - 150), (X + 230, GY - 470), (X + 280, GY - 460), (X + 200, GY - 150), close=True)
            c.drawPath(back, K.paint("#F0D8BF"))
            c.drawPath(back, wb.marker("#A9773E", 7))
            for dx in (-120, 140):
                C.line(c, (X + dx, GY - 125), (X + dx, GY), "#A9773E", 9)
            c.save()
            c.translate(X + 60, GY - 150)
            c.rotate(10)
            c.translate(-(X + 60), -(GY - 150))
            hy = GY - 150 - 170 * s - 290 * s + 120 * s
            cup_xy = (X - 40, hy + (40 if sip else 130) * s)
            draw_li(c, X + 60, GY - 150 + 120 * s - 0, s * 0.9, "smile", rh=cup_xy)
            c.restore()
            if T >= tb(j, k_cup):
                g = pop_scale(T - tb(j, k_cup))
                cx_, cy_ = cup_xy[0] + 10, cup_xy[1] - 20
                with K.at(c, cx_, cy_, 0, g):
                    box(c, 0, 0, 90, 100, "#FFFFFF", ORANGE, 6, 12)
                    c.drawArc(skia.Rect.MakeXYWH(30, -25, 46, 46), -90, 180, False, wb.marker(ORANGE, 6))
                    c.drawRect(skia.Rect.MakeXYWH(-40, -46, 80, 18), K.paint("#7A4A1E"))
                    for n in range(3):
                        ph = (T * 0.9 + n * 0.33) % 1
                        c.drawPath(P((-25 + n * 25, -60 - ph * 120), (-10 + n * 25, -90 - ph * 120),
                                     (-25 + n * 25, -120 - ph * 120)), wb.marker(GRAY, 6, 1 - ph))
                K.text(c, "热咖啡", cx_ - 10, cy_ + 120, 48, "hand", ORANGE)
        return None
    ev(j, k_chair, chair, "wood_low", 0.6)
    b.hit(j, k_cup, "pop", 0.75, "端起咖啡")
    b.hit(j, k_sip, "wood_high", 0.7, "喝一口")

    def clk(c, sc, T):
        x, y = cx + 300, cy - 330
        with at_pop(c, x, y, sc):
            stopwatch(c, x, y, 90, 1 / 6, "十分钟", GREEN, 52)
        return None
    ev(j, k_clk, pop_fn(j, k_clk, clk), "ding", 0.7)


screen17()


# ================================================================ 屏 18：评论区比图标数；小李把桌面清出一块坐进去；下一讲预告
def screen18(j=18):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z))
    k_cmt = 0
    k_nums = kq(j, wp(27, 0, 0.5), 1)
    k_most = nx(j, wp(27, 2, 0.5), k_nums)
    k_clear = nx(j, wp(28, 2, 0.4), k_most)
    k_sit = nx(j, wp(28, 3, 0.5), k_clear)
    k_next = nx(j, wp(29, 0, 0.3), k_sit)
    b.move(j, k_clear, (cx, cy + 420, Z), 1.1)
    NUMS = ["126个", "58个", "203个", "9个"]
    L.note("你桌面有几个图标？", *NUMS, "最满", "下一讲", "明明很小心", "为什么还是手滑？", "附件呢？")
    BY = cy - 300

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 60, BY, 0, sc):
            bubble_box(c, 0, 0, 900, 360, -1)
            K.text(c, "你桌面有几个图标？", 0, -110, 60, "hand", RED)
            for i, nm in enumerate(NUMS):
                g = pop_scale(T - tb(j, k_nums) - i * 0.12, 0.22)
                if g <= 0:
                    continue
                x = -330 + i * 220
                top = i == 2 and T >= tb(j, k_most)
                with K.at(c, x, 30, 0, g * (1.2 if top else 1)):
                    K.rr(c, 0, 0, 180, 80, 40, NOTE_FILL if top else BLUE_FILL)
                    K.text(c, nm, 0, 2, 44, "hand", RED if top else BLUE)
            if T >= tb(j, k_most):
                K.text(c, "最满", 110, 120, 50, "hand", RED, clamp01((T - tb(j, k_most)) / 0.2))
        return None
    ev(j, k_cmt, cmt, "pop", 0.7)
    b.hit(j, k_nums, "wood_high", 0.6, "评论里的数字")
    b.hit(j, k_most, "rim", 0.7, "最满的那个")

    MX, MY = cx + 20, cy + 300

    def desk_(c, kk, T):
        sc = pop_scale(T - tb(j, k_most) - 0.3)
        if sc <= 0:
            return None
        tcl = tb(j, k_clear)
        with at_pop(c, MX, MY, sc):
            monitor(c, MX, MY, 700, 420)
            for i in range(28):
                x0, y0 = MX - 300 + (i % 7) * 100, MY - 150 + (i // 7) * 100
                f = ease_in_out(clamp01((T - tcl - (i % 7) * 0.03) / 0.5)) if T >= tcl else 0
                side = -1 if i % 7 < 3 else 1
                x = lerp(x0, MX + side * 320 - side * (i // 7) * 10, f) if (i % 7) in (2, 3, 4) else x0
                if (i % 7) in (1, 5):
                    x = lerp(x0, MX + side * 300, f)
                icon(c, x, y0, ICON_COLS[i % 4], 0.65)
            ts = tb(j, k_sit)
            if T >= ts:
                g = pop_scale(T - ts)
                with K.at(c, MX, MY + 120, 0, g):
                    draw_li(c, 0, 0, 0.5, "smile", lh=(-40, -90), rh=(40, -90))
                    C.line(c, (-60, -40), (60, -40), "#A9773E", 8)
                sparkle(c, MX, MY - 40, T - ts, YELLOW, 10, 90, 170)
        return None
    b.custom(j, k_most, k_most + 0.3, desk_)
    b.hit(j, k_clear, "shaker", 0.75, "桌面清出一块")
    b.hit(j, k_sit, "ding", 0.8, "小李坐进去")

    def nxt(c, kk, T):
        t0 = tb(j, k_next)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        x, y = cx + 20, cy + 700
        with K.at(c, x, y, -2, sc):
            box(c, 0, 0, 980, 230, "#FFFFFF", BLACK, 7, 18)
            K.rr(c, -380, -70, 170, 60, 30, RED)
            K.text(c, "下一讲", -380, -68, 38, "hand", "#FFFFFF")
            K.text(c, "明明很小心", -90, -60, 58, "hand", BLACK)
            K.text(c, "为什么还是手滑？", -60, 40, 58, "hand", BLACK)
            with K.at(c, 360, 0, 8, 1):
                c.drawRect(skia.Rect.MakeXYWH(-80, -50, 160, 100), K.paint("#FFFFFF"))
                c.drawRect(skia.Rect.MakeXYWH(-80, -50, 160, 100), wb.marker(BLUE, 6))
                c.drawPath(P((-80, -50), (0, 10), (80, -50)), wb.marker(BLUE, 6))
                K.text(c, "附件呢？", 0, 90, 34, "hand", RED)
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen18()

# ================================================================ 收尾
L.finish(cover_shot=3, square_shot=6, notes=NOTES)
L.export(globals())
