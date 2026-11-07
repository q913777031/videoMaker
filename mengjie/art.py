"""《梦的解析》系列共用：画面元件（梦泡泡、月亮、床、弗洛伊德、小女孩……）、拍点小工具 Kit、每讲样式 THEMES、
按 PLAN.md 建 Lesson（setup）。分镜模块写法见 mengjie/ep02_wish.py。

坐标约定同 fengtian：人物 (x, y) 为脚底，头在 y - 290*s；每屏取景 (cx, cy + 10, Z=0.72)，内容放在 cx±560、cy-560…cy+520。
颜色用白板墨色（BLACK / RED / BLUE / GREEN / ORANGE / NIGHT），换纸色时由 fengtian.theme.Recolor 统一处理。
"""

import math
from contextlib import contextmanager
from pathlib import Path

import skia

from adler import core
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import hooks as HK
from fengtian import plan
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_li, pop_scale, slam_scale  # noqa: F401
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross, rect  # noqa: F401

PLAN = Path(__file__).with_name("PLAN.md")
core.SERIES.update(name="梦的解析", count="第一季", prefix="梦的解析")
HK.SERIES_SUB = "弗洛伊德 · 梦的解析"

GRAY, GRAY_FILL = "#8A8F99", "#ECEEF1"
SKIN, WOOD, PAPER_W = "#FBE3CF", "#E3C9A0", "#FFFFFF"
NIGHT, NIGHT_FILL, CLOUD = "#3B3A8C", "#E4E2F6", "#FFFFFF"
SUIT = "#3D4A63"
NOTE_FILL, RED_FILL, GREEN_FILL, BLUE_FILL = "#FFF1A8", "#F6C3BE", "#D3EDDC", "#CFE0F5"

# 每讲一套样式（纸色、纹理、主题色、页眉、转场），相邻两讲不同；都是浅色纸
THEMES = {
    "01": dict(name="月夜蓝格", acc="#3B3A8C", paper="#E9EEF7", pattern="grid", pat="#B9C7DF", grid=80, header="circle", move="pullpush", move_s=1.4),
    "02": dict(name="奶油点阵", acc="#B4471E", paper="#FBF0DC", pattern="dots", pat="#E3C79A", grid=60, header="tab", move="pan", move_s=1.35),
    "03": dict(name="淡粉信纸", acc="#8E2C5C", paper="#F8E6E8", pattern="ruled", pat="#E8B9C0", margin=None, header="stamp", move="swing", move_s=1.25),
    "04": dict(name="牛皮纸", acc="#6B3A12", paper="#EAD7B4", pattern="kraft", pat="#C2A479", header="circle", move="drop", move_s=1.3),
    "05": dict(name="薄荷方格", acc="#1F6B5C", paper="#E2F1EC", pattern="grid", pat="#A6CFC3", grid=60, header="bar", move="tilt", move_s=1.4),
    "06": dict(name="薰衣草点阵", acc="#5537A0", paper="#ECE7F6", pattern="dots", pat="#B7A9D8", header="pill", move="arc", move_s=1.45),
    "07": dict(name="天蓝横线", acc="#B53A0A", paper="#DCEBF7", pattern="ruled", pat="#9DBFDD", margin=None, header="tab", move="wipe", move_s=1.05),
    "08": dict(name="暖杏方格", acc="#0F6E6E", paper="#F6E3CC", pattern="grid", pat="#E2BF98", grid=100, header="stamp", move="pullpush", move_s=1.4),
    "09": dict(name="晨粉点阵", acc="#0B7285", paper="#F9E1EA", pattern="dots", pat="#E3A9BE", grid=64, header="circle", move="pan", move_s=1.3),
    "10": dict(name="方眼本", acc="#A8401A", paper="#E4EFEC", pattern="graph", pat="#9EC3BA", grid=44, header="bar", move="drop", move_s=1.3),
    "11": dict(name="雾灰横线", acc="#2E3A8C", paper="#E8E8EE", pattern="ruled", pat="#B8BACB", margin="#D9A0A0", header="pill", move="swing", move_s=1.3),
    "12": dict(name="白色工程纸", acc="#C62828", paper="#F6F8FB", pattern="grid", pat="#B9CCE6", grid=60, header="tab", move="wipe", move_s=1.0),
    "13": dict(name="淡黄格子纸", acc="#3B3A8C", paper="#FBF1C8", pattern="grid", pat="#E3CF86", header="circle", move="tilt", move_s=1.4),
}


def setup(nn, hook_fn, drop_screen=2, hold=1.55):
    """按 PLAN.md「### nn」建一讲：注册开场钩子（大字 = PLAN 里的 HOOK）、按 SCREENS 分屏、蛇形排白板区块。
    返回 (L, R, Z)：L 为 fengtian.common.Lesson，R[j] 为第 j 屏区块中心，Z 为默认取景缩放。"""
    p = plan.load(nn, PLAN)
    key = f"mj{nn}"
    HK.HOOK_TEXT[key] = p["HOOK"]
    HK.HOOKS[key] = hook_fn
    screens = [(ls, tag, i) for i, (ls, tag) in enumerate(p["SCREENS"])]
    n = len(screens) - 2
    rows = (n + 2) // 3
    theme = dict(THEMES[nn], hook=key)
    L = C.Lesson(nn, screens, drop_screen=drop_screen, hold=hold, board_size=(5000, 2500 + 1600 * rows + 400),
                 theme=theme, plan_path=PLAN)
    cols = (900, 2500, 4100)
    R = [(2600, 800), (900, 900)] + [(cols[i % 3] if (i // 3) % 2 == 0 else cols[2 - i % 3], 2500 + 1600 * (i // 3))
                                     for i in range(n)]
    return L, R, 0.72


class Kit:
    """拍点小工具（绑定一讲的 Lesson）：
      nx(j, t, prev) 离本地秒 t 最近、且在 prev 之后的拍（不超过本屏能放事件的最后一拍）；
      kq(j, t, lo) 离 t 最近的拍；cap(j, k) 夹到最后可用拍；klast(j) 最后可用拍（事件做完到切屏至少停 1.6 秒）；
      ev(j, k, fn, sfx) 第 j 屏第 k 拍放一个自定义项；pop_fn(j, k, draw) 把 draw(c, sc, T) 包成第 k 拍弹出。"""

    def __init__(self, L):
        self.L, self.b = L, L.b
        self.tb, self.wt = L.tb, L.wt

    def nbeats(self, j):
        return self.L.BOUNDS[j][1] - self.L.BOUNDS[j][0]

    def kq(self, j, t_local, lo=0):
        return self.L.kb(j, t_local, lo=min(lo, self.nbeats(j) - 1))

    def klast(self, j, tail=0.35):
        b0, b1 = self.L.BOUNDS[j]
        return max(k for k in range(b1 - b0) if core.bt(b0 + k) + tail <= core.bt(b1) - 1.6)

    def cap(self, j, k, tail=0.35):
        return min(k, self.klast(j, tail))

    def nx(self, j, t_local, prev, gap=1):
        return self.cap(j, max(self.kq(j, t_local, prev + gap), prev + gap))

    def pop_fn(self, j, k, draw, dur=0.32):
        def fn(c, kk, T):
            sc = pop_scale(T - self.tb(j, k), dur)
            if sc > 0:
                draw(c, sc, T)
            return None
        return fn

    def ev(self, j, k, fn, sfx=None, gain=0.8, dur=0.3):
        self.b.custom(j, k, k + dur, fn, sfx=sfx, gain=gain)

    def next_card(self, j, k, title, cx, cy, w=1000):
        """评论区屏底部的“下一讲”预告卡：第 k 拍画框，随后写“下一讲”与片名（片名自动缩到框内）。"""
        b = self.b
        b.path(j, k, k + 0.6, rect(cx, cy, w, 240, 24), BLUE, 8, sfx="wood_high")
        b.text(j, k + 0.5, k + 0.8, "下一讲", cx - w / 2 + 110, cy - 70, 46, BLUE)
        size = min(56, 56 * (w - 80) / max(1.0, K.text_w(title, 56, "hand")))
        b.text(j, k + 0.8, k + 2.0, title, cx, cy + 30, size, BLACK)


@contextmanager
def at_pop(c, x, y, sc):
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    c.translate(-x, -y)
    try:
        yield
    finally:
        c.restore()


def box(c, x, y, w, h, fill, line, width=6, r=14, alpha=1.0):
    rr = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(rr, r, r, K.paint(fill, alpha))
    c.drawRoundRect(rr, r, r, wb.marker(line, width, alpha))


def _sweat(c, x, y, s=1.0, alpha=1.0):
    p = skia.Path()
    p.moveTo(x, y - 22 * s)
    p.quadTo(x + 16 * s, y + 2 * s, x, y + 12 * s)
    p.quadTo(x - 16 * s, y + 2 * s, x, y - 22 * s)
    c.drawPath(p, K.paint("#BFDDF7", alpha))
    c.drawPath(p, wb.marker(BLUE, 4, alpha))


def sparkle(c, x, y, dt, color=YELLOW, n=8, r0=40, r1=130):
    if dt < 0 or dt > 0.9:
        return
    f = ease_out(clamp01(dt / 0.5))
    a = 1 - clamp01((dt - 0.5) / 0.4)
    for i in range(n):
        ang = 2 * math.pi * i / n
        r_a, r_b = lerp(r0, r1 * 0.7, f), lerp(r0 + 20, r1, f)
        C.line(c, (x + math.cos(ang) * r_a, y + math.sin(ang) * r_a), (x + math.cos(ang) * r_b, y + math.sin(ang) * r_b),
               color, 7, a)


def cloud_path(x, y, w, h):
    """梦泡泡：椭圆主体 + 一圈鼓包（并集），(x, y) 为中心。"""
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    n = 9
    for i in range(n):
        a = 2 * math.pi * i / n
        r = min(w, h) * 0.2
        bx, by = x + math.cos(a) * w * 0.46, y + math.sin(a) * h * 0.44
        q = skia.Path()
        q.addCircle(bx, by, r)
        p = skia.Op(p, q, skia.PathOp.kUnion_PathOp)
    return p


def dream_cloud(c, x, y, w, h, sc, tail_to=None, alpha=1.0):
    """画一个梦泡泡（白底紫线），tail_to=(x, y) 时从泡泡到那儿画三个渐小的小圆。返回是否画了。"""
    if sc <= 0:
        return False
    if tail_to is not None:
        tx, ty = tail_to
        for i, f in enumerate((0.25, 0.55, 0.82)):
            if sc < 0.3 + 0.2 * i:
                continue
            px, py = lerp(x, tx, 0.62 + f * 0.38), lerp(y + h * 0.45, ty, 0.3 + f * 0.7)
            r = 26 - i * 7
            c.drawCircle(px, py, r, K.paint(CLOUD, alpha))
            c.drawCircle(px, py, r, wb.marker(NIGHT, 5, alpha))
    with at_pop(c, x, y, sc):
        p = cloud_path(x, y, w, h)
        c.drawPath(p, K.paint(CLOUD, alpha))
        c.drawPath(p, wb.marker(NIGHT, 8, alpha))
    return True


def moon(c, x, y, r=60, alpha=1.0):
    p = skia.Path()
    p.addCircle(x, y, r)
    q = skia.Path()
    q.addCircle(x + r * 0.45, y - r * 0.3, r * 0.85)
    m = skia.Op(p, q, skia.PathOp.kDifference_PathOp)
    c.drawPath(m, K.paint("#FFE39A", alpha))
    c.drawPath(m, wb.marker(YELLOW, 6, alpha))


def star(c, x, y, r=40, fill="#FFE39A", line=YELLOW, alpha=1.0, rot=0.0):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5 + rot
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    p = P(*pts, close=True)
    c.drawPath(p, K.paint(fill, alpha))
    c.drawPath(p, wb.marker(line, 5, alpha))


def sun(c, x, y, r=50, alpha=1.0):
    c.drawCircle(x, y, r, K.paint("#FFD27A", alpha))
    c.drawCircle(x, y, r, wb.marker(ORANGE, 6, alpha))
    for i in range(8):
        a = i * math.pi / 4
        C.line(c, (x + math.cos(a) * (r + 14), y + math.sin(a) * (r + 14)),
               (x + math.cos(a) * (r + 40), y + math.sin(a) * (r + 40)), ORANGE, 6, alpha)


def bed(c, x, y, w=520, alpha=1.0):
    """床：(x, y) 为床面左端；床头在左。"""
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, 50), K.paint(WOOD, alpha))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, 50), wb.marker("#A9773E", 7, alpha))
    C.line(c, (x, y - 90), (x, y + 110), "#A9773E", 12, alpha)
    C.line(c, (x + w, y - 20), (x + w, y + 110), "#A9773E", 12, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x + 14, y - 46, 110, 46), 20, 20, K.paint(PAPER_W, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x + 14, y - 46, 110, 46), 20, 20, wb.marker(GRAY, 5, alpha))


def sleeper(c, x, y, s, T, t_wake=None, mood="flat", sweat=False):
    """躺在床上的小李（脚在右）：t_wake 之后 0.25 秒内坐起来；被子盖住腰以下。(x, y) 为臀部。"""
    up = ease_out(clamp01((T - t_wake) / 0.25)) if t_wake is not None and T >= t_wake else 0.0
    rot = lerp(-90, 0, up)
    with K.at(c, x, y, rot):
        draw_li(c, 0, 120 * s, s, mood)
    blanket = skia.Rect.MakeXYWH(x - 30, y - 30, 330, 70)
    c.drawRoundRect(blanket, 26, 26, K.paint("#CFE0F5"))
    c.drawRoundRect(blanket, 26, 26, wb.marker(BLUE, 6))
    if sweat and up > 0.9:
        hy = y + 120 * s - 290 * s
        for n in range(3):
            ph = ((T - t_wake) * 1.4 + n * 0.33) % 1.0
            _sweat(c, x + (-70 if n % 2 else 70), hy - 20 + ph * 80, 1.0, 1 - ph)
    a = math.radians(rot)
    vy = (120 - 290) * s                       # 头相对臀部（坐直时）的偏移，随身体转动
    return x - vy * math.sin(a), y + vy * math.cos(a)


def draw_freud(c, x, y, s, mood="flat", alpha=1.0, cigar=True):
    """弗洛伊德：深色西装、白衬衫、圆眼镜、灰白胡子、后退的发际线。(x, y) 为脚底。"""
    hy = y - 290 * s
    torso = skia.Rect.MakeLTRB(x - 60 * s, hy + 50 * s, x + 60 * s, y - 100 * s)
    for foot in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, (x, y - 110 * s), foot, BLACK, 11, alpha)
    c.drawRoundRect(torso, 22 * s, 22 * s, K.paint(SUIT, alpha))
    c.drawRoundRect(torso, 22 * s, 22 * s, wb.marker(BLACK, 7, alpha))
    c.drawPath(P((x - 20 * s, hy + 52 * s), (x, hy + 110 * s), (x + 20 * s, hy + 52 * s), close=True), K.paint(PAPER_W, alpha))
    c.drawCircle(x, hy, 52 * s, K.paint(SKIN, alpha))
    c.drawCircle(x, hy, 52 * s, wb.marker(BLACK, 8, alpha))
    beard = skia.Path()
    beard.moveTo(x - 46 * s, hy + 6 * s)
    beard.quadTo(x - 40 * s, hy + 70 * s, x, hy + 82 * s)
    beard.quadTo(x + 40 * s, hy + 70 * s, x + 46 * s, hy + 6 * s)
    beard.quadTo(x, hy + 34 * s, x - 46 * s, hy + 6 * s)
    c.drawPath(beard, K.paint("#C9C9C9", alpha))
    c.drawPath(beard, wb.marker(GRAY, 5, alpha))
    for sg in (-1, 1):
        c.drawCircle(x + sg * 20 * s, hy - 10 * s, 15 * s, K.paint(PAPER_W, alpha * 0.6))
        c.drawCircle(x + sg * 20 * s, hy - 10 * s, 15 * s, wb.marker(BLACK, 4, alpha))
        c.drawCircle(x + sg * 20 * s, hy - 10 * s, 3.5 * s, K.paint(BLACK, alpha))
        C.line(c, (x + sg * 36 * s, hy - 26 * s), (x + sg * 50 * s, hy - 16 * s), "#9A9A9A", 8, alpha)
    C.line(c, (x - 5 * s, hy - 10 * s), (x + 5 * s, hy - 10 * s), BLACK, 3, alpha)
    if mood == "smile":
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(x - 14 * s, hy + 14 * s, 28 * s, 16 * s), 20, 140)
        c.drawPath(m, wb.marker(BLACK, 5, alpha))
    else:
        C.line(c, (x - 12 * s, hy + 26 * s), (x + 12 * s, hy + 26 * s), BLACK, 5, alpha)
    if cigar:
        C.line(c, (x + 12 * s, hy + 28 * s), (x + 62 * s, hy + 36 * s), "#8A5A2B", 9, alpha)
        c.drawCircle(x + 64 * s, hy + 36 * s, 5 * s, K.paint(RED, alpha))
    rh = (x + 75 * s, hy + 175 * s)
    lh = (x - 75 * s, hy + 175 * s)
    for h_ in (lh, rh):
        C.line(c, (x, hy + 80 * s), h_, SUIT, 12, alpha)


def draw_girl(c, x, y, s, mood="flat", alpha=1.0):
    """小女孩：短裙、两个小辫。(x, y) 为脚底。"""
    hy = y - 220 * s
    for foot in ((x - 30 * s, y), (x + 30 * s, y)):
        C.line(c, (x, y - 70 * s), foot, BLACK, 9, alpha)
    dress = P((x, hy + 40 * s), (x - 60 * s, y - 60 * s), (x + 60 * s, y - 60 * s), close=True)
    c.drawPath(dress, K.paint("#F6C3BE", alpha))
    c.drawPath(dress, wb.marker(RED, 6, alpha))
    for sg in (-1, 1):
        C.line(c, (x, hy + 70 * s), (x + sg * 60 * s, hy + 120 * s), BLACK, 8, alpha)
        c.drawCircle(x + sg * 50 * s, hy - 10 * s, 16 * s, K.paint("#5A3A2A", alpha))
    c.drawCircle(x, hy, 40 * s, K.paint(PAPER_W, alpha))
    c.drawCircle(x, hy, 40 * s, wb.marker(BLACK, 8, alpha))
    for dx in (-13, 13):
        c.drawCircle(x + dx * s, hy - 4 * s, 4 * s, K.paint(BLACK, alpha))
    m = skia.Path()
    if mood == "smile":
        m.addArc(skia.Rect.MakeXYWH(x - 13 * s, hy + 4 * s, 26 * s, 18 * s), 20, 140)
    else:
        m.addArc(skia.Rect.MakeXYWH(x - 12 * s, hy + 14 * s, 24 * s, 14 * s), 200, 140)
    c.drawPath(m, wb.marker(BLACK, 5, alpha))


def exam_paper(c, x, y, w=260, h=320, rot=0.0, title="考试", mark=None, alpha=1.0):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, PAPER_W, BLACK, 6, 6, alpha)
        K.text(c, title, -w / 2 + 70, -h / 2 + 46, 44, "hand", RED, alpha)
        for r in range(4):
            C.line(c, (-w / 2 + 30, -h / 2 + 110 + r * 48), (w / 2 - 30 - (r % 2) * 50, -h / 2 + 110 + r * 48), GRAY, 6,
                   alpha)
        if mark:
            K.text(c, mark, w / 2 - 60, -h / 2 + 56, 80, "hand", RED, alpha)


def pen(c, x, y, rot=-30, s=1.0, alpha=1.0):
    with K.at(c, x, y, rot, s):
        c.drawRoundRect(skia.Rect.MakeXYWH(-70, -12, 120, 24), 6, 6, K.paint("#FFD27A", alpha))
        c.drawRoundRect(skia.Rect.MakeXYWH(-70, -12, 120, 24), 6, 6, wb.marker(BLACK, 4, alpha))
        c.drawPath(P((50, -12), (80, 0), (50, 12), close=True), K.paint(SKIN, alpha))
        c.drawPath(P((50, -12), (80, 0), (50, 12), close=True), wb.marker(BLACK, 4, alpha))


def note_card(c, x, y, w, h, rot=0.0, fill="#FFF1A8", line=ORANGE):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, fill, line, 6, 8)


def brain(c, x, y, r=150):
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - r * 1.2, y - r * 0.85, r * 2.4, r * 1.7))
    c.drawPath(p, K.paint("#F6C3BE"))
    c.drawPath(p, wb.marker(RED, 8))
    C.line(c, (x, y - r * 0.85), (x, y + r * 0.7), RED, 5)
    for i in range(3):
        a = skia.Path()
        a.addArc(skia.Rect.MakeXYWH(x - r * 1.0 + i * 50, y - 60 + i * 30, 90, 60), 180, 180)
        c.drawPath(a, wb.marker(RED, 4))
        a2 = skia.Path()
        a2.addArc(skia.Rect.MakeXYWH(x + r * 0.15 + i * 40, y - 50 + i * 28, 90, 60), 0, 180)
        c.drawPath(a2, wb.marker(RED, 4))


def hook_text(H):
    """本讲开场大字（PLAN.md 的 HOOK）。"""
    return HK.HOOK_TEXT[H.THEME["hook"]]


def finish_hook(H, j, cx, cy, acc, size=128):
    """开场屏收尾：大字随开场配音逐字砸下，再弹出系列小字。画面内容放在 cy+130 以上。"""
    HK._finish(H, j, cx, cy, hook_text(H), acc, size=size)
