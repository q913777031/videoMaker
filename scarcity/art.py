"""《稀缺》系列的专用元件：带宽条、隧道视野、循环箭头、行李箱、果篮、账单。
在阿德勒系列的纸片剪影元件（adler.kit）与光效层（adler.fx）之上组合，坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

GROUND_Y = 1130


def ground(g):
    K.ground(g.c, GROUND_Y)


def meter(c, g, el_t, d):
    """带宽条：整条为心智容量；eat [(拍, 比例, 名称)] 依次从右往左被占用，剩余部分随节拍轻微发光。"""
    w, h = d.get("w", 760), d.get("h", 120)
    K.card(c, 0, 0, w + 36, h + 36, K.PAPER, 1, r=30)
    x0 = -w / 2
    used = 0.0
    blocks = []
    for b, frac, name in d.get("eat", []):
        k = ease_out(clamp01(g.since(b) / 0.35))
        if k <= 0:
            continue
        blocks.append((used, frac * k, name, k))
        used += frac * k
    free = 1 - used
    col = g.acc if free > 0.45 else K.RED
    fx.glow(c, x0 + w * free / 2, 0, w * 0.45, col, 0.18 + 0.12 * g.pulse(5))
    K.rr(c, x0 + w * free / 2, 0, max(1.0, w * free), h, 20, col)
    x = x0 + w
    for u, f, name, k in blocks:
        bw = w * f
        K.rr(c, x - bw / 2, 0, max(1.0, bw - 6), h, 20, K.DARK, k)
        if bw > 120:
            K.text(c, name, x - bw / 2, 0, 38, "sans_medium", K.PAPER, k)
        x -= bw
    label = d.get("label", "带宽")
    K.text(c, label, 0, -h / 2 - 70, 46, "serif_black", K.INK)
    if d.get("pct", True):
        K.text(c, f"剩余 {round(free * 100):d}%", 0, h / 2 + 70, 40, "sans_medium", col)


def tunnel(c, g, el_t, d):
    """隧道视野：舞台区（不压字幕与页眉）四周压暗，中间留一个圆洞；r 为洞的半径，随进度从大收到小。
    box 为压暗区域 (左, 上, 右, 下)，以元素中心为原点。"""
    r = lerp(d.get("r0", 900), d.get("r", 300), ease_in_out(clamp01(el_t / d.get("close", 1.2))))
    cx, cy = d.get("cx", 0), d.get("cy", 0)
    p = skia.Path()
    l, t, r_, b = d.get("box", (-500, -440, 500, 460))
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(l, t, r_, b), 40, 40))
    p.addCircle(cx, cy, r)
    p.setFillType(skia.PathFillType.kEvenOdd)
    paint = K.paint(K.INK, d.get("dark", 0.78), blur=18)
    c.drawPath(p, paint)
    K.ring(c, cx, cy, r, g.acc2, 6, 0.6 + 0.4 * g.pulse(6))


def cycle(c, g, el_t, d):
    """循环箭头图：labels 均匀排在圆上，第 i 段箭头在 b0 + i*step 拍画出，节点为纸片标签。"""
    labels = d["labels"]
    R = d.get("R", 280)
    n = len(labels)
    b0, step = d.get("b0", 0), d.get("step", 2)
    pts = [(R * math.cos(-math.pi / 2 + i * math.tau / n), R * math.sin(-math.pi / 2 + i * math.tau / n)) for i in range(n)]
    for i in range(n):
        k = clamp01(g.since(b0 + i * step + 1) / 0.5)
        if k <= 0:
            continue
        a0 = -90 + i * 360 / n + 22
        sweep = 360 / n - 44
        rect = skia.Rect.MakeXYWH(-R, -R, 2 * R, 2 * R)
        path = skia.Path()
        path.addArc(rect, a0, sweep * ease_out(k))
        c.drawPath(path, K.paint(g.acc, 1, stroke=12))
        if k >= 1:
            ang = math.radians(a0 + sweep)
            hx, hy = R * math.cos(ang), R * math.sin(ang)
            tang = ang + math.pi / 2
            K.poly(c, [(hx + 26 * math.cos(tang), hy + 26 * math.sin(tang)),
                       (hx + 14 * math.cos(tang + 2.3), hy + 14 * math.sin(tang + 2.3)),
                       (hx + 14 * math.cos(tang - 2.3), hy + 14 * math.sin(tang - 2.3))], g.acc)
    spin = d.get("spin_at")
    rot = 0.0 if spin is None or g.since(spin) < 0 else g.since(spin) * 50
    for i, (x, y) in enumerate(pts):
        st = fx.word_pop(g.since(b0 + i * step))
        if st is None:
            continue
        a, s_, r_ = st
        hi = i == d.get("hi", -1)
        with K.at(c, x, y, r_ * 0.6, s_):
            fx.draw_word(c, labels[i], 0, 0, 52, "serif_black", K.INK, g.acc if hi else K.DARK, K.PAPER, a, True)
    if spin is not None and g.since(spin) >= 0:
        fx.rays(c, 0, 0, R * 0.7, g.acc2, g.t, 10, 0.25, 40)
        with K.at(c, 0, 0, rot):
            K.ring(c, 0, 0, R * 0.32, g.acc2, 8, 0.8, 0.75)


def suitcase(c, x, y, w, h, color, items, alpha=1.0, p=1.0):
    """行李箱：items [(相对 x, 相对 y, 尺寸, 颜色)] 为装进去的物品（p 为装入进度）。"""
    K.card(c, x, y, w, h, color, alpha, r=26)
    K.rr_stroke(c, x, y - h / 2 - 22, w * 0.3, 44, 18, K.shade(color, 0.3), 12, alpha)
    for i, (ix, iy, s, col) in enumerate(items):
        k = clamp01(p * len(items) - i)
        if k <= 0:
            continue
        K.rr(c, x + ix * w / 2, y + iy * h / 2 - (1 - ease_out(k)) * 80, s, s * 0.7, 10, col, alpha * k)


def basket(c, x, y, s, alpha=1.0, n=7):
    """果篮：编织纹篮子 + 一堆圆形水果。"""
    cols = ["#D9593A", "#E3A33B", "#7FA34A", "#C0504D", "#E8B84A", "#6F9E3F", "#D9703A"]
    for i in range(n):
        a = i / max(1, n - 1)
        K.dot(c, x + (a - 0.5) * s * 0.9, y - s * 0.28 - math.sin(a * math.pi) * s * 0.18, s * 0.17, cols[i % len(cols)], alpha)
    K.poly(c, [(x - s * 0.62, y - s * 0.25), (x + s * 0.62, y - s * 0.25), (x + s * 0.45, y + s * 0.3),
               (x - s * 0.45, y + s * 0.3)], "#B98A55", alpha)
    for j in range(3):
        yy = y - s * 0.1 + j * s * 0.13
        K.seg(c, x - s * 0.55 + j * 0.06 * s, yy, x + s * 0.55 - j * 0.06 * s, yy, "#94693C", 6, alpha)


def bill(c, g, el_t, d):
    """账单纸：标题 + 几行横线 + 红色金额条。"""
    w, h = d.get("w", 260), d.get("h", 320)
    K.card(c, 0, 0, w, h, K.PAPER, 1, r=14)
    K.text(c, d.get("title", "账单"), 0, -h / 2 + 50, 40, "serif_black", K.INK)
    for i in range(3):
        K.seg(c, -w / 2 + 34, -h / 2 + 110 + i * 46, w / 2 - 34 - (i % 2) * 50, -h / 2 + 110 + i * 46, K.LINE, 8)
    K.rr(c, 0, h / 2 - 54, w - 70, 46, 12, K.RED)
    K.text(c, d.get("amount", "待付"), 0, h / 2 - 54, 30, "sans_medium", K.PAPER)


# ---------------------------------------------------------------- 上班族日常场景

def clock_digital(c, g, el_t, d):
    """电子钟：显示 hh:mm，每拍跳一分钟（从 t0 到 t1），最后几分钟变红并随拍闪动。"""
    t0, t1 = d.get("t0", 8 * 60 + 50), d.get("t1", 8 * 60 + 58)
    b0 = d.get("b0", 0)
    m = int(min(t1, t0 + max(0, int(g.since(b0) / max(1e-6, g.b(b0 + 1) - g.b(b0))) if g.since(b0) >= 0 else 0)))
    w, h = d.get("w", 360), d.get("h", 150)
    late = m >= t1 - 2
    col = K.RED if late else K.INK
    K.card(c, 0, 0, w, h, K.PAPER, 1, r=28)
    if late:
        fx.glow(c, 0, 0, w * 0.9, K.RED, 0.2 + 0.25 * g.pulse(6))
    K.text(c, f"{m // 60:02d}:{m % 60:02d}", 0, 0, h * 0.62, "black", col, 1)
    if d.get("label"):
        K.text(c, d["label"], 0, h / 2 + 44, 34, "sans_medium", K.INK2)


def badge(c, x, y, s, color, alpha=1.0):
    """工牌：挂绳 + 卡片 + 头像与两行字。"""
    K.seg(c, x - s * 0.18, y - s * 0.75, x, y - s * 0.38, color, s * 0.05, alpha)
    K.seg(c, x + s * 0.18, y - s * 0.75, x, y - s * 0.38, color, s * 0.05, alpha)
    K.card(c, x, y, s * 0.62, s * 0.8, K.PAPER, alpha, r=s * 0.06)
    K.rr(c, x, y - s * 0.28, s * 0.62, s * 0.12, s * 0.03, color, alpha)
    K.dot(c, x, y - s * 0.06, s * 0.12, K.SKIN, alpha)
    K.rr(c, x, y + s * 0.16, s * 0.36, s * 0.05, s * 0.02, K.INK2, alpha)
    K.rr(c, x, y + s * 0.26, s * 0.26, s * 0.04, s * 0.02, K.LINE, alpha)


def checklist(c, g, el_t, d):
    """出门清单：items [(文字, 是否带了)]，第 i 项在 b0 + i*step 拍打勾或打叉。"""
    items = d["items"]
    b0, step = d.get("b0", 0), d.get("step", 1)
    w = d.get("w", 600)
    rh = 112
    h = rh * len(items) + 130
    K.card(c, 0, 0, w, h, K.PAPER, 1, r=24, accent=g.acc)
    K.text(c, d.get("title", "出门清单"), 0, -h / 2 + 62, 50, "serif_black", K.INK)
    for i, (name, ok) in enumerate(items):
        y = -h / 2 + 140 + i * rh + rh / 2 - 20
        K.text(c, name, -w / 2 + 60, y, 52, "serif", K.INK, 1, "left")
        st = fx.word_pop(g.since(b0 + i * step))
        if st is None:
            K.rr_stroke(c, w / 2 - 80, y, 62, 62, 12, K.LINE, 5)
            continue
        a, s_, _ = st
        with K.at(c, w / 2 - 80, y, 0, s_):
            K.icon(c, "check" if ok else "cross", 0, 0, 80, K.GREEN if ok else K.RED, a, 0.4, 0, 1, 1, g.acc2)


def phone_chat(c, g, el_t, d):
    """手机聊天：msgs [(拍, 文字)] 依次弹出（左侧对方气泡），右上角未读数随消息增加。"""
    w, h = d.get("w", 520), d.get("h", 820)
    K.card(c, 0, 0, w, h, K.DARK, 1, r=48)
    K.rr(c, 0, 0, w - 30, h - 30, 36, K.PAPER)
    K.text(c, d.get("who", "妈妈"), 0, -h / 2 + 70, 44, "sans_medium", K.INK)
    K.seg(c, -w / 2 + 30, -h / 2 + 112, w / 2 - 30, -h / 2 + 112, K.LINE, 3)
    n = 0
    for i, (b, txt) in enumerate(d["msgs"]):
        st = fx.word_pop(g.since(b))
        if st is None:
            continue
        n += 1
        a, s_, _ = st
        tw = min(w - 80, K.text_w(txt, 42, "sans_medium") + 50)
        y = -h / 2 + 190 + i * 126
        with K.at(c, -w / 2 + 40 + tw / 2, y, 0, s_):
            K.rr(c, 0, 0, tw, 88, 28, "#E9E2D6", a)
            K.text(c, txt, 0, 0, 42, "sans_medium", K.INK, a)
    if n and d.get("unread", True):
        K.dot(c, w / 2 - 10, -h / 2 + 10, 44, K.RED)
        K.text(c, str(n), w / 2 - 10, -h / 2 + 10, 46, "black", K.PAPER)


def laptop(c, g, el_t, d):
    """笔记本电脑：屏幕上一条进度条，从 p0 到 p1 在 b0→b1 拍间推进，并显示标题。"""
    w, h = d.get("w", 560), d.get("h", 350)
    K.card(c, 0, 0, w, h, K.DARK, 1, r=20)
    K.rr(c, 0, 0, w - 34, h - 34, 10, "#EEF2F6")
    K.poly(c, [(-w / 2 - 50, h / 2 + 4), (w / 2 + 50, h / 2 + 4), (w / 2 + 80, h / 2 + 40), (-w / 2 - 80, h / 2 + 40)], K.INK2)
    K.text(c, d.get("title", "汇报.pptx"), 0, -h / 2 + 70, 42, "sans_medium", K.INK)
    p = lerp(d.get("p0", 0.05), d.get("p1", 1.0), g.span(d.get("b0", 0), d.get("b1", 8)))
    K.rr(c, 0, 20, w - 110, 34, 17, K.LINE)
    pw = (w - 110) * p
    K.rr(c, -(w - 110) / 2 + pw / 2, 20, max(1.0, pw), 34, 17, g.acc)
    K.text(c, f"{round(p * 100)}%", 0, 96, 50, "black", g.acc)


def calendar(c, g, el_t, d):
    """一周日程：5 列 × rows 行，blocks [(列, 行, 跨行, 颜色, 出现拍)] 依次落入；gap 为空着的格子（余闲）。"""
    cols, rows = 5, d.get("rows", 6)
    cw, ch = d.get("cw", 176), d.get("ch", 96)
    W_, H_ = cols * cw + 40, rows * ch + 110
    K.card(c, 0, 0, W_, H_, K.PAPER, 1, r=24)
    x0, y0 = -cols * cw / 2, -H_ / 2 + 90
    for j, name in enumerate("一二三四五"):
        K.text(c, f"周{name}", x0 + j * cw + cw / 2, y0 - 42, 38, "sans_medium", K.INK2)
    for j in range(cols + 1):
        K.seg(c, x0 + j * cw, y0, x0 + j * cw, y0 + rows * ch, K.LINE, 2)
    for col, row, span, color, b in d.get("blocks", []):
        st = fx.word_pop(g.since(b))
        if st is None:
            continue
        a, s_, _ = st
        with K.at(c, x0 + col * cw + cw / 2, y0 + (row + span / 2) * ch, 0, s_):
            K.rr(c, 0, 0, cw - 12, span * ch - 10, 12, color, a)


# ---------------------------------------------------------------- 开场互动小游戏通用元件

def countdown(c, g, el_t, d):
    """倒计时：从 n 数到 1，每个数占 step 拍，外圈随真实时间收缩；结束拍弹出 end_text 红牌。"""
    n0, step = d.get("n", 3), d.get("step", 2)
    b0 = d.get("b0", 0)
    b_end = b0 + n0 * step
    if g.since(b_end) >= 0:
        dt = g.since(b_end)
        sc = 1 + 0.5 * (1 - ease_out(clamp01(dt / 0.2)))
        txt = d.get("end_text", "时间到！")
        w = K.text_w(txt, 80, "serif_black") + 120
        with K.at(c, 0, 0, -4, sc):
            K.rr(c, 0, 0, w, 140, 70, K.RED)
            K.text(c, txt, 0, 0, 80, "serif_black", K.PAPER)
        return
    if g.since(b0) < 0:
        return
    span = max(1e-6, g.b(b0 + step) - g.b(b0))
    n = n0 - int(max(0, min(n0 - 1, g.since(b0) // span)))
    k = clamp01(g.since(b0) / max(1e-6, g.b(b_end) - g.b(b0)))
    r = d.get("r", 92)
    K.dot(c, 0, 0, r, K.PAPER)
    K.ring(c, 0, 0, r, K.LINE, 14)
    K.ring(c, 0, 0, r, K.RED if n == 1 else g.acc, 14, 1, 1 - k)
    sc = 1 + 0.35 * (1 - ease_out(clamp01(g.since(b0 + (n0 - n) * step) / 0.18)))
    with K.at(c, 0, 0, 0, sc):
        K.text(c, str(n), 0, 0, r * 1.3, "black", K.RED if n == 1 else K.INK)


def flame(c, x, y, s, t=0.0, alpha=1.0):
    """小火苗：两层水滴形，随时间抖动。"""
    wob = 1 + 0.08 * math.sin(t * 14 + x)
    for col, k in (("#E8622C", 1.0), ("#F6C14B", 0.55)):
        h = s * k * wob
        p = skia.Path()
        p.moveTo(x, y - h)
        p.cubicTo(x + h * 0.55, y - h * 0.4, x + h * 0.5, y + h * 0.35, x, y + h * 0.4)
        p.cubicTo(x - h * 0.5, y + h * 0.35, x - h * 0.55, y - h * 0.4, x, y - h)
        c.drawPath(p, K.paint(col, alpha))


def fires(c, g, el_t, d):
    """火苗依次在 spots [(x, y, 出现拍)] 冒出；右上角计数随之增加。"""
    n = 0
    for x, y, b in d["spots"]:
        k = clamp01(g.since(b) / 0.25)
        if k <= 0:
            continue
        n += 1
        flame(c, x, y, 60 * (0.4 + 0.6 * ease_out(k)), g.t)
    if d.get("count", True):
        K.rr(c, 330, -330, 170, 90, 45, K.RED)
        K.text(c, f"×{n}", 330, -330, 56, "black", K.PAPER)


def toasts(c, g, el_t, d):
    """屏幕边缘的通知小卡：items [(拍, x, y, 文字)] 弹出后 hold 拍内保持，然后淡出。"""
    hold = d.get("hold", 3)
    for b, x, y, txt in d["items"]:
        st = fx.word_pop(g.since(b))
        if st is None:
            continue
        a, s_, _ = st
        a *= 1 - clamp01((g.since(b + hold)) / 0.3)
        if a <= 0:
            continue
        w = K.text_w(txt, 34, "sans_medium") + 50
        with K.at(c, x, y, 0, s_):
            K.card(c, 0, 0, w, 76, K.PAPER, a, r=20)
            K.dot(c, -w / 2 + 26, 0, 10, K.RED, a)
            K.text(c, txt, 6, 0, 34, "sans_medium", K.INK, a)


def digits(c, g, el_t, d):
    """记忆数字：seq 逐个弹出（b0 起每拍一个），hide 拍起用灰块盖住，reveal 拍起第 ask 位亮出答案。"""
    seq = d["seq"]
    b0, hide = d.get("b0", 0), d.get("hide", 99)
    w = 120
    x0 = -(len(seq) - 1) * w / 2
    for i, ch in enumerate(seq):
        x = x0 + i * w
        st = fx.word_pop(g.since(b0 + i * d.get("step", 0.5)))
        if st is None:
            continue
        a, s_, _ = st
        covered = g.since(hide) >= 0
        with K.at(c, x, 0, 0, s_):
            K.card(c, 0, 0, 100, 130, K.PAPER, a, r=16)
            if covered:
                ask = i == d.get("ask", -1)
                K.rr(c, 0, 0, 84, 112, 12, g.acc if ask else K.INK3, a)
                if ask and g.since(d.get("reveal", 99)) >= 0:
                    K.text(c, ch, 0, 0, 80, "black", K.PAPER, a)
                elif ask:
                    K.text(c, "?", 0, 0, 80, "black", K.PAPER, a)
            else:
                K.text(c, ch, 0, 0, 80, "black", K.INK, a)


def choice(c, g, el_t, d):
    """二选一卡片：left/right = (标题, 金额)；pick 拍起选中的一侧（pick_side）放大发光，另一侧变暗。"""
    side = d.get("pick_side", 0)
    picked = g.since(d.get("pick", 99)) >= 0
    for j, (title, amount, col) in enumerate((d["left"], d["right"])):
        x = (j - 0.5) * 440
        st = fx.word_pop(g.since(d.get("b0", 0) + j))
        if st is None:
            continue
        a, s_, _ = st
        sc = s_
        if picked:
            sc *= 1.12 if j == side else 0.9
            a *= 1 if j == side else 0.45
            if j == side:
                fx.glow(c, x, 0, 300, K.GOLD, 0.35 + 0.2 * g.pulse(5))
        with K.at(c, x, 0, 0, sc):
            K.card(c, 0, 0, 380, 420, col, a, r=36)
            K.text(c, title, 0, -100, 60, "serif_black", K.PAPER, a)
            K.text(c, amount, 0, 50, 110, "black", K.PAPER, a)


def find_grid(c, g, el_t, d):
    """找东西：cols×rows 个灰色闹钟里藏一个红色闹钟（target），角落有一个蛋糕（odd）；
    found 拍起红闹钟被圈出，odd_at 拍起蛋糕被圈出。"""
    cols, rows = d.get("cols", 5), d.get("rows", 4)
    gap = 150
    tx, ty = d.get("target", (3, 2))
    ox, oy = d.get("odd", (0, 3))
    for r in range(rows):
        for col in range(cols):
            x = (col - (cols - 1) / 2) * gap
            y = (r - (rows - 1) / 2) * gap
            k = clamp01(g.since(d.get("b0", 0) + 0.25 * (r * cols + col) / cols) / 0.25)
            if k <= 0:
                continue
            if (col, r) == (ox, oy):
                K.icon(c, "gift", x, y, 100, K.INK3, k, 0.5, 0, 1, 1, K.INK3)
            else:
                K.icon(c, "clock", x, y, 100, K.RED if (col, r) == (tx, ty) else K.INK3, k, 0.5, 8 * math.sin(col + r), 1, 1,
                       K.GOLD)
    for (cx, cy), key in (((tx, ty), "found"), ((ox, oy), "odd_at")):
        k = clamp01(g.since(d.get(key, 99)) / 0.3)
        if k > 0:
            x = (cx - (cols - 1) / 2) * gap
            y = (cy - (rows - 1) / 2) * gap
            K.ring(c, x, y, 80 * (1.4 - 0.4 * ease_out(k)), K.GREEN if key == "found" else K.RED, 8, k)


def memo(c, g, el_t, d):
    """待办便签：items 逐行出现（b0 起每拍一行）；cover 拍起整张被翻面盖住，只露出标题与“第 ask 件是？”。"""
    items = d["items"]
    w, rh = 600, 92
    h = rh * len(items) + 140
    covered = g.since(d.get("cover", 99)) >= 0
    K.card(c, 0, 0, w, h, "#FFF3B0", 1, r=20)
    K.text(c, d.get("title", "今天要做"), 0, -h / 2 + 60, 50, "serif_black", K.INK)
    if covered:
        k = clamp01(g.since(d["cover"]) / 0.3)
        K.rr(c, 0, 40, w - 60, h - 160, 16, g.acc, k)
        K.text(c, d.get("ask_text", "第 3 件是？"), 0, 40, 70, "serif_black", K.PAPER, k)
        return
    for i, txt in enumerate(items):
        st = fx.word_pop(g.since(d.get("b0", 0) + i))
        if st is None:
            continue
        a, s_, _ = st
        y = -h / 2 + 140 + i * rh
        with K.at(c, -w / 2 + 60, y, 0, s_):
            K.text(c, f"{i + 1}. {txt}", 0, 0, 46, "serif", K.INK, a, "left")
