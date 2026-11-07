"""《丰田模式》15 一页纸：汇报做了三十页，为什么没人看？（白板手绘 + AI 旁白，竖屏 2:3）

两人对比：同一个问题，小李交三十页幻灯片，小王交一张纸。对比屏顶上一块“比分牌”（左“小李 · 30页”、右“小王 · 1页”，
下面各记看完用了多久），中间一道竖线把画面分成两半；讲丰田时把小王那张纸放大，按格子一格格写。
- 开场（slides）：幻灯片一摞摞往上叠到 30 页，“结论呢？”；
- 日常：月亮下小李熬夜做幻灯片；领导翻两页，“结论是什么？”；小李轻轻合上电脑；
- 两个人（drop）：左半小李抱着厚厚一摞，一页比一页满，“30页”砸下；右半小王递上一张纸，左“问题”右“怎么办”，
  领导五分钟看完，在纸上画个圈，“这里，展开说说”；
- 书中做法：纸放大，角上“A3”，两张打印纸拼起来一样大；左半三格（出了什么问题 / 现在什么样 / 想做到什么样），
  右半三格（原因 / 怎么改 / 谁、什么时候），纸边挤出来一串写不进去的字，打问号；
- 为什么：左边看的人在一堆页里拼图，问题和答案隔得老远；右边一条箭头从问题直通办法；小王对着纸想，乱线团理成一根直线；
- 说回我们：周报流水账里找不到重点；消息三段铺垫，正事在最后一行；饭桌上讲一晚上，爸妈三个问号；
  怕被说没下功夫 vs 领导的表在走，“三步”；三步做法（最上面一行写结论 / 四格写满就停 / 截图放进附件夹，问到再拿）；
  领导在小李名字旁打勾；
- 收尾：评论区报页数；一大摞纸压成一张，亮起一颗心；下一讲预告（新人头顶三个问号）。
办公室同事小王用 scenekit.draw_wang（短发、白衬衫、蓝工牌，不戴安全帽）；领导 common.draw_boss；家人 scenekit.draw_mom / draw_dad。
文案见 fengtian/PLAN.md「### 15」；时间轴、配乐、相机、人物见 fengtian/common.py，小工具见 fengtian/scenekit.py。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, pop_scale, wobble
from fengtian.scenekit import (GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL, NOTE_FILL, ORANGE_FILL, WOOD, WOOD_LINE,
                               Kit, at_pop, box, bubble_text, clock_face, comment_box, dashed, dashed_rect, desk,
                               draw_dad, draw_mom, draw_wang, draw_zhou, head_of, heart, laptop, paper, phone, qmark, sparkle,
                               sweat, tick, xmark)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)；句子分组与 PLAN 的 SCREENS_DRAFT 一致
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "两个人 · 小李", 2),
    ([4, 5], "两个人 · 小王", 3),
    ([6, 7], "丰田模式 · 书中做法", 4),
    ([8], "丰田模式 · 书中做法", 5),
    ([9, 10], "丰田模式 · 书中做法", 6),
    ([11, 12], "为什么一页纸好懂", 7),
    ([13, 14], "为什么一页纸好懂", 8),
    ([15, 16], "说回我们自己", 9),
    ([17], "说回我们自己", 10),
    ([18], "说回我们自己", 11),
    ([19, 20, 21], "说回我们自己", 12),
    ([22], "做法一 · 示意", 13),
    ([23], "做法二 · 示意", 14),
    ([24], "做法三 · 示意", 15),
    ([25], "靠谱的人", 16),
    ([26, 27, 28, 29], "评论区见", 17),
]

THEME = FT.get("15")          # 本讲样式：白色工程纸、开场 slides、转场 wipe
L = C.Lesson("15", SCREENS, drop_screen=2, board_size=(5000, 12000), theme=THEME)
b = L.b
tb, wt = L.tb, L.wt
KT = Kit(L)
kq, nx, ev, pop, seq = KT.kq, KT.nx, KT.ev, KT.pop, KT.seq

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(16)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 13 一章讲到的一页纸报告（A3 报告）——方案、汇报、改善写在一张 A3 纸上，按顺序写问题、现状、目标、原因、"
    "对策、谁什么时候做完；写不下说明还没想清楚（具体篇幅待核）。",
    "幻灯片、周报、聊天记录为示意；小李、小王、领导、家人为虚构人物。",
]

SLIDE_COLS = (BLUE, RED, GREEN, ORANGE)


# ================================================================ 本讲道具

def slide(c, x, y, w, h, n, alpha=1.0, rot=0.0):
    """一页塞满图表的幻灯片：(x, y) 为中心。"""
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, "#FFFFFF", BLACK, 5, 6, alpha)
        col = SLIDE_COLS[n % 4]
        for i in range(4):
            hh = h * (0.15 + ((n * 7 + i * 13) % 5) * 0.08)
            c.drawRect(skia.Rect.MakeXYWH(-w * 0.42 + i * w * 0.1, h * 0.36 - hh, w * 0.07, hh), K.paint(col, alpha))
        for i in range(3):
            C.line(c, (w * 0.05, -h * 0.3 + i * h * 0.2), (w * 0.42 - (i % 2) * w * 0.12, -h * 0.3 + i * h * 0.2), GRAY, 4, alpha)
        c.drawRect(skia.Rect.MakeXYWH(w * 0.05, h * 0.18, w * 0.36, h * 0.2), K.paint(GRAY_FILL, alpha))


def stack(c, x, y, n, w=300, h=180, step=10, sway=0.0):
    """一摞幻灯片：(x, y) 为最底下一页的中心。"""
    for i in range(n):
        slide(c, x + ((i * 37) % 13 - 6) + sway * i * 0.3, y - i * step, w, h, i, rot=((i * 53) % 7 - 3) * 0.6)


def a3_sheet(c, x, y, w, h, alpha=1.0, mid=True, label=True, titles=None):
    """小王的一张纸：左半“问题”、右半“怎么办”。"""
    box(c, x, y, w, h, "#FFFFFF", BLACK, 7, 8, alpha)
    if mid:
        C.line(c, (x, y - h / 2 + 20), (x, y + h / 2 - 20), GRAY, 5, alpha)
    if label:
        lt, rt = titles or ("问题", "怎么办")
        K.text(c, lt, x - w / 4, y - h / 2 + h * 0.12, h * 0.11, "hand", RED, alpha)
        K.text(c, rt, x + w / 4, y - h / 2 + h * 0.12, h * 0.11, "hand", GREEN, alpha)


L.note("问题", "怎么办")


def scoreboard(c, x, y, li_txt, wang_txt, alpha=1.0, li_t=None, wang_t=None):
    """比分牌：左“小李 · …”，右“小王 · …”。"""
    box(c, x, y, 1040, 150, "#FFFFFF", BLACK, 7, 20, alpha)
    C.line(c, (x, y - 60), (x, y + 60), BLACK, 6, alpha)
    K.text(c, "小李", x - 400, y - 28, 46, "hand", BLACK, alpha)
    K.text(c, li_txt, x - 230, y - 26, 62, "hand", RED, alpha)
    K.text(c, "小王", x + 140, y - 28, 46, "hand", BLUE, alpha)
    K.text(c, wang_txt, x + 320, y - 26, 62, "hand", GREEN, alpha)
    if li_t:
        K.text(c, li_t, x - 300, y + 40, 40, "sans_medium", GRAY, alpha)
    if wang_t:
        K.text(c, wang_t, x + 240, y + 40, 40, "sans_medium", GRAY, alpha)


L.note("小李", "小王", "30页", "1页", "看了2页", "5分钟看完")


def moon(c, x, y, r, alpha=1.0):
    m = skia.Path()
    m.addCircle(x, y, r)
    cut = skia.Path()
    cut.addCircle(x + r * 0.5, y - r * 0.3, r * 0.9)
    m = skia.Op(m, cut, skia.PathOp.kDifference_PathOp)
    c.drawPath(m, K.paint(YELLOW, alpha))
    c.drawPath(m, wb.marker("#B88A10", 4, alpha))


def pen(c, x, y, rot=-35, s=1.0, alpha=1.0):
    with K.at(c, x, y, rot):
        c.drawRoundRect(skia.Rect.MakeXYWH(-12 * s, -150 * s, 24 * s, 140 * s), 6, 6, K.paint(BLUE, alpha))
        c.drawPath(P((-12 * s, -10 * s), (12 * s, -10 * s), (0, 18 * s), close=True), K.paint(BLACK, alpha))


def folder(c, x, y, w, h, label=None, alpha=1.0):
    c.drawPath(P((x - w / 2, y - h / 2 - 30), (x - w / 6, y - h / 2 - 30), (x - w / 10, y - h / 2), (x + w / 2, y - h / 2),
                 (x + w / 2, y + h / 2), (x - w / 2, y + h / 2), close=True), K.paint("#F2C14E", alpha))
    c.drawPath(P((x - w / 2, y - h / 2 - 30), (x - w / 6, y - h / 2 - 30), (x - w / 10, y - h / 2), (x + w / 2, y - h / 2),
                 (x + w / 2, y + h / 2), (x - w / 2, y + h / 2), close=True), wb.marker(BLACK, 7, alpha))
    if label:
        K.text(c, label, x, y + 10, h * 0.28, "hand", BLACK, alpha)


def magnifier(c, x, y, r, alpha=1.0):
    c.drawCircle(x, y, r, K.paint("#E4EEF8", 0.5 * alpha))
    c.drawCircle(x, y, r, wb.marker(BLACK, 9, alpha))
    C.line(c, (x + r * 0.7, y + r * 0.7), (x + r * 1.5, y + r * 1.5), WOOD_LINE, 18, alpha)


def tangle(c, x, y, r, f, alpha=1.0):
    """乱线团 → 直线：f 0 为乱，1 为直。"""
    p = skia.Path()
    n = 60
    for i in range(n + 1):
        u = i / n
        a = u * 6 * math.pi
        rx = math.cos(a) * r * (0.4 + 0.6 * math.sin(u * 7)) * (1 - f)
        ry = math.sin(a * 1.3) * r * 0.7 * (1 - f)
        px_, py_ = x - r * 1.4 * f + 2.8 * r * f * u + rx, y + ry
        if i == 0:
            p.moveTo(px_, py_)
        else:
            p.lineTo(px_, py_)
    c.drawPath(p, wb.marker(RED if f < 1 else GREEN, 7, alpha))


def watch(c, x, y, r, T, alpha=1.0):
    """手表：表带 + 一直在走的秒针。"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - r * 0.5, y - r * 1.9, r, r * 3.8), 10, 10, K.paint("#3B3F48", alpha))
    clock_face(c, x, y, r, 0.0, (T * 0.5) % 1.0, RED, RED_FILL, alpha)


# ================================================================ 屏 0：开场（幻灯片叠到 30 页）
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：月亮下小李熬夜做幻灯片；领导翻两页，“结论是什么？”；小李合上电脑
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k1_moon, k1_li, k1_boss, k1_ask, k1_close = seq(j, [None, (0, 0, 0.7), (0, 1, 0.3), (0, 2, 0.6), (1, 1, 0.5)])
L.note("凌晨2点", "结论是什么？")


def night1(c, T, cx=cx, cy=cy):
    moon(c, cx - 420, cy - 470, 60)
    K.text(c, "凌晨2点", cx - 260, cy - 470, 50, "hand", GRAY)
    for i in range(4):
        tw = 0.5 + 0.5 * math.sin(T * 3 + i)
        c.drawCircle(cx - 470 + i * 70, cy - 380 + (i % 2) * 30, 6, K.paint(YELLOW, tw))


pop(j, k1_moon, cx - 420, cy - 470, night1, "pop", 0.6)


def li1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k1_li))
    if sc <= 0:
        return None
    x, y = cx - 300, cy + 470
    closed = T >= tb(1, k1_close)
    op = 1 - ease_in_out(clamp01((T - tb(1, k1_close)) / 0.35)) if closed else 1.0
    with at_pop(c, x, y, sc):
        desk(c, x + 150, y - 190, 440)
        laptop(c, x + 200, y - 202, 0.8, BLUE_FILL, open_=max(0.05, op))
        hy = y - 290 * 0.85
        typing = 10 * math.sin(T * 20) if not closed else 0
        draw_li(c, x - 20, y, 0.85, "sad" if T >= tb(1, k1_ask) else "flat",
                rh=(x + 100, y - 200 + typing) if not closed else (x + 120, y - 250 + 40 * (1 - op)),
                lh=(x + 60, y - 200 - typing))
        n = min(30, int(clamp01((T - tb(1, k1_li)) / 1.5) * 30))
        K.text(c, f"{n}页", x + 200, y - 470, 60, "hand", RED)
    return None


ev(j, k1_li, li1, "wood_low", 0.7)
b.hit(j, k1_close, "wood_low", 0.8, "合上电脑")


def boss1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k1_boss))
    if sc <= 0:
        return None
    x, y = cx + 330, cy + 470
    with at_pop(c, x, y, sc):
        hy = y - 290 * 0.9
        flip = (T - tb(1, k1_boss)) * 2.5
        draw_boss(c, x, y, 0.9, rh=(x - 100, hy + 120), mood="flat")
        for i in range(3):
            ang = clamp01(flip - i) * 160 if i < 2 else 0
            with K.at(c, x - 150, hy + 120, -ang * 0.2):
                slide(c, 0, 0, 160, 100, i)
    return None


ev(j, k1_boss, boss1, "wood_high", 0.7)
if k1_boss + 1 < k1_ask:
    b.hit(j, k1_boss + 1, "wood_high", 0.6, "又翻一页")
ev(j, k1_ask, L.pop_bubble("结论是什么？", cx + 230, cy - 200, j, k1_ask, 64, RED, tail=1), "rim", 0.85)

# ================================================================ 屏 2：左半小李抱着厚厚一摞，一页比一页满；drop 时“30页”砸下
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k2_sb = 0
k2_li = min(max(kq(j, wt(2, 1, 0.4), 1), 1), KD - 2)
k2_pg = min(max(kq(j, wt(3, 1, 0.2), k2_li + 1), k2_li + 1), KD - 1)
L.note("同一个问题", "背景", "数据", "截图", "图表")


def sb2(c, T, cx=cx, cy=cy):
    scoreboard(c, cx, cy - 470, "30页" if T >= tb(2, KD) else "？", "？")
    C.line(c, (cx, cy - 380), (cx, cy + 560), GRAY, 6)
    box(c, cx + 300, cy - 330, 300, 70, NOTE_FILL, ORANGE, 5, 30)
    K.text(c, "同一个问题", cx + 300, cy - 328, 44, "hand", ORANGE)


L.note("？")
pop(j, k2_sb, cx, cy - 470, sb2, "rim", 0.8)


def li2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k2_li))
    if sc <= 0:
        return None
    x, y = cx - 300, cy + 500
    n = 6
    if T >= tb(2, k2_pg):
        n = 6 + int(clamp01((T - tb(2, k2_pg)) / max(0.3, tb(2, KD) - tb(2, k2_pg))) * 18)
    sway = wobble(T - tb(2, KD), 3, 12, 3) if T >= tb(2, KD) else 0
    with at_pop(c, x, y, sc):
        hy = y - 290 * 0.85
        stack(c, x, hy + 130, n, 260, 150, 13, sway)
        draw_li(c, x, y, 0.85, "sad" if T >= tb(2, KD) else "flat", lh=(x - 120, hy + 140), rh=(x + 120, hy + 140))
    return None


ev(j, k2_li, li2, "wood_low", 0.7)
LBL2 = [("背景", -540, -60), ("数据", -110, -100), ("截图", -540, 120), ("图表", -110, 80)]


def tags2(c, kk, T, cx=cx, cy=cy):
    for n, (s_, dx, dy) in enumerate(LBL2):
        g = pop_scale(T - tb(2, k2_pg) - n * 0.12)
        if g > 0:
            with K.at(c, cx + dx + 60, cy + dy, (n % 2 * 2 - 1) * 6, g):
                box(c, 0, 0, 150, 70, "#FFFFFF", SLIDE_COLS[n], 5, 10)
                K.text(c, s_, 0, 2, 44, "hand", SLIDE_COLS[n])
    return None


ev(j, k2_pg, tags2, "pop", 0.7)


def wang2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k2_li) - 0.1)
    if sc <= 0:
        return None
    x, y = cx + 300, cy + 500
    with at_pop(c, x, y, sc):
        draw_wang(c, x, y, 0.85, mood="smile", alpha=0.35)
        qmark(c, x, y - 390, 90, T - tb(2, k2_li) - 0.3, GRAY)
    return None


ev(j, k2_li, wang2)


def thud2(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(2, KD))
    if sc <= 0:
        return None
    with K.at(c, cx - 300, cy - 320, -6, sc):
        K.text(c, "一页比一页满", 0, 0, 58, "hand", RED)
    return None


L.note("一页比一页满")
ev(j, KD, thud2, "kick", 0.95)

# ================================================================ 屏 3：右半小王递上一张纸；领导五分钟看完，在纸上画圈，“这里，展开说说”
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k3_sb, k3_wang, k3_sheet, k3_boss, k3_ring, k3_say = seq(j, [None, (4, 0, 0.5), (4, 2, 0.3), (5, 0, 0.4), (5, 1, 0.5),
                                                             (5, 2, 0.3)])
L.note("这里，展开说说", "5分钟")


def sb3(c, T, cx=cx, cy=cy):
    scoreboard(c, cx, cy - 470, "30页", "1页" if T >= tb(3, k3_sheet) else "？", li_t="看了2页",
               wang_t="5分钟看完" if T >= tb(3, k3_ring) else None)


pop(j, k3_sb, cx, cy - 470, sb3, "rim", 0.7)


def scene3(c, kk, T, cx=cx, cy=cy):
    t_w = tb(3, k3_wang)
    sc = pop_scale(T - t_w)
    if sc <= 0:
        return None
    wx, y = cx - 330, cy + 500
    hy = y - 290 * 0.85
    give = T >= tb(3, k3_sheet)
    with at_pop(c, wx, y, sc):
        draw_wang(c, wx, y, 0.85, mood="smile", rh=(wx + 130, hy + 60) if give else None)
    sb = pop_scale(T - tb(3, k3_boss))
    bx = cx + 330
    if sb > 0:
        with at_pop(c, bx, y, sb):
            nod = 6 * math.sin((T - tb(3, k3_boss)) * 4)
            draw_boss(c, bx, y, 0.9, lh=(bx - 110, hy + 50), mood="smile" if T >= tb(3, k3_say) else "flat", head_dy=nod)
            watch(c, bx + 100, hy + 160, 34, T)
    if give:
        u = ease_in_out(clamp01((T - tb(3, k3_sheet)) / 0.5))
        sx, sy = lerp(wx + 170, cx, u), lerp(hy + 30, cy - 120, u)
        s_ = lerp(0.4, 1.0, u)
        with K.at(c, sx, sy, lerp(-10, 0, u), s_):
            a3_sheet(c, 0, 0, 520, 340)
            for side in (-1, 1):
                for r in range(3):
                    C.line(c, (side * 230, -40 + r * 50), (side * 40, -40 + r * 50), GRAY, 5)
            if T >= tb(3, k3_ring):
                f = clamp01((T - tb(3, k3_ring)) / 0.4)
                ring = skia.Path()
                ring.addArc(skia.Rect.MakeXYWH(40, -70, 210, 120), -100, 350 * f)
                c.drawPath(ring, wb.marker(RED, 10))
    return None


ev(j, k3_wang, scene3, "wood_low", 0.7)
b.hit(j, k3_sheet, "wood_high", 0.75, "递上一张纸")
b.hit(j, k3_boss, "pop", 0.7, "领导接过来")
b.hit(j, k3_ring, "rim", 0.8, "画了个圈")
ev(j, k3_say, L.pop_bubble("这里，展开说说", cx + 220, cy + 120, j, k3_say, 56, BLACK, tail=1), "pop", 0.75)

# ================================================================ 屏 4：小王那张纸放大，角上“A3”；两张打印纸拼起来正好一样大
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k4_big, k4_a3, k4_name, k4_two, k4_eq = seq(j, [None, (6, 1, 0.3), (6, 1, 0.8), (7, 3, 0.2), (7, 3, 0.8)])
SX4, SY4, SW4, SH4 = cx - 120, cy - 120, 640, 450
L.note("A3", "A4", "一页纸报告", "一样大")


def big4(c, T, cx=cx, cy=cy):
    a3_sheet(c, SX4, SY4, SW4, SH4)
    for side in (-1, 1):
        for r in range(4):
            C.line(c, (SX4 + side * 280, SY4 - 60 + r * 55), (SX4 + side * 50, SY4 - 60 + r * 55), GRAY, 5)
    hy = cy + 520 - 290 * 0.8
    draw_wang(c, cx + 400, cy + 520, 0.8, mood="smile", lh=(cx + 300, hy + 40))


pop(j, k4_big, SX4, SY4, big4, "wood_low", 0.75)
ev(j, k4_a3, L.stamp("A3", SX4 + SW4 / 2 + 20, SY4 + SH4 / 2 + 20, 60, j, k4_a3, BLUE, rot=10), "rim", 0.8)
ev(j, k4_name, L.slam_text("一页纸报告", cx, cy - 480, 100, RED, j, k4_name), "kick", 0.85)


def two4(c, kk, T, cx=cx, cy=cy):
    t0 = tb(4, k4_two)
    if T < t0:
        return None
    u = ease_in_out(clamp01((T - tb(4, k4_eq)) / 0.5)) if T >= tb(4, k4_eq) else 0.0
    for n in range(2):
        g = pop_scale(T - t0 - n * 0.12)
        if g <= 0:
            continue
        x0, y0 = cx - 300 + n * 330, cy + 370
        x1 = SX4 - SW4 / 4 + n * SW4 / 2
        x, y = lerp(x0, x1, u), lerp(y0, SY4, u)
        w, h = lerp(300, SW4 / 2, u), lerp(210, SH4, u)
        with K.at(c, x, y, 0, g):
            dashed_rect(c, 0, 0, w, h, BLUE, 6, 1.0, 8)
            K.text(c, "A4", 0, 0, 60, "hand", BLUE, 1 - 0.6 * u)
    if u >= 1:
        sparkle(c, SX4, SY4, T - tb(4, k4_eq) - 0.5, BLUE, 10, 200, 360)
    return None


ev(j, k4_two, two4, "pop", 0.75)
b.hit(j, k4_eq, "ding", 0.8, "两张拼起来正好一样大")

# ================================================================ 屏 5：纸的左半边逐格写出：出了什么问题 → 现在什么样 → 想做到什么样
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k5_sheet, k5_c1, k5_c2, k5_c3 = seq(j, [None, (8, 1, 0.5), (8, 2, 0.4), (8, 3, 0.4)])
SX5, SY5 = cx, cy - 20
CELLS_L = ["出了什么问题", "现在什么样", "想做到什么样"]
L.note(*CELLS_L)


def sheet5(c, T, cx=cx, cy=cy):
    a3_sheet(c, SX5, SY5, 1000, 860)
    for r in range(3):
        dashed_rect(c, SX5 - 250, SY5 - 170 + r * 235, 450, 190, GRAY, 4)
        dashed_rect(c, SX5 + 250, SY5 - 170 + r * 235, 450, 190, GRAY, 4)


pop(j, k5_sheet, SX5, SY5, sheet5, "wood_low", 0.75)
for n, k_ in enumerate((k5_c1, k5_c2, k5_c3)):
    y = SY5 - 170 + n * 235
    b.text(j, k_, k_ + 0.8, CELLS_L[n], SX5 - 250, y - 40, 52, BLACK, sfx=("wood_high", "wood_high", "bongo_high")[n], gain=0.75)


def arrows5(c, kk, T, cx=cx, cy=cy):
    for n, k_ in enumerate((k5_c2, k5_c3)):
        f = clamp01((T - tb(5, k_)) / 0.3)
        if f > 0:
            y0 = SY5 - 170 + n * 235 + 30
            C.line(c, (SX5 - 250, y0), (SX5 - 250, y0 + 80 * f), RED, 8)
            if f >= 1:
                C.line(c, (SX5 - 250, y0 + 80), (SX5 - 270, y0 + 56), RED, 8)
                C.line(c, (SX5 - 250, y0 + 80), (SX5 - 230, y0 + 56), RED, 8)
    for n, k_ in enumerate((k5_c1, k5_c2, k5_c3)):
        g = pop_scale(T - tb(5, k_) - 0.5)
        if g > 0:
            with K.at(c, SX5 - 250, SY5 - 170 + n * 235 + 30, 0, g):
                if n == 0:
                    K.text(c, "！", -150, 0, 70, "black", RED)
                elif n == 1:
                    for i in range(3):
                        c.drawRect(skia.Rect.MakeXYWH(-60 + i * 50, 10 - 20 * (i + 1), 34, 20 * (i + 1)), K.paint(BLUE))
                else:
                    c.drawCircle(0, 0, 36, wb.marker(GREEN, 7))
                    c.drawCircle(0, 0, 14, K.paint(GREEN))
    return None


ev(j, k5_c1, arrows5)

# ================================================================ 屏 6：右半边逐格写出：原因 → 怎么改 → 谁、什么时候；写不进去的字挤出来，打问号
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k6_sheet, k6_c1, k6_c2, k6_c3, k6_over, k6_q = seq(j, [None, (9, 0, 0.6), (9, 1, 0.5), (9, 2, 0.5), (10, 0, 0.5), (10, 1, 0.6)])
SX6, SY6 = cx - 40, cy - 60
CELLS_R = ["原因在哪", "打算怎么改", "谁 · 几号做完"]
L.note(*CELLS_L, *CELLS_R, "没想清楚")


def sheet6(c, T, cx=cx, cy=cy):
    a3_sheet(c, SX6, SY6, 960, 820)
    for r in range(3):
        y = SY6 - 170 + r * 225
        dashed_rect(c, SX6 - 240, y, 430, 185, GRAY, 4)
        K.text(c, CELLS_L[r], SX6 - 240, y - 40, 46, "hand", GRAY)
        dashed_rect(c, SX6 + 240, y, 430, 185, GRAY, 4)


pop(j, k6_sheet, SX6, SY6, sheet6, "wood_low", 0.75)
for n, k_ in enumerate((k6_c1, k6_c2, k6_c3)):
    y = SY6 - 170 + n * 225
    b.text(j, k_, k_ + 0.8, CELLS_R[n], SX6 + 240, y - 40, 50, GREEN, sfx=("wood_high", "wood_high", "bongo_high")[n], gain=0.75)


def over6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k6_over)
    if T < t0:
        return None
    words = ["还有", "另外", "补充", "再说"]
    for n, s_ in enumerate(words):
        f = ease_out(clamp01((T - t0 - n * 0.15) / 0.5))
        if f <= 0:
            continue
        x = lerp(SX6 + 400, SX6 + 470 + (n % 2) * 40, f)
        y = SY6 + 330 + n * 0 - 60 * n * f + 120
        with K.at(c, x, y - 120, (n - 1.5) * 12, f):
            box(c, 0, 0, 130, 60, "#FFFFFF", GRAY, 4, 8)
            K.text(c, s_, 0, 2, 40, "hand", GRAY)
    return None


L.note("还有", "另外", "补充", "再说")
ev(j, k6_over, over6, "shaker", 0.7)


def q6(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k6_q)
    if dt < 0:
        return None
    qmark(c, SX6 + 470, SY6 + 460, 110, dt, RED)
    g = C.slam_scale(dt)
    with K.at(c, cx - 200, cy + 470, -4, g):
        K.text(c, "没想清楚", 0, 0, 84, "hand", RED)
    return None


ev(j, k6_q, q6, "kick", 0.85)

# ================================================================ 屏 7：左：看的人在一堆页里拼图，问题和答案隔得老远；右：一张纸，一条箭头从问题直通办法
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k7_q, k7_pile, k7_find, k7_one, k7_arrow = seq(j, [None, (12, 0, 0.5), (12, 1, 0.6), (12, 2, 0.2), (12, 2, 0.8)])
L.note("为什么？", "问题在第3页", "答案在第27页", "一眼看完", "办法")
ev(j, k7_q, L.slam_text("为什么？", cx, cy - 510, 90, RED, j, k7_q), "rim", 0.8)


def divider7(c, T, cx=cx, cy=cy):
    C.line(c, (cx, cy - 420), (cx, cy + 560), GRAY, 6)
    K.text(c, "小李", cx - 300, cy - 400, 52, "hand", BLACK)
    K.text(c, "小王", cx + 300, cy - 400, 52, "hand", BLUE)


pop(j, k7_q, cx, cy, divider7)


def pile7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k7_pile))
    if sc <= 0:
        return None
    spots = [(-470, -260, -12), (-160, -300, 8), (-420, -60, 5), (-180, -110, -6), (-460, 140, 10), (-170, 120, -4)]
    with at_pop(c, cx - 300, cy - 50, sc):
        for n, (dx, dy, r) in enumerate(spots):
            slide(c, cx + dx + 10, cy + dy, 220, 140, n, rot=r)
        if T >= tb(7, k7_find):
            g = pop_scale(T - tb(7, k7_find))
            with K.at(c, cx - 450, cy - 260, 0, g):
                box(c, 0, 0, 240, 64, RED_FILL, RED, 5, 10)
                K.text(c, "问题在第3页", 0, 2, 34, "hand", RED)
            with K.at(c, cx - 180, cy + 210, 0, g):
                box(c, 0, 0, 260, 64, GREEN_FILL, GREEN, 5, 10)
                K.text(c, "答案在第27页", 0, 2, 34, "hand", GREEN)
            dashed(c, (cx - 450, cy - 225), (cx - 180, cy + 175), GRAY, 5)
        hy = cy + 520 - 290 * 0.75
        look = math.sin(T * 4) * 40
        draw_boss(c, cx - 300, cy + 520, 0.75, lh=(cx - 380, hy + 60 + look), rh=(cx - 220, hy + 60 - look), mood="sad")
        qmark(c, cx - 210, hy - 110, 80, T - tb(7, k7_pile) - 0.4, GRAY)
    return None


ev(j, k7_pile, pile7, "wood_low", 0.7)
b.hit(j, k7_find, "rim", 0.7, "问题和答案隔得老远")


def one7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k7_one))
    if sc <= 0:
        return None
    x, y = cx + 300, cy - 70
    with at_pop(c, x, y, sc):
        a3_sheet(c, x, y, 420, 300)
        if T >= tb(7, k7_arrow):
            f = clamp01((T - tb(7, k7_arrow)) / 0.4)
            C.line(c, (x - 110, y + 30), (x - 110 + 220 * f, y + 30), RED, 10)
            if f >= 1:
                C.line(c, (x + 110, y + 30), (x + 82, y + 8), RED, 10)
                C.line(c, (x + 110, y + 30), (x + 82, y + 52), RED, 10)
                K.text(c, "一眼看完", x, y + 220, 60, "hand", GREEN)
        hy = cy + 520 - 290 * 0.75
        draw_boss(c, x, cy + 520, 0.75, rh=(x + 60, hy + 40), mood="smile")
    return None


ev(j, k7_one, one7, "wood_high", 0.75)
b.hit(j, k7_arrow, "ding", 0.8, "箭头从问题直通办法")

# ================================================================ 屏 8：小王拿着笔对着一张纸想，头顶的乱线团慢慢理成一根直线
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k8_w, k8_sq, k8_tan, k8_straight, k8_bulb = seq(j, [None, (13, 1, 0.4), (14, 0, 0.6), (14, 1, 0.6), (14, 2, 0.6)])
L.note("挤进一张纸", "想明白")


def wang8(c, T, cx=cx, cy=cy):
    x, y = cx - 260, cy + 500
    hy = y - 290 * 0.95
    wr = 10 * math.sin(T * 9) if T >= tb(8, k8_straight) else 0
    desk(c, cx + 60, cy + 270, 560)
    a3_sheet(c, cx + 120, cy + 220, 300, 90, label=False)
    draw_wang(c, x, y, 0.95, mood="smile" if T >= tb(8, k8_bulb) else "flat", rh=(cx - 20, cy + 220 + wr))
    pen(c, cx - 10, cy + 230 + wr, -30, 0.8)


pop(j, k8_w, cx - 260, cy + 500, wang8, "wood_low", 0.7)


def squeeze8(c, kk, T, cx=cx, cy=cy):
    t0 = tb(8, k8_sq)
    if T < t0:
        return None
    f = ease_in_out(clamp01((T - t0) / 0.8))
    x, y = cx + 280, cy - 10
    for n in range(5):
        dy = lerp(-200 - n * 60, -20, f)
        with K.at(c, x + (n - 2) * 30 * (1 - f), y + dy, (n - 2) * 8 * (1 - f), lerp(0.9, 0.3, f)):
            box(c, 0, 0, 200, 70, "#FFFFFF", GRAY, 4, 8)
    K.text(c, "挤进一张纸", x, y + 120, 50, "hand", BLUE, clamp01((T - t0) / 0.3))
    return None


ev(j, k8_sq, squeeze8, "shaker", 0.7)


def tangle8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k8_tan))
    if sc <= 0:
        return None
    f = ease_in_out(clamp01((T - tb(8, k8_straight)) / 0.8)) if T >= tb(8, k8_straight) else 0.0
    x, y = cx - 230, cy - 330
    with at_pop(c, x, y, sc):
        tangle(c, x, y, 150, f)
    return None


ev(j, k8_tan, tangle8, "wood_high", 0.7)
b.hit(j, k8_straight, "shaker", 0.7, "线团理直")


def bulb8(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k8_bulb)
    if dt < 0:
        return None
    g = pop_scale(dt)
    with K.at(c, cx + 300, cy - 400, 0, g):
        c.drawPath(C.bulb_path(0, 0, 50), K.paint(NOTE_FILL))
        c.drawPath(C.bulb_path(0, 0, 50), wb.marker(ORANGE, 7))
    with K.at(c, cx + 300, cy - 260, 0, g):
        K.text(c, "想明白", 0, 0, 64, "hand", GREEN)
    return None


ev(j, k8_bulb, bulb8, "ding", 0.8)

# ================================================================ 屏 9：周报一行行“周一…周二…”，重点被埋在中间，放大镜找不到
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k9_doc, k9_rows, k9_mag, k9_lost = seq(j, [None, (16, 1, 0.3), (16, 2, 0.2), (16, 2, 0.8)])
DAYS9 = ["周一：开会", "周二：改表", "周三：开会", "周四：对数", "周五：开会"]
L.note("周报", *DAYS9, "重点", "找不到")


def doc9(c, T, cx=cx, cy=cy):
    box(c, cx - 80, cy, 700, 940, "#FFFFFF", BLACK, 7, 10)
    K.text(c, "周报", cx - 80, cy - 400, 66, "hand", BLACK)


pop(j, k9_doc, cx - 80, cy, doc9, "wood_low", 0.7)


def rows9(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k9_rows)
    n = int(clamp01((T - t0) / 1.2) * 4.999)
    for r in range(n + 1):
        y = cy - 280 + r * 130
        K.text(c, DAYS9[r], cx - 300, y, 50, "hand", GRAY, align="left")
        C.line(c, (cx - 300, y + 45), (cx + 220 - (r % 2) * 80, y + 45), GRAY_FILL, 6)
        if r == 2:
            K.text(c, "重点", cx + 130, y, 34, "hand", "#B9BEC6")
    return None


ev(j, k9_rows, rows9, "shaker", 0.7)


def mag9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k9_mag))
    if sc <= 0:
        return None
    u = (T - tb(9, k9_mag)) * 1.6
    x, y = cx + 160 + 160 * math.sin(u), cy - 60 + 230 * math.sin(u * 0.7 + 1)
    with at_pop(c, x, y, sc):
        magnifier(c, x, y, 90)
    hy = cy + 540 - 290 * 0.7
    draw_li(c, cx + 380, cy + 540, 0.7, "sad", rh=(x + 60, y + 80))
    return None


ev(j, k9_mag, mag9, "wood_high", 0.7)
ev(j, k9_lost, L.stamp("找不到", cx + 300, cy - 440, 66, j, k9_lost, rot=8), "rim", 0.8)

# ================================================================ 屏 10：聊天窗口里三大段铺垫，正事在最底下一行，红圈
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k10_win, k10_p1, k10_p2, k10_p3, k10_ring = seq(j, [None, (17, 1, 0.1), (17, 1, 0.5), (17, 1, 0.9), (17, 2, 0.6)])
L.note("领导", "能请两天假吗？", "最后一行")


def win10(c, T, cx=cx, cy=cy):
    phone(c, cx - 40, cy + 20, 720, 1060)
    c.drawRect(skia.Rect.MakeXYWH(cx - 387, cy - 480, 694, 70), K.paint(BLUE_FILL))
    K.text(c, "领导", cx - 40, cy - 445, 44, "hand", BLUE)

pop(j, k10_win, cx - 40, cy + 20, win10, "wood_low", 0.7)
for n, k_ in enumerate((k10_p1, k10_p2, k10_p3)):
    def para(c, T, n=n, cx=cx, cy=cy):
        y = cy - 300 + n * 230
        box(c, cx + 20, y, 560, 190, "#FFFFFF", GRAY, 4, 22)
        for r in range(4):
            C.line(c, (cx - 230, y - 60 + r * 40), (cx + 270 - (r == 3) * 160, y - 60 + r * 40), GRAY, 6)
    pop(j, k_, cx + 20, cy - 300 + n * 230, para, "pop", 0.65)


def last10(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(10, k10_ring)
    if dt < 0:
        return None
    y = cy + 420
    g = pop_scale(dt)
    with K.at(c, cx + 60, y, 0, g):
        box(c, 0, 0, 440, 80, GREEN_FILL, GREEN, 4, 22)
        K.text(c, "能请两天假吗？", 0, 2, 44, "hand", BLACK)
    f = clamp01((dt - 0.15) / 0.4)
    if f > 0:
        ring = skia.Path()
        ring.addArc(skia.Rect.MakeXYWH(cx - 190, y - 70, 500, 140), -100, 350 * f)
        c.drawPath(ring, wb.marker(RED, 10))
        K.text(c, "最后一行", cx - 290, y - 100, 46, "hand", RED, f)
    return None


ev(j, k10_ring, last10, "rim", 0.85)

# ================================================================ 屏 11：饭桌上小李讲了一晚上，爸妈头顶三个问号
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k11_tab, k11_moon, k11_q1, k11_q2 = seq(j, [None, (18, 1, 0.5), (18, 2, 0.2), (18, 2, 0.7)])
L.note("换工作")


def table11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k11_tab))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 300, sc):
        draw_mom(c, cx + 180, cy + 420, 0.8, mood="flat")
        draw_dad(c, cx + 420, cy + 420, 0.8, mood="flat")
        hy = cy + 420 - 290 * 0.85
        talk = math.sin(T * 9) * 40
        draw_li(c, cx - 330, cy + 420, 0.85, "smile", rh=(cx - 220, hy + 40 + talk), lh=(cx - 420, hy + 60 - talk))
        c.drawRoundRect(skia.Rect.MakeXYWH(cx - 520, cy + 260, 1040, 40), 10, 10, K.paint(WOOD))
        c.drawRoundRect(skia.Rect.MakeXYWH(cx - 520, cy + 260, 1040, 40), 10, 10, wb.marker(WOOD_LINE, 6))
        for x in (cx - 150, cx + 300):
            c.drawOval(skia.Rect.MakeXYWH(x - 70, cy + 230, 140, 40), K.paint("#FFFFFF"))
            c.drawOval(skia.Rect.MakeXYWH(x - 70, cy + 230, 140, 40), wb.marker(BLACK, 5))
        if math.sin(T * 9) > -0.3:
            bubble_text(c, "换工作…", cx - 230, cy - 120, 56, BLACK, -1)
    return None


L.note("换工作…")
ev(j, k11_tab, table11, "wood_low", 0.7)


def moon11(c, kk, T, cx=cx, cy=cy):
    t0 = tb(11, k11_moon)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    y = cy - 430 + 40 * math.sin(clamp01((T - t0) / 3) * math.pi)
    x = lerp(cx - 400, cx + 400, clamp01((T - t0) / 3))
    with at_pop(c, x, y, sc):
        moon(c, x, y, 55)
    return None


ev(j, k11_moon, moon11, "pop", 0.6)


def qs11(c, kk, T, cx=cx, cy=cy):
    for n, (x, y, k_) in enumerate(((cx + 180, cy - 80, k11_q1), (cx + 420, cy - 80, k11_q1), (cx + 300, cy - 230, k11_q2))):
        qmark(c, x, y, 90 + 30 * n, T - tb(11, k_) - n * 0.1, RED)
    return None


ev(j, k11_q1, qs11, "bongo_high", 0.75)
b.hit(j, k11_q2, "bongo_low", 0.8, "第三个问号更大")

# ================================================================ 屏 12：小李抱着厚报告怕被说偷懒；领导的表在走；大字“三步”
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k12_li, k12_fear, k12_boss, k12_short, k12_3 = seq(j, [None, (19, 1, 0.5), (20, 0, 0.5), (20, 2, 0.4), (21, 1, 0.5)])
L.note("没下功夫？", "替他着想", "三步")


def li12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k12_li))
    if sc <= 0:
        return None
    x, y = cx - 300, cy + 520
    hy = y - 290 * 0.85
    short = T >= tb(12, k12_short)
    u = ease_in_out(clamp01((T - tb(12, k12_short)) / 0.5)) if short else 0.0
    with at_pop(c, x, y, sc):
        n = int(lerp(16, 1, u))
        stack(c, x, hy + 130, n, 240, 140, 13)
        draw_li(c, x, y, 0.85, "smile" if short else "sad", lh=(x - 110, hy + 140), rh=(x + 110, hy + 140))
        if T >= tb(12, k12_fear) and not short:
            bubble_text(c, "没下功夫？", x + 40, hy - 330, 54, GRAY, -1)
            sweat(c, x + 60, hy - 20 + 6 * math.sin(T * 6))
    return None


ev(j, k12_li, li12, "wood_low", 0.7)
b.hit(j, k12_fear, "pop", 0.7, "怕被说没下功夫")


def boss12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k12_boss))
    if sc <= 0:
        return None
    x, y = cx + 330, cy + 520
    hy = y - 290 * 0.85
    with at_pop(c, x, y, sc):
        draw_boss(c, x, y, 0.85, rh=(x - 30, hy + 60), mood="smile" if T >= tb(12, k12_short) else "flat")
        watch(c, x + 20, cy - 70, 90, T * 4)
    if T >= tb(12, k12_short):
        g = pop_scale(T - tb(12, k12_short))
        with K.at(c, cx + 10, cy - 260, 0, g):
            heart(c, -170, 0, 40)
            K.text(c, "替他着想", 40, 0, 56, "hand", RED)
    return None


ev(j, k12_boss, boss12, "wood_high", 0.7)
b.hit(j, k12_short, "shaker", 0.75, "一摞压成一页")
ev(j, k12_3, L.slam_text("三步", cx, cy - 470, 160, RED, j, k12_3, rot=-4), "kick", 0.9)
b.shots[j].shake = [(k12_3, 9.0)]

# ================================================================ 屏 13：做法一——纸的最上面一行亮起“结论”
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k13_n, k13_pg, k13_top, k13_li = seq(j, [None, (22, 0, 0.5), (22, 1, 0.3), (22, 1, 0.8)])
L.note("第一", "结论", "一句话")
pop(j, k13_n, cx - 380, cy - 480, lambda c, T, cx=cx, cy=cy: K.text(c, "第一", cx - 440, cy - 480, 90, "hand", RED), "rim", 0.8)


def page13(c, T, cx=cx, cy=cy):
    box(c, cx + 20, cy - 20, 640, 880, "#FFFFFF", BLACK, 7, 10)
    for r in range(8):
        C.line(c, (cx - 240, cy - 180 + r * 70), (cx + 280 - (r % 3) * 80, cy - 180 + r * 70), GRAY_FILL, 7)


pop(j, k13_pg, cx, cy - 20, page13, "wood_low", 0.7)


def top13(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(13, k13_top)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.4))
    c.drawRoundRect(skia.Rect.MakeXYWH(cx - 270, cy - 400, 580 * f, 130), 16, 16, K.paint(NOTE_FILL))
    c.drawRoundRect(skia.Rect.MakeXYWH(cx - 270, cy - 400, 580 * f, 130), 16, 16, wb.marker(ORANGE, 6))
    if f >= 1:
        K.text(c, "结论", cx - 180, cy - 333, 70, "hand", RED)
        K.text(c, "一句话", cx + 100, cy - 333, 52, "hand", GRAY)
        sparkle(c, cx + 300, cy - 400, dt - 0.4, YELLOW)
    return None


ev(j, k13_top, top13, "ding", 0.8)


def li13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k13_li))
    if sc <= 0:
        return None
    x, y = cx + 440, cy + 540
    hy = y - 290 * 0.75
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.75, "smile", lh=(x - 110, hy + 30))
    return None


ev(j, k13_li, li13, "pop", 0.7)

# ================================================================ 屏 14：做法二——四格：问题、原因、办法、谁来做；写满最后一格，笔停住
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k14_n, k14_c1, k14_c2, k14_c3, k14_c4, k14_stop = seq(j, [None, (23, 0, 0.6), (23, 0, 0.95), (23, 1, 0.3), (23, 1, 0.7),
                                                          (23, 2, 0.6)])
FOUR = ["问题", "原因", "办法", "谁来做"]
L.note("第二", *FOUR, "停")
pop(j, k14_n, cx - 380, cy - 480, lambda c, T, cx=cx, cy=cy: (K.text(c, "第二", cx - 380, cy - 480, 90, "hand", RED),
                                                             box(c, cx, cy + 10, 900, 760, "#FFFFFF", BLACK, 7, 10)),
    "rim", 0.8)
CELL14 = [(cx - 220, cy - 170), (cx + 220, cy - 170), (cx - 220, cy + 190), (cx + 220, cy + 190)]
for n, k_ in enumerate((k14_c1, k14_c2, k14_c3, k14_c4)):
    x, y = CELL14[n]
    b.path(j, k_, k_ + 0.4, rect(x, y, 400, 320, 16), BLUE, 6, sfx=("wood_high", "wood_high", "wood_high", "bongo_high")[n],
           gain=0.7)
    b.text(j, k_ + 0.2, k_ + 0.8, FOUR[n], x, y - 100, 56, BLUE)


def fill14(c, kk, T, cx=cx, cy=cy):
    for n, k_ in enumerate((k14_c1, k14_c2, k14_c3, k14_c4)):
        x, y = CELL14[n]
        f = clamp01((T - tb(14, k_) - 0.5) / 0.6)
        for r in range(3):
            g = clamp01(f * 3 - r)
            if g > 0:
                C.line(c, (x - 150, y - 20 + r * 50), (x - 150 + 300 * g, y - 20 + r * 50), GRAY, 6)
    dt = T - tb(14, k14_stop)
    x, y = CELL14[3]
    if dt < 0:
        pen(c, x + 160, y + 90 + 6 * math.sin(T * 14), -30, 0.9)
    else:
        pen(c, x + 160, y + 90, -30, 0.9)
        with K.at(c, cx + 410, cy + 440, 0, C.slam_scale(dt)):
            K.text(c, "停", 0, 0, 110, "hand", RED)
    return None


ev(j, k14_c1, fill14)
b.hit(j, k14_stop, "kick", 0.85, "写满一页，笔停住")

# ================================================================ 屏 15：做法三——数据和截图装进“附件”文件夹；领导一问，小李抽出一张
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k15_n, k15_fold, k15_in, k15_ask, k15_pull = seq(j, [None, (24, 0, 0.6), (24, 1, 0.5), (24, 2, 0.3), (24, 2, 0.8)])
L.note("第三", "附件", "这个数呢？")
pop(j, k15_n, cx - 380, cy - 480, lambda c, T, cx=cx, cy=cy: K.text(c, "第三", cx - 380, cy - 480, 90, "hand", RED), "rim", 0.8)
FX15, FY15 = cx - 150, cy - 120
pop(j, k15_fold, FX15, FY15, lambda c, T, cx=cx, cy=cy: folder(c, FX15, FY15, 420, 300, "附件"), "wood_low", 0.7)


def into15(c, kk, T, cx=cx, cy=cy):
    t0 = tb(15, k15_in)
    if T < t0:
        return None
    for n in range(4):
        u = ease_in_out(clamp01((T - t0 - n * 0.12) / 0.4))
        if u >= 1:
            continue
        x0, y0 = cx + 300 + (n % 2) * 120, cy - 420 + n * 60
        slide(c, lerp(x0, FX15, u), lerp(y0, FY15, u), lerp(200, 120, u), lerp(130, 80, u), n, 1 - u * 0.7)
    return None


ev(j, k15_in, into15, "shaker", 0.7)


def ask15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k15_ask))
    if sc <= 0:
        return None
    x, y = cx + 350, cy + 520
    hy = y - 290 * 0.85
    with at_pop(c, x, y, sc):
        draw_boss(c, x, y, 0.85, mood="flat", lh=(x - 100, hy + 20))
        bubble_text(c, "这个数呢？", x - 60, hy - 140, 52, BLACK, 1)
    lx = cx - 330
    pulled = T >= tb(15, k15_pull)
    u = ease_out(clamp01((T - tb(15, k15_pull)) / 0.4)) if pulled else 0.0
    draw_li(c, lx, y, 0.85, "smile", rh=(lerp(FX15, cx + 40, u), lerp(FY15 + 60, hy + 40, u)))
    if pulled:
        slide(c, lerp(FX15, cx + 60, u), lerp(FY15, hy + 20, u), lerp(120, 220, u), lerp(80, 140, u), 1)
    return None


ev(j, k15_ask, ask15, "pop", 0.7)
b.hit(j, k15_pull, "wood_high", 0.8, "抽出一张")

# ================================================================ 屏 16：领导对着那张纸点头，在小李名字旁画一个勾
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
k16_sheet, k16_boss, k16_tick, k16_word = seq(j, [None, (25, 1, 0.3), (25, 2, 0.2), (25, 2, 0.8)])
L.note("小李", "靠谱")


def sheet16(c, T, cx=cx, cy=cy):
    a3_sheet(c, cx - 150, cy - 180, 600, 420)
    for side in (-1, 1):
        for r in range(3):
            C.line(c, (cx - 150 + side * 260, cy - 200 + r * 55), (cx - 150 + side * 40, cy - 200 + r * 55), GRAY, 5)
    box(c, cx - 150, cy + 80, 260, 70, "#FFFFFF", BLACK, 4, 10)
    K.text(c, "小李", cx - 150, cy + 82, 46, "hand", BLACK)


pop(j, k16_sheet, cx - 150, cy - 180, sheet16, "wood_low", 0.7)


def boss16(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(16, k16_boss))
    if sc <= 0:
        return None
    x, y = cx + 330, cy + 520
    hy = y - 290 * 0.9
    nod = 8 * abs(math.sin((T - tb(16, k16_boss)) * 5))
    with at_pop(c, x, y, sc):
        tk = T >= tb(16, k16_tick)
        draw_boss(c, x, y, 0.9, lh=(x - 120, hy + 60) if tk else None, mood="smile", head_dy=nod)
    if T >= tb(16, k16_tick):
        tick(c, cx + 20, cy + 70, 50, clamp01((T - tb(16, k16_tick)) / 0.3))
    hy2 = cy + 520 - 290 * 0.8
    draw_li(c, cx - 380, cy + 520, 0.8, "smile" if T >= tb(16, k16_tick) else "flat")
    return None


ev(j, k16_boss, boss16, "pop", 0.7)
b.hit(j, k16_tick, "ding", 0.85, "名字旁画勾")
ev(j, k16_word, L.slam_text("靠谱", cx - 380, cy - 470, 110, GREEN, j, k16_word, rot=-5), "kick", 0.85)

# ================================================================ 屏 17：评论区报页数；一大摞纸压成一张，亮起一颗心；下一讲预告
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
k17_cb, k17_g, k17_stack, k17_press, k17_heart, k17_nx = seq(j, [None, (27, 0, 0.4), (28, 0, 0.3), (28, 2, 0.3), (28, 2, 0.8), (29, 0, 0.2)])
GRIPES = [("45页", cx - 330, cy - 420), ("80页！", cx + 180, cy - 420), ("120页", cx - 70, cy - 320)]
L.note("最长一份有多少页？", *[g[0] for g in GRIPES], "下一讲", "新人教了三遍", "怎么还是不会？")


def cb17(c, T, cx=cx, cy=cy):
    comment_box(c, cx, cy - 400, 1040, 330)
    K.text(c, "最长一份有多少页？", cx - 100, cy - 520, 52, "hand", RED)


pop(j, k17_cb, cx, cy - 400, cb17, "wood_high", 0.7)
for n, (s_, x, y) in enumerate(GRIPES):
    ev(j, k17_g, L.pop_text(s_, x, y, 60, BLACK, j, k17_g + 0.15 * n), "pop" if n == 0 else None, 0.6)


def press17(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(17, k17_stack))
    if sc <= 0:
        return None
    x, y = cx - 250, cy + 130
    u = ease_in_out(clamp01((T - tb(17, k17_press)) / 0.4)) if T >= tb(17, k17_press) else 0.0
    with at_pop(c, x, y, sc):
        n = int(lerp(14, 1, u))
        stack(c, x, y, n, 280, 160, 12)
        if u >= 1:
            g = pop_scale(T - tb(17, k17_heart))
            with K.at(c, x, y - 60, 0, g * (1 + 0.06 * math.sin(T * 6))):
                heart(c, 0, 0, 55)
    return None


ev(j, k17_stack, press17, "wood_low", 0.7)
b.hit(j, k17_press, "kick", 0.8, "一摞压成一张")
b.hit(j, k17_heart, "ding", 0.8, "亮起一颗心")


def next17(c, kk, T, cx=cx, cy=cy):
    t0 = tb(17, k17_nx)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 420, sc):
        box(c, cx, cy + 420, 1000, 300, "#FFFFFF", BLUE, 8, 24)
        K.text(c, "下一讲", cx + 120, cy + 320, 48, "hand", BLUE)
        K.text(c, "新人教了三遍", cx + 120, cy + 410, 62, "hand", BLACK)
        K.text(c, "怎么还是不会？", cx + 120, cy + 500, 62, "hand", BLACK)
        draw_zhou(c, cx - 360, cy + 545, 0.5, mood="o")
        for n in range(3):
            qmark(c, cx - 420 + n * 60, cy + 330 - (n % 2) * 30, 50, T - t0 - 0.2 - n * 0.15, RED)
    return None


ev(j, k17_nx, next17, "wood_high", 0.75)

# ================================================================ 收尾
L.finish(cover_shot=3, square_shot=4, notes=NOTES)
L.export(globals())
