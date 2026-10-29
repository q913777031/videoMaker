"""08 政治（白板手绘版）：什么样才算混得好，谁说了算？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
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
SQUARE_SHOT = 5

b = Board(size=(3600, 15400))


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


# ---------------------------------------------------------------- 开局：混得好的标准（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。
# 白板按区块上下拉开间距，保证每个场景的页眉区（屏幕顶部）不压到相邻区块的字。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("同学会一开口就问房", "灵魂拷问", (950, 850, 0.85))
L(table(950, 1080, 640), 0, 0.4, BLACK, 10, sfx="wood_high")
for n, x in enumerate((700, 880, 1060, 1240)):
    L(stick(x, 1180, 0.6, hair=n == 2), 0.4 + n * 0.25, 0.65 + n * 0.25, BLUE if n == 3 else BLACK, 9)
T("同学会", 950, 560, 70, k0=1.5, k1=2.0)
L(bubble(760, 790, 420, 130, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("买房了吗？", 760, 790, 60, k0=2.4, k1=2.95)
L(bubble(1150, 680, 280, 110, -1), 3, 3.3, BLACK, 8, sfx="pop")
T("车呢？", 1150, 680, 56, k0=3.3, k1=3.8)
L(face(1240, 1180, 0.6, "sad"), 4, 4.2, BLUE, 8, sfx="rim")

scene("有房有车，还得考编", "灵魂拷问", (2650, 1400, 0.62))
T("30岁", 2650, 720, 120, RED, k0=0, k1=0.6, sfx="kick")
L(house(2380, 1150, 1.0), 1, 1.6, BLACK, 9, sfx="wood_high")
T("有房", 2380, 1240, 56, k0=1.6, k1=2.0)
L(car(2900, 1150, 1.0), 2, 2.6, BLACK, 9, sfx="wood_high")
T("有车", 2900, 1240, 56, k0=2.6, k1=3.0)
L(phone(2650, 1850, 480, 620), 3, 3.6, BLACK, 9, sfx="wood_high")
T("妈", 2650, 1600, 56, k0=3.6, k1=3.9)
L(bubble(2650, 1760, 400, 110, -1), 4, 4.3, BLUE, 8, sfx="pop")
T("考个编吧", 2650, 1760, 56, BLUE, k0=4.3, k1=4.9)
T("稳当！", 2650, 1950, 64, RED, k0=5, k1=5.5, sfx="pop")

scene("一条没占，谁定的？", "灵魂拷问", (1400, 2350, 0.62), shake=[4], flashes=[4])
L(stick(800, 2450, 0.75, "shrug"), 0, 0.5, BLUE, 9, sfx="wood_high")
L(face(800, 2450, 0.75, "flat"), 0.5, 0.6, BLUE, 8)
CHK = [(w, 1900 + n * 150) for n, w in enumerate(("有房", "有车", "编制"))]
for n, (w, yy) in enumerate(CHK):
    L(rect(1150, yy, 70, 70, 8), 0.6 + n * 0.3, 0.75 + n * 0.3, BLACK, 7)
    T(w, 1330, yy, 60, k0=0.75 + n * 0.3, k1=0.9 + n * 0.3)
for n, (w, yy) in enumerate(CHK):
    L(cross(1150, yy, 40), 2 + n * 0.5, 2.3 + n * 0.5, RED, 10, sfx="rim" if n != 1 else None)
T("？", 1900, 2150, 380, RED, k0=4, k1=4.5, sfx="kick")
T("谁定的标准", 1900, 2600, 100, k0=5, k1=5.9, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

scene("书里问：啥算体面", "身份的焦虑", (1100, 4350, 0.85))
L(book(750, 4350, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 750, 4110, 76, GREEN, k0=1, k1=1.9, sfx="pop")
T("阿兰 · 德波顿", 750, 4590, 50, k0=2, k1=3.0, sfx="pop")
T("体面 = ？", 1400, 4250, 100, RED, k0=3, k1=3.8, sfx="rim")
T("混得好？", 1400, 4420, 64, k0=4, k1=4.6, sfx="pop")

LINE_Y = 6030
ERAS = (750, 1800, 2850)
TAG_Y = 5550
TOP = (380, 3240)
WIDE = (1800, 5100, 0.355)
scene("每个时代答案不同", "书中观点 · 时间轴", WIDE, shake=[0], flashes=[0])
L(arrow((TOP[0], LINE_Y), (TOP[1], LINE_Y), 0, 70), 0, 0.4, BLACK, 14, sfx="kick")
b.hit(J(), 0, "cymbal", 0.5)
for n, x in enumerate(ERAS):
    L(P((x, LINE_Y - 40), (x, LINE_Y + 40)), 1 + n * 0.15, 1.1 + n * 0.15, BLACK, 12, sfx="wood_high" if n == 0 else None)
for n, x in enumerate(ERAS):
    T("？", x, TAG_Y, 150, RED, k0=2 + n, k1=2.3 + n, sfx="pop")
T("时间", 3130, LINE_Y + 130, 70, k0=5, k1=5.4, sfx="wood_high")

S = 0.8
scene("先看武士，再看骑士", "书中例子 · 斯巴达与中世纪", (1290, 5850, 0.68))
for n, (gear, arms, name, word, hang) in enumerate(((warrior_gear, "hold", "斯巴达", "体面：能打仗", 170),
                                                    (knight_gear, "point", "中世纪", "体面：当骑士", 100))):
    x, k = ERAS[n], 3 * n
    L(stick(x, LINE_Y - 60, S, arms), k, k + 0.5, BLACK, 10, sfx="wood_high")
    L(gear(x, LINE_Y - 60, S), k + 0.5, k + 1.0, BLACK, 9)
    T(name, x, LINE_Y + 110, 64, k0=k + 1, k1=k + 1.5, sfx="pop")
    b.erase(J(), k + 1.5, k + 1.7, x, TAG_Y, 260, 220)
    L(tag(x, TAG_Y - 20, 480, 130, (x, TAG_Y + hang)), k + 1.7, k + 2.0, RED, 8)
    T(word, x + 20, TAG_Y - 20, 58, RED, k0=k + 2, k1=k + 2.9, sfx="pop")

scene("换来换去，都是人定的", "书中观点 · 人定的", (2820, 5950, 0.8))
b.erase(J(), 0, 0.3, ERAS[2], TAG_Y, 260, 220)
H(0, "shaker")
L(house(ERAS[2] - 180, LINE_Y - 60, 0.75), 1, 1.5, BLACK, 9, sfx="wood_high")
L(car(ERAS[2] + 190, LINE_Y - 60, 0.75), 1.5, 2.0, BLACK, 9)
L(tag(ERAS[2], TAG_Y - 20, 480, 130, (ERAS[2], TAG_Y + 170)), 2, 2.3, RED, 8, sfx="pop")
T("体面：房车编", ERAS[2] + 20, TAG_Y - 20, 58, RED, k0=2.3, k1=3.0)
T("今天", ERAS[2], LINE_Y + 110, 64, k0=3, k1=3.4, sfx="pop")
T("人定的", 2620, 6350, 90, RED, k0=4, k1=4.6, sfx="rim")
L(arrow((2780, 6350), (2920, 6350), 0, 30), 4.6, 4.9, GREEN, 9)
T("也能改", 3070, 6350, 90, GREEN, k0=5, k1=5.6, sfx="pop")
L(P((3200, 6420), (3135, 6432), (3070, 6420), (3005, 6432), (2940, 6420)), 5.6, 6.0, GREEN, 7)   # 从右往左画，手停在左下不挡字

BAL = (1100, 7420, 0.75)
scene("再问：对谁有利", "书中观点 · 谁得利", (1100, 7120, 0.85))
b.custom(J(), 0, 0.8, balance_fn(*BAL, J()), sfx="wood_high")
T("这条标准", 1100, 7000, 60, k0=1, k1=1.7, sfx="pop")
T("对谁有利？", 1100, 7500, 64, RED, k0=2, k1=2.9, sfx="rim")
H(3, "tom", 0.7)
_pan_x = BAL[0] + 230 * BAL[2] * math.cos(0.32)
_pan_y = BAL[1] - 300 * BAL[2] + 230 * BAL[2] * math.sin(0.32)
T("¥", _pan_x, _pan_y + 50, 60, RED, k0=4, k1=4.3, sfx="pop")
L(underline(930, 1270, 7560, 8, 24), 5, 5.4, RED, 6, sfx="ding")

scene("体面像把尺子，会换", "书中观点 · 一张图", WIDE)
L(ruler(1800, 5100, 2700, 130), 0, 0.8, BLUE, 9, sfx="wood_high")
T("体面这把尺子", 1800, 4880, 110, BLUE, k0=1, k1=2.2, sfx="pop")
for n, x in enumerate(ERAS):
    L(arrow((x, 5190), (x, 5420), 0, 34), 2.2 + n * 0.3, 2.5 + n * 0.3, BLUE, 8)
H(2, "wood_high", 0.6)
H(4, "ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 9200), (2650, 9200), (950, 10400), (2650, 10400)]
CW = 1160
EX = (1800, 9800, 0.355)
scene("身边全是尺子", "身边的例子", EX)
T("身边的尺子", 1800, 8600, 100, k0=0, k1=1.0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, CW, 820, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

cx, cy = CARDS[0]
cx -= 50    # 视角略偏外侧，总览大字不进画面
scene("不当主管，就没上进？", "例子 · 职场", (cx, cy, 0.85))
L(desk(950, cy + 150, 360), 0, 0.6, BLACK, 9, sfx="wood_high")
L(stick(680, cy + 320, 0.65), 0.6, 1.0, BLUE, 9)
T("干技术十年", 900, cy - 270, 60, k0=1, k1=1.9, sfx="pop")
L(face(680, cy + 320, 0.65, "smile"), 1.9, 2.0, BLUE, 8)
L(stick(1330, cy + 320, 0.65, "point"), 2, 2.5, BLACK, 9, sfx="wood_high")
L(bubble(1220, cy - 140, 340, 110, 1), 3, 3.4, BLACK, 8, sfx="pop")
T("还不升？", 1220, cy - 140, 54, k0=3.4, k1=4.0)
T("没上进", 1440, cy + 10, 50, RED, k0=4, k1=4.5, sfx="pop")
L(underline(1365, 1515, cy + 60, 8, 20), 5, 5.3, RED, 6, sfx="rim")

cx, cy = CARDS[1]
cx += 50    # 视角略偏外侧，总览大字不进画面
scene("朋友晒车，我也得晒？", "例子 · 生活", (cx, cy, 0.85))
L(phone(2500, cy + 20, 460, 640), 0, 0.7, BLACK, 9, sfx="wood_high")
L(key(2500, cy - 80, 1.2), 1, 1.5, BLACK, 9, sfx="pop")
T("提车啦", 2500, cy - 220, 52, k0=1.5, k1=2.0)
T("点赞 99", 2500, cy + 140, 50, RED, k0=2, k1=2.6, sfx="pop")
L(stick(3000, cy + 320, 0.6, "hold"), 3, 3.5, BLUE, 9, sfx="wood_high")
L(face(3000, cy + 320, 0.6, "sad"), 3.5, 3.6, BLUE, 8)
L(bubble(3030, cy - 140, 340, 110, -1), 4, 4.3, BLUE, 8, sfx="pop")
T("我也得晒？", 3030, cy - 140, 50, BLUE, k0=4.3, k1=4.9)
L(scribble(3000, cy + 30, 130, 50, 6), 5, 5.4, RED, 6, sfx="shaker")

cx, cy = CARDS[2]
cx -= 50    # 视角略偏外侧，总览大字不进画面
scene("相亲没聊，先问房子", "例子 · 家庭", (cx, cy, 0.85))
L(table(950, cy + 230, 520), 0, 0.4, BLACK, 10, sfx="wood_high")
L(stick(640, cy + 330, 0.55, hair=True), 0.4, 0.7, BLACK, 9)
L(stick(1260, cy + 330, 0.55), 0.7, 1.0, BLUE, 9)
L(bubble(700, cy - 200, 300, 110, -1), 1, 1.3, BLACK, 8, sfx="pop")
T("有房吗？", 700, cy - 200, 54, k0=1.3, k1=1.9)
L(face(1260, cy + 330, 0.55, "flat"), 2, 2.2, BLUE, 8, sfx="rim")
L(doc(1080, cy - 90, 240, 310, 0), 3, 3.5, BLACK, 8, sfx="wood_high")
T("房：？", 1070, cy - 180, 50, RED, k0=4, k1=4.5, sfx="pop")
T("车：？", 1070, cy - 90, 50, RED, k0=4.5, k1=5.0)
T("打分", 1070, cy, 50, k0=5, k1=5.4, sfx="rim")

cx, cy = CARDS[3]
cx += 50    # 视角略偏外侧，总览大字不进画面
scene("想学做菜，爸妈嫌丢人", "例子 · 家庭", (cx, cy, 0.85))
L(stick(2350, cy + 330, 0.5), 0, 0.4, BLUE, 9, sfx="wood_high")
L(chef_hat(2350, cy + 330, 0.5), 0.4, 0.8, BLUE, 8)
L(pan(2600, cy + 180, 0.8), 1, 1.5, BLACK, 9, sfx="pop")
L(bubble(2400, cy - 200, 360, 110, -1), 2, 2.3, BLUE, 8, sfx="pop")
T("我想学做菜", 2400, cy - 200, 50, BLUE, k0=2.3, k1=3.0)
for n, x in enumerate((2950, 3120)):
    L(stick(x, cy + 330, 0.6, hair=n == 1), 3 + n * 0.4, 3.4 + n * 0.4, BLACK, 9, sfx="wood_high" if n == 0 else None)
L(face(2950, cy + 330, 0.6, "flat"), 4, 4.1, BLACK, 8, sfx="rim")
L(face(3120, cy + 330, 0.6, "sad"), 4.1, 4.2, BLACK, 8)
L(bubble(3000, cy - 170, 340, 110, 1), 5, 5.3, BLACK, 8, sfx="pop")
T("多没面子", 3000, cy - 170, 52, k0=5.3, k1=5.9)

scene("拿别人的尺子量自己", "身边的例子", EX, shake=[4])
for n, (x, y) in enumerate(CARDS):
    T("谁说的？", x, y + 470, 84, RED, k0=n, k1=n + 0.7, sfx="pop")
T("别人的尺子", 1800, 11050, 150, RED, k0=4, k1=4.9, sfx="kick")
H(5, "ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 12100), (2650, 12100), (950, 13300), (2650, 13300)]


def card(n, title, size=76):
    x, y = SOL[n]
    L(rect(x, y, 1200, 820, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
    T(title, x, y - 300, size, BLUE, k0=1, k1=1.9, sfx="pop")
    return x, y


scene("先把混得好写下来", "第一步 · 写下来", (SOL[0][0], SOL[0][1], 0.85))
x, y = card(0, "① 写下混得好")
L(doc(680, y + 70, 260, 330, 5), 2, 2.5, BLACK, 8, sfx="wood_high")
L(P((800, y + 250), (860, y - 90)), 2.5, 2.7, BLUE, 12)
for n, w in enumerate(("有房", "有车", "有编制", "当主管")):
    k = 3 + n * 0.5
    T(w, 1180, y - 110 + n * 110, 58, k0=k, k1=k + 0.45, sfx="pop" if n % 2 == 0 else None)

scene("逐条问谁说的，谁得利", "第二步 · 问出处", (SOL[1][0], SOL[1][1], 0.85))
x, y = card(1, "② 逐条问出处")
L(stick(2200, y + 330, 0.6, "point"), 2, 2.5, BLACK, 9, sfx="wood_high")
T("有房 ← 亲戚", 2750, y - 90, 58, k0=3, k1=3.5, sfx="pop")
T("有编 ← 爸妈", 2750, y + 40, 58, k0=3.5, k1=4.0)
T("越贵越体面", 2600, y + 190, 58, k0=4, k1=4.6, sfx="pop")
L(arrow((2890, y + 190), (3000, y + 190), 0, 26), 4.6, 4.8, RED, 8)
T("商家", 3130, y + 190, 58, RED, k0=5, k1=5.4, sfx="rim")
L(underline(3050, 3210, y + 245, 8, 20), 5.4, 5.8, RED, 6)

scene("不认的划掉，想要的留", "第三步 · 挑一挑", (SOL[2][0], SOL[2][1], 0.85))
x, y = card(2, "③ 留下你认的")
ITEMS = ("有房", "有车", "有编制", "当主管")
for n, w in enumerate(ITEMS):
    k = 2 + n // 2 + (n % 2) * 0.4
    T(w, 850, y - 130 + n * 115, 58, k0=k, k1=k + 0.35, sfx="pop" if n % 2 == 0 else None)
for n, i in enumerate((1, 3)):
    yy = y - 130 + i * 115
    L(P((730, yy), (970, yy)), 4 + n * 0.3, 4.3 + n * 0.3, RED, 10, sfx="rim" if n == 0 else None)
for n, i in enumerate((0, 2)):
    L(check(1050, y - 130 + i * 115, 34), 5 + n * 0.3, 5.3 + n * 0.3, GREEN, 10, sfx="ding" if n == 0 else None)

scene("加一条自己的，贴起来", "第四步 · 加一条", (SOL[3][0], SOL[3][1], 0.85))
x, y = card(3, "④ 加一条自己的", 72)
L(note(2800, y - 100, 420, 160), 2, 2.3, RED, 8, sfx="wood_high")
T("陪娃吃晚饭", 2780, y - 100, 54, k0=2.3, k1=2.9)
L(note(2800, y + 130, 420, 160), 3, 3.3, RED, 8, sfx="wood_high")
T("手艺越练越好", 2780, y + 130, 52, k0=3.3, k1=4.0)
L(monitor(2290, y + 50, 300, 210), 4, 4.6, BLACK, 9, sfx="wood_high")
L(arrow((2580, y + 10), (2460, y + 40), 0.2, 26), 4.6, 4.9, GREEN, 8)
L(check(2290, y + 50, 50), 5, 5.3, GREEN, 10, sfx="ding")

scene("尺子在你手里", "一句话", (1800, 6080, 0.235))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 14560, 0.8))
H(0, "cymbal", 0.5)
T("你最想划掉哪条？", 1800, 14480, 80, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：为什么去趟山里，烦心事就小了？", 1800, 14640, 50, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "politics", "政治", "什么样才算混得好，谁说了算？", ACC, b.shots,
                 [f"{BOOK}第二部分“解决方法”第三章“政治”（转述）",
                  "中译本：阿兰·德波顿《身份的焦虑》，陈广兴、南治国译，上海译文出版社"],
                 "混得好不好|谁【说了算】", 5,
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
