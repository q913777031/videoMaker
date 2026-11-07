"""弗洛伊德《梦的解析》：昨晚的梦那么离谱，到底想说什么？（白板手绘 + AI 旁白，竖屏 2:3）

形式照《丰田模式》新版（fengtian/common.Lesson）：痛点开场 → 身边的例子 → 书中例子与观点 → 现在怎么看 → 三步 → 评论区 + 收尾鼓励。
故事贯穿：开场是“毕业多年还梦见考试”，书中段讲到考试梦时回到同一个考场。
- 0–4 秒：考场、挂钟狂转、笔袋空空，配音“又梦见考试”逐字砸下；
- 痛点：小李睡着，梦泡泡里是考场，笔打叉；惊醒坐起一身汗，头顶问号；
- 身边的例子（drop 在第 2 屏）：领导催方案 → 梦里被一张大方案追着跑；老同学照片 → 梦回高中教室；饿着睡 → 梦里火锅，筷子刚伸就醒；
- 书中：弗洛伊德与《梦的解析》；咸鱼 → 梦里喝水、小女儿 → 梦里草莓；“愿望的满足”；梦有两层；化了妆（面具、三人捏成一人、石头换纽扣）；
  考试梦回到开头的考场，旧卷子上一个“过”；拆开问“想到什么”、解梦词典打叉；
- 现在怎么看：老书“一百多年前”，睡眠研究，梦连着白天的心事；
- 三步：醒来先记三个词、找白天的影子、问感受；梦变成一张便条；评论区与天亮伸懒腰。
文案与出处见 mengjie/PLAN.md；人物小李为虚构，例子是示意。
"""

import math
from contextlib import contextmanager
from pathlib import Path

import skia

from adler import core
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import hooks as HK
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, pop_scale, slam_scale)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross, rect

core.SERIES.update(name="梦的解析", count="单讲", prefix="梦的解析")

# ---------------------------------------------------------------- 开场钩子（注册进 fengtian.hooks，Lesson 构造时读取）
HK.HOOK_TEXT["dream"] = "又梦见考试"
HK.SERIES_SUB = "弗洛伊德 · 梦的解析"

GRAY, GRAY_FILL = "#8A8F99", "#ECEEF1"
SKIN, WOOD, PAPER_W = "#FBE3CF", "#E3C9A0", "#FFFFFF"
NIGHT, NIGHT_FILL, CLOUD = "#3B3A8C", "#E4E2F6", "#FFFFFF"
SUIT = "#3D4A63"


def _hook_dream(H, j, cx, cy, acc):
    """开场：课桌与试卷、挂钟指针狂转、笔袋翻开空空；随后“又梦见考试”逐字砸下。"""
    b = H.b
    gy = cy + 40
    H.note("考试", "？")

    def desk(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        panic = T >= H.tb(j, 2)
        with K.at(c, cx - 40, gy, 0, sc):
            c.translate(-(cx - 40), -gy)
            draw_li(c, cx - 200, gy + 40, 0.95, "sad" if panic else "flat")
            top = skia.Rect.MakeXYWH(cx - 420, gy - 120, 760, 36)
            c.drawRect(top, K.paint(WOOD))
            c.drawRect(top, wb.marker("#A9773E", 7))
            for lx in (cx - 380, cx + 300):
                C.line(c, (lx, gy - 84), (lx, gy + 60), "#A9773E", 9)
            with K.at(c, cx - 30, gy - 170, -4):
                c.drawRect(skia.Rect.MakeXYWH(-120, -70, 240, 140), K.paint(PAPER_W))
                c.drawRect(skia.Rect.MakeXYWH(-120, -70, 240, 140), wb.marker(BLACK, 5))
                K.text(c, "考试", -40, -36, 40, "hand", RED)
                for r in range(3):
                    C.line(c, (-95, -2 + r * 26), (95 - r * 30, -2 + r * 26), GRAY, 5)
            if panic:
                for n in range(3):
                    ph = ((T - H.tb(j, 2)) * 1.4 + n * 0.33) % 1.0
                    _sweat(c, cx - 200 + (-75 if n % 2 else 75), gy + 40 - 290 * 0.95 - 30 + ph * 80, 1.0, 1 - ph)
        return None
    b.custom(j, 0, 0.3, desk, sfx="wood_low", gain=0.7)

    def clock(c, kk, T):
        sc = pop_scale(T - H.tb(j, 1))
        if sc <= 0:
            return None
        x, y = cx + 300, cy - 420
        with K.at(c, x, y, 0, sc):
            c.drawCircle(0, 0, 120, K.paint(PAPER_W))
            c.drawCircle(0, 0, 120, wb.marker(BLACK, 9))
            for i in range(12):
                a = i * math.pi / 6
                C.line(c, (math.cos(a) * 96, math.sin(a) * 96), (math.cos(a) * 108, math.sin(a) * 108), BLACK, 5)
            spin = max(0.0, T - H.tb(j, 1)) * 9.0
            C.line(c, (0, 0), (math.cos(spin - 1.57) * 85, math.sin(spin - 1.57) * 85), RED, 8)
            C.line(c, (0, 0), (math.cos(spin / 12 - 1.57) * 55, math.sin(spin / 12 - 1.57) * 55), BLACK, 10)
            c.drawCircle(0, 0, 10, K.paint(BLACK))
            for sg in (-1, 1):
                C.line(c, (sg * 140, -90), (sg * 175, -120), GRAY, 6)
        return None
    b.custom(j, 1, 1.3, clock, sfx="shaker", gain=0.6)

    def pouch(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        x, y = cx + 170, gy - 170
        with K.at(c, x, y, 0, pop_scale(dt)):
            c.drawRoundRect(skia.Rect.MakeXYWH(-90, -40, 180, 80), 30, 30, K.paint("#CFE0F5"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-90, -40, 180, 80), 30, 30, wb.marker(BLUE, 6))
            lid = clamp01(dt / 0.25)
            with K.at(c, -90, -40, -35 * lid):
                c.drawRoundRect(skia.Rect.MakeXYWH(0, -16, 180, 22), 10, 10, K.paint("#CFE0F5"))
                c.drawRoundRect(skia.Rect.MakeXYWH(0, -16, 180, 22), 10, 10, wb.marker(BLUE, 5))
            g = pop_scale(dt - 0.15)
            with K.at(c, 0, -120, 0, g):
                K.text(c, "？", 0, 0, 110, "hand", RED)
        return None
    b.custom(j, 2, 2.3, pouch, sfx="rim", gain=0.8)
    HK._finish(H, j, cx, cy, HK.HOOK_TEXT["dream"], acc, size=128)


HK.HOOKS["dream"] = _hook_dream

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "你也梦过吗", 1),
    ([2, 3], "身边的例子", 2),
    ([4], "身边的例子", 3),
    ([5], "身边的例子", 4),
    ([6, 7], "梦的解析 · 书中例子", 5),
    ([8, 9], "梦的解析 · 书中例子", 6),
    ([10, 11], "书中观点", 7),
    ([12, 13], "书中观点", 8),
    ([14, 15], "书中观点", 9),
    ([16, 17], "书中观点 · 考试梦", 10),
    ([18, 19], "书中的读法", 11),
    ([20, 21, 22], "现在怎么看", 12),
    ([23], "说回我们自己", 13),
    ([24], "做法一 · 示意", 14),
    ([25], "做法二 · 示意", 15),
    ([26], "做法三 · 示意", 16),
    ([27], "这样看梦", 17),
    ([28, 29, 30], "评论区见", 18),
]

THEME = dict(name="月夜蓝格", acc="#3B3A8C", paper="#E9EEF7", pattern="grid", pat="#B9C7DF", grid=80,
             header="circle", hook="dream", move="pullpush", move_s=1.4)
L = C.Lesson("01", SCREENS, drop_screen=2, board_size=(5000, 11600), theme=THEME,
             plan_path=Path(__file__).with_name("PLAN.md"))
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(17)]
Z = 0.72

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899 年出版，书上印 1900 年；中译本《梦的解析》）。",
    "书中例子：吃咸后梦见喝水、小女儿饿了一天梦见草莓（第三章）；梦有两层与“化妆”（凝缩、移置，第六章）；考试梦（第五章）；"
    "拆开逐块联想、批评按词典解梦（第二章）。",
    "现在的研究不支持“每个梦都是愿望的满足”；片中交代为一百多年前的说法。小李为虚构人物，例子均为示意。",
]


# ================================================================ 时间小工具

def nbeats(j):
    return L.BOUNDS[j][1] - L.BOUNDS[j][0]


def kq(j, t_local, lo=0):
    return kb(j, t_local, lo=min(lo, nbeats(j) - 1))


def klast(j, tail=0.35):
    """本屏最后一个能放画面事件的拍：事件做完后到切屏至少还停 1.6 秒。"""
    b0, b1 = L.BOUNDS[j]
    return max(k for k in range(b1 - b0) if core.bt(b0 + k) + tail <= core.bt(b1) - 1.6)


def cap(j, k, tail=0.35):
    return min(k, klast(j, tail))


def nx(j, t_local, prev, gap=1):
    """离 t_local 最近、且至少在 prev 之后 gap 拍的拍号（不超过本屏可用的最后一拍）。"""
    return cap(j, max(kq(j, t_local, prev + gap), prev + gap))


# ================================================================ 画面小工具

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


def _sweat(c, x, y, s=1.0, alpha=1.0):
    p = skia.Path()
    p.moveTo(x, y - 22 * s)
    p.quadTo(x + 16 * s, y + 2 * s, x, y + 12 * s)
    p.quadTo(x - 16 * s, y + 2 * s, x, y - 22 * s)
    c.drawPath(p, K.paint("#BFDDF7", alpha))
    c.drawPath(p, wb.marker(BLUE, 4, alpha))


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


def cloud_path(x, y, w, h):
    """梦泡泡：椭圆主体 + 一圈鼓包（并集），(x, y) 为中心。"""
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    n = 9
    for i in range(n):
        a = 2 * math.pi * i / n
        r = min(w, h) * 0.2
        bx, by = x + math.cos(a) * w * 0.46, y + math.sin(a) * h * 0.44
        q = skia.Path()
        q.addCircle(bx, by, r)
        p = skia.Op(p, q, skia.PathOp.kUnion_PathOp)
    return p


def dream_cloud(c, x, y, w, h, sc, tail_to=None, alpha=1.0):
    """画一个梦泡泡（白底紫线），tail_to=(x, y) 时从泡泡到那儿画三个渐小的小圆。返回是否画了。"""
    if sc <= 0:
        return False
    if tail_to is not None:
        tx, ty = tail_to
        for i, f in enumerate((0.25, 0.55, 0.82)):
            if sc < 0.3 + 0.2 * i:
                continue
            px, py = lerp(x, tx, 0.62 + f * 0.38), lerp(y + h * 0.45, ty, 0.3 + f * 0.7)
            r = 26 - i * 7
            c.drawCircle(px, py, r, K.paint(CLOUD, alpha))
            c.drawCircle(px, py, r, wb.marker(NIGHT, 5, alpha))
    with at_pop(c, x, y, sc):
        p = cloud_path(x, y, w, h)
        c.drawPath(p, K.paint(CLOUD, alpha))
        c.drawPath(p, wb.marker(NIGHT, 8, alpha))
    return True


def moon(c, x, y, r=60, alpha=1.0):
    p = skia.Path()
    p.addCircle(x, y, r)
    q = skia.Path()
    q.addCircle(x + r * 0.45, y - r * 0.3, r * 0.85)
    m = skia.Op(p, q, skia.PathOp.kDifference_PathOp)
    c.drawPath(m, K.paint("#FFE39A", alpha))
    c.drawPath(m, wb.marker(YELLOW, 6, alpha))


def star(c, x, y, r=40, fill="#FFE39A", line=YELLOW, alpha=1.0, rot=0.0):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5 + rot
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    p = P(*pts, close=True)
    c.drawPath(p, K.paint(fill, alpha))
    c.drawPath(p, wb.marker(line, 5, alpha))


def sun(c, x, y, r=50, alpha=1.0):
    c.drawCircle(x, y, r, K.paint("#FFD27A", alpha))
    c.drawCircle(x, y, r, wb.marker(ORANGE, 6, alpha))
    for i in range(8):
        a = i * math.pi / 4
        C.line(c, (x + math.cos(a) * (r + 14), y + math.sin(a) * (r + 14)),
               (x + math.cos(a) * (r + 40), y + math.sin(a) * (r + 40)), ORANGE, 6, alpha)


def bed(c, x, y, w=520, alpha=1.0):
    """床：(x, y) 为床面左端；床头在左。"""
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, 50), K.paint(WOOD, alpha))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, 50), wb.marker("#A9773E", 7, alpha))
    C.line(c, (x, y - 90), (x, y + 110), "#A9773E", 12, alpha)
    C.line(c, (x + w, y - 20), (x + w, y + 110), "#A9773E", 12, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x + 14, y - 46, 110, 46), 20, 20, K.paint(PAPER_W, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x + 14, y - 46, 110, 46), 20, 20, wb.marker(GRAY, 5, alpha))


def sleeper(c, x, y, s, T, t_wake=None, mood="flat", sweat=False):
    """躺在床上的小李（脚在右）：t_wake 之后 0.25 秒内坐起来；被子盖住腰以下。(x, y) 为臀部。"""
    up = ease_out(clamp01((T - t_wake) / 0.25)) if t_wake is not None and T >= t_wake else 0.0
    rot = lerp(-90, 0, up)
    with K.at(c, x, y, rot):
        draw_li(c, 0, 120 * s, s, mood)
    blanket = skia.Rect.MakeXYWH(x - 30, y - 30, 330, 70)
    c.drawRoundRect(blanket, 26, 26, K.paint("#CFE0F5"))
    c.drawRoundRect(blanket, 26, 26, wb.marker(BLUE, 6))
    if sweat and up > 0.9:
        hy = y + 120 * s - 290 * s
        for n in range(3):
            ph = ((T - t_wake) * 1.4 + n * 0.33) % 1.0
            _sweat(c, x + (-70 if n % 2 else 70), hy - 20 + ph * 80, 1.0, 1 - ph)
    a = math.radians(rot)
    vy = (120 - 290) * s                       # 头相对臀部（坐直时）的偏移，随身体转动
    return x - vy * math.sin(a), y + vy * math.cos(a)


def draw_freud(c, x, y, s, mood="flat", alpha=1.0, cigar=True):
    """弗洛伊德：深色西装、白衬衫、圆眼镜、灰白胡子、后退的发际线。(x, y) 为脚底。"""
    hy = y - 290 * s
    torso = skia.Rect.MakeLTRB(x - 60 * s, hy + 50 * s, x + 60 * s, y - 100 * s)
    for foot in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, (x, y - 110 * s), foot, BLACK, 11, alpha)
    c.drawRoundRect(torso, 22 * s, 22 * s, K.paint(SUIT, alpha))
    c.drawRoundRect(torso, 22 * s, 22 * s, wb.marker(BLACK, 7, alpha))
    c.drawPath(P((x - 20 * s, hy + 52 * s), (x, hy + 110 * s), (x + 20 * s, hy + 52 * s), close=True), K.paint(PAPER_W, alpha))
    c.drawCircle(x, hy, 52 * s, K.paint(SKIN, alpha))
    c.drawCircle(x, hy, 52 * s, wb.marker(BLACK, 8, alpha))
    beard = skia.Path()
    beard.moveTo(x - 46 * s, hy + 6 * s)
    beard.quadTo(x - 40 * s, hy + 70 * s, x, hy + 82 * s)
    beard.quadTo(x + 40 * s, hy + 70 * s, x + 46 * s, hy + 6 * s)
    beard.quadTo(x, hy + 34 * s, x - 46 * s, hy + 6 * s)
    c.drawPath(beard, K.paint("#C9C9C9", alpha))
    c.drawPath(beard, wb.marker(GRAY, 5, alpha))
    for sg in (-1, 1):
        c.drawCircle(x + sg * 20 * s, hy - 10 * s, 15 * s, K.paint(PAPER_W, alpha * 0.6))
        c.drawCircle(x + sg * 20 * s, hy - 10 * s, 15 * s, wb.marker(BLACK, 4, alpha))
        c.drawCircle(x + sg * 20 * s, hy - 10 * s, 3.5 * s, K.paint(BLACK, alpha))
        C.line(c, (x + sg * 36 * s, hy - 26 * s), (x + sg * 50 * s, hy - 16 * s), "#9A9A9A", 8, alpha)
    C.line(c, (x - 5 * s, hy - 10 * s), (x + 5 * s, hy - 10 * s), BLACK, 3, alpha)
    if mood == "smile":
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(x - 14 * s, hy + 14 * s, 28 * s, 16 * s), 20, 140)
        c.drawPath(m, wb.marker(BLACK, 5, alpha))
    else:
        C.line(c, (x - 12 * s, hy + 26 * s), (x + 12 * s, hy + 26 * s), BLACK, 5, alpha)
    if cigar:
        C.line(c, (x + 12 * s, hy + 28 * s), (x + 62 * s, hy + 36 * s), "#8A5A2B", 9, alpha)
        c.drawCircle(x + 64 * s, hy + 36 * s, 5 * s, K.paint(RED, alpha))
    rh = (x + 75 * s, hy + 175 * s)
    lh = (x - 75 * s, hy + 175 * s)
    for h_ in (lh, rh):
        C.line(c, (x, hy + 80 * s), h_, SUIT, 12, alpha)


def draw_girl(c, x, y, s, mood="flat", alpha=1.0):
    """小女孩：短裙、两个小辫。(x, y) 为脚底。"""
    hy = y - 220 * s
    for foot in ((x - 30 * s, y), (x + 30 * s, y)):
        C.line(c, (x, y - 70 * s), foot, BLACK, 9, alpha)
    dress = P((x, hy + 40 * s), (x - 60 * s, y - 60 * s), (x + 60 * s, y - 60 * s), close=True)
    c.drawPath(dress, K.paint("#F6C3BE", alpha))
    c.drawPath(dress, wb.marker(RED, 6, alpha))
    for sg in (-1, 1):
        C.line(c, (x, hy + 70 * s), (x + sg * 60 * s, hy + 120 * s), BLACK, 8, alpha)
        c.drawCircle(x + sg * 50 * s, hy - 10 * s, 16 * s, K.paint("#5A3A2A", alpha))
    c.drawCircle(x, hy, 40 * s, K.paint(PAPER_W, alpha))
    c.drawCircle(x, hy, 40 * s, wb.marker(BLACK, 8, alpha))
    for dx in (-13, 13):
        c.drawCircle(x + dx * s, hy - 4 * s, 4 * s, K.paint(BLACK, alpha))
    m = skia.Path()
    if mood == "smile":
        m.addArc(skia.Rect.MakeXYWH(x - 13 * s, hy + 4 * s, 26 * s, 18 * s), 20, 140)
    else:
        m.addArc(skia.Rect.MakeXYWH(x - 12 * s, hy + 14 * s, 24 * s, 14 * s), 200, 140)
    c.drawPath(m, wb.marker(BLACK, 5, alpha))


def exam_paper(c, x, y, w=260, h=320, rot=0.0, title="考试", mark=None, alpha=1.0):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, PAPER_W, BLACK, 6, 6, alpha)
        K.text(c, title, -w / 2 + 70, -h / 2 + 46, 44, "hand", RED, alpha)
        for r in range(4):
            C.line(c, (-w / 2 + 30, -h / 2 + 110 + r * 48), (w / 2 - 30 - (r % 2) * 50, -h / 2 + 110 + r * 48), GRAY, 6,
                   alpha)
        if mark:
            K.text(c, mark, w / 2 - 60, -h / 2 + 56, 80, "hand", RED, alpha)


def pen(c, x, y, rot=-30, s=1.0, alpha=1.0):
    with K.at(c, x, y, rot, s):
        c.drawRoundRect(skia.Rect.MakeXYWH(-70, -12, 120, 24), 6, 6, K.paint("#FFD27A", alpha))
        c.drawRoundRect(skia.Rect.MakeXYWH(-70, -12, 120, 24), 6, 6, wb.marker(BLACK, 4, alpha))
        c.drawPath(P((50, -12), (80, 0), (50, 12), close=True), K.paint(SKIN, alpha))
        c.drawPath(P((50, -12), (80, 0), (50, 12), close=True), wb.marker(BLACK, 4, alpha))


def note_card(c, x, y, w, h, rot=0.0, fill="#FFF1A8", line=ORANGE):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, fill, line, 6, 8)


# ================================================================ 屏 0：开场（钩子）
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：小李睡着，梦泡泡里考场、笔打叉；惊醒坐起一身汗，头顶问号
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_bed = 0
k_cl = nx(j, wt(0, 1, 0.2), k_bed + 1)
k_x = nx(j, wt(0, 2, 0.5), k_cl)
k_wake = nx(j, wt(1, 0, 0.3), k_x)
k_q = nx(j, wt(1, 1, 0.7), k_wake)
BED1 = (cx - 330, cy + 300)
HIP1 = (BED1[0] + 230, BED1[1] - 20)
CL1 = (cx + 110, cy - 280)
L.note("考试", "？", "毕业多年")


def scene1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_bed))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED1[1], sc):
        bed(c, *BED1, 560)
        hx, hy = sleeper(c, *HIP1, 0.8, T, tb(1, k_wake), "sad" if T >= tb(1, k_wake) else "flat", sweat=True)
        if T < tb(1, k_wake):
            for i in range(3):
                f = ((T - tb(1, k_bed)) * 0.7 + i / 3) % 1
                K.text(c, "z", HIP1[0] - 260 + f * 60, HIP1[1] - 120 - f * 120, 40 + i * 8, "hand", GRAY, 1 - f)
        else:
            dt = T - tb(1, k_wake)
            if dt < 0.5:
                for i in range(6):
                    a = -math.pi / 2 + (i - 2.5) * 0.45
                    r0 = 70 + dt * 160
                    C.line(c, (hx + math.cos(a) * r0, hy + math.sin(a) * r0),
                           (hx + math.cos(a) * (r0 + 40), hy + math.sin(a) * (r0 + 40)), RED, 6, 1 - dt / 0.5)
    return None


ev(j, k_bed, scene1, "wood_low", 0.7)


def cloud1(c, kk, T, cx=cx, cy=cy):
    t0 = tb(1, k_cl)
    out = 1 - ease_in_out(clamp01((T - tb(1, k_wake)) / 0.3))
    sc = pop_scale(T - t0) * out
    if not dream_cloud(c, CL1[0], CL1[1], 760, 520, sc, tail_to=(HIP1[0] - 280, HIP1[1] - 80)):
        return None
    with at_pop(c, CL1[0], CL1[1], sc):
        exam_paper(c, CL1[0] - 150, CL1[1] + 10, 230, 280, -5)
        x0, y0 = CL1[0] + 170, CL1[1] - 40
        c.drawCircle(x0, y0, 80, K.paint(PAPER_W))
        c.drawCircle(x0, y0, 80, wb.marker(BLACK, 7))
        spin = max(0.0, T - t0) * 6.0
        C.line(c, (x0, y0), (x0 + math.cos(spin) * 60, y0 + math.sin(spin) * 60), RED, 7)
        pen(c, CL1[0] + 160, CL1[1] + 120, -20, 0.9)
        if T >= tb(1, k_x):
            g = pop_scale(T - tb(1, k_x))
            with K.at(c, CL1[0] + 160, CL1[1] + 120, 0, g):
                c.drawPath(cross(0, 0, 70), wb.marker(RED, 12))
    return None


ev(j, k_cl, cloud1, "pop", 0.7)
b.hit(j, k_x, "rim", 0.85, "梦里笔不见了")
b.hit(j, k_wake, "kick", 0.85, "惊醒坐起")
b.shots[j].shake = [(k_wake, 9.0)]


def q1(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(1, k_q))
    if sc <= 0:
        return None
    with K.at(c, HIP1[0] + 150, HIP1[1] - 470, 8, sc):
        K.text(c, "？", 0, 0, 220, "hand", NIGHT)
    with K.at(c, cx + 250, cy - 360, -4, pop_scale(T - tb(1, k_q) - 0.2)):
        box(c, 0, 0, 360, 110, PAPER_W, NIGHT, 6, 50)
        K.text(c, "什么意思", 0, 2, 60, "hand", NIGHT)
    return None


L.note("什么意思")
ev(j, k_q, q1, "ding", 0.75)

# ================================================================ 屏 2：领导催方案 → 梦里被一张大方案追着跑（drop：方案砸在身后）
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_icons = 1
k_boss = kq(j, wt(3, 0, 0.3), k_icons + 1)
k_moon = max(k_boss + 2, KD - 5)
k_run = max(k_moon + 1, KD - 3)
GY2 = cy + 420
L.note("梦", "明天交方案", "方案", "追着跑")


def icons2(c, kk, T, cx=cx, cy=cy):
    for i in range(3):
        sc = pop_scale(T - tb(2, k_icons) - i * 0.12)
        if sc > 0:
            x = cx - 220 + i * 220
            dream_cloud(c, x, cy - 520, 170, 110, sc)
            with at_pop(c, x, cy - 520, sc):
                K.text(c, "梦", x, cy - 518, 56, "hand", NIGHT)
    return None


ev(j, k_icons, icons2, "pop", 0.6)


def boss2(c, sc, T, cx=cx, cy=cy):
    x = cx - 320
    with at_pop(c, x, GY2 - 300, sc):
        sun(c, x - 170, cy - 300, 40)
        draw_boss(c, x, GY2 - 260, 0.62, rh=(x + 90, GY2 - 260 - 290 * 0.62 + 40), mood="flat")
        box(c, x + 40, cy - 170, 340, 100, PAPER_W, BLACK, 6, 40)
        K.text(c, "明天交方案", x + 40, cy - 168, 54, "hand", RED)
    return None


ev(j, k_boss, pop_fn(j, k_boss, boss2), "wood_high", 0.7)


def night2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_moon))
    if sc <= 0:
        return None
    with at_pop(c, cx + 340, cy - 330, sc):
        moon(c, cx + 340, cy - 330, 60)
        star(c, cx + 200, cy - 380, 22)
        star(c, cx + 450, cy - 250, 16)
    return None


ev(j, k_moon, night2, "wood_high", 0.6)


def chase2(c, kk, T, cx=cx, cy=cy):
    t0 = tb(2, k_run)
    if T < t0:
        return None
    sc = pop_scale(T - t0)
    run_t = T - t0
    x_li = cx + 20 + min(run_t, 3.0) * 30
    ph = run_t * 3.2
    with at_pop(c, cx + 80, GY2, sc):
        C.line(c, (cx - 120, GY2), (cx + 560, GY2), BLACK, 7)
        # 小李跑：腿手摆动
        s = 0.62
        hy = GY2 - 290 * s - abs(math.sin(ph * math.pi)) * 14
        hip = (x_li, GY2 - 120 * s)
        sw = math.sin(ph * math.pi)
        for sg in (1, -1):
            C.line(c, hip, (x_li + sg * sw * 50, GY2), BLACK, 9)
            C.line(c, (x_li, hy + 80 * s), (x_li - sg * sw * 50, hy + 140 * s), BLACK, 9)
        C.line(c, (x_li, hy + 40 * s), hip, BLACK, 9)
        c.drawCircle(x_li, hy, 40 * s * 1.1, K.paint(PAPER_W))
        c.drawCircle(x_li, hy, 40 * s * 1.1, wb.marker(BLACK, 8))
        c.drawPath(P((x_li - 14, hy + 16), (x_li + 14, hy + 10)), wb.marker(BLACK, 5))
        _sweat(c, x_li - 50, hy - 10 + (run_t * 60) % 40, 0.9)
        # 大方案纸追上来
        land = tb(2, KD)
        if T < land:
            f = clamp01((T - t0) / max(0.1, land - t0))
            px, py = lerp(cx - 120, x_li - 210, f), GY2 - 280 - math.sin(f * math.pi * 3) * 30
            rot = -12 + 8 * math.sin(T * 9)
        else:
            px, py, rot = x_li - 230, GY2 - 200, -6
        with K.at(c, px, py, rot, 1.0 if T < land else C.slam_scale(T - land)):
            box(c, 0, 0, 260, 330, PAPER_W, BLACK, 8, 8)
            K.text(c, "方案", 0, -100, 64, "hand", RED)
            for dx in (-50, 50):
                c.drawCircle(dx, -20, 16, K.paint(BLACK))
                C.line(c, (dx - 30, -55), (dx + 26, -40 if dx < 0 else -70), BLACK, 7)
            m = skia.Path()
            m.addArc(skia.Rect.MakeXYWH(-50, 30, 100, 50), 200, 140)
            c.drawPath(m, wb.marker(BLACK, 7))
    return None


ev(j, k_run, chase2, "shaker", 0.6)
ev(j, KD, L.slam_text("追着跑", cx + 260, cy - 120, 120, RED, j, KD, rot=-6), "kick", 0.95)

# ================================================================ 屏 3：手机里老同学合照 → 梦回高中教室
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_ph = 0
k_cl3 = nx(j, wt(4, 1, 0.2), k_ph + 1)
k_bd = nx(j, wt(4, 1, 0.6), k_cl3)
k_li3 = nx(j, wt(4, 1, 0.95), k_bd)
L.note("老同学", "高三")


def phone3(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 330, cy + 200
    with at_pop(c, x, y, sc):
        box(c, x, y, 300, 520, "#2E2A28", BLACK, 6, 40)
        box(c, x, y - 10, 260, 430, "#E4EEF8", BLUE, 4, 16)
        K.text(c, "老同学", x, y - 180, 40, "sans_medium", BLUE)
        for i, dx in enumerate((-70, 0, 70)):
            hx, hy = x + dx, y - 40 - (i % 2) * 14
            c.drawCircle(hx, hy, 30, K.paint(PAPER_W))
            c.drawCircle(hx, hy, 30, wb.marker(BLACK, 6))
            c.drawPath(P((hx - 36, hy + 90), (hx - 30, hy + 40), (hx + 30, hy + 40), (hx + 36, hy + 90)), wb.marker(BLACK, 6))
            m = skia.Path()
            m.addArc(skia.Rect.MakeXYWH(hx - 12, hy, 24, 14), 20, 140)
            c.drawPath(m, wb.marker(BLACK, 4))
        C.line(c, (x - 60, y + 230), (x + 60, y + 230), GRAY, 6)
    return None


ev(j, k_ph, pop_fn(j, k_ph, phone3), "wood_low", 0.7)
CL3 = (cx + 170, cy - 180)


def cloud3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_cl3))
    if not dream_cloud(c, CL3[0], CL3[1], 780, 640, sc, tail_to=(cx - 300, cy - 100)):
        return None
    with at_pop(c, CL3[0], CL3[1], sc):
        g = pop_scale(T - tb(3, k_bd))
        if g > 0:
            with K.at(c, CL3[0], CL3[1] - 120, 0, g):
                box(c, 0, 0, 460, 200, "#2F4A3A", "#6B4A2A", 10, 6)
                K.text(c, "高三", -120, -40, 56, "hand", "#FFFFFF")
                C.line(c, (-40, 30), (180, 30), "#FFFFFF", 5, 0.8)
                C.line(c, (-40, 70), (120, 70), "#FFFFFF", 5, 0.8)
        g2 = pop_scale(T - tb(3, k_li3))
        if g2 > 0:
            with K.at(c, CL3[0], CL3[1] + 150, 0, g2):
                for dx in (-220, 0, 220):
                    c.drawRect(skia.Rect.MakeXYWH(dx - 80, 30, 160, 26), K.paint(WOOD))
                    c.drawRect(skia.Rect.MakeXYWH(dx - 80, 30, 160, 26), wb.marker("#A9773E", 5))
                draw_li(c, 0, 120, 0.45, "o")
    return None


ev(j, k_cl3, cloud3, "pop", 0.7)
b.hit(j, k_bd, "wood_high", 0.7, "黑板出现")
b.hit(j, k_li3, "ding", 0.75, "又坐回高中教室")

# ================================================================ 屏 4：饿着睡，梦里火锅，筷子刚伸过去就醒（泡泡破掉）
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_bed4 = 0
k_gu = nx(j, wt(5, 0, 0.6), k_bed4 + 1)
k_pot = nx(j, wt(5, 1, 0.3), k_gu)
k_chop = nx(j, wt(5, 2, 0.4), k_pot)
k_pop4 = nx(j, wt(5, 3, 0.4), k_chop)
BED4 = (cx - 380, cy + 360)
HIP4 = (BED4[0] + 230, BED4[1] - 20)
CL4 = (cx + 120, cy - 250)
L.note("咕", "醒了")


def scene4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, k_bed4))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED4[1], sc):
        bed(c, *BED4, 560)
        sleeper(c, *HIP4, 0.8, T, tb(4, k_pop4), "sad" if T >= tb(4, k_pop4) else "flat")
        if T >= tb(4, k_gu):
            g = pop_scale(T - tb(4, k_gu))
            with K.at(c, HIP4[0] - 10, HIP4[1] - 120, -6, g):
                K.text(c, "咕", 0, 0, 70, "hand", ORANGE)
    return None


ev(j, k_bed4, scene4, "wood_low", 0.7)
b.hit(j, k_gu, "tom", 0.7, "肚子咕咕叫")


def cloud4(c, kk, T, cx=cx, cy=cy):
    t_pop = tb(4, k_pop4)
    sc = pop_scale(T - tb(4, k_pot))
    if T >= t_pop:
        dt = T - t_pop
        if dt > 0.3:
            return None
        for i in range(10):
            a = i * math.pi / 5
            r = 200 + dt * 900
            c.drawCircle(CL4[0] + math.cos(a) * r, CL4[1] + math.sin(a) * r * 0.7, 20 * (1 - dt / 0.3),
                         wb.marker(NIGHT, 5, 1 - dt / 0.3))
        return None
    if not dream_cloud(c, CL4[0], CL4[1], 760, 560, sc, tail_to=(HIP4[0] - 300, HIP4[1] - 60)):
        return None
    with at_pop(c, CL4[0], CL4[1], sc):
        x, y = CL4[0], CL4[1] + 60
        pot = skia.Path()
        pot.addArc(skia.Rect.MakeXYWH(x - 190, y - 120, 380, 240), 0, 180)
        pot.close()
        c.drawPath(pot, K.paint("#F6C3BE"))
        c.drawPath(pot, wb.marker(RED, 8))
        C.line(c, (x - 210, y), (x + 210, y), BLACK, 9)
        C.line(c, (x, y), (x, y - 18), BLACK, 9)
        for i in range(4):
            c.drawCircle(x - 120 + i * 80, y + 34, 18, K.paint(RED))
        for i in range(3):
            ph = (T * 0.8 + i / 3) % 1
            sx = x - 90 + i * 90
            stm = P((sx, y - 30 - ph * 10), (sx + 20, y - 80 - ph * 40), (sx - 10, y - 130 - ph * 50))
            c.drawPath(stm, wb.marker(GRAY, 6, 1 - ph))
        if T >= tb(4, k_chop):
            f = ease_out(clamp01((T - tb(4, k_chop)) / 0.5))
            ox = lerp(x + 360, x + 120, f)
            for dy in (-14, 14):
                C.line(c, (ox + 200, y - 160 + dy), (ox, y - 40 + dy), "#A9773E", 8)
    return None


ev(j, k_pot, cloud4, "pop", 0.7)
b.hit(j, k_chop, "wood_high", 0.7, "筷子伸过去")
ev(j, k_pop4, L.slam_text("醒了", cx + 230, cy - 260, 130, RED, j, k_pop4, rot=5), "kick", 0.85)
b.shots[j].shake = [(k_pop4, 8.0)]

# ================================================================ 屏 5：一百多年前，弗洛伊德；书《梦的解析》
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_100 = kq(j, wt(6, 0, 0.4), 0)
k_fr = nx(j, wt(6, 1, 0.5), k_100)
k_nm = nx(j, wt(6, 2, 0.5), k_fr)
k_bk = nx(j, wt(7, 1, 0.3), k_nm)
L.note("一百多年前", "弗洛伊德", "梦的解析", "医生")


def year5(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 300, cy - 470, sc):
        box(c, cx - 300, cy - 470, 380, 110, "#F1E3CB", "#A9773E", 6, 16)
        K.text(c, "一百多年前", cx - 300, cy - 468, 58, "hand", "#7A4A1A")
    return None


ev(j, k_100, pop_fn(j, k_100, year5), "wood_high", 0.7)
FR5 = (cx - 220, cy + 400)


def freud5(c, sc, T, cx=cx, cy=cy):
    x, y = FR5
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 1.05)
        box(c, x - 210, y - 520, 150, 70, PAPER_W, BLUE, 5, 30)
        K.text(c, "医生", x - 210, y - 518, 42, "sans_medium", BLUE)
    return None


ev(j, k_fr, pop_fn(j, k_fr, freud5), "wood_low", 0.75)
ev(j, k_nm, L.slam_text("弗洛伊德", FR5[0], FR5[1] + 80, 92, NIGHT, j, k_nm), "kick", 0.85)


def book5(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(5, k_bk))
    if sc <= 0:
        return None
    x, y = cx + 300, cy + 60
    with K.at(c, x, y, 6, sc):
        box(c, 0, 0, 340, 460, NIGHT, BLACK, 7, 12)
        box(c, 0, -20, 280, 380, "#4B4AA6", "#2A2970", 4, 8)
        K.text(c, "梦的", 0, -100, 78, "serif_black", "#FFE39A")
        K.text(c, "解析", 0, -10, 78, "serif_black", "#FFE39A")
        moon(c, 0, 120, 44)
        star(c, 70, 90, 14)
    sparkle(c, x, y - 300, T - tb(5, k_bk), YELLOW, 8, 60, 140)
    return None


ev(j, k_bk, book5, "ding", 0.8)

# ================================================================ 屏 6：咸鱼 → 梦里喝水；小女儿 → 梦里草莓
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_fish = kq(j, wt(8, 0, 0.7), 0)
k_salt = nx(j, wt(8, 0, 0.95), k_fish)
k_water = nx(j, wt(8, 1, 0.6), k_salt)
k_girl = nx(j, wt(9, 0, 0.4), k_water)
k_berry = nx(j, wt(9, 1, 0.6), k_girl)
L.note("咸", "饿了一天")
C6L, C6R = (cx - 290, cy - 260), (cx + 290, cy - 260)


def fish6(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 290, cy + 260
    with at_pop(c, x, y, sc):
        c.drawOval(skia.Rect.MakeXYWH(x - 190, y - 40, 380, 90), K.paint(PAPER_W))
        c.drawOval(skia.Rect.MakeXYWH(x - 190, y - 40, 380, 90), wb.marker(BLACK, 6))
        for dx in (-60, 60):
            f = skia.Path()
            f.addOval(skia.Rect.MakeXYWH(x + dx - 70, y - 18, 120, 40))
            f.addPath(P((x + dx + 50, y + 2), (x + dx + 80, y - 18), (x + dx + 80, y + 22), close=True))
            c.drawPath(f, K.paint("#C9D6E8"))
            c.drawPath(f, wb.marker(BLUE, 5))
            c.drawCircle(x + dx - 40, y - 2, 5, K.paint(BLACK))
        K.text(c, "晚饭", x, y + 110, 46, "sans_medium", GRAY)
    return None


ev(j, k_fish, pop_fn(j, k_fish, fish6), "wood_low", 0.7)
ev(j, k_salt, L.slam_text("咸", cx - 90, cy + 140, 110, RED, j, k_salt, rot=-8), "rim", 0.8)


def water6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_water))
    if not dream_cloud(c, *C6L, 480, 420, sc, tail_to=(cx - 290, cy + 150)):
        return None
    with at_pop(c, *C6L, sc):
        x, y = C6L
        cup = P((x - 70, y - 110), (x + 70, y - 110), (x + 52, y + 110), (x - 52, y + 110), close=True)
        lvl = 1 - 0.5 * clamp01((T - tb(6, k_water) - 0.3) / 1.5)
        water = P((x - 70 + 18 * (1 - lvl), y + 110 - 220 * lvl), (x + 70 - 18 * (1 - lvl), y + 110 - 220 * lvl),
                  (x + 52, y + 110), (x - 52, y + 110), close=True)
        c.drawPath(water, K.paint("#BFDDF7"))
        c.drawPath(cup, wb.marker(BLUE, 7))
        for i in range(2):
            ph = (T * 1.2 + i * 0.5) % 1
            _sweat(c, x + 110 + i * 30, y - 80 + ph * 60, 0.9, 1 - ph)
    return None


ev(j, k_water, water6, "pop", 0.75)


def girl6(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 290, cy + 400
    with at_pop(c, x, y, sc):
        draw_girl(c, x, y, 1.0, "flat")
        box(c, x, y + 70, 220, 70, PAPER_W, GRAY, 4, 30)
        K.text(c, "饿了一天", x, y + 72, 40, "sans_medium", GRAY)
    return None


ev(j, k_girl, pop_fn(j, k_girl, girl6), "wood_high", 0.7)


def berry6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_berry))
    if not dream_cloud(c, *C6R, 480, 420, sc, tail_to=(cx + 290, cy + 120)):
        return None
    with at_pop(c, *C6R, sc):
        x, y = C6R
        bp = skia.Path()
        bp.moveTo(x, y + 120)
        bp.cubicTo(x - 150, y + 20, x - 120, y - 110, x, y - 80)
        bp.cubicTo(x + 120, y - 110, x + 150, y + 20, x, y + 120)
        c.drawPath(bp, K.paint("#E5484D"))
        c.drawPath(bp, wb.marker(RED, 7))
        for r_ in range(3):
            for q in range(3 - (r_ == 2)):
                c.drawCircle(x - 50 + q * 50 + (r_ == 2) * 25, y - 30 + r_ * 45, 6, K.paint("#FFE39A"))
        c.drawPath(P((x - 60, y - 95), (x, y - 70), (x + 60, y - 95), (x, y - 120), close=True), K.paint("#3FA34D"))
    sparkle(c, C6R[0], C6R[1], T - tb(6, k_berry), YELLOW, 8, 140, 220)
    return None


ev(j, k_berry, berry6, "ding", 0.8)

# ================================================================ 屏 7：“愿望的满足”；白天够不着的星星，梦里抱住
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_card = kq(j, wt(10, 1, 0.6), 0)
k_day = nx(j, wt(11, 0, 0.3), k_card)
k_night = nx(j, wt(11, 1, 0.3), k_day)
k_hug = nx(j, wt(11, 1, 0.9), k_night)
GY7 = cy + 440
L.note("愿望的满足", "白天", "晚上")


def card7(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(7, k_card))
    if sc <= 0:
        return None
    with K.at(c, cx, cy - 420, -2, sc):
        box(c, 0, 0, 760, 180, PAPER_W, NIGHT, 9, 30)
        K.text(c, "愿望的满足", 0, 4, 110, "hand", NIGHT)
    return None


ev(j, k_card, card7, "kick", 0.85)
b.shots[j].shake = [(k_card, 7.0)]


def day7(c, sc, T, cx=cx, cy=cy):
    x = cx - 290
    with at_pop(c, x, GY7, sc):
        C.line(c, (x - 230, GY7), (x + 230, GY7), BLACK, 7)
        sun(c, x - 160, cy - 200, 40)
        K.text(c, "白天", x + 80, cy - 200, 50, "hand", ORANGE)
        reach = 1 + 0.06 * math.sin(T * 6)
        hy = GY7 - 290 * 0.8
        draw_li(c, x, GY7, 0.8, "sad", rh=(x + 50, hy - 90 * reach), lh=(x - 70, hy + 140))
        star(c, x + 70, cy - 70, 46)
        C.line(c, (x + 50, hy - 100), (x + 60, cy - 30), GRAY, 4, 0.6)
    return None


ev(j, k_day, pop_fn(j, k_day, day7), "wood_low", 0.7)


def night7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_night))
    x, y = cx + 300, cy + 60
    if not dream_cloud(c, x, y, 520, 640, sc):
        return None
    with at_pop(c, x, y, sc):
        moon(c, x + 150, y - 230, 44)
        K.text(c, "晚上", x - 120, y - 230, 50, "hand", NIGHT)
        hug = T >= tb(7, k_hug)
        s = 0.7
        fy = y + 230
        hy = fy - 290 * s
        if hug:
            draw_li(c, x, fy, s, "smile", lh=(x - 20, hy + 120), rh=(x + 20, hy + 120))
            star(c, x, hy + 110, 54)
        else:
            draw_li(c, x, fy, s, "flat")
            star(c, x + 110, hy - 40, 44)
    if T >= tb(7, k_hug):
        sparkle(c, x, y + 30, T - tb(7, k_hug), YELLOW, 10, 80, 180)
    return None


ev(j, k_night, night7, "pop", 0.7)
b.hit(j, k_hug, "ding", 0.8, "梦里抱住星星")

# ================================================================ 屏 8：乱糟糟的梦；梦有两层：记得的故事 / 底下的意思
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_mess = kq(j, wt(12, 0, 0.5), 0)
k_weird = nx(j, wt(12, 2, 0.3), k_mess)
k_two = nx(j, wt(13, 0, 0.35), k_weird)
k_top = nx(j, wt(13, 0, 0.8), k_two)
k_bot = nx(j, wt(13, 1, 0.6), k_top)
L.note("又乱又怪", "两层", "记得的故事", "底下的意思")
CL8 = (cx, cy - 250)


def mess8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_mess))
    if not dream_cloud(c, *CL8, 860, 520, sc):
        return None
    x, y = CL8
    with at_pop(c, x, y, sc):
        spin = (T - tb(8, k_mess)) * 0.8
        items = [(-250, -60), (-80, 90), (100, -80), (260, 60), (0, -10)]
        for i, (dx, dy) in enumerate(items):
            with K.at(c, x + dx, y + dy, math.degrees(spin * (1 if i % 2 else -1)) * 0.3):
                if i == 0:
                    c.drawCircle(0, 0, 50, K.paint(PAPER_W))
                    c.drawCircle(0, 0, 50, wb.marker(BLACK, 6))
                    C.line(c, (0, 0), (0, -36), RED, 6)
                elif i == 1:
                    c.drawOval(skia.Rect.MakeXYWH(-70, -22, 120, 44), K.paint("#C9D6E8"))
                    c.drawOval(skia.Rect.MakeXYWH(-70, -22, 120, 44), wb.marker(BLUE, 5))
                elif i == 2:
                    star(c, 0, 0, 40)
                elif i == 3:
                    c.drawRect(skia.Rect.MakeXYWH(-50, -40, 100, 80), K.paint("#F6C3BE"))
                    c.drawRect(skia.Rect.MakeXYWH(-50, -40, 100, 80), wb.marker(RED, 5))
                else:
                    c.drawPath(wb.scribble(-60, -40, 120, 80, 6), wb.marker(GRAY, 6))
    return None


ev(j, k_mess, mess8, "pop", 0.7)
ev(j, k_weird, L.stamp("又乱又怪", cx + 260, cy - 520, 56, j, k_weird, color=RED, rot=6), "rim", 0.85)
LY8 = cy + 100


def layers8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_two))
    if sc <= 0:
        return None
    with at_pop(c, cx, LY8 + 180, sc):
        K.text(c, "两层", cx - 420, LY8 + 180, 64, "hand", NIGHT)
        C.line(c, (cx - 340, LY8 + 180), (cx + 520, LY8 + 180), NIGHT, 7)
        g1 = pop_scale(T - tb(8, k_top))
        if g1 > 0:
            with K.at(c, cx + 90, LY8 + 80, 0, g1):
                box(c, 0, 0, 520, 120, PAPER_W, BLACK, 6, 20)
                K.text(c, "记得的故事", 0, 2, 60, "hand", BLACK)
        g2 = pop_scale(T - tb(8, k_bot))
        if g2 > 0:
            with K.at(c, cx + 90, LY8 + 300, 0, g2):
                box(c, 0, 0, 520, 140, "#E4E2F6", NIGHT, 8, 20)
                K.text(c, "底下的意思", 0, 2, 68, "hand", NIGHT)
            for i in range(3):
                C.line(c, (cx - 120 + i * 120, LY8 + 140), (cx - 120 + i * 120, LY8 + 220), NIGHT, 5, g2)
    return None


ev(j, k_two, layers8, "wood_high", 0.7)
b.hit(j, k_top, "pop", 0.65, "上层：记得的故事")
b.hit(j, k_bot, "ding", 0.8, "下层：底下的意思")

# ================================================================ 屏 9：意思戴上面具；三个人捏成一个；大石头换成小纽扣
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_mean = kq(j, wt(14, 0, 0.3), 0)
k_mask = nx(j, wt(14, 1, 0.5), k_mean)
k_three = nx(j, wt(15, 0, 0.2), k_mask)
k_merge = nx(j, wt(15, 0, 0.9), k_three)
k_rock = nx(j, wt(15, 1, 0.5), k_merge)
k_btn = nx(j, wt(15, 2, 0.7), k_rock)
L.note("意思", "化妆", "要紧的事", "小事")


def mean9(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 260, cy - 340
    with at_pop(c, x, y, sc):
        box(c, x, y, 300, 200, "#E4E2F6", NIGHT, 8, 24)
        K.text(c, "意思", x, y + 4, 80, "hand", NIGHT)
        if T >= tb(9, k_mask):
            f = ease_out(clamp01((T - tb(9, k_mask)) / 0.3))
            my = lerp(y - 260, y - 10, f)
            mk = skia.Path()
            mk.addOval(skia.Rect.MakeXYWH(x - 170, my - 70, 340, 140))
            c.drawPath(mk, K.paint("#F6C3BE"))
            c.drawPath(mk, wb.marker(RED, 7))
            for dx in (-70, 70):
                c.drawOval(skia.Rect.MakeXYWH(x + dx - 40, my - 20, 80, 40), K.paint("#2E2A28"))
            for sg in (-1, 1):
                C.line(c, (x + sg * 170, my), (x + sg * 230, my - 50), RED, 5)
            K.text(c, "化妆", x + 260, my - 80, 54, "hand", RED, f)
    return None


ev(j, k_mean, pop_fn(j, k_mean, mean9), "wood_high", 0.7)
b.hit(j, k_mask, "rim", 0.8, "戴上面具")
PEOPLE9 = (cx + 260, cy - 120)


def people9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k_three))
    if sc <= 0:
        return None
    x, y = PEOPLE9
    m = ease_in_out(clamp01((T - tb(9, k_merge)) / 0.4))
    with at_pop(c, x, y, sc):
        if m < 1:
            for i, (dx, col) in enumerate(((-150, RED), (0, BLUE), (150, GREEN))):
                xx = x + dx * (1 - m)
                hy = y - 120
                c.drawCircle(xx, hy, 40, K.paint(PAPER_W, 1 - m * 0.6))
                c.drawCircle(xx, hy, 40, wb.marker(col, 7, 1 - m * 0.6))
                C.line(c, (xx, hy + 40), (xx, y + 40), col, 8, 1 - m * 0.6)
                if i == 0:
                    C.line(c, (xx - 50, hy - 36), (xx + 50, hy - 36), RED, 10, 1 - m)
                elif i == 1:
                    for sg in (-1, 1):
                        c.drawCircle(xx + sg * 15, hy - 4, 11, wb.marker(BLUE, 4, 1 - m))
                else:
                    C.line(c, (xx - 20, hy + 22), (xx + 20, hy + 22), GREEN, 6, 1 - m)
        if m > 0:
            hy = y - 120
            g = lerp(0.6, 1.0, m)
            with K.at(c, x, y, 0, g):
                c.drawCircle(x - x, hy - y, 48, K.paint(PAPER_W))
                c.drawCircle(0, hy - y, 48, wb.marker(NIGHT, 8))
                C.line(c, (-56, hy - y - 42), (56, hy - y - 42), RED, 10)
                for sg in (-1, 1):
                    c.drawCircle(sg * 17, hy - y - 4, 12, wb.marker(BLUE, 4))
                C.line(c, (-20, hy - y + 26), (20, hy - y + 26), GREEN, 6)
                C.line(c, (0, hy - y + 48), (0, 40), NIGHT, 9)
        K.text(c, "3 → 1", x, y + 110, 54, "hand", NIGHT, m)
    return None


L.note("3 → 1")
ev(j, k_three, people9, "wood_low", 0.7)
b.hit(j, k_merge, "clap", 0.8, "三个人捏成一个")
GY9 = cy + 420


def rock9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k_rock))
    if sc <= 0:
        return None
    sw = ease_in_out(clamp01((T - tb(9, k_btn)) / 0.35)) if T >= tb(9, k_btn) else 0.0
    x0, x1 = cx - 280, cx + 280
    with at_pop(c, cx, GY9, sc):
        rp = P((x0 - 150, GY9), (x0 - 130, GY9 - 150), (x0 - 20, GY9 - 210), (x0 + 120, GY9 - 160), (x0 + 150, GY9),
               close=True)
        c.drawPath(rp, K.paint("#B8BEC9", 1 - sw * 0.6))
        c.drawPath(rp, wb.marker(BLACK, 8, 1 - sw * 0.6))
        K.text(c, "要紧的事", x0, GY9 - 90, 52, "hand", BLACK, 1 - sw * 0.5)
        c.drawPath(wb.arrow((x0 + 180, GY9 - 100), (x1 - 120, GY9 - 100), 0.15, 34), wb.marker(NIGHT, 7))
        if sw > 0:
            with K.at(c, x1, GY9 - 60, 0, pop_scale(T - tb(9, k_btn))):
                c.drawCircle(0, 0, 40, K.paint("#F2B705"))
                c.drawCircle(0, 0, 40, wb.marker(ORANGE, 6))
                for dx, dy in ((-12, -12), (12, -12), (-12, 12), (12, 12)):
                    c.drawCircle(dx, dy, 6, K.paint(ORANGE))
                K.text(c, "小事", 0, 90, 52, "hand", ORANGE)
    return None


ev(j, k_rock, rock9, "wood_low", 0.7)
b.hit(j, k_btn, "pop", 0.75, "换成一颗小纽扣")

# ================================================================ 屏 10：考试梦——回到开头的考场；旧卷子上一个“过”；大手拍肩“能行”
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_room = kq(j, wt(16, 0, 0.5), 0)
k_old = nx(j, wt(16, 1, 0.4), k_room)
k_pass = nx(j, wt(16, 1, 0.9), k_old)
k_pat = nx(j, wt(17, 0, 0.5), k_pass)
k_ok = nx(j, wt(17, 1, 0.5), k_pat)
GY10 = cy + 380
LI10 = (cx - 260, GY10 + 40, 0.9)
L.note("考试梦", "当年", "过", "能行")


def room10(c, sc, T, cx=cx, cy=cy):
    x, y, s = LI10
    pat = T >= tb(10, k_pat)
    with at_pop(c, cx, GY10, sc):
        draw_li(c, x, y, s, "smile" if T >= tb(10, k_ok) else "sad")
        top = skia.Rect.MakeXYWH(x - 240, GY10 - 120, 560, 34)
        c.drawRect(top, K.paint(WOOD))
        c.drawRect(top, wb.marker("#A9773E", 7))
        for lx in (x - 210, x + 290):
            C.line(c, (lx, GY10 - 86), (lx, GY10 + 60), "#A9773E", 9)
        exam_paper(c, x + 40, GY10 - 190, 220, 130, -4)
        if not pat:
            for n in range(3):
                ph = (T * 1.4 + n * 0.33) % 1.0
                _sweat(c, x + (-70 if n % 2 else 70), y - 290 * s - 20 + ph * 70, 1.0, 1 - ph)
        K.text(c, "考试梦", cx - 300, cy - 500, 64, "hand", NIGHT)
    return None


ev(j, k_room, pop_fn(j, k_room, room10), "wood_low", 0.7)
OLD10 = (cx + 270, cy - 220)


def old10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_old))
    if sc <= 0:
        return None
    x, y = OLD10
    with K.at(c, x, y, 5, sc):
        exam_paper(c, 0, 0, 300, 380, 0, "当年", None)
        c.drawRect(skia.Rect.MakeXYWH(-150, -190, 300, 380), K.paint("#E3C9A0", 0.25))
    return None


ev(j, k_old, old10, "wood_high", 0.7)
ev(j, k_pass, L.stamp("过", OLD10[0] + 60, OLD10[1] + 60, 110, j, k_pass, color=RED, rot=-10), "kick", 0.85)
b.shots[j].shake = [(k_pass, 7.0)]


def hand10(c, kk, T, cx=cx, cy=cy):
    t0 = tb(10, k_pat)
    if T < t0:
        return None
    x, y, s = LI10
    sx, sy = x + 30, y - 290 * s + 90
    f = ease_out(clamp01((T - t0) / 0.3))
    pat = 12 * max(0.0, math.sin((T - t0) * 9)) * math.exp(-(T - t0) * 1.2)
    hx, hy = lerp(sx + 320, sx + 95, f), lerp(sy - 260, sy + 5, f) + pat
    C.line(c, (hx + 60, hy - 40), (hx + 300, hy - 220), ORANGE, 16)
    c.drawRoundRect(skia.Rect.MakeXYWH(hx - 60, hy - 50, 130, 100), 40, 40, K.paint(SKIN))
    c.drawRoundRect(skia.Rect.MakeXYWH(hx - 60, hy - 50, 130, 100), 40, 40, wb.marker(ORANGE, 6))
    return None


ev(j, k_pat, hand10, "wood_high", 0.7)
ev(j, k_ok, L.pop_bubble("明天也能行", cx + 230, cy + 160, j, k_ok, 60, GREEN, tail=-1), "ding", 0.8)

# ================================================================ 屏 11：梦拆成拼图，每块“想到什么？”；解梦词典打叉；同一样东西，两个人意思不一样
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_pz = kq(j, wt(18, 1, 0.5), 0)
k_ask = nx(j, wt(18, 2, 0.75), k_pz)
k_dict = nx(j, wt(19, 1, 0.3), k_ask)
k_xd = nx(j, wt(19, 1, 0.9), k_dict)
k_key = nx(j, wt(19, 3, 0.3), k_xd)
k_diff = nx(j, wt(19, 4, 0.5), k_key)
L.note("想到什么？", "解梦词典", "不一样")
PZ = (cx - 160, cy - 300)


def puzzle11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_pz))
    if sc <= 0:
        return None
    x, y = PZ
    spread = ease_out(clamp01((T - tb(11, k_pz) - 0.2) / 0.4))
    cols = ("#E4E2F6", "#CFE0F5", "#F6C3BE", "#D3EDDC")
    with at_pop(c, x, y, sc):
        for i, (dx, dy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
            px, py = x + dx * (90 + 40 * spread), y + dy * (70 + 30 * spread)
            box(c, px, py, 170, 130, cols[i], NIGHT, 6, 14)
            c.drawCircle(px - dx * 85, py, 18, K.paint(cols[i]))
            K.text(c, "ABCD"[i], px, py, 50, "black", NIGHT)
        if T >= tb(11, k_ask):
            g = pop_scale(T - tb(11, k_ask))
            with K.at(c, x + 420, y, 0, g):
                box(c, 0, 0, 300, 110, PAPER_W, BLACK, 6, 50)
                K.text(c, "想到什么？", 0, 2, 52, "hand", NIGHT)
            c.drawPath(wb.arrow((x + 240, y - 30), (x + 270, y), 0.2, 20), wb.marker(NIGHT, 6, g))
    return None


L.note("A", "B", "C", "D")
ev(j, k_pz, puzzle11, "wood_low", 0.7)
b.hit(j, k_ask, "pop", 0.7, "每块问想到什么")


def dict11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_dict))
    if sc <= 0:
        return None
    x, y = cx - 300, cy + 280
    with K.at(c, x, y, -5, sc):
        box(c, 0, 0, 300, 220, "#F1E3CB", "#A9773E", 7, 10)
        K.text(c, "解梦词典", 0, -20, 58, "hand", "#7A4A1A")
        C.line(c, (-100, 50), (100, 50), "#A9773E", 5)
        if T >= tb(11, k_xd):
            c.drawPath(cross(0, 0, 120), wb.marker(RED, 14, clamp01((T - tb(11, k_xd)) / 0.1)))
    return None


ev(j, k_dict, dict11, "wood_high", 0.7)
b.hit(j, k_xd, "rim", 0.85, "词典打叉")


def two11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_key))
    if sc <= 0:
        return None
    x, y = cx + 280, cy + 300
    with at_pop(c, x, y, sc):
        for i, dx in enumerate((-120, 120)):
            hx, hy = x + dx, y + 140
            c.drawCircle(hx, hy, 50, K.paint(PAPER_W))
            c.drawCircle(hx, hy, 50, wb.marker(BLACK, 7))
            dream_cloud(c, hx, hy - 170, 180, 130, 1.0)
            K.text(c, "水", hx, hy - 168, 56, "hand", BLUE)
            g = pop_scale(T - tb(11, k_diff) - i * 0.12)
            if g > 0:
                with K.at(c, hx, hy - 320, 0, g):
                    if i == 0:
                        K.text(c, "口渴", 0, 0, 48, "hand", ORANGE)
                    else:
                        K.text(c, "想家", 0, 0, 48, "hand", RED)
        if T >= tb(11, k_diff):
            K.text(c, "不一样", x, y + 260, 60, "hand", NIGHT, clamp01((T - tb(11, k_diff)) / 0.2))
    return None


L.note("水", "口渴", "想家")
ev(j, k_key, two11, "pop", 0.7)
b.hit(j, k_diff, "ding", 0.8, "意思不一样")

# ================================================================ 屏 12：一百多年前的老书；研究：大脑连着白天的日程与心事
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_oldbk = kq(j, wt(20, 1, 0.3), 0)
k_lab = nx(j, wt(21, 0, 0.5), k_oldbk)
k_q12 = nx(j, wt(21, 1, 0.7), k_lab)
k_link = nx(j, wt(22, 1, 0.3), k_q12)
k_heart = nx(j, wt(22, 1, 0.8), k_link)
L.note("一百多年前", "研究", "白天", "心事")


def oldbk12(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 300, cy - 360
    with at_pop(c, x, y, sc):
        box(c, x, y, 260, 330, "#C9B79A", "#7A5A3A", 7, 10)
        box(c, x, y - 10, 200, 260, "#D8C8AA", "#7A5A3A", 4, 6)
        K.text(c, "梦的", x, y - 50, 54, "serif_black", "#5A3A1A")
        K.text(c, "解析", x, y + 20, 54, "serif_black", "#5A3A1A")
        box(c, x + 230, y - 120, 290, 80, PAPER_W, GRAY, 4, 30)
        K.text(c, "一百多年前", x + 230, y - 118, 44, "sans_medium", GRAY)
    return None


ev(j, k_oldbk, pop_fn(j, k_oldbk, oldbk12), "wood_low", 0.7)
BR12 = (cx + 40, cy + 170)


def brain(c, x, y, r=150):
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - r * 1.2, y - r * 0.85, r * 2.4, r * 1.7))
    c.drawPath(p, K.paint("#F6C3BE"))
    c.drawPath(p, wb.marker(RED, 8))
    C.line(c, (x, y - r * 0.85), (x, y + r * 0.7), RED, 5)
    for i in range(3):
        a = skia.Path()
        a.addArc(skia.Rect.MakeXYWH(x - r * 1.0 + i * 50, y - 60 + i * 30, 90, 60), 180, 180)
        c.drawPath(a, wb.marker(RED, 4))
        a2 = skia.Path()
        a2.addArc(skia.Rect.MakeXYWH(x + r * 0.15 + i * 40, y - 50 + i * 28, 90, 60), 0, 180)
        c.drawPath(a2, wb.marker(RED, 4))


def lab12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_lab))
    if sc <= 0:
        return None
    x, y = BR12
    with at_pop(c, x, y, sc):
        brain(c, x, y, 150)
        K.text(c, "研究", x, y - 200, 54, "hand", BLUE)
        if T >= tb(12, k_q12):
            g = C.slam_scale(T - tb(12, k_q12))
            with K.at(c, x + 310, y - 150, 6, g):
                box(c, 0, 0, 320, 120, PAPER_W, RED, 6, 20)
                K.text(c, "都是愿望？", 0, 2, 50, "hand", RED)
    return None


L.note("都是愿望？")
ev(j, k_lab, lab12, "wood_high", 0.7)
b.hit(j, k_q12, "rim", 0.8, "每个梦都是愿望？")


def link12(c, kk, T, cx=cx, cy=cy):
    t0 = tb(12, k_link)
    if T < t0:
        return None
    x, y = BR12
    f = ease_out(clamp01((T - t0) / 0.4))
    cal = (x - 380, y + 300)
    C.line(c, (x - 140, y + 90), (lerp(x - 140, cal[0] + 60, f), lerp(y + 90, cal[1] - 60, f)), NIGHT, 7)
    with K.at(c, *cal, 0, pop_scale(T - t0)):
        box(c, 0, 0, 220, 200, PAPER_W, BLACK, 6, 10)
        c.drawRect(skia.Rect.MakeXYWH(-110, -100, 220, 50), K.paint(RED))
        K.text(c, "白天", 0, -74, 36, "sans_medium", "#FFFFFF")
        for r_ in range(2):
            C.line(c, (-80, 0 + r_ * 50), (80 - r_ * 40, 0 + r_ * 50), GRAY, 6)
    t1 = tb(12, k_heart)
    if T >= t1:
        f2 = ease_out(clamp01((T - t1) / 0.4))
        hp = (x + 380, y + 300)
        C.line(c, (x + 140, y + 90), (lerp(x + 140, hp[0] - 50, f2), lerp(y + 90, hp[1] - 60, f2)), NIGHT, 7)
        with K.at(c, *hp, 0, pop_scale(T - t1)):
            c.drawPath(C.heart_path(0, 0, 70), K.paint("#F6C3BE"))
            c.drawPath(C.heart_path(0, 0, 70), wb.marker(RED, 7))
            K.text(c, "心事", 0, 120, 56, "hand", RED)
    return None


ev(j, k_link, link12, "wood_high", 0.7)
b.hit(j, k_heart, "ding", 0.8, "连着白天的心事")

# ================================================================ 屏 13：说回我们自己——醒来不慌、合上词典；“三步”
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_li13 = kq(j, wt(23, 1, 0.3), 0)
k_close = nx(j, wt(23, 3, 0.6), k_li13)
k_3 = nx(j, wt(23, 4, 0.6), k_close)
GY13 = cy + 420
L.note("别慌", "三步")


def li13(c, sc, T, cx=cx, cy=cy):
    x = cx - 220
    with at_pop(c, x, GY13, sc):
        C.line(c, (x - 300, GY13), (x + 300, GY13), BLACK, 7)
        draw_li(c, x, GY13, 0.9, "smile", rh=(x + 120, GY13 - 290 * 0.9 + 150))
        f = ease_in_out(clamp01((T - tb(13, k_close)) / 0.3)) if T >= tb(13, k_close) else 0.0
        bx, by = x + 170, GY13 - 290 * 0.9 + 140
        w = lerp(200, 100, f)
        box(c, bx + w / 2, by, w, 140, "#F1E3CB", "#A9773E", 6, 8)
        K.text(c, "词典", bx + w / 2, by, 40 if f > 0.5 else 44, "hand", "#7A4A1A")
        if f >= 1:
            c.drawPath(check(bx + 50, by - 140, 40), wb.marker(GREEN, 9))
        dream_cloud(c, x - 150, cy - 300, 200, 140, 1.0)
        K.text(c, "别慌", x - 150, cy - 298, 50, "hand", GREEN)
    return None


ev(j, k_li13, pop_fn(j, k_li13, li13), "wood_low", 0.7)
b.hit(j, k_close, "wood_high", 0.7, "合上词典")


def three13(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(13, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 270, cy - 160, -4, sc):
        c.drawCircle(0, 0, 190, K.paint("#E4E2F6"))
        c.drawCircle(0, 0, 190, wb.marker(NIGHT, 10))
        K.text(c, "三步", 0, 6, 130, "hand", NIGHT)
    return None


ev(j, k_3, three13, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 14：做法一——床头便签写下三个词
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_tab = 0
k_note = nx(j, wt(24, 2, 0.3), k_tab)
k_w = [nx(j, wt(24, 3, 0.2), k_note)]
k_w += [cap(j, k_w[0] + 1), cap(j, k_w[0] + 2)]
k_ok14 = cap(j, k_w[2] + 1)
WORDS14 = ["考场", "没带笔", "一身汗"]
L.note("第一", "醒来先记", "三个词")
NT14 = (cx + 120, cy - 120)


def table14(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy + 360, sc):
        K.text(c, "第一", cx - 380, cy - 500, 70, "hand", NIGHT)
        K.text(c, "醒来先记", cx - 120, cy - 500, 60, "hand", BLACK)
        c.drawRect(skia.Rect.MakeXYWH(cx - 420, cy + 240, 840, 40), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(cx - 420, cy + 240, 840, 40), wb.marker("#A9773E", 7))
        for lx in (cx - 380, cx + 380):
            C.line(c, (lx, cy + 280), (lx, cy + 460), "#A9773E", 10)
        lx, ly = cx - 330, cy + 120
        c.drawPath(P((lx - 50, ly + 120), (lx + 50, ly + 120), (lx + 20, ly), (lx - 20, ly), close=True), K.paint("#FFE39A"))
        c.drawPath(P((lx - 50, ly + 120), (lx + 50, ly + 120), (lx + 20, ly), (lx - 20, ly), close=True), wb.marker(ORANGE, 6))
        C.line(c, (lx, ly + 120), (lx, ly + 230), GRAY, 8)
        moon(c, cx + 360, cy - 380, 50)
    return None


ev(j, k_tab, pop_fn(j, k_tab, table14), "wood_low", 0.7)


def note14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_note))
    if sc <= 0:
        return None
    x, y = NT14
    with K.at(c, x, y, -3, sc):
        box(c, 0, 0, 460, 470, "#FFF1A8", ORANGE, 6, 10)
        for i, w_ in enumerate(WORDS14):
            g = clamp01((T - tb(14, k_w[i])) / 0.35)
            if g <= 0:
                continue
            n = max(1, int(math.ceil(len(w_) * g)))
            K.text(c, f"{i + 1}. {w_[:n]}", -170, -140 + i * 130, 64, "hand", BLACK, 1.0, "left")
        pen(c, 200, 200, -40, 1.0)
    if T >= tb(14, k_ok14):
        g = pop_scale(T - tb(14, k_ok14))
        with K.at(c, x + 250, y - 280, 6, g):
            box(c, 0, 0, 240, 90, PAPER_W, GREEN, 6, 40)
            K.text(c, "三个词", 0, 2, 50, "hand", GREEN)
    return None


L.note(*WORDS14, *[f"{i + 1}. {w_}" for i, w_ in enumerate(WORDS14)])
ev(j, k_note, note14, "wood_high", 0.7)
for i, k_ in enumerate(k_w):
    b.hit(j, k_, "pop", 0.65, f"写下：{WORDS14[i]}")
b.hit(j, k_ok14, "ding", 0.75, "三个词就行")

# ================================================================ 屏 15：做法二——便签连到昨天的日历：“明天要汇报”
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k_n15 = 0
k_cal15 = nx(j, wt(25, 1, 0.6), k_n15)
k_ln15 = nx(j, wt(25, 2, 0.3), k_cal15)
k_ah = nx(j, wt(25, 2, 0.9), k_ln15)
L.note("第二", "白天的影子", "昨天", "明天要汇报", "像")


def n15(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 280, cy + 40
    with at_pop(c, x, y, sc):
        K.text(c, "第二", cx - 380, cy - 500, 70, "hand", NIGHT)
        K.text(c, "白天的影子", cx - 80, cy - 500, 60, "hand", BLACK)
        with K.at(c, x, y, -4):
            box(c, 0, 0, 340, 340, "#FFF1A8", ORANGE, 6, 10)
            for i, w_ in enumerate(WORDS14):
                K.text(c, w_, 0, -100 + i * 100, 60, "hand", BLACK)
    return None


ev(j, k_n15, pop_fn(j, k_n15, n15), "wood_low", 0.7)
CAL15 = (cx + 270, cy - 40)


def cal15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_cal15))
    if sc <= 0:
        return None
    x, y = CAL15
    with K.at(c, x, y, 4, sc):
        box(c, 0, 0, 340, 380, PAPER_W, BLACK, 7, 12)
        c.drawRect(skia.Rect.MakeXYWH(-170, -190, 340, 90), K.paint(RED))
        K.text(c, "昨天", 0, -146, 58, "hand", "#FFFFFF")
        K.text(c, "明天要", 0, -10, 60, "hand", BLACK)
        K.text(c, "汇报", 0, 80, 60, "hand", RED)
    return None


ev(j, k_cal15, cal15, "wood_high", 0.7)


def ln15(c, kk, T, cx=cx, cy=cy):
    t0 = tb(15, k_ln15)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.45))
    a, z = (cx - 140, cy - 60), (CAL15[0] - 170, CAL15[1] + 40)
    p = wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), 0.25, 34)
    c.drawPath(p, wb.marker(NIGHT, 8))
    if T >= tb(15, k_ah):
        g = C.slam_scale(T - tb(15, k_ah))
        with K.at(c, cx, cy + 360, -4, g):
            box(c, 0, 0, 520, 130, "#E4E2F6", NIGHT, 7, 30)
            K.text(c, "考试 ≈ 汇报", 0, 4, 66, "hand", NIGHT)
    return None


L.note("考试 ≈ 汇报")
ev(j, k_ln15, ln15, "wood_high", 0.7)
b.hit(j, k_ah, "ding", 0.8, "原来像明天的汇报")

# ================================================================ 屏 16：做法三——三张表情卡，圈住“着急”，连到“最近：汇报”
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
k_cards = kq(j, wt(26, 1, 0.3), 1)
k_circ = nx(j, wt(26, 2, 0.2), k_cards + 2)
k_recent = nx(j, wt(26, 2, 0.7), k_circ)
FEEL = [("着急", RED, "sad"), ("委屈", BLUE, "sad"), ("开心", GREEN, "smile")]
L.note("第三", "问感受", "最近", "也是这种感觉", *[f[0] for f in FEEL])


def head16(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第三", cx - 380, cy - 500, 70, "hand", NIGHT)
        K.text(c, "问感受", cx - 140, cy - 500, 60, "hand", BLACK)
    return None


ev(j, 0, pop_fn(j, 0, head16), "wood_low", 0.6)


def cards16(c, kk, T, cx=cx, cy=cy):
    for i, (nm, col, md) in enumerate(FEEL):
        g = pop_scale(T - tb(16, k_cards) - i * 0.18)
        if g <= 0:
            continue
        x, y = cx - 330 + i * 330, cy - 170
        with K.at(c, x, y, (-4, 2, 5)[i], g):
            box(c, 0, 0, 260, 300, PAPER_W, col, 7, 16)
            c.drawCircle(0, -40, 70, K.paint(PAPER_W))
            c.drawCircle(0, -40, 70, wb.marker(col, 7))
            for dx in (-24, 24):
                c.drawCircle(dx, -55, 7, K.paint(BLACK))
            m = skia.Path()
            if md == "smile":
                m.addArc(skia.Rect.MakeXYWH(-30, -45, 60, 40), 20, 140)
            else:
                m.addArc(skia.Rect.MakeXYWH(-26, -15, 52, 30), 200, 140)
            c.drawPath(m, wb.marker(BLACK, 6))
            if i == 0:
                _sweat(c, 60, -80, 0.9)
            K.text(c, nm, 0, 95, 58, "hand", col)
    if T >= tb(16, k_circ):
        f = clamp01((T - tb(16, k_circ)) / 0.35)
        o = skia.Path()
        o.addOval(skia.Rect.MakeXYWH(cx - 330 - 170, cy - 170 - 190, 340, 380))
        c.drawPath(wb.partial(o, f)[0], wb.marker(RED, 10))
    return None


ev(j, k_cards, cards16, "pop", 0.7)
b.hit(j, k_cards + 1, "pop", 0.6, "第二张表情卡")
b.hit(j, k_circ, "rim", 0.8, "圈住着急")


def recent16(c, kk, T, cx=cx, cy=cy):
    t0 = tb(16, k_recent)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.4))
    a = (cx - 330, cy + 30)
    z = (cx - 120, cy + 260)
    c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), -0.2, 30), wb.marker(NIGHT, 8))
    with K.at(c, cx + 120, cy + 330, 0, pop_scale(T - t0 - 0.2)):
        box(c, 0, 0, 560, 200, "#E4E2F6", NIGHT, 7, 24)
        K.text(c, "最近：汇报前", 0, -40, 58, "hand", NIGHT)
        K.text(c, "也是这种感觉", 0, 40, 50, "hand", BLACK)
    return None


L.note("最近：汇报前")
ev(j, k_recent, recent16, "ding", 0.8)

# ================================================================ 屏 17：这样看梦——梦泡泡折成一张便条“最近在担心什么”
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
k_cl17 = 0
k_fold = nx(j, wt(27, 1, 0.5), k_cl17)
k_txt17 = nx(j, wt(27, 2, 0.6), k_fold)
L.note("便条", "最近在担心什么？", "给自己")


def fold17(c, kk, T, cx=cx, cy=cy):
    t0 = tb(17, k_cl17)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    m = ease_in_out(clamp01((T - tb(17, k_fold)) / 0.45)) if T >= tb(17, k_fold) else 0.0
    x, y = cx, cy - 120
    if m < 1:
        with K.at(c, x, y, 0, 1 - m * 0.7):
            c.translate(-x, -y)
            dream_cloud(c, x, y, 700, 480, sc, alpha=1 - m)
    if m > 0:
        with K.at(c, x, y, -3 * m, lerp(0.3, 1.0, m)):
            box(c, 0, 0, 640, 420, "#FFF1A8", ORANGE, 7, 10)
            c.drawRect(skia.Rect.MakeXYWH(-80, -230, 160, 50), K.paint("#F2B705", 0.7))
            K.text(c, "便条", -220, -150, 54, "hand", ORANGE)
            if T >= tb(17, k_txt17):
                g = clamp01((T - tb(17, k_txt17)) / 0.6)
                s = "最近在担心什么？"
                n = max(1, int(math.ceil(len(s) * g)))
                K.text(c, s[:n], -260, 10, 62, "hand", NIGHT, 1.0, "left")
                C.line(c, (-260, 70), (-260 + 520 * g, 70), NIGHT, 5)
    return None


ev(j, k_cl17, fold17, "pop", 0.7)
b.hit(j, k_fold, "clap", 0.8, "梦泡泡折成便条")
b.hit(j, k_txt17, "pop", 0.7, "写上：最近在担心什么")


def me17(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(17, k_txt17) - 0.8)
    if sc <= 0:
        return None
    x, y = cx + 300, cy + 470
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.75, "smile", rh=(x - 90, y - 290 * 0.75 + 80))
        K.text(c, "给自己", x - 300, y - 120, 54, "hand", GREEN)
    return None


b.custom(j, k_txt17, k_txt17 + 0.3, me17)

# ================================================================ 屏 18：评论区——“又梦见考试”；天亮了，小李伸懒腰，“有办法”
cx, cy = R[18]
j = L.scene(18, (cx, cy + 10, Z))
k_box = kq(j, wt(28, 0, 0.4), 0)
k_type = nx(j, wt(29, 0, 0.5), k_box)
k_likes = nx(j, wt(29, 2, 0.5), k_type)
k_sun = nx(j, wt(30, 1, 0.3), k_likes)
k_way = nx(j, wt(30, 2, 0.5), k_sun)
L.note("评论区", "又梦见考试了", "发送", "有办法", "+1")


def input18(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(18, k_box))
    if sc <= 0:
        return None
    x, y = cx, cy - 400
    w = 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(18, k_type):
            s = "又梦见考试了"
            g = clamp01((T - tb(18, k_type)) / 0.8)
            n = max(1, int(math.ceil(len(s) * g)))
            K.text(c, s[:n], x - w / 2 + 40, y + 2, 58, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, NIGHT)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
        n_like = sum(1 for i in range(6) if T >= tb(18, k_likes) + i * 0.15)
        for i in range(n_like):
            g = pop_scale(T - tb(18, k_likes) - i * 0.15)
            with K.at(c, x - 330 + i * 120, y + 140, 0, g):
                K.rr(c, 0, 0, 100, 60, 30, "#E4E2F6")
                K.text(c, "+1", 0, 2, 40, "hand", NIGHT)
    return None


ev(j, k_box, input18, "wood_high", 0.7)
b.hit(j, k_type, "pop", 0.6, "打字")
b.hit(j, k_likes, "clap", 0.75, "好多人加一")
GY18 = cy + 470


def morning18(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(18, k_sun))
    if sc <= 0:
        return None
    x = cx - 150
    with at_pop(c, cx, GY18, sc):
        wx, wy = cx + 260, cy - 20
        box(c, wx, wy, 300, 300, "#FFF4D6", "#A9773E", 8, 8)
        sun(c, wx, wy + 40, 50)
        C.line(c, (wx - 150, wy), (wx + 150, wy), "#A9773E", 6)
        C.line(c, (wx, wy - 150), (wx, wy + 150), "#A9773E", 6)
        hy = GY18 - 290 * 0.85
        up = 0.5 + 0.5 * math.sin((T - tb(18, k_sun)) * 4)
        draw_li(c, x, GY18, 0.85, "smile", lh=(x - 110, hy - 60 - 30 * up), rh=(x + 110, hy - 60 - 30 * up))
        C.line(c, (cx - 520, GY18), (cx + 480, GY18), BLACK, 7)
    sparkle(c, cx + 260, cy + 20, T - tb(18, k_sun), YELLOW, 10, 70, 170)
    return None


ev(j, k_sun, morning18, "wood_low", 0.75)
ev(j, k_way, L.slam_text("有办法", cx - 160, cy - 30, 120, GREEN, j, k_way, rot=-5), "kick", 0.85)
b.shots[j].shake = [(k_way, 6.0)]

# ================================================================ 收尾
L.finish(cover_shot=1, square_shot=7, notes=NOTES)
L.export(globals())
