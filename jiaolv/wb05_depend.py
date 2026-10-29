"""05 制约因素（白板手绘版）：工作干得好好的，为什么还怕被裁？

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
SQUARE_SHOT = 15

b = Board(size=(3600, 10200))


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


# ---------------------------------------------------------------- 开局：绩效挺好，还是怕（镜头 1–6）

b.shot("绩效拿了个优秀", "灵魂拷问", view=(950, 850, 0.85))
L(P((420, 1180), (1480, 1180)), 0, 0.4, BLACK, 6, sfx="wood_high")
L(stick(1200, 1180, 0.75, "up"), 1, 1.6, sfx="pop")
L(face(1200, 1180, 0.75, "smile"), 1.6, 1.75)
L(doc(700, 860, 260, 320), 2, 2.6, BLACK, 9, sfx="wood_high")
T("绩效", 700, 620, 60, k0=2.6)
T("优秀", 960, 760, 90, RED, k0=3, k1=3.3, sfx="pop")

b.shot("听说部门要优化", "灵魂拷问", view=(2650, 850, 0.85))
L(phone(2650, 870, 560, 800), 0, 0.8, BLACK, 9, sfx="wood_high")
T("小道消息", 2650, 560, 56, k0=0.8)
L(rect(2620, 760, 440, 120, 40), 1, 1.3, BLUE, 8, sfx="pop")
T("下个月要优化", 2620, 760, 56, BLUE, k0=1.3)
L(rect(2680, 950, 380, 120, 40), 2, 2.3, BLACK, 8, sfx="pop")
T("真的假的", 2680, 950, 56, k0=2.3)
T("！", 3070, 640, 120, RED, k0=3, k1=3.3, sfx="rim")

b.shot("名单上有我吗", "灵魂拷问", view=(950, 1800, 0.85))
T("优化名单", 950, 1380, 66, RED, k0=0, sfx="pop")
L(podium_list(900, 1560, 4, 420, 90), 0.8, 1.6, BLACK, 8, sfx="wood_high")
for n, w in enumerate(("老周", "小林", "阿杰", "我")):
    T(w, 900, 1560 + n * 106, 54, BLUE if n == 3 else BLACK, k0=1.6 + n * 0.2, k1=1.8 + n * 0.2)
T("？", 1240, 1878, 100, RED, k0=3, k1=3.3, sfx="rim")
L(stick(480, 2180, 0.6), 2, 2.4, BLUE, 9, sfx="pop")
L(face(480, 2180, 0.6, "flat"), 2.4, 2.5, BLUE, 8)

BED = (2650, 2080)
HEAD = (2380, 1990)
b.shot("半夜两点睡不着", "灵魂拷问", view=(2650, 1800, 0.85))
L(join(rect(*BED, 760, 110, 16), P((2270, 2135), (2270, 2220)), P((3030, 2135), (3030, 2220))), 0, 0.6, BLACK, 9,
  sfx="wood_high")
L(join(circle(*HEAD, 55), P((2440, 2025), (2900, 1990), (3000, 2025))), 0.6, 1.0, BLACK, 9)
L(clock(2260, 1430, 100), 1, 1.5, BLACK, 9, sfx="wood_low")
L(hands_at(2260, 1430, 100, 2, 0), 1.5, 1.7, RED, 10)
T("02:00", 2260, 1590, 60, RED, k0=2, sfx="pop")
moon = skia.Path()
moon.addArc(skia.Rect.MakeXYWH(2960, 1350, 140, 140), 60, 240)
moon.quadTo(3010, 1420, 3065, 1471)
L(moon, 2, 2.4, BLACK, 8)
b.custom(J(), 3, 3.2, spot_fn(HEAD[0] - 18, HEAD[1] - 8, 7, BLACK), sfx="pop")
b.custom(J(), 3, 3.2, spot_fn(HEAD[0] + 18, HEAD[1] - 8, 7, BLACK))

b.shot("躺着算房贷", "灵魂拷问", view=(2650, 1750, 0.85))
L(join(circle(2420, 1880, 18), circle(2470, 1830, 26)), 0, 0.3, BLACK, 7, sfx="pop")
L(rect(2760, 1700, 720, 250, 60), 0.3, 0.8, BLACK, 8)
T("房贷 ¥6800/月", 2760, 1650, 56, k0=1, sfx="pop")
T("存款撑几个月？", 2760, 1750, 56, RED, k0=2, sfx="pop")
L(scribble(2380, 1990, 150, 90, 6), 3, 3.4, RED, 6, sfx="shaker")

b.shot("干得好，怎么还怕？", "灵魂拷问", view=(1800, 1300, 0.42), flashes=[1])
T("活干得好好的", 1800, 250, 120, k0=0, k1=1.0, sfx="pop")
T("为什么还怕？", 1800, 400, 130, RED, k0=1, k1=1.8, sfx="kick")
H(3, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "身份的焦虑", view=(1050, 3250, 0.9))
L(book(800, 3250, 420, 280), 0, 1.0, sfx="wood_low")
T("身份的焦虑", 800, 3000, 76, GREEN, k0=1.0, sfx="pop")
T("阿兰 · 德波顿", 800, 3490, 52, k0=2.0, sfx="pop")
T("第五章 制约因素", 800, 3590, 48, RED, k0=3.0, sfx="pop")

AX = [2130, 2390, 2650, 2910, 3170]
AY = 2990
PX, PY, PS = 2650, 3720, 0.8
NAMES = ["才华", "运气", "雇主", "利润", "经济"]

j_bar = b.shot("地位拴在五样上", "书中观点 · 五根线", view=(2650, 3250, 0.85))
j_drop = j_bar + 1
j_lab = j_bar + 2                # 五个标签镜头：j_lab … j_lab+4
j_jerk = j_bar + 7
j_push = j_bar + 8
L(P((2040, AY), (3260, AY)), 0, 0.5, BLACK, 14, sfx="wood_high")
T("你的地位", 2290, 3660, 54, k0=2, sfx="pop")
for n, x in enumerate(AX):
    b.custom(J(), 3 + n * 0.12, 3.2 + n * 0.12, spot_fn(x, AY, 16, BLACK), sfx="pop" if n == 0 else None)


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
    """被五根线吊着的小人：镜头 8 画出，drop 时五根线同时绷上；标签镜头里当前那根加粗；
    镜头 15 经济那根一抖，小人跟着晃；镜头 16 举手使劲往上蹦，还是被线拴着。"""
    t_fig0, t_fig1 = b.t_of(j_bar, 1), b.t_of(j_bar, 2)
    t_drop, t_jerk = b.t_of(j_drop, 0), b.t_of(j_jerk, 1)
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
    if t < t_fig1:
        part, tip = partial(fig, clamp01((t - t_fig0) / (t_fig1 - t_fig0)))
        c.drawPath(part, marker(BLACK, 9))
    else:
        c.drawPath(fig, marker(BLACK, 9))
    if t >= t_drop:
        f = clamp01((t - t_drop) / 0.18)
        for i, (px, py) in enumerate(_attach(x, y, PS, arms)):
            ax = AX[i] + (jo if i == 4 else 0)
            hl = b.t_of(j_lab + i, 0) <= t < b.t_of(j_lab + i, 4) or (i == 4 and b.t_of(j_jerk, 0) <= t < b.t_of(j_jerk, 4))
            c.drawPath(P((ax, AY), (ax + (px - ax) * f, AY + (py - AY) * f)), marker(RED, 13 if hl else 7))
            K.dot(c, ax, AY, 16, BLACK)
    return tip


b.custom(j_bar, 1, 2, puppet_fn, sfx="wood_high")

b.shot("五样都由不得你", "书中观点 · 五根线", view=(2650, 3250, 0.85), shake=[0], flashes=[0])
b.hit(J(), 0, "kick", 1.0, "五根线同时绷上")
T("管不了！", 3110, 3380, 60, RED, k0=1, sfx="rim")
H(2, "tom", 0.7)
H(3, "tom", 0.5)


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


for i, (cap, nm) in enumerate(zip(("才华时灵时不灵", "运气说变就变", "老板看不看重你", "公司赚不赚钱", "大环境好不好"), NAMES)):
    x = AX[i]
    b.shot(cap, f"书中观点 · {nm}", view=(2650, 3235 + (i % 2) * 30, 0.86 + 0.01 * i))
    T(nm, x, 2930, 52, RED, k0=0, sfx="pop")
    if i == 0:
        L(bulb(x, 2770), 1, 1.5, BLACK, 8, sfx="wood_high")
        b.custom(J(), 2, 2.2, flicker_fn(x, 2770, [(b.t_of(J(), 2), b.t_of(J(), 2.5)), (b.t_of(J(), 3), b.t_of(J(), 3.4))]),
                 sfx="pop")
        H(3, "pop", 0.6)
    elif i == 1:
        jj = J()
        b.custom(jj, 1, 1.2, dice_fn(x, 2790, b.t_of(jj, 1), b.t_of(jj, 3)), sfx="wood_high")
        H(2, "shaker")
        H(3, "pop")
    elif i == 2:
        L(stick(x, 2860, 0.3, "down", tie=True), 1, 1.4, BLACK, 7, sfx="wood_high")
        L(check(x + 85, 2760, 30), 2, 2.2, GREEN, 8, sfx="pop")
        L(cross(x + 85, 2760, 34), 3, 3.25, RED, 9, sfx="rim")
    elif i == 3:
        L(chart(x, 2790), 1, 1.4, BLACK, 7, sfx="wood_high")
        L(arrow((x - 55, 2750), (x + 65, 2825), 0.05, 30), 2, 2.4, RED, 8, sfx="rim")
        T("亏", x + 70, 2740, 50, RED, k0=3, sfx="pop")
    else:
        jj = J()
        b.custom(jj, 1, 1.2, wave_fn(x, 2790, b.t_of(jj, 1), b.t_of(jj, 2)), sfx="wood_high")
        H(2, "shaker")
        H(3, "tom", 0.6)

b.shot("哪根一动你就晃", "书中观点 · 晃", view=(2650, 3250, 0.85), shake=[1])
H(0, "wood_low", 0.6)
H(1, "kick", 0.9)
T("晃", 2300, 3480, 80, RED, k0=2, sfx="tom")
H(3, "tom", 0.5)

b.shot("再拼也难睡踏实", "书中观点 · 使劲", view=(2650, 3250, 0.85))
for kb in (0, 1, 2):
    H(kb, "pop" if kb != 1 else "wood_high", 0.7)
T("使劲干", 3110, 3540, 54, k0=1)
T("还是被拴着", 3110, 3680, 50, BLUE, k0=3, sfx="rim")

b.shot("所以怕很正常", "书中观点 · 一张图", view=(1880, 3350, 0.38))
L(arrow((1250, 3300), (1950, 3300), -0.12, 50), 0, 0.6, GREEN, 10, sfx="wood_high")
T("五根线管不了 → 怕，很正常", 1800, 4150, 100, RED, k0=1, k1=2.6, sfx="pop")
L(underline(1180, 2420, 4230), 3, 3.4, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5300), (2650, 5300), (950, 6200), (2650, 6200)]
b.shot("身边常有这种事", "身边的例子", view=(1800, 5750, 0.355))
T("身边的例子", 1800, 4720, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("项目做得挺漂亮", "例子 · 项目被砍", view=(950, 5300, 0.85))
L(stick(600, 5650, 0.75, "up"), 0, 0.6, sfx="wood_high")
L(face(600, 5650, 0.75, "smile"), 0.6, 0.7)
L(doc(1100, 5280, 230, 280), 1, 1.5, BLACK, 9, sfx="wood_high")
L(check(1100, 5280, 70), 2, 2.3, GREEN, 12, sfx="ding")
T("项目上线", 1100, 5040, 60, k0=3, sfx="pop")

b.shot("整条业务被砍了", "例子 · 项目被砍", view=(950, 5300, 0.85), shake=[1])
L(cross(1100, 5280, 160), 0, 0.4, RED, 14, sfx="rim")
T("业务砍掉", 1100, 5530, 60, RED, k0=1, sfx="kick")
mood(600, 5650, 0.75, "sad", 2, BLUE, sfx="wood_high")
T("……", 600, 5300, 60, k0=3, sfx="pop")

b.shot("来了个新领导", "例子 · 换领导", view=(2650, 5300, 0.85))
L(stick(2650, 5650, 0.75, "point", tie=True), 0, 0.6, sfx="wood_high")
L(face(2650, 5650, 0.75, "flat"), 0.6, 0.7)
T("新领导", 2650, 5320, 56, k0=1, sfx="pop")
L(stick(2300, 5650, 0.6), 2, 2.5, BLUE, 9, sfx="pop")
T("我", 2300, 5370, 54, BLUE, k0=3, sfx="pop")

b.shot("带来自己的人", "例子 · 换领导", view=(2650, 5300, 0.85))
for n, x in enumerate((2870, 3010, 3150)):
    L(stick(x, 5650, 0.5), n * 0.25, n * 0.25 + 0.4, BLACK, 8, sfx="wood_high" if n == 0 else None)
T("老部下", 3010, 5410, 52, k0=1, sfx="pop")
L(arrow((2240, 5560), (2100, 5560), 0.1, 30), 2, 2.4, RED, 9, sfx="rim")
T("靠边站", 2300, 5000, 56, RED, k0=3, sfx="pop")

b.shot("街角开了家面馆", "例子 · 小店", view=(950, 6200, 0.85))
L(shop(780, 6250), 0, 0.8, BLACK, 9, sfx="wood_high")
T("面馆", 780, 5990, 60, k0=1, sfx="pop")
for n, x in enumerate((1170, 1320)):
    L(stick(x, 6520, 0.5), 2 + n * 0.3, 2.4 + n * 0.3, BLACK, 8, sfx="pop" if n == 0 else None)
T("排队", 1245, 6180, 52, k0=3, sfx="pop")

b.shot("门口修路半年", "例子 · 小店", view=(950, 6200, 0.85))
b.erase(J(), 0, 0.5, 1245, 6330, 330, 440)
H(0, "shaker")
L(barrier(1240, 6380, 280), 1, 1.6, RED, 9, sfx="wood_high")
T("修路 6个月", 1240, 6170, 52, RED, k0=2, sfx="pop")
T("没客人", 780, 6520, 52, BLUE, k0=3, sfx="rim")

b.shot("老爸干了二十年", "例子 · 家里", view=(2650, 6200, 0.85))
L(factory(2900, 6540), 0, 0.8, BLACK, 9, sfx="wood_high")
L(stick(2350, 6540, 0.7), 1, 1.5, BLUE, 9, sfx="pop")
L(face(2350, 6540, 0.7, "smile"), 1.5, 1.6, BLUE, 8)
T("厂里 20年", 2400, 5980, 58, k0=2, sfx="pop")
L(underline(2240, 2560, 6030), 3, 3.3, BLACK, 6, sfx="wood_high")

b.shot("厂子说停就停", "例子 · 家里", view=(2650, 6200, 0.85), shake=[0])
L(cross(2900, 6360, 150), 0, 0.4, RED, 14, sfx="kick")
T("停产", 3200, 6100, 60, RED, k0=1, sfx="rim")
mood(2350, 6540, 0.7, "sad", 2, BLUE, sfx="wood_high")
T("……", 2350, 6200, 60, BLUE, k0=3, sfx="pop")

b.shot("每件都连着一根线", "身边的例子", view=(1800, 5750, 0.355))
for n, ((x, y), w) in enumerate(zip(CARDS, ("利润", "雇主", "运气", "经济"))):
    T(w, x + 430, y - 320, 90, RED, k0=n, sfx="pop")

b.shot("人没做错什么", "身边的例子", view=(1800, 5750, 0.355), shake=[0])
T("人没做错什么", 1800, 6820, 150, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 7850), (2650, 7850), (950, 8750), (2650, 8750)]
b.shot("心里慌，这样做", "具体做法", view=(1800, 8300, 0.355))
T("心里慌，这样做", 1800, 7250, 130, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("拿张纸分两栏", "第一步 · 分两栏", view=(950, 7850, 0.85))
T("① 分两栏", 950, 7560, 76, BLUE, k0=0, sfx="pop")
L(P((950, 7650), (950, 8200)), 1, 1.4, BLACK, 8, sfx="wood_high")
T("能管的", 680, 7700, 60, GREEN, k0=2, sfx="pop")
T("管不了", 1220, 7700, 60, RED, k0=3, sfx="pop")

b.shot("能管的写左边", "第一步 · 分两栏", view=(950, 7880, 0.85))
for n, w in enumerate(("手上的活", "学新本事", "每天睡够")):
    T(w, 680, 7820 + n * 110, 52, k0=n, sfx="pop")
L(check(870, 8040, 32), 3, 3.25, GREEN, 9, sfx="ding")

b.shot("管不了的先放下", "第一步 · 分两栏", view=(950, 7880, 0.85))
for n, w in enumerate(("裁员名单", "大行情")):
    T(w, 1220, 7820 + n * 110, 52, k0=n * 0.5, k1=n * 0.5 + 0.4, sfx="pop" if n == 0 else None)
L(join(P((1100, 7820), (1340, 7820)), P((1130, 7930), (1310, 7930))), 1, 1.4, RED, 8, sfx="rim")
T("先放一放", 1220, 8060, 52, BLUE, k0=2, sfx="pop")
H(3, "wood_low", 0.6)

b.shot("给自己留缓冲", "第二步 · 留缓冲", view=(2650, 7850, 0.85))
T("② 留缓冲", 2650, 7560, 76, BLUE, k0=0, sfx="pop")
L(jar(2420, 7930), 1, 1.6, BLACK, 9, sfx="wood_high")
T("存款", 2420, 8130, 50, k0=2, sfx="pop")
L(circle(2420, 7670, 30), 3, 3.2, GREEN, 8, sfx="pop")
T("¥", 2420, 7672, 40, GREEN, k0=3.2, k1=3.3)


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


b.shot("先存半年开销", "第二步 · 留缓冲", view=(2650, 7850, 0.85))
jj = J()
b.custom(jj, 0, 0.3, fill_fn(2420, 7930, 220, 300, [b.t_of(jj, 0), b.t_of(jj, 1), b.t_of(jj, 2)]), sfx="pop")
H(1, "pop")
H(2, "pop")
T("6个月开销", 2880, 7780, 56, RED, k0=1)
L(check(2880, 7880, 36), 3, 3.25, GREEN, 9, sfx="ding")

b.shot("发了工资先存", "第二步 · 留缓冲", view=(2650, 7900, 0.85))
T("发工资", 2880, 7990, 52, k0=0, sfx="pop")
L(arrow((2880, 8030), (2880, 8110), 0.0, 26), 1, 1.3, GREEN, 8, sfx="wood_high")
T("先存一笔", 2880, 8160, 52, GREEN, k0=2, sfx="pop")
L(underline(2760, 3000, 8205), 3, 3.3, RED, 6, sfx="ding")

b.shot("攒带得走的本事", "第三步 · 本事人脉", view=(950, 8750, 0.85))
T("③ 本事和人脉", 950, 8460, 76, BLUE, k0=0, sfx="pop")
L(stick(620, 9100, 0.65, "hold"), 1, 1.5, BLUE, 9, sfx="wood_high")
L(doc(860, 8790, 150, 190), 2, 2.4, BLACK, 8, sfx="pop")
T("作品", 860, 8640, 48, k0=2.4)
T("走到哪都能用", 1150, 9000, 50, RED, k0=3, sfx="pop")

b.shot("简历每季改一次", "第三步 · 本事人脉", view=(950, 8750, 0.85))
L(doc(1220, 8720, 170, 210), 0, 0.5, BLACK, 8, sfx="wood_high")
T("简历", 1220, 8560, 50, k0=0.5)
T("每3个月改一次", 1150, 8890, 50, k0=1, k1=1.9)
L(check(1400, 8720, 36), 2, 2.25, GREEN, 9, sfx="ding")
H(3, "pop", 0.6)

b.shot("老同事常联系", "第三步 · 本事人脉", view=(950, 8800, 0.85))
b.erase(J(), 0, 0.5, 1200, 8800, 560, 460)
H(0, "shaker")
L(stick(1250, 9100, 0.6), 1, 1.4, BLACK, 9, sfx="wood_high")
L(face(1250, 9100, 0.6, "smile"), 1.4, 1.5)
L(rect(1150, 8740, 380, 110, 40), 2, 2.3, BLACK, 8, sfx="pop")
T("最近咋样？", 1150, 8740, 50, k0=2.3)
L(face(620, 9100, 0.65, "smile"), 3, 3.2, BLUE, 8, sfx="pop")

STOOL_Y = 8680
b.shot("别全押在工作上", "第四步 · 多几条腿", view=(2650, 8750, 0.85))
T("④ 多几条腿", 2650, 8460, 76, BLUE, k0=0, sfx="pop")
L(P((2280, STOOL_Y), (3020, STOOL_Y)), 1, 1.3, BLACK, 12, sfx="wood_high")
L(P((2650, STOOL_Y), (2650, 8980)), 1.3, 1.5, BLACK, 12)
T("工作", 2650, 9040, 50, k0=1.6)
L(stick(2650, STOOL_Y - 10, 0.45), 2, 2.4, BLUE, 8, sfx="pop")
T("一根腿，晃", 2950, 8580, 50, RED, k0=3, sfx="rim")

b.shot("多几条腿站得稳", "第四步 · 多几条腿", view=(2650, 8750, 0.85))
for n, (x, w) in enumerate(((2330, "家人"), (2490, "朋友"), (2810, "爱好"), (2970, "存款"))):
    L(P((x, STOOL_Y), (x, 8980)), n * 0.5, n * 0.5 + 0.2, GREEN, 12, sfx="wood_high" if n % 2 == 0 else None)
    T(w, x, 9040 if n % 2 == 0 else 9100, 46, GREEN, k0=n * 0.5 + 0.2, k1=n * 0.5 + 0.45)
L(check(3170, 8580, 40), 3, 3.25, GREEN, 10, sfx="ding")

b.shot("能管的先管好", "一句话", view=(1800, 5100, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 9780, 0.8))
T("你给自己留了几条腿？", 1800, 9690, 76, RED, k0=0.5, k1=1.8)
T("下一讲：别人一句话，为什么能堵你一整天？", 1800, 9850, 48, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(J(), 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "depend", "制约因素", "工作干得好好的，为什么还怕被裁？", ACC, b.shots,
                 [f"{BOOK}第一部分“焦虑起因”第五章“制约因素”（转述）",
                  "原书：Alain de Botton, Status Anxiety, Hamish Hamilton / Pantheon, 2004",
                  "中译本：陈广兴、南治国译，上海译文出版社"],
                 "干得好好的|为什么还【怕被裁】", 15,
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
