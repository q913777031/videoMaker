"""05 听出需要（白板手绘版）：“你又加班”，到底想说啥？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：场景 1 为 2 小节，场景 2–13 各 3 小节，场景 14 为 4 小节）。
叙事（形式 H 对话改写）：晚上十点进门，对象一句“你又加班”像带刺的小泡飞过来 → 顶回去“我加班还有错？”，两个带刺小泡相撞，
卧室门“砰” → drop：带刺小泡被剥开，里面是一节快没电的电池（书中观点，第五章：批评、指责常是在拐着弯说自己没被满足的需要）→
亮书，四格卡点亮“需要” → 同一台翻译机连翻五句冲话（对象三句、同事一句、领导一句），左红右蓝，中间都有一节缺电的电池 →
拉远看整列 → 做法：听到刺先找电池（据书中思路）；把听到的需要说出来请对方确认（第七章思路），小泡的刺缩回去 → 评论区互动。
书中观点为转述（马歇尔·卢森堡《非暴力沟通》，阮胤华译，华夏出版社；第五章 感受的根源、第七章 用全身心倾听）；
所有原话、改写与场景均为示意，据书中思路整理。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, clock,
                               desk, doc, face, hands_at, join, marker, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#2F8F83"
SQUARE_SHOT = 12                # 场景 13：说出听到的需要，对象收刺变笑脸
COVER_SHOT = 3                  # 竖版封面：场景 4，带刺小泡剥开露出电池

b = Board(size=(3600, 10500))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


# ---------------------------------------------------------------- 本讲画法：话泡泡“小泡”、电池、翻译机

def spikes_along(contour, cx, cy, length, step=85, base=16, skip=None) -> skia.Path:
    """沿轮廓等距长出三角刺（朝外）。length 为刺长，0 时不出刺。"""
    out = skia.Path()
    if length < 1:
        return out
    pm = skia.PathMeasure(contour, False)
    total = pm.getLength()
    n = max(8, int(total / step))
    for i in range(n):
        pos, tan = pm.getPosTan((i + 0.5) * total / n)
        px, py, tx, ty = pos.x(), pos.y(), tan.x(), tan.y()
        nx, ny = ty, -tx
        if nx * (px - cx) + ny * (py - cy) < 0:
            nx, ny = -nx, -ny
        if skip and skip(px, py):
            continue
        out.addPath(P((px - tx * base, py - ty * base), (px + nx * length, py + ny * length),
                      (px + tx * base, py + ty * base)))
    return out


def pao_face(fx, fy, mood="sad", s=1.0) -> skia.Path:
    """小泡的脸：两点眼睛 + 一张小嘴。"""
    p = skia.Path()
    p.addCircle(fx - 16 * s, fy - 16 * s, 5 * s)
    p.addCircle(fx + 16 * s, fy - 16 * s, 5 * s)
    if mood == "smile":
        p.addArc(skia.Rect.MakeXYWH(fx - 18 * s, fy - 4 * s, 36 * s, 26 * s), 20, 140)
    else:
        p.addArc(skia.Rect.MakeXYWH(fx - 18 * s, fy + 8 * s, 36 * s, 24 * s), 200, 140)
    return p


def pao(x, y, w, h, tail=-1, spike=45.0, mood="sad", fdx=None, fs=1.0) -> skia.Path:
    """话泡泡“小泡”：圆角泡 + 尾巴 + 外圈红刺（spike=0 时圆滚滚）+ 左侧小脸。"""
    body = rect(x, y, w, h, 40)
    parts = [body]
    t0, t1 = x + tail * w * 0.1, x + tail * w * 0.38
    if tail:
        tl = skia.Path()
        tl.moveTo(x + tail * w * 0.25, y + h / 2)
        tl.lineTo(t1, y + h / 2 + 60)
        tl.lineTo(t0, y + h / 2)
        parts.append(tl)
    lo, hi = min(t0, t1) - 20, max(t0, t1) + 20
    parts.append(spikes_along(body, x, y, spike,
                              skip=lambda px, py: tail and py > y + h / 2 - 2 and lo <= px <= hi))
    parts.append(pao_face(x + (fdx if fdx is not None else -w / 2 + 55 * fs), y, mood, fs))
    return join(*parts)


def ball(x, y, r, spike=55.0) -> skia.Path:
    """一团带刺的冲话（刺球）。"""
    body = circle(x, y, r)
    return join(body, spikes_along(body, x, y, spike, step=70, base=18), pao_face(x, y - 20, "sad", 1.6))


def battery(x, y, w=110, h=50) -> skia.Path:
    """电池：外壳 + 正极小头 + 三道分格（四格电量）。"""
    parts = [rect(x, y, w, h, max(6, h * 0.18)), rect(x + w / 2 + w * 0.05, y, w * 0.1, h * 0.4, 3)]
    for i in (1, 2, 3):
        xx = x - w / 2 + w * i / 4
        parts.append(P((xx, y - h / 2 + h * 0.18), (xx, y + h / 2 - h * 0.18)))
    return join(*parts)


def low_cell_fn(x, y, w=110, h=50, color=RED, blink=True):
    """电池最左一格亮着（快没电），一直闪。"""
    def fn(c, k, t):
        a = 0.85 if not blink else 0.35 + 0.55 * (0.5 + 0.5 * math.cos(t * 2 * math.pi * 1.6))
        K.rr(c, x - w / 2 + w / 8, y, w / 4 - w * 0.08, h - h * 0.36, 3, color, a * clamp01(k * 3))
        return None

    return fn


def machine(x, y) -> skia.Path:
    """翻译机：机身 + 天线 + 电池窗 + 两个旋钮 + 进出箭头。(x, y) 为机身中心。"""
    dial = join(circle(x - 45, y + 70, 18), P((x - 45, y + 70), (x - 45, y + 54)),
                circle(x + 45, y + 70, 18), P((x + 45, y + 70), (x + 58, y + 60)))
    return join(rect(x, y, 190, 240, 26), P((x, y - 120), (x, y - 168)), circle(x, y - 182, 14),
                rect(x, y - 30, 150, 90, 12), dial,
                arrow((x - 175, y), (x - 102, y), 0, 24), arrow((x + 102, y), (x + 178, y), 0, 24))


def door(x, y, w=220, h=400) -> skia.Path:
    """门：(x, y) 为地面中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                circle(x + w / 2 - 35, y - h / 2, 12))


def eye_icon(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 70 * s, y)
    p.quadTo(x, y - 60 * s, x + 70 * s, y)
    p.quadTo(x, y + 60 * s, x - 70 * s, y)
    return join(p, circle(x, y, 20 * s))


def heart(x, y, r=55) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def hand_icon(x, y, s=1.0) -> skia.Path:
    """伸出的手：掌心 + 四根手指 + 拇指（朝右伸）。"""
    parts = [rect(x - 20 * s, y, 80 * s, 70 * s, 18 * s)]
    for i, dy in enumerate((-26, -9, 8, 25)):
        ln = (52, 60, 56, 44)[i]
        parts.append(P((x + 20 * s, y + dy * s), (x + (20 + ln) * s, y + dy * s)))
    parts.append(P((x - 10 * s, y - 35 * s), (x + 15 * s, y - 62 * s)))
    return join(*parts)


def open_hand(x, y) -> skia.Path:
    """掌心朝上、伸向左边的手 + 胳膊（(x, y) 为掌心）。"""
    palm = skia.Path()
    palm.moveTo(x + 70, y - 10)
    palm.quadTo(x + 10, y + 60, x - 80, y + 20)
    parts = [palm, P((x + 70, y - 10), (x + 230, y + 120)), P((x + 40, y + 50), (x + 200, y + 170))]
    for i in range(4):
        fy = y + 20 - i * 14
        parts.append(P((x - 80 + i * 22, fy + i * 4), (x - 150 + i * 30, fy - 30 - i * 6)))
    parts.append(P((x + 30, y - 2), (x - 10, y - 60)))
    return join(*parts)


def burst(x, y, r=90) -> skia.Path:
    parts = []
    for i in range(8):
        a = i / 8 * 2 * math.pi + 0.2
        parts.append(P((x + math.cos(a) * r * 0.45, y + math.sin(a) * r * 0.45), (x + math.cos(a) * r, y + math.sin(a) * r)))
    return join(*parts)


def ink(c, path, color, width=9, alpha=1.0):
    c.drawPath(path, marker(color, width, alpha))
    c.drawPath(path, K.paint(color, 0.22 * alpha, width * 0.45, blur=1.2))


def mix_hex(a, b_, f):
    ca, cb = [int(a[i:i + 2], 16) for i in (1, 3, 5)], [int(b_[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(lerp(u, v, f)):02X}" for u, v in zip(ca, cb))


def pao_text(c, lines, tx, y, size, color, alpha=1.0):
    n = len(lines)
    for i, ln in enumerate(lines):
        K.text(c, ln, tx, y + (i - (n - 1) / 2) * size * 1.25, size, "hand", color, alpha)


def PT(lines, x, y, size, color, k0, k1, sfx="pop"):
    """在小泡里分行写字（按字数分配时长）。"""
    n = sum(len(s) for s in lines)
    k = k0
    for i, s in enumerate(lines):
        d = (k1 - k0) * len(s) / n
        T(s, x, y + (i - (len(lines) - 1) / 2) * size * 1.25, size, color, k0=k, k1=k + d, sfx=sfx if i == 0 else None)
        k += d


# ---------------------------------------------------------------- 开局：晚上十点，一句“你又加班”（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


HERO = (1150, 1260)             # 主角（脚底）
scene("晚上十点到家", "开局 · 进门", (1000, 900, 0.85), bars=2)
L(door(650, 1260, 240, 420), 0, 0.9, sfx="wood_low")
L(join(clock(1000, 560, 85), hands_at(1000, 560, 85, 10, 0)), 1, 1.9, BLACK, 9, sfx="wood_high")
T("22:00", 1260, 560, 70, RED, k0=2, k1=3.2, sfx="pop")
L(stick(*HERO, 0.8, "down"), 3, 3.8, sfx="wood_high")
L(face(*HERO, 0.8, "flat"), 3.8, 4.0)
L(join(P((1206, 1164), (1215, 1155)), rect(1240, 1195, 90, 70, 10)), 4, 4.8, BLUE, 9, sfx="pop")
T("电脑包", 1360, 1120, 50, k0=5, k1=5.8)

SHE = (2150, 1260)              # 对象（脚底）
FLY0, FLY1 = (2010, 820), (1480, 760)


def fly_fn(c, k, t):
    """对象的带刺小泡从嘴边冒出，飞到主角头顶。"""
    g = ease_out(clamp01(k / 0.2))
    f = ease_in_out(clamp01((k - 0.15) / 0.85))
    x, y = lerp(FLY0[0], FLY1[0], f), lerp(FLY0[1], FLY1[1], f) - 70 * math.sin(f * math.pi)
    with K.at(c, x, y, -8 * math.sin(f * math.pi * 2), 0.3 + 0.7 * g):
        ink(c, pao(0, 0, 420, 220, 1, 45, "sad"), RED, 9)
        pao_text(c, ["你又加班"], 40, 0, 60, RED)
    return None


scene("你又加班", "开局 · 进门一句话", (1700, 900, 0.85), shake=[3])
L(stick(*SHE, 0.8, "down", hair=True), 0, 0.8, sfx="wood_high")
L(face(*SHE, 0.8, "sad"), 0.8, 1.0)
C(1, 3, fly_fn, sfx="pop")
L(burst(1180, 960, 110), 3, 3.6, RED, 8, sfx="rim")
L(face(*HERO, 0.8, "sad"), 4, 4.6, RED, 8, sfx="wood_low")
T("！", 1040, 900, 80, RED, k0=5, k1=5.8, sfx="pop")

ME3, HIS = (2560, 1260), (2680, 620)


def her_fn(c, k, t):
    """另一个带刺小泡从卧室方向冲过来，跟主角的小泡撞上。"""
    f = ease_in_out(k)
    with K.at(c, lerp(3700, 3155, f), 620 + 20 * math.sin(f * math.pi)):
        ink(c, pao(0, 0, 360, 200, 1, 45, "sad"), RED, 9)
        pao_text(c, ["哼！"], 40, 0, 64, RED)
    return None


scene("我加班还有错", "开局 · 顶回去", (2900, 850, 0.85), shake=[5, 7])
L(stick(*ME3, 0.8, "shrug"), 0, 0.8, sfx="wood_high")
L(face(*ME3, 0.8, "sad"), 0.8, 1.0)
L(pao(*HIS, 500, 220, -1, 45, "sad", fdx=-200), 1, 1.9, RED, 9, sfx="pop")
T("我加班还有错？", HIS[0] + 35, HIS[1], 54, RED, k0=2, k1=3.75, sfx="pop")
C(4, 5, her_fn, sfx="shaker")
L(burst(2952, 620, 100), 5, 5.6, RED, 9, sfx="kick")
L(join(door(3380, 1260), P((3235, 900), (3205, 880)), P((3235, 990), (3195, 990)), P((3235, 1080), (3205, 1100))),
  6, 6.8, BLACK, 9, sfx="wood_low")
T("砰！", 3360, 1000, 84, RED, k0=7, k1=7.8, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 4–5）

PX, PY = 2200, 2150             # drop：大号带刺小泡


def peel_fn(c, k, t):
    """第 0 拍大泡弹出，第 1–2 拍从中间撕开、两半往外翻，露出里面的电池。"""
    g = ease_out(clamp01(k / 0.2))
    s = 0.4 + 0.6 * g + 0.08 * math.sin(clamp01(k / 0.3) * math.pi)
    f = ease_in_out(clamp01((k - 0.5) / 0.4))
    zz = P(*[(0 if i % 2 == 0 else (-14 if i % 4 == 1 else 14), -240 + i * 40) for i in range(13)])
    for side in (-1, 1):
        c.save()
        c.translate(PX + side * 230 * f, PY + 30 * f)
        c.rotate(side * 12 * f)
        c.scale(s, s)
        if f > 0:
            c.clipRect(skia.Rect.MakeLTRB(-600, -400, 0, 400) if side < 0 else skia.Rect.MakeLTRB(0, -400, 600, 400))
        ink(c, pao(0, 0, 860, 480, 0, 50, "sad", fdx=-360, fs=1.8), RED, 12)
        pao_text(c, ["你又加班"], 20, 0, 120, RED)
        if f > 0:
            ink(c, zz, RED, 8, f)
        c.restore()
    return None


scene("抱怨里有需要", "书中观点 · 第五章", (PX, 2200, 0.75), shake=[0], flashes=[0])
C(0, 2, peel_fn, sfx="kick")
H(1, "rim", 0.8, "撕开")
L(battery(PX, PY + 20, 330, 150), 2, 2.9, BLACK, 11, sfx="wood_low")
C(3, 3.6, low_cell_fn(PX, PY + 20, 330, 150), sfx="ding")
T("冲话里，藏着需要", PX, 2560, 100, k0=5, k1=7, sfx="pop")
L(underline(2000, 2400, 2630, 14, 40), 7, 7.8, RED, 9, sfx="wood_high")

CARD = (2200, 3700)
CELLS = [CARD[0] - 420 + 280 * i for i in range(4)]


def cell_fn(c, k, t):
    K.rr(c, CELLS[2], CARD[1], 250, 300, 20, GREEN, 0.18 * ease_out(k))
    return None


scene("有本书讲过", "非暴力沟通 · 书中观点", (2200, 3450, 0.85))
L(book(1850, 3150, 380, 250), 0, 0.9, sfx="wood_low")
T("《非暴力沟通》", 2460, 3110, 66, GREEN, k0=1, k1=2.75, sfx="pop")
L(join(rect(*CARD, 1120, 330, 28), *[P((x, CARD[1] - 150), (x, CARD[1] + 150)) for x in (CELLS[0] + 140, CELLS[1] + 140,
                                                                                         CELLS[2] + 140)]),
  2, 2.9, BLACK, 9, sfx="wood_high")
L(join(eye_icon(CELLS[0], 3640, 0.9), heart(CELLS[1], 3650, 48), battery(CELLS[2], 3640, 130, 60),
       hand_icon(CELLS[3] - 20, 3640, 1.0)), 3, 3.9, BLACK, 8, sfx="pop")
for n, w in enumerate(("观察", "感受", "需要", "请求")):
    T(w, CELLS[n], 3790, 50, GREEN if n == 2 else BLACK, k0=4 + n * 0.8, k1=4.8 + n * 0.8, sfx="pop" if n == 0 else None)
C(7, 7.8, cell_fn, sfx="ding")
L(check(CELLS[2] + 95, 3570, 40), 7.2, 8.0, GREEN, 10)
C(7, 7.6, low_cell_fn(CELLS[2], 3640, 130, 60))

# ---------------------------------------------------------------- 翻译机：五句冲话（场景 6–10），左右交错排成一列

ROWS = [  # (列中心 x, 行中心 y, 字幕, 页眉, 原话, 改写, 电量格颜色)
    (1050, 4900, "翻译一下", "据书中思路 · 翻译机", ["你又加班"], ["我想多跟你", "待一会儿"], RED),
    (2550, 5500, "你从来不管孩子", "据书中思路 · 对象说", ["你从来", "不管孩子"], ["我想有人", "搭把手"], RED),
    (1050, 6100, "你根本不听我说", "据书中思路 · 对象说", ["你根本", "不听我说"], ["我想被", "认真听一回"], ORANGE),
    (2550, 6700, "这活又给我", "据书中思路 · 同事说", ["这活怎么", "又给我"], ["我也想喘口气", "排个公平"], RED),
    (1050, 7300, "小事都办不好", "据书中思路 · 领导说", ["这点小事", "都办不好"], ["我要这事", "明天稳稳落地"], RED),
]


def speaker(n, cx, y):
    """各行说话的人：对象（长发）、对象和孩子、同事和工位、领导（领带）和会议桌。"""
    x, f = cx - 600, y + 340
    if n in (0, 2):
        return join(stick(x, f, 0.45, "down", hair=True), face(x, f, 0.45, "sad"))
    if n == 1:
        return join(stick(x, f, 0.45, "down", hair=True), face(x, f, 0.45, "sad"), stick(x + 100, f, 0.28, "up"))
    if n == 3:
        return join(stick(x, f, 0.45, "point"), face(x, f, 0.45, "sad"), desk(cx - 330, y + 290, 200))
    return join(stick(x, f, 0.45, "point", tie=True), face(x, f, 0.45, "sad"),
                P((cx - 470, y + 270), (cx - 150, y + 270)), P((cx - 440, y + 270), (cx - 440, y + 360)),
                P((cx - 180, y + 270), (cx - 180, y + 360)), doc(cx - 300, y + 222, 70, 80, 2))


for n, (cx, y, cap, tag, orig, new, cell) in enumerate(ROWS):
    scene(cap, tag, (cx, y + 80, 0.78))
    L(join(pao(cx - 430, y, 420, 240, -1, 45, "sad"), speaker(n, cx, y)), 0, 0.9, RED, 9, sfx="wood_high")
    PT(orig, cx - 390, y, 52, RED, 1, 1 + max(0.8, 0.25 * sum(map(len, orig))) if len(orig) == 1 else 2.8)
    if n == 0:
        T("翻译机", cx, y - 235, 52, BLUE, k0=2, k1=2.8, sfx="pop")
    L(machine(cx, y), 3, 3.9, BLACK, 9, sfx="wood_high")
    L(battery(cx, y - 30), 4, 4.7, BLACK, 7, sfx="pop")
    C(4.7, 5, low_cell_fn(cx, y - 30, color=cell))
    L(pao(cx + 430, y, 420, 240, 1, 0, "smile"), 5, 5.9, BLUE, 9, sfx="wood_high")
    PT(new, cx + 470, y, 52, BLUE, 6, 8.0)

# ---------------------------------------------------------------- 拉远：每句冲话后面都有一节缺电的电池（场景 11，封面镜头）

scene("话越冲，越着急", "据书中思路 · 拉远看", (1800, 6140, 0.30))
for n, (cx, y, *_rest) in enumerate(ROWS):
    L(circle(cx, y - 30, 120), n, n + 0.8, RED, 14, sfx="tom")
T("冲话背后，都缺电", 2550, 7330, 150, RED, k0=5, k1=7, sfx="pop")
L(underline(1950, 3150, 7440, 22, 60), 7, 7.8, RED, 14, sfx="ding")

# ---------------------------------------------------------------- 做法（场景 12–13）

BX, BY = 1150, 8450
HX, HY = 1700, 8520


def pull_fn(c, k, t):
    """电池从刺球里被拽出来，落到手心上方。"""
    f = ease_in_out(k)
    x, y = lerp(BX, HX - 40, f), lerp(BY + 60, HY - 120, f) - 90 * math.sin(f * math.pi)
    a = clamp01(k * 4)
    ink(c, battery(x, y, 180, 80), BLACK, 9, a)
    if k >= 1:
        low_cell_fn(x, y, 180, 80)(c, 1, t)
    return None


scene("听到刺，找电池", "做法 · 据书中思路", (1300, 8500, 0.85))
L(ball(BX, BY, 220), 0, 0.9, RED, 10, sfx="wood_high")
L(open_hand(HX, HY), 1, 1.9, BLACK, 9, sfx="wood_low")
C(2, 3, pull_fn, sfx="shaker")
H(3, "ding", 0.8, "电池落到手上")
T("他缺的是什么？", 1300, 8900, 84, BLUE, k0=5, k1=6.75, sfx="pop")
L(underline(1010, 1590, 8970), 7, 7.8, BLUE, 9, sfx="wood_high")

ME13, SHE13 = (2300, 9000), (3100, 9000)
SP = (2950, 8350)


def soften_fn(c, k, t):
    """对象的带刺小泡：第 2 拍冒出；第 7–8 拍刺一根根缩回去，红变蓝，嘴角上扬，话变成“嗯，是”。"""
    g = ease_out(clamp01(k / 0.1))
    f = ease_in_out(clamp01((k - 5 / 6) * 6))
    col = mix_hex(RED, BLUE, f)
    with K.at(c, *SP, 0, 0.3 + 0.7 * g):
        ink(c, pao(0, 0, 380, 200, 1, 45 * (1 - f), "smile" if f > 0.5 else "sad"), col, 9)
        pao_text(c, ["嗯，对"] if f > 0.5 else ["你又加班"], 40, 0, 56, col)
    return None


def she_face_fn(c, k, t):
    ink(c, face(*SHE13, 0.75, "smile" if k > 6.5 / 7 else "sad"), BLACK, 10)
    return None


scene("说出你听到的", "做法 · 第七章思路", (2700, 8500, 0.85))
L(join(stick(*ME13, 0.75, "point"), face(*ME13, 0.75, "smile")), 0, 0.9, sfx="wood_high")
L(stick(*SHE13, 0.75, "down", hair=True), 1, 1.8, sfx="wood_low")
C(1, 8, she_face_fn)
C(2, 8, soften_fn, sfx="rim")
L(pao(2380, 8530, 560, 220, -1, 0, "smile", fdx=-230), 3, 3.8, BLUE, 9, sfx="pop")
PT(["你是想多点时间", "一起吃饭吗？"], 2420, 8530, 52, BLUE, 4, 7.0)
H(7, "ding", 0.9, "刺缩回去")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 5250, 0.145)
VC = (1800, 9900, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, VC, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(bubble(1800, 9880, 1250, 400, -1), 5, 5.9, BLUE, 9, sfx="wood_high")
T("冲你的那句话，翻译一下？", 1800, 9810, 72, RED, k0=6, k1=9, sfx="pop")
T("下一讲：说了“别总加班”，他报了球赛", 1800, 9960, 50, k0=9, k1=13, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "needs", "听出需要", "“你又加班”，到底想说啥？", ACC, b.shots,
                 [f"{BOOK}第五章 感受的根源、第七章 用全身心倾听（转述）",
                  "中译本：阮胤华译，华夏出版社"],
                 "“你又加班”|到底想说【啥】", COVER_SHOT,
                 ["书中观点均为转述：别人的言行是刺激，感受的根源在自己的需要；对别人的批评、指责，往往是在拐着弯说自己"
                  "没被满足的需要（第五章 感受的根源）；倾听时把注意力放在对方的感受和需要上，可以说出自己听到的感受和需要，"
                  "请对方确认（第七章 用全身心倾听）。出处：马歇尔·卢森堡《非暴力沟通》（阮胤华译，华夏出版社；"
                  "Marshall B. Rosenberg, Nonviolent Communication: A Language of Life）。上屏均为转述，不是逐字引文。",
                  "晚上十点进门、对象说“你又加班”、顶嘴和摔门为家庭场景示意；“这活怎么又给我”“这点小事都办不好”为工位与"
                  "会议室场景示意，不指向任何具体公司或个人；时间为示意。",
                  "五句原话与改写（“我想多跟你待一会儿”“我想有人搭把手”“我想被认真听一回”“我也想喘口气，排个公平”"
                  "“我要这事明天稳稳落地”）均为示意，据书中思路整理；翻译机、电池（缺电 = 需要没满足）、刺球是系列视觉比喻。",
                  "两步做法（听到刺先问他缺什么；把听到的需要说出来，请对方确认，如“你是想多点时间一起吃饭吗？”）"
                  "为据书中第五章、第七章思路整理的建议。"],
                 tags="#恋爱 #家庭沟通")
    return b.attach(ep)
