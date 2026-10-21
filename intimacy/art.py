"""《亲密关系》系列的专用元件：宿舍楼、爱情三角、四格回应、情侣。其余复用 sapiens.art 与 scarcity.art。
坐标以元素中心为原点。"""

import math

from adler import fx
from adler import kit as K
from scarcity.art import bill, calendar, checklist, clock_digital, cycle, phone_chat  # noqa: F401
from sapiens.art import GROUND_Y, crowd, ground, two_lines  # noqa: F401

HER = "#C97B84"


def building(c, g, el_t, d):
    """宿舍楼：rows×cols 扇窗，friends [(行, 列)] 的窗户依次亮起并以弧线相连（邻居成了朋友）。"""
    rows, cols = d.get("rows", 3), d.get("cols", 5)
    cw, ch = 130, 120
    w, h = cols * cw + 60, rows * ch + 80
    K.card(c, 0, 0, w, h, "#D9CDB8", 1, r=16)
    K.poly(c, [(-w / 2 - 30, -h / 2), (w / 2 + 30, -h / 2), (0, -h / 2 - 110)], K.shade("#D9CDB8", 0.2))
    x0, y0 = -cols * cw / 2 + cw / 2, -rows * ch / 2 + ch / 2 + 10
    lit = {}
    for i, (r, col) in enumerate(d.get("friends", [])):
        lit[(r, col)] = g.since(d.get("b0", 0) + i * d.get("step", 1))
    for r in range(rows):
        for col in range(cols):
            x, y = x0 + col * cw, y0 + r * ch
            t = lit.get((r, col), -1)
            on = t >= 0
            if on:
                fx.glow(c, x, y, 90, K.GOLD, 0.35)
            K.rr(c, x, y, 76, 80, 8, K.GOLD if on else "#8E9AA8")
    pts = [(x0 + col * cw, y0 + r * ch) for r, col in d.get("friends", [])]
    for i in range(1, len(pts)):
        k = fx.clamp01(g.since(d.get("b0", 0) + i * d.get("step", 1)) / 0.4)
        if k > 0:
            K.arrow(c, pts[i - 1], pts[i], K.RED, 6, 1, k, -0.4, 0)


def triangle(c, g, el_t, d):
    """斯滕伯格爱情三角：三个顶点（亲密、激情、承诺）依次弹出，边依次画出；dim 中的顶点变暗。"""
    R = d.get("R", 300)
    names = d.get("names", ["亲密", "激情", "承诺"])
    pts = [(R * math.cos(-math.pi / 2 + i * math.tau / 3), R * math.sin(-math.pi / 2 + i * math.tau / 3) + R * 0.15)
           for i in range(3)]
    b0, step = d.get("b0", 0), d.get("step", 2)
    for i in range(3):
        k = fx.clamp01(g.since(b0 + i * step + 1) / 0.5)
        if k > 0:
            K.seg(c, *pts[i], *pts[(i + 1) % 3], g.acc, 10, 1, k)
    dim = d.get("dim", ())
    for i, (x, y) in enumerate(pts):
        st = fx.word_pop(g.since(b0 + i * step))
        if st is None:
            continue
        a, s_, _ = st
        fade = 0.35 if i in dim and g.since(d.get("dim_at", 99)) >= 0 else 1.0
        with K.at(c, x, y, 0, s_):
            fx.draw_word(c, names[i], 0, 0, 60, "serif_black", K.INK, g.acc if i != 1 else K.RED, K.PAPER, a * fade, True)


def grid4(c, g, el_t, d):
    """2×2 四格：cells [(标题, 例句, 颜色)] 依次弹出，hi 格随拍发光。"""
    cells = d["cells"]
    w, h = d.get("w", 430), d.get("h", 250)
    b0, step = d.get("b0", 0), d.get("step", 2)
    for i, (title, ex, col) in enumerate(cells):
        st = fx.word_pop(g.since(b0 + i * step))
        if st is None:
            continue
        a, s_, _ = st
        x = (i % 2 - 0.5) * (w + 30)
        y = (i // 2 - 0.5) * (h + 30)
        if i == d.get("hi", -1):
            fx.glow(c, x, y, w * 0.8, K.GOLD, 0.3 + 0.2 * g.pulse(5))
        K.card(c, x, y, w, h, col, a, r=24, scale=s_)
        K.text(c, title, x, y - 50, 48, "serif_black", K.PAPER, a)
        K.text(c, ex, x, y + 40, 38, "sans_medium", K.PAPER, a)
