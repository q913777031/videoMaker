"""《丰田模式》06 目视化：事情一多，为什么总有漏掉的？（白板手绘 + AI 旁白，竖屏 2:3）

两人对比：同样一天十几件事，左格小李全记在脑子里、翻聊天记录，右格小王在桌边贴一块三栏小白板。
全片用“左右两格分屏”（像视频通话的两个窗口，每格顶上一块名牌）对照两个人，讲丰田时插入车间画线、取货卡片、头顶的灯。
2026-11 结构：先问题（痛点 + 身边的例子），再书中做法，再办法，最后鼓励。
- 开场钩子 → 痛点：“周五交”的便利贴被吹走，“又忘了”，组长来催；
- 身边的例子：周五问进度（drop：第 2 屏聊天记录滚成长条，“翻了半天”砸下，重击 + 震屏 + 闪白）、取件码截图、
  药吃没吃 → 脑子当仓库；
- 两格分屏（屏 6/7 共用一块画面）：左格脑袋里塞满小方块、手机聊天一路往上翻；右格小王贴三栏白板，组长路过看一眼；
- 书中做法：“目视化管理”印章；组长沿流水线走过去，头顶一只眼睛，绿灯正常、红灯异常；地面黄线框、最高线；
  取货卡片 / 头顶的灯 / 整齐的工具三块牌，问题红点浮在外面；
- 为什么摆出来：红点钻进脑袋和电脑，没了，“没人管”；
- 两格分屏再来一次（结果）：左格方块往外掉，“漏”；右格一张卡片变红，小王举手，组长赶来；
- 怕作秀 → 三步 → 安心 → 评论区 + 下一讲预告。
办公室里的小王用本模块的 draw_wang（短发、白衬衫、蓝工牌，不戴安全帽）；安全帽造型（common.draw_worker）只用于车间员工。
文案见 fengtian/PLAN.md「### 06 目视化」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_leader, draw_li, draw_worker,
                             pop_scale, rest_hands, wobble)
from whiteboard import engine as wb
from whiteboard.engine import P, arrow, check, circle, cross, join, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "身边的例子", 8),
    ([4], "身边的例子", 9),
    ([5], "身边的例子", 10),
    ([6], "身边的例子", 11),
    ([7, 8], "两个人 · 小李", 2),
    ([9, 10], "两个人 · 小王", 2),
    ([11, 12], "丰田模式 · 书中做法", 3),
    ([13], "丰田模式 · 书中做法", 4),
    ([14], "丰田模式 · 书中做法", 5),
    ([15, 16, 17], "为什么摆出来", 6),
    ([18, 19], "两个人 · 结果", 7),
    ([20, 21], "说回我们自己", 12),
    ([22], "做法一 · 示意", 13),
    ([23], "做法二 · 示意", 14),
    ([24], "做法三 · 示意", 15),
    ([25, 26], "安心", 16),
    ([27, 28, 29, 30], "评论区见", 17),
]

THEME = FT.get("06")          # 本讲样式（fengtian/theme.py）：墨绿黑板、开场 sticky、转场 arc
L = C.Lesson("06", SCREENS, drop_screen=2, board_size=(5000, 13000), extra_hold={3: 0.5, 15: 0.8, 16: 1.0}, theme=THEME)
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

# 各白板区块中心（相邻区块相距 1600，按新屏序蛇形排列：区块 8–11 的身边例子排在 1 之后）
R = [(2600, 800), (900, 900), (2500, 4100), (900, 4100), (900, 5700), (2500, 5700), (4100, 5700), (4100, 7300),
     (900, 2500), (2500, 2500), (4100, 2500), (4100, 4100), (2500, 7300), (900, 7300), (900, 8900), (2500, 8900),
     (4100, 8900), (4100, 10500)]
SCR = [0, 1, 8, 9, 10, 11, 2, 2, 3, 4, 5, 6, 7, 12, 13, 14, 15, 16, 17]      # 屏 → 区块
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 7——通过可视化管理使问题无所隐藏（Use Visual Control So No Problems Are Hidden）；"
    "好的目视管理让人走过去看一眼就知道正常还是异常；5S（整理整顿等）、看板、安灯；把信息藏在电脑里会让问题看不见。",
    "地面画线、最高堆放线为车间通用做法的示意；小李、小王、组长、领导为虚构人物，三栏白板、取件码等为示意。",
]


def nbeats(j):
    return L.BOUNDS[j][1] - L.BOUNDS[j][0]


def kq(j, t_local, lo=0):
    """kb，但 lo 超出本屏时夹到最后一拍（防止排期变短时报错）。"""
    return kb(j, t_local, lo=min(lo, nbeats(j) - 1))


def center(j):
    return R[SCR[j]]


# ================================================================ 小工具

def pop_fn(j, k, draw, dur=0.32):
    """第 j 屏第 k 拍弹出：draw(c, sc, T)。"""
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k), dur)
        if sc > 0:
            draw(c, sc, T)
        return None
    return fn


@contextmanager
def at_pop(c, x, y, sc, rot=0.0):
    c.save()
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    c.scale(sc, sc)
    c.translate(-x, -y)
    try:
        yield
    finally:
        c.restore()


def label(j, k0, s, x, y, size=64, color=BLACK, sfx=None):
    b.text(j, k0, k0 + 0.1 + 0.12 * len(s), s, x, y, size, color, sfx=sfx)


def is_int(k):
    return abs(k - round(k)) < 1e-9


# ================================================================ 办公室里的小王（不戴安全帽）

WANG_SHIRT = "#FFFFFF"
HAIR = "#2E2A28"


def draw_wang(c, x, y, s, lh=None, rh=None, mood="flat", head_dx=0.0, alpha=1.0):
    """同事小王（办公室）：齐耳短发 + 橙色发卡、白衬衫蓝描边、蓝工牌、蓝色四肢（手臂画在衬衫后面）。(x, y) 为脚底，身高约 330·s。
    车间员工仍用 common.draw_worker（黄安全帽 + 蓝工服）。"""
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
    back = skia.Rect.MakeLTRB(hx - 54 * s, hy - 46 * s, hx + 54 * s, hy + 40 * s)       # 后面的短发
    c.drawRoundRect(back, 26 * s, 26 * s, K.paint(HAIR, alpha))
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(hx - 50 * s, hy - 52 * s, 100 * s, 72 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint(HAIR, alpha))
    c.drawCircle(hx + 36 * s, hy - 24 * s, 9 * s, K.paint(ORANGE, alpha))
    C._eyes_mouth(c, hx, hy + 4 * s, s, mood, alpha)


# ================================================================ 道具

NOTE_FILL, NOTE_LINE = "#FFE58A", "#C99A12"
RED_FILL, GREEN_FILL, BLUE_FILL = "#F6C3BE", "#DCEFD9", "#E4EDFA"
GRAY = "#9AA0AC"
TINT_L, TINT_R = "#F4ECEA", "#EAF3EA"


def sticky(c, x, y, s=1.0, txt="", fill=NOTE_FILL, line=NOTE_LINE, rot=0.0, alpha=1.0, size=None, flip=1.0, tcolor=BLACK):
    """便利贴：(x, y) 为中心，边长 130·s；flip 为水平翻转系数（-1–1，翻面时为背面灰黄）。"""
    w = 130 * s
    with K.at(c, x, y, rot, 1.0):
        c.scale(max(0.04, abs(flip)), 1.0)
        r = skia.Rect.MakeXYWH(-w / 2, -w / 2, w, w)
        c.drawRect(r, K.paint(fill if flip >= 0 else "#E8CF77", alpha))
        c.drawRect(r, wb.marker(line, 4, alpha))
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -w / 2, w, w * 0.16), K.paint(line, 0.25 * alpha))
        if txt and flip >= 0:
            K.text(c, txt, 0, w * 0.06, size or 40 * s, "hand", tcolor, alpha)


def board3(c, x, y, w, h, heads=(1, 1, 1), alpha=1.0, hl=None):
    """三栏小白板：(x, y) 为中心；heads 为三栏表头显现比例（0–1，弹出缩放）；hl=栏号时该栏淡黄高亮。返回三栏中心 x。"""
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(r, 14, 14, K.paint("#FFFFFF", alpha))
    cw = w / 3
    xs = [x - w / 2 + cw * (i + 0.5) for i in range(3)]
    if hl is not None:
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + cw * hl + 4, y - h / 2 + 4, cw - 8, h - 8), K.paint("#FFF4C2", alpha))
    c.drawRoundRect(r, 14, 14, wb.marker("#5A6170", 8, alpha))
    for i in (1, 2):
        xx = x - w / 2 + cw * i
        c.drawLine(xx, y - h / 2 + 10, xx, y + h / 2 - 10, wb.marker(GRAY, 4, alpha))
    hy = y - h / 2 + h * 0.13
    c.drawLine(x - w / 2 + 10, hy + h * 0.09, x + w / 2 - 10, hy + h * 0.09, wb.marker(GRAY, 3, alpha))
    for i, (xx, t) in enumerate(zip(xs, COLS)):
        sc = heads[i]
        if sc > 0:
            with K.at(c, xx, hy, 0, sc):
                K.text(c, t, 0, 0, min(56, cw * 0.3), "hand", COL_C[i], alpha)
    return xs


COLS = ["要做", "在做", "做完"]
COL_C = [BLACK, ORANGE, GREEN]


def cloud(c, x, y, r, alpha=1.0, fill="#FFFFFF", line_c=BLACK, tail=None):
    """想法云：(x, y) 为中心，半径约 r；tail=(x, y) 为小圆点尾巴指向的头顶。"""
    pts = [(-0.55, -0.3, 0.55), (0.0, -0.5, 0.6), (0.55, -0.3, 0.55), (0.6, 0.25, 0.5), (0.05, 0.42, 0.6),
           (-0.55, 0.25, 0.5)]
    for dx, dy, rr in pts:
        c.drawCircle(x + dx * r, y + dy * r, rr * r, wb.marker(line_c, 7, alpha))
    for dx, dy, rr in pts:
        c.drawCircle(x + dx * r, y + dy * r, rr * r - 3, K.paint(fill, alpha))
    if tail:
        tx, ty = tail
        for i, f in enumerate((0.35, 0.65)):
            px, py = lerp(x, tx, 0.55 + f * 0.4), lerp(y + r * 0.7, ty, 0.55 + f * 0.4)
            rr = r * (0.12 - i * 0.04)
            c.drawCircle(px, py, rr, K.paint(fill, alpha))
            c.drawCircle(px, py, rr, wb.marker(line_c, 5, alpha))


BLOCK_C = ["#BFD5F2", "#F6C3BE", "#DCEFD9", "#FFE58A", "#E6DDC4", "#D9CFF0"]


def blocks_in(c, x, y, r, n, alpha=1.0, drop=None, T=0.0):
    """云里塞小方块：n 个，按网格往外挤；drop=[(i, t0)] 时第 i 块从 t0 起往下掉出去。"""
    pos = []
    for i in range(14):
        row, col = divmod(i, 4)
        jx = ((i * 37) % 11 - 5) * 3
        jy = ((i * 53) % 9 - 4) * 3
        pos.append((x - r * 0.62 + col * r * 0.41 + jx + (row % 2) * r * 0.1, y - r * 0.42 + row * r * 0.3 + jy))
    falls = dict(drop or [])
    for i in range(min(n, len(pos))):
        px, py = pos[i]
        rot = ((i * 29) % 21 - 10)
        a = alpha
        if i in falls and T >= falls[i]:
            dt = T - falls[i]
            py += 900 * dt * dt + 60 * dt
            px += (i % 3 - 1) * 90 * dt
            rot += 300 * dt
            a *= 1 - clamp01((dt - 0.5) / 0.3)
            if a <= 0:
                continue
        with K.at(c, px, py, rot, 1.0):
            sz = r * 0.3
            c.drawRoundRect(skia.Rect.MakeXYWH(-sz / 2, -sz / 2, sz, sz), 6, 6, K.paint(BLOCK_C[i % len(BLOCK_C)], a))
            c.drawRoundRect(skia.Rect.MakeXYWH(-sz / 2, -sz / 2, sz, sz), 6, 6, wb.marker(BLACK, 4, a))


def chat_phone(c, x, y, s=1.0, scroll=0.0, alpha=1.0, n=40):
    """手机聊天记录：(x, y) 为中心，宽 150·s；scroll 为往上翻过的条数（可为小数）。"""
    w, h = 150 * s, 260 * s
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(r, 22 * s, 22 * s, K.paint("#FFFFFF", alpha))
    scr = skia.Rect.MakeXYWH(x - w / 2 + 12 * s, y - h / 2 + 26 * s, w - 24 * s, h - 52 * s)
    c.drawRect(scr, K.paint("#EEF2F6", alpha))
    c.save()
    c.clipRect(scr)
    step = 38 * s
    off = (scroll % 1.0) * step
    base = int(scroll)
    for i in range(-1, 8):
        idx = base + i
        yy = scr.bottom() - 18 * s - i * step + off - step
        left = (idx * 7) % 3 != 0
        bw = (50 + (idx * 23) % 50) * s
        bx = scr.left() + 10 * s if left else scr.right() - 10 * s - bw
        c.drawRoundRect(skia.Rect.MakeXYWH(bx, yy - 12 * s, bw, 24 * s), 10 * s, 10 * s,
                        K.paint("#FFFFFF" if left else "#BFE3C8", alpha))
    c.restore()
    c.drawRoundRect(r, 22 * s, 22 * s, wb.marker(BLACK, 7, alpha))
    c.drawCircle(x, y + h / 2 - 13 * s, 5 * s, K.paint(BLACK, alpha))


def monitor(c, x, y, w=330, h=230, alpha=1.0, glow=None):
    """电脑屏幕：(x, y) 为屏幕中心。"""
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(r, 14, 14, K.paint("#DCE8F7" if glow is None else glow, alpha))
    c.drawRoundRect(r, 14, 14, wb.marker(BLACK, 8, alpha))
    c.drawPath(P((x - 30, y + h / 2), (x - 45, y + h / 2 + 60), (x + 45, y + h / 2 + 60), (x + 30, y + h / 2)),
               wb.marker(BLACK, 7, alpha))
    c.drawLine(x - 90, y + h / 2 + 60, x + 90, y + h / 2 + 60, wb.marker(BLACK, 8, alpha))


def lamp(c, x, y, on, color, alpha=1.0, blink=1.0, r=34, pole=120):
    """安灯灯头：(x, y) 为灯中心；on 为 0–1 亮度；pole 为灯杆长。"""
    c.drawLine(x, y + r, x, y + r + pole, wb.marker(BLACK, 6, alpha))
    if on > 0:
        c.drawCircle(x, y, r * 2.0, K.paint(color, 0.25 * on * blink * alpha, blur=18))
    c.drawCircle(x, y, r, K.paint(K.mix("#FFFFFF", color, 0.15 + 0.85 * on * blink) if on > 0 else "#EEEEEE", alpha))
    c.drawCircle(x, y, r, wb.marker(BLACK, 6, alpha))


def eye(c, x, y, s=1.0, alpha=1.0, look=0.0, slash=False):
    """一只眼睛：(x, y) 为中心，宽 140·s；look 为眼珠左右偏移 -1–1。"""
    w, h = 70 * s, 42 * s
    p = skia.Path()
    p.moveTo(x - w, y)
    p.quadTo(x, y - h * 1.6, x + w, y)
    p.quadTo(x, y + h * 1.6, x - w, y)
    p.close()
    c.drawPath(p, K.paint("#FFFFFF", alpha))
    c.save()
    c.clipPath(p, doAntiAlias=True)
    c.drawCircle(x + look * w * 0.45, y, h * 0.9, K.paint(BLUE, alpha))
    c.drawCircle(x + look * w * 0.45, y, h * 0.42, K.paint(BLACK, alpha))
    c.restore()
    c.drawPath(p, wb.marker(BLACK, 7, alpha))
    if slash:
        c.drawLine(x - w * 0.9, y + h * 1.3, x + w * 0.9, y - h * 1.3, wb.marker(RED, 10, alpha))


def red_dot(c, x, y, sc=1.0, alpha=1.0, tagged=False):
    """问题小红点（带“!”）。"""
    c.drawCircle(x, y, 30 * sc, K.paint(RED, alpha))
    c.drawCircle(x, y, 30 * sc, wb.marker("#8E0B1F", 4, alpha))
    K.text(c, "!", x, y, 46 * sc, "black", "#FFFFFF", alpha)


def big_head(c, x, y, r, alpha=1.0, mood="flat", face_on=True, fill="#FFFFFF"):
    """小李的大头像（胸像）：(x, y) 为头中心，半径 r；头发一道粗弧 + 一撮，脖子、肩膀、领带。"""
    c.drawPath(P((x - r * 1.05, y + r * 1.75), (x - r * 0.55, y + r * 1.12), (x + r * 0.55, y + r * 1.12),
                 (x + r * 1.05, y + r * 1.75)), wb.marker(BLACK, 10, alpha))
    c.drawPath(P((x, y + r * 1.0), (x - r * 0.1, y + r * 1.35), (x, y + r * 1.7), (x + r * 0.1, y + r * 1.35), close=True),
               K.paint(BLACK, alpha))
    c.drawCircle(x, y, r, K.paint(fill, alpha))
    c.drawCircle(x, y, r, wb.marker(BLACK, 10, alpha))
    hair = skia.Path()
    hair.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 195, 150)
    c.drawPath(hair, wb.marker(BLACK, 22, alpha))
    if face_on:
        for dx in (-0.35, 0.35):
            c.drawCircle(x + dx * r, y + r * 0.2, r * 0.07, K.paint(BLACK, alpha))
        if mood == "smile":
            m = skia.Path()
            m.addArc(skia.Rect.MakeXYWH(x - r * 0.3, y + r * 0.3, r * 0.6, r * 0.35), 20, 140)
            c.drawPath(m, wb.marker(BLACK, 8, alpha))
        else:
            c.drawLine(x - r * 0.2, y + r * 0.55, x + r * 0.2, y + r * 0.55, wb.marker(BLACK, 8, alpha))


def crate(c, x, yb, w=120, h=90, fill="#E6CFA8", alpha=1.0):
    """零件箱（正视）：(x, yb) 为底边中点。"""
    r = skia.Rect.MakeXYWH(x - w / 2, yb - h, w, h)
    c.drawRect(r, K.paint(fill, alpha))
    c.drawRect(r, wb.marker("#8A6A3E", 5, alpha))
    c.drawLine(x - w / 2 + 12, yb - h * 0.55, x + w / 2 - 12, yb - h * 0.55, wb.marker("#8A6A3E", 3, alpha))


def bubble_txt(c, s, x, y, size=60, color=BLACK, tail=-1, alpha=1.0, w=None, h=None):
    w = w or K.text_w(s, size, "hand") + 80
    h = h or size + 60
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 40, 40, K.paint("#FFFFFF", alpha))
    c.drawPath(wb.bubble(x, y, w, h, tail), wb.marker(BLACK, 7, alpha))
    K.text(c, s, x, y, size, "hand", color, alpha)


# ---------------------------------------------------------------- 两格分屏（本讲的固定版式）

PANEL_W, PANEL_H = 568, 960
PANEL_TOP = -440


def panels_xy(j):
    cx, cy = center(j)
    return cx - 296, cx + 296, cy + PANEL_TOP, cy + PANEL_TOP + PANEL_H


def panel_rect(j, side):
    lx, rx, y0, y1 = panels_xy(j)
    x = lx if side == 0 else rx
    return skia.Rect.MakeLTRB(x - PANEL_W / 2, y0, x + PANEL_W / 2, y1)


def split_frame(j, k0=0):
    """两格分屏：左格（小李，淡红底）、右格（小王，淡绿底），各一块名牌。名牌在 k0、k0+1 拍弹出。"""
    lx, rx, y0, y1 = panels_xy(j)

    def bg(c, kk, T):
        for side, tint in ((0, TINT_L), (1, TINT_R)):
            a = clamp01((T - tb(j, k0 + 0.5 * side)) / 0.4)
            if a > 0:
                c.drawRoundRect(panel_rect(j, side), 26, 26, K.paint(tint, a))
        return None
    b.custom(j, k0, k0 + 0.1, bg)
    for side in (0, 1):
        b.path(j, k0 + 0.5 * side, k0 + 0.5 * side + 0.5, rect((lx, rx)[side], (y0 + y1) / 2, PANEL_W, PANEL_H, 26),
               (BLACK, BLUE)[side], 7, sfx="wood_high" if side == 0 else None, gain=0.6)
    L.note("小李", "小王")
    for side, (name, color, k_) in enumerate((("小李", BLACK, k0 + 1), ("小王", BLUE, k0 + 2))):
        x = (lx, rx)[side]

        def tab(c, sc, T, x=x, name=name, color=color, side=side):
            with at_pop(c, x, y0, sc):
                r = skia.Rect.MakeXYWH(x - 105, y0 - 40, 210, 80)
                c.drawRoundRect(r, 40, 40, K.paint("#FFFFFF"))
                c.drawRoundRect(r, 40, 40, wb.marker(color, 7))
                c.drawCircle(x - 62, y0, 14, K.paint(RED if side == 0 else GREEN))
                K.text(c, name, x + 18, y0, 54, "hand", color)
        b.custom(j, k_, k_ + 0.3, pop_fn(j, k_, tab), sfx="pop", gain=0.6)


def clip_panel(c, j, side):
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(panel_rect(j, side), 26, 26), doAntiAlias=True)


def walker(j, k0, beats, x0, x1, y, s, clip=None):
    """组长走路：第 j 屏第 k0 拍起用 beats 拍从 x0 走到 x1（clip=(屏, 格) 时裁在分屏格里）。"""
    def fn(c, kk, T):
        t0 = tb(j, k0)
        if T < t0:
            return None
        dur = tb(j, k0 + beats) - t0
        x, _, moving = C.walk(T, t0, dur, x0, x1)
        if clip:
            clip_panel(c, *clip)
        draw_leader(c, x, y, s, phase=((T - t0) * 1.6) % 1.0, run=0.55 if moving else 0.0)
        if clip:
            c.restore()
        return None
    return fn


def walker_x(j, k0, beats, x0, x1, T):
    t0 = tb(j, k0)
    return C.walk(T, t0, tb(j, k0 + beats) - t0, x0, x1)[0]


# ================================================================ 屏 0：系列开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：“周五交”的便利贴被吹走，“又忘了”；组长来催，小李才想起来
cx, cy = R[1]
j = L.scene(1, (cx, cy + 20, Z))
LI1 = (cx - 400, cy + 440, 0.9)
LD1 = (cx + 400, cy + 440, 0.9)
DESK1 = (cx - 60, cy + 250, 380)
MON1 = (DESK1[0] + 40, DESK1[1] - 60)
NOTE1 = (MON1[0] + 70, MON1[1] - 50)
b.path(j, 0, 0.7, wb.desk(*DESK1), BLACK, 9, sfx="wood_high")
b.custom(j, 0, 0.3, L.figure(draw_li, j, 0, *LI1,
                             mood=lambda T: "o" if T >= tb(1, k_up) else ("sad" if T >= tb(1, k_ask) else "flat"),
                             lh=lambda T: (LI1[0] - 70, LI1[1] - 290 * LI1[2] - 20) if T >= tb(1, k_up) else None,
                             rh=lambda T: (LI1[0] + 70, LI1[1] - 290 * LI1[2] - 20) if T >= tb(1, k_up) else
                             (LI1[0] + 120, LI1[1] - 290 * LI1[2] + 150)))
label(j, 0.4, "小李", LI1[0], LI1[1] + 85, 64)
k_note = 1
k_fly = kq(j, wt(0, 0, 0.75), lo=k_note + 1)
k_forget = kq(j, wt(0, 1, 0.6), lo=k_fly + 2)
k_ask = kq(j, wt(1, 0, 0.1), lo=k_forget + 1)
k_up = kq(j, wt(1, 1, 0.5), lo=k_ask + 1)
L.note("周五交")


def note1(c, kk, T):
    cx, cy = R[1]
    t_in, t_fly = tb(1, k_note), tb(1, k_fly)
    sc = pop_scale(T - t_in)
    if sc <= 0:
        return None
    if T < t_fly:
        rot = wobble(T - t_in, 8, 18, 5)
        with at_pop(c, *NOTE1, sc):
            sticky(c, *NOTE1, 1.0, "周五交", rot=-6 + rot, size=42)
        return None
    t_end = tb(1, k_fly + 2.5)
    f = clamp01((T - t_fly) / (t_end - t_fly))
    if f >= 1:
        return None
    x = lerp(NOTE1[0], cx + 760, f) + 60 * math.sin(f * 7)
    y = lerp(NOTE1[1], cy - 560, ease_in_out(f)) - 120 * math.sin(f * math.pi)
    bp = L.beat_pos(T) - L.beat_pos(t_fly)
    flip = math.cos(math.pi * bp)                                   # 每拍翻一面
    sticky(c, x, y, 1.0, "周五交", rot=-6 + 50 * f, size=42, flip=flip)
    return None


b.custom(j, k_note, k_note + 0.3, note1, sfx="pop", gain=0.7)
for i in range(3):
    b.hit(j, k_fly + i, ("shaker", "wood_high", "shaker")[i], 0.5, "便利贴翻着飘走")


def wind1(c, kk, T):
    cx, cy = R[1]
    t0 = tb(1, k_fly)
    a = clamp01((T - t0) / 0.2) * (1 - clamp01((T - t0 - 1.2) / 0.5))
    if a <= 0:
        return None
    for i, yy in enumerate((cy + 40, cy - 30, cy + 110)):
        d = ((T - t0) * 700 + i * 120) % 500
        x0 = cx - 300 + d
        c.drawPath(P((x0, yy), (x0 + 120, yy - 10), (x0 + 200, yy + 10)), wb.marker(GRAY, 6, a * 0.8))
    return None


b.custom(j, k_fly, k_fly + 0.1, wind1)
b.custom(j, k_forget, k_forget + 0.3, L.stamp("又忘了", cx - 60, cy - 400, 120, j, k_forget), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_forget, 12.0)]
b.custom(j, k_ask, k_ask + 0.3, L.figure(draw_leader, j, k_ask, *LD1), sfx="pop", gain=0.6)
label(j, k_ask + 0.4, "组长", LD1[0], LD1[1] + 85, 64, RED)
b.custom(j, k_ask, k_ask + 0.3, L.pop_bubble("我那份呢？", cx + 270, cy - 110, j, k_ask, size=66, tail=1))
b.custom(j, k_up, k_up + 0.3, L.slam_text("！", LI1[0] + 100, LI1[1] - 360, 130, RED, j, k_up, font="black"), sfx="rim", gain=0.8)

# ================================================================ 屏 2（drop）：周五领导问“进度呢？”；小李手机聊天记录滚成长条，drop 时“翻了半天”
cx, cy = R[8]
j = L.scene(2, (cx, cy + 20, Z))
LI9 = (cx - 400, cy + 440, 0.9)
BO9 = (cx + 400, cy + 440, 0.9)
CAL9 = (cx - 380, cy - 400)
k_bo9 = kq(j, wt(2, 1, 0.2), lo=2)
k_fri = kq(j, wt(3, 0, 0.25), lo=k_bo9 + 1)
k_q9 = kq(j, wt(3, 0, 0.75), lo=k_fri + 1)
KD2 = L.drop_k()                                      # drop：“翻了半天”砸下
k_scr = min(kq(j, wt(3, 1, 0.2), lo=k_q9 + 1), KD2 - 2)
k_fan9 = KD2
b.shots[j].shake, b.shots[j].flashes = [(KD2, 16.0)], [(KD2, 0.45)]


def cal9(c, sc, T):
    x, y = CAL9
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - 110, y - 100, 220, 210)
        c.drawRoundRect(r, 16, 16, K.paint("#FFFFFF"))
        c.drawRect(skia.Rect.MakeXYWH(x - 110, y - 100, 220, 60), K.paint(RED))
        c.drawRoundRect(r, 16, 16, wb.marker(BLACK, 7))
        K.text(c, "周五", x, y + 40, 76, "hand", BLACK)
        for dx in (-55, 55):
            c.drawLine(x + dx, y - 120, x + dx, y - 80, wb.marker(BLACK, 8))


L.note("周五")
b.custom(j, k_fri, k_fri + 0.3, pop_fn(j, k_fri, cal9), sfx="wood_high", gain=0.7)
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI9, mood=lambda T: "sad" if T >= tb(2, k_fan9) else "flat",
                             rh=lambda T: (LI9[0] + 110, LI9[1] - 290 * LI9[2] + 130)), sfx="pop", gain=0.6)
label(j, 1.4, "小李", LI9[0], LI9[1] + 85, 64)
b.custom(j, k_bo9, k_bo9 + 0.3, L.figure(draw_boss, j, k_bo9, *BO9,
                                         lh=lambda T: (BO9[0] - 120, BO9[1] - 290 * BO9[2] + 110) if T >= tb(2, k_q9) else None))
label(j, k_bo9 + 0.4, "领导", BO9[0], BO9[1] + 85, 64, C.BOSS_SUIT)
b.custom(j, k_q9, k_q9 + 0.3, L.pop_bubble("进度呢？", cx + 300, cy - 120, j, k_q9, size=70, tail=1), sfx="pop", gain=0.75)
STRIP9 = (cx - 120, cy - 520, cy + 330)


def strip9(c, kk, T):
    """手机里的聊天记录拉成一条长纸带：从手机往上展开，并一直往下滚。"""
    cx, cy = R[8]
    t0 = tb(2, k_scr)
    if T < t0:
        return None
    x, ytop, ybot = STRIP9
    g = ease_out(clamp01((T - t0) / 0.6))
    top = lerp(ybot - 60, ytop, g)
    w = 220
    r = skia.Rect.MakeLTRB(x - w / 2, top, x + w / 2, ybot)
    c.drawRoundRect(r, 20, 20, K.paint("#EEF2F6"))
    c.save()
    c.clipRect(r)
    scroll = (T - t0) * 420
    step = 64
    i0 = int(scroll // step)
    for i in range(i0 - 2, i0 + int((ybot - ytop) / step) + 3):
        yy = top + (i * step - scroll) % (ybot - ytop + 2 * step) - step
        left = (i * 7) % 3 != 0
        bw = 90 + (i * 31) % 70
        bx = x - w / 2 + 14 if left else x + w / 2 - 14 - bw
        c.drawRoundRect(skia.Rect.MakeXYWH(bx, yy, bw, 40), 16, 16, K.paint("#FFFFFF" if left else "#BFE3C8"))
    c.restore()
    c.drawRoundRect(r, 20, 20, wb.marker(BLACK, 7))
    chat_phone(c, x, ybot + 80, 0.95, 0)
    if T >= tb(2, k_fan9):
        dt = T - tb(2, k_fan9)
        a = clamp01(dt / 0.08)
        with K.at(c, x - 300, cy - 120, -6, C.slam_scale(dt)):
            K.text(c, "翻了半天", 0, 0, 66, "hand", RED, a)
        c.drawPath(arrow((x - 150, cy - 260), (x - 150, cy - 30), 0, 26), wb.marker(RED, 7, a))
        c.drawPath(arrow((x - 150, cy - 30), (x - 150, cy - 260), 0, 26), wb.marker(RED, 7, a))
    return None


L.note("翻了半天")
b.custom(j, k_scr, k_scr + 0.3, strip9, sfx="wood_low", gain=0.7)
b.hit(j, k_scr + 1, "shaker", 0.55, "聊天记录一直滚")
b.hit(j, k_fan9, "kick", 0.95, "drop：翻了半天")

# ================================================================ 屏 3：取件码截了图，相册里几百张截图，找不到；快递柜
cx, cy = R[9]
j = L.scene(3, (cx, cy + 20, Z))
PH10 = (cx - 220, cy - 120)
LOCK10 = (cx + 320, cy - 60)
LI10 = (cx - 420, cy + 450, 0.8)
k_shot = kq(j, wt(4, 1, 0.3), lo=1)
k_find = k_shot + 1
k_nf = kq(j, wt(4, 2, 0.8), lo=k_find + 2)


def lockers(c, sc, T):
    x, y = LOCK10
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - 170, y - 300, 340, 560)
        c.drawRoundRect(r, 12, 12, K.paint("#E9EEF4"))
        c.drawRoundRect(r, 12, 12, wb.marker(BLACK, 8))
        for row in range(5):
            for col in range(3):
                bx, by = x - 150 + col * 102, y - 280 + row * 106
                c.drawRoundRect(skia.Rect.MakeXYWH(bx, by, 92, 96), 6, 6, wb.marker("#5A6170", 4))
                c.drawCircle(bx + 76, by + 48, 5, K.paint("#5A6170"))
        c.drawRect(skia.Rect.MakeXYWH(x - 60, y + 270, 120, 30), K.paint(BLACK))
        K.text(c, "快递柜", x, y - 345, 56, "hand", BLACK)
        bl = 0.5 + 0.5 * math.cos(T * 6)
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 150 + 102, y - 280 + 2 * 106, 92, 96), 6, 6, wb.marker(ORANGE, 7, bl))


L.note("快递柜")
b.custom(j, 0, 0.3, pop_fn(j, 0, lockers), sfx="wood_high", gain=0.7)


def gallery(c, kk, T):
    t0 = tb(3, k_shot)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = PH10
    w, h = 340, 560
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
        c.drawRoundRect(r, 30, 30, K.paint("#FFFFFF"))
        scr = skia.Rect.MakeXYWH(x - w / 2 + 18, y - h / 2 + 40, w - 36, h - 80)
        c.drawRect(scr, K.paint("#F3F5F8"))
        c.save()
        c.clipRect(scr)
        scroll = max(0.0, (min(T, tb(3, k_nf)) - tb(3, k_find))) * 900
        cell = (w - 36 - 16) / 3
        for i in range(60):
            row, col = divmod(i, 3)
            bx = scr.left() + 4 + col * (cell + 4)
            by = scr.top() + 4 + row * (cell + 4) - scroll % (cell * 12)
            if by > scr.bottom() or by + cell < scr.top():
                continue
            c.drawRect(skia.Rect.MakeXYWH(bx, by, cell, cell), K.paint(BLOCK_C[(i * 5) % len(BLOCK_C)]))
            c.drawLine(bx + 14, by + cell * 0.35, bx + cell - 14, by + cell * 0.35, wb.marker("#FFFFFF", 6))
            c.drawLine(bx + 14, by + cell * 0.6, bx + cell - 30, by + cell * 0.6, wb.marker("#FFFFFF", 6))
        c.restore()
        c.drawRoundRect(r, 30, 30, wb.marker(BLACK, 9))
        K.text(c, "截图 ×300", x, y - h / 2 - 50, 58, "sans_medium", BLACK)
    if T >= tb(3, k_find):
        g = T - tb(3, k_find)
        mx = x + 120 * math.sin(g * 4.5)
        my = y - 50 + 140 * math.sin(g * 2.7)
        c.drawCircle(mx, my, 62, K.paint("#FFFFFF", 0.35))
        c.drawCircle(mx, my, 62, wb.marker(BLACK, 9))
        c.drawLine(mx + 44, my + 44, mx + 100, my + 100, wb.marker(BLACK, 14))
    return None


L.note("截图 ×300")
b.custom(j, k_shot, k_shot + 0.3, gallery, sfx="pop", gain=0.7)
b.hit(j, k_find, "shaker", 0.55, "相册往下翻")
b.hit(j, k_find + 1, "wood_high", 0.5, "相册往下翻")
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI10, mood=lambda T: "sad" if T >= tb(3, k_nf) else "flat",
                             rh=lambda T: (LI10[0] + 120, LI10[1] - 290 * LI10[2] + 90)), sfx="pop", gain=0.55)
label(j, 1.4, "小李", LI10[0], LI10[1] + 80, 60)
b.custom(j, k_nf, k_nf + 0.3, L.stamp("没找到", cx - 30, cy + 300, 104, j, k_nf), sfx="kick", gain=0.8)
b.shots[j].shake = [(k_nf, 9.0)]

# ================================================================ 屏 4：抽屉里一盒药，吃没吃记不清；小李歪头
cx, cy = R[10]
j = L.scene(4, (cx, cy + 20, Z))
DR = (cx + 120, cy - 40)
LI11 = (cx - 380, cy + 450, 0.9)
k_box = kq(j, wt(5, 0, 0.6), lo=2)
k_eat = kq(j, wt(5, 1, 0.1), lo=k_box + 1)
k_q11 = kq(j, wt(5, 2, 0.4), lo=k_eat + 2)
WOOD = "#8A6A3E"
b.path(j, 0, 0.8, join(rect(DR[0], DR[1] + 180, 540, 380, 14), rect(DR[0], DR[1] + 270, 460, 130, 6),
                       P((DR[0] - 50, DR[1] + 270), (DR[0] + 50, DR[1] + 270))), WOOD, 9, sfx="wood_high")


def drawer11(c, kk, T):
    """上层抽屉拉开：抽屉面板往前（变宽、下移），露出里面，药盒立在抽屉里。"""
    x, y = DR
    g = ease_out(clamp01((T - tb(4, 1)) / 0.4))
    if g <= 0:
        c.drawRect(skia.Rect.MakeXYWH(x - 230, y + 20, 460, 120), K.paint("#F3E6CF"))
        c.drawRect(skia.Rect.MakeXYWH(x - 230, y + 20, 460, 120), wb.marker(WOOD, 7))
        return None
    fw = lerp(460, 540, g)
    ftop = lerp(y + 20, y + 90, g)
    inner = P((x - 230, y + 20), (x + 230, y + 20), (x + fw / 2, ftop), (x - fw / 2, ftop), close=True)
    c.drawPath(inner, K.paint("#6E5432"))
    sc = pop_scale(T - tb(4, k_box))
    if sc > 0:
        bx, by = x - 70, ftop - 45
        with at_pop(c, bx, by + 45, sc):
            rr_ = skia.Rect.MakeXYWH(bx - 85, by - 60, 170, 105)
            c.drawRoundRect(rr_, 10, 10, K.paint("#FFFFFF"))
            c.drawRoundRect(rr_, 10, 10, wb.marker(BLUE, 7))
            c.drawRect(skia.Rect.MakeXYWH(bx - 13, by - 42, 26, 64), K.paint(RED))
            c.drawRect(skia.Rect.MakeXYWH(bx - 32, by - 23, 64, 26), K.paint(RED))
        K.text(c, "药", bx + 170, y - 70, 64, "hand", BLUE, clamp01(sc))
    front = skia.Rect.MakeXYWH(x - fw / 2, ftop, fw, 135)
    c.drawRect(front, K.paint("#F3E6CF"))
    c.drawRect(front, wb.marker(WOOD, 8))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 55, ftop + 55, 110, 24), 12, 12, K.paint(WOOD))
    return None


L.note("药")
b.custom(j, 0.8, 0.9, drawer11)
b.hit(j, 1, "wood_low", 0.7, "拉开抽屉")
b.hit(j, k_box, "pop", 0.7, "一盒药")
PILL = (cx + 120, cy - 330)
DAYS = ["一", "二", "三", "四"]


def pills11(c, kk, T):
    t0 = tb(4, k_eat)
    if T < t0:
        return None
    x0, y = PILL
    for i, d in enumerate(DAYS):
        sc = pop_scale(T - t0 - i * 0.15, 0.25)
        if sc <= 0:
            continue
        x = x0 - 270 + i * 180
        with at_pop(c, x, y, sc):
            r = skia.Rect.MakeXYWH(x - 75, y - 70, 150, 150)
            c.drawRoundRect(r, 16, 16, K.paint("#FFFFFF"))
            c.drawRoundRect(r, 16, 16, wb.marker(BLACK, 6))
            K.text(c, d, x, y - 35, 46, "hand", "#5A6170")
            if i < 2:
                c.drawPath(check(x, y + 30, 30), wb.marker(GREEN, 9))
            else:
                K.text(c, "?", x, y + 32, 64, "black", RED)
    return None


L.note(*DAYS, "?")
b.custom(j, k_eat, k_eat + 0.3, pills11, sfx="wood_high", gain=0.6)
b.hit(j, k_eat + 1, "pop", 0.55, "格子里打问号")


def li11(c, kk, T):
    x, y, s = LI11
    sc = pop_scale(T - tb(4, 1))
    if sc <= 0:
        return None
    tilt = -10 * ease_out(clamp01((T - tb(4, k_q11)) / 0.3))
    hy = y - 290 * s
    scratch = T >= tb(4, k_q11)
    rh = (x + 32, hy + 58 + 4 * math.sin(T * 10)) if scratch else None
    with at_pop(c, x, y, sc, rot=tilt):
        draw_li(c, x, y, s, "o" if scratch else "flat", rh=rh)
    return None


b.custom(j, 1, 1.3, li11, sfx="pop", gain=0.55)
label(j, 1.4, "小李", LI11[0], LI11[1] + 85, 64)
b.custom(j, k_q11, k_q11 + 0.3, L.slam_text("？", LI11[0] + 150, LI11[1] - 400, 130, RED, j, k_q11), sfx="rim", gain=0.75)
b.custom(j, k_q11, k_q11 + 0.3, L.pop_text("记不清", cx + 160, cy + 440, 76, RED, j, k_q11))

# ================================================================ 屏 5：脑袋当仓库，箱子堆到屋顶，打叉；换成脑袋里一个灯泡
cx, cy = R[11]
j = L.scene(5, (cx, cy + 20, Z))
HD12 = (cx - 40, cy - 110, 290)
k_think = kq(j, wt(6, 0, 0.8), lo=1)
k_box12 = kq(j, wt(6, 1, 0.0), lo=k_think + 1)
k_x12 = kq(j, wt(6, 1, 0.75), lo=k_box12 + 2)
k_bulb = k_x12 + 1


def head12(c, kk, T):
    """小李的大头：先有想事的小齿轮；箱子堆满脑袋 → 红叉 → 箱子和叉一起掉出去，换成灯泡。"""
    x, y, r = HD12
    big_head(c, x, y, r, face_on=False)
    gone = ease_in_out(clamp01((T - tb(5, k_bulb)) / 0.45))
    sc = pop_scale(T - tb(5, k_think))
    if sc > 0 and gone < 1:
        with at_pop(c, x, y - 20, sc * (1 - gone)):
            c.drawCircle(x, y - 20, 60, wb.marker(BLUE, 9))
            for i in range(8):
                a = i * math.pi / 4 + T * 1.5
                c.drawLine(x + math.cos(a) * 60, y - 20 + math.sin(a) * 60, x + math.cos(a) * 82, y - 20 + math.sin(a) * 82,
                           wb.marker(BLUE, 12))
    t_b = tb(5, k_box12)
    if T >= t_b and gone < 1:
        n = min(9, int((T - t_b) / (tb(5, k_box12 + 2) - t_b) * 9) + 1)
        c.save()
        c.clipPath(C.circle(x, y, r - 10), doAntiAlias=True)
        for i in range(n):
            row, col = divmod(i, 3)
            bx = x - 145 + col * 145 + (row % 2) * 18
            by = y + r - 30 - row * 112 + 500 * gone * gone
            crate(c, bx, by, 135, 108, alpha=1 - gone)
        c.restore()
    if T >= tb(5, k_x12) and gone < 1:
        f = clamp01((T - tb(5, k_x12)) / 0.3)
        part, _ = wb.partial(cross(x, y, 200), f)
        c.drawPath(part, wb.marker(RED, 18, 1 - gone))
    bs = pop_scale(T - tb(5, k_bulb))
    if bs > 0:
        with at_pop(c, x, y - 20, bs):
            c.drawCircle(x, y - 40, 95, K.paint(YELLOW, 0.35, blur=24))
            c.drawPath(C.bulb_path(x, y - 50, 80), wb.marker(ORANGE, 10))
        K.text(c, "想事", x, y + 150, 72, "hand", ORANGE, clamp01((T - tb(5, k_bulb)) / 0.3))
    return None


L.note("想事")
b.path(j, 0, 0.8, C.circle(*HD12), BLACK, 10, sfx="wood_high")
b.custom(j, 0.8, 0.9, head12)
b.hit(j, k_think, "pop", 0.55, "脑子用来想事")
b.hit(j, k_box12, "wood_low", 0.65, "箱子堆进脑袋")
b.hit(j, k_box12 + 1, "wood_low", 0.6, "箱子堆到头顶")
WH12 = (cx + 400, cy - 450)


def ware12(c, sc, T):
    x, y = WH12
    with at_pop(c, x, y, sc):
        K.text(c, "仓库", x, y, 76, "hand", BLACK)
        f = clamp01((T - tb(5, k_x12)) / 0.25)
        if f > 0:
            c.drawLine(x - 90, y + 4, x - 90 + 180 * f, y + 4, wb.marker(RED, 10))


L.note("仓库")
b.custom(j, k_box12, k_box12 + 0.3, pop_fn(j, k_box12, ware12))
b.hit(j, k_x12, "kick", 0.8, "红叉")
b.shots[j].shake = [(k_x12, 9.0)]
b.hit(j, k_bulb, "ding", 0.8, "换成一个灯泡")

# ================================================================ 屏 6/7：两格分屏（同一块画面）——左格小李、右格小王
cx, cy = R[2]
j = L.scene(6, (cx, cy + 20, Z))
LX, RX, PY0, PY1 = panels_xy(6)
b.custom(j, 0, 0.3, L.pop_text("同样一天，十几件事", cx, cy - 545, 72, BLACK, j, 0), sfx="pop", gain=0.6)
split_frame(j, 1)
LI2 = (LX - 120, cy + 440, 0.8)
WG2 = (RX - 140, cy + 440, 0.8)
CL2 = (LX - 20, cy - 175, 200)
PH2 = (LX + 160, cy + 200)
k_li = max(kq(j, wt(7, 1, 0.5), lo=3), 3)
k_wang = k_li + 1
k_head = kq(j, wt(8, 0, 0.3), lo=k_wang + 1)
k_chat = kq(j, wt(8, 1, 0.1), lo=k_head + 2)
k_sore = kq(j, wt(8, 1, 0.8), lo=k_chat + 1)


def li2(c, kk, T):
    x, y, s = LI2
    sc = pop_scale(T - tb(6, k_li))
    if sc <= 0:
        return None
    hy = y - 290 * s
    on = T >= tb(6, k_chat)
    sw = 10 * math.sin((T - tb(6, k_chat)) * 14) if on and T < tb(7, 0) else 0.0
    rh = (PH2[0] - 60, PH2[1] + 40 + sw) if on else (x + 70 * s, y - 120 * s)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad" if T >= tb(6, k_sore) else "flat", rh=rh)
    return None


b.custom(j, k_li, k_li + 0.3, li2, sfx="pop", gain=0.6)
b.custom(j, k_wang, k_wang + 0.3, L.figure(draw_wang, j, k_wang, *WG2,
                                           mood="smile",
                                           rh=lambda T: rh3(T)), sfx="pop", gain=0.6)
N_HEAD = 12


def cloud2(c, kk, T):
    t0 = tb(6, k_head)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    n = min(N_HEAD, int((T - t0) / (tb(6, k_head + 2) - t0) * N_HEAD) + 1)
    x, y, r = CL2
    with at_pop(c, x, y, sc):
        cloud(c, x, y, r, tail=(LI2[0], LI2[1] - 290 * LI2[2] - 60))
        blocks_in(c, x, y, r, n)
        if n >= N_HEAD:
            K.text(c, "×12", x + r * 0.95, y - r * 0.85, 52, "sans_medium", RED)
    return None


L.note("×12")
b.custom(j, k_head, k_head + 0.3, cloud2, sfx="pop", gain=0.6)
b.hit(j, k_head + 1, "wood_high", 0.55, "方块塞满脑袋")
b.hit(j, k_head + 2, "wood_low", 0.55, "方块塞满脑袋")


def phone2(c, kk, T):
    t0 = tb(6, k_chat)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    scroll = max(0.0, (min(T, tb(7, 0)) - t0) * 6.0)
    with at_pop(c, *PH2, sc):
        chat_phone(c, *PH2, 1.05, scroll)
        if scroll > 0 and T < tb(7, 0):
            for i in range(2):
                yy = PH2[1] - 60 + i * 40
                c.drawPath(arrow((PH2[0] + 105, yy + 30), (PH2[0] + 105, yy - 30), 0, 14), wb.marker(GRAY, 5))
    return None


b.custom(j, k_chat, k_chat + 0.3, phone2, sfx="wood_high", gain=0.6)
b.hit(j, k_chat + 1, "shaker", 0.5, "聊天记录往上翻")


def sore2(c, sc, T):
    x, y = PH2[0] - 40, PH2[1] + 175
    with at_pop(c, x, y, sc):
        K.text(c, "手酸", x, y, 64, "hand", RED)
        for i, (dx, dy) in enumerate(((-90, -40), (95, -55))):
            dd = 6 * math.sin(T * 9 + i)
            drop_ = P((x + dx - 11, y + dy + dd), (x + dx, y + dy - 24 + dd), (x + dx + 11, y + dy + dd))
            c.drawCircle(x + dx, y + dy + 4 + dd, 11, K.paint("#BFD5F2"))
            c.drawPath(drop_, K.paint("#BFD5F2"))
            c.drawCircle(x + dx, y + dy + 4 + dd, 11, wb.marker(BLUE, 3))


L.note("手酸")
b.custom(j, k_sore, k_sore + 0.3, pop_fn(j, k_sore, sore2), sfx="rim", gain=0.7)

# ---------------------------------------------------------------- 屏 3：右格小王——贴三栏白板、贴便利贴；组长路过看一眼
j = L.scene(7, (cx, cy + 20, Z))
BD3 = (RX, cy - 165, 470, 360)
k_bd = kq(j, wt(9, 0, 0.5), lo=1)
k_h = [kq(j, wt(9, 0, 0.72), lo=k_bd + 1)]
k_h += [k_h[0] + 1, k_h[0] + 2]
k_walk = kq(j, wt(10, 0, 0.0), lo=k_h[2] + 1)
k_look = kq(j, wt(10, 0, 0.75), lo=k_walk + 2)
k_stuck3 = kq(j, wt(10, 1, 0.55), lo=k_look + 1)
LD3 = (RX + 330, RX + 140, cy + 440, 0.8)
# 三栏里的便利贴：(栏, 行)，在表头那拍随之贴上
NOTES3 = {0: [(0, 0), (0, 1), (0, 2)], 1: [(1, 0), (1, 1)], 2: [(2, 0), (2, 1)]}


def note_xy(xs, col, row, by, bh):
    return xs[col] + (row % 2) * 10 - 5, by - bh / 2 + bh * 0.36 + row * bh * 0.22


def rh3(T):
    """小王的右手：贴白板那几拍抬起来。"""
    x, y, s = WG2
    hy = y - 290 * s
    for k_ in [k_bd] + k_h:
        t = tb(7, k_)
        if t - 0.25 <= T < t + 0.35:
            return BD3[0] - 60 + 110 * (k_h.index(k_) if k_ in k_h else 0), BD3[1] + BD3[3] / 2 - 10
    return x + 70 * s, hy + 170 * s


def board3_fn(c, kk, T):
    x, y, w, h = BD3
    t0 = tb(7, k_bd)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    heads = [pop_scale(T - tb(7, k_)) for k_ in k_h]
    with at_pop(c, x, y, sc):
        xs = board3(c, x, y, w, h, heads)
        for col, k_ in enumerate(k_h):
            for i, (cc, row) in enumerate(NOTES3[col]):
                nsc = pop_scale(T - tb(7, k_) - 0.08 * i)
                if nsc <= 0:
                    continue
                nx, ny = note_xy(xs, cc, row, y, h)
                red = col == 1 and row == 0 and T >= tb(7, k_stuck3)
                bl = 0.6 + 0.4 * math.cos((T - tb(7, k_stuck3)) * 18) if red and T - tb(7, k_stuck3) < 0.8 else 1.0
                with at_pop(c, nx, ny, nsc):
                    sticky(c, nx, ny, 0.62, "", fill=(RED_FILL if red else (NOTE_FILL, "#FFD9A8", GREEN_FILL)[col]),
                           line=RED if red else NOTE_LINE, rot=((row * 17) % 9 - 4), alpha=bl)
                    c.drawLine(nx - 22, ny + 4, nx + 22, ny + 4, wb.marker(GRAY, 3))
                    c.drawLine(nx - 22, ny + 18, nx + 12, ny + 18, wb.marker(GRAY, 3))
        if T >= tb(7, k_stuck3):
            nx, ny = note_xy(xs, 1, 0, y, h)
            K.ripple(c, nx, ny, T - tb(7, k_stuck3), RED, 120, 7, 0.9, 0.6)
            c.drawCircle(nx, ny + 4, 56, wb.marker(RED, 8, clamp01((T - tb(7, k_stuck3)) / 0.3)))
    return None


L.note(*COLS)
b.custom(j, k_bd, k_bd + 0.3, board3_fn, sfx="wood_low", gain=0.75)
for k_ in k_h:
    b.hit(j, k_, "pop", 0.6, "表头 + 便利贴贴上")
b.custom(j, k_walk, k_walk + 0.3, walker(j, k_walk, 2, LD3[0], LD3[1], LD3[2], LD3[3], clip=(3, 1)), sfx="wood_low",
         gain=0.55)
b.hit(j, k_walk + 1, "wood_high", 0.45, "组长走过来")


def look3(c, kk, T):
    t0 = tb(7, k_look)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x = LD3[1]
    hy = LD3[2] - 290 * LD3[3]
    ex, ey = x - 20, hy - 120
    with at_pop(c, ex, ey, sc):
        eye(c, ex, ey, 0.75, look=-0.6)
    a = clamp01((T - t0) / 0.3)
    xs = [BD3[0] - BD3[2] / 3, BD3[0], BD3[0] + BD3[2] / 3]
    tx, ty = note_xy(xs, 1, 0, BD3[1], BD3[3])
    for i in range(4):
        f0, f1 = i / 4, i / 4 + 0.13
        p0 = (lerp(ex - 40, tx + 30, f0), lerp(ey - 20, ty + 40, f0))
        p1 = (lerp(ex - 40, tx + 30, f1), lerp(ey - 20, ty + 40, f1))
        c.drawLine(*p0, *p1, wb.marker(ORANGE, 6, a))
    return None


b.custom(j, k_look, k_look + 0.3, look3, sfx="ding", gain=0.6)
b.hit(j, k_stuck3, "rim", 0.75, "在做里一张卡住")

# ================================================================ 屏 8：“目视化管理”；组长沿流水线走过去看一眼：绿灯正常，念完时红灯亮“异常”
cx, cy = R[3]
j = L.scene(8, (cx, cy + 20, Z))
BELT4 = cy + 300
ST4 = [cx - 370, cx, cx + 370]
LAMP_Y = cy - 110
b.path(j, 0, 0.8, join(P((cx - 560, BELT4), (cx + 560, BELT4)), P((cx - 560, BELT4 + 36), (cx + 560, BELT4 + 36)),
                       *[circle(cx - 530 + i * 1060 / 10, BELT4 + 18, 13) for i in range(11)]), BLACK, 7, sfx="wood_high")


def parts4(c, kk, T):
    """流水线上的零件箱一直往右走。"""
    cx, cy = R[3]
    for i in range(6):
        x = cx - 600 + ((T * 70 + i * 220) % 1320)
        if cx - 560 < x < cx + 540:
            crate(c, x, BELT4 - 2, 80, 55)
    return None


b.custom(j, 0.8, 0.9, parts4)
WK4 = [(ST4[0] + 10, BELT4 - 60, 0.6), (ST4[2] - 30, BELT4 - 60, 0.6)]
for i, w_ in enumerate(WK4):
    kk_ = 1 + 0.5 * i
    b.custom(j, kk_, kk_ + 0.3, L.figure(draw_worker, j, kk_, *w_,
                                         lh=lambda T, w_=w_: (w_[0] - 60, w_[1] - 290 * w_[2] + 175 + 8 * math.sin(T * 9)),
                                         rh=lambda T, w_=w_: (w_[0] + 70, w_[1] - 290 * w_[2] + 165 - 8 * math.sin(T * 9))),
             sfx="pop" if i == 0 else None, gain=0.5)
label(j, 1.4, "员工", ST4[0] - 150, BELT4 - 160, 54, BLUE)


def lamps4(c, kk, T):
    cx, cy = R[3]
    for i, x in enumerate(ST4):
        on, bl = 0.0, 1.0
        if i < 2 and T >= tb(8, k_lamp0):
            on = 1.0
        if i == 2 and T >= tb(8, KD):
            on = 1.0
            bl = 0.65 + 0.35 * math.cos((T - tb(8, KD)) * 9)
        lamp(c, x + 130, LAMP_Y, on, LCOL[i], blink=bl, pole=BELT4 - LAMP_Y - 34)
    return None


LCOL = [GREEN, GREEN, RED]
b.custom(j, 2, 2.3, lamps4, sfx="wood_low", gain=0.55)
k_title4 = kq(j, wt(11, 1, 0.55), lo=3)
b.custom(j, k_title4, k_title4 + 0.3, L.stamp("目视化管理", cx, cy - 440, 108, j, k_title4, rot=-4), sfx="kick", gain=0.75)
k_walk4 = kq(j, wt(12, 2, 0.0), lo=k_title4 + 1)
k_lamp0 = kq(j, wt(12, 3, 0.1), lo=k_walk4 + 1)
KD = max(kq(j, wt(12, 3, 0.8), lo=k_lamp0 + 1), k_lamp0 + 1)   # “正不正常”念完，红灯亮
b.shots[j].shake = [(KD, 12.0)]
LD4 = (cx - 650, cx + 300, BELT4 + 150, 0.62)


def lead4(c, kk, T):
    t0 = tb(8, k_walk4)
    if T < t0:
        return None
    x0, x1, y, s = LD4
    dur = tb(8, KD) - t0
    x, _, moving = C.walk(T, t0, dur, x0, x1)
    draw_leader(c, x, y, s, phase=((T - t0) * 1.6) % 1.0, run=0.55 if moving else 0.0)
    hy = y - 290 * s
    eye(c, x, hy - 90, 0.6, look=0.8 if T >= tb(8, KD) else math.sin((T - t0) * 3.0))
    K.text(c, "组长", x - 120, hy + 10, 50, "hand", RED)
    return None


L.note("组长")
b.custom(j, k_walk4, k_walk4 + 0.3, lead4, sfx="wood_low", gain=0.5)
b.hit(j, k_lamp0, "ding", 0.7, "绿灯：正常")
b.hit(j, KD, "rim", 0.9, "红灯亮，异常")
b.custom(j, k_lamp0, k_lamp0 + 0.3, L.pop_text("正常", (ST4[0] + ST4[1]) / 2 + 130, LAMP_Y - 100, 64, GREEN, j, k_lamp0))
b.custom(j, KD, KD + 0.3, L.slam_text("异常", ST4[2] + 130, LAMP_Y - 100, 76, RED, j, KD))
b.custom(j, k_lamp0, k_lamp0 + 0.3, L.pop_text("一眼就知道", cx - 250, BELT4 + 230, 66, BLUE, j, k_lamp0))

# ================================================================ 屏 9：车间地上画线：黄线框里放箱子，墙上一条“最高”线
cx, cy = R[4]
j = L.scene(9, (cx, cy + 20, Z))
FLOOR = cy + 120
b.path(j, 0, 0.6, P((cx - 580, FLOOR), (cx + 580, FLOOR)), "#5A6170", 8, sfx="wood_high")
FR = [(cx - 300, 360), (cx + 170, 300)]          # 地面线框：中心 x、宽
BASE5 = FLOOR + 170                              # 箱子落地的底边


def frame_path(x, w):
    return P((x - w / 2 + 30, FLOOR + 60), (x + w / 2 - 30, FLOOR + 60), (x + w / 2 + 10, FLOOR + 230),
             (x - w / 2 - 10, FLOOR + 230), close=True)


k_line5 = kq(j, wt(13, 0, 0.45), lo=1)
for i, (x, w) in enumerate(FR):
    b.path(j, k_line5 + i, k_line5 + i + 0.6, frame_path(x, w), YELLOW, 14, sfx=("wood_high", "wood_low")[i], gain=0.7)
k_put = kq(j, wt(13, 1, 0.2), lo=k_line5 + 2)
k_high = kq(j, wt(13, 1, 0.75), lo=k_put + 1)
k_mark = kq(j, wt(13, 2, 0.3), lo=k_high + 1)
HI_Y = BASE5 - 3 * 88 - 30
CR5 = [(FR[0][0] - 70, 0), (FR[0][0] + 70, 0), (FR[0][0] - 70, 1), (FR[0][0] + 70, 1), (FR[0][0], 2)]


def crates5(c, kk, T):
    for i, (x, lvl) in enumerate(CR5):
        t0 = tb(9, k_put) + i * 0.12
        if T < t0 - 0.3:
            continue
        g = clamp01((T - (t0 - 0.3)) / 0.3)
        yb = BASE5 - lvl * 88
        crate(c, x, lerp(yb - 250, yb, g * g), 128, 88)
    return None


b.custom(j, max(0.0, k_put - 0.3), k_put, crates5)
b.hit(j, k_put, "wood_low", 0.75, "箱子落进线框")
b.custom(j, k_put, k_put + 0.3, L.pop_text("放这里", FR[0][0], FLOOR + 300, 58, ORANGE, j, k_put))
WK5 = (cx + 480, FLOOR + 250, 0.85)
k_carry = k_put + 1


def worker5(c, kk, T):
    x0, y, s = WK5
    sc = pop_scale(T - tb(9, 1))
    if sc <= 0:
        return None
    t0, t1 = tb(9, k_carry), tb(9, k_carry + 1)
    x, _, moving = C.walk(T, t0, t1 - t0, x0, FR[1][0] + 255)
    hy = y - 290 * s
    hold = T < t1
    lh = (x - 85 * s, hy + 140 * s) if hold else None
    rh = (x - 30 * s, hy + 130 * s) if hold else None
    with at_pop(c, x0, y, sc):
        draw_worker(c, x, y, s, lh=lh, rh=rh, mood="smile" if T >= t1 else "flat")
        if hold:
            crate(c, x - 60 * s, hy + 175 * s, 110, 80)
    if T >= t1:
        crate(c, FR[1][0], BASE5, 128, 88)
    return None


b.custom(j, 1, 1.3, worker5, sfx="pop", gain=0.55)
label(j, 1.4, "员工", WK5[0], WK5[1] + 70, 54, BLUE)
b.hit(j, k_carry + 1, "wood_low", 0.65, "员工把箱子放进框")


def hiline5(c, kk, T):
    cx, cy = R[4]
    t0 = tb(9, k_high)
    f = clamp01((T - t0) / 0.4)
    if f <= 0:
        return None
    x0, x1 = cx - 560, cx + 330
    xe = lerp(x0, x1, f)
    for xx in range(int(x0), int(xe), 44):
        c.drawLine(xx, HI_Y, min(xx + 26, xe), HI_Y, wb.marker(RED, 10))
    if f >= 1:
        K.text(c, "最高", x1 + 100, HI_Y, 66, "hand", RED)
    return None


L.note("最高")
b.custom(j, k_high, k_high + 0.4, hiline5, sfx="rim", gain=0.75)
b.custom(j, k_mark, k_mark + 0.3, L.stamp("都标出来", cx, cy - 400, 92, j, k_mark, color=GREEN, rot=-5), sfx="kick",
         gain=0.75)
b.shots[j].shake = [(k_mark, 8.0)]

# ================================================================ 屏 10：取货卡片、头顶的灯、整齐的工具三块牌；问题红点浮在外面
cx, cy = R[5]
j = L.scene(10, (cx, cy + 20, Z))
IX = [cx - 380, cx, cx + 380]
IY = cy - 150
k_i6 = [kq(j, wt(14, 0, 0.25), lo=1)]               # 2026-11 第 9 句改为“取货卡片、头顶的灯、摆整齐的工具”
k_i6 += [kq(j, wt(14, 0, 0.47), lo=k_i6[0] + 1)]
k_i6 += [kq(j, wt(14, 0, 0.70), lo=k_i6[1] + 1)]
k_out6 = kq(j, wt(14, 1, 0.55), lo=k_i6[2] + 1)
NAMES6 = ["取货卡片", "头顶的灯", "整齐的工具"]


def icon6(i):
    def draw(c, sc, T):
        x, y = IX[i], IY
        with at_pop(c, x, y, sc):
            r = skia.Rect.MakeXYWH(x - 150, y - 160, 300, 320)
            c.drawRoundRect(r, 22, 22, K.paint("#FFFFFF"))
            c.drawRoundRect(r, 22, 22, wb.marker(BLUE, 7))
            if i == 0:                                   # 取货卡片
                card = skia.Rect.MakeXYWH(x - 70, y - 120, 140, 180)
                c.drawRect(card, K.paint("#FFF4C2"))
                c.drawRect(card, wb.marker(BLACK, 5))
                c.drawCircle(x, y - 105, 9, wb.marker(BLACK, 4))
                for k_ in range(3):
                    c.drawLine(x - 45, y - 60 + k_ * 34, x + 45 - (k_ % 2) * 25, y - 60 + k_ * 34, wb.marker(GRAY, 4))
                c.drawPath(C.box_path(x, y + 50, 70, 40), wb.marker(BLACK, 5))
            elif i == 1:                                 # 头顶的灯
                tw = T - tb(10, k_i6[1])
                lamp(c, x, y - 70, 1.0, RED, blink=0.7 + 0.3 * math.cos(tw * 8), r=40)
                c.drawPath(P((x + 60, y - 120), (x + 60, y + 20)), wb.marker(BLACK, 4))
                c.drawCircle(x + 60, y + 30, 10, K.paint(ORANGE))
            else:                                        # 整齐的工具：工具墙，每件工具有画好的轮廓
                for k_, (dx, tw_) in enumerate(((-75, 0), (0, 1), (75, 2))):
                    xx = x + dx
                    c.drawRoundRect(skia.Rect.MakeXYWH(xx - 30, y - 120, 60, 170), 10, 10, wb.marker(GRAY, 3))
                    if tw_ == 0:
                        c.drawLine(xx, y - 105, xx, y + 30, wb.marker(BLACK, 9))
                        c.drawRect(skia.Rect.MakeXYWH(xx - 22, y - 115, 44, 34), K.paint("#5A6170"))
                    elif tw_ == 1:
                        c.drawLine(xx, y - 80, xx, y + 35, wb.marker(BLACK, 7))
                        c.drawCircle(xx, y - 92, 18, wb.marker(BLACK, 6))
                    else:
                        c.drawLine(xx - 6, y - 110, xx + 6, y + 35, wb.marker(ORANGE, 12))
                        c.drawLine(xx - 6, y - 110, xx + 6, y + 35, wb.marker(BLACK, 3))
            K.text(c, NAMES6[i], x, y + 110, 52, "hand", BLUE)
    return draw


L.note(*NAMES6)
for i in range(3):
    b.custom(j, k_i6[i], k_i6[i] + 0.3, pop_fn(j, k_i6[i], icon6(i)), sfx=("wood_high", "pop", "wood_low")[i], gain=0.7)


def dots6(c, kk, T):
    t0 = tb(10, k_out6)
    if T < t0:
        return None
    for i, x in enumerate(IX):
        dt = T - t0 - i * 0.12
        if dt < 0:
            continue
        y = IY - 160 - 90 * ease_out(clamp01(dt / 0.45)) + 6 * math.sin(T * 4 + i)
        red_dot(c, x + 110, y, pop_scale(dt))
        K.ripple(c, x + 110, y, dt, RED, 90, 6, 0.8, 0.5)
    return None


b.custom(j, k_out6, k_out6 + 0.3, dots6, sfx="pop", gain=0.75)
b.hit(j, k_out6 + 1, "rim", 0.6, "问题露在外面")
b.custom(j, k_out6 + 1, k_out6 + 1.3, L.pop_text("问题露在外面", cx, cy + 105, 74, RED, j, k_out6 + 1))
WK6 = (cx - 360, cy + 470, 0.72)
k_point6 = k_out6 + 1


def wk6(c, kk, T):
    x, y, s = WK6
    sc = pop_scale(T - tb(10, 1))
    if sc <= 0:
        return None
    hy = y - 290 * s
    up = ease_out(clamp01((T - tb(10, k_point6)) / 0.3))
    rh = (lerp(x + 70 * s, x + 150 * s, up), lerp(hy + 170 * s, hy - 40 * s, up))
    with at_pop(c, x, y, sc):
        draw_worker(c, x, y, s, rh=rh, mood="smile" if up > 0 else "flat")
    return None


b.custom(j, 1, 1.3, wk6, sfx="pop", gain=0.5)
label(j, 1.4, "员工", WK6[0], WK6[1] + 70, 52, BLUE)

# ================================================================ 屏 11：为什么要摆出来？红点钻进脑袋、电脑，没了；看不见，就没人管
cx, cy = R[6]
j = L.scene(11, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("为什么要摆出来？", cx, cy - 520, 86, BLACK, j, 0), sfx="pop", gain=0.6)
HEAD7 = (cx - 290, cy - 230, 130)
MON7 = (cx + 290, cy - 230)
k_hd = kq(j, wt(16, 0, 0.3), lo=1)
k_pc = kq(j, wt(16, 0, 0.65), lo=k_hd + 1)
k_gone = kq(j, wt(16, 1, 0.2), lo=k_pc + 1)
k_none7 = kq(j, wt(17, 1, 0.3), lo=k_gone + 1)


def head7(c, sc, T):
    x, y, r = HEAD7
    with at_pop(c, x, y, sc):
        big_head(c, x, y, r)
        K.text(c, "脑子里", x, y + r * 1.75 + 60, 60, "hand", BLACK)


def mon7(c, sc, T):
    with at_pop(c, *MON7, sc):
        monitor(c, *MON7, 340, 240)
        for i in range(4):
            c.drawLine(MON7[0] - 120, MON7[1] - 70 + i * 40, MON7[0] + 120 - (i % 2) * 60, MON7[1] - 70 + i * 40,
                       wb.marker(GRAY, 5))
        K.text(c, "电脑里", MON7[0], HEAD7[1] + HEAD7[2] * 1.75 + 60, 60, "hand", BLACK)


L.note("脑子里", "电脑里")
b.custom(j, k_hd, k_hd + 0.3, pop_fn(j, k_hd, head7), sfx="wood_high", gain=0.7)
b.custom(j, k_pc, k_pc + 0.3, pop_fn(j, k_pc, mon7), sfx="wood_low", gain=0.7)


def dots7(c, kk, T):
    """红点从上方落下，钻进脑袋 / 屏幕，缩小消失。"""
    for i, (tx, ty, k_) in enumerate(((HEAD7[0] - 40, HEAD7[1], k_hd), (HEAD7[0] + 50, HEAD7[1] + 30, k_hd),
                                      (MON7[0] - 50, MON7[1], k_pc), (MON7[0] + 60, MON7[1] + 10, k_pc))):
        t0 = tb(11, k_) + 0.3 + (i % 2) * 0.15
        t1 = tb(11, k_gone)
        if T < t0:
            continue
        g = ease_in_out(clamp01((T - t0) / 0.5))
        x, y = lerp(tx + (i % 2 * 2 - 1) * 60, tx, g), lerp(ty - 300, ty, g)
        sc = 1.0 - ease_in_out(clamp01((T - t1 - i * 0.07) / 0.35))
        if sc <= 0:
            K.ripple(c, tx, ty, T - t1 - i * 0.07 - 0.35, GRAY, 60, 4, 0.6, 0.4)
            continue
        red_dot(c, x, y, 0.8 * sc)
    return None


b.custom(j, k_hd, k_hd + 0.1, dots7)
b.hit(j, k_gone, "shaker", 0.6, "红点钻进去，没了")
LD7 = (cx - 300, cy + 480, 0.75)


def ld7(c, kk, T):
    x, y, s = LD7
    sc = pop_scale(T - tb(11, k_gone))
    if sc <= 0:
        return None
    look = math.sin((T - tb(11, k_gone)) * 3.5)
    with at_pop(c, x, y, sc):
        draw_leader(c, x, y, s, head_dx=12 * look)
        eye(c, x, y - 290 * s - 105, 0.62, look=look, slash=T >= tb(11, k_gone + 1))
    return None


b.custom(j, k_gone, k_gone + 0.3, ld7, sfx="pop", gain=0.55)
b.hit(j, k_gone + 1, "rim", 0.65, "谁也看不见")
label(j, k_gone + 0.5, "组长", LD7[0] + 150, LD7[1] - 30, 52, RED)
b.custom(j, k_none7, k_none7 + 0.3, L.stamp("没人管", cx + 250, cy + 330, 112, j, k_none7), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_none7, 12.0)]

# ================================================================ 屏 12：两格分屏（结果）——左格方块往外掉“漏”；右格卡片变红，小王举手，组长赶来
cx, cy = R[7]
j = L.scene(12, (cx, cy + 20, Z))
LX, RX, PY0, PY1 = panels_xy(12)
split_frame(j, 0)
LI8 = (LX - 120, cy + 440, 0.8)
WG8 = (RX - 150, cy + 440, 0.8)
CL8 = (LX - 20, cy - 175, 200)
BD8 = (RX, cy - 165, 470, 360)
k_busy = kq(j, wt(18, 0, 0.3), lo=3)
k_leak = kq(j, wt(18, 1, 0.3), lo=k_busy + 1)
k_red8 = kq(j, wt(19, 1, 0.6), lo=k_leak + 2)
k_see8 = kq(j, wt(19, 2, 0.5), lo=k_red8 + 1)
k_help = kq(j, wt(19, 3, 0.2), lo=k_see8 + 1)
DROPS8 = [(i, k_leak + 0.35 * n) for n, i in enumerate((11, 7, 3, 9))]


def li8(c, kk, T):
    x, y, s = LI8
    sc = pop_scale(T - tb(12, 2))
    if sc <= 0:
        return None
    hy = y - 290 * s
    sad = T >= tb(12, k_leak)
    lh = (x - 80, hy - 10) if sad else None
    rh = (x + 80, hy - 10) if sad else None
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad" if sad else "flat", lh=lh, rh=rh)
    x, y, r = CL8
    with at_pop(c, x, y, sc):
        cloud(c, x, y, r, tail=(LI8[0], LI8[1] - 290 * LI8[2] - 60))
        n = 12 if T < tb(12, k_busy) else 14
        blocks_in(c, x, y, r, n, drop=[(i, tb(12, k_)) for i, k_ in DROPS8], T=T)
    return None


b.custom(j, 2, 2.3, li8, sfx="pop", gain=0.6)
b.hit(j, k_busy, "wood_high", 0.6, "一忙起来，又塞进两块")
for i, k_ in DROPS8:
    if is_int(k_):
        b.hit(j, k_, "wood_low", 0.6, "方块往外掉")
b.custom(j, k_leak + 1, k_leak + 1.3, L.slam_text("漏", LX + 190, cy + 170, 150, RED, j, k_leak + 1), sfx="kick", gain=0.8)
b.shots[j].shake = [(k_leak + 1, 9.0)]


def board8(c, kk, T):
    x, y, w, h = BD8
    sc = pop_scale(T - tb(12, 2.5))
    if sc <= 0:
        return None
    with at_pop(c, x, y, sc):
        xs = board3(c, x, y, w, h)
        cards = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2)]
        for cc, row in cards:
            nx, ny = note_xy(xs, cc, row, y, h)
            red = cc == 1 and row == 1 and T >= tb(12, k_red8)
            t_r = tb(12, k_red8)
            bl = 0.6 + 0.4 * math.cos((T - t_r) * 18) if red and T - t_r < 0.8 else 1.0
            sticky(c, nx, ny, 0.62, "", fill=RED_FILL if red else (NOTE_FILL, "#FFD9A8", GREEN_FILL)[cc],
                   line=RED if red else NOTE_LINE, rot=((row * 17) % 9 - 4), alpha=bl)
            c.drawLine(nx - 22, ny + 4, nx + 22, ny + 4, wb.marker(GRAY, 3))
        if T >= tb(12, k_red8):
            nx, ny = note_xy(xs, 1, 1, y, h)
            K.ripple(c, nx, ny, T - tb(12, k_red8), RED, 120, 7, 0.9, 0.6)
            if T >= tb(12, k_see8):
                a = clamp01((T - tb(12, k_see8)) / 0.3)
                c.drawCircle(nx, ny, 62, wb.marker(RED, 8, a))
                K.text(c, "卡住", nx + 5, ny + 98, 46, "hand", RED, a)
    return None


L.note("卡住")
b.custom(j, 2.5, 2.8, board8)
b.hit(j, k_red8, "rim", 0.75, "一张卡片变红")
b.hit(j, k_see8, "ding", 0.6, "一眼就看到")


def wang8(c, kk, T):
    x, y, s = WG8
    sc = pop_scale(T - tb(12, 3))
    if sc <= 0:
        return None
    hy = y - 290 * s
    up = ease_out(clamp01((T - tb(12, k_see8)) / 0.3))
    rh = (lerp(x + 70 * s, x + 155 * s, up), lerp(hy + 170 * s, hy - 40 * s, up))
    with at_pop(c, x, y, sc):
        draw_wang(c, x, y, s, rh=rh, mood="smile" if T >= tb(12, k_help) else "flat")
    return None


b.custom(j, 3, 3.3, wang8, sfx="pop", gain=0.55)
b.custom(j, k_help, k_help + 0.3, walker(j, k_help, 1.5, RX + 340, RX + 150, cy + 440, 0.8, clip=(8, 1)), sfx="wood_low",
         gain=0.55)
b.hit(j, k_help + 1, "wood_high", 0.5, "组长赶来")
b.custom(j, k_help + 1, k_help + 1.3, L.pop_text("来帮忙", RX + 150, cy + 60, 58, GREEN, j, k_help + 1))

# ================================================================ 屏 13：小李拿着小白板犹豫，组长好奇看；“三步”
cx, cy = R[12]
j = L.scene(13, (cx, cy + 20, Z))
LI13 = (cx - 260, cy + 440, 0.9)
LD13 = (cx + 380, cy + 440, 0.85)
k_hold = kq(j, wt(20, 1, 0.3), lo=1)
k_shy = kq(j, wt(20, 2, 0.3), lo=k_hold + 1)
k_peek = kq(j, wt(20, 3, 0.2), lo=k_shy + 1)
k_three = kq(j, wt(21, 1, 0.5), lo=k_peek + 2)


def li13(c, kk, T):
    x, y, s = LI13
    sc = pop_scale(T - tb(13, 1))
    if sc <= 0:
        return None
    hy = y - 290 * s
    hold = T >= tb(13, k_hold)
    hide = ease_in_out(clamp01((T - tb(13, k_shy)) / 0.4)) * (1 - ease_in_out(clamp01((T - tb(13, k_three)) / 0.4)))
    bx = x + 150 - 60 * hide
    by = hy + 110 + 40 * hide
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad" if hide > 0.5 else ("smile" if T >= tb(13, k_three) else "flat"),
                lh=(bx - 80, by + 30) if hold else None, rh=(bx + 70, by + 30) if hold else None)
        if hold:
            board3(c, bx, by, 260, 180, alpha=clamp01((T - tb(13, k_hold)) / 0.2))
        if hide > 0.3:
            for i in range(2):
                c.drawPath(P((x - 70 + i * 140, hy - 20), (x - 60 + i * 140, hy - 50), (x - 50 + i * 140, hy - 20)),
                           wb.marker(BLUE, 5, hide))
    return None


b.custom(j, 1, 1.3, li13, sfx="pop", gain=0.6)
label(j, 1.4, "小李", LI13[0], LI13[1] + 85, 64)
b.hit(j, k_hold, "wood_high", 0.6, "拿起小白板")
b.hit(j, k_shy, "wood_low", 0.55, "往身后藏")
b.custom(j, k_peek, k_peek + 0.3, L.figure(draw_leader, j, k_peek, *LD13, head_dx=-10), sfx="pop", gain=0.55)
label(j, k_peek + 0.4, "组长", LD13[0], LD13[1] + 80, 60, RED)
b.custom(j, k_peek, k_peek + 0.3, L.pop_bubble("这是啥？", cx + 330, cy - 100, j, k_peek, size=64, tail=1,
                                                until=(13, k_three)))
b.custom(j, k_three, k_three + 0.3, L.slam_text("三步", cx, cy - 330, 220, RED, j, k_three, rot=-4), sfx="kick", gain=0.9)
b.shots[j].shake = [(k_three, 12.0)]

# ================================================================ 屏 14：做法一——小王的话还没说完，小李已经写好便利贴
cx, cy = R[13]
j = L.scene(14, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("① 当场写", cx, cy - 500, 96, BLUE, j, 0), sfx="pop", gain=0.6)
WG14 = (cx + 380, cy + 440, 0.9)
LI14 = (cx - 380, cy + 440, 0.9)
NT14 = (cx - 150, cy - 50)
k_say = kq(j, wt(22, 1, 0.2), lo=1)
k_write = kq(j, wt(22, 2, 0.1), lo=k_say + 1)
k_mem = kq(j, wt(22, 3, 0.3), lo=k_write + 2)
b.custom(j, 1, 1.3, L.figure(draw_wang, j, 1, *WG14, mood="smile",
                             lh=lambda T: (WG14[0] - 130, WG14[1] - 290 * WG14[2] + 110) if T >= tb(14, k_say) else None),
         sfx="pop", gain=0.55)
label(j, 1.4, "小王", WG14[0], WG14[1] + 85, 64, BLUE)
b.custom(j, k_say, k_say + 0.3, L.pop_bubble("周三前给我", cx + 270, cy - 260, j, k_say, size=62, tail=1), sfx="pop", gain=0.7)


def li14(c, kk, T):
    x, y, s = LI14
    sc = pop_scale(T - tb(14, 1.5))
    if sc <= 0:
        return None
    hy = y - 290 * s
    w = T >= tb(14, k_write) and T < tb(14, k_write + 1.5)
    rh = (NT14[0] - 40 + 25 * math.sin(T * 16), NT14[1] + 40 + 8 * math.cos(T * 11)) if w else (x + 100, hy + 120)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile", rh=rh)
    return None


b.custom(j, 1.5, 1.8, li14)
label(j, 1.9, "小李", LI14[0], LI14[1] + 85, 64)


def note14(c, kk, T):
    t0 = tb(14, k_write)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    msg = "周三交表"
    n = min(len(msg), int((T - t0) / 0.22) + 1)
    with at_pop(c, *NT14, sc):
        sticky(c, *NT14, 1.6, "", rot=-4)
        K.text(c, msg[:n], NT14[0], NT14[1] + 12, 44, "hand", BLACK)
    return None


L.note("周三交表")
b.custom(j, k_write, k_write + 0.3, note14, sfx="wood_high", gain=0.7)
b.hit(j, k_write + 1, "wood_low", 0.5, "写下来")


def mem14(c, sc, T):
    cx, cy = R[13]
    x, y = cx + 50, cy + 230
    with at_pop(c, x, y, sc):
        cloud(c, x, y, 85, fill="#F4F4F4", line_c=GRAY)
        K.text(c, "记性", x, y + 5, 50, "hand", GRAY)
        c.drawPath(cross(x, y, 70), wb.marker(RED, 11))


L.note("记性")
b.custom(j, k_mem, k_mem + 0.3, pop_fn(j, k_mem, mem14), sfx="rim", gain=0.75)

# ================================================================ 屏 15：做法二——三栏：要做 / 在做 / 做完，便利贴从左往右移
cx, cy = R[14]
j = L.scene(15, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("② 分三栏", cx, cy - 500, 96, BLUE, j, 0), sfx="pop", gain=0.6)
BD15 = (cx + 80, cy - 90, 860, 600)
LI15 = (cx - 430, cy + 470, 0.8)
k_cols = [kq(j, wt(23, 1, 0.6), lo=2)]
k_cols += [k_cols[0] + 0.5, k_cols[0] + 1]
k_mv = [k_cols[0] + 2, k_cols[0] + 3]
L.note(*COLS)


def board15(c, kk, T):
    x, y, w, h = BD15
    sc = pop_scale(T - tb(15, 1))
    if sc <= 0:
        return None
    heads = [pop_scale(T - tb(15, k_)) for k_ in k_cols]
    with at_pop(c, x, y, sc):
        xs = board3(c, x, y, w, h, heads)
        # 三张便利贴：A 从要做 → 在做 → 做完；B 从要做 → 在做；C 留在要做
        def pos(col, row):
            return xs[col], y - h / 2 + h * 0.36 + row * h * 0.24
        moves = {"周报": [(0, 0), (1, 0), (2, 0)], "报销": [(0, 1), (0, 1), (1, 1)], "订票": [(0, 2), (0, 2), (0, 2)]}
        for name, seq in moves.items():
            st = sum(1 for k_ in k_mv if T >= tb(15, k_))
            p0 = pos(*seq[max(0, st - 1)]) if st else pos(*seq[0])
            p1 = pos(*seq[st])
            g = ease_in_out(clamp01((T - tb(15, k_mv[st - 1])) / 0.35)) if st else 1.0
            nx, ny = lerp(p0[0], p1[0], g), lerp(p0[1], p1[1], g) - math.sin(g * math.pi) * 40
            if T < tb(15, k_cols[0]):
                continue
            col_now = seq[st][0] if g >= 1 else seq[max(0, st - 1)][0]
            sticky(c, nx, ny, 0.95, name, fill=(NOTE_FILL, "#FFD9A8", GREEN_FILL)[col_now], size=44,
                   tcolor=COL_C[col_now] if col_now else BLACK)
            if col_now == 2:
                c.drawPath(check(nx + 50, ny - 40, 26), wb.marker(GREEN, 8))
    return None


L.note("周报", "报销", "订票")
b.custom(j, 1, 1.3, board15, sfx="wood_low", gain=0.7)
for k_ in k_cols:
    if is_int(k_):
        b.hit(j, k_, "pop", 0.65, "表头")
for k_ in k_mv:
    b.hit(j, k_, "wood_high", 0.7, "便利贴往右挪一栏")
b.custom(j, 1.5, 1.8, L.figure(draw_li, j, 1.5, *LI15, mood="smile",
                               rh=lambda T: (LI15[0] + 140, LI15[1] - 290 * LI15[2] - 10)
                               if any(tb(15, k_) - 0.2 <= T < tb(15, k_) + 0.4 for k_ in k_mv) else None))
label(j, 1.9, "小李", LI15[0], LI15[1] + 80, 60)
b.path(j, k_mv[0] + 0.2, k_mv[0] + 0.7, arrow((cx - 280, cy + 300), (cx + 440, cy + 300), 0.04, 34), ORANGE, 9)
b.text(j, k_mv[0] + 0.7, k_mv[0] + 1.2, "从左往右挪", cx + 80, cy + 390, 60, ORANGE)

# ================================================================ 屏 16：做法三——“在做”只放三件，第四张挤不进去，被挡回
cx, cy = R[15]
j = L.scene(16, (cx, cy + 20, Z))
b.custom(j, 0, 0.3, L.pop_text("③ 最多三件", cx, cy - 500, 96, BLUE, j, 0), sfx="pop", gain=0.6)
COL16 = (cx - 40, cy - 40, 340, 640)
LI16 = (cx + 400, cy + 460, 0.8)
k_c16 = kq(j, wt(24, 1, 0.1), lo=1)
k_fill = kq(j, wt(24, 2, 0.0), lo=k_c16 + 1)
k_4th = kq(j, wt(24, 2, 0.8), lo=k_fill + 2)


def col16(c, kk, T):
    x, y, w, h = COL16
    sc = pop_scale(T - tb(16, k_c16))
    if sc <= 0:
        return None
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
        c.drawRoundRect(r, 16, 16, K.paint("#FFF4C2"))
        c.drawRoundRect(r, 16, 16, wb.marker(ORANGE, 9))
        K.text(c, "在做", x, y - h / 2 + 55, 64, "hand", ORANGE)
        c.drawLine(x - w / 2 + 14, y - h / 2 + 105, x + w / 2 - 14, y - h / 2 + 105, wb.marker(ORANGE, 4))
    n = sum(1 for i in range(3) if T >= tb(16, k_fill + i * 0.5))
    for i in range(n):
        ny = y - h / 2 + 190 + i * 160
        s_ = pop_scale(T - tb(16, k_fill + i * 0.5), 0.25)
        with at_pop(c, x, ny, s_):
            sticky(c, x, ny, 1.0, str(i + 1), fill="#FFD9A8", size=56, rot=((i * 17) % 9 - 4))
    t4 = tb(16, k_4th)
    if T >= t4 - 0.35:
        g = clamp01((T - (t4 - 0.35)) / 0.35)
        if T < t4:
            nx = lerp(x - 520, x - w / 2 - 30, g * g)
        else:
            dt = T - t4
            nx = x - w / 2 - 75 - 150 * ease_out(clamp01(dt / 0.35)) + wobble(dt, 18, 26, 6)
        ny = y + 40
        sticky(c, nx, ny, 1.0, "4", fill=RED_FILL, line=RED, size=56, rot=8)
        if T >= t4:
            a = clamp01((T - t4) / 0.2)
            c.drawPath(cross(x - w / 2 - 5, ny - 95, 30), wb.marker(RED, 9, a))
    return None


L.note("在做", "1", "2", "3", "4")
b.custom(j, k_c16, k_c16 + 0.3, col16, sfx="wood_low", gain=0.7)
b.hit(j, k_fill, "pop", 0.6, "放进三张")
b.hit(j, k_fill + 1, "pop", 0.6, "放进三张")
b.hit(j, k_4th, "tom", 0.8, "第四张被挡回")
b.shots[j].shake = [(k_4th, 7.0)]
b.custom(j, k_4th, k_4th + 0.3, L.pop_text("满了", cx - 430, cy + 230, 72, RED, j, k_4th))


def li16(c, kk, T):
    x, y, s = LI16
    sc = pop_scale(T - tb(16, 1))
    if sc <= 0:
        return None
    hy = y - 290 * s
    up = ease_out(clamp01((T - tb(16, k_4th + 1)) / 0.3))
    rh = (lerp(x + 70 * s, x + 130 * s, up), lerp(hy + 170 * s, hy - 60 * s, up))
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if up > 0 else "flat", rh=rh)
    return None


b.custom(j, 1, 1.3, li16, sfx="pop", gain=0.55)
label(j, 1.4, "小李", LI16[0], LI16[1] + 80, 60)
b.custom(j, k_4th + 1, k_4th + 1.3, L.pop_text("做完一件再拿", cx + 330, cy - 190, 56, GREEN, j, k_4th + 1), sfx="ding",
         gain=0.55)

# ================================================================ 屏 17：小李靠在椅背上喝水；催促的气泡越来越少
cx, cy = R[16]
j = L.scene(17, (cx, cy + 20, Z))
LI17 = (cx - 200, cy + 440, 1.1)
BD17 = (cx - 280, cy - 300, 380, 270)
k_lean = kq(j, wt(25, 0, 0.3), lo=1)
k_sip = kq(j, wt(25, 1, 0.5), lo=k_lean + 1)
k_less = kq(j, wt(26, 0, 0.3), lo=k_sip + 1)
k_less2 = kq(j, wt(26, 1, 0.6), lo=k_less + 2)
BUB17 = [(cx + 300, cy - 440), (cx + 360, cy - 280), (cx + 260, cy - 120), (cx + 380, cy + 40), (cx + 300, cy + 200)]
GONE17 = [k_less, k_less + 0.5, k_less + 1, k_less2]


def board17(c, sc, T):
    x, y, w, h = BD17
    with at_pop(c, x, y, sc):
        xs = board3(c, x, y, w, h)
        for col, n in enumerate((1, 2, 4)):
            for i in range(n):
                nx, ny = xs[col] + (i % 2) * 30 - 15, y - h / 2 + h * 0.4 + (i // 2) * h * 0.25 + (i % 2) * 12
                sticky(c, nx, ny, 0.42, "", fill=(NOTE_FILL, "#FFD9A8", GREEN_FILL)[col])


b.custom(j, 0, 0.3, pop_fn(j, 0, board17), sfx="wood_high", gain=0.6)


def chair_li(c, kk, T):
    """小李坐在椅子上：往后一靠，端起杯子喝一口。"""
    x, y, s = LI17
    sc = pop_scale(T - tb(17, 0.5))
    if sc <= 0:
        return None
    lean = ease_in_out(clamp01((T - tb(17, k_lean)) / 0.5))
    sip = 0.5 - 0.5 * math.cos(clamp01((T - tb(17, k_sip)) / 1.2) * 2 * math.pi) if T >= tb(17, k_sip) else 0.0
    seat_y = y - 150 * s
    hip = (x, seat_y - 8)
    ang = math.radians(-4 - 16 * lean)                     # 上身后仰
    L_t = 170 * s
    neck = (hip[0] + math.sin(ang) * L_t, hip[1] - math.cos(ang) * L_t)
    hr = 45 * s
    head = (neck[0] + math.sin(ang) * (hr + 4), neck[1] - math.cos(ang) * (hr + 4))
    sh = (lerp(hip[0], neck[0], 0.82), lerp(hip[1], neck[1], 0.82))
    knee = (x + 120 * s, seat_y - 8)
    foot = (x + 135 * s, y)
    cup = (lerp(x + 150 * s, head[0] + 40 * s, sip), lerp(seat_y - 60 * s, head[1] + 30 * s, sip))
    with at_pop(c, x, y, sc):
        wood = wb.marker("#8A6A3E", 10)
        c.drawPath(join(P((x - 70 * s, seat_y), (x + 80 * s, seat_y)), P((x - 60 * s, seat_y), (x - 70 * s, y)),
                        P((x + 70 * s, seat_y), (x + 80 * s, y)),
                        P((x - 70 * s, seat_y), (x - 95 * s - 40 * s * lean, seat_y - 230 * s))), wood)
        ink = wb.marker(BLACK, 10)
        c.drawPath(join(P(hip, neck), P(hip, knee, foot), P(sh, (x - 30 * s, seat_y - 40 * s)), P(sh, cup)), ink)
        c.drawPath(P(neck, (neck[0] + 10 * s, neck[1] + 45 * s), (neck[0], neck[1] + 70 * s), (neck[0] - 10 * s, neck[1] + 45 * s),
                     close=True), ink)
        c.drawCircle(*head, hr, K.paint("#FFFFFF"))
        hx, hy = head
        c.drawPath(join(circle(hx, hy, hr),
                        P((hx - 45 * s, hy - 5 * s), (hx - 30 * s, hy - 45 * s), (hx + 30 * s, hy - 45 * s), (hx + 50 * s, hy + 10 * s))),
                   ink)
        c.drawPath(wb.face(hx, hy + 290 * s, s, "smile" if lean > 0.5 else "flat"), wb.marker(BLACK, 7))
        c.drawRoundRect(skia.Rect.MakeXYWH(cup[0] - 18, cup[1] - 50, 36, 52), 6, 6, K.paint("#FFFFFF"))
        c.drawRoundRect(skia.Rect.MakeXYWH(cup[0] - 18, cup[1] - 50, 36, 52), 6, 6, wb.marker(BLUE, 6))
    return None


b.custom(j, 0.5, 0.8, chair_li)
label(j, 1.0, "小李", LI17[0] - 20, LI17[1] + 85, 64)
b.hit(j, k_lean, "wood_low", 0.6, "靠在椅背上")
b.hit(j, k_sip, "pop", 0.55, "喝口水")


def bubbles17(c, kk, T):
    for i, (x, y) in enumerate(BUB17):
        sc = pop_scale(T - tb(17, 1 + i * 0.25), 0.25)
        if sc <= 0:
            continue
        if i < len(GONE17):
            t_g = tb(17, GONE17[i])
            sc *= 1 - ease_in_out(clamp01((T - t_g) / 0.25))
            if sc <= 0:
                K.ripple(c, x, y, T - t_g - 0.25, GRAY, 70, 4, 0.6, 0.35)
                continue
        with at_pop(c, x, y, sc):
            bubble_txt(c, "快点！", x, y, 50, RED, tail=-1)
    return None


L.note("快点！")
b.custom(j, 1, 1.3, bubbles17, sfx="pop", gain=0.55)
for k_ in GONE17:
    if is_int(k_):
        b.hit(j, k_, "pop", 0.5, "催促气泡一个个消失")
b.custom(j, k_less2, k_less2 + 0.3, L.stamp("少了", cx + 330, cy - 260, 110, j, k_less2, color=GREEN, rot=-6), sfx="kick",
         gain=0.75)

# ================================================================ 屏 18：评论区见 + 下一讲预告
cx, cy = R[17]
j = L.scene(18, (cx, cy + 20, Z))
k_q18 = kq(j, wt(27, 0, 0.15), lo=1)
b.text(j, k_q18, k_q18 + 1.0, "你最常忘的", cx, cy - 520, 70, RED, sfx="pop")
b.text(j, k_q18 + 1.0, k_q18 + 1.8, "是哪类事？", cx, cy - 430, 70, RED)
LI18 = (cx - 420, cy + 120, 0.75)
k_type = kq(j, wt(28, 0, 0.3), lo=k_q18 + 2)
INP = (cx + 130, cy - 230, 700, 120)
b.custom(j, 1, 1.3, L.figure(draw_li, j, 1, *LI18, mood="smile",
                             rh=lambda T: (LI18[0] + 120, LI18[1] - 290 * LI18[2] + 60) if T >= tb(18, k_type) else None),
         sfx="pop", gain=0.6)
label(j, 1.4, "小李", LI18[0], LI18[1] + 65, 54)
CATS = [("消息", cx - 130), ("交表", cx + 110), ("取快递", cx + 360)]
k_cat = kq(j, wt(28, 1, 0.1), lo=k_type + 1)
for i, (t_, x) in enumerate(CATS):
    k_ = k_cat + i * 0.5

    def cat18(c, sc, T, x=x, t_=t_, i=i):
        y = R[17][1] - 20
        with at_pop(c, x, y, sc):
            sticky(c, x, y, 1.25, "", fill=(NOTE_FILL, "#FFD9A8", GREEN_FILL)[i], rot=(i - 1) * 6)
            K.text(c, t_, x, y + 8, 48 if len(t_) < 3 else 42, "hand", BLACK)
    L.note(t_)
    b.custom(j, k_, k_ + 0.3, pop_fn(j, k_, cat18), sfx="pop" if is_int(k_) else None, gain=0.6)


def input18(c, kk, T):
    x, y, w, h = INP
    sc = pop_scale(T - tb(18, k_type))
    if sc <= 0:
        return None
    with at_pop(c, x, y, sc):
        r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
        c.drawRoundRect(r, h / 2, h / 2, K.paint("#FFFFFF"))
        c.drawRoundRect(r, h / 2, h / 2, wb.marker(BLUE, 7))
        msg = "我总忘回消息"
        n = min(len(msg), int((T - tb(18, k_type)) / 0.16) + 1)
        tw = K.text(c, msg[:n], x - w / 2 + 40, y, 54, "hand", BLACK, 1, "left")
        if (T * 2) % 1 < 0.5:
            c.drawLine(x - w / 2 + 48 + tw, y - 30, x - w / 2 + 48 + tw, y + 30, wb.marker(BLUE, 5))
        c.drawRoundRect(skia.Rect.MakeXYWH(x + w / 2 - 150, y - 38, 130, 76), 38, 38, K.paint(BLUE))
        K.text(c, "发送", x + w / 2 - 85, y, 44, "sans_medium", "#FFFFFF")
    return None


L.note("我总忘回消息", "发送")
b.custom(j, k_type, k_type + 0.3, input18, sfx="wood_high")
# 2026-11 收尾鼓励（第 29 句）：镜头下移；小李脑袋上压着的箱子搬到白板上变成便利贴，脑袋一轻、人飘起一点；预告卡整体下移 DY
DY = 730
k_e = kq(j, wt(29, 0, 0.0), lo=k_cat + 2)
b.move(j, k_e, (cx, cy + 860, Z), 1.1)
k_e1 = k_e + 2
k_full = kq(j, wt(29, 1, 0.4), lo=k_e1 + 1)
k_out = kq(j, wt(29, 2, 0.1), lo=k_full + 1)
k_float = k_out + 2
LI18E = (cx - 230, cy + 860, 0.8)
WB18 = (cx + 230, cy + 660)
BOX18 = [(-40, -62), (38, -64), (0, -106)]
NOTE18 = [(-95, -20), (0, 30), (95, -20)]


def unload18(c, kk, T, cx=cx, cy=cy):
    """箱子压在小李头上（太满时晃），一个个飞到白板上变成便利贴；最后小李笑着飘起一点。"""
    sc = pop_scale(T - tb(18, k_e1))
    if sc <= 0:
        return None
    x, y, s = LI18E
    wx, wy = WB18
    fl = ease_out(clamp01((T - tb(18, k_float)) / 0.5))
    lift = -45 * fl - 8 * math.sin((T - tb(18, k_float)) * 4) * fl
    hy = y - 290 * s + lift
    with at_pop(c, cx, cy + 660, sc):
        r = skia.Rect.MakeXYWH(wx - 200, wy - 150, 400, 300)
        c.drawRoundRect(r, 12, 12, K.paint("#FFFFFF"))
        c.drawRoundRect(r, 12, 12, wb.marker(BLACK, 7))
        c.drawLine(wx - 150, wy + 150, wx - 170, wy + 210, wb.marker(BLACK, 7))
        c.drawLine(wx + 150, wy + 150, wx + 170, wy + 210, wb.marker(BLACK, 7))
        if fl > 0:
            c.drawLine(x - 50, y + 20, x + 50, y + 20, wb.marker(GRAY, 5, 0.6))
        draw_li(c, x, y + lift, s, "smile" if fl > 0 else ("sad" if T >= tb(18, k_full) else "flat"))
        shake = 7 * math.sin(T * 30) if tb(18, k_full) <= T < tb(18, k_out) else 0.0
        for i, ((bx_, by_), (nx_, ny_)) in enumerate(zip(BOX18, NOTE18)):
            f = ease_in_out(clamp01((T - tb(18, k_out) - i * 0.35) / 0.4))
            px = lerp(x + bx_ + shake, wx + nx_, f)
            py = lerp(hy + by_, wy + ny_, f) - 90 * math.sin(math.pi * f)
            if f < 1:
                with K.at(c, px, py, (i - 1) * 8 * (1 - f)):
                    c.drawPath(C.box_path(0, 0, 90, 64), K.paint("#F1DDB8"))
                    c.drawPath(C.box_path(0, 0, 90, 64), wb.marker("#A9773E", 6))
            else:
                sticky(c, px, py, 0.75, "", fill=(NOTE_FILL, "#FFD9A8", GREEN_FILL)[i], rot=(i - 1) * 6)
    return None


b.custom(j, k_e1, k_e1 + 0.3, unload18, sfx="pop", gain=0.6)
b.hit(j, k_full, "wood_low", 0.7, "头上的箱子晃")
b.hit(j, k_out, "pop", 0.6, "箱子飞到白板上")
b.hit(j, k_out + 1, "pop", 0.5, "箱子飞到白板上")
b.custom(j, k_float, k_float + 0.3, L.pop_text("给脑子减减负", cx, cy + 390, 70, BLUE, j, k_float), sfx="ding", gain=0.7)
k_n18 = kq(j, wt(30, 0, 0.15), lo=k_float + 1)
b.path(j, k_n18, k_n18 + 0.6, rect(cx, cy + 390 + DY, 1060, 260, 24), BLUE, 8, sfx="wood_high")
b.text(j, k_n18 + 0.5, k_n18 + 0.8, "下一讲", cx - 120, cy + 300 + DY, 50, BLUE)
b.text(j, k_n18 + 0.8, k_n18 + 2.2, "会开了三次，问题怎么还在？", cx - 80, cy + 390 + DY, 56, BLACK)


def door18(c, sc, T):
    cx, cy = R[17]
    x, y = cx + 420, cy + 420 + DY
    with at_pop(c, x, y, sc, rot=6):
        r = skia.Rect.MakeXYWH(x - 70, y - 40, 140, 80)
        c.drawRoundRect(r, 10, 10, K.paint("#FFFFFF"))
        c.drawRoundRect(r, 10, 10, wb.marker(RED, 6))
        K.text(c, "第三次", x, y, 40, "hand", RED)


L.note("第三次")
b.custom(j, k_n18 + 2.2, k_n18 + 2.5, pop_fn(j, k_n18 + 2.2, door18))

# ================================================================ 收尾
L.finish(cover_shot=12, square_shot=7)
L.export(globals())
