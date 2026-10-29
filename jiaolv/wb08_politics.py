"""08 政治（白板手绘版）：什么样才算混得好，谁说了算？

叙事：打工人切身问题开局（同学会上被问买房没 → 三十岁该有房有车 → 妈说考编才稳 → 一条都没占 → 这标准谁定的）→
书中观点（亮书《身份的焦虑》、德波顿；什么样的人算体面，每个时代都不一样：古代斯巴达看重能打仗的武士，中世纪看重骑士，
今天又换了一套；标准是人定的，也能改；可以追问一条标准对谁有利；画成一张图：体面像一把会换的尺子）→
身边的例子（老同事干技术不想当主管被说没上进、朋友圈晒车钥匙、相亲先问房子、孩子想学做菜爸妈觉得没面子）→
具体做法（把“混得好”写下来 / 逐条问谁说的、对谁有利 / 划掉不认的、留下想要的 / 加一条自己的贴在电脑边）→ 评论区互动。
书中观点为转述（Alain de Botton, Status Anxiety, 2004，第二部分“解决方法”第三章“政治”；中译本《身份的焦虑》，
陈广兴、南治国译，上海译文出版社）；“尺子”是本讲的通俗比喻；例子与做法为现实场景示意与据书中思路整理的建议。
本讲“政治”按书中意思讲“体面的标准由谁定”，不涉及任何现实政治人物与当下政治议题。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross, desk, doc,
                               face, join, marker, partial, rect, scribble, stick, underline)
from engine.gfx import clamp01, ease_out

from .common import BOOK, episode

ACC = "#7A4FA0"
SQUARE_SHOT = 12

b = Board(size=(3600, 10600))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def house(x, y, s=1.0) -> skia.Path:
    """房子：(x, y) 为地面中点。"""
    w, h = 220 * s, 170 * s
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 30 * s, y - h), (x, y - h - 130 * s), (x + w / 2 + 30 * s, y - h)),
                P((x - 30 * s, y), (x - 30 * s, y - 90 * s), (x + 30 * s, y - 90 * s), (x + 30 * s, y)))


def car(x, y, s=1.0) -> skia.Path:
    """小轿车（侧视）：(x, y) 为地面中点。"""
    return join(P((x - 160 * s, y - 40 * s), (x - 160 * s, y - 100 * s), (x - 90 * s, y - 110 * s),
                  (x - 50 * s, y - 170 * s), (x + 60 * s, y - 170 * s), (x + 110 * s, y - 110 * s),
                  (x + 160 * s, y - 100 * s), (x + 160 * s, y - 40 * s), close=True),
                circle(x - 90 * s, y - 35 * s, 35 * s), circle(x + 90 * s, y - 35 * s, 35 * s))


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12 if w < 200 else 40), P((x - w * 0.17, y + h / 2 - h * 0.13),
                                                           (x + w * 0.17, y + h / 2 - h * 0.13)))


def warrior_gear(x, y, s=1.0) -> skia.Path:
    """武士装备（配 stick(x, y, s, "hold")）：盔缨、圆盾、长矛。"""
    hy = y - 290 * s
    crest = P((x - 50 * s, hy - 30 * s), (x - 10 * s, hy - 95 * s), (x + 50 * s, hy - 40 * s))
    shield = circle(x - 85 * s, hy + 160 * s, 70 * s)
    spear = join(P((x + 110 * s, y - 20 * s), (x + 110 * s, hy - 120 * s)),
                 P((x + 85 * s, hy - 80 * s), (x + 110 * s, hy - 150 * s), (x + 135 * s, hy - 80 * s), close=True))
    return join(crest, shield, spear)


def knight_gear(x, y, s=1.0) -> skia.Path:
    """骑士装备（配 stick(x, y, s, "point")）：头盔、长剑、小旗。"""
    hy = y - 290 * s
    helmet = join(P((x - 50 * s, hy + 5 * s), (x - 50 * s, hy - 45 * s), (x, hy - 70 * s), (x + 50 * s, hy - 45 * s),
                    (x + 50 * s, hy + 5 * s)), P((x - 50 * s, hy - 5 * s), (x + 50 * s, hy - 5 * s)))
    sx, sy = x + 120 * s, hy + 60 * s
    sword = join(P((sx, sy), (sx + 120 * s, sy - 170 * s)), P((sx - 25 * s, sy - 45 * s), (sx + 40 * s, sy + 10 * s)))
    pole = x - 120 * s
    flag = join(P((pole, y), (pole, hy - 140 * s)), P((pole, hy - 140 * s), (pole + 110 * s, hy - 110 * s),
                                                     (pole, hy - 75 * s)))
    return join(helmet, sword, flag)


def tag(x, y, w, h, hang_to=None) -> skia.Path:
    """吊牌：圆角牌子 + 小孔 + 吊绳（hang_to 为吊绳下端）。"""
    parts = [rect(x, y, w, h, 20), circle(x - w / 2 + 34, y, 12)]
    if hang_to:
        parts.append(P((x, y + h / 2), hang_to))
    return join(*parts)


def ruler(x, y, w, h=120) -> skia.Path:
    parts = [rect(x, y, w, h, 10)]
    n = 24
    for i in range(1, n):
        xx = x - w / 2 + w * i / n
        parts.append(P((xx, y - h / 2), (xx, y - h / 2 + (55 if i % 4 == 0 else 30))))
    return join(*parts)


def balance(x, y, tilt=0.0, s=1.0) -> skia.Path:
    """天平：(x, y) 为底座中点；tilt>0 右边沉。"""
    top = y - 300 * s
    dx, dy = 230 * s * math.cos(tilt), 230 * s * math.sin(tilt)
    lx, ly, rx, ry = x - dx, top - dy, x + dx, top + dy
    parts = [P((x - 90 * s, y), (x + 90 * s, y)), P((x, y), (x, top - 20 * s)), circle(x, top - 30 * s, 12 * s),
             P((lx, ly), (rx, ry))]
    for px, py in ((lx, ly), (rx, ry)):
        parts.append(join(P((px, py), (px - 70 * s, py + 130 * s)), P((px, py), (px + 70 * s, py + 130 * s)),
                          P((px - 85 * s, py + 130 * s), (px + 85 * s, py + 130 * s))))
    return join(*parts)


def balance_fn(x, y, s, j):
    """天平：第 0–0.8 拍描出，第 3 拍往右边一沉（对谁有利）。"""

    def fn(c, k, t):
        t3 = b.t_of(j, 3)
        tilt = 0.32 * ease_out(clamp01((t - t3) / 0.35)) if t >= t3 else 0.0
        part, tip = partial(balance(x, y, tilt, s), k)
        c.drawPath(part, marker(RED if t >= t3 else BLACK, 9))
        return tip if k < 1 else None

    return fn


def key(x, y, s=1.0) -> skia.Path:
    return join(circle(x - 70 * s, y, 40 * s), P((x - 30 * s, y), (x + 90 * s, y)),
                P((x + 50 * s, y), (x + 50 * s, y + 30 * s)), P((x + 80 * s, y), (x + 80 * s, y + 40 * s)))


def note(x, y, w=380, h=200) -> skia.Path:
    """便利贴：右下角折一角。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 40),
                  (x + w / 2 - 40, y + h / 2), (x - w / 2, y + h / 2), close=True),
                P((x + w / 2, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2)))


def monitor(x, y, w=300, h=200) -> skia.Path:
    return join(rect(x, y, w, h, 12), P((x, y + h / 2), (x, y + h / 2 + 50)),
                P((x - 70, y + h / 2 + 50), (x + 70, y + h / 2 + 50)))


def pan(x, y, s=1.0) -> skia.Path:
    """炒锅：(x, y) 为锅中心。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - 90 * s, y - 50 * s, 180 * s, 100 * s), 0, 180)
    return join(P((x - 95 * s, y), (x + 95 * s, y)), p, P((x + 95 * s, y), (x + 210 * s, y - 30 * s)))


def chef_hat(x, y, s=1.0) -> skia.Path:
    """厨师帽（配 stick(x, y, s)）。"""
    hy = y - 290 * s
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - 60 * s, hy - 150 * s, 120 * s, 110 * s), 160, 220)
    return join(rect(x, hy - 55 * s, 90 * s, 40 * s, 6), p)


def table(x, y, w=560) -> skia.Path:
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 40, y), (x - w / 2 + 40, y + 100)),
                P((x + w / 2 - 40, y), (x + w / 2 - 40, y + 100)))


# ---------------------------------------------------------------- 开局：混得好的标准（镜头 1–6）

b.shot("周末同学聚会", "灵魂拷问", view=(950, 850, 0.85))
L(table(950, 1080, 640), 0, 0.5, BLACK, 10, sfx="wood_high")
for n, x in enumerate((700, 880, 1060, 1240)):
    L(stick(x, 1180, 0.6, hair=n == 2), 0.6 + n * 0.2, 0.9 + n * 0.2, BLUE if n == 3 else BLACK, 9,
      sfx="pop" if n == 2 else None)
T("同学会", 950, 560, 70, k0=2, sfx="pop")

b.shot("一开口就问房子", "灵魂拷问", view=(950, 850, 0.85))
L(bubble(760, 790, 420, 130, -1), 0, 0.4, BLACK, 8, sfx="pop")
T("买房了吗？", 760, 790, 60, k0=0.4)
L(bubble(1150, 680, 280, 110, -1), 1, 1.3, BLACK, 8, sfx="pop")
T("车呢？", 1150, 680, 56, k0=1.3)
L(face(1240, 1180, 0.6, "sad"), 2, 2.2, BLUE, 8, sfx="rim")
T("……", 1390, 900, 60, BLUE, k0=3, sfx="wood_high")

b.shot("三十岁要有房有车", "灵魂拷问", view=(2650, 850, 0.85))
T("30岁", 2650, 700, 120, RED, k0=0, sfx="kick")
L(house(2380, 1150, 1.0), 1, 1.7, BLACK, 9, sfx="wood_high")
L(car(2900, 1150, 1.0), 2, 2.7, BLACK, 9, sfx="wood_high")
T("有房", 2380, 1240, 56, k0=1.8)
T("有车", 2900, 1240, 56, k0=2.8)
H(3, "pop", 0.6)

b.shot("我妈说考编才稳", "灵魂拷问", view=(950, 1800, 0.85))
L(phone(950, 1820, 560, 760), 0, 0.8, BLACK, 9, sfx="wood_high")
T("妈", 950, 1530, 56, k0=0.8)
L(bubble(950, 1720, 440, 120, -1), 1, 1.4, BLUE, 8, sfx="pop")
T("考个编吧", 950, 1720, 56, BLUE, k0=1.4)
T("稳当！", 950, 1900, 64, RED, k0=2, sfx="pop")
H(3, "wood_high", 0.6)

b.shot("我一条都没占", "灵魂拷问", view=(2650, 1800, 0.85))
L(stick(2250, 2150, 0.75, "shrug"), 0, 0.6, BLUE, 9, sfx="wood_high")
L(face(2250, 2150, 0.75, "flat"), 0.6, 0.7, BLUE, 8)
for n, w in enumerate(("有房", "有车", "编制")):
    yy = 1620 + n * 150
    L(rect(2700, yy, 70, 70, 8), 0.2 + n * 0.2, 0.4 + n * 0.2, BLACK, 7)
    T(w, 2880, yy, 60, k0=0.3 + n * 0.2, k1=0.6 + n * 0.2)
    L(cross(2700, yy, 40), 1 + n, 1.3 + n, RED, 10, sfx="rim")

b.shot("这标准谁定的？", "灵魂拷问", view=(1800, 1350, 0.42), flashes=[0])
T("？", 1800, 1850, 460, RED, k0=0, k1=0.6, sfx="kick")
T("谁定的标准", 1800, 2250, 120, k0=1.0, k1=2.0, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "身份的焦虑", view=(1050, 2950, 0.9))
L(book(750, 2950, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 750, 2710, 76, GREEN, k0=1.0, sfx="pop")
T("阿兰 · 德波顿", 750, 3190, 50, k0=2.0, sfx="pop")

b.shot("书里问：啥算体面", "书中观点 · 体面", view=(2650, 2950, 0.85))
T("体面 = ？", 2650, 2700, 100, RED, k0=0, k1=0.8, sfx="pop")
L(stick(2400, 3250, 0.65, "up"), 1, 1.5, BLACK, 9, sfx="wood_high")
L(face(2400, 3250, 0.65, "flat"), 1.5, 1.6)
L(stick(2900, 3250, 0.65, "shrug"), 2, 2.5, BLUE, 9, sfx="wood_high")
L(face(2900, 3250, 0.65, "flat"), 2.5, 2.6, BLUE, 8)
T("混得好？", 2650, 2870, 56, k0=3, sfx="pop")

LINE_Y = 4300
ERAS = (750, 1800, 2850)
TAG_Y = 3820
TOP = (380, 3240)
b.shot("每个时代答案不同", "书中观点 · 时间轴", view=(1800, 4050, 0.355), shake=[0], flashes=[0])
L(arrow((TOP[0], LINE_Y), (TOP[1], LINE_Y), 0, 70), 0, 0.4, BLACK, 14, sfx="kick")
b.hit(J(), 0, "cymbal", 0.5)
for n, x in enumerate(ERAS):
    L(P((x, LINE_Y - 40), (x, LINE_Y + 40)), 1 + n * 0.15, 1.1 + n * 0.15, BLACK, 12, sfx="wood_high" if n == 0 else None)
for n, x in enumerate(ERAS):
    T("？", x, TAG_Y, 150, RED, k0=2 + n * 0.5, k1=2.3 + n * 0.5, sfx="pop" if n != 1 else None)
T("时间", 3240, LINE_Y + 130, 70, k0=3.5)

S = 0.8
b.shot("古代斯巴达", "书中例子 · 斯巴达", view=(ERAS[0] + 50, 4000, 0.85))
L(stick(ERAS[0], LINE_Y - 60, S, "hold"), 0, 0.6, BLACK, 10, sfx="wood_high")
L(warrior_gear(ERAS[0], LINE_Y - 60, S), 1, 1.8, BLACK, 9, sfx="wood_high")
T("斯巴达", ERAS[0], LINE_Y + 110, 64, k0=2, sfx="pop")
H(3, "tom", 0.6)

b.shot("能打仗才体面", "书中例子 · 斯巴达", view=(ERAS[0] + 50, 4000, 0.85))
b.erase(J(), 0, 0.3, ERAS[0], TAG_Y, 260, 220)
H(0, "shaker")
L(tag(ERAS[0], TAG_Y - 20, 480, 130, (ERAS[0], 3990)), 0.4, 0.9, RED, 8)
T("体面：能打仗", ERAS[0] + 20, TAG_Y - 20, 58, RED, k0=1, sfx="pop")
L(underline(ERAS[0] - 200, ERAS[0] + 240, TAG_Y + 70, 10, 30), 3, 3.4, RED, 7, sfx="ding")

b.shot("到了中世纪", "书中例子 · 中世纪", view=(ERAS[1] + 30, 4000, 0.85))
L(stick(ERAS[1], LINE_Y - 60, S, "point"), 0, 0.6, BLACK, 10, sfx="wood_high")
L(knight_gear(ERAS[1], LINE_Y - 60, S), 1, 1.8, BLACK, 9, sfx="wood_high")
T("中世纪", ERAS[1], LINE_Y + 110, 64, k0=2, sfx="pop")
H(3, "tom", 0.6)

b.shot("骑士最有面子", "书中例子 · 中世纪", view=(ERAS[1] + 30, 4000, 0.85))
b.erase(J(), 0, 0.3, ERAS[1], TAG_Y, 260, 220)
H(0, "shaker")
L(tag(ERAS[1], TAG_Y - 20, 480, 130, (ERAS[1], 3920)), 0.4, 0.9, RED, 8)
T("体面：当骑士", ERAS[1] + 20, TAG_Y - 20, 58, RED, k0=1, sfx="pop")
L(underline(ERAS[1] - 200, ERAS[1] + 240, TAG_Y + 70, 10, 30), 3, 3.4, RED, 7, sfx="ding")

b.shot("今天又换一套", "书中观点 · 今天", view=(ERAS[2] - 30, 4000, 0.85))
b.erase(J(), 0, 0.3, ERAS[2], TAG_Y, 260, 220)
H(0, "shaker")
L(house(ERAS[2] - 180, LINE_Y - 60, 0.75), 1, 1.5, BLACK, 9, sfx="wood_high")
L(car(ERAS[2] + 190, LINE_Y - 60, 0.75), 1.5, 2.0, BLACK, 9)
L(tag(ERAS[2], TAG_Y - 20, 480, 130, (ERAS[2], 3990)), 2, 2.4, RED, 8, sfx="pop")
T("体面：房车编", ERAS[2] + 20, TAG_Y - 20, 58, RED, k0=2.4)
T("今天", ERAS[2], LINE_Y + 110, 64, k0=3, sfx="pop")

b.shot("人定的，就能改", "书中观点 · 人定的", view=(1800, 4350, 0.5))
T("人定的", 1300, 4680, 110, RED, k0=0, k1=0.7, sfx="kick")
L(arrow((1560, 4670), (1860, 4670), 0, 40), 1, 1.4, GREEN, 10, sfx="wood_high")
T("也能改", 2120, 4680, 110, GREEN, k0=2, k1=2.7, sfx="pop")
L(underline(1880, 2360, 4760), 3, 3.4, GREEN, 8, sfx="ding")

b.shot("再问：对谁有利", "书中观点 · 谁得利", view=(2650, 4650, 0.85))
b.custom(J(), 0, 0.8, balance_fn(2900, 4980, 0.75, J()), sfx="wood_high")
T("这条标准", 2900, 4560, 60, k0=1, sfx="pop")
T("对谁有利？", 2900, 5060, 64, RED, k0=2, sfx="rim")
H(3, "tom", 0.7)

b.shot("体面像把尺子", "书中观点 · 一张图", view=(1800, 4050, 0.355))
L(ruler(1800, 3480, 2700, 130), 0, 0.8, BLUE, 9, sfx="wood_high")
T("体面这把尺子", 1800, 3260, 110, BLUE, k0=1, k1=2.2, sfx="pop")
for n, x in enumerate(ERAS):
    L(arrow((x, 3570), (x, 3720), 0, 34), 2 + n * 0.3, 2.3 + n * 0.3, BLUE, 8, sfx="wood_high" if n == 0 else None)
H(3, "ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 6100), (2650, 6100), (950, 7000), (2650, 7000)]
b.shot("身边全是尺子", "身边的例子", view=(1800, 6550, 0.355))
T("身边的尺子", 1800, 5550, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("老同事不想当主管", "例子 · 职场", view=(950, 6100, 0.85))
L(desk(950, 6250, 360), 0, 0.6, BLACK, 9, sfx="wood_high")
L(stick(680, 6420, 0.65), 0.6, 1.0, BLUE, 9)
T("干技术十年", 900, 5830, 60, k0=1, sfx="pop")
L(face(680, 6420, 0.65, "smile"), 2, 2.2, BLUE, 8, sfx="pop")
T("挺好", 680, 6080, 54, GREEN, k0=3, sfx="wood_high")

b.shot("就被说没上进", "例子 · 职场", view=(950, 6100, 0.85))
L(stick(1330, 6420, 0.65, "point"), 0, 0.5, BLACK, 9, sfx="wood_high")
L(bubble(1220, 5960, 340, 110, 1), 1, 1.4, BLACK, 8, sfx="pop")
T("还不升？", 1220, 5960, 54, k0=1.4)
L(face(680, 6420, 0.65, "flat"), 2, 2.2, BLUE, 8, sfx="rim")
T("没上进", 1440, 6110, 50, RED, k0=3, sfx="pop")

b.shot("朋友圈晒车钥匙", "例子 · 生活", view=(2650, 6100, 0.85))
L(phone(2500, 6120, 460, 640), 0, 0.7, BLACK, 9, sfx="wood_high")
L(key(2500, 6020, 1.2), 1, 1.5, BLACK, 9, sfx="pop")
T("提车啦", 2500, 5880, 52, k0=1.6)
T("点赞 99", 2500, 6240, 50, RED, k0=2, sfx="pop")

b.shot("不晒好像就输了", "例子 · 生活", view=(2650, 6100, 0.85))
L(stick(3000, 6420, 0.6, "hold"), 0, 0.5, BLUE, 9, sfx="wood_high")
L(face(3000, 6420, 0.6, "sad"), 0.5, 0.6, BLUE, 8)
L(bubble(3060, 5960, 340, 110, -1), 1, 1.3, BLUE, 8, sfx="pop")
T("我也得晒？", 3060, 5960, 50, BLUE, k0=1.3)
L(scribble(3000, 6130, 130, 50, 6), 2, 2.4, RED, 6, sfx="shaker")

b.shot("相亲先问房子", "例子 · 家庭", view=(950, 7000, 0.85))
L(table(950, 7230, 520), 0, 0.4, BLACK, 10, sfx="wood_high")
L(stick(640, 7330, 0.55, hair=True), 0.4, 0.8, BLACK, 9)
L(stick(1260, 7330, 0.55), 0.6, 1.0, BLUE, 9)
L(bubble(700, 6800, 300, 110, -1), 1, 1.3, BLACK, 8, sfx="pop")
T("有房吗？", 700, 6800, 54, k0=1.3)
L(face(1260, 7330, 0.55, "flat"), 2, 2.2, BLUE, 8, sfx="rim")

b.shot("还没聊就先打分", "例子 · 家庭", view=(950, 7000, 0.85))
L(doc(1080, 6910, 240, 310, 0), 0, 0.5, BLACK, 8, sfx="wood_high")
T("房：？", 1070, 6820, 50, RED, k0=1, sfx="pop")
T("车：？", 1070, 6910, 50, RED, k0=2, sfx="pop")
T("打分", 1070, 7000, 50, k0=3, sfx="rim")

b.shot("孩子想学做菜", "例子 · 家庭", view=(2650, 7000, 0.85))
L(stick(2350, 7330, 0.5), 0, 0.4, BLUE, 9, sfx="wood_high")
L(chef_hat(2350, 7330, 0.5), 0.4, 0.8, BLUE, 8)
L(pan(2600, 7180, 0.8), 1, 1.5, BLACK, 9, sfx="pop")
L(bubble(2400, 6800, 360, 110, -1), 2, 2.3, BLUE, 8, sfx="pop")
T("我想学做菜", 2400, 6800, 50, BLUE, k0=2.3)

b.shot("爸妈脸一下变了", "例子 · 家庭", view=(2650, 7000, 0.85))
for n, x in enumerate((2950, 3120)):
    L(stick(x, 7330, 0.6, hair=n == 1), n * 0.3, n * 0.3 + 0.4, BLACK, 9, sfx="wood_high" if n == 0 else None)
L(face(2950, 7330, 0.6, "flat"), 1, 1.1, BLACK, 8, sfx="rim")
L(face(3120, 7330, 0.6, "sad"), 1.1, 1.2, BLACK, 8)
L(bubble(3000, 6830, 340, 110, 1), 2, 2.3, BLACK, 8, sfx="pop")
T("多没面子", 3000, 6830, 52, k0=2.3)

b.shot("每把尺子谁递的", "身边的例子", view=(1800, 6550, 0.355))
for n, (x, y) in enumerate(CARDS):
    T("谁说的？", x + 380, y - 330, 80, RED, k0=n, sfx="pop")

b.shot("拿别人尺子量自己", "身边的例子", view=(1800, 6600, 0.355), shake=[0])
T("别人的尺子", 1800, 7620, 150, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 8650), (2650, 8650), (950, 9550), (2650, 9550)]
b.shot("换把自己的尺子", "具体做法", view=(1800, 9100, 0.355))
T("换把自己的尺子", 1800, 8080, 130, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先写下来", "第一步 · 写下来", view=(950, 8650, 0.85))
T("① 写下混得好", 950, 8350, 76, BLUE, k0=0, sfx="pop")
L(doc(680, 8720, 260, 330, 5), 1, 1.6, BLACK, 8, sfx="wood_high")
L(P((800, 8900), (860, 8560)), 2, 2.3, BLUE, 12, sfx="pop")

b.shot("房车编，全写上", "第一步 · 写下来", view=(950, 8700, 0.85))
for n, w in enumerate(("有房", "有车", "有编制", "当主管")):
    T(w, 1180, 8540 + n * 110, 58, k0=n, sfx="pop")

b.shot("逐条问谁说的", "第二步 · 问出处", view=(2650, 8650, 0.85))
T("② 逐条问出处", 2650, 8350, 76, BLUE, k0=0, sfx="pop")
L(stick(2200, 8980, 0.6, "point"), 1, 1.5, BLACK, 9, sfx="wood_high")
T("谁说的？", 2750, 8560, 64, RED, k0=2, sfx="rim")

b.shot("这条是亲戚说的", "第二步 · 问出处", view=(2650, 8700, 0.85))
T("有房 ← 亲戚", 2750, 8690, 58, k0=0, sfx="pop")
T("有编 ← 爸妈", 2750, 8800, 58, k0=1, sfx="pop")
L(underline(2840, 2950, 8735, 8, 20), 2, 2.2, GREEN, 6, sfx="wood_high")
L(underline(2840, 2950, 8845, 8, 20), 3, 3.2, GREEN, 6, sfx="wood_high")

b.shot("这条对谁有利", "第二步 · 谁得利", view=(2650, 8700, 0.85))
T("越贵越体面", 2600, 8930, 58, k0=0, sfx="pop")
L(arrow((2890, 8930), (3000, 8930), 0, 26), 1, 1.3, RED, 8, sfx="wood_high")
T("商家", 3130, 8930, 58, RED, k0=2, sfx="rim")
L(underline(3050, 3210, 8985, 8, 20), 3, 3.3, RED, 6, sfx="ding")

b.shot("留下你认的", "第三步 · 挑一挑", view=(950, 9550, 0.85))
T("③ 留下你认的", 950, 9250, 76, BLUE, k0=0, sfx="pop")
ITEMS = ("有房", "有车", "有编制", "当主管")
for n, w in enumerate(ITEMS):
    T(w, 850, 9420 + n * 115, 58, k0=1 + n * 0.5, sfx="pop" if n % 2 == 0 else None)

b.shot("不认的划掉", "第三步 · 挑一挑", view=(950, 9550, 0.85))
for n, i in enumerate((1, 3)):
    yy = 9420 + i * 115
    L(P((730, yy), (970, yy)), n * 1.0, n * 1.0 + 0.3, RED, 10, sfx="rim")
L(stick(1350, 9900, 0.55, "shrug"), 2, 2.5, BLUE, 9, sfx="wood_high")
L(face(1350, 9900, 0.55, "smile"), 2.5, 2.6, BLUE, 8)

b.shot("想要的照样留", "第三步 · 挑一挑", view=(950, 9550, 0.85))
for n, i in enumerate((0, 2)):
    L(check(1050, 9420 + i * 115, 34), n, n + 0.3, GREEN, 10, sfx="ding")
T("想要就留着", 1300, 9480, 52, GREEN, k0=2, sfx="pop")

b.shot("再加一条自己的", "第四步 · 加一条", view=(2650, 9550, 0.85))
T("④ 加一条自己的", 2650, 9250, 72, BLUE, k0=0, sfx="pop")
L(note(2800, 9450, 420, 160), 1, 1.4, RED, 8, sfx="wood_high")
T("陪娃吃晚饭", 2780, 9450, 54, k0=1.5)
L(note(2800, 9680, 420, 160), 2, 2.4, RED, 8, sfx="wood_high")
T("手艺越练越好", 2780, 9680, 52, k0=3, sfx="pop")

b.shot("贴在电脑边上", "第四步 · 加一条", view=(2650, 9600, 0.85))
L(monitor(2290, 9600, 300, 210), 0, 0.6, BLACK, 9, sfx="wood_high")
L(arrow((2580, 9560), (2460, 9590), 0.2, 26), 1, 1.3, GREEN, 8, sfx="pop")
L(check(2290, 9600, 50), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("就这四步", "具体做法", view=(1800, 9100, 0.355))
for n, (x, y) in enumerate(SOL):
    L(check(x + 500, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 else "pop")

b.shot("尺子在你手里", "一句话", view=(1800, 5300, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 10300, 0.8))
T("你最想划掉哪条？", 1800, 10220, 80, RED, k0=0.5, k1=1.8)
T("下一讲：为什么去趟山里，烦心事就小了？", 1800, 10380, 50, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(J(), 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "politics", "政治", "什么样才算混得好，谁说了算？", ACC, b.shots,
                 [f"{BOOK}第二部分“解决方法”第三章“政治”（转述）",
                  "中译本：阿兰·德波顿《身份的焦虑》，陈广兴、南治国译，上海译文出版社"],
                 "混得好不好|谁【说了算】", 10,
                 ["书中观点均为转述：什么样的人算成功、体面，每个时代、每个社会的标准都不一样（书中举古代斯巴达看重武士、"
                  "中世纪看重骑士等例子）；标准是人定的，也可以改；可以追问一条标准对谁有利。出处：Alain de Botton, "
                  "Status Anxiety (Hamish Hamilton / Pantheon, 2004)，第二部分“解决方法”第三章“政治”；中译本《身份的焦虑》"
                  "（陈广兴、南治国译，上海译文出版社）。上屏均为转述，不是逐字引文。",
                  "时间轴上“今天：房车编”一格、“体面像一把尺子”的比喻为本讲的通俗示意，不是书中原话；本讲“政治”按书中意思讲"
                  "“标准由谁定”，不涉及现实政治人物与当下政治议题。",
                  "同学会问买房、三十岁有房有车、考编才稳、老同事不想当主管、朋友圈晒车钥匙、相亲先问房子、孩子想学做菜均为现实场景"
                  "示意，不指向任何具体公司或个人，也不评价任何职业和收入水平；“点赞 99”等数字为示意。",
                  "四步做法（把“混得好”写下来、逐条问谁说的和对谁有利、划掉不认的留下想要的、加一条自己的贴在电脑边）"
                  "为据书中思路整理的建议。"],
                 tags="#成功 #价值观")
    return b.attach(ep)
