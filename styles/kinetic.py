"""动态排版：没有人物与图标，文字本身就是画面——巨型黑体字在实测拍点上砸落、翻转、加粗冲出、滚动、被斜切、像弹簧一样伸缩。

    python3 -m styles.kinetic --stills
    python3 -m styles.kinetic            # → out/styles/kinetic.mp4
"""

import math

import skia

from adler import fx
from engine import gfx
from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, ease_out_back, lerp
from styles import seg

W, H = seg.W, seg.H
BG = "#0B0B0E"
WHITE = "#F4F1EA"
LIME = "#C6FF3D"
PINK = "#FF3D7F"
F = "black"


def txt(c, s, x, y, size, color=WHITE, alpha=1.0, align="center", font=F):
    return gfx.draw_text(c, s, x, y, size, font, color, alpha, align)


def tw(s, size):
    return gfx.text_width(s, size, F)


def flip_x(c, cx, cy, ang):
    """绕水平轴翻转（透视）：ang 弧度。"""
    c.translate(cx, cy)
    m = skia.Matrix.MakeAll(1, 0, 0, 0, math.cos(ang), 0, 0, math.sin(ang) * 0.0012, 1)
    c.concat(m)
    c.translate(-cx, -cy)


def thud(c, dt, y, color=WHITE):
    """砸地时的速度线与灰尘。"""
    if 0 <= dt < 0.4:
        a = 1 - dt / 0.4
        for i in range(14):
            x = 60 + i * 72
            L = 80 + 40 * math.sin(i * 2.3)
            gfx.rrect(c, x, y + 30 + dt * 400 + L / 2, 8, L * a, 4, color, 0.6 * a)


def bar0(c, t, b):
    d0 = seg.since(b, 0, t)
    k = ease_in(clamp01((d0 + 0.22) / 0.22))
    y = lerp(-400, 1000, k)
    sq = 1.0
    if d0 >= 0:
        sq = 1 - 0.25 * math.exp(-d0 * 10) * math.cos(d0 * 30)
    c.save()
    c.translate(W / 2, y + 150)
    c.scale(1 / sq, sq)
    txt(c, "新领导", 0, -150, 300, WHITE)
    c.restore()
    thud(c, d0, 1150)
    d1 = seg.since(b, 1, t)
    if d1 >= 0:
        x = lerp(-600, W / 2, ease_out(clamp01(d1 / 0.25)))
        txt(c, "新部门", x, 620, 130, LIME)
    d2 = seg.since(b, 2, t)
    if d2 >= 0:
        st = fx.word_pop(d2)
        c.save()
        c.translate(820, 1330)
        c.rotate(-8)
        c.scale(st[1], st[1])
        gfx.rrect(c, 0, 0, 260, 130, 16, PINK)
        txt(c, "来了", 0, 0, 90, BG)
        c.restore()


SUR_OLD = "李陈梅刘"
SUR_NEW = "周吴郑王"


def bar1(c, t, b):
    d0 = seg.since(b, 0, t)
    s = 0.6 + 0.4 * ease_out_back(clamp01((d0 + 0.05) / 0.3), 2)
    c.save()
    c.translate(W / 2, 560)
    c.scale(s, s)
    txt(c, "团队", 0, 0, 280, WHITE)
    c.restore()
    for i, ch in enumerate(SUR_OLD):
        x = 165 + i * 250
        y = 1040
        flip = i in (1, 2)
        ang = 0.0
        if flip:
            dt = seg.since(b, 1 if i == 1 else 2, t)
            ang = math.pi * ease_in_out(clamp01(dt / 0.3)) if dt >= 0 else 0.0
        c.save()
        flip_x(c, x, y, ang)
        front = ang < math.pi / 2
        gfx.rrect(c, x, y, 220, 260, 20, "#1E1E26" if front else LIME)
        if front:
            txt(c, ch, x, y, 190, WHITE)
        else:
            c.translate(x, y)
            c.scale(1, -1)
            txt(c, SUR_NEW[i], 0, 0, 190, BG)
        c.restore()
    d3 = seg.since(b, 3, t)
    if d3 >= 0:
        st = fx.word_pop(d3)
        c.save()
        c.translate(W / 2, 1420)
        c.rotate(-4)
        c.scale(st[1], st[1])
        txt(c, "换了一半", 0, 0, 170, PINK)
        c.restore()


def bar2(c, t, b):
    sizes = [150, 230, 330, 520]
    k = 0
    for j in range(4):
        if seg.since(b, j, t) >= 0:
            k = j
    dt = seg.since(b, k, t)
    prev = sizes[k - 1] if k else 90
    size = lerp(prev, sizes[k], ease_out_back(clamp01(dt / 0.25), 2.5))
    if k == 3:
        size += dt * 900
    for e in range(4, 0, -1):
        txt(c, "干劲十足", W / 2, 900 + e * 24, size * (1 - e * 0.04), LIME if e % 2 else PINK, 0.12 * (5 - e))
    txt(c, "干劲十足", W / 2, 900, size, WHITE, stroke=None) if False else txt(c, "干劲十足", W / 2, 900, size, WHITE)
    if k == 3:
        fx.sparks(c, W / 2, 900, dt, [LIME, PINK, WHITE], n=22, reach=520)
    txt(c, "大家", W / 2, 420, 120, LIME, clamp01(seg.since(b, 0, t) / 0.1))


def bar3(c, t, b):
    d0 = seg.since(b, 0, t)
    land = seg.since(b, 2, t)
    if land < 0:
        v = (t * 18) % 10
    else:
        v = 3
    cx, cy = 330, 900
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(cx - 220, cy - 300, 440, 600))
    if land < 0:
        off = (v % 1) * 520
        n = int(v)
        txt(c, str(n), cx, cy - off, 560, LIME)
        txt(c, str((n + 1) % 10), cx, cy + 520 - off, 560, LIME)
    else:
        bounce = 40 * math.exp(-land * 8) * math.cos(land * 25)
        txt(c, "3", cx, cy + bounce, 560, LIME)
    c.restore()
    a = clamp01((d0 + 0.05) / 0.2)
    txt(c, "个", 760, 760, 200, WHITE, a)
    txt(c, "月后", 760, 1030, 200, WHITE, a)
    d3 = seg.since(b, 3, t)
    if d3 >= 0:
        txt(c, "……又回到老样子", W / 2, 1400, 72, "#8A8F98", clamp01(d3 / 0.25), font="bold")


def bar4(c, t, b):
    d0 = seg.since(b, 0, t)
    d1 = seg.since(b, 1, t)
    s0 = 1 + 1.5 * (1 - ease_out(clamp01((d0 + 0.02) / 0.18)))
    top = "不是人的问题"
    size = min(170, 960 / len(top) * 1.0)
    if d1 >= 0:
        # 被斜切后露出“是结构”
        k = ease_out(clamp01(d1 / 0.3))
        st = 0.7 + 0.3 * ease_out_back(clamp01(d1 / 0.3), 2.5)
        c.save()
        c.translate(W / 2, 1000)
        c.scale(st, st)
        gfx.rrect(c, 0, 0, 900, 400, 30, LIME)
        txt(c, "是结构", 0, 0, 260, BG)
        c.restore()
        fx.sparks(c, W / 2, 1000, seg.since(b, 2, t), [LIME, PINK, WHITE], n=24, reach=560)
        for side in (-1, 1):
            c.save()
            p = skia.Path()
            if side < 0:
                p.moveTo(-200, -200)
                p.lineTo(W + 200, -200)
                p.lineTo(W + 200, 640)
                p.lineTo(-200, 960)
            else:
                p.moveTo(-200, 960)
                p.lineTo(W + 200, 640)
                p.lineTo(W + 200, H + 200)
                p.lineTo(-200, H + 200)
            p.close()
            c.clipPath(p, doAntiAlias=True)
            c.translate(side * 180 * k, side * 260 * k)
            c.rotate(side * 6 * k)
            txt(c, top, W / 2, 800, size, WHITE, 1 - 0.85 * k)
            c.restore()
        a = 1 - clamp01(d1 / 0.15)
        gfx.rrect(c, W / 2, 800, 1400, 10, 5, PINK, a) if a > 0 else None
    else:
        c.save()
        c.translate(W / 2, 800)
        c.scale(s0, s0)
        txt(c, top, 0, 0, size, WHITE)
        c.restore()
    txt(c, "书中观点", W / 2, 420, 54, "#8A8F98", 1, font="bold")
    for k_ in (0, 1):
        fx.flash(c, fx.flash_alpha(seg.since(b, k_, t), 0.6))


def bar5(c, t, b):
    d0 = seg.since(b, 0, t)
    txt(c, "书一开头", W / 2, 470, 110, "#8A8F98", clamp01((d0 + 0.05) / 0.15))
    s = 0.4 + 0.6 * ease_out_back(clamp01((d0 + 0.05) / 0.3), 2.5)
    c.save()
    c.translate(W / 2, 960)
    c.scale(s, s)
    txt(c, "弹簧", 0, 0, 400, WHITE)
    c.restore()
    d2 = seg.since(b, 2, t)
    if d2 >= 0:
        st = fx.word_pop(d2)
        c.save()
        c.translate(250, 700)
        c.rotate(-12)
        c.scale(st[1], st[1])
        gfx.rrect(c, 0, 0, 280, 130, 16, LIME)
        txt(c, "拿出", 0, 0, 96, BG)
        c.restore()


def bar6(c, t, b):
    d1 = seg.since(b, 1, t)
    sy = 1.0
    if d1 >= 0:
        sy = 1 + 0.55 * math.sin(d1 * 7.2) * math.exp(-d1 * 1.0)
    txt(c, "手一松", W / 2, 430, 120, LIME, clamp01((seg.since(b, 0, t) + 0.05) / 0.15))
    for i, ch in enumerate("弹簧"):
        c.save()
        c.translate(W / 2 + (i - 0.5) * 420, 1180)
        c.scale(1 / math.sqrt(sy), sy)
        txt(c, ch, 0, -200, 400, WHITE)
        c.restore()
    d2 = seg.since(b, 2, t)
    if d2 >= 0:
        txt(c, "它自己弹", W / 2, 1520, 130, PINK, clamp01(d2 / 0.1))
    thud(c, d1, 1230, LIME)


WORDS = [("行为", WHITE), ("藏在", WHITE), ("结构", LIME), ("里", WHITE)]


def bar7(c, t, b):
    for j, (w, col) in enumerate(WORDS):
        dt = seg.since(b, j, t)
        if dt < 0:
            continue
        st = fx.word_pop(dt)
        y = 520 + j * 300
        x = W / 2 + (-140 if j % 2 == 0 else 140)
        c.save()
        c.translate(x, y)
        c.rotate(st[2] * (1 if j % 2 else -1))
        c.scale(st[1], st[1])
        if col == LIME:
            gfx.rrect(c, 0, 0, tw(w, 260) + 60, 300, 20, LIME)
            txt(c, w, 0, 0, 260, BG)
        else:
            txt(c, w, 0, 0, 240, col, st[0])
        c.restore()
        if col == LIME:
            fx.sparks(c, x, y, dt, [LIME, PINK, WHITE], n=20, reach=420)


BARS = [bar0, bar1, bar2, bar3, bar4, bar5, bar6, bar7]


def draw(c, t):
    c.clear(gfx.col(BG))
    b, lt = seg.bar_at(t)
    dx = dy = 0.0
    for k, *_ in b["hits"]:
        if _[0] in ("kick", "tom", "rim"):
            ox, oy = fx.shake_offset(seg.since(b, k, t), 18, 0.3, seed=k)
            dx += ox
            dy += oy
    z = 1 + 0.06 * math.exp(-lt * 9) if b["i"] else 1.0
    c.save()
    c.translate(W / 2 + dx, H / 2 + dy)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    BARS[b["i"]](c, t, b)
    c.restore()
    # 进度条：每小节一格
    for i in range(8):
        on = i <= b["i"]
        gfx.rrect(c, 120 + i * 120, 120, 100, 10, 5, LIME if on else "#2A2A33")
    txt(c, "系统之美 · 01", 60, 190, 34, "#8A8F98", 1, "left", "bold")


if __name__ == "__main__":
    seg.main("kinetic", draw)
