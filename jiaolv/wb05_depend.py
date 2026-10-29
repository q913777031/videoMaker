"""05 制约因素（白板手绘版）：工作干得好好的，为什么还怕被裁？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
叙事：打工人切身问题开局（这个月绩效拿了优秀 → 听说部门要优化 → 名单上有没有我 → 半夜两点睡不着、躺着算房贷）→
书中观点（亮书《身份的焦虑》+ 德波顿，第一部分第五章“制约因素”；你的地位拴在五样自己管不了的东西上：才华时灵时不灵、
运气、雇主、雇主的利润、整体经济；画成一个被五根线吊着的小人，哪根一动你就晃，再拼也难踏实，所以会怕很正常）→
身边的例子（项目做得漂亮整条业务被砍、来了新领导带自己的人、街角面馆门口修路半年、老爸在厂里干了二十年厂子停产；
每件都连着一根线，人没做错什么）→
具体做法（拿张纸分两栏，能管的管好、管不了的先放下 / 存够半年开销留缓冲 / 攒带得走的本事和人脉 /
别把自己全押在一份工作上，多几条腿站得稳）→ 评论区互动 + 下一讲预告。
书中观点为转述（Alain de Botton, Status Anxiety, Hamish Hamilton / Pantheon, 2004；中译本《身份的焦虑》，
陈广兴、南治国译，上海译文出版社，第一部分“焦虑起因”第五章“制约因素”）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, building, check, circle, clock, cross,
                               doc, face, hands_at, join, marker, partial, podium_list, rect, scribble, stick, underline)
from adler import kit as K
from engine.gfx import clamp01

from .common import BOOK, episode

ACC = "#5B6F8F"
SQUARE_SHOT = 8

D = 1150                         # 身边的例子及以后各段整体下移（给书中观点的大图留位置）
R = 400                          # 例子第二排、做法各段再下移（上一排的字不漏进页眉）
R2 = 700                         # 做法第二排、评论区再下移
b = Board(size=(3600, 10400 + D + R + R2))


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


def mood(x, y, s, m, k, color=BLACK, sfx=None):
    """换表情：先擦掉小人的头，再画新头和新表情。"""
    hy = y - 290 * s
    b.erase(J(), k, k + 0.25, x, hy, 104 * s, 104 * s)
    L(join(circle(x, hy, 45 * s), face(x, y, s, m)), k + 0.3, k + 0.6, color, 9, sfx=sfx)


# ---------------------------------------------------------------- 本讲画法

def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 40), P((x - w * 0.17, y + h / 2 - h * 0.13), (x + w * 0.17, y + h / 2 - h * 0.13)))


def bulb(x, y) -> skia.Path:
    """灯泡：(x, y) 为玻璃球中心。"""
    return join(circle(x, y, 40), P((x - 20, y + 38), (x - 20, y + 60), (x + 20, y + 60), (x + 20, y + 38)),
                P((x - 20, y + 49), (x + 20, y + 49)))


def dice(x, y, n=5, s=100) -> skia.Path:
    parts = [rect(x, y, s, s, 16)]
    for dx, dy in PIPS[n]:
        parts.append(circle(x + dx * s * 0.27, y + dy * s * 0.27, 7))
    return join(*parts)


PIPS = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
        5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}


def chart(x, y) -> skia.Path:
    """小坐标轴：(x, y) 为中心。"""
    return P((x - 70, y - 60), (x - 70, y + 50), (x + 75, y + 50))


def wave(x, y, w, amp, phase=0.0, n=28) -> skia.Path:
    return P(*[(x - w / 2 + w * i / n, y + amp * math.sin(i / n * 2 * math.pi * 1.5 + phase)) for i in range(n + 1)])


def jar(x, y, w=220, h=300) -> skia.Path:
    """储蓄罐（玻璃罐）：(x, y) 为罐身中心。"""
    return join(P((x - w / 2 + 40, y - h / 2 - 40), (x - w / 2 + 40, y - h / 2), (x - w / 2, y - h / 2 + 40),
                  (x - w / 2, y + h / 2), (x + w / 2, y + h / 2), (x + w / 2, y - h / 2 + 40),
                  (x + w / 2 - 40, y - h / 2), (x + w / 2 - 40, y - h / 2 - 40)),
                P((x - w / 2 + 25, y - h / 2 - 40), (x + w / 2 - 25, y - h / 2 - 40)))


def shop(x, y, w=420, h=320) -> skia.Path:
    """小店：(x, y) 为店面中心，上沿是锯齿遮阳棚。"""
    top = y - h / 2
    zz = [(x - w / 2 - 20 + i * (w + 40) / 8, top + (40 if i % 2 else 0)) for i in range(9)]
    return join(P((x - w / 2, top), (x - w / 2, y + h / 2), (x + w / 2, y + h / 2), (x + w / 2, top)), P(*zz),
                P((x - w / 2 - 20, top), (x + w / 2 + 20, top)), rect(x + 90, y + h / 2 - 90, 100, 180, 6),
                rect(x - 90, y + 20, 140, 100, 6))


def barrier(x, y, w=300) -> skia.Path:
    """施工路障：横板 + 斜纹 + 两条腿。(x, y) 为横板中心。"""
    parts = [rect(x, y, w, 70, 8), P((x - w / 2 + 30, y + 35), (x - w / 2 + 30, y + 150)),
             P((x + w / 2 - 30, y + 35), (x + w / 2 - 30, y + 150))]
    for i in range(4):
        x0 = x - w / 2 + 40 + i * 70
        parts.append(P((x0, y + 30), (x0 + 50, y - 30)))
    return join(*parts)


def factory(x, y) -> skia.Path:
    """工厂：楼 + 烟囱。(x, y) 为底边中点。"""
    return join(building(x, y, 300, 330), P((x + 90, y - 330), (x + 90, y - 450), (x + 140, y - 450), (x + 140, y - 330)))


def spot_fn(x, y, r, color, alpha=1.0):
    def fn(c, k, t):
        K.dot(c, x, y, r * k, color, alpha)
        return None

    return fn

def flicker_fn(x, y, ons):
    def fn(c, k, t):
        if any(a <= t < a2 for a, a2 in ons):
            K.dot(c, x, y, 34, "#F2C230", 0.9)
        return None

    return fn


def dice_fn(x, y, t0, t1):
    """骰子在 t0–t1 之间乱跳点数，t1 后停在 2 点。"""

    def fn(c, k, t):
        if t < t0:
            return None
        n = 2 if t >= t1 else 1 + int((t - t0) * 12) % 6
        c.drawPath(dice(x, y, n), marker(BLACK, 8))
        return None

    return fn


def wave_fn(x, y, t0, t_big):
    def fn(c, k, t):
        if t < t0:
            return None
        big = clamp01((t - t_big) / 0.3) if t >= t_big else 0.0
        amp = 18 + 22 * big
        c.drawPath(wave(x, y, 170, amp, (t - t0) * 6), marker(RED if big > 0.5 else BLACK, 8))
        return None

    return fn


def fill_fn(x, y, w, h, beats):
    """罐子按拍一格格装满（每拍一格，绿色）。"""

    def fn(c, k, t):
        lv = 0.0
        for n, tb in enumerate(beats):
            lv = max(lv, (n + clamp01((t - tb) / 0.25)) / len(beats) if t >= tb else lv)
        hh = (h - 20) * lv
        if hh > 0:
            c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 12, y + h / 2 - 10 - hh, w - 24, hh), K.paint(GREEN, 0.35))
        return None

    return fn


# ---------------------------------------------------------------- 开局：绩效挺好，还是怕（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("刚评优秀，就传要裁", "灵魂拷问", (1100, 750, 0.62))
L(P((330, 1050), (1180, 1050)), 0, 0.3, BLACK, 6, sfx="wood_high")
L(stick(560, 1050, 0.85, "up"), 0.3, 0.9)
L(face(560, 1050, 0.85, "smile"), 0.9, 1.0)
L(doc(920, 720, 300, 360, 0), 1, 1.5, BLACK, 9, sfx="wood_high")
T("绩效", 920, 480, 70, k0=1.5, k1=1.9)
T("优秀", 920, 730, 110, RED, k0=2, k1=2.5, sfx="pop")
L(phone(1430, 720, 560, 640), 3, 3.6, BLACK, 9, sfx="wood_high")
T("小道消息", 1430, 350, 66, k0=3.6, k1=4.0)
L(rect(1430, 620, 500, 130, 40), 4, 4.3, BLUE, 8, sfx="pop")
T("下个月要优化", 1430, 620, 64, BLUE, k0=4.3, k1=4.9)
L(rect(1490, 820, 380, 130, 40), 5, 5.3, BLACK, 8, sfx="pop")
T("真的假的", 1490, 820, 64, k0=5.3, k1=5.7)
T("！", 1230, 820, 110, RED, k0=5.7, k1=6)

HEAD = (2680, 1960)
BED = (2950, 2050)
scene("半夜两点，怕上名单", "灵魂拷问", (2600, 2100, 0.62))
T("优化名单", 2000, 1500, 72, RED, k0=0, k1=0.7, sfx="pop")
L(podium_list(2000, 1650, 4, 420, 90), 1, 1.6, BLACK, 8, sfx="wood_high")
for n, w in enumerate(("老周", "小林", "阿杰", "我")):
    T(w, 2000, 1650 + n * 106, 60, BLUE if n == 3 else BLACK, k0=1.6 + n * 0.2, k1=1.8 + n * 0.2)
T("？", 2340, 1968, 110, RED, k0=3, k1=3.3, sfx="rim")
L(join(rect(*BED, 760, 110, 16), P((BED[0] - 380, BED[1] + 55), (BED[0] - 380, BED[1] + 140)),
       P((BED[0] + 380, BED[1] + 55), (BED[0] + 380, BED[1] + 140))), 4, 4.5, BLACK, 9, sfx="wood_high")
L(join(circle(*HEAD, 55), P((HEAD[0] + 60, HEAD[1] + 35), (HEAD[0] + 520, HEAD[1]), (HEAD[0] + 620, HEAD[1] + 35))),
  4.5, 4.9, BLACK, 9)
L(clock(3150, 1600, 100), 5, 5.4, BLACK, 9, sfx="wood_low")
L(hands_at(3150, 1600, 100, 2, 0), 5.4, 5.6, RED, 10)
T("02:00", 3150, 1765, 64, RED, k0=5.6, k1=6)
b.custom(J(), 6, 6.2, spot_fn(HEAD[0] - 18, HEAD[1] - 8, 7, BLACK), sfx="pop")
b.custom(J(), 6, 6.2, spot_fn(HEAD[0] + 18, HEAD[1] - 8, 7, BLACK))

scene("活干得好，为啥还怕", "灵魂拷问", (2600, 2100, 0.62), flashes=[5])
L(join(circle(HEAD[0] + 30, HEAD[1] - 85, 18), circle(HEAD[0] + 60, HEAD[1] - 150, 26)), 0, 0.3, BLACK, 7, sfx="pop")
L(rect(2700, 1640, 620, 230, 60), 0.3, 0.8, BLACK, 8)
T("房贷 ¥6800/月", 2700, 1590, 60, k0=1, k1=1.9, sfx="pop")
T("存款撑几个月？", 2700, 1700, 60, RED, k0=2, k1=2.9, sfx="pop")
L(scribble(HEAD[0], HEAD[1], 150, 90, 6), 3, 3.4, RED, 6, sfx="shaker")
T("活干得好好的", 2050, 2190, 84, k0=4, k1=4.8, sfx="pop")
T("为什么还怕？", 2050, 2330, 96, RED, k0=5, k1=5.8, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

AY = 3480
AX = [2130, 2390, 2650, 2910, 3170]
PX, PY, PS = 2650, AY + 730, 0.8
NAMES = ["才华", "运气", "雇主", "利润", "经济"]
PV = (2650, AY + 260, 0.85)           # 五根线大图的固定视角

j_bar = scene("有本书讲过这种怕", "身份的焦虑", (2310, AY + 370, 0.55))
j_drop, j_l01, j_l23, j_jerk, j_push = j_bar + 1, j_bar + 2, j_bar + 3, j_bar + 4, j_bar + 5
L(book(1550, AY + 310, 380, 260), 0, 0.8, sfx="wood_low")
T("身份的焦虑", 1550, AY + 80, 72, GREEN, k0=1, sfx="pop")
T("阿兰 · 德波顿", 1550, AY + 550, 56, k0=2, k1=2.6, sfx="pop")
T("第五章 制约因素", 1550, AY + 650, 56, RED, k0=2.6, k1=3.0)
L(P((2040, AY), (3260, AY)), 3, 3.5, BLACK, 14, sfx="wood_high")
T("你的地位", 2290, PY - 60, 58, k0=5, k1=5.7, sfx="pop")
for n, x in enumerate(AX):
    b.custom(J(), 5.7 + n * 0.1, 5.9 + n * 0.1, spot_fn(x, AY, 16, BLACK))
L(underline(1380, 1720, AY + 130), 5.7, 6, GREEN, 6)
b.hit(J(), 6, "pop", 0.6)
# 小人画在第 4–5 拍（puppet_fn 里），起笔配音效
b.hit(J(), 4, "wood_high", 0.8)

# 标签高亮窗口：(镜头, 起拍, 止拍)
HL = [(j_l01, 0, 4), (j_l01, 4, 8), (j_l23, 0, 4), (j_l23, 4, 8), (j_jerk, 0, 8)]


def _attach(x, y, s, arms):
    hy = y - 290 * s
    if arms == "up":
        lh, rh = (x - 80 * s, hy - 40 * s), (x + 80 * s, hy - 40 * s)
        le, re = (x - 40 * s, hy + 20 * s), (x + 40 * s, hy + 20 * s)
    else:
        lh, rh = (x - 70 * s, hy + 170 * s), (x + 70 * s, hy + 170 * s)
        le, re = (x - 35 * s, hy + 125 * s), (x + 35 * s, hy + 125 * s)
    return [lh, le, (x, hy - 45 * s), re, rh]


def _bump(t, tb, dur=0.4):
    f = (t - tb) / dur
    return math.sin(math.pi * f) if 0 <= f <= 1 else 0.0


def puppet_fn(c, k, t):
    """被五根线吊着的小人：场景 4 第 4–5 拍画出；场景 5 drop 时五根线同时绷上；标签场景里当前那根加粗；
    场景 8 第 3 拍经济那根一抖，小人跟着晃；场景 9 举手使劲往上蹦，还是被线拴着。"""
    t_fig0, t_fig1 = b.t_of(j_bar, 4), b.t_of(j_bar, 5)
    t_drop, t_jerk = b.t_of(j_drop, 0), b.t_of(j_jerk, 3)
    t_up = b.t_of(j_push, 0)
    dx = dy = 0.0
    if t >= t_drop:
        dx += 6 * math.sin((t - t_drop) * 2.4)
    jo = 0.0
    if t >= t_jerk:
        d = t - t_jerk
        dx += 70 * math.sin(d * 7) * math.exp(-d * 0.8)
        jo = 60 * math.sin(d * 16) * math.exp(-d * 3)
    for kb in (0, 1, 2):
        dy -= 70 * _bump(t, b.t_of(j_push, kb))
    arms = "up" if t >= t_up else "down"
    m = "sad" if t >= t_jerk else "flat"
    x, y = PX + dx, PY + dy
    fig = join(stick(x, y, PS, arms), face(x, y, PS, m))
    tip = None
    if t < t_fig0:
        return None
    if t < t_fig1:
        part, tip = partial(fig, clamp01((t - t_fig0) / (t_fig1 - t_fig0)))
        c.drawPath(part, marker(BLACK, 9))
    else:
        c.drawPath(fig, marker(BLACK, 9))
    if t >= t_drop:
        f = clamp01((t - t_drop) / 0.18)
        for i, (px, py) in enumerate(_attach(x, y, PS, arms)):
            ax = AX[i] + (jo if i == 4 else 0)
            jj, ka, kb = HL[i]
            hl = b.t_of(jj, ka) <= t < b.t_of(jj, kb)
            c.drawPath(P((ax, AY), (ax + (px - ax) * f, AY + (py - AY) * f)), marker(RED, 13 if hl else 7))
            K.dot(c, ax, AY, 16, BLACK)
    return tip


b.custom(j_bar, 4, 5, puppet_fn)

scene("五样都由不得你", "书中观点 · 五根线", PV, shake=[0], flashes=[0])
b.hit(J(), 0, "kick", 1.0, "五根线同时绷上")
T("管不了！", 3110, AY + 390, 64, RED, k0=1, sfx="rim")
H(2, "tom", 0.7)
H(3, "tom", 0.5)

scene("才华运气，都说不准", "书中观点 · 才华 运气", PV)
x0, x1 = AX[0], AX[1]
T("才华", x0, AY - 60, 54, RED, k0=0, sfx="pop")
L(bulb(x0, AY - 220), 1, 1.5, BLACK, 8, sfx="wood_high")
b.custom(J(), 2, 2.2, flicker_fn(x0, AY - 220, [(b.t_of(J(), 2), b.t_of(J(), 2.5)), (b.t_of(J(), 3), b.t_of(J(), 3.4))]),
         sfx="pop")
H(3, "pop", 0.6)
T("运气", x1, AY - 60, 54, RED, k0=4, sfx="pop")
b.custom(J(), 5, 5.2, dice_fn(x1, AY - 200, b.t_of(J(), 5), b.t_of(J(), 6.5)), sfx="wood_high")
H(6, "shaker")

scene("老板公司，你管不了", "书中观点 · 雇主 利润", PV)
x2, x3 = AX[2], AX[3]
T("雇主", x2, AY - 60, 54, RED, k0=0, sfx="pop")
L(stick(x2, AY - 130, 0.3, "down", tie=True), 1, 1.4, BLACK, 7, sfx="wood_high")
L(check(x2 + 85, AY - 230, 30), 2, 2.2, GREEN, 8, sfx="pop")
L(cross(x2 + 85, AY - 230, 34), 3, 3.25, RED, 9, sfx="rim")
T("利润", x3, AY - 60, 54, RED, k0=4, sfx="pop")
L(chart(x3, AY - 200), 4.5, 4.9, BLACK, 7)
L(arrow((x3 - 55, AY - 240), (x3 + 65, AY - 165), 0.05, 30), 5, 5.4, RED, 8, sfx="rim")
T("亏", x3 + 70, AY - 250, 50, RED, k0=5.4, k1=5.9)

scene("大环境一动你就晃", "书中观点 · 经济", PV, shake=[3])
x4 = AX[4]
T("经济", x4, AY - 60, 54, RED, k0=0, sfx="pop")
b.custom(J(), 1, 1.2, wave_fn(x4, AY - 200, b.t_of(J(), 1), b.t_of(J(), 2)), sfx="wood_high")
H(2, "shaker")
H(3, "kick", 0.9)
T("晃", 2300, AY + 490, 90, RED, k0=4, sfx="tom")
H(5, "tom", 0.5)

scene("再拼也拴着，怕很正常", "书中观点 · 一张图", (2650, AY + 420, 0.64))
for kb in (0, 1, 2):
    H(kb, "pop" if kb != 1 else "wood_high", 0.7)
T("使劲干", 3110, AY + 500, 58, k0=1.2, k1=1.8)
T("还是被拴着", 3110, AY + 610, 54, BLUE, k0=3, sfx="rim")
T("怕，很正常", 2650, AY + 1000, 110, RED, k0=4, k1=4.9, sfx="kick")
L(underline(2380, 2920, AY + 1075), 5, 5.4, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 5300 + D), (2650, 5300 + D), (950, 6200 + D + R), (2650, 6200 + D + R)]
OV = (1800, 6790, 0.345)
scene("身边常有这种事", "身边的例子", OV)
T("身边的例子", 1800, 5500, 110, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 2 + n, 2.5 + n, GREEN, 8, sfx="wood_high" if n in (0, 2) else None)

scene("项目漂亮，业务被砍", "例子 · 项目被砍", (950, 5350 + D, 0.85), shake=[3])
L(stick(600, 5650 + D, 0.75, "up"), 0, 0.6, sfx="wood_high")
L(face(600, 5650 + D, 0.75, "smile"), 0.6, 0.7)
L(doc(1100, 5280 + D, 230, 280), 1, 1.5, BLACK, 9, sfx="wood_high")
L(check(1100, 5280 + D, 70), 2, 2.3, GREEN, 12, sfx="ding")
T("项目上线", 1100, 5040 + D, 60, k0=2.4, k1=3.0)
L(cross(1100, 5280 + D, 160), 3, 3.4, RED, 14, sfx="rim")
T("业务砍掉", 1060, 5530 + D, 60, RED, k0=4, k1=4.7, sfx="kick")
mood(600, 5650 + D, 0.75, "sad", 5, BLUE, sfx="wood_high")

scene("新领导带来自己人", "例子 · 换领导", (2650, 5350 + D, 0.85))
L(stick(2650, 5650 + D, 0.75, "point", tie=True), 0, 0.6, sfx="wood_high")
L(face(2650, 5650 + D, 0.75, "flat"), 0.6, 0.7)
T("新领导", 2650, 5320 + D, 56, k0=1, sfx="pop")
L(stick(2300, 5650 + D, 0.6), 2, 2.5, BLUE, 9, sfx="pop")
T("我", 2300, 5370 + D, 54, BLUE, k0=2.5, k1=2.8)
for n, x in enumerate((2870, 3010, 3150)):
    L(stick(x, 5650 + D, 0.5), 3 + n * 0.25, 3.4 + n * 0.25, BLACK, 8, sfx="wood_high" if n == 0 else None)
T("老部下", 3010, 5410 + D, 52, k0=4, k1=4.6, sfx="pop")
L(arrow((2240, 5560 + D), (2100, 5560 + D), 0.1, 30), 5, 5.4, RED, 9, sfx="rim")
T("靠边站", 2300, 5265 + D, 56, RED, k0=5.4, k1=5.95)

scene("面馆门口修路半年", "例子 · 小店", (950, 6200 + D + R, 0.85))
L(shop(780, 6250 + D + R), 0, 0.8, BLACK, 9, sfx="wood_high")
T("面馆", 780, 5990 + D + R, 60, k0=1, sfx="pop")
for n, x in enumerate((1170, 1320)):
    L(stick(x, 6520 + D + R, 0.5), 2 + n * 0.3, 2.4 + n * 0.3, BLACK, 8, sfx="pop" if n == 0 else None)
b.erase(J(), 3, 3.5, 1245, 6330 + D + R, 330, 440)
H(3, "shaker")
L(barrier(1240, 6380 + D + R, 280), 4, 4.6, RED, 9, sfx="wood_high")
T("修路 6个月", 1240, 6170 + D + R, 52, RED, k0=4.6, k1=5.3)
T("没客人", 780, 6520 + D + R, 52, BLUE, k0=5.4, k1=5.95)
H(5, "rim", 0.6)

scene("老爸的厂说停就停", "例子 · 家里", (2650, 6200 + D + R, 0.85), shake=[3])
L(factory(2900, 6540 + D + R), 0, 0.8, BLACK, 9, sfx="wood_high")
L(stick(2350, 6540 + D + R, 0.7), 1, 1.5, BLUE, 9, sfx="pop")
L(face(2350, 6540 + D + R, 0.7, "smile"), 1.5, 1.6, BLUE, 8)
T("厂里 20年", 2400, 5980 + D + R, 58, k0=2, k1=2.8, sfx="pop")
L(cross(2900, 6360 + D + R, 150), 3, 3.4, RED, 14, sfx="kick")
T("停产", 3170, 6080 + D + R, 60, RED, k0=4, sfx="rim")
mood(2350, 6540 + D + R, 0.7, "sad", 5, BLUE, sfx="wood_high")

scene("每件都连着一根线", "身边的例子", OV, shake=[4])
for n, ((x, y), w) in enumerate(zip(CARDS, ("利润", "雇主", "运气", "经济"))):
    T(w, x + 430, y - 320, 90, RED, k0=n, sfx="pop")
T("人没做错什么", 1800, 5750 + D + R // 2, 130, RED, k0=4, k1=5, sfx="kick")
H(5, "ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

SOL = [(950, 7850 + D + R), (2650, 7850 + D + R), (950, 8750 + D + R + R2), (2650, 8750 + D + R + R2)]

scene("能管的管，管不了先放", "第一步 · 分两栏", (950, 7880 + D + R, 0.85))
L(rect(*SOL[0], 1200, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("① 分两栏", 950, 7560 + D + R, 76, BLUE, k0=1, sfx="pop")
L(P((950, 7650 + D + R), (950, 8200 + D + R)), 1.8, 2.0, BLACK, 8)
T("能管的", 680, 7700 + D + R, 60, GREEN, k0=2, k1=2.5, sfx="pop")
T("管不了", 1220, 7700 + D + R, 60, RED, k0=2.5, k1=3.0)
for n, w in enumerate(("手上的活", "学新本事")):
    T(w, 680, 7830 + n * 110 + D + R, 52, k0=3 + n * 0.6, k1=3.55 + n * 0.6, sfx="pop" if n == 0 else None)
for n, w in enumerate(("裁员名单", "大行情")):
    T(w, 1220, 7830 + n * 110 + D + R, 52, k0=4.2 + n * 0.45, k1=4.6 + n * 0.45)
H(4, "wood_low", 0.6)
L(join(P((1100, 7830 + D + R), (1340, 7830 + D + R)), P((1130, 7940 + D + R), (1310, 7940 + D + R))), 5, 5.3, RED, 8, sfx="rim")
T("先放一放", 1220, 8070 + D + R, 52, BLUE, k0=5.3, k1=5.95)

scene("先存半年开销", "第二步 · 留缓冲", (2650, 7880 + D + R, 0.85))
L(rect(*SOL[1], 1200, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("② 留缓冲", 2650, 7560 + D + R, 76, BLUE, k0=1, sfx="pop")
L(jar(2420, 7930 + D + R), 2, 2.6, BLACK, 9, sfx="wood_high")
T("存款", 2420, 8130 + D + R, 50, k0=2.6, k1=2.95)
jj = J()
b.custom(jj, 3, 3.3, fill_fn(2420, 7930 + D + R, 220, 300, [b.t_of(jj, 3), b.t_of(jj, 4), b.t_of(jj, 5)]), sfx="pop")
T("6个月开销", 2880, 7780 + D + R, 56, RED, k0=3.2, k1=4.0)
H(4, "pop")
T("发了工资先存", 2880, 7930 + D + R, 52, k0=4.2, k1=5.1)
H(5, "pop")
L(check(2880, 8060 + D + R, 40), 5.4, 5.7, GREEN, 9)
H(6, "ding", 0.6)

scene("攒本事，也攒人脉", "第三步 · 本事人脉", (950, 8780 + D + R + R2, 0.85))
L(rect(*SOL[2], 1200, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("③ 本事和人脉", 950, 8460 + D + R + R2, 76, BLUE, k0=1, sfx="pop")
L(stick(560, 9100 + D + R + R2, 0.65, "hold"), 2, 2.5, BLUE, 9, sfx="wood_high")
L(face(560, 9100 + D + R + R2, 0.65, "smile"), 2.5, 2.65, BLUE, 8)
L(doc(800, 8790 + D + R + R2, 150, 190), 3, 3.4, BLACK, 8, sfx="pop")
T("作品", 800, 8640 + D + R + R2, 48, k0=3.4, k1=3.8)
L(stick(1300, 9100 + D + R + R2, 0.6), 4, 4.4, BLACK, 9, sfx="wood_high")
L(face(1300, 9100 + D + R + R2, 0.6, "smile"), 4.4, 4.5)
L(rect(1180, 8720 + D + R + R2, 380, 110, 40), 5, 5.3, BLACK, 8, sfx="pop")
T("最近咋样？", 1180, 8720 + D + R + R2, 50, k0=5.3, k1=5.95)

STOOL_Y = 8680 + D + R + R2
scene("多几条腿，站得稳", "第四步 · 多几条腿", (2650, STOOL_Y + 170, 0.85))
L(rect(*SOL[3], 1200, 820, 40), 0, 0.6, GREEN, 8, sfx="wood_high")
T("④ 多几条腿", 2650, STOOL_Y - 220, 76, BLUE, k0=1, sfx="pop")
L(P((2280, STOOL_Y), (3020, STOOL_Y)), 2, 2.3, BLACK, 12, sfx="wood_high")
L(P((2650, STOOL_Y), (2650, STOOL_Y + 300)), 2.3, 2.5, BLACK, 12)
T("工作", 2650, STOOL_Y + 360, 50, k0=2.5, k1=2.8)
L(stick(2650, STOOL_Y - 10, 0.45), 2.8, 3.0, BLUE, 8)
for n, (x, w) in enumerate(((2330, "家人"), (2490, "朋友"), (2810, "爱好"), (2970, "存款"))):
    L(P((x, STOOL_Y), (x, STOOL_Y + 300)), 3 + n * 0.5, 3.2 + n * 0.5, GREEN, 12,
      sfx="wood_high" if n % 2 == 0 else None)
    T(w, x, STOOL_Y + 360, 46, GREEN, k0=3.2 + n * 0.5, k1=3.45 + n * 0.5)
L(check(3170, STOOL_Y - 100, 40), 5, 5.25, GREEN, 10, sfx="ding")

# ---------------------------------------------------------------- 收尾（场景 20–21）

scene("能管的先管好", "一句话", (1800, 7400, 0.2))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 9780 + D + R + R2 + 200, 0.8))
H(0, "cymbal", 0.5)
T("你给自己留了几条腿？", 1800, 9690 + D + R + R2 + 200, 76, RED, k0=1, k1=2.6)
H(1, "pop")
T("下一讲：别人一句话，为什么能堵你一整天？", 1800, 9850 + D + R + R2 + 200, 48, k0=3, k1=4.5)
H(3, "wood_high", 0.7)
b.hit(J(), 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "depend", "制约因素", "工作干得好好的，为什么还怕被裁？", ACC, b.shots,
                 [f"{BOOK}第一部分“焦虑起因”第五章“制约因素”（转述）",
                  "原书：Alain de Botton, Status Anxiety, Hamish Hamilton / Pantheon, 2004",
                  "中译本：陈广兴、南治国译，上海译文出版社"],
                 "干得好好的|为什么还【怕被裁】", 4,
                 ["书中观点均为转述：作者在第一部分第五章“制约因素”中指出，一个人的地位取决于几样自己控制不了的东西——"
                  "才华（时灵时不灵）、运气、雇主、雇主的利润和整体经济，所以再努力也难高枕无忧，为地位担心是可以理解的。"
                  "出处：Alain de Botton, Status Anxiety (Hamish Hamilton / Pantheon, 2004)，中译本《身份的焦虑》"
                  "（陈广兴、南治国译，上海译文出版社）。上屏均为转述，不是逐字引文；“五根线吊着的小人”是本讲为说明观点画的示意图。",
                  "绩效优秀、部门优化传闻、房贷数字、项目所在业务被砍、新领导带自己的人、面馆门口修路、父亲所在工厂停产均为现实场景"
                  "示意，数字为示意，不指向任何具体公司或个人。",
                  "四步做法（分清能管和管不了的、存够几个月开销留缓冲、攒带得走的本事和人脉、别把自己全押在一份工作上）"
                  "为据书中思路整理的建议，不是书中原有的清单。"],
                 tags="#裁员 #职场")
    return b.attach(ep)
