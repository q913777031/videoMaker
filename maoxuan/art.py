"""《毛选》系列的专用元件：会议桌与投影、十格进度（十月怀胎）、捧书走路撞墙、脚印、纸地图钉、县城店铺、
脑袋装货、结论时间轴、调查纲目树、调查会圆桌、笔记本记录、纸堆。坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from scarcity.art import GROUND_Y, ground  # noqa: F401
from zizhi.art import WOOD, pit, stack, thing  # noqa: F401

RED = "#B8322A"
PAPER2 = "#EFE2C6"
DESK = "#9C6B45"


# ---------------------------------------------------------------- 会议室

def meeting(c, g, el_t, d):
    """会议室：投影幕（标题 + 柱状图，b0 起柱子长高）+ 长会议桌。"""
    K.card(c, 0, -250, 760, 400, K.PAPER, 1, r=16)
    K.rr(c, 0, -440, 800, 26, 13, K.INK2)
    K.text(c, d.get("title", "周例会 · 汇报"), 0, -380, 44, "serif_black", K.INK)
    k = ease_out(clamp01(g.since(d.get("b0", 0)) / 0.6))
    for i, v in enumerate((0.45, 0.7, 0.55, 0.95)):
        h = 200 * v * k
        K.rr(c, -210 + i * 140, -110 - h / 2, 80, max(1.0, h), 8, (K.INK2, g.acc2, K.GREEN, g.acc)[i])
    K.seg(c, -300, -110, 300, -110, K.INK2, 4)
    K.rr(c, 0, 250, 960, 70, 20, DESK)
    K.rr(c, -400, 330, 30, 120, 8, K.shade(DESK, 0.3))
    K.rr(c, 400, 330, 30, 120, 8, K.shade(DESK, 0.3))


# ---------------------------------------------------------------- 十月怀胎，一朝分娩

def months(c, g, el_t, d):
    """十格进度：前 9 格“调查”从 b0 起每 step 拍点亮一格，第 10 格“解决”在 last 拍弹出（金色）。"""
    b0, step, last = d.get("b0", 0), d.get("step", 0.25), d.get("last", 3)
    cw, gap = 82, 10
    x0 = -(10 * cw + 9 * gap) / 2 + cw / 2
    for i in range(10):
        x = x0 + i * (cw + gap)
        if i < 9:
            on = g.since(b0 + i * step) >= 0
            K.rr(c, x, 0, cw, 200, 14, g.acc if on else K.LINE)
            K.text(c, "查", x, 0, 50, "serif_black", K.PAPER if on else K.INK3)
        else:
            st = fx.word_pop(g.since(last))
            K.rr_stroke(c, x, 0, cw, 200, 14, K.INK3, 4, 1, (12, 10))
            if st:
                a, s_, _ = st
                fx.glow(c, x, 0, 160, K.GOLD, 0.5 * a)
                with K.at(c, x, 0, 0, s_):
                    K.rr(c, 0, 0, cw, 200, 14, K.GOLD, a)
                    K.text(c, "解", 0, 0, 50, "serif_black", K.PAPER, a)
    xm = x0 + 4 * (cw + gap)
    K.seg(c, x0 - cw / 2, -150, x0 + 8 * (cw + gap) + cw / 2, -150, K.INK2, 5)
    K.text(c, "十月怀胎 = 调查", xm, -210, 50, "serif_black", K.INK)
    xl = x0 + 9 * (cw + gap)
    a = clamp01(g.since(last) / 0.3)
    K.text(c, "一朝分娩", xl - 90, 190, 46, "serif_black", K.GOLD, a)


# ---------------------------------------------------------------- 捧书走路

def book_prop(c, h):
    """手持一本打开的书（遮住视线）。"""
    x, y = h
    with K.at(c, x + 20, y - 40, -8):
        K.rr(c, -38, 0, 76, 100, 6, RED)
        K.rr(c, 38, 0, 76, 100, 6, K.shade(RED, 0.2))
        K.seg(c, 0, -48, 0, 48, K.PAPER, 4)
        K.text(c, "本本", 0, 0, 30, "serif_black", K.PAPER)


def blind_walk(c, g, el_t, d):
    """捧着“本本”走路不看前方：从左走向右侧墙，在 bump 拍撞墙（星星），之后后仰。"""
    bump = d.get("bump", 2)
    wall_x = d.get("wall", 300)
    K.rr(c, wall_x + 90, -60, 180, 640, 6, "#B9A88A")
    for r in range(8):
        y = -360 + r * 80
        K.seg(c, wall_x, y, wall_x + 180, y, K.shade("#B9A88A", 0.25), 4)
        xo = wall_x + (60 if r % 2 else 120)
        K.seg(c, xo, y, xo, y + 80, K.shade("#B9A88A", 0.25), 4)
    db = g.since(bump)
    span = g.span(d.get("b0", 0), bump, ease=lambda x: x)
    x = lerp(-380, wall_x - 90, span)
    if db >= 0:
        x -= 40 * ease_out(clamp01(db / 0.25))
        pose = K.blend(K.pose("stand"), K.pose("cover"), clamp01(db / 0.2))
        mood = "surprised"
    else:
        pose = K.walk(g.t * 2.2, 1.0, "reach")
        mood = "calm"
    K.figure(c, x, 260, 330, pose, d.get("color", "#7A6A55"), mood=mood, hair="cap", prop=book_prop if db < 0 else None)
    if db >= 0:
        K.burst(c, wall_x - 10, -20, db, K.GOLD, 30, 150, 10, 8)
        for i in range(3):
            ang = g.t * 4 + i * 2.1
            K.star(c, x + math.cos(ang) * 90, -60 + math.sin(ang) * 30, 22, K.GOLD)


# ---------------------------------------------------------------- 脚印

def footprints(c, g, el_t, d):
    """一串脚印从左下走向右上，b0 起每 step 拍落下一对；终点 label 牌在最后一步亮起。"""
    n, b0, step = d.get("n", 6), d.get("b0", 0), d.get("step", 0.5)
    for i in range(n):
        dt = g.since(b0 + i * step)
        if dt < 0:
            continue
        k = ease_out(clamp01(dt / 0.15))
        t = i / max(1, n - 1)
        x, y = lerp(-360, 300, t), lerp(300, -220, t) + math.sin(t * 6) * 30
        side = -1 if i % 2 else 1
        with K.at(c, x + side * 26, y, 35, k):
            c.drawOval(skia.Rect.MakeXYWH(-20, -34, 40, 68), K.paint(K.INK2, 0.85))
            for j in range(3):
                K.dot(c, -12 + j * 12, -46, 7, K.INK2, 0.85)
    lab = d.get("label")
    if lab:
        st = fx.word_pop(g.since(b0 + (n - 1) * step))
        if st:
            a, s_, _ = st
            with K.at(c, 340, -330, 0, s_):
                K.pill(c, 0, 0, lab, 50, g.acc, K.PAPER, a)


# ---------------------------------------------------------------- 纸地图钉

def map_pin(c, g, el_t, d):
    """纸地图：省份轮廓 + 图钉在 pin 拍落下，弹出地名牌。"""
    K.card(c, 0, 0, 820, 620, PAPER2, 1, r=10, rot=-1.5)
    pts = [(-250, -200), (-40, -250), (200, -190), (260, 10), (180, 220), (-60, 250), (-260, 100)]
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    c.drawPath(p, K.paint(K.tint(g.acc, 0.8)))
    c.drawPath(p, K.paint(g.acc, 0.8, 5))
    K.text(c, d.get("region", "江西"), -40, -40, 110, "serif_black", K.tint(g.acc, 0.35))
    px, py = d.get("px", 110), d.get("py", 150)
    dt = g.since(d.get("pin", 1))
    if dt >= 0:
        k = clamp01(dt / 0.25)
        yy = lerp(py - 300, py, k * k)
        if k >= 1:
            K.ripple(c, px, py, dt - 0.25, g.acc, 120, 5)
        K.seg(c, px, yy, px, yy - 70, K.INK2, 8)
        K.dot(c, px, yy - 90, 34, g.acc)
        K.dot(c, px - 10, yy - 100, 10, K.PAPER, 0.8)
        st = fx.word_pop(dt - 0.3)
        if st:
            a, s_, _ = st
            with K.at(c, px + 10, py + 70, 0, s_):
                K.pill(c, 0, 0, d.get("place", "寻乌"), 54, K.INK, K.PAPER, a)


# ---------------------------------------------------------------- 县城店铺

def shops(c, g, el_t, d):
    """一排店铺：招牌 names 从 b0 起每 step 拍亮起，亮起时门口出现一个问号气泡。"""
    names = d["names"]
    n = len(names)
    sw = 1000 / n
    for i, name in enumerate(names):
        x = -500 + sw * (i + 0.5)
        row = i % 2
        y = -150 + row * 330
        K.rr(c, x, y, sw - 16, 240, 8, "#D9C6A5")
        K.poly(c, [(x - sw / 2 + 4, y - 120), (x + sw / 2 - 4, y - 120), (x + sw / 2 - 20, y - 160), (x - sw / 2 + 20, y - 160)],
               K.shade("#D9C6A5", 0.25))
        K.rr(c, x, y + 50, 70, 140, 6, K.shade("#D9C6A5", 0.4))
        dt = g.since(d.get("b0", 0) + i * d.get("step", 0.5))
        on = dt >= 0
        K.rr(c, x, y - 70, sw - 40, 64, 8, g.acc if on else K.PAPER)
        K.text(c, name, x, y - 70, 40, "serif_black", K.PAPER if on else K.INK2)
        if on:
            st = fx.word_pop(dt)
            if st:
                a, s_, _ = st
                with K.at(c, x + 10, y + 10, 0, s_):
                    K.icon(c, "check", 0, 0, 60, K.GREEN, a, 0.3)


# ---------------------------------------------------------------- 脑袋：出门空，回来满

def head_fill(c, g, el_t, d):
    """侧脸剪影：脑袋里先是空的（虚线 + “空”），fill 拍起 items 依次飞进去并点亮。"""
    K.card(c, 0, 0, 520, 600, K.PAPER, 1, r=260)
    c.drawCircle(-10, -40, 220, K.paint(K.SKIN))
    K.poly(c, [(200, -10), (250, 40), (205, 70)], K.SKIN)
    K.rr(c, -10, 240, 220, 120, 30, K.SKIN)
    K.dot(c, 120, -60, 14, K.INK)
    fill = d.get("fill", 1)
    items = d.get("items", ())
    if g.since(fill) < 0:
        K.ring(c, -40, -60, 130, K.INK3, 5)
        K.text(c, "空", -40, -60, 110, "serif_black", K.INK3)
        return
    for i, (name, col) in enumerate(items):
        dt = g.since(fill + i * d.get("step", 0.5))
        if dt < 0:
            continue
        k = ease_out(clamp01(dt / 0.35))
        ang = i * 2 * math.pi / max(1, len(items)) - 1.2
        tx, ty = -40 + math.cos(ang) * 95, -60 + math.sin(ang) * 85
        x, y = lerp(-520, tx, k), lerp(-420 + i * 60, ty, k)
        K.pill(c, x, y, name, 38, col, K.PAPER)
    if g.since(fill + (len(items) - 1) * d.get("step", 0.5)) >= 0.35:
        fx.glow(c, -40, -60, 220, K.GOLD, 0.3)


# ---------------------------------------------------------------- 结论在末尾

def conclusion_line(c, g, el_t, d):
    """时间轴：左端“结论”先被打叉（cross 拍），调查脚步一段段走完，右端“结论”在 end 拍亮起。"""
    K.arrow(c, (-430, 0), (430, 0), K.INK2, 10, 1, 1, 0, 36)
    dt = g.since(d.get("cross", 0))
    K.pill(c, -360, -110, "结论", 46, K.INK3, K.PAPER)
    if dt >= 0:
        k = ease_out(clamp01(dt / 0.25))
        with K.at(c, -360, -110, 0, k):
            K.icon(c, "cross", 0, 0, 110, K.RED, 1, 0.3)
    for i in range(4):
        a = clamp01(g.since(d.get("b0", 1) + i * 0.5) / 0.15)
        x = -250 + i * 150
        K.rr(c, x, 0, 110, 60, 30, g.acc, a)
        K.text(c, "调查", x, 0, 32, "serif_black", K.PAPER, a)
    st = fx.word_pop(g.since(d.get("end", 3)))
    if st:
        a, s_, _ = st
        fx.glow(c, 360, -110, 170, K.GOLD, 0.5 * a)
        with K.at(c, 360, -110, 0, s_):
            K.pill(c, 0, 0, "结论", 56, K.GOLD, K.PAPER, a)
    K.text(c, "先头", -360, 90, 40, "sans_medium", K.INK3)
    K.text(c, "末尾", 360, 90, 40, "sans_medium", K.INK2)


# ---------------------------------------------------------------- 调查纲目

def outline(c, g, el_t, d):
    """调查纲目树：大纲“商业”（b0）→ 细目 4 个（b1 起每 step 拍）→ “布匹”下 3 个更细的细目（b2 拍一起出）。"""
    b0, b1, b2, step = d.get("b0", 0), d.get("b1", 1), d.get("b2", 3), d.get("step", 0.5)
    K.card(c, 0, 0, 900, 720, K.PAPER, 1, r=24, accent=g.acc)

    def node(x, y, s, col, b, size=46):
        st = fx.word_pop(g.since(b))
        if st:
            a, k, _ = st
            with K.at(c, x, y, 0, k):
                K.pill(c, 0, 0, s, size, col, K.PAPER, a)
        return st is not None

    if node(0, -250, "商业", g.acc, b0, 58):
        K.text(c, "大纲", 200, -250, 34, "sans_medium", K.INK3)
    kids = ("布匹", "粮食", "杂货", "药材")
    for i, s in enumerate(kids):
        x = -330 + i * 220
        if g.since(b1 + i * step) >= 0:
            K.seg(c, 0, -205, x, -60, K.LINE, 5)
        node(x, -30, s, K.INK2, b1 + i * step)
    if g.since(b1) >= 0:
        K.text(c, "细目", 0, 50, 34, "sans_medium", K.INK3)
    for j, s in enumerate(("洋布", "土布", "绸缎")):
        x = -470 + j * 150
        if g.since(b2) >= 0:
            K.seg(c, -330, 0, x + 40, 150, K.LINE, 4)
        node(x + 40, 190, s, K.GOLD, b2, 36)


# ---------------------------------------------------------------- 调查会

def round_table(c, g, el_t, d):
    """调查会：圆桌 + 人从 b0 起每拍入座一位（最多 n 位），每位头顶有身份牌；count 拍弹出“至少 3 人”。"""
    roles = d.get("roles", ("老店主", "老农", "年轻人"))
    c.drawOval(skia.Rect.MakeXYWH(-330, 120, 660, 180), K.paint(DESK))
    c.drawOval(skia.Rect.MakeXYWH(-330, 110, 660, 170), K.paint(K.tint(DESK, 0.25)))
    pos = [(-300, 60), (0, 20), (300, 60), (-150, 30), (150, 30)]
    cols = (K.OTHER, K.OTHER2, K.HERO, "#9C8FB0", K.OTHER)
    for i, role in enumerate(roles):
        dt = g.since(d.get("b0", 0) + i)
        if dt < 0:
            continue
        k = ease_out(clamp01(dt / 0.3))
        x, y = pos[i]
        K.figure(c, x, y + 120 * (1 - k), 280, "stand", cols[i], alpha=k, mood="open" if i % 2 else "smile",
                 hair=("bun", "short", "long", "cap", "short")[i], face=1 if x < 0 else -1)
        K.pill(c, x, y - 410, role, 36, K.INK, K.PAPER, k)


# ---------------------------------------------------------------- 笔记本

def notebook(c, g, el_t, d):
    """笔记本：lines 从 b0 起每 step 拍写出一行（逐字显现），笔尖跟着最新一行。"""
    lines = d["lines"]
    b0, step = d.get("b0", 0), d.get("step", 1)
    K.card(c, 0, 0, 640, 720, "#FFF8E2", 1, r=16, rot=-2)
    for i in range(7):
        K.seg(c, -270, -230 + i * 90, 270, -230 + i * 90, K.tint(K.HERO, 0.7), 3)
    K.seg(c, -230, -330, -230, 330, K.tint(K.RED, 0.5), 3)
    px, py = -200, -270
    for i, s in enumerate(lines):
        k = clamp01(g.since(b0 + i * step) / 0.6)
        if k <= 0:
            continue
        n = max(1, round(len(s) * k))
        y = -270 + i * 90
        K.text(c, s[:n], -205, y, 46, "serif", K.INK, 1, "left")
        px, py = -205 + K.text_w(s[:n], 46, "serif") + 20, y
    with K.at(c, px + 40, py - 40, 35 + math.sin(g.t * 14) * 4):
        K.rr(c, 0, 0, 26, 170, 8, g.acc)
        K.poly(c, [(-13, 85), (13, 85), (0, 120)], K.INK)


# ---------------------------------------------------------------- 书面报告 vs 亲身

def report(c, g, el_t, d):
    """一份“书面报告”纸，在 cross 拍被盖上“不能单靠”的红章。"""
    K.card(c, 0, 0, 380, 480, K.PAPER, 1, r=12, rot=3)
    K.text(c, d.get("title", "书面报告"), 0, -170, 44, "serif_black", K.INK)
    for i in range(5):
        K.rr(c, 0, -80 + i * 55, 280 - (i % 2) * 60, 16, 8, K.LINE)
    dt = g.since(d.get("cross", 2))
    if dt >= 0:
        k = clamp01(1 - dt / 0.18)
        with K.at(c, 0, 40, -14, 1 + 0.6 * k):
            K.rr_stroke(c, 0, 0, 300, 110, 14, RED, 8)
            K.text(c, "不能单靠", 0, 0, 56, "serif_black", RED)


def papers(c, g, el_t, d):
    """一摞稿纸：b0→b1 拍间越堆越高，顶上一张写标题。"""
    k = g.span(d.get("b0", 0), d.get("b1", 2))
    n = 3 + round(17 * k)
    for i in range(n):
        y = 260 - i * 22
        K.rr(c, (i % 3 - 1) * 6, y, 420, 20, 4, K.PAPER if i % 2 else PAPER2)
    K.card(c, 0, 260 - n * 22 - 60, 440, 120, K.PAPER, 1, r=10, rot=-2)
    K.text(c, d.get("title", "寻乌调查"), 0, 260 - n * 22 - 60, 52, "serif_black", K.INK)


def talker(c, g, el_t, d):
    """张嘴就说：人物旁连串冒出“瞎说”气泡（b0 起每 step 拍一个），气泡越来越多。"""
    words = d.get("words", ("我觉得", "应该是", "肯定行", "听我的"))
    K.figure(c, -260, 300, 340, "point", d.get("color", K.HERO), mood="open", hair="short")
    for i, w in enumerate(words):
        st = fx.word_pop(g.since(d.get("b0", 0) + i * d.get("step", 0.5)))
        if st:
            a, s_, _ = st
            x, y = 40 + (i % 2) * 230, -250 + i * 110
            with K.at(c, x, y, (-4, 3)[i % 2], s_):
                K.bubble(c, 0, 0, w, 44, (-1, 1), a)
