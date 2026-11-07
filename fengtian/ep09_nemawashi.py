"""《丰田模式》09 共识：方案挺好，为什么一开会就被否？（白板手绘 + AI 旁白，竖屏 2:3）

对话改写：同一场会演两遍。
- 0–3 秒：系列开场“丰田模式”四字，缓推到小李举着熬夜写的方案，组长问“预算？”、小王问“人手？”，“再看看吧”砸下；
- 回放（左上角红色“▶ 回放”牌 + 走动的时间码）：会议桌，小李站起来，drop 时投影“换新流程”砸下；
  小王愣住冒感叹号“活谁来接？”，组长皱眉冒火“怎么没提前说？”；回放暂停：方案打勾，时间轴上“会前”是空的，
  两个人都在“会上”才第一次听到；
- 书中做法：“会前沟通”（小字 nemawashi）；移树——铲子绕着树根松土三下，树连根挪到新坑，长出新叶；
  时间轴：决定很长（一个个问、几种办法比过），执行很短很快；会前小房间吵完、会上大家点头；
- 改写（“回放”被划掉，蓝色“✎ 改写”牌砸下）：会前一天茶水间，小李和小王圈出最怕的一步；再到组长桌边，组长指出风险；
  第二天同一张会议桌，投影上多了两条带头像的意见，十分钟，“通过”；
- 说回我们：私下聊换岗（打勾）vs 周会上突然举手（打叉）；先看家里日历（打勾）vs 先订好票（打叉）；
  一长串名字有点累、怕被说搞关系；三步做法；会前十分钟 vs 会上一小时；评论区 + 下一讲预告（日历飞快翻，小李站在原地）。
办公室里的同事小王用本模块的 draw_wang（短发、白衬衫、蓝工牌，不戴安全帽，与第 06、07 讲同一造型）；
组长用 common.draw_leader（红帽、夹板、红臂章），领导用 common.draw_boss；本讲没有车间员工。
文案见 fengtian/PLAN.md「### 09 共识」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian import theme as FT
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, BOARD_C, draw_boss, draw_li, pop_scale,
                             rest_hands, walk)
from whiteboard import engine as wb
from whiteboard.engine import P, check, circle, cross, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2, 3], "回放 · 原来那场会", 2),
    ([4, 5], "回放 · 原来那场会", 3),
    ([6], "回放 · 问题在哪", 4),
    ([7, 8], "丰田模式 · 书中做法", 5),
    ([9], "丰田模式 · 书中做法", 6),
    ([10, 11], "丰田模式 · 书中做法", 7),
    ([12, 13], "书中观点", 8),
    ([14, 15], "改写 · 同一场会", 9),
    ([16], "改写 · 同一场会", 10),
    ([17], "改写 · 同一场会", 11),
    ([18, 19], "说回我们自己", 12),
    ([20], "说回我们自己", 13),
    ([21, 22], "说回我们自己", 14),
    ([23], "做法一 · 示意", 15),
    ([24], "做法二 · 示意", 16),
    ([25], "做法三 · 示意", 17),
    ([26], "少吵一小时", 18),
    ([27, 28, 29], "评论区见", 19),
]

THEME = FT.get("09")          # 本讲样式（fengtian/theme.py）：蓝图纸、开场 reject、转场 wipe
L = C.Lesson("09", SCREENS, drop_screen=2, board_size=(5000, 11900), theme=THEME)
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

# 各屏在白板上的区块中心（相邻屏相距 1600，蛇形排列）
R = [(2600, 800), (900, 900), (900, 2500), (2500, 2500), (4100, 2500), (4100, 4100), (2500, 4100), (900, 4100),
     (900, 5700), (2500, 5700), (4100, 5700), (4100, 7300), (2500, 7300), (900, 7300), (900, 8900), (2500, 8900),
     (4100, 8900), (4100, 10500), (2500, 10500), (900, 10500)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 13——决策要慢、要取得共识、充分考虑各种选择，执行要快（根回し nemawashi）。根回し原指移树前先把树根周围的土"
    "松开；丰田做决定时把相关的人都问到、几种办法都比过，定下来以后执行很快。",
    "会议、方案内容为示意；小李、小王、组长、领导、家人为虚构人物。",
]

GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL = "#8A8F99", "#ECEEF1", "#D3EDDC", "#F6C3BE", "#D5E3F7"
WOOD, WOOD_LINE, NOTE_FILL, SKY = "#E3C9A0", "#A9773E", "#FFF1A8", "#E4EEF8"
SOIL, SOIL_LINE, BARK, LEAF, LEAF_LINE = "#C79A6B", "#8A5A2B", "#9B6A3C", "#BFE3B0", "#3E8E4F"


def nbeats(j):
    return L.BOUNDS[j][1] - L.BOUNDS[j][0]


def kq(j, t_local, lo=0):
    """kb，但 lo 超出本屏时夹到最后一拍（排期变短时不报错）。"""
    return kb(j, t_local, lo=min(lo, nbeats(j) - 1))


def nx(j, t_local, prev, gap=1):
    """离 t_local 最近、且至少在 prev 之后 gap 拍的拍号。"""
    return max(kq(j, t_local, prev + gap), prev + gap)


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
def at_pop(c, x, y, sc):
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    c.translate(-x, -y)
    try:
        yield
    finally:
        c.restore()


def ev(j, k, fn, sfx=None, gain=0.8, dur=0.3):
    b.custom(j, k, k + dur, fn, sfx=sfx, gain=gain)


def box(c, x, y, w, h, fill, line, width=6, r=14, alpha=1.0):
    rr = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(rr, r, r, K.paint(fill, alpha))
    c.drawRoundRect(rr, r, r, wb.marker(line, width, alpha))


def dashed(c, a, z, color, width, alpha=1.0, on=18, off=12):
    p = K.paint(color, alpha, width)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    c.drawLine(a[0], a[1], z[0], z[1], p)


def dashed_path(c, path, color, width, alpha=1.0, on=22, off=16):
    p = K.paint(color, alpha, width)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    c.drawPath(path, p)


def head_of(x, y, s):
    return x, y - 290 * s


def bubble_box(c, x, y, w, h, tail=-1, alpha=1.0, fill="#FFFFFF"):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 40, 40, K.paint(fill, alpha))
    c.drawPath(wb.bubble(x, y, w, h, tail), wb.marker(BLACK, 7, alpha))


def sparkle(c, x, y, dt, color=YELLOW, n=8, r0=40, r1=130):
    """放射短线（亮了 / 活了），dt 为距触发的秒数。"""
    if dt < 0 or dt > 0.9:
        return
    f = ease_out(clamp01(dt / 0.5))
    a = 1 - clamp01((dt - 0.5) / 0.4)
    for i in range(n):
        ang = 2 * math.pi * i / n
        r_a, r_b = lerp(r0, r1 * 0.7, f), lerp(r0 + 20, r1, f)
        C.line(c, (x + math.cos(ang) * r_a, y + math.sin(ang) * r_a), (x + math.cos(ang) * r_b, y + math.sin(ang) * r_b),
               color, 7, a)


def sweat(c, x, y, s=1.0, alpha=1.0):
    """一滴汗：(x, y) 为水滴中心。"""
    p = skia.Path()
    p.moveTo(x, y - 26 * s)
    p.cubicTo(x + 4 * s, y - 14 * s, x + 16 * s, y - 2 * s, x + 16 * s, y + 8 * s)
    p.cubicTo(x + 16 * s, y + 18 * s, x + 8 * s, y + 24 * s, x, y + 24 * s)
    p.cubicTo(x - 8 * s, y + 24 * s, x - 16 * s, y + 18 * s, x - 16 * s, y + 8 * s)
    p.cubicTo(x - 16 * s, y - 2 * s, x - 4 * s, y - 14 * s, x, y - 26 * s)
    c.drawPath(p, K.paint("#CFE3F8", alpha))
    c.drawPath(p, wb.marker(BLUE, 4, alpha))


def brows(c, hx, hy, s, alpha=1.0):
    """皱眉：两道朝里压下的粗眉。(hx, hy) 为头中心。"""
    for sgn in (-1, 1):
        C.line(c, (hx + sgn * 30 * s, hy - 26 * s), (hx + sgn * 6 * s, hy - 14 * s), BLACK, 7, alpha)


def puff(c, x, y, dt, color=RED):
    """头顶冒火：两团小烟一抖一抖往上飘。"""
    if dt < 0:
        return
    for n, dx in enumerate((-30, 30)):
        ph = (dt * 1.4 + n * 0.5) % 1.0
        a = 1 - ph
        yy = y - 60 * ph
        r = 14 + 10 * ph
        c.drawCircle(x + dx + 6 * math.sin(dt * 9 + n), yy, r, wb.marker(color, 5, a))


def avatar(c, who, x, y, s=0.6, mood="smile"):
    """只画头像（头中心在 (x, y)）：who = "wang" / "leader" / "boss" / "li"。"""
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x - 90 * s, y - 90 * s, x + 70 * s, y + 52 * s))
    fy = y + 290 * s
    if who == "wang":
        draw_wang(c, x, fy, s, mood=mood)
    elif who == "leader":
        draw_leader(c, x, fy, s, mood="smile" if mood == "smile" else "frown")
    elif who == "boss":
        draw_boss(c, x, fy, s, mood="smile")
    else:
        draw_li(c, x, fy, s, "smile")
    c.restore()


def clock_face(c, x, y, r, frac, color=GREEN, fill=GREEN_FILL, alpha=1.0):
    """钟面：从 12 点顺时针扫出 frac（0–1）的扇形。"""
    c.drawCircle(x, y, r, K.paint("#FFFFFF", alpha))
    if frac > 0.002:
        pie = skia.Path()
        pie.moveTo(x, y)
        pie.arcTo(skia.Rect.MakeXYWH(x - r * 0.9, y - r * 0.9, r * 1.8, r * 1.8), -90, 360 * min(frac, 0.9999), False)
        pie.close()
        c.drawPath(pie, K.paint(fill, alpha))
        c.drawPath(pie, wb.marker(color, max(3, r * 0.03), alpha))
    c.drawCircle(x, y, r, wb.marker(BLACK, max(5, r * 0.05), alpha))
    for i in range(12):
        a = i * math.pi / 6
        C.line(c, (x + math.cos(a) * r * 0.86, y + math.sin(a) * r * 0.86), (x + math.cos(a) * r * 0.96, y + math.sin(a) * r * 0.96),
               BLACK, max(3, r * 0.03), alpha)


def mug(c, x, y, s=1.0, color=ORANGE, fill="#FDE3C8"):
    """马克杯：(x, y) 为杯底中点。"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 26 * s, y - 56 * s, 52 * s, 56 * s), 8 * s, 8 * s, K.paint(fill))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 26 * s, y - 56 * s, 52 * s, 56 * s), 8 * s, 8 * s, wb.marker(color, 5))
    hnd = skia.Path()
    hnd.addArc(skia.Rect.MakeXYWH(x + 16 * s, y - 46 * s, 28 * s, 30 * s), -90, 180)
    c.drawPath(hnd, wb.marker(color, 5))
    for n in range(2):
        st = P((x - 8 * s + n * 14 * s, y - 66 * s), (x - 14 * s + n * 14 * s, y - 82 * s), (x - 6 * s + n * 14 * s, y - 98 * s))
        c.drawPath(st, wb.marker(GRAY, 3))


def badge(c, x, y, kind, alpha=1.0, timecode=None):
    """左上角的“回放 / 暂停 / 改写”牌：(x, y) 为牌子中心。"""
    col = BLUE if kind == "rewrite" else RED
    w, h = 250, 104
    box(c, x, y, w, h, "#FFFFFF", col, 8, 22, alpha)
    ix = x - 72
    if kind == "replay":
        c.drawPath(P((ix - 20, y - 26), (ix - 20, y + 26), (ix + 24, y), close=True), K.paint(col, alpha))
        txt = "回放"
    elif kind == "pause":
        for dx in (-14, 10):
            c.drawRoundRect(skia.Rect.MakeXYWH(ix + dx - 3, y - 26, 14, 52), 3, 3, K.paint(col, alpha))
        txt = "暂停"
    else:
        with K.at(c, ix, y, 40):
            c.drawRoundRect(skia.Rect.MakeXYWH(-9, -32, 18, 52), 3, 3, K.paint("#FFE58A", alpha))
            c.drawRoundRect(skia.Rect.MakeXYWH(-9, -32, 18, 52), 3, 3, wb.marker(col, 4, alpha))
            c.drawPath(P((-9, 20), (9, 20), (0, 36), close=True), K.paint(col, alpha))
        txt = "改写"
    K.text(c, txt, x + 32, y + 3, 64, "hand", col, alpha)
    if timecode is not None:
        K.text(c, timecode, x + 152, y + 4, 46, "sans_medium", GRAY, alpha, "left")


L.note("回放", "暂停", "改写")


def timecode(T, t0):
    s = max(0, int(T - t0))
    return f"00:{s:02d}"


def plan_card(c, x, y, w, h, title, alpha=1.0, steps=True):
    """方案卡：白底，标题 + 三个步骤框（步骤框中心见 step_xy）。"""
    box(c, x, y, w, h, "#FFFFFF", BLACK, 7, 12, alpha)
    K.text(c, title, x, y - h / 2 + 46, 52, "hand", BLACK, alpha)
    if steps:
        for i in range(3):
            sx, sy = step_xy(x, y, w, h, i)
            box(c, sx, sy, w * 0.2, h * 0.34, BLUE_FILL, BLUE, 5, 10, alpha)
            K.text(c, "一二三"[i], sx, sy + 2, 44, "hand", BLUE, alpha)
            if i < 2:
                C.line(c, (sx + w * 0.11, sy), (sx + w * 0.19, sy), BLUE, 5, alpha)
                C.line(c, (sx + w * 0.19, sy), (sx + w * 0.16, sy - 12), BLUE, 5, alpha)
                C.line(c, (sx + w * 0.19, sy), (sx + w * 0.16, sy + 12), BLUE, 5, alpha)


def step_xy(x, y, w, h, i):
    return x + (i - 1) * w * 0.3, y + h * 0.14


L.note("一", "二", "三")


def warn(c, x, y, r, color=RED, rot=0.0, alpha=1.0):
    """警示三角（!）：(x, y) 为中心，r 为外接圆半径。"""
    with K.at(c, x, y, rot):
        p = P((0, -r), (r * 0.9, r * 0.6), (-r * 0.9, r * 0.6), close=True)
        c.drawPath(p, K.paint("#FFE2DE", alpha))
        c.drawPath(p, wb.marker(color, max(4, r * 0.09), alpha))
        K.text(c, "!", 0, r * 0.12, r * 0.95, "black", color, alpha)


def tree(c, x, gy, s=1.0, ball=0.0, buds=0.0, alpha=1.0):
    """一棵树：(x, gy) 为树干落地点；ball>0 时根外包一团松好的土（0–1 为显出程度）；buds 0–1 为新叶。"""
    if ball > 0:
        c.drawOval(skia.Rect.MakeXYWH(x - 150 * s, gy - 30 * s, 300 * s, 170 * s), K.paint(SOIL, alpha * ball))
        c.drawOval(skia.Rect.MakeXYWH(x - 150 * s, gy - 30 * s, 300 * s, 170 * s), wb.marker(SOIL_LINE, 6, alpha * ball))
    for dx, dy in ((-90, 90), (-40, 120), (30, 125), (95, 85), (0, 70)):
        C.line(c, (x, gy - 10 * s), (x + dx * s, gy + dy * s), SOIL_LINE, 7, alpha)
    trunk = P((x - 26 * s, gy), (x - 18 * s, gy - 250 * s), (x + 18 * s, gy - 250 * s), (x + 26 * s, gy), close=True)
    c.drawPath(trunk, K.paint(BARK, alpha))
    c.drawPath(trunk, wb.marker("#6B4423", 6, alpha))
    for dx, dy, r in ((-80, -330, 100), (80, -330, 100), (0, -410, 120)):
        c.drawCircle(x + dx * s, gy + dy * s, r * s, K.paint(LEAF, alpha))
    for dx, dy, r in ((-80, -330, 100), (80, -330, 100), (0, -410, 120)):
        c.drawCircle(x + dx * s, gy + dy * s, r * s, wb.marker(LEAF_LINE, 7, alpha))
    if buds > 0:
        for n, (dx, dy) in enumerate(((-140, -390), (130, -400), (-40, -520), (60, -270), (-150, -280))):
            g = pop_scale(buds * 1.6 - n * 0.12, 0.3)
            if g > 0:
                with K.at(c, x + dx * s, gy + dy * s, n * 40 - 60, g):
                    leaf = skia.Path()
                    leaf.moveTo(0, 22)
                    leaf.quadTo(26, 0, 0, -26)
                    leaf.quadTo(-26, 0, 0, 22)
                    c.drawPath(leaf, K.paint("#7CCB6A", alpha))
                    c.drawPath(leaf, wb.marker(LEAF_LINE, 4, alpha))


def shovel(c, x, y, rot=-20, alpha=1.0):
    """铁锹：(x, y) 为锹头尖。"""
    with K.at(c, x, y, rot):
        blade = P((-30, -70), (30, -70), (26, -20), (0, 0), (-26, -20), close=True)
        c.drawPath(blade, K.paint("#C9CED6", alpha))
        c.drawPath(blade, wb.marker("#5A606B", 5, alpha))
        C.line(c, (0, -70), (0, -260), WOOD_LINE, 10, alpha)
        C.line(c, (-28, -262), (28, -262), WOOD_LINE, 10, alpha)


def meeting_table(c, x, fy, w, h=170):
    tab = skia.Rect.MakeXYWH(x - w / 2, fy - 130, w, h)
    c.drawOval(tab, K.paint(WOOD))
    c.drawOval(tab, wb.marker(WOOD_LINE, 8))


def calendar(c, x, y, w, h, title=None, alpha=1.0, rows=3, ring=None):
    """月历：红色页头 + rows×7 小格；ring=(行, 列列表) 时这些格涂黄。返回格中心函数。"""
    box(c, x, y, w, h, "#FFFFFF", BLACK, 6, 10, alpha)
    top = y - h / 2
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, top, w, h * 0.26), 10, 10, K.paint(RED, alpha))
    if title:
        K.text(c, title, x, top + h * 0.13 + 2, h * 0.17, "hand", "#FFFFFF", alpha)
    gx0, gy0 = x - w / 2 + w * 0.08, top + h * 0.34
    cw, ch = w * 0.84 / 7, (h * 0.6) / rows

    def cell(r, k):
        return gx0 + cw * (k + 0.5), gy0 + ch * (r + 0.5)
    for r in range(rows):
        for k in range(7):
            cx_, cy_ = cell(r, k)
            hot = ring is not None and r == ring[0] and k in ring[1]
            c.drawRoundRect(skia.Rect.MakeXYWH(cx_ - cw * 0.36, cy_ - ch * 0.32, cw * 0.72, ch * 0.64), 4, 4,
                            K.paint(NOTE_FILL if hot else GRAY_FILL, alpha))
    return cell


# ================================================================ 本讲人物

WANG_SHIRT, HAIR = "#FFFFFF", "#2E2A28"


def draw_wang(c, x, y, s, lh=None, rh=None, mood="flat", head_dx=0.0, alpha=1.0):
    """同事小王（办公室）：齐耳短发 + 橙色发卡、白衬衫蓝描边、蓝工牌、蓝色四肢；不戴安全帽（与第 06、07 讲同一造型，照抄 ep07）。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, ft, BLUE, 10, alpha)
    C.line(c, sh, lh, BLUE, 10, alpha)
    C.line(c, sh, rh, BLUE, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 42 * s, hy + 55 * s, x + 42 * s, y - 105 * s)
    c.drawRoundRect(torso, 18 * s, 18 * s, K.paint(WANG_SHIRT, alpha))
    c.drawRoundRect(torso, 18 * s, 18 * s, wb.marker(BLUE, 7, alpha))
    c.drawPath(P((x - 16 * s, hy + 58 * s), (x, hy + 82 * s), (x + 16 * s, hy + 58 * s)), wb.marker(BLUE, 5, alpha))
    badge_ = skia.Rect.MakeXYWH(x - 20 * s, hy + 110 * s, 40 * s, 30 * s)
    c.drawRoundRect(badge_, 4, 4, K.paint("#DCE8F7", alpha))
    c.drawRoundRect(badge_, 4, 4, wb.marker(BLUE, 4, alpha))
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


def draw_leader(c, x, y, s, rh=None, mood="frown", head_dx=0.0, alpha=1.0):
    """组长（老张）：红帽、夹板、红臂章——照抄 common.draw_leader（不跑步），另加 rh（右手位置，用来指方案）和
    mood（"frown" 与 common 相同的撇嘴，"smile" 笑）。默认参数时与 common.draw_leader 画出来一样。"""
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    C.line(c, (x, hy + 45 * s), hip, BLACK, 11, alpha)
    for sgn in (1, -1):
        C.line(c, hip, (x + sgn * 55 * s, y), BLACK, 11, alpha)
    clip_c = (x - 80 * s, hy + 150 * s)
    C.line(c, sh, (clip_c[0] + 10 * s, clip_c[1]), BLACK, 11, alpha)
    rh = rh or (x + 70 * s, hy + 170 * s)
    C.line(c, sh, rh, BLACK, 11, alpha)
    clip = skia.Rect.MakeXYWH(clip_c[0] - 40 * s, clip_c[1] - 55 * s, 80 * s, 105 * s)
    c.drawRoundRect(clip, 6, 6, K.paint(BOARD_C, alpha))
    c.drawRoundRect(clip, 6, 6, wb.marker(BLACK, 6, alpha))
    for i in range(3):
        yy = clip_c[1] - 20 * s + i * 22 * s
        C.line(c, (clip_c[0] - 25 * s, yy), (clip_c[0] + 25 * s, yy), BLACK, 4, alpha)
    ax, ay = lerp(sh[0], rh[0], 0.4), lerp(sh[1], rh[1], 0.4)
    with K.at(c, ax, ay, math.degrees(math.atan2(rh[1] - sh[1], rh[0] - sh[0])) - math.degrees(math.atan2(90, 70))):
        c.drawRoundRect(skia.Rect.MakeXYWH(-30 * s, -15 * s, 60 * s, 30 * s), 6, 6, K.paint(RED, alpha))
    hx = x + head_dx
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    for dx in (-15, 15):
        c.drawCircle(hx + dx * s, hy - 4 * s, 4 * s, K.paint(BLACK, alpha))
    m = skia.Path()
    if mood == "smile":
        m.addArc(skia.Rect.MakeXYWH(hx - 18 * s, hy + 2 * s, 36 * s, 26 * s), 20, 140)
    else:
        m.addArc(skia.Rect.MakeXYWH(hx - 16 * s, hy + 12 * s, 32 * s, 18 * s), 200, 140)
    c.drawPath(m, wb.marker(BLACK, 6, alpha))
    cap = skia.Path()
    cap.addArc(skia.Rect.MakeXYWH(hx - 47 * s, hy - 70 * s, 94 * s, 70 * s), 180, 180)
    cap.close()
    c.drawPath(cap, K.paint(RED, alpha))
    c.drawPath(cap, wb.marker(BLACK, 6, alpha))
    C.line(c, (hx - 10 * s, hy - 35 * s), (hx - 80 * s, hy - 30 * s), BLACK, 10, alpha)


def draw_mom(c, x, y, s, lh=None, rh=None, mood="flat", alpha=1.0):
    """家里人（妈妈）：长发 + 红色连衣裙（与第 07 讲同一造型，照抄 ep07）。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    for ft in ((x - 35 * s, y), (x + 35 * s, y)):
        C.line(c, (ft[0] * 0.6 + x * 0.4, y - 90 * s), ft, BLACK, 9, alpha)
    dress = P((x - 32 * s, hy + 55 * s), (x + 32 * s, hy + 55 * s), (x + 75 * s, y - 80 * s), (x - 75 * s, y - 80 * s),
              close=True)
    c.drawPath(dress, K.paint(RED_FILL, alpha))
    c.drawPath(dress, wb.marker(RED, 7, alpha))
    C.line(c, sh, lh, BLACK, 9, alpha)
    C.line(c, sh, rh, BLACK, 9, alpha)
    hair = skia.Rect.MakeLTRB(x - 55 * s, hy - 50 * s, x + 55 * s, hy + 75 * s)
    c.drawRoundRect(hair, 30 * s, 30 * s, K.paint(HAIR, alpha))
    c.drawCircle(x, hy, 44 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 44 * s, wb.marker(BLACK, 8, alpha))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(x - 48 * s, hy - 52 * s, 96 * s, 64 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint(HAIR, alpha))
    C._eyes_mouth(c, x, hy + 6 * s, s, mood, alpha)


def draw_gossip(c, x, y, s, flip=1, alpha=1.0):
    """路过的同事（灰色简笔，一只手挡在嘴边说悄悄话）。"""
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    c.drawPath(wb.join(P((x, hy + 45 * s), (x, y - 120 * s)), P((x - 50 * s, y), (x, y - 120 * s), (x + 50 * s, y)),
                       P(sh, (x - flip * 60 * s, hy + 160 * s))), wb.marker(GRAY, 9, alpha))
    C.line(c, sh, (x + flip * 60 * s, hy + 10 * s), GRAY, 9, alpha)
    c.drawCircle(x, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 45 * s, wb.marker(GRAY, 8, alpha))
    for dx in (-14, 14):
        c.drawCircle(x + dx * s + flip * 8 * s, hy - 6 * s, 4 * s, K.paint(GRAY, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x + flip * 40 * s - 14 * s, hy - 4 * s, 28 * s, 36 * s), 10 * s, 10 * s,
                    K.paint("#FFFFFF", alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x + flip * 40 * s - 14 * s, hy - 4 * s, 28 * s, 36 * s), 10 * s, 10 * s,
                    wb.marker(GRAY, 5, alpha))


# ================================================================ 屏 0：系列开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：小李举着熬夜写的方案；组长“预算？”、小王“人手？”；“再看看吧”砸下
cx, cy = R[1]
j = L.scene(1, (cx + 5, cy + 60, 0.78))
FY1 = cy + 450
LI1, ZH1, WG1 = (cx - 20, FY1, 0.95), (cx - 420, FY1, 0.8), (cx + 410, FY1, 0.8)
k_ppl = 0
k_doc = kq(j, wt(0, 0, 0.8), 1)
k_sad = nx(j, wt(0, 1, 0.7), k_doc)
k_b1 = nx(j, wt(1, 0, 0.45), k_sad)
k_b2 = nx(j, wt(1, 1, 0.45), k_b1)
k_st = nx(j, wt(1, 2, 0.75), k_b2)
L.note("方案")


def people1(c, sc, T):
    with at_pop(c, cx, FY1, sc):
        x, y, s = ZH1
        jump = 14 * abs(math.sin((T - tb(1, k_b1)) * 9)) * math.exp(-(T - tb(1, k_b1)) * 3) if T >= tb(1, k_b1) else 0
        draw_leader(c, x, y - jump, s, head_dx=8)
        x, y, s = WG1
        asked = T >= tb(1, k_b2)
        hx, hy = head_of(x, y, s)
        draw_wang(c, x, y, s, mood="o" if asked else "flat", head_dx=-6,
                  lh=(x - 80 * s, hy + 40 * s) if asked else None)
        x, y, s = LI1
        hx, hy = head_of(x, y, s)
        held = T >= tb(1, k_doc)
        sad = T >= tb(1, k_sad)
        sq = lerp(1.0, 0.9, ease_out(clamp01((T - tb(1, k_st)) / 0.2))) if T >= tb(1, k_st) else 1.0
        hands = dict(lh=(x - 85 * s, hy + 150 * s), rh=(x + 85 * s, hy + 150 * s)) if held else {}
        draw_li(c, x, y, s, "sad" if sad else "flat", squash=sq, **hands)
        if sad:
            sweat(c, hx + 62 * s, hy - 20 * s + 10 * math.sin(T * 5), 1.1)
    return None


ev(j, k_ppl, pop_fn(j, k_ppl, people1), "wood_low", 0.7)


def paper1(c, kk, T):
    t0 = tb(1, k_doc)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y, s = LI1
    hx, hy = head_of(x, y, s)
    sq = lerp(1.0, 0.9, ease_out(clamp01((T - tb(1, k_st)) / 0.2))) if T >= tb(1, k_st) else 1.0
    py = y - (y - (hy + 175 * s)) * sq
    with K.at(c, x, py, -4, sc * 0.85):
        box(c, 0, 0, 230, 170, "#FFFFFF", BLACK, 6, 8)
        K.text(c, "方案", -20, -42, 50, "hand", BLACK)
        for r in range(3):
            C.line(c, (-80, 4 + r * 28), (80 - (r % 2) * 40, 4 + r * 28), GRAY, 6)
        moon = skia.Path()
        moon.addCircle(78, -48, 24)
        cut = skia.Path()
        cut.addCircle(90, -56, 22)
        moon = skia.Op(moon, cut, skia.PathOp.kDifference_PathOp)
        c.drawPath(moon, K.paint(YELLOW))
        c.drawPath(moon, wb.marker("#B88A10", 3))
    return None


ev(j, k_doc, paper1, "pop", 0.7)
b.hit(j, k_sad, "wood_high", 0.6, "小李冒汗")
ev(j, k_b1, L.pop_bubble("预算？", cx - 330, cy - 40, j, k_b1, 66, BLACK, tail=-1), "pop", 0.7)
ev(j, k_b2, L.pop_bubble("人手？", cx + 320, cy - 40, j, k_b2, 66, BLACK, tail=1), "pop", 0.7)
ev(j, k_st, L.stamp("再看看吧", cx, cy - 330, 84, j, k_st, rot=-6), "kick", 0.9)
b.shots[j].shake = [(k_st, 10.0)]

# ================================================================ 屏 2：回放——会议桌，小李站起来开口，drop 时投影“换新流程”砸下
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(0, 6.0), (KD, 16.0)], [(KD, 0.45)]
FY2 = cy + 450
SIT = 60                                  # 坐着的人比桌后地面高出的量（让上半身露出桌面）
TAB2 = (cx + 250, 640)
SEAT2 = [(draw_wang, cx + 110), (draw_leader, cx + 390)]
LI2 = (cx - 380, FY2, 0.9)
k_bd = 0
k_ppl2 = 1 if KD > 4 else 0
k_open = min(max(kq(j, wt(3, 0, 0.12), k_ppl2 + 1), k_ppl2 + 1), KD - 1)
L.note("下个月", "换新流程")


def badge2(c, kk, T, cx=cx, cy=cy):
    t0 = tb(2, k_bd)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    with K.at(c, cx - 400, cy - 470, -3, sc):
        badge(c, 0, 0, "replay", timecode=timecode(T, t0))
    return None


ev(j, k_bd, badge2, "rim", 0.85)


def meeting2(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, TAB2[0], FY2, sc):
        for draw, x in SEAT2:
            draw(c, x, FY2 - SIT, 0.8)
        meeting_table(c, TAB2[0], FY2, TAB2[1])
        for x in (cx + 110, cx + 390):
            box(c, x, FY2 - 50, 90, 60, "#FFFFFF", GRAY, 4, 6)
    x, y, s = LI2
    hx, hy = head_of(x, y, s)
    up = T >= tb(2, k_open)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if up else "flat", rh=(x + 120 * s, hy - 50 * s) if up else None)
        if up:
            for n in range(3):
                a = math.radians(-40 + n * 25)
                g = clamp01((T - tb(2, k_open)) / 0.25)
                C.line(c, (hx + 70 * s + math.cos(a) * 20, hy + math.sin(a) * 20 + 20),
                       (hx + 70 * s + math.cos(a) * (20 + 40 * g), hy + math.sin(a) * (20 + 40 * g) + 20), BLACK, 6)
    return None


ev(j, k_ppl2, pop_fn(j, k_ppl2, meeting2), "wood_low", 0.7)
b.hit(j, k_open, "wood_high", 0.7, "小李站起来开口")


def screen2(c, kk, T, cx=cx, cy=cy):
    t0 = tb(2, KD)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 70, cy - 220
    with K.at(c, x, y, -2, sc):
        C.line(c, (-300, -165), (300, -165), BLACK, 12)
        box(c, 0, 0, 560, 300, "#FFFFFF", BLACK, 7, 8)
        K.text(c, "下个月", 0, -70, 56, "hand", GRAY)
        K.text(c, "换新流程", 0, 45, 104, "hand", RED)
    return None


ev(j, KD, screen2, "kick", 0.95)

# ================================================================ 屏 3：回放——小王愣住“活谁来接？”；组长皱眉冒火“怎么没提前说？”
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
FY3 = cy + 450
S3 = 0.85
WG3, ZH3, LI3 = (cx - 130, FY3), (cx + 330, FY3), (cx - 470, FY3, 0.75)
k_ppl3 = 0
k_wow = kq(j, wt(4, 1, 0.1), 1)
k_wb = nx(j, wt(4, 1, 0.65), k_wow)
k_fr = nx(j, wt(5, 0, 0.4), k_wb)
k_lb = nx(j, wt(5, 1, 0.35), k_fr)
k_sw = nx(j, wt(5, 1, 0.95), k_lb)
L.note("!")


def T2():
    """回放开始的时刻（第 2 屏第 0 拍）；排期在 finish() 后才定，所以现算。"""
    return tb(2, k_bd)


def badge3(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 400, cy - 470, sc):
        badge(c, cx - 400, cy - 470, "replay", timecode=timecode(T, T2()))
    return None


ev(j, k_ppl3, pop_fn(j, k_ppl3, badge3))


def meeting3(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx + 120, FY3, sc):
        wx, wy = WG3
        jump = 30 * abs(math.sin((T - tb(3, k_wow)) * 10)) * math.exp(-(T - tb(3, k_wow)) * 4) if T >= tb(3, k_wow) else 0
        wow = T >= tb(3, k_wow)
        hx, hy = head_of(wx, wy, S3)
        wy -= SIT
        draw_wang(c, wx, wy - jump, S3, mood="o" if wow else "smile",
                  lh=(wx - 100 * S3, hy - 30 * S3 - jump) if wow else None,
                  rh=(wx + 100 * S3, hy - 30 * S3 - jump) if wow else None)
        zx, zy = ZH3
        zy -= SIT
        draw_leader(c, zx, zy, S3, head_dx=-6)
        hx, hy = head_of(zx, zy, S3)
        if T >= tb(3, k_fr):
            g = clamp01((T - tb(3, k_fr)) / 0.15)
            brows(c, hx - 6, hy, S3, g)
            puff(c, hx, hy - 90, T - tb(3, k_fr))
        meeting_table(c, cx + 120, FY3, 860)
        for x in (wx, zx):
            box(c, x, FY3 - 50, 90, 60, "#FFFFFF", GRAY, 4, 6)
    x, y, s = LI3
    hx, hy = head_of(x, y, s)
    sw_ = T >= tb(3, k_sw)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad" if sw_ else "flat")
        if sw_:
            sweat(c, hx + 60 * s, hy - 20 * s + 8 * math.sin(T * 5), 1.0)
    return None


ev(j, k_ppl3, pop_fn(j, k_ppl3, meeting3), "wood_low", 0.7)


def wow3(c, kk, T, cx=cx, cy=cy):
    t0 = tb(3, k_wow)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    with K.at(c, cx - 10, cy + 70, 8, sc):
        K.text(c, "!", 0, 0, 150, "black", RED)
    return None


ev(j, k_wow, wow3, "rim", 0.85)
ev(j, k_wb, L.pop_bubble("活谁来接？", cx - 60, cy - 90, j, k_wb, 64, BLACK, tail=-1), "pop", 0.7)
b.hit(j, k_fr, "tom", 0.8, "组长皱眉冒火")
ev(j, k_lb, L.pop_bubble("怎么没提前说？", cx + 255, cy - 335, j, k_lb, 62, RED, tail=1), "pop", 0.75)
b.hit(j, k_sw, "wood_high", 0.6, "小李冒汗")

# ================================================================ 屏 4：回放暂停——方案打勾；时间轴“会前”空着，“会上”两人都冒感叹号，“第一次听到”砸下
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_ps = 0
k_doc4 = kq(j, wt(6, 0, 0.25), 1)
k_ck4 = nx(j, wt(6, 0, 0.95), k_doc4)
k_tl = nx(j, wt(6, 1, 0.1), k_ck4)
k_h1 = nx(j, wt(6, 1, 0.5), k_tl)
k_h2 = k_h1 + 1
k_sl = nx(j, wt(6, 1, 0.85), k_h2)
TL_Y = cy + 330
L.note("会前", "会上", "第一次听到", "？")


def badge4(c, kk, T, cx=cx, cy=cy):
    t0 = tb(4, k_ps)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    with K.at(c, cx - 400, cy - 470, -3, sc):
        badge(c, 0, 0, "pause", timecode=timecode(tb(4, 0), T2()))
    return None


ev(j, k_ps, badge4, "rim", 0.8)


def doc4(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 320, cy - 150
    with at_pop(c, x, y, sc):
        box(c, x, y, 300, 360, "#FFFFFF", BLACK, 7, 8)
        K.text(c, "方案", x, y - 120, 60, "hand", BLACK)
        for r in range(4):
            C.line(c, (x - 100, y - 40 + r * 50), (x + 100 - (r % 2) * 50, y - 40 + r * 50), GRAY, 7)
        if T >= tb(4, k_ck4):
            part, _ = wb.partial(check(x + 90, y + 120, 80), clamp01((T - tb(4, k_ck4)) / 0.3))
            c.drawPath(part, wb.marker(GREEN, 16))
    return None


ev(j, k_doc4, pop_fn(j, k_doc4, doc4), "wood_high", 0.7)
b.hit(j, k_ck4, "pop", 0.7, "方案打勾")
TICK_A, TICK_B = cx - 280, cx + 250


def line4(c, kk, T, cx=cx, cy=cy):
    t0 = tb(4, k_tl)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.6))
    x0, x1 = cx - 520, cx + 530
    xe = lerp(x0, x1, f)
    C.line(c, (x0, TL_Y), (xe, TL_Y), BLACK, 10)
    if f > 0.97:
        C.line(c, (x1, TL_Y), (x1 - 34, TL_Y - 24), BLACK, 10)
        C.line(c, (x1, TL_Y), (x1 - 34, TL_Y + 24), BLACK, 10)
    for x, s_, col in ((TICK_A, "会前", GRAY), (TICK_B, "会上", RED)):
        if xe >= x:
            g = pop_scale(T - t0 - 0.6 * (x - x0) / (x1 - x0))
            C.line(c, (x, TL_Y - 24), (x, TL_Y + 24), col, 10)
            with K.at(c, x, TL_Y + 80, 0, g):
                K.text(c, s_, 0, 0, 64, "hand", col)
    if xe >= TICK_A:
        g = pop_scale(T - t0 - 0.3)
        with K.at(c, TICK_A, TL_Y - 150, 0, g):
            p = K.paint(GRAY, 1.0, 6)
            p.setPathEffect(skia.DashPathEffect.Make([16, 12], 0))
            c.drawCircle(0, 0, 80, p)
            K.text(c, "？", 0, 4, 80, "hand", GRAY)
    return None


ev(j, k_tl, line4, "wood_low", 0.7)


def heads4(c, kk, T, cx=cx, cy=cy):
    for n, (who, x) in enumerate((("wang", TICK_B - 120), ("leader", TICK_B + 130))):
        k_ = (k_h1, k_h2)[n]
        sc = pop_scale(T - tb(4, k_))
        if sc <= 0:
            continue
        y = TL_Y - 150
        with at_pop(c, x, y, sc):
            avatar(c, who, x, y, 1.1, "o")
            K.text(c, "!", x + 70, y - 70, 90, "black", RED)
    return None


ev(j, k_h1, heads4, "pop", 0.7)
b.hit(j, k_h2, "pop", 0.7, "组长头像冒感叹号")
ev(j, k_sl, L.slam_text("第一次听到", cx + 250, cy - 150, 84, RED, j, k_sl, rot=-4), "kick", 0.9)
b.shots[j].shake = [(k_sl, 9.0)]

# ================================================================ 屏 5：“会前沟通”（小字 nemawashi）；移树——铲子绕着树根松土三下
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_card = 0
k_nm = kq(j, wt(7, 0, 0.6), 1)
k_hq = nx(j, wt(7, 1, 0.75), k_nm)
k_tree = nx(j, wt(8, 0, 0.5), k_hq)
k_dig = [nx(j, wt(8, 1, 0.1), k_tree)]
k_dig += [k_dig[0] + 1, k_dig[0] + 2]
GY5 = cy + 330
L.note("nemawashi", "会前沟通", "移树")


def card5(c, sc, T, cx=cx, cy=cy):
    x, y = cx, cy - 390
    with at_pop(c, x, y, sc):
        box(c, x, y, 820, 270, "#FFFFFF", RED, 8, 24)
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 395, y - 120, 790, 240), 16, 16, wb.marker(RED, 3))
        nm = pop_scale(T - tb(5, k_nm))
        if nm > 0:
            with K.at(c, x, y + 85, 0, nm):
                K.text(c, "nemawashi", 0, 0, 50, "sans_medium", GRAY)
    return None


ev(j, k_card, pop_fn(j, k_card, card5), "wood_high", 0.7)
b.hit(j, k_nm, "pop", 0.6, "小字 nemawashi")
ev(j, k_hq, L.slam_text("会前沟通", cx, cy - 420, 118, RED, j, k_hq), "kick", 0.9)
b.shots[j].shake = [(k_hq, 9.0)]
DIG5 = [(cx - 250, GY5 + 70, -30), (cx, GY5 + 200, 0), (cx + 250, GY5 + 70, 30)]


def tree5(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, GY5, sc):
        C.line(c, (cx - 540, GY5 - 6), (cx + 540, GY5 - 6), SOIL_LINE, 8)
        tree(c, cx, GY5, 0.95)
        K.text(c, "移树", cx + 330, cy - 60, 70, "hand", LEAF_LINE)
    return None


ev(j, k_tree, pop_fn(j, k_tree, tree5), "wood_low", 0.75)


def dig5(c, kk, T, cx=cx, cy=cy):
    n = sum(1 for k_ in k_dig if T >= tb(5, k_))
    if n == 0:
        return None
    oval = skia.Rect.MakeXYWH(cx - 270, GY5 - 40, 540, 290)
    t_last = tb(5, k_dig[n - 1])
    f = (n - 1 + clamp01((T - t_last) / 0.35)) / 3
    arc = skia.Path()
    arc.addArc(oval, 180, 360 * f * 0.999)
    dashed_path(c, arc, SOIL_LINE, 9, 1.0, 26, 14)
    for i in range(n):
        dt = T - tb(5, k_dig[i])
        x, y, rot = DIG5[i]
        for m in range(5):
            if dt < 0.6:
                a = math.radians(-150 + m * 30)
                d = 30 + 120 * ease_out(clamp01(dt / 0.6))
                c.drawCircle(x + math.cos(a) * d, y - 40 + math.sin(a) * d * 0.6 + 80 * dt * dt, 9, K.paint(SOIL, 1 - dt / 0.6))
    x, y, rot = DIG5[n - 1]
    dip = 30 * math.exp(-(T - t_last) * 8) if T - t_last < 0.6 else 0.0
    shovel(c, x, y - 30 + dip, rot)
    return None


ev(j, k_dig[0], dig5, "wood_high", 0.8)
b.hit(j, k_dig[1], "wood_high", 0.8, "铲第二下")
b.hit(j, k_dig[2], "wood_low", 0.85, "铲第三下，土松开一圈")

# ================================================================ 屏 6：根松好了（打勾）；树连根抬起，沿弧线挪到新坑，长出新叶，“活了”
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
GY6 = cy + 300
A6, B6 = cx - 300, cx + 300
k_g6 = 0
k_ok6 = kq(j, wt(9, 0, 0.55), 1)
k_mv = nx(j, wt(9, 1, 0.05), k_ok6)
k_land = k_mv + 2
k_live = k_land + 1
L.note("活了")


def ground6(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, GY6, sc):
        C.line(c, (cx - 560, GY6 - 6), (cx + 560, GY6 - 6), SOIL_LINE, 8)
        for x in (A6, B6):
            c.drawOval(skia.Rect.MakeXYWH(x - 160, GY6 - 30, 320, 170), K.paint("#6E4A2A"))
            c.drawOval(skia.Rect.MakeXYWH(x - 160, GY6 - 30, 320, 170), wb.marker(SOIL_LINE, 6))
    return None


ev(j, k_g6, pop_fn(j, k_g6, ground6), "wood_low", 0.7)


def tree6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_g6) - 0.15)
    if sc <= 0:
        return None
    t0, t1 = tb(6, k_mv), tb(6, k_land)
    f = ease_in_out(clamp01((T - t0) / (t1 - t0))) if T >= t0 else 0.0
    x = lerp(A6, B6, f)
    y = GY6 - 260 * math.sin(math.pi * f)
    rot = 8 * math.sin(math.pi * f) * (1 if f < 0.5 else -1)
    bump = C.wobble(T - t1, 10, 26, 8) if T >= t1 else 0.0
    with K.at(c, x, y + bump, rot, sc):
        buds = clamp01((T - tb(6, k_live)) / 0.6) if T >= tb(6, k_live) else 0.0
        tree(c, 0, 0, 0.9, ball=1.0, buds=buds)
    if T >= tb(6, k_live):
        sparkle(c, B6, GY6 - 400, T - tb(6, k_live), LEAF_LINE, 10, 160, 300)
    return None


b.custom(j, k_g6, k_g6 + 0.3, tree6)


def ok6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_ok6)
    if T < t0:
        return None
    part, _ = wb.partial(check(A6 + 210, GY6 + 40, 60), clamp01((T - t0) / 0.3))
    fade = 1 - clamp01((T - tb(6, k_mv)) / 0.3) if T >= tb(6, k_mv) else 1.0
    if fade > 0:
        c.drawPath(part, wb.marker(GREEN, 14, fade))
    return None


ev(j, k_ok6, ok6, "wood_high", 0.7)


def arc6(c, kk, T, cx=cx, cy=cy):
    t0 = tb(6, k_mv)
    if T < t0:
        return None
    f = clamp01((T - t0) / (tb(6, k_land) - t0))
    p = skia.Path()
    p.moveTo(A6, GY6 - 560)
    p.quadTo(cx, GY6 - 820, B6, GY6 - 560)
    part, _ = wb.partial(p, max(0.001, f))
    dashed_path(c, part, GRAY, 6)
    if f >= 1:
        C.line(c, (B6, GY6 - 560), (B6 - 40, GY6 - 590), GRAY, 6)
        C.line(c, (B6, GY6 - 560), (B6 - 6, GY6 - 610), GRAY, 6)
    return None


b.custom(j, k_mv, k_mv + 0.3, arc6, sfx="shaker", gain=0.7)
b.hit(j, k_land, "tom", 0.85, "树落进新坑")
b.shots[j].shake = [(k_land, 7.0)]
ev(j, k_live, L.stamp("活了", cx - 300, cy - 420, 90, j, k_live, color=GREEN, rot=-6), "clap", 0.8)

# ================================================================ 屏 7：时间轴——决定很长（一个个问、几种办法比过），执行很短很快
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
BAR_Y = cy - 30
D0, D1, E0, E1 = cx - 540, cx + 250, cx + 290, cx + 540
k_book = 0
k_d = kq(j, wt(10, 1, 0.05), 1)
k_slow = nx(j, wt(10, 1, 0.8), k_d)
k_av = [nx(j, wt(10, 2, 0.1), k_slow)]
k_av += [k_av[0] + 1, k_av[0] + 2]
k_opt = nx(j, wt(10, 3, 0.1), k_av[2])
k_pick = k_opt + 1
k_e = nx(j, wt(11, 1, 0.05), k_pick)
k_fast = nx(j, wt(11, 1, 0.75), k_e)
L.note("决定", "执行", "慢", "快", "办法一", "办法二", "办法三")


def book7(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 420, cy - 450
    with at_pop(c, x, y, sc):
        p = wb.book(x, y, 220, 150)
        c.drawPath(p, K.paint("#FFFFFF"))
        c.drawPath(p, wb.marker(BLUE, 7))
    return None


ev(j, k_book, pop_fn(j, k_book, book7), "wood_high", 0.7)


def bar7(c, kk, T, cx=cx, cy=cy):
    t0 = tb(7, k_d)
    if T < t0:
        return None
    f = ease_in_out(clamp01((T - t0) / (tb(7, k_d + 2) - t0)))
    c.drawRoundRect(skia.Rect.MakeLTRB(D0, BAR_Y - 18, lerp(D0 + 20, D1, f), BAR_Y + 18), 18, 18, K.paint("#FBD7A8"))
    c.drawRoundRect(skia.Rect.MakeLTRB(D0, BAR_Y - 18, lerp(D0 + 20, D1, f), BAR_Y + 18), 18, 18, wb.marker(ORANGE, 6))
    g = pop_scale(T - t0 - 0.2)
    with K.at(c, (D0 + D1) / 2, BAR_Y + 80, 0, g):
        K.text(c, "决定", 0, 0, 64, "hand", ORANGE)
    t1 = tb(7, k_e)
    if T >= t1:
        fe = ease_out(clamp01((T - t1) / 0.25))
        xe = lerp(E0 + 10, E1, fe)
        c.drawRoundRect(skia.Rect.MakeLTRB(E0, BAR_Y - 18, xe, BAR_Y + 18), 18, 18, K.paint(GREEN_FILL))
        c.drawRoundRect(skia.Rect.MakeLTRB(E0, BAR_Y - 18, xe, BAR_Y + 18), 18, 18, wb.marker(GREEN, 6))
        for n in range(3):
            ax = xe - 40 - n * 50 + 18 * ((T * 4) % 1)
            if ax > E0 + 20:
                c.drawPath(P((ax - 14, BAR_Y - 30 - 20), (ax + 6, BAR_Y - 50 + 16), (ax - 14, BAR_Y - 50 + 32)),
                           wb.marker(GREEN, 6, 0.8))
        with K.at(c, (E0 + E1) / 2, BAR_Y + 80, 0, pop_scale(T - t1 - 0.15)):
            K.text(c, "执行", 0, 0, 64, "hand", GREEN)
    return None


b.custom(j, k_d, k_d + 0.3, bar7, sfx="wood_low", gain=0.7)


def snail(c, x, y, s=1.0):
    shell = skia.Path()
    shell.addCircle(x, y - 30 * s, 34 * s)
    c.drawPath(shell, K.paint("#FBD7A8"))
    c.drawPath(shell, wb.marker(ORANGE, 5))
    sp = skia.Path()
    sp.addArc(skia.Rect.MakeXYWH(x - 18 * s, y - 48 * s, 36 * s, 36 * s), 0, 300)
    c.drawPath(sp, wb.marker(ORANGE, 4))
    body = skia.Path()
    body.moveTo(x - 50 * s, y + 6 * s)
    body.lineTo(x + 40 * s, y + 6 * s)
    body.quadTo(x + 64 * s, y + 4 * s, x + 62 * s, y - 22 * s)
    body.quadTo(x + 44 * s, y - 14 * s, x + 30 * s, y - 6 * s)
    body.lineTo(x - 50 * s, y - 6 * s)
    body.close()
    c.drawPath(body, K.paint("#E8DCC8"))
    c.drawPath(body, wb.marker(BLACK, 5))
    C.line(c, (x + 55 * s, y - 18 * s), (x + 66 * s, y - 44 * s), BLACK, 4)
    c.drawCircle(x + 66 * s, y - 46 * s, 4 * s, K.paint(BLACK))


def slow7(c, kk, T, cx=cx, cy=cy):
    t0 = tb(7, k_slow)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    with K.at(c, cx - 170, cy - 450, -4, sc):
        K.text(c, "慢", 0, 0, 120, "hand", ORANGE)
    sx = lerp(cx - 30, cx + 10, clamp01((T - t0) / 6))
    with K.at(c, sx, cy - 420, 0, pop_scale(T - t0 - 0.1)):
        snail(c, 0, 0, 1.0)
    return None


ev(j, k_slow, slow7, "rim", 0.8)


def avatars7(c, kk, T, cx=cx, cy=cy):
    for n, who in enumerate(("wang", "leader", "boss")):
        sc = pop_scale(T - tb(7, k_av[n]))
        if sc <= 0:
            continue
        x, y = D0 + 130 + n * 250, BAR_Y - 130
        with at_pop(c, x, y, sc):
            avatar(c, who, x, y, 0.85)
            bx, by = x + 85, y - 62
            c.drawPath(P((bx - 26, by + 14), (bx - 44, by + 34), (bx - 10, by + 20), close=True), K.paint("#FFFFFF"))
            c.drawPath(P((bx - 26, by + 14), (bx - 44, by + 34), (bx - 10, by + 20)), wb.marker(BLACK, 5))
            c.drawOval(skia.Rect.MakeXYWH(bx - 42, by - 26, 84, 52), K.paint("#FFFFFF"))
            c.drawOval(skia.Rect.MakeXYWH(bx - 42, by - 26, 84, 52), wb.marker(BLACK, 5))
            for d in range(3):
                c.drawCircle(bx - 16 + d * 16, by, 5, K.paint(BLACK))
    return None


ev(j, k_av[0], avatars7, "pop", 0.65)
b.hit(j, k_av[1], "pop", 0.65, "又问一个人")
b.hit(j, k_av[2], "pop", 0.65, "再问一个人")
OPT7 = [(cx - 420, "办法一"), (cx - 170, "办法二"), (cx + 80, "办法三")]


def opts7(c, kk, T, cx=cx, cy=cy):
    t0 = tb(7, k_opt)
    for n, (x, s_) in enumerate(OPT7):
        sc = pop_scale(T - t0 - n * 0.12)
        if sc <= 0:
            continue
        y = cy + 290
        with at_pop(c, x, y, sc):
            picked = T >= tb(7, k_pick) and n == 1
            box(c, x, y, 210, 170, GREEN_FILL if picked else "#FFFFFF", GREEN if picked else GRAY, 6, 12)
            K.text(c, s_, x, y - 40, 46, "hand", BLACK)
            for r in range(2):
                C.line(c, (x - 60, y + 15 + r * 32), (x + 60 - r * 30, y + 15 + r * 32), GRAY, 6)
    if T >= tb(7, k_pick):
        part, _ = wb.partial(check(OPT7[1][0] + 70, cy + 370, 50), clamp01((T - tb(7, k_pick)) / 0.3))
        c.drawPath(part, wb.marker(GREEN, 12))
    return None


ev(j, k_opt, opts7, "wood_high", 0.7)
b.hit(j, k_pick, "pop", 0.7, "比完挑一个")
ev(j, k_fast, L.slam_text("快", cx + 415, cy - 400, 150, GREEN, j, k_fast, rot=-6), "kick", 0.9)
b.hit(j, k_e, "shaker", 0.75, "执行一下冲到头")
b.shots[j].shake = [(k_fast, 9.0)]

# ================================================================ 屏 8：会前小房间里吵完（打勾）；会上大家点头；“会前聊天 → 会上点头”
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
RL, RR, RY = cx - 290, cx + 290, cy - 80
k_rl = 0
k_ar = kq(j, wt(12, 0, 0.55), 1)
k_done = nx(j, wt(12, 1, 0.65), k_ar)
k_rr = nx(j, wt(13, 0, 0.0), k_done)
k_nod = nx(j, wt(13, 0, 0.75), k_rr)
k_link = nx(j, wt(13, 1, 0.55), k_nod)
L.note("会前", "会上", "吵完了", "会前聊天", "会上点头")


def room(c, x, y, title, col):
    box(c, x, y, 500, 520, "#FFFFFF", col, 7, 16)
    K.text(c, title, x, y - 320, 70, "hand", col)


def left8(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, RL, RY, sc):
        room(c, RL, RY, "会前", BLUE)
        fy = RY + 230
        argue = tb(8, k_ar) <= T < tb(8, k_done)
        jit = 4 * math.sin(T * 30) if argue else 0
        done = T >= tb(8, k_done)
        draw_li(c, RL - 110 + jit, fy, 0.55, "smile" if done else "sad")
        draw_wang(c, RL + 110 - jit, fy, 0.55, mood="smile" if done else "o")
    return None


ev(j, k_rl, pop_fn(j, k_rl, left8), "wood_low", 0.7)


def argue8(c, kk, T, cx=cx, cy=cy):
    t0, t1 = tb(8, k_ar), tb(8, k_done)
    sc = pop_scale(T - t0)
    if T >= t1:
        sc *= 1 - ease_in_out(clamp01((T - t1) / 0.25))
    if sc > 0:
        for n, (dx, dy) in enumerate(((-90, -10), (90, -60))):
            x, y = RL + dx, RY - 170 + dy
            with K.at(c, x, y, (-6, 6)[n] + 3 * math.sin(T * 20 + n), sc):
                pts = []
                for i in range(14):
                    a = 2 * math.pi * i / 14
                    r = (88 if i % 2 else 64)
                    pts.append((math.cos(a) * r * 1.2, math.sin(a) * r * 0.75))
                zz = P(*pts, close=True)
                c.drawPath(zz, K.paint("#FFFFFF"))
                c.drawPath(zz, wb.marker(RED if n else ORANGE, 6))
                c.drawPath(wb.scribble(0, 0, 70, 30, 5), wb.marker(RED if n else ORANGE, 5))
    if T >= t1:
        g = pop_scale(T - t1 - 0.1)
        with K.at(c, RL, RY - 180, 0, g):
            c.drawPath(check(-120, 0, 50), wb.marker(GREEN, 14))
            K.text(c, "吵完了", 40, 4, 66, "hand", GREEN)
    return None


ev(j, k_ar, argue8, "rim", 0.8)
b.shots[j].shake = [(k_ar, 6.0)]
b.hit(j, k_done, "wood_high", 0.75, "吵完了，打勾")


def right8(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, RR, RY, sc):
        room(c, RR, RY, "会上", GREEN)
        fy = RY + 230
        for n, (draw, dx) in enumerate(((draw_li, -140), (draw_wang, 0), (draw_leader, 140))):
            nod = T >= tb(8, k_nod)
            dy = 6 * abs(math.sin((T - tb(8, k_nod)) * 6 + n)) if nod else 0
            x = RR + dx
            c.save()
            c.translate(0, dy)
            if draw is draw_leader:
                draw(c, x, fy - 60, 0.5, mood="smile" if nod else "frown")
            elif draw is draw_wang:
                draw(c, x, fy - 60, 0.5, mood="smile" if nod else "flat")
            else:
                draw(c, x, fy - 60, 0.5, "smile" if nod else "flat")
            c.restore()
            if nod:
                g = pop_scale(T - tb(8, k_nod) - n * 0.1)
                with K.at(c, x, fy - 60 - 0.5 * 290 - 75, 0, g):
                    c.drawPath(check(0, 0, 26), wb.marker(GREEN, 9))
        meeting_table(c, RR, fy + 20, 440, 90)
    return None


ev(j, k_rr, pop_fn(j, k_rr, right8), "wood_low", 0.7)
b.hit(j, k_nod, "pop", 0.7, "会上大家点头")


def link8(c, kk, T, cx=cx, cy=cy):
    t0 = tb(8, k_link)
    if T < t0:
        return None
    y = cy + 380
    g1 = pop_scale(T - t0)
    with K.at(c, RL, y, 0, g1):
        K.text(c, "会前聊天", 0, 0, 66, "hand", BLUE)
    f = clamp01((T - t0 - 0.15) / 0.35)
    if f > 0:
        part, _ = wb.partial(wb.arrow((cx - 120, y), (cx + 120, y), 0.0, 32), f)
        c.drawPath(part, wb.marker(BLACK, 8))
    g2 = pop_scale(T - t0 - 0.45)
    with K.at(c, RR, y, 0, g2):
        K.text(c, "会上点头", 0, 0, 66, "hand", GREEN)
    return None


ev(j, k_link, link8, "clap", 0.8)

# ================================================================ 屏 9：改写——“回放”被划掉，“✎ 改写”砸下；会前一天茶水间，小李问小王，圈出最怕的一步
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_old = 0
k_x9 = kq(j, wt(14, 1, 0.05), 1)
k_rw = nx(j, wt(14, 1, 0.7), k_x9)
k_cal9 = nx(j, wt(15, 0, 0.3), k_rw)
k_ppl9 = nx(j, wt(15, 1, 0.05), k_cal9)
k_ask = nx(j, wt(15, 1, 0.4), k_ppl9)
k_circ = nx(j, wt(15, 1, 0.82), k_ask)
FY9 = cy + 460
LI9, WG9 = (cx - 330, FY9, 0.85), (cx + 330, FY9, 0.85)
CARD9 = (cx, cy - 190, 540, 250)
L.note("会前一天", "最怕哪一步？", "新流程")


def old9(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 410, cy - 470, sc):
        badge(c, cx - 410, cy - 470, "replay", alpha=0.55 if T >= tb(9, k_x9) else 1.0)
    return None


ev(j, k_old, pop_fn(j, k_old, old9), "wood_high", 0.7)
b.path(j, k_x9, k_x9 + 0.35, P((cx - 550, cy - 440), (cx - 270, cy - 500)), RED, 12, sfx="wood_high", gain=0.75)


def rw9(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k_rw)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    with K.at(c, cx - 110, cy - 470, -3, sc):
        badge(c, 0, 0, "rewrite")
    return None


ev(j, k_rw, rw9, "kick", 0.9)
b.shots[j].shake = [(k_rw, 8.0)]


def cal9(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 400, cy - 460
    with at_pop(c, x, y, sc):
        calendar(c, x, y, 260, 210, "会前一天", rows=2)
    return None


ev(j, k_cal9, pop_fn(j, k_cal9, cal9), "pop", 0.7)


def scene9(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, FY9, sc):
        x, y, s = LI9
        hx, hy = head_of(x, y, s)
        draw_li(c, x, y, s, "smile")
        x, y, s = WG9
        hx, hy = head_of(x, y, s)
        point = T >= tb(9, k_circ)
        draw_wang(c, x, y, s, mood="smile" if point else "flat",
                  lh=(x - 120 * s, hy - 60 * s) if point else None)
        # 高脚小圆桌 + 两杯咖啡
        c.drawRoundRect(skia.Rect.MakeXYWH(cx - 150, FY9 - 230, 300, 26), 12, 12, K.paint(WOOD))
        c.drawRoundRect(skia.Rect.MakeXYWH(cx - 150, FY9 - 230, 300, 26), 12, 12, wb.marker(WOOD_LINE, 6))
        C.line(c, (cx, FY9 - 204), (cx, FY9), WOOD_LINE, 10)
        C.line(c, (cx - 70, FY9), (cx + 70, FY9), WOOD_LINE, 10)
        mug(c, cx - 70, FY9 - 230, 1.0, ORANGE, "#FDE3C8")
        mug(c, cx + 70, FY9 - 230, 1.0, BLUE, "#DCEAFB")
    x, y, w, h = CARD9
    with at_pop(c, x, y, sc):
        plan_card(c, x, y, w, h, "新流程")
    return None


ev(j, k_ppl9, pop_fn(j, k_ppl9, scene9), "wood_low", 0.7)
ev(j, k_ask, L.pop_bubble("最怕哪一步？", cx - 330, cy + 40, j, k_ask, 58, BLACK, tail=-1), "pop", 0.7)
_sx, _sy = step_xy(*CARD9, 1)
_ov = skia.Path()
_ov.addOval(skia.Rect.MakeXYWH(_sx - 80, _sy - 62, 160, 124))
b.path(j, k_circ, k_circ + 0.45, _ov, RED, 9, sfx="wood_high", gain=0.75)

# ================================================================ 屏 10：小李走到组长桌边“哪里有风险？”；组长指出第三步，画上警示三角
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
FY10 = cy + 460
ZH10 = (cx + 260, FY10, 0.9)
LI10 = (cx - 300, FY10, 0.9)
CARD10 = (cx + 20, cy - 230, 560, 250)
k_desk = 0
k_li10 = kq(j, wt(16, 0, 0.1), 1)
k_bub10 = nx(j, wt(16, 1, 0.1), k_li10)
k_tri = nx(j, wt(16, 1, 0.85), k_bub10)
L.note("哪里有风险？", "新流程")


def badge10(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 420, cy - 480, sc):
        badge(c, cx - 420, cy - 480, "rewrite")
    return None


ev(j, k_desk, pop_fn(j, k_desk, badge10))


def desk10(c, sc, T, cx=cx, cy=cy):
    x, y, s = ZH10
    with at_pop(c, x, y, sc):
        point = T >= tb(10, k_tri)
        hx, hy = head_of(x, y, s)
        g = ease_out(clamp01((T - tb(10, k_tri)) / 0.25)) if point else 0.0
        rh = (lerp(x + 70 * s, x - 40 * s, g), lerp(hy + 170 * s, hy - 150 * s, g))
        draw_leader(c, x, y, s, rh=rh, mood="smile" if point else "frown", head_dx=-8)
        if point:
            C.line(c, rh, (rh[0] - 30 * g, rh[1] - 40 * g), RED, 8)
        c.drawRect(skia.Rect.MakeXYWH(x - 250, y - 120, 500, 120), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(x - 250, y - 120, 500, 120), wb.marker(WOOD_LINE, 7))
        C.line(c, (x - 270, y - 120), (x + 270, y - 120), WOOD_LINE, 12)
        mug(c, x + 170, y - 126, 0.9, GREEN, GREEN_FILL)
    cx_, cy_, w, h = CARD10
    with at_pop(c, cx_, cy_, sc):
        plan_card(c, cx_, cy_, w, h, "新流程")
        sx, sy = step_xy(*CARD10, 1)
        c.drawOval(skia.Rect.MakeXYWH(sx - 80, sy - 62, 160, 124), wb.marker(RED, 7))
    return None


ev(j, k_desk, pop_fn(j, k_desk, desk10), "wood_low", 0.7)


def li10(c, kk, T, cx=cx, cy=cy):
    t0 = tb(10, k_li10)
    if T < t0:
        return None
    x0, y, s = LI10
    x, dy, moving = walk(T, t0, 0.8, x0 - 330, x0, 14, 3.5)
    draw_li(c, x, y + dy, s, "flat" if T < tb(10, k_tri) else "smile")
    return None


b.custom(j, k_li10, k_li10 + 0.3, li10, sfx="wood_high", gain=0.6)
ev(j, k_bub10, L.pop_bubble("哪里有风险？", cx - 290, cy + 30, j, k_bub10, 58, BLACK, tail=-1), "pop", 0.7)


def tri10(c, kk, T, cx=cx, cy=cy):
    t0 = tb(10, k_tri)
    if T < t0:
        return None
    sx, sy = step_xy(*CARD10, 2)
    g = C.slam_scale(T - t0)
    if g > 0:
        with K.at(c, sx + 50, sy - 52, 0, g):
            warn(c, 0, 0, 40)
    return None


ev(j, k_tri, tri10, "rim", 0.85)

# ================================================================ 屏 11：改写——第二天同一张会议桌：投影上多了两条带头像的意见，十分钟，“通过”
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
FY11 = cy + 450
TAB11 = (cx + 250, 640)
k_m11 = 0
k_scr = kq(j, wt(17, 0, 0.5), 1)
k_o1 = nx(j, wt(17, 1, 0.3), k_scr)
k_o2 = k_o1 + 1
k_clk = nx(j, wt(17, 2, 0.0), k_o2)
k_pass = nx(j, wt(17, 2, 0.8), k_clk)
L.note("换新流程", "人手排好", "先试一组", "10分钟", "第二天")


def badge11(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 400, cy - 470, sc):
        badge(c, cx - 400, cy - 470, "rewrite")
        box(c, cx - 140, cy - 470, 200, 80, NOTE_FILL, "#C9A227", 5, 10)
        K.text(c, "第二天", cx - 140, cy - 468, 50, "hand", BLACK)
    return None


ev(j, k_m11, pop_fn(j, k_m11, badge11))


def meeting11(c, sc, T, cx=cx, cy=cy):
    ok = T >= tb(11, k_pass)
    with at_pop(c, TAB11[0], FY11, sc):
        for n, (draw, x) in enumerate(((draw_wang, cx + 110), (draw_leader, cx + 390))):
            dy = 6 * abs(math.sin((T - tb(11, k_pass)) * 6 + n)) if ok else 0
            c.save()
            c.translate(0, dy)
            if draw is draw_wang:
                draw(c, x, FY11 - SIT, 0.8, mood="smile")
            else:
                draw(c, x, FY11 - SIT, 0.8, mood="smile" if ok else "frown")
            c.restore()
            if ok:
                g = pop_scale(T - tb(11, k_pass) - 0.2 - n * 0.12)
                with K.at(c, x + 70, FY11 - SIT - 0.8 * 290 - 40, 0, g):
                    c.drawPath(check(0, 0, 30), wb.marker(GREEN, 10))
        meeting_table(c, TAB11[0], FY11, TAB11[1])
        for x in (cx + 110, cx + 390):
            box(c, x, FY11 - 50, 90, 60, "#FFFFFF", GRAY, 4, 6)
    x, y, s = cx - 380, FY11, 0.9
    hx, hy = head_of(x, y, s)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile", rh=(x + 120 * s, hy - 50 * s))
    return None


ev(j, k_m11, pop_fn(j, k_m11, meeting11), "wood_low", 0.7)
SCR11 = (cx + 70, cy - 220)


def screen11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_scr))
    if sc <= 0:
        return None
    x, y = SCR11
    with K.at(c, x, y, -2, sc):
        C.line(c, (-300, -175), (300, -175), BLACK, 12)
        box(c, 0, 0, 580, 330, "#FFFFFF", BLACK, 7, 8)
        K.text(c, "换新流程", 0, -105, 72, "hand", RED)
        for n, (who, s_) in enumerate((("wang", "人手排好"), ("leader", "先试一组"))):
            k_ = (k_o1, k_o2)[n]
            g = pop_scale(T - tb(11, k_))
            if g <= 0:
                continue
            yy = -12 + n * 112
            with K.at(c, -170, yy, 0, g):
                c.drawCircle(0, 0, 44, K.paint(NOTE_FILL))
                avatar(c, who, 0, 4, 0.75)
            with K.at(c, 60, yy, 0, g):
                K.text(c, s_, 0, 4, 58, "hand", BLACK)
    return None


ev(j, k_scr, screen11, "pop", 0.7)
b.hit(j, k_o1, "wood_high", 0.7, "小王的意见写进方案")
b.hit(j, k_o2, "wood_high", 0.7, "组长的意见写进方案")


def clock11(c, kk, T, cx=cx, cy=cy):
    t0 = tb(11, k_clk)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx - 400, cy - 160
    f = ease_out(clamp01((T - t0) / 0.6)) / 6
    with K.at(c, x, y, 0, sc):
        clock_face(c, 0, 0, 95, f)
        K.text(c, "10分钟", 0, 145, 56, "hand", GREEN)
    return None


ev(j, k_clk, clock11, "pop", 0.7)
ev(j, k_pass, L.stamp("通过", cx + 400, cy + 25, 84, j, k_pass, color=GREEN, rot=-8), "kick", 0.9)
b.shots[j].shake = [(k_pass, 9.0)]

# ================================================================ 屏 12：想换岗——私下跟领导喝咖啡聊（打勾）vs 周会上突然举手（打叉）
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
PL, PR, PY = cx - 285, cx + 285, cy - 30
k_fr12 = 0
k_lc = kq(j, wt(19, 0, 0.05), 1)
k_want = nx(j, wt(19, 0, 0.75), k_lc)
k_ok12 = nx(j, wt(19, 1, 0.8), k_want)
k_rc = nx(j, wt(19, 2, 0.1), k_ok12)
k_x12 = nx(j, wt(19, 2, 0.8), k_rc)
L.note("私下聊", "周会上提", "想换岗", "周会")


def frames12(c, sc, T, cx=cx, cy=cy):
    for x, s_, col in ((PL, "私下聊", GREEN), (PR, "周会上提", RED)):
        with at_pop(c, x, PY, sc):
            box(c, x, PY, 520, 820, "#FFFFFF", col, 7, 18)
            K.text(c, s_, x, PY - 340, 62, "hand", col)
    return None


ev(j, k_fr12, pop_fn(j, k_fr12, frames12), "wood_high", 0.7)


def left12(c, sc, T, cx=cx, cy=cy):
    fy = PY + 340
    with at_pop(c, PL, fy, sc):
        draw_li(c, PL - 140, fy, 0.62, "smile")
        draw_boss(c, PL + 140, fy, 0.62, mood="smile")
        c.drawOval(skia.Rect.MakeXYWH(PL - 110, fy - 150, 220, 40), K.paint(WOOD))
        c.drawOval(skia.Rect.MakeXYWH(PL - 110, fy - 150, 220, 40), wb.marker(WOOD_LINE, 6))
        C.line(c, (PL, fy - 110), (PL, fy), WOOD_LINE, 9)
        mug(c, PL - 45, fy - 132, 0.8, ORANGE, "#FDE3C8")
        mug(c, PL + 45, fy - 132, 0.8, BLUE, "#DCEAFB")
    return None


ev(j, k_lc, pop_fn(j, k_lc, left12), "wood_low", 0.7)
ev(j, k_want, L.pop_bubble("想换岗", PL - 90, PY + 30, j, k_want, 56, BLACK, tail=-1), "pop", 0.7)


def ok12(c, kk, T, cx=cx, cy=cy):
    t0 = tb(12, k_ok12)
    if T < t0:
        return None
    part, _ = wb.partial(check(PL + 10, PY - 190, 80), clamp01((T - t0) / 0.3))
    c.drawPath(part, wb.marker(GREEN, 16))
    return None


ev(j, k_ok12, ok12, "wood_high", 0.75)


def right12(c, sc, T, cx=cx, cy=cy):
    fy = PY + 340
    with at_pop(c, PR, fy, sc):
        box(c, PR - 130, PY - 170, 180, 110, SKY, GRAY, 5, 8)
        K.text(c, "周会", PR - 130, PY - 168, 46, "hand", GRAY)
        draw_boss(c, PR - 120, fy - 40, 0.55, mood="o")
        for n in range(4):
            hx_ = PR - 200 + n * 110
            c.drawCircle(hx_, fy + 10, 34, K.paint(GRAY_FILL))
            c.drawCircle(hx_, fy + 10, 34, wb.marker(GRAY, 5))
        x = PR + 160
        hx, hy = head_of(x, fy - 40, 0.55)
        up = clamp01((T - tb(12, k_rc)) / 0.2)
        draw_li(c, x, fy - 40, 0.55, "flat", rh=(lerp(x + 40, x + 50, up), lerp(hy + 90, hy - 90, up)))
    return None


ev(j, k_rc, pop_fn(j, k_rc, right12), "wood_low", 0.7)


def x12(c, kk, T, cx=cx, cy=cy):
    t0 = tb(12, k_x12)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    with K.at(c, PR + 150, PY - 170, 0, sc):
        c.drawPath(cross(0, 0, 70), wb.marker(RED, 18))
    return None


ev(j, k_x12, x12, "rim", 0.85)
b.shots[j].shake = [(k_x12, 7.0)]

# ================================================================ 屏 13：周末出去玩——先问家里人、圈出周末（打勾）；票先订好（打叉）
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
FY13 = cy + 460
LI13, MOM13 = (cx - 360, FY13, 0.85), (cx + 60, FY13, 0.85)
CAL13 = (cx - 190, cy - 270, 380, 300)
k_tab13 = 0
k_cal13 = kq(j, wt(20, 0, 0.55), 1)
k_ring = nx(j, wt(20, 1, 0.55), k_cal13)
k_tk = nx(j, wt(20, 2, 0.15), k_ring)
k_x13 = nx(j, wt(20, 2, 0.8), k_tk)
L.note("周末", "票")


def table13(c, sc, T, cx=cx, cy=cy):
    ring = T >= tb(13, k_ring)
    with at_pop(c, cx - 150, FY13, sc):
        x, y, s = LI13
        hx, hy = head_of(x, y, s)
        draw_li(c, x, y, s, "smile", rh=(x + 110 * s, hy - 60 * s) if ring else None)
        x, y, s = MOM13
        draw_mom(c, x, y, s, mood="smile" if ring else "flat")
        c.drawRect(skia.Rect.MakeXYWH(cx - 470, FY13 - 170, 640, 30), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(cx - 470, FY13 - 170, 640, 30), wb.marker(WOOD_LINE, 6))
        for x in (cx - 430, cx + 130):
            C.line(c, (x, FY13 - 140), (x, FY13), WOOD_LINE, 9)
        c.drawOval(skia.Rect.MakeXYWH(cx - 210, FY13 - 196, 120, 30), K.paint("#FFFFFF"))
        c.drawOval(skia.Rect.MakeXYWH(cx - 210, FY13 - 196, 120, 30), wb.marker(GRAY, 4))
    return None


ev(j, k_tab13, pop_fn(j, k_tab13, table13), "wood_low", 0.7)


def cal13(c, sc, T, cx=cx, cy=cy):
    x, y, w, h = CAL13
    ring = T >= tb(13, k_ring)
    with at_pop(c, x, y, sc):
        cell = calendar(c, x, y, w, h, "周末", rows=3, ring=(1, (5, 6)) if ring else None)
    return None


ev(j, k_cal13, pop_fn(j, k_cal13, cal13), "pop", 0.7)


def ring13(c, kk, T, cx=cx, cy=cy):
    t0 = tb(13, k_ring)
    if T < t0:
        return None
    x, y, w, h = CAL13
    gx0, gy0 = x - w / 2 + w * 0.08, y - h / 2 + h * 0.34
    cw, ch = w * 0.84 / 7, h * 0.6 / 3
    ox, oy = gx0 + cw * 6, gy0 + ch * 1.5
    oval = skia.Path()
    oval.addOval(skia.Rect.MakeXYWH(ox - cw * 1.25, oy - ch * 0.75, cw * 2.5, ch * 1.5))
    part, _ = wb.partial(oval, clamp01((T - t0) / 0.35))
    c.drawPath(part, wb.marker(GREEN, 8))
    if T - t0 > 0.35:
        g = pop_scale(T - t0 - 0.35)
        with K.at(c, x + w / 2 + 70, y - 20, 0, g):
            c.drawPath(check(0, 0, 50), wb.marker(GREEN, 13))
    return None


ev(j, k_ring, ring13, "wood_high", 0.75)


def ticket13(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 360, cy - 120
    with K.at(c, x, y, 6, sc):
        p = skia.Path()
        p.addRoundRect(skia.Rect.MakeXYWH(-130, -80, 260, 160), 14, 14)
        for sy in (-1, 1):
            notch = skia.Path()
            notch.addCircle(60, sy * 80, 18)
            p = skia.Op(p, notch, skia.PathOp.kDifference_PathOp)
        c.drawPath(p, K.paint("#FDE3C8"))
        c.drawPath(p, wb.marker(ORANGE, 6))
        dashed(c, (60, -60), (60, 60), ORANGE, 4, 1.0, 10, 8)
        K.text(c, "票", -40, 4, 76, "hand", ORANGE)
        c.drawPath(P((92, -24), (110, 0), (92, 24)), wb.marker(ORANGE, 5))
    return None


ev(j, k_tk, pop_fn(j, k_tk, ticket13), "pop", 0.7)


def x13(c, kk, T, cx=cx, cy=cy):
    t0 = tb(13, k_x13)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    with K.at(c, cx + 360 + 150, cy - 120 - 95, 0, sc):
        c.drawCircle(0, 0, 58, K.paint("#FFFFFF"))
        c.drawCircle(0, 0, 58, wb.marker(RED, 8))
        c.drawPath(cross(0, 0, 30), wb.marker(RED, 14))
    return None


ev(j, k_x13, x13, "rim", 0.85)
b.shots[j].shake = [(k_x13, 7.0)]

# ================================================================ 屏 14：小李看着一长串名字发愁；路过同事“搞关系？”；“三步”砸下
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
LI14 = (cx - 360, cy + 470, 0.95)
LIST14 = (cx - 90, cy + 20)
NAMES14 = ["小王", "组长", "领导", "财务", "隔壁组", "……"]
k_li14 = 0
k_tired = kq(j, wt(21, 2, 0.3), 1)
k_gos = nx(j, wt(21, 3, 0.35), k_tired)
k_three = nx(j, wt(22, 1, 0.75), k_gos)
L.note(*NAMES14, "搞关系？", "三步")


def li14(c, sc, T, cx=cx, cy=cy):
    x, y, s = LI14
    hx, hy = head_of(x, y, s)
    tired = T >= tb(14, k_tired)
    sq = lerp(1.0, 0.92, ease_out(clamp01((T - tb(14, k_tired)) / 0.2))) if tired else 1.0
    lx, ly = LIST14
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad" if tired else "flat", squash=sq, rh=(lx - 122, ly + 150))
        if tired:
            sweat(c, hx + 60 * s, y - (y - hy) * sq - 30 + 8 * math.sin(T * 5), 1.2)
        # 长长的名单
        box(c, lx, ly, 240, 520, "#FFFFFF", BLACK, 6, 6)
        for n, s_ in enumerate(NAMES14):
            yy = ly - 200 + n * 80
            c.drawCircle(lx - 80, yy, 9, K.paint(GRAY))
            K.text(c, s_, lx + 10, yy + 2, 46, "hand", BLACK)
        c.drawOval(skia.Rect.MakeXYWH(lx - 130, ly + 250, 260, 50), K.paint("#FFFFFF"))
        c.drawOval(skia.Rect.MakeXYWH(lx - 130, ly + 250, 260, 50), wb.marker(BLACK, 6))
    return None


ev(j, k_li14, pop_fn(j, k_li14, li14), "wood_low", 0.7)
b.hit(j, k_tired, "wood_high", 0.6, "小李发愁冒汗")


def gossip14(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx + 360, cy + 470, sc):
        draw_gossip(c, cx + 260, cy + 470, 0.65, 1)
        draw_gossip(c, cx + 450, cy + 470, 0.65, -1)
    return None


ev(j, k_gos, pop_fn(j, k_gos, gossip14), "pop", 0.7)
b.custom(j, k_gos + 0.4, k_gos + 0.7, L.pop_bubble("搞关系？", cx + 330, cy + 0, j, k_gos + 0.4, 58, GRAY, tail=1))
ev(j, k_three, L.slam_text("三步", cx + 330, cy - 400, 140, RED, j, k_three, rot=-5), "kick", 0.9)
b.shots[j].shake = [(k_three, 10.0)]

# ================================================================ 屏 15–17：三步做法（右上角三个步骤圆点）


def steps_row(jj, k0, active, sfx="wood_high"):
    """右上角三个步骤圆点：第 active 个（0 起）在 k0 拍变红放大。"""
    x0, y0 = R[jj][0] + 60, R[jj][1] - 440

    def fn(c, kk, T):
        for i in range(3):
            sc = pop_scale(T - tb(jj, 0) - i * 0.1)
            if sc <= 0:
                continue
            on = i == active and T >= tb(jj, k0)
            g = 1 + 0.25 * pop_scale(T - tb(jj, k0)) if on else 1.0
            x = x0 + 120 + i * 140
            with K.at(c, x, y0, 0, sc * g):
                c.drawCircle(0, 0, 50, K.paint(RED if on else "#FFFFFF"))
                c.drawCircle(0, 0, 50, wb.marker(RED if on else GRAY, 7))
                K.text(c, str(i + 1), 0, 4, 60, "hand", "#FFFFFF" if on else GRAY)
        return None
    b.custom(jj, k0, k0 + 0.3, fn, sfx=sfx, gain=0.7)


L.note("1", "2", "3")

# ---------------------------------------------------------------- 屏 15：做法一——名单上逐个打勾，每个勾旁一个十分钟小钟
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
steps_row(j, 0, 0)
LI15 = (cx - 450, cy + 470, 0.8)
k_list = kq(j, wt(23, 1, 0.1), 1)
k_rows = [nx(j, wt(23, 2, 0.1), k_list)]
k_rows += [k_rows[0] + 1, k_rows[0] + 2]
ROWS15 = [("wang", "小王"), ("leader", "组长"), ("boss", "领导")]
L.note("会被影响的人", "小王", "组长", "领导", "10分钟")


def li15(c, sc, T, cx=cx, cy=cy):
    x, y, s = LI15
    hx, hy = head_of(x, y, s)
    point = T >= tb(15, k_rows[0])
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if point else "flat", rh=(x + 110 * s, hy - 40 * s) if point else None)
    return None


ev(j, 0, pop_fn(j, 0, li15))


def list15(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 60, cy + 10
    with at_pop(c, x, y, sc):
        box(c, x, y, 760, 600, "#FFFFFF", BLACK, 7, 12)
        K.text(c, "会被影响的人", x, y - 230, 62, "hand", BLUE)
        C.line(c, (x - 300, y - 180), (x + 300, y - 180), BLUE, 5)
        for n, (who, s_) in enumerate(ROWS15):
            yy = y - 90 + n * 150
            avatar(c, who, x - 270, yy, 0.8)
            K.text(c, s_, x - 120, yy + 4, 58, "hand", BLACK)
    return None


ev(j, k_list, pop_fn(j, k_list, list15), "wood_low", 0.7)


def rows15(c, kk, T, cx=cx, cy=cy):
    x, y = cx + 60, cy + 10
    for n in range(3):
        t0 = tb(15, k_rows[n])
        if T < t0:
            continue
        yy = y - 90 + n * 150
        part, _ = wb.partial(check(x + 30, yy, 40), clamp01((T - t0) / 0.25))
        c.drawPath(part, wb.marker(GREEN, 12))
        g = pop_scale(T - t0 - 0.15)
        with K.at(c, x + 150, yy, 0, g):
            clock_face(c, 0, 0, 38, ease_out(clamp01((T - t0 - 0.15) / 0.5)) / 6)
        with K.at(c, x + 275, yy + 4, 0, g):
            K.text(c, "10分钟", 0, 0, 48, "hand", GREEN)
    return None


ev(j, k_rows[0], rows15, "pop", 0.7)
b.hit(j, k_rows[1], "pop", 0.7, "第二个人聊完")
b.hit(j, k_rows[2], "clap", 0.8, "第三个人聊完")

# ---------------------------------------------------------------- 屏 16：做法二——只问一个问题“你最担心什么？”，小王答“怕加班”，小李记下
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
steps_row(j, 0, 1)
LI16, WG16 = (cx - 330, cy + 470, 0.95), (cx + 330, cy + 470, 0.95)
k_q16 = kq(j, wt(24, 1, 0.25), 1)
k_ans = nx(j, wt(24, 1, 0.9), k_q16)
k_note16 = k_ans + 1
L.note("你最担心什么？", "怕加班")


def ppl16(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy + 470, sc):
        x, y, s = LI16
        hx, hy = head_of(x, y, s)
        writing = T >= tb(16, k_note16)
        rh = (x + 120 * s + 10 * math.sin(T * 16), hy + 130 * s) if writing else (x + 130 * s, hy + 160 * s)
        draw_li(c, x, y, s, "smile", lh=(x + 40 * s, hy + 170 * s), rh=rh)
        with K.at(c, x + 100 * s, hy + 150 * s, -8):
            box(c, 0, 0, 130, 100, NOTE_FILL, "#C9A227", 5, 6)
            if writing:
                for r in range(2):
                    f = clamp01((T - tb(16, k_note16) - r * 0.4) / 0.4)
                    if f > 0:
                        C.line(c, (-45, -18 + r * 30), (-45 + 90 * f, -18 + r * 30), BLUE, 6)
        x, y, s = WG16
        ans = T >= tb(16, k_ans)
        draw_wang(c, x, y, s, mood="sad" if ans else "flat")
    return None


ev(j, 0, pop_fn(j, 0, ppl16))
ev(j, k_q16, L.pop_bubble("你最担心什么？", cx - 130, cy - 230, j, k_q16, 72, BLUE, tail=-1), "pop", 0.75)


def ans16(c, kk, T, cx=cx, cy=cy):
    t0 = tb(16, k_ans)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 300, cy + 20
    with at_pop(c, x, y, sc):
        bubble_box(c, x, y, 320, 150, 1)
        K.text(c, "怕加班", x + 20, y + 4, 64, "hand", BLACK)
        sweat(c, x - 110, y, 1.0)
    return None


ev(j, k_ans, ans16, "pop", 0.75)
b.hit(j, k_note16, "wood_low", 0.6, "小李记在本子上")

# ---------------------------------------------------------------- 屏 17：做法三——方案里每条意见后面贴着提的人的头像，“小王提”“组长提”
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
steps_row(j, 0, 2)
LI17 = (cx - 430, cy + 470, 0.85)
CARD17 = (cx + 90, cy - 50)
k_card17 = kq(j, wt(25, 1, 0.1), 1)
k_p1 = nx(j, wt(25, 1, 0.75), k_card17)
k_p2 = k_p1 + 1
k_tag = nx(j, wt(25, 3, 0.25), k_p2)
OPS17 = [("wang", "人手排好", "小王提"), ("leader", "先试一组", "组长提")]
L.note("新流程方案", *[o[1] for o in OPS17], *[o[2] for o in OPS17])


def li17(c, sc, T, cx=cx, cy=cy):
    x, y, s = LI17
    hx, hy = head_of(x, y, s)
    point = T >= tb(17, k_tag)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile", rh=(x + 120 * s, hy - 70 * s) if point else None)
    return None


ev(j, 0, pop_fn(j, 0, li17))


def card17(c, sc, T, cx=cx, cy=cy):
    x, y = CARD17
    with at_pop(c, x, y, sc):
        box(c, x, y, 700, 540, "#FFFFFF", BLACK, 7, 12)
        K.text(c, "新流程方案", x, y - 210, 62, "hand", BLACK)
        C.line(c, (x - 280, y - 160), (x + 280, y - 160), GRAY, 5)
        for n, (who, s_, tag) in enumerate(OPS17):
            k_ = (k_p1, k_p2)[n]
            yy = y - 60 + n * 150
            g = pop_scale(T - tb(17, k_))
            if g <= 0:
                for r in range(2):
                    C.line(c, (x - 260, yy - 20 + r * 40), (x + 200 - r * 80, yy - 20 + r * 40), GRAY_FILL, 8)
                continue
            with K.at(c, x - 160, yy, 0, g):
                K.text(c, s_, 0, 4, 58, "hand", BLACK)
            with K.at(c, x + 60, yy, 0, g):
                c.drawCircle(0, 0, 50, K.paint(NOTE_FILL))
                avatar(c, who, 0, 4, 0.8)
            gt = pop_scale(T - tb(17, k_tag) - n * 0.12)
            if gt > 0:
                with K.at(c, x + 225, yy, 0, gt):
                    box(c, 0, 0, 180, 64, "#FFFFFF", RED, 5, 32)
                    K.text(c, tag, 0, 2, 46, "hand", RED)
    return None


ev(j, k_card17, pop_fn(j, k_card17, card17), "pop", 0.7)
b.hit(j, k_p1, "wood_high", 0.7, "第一条意见 + 小王头像")
b.hit(j, k_p2, "wood_high", 0.7, "第二条意见 + 组长头像")
b.hit(j, k_tag, "clap", 0.8, "标上是谁提的")

# ================================================================ 屏 18：会前十分钟（小钟，打勾）vs 会上一小时（大钟，打叉）
cx, cy = R[18]
j = L.scene(18, (cx, cy + 10, Z))
LI18 = (cx - 280, cy + 480, 0.8)
k_li18 = 0
k_l18 = kq(j, wt(26, 0, 0.25), 1)
k_r18 = nx(j, wt(26, 1, 0.05), k_l18)
k_x18 = nx(j, wt(26, 1, 0.7), k_r18)
L.note("会前", "会上", "10分钟", "1小时")


def li18(c, sc, T, cx=cx, cy=cy):
    x, y, s = LI18
    hx, hy = head_of(x, y, s)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile", rh=(x + 100 * s, hy - 60 * s))
        mug(c, x + 100 * s + 10, hy - 50 * s, 0.9)
        wx = cx + 260
        draw_wang(c, wx, y, s, mood="smile", lh=(wx - 100 * s, hy - 60 * s))
        mug(c, wx - 100 * s - 10, hy - 50 * s, 0.9, BLUE, "#DCEAFB")

    return None


ev(j, k_li18, pop_fn(j, k_li18, li18), "pop", 0.6)


def lclk18(c, kk, T, cx=cx, cy=cy):
    t0 = tb(18, k_l18)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx - 280, cy - 170
    with K.at(c, x, y, 0, sc):
        K.text(c, "会前", 0, -230, 70, "hand", BLUE)
        clock_face(c, 0, 0, 130, ease_out(clamp01((T - t0) / 0.6)) / 6)
        K.text(c, "10分钟", 0, 190, 64, "hand", GREEN)
    return None


ev(j, k_l18, lclk18, "wood_high", 0.75)


def rclk18(c, kk, T, cx=cx, cy=cy):
    t0 = tb(18, k_r18)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 260, cy - 170
    with K.at(c, x, y, 0, sc):
        K.text(c, "会上", 0, -230, 70, "hand", RED)
        clock_face(c, 0, 0, 190, ease_out(clamp01((T - t0) / 0.8)), RED, RED_FILL)
        K.text(c, "1小时", 0, 250, 64, "hand", RED)
    return None


ev(j, k_r18, rclk18, "wood_low", 0.75)


def x18(c, kk, T, cx=cx, cy=cy):
    t0 = tb(18, k_x18)
    sc = C.slam_scale(T - t0)
    if sc <= 0:
        return None
    with K.at(c, cx + 260, cy - 170, 0, sc):
        c.drawPath(cross(0, 0, 150), wb.marker(RED, 20))
    return None


ev(j, k_x18, x18, "kick", 0.9)
b.shots[j].shake = [(k_x18, 9.0)]

# ================================================================ 屏 19：评论区——方案卡在谁那里；几条留言；下一讲预告（日历飞快翻，小李站在原地）
cx, cy = R[19]
j = L.scene(19, (cx, cy + 10, Z))
b.path(j, 0, 0.8, wb.bubble(cx, cy - 440, 1000, 200, -1), BLACK, 9, sfx="wood_high")
k_c1 = kq(j, wt(27, 0, 0.2), 1)
b.text(j, k_c1, k_c1 + 1.3, "方案卡在谁那里？", cx, cy - 440, 64, RED, sfx="pop")
k_gr = nx(j, wt(28, 0, 0.1), k_c1 + 1)
GRIPES = [("卡在领导", cx - 280, cy - 160), ("卡在隔壁组", cx + 250, cy - 200), ("卡在财务", cx + 40, cy - 10)]
L.note(*[g[0] for g in GRIPES])
for n, (s_, x, y) in enumerate(GRIPES):
    ev(j, k_gr + n, L.pop_bubble(s_, x, y, j, k_gr + n, 56, BLACK, tail=-1 if n % 2 == 0 else 1),
       ("pop", "pop", "wood_high")[n], 0.6)
k_n = nx(j, wt(29, 0, 0.15), k_gr + 2)
b.path(j, k_n, k_n + 0.6, rect(cx, cy + 300, 1000, 330, 24), BLUE, 8, sfx="wood_high")
b.text(j, k_n + 0.5, k_n + 0.8, "下一讲", cx, cy + 180, 52, BLUE)
b.text(j, k_n + 0.8, k_n + 1.6, "每天都很忙", cx, cy + 265, 64, BLACK)
b.text(j, k_n + 1.6, k_n + 2.6, "为什么还在原地？", cx, cy + 350, 64, BLACK)


def preview19(c, kk, T, cx=cx, cy=cy):
    """预告卡两侧：左边日历一页页飞快翻过，右边小李站在原地。"""
    t0 = tb(19, k_n + 1)
    if T < t0:
        return None
    g = pop_scale(T - t0)
    x, y = cx - 395, cy + 310
    with K.at(c, x, y, 0, g):
        box(c, 0, 0, 120, 130, "#FFFFFF", BLACK, 5, 8)
        c.drawRect(skia.Rect.MakeXYWH(-60, -65, 120, 34), K.paint(RED))
        ph = ((T - t0) * 3) % 1.0
        n = int((T - t0) * 3) % 12 + 1
        K.text(c, str(n), 0, 22, 56, "black", BLACK)
        if ph < 0.4:
            c.save()
            c.translate(0, -31)
            c.scale(1, 1 - ph / 0.4)
            c.drawRect(skia.Rect.MakeXYWH(-58, 0, 116, 92), K.paint("#FFFFFF"))
            C.line(c, (-58, 92), (58, 92), GRAY, 3)
            c.restore()
    x2 = cx + 400
    with K.at(c, x2, cy + 445, 0, g):
        draw_li(c, 0, 0, 0.5, "sad")

        dashed(c, (-60, 4), (60, 4), GRAY, 5)
    return None


b.custom(j, k_n + 1, k_n + 1.3, preview19)

# ================================================================ 收尾
L.finish(cover_shot=1, square_shot=11, notes=NOTES)
L.export(globals())
