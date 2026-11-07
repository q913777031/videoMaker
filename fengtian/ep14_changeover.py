"""《丰田模式》14 准备挪到前面：每次开工，为什么都要磨蹭半天？（白板手绘 + AI 旁白，竖屏 2:3）

比喻贯穿：赛车进站换轮胎从头用到尾。每屏地上都有一块黄白相间的“维修区格子”（进站的地方），讲丰田时把模具画成一只大轮胎，
说回职场时把小李的工位、门口、会议室都画成维修区：东西提前站进格子里，车一到就走。
- 开场（startlights）：起跑灯一盏盏亮红——找文件、倒水、连网，“还没开始”；
- 日常：小李在工位前找文件、倒水、连网，钟走了半圈；会议室里投屏黑着，“连不上”；
- 比喻（drop）：赛车滑进格子，四个轮胎同时换下，秒表“几秒”砸下；倒回去：车还没来，人、轮胎、扳手已经站进格子；
- 书中做法：冲压机上的模具画成大轮胎，换一种零件换一只；以前机器停着、工人坐着等，钟转好几圈；
  换模流程从中间剪开，右半“停机前就能做”的三块挪到停机线之前，左半压短；“几个小时”划掉改成“几分钟”，冲压机旁画上维修区格子；
- 为什么：小李开工前那半天拆成五块，四块盖上“提前做”，挪到前一天，开工那一下只剩一小块；
- 说回我们：周一对着电脑想“上周做到哪？”；出门才打印合同；门口找袜子、钥匙、耳机；下班只想走，沙漏五分钟，“三步”；
  三步做法（便签“明天第一件事”贴在屏幕上；提前五分钟插好投屏线；边开会边写纪要，散会就发出）；日程里多出一整块；
- 收尾：评论区的磨蹭清单；小李在维修区格子里站好位，车一来就出发；下一讲预告（三十页幻灯片叠成一摞）。
办公室里只有小李（common.draw_li）；赛车维修工与冲压车间工人戴安全帽（common.draw_worker），车间组长 scenekit.draw_leader2。
文案见 fengtian/PLAN.md「### 14」；时间轴、配乐、相机、人物见 fengtian/common.py，小工具见 fengtian/scenekit.py。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_li, draw_worker, pop_scale, wobble
from fengtian.scenekit import (GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL, NOTE_FILL, ORANGE_FILL, WOOD, WOOD_LINE,
                               Kit, at_pop, bag, box, bubble_text, clock_face, comment_box, dashed, dashed_rect, desk,
                               draw_leader2, head_of, heart, hourglass, laptop, paper, phone, qmark, sparkle, sweat, tick,
                               xmark)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)；句子分组与 PLAN 的 SCREENS_DRAFT 一致
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "比喻 · 赛车进站", 2),
    ([4], "比喻 · 赛车进站", 3),
    ([5, 6], "丰田模式 · 书中做法", 4),
    ([7], "丰田模式 · 书中做法", 5),
    ([8, 9], "丰田模式 · 书中做法", 6),
    ([10, 11], "丰田模式 · 书中做法", 7),
    ([12], "丰田模式 · 书中做法", 8),
    ([13, 14, 15, 16], "为什么拆开管用", 9),
    ([17, 18], "说回我们自己", 10),
    ([19], "说回我们自己", 11),
    ([20], "说回我们自己", 12),
    ([21, 22], "说回我们自己", 13),
    ([23], "做法一 · 示意", 14),
    ([24], "做法二 · 示意", 15),
    ([25], "做法三 · 示意", 16),
    ([26], "整块的时间", 17),
    ([27, 28, 29, 30], "评论区见", 18),
]

THEME = FT.get("14")          # 本讲样式：天蓝横线、开场 startlights、转场 pullpush
L = C.Lesson("14", SCREENS, drop_screen=2, board_size=(5000, 12000), theme=THEME)
b = L.b
tb, wt = L.tb, L.wt
KT = Kit(L)
kq, nx, ev, pop, seq = KT.kq, KT.nx, KT.ev, KT.pop, KT.seq

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(17)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：书中讲小批量、均衡生产时提到的快速换模——把换模拆成必须停机做的（内部作业）和停机前就能准备的（外部作业），"
    "后者全挪到停机之前，冲压机换模从几个小时缩到几分钟（书中篇幅待核）。",
    "赛车进站为比喻；小李、维修工、车间工人为虚构人物，时间数字为示意。",
]

TIRE, HUB, CAR, CAR_LINE = "#2B2B30", "#B8BEC8", "#F07A3A", "#B5401A"
LANE_Y, LANE_W = "#F2C94C", "#FFFFFF"


# ================================================================ 本讲道具

def pit_box(c, x, y, w, h, alpha=1.0, glow=0.0):
    """维修区格子：黄白相间的边框（地面俯视）。(x, y) 为中心。"""
    if glow > 0:
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 14, y - h / 2 - 14, w + 28, h + 28), 18, 18,
                        K.paint(YELLOW, 0.25 * glow, blur=16))
    seg = 60
    per = 2 * (w + h)
    n = int(per // seg)
    pts = []
    for i in range(n + 1):
        d = i * per / n
        if d <= w:
            pts.append((x - w / 2 + d, y - h / 2))
        elif d <= w + h:
            pts.append((x + w / 2, y - h / 2 + d - w))
        elif d <= 2 * w + h:
            pts.append((x + w / 2 - (d - w - h), y + h / 2))
        else:
            pts.append((x - w / 2, y + h / 2 - (d - 2 * w - h)))
    for i in range(n):
        C.line(c, pts[i], pts[i + 1], LANE_Y if i % 2 == 0 else "#FFFFFF", 16, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 9, y - h / 2 - 9, w + 18, h + 18), 6, 6, wb.marker(BLACK, 3, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 + 9, y - h / 2 + 9, w - 18, h - 18), 6, 6, wb.marker(BLACK, 3, alpha))


def tire(c, x, y, r, alpha=1.0, spin=0.0, color=TIRE):
    c.drawCircle(x, y, r, K.paint(color, alpha))
    c.drawCircle(x, y, r, wb.marker(BLACK, 6, alpha))
    c.drawCircle(x, y, r * 0.5, K.paint(HUB, alpha))
    c.drawCircle(x, y, r * 0.5, wb.marker(BLACK, 4, alpha))
    for i in range(5):
        a = spin + i * 2 * math.pi / 5
        C.line(c, (x, y), (x + math.cos(a) * r * 0.45, y + math.sin(a) * r * 0.45), BLACK, 3, alpha)


def car_top(c, x, y, s=1.0, alpha=1.0, off=(0, 0, 0, 0), new=(False,) * 4):
    """赛车（俯视，车头朝右）：(x, y) 为车身中心；off 为四个轮胎被拉离车身的距离，new 为是否画成新胎（带黄边）。"""
    L_, W_ = 520 * s, 150 * s
    wheels = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for i, (sx, sy) in enumerate(wheels):
        wx, wy = x + sx * 175 * s, y + sy * (W_ / 2 + 38 * s + off[i])
        rr = skia.Rect.MakeXYWH(wx - 50 * s, wy - 30 * s, 100 * s, 60 * s)
        c.drawRoundRect(rr, 14 * s, 14 * s, K.paint(TIRE, alpha))
        c.drawRoundRect(rr, 14 * s, 14 * s, wb.marker(YELLOW if new[i] else BLACK, 6, alpha))
    body = P((x - L_ / 2, y - W_ / 2), (x + L_ * 0.25, y - W_ * 0.42), (x + L_ / 2, y - W_ * 0.12),
             (x + L_ / 2, y + W_ * 0.12), (x + L_ * 0.25, y + W_ * 0.42), (x - L_ / 2, y + W_ / 2), close=True)
    c.drawPath(body, K.paint(CAR, alpha))
    c.drawPath(body, wb.marker(CAR_LINE, 7, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x + L_ / 2 - 20 * s, y - W_ * 0.95, 34 * s, W_ * 1.9), 6, 6, K.paint(BLACK, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - L_ / 2 - 26 * s, y - W_ * 0.85, 40 * s, W_ * 1.7), 6, 6, K.paint(BLACK, alpha))
    c.drawOval(skia.Rect.MakeXYWH(x - 60 * s, y - 34 * s, 120 * s, 68 * s), K.paint("#2B2B30", alpha))
    c.drawCircle(x - 4 * s, y, 24 * s, K.paint(YELLOW, alpha))
    C.line(c, (x - L_ * 0.35, y), (x - 110 * s, y), "#FFFFFF", 8, alpha)


def wrench(c, x, y, s=1.0, rot=0.0, alpha=1.0):
    with K.at(c, x, y, rot):
        c.drawRoundRect(skia.Rect.MakeXYWH(-14 * s, -90 * s, 28 * s, 150 * s), 10, 10, K.paint(HUB, alpha))
        c.drawRoundRect(skia.Rect.MakeXYWH(-14 * s, -90 * s, 28 * s, 150 * s), 10, 10, wb.marker(BLACK, 5, alpha))
        c.drawCircle(0, -100 * s, 32 * s, K.paint(HUB, alpha))
        c.drawCircle(0, -100 * s, 32 * s, wb.marker(BLACK, 5, alpha))
        c.drawRect(skia.Rect.MakeXYWH(-12 * s, -136 * s, 24 * s, 38 * s), K.paint("#FFFFFF", alpha))


def stopwatch(c, x, y, r, label=None, frac=0.0, alpha=1.0, color=RED):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - r * 0.22, y - r * 1.32, r * 0.44, r * 0.28), 6, 6, K.paint(BLACK, alpha))
    clock_face(c, x, y, r, frac, None, color, RED_FILL if color == RED else GREEN_FILL, alpha)
    if label:
        K.text(c, label, x, y + 6, r * 0.55, "hand", color, alpha)


def press(c, x, y, s=1.0, ram=0.0, alpha=1.0, gray=False):
    """冲压机（正视）：(x, y) 为底座中点；ram 0–1 为上模下压量。"""
    col = "#9AA3AE" if gray else "#6F8FB8"
    fill = "#E3E7EC" if gray else BLUE_FILL
    for dx in (-230, 230):
        box(c, x + dx * s, y - 330 * s, 60 * s, 600 * s, fill, col, 7, 8, alpha)
    box(c, x, y - 640 * s, 560 * s, 90 * s, fill, col, 8, 10, alpha)
    box(c, x, y - 20 * s, 600 * s, 60 * s, fill, col, 8, 10, alpha)
    ry = y - 520 * s + 160 * s * ram
    C.line(c, (x, y - 600 * s), (x, ry - 40 * s), col, 18, alpha)
    box(c, x, ry, 360 * s, 70 * s, "#FFFFFF", col, 7, 8, alpha)


def die_tire(c, x, y, r, alpha=1.0, color=ORANGE, label=None):
    """模具画成的大“轮胎”：粗环 + 中间的零件形状。"""
    c.drawCircle(x, y, r, K.paint(TIRE, alpha))
    c.drawCircle(x, y, r, wb.marker(BLACK, 7, alpha))
    c.drawCircle(x, y, r * 0.58, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, y, r * 0.58, wb.marker(color, 8, alpha))
    for i in range(8):
        a = i * math.pi / 4
        C.line(c, (x + math.cos(a) * r * 0.7, y + math.sin(a) * r * 0.7), (x + math.cos(a) * r * 0.92, y + math.sin(a) * r * 0.92),
               "#5A5F68", 6, alpha)
    if label:
        K.text(c, label, x, y + 4, r * 0.42, "hand", color, alpha)


def sitting_worker(c, x, y, s, alpha=1.0, mood="flat"):
    """戴安全帽的工人坐在小凳上（脚底 (x, y)）。"""
    box(c, x, y - 60 * s, 110 * s, 22 * s, WOOD, WOOD_LINE, 5, 4, alpha)
    for dx in (-40, 40):
        C.line(c, (x + dx * s, y - 50 * s), (x + dx * s, y), WOOD_LINE, 7, alpha)
    draw_worker(c, x, y - 60 * s, s * 0.85, lh=(x - 30 * s, y - 150 * s), rh=(x + 30 * s, y - 150 * s), mood=mood, alpha=alpha)


def block(c, x, y, w, h, fill, line, label=None, size=46, alpha=1.0, color=None):
    box(c, x, y, w, h, fill, line, 6, 12, alpha)
    if label:
        K.text(c, label, x, y + 2, size, "hand", color or line, alpha)


def strike(c, x0, x1, y, f, color=RED, width=10):
    if f > 0:
        C.line(c, (x0, y), (lerp(x0, x1, f), y), color, width)


def rewind_badge(c, x, y, alpha=1.0):
    box(c, x, y, 260, 100, "#FFFFFF", BLUE, 7, 22, alpha)
    for dx in (-88, -54):
        c.drawPath(P((x + dx + 24, y - 26), (x + dx + 24, y + 26), (x + dx - 14, y), close=True), K.paint(BLUE, alpha))
    K.text(c, "倒回去", x + 44, y + 3, 54, "hand", BLUE, alpha)


L.note("倒回去")


def clock_hand_frac(T, t0, turns, dur):
    return turns * ease_in_out(clamp01((T - t0) / dur)) if T >= t0 else 0.0


def calendar_page(c, x, y, w, h, title, alpha=1.0):
    box(c, x, y, w, h, "#FFFFFF", BLACK, 6, 10, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h * 0.24), 10, 10, K.paint(RED, alpha))
    K.text(c, title, x, y - h / 2 + h * 0.12 + 2, h * 0.14, "hand", "#FFFFFF", alpha)


# ================================================================ 屏 0：开场（起跑灯）
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：小李坐下找文件、倒水、连网，钟走半圈；会议室投屏连不上
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_li, k_f, k_w, k_n, k_half, k_room, k_x = seq(j, [None, (0, 2, 0.1), (0, 2, 0.45), (0, 2, 0.85), (0, 3, 0.5),
                                                   (1, 0, 0.3), (1, 1, 0.6)])
LX, LY = cx - 330, cy + 60
L.note("找文件", "倒水", "连网", "半小时", "连不上")


def desk1(c, T, cx=cx, cy=cy):
    desk(c, LX + 120, LY - 110, 460)
    laptop(c, LX + 200, LY - 122, 0.75)
    hy = LY - 290 * 0.8
    reach = T >= tb(1, k_f)
    draw_li(c, LX - 40, LY, 0.8, "sad" if T >= tb(1, k_half) else "flat",
            rh=(LX + 60, hy + 90 + 25 * math.sin((T - tb(1, k_f)) * 8)) if reach else None)


pop(j, k_li, LX, LY, desk1, "wood_low", 0.7)
ICONS1 = [(k_f, "找文件", LX - 60, cy - 470), (k_w, "倒水", LX + 140, cy - 470), (k_n, "连网", LX + 340, cy - 470)]


def icon1(n, x, y, cx=cx, cy=cy):
    def draw(c, T):
        if n == 0:
            box(c, x, y, 150, 100, "#F2C14E", BLACK, 6, 8)
            qmark(c, x + 60, y - 70, 70, T - tb(1, ICONS1[0][0]) - 0.2, RED)
        elif n == 1:
            c.drawPath(P((x - 45, y - 55), (x + 45, y - 55), (x + 35, y + 50), (x - 35, y + 50), close=True), K.paint("#CFE3F8"))
            c.drawPath(P((x - 45, y - 55), (x + 45, y - 55), (x + 35, y + 50), (x - 35, y + 50), close=True), wb.marker(BLACK, 6))
            for m in range(3):
                ph = ((T * 1.5) + m * 0.33) % 1
                c.drawCircle(x - 20 + m * 20, y - 70 - ph * 50, 6, K.paint(BLUE, 1 - ph))
        else:
            for r in (24, 50, 76):
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(x - r, y + 40 - r, 2 * r, 2 * r), 225, 90)
                c.drawPath(arc, wb.marker(BLACK, 8))
            spin = (T * 3) % 1
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(x + 50, y - 60, 50, 50), spin * 360, 270)
            c.drawPath(arc, wb.marker(GRAY, 6))
        K.text(c, ICONS1[n][1], x, y + 95, 48, "hand", BLACK)
    return draw


for n, (k_, s_, x, y) in enumerate(ICONS1):
    pop(j, k_, x, y, icon1(n, x, y), ("pop", "pop", "wood_high")[n], 0.65)


def clock1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_f))
    if sc <= 0:
        return None
    x, y = cx + 380, cy - 330
    f = 0.5 * ease_in_out(clamp01((T - tb(1, k_f)) / max(0.3, tb(1, k_half) - tb(1, k_f))))
    with at_pop(c, x, y, sc):
        clock_face(c, x, y, 120, f, f, RED, RED_FILL)
        if T >= tb(1, k_half):
            g = pop_scale(T - tb(1, k_half))
            with K.at(c, x, y + 175, 0, g):
                K.text(c, "半小时", 0, 0, 56, "hand", RED)
    return None


ev(j, k_f, clock1)
b.hit(j, k_half, "wood_low", 0.7, "钟走了半圈")
RX, RY = cx + 160, cy + 330


def room1(c, T, cx=cx, cy=cy):
    box(c, RX, RY - 80, 420, 220, "#2B2B30", BLACK, 8, 10)
    C.line(c, (RX, RY - 190), (RX, RY - 230), BLACK, 8)
    for n, dx in enumerate((-160, -50, 60, 170)):
        hx, hy = RX + dx, RY + 130
        c.drawCircle(hx, hy, 34, K.paint("#FFFFFF"))
        c.drawCircle(hx, hy, 34, wb.marker(BLACK, 6))
        c.drawArc(skia.Rect.MakeXYWH(hx - 50, hy + 30, 100, 80), 180, 180, False, wb.marker(BLACK, 6))
    blink = (math.sin((T - tb(1, k_room)) * 7) > 0.3)
    if blink:
        K.text(c, "无信号", RX, RY - 80, 40, "sans_medium", "#C9CED6")


L.note("无信号")
pop(j, k_room, RX, RY, room1, "wood_low", 0.7)
ev(j, k_x, L.stamp("连不上", RX + 30, RY - 260, 70, j, k_x, rot=-7), "kick", 0.85)
b.shots[j].shake = [(k_x, 8.0)]

# ================================================================ 屏 2：赛车滑进维修区，四个轮胎同时换下，drop 时秒表“几秒”砸下
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
PBX, PBY = cx - 20, cy + 40
k_box = 0
k_in = min(max(kq(j, wt(2, 0, 0.6), 1), 1), KD - 3)
k_crew = min(max(kq(j, wt(3, 1, 0.1), k_in + 1), k_in + 1), KD - 1)
CREW = [(PBX - 190, PBY - 210), (PBX + 190, PBY - 210), (PBX - 190, PBY + 330), (PBX + 190, PBY + 330)]
L.note("几秒")


def box2(c, T, cx=cx, cy=cy):
    pit_box(c, PBX, PBY, 760, 380, glow=1.0 if T >= tb(2, KD) else 0.0)
    C.line(c, (cx - 560, PBY - 250), (cx + 560, PBY - 250), GRAY, 5)
    dashed(c, (cx - 560, PBY - 300), (cx + 560, PBY - 300), GRAY, 4)


pop(j, k_box, PBX, PBY, box2, "wood_low", 0.7)


def car2(c, kk, T, cx=cx, cy=cy):
    t0, t1 = tb(2, k_in), tb(2, k_in + 1)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / max(0.3, t1 - t0)))
    x = lerp(cx - 1100, PBX, f)
    td = tb(2, KD)
    off = [0.0] * 4
    new = [False] * 4
    if T >= td - 0.35:
        u = clamp01((T - (td - 0.35)) / 0.35)
        off = [70 * math.sin(math.pi * u)] * 4
        if T >= td:
            new = [True] * 4
            off = [0.0] * 4
    leave = 0.0
    car_top(c, x + leave, PBY, 0.95, off=off, new=new)
    if f < 1:
        for i in range(3):
            C.line(c, (x - 330 - i * 40, PBY - 60 + i * 60), (x - 480 - i * 40, PBY - 60 + i * 60), GRAY, 6, 1 - f)
    if T >= td:
        dt = T - td
        for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
            ox = PBX + sx * 170 + sx * 260 * ease_out(clamp01(dt / 0.5))
            oy = PBY + sy * 160 + sy * 120 * ease_out(clamp01(dt / 0.5))
            tire(c, ox, oy, 46, 1 - clamp01((dt - 0.6) / 0.4), dt * 8)
    return None


ev(j, k_in, car2, "shaker", 0.75)


def crew2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_crew))
    if sc <= 0:
        return None
    td = tb(2, KD)
    for n, (x, y) in enumerate(CREW):
        lean = 26 * math.sin(math.pi * clamp01((T - (td - 0.35)) / 0.5)) if T >= td - 0.35 else 0.0
        top = n < 2
        hy = y - 290 * 0.62
        with at_pop(c, x, y, sc):
            draw_worker(c, x, y, 0.62, lh=(x - 30, hy + (150 if top else 60) + lean), rh=(x + 30, hy + (150 if top else 60) + lean),
                        mood="smile")
    return None


ev(j, k_crew, crew2, "pop", 0.7)
if k_crew + 1 < KD:
    b.hit(j, k_crew + 1, "wood_high", 0.6, "维修工弯腰扶胎")


def watch2(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(2, KD))
    if sc <= 0:
        return None
    x, y = cx + 360, cy - 400
    with K.at(c, x, y, 6, sc):
        stopwatch(c, 0, 0, 130, "几秒", 0.06)
    return None


ev(j, KD, watch2, "kick", 0.95)

# ================================================================ 屏 3：倒回去——车还没来，人、轮胎、扳手已经站进格子
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_rw, k_ppl, k_tire, k_wr, k_ok = seq(j, [None, (4, 2, 0.2), (4, 2, 0.5), (4, 2, 0.85), (4, 3, 0.5)])
PB3 = (cx, cy + 80)
L.note("站好了")


def rw3(c, T, cx=cx, cy=cy):
    rewind_badge(c, cx - 380, cy - 480)
    for i in range(3):
        ph = ((T - tb(3, k_rw)) * 1.2 + i * 0.33) % 1
        C.line(c, (cx + 380 - ph * 260, cy - 480), (cx + 300 - ph * 260, cy - 480), GRAY, 6, 1 - ph)


pop(j, k_rw, cx - 380, cy - 480, rw3, "rim", 0.8)


def box3(c, T, cx=cx, cy=cy):
    pit_box(c, PB3[0], PB3[1], 760, 380, glow=1.0 if T >= tb(3, k_ok) else 0.0)
    dashed_rect(c, PB3[0], PB3[1], 560, 190, GRAY, 5)
    K.text(c, "车还没来", PB3[0], PB3[1] + 4, 50, "hand", GRAY)


L.note("车还没来")
pop(j, k_rw, PB3[0], PB3[1], box3)
SPOTS3 = [(PB3[0] - 260, PB3[1] - 200), (PB3[0] + 260, PB3[1] - 200), (PB3[0] - 260, PB3[1] + 370), (PB3[0] + 260, PB3[1] + 370)]


def ppl3(c, kk, T, cx=cx, cy=cy):
    for n, (x, y) in enumerate(SPOTS3):
        sc = pop_scale(T - tb(3, k_ppl) - n * 0.07)
        if sc > 0:
            with at_pop(c, x, y, sc):
                draw_worker(c, x, y, 0.6, mood="smile")
    return None


ev(j, k_ppl, ppl3, "pop", 0.7)


def tires3(c, kk, T, cx=cx, cy=cy):
    for n, (x, y) in enumerate(SPOTS3):
        sc = pop_scale(T - tb(3, k_tire) - n * 0.07)
        if sc > 0:
            with at_pop(c, x + 110, y - 40, sc):
                tire(c, x + 110, y - 40, 44, color=TIRE)
                c.drawCircle(x + 110, y - 40, 44, wb.marker(YELLOW, 6))
    return None


ev(j, k_tire, tires3, "wood_high", 0.7)


def wr3(c, kk, T, cx=cx, cy=cy):
    for n, (x, y) in enumerate(SPOTS3):
        sc = pop_scale(T - tb(3, k_wr) - n * 0.07)
        if sc > 0:
            with at_pop(c, x - 100, y - 30, sc):
                wrench(c, x - 100, y - 30, 0.55, -20)
    return None


ev(j, k_wr, wr3, "wood_low", 0.7)
ev(j, k_ok, L.slam_text("站好了", cx + 280, cy - 480, 96, RED, j, k_ok, rot=-5), "kick", 0.85)

# ================================================================ 屏 4：冲压机上的模具画成大轮胎；换一种零件，换一只模具
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_pr, k_lab, k_tag, k_partA, k_partB, k_swap = seq(j, [None, (5, 0, 0.6), (5, 1, 0.8), (6, 0, 0.5), (6, 1, 0.6), (6, 2, 0.5)])
PX4, PY4 = cx - 150, cy + 400
L.note("冲压机", "换模具", "车门", "车顶")


def press4(c, T, cx=cx, cy=cy):
    ram = 0.25 + 0.15 * math.sin((T - tb(4, k_pr)) * 3)
    press(c, PX4, PY4, 0.95, ram)
    K.text(c, "冲压机", PX4, PY4 + 70, 52, "hand", BLUE)


pop(j, k_pr, PX4, PY4, press4, "wood_low", 0.75)


def die4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_lab))
    if sc <= 0:
        return None
    swap = T >= tb(4, k_swap)
    u = ease_in_out(clamp01((T - tb(4, k_swap)) / 0.5)) if swap else 0.0
    x0, y0 = PX4, PY4 - 220
    with at_pop(c, x0, y0, sc):
        die_tire(c, x0 + 700 * u, y0, 120, 1 - u, ORANGE)
        if swap:
            die_tire(c, lerp(x0 + 520, x0, u), y0, 120, u, GREEN)
    return None


ev(j, k_lab, die4, "wood_high", 0.75)
ev(j, k_tag, L.slam_text("换模具", cx + 320, cy - 450, 100, RED, j, k_tag), "kick", 0.85)


def part(c, x, y, kind, color, cx=cx, cy=cy):
    if kind == 0:
        c.drawPath(P((x - 70, y - 60), (x + 70, y - 60), (x + 70, y + 60), (x - 60, y + 60), (x - 70, y), close=True), K.paint("#FFFFFF"))
        c.drawPath(P((x - 70, y - 60), (x + 70, y - 60), (x + 70, y + 60), (x - 60, y + 60), (x - 70, y), close=True), wb.marker(color, 7))
        box(c, x + 10, y - 25, 90, 40, BLUE_FILL, color, 4, 6)
    else:
        c.drawPath(P((x - 90, y + 30), (x - 50, y - 40), (x + 50, y - 40), (x + 90, y + 30), close=True), K.paint("#FFFFFF"))
        c.drawPath(P((x - 90, y + 30), (x - 50, y - 40), (x + 50, y - 40), (x + 90, y + 30), close=True), wb.marker(color, 7))


pop(j, k_partA, cx + 360, cy - 180, lambda c, T, cx=cx, cy=cy: (part(c, cx + 360, cy - 180, 0, ORANGE),
                                                  K.text(c, "车门", cx + 360, cy - 70, 48, "hand", ORANGE)), "pop", 0.7)
pop(j, k_partB, cx + 360, cy + 100, lambda c, T, cx=cx, cy=cy: (part(c, cx + 360, cy + 100, 1, GREEN),
                                                  K.text(c, "车顶", cx + 360, cy + 190, 48, "hand", GREEN)), "pop", 0.7)
b.hit(j, k_swap, "wood_low", 0.8, "模具（轮胎）换下")

# ================================================================ 屏 5：以前——机器停着（灰），工人坐着等，钟转好几圈
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_m5, k_hr, k_stop, k_wait = seq(j, [None, (7, 1, 0.3), (7, 2, 0.15), (7, 2, 0.7)])
L.note("以前", "停", "好几个小时")
pop(j, k_m5, cx - 230, cy + 420, lambda c, T, cx=cx, cy=cy: (press(c, cx - 230, cy + 420, 0.8, 0.0, gray=True),
                                               K.text(c, "以前", cx - 430, cy - 470, 64, "hand", GRAY)), "wood_low", 0.7)


def clock5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_hr))
    if sc <= 0:
        return None
    x, y = cx + 330, cy - 320
    h = clock_hand_frac(T, tb(5, k_hr), 4.0, 3.5)
    with at_pop(c, x, y, sc):
        clock_face(c, x, y, 140, h % 1.0, (h * 12) % 1.0, RED, RED_FILL)
        K.text(c, "好几个小时", x, y + 200, 54, "hand", RED)
    return None


ev(j, k_hr, clock5, "tom", 0.75)
ev(j, k_stop, L.stamp("停", cx - 230, cy - 250, 110, j, k_stop, rot=-10), "rim", 0.85)


def wait5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_wait))
    if sc <= 0:
        return None
    for n, x in enumerate((cx + 150, cx + 400)):
        y = cy + 430
        with at_pop(c, x, y, sc):
            sitting_worker(c, x, y, 0.8, mood="sad")
            if n == 1:
                hx, hy = x, y - 60 - 290 * 0.68
                for m in range(3):
                    ph = ((T - tb(5, k_wait)) * 0.8 + m / 3) % 1
                    K.text(c, "z", hx + 60 + ph * 60, hy - 60 - ph * 90, 40 + 20 * ph, "hand", GRAY, 1 - ph)
    return None


ev(j, k_wait, wait5, "wood_high", 0.7)

# ================================================================ 屏 6：换模流程一整条，从中间剪开：左“停机才能做”，右“停机前就能做”
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_bar, k_cut, k_left, k_right, k_hi = seq(j, [None, (8, 1, 0.5), (9, 0, 0.5), (9, 1, 0.4), (9, 1, 0.9)])
BY6 = cy - 120
SEG6 = [("推模具", ORANGE_FILL, ORANGE), ("拆旧模", RED_FILL, RED), ("摆工具", GREEN_FILL, GREEN), ("装新模", RED_FILL, RED),
        ("备螺丝", GREEN_FILL, GREEN)]
L.note("换模流程", *[s[0] for s in SEG6], "停机才能做", "停机前就能做")


def bar6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_bar)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.8))
    split = ease_in_out(clamp01((T - tb(6, k_cut)) / 0.5)) if T >= tb(6, k_cut) else 0.0
    K.text(c, "换模流程", cx, BY6 - 170, 60, "hand", BLACK, clamp01(f * 2))
    order = [1, 3, 0, 2, 4] if split > 0 else [0, 1, 2, 3, 4]
    for n in range(5):
        if f * 5 < n + 0.2:
            continue
        lab, fill, line = SEG6[n]
        x_line = cx - 420 + n * 210
        inner = line == RED
        if split > 0:
            slot = order.index(n)
            x_split = (cx - 450 + slot * 200) if inner else (cx + 60 + (slot - 2) * 200)
            x = lerp(x_line, x_split, split)
            y = lerp(BY6, BY6 + (0 if inner else 0), split)
        else:
            x, y = x_line, BY6
        hl = T >= tb(6, k_hi) and not inner
        with K.at(c, x, y, wobble(T - tb(6, k_hi), 5, 18, 5) if hl else 0, 1.0 + (0.06 if hl else 0)):
            block(c, 0, 0, 190, 120, fill if split > 0 else "#FFFFFF", line if split > 0 else BLACK, lab, 44)
    return None


ev(j, k_bar, bar6, "wood_high", 0.75)


def cut6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_cut)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.4))
    x = cx - 40
    dashed(c, (x, BY6 - 120), (x, lerp(BY6 - 120, BY6 + 520, f)), BLACK, 7)
    sx, sy = x, lerp(BY6 - 120, BY6 + 520, f)
    for d in (-1, 1):
        with K.at(c, sx, sy, 90 + d * 20 * math.cos((T - t0) * 20)):
            c.drawOval(skia.Rect.MakeXYWH(-60, -18 + d * 26, 46, 32), wb.marker(BLACK, 6))
            C.line(c, (-14, d * 10), (40, -d * 4), BLACK, 6)
    return None


ev(j, k_cut, cut6, "rim", 0.8)
pop(j, k_left, cx - 300, BY6 + 210, lambda c, T, cx=cx, cy=cy: (box(c, cx - 300, BY6 + 210, 430, 110, RED_FILL, RED, 7, 20),
                                                  K.text(c, "停机才能做", cx - 300, BY6 + 212, 56, "hand", RED)), "wood_low", 0.75)
pop(j, k_right, cx + 260, BY6 + 210, lambda c, T, cx=cx, cy=cy: (box(c, cx + 260, BY6 + 210, 470, 110, GREEN_FILL, GREEN, 7, 20),
                                                   K.text(c, "停机前就能做", cx + 260, BY6 + 212, 56, "hand", GREEN)), "wood_high", 0.75)


def lights6(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k_hi)
    if dt < 0:
        return None
    sparkle(c, cx + 260, BY6 + 360, dt, GREEN)
    g = pop_scale(dt)
    with K.at(c, cx + 260, BY6 + 400, 0, g):
        K.text(c, "准备好", 0, 0, 74, "hand", GREEN)
    return None


L.note("准备好")
ev(j, k_hi, lights6, "ding", 0.75)

# ================================================================ 屏 7：右半三块挪到停机线之前；左半两块压短
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_tl, k_mv, k_m2, k_m3, k_sh, k_fast = seq(j, [None, (10, 1, 0.3), (10, 2, 0.4), (10, 3, 0.4), (11, 1, 0.1), (11, 1, 0.7)])
TY = cy - 60
STOP_X = cx + 40
PREP = [("推模具", ORANGE), ("摆工具", GREEN), ("备螺丝", GREEN)]
L.note("停机", "时间", "缩短")


def tl7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_tl))
    if sc <= 0:
        return None
    with at_pop(c, cx, TY, sc):
        C.line(c, (cx - 540, TY + 120), (cx + 520, TY + 120), BLACK, 9)
        C.line(c, (cx + 520, TY + 120), (cx + 490, TY + 100), BLACK, 9)
        C.line(c, (cx + 520, TY + 120), (cx + 490, TY + 140), BLACK, 9)
        K.text(c, "时间", cx + 460, TY + 175, 44, "hand", GRAY)
        C.line(c, (STOP_X, TY - 330), (STOP_X, TY + 160), RED, 10)
        box(c, STOP_X, TY - 380, 160, 80, RED, RED, 6, 16)
        K.text(c, "停机", STOP_X, TY - 378, 50, "hand", "#FFFFFF")
    # 停机后的两块（必须停机做的），第 k_sh 拍起压短
    sh = ease_in_out(clamp01((T - tb(7, k_sh)) / 0.5)) if T >= tb(7, k_sh) else 0.0
    w = lerp(200, 120, sh)
    for n, lab in enumerate(("拆旧模", "装新模")):
        x = STOP_X + 20 + w / 2 + n * (w + 10)
        with at_pop(c, cx, TY, sc):
            block(c, x, TY + 40, w, 110, RED_FILL, RED, lab, lerp(42, 32, sh))
    # 准备的三块：起初在停机线之后，逐块挪到前面
    ks = (k_mv, k_m2, k_m3)
    for n, (lab, col) in enumerate(PREP):
        x0 = STOP_X + 460 + n * 0 - 10
        y0 = TY + 40 - 140 * (n + 1) + 80
        x1 = STOP_X - 130 - (2 - n) * 200
        u = ease_in_out(clamp01((T - tb(7, ks[n])) / 0.45)) if T >= tb(7, ks[n]) else 0.0
        x = lerp(x0, x1, u)
        y = lerp(y0, TY + 40, u) - 90 * math.sin(math.pi * u)
        with at_pop(c, cx, TY, sc):
            block(c, x, y, 180, 110, GREEN_FILL if u >= 1 else "#FFFFFF", col, lab, 42)
    return None


ev(j, k_tl, tl7, "wood_low", 0.7)
for n, k_ in enumerate((k_mv, k_m2, k_m3)):
    b.hit(j, k_, ("wood_high", "wood_high", "bongo_high")[n], 0.75, f"第 {n + 1} 块挪到停机前")
b.hit(j, k_sh, "tom", 0.8, "停机后的两块压短")


def fast7(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(7, k_fast)
    if dt < 0:
        return None
    g = C.slam_scale(dt)
    x = STOP_X + 140
    with K.at(c, x, TY + 300, -4, g):
        K.text(c, "缩短", 0, 0, 92, "hand", RED)
    C.line(c, (STOP_X + 20, TY + 200), (STOP_X + 270, TY + 200), RED, 8)
    for d in (-1, 1):
        C.line(c, (STOP_X + 20, TY + 200), (STOP_X + 44, TY + 200 + d * 16), RED, 8)
        C.line(c, (STOP_X + 270, TY + 200), (STOP_X + 246, TY + 200 + d * 16), RED, 8)
    return None


ev(j, k_fast, fast7, "kick", 0.85)

# ================================================================ 屏 8：“几个小时”划掉改成“几分钟”；冲压机旁画上维修区格子
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_cl, k_x8, k_min, k_pit = seq(j, [None, (12, 1, 0.5), (12, 2, 0.4), (12, 2, 0.9)])
L.note("几个小时", "几分钟")


def clock8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_cl))
    if sc <= 0:
        return None
    x, y = cx - 260, cy - 300
    fast = T >= tb(8, k_min)
    f = 0.75 * (1 - ease_in_out(clamp01((T - tb(8, k_min)) / 0.6))) + 0.06 if fast else 0.75
    with at_pop(c, x, y, sc):
        clock_face(c, x, y, 170, f, None, GREEN if fast else RED, GREEN_FILL if fast else RED_FILL)
        K.text(c, "几个小时", x, y + 240, 64, "hand", GRAY if T >= tb(8, k_x8) else RED)
        if T >= tb(8, k_x8):
            strike(c, x - 150, x + 150, y + 242, clamp01((T - tb(8, k_x8)) / 0.25))
    return None


ev(j, k_cl, clock8, "wood_low", 0.7)
b.hit(j, k_x8, "rim", 0.8, "划掉几个小时")
ev(j, k_min, L.slam_text("几分钟", cx + 270, cy - 330, 120, GREEN, j, k_min, rot=-4), "kick", 0.85)


def pit8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_pit))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 330, sc):
        pit_box(c, cx, cy + 330, 900, 380, glow=1.0)
        press(c, cx - 150, cy + 480, 0.5, 0.1)
        for n, x in enumerate((cx + 160, cx + 320)):
            draw_worker(c, x, cy + 470, 0.5, mood="smile")
        die_tire(c, cx + 240, cy + 250, 60, 1.0, GREEN)
    return None


ev(j, k_pit, pit8, "ding", 0.75)

# ================================================================ 屏 9：小李开工前那半天拆成五块，四块盖“提前做”，挪到前一天，开工那一下变短
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_q, k_split, k_st, k_wait9, k_mv9, k_go = seq(j, [None, (14, 0, 0.6), (14, 2, 0.4), (15, 1, 0.4), (16, 0, 0.5), (16, 1, 0.6)])
BY9 = cy - 40
JOBS9 = [("找文件", True), ("倒水", True), ("连网", True), ("打印", True), ("动手做", False)]
L.note("为什么？", "开工前", "前一天", "提前做", "快了", *[s for s, _ in JOBS9])
ev(j, k_q, L.slam_text("为什么？", cx, cy - 520, 90, RED, j, k_q), "rim", 0.8)


def bar9(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k_split)
    if T < t0:
        return None
    u = ease_out(clamp01((T - t0) / 0.5))
    mv = ease_in_out(clamp01((T - tb(9, k_mv9)) / 0.6)) if T >= tb(9, k_mv9) else 0.0
    K.text(c, "开工前", cx + 150, BY9 - 140, 56, "hand", BLACK)
    K.text(c, "前一天", cx - 380, BY9 + 290, 56, "hand", BLUE, mv)
    if mv > 0:
        dashed_rect(c, cx - 290, BY9 + 400, 520, 140, BLUE, 5, mv)
    for n, (lab, pre) in enumerate(JOBS9):
        x_line = cx - 380 + n * 205 if u >= 1 else lerp(cx + 150, cx - 380 + n * 205, u)
        x, y = x_line, BY9
        if pre and mv > 0:
            xt = cx - 480 + n * 130
            x, y = lerp(x_line, xt, mv), lerp(BY9, BY9 + 400, mv) - 120 * math.sin(math.pi * mv)
        w = 190 if (pre or mv == 0) else lerp(190, 200, mv)
        sc = lerp(1.0, 0.68, mv) if pre else 1.0
        with K.at(c, x, y, 0, sc):
            block(c, 0, 0, w, 120, ORANGE_FILL if pre else GREEN_FILL, ORANGE if pre else GREEN, lab, 44)
        if pre and T >= tb(9, k_st):
            g = pop_scale(T - tb(9, k_st) - n * 0.06)
            with K.at(c, x, y - 90 * sc, -8, g * sc):
                box(c, 0, 0, 150, 52, "#FFFFFF", RED, 5, 10)
                K.text(c, "提前做", 0, 2, 36, "hand", RED)
    return None


ev(j, k_split, bar9, "wood_high", 0.75)
b.hit(j, k_st, "rim", 0.8, "四块盖上“提前做”")


def wait9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k_wait9))
    if sc <= 0:
        return None
    x, y = cx + 360, cy + 520
    hy = y - 290 * 0.7
    gone = T >= tb(9, k_go)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.7, "smile" if gone else "sad",
                rh=(x + 80, hy - 40) if gone else None)
        if not gone:
            hourglass(c, x - 170, y - 120, 150, clamp01((T - tb(9, k_wait9)) / 3))
    return None


L.note("干等")
ev(j, k_wait9, wait9, "wood_low", 0.7)
b.hit(j, k_mv9, "shaker", 0.8, "四块挪到前一天")
ev(j, k_go, L.slam_text("快了", cx + 320, cy + 160, 110, GREEN, j, k_go, rot=-5), "kick", 0.85)
b.shots[j].shake = [(k_go, 8.0)]

# ================================================================ 屏 10：周一早上小李对着电脑发呆，头顶“上周做到哪？”；二十分钟
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_pit10, k_li10, k_cal, k_th, k_20 = seq(j, [None, (17, 1, 0.3), (18, 0, 0.3), (18, 2, 0.2), (18, 1, 0.6)])
k_th, k_20 = sorted((k_th, k_20))
L.note("进站慢", "周一", "上周做到哪？", "20分钟")
pop(j, k_pit10, cx, cy + 300, lambda c, T, cx=cx, cy=cy: (pit_box(c, cx, cy + 300, 1000, 420),
                                           K.text(c, "进站慢", cx + 360, cy + 560, 50, "hand", GRAY)), "wood_low", 0.7)


def li10(c, T, cx=cx, cy=cy):
    desk(c, cx - 60, cy + 280, 560)
    laptop(c, cx + 20, cy + 268, 0.9, "#E4EEF8")
    hy = cy + 470 - 290 * 0.85
    draw_li(c, cx - 300, cy + 470, 0.85, "flat", rh=(cx - 220, hy + 60), lh=(cx - 380, hy + 160))
    # 鼠标指针在屏幕上一动不动地闪
    if math.sin(T * 6) > 0:
        C.line(c, (cx + 20, cy + 140), (cx + 20, cy + 180), BLACK, 5)


pop(j, k_li10, cx - 60, cy + 470, li10, "wood_high", 0.7)
pop(j, k_cal, cx + 360, cy - 420, lambda c, T, cx=cx, cy=cy: calendar_page(c, cx + 360, cy - 420, 220, 220, "周一"), "pop", 0.7)


def think10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_th))
    if sc <= 0:
        return None
    x, y = cx - 120, cy - 180
    with at_pop(c, x, y, sc):
        for n, (dx, dy, r) in enumerate(((-160, 150, 16), (-130, 105, 24))):
            c.drawCircle(x + dx, y + dy, r, K.paint("#FFFFFF"))
            c.drawCircle(x + dx, y + dy, r, wb.marker(BLACK, 5))
        c.drawOval(skia.Rect.MakeXYWH(x - 280, y - 90, 560, 180), K.paint("#FFFFFF"))
        c.drawOval(skia.Rect.MakeXYWH(x - 280, y - 90, 560, 180), wb.marker(BLACK, 7))
        K.text(c, "上周做到哪？", x, y + 2, 64, "hand", BLACK)
    return None


ev(j, k_th, think10, "pop", 0.75)


def clk10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_20))
    if sc <= 0:
        return None
    x, y = cx + 360, cy - 130
    f = clamp01((T - tb(10, k_20)) / 1.2) / 3
    with at_pop(c, x, y, sc):
        clock_face(c, x, y, 95, f, None, RED, RED_FILL)
        K.text(c, "20分钟", x, y + 140, 50, "hand", RED)
    return None


ev(j, k_20, clk10, "wood_low", 0.75)

# ================================================================ 屏 11：要出门了才想起合同没打印——小李冲出门又跑回来，打印机慢慢吐纸
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_door, k_run, k_back, k_pr11, k_late = seq(j, [None, (19, 0, 0.4), (19, 0, 0.9), (19, 1, 0.3), (19, 1, 0.85)])
DX11 = cx + 380
L.note("合同", "客户", "还没打印")


def door11(c, T, cx=cx, cy=cy):
    box(c, DX11, cy + 110, 240, 480, WOOD, WOOD_LINE, 8, 8)
    c.drawCircle(DX11 - 80, cy + 120, 14, K.paint(BLACK))
    box(c, DX11, cy - 230, 200, 70, "#FFFFFF", BLUE, 5, 10)
    K.text(c, "客户", DX11, cy - 228, 44, "hand", BLUE)


pop(j, k_door, DX11, cy + 110, door11, "wood_low", 0.7)


def li11(c, kk, T, cx=cx, cy=cy):
    t0 = tb(11, k_run)
    if T < t0:
        return None
    t1, t2 = tb(11, k_back), tb(11, k_back) + 0.6
    if T < t1:
        x, dy, mv = C.walk(T, t0, t1 - t0, cx - 300, DX11 - 160, 16, 4)
    else:
        x, dy, mv = C.walk(T, t1, 0.6, DX11 - 160, cx - 160, 16, 4)
    hy = cy + 470 - 290 * 0.85
    sc = pop_scale(T - t0)
    with at_pop(c, x, cy + 470, sc):
        draw_li(c, x, cy + 470 + dy, 0.85, "sad" if T >= t1 else "flat", bag=True)
        if T >= t1:
            sweat(c, x + 60, hy - 20 + 8 * math.sin(T * 6))
            K.text(c, "！", x + 10, hy - 110, 90, "black", RED)
    return None


ev(j, k_run, li11, "shaker", 0.7)
b.hit(j, k_back, "rim", 0.8, "想起合同，跑回来")


def printer11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_pr11))
    if sc <= 0:
        return None
    x, y = cx - 250, cy - 230
    f = clamp01((T - tb(11, k_pr11)) / 2.0)
    with at_pop(c, x, y, sc):
        out_h = 200 * f
        paper(c, x, y - 60 - out_h / 2 + 100, 220, max(10, out_h), rows=int(3 * f) + 1, title="合同" if f > 0.6 else None)
        box(c, x, y + 60, 360, 150, "#E3E7EC", BLACK, 7, 16)
        box(c, x, y + 10, 260, 22, "#3B3F48", BLACK, 4, 6)
        c.drawCircle(x + 140, y + 90, 12, K.paint(GREEN if math.sin(T * 8) > 0 else "#9AA3AE"))
    return None


ev(j, k_pr11, printer11, "wood_high", 0.7)
ev(j, k_late, L.stamp("还没打印", cx + 100, cy - 480, 70, j, k_late, rot=-6), "kick", 0.85)

# ================================================================ 屏 12：门口一只袜子、一串钥匙、一副耳机散在三处；“差点迟到”
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_li12, k_sock, k_key, k_ear, k_late12 = seq(j, [None, (20, 1, 0.2), (20, 1, 0.5), (20, 1, 0.85), (20, 2, 0.5)])
L.note("袜子", "钥匙", "耳机", "差点迟到")


def li12(c, T, cx=cx, cy=cy):
    hy = cy + 480 - 290 * 0.85
    look = math.sin((T - tb(12, k_li12)) * 5)
    draw_li(c, cx, cy + 480, 0.85, "sad", rh=(cx + 90, hy + 40 + 30 * look), lh=(cx - 90, hy + 40 - 30 * look))
    qmark(c, cx + 80, hy - 120, 80, T - tb(12, k_li12) - 0.2, GRAY)


pop(j, k_li12, cx, cy + 480, li12, "wood_low", 0.7)


def sock(c, T, x=cx - 380, y=cy + 330, cx=cx, cy=cy):
    c.drawPath(P((x - 30, y - 90), (x + 30, y - 90), (x + 30, y + 10), (x + 80, y + 30), (x + 70, y + 70), (x - 30, y + 60),
                 close=True), K.paint("#F4A7A0"))
    c.drawPath(P((x - 30, y - 90), (x + 30, y - 90), (x + 30, y + 10), (x + 80, y + 30), (x + 70, y + 70), (x - 30, y + 60),
                 close=True), wb.marker(BLACK, 6))
    K.text(c, "袜子", x + 20, y + 130, 48, "hand", BLACK)


def keys(c, T, x=cx + 360, y=cy - 380, cx=cx, cy=cy):
    sw = 14 * math.sin((T - tb(12, k_key)) * 5)
    with K.at(c, x, y, sw):
        c.drawCircle(0, 0, 34, wb.marker(GRAY, 7))
        for n, a in enumerate((60, 100)):
            ex, ey = math.cos(math.radians(a)) * 110, math.sin(math.radians(a)) * 110
            C.line(c, (math.cos(math.radians(a)) * 30, math.sin(math.radians(a)) * 30), (ex, ey), "#C9A227", 12)
            c.drawCircle(ex, ey, 22, K.paint("#E8C14E"))
            c.drawCircle(ex, ey, 22, wb.marker(BLACK, 5))
    K.text(c, "钥匙", x + 100, y - 40, 48, "hand", BLACK)


def ears(c, T, x=cx - 330, y=cy - 330, cx=cx, cy=cy):
    for dx in (-50, 50):
        c.drawCircle(x + dx, y, 34, K.paint("#FFFFFF"))
        c.drawCircle(x + dx, y, 34, wb.marker(BLACK, 6))
        C.line(c, (x + dx, y + 34), (x + dx * 0.6, y + 120), BLACK, 5)
    K.text(c, "耳机", x, y - 80, 48, "hand", BLACK)


pop(j, k_sock, cx - 380, cy + 330, sock, "pop", 0.7)
pop(j, k_key, cx + 360, cy - 380, keys, "wood_high", 0.7)
pop(j, k_ear, cx - 330, cy - 330, ears, "pop", 0.7)


def late12(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(12, k_late12))
    if sc <= 0:
        return None
    x, y = cx + 300, cy - 30
    with K.at(c, x, y, -5, sc):
        clock_face(c, 0, -10, 110, 0.0, 0.95 + 0.01 * math.sin(T * 20), RED, RED_FILL)
        K.text(c, "差点迟到", 0, 160, 64, "hand", RED)
    return None


ev(j, k_late12, late12, "kick", 0.85)
b.shots[j].shake = [(k_late12, 7.0)]

# ================================================================ 屏 13：下班时小李只想走，包已经背上；大字“三步”；五分钟沙漏
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_li13, k_go13, k_hg, k_3 = seq(j, [None, (21, 1, 0.5), (22, 0, 0.5), (22, 1, 0.6)])
L.note("下班", "5分钟", "三步")


def li13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_li13))
    if sc <= 0:
        return None
    t0 = tb(13, k_go13)
    x = cx - 250 + (60 * ease_out(clamp01((T - t0) / 0.4)) if T >= t0 else 0)
    hy = cy + 470 - 290 * 0.9
    with at_pop(c, x, cy + 470, sc):
        draw_li(c, x, cy + 470, 0.9, "flat", bag=True, rh=(x + 110, hy - 40) if T >= t0 else None)
        if T >= t0:
            for i in range(3):
                C.line(c, (x - 120 - i * 30, hy + 60 + i * 50), (x - 200 - i * 30, hy + 60 + i * 50), GRAY, 6,
                       1 - clamp01((T - t0) / 1.0))
        box(c, x - 40, cy - 330, 220, 90, "#FFFFFF", BLACK, 6, 14)
        K.text(c, "下班", x - 40, cy - 328, 56, "hand", BLACK)
        C.line(c, (x - 40, cy - 285), (x - 40, cy - 230), BLACK, 6)
    return None


ev(j, k_li13, li13, "wood_low", 0.7)
b.hit(j, k_go13, "shaker", 0.7, "迈步想走")


def hg13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_hg))
    if sc <= 0:
        return None
    x, y = cx + 300, cy + 260
    with at_pop(c, x, y, sc):
        hourglass(c, x, y, 300, clamp01((T - tb(13, k_hg)) / 4.0))
        K.text(c, "5分钟", x, y + 220, 60, "hand", BLUE)
    return None


ev(j, k_hg, hg13, "pop", 0.7)
ev(j, k_3, L.slam_text("三步", cx + 260, cy - 260, 170, RED, j, k_3, rot=-4), "kick", 0.9)
b.shots[j].shake = [(k_3, 9.0)]

# ================================================================ 屏 14：做法一——下班前在便签上写“明天第一件事”，贴在屏幕上，文件窗口开着
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_mon, k_note, k_stick, k_open = seq(j, [None, (23, 1, 0.2), (23, 1, 0.9), (23, 2, 0.5)])
L.note("第一", "明天第一件事", "别关")
pop(j, k_mon, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: K.text(c, "第一", cx - 380, cy - 470, 90, "hand", RED), "rim", 0.8)


def mon14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_mon))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 50, sc):
        box(c, cx, cy - 50, 760, 480, "#2B2B30", BLACK, 9, 18)
        box(c, cx, cy - 50, 720, 440, "#FFFFFF", GRAY, 4, 10)
        C.line(c, (cx, cy + 190), (cx, cy + 260), BLACK, 14)
        C.line(c, (cx - 140, cy + 265), (cx + 140, cy + 265), BLACK, 14)
        if T >= tb(14, k_open):
            g = pop_scale(T - tb(14, k_open))
            with K.at(c, cx - 120, cy - 30, 0, g):
                box(c, 0, 0, 380, 260, BLUE_FILL, BLUE, 6, 8)
                c.drawRect(skia.Rect.MakeXYWH(-190, -130, 380, 42), K.paint(BLUE))
                for r in range(4):
                    C.line(c, (-150, -50 + r * 44), (150 - (r % 2) * 60, -50 + r * 44), GRAY, 6)
    return None


ev(j, k_mon, mon14, "wood_low", 0.7)


def note14(c, kk, T, cx=cx, cy=cy):
    t0 = tb(14, k_note)
    if T < t0:
        return None
    t1 = tb(14, k_stick)
    u = ease_in_out(clamp01((T - t1) / 0.35)) if T >= t1 else 0.0
    x, y = lerp(cx + 200, cx + 230, u), lerp(cy + 420, cy - 200, u)
    with K.at(c, x, y, lerp(-8, 6, u), pop_scale(T - t0)):
        box(c, 0, 0, 300, 220, "#FFE58A", BLACK, 6, 4)
        K.text(c, "明天", 0, -50, 54, "hand", BLACK)
        K.text(c, "第一件事", 0, 30, 54, "hand", RED)
    hx = cx - 330
    draw_li(c, hx, cy + 560, 0.75, "smile", rh=(x - 150, y + 40) if u < 1 else (hx + 90, cy + 300))
    return None


ev(j, k_note, note14, "pop", 0.7)
b.hit(j, k_stick, "wood_high", 0.8, "便签贴上屏幕")
ev(j, k_open + 1 if k_open + 1 < KT.nbeats(j) - 3 else k_open,
   L.stamp("别关", cx + 360, cy + 360, 74, j, k_open + 1 if k_open + 1 < KT.nbeats(j) - 3 else k_open, GREEN, rot=8),
   "rim", 0.8)
b.hit(j, k_open, "pop", 0.7, "文件窗口开着")

# ================================================================ 屏 15：做法二——提前五分钟进会议室，把投屏线插好，屏幕亮
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k_rm, k_clk15, k_plug, k_on = seq(j, [None, (24, 0, 0.6), (24, 2, 0.2), (24, 2, 0.8)])
L.note("第二", "提前5分钟", "连好了")


def room15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_rm))
    if sc <= 0:
        return None
    on = T >= tb(15, k_on)
    with at_pop(c, cx, cy, sc):
        K.text(c, "第二", cx - 380, cy - 470, 90, "hand", RED)
        box(c, cx + 80, cy - 220, 640, 360, "#FFFFFF" if on else "#2B2B30", BLACK, 9, 10)
        if on:
            K.text(c, "连好了", cx + 80, cy - 220, 90, "hand", GREEN)
            sparkle(c, cx + 80, cy - 220, T - tb(15, k_on), GREEN, 10, 200, 330)
        desk(c, cx + 40, cy + 260, 700)
        laptop(c, cx + 220, cy + 248, 0.7, BLUE_FILL)
    return None


ev(j, k_rm, room15, "wood_low", 0.7)


def clk15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_clk15))
    if sc <= 0:
        return None
    with at_pop(c, cx - 370, cy - 190, sc):
        clock_face(c, cx - 370, cy - 190, 80, 1 / 12, None, GREEN, GREEN_FILL)
        K.text(c, "提前5分钟", cx - 370, cy - 60, 46, "hand", GREEN)
    return None


ev(j, k_clk15, clk15, "pop", 0.7)


def plug15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_plug))
    if sc <= 0:
        return None
    u = ease_in_out(clamp01((T - tb(15, k_plug)) / max(0.3, tb(15, k_on) - tb(15, k_plug))))
    px = lerp(cx - 60, cx + 80, u)
    hy = cy + 520 - 290 * 0.85
    draw_li(c, cx - 170, cy + 520, 0.85, "smile", rh=(px - 30, cy + 260))
    c.drawPath(P((cx + 220, cy + 240), (cx + 170, cy + 300), (px + 10, cy + 300), (px, cy + 250)), wb.marker(BLACK, 7))
    box(c, px, cy + 250, 50, 34, GRAY_FILL, BLACK, 4, 4)
    return None


ev(j, k_plug, plug15, "wood_high", 0.7)
b.hit(j, k_on, "ding", 0.8, "屏幕亮")

# ================================================================ 屏 16：做法三——会议中边听边记，散会时消息已发出
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
k_mt, k_wr16, k_end, k_sent = seq(j, [None, (25, 1, 0.3), (25, 2, 0.2), (25, 2, 0.8)])
L.note("第三", "纪要", "已发送")


def meet16(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(16, k_mt))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 300, sc):
        K.text(c, "第三", cx - 380, cy - 470, 90, "hand", RED)
        c.drawOval(skia.Rect.MakeXYWH(cx - 420, cy + 180, 840, 170), K.paint(WOOD))
        c.drawOval(skia.Rect.MakeXYWH(cx - 420, cy + 180, 840, 170), wb.marker(WOOD_LINE, 8))
        for n, x in enumerate((cx - 250, cx + 250)):
            c.drawCircle(x, cy + 100, 50, K.paint("#FFFFFF"))
            c.drawCircle(x, cy + 100, 50, wb.marker(BLACK, 7))
            c.drawArc(skia.Rect.MakeXYWH(x - 70, cy + 140, 140, 120), 180, 180, False, wb.marker(BLACK, 7))
        talk = (math.sin((T - tb(16, k_mt)) * 9) > 0) and T < tb(16, k_end)
        if talk:
            for i in range(3):
                C.line(c, (cx - 190 + i * 10, cy + 20 - i * 20), (cx - 150 + i * 20, cy + 0 - i * 26), BLACK, 5)
        hy = cy + 520 - 290 * 0.8
        draw_li(c, cx, cy + 520, 0.8, "smile", rh=(cx + 90, cy + 250 + 8 * math.sin(T * 12)))
    return None


ev(j, k_mt, meet16, "wood_low", 0.7)


def note16(c, kk, T, cx=cx, cy=cy):
    t0 = tb(16, k_wr16)
    if T < t0:
        return None
    x, y = cx + 20, cy - 220
    with K.at(c, x, y, -3, pop_scale(T - t0)):
        box(c, 0, 0, 420, 300, "#FFFFFF", BLACK, 6, 8)
        K.text(c, "纪要", 0, -100, 56, "hand", BLUE)
        n = int(clamp01((T - t0) / 2.0) * 4)
        for r in range(n + 1):
            C.line(c, (-160, -30 + r * 44), (160 - (r % 2) * 50, -30 + r * 44), GRAY, 6)
    return None


ev(j, k_wr16, note16, "pop", 0.7)
b.hit(j, k_end, "wood_high", 0.7, "散会")


def sent16(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(16, k_sent)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.7))
    x, y = lerp(cx + 200, cx + 400, f), lerp(cy - 220, cy - 470, f)
    with K.at(c, x, y, -20):
        plane = P((-60, 20), (70, -30), (-20, 40), close=True)
        c.drawPath(plane, K.paint("#FFFFFF"))
        c.drawPath(plane, wb.marker(BLUE, 6))
        C.line(c, (70, -30), (-20, 40), BLUE, 5)
    g = pop_scale(dt - 0.2)
    with K.at(c, cx + 330, cy - 330, 0, g):
        box(c, 0, 0, 240, 80, GREEN_FILL, GREEN, 5, 30)
        K.text(c, "已发送", 0, 2, 50, "hand", GREEN)
    return None


ev(j, k_sent, sent16, "ding", 0.8)

# ================================================================ 屏 17：日程表上多出一大块完整的空格，小李坐进去专心做事
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
k_cal17, k_blk, k_sit, k_word = seq(j, [None, (26, 0, 0.6), (26, 1, 0.3), (26, 1, 0.85)])
L.note("整块的时间", "9点", "10点", "11点", "12点")
ROWS17 = ["9点", "10点", "11点", "12点"]


def cal17(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(17, k_cal17))
    if sc <= 0:
        return None
    x0, y0 = cx - 480, cy - 450
    with at_pop(c, cx, cy, sc):
        box(c, cx, cy - 20, 1000, 900, "#FFFFFF", BLACK, 7, 14)
        for n, s_ in enumerate(ROWS17):
            y = y0 + 80 + n * 210
            K.text(c, s_, x0 + 70, y, 44, "hand", GRAY)
            C.line(c, (x0 + 130, y - 20), (cx + 480, y - 20), GRAY_FILL, 4)
        for n, (yy, hh) in enumerate(((y0 + 80, 70), (y0 + 760, 70))):
            box(c, cx + 60, yy + 10, 700, hh, ORANGE_FILL, ORANGE, 5, 10)
    return None


ev(j, k_cal17, cal17, "wood_low", 0.7)


def blk17(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(17, k_blk)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.5))
    top, full = cy - 300, 560
    h = full * f
    box(c, cx + 60, top + h / 2, 700, max(10, h), GREEN_FILL, GREEN, 7, 16)
    if T >= tb(17, k_sit):
        g = pop_scale(T - tb(17, k_sit))
        with at_pop(c, cx + 60, cy + 220, g):
            desk(c, cx + 140, cy + 130, 300)
            laptop(c, cx + 170, cy + 118, 0.55)
            draw_li(c, cx - 80, cy + 220, 0.65, "smile", rh=(cx + 40, cy + 70))
            sparkle(c, cx - 80, cy + 220 - 290 * 0.65 - 60, T - tb(17, k_sit) - 0.2, YELLOW, 6, 30, 90)
    return None


ev(j, k_blk, blk17, "shaker", 0.75)
b.hit(j, k_sit, "pop", 0.7, "小李坐进去")
ev(j, k_word, L.pop_text("整块的时间", cx + 60, cy - 220, 78, GREEN, j, k_word), "ding", 0.8)

# ================================================================ 屏 18：评论区的磨蹭清单；维修区里小李提前站好位，车一来就出发；下一讲预告
cx, cy = R[18]
j = L.scene(18, (cx, cy + 10, Z))
k_cb, k_g1, k_pit18, k_car, k_heart, k_nx = seq(j, [None, (28, 0, 0.3), (29, 0, 0.3), (29, 1, 0.7), (29, 2, 0.7), (30, 0, 0.2)])
GRIPES = [("找鼠标", cx - 340, cy - 500), ("等电脑开机", cx + 200, cy - 500), ("先刷会手机", cx - 90, cy - 400)]
L.note("哪一步最磨蹭？", *[g[0] for g in GRIPES], "下一讲", "汇报做了三十页", "为什么没人看？")


def cb18(c, T, cx=cx, cy=cy):
    comment_box(c, cx, cy - 400, 1040, 330)
    K.text(c, "哪一步最磨蹭？", cx - 140, cy - 520, 52, "hand", RED)


pop(j, k_cb, cx, cy - 400, cb18, "wood_high", 0.7)
for n, (s_, x, y) in enumerate(GRIPES):
    ev(j, k_g1, L.pop_text(s_, x + 40, y + 80, 52, BLACK, j, k_g1 + 0.15 * n), "pop" if n == 0 else None, 0.6)


def pit18(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(18, k_pit18))
    if sc <= 0:
        return None
    x, y = cx - 120, cy + 70
    with at_pop(c, x, y, sc):
        pit_box(c, x, y, 640, 260, glow=1.0)
        t0 = tb(18, k_car)
        if T >= t0:
            u = clamp01((T - t0) / 1.4)
            cxr = lerp(x - 900, x + 900, ease_in_out(u)) if u < 1 else x + 900
            if u < 0.4:
                cxr = lerp(x - 900, x, ease_out(u / 0.4))
            elif u < 0.6:
                cxr = x
            else:
                cxr = lerp(x, x + 900, ease_in_out((u - 0.6) / 0.4))
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(cx - 560, y - 200, cx + 560, y + 200))
            car_top(c, cxr, y, 0.6, new=(u >= 0.5,) * 4)
            c.restore()
        draw_li(c, x + 360, y + 160, 0.6, "smile", rh=(x + 440, y - 60))
        tire(c, x + 260, y + 120, 34)
    return None


ev(j, k_pit18, pit18, "wood_low", 0.7)
b.hit(j, k_car, "shaker", 0.8, "车进站又出发")


def heart18(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(18, k_heart))
    if sc <= 0:
        return None
    with K.at(c, cx + 400, cy - 60, 0, sc * (1 + 0.05 * math.sin((T - tb(18, k_heart)) * 6))):
        heart(c, 0, 0, 60)
    return None


ev(j, k_heart, heart18, "ding", 0.75)


def next18(c, kk, T, cx=cx, cy=cy):
    t0 = tb(18, k_nx)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 420, sc):
        box(c, cx, cy + 420, 1000, 300, "#FFFFFF", BLUE, 8, 24)
        K.text(c, "下一讲", cx + 120, cy + 320, 48, "hand", BLUE)
        K.text(c, "汇报做了三十页", cx + 120, cy + 410, 62, "hand", BLACK)
        K.text(c, "为什么没人看？", cx + 120, cy + 500, 62, "hand", BLACK)
        for n in range(8):
            yy = cy + 520 - n * 22 - 12 * pop_scale(T - t0 - 0.1 * n)
            box(c, cx - 360 + (n % 2) * 8, yy, 180, 110, "#FFFFFF", BLACK, 4, 6)
    return None


ev(j, k_nx, next18, "wood_high", 0.75)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=3, notes=NOTES)
L.export(globals())
