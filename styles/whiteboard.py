"""白板手绘过程：一块 3240×5760 的大白板，一只手握马克笔实时描线写字，相机在白板上平移缩放，
8 个小节依次画在白板不同位置并用箭头连成思维导图，最后一小节拉远露出整张全景。

用法：python3 -m styles.whiteboard [--stills]   → out/styles/whiteboard.mp4
"""

import math

import skia

from adler import kit as K
from engine import gfx
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from styles import seg

gfx.FONT_FILES.setdefault("hand", "MaShanZheng-Regular.ttf")

BW, BH = 3240, 5760
BLACK = "#1E1E24"
RED = "#D23A2E"
BLUE = "#2F62B8"
GREEN = "#2E8A57"

# 每小节的白板区域中心与相机缩放
VIEWS = [(800, 900, 1.0), (2400, 900, 1.0), (800, 2150, 1.0), (2400, 2150, 1.0),
         (1620, 3300, 0.82), (900, 4450, 1.0), (1500, 4450, 0.95), (1620, 5250, 1.0)]
FULL = (BW / 2, BH / 2, 1080 / BW)


def tb(i: int, k: float) -> float:
    """第 i 小节第 k 拍（可小数、可为负或超过 4，超出部分按平均拍长外推）的本地时刻。"""
    b = seg.BARS[i]
    beat = (b["t1"] - b["beats"][0]) / 4
    if k < 0:
        return b["beats"][0] + k * beat
    if k >= 4:
        return b["t1"] + (k - 4) * beat
    return -seg.since(b, k, 0.0)


# ---------------------------------------------------------------- 图元（板上坐标）

def P(*pts, close=False) -> skia.Path:
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def circle(x, y, r) -> skia.Path:
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def join(*paths) -> skia.Path:
    out = skia.Path()
    for p in paths:
        out.addPath(p)
    return out


def stick(x, y, s=1.0, arms="down", tie=False) -> skia.Path:
    """简笔小人：(x, y) 为脚底，身高约 330·s。"""
    hy = y - 290 * s
    body = P((x, hy + 45 * s), (x, y - 120 * s))
    legs = P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y))
    if arms == "up":
        arm = P((x - 80 * s, hy - 40 * s), (x, hy + 80 * s), (x + 80 * s, hy - 40 * s))
    elif arms == "point":
        arm = join(P((x - 60 * s, hy + 150 * s), (x, hy + 80 * s)), P((x, hy + 80 * s), (x + 120 * s, hy + 60 * s)))
    else:
        arm = P((x - 70 * s, hy + 170 * s), (x, hy + 80 * s), (x + 70 * s, hy + 170 * s))
    parts = [circle(x, hy, 45 * s), body, arm, legs]
    if tie:
        parts.append(P((x, hy + 50 * s), (x - 12 * s, hy + 100 * s), (x, hy + 120 * s), (x + 12 * s, hy + 100 * s),
                       close=True))
    return join(*parts)


def smile(x, hy, s=1.0, mood="smile") -> skia.Path:
    p = skia.Path()
    p.addCircle(x - 15 * s, hy - 8 * s, 3 * s)
    p.addCircle(x + 15 * s, hy - 8 * s, 3 * s)
    if mood == "smile":
        p.addArc(skia.Rect.MakeXYWH(x - 20 * s, hy - 5 * s, 40 * s, 28 * s), 20, 140)
    else:
        p.addArc(skia.Rect.MakeXYWH(x - 18 * s, hy + 10 * s, 36 * s, 24 * s), 200, 140)
    return p


def bubble(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 40, 40)
    p.moveTo(x - w * 0.25, y + h / 2)
    p.lineTo(x - w * 0.38, y + h / 2 + 60)
    p.lineTo(x - w * 0.1, y + h / 2)
    return p


def arrow(a, b, bend=0.25) -> skia.Path:
    (x0, y0), (x1, y1) = a, b
    mx, my = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend
    p = skia.Path()
    p.moveTo(x0, y0)
    p.quadTo(mx, my, x1, y1)
    ang = math.atan2(y1 - my, x1 - mx)
    for d in (2.6, -2.6):
        p.moveTo(x1, y1)
        p.lineTo(x1 - 50 * math.cos(ang + d / 6), y1 - 50 * math.sin(ang + d / 6))
    return p


def scribble(x, y, w, h, n=7) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - w / 2, y - h / 2)
    for i in range(n):
        p.lineTo(x + w / 2 * (1 if i % 2 == 0 else -1), y - h / 2 + h * (i + 1) / n)
    return p


def wave(x0, x1, y, amp=16, step=40) -> skia.Path:
    p = skia.Path()
    p.moveTo(x0, y)
    x = x0
    k = 0
    while x < x1:
        p.quadTo(x + step / 2, y + (amp if k % 2 == 0 else -amp), x + step, y)
        x += step
        k += 1
    return p


def spring_path(x, top, length, w=150, coils=12) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - w / 2, top)
    for i in range(coils * 2):
        y = top + length * (i + 1) / (coils * 2)
        p.lineTo(x + (w / 2 if i % 2 == 0 else -w / 2), y)
    return p


def clock_face(x, y, r) -> skia.Path:
    p = circle(x, y, r)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        p.moveTo(x + math.cos(a) * r * 0.82, y + math.sin(a) * r * 0.82)
        p.lineTo(x + math.cos(a) * r * 0.92, y + math.sin(a) * r * 0.92)
    return p


def book(x, y, w=360, h=240) -> skia.Path:
    return join(P((x, y - h / 2 + 20), (x - w / 2, y - h / 2), (x - w / 2, y + h / 2), (x, y + h / 2 + 20),
                  (x + w / 2, y + h / 2), (x + w / 2, y - h / 2), (x, y - h / 2 + 20), (x, y + h / 2 + 20)),
                P((x - w / 2 + 40, y - h / 4), (x - 40, y - h / 4 + 12)), P((x - w / 2 + 40, y), (x - 40, y + 12)),
                P((x + 40, y - h / 4 + 12), (x + w / 2 - 40, y - h / 4)), P((x + 40, y + 12), (x + w / 2 - 40, y)))


# ---------------------------------------------------------------- 绘制项：(开始时刻, 结束时刻, 类型, 参数)

ITEMS = []


def add_path(i, k0, k1, path, color=BLACK, width=10):
    ITEMS.append(dict(t0=tb(i, k0), t1=tb(i, k1), kind="path", path=path, color=color, width=width))


def add_text(i, k0, k1, s, x, y, size, color=BLACK, font="hand"):
    ITEMS.append(dict(t0=tb(i, k0), t1=tb(i, k1), kind="text", s=s, x=x, y=y, size=size, color=color, font=font))


def add_custom(i, k0, k1, fn):
    ITEMS.append(dict(t0=tb(i, k0), t1=tb(i, k1), kind="custom", fn=fn))


def caption(i, k0, k1, s, cx, cy):
    add_text(i, k0, k1, s, cx, cy, 78, BLUE)


def _build():
    # 0 新领导 + 对话框
    x, y = 640, 1150
    add_path(0, 0.0, 0.85, stick(x, y, 1.1, "point", tie=True))
    add_path(0, 0.85, 1.0, smile(x, y - 290 * 1.1, 1.1))
    add_path(0, 1.0, 1.45, bubble(1050, 640, 560, 200))
    add_text(0, 1.45, 2.6, "咱们重新出发！", 1050, 640, 64)
    caption(0, 2.55, 3.6, "新部门来了新领导", 800, 1330)
    # 1 一排工位，划掉重画
    for n, dx in enumerate((-380, 0, 380)):
        X = 2400 + dx
        add_path(1, 0.0 + n * 0.25, 0.3 + n * 0.25, join(P((X - 130, 1010), (X + 130, 1010)), P((X - 110, 1010), (X - 110, 1120)),
                                                         P((X + 110, 1010), (X + 110, 1120))))
        add_path(1, 0.05 + n * 0.25, 0.3 + n * 0.25, stick(X - 20, 1000, 0.6))
        add_path(1, 1.0 + n * 0.25, 1.22 + n * 0.25, scribble(X - 20, 880, 160, 230), RED, 9)
        add_path(1, 2.0 + n * 0.25, 2.25 + n * 0.25, stick(X + 95, 1000, 0.6), BLUE, 9)
    caption(1, 2.85, 3.65, "团队也换了一半", 2400, 1330)
    # 2 三个欢呼的人
    for n, X in enumerate((520, 800, 1080)):
        add_path(2, n, n + 0.6, stick(X, 2380, 0.85, "up"))
        add_path(2, n + 0.6, n + 0.75, smile(X, 2380 - 290 * 0.85, 0.85))
    burst = skia.Path()
    for a in range(12):
        ang = a / 12 * 2 * math.pi
        burst.moveTo(800 + math.cos(ang) * 230, 1900 + math.sin(ang) * 120)
        burst.lineTo(800 + math.cos(ang) * 320, 1900 + math.sin(ang) * 170)
    add_path(2, 3.0, 3.25, burst, RED, 8)
    caption(2, 3.2, 3.75, "大家干劲十足", 800, 2560)
    # 3 时钟转过三个月
    add_path(3, 0.0, 0.8, clock_face(2400, 2080, 260))
    add_custom(3, 0.8, 4.0, "clock_hands")
    add_text(3, 2.0, 2.9, "三个月后……", 2400, 2470, 96, RED)
    add_path(3, 2.9, 3.3, P((2700, 1760), (2730, 1860)), RED, 12)
    # 4 drop：不是人的问题 / 是结构，框起来
    add_text(4, 0.0, 0.55, "不是人的问题", 1620, 3150, 150)
    add_text(4, 1.0, 1.45, "是结构", 1620, 3420, 230, RED)
    box = skia.Path()
    box.addRoundRect(skia.Rect.MakeXYWH(1620 - 640, 2960, 1280, 640), 50, 50)
    add_path(4, 2.0, 2.7, box, RED, 16)
    add_path(4, 2.7, 3.2, join(P((1620 - 560, 3640), (1620 + 560, 3655)), P((1620 - 520, 3672), (1620 + 520, 3684))),
             BLACK, 9)
    # 5 书与弹簧
    add_path(5, 0.0, 0.9, book(560, 4400))
    add_text(5, 0.9, 1.4, "系统之美", 560, 4400 - 200, 64, GREEN)
    add_custom(5, 1.6, 6.0, "spring")
    caption(5, 2.4, 3.6, "书一开头，拿出弹簧", 700, 4760)
    # 6 松手，弹簧自己弹
    add_text(6, 1.0, 1.3, "松手！", 1900, 4130, 90, RED)
    caption(6, 2.2, 3.55, "手一松，它自己弹", 1750, 4980)
    # 7 金句
    for n, w in enumerate(("行为", "藏在", "结构", "里")):
        X = 1100 + n * 330 - (60 if n >= 3 else 0)
        add_text(7, n * 0.95 if n < 3 else 2.9, n * 0.95 + 0.55 if n < 3 else 3.2, w, X, 5250, 170, RED if w == "结构" else BLACK)
    add_path(7, 2.5, 2.9, wave(1760 - 170, 1760 + 170, 5370), RED, 10)
    # 思维导图连线（相机转场时画）
    links = [((1150, 900), (2000, 900)), ((2400, 1420), (1100, 1850)), ((1100, 2150), (2050, 2150)),
             ((2300, 2600), (1800, 2940)), ((1400, 3700), (800, 4130)), ((1000, 4300), (1600, 4300)),
             ((1600, 4980), (1620, 5110))]
    for n, (a, b) in enumerate(links):
        add_path(n + 1, -0.02, 0.45, arrow(a, b, 0.15), GREEN, 8)


_build()


# ---------------------------------------------------------------- 绘制

def _partial(path: skia.Path, k: float):
    """取路径前 k 比例（按总长度），返回（部分路径，笔尖坐标）。"""
    pm = skia.PathMeasure(path, False)
    lens = []
    while True:
        lens.append(pm.getLength())
        if not pm.nextContour():
            break
    total = sum(lens)
    target = total * k
    out = skia.Path()
    tip = None
    pm = skia.PathMeasure(path, False)
    acc = 0.0
    for L in lens:
        if acc >= target:
            break
        take = min(L, target - acc)
        if L > 0:
            seg_ = skia.Path()
            pm.getSegment(0, take, seg_, True)
            out.addPath(seg_)
            pos, _ = pm.getPosTan(max(0.0, take))
            tip = (pos.x(), pos.y())
        acc += L
        pm.nextContour()
    return out, tip


def _marker(color, width, alpha=1.0):
    return K.paint(color, alpha, width)


def _spring(c, t):
    """弹簧：第 5 小节逐段画出，第 6 小节第 1 拍松手后衰减振荡。"""
    x, top = 1150, 4180
    rel = tb(6, 1.0)
    length = 380
    if t >= rel:
        dt = t - rel
        length = 380 + 220 * math.sin(dt * 9) * math.exp(-dt * 1.6)
        for j in range(3):
            yy = top + length + 40 + j * 26
            c.drawPath(P((x - 90 + j * 20, yy), (x + 90 - j * 20, yy)), _marker(BLUE, 5, 0.6 * math.exp(-dt * 1.5)))
    path = spring_path(x, top, length)
    it = next(i for i in ITEMS if i["kind"] == "custom" and i["fn"] == "spring")
    k = clamp01((t - it["t0"]) / (tb(5, 3.0) - it["t0"]))
    part, tip = _partial(path, k)
    c.drawPath(part, _marker(BLACK, 9))
    if t < rel:
        hand = join(P((x - 70, top - 10), (x + 70, top - 10)), circle(x, top - 70, 55))
        hk = clamp01((t - it["t0"]) / 0.3)
        c.drawPath(_partial(hand, hk)[0], _marker(BLACK, 9))
    else:
        c.drawPath(circle(x, top - 70 - 180 * ease_out(clamp01((t - rel) / 0.3)), 55), _marker(BLACK, 9, 0.35))
    return tip if k < 1 else None


def _clock_hands(c, t):
    it = next(i for i in ITEMS if i["kind"] == "custom" and i["fn"] == "clock_hands")
    k = clamp01((t - it["t0"]) / (tb(3, 2.0) - it["t0"]))
    spins = 6 * ease_in_out(k)
    a1 = -math.pi / 2 + spins * 2 * math.pi
    a2 = -math.pi / 2 + spins * 2 * math.pi / 12
    x, y = 2400, 2080
    c.drawPath(P((x, y), (x + math.cos(a1) * 200, y + math.sin(a1) * 200)), _marker(BLACK, 10))
    c.drawPath(P((x, y), (x + math.cos(a2) * 130, y + math.sin(a2) * 130)), _marker(RED, 14))
    K.dot(c, x, y, 14, BLACK)
    return None


def _draw_items(c, t):
    tip = None
    for it in ITEMS:
        if t < it["t0"]:
            continue
        k = clamp01((t - it["t0"]) / max(1e-3, it["t1"] - it["t0"]))
        if it["kind"] == "path":
            part, p = _partial(it["path"], k)
            c.drawPath(part, _marker(it["color"], it["width"]))
            c.drawPath(part, K.paint(it["color"], 0.25, it["width"] * 0.4, blur=1.2))
            if k < 1:
                tip = p
        elif it["kind"] == "text":
            w = K.text_w(it["s"], it["size"], it["font"])
            x0 = it["x"] - w / 2
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(x0 - 20, it["y"] - it["size"], x0 + w * k + 4, it["y"] + it["size"]))
            K.text(c, it["s"], it["x"], it["y"], it["size"], it["font"], it["color"])
            c.restore()
            if k < 1:
                tip = (x0 + w * k, it["y"] + it["size"] * 0.25 * math.sin(k * 40))
        else:
            p = _spring(c, t) if it["fn"] == "spring" else _clock_hands(c, t)
            if p and k < 1:
                tip = p
    return tip


def _camera(t):
    b, lt = seg.bar_at(t)
    i = b["i"]
    cur = VIEWS[i]
    prev = VIEWS[i - 1] if i > 0 else (VIEWS[0][0] - 300, VIEWS[0][1] - 200, 1.15)
    k = ease_in_out(clamp01(lt / 0.42))
    cx, cy, z = (lerp(prev[j], cur[j], k) for j in range(3))
    if i == 7:
        f = ease_in_out(clamp01((t - tb(7, 3.2)) / (b["t1"] - tb(7, 3.2) - 0.05)))
        cx, cy = lerp(cx, FULL[0], f), lerp(cy, FULL[1], f)
        z = math.exp(lerp(math.log(z), math.log(FULL[2]), f))
    # 重拍抖动
    sx = sy = 0.0
    for (bi, kb) in ((4, 0), (4, 1), (6, 1)):
        dt = t - tb(bi, kb)
        if 0 <= dt < 0.3:
            a = 14 * math.exp(-dt * 14)
            sx += a * math.sin(dt * 90)
            sy += a * math.cos(dt * 77)
    return cx, cy, z, sx, sy


def _board(c):
    c.drawColor(skia.ColorSetRGB(250, 250, 248))
    K.rr(c, BW / 2, BH / 2, BW, BH, 0, "#FBFBF9")
    for x0, y0, r in ((700, 1700, 500), (2600, 3800, 700), (1200, 5000, 500), (2800, 300, 400)):
        c.drawCircle(x0, y0, r, K.paint("#E9ECEF", 0.6, blur=120))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, BW, BH), K.paint("#C9CED6", 1, 30))


def _hand(c, x, y, active: bool):
    """简笔手 + 马克笔（屏幕坐标，笔尖在 (x, y)）。"""
    with K.at(c, x, y, -32):
        K.rr(c, 0, 95, 30, 170, 10, "#2B2B33")
        K.rr(c, 0, 12, 22, 34, 6, "#4A4A55")
        K.poly(c, [(-8, -4), (8, -4), (0, -16)], "#2B2B33")
        K.rr(c, 0, 172, 30, 28, 8, RED)
        hp = skia.Path()
        hp.addRoundRect(skia.Rect.MakeXYWH(-46, 70, 120, 150), 50, 50)
        c.drawPath(hp, K.paint("#F3D2B5"))
        c.drawPath(hp, K.paint("#8A6A55", 1, 4))
        for j in range(3):
            K.seg(c, -30 + j * 22, 92, -30 + j * 22, 128, "#8A6A55", 3)
        if not active:
            pass


_LAST_TIP = {}


def draw(c, t: float):
    cx, cy, z, sx, sy = _camera(t)
    c.drawColor(skia.ColorSetRGB(70, 74, 82))
    c.save()
    c.translate(seg.W / 2 + sx, seg.H / 2 + sy)
    c.scale(z, z)
    c.translate(-cx, -cy)
    _board(c)
    tip = _draw_items(c, t)
    c.restore()
    if tip is None:
        # 空闲时手停在最近一个完成项的末端附近
        done = [it for it in ITEMS if it["t1"] <= t and it["kind"] != "custom"]
        if done:
            it = done[-1]
            if it["kind"] == "text":
                w = K.text_w(it["s"], it["size"], it["font"])
                tip = (it["x"] + w / 2 + 30, it["y"] + 40)
            else:
                b = it["path"].getBounds()
                tip = (b.right() + 20, b.bottom())
        else:
            tip = (VIEWS[0][0] + 300, VIEWS[0][1] + 500)
        idle = True
    else:
        idle = False
    hx, hy = (tip[0] - cx) * z + seg.W / 2 + sx, (tip[1] - cy) * z + seg.H / 2 + sy
    if z > 0.6:
        _hand(c, hx, hy + (18 if idle else 0), not idle)


if __name__ == "__main__":
    seg.main("whiteboard", draw)
