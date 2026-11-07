"""《丰田模式》每讲的开场钩子（第 0 屏，黄金 3 秒）：用本讲的痛点画面 + 一句大字开场，“丰田模式”改成随后弹出的小字系列标识。

统一节奏（8 拍开场屏，约 4.3 秒）：
  第 0–2 拍 画面动作（每拍一个，配打击乐），第 3 拍 大字砸下（kick + 轻震，画面同拍到高潮），
  第 4 拍 小字系列标识弹出；之后不再出新笔画，停约 1.8 秒看清，再由本讲的转场缓缓进入第 1 屏。
接口：hook(H, j, cx, cy, acc)。H 要有 b（白板）、tb(j, k)（拍 → 绝对秒）、note(*字)（登记画面字给文案检查）。
画面以 (cx, cy) 为中心，开场视角 (cx, cy - 40, 0.7)：可视约 x ±620、y cy-680…cy+600，内容留在 x ±560、y cy-620…cy+560。
颜色用白板墨色（BLACK / RED / BLUE / GREEN），深色底由 theme.Recolor 统一反色；大字用本讲主题色 acc（不换色）。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, box_path, draw_li, pop_scale, slam_scale, wobble
from whiteboard import engine as wb
from whiteboard.engine import P, check, circle, join, rect

SERIES_SUB = "丰田模式 · 精益制造的14项原则"
GRAY = "#6B6B6B"


# ---------------------------------------------------------------- 公共件

def _big(H, j, k, s, x, y, size, color):
    H.note(s)

    def fn(c, kk, T):
        dt = T - H.tb(j, k)
        sc = slam_scale(dt)
        if sc > 0:
            with K.at(c, x, y, 0, sc):
                K.text(c, s, 0, 0, size, "hand", color, clamp01(dt / 0.06))
        return None
    return fn


def _label(H, j, k, x, y):
    H.note(SERIES_SUB)

    def fn(c, kk, T):
        sc = pop_scale(T - H.tb(j, k))
        if sc > 0:
            with K.at(c, x, y, 0, sc):
                w = K.text_w(SERIES_SUB, 46, "sans_medium") + 60
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -38, w, 76), 38, 38, wb.marker(GRAY, 4, clamp01(sc * 2)))
                K.text(c, SERIES_SUB, 0, 0, 46, "sans_medium", GRAY, clamp01(sc * 2))
        return None
    return fn


def _finish(H, j, cx, cy, text, acc, size=124, ty=None, shake=8.0, text_sfx="kick"):
    """第 3 拍大字 + 轻震，第 4 拍系列小字。"""
    b = H.b
    ty = cy + 250 if ty is None else ty
    b.custom(j, 3, 3.3, _big(H, j, 3, text, cx, ty, size, acc), sfx=text_sfx, gain=0.75)
    b.shots[j].shake = [(3, shake)]
    b.custom(j, 4, 4.3, _label(H, j, 4, cx, ty + size * 0.6 + 105), sfx="pop", gain=0.55)


def _stamp(H, j, k, s, x, y, size, rot, color=RED):
    H.note(s)
    w = K.text_w(s, size, "hand") + size * 0.8
    h = size * 1.45

    def fn(c, kk, T):
        dt = T - H.tb(j, k)
        sc = slam_scale(dt)
        if sc <= 0:
            return None
        a = clamp01(dt / 0.06)
        with K.at(c, x, y, rot, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 14, 14, K.paint("#FFFFFF", 0.8 * a))
            c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 14, 14, wb.marker(color, 10, a))
            c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 12, -h / 2 + 12, w - 24, h - 24), 8, 8, wb.marker(color, 4, a))
            K.text(c, s, 0, 0, size, "hand", color, a)
        return None
    return fn


def _doc_lines(x, y, w, h, n, top=0.22):
    parts = [rect(x, y, w, h, 18)]
    for i in range(n):
        yy = y - h / 2 + h * top + i * h * (0.7 / max(1, n))
        parts.append(P((x - w * 0.36, yy), (x + w * (0.36 if i % 3 != 2 else 0.12), yy)))
    return join(*parts)


# ---------------------------------------------------------------- 01 停线：同一份活被“返工”章盖了三遍

def stamp3(H, j, cx, cy, acc):
    b = H.b
    b.path(j, 0, 0.6, _doc_lines(cx, cy - 270, 540, 640, 7), BLACK, 10, sfx="wood_high")
    for k, (dx, dy, rot, size, sfx) in enumerate(((-120, -460, -14, 88, "rim"), (120, -280, 10, 92, "rim"))):
        b.custom(j, k + 1, k + 1.3, _stamp(H, j, k + 1, "返工", cx + dx, cy + dy, size, rot), sfx=sfx, gain=0.8)
    b.custom(j, 3, 3.3, _stamp(H, j, 3, "返工", cx - 10, cy - 90, 112, -5), sfx="tom", gain=0.8)
    _finish(H, j, cx, cy, "第三遍了", acc, size=150, ty=cy + 260, text_sfx="kick")


# ---------------------------------------------------------------- 02 拉动：活越堆越高，塌了

def pile(H, j, cx, cy, acc):
    b = H.b
    floor = cy + 40
    pieces = []                       # (宽, 高, 落下拍, 塌落方向, 塌落角)
    spec = [(420, 110, 0, -1, -70), (370, 105, 0, 1, 40), (390, 105, 1, -1, -35), (340, 100, 1, 1, 65),
            (360, 100, 2, -1, -55), (310, 95, 2, 1, 80)]
    y = floor
    for i, (w, h, k, d, ang) in enumerate(spec):
        pieces.append((w, h, k + (0.0 if i % 2 == 0 else 0.25), d, ang, y, (i * 37) % 23 - 11))
        y -= h
    b.path(j, 0, 0.5, P((cx - 520, floor), (cx + 520, floor)), BLACK, 9, sfx="wood_low")
    t_fall = lambda: H.tb(j, 3)

    def fn(c, kk, T):
        tf = t_fall()
        lean = 0.0
        for k_ in (1, 2):
            lean += wobble(T - H.tb(j, k_), 2.0 + k_ * 1.5, 16, 4)
        for i, (w, h, k, d, ang, yb, off) in enumerate(pieces):
            t0 = H.tb(j, k)
            dt = T - t0
            if dt < 0:
                continue
            drop = (1 - ease_out(clamp01(dt / 0.22))) * 420
            x, yy, rot = cx + off, yb - drop, lean * (i + 1) * 0.35
            if T > tf:
                f = ease_in_out(clamp01((T - tf) / 0.45))
                x += d * f * (160 + i * 60)
                yy = lerp(yy, floor - 40 - (i % 3) * 30, f)
                rot = lerp(rot, ang, f)
            with K.at(c, x, yy - h / 2, rot):
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 10, 10, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 10, 10, wb.marker(BLACK, 8))
                c.drawLine(-w * 0.32, 0, w * 0.2, 0, wb.marker(BLUE if i % 2 else RED, 8))
        if T > tf:
            dt = T - tf
            if dt < 0.5:
                for s_ in (-1, 1):
                    K.burst(c, cx + s_ * 300, floor - 20, dt, wb.BLACK, 30, 120, 6, 6, 0.7)
        return None
    b.custom(j, 0, 3.5, fn)
    b.hit(j, 1, "wood_high", 0.8, "又压上两份")
    b.hit(j, 2, "wood_high", 0.8, "再压三份，开始晃")
    b.custom(j, 3, 3.3, lambda c, k, T: None, sfx="tom", gain=0.8)
    _finish(H, j, cx, cy, "越堆越乱", acc, ty=cy + 270)


# ---------------------------------------------------------------- 03 均衡：忙闲曲线一笔划出

def curve(H, j, cx, cy, acc):
    b = H.b
    x0, x1, base = cx - 500, cx + 500, cy + 40
    b.path(j, 0, 0.5, join(P((x0, cy - 560), (x0, base), (x1, base)),
                           P((x1 - 30, base - 22), (x1, base), (x1 - 30, base + 22))), BLACK, 9, sfx="wood_low")
    pts = []
    for i in range(121):
        u = i / 120
        y = base - 60 - 230 * (1 + math.sin(u * math.pi * 4 - math.pi / 2)) * (0.75 + 0.25 * math.sin(u * 7))
        pts.append((x0 + 30 + u * 940, y))
    b.path(j, 1, 2.6, P(*pts), RED, 13, sfx="shaker", gain=0.7)
    hi = min(pts[:60], key=lambda p: p[1])
    lo = max(pts[40:90], key=lambda p: p[1])
    b.custom(j, 2, 2.3, _pop(H, j, 2, "忙死", hi[0], hi[1] - 70, 66, RED), sfx="pop")
    b.custom(j, 3, 3.3, _pop(H, j, 3, "闲死", lo[0], base + 70, 66, BLUE))
    _finish(H, j, cx, cy, "忙一阵 闲一阵", acc, size=112, ty=cy + 250)


def _pop(H, j, k, s, x, y, size, color, font="hand"):
    H.note(s)

    def fn(c, kk, T):
        sc = pop_scale(T - H.tb(j, k))
        if sc > 0:
            with K.at(c, x, y, 0, sc):
                K.text(c, s, 0, 0, size, font, color, clamp01(sc * 2))
        return None
    return fn


# ---------------------------------------------------------------- 04 单件流：十个进度条全卡在一半

def bars(H, j, cx, cy, acc):
    b = H.b
    n, x0, w, hgt, gap, top = 10, cx - 500, 780, 44, 72, cy - 640
    targets = [0.47, 0.52, 0.44, 0.55, 0.49, 0.5, 0.46, 0.53, 0.48, 0.51]
    outl = join(*[rect(x0 + w / 2, top + i * gap, w, hgt, 22) for i in range(n)])
    b.path(j, 0, 0.7, outl, BLACK, 7, sfx="wood_high")
    H.note(*[f"{int(t * 100)}%" for t in targets])

    def fn(c, kk, T):
        for i, tg in enumerate(targets):
            t0 = H.tb(j, 0.6 + i * 0.12)
            f = ease_out(clamp01((T - t0) / max(0.1, H.tb(j, 2.6) - t0)))
            p = tg * f
            if T > H.tb(j, 3):
                p += 0.006 * math.sin((T - H.tb(j, 3)) * 30 + i) * math.exp(-(T - H.tb(j, 3)) * 3)
            if p <= 0:
                continue
            y = top + i * gap
            c.drawRoundRect(skia.Rect.MakeXYWH(x0 + 6, y - hgt / 2 + 6, (w - 12) * p, hgt - 12), 16, 16,
                            K.paint(GREEN if T < H.tb(j, 3) else ORANGE))
            K.text(c, f"{int(round(p * 100))}%", x0 + w + 80, y, 48, "sans_medium", BLACK, clamp01((T - t0) / 0.2))
        tb3 = H.tb(j, 3)
        if T > tb3:
            a = clamp01((T - tb3) / 0.15)
            xm = x0 + w * 0.5
            c.drawLine(xm, top - 50, xm, top + (n - 1) * gap + 50, wb.marker(RED, 8, a))
        return None
    b.custom(j, 0.6, 2.6, fn)
    b.hit(j, 1, "shaker", 0.6, "进度条往前走")
    b.hit(j, 2, "wood_low", 0.8, "越走越慢")
    _finish(H, j, cx, cy, "全卡在一半", acc, size=136, ty=cy + 250, text_sfx="kick")


# ---------------------------------------------------------------- 05 标准化：清单第 100 遍，漏了一步

def checklist(H, j, cx, cy, acc):
    b = H.b
    x, top, w, h = cx - 40, cy - 640, 640, 700
    steps = ["写正文", "加附件", "抄送", "检查", "发送"]
    H.note(*steps, "发邮件 · 第100遍")
    clip = join(rect(x, top + h / 2, w, h, 26), rect(x, top + 10, 200, 56, 14))
    b.path(j, 0, 0.6, clip, BLACK, 9, sfx="wood_high")
    b.text(j, 0.4, 0.9, "发邮件 · 第100遍", x, top + 100, 54, BLACK, font="sans_medium")
    ys = [top + 210 + i * 104 for i in range(5)]
    boxes = join(*[rect(x - 220, y, 56, 56, 10) for y in ys])
    b.path(j, 0.6, 1.0, boxes, BLACK, 7)
    for y, s in zip(ys, steps):
        b.text(j, 0.7, 1.0, s, x + 20, y, 56, BLACK)
    for k, idx in ((1, (0,)), (2, (2, 3, 4))):
        for n, i in enumerate(idx):
            b.path(j, k + n * 0.18, k + n * 0.18 + 0.2, check(x - 220, ys[i], 30), GREEN, 10,
                   sfx="pop" if n == 0 else None, gain=0.6)
    ring = skia.Path()
    ring.addOval(skia.Rect.MakeXYWH(x - 300, ys[1] - 70, 460, 140))
    b.path(j, 3, 3.4, ring, RED, 11)
    b.custom(j, 3, 3.3, _pop(H, j, 3, "漏了", x + 330, ys[1], 80, RED))
    _finish(H, j, cx, cy, "做了100遍还漏", acc, size=108, ty=cy + 260)


# ---------------------------------------------------------------- 06 目视化：便利贴飘走了

def sticky(H, j, cx, cy, acc):
    b = H.b
    notes = [("周报", -260, -470, -6, 0), ("报销", 170, -500, 5, 1), ("交合同", -230, -170, 4, 1), ("回电话", 200, -160, -5, 2)]
    H.note(*[n[0] for n in notes])
    b.path(j, 0, 0.5, rect(cx - 20, cy - 330, 1000, 640, 20), BLACK, 8)

    def card(s, x, y, rot, k, fly):
        def fn(c, kk, T):
            sc = pop_scale(T - H.tb(j, k))
            if sc <= 0:
                return None
            xx, yy, rr, a = x, y, rot, 1.0
            if fly:
                t3 = H.tb(j, 3)
                if T > t3:
                    f = clamp01((T - t3) / 1.2)
                    e = ease_in_out(f)
                    xx += 420 * e + 40 * math.sin(f * 9)
                    yy -= 360 * e - 60 * math.sin(f * 5)
                    rr += 160 * e
                    a = 1 - clamp01((f - 0.55) / 0.45)
                    sc *= 1 - 0.3 * e
            with K.at(c, xx, yy, rr, sc):
                c.drawRect(skia.Rect.MakeXYWH(-130, -110, 260, 220), K.paint("#FFE58A", a))
                c.drawRect(skia.Rect.MakeXYWH(-130, -110, 260, 220), wb.marker(BLACK, 6, a))
                c.drawRect(skia.Rect.MakeXYWH(-50, -128, 100, 34), K.paint("#9FD3F0", 0.8 * a))
                K.text(c, s, 0, 10, 60, "hand", BLACK, a)
            return None
        return fn
    sfx = {0: "pop", 1: "pop", 2: "pop"}
    seen = set()
    for s, dx, dy, rot, k in notes:
        b.custom(j, k, k + 0.3, card(s, cx + dx, cy + dy, rot, k, s == "回电话"),
                 sfx=None if k in seen else sfx[k], gain=0.7)
        seen.add(k)

    def gust(c, kk, T):
        dt = T - H.tb(j, 3)
        if 0 <= dt < 0.8:
            a = 1 - dt / 0.8
            for i in range(3):
                yy = cy - 230 + i * 50
                c.drawLine(cx + 40 + dt * 300, yy, cx + 260 + dt * 400, yy - 40, wb.marker(BLUE, 6, a))
        return None
    b.custom(j, 3, 3.8, gust, sfx="shaker", gain=0.7)
    _finish(H, j, cx, cy, "又漏了一件", acc, ty=cy + 250, text_sfx="kick")


# ---------------------------------------------------------------- 07 现地现物：门牌翻到“第3次会”

def doorsign(H, j, cx, cy, acc):
    b = H.b
    dx, dy = cx, cy - 300
    door = join(rect(dx, dy, 520, 700, 14), circle(dx + 190, dy + 40, 18), P((dx - 300, dy + 350), (dx + 300, dy + 350)))
    b.path(j, 0, 0.7, door, BLACK, 9, sfx="wood_low")
    signs = ["第1次会", "第2次会", "第3次会"]
    H.note(*signs, "会议中")

    def fn(c, kk, T):
        idx, sy = 0, 1.0
        for k in (1, 2):
            t0 = H.tb(j, k)
            if T >= t0:
                f = clamp01((T - t0) / 0.28)
                if f < 0.5:
                    sy, idx = 1 - 2 * f, k - 1
                else:
                    sy, idx = 2 * f - 1, k
        last = H.tb(j, 2) if T > H.tb(j, 2) else H.tb(j, 1)
        sw = wobble(T - last - 0.28, 4, 14, 4)
        x, y = dx, dy - 150
        c.drawLine(x - 80, y - 120, x, y - 200, wb.marker(BLACK, 5))
        c.drawLine(x + 80, y - 120, x, y - 200, wb.marker(BLACK, 5))
        c.drawCircle(x, y - 200, 8, K.paint(BLACK))
        with K.at(c, x, y, sw, 1.0, max(0.02, sy)):
            c.drawRoundRect(skia.Rect.MakeXYWH(-190, -80, 380, 160), 14, 14, K.paint("#FFFFFF"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-190, -80, 380, 160), 14, 14, wb.marker(RED if idx == 2 else BLACK, 8))
            K.text(c, signs[idx], 0, 0, 74, "hand", RED if idx == 2 else BLACK)
        return None
    b.custom(j, 0.6, 0.9, fn)
    b.hit(j, 1, "wood_high", 0.8, "翻牌：第2次会")
    b.hit(j, 2, "rim", 0.8, "翻牌：第3次会")
    b.custom(j, 3, 3.3, _pop(H, j, 3, "会议中", dx, dy + 120, 56, GRAY, "sans_medium"))
    _finish(H, j, cx, cy, "问题还在", acc, ty=cy + 260)


# ---------------------------------------------------------------- 08 五问：打下去一个，又冒出一个

def mole(H, j, cx, cy, acc):
    b = H.b
    hy = cy - 60
    xs = [cx - 370, cx, cx + 370]
    holes = []
    for x in xs:
        o = skia.Path()
        o.addOval(skia.Rect.MakeXYWH(x - 160, hy - 40, 320, 80))
        holes.append(o)
    b.path(j, 0, 0.6, join(*holes), BLACK, 9, sfx="wood_low")
    H.note("问题")
    ups = [(0, 1, 2), (2, 2, 3), (1, 3, 99)]          # (洞, 冒头拍, 被打/缩回拍)

    def fn(c, kk, T):
        for hole, ku, kd in ups:
            tu, td = H.tb(j, ku), H.tb(j, kd) if kd < 99 else 1e9
            if T < tu:
                continue
            up = ease_out_back(clamp01((T - tu) / 0.25))
            if T > td:
                up *= 1 - ease_in_out(clamp01((T - td) / 0.18))
            if up <= 0.01:
                continue
            x = xs[hole]
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(x - 220, hy - 700, x + 220, hy))
            yy = hy + 60 - 330 * up
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 125, yy - 160, 250, 400), 120, 120, K.paint("#D9B38C"))
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 125, yy - 160, 250, 400), 120, 120, wb.marker(BLACK, 9))
            for ex in (-42, 42):
                c.drawCircle(x + ex, yy - 70, 12, K.paint(BLACK))
            c.drawCircle(x, yy - 30, 18, K.paint(BLACK))
            K.text(c, "问题", x, yy + 70, 66, "hand", RED)
            c.restore()
        c.drawPath(join(*holes), wb.marker(BLACK, 9))
        # 锤子：第 2 拍砸左边的洞
        t2 = H.tb(j, 2)
        if T > t2 - 0.3:
            f = clamp01((T - (t2 - 0.3)) / 0.3)
            ang = lerp(-60, 10, ease_in_out(f)) if T < t2 else 10 - 10 * ease_out(clamp01((T - t2) / 0.4))
            a = 1 - clamp01((T - t2 - 0.9) / 0.3)
            px, py = xs[0] + 300, hy - 90
            with K.at(c, px, py, ang):
                c.drawRoundRect(skia.Rect.MakeXYWH(-300, -16, 300, 32), 10, 10, K.paint("#C89B63", a))
                c.drawRoundRect(skia.Rect.MakeXYWH(-300, -16, 300, 32), 10, 10, wb.marker(BLACK, 6, a))
                c.drawRoundRect(skia.Rect.MakeXYWH(-360, -70, 120, 140), 16, 16, K.paint(RED, a))
                c.drawRoundRect(skia.Rect.MakeXYWH(-360, -70, 120, 140), 16, 16, wb.marker(BLACK, 7, a))
            if T > t2 and T - t2 < 0.4:
                K.burst(c, xs[0], hy - 160, T - t2, ORANGE, 50, 190, 8, 8, 0.9)
        return None
    b.custom(j, 0.6, 0.9, fn)
    b.hit(j, 1, "bongo_high", 0.8, "左边冒头")
    b.hit(j, 2, "rim", 0.9, "锤子砸下 + 右边冒头")
    b.custom(j, 3, 3.3, lambda c, k, T: None, sfx="bongo_low", gain=0.8)
    _finish(H, j, cx, cy, "又冒出来了", acc, size=136, ty=cy + 220)


# ---------------------------------------------------------------- 09 共识：方案被盖“否”

def reject(H, j, cx, cy, acc):
    b = H.b
    x, y = cx, cy - 330
    chart = join(P((x - 120, y + 120), (x - 120, y + 20)), P((x - 40, y + 120), (x - 40, y - 30)),
                 P((x + 40, y + 120), (x + 40, y + 50)), P((x + 120, y + 120), (x + 120, y - 70)))
    b.path(j, 0, 0.6, join(rect(x, y, 440, 560, 18), P((x - 160, y + 150), (x + 170, y + 150))), BLACK, 9,
           sfx="wood_high")
    b.text(j, 0.3, 0.7, "方案", x, y - 200, 76, BLACK)
    b.path(j, 0.6, 1.0, chart, BLUE, 16)
    H.note("挺好？")

    def heads(c, kk, T):
        for i, hx in enumerate((cx - 380, cx + 380)):
            sc = pop_scale(T - H.tb(j, 1) - i * 0.08)
            if sc <= 0:
                continue
            with K.at(c, hx, y + 60, 0, sc):
                c.drawCircle(0, 0, 70, K.paint("#FFFFFF"))
                c.drawCircle(0, 0, 70, wb.marker(BLACK, 8))
                for ex in (-24, 24):
                    c.drawCircle(ex, -10, 7, K.paint(BLACK))
                frown = T > H.tb(j, 2)
                m = skia.Path()
                if frown:
                    m.addArc(skia.Rect.MakeXYWH(-26, 22, 52, 32), 200, 140)
                else:
                    m.moveTo(-22, 30)
                    m.lineTo(22, 30)
                c.drawPath(m, wb.marker(BLACK, 6))
                c.drawLine(-60, 130, 60, 130, wb.marker(BLACK, 8))
                c.drawLine(0, 70, 0, 130, wb.marker(BLACK, 8))
        return None
    b.custom(j, 1, 1.3, heads, sfx="pop", gain=0.7)
    b.custom(j, 1.4, 1.7, _pop(H, j, 1.4, "挺好？", cx - 380, y - 70, 56, GRAY))
    b.custom(j, 2, 2.3, _stamp(H, j, 2, "否", x + 20, y + 10, 210, -12), sfx="kick", gain=0.8)
    b.shots[j].shake = [(2, 9.0)]
    b.custom(j, 3, 3.3, _big(H, j, 3, "一开会就被否", cx, cy + 250, 112, acc), sfx="rim", gain=0.8)
    b.custom(j, 4, 4.3, _label(H, j, 4, cx, cy + 425), sfx="pop", gain=0.55)


# ---------------------------------------------------------------- 10 反省：跑步机上原地跑

def treadmill(H, j, cx, cy, acc):
    b = H.b
    by = cy + 20
    frame = join(P((cx - 420, by), (cx + 380, by)), P((cx - 420, by + 50), (cx + 380, by + 50)),
                 circle(cx - 420, by + 25, 25), circle(cx + 380, by + 25, 25),
                 P((cx + 330, by), (cx + 430, by - 520)), P((cx + 370, by - 520), (cx + 500, by - 520)))
    b.path(j, 0, 0.6, frame, BLACK, 9, sfx="wood_low")
    H.note("0米")

    def fn(c, kk, T):
        t1 = H.tb(j, 1)
        ph = max(0.0, T - t1) * 2.6
        # 履带上的刻线往后走
        for i in range(9):
            u = ((i / 9) - ph * 0.35) % 1
            xx = cx - 400 + u * 760
            c.drawLine(xx, by + 8, xx - 20, by + 42, wb.marker(BLACK, 4, 0.7))
        sc = pop_scale(T - t1)
        if sc <= 0:
            return None
        s = 1.0
        x, y0 = cx - 40, by - 6
        c.save()
        c.translate(x, y0)
        c.scale(1.3, 1.3)
        c.translate(-x, -y0)
        bob = -abs(math.sin(ph * math.pi)) * 22
        hy = y0 - 300 * s + bob
        hip = (x, y0 - 130 * s + bob)
        sw = math.sin(ph * math.pi)
        with K.at(c, x, y0, 0, sc):
            c.translate(-x, -y0)
            c.drawCircle(x + 14, hy, 44 * s, K.paint("#FFFFFF"))
            c.drawCircle(x + 14, hy, 44 * s, wb.marker(BLACK, 9))
            c.drawPath(P((x - 30, hy - 10), (x - 10, hy - 50), (x + 40, hy - 48), (x + 58, hy - 5)), wb.marker(BLACK, 7))
            for ex in (2, 30):
                c.drawCircle(x + ex, hy - 4, 4, K.paint(BLACK))
            c.drawLine(x + 2, hy + 22, x + 28, hy + 22, wb.marker(BLACK, 6))
            sh = (x + 6, hy + 75)
            c.drawLine(x + 10, hy + 44, hip[0], hip[1], wb.marker(BLACK, 10))
            for sg in (1, -1):
                k_ = sg * sw
                knee = (hip[0] + 55 * k_, hip[1] + 70)
                foot = (hip[0] + 95 * k_ - 20, y0 - 8 - 30 * max(0.0, -k_))
                c.drawPath(P(hip, knee, foot), wb.marker(BLACK, 10))
                elbow = (sh[0] - 50 * k_, sh[1] + 50)
                hand = (sh[0] - 20 * k_ + 30, sh[1] + 20)
                c.drawPath(P(sh, elbow, hand), wb.marker(BLACK, 10))
            t2 = H.tb(j, 2)
            if T > t2:
                for i, (dx_, dy_) in enumerate(((-70, -40), (80, -70))):
                    f = ((T - t2) * 1.4 + i * 0.5) % 1
                    c.drawCircle(x + 14 + dx_ * (1 + f * 0.4), hy + dy_ + f * 60, 10, K.paint(BLUE, 1 - f))
        c.restore()
        return None
    b.custom(j, 1, 1.3, fn, sfx="shaker", gain=0.6)

    def meter(c, kk, T):
        sc = pop_scale(T - H.tb(j, 2))
        if sc > 0:
            with K.at(c, cx + 430, by - 610, 6, sc):
                c.drawRoundRect(skia.Rect.MakeXYWH(-120, -60, 240, 120), 16, 16, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-120, -60, 240, 120), 16, 16, wb.marker(BLACK, 7))
                K.text(c, "0米", 0, 0, 76, "hand", RED)
        return None
    b.custom(j, 2, 2.3, meter, sfx="ding", gain=0.7)
    _finish(H, j, cx, cy, "忙了一天 还在原地", acc, size=104, ty=cy + 250)


# ---------------------------------------------------------------- 旧版：丰田模式四字（留作对照）

def title(H, j, cx, cy, acc):
    raise NotImplementedError("旧版四字开场在 common.Lesson.intro_title")


HOOKS = dict(stamp3=stamp3, pile=pile, curve=curve, bars=bars, checklist=checklist, sticky=sticky, doorsign=doorsign,
             mole=mole, reject=reject, treadmill=treadmill)
