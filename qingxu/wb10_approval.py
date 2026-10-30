"""10 往下挖（白板手绘版）：别人一不满意，你就慌？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒。
叙事（形式 K 层层下挖，本系列自创）：白板竖着长，相机一路往下走——
地面上是一件小事（客户只回了一个“嗯。”，小周改方案改到凌晨一点）→ 亮书：书里有个追问的办法，往下挖 →
★drop：钻头一口气穿过四层土，砸到最底下那块石头「人人都得满意」→
往回走，一层一层看：客户不满意 → 领导会觉得我不行 → 大家都会看不起我 → 没人认可，我就一文不值，连到石头 →
书中观点（这块石头叫沉默的假设，平时看不见，一碰就疼；第 11 章认同上瘾：把认可当成价值的前提，怎么都不够）→
在石头旁边长出一朵白云：有人不满意，我照样值得 → 做法：慌了连问三次“那又怎样”，写下挖到的那句 →
这一季的工具排一排 → 拉远看全板 → 评论区 + 健康提醒。
系列视觉角色：小周（戴工牌）、乌云状念头云（红字）与改写后的白云（蓝字）。
书中观点为转述：戴维·伯恩斯《伯恩斯新情绪疗法》第 10 章（向下箭头法、沉默的假设）、第 11 章（认同上瘾）；
每层的话、客户与领导的场景为现实场景示意，“连问三次”为据书中思路整理的做法。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, circle, clock, desk, face,
                               hands_at, join, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out

from .common import BOOK, episode

ACC = "#8A5A2B"                 # 本讲主色：泥土棕
SQUARE_SHOT = 3                 # 场景 4：钻到底，小周站在写着「人人都得满意」的石头上

b = Board(size=(7200, 13000))

X0 = 3600                       # 竖井中线
WALL = 350                      # 竖井半宽：井壁在 X0 ± 350
GY = 2500                       # 地面
LAYER_H = 1200
YT = [GY + i * LAYER_H for i in range(4)]       # 四层土的上沿：2500 / 3700 / 4900 / 6100
ROCK_TOP, ROCK = 7300, (X0, 7560, 1000, 520)    # 最底下那块石头 (cx, cy, w, h)


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def J():
    return len(b.shots) - 1


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def cloud(x, y, w, h, bumps=10) -> skia.Path:
    """念头云轮廓：椭圆外缘一圈鼓包。"""
    pts = []
    for i in range(96):
        a = i / 96 * 2 * math.pi
        r = 0.9 + 0.1 * abs(math.sin(a * bumps / 2))
        pts.append((x + w / 2 * r * math.cos(a), y + h / 2 * r * math.sin(a)))
    return P(*pts, close=True)


def ring(x, y, w, h, n=34) -> skia.Path:
    """乌云的涂黑边：沿云边来回折的一圈短线。"""
    pts = []
    for i in range(n * 2 + 1):
        a = i / (n * 2) * 2 * math.pi
        r = 0.9 if i % 2 == 0 else 0.76
        pts.append((x + w / 2 * r * math.cos(a), y + h / 2 * r * math.sin(a)))
    return P(*pts)


def badge(x, y, s=1.0) -> skia.Path:
    """小周的工牌：挂绳 + 胸前小卡。(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 16 * s, hy + 48 * s), (x, hy + 112 * s), (x + 16 * s, hy + 48 * s)),
                rect(x, hy + 135 * s, 40 * s, 46 * s, 6 * s))


def zhou(x, y, s=0.75, arms="down", mood="flat"):
    """小周（戴工牌）：返回（身体 + 工牌，五官）。"""
    return join(stick(x, y, s, arms), badge(x, y, s)), face(x, y, s, mood)


def phone(x, y, w=140, h=230) -> skia.Path:
    return join(rect(x, y, w, h, 14 if w < 200 else 36), P((x - w * 0.15, y + h / 2 - h * 0.08),
                                                           (x + w * 0.15, y + h / 2 - h * 0.08)))


def lamp(x, y, s=1.0) -> skia.Path:
    """台灯：(x, y) 为底座中点。"""
    return join(P((x - 60 * s, y), (x + 60 * s, y)), P((x, y), (x - 40 * s, y - 150 * s), (x + 30 * s, y - 230 * s)),
                P((x - 20 * s, y - 250 * s), (x + 110 * s, y - 210 * s), (x + 60 * s, y - 160 * s), close=True),
                P((x + 70 * s, y - 150 * s), (x + 85 * s, y - 115 * s)), P((x + 100 * s, y - 160 * s), (x + 130 * s, y - 135 * s)))


def shovel(x0, y0, x1, y1) -> skia.Path:
    """铲子：把手顶端 (x0, y0)，铲头尖 (x1, y1)。"""
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    bx, by = x1 - ux * 110, y1 - uy * 110
    return join(P((x0 - px * 30, y0 - py * 30), (x0 + px * 30, y0 + py * 30)), P((x0, y0), (bx, by)),
                P((bx - px * 45, by - py * 45), (bx + px * 45, by + py * 45), (x1 + px * 18, y1 + py * 18),
                  (x1 - px * 18, y1 - py * 18), close=True))


def ground(y, x0, x1) -> skia.Path:
    parts = [P((x0, y), (x1, y))]
    for i in range(int((x1 - x0) / 140)):
        gx = x0 + 60 + i * 140
        if abs(gx - X0) < WALL + 30:
            continue
        parts.append(P((gx, y), (gx - 18, y - 34)))
        parts.append(P((gx + 16, y), (gx + 30, y - 28)))
    return join(*parts)


def strata(y) -> skia.Path:
    """一层土的分界：井壁两侧的波浪线 + 几颗小石子。"""
    parts = [underline(X0 - 1700, X0 - WALL - 10, y, 16, 60), underline(X0 + WALL + 10, X0 + 1700, y, 16, 60)]
    for dx, dy, r in ((-1250, 160, 18), (-800, 260, 12), (-1500, 420, 14), (900, 190, 16), (1350, 330, 12),
                      (1100, 520, 18)):
        parts.append(circle(X0 + dx, y + dy, r))
    return join(*parts)


def rock(x, y, w, h) -> skia.Path:
    pts = [(-0.5, 0.1), (-0.42, -0.32), (-0.2, -0.5), (0.12, -0.46), (0.36, -0.5), (0.5, -0.12), (0.46, 0.34),
           (0.2, 0.5), (-0.16, 0.48), (-0.44, 0.38)]
    return join(P(*[(x + w * a, y + h * c) for a, c in pts], close=True),
                P((x - w * 0.3, y + h * 0.3), (x - w * 0.18, y + h * 0.36)), P((x + w * 0.28, y - h * 0.3),
                                                                               (x + w * 0.36, y - h * 0.18)))


def rays(x, y, r0, r1, n=8, a0=0.0) -> skia.Path:
    parts = []
    for i in range(n):
        a = a0 + i / n * 2 * math.pi
        parts.append(P((x + r0 * math.cos(a) * 1.5, y + r0 * math.sin(a)), (x + r1 * math.cos(a) * 1.5, y + r1 * math.sin(a))))
    return join(*parts)


def cup(x, y, w=150, h=180) -> skia.Path:
    """杯子（杯底有条裂缝）：(x, y) 为杯身中心。"""
    return join(P((x - w / 2, y - h / 2), (x - w * 0.36, y + h / 2), (x + w * 0.36, y + h / 2), (x + w / 2, y - h / 2)),
                P((x - w / 2 - 10, y - h / 2), (x + w / 2 + 10, y - h / 2)),
                P((x - 10, y + h / 2), (x + 4, y + h / 2 - 26), (x - 6, y + h / 2 - 48)))


def drops(x, y) -> skia.Path:
    parts = []
    for i, (dx, dy) in enumerate(((0, 0), (-14, 70), (10, 140))):
        cx, cy = x + dx, y + dy
        parts.append(P((cx, cy - 22), (cx - 12, cy + 2), (cx, cy + 14), (cx + 12, cy + 2), close=True))
    return join(*parts)


def tag(x, y, w=200, h=120) -> skia.Path:
    """价签：(x, y) 为中心，左侧尖头带孔。"""
    return join(P((x - w / 2, y), (x - w / 2 + 50, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2),
                  (x - w / 2 + 50, y + h / 2), close=True), circle(x - w / 2 + 40, y, 10))


def heads(x, y, r=28) -> skia.Path:
    """三个围观的小脑袋，嘴角往下。"""
    parts = []
    for dx in (-72, 0, 72):
        parts.append(circle(x + dx, y, r))
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(x + dx - 12, y + 6, 24, 18), 200, 140)
        parts.append(arc)
    return join(*parts)


def note(x, y, w=340, h=340) -> skia.Path:
    """便签：右下角折起。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 60), (x + w / 2 - 60, y + h / 2),
                  (x - w / 2, y + h / 2), close=True), P((x + w / 2, y + h / 2 - 60), (x + w / 2 - 60, y + h / 2 - 60),
                                                        (x + w / 2 - 60, y + h / 2)))


def grid_list(x, y) -> skia.Path:
    """十格清单：纸 + 两列五行小方格。"""
    parts = [rect(x, y, 170, 230, 10)]
    for r in range(5):
        for c in range(2):
            parts.append(rect(x - 38 + c * 76, y - 80 + r * 40, 26, 26, 4))
    return join(*parts)


def column_card(x, y) -> skia.Path:
    """三栏卡。"""
    return join(rect(x, y, 230, 160, 12), P((x - 115, y - 40), (x + 115, y - 40)), P((x - 38, y - 80), (x - 38, y + 80)),
                P((x + 38, y - 80), (x + 38, y + 80)))


def bars_icon(x, y) -> skia.Path:
    """两根柱子：预想有多难 vs 真做起来。"""
    return join(P((x - 110, y + 90), (x + 110, y + 90)), rect(x - 50, y - 10, 60, 200, 6), rect(x + 50, y + 50, 60, 80, 6))


def high_jump(x, y) -> skia.Path:
    """跳高架，横杆放得很低。"""
    return join(P((x - 100, y + 90), (x - 100, y - 110)), P((x + 100, y + 90), (x + 100, y - 110)),
                P((x - 100, y + 30), (x + 100, y + 30)), P((x - 130, y + 90), (x - 70, y + 90)),
                P((x + 70, y + 90), (x + 130, y + 90)))


def glow_fn(x, y, w, h, color="#F2C14E", alpha=0.32):
    def fn(c, k, t):
        c.drawOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), K.paint(color, alpha * k, blur=50))
        return None

    return fn


# ---------------------------------------------------------------- 地面上：一件小事（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

C1 = (X0 - 650, 1000)
scene("就回了一个嗯", "灵魂拷问", (*C1, 0.85), bars=2)
PH = (C1[0] - 200, 920)
L(phone(*PH, 380, 620), 0, 0.9, BLACK, 9, sfx="wood_high")
T("客户", PH[0], 700, 50, k0=1, k1=1.8, sfx="pop")
L(bubble(PH[0], 900, 240, 130, -1), 2, 2.5, BLACK, 8, sfx="pop")
T("嗯。", PH[0], 905, 80, RED, k0=2.5, k1=3.3)
Z1 = (C1[0] + 350, 1330)
body, mouth = zhou(*Z1, 0.75)
L(body, 3, 3.8, BLACK, 9, sfx="wood_high")
L(face(*Z1, 0.75, "sad"), 3.8, 4.0, BLACK, 8)
L(cloud(Z1[0], 760, 400, 210), 4, 4.7, BLACK, 8, sfx="pop")
L(ring(Z1[0], 760, 400, 210, 26), 5, 5.6, BLACK, 5, sfx="shaker")
T("他不满意了", Z1[0], 762, 54, RED, k0=4.7, k1=6.0)

C2 = (X0 + 650, 1000)
scene("改方案改到半夜", "灵魂拷问", (*C2, 0.85))
L(desk(C2[0] + 50, 1130, 460), 0, 0.9, BLACK, 10, sfx="wood_high")
Z2 = (C2[0] - 350, 1330)
body, _ = zhou(*Z2, 0.75, "hold")
L(body, 1, 1.8, BLACK, 9, sfx="pop")
L(face(*Z2, 0.75, "flat"), 1.8, 2.0, BLACK, 8)
L(lamp(C2[0] + 230, 1130, 0.8), 2, 2.9, BLACK, 8, sfx="wood_low")
CK = (C2[0] + 300, 640)
L(join(clock(*CK, 85), hands_at(*CK, 85, 1, 0)), 3, 3.9, BLACK, 8, sfx="wood_high")
T("凌晨一点", CK[0], 800, 52, RED, k0=4, k1=5, sfx="pop")
L(cloud(Z2[0], 760, 420, 210), 5, 5.7, BLACK, 8, sfx="pop")
L(ring(Z2[0], 760, 420, 210, 26), 6, 6.6, BLACK, 5, sfx="shaker")
T("得让他满意", Z2[0], 762, 54, RED, k0=6.6, k1=7.9)

# ---------------------------------------------------------------- 亮书：往下挖（场景 3）

scene("书里教你往下挖", "伯恩斯新情绪疗法 · 书中办法", (X0, 2150, 0.85))
L(book(X0 - 350, 1980, 400, 260), 0, 0.9, BLACK, 9, sfx="wood_low")
T("伯恩斯新情绪疗法", X0 - 350, 1760, 56, GREEN, k0=1, k1=3, sfx="pop")
L(ground(GY, X0 - 1500, X0 + 1500), 3, 3.9, BLACK, 9, sfx="wood_high")
Z3 = (X0 + 350, GY)
body, _ = zhou(*Z3, 0.7, "hold")
L(body, 4, 4.8, BLACK, 9, sfx="pop")
L(face(*Z3, 0.7, "flat"), 4.8, 5.0, BLACK, 8)
L(shovel(Z3[0] + 100, GY - 230, Z3[0] + 170, GY + 70), 5, 5.8, BLACK, 8, sfx="wood_high")
T("往下挖", X0 + 400, 1800, 70, RED, k0=6, k1=6.8, sfx="pop")
L(arrow((X0, GY - 170), (X0, GY + 180), 0.0, 44), 7, 7.9, RED, 10, sfx="ding")

# ---------------------------------------------------------------- ★ drop：钻头一口气穿过四层土（场景 4）

FINAL4 = (X0, 7000, 0.4)
J4 = scene("挖到底了", "往下挖 · 一口气到底", FINAL4, shake=[0, 4], flashes=[0])
STOPS = [GY, YT[1], YT[2], YT[3], ROCK_TOP]     # 第 0–4 拍钻头尖所在深度
BIT = 260


def _tip(t):
    ts = [b.t_of(J4, k) for k in range(5)]
    if t <= ts[0]:
        return STOPS[0]
    for i in range(4):
        if t < ts[i + 1]:
            f = ease_in_out(clamp01((t - ts[i]) / (ts[i + 1] - ts[i])))
            return STOPS[i] + (STOPS[i + 1] - STOPS[i]) * f
    return STOPS[-1]


def drill_fn(c, k, t):
    """钻头往下钻：身后留下两道井壁；每穿过一层土溅起碎土。"""
    y = _tip(t)
    done = t >= b.t_of(J4, 4)
    bottom = ROCK_TOP if done else max(GY, y - BIT)
    pen = wb.marker(BLACK, 12)
    c.drawPath(join(P((X0 - WALL, GY), (X0 - WALL, bottom)), P((X0 + WALL, GY), (X0 + WALL, bottom))), pen)
    if not done:
        c.drawPath(join(P((X0 - WALL + 20, y - BIT), (X0 + WALL - 20, y - BIT), (X0, y), close=True),
                        P((X0 - 220, y - BIT + 40), (X0 + 120, y - BIT + 120)),
                        P((X0 - 130, y - BIT + 110), (X0 + 60, y - BIT + 170)),
                        P((X0 - 60, y - BIT + 180), (X0 + 20, y - 40))), wb.marker(RED, 12))
    for i in range(1, 5):
        dt = t - b.t_of(J4, i)
        if 0 <= dt < 0.45:
            f = dt / 0.45
            yy = STOPS[i]
            for sx in (-1, 1):
                for n, (ax, ay) in enumerate(((1.0, -0.6), (0.8, -1.0), (1.2, -0.2))):
                    px = X0 + sx * (WALL - 40 + 260 * f * ax)
                    py = yy - 40 + 220 * f * ay + 260 * f * f
                    c.drawCircle(px, py, 14 - 6 * f, K.paint(BLACK, 1 - f))
    return None


b.custom(J4, 0, 4, drill_fn, sfx="kick")
for i in range(1, 4):
    L(strata(YT[i]), i, i + 0.6, BLACK, 8, sfx="pop")
L(rock(*ROCK), 4, 4.9, BLACK, 12, sfx="kick")
T("人人都得满意", X0, 7580, 130, RED, k0=5, k1=6.5, sfx="pop")
Z4 = (X0 - 250, ROCK_TOP + 12)
body, _ = zhou(*Z4, 0.9, "hold")
L(body, 7, 7.7, BLUE, 10, sfx="wood_high")
L(face(*Z4, 0.9, "sad"), 7.7, 7.9, BLUE, 9)
for kb, cy in ((0, YT[0] + 1200), (1, YT[1] + 1200), (2, YT[2] + 1200), (3, 7000)):
    b.move(J4, kb, (X0, cy, 0.42), dur=0.5)
b.move(J4, 5, FINAL4, dur=1.1)

# ---------------------------------------------------------------- 往回走，一层一层看（场景 5–8）

LAYERS = [("客户不满意", 64, "phone"), ("领导会觉得我不行", 56, "boss"), ("大家都会看不起我", 56, "heads")]
CAPS = ["客户不满意，又怎样", "领导会觉得我不行", "大家都看不起我"]


def layer_icon(kind, x, y):
    if kind == "phone":
        L(phone(x, y, 140, 230), 1, 1.8, BLACK, 8, sfx="pop")
        T("嗯。", x, y - 10, 50, RED, k0=1.8, k1=2.0)
    elif kind == "boss":
        L(stick(x, y + 110, 0.5, "down", tie=True), 1, 1.7, BLACK, 8, sfx="pop")
        L(face(x, y + 110, 0.5, "sad"), 1.7, 2.0, BLACK, 7)
    elif kind == "heads":
        L(heads(x, y), 1, 2.0, BLACK, 7, sfx="pop")
    else:
        L(tag(x, y, 230, 130), 1, 1.6, BLACK, 8, sfx="pop")
        T("¥0", x + 20, y + 2, 64, RED, k0=1.6, k1=2.4)


def layer_label(n, y):
    L(circle(X0 - 500, y, 70), 0, 0.8, ACC, 9, sfx="wood_high")
    T(str(n), X0 - 500, y + 4, 80, ACC, k0=0.2, k1=1.0)


for i, (thought, size, icon) in enumerate(LAYERS):
    yt = YT[i]
    scene(CAPS[i], f"往回走 · 第 {i + 1} 层", (X0, yt + 600, 0.85))
    layer_label(i + 1, yt + 300)
    layer_icon(icon, X0 + 500, yt + 330)
    L(cloud(X0, yt + 380, 600, 290), 2, 2.9, BLACK, 8, sfx="wood_high")
    T(thought, X0, yt + 384, size, RED, k0=3, k1=3 + max(1.25, 0.25 * len(thought)), sfx="pop")
    L(ring(X0, yt + 380, 600, 290), 5, 5.9, BLACK, 5 + i, sfx="shaker")
    T("那又怎样？", X0, yt + 720, 70, BLUE, k0=6, k1=7.25, sfx="pop")
    L(arrow((X0, yt + 790), (X0, yt + 990), 0.0, 40), 7.3, 8.0, BLUE, 9)

yt = YT[3]
scene("没人认可就不值钱", "往回走 · 第 4 层", (X0, yt + 700, 0.85))
layer_label(4, yt + 300)
layer_icon("tag", X0 + 500, yt + 330)
L(cloud(X0, yt + 380, 620, 340), 2, 2.9, BLACK, 8, sfx="wood_high")
T("没人认可", X0, yt + 330, 62, RED, k0=3, k1=4, sfx="pop")
T("我就一文不值", X0, yt + 430, 62, RED, k0=4, k1=5.5)
L(ring(X0, yt + 380, 620, 340), 5.5, 6.0, BLACK, 9)
L(arrow((X0, yt + 600), (X0, ROCK_TOP - 20), 0.0, 46), 6, 6.9, RED, 11, sfx="ding")
T("到底了", X0 + 190, 7150, 56, RED, k0=7, k1=7.9, sfx="tom")
H(5, "shaker")

# ---------------------------------------------------------------- 书中观点：沉默的假设、认同上瘾（场景 9–10）

scene("平时看不见", "书中观点 · 沉默的假设", (X0, 7600, 0.8))
b.custom(J(), 0, 0.9, glow_fn(X0, ROCK[1], 1300, 760), sfx="ding")
L(rays(X0, ROCK[1], 330, 420, 10, 0.2), 0, 0.9, ACC, 8)
T("沉默的假设", X0, 7930, 80, GREEN, k0=2, k1=3.25, sfx="pop")
T("平时看不见", X0, 8050, 56, k0=4, k1=5.25, sfx="pop")
L(join(P((X0 - 140, 7330), (X0 - 90, 7260)), P((X0 - 110, 7340), (X0 - 30, 7300)), P((X0 - 160, 7300), (X0 - 170, 7230))),
  6, 6.6, RED, 8, sfx="rim")
T("一碰就疼", X0 - 510, 7150, 56, RED, k0=7, k1=8, sfx="pop")

VC = (X0 - 1950, 7600)
scene("怎么都不够", "书中观点 · 认同上瘾", (*VC, 0.85))
T("书中：认同上瘾", VC[0], 7150, 64, GREEN, k0=0, k1=1.75, sfx="pop")
Z10 = (VC[0] - 200, 7900)
body, _ = zhou(*Z10, 0.8, "hold")
L(body, 2, 2.8, BLACK, 9, sfx="wood_high")
L(face(*Z10, 0.8, "sad"), 2.8, 3.0, BLACK, 8)
CUP = (VC[0] - 50, 7690)
L(cup(*CUP), 3, 3.7, BLACK, 9, sfx="pop")
T("认可", CUP[0], CUP[1] - 10, 48, RED, k0=3.7, k1=4.5)
L(arrow((VC[0] + 400, 7420), (CUP[0] + 60, 7580), 0.15, 36), 5, 5.7, BLUE, 8, sfx="wood_high")
T("不错", VC[0] + 450, 7340, 56, BLUE, k0=5.7, k1=6.5)
L(drops(CUP[0], CUP[1] + 125), 6, 6.6, BLUE, 7, sfx="shaker")
T("怎么都不够", VC[0], 8080, 70, RED, k0=6.6, k1=7.9)
H(7, "rim")

# ---------------------------------------------------------------- 换一句自己信的话（场景 11）

WC = (X0 + 620, 7150)
scene("换一块垫脚石", "换一句话 · 白云", (X0 + 300, 7600, 0.7))
L(P((X0 - 420, 7585), (X0 + 420, 7575)), 0, 0.7, BLUE, 12, sfx="rim")
L(arrow((X0 + 420, 7380), (WC[0] - 240, WC[1] + 60), -0.25, 36), 1, 1.8, BLUE, 9, sfx="wood_high")
L(cloud(*WC, 460, 280), 2, 2.9, BLUE, 8, sfx="pop")
T("有人不满意", WC[0], WC[1] - 55, 56, BLUE, k0=3, k1=4.25, sfx="pop")
T("我照样值得", WC[0], WC[1] + 55, 56, BLUE, k0=5, k1=6.25, sfx="pop")
L(rays(*WC, 175, 215, 8, 0.4), 7, 7.8, BLUE, 7, sfx="ding")

# ---------------------------------------------------------------- 做法：连问三次（场景 12）

scene("连问三次", "做法 · 连问三次", (X0, 9000, 0.85))
T("慌了，连问三次", X0, 8580, 70, BLUE, k0=0, k1=1.75, sfx="pop")
for n in range(3):
    y0 = 8680 + n * 180
    L(arrow((X0 - 400, y0), (X0 - 400, y0 + 140), 0.0, 34), 2 + n, 2.8 + n, ACC, 10, sfx="wood_high")
T("那又怎样？", X0 - 40, 8930, 56, BLUE, k0=5, k1=6.25, sfx="pop")
NT = (X0 + 400, 8940)
L(note(*NT), 6.3, 7.0, BLACK, 8)
T("写下", NT[0] - 20, 8880, 56, k0=7, k1=7.5, sfx="pop")
T("挖到的那句", NT[0] - 20, 8980, 50, RED, k0=7.5, k1=8.0)

# ---------------------------------------------------------------- 这一季回顾（场景 13）

scene("这一季的工具", "这一季回顾", (X0, 10400, 0.6))
T("这一季的工具", X0, 9850, 90, k0=0, k1=1.5, sfx="pop")
IY = 10300
ICONS = [lambda x: join(cloud(x, IY, 230, 140), ring(x, IY, 230, 140, 20)), lambda x: grid_list(x, IY),
         lambda x: column_card(x, IY), lambda x: bars_icon(x, IY), lambda x: high_jump(x, IY),
         lambda x: rock(x, IY, 230, 150)]
L(underline(X0 - 860, X0 + 860, 10520, 14, 50), 1, 1.9, ACC, 8, sfx="wood_low")
for n, fn in enumerate(ICONS):
    x = X0 + (n - 2.5) * 290
    L(fn(x), 2 + n, 2.8 + n, RED if n in (0, 5) else BLACK, 7 if n == 0 else 9,
      sfx="ding" if n == 5 else ("wood_high" if n % 2 else "pop"))

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (X0, 5450, 0.15)
COMMENT = (X0, 11500, 0.8)
J14 = scene("你挖到哪一句了", "评论区见", FAR, bars=4)
b.move(J14, 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
WC2 = (X0 + 300, 11760)
L(cloud(*WC2, 520, 190), 1, 1.8, BLUE, 8, sfx="wood_high")
T("今天换掉一朵乌云", WC2[0], WC2[1] + 2, 46, BLUE, k0=2, k1=4)
T("你挖到底，是哪一句？", X0, 11150, 76, RED, k0=6, k1=8.5, sfx="pop")
T("这一季讲完了", X0, 11310, 56, k0=9, k1=10.5, sfx="wood_high")
T("一直低落、睡不好、不想活，去找医生聊聊", X0, 11450, 46, k0=11, k1=15, sfx="pop")
b.hit(J14, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "approval", "往下挖", "别人一不满意，你就慌？", ACC, b.shots,
                 [f"{BOOK}第 10 章（向下箭头法、沉默的假设）、第 11 章“认同上瘾”（转述）",
                  "中译本：中国城市出版社 2011；科学技术文献出版社 2014"],
                 "别人一不满意|你就【慌】", SQUARE_SHOT,
                 ["书中观点均为转述：对一个让人难受的想法一路追问“如果这是真的，对我意味着什么”，一层层往下，"
                  "能挖到底下平时看不见的信念，书中称为沉默的假设（如“我得让每个人都满意”）（第 10 章，向下箭头法，通行译法）；"
                  "把别人的认可当成自己有价值的前提，书中称为认同上瘾；别人不满意，说明的是对方的看法，定不了你的价值（第 11 章）。"
                  "出处：David D. Burns, Feeling Good: The New Mood Therapy（中译本《伯恩斯新情绪疗法》，李亚萍译）。"
                  "上屏均为转述，不是逐字引文；“那又怎样？”为对书中追问方式的口语化说法。",
                  "客户只回“嗯。”、改方案到凌晨一点、四层想法（客户不满意 / 领导会觉得我不行 / 大家都会看不起我 / "
                  "没人认可我就一文不值）均为现实场景示意，不是书中病例，不指向任何具体公司或个人；时间、价签数字为示意。",
                  "钻头穿土、石头、漏底的“认可”杯子为画面比喻；白云里的“有人不满意，我照样值得”与“慌了连问三次、"
                  "写下挖到的那句”为据书中思路整理的做法。",
                  "场景 13 排出的是本系列各讲用过的画面道具（念头云、十格清单、三栏卡、柱子、跳高横杆、石头），为回顾示意。",
                  "本片为读书分享，不能替代诊断和治疗；情绪持续低落或有轻生念头，请尽快联系医生、心理咨询师或当地心理援助热线。"],
                 tags="#讨好型人格")
    return b.attach(ep)
