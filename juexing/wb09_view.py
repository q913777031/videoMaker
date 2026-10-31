"""09 多个视角（白板手绘版）：领导一句话，郁闷一整天？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事形式 A 经典（打工人问题 → 书中观点 → 身边例子 → 做法），主线画面是一根“窥视管”：
交了方案，领导只回一个“嗯”→ 头顶冒问号：他嫌我写得差？→ 一朵乌云从下午跟到晚上，晚饭吃不下 →
drop：一根管子从眼睛连到领导的黑脸，只看得见这一面；管子“砰”地炸开，六个视角围成一圈 →
亮书（书旁一个舵写“09”）→ 书中观点：只从一个角度看最难受，人容易固执、急躁、钻牛角尖 →
回到那一圈，给其中三个视角写上别的解释（他在开会 / 他就这么回 / 在等别人意见）→
身边例子：早上堵车越想越急；过年亲戚问工资憋一肚子气 → 书中观点：脑子同时塞太多事，就没空位换角度，
拿几件放进抽屉 → 做法：郁闷时写三条别的解释 → 书中观点：游戏心态，回到那条堵车的路，猜下一辆车的颜色，火灭了 →
管子拆了、乌云散了，宝宝握舵，舵上第九道握痕 → 评论区互动。
书中观点为转述（周岭《认知觉醒》第七章 情绪力：第一节 心智带宽、第二节 单一视角、第三节 游戏心态）；
领导的“嗯”、堵车、亲戚问工资、写三条解释、猜车的颜色均为示意，据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, circle, face, join,
                               rect, scribble, stick)

from .common import BOOK, episode

ACC = "#2B8A8E"
SQUARE_SHOT = 3                 # 场景 4：管子炸开，六个视角围着主角

b = Board(size=(3600, 10800))
DARK = "#2B2B33"


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(fn, k0, k1, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


def ink(c, path, color, width, alpha=1.0):
    """和引擎描线同样的马克笔笔触（custom 动画里用）。"""
    c.drawPath(path, wb.marker(color, width, alpha))
    c.drawPath(path, K.paint(color, 0.22 * alpha, width * 0.45, blur=1.2))


def moved(path, dx=0.0, dy=0.0, s=1.0, ax=0.0, ay=0.0, rot=0.0) -> skia.Path:
    """以 (ax, ay) 为锚点缩放、旋转后再平移的路径副本。"""
    p = skia.Path(path)
    m = skia.Matrix()
    m.setTranslate(-ax, -ay)
    m.postScale(s, s)
    m.postRotate(rot)
    m.postTranslate(ax + dx, ay + dy)
    p.transform(m)
    return p


def pop_s(k):
    """弹出：0 → 1.15 → 1。"""
    return ease_out(clamp01(k * 1.6)) * (1 + 0.15 * math.sin(math.pi * clamp01(k)))


def span(j, T_, k0, k1):
    """第 j 镜第 k0–k1 拍之间的进度 0–1。"""
    t0, t1 = b.t_of(j, k0), b.t_of(j, k1)
    return clamp01((T_ - t0) / max(1e-3, t1 - t0))


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def thought(x, y, w, h, fx, fy) -> skia.Path:
    """想法泡泡：椭圆 + 两个小圆点连到 (fx, fy)。"""
    parts = [oval(x, y, w, h)]
    for f, r in ((0.35, 14), (0.65, 20)):
        parts.append(circle(fx + (x - w * 0.3 - fx) * f, fy + (y + h * 0.35 - fy) * f, r))
    return join(*parts)


def cloud(x, y, w=380, h=150) -> skia.Path:
    p = skia.Path()
    for bx, by, br in ((-0.38, 0.1, 0.32), (-0.15, -0.18, 0.4), (0.15, -0.2, 0.38), (0.38, 0.08, 0.3)):
        p.addArc(skia.Rect.MakeXYWH(x + bx * w - br * w / 2, y + by * h - br * w / 2, br * w, br * w), 160, 220)
    p.moveTo(x - w * 0.52, y + h * 0.3)
    p.lineTo(x + w * 0.52, y + h * 0.3)
    return p


def rain(x, y, w=300) -> skia.Path:
    return join(*[P((x - w / 2 + i * w / 4, y), (x - w / 2 + i * w / 4 - 18, y + 70)) for i in range(5)])


def eye(x, y, w=300, h=150) -> skia.Path:
    """杏仁眼 + 虹膜 + 瞳孔。"""
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.quadTo(x, y - h, x + w / 2, y)
    p.quadTo(x, y + h, x - w / 2, y)
    return join(p, circle(x, y, h * 0.32), circle(x, y, h * 0.12))


def dark_face(c, x, y, r, alpha=1.0):
    """领导的黑脸：涂黑的圆脸 + 红色倒八字眉 + 白色撇嘴。"""
    K.dot(c, x, y, r, DARK, alpha)
    ink(c, P((x - r * 0.62, y - r * 0.42), (x - r * 0.18, y - r * 0.2)), RED, max(5, r * 0.11), alpha)
    ink(c, P((x + r * 0.62, y - r * 0.42), (x + r * 0.18, y - r * 0.2)), RED, max(5, r * 0.11), alpha)
    K.dot(c, x - r * 0.32, y - r * 0.02, r * 0.09, "#FFFFFF", alpha)
    K.dot(c, x + r * 0.32, y - r * 0.02, r * 0.09, "#FFFFFF", alpha)
    m = skia.Path()
    m.addArc(skia.Rect.MakeXYWH(x - r * 0.35, y + r * 0.3, r * 0.7, r * 0.45), 200, 140)
    c.drawPath(m, wb.marker("#FFFFFF", max(4, r * 0.09), alpha))


def lens(c, x, y, r, s=1.0, dark=False):
    """一个“视角”：白底圆框，里面一只眼（dark=True 时是那张黑脸）。"""
    if s <= 0:
        return
    r *= s
    K.dot(c, x, y, r, "#FFFFFF")
    ink(c, circle(x, y, r), BLACK, 8)
    if dark:
        dark_face(c, x, y, r * 0.78)
    else:
        e = eye(x, y, r * 1.3, r * 0.75)
        ink(c, e, BLUE, 6)
        K.dot(c, x, y, r * 0.09, BLUE)


def car(x, g, w=240) -> skia.Path:
    """小汽车（侧视）：(x, g) 为地面中点。"""
    return join(rect(x, g - 70, w, 80, 18),
                P((x - 0.32 * w, g - 110), (x - 0.2 * w, g - 170), (x + 0.2 * w, g - 170), (x + 0.32 * w, g - 110)),
                circle(x - 0.3 * w, g - 30, 28), circle(x + 0.3 * w, g - 30, 28))


def flame(x, y, s=1.0) -> skia.Path:
    """冒火：(x, y) 为火苗底部中点。"""
    fl = skia.Path()
    fl.moveTo(x, y - 170 * s)
    fl.quadTo(x + 85 * s, y - 70 * s, x + 35 * s, y)
    fl.lineTo(x - 35 * s, y)
    fl.quadTo(x - 85 * s, y - 70 * s, x, y - 170 * s)
    inner = skia.Path()
    inner.moveTo(x, y - 90 * s)
    inner.quadTo(x + 35 * s, y - 40 * s, x, y - 5 * s)
    inner.quadTo(x - 35 * s, y - 40 * s, x, y - 90 * s)
    return join(fl, inner)


def bust(x, y, r=45) -> skia.Path:
    """饭桌后的半身：(x, y) 为头心。"""
    sh = skia.Path()
    sh.addArc(skia.Rect.MakeXYWH(x - r * 2.2, y + r * 1.1, r * 4.4, r * 3), 180, 180)
    return join(circle(x, y, r), sh)


def steam(x, y) -> skia.Path:
    """头顶冒气：三道往上的波浪线，(x, y) 为底部中点。"""
    parts = []
    for dx in (-50, 0, 50):
        p = skia.Path()
        p.moveTo(x + dx, y)
        p.quadTo(x + dx + 22, y - 30, x + dx, y - 60)
        p.quadTo(x + dx - 22, y - 90, x + dx, y - 120)
        parts.append(p)
    return join(*parts)


def cabinet(x, y, w=300, h=280) -> skia.Path:
    """抽屉柜：上层抽屉拉开。(x, y) 为柜身中心。"""
    top = y - h / 2
    return join(rect(x, y, w, h, 10), P((x - w / 2, y), (x + w / 2, y)), P((x - 30, y + h / 4), (x + 30, y + h / 4)),
                P((x - w / 2 + 20, top), (x - w / 2 + 50, top - 70), (x + w / 2 - 50, top - 70), (x + w / 2 - 20, top)),
                P((x - 30, top + h / 4), (x + 30, top + h / 4)))


def small_eye(x, y, w=110) -> skia.Path:
    return eye(x, y, w, w * 0.55)


def sun(x, y, r=70) -> skia.Path:
    parts = [circle(x, y, r)]
    for i in range(8):
        a = i / 8 * 2 * math.pi
        parts.append(P((x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3),
                       (x + math.cos(a) * r * 1.75, y + math.sin(a) * r * 1.75)))
    return join(*parts)


def rot_rect(x, y, w, h, deg) -> skia.Path:
    return moved(rect(x, y, w, h, 14), rot=deg, ax=x, ay=y)


def tube_piece(x, y, w, deg) -> skia.Path:
    """炸断的一截管子：一段圆筒，两端画椭圆口。"""
    return moved(join(rect(x, y, w, 64, 10), oval(x - w / 2, y, 26, 64), oval(x + w / 2, y, 26, 64)), rot=deg, ax=x, ay=y)


def grandpa(x, y, s=1.0) -> skia.Path:
    """老大“本能脑”：驼背、白胡子、拄拐的老爷爷。(x, y) 为脚底。"""
    hy = y - 285 * s
    hook = skia.Path()
    hook.moveTo(x + 70 * s, hy + 150 * s)
    hook.quadTo(x + 72 * s, hy + 108 * s, x + 40 * s, hy + 118 * s)
    return join(circle(x - 10 * s, hy, 45 * s),
                P((x - 45 * s, hy + 18 * s), (x - 10 * s, hy + 78 * s), (x + 25 * s, hy + 18 * s)),
                P((x - 10 * s, hy + 45 * s), (x - 30 * s, hy + 120 * s), (x - 5 * s, y - 120 * s)),
                P((x - 55 * s, y), (x - 5 * s, y - 120 * s), (x + 45 * s, y)),
                P((x - 22 * s, hy + 95 * s), (x + 70 * s, hy + 160 * s)),
                P((x + 70 * s, y), (x + 70 * s, hy + 150 * s)), hook)


def uncle(x, y, s=1.0) -> skia.Path:
    """老二“情绪脑”：戴耳机、攥着手机的大叔。(x, y) 为脚底。"""
    hy = y - 290 * s
    band = skia.Path()
    band.addArc(skia.Rect.MakeXYWH(x - 58 * s, hy - 62 * s, 116 * s, 116 * s), 180, 180)
    return join(stick(x, y, s, "hold"), band, rect(x - 54 * s, hy, 22 * s, 44 * s, 8 * s),
                rect(x + 54 * s, hy, 22 * s, 44 * s, 8 * s))


def baby(x, y, s=1.0) -> skia.Path:
    """老三“理智脑”：大头、戴围嘴的小宝宝，双手举起握舵。(x, y) 为脚底。"""
    hy = y - 150 * s
    r = 55 * s
    bib = skia.Path()
    bib.addArc(skia.Rect.MakeXYWH(x - 30 * s, hy + r - 22 * s, 60 * s, 50 * s), 0, 180)
    curl = skia.Path()
    curl.moveTo(x - 6 * s, hy - r)
    curl.quadTo(x + 4 * s, hy - r - 26 * s, x + 18 * s, hy - r - 12 * s)
    eyes = skia.Path()
    eyes.addCircle(x - 18 * s, hy - 4 * s, 3.5 * s)
    eyes.addCircle(x + 18 * s, hy - 4 * s, 3.5 * s)
    hands = join(P((x - 24 * s, hy + r + 8 * s), (x - 80 * s, hy - 70 * s)),
                 P((x + 24 * s, hy + r + 8 * s), (x + 80 * s, hy - 70 * s)))
    return join(circle(x, hy, r), curl, eyes, P((x - 8 * s, hy + 22 * s), (x + 8 * s, hy + 22 * s)), bib,
                P((x, hy + r), (x, y - 50 * s)), P((x - 34 * s, y), (x, y - 50 * s), (x + 34 * s, y)), hands)


def rudder(x, y, r=140) -> skia.Path:
    """船舵：轮圈 + 轮毂 + 八根辐条伸出把手。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.22)]
    for i in range(8):
        a = i / 8 * 2 * math.pi
        parts.append(P((x + math.cos(a) * r * 0.22, y + math.sin(a) * r * 0.22),
                       (x + math.cos(a) * r * 1.28, y + math.sin(a) * r * 1.28)))
        parts.append(circle(x + math.cos(a) * r * 1.33, y + math.sin(a) * r * 1.33, r * 0.07))
    return join(*parts)


def grips(x, y, r, idx) -> skia.Path:
    """舵圈上的握痕：一圈分十格（第 N 讲握满 N 格），每道是轮圈上一小段粗弧。"""
    p = skia.Path()
    for i in idx:
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -90 - 8 + i * 36, 16)
    return p


# ---------------------------------------------------------------- 打工人问题（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("领导回了一个嗯", "打工人问题 · 一个嗯", (1000, 850, 0.85), bars=2)
L(join(rect(1000, 880, 560, 880, 60), P((950, 1270), (1050, 1270))), 0, 0.9, BLACK, 10, sfx="wood_high")
T("领导", 1000, 545, 54, k0=1, k1=1.8, sfx="pop")
L(P((760, 600), (1240, 600)), 1.8, 2.0, BLACK, 5)
L(bubble(1100, 730, 400, 120, 1), 2, 2.6, BLUE, 8, sfx="wood_low")
T("方案发您了", 1100, 730, 54, BLUE, k0=2.6, k1=3.85)
L(bubble(860, 960, 220, 170, -1), 4, 4.6, BLACK, 8, sfx="wood_high")
T("嗯", 860, 960, 100, k0=5, k1=5.8, sfx="rim")

scene("他嫌我写得差？", "打工人问题 · 开始乱想", (2600, 850, 0.85))
L(stick(2330, 1320, 1.05, "down"), 0, 0.9, BLACK, 10, sfx="wood_high")
L(face(2330, 1320, 1.05, "sad"), 1, 1.4, BLACK, 8, sfx="wood_low")
L(thought(2740, 610, 780, 260, 2370, 960), 2, 2.8, BLACK, 8, sfx="pop")
T("他嫌我写得差？", 2740, 615, 64, k0=3, k1=4.75, sfx="pop")
T("？", 2620, 1010, 100, RED, k0=5, k1=5.8, sfx="pop")
T("？", 2820, 920, 120, RED, k0=6, k1=6.8, sfx="wood_high")
T("？", 3020, 1030, 130, RED, k0=7, k1=7.8, sfx="pop")

CX0, CX1, CY3 = 600, 1600, 2240
GROUND3 = 2700


def cloud_walk(j):
    """场景 3：乌云跟着垂头的小人，从下午走到晚上。"""
    def fn(c, k, T_):
        x = lerp(CX0, CX1, ease_in_out(k))
        ink(c, moved(stick(CX0, GROUND3 - 10, 0.7, "down"), dx=x - CX0), BLACK, 9)
        ink(c, moved(face(CX0, GROUND3 - 10, 0.7, "sad"), dx=x - CX0), BLACK, 7)
        ink(c, cloud(x, CY3, 380, 150), DARK, 9)
        ink(c, rain(x, CY3 + 85, 280), BLUE, 6, 0.5 + 0.5 * abs(math.sin(T_ * 6)))
        return None
    return fn


scene("郁闷到晚上", "打工人问题 · 郁闷一天", (1250, 2500, 0.55))
L(arrow((450, GROUND3), (2120, GROUND3), 0.0, 60), 0, 0.9, BLACK, 10, sfx="wood_high")
T("15:00", 600, 2830, 88, k0=1, k1=2.25, sfx="pop")
T("21:00", 1950, 2830, 88, RED, k0=2, k1=3.25, sfx="pop")
C(cloud_walk(J()), 3, 6, sfx="shaker")
H(5, "shaker", 0.6)
L(join(oval(1960, GROUND3 - 45, 150, 40), P((1885, GROUND3 - 45), (1910, GROUND3 - 5), (2010, GROUND3 - 5),
                                           (2035, GROUND3 - 45))), 6, 6.8, BLACK, 9, sfx="wood_low")
T("吃不下", 1960, 2500, 84, RED, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- drop：管子里只看见一张黑脸，炸开成六个视角（场景 4）

RC, RR, LR = (1250, 4100), 470, 85
MAN = (1250, 4250, 0.8)                         # 主角：圆心正下方
TUBE = (1310, 1760, 4010, 38)                   # 管子：x0, x1, 中线 y, 半粗
FACE = (1850, 4010, 90)
SLOTS = [(RC[0] + RR * math.cos(math.radians(a)), RC[1] + RR * math.sin(math.radians(a))) for a in range(0, 360, 60)]
WAVE = {0: (3, 4), 2: (3, 4), 4: (3, 4), 1: (4, 5), 3: (4, 5), 5: (4, 5)}   # 每个视角飞出、落定的拍
SHARDS = [(1360 + i * 45, 4010 + (-1) ** i * 38, math.radians(-150 + i * 33)) for i in range(10)]


def tube_path(dy=0.0) -> skia.Path:
    x0, x1, y, h = TUBE
    return join(P((x0, y - h + dy), (x1, y - h + dy)), P((x0, y + h + dy), (x1, y + h + dy)),
                oval(x0, y + dy, 26, 2 * h), oval(x1, y + dy, 26, 2 * h))


def drop_fn(j):
    def fn(c, k, T_):
        s = pop_s(span(j, T_, 0, 0.7))
        mx, my, ms = MAN
        ink(c, moved(stick(mx, my, ms, "down"), s=s, ax=mx, ay=my), BLACK, 9)
        ink(c, moved(face(mx, my, ms, "sad"), s=s, ax=mx, ay=my), BLACK, 7)
        burst = span(j, T_, 3, 3.9)
        if burst <= 0:
            shake = 7 * math.sin(T_ * 70) * span(j, T_, 2, 2.3)
            ink(c, moved(tube_path(shake), s=s, ax=TUBE[0], ay=TUBE[2]), BLACK, 10)
            cr = span(j, T_, 2, 2.9)
            if cr > 0:                                       # 管壁裂纹
                for i in range(int(cr * 4) + 1):
                    x = 1400 + i * 100
                    ink(c, P((x, 3972 + shake), (x + 20, 3995 + shake), (x - 10, 4015 + shake)), RED, 6)
            fx, fy, fr = FACE
            dark_face(c, fx, fy, fr * s)
            a = span(j, T_, 1, 1.6)
            if a > 0:                                        # 黑脸冒怒气
                for d in (-0.9, -0.5, -0.1):
                    ink(c, P((fx + math.cos(d) * fr * 1.2, fy + math.sin(d) * fr * 1.2),
                             (fx + math.cos(d) * fr * (1.2 + 0.5 * a), fy + math.sin(d) * fr * (1.2 + 0.5 * a))), RED, 8)
        elif burst < 1:                                      # 碎片四散
            for x, y, ang in SHARDS:
                d = 260 * ease_out(burst)
                xx, yy = x + math.cos(ang) * d, y + math.sin(ang) * d
                ink(c, P((xx - 30 * math.cos(ang + 1.2), yy - 30 * math.sin(ang + 1.2)),
                         (xx + 30 * math.cos(ang + 1.2), yy + 30 * math.sin(ang + 1.2))), BLACK, 9, 1 - burst)
            K.dot(c, 1530, 4010, 220 * ease_out(burst), "#F2C14E", 0.5 * (1 - burst))
        for i, (sx, sy) in enumerate(SLOTS):
            k0, k1 = WAVE[i]
            u = span(j, T_, k0, k1 - 0.15)
            if u <= 0:
                continue
            e = ease_out(u)
            ox, oy = (FACE[0], FACE[1]) if i == 0 else (1530, 4010)
            lens(c, lerp(ox, sx, e), lerp(oy, sy, e), LR, pop_s(u) if i else 1.0, dark=(i == 0))
        return None
    return fn


scene("只从管子里看", "书中观点 · 管子里只有一面", (RC[0], RC[1], 0.66), shake=[0, 3], flashes=[0])
C(drop_fn(J()), 0, 5, sfx="kick")
H(1, "tom")
H(2, "shaker")
H(3, "kick", 0.9, "管子炸开")
H(4, "pop")
H(5, "pop")
T("六个角度", RC[0], 3480, 72, GREEN, k0=6, k1=7, sfx="ding")

# ---------------------------------------------------------------- 亮书（场景 5）

scene("有本书讲过", "亮书 · 认知觉醒", (2900, 2500, 0.85))
L(book(2700, 2550, 440, 300), 0, 0.9, BLACK, 9, sfx="wood_low")
T("《认知觉醒》", 2700, 2280, 68, GREEN, k0=1, k1=2.5, sfx="pop")
T("周岭", 2700, 2820, 56, k0=3, k1=3.8, sfx="pop")
L(rudder(3290, 2480, 105), 4, 4.9, GREEN, 8, sfx="wood_high")
T("09", 3290, 2740, 80, RED, k0=5, k1=5.8, sfx="ding")
T("第七章 情绪力", 2900, 2090, 56, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 书中观点：一个角度（场景 6）

scene("一个角度最难受", "书中观点 · 视角单一", (2700, 4100, 0.85))
L(eye(2290, 4100, 300, 150), 0, 0.9, BLACK, 9, sfx="wood_high")
L(join(P((2450, 4085), (3170, 4045)), P((2450, 4115), (3170, 4155)), oval(3170, 4100, 40, 110)), 1, 1.9, BLACK, 8,
  sfx="wood_low")
C(lambda c, k, T_: dark_face(c, 3215, 4100, 46 * ease_out(k)), 2, 2.5, sfx="rim")
T("只看见一面", 2700, 3740, 66, k0=3, k1=4.25, sfx="pop")
T("固执", 2330, 4490, 62, RED, k0=5, k1=5.8, sfx="pop")
T("急躁", 2700, 4490, 62, RED, k0=6, k1=6.8, sfx="pop")
T("钻牛角尖", 3090, 4490, 62, RED, k0=7, k1=8, sfx="rim")

# ---------------------------------------------------------------- 回到那一圈：给三个视角写上别的解释（场景 7）

scene("换几个角度", "示意 · 换几个角度", (RC[0], RC[1], 0.66))
LAB_Y = LR + 62
T("嫌我写得差", SLOTS[0][0], SLOTS[0][1] + LAB_Y, 60, RED, k0=0, k1=1.25, sfx="rim")
T("他在开会", SLOTS[3][0], SLOTS[3][1] + LAB_Y, 62, BLUE, k0=2, k1=3, sfx="pop")
T("他就这么回", SLOTS[4][0], SLOTS[4][1] + LAB_Y, 62, BLUE, k0=4, k1=5.25, sfx="pop")
T("在等别人意见", SLOTS[5][0], SLOTS[5][1] + LAB_Y, 62, BLUE, k0=6, k1=7.5, sfx="ding")

# ---------------------------------------------------------------- 身边例子：堵车（场景 8）

G8 = 5800
CARS = [600, 890, 1180, 1470]                   # 第三辆是主角的车
FIRE = [(1150, 5615, 0.7), (1225, 5615, 0.55)]

scene("堵车也一样", "身边例子 · 早上堵车", (1050, 5600, 0.85))
L(join(P((440, G8), (1660, G8)), *[P((480 + i * 180, G8 + 70), (560 + i * 180, G8 + 70)) for i in range(7)]),
  0, 0.9, BLACK, 9, sfx="wood_high")
L(join(car(CARS[0], G8), car(CARS[1], G8)), 1, 1.9, BLACK, 8, sfx="wood_low")
L(car(CARS[3], G8), 2, 2.8, BLACK, 8, sfx="wood_low")
L(join(car(CARS[2], G8), circle(CARS[2], G8 - 135, 24)), 3, 3.8, RED, 9, sfx="wood_high")
L(join(*[flame(*f) for f in FIRE]), 4, 4.9, RED, 8, sfx="tom")
T("越想越急", 1050, 5250, 66, RED, k0=6, k1=7, sfx="pop")

# ---------------------------------------------------------------- 身边例子：亲戚问工资（场景 9）

TB = 5720
scene("亲戚问工资", "身边例子 · 过年饭桌", (2650, 5600, 0.85))
L(join(P((2150, TB), (3170, TB)), P((2200, TB), (2200, TB + 150)), P((3120, TB), (3120, TB + 150))), 0, 0.9, BLACK, 9,
  sfx="wood_high")
L(join(bust(2330, 5540), bust(2580, 5540)), 1, 1.9, BLACK, 8, sfx="pop")
L(bust(2960, 5560), 2, 2.8, BLUE, 9, sfx="wood_low")
L(bubble(2450, 5280, 460, 140, 1), 3, 3.7, BLACK, 8, sfx="pop")
T("一个月多少？", 2450, 5280, 56, k0=3.7, k1=5.2)
L(steam(2960, 5470), 5.2, 6.0, RED, 7)
H(5, "tom")
T("憋一肚子气", 2650, 5890, 62, RED, k0=6, k1=7.25, sfx="pop")

# ---------------------------------------------------------------- 书中观点：脑子塞满了（场景 10）

HC, HR_ = (2400, 7020), 320
DRAWER = (3060, 7250)
_icons = [(-170, -150), (-30, -190), (110, -130), (-210, -20), (-70, -50), (70, 0), (200, 40), (-160, 110),
          (-20, 110), (120, 140), (-90, 220), (50, 230)]
ICONS = [(HC[0] + dx, HC[1] + dy, (i * 37) % 30 - 15) for i, (dx, dy) in enumerate(_icons)]
MOVE = [2, 6, 5]                                # 这三件拿出来放进抽屉
SPOT = (HC[0] + 130, HC[1] - 60)


def icon(c, x, y, deg, s=1.0, col=BLACK):
    """一件“事”：小便签（带两行字线）。"""
    p = join(rect(x, y, 96, 72, 10), P((x - 30, y - 10), (x + 30, y - 10)), P((x - 30, y + 14), (x + 14, y + 14)))
    ink(c, moved(p, s=s, rot=deg, ax=x, ay=y), col, 6)


def crammed_fn(j):
    def fn(c, k, T_):
        for i, (x, y, deg) in enumerate(ICONS):
            u = span(j, T_, 1 + i * 0.12, 1.4 + i * 0.12)
            if u <= 0:
                break
            col = (BLACK, RED, BLUE)[i % 3]
            if i in MOVE:
                n = MOVE.index(i)
                m = span(j, T_, 6 + n * 0.25, 6.6 + n * 0.25)
                if m >= 1:
                    continue
                e = ease_in_out(m)
                icon(c, lerp(x, DRAWER[0], e), lerp(y, DRAWER[1] - 190, e), deg * (1 - e), pop_s(u) * (1 - 0.5 * e), col)
            else:
                icon(c, x, y, deg, pop_s(u), col)
        return None
    return fn


def spot_fn(c, k, T_):
    pt = wb.marker(GREEN, 7)
    pt.setPathEffect(skia.DashPathEffect.Make([22, 16], 0))
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(SPOT[0] - 120, SPOT[1] - 120, 240, 240), -90, 360 * k)
    c.drawPath(p, pt)
    return None


scene("脑子塞满了", "书中观点 · 心智带宽", (2650, 7000, 0.85))
L(join(circle(*HC, HR_), P((HC[0] - 90, HC[1] + 310), (HC[0] - 90, HC[1] + 400)),
       P((HC[0] + 90, HC[1] + 310), (HC[0] + 90, HC[1] + 400))), 0, 0.9, BLACK, 10, sfx="wood_high")
C(crammed_fn(J()), 1, 7, sfx="pop")
H(2, "pop", 0.7)
T("同时装太多事", 2650, 6570, 62, k0=3, k1=4.5, sfx="pop")
L(cabinet(*DRAWER), 5, 5.8, BLACK, 8, sfx="wood_low")
H(6, "shaker")
C(spot_fn, 7, 7.6)
T("空位", SPOT[0], SPOT[1], 60, GREEN, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 做法：写下三个角度（场景 11）

scene("写下三个角度", "做法 · 写三条解释", (1050, 7000, 0.85))
L(rect(1050, 7060, 760, 700, 20), 0, 0.9, BLACK, 9, sfx="wood_high")
T("郁闷时写三条", 1050, 6610, 64, BLUE, k0=1, k1=2.5, sfx="pop")
for n, (s_, k) in enumerate((("他在忙", 2), ("他打字就这样", 4), ("明天当面问", 6))):
    y = 6880 + n * 200
    L(small_eye(790, y), k, k + 0.5, BLUE, 7, sfx="wood_low" if n != 1 else "wood_high")
    T(s_, 1110, y, 60, k0=k + 0.5)

# ---------------------------------------------------------------- 书中观点：游戏心态，回到那条堵车的路（场景 12）

scene("把它当个游戏", "书中观点 · 游戏心态", (1050, 5600, 0.85))
b.erase(J(), 0, 0.9, 1050, 5412, 920, 420)
H(0, "shaker")
T("猜下一辆啥颜色", 1050, 5290, 64, BLUE, k0=1, k1=2.75, sfx="pop")
for n, (ci, col) in enumerate(((0, BLUE), (1, GREEN), (3, ORANGE))):
    L(scribble(CARS[ci], G8 - 70, 200, 56, 6), 3 + n, 3.8 + n, col, 9, sfx="wood_high" if n != 1 else "wood_low")
L(face(CARS[2], G8 - 135 + 290 * 0.5, 0.5, "smile"), 6, 6.6, GREEN, 6, sfx="pop")
T("火灭了", CARS[2], 5480, 58, GREEN, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 管子拆了，宝宝握舵（场景 13）

MX13, G13 = 1300, 9050
HD = (2250, 8600, 330)
WH = (2400, 8690, 58)


def cloud_away(c, k, T_):
    """乌云往右上飘走、变淡。"""
    e = ease_in_out(k)
    ink(c, cloud(MX13 + 320 * e, 8300 - 120 * e, 380, 150), DARK, 9, 1 - e)
    return None


scene("管子拆了", "拉远 · 换个角度", (1800, 8700, 0.6))
L(join(P((900, G13), (1720, G13)), tube_piece(1030, G13 - 40, 200, -12), tube_piece(1560, G13 - 36, 170, 15)),
  0, 0.9, BLACK, 9, sfx="wood_high")
L(join(stick(MX13, G13, 1.0, "up"), face(MX13, G13, 1.0, "smile")), 1, 1.9, BLACK, 10, sfx="pop")
C(cloud_away, 2, 3.4, sfx="shaker")
L(sun(1560, 8180, 64), 3, 3.8, ORANGE, 9, sfx="wood_low")
L(join(circle(HD[0], HD[1], HD[2]), P((HD[0] - 90, HD[1] + 318), (HD[0] - 90, HD[1] + 420)),
       P((HD[0] + 90, HD[1] + 318), (HD[0] + 90, HD[1] + 420))), 4, 4.9, BLACK, 10, sfx="wood_high")
L(join(grandpa(2060, 8880, 0.5), uncle(2210, 8880, 0.5)), 5, 5.8, BLACK, 7, sfx="pop")
L(join(baby(WH[0], 8900, 0.65), rudder(*WH)), 6, 6.8, BLUE, 7, sfx="wood_low")
L(grips(*WH, range(8)), 7, 7.4, BLUE, 16, sfx="ding")
L(grips(*WH, [8]), 7.4, 7.9, RED, 20)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 5400, 0.088)
COMMENT = (1800, 10100, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
L(join(rect(1800, 10100, 1250, 480, 40), P((1500, 10340), (1440, 10430), (1600, 10340))), 5, 5.9, BLACK, 9,
  sfx="wood_high")
T("最近哪件事让你郁闷一整天？", 1800, 10030, 64, RED, k0=6, k1=9.25, sfx="pop")
T("下一讲：下班后那两小时，怎么过？", 1800, 10200, 50, k0=10, k1=14, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "view", "多个视角", "领导一句话，郁闷一整天？", ACC, b.shots,
                 [f"{BOOK}第七章 情绪力——情绪是多角度看问题的智慧：第一节 心智带宽、第二节 单一视角、第三节 游戏心态（转述）"],
                 "领导一句话|郁闷【一整天】", SQUARE_SHOT,
                 ["书中观点均为转述，不是逐字引文：坏情绪常来自只从一个角度看问题，视角单一的人容易固执、急躁、钻牛角尖；"
                  "脑子同时装着太多事就没有余量，会行动的人会想办法避免同时做很多事（心智带宽）；"
                  "做一件事时给自己找另一种乐趣（游戏心态）。见第七章 情绪力（第一、二、三节）。"
                  "第七章是否引了《稀缺》一书未核实，本讲不提。",
                  "领导只回一个“嗯”、郁闷到晚上吃不下饭、早上堵车、过年亲戚问工资均为现实场景示意，不指向任何具体公司或个人；"
                  "“15:00 / 21:00”等时间为示意，不是数据。",
                  "“窥视管”炸开成六个视角、三个视角上的解释（他在开会 / 他就这么回 / 在等别人意见）、"
                  "郁闷时写三条别的解释、堵车时猜下一辆车的颜色，均为据书中思路整理的示意与做法。",
                  "脑内三兄弟（本能脑、情绪脑、理智脑宝宝）与船舵握痕为系列视觉角色，据第一章“三重大脑”与第三章“思维舵手”的比喻；"
                  "第 9 讲舵上共九道握痕（前八道蓝色，新加一道红色）。"],
                 tags="#情绪 #职场")
    return b.attach(ep)
