"""一镜到底长卷：一幅很长的彩色水墨横卷，相机从左到右连续平移（无硬切），四层视差（远山、近丘、地面、前景草木）；
8 个小节的场景依次画在卷上不同位置，相机在每小节内缓慢漂移、在小节末尾快速滑到下一处；已经过的场景保持终态留在卷上。
底部为固定在屏幕上的字幕条，顶部为卷名。"""

import math

import numpy as np
import skia

from adler import fx
from adler import kit as K
from engine import gfx
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from maoxuan import ink
from styles import seg
from xitong import art as A

ink.install()
W, H = seg.W, seg.H
GROUND = 1300
GAP = 1000                                  # 相邻场景在卷上的间距（相邻场景边缘会露出，强化“连续长卷”）
CENTERS = [540 + i * GAP for i in range(8)]
SCROLL_W = CENTERS[-1] + 1400


class FakeG:
    """给元件函数用的拍点上下文：since(k) 以该场景所在小节的实测拍点计时。"""

    def __init__(self, c, bar, t):
        self.c, self.bar, self.t_abs = c, bar, t
        self.t = t - bar["t0"]
        self.acc, self.acc2 = A.TEAL, K.GOLD

    def since(self, k):
        return seg.since(self.bar, k, self.t_abs)

    def p(self, k, dur=0.45, ease=ease_out):
        return ease(clamp01(self.since(k) / dur)) if dur > 0 else float(self.since(k) >= 0)

    def span(self, k0, k1, ease=ease_in_out):
        a, b = self.since(k0), self.since(k1)
        d = a - b
        return ease(clamp01(a / max(1e-6, d)))

    def pulse(self, decay=6.0, downbeat=False):
        best = 0.0
        for k in range(4):
            dt = self.since(k)
            if 0 <= dt:
                best = math.exp(-dt * decay)
        return best

    @property
    def exit(self):
        return 0.0


def camera_x(t: float) -> float:
    bar, lt = seg.bar_at(t)
    i = bar["i"]
    d = bar["t1"] - bar["t0"]
    x = CENTERS[i] + (lt / d - 0.5) * 140
    move = 0.38
    if i < 7 and lt > d - move:
        k = ease_in_out((lt - (d - move)) / move)
        x = lerp(x, CENTERS[i + 1] - 70, k)
    return x


def _ridge(x0, x1, base, amp, seed, freq):
    rng = np.random.default_rng(seed)
    ph = rng.random(5) * 6.28
    p = skia.Path()
    p.moveTo(x0, H)
    xs = np.arange(x0, x1 + 40, 40)
    for x in xs:
        y = base + sum(amp / k * math.sin(x * freq * k / 1000 + ph[k - 1]) for k in range(1, 6))
        p.lineTo(float(x), float(y))
    p.lineTo(x1, H)
    p.close()
    return p


_LAYERS = {}


def _layer_paths():
    if not _LAYERS:
        _LAYERS["far"] = _ridge(-600, SCROLL_W * 0.35 + 1200, 760, 130, 3, 1.3)
        _LAYERS["mid"] = _ridge(-600, SCROLL_W * 0.65 + 1200, 980, 90, 8, 2.2)
        _LAYERS["ground"] = _ridge(-600, SCROLL_W + 600, GROUND + 10, 14, 13, 3.0)
    return _LAYERS


def draw_backdrop(c, cx):
    c.drawImage(ink.bg_image(A.TEAL), 0, 0)
    L = _layer_paths()
    for name, f, col, a in (("far", 0.35, "#8FA6A0", 0.35), ("mid", 0.65, "#6F8C86", 0.45)):
        with K.at(c, -(cx - 540) * f, 0):
            c.drawPath(L[name], K.paint(col, a, blur=4))
            c.drawPath(L[name], K.paint(K.shade(col, 0.3), a * 0.7, 3, blur=1))


def draw_ground(c):
    L = _layer_paths()
    c.drawPath(L["ground"], K.paint("#E8DCC2", 0.95))
    c.drawPath(L["ground"], K.paint(ink.INK_SOFT, 0.6, 4, blur=1))


def draw_foreground(c, cx):
    with K.at(c, -(cx - 540) * 1.35, 0):
        rng = np.random.default_rng(5)
        for i in range(60):
            x = i * 260 + rng.random() * 120
            h = 60 + rng.random() * 90
            for j in range(5):
                a = (j - 2) * 0.25
                K.seg(c, x, H - 40, x + math.sin(a) * h, H - 40 - math.cos(a) * h, "#4E6660", 6, 0.55)


# ---------------------------------------------------------------- 各场景（坐标为卷上世界坐标）

def scene(c, i, t):
    bar = seg.BARS[i]
    g = FakeG(c, bar, t)
    x = CENTERS[i]
    if i == 0:
        _pavilion(c, x, g)
        K.figure(c, x + 160, GROUND, 340, "wave" if g.since(1) >= 0 else "stand", K.DARK, alpha=1, face=-1,
                 mood="smile", hair="short", role="boss")
        K.figure(c, x - 230, GROUND, 300, "stand", K.HERO, mood="calm", hair="short", role="worker")
        st = fx.word_pop(g.since(2))
        if st:
            a, s_, _ = st
            with K.at(c, x + 60, GROUND - 520, 0, s_):
                K.bubble(c, 0, 0, "咱们【重新出发】！", 46, (0.4, 1), a)
    elif i == 1:
        with K.at(c, x, GROUND - 420):
            A.desks(c, g, 0, dict(swap=1, step=0.5, mood="smile"))
    elif i == 2:
        for j, (dx, role, col, b) in enumerate(((-280, "worker", K.HERO, 0), (0, "worker_f", None, 1),
                                                 (280, "worker", "#C98B5A", 2))):
            up = g.since(b) >= 0
            K.figure(c, x + dx, GROUND, 310, "cheer" if up else "stand", col, mood="happy" if up else "calm",
                     hair="long" if role == "worker_f" else "short", role=role, face=-1 if dx > 0 else 1,
                     bob=0.04 * abs(math.sin(g.t * 9)) if up else 0)
            if 0 <= g.since(b) < 0.9:
                fx.sparks(c, x + dx, GROUND - 380, g.since(b), [K.GOLD, A.TEAL, K.PAPER], 16, j + 3, 220, 16)
    elif i == 3:
        spin = max(0.0, g.since(0)) * 900
        with K.at(c, x, GROUND - 520):
            K.ring(c, 0, 0, 170, K.INK2, 16)
            K.dot(c, 0, 0, 150, K.PAPER)
            with K.at(c, 0, 0, spin):
                K.seg(c, 0, 0, 0, -120, K.INK, 10)
            with K.at(c, 0, 0, spin / 12):
                K.seg(c, 0, 0, 0, -80, K.INK, 14)
        if g.since(2) >= 0:
            K.pill(c, x, GROUND - 260, "三个月后", 52, A.RED, K.PAPER, clamp01(g.since(2) / 0.2))
        for k in range(12):
            ft = (g.t * 0.6 + k * 0.17) % 1.0
            K.dot(c, x - 420 + k * 75, GROUND - 900 + ft * 800, 12, "#C97B3A", 0.6 * (1 - ft))
    elif i == 4:
        for j, (txt, y, b, size) in enumerate((("不是人的问题", GROUND - 700, 0, 130), ("是结构", GROUND - 420, 1, 200))):
            k = clamp01(g.since(b) / 0.22)
            if k <= 0:
                continue
            c.save()
            w = K.text_w(txt, size, "serif_black")
            c.clipRect(skia.Rect.MakeLTRB(x - w / 2 - 20, y - size, x - w / 2 - 20 + (w + 40) * k, y + size))
            if j == 1:
                fx.glow(c, x, y, 380, K.GOLD, 0.4)
            K.text(c, txt, x, y, size, "serif_black", A.TEAL if j else K.INK, 1, shadow=(4, 6, 8, K.SHADOW))
            c.restore()
        if g.since(2) >= 0:
            K.pill(c, x, GROUND - 230, "书中观点", 40, K.INK2, K.PAPER, clamp01(g.since(2) / 0.2))
    elif i in (5, 6):
        if i == 5:
            K.icon(c, "book", x - 300, GROUND - 200, 220, A.TEAL)
        drop = 1 if i == 6 else None
        with K.at(c, x + (60 if i == 5 else 0), GROUND - 470):
            A.slinky(c, g, 0, dict(drop=drop) if drop is not None else {})
    elif i == 7:
        words = [("行为", K.INK), ("藏在", K.INK), ("结构", A.TEAL), ("里", K.INK)]
        for j, (wd, col) in enumerate(words):
            st = fx.word_pop(g.since(j))
            if not st:
                continue
            a, s_, _ = st
            y = GROUND - 760 + j * 170
            with K.at(c, x - 120 + j * 80, y, -3 + j * 2, s_):
                if wd == "结构":
                    fx.glow(c, 0, 0, 220, K.GOLD, 0.45 * a)
                    K.rr(c, 0, 0, 300, 150, 18, A.TEAL, a)
                    K.text(c, wd, 0, 0, 120, "serif_black", K.PAPER, a)
                else:
                    K.text(c, wd, 0, 0, 120, "serif_black", col, a)


def _pavilion(c, x, g):
    """卷首的小亭子（办公楼的古意写法）。"""
    K.poly(c, [(x - 420, GROUND - 600), (x, GROUND - 760), (x + 420, GROUND - 600)], "#8A5A35")
    K.rr(c, x - 340, GROUND - 300, 30, 600, 6, "#6E4A2E")
    K.rr(c, x + 340, GROUND - 300, 30, 600, 6, "#6E4A2E")
    K.rr(c, x, GROUND - 590, 760, 24, 6, "#6E4A2E")


def draw(c, t):
    cx = camera_x(t)
    bob = 6 * math.sin(t * 1.3)
    draw_backdrop(c, cx)
    bar, lt = seg.bar_at(t)
    shake = 0.0
    if bar["i"] in (4, 6):
        for k in ((0, 1) if bar["i"] == 4 else (1,)):
            dt = seg.since(bar, k, t)
            if 0 <= dt < 0.35:
                shake = max(shake, 14 * math.exp(-dt * 9))
    with K.at(c, -(cx - 540) + shake * math.sin(t * 90), bob + shake * math.cos(t * 70)):
        draw_ground(c)
        for i in range(8):
            if abs(CENTERS[i] - cx) < 1300:
                scene(c, i, t)
    draw_foreground(c, cx)
    # 屏幕固定：卷名与字幕
    K.text(c, "系统之美 · 一镜到底长卷", 72, 190, 32, "sans_medium", K.INK2, 1, "left")
    K.seg(c, 72, 240, W - 72, 240, K.INK3, 2)
    K.seg(c, 72, 240, 72 + (W - 144) * t / seg.TOTAL, 240, A.TEAL, 4)
    a = clamp01(lt / 0.25)
    K.rr(c, W / 2, 1610, 900, 120, 60, "#F7F0E2", 0.88 * a)
    K.text(c, bar["text"], W / 2, 1610, 56, "serif", K.INK, a)
    if bar["i"] == 4:
        for k in (0, 1):
            fl = fx.flash_alpha(seg.since(bar, k, t), 0.5)
            if fl > 0:
                c.drawPaint(K.paint(K.PAPER, fl))
    fade = max(1 - clamp01(t / 0.3), clamp01((t - (seg.TOTAL - 0.4)) / 0.4))
    if fade > 0:
        c.drawPaint(K.paint("#F3EBDA", fade))


if __name__ == "__main__":
    seg.main("scroll", draw)
