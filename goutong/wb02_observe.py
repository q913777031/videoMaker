"""02 观察和评论（白板手绘版）：“你总迟到”，为啥一说就炸？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（C 书里的小测验，先猜再揭晓）：开局组长对同事说「你总迟到」，小泡长出红刺 → 同事当场炸了：「我哪天总迟到了？」
翻日历数日子 → 两人中间压下一个大问号：明明迟到过，为啥吵起来 →
drop：放大镜扣在「总」字上，红圈砸出——评论混进了观察，对方听着像批评，就会反驳 →
亮书，四格卡点亮「眼睛」一格 → 书中观点：观察只说摄像机能拍到的，评论加了自己的判断（左摄像机「九点二十到」，右法官锤「懒」）→
小测验四道题，每题先倒数两拍给观众猜，再打勾打叉揭晓（他很懒 / 他这周有三天没交日报 / 她老是不回消息 / 领导偏心 vs 三个项目都给了同一个人）→
书中观点：总、老、从来这类词容易把观察变成评论，三个词关进笼子 → 做法：说出哪天、几次、什么事（日历圈两天，九点二十）→
组长再说一遍，小泡的刺一根根缩回去，同事点头 → 拉远看全板，推到评论区。
系列视觉角色：话泡泡「小泡」（带红刺 → 刺缩回去变蓝变圆）、四格卡（本讲点亮眼睛 = 观察）。
书中观点为转述：马歇尔·卢森堡《非暴力沟通》第三章“区分观察和评论”（评论混进观察，对方容易听成批评而反驳；
“总是”“从不”“每次”这类词常把观察变成评论；章末有“观察还是评论”的练习）。中译本阮胤华译，华夏出版社。
组长与同事、四道题和改写句都是示意，不照抄书里的练习题；“像摄像机一样只拍能拍到的”是对书中观点的通俗比喻。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross, face,
                               join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#2C8C99"                 # 本讲主色：摄像机镜头的青蓝（观察）
SQUARE_SHOT = 5                 # 场景 6：同事 + 左摄像机「九点二十到」/ 右法官锤「懒」

b = Board(size=(3600, 13400))


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


def char_x(s, x, size, i):
    """居中书写的一行字里第 i 个字的中心横坐标。"""
    w = K.text_w(s, size, "hand")
    return x - w / 2 + K.text_w(s[:i], size, "hand") + K.text_w(s[i], size, "hand") / 2


# ---------------------------------------------------------------- 系列角色：小泡（会长刺的话泡泡）

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def _on_oval(x, y, w, h, a, push=0.0):
    """椭圆上参数角 a 的点，沿外法线推出 push。"""
    px, py = x + w / 2 * math.cos(a), y + h / 2 * math.sin(a)
    nx, ny = math.cos(a) / (w / 2), math.sin(a) / (h / 2)
    d = math.hypot(nx, ny)
    return px + push * nx / d, py + push * ny / d


def pao(x, y, w, h, tail) -> skia.Path:
    """小泡：椭圆气泡 + 朝 tail 点伸出的尖尾巴。"""
    tx, ty = tail
    a = math.atan2((ty - y) / (h / 2), (tx - x) / (w / 2))
    p = oval(x, y, w, h)
    p.addPath(P(_on_oval(x, y, w, h, a - 0.16), (tx, ty), _on_oval(x, y, w, h, a + 0.16)))
    return p


def spikes(x, y, w, h, n=14, length=56, f=1.0, skip=None) -> skia.Path:
    """沿小泡轮廓等距长出的三角刺；f 为刺长比例（缩回去时从 1 到 0）；skip 为尾巴方向的参数角，那里不长刺。"""
    p = skia.Path()
    da = math.pi / n * 0.55
    for i in range(n):
        a = 2 * math.pi * i / n + 0.11
        if skip is not None and abs(math.remainder(a - skip, 2 * math.pi)) < 0.35:
            continue
        p.moveTo(*_on_oval(x, y, w, h, a - da))
        p.lineTo(*_on_oval(x, y, w, h, a, length * f))
        p.lineTo(*_on_oval(x, y, w, h, a + da))
    return p


def tail_angle(x, y, w, h, tail):
    return math.atan2((tail[1] - y) / (h / 2), (tail[0] - x) / (w / 2))


def pao_face(x, y, w, h, mood="sad") -> skia.Path:
    """小泡的两点眼睛 + 小嘴，画在气泡上沿（下面留给字）。"""
    ey, my = y - h * 0.30, y - h * 0.17
    p = join(circle(x - 46, ey, 6), circle(x + 46, ey, 6))
    m = skia.Path()
    if mood == "smile":
        m.addArc(skia.Rect.MakeXYWH(x - 30, my - 22, 60, 34), 20, 140)
    else:
        m.addArc(skia.Rect.MakeXYWH(x - 28, my - 6, 56, 30), 200, 140)
    p.addPath(m)
    return p


def pao_turn_fn(j, x, y, w, h, tail, k_off, k_end):
    """小泡的刺：本项进度内长出来；第 k_off–k_end 拍一根根缩回去，轮廓变蓝，嘴角上扬。"""
    sk = tail_angle(x, y, w, h, tail)

    def fn(c, k, t):
        t0, t1 = b.t_of(j, k_off), b.t_of(j, k_end)
        r = ease_in_out(clamp01((t - t0) / max(1e-3, t1 - t0)))
        n = 14
        grow = ease_out(clamp01(k))
        for i in range(n):                       # 一根根缩：每根刺的缩回时刻错开一点
            ri = clamp01(r * 1.6 - i / n * 0.6)
            f = grow * (1 - ri)
            if f > 0.02:
                a = 2 * math.pi * i / n + 0.11
                if abs(math.remainder(a - sk, 2 * math.pi)) < 0.35:
                    continue
                da = math.pi / n * 0.55
                c.drawPath(P(_on_oval(x, y, w, h, a - da), _on_oval(x, y, w, h, a, 56 * f), _on_oval(x, y, w, h, a + da)),
                           K.paint(RED, 1, 9))
        if r > 0:
            c.drawPath(pao(x, y, w, h, tail), K.paint(BLUE, r, 11))
        c.drawPath(pao_face(x, y, w, h, "smile" if r > 0.5 else "sad"), K.paint(BLACK if r <= 0.5 else BLUE, 1, 8))
        return None

    return fn


# ---------------------------------------------------------------- 系列角色：四格卡（眼睛 / 心 / 电池 / 手）

def eye_icon(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 70 * s, y)
    p.quadTo(x, y - 62 * s, x + 70 * s, y)
    p.quadTo(x, y + 62 * s, x - 70 * s, y)
    return join(p, circle(x, y, 20 * s))


def heart(x, y, r=40) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def battery(x, y, s=1.0) -> skia.Path:
    return join(rect(x - 6 * s, y, 120 * s, 64 * s, 10 * s), rect(x + 62 * s, y, 12 * s, 28 * s, 3 * s),
                P((x - 46 * s, y - 16 * s), (x - 46 * s, y + 16 * s)))


def palm(x, y, s=1.0) -> skia.Path:
    """伸出的手：掌心 + 四指 + 拇指。"""
    parts = [rect(x, y + 14 * s, 70 * s, 56 * s, 18 * s)]
    for i in range(4):
        fx = x - 26 * s + i * 17 * s
        parts.append(P((fx, y - 14 * s), (fx, y - 52 * s + abs(i - 1.5) * 6 * s)))
    parts.append(P((x - 35 * s, y + 10 * s), (x - 62 * s, y - 14 * s)))
    return join(*parts)


CARD_W, CARD_H = 880, 240


def fourcard(x, y):
    """返回（外框 + 隔线，四个图标，各格中心横坐标）。"""
    cw = CARD_W / 4
    xs = [x - CARD_W / 2 + cw * (i + 0.5) for i in range(4)]
    frame = join(rect(x, y, CARD_W, CARD_H, 22), *[P((x - CARD_W / 2 + cw * i, y - CARD_H / 2), (x - CARD_W / 2 + cw * i, y + CARD_H / 2))
                                                   for i in (1, 2, 3)])
    iy = y - 30
    icons = join(eye_icon(xs[0], iy, 0.9), heart(xs[1], iy + 4, 36), battery(xs[2], iy), palm(xs[3], iy + 6))
    return frame, icons, xs


def fill_fn(x, y, w, h, color, alpha=0.25):
    """从左往右涂一格颜色。"""

    def fn(c, k, t):
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 8, y - h / 2 + 8, (w - 16) * ease_out(k), h - 16), K.paint(color, alpha))
        return (x - w / 2 + 8 + (w - 16) * k, y + 30 * math.sin(k * 18))

    return fn


# ---------------------------------------------------------------- 本讲画法

def qmark(x, y, s=1.0) -> skia.Path:
    """大问号：(x, y) 为问号竖弯的中心。"""
    p = skia.Path()
    p.moveTo(x - 70 * s, y - 70 * s)
    p.cubicTo(x - 70 * s, y - 160 * s, x + 80 * s, y - 165 * s, x + 75 * s, y - 75 * s)
    p.cubicTo(x + 72 * s, y - 15 * s, x, y - 5 * s, x, y + 60 * s)
    return join(p, circle(x, y + 125 * s, 14 * s))


def anger(x, y, s=1.0) -> skia.Path:
    """头顶的生气符号（四个弯角）。"""
    parts = []
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        p = skia.Path()
        p.moveTo(x + sx * 10 * s, y + sy * 34 * s)
        p.quadTo(x + sx * 12 * s, y + sy * 12 * s, x + sx * 34 * s, y + sy * 10 * s)
        parts.append(p)
    return join(*parts)


def calendar(x, y, w=240, h=220) -> skia.Path:
    """台历：外框 + 顶部装订环 + 表头线 + 格子。"""
    parts = [rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 55), (x + w / 2, y - h / 2 + 55))]
    for dx in (-w / 4, w / 4):
        parts.append(P((x + dx, y - h / 2 - 20), (x + dx, y - h / 2 + 18)))
    for i in (1, 2):
        parts.append(P((x - w / 2 + w * i / 3, y - h / 2 + 55), (x - w / 2 + w * i / 3, y + h / 2)))
    parts.append(P((x - w / 2, y + 30), (x + w / 2, y + 30)))
    return join(*parts)


def flip_fn(x, y, w=240, h=220, pages=3):
    """台历哗哗往上翻：几页纸从底边掀起，翻过装订线。"""
    top = y - h / 2

    def fn(c, k, t):
        for i in range(pages):
            e = clamp01(k * (pages + 1) / 2 - i * 0.5)
            if e <= 0 or e >= 1:
                continue
            yb = lerp(y + h / 2, top - h * 0.55, ease_in_out(e))
            sk = 30 * math.sin(e * math.pi)
            pg = P((x - w / 2, top), (x + w / 2, top), (x + w / 2 + sk, yb), (x - w / 2 + sk, yb), close=True)
            c.drawPath(pg, K.paint("#FFFFFF"))
            c.drawPath(pg, K.paint(BLACK, 1, 6))
        return None

    return fn


def magnifier_fn(x, y, s, size, idx):
    """drop：一行大字盖章似地落下，放大镜从上方扣到第 idx 个字上，镜片里那个字放大变红。"""
    zx = char_x(s, x, size, idx)
    r = size * 0.72

    def fn(c, k, t):
        e = ease_out(clamp01(k / 0.5))
        with K.at(c, x, y, 0, lerp(1.4, 1.0, e)):
            K.text(c, s, 0, 0, size, "hand", BLACK, e)
        f = ease_out(clamp01(k / 0.8))
        off = -520 * (1 - f)
        lx, ly = zx, y + off
        c.drawLine(lx + r * 0.72, ly + r * 0.72, lx + r * 1.75, ly + r * 1.75, K.paint(BLACK, 1, 34))
        c.drawCircle(lx, ly, r, K.paint("#FFFFFF"))
        c.save()
        clip = skia.Path()
        clip.addCircle(lx, ly, r)
        c.clipPath(clip, doAntiAlias=True)
        K.text(c, s[idx], lx, ly, size * 1.25, "hand", RED)
        c.restore()
        c.drawCircle(lx, ly, r, K.paint(BLACK, 1, 14))
        return None

    return fn


def camcorder(x, y, s=1.0) -> skia.Path:
    """摄像机：机身 + 两个片盘 + 朝右的镜头。"""
    return join(rect(x - 30 * s, y, 230 * s, 150 * s, 18 * s), circle(x - 90 * s, y - 120 * s, 45 * s),
                circle(x + 10 * s, y - 120 * s, 45 * s),
                P((x + 85 * s, y - 35 * s), (x + 165 * s, y - 75 * s), (x + 165 * s, y + 75 * s), (x + 85 * s, y + 35 * s)))


def rec_dot_fn(x, y):
    def fn(c, k, t):
        c.drawCircle(x, y, 16 * ease_out(k), K.paint(RED))
        return None

    return fn


def gavel(x, y, s=1.0) -> skia.Path:
    """法官锤：斜着的锤头 + 锤柄 + 底座。(x, y) 为锤头中心。"""
    a = math.radians(-35)
    ux, uy = math.cos(a), math.sin(a)          # 锤头长轴
    vx, vy = -uy, ux
    hl, hw = 120 * s, 50 * s
    head = P(*[(x + ux * hl * i + vx * hw * j, y + uy * hl * i + vy * hw * j) for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))],
             close=True)
    handle = P((x + vx * hw, y + vy * hw), (x + vx * 330 * s, y + vy * 330 * s))
    base = rect(x - 150 * s, y + 200 * s, 220 * s, 50 * s, 10 * s)
    return join(head, handle, base)


def bang(x, y, r=90) -> skia.Path:
    """敲击的短放射线。"""
    parts = []
    for a in (-150, -110, -70, -30):
        t = math.radians(a)
        parts.append(P((x + r * math.cos(t), y + r * math.sin(t)), (x + 1.6 * r * math.cos(t), y + 1.6 * r * math.sin(t))))
    return join(*parts)


def count_fn(x, y, size=130):
    """倒数两拍：前半拍显示 2，后半拍显示 1，倒数完消失（留给揭晓）。"""

    def fn(c, k, t):
        if k >= 1:
            return None
        n = "2" if k < 0.5 else "1"
        f = (k % 0.5) / 0.5
        with K.at(c, x, y, 0, lerp(1.25, 1.0, ease_out(clamp01(f / 0.4)))):
            c.drawCircle(0, 0, size * 0.62, K.paint(BLACK, 1, 8))
            K.text(c, n, 0, 0, size, "hand", RED)
        return None

    return fn


def cage(x, y, w, h) -> skia.Path:
    """笼子：拱顶 + 底座 + 竖栏 + 顶上挂环。"""
    x0, x1, y0, y1 = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    top = skia.Path()
    top.moveTo(x0, y0 + 60)
    top.quadTo(x, y0 - 90, x1, y0 + 60)
    parts = [top, P((x0 - 30, y1), (x1 + 30, y1)), P((x0, y0 + 60), (x1, y0 + 60)), circle(x, y0 - 48, 22)]
    n = 7
    for i in range(n + 1):
        bx = x0 + w * i / n
        parts.append(P((bx, y0 + 60 - (0 if i in (0, n) else 40 * math.sin(math.pi * i / n))), (bx, y1)))
    return join(*parts)


def padlock(x, y, s=1.0) -> skia.Path:
    sh = skia.Path()
    sh.addArc(skia.Rect.MakeXYWH(x - 32 * s, y - 70 * s, 64 * s, 70 * s), 180, 180)
    return join(rect(x, y + 20 * s, 100 * s, 80 * s, 12 * s), sh, P((x - 32 * s, y - 35 * s), (x - 32 * s, y - 20 * s)),
                P((x + 32 * s, y - 35 * s), (x + 32 * s, y - 20 * s)), circle(x, y + 14 * s, 9 * s))


def week(x, y, w=900, head=100, h=360) -> skia.Path:
    """一周五天的日历条：外框 + 表头线 + 四根竖线。"""
    x0, y0 = x - w / 2, y - h / 2
    return join(rect(x, y, w, h, 18), P((x0, y0 + head), (x0 + w, y0 + head)),
                *[P((x0 + w * i / 5, y0), (x0 + w * i / 5, y0 + h)) for i in range(1, 5)])


def scale_beam(x, y) -> skia.Path:
    """天平（不偏不倚）：支架 + 横梁 + 两根吊绳。(x, y) 为支点。"""
    return join(P((x, y), (x, y + 560)), P((x - 140, y + 560), (x + 140, y + 560)), circle(x, y, 16),
                P((x - 300, y), (x + 300, y)), P((x - 300, y), (x - 300, y + 60)), P((x + 300, y), (x + 300, y + 60)))


# ---------------------------------------------------------------- 开局（场景 1–3）：同一块白板上推拉
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

BOSS = (1000, 1450)             # 组长脚底
MATE = (2450, 1450)             # 同事脚底
PA = (1350, 800, 600, 300)      # 小泡（组长的话）
PA_TAIL = (1080, 1150)
SAY = "你总迟到"

scene("你总迟到", "开局", (1250, 1000, 0.85), bars=2)
L(stick(*BOSS, 0.8, "point", tie=True), 0, 0.9, BLACK, 10, sfx="wood_high")
L(pao(*PA, PA_TAIL), 1, 1.8, BLACK, 10, sfx="pop")
T(SAY, PA[0], PA[1] + 40, 96, k0=2, k1=3)
H(2, "pop")
L(pao_face(*PA, "sad"), 3, 3.5, BLACK, 8, sfx="wood_low")
L(spikes(*PA, skip=tail_angle(*PA, PA_TAIL)), 4, 4.9, RED, 9, sfx="rim")
T("组长", BOSS[0], BOSS[1] + 62, 54, k0=5, k1=5.8, sfx="pop")

CAL = (2150, 1250)
B2 = (2200, 780)
scene("对方当场炸了", "开局 · 当场炸了", (2150, 1000, 0.85))
L(stick(*MATE, 0.8, "shrug", hair=True), 0, 0.9, BLACK, 10, sfx="wood_high")
L(join(face(*MATE, 0.8, "sad"), P((MATE[0] - 30, 1180), (MATE[0] - 8, 1192)), P((MATE[0] + 30, 1180), (MATE[0] + 8, 1192))),
  1, 1.6, RED, 8, sfx="pop")
L(bubble(*B2, 560, 150, 1), 2, 2.4, BLACK, 8, sfx="tom")
T("我哪天总迟到了？", B2[0], B2[1], 56, k0=2.4, k1=4.4)
L(calendar(*CAL), 5, 5.9, BLACK, 8, sfx="wood_high")
C(6, 7.6, flip_fn(*CAL), sfx="shaker")
T("周一？周三？", CAL[0], 1440, 56, RED, k0=6.4, k1=7.9)
H(7, "shaker", 0.6)

scene("一句话，错在哪", "开局 · 错在哪", (1750, 1000, 0.62))
L(qmark(1810, 790, 1.15), 0, 0.9, RED, 14, sfx="tom")
T("明明迟到过", 1750, 470, 84, k0=2, k1=3.25, sfx="pop")
T("为啥吵起来？", 1750, 1620, 76, RED, k0=4, k1=5.5, sfx="pop")
L(join(anger(BOSS[0] + 95, 1140), anger(MATE[0] - 95, 1140)), 6, 6.8, RED, 8, sfx="rim")

# ---------------------------------------------------------------- drop（场景 4）：放大镜扣在“总”字上

DROP = (1800, 2150)
scene("评论混进来了", "非暴力沟通 · 书中观点", (1800, 2380, 0.85), shake=[0], flashes=[0])
b.move(J(), 0, (1800, 2380, 0.85), dur=0.12)      # drop：镜头几乎硬切到位，放大镜扣下那一下就在画面里
C(0, 0.5, magnifier_fn(*DROP, SAY, 200, 1), sfx="kick")
ZX = char_x(SAY, DROP[0], 200, 1)
L(circle(ZX, DROP[1], 200), 1, 1.6, RED, 14, sfx="rim")
L(arrow((ZX - 170, DROP[1] + 200), (1420, 2500), 0.15, 36), 2, 2.8, RED, 9, sfx="wood_high")
T("评论", 1400, 2600, 96, RED, k0=3, k1=3.8, sfx="pop")
L(rect(1400, 2600, 280, 150, 18), 3.8, 4.4, RED, 8)
T("听着像批评", 2000, 2580, 72, k0=5, k1=6.25, sfx="pop")
T("就会反驳", 2000, 2730, 76, RED, k0=7, k1=8, sfx="tom")

# ---------------------------------------------------------------- 亮书 + 书中观点（场景 5–6）

FC = (1800, 3880)
scene("有本书讲过", "非暴力沟通 · 第三章", (1800, 3650, 0.85))
L(book(1500, 3430, 360, 240), 0, 0.9, BLACK, 9, sfx="wood_low")
T("非暴力沟通", 2080, 3370, 72, GREEN, k0=1, k1=2.25, sfx="pop")
T("卢森堡", 2080, 3490, 56, k0=2.4, k1=3.2)
frame, icons, CX = fourcard(*FC)
L(frame, 3, 3.9, BLACK, 8, sfx="wood_high")
L(icons, 4, 4.9, BLACK, 7, sfx="pop")
C(6, 6.8, fill_fn(CX[0], FC[1], CARD_W / 4, CARD_H, BLUE), sfx="ding")
T("观察", CX[0], FC[1] + 75, 50, BLUE, k0=7, k1=7.8, sfx="pop")

CAM = (1380, 4660)
GV = (2250, 4600)
scene("只说看到的", "书中观点 · 观察和评论", (1800, 4850, 0.85))
L(stick(1800, 5330, 0.6, hair=True), 0, 0.8, BLACK, 9, sfx="wood_high")
L(camcorder(*CAM), 1, 1.9, BLUE, 9, sfx="wood_low")
C(1.9, 2.2, rec_dot_fn(CAM[0] - 110, CAM[1] - 40))
T("观察", CAM[0], 4440, 70, BLUE, k0=2, k1=2.8, sfx="pop")
T("九点二十到", CAM[0], 4900, 62, BLUE, k0=3, k1=4.25, sfx="pop")
L(P((1800, 4390), (1800, 5020)), 4.4, 4.9, BLACK, 6)
L(gavel(*GV), 5, 5.9, BLACK, 9, sfx="wood_high")
T("评论", 2220, 4440, 70, RED, k0=6, k1=6.8, sfx="pop")
T("懒", 2100, 4950, 120, RED, k0=7, k1=7.6, sfx="tom")
L(bang(2100, 4950, 80), 7.6, 8, RED, 7)

# ---------------------------------------------------------------- 小测验（场景 7–10）：四张题卡排成田字

BW_, BH_ = 360, 150             # 按钮


def quiz(cx, cy, n, q, size=64):
    """题卡骨架：外框 + 题号 + 题目泡泡 + 两颗按钮；返回两颗按钮中心。"""
    L(rect(cx, cy, 1080, 960, 30), 0, 0.8, BLACK, 8, sfx="wood_high")
    T(f"第 {n} 题", cx - 380, cy - 400, 56, k0=0.8, k1=1.6)
    L(bubble(cx, cy - 190, 900, 190, -1), 2, 2.4, BLACK, 8, sfx="pop")
    T(q, cx, cy - 190, size, k0=2.4, k1=2.4 + max(0.8, 0.25 * len(q)))
    bo, bp = (cx - 230, cy + 110), (cx + 230, cy + 110)
    return bo, bp


def buttons(bo, bp, k):
    L(join(rect(*bo, BW_, BH_, 75), rect(*bp, BW_, BH_, 75)), k, k + 0.8, BLACK, 8, sfx="wood_low")
    T("观察", bo[0], bo[1], 66, BLUE, k0=k + 0.8, k1=k + 1.6)
    T("评论", bp[0], bp[1], 66, RED, k0=k + 0.8, k1=k + 1.6)


def countdown(cx, cy, k=5):
    C(k, k + 2, count_fn(cx, cy + 340), sfx="shaker")
    H(k + 1, "shaker", 0.7)


Q1 = (1100, 6200)
scene("第一题，猜猜看", "小测验 · 第一题", (*Q1, 0.85))
bo, bp = quiz(*Q1, 1, "他很懒", 80)
buttons(bo, bp, 3.4)
H(4, "wood_low", 0.6)
countdown(*Q1)
L(rect(*bp, BW_ + 50, BH_ + 50, 95), 7, 7.6, RED, 12, sfx="rim")
L(cross(bp[0] + 230, bp[1] - 100, 34), 7.4, 7.9, RED, 10)

Q2 = (2500, 6200)
scene("第二题", "小测验 · 第二题", (*Q2, 0.85))
bo, bp = quiz(*Q2, 2, "他这周有 3 天没交日报", 58)
buttons(bo, bp, 4)
countdown(*Q2, 5.5)
L(rect(*bo, BW_ + 50, BH_ + 50, 95), 7, 7.6, BLUE, 12, sfx="ding")
L(check(bo[0] - 250, bo[1] - 100, 40), 7.3, 7.9, GREEN, 11)

Q3 = (1100, 7500)
Q3S = "她老是不回消息"
scene("第三题", "小测验 · 第三题", (*Q3, 0.85))
bo, bp = quiz(*Q3, 3, Q3S, 66)
buttons(bo, bp, 4)
countdown(*Q3, 5.5)
lx = (char_x(Q3S, Q3[0], 66, 1) + char_x(Q3S, Q3[0], 66, 2)) / 2
L(join(oval(lx, Q3[1] - 190, 190, 110), rect(*bp, BW_ + 50, BH_ + 50, 95)), 7, 7.8, RED, 10, sfx="rim")

Q4 = (2500, 7500)
scene("第四题", "小测验 · 第四题", (*Q4, 0.85))
L(rect(*Q4, 1080, 960, 30), 0, 0.8, BLACK, 8, sfx="wood_high")
T("第 4 题", Q4[0] - 380, Q4[1] - 400, 56, k0=0.8, k1=1.6)
T("哪句是观察？", Q4[0] + 80, Q4[1] - 400, 60, k0=1.6, k1=3.1)
H(2, "pop")
PIV = (Q4[0], Q4[1] - 250)
L(scale_beam(*PIV), 3, 3.9, BLACK, 8, sfx="wood_low")
LP, RP = (PIV[0] - 300, PIV[1] + 170), (PIV[0] + 300, PIV[1] + 190)
L(join(rect(*LP, 380, 220, 18), rect(*RP, 400, 260, 18)), 4, 4.6, BLACK, 7, sfx="pop")
T("领导偏心", LP[0], LP[1], 64, k0=4.6, k1=5.6)
T("这个月 3 个项目", RP[0], RP[1] - 45, 50, k0=5, k1=6.2)
T("都给了同一个人", RP[0], RP[1] + 40, 50, k0=6.2, k1=7.4)
H(5, "wood_high", 0.6)
C(6, 7, count_fn(Q4[0], Q4[1] + 360, 110), sfx="shaker")
T("评论 ✗", LP[0], Q4[1] + 230, 60, RED, k0=7, k1=7.8, sfx="rim")
T("观察 ✓", RP[0], Q4[1] + 230, 60, BLUE, k0=7, k1=7.8)

# ---------------------------------------------------------------- 书中观点 + 做法（场景 11–12）

WY = 8820
scene("总、老、从来", "书中观点 · 露馅的词", (1800, 8880, 0.85))
T("总", 1460, WY, 120, RED, k0=0, k1=0.8, sfx="pop")
T("老", 1780, WY, 120, RED, k0=1, k1=1.8, sfx="pop")
T("从来", 2130, WY, 120, RED, k0=2, k1=2.8, sfx="pop")
L(cage(1800, 8780, 1000, 380), 3, 4.2, BLACK, 8, sfx="wood_high")
L(padlock(2300, 8900, 0.9), 5, 5.6, BLACK, 8, sfx="rim")
T("一用就像评论", 1800, 9180, 72, k0=6, k1=7.5, sfx="pop")

WK = (1800, 10000)
scene("换成时间和次数", "做法 · 据书中思路", (1800, 10060, 0.85))
T("这周", WK[0], 9690, 66, k0=0, k1=0.8, sfx="pop")
L(week(*WK), 1, 1.9, BLACK, 8, sfx="wood_high")
DAYS = [WK[0] - 450 + 90 + 180 * i for i in range(5)]
for i, d in enumerate("一二三四五"):
    T(d, DAYS[i], WK[1] - 130, 54, k0=2, k1=2.8, sfx="pop" if i == 0 else None)
for n, i in enumerate((1, 3)):
    L(circle(DAYS[i], WK[1] + 50, 82), 3 + 2 * n, 3.6 + 2 * n, RED, 9, sfx="rim")
    T("9:20", DAYS[i], WK[1] + 50, 50, RED, k0=3.6 + 2 * n, k1=4.4 + 2 * n)
T("共 2 次", WK[0], 10330, 72, BLUE, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 再说一遍（场景 13）：小泡的刺缩回去

PB = (1800, 11120, 820, 340)
PB_TAIL = (1490, 11480)
BOSS2, MATE2 = (1400, 11820), (2350, 11820)
scene("再说一遍", "再说一遍 · 改写", (1800, 11360, 0.85))
L(join(stick(*BOSS2, 0.75, "point", tie=True), face(*BOSS2, 0.75, "flat"), stick(*MATE2, 0.75, hair=True)), 0, 0.9, BLACK,
  9, sfx="wood_high")
L(pao(*PB, PB_TAIL), 1, 1.8, BLACK, 10, sfx="pop")
C(1.8, 2.2, pao_turn_fn(J(), *PB, PB_TAIL, 6, 7.4))
T("这周2天9:20到", PB[0], PB[1] + 10, 66, k0=2, k1=4.25, sfx="pop")
T("早会没赶上", PB[0], PB[1] + 95, 66, k0=5, k1=6.25, sfx="pop")
H(6, "pop")
L(face(*MATE2, 0.75, "smile"), 7, 7.5, BLACK, 8, sfx="ding")
L(join(P((MATE2[0] + 70, 11560), (MATE2[0] + 90, 11600)), P((MATE2[0] + 90, 11530), (MATE2[0] + 115, 11585))), 7.5, 7.9,
  BLUE, 7)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：第 0 拍拉远看全板，第 4 拍推到评论区

FAR = (1800, 6500, 0.095)
CM = (1800, 12720, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
H(0, "cymbal", 0.5)
H(2, "ding")
b.move(J(), 4, CM)
H(4, "wood_high", 0.6)
L(rect(1800, 12560, 1160, 380, 30), 5, 5.8, BLACK, 8, sfx="wood_low")
T("你会怎么改", 1800, 12470, 70, RED, k0=6, k1=7.25, sfx="pop")
T("“你从来不洗碗”？", 1800, 12640, 70, RED, k0=7.4, k1=9.6)
T("下一讲：“我觉得你不在乎”，算感受吗？", 1800, 12880, 50, k0=10, k1=14.5, sfx="wood_high")
PE = (1800, 13130, 300, 150)
L(join(oval(*PE[:2], PE[2], PE[3]), pao_face(*PE, "smile")), 15, 15.8, BLUE, 8, sfx="pop")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "observe", "观察和评论", "“你总迟到”，为啥一说就炸？", ACC, b.shots,
                 [f"{BOOK}第三章“区分观察和评论”（转述）",
                  "中译本：阮胤华译，华夏出版社（2009 起多版；豆瓣 subject/26331553、30761952）"],
                 "“你总迟到”|为啥一说就【炸】", SQUARE_SHOT,
                 ["书中观点均为转述：把评论混进观察，对方容易听成批评，就会反驳；“总是”“从不”“每次”这类词常把观察变成评论；"
                  "章末有“观察还是评论”的练习。见第三章“区分观察和评论”。上屏均为转述，不是逐字引文。",
                  "组长与同事、“你总迟到”的开局、四道小测验题（他很懒 / 他这周有三天没交日报 / 她老是不回消息 / "
                  "领导偏心与“这个月三个项目都给了同一个人”）以及改写句“这周有两天九点二十到，早会没赶上”均为示意，"
                  "不照抄书中练习题，不指向任何具体公司或个人；日期、次数、时间点为示意，不是数据。",
                  "“观察 = 摄像机能拍到的，评论 = 加了自己的判断”（摄像机与法官锤）为对书中观点的通俗比喻；"
                  "“说出哪天、几次、什么事”为据书中思路整理的做法。",
                  "四格卡（眼睛 / 心 / 电池 / 手 = 观察 / 感受 / 需要 / 请求）与小泡为本系列的视觉角色，本讲点亮“眼睛”一格。"],
                 tags="#职场沟通 #情商")
    return b.attach(ep)
