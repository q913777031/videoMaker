"""《丰田模式》17 合作伙伴：合作方总掉链子，换掉就好了吗？（白板手绘 + AI 旁白，竖屏 2:3）

倒叙：先给结果，再倒回去讲。2026-11 新结构：先痛点和身边的例子，例子段之后才进倒叙开头（“丰田的合作方，也出过大事”）。
画面上有一条贯穿的“倒叙磁带”——第 5、6 屏右上角一张“结果”胶片角标；第 7 屏一个倒带键“◀◀ 倒回去”，之后讲丰田平时怎么做的几屏，
角标换成“起因”。
- 开场（chain）：小李和合作方各拽一头，链子逐拍绷紧，中间一节裂开，“掉链子”；
- 日常：桌上改了五遍的稿子盖“第5版”；隔壁工位的数据表旁一个沙漏；小李握拳，气泡“换掉！”；
- 身边的例子：设计师屏幕上“第5版”，小李的需求只有一行“要大气一点”，drop 拍放大镜照上去；隔壁同事等系统导出进度条；
  装修师傅贴砖，小李连声催，砖越贴越歪；
- 先看结果：日历“一九九七年”；画着刹车盘的工厂，大火窜起，员工往外跑；
  丰田生产线一盏盏灯熄灭、传送带停住，“停了”；接着灯一盏盏亮回来，传送带又转起来；
- 倒回去：倒带键；地图上一家家小工厂亮灯，举着零件，箭头汇向丰田；月亮下窗户都亮着，“连夜开工”；
- 书中做法：丰田组长和合作厂员工握手，下面一条“很多年”的时间轴；一级级台阶“价格”“质量”，丰田派人进对方工厂一起拧扳手；
  “挑战”“帮助”两张卡，一群人一起扛起大梁；
- 为什么换掉不一定好：左边换了个新人，头上照样冒出“老问题”；右边帮对方补上缺口，变成“靠得住”；
- 说回我们：领导皱眉、小李夹在中间，“三步”；三步做法；链子接好，两人一起往前走；
- 收尾：评论区三种头疼的合作方；小李拉别人一把，后来他摔倒时一群人跑来扶；下一讲预告（手机上一个个应用图标）。
小李 common.draw_li；同事小王 scenekit.draw_wang（不戴安全帽）；车间员工 common.draw_worker（戴安全帽）；
丰田组长 scenekit.draw_leader2；领导 common.draw_boss；设计师为本讲小人（贝雷帽、橙色毛衣，不戴安全帽）。
文案见 fengtian/PLAN.md「### 17」；时间轴、配乐、相机、人物见 fengtian/common.py，小工具见 fengtian/scenekit.py。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, draw_worker, pop_scale, wobble
from fengtian.scenekit import (GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL, NOTE_FILL, ORANGE_FILL, WOOD_LINE,
                               Kit, at_pop, box, bubble_text, comment_box, dashed, desk, draw_leader2, draw_wang,
                               heart, hourglass, laptop, paper, phone, sparkle, sweat, tick, xmark)
from whiteboard import engine as wb
from whiteboard.engine import P

# 每屏：(旁白句序号, 页眉标签, 白板区块)；句子分组与 PLAN 的 SCREENS_DRAFT 一致
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "身边的例子", 2),
    ([4], "身边的例子", 3),
    ([5], "身边的例子", 4),
    ([6], "倒叙 · 先看结果", 5),
    ([7, 8], "倒叙 · 先看结果", 6),
    ([9, 10], "倒叙 · 倒回去", 7),
    ([11, 12], "丰田模式 · 书中做法", 8),
    ([13, 14], "丰田模式 · 书中做法", 9),
    ([15, 16], "书中观点", 10),
    ([17, 18, 19], "为什么换掉不一定好", 11),
    ([20, 21], "说回我们自己", 12),
    ([22], "做法一 · 示意", 13),
    ([23], "做法二 · 示意", 14),
    ([24], "做法三 · 示意", 15),
    ([25], "顺了", 16),
    ([26, 27, 28, 29], "评论区见", 17),
]

THEME = FT.get("17")          # 本讲样式：鼠尾草横线、开场 chain、转场 swing
L = C.Lesson("17", SCREENS, drop_screen=2, board_size=(5000, 12800), theme=THEME)
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
    "本讲依据：原则 11——尊重合作伙伴和供应商，给挑战也给帮助。",
    "一九九七年给丰田供刹车零件的工厂失火、众多合作厂分头赶做零件是真实事件（爱信火灾，书中是否写到待核），"
    "画面不写恢复天数和公司数。稿子、数据表、装修为示意；小李、小王、设计师、领导为虚构人物。",
]


# ================================================================ 本讲道具

def label(c, s, x, y, size, color=BLACK, font="hand", alpha=1.0):
    K.text(c, s, x, y, size, font, color, alpha)


def film_tag(c, x, y, s, color=RED, alpha=1.0):
    """倒叙角标：一小段胶片 + 字（“结果”“起因”）。"""
    box(c, x, y, 230, 100, "#2B2B30", BLACK, 5, 8, alpha)
    for i in range(5):
        for yy in (y - 38, y + 38):
            c.drawRect(skia.Rect.MakeXYWH(x - 100 + i * 46, yy - 7, 22, 14), K.paint("#FFFFFF", alpha))
    box(c, x, y, 170, 52, "#FFFFFF", color, 4, 6, alpha)
    label(c, s, x, y + 2, 40, color, alpha=alpha)


L.note("结果", "起因")


def tag_fn(j, s, color=RED):
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, 0))
        if sc <= 0:
            return None
        cx_, cy_ = R[j]
        with at_pop(c, cx_ + 420, cy_ - 500, sc):
            film_tag(c, cx_ + 420, cy_ - 500, s, color)
        return None
    return fn


def factory(c, x, y, w=300, h=200, fill="#FFFFFF", alpha=1.0, lit=0.0, chimney=True):
    """小工厂：(x, y) 为底边中点；锯齿屋顶 + 烟囱；lit 0–1 为窗户亮灯程度。"""
    n = 3
    pts = [(x - w / 2, y), (x - w / 2, y - h * 0.6)]
    for i in range(n):
        x0 = x - w / 2 + i * w / n
        pts += [(x0 + w / n, y - h), (x0 + w / n, y - h * 0.6)]
    pts += [(x + w / 2, y)]
    body = P(*pts, close=True)
    if chimney:
        c.drawRect(skia.Rect.MakeXYWH(x + w / 2 - 60, y - h * 1.25, 34, h * 0.65), K.paint(fill, alpha))
        c.drawRect(skia.Rect.MakeXYWH(x + w / 2 - 60, y - h * 1.25, 34, h * 0.65), wb.marker(BLACK, 6, alpha))
    c.drawPath(body, K.paint(fill, alpha))
    c.drawPath(body, wb.marker(BLACK, 7, alpha))
    for i in range(3):
        r_ = skia.Rect.MakeXYWH(x - w / 2 + 30 + i * (w - 60) / 3, y - h * 0.42, (w - 60) / 3 - 20, h * 0.22)
        c.drawRect(r_, K.paint(YELLOW if lit > i / 3 else GRAY_FILL, alpha))
        c.drawRect(r_, wb.marker(BLACK, 4, alpha))


def brake_disc(c, x, y, r, alpha=1.0):
    c.drawCircle(x, y, r, K.paint("#D9DCE1", alpha))
    c.drawCircle(x, y, r, wb.marker(BLACK, 6, alpha))
    c.drawCircle(x, y, r * 0.35, wb.marker(BLACK, 5, alpha))
    for i in range(5):
        a = i * 2 * math.pi / 5
        c.drawCircle(x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62, r * 0.09, K.paint(BLACK, alpha))


def flame(c, x, y, h, T, alpha=1.0):
    """火苗：(x, y) 为底部中点。"""
    for k_, (col, s_) in enumerate(((RED, 1.0), (ORANGE, 0.72), (YELLOW, 0.42))):
        hh = h * s_ * (1 + 0.08 * math.sin(T * 13 + k_ * 2))
        w = hh * 0.55
        p = skia.Path()
        p.moveTo(x - w, y)
        p.cubicTo(x - w * 1.1, y - hh * 0.5, x - w * 0.2, y - hh * 0.6, x + 8 * math.sin(T * 9 + k_), y - hh)
        p.cubicTo(x + w * 0.3, y - hh * 0.6, x + w * 1.1, y - hh * 0.45, x + w, y)
        p.close()
        c.drawPath(p, K.paint(col, alpha * 0.92))
    c.drawPath(P((x - h * 0.55, y), (x + h * 0.55, y)), wb.marker(BLACK, 5, alpha))


def car(c, x, y, s=1.0, color="#7FB2E5", alpha=1.0):
    """小汽车侧视：(x, y) 为底边中点。"""
    body = P((x - 110 * s, y - 20 * s), (x - 100 * s, y - 60 * s), (x - 50 * s, y - 64 * s), (x - 20 * s, y - 100 * s),
             (x + 50 * s, y - 100 * s), (x + 80 * s, y - 64 * s), (x + 110 * s, y - 56 * s), (x + 112 * s, y - 20 * s),
             close=True)
    c.drawPath(body, K.paint(color, alpha))
    c.drawPath(body, wb.marker(BLACK, 6, alpha))
    for dx in (-60, 60):
        c.drawCircle(x + dx * s, y - 18 * s, 22 * s, K.paint("#3B3F48", alpha))
        c.drawCircle(x + dx * s, y - 18 * s, 22 * s, wb.marker(BLACK, 5, alpha))


def lamp(c, x, y, on, alpha=1.0, color=GREEN):
    C.line(c, (x, y - 70), (x, y - 30), BLACK, 6, alpha)
    c.drawCircle(x, y, 32, K.paint(color if on else "#6B6F78", alpha))
    c.drawCircle(x, y, 32, wb.marker(BLACK, 6, alpha))
    if on:
        c.drawCircle(x, y, 52, K.paint(color, 0.22 * alpha, blur=12))


def wrench(c, x, y, rot, s=1.0, alpha=1.0):
    with K.at(c, x, y, rot):
        c.drawRoundRect(skia.Rect.MakeXYWH(-14 * s, 0, 28 * s, 150 * s), 10, 10, K.paint("#B8BEC8", alpha))
        c.drawRoundRect(skia.Rect.MakeXYWH(-14 * s, 0, 28 * s, 150 * s), 10, 10, wb.marker(BLACK, 5, alpha))
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(-36 * s, -40 * s, 72 * s, 72 * s), 120, 300)
        c.drawPath(p, wb.marker(BLACK, 12, alpha))


def gear(c, x, y, r, rot, color=GRAY, alpha=1.0):
    with K.at(c, x, y, rot):
        for i in range(8):
            a = i * math.pi / 4
            C.line(c, (math.cos(a) * r * 0.8, math.sin(a) * r * 0.8), (math.cos(a) * r * 1.15, math.sin(a) * r * 1.15),
                   color, r * 0.32, alpha)
        c.drawCircle(0, 0, r * 0.85, K.paint("#FFFFFF", alpha))
        c.drawCircle(0, 0, r * 0.85, wb.marker(color, 7, alpha))
        c.drawCircle(0, 0, r * 0.3, wb.marker(color, 6, alpha))


def draw_designer(c, x, y, s, lh=None, rh=None, mood="flat", alpha=1.0):
    """设计师（办公室，不戴安全帽）：贝雷帽 + 橙色毛衣 + 黑框眼镜。"""
    d_lh, d_rh = C.rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, ft, BLACK, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 44 * s, hy + 55 * s, x + 44 * s, y - 102 * s)
    c.drawRoundRect(torso, 20 * s, 20 * s, K.paint(ORANGE_FILL, alpha))
    c.drawRoundRect(torso, 20 * s, 20 * s, wb.marker(ORANGE, 7, alpha))
    C.line(c, sh, lh, ORANGE, 10, alpha)
    C.line(c, sh, rh, ORANGE, 10, alpha)
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    for dx in (-16, 16):
        c.drawRoundRect(skia.Rect.MakeXYWH(x + dx * s - 13 * s, hy - 14 * s, 26 * s, 20 * s), 4, 4, wb.marker(BLACK, 5, alpha))
    C._eyes_mouth(c, x, hy + 4 * s, s, mood, alpha)
    beret = skia.Path()
    beret.addOval(skia.Rect.MakeXYWH(x - 56 * s, hy - 70 * s, 104 * s, 42 * s))
    c.drawPath(beret, K.paint("#7A3B5A", alpha))
    c.drawPath(beret, wb.marker(BLACK, 5, alpha))
    c.drawCircle(x - 4 * s, hy - 74 * s, 8 * s, K.paint(BLACK, alpha))


def monitor(c, x, y, w=300, h=200, screen="#FFFFFF", alpha=1.0):
    box(c, x, y, w, h, "#2B2B30", BLACK, 7, 10, alpha)
    box(c, x, y, w - 24, h - 24, screen, GRAY, 3, 6, alpha)
    C.line(c, (x, y + h / 2), (x, y + h / 2 + 40), BLACK, 10, alpha)
    C.line(c, (x - 60, y + h / 2 + 42), (x + 60, y + h / 2 + 42), BLACK, 10, alpha)


def chain_row(c, x0, x1, y, gap_f=0.0, alpha=1.0, color=BLACK):
    """一条横链：gap_f 0–1 为中间断口张开的程度（0 = 接好）。"""
    n = 9
    mid = n // 2
    for i in range(n):
        u = i / (n - 1)
        x = lerp(x0, x1, u)
        if i == mid and gap_f > 0.5:
            continue
        dx = (-1 if i < mid else 1) * 60 * gap_f if i != mid else 0
        col = GREEN if (gap_f == 0 and abs(i - mid) <= 1 and color == GREEN) else color
        if i % 2:
            C.line(c, (x - 30 + dx, y), (x + 30 + dx, y), col, 12, alpha)
        else:
            c.drawOval(skia.Rect.MakeXYWH(x - 46 + dx, y - 24, 92, 48), wb.marker(col, 10, alpha))


def thumb(c, x, y, s=1.0, alpha=1.0):
    """竖大拇指。"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 40 * s, y - 20 * s, 80 * s, 80 * s), 18 * s, 18 * s, K.paint("#F6D9C2", alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 40 * s, y - 20 * s, 80 * s, 80 * s), 18 * s, 18 * s, wb.marker(BLACK, 6, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 30 * s, y - 80 * s, 30 * s, 70 * s), 14 * s, 14 * s, K.paint("#F6D9C2", alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 30 * s, y - 80 * s, 30 * s, 70 * s), 14 * s, 14 * s, wb.marker(BLACK, 6, alpha))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：改了五遍的稿子“第5版”；隔壁的数据表 + 沙漏；小李握拳“换掉！”
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k1_desk, k1_draft, k1_v5, k1_hg, k1_bub = seq(j, [None, (0, 0, 0.6), (0, 0, 0.95), (0, 1, 0.5), (1, 0, 0.9)])
L.note("第5版", "数据", "换掉！")


def desk1(c, T, cx=cx, cy=cy):
    desk(c, cx - 20, cy + 230, 560)
    angry = T >= tb(1, k1_bub)
    shake = 18 * math.sin(T * 16) if angry else 0.0
    hy = cy + 540 - 290 * 0.85
    draw_li(c, cx - 450, cy + 540, 0.85, "sad" if angry else "flat",
            rh=(cx - 360, hy - 40 + shake) if angry else (cx - 340, cy + 330))


pop(j, k1_desk, cx - 200, cy + 300, desk1, "wood_low", 0.7)


def draft1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k1_draft))
    if sc <= 0:
        return None
    x, y = cx - 100, cy + 40
    with at_pop(c, x, y, sc):
        for i in range(4):
            paper(c, x - 40 + i * 14, y - 40 + i * 12, 230, 290, rows=4, rot=-10 + i * 4, fill=GRAY_FILL)
        paper(c, x + 20, y + 10, 240, 300, rows=5, rot=4)
        if T >= tb(1, k1_v5):
            with K.at(c, x + 40, y - 60, -10, C.slam_scale(T - tb(1, k1_v5))):
                box(c, 0, 0, 200, 86, "#FFFFFF", RED, 7, 12)
                label(c, "第5版", 0, 2, 56, RED)
    return None


ev(j, k1_draft, draft1, "wood_high", 0.75)
b.hit(j, k1_v5, "rim", 0.85, "盖上第5版")


def hg1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k1_hg))
    if sc <= 0:
        return None
    x, y = cx + 340, cy + 20
    with at_pop(c, x, y, sc):
        desk(c, x, y + 210, 360)
        paper(c, x - 40, y + 30, 200, 240, rows=4, title="数据", tsize=44)
        f = clamp01((T - tb(1, k1_hg)) / 3.0)
        hourglass(c, x + 110, y + 100, 170, f)
    return None


ev(j, k1_hg, hg1, "wood_low", 0.75)
ev(j, k1_bub, L.slam_text("换掉！", cx - 160, cy - 380, 130, RED, j, k1_bub, rot=-5), "kick", 0.85)
b.shots[j].shake = [(k1_bub, 8.0)]

# ================================================================ 屏 2：设计师屏幕上第5版；小李发过去的需求只有一行“要大气一点”，放大镜照着
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()                       # drop 屏：“要大气一点”说完正好 drop，放大镜照上去、红问号、震屏、闪白
b.shots[j].shake, b.shots[j].flashes = [(KD, 14.0)], [(KD, 0.4)]
k9_d, k9_v5, k9_note = seq(j, [None, (3, 0, 0.5), (3, 1, 0.45)])
k9_note = min(k9_note, KD - 1)
k9_mag = KD
L.note("隔壁工位", "第5版", "需求", "要大气一点")


def des9(c, T, cx=cx, cy=cy):
    desk(c, cx + 220, cy + 250, 560)
    monitor(c, cx + 220, cy + 70, 380, 250)
    hy = cy + 540 - 290 * 0.8
    tap = 10 * math.sin(T * 14)
    draw_designer(c, cx + 460, cy + 540, 0.8, mood="sad", lh=(cx + 380 + tap, cy + 250))
    label(c, "隔壁工位", cx + 220, cy - 140, 46, GRAY)


pop(j, k9_d, cx + 260, cy + 250, des9, "wood_low", 0.7)


def v5_9(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(2, k9_v5)
    if dt < 0:
        return None
    g = C.slam_scale(dt)
    with K.at(c, cx + 220, cy + 70, -6, g):
        box(c, 0, 0, 200, 86, "#FFFFFF", RED, 7, 12)
        label(c, "第5版", 0, 2, 54, RED)
    return None


ev(j, k9_v5, v5_9, "rim", 0.85)


def note9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k9_note))
    if sc <= 0:
        return None
    x, y = cx - 260, cy - 330
    with at_pop(c, x, y, sc):
        box(c, x, y, 500, 270, "#FFFFFF", BLACK, 7, 14)
        label(c, "需求", x - 170, y - 80, 48, GRAY)
        label(c, "要大气一点", x, y + 20, 66, BLACK)
        hy = cy + 540 - 290 * 0.8
        draw_li(c, cx - 420, cy + 540, 0.8, "smile", rh=(cx - 320, hy + 30))
    return None


ev(j, k9_note, note9, "pop", 0.8)


def mag9(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(2, k9_mag)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.5))
    x, y = lerp(cx - 40, cx - 230, f), lerp(cy - 120, cy - 300, f)
    c.drawCircle(x, y, 120, K.paint("#FFFFFF", 0.25))
    c.drawCircle(x, y, 120, wb.marker(BLACK, 10))
    C.line(c, (x + 85, y + 85), (x + 190, y + 190), WOOD_LINE, 22)
    if f >= 1:
        label(c, "？", x + 170, y - 120, 90, RED, "black")
    return None


ev(j, k9_mag, mag9, "kick", 0.95)

# ================================================================ 屏 3：隔壁部门同事在等系统的进度条一点点导出
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k10_w, k10_ask, k10_sys, k10_bar = seq(j, [None, (4, 0, 0.6), (4, 2, 0.4), (4, 2, 0.9)])
L.note("怎么还没好？", "另一个系统", "导出中")


def wang10(c, T, cx=cx, cy=cy):
    desk(c, cx + 140, cy + 260, 620)
    monitor(c, cx + 140, cy + 70, 380, 250)
    hy = cy + 540 - 290 * 0.8
    draw_wang(c, cx + 430, cy + 540, 0.8, mood="sad", lh=(cx + 360, cy + 270))


pop(j, k10_w, cx + 200, cy + 260, wang10, "wood_low", 0.7)


def ask10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k10_ask))
    if sc <= 0:
        return None
    with at_pop(c, cx - 300, cy + 300, sc):
        draw_li(c, cx - 400, cy + 540, 0.8, "o")
        bubble_text(c, "怎么还没好？", cx - 300, cy - 120, 56, BLACK, -1)
    return None


ev(j, k10_ask, ask10, "pop", 0.75)


def sys10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k10_sys))
    if sc <= 0:
        return None
    x, y = cx + 140, cy - 380
    with at_pop(c, x, y, sc):
        box(c, x, y, 440, 170, BLUE_FILL, BLUE, 7, 16)
        label(c, "另一个系统", x, y - 30, 54, BLUE)
        gear(c, x - 170, y + 40, 26, (T - tb(3, k10_sys)) * 120, BLUE)
        dashed(c, (x, y + 86), (x, cy - 50), BLUE, 6)
    return None


ev(j, k10_sys, sys10, "wood_high", 0.75)


def bar10(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(3, k10_bar)
    if dt < 0:
        return None
    f = 0.08 + 0.3 * clamp01(dt / 4.0)
    x, y = cx + 140, cy + 60
    box(c, x, y + 20, 300, 44, "#FFFFFF", BLACK, 5, 10)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 146, y + 2, 292 * f, 36), 8, 8, K.paint(GREEN))
    label(c, "导出中", x, y - 50, 46, GRAY)
    hourglass(c, x - 300, y - 40, 120, clamp01(dt / 4.0))
    return None


ev(j, k10_bar, bar10, "shaker", 0.75)

# ================================================================ 屏 4：装修师傅贴砖，小李在旁边连声催，砖越贴越歪
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k11_wall, k11_c1, k11_c2, k11_bad = seq(j, [None, (5, 2, 0.3), None, (5, 3, 0.4)])
L.note("快点！", "再快点！")
TILES = [(cx - 40 + (i % 4) * 130, cy - 380 + (i // 4) * 120) for i in range(12)]


def wall11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k11_wall))
    if sc <= 0:
        return None
    with at_pop(c, cx + 150, cy, sc):
        c.drawRect(skia.Rect.MakeXYWH(cx - 120, cy - 460, 640, 540), K.paint("#F4EFE6"))
        c.drawRect(skia.Rect.MakeXYWH(cx - 120, cy - 460, 640, 540), wb.marker(BLACK, 7))
        n_tiles = 4
        for k_, upto in ((k11_c1, 7), (k11_c2, 10), (k11_bad, 12)):
            if T >= tb(4, k_):
                n_tiles = upto
        for i in range(n_tiles):
            x, y = TILES[i]
            bad = max(0, i - 3)
            rot = bad * 3.2 * (1 if i % 2 else -1)
            with K.at(c, x + bad * 4, y + bad * 3, rot):
                box(c, 0, 0, 120, 110, "#FFFFFF", GRAY, 5, 4)
        busy = 30 * math.sin(T * (8 + 6 * (n_tiles > 7)))
        hy = cy + 560 - 290 * 0.85
        draw_worker(c, cx + 200, cy + 560, 0.85, rh=(cx + 290 + busy * 0.6, cy + 220), mood="sad" if n_tiles > 7 else "flat")
        C.line(c, (cx + 290 + busy * 0.6, cy + 220), (cx + 330 + busy * 0.6, cy + 120), WOOD_LINE, 10)
        box(c, cx + 340 + busy * 0.6, cy + 100, 90, 40, "#C9CED6", BLACK, 5, 6)
        draw_li(c, cx - 380, cy + 560, 0.85, "o" if n_tiles > 4 else "flat",
                rh=(cx - 280, hy - 30 + 20 * math.sin(T * 12)) if n_tiles > 4 else None)
    return None


ev(j, k11_wall, wall11, "wood_low", 0.75)
ev(j, k11_c1, L.pop_bubble("快点！", cx - 330, cy - 160, j, k11_c1, 64, RED, tail=-1), "bongo_high", 0.8)
ev(j, k11_c2, L.pop_bubble("再快点！", cx - 290, cy - 360, j, k11_c2, 64, RED, tail=-1), "bongo_low", 0.85)


def bad11(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(4, k11_bad)
    if dt < 0:
        return None
    x, y = TILES[11]
    xmark(c, x + 30, y + 20, 50, clamp01(dt / 0.3))
    return None


ev(j, k11_bad, bad11, "rim", 0.85)

# ================================================================ 屏 5：倒叙开头——日历一九九七年；画着刹车盘的工厂，“着了大火”时大火窜起
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k2_head, k2_cal, k2_fac = seq(j, [(6, 1, 0.45), (6, 1, 0.9), (6, 2, 0.5)], first=1)
KD5 = nx(j, wt(6, 3, 0.5), k2_fac)       # “着了大火”：大火窜起，员工往外跑
b.shots[j].shake, b.shots[j].flashes = [(KD5, 16.0)], [(KD5, 0.45)]
L.note("一九九七年", "先看结果")
ev(j, 0, tag_fn(j, "结果"), "clap", 0.8)
ev(j, k2_head, L.pop_text("先看结果", cx - 330, cy - 500, 64, RED, j, k2_head), "pop", 0.7)


def cal2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k2_cal))
    if sc <= 0:
        return None
    x, y = cx - 330, cy - 280
    with at_pop(c, x, y, sc):
        box(c, x, y, 330, 230, "#FFFFFF", BLACK, 6, 12)
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 165, y - 115, 330, 64), 12, 12, K.paint(RED))
        label(c, "一九九七年", x, y + 40, 62, BLACK)
    return None


ev(j, k2_cal, cal2, "wood_high", 0.75)


def fac2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k2_fac))
    if sc <= 0:
        return None
    x, y = cx + 80, cy + 360
    fire = T >= tb(5, KD5)
    with at_pop(c, x, y - 150, sc):
        c.drawLine(cx - 560, y, cx + 560, y, wb.marker(GRAY, 6))
        factory(c, x, y, 560, 330, "#FFFFFF")
        box(c, x - 60, y - 400, 190, 120, "#FFFFFF", BLACK, 5, 10)
        brake_disc(c, x - 60, y - 400, 44)
        if fire:
            dt = T - tb(5, KD5)
            g = C.slam_scale(dt)
            for n, (dx, h) in enumerate(((-180, 300), (20, 420), (210, 330))):
                with K.at(c, x + dx, y - 330, 0, g):
                    flame(c, 0, 0, h, T + n)
            for i in range(4):
                ph = ((T - tb(5, KD5)) * 0.6 + i * 0.25) % 1
                c.drawCircle(x + 120 + 60 * math.sin(i * 2 + T), y - 700 - ph * 200, 40 + 40 * ph, K.paint(GRAY, 0.35 * (1 - ph)))
    return None


ev(j, k2_fac, fac2, "wood_low", 0.75)


def run2(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(5, KD5)
    if dt < 0:
        return None
    x, dy, _ = C.walk(T, tb(5, KD5), 1.2, cx + 250, cx + 380, 16, 4)
    draw_worker(c, x, cy + 560 + dy, 0.65, mood="o", lh=(x - 60, cy + 300), rh=(x + 70, cy + 320))
    sweat(c, x - 50, cy + 300, 1.2)
    return None


ev(j, KD5, run2, "kick", 0.9)

# ================================================================ 屏 6：丰田生产线灯一盏盏熄灭、传送带停住“停了”；灯又亮回来，传送带转起来
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k3_line, k3_one, k3_off1, k3_off2, k3_on1, k3_on2 = seq(j, [None, (7, 1, 0.3), (7, 2, 0.6), (7, 3, 0.5), (8, 1, 0.2),
                                                           (8, 1, 0.8)])
L.note("只有它一家", "丰田生产线", "停了", "又转起来了")
ev(j, 0, tag_fn(j, "结果"))
LAMPS = [cx - 360 + 180 * i for i in range(5)]


def line3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k3_line))
    if sc <= 0:
        return None
    on_ = 5
    for i in range(5):
        if T >= tb(6, k3_off1) and i >= 3:
            on_ = min(on_, i)
        if T >= tb(6, k3_off2):
            on_ = 0
    if T >= tb(6, k3_on1):
        on_ = 3
    if T >= tb(6, k3_on2):
        on_ = 5
    stopped = tb(6, k3_off2) <= T < tb(6, k3_on1)
    with at_pop(c, cx, cy + 200, sc):
        label(c, "丰田生产线", cx - 300, cy - 260, 52, BLACK)
        C.line(c, (cx - 520, cy - 200), (cx + 540, cy - 200), BLACK, 9)
        for i, x in enumerate(LAMPS):
            lamp(c, x, cy - 130, i < on_)
        by = cy + 230
        box(c, cx, by, 1060, 60, "#C9CED6", BLACK, 7, 30)
        if T < tb(6, k3_off2):
            off = (T - tb(6, k3_line)) * 160
        elif T < tb(6, k3_on1):
            off = (tb(6, k3_off2) - tb(6, k3_line)) * 160
        else:
            off = (tb(6, k3_off2) - tb(6, k3_line)) * 160 + (T - tb(6, k3_on1)) * 160
        for i in range(10):
            xx = cx - 520 + ((i * 110 + off) % 1080)
            C.line(c, (xx, by - 20), (xx + 30, by + 20), GRAY, 5)
        for i in range(3):
            xx = cx - 520 + ((i * 360 + off) % 1080)
            car(c, xx, by - 30, 0.9, ("#7FB2E5", "#F28C8C", "#8FD19E")[i])
        hy = cy + 560 - 290 * 0.7
        draw_worker(c, cx + 380, cy + 560, 0.7, mood="sad" if stopped else "smile",
                    rh=(cx + 470, hy - 40) if T >= tb(6, k3_on2) else None)
    return None


ev(j, k3_line, line3, "wood_low", 0.7)


def one3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k3_one))
    if sc <= 0:
        return None
    x, y = cx - 360, cy - 360
    with at_pop(c, x, y, sc):
        factory(c, x - 60, y + 60, 200, 130, GRAY_FILL, chimney=False)
        brake_disc(c, x - 60, y - 20, 26)
        label(c, "只有它一家", x + 230, y, 54, RED)
    return None


ev(j, k3_one, one3, "pop", 0.7)
b.hit(j, k3_off1, "tom", 0.8, "灯熄了两盏")


def stop3(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k3_off2)
    if dt < 0:
        return None
    if T >= tb(6, k3_on1):
        g = 1 - ease_in_out(clamp01((T - tb(6, k3_on1)) / 0.25))
        if g <= 0:
            return None
    else:
        g = C.slam_scale(dt)
    with K.at(c, cx, cy + 20, -6, g):
        box(c, 0, 0, 260, 120, "#FFFFFF", RED, 9, 14)
        label(c, "停了", 0, 2, 80, RED)
    return None


ev(j, k3_off2, stop3, "rim", 0.85)


def go3(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(6, k3_on2)
    if dt < 0:
        return None
    g = pop_scale(dt)
    with K.at(c, cx - 40, cy + 20, 0, g):
        label(c, "又转起来了", 0, 0, 80, GREEN)
    sparkle(c, cx + 300, cy - 130, dt)
    return None


b.hit(j, k3_on1, "ding", 0.75, "灯亮回三盏")
ev(j, k3_on2, go3, "ding", 0.85)

# ================================================================ 屏 7：倒带键；地图上小工厂一家家亮灯，举着零件，箭头汇向丰田；夜里窗户都亮着
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k4_rw, k4_map, k4_w1, k4_w2, k4_moon = seq(j, [None, (10, 0, 0.5), (10, 1, 0.4), (10, 2, 0.5), (10, 4, 0.4)])
L.note("倒回去", "丰田", "连夜开工")
ev(j, 0, tag_fn(j, "起因", BLUE))


def rewind4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k4_rw))
    if sc <= 0:
        return None
    x, y = cx - 300, cy - 480
    with at_pop(c, x, y, sc):
        box(c, x - 60, y, 150, 110, "#FFFFFF", BLUE, 7, 22)
        for dx in (-30, 10):
            c.drawPath(P((x - 60 + dx + 30, y - 32), (x - 60 + dx - 10, y), (x - 60 + dx + 30, y + 32), close=True),
                       K.paint(BLUE))
        label(c, "倒回去", x + 150, y, 66, BLUE)
    return None


ev(j, k4_rw, rewind4, "shaker", 0.8)
SPOTS = [(cx - 400, cy - 160), (cx - 420, cy + 200), (cx - 150, cy + 330), (cx + 400, cy - 180), (cx + 420, cy + 190),
         (cx + 170, cy + 330), (cx - 200, cy - 270), (cx + 180, cy - 270)]


def map4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k4_map))
    if sc <= 0:
        return None
    night = T >= tb(7, k4_moon)
    with at_pop(c, cx, cy, sc):
        blob = P((cx - 540, cy - 260), (cx - 260, cy - 370), (cx + 120, cy - 350), (cx + 520, cy - 290), (cx + 560, cy + 60),
                 (cx + 470, cy + 400), (cx + 40, cy + 440), (cx - 420, cy + 400), (cx - 560, cy + 120), close=True)
        c.drawPath(blob, K.paint("#E8EDF7" if night else "#EEF2E4"))
        c.drawPath(blob, wb.marker(BLACK, 7))
        factory(c, cx, cy + 60, 230, 150, "#FFFFFF", chimney=False, lit=1.0 if night else 0.0)
        label(c, "丰田", cx, cy + 120, 52, RED)
        for n, (x, y) in enumerate(SPOTS):
            k_ = k4_w1 if n < 4 else k4_w2
            dt = T - tb(7, k_) - 0.08 * (n % 4)
            if dt < 0:
                continue
            g = pop_scale(dt)
            f = ease_out(clamp01(dt / 0.6))
            ax, ay = lerp(x, cx, 0.35), lerp(y, cy, 0.35)
            bx, by = lerp(x, cx, 0.35 + 0.35 * f), lerp(y, cy, 0.35 + 0.35 * f)
            C.line(c, (ax, ay), (bx, by), ORANGE, 7)
            with K.at(c, x, y, 0, g):
                factory(c, 0, 50, 130, 90, "#FFFFFF", chimney=False, lit=1.0)
                if n % 2 == 0:
                    brake_disc(c, 0, -45, 22)
                else:
                    gear(c, 0, -45, 22, T * 60)
    if night:
        dt = T - tb(7, k4_moon)
        g = pop_scale(dt)
        with K.at(c, cx + 140, cy - 460, 0, g):
            c.drawCircle(0, 0, 50, K.paint(YELLOW))
            c.drawCircle(22, -16, 44, K.paint(THEME["paper"]))
        with K.at(c, cx, cy + 530, 0, g):
            box(c, 0, 0, 320, 96, "#FFFFFF", BLUE, 6, 14)
            label(c, "连夜开工", 0, 2, 62, BLUE)
    return None


ev(j, k4_map, map4, "wood_low", 0.75)
b.hit(j, k4_w1, "pop", 0.8, "第一批小工厂亮灯")
b.hit(j, k4_w2, "pop", 0.8, "第二批小工厂亮灯")
b.hit(j, k4_moon, "ding", 0.8, "月亮升起、连夜开工")

# ================================================================ 屏 8：丰田组长和合作厂员工握手；时间轴“很多年”
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k5_two, k5_shake, k5_self, k5_years = seq(j, [None, (11, 1, 0.5), (12, 1, 0.7), (12, 2, 0.4)])
L.note("丰田", "合作厂", "自己人", "很多年")
ev(j, 0, tag_fn(j, "起因", BLUE))


def two5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k5_two))
    if sc <= 0:
        return None
    shook = T >= tb(8, k5_shake)
    with at_pop(c, cx, cy + 100, sc):
        factory(c, cx - 330, cy - 160, 300, 180, "#FFFFFF")
        label(c, "丰田", cx - 330, cy - 390, 56, RED)
        factory(c, cx + 330, cy - 160, 300, 180, "#FFFFFF")
        label(c, "合作厂", cx + 330, cy - 390, 56, BLUE)
        hy = cy + 340 - 290 * 0.85
        bob = 10 * math.sin((T - tb(8, k5_shake)) * 14) if shook else 0.0
        hx = cx
        draw_leader2(c, cx - 160, cy + 340, 0.85, mood="smile", rh=(hx - 10, hy + 110 + bob) if shook else None)
        draw_worker(c, cx + 160, cy + 340, 0.85, mood="smile", lh=(hx + 10, hy + 110 + bob) if shook else None)
        if shook:
            c.drawCircle(hx, hy + 110 + bob, 18, K.paint("#F6D9C2"))
            c.drawCircle(hx, hy + 110 + bob, 18, wb.marker(BLACK, 5))
    return None


ev(j, k5_two, two5, "wood_low", 0.75)
b.hit(j, k5_shake, "clap", 0.8, "握手")


def self5(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k5_self)
    if dt < 0:
        return None
    g = pop_scale(dt)
    with K.at(c, cx, cy - 300, wobble(dt, 6, 16, 5), g):
        heart(c, 0, 0, 60)
        label(c, "自己人", 0, 110, 64, RED)
    return None


ev(j, k5_self, self5, "pop", 0.8)


def years5(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(8, k5_years)
    if dt < 0:
        return None
    f = ease_out(clamp01(dt / 0.9))
    y = cy + 470
    x0, x1 = cx - 520, cx - 520 + 1040 * f
    C.line(c, (x0, y), (x1, y), GREEN, 10)
    for i in range(12):
        xx = cx - 500 + i * 90
        if xx <= x1:
            C.line(c, (xx, y - 18), (xx, y + 18), GREEN, 6)
    if f > 0.6:
        label(c, "很多年", cx + 360, y - 60, 56, GREEN, alpha=clamp01((f - 0.6) / 0.3))
    return None


ev(j, k5_years, years5, "shaker", 0.75)

# ================================================================ 屏 9：台阶“价格”“质量”年年往上；丰田派人进对方工厂一起拧扳手
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k6_steps, k6_tags, k6_walk, k6_fix, k6_fix2 = seq(j, [None, (13, 1, 0.5), (14, 1, 0.3), (14, 2, 0.4), None])
L.note("价格", "质量", "年年进步", "一起改")
ev(j, 0, tag_fn(j, "起因", BLUE))


def steps6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k6_steps))
    if sc <= 0:
        return None
    x0, y0 = cx - 540, cy - 40
    with at_pop(c, x0 + 250, y0 - 200, sc):
        pts = [(x0, y0)]
        for i in range(4):
            pts += [(x0 + i * 130, y0 - (i + 1) * 90), (x0 + (i + 1) * 130, y0 - (i + 1) * 90)]
        pts += [(x0 + 520, y0)]
        c.drawPath(P(*pts, close=True), K.paint(GRAY_FILL))
        c.drawPath(P(*pts, close=True), wb.marker(BLACK, 7))
        c.drawPath(wb.arrow((x0 + 40, y0 - 160), (x0 + 450, y0 - 470), 0.15, 40), wb.marker(RED, 8))
        if T >= tb(9, k6_tags):
            g = pop_scale(T - tb(9, k6_tags))
            with K.at(c, x0 + 130, y0 - 230, 0, g):
                label(c, "价格", 0, 0, 52, RED)
            with K.at(c, x0 + 390, y0 - 410, 0, pop_scale(T - tb(9, k6_tags) - 0.12)):
                label(c, "质量", 0, 0, 52, RED)
            with K.at(c, x0 + 330, y0 - 520, 0, pop_scale(T - tb(9, k6_tags) - 0.24)):
                label(c, "年年进步", 0, 0, 46, GRAY)
    return None


ev(j, k6_steps, steps6, "wood_low", 0.75)
b.hit(j, k6_tags, "pop", 0.8, "价格、质量两块牌子")


def fix6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k6_walk))
    if sc <= 0:
        return None
    fx, fy = cx + 280, cy + 520
    factory(c, fx, cy - 30, 520, 300, "#FFFFFF")
    label(c, "合作厂", fx - 120, cy - 400, 50, BLUE)
    box(c, fx, fy - 150, 240, 150, "#C9CED6", BLACK, 6, 10)
    gear(c, fx, fy - 150, 40, (T - tb(9, k6_fix)) * 140 if T >= tb(9, k6_fix) else 0)
    x, dy, _ = C.walk(T, tb(9, k6_walk), 0.9, cx - 420, fx - 230, 14, 3)
    hy = fy - 290 * 0.75
    working = T >= tb(9, k6_fix)
    turn = 25 * math.sin((T - tb(9, k6_fix)) * 8) if working else 0
    draw_leader2(c, x, fy + dy, 0.75, mood="smile", rh=(fx - 110, fy - 170) if working else None)
    draw_worker(c, fx + 230, fy, 0.75, mood="smile" if working else "flat", lh=(fx + 110, fy - 170) if working else None)
    if working:
        wrench(c, fx - 100, fy - 180, -60 + turn, 0.6)
        wrench(c, fx + 100, fy - 180, 60 - turn, 0.6)
    if T >= tb(9, k6_fix2):
        g = pop_scale(T - tb(9, k6_fix2))
        with K.at(c, fx, fy - 330, 0, g):
            box(c, 0, 0, 230, 84, "#FFFFFF", GREEN, 6, 14)
            label(c, "一起改", 0, 2, 54, GREEN)
    return None


ev(j, k6_walk, fix6, "wood_low", 0.75)
b.hit(j, k6_fix, "rim", 0.85, "两把扳手一起拧")
b.hit(j, k6_fix2, "ding", 0.8, "一起改")

# ================================================================ 屏 10：“挑战”“帮助”两张卡；一群人一起扛起大梁
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k7_c1, k7_c2, k7_ppl, k7_lift = seq(j, [(15, 0, 0.8), (15, 1, 0.5), (16, 0, 0.4), (16, 1, 0.4)])
L.note("挑战", "帮助", "一起扛")


def card7(n, k):
    def fn(c, kk, T, cx=cx, cy=cy):
        dt = T - tb(10, k)
        if dt < 0:
            return None
        g = pop_scale(dt)
        x, y = (cx - 260, cy - 300) if n == 0 else (cx + 260, cy - 300)
        with K.at(c, x, y, (-4 if n == 0 else 4) + wobble(dt, 4, 14, 5), g):
            box(c, 0, 0, 400, 300, "#FFFFFF", RED if n == 0 else GREEN, 9, 24)
            if n == 0:
                c.drawPath(wb.arrow((-80, 60), (60, -70), 0.1, 40), wb.marker(RED, 12))
                c.drawPath(P((-130, 80), (-60, 80), (-60, 20), (10, 20), (10, -40)), wb.marker(BLACK, 6))
            else:
                c.drawRoundRect(skia.Rect.MakeXYWH(-110, -60, 120, 70), 30, 30, K.paint("#F6D9C2"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-110, -60, 120, 70), 30, 30, wb.marker(BLACK, 6))
                c.drawRoundRect(skia.Rect.MakeXYWH(-10, -40, 120, 70), 30, 30, K.paint("#F6D9C2"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-10, -40, 120, 70), 30, 30, wb.marker(BLACK, 6))
            label(c, "挑战" if n == 0 else "帮助", 0, 100, 72, RED if n == 0 else GREEN)
        return None
    return fn


ev(j, k7_c1, card7(0, k7_c1), "rim", 0.8)
ev(j, k7_c2, card7(1, k7_c2), "pop", 0.8)


def beam7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k7_ppl))
    if sc <= 0:
        return None
    lift = ease_out(clamp01((T - tb(10, k7_lift)) / 0.4)) if T >= tb(10, k7_lift) else 0.0
    gy = cy + 560
    s = 0.6
    with at_pop(c, cx, gy - 150, sc):
        by = gy - 290 * s - 70 - 60 * lift + wobble(T - tb(10, k7_lift), 4, 20, 6)
        xs = [cx - 400, cx - 200, cx, cx + 200, cx + 400]
        for n, x in enumerate(xs):
            hy = gy - 290 * s
            hand_y = by + 24
            draw = draw_worker if n % 2 == 0 else draw_leader2
            if draw is draw_worker:
                draw_worker(c, x, gy, s, lh=(x - 30, hand_y), rh=(x + 30, hand_y), mood="smile" if lift > 0.5 else "flat")
            else:
                draw_leader2(c, x, gy, s, rh=(x + 30, hand_y), lh=(x - 30, hand_y), mood="smile" if lift > 0.5 else "frown")
        box(c, cx, by, 1060, 46, "#D7B98E", WOOD_LINE, 7, 8)
        if lift > 0.5:
            label(c, "一起扛", cx, cy - 20, 74, GREEN, alpha=clamp01((lift - 0.5) * 2))
    return None


ev(j, k7_ppl, beam7, "wood_low", 0.75)
b.hit(j, k7_lift, "kick", 0.85, "一起扛起大梁")
b.shots[j].shake = [(k7_lift, 7.0)]

# ================================================================ 屏 11：左边换掉一个人，新人头上又冒“老问题”；右边帮对方补好缺口，变成“靠得住”
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k8_q, k8_swap, k8_gear, k8_old, k8_patch, k8_ok = seq(j, [None, (18, 0, 0.5), (18, 1, 0.5), (18, 2, 0.5), (19, 0, 0.5),
                                                          (19, 1, 0.7)])
L.note("换掉？", "从头磨合", "老问题", "靠得住")
ev(j, k8_q, L.pop_text("换掉？", cx, cy - 500, 80, RED, j, k8_q), "rim", 0.8)


def left8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k8_swap))
    if sc <= 0:
        return None
    x, gy = cx - 280, cy + 380
    with at_pop(c, x, gy - 150, sc):
        dashed(c, (cx, cy - 400), (cx, cy + 560), GRAY, 5)
        f = ease_out(clamp01((T - tb(11, k8_swap)) / 0.6))
        draw_designer(c, x - 120 - 120 * f, gy, 0.7, mood="sad", alpha=1 - 0.6 * f)
        xmark(c, x - 120 - 120 * f, gy - 200, 50, f)
        draw_wang(c, x + 120, gy, 0.7, mood="o" if T >= tb(11, k8_old) else "flat", alpha=f)
        if T >= tb(11, k8_gear):
            rot = (T - tb(11, k8_gear)) * 90
            gear(c, x - 40, gy - 420, 44, rot)
            gear(c, x + 40, gy - 400, 34, -rot * 1.3)
            label(c, "从头磨合", x, gy - 520, 52, GRAY)
        if T >= tb(11, k8_old):
            dt = T - tb(11, k8_old)
            g = C.slam_scale(dt)
            with K.at(c, x + 120, gy - 310, 0, g):
                box(c, 0, 0, 220, 80, RED_FILL, RED, 6, 30)
                label(c, "老问题", 0, 2, 50, RED)
    return None


ev(j, k8_swap, left8, "wood_high", 0.75)
b.hit(j, k8_gear, "shaker", 0.75, "齿轮磨合")
b.hit(j, k8_old, "tom", 0.85, "老问题又冒出来")


def right8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k8_patch))
    if sc <= 0:
        return None
    x, gy = cx + 290, cy + 380
    dt = T - tb(11, k8_patch)
    with at_pop(c, x, gy - 150, sc):
        wall = P((x - 220, gy - 420), (x + 220, gy - 420), (x + 220, gy - 280), (x - 220, gy - 280), close=True)
        c.drawPath(wall, K.paint(GRAY_FILL))
        c.drawPath(wall, wb.marker(BLACK, 6))
        f = ease_out(clamp01(dt / 0.5))
        with K.at(c, x, gy - 350 - 80 * (1 - f)):
            box(c, 0, 0, 120, 100, GREEN_FILL, GREEN, 6, 4)
        hy = gy - 290 * 0.7
        draw_li(c, x - 150, gy, 0.7, "smile", rh=(x - 60, gy - 350 + 40 * (1 - f)))
        ok = T >= tb(11, k8_ok)
        draw_designer(c, x + 150, gy, 0.7, mood="smile" if ok else "flat")
        if ok:
            g = pop_scale(T - tb(11, k8_ok))
            with K.at(c, x + 30, gy - 520, 0, g):
                box(c, 0, 0, 240, 84, "#FFFFFF", GREEN, 7, 30)
                label(c, "靠得住", 0, 2, 54, GREEN)
            tick(c, x + 210, gy - 330, 34, clamp01((T - tb(11, k8_ok)) / 0.3))
    return None


ev(j, k8_patch, right8, "wood_low", 0.75)
b.hit(j, k8_ok, "ding", 0.85, "变成靠得住")

# ================================================================ 屏 12：领导对小李皱眉，小李夹在中间；大字“三步”
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k12_boss, k12_mid, k12_p, k12_3 = seq(j, [None, (20, 1, 0.5), (20, 2, 0.3), (21, 1, 0.3)])
L.note("怎么又晚了？", "等等我")


def boss12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k12_boss))
    if sc <= 0:
        return None
    gy = cy + 540
    hy = gy - 290 * 0.85
    poke = 16 * math.sin(T * 10)
    with at_pop(c, cx - 380, gy - 150, sc):
        draw_boss(c, cx - 400, gy, 0.85, mood="sad", rh=(cx - 280 + poke, hy + 40))
        bubble_text(c, "怎么又晚了？", cx - 300, cy - 160, 52, RED, 1)
    return None


ev(j, k12_boss, boss12, "tom", 0.8)


def mid12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k12_mid))
    if sc <= 0:
        return None
    gy = cy + 540
    sq = 1 - 0.1 * ease_out(clamp01((T - tb(12, k12_p)) / 0.3)) if T >= tb(12, k12_p) else 1.0
    with at_pop(c, cx, gy - 150, sc):
        draw_li(c, cx, gy, 0.85, "sad", squash=sq)
        sweat(c, cx + 60, gy - 330, 1.3)
    return None


ev(j, k12_mid, mid12, "wood_low", 0.75)


def p12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k12_p))
    if sc <= 0:
        return None
    gy = cy + 540
    with at_pop(c, cx + 380, gy - 150, sc):
        draw_designer(c, cx + 400, gy, 0.85, mood="flat")
        bubble_text(c, "等等我", cx + 380, cy - 40, 52, BLACK, -1)
    return None


ev(j, k12_p, p12, "pop", 0.75)
ev(j, k12_3, L.slam_text("三步", cx + 60, cy - 400, 170, RED, j, k12_3, rot=-4), "kick", 0.9)
b.shots[j].shake = [(k12_3, 9.0)]

# ================================================================ 屏 13：做法一——需求单写清楚几行，旁边贴一张“参考样子”
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k13_n, k13_rows, k13_ref, k13_li = seq(j, [None, (22, 1, 0.3), (22, 2, 0.4), (22, 2, 0.9)])
L.note("第一", "需求单", "给谁看", "放在哪", "哪天要", "参考样子")
pop(j, k13_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: label(c, "第一", cx - 380, cy - 470, 90, RED), "rim", 0.8)
ROWS13 = ["给谁看", "放在哪", "哪天要"]


def sheet13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k13_rows))
    if sc <= 0:
        return None
    x, y = cx - 170, cy - 60
    with at_pop(c, x, y, sc):
        box(c, x, y, 480, 560, "#FFFFFF", BLACK, 7, 14)
        label(c, "需求单", x, y - 220, 56, BLACK)
        for i, s_ in enumerate(ROWS13):
            dt = T - tb(13, k13_rows) - 0.25 * i
            if dt < 0:
                continue
            yy = y - 110 + i * 120
            label(c, s_, x - 80, yy, 48, BLUE, alpha=clamp01(dt / 0.15))
            tick(c, x + 140, yy, 26, clamp01(dt / 0.25), GREEN, 9)
    return None


ev(j, k13_rows, sheet13, "wood_high", 0.75)


def ref13(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(13, k13_ref)
    if dt < 0:
        return None
    g = pop_scale(dt)
    x, y = cx + 300, cy - 150
    with K.at(c, x, y, 6 + wobble(dt, 5, 14, 5), g):
        box(c, 0, 0, 280, 320, "#FFFFFF", ORANGE, 8, 8)
        c.drawRect(skia.Rect.MakeXYWH(-110, -120, 220, 150), K.paint(BLUE_FILL))
        c.drawCircle(60, -80, 26, K.paint(YELLOW))
        c.drawPath(P((-110, 30), (-40, -50), (20, 10), (60, -20), (110, 30), close=True), K.paint(GREEN_FILL))
        label(c, "参考样子", 0, 100, 48, ORANGE)
        c.drawRect(skia.Rect.MakeXYWH(-40, -175, 80, 34), K.paint("#F2E3A0", 0.9))
    return None


ev(j, k13_ref, ref13, "pop", 0.8)
ev(j, k13_li, L.figure(draw_li, j, k13_li, cx - 420, cy + 560, 0.75, mood="smile", rh=(cx - 320, cy + 300)), "wood_low", 0.7)

# ================================================================ 屏 14：做法二——小李走到对方桌边，“卡在哪？”“我能帮什么？”
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k14_n, k14_walk, k14_q1, k14_q2 = seq(j, [None, (23, 0, 0.6), (23, 1, 0.7), (23, 2, 0.4)])
L.note("第二", "卡在哪？", "我能帮什么？")
pop(j, k14_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: label(c, "第二", cx - 380, cy - 470, 90, RED), "rim", 0.8)


def walk14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k14_walk))
    if sc <= 0:
        return None
    desk(c, cx + 250, cy + 290, 440)
    monitor(c, cx + 250, cy + 110, 300, 200)
    hy = cy + 560 - 290 * 0.8
    draw_designer(c, cx + 430, cy + 560, 0.8, mood="smile" if T >= tb(14, k14_q2) else "flat",
                  lh=(cx + 360, cy + 300))
    x, dy, _ = C.walk(T, tb(14, k14_walk), 0.9, cx - 520, cx - 120, 14, 3)
    draw_li(c, x, cy + 560 + dy, 0.85, "smile")
    return None


ev(j, k14_walk, walk14, "wood_low", 0.7)
ev(j, k14_q1, L.pop_bubble("卡在哪？", cx - 220, cy - 200, j, k14_q1, 62, BLUE, tail=-1), "pop", 0.8)
ev(j, k14_q2, L.pop_bubble("我能帮什么？", cx - 80, cy - 380, j, k14_q2, 62, BLUE, tail=-1), "bongo_high", 0.8)

# ================================================================ 屏 15：做法三——当面竖大拇指；再给对方领导发一条“谢谢”
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k15_n, k15_th, k15_ph, k15_boss = seq(j, [None, (24, 2, 0.3), (24, 3, 0.3), (24, 3, 0.8)])
L.note("第三", "做得好", "谢谢", "他的领导")
pop(j, k15_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: label(c, "第三", cx - 380, cy - 470, 90, RED), "rim", 0.8)


def th15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k15_th))
    if sc <= 0:
        return None
    gy = cy + 560
    with at_pop(c, cx - 200, gy - 150, sc):
        hy = gy - 290 * 0.8
        draw_li(c, cx - 400, gy, 0.8, "smile", rh=(cx - 290, hy - 10))
        thumb(c, cx - 270, hy - 40, 0.8)
        draw_designer(c, cx - 70, gy, 0.8, mood="smile")
        bubble_text(c, "做得好", cx - 330, cy - 120, 56, GREEN, 1)
    return None


ev(j, k15_th, th15, "clap", 0.85)


def ph15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k15_ph))
    if sc <= 0:
        return None
    x, y = cx + 120, cy - 320
    with at_pop(c, x, y, sc):
        phone(c, x, y, 190, 320)
        box(c, x, y - 20, 140, 70, GREEN_FILL, GREEN, 4, 16)
        label(c, "谢谢", x, y - 18, 42, GREEN)
        f = clamp01((T - tb(15, k15_ph)) / 0.8)
        ex, ey = lerp(x + 100, cx + 380, ease_out(f)), lerp(y, cy - 120, ease_out(f))
        c.drawPath(P((ex - 34, ey - 22), (ex + 34, ey - 22), (ex + 34, ey + 22), (ex - 34, ey + 22), close=True),
                   K.paint("#FFFFFF"))
        c.drawPath(P((ex - 34, ey - 22), (ex + 34, ey - 22), (ex + 34, ey + 22), (ex - 34, ey + 22), close=True),
                   wb.marker(BLACK, 5))
        c.drawPath(P((ex - 34, ey - 22), (ex, ey + 4), (ex + 34, ey - 22)), wb.marker(BLACK, 5))
    return None


ev(j, k15_ph, ph15, "pop", 0.8)


def boss15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k15_boss))
    if sc <= 0:
        return None
    gy = cy + 560
    with at_pop(c, cx + 380, gy - 150, sc):
        hy = gy - 290 * 0.8
        nod = 8 * math.sin((T - tb(15, k15_boss)) * 9)
        draw_boss(c, cx + 380, gy, 0.8, mood="smile", head_dy=nod)
        label(c, "他的领导", cx + 380, gy - 330, 44, GRAY)
    return None


ev(j, k15_boss, boss15, "ding", 0.8)

# ================================================================ 屏 16：链子重新接好，两头的小人一起往前走
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
k16_ch, k16_join, k16_walk, k16_ok = seq(j, [None, (25, 0, 0.6), (25, 1, 0.3), (25, 1, 0.9)])
L.note("顺了")


def chain16(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(16, k16_ch))
    if sc <= 0:
        return None
    joined = T >= tb(16, k16_join)
    gap = 1.0 if not joined else 1 - ease_out(clamp01((T - tb(16, k16_join)) / 0.3))
    walking = T >= tb(16, k16_walk)
    off = (T - tb(16, k16_walk)) * 120 if walking else 0.0
    off = min(off, 220)
    gy = cy + 400
    with at_pop(c, cx, cy, sc):
        C.line(c, (cx - 560, gy), (cx + 560, gy), GRAY, 6)
        for i in range(6):
            xx = cx - 540 + ((i * 200 - off * 2) % 1100)
            C.line(c, (xx, gy + 30), (xx + 60, gy + 30), GRAY, 4)
        y = cy + 160
        chain_row(c, cx - 380 + off * 0.2, cx + 380 + off * 0.2, y, gap, color=GREEN if joined else BLACK)
        bob = -abs(math.sin((T - tb(16, k16_walk)) * 6)) * 12 if walking else 0.0
        draw_li(c, cx - 470 + off * 0.2, gy + bob, 0.8, "smile", rh=(cx - 400 + off * 0.2, y + 20))
        draw_designer(c, cx + 470 + off * 0.2, gy + bob, 0.8, mood="smile", lh=(cx + 400 + off * 0.2, y + 20))
        if gap == 0:
            sparkle(c, cx + off * 0.2, y, T - tb(16, k16_join) - 0.3)
        if T >= tb(16, k16_ok):
            g = pop_scale(T - tb(16, k16_ok))
            with K.at(c, cx, cy - 250, 0, g):
                label(c, "顺了", 0, 0, 150, GREEN)
    return None


ev(j, k16_ch, chain16, "wood_low", 0.7)
b.hit(j, k16_join, "clap", 0.85, "链子接好")
b.hit(j, k16_walk, "shaker", 0.7, "一起往前走")
b.hit(j, k16_ok, "ding", 0.8, "顺了")

# ================================================================ 屏 17：评论区头疼的合作方；小李拉人一把，后来他摔倒，一群人来扶；下一讲预告
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
k17_cb, k17_g, k17_help, k17_fall, k17_nx = seq(j, [None, (27, 0, 0.4), (28, 0, 0.5), (28, 2, 0.3), (29, 0, 0.2)])
GRIPES = [("改五遍的外包", cx - 280, cy - 440), ("总拖的隔壁", cx + 270, cy - 440), ("越催越慢的师傅", cx, cy - 345)]
L.note("哪种合作方最头疼？", *[g[0] for g in GRIPES], "下一讲", "新工具一个接一个", "活怎么没少？")


def cb17(c, T, cx=cx, cy=cy):
    comment_box(c, cx, cy - 420, 1060, 300)
    label(c, "哪种合作方最头疼？", cx - 80, cy - 525, 50, RED)


pop(j, k17_cb, cx, cy - 420, cb17, "wood_high", 0.7)
for n, (s_, x, y) in enumerate(GRIPES):
    ev(j, k17_g, L.pop_text(s_, x, y, 52, BLACK, j, k17_g + 0.15 * n), "pop" if n == 0 else None, 0.6)


def help17(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(17, k17_help))
    if sc <= 0:
        return None
    gy = cy + 250
    fallen = T >= tb(17, k17_fall)
    with at_pop(c, cx, gy - 100, sc):
        C.line(c, (cx - 540, gy), (cx + 540, gy), GRAY, 5)
        if not fallen:
            f = ease_out(clamp01((T - tb(17, k17_help)) / 0.6))
            hy = gy - 290 * 0.72
            draw_li(c, cx - 120, gy, 0.72, "smile", rh=(cx - 40, hy + 60 - 30 * f))
            with K.at(c, cx + 60, gy, -70 * (1 - f)):
                draw_designer(c, 0, 0, 0.72, mood="smile" if f > 0.8 else "o", lh=(-80, -290 * 0.72 + 60 - 30 * f))
        else:
            dt = T - tb(17, k17_fall)
            with K.at(c, cx - 60, gy, -80):
                draw_li(c, 0, 0, 0.72, "o")
            for n, (sx, mood) in enumerate(((cx - 450, "smile"), (cx + 330, "smile"), (cx + 470, "smile"))):
                x, dy, _ = C.walk(T, tb(17, k17_fall) + 0.1 * n, 0.8, sx, lerp(sx, cx - 60, 0.6), 10, 3)
                draw = (draw_designer, draw_wang, draw_worker)[n]
                draw(c, x, gy + dy, 0.66, mood=mood)
            if dt > 0.8:
                heart(c, cx - 60, gy - 300, 40)
    return None


ev(j, k17_help, help17, "wood_low", 0.7)
b.hit(j, k17_fall, "tom", 0.8, "小李摔倒，大家跑来扶")


def next17(c, kk, T, cx=cx, cy=cy):
    t0 = tb(17, k17_nx)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 420, sc):
        box(c, cx, cy + 420, 1000, 260, "#FFFFFF", BLUE, 8, 24)
        label(c, "下一讲", cx + 120, cy + 335, 46, BLUE)
        label(c, "新工具一个接一个", cx + 120, cy + 415, 58, BLACK)
        label(c, "活怎么没少？", cx + 120, cy + 495, 58, BLACK)
        for i, col in enumerate(("#5B8DEF", "#F28C5B", "#7BC67E")):
            g = pop_scale(T - t0 - 0.2 - 0.15 * i)
            if g > 0:
                with K.at(c, cx - 400 + i * 70, cy + 420 + (i % 2) * 40 - 20, 0, g):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-30, -30, 60, 60), 14, 14, K.paint(col))
                    c.drawRoundRect(skia.Rect.MakeXYWH(-30, -30, 60, 60), 14, 14, wb.marker(BLACK, 4))
    return None


ev(j, k17_nx, next17, "wood_high", 0.75)

# ================================================================ 收尾
L.finish(cover_shot=5, square_shot=9, notes=NOTES)
L.export(globals())
