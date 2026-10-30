"""04 三栏法（白板手绘版）：脑子里骂自己，怎么回嘴？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（H 对话改写）：每屏一句脑子里的原话，经过一张“三栏卡”改写成一句能说出口的话。
开局：汇报卡壳，小周下台后头顶的念头云开骂 → 在脑子里吵架越吵越乱 → 亮书：拿笔写下来 →
★ drop：三栏卡“哗”地拉开（想法｜哪种歪｜换个说法），乌云被箭头吸进第一栏 →
在同一张大卡上逐栏推近：第一栏照原话抄、第二栏对照十格贴名牌、第三栏写一句自己信的（喊口号的被划掉，乌云缩小）→
改写二（被催进度）、改写三（没抢到项目）用两张小卡 → 拉远看三张卡的第三栏，都说得具体、能去核对 →
三个做法（难受时先写第一栏 / 写不出就当成在劝朋友 / 写完前后对一对难受程度）→ 评论区。
本讲起系列多一个道具“三栏卡”，之后各讲的做法段落都用它收尾。
书中观点为转述（戴维·伯恩斯《伯恩斯新情绪疗法》第 4 章“从建立自尊开始”，李亚萍译，中国城市出版社 2011）；
例子、数字与做法为现实场景示意与据书中思路整理的建议。
"""

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               doc, face, hands_at, join, marker, partial, rect, stick, underline)

from .common import BOOK, episode

ACC = "#2A8C8C"
SQUARE_SHOT = 3                 # 场景 4：小周 + 念头云 + 拉开的三栏卡

b = Board(size=(3600, 10000))
GREY = "#5A5F6B"


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


# ---------------------------------------------------------------- 本讲画法

def cloud(x, y, w, h, n=9) -> skia.Path:
    """念头云外轮廓：沿椭圆一圈向外鼓的小弧。"""
    import math
    p = skia.Path()
    pts = [(x + w / 2 * math.cos(2 * math.pi * i / n - math.pi / 2),
            y + h / 2 * math.sin(2 * math.pi * i / n - math.pi / 2)) for i in range(n)]
    p.moveTo(*pts[0])
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = mx - x, my - y
        d = max(1.0, math.hypot(dx / (w / 2), dy / (h / 2)))
        p.quadTo(x + dx / d * 1.32, y + dy / d * 1.32, x1, y1)
    p.close()
    return p


def ring(x, y, w, h, n=30) -> skia.Path:
    """乌云的涂黑边：沿轮廓内侧来回折的一圈短线。"""
    import math
    p = skia.Path()
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        f = 0.80 if i % 2 == 0 else 0.97
        q = (x + w / 2 * f * math.cos(a), y + h / 2 * f * math.sin(a))
        p.moveTo(*q) if i == 0 else p.lineTo(*q)
    return p


def dots(x, y, w, h, tx, ty) -> skia.Path:
    """念头云底下两个小圈，指向小周的头。"""
    sx, sy = x + (tx - x) * 0.25, y + h / 2 + 12
    return join(circle(sx + (tx - sx) * 0.35, sy + (ty - sy) * 0.35, 18),
                circle(sx + (tx - sx) * 0.72, sy + (ty - sy) * 0.72, 11))


def fill_fn(path, color=GREY, alpha=0.16, extra=None):
    """乌云的灰底，逐渐显出；extra=(镜头, 起拍, 末拍, 增量) 时在该段再加深一层。"""

    def fn(c, k, t):
        a = alpha * k
        if extra and b.ep is not None:
            j, k0, k1, add = extra
            t0, t1 = b.t_of(j, k0), b.t_of(j, k1)
            a += add * clamp01((t - t0) / max(1e-3, t1 - t0))
        c.drawPath(path, K.paint(color, a))
        return None

    return fn


def dark(x, y, w, h, k0, to=None, sfx="wood_low", extra=None):
    """系列道具：乌云状念头云（轮廓 + 涂黑边 + 灰底）。"""
    out = join(cloud(x, y, w, h), ring(x, y, w, h))
    if to:
        out = join(out, dots(x, y, w, h, *to))
    L(out, k0, k0 + 0.9, BLACK, 7, sfx)
    b.custom(J(), k0, k0 + 0.9, fill_fn(cloud(x, y, w, h), extra=extra))


def badge(x, y, s=1.0) -> skia.Path:
    """工牌：挂绳 + 小卡，(x, y) 为小人的脚底。"""
    hy = y - 290 * s
    return join(P((x - 18 * s, hy + 46 * s), (x + 6 * s, hy + 112 * s), (x + 22 * s, hy + 44 * s)),
                rect(x + 8 * s, hy + 138 * s, 36 * s, 48 * s, 5 * s))


def zhou(x, y, s=0.8, arms="down", mood="sad") -> skia.Path:
    """小周：打工人，戴工牌。"""
    return join(stick(x, y, s, arms), badge(x, y, s), face(x, y, s, mood))


def screen(x, y, w=420, h=260) -> skia.Path:
    """投影幕 + 支架。"""
    return join(rect(x, y, w, h, 10), P((x, y + h / 2), (x, y + h / 2 + 170)),
                P((x - 90, y + h / 2 + 230), (x, y + h / 2 + 170), (x + 90, y + h / 2 + 230)))


def pen(x, y, s=1.0) -> skia.Path:
    """斜放的笔：(x, y) 为笔尖。"""
    return join(P((x, y), (x + 30 * s, y - 22 * s), (x + 170 * s, y - 160 * s), (x + 150 * s, y - 182 * s),
                  (x + 10 * s, y - 42 * s), close=True),
                P((x + 140 * s, y - 130 * s), (x + 120 * s, y - 152 * s)))


def loop(x, y, r=110) -> skia.Path:
    """绕圈的两支箭头。"""
    return join(arrow((x - r, y - 12), (x + r, y - 12), -0.5, 34), arrow((x + r, y + 12), (x - r, y + 12), -0.5, 34))


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def tag(x, y, w=340, h=100) -> skia.Path:
    """名牌：圆角小牌 + 左边一个穿绳孔。"""
    return join(rect(x, y, w, h, 18), circle(x - w / 2 + 26, y, 10))


def note(x, y, w=440, h=380) -> skia.Path:
    """便签：右下角折起。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 70),
                  (x + w / 2 - 70, y + h / 2), (x - w / 2, y + h / 2), close=True),
                P((x + w / 2, y + h / 2 - 70), (x + w / 2 - 70, y + h / 2 - 70), (x + w / 2 - 70, y + h / 2)))


def mini(x, y, w=900, h=170) -> skia.Path:
    """小三栏卡：横着三格。"""
    return join(rect(x, y, w, h, 16), P((x - w / 6, y - h / 2), (x - w / 6, y + h / 2)),
                P((x + w / 6, y - h / 2), (x + w / 6, y + h / 2)))


# ---------------------------------------------------------------- 开局：下台就开骂（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag_, view, bars=3, **kw):
    return b.shot(text, tag_, view=view, bars=bars, **kw)


scene("下台就开骂", "灵魂拷问", (950, 900, 0.85), bars=2)
L(screen(650, 560), 0, 0.9, sfx="wood_high")
T("汇报", 650, 560, 72, k0=1, k1=1.8, sfx="pop")
L(zhou(1060, 1250), 2, 2.9, sfx="wood_high")
dark(1160, 640, 400, 250, 3, to=(1070, 1000))
T("丢人", 1160, 595, 64, RED, k0=4, sfx="pop")
T("你不行", 1160, 690, 64, RED, k0=5, sfx="rim")

scene("脑子里越吵越乱", "灵魂拷问", (2650, 900, 0.85))
L(zhou(2650, 1320, mood="sad"), 0, 0.9, sfx="wood_high")
dark(2340, 720, 360, 210, 1, to=(2630, 1060), extra=(J(), 6, 6.8, 0.30))
T("你就是笨", 2340, 720, 58, RED, k0=2, sfx="pop")
L(join(cloud(2960, 720, 360, 210), dots(2960, 720, 360, 210, 2670, 1060)), 3, 3.9, BLACK, 7, sfx="wood_high")
T("我尽力了", 2960, 720, 58, k0=4, sfx="pop")
L(loop(2650, 720), 5, 5.9, RED, 9, sfx="shaker")
H(6, "tom")

# ---------------------------------------------------------------- 书中办法：三栏卡（场景 3–7）

scene("伯恩斯给的办法", "伯恩斯新情绪疗法 · 第四章", (1800, 2200, 0.85))
L(book(1500, 2270, 420, 280), 0, 0.9, sfx="wood_low")
T("伯恩斯新情绪疗法", 1500, 1990, 60, GREEN, k0=1, sfx="pop")
L(join(doc(2150, 2160, 220, 280, 4), pen(2230, 2250, 0.9)), 3, 3.9, BLACK, 9, sfx="wood_high")
T("拿笔写下来", 2150, 2440, 76, RED, k0=5, sfx="pop")
L(underline(1950, 2350, 2500), 7, 7.8, RED, 9, sfx="ding")

# 大三栏卡：x 1300–2700，y 3400–4400；三栏中心 C1 / C2 / C3
CX, CY, CW, CH = 2000, 3900, 1400, 1000
C1, C2, C3 = CX - CW / 3, CX, CX + CW / 3
HY = 3470                       # 表头文字
VD = (1800, 3900, 0.55)         # 整张卡
CLOUD = (1010, 3700, 320, 230)  # 第 4 讲的那朵乌云（场景 7 缩小）
ZHOU = (1010, 4330)

scene("拆成三格", "书中办法 · 三栏法", VD, shake=[0], flashes=[0])
J_DROP = J()


def card_fn(c, k, t):
    """三栏卡从中间“哗”地横向拉开。"""
    w = CW * ease_out(k)
    c.drawPath(rect(CX, CY, max(4.0, w), CH, 24), marker(BLACK, 12))
    c.drawPath(rect(CX, CY, max(4.0, w), CH, 24), K.paint(ACC, 0.06 * k))
    return (CX + w / 2, CY) if k < 1 else None


b.custom(J(), 0, 0.5, card_fn, sfx="kick")
L(join(P((CX - CW / 2, 3540), (CX + CW / 2, 3540)), P((CX - CW / 6, 3400), (CX - CW / 6, 4400)),
       P((CX + CW / 6, 3400), (CX + CW / 6, 4400))), 1, 1.9, BLACK, 9, sfx="wood_high")
T("想法", C1, HY, 80, k0=2, sfx="pop")
T("哪种歪", C2, HY, 80, k0=3, sfx="pop")
T("换个说法", C3, HY, 80, BLUE, k0=4, sfx="pop")
L(zhou(*ZHOU), 5, 5.9, sfx="wood_low")
SHRINK = {}                     # 场景 7 填入：乌云缩小的镜头与拍


def big_cloud_fn(c, k, t):
    """场景 4 的乌云：第 5 拍描出、第 6 拍写字，场景 7 第 6 拍起缩小。"""
    x, y, w, h = CLOUD
    s = 1.0
    if SHRINK and b.ep is not None:
        t0 = b.t_of(SHRINK["j"], SHRINK["k"])
        s = 1 - 0.5 * ease_in_out(clamp01((t - t0) / max(1e-3, b.t_of(SHRINK["j"], SHRINK["k"] + 1) - t0)))
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.translate(-x, -y)
    outline = join(cloud(x, y, w, h), ring(x, y, w, h), dots(x, y, w, h, ZHOU[0], ZHOU[1] - 262))
    f = clamp01((t - b.t_of(J_DROP, 5)) / max(1e-3, b.t_of(J_DROP, 5.9) - b.t_of(J_DROP, 5)))
    part, tip = partial(outline, f)
    c.drawPath(part, marker(BLACK, 7))
    c.drawPath(cloud(x, y, w, h), K.paint(GREY, 0.2 * f))
    ft = clamp01((t - b.t_of(J_DROP, 6)) / max(1e-3, b.t_of(J_DROP, 6.8) - b.t_of(J_DROP, 6)))
    if ft > 0:
        tw = K.text_w("我不行", 80, "hand")
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x - tw / 2 - 20, y - 80, x - tw / 2 + tw * ft + 4, y + 80))
        K.text(c, "我不行", x, y, 80, "hand", RED)
        c.restore()
        if ft < 1:
            tip = (x - tw / 2 + tw * ft, y)
    c.restore()
    return tip if f < 1 or ft < 1 else None


b.custom(J(), 5, 6.8, big_cloud_fn)
H(6, "pop")
L(arrow((1160, 3790), (1440, 4120), 0.2, 44), 7, 7.8, RED, 10, sfx="ding")

scene("第一栏照原话抄", "三栏法 · 第一栏", (C1, 3950, 0.85))
T("我又搞砸了，", C1, 3700, 64, RED, k0=0, sfx="pop")
T("我不行", C1, 3850, 80, RED, k0=2, sfx="pop")
L(underline(C1 - 125, C1 + 125, 3905, 10, 30), 3, 3.8, RED, 8, sfx="rim")
L(pen(C1 + 80, 4130, 0.8), 4, 4.8, BLACK, 8, sfx="wood_low")
T("一字不改", C1, 4320, 56, k0=5, sfx="pop")

scene("对照十格找一找", "三栏法 · 第二栏", (C2, 3950, 0.85))
GX, GY, GC = C2, 3680, 64       # 十格小图：5 列 × 2 行（上两讲的十种想歪）


def grid() -> skia.Path:
    parts = [rect(GX, GY, 5 * GC, 2 * GC, 6), P((GX - 2.5 * GC, GY), (GX + 2.5 * GC, GY))]
    for i in range(1, 5):
        parts.append(P((GX - 2.5 * GC + i * GC, GY - GC), (GX - 2.5 * GC + i * GC, GY + GC)))
    return join(*parts)


def cells_fn(c, k, t):
    for col, row in ((1, 0), (3, 1)):          # 第 2 种 以偏概全、第 9 种 乱贴标签
        x0, y0 = GX - 2.5 * GC + col * GC, GY - GC + row * GC
        c.drawRect(skia.Rect.MakeXYWH(x0 + 4, y0 + 4, GC - 8, GC - 8), K.paint(RED, 0.55 * k))
    return None


L(grid(), 0, 0.9, BLACK, 7, sfx="wood_high")
b.custom(J(), 1, 1.6, cells_fn, sfx="ding")
L(tag(C2, 3930), 2, 2.8, BLACK, 8, sfx="wood_high")
T("以偏概全", C2 + 14, 3930, 60, k0=3, sfx="pop")
L(tag(C2, 4140), 4, 4.8, BLACK, 8, sfx="wood_high")
T("乱贴标签", C2 + 14, 4140, 60, k0=5, sfx="pop")
L(arrow((C1 + 200, 3720), (C2 - 180, 3915), 0.15, 30), 6, 6.8, RED, 8, sfx="rim")
L(arrow((C1 + 130, 3880), (C2 - 180, 4125), 0.15, 30), 7, 7.8, RED, 8, sfx="rim")

scene("写句你信的", "三栏法 · 第三栏", (C3, 3950, 0.85))
T("卡了一处，", C3, 3700, 64, BLUE, k0=0, sfx="pop")
T("后面讲完了", C3, 3830, 64, BLUE, k0=2, sfx="pop")
T("我最棒！", C3, 4080, 56, k0=4, sfx="wood_low")
L(cross(C3, 4080, 75), 5, 5.8, RED, 10, sfx="rim")
b.move(J(), 6, VD)
SHRINK.update(j=J(), k=6)
H(6, "shaker")
L(check(C3, 3955, 42), 7, 7.8, GREEN, 11, sfx="ding")

# ---------------------------------------------------------------- 再改两句（场景 8–10）

scene("被催进度了", "改写二 · 被催进度", (950, 5400, 0.85))
L(zhou(450, 5600, 0.7), 0, 0.9, sfx="wood_high")
dark(850, 5050, 520, 220, 1, to=(470, 5370))
T("我拖累大家", 850, 5050, 60, RED, k0=2, sfx="pop")
L(mini(1100, 5650), 3.5, 4.3, BLACK, 9)
L(arrow((850, 5175), (800, 5600), 0.12, 34), 4.4, 5.0, RED, 9)
H(4, "shaker")
T("罪责归己", 1100, 5650, 54, k0=5, sfx="pop")
T("排期太紧", 1400, 5650, 54, BLUE, k0=6, k1=6.9, sfx="pop")
L(underline(1300, 1500, 5700, 8, 25), 7, 7.8, BLUE, 7, sfx="wood_low")

scene("没抢到项目", "改写三 · 没抢到项目", (2650, 5400, 0.85))
L(zhou(2150, 5600, 0.7, "shrug"), 0, 0.9, sfx="wood_high")
dark(2600, 5050, 560, 220, 1, to=(2170, 5370))
T("领导看不上我", 2600, 5050, 60, RED, k0=2, sfx="pop")
L(mini(2800, 5650), 3.5, 4.3, BLACK, 9)
L(arrow((2560, 5175), (2500, 5600), 0.12, 34), 4.4, 5.0, RED, 9)
H(4, "shaker")
T("读心术", 2800, 5650, 54, k0=5, sfx="pop")
T("问问理由", 3100, 5650, 54, BLUE, k0=6, k1=6.9, sfx="pop")
L(underline(3000, 3200, 5700, 8, 25), 7, 7.8, BLUE, 7, sfx="wood_low")

scene("三张卡摆一起", "三张卡 · 第三栏", (1800, 4650, 0.34))
L(oval(C3, 3765, 460, 270), 2, 2.8, RED, 16, sfx="ding")
L(oval(1400, 5650, 330, 150), 3, 3.8, RED, 16, sfx="ding")
L(oval(3100, 5650, 330, 150), 4, 4.8, RED, 16, sfx="ding")
T("说得具体", 1800, 4600, 120, RED, k0=5, sfx="pop")
T("能去核对", 1800, 4770, 120, RED, k0=6, sfx="pop")
L(underline(1560, 2040, 4860, 16, 48), 7, 7.8, RED, 14, sfx="wood_high")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

scene("难受时先写下来", "做法一 · 先写第一栏", (950, 6600, 0.85))
T("① 先写第一栏", 950, 6200, 76, BLUE, k0=0, sfx="pop")
L(note(950, 6620), 2, 2.8, BLACK, 9, sfx="wood_high")
T("想法：", 860, 6550, 60, k0=3, sfx="pop")
L(P((790, 6700), (1110, 6700)), 4, 4.8, BLACK, 7, sfx="wood_low")
L(join(clock(450, 7000, 80), hands_at(450, 7000, 80, 0, 10)), 5, 5.8, BLACK, 8, sfx="wood_high")
T("十分钟内", 740, 7005, 64, RED, k0=6, sfx="pop")

scene("当成朋友来劝", "做法二 · 换成对朋友说", (2650, 6600, 0.85))
T("② 对朋友会怎么说", 2650, 6200, 70, BLUE, k0=0, sfx="pop")
L(join(zhou(2350, 7000, 0.75, "point", "smile"), stick(2950, 7000, 0.75, "down", hair=True),
       face(2950, 7000, 0.75, "sad")), 2, 2.9, BLACK, 9, sfx="wood_high")
L(bubble(2650, 6440, 600, 160, 1), 3, 3.8, BLUE, 8, sfx="pop")
T("卡一下很正常", 2650, 6440, 56, BLUE, k0=4, sfx="pop")
L(arrow((2420, 6530), (2330, 6690), -0.35, 30), 6, 6.8, GREEN, 9, sfx="ding")
T("说给自己", 2650, 7080, 56, GREEN, k0=7, sfx="pop")

scene("前后对一对", "做法三 · 写完对一对", (1800, 8000, 0.85))
T("难受程度", 1800, 7580, 72, k0=0, sfx="pop")
L(P((1400, 8350), (2200, 8350)), 1, 1.8, BLACK, 9, sfx="wood_high")
L(rect(1600, 8070, 180, 560, 8), 4, 4.8, RED, 10, sfx="wood_low")
T("八十", 1600, 7730, 70, RED, k0=5, sfx="pop")
L(rect(2000, 8210, 180, 280, 8), 6, 6.8, BLUE, 10, sfx="wood_low")
T("四十", 2000, 8020, 70, BLUE, k0=7, sfx="pop")
T("写之前", 1600, 8415, 54, k0=2, sfx="pop")
T("写之后", 2000, 8415, 54, k0=3, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5000, 0.105)
COMMENT = (1800, 9300, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你脑子里最常骂自己哪句？", 1800, 9100, 72, RED, k0=6, sfx="pop")
T("下一讲：拖了一周的事，怎么开头？", 1800, 9280, 48, k0=9, sfx="wood_high")
L(cloud(2150, 9620, 500, 170), 13, 13.8, BLUE, 7, sfx="wood_low")
T("今天换掉一朵乌云", 2150, 9620, 46, BLUE, k0=14, sfx="pop")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(4, "column", "三栏法", "脑子里骂自己，怎么回嘴？", ACC, b.shots,
                 [f"{BOOK}第 4 章“从建立自尊开始”（三栏法，转述）",
                  "中译本：李亚萍译，中国城市出版社 2011（豆瓣 subject/5980113）"],
                 "脑子里骂自己|怎么【回嘴】", SQUARE_SHOT,
                 ["书中观点均为转述：第 4 章“从建立自尊开始”介绍三栏法——把脑子里自动冒出来的自我批评写下来，"
                  "分三栏：自动想法 / 属于哪种认知扭曲 / 更合理的回应；写下来比只在脑子里想更有用。"
                  "“回应要你自己信，喊口号没用”为据书中思路整理，具体措辞未核实。",
                  "三栏的栏名（想法｜哪种歪｜换个说法）、“以偏概全”“乱贴标签”“罪责归己”“读心术”为通行译法的口语叫法，"
                  "李亚萍译本中的原用词未核实。",
                  "汇报卡壳、被催进度、没抢到项目三个改写例子为现实场景示意，不是书中病例，不指向具体公司或个人。",
                  "三个做法（难受时十分钟内先写第一栏；写不出回应就想想对朋友会怎么说；写完对比前后的难受程度）"
                  "为据书中思路整理的建议；“对朋友怎么说”即通常所说的双重标准法，所在章节未核实；"
                  "“十分钟”“八十 / 四十”为示意数字，不是书中数据。",
                  "本片为读书分享，不能替代诊断和治疗；情绪持续低落或有轻生念头，请尽快联系医生、心理咨询师或当地心理援助热线。"],
                 tags="#自我批评")
    return b.attach(ep)
