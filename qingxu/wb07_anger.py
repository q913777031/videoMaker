"""07 生气（白板手绘版）：群里怼完同事，为什么又后悔？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（G 倒叙，先给结局再一格一格往回倒）：开局就是结局——群里那句「你自己看看你干的好事」已发送、撤不回；
同事不说话了，小周后悔一下午 → 倒带（◀◀、时钟倒转、一条往左走的时间带）→
drop：倒回到大拇指按下「发送」的那一下，屏幕炸开 → 再往前一分钟：小周头顶的乌云里冒着两句话
「他就应该先问我」「他这人就是不靠谱」→ 亮书：点火的是这两句，贴上名牌「应该句式」「乱贴标签」→
再往前二十分钟：事情本身只是同事改了文件没说一声 → 把三格摆正：事情 → 火热的想法 → 发火 →
书中观点：先问这次生气有没有用（天平：出气 vs 关系僵、事没解决）；把火热的想法换成冷静的想法（应该 → 希望，乌云旁长出白云）→
正着重放：换了想法，发出去的是另一条消息，同事回「好嘞」→ 做法（手指悬在发送键上，先在三栏卡里写下那句话；
圈出「就是」，归到「乱贴标签」，换个说法）→ 拉远看全板，推到评论区。
系列视觉角色：小周（戴工牌）、乌云念头云（红字）与白云（蓝字）、名牌、三栏卡；片尾右下角小白云「今天换掉一朵乌云」。
书中观点为转述：戴维·伯恩斯《伯恩斯新情绪疗法》第 7 章“生气了吗——你的‘易怒商数’是多少”（让人生气的是你对事情的想法，
常见应该句式和乱贴标签；先问这次生气对自己有没有用；把火热的想法换成冷静的想法——中文叫法为通行译法，未核对译本原词）；
中译本李亚萍译，中国城市出版社 2011。群消息、时间点与同事改文件的情节为现实场景示意；做法据第 7 章思路整理。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, clock,
                               doc, face, hands_at, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#D2552E"                 # 本讲主色：火气的橙红
SQUARE_SHOT = 9                 # 场景 10：小周 + 乌云红字「他就应该先问我」→ 白云蓝字「我希望他先说一声」

b = Board(size=(3600, 14900))
GREY = "#8A8A93"


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = J() if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法（系列角色：小周、念头云、名牌、三栏卡）

def badge(x, y, s=1.0) -> skia.Path:
    """工牌：挂绳 + 小卡片，(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 12 * s, hy + 46 * s), (x + 14 * s, hy + 112 * s)), P((x + 14 * s, hy + 46 * s), (x + 30 * s, hy + 112 * s)),
                rect(x + 22 * s, hy + 136 * s, 38 * s, 48 * s, 5 * s))


def zhou(x, y, s=0.8, arms="down") -> skia.Path:
    """小周：简笔小人 + 工牌。arms 另有 cover（双手捂脸）。"""
    if arms != "cover":
        return join(stick(x, y, s, arms), badge(x, y, s))
    hy = y - 290 * s
    sh = hy + 80 * s
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)),
                P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)),
                P((x - 24 * s, hy + 4 * s), (x - 75 * s, sh + 50 * s), (x, sh), (x + 75 * s, sh + 50 * s), (x + 24 * s, hy + 4 * s)),
                circle(x - 24 * s, hy + 2 * s, 17 * s), circle(x + 24 * s, hy + 2 * s, 17 * s), badge(x, y, s))


def brows(x, y, s=0.8) -> skia.Path:
    """生气的眉毛（配合 face 的“sad”嘴）。"""
    hy = y - 290 * s
    return join(P((x - 32 * s, hy - 30 * s), (x - 6 * s, hy - 18 * s)), P((x + 32 * s, hy - 30 * s), (x + 6 * s, hy - 18 * s)))


def cloud(x, y, w, h, tail=None) -> skia.Path:
    """念头云：一圈鼓包的云朵轮廓；tail=(tx, ty) 时朝该点冒两个小圆泡。"""
    rx, ry = w / 2 * 0.86, h / 2 * 0.80
    n = max(8, int((w + h) / 95))
    pts = [(x + rx * math.cos(2 * math.pi * i / n + 0.2), y + ry * math.sin(2 * math.pi * i / n + 0.2)) for i in range(n)]
    p = skia.Path()
    p.moveTo(*pts[0])
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n + 0.2
        q = pts[(i + 1) % n]
        p.quadTo(x + 1.38 * rx * math.cos(a), y + 1.38 * ry * math.sin(a), *q)
    parts = [p]
    if tail:
        tx, ty = tail
        dx, dy = tx - x, ty - y
        d = math.hypot(dx, dy)
        ex, ey = x + dx / d * rx * 1.05, y + dy / d * ry * 1.05
        for f, r in ((0.38, 22), (0.72, 13)):
            parts.append(circle(ex + (tx - ex) * f, ey + (ty - ey) * f, r))
    return join(*parts)


def soot(x, y, w, h) -> skia.Path:
    """乌云的一圈涂黑边：沿云内侧来回划的锯齿。"""
    rx, ry = w / 2 * 0.86, h / 2 * 0.80
    p = skia.Path()
    m = 64
    for i in range(m + 1):
        a = 2 * math.pi * i / m
        f = 0.97 if i % 2 == 0 else 0.86
        (p.moveTo if i == 0 else p.lineTo)(x + rx * f * math.cos(a), y + ry * f * math.sin(a))
    return p


def tag_box(x, y, s, size=58) -> skia.Path:
    """名牌外框：按字数定宽，左边打一个挂孔。"""
    w = len(s) * size + 56
    return join(rect(x, y, w, size + 40, 12), circle(x - w / 2 + 18, y, 7))


def flame(x, y, s=1.0) -> skia.Path:
    """火苗：(x, y) 为火苗底部中点。"""
    fl = skia.Path()
    fl.moveTo(x, y - 170 * s)
    fl.quadTo(x + 90 * s, y - 70 * s, x + 40 * s, y)
    fl.lineTo(x - 40 * s, y)
    fl.quadTo(x - 90 * s, y - 70 * s, x, y - 170 * s)
    inner = skia.Path()
    inner.moveTo(x - 6 * s, y - 85 * s)
    inner.quadTo(x + 35 * s, y - 35 * s, x, y - 4 * s)
    inner.quadTo(x - 32 * s, y - 35 * s, x - 6 * s, y - 85 * s)
    return join(fl, inner)


def rewind(x, y, s=1.0) -> skia.Path:
    """倒带符号 ◀◀：(x, y) 为中心。"""
    return join(P((x - 120 * s, y), (x, y - 80 * s), (x, y + 80 * s), close=True),
                P((x, y), (x + 120 * s, y - 80 * s), (x + 120 * s, y + 80 * s), close=True))


def play(x, y, s=1.0) -> skia.Path:
    return P((x - 45 * s, y - 60 * s), (x + 60 * s, y), (x - 45 * s, y + 60 * s), close=True)


def ccw_arc(x, y, r) -> skia.Path:
    """绕时钟逆时针转的箭头。"""
    p = skia.Path()
    a0, a1 = -20, -250
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), a0, a1 - a0)
    a = math.radians(a1)
    ex, ey = x + r * math.cos(a), y + r * math.sin(a)
    tx, ty = math.sin(a), -math.cos(a)            # 逆时针方向的切线
    for d in (0.5, -0.5):
        hx = -(tx * math.cos(d) - ty * math.sin(d))
        hy = -(tx * math.sin(d) + ty * math.cos(d))
        p.moveTo(ex, ey)
        p.lineTo(ex + 45 * hx, ey + 45 * hy)
    return p


def star(x, y, r0, r1, n=14) -> skia.Path:
    pts = []
    for i in range(2 * n):
        a = math.pi * i / n - math.pi / 2
        r = r1 if i % 2 == 0 else r0
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    return P(*pts, close=True)


def finger(x, y, s=1.0) -> skia.Path:
    """从上往下伸的一根手指：(x, y) 为指尖。"""
    w, h = 90 * s, 200 * s
    p = skia.Path()
    p.addRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h, w, h), w / 2, w / 2)
    nail = skia.Path()
    nail.addRoundRect(skia.Rect.MakeXYWH(x - w * 0.3, y - 70 * s, w * 0.6, 55 * s), 14 * s, 14 * s)
    return join(p, nail, P((x - w / 2 + 12 * s, y - 120 * s), (x + w / 2 - 12 * s, y - 120 * s)))


def scale(x, y, s=1.0) -> tuple:
    """天平：返回（支架，横梁 + 两只吊篮），(x, y) 为支点；右边往下沉。左篮 150×110，右篮 300×170（两行字）。"""
    stand = join(P((x, y), (x, y + 550 * s)), P((x - 160 * s, y + 550 * s), (x + 160 * s, y + 550 * s)),
                 circle(x, y, 16 * s))
    lx, ly, rx, ry = x - 400 * s, y - 80 * s, x + 400 * s, y + 80 * s
    beam = [P((lx, ly), (rx, ry)),
            P((lx, ly), (lx, ly + 40 * s)), rect(lx, ly + 95 * s, 220 * s, 110 * s, 14 * s),
            P((rx, ry), (rx, ry + 50 * s)), rect(rx, ry + 135 * s, 300 * s, 170 * s, 14 * s)]
    return stand, join(*beam)


def card(x, y, w, h, head=110) -> skia.Path:
    """三栏卡：外框 + 表头横线 + 两根竖线（想法 / 歪在哪 / 换说法）。"""
    x0, y0 = x - w / 2, y - h / 2
    return join(rect(x, y, w, h, 18), P((x0, y0 + head), (x0 + w, y0 + head)),
                P((x0 + w / 3, y0), (x0 + w / 3, y0 + h)), P((x0 + 2 * w / 3, y0), (x0 + 2 * w / 3, y0 + h)))


def press_fn(bx, by, msg):
    """drop：输入框 + 发送键，大拇指一下按下去，按键四周爆出放射线。"""

    def fn(c, k, t):
        c.drawPath(rect(bx - 600, by, 760, 140, 22), K.paint("#FFFFFF"))
        c.drawPath(rect(bx - 600, by, 760, 140, 22), K.paint(BLACK, 1, 8))
        K.text(c, msg, bx - 600, by, 48, "hand", BLACK)
        sink = 8 * clamp01((k - 0.55) / 0.45)
        c.drawPath(rect(bx, by + sink, 260, 140, 26), K.paint(GREEN, 0.9))
        c.drawPath(rect(bx, by + sink, 260, 140, 26), K.paint(BLACK, 1, 8))
        K.text(c, "发送", bx, by + sink, 70, "hand", "#FFFFFF")
        g = clamp01((k - 0.5) / 0.5)
        if g > 0:
            for i in range(12):
                a = 2 * math.pi * i / 12 + 0.13
                r0, r1 = 190, 190 + 150 * ease_out(g)
                c.drawLine(bx + r0 * math.cos(a), by + r0 * math.sin(a), bx + r1 * math.cos(a), by + r1 * math.sin(a),
                           K.paint(RED, 1, 9))
        off = 260 * (1 - ease_out(clamp01(k / 0.55)))
        th = skia.Path()
        th.addRoundRect(skia.Rect.MakeXYWH(bx - 75, by - 330 - off + 30, 150, 330), 75, 75)
        c.drawPath(th, K.paint("#FFFFFF"))
        c.drawPath(th, K.paint(BLACK, 1, 9))
        nail = skia.Path()
        nail.addRoundRect(skia.Rect.MakeXYWH(bx - 37, by - 115 - off + 30, 74, 70), 20, 20)
        c.drawPath(nail, K.paint(BLACK, 1, 6))
        return None

    return fn


# ---------------------------------------------------------------- 结局（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

scene("撤不回了", "结局", (950, 1000, 0.85), bars=2)
L(join(rect(950, 1010, 660, 820, 44), P((870, 1370), (1030, 1370)), P((640, 720), (1260, 720))), 0, 0.9, BLACK, 9,
  sfx="wood_high")
L(bubble(930, 880, 600, 120, 1), 1, 1.4, BLUE, 8, sfx="pop")
T("你自己看看你干的好事", 930, 880, 50, BLUE, k0=1.4, k1=3.9)
T("已发送", 950, 1090, 96, RED, k0=4, k1=4.8, sfx="tom")
T("撤不回", 950, 1250, 64, k0=5, k1=5.8, sfx="rim")

scene("后悔了一下午", "结局 · 一下午过去", (2650, 1000, 0.85))
L(stick(3060, 1350, 0.75, hair=True), 0, 0.9, BLACK, 9, sfx="wood_high")
L(bubble(3060, 870, 240, 110, -1), 1, 1.4, BLACK, 7, sfx="pop")
T("……", 3060, 870, 60, k0=1.4, k1=2.2)
L(zhou(2280, 1350, 0.75, "cover"), 3, 3.9, BLUE, 9, sfx="wood_low")
L(join(clock(2660, 1150, 80), hands_at(2660, 1150, 80, 6, 0)), 4, 4.8, BLACK, 7, sfx="shaker")
T("18:00", 2660, 1290, 54, k0=4.8, k1=5.6)
T("后悔一下午", 2650, 600, 84, RED, k0=6, k1=7.25, sfx="pop")

# ---------------------------------------------------------------- 倒带（场景 3–7）

scene("往回倒一倒", "倒带", (1800, 2400, 0.75))
L(rewind(1370, 2110), 0, 0.9, RED, 10, sfx="wood_low")
T("往回倒", 1850, 2110, 100, RED, k0=1, k1=1.8, sfx="pop")
L(join(clock(1450, 2510, 150), hands_at(1450, 2510, 150, 3, 0)), 2, 2.9, BLACK, 9, sfx="wood_high")
L(ccw_arc(1450, 2510, 205), 3, 3.8, RED, 9, sfx="shaker")
L(join(arrow((2420, 2880), (1180, 2880), 0, 42), P((2300, 2855), (2300, 2905)), P((1850, 2855), (1850, 2905))), 5, 5.8,
  BLACK, 8, sfx="wood_high")
T("18:00", 2300, 2800, 60, k0=6, k1=6.8, sfx="pop")
T("15:02", 1850, 2800, 60, RED, k0=6.8, k1=7.6)

BTN = (2150, 3850)
scene("就是这一下", "倒带 · 按下发送", (1800, 3750, 0.8), shake=[0], flashes=[0])
b.move(J(), 0, (1800, 3750, 0.8), dur=0.12)      # drop：镜头几乎硬切到位，按下那一下就在画面里
b.custom(J(), 0, 0.5, press_fn(*BTN, "你自己看看你干的好事"), sfx="kick")
L(star(*BTN, 200, 290), 1, 1.8, RED, 8, sfx="wood_low")
L(join(P((BTN[0] - 160, BTN[1] - 80), (BTN[0] - 300, BTN[1] - 125), (BTN[0] - 420, BTN[1] - 100), (BTN[0] - 600, BTN[1] - 175)),
       P((BTN[0] - 160, BTN[1] + 80), (BTN[0] - 320, BTN[1] + 125), (BTN[0] - 450, BTN[1] + 100), (BTN[0] - 640, BTN[1] + 175))),
  2, 2.8, BLACK, 7, sfx="rim")
T("已发送", 1650, 3400, 120, RED, k0=3, k1=3.8, sfx="pop")
T("就是这一下", 1800, 4180, 100, RED, k0=5, k1=6.25, sfx="ding")
L(underline(1550, 2050, 4250), 6.5, 7.3, RED, 8)
H(7, "tom", 0.6)

ZX, ZY = 900, 5600              # 小周
CL = (1280, 4950, 860, 360)     # 乌云
scene("发之前在想啥", "倒带 · 发送前一分钟", (1230, 5100, 0.85))
L(zhou(ZX, ZY), 0, 0.9, BLUE, 9, sfx="wood_high")
L(join(face(ZX, ZY, 0.8, "sad"), brows(ZX, ZY)), 1, 1.6, RED, 8, sfx="pop")
L(cloud(*CL, tail=(ZX + 20, ZY - 290 * 0.8 - 50)), 2, 2.9, BLACK, 9, sfx="wood_low")
L(soot(*CL), 3, 3.8, BLACK, 6, sfx="shaker")
T("他就应该先问我", CL[0], CL[1] - 45, 58, RED, k0=4, k1=5.75, sfx="pop")
T("他这人就是不靠谱", CL[0], CL[1] + 45, 58, RED, k0=6, k1=8, sfx="pop")

scene("点火的是这两句", "伯恩斯新情绪疗法 · 书中观点", (1600, 5150, 0.7))
L(book(2050, 4860, 340, 230), 0, 0.9, BLACK, 9, sfx="wood_low")
T("伯恩斯新情绪疗法", 2050, 4660, 56, GREEN, k0=1, k1=3, sfx="pop")
L(tag_box(1700, 4760, "应该句式"), 3, 3.4, RED, 7, sfx="wood_high")
T("应该句式", 1708, 4760, 58, k0=3.4, k1=4.4)
L(tag_box(1700, 5160, "乱贴标签"), 5, 5.4, RED, 7, sfx="wood_high")
T("乱贴标签", 1708, 5160, 58, k0=5.4, k1=6.4)
L(flame(CL[0], 4715, 0.9), 7, 7.8, RED, 9, sfx="tom")

DOC = (2250, 6230)
scene("事情就这么大", "倒带 · 二十分钟前", (2500, 6300, 0.85))
L(doc(*DOC, 260, 330, 5), 0, 0.9, BLACK, 9, sfx="wood_high")
L(stick(2860, 6650, 0.75, "point", hair=True), 1, 1.9, BLACK, 9, sfx="pop")
L(join(arrow((2820, 6330), (2420, 6230), 0.12, 34),
       P((2160, 6180), (2210, 6150), (2260, 6190), (2310, 6150), (2340, 6180))), 2, 2.8, RED, 7, sfx="wood_high")
T("改了我的文件", DOC[0], 6500, 60, k0=3, k1=4.5, sfx="pop")
T("没说一声", 2860, 6110, 66, RED, k0=5, k1=6, sfx="rim")
L(P((2060, 6680), (2060, 6730), (3000, 6730), (3000, 6680)), 7, 7.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 书中观点（场景 8–10）

CH = [(1380, "事情", BLACK), (1800, "火热的想法", RED), (2220, "发火", BLACK)]
CY = 7600
scene("中间这格冒了火", "书中观点 · 三格", (1800, 7600, 0.8))
L(rect(CH[0][0], CY, 320, 240, 20), 0, 0.9, BLACK, 9, sfx="wood_high")
T(CH[0][1], CH[0][0], CY, 64, k0=1, k1=1.8, sfx="pop")
L(join(arrow((1545, CY), (1635, CY), 0, 26), rect(CH[1][0], CY, 320, 240, 20)), 2, 2.9, RED, 9, sfx="wood_high")
T(CH[1][1], CH[1][0], CY, 56, RED, k0=3, k1=4.25, sfx="pop")
L(join(arrow((1965, CY), (2055, CY), 0, 26), rect(CH[2][0], CY, 320, 240, 20)), 5, 5.9, BLACK, 9, sfx="wood_high")
T(CH[2][1], CH[2][0], CY, 64, k0=6, k1=6.8, sfx="pop")
L(flame(CH[1][0], CY - 125, 0.9), 7, 7.8, RED, 9, sfx="tom")

SC = (1800, 8400)
scene("这次生气有用吗", "书中观点 · 先问一句", (1800, 8650, 0.8))
T("这次生气有用吗？", 1800, 8150, 70, k0=0, k1=2, sfx="pop")
stand, beam = scale(*SC)
L(stand, 2, 2.8, BLACK, 9, sfx="wood_high")
L(beam, 3, 3.9, BLACK, 8, sfx="wood_low")
T("出气", 1400, 8415, 60, k0=4, k1=4.8, sfx="pop")
T("关系僵", 2200, 8582, 56, RED, k0=5, k1=5.8, sfx="pop")
T("事没解决", 2200, 8650, 56, RED, k0=6, k1=7, sfx="pop")
L(arrow((2420, 8520), (2420, 8720), 0, 34), 7, 7.8, RED, 9, sfx="ding")

HZ = (1300, 10450)
DK = (1900, 9560, 760, 280)
WT = (1900, 10010, 800, 280)
scene("把应该换成希望", "书中观点 · 换个想法", (1800, 9900, 0.8))
L(join(zhou(*HZ), face(*HZ, 0.8, "flat")), 0, 0.9, BLUE, 9, sfx="wood_high")
L(join(cloud(*DK), soot(*DK)), 1, 1.9, BLACK, 7, sfx="wood_low")
T("他就应该先问我", DK[0], DK[1], 58, RED, k0=2, k1=3.75, sfx="pop")
L(arrow((DK[0], DK[1] + 150), (DK[0], WT[1] - 150), 0, 30), 4, 4.8, BLACK, 8, sfx="wood_high")
L(cloud(*WT, tail=(HZ[0] + 40, HZ[1] - 290 * 0.8 - 40)), 5, 5.8, BLUE, 9, sfx="ding")
T("我希望他先说一声", WT[0], WT[1], 58, BLUE, k0=5.8, k1=7.8)

# ---------------------------------------------------------------- 重放 + 做法（场景 11–13）

PH = (1800, 11420)
scene("换一条再发", "重放", (1800, 11350, 0.8))
L(play(1330, 10900), 0, 0.8, GREEN, 9, sfx="wood_low")
T("重放", 1510, 10900, 80, GREEN, k0=0.8, k1=1.6)
L(join(rect(*PH, 640, 780, 44), P((1720, 11760), (1880, 11760))), 2, 2.9, BLACK, 9, sfx="wood_high")
L(bubble(1830, 11200, 540, 120, 1), 3, 3.4, BLUE, 8, sfx="pop")
T("下次改我文件说一声", 1830, 11200, 50, BLUE, k0=3.4, k1=5.65)
L(bubble(1640, 11420, 240, 110, -1), 6, 6.4, BLACK, 8, sfx="pop")
T("好嘞", 1640, 11420, 56, k0=6.4, k1=7.2)
L(join(circle(1850, 11420, 40), face(1850, 11420 + 290 * 0.5, 0.5, "smile")), 7.2, 8, GREEN, 7)

CD = (1800, 12480, 1160, 360)
COL = [CD[0] - CD[2] / 3, CD[0], CD[0] + CD[2] / 3]
HEAD_Y, ROW_Y = CD[1] - CD[3] / 2 + 55, CD[1] + 55
BT = (1800, 13130)
scene("发之前先写下来", "第一步 · 先写下来", (1800, 12800, 0.78))
L(rect(*BT, 300, 140, 26), 0, 0.8, GREEN, 9, sfx="wood_high")
T("发送", *BT, 66, GREEN, k0=0.8, k1=1.6)
L(finger(BT[0], BT[1] - 100), 2, 2.8, BLACK, 8, sfx="wood_low")
L(card(*CD), 3, 3.9, BLACK, 8, sfx="wood_high")
T("想法", COL[0], HEAD_Y, 56, k0=4, k1=4.8, sfx="pop")
T("歪在哪", COL[1], HEAD_Y, 56, k0=4.8, k1=5.6)
T("换说法", COL[2], HEAD_Y, 56, k0=5.6, k1=6.4)
T("他就是不靠谱", COL[0], ROW_Y, 54, RED, k0=6.5, k1=8)

scene("圈出“就是”改掉", "第二步 · 圈出来改", (1800, 12560, 0.88))
hole = skia.Path()
hole.addOval(skia.Rect.MakeXYWH(COL[0] - 27 - 75, ROW_Y - 45, 150, 90))
L(hole, 0, 0.7, RED, 7, sfx="rim")
T("乱贴标签", COL[1], ROW_Y, 54, k0=1, k1=2, sfx="pop")
T("这次没打招呼", COL[2], ROW_Y, 54, BLUE, k0=3, k1=4.5, sfx="pop")
L(check(COL[2] + 150, ROW_Y - 95, 30), 5, 5.6, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：第 0 拍拉远看全板，第 4 拍推到评论区

FAR = (1800, 7350, 0.13)
CM = (1800, 14100, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
H(0, "cymbal", 0.5)
H(2, "ding")
b.move(J(), 4, CM)
H(4, "wood_high", 0.6)
T("你最后悔发出去的一句话？", 1800, 13680, 66, RED, k0=6, k1=8.75, sfx="pop")
T("下一讲：项目黄了，人就不值钱了？", 1800, 13860, 50, k0=9, k1=13, sfx="wood_high")
L(cloud(2150, 14170, 600, 220), 13, 13.8, BLUE, 8, sfx="pop")
T("今天换掉一朵乌云", 2150, 14170, 50, BLUE, k0=13.8, k1=15.8)
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "anger", "生气", "群里怼完同事，为什么又后悔？", ACC, b.shots,
                 [f"{BOOK}第 7 章“生气了吗——你的‘易怒商数’是多少”（转述）",
                  "中译本：李亚萍译，中国城市出版社 2011（豆瓣 subject/5980113）"],
                 "群里怼完同事|为什么又【后悔】", SQUARE_SHOT,
                 ["书中观点均为转述：让人生气的主要是你对事情的想法，生气时常见“应该句式”（他就应该……）和“乱贴标签”"
                  "（他这人就是……）；可以先问自己这次生气对自己有没有用；把“火热的想法”写下来，换成“冷静的想法”。"
                  "见第 7 章“生气了吗——你的‘易怒商数’是多少”。“应该句式”“乱贴标签”“火热的想法 / 冷静的想法”为通行译法，"
                  "未核对李亚萍译本原词；书中“易怒商数”自测本片不放分数。上屏均为转述，不是逐字引文。",
                  "群里的消息、15:02 / 18:00 等时间点、同事改文件没打招呼、重放时的另一条消息与“好嘞”均为现实场景示意，"
                  "不指向任何具体公司、个人或具体 App；天平、三格链条、倒带时间带为对书中观点的通俗化示意。",
                  "“把应该换成希望”与两步做法（发之前先在三栏卡里写下那句火热的想法；圈出“应该”“就是”这类词，"
                  "归到哪种想歪，再换个说法）为据书中思路整理的建议。",
                  "本片为读书分享，不能替代诊断和治疗；情绪持续低落或有轻生念头，请尽快联系医生、心理咨询师或当地心理援助热线。"],
                 tags="#情绪管理")
    return b.attach(ep)
