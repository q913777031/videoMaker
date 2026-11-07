"""《丰田模式》19 长期：眼前都顾不过来，还要想以后吗？（白板手绘 + AI 旁白，竖屏 2:3；系列收尾）

经典问答：三个问题一问一答。第 3 屏三张问号卡排成一排；之后每屏右上角一张“问答进度卡”（一问 / 二问 / 三问），
问到哪一张，哪一张翻开变亮；答完三问，卡片全亮。最后两屏收住整季：十九讲小卡排成几排，第一讲那张亮起；
小李回头，身后一条长路插满十九面小旗，他转身继续往前走，脚下的路一段段亮起来。
- 开场（alarm）：“考核”大闹钟追着小李跑，逐拍三步，第四拍远处路标“以后”一闪，“先顾眼前”；
- 日常：小李在跑，脚下日历一页页翻过；待办卡片一直排到天边，“一直没完”；
- 第一条原则（drop）：“最后一讲”；一本书翻开“第一条原则”亮起；天平左“眼前吃点亏”右“看长远”，drop 拍往右沉；
- 三个问题：三张问号卡排开，第一张翻开；
- 第一问：九十年代日历，一辆油电混合的车，旁边“卖得好吗？”；年份一格格往后走，车身亮起“招牌”；
- 第二问：一九五零年，工厂门口一排人离开、乌云；社长鞠躬放下“社长”帽子，之后员工手拉手站成一排；
- 第三问：小李停下，抬头看远处路标；心里亮起指南针，一堆事分成“拼”“放”；对照：没有指南针，每件事都闪红；
- 说回我们：糊弄老客户、下个季度椅子空了；半夜加班趴下，“机会”的门够不着；手机换成书和工具，三年后像换了个人；
  房租单、考核表、家里电话压在肩上，“三步”；三步做法；照样忙，脚下多了一条通向路标的路；
- 收尾：十九讲小卡排成几排，第一讲那张亮起，评论框；小李回头看十九面小旗，再往前走，路越走越亮。
小李 common.draw_li；车间员工 common.draw_worker（戴安全帽）；社长 common.draw_boss（深色西装，另戴“社长”帽）；
老客户为本讲小人（灰色礼帽、棕色外套）。
文案见 fengtian/PLAN.md「### 19」；时间轴、配乐、相机、人物见 fengtian/common.py，小工具见 fengtian/scenekit.py。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, draw_worker, pop_scale, wobble
from fengtian.scenekit import (GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL, NOTE_FILL, ORANGE_FILL, WOOD, WOOD_LINE,
                               Kit, at_pop, box, bubble_text, clock_face, comment_box, dashed, dashed_rect, desk,
                               heart, laptop, paper, phone, sparkle, sweat, tick, xmark)
from whiteboard import engine as wb
from whiteboard.engine import P

# 每屏：(旁白句序号, 页眉标签, 白板区块)；句子分组与 PLAN 的 SCREENS_DRAFT 一致
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "丰田模式 · 书中做法", 2),
    ([4], "三个问题", 3),
    ([5, 6], "第一问 · 不赚钱的事", 4),
    ([7], "第一问 · 不赚钱的事", 5),
    ([8, 9], "第二问 · 日子难的时候", 6),
    ([10, 11], "第二问 · 日子难的时候", 7),
    ([12, 13], "第三问 · 打工人", 8),
    ([14, 15], "为什么看远更稳", 9),
    ([16, 17], "说回我们自己", 10),
    ([18], "说回我们自己", 11),
    ([19], "说回我们自己", 12),
    ([20, 21], "说回我们自己", 13),
    ([22], "做法一 · 示意", 14),
    ([23], "做法二 · 示意", 15),
    ([24], "做法三 · 示意", 16),
    ([25], "知道往哪走", 17),
    ([26, 27, 28], "系列收尾", 18),
    ([29], "系列收尾", 19),
]

THEME = FT.get("19")          # 本讲样式：晨粉点阵、开场 alarm、转场 pan
L = C.Lesson("19", SCREENS, drop_screen=2, board_size=(5000, 12800), theme=THEME)
b = L.b
tb, wt = L.tb, L.wt
KT = Kit(L)
kq, nx, ev, pop, seq = KT.kq, KT.nx, KT.ev, KT.pop, KT.seq

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(18)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 1——管理决策以长期理念为基础，即使牺牲短期财务目标。",
    "油电混合车（普锐斯）上世纪九十年代开始做；一九五〇年丰田经营危机裁员、丰田喜一郎辞去社长，此后丰田重视留住员工"
    "（书中写法待核）。客户、加班、手艺为示意；小李、老客户为虚构人物。",
]

LESSONS = ["停线", "拉动", "均衡", "单件流", "标准化", "目视化", "现地现物", "五问", "共识", "反省", "浪费", "整理整顿",
           "防错", "快速换模", "一页纸", "教人", "合作伙伴", "可靠技术", "看长远"]
L.note(*LESSONS)


# ================================================================ 本讲道具

def label(c, s, x, y, size, color=BLACK, font="hand", alpha=1.0):
    K.text(c, s, x, y, size, font, color, alpha)


QN = ["一问", "二问", "三问"]
L.note(*QN)


def q_progress(c, x, y, n_open, glow_t=None):
    """右上角的问答进度卡：前 n_open 张翻开（绿），其余还是问号。"""
    box(c, x, y, 390, 110, "#FFFFFF", BLACK, 6, 16)
    for i in range(3):
        on = i < n_open
        xx = x - 125 + i * 125
        box(c, xx, y, 112, 80, GREEN_FILL if on else GRAY_FILL, GREEN if on else GRAY, 5, 12)
        label(c, QN[i] if on else "？", xx, y + 2, 40, GREEN if on else GRAY)
    if glow_t is not None and 0 <= glow_t < 0.8:
        sparkle(c, x - 125 + (n_open - 1) * 125, y, glow_t, YELLOW, 8, 40, 90)


def qp_fn(j, n_open, k_on):
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, 0))
        if sc <= 0:
            return None
        cx_, cy_ = R[j]
        lit = n_open if (k_on is None or T >= tb(j, k_on)) else n_open - 1
        with at_pop(c, cx_ + 340, cy_ - 490, sc):
            q_progress(c, cx_ + 340, cy_ - 490, lit, None if k_on is None else T - tb(j, k_on))
        return None
    return fn


def calendar_page(c, x, y, w, h, title, alpha=1.0, size=None):
    box(c, x, y, w, h, "#FFFFFF", BLACK, 6, 10, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h * 0.26), 10, 10, K.paint(RED, alpha))
    K.text(c, title, x, y + h * 0.12, size or h * 0.24, "hand", BLACK, alpha)


def car(c, x, y, s=1.0, color="#8FD19E", alpha=1.0):
    body = P((x - 150 * s, y - 30 * s), (x - 140 * s, y - 80 * s), (x - 70 * s, y - 88 * s), (x - 20 * s, y - 140 * s),
             (x + 70 * s, y - 140 * s), (x + 120 * s, y - 88 * s), (x + 150 * s, y - 76 * s), (x + 152 * s, y - 30 * s),
             close=True)
    c.drawPath(body, K.paint(color, alpha))
    c.drawPath(body, wb.marker(BLACK, 7, alpha))
    c.drawPath(P((x - 5 * s, y - 128 * s), (x + 62 * s, y - 128 * s), (x + 98 * s, y - 92 * s), (x - 5 * s, y - 92 * s),
                 close=True), K.paint("#FFFFFF", alpha))
    for dx in (-85, 85):
        c.drawCircle(x + dx * s, y - 26 * s, 30 * s, K.paint("#3B3F48", alpha))
        c.drawCircle(x + dx * s, y - 26 * s, 30 * s, wb.marker(BLACK, 6, alpha))


def leaf(c, x, y, r, alpha=1.0):
    p = skia.Path()
    p.moveTo(x - r, y + r)
    p.cubicTo(x - r, y - r * 0.6, x + r * 0.2, y - r, x + r, y - r)
    p.cubicTo(x + r, y + r * 0.2, x + r * 0.2, y + r, x - r, y + r)
    c.drawPath(p, K.paint(GREEN_FILL, alpha))
    c.drawPath(p, wb.marker(GREEN, 6, alpha))
    C.line(c, (x - r, y + r), (x + r * 0.4, y - r * 0.4), GREEN, 4, alpha)


def factory(c, x, y, w=300, h=200, fill="#FFFFFF", alpha=1.0):
    n = 3
    pts = [(x - w / 2, y), (x - w / 2, y - h * 0.6)]
    for i in range(n):
        x0 = x - w / 2 + i * w / n
        pts += [(x0 + w / n, y - h), (x0 + w / n, y - h * 0.6)]
    pts += [(x + w / 2, y)]
    c.drawRect(skia.Rect.MakeXYWH(x + w / 2 - 60, y - h * 1.25, 34, h * 0.65), K.paint(fill, alpha))
    c.drawRect(skia.Rect.MakeXYWH(x + w / 2 - 60, y - h * 1.25, 34, h * 0.65), wb.marker(BLACK, 6, alpha))
    body = P(*pts, close=True)
    c.drawPath(body, K.paint(fill, alpha))
    c.drawPath(body, wb.marker(BLACK, 7, alpha))


def cloud(c, x, y, s=1.0, color="#8A8F99", alpha=1.0):
    for dx, dy, r in ((-70, 10, 55), (0, -20, 70), (75, 10, 55), (20, 30, 50)):
        c.drawCircle(x + dx * s, y + dy * s, r * s, K.paint(color, alpha))


def road_sign(c, x, y, s, text, color=GREEN, alpha=1.0):
    """路标：(x, y) 为杆底。"""
    C.line(c, (x, y), (x, y - 260 * s), GRAY, 9, alpha)
    p = P((x - 90 * s, y - 360 * s), (x + 70 * s, y - 360 * s), (x + 110 * s, y - 310 * s), (x + 70 * s, y - 260 * s),
          (x - 90 * s, y - 260 * s), close=True)
    c.drawPath(p, K.paint("#FFFFFF", alpha))
    c.drawPath(p, wb.marker(color, 7, alpha))
    label(c, text, x, y - 310 * s, 56 * s, color, alpha=alpha)


def compass(c, x, y, r, rot, alpha=1.0):
    c.drawCircle(x, y, r, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, y, r, wb.marker(BLACK, 7, alpha))
    with K.at(c, x, y, rot):
        c.drawPath(P((0, -r * 0.8), (r * 0.16, 0), (-r * 0.16, 0), close=True), K.paint(RED, alpha))
        c.drawPath(P((0, r * 0.8), (r * 0.16, 0), (-r * 0.16, 0), close=True), K.paint(GRAY, alpha))
    c.drawCircle(x, y, r * 0.08, K.paint(BLACK, alpha))


def flag(c, x, y, n, h=150, color=None, alpha=1.0, wave=0.0):
    color = color or (RED, ORANGE, YELLOW, GREEN, BLUE)[n % 5]
    C.line(c, (x, y), (x, y - h), WOOD_LINE, 6, alpha)
    p = P((x, y - h), (x + h * 0.5, y - h * 0.86 + wave), (x, y - h * 0.7), close=True)
    c.drawPath(p, K.paint(color, alpha))
    c.drawPath(p, wb.marker(BLACK, 4, alpha))


def draw_client(c, x, y, s, lh=None, rh=None, mood="flat", alpha=1.0, back=False):
    """老客户：灰色礼帽、棕色外套。"""
    d_lh, d_rh = C.rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, ft, BLACK, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 46 * s, hy + 55 * s, x + 46 * s, y - 95 * s)
    c.drawRoundRect(torso, 16 * s, 16 * s, K.paint("#B07A4F", alpha))
    c.drawRoundRect(torso, 16 * s, 16 * s, wb.marker("#6B4226", 7, alpha))
    C.line(c, sh, lh, "#6B4226", 10, alpha)
    C.line(c, sh, rh, "#6B4226", 10, alpha)
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    if not back:
        C._eyes_mouth(c, x, hy + 4 * s, s, mood, alpha)
    c.drawRect(skia.Rect.MakeXYWH(x - 62 * s, hy - 44 * s, 124 * s, 12 * s), K.paint("#6B6B6B", alpha))
    c.drawRect(skia.Rect.MakeXYWH(x - 38 * s, hy - 100 * s, 76 * s, 60 * s), K.paint("#6B6B6B", alpha))


def point_at(path, f):
    pm = skia.PathMeasure(path, False)
    pos, _ = pm.getPosTan(pm.getLength() * clamp01(f))
    return pos


def chair(c, x, y, alpha=1.0):
    C.line(c, (x - 60, y - 120), (x + 60, y - 120), WOOD_LINE, 12, alpha)
    C.line(c, (x - 60, y - 120), (x - 60, y), WOOD_LINE, 9, alpha)
    C.line(c, (x + 60, y - 120), (x + 60, y), WOOD_LINE, 9, alpha)
    C.line(c, (x + 60, y - 120), (x + 60, y - 280), WOOD_LINE, 9, alpha)


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：小李在跑，脚下日历一页页翻；待办一直排到天边，“一直没完”
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k1_run, k1_cal, k1_todo, k1_lab = seq(j, [None, (1, 0, 0.5), (1, 1, 0.5), (1, 2, 0.5)])
L.note("待办", "一直没完")


def run1(c, T, cx=cx, cy=cy):
    gy = cy + 520
    C.line(c, (cx - 560, gy), (cx + 560, gy), GRAY, 6)
    t0 = tb(1, k1_run)
    ph = (T - t0) * 3.2
    bob = -abs(math.sin(ph * math.pi)) * 18
    x = cx - 280
    draw_li(c, x, gy + bob - 60, 0.85, "o", lh=(x - 80, gy - 300 + 30 * math.sin(ph * math.pi)),
            rh=(x + 80, gy - 300 - 30 * math.sin(ph * math.pi)))
    for i in range(3):
        C.line(c, (x - 110 - i * 30, gy - 300 + i * 50), (x - 170 - i * 30, gy - 300 + i * 50), GRAY, 6, 0.7)


pop(j, k1_run, cx - 280, cy + 300, run1, "tom", 0.8)


def cal1(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(1, k1_cal)
    if dt < 0:
        return None
    n = int(dt * 4)
    x, y = cx - 280, cy + 520
    for i in range(3):
        calendar_page(c, x - 30 + i * 30, y - 10 + i * 6, 170, 110, "又一年",
                      size=32)
    f = (dt * 4) % 1
    with K.at(c, x + 60, y - 10, -60 * f):
        calendar_page(c, 0, 0, 170, 110, "又一年", 1 - f, size=32)
    return None


ev(j, k1_cal, cal1, "shaker", 0.75)


def todo1(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(1, k1_todo)
    if dt < 0:
        return None
    for i in range(9):
        d = dt - 0.06 * i
        if d < 0:
            continue
        u = i / 8
        x = lerp(cx - 40, cx + 460, u)
        y = lerp(cy + 160, cy - 380, u)
        s = lerp(1.0, 0.35, u)
        with K.at(c, x, y, 0, pop_scale(d) * s):
            box(c, 0, 0, 220, 120, NOTE_FILL, ORANGE, 6, 10)
            for r in range(3):
                C.line(c, (-80, -30 + r * 30), (60 - (r % 2) * 40, -30 + r * 30), GRAY, 6)
    label(c, "待办", cx + 230, cy + 170, 54, ORANGE)
    return None


ev(j, k1_todo, todo1, "pop", 0.8)
ev(j, k1_lab, L.slam_text("一直没完", cx - 200, cy - 400, 110, RED, j, k1_lab, rot=-4), "kick", 0.85)
b.shots[j].shake = [(k1_lab, 7.0)]

# ================================================================ 屏 2（drop）：“最后一讲”；书翻到“第一条原则”；天平 drop 拍往“看长远”一边沉
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 14.0)], [(KD, 0.4)]
k2_last = 0
k2_book = min(max(kq(j, wt(2, 1, 0.4), 1), 1), KD - 2)
k2_scale = min(max(kq(j, wt(3, 0, 0.4), k2_book + 1), k2_book + 1), KD - 1)
L.note("最后一讲", "第一条原则", "眼前吃点亏", "看长远")
ev(j, k2_last, L.stamp("最后一讲", cx - 300, cy - 480, 64, j, k2_last, color=RED, rot=-6), "clap", 0.85)


def book2(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(2, k2_book)
    if dt < 0:
        return None
    x, y = cx + 180, cy - 330
    f = ease_out(clamp01(dt / 0.5))
    with K.at(c, x, y, 0, pop_scale(dt)):
        for sgn in (-1, 1):
            w = 220 * (f if sgn > 0 else 1)
            pg = P((0, -110), (sgn * w, -125), (sgn * w, 115), (0, 125), close=True)
            c.drawPath(pg, K.paint("#FFFFFF"))
            c.drawPath(pg, wb.marker(BLACK, 6))
        C.line(c, (0, -110), (0, 125), BLACK, 6)
        if f >= 1:
            label(c, "第一条", 110, -40, 46, BLACK)
            label(c, "原则", 110, 30, 46, BLACK)
            for r in range(4):
                C.line(c, (-180, -60 + r * 40), (-40, -60 + r * 40), GRAY, 5)
            if dt < 1.6:
                c.drawCircle(110, 0, 130, K.paint(YELLOW, 0.3 * (1 - (dt - 0.5) / 1.1), blur=20))
    return None


ev(j, k2_book, book2, "wood_high", 0.8)


def scale2(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(2, k2_scale)
    if dt < 0:
        return None
    tilt = 0.0
    if T >= tb(2, KD):
        d = T - tb(2, KD)
        tilt = 16 * ease_out(clamp01(d / 0.3)) + wobble(d, 3, 18, 5)
    x, y = cx, cy + 120
    with K.at(c, x, y + 200, 0, pop_scale(dt)):
        c.translate(-x, -(y + 200))
        C.line(c, (x, y), (x, y + 400), BLACK, 12)
        C.line(c, (x - 130, y + 400), (x + 130, y + 400), BLACK, 12)
        with K.at(c, x, y, tilt):
            C.line(c, (-420, 0), (420, 0), BLACK, 12)
            for sgn, s_, col in ((-1, "眼前吃点亏", ORANGE), (1, "看长远", GREEN)):
                px = sgn * 400
                with K.at(c, px, 0, -tilt):
                    C.line(c, (0, 0), (-100, 160), GRAY, 5)
                    C.line(c, (0, 0), (100, 160), GRAY, 5)
                    arc = skia.Path()
                    arc.addArc(skia.Rect.MakeXYWH(-130, 110, 260, 100), 0, 180)
                    c.drawPath(arc, K.paint(col, 0.4))
                    c.drawPath(arc, wb.marker(col, 7))
                    label(c, s_, 0, 280, 56 if sgn < 0 else 66, col)
        c.drawCircle(x, y, 18, K.paint(BLACK))
    return None


ev(j, k2_scale, scale2, "wood_low", 0.8)
b.hit(j, KD, "kick", 0.9, "天平往看长远一边沉")

# ================================================================ 屏 3：三张问号卡排成一排，第一张翻开
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k3_c1, k3_c2, k3_c3, k3_flip = seq(j, [(4, 0, 0.3), (4, 0, 0.6), (4, 0, 0.9), (4, 1, 0.5)])
L.note("一问一答", "第一问")
CARD_X = [cx - 360, cx, cx + 360]
for n, k_ in enumerate((k3_c1, k3_c2, k3_c3)):
    def qcard3(c, kk, T, n=n, k_=k_, cx=cx, cy=cy):
        dt = T - tb(3, k_)
        if dt < 0:
            return None
        x, y = CARD_X[n], cy - 120
        flip = 0.0
        if n == 0 and T >= tb(3, k3_flip):
            flip = clamp01((T - tb(3, k3_flip)) / 0.35)
        sx = abs(math.cos(math.pi * flip))
        with K.at(c, x, y, wobble(dt, 5, 14, 5), pop_scale(dt)):
            c.scale(max(0.02, sx), 1)
            if flip < 0.5:
                box(c, 0, 0, 290, 400, GRAY_FILL, BLACK, 8, 24)
                label(c, "？", 0, 0, 200, RED, "black")
            else:
                box(c, 0, 0, 290, 400, GREEN_FILL, GREEN, 8, 24)
                label(c, "第一问", 0, 0, 80, GREEN)
        return None
    ev(j, k_, qcard3, ("pop", "pop", "bongo_high")[n], 0.8)
b.hit(j, k3_flip, "clap", 0.85, "第一张翻开")


def li3(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(3, k3_c1)
    if dt < 0:
        return None
    gy = cy + 560
    hy = gy - 290 * 0.75
    draw_li(c, cx - 380, gy, 0.75, "smile", rh=(cx - 280, hy + 20))
    label(c, "一问一答", cx + 200, cy + 300, 80, BLACK)
    return None


ev(j, k3_c1, li3)

# ================================================================ 屏 4：第一问——九十年代日历；油电混合的车，旁边“卖得好吗？”
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k4_q, k4_cal, k4_car, k4_ask = seq(j, [(5, 0, 0.5), (6, 0, 0.5), (6, 1, 0.5), (6, 2, 0.6)])
L.note("不赚钱的事？", "九十年代", "油", "电", "卖得好吗？")
ev(j, 0, qp_fn(4, 1, None))
ev(j, k4_q, L.pop_text("不赚钱的事？", cx - 150, cy - 480, 70, RED, j, k4_q), "rim", 0.8)


def cal4(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(4, k4_cal)
    if dt < 0:
        return None
    with K.at(c, cx - 330, cy - 220, 0, pop_scale(dt)):
        calendar_page(c, 0, 0, 320, 220, "九十年代", size=56)
    return None


ev(j, k4_cal, cal4, "wood_high", 0.8)


def car4(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(4, k4_car)
    if dt < 0:
        return None
    gy = cy + 420
    with K.at(c, cx + 60, gy - 100, 0, pop_scale(dt)):
        c.translate(-(cx + 60), -(gy - 100))
        C.line(c, (cx - 540, gy), (cx + 540, gy), GRAY, 6)
        car(c, cx + 100, gy, 1.5)
        box(c, cx + 20, gy - 330, 90, 70, "#FFFFFF", ORANGE, 5, 10)
        label(c, "油", cx + 20, gy - 328, 40, ORANGE)
        box(c, cx + 180, gy - 330, 90, 70, "#FFFFFF", BLUE, 5, 10)
        label(c, "电", cx + 180, gy - 328, 40, BLUE)
        leaf(c, cx + 100, gy - 420, 34)
        hy = gy - 290 * 0.8
        draw_worker(c, cx - 330, gy, 0.8, mood="flat", rh=(cx - 220, hy + 60 + 8 * math.sin(T * 6)))
    return None


ev(j, k4_car, car4, "wood_low", 0.8)


def ask4(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(4, k4_ask)
    if dt < 0:
        return None
    with K.at(c, cx + 300, cy - 230, wobble(dt, 5, 14, 4), pop_scale(dt)):
        bubble_text(c, "卖得好吗？", 0, 0, 64, RED, -1)
    return None


ev(j, k4_ask, ask4, "bongo_low", 0.85)

# ================================================================ 屏 5：年份一格格往后走，车身亮起一块招牌
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k5_car, k5_y1, k5_y2, k5_sign = seq(j, [None, (7, 0, 0.4), (7, 0, 0.9), (7, 1, 0.6)])
L.note("一年年", "招牌")
ev(j, 0, qp_fn(5, 1, None))


def car5(c, T, cx=cx, cy=cy):
    gy = cy + 440
    C.line(c, (cx - 540, gy), (cx + 540, gy), GRAY, 6)
    car(c, cx, gy, 1.6)
    hy = gy - 290 * 0.75
    draw_worker(c, cx - 400, gy, 0.75, mood="smile", rh=(cx - 300, hy + 60 + 10 * math.sin(T * 7)))


pop(j, k5_car, cx, cy + 300, car5, "wood_low", 0.75)


def years5(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(5, k5_y1)
    if dt < 0:
        return None
    y = cy - 300
    n = 3 + (4 if T >= tb(5, k5_y2) else 0)
    C.line(c, (cx - 500, y), (cx - 500 + 1000 * min(1, n / 9), y), BLUE, 9)
    for i in range(n):
        d = T - tb(5, k5_y1 if i < 3 else k5_y2) - 0.06 * (i % 4)
        if d < 0:
            continue
        x = cx - 460 + i * 130
        with K.at(c, x, y, 0, pop_scale(d)):
            c.drawCircle(0, 0, 22, K.paint(BLUE))
    label(c, "一年年", cx - 360, y - 80, 56, BLUE)
    return None


ev(j, k5_y1, years5, "wood_high", 0.75)
b.hit(j, k5_y2, "wood_high", 0.8, "又走了几年")


def sign5(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(5, k5_sign)
    if dt < 0:
        return None
    gy = cy + 440
    with K.at(c, cx + 20, gy - 330, -3, C.slam_scale(dt)):
        box(c, 0, 0, 260, 110, YELLOW, ORANGE, 8, 18)
        label(c, "招牌", 0, 2, 72, RED)
    sparkle(c, cx + 20, gy - 330, dt, YELLOW, 10, 80, 220)
    return None


ev(j, k5_sign, sign5, "ding", 0.9)

# ================================================================ 屏 6：第二问——一九五零年，工厂门口一排人离开，天上乌云
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k6_flip, k6_cal, k6_fac, k6_leave = seq(j, [(8, 0, 0.5), (9, 0, 0.5), (9, 1, 0.5), (9, 2, 0.5)])
L.note("先保什么？", "一九五零年")
ev(j, k6_flip, qp_fn(6, 2, k6_flip), "clap", 0.8)
ev(j, k6_flip, L.pop_text("先保什么？", cx - 220, cy - 480, 70, RED, j, k6_flip))


def cal6(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k6_cal)
    if dt < 0:
        return None
    with K.at(c, cx - 360, cy - 250, 0, pop_scale(dt)):
        calendar_page(c, 0, 0, 320, 210, "一九五零年", size=50)
    return None


ev(j, k6_cal, cal6, "wood_high", 0.8)


def fac6(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k6_fac)
    if dt < 0:
        return None
    gy = cy + 470
    with K.at(c, cx + 150, gy - 150, 0, pop_scale(dt)):
        c.translate(-(cx + 150), -(gy - 150))
        C.line(c, (cx - 540, gy), (cx + 540, gy), GRAY, 6)
        factory(c, cx + 250, gy - 60, 520, 300, GRAY_FILL)
        c.drawRect(skia.Rect.MakeXYWH(cx + 120, gy - 250, 140, 190), K.paint("#3B3F48"))
        cloud(c, cx + 230 + 20 * math.sin(T * 0.8), cy - 280, 1.1)
        if dt > 0.3:
            for i in range(4):
                xx = cx + 330 + i * 60 + 20 * math.sin(T * 9 + i)
                C.line(c, (xx, cy - 180), (xx - 20, cy - 110), BLUE, 4, 0.7)
    return None


ev(j, k6_fac, fac6, "tom", 0.8)


def leave6(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k6_leave)
    if dt < 0:
        return None
    gy = cy + 470
    for n in range(3):
        x, dy, _ = C.walk(T, tb(6, k6_leave) + 0.2 * n, 2.0, cx + 120 - n * 10, cx - 200 - n * 160, 10, 2)
        with K.at(c, x, gy + dy, 0, pop_scale(dt - 0.2 * n)):
            draw_worker(c, 0, 0, 0.6, mood="sad")
    return None


ev(j, k6_leave, leave6, "bongo_low", 0.8)

# ================================================================ 屏 7：社长鞠躬，放下“社长”帽子；之后员工手拉手站成一排
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k7_boss, k7_bow, k7_hat, k7_row = seq(j, [None, (10, 1, 0.3), (10, 1, 0.8), (11, 1, 0.5)])
L.note("社长", "留住员工")
ev(j, 0, qp_fn(7, 2, None))


def boss7(c, T, cx=cx, cy=cy):
    gy = cy + 120
    bow = ease_out(clamp01((T - tb(7, k7_bow)) / 0.5)) if T >= tb(7, k7_bow) else 0.0
    hat_off = T >= tb(7, k7_hat)
    C.line(c, (cx - 540, gy), (cx + 200, gy), GRAY, 6)
    hy = gy - 290 * 0.85
    draw_boss(c, cx - 250, gy, 0.85, mood="sad" if bow > 0 else "flat", head_dy=36 * bow,
              lh=(cx - 300, hy + 150), rh=(cx - 200, hy + 150))
    if not hat_off:
        box(c, cx - 250, hy - 70 + 36 * bow, 170, 76, "#2B2B30", BLACK, 5, 6)
        label(c, "社长", cx - 250, hy - 70 + 36 * bow, 44, "#FFFFFF")
    if hat_off:
        f = ease_out(clamp01((T - tb(7, k7_hat)) / 0.5))
        x, y = lerp(cx - 250, cx + 30, f), lerp(hy - 34, gy - 160, f)
        desk(c, cx + 30, gy - 110, 260)
        box(c, x, y, 170, 76, "#2B2B30", BLACK, 5, 6)
        label(c, "社长", x, y, 44, "#FFFFFF")


pop(j, k7_boss, cx - 250, cy, boss7, "wood_low", 0.75)
b.hit(j, k7_bow, "tom", 0.75, "社长鞠躬")
b.hit(j, k7_hat, "wood_high", 0.8, "放下社长帽子")


def row7(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(7, k7_row)
    if dt < 0:
        return None
    gy = cy + 560
    s = 0.6
    xs = [cx - 420 + i * 210 for i in range(5)]
    hy = gy - 290 * s
    for n, x in enumerate(xs):
        g = pop_scale(dt - 0.08 * n)
        if g <= 0:
            continue
        with K.at(c, x, gy, 0, g):
            draw_worker(c, 0, 0, s, mood="smile", lh=(-105, -290 * s + 130 * s), rh=(105, -290 * s + 130 * s))
    if dt > 0.5:
        f = clamp01((dt - 0.5) / 0.3)
        for x in xs[:-1]:
            c.drawCircle(x + 105, hy + 130 * s, 12, K.paint("#F6D9C2", f))
        heart(c, cx + 300, cy - 120, 50)
        label(c, "留住员工", cx + 300, cy - 20, 60, RED, alpha=f)
    return None


ev(j, k7_row, row7, "clap", 0.85)

# ================================================================ 屏 8：第三问——小李停下脚步，抬头看远处的路标
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k8_flip, k8_stop, k8_sign, k8_ok = seq(j, [(12, 0, 0.5), (12, 1, 0.5), (13, 1, 0.5), (13, 2, 0.6)])
L.note("也要想吗？", "以后", "更稳")
ev(j, k8_flip, qp_fn(8, 3, k8_flip), "clap", 0.8)
ev(j, k8_flip, L.pop_text("也要想吗？", cx - 220, cy - 480, 70, RED, j, k8_flip))


def stop8(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k8_stop)
    if dt < 0:
        return None
    gy = cy + 520
    C.line(c, (cx - 560, gy), (cx + 560, gy), GRAY, 6)
    p = P((cx - 300, gy), (cx - 40, gy - 220), (cx + 200, gy - 330), (cx + 380, gy - 380))
    c.drawPath(p, wb.marker(GRAY, 6))
    x, dy, mv = C.walk(T, tb(8, k8_stop), 0.5, cx - 520, cx - 380, 14, 4)
    look = T >= tb(8, k8_sign)
    hy = gy - 290 * 0.85
    draw_li(c, x, gy + dy, 0.85, "smile" if look else "o", rh=(x + 40, hy - 10) if look else None)
    if look:
        C.line(c, (x + 40, hy - 10), (x + 70, hy - 20), BLACK, 8)
    return None


ev(j, k8_stop, stop8, "wood_low", 0.8)


def sign8(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k8_sign)
    if dt < 0:
        return None
    with K.at(c, cx + 330, cy + 140, 0, pop_scale(dt)):
        road_sign(c, 0, 0, 1.0, "以后")
    dashed(c, (cx - 250, cy + 220), (cx + 230, cy - 140), GREEN, 5, clamp01(dt / 0.3))
    return None


ev(j, k8_sign, sign8, "ding", 0.85)


def ok8(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k8_ok)
    if dt < 0:
        return None
    with K.at(c, cx - 60, cy - 260, -4, C.slam_scale(dt)):
        label(c, "更稳", 0, 0, 120, GREEN)
    return None


ev(j, k8_ok, ok8, "kick", 0.85)

# ================================================================ 屏 9：心里亮起指南针；一堆事分成“拼”“放”；对照：没有指南针，每件事都闪红
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k9_comp, k9_pile, k9_split, k9_bad = seq(j, [(14, 0, 0.5), (14, 1, 0.3), (14, 2, 0.3), (15, 1, 0.4)])
L.note("拼", "放", "方向", "急")


def comp9(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(9, k9_comp)
    if dt < 0:
        return None
    gy = cy + 40
    hy = gy - 290 * 0.8
    draw_li(c, cx - 400, gy, 0.8, "smile")
    with K.at(c, cx - 230, hy - 40, 0, pop_scale(dt)):
        heart(c, 0, 0, 90, GREEN, GREEN_FILL)
        compass(c, 0, -10, 52, wobble(dt, 40, 10, 3) + 20)
    C.line(c, (cx - 360, hy + 10), (cx - 300, hy - 20), GREEN, 5, clamp01(dt / 0.3))
    label(c, "方向", cx - 230, hy - 190, 60, GREEN, alpha=clamp01(dt / 0.3))
    return None


ev(j, k9_comp, comp9, "ding", 0.8)
TASKS9 = [(cx - 80 + (i % 3) * 120, cy - 200 + (i // 3) * 100) for i in range(6)]


def pile9(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(9, k9_pile)
    if dt < 0:
        return None
    f = ease_in_out(clamp01((T - tb(9, k9_split)) / 0.6)) if T >= tb(9, k9_split) else 0.0
    for i, (x, y) in enumerate(TASKS9):
        tgt = (cx + 130 + (i % 2) * 110, cy - 280 + (i // 2) * 90) if i % 2 == 0 else \
              (cx + 380 + (i % 2) * 0, cy - 280 + (i // 2) * 90)
        if i % 2 == 0:
            tgt = (cx + 80 + (i // 2) * 0, cy - 300 + (i // 2) * 100)
        else:
            tgt = (cx + 380, cy - 300 + (i // 2) * 100)
        xx, yy = lerp(x, tgt[0], f), lerp(y, tgt[1], f)
        with K.at(c, xx, yy, 0, pop_scale(dt - 0.05 * i)):
            box(c, 0, 0, 160, 70, NOTE_FILL if i % 2 == 0 else GRAY_FILL, ORANGE if i % 2 == 0 else GRAY, 5, 8)
    if f > 0.6:
        a = clamp01((f - 0.6) / 0.3)
        label(c, "拼", cx + 80, cy - 400, 70, RED, alpha=a)
        label(c, "放", cx + 380, cy - 400, 70, GRAY, alpha=a)
    return None


ev(j, k9_pile, pile9, "pop", 0.8)
b.hit(j, k9_split, "shaker", 0.8, "分成拼和放")


def bad9(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(9, k9_bad)
    if dt < 0:
        return None
    dashed(c, (cx - 540, cy + 120), (cx + 540, cy + 120), GRAY, 4)
    gy = cy + 560
    with K.at(c, cx, gy - 150, 0, pop_scale(dt)):
        c.translate(-cx, -(gy - 150))
        draw_li(c, cx - 400, gy, 0.7, "o")
        for i in range(6):
            x, y = cx - 160 + (i % 3) * 200, cy + 260 + (i // 3) * 120
            on = int((T - tb(9, k9_bad)) * 6 + i) % 2 == 0
            box(c, x, y, 170, 80, RED_FILL if on else "#FFFFFF", RED, 5, 8)
            label(c, "急", x, y + 2, 46, RED)
    return None


ev(j, k9_bad, bad9, "bongo_high", 0.85)

# ================================================================ 屏 10：小李糊弄老客户，客户转身离开；日历翻到下个季度，那把椅子空着
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k10_two, k10_fake, k10_cal, k10_empty = seq(j, [(16, 1, 0.5), (17, 1, 0.5), (17, 2, 0.5), (17, 3, 0.5)])
L.note("这个月的数字", "下个季度")


def two10(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(10, k10_two)
    if dt < 0:
        return None
    gy = cy + 540
    empty = T >= tb(10, k10_empty)
    desk(c, cx, gy - 200, 420)
    chair(c, cx + 260, gy)
    hy = gy - 290 * 0.8
    draw_li(c, cx - 300, gy, 0.8, "smile", rh=(cx - 200, hy + 40))
    if not empty:
        fake = T >= tb(10, k10_fake)
        draw_client(c, cx + 260, gy - 105, 0.75, mood="sad" if fake else "flat")
    return None


ev(j, k10_two, two10, "wood_low", 0.75)


def fake10(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(10, k10_fake)
    if dt < 0:
        return None
    with K.at(c, cx - 200, cy - 120, 0, pop_scale(dt)):
        box(c, 0, 0, 380, 200, "#FFFFFF", BLACK, 6, 12)
        label(c, "这个月的数字", 0, -50, 46, RED)
        c.drawPath(P((-140, 60), (-60, 20), (20, 50), (130, -20)), wb.marker(GREEN, 8))
    return None


ev(j, k10_fake, fake10, "rim", 0.8)


def cal10(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(10, k10_cal)
    if dt < 0:
        return None
    with K.at(c, cx + 300, cy - 360, 0, pop_scale(dt)):
        calendar_page(c, 0, 0, 300, 200, "下个季度", size=50)
    return None


ev(j, k10_cal, cal10, "wood_high", 0.8)


def empty10(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(10, k10_empty)
    if dt < 0:
        return None
    gy = cy + 540
    x, dy, _ = C.walk(T, tb(10, k10_empty), 1.2, cx + 300, cx + 480, 10, 3)
    draw_client(c, x, gy + dy, 0.6, back=True, alpha=1 - 0.6 * clamp01(dt / 1.2))
    label(c, "？", cx + 260, gy - 280, 80, GRAY, "black")
    return None


ev(j, k10_empty, empty10, "tom", 0.85)

# ================================================================ 屏 11：深夜加班的小李趴下；一扇写着“机会”的门开着，他够不着
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k11_desk, k11_down, k11_door, k11_reach = seq(j, [None, (18, 1, 0.5), (18, 2, 0.5), (18, 3, 0.5)])
L.note("机会", "半夜")


def desk11(c, T, cx=cx, cy=cy):
    gy = cy + 540
    c.drawCircle(cx - 420, cy - 420, 60, K.paint(YELLOW))
    c.drawCircle(cx - 396, cy - 440, 54, K.paint(THEME["paper"]))
    label(c, "半夜", cx - 260, cy - 430, 50, GRAY)
    desk(c, cx - 200, gy - 200, 520)
    laptop(c, cx - 200, gy - 210, 1.1)
    down = T >= tb(11, k11_down)
    if down:
        draw_li(c, cx - 420, gy, 0.8, "sad", squash=0.82, lh=(cx - 330, gy - 215), rh=(cx - 300, gy - 215))
        sweat(c, cx - 360, gy - 330, 1.2)
    else:
        hy = gy - 290 * 0.8
        draw_li(c, cx - 420, gy, 0.8, "sad", rh=(cx - 260, gy - 240), lh=(cx - 280, gy - 230))
    return None


pop(j, k11_desk, cx - 200, cy + 300, desk11, "wood_low", 0.75)
b.hit(j, k11_down, "tom", 0.8, "小李趴下")


def door11(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(11, k11_door)
    if dt < 0:
        return None
    gy = cy + 540
    x = cx + 350
    with K.at(c, x, gy - 250, 0, pop_scale(dt)):
        c.translate(-x, -(gy - 250))
        c.drawRect(skia.Rect.MakeXYWH(x - 120, gy - 520, 240, 520), K.paint(YELLOW, 0.6))
        c.drawRect(skia.Rect.MakeXYWH(x - 120, gy - 520, 240, 520), wb.marker(BLACK, 7))
        c.drawPath(P((x - 120, gy - 520), (x - 210, gy - 480), (x - 210, gy + 30), (x - 120, gy)), K.paint(WOOD))
        c.drawPath(P((x - 120, gy - 520), (x - 210, gy - 480), (x - 210, gy + 30), (x - 120, gy)), wb.marker(WOOD_LINE, 7))
        label(c, "机会", x, gy - 600, 70, ORANGE)
    return None


ev(j, k11_door, door11, "ding", 0.8)


def reach11(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(11, k11_reach)
    if dt < 0:
        return None
    gy = cy + 540
    f = ease_out(clamp01(dt / 0.4))
    C.line(c, (cx - 120, gy - 220), (cx - 120 + 140 * f, gy - 260), BLACK, 10)
    dashed(c, (cx + 40, gy - 260), (cx + 150, gy - 260), GRAY, 5, clamp01(dt / 0.3))
    xmark(c, cx + 90, gy - 330, 40, clamp01((dt - 0.2) / 0.3))
    return None


ev(j, k11_reach, reach11, "rim", 0.8)

# ================================================================ 屏 12：手机屏幕换成一本书和一把工具；三年后的小李站在旁边，像换了个人
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k12_ph, k12_swap, k12_yr, k12_new = seq(j, [None, (19, 1, 0.5), (19, 2, 0.5), (19, 3, 0.5)])
L.note("一小时", "手艺", "三年后")


def ph12(c, T, cx=cx, cy=cy):
    x, y = cx - 250, cy - 120
    swap = T >= tb(12, k12_swap)
    phone(c, x, y, 300, 520)
    if not swap:
        for i in range(4):
            yy = y - 160 + ((T * 160 + i * 90) % 360)
            box(c, x, yy, 200, 70, BLUE_FILL, GRAY, 3, 8)
        label(c, "一小时", x, y + 330, 50, GRAY)
    else:
        f = pop_scale(T - tb(12, k12_swap))
        with K.at(c, x, y, 0, f):
            box(c, -40, -60, 130, 170, ORANGE_FILL, ORANGE, 6, 6)
            C.line(c, (-40, -140), (-40, 20), ORANGE, 4)
            with K.at(c, 50, 90, -30):
                c.drawRoundRect(skia.Rect.MakeXYWH(-12, -10, 24, 150), 8, 8, K.paint(WOOD))
                box(c, 0, -20, 110, 46, "#9AA0A8", BLACK, 5, 6)
        label(c, "手艺", x, y + 330, 54, ORANGE)
    hy = cy + 560 - 290 * 0.75
    draw_li(c, cx - 470, cy + 560, 0.75, "flat", rh=(cx - 380, hy + 30))


pop(j, k12_ph, cx - 300, cy + 100, ph12, "wood_low", 0.75)
b.hit(j, k12_swap, "pop", 0.85, "手机换成书和工具")


def yr12(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(12, k12_yr)
    if dt < 0:
        return None
    with K.at(c, cx + 300, cy - 400, 0, pop_scale(dt)):
        calendar_page(c, 0, 0, 280, 190, "三年后", size=52)
    c.drawPath(wb.arrow((cx - 60, cy + 120), (cx + 160, cy + 120), 0.0, 40), wb.marker(GREEN, 9))
    return None


ev(j, k12_yr, yr12, "wood_high", 0.8)


def new12(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(12, k12_new)
    if dt < 0:
        return None
    gy = cy + 560
    x = cx + 340
    with K.at(c, x, gy, 0, pop_scale(dt)):
        c.translate(-x, -gy)
        hy = gy - 290 * 1.0
        draw_li(c, x, gy, 1.0, "smile", rh=(x + 100, hy + 40))
        with K.at(c, x + 110, hy + 20, -30):
            c.drawRoundRect(skia.Rect.MakeXYWH(-12, -10, 24, 150), 8, 8, K.paint(WOOD))
            box(c, 0, -20, 110, 46, "#9AA0A8", BLACK, 5, 6)
    sparkle(c, x, gy - 300, dt, YELLOW, 10, 90, 220)
    return None


ev(j, k12_new, new12, "ding", 0.9)

# ================================================================ 屏 13：房租单、考核表、家里的电话压在小李肩上；大字“三步”
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k13_li, k13_a, k13_b, k13_c, k13_3 = seq(j, [None, (20, 1, 0.2), (20, 1, 0.5), (20, 1, 0.8), (21, 1, 0.3)])
LOADS = [("房租", ORANGE), ("考核", RED), ("家里", BLUE)]
L.note(*[x[0] for x in LOADS])


def li13(c, kk, T, cx=cx, cy=cy):
    n = sum(1 for k_ in (k13_a, k13_b, k13_c) if T >= tb(13, k_))
    gy = cy + 560
    sq = 1 - 0.05 * n
    draw_li(c, cx - 100, gy, 0.9, "sad" if n else "flat", squash=sq,
            lh=(cx - 180, gy - 290 * 0.9 * sq), rh=(cx - 20, gy - 290 * 0.9 * sq))
    top = gy - 290 * 0.9 * sq - 70
    for i in range(n):
        s_, col = LOADS[i]
        d = T - tb(13, (k13_a, k13_b, k13_c)[i])
        drop = (1 - ease_out(clamp01(d / 0.2))) * 300
        with K.at(c, cx - 100 + (i - 1) * 12, top - i * 92 - drop, (i - 1) * 4):
            box(c, 0, 0, 260, 84, "#FFFFFF", col, 7, 10)
            label(c, s_, 0, 2, 52, col)
    if n:
        sweat(c, cx - 20, gy - 330, 1.3)
    return None


ev(j, k13_li, li13, "wood_low", 0.75)
b.hit(j, k13_a, "tom", 0.8, "房租单压上来")
b.hit(j, k13_b, "tom", 0.8, "考核表压上来")
b.hit(j, k13_c, "tom", 0.85, "家里电话压上来")
ev(j, k13_3, L.slam_text("三步", cx + 280, cy - 300, 170, RED, j, k13_3, rot=-4), "kick", 0.9)
b.shots[j].shake = [(k13_3, 9.0)]

# ================================================================ 屏 14：做法一——便签上只写一样本事，用框框住
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k14_n, k14_note, k14_one, k14_box = seq(j, [None, (22, 1, 0.5), (22, 2, 0.6), (22, 3, 0.5)])
L.note("第一", "三年后", "一样本事", "做表", "画画", "外语", "就一样")
pop(j, k14_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: label(c, "第一", cx - 380, cy - 470, 90, RED), "rim", 0.8)


def note14(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(14, k14_note)
    if dt < 0:
        return None
    with K.at(c, cx, cy - 120, -2, pop_scale(dt)):
        box(c, 0, 0, 600, 420, NOTE_FILL, ORANGE, 7, 10)
        label(c, "三年后", -170, -150, 50, GRAY)
        one = T >= tb(14, k14_one)
        if one:
            label(c, "一样本事", 0, 0, 90, BLACK)
        for n, s_ in enumerate(("做表", "画画", "外语")):
            if one:
                a = 1 - clamp01((T - tb(14, k14_one)) / 0.4)
                if a <= 0:
                    continue
            else:
                a = 1.0
            label(c, s_, -170 + n * 170, 60, 56, GRAY, alpha=a)
    hy = cy + 560 - 290 * 0.75
    draw_li(c, cx - 400, cy + 560, 0.75, "flat", rh=(cx - 300, hy + 30 + 10 * math.sin(T * 8)))
    return None


ev(j, k14_note, note14, "wood_high", 0.8)
b.hit(j, k14_one, "pop", 0.8, "只留一样")


def box14(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(14, k14_box)
    if dt < 0:
        return None
    part, _ = wb.partial(wb.rect(cx, cy - 120, 440, 150, 20), clamp01(dt / 0.4))
    c.drawPath(part, wb.marker(RED, 10))
    with K.at(c, cx + 150, cy + 250, -4, pop_scale(dt - 0.3)):
        label(c, "就一样", 0, 0, 80, RED)
    return None


ev(j, k14_box, box14, "rim", 0.85)

# ================================================================ 屏 15：做法二——每周日历里一格一小时被钉住，雷打不动
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k15_n, k15_cal, k15_pin, k15_lab = seq(j, [None, (23, 1, 0.3), (23, 1, 0.8), (23, 2, 0.5)])
L.note("第二", "一小时", "雷打不动", "一", "二", "三", "四", "五", "六", "日")
pop(j, k15_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: label(c, "第二", cx - 380, cy - 470, 90, RED), "rim", 0.8)
DAYS = ["一", "二", "三", "四", "五", "六", "日"]


def cal15(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(15, k15_cal)
    if dt < 0:
        return None
    x0, y0 = cx - 450, cy - 250
    with K.at(c, cx, cy, 0, pop_scale(dt)):
        c.translate(-cx, -cy)
        box(c, cx, cy + 20, 1000, 640, "#FFFFFF", BLACK, 7, 14)
        for i, d in enumerate(DAYS):
            label(c, d, x0 + 70 + i * 135, y0 - 20, 46, GRAY)
            for r in range(4):
                xx, yy = x0 + 70 + i * 135, y0 + 60 + r * 120
                busy = (i * 3 + r * 5) % 4 != 0
                box(c, xx, yy, 115, 100, BLUE_FILL if busy else "#FFFFFF", GRAY, 3, 8)
    return None


ev(j, k15_cal, cal15, "wood_low", 0.8)


def pin15(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(15, k15_pin)
    if dt < 0:
        return None
    x0, y0 = cx - 450, cy - 250
    xx, yy = x0 + 70 + 5 * 135, y0 + 60 + 1 * 120
    box(c, xx, yy, 115, 100, GREEN_FILL, GREEN, 6, 8)
    label(c, "一小时", xx, yy + 20, 30, GREEN)
    drop = (1 - ease_out(clamp01(dt / 0.15))) * 120
    c.drawCircle(xx, yy - 30 - drop, 18, K.paint(RED))
    C.line(c, (xx, yy - 30 - drop), (xx, yy - drop), BLACK, 5)
    return None


ev(j, k15_pin, pin15, "kick", 0.85)
ev(j, k15_lab, L.stamp("雷打不动", cx + 150, cy + 470, 70, j, k15_lab, color=GREEN, rot=-5), "rim", 0.85)

# ================================================================ 屏 16：做法三——要取舍时，三年后的小李在旁边举着一个问号
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
k16_n, k16_fork, k16_fut, k16_q = seq(j, [None, (24, 1, 0.5), (24, 2, 0.5), (24, 3, 0.5)])
L.note("第三", "三年后的我", "这个", "那个")
pop(j, k16_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: label(c, "第三", cx - 380, cy - 470, 90, RED), "rim", 0.8)


def fork16(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(16, k16_fork)
    if dt < 0:
        return None
    gy = cy + 540
    with K.at(c, cx - 150, gy - 150, 0, pop_scale(dt)):
        c.translate(-(cx - 150), -(gy - 150))
        c.drawPath(P((cx - 300, gy), (cx - 150, gy - 160), (cx - 330, gy - 380)), wb.marker(GRAY, 8))
        c.drawPath(P((cx - 150, gy - 160), (cx + 20, gy - 380)), wb.marker(GRAY, 8))
        box(c, cx - 330, gy - 430, 150, 70, "#FFFFFF", BLUE, 5, 10)
        label(c, "这个", cx - 330, gy - 428, 44, BLUE)
        box(c, cx + 20, gy - 430, 150, 70, "#FFFFFF", ORANGE, 5, 10)
        label(c, "那个", cx + 20, gy - 428, 44, ORANGE)
        hy = gy - 290 * 0.75
        draw_li(c, cx - 360, gy, 0.75, "o", rh=(cx - 270, hy - 20))
    return None


ev(j, k16_fork, fork16, "wood_low", 0.8)


def fut16(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(16, k16_fut)
    if dt < 0:
        return None
    x, gy = cx + 340, cy + 540
    with K.at(c, x, gy, 0, pop_scale(dt)):
        c.translate(-x, -gy)
        dashed_rect(c, x, gy - 230, 300, 520, GREEN, 5, 0.8, 30)
        hy = gy - 290 * 0.85
        draw_li(c, x, gy - 20, 0.85, "smile", rh=(x + 90, hy - 60))
        label(c, "三年后的我", x, gy - 540, 50, GREEN)
    return None


ev(j, k16_fut, fut16, "pop", 0.8)


def q16(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(16, k16_q)
    if dt < 0:
        return None
    with K.at(c, cx + 450, cy + 70, wobble(dt, 10, 12, 4), pop_scale(dt)):
        label(c, "？", 0, 0, 150, GREEN, "black")
    return None


ev(j, k16_q, q16, "bongo_high", 0.85)

# ================================================================ 屏 17：小李照样在忙，脚下多了一条通向路标的路
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
k17_busy, k17_path, k17_sign, k17_walk = seq(j, [None, (25, 1, 0.5), (25, 2, 0.3), (25, 2, 0.8)])
L.note("照样忙", "以后")


def busy17(c, T, cx=cx, cy=cy):
    gy = cy + 540
    desk(c, cx - 200, gy - 200, 480)
    for i in range(4):
        box(c, cx - 320 + i * 20, gy - 230 - i * 26, 200, 26, NOTE_FILL, ORANGE, 4, 4)
    hy = gy - 290 * 0.8
    tap = 14 * math.sin(T * 14)
    if T < tb(17, k17_walk):
        draw_li(c, cx - 420, gy, 0.8, "flat", rh=(cx - 300, gy - 230 + tap), lh=(cx - 330, gy - 220 - tap))
    label(c, "照样忙", cx - 200, cy - 20, 60, GRAY)


pop(j, k17_busy, cx - 200, cy + 300, busy17, "wood_low", 0.75)


def path17(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(17, k17_path)
    if dt < 0:
        return None
    gy = cy + 540
    p = skia.Path()
    p.moveTo(cx - 420, gy + 40)
    p.cubicTo(cx - 100, gy + 40, cx + 100, cy + 200, cx + 330, cy - 120)
    part, _ = wb.partial(p, clamp01(dt / 0.6))
    c.drawPath(part, wb.marker(YELLOW, 28, 0.6))
    c.drawPath(part, wb.marker(GREEN, 8))
    if T >= tb(17, k17_sign):
        with K.at(c, cx + 380, cy - 100, 0, pop_scale(T - tb(17, k17_sign))):
            road_sign(c, 0, 0, 1.0, "以后")
    if T >= tb(17, k17_walk):
        d = T - tb(17, k17_walk)
        f = ease_in_out(clamp01(d / 1.4))
        pt = point_at(p, 0.45 * f)
        bob = -abs(math.sin(d * 9)) * 10
        draw_li(c, pt.x(), pt.y() + bob, 0.7, "smile", bag=True)
    return None


ev(j, k17_path, path17, "shaker", 0.8)
b.hit(j, k17_sign, "ding", 0.85, "路标亮起")
b.hit(j, k17_walk, "wood_high", 0.75, "小李踏上路")

# ================================================================ 屏 18：十九讲小卡片排成几排；第一讲那张亮起；评论框
cx, cy = R[18]
j = L.scene(18, (cx, cy + 10, Z))
k18_rows, k18_end, k18_cb, k18_first = seq(j, [(26, 1, 0.3), (27, 0, 0.6), (27, 1, 0.6), (28, 1, 0.4)])
L.note("最想先用哪一讲？", "从这里开始")
GRID18 = [(cx - 420 + (i % 5) * 210, cy - 430 + (i // 5) * 135) for i in range(19)]


def cards18(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(18, k18_rows)
    if dt < 0:
        return None
    for i, (x, y) in enumerate(GRID18):
        d = dt - 0.045 * i
        if d < 0:
            continue
        first = i == 0 and T >= tb(18, k18_first)
        last = i == 18 and T >= tb(18, k18_end)
        fill = YELLOW if first else (GREEN_FILL if last else "#FFFFFF")
        col = RED if first else (GREEN if last else BLACK)
        with K.at(c, x, y, ((i * 37) % 7 - 3) * 0.8, pop_scale(d) * (1.12 if first else 1.0)):
            box(c, 0, 0, 190, 108, fill, col, 6, 12)
            label(c, f"{i + 1:02d}", -62, -26, 28, GRAY, "sans_medium")
            s_ = LESSONS[i]
            label(c, s_, 0, 16, 44 if len(s_) <= 3 else 36, col)
    if T >= tb(18, k18_first):
        d = T - tb(18, k18_first)
        x, y = GRID18[0]
        sparkle(c, x, y, d, YELLOW, 10, 80, 180)
        with K.at(c, x + 60, y - 95, 0, pop_scale(d - 0.15)):
            label(c, "从这里开始", 0, 0, 44, ORANGE)
    return None


ev(j, k18_rows, cards18, "shaker", 0.75)
b.hit(j, k18_end, "pop", 0.8, "看长远那张亮起")


def cb18(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(18, k18_cb)
    if dt < 0:
        return None
    with K.at(c, cx + 80, cy + 400, 0, pop_scale(dt)):
        comment_box(c, 0, 0, 820, 220)
        label(c, "最想先用哪一讲？", 0, -20, 64, RED)
    with K.at(c, cx - 450, cy + 600, 0, pop_scale(dt)):
        draw_li(c, 0, 0, 0.6, "smile", rh=(80, -230 + 12 * math.sin(T * 6)))
    return None


ev(j, k18_cb, cb18, "wood_high", 0.8)
b.hit(j, k18_first, "ding", 0.9, "第一讲亮起")

# ================================================================ 屏 19：小李回头，身后长路插满十九面小旗；他继续往前走，路越走越亮
cx, cy = R[19]
j = L.scene(19, (cx, cy + 10, Z))
k19_road, k19_flags, k19_back, k19_go, k19_glow = seq(j, [None, (29, 0, 0.4), (29, 0, 0.9), (29, 1, 0.6), (29, 2, 0.4)])
L.note("一点点变好")


def road_path():
    p = skia.Path()
    p.moveTo(cx - 60, cy + 600)
    p.cubicTo(cx - 520, cy + 360, cx + 420, cy + 120, cx - 120, cy - 120)
    p.cubicTo(cx - 420, cy - 260, cx - 100, cy - 380, cx - 160, cy - 470)
    return p


ROAD = road_path()
FLAG_U = [0.08 + 0.9 * i / 18 for i in range(19)]


def road19(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(19, k19_road)
    if dt < 0:
        return None
    a = clamp01(dt / 0.4)
    c.drawPath(ROAD, wb.marker(WOOD, 70, a * 0.8))
    c.drawPath(ROAD, wb.marker(WOOD_LINE, 6, a))
    for i, u in enumerate(FLAG_U):
        d = T - tb(19, k19_flags) - 0.05 * (18 - i)
        if d < 0:
            continue
        pt = point_at(ROAD, 1 - u)
        s = lerp(1.0, 0.45, 1 - u)
        with K.at(c, pt.x() + 30 * s, pt.y(), 0, pop_scale(d) * s):
            flag(c, 0, 0, i, 150, wave=6 * math.sin(T * 4 + i))
    return None


ev(j, k19_road, road19, "wood_low", 0.75)
b.hit(j, k19_flags, "shaker", 0.8, "十九面小旗插满长路")


def li19(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(19, k19_back)
    if dt < 0:
        return None
    gy = cy + 560
    going = T >= tb(19, k19_go)
    if not going:
        draw_li(c, cx + 200, gy, 0.9, "smile", back=True)
        label(c, "回头看", cx + 380, gy - 380, 56, GRAY, alpha=clamp01(dt / 0.3))
    else:
        d = T - tb(19, k19_go)
        x, dy, _ = C.walk(T, tb(19, k19_go), 2.4, cx + 200, cx + 420, 12, 2.5)
        draw_li(c, x, gy + dy, 0.9, "smile", bag=True)
    return None


L.note("回头看")
ev(j, k19_back, li19, "pop", 0.8)
b.hit(j, k19_go, "wood_high", 0.75, "转身往前走")


def glow19(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(19, k19_glow)
    if dt < 0:
        return None
    gy = cy + 560
    for i in range(5):
        a = clamp01((dt - 0.15 * i) / 0.3)
        if a <= 0:
            continue
        x = cx + 120 + i * 90
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 40, gy + 6, 80, 20), 10, 10, K.paint(YELLOW, a))
    sparkle(c, cx + 420, gy - 200, dt, YELLOW, 10, 60, 160)
    with K.at(c, cx + 280, cy - 330, 0, pop_scale(dt - 0.2)):
        label(c, "一点点变好", 0, 0, 80, THEME["acc"])
    return None


ev(j, k19_glow, glow19, "ding", 0.9)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=19, notes=NOTES)
L.export(globals())
