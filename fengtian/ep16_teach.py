"""《丰田模式》16 教人：新人教了三遍，怎么还是不会？（白板手绘 + AI 旁白，竖屏 2:3）

对话改写：同一段“带新人”拍两遍（2026-11 新结构：先痛点和身边的例子，再回放原来那段）。原来那段开头打一块场记板“第一遍”，讲完丰田带新人的四步，场记板翻成“改写版”，
同一张桌子、同一份活再演一遍；改写版每屏右上角一张四格进度卡（一二三四），做到哪一步亮哪一格。
- 开场（qmarks）：小李讲第 1、2、3 遍，小周头顶的问号一个比一个大，“又错了”；
- 日常：小李第三次指着屏幕讲，气泡越来越大；小周交上来的文件一个红叉；小李心里嘀咕“这么简单”；
- 身边的例子：交接时扔过去一个文件夹“都在里面了”；教爸妈手机挂号，手指在屏幕上飞，爸妈摆手“算了”（drop）；
- 第一遍：场记板“第一遍”拍下；小李的鼠标快成一团残影，“这样，再这样，懂了吧？”砸下；
  小周点头说懂了，日历翻到第二天，桌上三个红叉；
- 书中做法：车间组长带新员工（戴安全帽），牌子上四个空格，“学的人没学会 / 就当是教的人没教会”；组长自己拧螺丝，
  再转身教人，“懂这份活”“会教别人”两个勾；
- 改写版：场记板翻成“改写版”，四格进度卡；第一步拉椅子坐下，纸上画出这份活用在哪、做错会怎样；第二步慢慢做，
  每步弹出“为什么”；第三步换小周操作，边做边说，错一处当场改成勾；第四步小李回座位，钟走一阵回来看，小周举手“找你”；
  结果：第二天小周交出一个勾，还问“为什么要这样？”；
- 为什么：小李闭着眼都会的一串步骤里有两步是虚线（忘了讲）；耳朵听的字往外漏，手做过的一步留在脑子里；
- 说回我们：小李桌上一摞自己的活、旁边站着等着学的新人，“三步”；三步做法（先画“用在哪”再画“怎么做” / 两人轮流做给对方看 /
  第二天走到桌边问“卡在哪了？”）；海边躺椅上手机很安静，工位上小周顺利接手；
- 收尾：评论区“谢谢某某”；多年后小周带着新人，墙上挂着小李的照片；下一讲预告（一条链子断了一节）。
小李 common.draw_li；新人小周 scenekit.draw_zhou（短卷发、圆框眼镜、绿卫衣、“新”字工牌，不戴安全帽）；
车间组长 scenekit.draw_leader2、车间新员工 common.draw_worker（戴安全帽）；爸妈 scenekit.draw_mom / draw_dad。
文案见 fengtian/PLAN.md「### 16」；时间轴、配乐、相机、人物见 fengtian/common.py，小工具见 fengtian/scenekit.py。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_li, draw_worker, pop_scale, wobble
from fengtian.scenekit import (GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL, NOTE_FILL, ORANGE_FILL, WOOD, WOOD_LINE,
                               Kit, at_pop, box, bubble_text, clock_face, comment_box, dashed, dashed_rect, desk,
                               draw_dad, draw_leader2, draw_mom, draw_zhou, head_of, heart, laptop, paper, phone, qmark,
                               sparkle, sweat, tick, xmark)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)；句子分组与 PLAN 的 SCREENS_DRAFT 一致
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "身边的例子", 2),
    ([4], "身边的例子", 3),
    ([5, 6], "回放 · 原来那一段", 4),
    ([7], "回放 · 原来那一段", 5),
    ([8, 9], "丰田模式 · 书中做法", 6),
    ([10], "丰田模式 · 书中做法", 7),
    ([11, 12], "改写 · 第一步", 8),
    ([13], "改写 · 第二步", 9),
    ([14], "改写 · 第三步", 10),
    ([15], "改写 · 第四步", 11),
    ([16], "改写 · 结果", 12),
    ([17, 18, 19], "为什么做一遍更好", 13),
    ([20, 21], "说回我们自己", 14),
    ([22], "做法一 · 示意", 15),
    ([23], "做法二 · 示意", 16),
    ([24], "做法三 · 示意", 17),
    ([25], "放心休假", 18),
    ([26, 27, 28, 29], "评论区见", 19),
]

THEME = FT.get("16")          # 本讲样式：深褐黑板、开场 qmarks、转场 drop
L = C.Lesson("16", SCREENS, drop_screen=3, board_size=(5000, 12800), theme=THEME, extra_hold={17: 0.8})
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
    "本讲依据：原则 9——培养懂工作、践行理念、能教别人的领导；原则 10 一章讲到的带人方法（工作教导四步：讲清用途、"
    "做给他看并讲为什么、让他做并说给你听、放手后跟进；“学的人没学会，就当是教的人没教会”，出处待核）。",
    "表格、文件夹、手机挂号为示意；小李、小周、组长、家人为虚构人物。",
]

STEP_NAMES = ["一", "二", "三", "四"]
L.note(*STEP_NAMES)


# ================================================================ 本讲道具

def clapper(c, x, y, label, open_=0.0, alpha=1.0, color=RED):
    """场记板：(x, y) 为板身中心；open_ 0–1 为拍杆张开角度。"""
    w, h = 300, 170
    box(c, x, y, w, h, "#2B2B30", BLACK, 6, 8, alpha)
    K.text(c, label, x, y + 18, 64, "hand", "#FFFFFF", alpha)
    with K.at(c, x - w / 2, y - h / 2, -28 * open_):
        c.drawRect(skia.Rect.MakeXYWH(0, -46, w, 46), K.paint("#FFFFFF", alpha))
        for i in range(6):
            c.drawPath(P((i * 52, -46), (i * 52 + 26, -46), (i * 52 + 10, 0), (i * 52 - 16, 0), close=True), K.paint("#2B2B30", alpha))
        c.drawRect(skia.Rect.MakeXYWH(0, -46, w, 46), wb.marker(BLACK, 5, alpha))


def clap_fn(j, k, x, y, label, color=RED):
    """第 j 屏第 k 拍：场记板张开后拍下。"""
    def fn(c, kk, T):
        dt = T - tb(j, k)
        if dt < -0.35:
            return None
        sc = pop_scale(dt + 0.35)
        op = clamp01(-dt / 0.3) if dt < 0 else 0.0
        with K.at(c, x, y, wobble(dt, 3, 20, 6), sc):
            clapper(c, 0, 0, label, op, color=color)
        return None
    return fn


L.note("第一遍", "改写版")


def steps_card(c, x, y, n_on, T=0.0, glow_t=None):
    """改写版右上角的四格进度卡：前 n_on 格亮起。"""
    box(c, x, y, 380, 110, "#FFFFFF", BLACK, 6, 16)
    for i in range(4):
        on = i < n_on
        cx_ = x - 135 + i * 90
        box(c, cx_, y, 76, 76, GREEN_FILL if on else GRAY_FILL, GREEN if on else GRAY, 5, 12)
        K.text(c, STEP_NAMES[i], cx_, y + 2, 50, "hand", GREEN if on else GRAY)
    if glow_t is not None and 0 <= glow_t < 0.8:
        i = n_on - 1
        sparkle(c, x - 135 + i * 90, y, glow_t, YELLOW, 8, 40, 90)


def step_card_fn(j, n_on, k_on):
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, 0))
        if sc <= 0:
            return None
        cx_, cy_ = R[j]
        lit = n_on if T >= tb(j, k_on) else n_on - 1
        with at_pop(c, cx_ + 330, cy_ - 480, sc):
            steps_card(c, cx_ + 330, cy_ - 480, lit, T, T - tb(j, k_on))
        return None
    return fn


def monitor(c, x, y, w=300, h=200, screen="#FFFFFF", alpha=1.0):
    box(c, x, y, w, h, "#2B2B30", BLACK, 7, 10, alpha)
    box(c, x, y, w - 24, h - 24, screen, GRAY, 3, 6, alpha)
    C.line(c, (x, y + h / 2), (x, y + h / 2 + 40), BLACK, 10, alpha)
    C.line(c, (x - 60, y + h / 2 + 42), (x + 60, y + h / 2 + 42), BLACK, 10, alpha)


def mouse_blur(c, x, y, T, alpha=1.0):
    for i in range(6):
        ox = 50 * math.sin(T * 25 + i)
        oy = 30 * math.cos(T * 21 + i * 2)
        c.drawOval(skia.Rect.MakeXYWH(x + ox - 26, y + oy - 36, 52, 72), K.paint("#C9CED6", 0.25 * alpha))
    c.drawOval(skia.Rect.MakeXYWH(x - 26, y - 36, 52, 72), K.paint("#FFFFFF", alpha))
    c.drawOval(skia.Rect.MakeXYWH(x - 26, y - 36, 52, 72), wb.marker(BLACK, 5, alpha))


def calendar_page(c, x, y, w, h, title, alpha=1.0, flip=1.0):
    box(c, x, y, w, h, "#FFFFFF", BLACK, 6, 10, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h * 0.26), 10, 10, K.paint(RED, alpha))
    K.text(c, title, x, y + h * 0.12, h * 0.26, "hand", BLACK, alpha)
    if flip < 1:
        c.save()
        c.translate(x, y - h / 2 + h * 0.26)
        c.scale(1, 1 - flip)
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, 0, w, h * 0.74), K.paint("#FFFFFF", alpha))
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, 0, w, h * 0.74), wb.marker(BLACK, 4, alpha))
        c.restore()


def chair(c, x, y, alpha=1.0):
    """椅子（侧视）：(x, y) 为地面中点。"""
    C.line(c, (x - 60, y - 120), (x + 60, y - 120), WOOD_LINE, 12, alpha)
    C.line(c, (x - 60, y - 120), (x - 60, y), WOOD_LINE, 9, alpha)
    C.line(c, (x + 60, y - 120), (x + 60, y), WOOD_LINE, 9, alpha)
    C.line(c, (x - 60, y - 120), (x - 60, y - 280), WOOD_LINE, 9, alpha)


def seated(draw, c, x, y, s, **kw):
    """坐在椅子上的人：(x, y) 为椅子地面中点。"""
    chair(c, x, y)
    draw(c, x, y - 105, s * 0.9, **kw)


def ear(c, x, y, s=1.0, alpha=1.0):
    p = skia.Path()
    p.moveTo(x - 20 * s, y - 70 * s)
    p.cubicTo(x + 60 * s, y - 120 * s, x + 90 * s, y + 10 * s, x + 20 * s, y + 50 * s)
    p.cubicTo(x, y + 70 * s, x - 10 * s, y + 90 * s, x - 30 * s, y + 70 * s)
    c.drawPath(p, K.paint("#F6D9C2", alpha))
    c.drawPath(p, wb.marker(BLACK, 7, alpha))


def brain(c, x, y, r, alpha=1.0):
    c.drawOval(skia.Rect.MakeXYWH(x - r * 1.2, y - r, r * 2.4, r * 2), K.paint("#F4C6D0", alpha))
    c.drawOval(skia.Rect.MakeXYWH(x - r * 1.2, y - r, r * 2.4, r * 2), wb.marker("#B0566A", 7, alpha))
    for i in range(3):
        C.line(c, (x - r * 0.8 + i * r * 0.6, y - r * 0.6), (x - r * 0.6 + i * r * 0.6, y + r * 0.5), "#B0566A", 4, alpha)


def folder(c, x, y, w, h, alpha=1.0, rot=0.0):
    with K.at(c, x, y, rot):
        c.drawPath(P((-w / 2, -h / 2 - 28), (-w / 6, -h / 2 - 28), (-w / 10, -h / 2), (w / 2, -h / 2), (w / 2, h / 2),
                     (-w / 2, h / 2), close=True), K.paint("#F2C14E", alpha))
        c.drawPath(P((-w / 2, -h / 2 - 28), (-w / 6, -h / 2 - 28), (-w / 10, -h / 2), (w / 2, -h / 2), (w / 2, h / 2),
                     (-w / 2, h / 2), close=True), wb.marker(BLACK, 7, alpha))
        for i in range(3):
            c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 20 + i * 14, -h / 2 - 20 - i * 6, w * 0.6, 20), K.paint("#FFFFFF", alpha))


def link_chain(c, x, y, n, broken=None, alpha=1.0):
    for i in range(n):
        xx = x + i * 70
        dy = 0
        if broken is not None and i >= broken:
            xx += 40
            dy = 16
        c.drawOval(skia.Rect.MakeXYWH(xx - 40, y - 22 + dy, 80, 44), wb.marker(GRAY if i % 2 else BLACK, 8, alpha))


# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：小李第三次指着屏幕讲，气泡越来越大；小周交上来的文件一个红叉；“这么简单”
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k1_ppl, k1_b1, k1_b2, k1_x, k1_th = seq(j, [None, (0, 1, 0.1), (0, 1, 0.8), (0, 2, 0.6), (1, 1, 0.5)])
L.note("第3遍", "这么简单", "这样…")


def ppl1(c, T, cx=cx, cy=cy):
    monitor(c, cx - 60, cy + 120, 320, 210)
    desk(c, cx - 60, cy + 270, 620)
    hy = cy + 520 - 290 * 0.85
    poke = 20 * math.sin((T - tb(1, k1_ppl)) * 8)
    draw_li(c, cx - 380, cy + 520, 0.85, "flat", rh=(cx - 200 + poke, cy + 110))
    seated(draw_zhou, c, cx + 300, cy + 530, 0.85, mood="o")


pop(j, k1_ppl, cx, cy + 300, ppl1, "wood_low", 0.7)


def bubbles1(c, kk, T, cx=cx, cy=cy):
    for n, (k_, size, x, y) in enumerate(((k1_b1, 0.7, cx - 420, cy - 120), (k1_b2, 1.15, cx - 300, cy - 300))):
        g = pop_scale(T - tb(1, k_))
        if g > 0:
            with K.at(c, x, y, 0, g * size):
                bubble_text(c, "这样…" if n == 0 else "第3遍", 0, 0, 62, BLACK if n == 0 else RED, 1)
    return None


ev(j, k1_b1, bubbles1, "pop", 0.7)
b.hit(j, k1_b2, "bongo_high", 0.75, "气泡变大")


def file1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k1_x))
    if sc <= 0:
        return None
    x, y = cx + 300, cy - 200
    with at_pop(c, x, y, sc):
        paper(c, x, y, 240, 300, rows=4, rot=6)
        xmark(c, x, y, 90, clamp01((T - tb(1, k1_x)) / 0.3))
    return None


ev(j, k1_x, file1, "rim", 0.85)


def think1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k1_th))
    if sc <= 0:
        return None
    x, y = cx + 20, cy - 480
    with at_pop(c, x, y, sc):
        c.drawOval(skia.Rect.MakeXYWH(x - 190, y - 70, 380, 140), K.paint("#FFFFFF"))
        c.drawOval(skia.Rect.MakeXYWH(x - 190, y - 70, 380, 140), wb.marker(BLACK, 7))
        K.text(c, "这么简单", x, y + 2, 60, "hand", BLACK)
    return None


ev(j, k1_th, think1, "wood_high", 0.75)

# ================================================================ 屏 2：交接时一个文件夹被扔到桌上，“都在里面了”；新人对着文件夹发愣
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
k12_desk, k12_throw, k12_say, k12_stare = seq(j, [None, (3, 1, 0.5), (3, 2, 0.4), (3, 2, 0.9)])
L.note("交接", "都在里面了")
pop(j, k12_desk, cx, cy + 290, lambda c, T, cx=cx, cy=cy: (desk(c, cx + 100, cy + 290, 640),
                                                         K.text(c, "交接", cx - 380, cy - 470, 70, "hand", GRAY)),
    "wood_low", 0.7)


def throw12(c, kk, T, cx=cx, cy=cy):
    t0 = tb(2, k12_throw)
    if T < t0:
        return None
    u = ease_in_out(clamp01((T - t0) / 0.45))
    x = lerp(cx - 330, cx + 100, u)
    y = lerp(cy - 50, cy + 220, u) - 200 * math.sin(math.pi * u)
    folder(c, x, y, 260, 180, rot=lerp(-30, 6, u))
    if u >= 1:
        dt = T - t0 - 0.45
        if dt < 0.4:
            for i in range(5):
                a = math.radians(200 + i * 35)
                C.line(c, (x + math.cos(a) * 150, y + 60 + math.sin(a) * 40), (x + math.cos(a) * 200, y + 60 + math.sin(a) * 60),
                       GRAY, 5, 1 - dt / 0.4)
    hy = cy + 520 - 290 * 0.85
    draw_li(c, cx - 400, cy + 520, 0.85, "flat", rh=(cx - 300, hy + 20) if u < 1 else None, bag=True)
    return None


ev(j, k12_throw, throw12, "wood_high", 0.8)
ev(j, k12_say, L.pop_bubble("都在里面了", cx - 330, cy - 250, j, k12_say, 58, BLACK, tail=-1), "pop", 0.75)


def stare12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k12_stare))
    if sc <= 0:
        return None
    x, y = cx + 380, cy + 520
    with at_pop(c, x, y, sc):
        draw_zhou(c, x, y, 0.85, mood="o")
        for n in range(3):
            c.drawCircle(x - 30 + n * 30, y - 290 * 0.85 - 90, 8, K.paint(GRAY))
    return None


ev(j, k12_stare, stare12, "bongo_low", 0.75)

# ================================================================ 屏 3：教爸妈手机挂号，手指在屏幕上飞；爸妈头顶问号越来越大，摆手“算了”
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
KD = L.drop_k()                       # drop 屏：“最后说算了”说完正好 drop，“算了”砸下、震屏、闪白
b.shots[j].shake, b.shots[j].flashes = [(KD, 14.0)], [(KD, 0.4)]
k13_ppl, k13_fast, k13_q = seq(j, [None, (4, 1, 0.4), (4, 2, 0.5)])
k13_q = min(k13_q, KD - 1)
k13_no = KD
L.note("挂号", "算了")


def ppl13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k13_ppl))
    if sc <= 0:
        return None
    no = T >= tb(3, k13_no)
    with at_pop(c, cx, cy + 520, sc):
        hy = cy + 520 - 290 * 0.85
        fast = T >= tb(3, k13_fast)
        fx = cx - 130 + (40 * math.sin(T * 30) if fast and not no else 0)
        draw_li(c, cx - 330, cy + 520, 0.85, "smile", rh=(fx, cy + 120))
        phone(c, cx - 150, cy + 140, 150, 260, screen=BLUE_FILL)
        K.text(c, "挂号", cx - 150, cy + 100, 40, "hand", BLUE)
        wave = 30 * math.sin((T - tb(3, k13_no)) * 14) if no else 0
        draw_mom(c, cx + 170, cy + 520, 0.8, mood="sad" if no else "o", rh=(cx + 260 + wave, cy + 180) if no else None)
        draw_dad(c, cx + 400, cy + 520, 0.8, mood="sad" if no else "o")
    return None


ev(j, k13_ppl, ppl13, "wood_low", 0.7)
b.hit(j, k13_fast, "shaker", 0.8, "手指在屏幕上飞")


def q13(c, kk, T, cx=cx, cy=cy):
    t0 = tb(3, k13_q)
    if T < t0:
        return None
    grow = 1 + 0.6 * clamp01((T - t0) / 1.5)
    for n, (x, y) in enumerate(((cx + 170, cy - 60), (cx + 400, cy - 80))):
        qmark(c, x, y - 40 * grow, 80 * grow, T - t0 - 0.1 * n, RED)
    return None


ev(j, k13_q, q13, "bongo_high", 0.75)
ev(j, k13_no, L.slam_text("算了", cx + 290, cy - 360, 130, RED, j, k13_no, rot=-6), "kick", 0.95)

# ================================================================ 屏 4：场记板“第一遍”拍下；鼠标快成残影；说完时“这样，再这样，懂了吧？”砸下
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k2_clap = 0
k2_ppl = max(kq(j, wt(5, 1, 0.3), 1), 1)
k2_fast = nx(j, wt(6, 0, 0.4), k2_ppl)
KD4 = nx(j, wt(6, 3, 0.8), k2_fast)      # “懂了吧？”说完：气泡砸下
b.shots[j].shake, b.shots[j].flashes = [(KD4, 12.0)], [(KD4, 0.3)]
L.note("这样，再这样", "懂了吧？")
ev(j, k2_clap, clap_fn(j, k2_clap, cx - 330, cy - 440, "第一遍"), "clap", 0.9)


def ppl2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k2_ppl))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 300, sc):
        monitor(c, cx, cy + 80, 380, 250, BLUE_FILL)
        desk(c, cx, cy + 270, 760)
        fast = T >= tb(4, k2_fast)
        mx, my = cx - 160, cy + 240
        if fast:
            mouse_blur(c, mx, my, T)
            for i in range(4):
                ph = ((T * 3) + i * 0.25) % 1
                c.drawRect(skia.Rect.MakeXYWH(cx - 150 + ph * 260, cy + 10 + i * 40, 60, 20), K.paint(BLUE, 1 - ph))
        else:
            mouse_blur(c, mx, my, 0.0, 1.0)
        hy = cy + 520 - 290 * 0.85
        draw_li(c, cx - 380, cy + 520, 0.85, "smile", rh=(mx, my - 20))
        seated(draw_zhou, c, cx + 330, cy + 530, 0.85, mood="o" if fast else "flat")
    return None


ev(j, k2_ppl, ppl2, "wood_low", 0.7)
b.hit(j, k2_fast, "shaker", 0.8, "鼠标飞快")


def say2(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(4, KD4))
    if sc <= 0:
        return None
    with K.at(c, cx + 100, cy - 330, -3, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(-310, -120, 620, 240), 50, 50, K.paint("#FFFFFF"))
        c.drawPath(wb.bubble(0, 0, 620, 240, -1), wb.marker(BLACK, 8))
        K.text(c, "这样，再这样", 0, -40, 66, "hand", BLACK)
        K.text(c, "懂了吧？", 0, 50, 80, "hand", RED)
    return None


ev(j, KD4, say2, "kick", 0.95)

# ================================================================ 屏 5：小周点头说懂了；日历翻到第二天；桌上三个红叉
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k3_nod, k3_cal, k3_x1 = seq(j, [None, (7, 1, 0.1), (7, 1, 0.6)])
k3_x2, k3_x3 = k3_x1 + 1, k3_x1 + 2
L.note("懂了", "第二天")
ev(j, 0, clap_fn(j, 0, cx - 380, cy - 470, "第一遍"))


def nod3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k3_nod))
    if sc <= 0:
        return None
    x, y = cx - 250, cy + 520
    nod = 10 * abs(math.sin((T - tb(5, k3_nod)) * 6)) if T < tb(5, k3_cal) else 0
    with at_pop(c, x, y, sc):
        draw_zhou(c, x, y + nod * 0.3, 0.95, mood="smile" if T < tb(5, k3_x1) else "sad")
        if T < tb(5, k3_cal) + 0.5:
            bubble_text(c, "懂了", x + 60, y - 430, 60, BLACK, -1)
    return None


ev(j, k3_nod, nod3, "pop", 0.7)


def cal3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k3_cal))
    if sc <= 0:
        return None
    x, y = cx + 300, cy - 280
    with at_pop(c, x, y, sc):
        calendar_page(c, x, y, 300, 280, "第二天", flip=ease_in_out(clamp01((T - tb(5, k3_cal)) / 0.4)))
    return None


ev(j, k3_cal, cal3, "wood_high", 0.75)


def xs3(c, kk, T, cx=cx, cy=cy):
    desk(c, cx + 200, cy + 300, 620)
    for n, k_ in enumerate((k3_x1, k3_x2, k3_x3)):
        if T >= tb(5, k_):
            x = cx + 20 + n * 180
            paper(c, x, cy + 220, 150, 150, rows=2, rot=(n - 1) * 6)
            xmark(c, x, cy + 220, 55, clamp01((T - tb(5, k_)) / 0.25))
    return None


ev(j, k3_x1, xs3, "rim", 0.8)
b.hit(j, k3_x2, "rim", 0.8, "第二个红叉")
b.hit(j, k3_x3, "kick", 0.85, "第三个红叉")

# ================================================================ 屏 6：车间组长带新员工；牌子四个空格；“学的人没学会 / 就当是教的人没教会”
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k4_ppl, k4_sign, k4_t1, k4_t2 = seq(j, [None, (8, 2, 0.3), (9, 0, 0.8), (9, 1, 0.6)])
L.note("学的人没学会", "就当是教的人没教会", "四步")


def ppl4(c, T, cx=cx, cy=cy):
    C.line(c, (cx - 560, cy + 530), (cx + 560, cy + 530), GRAY, 6)
    hy = cy + 520 - 290 * 0.9
    draw_leader2(c, cx - 300, cy + 520, 0.9, rh=(cx - 180, hy + 70), mood="smile")
    draw_worker(c, cx - 30, cy + 520, 0.85, mood="o")


pop(j, k4_ppl, cx - 150, cy + 520, ppl4, "wood_low", 0.7)


def sign4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k4_sign))
    if sc <= 0:
        return None
    x, y = cx + 330, cy + 180
    with at_pop(c, x, y, sc):
        C.line(c, (x, y + 120), (x, y + 350), WOOD_LINE, 12)
        box(c, x, y, 380, 240, WOOD, WOOD_LINE, 8, 12)
        K.text(c, "四步", x, y - 75, 54, "hand", BLACK)
        for i in range(4):
            g = pop_scale(T - tb(6, k4_sign) - 0.1 * i)
            with K.at(c, x - 135 + i * 90, y + 35, 0, g):
                box(c, 0, 0, 74, 74, "#FFFFFF", BLACK, 5, 10)
                K.text(c, STEP_NAMES[i], 0, 2, 46, "hand", BLACK)
    return None


ev(j, k4_sign, sign4, "wood_high", 0.75)
ev(j, k4_t1, L.slam_text("学的人没学会", cx - 30, cy - 450, 80, BLACK, j, k4_t1), "rim", 0.8)
ev(j, k4_t2, L.slam_text("就当是教的人没教会", cx - 30, cy - 320, 80, RED, j, k4_t2, rot=-2), "kick", 0.9)
b.shots[j].shake = [(k4_t2, 8.0)]

# ================================================================ 屏 7：组长自己拧螺丝，再转身教新员工；“懂这份活”“会教别人”两个勾
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k5_bench, k5_turn, k5_c1, k5_c2 = seq(j, [None, (10, 2, 0.2), (10, 2, 0.8), (10, 3, 0.7)])
L.note("懂这份活", "会教别人", "丰田的领导")


def bench5(c, T, cx=cx, cy=cy):
    K.text(c, "丰田的领导", cx - 300, cy - 470, 58, "hand", GRAY)
    box(c, cx - 150, cy + 250, 560, 40, WOOD, WOOD_LINE, 6, 6)
    for dx in (-400, 100):
        C.line(c, (cx + dx, cy + 270), (cx + dx, cy + 530), WOOD_LINE, 9)
    box(c, cx - 150, cy + 190, 200, 80, "#C9CED6", BLACK, 5, 8)
    turned = T >= tb(7, k5_turn)
    x, y = cx - 380, cy + 520
    hy = y - 290 * 0.9
    tw = 18 * math.sin((T - tb(7, k5_bench)) * 10) if not turned else 0
    draw_leader2(c, x, y, 0.9, rh=(cx - 200 + tw, cy + 170) if not turned else (x + 160, hy + 40), mood="smile")
    a = math.radians((T - tb(7, k5_bench)) * 400 if not turned else 0)
    C.line(c, (cx - 150, cy + 170), (cx - 150 + 50 * math.cos(a), cy + 170 + 20 * math.sin(a)), GRAY, 8)
    if turned:
        g = pop_scale(T - tb(7, k5_turn))
        with at_pop(c, cx + 300, cy + 520, g):
            draw_worker(c, cx + 300, cy + 520, 0.85, mood="smile")


pop(j, k5_bench, cx - 150, cy + 300, bench5, "wood_low", 0.7)
b.hit(j, k5_turn, "pop", 0.7, "转身教新员工")


def checks5(c, kk, T, cx=cx, cy=cy):
    for n, (k_, s_, y) in enumerate(((k5_c1, "懂这份活", cy - 300), (k5_c2, "会教别人", cy - 120))):
        g = pop_scale(T - tb(7, k_))
        if g <= 0:
            continue
        with K.at(c, cx + 220, y, 0, g):
            box(c, 0, 0, 440, 130, "#FFFFFF", GREEN, 6, 20)
            K.text(c, s_, 40, 2, 62, "hand", BLACK)
        tick(c, cx + 50, y, 40, clamp01((T - tb(7, k_)) / 0.3))
    return None


ev(j, k5_c1, checks5, "ding", 0.75)
b.hit(j, k5_c2, "ding", 0.8, "第二个勾")

# ================================================================ 屏 8：改写版——场记板翻面；拉椅子让小周坐下；纸上画出这份活用在哪、做错会怎样
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k6_clap, k6_chair, k6_use, k6_err = seq(j, [None, (12, 0, 0.6), (12, 1, 0.6), (12, 3, 0.5)])
k6_card = k6_chair
L.note("报表", "领导开会用", "错一个数", "会上出丑")
ev(j, k6_clap, clap_fn(j, k6_clap, cx - 330, cy - 440, "改写版", GREEN), "clap", 0.9)
ev(j, k6_card, step_card_fn(j, 1, k6_card))


def ppl6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k6_chair))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 400, sc):
        desk(c, cx + 60, cy + 270, 640)
        u = ease_out(clamp01((T - tb(8, k6_chair)) / 0.5))
        seated(draw_zhou, c, lerp(cx + 450, cx + 300, u), cy + 530, 0.85, mood="smile")
        hy = cy + 520 - 290 * 0.85
        draw_li(c, cx - 380, cy + 520, 0.85, "smile", rh=(cx - 160, cy + 230))
    return None


ev(j, k6_chair, ppl6, "wood_low", 0.7)


def sheet6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k6_use))
    if sc <= 0:
        return None
    x, y = cx + 20, cy - 120
    with at_pop(c, x, y, sc):
        box(c, x, y, 700, 300, "#FFFFFF", BLACK, 6, 8)
        box(c, x - 210, y - 40, 170, 110, BLUE_FILL, BLUE, 5, 8)
        K.text(c, "报表", x - 210, y - 38, 48, "hand", BLUE)
        C.line(c, (x - 110, y - 40), (x + 10, y - 40), BLUE, 8)
        C.line(c, (x + 10, y - 40), (x - 15, y - 58), BLUE, 8)
        C.line(c, (x + 10, y - 40), (x - 15, y - 22), BLUE, 8)
        K.text(c, "领导开会用", x + 170, y - 38, 48, "hand", BLUE)
        if T >= tb(8, k6_err):
            g = pop_scale(T - tb(8, k6_err))
            with K.at(c, x, y + 80, 0, g):
                K.text(c, "错一个数 → 会上出丑", 0, 0, 46, "hand", RED)
    return None


L.note("错一个数 → 会上出丑")
ev(j, k6_use, sheet6, "wood_high", 0.75)
b.hit(j, k6_err, "rim", 0.8, "做错会怎样")

# ================================================================ 屏 9：第二步——小李慢慢做，每做一步弹出一张“为什么”小卡片
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k7_ppl, k7_w1, k7_w2, k7_w3 = seq(j, [None, (13, 1, 0.6), (13, 2, 0.6), (13, 3, 0.6)])
L.note("为什么")
ev(j, k7_ppl, step_card_fn(j, 2, k7_ppl))


def ppl7(c, T, cx=cx, cy=cy):
    monitor(c, cx - 60, cy + 120, 340, 220, BLUE_FILL)
    desk(c, cx - 20, cy + 270, 700)
    hy = cy + 520 - 290 * 0.85
    slow = 12 * math.sin((T - tb(9, k7_ppl)) * 2)
    draw_li(c, cx - 380, cy + 520, 0.85, "smile", rh=(cx - 220 + slow, cy + 230))
    seated(draw_zhou, c, cx + 330, cy + 530, 0.85, mood="smile")
    K.text(c, "慢", cx - 380, cy - 140, 60, "hand", GREEN)


L.note("慢")
pop(j, k7_ppl, cx, cy + 300, ppl7, "wood_low", 0.7)


def whys7(c, kk, T, cx=cx, cy=cy):
    for n, k_ in enumerate((k7_w1, k7_w2, k7_w3)):
        g = pop_scale(T - tb(9, k_))
        if g <= 0:
            continue
        x, y = cx - 260 + n * 260, cy - 260
        with K.at(c, x, y, (n - 1) * 5, g):
            box(c, 0, 0, 220, 150, NOTE_FILL, ORANGE, 6, 12)
            K.text(c, f"第{STEP_NAMES[n]}步", 0, -35, 40, "hand", GRAY)
            K.text(c, "为什么", 0, 25, 52, "hand", ORANGE)
    return None


L.note("第一步", "第二步", "第三步")
ev(j, k7_w1, whys7, "pop", 0.75)
b.hit(j, k7_w2, "pop", 0.75, "第二张为什么")
b.hit(j, k7_w3, "bongo_high", 0.75, "第三张为什么")

# ================================================================ 屏 10：第三步——换小周操作，边做边说；错了一处，小李当场一指，改成勾
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k8_swap, k8_say, k8_err, k8_fix = seq(j, [None, (14, 1, 0.4), (14, 2, 0.3), (14, 3, 0.5)])
L.note("先点这个…", "当场改")
ev(j, k8_swap, step_card_fn(j, 3, k8_swap))


def ppl8(c, T, cx=cx, cy=cy):
    monitor(c, cx + 60, cy + 120, 340, 220, BLUE_FILL)
    desk(c, cx + 40, cy + 270, 700)
    point = T >= tb(10, k8_err)
    hy = cy + 520 - 290 * 0.85
    draw_li(c, cx - 400, cy + 520, 0.85, "o" if point and T < tb(10, k8_fix) else "smile",
            rh=(cx - 40, cy + 60) if point else None)
    ty = 10 * math.sin((T - tb(10, k8_swap)) * 12)
    seated(draw_zhou, c, cx - 100, cy + 530, 0.85, mood="smile", rh=(cx + 30, cy + 230 + ty))


pop(j, k8_swap, cx, cy + 300, ppl8, "wood_low", 0.7)
ev(j, k8_say, L.pop_bubble("先点这个…", cx - 60, cy - 160, j, k8_say, 58, BLACK, tail=-1), "pop", 0.75)


def fix8(c, kk, T, cx=cx, cy=cy):
    t0 = tb(10, k8_err)
    if T < t0:
        return None
    x, y = cx + 60, cy + 110
    fixed = T >= tb(10, k8_fix)
    if not fixed:
        xmark(c, x, y, 50, clamp01((T - t0) / 0.25))
    else:
        tick(c, x, y, 55, clamp01((T - tb(10, k8_fix)) / 0.25))
        g = C.slam_scale(T - tb(10, k8_fix))
        with K.at(c, cx + 300, cy - 360, -4, g):
            K.text(c, "当场改", 0, 0, 90, "hand", GREEN)
    return None


ev(j, k8_err, fix8, "rim", 0.8)
b.hit(j, k8_fix, "kick", 0.85, "改成勾")

# ================================================================ 屏 11：第四步——小李回到自己座位；钟走一阵他探头回来看；小周举手“找你”
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k9_back, k9_clk, k9_peek, k9_hand = seq(j, [None, (15, 1, 0.3), (15, 2, 0.4), (15, 3, 0.6)])
L.note("有问题找我", "放手")
ev(j, k9_back, step_card_fn(j, 4, k9_back))


def ppl9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k9_back))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 400, sc):
        desk(c, cx + 230, cy + 300, 420)
        monitor(c, cx + 230, cy + 160, 260, 170, BLUE_FILL)
        hand = T >= tb(11, k9_hand)
        seated(draw_zhou, c, cx + 360, cy + 540, 0.8, mood="smile", lh=(cx + 300, cy + 60) if hand else None)
        desk(c, cx - 360, cy + 300, 300)
        u = ease_out(clamp01((T - tb(11, k9_back)) / 0.6))
        peek = T >= tb(11, k9_peek)
        x = lerp(cx + 50, cx - 360, u)
        if peek:
            x = lerp(cx - 360, cx - 120, ease_out(clamp01((T - tb(11, k9_peek)) / 0.4)))
        draw_li(c, x, cy + 520, 0.8, "smile")
    return None


ev(j, k9_back, ppl9, "wood_low", 0.7)
ev(j, k9_back, L.pop_text("放手", cx - 380, cy - 470, 80, GREEN, j, k9_back))


def clk9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k9_clk))
    if sc <= 0:
        return None
    x, y = cx - 300, cy - 220
    h = clamp01((T - tb(11, k9_clk)) / 1.5) * 0.4
    with at_pop(c, x, y, sc):
        clock_face(c, x, y, 120, h, h, GREEN, GREEN_FILL)
    return None


ev(j, k9_clk, clk9, "wood_high", 0.7)
b.hit(j, k9_peek, "pop", 0.7, "探头回来看")
ev(j, k9_hand, L.pop_bubble("有问题找我", cx + 150, cy - 230, j, k9_hand, 56, BLACK, tail=-1), "bongo_high", 0.75)

# ================================================================ 屏 12：结果——第二天小周交出一个勾，还举着问号“为什么要这样？”
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k10_cal, k10_done, k10_q = seq(j, [None, (16, 1, 0.5), (16, 2, 0.6)])
L.note("第二天", "为什么要这样？")
pop(j, k10_cal, cx - 330, cy - 400, lambda c, T, cx=cx, cy=cy: calendar_page(c, cx - 330, cy - 400, 260, 240, "第二天"),
    "wood_high", 0.7)


def zhou10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k10_cal) - 0.15)
    if sc <= 0:
        return None
    x, y = cx - 150, cy + 520
    hy = y - 290 * 0.95
    done = T >= tb(12, k10_done)
    with at_pop(c, x, y, sc):
        draw_zhou(c, x, y, 0.95, mood="smile", rh=(x + 150, hy + 40) if done else None)
        draw_li(c, cx + 380, y, 0.85, "smile" if done else "flat")
    if done:
        g = pop_scale(T - tb(12, k10_done))
        with K.at(c, x + 250, hy + 10, 4, g):
            paper(c, 0, 0, 220, 260, rows=4)
            tick(c, 30, 40, 70, clamp01((T - tb(12, k10_done)) / 0.3))
    return None


ev(j, k10_cal, zhou10)
b.hit(j, k10_done, "ding", 0.85, "交出一个勾")
ev(j, k10_q, L.pop_bubble("为什么要这样？", cx + 160, cy - 300, j, k10_q, 58, BLUE, tail=-1), "pop", 0.75)

# ================================================================ 屏 13：步骤链里两步是虚线（忘了讲）；耳朵听的字往外漏，手做过的一步留在脑子里
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k11_q, k11_chain, k11_hid, k11_ear, k11_hand = seq(j, [None, (18, 0, 0.6), (18, 2, 0.5), (19, 0, 0.6), (19, 2, 0.4)])
L.note("讲三遍", "做一遍", "忘了讲", "听", "做")
ev(j, k11_q, L.slam_text("讲三遍 < 做一遍", cx, cy - 500, 80, RED, j, k11_q), "rim", 0.8)
L.note("讲三遍 < 做一遍")


def chain11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k11_chain))
    if sc <= 0:
        return None
    y = cy - 260
    hid = T >= tb(13, k11_hid)
    with at_pop(c, cx, y, sc):
        for i in range(6):
            x = cx - 450 + i * 180
            ghost = i in (2, 4)
            if ghost and hid:
                dashed_rect(c, x, y, 130, 100, GRAY, 5)
                K.text(c, "?", x, y, 50, "hand", GRAY)
            else:
                box(c, x, y, 130, 100, BLUE_FILL, BLUE, 5, 12)
                K.text(c, str(i + 1), x, y + 2, 54, "hand", BLUE)
            if i < 5:
                C.line(c, (x + 66, y), (x + 114, y), GRAY, 6)
        if hid:
            g = pop_scale(T - tb(13, k11_hid))
            with K.at(c, cx - 90, y + 110, 0, g):
                K.text(c, "忘了讲", 0, 0, 52, "hand", RED)
    return None


ev(j, k11_chain, chain11, "wood_high", 0.75)
b.hit(j, k11_hid, "rim", 0.8, "两步变虚线")


def ear11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k11_ear))
    if sc <= 0:
        return None
    x, y = cx - 260, cy + 200
    with at_pop(c, x, y, sc):
        ear(c, x, y, 1.6)
        K.text(c, "听", x, y + 220, 60, "hand", GRAY)
        for n in range(4):
            ph = ((T - tb(13, k11_ear)) * 0.8 + n * 0.25) % 1
            K.text(c, "字", x + 30 + ph * 230, y - 40 + ph * 180 + n * 10, 40, "hand", GRAY, 1 - ph)
    return None


L.note("字")
ev(j, k11_ear, ear11, "shaker", 0.7)


def hand11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k11_hand))
    if sc <= 0:
        return None
    x, y = cx + 260, cy + 200
    with at_pop(c, x, y, sc):
        brain(c, x, y - 40, 110)
        g = clamp01((T - tb(13, k11_hand)) / 0.5)
        bx, by = x, lerp(y + 230, y - 40, ease_out(g))
        box(c, bx, by, 110, 80, GREEN_FILL, GREEN, 5, 10)
        K.text(c, "做", bx, by + 2, 50, "hand", GREEN)
        if g >= 1:
            sparkle(c, x, y - 40, T - tb(13, k11_hand) - 0.5, GREEN, 8, 130, 200)
    return None


ev(j, k11_hand, hand11, "ding", 0.8)

# ================================================================ 屏 14：小李桌上一摞自己的活，旁边站着等着学的新人；大字“三步”
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k14_pile, k14_tired, k14_new, k14_3 = seq(j, [None, (20, 2, 0.5), (21, 0, 0.4), (21, 1, 0.6)])
L.note("很累", "三步")


def pile14(c, T, cx=cx, cy=cy):
    desk(c, cx - 150, cy + 290, 560)
    for i in range(9):
        paper(c, cx - 150 + ((i * 37) % 21 - 10), cy + 250 - i * 26, 260, 40, rows=0)
    tired = T >= tb(14, k14_tired)
    draw_li(c, cx - 420, cy + 520, 0.85, "sad" if tired else "flat")
    if tired:
        sweat(c, cx - 360, cy + 520 - 290 * 0.85 - 20 + 6 * math.sin(T * 6))


pop(j, k14_pile, cx - 150, cy + 290, pile14, "wood_low", 0.7)
b.hit(j, k14_tired, "tom", 0.7, "带人很累")


def new14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k14_new))
    if sc <= 0:
        return None
    x, y = cx + 380, cy + 520
    with at_pop(c, x, y, sc):
        draw_zhou(c, x, y, 0.85, mood="smile", rh=(x + 40, y - 330))
    return None


ev(j, k14_new, new14, "pop", 0.75)
ev(j, k14_3, L.slam_text("三步", cx + 100, cy - 380, 170, RED, j, k14_3, rot=-4), "kick", 0.9)
b.shots[j].shake = [(k14_3, 9.0)]

# ================================================================ 屏 15：做法一——先画一个箭头指向“用在哪”，再画“怎么做”
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k15_n, k15_use, k15_how, k15_li = seq(j, [None, (22, 1, 0.5), (22, 2, 0.5), (22, 2, 0.9)])
L.note("第一", "用在哪", "怎么做", "先", "再")
pop(j, k15_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: K.text(c, "第一", cx - 380, cy - 470, 90, "hand", RED), "rim", 0.8)
b.path(j, k15_use, k15_use + 0.5, wb.arrow((cx - 380, cy - 120), (cx + 50, cy - 200), 0.2, 50), GREEN, 10,
       sfx="wood_high", gain=0.75)
b.text(j, k15_use + 0.3, k15_use + 1.0, "用在哪", cx + 230, cy - 210, 76, GREEN)
b.text(j, k15_use, k15_use + 0.3, "先", cx - 430, cy - 120, 64, GRAY)
b.path(j, k15_how, k15_how + 0.5, wb.arrow((cx - 380, cy + 80), (cx + 50, cy + 80), 0.0, 50), BLUE, 10, sfx="wood_high", gain=0.75)
b.text(j, k15_how + 0.3, k15_how + 1.0, "怎么做", cx + 230, cy + 80, 76, BLUE)
b.text(j, k15_how, k15_how + 0.3, "再", cx - 430, cy + 80, 64, GRAY)
ev(j, k15_li, L.figure(draw_li, j, k15_li, cx - 300, cy + 540, 0.8, mood="smile", rh=(cx - 200, cy + 200)), "pop", 0.7)

# ================================================================ 屏 16：做法二——两个小人轮流：小李做给小周看，小周做给小李看
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
k16_n, k16_a, k16_b, k16_sw = seq(j, [None, (23, 0, 0.6), (23, 2, 0.2), (23, 2, 0.8)])
L.note("第二", "做给他看", "做给你看")
pop(j, k16_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: K.text(c, "第二", cx - 380, cy - 470, 90, "hand", RED), "rim", 0.8)


def turns16(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(16, k16_a))
    if sc <= 0:
        return None
    swap = T >= tb(16, k16_b)
    with at_pop(c, cx, cy + 300, sc):
        desk(c, cx, cy + 270, 400)
        box(c, cx, cy + 220, 160, 70, "#C9CED6", BLACK, 5, 8)
        hy = cy + 520 - 290 * 0.85
        tw = 14 * math.sin(T * 10)
        draw_li(c, cx - 330, cy + 520, 0.85, "smile", rh=(cx - 80 + tw, cy + 200) if not swap else None)
        draw_zhou(c, cx + 330, cy + 520, 0.85, mood="smile", lh=(cx + 80 + tw, cy + 200) if swap else None)
        lab = "做给你看" if swap else "做给他看"
        x = cx + 280 if swap else cx - 280
        bubble_text(c, lab, x, cy - 120, 58, BLUE if swap else BLACK, 1 if not swap else -1)
    return None


ev(j, k16_a, turns16, "pop", 0.75)
b.hit(j, k16_b, "wood_high", 0.8, "换他做")


def swap16(c, kk, T, cx=cx, cy=cy):
    dt = T - tb(16, k16_sw)
    if dt < 0:
        return None
    g = pop_scale(dt)
    with K.at(c, cx, cy - 330, (dt * 120) % 360 if dt < 0.6 else 0, g):
        c.drawPath(C.loop_arrow(0, 0, 70), wb.marker(GREEN, 10))
    return None


ev(j, k16_sw, swap16, "pop", 0.75)

# ================================================================ 屏 17：做法三——第二天早上小李走到小周桌边，“卡在哪了？”
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
k17_n, k17_walk, k17_ask, k17_ans = seq(j, [None, (24, 1, 0.4), (24, 2, 0.4), (24, 2, 0.9)])
L.note("第三", "第二天", "卡在哪了？", "这一步")
pop(j, k17_n, cx - 380, cy - 470, lambda c, T, cx=cx, cy=cy: (K.text(c, "第三", cx - 380, cy - 470, 90, "hand", RED),
                                                             calendar_page(c, cx + 380, cy - 430, 220, 200, "第二天")),
    "rim", 0.8)


def walk17(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(17, k17_walk))
    if sc <= 0:
        return None
    desk(c, cx + 240, cy + 290, 420)
    monitor(c, cx + 240, cy + 150, 260, 170, BLUE_FILL)
    seated(draw_zhou, c, cx + 380, cy + 540, 0.8, mood="smile")
    x, dy, mv = C.walk(T, tb(17, k17_walk), 0.9, cx - 500, cx - 80, 14, 3)
    draw_li(c, x, cy + 520 + dy, 0.85, "smile")
    return None


ev(j, k17_walk, walk17, "wood_low", 0.7)
ev(j, k17_ask, L.pop_bubble("卡在哪了？", cx - 100, cy - 150, j, k17_ask, 62, BLUE, tail=-1), "pop", 0.8)
ev(j, k17_ans, L.pop_bubble("这一步", cx + 320, cy - 120, j, k17_ans, 56, BLACK, tail=1), "bongo_high", 0.75)

# ================================================================ 屏 18：海边躺椅上小李，手机很安静；工位上小周顺利接手
cx, cy = R[18]
j = L.scene(18, (cx, cy + 10, Z))
k18_sea, k18_ph, k18_desk, k18_ok = seq(j, [None, (25, 0, 0.6), (25, 1, 0.4), (25, 1, 0.9)])
L.note("休假", "静音")


def sea18(c, T, cx=cx, cy=cy):
    c.drawCircle(cx + 380, cy - 430, 70, K.paint(YELLOW))
    for i in range(3):
        y = cy - 230 + i * 40
        ph = T * 1.5 + i
        p = skia.Path()
        p.moveTo(cx - 540, y)
        for k_ in range(1, 12):
            p.lineTo(cx - 540 + k_ * 100, y + 12 * math.sin(ph + k_))
        c.drawPath(p, wb.marker(BLUE, 6))
    c.drawPath(P((cx - 540, cy - 110), (cx + 560, cy - 110)), wb.marker(YELLOW, 6))
    C.line(c, (cx - 420, cy - 20), (cx - 160, cy - 120), WOOD_LINE, 12)
    C.line(c, (cx - 160, cy - 120), (cx - 60, cy - 20), WOOD_LINE, 12)
    draw_li(c, cx - 280, cy - 60, 0.55, "smile", lh=(cx - 330, cy - 200), rh=(cx - 230, cy - 210))
    K.text(c, "休假", cx - 420, cy - 430, 70, "hand", GREEN)


pop(j, k18_sea, cx - 200, cy - 200, sea18, "wood_low", 0.7)


def ph18(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(18, k18_ph))
    if sc <= 0:
        return None
    x, y = cx + 150, cy - 30
    with at_pop(c, x, y, sc):
        phone(c, x, y, 110, 180)
        K.text(c, "静音", x, y + 130, 40, "hand", GRAY)
        K.text(c, "z", x + 70, y - 110 - 20 * math.sin(T * 2), 46, "hand", GRAY)
    return None


ev(j, k18_ph, ph18, "pop", 0.7)


def desk18(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(18, k18_desk))
    if sc <= 0:
        return None
    with at_pop(c, cx + 100, cy + 400, sc):
        dashed(c, (cx - 540, cy + 90), (cx + 560, cy + 90), GRAY, 4)
        desk(c, cx + 150, cy + 320, 500)
        monitor(c, cx + 150, cy + 180, 260, 170, BLUE_FILL)
        tw = 10 * math.sin(T * 12)
        seated(draw_zhou, c, cx - 180, cy + 560, 0.8, mood="smile", rh=(cx + 40 + tw, cy + 280))
        if T >= tb(18, k18_ok):
            tick(c, cx + 150, cy + 180, 50, clamp01((T - tb(18, k18_ok)) / 0.3))
    return None


ev(j, k18_desk, desk18, "wood_low", 0.7)
b.hit(j, k18_ok, "ding", 0.8, "小周顺利接手")

# ================================================================ 屏 19：评论区“谢谢某某”；多年后小周带新人，墙上挂着小李的照片；下一讲预告
cx, cy = R[19]
j = L.scene(19, (cx, cy + 10, Z))
k19_cb, k19_g, k19_later, k19_photo, k19_nx = seq(j, [None, (27, 0, 0.4), (28, 0, 0.5), (28, 1, 0.5), (29, 0, 0.2)])
GRIPES = [("谢谢老刘", cx - 330, cy - 420), ("谢谢我师父", cx + 200, cy - 420), ("谢谢陈姐", cx - 70, cy - 320)]
L.note("被谁好好教过？", *[g[0] for g in GRIPES], "多年后", "下一讲", "合作方总掉链子", "换掉就好了吗？")


def cb19(c, T, cx=cx, cy=cy):
    comment_box(c, cx, cy - 400, 1040, 330)
    K.text(c, "被谁好好教过？", cx - 120, cy - 520, 52, "hand", RED)


pop(j, k19_cb, cx, cy - 400, cb19, "wood_high", 0.7)
for n, (s_, x, y) in enumerate(GRIPES):
    ev(j, k19_g, L.pop_text(s_, x, y, 56, BLACK, j, k19_g + 0.15 * n), "pop" if n == 0 else None, 0.6)


def later19(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(19, k19_later))
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 100, sc):
        K.text(c, "多年后", cx - 400, cy - 140, 50, "hand", GRAY)
        hy = cy + 200 - 290 * 0.6
        draw_zhou(c, cx - 300, cy + 200, 0.6, mood="smile", rh=(cx - 220, hy + 40))
        c.drawPath(wb.stick(cx - 120, cy + 200, 0.5, arms="down"), wb.marker(GRAY, 9))
        c.drawPath(wb.face(cx - 120, cy + 200, 0.5, "smile"), wb.marker(GRAY, 6))
        if T >= tb(19, k19_photo):
            g = pop_scale(T - tb(19, k19_photo))
            with K.at(c, cx + 200, cy - 20, 0, g):
                box(c, 0, 0, 200, 220, "#FFFFFF", WOOD_LINE, 10, 6)
                c.save()
                c.clipRect(skia.Rect.MakeXYWH(-90, -100, 180, 200))
                draw_li(c, 0, 230, 0.75, "smile")
                c.restore()
                heart(c, 140, -100, 34)
    return None


ev(j, k19_later, later19, "wood_low", 0.7)
b.hit(j, k19_photo, "ding", 0.8, "墙上小李的照片")


def next19(c, kk, T, cx=cx, cy=cy):
    t0 = tb(19, k19_nx)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    with at_pop(c, cx, cy + 420, sc):
        box(c, cx, cy + 420, 1000, 300, "#FFFFFF", BLUE, 8, 24)
        K.text(c, "下一讲", cx + 120, cy + 320, 48, "hand", BLUE)
        K.text(c, "合作方总掉链子", cx + 120, cy + 410, 62, "hand", BLACK)
        K.text(c, "换掉就好了吗？", cx + 120, cy + 500, 62, "hand", BLACK)
        link_chain(c, cx - 450, cy + 430, 4, broken=2 if T - t0 > 0.5 else None)
    return None


ev(j, k19_nx, next19, "wood_high", 0.75)

# ================================================================ 收尾
L.finish(cover_shot=4, square_shot=10, notes=NOTES)
L.export(globals())
