"""《丰田模式》05 标准化：干了一百遍的事，怎么还会出错？（白板手绘 + AI 旁白，竖屏 2:3）

误区对照：先摆出“标准 = 死板、管人”的印象，再拿一张“我们以为 | 书里讲的”对照表，三个误区逐个对照。
- 0–3 秒：系列开场“丰田模式”四字，缓推到小李的清单：第 98、99、100 遍逐拍翻过，第一百遍漏了一步（红圈）；
- drop：第 2 屏小王举着作业卡，“标准化作业”印章砸下（重击 + 震屏 + 闪白）；
- 印象：小李被绳子捆在“标准”本子上，领导叉腰，“死板”“管人”两块牌子砸下；
- 对照表：左列“我们以为”三条逐拍弹出，右列打问号，“反着来”；
- 误区一 / 二 / 三三屏用同一套左右分栏（左灰右绿、中间虚线），左边画完盖红叉，右边画书里的做法打勾：
  石碑“永远这样做” vs 可擦写的作业卡；领导往下扔规定 vs 工人自己掐表改步骤；凭经验每次不一样 vs 同一张流程好找错；
- 书中观点：三次按同一张流程做，第三次第 3 步歪了，一比就亮红，扶正后长出“改进”箭头；
- 说回我们：报表、同事请假、出差忘带充电器、凭感觉一百种做法 → 又慢又烦 → 三步做法 → 清单的好处 → 评论区 + 下一讲预告。
文案见 fengtian/PLAN.md「### 05 标准化」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_leader, draw_li, draw_worker,
                             pop_scale, walk, wobble)
from whiteboard import engine as wb
from whiteboard.engine import P, book, check, circle, cross, join, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "丰田模式 · 书中做法", 2),
    ([3], "大家的印象", 3),
    ([4], "误区对照", 4),
    ([5], "误区一 · 对照", 5),
    ([6], "误区一 · 对照", 6),
    ([7, 8], "误区二 · 对照", 7),
    ([9, 10], "误区三 · 对照", 8),
    ([11, 12], "书中观点", 9),
    ([13, 14], "说回我们自己", 10),
    ([15], "说回我们自己", 11),
    ([16], "说回我们自己", 12),
    ([17, 18], "说回我们自己", 13),
    ([19, 20], "说回我们自己", 14),
    ([21], "做法一 · 示意", 15),
    ([22], "做法二 · 示意", 16),
    ([23], "做法三 · 示意", 17),
    ([24, 25], "清单的好处", 18),
    ([26, 27, 28], "评论区见", 19),
]

L = C.Lesson("05", SCREENS, drop_screen=2, board_size=(5000, 11400))
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

# 各屏在白板上的区块中心（相邻屏相距 1600，蛇形排列）
R = [(2600, 800), (900, 900), (900, 2500), (2500, 2500), (4100, 2500), (4100, 4100), (2500, 4100), (900, 4100),
     (900, 5700), (2500, 5700), (4100, 5700), (4100, 7300), (2500, 7300), (900, 7300), (900, 8900), (2500, 8900),
     (4100, 8900), (4100, 10500), (2500, 10500), (900, 10500)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 6——标准化的任务是持续改进与授权员工的基础（Standardized tasks are the foundation for continuous "
    "improvement and employee empowerment）；书中引福特“今天的标准是明天改进的基础”，并以丰田与通用合办的 NUMMI 工厂为例，"
    "工人自己计时、自己改写标准作业。",
    "清单、报表、行李等为示意；小李、小王、组长、领导为虚构人物。",
]

GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL = "#8A8F99", "#ECEEF1", "#D3EDDC", "#F6C3BE", "#D5E3F7"
PAPER_FILL, NOTE_FILL = "#FFFFFF", "#FFF1A8"


def nbeats(j):
    return L.BOUNDS[j][1] - L.BOUNDS[j][0]


def kq(j, t_local, lo=0):
    """kb，但 lo 超出本屏时夹到最后一拍（排期变短时不报错）。"""
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


def checkbox(c, x, y, sz, state, alpha=1.0):
    """清单里的小方框：state = None / "ok"（绿勾）/ "miss"（空着）。"""
    box(c, x, y, sz, sz, "#FFFFFF", BLACK, 5, 6, alpha)
    if state == "ok":
        c.drawPath(check(x, y, sz * 0.42), wb.marker(GREEN, 7, alpha))


def clipboard(c, x, y, w, h, alpha=1.0):
    """夹板：(x, y) 为中心。"""
    box(c, x, y, w, h, "#E9D2AE", "#A9773E", 7, 18, alpha)
    box(c, x, y + 14, w - 40, h - 60, "#FFFFFF", BLACK, 4, 8, alpha)
    box(c, x, y - h / 2 + 6, 120, 34, "#8A8F99", BLACK, 4, 8, alpha)


def sticky(c, x, y, w=150, h=130, rot=0.0, alpha=1.0, fill=NOTE_FILL):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, fill, "#C9A227", 5, 4, alpha)


def step_box(c, x, y, n, w=120, h=84, fill=BLUE_FILL, line=BLUE, alpha=1.0, rot=0.0):
    """流程里的一步：带序号的小方块。"""
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, fill, line, 6, 12, alpha)
        K.text(c, str(n), 0, 2, 52, "hand", line, alpha)


def sweat(c, x, y, s=1.0, alpha=1.0):
    p = skia.Path()
    p.moveTo(x, y - 22 * s)
    p.quadTo(x + 15 * s, y, x, y + 10 * s)
    p.quadTo(x - 15 * s, y, x, y - 22 * s)
    c.drawPath(p, K.paint("#BFD5F2", alpha))
    c.drawPath(p, wb.marker(BLUE, 4, alpha))


def qmark(c, x, y, size, color, alpha=1.0):
    K.text(c, "？", x, y, size, "hand", color, alpha)


def head_of(x, y, s):
    return x, y - 290 * s


# —— 误区对照的固定分栏：上方两个标签，中间一条虚线（误区一 / 二 / 三三屏共用）
VS_L, VS_R = "我们以为", "书里讲的"
L.note(VS_L, VS_R)


def vs_frame(j, k, cx, cy, no):
    """第 j 屏第 k 拍画出分栏：左“我们以为”（灰）、右“书里讲的”（绿），中间虚线；左上角“误区一 / 二 / 三”。"""
    ylab = cy - 470

    def fn(c, kk, T, cx=cx, cy=cy):
        f = ease_out(clamp01((T - tb(j, k)) / 0.45))
        if f <= 0:
            return None
        dashed(c, (cx, ylab + 60), (cx, ylab + 60 + 860 * f), GRAY, 5)
        for x, s, fill, line in ((cx - 270, VS_L, GRAY_FILL, GRAY), (cx + 270, VS_R, GREEN_FILL, GREEN)):
            sc = pop_scale(T - tb(j, k) - (0 if x < cx else 0.12))
            if sc <= 0:
                continue
            with K.at(c, x, ylab, 0, sc):
                box(c, 0, 0, 300, 86, fill, line, 6, 43)
                K.text(c, s, 0, 2, 54, "hand", line)
        return None
    b.custom(j, k, k + 0.5, fn, sfx="wood_high")
    del no


def big_x(j, k, x, y, r=150, gain=0.85):
    """左栏画完后砸一个红叉（kick + 震屏）。"""
    b.path(j, k, k + 0.35, cross(x, y, r), RED, 18, sfx="kick", gain=gain)
    b.shots[j].shake = b.shots[j].shake + [(k, 10.0)]


# ================================================================ 屏 0：系列开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：清单第 98、99、100 遍——第一百遍漏了一步；组长问“错在哪？”，小李挠头
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
CB1 = (cx - 210, cy - 40, 470, 640)
ROWS1 = [CB1[1] - 190 + i * 105 for i in range(5)]
MISS1 = 3
k_cb = 0
k_cnt = [kq(j, wt(0, 0, 0.35), 1)]
k_cnt += [k_cnt[0] + 1, k_cnt[0] + 2]
k_tick = k_cnt[2] + 1
k_miss = max(kq(j, wt(0, 1, 0.55), k_tick + 2), k_tick + 2)
L.note("第98遍", "第99遍", "第100遍", "漏了")


def board1(c, sc, T):
    x, y, w, h = CB1
    with at_pop(c, x, y, sc):
        clipboard(c, x, y, w, h)
        t_t = tb(1, k_tick)
        for i, ry in enumerate(ROWS1):
            st = None
            if T >= t_t + i * 0.18 and i != MISS1:
                st = "ok"
            if i == MISS1 + 1 and T < t_t + i * 0.18:
                st = None
            checkbox(c, x - 150, ry, 54, st)
            col = RED if (i == MISS1 and T >= tb(1, k_miss)) else "#9AA0AC"
            c.drawLine(x - 95, ry, x + 160 - (i % 2) * 50, ry, wb.marker(col, 7))
    return None


ev(j, k_cb, pop_fn(j, k_cb, board1), "wood_high")


def counter1(c, kk, T, cx=cx, cy=cy):
    """右上角计数：第 98 → 99 → 100 遍，每拍翻一次。"""
    x, y = cx + 260, cy - 440
    n = sum(1 for k_ in k_cnt if T >= tb(1, k_))
    if n == 0:
        return None
    s = f"第{97 + n}遍"
    dt = T - tb(1, k_cnt[n - 1])
    sc = C.slam_scale(dt) if n == 3 else pop_scale(dt, 0.22)
    col = RED if n == 3 else BLACK
    with K.at(c, x, y, -4 if n == 3 else 0, sc):
        K.text(c, s, 0, 0, 92 if n == 3 else 80, "hand", col)
    return None


ev(j, k_cnt[0], counter1, "wood_low", 0.6)
b.hit(j, k_cnt[1], "wood_high", 0.6, "计数翻到第99遍")
b.hit(j, k_cnt[2], "rim", 0.85, "计数砸到第100遍")
b.hit(j, k_tick, "pop", 0.6, "清单一行行打勾")


def miss1(c, kk, T, cx=cx, cy=cy):
    t0 = tb(1, k_miss)
    if T < t0:
        return None
    f = clamp01((T - t0) / 0.3)
    x, y = CB1[0] - 150, ROWS1[MISS1]
    ring = skia.Path()
    ring.addOval(skia.Rect.MakeXYWH(x - 70, y - 55, 340, 110))
    part, tip = wb.partial(ring, f)
    c.drawPath(part, wb.marker(RED, 9))
    sc = pop_scale(T - t0 - 0.25)
    if sc > 0:
        with K.at(c, CB1[0] + 280, y - 10, 0, sc):
            K.text(c, "漏了", 0, 0, 70, "hand", RED)
    return tip


ev(j, k_miss, miss1, "kick", 0.85, 0.35)
b.shots[j].shake = [(k_miss, 9.0)]
LI1 = (cx + 230, cy + 430, 0.82)
k_li1 = k_cnt[0]
k_ask = max(kq(j, wt(1, 0, 0.3), k_miss + 1), k_miss + 1)
k_scr = max(kq(j, wt(1, 1, 0.5), k_ask + 1), k_ask + 1)


def li1(c, sc, T, cx=cx, cy=cy):
    x, y, s = LI1
    hx, hy = head_of(x, y, s)
    scratching = T >= tb(1, k_scr)
    if scratching:
        rh = (hx + 40 * s, hy - 40 * s + 8 * math.sin((T - tb(1, k_scr)) * 18))
        mood = "sad"
    else:
        rh = (x + 80 * s, hy + 150 * s)
        mood = "sad" if T >= tb(1, k_miss) else "flat"
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, mood, rh=rh, lh=(x - 110 * s, hy + 130 * s))
        if scratching:
            a = pop_scale(T - tb(1, k_scr))
            with K.at(c, hx + 75, hy - 95, 0, a):
                qmark(c, 0, 0, 90, BLUE)
    return None


ev(j, k_li1, pop_fn(j, k_li1, li1))
L.note("？")
LD1 = (cx + 470, cy + 430, 0.78)


def leader1(c, kk, T, cx=cx, cy=cy):
    t0 = tb(1, k_ask) - 0.6
    if T < t0:
        return None
    x, dy, moving = walk(T, t0, 0.6, cx + 800, LD1[0], 12, 3.0)
    draw_leader(c, x, LD1[1], LD1[2], phase=(T - t0) * 2.5 if moving else 0.0, run=0.8 if moving else 0.0)
    return None


b.custom(j, max(0, k_ask - 1.2), max(0, k_ask - 1.2) + 0.3, leader1)
ev(j, k_ask, L.pop_bubble("错在哪？", cx + 330, cy - 200, j, k_ask, 70, BLACK, tail=1), "pop")
b.hit(j, k_scr, "wood_low", 0.6, "小李挠头")

# ================================================================ 屏 2：丰田的办法，有点土——标准化作业（drop 时印章砸下）
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
b.path(j, 0, 0.6, book(cx - 420, cy - 450, 150, 100), GREEN, 7, sfx="wood_low")
b.text(j, 0.6, 1.4, "丰田模式", cx - 160, cy - 450, 76, GREEN)
WK2 = (cx - 280, cy + 430, 0.9)
k_wk2 = 1 if KD > 4 else 0
k_card2 = min(k_wk2 + 1, KD - 1)
k_tu = kq(j, wt(2, 1, 0.35), k_card2 + 1)
if k_tu >= KD:
    k_tu = max(k_card2 + 1, KD - 1)
CARD2 = (cx + 180, cy + 60, 420, 470)


def worker2(c, sc, T):
    x, y, s = WK2
    hx, hy = head_of(x, y, s)
    lift = ease_out(clamp01((T - tb(2, KD) + 0.2) / 0.3))
    rh = (lerp(x + 120 * s, x + 170 * s, lift), lerp(hy + 140 * s, hy - 10 * s, lift))
    with at_pop(c, x, y, sc):
        draw_worker(c, x, y, s, mood="smile" if T >= tb(2, KD) else "flat", rh=rh)
    return None


ev(j, k_wk2, pop_fn(j, k_wk2, worker2), "pop", 0.7)


def card2(c, sc, T, cx=cx, cy=cy):
    x, y, w, h = CARD2
    with at_pop(c, x, y, sc):
        box(c, x, y, w, h, PAPER_FILL, BLACK, 7, 16)
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 6, y - h / 2 + 6, w - 12, 70), K.paint(BLUE_FILL))
        K.text(c, "作业卡", x, y - h / 2 + 42, 54, "hand", BLUE)
        for i in range(4):
            yy = y - h / 2 + 130 + i * 90
            K.text(c, str(i + 1), x - w / 2 + 50, yy, 48, "hand", BLUE)
            c.drawLine(x - w / 2 + 90, yy, x + w / 2 - 40 - (i % 2) * 60, yy, wb.marker("#9AA0AC", 7))
    return None


L.note("作业卡", "1", "2", "3", "4")
ev(j, k_card2, pop_fn(j, k_card2, card2), "wood_high")
ev(j, k_tu, L.pop_text("有点土", cx - 300, cy - 60, 78, ORANGE, j, k_tu), "clap", 0.7)
ev(j, KD, L.stamp("标准化作业", cx + 60, cy - 260, 100, j, KD, rot=-6), "kick", 0.95)

# ================================================================ 屏 3：一说标准——死板，管人（小李被捆在本子上，领导叉腰）
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
BK3 = (cx - 120, cy + 120, 300, 420)
LI3 = (cx - 120, cy + 430, 0.85)
BO3 = (cx + 330, cy + 430, 0.9)
k_bk3 = 0
k_li3 = kq(j, wt(3, 0, 0.4), 1)
k_rope = k_li3 + 1
k_boss3 = kq(j, wt(3, 1, 0.3), k_rope + 1)
k_ban = max(kq(j, wt(3, 1, 0.92), k_boss3 + 1), k_boss3 + 1)
k_guan = max(kq(j, wt(3, 2, 0.4), k_ban + 1), k_ban + 1)


def book3(c, sc, T):
    x, y, w, h = BK3
    with at_pop(c, x, y + h / 2, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 + 18, y - h / 2 + 14, w, h), 14, 14, K.paint("#3D4A63"))
        box(c, x, y, w, h, "#5B6B8C", BLACK, 7, 14)
        box(c, x, y - 90, w - 80, 110, "#FFFFFF", BLACK, 5, 10)
        K.text(c, "标准", x, y - 88, 76, "hand", BLACK)
        for i in range(3):
            c.drawLine(x - w / 2 + 40, y + 40 + i * 50, x + w / 2 - 40, y + 40 + i * 50, wb.marker("#C9CED6", 5))
    return None


L.note("标准")
ev(j, k_bk3, pop_fn(j, k_bk3, book3), "tom", 0.7)


def li3(c, sc, T):
    x, y, s = LI3
    tied = T >= tb(3, k_rope)
    wig = 7 * math.sin((T - tb(3, k_rope)) * 14) if tied else 0.0
    hx, hy = head_of(x, y, s)
    with at_pop(c, x, y, sc):
        c.save()
        c.translate(wig, 0)
        if tied:
            draw_li(c, x, y, s, "sad", lh=(x - 50 * s, hy + 170 * s), rh=(x + 50 * s, hy + 170 * s))
        else:
            draw_li(c, x, y, s, "flat")
        c.restore()
        if tied:
            f = clamp01((T - tb(3, k_rope)) / 0.35)
            for i, yy in enumerate((hy + 115 * s, hy + 175 * s, hy + 235 * s)):
                if f * 3 <= i:
                    break
                p = skia.Path()
                p.addOval(skia.Rect.MakeXYWH(x - 85 * s, yy - 18, 170 * s, 36))
                c.drawPath(p, wb.marker("#B07A44", 9))
    return None


ev(j, k_li3, pop_fn(j, k_li3, li3), "pop", 0.7)
b.hit(j, k_rope, "shaker", 0.8, "绳子把小李捆在本子前")


def boss3(c, sc, T, cx=cx, cy=cy):
    x, y, s = BO3
    hx, hy = head_of(x, y, s)
    point = T >= tb(3, k_guan)
    lh = (x - 150 * s, hy + 40 * s) if point else (x - 40 * s, y - 130 * s)
    with at_pop(c, x, y, sc):
        draw_boss(c, x, y, s, lh=lh, rh=(x + 40 * s, y - 130 * s), mood="flat")
    return None


ev(j, k_boss3, pop_fn(j, k_boss3, boss3), "wood_low")
ev(j, k_ban, L.slam_text("死板", cx - 300, cy - 400, 120, BLACK, j, k_ban, rot=-6), "rim")
ev(j, k_guan, L.slam_text("管人", cx + 260, cy - 400, 120, BLACK, j, k_guan, rot=6), "kick", 0.8)
b.shots[j].shake = [(k_guan, 10.0)]

# ================================================================ 屏 4：对照表——左列“我们以为”三条，右列问号；“反着来”
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
TB_X = (cx - 250, cx + 250)
TB_Y = [cy - 260 + i * 150 for i in range(3)]
LEFT4 = ["定了不改", "上面定的", "凭经验就行"]
L.note(*LEFT4, "1", "2", "3")
k_hd4 = 0
k_row = [kq(j, wt(4, 0, 0.3), 1)]
k_row += [k_row[0] + 1, k_row[0] + 2]
k_flip = max(kq(j, wt(4, 1, 0.7), k_row[2] + 1), k_row[2] + 1)


def table4(c, kk, T, cx=cx, cy=cy):
    f = ease_out(clamp01((T - tb(4, k_hd4)) / 0.5))
    if f <= 0:
        return None
    top, bot = cy - 440, TB_Y[-1] + 75
    dashed(c, (cx, top), (cx, top + (bot - top) * f), GRAY, 5)
    for x, s, fill, line in ((TB_X[0], VS_L, GRAY_FILL, GRAY), (TB_X[1], VS_R, GREEN_FILL, GREEN)):
        sc = pop_scale(T - tb(4, k_hd4) - (0 if x < cx else 0.12))
        if sc > 0:
            with K.at(c, x, cy - 400, 0, sc):
                box(c, 0, 0, 300, 86, fill, line, 6, 43)
                K.text(c, s, 0, 2, 54, "hand", line)
    for i, y in enumerate(TB_Y):
        sc = pop_scale(T - tb(4, k_row[i]))
        if sc <= 0:
            continue
        flipped = T >= tb(4, k_flip) + i * 0.15
        with K.at(c, TB_X[0], y, 0, sc):
            box(c, 0, 0, 420, 110, GRAY_FILL, GRAY, 6, 16)
            K.text(c, str(i + 1), -170, 2, 54, "hand", GRAY)
            K.text(c, LEFT4[i], 25, 2, 60, "hand", BLACK)
        with K.at(c, TB_X[1], y, 0, sc):
            box(c, 0, 0, 420, 110, "#FFFFFF", GREEN, 6, 16)
            g = pop_scale(T - tb(4, k_flip) - i * 0.15) if flipped else 0.0
            if g > 0:
                with K.at(c, 0, 0, 0, g):
                    qmark(c, 0, 4, 80, GREEN)
    return None


ev(j, k_hd4, table4, "wood_high")
for i in range(3):
    b.hit(j, k_row[i], ("wood_low", "wood_high", "wood_low")[i], 0.65, f"对照表左列第{i + 1}条")
LI4 = (cx - 360, cy + 430, 0.75)
k_li4 = max(0, k_flip - 1)


def li4(c, sc, T):
    x, y, s = LI4
    hx, hy = head_of(x, y, s)
    surprised = T >= tb(4, k_flip)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if surprised else "flat",
                rh=(x + 130 * s, hy - 30 * s) if surprised else None)
    return None


ev(j, k_li4, pop_fn(j, k_li4, li4), "pop", 0.6)


def flip4(c, kk, T, cx=cx, cy=cy):
    """“反着来”：两条弯箭头在两列之间来回翻。"""
    t0 = tb(4, k_flip)
    if T < t0:
        return None
    f = clamp01((T - t0) / 0.4)
    y = cy + 300
    for sgn in (1, -1):
        a = (cx - 120 * sgn, y - 40 * sgn)
        z = (cx + 120 * sgn, y - 40 * sgn)
        part, _ = wb.partial(wb.arrow(a, z, 0.35 * sgn, 34), f)
        c.drawPath(part, wb.marker(RED, 9))
    sc = C.slam_scale(T - t0 - 0.1)
    if sc > 0:
        with K.at(c, cx + 300, y, -4, sc):
            K.text(c, "反着来", 0, 0, 90, "hand", RED)
    return None


L.note("反着来")
ev(j, k_flip, flip4, "rim", 0.85, 0.4)
b.hit(j, k_flip + 1, "pop", 0.6, "右列问号逐个冒出")

# ================================================================ 屏 5：误区一——石碑“永远这样做”（红叉）vs 现在最好的做法（橡皮擦改一行）
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
vs_frame(j, 0, cx, cy, 1)
TAB5 = (cx - 265, cy + 40)
k_tab = max(1, kq(j, wt(5, 0, 0.6), 1))
k_x5 = max(kq(j, wt(5, 1, 0.15), k_tab + 1), k_tab + 1)
k_card5 = max(kq(j, wt(5, 1, 0.7), k_x5 + 1), k_x5 + 1)
k_erase = max(kq(j, wt(5, 2, 0.5), k_card5 + 1), k_card5 + 1)
k_new5 = max(kq(j, wt(5, 3, 0.4), k_erase + 1), k_erase + 1)
L.note("永远", "这样做", "现在最好的", "更快的")


def tablet5(c, sc, T, cx=cx, cy=cy):
    x, y = TAB5
    with at_pop(c, x, y + 330, sc):
        stone = skia.Path()
        stone.moveTo(x - 170, y + 330)
        stone.lineTo(x - 170, y - 180)
        stone.arcTo(skia.Rect.MakeXYWH(x - 170, y - 350, 340, 340), 180, 180, False)
        stone.lineTo(x + 170, y + 330)
        stone.close()
        c.drawPath(stone, K.paint("#C9CED6"))
        c.drawPath(stone, wb.marker("#5E6470", 8))
        c.drawLine(x - 210, y + 330, x + 210, y + 330, wb.marker("#5E6470", 10))
        K.text(c, "永远", x, y - 130, 86, "hand", "#4A4F5A")
        K.text(c, "这样做", x, y - 20, 86, "hand", "#4A4F5A")
        for i in range(3):
            c.drawLine(x - 110, y + 90 + i * 60, x + 110 - i * 30, y + 90 + i * 60, wb.marker("#8A8F99", 6))
    return None


ev(j, k_tab, pop_fn(j, k_tab, tablet5), "tom", 0.8)
big_x(j, k_x5, TAB5[0], TAB5[1] + 40, 170)
CARD5 = (cx + 265, cy - 120, 400, 420)
ROWS5 = [CARD5[1] - 90 + i * 80 for i in range(4)]
ERASE_ROW = 2


def card5(c, sc, T, cx=cx, cy=cy):
    x, y, w, h = CARD5
    t_e, t_n = tb(5, k_erase), tb(5, k_new5)
    with at_pop(c, x, y, sc):
        box(c, x, y, w, h, PAPER_FILL, GREEN, 7, 16)
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 6, y - h / 2 + 6, w - 12, 76), K.paint(GREEN_FILL))
        K.text(c, "现在最好的", x, y - h / 2 + 46, 56, "hand", GREEN)
        for i, yy in enumerate(ROWS5):
            K.text(c, str(i + 1), x - w / 2 + 45, yy, 44, "hand", GREEN)
            x0, x1 = x - w / 2 + 85, x + w / 2 - 40 - (i % 2) * 50
            if i == ERASE_ROW:
                fe = clamp01((T - t_e) / 0.5)
                if fe < 1:
                    c.save()
                    c.clipRect(skia.Rect.MakeLTRB(x0 + (x1 - x0) * fe, yy - 20, x1 + 10, yy + 20))
                    c.drawLine(x0, yy, x1, yy, wb.marker("#9AA0AC", 7))
                    c.restore()
                fn_ = clamp01((T - t_n) / 0.35)
                if fn_ > 0:
                    K.text(c, "更快的", x0 + 90, yy, 50, "hand", GREEN, fn_)
            else:
                c.drawLine(x0, yy, x1, yy, wb.marker("#9AA0AC", 7))
    return None


ev(j, k_card5, pop_fn(j, k_card5, card5), "wood_high")
WK5 = (cx + 340, cy + 430, 0.72)


def eraser_pos(T):
    t_e = tb(5, k_erase)
    x, y, w, h = CARD5
    x0, x1 = x - w / 2 + 85, x + w / 2 - 40
    f = clamp01((T - t_e) / 0.5)
    return lerp(x0, x1, f), ROWS5[ERASE_ROW] + 6 * math.sin((T - t_e) * 30) * (0 < f < 1)


def worker5(c, sc, T, cx=cx, cy=cy):
    x, y, s = WK5
    hx, hy = head_of(x, y, s)
    t_e = tb(5, k_erase)
    working = T >= t_e - 0.3
    if working:
        ex, ey = eraser_pos(T)
        rh = (ex, ey + 40)
    else:
        rh = (x + 70 * s, hy + 170 * s)
    with at_pop(c, x, y, sc):
        draw_worker(c, x, y, s, mood="smile" if T >= tb(5, k_new5) else "flat", rh=rh)
        if working:
            with K.at(c, rh[0], rh[1] - 25, -15):
                box(c, 0, 0, 70, 40, "#F28B82", BLACK, 4, 8)
                c.drawRect(skia.Rect.MakeXYWH(-35, 2, 70, 18), K.paint("#4A6FA5"))
    return None


ev(j, k_card5 + 1 if k_card5 + 1 < k_erase else k_card5, pop_fn(j, k_card5 + 1 if k_card5 + 1 < k_erase else k_card5,
                                                                 worker5))
b.hit(j, k_erase, "shaker", 0.8, "橡皮擦掉一行")
b.hit(j, k_new5, "ding", 0.75, "写上更快的做法")
b.path(j, k_new5 + 1, k_new5 + 1.4, check(CARD5[0] + 130, ROWS5[ERASE_ROW], 30), GREEN, 13, sfx="pop", gain=0.7)

# ================================================================ 屏 6：福特——今天的标准是台阶，明天站在上面再改
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_ford = kq(j, wt(6, 0, 0.25), 0)
STEP_W, STEP_H = 380, 230
ST0 = (cx - 470, cy + 430)         # 台阶左下角
L.note("福特说", "今天的标准", "明天", "改进", "基础")


def ford6(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 250, cy - 440
    with at_pop(c, x, y, sc):
        box(c, x, y, 340, 100, "#FFFFFF", BLACK, 6, 50)
        K.text(c, "福特说", x, y + 2, 62, "hand", BLACK)
        c.drawPath(P((x + 120, y + 50), (x + 150, y + 100), (x + 80, y + 50)), wb.marker(BLACK, 6))
    return None


ev(j, k_ford, pop_fn(j, k_ford, ford6), "pop")
k_st1 = max(kq(j, wt(6, 0, 0.75), k_ford + 1), k_ford + 1)
k_st2 = max(kq(j, wt(6, 1, 0.3), k_st1 + 1), k_st1 + 1)
k_climb = k_st2 + 1
k_base = max(kq(j, wt(6, 1, 0.85), k_climb + 1), k_climb + 1)


def step6(i):
    def draw(c, sc, T):
        x0 = ST0[0] + i * (STEP_W - 40)
        top = ST0[1] - (i + 1) * STEP_H
        with at_pop(c, x0 + STEP_W / 2, ST0[1], sc):
            r = skia.Rect.MakeXYWH(x0, top, STEP_W + (1 - i) * 0 + (i * 0), ST0[1] - top)
            c.drawRect(r, K.paint(BLUE_FILL if i == 0 else GREEN_FILL))
            c.drawRect(r, wb.marker(BLUE if i == 0 else GREEN, 8))
            K.text(c, "今天的标准" if i == 0 else "明天", x0 + STEP_W / 2, top + 70, 60 if i == 0 else 70, "hand",
                   BLUE if i == 0 else GREEN)
            if i == 0:
                for n in range(3):
                    yy = top + 140 + n * 30
                    c.drawLine(x0 + 50, yy, x0 + STEP_W - 60 - n * 30, yy, wb.marker("#9AA0AC", 5))
    return draw


ev(j, k_st1, pop_fn(j, k_st1, step6(0)), "wood_low")
ev(j, k_st2, pop_fn(j, k_st2, step6(1)), "wood_high")


def worker6(c, kk, T):
    """小王站在“今天”上，往上一步跳到“明天”。"""
    t0 = tb(6, k_st1) + 0.15
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    s = 0.62
    xa = ST0[0] + STEP_W / 2 + 60
    ya = ST0[1] - STEP_H
    xb = ST0[0] + (STEP_W - 40) + STEP_W / 2
    yb = ST0[1] - 2 * STEP_H
    g = ease_in_out(clamp01((T - tb(6, k_climb) + 0.35) / 0.35))
    x = lerp(xa, xb, g)
    y = lerp(ya, yb, g) - math.sin(g * math.pi) * 110
    hx, hy = head_of(x, y, s)
    up = g > 0
    with at_pop(c, x, y, sc):
        draw_worker(c, x, y, s, mood="smile" if g >= 1 else "flat",
                    lh=(x - 90 * s, hy - 40 * s) if up else None, rh=(x + 90 * s, hy - 40 * s) if up else None)
    return None


b.custom(j, k_st1, k_st1 + 0.3, worker6)
b.hit(j, k_climb, "bongo_high", 0.8, "小王跳上明天那一级")


def base6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_base)
    if T < t0:
        return None
    f = clamp01((T - t0) / 0.35)
    y = ST0[1] + 40
    part, tip = wb.partial(wb.underline(ST0[0] + 10, ST0[0] + STEP_W - 10, y, 12, 40), f)
    c.drawPath(part, wb.marker(RED, 10))
    sc = pop_scale(T - t0 - 0.2)
    if sc > 0:
        with K.at(c, cx + 390, cy - 120, 0, sc):
            c.drawPath(wb.arrow((0, 140), (0, -40), 0, 36), wb.marker(GREEN, 10))
            K.text(c, "改进", 0, -100, 70, "hand", GREEN)
    return tip


ev(j, k_base, base6, "ding", 0.8, 0.35)

# ================================================================ 屏 7：误区二——领导往下扔规定（红叉）vs 工人自己掐表、改步骤
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
vs_frame(j, 0, cx, cy, 2)
BO7 = (cx - 390, cy + 430, 0.8)
k_boss7 = max(1, kq(j, wt(7, 0, 0.5), 1))
k_throw = k_boss7 + 1
k_x7 = max(kq(j, wt(7, 1, 0.6), k_throw + 1), k_throw + 1)
k_fac = max(kq(j, wt(8, 0, 0.35), k_x7 + 1), k_x7 + 1)
k_watch = max(kq(j, wt(8, 1, 0.4), k_fac + 1), k_fac + 1)
k_rew = max(kq(j, wt(8, 2, 0.4), k_watch + 1), k_watch + 1)
L.note("规定", "合办工厂")
RULE_LAND = (cx - 160, cy + 410)


def boss7(c, sc, T):
    x, y, s = BO7
    hx, hy = head_of(x, y, s)
    t_t = tb(7, k_throw)
    up = t_t - 0.5 <= T < t_t + 0.1
    rh = (x + 110 * s, hy - 80 * s) if up else (x + 60 * s, y - 130 * s)
    with at_pop(c, x, y, sc):
        draw_boss(c, x, y, s, rh=rh, lh=(x - 40 * s, y - 130 * s), mood="flat")
    return None


ev(j, k_boss7, pop_fn(j, k_boss7, boss7), "wood_low")


def rules7(c, kk, T, cx=cx, cy=cy):
    t_t = tb(7, k_throw)
    if T < t_t - 0.45:
        return None
    x0, y0 = BO7[0] + 100, BO7[1] - 290 * BO7[2] - 100
    g = clamp01((T - t_t + 0.45) / 0.45)
    x = lerp(x0, RULE_LAND[0], g)
    y = lerp(y0, RULE_LAND[1] - 70, g) - math.sin(g * math.pi) * 180
    rot = lerp(-30, 0, g) + wobble(T - t_t, 5, 25, 8)
    with K.at(c, x, y, rot):
        box(c, 0, 0, 190, 140, "#3D4A63", BLACK, 6, 10)
        box(c, 0, -10, 130, 56, "#FFFFFF", BLACK, 4, 6)
        K.text(c, "规定", 0, -8, 46, "hand", BLACK)
    if T >= t_t:
        K.ripple(c, RULE_LAND[0], RULE_LAND[1], T - t_t, GRAY, 160, 5, 0.7, 0.4)
    return None


b.custom(j, k_throw - 1, k_throw - 0.7, rules7)
b.hit(j, k_throw, "tom", 0.9, "规定砸到地上")
big_x(j, k_x7, RULE_LAND[0], RULE_LAND[1] - 80, 115)
FAC = (cx + 270, cy - 330)


def factory7(c, sc, T, cx=cx, cy=cy):
    x, y = FAC
    with at_pop(c, x, y, sc):
        pts = [(x - 230, y + 60)]
        for i in range(3):
            x0 = x - 230 + i * 153
            pts += [(x0, y - 20), (x0 + 153, y + 30)]
        pts.append((x + 230, y + 60))
        c.drawPath(P(*pts), wb.marker(BLACK, 7))
        K.text(c, "合办工厂", x, y + 100, 56, "hand", BLACK)
    return None


ev(j, k_fac, pop_fn(j, k_fac, factory7), "wood_high")
WK7 = (cx + 430, cy + 430, 0.75)
CARD7 = (cx + 160, cy + 60, 250, 300)


def worker7(c, sc, T):
    x, y, s = WK7
    hx, hy = head_of(x, y, s)
    click = T >= tb(7, k_watch)
    writing = T >= tb(7, k_rew)
    if writing:
        rh = (CARD7[0] + 60 + 30 * math.sin((T - tb(7, k_rew)) * 10) * (T < tb(7, k_rew) + 0.6), CARD7[1] + 40)
    else:
        rh = (x + 70 * s, hy + 170 * s)
    lh = (x - 30 * s, hy - 20 * s) if click else (x - 70 * s, hy + 170 * s)
    with at_pop(c, x, y, sc):
        draw_worker(c, x, y, s, mood="smile" if writing else "flat", lh=lh, rh=rh)
        if click:
            f = (T - tb(7, k_watch)) / 3.0
            C_ = (lh[0] - 10, lh[1] - 60)
            c.drawCircle(C_[0], C_[1], 52, K.paint("#FFFFFF"))
            c.drawPath(wb.clock(C_[0], C_[1], 52), wb.marker(BLACK, 6))
            a = -math.pi / 2 + 2 * math.pi * f
            c.drawLine(C_[0], C_[1], C_[0] + math.cos(a) * 40, C_[1] + math.sin(a) * 40, wb.marker(RED, 6))
            c.drawRect(skia.Rect.MakeXYWH(C_[0] - 10, C_[1] - 74, 20, 16), K.paint(BLACK))
        if writing:
            c.drawLine(rh[0], rh[1], rh[0] + 30, rh[1] - 60, wb.marker(ORANGE, 10))
    return None


def card7(c, sc, T, cx=cx, cy=cy):
    x, y, w, h = CARD7
    with at_pop(c, x, y, sc):
        box(c, x, y, w, h, PAPER_FILL, GREEN, 6, 14)
        for i in range(3):
            yy = y - h / 2 + 70 + i * 80
            K.text(c, str(i + 1), x - w / 2 + 35, yy, 42, "hand", GREEN)
            if i == 1 and T >= tb(7, k_rew):
                f = clamp01((T - tb(7, k_rew)) / 0.5)
                c.drawLine(x - w / 2 + 65, yy, x - w / 2 + 65 + (w - 100) * f, yy, wb.marker(ORANGE, 8))
                c.drawLine(x - w / 2 + 65, yy - 24, x + w / 2 - 30, yy - 24 + 0 * f, wb.marker("#9AA0AC", 0.01))
            else:
                c.drawLine(x - w / 2 + 65, yy, x + w / 2 - 30 - (i % 2) * 30, yy, wb.marker("#9AA0AC", 6))
    return None


ev(j, k_fac, pop_fn(j, k_fac, card7))
ev(j, k_fac + 1 if k_fac + 1 < k_watch else k_fac, pop_fn(j, k_fac + 1 if k_fac + 1 < k_watch else k_fac, worker7),
   "pop", 0.6)
b.hit(j, k_watch, "rim", 0.85, "小王按下秒表")
b.hit(j, k_rew, "wood_low", 0.7, "小王改写一步")
b.path(j, k_rew + 1, k_rew + 1.4, check(CARD7[0] + 30, CARD7[1] - CARD7[3] / 2 - 50, 44), GREEN, 13, sfx="ding",
       gain=0.7)

# ================================================================ 屏 8：误区三——凭经验每次都不一样，错了找不到（红叉）vs 同一张流程，错哪一步一眼看到
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
vs_frame(j, 0, cx, cy, 3)
FLOW_R = [(cx + 270, cy - 280 + i * 165) for i in range(4)]
k_flowR = max(1, kq(j, wt(9, 1, 0.3), 1))
k_dotR = max(kq(j, wt(9, 2, 0.4), k_flowR + 1), k_flowR + 1)
k_ptR = max(kq(j, wt(9, 3, 0.6), k_dotR + 1), k_dotR + 1)


def flow_r(c, sc, T, cx=cx, cy=cy):
    x = FLOW_R[0][0]
    with at_pop(c, x, cy, sc):
        for i, (fx, fy) in enumerate(FLOW_R):
            if i:
                c.drawPath(wb.arrow((fx, fy - 120), (fx, fy - 48), 0, 18), wb.marker(GREEN, 5))
            bad = i == 2 and T >= tb(8, k_dotR)
            step_box(c, fx, fy, i + 1, 170, 84, RED_FILL if bad else GREEN_FILL, RED if bad else GREEN)
    return None


ev(j, k_flowR, pop_fn(j, k_flowR, flow_r), "wood_high")


def dot_r(c, kk, T):
    t0 = tb(8, k_dotR)
    if T < t0:
        return None
    fx, fy = FLOW_R[2]
    K.ripple(c, fx + 120, fy, T - t0, RED, 90, 5, 0.8, 0.5)
    c.drawCircle(fx + 120, fy, 20 * pop_scale(T - t0), K.paint(RED))
    t1 = tb(8, k_ptR)
    if T >= t1:
        f = clamp01((T - t1) / 0.3)
        part, tip = wb.partial(wb.arrow((fx + 230, fy - 110), (fx + 150, fy - 30), 0.2, 26), f)
        c.drawPath(part, wb.marker(RED, 8))
        if f < 1:
            return tip
    return None


ev(j, k_dotR, dot_r, "rim", 0.8)
b.hit(j, k_ptR, "ding", 0.75, "箭头指着出错那一步")
# 左栏：三张不一样的流程叠在一起
k_flowL = max(kq(j, wt(10, 0, 0.35), k_ptR + 1), k_ptR + 1)
k_dotL = max(kq(j, wt(10, 1, 0.3), k_flowL + 3), k_flowL + 3)
k_mag = k_dotL + 1
k_xL = max(kq(j, wt(10, 2, 0.6), k_mag + 1), k_mag + 1)
FLOWS_L = [  # (dx, dy, 步骤序号顺序, 旋转)
    (-120, -60, [1, 2, 3], -6),
    (0, 0, [2, 1, 4, 3], 3),
    (110, 70, [1, 3], -2),
]


def flows_l(c, kk, T, cx=cx, cy=cy):
    for n, (dx, dy, order, rot) in enumerate(FLOWS_L):
        sc = pop_scale(T - tb(8, k_flowL + n))
        if sc <= 0:
            continue
        x0, y0 = cx - 270 + dx, cy - 200 + dy
        with K.at(c, x0, y0 + 150, rot, sc):
            box(c, 0, 0, 230, 120 + 95 * len(order), "#FFFFFF", GRAY, 5, 14, 0.95)
            for i, st in enumerate(order):
                step_box(c, 0, -((len(order) - 1) * 95) / 2 + i * 95, st, 120, 70,
                         ("#E4EDFA", "#FBE0C6", "#ECEEF1")[n], (BLUE, ORANGE, GRAY)[n])
    return None


b.custom(j, k_flowL, k_flowL + 0.3, flows_l)
for n in range(3):
    b.hit(j, k_flowL + n, ("wood_low", "wood_high", "wood_low")[n], 0.6, f"第{n + 1}张做法不一样的流程")


def mag_l(c, kk, T, cx=cx, cy=cy):
    t_d = tb(8, k_dotL)
    if T < t_d:
        return None
    a = pop_scale(T - t_d)
    c.drawCircle(cx - 160, cy + 20, 18 * a, K.paint(RED))
    t_m = tb(8, k_mag)
    if T >= t_m:
        sc = pop_scale(T - t_m)
        u = (T - t_m) * 1.8
        mx, my = cx - 270 + 110 * math.sin(u), cy - 60 + 130 * math.sin(u * 1.37)
        with K.at(c, mx, my, 0, sc):
            c.drawCircle(0, 0, 70, K.paint("#E4EDFA", 0.4))
            c.drawCircle(0, 0, 70, wb.marker(BLUE, 9))
            c.drawLine(50, 50, 110, 110, wb.marker(BLUE, 16))
            qmark(c, 0, 4, 70, BLUE)
    return None


ev(j, k_dotL, mag_l, "pop", 0.7)
b.hit(j, k_mag, "shaker", 0.7, "放大镜到处找")
big_x(j, k_xL, cx - 270, cy + 330, 110, 0.8)

# ================================================================ 屏 9：三次按同一个步骤做，第三次第 3 步歪了，一比就看出来；扶正→改进
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
ROW9_Y = [cy - 380 + i * 165 for i in range(3)]
COL9_X = [cx - 230 + i * 170 for i in range(4)]
k_rows9 = [kq(j, wt(11, 0, 0.2), 0)]
k_rows9 += [k_rows9[0] + 1, k_rows9[0] + 2]
k_dev = max(kq(j, wt(11, 1, 0.6), k_rows9[2] + 1), k_rows9[2] + 1)
k_cmp = max(kq(j, wt(11, 2, 0.5), k_dev + 1), k_dev + 1)
k_fix = max(kq(j, wt(12, 0, 0.5), k_cmp + 1), k_cmp + 1)
k_up = max(kq(j, wt(12, 1, 0.5), k_fix + 1), k_fix + 1)
L.note("第1次", "第2次", "第3次", "改进")


def rows9(c, kk, T, cx=cx, cy=cy):
    t_dev, t_fix = tb(9, k_dev), tb(9, k_fix)
    for r, y in enumerate(ROW9_Y):
        sc = pop_scale(T - tb(9, k_rows9[r]))
        if sc <= 0:
            continue
        with K.at(c, cx, y, 0, sc):
            c.translate(-cx, -y)
            K.text(c, f"第{r + 1}次", cx - 420, y, 50, "hand", BLACK)
            for i, x in enumerate(COL9_X):
                if i:
                    c.drawPath(wb.arrow((x - 115, y), (x - 70, y), 0, 16), wb.marker(BLUE, 5))
                bad = r == 2 and i == 2
                off = 0.0
                rot = 0.0
                if bad:
                    g = ease_out(clamp01((T - t_dev) / 0.3)) * (1 - ease_in_out(clamp01((T - t_fix) / 0.35)))
                    off, rot = 46 * g, 18 * g
                col = ORANGE if (bad and t_dev <= T < t_fix) else (GREEN if (bad and T >= t_fix) else BLUE)
                fill = "#FBE0C6" if col == ORANGE else (GREEN_FILL if col == GREEN else BLUE_FILL)
                step_box(c, x, y + off, i + 1, 110, 80, fill, col, rot=rot)
    return None


b.custom(j, k_rows9[0], k_rows9[0] + 0.3, rows9)
for r in range(3):
    b.hit(j, k_rows9[r], ("wood_low", "wood_high", "wood_low")[r], 0.65, f"第{r + 1}次按同一张流程做")
b.hit(j, k_dev, "bongo_low", 0.8, "第三次第3步歪了")


def band9(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k_cmp)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.3))
    fade = 1 - 0.7 * clamp01((T - tb(9, k_fix)) / 0.3)
    x = COL9_X[2]
    top, bot = ROW9_Y[0] - 70, ROW9_Y[2] + 110
    r = skia.Rect.MakeLTRB(x - 75, top, x + 75, top + (bot - top) * f)
    c.drawRoundRect(r, 20, 20, K.paint(RED, 0.10 * fade))
    c.drawRoundRect(r, 20, 20, wb.marker(RED, 7, fade))
    return None


ev(j, k_cmp, band9, "ding", 0.85)
LD9 = (cx + 380, cy + 430, 0.78)


def leader9(c, sc, T):
    x, y, s = LD9
    with at_pop(c, x, y, sc):
        draw_leader(c, x, y, s, head_dx=-6 if T >= tb(9, k_cmp) else 0.0)
    return None


ev(j, k_rows9[0] + 1, pop_fn(j, k_rows9[0] + 1, leader9))


def up9(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k_up)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.4))
    base_y = cy + 300
    x0 = cx - 420
    c.drawRoundRect(skia.Rect.MakeXYWH(x0, base_y, 560, 90), 14, 14, K.paint(BLUE_FILL))
    c.drawRoundRect(skia.Rect.MakeXYWH(x0, base_y, 560, 90), 14, 14, wb.marker(BLUE, 6))
    K.text(c, "同一张流程", x0 + 280, base_y + 46, 52, "hand", BLUE)
    ax = x0 + 280
    part, tip = wb.partial(wb.arrow((ax, base_y - 10), (ax + 40, base_y - 10 - 150 * f), 0.1, 30), 1.0)
    c.drawPath(part, wb.marker(GREEN, 11))
    sc = pop_scale(T - t0 - 0.2)
    if sc > 0:
        with K.at(c, ax + 170, base_y - 120, 0, sc):
            K.text(c, "改进", 0, 0, 76, "hand", GREEN)
    return None


L.note("同一张流程")
b.hit(j, k_fix, "pop", 0.75, "歪掉的一步扶正、变绿")
ev(j, k_up, up9, "ding", 0.8)

# ================================================================ 屏 10：每月做报表——四个月，三月忘了更新数据（红圈）
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
LI10 = (cx - 330, cy + 430, 0.85)
DK10 = (cx - 170, cy + 250)
ev(j, 0, L.figure(draw_li, j, 0, *LI10, mood=lambda T: "sad" if T >= tb(10, k_old) else "flat",
                  lh=lambda T: (LI10[0] + 60, DK10[1] - 10 + 6 * math.sin(T * 14)),
                  rh=lambda T: (LI10[0] + 140, DK10[1] - 10 - 6 * math.sin(T * 14))), "pop", 0.6)
b.path(j, 0.3, 1.0, wb.desk(DK10[0], DK10[1], 340), BLACK, 8)
MON = [(cx - 330 + i * 220, cy - 330) for i in range(4)]
L.note("1月", "2月", "3月", "4月", "旧数据", "从头想")
k_m = [kq(j, wt(14, 0, 0.1), 2)]
k_m += [k_m[0] + i for i in range(1, 4)]
k_think = max(kq(j, wt(14, 1, 0.35), k_m[3] + 1), k_m[3] + 1)
k_old = max(kq(j, wt(14, 2, 0.7), k_think + 1), k_think + 1)


def months10(c, kk, T):
    for i, (x, y) in enumerate(MON):
        sc = pop_scale(T - tb(10, k_m[i]))
        if sc <= 0:
            continue
        stale = i == 2 and T >= tb(10, k_old)
        with K.at(c, x, y, 0, sc):
            box(c, 0, 0, 190, 230, "#FFFFFF", BLACK, 6, 12)
            c.drawRect(skia.Rect.MakeXYWH(-89, -109, 178, 50), K.paint(RED_FILL if stale else BLUE_FILL))
            K.text(c, f"{i + 1}月", 0, -82, 44, "hand", BLACK)
            for n, hh in enumerate((40, 70, 55, 95) if not stale else (40, 70, 55, 30)):
                bx = -60 + n * 40
                col = GRAY if stale and n == 3 else BLUE
                c.drawRect(skia.Rect.MakeXYWH(bx - 14, 90 - hh, 28, hh), K.paint(GRAY_FILL if stale and n == 3 else BLUE_FILL))
                c.drawRect(skia.Rect.MakeXYWH(bx - 14, 90 - hh, 28, hh), wb.marker(col, 4))
    return None


b.custom(j, k_m[0], k_m[0] + 0.3, months10)
for i in range(4):
    b.hit(j, k_m[i], ("wood_low", "wood_high")[i % 2], 0.6, f"{i + 1}月报表")


def think10(c, kk, T, cx=cx, cy=cy):
    t0 = tb(10, k_think)
    if T < t0:
        return None
    sc = pop_scale(T - t0)
    x, y = cx + 60, cy + 50
    with K.at(c, x, y, 0, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(-200, -90, 400, 180), 80, 80, K.paint("#FFFFFF"))
        c.drawRoundRect(skia.Rect.MakeXYWH(-200, -90, 400, 180), 80, 80, wb.marker(BLACK, 6))
        for n, (dx, dy, r) in enumerate(((-230, 50, 18), (-290, 80, 12))):
            c.drawCircle(dx, dy, r, K.paint("#FFFFFF"))
            c.drawCircle(dx, dy, r, wb.marker(BLACK, 5))
        sp = skia.Path()
        rot = (T - t0) * 260
        for i in range(60):
            a = math.radians(i * 14 + rot)
            rr = 4 + i * 0.85
            px, py = -110 + math.cos(a) * rr, math.sin(a) * rr
            sp.moveTo(px, py) if i == 0 else sp.lineTo(px, py)
        c.drawPath(sp, wb.marker(BLUE, 5))
        K.text(c, "从头想", 60, 0, 60, "hand", BLUE)
    return None


ev(j, k_think, think10, "shaker", 0.8)


def old10(c, kk, T, cx=cx, cy=cy):
    t0 = tb(10, k_old)
    if T < t0:
        return None
    f = clamp01((T - t0) / 0.35)
    x, y = MON[2]
    ring = skia.Path()
    ring.addOval(skia.Rect.MakeXYWH(x - 135, y - 155, 270, 310))
    part, tip = wb.partial(ring, f)
    c.drawPath(part, wb.marker(RED, 9))
    sc = pop_scale(T - t0 - 0.25)
    if sc > 0:
        with K.at(c, x, y + 205, 0, sc):
            K.text(c, "旧数据", 0, 0, 60, "hand", RED)
    return tip if f < 1 else None


ev(j, k_old, old10, "rim", 0.85, 0.35)

# ================================================================ 屏 11：同事请假——空座位；小李对着一堆文件发愣；小王脑子里装着流程
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
CH11 = (cx - 330, cy + 300)
k_chair = 0
k_note = kq(j, wt(15, 0, 0.6), 1)
k_pile = max(kq(j, wt(15, 1, 0.3), k_note + 1), k_note + 1)
k_li11 = k_pile + 1
k_head = max(kq(j, wt(15, 2, 0.5), k_li11 + 1), k_li11 + 1)
L.note("请假")


def chair11(c, sc, T):
    x, y = CH11
    with at_pop(c, x, y + 130, sc):
        c.drawPath(wb.desk(x, y - 40, 300), wb.marker(BLACK, 8))
        ch = P((x - 60, y - 180 + 200), (x - 60, y + 130), (x - 60, y + 30), (x + 40, y + 30), (x + 40, y + 130))
        c.drawPath(join(ch, P((x - 60, y + 30), (x - 75, y - 70))), wb.marker(GRAY, 8))
    return None


ev(j, k_chair, pop_fn(j, k_chair, chair11), "wood_high")


def note11(c, kk, T):
    t0 = tb(11, k_note)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    x, y = CH11[0] + 40, CH11[1] - 180
    with K.at(c, x, y, -8, sc):
        sticky(c, 0, 0, 170, 120)
        K.text(c, "请假", 0, 0, 62, "hand", RED)
    return None


ev(j, k_note, note11, "rim", 0.8)


def pile11(c, kk, T, cx=cx, cy=cy):
    t0 = tb(11, k_pile)
    for i in range(6):
        f = pop_scale(T - t0 - i * 0.07, 0.2)
        if f <= 0:
            continue
        with K.at(c, cx + 20 + ((i * 29) % 21 - 10), cy + 330 - i * 34, (i % 3 - 1) * 4, f):
            box(c, 0, 0, 200, 32, "#FFFFFF", BLACK, 4, 4)
    return None


ev(j, k_pile, pile11, "wood_low", 0.7)
LI11 = (cx + 200, cy + 430, 0.8)


def li11(c, sc, T, cx=cx, cy=cy):
    x, y, s = LI11
    hx, hy = head_of(x, y, s)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad", lh=(x - 110 * s, hy + 120 * s), rh=(x + 80 * s, hy + 170 * s))
        a = pop_scale(T - tb(11, k_li11) - 0.3)
        if a > 0:
            with K.at(c, hx - 90, hy - 80, 0, a):
                qmark(c, 0, 0, 90, BLUE)
                qmark(c, 50, -30, 60, BLUE)
    return None


ev(j, k_li11, pop_fn(j, k_li11, li11), "pop", 0.7)
WK11 = (cx + 330, cy - 120, 0.62)


def head11(c, sc, T, cx=cx, cy=cy):
    """右上：小王（在家）头上一个大想法泡，里面是一整张流程。"""
    x, y, s = WK11
    hx, hy = head_of(x, y, s)
    with at_pop(c, x, y, sc):
        draw_worker(c, x, y, s, mood="smile")
        bx, by = cx - 20, cy - 360
        c.drawRoundRect(skia.Rect.MakeXYWH(bx - 230, by - 110, 460, 220), 90, 90, K.paint("#FFFFFF"))
        c.drawRoundRect(skia.Rect.MakeXYWH(bx - 230, by - 110, 460, 220), 90, 90, wb.marker(BLACK, 6))
        for dx, dy, r in ((hx - 120, hy - 70, 22), (hx - 70, hy - 40, 14)):
            c.drawCircle(dx, dy, r, K.paint("#FFFFFF"))
            c.drawCircle(dx, dy, r, wb.marker(BLACK, 5))
        for i in range(4):
            fx = bx - 165 + i * 110
            if i:
                c.drawPath(wb.arrow((fx - 70, by), (fx - 42, by), 0, 12), wb.marker(BLUE, 4))
            step_box(c, fx, by, i + 1, 74, 64)
    return None


ev(j, k_head, pop_fn(j, k_head, head11), "ding", 0.75)

# ================================================================ 屏 12：出差收拾行李——箱子塞满盖上，充电器还插在墙上
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
SC12 = (cx - 120, cy + 260)
k_case = 0
k_items = [kq(j, wt(16, 0, 0.3), 1)]
k_items += [k_items[0] + 1, k_items[0] + 2]
k_lid = k_items[2] + 1
k_plug = max(kq(j, wt(16, 1, 0.6), k_lid + 1), k_lid + 1)
L.note("充电器")


def case12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_case))
    if sc <= 0:
        return None
    x, y = SC12
    with at_pop(c, x, y + 120, sc):
        box(c, x, y, 460, 240, "#F1DDB8", "#A9773E", 8, 20)
        for i, kind in enumerate(("shirt", "shoe", "book")):
            f = pop_scale(T - tb(12, k_items[i]), 0.22)
            if f <= 0:
                continue
            ix = x - 140 + i * 140
            with K.at(c, ix, y - 40 - (1 - f) * 120, (i - 1) * 8, f):
                if kind == "shirt":
                    c.drawPath(P((-55, -40), (-20, -55), (20, -55), (55, -40), (45, 40), (-45, 40), close=True),
                               K.paint(BLUE_FILL))
                    c.drawPath(P((-55, -40), (-20, -55), (20, -55), (55, -40), (45, 40), (-45, 40), close=True),
                               wb.marker(BLUE, 5))
                elif kind == "shoe":
                    c.drawPath(P((-50, 20), (-50, -30), (-10, -30), (10, 0), (55, 10), (55, 25), close=True),
                               K.paint("#FBE0C6"))
                    c.drawPath(P((-50, 20), (-50, -30), (-10, -30), (10, 0), (55, 10), (55, 25), close=True),
                               wb.marker(ORANGE, 5))
                else:
                    box(c, 0, 0, 90, 110, GREEN_FILL, GREEN, 5, 8)
        t_l = tb(12, k_lid)
        g = ease_in_out(clamp01((T - t_l + 0.3) / 0.3))
        ang = lerp(-75, 0, g) + wobble(T - t_l, 4, 30, 9)
        with K.at(c, x - 230, y - 120, ang):
            box(c, 230, -20, 460, 40, "#E9C891", "#A9773E", 7, 14)
        if g >= 1:
            box(c, x, y - 140, 120, 26, "#A9773E", "#7A5228", 5, 12)
    return None


ev(j, k_case, case12, "wood_low", 0.7)
for i in range(3):
    b.hit(j, k_items[i], ("pop", "pop", "pop")[i], 0.55, "东西塞进箱子")
b.hit(j, k_lid, "tom", 0.85, "箱盖压上")
LI12 = (cx + 330, cy + 430, 0.8)
ev(j, k_lid, L.figure(draw_li, j, k_lid, *LI12, mood=lambda T: "o" if T >= tb(12, k_plug) else "smile",
                      lh=lambda T: (LI12[0] - 130, LI12[1] - 150)))


def plug12(c, kk, T, cx=cx, cy=cy):
    """左上：墙上插座，充电器还插着（红圈）。"""
    t0 = tb(12, k_plug)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx - 280, cy - 300
    with at_pop(c, x, y, sc):
        box(c, x, y, 170, 200, "#FFFFFF", BLACK, 6, 18)
        for dx in (-25, 25):
            c.drawRoundRect(skia.Rect.MakeXYWH(x + dx - 7, y - 40, 14, 34), 4, 4, K.paint(BLACK))
        box(c, x, y + 10, 90, 70, "#F5F5F5", BLACK, 5, 10)
        cord = skia.Path()
        cord.moveTo(x, y + 45)
        cord.cubicTo(x + 10, y + 170, x + 140, y + 60, x + 200, y + 150)
        c.drawPath(cord, wb.marker(BLACK, 6))
        ring = skia.Path()
        ring.addOval(skia.Rect.MakeXYWH(x - 130, y - 150, 260, 300))
        part, _ = wb.partial(ring, clamp01((T - t0 - 0.15) / 0.3))
        c.drawPath(part, wb.marker(RED, 9))
        K.text(c, "充电器", x + 270, y - 30, 64, "hand", RED, clamp01((T - t0 - 0.3) / 0.2))
    return None


ev(j, k_plug, plug12, "rim", 0.85)
b.shots[j].shake = [(k_plug, 8.0)]

# ================================================================ 屏 13：做熟了就凭感觉——小李蒙着眼做，一百个箭头指向四面八方
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
LI13 = (cx - 40, cy + 430, 0.85)
k_task = 0
k_li13 = kq(j, wt(17, 0, 0.5), 1)
k_mask = max(kq(j, wt(17, 1, 0.6), k_li13 + 1), k_li13 + 1)
k_arr = max(kq(j, wt(18, 0, 0.4), k_mask + 1), k_mask + 1)
k_100 = max(kq(j, wt(18, 1, 0.55), k_arr + 2), k_arr + 2)
L.note("做熟了", "凭感觉", "一百种")


def task13(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 330, cy - 420
    with at_pop(c, x, y, sc):
        box(c, x, y, 300, 100, "#FFFFFF", BLACK, 6, 16)
        K.text(c, "做熟了", x - 20, y + 2, 60, "hand", BLACK)
        c.drawPath(check(x + 105, y, 26), wb.marker(GREEN, 9))
    return None


ev(j, k_task, pop_fn(j, k_task, task13), "wood_high")


def li13(c, sc, T, cx=cx, cy=cy):
    x, y, s = LI13
    hx, hy = head_of(x, y, s)
    mask = T >= tb(13, k_mask)
    sway = 10 * math.sin((T - tb(13, k_mask)) * 3) if mask else 0.0
    with at_pop(c, x, y, sc):
        draw_li(c, x + sway * 0.3, y, s, "smile",
                lh=(x - 120 * s + sway, hy + 60 * s), rh=(x + 120 * s + sway, hy + 60 * s))
        if mask:
            f = ease_out(clamp01((T - tb(13, k_mask)) / 0.25))
            c.drawRoundRect(skia.Rect.MakeXYWH(hx + sway * 0.3 - 52 * s, hy - 24 * s, 104 * s * f, 34 * s), 10, 10,
                            K.paint(BLACK))
            if f >= 1:
                c.drawPath(P((hx + 50 * s, hy - 8 * s), (hx + 90 * s, hy - 30 * s)), wb.marker(BLACK, 6))
                c.drawPath(P((hx + 50 * s, hy - 8 * s), (hx + 90 * s, hy + 12 * s)), wb.marker(BLACK, 6))
    return None


ev(j, k_li13, pop_fn(j, k_li13, li13), "pop", 0.7)
b.hit(j, k_mask, "wood_low", 0.75, "蒙上眼罩")
ev(j, k_mask, L.pop_text("凭感觉", cx + 290, cy - 420, 76, BLUE, j, k_mask))
ARR_COLS = [BLUE, ORANGE, GREEN, RED, "#7A5AA6"]


def arrows13(c, kk, T, cx=cx, cy=cy):
    """一百种做法：从小李手里往四面八方射出箭头，分三拍一批批出来。"""
    hx, hy = LI13[0], LI13[1] - 290 * LI13[2] + 60
    n_tot = 22
    for n in range(n_tot):
        batch = n % 3
        t0 = tb(13, k_arr + batch) + (n // 3) * 0.03
        f = ease_out(clamp01((T - t0) / 0.25))
        if f <= 0:
            continue
        a = math.radians(-170 + n * (160 / (n_tot - 1)) + (n * 37 % 11 - 5))
        r0, r1 = 160, 300 + (n * 53 % 120)
        a0 = (hx + math.cos(a) * r0, hy + math.sin(a) * r0)
        a1 = (hx + math.cos(a) * lerp(r0, r1, f), hy + math.sin(a) * lerp(r0, r1, f))
        c.drawPath(wb.arrow(a0, a1, 0.08 * ((n % 3) - 1), 22 * f), wb.marker(ARR_COLS[n % 5], 6))
    return None


b.custom(j, k_arr, k_arr + 0.3, arrows13)
b.hit(j, k_arr, "shaker", 0.7, "箭头一批批射出")
b.hit(j, k_arr + 1, "wood_high", 0.55, "箭头第二批")
ev(j, k_100, L.stamp("一百种", cx + 250, cy + 150, 84, j, k_100, rot=7), "kick", 0.8)
b.shots[j].shake = [(k_100, 9.0)]

# ================================================================ 屏 14：写步骤又慢又烦，活都干不完——小李叹气；就从这三步开始
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
LI14 = (cx - 330, cy + 430, 0.82)
k_li14 = 0
k_snail = max(kq(j, wt(19, 1, 0.55), 1), 1)
k_scroll = max(kq(j, wt(19, 2, 0.4), k_snail + 1), k_snail + 1)
k_3 = max(kq(j, wt(20, 1, 0.45), k_scroll + 2), k_scroll + 2)
L.note("写步骤", "三步")


def li14(c, sc, T):
    x, y, s = LI14
    hx, hy = head_of(x, y, s)
    happy = T >= tb(14, k_3)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if happy else "sad", squash=1.0 if happy else 0.95,
                rh=(x + 120 * s, hy - 20 * s) if happy else None)
        if not happy:
            ph = ((T - tb(14, k_li14)) * 0.8) % 1.0
            c.drawCircle(hx + 80 * s + ph * 40, hy + 20 * s - ph * 30, 14 + ph * 10, wb.marker(GRAY, 4, 1 - ph))
    return None


ev(j, k_li14, pop_fn(j, k_li14, li14), "pop", 0.6)


def snail14(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 220, cy - 330
    with at_pop(c, x, y, sc):
        box(c, x, y, 280, 210, "#FFFFFF", BLACK, 6, 12)
        K.text(c, "写步骤", x, y - 60, 54, "hand", BLACK)
        c.drawLine(x - 90, y + 10, x - 30, y + 10, wb.marker("#9AA0AC", 6))
        sx = x + 30 + 18 * clamp01((T - tb(14, k_snail)) / 4)
        sy = y + 70
        c.drawCircle(sx, sy - 22, 26, K.paint("#FBE0C6"))
        sp = skia.Path()
        for i in range(30):
            a = math.radians(i * 22)
            rr = 2 + i * 0.75
            px, py = sx + math.cos(a) * rr, sy - 22 + math.sin(a) * rr
            sp.moveTo(px, py) if i == 0 else sp.lineTo(px, py)
        c.drawPath(sp, wb.marker(ORANGE, 4))
        c.drawCircle(sx, sy - 22, 26, wb.marker(ORANGE, 5))
        c.drawPath(P((sx - 30, sy + 4), (sx + 55, sy + 4), (sx + 70, sy - 20)), wb.marker(ORANGE, 6))
        c.drawPath(join(P((sx + 60, sy - 14), (sx + 58, sy - 44)), P((sx + 70, sy - 18), (sx + 78, sy - 46))),
                   wb.marker(ORANGE, 4))
    return None


ev(j, k_snail, pop_fn(j, k_snail, snail14), "wood_high")


def scroll14(c, kk, T, cx=cx, cy=cy):
    """长长的待办清单从桌上一路滚到地上。"""
    t0 = tb(14, k_scroll)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.6))
    x, top = cx + 200, cy - 430
    hh = 820 * f
    c.drawRect(skia.Rect.MakeXYWH(x - 120, top, 240, hh), K.paint("#FFFFFF"))
    c.drawRect(skia.Rect.MakeXYWH(x - 120, top, 240, hh), wb.marker(BLACK, 6))
    n = int(hh / 52)
    for i in range(n):
        yy = top + 34 + i * 52
        checkbox(c, x - 85, yy, 28, None)
        c.drawLine(x - 55, yy, x + 90 - (i * 37 % 40), yy, wb.marker("#9AA0AC", 5))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 140, top + hh - 20, 280, 40), 20, 20, K.paint("#E9D2AE"))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 140, top + hh - 20, 280, 40), 20, 20, wb.marker("#A9773E", 6))
    return None


ev(j, k_scroll, scroll14, "shaker", 0.8)
b.hit(j, k_scroll + 1, "tom", 0.7, "清单滚到地上")


def three14(c, kk, T, cx=cx, cy=cy):
    t0 = tb(14, k_3)
    if T < t0:
        return None
    for i in range(3):
        sc = C.slam_scale(T - t0 - i * 0.0) if i == 0 else pop_scale(T - tb(14, k_3 + i))
        if sc <= 0:
            continue
        x, y = cx - 300 + i * 150, cy - 40 + (i % 2) * 20
        with K.at(c, x, y, (i - 1) * 6, sc):
            sticky(c, 0, 0, 120, 110)
            K.text(c, str(i + 1), 0, 2, 72, "hand", RED)
    sc = pop_scale(T - t0 - 0.1)
    with K.at(c, cx - 150, cy + 100, 0, sc):
        K.text(c, "三步", 0, 0, 80, "hand", RED)
    return None


ev(j, k_3, three14, "kick", 0.8)
b.hit(j, k_3 + 1, "pop", 0.6, "便签 2")
b.hit(j, k_3 + 2, "pop", 0.6, "便签 3")

# ================================================================ 屏 15：做法一——挑一件每周都做的事，下次做的时候顺手记下步骤
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
ev(j, 0, L.pop_text("① 每周那件事", cx, cy - 460, 88, BLUE, j, 0), "pop")
WEEK = [(cx - 390 + i * 130, cy - 290) for i in range(7)]
k_wk15 = 1
k_pick = max(kq(j, wt(21, 1, 0.6), 2), 2)
k_li15 = max(kq(j, wt(21, 2, 0.3), k_pick + 1), k_pick + 1)
k_wr = max(kq(j, wt(21, 3, 0.2), k_li15 + 1), k_li15 + 1)
L.note("一二三四五六日", "报表")


def week15(c, kk, T, cx=cx, cy=cy):
    for i, (x, y) in enumerate(WEEK):
        sc = pop_scale(T - tb(15, k_wk15) - i * 0.06, 0.22)
        if sc <= 0:
            continue
        picked = i == 0 and T >= tb(15, k_pick)
        with K.at(c, x, y, 0, sc):
            box(c, 0, 0, 110, 120, GREEN_FILL if picked else "#FFFFFF", GREEN if picked else BLACK, 5, 10)
            K.text(c, "一二三四五六日"[i], 0, -26, 42, "hand", BLACK)
            if i == 0:
                K.text(c, "报表", 0, 26, 38, "hand", BLUE)
    t0 = tb(15, k_pick)
    if T >= t0:
        x, y = WEEK[0]
        ring = skia.Path()
        ring.addOval(skia.Rect.MakeXYWH(x - 85, y - 95, 170, 190))
        part, tip = wb.partial(ring, clamp01((T - t0) / 0.3))
        c.drawPath(part, wb.marker(RED, 8))
    return None


b.custom(j, k_wk15, k_wk15 + 0.3, week15, sfx="wood_high")
b.hit(j, k_pick, "ding", 0.75, "圈出每周一做报表")
LI15 = (cx - 300, cy + 430, 0.82)
NOTE15 = (cx + 200, cy + 150)


def li15(c, sc, T):
    x, y, s = LI15
    hx, hy = head_of(x, y, s)
    wr = T >= tb(15, k_wr)
    n = min(3, int((T - tb(15, k_wr)) / 0.53) + 1) if wr else 0
    pen = (NOTE15[0] - 60 + 30 * math.sin(T * 12), NOTE15[1] - 70 + (n - 1) * 60) if wr else (x + 110 * s, hy + 130 * s)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if wr else "flat", rh=pen)
        c.drawPath(wb.desk(x + 230, y - 150, 300), wb.marker(BLACK, 7))
    return None


ev(j, k_li15, pop_fn(j, k_li15, li15), "pop", 0.6)


def note15(c, kk, T, cx=cx, cy=cy):
    t0 = tb(15, k_li15)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = NOTE15
    with K.at(c, x, y, -3, sc):
        sticky(c, 0, 0, 280, 250)
        for i in range(3):
            if T < tb(15, k_wr + i):
                continue
            yy = -70 + i * 60
            K.text(c, str(i + 1), -100, yy, 46, "hand", BLUE)
            f = clamp01((T - tb(15, k_wr + i)) / 0.4)
            c.drawLine(-70, yy, -70 + 160 * f, yy, wb.marker(BLUE, 6))
    return None


b.custom(j, k_li15, k_li15 + 0.3, note15)
for i in range(3):
    b.hit(j, k_wr + i, ("wood_high", "wood_low", "wood_high")[i], 0.6, f"便签上写第{i + 1}步")

# ================================================================ 屏 16：做法二——出一次错，清单上加一行
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
ev(j, 0, L.pop_text("② 错一次，加一行", cx, cy - 460, 84, BLUE, j, 0), "pop")
CL16 = (cx - 120, cy - 20, 460, 600)
ROW16 = [CL16[1] - 170 + i * 100 for i in range(4)]
k_cl16 = 1
k_err16 = max(kq(j, wt(22, 1, 0.5), 2), 2)
k_add = max(kq(j, wt(22, 2, 0.6), k_err16 + 1), k_err16 + 1)
k_ok16 = k_add + 1
L.note("核对数据", "出错")


def cl16(c, kk, T):
    sc = pop_scale(T - tb(16, k_cl16))
    if sc <= 0:
        return None
    x, y, w, h = CL16
    with at_pop(c, x, y, sc):
        clipboard(c, x, y, w, h)
        for i, ry in enumerate(ROW16[:3]):
            checkbox(c, x - 150, ry, 50, "ok")
            c.drawLine(x - 100, ry, x + 160 - (i % 2) * 50, ry, wb.marker("#9AA0AC", 7))
        t_a = tb(16, k_add)
        if T >= t_a - 0.3:
            g = ease_out(clamp01((T - t_a + 0.3) / 0.3))
            ry = ROW16[3]
            with K.at(c, x + (1 - g) * 300, ry, 0, 1):
                checkbox(c, -150, 0, 50, "ok" if T >= tb(16, k_ok16) else None, g)
                K.text(c, "核对数据", 20, 0, 52, "hand", RED, g)
    return None


b.custom(j, k_cl16, k_cl16 + 0.3, cl16, sfx="wood_high")


def err16(c, kk, T, cx=cx, cy=cy):
    t0 = tb(16, k_err16)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 340, cy - 100
    with K.at(c, x, y, 8, sc):
        box(c, 0, 0, 170, 210, "#FFFFFF", BLACK, 6, 10)
        c.drawPath(cross(0, 10, 50), wb.marker(RED, 12))
        K.text(c, "出错", 0, -150, 56, "hand", RED)
    return None


ev(j, k_err16, err16, "rim", 0.85)
b.hit(j, k_add, "shaker", 0.75, "新的一行滑进清单")
b.hit(j, k_ok16, "ding", 0.8, "新一行打勾")
WK16 = (cx + 340, cy + 430, 0.75)
ev(j, k_err16 + 1 if k_err16 + 1 < k_add else k_err16,
   L.figure(draw_li, j, k_err16 + 1 if k_err16 + 1 < k_add else k_err16, *WK16,
            mood=lambda T: "smile" if T >= tb(16, k_ok16) else "flat",
            lh=lambda T: (WK16[0] - 150, WK16[1] - 220) if T >= tb(16, k_add) - 0.3 else (WK16[0] - 60, WK16[1] - 120)))

# ================================================================ 屏 17：做法三——发现更快的做法，旧的一行划掉，旁边写新的
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
ev(j, 0, L.pop_text("③ 旧的划掉", cx, cy - 460, 88, BLUE, j, 0), "pop")
CL17 = (cx - 100, cy - 20, 500, 600)
ROW17 = [CL17[1] - 170 + i * 110 for i in range(4)]
OLD_ROW = 1
k_cl17 = 1
k_fast = max(kq(j, wt(23, 1, 0.5), 2), 2)
k_strike = max(kq(j, wt(23, 2, 0.5), k_fast + 1), k_fast + 1)
k_new17 = max(kq(j, wt(23, 3, 0.4), k_strike + 1), k_strike + 1)
L.note("更快", "慢")


def cl17(c, kk, T):
    sc = pop_scale(T - tb(17, k_cl17))
    if sc <= 0:
        return None
    x, y, w, h = CL17
    with at_pop(c, x, y, sc):
        clipboard(c, x, y, w, h)
        for i, ry in enumerate(ROW17):
            checkbox(c, x - 170, ry, 50, "ok" if i != OLD_ROW else None)
            x1 = x + 170 - (i % 2) * 40
            c.drawLine(x - 120, ry, x1, ry, wb.marker("#9AA0AC", 7))
            if i == OLD_ROW:
                K.text(c, "慢", x1 + 40, ry, 46, "hand", GRAY)
                ts = tb(17, k_strike)
                if T >= ts:
                    f = clamp01((T - ts) / 0.3)
                    c.drawLine(x - 140, ry + 4, x - 140 + (x1 + 80 - x + 140) * f, ry - 4, wb.marker(RED, 10))
                tn = tb(17, k_new17)
                if T >= tn:
                    g = pop_scale(T - tn)
                    with K.at(c, x + 20, ry + 52, -3, g):
                        K.text(c, "更快", 0, 0, 52, "hand", GREEN)
                        c.drawPath(check(110, 0, 22), wb.marker(GREEN, 8))
    return None


b.custom(j, k_cl17, k_cl17 + 0.3, cl17, sfx="wood_high")


def bolt17(c, kk, T, cx=cx, cy=cy):
    t0 = tb(17, k_fast)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 340, cy - 250
    with K.at(c, x, y, 0, sc):
        p = P((20, -110), (-50, 10), (0, 10), (-25, 110), (60, -20), (10, -20), close=True)
        c.drawPath(p, K.paint("#FFE08A"))
        c.drawPath(p, wb.marker(ORANGE, 7))
    return None


ev(j, k_fast, bolt17, "ding", 0.75)
b.hit(j, k_strike, "rim", 0.85, "旧的一行划掉")
b.hit(j, k_new17, "pop", 0.75, "写上更快的做法")
WK17 = (cx + 350, cy + 430, 0.75)
ev(j, k_fast, L.figure(draw_worker, j, k_fast, *WK17,
                       mood=lambda T: "smile" if T >= tb(17, k_new17) else "o",
                       lh=lambda T: (WK17[0] - 140, WK17[1] - 230) if T >= tb(17, k_strike) - 0.2
                       else (WK17[0] - 50, WK17[1] - 120)))

# ================================================================ 屏 18：清单在，脑子空出来（杂物飞出，灯泡亮）；请假也不怕，同事拿着清单接手
cx, cy = R[18]
j = L.scene(18, (cx, cy + 10, Z))
LI18 = (cx - 270, cy + 430, 0.95)
k_li18 = 0
k_fly = max(kq(j, wt(24, 1, 0.5), 1), 1)
k_bulb = max(kq(j, wt(24, 2, 0.4), k_fly + 1), k_fly + 1)
k_wk18 = max(kq(j, wt(25, 0, 0.5), k_bulb + 1), k_bulb + 1)
k_thumb = max(kq(j, wt(25, 1, 0.75), k_wk18 + 1), k_wk18 + 1)
JUNK = [(-60, -40, BLUE), (10, -60, ORANGE), (50, -20, GREEN), (-20, 0, RED), (30, 20, BLUE)]
L.note("接手")


def li18(c, sc, T, cx=cx, cy=cy):
    x, y, s = LI18
    hx, hy = head_of(x, y, s)
    t_f = tb(18, k_fly)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if T >= tb(18, k_bulb) else "flat")
        for n, (dx, dy, col) in enumerate(JUNK):
            g = ease_out(clamp01((T - t_f - n * 0.05) / 0.5))
            if g >= 1:
                continue
            a = math.radians(-150 + n * 30)
            px = hx + dx * 0.6 * s + math.cos(a) * 420 * g
            py = hy + dy * 0.6 * s + math.sin(a) * 420 * g
            with K.at(c, px, py, g * 180 * (1 if n % 2 else -1), 1 - 0.3 * g):
                box(c, 0, 0, 34, 30, "#FFFFFF", col, 4, 4, 1 - g)
        tb_ = tb(18, k_bulb)
        if T >= tb_:
            a = pop_scale(T - tb_)
            with K.at(c, hx, hy - 150, 0, a):
                c.drawCircle(0, 0, 70, K.paint("#FFE9A8", 0.7, blur=18))
                c.drawPath(C.bulb_path(0, 0, 46), wb.marker(ORANGE, 7))
    return None


ev(j, k_li18, pop_fn(j, k_li18, li18), "pop", 0.6)
b.hit(j, k_fly, "shaker", 0.8, "脑子里的杂物飞出去")
b.hit(j, k_bulb, "ding", 0.85, "灯泡亮")
WK18 = (cx + 300, cy + 430, 0.9)
CLIP18 = (cx + 120, cy + 30)


def wk18(c, sc, T, cx=cx, cy=cy):
    x, y, s = WK18
    hx, hy = head_of(x, y, s)
    thumb = T >= tb(18, k_thumb)
    with at_pop(c, x, y, sc):
        draw_worker(c, x, y, s, mood="smile", lh=(x - 120 * s, hy + 120 * s),
                    rh=(x + 110 * s, hy - 20 * s) if thumb else None)
        with K.at(c, x - 170 * s, hy + 90 * s, -8):
            clipboard(c, 0, 0, 150, 200)
            for i in range(3):
                checkbox(c, -40, -40 + i * 45, 26, "ok" if T >= tb(18, k_thumb) - 0.6 + i * 0.15 else None)
                c.drawLine(-18, -40 + i * 45, 50, -40 + i * 45, wb.marker("#9AA0AC", 4))
        if thumb:
            g = pop_scale(T - tb(18, k_thumb))
            with K.at(c, x + 110 * s, hy - 40 * s, 0, g):
                c.drawRoundRect(skia.Rect.MakeXYWH(-16, -10, 32, 34), 8, 8, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-16, -10, 32, 34), 8, 8, wb.marker(BLUE, 5))
                c.drawRoundRect(skia.Rect.MakeXYWH(-8, -42, 14, 36), 7, 7, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-8, -42, 14, 36), 7, 7, wb.marker(BLUE, 5))
    return None


ev(j, k_wk18, pop_fn(j, k_wk18, wk18), "wood_high")
b.hit(j, k_thumb, "clap", 0.8, "小王竖大拇指")
ev(j, k_thumb, L.pop_text("接手", cx + 260, cy - 330, 84, GREEN, j, k_thumb))

# ================================================================ 屏 19：评论区——哪件事每次从头想？几张小清单；下一讲预告
cx, cy = R[19]
j = L.scene(19, (cx, cy + 10, Z))
b.path(j, 0, 0.8, wb.bubble(cx, cy - 430, 1000, 220, -1), BLACK, 9, sfx="wood_high")
k_c1 = kq(j, wt(26, 0, 0.2), 1)
b.text(j, k_c1, k_c1 + 1.3, "哪件事每次都从头想？", cx, cy - 430, 64, RED, sfx="pop")
k_cards = max(kq(j, wt(27, 1, 0.2), k_c1 + 2), k_c1 + 2)
CARDS19 = [(cx - 330, -5), (cx, 3), (cx + 330, -4)]
L.note("报表", "出差", "交接")
NAMES19 = ["报表", "出差", "交接"]


def mini19(i):
    x, rot = CARDS19[i]

    def draw(c, sc, T, cx=cx, cy=cy):
        y = cy - 110
        with K.at(c, x, y, rot, sc):
            sticky(c, 0, 0, 260, 230)
            K.text(c, NAMES19[i], 0, -70, 52, "hand", BLACK)
            for n in range(3):
                checkbox(c, -80, -10 + n * 50, 30, "ok")
                c.drawLine(-55, -10 + n * 50, 90 - n * 20, -10 + n * 50, wb.marker("#9AA0AC", 5))
    return draw


for i in range(3):
    ev(j, k_cards + i, pop_fn(j, k_cards + i, mini19(i)), "pop", 0.6)
k_n = max(kq(j, wt(28, 0, 0.15), k_cards + 3), k_cards + 3)
b.path(j, k_n, k_n + 0.6, rect(cx, cy + 300, 1000, 330, 24), BLUE, 8, sfx="wood_high")
b.text(j, k_n + 0.5, k_n + 0.8, "下一讲", cx, cy + 180, 52, BLUE)
b.text(j, k_n + 0.8, k_n + 1.6, "事情一多", cx, cy + 265, 64, BLACK)
b.text(j, k_n + 1.6, k_n + 2.6, "为什么总有漏掉的？", cx, cy + 350, 64, BLACK)


def fly19(c, kk, T, cx=cx, cy=cy):
    """便利贴一张张被风吹走（下一讲：漏掉的事）。"""
    t0 = tb(19, k_n + 2.6)
    for i in range(3):
        g = clamp01((T - t0 - i * 0.25) / 1.2)
        if g <= 0:
            continue
        x = cx + 380 + 80 * g + i * 10
        y = cy + 260 - 220 * g + i * 50 + 20 * math.sin(g * 9 + i)
        with K.at(c, x, y, 30 * g * (1 if i % 2 else -1) + i * 6):
            sticky(c, 0, 0, 80, 70, alpha=1 - 0.6 * g)
    return None


b.custom(j, k_n + 2.6, k_n + 3.2, fly19)

# ================================================================ 收尾
L.finish(cover_shot=1, square_shot=5, notes=NOTES)
L.export(globals())
