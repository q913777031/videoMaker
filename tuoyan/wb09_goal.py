"""09 能动手的目标（白板手绘版）：目标定成这样，才动得起来。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：最后 4 拍不出新笔画）。
叙事（D 误区对照）：开头一座大山，结尾这座山变成台阶；中间白板分左右两列，左列红叉“常这么定”，右列绿勾“书里建议”，
一屏一对，共四对——
打工人开局（元旦写下便利贴“我要自律”，三天后被风吹走）→ 目标像一座山，山顶蹲着明天怪兽，看一眼就累 →
亮书《拖延心理学》，博克和袁，第12章专讲定目标 → drop：红笔三刀把山切成一级级台阶，怪兽滚下山，小周站上第一级 →
四对对照（“我要自律”／“周三下班前写完第一页”；同时立十个／先挑一个；这周弄完报告／打开文档列个提纲；
等状态来了／先做一会儿）→ 台阶特写（会卡住，绕过去接着走；走一步记一步，奖励一下）→ 拉远看四对 →
观众作业（今晚写下你的第一级）→ 回到山：小周跳上第三级，明天怪兽在山脚缩小 → 评论区互动。
书中观点为转述（Jane B. Burka & Lenora M. Yuen, Procrastination: Why You Do It, What to Do About It Now, 2008 修订版；
中译本《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009，第12章“作战武器：明确的目标与可行性的计划”）；
例子与做法为示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, cross,
                               desk, doc, face, join, partial, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, lerp

from .common import BOOK, episode

ACC = "#2F8C9A"
SQUARE_SHOT = 3                 # 场景 4（drop）：大山被红笔切成台阶，小周站在第一级

b = Board(size=(3600, 11600))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 系列角色

def badge(x, y, s=1.0) -> skia.Path:
    """配合 stick 的工牌（挂绳 + 卡片）：(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 22 * s, hy + 45 * s), (x + 18 * s, hy + 130 * s), (x + 30 * s, hy + 45 * s)),
                rect(x + 18 * s, hy + 155 * s, 38 * s, 50 * s, 5 * s))


def zhou(x, y, s=0.75, arms="down", mood="flat") -> skia.Path:
    """小周：火柴人 + 胸前工牌。"""
    return join(stick(x, y, s, arms), face(x, y, s, mood), badge(x, y, s))


def monster(x, y, r) -> skia.Path:
    """明天怪兽：毛茸茸的一团 + 两只圆眼 + 小手攥着一张日历页（“明天”二字另写）。"""
    pts = []
    n = 44
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = r * (1.12 if i % 2 else 1.0)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    parts = [P(*pts, close=True)]
    for dx in (-0.33, 0.33):
        parts += [circle(x + dx * r, y - 0.3 * r, 0.2 * r), circle(x + dx * r + 0.04 * r, y - 0.28 * r, 0.07 * r)]
    parts += [P((x - 1.05 * r, y + 0.1 * r), (x - 1.35 * r, y - 0.2 * r)),
              P((x + 1.05 * r, y + 0.1 * r), (x + 1.3 * r, y - 0.05 * r)),
              rect(x + 1.55 * r, y - 0.15 * r, 0.5 * r, 0.6 * r, 6), P((x + 1.3 * r, y - 0.33 * r), (x + 1.8 * r, y - 0.33 * r))]
    return join(*parts)


# ---------------------------------------------------------------- 本讲画法

def calendar(x, y, w=280, h=300) -> skia.Path:
    """台历页：外框 + 顶部横条 + 两个挂环。"""
    t = y - h / 2
    return join(rect(x, y, w, h, 14), P((x - w / 2, t + 70), (x + w / 2, t + 70)),
                circle(x - w / 4, t, 16), circle(x + w / 4, t, 16))


def wind(x0, x1, ys) -> skia.Path:
    """几道风：横向波浪线，末端打个卷。"""
    parts = []
    for i, y in enumerate(ys):
        p = underline(x0 + i * 30, x1 - 40, y, 12, 60)
        p.quadTo(x1, y - 10, x1 - 20, y - 40)
        parts.append(p)
    return join(*parts)


def mountain(cx=1800, base=2900, half=600, peak=1750) -> skia.Path:
    return P((cx - half, base), (cx, peak), (cx + half, base))


def stairs(pts) -> skia.Path:
    return P(*pts)


def drop(x, y, s=1.0) -> skia.Path:
    """汗珠。"""
    return P((x, y - 22 * s), (x - 13 * s, y + 4 * s), (x, y + 18 * s), (x + 13 * s, y + 4 * s), close=True)


def note(x, y, w, h, lines=0) -> skia.Path:
    """便利贴外框（可带几道横线）。"""
    parts = [rect(x, y, w, h, 8)]
    for i in range(lines):
        yy = y - h / 2 + h * (i + 1) / (lines + 1)
        parts.append(P((x - w / 2 + 30, yy), (x + w / 2 - 30 - 40 * (i % 2), yy)))
    return join(*parts)


def pen(x, y, ang=35, length=260, w=46) -> skia.Path:
    """马克笔：斜放的笔杆 + 笔帽分界 + 笔尖（(x, y) 为笔尖）。"""
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)          # 笔杆方向（从笔尖往后）
    nx, ny = -uy, ux
    tip = (x, y)
    b0 = (x + ux * 50, y + uy * 50)
    b1 = (x + ux * length, y + uy * length)
    hw = w / 2
    body = P((b0[0] + nx * hw, b0[1] + ny * hw), (b1[0] + nx * hw, b1[1] + ny * hw),
             (b1[0] - nx * hw, b1[1] - ny * hw), (b0[0] - nx * hw, b0[1] - ny * hw), close=True)
    cone = P((b0[0] + nx * hw, b0[1] + ny * hw), tip, (b0[0] - nx * hw, b0[1] - ny * hw))
    cap = P((x + ux * (length - 70) + nx * hw, y + uy * (length - 70) + ny * hw),
            (x + ux * (length - 70) - nx * hw, y + uy * (length - 70) - ny * hw))
    return join(body, cone, cap)


def bolt(x, y, s=1.0) -> skia.Path:
    """闪电（等灵感）。"""
    return P((x + 20 * s, y - 90 * s), (x - 35 * s, y + 5 * s), (x + 5 * s, y + 5 * s), (x - 20 * s, y + 90 * s),
             (x + 40 * s, y - 15 * s), (x + 2 * s, y - 15 * s), (x + 35 * s, y - 90 * s), close=True)


def lying(x, y, s=0.55) -> skia.Path:
    """躺着的小周（转 90 度；(x, y) 为身子中点所在的地面）。"""
    p = zhou(0, 0, s, "down", "flat")
    m = skia.Matrix.RotateDeg(-90)
    p.transform(m)
    p.offset(x - 150 * s, y - 50 * s)
    return p


def ground(x0, x1, y) -> skia.Path:
    return P((x0, y), (x1, y))


def stone(x, y, r=62) -> skia.Path:
    """石头：一块不规则的圆，压在台阶上（(x, y) 为底边中点）。"""
    pts = [(x - r, y), (x - r * 1.05, y - r * 0.7), (x - r * 0.5, y - r * 1.35), (x + r * 0.35, y - r * 1.4),
           (x + r * 1.0, y - r * 0.85), (x + r * 1.05, y)]
    return join(P(*pts, close=True), P((x - r * 0.3, y - r * 0.9), (x + r * 0.1, y - r * 0.6)))


def flag(x, y, h=200) -> skia.Path:
    return join(P((x, y), (x, y - h)), P((x, y - h), (x + 120, y - h + 35), (x, y - h + 70)))


def cup(x, y) -> skia.Path:
    """奶茶：杯身 + 杯盖 + 吸管 + 三颗珍珠（(x, y) 为杯底中点）。"""
    return join(P((x - 48, y - 130), (x - 36, y), (x + 36, y), (x + 48, y - 130), close=True),
                P((x - 56, y - 130), (x + 56, y - 130)), P((x + 8, y - 130), (x + 30, y - 195), (x + 55, y - 205)),
                circle(x - 16, y - 28, 9), circle(x + 12, y - 30, 9), circle(x - 2, y - 56, 9))


def sparks(x, y, r0, r1, n=6, a0=-90, span=180) -> skia.Path:
    parts = []
    for i in range(n):
        a = math.radians(a0 - span / 2 + span * i / max(1, n - 1))
        parts.append(P((x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))))
    return join(*parts)


def bracket(x, y0, y1, d=60) -> skia.Path:
    """竖着的大括号线（d>0 开口朝右，d<0 开口朝左）。"""
    return P((x + d, y0), (x, y0), (x, y1), (x + d, y1))


def fill_fn(x, y, w, h, color="#FFE27A", alpha=0.9):
    """便利贴底色。"""

    def fn(c, k, t):
        K.rr(c, x, y, w, h, 8, color, alpha * k)
        return None

    return fn


# ---------------------------------------------------------------- 会动的画面（custom）

def _clip_text(c, s, x, y, size, color, k):
    """在 custom 里按进度从左到右写字（与引擎写字一致的裁剪）。"""
    if k <= 0:
        return None
    w = K.text_w(s, size, "hand")
    x0 = x - w / 2
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0 - 20, y - size, x0 + w * k + 4, y + size))
    K.text(c, s, x, y, size, "hand", color)
    c.restore()
    return (x0 + w * k, y) if k < 1 else None


def flying_note(x0, y0, x1, y1, w=260, h=170, text="我要自律"):
    """开局便利贴：前 1/3 画框写字，中间停住，最后 1/3 被风卷着翻飞出画面。"""
    shape = rect(0, 0, w, h, 8)

    def fn(c, k, t):
        draw = clamp01(k / 0.34)
        fly = clamp01((k - 0.62) / 0.38)
        if fly >= 1:
            return None
        e = ease_in_out(fly)
        x = lerp(x0, x1, e)
        y = lerp(y0, y1, e) - 160 * math.sin(math.pi * e)
        c.save()
        c.translate(x, y)
        c.rotate(-8 * math.sin(fly * 10) + 70 * e)
        a = 1 - clamp01((fly - 0.7) / 0.3)
        K.rr(c, 0, 0, w, h, 8, "#FFE27A", 0.9 * clamp01(draw * 2) * a)
        part, tip = partial(shape, clamp01(draw * 1.6))
        c.drawPath(part, wb.marker(ORANGE, 7, a))
        tp = _clip_text(c, text, 0, 0, 54, BLACK, clamp01((draw - 0.55) / 0.45))
        c.restore()
        if draw < 1:
            p = tip if tip is not None and draw < 0.62 else tp
            return (x + p[0], y + p[1]) if p else None
        return None

    return fn


PEAK = (1800, 1750)
MBASE = 2900
MR = 95
M_TOP = (1800, 1750 - MR)                # 怪兽蹲在山顶
M_FOOT = (2480, MBASE - MR)              # 滚到右边山脚


def monster_actor(c, k, t):
    """明天怪兽：场景 2 画在山顶 → 场景 4 滚下山 → 场景 13 在山脚缩小。"""
    roll = clamp01((t - b.t_of(3, 4)) / (b.t_of(3, 6) - b.t_of(3, 4)))
    shrink = ease_in_out(clamp01((t - b.t_of(12, 2)) / (b.t_of(12, 3) - b.t_of(12, 2))))
    e = roll * roll
    s = lerp(1.0, 0.45, shrink)
    x = lerp(M_TOP[0], M_FOOT[0], e)
    y = lerp(M_TOP[1], M_FOOT[1], e) - 50 * math.sin(math.pi * e)
    if roll >= 1:
        y = MBASE - MR * s
    ang = math.degrees((x - M_TOP[0]) / MR) * 0.6
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    part, tip = partial(monster(0, 0, MR), clamp01(k / 0.75))
    c.drawPath(part, wb.marker(BLACK, 8))
    tp = _clip_text(c, "明天", 0, 0.4 * MR, 0.48 * MR, RED, clamp01((k - 0.75) / 0.25))
    c.restore()
    if k < 1:
        p = tip if tip is not None else tp
        return (x + p[0], y + p[1]) if p else None
    return None


# 山被切成的台阶（先踏面后立面，切进山体）：4 级，每级宽 150、高 287.5
_DX, _DY = 150, 287.5
STEPS = [(1200 + i * _DX, MBASE - i * _DY) for i in range(5)]
STAIR_PTS = []
for i in range(4):
    STAIR_PTS += [STEPS[i], (STEPS[i + 1][0], STEPS[i][1])]
STAIR_PTS.append(STEPS[4])
STEP_TOP = [((STEPS[i][0] + STEPS[i + 1][0]) / 2, STEPS[i][1]) for i in range(1, 4)]   # 第 1–3 级踏面中点


def right_slope_x(y):
    return 1800 + (y - PEAK[1]) * 600 / (MBASE - PEAK[1])


def zhou_actor(c, k, t):
    """小周：场景 4 画在第一级 → 场景 13 跳两下到第三级。"""
    hops = [(b.t_of(12, 0), b.t_of(12, 0.8)), (b.t_of(12, 1), b.t_of(12, 1.8))]
    x, y = STEP_TOP[0]
    for i, (h0, h1) in enumerate(hops):
        f = ease_in_out(clamp01((t - h0) / (h1 - h0)))
        if f <= 0:
            break
        (ax, ay), (bx, by) = STEP_TOP[i], STEP_TOP[i + 1]
        x, y = lerp(ax, bx, f), lerp(ay, by, f) - 130 * math.sin(math.pi * f)
    s = 0.55
    c.save()
    c.translate(x, y)
    part, tip = partial(zhou(0, 0, s, "up", "smile"), k)
    c.drawPath(part, wb.marker(BLACK, 9))
    c.restore()
    if tip is not None:
        return (x + tip[0], y + tip[1])
    return None


# ---------------------------------------------------------------- 版面
VM = (1800, 2230, 0.6)              # 看整座山
LX, RX = 1360, 2240                 # 对照表左列（常这么定）、右列（书里建议）
HY = 3650                           # 表头
ROWS = [4100, 5350, 6600, 7850]     # 四对对照的行中线
MARK = -200                         # 每行红叉 / 绿勾相对行中线的位置


def VR(i):
    return (1800, ROWS[i] + 140, 0.66)


SX, SY = 1800, 9330                 # 台阶特写
VS = (SX, SY, 0.62)
GS = 9750                           # 特写台阶地面
SS = [(950, GS), (1350, GS), (1350, 9550), (1750, 9550), (1750, 9350), (2150, 9350), (2150, 9150), (2550, 9150),
      (2550, GS)]

# ---------------------------------------------------------------- 开局：元旦的便利贴（场景 1）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

b.shot("今年我要自律", "元旦 · 新目标", (1800, 850, 0.85), bars=2)
L(zhou(1450, 1300, 0.85, "hold", "smile"), 0, 0.9, sfx="wood_high")
L(calendar(2150, 600), 1, 1.8, BLACK, 9, sfx="wood_low")
T("1月1日", 2150, 640, 70, RED, k0=2, k1=2.9, sfx="pop")
b.custom(J(), 3, 6, flying_note(1720, 1070, 2780, 1250), sfx="pop")
T("三天后", 2150, 880, 66, BLUE, k0=4, k1=4.8, sfx="pop")
L(wind(1180, 1400, (860, 930)), 5, 5.8, BLUE, 7, sfx="shaker")

# ---------------------------------------------------------------- 目标像一座山（场景 2）

b.shot("一看就不想动", "目标 · 一座山", VM, bars=3)
L(mountain(), 0, 0.9, BLACK, 11, sfx="wood_low")
T("大目标", 1840, 2480, 100, k0=1, k1=1.8, sfx="pop")
L(zhou(1030, 2900, 0.7, "down", "sad"), 2, 2.9, sfx="wood_high")
b.custom(J(), 3, 4.2, monster_actor, sfx="wood_low")
L(bubble(1060, 2480, 240, 110, -1), 5, 5.7, BLACK, 8, sfx="pop")
T("好累", 1060, 2480, 66, k0=6, k1=6.8, sfx="pop")
L(join(drop(1110, 2620), drop(1135, 2680, 0.8)), 7, 7.6, BLUE, 6, sfx="pop")

# ---------------------------------------------------------------- 书里有一章专讲定目标（场景 3）

b.shot("书里教定目标", "拖延心理学 · 书中观点", (2950, 2250, 0.85), bars=3)
L(book(2950, 1950, 340, 230), 0, 0.9, sfx="wood_low")
T("《拖延心理学》", 2950, 2190, 70, GREEN, k0=1, k1=2.75, sfx="pop")
T("博克和袁", 2950, 2300, 56, k0=3, k1=4, sfx="pop")
L(join(rect(2950, 2450, 520, 90, 8), *[P((2950 - 230 + i * 46, 2405), (2950 - 230 + i * 46, 2405 + (40 if i % 2 else 22)))
                                       for i in range(11)]), 4, 4.9, ORANGE, 8, sfx="wood_high")
T("第12章：定目标", 2950, 2600, 66, BLUE, k0=5, k1=6.75, sfx="pop")
L(underline(2970, 3200, 2650, 9, 30), 7, 7.7, RED, 7, sfx="ding")

# ---------------------------------------------------------------- drop：山被切成台阶（场景 4）

b.shot("山切成台阶", "书中观点 · 拆成小步", VM, shake=[0], flashes=[0], bars=3)
for i, (k, y) in enumerate(((0, STEPS[1][1]), (1, STEPS[2][1]), (2, STEPS[3][1]))):
    L(P((right_slope_x(y) + 30, y), (STEPS[i + 1][0], y)), k, k + 0.5, RED, 14, sfx="kick")
L(stairs(STAIR_PTS), 3, 3.9, RED, 12, sfx="wood_high")
b.erase(J(), 4, 4.8, 1045, 2680, 290, 540)                 # 山脚下的旧小周和“好累”擦掉，小周站上台阶
b.custom(J(), 4, 6, lambda c, k, t: None, sfx="shaker")    # 怪兽滚下山（monster_actor 按时间演）
b.custom(J(), 5, 5.9, zhou_actor, sfx="wood_high")
T("第一级", 1050, 2560, 70, RED, k0=6, k1=6.8, sfx="pop")
L(arrow((1150, 2610), (1330, 2700), 0.2, 34), 7, 7.7, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 四对对照（场景 5–8）

b.shot("写成看得见的事", "对照一 · 看得见", VR(0), bars=3)
R = ROWS[0]
T("常这么定", LX, HY, 76, RED, k0=0, k1=1, sfx="pop")
T("书里建议", RX, HY, 76, GREEN, k0=1, k1=2, sfx="pop")
T("我要自律", LX, R + 20, 76, k0=2, k1=3, sfx="pop")
L(cross(LX, R + MARK, 50), 3, 3.5, RED, 11, sfx="rim")
T("周三下班前", RX, R - 20, 72, k0=4, k1=5.2, sfx="pop")
T("写完第一页", RX, R + 80, 72, BLUE, k0=5.3, k1=6.5)
L(check(RX, R + MARK, 55), 7, 7.6, GREEN, 12, sfx="ding")

b.shot("一次只挑一个", "对照二 · 一次一个", VR(1), bars=3)
R = ROWS[1]
for i in range(5):
    b.custom(J(), 0, 0.5, fill_fn(LX - 240 + i * 120, R - 40, 100, 80))
L(join(*[note(LX - 240 + i * 120, R - 40, 100, 80) for i in range(5)]), 0, 0.9, ORANGE, 7, sfx="wood_high")
T("同时立十个", LX, R + 110, 72, k0=1, k1=2.25, sfx="pop")
L(cross(LX, R + MARK, 50), 3, 3.5, RED, 11, sfx="rim")
L(P((LX - 310, R - 30), (LX + 310, R - 50)), 4, 4.5, RED, 10, sfx="rim")
b.custom(J(), 5, 5.5, fill_fn(RX, R - 40, 220, 150))
L(note(RX, R - 40, 220, 150, 2), 5, 5.9, ORANGE, 8, sfx="wood_high")
T("先挑一个", RX, R + 110, 72, BLUE, k0=6, k1=7, sfx="pop")
L(check(RX, R + MARK, 55), 7.2, 7.8, GREEN, 12)
H(7, "ding")

b.shot("第一步要很小", "对照三 · 第一步", VR(2), bars=3)
R = ROWS[2]
L(P((LX - 200, R + 20), (LX - 30, R + 20), (LX - 30, R - 130), (LX + 200, R - 130)), 0, 0.9, BLACK, 10, sfx="wood_low")
T("这周弄完报告", LX, R + 110, 70, k0=1, k1=2.5, sfx="pop")
L(cross(LX, R + MARK - 20, 50), 3, 3.5, RED, 11, sfx="rim")
L(P((RX - 210, R + 20), (RX - 90, R + 20), (RX - 90, R - 5), (RX + 30, R - 5), (RX + 30, R - 70), (RX + 150, R - 70),
    (RX + 150, R - 135), (RX + 210, R - 135)), 4, 4.9, BLACK, 10, sfx="wood_high")
L(circle(RX - 150, R + 5, 55), 5, 5.6, RED, 7, sfx="pop")
T("打开文档", RX, R + 110, 70, BLUE, k0=6, k1=6.9, sfx="pop")
T("列个提纲", RX, R + 200, 70, BLUE, k0=7, k1=7.9, sfx="pop")
L(check(RX, R + MARK - 20, 55), 7, 7.6, GREEN, 12)

b.shot("别等有感觉", "对照四 · 先动手", VR(3), bars=3)
R = ROWS[3]
L(lying(LX - 40, R + 40), 0, 0.9, BLACK, 9, sfx="wood_low")
L(bolt(LX + 220, R - 110, 0.9), 1, 1.8, ORANGE, 8, sfx="wood_high")
T("等状态来了", LX, R + 150, 72, k0=2, k1=3.25, sfx="pop")
L(cross(LX - 60, R + MARK, 50), 3.5, 4, RED, 11)
H(4, "rim")
L(zhou(RX - 150, R + 70, 0.55, "point", "smile"), 5, 5.9, BLACK, 9, sfx="wood_high")
L(doc(RX + 60, R - 30, 130, 160, 3), 6, 6.7, BLUE, 8, sfx="pop")
T("先做一会儿", RX, R + 150, 72, BLUE, k0=6.7, k1=7.95)
L(check(RX + 40, R + MARK, 55), 7, 7.6, GREEN, 12, sfx="ding")

# ---------------------------------------------------------------- 台阶特写：会卡住，每一步都算（场景 9–10）

b.shot("卡住很正常", "书中观点 · 卡了接着来", VS, bars=3)
L(stairs(SS), 0, 0.9, BLACK, 11, sfx="wood_low")
L(zhou(1520, 9550, 0.6, "down", "flat"), 1, 1.9, BLACK, 9, sfx="wood_high")
L(stone(1960, 9350), 2, 2.8, BLACK, 10, sfx="tom")
T("会卡住", 1950, 9480, 72, RED, k0=3, k1=3.8, sfx="pop")
L(arrow((1600, 9240), (2230, 9070), -0.35, 40), 4, 4.9, GREEN, 10, sfx="wood_high")
T("绕过去，接着走", 1880, 8880, 70, GREEN, k0=5, k1=6.75, sfx="pop")
L(flag(2480, 9150), 7, 7.7, RED, 9, sfx="ding")

b.shot("每一步都算数", "书中观点 · 走一步记一步", VS, bars=3)
for n, (cx, cy) in enumerate(((1550, 9665), (1950, 9650), (2350, 9300))):
    L(check(cx, cy, 45), n, n + 0.6, GREEN, 11, sfx="ding")
T("走一步，记一步", SX, 9880, 72, k0=3, k1=4.75, sfx="pop")
L(cup(2350, 9150), 5, 5.8, ORANGE, 8, sfx="wood_high")
T("奖励一下", 2500, 8880, 64, ORANGE, k0=6, k1=7, sfx="pop")
L(sparks(2350, 9080, 120, 160, 5, -90, 120), 7, 7.6, ORANGE, 6, sfx="pop")

# ---------------------------------------------------------------- 拉远看四对（场景 11）

b.shot("四对放一起看", "四对放一起看", (1800, 5850, 0.2), bars=3)
L(bracket(930, 3560, 8150, 70), 0, 0.9, RED, 30, sfx="wood_high")
L(bracket(2670, 3560, 8150, -70), 1, 1.9, GREEN, 30, sfx="wood_high")
T("看着燃", 470, 5600, 210, RED, k0=2, k1=2.8, sfx="pop")
T("动不了", 470, 5900, 210, RED, k0=3, k1=3.8, sfx="pop")
T("看得见", 3130, 5600, 210, GREEN, k0=4, k1=4.8, sfx="pop")
T("马上做", 3130, 5900, 210, GREEN, k0=5, k1=5.8, sfx="pop")
L(underline(2840, 3420, 6060, 30, 90), 6, 6.8, GREEN, 26, sfx="ding")

# ---------------------------------------------------------------- 观众作业（场景 12）

b.shot("今晚就写一级", "作业 · 写下第一级", (640, 1850, 0.85), bars=3)
b.custom(J(), 0, 0.6, fill_fn(560, 1830, 400, 300))
L(note(560, 1830, 400, 300), 0, 0.9, ORANGE, 9, sfx="wood_high")
L(join(P((410, 1800), (710, 1800)), P((410, 1890), (650, 1890))), 1, 1.6, BLUE, 5, sfx="pop")
L(pen(840, 1990, 40), 2, 2.8, BLACK, 8, sfx="wood_low")
T("今晚写下", 560, 1550, 76, k0=3, k1=4, sfx="pop")
T("你的第一级", 560, 2120, 76, RED, k0=5, k1=6.25, sfx="pop")
L(underline(380, 740, 2180, 10, 30), 7, 7.7, RED, 7, sfx="ding")

# ---------------------------------------------------------------- 回到山：小周上到第三级（场景 13）

b.shot("山没那么吓人了", "回到这座山", VM, bars=3)
H(0, "wood_high")
H(1, "wood_high")
H(2, "pop")
L(check(STEP_TOP[0][0], STEP_TOP[0][1] - 60, 40), 3, 3.6, GREEN, 10, sfx="ding")
L(check(STEP_TOP[1][0] - 20, STEP_TOP[1][1] - 60, 40), 4, 4.6, GREEN, 10, sfx="ding")
T("一级一级来", 2300, 1950, 72, GREEN, k0=5, k1=6.25, sfx="pop")
L(underline(2130, 2470, 2010, 9, 30), 6.5, 7.2, GREEN, 7)
H(7, "shaker")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5800, 0.085)
COMMENT = (1800, 10900, 0.8)
b.shot("你第一级是啥", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你的第一级台阶是什么？", 1800, 10800, 72, RED, k0=6, k1=8.75, sfx="pop")
T("下一讲：拖延改不干净，那就少拖一点", 1800, 10960, 50, k0=9, k1=13.25, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "goal", "能动手的目标", "目标定成这样，才动得起来", ACC, b.shots,
                 [f"{BOOK}第12章（中译本“作战武器：明确的目标与可行性的计划”，转述）",
                  "中译本：《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009；原书 Da Capo Lifelong Books 2008 修订版"],
                 "目标定成这样|才【动得起来】", SQUARE_SHOT,
                 ["书中观点为转述：书里讲定目标，主张把目标定成看得见、具体、能落地的行动；一次只挑一个；拆成小步，"
                  "第一步要小到马上能做；预料到会卡住，卡住了接着来；每走一步都算数，给自己一点奖励；"
                  "别等“有感觉了”才开始（第12章，据书中思路整理，具体步骤措辞需核实）。上屏句子均为口语转述，不是逐字引文。",
                  "“我要自律”“周三下班前写完第一页”“同时立十个”“这周弄完报告／打开文档列个提纲”“等状态来了／先做一会儿”"
                  "为示意例子；“奶茶”奖励为示意；元旦便利贴、“三天后”为现实场景示意，不是数据，不指向任何具体公司或个人。",
                  "“今晚写下你的第一级”为据书中思路整理的观众作业。",
                  "明天怪兽、大山与台阶、石头、小旗为本系列的画面比喻。"],
                 tags="#目标管理 #自律")
    return b.attach(ep)
