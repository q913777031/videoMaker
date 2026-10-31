"""10 表达感激（白板手绘版）：夸人一句“真棒”，够了吗？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（形式 F 两人对比：左右两栏并排，不画路口）：同一晚，甲乙两个组的实习生都熬夜把数据对完了（两张工位、两盏台灯）→
甲组长竖个大拇指说“真棒！”，乙组长写了一张三行的便签 → 一个月后：甲组实习生头顶问号，说不清自己哪做得好；
乙组实习生头顶灯泡，知道下次咋做 → drop：三个格子“做了啥 / 帮到啥 / 啥心情”同时砸到板上，两个组长分立左右（封面镜头）→
亮书与四格卡 → 拆开乙组长的便签，一屏一格：三张表叠齐（做了啥）、会议桌和充满的电池（帮到啥）、一颗亮起来的心（啥心情）→
书中观点：赞扬也可能是一种评判，“真棒”像评委举起的打分牌 → 回家也能用：跟爸妈说取快递那件事 →
别人谢你时（据书中思路）：✗ 没啥没啥 / ✓ 能帮上就好 → 系列收尾：四格卡四格依次全亮 → 十讲的十个小泡，刺一齐收回去 →
拉远看全板，推到评论区：这季你最想先用哪一招。
系列视觉角色：话泡泡“小泡”（场景 13：十个带刺小泡的刺同时缩回去，变蓝变圆）、四格卡（场景 5 画出，场景 12 四格全亮）。
书中观点为转述：马歇尔·卢森堡《非暴力沟通》第十三章“表达感激”（表达感激时说清对方做了什么、满足了我什么需要、
我现在是什么心情；赞扬、恭维也可能是一种评判）。“接受感激时别急着推开”据书中思路整理，不当原文。中译本阮胤华译，华夏出版社。
实习生、甲乙两个组长、一个月后的结果、给爸妈的话都是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, check, circle, cross, desk,
                               face, join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#4E9A3C"                 # 本讲主色：叶绿（感激，温和）
SQUARE_SHOT = 3                 # 场景 4：三个格子砸到板上，两个组长分立左右
YELLOW = "#F2C14E"

b = Board(size=(3600, 18000))


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


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


def beat_f(j, k, dur):
    """镜头 j 第 k 拍起、dur 拍内的进度 0→1（给动态 custom 用）。"""
    t0, t1 = b.t_of(j, k), b.t_of(j, k + dur)
    return lambda T: clamp01((T - t0) / max(1e-3, t1 - t0))


# ---------------------------------------------------------------- 本讲画法

def mirror(path: skia.Path, x: float) -> skia.Path:
    """以竖线 x 为轴左右翻转。"""
    p = skia.Path(path)
    m = skia.Matrix.Scale(-1, 1)
    m.postTranslate(2 * x, 0)
    p.transform(m)
    return p


def _ell(x, y, rx, ry, a):
    return x + rx * math.cos(a), y + ry * math.sin(a)


def pao_outline(x, y, rx, ry, tail=0) -> skia.Path:
    """小泡的轮廓：椭圆 + 底部小尾巴（tail=-1 偏左、1 偏右、0 无尾巴）。"""
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    if tail:
        a0 = math.pi / 2 - tail * 0.55
        b0, b1 = _ell(x, y, rx, ry, a0 - 0.16), _ell(x, y, rx, ry, a0 + 0.16)
        tip = (x + tail * rx * 0.62, y + ry + 60)
        p.moveTo(*b0)
        p.lineTo(*tip)
        p.lineTo(*b1)
    return p


def spikes_path(x, y, rx, ry, lens) -> skia.Path:
    """在椭圆轮廓上等距加三角刺；lens 为每根刺的长度（0 = 缩回）。"""
    p = skia.Path()
    n = len(lens)
    for i, ln in enumerate(lens):
        if ln <= 1:
            continue
        a = -math.pi / 2 + i * 2 * math.pi / n
        d = 0.17 * min(1.0, 140 / max(rx, ry)) + 0.06
        b0, b1 = _ell(x, y, rx, ry, a - d), _ell(x, y, rx, ry, a + d)
        nx, ny = math.cos(a) / rx, math.sin(a) / ry
        nn = math.hypot(nx, ny)
        mx, my = _ell(x, y, rx, ry, a)
        p.moveTo(*b0)
        p.lineTo(mx + nx / nn * ln, my + ny / nn * ln)
        p.lineTo(*b1)
    return p


def pao_face(c, x, y, rx, ry, mood, color, s=1.0):
    """小泡的脸放上半部，下半部留给期号。"""
    ey = y - ry * 0.42
    dx = rx * 0.2
    K.dot(c, x - dx, ey, 8 * s, color)
    K.dot(c, x + dx, ey, 8 * s, color)
    my = ey + 24 * s
    w = 20 * s
    m = skia.Path()
    if mood == "smile":
        m.moveTo(x - w, my)
        m.quadTo(x, my + 20 * s, x + w, my)
    else:
        m.moveTo(x - w, my + 10 * s)
        m.quadTo(x, my - 12 * s, x + w, my + 10 * s)
    c.drawPath(m, K.paint(color, 1, 6 * s))


class Pao:
    """系列角色“小泡”：画出来就长着红刺、嘴往下撇；retract 之后刺一齐缩回去，变成蓝色圆泡、嘴角上扬。"""

    def __init__(self, x, y, rx, ry, label, n=10, L=30):
        self.x, self.y, self.rx, self.ry, self.label, self.n, self.L = x, y, rx, ry, label, n, L
        self.grow_f = None
        self.retract_f = None

    def draw(self, j, k0, k1, sfx=None):
        self.grow_f = beat_f(j, k1 - 0.1, 0.4)
        b.custom(j, k0, k1, self.fn, sfx=sfx)

    def retract(self, j, k, dur=0.6):
        self.retract_f = beat_f(j, k, dur)

    def fn(self, c, k, T):
        g = ease_out(self.grow_f(T)) if self.grow_f else 0.0
        r = ease_in_out(self.retract_f(T)) if self.retract_f else 0.0
        ln = self.L * g * (1 - r)
        calm = r > 0.6
        color = BLUE if calm else RED
        out = pao_outline(self.x, self.y, self.rx, self.ry, tail=-1)
        part, tip = wb.partial(out, k)
        c.drawPath(part, wb.marker(color, 8))
        if k >= 0.8:
            c.drawPath(spikes_path(self.x, self.y, self.rx, self.ry, [ln] * self.n), wb.marker(color, 7))
            pao_face(c, self.x, self.y, self.rx, self.ry, "smile" if calm else "frown", color)
            K.text(c, self.label, self.x, self.y + self.ry * 0.38, 46, "hand", color)
        return tip


def eye(x, y, s=1.0) -> skia.Path:
    w, h = 62 * s, 34 * s
    p = skia.Path()
    p.moveTo(x - w, y)
    p.quadTo(x, y - 2 * h, x + w, y)
    p.quadTo(x, y + 2 * h, x - w, y)
    p.addCircle(x, y, h * 0.75)
    p.addCircle(x, y, h * 0.22)
    return p


def heart(x, y, r=60) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def battery(x, y, s=1.0) -> skia.Path:
    """快没电的电池：外壳 + 正极 + 一格电。"""
    return join(rect(x - 8 * s, y, 120 * s, 64 * s, 10 * s), rect(x + 60 * s, y, 14 * s, 26 * s, 4 * s),
                rect(x - 50 * s, y, 18 * s, 38 * s, 3 * s))


def palm(x, y, s=1.0) -> skia.Path:
    """伸出来的手（掌心朝上）：袖口 + 托起的手掌 + 拇指。"""
    cup = skia.Path()
    cup.moveTo(x - 40 * s, y - 18 * s)
    cup.cubicTo(x - 30 * s, y + 45 * s, x + 50 * s, y + 45 * s, x + 78 * s, y - 20 * s)
    cup.lineTo(x + 20 * s, y - 8 * s)
    thumb = skia.Path()
    thumb.moveTo(x - 30 * s, y - 16 * s)
    thumb.quadTo(x - 20 * s, y - 48 * s, x + 6 * s, y - 40 * s)
    return join(rect(x - 70 * s, y + 4 * s, 44 * s, 58 * s, 6 * s), cup, thumb)


ICONS = (eye, lambda x, y, s=1.0: heart(x, y + 8 * s, 50 * s), battery, palm)


def card_frame(x, y, cell, h) -> skia.Path:
    parts = [rect(x, y, 4 * cell, h, 20)]
    for i in range(1, 4):
        xx = x - 2 * cell + i * cell
        parts.append(P((xx, y - h / 2 + 14), (xx, y + h / 2 - 14)))
    return join(*parts)


def cell_x(x, cell, i):
    return x - 1.5 * cell + i * cell


def card_icons(x, y, cell, s):
    return join(*[ICONS[i](cell_x(x, cell, i), y, s) for i in range(4)])


def fill_fn(x, y, w, h, color=BLUE, alpha=0.2):
    """四格卡某一格涂色（点亮）。"""
    def fn(c, k, t):
        c.drawPath(rect(x, y, w * (0.6 + 0.4 * ease_out(k)), h * (0.6 + 0.4 * ease_out(k)), 16), K.paint(color, alpha * k))
        return None

    return fn


def lamp(x, y) -> skia.Path:
    """台灯：(x, y) 为底座中点（桌面上），灯罩朝右下。"""
    return join(P((x - 45, y), (x + 45, y)), P((x, y), (x - 35, y - 130), (x + 10, y - 200)),
                P((x - 5, y - 215), (x + 55, y - 240), (x + 110, y - 150), (x + 40, y - 125), close=True))


def glow_fn(x, y, flip=False):
    """台灯的光：从灯罩口铺到桌面的一片淡黄。"""
    def fn(c, k, T):
        pts = [(x + 40, y - 125), (x + 110, y - 150), (x + 230, y), (x + 20, y)]
        if flip:
            pts = [(3600 - px, py) for px, py in pts]
        p = P(*pts, close=True)
        c.drawPath(p, K.paint(YELLOW, 0.35 * ease_out(k), blur=6))
        return None

    return fn


def moon(x, y, r=70) -> skia.Path:
    p = skia.Path()
    p.moveTo(x + 0.3 * r, y - 0.95 * r)
    p.cubicTo(x - 1.3 * r, y - 0.9 * r, x - 1.3 * r, y + 0.9 * r, x + 0.3 * r, y + 0.95 * r)
    p.cubicTo(x - 0.45 * r, y + 0.5 * r, x - 0.45 * r, y - 0.5 * r, x + 0.3 * r, y - 0.95 * r)
    return p


def thumb(x, y, s=1.0) -> skia.Path:
    """竖起的大拇指：拳头 + 拇指 + 袖口。(x, y) 为拳头中心。"""
    fist = rect(x, y, 110 * s, 96 * s, 22 * s)
    th = P((x - 50 * s, y - 40 * s), (x - 42 * s, y - 130 * s), (x - 8 * s, y - 135 * s), (x + 2 * s, y - 48 * s))
    knuckles = join(P((x + 6 * s, y - 16 * s), (x + 52 * s, y - 16 * s)), P((x + 6 * s, y + 12 * s), (x + 52 * s, y + 12 * s)))
    cuff = rect(x - 2 * s, y + 78 * s, 80 * s, 56 * s, 8 * s)
    return join(fist, th, knuckles, cuff)


def note(x, y, w=320, h=300) -> skia.Path:
    """便签：方块 + 折角。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 50),
                  (x + w / 2 - 50, y + h / 2), (x - w / 2, y + h / 2), close=True),
                P((x + w / 2, y + h / 2 - 50), (x + w / 2 - 50, y + h / 2 - 50), (x + w / 2 - 50, y + h / 2)))


def note_lines(x, y, w=320, h=300) -> skia.Path:
    return join(*[underline(x - w / 2 + 40, x + w / 2 - 50 - 30 * (i == 2), y - h / 2 + 70 + i * 75, amp=10, step=34)
                  for i in range(3)])


def calendar(x, y, w=280, h=190) -> skia.Path:
    return join(rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 50), (x + w / 2, y - h / 2 + 50)),
                P((x - 70, y - h / 2 - 22), (x - 70, y - h / 2 + 22)), P((x + 70, y - h / 2 - 22), (x + 70, y - h / 2 + 22)))


def bulb(x, y) -> skia.Path:
    """灯泡（亮了）：(x, y) 为玻璃球中心。"""
    rays = [P((x + 85 * math.cos(a), y + 85 * math.sin(a)), (x + 120 * math.cos(a), y + 120 * math.sin(a)))
            for a in (-math.pi / 2, -math.pi / 6, -5 * math.pi / 6, 0.15, math.pi - 0.15)]
    return join(circle(x, y, 55), P((x - 26, y + 62), (x + 26, y + 62)), P((x - 20, y + 84), (x + 20, y + 84)), *rays)


def sheet(x, y, w=380, h=250) -> skia.Path:
    """一张表：外框 + 三行三列格子。"""
    parts = [rect(x, y, w, h, 10)]
    for i in range(1, 3):
        parts.append(P((x - w / 2, y - h / 2 + i * h / 3), (x + w / 2, y - h / 2 + i * h / 3)))
        parts.append(P((x - w / 2 + i * w / 3, y - h / 2), (x - w / 2 + i * w / 3, y + h / 2)))
    return join(*parts)


def meeting(x, y) -> skia.Path:
    """会议桌（俯视椭圆）+ 四个人头。"""
    t = skia.Path()
    t.addOval(skia.Rect.MakeXYWH(x - 190, y - 65, 380, 130))
    heads = [circle(x + dx, y + dy, 34) for dx, dy in ((-120, -115), (0, -120), (120, -115), (0, 120))]
    return join(t, *heads)


def parcel(x, y) -> skia.Path:
    """快递盒：盒身 + 盒盖缝 + 胶带。"""
    return join(rect(x, y, 230, 160, 8), P((x - 115, y - 40), (x + 115, y - 40)), P((x - 25, y - 80), (x - 25, y - 40)),
                P((x + 25, y - 80), (x + 25, y - 40)), P((x - 70, y + 30), (x + 30, y + 30)))


# ---------------------------------------------------------------- 开局：两个组，同一晚（场景 1–3，左右两栏）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

MID = 1800
DESK_L = (1520, 1270)
LAMP_L = (1410, 1270)
INTERN_L = (1290, 1400)
left_station = join(desk(*DESK_L, 300), stick(*INTERN_L, 0.65), face(*INTERN_L, 0.65, "flat"))

scene("实习生熬了个夜", "开局 · 两个组的夜", (MID, 1000, 0.8), bars=2)
L(left_station, 0, 0.9, BLACK, 9, sfx="wood_high")
L(lamp(*LAMP_L), 1, 1.7, BLACK, 8, sfx="pop")
C(1.7, 2.0, glow_fn(*LAMP_L))
L(mirror(left_station, MID), 2, 2.9, BLACK, 9, sfx="wood_high")
L(mirror(lamp(*LAMP_L), MID), 3, 3.7, BLACK, 8, sfx="pop")
C(3.7, 4.0, glow_fn(*LAMP_L, flip=True))
L(moon(MID, 640, 70), 4, 4.8, ORANGE, 9, sfx="shaker")
T("熬到半夜", MID, 1500, 66, k0=5, k1=6.0, sfx="pop")

# 场景 2：两个组长，两种夸
LEAD_L = (1330, 2700)
LEAD_R = (2290, 2700)
NOTE = (2020, 2160)
scene("两个组长，两种夸", "开局 · 两种夸", (MID, 2250, 0.8))
L(P((MID, 1720), (MID, 2800)), 0, 0.6, BLACK, 6, sfx="wood_low")
L(join(stick(*LEAD_L, 0.75, "point", tie=True), face(*LEAD_L, 0.75, "smile")), 1, 1.9, BLACK, 10, sfx="wood_high")
L(thumb(1560, 2300), 2, 2.8, BLACK, 9, sfx="pop")
T("真棒！", 1560, 2030, 90, RED, k0=3, k1=3.8, sfx="tom")
L(mirror(join(stick(*LEAD_R, 0.75, "hold", tie=True), face(*LEAD_R, 0.75, "smile")), LEAD_R[0]), 4, 4.9, BLACK, 10,
  sfx="wood_high")
L(note(*NOTE), 5, 5.8, BLACK, 9, sfx="wood_low")
L(note_lines(*NOTE), 6, 6.8, BLUE, 7, sfx="pop")
T("写了三行", NOTE[0], 2400, 60, BLUE, k0=7, k1=8.0, sfx="pop")

# 场景 3：一个月后
scene("一个月后", "开局 · 一个月后", (MID, 3500, 0.8))
L(calendar(MID, 3070), 0, 0.8, BLACK, 9, sfx="wood_low")
T("一个月后", MID, 3110, 56, k0=1, k1=2.0, sfx="pop")
L(join(stick(1450, 3880, 0.7, "shrug"), face(1450, 3880, 0.7, "flat")), 2, 2.9, BLACK, 10, sfx="wood_high")
T("？", 1450, 3480, 140, RED, k0=3, k1=3.8, sfx="tom")
L(join(stick(2150, 3880, 0.7, "up"), face(2150, 3880, 0.7, "smile")), 4, 4.9, BLACK, 10, sfx="wood_high")
L(bulb(2150, 3470), 5, 5.8, ORANGE, 8, sfx="ding")
T("说不清", 1450, 3990, 60, RED, k0=6, k1=6.8, sfx="pop")
T("知道咋做", 2150, 3990, 60, BLUE, k0=7, k1=8.0, sfx="pop")

# ---------------------------------------------------------------- drop（场景 4，封面镜头）：三个格子同时砸到板上

BOX_Y = 4570
BOX_X = (1430, MID, 2170)
BOX_W, BOX_H = 330, 230
J_DROP = scene("说清三件事", "书中观点 · 第十三章", (MID, 4850, 0.8), shake=[0], flashes=[0])


def slam_fn(c, k, T):
    """第 0 拍三个格子从板外一齐砸下（0.35 拍落地），落地后压扁回弹，四周崩出几道尘线。"""
    t0, t1 = b.t_of(J_DROP, 0), b.t_of(J_DROP, 0.35)
    f = clamp01((T - t0) / (t1 - t0))
    y = lerp(BOX_Y - 760, BOX_Y, f * f)
    sq = 0.0
    if T >= t1:
        dt = T - t1
        sq = 0.14 * math.exp(-dt * 8) * math.cos(dt * 28)
    for x in BOX_X:
        w, h = BOX_W * (1 + sq), BOX_H * (1 - sq)
        yy = y + BOX_H * sq / 2
        c.drawPath(rect(x, yy, w, h, 22), K.paint(ACC, 0.10))
        c.drawPath(rect(x, yy, w, h, 22), wb.marker(BLACK, 11))
        if T >= t1:
            g = ease_out(clamp01((T - t1) / (b.t_of(J_DROP, 0.8) - t1)))
            yb = BOX_Y + BOX_H / 2
            dust = join(P((x - w / 2 - 20, yb), (x - w / 2 - 20 - 50 * g, yb - 10 - 30 * g)),
                        P((x + w / 2 + 20, yb), (x + w / 2 + 20 + 50 * g, yb - 10 - 30 * g)))
            c.drawPath(dust, wb.marker(BLACK, 6, 1 - 0.4 * g))
    return None


C(0, 0.35, slam_fn, sfx="kick")
T("做了啥", BOX_X[0], BOX_Y + 22, 70, k0=1, k1=1.75, sfx="pop")
T("帮到啥", BOX_X[1], BOX_Y + 22, 70, k0=2, k1=2.75, sfx="pop")
T("啥心情", BOX_X[2], BOX_Y + 22, 70, k0=3, k1=3.75, sfx="pop")
L(join(stick(1330, 5340, 0.62, "point", tie=True), face(1330, 5340, 0.62, "smile")), 4, 4.9, BLACK, 9, sfx="wood_high")
L(mirror(join(stick(2270, 5340, 0.62, "hold", tie=True), face(2270, 5340, 0.62, "smile"), note(2165, 5200, 110, 100)),
         2270), 5, 5.9, BLACK, 9, sfx="wood_low")
T("感激，说清这三样", MID, 4900, 70, ACC, k0=6, k1=8.0, sfx="pop")

# ---------------------------------------------------------------- 亮书（场景 5）

CARD_S = (MID, 6380, 200, 210)
scene("有本书讲过", "非暴力沟通 · 书中观点", (MID, 6100, 0.85))
L(book(1480, 5900, 380, 260), 0, 0.9, BLACK, 10, sfx="wood_low")
T("非暴力沟通", 2080, 5850, 72, GREEN, k0=1, k1=2.25, sfx="pop")
T("卢森堡", 2080, 5970, 56, k0=3, k1=3.8, sfx="pop")
L(card_frame(*CARD_S), 4, 4.9, BLACK, 8, sfx="wood_high")
L(card_icons(CARD_S[0], CARD_S[1] - 10, CARD_S[2], 0.75), 5, 5.9, BLACK, 7, sfx="pop")
T("讲感激的一章", MID, 6575, 56, BLUE, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 拆开乙组长的便签（场景 6–8，一屏一格）

SH = (MID, 7310)
OFFS = ((-80, -60, -0.13), (70, -15, 0.11), (-30, 45, -0.06))
J_SHEET = scene("他做了啥", "说清三件事 · 做了啥", (MID, 7350, 0.85))
L(eye(1340, 6935, 0.95), 0, 0.8, BLACK, 8, sfx="wood_high")
T("做了啥", 1560, 6945, 72, k0=1, k1=1.75, sfx="pop")


def sheets_fn(c, k, T):
    """第 2、2.5、3 拍三张表歪着一张张叠上来；第 4 拍“咔”地对齐，两边各一条绿色对齐线。"""
    tip = None
    a = ease_in_out(beat_f(J_SHEET, 4, 0.4)(T))
    for i, (dx, dy, rot) in enumerate(OFFS):
        f = beat_f(J_SHEET, 2 + 0.5 * i, 0.5)(T)
        if f <= 0:
            continue
        x, y = SH[0] + dx * (1 - a), SH[1] + dy * (1 - a)
        p = sheet(x, y)
        p.transform(skia.Matrix.RotateRad(rot * (1 - a), skia.Point(x, y)))
        bg = rect(x, y, 380, 250, 10)
        bg.transform(skia.Matrix.RotateRad(rot * (1 - a), skia.Point(x, y)))
        c.drawPath(bg, K.paint("#FBFBF9"))
        part, t = wb.partial(p, f)
        c.drawPath(part, wb.marker(BLACK, 8))
        if f < 1:
            tip = t
    if a > 0:
        g = beat_f(J_SHEET, 4.1, 0.5)(T)
        for x in (SH[0] - 205, SH[0] + 205):
            c.drawPath(P((x, SH[1] - 170), (x, SH[1] - 170 + 340 * g)), wb.marker(GREEN, 6))
    return tip


C(2, 4.6, sheets_fn, sfx="wood_low")
H(3, "wood_low")
H(4, "rim")
T("“周末你把", MID, 7620, 64, BLUE, k0=5, k1=6.0, sfx="pop")
T("三张表对齐了”", MID, 7730, 64, BLUE, k0=6, k1=7.75, sfx="pop")

BAT = (2170, 8560)
J_BAT = scene("帮到了啥", "说清三件事 · 帮到啥", (MID, 8600, 0.85))
L(battery(1340, 8190, 0.95), 0, 0.8, BLACK, 8, sfx="wood_high")
T("帮到啥", 1560, 8195, 72, k0=1, k1=1.75, sfx="pop")
L(meeting(1530, 8560), 2, 2.9, BLACK, 8, sfx="wood_low")
L(join(rect(*BAT, 250, 140, 16), rect(BAT[0] + 140, BAT[1], 22, 56, 6)), 3, 3.8, BLACK, 9, sfx="wood_high")


def charge_fn(c, k, T):
    """第 4 拍起电池三格电一格格充满（绿）。"""
    for i in range(3):
        f = ease_out(beat_f(J_BAT, 4 + 0.3 * i, 0.3)(T))
        if f > 0:
            c.drawPath(rect(BAT[0] - 76 + 76 * i, BAT[1], 60 * f, 100 * f, 6), K.paint(GREEN, 0.75))
    return None


C(4, 4.9, charge_fn, sfx="ding")
T("“周一上会，", MID, 8870, 64, BLUE, k0=5, k1=6.5, sfx="pop")
T("我心里有底”", MID, 8980, 64, BLUE, k0=6.5, k1=8.0)

HEART = (2080, 9720, 105)
scene("我啥心情", "说清三件事 · 啥心情", (MID, 9850, 0.85))
L(heart(1340, 9450, 40), 0, 0.8, BLACK, 8, sfx="wood_high")
T("啥心情", 1560, 9445, 72, k0=1, k1=1.75, sfx="pop")
L(join(stick(1480, 10010, 0.75, tie=True), face(1480, 10010, 0.75, "smile")), 2, 2.9, BLACK, 10, sfx="wood_high")
L(heart(*HEART), 3, 3.9, ORANGE, 10, sfx="pop")


def heart_glow(c, k, T):
    """心亮起来：涂上暖色，四周冒出几道光。"""
    x, y, r = HEART
    c.drawPath(heart(x, y, r), K.paint(ORANGE, 0.35 * ease_out(k)))
    rays = join(*[P((x + 190 * math.cos(a), y + 160 * math.sin(a)), (x + (190 + 60 * k) * math.cos(a), y + (160 + 50 * k) * math.sin(a)))
                  for a in (-math.pi / 2, -math.pi / 5, -4 * math.pi / 5, 0.3, math.pi - 0.3)])
    c.drawPath(rays, wb.marker(ORANGE, 7))
    return None


C(4, 4.6, heart_glow, sfx="ding")
T("“我很踏实，", MID, 10190, 64, BLUE, k0=5, k1=6.5, sfx="pop")
T("谢谢你”", MID, 10300, 64, BLUE, k0=6.5, k1=7.5)

# ---------------------------------------------------------------- 书中观点：“真棒”像打分（场景 9）

scene("真棒像打分", "书中观点 · 第十三章", (MID, 11100, 0.85))
L(join(P((1240, 11250), (1680, 11250)), rect(1460, 11320, 400, 130, 6)), 0, 0.7, BLACK, 9, sfx="wood_low")
L(join(stick(1450, 11250, 0.7, "up", tie=True), face(1450, 11250, 0.7, "flat")), 1, 1.9, BLACK, 10, sfx="wood_high")
L(join(rect(1570, 10770, 260, 160, 12), P((1540, 10850), (1506, 11020))), 2, 2.8, BLACK, 9, sfx="wood_high")
T("真棒", 1570, 10790, 80, RED, k0=3, k1=3.8, sfx="tom")
L(join(rect(2160, 11350, 380, 56, 8), stick(2160, 11322, 0.7), face(2160, 11322, 0.7, "flat")), 4, 4.9, BLACK, 10,
  sfx="wood_high")
L(arrow((1720, 10820), (2060, 11000), -0.2, 40), 5, 5.7, RED, 8, sfx="rim")
T("夸，也可能是评判", MID, 11530, 64, k0=6, k1=8.0, sfx="pop")

# ---------------------------------------------------------------- 回家也能用（场景 10）

scene("回家也能用", "做法 · 据书中思路", (MID, 12350, 0.85))
L(parcel(1350, 12200), 0, 0.8, BLACK, 9, sfx="wood_low")
L(moon(2260, 12000, 70), 1, 1.8, ORANGE, 9, sfx="shaker")
L(join(stick(MID, 12450, 0.75, hair=True), face(MID, 12450, 0.75, "smile")), 2, 2.9, BLACK, 10, sfx="wood_high")
T("“你帮我取了快递", MID, 12600, 62, BLUE, k0=3, k1=5.0, sfx="pop")
T("我能早点睡，挺暖的”", MID, 12710, 62, BLUE, k0=5, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 别人谢你时（场景 11）

GIVE, TAKE = (1350, 13700), (2250, 13700)
J_GIFT = scene("别人谢你时", "据书中思路 · 接住感谢", (MID, 13600, 0.85))
L(join(stick(*GIVE, 0.75, "hold"), face(*GIVE, 0.75, "smile")), 0, 0.9, BLACK, 10, sfx="wood_high")
L(mirror(join(stick(*TAKE, 0.75, "hold"), face(*TAKE, 0.75, "smile")), TAKE[0]), 1, 1.9, BLACK, 10, sfx="wood_high")


def gift_fn(c, k, T):
    """一颗心从左边的人手里飞到右边的人手里（弧线），接住后停在手上。"""
    f = ease_in_out(beat_f(J_GIFT, 2, 0.9)(T))
    x0, x1, y0 = GIVE[0] + 120, TAKE[0] - 120, 13530
    x = lerp(x0, x1, f)
    y = y0 - 220 * 4 * f * (1 - f)
    c.drawPath(heart(x, y, 36), K.paint(ORANGE, 0.45))
    c.drawPath(heart(x, y, 36), wb.marker(ORANGE, 7))
    return (x, y) if f < 1 else None


C(2, 2.9, gift_fn, sfx="pop")
T("谢谢你", GIVE[0], 13180, 60, k0=3, k1=3.8, sfx="pop")
L(cross(1440, 13868, 30), 4, 4.4, RED, 9, sfx="rim")
T("没啥没啥", 1680, 13880, 60, RED, k0=4.4, k1=5.4)
L(check(1440, 14000, 32), 6, 6.4, BLUE, 9, sfx="ding")
T("能帮上就好", 1710, 14012, 60, BLUE, k0=6.4, k1=7.65)

# ---------------------------------------------------------------- 系列收尾：四格卡全亮（场景 12）

CARD = (MID, 14780, 260, 300)
EPS = ("第2讲", "第3讲", "第4–5讲", "第6讲")
scene("四格都亮了", "这一季 · 四格卡", (MID, 14850, 0.85))
L(card_frame(*CARD), 0, 0.8, BLACK, 10, sfx="wood_low")
L(card_icons(CARD[0], CARD[1] - 20, CARD[2], 1.0), 1, 1.9, BLACK, 8, sfx="pop")
for i in range(4):
    C(2 + i, 2.5 + i, fill_fn(cell_x(CARD[0], CARD[2], i), CARD[1], CARD[2] - 24, CARD[3] - 24), sfx="ding")
    T(EPS[i], cell_x(CARD[0], CARD[2], i), CARD[1] + 100, 48, BLUE, k0=2 + i, k1=2.9 + i)
T("十讲走完一圈", MID, 15130, 66, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 十讲的十个小泡（场景 13）：刺一齐收回去

PAOS = [Pao(1300 + 250 * (i % 5), 15840 + 330 * (i // 5), 98, 82, f"{i + 1:02d}") for i in range(10)]
scene("十个泡泡", "这一季 · 十讲", (MID, 16100, 0.8))
for i, p in enumerate(PAOS):
    k0 = 0.5 * i
    p.draw(J(), k0, k0 + 0.45, sfx=("wood_high" if i % 4 == 0 else "pop") if i % 2 == 0 else None)
    p.retract(J(), 5)
H(5, "ding")
T("刺都收回去了", MID, 16480, 70, BLUE, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：第 0 拍拉远看全板，第 4 拍推到评论区

COMMENT = (MID, 17300, 0.8)
scene("这一季讲完了", "评论区见", (MID, 8300, 0.1), bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(rect(MID, 17300, 1120, 460, 30), 6, 6.8, BLACK, 9, sfx="wood_low")
T("这季你最想先用哪一招？", MID, 17220, 62, RED, k0=7, k1=9.75, sfx="pop")
T("这一季讲完了", MID, 17400, 64, k0=10, k1=11.5, sfx="wood_high")
T("谢谢你一路看完", MID, 17660, 56, BLUE, k0=12, k1=13.75, sfx="ding")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "thanks", "表达感激", "夸人一句“真棒”，够了吗？", ACC, b.shots,
                 [f"{BOOK}第十三章“表达感激”（转述）",
                  "中译本：阮胤华译，华夏出版社（2009 起多版；豆瓣 subject/26331553、30761952）"],
                 "夸人一句“真棒”|【够了吗】？", SQUARE_SHOT,
                 ["书中观点均为转述：表达感激时说清三件事——对方做了什么、满足了我什么需要、我现在是什么心情；"
                  "赞扬、恭维也可能是一种评判。见第十三章“表达感激”。上屏均为转述，不是逐字引文。"
                  "出处：Marshall B. Rosenberg, Nonviolent Communication: A Language of Life；中译本《非暴力沟通》，"
                  "马歇尔·卢森堡著，阮胤华译，华夏出版社。",
                  "“别人谢你时，听听自己帮到了别人什么，别急着说没啥”据书中思路整理（书中相关说法需核实），不当原文。",
                  "两个组的实习生、甲乙两个组长、“真棒！”与三行便签、一个月后的结果（说不清 / 知道咋做）、"
                  "“周末你把三张表对齐了 / 周一上会，我心里有底 / 我很踏实，谢谢你”、给爸妈的话"
                  "（“你帮我取了快递，我能早点睡，挺暖的”）均为示意，不指向任何具体公司或个人。",
                  "三个格子（做了啥 / 帮到啥 / 啥心情）、评委打分牌、四格卡（眼睛 / 心 / 电池 / 手 = 观察 / 感受 / 需要 / 请求）"
                  "与小泡为本系列的通俗化视觉示意；场景 12 四格卡下标注的讲次对应本系列第 2、3、4–5、6 讲。"],
                 tags="#职场 #带团队")
    return b.attach(ep)
