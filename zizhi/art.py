"""《资治通鉴》系列的专用元件：竹简、卷轴地图、族谱树、骏马与缰绳、城墙与水位、旗帜、裂字、毛笔写字、
宝箱、钱袋、汽车、坑、裂缝、评分。在纸片剪影元件（adler.kit）与光效层（adler.fx）之上组合，坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_in, ease_in_out, ease_out, lerp
from scarcity.art import GROUND_Y, ground  # noqa: F401

CINNABAR = "#B8392B"
BAMBOO = "#D8B97A"
WOOD = "#8A5A35"
INKWASH = "#3B3A36"
WATER = "#5B8DB8"
FLAG = {"智": "#3B3A36", "韩": "#3D6E92", "赵": "#B8392B", "魏": "#5E9A6A"}


# ---------------------------------------------------------------- 竹简与书

def bamboo(c, g, el_t, d):
    """竹简：n 根竹片从中间向两侧依次展开（b0 起每 step 拍展开一半），竖排文字 text 从右往左逐列显现。"""
    text = d.get("text", "资治通鉴")
    n = max(len(text), d.get("n", 7))
    w, h = d.get("w", 70), d.get("h", 520)
    k = ease_out(clamp01(g.since(d.get("b0", 0)) / d.get("dur", 0.6)))
    for i in range(n):
        x = (i - (n - 1) / 2) * (w + 6) * k
        K.rr(c, x, 0, w, h, 10, BAMBOO, 1)
        K.seg(c, x - w / 2 + 6, -h / 2 + 40, x + w / 2 - 6, -h / 2 + 40, K.shade(BAMBOO, 0.3), 3, 0.6)
        K.seg(c, x - w / 2 + 6, h / 2 - 40, x + w / 2 - 6, h / 2 - 40, K.shade(BAMBOO, 0.3), 3, 0.6)
    if k < 1:
        return
    off = (n - len(text)) / 2
    for j, ch in enumerate(text):
        i = off + j
        a = clamp01(g.since(d.get("b0", 0) + 1 + j * d.get("step", 0.35)) / 0.2)
        x = (i - (n - 1) / 2) * (w + 6)
        K.text(c, ch, x, 0, w * 0.8, "serif_black", INKWASH, a)


# ---------------------------------------------------------------- 卷轴地图

def scroll_map(c, g, el_t, d):
    """卷轴地图：两根轴从中间向两侧展开，露出晋国版图；labels 依次在 b1 起每拍亮起。"""
    w, h = d.get("w", 820), d.get("h", 560)
    k = ease_in_out(clamp01(g.since(d.get("b0", 0)) / 0.6))
    ww = max(40.0, w * k)
    K.card(c, 0, 0, ww, h, "#EFE2C6", 1, r=8)
    if k > 0.6:
        a = clamp01((k - 0.6) / 0.4)
        p = skia.Path()
        pts = [(-260, -150), (-60, -210), (200, -170), (280, 20), (160, 190), (-120, 200), (-280, 60)]
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close()
        c.drawPath(p, K.paint(K.tint(CINNABAR, 0.75), a))
        c.drawPath(p, K.paint(CINNABAR, a, 5))
        K.text(c, d.get("title", "晋"), 0, 0, 170, "serif_black", K.shade(CINNABAR, 0.1), a * 0.9)
        for i, (lab, x, y) in enumerate(d.get("labels", [])):
            st = fx.word_pop(g.since(d.get("b1", 1) + i * d.get("step", 1)))
            if st:
                aa, s_, _ = st
                with K.at(c, x, y, 0, s_):
                    K.dot(c, 0, 0, 44, FLAG.get(lab, INKWASH), aa)
                    K.text(c, lab, 0, 0, 50, "serif_black", K.PAPER, aa)
    for sx in (-1, 1):
        K.rr(c, sx * ww / 2, 0, 34, h + 60, 14, WOOD)


# ---------------------------------------------------------------- 骏马与缰绳

def horse(c, x, y, s, t=0.0, run=0.0, color=WOOD, alpha=1.0):
    """纸片骏马：(x, y) 为蹄底中点，s 为身长；run>0 时四腿摆动。"""
    with K.paper(c, alpha, 0.9, skia.Rect.MakeXYWH(x - s, y - s * 1.2, 2 * s, 1.5 * s)):
        body_y = y - s * 0.55
        for i, lx in enumerate((-0.32, -0.18, 0.2, 0.34)):
            sw = math.sin(t * 14 + i * 1.7) * 28 * run
            with K.at(c, x + lx * s, body_y + s * 0.12, sw):
                K.rr(c, 0, s * 0.2, s * 0.07, s * 0.42, s * 0.03, K.shade(color, 0.15 if i % 2 else 0))
        c.drawOval(skia.Rect.MakeXYWH(x - s * 0.45, body_y - s * 0.17, s * 0.9, s * 0.36), K.paint(color))
        neck = [(x + s * 0.3, body_y - s * 0.05), (x + s * 0.48, body_y - s * 0.45), (x + s * 0.6, body_y - s * 0.38),
                (x + s * 0.44, body_y + s * 0.05)]
        K.poly(c, neck, color)
        with K.at(c, x + s * 0.6, body_y - s * 0.45, 25):
            c.drawOval(skia.Rect.MakeXYWH(-s * 0.1, -s * 0.07, s * 0.26, s * 0.13), K.paint(color))
        K.dot(c, x + s * 0.57, body_y - s * 0.5, s * 0.018, K.INK)
        for i in range(4):
            K.seg(c, x + s * (0.38 + i * 0.04), body_y - s * (0.2 + i * 0.07), x + s * (0.3 + i * 0.04),
                  body_y - s * (0.15 + i * 0.07), INKWASH, s * 0.035)
        tail = math.sin(t * 9) * 10 * (0.3 + run)
        with K.at(c, x - s * 0.44, body_y - s * 0.05, 30 + tail):
            K.rr(c, 0, s * 0.15, s * 0.06, s * 0.32, s * 0.03, INKWASH)


def horse_reins(c, g, el_t, d):
    """“才是马，德是缰绳”：马（标“才”）与骑手（标“德”）之间一根缰绳；snap 拍缰绳断开，马冲向右侧悬崖。"""
    snap = d.get("snap")
    ds = g.since(snap) if snap is not None else -1
    run = 1.0 if ds >= 0 else 0.25
    hx = d.get("hx", 40) + (ease_in(clamp01(ds / 1.1)) * 360 if ds >= 0 else 0)
    hy = 250 + (ease_in(clamp01((ds - 1.0) / 0.45)) * 420 if ds >= 0 else 0)
    if d.get("cliff"):
        K.poly(c, [(-540, 252), (330, 252), (330, 380), (-540, 380)], "#C9B89A")
        K.seg(c, 330, 252, 330, 380, K.shade("#C9B89A", 0.3), 6)
        K.pill(c, 430, 160, "悬崖", 36, K.RED, K.PAPER)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(-540, -470, 540, 380))
    horse(c, hx, hy, 300, g.t, run)
    K.text(c, "才", hx - 10, hy - 165, 64, "serif_black", K.PAPER)
    c.restore()
    rider = (-330, 250)
    K.figure(c, *rider, 300, "reach", K.HERO, mood="worried" if ds >= 0 else "calm", hair="bun")
    hand = (rider[0] + 70, rider[1] - 170)
    mouth = (hx + 200, hy - 290)
    if ds < 0:
        K.seg(c, *hand, *mouth, CINNABAR, 8)
        K.pill(c, (hand[0] + mouth[0]) / 2, (hand[1] + mouth[1]) / 2 - 40, "德", 40, CINNABAR, K.PAPER)
    else:
        k = clamp01(ds / 0.3)
        mid = ((hand[0] + mouth[0]) / 2, (hand[1] + mouth[1]) / 2)
        K.seg(c, *hand, lerp(mid[0], hand[0] + 40, k), mid[1] + 80 * k, CINNABAR, 8)
        K.seg(c, *mouth, lerp(mid[0], mouth[0] - 40, k), mid[1] + 80 * k, CINNABAR, 8)
        if ds < 0.4:
            K.burst(c, *mid, ds, CINNABAR, 30, 120, 10, 7)


# ---------------------------------------------------------------- 族谱树

def family_tree(c, g, el_t, d):
    """族谱树：主干 + 三层牌位；fill=(拍, 字) 在空牌位填入名字；alt=(拍, 字) 在右下牌位亮起（改姓的分支）；
    fall 拍起其他牌位变灰（灭族）。"""
    K.seg(c, 0, 380, 0, -300, WOOD, 26)
    slots = [(0, -330), (-220, -150), (220, -150), (-320, 60), (-100, 60), (120, 60), (330, 60)]
    for x, y in slots[1:]:
        K.seg(c, 0, y + 20 if y > -200 else y, x, y, WOOD, 12)
    fall = d.get("fall")
    gone = fall is not None and g.since(fall) >= 0
    names = d.get("names", ["智", "宣", "果", "", "宵", "", ""])
    fill_b, fill_ch = d.get("fill", (None, "瑶"))
    alt_b, alt_ch = d.get("alt", (None, "辅"))
    for i, (x, y) in enumerate(slots):
        ch = names[i] if i < len(names) else ""
        col = "#EFE2C6"
        if i == 3 and fill_b is not None and g.since(fill_b) >= 0:
            ch, col = fill_ch, K.GOLD
        if i == 6 and alt_b is not None and g.since(alt_b) >= 0:
            ch, col = alt_ch, K.GOLD
        a = 1.0
        if gone and i != 6:
            col, a = "#9A958C", 0.55
        if i == 3 and fill_b is not None and 0 <= g.since(fill_b) < 1:
            fx.glow(c, x, y, 140, K.GOLD, 0.4)
        if i == 6 and col == K.GOLD:
            fx.glow(c, x, y, 150, K.GOLD, 0.35 + 0.2 * g.pulse(5))
        K.card(c, x, y, 120, 150, col, a, r=12)
        if ch:
            K.text(c, ch, x, y, 70, "serif_black", INKWASH, a)
        elif i == 3:
            K.text(c, "？", x, y, 70, "serif_black", K.INK3, a)


# ---------------------------------------------------------------- 旗帜、城墙与水

def banner(c, x, y, s, ch, color, alpha=1.0, wave_t=0.0, broken=0.0):
    """旗帜：旗杆 + 飘动的方旗与单字；broken>0 时旗杆从中折断、旗面下坠。"""
    rot = 70 * ease_in(clamp01(broken))
    with K.at(c, x, y):
        K.seg(c, 0, 0, 0, -s * 0.5, INKWASH, s * 0.04, alpha)
        with K.at(c, 0, -s * 0.5, rot):
            K.seg(c, 0, 0, 0, -s * 0.5, INKWASH, s * 0.04, alpha)
            wv = math.sin(wave_t * 5 + x) * s * 0.03
            p = skia.Path()
            p.moveTo(0, -s * 0.98)
            p.quadTo(s * 0.25, -s * 0.98 + wv, s * 0.5, -s * 0.95)
            p.lineTo(s * 0.5, -s * 0.6)
            p.quadTo(s * 0.25, -s * 0.6 - wv, 0, -s * 0.62)
            p.close()
            c.drawPath(p, K.paint(color, alpha))
            K.text(c, ch, s * 0.25, -s * 0.79, s * 0.24, "serif_black", K.PAPER, alpha)


def flags(c, g, el_t, d):
    """一排旗帜：items [(字, x, y, 入场拍, 折断拍或 None, 翻转拍或 None)]；翻转时旗面镜像（调转矛头）。"""
    for ch, x, y, b, brk, flip in d["items"]:
        st = fx.word_pop(g.since(b))
        if st is None:
            continue
        a, s_, _ = st
        br = clamp01(g.since(brk) / 0.4) if brk is not None else 0.0
        tilt = (25 if x < 540 else -25) * ease_out(clamp01(g.since(flip) / 0.35)) if flip is not None else 0.0
        with K.at(c, x, y, tilt, s_):
            if flip is not None and 0 <= g.since(flip) < 0.5:
                fx.glow(c, 0, -d.get("s", 300) * 0.8, 160, K.GOLD, 0.5)
            banner(c, 0, 0, d.get("s", 300), ch, FLAG.get(ch, INKWASH), a, g.t, br)


def city(c, g, el_t, d):
    """城池：城墙（砖缝）+ 城门；水位从 b0 到 b1 拍上涨到只剩三层砖露出水面（城不浸者三版）。"""
    w, h = d.get("w", 560), d.get("h", 380)
    top = -h / 2
    K.card(c, 0, 0, w, h, "#B9A88A", 1, r=6)
    for i in range(int(w // 70) + 1):
        K.rr(c, -w / 2 + 35 + i * 70, top - 26, 44, 52, 4, "#B9A88A")
    rows = 9
    rh = h / rows
    for r in range(1, rows):
        K.seg(c, -w / 2, top + r * rh, w / 2, top + r * rh, K.shade("#B9A88A", 0.25), 3)
    K.rr(c, 0, h / 2 - 70, 110, 140, 50, K.shade("#B9A88A", 0.45))
    K.text(c, d.get("name", "晋阳"), 0, top + rh * 1.5, 56, "serif_black", INKWASH)
    k = ease_in_out(g.span(d.get("b0", 0), d.get("b1", 3), ease=lambda x: x)) if d.get("b1") else 0.0
    level = lerp(h / 2 + 30, top + rh * 3, k)
    p = skia.Path()
    p.moveTo(-w / 2 - 260, level)
    for i in range(13):
        xx = -w / 2 - 260 + (w + 520) * (i + 0.5) / 12
        p.quadTo(xx - 20, level + 14 * math.sin(g.t * 4 + i), xx + (w + 520) / 24, level)
    p.lineTo(w / 2 + 260, h / 2 + 80)
    p.lineTo(-w / 2 - 260, h / 2 + 80)
    p.close()
    c.drawPath(p, K.paint(WATER, 0.82))
    if k > 0.95:
        K.pill(c, w / 2 + 120, top + rh * 1.5, "只剩三版", 34, CINNABAR, K.PAPER)


def night(c, g, el_t, d):
    """夜色：舞台区压暗 + 月亮。"""
    K.rr(c, 0, 0, 1080, 940, 0, "#1E2333", d.get("dark", 0.55))
    K.dot(c, 300, -300, 70, "#F4E7C1")
    fx.glow(c, 300, -300, 200, "#F4E7C1", 0.3)


# ---------------------------------------------------------------- 文字特效

def crack_char(c, g, el_t, d):
    """裂字：一个大字在 split 拍从中间裂成两半并错开，裂缝闪光。"""
    ch, s = d.get("text", "仁"), d.get("s", 340)
    k = ease_out(clamp01(g.since(d.get("split", 1)) / 0.35))
    for side in (-1, 1):
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(-s if side < 0 else 0, -s, 0 if side < 0 else s, s))
        with K.at(c, side * 40 * k, side * 18 * k, side * 6 * k):
            K.text(c, ch, 0, 0, s, "serif_black", INKWASH, 1, shadow=(6, 10, 10, K.SHADOW))
        c.restore()
    if 0 < k < 1:
        K.seg(c, 0, -s * 0.6, 0, s * 0.6, K.GOLD, 10 * (1 - k))


def brush_text(c, g, el_t, d):
    """毛笔写字：text 逐字从上往下“写”出（每字 step 拍），字后带一支毛笔。竖排。"""
    text, size = d.get("text", ""), d.get("size", 110)
    b0, step = d.get("b0", 0), d.get("step", 0.5)
    n = len(text)
    y0 = -(n - 1) * size * 1.05 / 2
    tip = None
    for i, ch in enumerate(text):
        k = clamp01(g.since(b0 + i * step) / (0.3))
        if k <= 0:
            continue
        y = y0 + i * size * 1.05
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(-size, y - size * 0.6, size, y - size * 0.6 + size * 1.2 * k))
        K.text(c, ch, 0, y, size, "serif_black", INKWASH)
        c.restore()
        tip = (size * 0.55, y - size * 0.6 + size * 1.2 * k)
    if tip and g.since(b0 + (n - 1) * step) < 0.4:
        with K.at(c, tip[0], tip[1], -35):
            K.rr(c, 0, -90, 22, 180, 8, WOOD)
            K.poly(c, [(-14, 0), (14, 0), (0, 46)], INKWASH)


# ---------------------------------------------------------------- 当下：物件

def moneybag(c, x, y, s, alpha=1.0, color="#C99A3A"):
    with K.paper(c, alpha, 0.8, skia.Rect.MakeXYWH(x - s, y - s, 2 * s, 2 * s)):
        c.drawOval(skia.Rect.MakeXYWH(x - s * 0.45, y - s * 0.25, s * 0.9, s * 0.75), K.paint(color))
        K.poly(c, [(x - s * 0.2, y - s * 0.22), (x + s * 0.2, y - s * 0.22), (x + s * 0.3, y - s * 0.5), (x - s * 0.3, y - s * 0.5)],
               color)
        K.rr(c, x, y - s * 0.24, s * 0.46, s * 0.08, s * 0.04, K.shade(color, 0.35))
        K.text(c, "¥", x, y + s * 0.15, s * 0.42, "black", K.PAPER)


def car(c, x, y, s, alpha=1.0, color="#3D6E92"):
    with K.paper(c, alpha, 0.8, skia.Rect.MakeXYWH(x - s, y - s, 2 * s, 2 * s)):
        K.rr(c, x, y, s, s * 0.32, s * 0.12, color)
        K.poly(c, [(x - s * 0.3, y - s * 0.15), (x + s * 0.22, y - s * 0.15), (x + s * 0.1, y - s * 0.4), (x - s * 0.2, y - s * 0.4)],
               color)
        K.poly(c, [(x - s * 0.22, y - s * 0.17), (x + s * 0.14, y - s * 0.17), (x + s * 0.06, y - s * 0.34), (x - s * 0.16, y - s * 0.34)],
               "#DDE8F0")
        for wx in (-0.3, 0.3):
            K.dot(c, x + wx * s, y + s * 0.17, s * 0.12, K.INK)
            K.dot(c, x + wx * s, y + s * 0.17, s * 0.05, "#C9C2B6")


def thing(c, g, el_t, d):
    """单个物件元素：obj = moneybag / car / chest。chest 在 open 拍打开，露出光与 label。"""
    kind, s = d.get("obj"), d.get("s", 200)
    if kind == "moneybag":
        moneybag(c, 0, 0, s)
    elif kind == "car":
        car(c, 0, 0, s)
    elif kind == "chest":
        ko = ease_out(clamp01(g.since(d.get("open", 99)) / 0.35))
        if ko > 0:
            fx.rays(c, 0, -s * 0.2, s * 1.6, K.GOLD, g.t, 12, 0.3 * ko)
            fx.glow(c, 0, -s * 0.2, s * 1.2, K.GOLD, 0.4 * ko)
        K.card(c, 0, s * 0.12, s, s * 0.55, WOOD, 1, r=14)
        K.rr(c, 0, s * 0.12, s, s * 0.08, 4, K.GOLD)
        with K.at(c, -s / 2, -s * 0.15, -100 * ko):
            K.rr(c, s / 2, -s * 0.08, s, s * 0.28, 14, K.shade(WOOD, 0.1))
        if ko <= 0:
            K.rr(c, 0, -s * 0.05, s * 0.16, s * 0.2, 6, K.GOLD)
            K.ring(c, 0, -s * 0.18, s * 0.06, K.GOLD, 8)
        if d.get("label"):
            K.pill(c, 0, -s * 0.62 - 40 * ko, d["label"], 44, CINNABAR, K.PAPER)


def magnifier(c, g, el_t, d):
    """放大镜：镜片内略亮，随时间轻微晃动；blur_at 拍后镜片中心出现模糊人影。"""
    r = d.get("r", 120)
    dx = 30 * math.sin(g.t * 2.2)
    with K.at(c, dx, 0):
        K.dot(c, 0, 0, r, "#FFFFFF", 0.35)
        if d.get("blur_at") is not None and g.since(d["blur_at"]) >= 0:
            c.drawCircle(0, -10, r * 0.32, K.paint(K.INK2, 0.7, blur=14))
            c.drawRoundRect(skia.Rect.MakeXYWH(-r * 0.35, r * 0.15, r * 0.7, r * 0.6), 30, 30, K.paint(K.INK2, 0.7, blur=14))
        K.ring(c, 0, 0, r, INKWASH, r * 0.13)
        with K.at(c, r * 0.72, r * 0.72, 45):
            K.rr(c, 0, r * 0.4, r * 0.22, r * 0.8, r * 0.1, WOOD)


def form(c, g, el_t, d):
    """审核表：rows [(项目, 结果)] 依次打勾；skip 行在 skip_at 拍被一页纸翻过盖住并打上“跳过”章。"""
    rows, w = d["rows"], d.get("w", 600)
    rh = 110
    h = rh * len(rows) + 130
    K.card(c, 0, 0, w, h, K.PAPER, 1, r=22, accent=g.acc)
    K.text(c, d.get("title", "录用审核"), 0, -h / 2 + 60, 46, "serif_black", K.INK)
    for i, (name, res) in enumerate(rows):
        y = -h / 2 + 140 + i * rh + rh / 2 - 20
        K.text(c, name, -w / 2 + 60, y, 50, "serif", K.INK, 1, "left")
        if i == d.get("skip"):
            k = ease_out(clamp01(g.since(d.get("skip_at", 2)) / 0.3))
            if k > 0:
                K.rr(c, lerp(w / 2, 0, k), y, w * k - 20, rh - 16, 10, "#E8DFD0")
                if k >= 1:
                    with K.at(c, 120, y, -12):
                        K.rr_stroke(c, 0, 0, 150, 70, 10, CINNABAR, 6)
                        K.text(c, "跳过", 0, 0, 40, "serif_black", CINNABAR)
            continue
        st = fx.word_pop(g.since(d.get("b0", 0) + i))
        if st:
            a, s_, _ = st
            with K.at(c, w / 2 - 90, y, 0, s_):
                if res:
                    K.text(c, res, 0, 0, 44, "serif_black", K.GREEN, a)
                else:
                    K.icon(c, "check", 0, 0, 72, K.GREEN, a, 0.4)


def rating(c, g, el_t, d):
    """评分：rows [(对象, 星数)] 第 i 行在 b0+i 拍出现，星星逐颗点亮。"""
    rows = d["rows"]
    for i, (name, n) in enumerate(rows):
        dt = g.since(d.get("b0", 0) + i)
        if dt < 0:
            continue
        y = (i - (len(rows) - 1) / 2) * 150
        K.card(c, 0, y, 720, 120, K.PAPER, clamp01(dt / 0.15), r=24)
        K.text(c, name, -300, y, 46, "serif_black", K.INK, 1, "left")
        for j in range(5):
            on = j < n and dt > 0.08 * j
            K.star(c, 40 + j * 66, y, 28, K.GOLD if on else K.LINE)


def pit(c, g, el_t, d):
    """一个坑（标签 label），古人与今人在 fall 拍先后掉进去。"""
    K.poly(c, [(-460, 0), (-160, 0), (-120, 60), (120, 60), (160, 0), (460, 0), (460, 40), (-460, 40)], K.LINE)
    c.drawOval(skia.Rect.MakeXYWH(-170, -30, 340, 120), K.paint("#2E2A24"))
    K.pill(c, 0, 150, d.get("label", "才胜德"), 44, CINNABAR, K.PAPER)
    for i, (x, hair, col) in enumerate(((-300, "bun", WOOD), (300, "short", K.HERO))):
        dt = g.since(d.get("fall", 1) + i)
        k = ease_in(clamp01(dt / 0.45))
        fx_ = lerp(x, -60 + 120 * i, k)
        fy = lerp(0, 90, k)
        a = 1 - 0.55 * clamp01((dt - 0.45) / 0.3)
        if a > 0:
            K.figure(c, fx_, fy, 260, "stand" if dt < 0 else "cheer", col, alpha=a, mood="surprised" if dt >= 0 else "calm",
                     hair=hair, face=1 if x < 0 else -1)


def crack_floor(c, g, el_t, d):
    """婚房：屋顶轮廓、房车图标；两人背对背；地面在 b 拍从中间裂开。"""
    K.poly(c, [(-420, -330), (0, -560), (420, -330)], K.tint(CINNABAR, 0.6))
    K.rr_stroke(c, 0, -60, 840, 540, 10, K.tint(CINNABAR, 0.6), 8)
    K.icon(c, "heart", 0, -400, 80, CINNABAR, 1, 0.5)
    k = ease_out(clamp01(g.since(d.get("b", 1)) / 0.4))
    K.seg(c, -420, 210, -12 * k, 210, K.LINE, 10)
    K.seg(c, 12 * k, 210, 420, 210, K.LINE, 10)
    if k > 0:
        p = skia.Path()
        p.moveTo(0, 210)
        for i in range(1, 6):
            p.lineTo((-1) ** i * 18 * k, 210 + i * 26 * k)
        c.drawPath(p, K.paint(INKWASH, 1, 6))
    K.figure(c, -130 - 30 * k, 210, 300, "stand", K.HERO, mood="sad", hair="short", face=-1)
    K.figure(c, 130 + 30 * k, 210, 290, "stand", "#C97B84", mood="sad", hair="long", face=1)


def stack(c, g, el_t, d):
    """排序：items 先按原序排列；top 拍时 items[-1]（人品）砸到最上面，其余整体下移。"""
    items = d["items"]
    k = ease_out(clamp01(g.since(d.get("top", 1)) / 0.35))
    n = len(items)
    for i, (name, col) in enumerate(items):
        if i == n - 1:
            y = lerp(-360 - 200, -330, k) if k > 0 else None
            if y is None:
                continue
            fx.glow(c, 0, y, 260, K.GOLD, 0.4 * k)
            K.card(c, 0, y, 520, 130, col, k, r=30)
            K.text(c, name, 0, y, 70, "serif_black", K.PAPER, k)
        else:
            y = -200 + i * 140 + 150 * k
            K.card(c, 0, y, 440, 110, col, 1, r=26)
            K.text(c, name, 0, y, 54, "serif_black", K.PAPER)


def sweat(c, g, el_t, d):
    """冷汗：两滴水珠从额头滑下。"""
    for i in range(2):
        dt = (g.t * 0.9 + i * 0.5) % 1.0
        K.icon(c, "water", 20 * i, 60 * dt, 40, WATER, 1 - dt, 0.2)
