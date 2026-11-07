"""《丰田模式》13 防错：明明很小心，为什么还是手滑？（白板手绘 + AI 旁白，竖屏 2:3）

误区对照：开头摆出“再细心一点”的想法，再逐条对照丰田反着来的三处。第 5–11 屏画面左右分栏：
左栏“我们以为”（灰）、右栏“丰田的做法”（亮），顶上三个圆点标出第几处；每处先画左栏、再画右栏，右栏落定时配重音。
- 0–3 秒：鼠标连点“发送”，邮件一封封飞出，“附件呢？”，“手滑”砸下；
- 打工人日常：两个群聊窗口，小李捂脸；邮件回形针是空的；“下次小心”便签贴了一排；
- 身边的例子（drop）：报价单留着上个客户的名字，drop 时红圈圈出 / 公式被删、月底才发现 / 走到楼下又跑回去看门；
- 误区对照：左栏放大镜“再细心一点”，右栏“三处”，砸下“反着来”；
- 误区一：左栏小李被“不够小心”压住，右栏工人拧螺丝、一排里漏一颗；手指从“人”挪到“工具和流程”；
- 误区二：左栏拿放大镜事后查，右栏零件和夹具像拼图卡在一起，“防错装置”；零件装反插不上、正过来滑进去；机器发现漏装，灯亮红、传送带停；
- 误区三：左栏贵机器打叉，右栏一块小挡片、一个小凸起，“简单又便宜”；
- 身边的防错：洗衣机门没关不肯转、手机卡缺角插不反；为什么：注意力曲线一累一急往下掉，一百个勾里一个红叉；
- 说回我们：别光骂自己，“三步”；
  三步做法（附件→正文→收件人、锁住格子、东西挂门把手）；轻松出门；评论区与下一讲。
车间员工戴安全帽（common.draw_worker），小李 common.draw_li。本讲是深色石墨板底，颜色由 theme.Recolor 统一反色。
文案见 fengtian/PLAN.md「### 13 防错」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import core
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_li, draw_worker, pop_scale, rest_hands)
from whiteboard import engine as wb
from whiteboard.engine import P, check, circle, cross, join, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "身边的例子", 2),
    ([4], "身边的例子", 3),
    ([5], "身边的例子", 4),
    ([6, 7], "误区对照", 5),
    ([8, 9], "误区一 · 对照", 6),
    ([10], "误区一 · 对照", 7),
    ([11, 12], "误区二 · 对照", 8),
    ([13], "误区二 · 对照", 9),
    ([14], "误区二 · 对照", 10),
    ([15], "误区三 · 对照", 11),
    ([16, 17], "身边的防错", 12),
    ([18, 19, 20], "为什么靠小心不管用", 13),
    ([21, 22], "说回我们自己", 14),
    ([23], "做法一 · 示意", 15),
    ([24], "做法二 · 示意", 16),
    ([25], "做法三 · 示意", 17),
    ([26], "不用提心吊胆", 18),
    ([27, 28, 29, 30], "评论区见", 19),
]

THEME = FT.get("13")          # 本讲样式（fengtian/theme.py）：石墨板（深色）、开场 mailfly、转场 pan
L = C.Lesson("13", SCREENS, drop_screen=2, board_size=(5000, 13400), theme=THEME,
              trim_tail={16: 0.15})          # 第 16 句句尾碎音（识别成“手”），裁掉
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(18)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 5 一章里讲自働化时提到的防错装置（poka-yoke）：默认人会出错，让错做不出来，防不住就报警停线；"
    "书中说防错装置大多简单便宜。",
    "螺丝、零件、洗衣机、手机卡等均为示意；小李为虚构人物。",
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



AMBER = "#E0A21B"


# ================================================================ 左右对照栏

L.note("我们以为", "丰田的做法")


def versus(j, n, k0=0):
    """左栏“我们以为”、右栏“丰田的做法”，中间竖虚线；顶上三个圆点，第 n 个（1 起，0 = 不亮）高亮。"""
    cx, cy = R[j]

    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k0))
        if sc <= 0:
            return None
        p = K.paint(GRAY, clamp01(sc), 5)
        p.setPathEffect(skia.DashPathEffect.Make([18, 14], 0))
        c.drawLine(cx - 20, cy - 400, cx - 20, cy + 560, p)
        for x, s_, col, fill in ((cx - 300, "我们以为", GRAY, GRAY_FILL), (cx + 260, "丰田的做法", RED, RED_FILL)):
            with K.at(c, x, cy - 470, 0, sc):
                w = K.text_w(s_, 50, "hand") + 60
                box(c, 0, 0, w, 84, fill, col, 6, 42)
                K.text(c, s_, 0, 2, 50, "hand", col)
        for i in range(3):
            on = i + 1 == n
            with K.at(c, cx - 70 + i * 70 + 380 * 0, cy - 560, 0, sc):
                c.drawCircle(0, 0, 18 if on else 12, K.paint(RED if on else GRAY))
        return None
    b.custom(j, k0, k0 + 0.3, fn, sfx="wood_low", gain=0.55)


def screw_row(c, x0, y, n, missing, t_tight, T, s=1.0):
    """一排螺丝：missing 号的那颗没拧，空着。t_tight[i] 为第 i 颗拧进去的时刻。"""
    for i in range(n):
        x = x0 + i * 62 * s
        c.drawCircle(x, y, 22 * s, K.paint(GRAY_FILL))
        c.drawCircle(x, y, 22 * s, wb.marker(BLACK, 4))
        if i == missing:
            continue
        if T >= t_tight[i]:
            a = 45 + 180 * ease_out(clamp01((T - t_tight[i]) / 0.3))
            with K.at(c, x, y, a):
                c.drawCircle(0, 0, 16 * s, K.paint("#C8CCD2"))
                C.line(c, (-12 * s, 0), (12 * s, 0), BLACK, 4)


def magnifier(c, x, y, r=60, ang=0.0):
    with K.at(c, x, y, ang):
        c.drawCircle(0, 0, r, K.paint("#FFFFFF", 0.35))
        c.drawCircle(0, 0, r, wb.marker(BLACK, 8))
        C.line(c, (r * 0.7, r * 0.7), (r * 1.7, r * 1.7), BLACK, 14)


def part_jig(c, x, y, dx, flip, s=1.0, ok=None, dy=0.0):
    """夹具（带凸起的槽）+ 零件（缺口朝向 flip=±1）。dx 为零件离槽的水平距离。"""
    with K.at(c, x, y, 0, s):
        jig = P((-160, -80), (-160, 90), (160, 90), (160, -80), (90, -80), (90, 40), (-90, 40), (-90, -80), close=True)
        c.drawPath(jig, K.paint(BLUE_FILL))
        c.drawPath(jig, wb.marker(BLUE, 7))
        c.drawPath(P((40, 40), (90, -10), (90, 40), close=True), K.paint(BLUE))
        with K.at(c, dx, -30 + dy, 0, 1):
            c.save()
            if flip < 0:
                c.scale(-1, 1)
            part = P((-80, -60), (80, -60), (80, 30), (36, 70), (-80, 70), close=True)
            c.drawPath(part, K.paint(NOTE_FILL))
            c.drawPath(part, wb.marker(ORANGE, 7))
            c.restore()
        if ok is True:
            c.drawPath(check(0, -180, 50), wb.marker(GREEN, 12))
        elif ok is False:
            c.drawPath(cross(0, -180, 46), wb.marker(RED, 12))


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


def envelope(c, x, y, s=1.0, rot=0.0, col=BLUE):
    with K.at(c, x, y, rot, s):
        c.drawRect(skia.Rect.MakeXYWH(-90, -60, 180, 120), K.paint("#FFFFFF"))
        c.drawRect(skia.Rect.MakeXYWH(-90, -60, 180, 120), wb.marker(col, 6))
        c.drawPath(P((-90, -60), (0, 10), (90, -60)), wb.marker(col, 6))


def sheet_grid(c, x, y, rows, cols, cw=110, ch=56, hot=None, hot_fill=RED_FILL, hot_line=RED):
    for r in range(rows):
        for q in range(cols):
            xx, yy = x + (q - (cols - 1) / 2) * cw, y + (r - (rows - 1) / 2) * ch
            is_hot = hot is not None and (r, q) in hot
            c.drawRect(skia.Rect.MakeXYWH(xx - cw / 2, yy - ch / 2, cw, ch), K.paint(hot_fill if is_hot else "#FFFFFF"))
            c.drawRect(skia.Rect.MakeXYWH(xx - cw / 2, yy - ch / 2, cw, ch),
                       wb.marker(hot_line if is_hot else GRAY, 5 if is_hot else 3))


def lock_icon(c, x, y, s=1.0, col=AMBER):
    with K.at(c, x, y, 0, s):
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(-20, -46, 40, 50), 180, 180)
        c.drawPath(arc, wb.marker(col, 7))
        C.line(c, (-20, -21), (-20, -6), col, 7)
        C.line(c, (20, -21), (20, -6), col, 7)
        c.drawRoundRect(skia.Rect.MakeXYWH(-30, -8, 60, 46), 8, 8, K.paint(col))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])


# ================================================================ 屏 1：两个群聊窗口，小李捂脸；空回形针；“下次小心”便签贴了一排
def screen1(j=1):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    k_win = 0
    k_wrong = 1
    k_face = kq(j, wp(0, 1, 0.6), 2)
    k_mail = nx(j, wp(0, 2, 0.5), k_face)
    k_n = [nx(j, wp(1, 1, 0.3), k_mail)]
    k_n += [cap(j, k_n[0] + 1), cap(j, k_n[0] + 2)]
    k_n = sorted(set(k_n))
    L.note("工作群", "家人群", "发错了", "下次小心", "附件：无")

    def wins(c, kk, T):
        for i, (x, s_) in enumerate(((cx - 360, "工作群"), (cx - 40, "家人群"))):
            g = pop_scale(T - tb(j, k_win) - i * 0.15)
            if g <= 0:
                continue
            with K.at(c, x, cy - 330, (i * 2 - 1) * 3, g):
                box(c, 0, 0, 280, 260, "#FFFFFF", GREEN, 7, 18)
                c.drawRect(skia.Rect.MakeXYWH(-140, -130, 280, 50), K.paint(GREEN_FILL))
                K.text(c, s_, 0, -105, 36, "sans_medium", BLACK)
                for r in range(2):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-110, -50 + r * 70, 150, 46), 16, 16, K.paint(GRAY_FILL))
                if i == 1 and T >= tb(j, k_wrong):
                    gg = pop_scale(T - tb(j, k_wrong))
                    with K.at(c, 40, 80, 0, gg):
                        c.drawRoundRect(skia.Rect.MakeXYWH(-90, -26, 180, 52), 16, 16, K.paint(RED_FILL))
                        c.drawRoundRect(skia.Rect.MakeXYWH(-90, -26, 180, 52), 16, 16, wb.marker(RED, 4))
                    K.text(c, "发错了", 30, 160, 44, "hand", RED, clamp01(gg))
        return None
    ev(j, k_win, wins, "pop", 0.65)
    b.hit(j, k_wrong, "tom", 0.75, "消息发进家人群")

    def li(c, sc, T):
        x, s = cx - 250, 0.9
        hx, hy = head_of(x, GY, s)
        palm = T >= tb(j, k_face)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "sad", rh=(hx + 10, hy + 5) if palm else None, lh=(hx - 30, hy + 10) if palm else None)
        return None
    ev(j, 0, pop_fn(j, 0, li))
    b.hit(j, k_face, "wood_high", 0.7, "小李捂脸")

    def mail(c, kk, T):
        t0 = tb(j, k_mail)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        x, y = cx + 330, cy - 330
        with K.at(c, x, y, 4, sc):
            envelope(c, 0, 0, 1.0)
            clip = skia.Path()
            clip.addRoundRect(skia.Rect.MakeXYWH(70, -110, 40, 80), 20, 20)
            p = K.paint(GRAY, 1, 6)
            p.setPathEffect(skia.DashPathEffect.Make([12, 9], 0))
            c.drawPath(clip, p)
            K.text(c, "附件：无", 0, 110, 42, "hand", RED)
        return None
    ev(j, k_mail, mail, "pop", 0.7)

    def notes(c, kk, T):
        for i, k_ in enumerate((k_n * 3)[:5]):
            t0 = tb(j, k_n[min(i // 2, len(k_n) - 1)]) + (i % 2) * 0.27
            g = C.slam_scale(T - t0)
            if g <= 0:
                continue
            x, y = cx - 40 + (i % 3) * 175 + (i // 3) * 85, cy + 10 + (i // 3) * 150
            with K.at(c, x, y, (i * 7) % 15 - 7, g):
                box(c, 0, 0, 150, 130, NOTE_FILL, ORANGE, 5, 6)
                K.text(c, "下次", 0, -24, 40, "hand", ORANGE)
                K.text(c, "小心", 0, 28, 40, "hand", ORANGE)
        return None
    L.note("下次", "小心")
    ev(j, k_n[0], notes)
    for k_ in k_n:
        b.hit(j, k_, "wood_high", 0.7, "便签“下次小心”贴上")


screen1()


# ================================================================ 屏 2：报价单上留着上一个客户的名字，红圈
def screen2(j=2):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    k_li = 0
    k_ch = kq(j, wp(2, 1, 0.3), 1)
    k_doc = nx(j, wp(3, 0, 0.3), k_ch)
    CHIPS = ["发错群", "忘加附件"]
    L.note(*CHIPS)

    def chips(c, kk, T):
        for i, s_ in enumerate(CHIPS):
            g = pop_scale(T - tb(j, k_ch) - i * 0.27)
            if g <= 0:
                continue
            with K.at(c, cx + 20 + i * 290, cy + 380, (i * 2 - 1) * 4, g):
                w = K.text_w(s_, 48, "hand") + 50
                box(c, 0, 0, w, 90, GRAY_FILL, GRAY, 5, 45)
                K.text(c, s_, 0, 2, 48, "hand", GRAY)
        return None
    ev(j, k_ch, chips, "pop", 0.65)
    k_name = nx(j, wp(3, 1, 0.6), k_doc)
    k_ring = L.drop_k()                          # drop：红圈圈出旧名字
    k_name = min(k_name, k_ring - 1)
    b.shots[j].shake, b.shots[j].flashes = [(k_ring, 16.0)], [(k_ring, 0.45)]
    L.note("报价单", "致：张总公司", "上一个客户", "发送")
    DX, DY = cx + 120, cy - 120

    def doc(c, kk, T):
        sc = pop_scale(T - tb(j, k_doc))
        if sc <= 0:
            return None
        with K.at(c, DX, DY, 2, sc):
            box(c, 0, 0, 560, 640, "#FFFFFF", BLACK, 8, 12)
            K.text(c, "报价单", 0, -250, 64, "hand", BLACK)
            if T >= tb(j, k_name):
                K.text(c, "致：张总公司", -40, -150, 50, "hand", BLACK, clamp01((T - tb(j, k_name)) / 0.2))
            for r in range(5):
                C.line(c, (-220, -60 + r * 70), (220 - (r % 2) * 60, -60 + r * 70), GRAY, 6)
            if T >= tb(j, k_ring):
                f = clamp01((T - tb(j, k_ring)) / 0.4)
                ring = skia.Path()
                ring.addArc(skia.Rect.MakeXYWH(-230, -200, 380, 100), -170, 359 * f)
                c.drawPath(ring, wb.marker(RED, 9))
                if f >= 1:
                    K.text(c, "上一个客户", 130, -370, 48, "hand", RED)
        return None
    ev(j, k_doc, doc, "wood_high", 0.7)
    b.hit(j, k_name, "pop", 0.65, "旧名字还在")
    b.hit(j, k_ring, "kick", 0.95, "drop：红圈圈出")

    def li(c, sc, T):
        x, s = cx - 380, 0.85
        hx, hy = head_of(x, GY, s)
        oops = T >= tb(j, k_ring)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "o" if oops else "smile", rh=(hx + 10, hy + 5) if oops else (x + 120 * s, hy + 80 * s))
            if not oops:
                with K.at(c, x + 160 * s, hy + 60 * s, 0, 1):
                    K.rr(c, 0, 0, 130, 60, 30, BLUE)
                    K.text(c, "发送", 0, 2, 38, "hand", "#FFFFFF")
        return None
    ev(j, k_li, pop_fn(j, k_li, li), "pop", 0.65)


screen2()


# ================================================================ 屏 3：公式格子被删成空白；日历翻到月底，红圈
def screen3(j=3):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    SX, SY = cx - 120, cy - 250
    k_sh = 0
    k_del = kq(j, wp(4, 1, 0.5), 1)
    k_cal = nx(j, wp(4, 2, 0.2), k_del)
    k_end = nx(j, wp(4, 2, 0.8), k_cal)
    L.note("=合计", "月底", "30日")

    def sheet(c, kk, T):
        sc = pop_scale(T - tb(j, k_sh))
        if sc <= 0:
            return None
        gone = T >= tb(j, k_del)
        with at_pop(c, SX, SY, sc):
            sheet_grid(c, SX, SY, 5, 5, 140, 64, hot={(4, 4)} if gone else None)
            if not gone:
                K.text(c, "=合计", SX + 280, SY + 128, 36, "sans_medium", GREEN)
            else:
                f = clamp01((T - tb(j, k_del)) / 0.3)
                K.text(c, "=合计", SX + 280, SY + 128 - 80 * f, 36, "sans_medium", GREEN, 1 - f)
            cursor(c, SX + 300, SY + 150)
        return None
    ev(j, k_sh, sheet, "wood_low", 0.6)
    b.hit(j, k_del, "pop", 0.7, "公式被删")

    def cal(c, kk, T):
        t0 = tb(j, k_cal)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        x, y = cx + 250, cy + 220
        te = tb(j, k_end)
        day = int(lerp(3, 30, clamp01((T - t0) / max(0.3, te - t0))))
        with K.at(c, x, y, 0, sc):
            box(c, 0, 20, 280, 260, "#FFFFFF", BLACK, 7, 12)
            c.drawRect(skia.Rect.MakeXYWH(-140, -110, 280, 60), K.paint(RED))
            K.text(c, f"{day}日", 0, 50, 80, "hand", RED if T >= te else BLACK)
            if T >= te:
                ring = skia.Path()
                ring.addOval(skia.Rect.MakeXYWH(-120, -20, 240, 140))
                c.drawPath(ring, wb.marker(RED, 8))
                K.text(c, "月底", 0, 200, 56, "hand", RED)
        return None
    L.note(*[f"{d}日" for d in range(3, 31)])
    ev(j, k_cal, cal, "wood_high", 0.7)
    b.hit(j, k_end, "rim", 0.85, "月底才发现")

    def li(c, sc, T):
        x, s = cx - 330, 0.85
        hx, hy = head_of(x, GY, s)
        oops = T >= tb(j, k_end)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "o" if oops else "flat", lh=(hx - 40, hy - 10) if oops else None,
                    rh=(hx + 40, hy - 10) if oops else None)
        return None
    ev(j, 1, pop_fn(j, 1, li), "pop", 0.6)


screen3()


# ================================================================ 屏 4：小李走到楼下，回头往楼上跑，头顶“锁了吗？”
def screen4(j=4):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    k_st = 0
    k_walk = 1
    k_q = kq(j, wp(5, 0, 0.6), 2)
    k_down = nx(j, wp(5, 1, 0.5), k_q)
    k_back = nx(j, wp(5, 2, 0.4), k_down)
    L.note("锁了吗？")
    # 楼梯：从右上（门）到左下
    steps = [(cx + 380 - i * 110, cy - 160 + i * 100) for i in range(7)]
    stair = P(*[p for i, (x, y) in enumerate(steps) for p in ((x, y), (x - 110, y))])
    b.path(j, k_st, k_st + 0.8, join(stair, rect(cx + 470, cy - 310, 160, 300, 8), circle(cx + 420, cy - 300, 10)),
           BLACK, 9, sfx="wood_low")

    def li(c, kk, T):
        sc = pop_scale(T - tb(j, k_walk))
        if sc <= 0:
            return None
        tw, td, tb_ = tb(j, k_walk), tb(j, k_down), tb(j, k_back)
        if T < td:
            f = ease_in_out(clamp01((T - tw) / max(0.3, td - tw)))
        elif T < tb_:
            f = 1.0
        else:
            f = 1 - ease_in_out(clamp01((T - tb_) / 1.0))
        idx = f * 6
        i0 = int(min(5, idx))
        u = idx - i0
        x = lerp(steps[i0][0], steps[i0 + 1][0], u) - 55
        y = lerp(steps[i0][1], steps[i0 + 1][1], u)
        bob = -abs(math.sin(T * 9)) * 10 if 0 < f < 1 else 0
        s = 0.7
        with at_pop(c, x, y, sc):
            c.save()
            if T >= tb_:
                c.translate(x, 0)
                c.scale(-1, 1)
                c.translate(-x, 0)
            draw_li(c, x, y + bob, s, "o" if T >= tb(j, k_q) else "flat", bag=True)
            c.restore()
        hx, hy = head_of(x, y, s)
        if T >= tb(j, k_q):
            g = pop_scale(T - tb(j, k_q))
            with K.at(c, hx + 40, hy - 120, 0, g):
                bubble_box(c, 0, 0, 280, 110, -1)
                K.text(c, "锁了吗？", 0, 2, 52, "hand", RED)
        return None
    b.custom(j, k_walk, k_walk + 0.3, li, sfx="pop", gain=0.6)
    b.hit(j, k_q, "tom", 0.75, "锁了吗？")
    b.hit(j, k_down, "wood_high", 0.6, "走到楼下")
    b.hit(j, k_back, "shaker", 0.8, "又跑回去")


screen4()


# ================================================================ 屏 5：左栏放大镜“再细心一点”，右栏“三处”；砸下“反着来”
def screen5(j=5):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    versus(j, 0)
    k_li = 1
    k_mag = kq(j, wp(6, 2, 0.3), 2)
    k_3 = nx(j, wp(7, 0, 0.6), k_mag)
    KD = nx(j, wp(7, 1, 0.8), k_3)              # “反着来”砸下（2026-11 起 drop 移到屏 2）
    b.shots[j].shake = [(KD, 12.0)]
    L.note("再细心一点", "三处", "反着来")

    def li(c, sc, T):
        x, s = cx - 330, 0.9
        hx, hy = head_of(x, GY, s)
        look = T >= tb(j, k_mag)
        mx = hx + 120 + 30 * math.sin((T - tb(j, k_mag)) * 3) if look else hx + 120
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "flat", rh=(mx - 50, hy + 60) if look else None)
            if look:
                magnifier(c, mx, hy - 30, 60, -20)
                for n in range(3):
                    ph = ((T - tb(j, k_mag)) * 1.4 + n * 0.33) % 1
                    c.drawCircle(hx + (-70 if n % 2 else 70), hy - 20 + ph * 80, 10, K.paint(BLUE, 1 - ph))
        return None
    ev(j, k_li, pop_fn(j, k_li, li), "pop", 0.65)
    ev(j, k_mag, L.pop_text("再细心一点", cx - 290, cy - 260, 60, GRAY, j, k_mag), "wood_high", 0.7)

    def three(c, kk, T):
        t0 = tb(j, k_3)
        if T < t0:
            return None
        for i in range(3):
            g = pop_scale(T - t0 - i * 0.12)
            with K.at(c, cx + 110 + i * 150, cy - 220, 0, g):
                c.drawCircle(0, 0, 56, K.paint(RED_FILL))
                c.drawCircle(0, 0, 56, wb.marker(RED, 7))
                K.text(c, str(i + 1), 0, 4, 64, "hand", RED)
        K.text(c, "三处", cx + 260, cy - 80, 64, "hand", RED, clamp01((T - t0 - 0.3) / 0.2))
        return None
    ev(j, k_3, three, "pop", 0.75)

    def flip(c, kk, T):
        t0 = tb(j, KD)
        if T < t0:
            return None
        g = pop_scale(T - t0, 0.25)
        y = cy + 20
        with K.at(c, cx - 20, y, 0, g):
            c.drawPath(wb.arrow((-240, -40), (200, -40), -0.15, 40), wb.marker(RED, 10))
            c.drawPath(wb.arrow((200, 60), (-240, 60), -0.15, 40), wb.marker(GRAY, 10))
        with K.at(c, cx + 230, cy + 400, -5, C.slam_scale(T - t0)):
            K.text(c, "反着来", 0, 0, 110, "hand", RED)
        return None
    ev(j, KD, flip, "kick", 0.95)


screen5()


# ================================================================ 屏 6：误区一——左栏小李被“不够小心”压住；右栏一排螺丝漏一颗
def screen6(j=6):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    versus(j, 1)
    k_li = kq(j, wp(8, 0, 0.5), 1)
    k_wt = nx(j, wp(8, 1, 0.5), k_li)
    k_wk = nx(j, wp(8, 2, 0.4), k_wt)
    k_def = nx(j, wp(8, 3, 0.5), k_wk)
    k_sc = nx(j, wp(9, 1, 0.2), k_def)
    k_miss = nx(j, wp(9, 2, 0.5), k_sc)
    L.note("不够小心", "人一定会出错", "漏了")

    def left(c, kk, T):
        sc = pop_scale(T - tb(j, k_li))
        if sc <= 0:
            return None
        x, s = cx - 300, 0.9
        tw = tb(j, k_wt)
        sq = 1.0 if T < tw else lerp(1.0, 0.72, ease_out(clamp01((T - tw) / 0.2)))
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "sad" if T >= tw else "flat", squash=sq)
        if T >= tw - 0.3:
            f = ease_out(clamp01((T - tw + 0.3) / 0.3))
            top = GY - 290 * s * sq - 60
            y = lerp(cy - 380, top - 60, f)
            with K.at(c, x, y, -3, 1):
                box(c, 0, 0, 300, 110, GRAY_FILL, BLACK, 7, 10)
                K.text(c, "不够小心", 0, 2, 54, "hand", BLACK)
        return None
    ev(j, k_li, left, "pop", 0.65)
    b.hit(j, k_wt, "tom", 0.85, "“不够小心”压下来")

    def right(c, kk, T):
        sc = pop_scale(T - tb(j, k_wk))
        if sc <= 0:
            return None
        x, s = cx + 400, 0.8
        hx, hy = head_of(x, GY, s)
        t0 = tb(j, k_sc)
        tt = [t0 + i * 0.22 for i in range(7)]
        busy = t0 <= T < t0 + 1.6
        with at_pop(c, x, GY, sc):
            box(c, cx + 190, cy + 170, 440, 110, BLUE_FILL, BLUE, 6, 10)
            screw_row(c, cx + 5, cy + 170, 7, 4, tt, T)
            rot = 30 * math.sin(T * 20) if busy else 0
            hand = (x - 120 * s, hy + 150 * s)
            draw_worker(c, x, GY, s, rh=hand, mood="flat")
            with K.at(c, hand[0] - 20, hand[1], rot):
                C.line(c, (0, 0), (-90, -30), GRAY, 12)
        if T >= tb(j, k_def):
            g = pop_scale(T - tb(j, k_def))
            with K.at(c, cx + 250, cy - 230, 0, g):
                K.text(c, "人一定会出错", 0, 0, 58, "hand", RED)
        tm = tb(j, k_miss)
        if T >= tm:
            ring = skia.Path()
            ring.addOval(skia.Rect.MakeXYWH(cx + 5 + 4 * 62 - 50, cy + 120, 100, 100))
            c.drawPath(ring, wb.marker(RED, 9, clamp01((T - tm) / 0.2)))
            K.text(c, "漏了", cx + 5 + 4 * 62, cy + 280, 52, "hand", RED, clamp01((T - tm) / 0.2))
        return None
    ev(j, k_wk, right, "pop", 0.65)
    b.hit(j, k_def, "rim", 0.8, "右栏：人一定会出错")
    b.hit(j, k_sc, "shaker", 0.7, "一颗颗拧螺丝")
    b.hit(j, k_miss, "ding", 0.8, "漏了一颗")


screen6()


# ================================================================ 屏 7：手指从“人”挪到“工具 / 流程”，扳手在流程图上拧一下
def screen7(j=7):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    versus(j, 1)
    k_ppl = 1
    k_mv = kq(j, wp(10, 1, 0.3), 2)
    k_wr = nx(j, wp(10, 1, 0.9), k_mv)
    k_no = nx(j, wp(10, 2, 0.5), k_wr)
    L.note("人", "工具", "流程", "别光盯着人")
    PX, PY = cx - 300, cy - 50
    FX, FY = cx + 260, cy - 50

    def ppl(c, sc, T):
        with at_pop(c, PX, PY, sc):
            draw_li(c, PX, PY + 160, 0.6, "flat")
            K.text(c, "人", PX, PY + 230, 60, "hand", GRAY)
            if T >= tb(j, k_no):
                g = clamp01((T - tb(j, k_no)) / 0.2)
                ring = skia.Path()
                ring.addOval(skia.Rect.MakeXYWH(PX - 130, PY - 120, 260, 400))
                c.drawPath(ring, wb.marker(GRAY, 6, g))
        return None
    ev(j, k_ppl, pop_fn(j, k_ppl, ppl), "pop", 0.65)

    def flow(c, kk, T):
        t0 = tb(j, k_mv)
        if T < t0:
            return None
        for i, s_ in enumerate(("工具", "流程")):
            g = pop_scale(T - t0 - i * 0.15)
            with K.at(c, FX, FY - 110 + i * 220, 0, g):
                box(c, 0, 0, 280, 130, RED_FILL, RED, 7, 16)
                K.text(c, s_, 0, 2, 64, "hand", RED)
        if T >= t0:
            C.line(c, (FX, FY - 45), (FX, FY + 45), RED, 6)
        tw = tb(j, k_wr)
        if T >= tw:
            a = -40 + 70 * ease_in_out(clamp01((T - tw) / 0.35))
            with K.at(c, FX + 200, FY + 110, a, 1):
                c.drawPath(join(rect(0, 70, 26, 150, 10), circle(0, -30, 36)), K.paint(GRAY_FILL))
                c.drawPath(join(rect(0, 70, 26, 150, 10), circle(0, -30, 36)), wb.marker(BLACK, 6))
        # 手指从“人”移到“工具”
        f = ease_in_out(clamp01((T - t0) / 0.6))
        hx, hy = lerp(PX + 120, FX - 170, f), lerp(PY - 200, FY - 110, f)
        with K.at(c, hx, hy, 90, 1):
            c.drawRoundRect(skia.Rect.MakeXYWH(-18, -10, 36, 110), 18, 18, K.paint(SKIN))
            c.drawRoundRect(skia.Rect.MakeXYWH(-18, -10, 36, 110), 18, 18, wb.marker(ORANGE, 5))
            c.drawRoundRect(skia.Rect.MakeXYWH(-40, 80, 80, 90), 26, 26, K.paint(SKIN))
            c.drawRoundRect(skia.Rect.MakeXYWH(-40, 80, 80, 90), 26, 26, wb.marker(ORANGE, 5))
        return None
    ev(j, k_mv, flow, "wood_high", 0.7)
    b.hit(j, k_wr, "rim", 0.8, "扳手拧一下")
    ev(j, k_no, L.slam_text("别光盯着人", cx - 20, cy + 400, 80, RED, j, k_no, rot=-3), "kick", 0.8)


screen7()


# ================================================================ 屏 8：误区二——左栏拿放大镜事后查；右栏零件和夹具卡在一起，“防错装置”
def screen8(j=8):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    versus(j, 2)
    k_li = kq(j, wp(11, 1, 0.3), 1)
    k_pj = nx(j, wp(11, 3, 0.2), k_li)
    k_fit = nx(j, wp(11, 3, 0.8), k_pj)
    k_name = nx(j, wp(12, 1, 0.4), k_fit)
    L.note("事后多查一遍", "防错装置")

    def left(c, sc, T):
        x, s = cx - 330, 0.85
        hx, hy = head_of(x, GY, s)
        mx = cx - 200 + 50 * math.sin((T - tb(j, k_li)) * 3)
        with at_pop(c, x, GY, sc):
            for i in range(3):
                doc_card(c, cx - 230 + i * 30, cy + 40 - i * 20, 150, 190, GRAY, 3, rot=(i - 1) * 6)
            draw_li(c, x, GY, s, "flat", rh=(mx - 60, cy + 120))
            magnifier(c, mx, cy + 40, 55, -20)
            K.text(c, "事后多查一遍", cx - 300, cy - 220, 50, "hand", GRAY)
        return None
    ev(j, k_li, pop_fn(j, k_li, left), "pop", 0.65)

    def right(c, kk, T):
        t0 = tb(j, k_pj)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        tf = tb(j, k_fit)
        f = ease_in_out(clamp01((T - tf + 0.35) / 0.35)) if T >= tf - 0.35 else 0.0
        with at_pop(c, cx + 260, cy + 80, sc):
            part_jig(c, cx + 260, cy + 80, 0, 1, 1.1, True if T >= tf + 0.05 else None, dy=-220 * (1 - f))
        if T >= tf:
            sparkle(c, cx + 260, cy + 80, T - tf, YELLOW, 10, 120, 200)
        return None
    ev(j, k_pj, right, "wood_high", 0.7)
    b.hit(j, k_fit, "rim", 0.85, "零件卡进夹具")
    stamp_ev(j, k_name, "防错装置", cx + 260, cy + 380, 80, -4, "kick", 0.9)


screen8()


# ================================================================ 屏 9：零件装反卡住（红叉），正过来滑进去（勾）
def screen9(j=9):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    versus(j, 2)
    k_rev = kq(j, wp(13, 1, 0.3), 1)
    k_stuck = nx(j, wp(13, 2, 0.3), k_rev)
    k_flip = nx(j, wp(13, 2, 0.8), k_stuck)
    k_in = cap(j, k_flip + 1)
    L.note("装反了", "插不上", "只有一个方向")

    def left(c, sc, T):
        with at_pop(c, cx - 300, cy, sc):
            K.text(c, "装反了", cx - 300, cy - 260, 60, "hand", GRAY)
            draw_li(c, cx - 300, GY, 0.85, "o" if T >= tb(j, k_stuck) else "flat",
                    rh=(cx - 200, GY - 300))
        return None
    ev(j, 0, pop_fn(j, 0, left))

    def right(c, kk, T):
        sc = pop_scale(T - tb(j, k_rev))
        if sc <= 0:
            return None
        ts, tf, ti = tb(j, k_stuck), tb(j, k_flip), tb(j, k_in)
        if T < tf:
            d = ease_out(clamp01((T - tb(j, k_rev)) / max(0.2, ts - tb(j, k_rev))))
            yoff = -260 + 170 * d + C.wobble(T - ts, 10, 30, 8)
            ok = False if T >= ts else None
            flip = -1
        else:
            rot = clamp01((T - tf) / 0.3)
            flip = 1 if rot > 0.5 else -1
            d = ease_in_out(clamp01((T - ti) / 0.3)) if T >= ti else 0
            yoff = -90 + 90 * d
            ok = True if T >= ti + 0.2 else None
        with at_pop(c, cx + 260, cy + 80, sc):
            part_jig(c, cx + 260, cy + 80, 0, flip, 1.1, ok, dy=yoff)
        K.text(c, "只有一个方向", cx + 260, cy - 260, 54, "hand", RED, clamp01((T - ti) / 0.2))
        if T >= ts and T < tf:
            K.text(c, "插不上", cx + 260, cy + 330, 56, "hand", RED)
        return None

    ev(j, k_rev, right, "pop", 0.65)
    b.hit(j, k_stuck, "tom", 0.85, "装反了卡住")
    b.hit(j, k_flip, "wood_high", 0.7, "翻过来")
    b.hit(j, k_in, "ding", 0.85, "滑进去")


screen9()


# ================================================================ 屏 10：机器一发现漏装，灯亮红，传送带停住
def screen10(j=10):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    versus(j, 2)
    k_belt = 1
    k_det = kq(j, wp(14, 1, 0.5), 2)
    k_alarm = nx(j, wp(14, 2, 0.4), k_det)
    k_stop = nx(j, wp(14, 2, 0.9), k_alarm)
    L.note("防不住", "停", "漏装")
    BY = cy + 200

    def left(c, sc, T):
        with at_pop(c, cx - 300, cy, sc):
            K.text(c, "防不住", cx - 300, cy - 260, 60, "hand", GRAY)
            c.drawPath(cross(cx - 300, cy - 80, 80), wb.marker(GRAY, 10))
            K.text(c, "？", cx - 300, cy + 140, 140, "hand", GRAY)
        return None
    ev(j, 0, pop_fn(j, 0, left))

    def belt(c, kk, T):
        sc = pop_scale(T - tb(j, k_belt))
        if sc <= 0:
            return None
        ts = tb(j, k_stop)
        tt = min(T, ts) - tb(j, k_belt)
        with at_pop(c, cx + 260, BY, sc):
            box(c, cx + 230, BY + 40, 560, 50, "#3A3F48", BLACK, 5, 25)
            for i in range(4):
                x = cx - 30 + ((i * 160 + tt * 180) % 640)
                if x > cx + 500:
                    continue
                miss = i == 2
                box(c, x, BY - 30, 90, 80, NOTE_FILL, ORANGE, 5, 8)
                if not miss:
                    c.drawCircle(x, BY - 30, 14, K.paint(GRAY))
            # 检测头 + 灯
            C.line(c, (cx + 330, BY - 220), (cx + 330, BY - 110), BLACK, 8)
            box(c, cx + 330, BY - 100, 80, 40, GRAY_FILL, BLACK, 5, 6)
            red = T >= tb(j, k_alarm)
            blink = red and (int((T - tb(j, k_alarm)) * 5) % 2 == 0 or T > ts + 0.6)
            c.drawCircle(cx + 330, BY - 260, 46, K.paint(RED if blink else GRAY_FILL))
            c.drawCircle(cx + 330, BY - 260, 46, wb.marker(BLACK, 6))
            if red:
                for n in range(6):
                    a = math.radians(n * 60 + 30)
                    C.line(c, (cx + 330 + 60 * math.cos(a), BY - 260 + 60 * math.sin(a)),
                           (cx + 330 + 90 * math.cos(a), BY - 260 + 90 * math.sin(a)), RED, 6, 0.8)
        if T >= tb(j, k_det):
            g = pop_scale(T - tb(j, k_det))
            with K.at(c, cx + 150, BY - 160, 0, g):
                K.text(c, "漏装", 0, 0, 46, "hand", RED)
        if T >= ts:
            with K.at(c, cx + 140, cy - 230, -6, C.slam_scale(T - ts)):
                box(c, 0, 0, 150, 150, RED_FILL, RED, 10, 75)
                K.text(c, "停", 0, 4, 90, "hand", RED)
        return None
    ev(j, k_belt, belt, "wood_low", 0.65)
    b.hit(j, k_det, "pop", 0.7, "检测到漏装")
    b.hit(j, k_alarm, "rim", 0.85, "灯亮红")
    b.hit(j, k_stop, "kick", 0.85, "传送带停住")

    def wk(c, sc, T):
        x, s = cx + 470, 0.7
        with at_pop(c, x, GY, sc):
            draw_worker(c, x, GY, s, mood="o" if T >= tb(j, k_alarm) else "flat",
                        rh=(x - 60, GY - 290 * s - 40) if T >= tb(j, k_stop) else None)
        return None
    ev(j, k_belt, pop_fn(j, k_belt, wk))


screen10()


# ================================================================ 屏 11：误区三——左栏贵机器打叉；右栏小挡片、小凸起，“简单又便宜”
def screen11(j=11):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    versus(j, 3)
    k_m = kq(j, wp(15, 1, 0.3), 1)
    k_x = nx(j, wp(15, 1, 0.9), k_m)
    k_tab = nx(j, wp(15, 2, 0.4), k_x)
    k_bump = cap(j, k_tab + 1)
    k_cheap = nx(j, wp(15, 3, 0.5), k_bump)
    L.note("花大钱", "¥¥¥", "简单又便宜", "挡片", "凸起")

    def mach(c, sc, T):
        x, y = cx - 300, cy + 60
        with at_pop(c, x, y, sc):
            box(c, x, y, 380, 300, GRAY_FILL, BLACK, 8, 16)
            box(c, x - 60, y - 40, 180, 120, "#3A3F48", BLACK, 5, 8)
            for i in range(3):
                c.drawCircle(x + 110, y - 80 + i * 60, 18, K.paint([RED, AMBER, GREEN][i]))
            with K.at(c, x + 120, y - 200, 10, 1):
                box(c, 0, 0, 180, 80, NOTE_FILL, ORANGE, 5, 10)
                K.text(c, "¥¥¥", 0, 2, 50, "black", ORANGE)
            K.text(c, "花大钱", x, y + 220, 56, "hand", GRAY)
        if T >= tb(j, k_x):
            c.drawPath(cross(x, y, 170), wb.marker(RED, 12, clamp01((T - tb(j, k_x)) / 0.15)))
        return None
    ev(j, k_m, pop_fn(j, k_m, mach), "pop", 0.7)
    b.hit(j, k_x, "tom", 0.8, "贵机器打叉")

    def small(c, kk, T):
        for k_, kind, x in ((k_tab, "tab", cx + 160), (k_bump, "bump", cx + 380)):
            g = pop_scale(T - tb(j, k_))
            if g <= 0:
                continue
            y = cy + 60
            with K.at(c, x, y, 0, g):
                if kind == "tab":
                    box(c, 0, 0, 40, 140, NOTE_FILL, ORANGE, 6, 6)
                    C.line(c, (-80, 70), (80, 70), BLACK, 8)
                    K.text(c, "挡片", 0, 130, 44, "hand", ORANGE)
                else:
                    C.line(c, (-90, 40), (90, 40), BLACK, 8)
                    c.drawPath(P((-30, 40), (0, -10), (30, 40), close=True), K.paint(NOTE_FILL))
                    c.drawPath(P((-30, 40), (0, -10), (30, 40), close=True), wb.marker(ORANGE, 6))
                    K.text(c, "凸起", 0, 130, 44, "hand", ORANGE)
        return None
    ev(j, k_tab, small, "pop", 0.75)
    b.hit(j, k_bump, "pop", 0.65, "一个小凸起")
    ev(j, k_cheap, L.slam_text("简单又便宜", cx + 260, cy - 220, 72, RED, j, k_cheap, rot=-3), "kick", 0.85)

    def wk(c, sc, T):
        x, s = cx + 270, 0.7
        with at_pop(c, x, GY, sc):
            draw_worker(c, x, GY, s, mood="smile" if T >= tb(j, k_cheap) else "flat",
                        rh=(x + 80, GY - 290 * s - 30) if T >= tb(j, k_cheap) else None)
        return None
    ev(j, k_tab, pop_fn(j, k_tab, wk))


screen11()


# ================================================================ 屏 12：洗衣机门没关不肯转；手机卡缺角，插反了放不进去
def screen12(j=12):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    WX, WY = cx - 270, cy - 120
    k_wm = 0
    k_open = kq(j, wp(16, 1, 0.5), 1)
    k_no = nx(j, wp(16, 2, 0.5), k_open)
    k_sim = nx(j, wp(17, 0, 0.4), k_no)
    k_rev = nx(j, wp(17, 1, 0.3), k_sim)
    k_ok = cap(j, k_rev + 2)
    L.note("不肯转", "放不进去", "门没关")
    b.path(j, k_wm, k_wm + 0.8, join(rect(WX, WY, 420, 480, 24), P((WX - 210, WY - 150), (WX + 210, WY - 150)),
                                     circle(WX + 140, WY - 195, 16)), BLACK, 9, sfx="wood_low")

    def wm(c, kk, T):
        to = tb(j, k_open)
        op = ease_out(clamp01((T - to) / 0.3)) if T >= to else 0
        c.drawCircle(WX, WY + 50, 130, K.paint("#3A3F48"))
        c.drawCircle(WX, WY + 50, 130, wb.marker(BLACK, 7))
        with K.at(c, WX - 130 * op * 1.6, WY + 50, 0, 1, max(0.25, 1 - 0.75 * op)):
            c.drawCircle(0, 0, 150, K.paint(BLUE_FILL, 0.7))
            c.drawCircle(0, 0, 150, wb.marker(BLUE, 8))
        if T >= tb(j, k_no):
            g = pop_scale(T - tb(j, k_no))
            with K.at(c, WX, WY + 380, 0, g):
                K.text(c, "不肯转", 0, 0, 64, "hand", RED)
            c.drawPath(cross(WX, WY + 50, 70), wb.marker(RED, 10, clamp01(g)))
        if T >= to:
            K.text(c, "门没关", WX - 60, WY - 330, 50, "hand", GRAY, clamp01((T - to) / 0.2))
        return None
    b.custom(j, 0.5, 0.8, wm)
    b.hit(j, k_open, "pop", 0.7, "门没关好")
    b.hit(j, k_no, "tom", 0.8, "不肯转")

    def sim(c, kk, T):
        t0 = tb(j, k_sim)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        x, y = cx + 300, cy - 60
        tr, tok = tb(j, k_rev), tb(j, k_ok)
        with at_pop(c, x, y, sc):
            box(c, x, y + 120, 240, 120, "#3A3F48", BLACK, 6, 10)
            c.drawPath(P((x - 90, y + 90), (x + 60, y + 90), (x + 90, y + 120), (x + 90, y + 150), (x - 90, y + 150),
                         close=True), K.paint("#1B1B1F"))
            flip = T < tok - 0.15
            d = 0.0
            if T >= tr and flip:
                d = 40 * ease_out(clamp01((T - tr) / 0.25)) + C.wobble(T - tr - 0.25, 8, 30, 8)
            if T >= tok:
                d = 150 * ease_in_out(clamp01((T - tok) / 0.3))
            with K.at(c, x, y - 120 + d, 0, 1):
                c.save()
                if flip:
                    c.scale(-1, 1)
                card = P((-80, -60), (50, -60), (80, -30), (80, 60), (-80, 60), close=True)
                c.drawPath(card, K.paint(NOTE_FILL))
                c.drawPath(card, wb.marker(AMBER, 7))
                c.drawRoundRect(skia.Rect.MakeXYWH(-40, -30, 70, 56), 8, 8, K.paint(AMBER))
                c.restore()
            if tr <= T < tok:
                K.text(c, "放不进去", x, y - 290, 56, "hand", RED)
                c.drawPath(cross(x + 160, y - 120, 40), wb.marker(RED, 9))
            if T >= tok + 0.3:
                c.drawPath(check(x + 170, y, 44), wb.marker(GREEN, 11))
        return None
    ev(j, k_sim, sim, "pop", 0.7)
    b.hit(j, k_rev, "tom", 0.8, "手机卡插反卡住")
    b.hit(j, k_ok, "ding", 0.8, "正过来插进去")

    def li(c, sc, T):
        x, s = cx + 160, 0.75
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile" if T >= tb(j, k_ok) else "flat",
                    rh=(x + 100 * s, GY - 290 * s + 60 * s))
        return None
    ev(j, k_sim, pop_fn(j, k_sim, li))


screen12()


# ================================================================ 屏 13：注意力曲线一累一急往下掉；一百个勾里一个红叉
def screen13(j=13):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    k_ax = 0
    k_cur = kq(j, wp(19, 0, 0.2), 1)
    k_drop = nx(j, wp(19, 1, 0.5), k_cur)
    k_grid = nx(j, wp(20, 0, 0.4), k_drop)
    k_x = nx(j, wp(20, 2, 0.4), k_grid)
    L.note("注意力", "累", "急", "掉线", "100次")
    AX, AY = cx - 480, cy - 40
    b.path(j, k_ax, k_ax + 0.7, join(P((AX, AY - 400), (AX, AY), (AX + 980, AY)),
                                     P((AX + 950, AY - 20), (AX + 980, AY), (AX + 950, AY + 20))), BLACK, 8, sfx="wood_low")
    b.text(j, 0.4, 0.9, "注意力", AX + 110, AY - 420, 50, GRAY)
    pts = []
    for i in range(101):
        u = i / 100
        y = AY - 320 + 10 * math.sin(u * 30)
        if u > 0.35:
            y += 60 * ease_in_out(clamp01((u - 0.35) / 0.1))
        if u > 0.62:
            y += 190 * ease_in_out(clamp01((u - 0.62) / 0.08))
        pts.append((AX + 20 + u * 920, y))
    b.path(j, k_cur, k_cur + 2.0, P(*pts), RED, 11, sfx="shaker", gain=0.6)

    def marks(c, kk, T):
        td = tb(j, k_drop)
        if T < td:
            return None
        g = pop_scale(T - td)
        for (u, s_) in ((0.38, "累"), (0.66, "急")):
            x = AX + 20 + u * 920
            with K.at(c, x, AY - 380, 0, g):
                box(c, 0, 0, 90, 80, NOTE_FILL, ORANGE, 5, 10)
                K.text(c, s_, 0, 2, 50, "hand", ORANGE)
        with K.at(c, AX + 880, AY - 60, 0, g):
            K.text(c, "掉线", 0, 0, 60, "hand", RED)
        return None
    ev(j, k_drop, marks, "tom", 0.8)

    GX, GY_ = cx - 470, cy + 120

    def grid(c, kk, T):
        t0 = tb(j, k_grid)
        if T < t0:
            return None
        n = min(100, int((T - t0) / 0.6 * 100) + 1)
        for i in range(n):
            x, y = GX + (i % 20) * 50, GY_ + (i // 20) * 56
            bad = i == 73 and T >= tb(j, k_x)
            if bad:
                c.drawPath(cross(x, y, 16), wb.marker(RED, 7))
            elif i != 73 or T < tb(j, k_x):
                c.drawPath(check(x, y, 15), wb.marker(GREEN, 5))
        if T >= tb(j, k_x):
            g = pop_scale(T - tb(j, k_x))
            x, y = GX + (73 % 20) * 50, GY_ + (73 // 20) * 56
            ring = skia.Path()
            ring.addCircle(x, y, 40 * g)
            c.drawPath(ring, wb.marker(RED, 7))
        K.text(c, "100次", GX + 1000 - 80, GY_ + 320, 50, "hand", GRAY, clamp01((T - t0) / 0.3))
        return None
    ev(j, k_grid, grid, "wood_high", 0.7)
    b.hit(j, k_x, "rim", 0.85, "一百个勾里一个红叉")


screen13()


# ================================================================ 屏 14：小李对着镜子敲自己脑袋；一只手拦住；“三步”
def screen14(j=14):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    MX = cx + 260
    k_mir = 0
    k_knock = kq(j, wp(21, 1, 0.3), 1)
    k_stop = nx(j, wp(22, 1, 0.4), k_knock)
    k_3 = nx(j, wp(22, 2, 0.6), k_stop)
    L.note("自责", "三步")
    b.path(j, k_mir, k_mir + 0.8, join(rect(MX, cy - 60, 300, 560, 150), P((MX - 100, cy + 220), (MX + 100, cy + 220))),
           GRAY, 8, sfx="wood_low")

    def li(c, kk, T):
        sc = pop_scale(T - tb(j, 0))
        if sc <= 0:
            return None
        x, s = cx - 140, 0.95
        hx, hy = head_of(x, GY, s)
        tk, ts = tb(j, k_knock), tb(j, k_stop)
        knock = tk <= T
        stopped = T >= ts
        hit = 0 if not knock or stopped else max(0, math.sin((T - tk) * 12))
        hand = (hx + 40, hy - 40 - 30 * hit) if knock else None
        if stopped:
            hand = (hx + 90, hy - 110)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "sad" if not stopped else "flat", rh=hand)
            # 镜子里的倒影
            c.save()
            c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(MX - 150, cy - 340, 300, 560), 150, 150))
            c.translate(2 * MX, 0)
            c.scale(-1, 1)
            s2, gy2 = 0.75, cy + 200
            hx2, hy2 = head_of(MX, gy2, s2)
            rh2 = None if hand is None else (MX + (hand[0] - hx) * s2 / s, hy2 + (hand[1] - hy) * s2 / s)
            draw_li(c, MX, gy2, s2, "sad" if not stopped else "flat", rh=rh2, alpha=0.45)
            c.restore()
            if knock and not stopped and hit > 0.8:
                K.burst(c, hx + 20, hy - 60, 0.05, ORANGE, 30, 80, 6, 6)
        if T >= tk + 0.4:
            K.text(c, "自责", cx - 400, cy - 300, 70, "hand", GRAY, clamp01((T - tk - 0.4) / 0.2))
        if stopped:
            g = pop_scale(T - ts)
            with K.at(c, hx + 170, hy - 170, -20, g):
                C.line(c, (10, 60), (60, 260), BLUE, 16)
                c.drawRoundRect(skia.Rect.MakeXYWH(-46, -30, 92, 96), 30, 30, K.paint("#FFFFFF"))
                for i, (fx, fl) in enumerate(((-33, 60), (-11, 72), (11, 70), (33, 58))):
                    C.line(c, (fx, -20), (fx, -20 - fl), BLACK, 16)
                c.drawRoundRect(skia.Rect.MakeXYWH(-46, -30, 92, 96), 30, 30, wb.marker(BLACK, 6))
                C.line(c, (-46, 20), (-80, -30), BLACK, 16)
        return None
    b.custom(j, 0, 0.3, li)
    b.hit(j, k_knock, "wood_high", 0.75, "敲自己脑袋")
    b.hit(j, k_stop, "clap", 0.8, "一只手拦住")
    stamp_ev(j, k_3, "三步", cx + 270, cy + 400, 120, -6, "kick", 0.9)
    b.shots[j].shake = [(k_3, 9.0)]
    ev(j, 2, L.pop_text("唉", cx - 330, cy - 120, 90, GRAY, j, 2), "wood_low", 0.6)


screen14()


# ================================================================ 屏 15：做法一——邮件编辑框三格依次亮：附件 → 正文 → 收件人
def screen15(j=15):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    steps_row(j, 0, 1)
    EX, EY = cx + 40, cy - 80
    k_ed = 1
    k_a = kq(j, wp(23, 1, 0.2), 2)
    k_b = nx(j, wp(23, 1, 0.75), k_a)
    k_c = nx(j, wp(23, 2, 0.6), k_b)
    ROWS = [("收件人", 3, -170), ("正文", 2, 20), ("附件", 1, 210)]
    L.note("收件人", "正文", "附件", "①", "②", "③")

    def ed(c, kk, T):
        sc = pop_scale(T - tb(j, k_ed))
        if sc <= 0:
            return None
        with at_pop(c, EX, EY, sc):
            box(c, EX, EY, 760, 600, "#FFFFFF", BLACK, 8, 14)
            for s_, order, dy in ROWS:
                kk_ = (k_a, k_b, k_c)[order - 1]
                on = T >= tb(j, kk_)
                y = EY + dy
                h = 150 if s_ == "正文" else 110
                box(c, EX + 60, y, 580, h, NOTE_FILL if on else "#FFFFFF", AMBER if on else GRAY, 7 if on else 4, 10)
                K.text(c, s_, EX - 300, y, 44, "hand", BLACK)
                with K.at(c, EX + 290, y - h / 2 + 4, 0, 1 + 0.3 * pop_scale(T - tb(j, kk_)) if on else 1):
                    c.drawCircle(0, 0, 30, K.paint(RED if on else GRAY_FILL))
                    K.text(c, "①②③"[order - 1], 0, 2, 40, "hand", "#FFFFFF" if on else GRAY)
                if on and s_ == "附件":
                    with K.at(c, EX - 140, y, 30, 1):
                        c.drawRoundRect(skia.Rect.MakeXYWH(-16, -36, 32, 72), 16, 16, wb.marker(AMBER, 6))
                    doc_card(c, EX + 40, y, 80, 90, BLUE, 2)
                if on and s_ == "正文":
                    for r in range(2):
                        C.line(c, (EX - 160, y - 30 + r * 50), (EX + 260 - r * 80, y - 30 + r * 50), GRAY, 6)
                if on and s_ == "收件人":
                    K.text(c, "王总", EX - 60, y, 46, "hand", BLUE)
        return None
    L.note("王总")
    ev(j, k_ed, ed, "pop", 0.65)
    b.hit(j, k_a, "ding", 0.8, "先加附件")
    b.hit(j, k_b, "wood_high", 0.7, "再写正文")
    b.hit(j, k_c, "rim", 0.85, "最后填收件人")

    def li(c, sc, T):
        x, s = cx - 420, 0.7
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile", rh=(x + 100 * s, GY - 290 * s + 40 * s))
        return None
    ev(j, 0, pop_fn(j, 0, li))


screen15()


# ================================================================ 屏 16：做法二——表格里几个格子挂上小锁，别人的鼠标点上去被弹开
def screen16(j=16):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    steps_row(j, 1, 1)
    SX, SY = cx + 20, cy - 120
    LOCKED = [(0, 3), (1, 3), (2, 3), (3, 3)]
    k_sh = 1
    k_lk = kq(j, wp(24, 2, 0.3), 2)
    k_poke = nx(j, wp(24, 3, 0.3), k_lk)
    k_bounce = cap(j, k_poke + 1)
    L.note("改不了")

    def sh(c, kk, T):
        sc = pop_scale(T - tb(j, k_sh))
        if sc <= 0:
            return None
        lk = T >= tb(j, k_lk)
        with at_pop(c, SX, SY, sc):
            sheet_grid(c, SX, SY, 4, 4, 180, 90, hot=set(LOCKED) if lk else None, hot_fill=NOTE_FILL, hot_line=AMBER)
            if lk:
                for i, (r, q) in enumerate(LOCKED):
                    g = pop_scale(T - tb(j, k_lk) - i * 0.1)
                    x, y = SX + (q - 1.5) * 180, SY + (r - 1.5) * 90
                    with K.at(c, x, y, 0, g * 0.8):
                        lock_icon(c, 0, 0, 1.0)
        tp, tbn = tb(j, k_poke), tb(j, k_bounce)
        if T >= tp - 0.5:
            tx, ty = SX + 1.5 * 180, SY + 0.5 * 90
            if T < tbn:
                f = ease_in_out(clamp01((T - tp + 0.5) / 0.5))
                mx, my = lerp(tx + 220, tx + 10, f), lerp(ty + 300, ty + 10, f)
            else:
                f = ease_out(clamp01((T - tbn) / 0.35))
                mx, my = lerp(tx + 10, tx + 200, f), lerp(ty + 10, ty + 220, f) - math.sin(f * math.pi) * 60
                K.text(c, "改不了", tx - 10, ty + 260, 52, "hand", RED, clamp01((T - tbn) / 0.2))
            p = P((mx, my), (mx, my + 56), (mx + 14, my + 42), (mx + 26, my + 66), (mx + 36, my + 60), (mx + 24, my + 38),
                  (mx + 42, my + 36), close=True)
            c.drawPath(p, K.paint(RED_FILL))
            c.drawPath(p, wb.marker(RED, 5))
        return None
    ev(j, k_sh, sh, "wood_low", 0.6)
    b.hit(j, k_lk, "wood_high", 0.8, "格子挂上小锁")
    b.hit(j, k_poke, "pop", 0.6, "别人的鼠标点过来")
    b.hit(j, k_bounce, "tom", 0.8, "被弹开")

    def li(c, sc, T):
        x, s = cx - 400, 0.72
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile" if T >= tb(j, k_bounce) else "flat")
        return None
    ev(j, 0, pop_fn(j, 0, li))


screen16()


# ================================================================ 屏 17：做法三——门把手上挂着工牌和钥匙，伸手开门先碰到它们
def screen17(j=17):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 540
    steps_row(j, 2, 1)
    DX, HY = cx + 200, cy + 40
    k_door = 1
    k_hang = kq(j, wp(25, 1, 0.4), 2)
    k_reach = nx(j, wp(25, 2, 0.3), k_hang)
    k_take = cap(j, k_reach + 1)
    L.note("工牌", "钥匙")
    b.path(j, k_door, k_door + 0.8, join(rect(DX, cy, 360, 900, 10), rect(DX - 140, HY, 60, 30, 10)), BLACK, 9,
           sfx="wood_low")

    def items(c, kk, T):
        th, tt = tb(j, k_hang), tb(j, k_take)
        if T < th:
            return None
        g = pop_scale(T - th)
        sw = C.wobble(T - th, 10, 10, 3) + (C.wobble(T - tb(j, k_reach), 18, 14, 4) if T >= tb(j, k_reach) else 0)
        taken = T >= tt
        if taken:
            return None
        with K.at(c, DX - 140, HY + 10, sw, g):
            C.line(c, (-10, 0), (-40, 120), BLUE, 5)
            C.line(c, (10, 0), (40, 120), BLUE, 5)
            box(c, 0, 170, 110, 130, BLUE_FILL, BLUE, 6, 10)
            K.text(c, "工牌", 0, 190, 34, "hand", BLUE)
            C.line(c, (0, 0), (60, 70), AMBER, 5)
            c.drawCircle(70, 90, 22, wb.marker(AMBER, 7))
            C.line(c, (70, 112), (70, 160), AMBER, 7)
        K.text(c, "钥匙", DX - 30, HY + 140, 34, "hand", AMBER, clamp01(g))
        return None
    ev(j, k_hang, items, "pop", 0.7)

    def li(c, sc, T):
        x, s = cx - 220, 0.9
        hx, hy = head_of(x, GY, s)
        tr, tt = tb(j, k_reach), tb(j, k_take)
        hand = None
        if T >= tr:
            f = ease_in_out(clamp01((T - tr) / 0.4))
            hand = (lerp(x + 70 * s, DX - 160, f), lerp(hy + 170 * s, HY + 60, f))
        if T >= tt:
            hand = (x + 110 * s, hy + 110 * s)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY, s, "smile" if T >= tt else "flat", rh=hand)
            if T >= tt:
                box(c, hand[0] + 20, hand[1] + 50, 90, 110, BLUE_FILL, BLUE, 6, 10)
                c.drawCircle(hand[0] + 70, hand[1] + 20, 20, wb.marker(AMBER, 7))
        return None
    ev(j, 0, pop_fn(j, 0, li))
    b.hit(j, k_reach, "wood_high", 0.7, "伸手开门")
    b.hit(j, k_take, "ding", 0.85, "先拿到工牌和钥匙")


screen17()


# ================================================================ 屏 18：小李轻松走出门，头顶的问号变成勾
def screen18(j=18):
    cx, cy = R[j]
    L.scene(j, (cx, cy + 10, Z))
    GY = cy + 520
    k_door = 0
    k_walk = 1
    k_q = kq(j, wp(26, 0, 0.4), 2)
    k_ok = nx(j, wp(26, 1, 0.6), k_q)
    L.note("？")
    b.path(j, k_door, k_door + 0.8, join(rect(cx - 380, GY - 300, 240, 600, 10), P((cx - 560, GY), (cx + 560, GY))),
           BLACK, 9, sfx="wood_low")

    def li(c, kk, T):
        sc = pop_scale(T - tb(j, k_walk))
        if sc <= 0:
            return None
        x, dy, _ = C.walk(T, tb(j, k_walk), 3.0, cx - 300, cx + 200)
        s = 0.9
        hx, hy = head_of(x, GY, s)
        ok = T >= tb(j, k_ok)
        with at_pop(c, x, GY, sc):
            draw_li(c, x, GY + dy, s, "smile", bag=True, rh=(x + 120 * s, hy - 40 * s) if ok else None)
        if T >= tb(j, k_q):
            if not ok:
                g = pop_scale(T - tb(j, k_q))
                with K.at(c, hx, hy - 170 + dy, 0, g):
                    K.text(c, "？", 0, 0, 160, "hand", GRAY)
            else:
                g = C.slam_scale(T - tb(j, k_ok))
                with K.at(c, hx, hy - 170 + dy, 0, g):
                    c.drawPath(check(0, 0, 70), wb.marker(GREEN, 16))
                sparkle(c, hx, hy - 170, T - tb(j, k_ok), YELLOW, 10, 80, 160)
        return None
    b.custom(j, k_walk, k_walk + 0.3, li, sfx="shaker", gain=0.6)
    b.hit(j, k_q, "pop", 0.65, "头顶问号")
    b.hit(j, k_ok, "ding", 0.85, "问号变成勾")

    def sun(c, sc, T):
        x, y = cx + 360, cy - 380
        with at_pop(c, x, y, sc):
            c.drawCircle(x, y, 70, K.paint(YELLOW))
            for i in range(8):
                a = math.radians(i * 45 + T * 20)
                C.line(c, (x + 90 * math.cos(a), y + 90 * math.sin(a)), (x + 130 * math.cos(a), y + 130 * math.sin(a)),
                       YELLOW, 8)
        return None
    ev(j, k_q, pop_fn(j, k_q, sun))


screen18()


# ================================================================ 屏 19：评论框里各自的小机关；小李卸下背上一摞事，肩膀松开；下一讲预告
def screen19(j=19):
    cx, cy = R[j]
    L.scene(j, (cx, cy - 60, Z))
    k_cmt = 0
    k_chips = kq(j, wp(27, 1, 0.3), 1)
    k_more = nx(j, wp(28, 1, 0.5), k_chips)
    k_load = nx(j, wp(29, 1, 0.3), k_more)
    k_drop = nx(j, wp(29, 3, 0.4), k_load)
    k_next = nx(j, wp(30, 0, 0.3), k_drop)
    b.move(j, k_load, (cx, cy + 440, Z), 1.1)
    CH = ["门口挂钥匙", "定时发送", "表格加锁", "出门清单"]
    L.note("你最常犯的手滑？", *CH, "下一讲", "每次开工", "为什么都要磨蹭半天？", "轻松一点")
    BY = cy - 300

    def cmt(c, kk, T):
        sc = pop_scale(T - tb(j, k_cmt))
        if sc <= 0:
            return None
        with K.at(c, cx + 60, BY, 0, sc):
            bubble_box(c, 0, 0, 900, 360, -1)
            K.text(c, "你最常犯的手滑？", 0, -110, 60, "hand", RED)
            for i, nm in enumerate(CH):
                g = pop_scale(T - tb(j, k_chips if i < 2 else k_more) - (i % 2) * 0.15, 0.22)
                if g <= 0:
                    continue
                x, y = -200 + (i % 2) * 400, 0 + (i // 2) * 95
                with K.at(c, x, y, 0, g):
                    w = K.text_w(nm, 44, "hand") + 40
                    K.rr(c, 0, 0, w, 76, 38, BLUE_FILL)
                    K.text(c, nm, 0, 2, 44, "hand", BLUE)
        return None
    ev(j, k_cmt, cmt, "pop", 0.7)
    b.hit(j, k_chips, "wood_high", 0.6, "评论里的小机关")
    b.hit(j, k_more, "pop", 0.6, "又冒出两条")

    LX, LY = cx - 120, cy + 560

    def li(c, kk, T):
        sc = pop_scale(T - tb(j, k_load) + 0.3)
        if sc <= 0:
            return None
        s = 0.95
        hx, hy = head_of(LX, LY, s)
        td = tb(j, k_drop)
        dropped = T >= td
        squash = 0.85 if not dropped else lerp(0.85, 1.0, ease_out(clamp01((T - td) / 0.4)))
        with at_pop(c, LX, LY, sc):
            draw_li(c, LX, LY, s, "smile" if dropped else "sad", squash=squash,
                    lh=(LX - 70 * s, hy + 80 * s) if not dropped else None,
                    rh=(LX + 70 * s, hy + 80 * s) if not dropped else None)
            f = ease_in_out(clamp01((T - td) / 0.5)) if dropped else 0
            for i in range(5):
                bx = LX + lerp(0, 220 + i * 20, f)
                by = lerp(LY - 290 * s * squash - 80 - i * 50, LY - 30 - i * 55, f)
                with K.at(c, bx, by, lerp((i % 2) * 6 - 3, (i - 2) * 4, f), 1):
                    box(c, 0, 0, 200, 46, NOTE_FILL if i % 2 else BLUE_FILL, ORANGE if i % 2 else BLUE, 5, 8)
            if dropped:
                sparkle(c, hx, hy, T - td, YELLOW, 10, 70, 150)
                K.text(c, "轻松一点", LX - 280, hy - 20, 60, "hand", GREEN, clamp01((T - td - 0.3) / 0.2))
        return None
    b.custom(j, k_load, k_load + 0.3, li, sfx="wood_low", gain=0.6)
    b.hit(j, k_drop, "ding", 0.85, "卸下一摞事")

    def nxt(c, kk, T):
        t0 = tb(j, k_next)
        sc = pop_scale(T - t0)
        if sc <= 0:
            return None
        x, y = cx + 20, cy + 770
        with K.at(c, x, y, -2, sc):
            box(c, 0, 0, 980, 230, "#FFFFFF", BLACK, 7, 18)
            K.rr(c, -380, -70, 170, 60, 30, RED)
            K.text(c, "下一讲", -380, -68, 38, "hand", "#FFFFFF")
            K.text(c, "每次开工", -130, -60, 58, "hand", BLACK)
            K.text(c, "为什么都要磨蹭半天？", -50, 40, 58, "hand", BLACK)
            with K.at(c, 380, -10, 0, 1):
                c.drawCircle(0, 0, 70, K.paint("#FFFFFF"))
                c.drawPath(wb.clock(0, 0, 70), wb.marker(BLACK, 6))
                a = math.radians(-90 + (T - t0) * 360)
                C.line(c, (0, 0), (55 * math.cos(a), 55 * math.sin(a)), RED, 6)
        return None
    ev(j, k_next, nxt, "rim", 0.8)


screen19()

# ================================================================ 收尾
L.finish(cover_shot=9, square_shot=8, notes=NOTES)
L.export(globals())
