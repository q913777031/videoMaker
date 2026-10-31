"""08 清晰力（白板手绘版）：道理都懂，为啥就是不动？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事形式 H 改写：开局是小林周一写在便签上的三条计划原话（学点东西 / 多运动 / 整理下简历）→
周日晚上日历翻到底，三个空框一个没勾 → 收藏夹里的“自律方法”越拉越长 →
drop：一团雾“轰”地压下来吞掉便签，雾里探出老大、老二，伸手把小林拖回沙发 →
亮书（《认知觉醒》+ 周岭，书旁一个舵写“08”）→ 书中观点：说不清的事，大脑本能地躲（雾里小人往后退）；
目标拆细、写具体才动得起来（一大块被切成“哪天 / 几点 / 做哪步”三小块）→
回到那张便签，三条原话一条条改写成具体的样子，每改一条，雾散一块；第三条改完雾散尽，老大老二跟着消失 →
书中观点：想先看到结果再动手，往往看不到结果（走一步，脚下才亮一块台阶）；懂百点不如改一点（收藏夹收起，换成一个打了勾的小格）→
新的周日：便签三个勾，脑袋剖面里宝宝握舵，舵上添第 8 道握痕 → 评论区互动。
书中观点为转述（周岭《认知觉醒》第二章第一节“模糊”，第六章 行动力：第一节 清晰、第二节“傻瓜”、第三节 行动）；
“雾”是对书中“模糊”的画面化；三条计划、改写和收藏夹均为示意，据书中思路整理。
"""

import math
import random

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, face, join,
                               partial, rect, stick)

from .common import BOOK, episode

ACC = "#2F8F83"
SQUARE_SHOT = 3                 # 场景 4：便签被雾吞掉，雾里伸出老大老二把小林拖回沙发

b = Board(size=(3600, 5600))
FOG_FILL = "#DCDFE4"
FOG_LINE = "#A3A9B2"
LAMP = "#F2C14E"


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(fn, k0, k1, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


def ink(c, path, color, width, alpha=1.0):
    """和引擎描线同样的马克笔笔触（custom 动画里用）。"""
    c.drawPath(path, wb.marker(color, width, alpha))
    c.drawPath(path, K.paint(color, 0.22 * alpha, width * 0.45, blur=1.2))


def moved(path, dx=0.0, dy=0.0, s=1.0, ax=0.0, ay=0.0, rot=0.0) -> skia.Path:
    """以 (ax, ay) 为锚点缩放、旋转后再平移的路径副本。"""
    p = skia.Path(path)
    m = skia.Matrix()
    m.setTranslate(-ax, -ay)
    m.postScale(s, s)
    m.postRotate(rot)
    m.postTranslate(ax + dx, ay + dy)
    p.transform(m)
    return p


def pop_s(k):
    """弹出：0 → 1.15 → 1。"""
    return ease_out(clamp01(k * 1.6)) * (1 + 0.15 * math.sin(math.pi * clamp01(k)))


def span(j, k0, k1, T):
    """镜头 j 第 k0–k1 拍之间的进度 0–1（按绝对时刻算，custom 动画跨拍用）。"""
    t0, t1 = b.t_of(j, k0), b.t_of(j, k1)
    return clamp01((T - t0) / max(1e-3, t1 - t0))


# ---------------------------------------------------------------- 本讲画法

def note(x, y, w=380, h=200) -> skia.Path:
    """便签：卷角的方纸。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2),
                  (x - w / 2, y + h / 2), close=True),
                P((x + w / 2, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2)))


def calendar(x, y, w=380, h=440) -> skia.Path:
    """台历：外框 + 顶部横条 + 两个装订环。"""
    top = y - h / 2
    return join(rect(x, y, w, h, 18), P((x - w / 2, top + 100), (x + w / 2, top + 100)),
                circle(x - w * 0.25, top, 16), circle(x + w * 0.25, top, 16))


def moon(x, y, r=60) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def sofa(x, y, s=1.0) -> skia.Path:
    """沙发：(x, y) 为地面中点。"""
    return join(rect(x, y - 270 * s, 640 * s, 150 * s, 24 * s), rect(x, y - 160 * s, 640 * s, 100 * s, 20 * s),
                rect(x - 345 * s, y - 190 * s, 70 * s, 180 * s, 26 * s), rect(x + 345 * s, y - 190 * s, 70 * s, 180 * s, 26 * s),
                P((x - 290 * s, y - 110 * s), (x - 290 * s, y)), P((x + 290 * s, y - 110 * s), (x + 290 * s, y)))


def cloud(x, y, w, h, n=9) -> skia.Path:
    """一团雾（轮廓）：椭圆一圈鼓包。"""
    p = skia.Path()
    pts = [(x + math.cos(2 * math.pi * i / n) * w / 2, y + math.sin(2 * math.pi * i / n) * h / 2) for i in range(n + 1)]
    p.moveTo(*pts[0])
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        p.quadTo(x + math.cos(a) * w * 0.68, y + math.sin(a) * h * 0.72, *pts[i + 1])
    return p


def helm(x, y, r=90) -> skia.Path:
    """船舵：外圈 + 轴心 + 八根带把手的辐条。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.3)]
    for i in range(8):
        a = i / 8 * 2 * math.pi + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        parts.append(P((x + ca * r * 0.3, y + sa * r * 0.3), (x + ca * r * 1.32, y + sa * r * 1.32)))
        parts.append(circle(x + ca * r * 1.36, y + sa * r * 1.36, r * 0.07))
    return join(*parts)


def grips(x, y, r, idx) -> skia.Path:
    """舵圈上的握痕：idx 为第几道（从 0 起，共 8 个位置，落在两根辐条之间），每道是横跨轮圈的三条短线。"""
    parts = []
    for i in idx:
        a = (-90 + i * 45) / 180 * math.pi
        for d in (-0.12, 0.0, 0.12):
            b0 = a + d
            parts.append(P((x + math.cos(b0) * r * 0.84, y + math.sin(b0) * r * 0.84),
                           (x + math.cos(b0) * r * 1.16, y + math.sin(b0) * r * 1.16)))
    return join(*parts)


def grandpa(x, y, s=1.0) -> skia.Path:
    """老大“本能脑”：驼背、白胡子、拄拐的老爷爷。(x, y) 为脚底。"""
    hy = y - 285 * s
    hook = skia.Path()
    hook.moveTo(x + 70 * s, hy + 150 * s)
    hook.quadTo(x + 72 * s, hy + 108 * s, x + 40 * s, hy + 118 * s)
    return join(circle(x - 10 * s, hy, 45 * s),
                P((x - 45 * s, hy + 18 * s), (x - 10 * s, hy + 78 * s), (x + 25 * s, hy + 18 * s)),
                P((x - 10 * s, hy + 45 * s), (x - 30 * s, hy + 120 * s), (x - 5 * s, y - 120 * s)),
                P((x - 55 * s, y), (x - 5 * s, y - 120 * s), (x + 45 * s, y)),
                P((x - 22 * s, hy + 95 * s), (x + 70 * s, hy + 160 * s)),
                P((x + 70 * s, y), (x + 70 * s, hy + 150 * s)), hook)


def uncle(x, y, s=1.0) -> skia.Path:
    """老二“情绪脑”：戴耳机、攥着手机的大叔。(x, y) 为脚底。"""
    hy = y - 290 * s
    band = skia.Path()
    band.addArc(skia.Rect.MakeXYWH(x - 58 * s, hy - 62 * s, 116 * s, 116 * s), 180, 180)
    return join(stick(x, y, s, "hold"), band, rect(x - 54 * s, hy, 22 * s, 44 * s, 8 * s),
                rect(x + 54 * s, hy, 22 * s, 44 * s, 8 * s))


def baby(x, y, s=1.0) -> skia.Path:
    """老三“理智脑”：大头、戴围嘴的小宝宝，双手举过头。(x, y) 为脚底。"""
    hy = y - 150 * s
    r = 55 * s
    bib = skia.Path()
    bib.addArc(skia.Rect.MakeXYWH(x - 30 * s, hy + r - 22 * s, 60 * s, 50 * s), 0, 180)
    eyes = skia.Path()
    eyes.addCircle(x - 18 * s, hy - 4 * s, 3.5 * s)
    eyes.addCircle(x + 18 * s, hy - 4 * s, 3.5 * s)
    hands = join(P((x - 24 * s, hy + r + 8 * s), (x - 70 * s, hy - 50 * s)),
                 P((x + 24 * s, hy + r + 8 * s), (x + 70 * s, hy - 50 * s)))
    return join(circle(x, hy, r), eyes, P((x - 8 * s, hy + 22 * s), (x + 8 * s, hy + 22 * s)), bib,
                P((x, hy + r), (x, y - 50 * s)), P((x - 34 * s, y), (x, y - 50 * s), (x + 34 * s, y)), hands)


def old_head(x, y, r=44) -> skia.Path:
    """雾里探出来的老大：圆脑袋 + 白胡子 + 眯眼。"""
    return join(circle(x, y, r), P((x - r * 0.8, y + r * 0.4), (x, y + r * 1.7), (x + r * 0.8, y + r * 0.4)),
                P((x - r * 0.5, y - r * 0.15), (x - r * 0.2, y - r * 0.15)), P((x + r * 0.2, y - r * 0.15), (x + r * 0.5, y - r * 0.15)))


def fun_head(x, y, r=44) -> skia.Path:
    """雾里探出来的老二：圆脑袋 + 耳机 + 咧嘴。"""
    band = skia.Path()
    band.addArc(skia.Rect.MakeXYWH(x - r * 1.3, y - r * 1.4, r * 2.6, r * 2.6), 180, 180)
    grin = skia.Path()
    grin.addArc(skia.Rect.MakeXYWH(x - r * 0.5, y - r * 0.1, r, r * 0.7), 10, 160)
    eyes = skia.Path()
    eyes.addCircle(x - r * 0.35, y - r * 0.2, 4)
    eyes.addCircle(x + r * 0.35, y - r * 0.2, 4)
    return join(circle(x, y, r), band, rect(x - r * 1.25, y, r * 0.5, r, 8), rect(x + r * 1.25, y, r * 0.5, r, 8), grin, eyes)


def sitter(x, ys, mood="sad") -> skia.Path:
    """瘫坐在沙发上的小林：(x, ys) 为屁股落在坐垫上的点。"""
    hx, hy = x - 16, ys - 185
    p = skia.Path()
    p.addCircle(hx - 12, hy - 6, 3.5)
    p.addCircle(hx + 12, hy - 6, 3.5)
    if mood == "smile":
        p.addArc(skia.Rect.MakeXYWH(hx - 15, hy - 2, 30, 22), 20, 140)
    else:
        p.addArc(skia.Rect.MakeXYWH(hx - 14, hy + 10, 28, 18), 200, 140)
    return join(circle(hx, hy, 34), p, P((x - 12, ys - 150), (x, ys)), P((x, ys), (x + 105, ys + 6), (x + 115, ys + 165)),
                P((x - 10, ys - 110), (x + 55, ys - 20)))


# ---------------------------------------------------------------- 便签与雾：一张便签管五屏（场景 1、4、8–10、13）

NX, NY, NW, NH = 1250, 1100, 620, 860
LX = 1210                                       # 便签上三行字的中线
ROWS = (920, 1150, 1380)
PLANS = ("学点东西", "多运动", "整理下简历")
BOXX = 1480                                     # 每行后面的空框
JD = None                                       # drop 镜头
JR = [None, None, None]                         # 三条改写各自的镜头

_rng = random.Random(8)
PUFFS = {0: [], 1: [], 2: []}
for _r, _y in enumerate(ROWS):
    for _x in range(990, 2170, 105):
        PUFFS[_r].append((_x + _rng.uniform(-20, 20), _y + _rng.uniform(-38, 38), _rng.uniform(80, 108), _rng.uniform(0, 0.45)))
for _x in range(990, 1560, 110):               # 顶上一排盖住“这周”
    PUFFS[0].append((_x, 800 + _rng.uniform(-20, 20), _rng.uniform(70, 90), _rng.uniform(0, 0.3)))
for _x in range(720, 1320, 95):                # 底下一团：老大老二藏在这里
    PUFFS[2].append((_x, 1610 + _rng.uniform(-25, 25), _rng.uniform(72, 96), _rng.uniform(0.2, 0.5)))


def fog_state(r, T):
    """第 r 行雾的 (浓度, 压下进度, 散开进度)：drop 第 0 拍压下；改写那屏第 0 拍变薄，第 7 拍散开。"""
    if JD is None or T < b.t_of(JD, 0):
        return 0.0, 0.0, 0.0
    slam = span(JD, 0, 0.9, T)
    a, cl = 0.94, 0.0
    j = JR[r]
    if j is not None:
        a += (0.5 - a) * ease_in_out(span(j, 0, 0.8, T))
        cl = ease_in_out(span(j, 7, 7.9, T))
        a *= 1 - cl
    return a, slam, cl


def fog_fn(c, k, T):
    for r in range(3):
        a, slam, cl = fog_state(r, T)
        if a <= 0.01:
            continue
        pts = []
        for x, y, rad, d in PUFFS[r]:
            f = clamp01((slam - d) / 0.55)
            if f <= 0:
                continue
            e = ease_out(f)
            pts.append((x + (x - 1500) * 0.35 * cl, y - 260 * (1 - e) - 40 * cl, rad * (0.4 + 0.6 * e) * (1 + 0.5 * cl)))
        c.saveLayerAlpha(None, int(255 * a))
        for x, y, rad in pts:
            c.drawCircle(x, y, rad, K.paint(FOG_LINE, 1, 12))
        for x, y, rad in pts:
            c.drawCircle(x, y, rad, K.paint(FOG_FILL))
        c.restore()
    return None


# ---------------------------------------------------------------- drop：老大老二把小林拖回沙发

GH, UH = (830, 1650), (1170, 1665)              # 雾里探出的两个脑袋
SOFA = (1000, 2050, 0.8)
SEAT = (1000, 1882)
STAND = (1750, 2050)
PS = 0.75


def drop_fn(c, k, T):
    """第 2 拍小林出现；第 3 拍两个哥哥探头伸手；第 4–5 拍拖回沙发；第三条改完雾散，两个哥哥跟着消失。"""
    j = JD
    a2 = fog_state(2, T)[0] / 0.94
    appear = span(j, 2, 2.6, T)
    reach = span(j, 3, 3.8, T)
    drag = ease_in_out(span(j, 4, 5, T))
    if drag < 1:
        x = STAND[0] + (SEAT[0] + 60 - STAND[0]) * drag
        y = STAND[1] - 70 * math.sin(math.pi * drag)
        rot = -16 * math.sin(math.pi * clamp01(drag * 1.4))
        man = join(stick(x, y, PS, "up"), face(x, y, PS, "sad"))
        ink(c, moved(man, s=pop_s(appear), ax=x, ay=y, rot=rot), BLACK, 9)
        tx, ty = x, y - 210 * PS
    else:
        ink(c, sitter(*SEAT, "smile" if a2 < 0.05 else "sad"), BLACK, 9)
        tx, ty = SEAT[0] - 10, SEAT[1] - 110
    if a2 <= 0.01 or reach <= 0:
        return (STAND[0], STAND[1] - 300 * PS) if k < 1 and drag == 0 else None
    c.saveLayerAlpha(None, int(255 * a2))
    s = pop_s(reach)
    for (hx, hy), head, col in ((GH, old_head, BLACK), (UH, fun_head, RED)):
        ink(c, moved(head(hx, hy), s=s, ax=hx, ay=hy), col, 8)
        arm = skia.Path()
        arm.moveTo(hx + 30, hy + 45)
        arm.quadTo((hx + tx) / 2, max(hy, ty) + 90, tx + (hx - tx) * 0.08, ty)
        part, tip = partial(arm, reach)
        ink(c, part, col, 9)
        if reach >= 1:
            ink(c, circle(tx + (hx - tx) * 0.08, ty, 18), col, 8)
    c.restore()
    return None


# ---------------------------------------------------------------- 收藏夹：场景 3 越拉越长，场景 12 收起

FAV = (3050, 700)
FAVS = ("自律的七个方法", "早起攻略", "拖延怎么治", "时间管理课", "执行力清单", "高效人的习惯", "专注训练营")
J3 = None
J12 = None


def fav_n(T):
    n = len(FAVS) * ease_in_out(span(J3, 2, 6, T))
    if J12 is not None:
        n *= 1 - ease_in_out(span(J12, 0, 1.4, T))
    return n


def fav_fn(c, k, T):
    x, y = FAV
    n = fav_n(T)
    bottom = y + 50 + 30 + n * 90
    c.drawPath(rect(x, (y + 50 + bottom) / 2, 540, bottom - y - 50, 16), wb.marker(BLACK, 8))
    K.rr(c, x, y, 540, 100, 16, "#FFFFFF")
    c.drawPath(rect(x, y, 540, 100, 16), wb.marker(BLACK, 9))
    K.text(c, "收藏夹", x, y + 4, 56, "hand", BLACK)
    for i, s in enumerate(FAVS):
        f = clamp01(n - i)
        if f <= 0:
            break
        yy = y + 110 + i * 90
        K.text(c, s, x + 20, yy, 48, "hand", BLUE, f)
        K.dot(c, x - 230, yy, 9, LAMP, f)
    return (x + 200, bottom - 30) if 0 < k < 1 else None


def fold_fn(c, k, T):
    """场景 12：手跟着往上收（列表本身由 fav_fn 画）。"""
    return (FAV[0] + 200, FAV[1] + 50 + fav_n(T) * 90) if k < 1 else None


# ---------------------------------------------------------------- 周一 → 周日（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("周一的三条计划", "周一 · 小林写计划", (1250, 1100, 0.85), bars=2)
L(note(NX, NY, NW, NH), 0, 0.9, BLACK, 10, sfx="wood_high")
T("这周：", LX - 150, 790, 60, GREEN, k0=1, k1=1.8, sfx="pop")
for n, s in enumerate(PLANS):
    T(s, LX, ROWS[n], 62, BLUE, k0=2 + n, sfx="pop")

DAYS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
CAL = (330, 1100)


def flip_fn(c, k, T):
    """台历一页页翻：周一 → 周日，每翻一页压扁一下。"""
    x, y = CAL[0], CAL[1] + 50
    v = k * (len(DAYS) - 0.01)
    i = min(len(DAYS) - 1, int(v))
    f = v - i
    sy = 1.0 if k >= 1 else max(0.15, abs(math.cos(math.pi * min(1.0, f * 2.2))) if f < 0.45 else 1.0)
    with K.at(c, x, y, s=1.0, sy=sy):
        K.text(c, DAYS[i], 0, 0, 110, "hand", RED if i == len(DAYS) - 1 else BLACK)
    return (x + 120, y - 40) if k < 1 else None


scene("周日晚上", "一周后", (850, 1100, 0.75))
L(join(*[rect(BOXX, y, 56, 56, 8) for y in ROWS]), 0, 0.9, BLACK, 7, sfx="wood_high")
L(calendar(*CAL), 1, 1.9, BLACK, 9, sfx="wood_low")
C(flip_fn, 2, 4.6, sfx="shaker")
H(3, "shaker", 0.6)
L(moon(CAL[0], 760, 52), 5, 5.8, BLUE, 8, sfx="pop")
T("一条没动", CAL[0], 1420, 60, RED, k0=6, k1=7, sfx="rim")

scene("道理都懂", "收藏夹", (2950, 1100, 0.85))
J3 = J()
L(join(stick(2500, 1550, 0.8, "shrug"), face(2500, 1550, 0.8, "flat")), 0, 0.9, BLACK, 9, sfx="wood_low")
L(bubble(2500, 1100, 260, 130, -1), 1, 1.6, BLACK, 8, sfx="pop")
T("都懂", 2500, 1100, 60, k0=1.6, k1=2.4)
C(fav_fn, 2, 6, sfx="pop")
H(3, "pop")
H(4, "pop")
H(5, "pop")
T("收藏 128 条", FAV[0], 590, 60, RED, k0=6, k1=7.5, sfx="rim")
DROP_VIEW = (1450, 1400, 0.6)
b.move(J3, 10, DROP_VIEW, dur=1.0)            # 停够 2 拍后先回到便签，drop 第 0 拍雾压下时镜头已就位

# ---------------------------------------------------------------- drop：一团雾（场景 4）

scene("一团雾", "被雾吞掉", DROP_VIEW, shake=[0], flashes=[0])
JD = J()
C(fog_fn, 0, 0.9, sfx="kick")
L(sofa(*SOFA), 1, 1.9, BLACK, 9, sfx="wood_low")
C(drop_fn, 2, 5, sfx="pop")
H(3, "tom")
H(4, "shaker")
H(5, "tom")
T("拖回沙发", 1850, 1800, 84, RED, k0=6, k1=7, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 5–7）

scene("有本书讲过", "认知觉醒 · 周岭", (800, 3700, 0.85))
L(book(650, 3720, 440, 300), 0, 0.9, BLACK, 10, sfx="wood_low")
T("《认知觉醒》", 650, 3450, 72, GREEN, k0=1, k1=2.5, sfx="pop")
T("周岭", 650, 3990, 56, k0=3, k1=3.8, sfx="pop")
L(helm(1130, 3680, 100), 4, 4.9, GREEN, 8, sfx="wood_high")
T("08", 1130, 3910, 80, RED, k0=5, k1=5.8, sfx="ding")
T("第六章 行动力", 800, 4180, 56, k0=6, k1=7.5, sfx="pop")

scene("看不清就躲", "书中观点 · 说不清", (1900, 3700, 0.85))
L(cloud(2050, 3600, 460, 300), 0, 0.9, FOG_LINE, 10, sfx="wood_high")
T("？？", 2050, 3600, 90, k0=1, k1=1.8, sfx="pop")
L(join(stick(1600, 4100, 0.8, "up"), face(1600, 4100, 0.8, "sad")), 2, 2.9, BLACK, 9, sfx="wood_low")
L(arrow((1660, 4170), (1430, 4170), 0.0, 36), 3, 3.7, RED, 9, sfx="rim")
T("说不清，就想躲", 1850, 3260, 66, k0=5, k1=6.75, sfx="pop")

BLK = (2900, 3700, 900, 260)


def block_fn(j):
    """一大块：第 0 拍描出来，第 3 拍“咔”地裂成三小块往两边散开。"""

    def fn(c, k, T):
        x, y, w, h = BLK
        d = span(j, 0, 0.9, T)
        if d < 1:
            part, tip = partial(rect(x, y, w, h, 20), d)
            ink(c, part, BLACK, 10)
            return tip
        u = ease_out(span(j, 3, 3.8, T))
        if u <= 0:
            ink(c, rect(x, y, w, h, 20), BLACK, 10)
            return None
        u = u * (1 + 0.2 * math.sin(math.pi * u))
        for i, dx in enumerate((-90, 0, 90)):
            ink(c, rect(x - w / 3 + i * w / 3 + dx * u, y - 14 * math.sin(math.pi * min(1, u)), w / 3 - 10 * u, h, 20), BLACK, 10)
        return None

    return fn


scene("拆小写具体", "书中观点 · 拆细写具体", (2900, 3700, 0.85))
C(block_fn(J()), 0, 3.8, sfx="wood_low")
T("学点东西", 2900, 3380, 70, k0=1, k1=2, sfx="pop")
L(join(*[P((xx, y0), (xx, y0 + 44)) for xx in (2750, 3050) for y0 in range(3530, 3870, 70)]), 2, 2.8, RED, 8, sfx="rim")
H(3, "tom")
for n, s in enumerate(("哪天", "几点", "做哪步")):
    T(s, 2510 + 390 * n, 3700, 60, BLUE, k0=4 + n, k1=4.8 + n, sfx="pop")
L(check(2900, 3990, 50), 7, 7.7, GREEN, 10, sfx="ding")

# ---------------------------------------------------------------- 回到便签：一条条改写，雾一块块散（场景 8–10）

REWRITE = (("周二晚八点", "看课第一节"), ("周三下班", "楼下走两圈"), ("周四午休", "改第一段"))
for n, (a, z) in enumerate(REWRITE):
    y = ROWS[n]
    scene(f"第{'一二三'[n]}条改写", f"改写 · 第{'一二三'[n]}条", (1560, 1050 + 90 * n, 0.85))
    JR[n] = J()
    H(0, "shaker")
    w = 62 * len(PLANS[n])
    L(P((LX - w / 2 - 16, y + 6), (LX + w / 2 + 16, y - 4)), 1, 1.6, RED, 10, sfx="rim")
    L(arrow((1560, y), (1770, y), -0.15, 34), 2, 2.7, BLUE, 9, sfx="wood_high")
    T(a, 1930, y - 42, 54, BLUE, k0=3, sfx="pop")
    T(z, 1930, y + 42, 54, BLUE, k0=5, sfx="pop")
    H(7, "ding")
    if n == 2:
        b.erase(J(), 7, 7.8, 1850, 1800, 420, 140)     # 雾散尽，“拖回沙发”一起擦掉

# ---------------------------------------------------------------- 书中观点：先迈步、改一点（场景 11–12）

STEPS = [(2750 + 230 * i, 2800 - 130 * i) for i in range(3)]
START = (2580, 2900)


def climb_fn(j):
    """小林在地上站着；第 3、4、5 拍各迈一步，脚落下那一块台阶才亮。"""

    def fn(c, k, T):
        pos = START
        for i, st in enumerate(STEPS):
            u = ease_in_out(span(j, 3 + i, 3.7 + i, T))
            if u <= 0:
                break
            prev = START if i == 0 else STEPS[i - 1]
            pos = (prev[0] + (st[0] - prev[0]) * u, prev[1] + (st[1] - prev[1]) * u - 70 * math.sin(math.pi * u))
            if u >= 1:
                sx, sy = st
                K.rr(c, sx, sy + 25, 220, 50, 10, LAMP, 0.55)
                c.drawPath(rect(sx, sy + 25, 220, 50, 10), wb.marker(BLACK, 8))
                for dx in (-80, 0, 80):
                    c.drawPath(P((sx + dx, sy + 70), (sx + dx * 1.3, sy + 110)), wb.marker(LAMP, 6))
        c.drawPath(P((START[0] - 110, START[1]), (START[0] + 110, START[1])), wb.marker(BLACK, 8))
        man = join(stick(pos[0], pos[1], 0.6, "point"), face(pos[0], pos[1], 0.6, "smile"))
        ink(c, moved(man, s=pop_s(span(j, 0, 0.6, T)), ax=pos[0], ay=pos[1]), BLACK, 8)
        return None

    return fn


scene("先干，结果后来", "书中观点 · 先动手", (3000, 2500, 0.85))
C(climb_fn(J()), 0, 5.7, sfx="wood_low")
L(cloud(3260, 2160, 440, 240), 1, 1.9, FOG_LINE, 9, sfx="wood_high")
T("结果", 3260, 2160, 64, k0=2, k1=2.8, sfx="pop")
H(3, "wood_high")
H(4, "wood_low")
H(5, "ding")
T("走一步，亮一块", 2950, 3060, 62, GREEN, k0=6, k1=7.5, sfx="pop")

scene("改一点就行", "书中观点 · 改变一点", (2950, 1100, 0.85))
J12 = J()
C(fold_fn, 0, 1.4, sfx="shaker")
L(rect(2850, 1000, 90, 90, 12), 2, 2.6, BLACK, 9, sfx="wood_high")
L(check(2850, 1000, 50), 3, 3.6, GREEN, 12, sfx="ding")
T("周二看了第一节", 3190, 1000, 54, BLUE, k0=4, k1=5.75, sfx="pop")
T("书中：懂百点，不如改一点", 2950, 1300, 54, GREEN, k0=6, k1=8.0, sfx="pop")

# ---------------------------------------------------------------- 新的周日（场景 13）

HD = (2050, 2100, 280)
FY = 2260
scene("新的周日", "新的周日", (1380, 1600, 0.5))
L(join(*[check(BOXX + 6, y - 6, 40) for y in ROWS]), 1, 1.9, GREEN, 12, sfx="pop")
neck = join(P((HD[0] - 70, HD[1] + HD[2] - 7), (HD[0] - 70, HD[1] + HD[2] + 60)),
            P((HD[0] + 70, HD[1] + HD[2] - 7), (HD[0] + 70, HD[1] + HD[2] + 60)))
L(join(circle(*HD), neck), 2, 2.9, BLACK, 10, sfx="wood_low")


def bros_fn(c, k, T):
    s = pop_s(k)
    if s <= 0:
        return None
    for path, ax, col in ((grandpa(1880, FY, 0.55), 1880, BLACK), (uncle(2020, FY, 0.55), 2020, RED),
                          (baby(2190, FY, 0.6), 2190, BLUE)):
        ink(c, moved(path, s=s, ax=ax, ay=FY), col, 7)
    return None


C(bros_fn, 3, 3.6, sfx="pop")
HM = (2190, 2060, 52)
L(join(helm(*HM), grips(*HM, range(7))), 4, 4.9, GREEN, 6, sfx="wood_high")
L(grips(*HM, [7]), 5, 5.5, RED, 9, sfx="ding")
T("握痕 +1", 2250, 1650, 90, GREEN, k0=6, k1=7, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，第 4 拍推到评论区

FAR = (1800, 2700, 0.27)
COMMENT = (1800, 5100, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
L(join(rect(1800, 5050, 1250, 480, 40), P((1500, 5290), (1440, 5380), (1600, 5290))), 5, 5.9, BLACK, 9,
  sfx="wood_high")
T("你哪条计划最想改？", 1800, 4970, 66, RED, k0=6, k1=8.25, sfx="pop")
T("下一讲：领导一句话，郁闷一整天？", 1800, 5150, 50, k0=9, k1=13, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "clear", "清晰力", "道理都懂，为啥就是不动？", ACC, b.shots,
                 [f"{BOOK}第二章第一节“模糊：人生是一场消除模糊的比赛”（转述）",
                  f"{BOOK}第六章 行动力：第一节 清晰、第二节“傻瓜”、第三节 行动（转述）"],
                 "道理都懂|为啥就是【不动】", SQUARE_SHOT,
                 ["书中观点均为转述，不是逐字引文：说不清的事会一直耗人，大脑本能地躲开它，看清、拆解才能化解（第二章第一节）；"
                  "把目标拆细、写具体，行动力才起得来（第六章第一节）；想先看到结果再动手的人，往往看不到结果（第六章第二节）；"
                  "懂得百点不如改变一点（第六章第三节，上屏缩写为“懂百点，不如改一点”）。",
                  "“雾”是对书中“模糊”的画面化；雾里探出老大、老二把人拖回沙发，以及脑内三兄弟（本能脑、情绪脑、理智脑宝宝）"
                  "与船舵握痕为系列视觉角色，据第一章“三重大脑”与第三章“思维舵手”的比喻，均为通俗化示意；本讲舵上第 8 道握痕。",
                  "小林周一的三条计划（学点东西 / 多运动 / 整理下简历）、收藏夹里的条目与“收藏 128 条”均为现实场景示意，"
                  "数字不是数据，不指向任何具体公司或个人。",
                  "三条改写（周二晚八点看课第一节 / 周三下班楼下走两圈 / 周四午休改第一段）与“哪天 / 几点 / 做哪步”的拆法"
                  "为据书中思路整理的做法示意。"],
                 tags="#拖延 #行动力")
    return b.attach(ep)
