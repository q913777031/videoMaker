"""08 爱自己（白板手绘版）：搞砸一件事，骂自己有用吗？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒。
叙事（形式 J：一个比喻贯穿——心里住着一个监工）：手一抖把周报发进客户群 → 胸口的小门里传出骂声“你怎么这么蠢” →
骂完下次还犯 → drop：小门砰地打开，跳出一个拿鞭子的监工，鞭子抽在桌上（书中观点：这样骂自己换来的多是羞愧）→
亮书（监工缩在书后偷看，四格卡点亮“需要”）→ 监工只会喊“应该” → 把骂声放进翻译机，出来一节缺电的电池 →
“我真蠢”改成“我想做事靠谱”（小泡的刺一根根缩回去）→ 体会当时想赶在下班前交掉 → 一串“不得不”锁链 →
“我选择今晚加班，因为想把项目做完”（锁链断开一节）→ 清单上划掉“周末必须秒回” → 监工放下鞭子、挂上哨子当教练 → 评论区。
系列角色：话泡泡“小泡”（场景 2 长刺、场景 8 刺缩回去、场景 13 变成圆滚滚的蓝泡）；四格卡（场景 5 点亮“需要”那一格）。
书中观点为转述（马歇尔·卢森堡《非暴力沟通》第九章“爱自己”，阮胤华译，华夏出版社）；监工、教练是本讲的示意比喻，
不是书中说法；发错群、加班、改写和清单均为示意，据书中思路整理。
"""

import math

import skia

from adler import kit as K
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, clamp01, cross, doc,
                               ease_in_out, ease_out, face, join, marker, partial, rect, stick)

from .common import BOOK, episode

ACC = "#7A4FA3"
SQUARE_SHOT = 12                # 场景 13：监工放下鞭子、挂上哨子、拿着清单当教练

b = Board(size=(3600, 11300))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前场景写字：时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def C(k0, k1, fn, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


def stroke(c, path, color, width):
    c.drawPath(path, marker(color, width))
    c.drawPath(path, K.paint(color, 0.22, width * 0.45, blur=1.2))


def moved(path, dx=0.0, dy=0.0, s=1.0, rot=0.0, px=0.0, py=0.0):
    """路径绕 (px, py) 缩放、旋转后平移。"""
    m = skia.Matrix()
    m.setTranslate(-px, -py)
    m.postScale(s, s)
    m.postRotate(rot)
    m.postTranslate(px + dx, py + dy)
    out = skia.Path(path)
    out.transform(m)
    return out


# ---------------------------------------------------------------- 本讲画法

def phone(x, y, w=420, h=680) -> skia.Path:
    return join(rect(x, y, w, h, 40), P((x - 40, y - h / 2 + 34), (x + 40, y - h / 2 + 34)),
                P((x - w / 2 + 30, y - h / 2 + 80), (x + w / 2 - 30, y - h / 2 + 80)))


def group_row(x, y) -> skia.Path:
    """聊天列表里的一行：头像 + 下划线。"""
    return join(circle(x - 130, y, 36), P((x - 70, y + 52), (x + 170, y + 52)))


def chest_door(x, y, s=1.0) -> skia.Path:
    """胸口的小门：(x, y) 为门中心。"""
    return join(rect(x, y, 70 * s, 92 * s, 6 * s), circle(x + 20 * s, y + 4 * s, 5 * s))


def waves(x, y, s=1.0) -> skia.Path:
    """门缝里传出的声音波纹（向右上）。"""
    parts = []
    for r in (40, 75, 110):
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(x - r * s, y - r * s, 2 * r * s, 2 * r * s), -80, 60)
        parts.append(p)
    return join(*parts)


def pao(x, y, w, h, mood="sad", face_dy=-50) -> skia.Path:
    """系列角色“小泡”：对话气泡 + 两点眼睛 + 小嘴（嘴在气泡上半部，下半部留给字）。"""
    p = rect(x, y, w, h, 46)
    p.moveTo(x - w * 0.25, y + h / 2)
    p.lineTo(x - w * 0.38, y + h / 2 + 60)
    p.lineTo(x - w * 0.1, y + h / 2)
    return join(p, pao_face(x, y + face_dy, mood))


def pao_face(x, y, mood="sad") -> skia.Path:
    p = join(circle(x - 38, y - 10, 6), circle(x + 38, y - 10, 6))
    if mood == "smile":
        p.addArc(skia.Rect.MakeXYWH(x - 26, y - 8, 52, 34), 20, 140)
    else:
        p.addArc(skia.Rect.MakeXYWH(x - 24, y + 10, 48, 30), 200, 140)
    return p


def spike_list(x, y, w, h, n=12, L=44):
    """气泡轮廓上等距的三角刺：[(底左, 底右, 尖, 方向)]（方向用于缩放刺长）。"""
    base = rect(x, y, w, h, 46)
    pm = skia.PathMeasure(base, False)
    total = pm.getLength()
    out = []
    for i in range(n):
        d = total * (i + 0.5) / n
        pos, tan = pm.getPosTan(d)
        px, py, tx, ty = pos.x(), pos.y(), tan.x(), tan.y()
        nx, ny = ty, -tx
        if nx * (px - x) + ny * (py - y) < 0:
            nx, ny = -nx, -ny
        out.append(((px - tx * 18, py - ty * 18), (px + tx * 18, py + ty * 18), (px, py), (nx * L, ny * L)))
    return out


def spikes(x, y, w, h, n=12, L=44) -> skia.Path:
    return join(*[P(a, (m[0] + d[0], m[1] + d[1]), c) for a, c, m, d in spike_list(x, y, w, h, n, L)])


def cap(x, y, s=1.0) -> skia.Path:
    """监工帽：配合 stick 的头（(x, y) 为脚底）。"""
    hy = y - 290 * s
    return join(P((x - 46 * s, hy - 22 * s), (x - 38 * s, hy - 70 * s), (x + 38 * s, hy - 70 * s), (x + 46 * s, hy - 22 * s)),
                P((x - 52 * s, hy - 22 * s), (x + 82 * s, hy - 22 * s)))


def angry(x, y, s=1.0) -> skia.Path:
    """皱眉撇嘴。"""
    hy = y - 290 * s
    return join(face(x, y, s, "sad"), P((x - 30 * s, hy - 18 * s), (x - 6 * s, hy - 8 * s)),
                P((x + 30 * s, hy - 18 * s), (x + 6 * s, hy - 8 * s)))


def whip(hx, hy, s=1.0, ang=-70.0) -> skia.Path:
    """鞭子：握把在 (hx, hy)，ang 为鞭身方向（度，0 = 向右，负数朝上）。"""
    p = P((0, 0), (110 * s, 0))
    lash = skia.Path()
    lash.moveTo(110 * s, 0)
    lash.cubicTo(190 * s, -50 * s, 250 * s, 40 * s, 320 * s, 10 * s)
    p.addPath(lash)
    return moved(p, hx, hy, 1.0, ang)


def overseer(x, y, s=1.0, ang=-70.0) -> skia.Path:
    """监工：戴帽子、皱眉、右手举鞭子。(x, y) 为脚底。"""
    hy = y - 290 * s
    return join(stick(x, y, s, "point"), cap(x, y, s), angry(x, y, s), whip(x + 120 * s, hy + 60 * s, s, ang))


def hand_of(x, y, s=1.0):
    hy = y - 290 * s
    return x + 120 * s, hy + 60 * s


def table(x, y, w=340) -> skia.Path:
    """桌子（无电脑）：(x, y) 为桌面中点。"""
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 24, y), (x - w / 2 + 24, y + 120)),
                P((x + w / 2 - 24, y), (x + w / 2 - 24, y + 120)))


def bursts(x, y, r0=40, r1=100, n=6, a0=-170, a1=-10) -> skia.Path:
    parts = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / (n - 1))
        parts.append(P((x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))))
    return join(*parts)


def calendar(x, y, w=640, h=560) -> skia.Path:
    top = y - h / 2
    return join(rect(x, y, w, h, 18), P((x - w / 2, top + 100), (x + w / 2, top + 100)),
                *[rect(x + dx, top, 22, 60, 10) for dx in (-w / 4, w / 4)])


def cal_grid(x, y, w=640, h=560) -> skia.Path:
    top, left = y - h / 2 + 100, x - w / 2
    parts = [P((left + w * i / 7, top), (left + w * i / 7, y + h / 2)) for i in range(1, 7)]
    parts += [P((left, top + (h - 100) * i / 4), (left + w, top + (h - 100) * i / 4)) for i in range(1, 4)]
    return join(*parts)


def cal_cell(x, y, col, row, w=640, h=560):
    top, left = y - h / 2 + 100, x - w / 2
    return left + w * (col + 0.5) / 7, top + (h - 100) * (row + 0.5) / 4


def card4(x, y, cw=130, ch=150) -> skia.Path:
    """四格卡：眼睛（观察）、心（感受）、电池（需要）、伸出的手（请求）。(x, y) 为卡片中心。"""
    parts = [rect(x, y, cw * 4, ch, 16)]
    parts += [P((x - cw * 2 + cw * i, y - ch / 2), (x - cw * 2 + cw * i, y + ch / 2)) for i in (1, 2, 3)]
    cx = [x - cw * 1.5 + cw * i for i in range(4)]
    eye = skia.Path()
    eye.moveTo(cx[0] - 42, y)
    eye.quadTo(cx[0], y - 44, cx[0] + 42, y)
    eye.quadTo(cx[0], y + 44, cx[0] - 42, y)
    parts += [eye, circle(cx[0], y, 13)]
    hp = skia.Path()
    r = 30
    hp.moveTo(cx[1], y + r * 0.9)
    hp.cubicTo(cx[1] - r * 1.7, y - r * 0.2, cx[1] - r * 0.65, y - r * 1.35, cx[1], y - r * 0.45)
    hp.cubicTo(cx[1] + r * 0.65, y - r * 1.35, cx[1] + r * 1.7, y - r * 0.2, cx[1], y + r * 0.9)
    parts.append(hp)
    parts += [battery(cx[2], y, 0.55)]
    parts += [rect(cx[3] - 6, y + 12, 52, 44, 12)] + [P((cx[3] - 26 + 13 * i, y - 10), (cx[3] - 26 + 13 * i, y - 42))
                                                     for i in range(4)] + [P((cx[3] + 20, y + 6), (cx[3] + 44, y - 18))]
    return join(*parts)


def battery(x, y, s=1.0) -> skia.Path:
    return join(rect(x, y, 150 * s, 80 * s, 12 * s), rect(x + 85 * s, y, 16 * s, 34 * s, 4 * s))


def machine(x, y) -> skia.Path:
    """翻译机：机身 + 左上漏斗 + 右侧出口 + 两个旋钮。(x, y) 为机身中心。"""
    return join(rect(x, y, 380, 260, 26),
                P((x - 170, y - 130), (x - 230, y - 250), (x - 30, y - 250), (x - 90, y - 130)),
                P((x + 190, y + 40), (x + 260, y + 40), (x + 260, y + 120), (x + 190, y + 120)),
                circle(x + 110, y - 60, 26), circle(x + 110, y + 20, 26))


def clock_face(x, y, r=110) -> skia.Path:
    """17:55 的钟。"""
    marks = [P((x + r * 0.82 * math.cos(math.radians(a)), y + r * 0.82 * math.sin(math.radians(a))),
               (x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a)))) for a in range(0, 360, 90)]
    ha = math.radians(-90 + 360 * (5 + 55 / 60) / 12)
    ma = math.radians(-90 + 360 * 55 / 60)
    return join(circle(x, y, r), *marks, P((x, y), (x + r * 0.5 * math.cos(ha), y + r * 0.5 * math.sin(ha))),
                P((x, y), (x + r * 0.78 * math.cos(ma), y + r * 0.78 * math.sin(ma))))


def laptop(x, y) -> skia.Path:
    """桌上的笔记本：(x, y) 为键盘底边中点。"""
    return join(P((x - 110, y), (x + 110, y)), P((x - 90, y), (x - 80, y - 150), (x + 80, y - 150), (x + 90, y)))


def hug(x, y, s=1.0) -> skia.Path:
    """环抱小人的两只手臂（左右各一道弧，端头三根手指）。(x, y) 为小人脚底。"""
    hy = y - 290 * s
    parts = []
    for sx in (-1, 1):
        a = skia.Path()
        a.moveTo(x + sx * 200 * s, hy - 40 * s)
        a.cubicTo(x + sx * 260 * s, hy + 120 * s, x + sx * 150 * s, hy + 230 * s, x + sx * 20 * s, hy + 200 * s)
        parts.append(a)
        for d in (-18, 0, 18):
            parts.append(P((x + sx * 20 * s, hy + (200 + d) * s), (x - sx * 18 * s, hy + (196 + d * 1.3) * s)))
    return join(*parts)


def heart(x, y, r=40) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def sweat(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y - 30 * s)
    p.quadTo(x + 20 * s, y, x, y + 12 * s)
    p.quadTo(x - 20 * s, y, x, y - 30 * s)
    return p


def links(x0, y0, x1, y1, n, rw=70, rh=40) -> skia.Path:
    """一串锁链：n 个椭圆环，从 (x0, y0) 排到 (x1, y1)，横竖交替。"""
    parts = []
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    for i in range(n):
        f = (i + 0.5) / n
        cx, cy = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        o = skia.Path()
        hh = rh if i % 2 == 0 else rh * 0.45
        o.addOval(skia.Rect.MakeXYWH(cx - rw / 2, cy - hh / 2, rw, hh))
        parts.append(moved(o, 0, 0, 1.0, ang, cx, cy))
    return join(*parts)


def ball(x, y, r=70) -> skia.Path:
    return join(circle(x, y, r), P((x - r * 0.4, y - r * 0.2), (x - r * 0.15, y - r * 0.5)))


def strike(x, y, w) -> skia.Path:
    return P((x - w / 2, y + 6), (x + w / 2, y - 6))


def clipboard(x, y, w=700, h=760) -> skia.Path:
    return join(rect(x, y, w, h, 24), rect(x, y - h / 2, 200, 50, 12))


def box(x, y, r=26) -> skia.Path:
    return rect(x, y, 2 * r, 2 * r, 6)


def whistle(x, y, s=1.0) -> skia.Path:
    """挂在脖子上的哨子：(x, y) 为小人脚底。"""
    hy = y - 290 * s
    wx, wy = x + 34 * s, hy + 150 * s
    return join(P((x - 34 * s, hy + 40 * s), (x, hy + 120 * s), (x + 34 * s, hy + 40 * s)),
                P((x, hy + 120 * s), (wx - 20 * s, wy - 18 * s)), rect(wx, wy, 56 * s, 34 * s, 12 * s),
                circle(wx + 8 * s, wy, 7 * s))


def pop_text(s, x, y, size, color=RED, k_in=0.0):
    """弹出的字：从 0 放大到 1.15 再落回 1。"""
    def fn(c, k, t):
        f = ease_out(clamp01(k))
        sc = f * (1 + 0.15 * math.sin(math.pi * f))
        if sc > 0.02:
            K.text(c, s, x, y, size * sc, "hand", color)
        return None

    return fn


# ---------------------------------------------------------------- 开局：周报发错群（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("周报发错群了", "开局 · 手一抖", (950, 900, 0.85), bars=2)
L(phone(1050, 880), 0, 0.9, sfx="wood_high")
L(group_row(1060, 690), 1, 1.4, BLACK, 8, sfx="pop")
T("项目组", 1080, 690, 56, k0=1.3, k1=2.0)
L(group_row(1060, 930), 2, 2.4, RED, 8, sfx="pop")
T("客户群", 1080, 930, 56, RED, k0=2.3, k1=3.0)
L(doc(520, 760, 170, 210), 3, 3.8, BLACK, 9, sfx="wood_low")
T("周报", 520, 560, 56, k0=3.8, k1=4.3)
L(arrow((610, 820), (880, 940), -0.2, 40), 4, 4.8, RED, 9, sfx="rim")
T("发错了！", 1050, 1340, 80, RED, k0=5, k1=6, sfx="kick")

P2 = (2350, 1400, 1.4)          # 主角：脚底 + 比例
BB = (2850, 720, 470, 270)      # 骂声小泡
scene("你怎么这么蠢", "开局 · 心里开骂", (2650, 900, 0.85))
L(stick(*P2, "down"), 0, 0.9, sfx="wood_high")
L(face(*P2, "flat"), 0.9, 1.0)
L(chest_door(P2[0], 1150, 1.3), 1, 1.8, BLACK, 8, sfx="wood_low")
L(waves(P2[0] + 50, 1120, 1.2), 2, 2.8, BLACK, 7, sfx="shaker")
L(pao(*BB, "sad"), 3, 3.9, RED, 9, sfx="pop")
T("你怎么这么蠢", BB[0], BB[1] + 60, 58, RED, k0=4, k1=5.5, sfx="rim")


def grow_spikes(x, y, w, h, n=12, Lmax=44):
    def fn(c, k, t):
        f = ease_out(clamp01(k))
        for a, cc, m, d in spike_list(x, y, w, h, n, Lmax):
            stroke(c, P(a, (m[0] + d[0] * f, m[1] + d[1] * f), cc), RED, 8)
        return None

    return fn


C(6, 6.6, grow_spikes(*BB), sfx="tom")
L(sweat(P2[0] + 85, P2[1] - 400, 1.2), 7, 7.6, BLUE, 7, sfx="pop")

CAL = (2650, 2330)
scene("骂完，下次还犯", "开局 · 老毛病", (2650, 2250, 0.85))
L(calendar(*CAL), 0, 0.9, sfx="wood_high")
L(cal_grid(*CAL), 1, 1.9, BLACK, 6, sfx="wood_low")
X = [cal_cell(*CAL, 2, r) for r in range(3)]
L(cross(*X[0], 34), 2, 2.6, RED, 10, sfx="rim")
L(arrow((X[0][0] + 50, X[0][1]), (X[1][0] + 50, X[1][1]), -0.5, 26), 3, 3.6, RED, 7, sfx="wood_high")
L(cross(*X[1], 34), 4, 4.6, RED, 10, sfx="rim")
L(arrow((X[1][0] + 50, X[1][1]), (X[2][0] + 50, X[2][1]), -0.5, 26), 5, 5.6, RED, 7, sfx="wood_high")
L(cross(*X[2], 34), 6, 6.6, RED, 10, sfx="rim")
T("又发错了", 2650, 1860, 84, RED, k0=7, k1=8, sfx="tom")

# ---------------------------------------------------------------- drop：心里住着个监工（场景 4）

DOOR = (560, 2350)
OV = (930, 2700, 1.0)           # 监工落地：脚底 + 比例
DESK = (1310, 2560)
scene("心里住着个监工", "书中观点 · 第九章", (950, 2250, 0.8), shake=[0, 4], flashes=[0])
L(join(rect(*DOOR, 260, 420, 10), P((430, 2140), (320, 2200), (320, 2620), (430, 2560)), circle(345, 2420, 9)),
  0, 0.6, BLACK, 10, sfx="kick")
L(bursts(DOOR[0], DOOR[1] - 40, 240, 300, 5, -150, -30), 0.6, 1.0, BLACK, 7)
J4 = J()


def overseer_jump(c, k, T):
    """监工从门里跳出来（第 1–1.8 拍），举着鞭子；第 3.7–4 拍鞭子抽到桌面。"""
    t1, t18 = b.t_of(J4, 1), b.t_of(J4, 1.8)
    f = ease_in_out(clamp01((T - t1) / max(1e-3, t18 - t1)))
    x0, y0, s0 = DOOR[0], DOOR[1] + 90, 0.35
    x = x0 + (OV[0] - x0) * f
    y = y0 + (OV[1] - y0) * f - 260 * 4 * f * (1 - f)
    s = s0 + (OV[2] - s0) * f
    ts, te = b.t_of(J4, 3.7), b.t_of(J4, 4)
    g = clamp01((T - ts) / max(1e-3, te - ts))
    ang = -75 + 90 * g * g
    hy = y - 290 * s
    stroke(c, join(stick(x, y, s, "point"), cap(x, y, s), angry(x, y, s)), BLACK, 10 * max(0.6, s))
    stroke(c, whip(x + 120 * s, hy + 60 * s, s, ang), RED, 10 * max(0.6, s))
    return None


C(1, 1.8, overseer_jump, sfx="wood_high")
L(table(*DESK), 2, 2.8, BLACK, 10, sfx="wood_low")
L(bursts(1340, 2555, 30, 95, 5), 4, 4.5, RED, 8, sfx="kick")
T("心里住着个监工", 950, 1790, 84, k0=5, k1=6.75, sfx="ding")
T("换来羞愧", 950, 1950, 64, RED, k0=7, k1=8, sfx="rim")

# ---------------------------------------------------------------- 书中观点（场景 5–7）

BK = (780, 3640)
scene("有本书讲过", "书中观点 · 第九章 爱自己", (950, 3600, 0.85))
L(book(*BK, 420, 280), 0, 0.9, sfx="wood_low")
T("非暴力沟通", 780, 3330, 76, GREEN, k0=1, k1=2.25, sfx="pop")
T("马歇尔·卢森堡", 780, 3880, 52, k0=3, k1=4.5, sfx="pop")
PK = (1060, 3420)               # 偷看的监工头
L(join(circle(*PK, 46), P((PK[0] - 48, PK[1] - 20), (PK[0] - 40, PK[1] - 70), (PK[0] + 40, PK[1] - 70),
                          (PK[0] + 48, PK[1] - 20)), P((PK[0] - 82, PK[1] - 20), (PK[0] + 54, PK[1] - 20)),
       circle(PK[0] - 16, PK[1] + 2, 5), circle(PK[0] + 14, PK[1] + 2, 5),
       P((PK[0] - 70, PK[1] + 30), (PK[0] - 40, PK[1] + 30)), P((PK[0] - 70, PK[1] + 44), (PK[0] - 42, PK[1] + 44))),
  5, 5.8, BLACK, 8, sfx="wood_high")
CARD = (1270, 3890)


def cell_fill(i, color=GREEN, alpha=0.28, cw=100, ch=116):
    def fn(c, k, t):
        x = CARD[0] - cw * 1.5 + cw * i
        K.rr(c, x, CARD[1], (cw - 10) * clamp01(k), ch - 10, 10, color, alpha)
        return None

    return fn


L(moved(card4(0, 0, 130, 150), CARD[0], CARD[1], 100 / 130), 6, 6.9, BLACK, 7, sfx="wood_high")
C(7, 7.6, cell_fill(2), sfx="ding")
L(check(CARD[0] + 50, CARD[1] - 90, 26), 7.6, 8.0, GREEN, 8)

OV6 = (2330, 3980, 0.95)
scene("它只会喊应该", "书中观点 · 应该", (2650, 3600, 0.85))
L(overseer(*OV6, -70), 0, 1.0, BLACK, 9, sfx="wood_high")
SH = [("应该细心", 2900, 3200), ("应该检查", 2950, 3440), ("应该完美", 2900, 3680)]
for n, (s, x, y) in enumerate(SH):
    C(2 + n, 2.5 + n, pop_text(s, x, y, 80), sfx="pop")
L(join(*[rect(x - 80, y, 180, 100, 46) for _, x, y in SH]), 5, 5.8, BLUE, 7, sfx="rim")
T("留意这两个字", 2650, 4080, 66, BLUE, k0=6, k1=7.5, sfx="ding")

MC = (2650, 5000)
scene("把骂声翻译了", "书中观点 · 翻译自责", (2650, 4950, 0.85))
L(machine(*MC), 0, 0.9, sfx="wood_high")
T("翻译机", MC[0] - 40, MC[1] + 70, 60, k0=1, k1=1.8, sfx="pop")
J7 = J()


def whip_in(c, k, T):
    """鞭子出现在漏斗左上方（第 2 拍），第 3–3.8 拍滑进漏斗消失。"""
    t3, t38 = b.t_of(J7, 3), b.t_of(J7, 3.8)
    f = ease_in_out(clamp01((T - t3) / max(1e-3, t38 - t3)))
    if f >= 1:
        return None
    x0, y0 = 2120, 4560
    x1, y1 = MC[0] - 130, MC[1] - 170
    x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, 3600, MC[1] - 200 + 40 * (1 - f)))
    stroke(c, whip(x - 40, y - 30, 1.0 - 0.4 * f, 25 + 40 * f), RED, 10)
    c.restore()
    return None


C(2, 2.4, whip_in, sfx="wood_low")
H(3, "shaker")


def rumble(c, k, T):
    """机身两侧抖动线：第 4–5 拍出现，之后保留。"""
    a = 10 * math.sin(T * 60) * (1 - clamp01(k))
    for sx in (-1, 1):
        for dy in (-60, 0, 60):
            x = MC[0] + sx * (215 + a)
            stroke(c, P((x, MC[1] + dy - 20), (x + sx * 30, MC[1] + dy + 20)), BLACK, 6)
    return None


C(4, 5, rumble, sfx="shaker")
BAT = (3080, 5260)
J7b = J()


def battery_out(c, k, T):
    """电池从出口滑出（第 5–5.8 拍）；电量只剩一格，红格闪烁。"""
    f = ease_out(clamp01(k))
    x = MC[0] + 225 + (BAT[0] - MC[0] - 225) * f
    y = MC[1] + 80 + (BAT[1] - MC[1] - 80) * f
    stroke(c, battery(x, y, 1.1), BLACK, 9)
    blink = 0.45 + 0.45 * (math.sin(T * 9) > 0)
    K.rr(c, x - 55, y, 34, 64, 6, RED, blink * f)
    return None


C(5, 5.8, battery_out, sfx="pop")
T("没被满足的需要", 2650, 5460, 70, BLUE, k0=6, k1=7.75, sfx="ding")

# ---------------------------------------------------------------- 改写（场景 8–9）

LB, RB = (640, 4820, 420, 280), (1260, 4820, 420, 280)
scene("我想做事靠谱", "书中观点 · 听出需要", (950, 4950, 0.85))
L(join(P((950, 4520), (950, 5420)), cross(640, 4500, 34), check(1260, 4500, 40)), 0, 0.9, BLACK, 8, sfx="wood_high")
L(join(pao(*LB, "sad"), spikes(*LB)), 1, 1.9, RED, 8, sfx="pop")
T("我真蠢", LB[0], LB[1] + 60, 62, RED, k0=2, k1=2.8, sfx="rim")
L(arrow((870, 4990), (1040, 4990), 0.1, 30), 3, 3.6, BLACK, 8, sfx="wood_low")
J8 = J()


def pao_heal(c, k, T):
    """右边的小泡：第 4 拍画出（带刺、红色、撇嘴），第 5/6/7 拍刺分三批缩回去，第 7 拍变蓝、嘴角上扬。"""
    x, y, w, h = RB
    t4, t49 = b.t_of(J8, 4), b.t_of(J8, 4.9)
    f = clamp01((T - t4) / max(1e-3, t49 - t4))
    tb = b.t_of(J8, 7)
    blue = T >= tb
    col = BLUE if blue else RED
    body = rect(x, y, w, h, 46)
    body.moveTo(x - w * 0.25, y + h / 2)
    body.lineTo(x - w * 0.38, y + h / 2 + 60)
    body.lineTo(x - w * 0.1, y + h / 2)
    part, tip = partial(body, f)
    stroke(c, part, col, 8)
    if f >= 1:
        stroke(c, pao_face(x, y - 50, "smile" if blue else "sad"), col, 8)
        for i, (a, cc, m, d) in enumerate(spike_list(x, y, w, h)):
            kk = 5 + i % 3
            r0, r1 = b.t_of(J8, kk), b.t_of(J8, kk + 0.6)
            g = 1 - ease_in_out(clamp01((T - r0) / max(1e-3, r1 - r0)))
            if g > 0.02:
                stroke(c, P(a, (m[0] + d[0] * g, m[1] + d[1] * g), cc), RED, 8)
    return tip


C(4, 4.9, pao_heal, sfx="pop")
H(5, "pop")
H(6, "pop")
H(7, "ding")
T("我想做事靠谱", RB[0], RB[1] + 60, 54, BLUE, k0=5, k1=6.5)
T("想让客户放心", RB[0], 5160, 54, BLUE, k0=6.5, k1=8)

P9 = (1000, 6640, 0.75)
scene("当时你在赶时间", "书中观点 · 体会当时", (950, 6300, 0.85))
L(clock_face(560, 5930, 105), 0, 0.9, sfx="wood_high")
T("17:55", 560, 6110, 64, RED, k0=1, k1=2, sfx="pop")
L(join(table(1210, 6460, 360), laptop(1210, 6450)), 2, 2.9, BLACK, 9, sfx="wood_low")
L(join(stick(*P9, "hold"), face(*P9, "flat"), sweat(P9[0] - 70, P9[1] - 300, 0.9)), 3, 3.9, BLACK, 9, sfx="pop")
T("想赶在下班前交掉", 1060, 5900, 62, k0=4, k1=6, sfx="pop")
L(hug(*P9), 6, 6.9, BLUE, 10, sfx="ding")
L(heart(P9[0], P9[1] - 390, 30), 7, 7.7, RED, 8, sfx="pop")

# ---------------------------------------------------------------- “不得不” → “我选择”（场景 10–12）

P10 = (2230, 6760, 0.8)
scene("不得不，太多了", "书中观点 · 不得不", (2650, 6300, 0.85))
L(join(stick(*P10, "shrug"), face(*P10, "sad")), 0, 0.9, sfx="wood_high")
HX, HY = P10[0] + 90 * P10[2], P10[1] - 290 * P10[2] + 30 * P10[2]
L(links(HX, HY, 2990, 6660, 8), 1, 1.9, BLACK, 7, sfx="shaker")
TAGS = [("不得不加班", 2830, 5900), ("不得不秒回", 2830, 6090), ("不得不合群", 2830, 6280)]
for n, (s, x, y) in enumerate(TAGS):
    T(s, x, y, 66, RED, k0=2 + n * 1.5 if n < 2 else 5, sfx="pop")
L(ball(3070, 6690, 70), 7, 7.8, BLACK, 10, sfx="tom")

CH = (2650, 7200)
scene("我选择加班", "书中观点 · 我选择", (2650, 7650, 0.85))
L(join(links(2250, CH[1], 2560, CH[1], 3), links(2740, CH[1], 3050, CH[1], 3)), 0, 0.9, BLACK, 7, sfx="wood_high")
J11 = J()


def mid_link(c, k, T):
    """中间那一环：第 0–0.9 拍画出，第 3 拍断开、两半往外弹。"""
    o = skia.Path()
    o.addOval(skia.Rect.MakeXYWH(CH[0] - 50, CH[1] - 20, 100, 40))
    t3, t36 = b.t_of(J11, 3), b.t_of(J11, 3.6)
    g = ease_out(clamp01((T - t3) / max(1e-3, t36 - t3)))
    if g <= 0:
        part, tip = partial(o, k)
        stroke(c, part, BLACK, 7)
        return tip
    for sx in (-1, 1):
        half = skia.Path()
        half.addArc(skia.Rect.MakeXYWH(CH[0] - 50, CH[1] - 20, 100, 40), 90 if sx < 0 else -90, 150)
        stroke(c, moved(half, sx * 40 * g, 0, 1.0, sx * 18 * g, CH[0], CH[1]), BLACK, 7)
    return None


C(0, 0.9, mid_link)
T("我不得不加班", 2650, 7420, 70, RED, k0=1, k1=2.5, sfx="pop")
L(join(bursts(CH[0], CH[1], 40, 85, 5, -160, -20), strike(2650, 7420, 470)), 3, 3.8, RED, 8, sfx="rim")
T("我选择今晚加班", 2650, 7640, 72, BLUE, k0=4, k1=5.75, sfx="pop")
T("因为想把项目做完", 2650, 7840, 66, BLUE, k0=6, k1=8, sfx="ding")

CB = (950, 7660)
scene("不想要的划掉", "据书中思路 · 划掉一条", (950, 7650, 0.85))
L(clipboard(*CB, 700, 760), 0, 0.9, sfx="wood_high")
L(box(720, 7470), 1, 1.3, BLACK, 7, sfx="pop")
T("今晚加班", 960, 7470, 64, k0=1.3, k1=2.3)
L(box(720, 7680), 3, 3.3, BLACK, 7, sfx="pop")
T("周末必须秒回", 1010, 7680, 64, k0=3.3, k1=4.8)
L(strike(1010, 7680, 420), 5, 5.6, RED, 10, sfx="rim")
T("怕别人说而已", 1010, 7820, 56, RED, k0=6, k1=7.5, sfx="pop")
L(check(720, 7465, 34), 7.6, 8.0, GREEN, 10)
H(7, "ding")

# ---------------------------------------------------------------- 换岗（场景 13）

P13 = (720, 9420, 0.95)
ME = (1270, 9420, 0.75)
scene("监工换了岗", "监工换岗 · 当教练", (950, 9000, 0.85))
L(join(stick(*P13, "hold"), face(*P13, "smile")), 0, 0.9, sfx="wood_high")
L(whistle(*P13), 1, 1.8, BLACK, 7, sfx="pop")
CX, CY = P13[0] + 110 * P13[2] + 60, P13[1] - 290 * P13[2] + 110 * P13[2]
L(join(rect(CX, CY, 150, 190, 10), rect(CX, CY - 95, 60, 24, 6), check(CX - 30, CY - 40, 18), check(CX - 30, CY + 20, 18),
       P((CX, CY - 40), (CX + 50, CY - 40)), P((CX, CY + 20), (CX + 50, CY + 20))), 2, 2.9, BLACK, 7, sfx="wood_low")
L(join(whip(400, 9400, 0.8, 0), moved(cap(0, 290), 470, 9320, 1.0, -15)), 3, 3.6, RED, 8, sfx="rim")
L(cross(520, 9310, 40), 3.6, 4.0, BLACK, 8)
L(join(stick(*ME, "down"), face(*ME, "smile")), 4, 4.8, BLUE, 9, sfx="pop")
PB = (1000, 8780, 560, 210)
L(pao(*PB, "smile", -45), 5, 5.8, BLUE, 8, sfx="pop")
T("发前先看群名", PB[0], PB[1] + 45, 56, BLUE, k0=6, k1=7.5, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5650, 0.16)
END = (1800, 10450, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, END, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
L(rect(1800, 10450, 1180, 420, 30), 4, 4.9, BLACK, 8, sfx="wood_high")
T("你心里的监工最爱骂哪句？", 1800, 10370, 66, RED, k0=6, k1=9, sfx="pop")
T("下一讲：气到想摔门，先做哪一步？", 1800, 10530, 48, k0=9, k1=13, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "self", "爱自己", "搞砸一件事，骂自己有用吗？", ACC, b.shots,
                 [f"{BOOK}第九章“爱自己”（转述）", "中译本：阮胤华译，华夏出版社"],
                 "搞砸一件事|骂自己【有用吗】", SQUARE_SHOT,
                 ["书中观点均为转述（第九章“爱自己”）：用“应该”“我真蠢”这类话责备自己，换来的多是羞愧和内疚，难带来改变；"
                  "留意“应该”这种说法；把自责翻译成没被满足的需要；也体会自己当时那样做是想满足什么需要；把“不得不”改成"
                  "“我选择……因为我想要……”。上屏均为转述，不是逐字引文。",
                  "“心里住着一个监工”、监工换岗当教练、翻译机、锁链为本讲的示意比喻，不是书中的说法。",
                  "周报发错群、17:55 赶着下班前交、加班、周末秒回消息均为现实场景示意，不指向任何具体公司或个人；"
                  "“我想做事靠谱，想让客户放心”“我选择今晚加班，因为想把项目做完”为示意改写，据书中思路整理。",
                  "“有的‘不得不’背后只是怕别人说，可以考虑不做”（划掉“周末必须秒回”）据书中思路整理。"],
                 tags="#自我成长 #情绪")
    return b.attach(ep)
