"""08 拖延的心里话（白板手绘版）：这几句心里话，你中了几句。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：最后 4 拍不出新笔画）。
叙事（E 自测清单）：整讲围着白板左边一张竖长的大清单走，观众跟着在心里打勾——
打工人开局（小周对着“待办”便利贴发呆，头上冒出一串只有“……”的对话框 → 一支红笔、一个空方框：中了一句就在心里打个勾）→
书中观点（亮书《拖延心理学》，博克和袁；书里列了拖延的人常有的一串心里话，卷轴展开，绿箭头指向左边空白处；
drop 时大纸“拖延的心里话”砸在白板上，六个空方框，明天怪兽从纸后探头，小周指着清单问“中了几句”）→
逐句自测（相机沿清单往下推，一屏一到两句：必须完美、做不好就别做 / 事情该轻松，羽毛对秤砣 / 不做比做砸安全，小周缩进壳里 /
等个标准答案，小周对着巨大的问号等 / 怕人看到真我，小周举面具挡脸；每句都弹出红勾）→
解读（右边三根柱子“1–2 / 3–4 / 5–6”越来越高，绿箭头指向明天怪兽：勾越多，越像在躲；分档为示意）→
具体做法（回到清单：划掉“我必须做到完美”，蓝字改成“先交个能看的” / 划掉“不做，比做砸安全”，改成“做一点，看看会怎样”，
壳里伸出一只手 / 把改过的那句写在便利贴上贴到显示器边，明天怪兽比虚线圈小了一圈）→
拉远看全板 → 评论区互动（你中了几句、最响的是哪句）+ 下一讲片名。
书中观点为转述（Jane B. Burka & Lenora M. Yuen, Procrastination: Why You Do It, What to Do About It Now, 2008 修订版，
第1章所列拖延者常有的一组信念；中译本《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009，第1章；条目与中译措辞需核实，
上屏六句只取大意、改成口语）；勾数分档、改写句与便利贴做法为示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, desk,
                               face, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#7A4FA3"
SQUARE_SHOT = 12                # 场景 13：显示器边贴便利贴，小周举手笑，明天怪兽缩小

b = Board(size=(3600, 7200))


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


# ---------------------------------------------------------------- 本讲画法

def flip(path: skia.Path, x) -> skia.Path:
    """以竖线 x 为轴左右镜像（让小周朝左指）。"""
    p = skia.Path(path)
    p.transform(skia.Matrix.MakeAll(-1, 0, 2 * x, 0, 1, 0, 0, 0, 1))
    return p


def badge(x, y, s=1.0) -> skia.Path:
    """配合 stick 的工牌（挂绳 + 卡片）：(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 22 * s, hy + 45 * s), (x + 18 * s, hy + 130 * s), (x + 30 * s, hy + 45 * s)),
                rect(x + 18 * s, hy + 155 * s, 38 * s, 50 * s, 5 * s))


def zhou(x, y, s=0.75, arms="down", mood="flat", with_face=True) -> skia.Path:
    """小周：火柴人 + 胸前工牌。"""
    parts = [stick(x, y, s, arms), badge(x, y, s)]
    if with_face:
        parts.append(face(x, y, s, mood))
    return join(*parts)


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


def belly(x, y, r, k0, k1=None, sfx=None):
    T("明天", x, y + 0.4 * r, 0.48 * r, RED, k0=k0, k1=k1, sfx=sfx)


def dots(x, y, gap=34, r=9) -> skia.Path:
    """对话框里的“……”：三个小圆点。"""
    return join(*[circle(x + (i - 1) * gap, y, r) for i in range(3)])


def pen(x, y, ang=-35, length=300, w=52) -> skia.Path:
    """红马克笔：(x, y) 为笔尖，ang 为笔身方向（度，0 指向右）。"""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    tip = 70

    def at(d, o):
        return (x + ux * d + nx * o, y + uy * d + ny * o)

    body = P(at(tip, -w / 2), at(length, -w / 2), at(length, w / 2), at(tip, w / 2), close=True)
    cone = P(at(tip, -w / 2), at(0, 0), at(tip, w / 2))
    cap = P(at(length - 80, -w / 2), at(length - 80, w / 2))
    return join(body, cone, cap)


def scroll(x, y, w=640, h=300) -> skia.Path:
    """展开的卷轴：上下两根卷棍 + 纸面两边。"""
    l, r, t, bt = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    return join(rect(x, t, w + 60, 46, 23), rect(x, bt, w + 60, 46, 23),
                P((l + 10, t + 23), (l + 10, bt - 23)), P((r - 10, t + 23), (r - 10, bt - 23)))


def shell(x, y, w=320, h=210) -> skia.Path:
    """小周缩进壳里：一只半圆壳 + 壳纹 + 从壳边探出的半个脑袋。(x, y) 为壳底中点。"""
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeXYWH(x - w / 2, y - h, w, 2 * h), 180, 180)
    parts = [dome, P((x - w / 2 - 20, y), (x + w / 2 + 20, y)),
             P((x - w * 0.22, y - h * 0.86), (x - w * 0.1, y - h * 0.45), (x - w * 0.3, y)),
             P((x + w * 0.22, y - h * 0.86), (x + w * 0.1, y - h * 0.45), (x + w * 0.3, y)),
             P((x - w * 0.1, y - h * 0.45), (x + w * 0.1, y - h * 0.45))]
    return join(*parts)


def peek_head(x, y, r=38) -> skia.Path:
    """壳边探出的脑袋：圆头 + 两只眼 + 一条平嘴。"""
    p = circle(x, y, r)
    p.addCircle(x - 12, y - 6, 4)
    p.addCircle(x + 10, y - 6, 4)
    p.moveTo(x - 12, y + 16)
    p.lineTo(x + 10, y + 16)
    return p


def feather(x, y, s=1.0) -> skia.Path:
    """一片羽毛（想象里的“轻松”）：弯弯的羽轴 + 两侧羽丝。"""
    spine = skia.Path()
    spine.moveTo(x - 70 * s, y + 90 * s)
    spine.quadTo(x - 10 * s, y, x + 60 * s, y - 100 * s)
    parts = [spine]
    for i in range(1, 6):
        f = i / 6
        px, py = x - 70 * s + 130 * s * f, y + 90 * s - 190 * s * f
        parts += [P((px, py), (px - 55 * s, py - 25 * s)), P((px, py), (px + 30 * s, py + 50 * s))]
    return join(*parts)


def weight(x, y, w=200, h=150) -> skia.Path:
    """秤砣（做起来的“沉”）：梯形砣身 + 提环。(x, y) 为砣身中心。"""
    ring = skia.Path()
    ring.addArc(skia.Rect.MakeXYWH(x - 40, y - h / 2 - 60, 80, 80), 180, 180)
    return join(P((x - w * 0.32, y - h / 2), (x + w * 0.32, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2),
                  close=True), ring, P((x - 40, y - h / 2 - 20), (x - 40, y - h / 2)), P((x + 40, y - h / 2 - 20), (x + 40, y - h / 2)))


def qmark(x, y, s=1.0) -> skia.Path:
    """巨大的问号：(x, y) 为问号中心。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - 70 * s, y - 130 * s, 140 * s, 140 * s), 180, 270)
    p.moveTo(x, y + 10 * s)
    p.lineTo(x, y + 55 * s)
    p.addCircle(x, y + 105 * s, 12 * s)
    return p


def mask(x, y, w=120, h=150) -> skia.Path:
    """笑脸面具 + 手柄：(x, y) 为面具中心。"""
    m = skia.Path()
    m.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    m.addOval(skia.Rect.MakeXYWH(x - 38, y - 30, 28, 16))
    m.addOval(skia.Rect.MakeXYWH(x + 10, y - 30, 28, 16))
    m.addArc(skia.Rect.MakeXYWH(x - 32, y - 5, 64, 44), 20, 140)
    return join(m, P((x + 30, y + h / 2 - 10), (x + 70, y + h / 2 + 45)))


def monitor(x, y, w=560, h=340) -> skia.Path:
    """显示器：屏幕 + 支架 + 底座。(x, y) 为屏幕中心。"""
    return join(rect(x, y, w, h, 16), rect(x, y, w - 50, h - 50, 8), P((x, y + h / 2), (x, y + h / 2 + 80)),
                P((x - 120, y + h / 2 + 80), (x + 120, y + h / 2 + 80)))


def dashed_circle(x, y, r, n=18) -> skia.Path:
    """虚线圈：怪兽原来的个头。"""
    p = skia.Path()
    for i in range(n):
        a0 = i / n * 360
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), a0, 360 / n * 0.55)
    return p


def rays(x, y, r0, r1, n=8, a0=0) -> skia.Path:
    parts = []
    for i in range(n):
        a = math.radians(a0 + i * 360 / n)
        parts.append(P((x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))))
    return join(*parts)


def note_fn(x, y, w, h):
    """黄便利贴底色。"""

    def fn(c, k, t):
        K.rr(c, x, y, w, h, 8, "#FFE27A", 0.9 * k)
        return None

    return fn


def slam_fn(x, y, w, h):
    """大纸从镜头前砸到白板上：由大变小、由虚到实，落下时一圈灰影。"""

    def fn(c, k, t):
        e = ease_out(k)
        s = 1.35 - 0.35 * e
        c.save()
        c.translate(x, y)
        c.scale(s, s)
        c.translate(-x, -y)
        if k >= 1:
            K.rr(c, x + 24, y + 30, w, h, 18, "#9AA0A8", 0.35)
        K.rr(c, x, y, w, h, 18, "#FFFDF4", 0.25 + 0.75 * e)
        c.drawPath(rect(x, y, w, h, 18), wb.marker(BLACK, 12, 0.3 + 0.7 * e))
        c.restore()
        return None

    return fn


def peek_fn(path: skia.Path, clip_rect, color=BLACK, width=9):
    """从纸后面探头：逐笔画出 path，被纸挡住的部分不画。"""

    def fn(c, k, t):
        part, _ = wb.partial(path, k)
        c.save()
        c.clipRect(clip_rect, skia.ClipOp.kDifference)
        c.drawPath(part, wb.marker(color, width))
        c.restore()
        return None

    return fn


# ---------------------------------------------------------------- 清单的位置（白板左边一张竖长大纸）

PX, PY, PW, PH = 1050, 4050, 1660, 3420          # 纸：x 220–1880，y 2340–5760
TITLE_Y = 2520
ROWS = [("我必须做到完美", 2900), ("做不好，干脆别做", 3420), ("事情都该轻轻松松", 3940),
        ("不做，比做砸安全", 4460), ("有标准答案，找到再动", 4980), ("露出真我，就没人喜欢", 5500)]
BOX_X, TXT_X, RS = 400, 500, 76                   # 方框中心 x、句子左边 x、句子字号
PAPER = skia.Rect.MakeXYWH(PX - PW / 2, PY - PH / 2, PW, PH)


def row_w(i):
    return K.text_w(ROWS[i][0], RS, "hand")


def row_text(i, k0, sfx="pop"):
    s, y = ROWS[i]
    T(s, TXT_X + row_w(i) / 2, y, RS, k0=k0, sfx=sfx)


def tick(i, k0, sfx="ding"):
    L(check(BOX_X, ROWS[i][1], 48), k0, k0 + 0.6, RED, 12, sfx=sfx)


def strike(i, k0):
    y = ROWS[i][1]
    L(P((TXT_X - 20, y + 4), (TXT_X + row_w(i) + 20, y - 4)), k0, k0 + 0.8, RED, 10, sfx="rim")


def row_view(i, dy=0):
    return (1050, ROWS[i][1] + dy, 0.68)


# ---------------------------------------------------------------- 开局：拖的时候心里说啥（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

b.shot("拖的时候心里说啥", "灵魂拷问", (900, 900, 0.85), bars=2)
L(desk(1050, 1150, 480), 0, 0.9, sfx="wood_high")
L(zhou(650, 1400, 0.8, "down"), 1, 1.9, sfx="wood_high")
b.custom(J(), 2, 2.3, note_fn(1270, 960, 200, 130))
L(rect(1270, 960, 200, 130, 8), 2, 2.4, ORANGE, 7, sfx="pop")
T("待办", 1270, 960, 56, k0=2.4, k1=3.0)
L(bubble(560, 1040, 150, 80, 1), 3, 3.6, BLACK, 7, sfx="pop")
L(dots(560, 1040, 30, 8), 3.6, 4.0, BLACK, 6)
L(bubble(680, 850, 210, 110, 1), 4, 4.6, BLACK, 8, sfx="pop")
L(dots(680, 850), 4.6, 5.0, BLACK, 7)
L(bubble(830, 630, 280, 140, 1), 5, 5.5, BLACK, 8, sfx="pop")
T("？", 830, 630, 90, RED, k0=5.5, k1=6.0)

b.shot("来，打个勾", "来做个自测", (2600, 900, 0.85), bars=3)
L(rect(2300, 780, 230, 230, 16), 0, 0.9, BLACK, 11, sfx="wood_high")
L(pen(2470, 700, -30, 330, 54), 1, 1.9, RED, 9, sfx="wood_low")
T("中了一句", 2600, 1110, 72, k0=2, k1=3, sfx="pop")
T("就在心里打个勾", 2600, 1240, 72, k0=4, k1=5.75, sfx="pop")
L(check(2300, 780, 80), 6, 6.6, RED, 14, sfx="ding")
L(rays(2300, 780, 150, 190, 8, 22), 7, 7.8, RED, 6, sfx="shaker")

# ---------------------------------------------------------------- 书中观点：书里列了一串（场景 3–4）

b.shot("书里列了一串", "拖延心理学 · 书中观点", (2950, 2700, 0.85), bars=3)
L(book(2700, 2440, 340, 230), 0, 0.9, sfx="wood_low")
T("《拖延心理学》", 3250, 2400, 64, GREEN, k0=1, k1=2.75, sfx="pop")
T("博克和袁", 3250, 2510, 56, k0=3, k1=4, sfx="pop")
L(scroll(2980, 2880, 600, 300), 4, 4.9, BLACK, 9, sfx="wood_high")
T("拖延的人", 2980, 2830, 60, k0=5, k1=5.8, sfx="pop")
T("常有的心里话", 2980, 2940, 60, RED, k0=5.8, k1=7.0)
L(arrow((2630, 3000), (2400, 3020), 0.15, 36), 7, 7.8, GREEN, 9, sfx="wood_high")

DROP = (1350, 3350, 0.42)
b.shot("拖延的心里话", "书中观点 · 一张清单", DROP, shake=[0], flashes=[0], bars=3)
b.custom(J(), 0, 0.45, slam_fn(PX, PY, PW, PH), sfx="kick")
T("拖延的心里话", PX, TITLE_Y, 130, RED, k0=1, k1=2.5, sfx="pop")
L(join(*[rect(BOX_X, y, 110, 110, 12) for _, y in ROWS]), 3, 3.9, BLACK, 9, sfx="wood_high")
MON = (1990, 2480, 190)
b.custom(J(), 4, 4.9, peek_fn(monster(*MON), PAPER), sfx="wood_low")
belly(*MON, k0=5, k1=5.8, sfx="pop")
ZX, ZY = 2200, 4480
L(flip(zhou(ZX, ZY, 1.7, "point", "smile"), ZX), 6, 6.9, BLACK, 10, sfx="wood_high")
T("中了几句？", 2230, 3640, 130, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 逐句自测（场景 5–9）：相机沿清单往下推

b.shot("必须做到完美", "自测 · 第一、二句", row_view(0, 260), bars=3)
row_text(0, 0)
tick(0, 2)
L(underline(TXT_X + row_w(0) - 160, TXT_X + row_w(0), ROWS[0][1] + 50, 8, 26), 3, 3.8, RED, 7, sfx="wood_high")
row_text(1, 4)
tick(1, 6)

y3 = ROWS[2][1]
b.shot("事情该很轻松", "自测 · 第三句", row_view(2), bars=3)
row_text(2, 0)
tick(2, 2)
L(feather(1350, y3 - 40, 0.8), 3, 3.9, BLUE, 8, sfx="wood_high")
L(arrow((1440, y3 - 40), (1530, y3 - 40), 0, 26), 4.5, 5.0, BLACK, 7)
L(weight(1680, y3 - 20, 200, 150), 5, 5.9, BLACK, 9, sfx="wood_low")
T("沉", 1680, y3 + 5, 64, RED, k0=6, k1=6.8, sfx="kick")

y4 = ROWS[3][1]
b.shot("不做最安全", "自测 · 第四句", row_view(3), bars=3)
row_text(3, 0)
tick(3, 2)
L(shell(1600, y4 + 60, 320, 210), 3, 3.9, BLACK, 9, sfx="wood_low")
L(peek_head(1405, y4 + 15), 4, 4.8, BLACK, 8, sfx="pop")
T("躲着", 1600, y4 - 20, 58, BLUE, k0=6, k1=6.8, sfx="rim")

y5 = ROWS[4][1]
b.shot("等个标准答案", "自测 · 第五句", row_view(4), bars=3)
row_text(4, 0)
tick(4, 3)
L(qmark(1680, y5 - 50, 1.05), 4, 4.9, RED, 12, sfx="tom")
L(zhou(1450, y5 + 65, 0.7, "down"), 5, 5.9, BLACK, 9, sfx="wood_high")
L(rays(1680, y5 - 100, 105, 135, 6, -90), 6, 6.7, ORANGE, 6, sfx="shaker")

y6 = ROWS[5][1]
b.shot("怕人看到真我", "自测 · 第六句", row_view(5), bars=3)
row_text(5, 0)
tick(5, 3)
MZ = (1550, y6 + 65, 0.75)
L(zhou(*MZ, "hold", with_face=False), 4, 4.9, BLACK, 9, sfx="wood_high")
L(mask(MZ[0] + 40, MZ[1] - 290 * MZ[2] + 5, 120, 140), 5, 5.8, BLUE, 9, sfx="pop")
T("怕被看穿", 1560, y6 + 160, 58, RED, k0=6, k1=7, sfx="rim")

# ---------------------------------------------------------------- 解读（场景 10）：勾越多，越像在躲

b.shot("勾越多越在躲", "解读 · 分档为示意", (2900, 3900, 0.85), bars=3)
T("勾越多", 2600, 3520, 72, k0=0, k1=0.8, sfx="pop")
BASE = 4150
for n, (bx, bh, lab) in enumerate(((2420, 110, "1–2"), (2580, 220, "3–4"), (2740, 340, "5–6"))):
    L(rect(bx, BASE - bh / 2, 100, bh, 8), 1 + n, 1.45 + n, BLUE if n < 2 else RED, 9, sfx="wood_high")
    T(lab, bx, BASE + 70, 50, k0=1.45 + n, k1=2.0 + n)
L(arrow((2780, 3760), (3010, 3680), 0.15, 34), 4, 4.8, GREEN, 9, sfx="wood_high")
MON10 = (3220, 3800, 135)
L(monster(*MON10), 5, 5.9, BLACK, 9, sfx="wood_low")
belly(*MON10, k0=6, k1=6.8, sfx="pop")
T("越像在躲", 3220, 4130, 80, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

b.shot("挑一句改宽点", "第一步 · 改一句", row_view(0, 180), bars=3)
strike(0, 0)
L(arrow((BOX_X + 10, ROWS[0][1] + 70), (TXT_X + 10, ROWS[0][1] + 170), -0.25, 26), 1, 1.8, BLUE, 8, sfx="wood_high")
NEW1 = "先交个能看的"
w1 = K.text_w(NEW1, 72, "hand")
T(NEW1, TXT_X + 40 + w1 / 2, ROWS[0][1] + 170, 72, BLUE, k0=2, k1=3.5, sfx="pop")
L(underline(TXT_X + 40, TXT_X + 40 + w1, ROWS[0][1] + 225, 8, 28), 4, 4.8, BLUE, 7, sfx="wood_high")
L(check(TXT_X + 90 + w1, ROWS[0][1] + 160, 40), 5, 5.6, GREEN, 10, sfx="ding")
T("太紧", 1450, ROWS[0][1], 60, RED, k0=6, k1=6.8, sfx="pop")

b.shot("再改一句", "第二步 · 再改一句", row_view(3, 80), bars=3)
strike(3, 0)
L(arrow((BOX_X + 10, y4 + 70), (TXT_X + 10, y4 + 170), -0.25, 26), 1, 1.8, BLUE, 8, sfx="wood_high")
NEW2 = "做一点，看看会怎样"
w2 = K.text_w(NEW2, 68, "hand")
T(NEW2, TXT_X + 40 + w2 / 2, y4 + 170, 68, BLUE, k0=2, k1=4.25, sfx="pop")
L(P((1650, y4 - 140), (1690, y4 - 190), (1740, y4 - 220)), 5, 5.7, BLACK, 8, sfx="wood_high")
L(circle(1758, y4 - 232, 18), 5.7, 6.0, BLACK, 7)
L(check(TXT_X + 90 + w2, y4 + 160, 40), 6, 6.6, GREEN, 10, sfx="ding")

MX, MY = 2850, 4880
b.shot("改过的贴桌上", "第三步 · 贴在显示器边", (2850, 5050, 0.85), bars=3)
L(monitor(MX, MY, 560, 340), 0, 0.9, BLACK, 9, sfx="wood_high")
NX, NY = 3200, 4780
b.custom(J(), 1, 1.4, note_fn(NX, NY, 330, 150))
L(rect(NX, NY, 330, 150, 8), 1, 1.8, ORANGE, 8, sfx="pop")
T("先交个能看的", NX, NY, 48, BLUE, k0=2, k1=3.5, sfx="pop")
L(zhou(2420, 5420, 0.7, "up", "smile"), 4, 4.9, BLACK, 9, sfx="wood_high")
MON13 = (3180, 5300, 100)
L(dashed_circle(MON13[0], MON13[1], 190), 5, 5.8, "#9AA0A8", 6, sfx="shaker")
L(monster(*MON13), 6, 6.9, BLACK, 8, sfx="wood_low")
belly(*MON13, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 3400, 0.15)
COMMENT = (2800, 6300, 0.8)
b.shot("你中了几句", "评论区见", FAR, bars=4)
b.move(J(), 4, COMMENT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你中了几句？最响哪句？", 2800, 6200, 70, RED, k0=6, k1=8.75, sfx="pop")
T("下一讲：目标定成这样，才动得起来", 2800, 6360, 50, k0=9, k1=13, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "check", "拖延的心里话", "这几句心里话，你中了几句", ACC, b.shots,
                 [f"{BOOK}第1章（中译本“质疑拖延：是可恶的坏习惯还是应得的报应”，书中所列拖延者常有的一组信念，转述）",
                  "中译本：《拖延心理学》，蒋永强、陆正芳译，中国人民大学出版社 2009；原书 Da Capo Lifelong Books 2008 修订版"],
                 "这几句心里话|你中了【几句】", SQUARE_SHOT,
                 ["书中观点为转述：书里列出拖延的人常有的一组信念（第1章，“拖延者的信条”），本讲只取其中六条的大意，"
                  "改成口语上屏：必须完美、做不好就别做、事情都该轻松做完、什么都不做比冒险失败安全、"
                  "有个正确答案找到之前先等着、让人看到真实的我就不会被喜欢。条目与中译措辞需核实，上屏句子不是逐字引文。",
                  "“1–2 / 3–4 / 5–6”勾数分档与“勾越多，越像在躲”为本讲示意，书中没有这份量表，也不作诊断。",
                  "改写句（“先交个能看的”“做一点，看看会怎样”）与把改过的那句贴在显示器边，为据书中思路整理的建议。",
                  "小周对着待办发呆、缩进壳里、对着问号等、举面具挡脸均为现实场景示意，不指向任何具体公司或个人。",
                  "明天怪兽、卷轴、羽毛与秤砣、面具等为本系列的画面比喻。"],
                 tags="#自测 #完美主义")
    return b.attach(ep)
