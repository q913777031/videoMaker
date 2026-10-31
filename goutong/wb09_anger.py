"""09 表达愤怒（白板手绘版）：气到想摔门，先做哪一步？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 I：一条怒气曲线）：白板上一条横贯全讲的“火气—时间”曲线（只画走势，不标刻度）。
周一例会，主角做了两周的方案被同事说成是他做的 → 曲线往上爬、逼近红线 → drop：冲破红线炸开，
炸点贴上“他就是抢功”这张评判标签（书中观点：他的行为是刺激，火来自心里的评判）→ 亮书 + 四格卡 →
四步让曲线一段段落下：停下来呼吸、听听脑子里的评判、找到没被满足的需要（评判标签擦掉，换成一节电池）、
说出感受和需要（带刺的小泡刺缩回去，带着四格卡的四个图标出来）→ 拉远看整条曲线 →
据书中思路：同事也可能有话，先听听他 → 做法：四步抄进手机备忘录、贴在会议室门上 → 评论区。
书中观点为转述（马歇尔·卢森堡《非暴力沟通》第十章“充分表达愤怒”，阮胤华译，华夏出版社）；
会议抢功的故事、曲线、改写句与做法均为示意，据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, book, bubble, circle, join, partial, rect,
                               stick, face, underline)

from .common import BOOK, episode

ACC = "#C2452D"
SQUARE_SHOT = 12                 # 场景 13：我指着门边的“停 听 找 说”便签（人物 + 四步）

b = Board(size=(4200, 6000))


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


# ---------------------------------------------------------------- 本讲画法

def mixc(a, c, f):
    a, c = a.lstrip("#"), c.lstrip("#")
    va = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    vc = [int(c[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(lerp(x, y, f)):02X}" for x, y in zip(va, vc))


def stroke(c, path, color, width):
    c.drawPath(path, wb.marker(color, width))
    c.drawPath(path, K.paint(color, 0.22, width * 0.45, blur=1.2))


def flip(path, x):
    """左右镜像（绕竖线 x）。"""
    p = skia.Path(path)
    m = skia.Matrix()
    m.setScale(-1, 1, x, 0)
    p.transform(m)
    return p


def arrowhead(x, y, ang, head=50):
    p = skia.Path()
    for d in (0.45, -0.45):
        p.moveTo(x, y)
        p.lineTo(x - head * math.cos(ang + d), y - head * math.sin(ang + d))
    return p


def dashed(x0, x1, y, dash=60, gap=36) -> skia.Path:
    parts, x = [], x0
    while x < x1:
        parts.append(P((x, y), (min(x + dash, x1), y)))
        x += dash + gap
    return join(*parts)


def eye(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 60 * s, y)
    p.quadTo(x, y - 50 * s, x + 60 * s, y)
    p.quadTo(x, y + 50 * s, x - 60 * s, y)
    return join(p, circle(x, y, 15 * s))


def heart(x, y, r=40) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def battery(x, y, w=120, h=60) -> skia.Path:
    return join(rect(x, y, w, h, 10), rect(x + w / 2 + 9, y, 14, h * 0.4, 4))


def palm(x, y, s=1.0) -> skia.Path:
    """伸出的手：掌心 + 四指 + 拇指。"""
    parts = [rect(x, y + 18 * s, 64 * s, 56 * s, 14 * s)]
    for i in range(4):
        fx = x - 24 * s + i * 16 * s
        parts.append(P((fx, y - 10 * s), (fx, y - 46 * s + abs(i - 1.5) * 6 * s)))
    parts.append(P((x - 32 * s, y + 20 * s), (x - 58 * s, y - 6 * s)))
    return join(*parts)


def head(x, y, r=140) -> skia.Path:
    """侧脸脑袋：圆 + 朝左的鼻子 + 脖子。"""
    return join(circle(x, y, r), P((x - r * 0.98, y - r * 0.08), (x - r * 1.18, y + r * 0.14), (x - r * 0.94, y + r * 0.26)),
                P((x - r * 0.35, y + r * 0.94), (x - r * 0.35, y + r * 1.3)), P((x + r * 0.35, y + r * 0.94),
                                                                                  (x + r * 0.35, y + r * 1.3)))


def star(x, y, r=150, n=12) -> skia.Path:
    pts = []
    for i in range(n * 2):
        a = i / (n * 2) * 2 * math.pi - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.52
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return P(*pts, close=True)


def tag(x, y, w, h) -> skia.Path:
    """标签：尖头卡片 + 穿绳小孔（孔在右边）。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2 - 40, y - h / 2), (x + w / 2, y), (x + w / 2 - 40, y + h / 2),
                  (x - w / 2, y + h / 2), close=True), circle(x + w / 2 - 40, y, 12))


def ear(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - 40 * s, y - 60 * s, 80 * s, 120 * s), 160, 250)
    q = skia.Path()
    q.addArc(skia.Rect.MakeXYWH(x - 15 * s, y - 25 * s, 36 * s, 50 * s), 180, 200)
    return join(p, q)


def four_card(x, y, cw=120, ch=130) -> skia.Path:
    """四格卡：眼睛（观察）、心（感受）、电池（需要）、手（请求）。"""
    parts = [rect(x, y, cw * 4, ch, 14)]
    for i in range(1, 4):
        parts.append(P((x - 2 * cw + i * cw, y - ch / 2), (x - 2 * cw + i * cw, y + ch / 2)))
    cx = [x - 1.5 * cw + i * cw for i in range(4)]
    parts += [eye(cx[0], y, 0.6), heart(cx[1], y + 4, 30), battery(cx[2] - 6, y, 70, 38), palm(cx[3], y + 6, 0.8)]
    return join(*parts)


# 动态项

def line_fn(path, color, width, ok):
    """逐段描出一条路径；笔尖跑出画面（ok 返回 False）时手停在画面边上，线自己往前延伸。"""

    def fn(c, k, t):
        part, tip = partial(path, k)
        stroke(c, part, color, width)
        return tip if tip and ok(*tip) else None

    return fn


def fill_fn(path, color, alpha=0.35):
    def fn(c, k, t):
        c.drawPath(path, K.paint(color, alpha * ease_out(k)))
        return None

    return fn


def blink_fn(path, color):
    """缺电的电量格：闪几下后亮着。"""

    def fn(c, k, t):
        a = 1.0 if k >= 1 else 0.25 + 0.75 * (0.5 + 0.5 * math.cos(t * 14))
        c.drawPath(path, K.paint(color, a))
        return None

    return fn


def burst_fn(x, y, r):
    def fn(c, k, t):
        s = ease_out(k)
        c.drawPath(star(x, y, r * (0.4 + 0.6 * s)), K.paint(ORANGE, 0.45))
        return None

    return fn


def xiaopao(x, y, w, h, kd0, kd1, kr0=None, kr1=None, tail=-1, eye_dy=-70, spike=42):
    """系列角色“小泡”：会变形的对话气泡。kd0–kd1 拍描出来并长出红刺；kr0–kr1 拍刺一根根缩回去，变蓝，嘴角上扬。"""
    body = bubble(x, y, w, h, tail)
    pm = skia.PathMeasure(rect(x, y, w, h, 40), False)
    total = pm.getLength()
    n = int(total // 105)
    spikes = []
    for i in range(n):
        pos, tan = pm.getPosTan((i + 0.5) * total / n)
        px, py, tx, ty = pos.x(), pos.y(), tan.x(), tan.y()
        if py > y + h / 2 - 5 and tail * (px - x) > w * 0.05:      # 让开尾巴
            continue
        spikes.append((px, py, tx, ty))
    kend = kr1 if kr1 is not None else kd1
    ey = y + eye_dy

    def fn(c, k, t):
        beat = kd0 + k * (kend - kd0)
        fd = clamp01((beat - kd0) / (kd1 - kd0))
        fr = ease_in_out(clamp01((beat - kr0) / (kr1 - kr0))) if kr0 is not None else 0.0
        col = mixc(RED, BLUE, fr)
        part, tip = partial(body, clamp01(fd / 0.7))
        stroke(c, part, col, 9)
        sg = clamp01((fd - 0.6) / 0.4)
        for idx, (px, py, tx, ty) in enumerate(spikes):
            # 缩回时一根根依次缩
            loc = clamp01(fr * 1.6 - idx / max(1, len(spikes)) * 0.6)
            g = sg * (1 - loc)
            if g < 0.03:
                continue
            nx, ny = ty, -tx
            sp = P((px - tx * 20, py - ty * 20), (px + nx * spike * g, py + ny * spike * g), (px + tx * 20, py + ty * 20))
            stroke(c, sp, col, 8)
        if fd > 0.75:
            K.dot(c, x - 34, ey, 9, BLACK)
            K.dot(c, x + 34, ey, 9, BLACK)
            curv = lerp(-22, 22, fr)
            m = skia.Path()
            m.moveTo(x - 28, ey + 34 - curv * 0.3)
            m.quadTo(x, ey + 34 + curv, x + 28, ey + 34 - curv * 0.3)
            c.drawPath(m, wb.marker(BLACK, 7))
        return tip if fd < 0.7 else None

    return fn


# ---------------------------------------------------------------- 怒气曲线（白板坐标）

O = (250, 3300)                 # 原点；纵轴“火气”到 y=1150，横轴“时间”到 x=4000
RED_Y = 2050                    # 红线
PTS = [(260, 3150), (1250, 3130), (1850, 2700), (2150, 2120), (2300, 1450), (2750, 1470), (3050, 1650), (3400, 2350),
       (3800, 3050)]


def seg(i) -> skia.Path:
    """曲线第 i 段（PTS[i] → PTS[i+1]），Catmull-Rom 平滑，段与段首尾相接。"""
    p0 = PTS[max(0, i - 1)]
    p1, p2 = PTS[i], PTS[i + 1]
    p3 = PTS[min(len(PTS) - 1, i + 2)]
    c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
    c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
    p = skia.Path()
    p.moveTo(*p1)
    p.cubicTo(*c1, *c2, *p2)
    return p


AXES = join(P((O[0], 1150), O, (4000, O[1])), arrowhead(O[0], 1150, -math.pi / 2, 50), arrowhead(4000, O[1], 0, 50))
ME = (500, 2550)                # 我（蓝）
CO = (1300, 2550)               # 同事
LBL = {1: (2600, 1290), 2: (3110, 1320), 3: (3700, 2250), 4: (3800, 2550)}   # 四步的标签位置

# ---------------------------------------------------------------- 开局：周一例会（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("周一的例会", "开局 · 例会", (1000, 2350, 0.5), bars=2)
L(rect(900, 1750, 560, 300, 16), 0, 0.9, sfx="wood_high")
T("我的方案", 900, 1700, 80, k0=1, k1=2, sfx="pop")
T("做了两周", 900, 1820, 80, BLUE, k0=2, k1=3, sfx="pop")
L(stick(*ME, 0.75), 3, 3.8, BLUE, 10, sfx="pop")
L(face(*ME, 0.75, "smile"), 3.8, 4.0, BLUE, 8)
C(line_fn(AXES, BLACK, 9, lambda x, y: x < 2050 and y > 1420), 4, 4.9, sfx="wood_high")
T("火气", 380, 1600, 80, k0=5, k1=5.5, sfx="pop")
L(seg(0), 5.5, 6.0, RED, 11)

scene("他说是他做的", "开局 · 例会", (1250, 2400, 0.55))
L(join(P((700, 2350), (1150, 2350)), P((730, 2350), (730, 2550)), P((1120, 2350), (1120, 2550))), 0, 0.8, BLACK, 10,
  sfx="wood_low")
L(flip(stick(*CO, 0.75, "point", tie=True), CO[0]), 1, 1.8, BLACK, 10, sfx="wood_high")
L(face(*CO, 0.75, "smile"), 1.8, 2.0, BLACK, 8)
L(bubble(1680, 2250, 480, 140, -1), 2, 2.6, BLACK, 8, sfx="pop")
T("我做的方案", 1680, 2250, 80, k0=2.6, k1=3.8)
T("没提我", 400, 2080, 80, RED, k0=4, k1=4.8, sfx="rim")
L(seg(1), 5, 6.0, RED, 11, sfx="wood_low")
H(7, "tom", 0.6)

scene("火一下上来了", "开局 · 火气", (1350, 2300, 0.6))
C(line_fn(dashed(1550, 4000, RED_Y), RED, 8, lambda x, y: x < 2250), 0, 1.2, sfx="wood_high")
T("红线", 1450, RED_Y, 70, RED, k0=1.2, k1=2)
L(seg(2), 2, 2.9, RED, 11, sfx="wood_low")
C(xiaopao(820, 2080, 400, 220, 3, 3.9, eye_dy=-62), 3, 3.9, sfx="rim")
T("想摔门", 820, 2120, 80, RED, k0=4, k1=4.8, sfx="pop")
L(join(circle(ME[0] - 52, 2462, 17), circle(ME[0] + 52, 2462, 17)), 6, 6.5, RED, 10, sfx="tom")
H(7, "shaker", 0.6)

# ---------------------------------------------------------------- drop：火从想法里来（场景 4）

scene("火从想法里来", "非暴力沟通 · 书中观点", (2150, 1750, 0.6), shake=[0], flashes=[0])
L(seg(3), 0, 0.6, RED, 13, sfx="kick")
C(burst_fn(2300, 1450, 150), 1, 1.5)
L(star(2300, 1450, 150), 1, 1.8, RED, 9, sfx="pop")
L(tag(1800, 1250, 560, 150), 2, 2.8, BLACK, 9, sfx="wood_high")
T("他就是抢功", 1780, 1250, 90, RED, k0=3, k1=4.25, sfx="pop")
L(P((2060, 1250), (2120, 1330), (2175, 1390)), 5, 5.6, BLACK, 7, sfx="rim")
T("这个评判在点火", 1800, 1090, 70, RED, k0=6, k1=7.75, sfx="ding")

# ---------------------------------------------------------------- 亮书 + 四格卡（场景 5）

CARD = (1250, 820)
scene("有本书讲过", "非暴力沟通 · 第十章", (950, 850, 0.85))
L(book(700, 820, 360, 240), 0, 0.9, BLACK, 10, sfx="wood_low")
T("非暴力沟通", 700, 600, 72, GREEN, k0=1, k1=2.25, sfx="pop")
T("卢森堡", 700, 1040, 56, k0=3, k1=3.8, sfx="pop")
L(four_card(*CARD), 4, 4.9, BLACK, 8, sfx="wood_high")
C(fill_fn(rect(CARD[0] - 60, CARD[1], 116, 126, 8), RED, 0.3), 6, 6.6, sfx="ding")
T("这讲：生气", 1250, 980, 56, RED, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 四步：曲线一段段落下（场景 6–9）

scene("第一步：停下来", "书中观点 · 第一步", (2650, 1650, 0.75))
L(seg(4), 0, 0.9, BLUE, 11, sfx="wood_low")
T("①停", *LBL[1], 120, BLUE, k0=1, k1=1.8, sfx="pop")
for n, r in enumerate((45, 90, 135)):
    L(circle(2550, 1780, r), 2 + n, 2.8 + n, BLUE, 8, sfx="shaker")
T("深呼吸", 2850, 1700, 80, k0=5, k1=5.9, sfx="pop")
H(7, "wood_high", 0.5)

HEAD = (3450, 1300)
scene("第二步：听脑子", "书中观点 · 第二步", (3550, 1300, 0.8))
L(seg(5), 0, 0.9, BLUE, 11, sfx="wood_low")
T("②听", *LBL[2], 120, BLUE, k0=1, k1=1.8, sfx="pop")
L(head(*HEAD, 140), 2, 2.9, BLACK, 9, sfx="wood_high")
L(join(circle(3610, 1200, 10), circle(3650, 1160, 14), circle(3700, 1110, 18), circle(3605, 1400, 10),
       circle(3630, 1445, 12)), 3, 3.6, BLACK, 6, sfx="pop")
L(rect(3900, 1050, 300, 120, 14), 4, 4.4, RED, 7, sfx="pop")
T("他无耻", 3900, 1050, 80, RED, k0=4.4, k1=5.2)
L(rect(3880, 1530, 460, 120, 14), 6, 6.4, RED, 7, sfx="pop")
T("他看不起我", 3880, 1530, 80, RED, k0=6.4, k1=7.65)

scene("第三步：找需要", "书中观点 · 第三步", (3500, 1660, 0.72))
b.erase(J(), 0, 1, 3880, 1290, 520, 660)
H(0, "shaker")
L(battery(3880, 1270, 260, 130), 1, 1.8, GREEN, 9, sfx="wood_high")
C(blink_fn(rect(3780, 1270, 46, 96, 6), RED), 2, 2.8, sfx="rim")
T("两周的活", 3880, 1110, 64, k0=3, k1=4, sfx="pop")
T("想被看见", 3880, 1430, 80, GREEN, k0=4, k1=5, sfx="pop")
L(seg(6), 5, 5.9, BLUE, 11, sfx="wood_low")
T("③找", *LBL[3], 120, BLUE, k0=6, k1=6.8, sfx="pop")
H(7, "ding", 0.6)

PAO = (2950, 2760)
CELLS = [((2590, 2700), (2770, 2700), "说成你做的"), ((3030, 2700), (3210, 2700), "我很生气"),
         ((2590, 2900), (2770, 2900), "想被看见"), ((3030, 2900), (3210, 2900), "会后聊聊？")]
ICONS = [eye(2590, 2700, 0.65), heart(3030, 2704, 36), battery(2584, 2900, 84, 44), palm(3030, 2906, 0.85)]
scene("第四步：说出来", "书中观点 · 第四步", (3200, 2640, 0.75))
L(seg(7), 0, 0.9, BLUE, 11, sfx="wood_low")
T("④说", *LBL[4], 120, BLUE, k0=1, k1=1.8, sfx="pop")
C(xiaopao(*PAO, 900, 560, 2, 2.8, 3, 4, eye_dy=-200), 2, 4, sfx="rim")
H(3, "ding")
for n, ((ix, iy), (tx, ty), s) in enumerate(CELLS):
    L(ICONS[n], 4 + n, 4.3 + n, (BLACK, RED, GREEN, BLUE)[n], 7, sfx="pop")
    T(s, tx, ty, 56, k0=4.3 + n, k1=5 + n)

# ---------------------------------------------------------------- 拉远：整条曲线（场景 10，封面镜头）

scene("曲线落下来了", "全板 · 四步", (2150, 2250, 0.27))
T("时间", 3880, 3420, 150, k0=0, k1=0.8, sfx="wood_high")
for n in range(1, 5):
    L(circle(*LBL[n], 120), n, n + 0.7, RED, 20, sfx="pop")
T("四步，火降下来", 3100, 750, 170, RED, k0=6, k1=7.75, sfx="ding")

# ---------------------------------------------------------------- 回到会议室：他也可能有话（场景 11）

scene("他也可能有话", "据书中思路 · 先听他", (1150, 2200, 0.8))
L(battery(1230, 2150, 220, 100), 0, 0.8, BLACK, 8, sfx="wood_high")
C(blink_fn(rect(1150, 2150, 40, 72, 6), RED), 1, 1.8, sfx="rim")
T("？", 1230, 2010, 100, RED, k0=2, k1=2.8, sfx="pop")
T("先听他说", 950, 2700, 80, BLUE, k0=4, k1=5, sfx="pop")
L(ear(720, 2700, 1.0), 6, 6.8, BLUE, 8, sfx="wood_low")

# ---------------------------------------------------------------- 做法（场景 12–13）

scene("抄在手机里", "做法 · 备忘录", (1250, 4250, 0.8))
L(join(rect(950, 4250, 480, 860, 50), P((890, 4640), (1010, 4640))), 0, 0.9, BLACK, 9, sfx="wood_high")
T("备忘录", 950, 3910, 56, k0=1, k1=1.8, sfx="pop")
for n, s in enumerate(("① 停下来", "② 听脑子", "③ 找需要", "④ 说出来")):
    T(s, 950, 4060 + n * 150, 64, BLUE if n else RED, k0=2 + n, k1=2.9 + n, sfx="pop")
L(eye(1600, 4100, 1.0), 6, 6.7, BLACK, 8, sfx="wood_low")
T("开会前看一眼", 1600, 4280, 64, k0=7, k1=8, sfx="pop")

scene("下次火上来", "做法 · 门上便签", (2800, 4150, 0.8))
L(rect(2700, 4150, 560, 1000, 10), 0, 0.9, BLACK, 10, sfx="wood_high")
L(circle(2920, 4220, 22), 1, 1.4, BLACK, 9, sfx="pop")
L(rect(2700, 3950, 380, 380, 8), 2, 2.8, ORANGE, 8, sfx="wood_high")
for n, (s, x, y) in enumerate((("停", 2610, 3870), ("听", 2790, 3870), ("找", 2610, 4040), ("说", 2790, 4040))):
    T(s, x, y, 90, BLUE, k0=3 + n, k1=3.8 + n, sfx="pop")
L(flip(stick(3250, 4650, 0.8, "point"), 3250), 7, 7.8, BLUE, 10, sfx="wood_high")
L(face(3250, 4650, 0.8, "smile"), 7.8, 8.0, BLUE, 8)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (2100, 2700, 0.21)
NEAR = (2100, 5300, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, NEAR, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(rect(2100, 5300, 1200, 380, 30), 5, 5.9, BLACK, 8, sfx="wood_low")
T("你上次为啥想摔门？", 2100, 5230, 76, RED, k0=6, k1=8.25, sfx="pop")
T("下一讲：夸人一句“真棒”，够了吗？", 2100, 5400, 50, k0=9, k1=13.5, sfx="wood_high")
L(underline(1700, 2500, 5450, 10, 40), 13.5, 14.2, BLACK, 6)
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "anger", "表达愤怒", "气到想摔门，先做哪一步？", ACC, b.shots,
                 [f"{BOOK}第十章 充分表达愤怒（转述）", "中译本：阮胤华译，华夏出版社"],
                 "气到想摔门|先做【哪一步】", 3,
                 ["书中观点均为转述（第十章“充分表达愤怒”）：别人的行为是刺激，愤怒来自我们心里对对方的评判；"
                  "表达愤怒的四步：停下来、呼吸；留意脑子里的评判；体会自己没被满足的需要；说出感受和没被满足的需要。"
                  "上屏均为转述，不是逐字引文。",
                  "例会上方案被同事说成是他做的、“他就是抢功”“他无耻”“他看不起我”几张评判标签、“两周的活想被看见”、"
                  "四格里的改写句（说成你做的 / 我很生气 / 想被看见 / 会后聊聊？）均为示意，据书中思路整理，不指向任何具体公司或个人。",
                  "怒气曲线、红线、四个拐点为示意，没有刻度，不是数据。",
                  "“他也可能有话，先听他说”据书中思路整理（对方情绪大时先倾听对方，据记忆，章节需核实）。",
                  "四步抄进手机备忘录、贴在会议室门上为据书中思路整理的做法建议。"],
                 tags="#情绪管理 #职场")
    return b.attach(ep)
