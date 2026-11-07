"""《丰田模式》18 新工具：新工具一个接一个，活怎么没少？（白板手绘 + AI 旁白，竖屏 2:3）

曲线故事：一张“新工具热度”坐标图贯穿全片。第 2–4 屏在同一张图上画出新工具的一生（上线冲到最高 → 第二周往下掉 →
一个月贴地）；讲完丰田的做法，第 9、10 屏镜头拉远回到这张图，在图下面讲为什么会掉，再在同一张图上画出另一条慢慢往上的绿线；
说回职场的三屏，每屏右上角一张小曲线卡，标出这件工具走到了曲线哪一段。
- 开场（apps）：手机上应用图标逐拍蹦出三个，第四拍全部变灰挂上红点，“又一个”；
- 日常：新系统登录页闪着光；日历翻到“两周后”，屏幕上又是表格；桌上一摞“使用手册”；
- 曲线：坐标轴画出来，drop 拍曲线冲到顶，顶上一群小人围着试；第二周流程和新工具的接口对不上、曲线往下掉；
  一个月后曲线贴地，只剩一个小人在角落里用；
- 书中做法：“可靠”“试过”“帮得上人和流程”三张卡逐个亮；车间一角虚线框里试新机器，试稳了框扩到整条线；
  闪亮的新机器接口形状不对，被推回去；工人先用手把乱箭头理直，机器再接上；对照：乱箭头加马达转得更乱；
- 为什么会掉：回到曲线，小李抱着一把大锤到处找钉子；丰田先在流程图上圈出卡住的那步，工具正好嵌进去，图上画出慢慢往上的绿线；
- 说回我们：协作软件页面空空、群里文件一条接一条；一排人工智能工具图标各配一个“一下午”的钟，小李自己敲日报；
  客厅智能音箱只亮闹钟；小李看着一列新工具、身后有人跑过，“三步”；三步做法；工具替你干活 vs 围着工具转；
- 收尾：评论区鸡肋工具和好用工具；小李把一个工具装进口袋轻快往前走；下一讲预告（大闹钟追着小李）。
小李 common.draw_li；同事小王 scenekit.draw_wang（不戴安全帽）；车间员工 common.draw_worker（戴安全帽）。
文案见 fengtian/PLAN.md「### 18」；时间轴、配乐、相机、人物见 fengtian/common.py，小工具见 fengtian/scenekit.py。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_li, draw_worker, pop_scale, wobble
from fengtian.scenekit import (GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL, NOTE_FILL, ORANGE_FILL, WOOD_LINE,
                               Kit, at_pop, box, bubble_text, clock_face, comment_box, dashed, dashed_rect, desk,
                               draw_wang, heart, laptop, paper, phone, sparkle, sweat, tick, xmark)
from whiteboard import engine as wb
from whiteboard.engine import P

# 每屏：(旁白句序号, 页眉标签, 白板区块)；句子分组与 PLAN 的 SCREENS_DRAFT 一致；区块 2 是贯穿全片的热度曲线图
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "热度曲线 · 一生", 2),
    ([4], "热度曲线 · 一生", 2),
    ([5], "热度曲线 · 一生", 2),
    ([6, 7], "丰田模式 · 书中做法", 5),
    ([8], "丰田模式 · 书中做法", 6),
    ([9], "丰田模式 · 书中做法", 7),
    ([10, 11], "丰田模式 · 书中做法", 8),
    ([12, 13], "为什么会掉下来", 2),
    ([14, 15], "为什么会掉下来", 2),
    ([16, 17], "说回我们自己", 11),
    ([18], "说回我们自己", 12),
    ([19], "说回我们自己", 13),
    ([20, 21], "说回我们自己", 14),
    ([22], "做法一 · 示意", 15),
    ([23], "做法二 · 示意", 16),
    ([24], "做法三 · 示意", 17),
    ([25], "工具替你干活", 18),
    ([26, 27, 28, 29], "评论区见", 19),
]

THEME = FT.get("18")          # 本讲样式：深紫方格、开场 apps、转场 tilt
L = C.Lesson("18", SCREENS, drop_screen=2, board_size=(5000, 12800), theme=THEME)
b = L.b
tb, wt = L.tb, L.wt
KT = Kit(L)
kq, nx, ev, pop, seq = KT.kq, KT.nx, KT.ev, KT.pop, KT.seq

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1800 * (i // 3))
                                 for i in range(18)]
Z = 0.72
CX, CY = R[2]                     # 曲线图
R[3] = R[4] = R[9] = R[10] = R[2]
FAR = (CX, CY + 300, 0.56)        # 回到曲线时的拉远视角（图在上半，下面讲原因）

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 8——只用可靠的、充分试过的、能帮到人和流程的技术；先小范围试；跟干活方式合不上的不用；"
    "“先用手把流程做顺，再上机器”的说法待核。",
    "热度曲线为示意，不是数据；工具图标、协作软件、智能音箱为示意；小李、小王为虚构人物。",
]


# ================================================================ 本讲道具

def label(c, s, x, y, size, color=BLACK, font="hand", alpha=1.0):
    K.text(c, s, x, y, size, font, color, alpha)


def monitor(c, x, y, w=300, h=200, screen="#FFFFFF", alpha=1.0):
    box(c, x, y, w, h, "#2B2B30", BLACK, 7, 10, alpha)
    box(c, x, y, w - 24, h - 24, screen, GRAY, 3, 6, alpha)
    C.line(c, (x, y + h / 2), (x, y + h / 2 + 40), BLACK, 10, alpha)
    C.line(c, (x - 60, y + h / 2 + 42), (x + 60, y + h / 2 + 42), BLACK, 10, alpha)


def gear(c, x, y, r, rot, color=GRAY, alpha=1.0):
    with K.at(c, x, y, rot):
        for i in range(8):
            a = i * math.pi / 4
            C.line(c, (math.cos(a) * r * 0.8, math.sin(a) * r * 0.8), (math.cos(a) * r * 1.15, math.sin(a) * r * 1.15),
                   color, r * 0.32, alpha)
        c.drawCircle(0, 0, r * 0.85, K.paint("#FFFFFF", alpha))
        c.drawCircle(0, 0, r * 0.85, wb.marker(color, 7, alpha))
        c.drawCircle(0, 0, r * 0.3, wb.marker(color, 6, alpha))


APP_COLS = ("#5B8DEF", "#F28C5B", "#7BC67E", "#B98AE0", "#F2C14E")


def app_icon(c, x, y, r, n, gray=False, alpha=1.0):
    col = "#9AA0A8" if gray else APP_COLS[n % 5]
    c.drawRoundRect(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), r * 0.45, r * 0.45, K.paint(col, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), r * 0.45, r * 0.45, wb.marker(BLACK, 5, alpha))
    m = n % 3
    if m == 0:
        c.drawPath(P((x, y - r * 0.55), (x + r * 0.17, y - r * 0.15), (x + r * 0.55, y), (x + r * 0.17, y + r * 0.15),
                     (x, y + r * 0.55), (x - r * 0.17, y + r * 0.15), (x - r * 0.55, y), (x - r * 0.17, y - r * 0.15),
                     close=True), K.paint("#FFFFFF", alpha))
    elif m == 1:
        c.drawCircle(x - r * 0.22, y - r * 0.05, r * 0.26, wb.marker("#FFFFFF", 6, alpha))
        c.drawCircle(x + r * 0.24, y + r * 0.12, r * 0.26, wb.marker("#FFFFFF", 6, alpha))
    else:
        c.drawRect(skia.Rect.MakeXYWH(x - r * 0.5, y - r * 0.42, r, r * 0.8), wb.marker("#FFFFFF", 6, alpha))
        C.line(c, (x - r * 0.5, y - r * 0.12), (x + r * 0.5, y - r * 0.12), "#FFFFFF", 5, alpha)


def sheet_grid(c, x, y, w, h, alpha=1.0):
    """表格：(x, y) 为中心。"""
    box(c, x, y, w, h, "#FFFFFF", GREEN, 5, 4, alpha)
    for i in range(1, 4):
        C.line(c, (x - w / 2 + i * w / 4, y - h / 2), (x - w / 2 + i * w / 4, y + h / 2), GREEN, 3, alpha)
    for i in range(1, 5):
        C.line(c, (x - w / 2, y - h / 2 + i * h / 5), (x + w / 2, y - h / 2 + i * h / 5), GREEN, 3, alpha)


def calendar_page(c, x, y, w, h, title, alpha=1.0):
    box(c, x, y, w, h, "#FFFFFF", BLACK, 6, 10, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h * 0.26), 10, 10, K.paint(RED, alpha))
    K.text(c, title, x, y + h * 0.12, h * 0.24, "hand", BLACK, alpha)


def machine(c, x, y, s=1.0, plug="square", shiny=False, alpha=1.0, T=0.0):
    """新机器：(x, y) 为底边中点；左侧接口 plug = square / round。"""
    box(c, x, y - 110 * s, 260 * s, 200 * s, "#C9D6EA" if shiny else "#C9CED6", BLACK, 7, 18, alpha)
    box(c, x + 30 * s, y - 140 * s, 120 * s, 70 * s, "#FFFFFF", BLUE, 5, 8, alpha)
    for i in range(3):
        c.drawCircle(x - 80 * s + i * 34 * s, y - 50 * s, 10 * s, K.paint((RED, YELLOW, GREEN)[i], alpha))
    px = x - 130 * s
    if plug == "square":
        c.drawRect(skia.Rect.MakeXYWH(px - 50 * s, y - 135 * s, 50 * s, 50 * s), K.paint(ORANGE, alpha))
        c.drawRect(skia.Rect.MakeXYWH(px - 50 * s, y - 135 * s, 50 * s, 50 * s), wb.marker(BLACK, 5, alpha))
    else:
        c.drawCircle(px - 26 * s, y - 110 * s, 26 * s, K.paint(ORANGE, alpha))
        c.drawCircle(px - 26 * s, y - 110 * s, 26 * s, wb.marker(BLACK, 5, alpha))
    if shiny:
        for i in range(4):
            a = T * 2 + i * 1.6
            sx, sy = x + 150 * s * math.cos(a), y - 120 * s + 120 * s * math.sin(a)
            C.line(c, (sx - 14, sy), (sx + 14, sy), YELLOW, 5, alpha)
            C.line(c, (sx, sy - 14), (sx, sy + 14), YELLOW, 5, alpha)


def tangle(x, y, w, h, seed=3):
    """一团乱箭头的路径。"""
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    for i in range(1, 9):
        u = i / 8
        p.lineTo(x - w / 2 + w * u + 60 * math.sin(i * 2.7 + seed), y + h / 2 * math.sin(i * 1.9 + seed * 0.7))
    return p


def hammer(c, x, y, rot, s=1.0, alpha=1.0):
    with K.at(c, x, y, rot):
        c.drawRoundRect(skia.Rect.MakeXYWH(-10 * s, -20 * s, 20 * s, 190 * s), 8, 8, K.paint("#D7B98E", alpha))
        c.drawRoundRect(skia.Rect.MakeXYWH(-10 * s, -20 * s, 20 * s, 190 * s), 8, 8, wb.marker(WOOD_LINE, 5, alpha))
        box(c, 0, -40 * s, 130 * s, 56 * s, "#9AA0A8", BLACK, 6, 8, alpha)


def mini_curve(c, x, y, stage, T=0.0, alpha=1.0, color=RED):
    """右上角的小曲线卡：stage 0–2（冲高 / 往下掉 / 贴地），小圆点标出当前位置。"""
    box(c, x, y, 260, 170, "#FFFFFF", GRAY, 5, 14, alpha)
    pts = [(x - 110, y + 60), (x - 60, y - 55), (x + 10, y + 30), (x + 110, y + 60)]
    p = skia.Path()
    p.moveTo(*pts[0])
    p.cubicTo(x - 90, y + 20, x - 80, y - 55, pts[1][0], pts[1][1])
    p.cubicTo(x - 30, y - 55, x - 10, y + 50, x + 30, y + 58)
    p.lineTo(*pts[3])
    c.drawPath(p, wb.marker(color, 6, alpha))
    dot = [(x - 60, y - 55), (x - 5, y + 20), (x + 90, y + 58)][stage]
    r = 14 + 4 * math.sin(T * 6)
    c.drawCircle(dot[0], dot[1], r, K.paint(color, alpha))


# ---------------------------------------------------------------- 热度曲线（第 2–4、9、10 屏共用）

OX, OY = CX - 500, CY + 300       # 原点
PEAK = (CX - 180, CY - 200)
WK2 = (CX + 60, CY + 150)
MON = (CX + 300, CY + 285)
END = (CX + 520, CY + 290)


def curve_up():
    p = skia.Path()
    p.moveTo(OX, OY - 5)
    p.cubicTo(OX + 120, OY - 20, PEAK[0] - 90, PEAK[1] + 10, PEAK[0], PEAK[1])
    return p


def curve_down():
    p = skia.Path()
    p.moveTo(*PEAK)
    p.cubicTo(PEAK[0] + 90, PEAK[1] - 10, WK2[0] - 120, WK2[1] - 160, WK2[0], WK2[1])
    return p


def curve_flat():
    p = skia.Path()
    p.moveTo(*WK2)
    p.cubicTo(WK2[0] + 90, WK2[1] + 110, MON[0] - 90, MON[1], MON[0], MON[1])
    p.lineTo(*END)
    return p


def curve_green():
    p = skia.Path()
    p.moveTo(OX, OY - 5)
    p.cubicTo(OX + 300, OY - 40, END[0] - 300, CY - 40, END[0], CY - 220)
    return p


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：新系统登录页闪光；两周后又是表格；桌上一摞“使用手册”
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k1_lap, k1_cal, k1_sheet, k1_man, k1_li = seq(j, [None, (0, 1, 0.3), (0, 2, 0.6), (1, 1, 0.5), (1, 2, 0.5)])
L.note("新系统", "登录", "两周后", "使用手册", "学工具")


def lap1(c, T, cx=cx, cy=cy):
    desk(c, cx, cy + 250, 760)
    x, y = cx - 40, cy + 230
    laptop(c, x, y, 1.6)
    sheet = T >= tb(1, k1_sheet)
    if sheet:
        sheet_grid(c, x, y - 170, 360, 230)
    else:
        box(c, x, y - 170, 360, 230, BLUE_FILL, BLUE, 4, 6)
        label(c, "新系统", x, y - 220, 60, BLUE)
        box(c, x, y - 130, 200, 54, "#FFFFFF", BLUE, 4, 20)
        label(c, "登录", x, y - 128, 38, BLUE)
        sparkle(c, x + 160, y - 280, (T - tb(1, k1_lap)) % 1.2, YELLOW, 8, 30, 90)


pop(j, k1_lap, cx, cy + 100, lap1, "ding", 0.75)


def cal1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k1_cal))
    if sc <= 0:
        return None
    with at_pop(c, cx - 380, cy - 380, sc):
        calendar_page(c, cx - 380, cy - 380, 280, 220, "两周后")
    return None


ev(j, k1_cal, cal1, "wood_high", 0.75)
b.hit(j, k1_sheet, "rim", 0.8, "屏幕又变回表格")


def man1(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(1, k1_man)
    if dt < 0:
        return None
    x, y = cx + 340, cy + 230
    for i in range(5):
        d = dt - 0.06 * i
        if d < 0:
            continue
        drop = (1 - ease_out(clamp01(d / 0.18))) * 200
        with K.at(c, x + (i % 2) * 10, y - 18 - i * 34 - drop, (i % 3 - 1) * 3):
            box(c, 0, 0, 230, 34, (BLUE_FILL, ORANGE_FILL, GREEN_FILL)[i % 3], BLACK, 5, 4)
    if dt > 0.3:
        label(c, "使用手册", x, y - 230, 50, GRAY)
    return None


ev(j, k1_man, man1, "wood_low", 0.8)


def li1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k1_li))
    if sc <= 0:
        return None
    with at_pop(c, cx - 420, cy + 400, sc):
        draw_li(c, cx - 430, cy + 560, 0.8, "sad", squash=0.94)
        sweat(c, cx - 370, cy + 260, 1.2)
        label(c, "学工具", cx - 420, cy + 120, 54, RED)
    return None


ev(j, k1_li, li1, "tom", 0.8)

# ================================================================ 屏 2（drop）：坐标轴画出来，曲线冲到顶，顶上一群小人围着试
j = L.scene(2, (CX, CY + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 14.0)], [(KD, 0.4)]
k2_ax = min(max(kq(j, wt(2, 0, 0.5), 0), 0), KD - 3)
k2_lab = min(max(kq(j, wt(2, 1, 0.5), k2_ax + 1), k2_ax + 1), KD - 2)
k2_t0 = min(max(kq(j, wt(3, 0, 0.5), k2_lab + 1), k2_lab + 1), KD - 1)
L.note("热度", "时间", "上线", "一个新工具的一生", "人人都在试")
b.path(j, k2_ax, k2_ax + 0.6, P((OX, CY - 470), (OX, OY), (END[0] + 30, OY)), BLACK, 10, sfx="wood_high", gain=0.75)
b.path(j, k2_ax + 0.3, k2_ax + 0.6, P((OX - 24, CY - 440), (OX, CY - 475), (OX + 24, CY - 440)), BLACK, 10)
b.text(j, k2_lab, k2_lab + 0.4, "热度", OX + 80, CY - 470, 54, GRAY, sfx="pop", gain=0.6)
b.text(j, k2_lab + 0.3, k2_lab + 0.7, "时间", END[0] - 30, OY + 60, 50, GRAY)
b.text(j, k2_lab + 0.5, k2_lab + 0.9, "一个新工具的一生", CX + 250, CY - 470, 54, BLACK)
ev(j, k2_t0, L.pop_text("上线", OX + 30, OY + 60, 46, BLUE, j, k2_t0), "pop", 0.7)
b.path(j, KD, KD + 0.35, curve_up(), RED, 14, sfx="kick", gain=0.85)


def crowd2(c, kk, T):
    dt = T - tb(2, KD) - 0.3
    if dt < 0:
        return None
    for n, (dx, h) in enumerate(((-130, 0), (-40, 1), (60, 0), (150, 1))):
        g = pop_scale(dt - 0.08 * n)
        if g <= 0:
            continue
        x, y = PEAK[0] + dx, PEAK[1] - 30 + abs(dx) * 0.25
        jump = -abs(math.sin((T + n) * 7)) * 18
        with K.at(c, x, y + jump, 0, g * 0.45):
            c.drawPath(wb.stick(0, 0, 1.0, arms="up"), wb.marker(BLACK, 12))
            c.drawPath(wb.face(0, 0, 1.0, "smile"), wb.marker(BLACK, 9))
    if dt > 0.4:
        app_icon(c, PEAK[0] + 10, PEAK[1] - 250, 46, 0)
        sparkle(c, PEAK[0] + 10, PEAK[1] - 250, (dt - 0.4) % 1.4, YELLOW, 8, 50, 110)
        fade = 1 - clamp01((T - tb(3, 0)) / 0.4)
        if fade > 0:
            label(c, "人人都在试", PEAK[0] + 330, PEAK[1] - 90, 52, RED, alpha=clamp01((dt - 0.4) / 0.2) * fade)
    return None


ev(j, KD, crowd2)

# ================================================================ 屏 3：第二周，流程和新工具的接口对不上，曲线往下掉
j = L.scene(3, (CX, CY + 10, Z))
k3_wk, k3_flow, k3_bump, k3_down = seq(j, [None, (4, 1, 0.3), (4, 1, 0.8), (4, 2, 0.4)])
L.note("第二周", "流程", "对不上")
ev(j, k3_wk, L.pop_text("第二周", WK2[0], OY + 60, 46, BLUE, j, k3_wk), "pop", 0.7)


def flow3(c, kk, T):
    sc = pop_scale(T - tb(3, k3_flow))
    if sc <= 0:
        return None
    x, y = CX + 330, CY - 60
    sc *= 1 - clamp01((T - tb(4, 0)) / 0.4)
    if sc <= 0:
        return None
    dt_b = T - tb(3, k3_bump)
    gap = 40 + (wobble(dt_b, 14, 30, 6) if dt_b >= 0 else 60 * (1 - clamp01((T - tb(3, k3_flow)) / 0.8)))
    with at_pop(c, x, y, sc):
        box(c, x - 120 - gap / 2, y, 190, 130, "#FFFFFF", BLACK, 6, 12)
        label(c, "流程", x - 120 - gap / 2, y - 10, 50, BLACK)
        c.drawCircle(x - 25 - gap / 2, y, 24, K.paint(ORANGE))
        c.drawCircle(x - 25 - gap / 2, y, 24, wb.marker(BLACK, 5))
        app_icon(c, x + 110 + gap / 2, y, 64, 0)
        c.drawRect(skia.Rect.MakeXYWH(x + 46 + gap / 2 - 40, y - 22, 40, 44), K.paint(BLUE))
        c.drawRect(skia.Rect.MakeXYWH(x + 46 + gap / 2 - 40, y - 22, 40, 44), wb.marker(BLACK, 5))
        if dt_b >= 0:
            with K.at(c, x, y - 120, -6, C.slam_scale(dt_b)):
                box(c, 0, 0, 210, 80, "#FFFFFF", RED, 7, 12)
                label(c, "对不上", 0, 2, 52, RED)
    return None


ev(j, k3_flow, flow3, "wood_low", 0.75)
b.hit(j, k3_bump, "rim", 0.85, "接口卡住")
b.path(j, k3_down, k3_down + 0.7, curve_down(), RED, 14, sfx="tom", gain=0.85)

# ================================================================ 屏 4：一个月后曲线贴地，只剩一个小人在角落里用
j = L.scene(4, (CX, CY + 10, Z))
k4_mon, k4_flat, k4_one, k4_lab = seq(j, [None, (5, 0, 0.6), (5, 1, 0.5), (5, 2, 0.6)])
L.note("一个月", "贴地")
ev(j, k4_mon, L.pop_text("一个月", MON[0], OY + 60, 46, BLUE, j, k4_mon), "pop", 0.7)
b.path(j, k4_flat, k4_flat + 0.7, curve_flat(), RED, 14, sfx="wood_low", gain=0.8)


def one4(c, kk, T):
    dt = T - tb(4, k4_one)
    if dt < 0:
        return None
    g = pop_scale(dt)
    x, y = END[0] - 40, OY - 20
    with K.at(c, x, y, 0, g * 0.45):
        c.drawPath(wb.stick(0, 0, 1.0, arms="down"), wb.marker(GRAY, 12))
        c.drawPath(wb.face(0, 0, 1.0, "sad"), wb.marker(GRAY, 9))
    app_icon(c, x - 70, y - 90, 26, 0, gray=True, alpha=clamp01(dt / 0.2))
    return None


ev(j, k4_one, one4, "pop", 0.75)


def lab4(c, kk, T):
    dt = T - tb(4, k4_lab)
    if dt < 0:
        return None
    with K.at(c, MON[0] - 80, MON[1] - 120, -4, C.slam_scale(dt)):
        label(c, "贴地", 0, 0, 70, RED)
    return None


ev(j, k4_lab, lab4, "bongo_low", 0.85)

# ================================================================ 屏 5：“可靠”“试过”“帮得上人和流程”三张卡逐个亮
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k5_w, k5_c1, k5_c2, k5_c3 = seq(j, [None, (7, 0, 0.6), (7, 0, 0.9), (7, 1, 0.5)])
CARDS5 = [("可靠", GREEN), ("试过", BLUE), ("帮得上人和流程", ORANGE)]
L.note("另一种态度", *[c_[0] for c_ in CARDS5])


def w5(c, T, cx=cx, cy=cy):
    hy = cy + 560 - 290 * 0.85
    nod = 6 * math.sin(T * 5)
    draw_worker(c, cx - 380, cy + 560, 0.85, mood="smile", rh=(cx - 270, hy + 20 + nod))
    label(c, "另一种态度", cx - 120, cy - 480, 70, BLACK)


pop(j, k5_w, cx - 300, cy + 300, w5, "wood_low", 0.75)
for n, k_ in enumerate((k5_c1, k5_c2, k5_c3)):
    def card5(c, kk, T, n=n, k_=k_, cx=cx, cy=cy):
        dt = T - tb(5, k_)
        if dt < 0:
            return None
        s_, col = CARDS5[n]
        x, y = cx + 140, cy - 280 + n * 210
        w = 330 if n < 2 else 640
        if n == 2:
            x = cx + 20
        with K.at(c, x, y, 0, pop_scale(dt)):
            box(c, 0, 0, w, 150, "#FFFFFF", col, 9, 22)
            tick(c, -w / 2 + 60, 0, 30, clamp01(dt / 0.3), col, 10)
            label(c, s_, 30, 0, 66, col)
            if dt < 0.8:
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 - 10, -85, w + 20, 170), 26, 26, K.paint(col, 0.25 * (1 - dt / 0.8),
                                                                                                blur=14))
        return None
    ev(j, k_, card5, ("pop", "pop", "ding")[n], 0.8)

# ================================================================ 屏 6：车间一角围出试验区试新机器；试稳了，虚线框扩到整条线
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k6_line, k6_box, k6_mach, k6_ok, k6_grow = seq(j, [None, (8, 1, 0.2), (8, 1, 0.7), (8, 2, 0.2), (8, 2, 0.7)])
L.note("试一试", "铺开")


def line6(c, T, cx=cx, cy=cy):
    by = cy + 250
    box(c, cx, by, 1060, 50, "#C9CED6", BLACK, 6, 25)
    for i in range(4):
        x = cx - 390 + i * 260
        box(c, x, by - 110, 170, 150, GRAY_FILL, BLACK, 6, 12)
    hy = cy + 560 - 290 * 0.7
    draw_worker(c, cx + 430, cy + 560, 0.7, mood="flat")


pop(j, k6_line, cx, cy + 200, line6, "wood_low", 0.75)


def trial6(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k6_box)
    if dt < 0:
        return None
    f = ease_out(clamp01((T - tb(6, k6_grow)) / 0.6)) if T >= tb(6, k6_grow) else 0.0
    x0 = cx - 390
    w = lerp(240, 1100, f)
    xc = lerp(x0, cx, f)
    dashed_rect(c, xc, cy + 140, w, 360, GREEN, 8, clamp01(dt / 0.2), 20, 26, 16)
    if f < 0.5:
        label(c, "试一试", x0, cy - 100, 54, GREEN, alpha=clamp01(dt / 0.2) * (1 - f * 2))
    if T >= tb(6, k6_mach):
        g = pop_scale(T - tb(6, k6_mach))
        for i in range(4):
            if i > 0 and f < (i / 4):
                continue
            x = cx - 390 + i * 260
            with K.at(c, x, cy + 100, 0, g if i == 0 else pop_scale(T - tb(6, k6_grow) - 0.12 * i)):
                box(c, 0, 0, 170, 150, BLUE_FILL, BLUE, 6, 12)
                gear(c, 0, -10, 34, (T - tb(6, k6_mach)) * 150, BLUE)
    if T >= tb(6, k6_ok):
        tick(c, x0 + 90, cy - 30, 34, clamp01((T - tb(6, k6_ok)) / 0.3))
    if f > 0.6:
        label(c, "铺开", cx, cy - 170, 90, GREEN, alpha=clamp01((f - 0.6) / 0.3))
    return None


ev(j, k6_box, trial6, "wood_high", 0.75)
b.hit(j, k6_mach, "pop", 0.8, "新机器放进试验区")
b.hit(j, k6_ok, "ding", 0.8, "试稳了")
b.hit(j, k6_grow, "shaker", 0.8, "框扩到整条线")

# ================================================================ 屏 7：闪亮的新机器想插进流程，接口形状不对，被推回去
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k7_line, k7_new, k7_bump, k7_no = seq(j, [None, (9, 0, 0.4), (9, 0, 0.9), (9, 1, 0.5)])
L.note("最新款", "不要")


def line7(c, T, cx=cx, cy=cy):
    by = cy + 300
    box(c, cx - 300, by - 120, 300, 200, GRAY_FILL, BLACK, 6, 16)
    c.drawCircle(cx - 150, by - 120, 34, K.paint("#FFFFFF"))
    c.drawCircle(cx - 150, by - 120, 34, wb.marker(BLACK, 6))
    label(c, "我们的流程", cx - 300, by - 280, 50, BLACK)


L.note("我们的流程")
pop(j, k7_line, cx - 300, cy + 200, line7, "wood_low", 0.75)


def new7(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(7, k7_new)
    if dt < 0:
        return None
    t_b = tb(7, k7_bump)
    if T < t_b:
        x = lerp(cx + 560, cx + 160, ease_in_out(clamp01((T - tb(7, k7_new)) / max(0.1, t_b - tb(7, k7_new)))))
    else:
        x = cx + 160 + 160 * ease_out(clamp01((T - t_b) / 0.4)) + wobble(T - t_b, 10, 30, 6)
    with K.at(c, x, cy + 300, 0, pop_scale(dt)):
        machine(c, 0, 0, 1.0, "square", True, T=T)
        label(c, "最新款", 0, -270, 50, BLUE)
    if T >= t_b:
        hy = cy + 560 - 290 * 0.75
        draw_worker(c, cx - 30, cy + 560, 0.75, mood="flat", rh=(cx + 50, hy + 90), lh=(cx + 40, hy + 120))
    return None


ev(j, k7_new, new7, "shaker", 0.75)
b.hit(j, k7_bump, "rim", 0.85, "接口对不上，被推回去")
ev(j, k7_no, L.stamp("不要", cx + 330, cy - 280, 96, j, k7_no), "kick", 0.85)

# ================================================================ 屏 8：先用手把流程理顺，机器再接上；对照：乱箭头加马达，转得更乱
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k8_tan, k8_hand, k8_mach, k8_bad, k8_fast = seq(j, [None, (10, 0, 0.7), (10, 1, 0.5), (11, 1, 0.4), (11, 2, 0.5)])
L.note("先用手", "再上机器", "乱得更快")


def top8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k8_tan))
    if sc <= 0:
        return None
    y = cy - 260
    f = ease_in_out(clamp01((T - tb(8, k8_hand)) / 0.8)) if T >= tb(8, k8_hand) else 0.0
    with at_pop(c, cx, y, sc):
        p = skia.Path()
        p.moveTo(cx - 480, y)
        for i in range(1, 9):
            u = i / 8
            p.lineTo(cx - 480 + 640 * u + (1 - f) * 60 * math.sin(i * 2.7), y + (1 - f) * 110 * math.sin(i * 1.9))
        c.drawPath(p, wb.marker(GREEN if f >= 1 else GRAY, 9))
        c.drawPath(P((cx + 130, y - 24), (cx + 166, y), (cx + 130, y + 24)), wb.marker(GREEN if f >= 1 else GRAY, 9))
        label(c, "先用手", cx - 330, y - 190, 54, GREEN)
        hy = y + 260 - 290 * 0.6
        draw_worker(c, cx - 260 + 300 * f, y + 260, 0.6, mood="smile", rh=(cx - 180 + 300 * f, y + 30))
        if T >= tb(8, k8_mach):
            g = pop_scale(T - tb(8, k8_mach))
            with K.at(c, cx + 360, y + 130, 0, g * 0.75):
                machine(c, 0, 0, 1.0, "round")
                gear(c, 30, -140, 22, (T - tb(8, k8_mach)) * 90, BLUE)
            label(c, "再上机器", cx + 360, y - 190, 54, BLUE, alpha=clamp01(g))
            tick(c, cx + 180, y - 90, 30, clamp01((T - tb(8, k8_mach)) / 0.3))
    return None


ev(j, k8_tan, top8, "wood_low", 0.75)
b.hit(j, k8_hand, "shaker", 0.75, "用手理顺")
b.hit(j, k8_mach, "pop", 0.8, "机器接上")


def bot8(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k8_bad)
    if dt < 0:
        return None
    y = cy + 300
    dashed(c, (cx - 540, cy + 90), (cx + 540, cy + 90), GRAY, 4)
    fast = T >= tb(8, k8_fast)
    spin = (T - tb(8, k8_bad)) * (900 if fast else 120)
    with K.at(c, cx - 130, y, 0, pop_scale(dt)):
        with K.at(c, 0, 0, spin * 0.3 if fast else 0):
            c.drawPath(tangle(0, 0, 420, 240, 5), wb.marker(RED, 9))
            c.drawPath(tangle(0, 20, 380, 200, 9), wb.marker(RED, 7))
        box(c, 300, 40, 140, 110, "#C9CED6", BLACK, 6, 12)
        gear(c, 300, 40, 34, spin, BLACK)
        if fast:
            for i in range(3):
                C.line(c, (380, -10 + i * 30), (440 + 20 * math.sin(T * 30 + i), -10 + i * 30), GRAY, 5)
    if fast:
        with K.at(c, cx + 200, cy + 520, -4, C.slam_scale(T - tb(8, k8_fast))):
            label(c, "乱得更快", 0, 0, 74, RED)
    return None


ev(j, k8_bad, bot8, "wood_high", 0.75)
b.hit(j, k8_fast, "bongo_low", 0.85, "转得更乱")

# ================================================================ 屏 9：回到曲线（拉远）：小李抱着大锤，到处找能用它的地方
j = L.scene(9, FAR)
k9_q, k9_li, k9_n1, k9_n2 = seq(j, [(12, 1, 0.3), (13, 0, 0.5), (13, 1, 0.3), (13, 1, 0.8)])
L.note("为什么掉？", "先挑工具", "能干什么？")


def q9(c, kk, T):
    dt = T - tb(9, k9_q)
    if dt < 0:
        return None
    with K.at(c, (PEAK[0] + WK2[0]) / 2 + 70, (PEAK[1] + WK2[1]) / 2 - 60, 0, pop_scale(dt)):
        c.drawCircle(0, 0, 70, wb.marker(ORANGE, 8))
        label(c, "？", 0, 4, 90, ORANGE, "black")
    with K.at(c, CX - 250, CY + 480, 0, pop_scale(dt - 0.1)):
        label(c, "为什么掉？", 0, 0, 84, ORANGE)
    return None


ev(j, k9_q, q9, "rim", 0.8)


def li9(c, kk, T):
    dt = T - tb(9, k9_li)
    if dt < 0:
        return None
    gy = CY + 1040
    x, dy, _ = C.walk(T, tb(9, k9_li), 1.6, CX - 640, CX - 300, 14, 3)
    with K.at(c, x, gy, 0, pop_scale(dt)):
        c.translate(-x, -gy)
        hy = gy - 290 * 0.85
        draw_li(c, x, gy + dy, 0.85, "o", rh=(x + 70, hy + 140), lh=(x + 40, hy + 160))
        hammer(c, x + 80, hy + 110, 30, 1.2)
        label(c, "先挑工具", x - 60, gy - 420, 70, RED)
    return None


ev(j, k9_li, li9, "wood_low", 0.75)
for n, k_ in enumerate((k9_n1, k9_n2)):
    def nail9(c, kk, T, n=n, k_=k_):
        dt = T - tb(9, k_)
        if dt < 0:
            return None
        x, y = CX - 60 + n * 130, CY + 860 + n * 60
        with K.at(c, x, y, 0, pop_scale(dt)):
            label(c, "？", 0, 0, 100, GRAY, "black")
        if n == 1:
            with K.at(c, CX - 10, CY + 690, 0, pop_scale(dt - 0.1)):
                bubble_text(c, "能干什么？", 0, 0, 70, BLACK, -1)
        return None
    ev(j, k_, nail9, ("pop", "bongo_high")[n], 0.75)

# ================================================================ 屏 10：丰田先圈出卡住的一步，工具正好嵌进去；图上一条绿线慢慢往上爬
j = L.scene(10, FAR)
k10_flow, k10_ring, k10_fit, k10_up = seq(j, [(14, 0, 0.4), (14, 0, 0.9), (14, 1, 0.6), (15, 2, 0.3)])
L.note("卡住", "丰田反过来", "慢慢往上走")


def flow10(c, kk, T):
    dt = T - tb(10, k10_flow)
    if dt < 0:
        return None
    y = CY + 820
    xs = [CX + 80, CX + 260, CX + 440, CX + 620]
    with K.at(c, CX + 350, y, 0, pop_scale(dt)):
        c.translate(-(CX + 350), -y)
        label(c, "丰田反过来", CX + 350, y - 230, 72, GREEN)
        for i, x in enumerate(xs):
            if i:
                C.line(c, (xs[i - 1] + 60, y), (x - 60, y), BLACK, 6)
            fill = RED_FILL if i == 2 else "#FFFFFF"
            box(c, x, y, 120, 100, fill, BLACK, 6, 12)
        if T >= tb(10, k10_ring):
            d = T - tb(10, k10_ring)
            part, _ = wb.partial(wb.circle(xs[2], y, 90), clamp01(d / 0.4))
            c.drawPath(part, wb.marker(RED, 9))
            label(c, "卡住", xs[2], y + 150, 64, RED, alpha=clamp01(d / 0.3))
        if T >= tb(10, k10_fit):
            d = T - tb(10, k10_fit)
            yy = lerp(y - 220, y, ease_out(clamp01(d / 0.4)))
            app_icon(c, xs[2], yy, 46, 2)
            if d > 0.4:
                sparkle(c, xs[2], y, d - 0.4, GREEN)
    return None


ev(j, k10_flow, flow10, "wood_low", 0.75)
b.hit(j, k10_ring, "rim", 0.8, "圈出卡住的一步")
b.hit(j, k10_fit, "clap", 0.85, "工具正好嵌进去")
b.path(j, k10_up, k10_up + 1.2, curve_green(), GREEN, 14, sfx="ding", gain=0.85)
b.text(j, k10_up + 0.8, k10_up + 1.4, "慢慢往上走", CX + 280, CY - 330, 60, GREEN)

# ================================================================ 屏 11：协作软件页面空空的；群聊里文件一条接一条
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k11_app, k11_f1, k11_f2, k11_f3 = seq(j, [None, (17, 1, 0.2), (17, 1, 0.6), (17, 1, 0.95)])
L.note("协作软件", "空", "文件", "工作群")


def app11(c, T, cx=cx, cy=cy):
    x, y = cx - 250, cy - 150
    box(c, x, y, 500, 380, "#FFFFFF", BLUE, 7, 14)
    c.drawRect(skia.Rect.MakeXYWH(x - 250, y - 190, 500, 60), K.paint(BLUE))
    label(c, "协作软件", x, y - 160, 44, "#FFFFFF")
    for i in range(3):
        dashed_rect(c, x - 160 + i * 160, y + 40, 130, 200, GRAY, 4)
    label(c, "空", x, y + 40, 80, GRAY)
    mini_curve(c, cx + 400, cy - 470, 2, T)


pop(j, k11_app, cx - 200, cy - 150, app11, "wood_low", 0.75)


def chat11(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(11, k11_f1)
    if dt < 0:
        return None
    x, y = cx + 300, cy + 140
    phone(c, x, y, 330, 560)
    label(c, "工作群", x, y - 230, 38, GRAY)
    for n, k_ in enumerate((k11_f1, k11_f2, k11_f3)):
        d = T - tb(11, k_)
        if d < 0:
            continue
        with K.at(c, x, y - 140 + n * 130, 0, pop_scale(d)):
            box(c, 0, 0, 240, 100, GREEN_FILL, GREEN, 4, 16)
            c.drawPath(P((-90, -30), (-50, -30), (-36, -16), (-36, 34), (-90, 34), close=True), K.paint("#FFFFFF"))
            c.drawPath(P((-90, -30), (-50, -30), (-36, -16), (-36, 34), (-90, 34), close=True), wb.marker(BLACK, 4))
            label(c, "文件", 40, 2, 40, BLACK)
    gy = cy + 560
    hy = gy - 290 * 0.7
    tap = 10 * math.sin(T * 14)
    draw_wang(c, cx - 300, gy, 0.7, mood="flat", rh=(cx - 220, hy + 60 + tap))
    phone(c, cx - 200, hy + 60, 70, 120)
    return None


ev(j, k11_f1, chat11, "pop", 0.75)
b.hit(j, k11_f2, "pop", 0.75, "又一个文件")
b.hit(j, k11_f3, "pop", 0.8, "又一个文件")

# ================================================================ 屏 12：一排人工智能工具图标，每个旁边一个“一下午”的钟；小李还在自己敲日报
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k12_i1, k12_i2, k12_i3, k12_li = seq(j, [(18, 0, 0.5), (18, 1, 0.2), (18, 1, 0.7), (18, 2, 0.4)])
L.note("一下午", "日报")


def icons12(n, k_):
    def fn(c, kk, T, cx=cx, cy=cy):
        dt = T - tb(12, k_)
        if dt < 0:
            return None
        x, y = cx - 380 + n * 270, cy - 330
        with K.at(c, x, y, 0, pop_scale(dt)):
            app_icon(c, 0, 0, 70, n + 1)
            clock_face(c, 70, 110, 52, clamp01(dt / 1.5) * 0.5, None, ORANGE, ORANGE_FILL)
            label(c, "一下午", 0, 205, 44, GRAY)
        if n == 0:
            mini_curve(c, cx + 400, cy - 480 + 0 * T, 1, T)
        return None
    return fn


ev(j, k12_i1, icons12(0, k12_i1), "pop", 0.75)
ev(j, k12_i2, icons12(1, k12_i2), "pop", 0.75)
ev(j, k12_i3, icons12(2, k12_i3), "bongo_high", 0.8)


def li12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k12_li))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 300, sc):
        desk(c, cx + 60, cy + 320, 560)
        laptop(c, cx + 60, cy + 300, 1.2)
        box(c, cx + 60, cy + 180, 260, 170, "#FFFFFF", GRAY, 3, 6)
        label(c, "日报", cx + 60, cy + 130, 44, BLACK)
        n = int((T - tb(12, k12_li)) * 6) % 5
        for i in range(n):
            C.line(c, (cx - 40, cy + 175 + i * 20), (cx + 150 - (i % 2) * 40, cy + 175 + i * 20), GRAY, 5)
        hy = cy + 580 - 290 * 0.8
        tap = 12 * math.sin(T * 20)
        draw_li(c, cx - 330, cy + 580, 0.8, "sad", rh=(cx - 80, cy + 290 + tap), lh=(cx - 120, cy + 300 - tap))
    return None


ev(j, k12_li, li12, "wood_low", 0.8)

# ================================================================ 屏 13：客厅里智能音箱只亮着一个闹钟图标
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k13_room, k13_spk, k13_alarm, k13_li = seq(j, [None, (19, 0, 0.6), (19, 1, 0.5), (19, 1, 0.9)])
L.note("只用来定闹钟", "天气", "音乐", "提醒")


def room13(c, T, cx=cx, cy=cy):
    gy = cy + 470
    C.line(c, (cx - 560, gy), (cx + 560, gy), GRAY, 6)
    sofa = P((cx - 480, gy - 20), (cx - 480, gy - 200), (cx - 440, gy - 230), (cx - 60, gy - 230), (cx - 20, gy - 200),
             (cx - 20, gy - 20), close=True)
    c.drawPath(sofa, K.paint("#E3C9A0"))
    c.drawPath(sofa, wb.marker(WOOD_LINE, 7))
    box(c, cx + 260, gy - 90, 280, 180, "#FFFFFF", WOOD_LINE, 7, 10)
    mini_curve(c, cx + 400, cy - 480, 2, T)


pop(j, k13_room, cx, cy + 300, room13, "wood_low", 0.75)


def spk13(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(13, k13_spk)
    if dt < 0:
        return None
    x, y = cx + 260, cy + 200
    with K.at(c, x, y, 0, pop_scale(dt)):
        c.drawRoundRect(skia.Rect.MakeXYWH(-60, -130, 120, 170), 40, 40, K.paint("#3B3F48"))
        c.drawRoundRect(skia.Rect.MakeXYWH(-60, -130, 120, 170), 40, 40, wb.marker(BLACK, 6))
        for i in range(3):
            C.line(c, (-34, -80 + i * 30), (34, -80 + i * 30), GRAY, 4)
    for n, s_ in enumerate(("天气", "音乐", "提醒")):
        d = dt - 0.1 * n
        if d < 0:
            continue
        a = 1.0 if T < tb(13, k13_alarm) else 0.25
        with K.at(c, x - 230 + n * 230, cy - 200 - (n % 2) * 60, 0, pop_scale(d)):
            box(c, 0, 0, 170, 80, GRAY_FILL, GRAY, 4, 30, a)
            label(c, s_, 0, 2, 44, GRAY, alpha=a)
    return None


ev(j, k13_spk, spk13, "pop", 0.75)


def alarm13(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(13, k13_alarm)
    if dt < 0:
        return None
    x, y = cx + 260, cy - 30
    with K.at(c, x, y - 40, wobble(dt, 8, 30, 3), pop_scale(dt)):
        clock_face(c, 0, 0, 90, 0, 0.1, ORANGE, ORANGE_FILL)
    label(c, "只用来定闹钟", cx - 60, cy - 420, 64, ORANGE, alpha=clamp01(dt / 0.2))
    return None


ev(j, k13_alarm, alarm13, "ding", 0.85)


def li13(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(13, k13_li)
    if dt < 0:
        return None
    with K.at(c, cx - 250, cy + 300, 0, pop_scale(dt)):
        c.translate(-(cx - 250), -(cy + 300))
        draw_li(c, cx - 250, cy + 420, 0.6, "smile")
    return None


ev(j, k13_li, li13, "wood_low", 0.7)

# ================================================================ 屏 14：小李看着一列新工具，背后有人在跑，他怕被落下；大字“三步”
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k14_col, k14_run, k14_li, k14_3 = seq(j, [None, (20, 2, 0.3), (20, 2, 0.8), (21, 1, 0.3)])
L.note("新出的", "怕落后")


def col14(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(14, k14_col)
    if dt < 0:
        return None
    for n in range(5):
        d = dt - 0.08 * n
        if d < 0:
            continue
        with K.at(c, cx + 400, cy - 330 + n * 150, 0, pop_scale(d)):
            app_icon(c, 0, 0, 56, n)
    label(c, "新出的", cx + 400, cy - 470, 50, GRAY)
    return None


ev(j, k14_col, col14, "pop", 0.75)


def run14(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(14, k14_run)
    if dt < 0:
        return None
    gy = cy + 560
    for n in range(2):
        x, dy, _ = C.walk(T, tb(14, k14_run) + 0.15 * n, 1.4, cx - 600 + n * 80, cx + 160 + n * 80, 18, 4)
        draw_wang(c, x, gy + dy - 40, 0.55, mood="smile", lh=(x - 50, gy - 160), rh=(x + 60, gy - 180)) if n == 0 else \
            draw_worker(c, x, gy + dy - 40, 0.55, mood="smile", lh=(x - 50, gy - 160), rh=(x + 60, gy - 180))
    return None


ev(j, k14_run, run14, "shaker", 0.75)


def li14(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(14, k14_li)
    if dt < 0:
        return None
    with K.at(c, cx - 60, cy + 360, 0, pop_scale(dt)):
        c.translate(-(cx - 60), -(cy + 360))
        draw_li(c, cx - 60, cy + 470, 0.8, "sad")
        sweat(c, cx, cy + 180, 1.2)
        bubble_text(c, "怕落后", cx - 120, cy + 20, 54, BLACK, 1)
    return None


ev(j, k14_li, li14, "tom", 0.8)
ev(j, k14_3, L.slam_text("三步", cx - 140, cy - 380, 170, RED, j, k14_3, rot=-4), "kick", 0.9)
b.shots[j].shake = [(k14_3, 9.0)]

# ================================================================ 屏 15：做法一——便签先写“最烦的一步”，再拿扳手对准它
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k15_n, k15_note, k15_tool, k15_x = seq(j, [None, (22, 1, 0.5), (22, 2, 0.5), (22, 3, 0.5)])
L.note("第一", "最烦的一步", "先", "再找工具", "别反过来")
pop(j, k15_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: label(c, "第一", cx - 380, cy - 470, 90, RED), "rim", 0.8)


def note15(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(15, k15_note)
    if dt < 0:
        return None
    with K.at(c, cx - 150, cy - 160, -3, pop_scale(dt)):
        box(c, 0, 0, 440, 260, NOTE_FILL, ORANGE, 6, 8)
        label(c, "先", -160, -80, 50, GRAY)
        label(c, "最烦的一步", 0, 20, 70, BLACK)
    with K.at(c, cx - 380, cy + 300, 0, pop_scale(dt)):
        c.translate(-(cx - 380), -(cy + 300))
        hy = cy + 560 - 290 * 0.8
        draw_li(c, cx - 400, cy + 560, 0.8, "flat", rh=(cx - 300, hy + 30))
    return None


ev(j, k15_note, note15, "wood_high", 0.8)


def tool15(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(15, k15_tool)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.5))
    x, y = lerp(cx + 500, cx + 230, f), lerp(cy + 300, cy - 60, f)
    with K.at(c, x, y, -40):
        c.drawRoundRect(skia.Rect.MakeXYWH(-14, 0, 28, 180), 10, 10, K.paint("#B8BEC8"))
        c.drawRoundRect(skia.Rect.MakeXYWH(-14, 0, 28, 180), 10, 10, wb.marker(BLACK, 5))
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(-40, -46, 80, 80), 120, 300)
        c.drawPath(p, wb.marker(BLACK, 12))
    if f >= 1:
        label(c, "再找工具", cx + 300, cy + 280, 56, BLUE)
    return None


ev(j, k15_tool, tool15, "clap", 0.85)
ev(j, k15_x, L.pop_text("别反过来", cx + 150, cy + 470, 64, RED, j, k15_x), "pop", 0.8)

# ================================================================ 屏 16：做法二——新工具先放进一个小框（一件小事），日历两周打勾，框扩大
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
k16_n, k16_box, k16_cal, k16_big = seq(j, [None, (23, 1, 0.5), (23, 2, 0.3), (23, 2, 0.8)])
L.note("第二", "一件小事", "两周", "扩大")
pop(j, k16_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: label(c, "第二", cx - 380, cy - 470, 90, RED), "rim", 0.8)


def box16(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(16, k16_box)
    if dt < 0:
        return None
    f = ease_out(clamp01((T - tb(16, k16_big)) / 0.5)) if T >= tb(16, k16_big) else 0.0
    w, h = lerp(300, 760, f), lerp(260, 560, f)
    x, y = cx - 150 + 150 * f, cy + 180
    dashed_rect(c, x, y, w, h, GREEN, 8, clamp01(dt / 0.2), 20)
    with K.at(c, x, y - 10, 0, pop_scale(dt)):
        app_icon(c, 0, 0, 60, 2)
    label(c, "一件小事" if f < 0.5 else "扩大", x, y + h / 2 - 50, 50, GREEN)
    hy = cy + 560 - 290 * 0.7
    if f < 0.5:
        draw_li(c, cx - 450, cy + 560, 0.7, "smile", rh=(cx - 330, hy + 40))
    return None


ev(j, k16_box, box16, "wood_high", 0.75)


def cal16(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(16, k16_cal)
    if dt < 0:
        return None
    with K.at(c, cx + 350, cy - 300, 0, pop_scale(dt)):
        calendar_page(c, 0, 0, 260, 220, "两周")
        tick(c, 70, 50, 34, clamp01((dt - 0.2) / 0.3))
    return None


ev(j, k16_cal, cal16, "ding", 0.8)
b.hit(j, k16_big, "shaker", 0.8, "框扩大")

# ================================================================ 屏 17：做法三——小李先用笔在纸上把流程走一遍，圈出一步“真能省”
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
k17_n, k17_paper, k17_walk, k17_ring = seq(j, [None, (24, 1, 0.5), (24, 2, 0.5), (24, 3, 0.5)])
L.note("第三", "真能省", "手工走一遍")
pop(j, k17_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: label(c, "第三", cx - 380, cy - 470, 90, RED), "rim", 0.8)
STEPS17 = [(cx - 300, cy - 150), (cx - 50, cy - 220), (cx + 200, cy - 150), (cx + 380, cy - 20)]


def paper17(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(17, k17_paper)
    if dt < 0:
        return None
    with K.at(c, cx, cy - 120, 0, pop_scale(dt)):
        c.translate(-cx, -(cy - 120))
        box(c, cx + 20, cy - 120, 1000, 460, "#FFFFFF", GRAY, 5, 10)
        label(c, "手工走一遍", cx - 280, cy - 300, 46, GRAY)
        f = clamp01((T - tb(17, k17_walk)) / 1.2) if T >= tb(17, k17_walk) else 0.0
        for i, (x, y) in enumerate(STEPS17):
            on = f * 4 > i
            box(c, x, y, 130, 90, GREEN_FILL if on else "#FFFFFF", BLACK, 5, 12)
            label(c, str(i + 1), x, y + 2, 50, BLACK, "sans_medium")
            if i:
                C.line(c, (STEPS17[i - 1][0] + 70, STEPS17[i - 1][1]), (x - 70, y), GRAY, 5)
        if 0 < f < 1:
            px, py = STEPS17[min(3, int(f * 4))]
            C.line(c, (px + 40, py + 40), (px + 90, py + 140), BLACK, 12)
    gy = cy + 560
    hy = gy - 290 * 0.8
    draw_li(c, cx - 330, gy, 0.8, "smile", rh=(cx - 220, hy + 40 + 10 * math.sin(T * 8)))
    return None


ev(j, k17_paper, paper17, "wood_low", 0.75)
b.hit(j, k17_walk, "shaker", 0.75, "笔顺着流程走")


def ring17(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(17, k17_ring)
    if dt < 0:
        return None
    x, y = STEPS17[1]
    part, _ = wb.partial(wb.circle(x, y, 95), clamp01(dt / 0.4))
    c.drawPath(part, wb.marker(RED, 9))
    with K.at(c, cx + 150, cy + 240, -4, pop_scale(dt - 0.2)):
        label(c, "真能省", 0, 0, 84, RED)
    C.line(c, (x + 40, y + 90), (cx + 80, cy + 180), RED, 5, clamp01((dt - 0.2) / 0.2))
    return None


ev(j, k17_ring, ring17, "ding", 0.85)

# ================================================================ 屏 18：工具小人在桌前忙，小李在旁边喝水；对照：小李围着工具转圈（打叉）
cx, cy = R[18]
j = L.scene(18, (cx, cy + 10, Z))
k18_bot, k18_cup, k18_bad, k18_x = seq(j, [None, (25, 1, 0.4), (25, 2, 0.3), (25, 2, 0.8)])
L.note("围着它转")


def robot(c, x, y, s, T, alpha=1.0):
    """工具小人：方脑袋 + 天线 + 两只机械手。(x, y) 为脚底。"""
    hy = y - 260 * s
    box(c, x, hy, 120 * s, 100 * s, BLUE_FILL, BLUE, 6, 18, alpha)
    for dx in (-25, 25):
        c.drawCircle(x + dx * s, hy - 5 * s, 10 * s, K.paint(BLUE, alpha))
    C.line(c, (x, hy - 50 * s), (x, hy - 90 * s), BLUE, 6, alpha)
    c.drawCircle(x, hy - 96 * s, 10 * s, K.paint(RED, alpha))
    box(c, x, y - 120 * s, 110 * s, 120 * s, "#FFFFFF", BLUE, 6, 16, alpha)
    sw = 30 * math.sin(T * 14)
    C.line(c, (x - 55 * s, y - 150 * s), (x - 110 * s, y - 120 * s + sw), BLUE, 9, alpha)
    C.line(c, (x + 55 * s, y - 150 * s), (x + 110 * s, y - 120 * s - sw), BLUE, 9, alpha)
    for dx in (-30, 30):
        C.line(c, (x + dx * s, y - 60 * s), (x + dx * s, y), BLUE, 9, alpha)


def top18(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(18, k18_bot)
    if dt < 0:
        return None
    gy = cy + 40
    with K.at(c, cx, gy - 150, 0, pop_scale(dt)):
        c.translate(-cx, -(gy - 150))
        desk(c, cx - 100, gy - 120, 420)
        laptop(c, cx - 100, gy - 140, 0.9)
        robot(c, cx - 100, gy, 1.2, T)
        if T >= tb(18, k18_cup):
            hy = gy - 290 * 0.75
            sip = 10 * math.sin((T - tb(18, k18_cup)) * 3)
            draw_li(c, cx + 300, gy, 0.75, "smile", rh=(cx + 250, hy + 20 + sip))
            box(c, cx + 245, hy + 10 + sip, 40, 56, "#FFFFFF", BLUE, 5, 6)
            tick(c, cx + 470, gy - 330, 40, clamp01((T - tb(18, k18_cup)) / 0.3))
    return None


ev(j, k18_bot, top18, "wood_low", 0.75)
b.hit(j, k18_cup, "pop", 0.75, "小李喝水")


def bot18(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(18, k18_bad)
    if dt < 0:
        return None
    gy = cy + 520
    dashed(c, (cx - 540, cy + 120), (cx + 540, cy + 120), GRAY, 4)
    with K.at(c, cx, gy - 150, 0, pop_scale(dt)):
        c.translate(-cx, -(gy - 150))
        app_icon(c, cx - 100, gy - 140, 60, 1)
        a = (T - tb(18, k18_bad)) * 4
        x = cx - 100 + 230 * math.cos(a)
        draw_li(c, x, gy + 20 * math.sin(a), 0.55, "sad")
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(cx - 360, gy - 120, 520, 140), 20, 300)
        c.drawPath(arc, wb.marker(GRAY, 5))
        label(c, "围着它转", cx + 330, gy - 260, 52, GRAY)
    if T >= tb(18, k18_x):
        xmark(c, cx - 100, gy - 140, 110, clamp01((T - tb(18, k18_x)) / 0.3))
    return None


ev(j, k18_bad, bot18, "shaker", 0.75)
b.hit(j, k18_x, "rim", 0.85, "打叉")

# ================================================================ 屏 19：评论区鸡肋工具和好用工具；小李把工具装进口袋往前走；下一讲预告
cx, cy = R[19]
j = L.scene(19, (cx, cy + 10, Z))
k19_cb, k19_g, k19_li, k19_go, k19_nx = seq(j, [None, (27, 0, 0.4), (28, 1, 0.5), (28, 2, 0.4), (29, 0, 0.2)])
GRIPES = [("鸡肋：只用了一次", cx - 230, cy - 440, RED), ("好用：天天开", cx + 290, cy - 440, GREEN),
          ("鸡肋：装了没打开", cx - 230, cy - 345, RED), ("好用：省半小时", cx + 290, cy - 345, GREEN)]
L.note("最鸡肋的工具？", *[g[0] for g in GRIPES], "下一讲", "眼前都顾不过来", "还要想以后吗？")


def cb19(c, T, cx=cx, cy=cy):
    comment_box(c, cx, cy - 420, 1080, 300)
    label(c, "最鸡肋的工具？", cx - 120, cy - 525, 50, RED)


pop(j, k19_cb, cx, cy - 420, cb19, "wood_high", 0.7)
for n, (s_, x, y, col) in enumerate(GRIPES):
    ev(j, k19_g, L.pop_text(s_, x, y, 46, col, j, k19_g + 0.12 * n), "pop" if n == 0 else None, 0.6)


def li19(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(19, k19_li)
    if dt < 0:
        return None
    gy = cy + 230
    C.line(c, (cx - 540, gy), (cx + 540, gy), GRAY, 5)
    pocket = T >= tb(19, k19_go)
    if pocket:
        x, dy, _ = C.walk(T, tb(19, k19_go), 1.6, cx - 200, cx + 220, 16, 3)
    else:
        x, dy = cx - 200, 0
    hy = gy - 290 * 0.72
    draw_li(c, x, gy + dy, 0.72, "smile", rh=None if pocket else (x + 80, hy + 20))
    if pocket:
        app_icon(c, x + 40, gy - 120 + dy, 22, 2)
        for i in range(3):
            C.line(c, (x - 90 - i * 26, gy - 160 + i * 40), (x - 140 - i * 26, gy - 160 + i * 40), GRAY, 5, 0.7)
    else:
        f = ease_out(clamp01(dt / 0.4))
        app_icon(c, x + 90, hy + 10 - 30 * f, 34, 2)
        for n in range(3):
            app_icon(c, cx + 200 + n * 110, gy - 60, 30, n + 3, gray=True)
    return None


ev(j, k19_li, li19, "pop", 0.75)
b.hit(j, k19_go, "shaker", 0.75, "装进口袋往前走")


def next19(c, kk, T, cx=cx, cy=cy):
    t0 = tb(19, k19_nx)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 430, sc):
        box(c, cx, cy + 430, 1000, 260, "#FFFFFF", BLUE, 8, 24)
        label(c, "下一讲", cx + 130, cy + 345, 46, BLUE)
        label(c, "眼前都顾不过来", cx + 130, cy + 425, 58, BLACK)
        label(c, "还要想以后吗？", cx + 130, cy + 505, 58, BLACK)
        x = cx - 330 + 30 * math.sin((T - t0) * 6)
        clock_face(c, cx - 400, cy + 430, 70, 0, (T - t0) * 0.5, RED, RED_FILL)
        draw_li(c, cx - 230 + 10 * math.sin((T - t0) * 8), cy + 540, 0.4, "o")
    return None


ev(j, k19_nx, next19, "wood_high", 0.75)

# ================================================================ 收尾
L.finish(cover_shot=4, square_shot=10, notes=NOTES)
L.export(globals())
