"""《丰田模式》04 单件流：手上一堆事，为什么一件也没做完？（白板手绘 + AI 旁白，竖屏 2:3）

复刻实验：同一张桌子、同样三步（折 / 装 / 封）、同一块秒表，小李一批一批做，小王一个一个做，
两条泳道并排计时，结果当场看见；再用“信纸折大了”看谁先发现问题。
- 0–3 秒：系列开场“丰田模式”四字，缓推到十个卡在一半、逐个闪红的进度条（钩子“全卡住”）；
- drop：第 2 屏实验台摆好、三步卡片就位，秒表砸下（“开始计时”）；
- 实验三屏（3–6）用同一套布局：左边人、桌上三个工位 + 交付筐、右上角秒表一直在走；
- 书中做法：车间每个工位手里只有一台车；库存像河水，水位一降石头（问题）露出来；
- 职场 / 家里三例 → 排队出不去 → 三步做法 → 下班做完一件 → 评论区 + 下一讲预告。
文案见 fengtian/PLAN.md「### 04 单件流」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_leader, draw_li, draw_worker,
                             pop_scale, wobble)
from whiteboard import engine as wb
from whiteboard.engine import P, arrow, book, check, circle, cross, join, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "小实验", 2),
    ([4], "小实验 · 小李", 3),
    ([5], "小实验 · 小王", 4),
    ([6], "小实验 · 结果", 5),
    ([7, 8], "小实验 · 结果", 6),
    ([9], "丰田模式 · 书中做法", 7),
    ([10, 11], "丰田模式 · 书中做法", 8),
    ([12], "书中观点", 9),
    ([13, 14], "说回我们自己", 10),
    ([15], "说回我们自己", 11),
    ([16], "说回我们自己", 12),
    ([17, 18], "说回我们自己", 13),
    ([19, 20], "说回我们自己", 14),
    ([21], "做法一 · 示意", 15),
    ([22], "做法二 · 示意", 16),
    ([23], "做法三 · 示意", 17),
    ([24, 25], "做完的那一件", 18),
    ([26, 27, 28, 29], "评论区见", 19),
]

THEME = FT.get("04")          # 本讲样式（fengtian/theme.py）：牛皮纸、开场 bars、转场 drop
L = C.Lesson("04", SCREENS, drop_screen=2, board_size=(5000, 13000), theme=THEME)
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

# 各屏在白板上的区块中心（相邻屏相距 1600，蛇形排列）
R = [(2600, 800), (900, 900), (900, 2500), (2500, 2500), (4100, 2500), (4100, 4100), (2500, 4100), (900, 4100),
     (900, 5700), (2500, 5700), (4100, 5700), (4100, 7300), (2500, 7300), (900, 7300), (900, 8900), (2500, 8900),
     (4100, 8900), (4100, 10500), (2500, 10500), (900, 10500)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 2——建立连续的作业流程，使问题浮现（Create Continuous Process Flow to Bring Problems to the Surface）；"
    "单件流对比批量生产；“库存像河水，水位一降石头露出来”为精益常用比方。",
    "叠信封实验为示意（十个信封、一分钟等数字不是数据）；小李、小王、组长、领导为虚构人物。",
]


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
def at_pop(c, x, y, sc):
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    c.translate(-x, -y)
    try:
        yield
    finally:
        c.restore()


def label(j, k0, s, x, y, size=64, color=BLACK, sfx=None):
    b.text(j, k0, k0 + 0.1 + 0.12 * len(s), s, x, y, size, color, sfx=sfx)


def ev(j, k, fn, sfx=None, gain=0.8, dur=0.3):
    b.custom(j, k, k + dur, fn, sfx=sfx, gain=gain)


# ================================================================ 道具

ENV_FILL, ENV_LINE, ENV_FLAP = "#F6E7C8", "#A9773E", "#EBD3A6"


def envelope(c, x, y, s=1.0, sealed=False, letter=False, alpha=1.0, simple=False, big_letter=False):
    """信封（正视）：(x, y) 为中心，宽 130·s。sealed 封好（盖红点）；letter 装了信（露出信纸上沿）。"""
    w, h = 130 * s, 86 * s
    if not sealed and not simple:
        flap = P((x - w / 2, y - h / 2), (x, y - h / 2 - 44 * s), (x + w / 2, y - h / 2), close=True)
        c.drawPath(flap, K.paint(ENV_FILL, alpha))
        c.drawPath(flap, wb.marker(ENV_LINE, 5, alpha))
    if letter and not sealed and not simple:
        lw = (w + 30 * s) if big_letter else (w - 32 * s)
        r = skia.Rect.MakeXYWH(x - lw / 2, y - h / 2 - 28 * s, lw, 50 * s)
        c.drawRect(r, K.paint("#FFFFFF", alpha))
        c.drawRect(r, wb.marker(BLACK, 4, alpha))
    body = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(body, 6 * s, 6 * s, K.paint(ENV_FILL, alpha))
    c.drawRoundRect(body, 6 * s, 6 * s, wb.marker(ENV_LINE, 5, alpha))
    if sealed:
        flap = P((x - w / 2, y - h / 2), (x, y + h * 0.12), (x + w / 2, y - h / 2), close=True)
        c.drawPath(flap, K.paint(ENV_FLAP, alpha))
        c.drawPath(flap, wb.marker(ENV_LINE, 5, alpha))
        c.drawCircle(x, y + h * 0.04, 11 * s, K.paint(RED, alpha))
    else:
        c.drawPath(P((x - w / 2, y - h / 2), (x, y + h * 0.12), (x + w / 2, y - h / 2)), wb.marker(ENV_LINE, 3, alpha * 0.5))


def folded(c, x, y, s=1.0, big=False, alpha=1.0, color=BLACK):
    """折好的信纸（三折后的长条）。big=True 折大了。"""
    w, h = (170 if big else 108) * s, 40 * s
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRect(r, K.paint("#FFFFFF", alpha))
    c.drawRect(r, wb.marker(color, 5, alpha))
    c.drawLine(x - w / 2 + 8 * s, y, x + w / 2 - 8 * s, y, wb.marker("#9AA0AC", 3, alpha))


def sheet(c, x, y, s=1.0, alpha=1.0):
    """一张没折的信纸。"""
    p = wb.doc(x, y, 92 * s, 118 * s, 3)
    c.drawPath(p, K.paint("#FFFFFF", alpha))
    c.drawPath(p, wb.marker(BLACK, 5, alpha))


def stack(c, kind, x, yb, n, s=0.85, big=False, alpha=1.0):
    """一摞：kind = "sheet" / "fold" / "env" / "sealed"；(x, yb) 为底部中点。"""
    for i in range(n):
        dx = ((i * 37) % 9 - 4) * s
        if kind == "fold":
            folded(c, x + dx, yb - 20 * s - i * 14 * s, s, big, alpha)
        elif kind == "sheet":
            sheet(c, x + dx, yb - 59 * s - i * 9 * s, s, alpha)
        else:
            top = i == n - 1
            envelope(c, x + dx, yb - 43 * s - i * 13 * s, s, sealed=kind == "sealed", letter=True, alpha=alpha,
                     simple=not top)


def stopwatch(c, x, y, r, frac, alpha=1.0):
    """秒表：frac 为指针转过的圈数比例（可大于 1）。"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 16 * r / 100, y - r - 32 * r / 100, 32 * r / 100, 26 * r / 100), 5, 5,
                    K.paint(BLACK, alpha))
    c.drawCircle(x, y, r, K.paint("#FFFFFF", alpha))
    f = frac % 1.0
    if f > 0:
        sweep = skia.Path()
        sweep.moveTo(x, y)
        sweep.arcTo(skia.Rect.MakeXYWH(x - r * 0.86, y - r * 0.86, r * 1.72, r * 1.72), -90, 360 * f, False)
        sweep.close()
        c.drawPath(sweep, K.paint("#F6C3BE", 0.8 * alpha))
    c.drawPath(wb.clock(x, y, r), wb.marker(BLACK, 8, alpha))
    a = -math.pi / 2 + 2 * math.pi * frac
    c.drawLine(x, y, x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78, wb.marker(RED, 7, alpha))
    c.drawCircle(x, y, 8 * r / 100, K.paint(RED, alpha))


def pbar(c, x0, y, w, h, f, fill="#BFD5F2", line=BLACK, alpha=1.0):
    r = skia.Rect.MakeXYWH(x0, y - h / 2, w, h)
    c.drawRoundRect(r, h / 2, h / 2, K.paint("#FFFFFF", alpha))
    if f > 0:
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(r, h / 2, h / 2), doAntiAlias=True)
        c.drawRect(skia.Rect.MakeXYWH(x0, y - h / 2, w * f, h), K.paint(fill, alpha))
        c.restore()
    c.drawRoundRect(r, h / 2, h / 2, wb.marker(line, 5, alpha))


def tray(c, x, yb, w=150, alpha=1.0):
    p = P((x - w / 2, yb - 70), (x - w / 2 + 14, yb), (x + w / 2 - 14, yb), (x + w / 2, yb - 70))
    c.drawPath(P((x - w / 2, yb - 70), (x - w / 2 + 14, yb), (x + w / 2 - 14, yb), (x + w / 2, yb - 70), close=True),
               K.paint("#E4EDFA", alpha))
    c.drawPath(p, wb.marker(BLUE, 7, alpha))


def phone(c, x, y, s=1.0, down=False, alpha=1.0, rot=0.0):
    with K.at(c, x, y, rot, s):
        r = skia.Rect.MakeXYWH(-55, -95, 110, 190)
        c.drawRoundRect(r, 18, 18, K.paint("#5A6170" if down else "#FFFFFF", alpha))
        c.drawRoundRect(r, 18, 18, wb.marker(BLACK, 7, alpha))
        if not down:
            c.drawRect(skia.Rect.MakeXYWH(-42, -72, 84, 136), K.paint("#DCE8F7", alpha))
            c.drawCircle(0, 80, 6, K.paint(BLACK, alpha))


def car(c, x, yb, s=1.0, alpha=1.0, fill="#DDE3EA"):
    """车身（侧视）：(x, yb) 为轮底中点。"""
    body = P((x - 110 * s, yb - 22 * s), (x - 110 * s, yb - 62 * s), (x - 55 * s, yb - 66 * s), (x - 30 * s, yb - 100 * s),
             (x + 45 * s, yb - 100 * s), (x + 75 * s, yb - 64 * s), (x + 110 * s, yb - 58 * s), (x + 110 * s, yb - 22 * s),
             close=True)
    c.drawPath(body, K.paint(fill, alpha))
    c.drawPath(body, wb.marker(BLACK, 6, alpha))
    c.drawPath(P((x - 20 * s, yb - 92 * s), (x - 20 * s, yb - 66 * s), (x + 60 * s, yb - 66 * s), (x + 40 * s, yb - 92 * s),
                 close=True), wb.marker(BLACK, 4, alpha))
    for dx in (-62, 62):
        c.drawCircle(x + dx * s, yb - 20 * s, 20 * s, K.paint(BLACK, alpha))
        c.drawCircle(x + dx * s, yb - 20 * s, 8 * s, K.paint("#FFFFFF", alpha))


def belt(x0, x1, y):
    """传送带：两条线 + 滚轮。"""
    parts = [P((x0, y), (x1, y)), P((x0, y + 36), (x1, y + 36))]
    n = int((x1 - x0) // 90)
    for i in range(n + 1):
        parts.append(circle(x0 + 18 + i * (x1 - x0 - 36) / n, y + 18, 14))
    return join(*parts)


def table(x0, x1, y, leg=140):
    return join(P((x0, y), (x1, y)), P((x0 + 20, y), (x0 + 20, y + leg)), P((x1 - 20, y), (x1 - 20, y + leg)))


def li_working(x, y, s, t_start, t_stop, mood_fn=None):
    """小李 / 小王 干活的手：双手在桌前上下忙。返回 (lh, rh) 函数。"""
    def hands(T):
        hy = y - 290 * s
        on = t_start <= T < t_stop
        d = 14 * math.sin(T * 13) if on else 0.0
        return (x + 60 * s, hy + 150 * s + d), (x + 120 * s, hy + 140 * s - d)
    return hands


def draw_wang(c, x, y, s, lh=None, rh=None, mood="flat", head_dy=0.0):
    """同事小王（办公室，不戴安全帽）：照抄第 06/07 讲造型。"""
    d_lh, d_rh = C.rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s + head_dy
    sh = (x, y - 290 * s + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, ft, BLUE, 10)
    C.line(c, sh, lh, BLUE, 10)
    C.line(c, sh, rh, BLUE, 10)
    torso = skia.Rect.MakeLTRB(x - 42 * s, y - 235 * s, x + 42 * s, y - 105 * s)
    c.drawRoundRect(torso, 18 * s, 18 * s, K.paint("#FFFFFF"))
    c.drawRoundRect(torso, 18 * s, 18 * s, wb.marker(BLUE, 7))
    badge = skia.Rect.MakeXYWH(x - 20 * s, y - 180 * s, 40 * s, 30 * s)
    c.drawRoundRect(badge, 4, 4, K.paint("#DCE8F7"))
    c.drawRoundRect(badge, 4, 4, wb.marker(BLUE, 4))
    c.drawRoundRect(skia.Rect.MakeLTRB(x - 54 * s, hy - 46 * s, x + 54 * s, hy + 40 * s), 26 * s, 26 * s, K.paint("#2E2A28"))
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF"))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 9))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(x - 50 * s, hy - 52 * s, 100 * s, 72 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint("#2E2A28"))
    c.drawCircle(x + 36 * s, hy - 24 * s, 9 * s, K.paint(ORANGE))
    C._eyes_mouth(c, x, hy + 4 * s, s, mood, 1.0)


# ================================================================ 屏 0：系列开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：十件事都开了头，进度条全卡在一半
cx, cy = R[1]
j = L.scene(1, (cx, cy + 20, Z))
LI1 = (cx - 400, cy + 400, 0.9)
CLK1 = (cx - 400, cy - 300, 115)
BX0, BW1, BH1 = cx - 190, 620, 34
BY = [cy - 470 + i * 62 for i in range(10)]
b.path(j, 0, 0.8, wb.clock(*CLK1), BLACK, 9, sfx="wood_high")
k_day = kq(j, wt(0, 0, 0.6), lo=2)
k_bar0 = kq(j, wt(0, 1, 0.0), lo=k_day + 1)
k_none = kq(j, wt(0, 2, 0.6), lo=k_bar0 + 5)
k_off = kq(j, wt(1, 0, 0.5), lo=k_none + 1)
k_red = kq(j, wt(1, 1, 0.25), lo=k_off + 1)
k_stuck = kq(j, wt(1, 1, 0.95), lo=k_red + 2)


def clock1(c, kk, T):
    x, y, r = CLK1
    t0, t1 = tb(1, k_day), tb(1, k_off)
    f = ease_in_out(clamp01((T - t0) / max(0.1, t1 - t0)))
    hour = 9 + 9 * f
    c.drawCircle(x, y, r, K.paint("#FFFFFF"))
    c.drawPath(wb.clock(x, y, r), wb.marker(BLACK, 9))
    c.drawPath(wb.hands_at(x, y, r, hour % 12, (hour * 60) % 60), wb.marker(RED if f > 0 else BLACK, 9))
    K.text(c, f"{int(hour):02d}:{int((hour * 60) % 60):02d}", x, y + r + 58, 62, "sans_medium", RED if f >= 1 else BLACK)
    return None


L.note("09:00", "18:00")
b.custom(j, 0.8, 0.9, clock1)
b.hit(j, k_off, "ding", 0.7, "钟走到下班")
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI1,
                             mood=lambda T: "sad" if T >= tb(1, k_red) else "flat",
                             lh=lambda T: ((LI1[0] - 60, LI1[1] - 290 * LI1[2] - 10) if T >= tb(1, k_stuck)
                                           else (LI1[0] - 70 * LI1[2], LI1[1] - 120 * LI1[2])),
                             rh=lambda T: ((LI1[0] + 60, LI1[1] - 290 * LI1[2] - 10) if T >= tb(1, k_stuck)
                                           else (LI1[0] + 110 * LI1[2], LI1[1] - 290 * LI1[2] + 120))), sfx="pop")
label(j, 1.4, "小李", LI1[0], LI1[1] + 85, 64)


def bars1(c, kk, T):
    for i, y in enumerate(BY):
        t0 = tb(1, k_bar0 + i * 0.5)
        sc = pop_scale(T - t0, 0.22)
        if sc <= 0:
            continue
        f = 0.5 * ease_out(clamp01((T - t0) / 0.45))
        t_r = tb(1, k_red) + i * 0.1
        red = T >= t_r
        blink = 1.0
        if red and T - t_r < 0.6:
            blink = 0.55 + 0.45 * math.cos((T - t_r) * 20)
        with at_pop(c, BX0, y, sc):
            pbar(c, BX0, y, BW1, BH1, f, fill="#F6C3BE" if red else "#BFD5F2", line=RED if red else BLACK, alpha=blink)
    return None


b.custom(j, k_bar0, k_bar0 + 0.3, bars1)
for i in range(0, 10, 2):
    b.hit(j, k_bar0 + i // 2, ("wood_high", "wood_low")[(i // 2) % 2], 0.55, "进度条开了头")
b.custom(j, k_none, k_none + 0.3, L.pop_text("做完：0", cx + 120, cy + 200, 80, RED, j, k_none), sfx="pop")
b.hit(j, k_red, "rim", 0.7, "进度条逐个闪红")
b.hit(j, k_red + 1, "rim", 0.55, "进度条逐个闪红")
b.custom(j, k_stuck, k_stuck + 0.3, L.stamp("全卡住", cx + 120, cy - 180, 120, j, k_stuck), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_stuck, 12.0)]

# ================================================================ 屏 2（drop）：实验台——十张信纸、十个信封、三步卡片，秒表砸下
cx, cy = R[2]
j = L.scene(2, (cx, cy + 20, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
TB2 = cy + 40


def beaker(x, y):
    return join(P((x - 30, y - 50), (x - 30, y - 10), (x - 60, y + 50), (x + 60, y + 50), (x + 30, y - 10), (x + 30, y - 50)),
                P((x - 42, y - 50), (x + 42, y - 50)), P((x - 45, y + 25), (x + 45, y + 25)))


b.path(j, 0, 0.8, table(cx - 520, cx + 520, TB2, 130), BLACK, 9, sfx="wood_high")
b.path(j, 1, 1.6, beaker(cx - 450, cy - 470), GREEN, 8, sfx="wood_low")
label(j, 1.6, "小实验", cx - 280, cy - 470, 80, GREEN)
k_env = kq(j, wt(2, 1, 0.25), lo=2)
b.custom(j, k_env, k_env + 0.3, pop_fn(j, k_env, lambda c, sc, T: _stack_pop(c, sc, "sheet", cx - 260, TB2)), sfx="wood_low")
b.custom(j, k_env, k_env + 0.3, L.pop_text("×10", cx - 260, cy - 235, 72, BLUE, j, k_env))
b.custom(j, k_env + 1, k_env + 1.3, pop_fn(j, k_env + 1, lambda c, sc, T: _stack_pop(c, sc, "env0", cx + 230, TB2)),
         sfx="wood_high")
b.custom(j, k_env + 1, k_env + 1.3, L.pop_text("×10", cx + 230, cy - 235, 72, BLUE, j, k_env + 1))


def _stack_pop(c, sc, kind, x, yb):
    with at_pop(c, x, yb, sc):
        if kind == "env0":
            for i in range(10):
                envelope(c, x + ((i * 37) % 9 - 4), yb - 40 - i * 12, 0.95, simple=i < 9)
        else:
            stack(c, kind, x, yb, 10, 1.0)


STEP_X = [cx - 370, cx, cx + 370]
STEP_Y = cy + 330
STEP_T = ["折", "装", "封"]


def step_card(i):
    def draw(c, sc, T):
        x, y = STEP_X[i], STEP_Y
        with at_pop(c, x, y, sc):
            r = skia.Rect.MakeXYWH(x - 115, y - 110, 230, 220)
            c.drawRoundRect(r, 20, 20, K.paint("#FFFFFF"))
            c.drawRoundRect(r, 20, 20, wb.marker(BLUE, 7))
            if i == 0:
                folded(c, x, y - 30, 1.0)
                c.drawPath(arrow((x - 60, y - 80), (x - 10, y - 58), 0.3, 18), wb.marker(ORANGE, 5))
            elif i == 1:
                envelope(c, x, y - 18, 0.9, letter=True)
            else:
                envelope(c, x, y - 30, 0.9, sealed=True)
            K.text(c, STEP_T[i], x, y + 65, 62, "hand", BLUE)
    return draw


L.note(*STEP_T)
k_s = [kq(j, wt(3, 0, 0.8), lo=k_env + 2)]
k_s.append(kq(j, wt(3, 1, 0.3), lo=k_s[0] + 1))
k_s.append(kq(j, wt(3, 2, 0.2), lo=k_s[1] + 1))
for i in range(3):
    b.custom(j, k_s[i], k_s[i] + 0.3, pop_fn(j, k_s[i], step_card(i)), sfx="pop", gain=0.7)
    if i:
        b.path(j, k_s[i] + 0.1, k_s[i] + 0.4, arrow((STEP_X[i - 1] + 125, STEP_Y), (STEP_X[i] - 125, STEP_Y), 0, 22), BLACK, 7)
SW2 = (cx + 380, cy - 330, 105)


def watch2(c, kk, T):
    x, y, r = SW2
    t0 = tb(2, KD)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    with K.at(c, x, y, 0, sc):
        stopwatch(c, 0, 0, r, max(0.0, (T - t0) / 6.0))
    return None


b.custom(j, KD, KD + 0.3, watch2, sfx="kick", gain=0.95)
b.custom(j, KD, KD + 0.3, L.stamp("开始计时", cx - 40, cy - 350, 84, j, KD, color=RED, rot=-6))

# ================================================================ 屏 3/4：实验台（同一布局）——左边人，桌上三个工位 + 交付筐，右上角秒表在走
TAB_Y = 150
ST_DX = [-170, 50, 270]
TRAY_DX = 470


def bench(j, cx, cy, who, title, k_title, title_color):
    """画实验台：桌子、工位名、交付筐、秒表（接着上一屏走）、标题。"""
    b.path(j, 0, 0.8, table(cx - 290, cx + 560, cy + TAB_Y, 150), BLACK, 9, sfx="wood_high")
    for dx, t in zip(ST_DX, STEP_T):
        b.text(j, 0.6, 0.8, t, cx + dx, cy + TAB_Y + 70, 58, BLUE)
    b.text(j, 0.8, 1.0, "交出", cx + TRAY_DX, cy + TAB_Y + 70, 58, GREEN)

    def tray_fn(c, kk, T):
        tray(c, cx + TRAY_DX, cy + TAB_Y - 4, 150)
        return None
    b.custom(j, 0.8, 0.9, tray_fn)

    def watch(c, kk, T):
        stopwatch(c, cx + 470, cy - 465, 62, (T - tb(2, KD)) / 6.0)
        return None
    b.custom(j, 0, 0.1, watch)
    b.custom(j, k_title, k_title + 0.3, L.pop_text(title, cx + 40, cy - 465, 88, title_color, j, k_title), sfx="pop")
    return (cx - 440, cy + 400, 0.9)


# ---------------------------------------------------------------- 屏 3：小李一批一批：十张全折完 → 全装 → 全封
cx, cy = R[3]
j = L.scene(3, (cx, cy + 20, Z))
k_t3 = kq(j, wt(4, 0, 0.25), lo=1)
P3 = bench(j, cx, cy, "小李", "一批一批做", k_t3, RED)
k_f3 = kq(j, wt(4, 0, 0.75), lo=k_t3 + 1)
k_i3 = kq(j, wt(4, 1, 0.1), lo=k_f3 + 2)
k_c3 = kq(j, wt(4, 2, 0.1), lo=k_i3 + 2)
PH3 = {}


def batch3(c, kk, T):
    """三个工位的摞：每个阶段 1.5 拍内 10 张全部从前一摞搬到后一摞。"""
    cx, cy = R[3]
    yb = cy + TAB_Y - 3
    tf, ti, tc = tb(3, k_f3), tb(3, k_i3), tb(3, k_c3)
    dur = tb(3, k_f3 + 1.5) - tf

    def n_of(t0):
        return int(round(10 * clamp01((T - t0) / dur)))
    nf, ni, nc = n_of(tf), n_of(ti), n_of(tc)
    sheets = 10 - nf
    folds = nf - ni
    envs = ni - nc
    if sheets:
        stack(c, "sheet", cx + ST_DX[0] - 55, yb, sheets, 0.75)
    if folds:
        stack(c, "fold", cx + ST_DX[0] + 45, yb, folds, 0.85)
    if envs:
        stack(c, "env", cx + ST_DX[1], yb, envs, 0.8)
    if nc:
        stack(c, "sealed", cx + ST_DX[2], yb, nc, 0.8)
    return None


b.custom(j, 1, 1.1, batch3)
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *P3[:3],
                             mood=lambda T: "sad" if T >= tb(3, k_c3 + 1) else "flat",
                             lh=lambda T: li_working(*P3, tb(3, k_f3), tb(3, k_c3 + 1.5))(T)[0],
                             rh=lambda T: li_working(*P3, tb(3, k_f3), tb(3, k_c3 + 1.5))(T)[1]), sfx="pop")
label(j, 1.4, "小李", P3[0], P3[1] + 85, 64)
for k_, n_ in ((k_f3, "全折"), (k_i3, "全装"), (k_c3, "全封")):
    b.hit(j, k_, "wood_high", 0.7, n_)
    b.hit(j, k_ + 1, "wood_low", 0.55, n_)
b.custom(j, k_f3, k_f3 + 0.3, L.pop_text("0", cx + TRAY_DX, cy - 30, 110, RED, j, k_f3))

# ---------------------------------------------------------------- 屏 4：小王一个一个：折一张、装一个、封一个、放进筐，再做下一个
cx, cy = R[4]
j = L.scene(4, (cx, cy + 20, Z))
k_t4 = kq(j, wt(5, 0, 0.25), lo=1)
P4 = bench(j, cx, cy, "小王", "一个一个做", k_t4, GREEN)
k_fold4 = kq(j, wt(5, 0, 0.85), lo=k_t4 + 1)
k_ins4 = kq(j, wt(5, 1, 0.4), lo=k_fold4 + 1)
k_seal4 = kq(j, wt(5, 2, 0.4), lo=k_ins4 + 1)
k_out4 = kq(j, wt(5, 3, 0.15), lo=k_seal4 + 1)
N_EXTRA4 = max(0, min(2, nbeats(4) - 4 - k_out4))
KS_OUT4 = [k_out4 + i for i in range(N_EXTRA4 + 1)]


def single4(c, kk, T):
    """一个信封从工位走到筐里；第一轮每步一拍，后面几轮一拍走完一整轮。"""
    cx, cy = R[4]
    yb = cy + TAB_Y - 3
    xs = [cx + d for d in ST_DX] + [cx + TRAY_DX]
    done = sum(1 for k_ in KS_OUT4 if T >= tb(4, k_))
    busy = done < len(KS_OUT4) and T >= (tb(4, k_fold4) if done == 0 else tb(4, KS_OUT4[done - 1])) - 0.3
    left = 10 - done - (1 if busy else 0)
    if left > 0:
        stack(c, "sheet", xs[0] - 55, yb, left, 0.75)
    for i in range(done):
        envelope(c, xs[3] + (i % 2) * 14 - 7, yb - 40 - i * 12, 0.8, sealed=True, simple=i < done - 1)
    if not busy:
        return None
    if done == 0:
        keys = [tb(4, k_fold4), tb(4, k_ins4), tb(4, k_seal4), tb(4, k_out4)]
    else:
        t0, t1 = tb(4, KS_OUT4[done - 1]), tb(4, KS_OUT4[done])
        keys = [lerp(t0, t1, f) for f in (0.25, 0.5, 0.75, 1.0)]
    states = [("sheet", xs[0] - 55, yb - 80), ("fold", xs[0] + 45, yb - 20), ("env", xs[1], yb - 40),
              ("sealed", xs[2], yb - 40), ("sealed", xs[3], yb - 40 - done * 12)]
    i = sum(1 for t_ in keys if T >= t_ - 0.3)
    a_, z_ = states[i - 1], states[i]
    g = ease_in_out(clamp01((T - (keys[i - 1] - 0.3)) / 0.3))
    x = lerp(a_[1], z_[1], g)
    y = lerp(a_[2], z_[2], g) - math.sin(g * math.pi) * 60
    kind = z_[0] if g > 0.5 else a_[0]
    if kind == "sheet":
        sheet(c, x, y, 0.75)
    elif kind == "fold":
        folded(c, x, y, 0.85)
    else:
        envelope(c, x, y, 0.8, sealed=kind == "sealed", letter=True)
    return None


b.custom(j, 1, 1.1, single4)
b.custom(j, 1, 1.3, L.figure(draw_wang, j, 1, *P4[:3],
                             mood=lambda T: "smile" if T >= tb(4, k_out4) else "flat",
                             lh=lambda T: li_working(*P4, tb(4, k_fold4) - 0.3, tb(4, KS_OUT4[-1]))(T)[0],
                             rh=lambda T: li_working(*P4, tb(4, k_fold4) - 0.3, tb(4, KS_OUT4[-1]))(T)[1]), sfx="pop")
label(j, 1.4, "小王", P4[0], P4[1] + 85, 64, BLUE)
b.hit(j, k_fold4, "wood_high", 0.7, "折一张")
b.hit(j, k_ins4, "wood_low", 0.7, "装一个")
b.hit(j, k_seal4, "clap", 0.6, "封一个")


def count4(n, k_):
    cx, cy = R[4]
    def draw(c, sc, T):
        nxt = [k2 for k2 in KS_OUT4 if k2 > k_]
        if nxt and T >= tb(4, nxt[0]):
            return
        with K.at(c, cx + TRAY_DX, cy - 30, 0, sc):
            K.text(c, str(n), 0, 0, 110, "hand", GREEN)
    return draw


for i, k_ in enumerate(KS_OUT4):
    L.note(str(i + 1))
    b.custom(j, k_, k_ + 0.3, pop_fn(j, k_, count4(i + 1, k_)), sfx="ding" if i == 0 else "pop", gain=0.75)

# ================================================================ 屏 5：并排计时——小王一分钟交出第一个，小李快结束才有第一个
cx, cy = R[5]
j = L.scene(5, (cx, cy + 20, Z))
AX0, AX1 = cx - 280, cx + 500
LANE = {"wang": cy - 170, "li": cy + 230}
k_q5 = kq(j, wt(6, 0, 0.05), lo=1)
k_p0 = kq(j, wt(6, 0, 0.3), lo=k_q5 + 1)
k_w1 = kq(j, wt(6, 0, 0.85), lo=k_p0 + 1)
k_l1 = kq(j, wt(6, 2, 0.15), lo=k_w1 + 2)
k_pe = k_l1 + 1
PL_KEYS = [(k_p0, 0.0), (k_w1, 0.1), (k_l1, 0.8), (k_pe, 1.0)]


def play5(T):
    """播放头位置 0–1（分段线性，关键点落在拍上）。"""
    if T < tb(5, PL_KEYS[0][0]):
        return 0.0
    for (ka, pa), (kz, pz) in zip(PL_KEYS, PL_KEYS[1:]):
        ta, tz = tb(5, ka), tb(5, kz)
        if T < tz:
            return lerp(pa, pz, (T - ta) / (tz - ta))
    return 1.0


def xm(p):
    return lerp(AX0, AX1, p)


b.custom(j, k_q5, k_q5 + 0.3, L.pop_text("结果呢？", cx - 140, cy - 470, 90, BLACK, j, k_q5), sfx="pop")


def watch5(c, kk, T):
    cx, cy = R[5]
    stopwatch(c, cx + 450, cy - 470, 62, (T - tb(2, KD)) / 6.0)
    return None


b.custom(j, 0, 0.1, watch5)
b.path(j, 0, 0.8, join(P((AX0, LANE["wang"]), (AX1, LANE["wang"])), P((AX0, LANE["li"]), (AX1, LANE["li"]))), "#8A8F99", 7,
       sfx="wood_high")
b.text(j, 0.8, 1.0, "0", AX0, cy - 330, 54, "#6B7080")
b.text(j, 1.0, 1.5, "10分钟", AX1 - 40, cy - 330, 54, "#6B7080")


def avatar(x, y, fn, bg, name, color):
    def draw(c, sc, T):
        with at_pop(c, x, y, sc):
            c.drawCircle(x, y, 78, K.paint(bg))
            c.save()
            c.clipRect(skia.Rect.MakeXYWH(x - 78, y - 78, 156, 156))
            if fn is draw_li:
                fn(c, x, y + 150, 0.62, "smile")
            else:
                fn(c, x, y + 150, 0.62, mood="smile")
            c.restore()
            c.drawCircle(x, y, 78, wb.marker(color, 6))
            K.text(c, name, x, y + 118, 52, "hand", color)
    return draw


L.note("小王", "小李")
b.custom(j, 1, 1.3, pop_fn(j, 1, avatar(cx - 430, LANE["wang"], draw_wang, "#E4EDFA", "小王", BLUE)), sfx="pop", gain=0.6)
b.custom(j, 1.5, 1.8, pop_fn(j, 1.5, avatar(cx - 430, LANE["li"], draw_li, "#F3E6CF", "小李", BLACK)))


def lanes5(c, kk, T):
    cx, cy = R[5]
    p = play5(T)
    if T < tb(5, k_p0):
        return None
    for m in range(1, 11):                                    # 小王：每分钟交一个
        pm = m / 10
        if p >= pm - 1e-6:
            tm = tb(5, k_w1) if m == 1 else None
            sc = pop_scale(T - tm) if tm is not None else 1.0
            with at_pop(c, xm(pm), LANE["wang"] - 50, sc):
                envelope(c, xm(pm), LANE["wang"] - 50, 0.45, sealed=True)
    for m in range(10):                                       # 小李：0.8 之后一下子交出一摞
        pm = 0.8 + m * 0.022
        if p >= pm:
            sc = pop_scale(T - tb(5, k_l1) - m * 0.03, 0.22)
            x = xm(0.82) + (m % 2) * 6
            with at_pop(c, x, LANE["li"] - 40, sc):
                envelope(c, x, LANE["li"] - 40 - m * 9, 0.45, sealed=True, simple=m < 9)
    x = xm(p)                                                 # 播放头
    c.drawLine(x, cy - 290, x, cy + 330, wb.marker(RED, 6, 0.85))
    c.drawPath(P((x - 16, cy - 300), (x + 16, cy - 300), (x, cy - 276), close=True), K.paint(RED))
    return None


b.custom(j, k_p0, k_p0 + 0.3, lanes5, sfx="shaker", gain=0.6)
b.custom(j, k_w1, k_w1 + 0.3, L.pop_text("1分钟", xm(0.1) + 20, LANE["wang"] + 60, 64, GREEN, j, k_w1), sfx="ding")
b.custom(j, k_l1, k_l1 + 0.3, L.pop_text("快结束", xm(0.82), LANE["li"] + 60, 64, RED, j, k_l1), sfx="tom", gain=0.8)

# ================================================================ 屏 6：信纸折大了——小李十张都折完才发现；小王第一个就塞不进，马上改
cx, cy = R[6]
j = L.scene(6, (cx, cy + 20, Z))
p_div = skia.Path()
p_div.moveTo(cx, cy - 380)
p_div.lineTo(cx, cy + 600)
b.path(j, 0, 0.6, p_div, "#9AA0AC", 6, sfx="wood_low")
b.text(j, 0.6, 0.9, "小李", cx - 300, cy - 330, 66, BLACK)
b.text(j, 0.9, 1.2, "小王", cx + 300, cy - 330, 66, BLUE)
k_t6 = kq(j, wt(7, 1, 0.2), lo=2)
k_try = kq(j, wt(7, 2, 0.45), lo=k_t6 + 1)
k_x6 = k_try + 1
k_try2 = kq(j, wt(8, 0, 0.6), lo=k_x6 + 1)
k_fix = kq(j, wt(8, 1, 0.3), lo=k_try2 + 1)
k_ok6 = k_fix + 1
PILE6 = (cx - 330, cy + 150)
ENV6L = (cx - 200, cy - 150)
ENV6R = (cx + 300, cy - 150)
ONE6 = (cx + 300, cy + 130)
b.custom(j, k_t6, k_t6 + 0.3, L.slam_text("折大了", cx, cy - 480, 100, RED, j, k_t6), sfx="rim", gain=0.7)


def left6(c, kk, T):
    t_try = tb(6, k_try)
    sc = pop_scale(T - tb(6, 1))
    if sc <= 0:
        return None
    with at_pop(c, PILE6[0], PILE6[1], sc):
        envelope(c, *ENV6L, 1.0)
        n = 10
        top_moving = t_try - 0.35 <= T < t_try + 0.5
        stack(c, "fold", PILE6[0], PILE6[1], n - (1 if top_moving else 0), 0.9, big=True)
    if t_try - 0.35 <= T < t_try + 0.5:                        # 最上面那张试着塞进信封，弹回来
        if T < t_try:
            g = ease_in_out(clamp01((T - (t_try - 0.35)) / 0.35))
            x, y = lerp(PILE6[0], ENV6L[0], g), lerp(PILE6[1] - 20 - 9 * 14 * 0.9, ENV6L[1] - 50, g)
        else:
            g = ease_out(clamp01((T - t_try) / 0.5))
            x = ENV6L[0] + wobble(T - t_try, 14, 30, 6)
            y = lerp(ENV6L[1] - 50, PILE6[1] - 20 - 9 * 14 * 0.9, g)
        folded(c, x, y, 0.9, big=True)
    if T >= tb(6, k_x6):
        for i in range(10):
            f = clamp01((T - tb(6, k_x6) - i * 0.05) / 0.15)
            if f > 0:
                y = PILE6[1] - 20 - i * 14 * 0.9
                part, _ = wb.partial(cross(PILE6[0] + 110, y, 14), f)
                c.drawPath(part, wb.marker(RED, 6))
    return None


b.custom(j, 1, 1.3, left6, sfx="pop", gain=0.6)
b.hit(j, k_try, "wood_high", 0.7, "小李那张塞不进")
b.hit(j, k_x6, "rim", 0.8, "十张都折大了")
b.custom(j, k_x6, k_x6 + 0.3, L.pop_text("十张白折", cx - 290, cy + 270, 72, RED, j, k_x6))


def right6(c, kk, T):
    sc = pop_scale(T - tb(6, 1.5))
    if sc <= 0:
        return None
    t_try, t_fix, t_ok = tb(6, k_try2), tb(6, k_fix), tb(6, k_ok6)
    with at_pop(c, ONE6[0], ONE6[1], sc):
        if T < t_ok - 0.3:
            envelope(c, *ENV6R, 1.0)
        big = T < t_fix
        if T < t_try - 0.35:
            folded(c, *ONE6, 0.9, big=True)
        elif T < t_try + 0.5:
            if T < t_try:
                g = ease_in_out(clamp01((T - (t_try - 0.35)) / 0.35))
                x, y = ONE6[0], lerp(ONE6[1], ENV6R[1] - 50, g)
            else:
                g = ease_out(clamp01((T - t_try) / 0.5))
                x, y = ONE6[0] + wobble(T - t_try, 14, 30, 6), lerp(ENV6R[1] - 50, ONE6[1], g)
            folded(c, x, y, 0.9, big=True)
        elif T < t_ok - 0.3:
            folded(c, *ONE6, 0.9, big=big)
        else:
            g = ease_in_out(clamp01((T - (t_ok - 0.3)) / 0.3))
            if g < 1:
                folded(c, ONE6[0], lerp(ONE6[1], ENV6R[1] - 30, g), 0.9)
            envelope(c, *ENV6R, 1.0, sealed=g >= 1, letter=g >= 1)
    if t_try <= T < t_fix + 0.2:
        f = clamp01((T - t_try) / 0.15)
        part, _ = wb.partial(cross(ONE6[0] + 130, ONE6[1] - 60, 22), f)
        c.drawPath(part, wb.marker(RED, 7))
    return None


b.custom(j, 1.5, 1.8, right6)
b.hit(j, k_try2, "wood_low", 0.75, "小王第一个就塞不进")
b.path(j, k_fix, k_fix + 0.5, C.loop_arrow(ONE6[0] - 150, ONE6[1], 42), ORANGE, 10, sfx="shaker", gain=0.7)
b.hit(j, k_ok6, "ding", 0.8, "改小以后装进去")
b.path(j, k_ok6, k_ok6 + 0.4, check(ENV6R[0] + 120, ENV6R[1] - 60, 40), GREEN, 12)
b.custom(j, k_ok6, k_ok6 + 0.3, L.pop_text("马上改", cx + 300, cy + 270, 72, GREEN, j, k_ok6))
for x, fn, mood in ((cx - 430, draw_li, "sad"), (cx + 430, draw_wang, "smile")):
    def who6(c, sc, T, x=x, fn=fn, mood=mood):
        cx, cy = R[6]
        y, s = cy + 580, 0.62
        late = T >= tb(6, k_x6 if fn is draw_li else k_ok6)
        with at_pop(c, x, y, sc):
            if fn is draw_li:
                fn(c, x, y, s, mood if late else "flat")
            else:
                fn(c, x, y, s, mood=mood if late else "flat")
    b.custom(j, 2, 2.3, pop_fn(j, 2, who6))
b.hit(j, 2, "pop", 0.5, "两人就位")

# ================================================================ 屏 7：书中做法——单件流：每个工位手里只有一台，做完马上传给下一步
cx, cy = R[7]
j = L.scene(7, (cx, cy + 20, Z))
BELT7 = cy + 260
STX7 = [cx - 360, cx, cx + 360]
b.path(j, 0, 0.8, belt(cx - 560, cx + 560, BELT7), BLACK, 8, sfx="wood_high")
b.path(j, 0.8, 1.3, book(cx - 440, cy - 470, 150, 100), GREEN, 7)
b.text(j, 1.3, 1.9, "丰田模式", cx - 190, cy - 470, 72, GREEN)
for i, x in enumerate(STX7):
    b.custom(j, 1 + i * 0.5, 1.3 + i * 0.5, L.figure(draw_worker, j, 1 + i * 0.5, x, BELT7 - 10, 0.72,
                                                     mood="smile",
                                                     lh=lambda T, x=x: (x - 70, BELT7 - 130 + 6 * math.sin(T * 9)),
                                                     rh=lambda T, x=x: (x + 70, BELT7 - 130 - 6 * math.sin(T * 9))))
b.hit(j, 1, "pop", 0.6, "三个工位的员工")
b.hit(j, 2, "pop", 0.5, "三个工位的员工")
k_sl7 = kq(j, wt(9, 0, 0.45), lo=3)
b.custom(j, k_sl7, k_sl7 + 0.3, L.slam_text("单件流", cx + 60, cy - 290, 170, RED, j, k_sl7), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_sl7, 12.0)]
k_c7 = kq(j, wt(9, 1, 0.0), lo=k_sl7 + 1)
KC7 = [k_c7, k_c7 + 1, k_c7 + 2]


def cars7(c, kk, T):
    """车身一台台往右传：第 m 台在 KC7[m] 拍进入 1 号工位，之后每拍往右挪一个工位。"""
    cx, cy = R[7]
    for m in range(3):
        t0 = tb(7, KC7[m])
        if T < t0 - 0.3:
            continue
        pos = 0.0
        for step in range(1, 3 - m):
            ts = tb(7, KC7[m] + step)
            pos += ease_in_out(clamp01((T - (ts - 0.35)) / 0.35))
        x = lerp(STX7[0], STX7[-1], pos / 2) if pos <= 2 else STX7[-1]
        if pos == 0:
            x = lerp(cx - 640, STX7[0], ease_out(clamp01((T - (t0 - 0.3)) / 0.3)))
        car(c, x, BELT7 - 2, 0.85, fill=("#F6C3BE", "#DCEFD9", "#DCE8F7")[m])
    return None


b.custom(j, k_c7, k_c7 + 0.3, cars7)
for i, k_ in enumerate(KC7):
    b.hit(j, k_, ("wood_high", "wood_low", "wood_high")[i], 0.7, "车身往下传一个工位")
b.custom(j, KC7[-1], KC7[-1] + 0.3, L.pop_text("每个工位只有一台", cx, BELT7 + 140, 66, BLUE, j, KC7[-1]))

# ================================================================ 屏 8：问题藏在堆里；库存像河里的水，水位一降，石头露出来
cx, cy = R[8]
j = L.scene(8, (cx, cy + 20, Z))
BED = [(cx - 560, cy - 40), (cx - 430, cy + 400), (cx + 360, cy + 400), (cx + 470, cy - 40), (cx + 560, cy - 40)]
ROCKS = [(cx - 200, 170, 200), (cx + 40, 230, 190), (cx + 270, 150, 170)]
HIGH, LOW = cy - 20, cy + 300
b.path(j, 0, 0.6, book(cx - 440, cy - 470, 150, 100), GREEN, 7, sfx="wood_low")
b.text(j, 0.6, 1.2, "书里说", cx - 230, cy - 470, 72, GREEN)
b.path(j, 1, 1.8, P(*BED), "#8A6A45", 10, sfx="wood_high")
k_fill8 = kq(j, wt(10, 1, 0.15), lo=2)
k_hide = kq(j, wt(10, 2, 0.45), lo=k_fill8 + 2)
k_ld8 = kq(j, wt(11, 0, 0.2), lo=k_hide + 1)
k_down = kq(j, wt(11, 1, 0.2), lo=k_ld8 + 1)
k_rock = kq(j, wt(11, 2, 0.35), lo=k_down + 2)


def rock_path(x, h, w):
    cx, cy = R[8]
    yb = cy + 400
    return P((x - w / 2, yb), (x - w / 2 + 25, yb - h * 0.6), (x - 15, yb - h), (x + w / 2 - 30, yb - h * 0.8), (x + w / 2, yb),
             close=True)


def level8(T):
    cx, cy = R[8]
    t_up = tb(8, k_fill8)
    up = ease_out(clamp01((T - t_up) / 0.7))
    down = ease_in_out(clamp01((T - tb(8, k_down)) / 1.0))
    full = lerp(cy + 400, HIGH, up)
    return lerp(full, LOW, down) if T >= tb(8, k_down) else full


def river8(c, kk, T):
    cx, cy = R[8]
    for x, h, w in ROCKS:
        rp = rock_path(x, h, w)
        c.drawPath(rp, K.paint("#B9B4AA"))
        c.drawPath(rp, wb.marker("#6B655C", 7))
    if T < tb(8, k_fill8):
        return None
    lv = level8(T)
    bed = P(*BED[:4], close=True)
    c.save()
    c.clipPath(bed, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(cx - 600, lv, cx + 600, cy + 420), K.paint("#9CC3EA", 0.93))
    wave = skia.Path()
    wave.moveTo(cx - 600, lv)
    for i in range(1, 61):
        wave.lineTo(cx - 600 + i * 20, lv + 7 * math.sin(i * 0.9 + T * 4))
    c.drawPath(wave, wb.marker(BLUE, 6))
    c.restore()
    return None


b.custom(j, k_fill8, k_fill8 + 0.3, river8, sfx="shaker", gain=0.8)


def stock_label(c, sc, T):
    cx, cy = R[8]
    lv = level8(T)
    x, y = cx - 360, lv - 60
    with K.at(c, x, y, 0, sc):
        K.text(c, "库存", 0, 0, 72, "hand", BLUE)


L.note("库存")
b.custom(j, k_fill8 + 1, k_fill8 + 1.3, pop_fn(j, k_fill8 + 1, stock_label), sfx="pop", gain=0.6)


def hidden8(c, sc, T):
    cx, cy = R[8]
    a = 1 - clamp01((T - tb(8, k_rock)) / 0.3)
    if a <= 0:
        return
    for i, (x, h, w) in enumerate(ROCKS):
        with K.at(c, x, cy + 400 - h * 0.5, 0, sc):
            K.text(c, "？", 0, 0, 90, "hand", "#4A6B8F", a * 0.9)


L.note("？")
b.custom(j, k_hide, k_hide + 0.3, pop_fn(j, k_hide, hidden8), sfx="rim", gain=0.6)
LD8 = (cx + 505, cy - 40, 0.62)
b.custom(j, k_ld8, k_ld8 + 0.3, L.figure(draw_leader, j, k_ld8, *LD8, head_dx=lambda T: 6 * math.sin(T * 2.5)), sfx="wood_high")
b.text(j, k_ld8 + 0.4, k_ld8 + 0.7, "组长", LD8[0], cy - 330, 56, RED)
b.path(j, k_down, k_down + 0.6, arrow((cx + 360, cy - 250), (cx + 360, cy - 100), 0, 30), BLUE, 9, sfx="tom", gain=0.8)
b.custom(j, k_down, k_down + 0.3, L.pop_text("水位降", cx + 200, cy - 300, 62, BLUE, j, k_down))
for i, (x, h, w) in enumerate(ROCKS):
    k_ = k_rock + i * 0.5
    b.custom(j, k_, k_ + 0.3, L.pop_text("问题", x, cy + 400 - h - 45, 54, RED, j, k_),
             sfx="pop" if i != 1 else None, gain=0.7)

# ================================================================ 屏 9：一件一件流起来，有毛病的那一件当场被看见
cx, cy = R[9]
j = L.scene(9, (cx, cy + 20, Z))
BELT9 = cy + 180
BX9 = (cx - 560, cx + 330)
SPOT9 = cx - 60
b.path(j, 0, 0.8, belt(BX9[0], BX9[1], BELT9), BLACK, 8, sfx="wood_high")
b.path(j, 0.5, 1.1, book(cx - 440, cy - 470, 150, 100), GREEN, 7)
b.text(j, 1.1, 1.7, "书中观点", cx - 200, cy - 470, 66, GREEN)
WK9 = (cx + 460, cy + 380, 0.85)
b.custom(j, 1, 1.3, L.figure(draw_worker, j, 1, *WK9, mood="smile",
                             lh=lambda T: (WK9[0] - 120, BELT9 - 30)), sfx="pop")
label(j, 1.4, "小王", WK9[0], WK9[1] + 80, 60, BLUE)
k_flow = kq(j, wt(12, 0, 0.15), lo=2)
k_pick = kq(j, wt(12, 1, 0.2), lo=k_flow + 3)
k_see = kq(j, wt(12, 1, 0.75), lo=k_pick + 1)
I_BAD = 2
SPACING = 210


def beats_since(T, k):
    return L.beat_pos(T) - L.beat_pos(tb(9, k))


def flow9(c, kk, T):
    cx, cy = R[9]
    p = beats_since(T, k_flow)
    if p < 0:
        return None
    p_pick = beats_since(tb(9, k_pick), k_flow)
    p = min(p, p_pick + 2.5)
    for i in range(8):
        x = SPOT9 + (p - p_pick - (i - I_BAD)) * SPACING
        if x < BX9[0] + 50 or x > BX9[1] - 40:
            continue
        if i == I_BAD and T >= tb(9, k_pick):
            continue
        bad = i == I_BAD
        envelope(c, x, BELT9 - 46, 0.8, sealed=True)
        if bad:
            c.drawPath(P((x - 30, BELT9 - 80), (x - 5, BELT9 - 55), (x - 20, BELT9 - 35), (x + 10, BELT9 - 20)),
                       wb.marker(RED, 5))
    if T >= tb(9, k_pick):                                     # 被拿起来的那一件
        g = ease_out(clamp01((T - tb(9, k_pick)) / 0.35))
        x, y = SPOT9, lerp(BELT9 - 46, cy - 120, g)
        a = 0.5 + 0.5 * math.cos((T - tb(9, k_pick)) * 10)
        c.drawCircle(x, y, 110, K.paint(RED, 0.25 * a, blur=20))
        envelope(c, x, y, 1.1, sealed=True)
        c.drawPath(P((x - 40, y - 45), (x - 7, y - 12), (x - 27, y + 12), (x + 14, y + 30)), wb.marker(RED, 7))
        c.drawCircle(x, y, 105, wb.marker(RED, 7, clamp01(g * 2)))
    return None


b.custom(j, k_flow, k_flow + 0.3, flow9, sfx="shaker", gain=0.6)
for k_ in range(k_flow + 1, k_pick):
    b.hit(j, k_, "wood_low", 0.4, "信封一个一个流过")
LD9 = (cx - 330, cy + 590, 0.66)
b.custom(j, k_pick - 1, k_pick - 0.7, L.figure(draw_leader, j, k_pick - 1, *LD9))
b.hit(j, k_pick, "rim", 0.85, "有毛病的那件被拿出来")
b.text(j, k_pick + 0.2, k_pick + 0.5, "组长", LD9[0] + 140, cy + 470, 56, RED)
b.custom(j, k_see, k_see + 0.3, L.slam_text("当场看见", cx + 40, cy - 320, 110, RED, j, k_see), sfx="kick", gain=0.8)

# ================================================================ 屏 10：待办清单——三个方案都写了一半，哪个都交不出去
cx, cy = R[10]
j = L.scene(10, (cx, cy + 20, Z))
LI10 = (cx - 410, cy + 400, 0.9)
LST = (cx + 130, cy - 60, 640, 640)
k_list = kq(j, wt(13, 1, 0.15), lo=2)
k_r10 = kq(j, wt(14, 0, 0.15), lo=k_list + 1)
k_no10 = kq(j, wt(14, 1, 0.55), lo=k_r10 + 3)
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI10, mood=lambda T: "sad" if T >= tb(10, k_no10) else "flat",
                             rh=lambda T: (LI10[0] + 130, LI10[1] - 290 * LI10[2] + 60) if T >= tb(10, k_list) else
                             (LI10[0] + 70 * LI10[2], LI10[1] - 120 * LI10[2])), sfx="pop")
label(j, 1.4, "小李", LI10[0], LI10[1] + 85, 64)


def board10(c, sc, T):
    x, y, w, h = LST
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
        c.drawRoundRect(r, 24, 24, K.paint("#FFFFFF"))
        c.drawRoundRect(r, 24, 24, wb.marker(BLACK, 8))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 90, y - h / 2 - 26, 180, 50), 12, 12, K.paint(BOARD_C))
        K.text(c, "待办", x, y - h / 2 + 70, 70, "hand", BLUE)


BOARD_C = C.BOARD_C
L.note("待办")
b.custom(j, k_list, k_list + 0.3, pop_fn(j, k_list, board10), sfx="wood_high")
ROWS10 = ["方案A", "方案B", "方案C"]


def row10(i):
    def draw(c, sc, T):
        x, y, w, h = LST
        ry = y - 150 + i * 130
        with at_pop(c, x - w / 2 + 40, ry, sc):
            K.text(c, ROWS10[i], x - w / 2 + 40, ry, 56, "hand", BLACK, 1, "left")
            f = 0.5 * ease_out(clamp01((T - tb(10, k_r10 + i)) / 0.4))
            pbar(c, x - 60, ry, 320, 34, f, fill="#FFE9A8", line=ORANGE)
    return draw


L.note(*ROWS10)
for i in range(3):
    b.custom(j, k_r10 + i, k_r10 + i + 0.3, pop_fn(j, k_r10 + i, row10(i)), sfx="pop", gain=0.6)
b.custom(j, k_no10, k_no10 + 0.3, L.stamp("交不出去", LST[0], LST[1] + 230, 76, j, k_no10), sfx="rim", gain=0.9)

# ================================================================ 屏 11：回消息、改文档、开会，来回切——一天没了
cx, cy = R[11]
j = L.scene(11, (cx, cy + 20, Z))
ICX = [cx - 340, cx, cx + 340]
ICY = cy - 230
FLOOR11 = cy + 330
WIN = (cx, cy - 470, 300, 150)
b.path(j, 0, 0.6, P((cx - 540, FLOOR11), (cx + 540, FLOOR11)), BLACK, 8, sfx="wood_high")
k_h = kq(j, wt(15, 0, 0.05), lo=1)
HOPS = [k_h, k_h + 1, k_h + 2, k_h + 2.5, k_h + 3, k_h + 3.5, k_h + 4]
SEQ = [0, 1, 2, 0, 2, 1, 0]
k_gone = kq(j, wt(15, 2, 0.45), lo=k_h + 5)


def icon11(i):
    def draw(c, sc, T):
        x, y = ICX[i], ICY
        hop = [h for h, s_ in zip(HOPS, SEQ) if s_ == i and T >= tb(11, h)]
        act = hop and T - tb(11, hop[-1]) < 0.5
        with at_pop(c, x, y, sc * (1.12 if act else 1.0)):
            if i == 0:
                c.drawRoundRect(skia.Rect.MakeXYWH(x - 85, y - 60, 170, 110), 30, 30, K.paint("#DCEFD9"))
                c.drawPath(wb.bubble(x, y - 5, 170, 110, -1), wb.marker(GREEN, 7))
                for dx in (-40, 0, 40):
                    c.drawCircle(x + dx, y - 5, 9, K.paint(GREEN))
            elif i == 1:
                p = wb.doc(x, y, 120, 150, 3)
                c.drawPath(p, K.paint("#FFFFFF"))
                c.drawPath(p, wb.marker(BLUE, 7))
            else:
                c.drawOval(skia.Rect.MakeXYWH(x - 95, y - 30, 190, 70), K.paint("#F3E6CF"))
                c.drawOval(skia.Rect.MakeXYWH(x - 95, y - 30, 190, 70), wb.marker("#A9773E", 7))
                for dx in (-70, 0, 70):
                    c.drawCircle(x + dx, y - 62, 20, wb.marker(BLACK, 6))
            K.text(c, ("消息", "文档", "开会")[i], x, y + 115, 58, "hand", BLACK)
    return draw


L.note("消息", "文档", "开会")
for i in range(3):
    b.custom(j, 0.5 + i * 0.3, 0.8 + i * 0.3, pop_fn(j, 0.5 + i * 0.3, icon11(i)))


def hopper11(c, kk, T):
    cx, cy = R[11]
    s = 0.8
    if T < tb(11, 1):
        return None
    sc = pop_scale(T - tb(11, 1))
    x, lift = cx, 0.0
    prev = cx
    for h, s_ in zip(HOPS, SEQ):
        th = tb(11, h)
        if T >= th - 0.35:
            g = ease_in_out(clamp01((T - (th - 0.35)) / 0.35))
            x = lerp(prev, ICX[s_], g)
            lift = math.sin(g * math.pi) * 110
            if g < 1:
                break
            prev = ICX[s_]
    # 来回切的轨迹：每次跳过都留下一条弧线
    for n, (h, s_) in enumerate(zip(HOPS, SEQ)):
        if n == 0 or T < tb(11, h):
            continue
        a_, z_ = ICX[SEQ[n - 1]], ICX[s_]
        y0 = cy - 50 + (n % 3) * 12
        p = skia.Path()
        p.moveTo(a_, y0)
        p.quadTo((a_ + z_) / 2, y0 + 50 + n * 9, z_, y0)
        c.drawPath(p, wb.marker("#9AA0AC", 5, 0.8))
    tired = T >= tb(11, k_gone)
    with at_pop(c, x, FLOOR11, sc):
        draw_li(c, x, FLOOR11 - lift, s, "sad" if tired else "flat")
    return None


b.custom(j, 1, 1.3, hopper11, sfx="pop", gain=0.6)
for h in HOPS:
    if abs(h - round(h)) < 1e-9:
        b.hit(j, h, "bongo_low", 0.6, "小李跳到另一件事")


def window11(c, sc, T):
    x, y, w, h = WIN
    dusk = ease_in_out(clamp01((T - (tb(11, k_gone) - 0.8)) / 0.8))
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
        c.save()
        c.clipRect(r)
        c.drawRect(r, K.paint("#CFE6FA" if dusk < 0.5 else "#3D4A63"))
        c.drawRect(r, K.paint("#F6B26B", 0.6 * math.sin(dusk * math.pi)))
        sy = lerp(y - 20, y + h / 2 + 40, dusk)
        c.drawCircle(x + 60, sy, 34, K.paint(YELLOW if dusk < 0.6 else ORANGE))
        c.restore()
        c.drawRect(r, wb.marker(BLACK, 8))
        c.drawLine(x, y - h / 2, x, y + h / 2, wb.marker(BLACK, 6))


b.custom(j, 0.2, 0.5, pop_fn(j, 0.2, window11))
b.custom(j, k_gone, k_gone + 0.3, L.slam_text("一天没了", cx, cy + 470, 100, RED, j, k_gone), sfx="kick", gain=0.8)

# ================================================================ 屏 12：家里也是——衣服洗一半、碗泡池子里、地拖一半
cx, cy = R[12]
j = L.scene(12, (cx, cy + 20, Z))
FL12 = cy + 420
b.path(j, 0, 0.9, join(P((cx - 540, cy - 260), (cx, cy - 520), (cx + 540, cy - 260)), P((cx - 470, cy - 300), (cx - 470, FL12)),
                       P((cx + 470, cy - 300), (cx + 470, FL12)), P((cx - 540, FL12), (cx + 540, FL12))), BLACK, 9,
       sfx="wood_high")
k_home = kq(j, wt(16, 0, 0.3), lo=1)
k_wash = kq(j, wt(16, 1, 0.2), lo=k_home + 1)
k_bowl = kq(j, wt(16, 2, 0.2), lo=k_wash + 1)
k_mop = kq(j, wt(16, 3, 0.2), lo=k_bowl + 1)
b.custom(j, k_home, k_home + 0.3, L.pop_text("家里", cx, cy - 360, 76, BLACK, j, k_home), sfx="pop", gain=0.6)
LI12 = (cx - 100, FL12, 0.72)
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI12, mood=lambda T: "sad" if T >= tb(12, k_mop) else "flat",
                             rh=lambda T: (LI12[0] + 40, LI12[1] - 290 * LI12[2] - 30 + 8 * math.sin(T * 10))))


def washer(c, sc, T):
    cx, cy = R[12]
    x, y = cx - 310, FL12 - 120
    with at_pop(c, x, FL12, sc):
        r = skia.Rect.MakeXYWH(x - 100, y - 120, 200, 240)
        c.drawRoundRect(r, 16, 16, K.paint("#FFFFFF"))
        c.drawRoundRect(r, 16, 16, wb.marker(BLACK, 8))
        c.drawLine(x - 100, y - 70, x + 100, y - 70, wb.marker(BLACK, 5))
        c.drawCircle(x, y + 20, 62, K.paint("#DCE8F7"))
        c.drawCircle(x, y + 20, 62, wb.marker(BLACK, 7))
        sh = P((x - 10, y + 10), (x + 40, y + 30), (x + 70, y + 90), (x + 30, y + 115), (x + 5, y + 70), close=True)
        c.drawPath(sh, K.paint("#BFD5F2"))
        c.drawPath(sh, wb.marker(BLUE, 5))
        c.drawOval(skia.Rect.MakeXYWH(x - 150, y - 40, 50, 130), wb.marker(BLACK, 6))


def sink(c, sc, T):
    cx, cy = R[12]
    x, y = cx + 140, FL12 - 220
    with at_pop(c, x, FL12, sc):
        c.drawRect(skia.Rect.MakeXYWH(x - 130, y, 260, 220), K.paint("#F3E6CF"))
        c.drawRect(skia.Rect.MakeXYWH(x - 130, y, 260, 220), wb.marker("#A9773E", 7))
        basin = skia.Path()
        basin.addArc(skia.Rect.MakeXYWH(x - 100, y - 50, 200, 100), 0, 180)
        c.drawPath(basin, K.paint("#9CC3EA"))
        c.drawPath(basin, wb.marker(BLUE, 6))
        c.drawLine(x - 110, y, x + 110, y, wb.marker(BLACK, 7))
        for dx in (-45, 30):
            bw = skia.Path()
            bw.addArc(skia.Rect.MakeXYWH(x + dx - 40, y - 30, 80, 60), 0, 180)
            c.drawPath(bw, K.paint("#FFFFFF"))
            c.drawPath(bw, wb.marker(BLACK, 5))
        for i in range(4):
            c.drawCircle(x - 60 + i * 38, y - 22 - 12 * math.sin(T * 3 + i), 9, wb.marker(BLUE, 3))
        c.drawPath(P((x + 80, y), (x + 80, y - 90), (x + 30, y - 90)), wb.marker(BLACK, 7))


def mop(c, sc, T):
    cx, cy = R[12]
    x = cx + 400
    with at_pop(c, x, FL12, sc):
        c.drawOval(skia.Rect.MakeXYWH(cx + 250, FL12 - 22, 210, 34), K.paint("#9CC3EA", 0.7))
        c.drawLine(x + 30, FL12 - 380, x - 30, FL12 - 50, wb.marker("#A9773E", 9))
        c.drawPath(P((x - 75, FL12 - 50), (x + 15, FL12 - 50), (x + 35, FL12), (x - 95, FL12), close=True), K.paint("#E9EDF3"))
        c.drawPath(P((x - 75, FL12 - 50), (x + 15, FL12 - 50), (x + 35, FL12), (x - 95, FL12), close=True), wb.marker(BLACK, 6))


b.custom(j, k_wash, k_wash + 0.3, pop_fn(j, k_wash, washer), sfx="wood_low")
b.custom(j, k_wash, k_wash + 0.3, L.pop_text("洗一半", cx - 310, FL12 - 330, 64, ORANGE, j, k_wash))
b.custom(j, k_bowl, k_bowl + 0.3, pop_fn(j, k_bowl, sink), sfx="wood_high")
b.custom(j, k_bowl, k_bowl + 0.3, L.pop_text("泡着", cx + 140, FL12 - 380, 64, ORANGE, j, k_bowl))
b.custom(j, k_mop, k_mop + 0.3, pop_fn(j, k_mop, mop), sfx="wood_low")
b.custom(j, k_mop, k_mop + 0.3, L.pop_text("拖一半", cx + 370, FL12 - 450, 64, ORANGE, j, k_mop))

# ================================================================ 屏 13：每件都在排队，谁也走不出去；开头越多，做完越少
cx, cy = R[13]
j = L.scene(13, (cx, cy + 20, Z))
DOOR = (cx + 440, cy + 200, 150, 380)
FEET13 = cy + 390
TASKS = [("方案", BLUE), ("文档", GREEN), ("衣服", ORANGE), ("碗", "#7A5BB5"), ("消息", RED)]
b.path(j, 0, 0.8, join(rect(DOOR[0], DOOR[1], DOOR[2], DOOR[3], 8), P((cx - 540, FEET13), (cx + 540, FEET13))), BLACK, 9,
       sfx="wood_high")
b.text(j, 0.8, 1.2, "做完", DOOR[0], DOOR[1] - DOOR[3] / 2 - 50, 60, GREEN)
k_tk = kq(j, wt(17, 0, 0.1), lo=1)
k_q13 = kq(j, wt(17, 1, 0.3), lo=k_tk + 3)
k_jam = kq(j, wt(17, 2, 0.5), lo=k_q13 + 1)
k_bar1 = kq(j, wt(18, 0, 0.4), lo=k_jam + 1)
k_bar2 = kq(j, wt(18, 1, 0.4), lo=k_bar1 + 1)
L.note(*[t for t, _ in TASKS])


def sign_guy(c, x, y, s, txt, col, mood, alpha=1.0):
    hy = y - 260 * s
    c.drawPath(join(circle(x, hy, 38 * s), P((x, hy + 38 * s), (x, y - 100 * s)), P((x - 45 * s, y), (x, y - 100 * s), (x + 45 * s, y))),
               wb.marker(BLACK, 8, alpha))
    c.drawPath(face(x, y + 30 * s, s * 0.85, mood), wb.marker(BLACK, 6, alpha))
    r = skia.Rect.MakeXYWH(x - 62 * s, hy + 55 * s, 124 * s, 66 * s)
    c.drawRoundRect(r, 8, 8, K.paint("#FFFFFF", alpha))
    c.drawRoundRect(r, 8, 8, wb.marker(col, 6, alpha))
    K.text(c, txt, x, hy + 88 * s, 44 * s, "hand", col, alpha)


face = wb.face


def queue13(c, kk, T):
    cx, cy = R[13]
    t_q, t_jam = tb(13, k_q13), tb(13, k_jam)
    for i, (txt, col) in enumerate(TASKS):
        t0 = tb(13, k_tk + i * 0.5)
        sc = pop_scale(T - t0)
        if sc <= 0:
            continue
        x0 = cx - 470 + i * 150
        x1 = DOOR[0] - 170 - (4 - i) * 128
        g = ease_in_out(clamp01((T - t_q - (4 - i) * 0.06) / 0.8))
        x = lerp(x0, x1, g)
        if T >= t_jam:
            x += wobble(T - t_jam - i * 0.04, 10, 26, 4)
        with at_pop(c, x, FEET13, sc):
            sign_guy(c, x, FEET13, 1.0, txt, col, "sad" if T >= t_jam else "flat")
    return None


b.custom(j, k_tk, k_tk + 0.3, queue13)
for i in range(0, 5, 2):
    b.hit(j, k_tk + i // 2, "pop", 0.6, "一件件事排进队")
b.hit(j, k_q13, "shaker", 0.7, "都往门口挤")
b.path(j, k_jam, k_jam + 0.4, cross(DOOR[0], DOOR[1] - 30, 70), RED, 13, sfx="rim", gain=0.85)
b.shots[j].shake = [(k_jam, 10.0)]
BASE13 = cy - 120
BARS13 = [(cx - 330, "开头", ORANGE, 0.0, 300.0, k_bar1), (cx - 100, "做完", GREEN, 200.0, 40.0, k_bar2)]
L.note("开头", "做完")


def bars13(c, sc, T):
    cx, cy = R[13]
    with at_pop(c, cx - 215, BASE13, sc):
        c.drawLine(cx - 450, BASE13, cx + 20, BASE13, wb.marker(BLACK, 7))
        for x, name, col, h0, h1, k_ in BARS13:
            h = lerp(h0, h1, ease_out(clamp01((T - tb(13, k_)) / 0.5)))
            if h > 1:
                r = skia.Rect.MakeXYWH(x - 60, BASE13 - h, 120, h)
                c.drawRect(r, K.paint(col, 0.35))
                c.drawRect(r, wb.marker(col, 7))
            K.text(c, name, x, BASE13 + 50, 54, "hand", col)


b.custom(j, k_bar1 - 1, k_bar1 - 0.7, pop_fn(j, k_bar1 - 1, bars13))
b.hit(j, k_bar1, "wood_low", 0.75, "开头的柱子长高")
b.hit(j, k_bar2, "tom", 0.75, "做完的柱子缩矮")
b.path(j, k_bar2, k_bar2 + 0.4, arrow((cx + 70, BASE13 - 300), (cx + 70, BASE13 - 80), 0, 28), RED, 9)

# ================================================================ 屏 14：消息一响就想回——所以从明天开始，试试这三步
cx, cy = R[14]
j = L.scene(14, (cx, cy + 20, Z))
DK14 = cy + 240
PH14 = (cx - 40, DK14 - 100)
LI14 = (cx - 380, cy + 420, 0.9)
b.path(j, 0, 0.8, table(cx - 220, cx + 540, DK14, 150), BLACK, 9, sfx="wood_high")
k_ring = kq(j, wt(19, 1, 0.6), lo=2)
k_reach = kq(j, wt(19, 2, 0.3), lo=k_ring + 1)
k_tom = kq(j, wt(20, 0, 0.4), lo=k_reach + 1)
k_three = kq(j, wt(20, 1, 0.25), lo=k_tom + 1)


def li14(T):
    x, y, s = LI14
    hy = y - 290 * s
    reach = ease_out(clamp01((T - tb(14, k_reach) + 0.3) / 0.3)) * (1 - ease_in_out(clamp01((T - tb(14, k_tom)) / 0.4)))
    return lerp(x + 80 * s, PH14[0] - 70, reach), lerp(hy + 160 * s, PH14[1], reach)


b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI14, mood=lambda T: "smile" if T >= tb(14, k_three) else "flat", rh=li14), sfx="pop")
label(j, 1.4, "小李", LI14[0], LI14[1] + 85, 64)


def phone14(c, kk, T):
    t_r, t_down = tb(14, k_ring), tb(14, k_tom)
    down = T >= t_down
    shake = wobble(T - t_r, 8, 50, 3) if t_r <= T < t_down else 0.0
    phone(c, PH14[0], PH14[1], 0.9, down=down, rot=shake)
    if t_r <= T < t_down:
        c.drawCircle(PH14[0] + 45, PH14[1] - 85, 22, K.paint(RED))
        K.text(c, "9", PH14[0] + 45, PH14[1] - 85, 30, "sans_medium", "#FFFFFF")
        for i in range(2):
            a = (T - t_r) * 3 + i * 0.5
            rr = 60 + (a % 1) * 50
            c.drawArc(skia.Rect.MakeXYWH(PH14[0] - rr, PH14[1] - rr, 2 * rr, 2 * rr), -40, 80, False,
                      wb.marker(RED, 5, 1 - a % 1))
    return None


L.note("9")
b.custom(j, 1.5, 1.6, phone14)
b.hit(j, k_ring, "pop", 0.7, "手机一响")
b.custom(j, k_ring, k_ring + 0.3, L.pop_bubble("叮！", PH14[0] + 190, PH14[1] - 190, j, k_ring, 64, RED, tail=-1,
                                              until=(j, k_tom)))
b.hit(j, k_reach, "shaker", 0.6, "小李伸手")


def cal14(c, sc, T):
    cx, cy = R[14]
    x, y = cx + 340, DK14 - 100
    with at_pop(c, x, y, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 95, y - 85, 190, 170), 14, 14, K.paint("#FFFFFF"))
        c.drawRect(skia.Rect.MakeXYWH(x - 95, y - 85, 190, 48), K.paint("#F6C3BE"))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 95, y - 85, 190, 170), 14, 14, wb.marker(BLACK, 8))
        for dx in (-45, 45):
            c.drawLine(x + dx, y - 105, x + dx, y - 70, wb.marker(BLACK, 8))
        K.text(c, "明天", x, y + 25, 64, "hand", BLACK)


L.note("明天")
b.custom(j, k_tom, k_tom + 0.3, pop_fn(j, k_tom, cal14), sfx="wood_high")
b.custom(j, k_three, k_three + 0.3, L.slam_text("试试这三步", cx, cy - 470, 104, RED, j, k_three), sfx="kick", gain=0.8)
KE14 = [k_three + 1, k_three + 1.5, k_three + 2]
for i, k_ in enumerate(KE14):
    def env14(c, sc, T, i=i):
        cx, cy = R[14]
        x, y = cx - 300 + i * 300, cy - 270
        with at_pop(c, x, y, sc):
            envelope(c, x, y, 1.15, sealed=True)
            c.drawCircle(x, y - 105, 34, K.paint(BLUE))
            K.text(c, str(i + 1), x, y - 105, 46, "sans_medium", "#FFFFFF")
    b.custom(j, k_, k_ + 0.3, pop_fn(j, k_, env14), sfx="pop" if abs(k_ - round(k_)) < 1e-9 else None, gain=0.6)
L.note("1", "2", "3")

# ================================================================ 屏 15：第一，同一时间只开一件，做完再开下一件
cx, cy = R[15]
j = L.scene(15, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("① 只开一件", cx, cy - 470, 92, BLUE, j, 0), sfx="pop")
LI15 = (cx - 420, cy + 420, 0.9)
CARDS = ["方案A", "周报", "报销", "回邮件"]
CY15 = [cy - 270 + i * 155 for i in range(4)]
CX15 = cx + 150
k_c15 = kq(j, wt(21, 0, 0.3), lo=1)
k_one = kq(j, wt(21, 1, 0.6), lo=k_c15 + 1)
k_done15 = kq(j, wt(21, 2, 0.3), lo=k_one + 1)
k_next15 = k_done15 + 1
L.note(*CARDS)


def cards15(c, kk, T):
    t_one, t_done, t_next = tb(15, k_one), tb(15, k_done15), tb(15, k_next15)
    for i, (y, name) in enumerate(zip(CY15, CARDS)):
        sc = pop_scale(T - tb(15, k_c15) - i * 0.08)
        if sc <= 0:
            continue
        active = (i == 0 and t_one <= T < t_done) or (i == 1 and T >= t_next)
        done = i == 0 and T >= t_done
        dim = T >= t_one and not active and not done
        a = 0.35 if dim else 1.0
        with at_pop(c, CX15, y, sc):
            r = skia.Rect.MakeXYWH(CX15 - 260, y - 58, 520, 116)
            if active:
                c.drawRoundRect(r.makeOutset(10, 10), 24, 24, K.paint(YELLOW, 0.35, blur=12))
            c.drawRoundRect(r, 20, 20, K.paint("#FFF4D6" if active else "#FFFFFF", a))
            c.drawRoundRect(r, 20, 20, wb.marker(ORANGE if active else (GREEN if done else BLACK), 7, a))
            K.text(c, name, CX15 - 30, y, 60, "hand", "#9AA0AC" if done else BLACK, a)
            if done:
                c.drawLine(CX15 - 130, y, CX15 + 70, y, wb.marker("#9AA0AC", 6))
                c.drawPath(check(CX15 + 190, y, 34), wb.marker(GREEN, 11))
    return None


b.custom(j, k_c15, k_c15 + 0.3, cards15, sfx="wood_high")
b.hit(j, k_one, "shaker", 0.6, "其余几件变灰，只亮一件")
b.hit(j, k_done15, "ding", 0.8, "做完打勾")
b.hit(j, k_next15, "pop", 0.7, "下一件亮起")
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI15, mood=lambda T: "smile" if T >= tb(15, k_done15) else "flat",
                             lh=lambda T: li_working(*LI15, tb(15, k_one), tb(15, k_done15))(T)[0],
                             rh=lambda T: li_working(*LI15, tb(15, k_one), tb(15, k_done15))(T)[1]))
label(j, 1.4, "小李", LI15[0], LI15[1] + 85, 64)

# ================================================================ 屏 16：第二，大事拆成半天能交的小块，交一块，算一块
cx, cy = R[16]
j = L.scene(16, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("② 拆成小块", cx, cy - 470, 92, BLUE, j, 0), sfx="pop")
LI16 = (cx - 420, cy + 420, 0.9)
BO16 = (cx + 420, cy + 420, 0.9)
k_big = kq(j, wt(22, 1, 0.1), lo=1)
k_split = kq(j, wt(22, 1, 0.7), lo=k_big + 1)
k_give16 = kq(j, wt(22, 2, 0.3), lo=k_split + 1)
k_ok16 = kq(j, wt(22, 3, 0.3), lo=k_give16 + 1)
BLK = [(cx - 300 + i * 200, cy - 200) for i in range(4)]
L.note("大方案", "半天")


def blocks16(c, kk, T):
    cx, cy = R[16]
    t_big, t_split, t_give = tb(16, k_big), tb(16, k_split), tb(16, k_give16)
    sc = pop_scale(T - t_big)
    if sc <= 0:
        return None
    g = ease_out(clamp01((T - t_split) / 0.4))
    if g <= 0:
        with at_pop(c, cx, cy - 200, sc):
            r = skia.Rect.MakeXYWH(cx - 390, cy - 300, 780, 200)
            c.drawRoundRect(r, 16, 16, K.paint("#E4EDFA"))
            c.drawRoundRect(r, 16, 16, wb.marker(BLUE, 9))
            K.text(c, "大方案", cx, cy - 200, 84, "hand", BLUE)
        return None
    for i, (x, y) in enumerate(BLK):
        xx = lerp(cx - 292 + i * 195, x, g)
        if i == 0 and T >= t_give - 0.4:
            h = ease_in_out(clamp01((T - (t_give - 0.4)) / 0.4))
            xx = lerp(x, BO16[0] - 200, h)
            y = lerp(y, BO16[1] - 150, h) - math.sin(h * math.pi) * 120
        r = skia.Rect.MakeXYWH(xx - 85, y - 95, 170, 190)
        c.drawRoundRect(r, 14, 14, K.paint("#DCEFD9" if i == 0 and T >= t_give else "#E4EDFA"))
        c.drawRoundRect(r, 14, 14, wb.marker(BLUE, 8))
        K.text(c, "半天", xx, y, 56, "hand", BLUE)
    return None


b.custom(j, k_big, k_big + 0.3, blocks16, sfx="wood_low")
b.hit(j, k_split, "tom", 0.8, "大块拆成四小块")
b.hit(j, k_give16, "pop", 0.8, "交出第一块")
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI16, mood="smile",
                             rh=lambda T: (LI16[0] + 140, LI16[1] - 290 * LI16[2] + 100) if tb(16, k_give16) - 0.5 <= T < tb(16, k_give16) + 0.4
                             else (LI16[0] + 70 * LI16[2], LI16[1] - 120 * LI16[2])), sfx="pop", gain=0.6)
label(j, 1.4, "小李", LI16[0], LI16[1] + 85, 64)
b.custom(j, 1.5, 1.8, L.figure(draw_boss, j, 1.5, *BO16, mood=lambda T: "smile" if T >= tb(16, k_ok16) else "flat",
                               head_dy=lambda T: 12 * math.sin(clamp01((T - tb(16, k_ok16)) / 0.7) * math.pi * 2),
                               lh=lambda T: (BO16[0] - 110, BO16[1] - 290 * BO16[2] + 120)))
label(j, 1.9, "领导", BO16[0], BO16[1] + 85, 64)
b.path(j, k_ok16, k_ok16 + 0.4, check(BO16[0] - 20, cy + 10, 50), GREEN, 13, sfx="ding")
b.custom(j, k_ok16, k_ok16 + 0.3, L.pop_text("算一块", cx, cy + 40, 76, GREEN, j, k_ok16))

# ================================================================ 屏 17：第三，消息攒到整点一起回，中间别切
cx, cy = R[17]
j = L.scene(17, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("③ 整点回", cx, cy - 470, 92, BLUE, j, 0), sfx="pop")
CLK17 = (cx - 260, cy - 170, 140)
PH17 = (cx + 260, cy - 120)
LI17 = (cx - 400, cy + 430, 0.85)
k_b17 = kq(j, wt(23, 1, 0.1), lo=1)
k_hour = kq(j, wt(23, 2, 0.0), lo=k_b17 + 2)
k_nocut = kq(j, wt(23, 3, 0.4), lo=k_hour + 1)
KB17 = [k_b17, k_b17 + 0.5, k_b17 + 1, k_b17 + 1.5]
b.path(j, 0.5, 1.2, wb.clock(*CLK17), BLACK, 9, sfx="wood_high")


def clock17(c, kk, T):
    x, y, r = CLK17
    t0, t1 = tb(17, 1), tb(17, k_hour)
    f = ease_in_out(clamp01((T - t0) / max(0.1, t1 - t0)))
    minute = 40 + 20 * f
    c.drawCircle(x, y, r, K.paint("#FFFFFF"))
    c.drawPath(wb.clock(x, y, r), wb.marker(BLACK, 9))
    c.drawPath(wb.hands_at(x, y, r, 9 if minute < 60 else 10, minute % 60), wb.marker(RED if f >= 1 else BLACK, 9))
    if T >= t1:
        K.ripple(c, x, y, T - t1, YELLOW, 220, 8, 0.8, 0.6)
        K.text(c, "整点", x, y + r + 60, 64, "hand", RED)
    return None


L.note("整点")
b.custom(j, 1.2, 1.3, clock17)


def phone17(c, kk, T):
    t_h = tb(17, k_hour)
    up = T >= t_h
    phone(c, PH17[0], PH17[1] + 60, 0.95, down=not up)
    n = sum(1 for k_ in KB17 if T >= tb(17, k_))
    for i in range(n):
        g = ease_in_out(clamp01((T - t_h - i * 0.08) / 0.4)) if up else 0.0
        sc = pop_scale(T - tb(17, KB17[i]))
        x = PH17[0] + 165
        y = PH17[1] - 60 - i * 70
        if g >= 1:
            continue
        with K.at(c, lerp(x, PH17[0], g), lerp(y, PH17[1] + 40, g), 0, sc * (1 - g)):
            c.drawRoundRect(skia.Rect.MakeXYWH(-70, -28, 140, 56), 26, 26, K.paint("#DCEFD9"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-70, -28, 140, 56), 26, 26, wb.marker(GREEN, 5))
            for dx in (-30, 0, 30):
                c.drawCircle(dx, 0, 7, K.paint(GREEN))
    if up:
        a = clamp01((T - t_h - 0.4) / 0.3)
        c.drawPath(check(PH17[0] + 165, PH17[1] - 250, 46), wb.marker(GREEN, 12, a))
        K.text(c, "一起回", PH17[0] + 165, PH17[1] - 140, 64, "hand", GREEN, a)
    return None


L.note("一起回")
b.custom(j, 1.4, 1.5, phone17)
for k_ in KB17:
    if abs(k_ - round(k_)) < 1e-9:
        b.hit(j, k_, "pop", 0.55, "消息攒着")
b.hit(j, k_hour, "ding", 0.85, "整点一起回")
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI17, mood="smile",
                             lh=lambda T: li_working(*LI17, tb(17, 1), tb(17, k_hour))(T)[0],
                             rh=lambda T: li_working(*LI17, tb(17, 1), tb(17, k_hour))(T)[1]), sfx="pop", gain=0.6)
label(j, 1.4, "小李", LI17[0], LI17[1] + 80, 60)


def nocut17(c, sc, T):
    cx, cy = R[17]
    x, y = cx + 150, cy + 300
    with at_pop(c, x, y, sc):
        c.drawPath(arrow((x - 150, y + 20), (x + 150, y + 20), 0.5, 30), wb.marker("#9AA0AC", 7))
        c.drawPath(arrow((x + 150, y - 20), (x - 150, y - 20), 0.5, 30), wb.marker("#9AA0AC", 7))
        c.drawPath(cross(x, y, 70), wb.marker(RED, 12))
        K.text(c, "别切", x + 260, y, 70, "hand", RED)


L.note("别切")
b.custom(j, k_nocut, k_nocut + 0.3, pop_fn(j, k_nocut, nocut17), sfx="rim", gain=0.8)

# ================================================================ 屏 18：一件一件交出去，进度条才往前走；下班时至少有一件做完
cx, cy = R[18]
j = L.scene(18, (cx, cy + 20, Z))
PB18 = (cx - 450, cy - 330, 900, 70)
LI18 = (cx - 160, cy + 430, 0.95)
TR18 = (cx + 330, cy + 430)
k_e18 = kq(j, wt(24, 0, 0.15), lo=1)
KE18 = [k_e18, k_e18 + 1, k_e18 + 2]
k_go18 = kq(j, wt(24, 1, 0.6), lo=KE18[-1] + 1)
k_clk18 = kq(j, wt(25, 0, 0.3), lo=k_go18 + 1)
k_done18 = kq(j, wt(25, 2, 0.15), lo=k_clk18 + 1)


def bar18(c, kk, T):
    x0, y, w, h = PB18
    f = 0.0
    for i, k_ in enumerate(KE18):
        f += 0.25 * ease_out(clamp01((T - tb(18, k_)) / 0.35))
    f += 0.25 * ease_out(clamp01((T - tb(18, k_go18)) / 0.5))
    pbar(c, x0, y, w, h, f, fill="#BFE3C8", line=GREEN)
    for i in range(1, 4):
        c.drawLine(x0 + w * i / 4, y - h / 2 + 6, x0 + w * i / 4, y + h / 2 - 6, wb.marker("#9AA0AC", 3))
    K.text(c, f"{int(round(f * 100))}%", x0 + w / 2, y + 90, 60, "sans_medium", GREEN)
    return None


L.note("0%", "25%", "50%", "75%", "100%")
b.path(j, 0, 0.8, rect(PB18[0] + PB18[2] / 2, PB18[1], PB18[2], PB18[3], 35), GREEN, 7, sfx="wood_high")
b.custom(j, 0.8, 0.9, bar18)


def tray18(c, kk, T):
    cx, cy = R[18]
    tray(c, TR18[0], TR18[1], 200)
    for i, k_ in enumerate(KE18):
        t0 = tb(18, k_)
        if T < t0 - 0.35:
            continue
        g = ease_in(clamp01((T - (t0 - 0.35)) / 0.35))
        y = lerp(cy - 120, TR18[1] - 40 - i * 14, g)
        envelope(c, TR18[0] + (i - 1) * 16, y, 0.85, sealed=True)
    return None


def ease_in(x):
    return x * x


b.custom(j, 0.6, 0.7, tray18)
for k_ in KE18:
    b.hit(j, k_, "wood_low", 0.7, "一件交出去，进度条走一格")
b.hit(j, k_go18, "clap", 0.7, "进度条往前走")
b.custom(j, k_go18, k_go18 + 0.3, L.pop_text("往前走", cx + 300, cy - 180, 68, GREEN, j, k_go18))


def li18(c, kk, T):
    x, y, s = LI18
    sc = pop_scale(T - tb(18, 1))
    if sc <= 0:
        return None
    hy = y - 290 * s
    up = ease_out(clamp01((T - tb(18, k_done18)) / 0.3))
    rh = (lerp(x + 75 * s, x + 110 * s, up), lerp(hy + 160 * s, hy - 60 * s, up))
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if T >= tb(18, k_clk18) else "flat", bag=True, rh=rh)
        if up > 0:
            envelope(c, rh[0] + 10, rh[1] - 50, 0.9, sealed=True, alpha=clamp01(up * 2))
    return None


b.custom(j, 1, 1.3, li18, sfx="pop", gain=0.6)
label(j, 1.4, "小李", LI18[0], LI18[1] + 85, 64)
b.path(j, k_clk18, k_clk18 + 0.6, join(wb.clock(cx + 360, cy + 30, 95), wb.hands_at(cx + 360, cy + 30, 95, 6, 0)), BLACK, 8,
       sfx="wood_high")
b.text(j, k_clk18 + 0.6, k_clk18 + 0.9, "18:00", cx + 360, cy + 175, 56, RED)
b.custom(j, k_done18, k_done18 + 0.3, L.stamp("做完了", cx + 10, cy - 100, 96, j, k_done18, color=GREEN, rot=-6),
         sfx="kick", gain=0.8)
b.shots[j].shake = [(k_done18, 10.0)]

# ================================================================ 屏 19：评论区见 + 下一讲预告
cx, cy = R[19]
j = L.scene(19, (cx, cy + 20, Z))
k_q19 = kq(j, wt(26, 0, 0.15), lo=1)
b.text(j, k_q19, k_q19 + 1.4, "开了头没做完的", cx, cy - 520, 66, RED, sfx="pop")
b.text(j, k_q19 + 1.4, k_q19 + 2.0, "有几件？", cx, cy - 430, 66, RED)
LI19 = (cx - 420, cy + 140, 0.8)
k_cnt = kq(j, wt(27, 0, 0.1), lo=k_q19 + 2)
k_type = kq(j, wt(27, 1, 0.1), lo=k_cnt + 2)
ENV19 = [(cx - 170 + i * 200, cy + 60) for i in range(3)]


def li19(c, kk, T):
    x, y, s = LI19
    sc = pop_scale(T - tb(19, 1))
    if sc <= 0:
        return None
    n = sum(1 for i in range(3) if T >= tb(19, k_cnt + i * 0.5))
    hy = y - 290 * s
    rh = (x + 110 * s, hy + 40 * s) if n else (x + 70 * s, hy + 170 * s)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if n else "flat", rh=rh)
        for i in range(n):
            c.drawLine(rh[0] - 12 + i * 12, rh[1], rh[0] - 18 + i * 14, rh[1] - 34, wb.marker(BLACK, 7))
    return None


b.custom(j, 1, 1.3, li19, sfx="pop", gain=0.6)
for i, (x, y) in enumerate(ENV19):
    k_ = k_cnt + i * 0.5

    def env19(c, sc, T, x=x, y=y, i=i):
        with at_pop(c, x, y, sc):
            envelope(c, x, y, 0.95, letter=True)
            K.text(c, str(i + 1), x, y - 120, 64, "sans_medium", ORANGE)
    b.custom(j, k_, k_ + 0.3, pop_fn(j, k_, env19), sfx="pop" if abs(k_ - round(k_)) < 1e-9 else None, gain=0.7)
INP = (cx + 130, cy - 230, 700, 120)


def input19(c, kk, T):
    x, y, w, h = INP
    sc = pop_scale(T - tb(19, k_type))
    if sc <= 0:
        return None
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
        c.drawRoundRect(r, h / 2, h / 2, K.paint("#FFFFFF"))
        c.drawRoundRect(r, h / 2, h / 2, wb.marker(BLUE, 7))
        msg = "我有3件"
        n = min(len(msg), int((T - tb(19, k_type)) / 0.18) + 1)
        tw = K.text(c, msg[:n], x - w / 2 + 40, y, 58, "hand", BLACK, 1, "left")
        if (T * 2) % 1 < 0.5:
            c.drawLine(x - w / 2 + 48 + tw, y - 30, x - w / 2 + 48 + tw, y + 30, wb.marker(BLUE, 5))
        c.drawRoundRect(skia.Rect.MakeXYWH(x + w / 2 - 150, y - 38, 130, 76), 38, 38, K.paint(BLUE))
        K.text(c, "发送", x + w / 2 - 85, y, 44, "sans_medium", "#FFFFFF")
    return None


L.note("我有3件", "发送")
b.custom(j, k_type, k_type + 0.3, input19, sfx="wood_high")
# 2026-11 收尾鼓励（第 28 句）：镜头下移；小李在小本子上画一个勾；预告卡整体下移 DY
DY = 670
k_e = kq(j, wt(28, 0, 0.0), lo=k_type + 1)
b.move(j, k_e, (cx, cy + 800, Z), 1.1)
k_e1 = k_e + 2
k_one = kq(j, wt(28, 0, 0.65), lo=k_e1 + 1)
k_chk = kq(j, wt(28, 1, 0.6), lo=k_one + 1)
k_txt = k_chk + 1
k_n19 = kq(j, wt(29, 0, 0.15), lo=k_txt + 1)
LI19E = (cx - 90, cy + 790, 0.8)
NB19 = (cx + 170, cy + 610)


def note19(c, kk, T):
    """小李拿着笔站在摊开的小本子旁；写勾时手跟着动。"""
    x, y, s = LI19E
    sc = pop_scale(T - tb(19, k_e1))
    if sc <= 0:
        return None
    nx_, ny_ = NB19
    hy = y - 290 * s
    w = ease_in_out(clamp01((T - tb(19, k_chk)) / 0.45))
    pen = (lerp(nx_ - 140, nx_ + 40, w), lerp(hy + 110 * s, ny_ + 60 - 40 * math.sin(math.pi * w), w))
    with at_pop(c, cx, cy + 610, sc):
        for side in (-1, 1):
            r = skia.Rect.MakeLTRB(nx_ + min(0, side * 170), ny_ - 120, nx_ + max(0, side * 170), ny_ + 120)
            c.drawRoundRect(r, 10, 10, K.paint("#FFFFFF"))
            c.drawRoundRect(r, 10, 10, wb.marker(BLACK, 6))
        for i in range(3):
            c.drawLine(nx_ - 140, ny_ - 60 + i * 50, nx_ - 30, ny_ - 60 + i * 50, wb.marker("#9AA0AC", 4))
        draw_li(c, x, y, s, "smile" if T >= tb(19, k_chk) else "flat", rh=pen)
        c.drawLine(pen[0], pen[1], pen[0] + 22, pen[1] - 50, wb.marker(ORANGE, 9))
    return None


b.custom(j, k_e1, k_e1 + 0.3, note19, sfx="pop", gain=0.6)
b.custom(j, k_one, k_one + 0.3, L.pop_text("今天做完 1 件", NB19[0], NB19[1] - 175, 50, BLACK, j, k_one, "sans_medium"),
         sfx="wood_high", gain=0.7)
b.path(j, k_chk, k_chk + 0.4, check(NB19[0] + 85, NB19[1] + 10, 60), GREEN, 12, sfx="ding")
b.custom(j, k_txt, k_txt + 0.3, L.pop_text("值得记一笔", cx, cy + 330, 70, BLUE, j, k_txt), sfx="pop", gain=0.6)
b.path(j, k_n19, k_n19 + 0.6, rect(cx, cy + 390 + DY, 1060, 260, 24), BLUE, 8, sfx="wood_high")
b.text(j, k_n19 + 0.5, k_n19 + 0.8, "下一讲", cx, cy + 300 + DY, 50, BLUE)
b.text(j, k_n19 + 0.8, k_n19 + 2.2, "干了一百遍的事，怎么还会出错？", cx, cy + 385 + DY, 58, BLACK)


def ticks19(c, sc, T):
    cx, cy = R[19]
    for i in range(10):
        x = cx - 315 + i * 70
        f = clamp01((T - tb(19, k_n19 + 2.2) - i * 0.06) / 0.15)
        if f <= 0:
            continue
        p = cross(x, cy + 465 + DY, 18) if i == 9 else check(x, cy + 465 + DY, 20)
        part, _ = wb.partial(p, f)
        c.drawPath(part, wb.marker(RED if i == 9 else GREEN, 7))


b.custom(j, k_n19 + 2.2, k_n19 + 2.4, pop_fn(j, k_n19 + 2.2, ticks19))

# ================================================================ 收尾
L.finish(cover_shot=5)
L.export(globals())
