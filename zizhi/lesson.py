"""《资治通鉴》白板手绘系列公共模块：复用丰田的 Lesson（fengtian/common.py），换上本系列的文案、系列名，
再加古人 / 今人造型、古风道具和分镜常用的拍点小工具。

分镜模块写法同丰田（见 zizhi/ep01_caide.py）：

    from zizhi import lesson as Z
    from zizhi.lesson import BLACK, RED, ...
    SCREENS = [([], "开场", 0), ([0, 1], "打工人日常", 1), ...]
    L = Z.Lesson("01", SCREENS, drop_screen=2, theme=ZT.get("01"))
    ...
    L.finish(cover_shot=…, square_shot=…, notes=NOTES)
    L.export(globals())

人物区分：
- 今人：小李 draw_li（黑线小人 + 头发 + 领带）、小王 draw_wang（短发 + 橙发卡、白衬衫）、“能人”同事 draw_ace（灰西装、尖头发、得意脸）、
  领导 draw_boss（深色西装）。都在办公室，不戴安全帽。
- 古人 draw_gu：长袍到脚、交领、宽袖、腰带，束发戴冠（guan）/ 发髻（bun）/ 幞头（futou，宋人司马光），长者有胡子；
  每个古人一种袍色。古人出场的屏用竹简框、卷轴或城池背景，和今人的办公室分开。
"""

import math
from contextlib import contextmanager

import skia

from adler import core
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, pop_scale,  # noqa: F401
                             rest_hands, slam_scale)
from whiteboard import engine as wb
from whiteboard.engine import P, check, circle, cross, join, rect  # noqa: F401
from zizhi import hooks as _hooks  # noqa: F401  注册开场钩子
from zizhi import plan

core.SERIES.update(name="资治通鉴", count="第一季", prefix="资治通鉴")

GRAY, GRAY_FILL = "#8A8F99", "#D9DCE1"
RED_FILL, GREEN_FILL, BLUE_FILL, NOTE_FILL = "#F6C3BE", "#D3EDDC", "#D5E3F7", "#FFF1A8"
INK = "#2B2622"
BAMBOO, BAMBOO_LINE = "#E9D49A", "#9C7A3A"
SKIN = "#FFFFFF"
WATER, WATER_LINE = "#BFD9EE", "#3F7FB8"
WALL, WALL_LINE = "#D8C7A6", "#7A5E3A"
HAIR = "#2E2A28"
_PUN = "，。：？！、；【】"


# ================================================================ 一讲

class Lesson(C.Lesson):
    """丰田 Lesson + 本系列文案（zizhi/PLAN.md）+ 拍点小工具。"""

    PLAN = plan

    def wp(self, li, pi, frac=0.0):
        """第 li 句第 pi 段字幕念到 frac（0–1）处的本地秒（按字的位置换算）。"""
        pieces = self.LINES[li][1]
        n0 = sum(len([ch for ch in p_ if ch not in _PUN]) for p_ in pieces[:pi])
        n = len([ch for ch in pieces[pi] if ch not in _PUN])
        return self.char_time(li, min(n0 + int(frac * n), n0 + n - 1)) if frac < 1 else self.char_time(li, n0 + n - 1) + 0.2

    def nbeats(self, j):
        return self.BOUNDS[j][1] - self.BOUNDS[j][0]

    def kq(self, j, t_local, lo=0):
        return self.kb(j, t_local, lo=min(lo, self.nbeats(j) - 1))

    def klast(self, j, tail=0.35):
        """本屏最后一个能放画面事件的拍：事件做完（tail 秒）后到切屏至少还停 1.6 秒。"""
        b0, b1 = self.BOUNDS[j]
        return max(k for k in range(b1 - b0) if core.bt(b0 + k) + tail <= core.bt(b1) - 1.6)

    def cap(self, j, k, tail=0.35):
        return min(k, self.klast(j, tail))

    def nx(self, j, t_local, prev, gap=1):
        """离 t_local 最近、且至少在 prev 之后 gap 拍的拍号（不超过本屏最后可用拍）。"""
        return self.cap(j, max(self.kq(j, t_local, prev + gap), prev + gap))

    def ev(self, j, k, fn, sfx=None, gain=0.8, dur=0.3):
        self.b.custom(j, k, k + dur, fn, sfx=sfx, gain=gain)

    def pop_fn(self, j, k, draw, dur=0.32):
        """第 j 屏第 k 拍弹出：draw(c, 缩放, T)。"""
        def fn(c, kk, T):
            sc = pop_scale(T - self.tb(j, k), dur)
            if sc > 0:
                draw(c, sc, T)
            return None
        return fn

    def stamp_ev(self, j, k, s, x, y, size, rot=-6.0, sfx="kick", gain=0.85, color=RED):
        self.ev(j, k, self.stamp(s, x, y, size, j, k, color=color, rot=rot), sfx, gain)

    def seal_ev(self, j, k, s, x, y, size=70, sfx="kick", gain=0.8, rot=-4.0):
        """朱红方印（白字），第 j 屏第 k 拍盖下。"""
        self.note(s)

        def fn(c, kk, T):
            dt = T - self.tb(j, k)
            sc = slam_scale(dt)
            if sc <= 0:
                return None
            seal(c, x, y, s, size, rot, sc, clamp01(dt / 0.06))
            return None
        self.ev(j, k, fn, sfx, gain)


# ================================================================ 小工具

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


def head_of(x, y, s):
    return x, y - 290 * s


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


def bubble_box(c, x, y, w, h, tail=-1, alpha=1.0, fill="#FFFFFF"):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 40, 40, K.paint(fill, alpha))
    c.drawPath(wb.bubble(x, y, w, h, tail), wb.marker(BLACK, 7, alpha))


def seal(c, x, y, s, size=70, rot=-4.0, sc=1.0, a=1.0):
    """朱红方印：红底白字，一到两个字一行。"""
    n = len(s)
    rows = [s] if n <= 3 else [s[: (n + 1) // 2], s[(n + 1) // 2:]]
    w = max(len(r_) for r_ in rows) * size * 1.02 + size * 0.5
    h = len(rows) * size * 1.08 + size * 0.42
    with K.at(c, x, y, rot, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), size * 0.12, size * 0.12, K.paint(RED, a))
        c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 7, -h / 2 + 7, w - 14, h - 14), size * 0.08, size * 0.08,
                        wb.marker("#FFFFFF", 3, 0.8 * a))
        for i, r_ in enumerate(rows):
            K.text(c, r_, 0, (i - (len(rows) - 1) / 2) * size * 1.08 + 2, size, "serif_black", "#FFFFFF", a)


def doc_card(c, x, y, w=200, h=250, color=BLACK, rows=4, fill="#FFFFFF", rot=0.0):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, fill, color, 6, 8)
        for r in range(rows):
            yy = -h / 2 + 45 + r * (h - 80) / max(1, rows - 1)
            C.line(c, (-w / 2 + 26, yy), (w / 2 - 26 - (r % 2) * 36, yy), GRAY, 5)


# ================================================================ 今人

WANG_SHIRT = "#FFFFFF"
ACE_SUIT, ACE_LINE = "#B9BEC8", "#4A5160"


def draw_wang(c, x, y, s, lh=None, rh=None, mood="flat", head_dx=0.0, alpha=1.0):
    """同事小王（办公室）：齐耳短发 + 橙色发卡、白衬衫蓝描边、蓝工牌、蓝色四肢。(x, y) 为脚底，身高约 330·s。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for foot in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, foot, BLUE, 10, alpha)
    C.line(c, sh, lh, BLUE, 10, alpha)
    C.line(c, sh, rh, BLUE, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 42 * s, hy + 55 * s, x + 42 * s, y - 105 * s)
    c.drawRoundRect(torso, 18 * s, 18 * s, K.paint(WANG_SHIRT, alpha))
    c.drawRoundRect(torso, 18 * s, 18 * s, wb.marker(BLUE, 7, alpha))
    c.drawPath(P((x - 16 * s, hy + 58 * s), (x, hy + 82 * s), (x + 16 * s, hy + 58 * s)), wb.marker(BLUE, 5, alpha))
    badge = skia.Rect.MakeXYWH(x - 20 * s, hy + 110 * s, 40 * s, 30 * s)
    c.drawRoundRect(badge, 4, 4, K.paint("#DCE8F7", alpha))
    c.drawRoundRect(badge, 4, 4, wb.marker(BLUE, 4, alpha))
    hx = x + head_dx
    back = skia.Rect.MakeLTRB(hx - 54 * s, hy - 46 * s, hx + 54 * s, hy + 40 * s)
    c.drawRoundRect(back, 26 * s, 26 * s, K.paint(HAIR, alpha))
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(hx - 50 * s, hy - 52 * s, 100 * s, 72 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint(HAIR, alpha))
    c.drawCircle(hx + 36 * s, hy - 24 * s, 9 * s, K.paint(ORANGE, alpha))
    C._eyes_mouth(c, hx, hy + 4 * s, s, mood, alpha)


def draw_ace(c, x, y, s, lh=None, rh=None, mood="smug", head_dx=0.0, alpha=1.0, chin=0.0):
    """“能人”同事（办公室）：灰西装、尖头发、挑眉得意脸；mood: smug / laugh / flat / cold。chin>0 抬下巴。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s - chin * 6 * s
    sh = (x, y - 290 * s + 80 * s)
    hip = (x, y - 120 * s)
    for foot in ((x - 48 * s, y), (x + 48 * s, y)):
        C.line(c, hip, foot, ACE_LINE, 11, alpha)
    C.line(c, sh, lh, ACE_LINE, 11, alpha)
    C.line(c, sh, rh, ACE_LINE, 11, alpha)
    top = y - 290 * s + 56 * s
    torso = P((x - 48 * s, top), (x + 48 * s, top), (x + 44 * s, y - 100 * s), (x - 44 * s, y - 100 * s), close=True)
    c.drawPath(torso, K.paint(ACE_SUIT, alpha))
    c.drawPath(torso, wb.marker(ACE_LINE, 6, alpha))
    c.drawPath(P((x - 20 * s, top), (x, top + 56 * s), (x + 20 * s, top), close=True), K.paint("#FFFFFF", alpha))
    c.drawPath(P((x, top + 6 * s), (x - 8 * s, top + 40 * s), (x, top + 60 * s), (x + 8 * s, top + 40 * s), close=True),
               K.paint(ORANGE, alpha))
    hx = x + head_dx
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    spikes = P((hx - 46 * s, hy - 12 * s), (hx - 40 * s, hy - 62 * s), (hx - 18 * s, hy - 44 * s), (hx - 2 * s, hy - 78 * s),
               (hx + 14 * s, hy - 46 * s), (hx + 38 * s, hy - 70 * s), (hx + 46 * s, hy - 12 * s), (hx, hy - 30 * s), close=True)
    c.drawPath(spikes, K.paint(HAIR, alpha))
    if mood == "cold":
        for dx in (-15, 15):
            C.line(c, (hx + dx * s - 8 * s, hy - 4 * s), (hx + dx * s + 8 * s, hy - 4 * s), BLACK, 6, alpha)
        C.line(c, (hx - 14 * s, hy + 22 * s), (hx + 14 * s, hy + 22 * s), BLACK, 6, alpha)
        return
    for dx in (-15, 15):
        c.drawCircle(hx + dx * s, hy - 2 * s, 4 * s, K.paint(BLACK, alpha))
    C.line(c, (hx + 4 * s, hy - 22 * s), (hx + 26 * s, hy - 28 * s), BLACK, 5, alpha)        # 挑眉
    if mood == "laugh":
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(hx - 20 * s, hy + 2 * s, 40 * s, 30 * s), 0, 180)
        m.close()
        c.drawPath(m, K.paint(BLACK, alpha))
    elif mood == "smug":
        c.drawPath(P((hx - 16 * s, hy + 20 * s), (hx + 4 * s, hy + 24 * s), (hx + 18 * s, hy + 14 * s)), wb.marker(BLACK, 6, alpha))
    else:
        C.line(c, (hx - 14 * s, hy + 20 * s), (hx + 14 * s, hy + 20 * s), BLACK, 6, alpha)


def desk(c, x, y, w=420, h=24, laptop=True, alpha=1.0):
    """办公桌（桌面在 y）+ 笔记本电脑。"""
    box(c, x, y, w, h, "#E7D6BA", "#8B6B43", 6, 6, alpha)
    for sg in (-1, 1):
        C.line(c, (x + sg * (w / 2 - 26), y + h / 2), (x + sg * (w / 2 - 26), y + 170), "#8B6B43", 8, alpha)
    if laptop:
        sc = P((x - 90, y - h / 2), (x - 70, y - 120), (x + 70, y - 120), (x + 90, y - h / 2), close=True)
        c.drawPath(sc, K.paint("#E9EEF4", alpha))
        c.drawPath(sc, wb.marker(BLACK, 6, alpha))


# ================================================================ 古人

def draw_gu(c, x, y, s, robe="#E3D3EC", line="#6B3F7A", hat="guan", beard=None, mood="flat", lh=None, rh=None,
            head_dx=0.0, alpha=1.0, belt=None, bow=False):
    """古人：长袍到脚、交领、宽袖、腰带，束发戴冠。(x, y) 为脚底，身高约 330·s。
    hat：guan（发髻 + 小冠 + 簪）/ bun（只束发髻）/ futou（宋代幞头，两翅平伸）/ helmet（武将盔）；
    beard：None / "black" / "white"；mood：flat / smile / sad / o / laugh / angry；
    lh / rh：左右手位置（宽袖跟着走）；bow=True 拱手（两手合在胸前）。"""
    d_lh, d_rh = rest_hands(x, y, s)
    hy = y - 290 * s
    sh_l, sh_r = (x - 34 * s, hy + 74 * s), (x + 34 * s, hy + 74 * s)
    if bow:
        lh = rh = (x, hy + 150 * s)
    lh, rh = lh or (d_lh[0] + 6 * s, d_lh[1] - 10 * s), rh or (d_rh[0] - 6 * s, d_rh[1] - 10 * s)
    belt = belt or line
    # 鞋
    for dx in (-26, 26):
        c.drawOval(skia.Rect.MakeXYWH(x + dx * s - 22 * s, y - 14 * s, 44 * s, 18 * s), K.paint(INK, alpha))
    # 袍身：肩到脚，下摆外扩
    body = P((x - 40 * s, hy + 56 * s), (x + 40 * s, hy + 56 * s), (x + 66 * s, y - 8 * s), (x - 66 * s, y - 8 * s), close=True)
    c.drawPath(body, K.paint(robe, alpha))
    c.drawPath(body, wb.marker(line, 7, alpha))
    # 交领（右衽：左襟压右襟）
    c.drawPath(P((x - 24 * s, hy + 56 * s), (x + 14 * s, hy + 130 * s)), wb.marker(line, 6, alpha))
    c.drawPath(P((x + 24 * s, hy + 56 * s), (x + 4 * s, hy + 92 * s)), wb.marker(line, 6, alpha))
    C.line(c, (x + 14 * s, hy + 130 * s), (x + 30 * s, y - 14 * s), line, 4, alpha)
    # 腰带
    c.drawRect(skia.Rect.MakeLTRB(x - 48 * s, hy + 150 * s, x + 48 * s, hy + 168 * s), K.paint(belt, alpha))
    # 宽袖：肩 → 手，袖口宽
    for sh, hd in ((sh_l, lh), (sh_r, rh)):
        dx, dy = hd[0] - sh[0], hd[1] - sh[1]
        d = math.hypot(dx, dy) or 1.0
        nx_, ny_ = -dy / d, dx / d
        w0, w1 = 18 * s, 34 * s
        sl = P((sh[0] + nx_ * w0, sh[1] + ny_ * w0), (hd[0] + nx_ * w1, hd[1] + ny_ * w1),
               (hd[0] - nx_ * w1, hd[1] - ny_ * w1), (sh[0] - nx_ * w0, sh[1] - ny_ * w0), close=True)
        c.drawPath(sl, K.paint(robe, alpha))
        c.drawPath(sl, wb.marker(line, 6, alpha))
        c.drawCircle(hd[0] + dx / d * 10 * s, hd[1] + dy / d * 10 * s, 11 * s, K.paint("#FFFFFF", alpha))
        c.drawCircle(hd[0] + dx / d * 10 * s, hd[1] + dy / d * 10 * s, 11 * s, wb.marker(BLACK, 4, alpha))
    # 头
    hx = x + head_dx
    c.drawCircle(hx, hy, 45 * s, K.paint(SKIN, alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    hair = skia.Path()
    hair.addArc(skia.Rect.MakeXYWH(hx - 47 * s, hy - 48 * s, 94 * s, 64 * s), 180, 180)
    hair.close()
    if hat != "helmet":
        c.drawPath(hair, K.paint(HAIR, alpha))
    if hat in ("guan", "bun"):
        c.drawCircle(hx, hy - 58 * s, 18 * s, K.paint(HAIR, alpha))
        if hat == "guan":
            cap = P((hx - 20 * s, hy - 52 * s), (hx - 16 * s, hy - 92 * s), (hx + 16 * s, hy - 92 * s), (hx + 20 * s, hy - 52 * s),
                    close=True)
            c.drawPath(cap, K.paint(line, alpha))
            C.line(c, (hx - 40 * s, hy - 74 * s), (hx + 40 * s, hy - 74 * s), "#C9A34A", 5, alpha)
    elif hat == "lady":                       # 女子：高髻 + 发簪 + 两鬓垂发
        c.drawOval(skia.Rect.MakeXYWH(hx - 30 * s, hy - 100 * s, 60 * s, 56 * s), K.paint(HAIR, alpha))
        C.line(c, (hx - 50 * s, hy - 80 * s), (hx + 50 * s, hy - 66 * s), "#C9A34A", 5, alpha)
        c.drawCircle(hx + 50 * s, hy - 66 * s, 8 * s, K.paint(RED, alpha))
        for sg in (-1, 1):
            c.drawRoundRect(skia.Rect.MakeXYWH(hx + sg * 40 * s - 10 * s, hy - 20 * s, 20 * s, 70 * s), 10 * s, 10 * s,
                            K.paint(HAIR, alpha))
    elif hat == "futou":
        cap = skia.Path()
        cap.addRoundRect(skia.Rect.MakeXYWH(hx - 40 * s, hy - 84 * s, 80 * s, 50 * s), 16 * s, 16 * s)
        c.drawPath(cap, K.paint(INK, alpha))
        for sg in (-1, 1):
            C.line(c, (hx + sg * 36 * s, hy - 56 * s), (hx + sg * 120 * s, hy - 60 * s), INK, 7, alpha)
    elif hat == "helmet":
        dome = skia.Path()
        dome.addArc(skia.Rect.MakeXYWH(hx - 52 * s, hy - 70 * s, 104 * s, 96 * s), 180, 180)
        dome.close()
        c.drawPath(dome, K.paint("#9AA3AD", alpha))
        c.drawPath(dome, wb.marker(BLACK, 6, alpha))
        C.line(c, (hx, hy - 70 * s), (hx, hy - 100 * s), RED, 8, alpha)
    # 脸
    _face(c, hx, hy, s, mood, alpha)
    if beard:
        bc = "#F2F2F2" if beard == "white" else INK
        bp = P((hx - 26 * s, hy + 24 * s), (hx, hy + 92 * s), (hx + 26 * s, hy + 24 * s), (hx, hy + 38 * s), close=True)
        c.drawPath(bp, K.paint(bc, alpha))
        c.drawPath(bp, wb.marker(GRAY if beard == "white" else INK, 4, alpha))


def _face(c, hx, hy, s, mood, alpha):
    if mood == "angry":
        for sg in (-1, 1):
            C.line(c, (hx + sg * 26 * s, hy - 18 * s), (hx + sg * 6 * s, hy - 10 * s), BLACK, 5, alpha)
    for dx in (-15, 15):
        c.drawCircle(hx + dx * s, hy - 2 * s, 4 * s, K.paint(BLACK, alpha))
    if mood == "laugh":
        m = skia.Path()
        m.addArc(skia.Rect.MakeXYWH(hx - 20 * s, hy + 4 * s, 40 * s, 28 * s), 0, 180)
        m.close()
        c.drawPath(m, K.paint(BLACK, alpha))
    elif mood in ("smile", "sad", "o"):
        if mood == "smile":
            m = skia.Path()
            m.addArc(skia.Rect.MakeXYWH(hx - 16 * s, hy + 4 * s, 32 * s, 22 * s), 20, 140)
            c.drawPath(m, wb.marker(BLACK, 5, alpha))
        elif mood == "sad":
            m = skia.Path()
            m.addArc(skia.Rect.MakeXYWH(hx - 14 * s, hy + 16 * s, 28 * s, 16 * s), 200, 140)
            c.drawPath(m, wb.marker(BLACK, 5, alpha))
        else:
            c.drawCircle(hx, hy + 22 * s, 7 * s, wb.marker(BLACK, 4, alpha))
    else:
        C.line(c, (hx - 12 * s, hy + 20 * s), (hx + 12 * s, hy + 20 * s), BLACK, 5, alpha)


# 本系列常用的古人配色（袍色, 线色）
ROBES = dict(purple=("#E6D6EE", "#6B3F7A"), green=("#D6E8D0", "#3F6B3A"), blue=("#D4E1F2", "#2F5B8E"),
             ochre=("#F0DDB8", "#8A5A1E"), red=("#F4CFC8", "#9C2F25"), gray=("#E2E2DE", "#5E5E58"),
             brown=("#E3D2BE", "#5E4128"), teal=("#CFE6E3", "#2C6E68"))


def gu(c, x, y, s, color="purple", **kw):
    robe, line = ROBES[color]
    draw_gu(c, x, y, s, robe, line, **kw)


# ================================================================ 古风道具

def bamboo_slips(c, x, y, w, h, n=None, alpha=1.0, rope=True, fill=BAMBOO, line=BAMBOO_LINE):
    """一卷展开的竹简：(x, y) 中心，n 根竹片（默认按宽度），上下两道编绳。"""
    n = n or max(4, int(w / 70))
    sw = w / n
    for i in range(n):
        r = skia.Rect.MakeXYWH(x - w / 2 + i * sw + 3, y - h / 2, sw - 6, h)
        c.drawRoundRect(r, 8, 8, K.paint(fill, alpha))
        c.drawRoundRect(r, 8, 8, wb.marker(line, 4, alpha))
    if rope:
        for yy in (y - h * 0.36, y + h * 0.36):
            C.line(c, (x - w / 2 - 10, yy), (x + w / 2 + 10, yy), "#6E4E22", 5, alpha)


def slip_text(c, x, y, s, size, color=INK, alpha=1.0, gap=1.08):
    """竖排文字（从上往下），(x, y) 为第一个字中心。"""
    for i, ch in enumerate(s):
        K.text(c, ch, x, y + i * size * gap, size, "serif_black", color, alpha)


def scroll(c, x, y, w, h, open_=1.0, fill="#F7EFD9", line="#8A6A3A", alpha=1.0):
    """横向卷轴：open_ 0–1 从中间向两边展开；(x, y) 中心。返回内容区 (左, 上, 右, 下)。"""
    ww = max(30.0, w * open_)
    r = skia.Rect.MakeXYWH(x - ww / 2, y - h / 2, ww, h)
    c.drawRect(r, K.paint(fill, alpha))
    c.drawRect(r, wb.marker(line, 5, alpha))
    for sg in (-1, 1):
        rx = x + sg * ww / 2
        c.drawRoundRect(skia.Rect.MakeXYWH(rx - 14, y - h / 2 - 26, 28, h + 52), 12, 12, K.paint("#8A5A2E", alpha))
        c.drawRoundRect(skia.Rect.MakeXYWH(rx - 14, y - h / 2 - 26, 28, h + 52), 12, 12, wb.marker(INK, 4, alpha))
    return x - ww / 2 + 30, y - h / 2 + 20, x + ww / 2 - 30, y + h / 2 - 20


def city_wall(c, x, y, w, h, alpha=1.0, label=None, fill=WALL, line=WALL_LINE):
    """城墙（正视）：(x, y) 为墙脚中点；带垛口和城门。"""
    top = y - h
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.lineTo(x - w / 2, top)
    n = max(3, int(w / 80))
    mw = w / (2 * n + 1)
    xx = x - w / 2
    for i in range(n):
        p.lineTo(xx + mw, top)
        p.lineTo(xx + mw, top - 34)
        p.lineTo(xx + 2 * mw, top - 34)
        p.lineTo(xx + 2 * mw, top)
        xx += 2 * mw
    p.lineTo(x + w / 2, top)
    p.lineTo(x + w / 2, y)
    p.close()
    c.drawPath(p, K.paint(fill, alpha))
    c.drawPath(p, wb.marker(line, 7, alpha))
    gate = skia.Path()
    gw, gh = min(140, w * 0.22), min(170, h * 0.55)
    gate.moveTo(x - gw / 2, y)
    gate.lineTo(x - gw / 2, y - gh + gw / 2)
    gate.arcTo(skia.Rect.MakeXYWH(x - gw / 2, y - gh, gw, gw), 180, 180, False)
    gate.lineTo(x + gw / 2, y)
    c.drawPath(gate, K.paint("#5E4128", alpha))
    for r in range(1, 4):
        yy = y - h * r / 4
        C.line(c, (x - w / 2 + 10, yy), (x + w / 2 - 10, yy), line, 2, 0.5 * alpha)
    if label:
        box(c, x, top + 60, K.text_w(label, 54, "serif_black") + 40, 74, "#F7EFD9", line, 5, 6, alpha)
        K.text(c, label, x, top + 62, 54, "serif_black", INK, alpha)


def water(c, x0, x1, level, bottom, T, alpha=0.85, amp=10.0):
    """水面（波浪）从 level 到 bottom 填满。"""
    p = skia.Path()
    p.moveTo(x0, bottom)
    n = 40
    for i in range(n + 1):
        u = i / n
        xx = lerp(x0, x1, u)
        p.lineTo(xx, level + amp * math.sin(u * 18 + T * 4))
    p.lineTo(x1, bottom)
    p.close()
    c.drawPath(p, K.paint(WATER, alpha))
    c.drawPath(p, wb.marker(WATER_LINE, 6, alpha))


def cup(c, x, y, s=1.0, alpha=1.0, line=INK):
    """酒爵（简笔）：(x, y) 为杯脚底。"""
    with K.at(c, x, y, 0, s):
        bowl = P((-34, -80), (34, -80), (24, -36), (-24, -36), close=True)
        c.drawPath(bowl, K.paint("#E6C27A", alpha))
        c.drawPath(bowl, wb.marker(line, 5, alpha))
        for dx in (-18, 0, 18):
            C.line(c, (dx * 0.6, -36), (dx, 0), line, 5, alpha)


def flag(c, x, y, s, ch, color=RED, alpha=1.0, wave=0.0):
    """旗杆 + 方旗（一个字）：(x, y) 杆脚。"""
    with K.at(c, x, y, 0, s):
        C.line(c, (0, 0), (0, -300), "#6E4E22", 8, alpha)
        p = P((0, -296), (150, -290 + 6 * wave), (150 + 4 * wave, -170), (0, -176), close=True)
        c.drawPath(p, K.paint(color, alpha))
        c.drawPath(p, wb.marker(INK, 5, alpha))
        K.text(c, ch, 75, -234, 80, "serif_black", "#FFFFFF", alpha)
