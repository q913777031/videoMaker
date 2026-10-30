"""10 少干浮活（白板手绘版）：活一件没少，怎么准点下班？（系列最后一讲）

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（H 对话改写，一句原话开局）：手机上弹来一句“在吗？有空聊聊？”→ 来回八条才约上 → 改写成一条说完的消息，
小红点被挡回去（书中“过程中心式”回复的示意）→ drop：一天切成彩色时间块，一块块砸进日程表，最后一块“17:30 下班”→
亮书《深度工作》：先在纸上把一天排成块；被打乱就擦掉重排，图的是心里有数 → 原话“这个你顺手弄一下”：先问新人要学多久，
学得越快越浅，浮活装进杂事箱一起干 → 跟上级对一下杂事占几成 → 先定下班点、倒推接哪些活 → 原话“收到，马上看”
改写成“周四给你”→ 有的群消息不回也行 → 收全系列：小周伸懒腰走向下班的门，小红点被一排改写过的消息挡在外头 →
拉远看全板，评论区问题 + 这一季讲完了。
书中观点为转述（卡尔·纽波特《深度工作》准则4“摒弃浮浅”：一天的每一分钟都要做好计划 / 定量分析每一项活动的深度 /
向老板申请浮浅工作预算 / 下午5点半之前结束工作 / 变得不容易联系到）；原话与改写、日程、比例均为示意，做法为据书中思路整理。

白板布局：3 列 × 4 行（列 x：650 / 1950 / 3250；行 y：800 / 2300 / 3800 / 5300），场景 1–12 按蛇形走位；
第 5 行（y≈7150）是收尾大画面，最下方（y≈8600）是评论区。行距 1500，各格内容控制在中心 ±500 内，避免漏进相邻镜头的页眉带。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_out
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, clock,
                               cross, face, hands_at, join, marker, rect, stick)

from .common import BOOK, episode

ACC = "#3A7D6B"
SQUARE_SHOT = 3                 # 场景 4：一天的时间块砸进日程表 + 小周举手

b = Board(size=(3900, 9400))

BLUE_FILL, ORANGE_FILL, GREEN_FILL = "#C9D9F2", "#F7D9B8", "#CFE9D8"


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = J() if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s.replace(" ", ""))) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def J():
    return len(b.shots) - 1


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    """一个场景：3 小节（12 拍，≈6.4 秒）第 0–8 拍画完、最后 4 拍停住；片头 2 小节第 0–6 拍画完；片尾 4 小节。"""
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """主角小周：火柴人 + 胸前工牌（挂绳 + 小方牌）。(x, y) 为脚底。"""
    hy = y - 290 * s
    return join(stick(x, y, s, arms), P((x - 14 * s, hy + 46 * s), (x + 30 * s, hy + 104 * s)),
                rect(x + 30 * s, hy + 128 * s, 36 * s, 44 * s, 4 * s))


def phone(x, y, w, h) -> skia.Path:
    """手机：圆角外框 + 顶部听筒 + 标题栏分隔线 + 底部横条。"""
    return join(rect(x, y, w, h, 46), P((x - 40, y - h / 2 + 30), (x + 40, y - h / 2 + 30)),
                P((x - w / 2 + 20, y - h / 2 + 150), (x + w / 2 - 20, y - h / 2 + 150)),
                P((x - 50, y + h / 2 - 32), (x + 50, y + h / 2 - 32)))


def paper(x, y, w, h) -> skia.Path:
    """一张纸：右上角折角。(x, y) 为中心。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2 - 50, y - h / 2), (x + w / 2, y - h / 2 + 50), (x + w / 2, y + h / 2),
                  (x - w / 2, y + h / 2), close=True),
                P((x + w / 2 - 50, y - h / 2), (x + w / 2 - 50, y - h / 2 + 50), (x + w / 2, y - h / 2 + 50)))


def calendar(x, y, w=240, h=220) -> skia.Path:
    return join(rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 52), (x + w / 2, y - h / 2 + 52)),
                P((x - w / 4, y - h / 2 - 22), (x - w / 4, y - h / 2 + 16)),
                P((x + w / 4, y - h / 2 - 22), (x + w / 4, y - h / 2 + 16)))


def grad_cap(x, y, s=1.0) -> skia.Path:
    """学士帽：(x, y) 为帽板中心。"""
    return join(P((x - 85 * s, y), (x, y - 32 * s), (x + 85 * s, y), (x, y + 32 * s), close=True),
                P((x - 45 * s, y + 18 * s), (x - 45 * s, y + 50 * s)), P((x + 45 * s, y + 18 * s), (x + 45 * s, y + 50 * s)),
                P((x + 85 * s, y), (x + 95 * s, y + 70 * s)))


def carton(x, y, w=500, h=260) -> skia.Path:
    """纸箱：箱身 + 两片张开的盖子 + 胶带线。(x, y) 为箱身中心。"""
    top = y - h / 2
    return join(rect(x, y, w, h, 8), P((x - w / 2, top), (x - w / 2 - 60, top - 90), (x - 30, top - 90), (x, top)),
                P((x + w / 2, top), (x + w / 2 + 60, top - 90), (x + 30, top - 90), (x, top)),
                P((x - 60, top), (x - 60, top + 50)), P((x + 60, top), (x + 60, top + 50)))


def door(x, y, w=420, h=700) -> skia.Path:
    """下班的门：门框 + 门板缝 + 门把手。(x, y) 为中心。"""
    return join(rect(x, y, w, h, 8), P((x - w / 2 + 40, y + h / 2), (x - w / 2 + 40, y - h / 2 + 40),
                                       (x + w / 2 - 40, y - h / 2 + 40), (x + w / 2 - 40, y + h / 2)),
                circle(x + w / 2 - 85, y + 20, 16))


def red_dot(c, x, y, r, num, alpha=1.0, sx=1.0, sy=1.0):
    """系列角色小红点：红色实心圆 + 白字数字 + 两条小短腿。"""
    if alpha <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(sx, sy)
    legs = join(P((-0.35 * r, 0.8 * r), (-0.45 * r, 1.45 * r), (-0.7 * r, 1.45 * r)),
                P((0.35 * r, 0.8 * r), (0.45 * r, 1.45 * r), (0.7 * r, 1.45 * r)))
    c.drawPath(legs, marker(RED, r * 0.16, alpha))
    K.dot(c, 0, 0, r, RED, alpha)
    K.text(c, num, 0, 0, r * (1.05 if len(num) < 3 else 0.72), "black", "#FFFFFF", alpha)
    c.restore()


def dot_anim(j, keys, r=46, num="1", gone=None, hop=0.3):
    """小红点按关键拍走位：keys=[(拍, x, y), …]，第一拍弹出，之后在每个关键拍前 hop 秒起跳、正好在该拍落地（落地压扁）；
    gone 为消失的拍（0.25 秒淡出）。"""

    def fn(c, k, t):
        ts = [b.t_of(j, kb) for kb, _, _ in keys]
        if t < ts[0]:
            return None
        x, y = keys[0][1], keys[0][2]
        sx = sy = 1.0
        f0 = clamp01((t - ts[0]) / 0.18)
        sc = (1 + 0.35 * math.sin(math.pi * f0)) * ease_out(clamp01(f0 * 2.5))
        sx = sy = sc
        for i in range(1, len(keys)):
            a, z = keys[i - 1], keys[i]
            if t >= ts[i]:
                x, y = z[1], z[2]
                f = clamp01((t - ts[i]) / 0.15)
                sx, sy = 1 + 0.35 * (1 - f), 1 - 0.3 * (1 - f)
            elif t >= ts[i] - hop:
                f = (t - (ts[i] - hop)) / hop
                x, y = a[1] + (z[1] - a[1]) * f, a[2] + (z[2] - a[2]) * f - math.sin(f * math.pi) * r * 2.2
                sx = sy = 1.0
        alpha = 1.0
        if gone is not None:
            alpha = 1 - clamp01((t - b.t_of(j, gone)) / 0.25)
        red_dot(c, x, y, r, num, alpha, sx, sy)
        return None

    return fn


def slam_block(j, kb, x, y, w, h, fill, edge, label, color=BLACK, size=58):
    """时间块砸进日程表：起拍时放大 1.4 倍、上移一截，2 帧内落定，落地两侧冒几道灰线。"""

    def fn(c, k, t):
        t0 = b.t_of(j, kb)
        if t < t0:
            return None
        f = ease_out(clamp01((t - t0) / 0.07))
        sc = 1 + 0.4 * (1 - f)
        yy = y - 70 * (1 - f)
        c.save()
        c.translate(x, yy)
        c.scale(sc, sc)
        K.rr(c, 0, 0, w, h - 6, 12, fill)
        K.rr_stroke(c, 0, 0, w, h - 6, 12, edge, 7)
        K.text(c, label, 0, 0, size, "hand", color)
        c.restore()
        d = t - t0
        if 0.05 < d < 0.35:
            a = 1 - (d - 0.05) / 0.3
            for sgn in (-1, 1):
                for dy in (-h * 0.25, h * 0.2):
                    x0 = x + sgn * (w / 2 + 20 + 60 * (d - 0.05))
                    K.seg(c, x0, y + dy, x0 + sgn * 50, y + dy - 12, "#9AA1AB", 6, a)
        return None

    return fn


def fly_card(j, kb, label, p0, p1, rot=0.0, w=210, h=92, size=50):
    """卡片从 p0 划弧飞进纸箱，正好在第 kb 拍落到 p1（之后斜插在箱口）。"""

    def fn(c, k, t):
        t1 = b.t_of(j, kb)
        t0 = t1 - 0.4
        if t < t0:
            return None
        f = clamp01((t - t0) / (t1 - t0))
        x = p0[0] + (p1[0] - p0[0]) * f
        y = p0[1] + (p1[1] - p0[1]) * f - math.sin(f * math.pi) * 160
        with K.at(c, x, y, rot * f):
            K.rr(c, 0, 0, w, h, 12, "#FFFFFF")
            K.rr_stroke(c, 0, 0, w, h, 12, ORANGE, 6)
            K.text(c, label, 0, 0, size, "hand", BLACK)
        return None

    return fn


# ---------------------------------------------------------------- 开局：一句原话（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

scene("在吗", "原话 · 每天都收到", (650, 800, 0.85), bars=2)
L(phone(520, 820, 520, 860), 0, 0.9, sfx="wood_high")
T("小李", 520, 520, 56, k0=1, k1=1.8, sfx="pop")
L(bubble(450, 690, 280, 110, -1), 2, 2.3, BLACK, 8, sfx="pop")
T("在吗？", 450, 690, 58, k0=2.2, k1=3.0)
L(bubble(500, 900, 380, 110, -1), 3, 3.3, BLACK, 8, sfx="pop")
T("有空聊聊？", 500, 900, 58, k0=3.2, k1=4.0)
L(zhou(1010, 1250, 0.8, "shrug"), 4, 4.8, BLUE, 9, sfx="wood_high")
L(face(1010, 1250, 0.8, "flat"), 4.8, 5.0, BLUE, 8)
b.custom(J(), 5, 5.4, dot_anim(J(), [(5, 775, 400)], 50, "1"), sfx="ding")

MSGS = [("在吗？", -1), ("在，啥事？", 1), ("想聊下方案", -1), ("现在？", 1), ("你啥时候有空", -1), ("明天吧", 1)]
scene("来回八条", "原话 · 来回拉扯", (1950, 800, 0.85))
for n, (s, side) in enumerate(MSGS):
    x, y = (1790 if side < 0 else 2120), 390 + n * 118
    w = max(230, len(s) * 48 + 90)
    L(bubble(x, y, w, 92, side), n, n + 0.25, BLUE if side > 0 else BLACK, 7, sfx="pop" if side < 0 else "wood_high")
    T(s, x, y, 48, BLUE if side > 0 else BLACK, k0=n + 0.2, k1=n + 1.0)
T("来回 8 条才约上", 1950, 1160, 72, RED, k0=6, k1=7.3, sfx="rim")
b.custom(J(), 7, 7.4, dot_anim(J(), [(7, 2330, 330)], 50, "8"), sfx="ding")

scene("一次说完", "改写 · 一条说完", (3250, 800, 0.85))
L(bubble(3250, 640, 880, 400, 1), 0, 0.9, BLUE, 9, sfx="wood_high")
T("周三 3 点或 4 点", 3250, 540, 62, k0=1, k1=2.8, sfx="pop")
T("聊 15 分钟", 3250, 650, 62, k0=3, k1=4.4, sfx="pop")
T("你选一个", 3250, 760, 62, BLUE, k0=5, k1=6.0, sfx="pop")
b.custom(J(), 6, 6.4, dot_anim(J(), [(6, 3800, 330), (7, 3690, 400), (8, 3830, 250)], 44, "1", gone=8.1))
L(check(2960, 1080, 60), 6, 6.6, GREEN, 12, sfx="ding")
T("一条就约上", 3330, 1080, 64, GREEN, k0=6.6, k1=7.9)
H(7, "rim", 0.8, "小红点撞上改写后的消息")
H(8, "shaker", 0.6, "小红点被挡回去")

# ---------------------------------------------------------------- drop：一天排成块（场景 4）

DAY = [("9:00 专注 · 写方案", 1770, 2005, BLUE_FILL, BLUE), ("11:00 回消息", 2005, 2123, ORANGE_FILL, ORANGE),
       ("12:00 午饭", 2123, 2299, GREEN_FILL, GREEN), ("13:30 专注 · 写方案", 2299, 2534, BLUE_FILL, BLUE),
       ("15:30 开会", 2534, 2652, ORANGE_FILL, ORANGE), ("16:30 杂事一起干", 2652, 2770, ORANGE_FILL, ORANGE)]
j_drop = scene("一天排成块", "改写 · 一天排成块", (3250, 2300, 0.75), shake=[0, 6], flashes=[0])
H(0, "cymbal", 0.5)
for n, (s, y0, y1, fill, edge) in enumerate(DAY):
    b.custom(j_drop, n, n + 0.2, slam_block(j_drop, n, 3380, (y0 + y1) / 2, 700, y1 - y0, fill, edge, s),
             sfx="kick" if n == 0 else "tom", gain=1.0 if n == 0 else 0.75)
b.custom(j_drop, 6, 6.2, slam_block(j_drop, 6, 3380, 2835, 700, 104, RED, RED, "17:30 下班", "#FFFFFF", 62),
         sfx="kick", gain=1.0)
L(zhou(2800, 2760, 0.85, "up"), 7, 7.8, BLUE, 9, sfx="pop")
L(face(2800, 2760, 0.85, "smile"), 7.8, 8.0, BLUE, 8)

# ---------------------------------------------------------------- 书里的办法：排时间、重排（场景 5–6）

scene("先把一天排好", "《深度工作》 · 书中做法", (1950, 2300, 0.85))
L(book(1690, 2250, 440, 290), 0, 0.9, sfx="wood_low")
T("《深度工作》", 1690, 2010, 64, GREEN, k0=1, k1=2.5, sfx="pop")
L(paper(2250, 2280, 380, 560), 3, 3.8, BLACK, 8, sfx="wood_high")
L(rect(2235, 2120, 290, 110, 10), 4, 4.7, BLUE, 9, sfx="pop")
L(rect(2235, 2250, 290, 80, 10), 5, 5.7, ORANGE, 9, sfx="pop")
L(rect(2235, 2400, 290, 150, 10), 6, 6.7, BLUE, 9, sfx="pop")
T("纸上排一天", 1950, 2700, 64, k0=7, k1=8.0, sfx="ding")

scene("乱了就重排", "书中做法 · 打乱就重排", (650, 2300, 0.85))
L(paper(500, 2290, 520, 780), 0, 0.9, BLACK, 8, sfx="wood_high")
L(rect(490, 2040, 400, 130, 10), 1, 1.3, BLUE, 9, sfx="pop")
T("写方案", 490, 2040, 58, BLUE, k0=1.2, k1=2.0)
L(rect(490, 2220, 400, 110, 10), 2, 2.3, ORANGE, 9, sfx="pop")
T("回消息", 490, 2220, 58, ORANGE, k0=2.2, k1=3.0)
b.custom(J(), 3, 3.4, dot_anim(J(), [(3, 680, 2030)], 40, "1"), sfx="ding")
b.erase(J(), 4, 4.8, 500, 2040, 500, 160)
H(4, "shaker", 0.8, "擦掉被打乱的一块")
L(arrow((720, 2050), (720, 2520), -0.3, 40), 5, 5.8, GREEN, 9, sfx="pop")
L(rect(490, 2540, 400, 130, 10), 6, 6.3, BLUE, 9, sfx="wood_high")
T("写方案", 490, 2540, 58, BLUE, k0=6.2, k1=7.0)
T("心里有数", 1010, 2560, 60, GREEN, k0=7, k1=8.0, sfx="ding")

# ---------------------------------------------------------------- 原话：顺手弄一下 → 先问新人要学多久（场景 7–9）

scene("新人多久学会", "原话 · 顺手弄一下", (650, 3800, 0.85))
L(bubble(650, 3400, 620, 130, -1), 0, 0.4, BLACK, 8, sfx="wood_high")
T("这个你顺手弄一下", 650, 3400, 54, k0=0.4, k1=2.4)
L(join(stick(370, 4260, 0.75, "down"), grad_cap(370, 4010, 0.8)), 3, 3.8, BLACK, 9, sfx="wood_high")
L(face(370, 4260, 0.75, "smile"), 3.8, 4.0, BLACK, 8)
T("新人要学多久？", 780, 3620, 60, RED, k0=4, k1=5.6, sfx="tom")
L(calendar(780, 3990), 6, 6.3, BLACK, 8, sfx="pop")
T("1 个月", 780, 4020, 50, k0=6.2, k1=7.0)
L(calendar(1050, 3990), 7, 7.3, BLACK, 8, sfx="pop")
T("6 个月", 1050, 4020, 50, k0=7.2, k1=8.0)

scene("浮活打包", "书中做法 · 浮活打包", (1950, 3800, 0.85))
T("上手越快，越浅", 1950, 3400, 64, k0=0, k1=1.75, sfx="pop")
L(carton(2150, 3960, 500, 260), 2, 2.8, BLACK, 9, sfx="wood_high")
T("杂事箱", 2150, 3990, 62, ORANGE, k0=3, k1=3.8, sfx="pop")
for n, (s, p1, rot) in enumerate((("填表", (1985, 3790), -10), ("报销", (2150, 3770), 4), ("群通知", (2315, 3790), 10))):
    b.custom(J(), 3.6 + n, 4 + n, fly_card(J(), 4 + n, s, (1620, 3640), p1, rot, w=160, h=86, size=46))
    H(4 + n, "tom" if n < 2 else "kick", 0.75, f"卡片落箱：{s}")
T("攒一块，一起干", 1950, 4230, 60, GREEN, k0=7, k1=8.0, sfx="ding")

scene("跟上级对一下", "书中做法 · 跟上级对一下", (3250, 3800, 0.85))
L(zhou(2900, 4260, 0.75, "point"), 0, 0.8, BLUE, 9, sfx="wood_high")
L(face(2900, 4260, 0.75, "smile"), 0.8, 1.0, BLUE, 8)
L(stick(3640, 4260, 0.8, "down", tie=True), 1, 1.8, BLACK, 9, sfx="wood_high")
L(face(3640, 4260, 0.8, "flat"), 1.8, 2.0, BLACK, 8)
L(bubble(3170, 3480, 620, 240, -1), 2, 2.6, BLUE, 8, sfx="pop")
T("这周杂事占三成", 3170, 3430, 56, k0=3, k1=4.75, sfx="pop")
T("您看行吗？", 3170, 3540, 56, k0=5, k1=6.25, sfx="pop")
L(bubble(3640, 3830, 200, 100, 1), 7, 7.3, BLACK, 8, sfx="ding")
T("可以", 3640, 3830, 56, GREEN, k0=7.2, k1=8.0)

# ---------------------------------------------------------------- 先定下班点；原话“马上看”→“周四给你”；不回也行（场景 10–12）

scene("先定下班点", "书中做法 · 先定下班点", (3250, 5300, 0.85))
L(clock(3530, 4980, 160), 0, 0.8, BLACK, 9, sfx="wood_high")
L(hands_at(3530, 4980, 160, 17, 30), 0.8, 1.0, RED, 10)
T("17:30 下班", 3530, 5230, 60, RED, k0=1, k1=2.5, sfx="pop")
T("倒推", 3170, 4870, 56, k0=3, k1=3.8, sfx="pop")
L(arrow((3360, 5040), (3010, 5040), 0.2, 40), 4, 4.8, GREEN, 9, sfx="wood_high")
T("写方案", 2880, 5180, 56, k0=5, k1=5.8, sfx="pop")
T("改报告", 2880, 5330, 56, k0=6, k1=6.8, sfx="pop")
T("新需求", 2880, 5480, 56, k0=7, k1=7.8, sfx="rim")
L(arrow((2990, 5480), (3100, 5480), 0, 26), 7.4, 7.6, BLUE, 8)
T("下周排", 3220, 5480, 56, BLUE, k0=7.5, k1=8.0)

DOTS = [(1720, 4870), (1860, 4850), (2000, 4870)]
scene("说个时间", "原话 → 改写 · 说个时间", (1950, 5300, 0.85))
L(bubble(1900, 4990, 520, 140, 1), 0, 0.4, BLACK, 8, sfx="wood_high")
T("收到，马上看", 1900, 4990, 58, k0=0.4, k1=2.0)
L(cross(2290, 4990, 44), 2, 2.6, RED, 11, sfx="rim")
for n, (x, y) in enumerate(DOTS):
    b.custom(J(), 3, 3.4, dot_anim(J(), [(3, x, y), (7, x - 60, 5200), (8, x - 260, 4980)], 34, str(n + 1), gone=8.1),
             sfx="ding" if n == 0 else None)
L(bubble(1900, 5340, 560, 140, 1), 4, 4.4, BLUE, 8, sfx="pop")
T("收到，周四给你", 1900, 5340, 58, BLUE, k0=4.3, k1=5.9)
L(check(2310, 5340, 50), 6, 6.6, GREEN, 12, sfx="ding")
H(7, "rim", 0.8, "小红点撞上改写后的消息")
H(8, "shaker", 0.6, "小红点被挡回去")


scene("有的不用回", "书中做法 · 不回也行", (650, 5300, 0.85))
L(phone(480, 5300, 600, 780), 0, 0.9, BLACK, 9, sfx="wood_high")
T("工作群", 480, 5010, 56, k0=1, k1=1.8, sfx="pop")
L(bubble(450, 5220, 470, 120, -1), 2, 2.3, BLACK, 8, sfx="pop")
T("周五团建照片", 450, 5220, 50, k0=2.2, k1=3.7)
L(bubble(450, 5440, 470, 120, -1), 4, 4.3, BLACK, 8, sfx="pop")
T("大家辛苦了", 450, 5440, 50, k0=4.2, k1=5.5)
L(check(880, 5440, 50), 6, 6.6, GREEN, 12, sfx="wood_high")
T("不回也行", 1000, 5590, 60, GREEN, k0=7, k1=8.0, sfx="ding")

# ---------------------------------------------------------------- 收全系列（场景 13）：小周伸懒腰走向下班的门，小红点被挡在外头

WALL = (6800, 7100, 7400)
scene("准点下班", "收尾 · 准点下班", (1950, 7150, 0.5))
L(door(2720, 7200, 420, 700), 0, 0.9, BLACK, 14, sfx="wood_high")
T("17:30", 2720, 6720, 110, RED, k0=1, k1=2.25, sfx="pop")
L(zhou(1950, 7700, 1.4, "up"), 2, 2.9, BLUE, 14, sfx="wood_high")
L(face(1950, 7700, 1.4, "smile"), 2.9, 3.1, BLUE, 12)
L(join(*[rect(1260, y, 300, 150, 30) for y in WALL]), 4, 4.6, BLUE, 12, sfx="pop")
L(join(*[check(1260, y, 45) for y in WALL]), 4.6, 5.0, GREEN, 12)
for n, y in enumerate(WALL):
    b.custom(J(), 4.4, 5, dot_anim(J(), [(4.4, 800, y - 40), (5, 1060, y), (6, 840, y + 160)], 70, ("9", "99", "99+")[n],
                                   gone=6.2))
H(5, "rim", 0.9, "小红点撞墙")
H(6, "shaker", 0.7, "小红点被挡回去")
T("准点下班", 1950, 6440, 130, GREEN, k0=7, k1=8.0, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：第 0 拍拉远看全板，第 4 拍推到评论区

j_end = scene("这一季讲完了", "评论区见", (1950, 4700, 0.105), bars=4)
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
b.move(j_end, 4, (1950, 8600, 0.85), dur=1.1)
H(4, "ding")
T("这十讲，你最想先试哪个？", 1950, 8330, 64, RED, k0=6, k1=8.75, sfx="pop")
T("这一季讲完了", 1950, 8540, 76, k0=9, k1=10.5, sfx="wood_high")
T("谢谢你一路看完", 1950, 8690, 58, k0=11, k1=12.75, sfx="pop")
L(zhou(1700, 9040, 0.55, "up"), 13, 13.8, BLUE, 8, sfx="wood_high")
L(face(1700, 9040, 0.55, "smile"), 13.8, 14.0, BLUE, 7)
b.custom(j_end, 14, 14.4, dot_anim(j_end, [(14, 2200, 8950)], 46, "0"), sfx="ding")
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "shallow", "少干浮活", "活一件没少，怎么准点下班？", ACC, b.shots,
                 [f"{BOOK}第二部分 准则4“摒弃浮浅”：一天的每一分钟都要做好计划 / 定量分析每一项活动的深度 / "
                  "向老板申请浮浅工作预算 / 下午5点半之前结束工作 / 变得不容易联系到（转述）",
                  "中译本：宋伟译，江西人民出版社 · 后浪 2017；民主与建设出版社 · 后浪 2023"],
                 "活一件没少|怎么【准点下班】", SQUARE_SHOT,
                 ["书中观点均为转述（准则4“摒弃浮浅”）：在纸上把一天分成时间块，被打乱就重排，目的是对时间心里有数"
                  "（“一天的每一分钟都要做好计划”）；用“培训一个刚毕业、没受过专门训练的聪明人要几个月才能上手”来衡量一件事"
                  "有多浅，月数越少越浅（“定量分析每一项活动的深度”）；跟上级商量一个浮浅工作的占比（“向老板申请浮浅工作预算”，"
                  "书中给的具体比例未核实，上屏“三成”为示意）；先定下班时间、倒推哪些事能接、哪些要推掉（“下午5点半之前结束工作”，"
                  "书中称固定日程生产力）；让发消息的人多花点功夫、回复时一次把流程说完（过程中心式回复）、有些消息可以不回"
                  "（“变得不容易联系到”）。出处：卡尔·纽波特《深度工作：如何有效使用每一点脑力》，宋伟译，"
                  "江西人民出版社 · 后浪 2017（再版：民主与建设出版社 · 后浪 2023）；原书 Deep Work, Grand Central Publishing, 2016。"
                  "正文页码未核实。",
                  "所有原话与改写（“在吗？有空聊聊？”“这个你顺手弄一下”“收到，马上看”→“周四给你”、约时间的消息、"
                  "跟上级说的话）均为示意，不是书中原话；“来回 8 条”、日程表各时间块、“1 个月 / 6 个月”、“三成”、"
                  "群消息内容均为示意，不是数据；人物“小周”“小李”为虚构，不指向任何具体公司或个人。",
                  "浮活装进“杂事箱”一起干、在纸上排一天、群消息“不回也行”等做法为据书中思路整理的建议。",
                  "片尾为全系列收尾，这一季（10 讲）到此讲完。"],
                 tags="#准点下班")
    return b.attach(ep)
