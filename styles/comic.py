"""漫画分格：每屏一页彩色漫画（粗黑边框、斜切分格、出血格、网点阴影），相机按小节逐格推进（推入当前格、其他格变暗），
对话气泡、拟声大字、速度线、跨格动作；小节 0–3 一页四格，小节 4 整页大格砸出观点，小节 5–7 一页三格；换页在小节边界快速平移。

用法：python3 -m styles.comic [--stills]   → out/styles/comic.mp4
"""

import math

import numpy as np
import skia

from adler import fx
from adler import kit as K
from engine import gfx
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from maoxuan import ink
from styles import seg
from themes import anime

anime.install()                      # 大眼赛璐珞人物（描边平涂）
figure = ink.ink_figure

INKC = "#141218"
PAGES = {
    "A": {0: [(36, 60), (1044, 60), (1044, 560), (36, 640)],
          1: [(36, 672), (560, 652), (520, 1232), (36, 1232)],
          2: [(592, 650), (1044, 632), (1044, 1232), (552, 1232)],
          3: [(36, 1264), (1044, 1264), (1044, 1880), (36, 1880)]},
    "B": {4: [(0, 0), (1080, 0), (1080, 1920), (0, 1920)]},
    "C": {5: [(36, 60), (1044, 60), (1044, 600), (36, 690)],
          6: [(36, 722), (1044, 632), (1044, 1240), (36, 1240)],
          7: [(36, 1272), (1044, 1272), (1044, 1880), (36, 1880)]},
}
PAGE_OF = {i: p for p, panels in PAGES.items() for i in panels}
BG = {0: ("#FFE9B8", "#F6B26B"), 1: ("#DCEBFA", "#9CC0E6"), 2: ("#FFF1C9", "#FFC94D"), 3: ("#E6E1F2", "#A89BC9"),
      4: ("#FFDDD2", "#E8574A"), 5: ("#E3F2E6", "#93C9A2"), 6: ("#DDEFFA", "#7FB6DE"), 7: ("#FFF0D6", "#F2A65A")}


def tb(i, k):
    return -seg.since(seg.BARS[i], k, 0.0)


def poly_path(pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p


def bounds(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


_BG_CACHE = {}


def panel_bg(i) -> skia.Image:
    """格子底：对角渐变 + 网点（越靠右下越大），预先算好缓存。"""
    if i in _BG_CACHE:
        return _BG_CACHE[i]
    W, H = seg.W, seg.H
    c0, c1 = (np.array(gfx.rgb(x), np.float32) for x in BG[i])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip((xx / W * 0.4 + yy / H * 0.6), 0, 1)[..., None]
    img = c0 * (1 - t) + c1 * t
    r = (np.clip(t[..., 0] - 0.35, 0, 1) * 9)
    dots = ((np.mod(xx, 18) - 9) ** 2 + (np.mod(yy, 18) - 9) ** 2) < r ** 2
    img[dots] = img[dots] * 0.82
    rgba = np.dstack([img.astype(np.uint8), np.full((H, W), 255, np.uint8)])
    _BG_CACHE[i] = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    return _BG_CACHE[i]


# ---------------------------------------------------------------- 漫画元件

def speed_lines(c, cx, cy, k, inner=260, n=60, seed=1, color=INKC):
    if k <= 0:
        return
    rng = np.random.default_rng(seed)
    p = skia.Path()
    for j in range(n):
        a = j / n * 2 * math.pi + rng.random() * 0.06
        r0 = inner + rng.random() * 120
        w = 0.01 + rng.random() * 0.012
        p.moveTo(cx + math.cos(a) * r0, cy + math.sin(a) * r0)
        p.lineTo(cx + math.cos(a - w) * 1500, cy + math.sin(a - w) * 1500)
        p.lineTo(cx + math.cos(a + w) * 1500, cy + math.sin(a + w) * 1500)
        p.close()
    c.drawPath(p, K.paint(color, 0.8 * k))


def sfx(c, text, x, y, size, dt, rot=-10, fill="#FFE14D", stroke=INKC):
    """拟声大字：在 dt=0 时砸出（过冲回弹），粗黑描边 + 白色外描边。"""
    st = fx.word_pop(dt, 0.28)
    if not st:
        return
    a, s_, _ = st
    with K.at(c, x, y, rot, s_):
        gfx.draw_text(c, text, 0, 0, size, "black", fill, a, stroke=("#FFFFFF", size * 0.34))
        gfx.draw_text(c, text, 0, 0, size, "black", fill, a, stroke=(stroke, size * 0.16))
        gfx.draw_text(c, text, 0, 0, size, "black", fill, a)


def balloon(c, text, x, y, size, dt, tail=(-60, 90), w=None):
    st = fx.word_pop(dt, 0.25)
    if not st:
        return
    a, s_, _ = st
    tw = (w or K.text_w(text, size, "black")) + size * 1.4
    th = size * 2.1
    with K.at(c, x, y, 0, s_):
        p = skia.Path()
        p.addOval(skia.Rect.MakeXYWH(-tw / 2, -th / 2, tw, th))
        q = skia.Path()
        q.moveTo(-size * 0.5, th * 0.35)
        q.lineTo(tail[0], tail[1])
        q.lineTo(size * 0.5, th * 0.38)
        q.close()
        p.addPath(q)
        c.drawPath(p, K.paint("#FFFFFF", a))
        c.drawPath(p, K.paint(INKC, a, 6))
        c.drawOval(skia.Rect.MakeXYWH(-tw / 2 + 4, -th / 2 + 4, tw - 8, th - 8), K.paint("#FFFFFF", a))
        gfx.draw_text(c, text, 0, 0, size, "black", INKC, a)


def caption_box(c, text, x, y, size=40, a=1.0):
    w = K.text_w(text, size, "black") + 44
    K.rr(c, x + w / 2, y, w, size * 1.6, 4, "#FFF6B0", a)
    K.rr_stroke(c, x + w / 2, y, w, size * 1.6, 4, INKC, 5, a)
    gfx.draw_text(c, text, x + w / 2, y, size, "black", INKC, a)


def poof(c, x, y, dt, r=110):
    if not 0 <= dt < 0.5:
        return
    k = dt / 0.5
    for j in range(7):
        a = j / 7 * 2 * math.pi
        rr = r * (0.4 + 0.6 * ease_out(k))
        c.drawCircle(x + math.cos(a) * rr * 0.7, y + math.sin(a) * rr * 0.5, rr * 0.45,
                     K.paint("#FFFFFF", 1 - k))
        c.drawCircle(x + math.cos(a) * rr * 0.7, y + math.sin(a) * rr * 0.5, rr * 0.45, K.paint(INKC, 1 - k, 4))


def clock(c, x, y, r, spin):
    c.drawCircle(x, y, r, K.paint("#FFFFFF"))
    c.drawCircle(x, y, r, K.paint(INKC, 1, 10))
    for j in range(12):
        a = j / 12 * 2 * math.pi
        K.seg(c, x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8, x + math.cos(a) * r * 0.92,
              y + math.sin(a) * r * 0.92, INKC, 7)
    a1 = -math.pi / 2 + spin * 2 * math.pi
    a2 = -math.pi / 2 + spin * 2 * math.pi / 12
    K.seg(c, x, y, x + math.cos(a1) * r * 0.75, y + math.sin(a1) * r * 0.75, INKC, 10)
    K.seg(c, x, y, x + math.cos(a2) * r * 0.5, y + math.sin(a2) * r * 0.5, "#E04A3A", 14)
    K.dot(c, x, y, 14, INKC)


def slinky(c, x, top, length, w=170, n=22):
    for j in range(n):
        y = top + length * j / (n - 1)
        rect = skia.Rect.MakeXYWH(x - w / 2, y - 16, w, 32)
        c.drawOval(rect, K.paint(INKC, 1, 13))
        c.drawOval(rect, K.paint("#9FB4C8" if j % 2 else "#C9D7E4", 1, 7))


def book(c, x, y, s=1.0):
    with K.at(c, x, y, -6, s):
        for side in (-1, 1):
            p = skia.Path()
            p.moveTo(0, -120)
            p.quadTo(side * 120, -150, side * 230, -120)
            p.lineTo(side * 230, 120)
            p.quadTo(side * 120, 90, 0, 120)
            p.close()
            c.drawPath(p, K.paint("#FFFDF4"))
            c.drawPath(p, K.paint(INKC, 1, 7))
            for j in range(4):
                K.seg(c, side * 40, -70 + j * 45, side * 190, -80 + j * 45, "#9A948A", 5)
        K.text(c, "系统之美", 0, -175, 46, "black", "#2E8A57")


# ---------------------------------------------------------------- 各格内容（页面坐标）

def p0(c, lt, t):
    b = seg.BARS[0]
    dx = 600 * (1 - ease_out(clamp01(-seg.since(b, 0, -t) / 0.35 if False else seg.since(b, 0, t) / 0.35)))
    speed_lines(c, 700, 360, clamp01(1 - seg.since(b, 0, t) / 0.6) if seg.since(b, 0, t) >= 0 else 0, 200, seed=3)
    figure(c, 740 + dx, 600, 420, "point", None, alpha=1, face=-1, mood="happy", role="boss")
    figure(c, 230, 610, 330, "stand", None, face=1, mood="surprised" if seg.since(b, 1, t) >= 0 else "calm", role="worker")
    balloon(c, "咱们重新出发！", 470, 190, 50, seg.since(b, 1, t), tail=(150, 110))
    sfx(c, "登场！", 900, 140, 90, seg.since(b, 2, t), rot=12)
    caption_box(c, "新部门来了新领导", 52, 96, 36)


def p1(c, lt, t):
    b = seg.BARS[1]
    for n, x in enumerate((150, 290, 420)):
        K.rr(c, x, 1050, 120, 18, 4, "#8A5A35")
        swapped = seg.since(b, n * 0.7 + 0.6, t) >= 0
        figure(c, x, 1150, 250, "sit", None if not swapped else ("#E8574A", "#2E8A57", "#7A5AC9")[n],
               mood="smile", role="worker" if not swapped else ("worker_f" if n == 1 else "worker"))
        poof(c, x, 1000, seg.since(b, n * 0.7 + 0.6, t))
    sfx(c, "换！", 300, 800, 110, seg.since(b, 1, t), rot=-14)
    caption_box(c, "团队也换了一半", 52, 706, 32)


def p2(c, lt, t):
    b = seg.BARS[2]
    for n, x in enumerate((690, 820, 950)):
        if seg.since(b, n, t) >= 0:
            hop = 40 * math.sin(clamp01(seg.since(b, n, t) / 0.3) * math.pi)
            figure(c, x, 1160 - hop, 250, "cheer", ("#E8574A", "#3D6E92", "#2E8A57")[n], mood="happy",
                   role="worker_f" if n == 1 else "worker")
    if seg.since(b, 3, t) >= 0:
        fx.sparks(c, 820, 860, seg.since(b, 3, t), ["#FFE14D", "#E8574A", "#FFFFFF"], 24, 3, 260, 22)
    sfx(c, "耶！", 820, 760, 110, seg.since(b, 3, t), rot=8)
    caption_box(c, "大家干劲十足", 610, 690, 32)


def p3(c, lt, t):
    b = seg.BARS[3]
    spin = 3 * ease_in_out(clamp01(seg.since(b, 0, t) / (tb(3, 2) - tb(3, 0))))
    blur = 1 - abs(2 * clamp01(seg.since(b, 0, t) / (tb(3, 2) - tb(3, 0))) - 1)
    speed_lines(c, 380, 1570, 0.6 * blur, 200, seed=8, color="#FFFFFF")
    clock(c, 380, 1570, 220, spin)
    figure(c, 820, 1840, 330, "sit_sad" if seg.since(b, 2, t) >= 0 else "stand", None,
           mood="sad" if seg.since(b, 2, t) >= 0 else "calm", face=-1, role="worker")
    sfx(c, "咔哒", 640, 1360, 80, seg.since(b, 0, t), rot=-6, fill="#FFFFFF")
    sfx(c, "……又是老样子？", 760, 1450, 52, seg.since(b, 2, t), rot=0, fill="#FFFFFF")
    caption_box(c, "三个月后", 52, 1300, 36)


def p4(c, lt, t):
    b = seg.BARS[4]
    speed_lines(c, 540, 900, 1.0 if seg.since(b, 0, t) >= 0 else 0, 420, n=90, seed=11)
    d0, d1 = seg.since(b, 0, t), seg.since(b, 1, t)
    st = fx.word_pop(d0, 0.24)
    if st:
        a, s_, _ = st
        with K.at(c, 540, 700, -4, s_):
            gfx.draw_text(c, "不是人的问题", 0, 0, 130, "black", "#FFFFFF", a, stroke=(INKC, 34))
            gfx.draw_text(c, "不是人的问题", 0, 0, 130, "black", "#FFFFFF", a)
    st = fx.word_pop(d1, 0.24)
    if st:
        a, s_, _ = st
        with K.at(c, 540, 1000, 3, s_ * 1.05):
            gfx.draw_text(c, "是结构", 0, 0, 260, "black", "#FFE14D", a, stroke=("#FFFFFF", 70))
            gfx.draw_text(c, "是结构", 0, 0, 260, "black", "#E8402E", a, stroke=(INKC, 34))
            gfx.draw_text(c, "是结构", 0, 0, 260, "black", "#E8402E", a)
    sfx(c, "咚！", 210, 420, 140, d0, rot=-18)
    sfx(c, "咚！", 880, 1280, 140, d1, rot=14)
    if seg.since(b, 2, t) >= 0:
        fx.sparks(c, 540, 1000, seg.since(b, 2, t), ["#FFE14D", "#FFFFFF"], 30, 9, 420, 26)
    caption_box(c, "书中观点", 60, 1700, 44)


def p5(c, lt, t):
    b = seg.BARS[5]
    book(c, 300, 380, 0.9)
    if seg.since(b, 1, t) >= 0:
        k = ease_out(clamp01(seg.since(b, 1, t) / 0.4))
        slinky(c, 780, 230, 230 * k + 20)
        K.rr(c, 780, 200, 150, 80, 36, "#F3D2B5")
        K.rr_stroke(c, 780, 200, 150, 80, 36, INKC, 6)
    sfx(c, "唰", 960, 140, 80, seg.since(b, 0, t), rot=10)
    caption_box(c, "书一开头，拿出弹簧", 52, 96, 34)


def p6(c, lt, t, out=False):
    """松手：弹簧掉落并冲出下边框（out=True 时画格外部分）。"""
    b = seg.BARS[6]
    d = seg.since(b, 1, t)
    if d < 0:
        if not out:
            slinky(c, 540, 760, 250)
            K.rr(c, 540, 730, 150, 80, 36, "#F3D2B5")
            K.rr_stroke(c, 540, 730, 150, 80, 36, INKC, 6)
        return
    length = 250 + 380 * abs(math.sin(d * 6)) * math.exp(-d * 1.2) + 260 * ease_out(clamp01(d / 0.25))
    slinky(c, 540, 760 + 40 * ease_out(clamp01(d / 0.2)), length)
    if not out:
        speed_lines(c, 540, 1000, clamp01(1 - d / 0.5), 300, seed=21)
        sfx(c, "啪！", 820, 820, 130, d, rot=12)
        sfx(c, "哗——", 260, 1080, 90, seg.since(b, 2, t), rot=-8, fill="#9FE3FF")
        caption_box(c, "手一松，它自己弹", 52, 790, 34)


def p7(c, lt, t):
    b = seg.BARS[7]
    words = [("行为", 250, 1500), ("藏在", 560, 1500), ("结构", 540, 1700), ("里", 850, 1700)]
    for n, (w, x, y) in enumerate(words):
        st = fx.word_pop(seg.since(b, n, t), 0.28)
        if not st:
            continue
        a, s_, _ = st
        hi = w == "结构"
        with K.at(c, x, y, -4 if hi else 0, s_):
            if hi:
                K.rr(c, 0, 0, 320, 170, 20, "#E8402E", a)
                K.rr_stroke(c, 0, 0, 320, 170, 20, INKC, 8, a)
            gfx.draw_text(c, w, 0, 0, 130, "black", "#FFFFFF" if hi else INKC, a, stroke=None)
    if seg.since(b, 2, t) >= 0:
        speed_lines(c, 540, 1700, clamp01(1 - seg.since(b, 2, t) / 0.5) * 0.7, 230, seed=31)


CONTENT = {0: p0, 1: p1, 2: p2, 3: p3, 4: p4, 5: p5, 6: p6, 7: p7}


# ---------------------------------------------------------------- 页面与相机

def draw_page(c, name, cur, t):
    c.drawRect(skia.Rect.MakeWH(seg.W, seg.H), K.paint("#FBF8F1"))
    for i, pts in PAGES[name].items():
        path = poly_path(pts)
        c.save()
        c.clipPath(path, doAntiAlias=True)
        c.drawImage(panel_bg(i), 0, 0)
        if i <= cur:
            tt = t if i == cur else seg.BARS[i]["t1"] - 0.02
            CONTENT[i](c, tt - seg.BARS[i]["t0"], tt)
        c.restore()
        c.drawPath(path, K.paint(INKC, 1, 12))
    for i, pts in PAGES[name].items():
        if i != cur:
            c.drawPath(poly_path(pts), K.paint("#000000", 0.45 if i < cur or name != PAGE_OF[cur] else 0.6))
    if name == "C" and cur >= 6:
        # 跨格：弹簧冲出第 6 格下边框，压到下一格上
        tt = t if cur == 6 else seg.BARS[6]["t1"] - 0.02
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, 1236, seg.W, 1560))
        p6(c, 0, tt, out=True)
        c.restore()


def cam_for(i):
    x0, y0, x1, y1 = bounds(PAGES[PAGE_OF[i]][i])
    w, h = x1 - x0, y1 - y0
    z = min(1040 / w, 1700 / h, 1.75)
    return (x0 + x1) / 2, (y0 + y1) / 2, z


def apply_cam(c, cx, cy, z, dx=0.0):
    c.translate(seg.W / 2 + dx, seg.H / 2)
    c.scale(z, z)
    c.translate(-cx, -cy)


def draw(c, t):
    b, lt = seg.bar_at(t)
    i = b["i"]
    c.drawColor(skia.ColorSetRGB(24, 22, 28))
    cur = cam_for(i)
    page = PAGE_OF[i]
    prev_i = max(0, i - 1)
    new_page = i > 0 and PAGE_OF[prev_i] != page
    k = ease_in_out(clamp01(lt / 0.32)) if i > 0 else 1.0
    shake = 0.0
    for (bi, kb) in ((4, 0), (4, 1), (6, 1)):
        d = t - tb(bi, kb)
        if 0 <= d < 0.3:
            shake += 16 * math.exp(-d * 14) * math.sin(d * 80)
    if new_page and k < 1:
        prev = cam_for(prev_i)
        c.save()
        apply_cam(c, *prev, dx=-seg.W * k)
        draw_page(c, PAGE_OF[prev_i], prev_i, seg.BARS[prev_i]["t1"] - 0.02)
        c.restore()
        c.save()
        apply_cam(c, *cur, dx=seg.W * (1 - k))
        draw_page(c, page, i, t)
        c.restore()
        return
    prev = cam_for(prev_i) if i > 0 else (540, 960, 1.0)
    cx, cy = lerp(prev[0], cur[0], k), lerp(prev[1], cur[1], k)
    z = math.exp(lerp(math.log(prev[2]), math.log(cur[2]), k))
    c.save()
    c.translate(shake, shake * 0.6)
    apply_cam(c, cx, cy, z)
    draw_page(c, page, i, t)
    c.restore()
    if i == 4:
        for kb in (0, 1):
            fl = fx.flash_alpha(seg.since(b, kb, t), 0.5)
            if fl > 0:
                c.drawPaint(K.paint("#FFFFFF", fl))


if __name__ == "__main__":
    seg.main("comic", draw)
