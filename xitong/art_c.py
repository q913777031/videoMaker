"""《系统之美》05–07 讲专用元件：动态曲线（振荡 / S 形 / 指数）、淋浴水温、经销商车场、延迟链、
增强与调节回路、木桶限制因素、草场与牛群、公司冰箱。坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_out, lerp
from maoxuan.art_d import cow as _cow
from zizhi.art import car as _car

GRASS = "#9DB06A"
HOT = "#D9593A"
COLD = "#4F86B8"


# ---------------------------------------------------------------- 动态曲线

def _f(kind, u):
    if kind == "osc":                       # 围绕目标线衰减振荡
        return 0.5 - 0.38 * math.exp(-2.2 * u) * math.cos(u * 4.2 * math.pi)
    if kind == "osc_big":                   # 反应更快：振荡更猛、更久
        return 0.5 - 0.42 * math.exp(-0.6 * u) * math.cos(u * 5.0 * math.pi)
    if kind == "smooth":                    # 等一等、看趋势：平稳逼近目标
        return 0.5 - 0.38 * math.exp(-4.5 * u)
    if kind == "s":                         # 有限环境中的增长：S 形
        return 0.1 + 0.72 / (1 + math.exp(-11 * (u - 0.42)))
    if kind == "exp":                       # 只看前半段：指数一样往上冲
        return 0.1 + 0.8 * (math.exp(2.6 * u) - 1) / (math.exp(2.6) - 1)
    if kind == "s_exp":                     # 预期的指数（虚线）与实际的 S 形
        return 0.1 + 0.72 / (1 + math.exp(-11 * (u - 0.42)))
    if kind == "fall":                      # 资源被耗尽
        return 0.85 - 0.75 * (1 - math.exp(-3 * u)) / (1 - math.exp(-3))
    return u


def curve(c, g, el_t, d):
    """坐标轴 + 曲线：shape 见 _f；曲线在 b0→b1 拍间画出，笔尖带圆点；target 不为空时画一条目标虚线并标注；
    ghost=True 时先画一条预期的指数虚线（s_exp 用）。"""
    w, h = d.get("w", 820), d.get("h", 480)
    kind = d.get("shape", "osc")
    K.seg(c, -w / 2, h / 2, w / 2 + 20, h / 2, K.INK2, 6)
    K.seg(c, -w / 2, h / 2, -w / 2, -h / 2 - 20, K.INK2, 6)
    if d.get("ylab"):
        K.text(c, d["ylab"], -w / 2 + 14, -h / 2 - 50, 36, "bold", K.INK2, 1, "left")
    if d.get("xlab"):
        K.text(c, d["xlab"], w / 2 - 10, h / 2 + 46, 34, "bold", K.INK3, 1, "right")
    if d.get("target"):
        y = h / 2 - 0.5 * h
        for i in range(16):
            x0 = -w / 2 + i * w / 16
            K.seg(c, x0, y, x0 + w / 32, y, K.GREEN, 5, 0.9)
        K.pill(c, w / 2 - 70, y - 44, d["target"], 32, K.GREEN, K.PAPER)
    if d.get("ghost") or kind == "s_exp":
        q = skia.Path()
        for i in range(61):
            u = i / 60
            yy = _f("exp", u)
            (q.moveTo if i == 0 else q.lineTo)(-w / 2 + u * w, h / 2 - yy * h)
        a = clamp01(g.since(d.get("ghost_at", 0)) / 0.4)
        p_ = K.paint(K.INK3, 0.7 * a, 6)
        p_.setPathEffect(skia.DashPathEffect.Make([18, 14], 0))
        c.drawPath(q, p_)
    k = g.span(d.get("b0", 0), d.get("b1", 3), ease=lambda x: x)
    if k <= 0:
        return
    n = max(2, int(120 * k))
    p = skia.Path()
    for i in range(n + 1):
        u = k * i / n
        (p.moveTo if i == 0 else p.lineTo)(-w / 2 + u * w, h / 2 - _f(kind, u) * h)
    col = d.get("color") or g.acc
    c.drawPath(p, K.paint(col, 0.35, 22, blur=6))
    c.drawPath(p, K.paint(col, 1, 10))
    x, y = -w / 2 + k * w, h / 2 - _f(kind, k) * h
    K.dot(c, x, y, 18, col)
    K.dot(c, x, y, 8, K.PAPER)
    for lab, u, dy in d.get("marks", ()):
        if k >= u:
            st = fx.word_pop((k - u) * 3)
            if st:
                a, s_, _ = st
                with K.at(c, -w / 2 + u * w, h / 2 - _f(kind, u) * h + dy, 0, s_):
                    K.pill(c, 0, 0, lab, 34, K.INK, K.PAPER, a)


# ---------------------------------------------------------------- 淋浴水温

def shower(c, g, el_t, d):
    """淋浴：喷头、水流颜色随水温冷热摆动，温度计指针摆动；mode="calm" 时水温平稳停在合适处。"""
    mode = d.get("mode", "osc")
    t = max(0.0, g.since(d.get("b0", 0)))
    if mode == "osc":
        temp = 0.5 + 0.42 * math.sin(t * 3.4)
    else:
        temp = 0.5 + 0.35 * math.exp(-1.6 * t) * math.cos(t * 1.4)
    K.seg(c, -120, -380, -120, -260, K.INK2, 14)
    K.seg(c, -120, -380, 40, -380, K.INK2, 14)
    K.rr(c, 60, -360, 120, 40, 14, K.INK2)
    col = K.mix(COLD, HOT, temp)
    for i in range(9):
        x0 = 20 + i * 10
        ph = (g.t * 2.2 + i * 0.37) % 1.0
        for j in range(4):
            y = -330 + ((ph + j * 0.25) % 1.0) * 380
            K.seg(c, x0 + (i - 4) * 4 * (y + 330) / 380, y, x0 + (i - 4) * 4 * (y + 330) / 380, y + 34, col, 6, 0.75)
    # 温度计
    tx, ty = 330, -40
    K.rr(c, tx, ty, 70, 440, 35, K.PAPER)
    K.rr_stroke(c, tx, ty, 70, 440, 35, K.INK2, 5)
    hh = 380 * temp
    K.rr(c, tx, ty + 190 - hh / 2, 34, hh, 17, col)
    K.dot(c, tx, ty + 220, 40, col)
    K.text(c, "烫", tx - 80, ty - 170, 40, "bold", HOT)
    K.text(c, "冷", tx - 80, ty + 170, 40, "bold", COLD)
    # 旋钮
    with K.at(c, -280, -60, (temp - 0.5) * 220):
        K.dot(c, 0, 0, 70, K.PAPER)
        K.ring(c, 0, 0, 70, K.INK2, 8)
        K.seg(c, 0, 0, 0, -58, K.RED, 12)


# ---------------------------------------------------------------- 经销商车场

def lot(c, g, el_t, d):
    """经销商车场：车位 4×3；keys [(拍, 车数)] 之间车数逐拍变化；truck 拍起一辆运车卡车从右驶入。"""
    keys = d.get("keys", [(0, 6)])
    n = keys[0][1]
    for b, v in keys:
        if g.since(b) >= 0:
            n = v
    sc = d.get("scale", 1.0)
    c.save()
    c.scale(sc, sc)
    _lot(c, g, d, n)
    c.restore()


def _lot(c, g, d, n):
    K.rr(c, 0, 20, 820, 470, 16, "#D8CDB8")
    K.text(c, d.get("title", "车场库存"), 0, -270, 44, "serif_black", K.INK)
    for i in range(12):
        x = -300 + (i % 4) * 200
        y = -120 + (i // 4) * 140
        K.rr_stroke(c, x, y, 170, 110, 8, K.PAPER, 4, 0.8)
        if i < n:
            _car(c, x, y + 6, 140, 1, ("#3D6E92", "#B8322A", "#5E9A6A", "#C99A3A")[i % 4])
    if n > 12:
        K.pill(c, 330, -270, "停不下了", 34, K.RED, K.PAPER)
    if d.get("label"):
        K.pill(c, 0, 300, d["label"], 38, g.acc, K.PAPER)


# ---------------------------------------------------------------- 延迟链

def delay_chain(c, g, el_t, d):
    """三段延迟：labels 三个方框从左到右，b0 起每 step 拍亮起一个，方框之间的沙漏转动。"""
    labels = d.get("labels", ("看到变化", "做出决定", "货才到"))
    b0, step = d.get("b0", 0), d.get("step", 1)
    for i, lab in enumerate(labels):
        x, y = -300 + i * 300, (i % 2) * 40 - 20
        on = g.since(b0 + i * step) >= 0
        st = fx.word_pop(g.since(b0 + i * step))
        s_ = st[1] if st else 1.0
        with K.at(c, x, y, 0, s_ if on else 1.0):
            K.card(c, 0, 0, 230, 130, g.acc if on else K.PAPER, 1, r=18)
            K.text(c, lab, 0, 0, 40, "serif_black", K.PAPER if on else K.INK3)
        if i < len(labels) - 1:
            hx = x + 150
            a = 1.0 if on else 0.4
            with K.at(c, hx, y + 20 - (i % 2) * 40 + 20, (g.t * 120) % 180 if on else 0):
                K.poly(c, [(-22, -30), (22, -30), (0, 0)], K.GOLD, a)
                K.poly(c, [(-22, 30), (22, 30), (0, 0)], K.GOLD, a)
                K.seg(c, -26, -32, 26, -32, K.INK2, 5, a)
                K.seg(c, -26, 32, 26, 32, K.INK2, 5, a)


# ---------------------------------------------------------------- 增强与调节回路

def _loop(c, x, y, r, col, label, t, sign, a=1.0):
    K.ring(c, x, y, r, col, 12, a)
    ang = t * 2.0 * sign
    hx, hy = x + r * math.cos(ang), y + r * math.sin(ang)
    with K.at(c, hx, hy, math.degrees(ang) + (90 if sign > 0 else -90)):
        K.poly(c, [(-22, -16), (22, 0), (-22, 16)], col, a)
    K.text(c, label, x, y, 54, "serif_black", col, a)


def loops(c, g, el_t, d):
    """左侧增强回路（R，越转越大）；b 拍起右侧调节回路（B）出现并把总量压住；labels 为两回路名称。"""
    la, lb = d.get("labels", ("增长", "极限"))
    ka = clamp01(g.since(d.get("a", 0)) / 0.4)
    if ka > 0:
        grow = 1 + 0.12 * math.sin(g.t * 3)
        _loop(c, -220, 0, 150 * ka * grow, g.acc, la, g.t, 1, ka)
        K.text(c, "增强", -220, -220, 36, "bold", g.acc, ka)
    kb = clamp01(g.since(d.get("b", 2)) / 0.4)
    if kb > 0:
        _loop(c, 220, 0, 150 * kb, K.INK2, lb, g.t, -1, kb)
        K.text(c, "调节", 220, -220, 36, "bold", K.INK2, kb)
        K.arrow(c, (-60, 0), (60, 0), K.INK, 8, kb, 1, 0, 26)


# ---------------------------------------------------------------- 木桶：限制因素

def staves(c, g, el_t, d):
    """木桶：items [(名称, 高度 0..1)] 为桶板；水位等于最短那块；raise=(拍, 序号, 新高度) 时那块被补长，水位上涨到新的最短板。"""
    items = [list(x) for x in d["items"]]
    rz = d.get("raise")
    k = 0.0
    if rz:
        k = ease_out(clamp01(g.since(rz[0]) / 0.5))
        items[rz[1]][1] = lerp(items[rz[1]][1], rz[2], k)
    n = len(items)
    bw, H = 120, 520
    x0 = -n * bw / 2 + bw / 2
    level = min(h for _, h in items)
    low = min(range(n), key=lambda i: items[i][1])
    for i, (name, h) in enumerate(items):
        x = x0 + i * bw
        hh = h * H
        is_low = i == low and d.get("mark", True)
        col = K.RED if is_low else "#B58A5A"
        K.rr(c, x, H / 2 - hh / 2 + 10, bw - 14, hh, 8, col, 0.95)
        K.rr_stroke(c, x, H / 2 - hh / 2 + 10, bw - 14, hh, 8, K.shade(col, 0.35), 3)
        K.text(c, name, x, H / 2 - hh + 60, 34, "serif_black", K.PAPER)
    K.rr(c, 0, H / 2 - level * H / 2 + 10, n * bw - 24, level * H, 8, "#5B8DB8", 0.55)
    wy = H / 2 - level * H + 10
    K.seg(c, -n * bw / 2 + 12, wy, n * bw / 2 - 12, wy, "#2F5F8A", 6, 0.9)
    K.text(c, "水位", n * bw / 2 + 60, wy, 32, "bold", "#2F5F8A")
    K.seg(c, -n * bw / 2, H / 2 + 14, n * bw / 2, H / 2 + 14, K.INK2, 8)
    if d.get("tag"):
        lx = x0 + low * bw
        K.pill(c, lx, H / 2 - items[low][1] * H - 60, d["tag"], 34, K.RED, K.PAPER)


# ---------------------------------------------------------------- 草场与牛群

def pasture(c, g, el_t, d):
    """公共草场：herd keys [(拍, 牛数)] 逐拍加牛；草的密度随牛数下降（草从绿变黄、变稀）；cap 为草场能承受的牛数。"""
    keys = d.get("keys", [(0, 3)])
    n = keys[0][1]
    for b, v in keys:
        if g.since(b) >= 0:
            n = v
    cap = d.get("cap", 6)
    health = clamp01(1.15 - n / (cap * 1.6))
    K.rr(c, 0, 120, 960, 300, 140, K.mix("#C9B37A", GRASS, health), 0.9)
    for i in range(int(14 + 30 * health)):
        gx = -440 + (i * 97) % 880
        gy = 40 + (i * 53) % 160
        K.seg(c, gx, gy, gx - 6, gy - 30, K.shade(GRASS, 0.3), 5, 0.8)
        K.seg(c, gx, gy, gx + 8, gy - 26, K.shade(GRASS, 0.3), 5, 0.8)
    for i in range(n):
        x = -360 + (i % 6) * 145 + (i // 6) * 60
        y = 170 + (i // 6) * -110
        with K.at(c, x, y, 0, 1):
            _cow(c, g, el_t, dict(s=150, face=1 if i % 2 else -1))
    if d.get("label"):
        K.pill(c, 0, -60, d["label"], 38, g.acc, K.PAPER)


# ---------------------------------------------------------------- 公司冰箱

def fridge(c, g, el_t, d):
    """敞开的冰箱：items 从 b0 起每 step 拍塞进去一件；mess=True 时东西东倒西歪、有过期标记；
    names=True 时每层贴上名字标签；rule 拍起门上贴一张“规则”便签。"""
    W_, H_ = 520, 700
    K.rr(c, 0, 0, W_, H_, 24, "#E9EEF1")
    K.rr_stroke(c, 0, 0, W_, H_, 24, K.INK2, 6)
    K.rr(c, -W_ / 2 - 120, 0, 220, H_ - 20, 18, "#DDE5EA")
    K.rr_stroke(c, -W_ / 2 - 120, 0, 220, H_ - 20, 18, K.INK2, 5)
    for j in range(3):
        K.seg(c, -W_ / 2 + 20, -130 + j * 200, W_ / 2 - 20, -130 + j * 200, K.INK3, 6)
    items = d.get("items", ())
    mess = d.get("mess", False)
    b0, step = d.get("b0", 0), d.get("step", 0.5)
    cols = ("#D9593A", "#E3A33B", "#5E9A6A", "#4F86B8", "#9C6B45", "#C77F86")
    for i, it in enumerate(items):
        dt = g.since(b0 + i * step)
        if dt < 0:
            continue
        k = ease_out(clamp01(dt / 0.25))
        shelf = i % 3
        x = -180 + (i // 3) * 120 + (25 if mess and i % 2 else 0)
        y = -175 + shelf * 200 - 30
        rot = (14 if i % 2 else -18) if mess else 0
        with K.at(c, x, lerp(y - 120, y, k), rot):
            K.rr(c, 0, 0, 90, 80, 12, cols[i % len(cols)])
            K.text(c, it, 0, 0, 30, "bold", K.PAPER)
            if mess and i % 3 == 2:
                K.pill(c, 0, -60, "过期", 26, K.INK, K.PAPER)
    if d.get("names"):
        for j, nm in enumerate(d["names"]):
            st = fx.word_pop(g.since(d.get("names_at", 0) + j * 0.5))
            if st:
                a, s_, _ = st
                with K.at(c, W_ / 2 - 70, -110 + j * 200, 0, s_):
                    K.pill(c, 0, 0, nm, 30, g.acc, K.PAPER, a)
    st = fx.word_pop(g.since(d.get("rule", 99)))
    if st:
        a, s_, _ = st
        with K.at(c, -W_ / 2 - 120, -120, -4, s_):
            K.rr(c, 0, 0, 190, 220, 8, "#FFF1A8", a)
            K.text(c, "冰箱规则", 0, -70, 34, "serif_black", K.INK, a)
            for j in range(3):
                K.rr(c, 0, -10 + j * 50, 140, 12, 6, K.INK3, a)


# ---------------------------------------------------------------- 推不动的大石头

def rock(c, g, el_t, d):
    """一块水墨大石：label 写在石上；shake 拍起轻微抖动（推不动）。"""
    s = d.get("s", 300)
    j = math.sin(g.t * 40) * 3 if g.since(d.get("shake", 99)) >= 0 else 0
    p = skia.Path()
    pts = [(-0.55, 0.0), (-0.6, -0.45), (-0.3, -0.8), (0.15, -0.85), (0.5, -0.6), (0.6, -0.15), (0.5, 0.0)]
    p.moveTo(pts[0][0] * s + j, pts[0][1] * s)
    for x, y in pts[1:]:
        p.lineTo(x * s + j, y * s)
    p.close()
    c.drawPath(p, K.paint("#8E8A80"))
    c.drawPath(p, K.paint(K.INK, 0.6, 6))
    K.seg(c, -0.2 * s + j, -0.6 * s, 0.05 * s + j, -0.4 * s, K.INK, 4, 0.5)
    if d.get("label"):
        K.text(c, d["label"], j, -0.42 * s, s * 0.2, "serif_black", K.PAPER)


# ---------------------------------------------------------------- 油田

def derrick(c, g, el_t, d):
    """油田：井架 + 抽油机点头；左侧地下储量条从 b0 到 b1 拍间下降，抽油越来越慢。"""
    k = g.span(d.get("b0", 0), d.get("b1", 3))
    for (x0, y0, x1, y1) in ((-60, 200, 0, -260), (60, 200, 0, -260), (-40, 80, 40, 80), (-25, -40, 25, -40)):
        K.seg(c, x0, y0, x1, y1, K.INK2, 10)
    speed = lerp(5.0, 1.2, k)
    ang = math.sin(g.t * speed) * 16
    with K.at(c, 200, 40, ang):
        K.rr(c, 0, 0, 260, 30, 10, K.INK2)
        K.rr(c, 120, 20, 40, 70, 10, K.INK2)
    K.rr(c, 200, 140, 30, 200, 6, K.INK3)
    K.seg(c, -460, 200, 460, 200, K.INK2, 8)
    left = 1 - 0.8 * k
    K.rr(c, -330, 200 + 130, 160, 220, 16, "#D8CDB8")
    K.rr(c, -330, 200 + 130 + 110 - left * 110, 140, left * 210, 12, "#3B3A36")
    K.text(c, "储量", -330, 470, 36, "bold", K.INK2)


# ---------------------------------------------------------------- 渔场

def fishery(c, g, el_t, d):
    """渔场：海面上船数按 boats [(拍, 船数)] 增加，水下鱼数按 fish [(拍, 鱼数)] 减少。"""
    def at(keys):
        v = keys[0][1]
        for b, n in keys:
            if g.since(b) >= 0:
                v = n
        return v

    nb, nf = at(d.get("boats", [(0, 1)])), at(d.get("fish", [(0, 12)]))
    K.rr(c, 0, 130, 960, 420, 30, "#9CC0D8", 0.85)
    for i in range(5):
        y = -70 + i * 6
        K.seg(c, -460, y + math.sin(g.t * 2 + i) * 4, 460, y + math.sin(g.t * 2 + i) * 4, "#6FA0C6", 3, 0.5)
    for i in range(nb):
        x = -360 + i * 150
        bob = math.sin(g.t * 2.4 + i) * 6
        K.poly(c, [(x - 60, -90 + bob), (x + 60, -90 + bob), (x + 40, -55 + bob), (x - 40, -55 + bob)], "#8A5A35")
        K.seg(c, x, -90 + bob, x, -190 + bob, K.INK2, 5)
        K.poly(c, [(x + 4, -185 + bob), (x + 50, -120 + bob), (x + 4, -120 + bob)], "#F3EBDA")
    for i in range(nf):
        fx_ = -380 + (i * 137) % 760 + math.sin(g.t * 1.5 + i) * 20
        fy = 40 + (i * 71) % 260
        f = 1 if i % 2 else -1
        with K.at(c, fx_, fy):
            c.drawOval(skia.Rect.MakeXYWH(-30, -14, 60, 28), K.paint("#E3A33B"))
            K.poly(c, [(-30 * f, 0), (-52 * f, -16), (-52 * f, 16)], "#E3A33B")
            K.dot(c, 16 * f, -4, 4, K.INK)
