"""06 提请求（白板手绘版）：说了“别总加班”，他报了球赛。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（G 倒叙）：先给结局（她把手机往沙发上一摔，更气了；他兴冲冲报了周末球赛，“加班少了”）→
倒带回三周前（日历往回翻）→ drop：她当时说的是“别总加班”，他照做了，加班换成了球赛 →
亮书《非暴力沟通》，四格卡点亮“手”（请求）→ 书中观点（第六章，转述）：说想要对方做什么，少说不要什么；
请求要具体明确；请求和命令，看对方说“不”时你的反应；可以请对方用自己的话复述一遍 →
换两个场景练一练（公司：别再出错 → 提交前对一遍清单；家里：多关心我 → 睡前陪我聊十分钟）→
重来一次：三周前她改说“周三周五七点前回家吃饭，行吗？”，小泡的刺缩回去 → 周三的饭桌 → 拉远看全板 → 评论区。
书中观点为转述（马歇尔·卢森堡《非暴力沟通》第六章“请求帮助”；英文版第 6 章 Requesting That Which Would
Enrich Life；中译本阮胤华译，华夏出版社）；球赛情节、公司与家里的改写均为示意 / 据书中思路整理。
"""

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, clock,
                               face, hands_at, join, marker, partial, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#C98A1C"                 # 本讲主色：琥珀（四格卡第四格“手”）
SQUARE_SHOT = 3                 # 场景 4：大“别”字 + 分岔箭头（少加班 → 去打球）+ 举球的他

b = Board(size=(3600, 12000))
Z = 0.85
XL, XR = 950, 2650              # 左右两列
R1, R2, R3, R4, R5, R6, R7, R8 = 900, 2350, 3900, 5400, 6850, 8300, 9750, 11200


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


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


def _stroke(c, path, color, width):
    c.drawPath(path, marker(color, width))
    c.drawPath(path, K.paint(color, 0.22, width * 0.45, blur=1.2))


def _span(j, k0, k1, t):
    """时刻 t 在镜头 j 第 k0–k1 拍之间的进度（0–1）。"""
    a, z = b.t_of(j, k0), b.t_of(j, k1)
    return clamp01((t - a) / max(1e-3, z - a))


# ---------------------------------------------------------------- 本讲画法

def sofa(x, y, w=520) -> skia.Path:
    """沙发：(x, y) 为地面中点；坐垫上沿在 y - 120。"""
    return join(rect(x, y - 75, w, 90, 20), rect(x, y - 200, w - 80, 160, 26),
                rect(x - w / 2, y - 130, 60, 150, 20), rect(x + w / 2, y - 130, 60, 150, 20),
                P((x - w / 2 + 30, y - 30), (x - w / 2 + 30, y)), P((x + w / 2 - 30, y - 30), (x + w / 2 - 30, y)))


def ball(x, y, r=45) -> skia.Path:
    s1 = skia.Path()
    s1.moveTo(x - r, y)
    s1.quadTo(x, y - r * 0.55, x + r, y)
    s2 = skia.Path()
    s2.moveTo(x, y - r)
    s2.quadTo(x + r * 0.55, y, x, y + r)
    return join(circle(x, y, r), s1, s2)


def calendar(x, y, w, h, cols=7, rows=3, head=70) -> skia.Path:
    top = y - h / 2
    parts = [rect(x, y, w, h, 14), P((x - w / 2, top + head), (x + w / 2, top + head))]
    for i in range(1, cols):
        xx = x - w / 2 + w * i / cols
        parts.append(P((xx, top + head), (xx, y + h / 2)))
    for r in range(1, rows):
        yy = top + head + (h - head) * r / rows
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
    for dx in (-w / 4, w / 4):
        parts.append(P((x + dx, top - 22), (x + dx, top + 22)))
    return join(*parts)


def rewind(x, y, s=1.0) -> skia.Path:
    """倒带符号：两个朝左的三角。"""
    return join(P((x, y - 70 * s), (x - 110 * s, y), (x, y + 70 * s), close=True),
                P((x + 110 * s, y - 70 * s), (x, y), (x + 110 * s, y + 70 * s), close=True))


def play(x, y, r=70) -> skia.Path:
    return join(circle(x, y, r), P((x - r * 0.3, y - r * 0.45), (x + r * 0.5, y), (x - r * 0.3, y + r * 0.45), close=True))


def eye(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 60 * s, y)
    p.quadTo(x, y - 55 * s, x + 60 * s, y)
    p.quadTo(x, y + 55 * s, x - 60 * s, y)
    return join(p, circle(x, y, 17 * s))


def heart(x, y, r=45) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def battery(x, y, s=1.0) -> skia.Path:
    return join(rect(x, y, 110 * s, 60 * s, 10 * s), rect(x + 63 * s, y, 14 * s, 26 * s, 4 * s),
                rect(x - 36 * s, y, 18 * s, 38 * s, 3 * s))


def palm(x, y, s=1.0) -> skia.Path:
    """伸出的手：手掌 + 四指 + 拇指。"""
    parts = [rect(x, y + 20 * s, 72 * s, 70 * s, 22 * s)]
    for n, dx in enumerate((-26, -9, 9, 26)):
        h = (62, 72, 70, 58)[n]
        parts.append(P((x + dx * s, y - 12 * s), (x + dx * s, y - 12 * s - h * s)))
    parts.append(P((x - 34 * s, y + 18 * s), (x - 62 * s, y - 14 * s)))
    return join(*parts)


CARD = (950, 5610, 880, 220)                            # 四格卡：中心、宽、高
CELLS = [CARD[0] - 330 + 220 * i for i in range(4)]    # 四格中心 x


def card4() -> skia.Path:
    x, y, w, h = CARD
    return join(rect(x, y, w, h, 20), *[P((x - w / 2 + w * i / 4, y - h / 2), (x - w / 2 + w * i / 4, y + h / 2))
                                        for i in (1, 2, 3)])


def card_icons() -> skia.Path:
    y = CARD[1]
    return join(eye(CELLS[0], y), heart(CELLS[1], y + 5, 42), battery(CELLS[2], y), palm(CELLS[3], y + 10))


def checklist(x, y, w=300, n=3, gap=95) -> tuple[skia.Path, skia.Path]:
    """清单：（框 + 方格 + 横线，勾）。"""
    h = gap * n + 70
    top = y - h / 2
    parts, ticks = [rect(x, y, w, h, 16)], []
    for i in range(n):
        yy = top + 70 + i * gap
        bx = x - w / 2 + 55
        parts += [rect(bx, yy, 44, 44, 6), P((bx + 50, yy), (x + w / 2 - 30 - (i % 2) * 30, yy))]
        ticks.append(check(bx, yy, 24))
    return join(*parts), join(*ticks)


def bed(x, y, w=520) -> skia.Path:
    """床：(x, y) 为地面中点，床头在左。"""
    return join(rect(x, y - 95, w, 70, 14), P((x - w / 2, y - 60), (x - w / 2, y - 280)),
                P((x - w / 2 - 12, y - 280), (x - w / 2 + 40, y - 280)), rect(x - w / 2 + 90, y - 155, 120, 50, 22),
                P((x - w / 2 + 20, y - 60), (x - w / 2 + 20, y)), P((x + w / 2 - 20, y - 60), (x + w / 2 - 20, y)))


def alarm(x, y, r=55) -> skia.Path:
    bells = []
    for sx in (-1, 1):
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(x + sx * r * 0.75 - r * 0.35, y - r * 1.15, r * 0.7, r * 0.7), 180, 180)
        bells.append(p)
    return join(clock(x, y, r), hands_at(x, y, r, 10, 10), P((x - r * 0.6, y + r * 0.8), (x - r * 0.85, y + r * 1.15)),
                P((x + r * 0.6, y + r * 0.8), (x + r * 0.85, y + r * 1.15)), *bells)


def bowl(x, y, r=70) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r * 0.9, 2 * r, 1.8 * r), 0, 180)
    parts = [p, P((x - r - 12, y), (x + r + 12, y))]
    for dx in (-r * 0.3, r * 0.3):
        st = skia.Path()
        st.moveTo(x + dx, y - 20)
        st.quadTo(x + dx - 18, y - 50, x + dx, y - 80)
        st.quadTo(x + dx + 18, y - 110, x + dx, y - 135)
        parts.append(st)
    return join(*parts)


def ripples(x, y, n=3, gap=34, r0=60) -> skia.Path:
    """回声：朝右张开的几道弧。"""
    parts = []
    for i in range(n):
        r = r0 + i * gap
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -40, 80)
        parts.append(p)
    return join(*parts)


def cracks(x, y, s=1.0) -> skia.Path:
    """砸地的裂纹 + 两侧冲击短线。"""
    return join(P((x - 20 * s, y), (x - 70 * s, y + 30 * s), (x - 110 * s, y + 20 * s), (x - 160 * s, y + 50 * s)),
                P((x + 20 * s, y), (x + 60 * s, y + 35 * s), (x + 120 * s, y + 25 * s), (x + 150 * s, y + 60 * s)),
                P((x - 190 * s, y - 120 * s), (x - 250 * s, y - 150 * s)), P((x - 200 * s, y - 50 * s), (x - 265 * s, y - 50 * s)),
                P((x + 190 * s, y - 120 * s), (x + 250 * s, y - 150 * s)), P((x + 200 * s, y - 50 * s), (x + 265 * s, y - 50 * s)))


def comment_box(x, y, w=1200, h=520) -> skia.Path:
    return join(rect(x, y, w, h, 30), circle(x - w / 2 + 80, y - h / 2 + 80, 40),
                P((x - w / 2 + 140, y - h / 2 + 80), (x - w / 2 + 380, y - h / 2 + 80)))


# ---------------------------------------------------------------- 系列角色：话泡泡“小泡”（会长刺、会缩刺）

def pao_fn(x, y, w, h, words="", size=64, tail=-1, retract=None, spike=46):
    """小泡：k 为描出进度；retract=(镜头, 起拍, 止拍) 时刺一根根缩回去，红变蓝、嘴角上扬、带刺的话淡出。"""
    outline = bubble(x, y, w, h, tail)
    ex, ey = y - h / 2 + 62, y - h / 2 + 96            # 眼睛、嘴的纵坐标

    def fn(c, k, t):
        r = ease_in_out(_span(*retract, t)) if retract else 0.0
        color = K.mix(RED, BLUE, r)
        part, tip = partial(outline, k)
        _stroke(c, part, color, 9)
        n = 9
        pm = skia.PathMeasure(rect(x, y, w, h, 40), False)
        total = pm.getLength()
        sp = skia.Path()
        for i in range(n * 2):
            # 逐根缩回：每根刺各自的进度错开
            ri = clamp01(r * 1.6 - i / (n * 2) * 0.6) if retract else 0.0
            grow = clamp01((k - 0.35) / 0.5)
            ln = spike * grow * (1 - ease_out(ri))
            if ln <= 0.5:
                continue
            d = total * (i + 0.5) / (n * 2)
            pos, tan = pm.getPosTan(d)
            px, py, tx, ty = pos.x(), pos.y(), tan.x(), tan.y()
            sp.moveTo(px - tx * 22, py - ty * 22)
            sp.lineTo(px + ty * ln, py - tx * ln)
            sp.lineTo(px + tx * 22, py + ty * 22)
        _stroke(c, sp, RED if not retract else K.mix(RED, BLUE, r), 7)
        if k > 0.6:
            a = clamp01((k - 0.6) / 0.3)
            for dx in (-55, 55):
                K.dot(c, x + dx, ex, 11, color, a)
            m = skia.Path()
            m.moveTo(x - 38, ey)
            m.quadTo(x, ey + lerp(-26, 30, r), x + 38, ey)
            c.drawPath(m, K.paint(color, a, 8))
            if words:
                K.text(c, words, x, y + h * 0.18, size, "hand", RED, a * (1 - r))
        return tip

    return fn


# ---------------------------------------------------------------- 结局先放（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

SOFA = (850, 1250)
SHE = (1300, 1330)
scene("结局：她更气了", "结局", (XL, R1, Z), bars=2, shake=[3])
L(sofa(*SOFA), 0, 0.9, sfx="wood_high")
L(stick(*SHE, 0.8, hair=True), 1, 1.8, sfx="pop")
L(face(*SHE, 0.8, "sad"), 1.8, 2.0)
L(join(P((1360, 1030), (1400, 1000)), P((1375, 1050), (1425, 1035)), P((1350, 1010), (1365, 970))), 2, 2.6, RED, 8,
  sfx="wood_low")


def phone_fn(c, k, t):
    """手机从她手边甩到沙发上，弹一下，躺平。"""
    x0, y0 = SHE[0] - 60, SHE[1] - 100
    x1, y1 = SOFA[0] - 90, SOFA[1] - 155
    if k < 0.55:
        f = k / 0.55
        x, y = lerp(x0, x1, f), lerp(y0, y1, f) - 260 * 4 * f * (1 - f)
        ang = lerp(0, 320, f)
    else:
        f = (k - 0.55) / 0.45
        x, y = x1 - 40 * f, y1 - 90 * 4 * f * (1 - f)
        ang = lerp(320, 450, ease_out(f))
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    _stroke(c, join(rect(0, 0, 70, 120, 12), P((-12, 44), (12, 44))), BLACK, 8)
    c.restore()
    return None


C(phone_fn, 3, 4.2, sfx="kick")
L(join(P((SOFA[0] - 200, 1070), (SOFA[0] - 175, 1020)), P((SOFA[0] - 130, 1050), (SOFA[0] - 130, 990)),
       P((SOFA[0] - 60, 1070), (SOFA[0] - 85, 1020))), 4.2, 4.9, BLACK, 7)
H(4, "pop")
C(pao_fn(1250, 720, 300, 160, "哼！", 66), 5, 5.8, sfx="rim")

MAN2 = (2350, 1330)
scene("他报了周末球赛", "结局", (XR, R1, Z))
L(stick(*MAN2, 0.8, "up"), 0, 0.9, sfx="wood_high")
L(face(*MAN2, 0.8, "smile"), 0.9, 1.0)
L(ball(MAN2[0], 990, 45), 1, 1.8, ORANGE, 9, sfx="pop")
L(calendar(2900, 1060, 420, 330), 2, 2.9, BLACK, 7, sfx="wood_high")
L(rect(3050, 1095, 130, 250, 30), 3, 3.8, RED, 9, sfx="ding")
T("球赛", 3050, 1095, 46, RED, k0=4, k1=4.8, sfx="pop")
L(bubble(2480, 680, 480, 140, -1), 5, 5.4, BLUE, 8, sfx="pop")
T("加班少了！", 2480, 680, 60, BLUE, k0=5.4, k1=6.65)

# ---------------------------------------------------------------- 倒带（场景 3–4）

CAL3 = (2650, 2420, 520, 440)
scene("倒回三周前", "倒带", (XR, R2, Z))
L(rewind(2650, 2040), 0, 0.8, RED, 10, sfx="tom")
L(calendar(*CAL3, cols=1, rows=1, head=90), 1, 1.8, BLACK, 8, sfx="wood_high")
J3 = J()
WEEKS = ["这周", "上周", "两周前", "三周前"]


def flip_fn(c, k, t):
    """日历哗哗往回翻：第 2、3、4 拍各翻一页（每页 0.6 拍）。"""
    x, y, w, h = CAL3
    top = y - h / 2 + 90
    ph = h - 90
    n, f = 0, 0.0
    for i in range(3):
        g = _span(J3, 2 + i, 2.6 + i, t)
        if g >= 1:
            n = i + 1
        elif g > 0:
            f = g
            break
    cy = top + ph / 2
    cur = WEEKS[n + 1] if f > 0 else WEEKS[n]
    K.text(c, cur, x, cy, 90, "hand", RED if cur == WEEKS[-1] else BLACK)
    if f > 0:                                   # 正在翻起的一页：从下往上卷到页眉
        hh = ph * (1 - ease_in_out(f))
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 6, top + 4, w - 12, max(0, hh - 8)), K.paint("#FBFBF9"))
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 6, top + 4, w - 12, max(0, hh - 8)), K.paint(BLACK, 0.6, 5))
        if hh > 80:
            K.text(c, WEEKS[n], x, top + hh / 2, 90 * min(1, hh / ph), "hand", BLACK, 1 - f)
    return None


C(flip_fn, 2, 5, sfx="shaker")
H(3, "shaker")
H(4, "shaker")
T("那天她说了一句", 2650, 2780, 60, k0=5, k1=6.75, sfx="pop")

# 场景 4（第 9 小节起）= 音乐 drop：大“别”字砸下，箭头分岔
BIE = (1570, 3600)
MAN4 = (2400, 4470)
scene("他照做了啊", "倒带 · 三周前", (1800, R3, 0.75), shake=[0], flashes=[0])


def slam_fn(c, k, t):
    s = lerp(2.3, 1.0, ease_out(k))
    K.text(c, "别", BIE[0], BIE[1], 300 * s, "hand", RED, clamp01(k * 3))
    return None


C(slam_fn, 0, 0.45, sfx="kick")
L(cracks(BIE[0], BIE[1] + 170), 1, 1.6, RED, 8, sfx="wood_low")
T("总加班", 2020, 3630, 110, k0=2, k1=2.8, sfx="pop")
L(arrow((1600, 3800), (1300, 4020), -0.15, 40), 3, 3.8, GREEN, 10, sfx="wood_high")
T("少加班", 1250, 4110, 80, GREEN, k0=4, k1=4.8, sfx="pop")
L(arrow((2000, 3730), (2160, 4010), 0.1, 40), 5, 5.8, RED, 10, sfx="wood_high")
T("去打球", 2150, 4110, 80, RED, k0=6, k1=6.8, sfx="tom")
L(stick(*MAN4, 0.6, "up"), 7, 7.6, BLACK, 9, sfx="pop")
L(face(*MAN4, 0.6, "smile"), 7.6, 7.75, BLACK, 7)
L(ball(MAN4[0], 4195, 36), 7.75, 8.0, ORANGE, 8)

# ---------------------------------------------------------------- 书中观点（场景 5–7、10–11）

scene("有本书讲过", "非暴力沟通 · 书中观点", (XL, R4, Z))
L(book(950, 5170, 400, 240), 0, 0.9, sfx="wood_low")
T("非暴力沟通", 950, 4960, 70, GREEN, k0=1, k1=2.25, sfx="pop")
T("马歇尔 · 卢森堡", 950, 5360, 50, k0=3, k1=4.75, sfx="pop")
L(card4(), 5, 5.9, BLACK, 8, sfx="wood_high")
L(card_icons(), 6, 6.9, BLACK, 7, sfx="pop")


def light_fn(c, k, t):
    """点亮第四格“手”：琥珀色由中心铺满。"""
    x, y = CELLS[3], CARD[1]
    w, h = 210 * ease_out(k), CARD[3] - 12
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 14, 14, K.paint(ACC, 0.32))
    return None


C(light_fn, 7, 7.6, sfx="ding")
T("请求", CELLS[3], 5790, 50, ACC, k0=7, k1=7.8)

scene("说你要什么", "书中观点 · 第六章", (XR, R4, Z))
C(pao_fn(2650, 5100, 560, 230, "别总加班", 64), 0, 0.9, sfx="wood_high")
L(P((2490, 5145), (2810, 5140)), 2, 2.6, BLACK, 9, sfx="rim")
L(arrow((2650, 5290), (2650, 5420), 0, 36), 3, 3.7, BLACK, 9, sfx="wood_high")
L(bubble(2650, 5530, 560, 150, -1), 4, 4.6, BLUE, 8, sfx="pop")
T("多陪我吃晚饭", 2650, 5530, 60, BLUE, k0=4.6, k1=6.1)
L(check(3010, 5530, 40), 7, 7.6, GREEN, 10, sfx="ding")

DAYS = "一二三四五六日"
DX = [2290 + 120 * i for i in range(7)]
scene("越具体越好办", "书中观点 · 请求要具体", (XR, R5, Z))
T("哪天？几点？", 2650, 6400, 70, k0=0, k1=1.5, sfx="pop")
L(calendar(2650, 6800, 840, 360, cols=7, rows=2, head=110), 2, 2.9, BLACK, 7, sfx="wood_high")
for i, d in enumerate(DAYS):
    T(d, DX[i], 6675, 50, k0=3 + 0.12 * i, k1=3.3 + 0.12 * i, sfx="pop" if i == 0 else None)
L(circle(DX[2], 6740, 72), 4, 4.7, RED, 9, sfx="ding")
L(circle(DX[4], 6740, 72), 5, 5.7, RED, 9, sfx="ding")
T("七点前到家", 2700, 7110, 64, BLUE, k0=6, k1=7.25, sfx="pop")
L(join(clock(2410, 7110, 48), hands_at(2410, 7110, 48, 7, 0)), 7.3, 8.0, BLACK, 7)
H(7, "wood_high")

# ---------------------------------------------------------------- 换两个场景（场景 8–9，示意）

BOSS = (560, 7250)
scene("公司里：别出错", "换个场景 · 公司", (XL, R5, Z))
L(stick(*BOSS, 0.75, "point", tie=True), 0, 0.9, sfx="wood_high")
L(face(*BOSS, 0.75, "flat"), 0.9, 1.0)
L(bubble(830, 6560, 420, 140, -1), 1, 1.4, RED, 8, sfx="pop")
T("别再出错", 830, 6560, 60, RED, k0=1.4, k1=2.4)
L(P((650, 6565), (1010, 6555)), 3, 3.6, BLACK, 9, sfx="rim")
LIST, TICKS = checklist(1200, 6960, 300)
L(LIST, 4, 4.9, BLACK, 8, sfx="wood_high")
L(TICKS, 5, 5.8, GREEN, 9, sfx="pop")
T("提交前对一遍清单", 950, 7360, 56, BLUE, k0=6, k1=8, sfx="pop")

scene("家里：多关心我", "换个场景 · 家里", (XL, R6, Z))
L(bed(780, 8700, 520), 0, 0.9, sfx="wood_high")
L(bubble(900, 7935, 420, 140, -1), 1, 1.4, RED, 8, sfx="pop")
T("你多关心我", 900, 7935, 60, RED, k0=1.4, k1=2.65)
L(P((730, 7940), (1070, 7930)), 3, 3.6, BLACK, 9, sfx="rim")
L(bubble(900, 8175, 560, 150, -1), 5, 5.4, BLUE, 8, sfx="pop")
T("睡前陪我聊十分钟", 900, 8175, 54, BLUE, k0=5.4, k1=7.4)
L(join(alarm(1300, 8520, 55), rect(1300, 8640, 160, 110, 10)), 6, 6.8, BLACK, 8, sfx="wood_high")
T("十分钟", 1300, 8760, 52, RED, k0=7, k1=7.8, sfx="pop")

MAN10 = (2650, 8150)
scene("他说不，然后呢", "书中观点 · 请求还是命令", (XR, R6, Z))
L(stick(*MAN10, 0.6, "shrug"), 0, 0.8, sfx="wood_high")
L(face(*MAN10, 0.6, "flat"), 0.8, 0.95)
L(bubble(2960, 7905, 380, 130, -1), 1, 1.4, BLACK, 8, sfx="pop")
T("今天不行", 2960, 7905, 56, k0=1.4, k1=2.4)
L(arrow((2560, 8200), (2280, 8390), -0.1, 36), 2, 2.4, RED, 9, sfx="wood_high")
L(arrow((2740, 8200), (3020, 8390), 0.1, 36), 2.4, 2.8, BLUE, 9)
T("甩脸", 2250, 8480, 72, RED, k0=3, k1=3.8, sfx="rim")
T("＝命令", 2250, 8610, 56, RED, k0=4, k1=4.8, sfx="tom")
T("你那边怎么了？", 3010, 8480, 56, BLUE, k0=5, k1=6.75, sfx="pop")
T("＝请求", 3010, 8610, 56, BLUE, k0=7, k1=7.8, sfx="ding")

SHE11, HE11 = (2250, 10150), (3050, 10150)
scene("请他说一遍", "书中观点 · 请对方复述", (XR, R7, Z))
L(join(stick(*SHE11, 0.7, hair=True), face(*SHE11, 0.7, "smile")), 0, 0.9, sfx="wood_high")
L(join(stick(*HE11, 0.7), face(*HE11, 0.7, "smile")), 0.9, 1.0)
L(bubble(2470, 9420, 480, 140, -1), 1, 1.4, BLACK, 8, sfx="pop")
T("周五七点前回家", 2470, 9420, 56, k0=1.4, k1=3.15)
L(bubble(2850, 9750, 520, 140, 1), 4, 4.6, BLUE, 8, sfx="wood_high")
T("七点前，对吧？", 2850, 9750, 56, BLUE, k0=5, k1=6.75, sfx="pop")
L(ripples(3125, 9750, 3, 30, 40), 7, 7.6, BLUE, 7, sfx="shaker")
L(check(2140, 9700, 40), 7.6, 8.0, GREEN, 10)

# ---------------------------------------------------------------- 重来一次（场景 12–13）

scene("重来一次", "重来一次", (XL, R7, Z))
L(play(620, 9330, 70), 0, 0.8, GREEN, 9, sfx="wood_high")
T("三周前", 830, 9330, 64, k0=1, k1=1.8, sfx="pop")
j12 = J()
C(pao_fn(1000, 9780, 680, 380, "别总加班", 80, retract=(j12, 3, 4)), 2, 2.9, sfx="wood_low")
H(3, "ding")
T("周三周五七点前", 1000, 9800, 60, BLUE, k0=4, k1=5.75, sfx="pop")
T("回家吃饭，行吗？", 1000, 9900, 60, BLUE, k0=6, k1=8, sfx="pop")

SHE13, HE13 = (440, 11480), (1460, 11480)
scene("周三的饭桌", "改写后的结局", (XL, R8, Z))
L(join(P((580, 11300), (1320, 11300)), P((630, 11300), (630, 11480)), P((1270, 11300), (1270, 11480))), 0, 0.9,
  BLACK, 10, sfx="wood_high")
L(join(stick(*SHE13, 0.7, hair=True), stick(*HE13, 0.7)), 1, 1.8, BLACK, 9, sfx="pop")
L(join(face(*SHE13, 0.7, "smile"), face(*HE13, 0.7, "smile")), 1.8, 2.0, BLACK, 8)
L(join(bowl(820, 11300), bowl(1080, 11300)), 3, 3.9, BLACK, 8, sfx="pop")
T("周三 18:50", 950, 10820, 64, k0=5, k1=6.25, sfx="wood_high")
L(heart(950, 11000, 40), 7, 7.7, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：拉远看全板 → 推到评论区

FULL = (1800, 6100, 0.1)
COMMENT = (XR, R8, 0.8)
scene("评论区聊聊", "评论区见", FULL, bars=4)
J_END = J()
b.move(J_END, 4, COMMENT)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(comment_box(XR, R8 - 20, 1200, 520), 5, 5.9, BLACK, 8)
T("把一句“别……”改成“要……”", XR, R8 - 40, 60, RED, k0=6, k1=9.25, sfx="pop")
T("下一讲：朋友吐槽，你接的哪句？", XR, R8 + 110, 48, k0=9.5, k1=13.25)
H(10, "wood_high", 0.6)
L(underline(XR - 380, XR + 380, R8 + 160, 10, 36), 13.3, 14, BLACK, 6)
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "ask", "提请求", "说了“别总加班”，他报了球赛", ACC, b.shots,
                 [f"{BOOK}第六章“请求帮助”（转述；英文版第 6 章 Requesting That Which Would Enrich Life）",
                  "中译本：阮胤华译，华夏出版社"],
                 "说了“别总加班”|他报了【球赛】", SQUARE_SHOT,
                 ["书中观点均为转述（第六章“请求帮助”）：说想要对方做什么，少说不要什么；请求要具体明确；"
                  "可以请对方用自己的话复述一遍，确认听对了；请求和命令的分别，看对方说“不”时我们怎么反应——"
                  "会责怪、惩罚对方，那就是命令。上屏均为转述，不是逐字引文。",
                  "“别总加班 → 他报了周末球赛”的倒叙情节为示意：书中有类似例子，细节需核实，上屏不说是书里的故事。",
                  "公司（别再出错 → 提交前对一遍清单）、家里（多关心我 → 睡前陪我聊十分钟）、"
                  "“周三周五七点前回家吃饭”的改写与“周三 18:50”饭桌均为据书中思路整理的示意，不指向任何具体公司或个人；"
                  "时间与日子为示意，不是数据。",
                  "人物均为火柴人；卢森堡只写名字，不画肖像。话泡泡“小泡”与四格卡为本系列视觉角色。"],
                 tags="#恋爱 #职场沟通")
    return b.attach(ep)
