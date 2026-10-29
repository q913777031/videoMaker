"""白板手绘引擎：整讲在一块大白板上完成——一只手握马克笔按实测拍点描线写字，相机在白板上平移缩放，没有硬切。

接入阿德勒引擎的时间轴与交付流程：每个镜头仍是 1 小节的 core.Shot（字幕、页眉标签、打击乐音效、闪白、抖动照旧），
画面由本引擎的 draw_frame 绘制；封面与单讲横屏封面取白板画面。install() 只影响当前进程。

分镜写法（见 xitong/wb01_system.py）：
    b = Board()
    j = b.shot("字幕", "页眉标签", view=(cx, cy, z))          # 新镜头（1 小节），相机看向白板 (cx, cy)，缩放 z
    b.path(j, 0, 1.2, stick(500, 900), sfx="wood_high")     # 第 0–1.2 拍描出一条路径；sfx 只能放整数起拍
    b.text(j, 1, 2.5, "写字", 800, 700, 90, RED, sfx="pop")  # 第 1–2.5 拍逐字写出
    b.custom(j, 0, 4, fn)                                    # fn(c, k, t) 画动态内容，k 为本项进度 0–1，返回笔尖或 None
    ep = b.episode(no=1, ...)                                # 交给系列的 episode() 构造
"""

import math

import skia

from adler import core
from adler import kit as K
from engine import gfx
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

gfx.FONT_FILES.setdefault("hand", "MaShanZheng-Regular.ttf")

BLACK = "#1E1E24"
RED = "#D23A2E"
BLUE = "#2F62B8"
GREEN = "#2E8A57"
ORANGE = "#E07B24"
STAGE_Y = 800                # 白板视图中心在屏幕上的纵坐标（字幕区留在下方）
CAP_TOP, CAP_BOTTOM = 1290, 1520


# ---------------------------------------------------------------- 图元（白板坐标）

def P(*pts, close=False) -> skia.Path:
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def circle(x, y, r) -> skia.Path:
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def rect(x, y, w, h, r=24) -> skia.Path:
    p = skia.Path()
    p.addRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), r, r)
    return p


def join(*paths) -> skia.Path:
    out = skia.Path()
    for p in paths:
        out.addPath(p)
    return out


def stick(x, y, s=1.0, arms="down", tie=False, hair=False) -> skia.Path:
    """简笔小人：(x, y) 为脚底，身高约 330·s。arms：down / up / point / shrug / hold。"""
    hy = y - 290 * s
    body = P((x, hy + 45 * s), (x, y - 120 * s))
    legs = P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y))
    sh = hy + 80 * s
    arm = {
        "up": P((x - 80 * s, hy - 40 * s), (x, sh), (x + 80 * s, hy - 40 * s)),
        "point": join(P((x - 60 * s, hy + 150 * s), (x, sh)), P((x, sh), (x + 120 * s, hy + 60 * s))),
        "shrug": P((x - 90 * s, hy + 30 * s), (x - 50 * s, sh + 20 * s), (x, sh), (x + 50 * s, sh + 20 * s),
                   (x + 90 * s, hy + 30 * s)),
        "hold": P((x - 60 * s, hy + 130 * s), (x, sh), (x + 70 * s, hy + 120 * s), (x + 110 * s, hy + 90 * s)),
    }.get(arms, P((x - 70 * s, hy + 170 * s), (x, sh), (x + 70 * s, hy + 170 * s)))
    parts = [circle(x, hy, 45 * s), body, arm, legs]
    if tie:
        parts.append(P((x, hy + 50 * s), (x - 12 * s, hy + 100 * s), (x, hy + 120 * s), (x + 12 * s, hy + 100 * s),
                       close=True))
    if hair:
        parts.append(P((x - 45 * s, hy - 5 * s), (x - 30 * s, hy - 45 * s), (x + 30 * s, hy - 45 * s),
                       (x + 50 * s, hy + 10 * s)))
    return join(*parts)


def face(x, y, s=1.0, mood="smile") -> skia.Path:
    """配合 stick 的五官：(x, y) 为该小人的脚底。"""
    hy = y - 290 * s
    p = skia.Path()
    p.addCircle(x - 15 * s, hy - 8 * s, 3 * s)
    p.addCircle(x + 15 * s, hy - 8 * s, 3 * s)
    if mood == "smile":
        p.addArc(skia.Rect.MakeXYWH(x - 20 * s, hy - 5 * s, 40 * s, 28 * s), 20, 140)
    elif mood == "flat":
        p.moveTo(x - 15 * s, hy + 18 * s)
        p.lineTo(x + 15 * s, hy + 18 * s)
    else:
        p.addArc(skia.Rect.MakeXYWH(x - 18 * s, hy + 10 * s, 36 * s, 24 * s), 200, 140)
    return p


def bubble(x, y, w, h, tail=-1) -> skia.Path:
    p = rect(x, y, w, h, 40)
    p.moveTo(x + tail * w * 0.25, y + h / 2)
    p.lineTo(x + tail * w * 0.38, y + h / 2 + 60)
    p.lineTo(x + tail * w * 0.1, y + h / 2)
    return p


def arrow(a, b, bend=0.2, head=50) -> skia.Path:
    (x0, y0), (x1, y1) = a, b
    mx, my = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend
    p = skia.Path()
    p.moveTo(x0, y0)
    p.quadTo(mx, my, x1, y1)
    ang = math.atan2(y1 - my, x1 - mx)
    for d in (0.45, -0.45):
        p.moveTo(x1, y1)
        p.lineTo(x1 - head * math.cos(ang + d), y1 - head * math.sin(ang + d))
    return p


def cross(x, y, r=70) -> skia.Path:
    return join(P((x - r, y - r), (x + r, y + r)), P((x + r, y - r), (x - r, y + r)))


def check(x, y, r=60) -> skia.Path:
    return P((x - r, y), (x - r * 0.3, y + r * 0.7), (x + r, y - r * 0.8))


def scribble(x, y, w, h, n=7) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - w / 2, y - h / 2)
    for i in range(n):
        p.lineTo(x + w / 2 * (1 if i % 2 == 0 else -1), y - h / 2 + h * (i + 1) / n)
    return p


def underline(x0, x1, y, amp=14, step=40) -> skia.Path:
    p = skia.Path()
    p.moveTo(x0, y)
    x, k = x0, 0
    while x < x1:
        p.quadTo(x + step / 2, y + (amp if k % 2 == 0 else -amp), x + step, y)
        x += step
        k += 1
    return p


def spring_path(x, top, length, w=150, coils=12) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - w / 2, top)
    for i in range(coils * 2):
        y = top + length * (i + 1) / (coils * 2)
        p.lineTo(x + (w / 2 if i % 2 == 0 else -w / 2), y)
    return p


def clock(x, y, r) -> skia.Path:
    p = circle(x, y, r)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        p.moveTo(x + math.cos(a) * r * 0.82, y + math.sin(a) * r * 0.82)
        p.lineTo(x + math.cos(a) * r * 0.92, y + math.sin(a) * r * 0.92)
    return p


def hands_at(x, y, r, hour, minute) -> skia.Path:
    a1 = -math.pi / 2 + minute / 60 * 2 * math.pi
    a2 = -math.pi / 2 + (hour % 12 + minute / 60) / 12 * 2 * math.pi
    return join(P((x, y), (x + math.cos(a1) * r * 0.75, y + math.sin(a1) * r * 0.75)),
                P((x, y), (x + math.cos(a2) * r * 0.5, y + math.sin(a2) * r * 0.5)))


def book(x, y, w=360, h=240) -> skia.Path:
    return join(P((x, y - h / 2 + 20), (x - w / 2, y - h / 2), (x - w / 2, y + h / 2), (x, y + h / 2 + 20),
                  (x + w / 2, y + h / 2), (x + w / 2, y - h / 2), (x, y - h / 2 + 20), (x, y + h / 2 + 20)),
                P((x - w / 2 + 40, y - h / 4), (x - 40, y - h / 4 + 12)), P((x - w / 2 + 40, y), (x - 40, y + 12)),
                P((x + 40, y - h / 4 + 12), (x + w / 2 - 40, y - h / 4)), P((x + 40, y + 12), (x + w / 2 - 40, y)))


def building(x, y, w=260, h=360) -> skia.Path:
    """办公楼：(x, y) 为底边中点。"""
    parts = [P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y))]
    for r in range(3):
        for c in range(3):
            wx, wy = x - w / 2 + 50 + c * (w - 100) / 2, y - h + 60 + r * 80
            parts.append(rect(wx, wy, 44, 44, 4))
    parts.append(P((x - 30, y), (x - 30, y - 70), (x + 30, y - 70), (x + 30, y)))
    return join(*parts)


def desk(x, y, w=260) -> skia.Path:
    """工位：桌面 + 两条腿 + 电脑。(x, y) 为桌面中点。"""
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 20, y), (x - w / 2 + 20, y + 110)),
                P((x + w / 2 - 20, y), (x + w / 2 - 20, y + 110)), rect(x + 40, y - 60, 120, 90, 8),
                P((x + 40, y - 15), (x + 40, y)))


def doc(x, y, w=150, h=190, lines=4) -> skia.Path:
    parts = [P((x - w / 2, y - h / 2), (x + w / 2 - 40, y - h / 2), (x + w / 2, y - h / 2 + 40), (x + w / 2, y + h / 2),
               (x - w / 2, y + h / 2), close=True)]
    for i in range(lines):
        yy = y - h / 2 + 50 + i * (h - 70) / max(1, lines - 1)
        parts.append(P((x - w / 2 + 25, yy), (x + w / 2 - 30 - (i % 2) * 30, yy)))
    return join(*parts)


def scooter(x, y, s=1.0) -> skia.Path:
    """外卖电动车（侧视）：(x, y) 为地面中点。"""
    return join(circle(x - 110 * s, y - 45 * s, 45 * s), circle(x + 110 * s, y - 45 * s, 45 * s),
                P((x - 110 * s, y - 45 * s), (x - 40 * s, y - 120 * s), (x + 80 * s, y - 120 * s), (x + 110 * s, y - 45 * s)),
                P((x + 80 * s, y - 120 * s), (x + 110 * s, y - 230 * s), (x + 150 * s, y - 230 * s)),
                rect(x - 90 * s, y - 175 * s, 110 * s, 90 * s, 10))


def light(x, y) -> skia.Path:
    """红绿灯：(x, y) 为灯箱中点。"""
    return join(rect(x, y, 90, 230, 20), circle(x, y - 65, 28), circle(x, y, 28), circle(x, y + 65, 28),
                P((x, y + 115), (x, y + 330)))


def node(x, y, r=80) -> skia.Path:
    return circle(x, y, r)


def target(x, y, r=110) -> skia.Path:
    return join(circle(x, y, r), circle(x, y, r * 0.62), circle(x, y, r * 0.24))


def podium_list(x, y, n=4, w=320, h=80) -> skia.Path:
    parts = []
    for i in range(n):
        parts.append(rect(x, y + i * (h + 16), w, h, 10))
    return join(*parts)


# ---------------------------------------------------------------- 路径逐段显现

def partial(path: skia.Path, k: float):
    """取路径前 k 比例（按总长度），返回（部分路径，笔尖坐标）。"""
    if k >= 1:
        return path, None
    pm = skia.PathMeasure(path, False)
    lens = []
    while True:
        lens.append(pm.getLength())
        if not pm.nextContour():
            break
    total = sum(lens)
    target_len = total * k
    out = skia.Path()
    tip = None
    pm = skia.PathMeasure(path, False)
    acc = 0.0
    for L in lens:
        if acc >= target_len:
            break
        take = min(L, target_len - acc)
        if L > 0 and take > 0:
            sg = skia.Path()
            pm.getSegment(0, take, sg, True)
            out.addPath(sg)
            pos, _ = pm.getPosTan(take)
            tip = (pos.x(), pos.y())
        acc += L
        pm.nextContour()
    return out, tip


def marker(color, width, alpha=1.0):
    return K.paint(color, alpha, width)


# ---------------------------------------------------------------- 白板分镜

class Board:
    """一讲的白板分镜：镜头（core.Shot，1 小节）+ 白板绘制项 + 每镜相机视角。"""

    def __init__(self, size=(3600, 7200)):
        self.BW, self.BH = size
        self.shots: list = []
        self.views: list = []
        self.items: list = []
        self.ep = None

    def shot(self, text: str, tag: str, view=None, punch=0.0, **kw) -> int:
        view = view or (self.views[-1] if self.views else (900, 900, 1.0))
        self.shots.append(core.Shot(1, text, tag, [], text_beat=0, punch=punch, **kw))
        self.views.append(view)
        return len(self.shots) - 1

    def _hit(self, j, k0, sfx, gain=0.8, note=""):
        if sfx:
            if abs(k0 - round(k0)) > 1e-9:
                raise ValueError(f"镜头{j + 1}：音效只能放在整数拍（{k0}）")
            self.shots[j].hits.append((int(round(k0)), sfx, gain, note or sfx))

    @staticmethod
    def _snap(k0, k1, sfx):
        """带音效的项起笔吸附到最近的整数拍（整段平移），保证笔触与音效同帧。"""
        if sfx and abs(k0 - round(k0)) > 1e-9:
            d = round(k0) - k0
            return k0 + d, k1 + d
        return k0, k1

    def path(self, j, k0, k1, path, color=BLACK, width=10, sfx=None, gain=0.8):
        k0, k1 = self._snap(k0, k1, sfx)
        self.items.append(dict(j=j, k0=k0, k1=k1, kind="path", path=path, color=color, width=width))
        self._hit(j, k0, sfx, gain, "描线")

    def text(self, j, k0, k1, s, x, y, size, color=BLACK, font="hand", sfx=None, gain=0.8):
        k0, k1 = self._snap(k0, k1, sfx)
        self.items.append(dict(j=j, k0=k0, k1=k1, kind="text", s=s, x=x, y=y, size=size, color=color, font=font))
        self._hit(j, k0, sfx, gain, f"写字：{s}")

    def custom(self, j, k0, k1, fn, sfx=None, gain=0.8):
        k0, k1 = self._snap(k0, k1, sfx)
        self.items.append(dict(j=j, k0=k0, k1=k1, kind="custom", fn=fn))
        self._hit(j, k0, sfx, gain, "动作")

    def erase(self, j, k0, k1, x, y, w, h):
        """擦掉一块区域（白板擦），之后该区域内更早的内容不再显示。"""
        self.items.append(dict(j=j, k0=k0, k1=k1, kind="erase", rect=(x, y, w, h)))

    def hit(self, j, k, sfx, gain=0.8, note=""):
        self._hit(j, k, sfx, gain, note)

    def attach(self, ep):
        """把分镜挂到构造好的 Episode 上（之后才有每镜的拍点时刻）。"""
        self.ep = ep
        ep.board = self
        return ep

    # 时间
    def t_of(self, j, k):
        s = self.shots[j]
        if k >= 4:
            return s.t1 + (k - 4) * (s.t1 - core.bt(s.b0)) / 4
        i = int(math.floor(k))
        f = k - i
        a = core.bt(s.b0 + i)
        b = core.bt(s.b0 + i + 1)
        return a + (b - a) * f


# ---------------------------------------------------------------- 绘制

def _board_bg(c, board):
    c.drawColor(skia.ColorSetRGB(226, 229, 233))
    K.rr(c, board.BW / 2, board.BH / 2, board.BW, board.BH, 0, "#FBFBF9")
    for x0, y0, r in ((700, 1700, 500), (2600, 3800, 700), (1200, 5000, 500), (2800, 300, 400), (900, 6600, 600)):
        c.drawCircle(x0, y0, r, K.paint("#E9ECEF", 0.6, blur=120))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, board.BW, board.BH), K.paint("#C9CED6", 1, 30))


def _items(c, board, T):
    tip = None
    erases = []
    for it in board.items:
        if it["kind"] == "erase":
            t0 = board.t_of(it["j"], it["k0"])
            if T >= t0:
                erases.append((t0, board.t_of(it["j"], it["k1"]), it["rect"]))
    for it in board.items:
        if it["kind"] == "erase":
            continue
        t0, t1 = board.t_of(it["j"], it["k0"]), board.t_of(it["j"], it["k1"])
        if T < t0:
            continue
        k = clamp01((T - t0) / max(1e-3, t1 - t0))
        c.save()
        for e0, e1, (x, y, w, h) in erases:
            if e0 > t0:                       # 擦除发生在该项之后：被擦部分随擦除进度消失
                f = clamp01((T - e0) / max(1e-3, e1 - e0))
                c.clipRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w * f, h), skia.ClipOp.kDifference)
        if it["kind"] == "path":
            part, p = partial(it["path"], k)
            c.drawPath(part, marker(it["color"], it["width"]))
            c.drawPath(part, K.paint(it["color"], 0.22, it["width"] * 0.45, blur=1.2))
            if p:
                tip = p
        elif it["kind"] == "text":
            w = K.text_w(it["s"], it["size"], it["font"])
            x0 = it["x"] - w / 2
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(x0 - 20, it["y"] - it["size"], x0 + w * k + 4, it["y"] + it["size"]))
            K.text(c, it["s"], it["x"], it["y"], it["size"], it["font"], it["color"])
            c.restore()
            if k < 1:
                tip = (x0 + w * k, it["y"] + it["size"] * 0.25 * math.sin(k * 40))
        else:
            p = it["fn"](c, k, T)
            if p and k < 1:
                tip = p
        c.restore()
    for e0, e1, (x, y, w, h) in erases:
        if e0 <= T < e1:
            f = clamp01((T - e0) / max(1e-3, e1 - e0))
            tip = ("eraser", x - w / 2 + w * f, y + 40 * math.sin(T * 30))
    return tip


def camera(board, T):
    ep = board.ep
    j = ep.shot_at(T)
    s = ep.shots[j]
    t = T - s.t0
    cur = board.views[j]
    prev = board.views[j - 1] if j > 0 else (cur[0], cur[1] - 120, cur[2] * 1.12)
    k = ease_in_out(clamp01(t / 0.45)) if prev != cur else 1.0
    cx, cy = lerp(prev[0], cur[0], k), lerp(prev[1], cur[1], k)
    z = math.exp(lerp(math.log(prev[2]), math.log(cur[2]), k))
    z *= 1 + 0.015 * clamp01(t / max(0.1, s.t1 - s.t0))
    sx = sy = 0.0
    for it in s.shake:
        kb, amp = it if isinstance(it, tuple) else (it, 14.0)
        dt = T - core.bt(s.b0 + kb)
        if 0 <= dt < 0.3:
            a = amp * math.exp(-dt * 14)
            sx += a * math.sin(dt * 90)
            sy += a * math.cos(dt * 77)
    return cx, cy, z, sx, sy


def hand(c, x, y, eraser=False):
    """简笔手 + 马克笔（或白板擦），屏幕坐标，笔尖在 (x, y)。"""
    with K.at(c, x, y, -32):
        if eraser:
            K.rr(c, 0, 40, 180, 80, 14, "#3C5A8A")
            K.rr(c, 0, 0, 180, 18, 6, "#E8E2D2")
        else:
            K.rr(c, 0, 95, 30, 170, 10, "#2B2B33")
            K.rr(c, 0, 12, 22, 34, 6, "#4A4A55")
            K.poly(c, [(-8, -4), (8, -4), (0, -16)], "#2B2B33")
            K.rr(c, 0, 172, 30, 28, 8, RED)
        hp = skia.Path()
        hp.addRoundRect(skia.Rect.MakeXYWH(-46, 70, 120, 150), 50, 50)
        c.drawPath(hp, K.paint("#F3D2B5"))
        c.drawPath(hp, K.paint("#8A6A55", 1, 4))
        for jj in range(3):
            K.seg(c, -30 + jj * 22, 92, -30 + jj * 22, 128, "#8A6A55", 3)


def render_board(c, board, T, view=None, hand_on=True):
    """把白板画到屏幕：view=(cx, cy, z) 时用固定视角（封面用），否则按镜头相机。"""
    if view is None:
        cx, cy, z, sx, sy = camera(board, T)
    else:
        (cx, cy, z), sx, sy = view, 0.0, 0.0
    c.save()
    c.translate(core.W / 2 + sx, STAGE_Y + sy)
    c.scale(z, z)
    c.translate(-cx, -cy)
    _board_bg(c, board)
    tip = _items(c, board, T)
    c.restore()
    if hand_on and z > 0.5:
        eraser = isinstance(tip, tuple) and len(tip) == 3
        if eraser:
            tip = tip[1:]
        if tip is None:
            board_last = getattr(board, "_last_tip", None)
            tip = board_last or (cx + 300, cy + 300)
            idle = True
        else:
            board._last_tip = tip
            idle = False
        hx, hy = (tip[0] - cx) * z + core.W / 2 + sx, (tip[1] - cy) * z + STAGE_Y + sy
        hand(c, hx, hy + (18 if idle else 0), eraser)


def draw_frame(c, ep, T, caption=True, ui=True):
    board = ep.board
    k = ep.shot_at(T)
    s = ep.shots[k]
    g = core.G(c, ep, s, T - s.t0)
    render_board(c, board, T)
    for it in s.flashes:
        kb, pk = it if isinstance(it, tuple) else (it, 0.45)
        from adler import fx
        a = fx.flash_alpha(g.since(kb), pk)
        if a > 0:
            c.drawPaint(K.paint("#FFFFFF", a))
    if caption:
        head = core._cap_head(ep, s)
        if head.text:
            c.drawRect(skia.Rect.MakeLTRB(0, CAP_TOP, core.W, CAP_BOTTOM), K.paint("#FFFFFF", 0.82, blur=8))
            core.draw_caption(c, ep, s, g)
    if ui:
        c.drawRect(skia.Rect.MakeLTRB(0, 140, core.W, 320), K.paint("#FFFFFF", 0.78, blur=10))
        core.draw_header(c, ep, s, T, g)
        core.draw_progress(c, ep, T)
    fin = 1 - clamp01(T / 0.4)
    fout = clamp01((T - (core.END - 1.2)) / 1.1)
    if fin > 0 or fout > 0:
        c.drawPaint(K.paint("#FBFBF9", max(fin, fout)))


def cover(ep, path: str):
    """竖版封面：取封面镜头末尾的白板画面（无手、无字幕），下方大标题。"""
    board = ep.board
    s = ep.shots[ep.cover_shot]
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    c = surf.getCanvas()
    T = s.t1 - 0.05
    vx, vy, vz = board.views[ep.cover_shot]
    vz *= 1.12
    c.save()
    c.translate(0, 80)
    render_board(c, board, T, view=(vx, vy, vz), hand_on=False)
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(0, 1240, core.W, core.H), K.paint("#FBFBF9"))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, core.W, 330), K.paint("#FBFBF9"))
    K.rr(c, 72 + 70, 230, 140, 70, 35, ep.accent)
    K.text(c, f"{ep.no:02d}", 72 + 70, 230, 46, "black", K.PAPER)
    K.text(c, core.SERIES["name"], 72 + 160, 230, 40, "sans_medium", K.INK2, 1, "left")
    lines = ep.cover_title.split("|")
    widest = max(K.text_w(gfx.plain(ln), 104, "hand") for ln in lines)
    size = min(110.0, 110 * 920 / widest)
    for i, ln in enumerate(lines):
        y = 1450 + (i - (len(lines) - 1) / 2) * size * 1.35
        gfx.draw_rich(c, ln, core.W / 2, y, size, "hand", BLACK, RED, 1.0)
    if ep.cover_sub:
        K.text(c, ep.cover_sub, core.W / 2, 1450 + len(lines) * 75 + 70, 44, "sans_medium", K.INK2)
    surf.makeImageSnapshot().save(path, skia.kPNG)


def install(B=None):
    """切换到白板引擎（只影响当前进程）：逐帧绘制、封面与单讲横屏封面都改由白板画面生成。"""
    core.draw_frame = draw_frame
    core.cover = cover

    def board_shot(c, ep, k, t):
        """单讲横屏封面取景：该镜头末尾的白板画面（无手）。"""
        board = ep.board
        T = ep.shots[k].t0 + t
        vx, vy, vz = board.views[k]
        render_board(c, board, T, view=(vx, vy, vz), hand_on=False)
        return core.G(c, ep, ep.shots[k], t)

    if B is not None:
        orig = B.episode_square

        def episode_square(k, path):
            saved = core._draw_shot
            core._draw_shot = board_shot
            try:
                return orig(k, path)
            finally:
                core._draw_shot = saved

        B.episode_square = episode_square
