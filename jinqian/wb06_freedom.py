"""06 钱买自由（白板手绘版）：钱最大的用处，是买回时间。

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（E 自测清单）：开局一张清单纸『你能做到吗』，四个空框，观众边看边对照打勾
（歇三个月不慌 / 生病请假不慌 / 不想要的加班能推掉 / 周末能不看工作群）→
drop：一只大闹钟从老板桌上被拎回小王手里，指针归他转 → 亮书《金钱心理学》第 7 章“自由” →
书中观点（转述）：钱给的最高回报，是能自己安排时间；书中提到坎贝尔的研究：“觉得能自己做主”比收入更能
预测幸福感；书中提到皮勒默访谈很多老人，他们看重朋友、家人、陪孩子，没人说该更拼命；很多工作下了班脑子还在上班 →
按勾数解读（打勾少：先攒几个月生活费；打勾多：用钱换时间，如请人打扫、搬近点少通勤）→
做法：涨薪别全换成东西，分一路给时间 → 小王和小猪罐坐在长椅上，闹钟在他手里 → 拉远看全板 → 评论区。
书中观点为转述（Morgan Housel, The Psychology of Money, Harriman House, 2020；中译本《金钱心理学》，
李青宗译，民主与建设出版社 / 后浪 2023，第 7 章“自由”）；自测清单、勾数解读与例子为示意 / 据书中思路整理。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               desk, doc, face, hands_at, join, marker, partial, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .common import BOOK, episode

ACC = "#3A7CA5"                 # 本讲主色：钢蓝（闹钟 / 时间）
SQUARE_SHOT = 3                 # 场景 4：闹钟从老板桌被拎回小王手里（人物 + 核心示意）

b = Board(size=(3600, 9000))
Z = 0.85
XL, XR = 950, 2650              # 左右两列
R1, R2, R3, R4, R5, R6 = 1000, 2450, 3900, 5350, 6800, 8250


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, gain=0.8):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx, gain=gain)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(fn, k0, k1, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


def _stroke(c, path, color, width):
    c.drawPath(path, marker(color, width))
    c.drawPath(path, K.paint(color, 0.22, width * 0.45, blur=1.2))


# ---------------------------------------------------------------- 本讲画法

def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def arc(x, y, w, h, start, sweep) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), start, sweep)
    return p


def pig(x, y, s=1.0, mood="smile") -> skia.Path:
    """系列角色小猪罐（正面）：(x, y) 为身体中心。mood：smile / sad / sweat / shock，只改嘴和汗滴。"""
    parts = [oval(x, y, 250 * s, 210 * s),
             P((x - 95 * s, y - 68 * s), (x - 108 * s, y - 138 * s), (x - 45 * s, y - 98 * s)),
             P((x + 95 * s, y - 68 * s), (x + 108 * s, y - 138 * s), (x + 45 * s, y - 98 * s)),
             P((x - 28 * s, y - 78 * s), (x + 28 * s, y - 78 * s)),                     # 背上的投币口
             circle(x - 45 * s, y - 32 * s, 6 * s), circle(x + 45 * s, y - 32 * s, 6 * s),
             oval(x, y + 10 * s, 84 * s, 54 * s), circle(x - 14 * s, y + 10 * s, 5 * s), circle(x + 14 * s, y + 10 * s, 5 * s),
             P((x - 60 * s, y + 100 * s), (x - 60 * s, y + 128 * s)), P((x + 60 * s, y + 100 * s), (x + 60 * s, y + 128 * s))]
    if mood == "smile":
        parts.append(arc(x, y + 52 * s, 60 * s, 34 * s, 20, 140))
    elif mood == "shock":
        parts.append(circle(x, y + 66 * s, 11 * s))
    else:
        parts.append(arc(x, y + 72 * s, 50 * s, 28 * s, 200, 140))
    if mood == "sweat":
        d = skia.Path()
        d.moveTo(x + 125 * s, y - 120 * s)
        d.quadTo(x + 150 * s, y - 80 * s, x + 125 * s, y - 70 * s)
        d.quadTo(x + 100 * s, y - 80 * s, x + 125 * s, y - 120 * s)
        parts.append(d)
    return join(*parts)


def coin(x, y, r=34) -> skia.Path:
    return join(circle(x, y, r), P((x, y - r * 0.5), (x, y + r * 0.5)))


def coin_stack(x, y, n=3) -> skia.Path:
    """一摞硬币（侧看）：(x, y) 为最底下一枚的中心。"""
    parts = []
    for i in range(n):
        yy = y - i * 44
        parts += [oval(x, yy, 170, 54), P((x - 85, yy), (x - 85, yy + 16)), P((x + 85, yy), (x + 85, yy + 16))]
    return join(*parts)


def alarm(x, y, r) -> skia.Path:
    """闹钟（不含指针）：钟面 + 两只铃铛 + 两只脚。"""
    return join(clock(x, y, r), arc(x - r * 0.62, y - r * 0.86, r * 0.6, r * 0.6, 180, 180),
                arc(x + r * 0.62, y - r * 0.86, r * 0.6, r * 0.6, 180, 180),
                P((x - r * 0.62 - r * 0.3, y - r * 0.86), (x - r * 0.62 + r * 0.3, y - r * 0.86)),
                P((x + r * 0.62 - r * 0.3, y - r * 0.86), (x + r * 0.62 + r * 0.3, y - r * 0.86)),
                P((x - r * 0.55, y + r * 0.85), (x - r * 0.75, y + r * 1.15)),
                P((x + r * 0.55, y + r * 0.85), (x + r * 0.75, y + r * 1.15)))


def hands_ang(x, y, r, a_min) -> skia.Path:
    """按分针角度（度，0 = 十二点）画两根指针，时针随分针走。"""
    am = math.radians(a_min - 90)
    ah = math.radians(a_min / 12 + 300 - 90)
    return join(P((x, y), (x + math.cos(am) * r * 0.75, y + math.sin(am) * r * 0.75)),
                P((x, y), (x + math.cos(ah) * r * 0.5, y + math.sin(ah) * r * 0.5)))


def rays(x, y, r) -> skia.Path:
    parts = []
    for a in (-150, -110, -70, -30, 10, 170):
        t = math.radians(a)
        parts.append(P((x + math.cos(t) * r, y + math.sin(t) * r), (x + math.cos(t) * r * 1.3, y + math.sin(t) * r * 1.3)))
    return join(*parts)


def paper(x, y, w, h) -> skia.Path:
    """清单纸：右上角折一角。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2 - 70, y - h / 2), (x + w / 2, y - h / 2 + 70), (x + w / 2, y + h / 2),
                  (x - w / 2, y + h / 2), close=True),
                P((x + w / 2 - 70, y - h / 2), (x + w / 2 - 70, y - h / 2 + 70), (x + w / 2, y - h / 2 + 70)))


def oldman(x, y, s=0.6) -> skia.Path:
    """老人火柴人：拄拐杖、微微驼背。(x, y) 为脚底。"""
    hy = y - 280 * s
    return join(circle(x + 12 * s, hy, 45 * s), P((x + 6 * s, hy + 45 * s), (x - 8 * s, hy + 110 * s), (x, y - 120 * s)),
                P((x - 55 * s, y), (x, y - 120 * s), (x + 50 * s, y)),
                P((x - 60 * s, hy + 170 * s), (x - 4 * s, hy + 85 * s), (x + 80 * s, hy + 150 * s)),
                P((x + 80 * s, hy + 150 * s), (x + 95 * s, y)), P((x + 60 * s, hy + 150 * s), (x + 100 * s, hy + 150 * s)))


def bed(x, y, w=700) -> skia.Path:
    """床：(x, y) 为床垫上沿中点。"""
    return join(P((x - w / 2, y), (x + w / 2, y), (x + w / 2, y + 70), (x - w / 2, y + 70), close=True),
                P((x - w / 2, y + 140), (x - w / 2, y - 150)), P((x - w / 2 + 20, y - 150), (x - w / 2 + 20, y)),
                P((x + w / 2, y + 70), (x + w / 2, y + 140)))


def lying(x, y, s=1.0) -> skia.Path:
    """躺在床上的小人（盖着被子）：(x, y) 为床垫上沿中点。"""
    hx, hy = x - 230 * s, y - 45 * s
    blanket = skia.Path()
    blanket.moveTo(x - 160 * s, y)
    blanket.quadTo(x - 150 * s, y - 95 * s, x - 60 * s, y - 85 * s)
    blanket.lineTo(x + 230 * s, y - 70 * s)
    blanket.quadTo(x + 300 * s, y - 40 * s, x + 300 * s, y)
    return join(circle(hx, hy, 42 * s), P((hx - 30 * s, hy + 42 * s), (hx + 50 * s, hy + 42 * s)), blanket)


def msg(x, y, w=250, h=96) -> skia.Path:
    """工作群消息框（带小尾巴）。"""
    return join(rect(x, y, w, h, 20), P((x - w / 2 + 30, y + h / 2), (x - w / 2 + 10, y + h / 2 + 34),
                                        (x - w / 2 + 60, y + h / 2)))


def bag(x, y, s=1.0) -> skia.Path:
    """购物袋：(x, y) 为袋身中心。"""
    return join(P((x - 70 * s, y - 60 * s), (x - 85 * s, y + 80 * s), (x + 85 * s, y + 80 * s), (x + 70 * s, y - 60 * s),
                  close=True), arc(x, y - 60 * s, 80 * s, 90 * s, 180, 180))


def bench(x, y, w=620) -> skia.Path:
    """长椅：(x, y) 为椅面中点。"""
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2, y - 130), (x + w / 2, y - 130)),
                P((x - w / 2 + 30, y - 130), (x - w / 2 + 30, y)), P((x + w / 2 - 30, y - 130), (x + w / 2 - 30, y)),
                P((x - w / 2 + 40, y), (x - w / 2 + 40, y + 120)), P((x + w / 2 - 40, y), (x + w / 2 - 40, y + 120)))


def sitting(x, y, s=1.0) -> skia.Path:
    """坐着的小人（面朝右，双手捧在膝上）：(x, y) 为臀部（椅面）。"""
    sh = (x, y - 150 * s)
    hy = y - 230 * s
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y)), P((x, y), (x + 110 * s, y), (x + 110 * s, y + 120 * s)),
                P((x - 10 * s, y + 6 * s), (x + 100 * s, y + 12 * s), (x + 100 * s, y + 120 * s)),
                P(sh, (x + 60 * s, y - 80 * s), (x + 110 * s, y - 70 * s)),
                arc(x, hy + 5 * s, 40 * s, 28 * s, 20, 140), circle(x - 15 * s, hy - 8 * s, 3 * s),
                circle(x + 15 * s, hy - 8 * s, 3 * s))


def sun(x, y, r=70) -> skia.Path:
    parts = [circle(x, y, r)]
    for i in range(8):
        a = i / 8 * 2 * math.pi
        parts.append(P((x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3), (x + math.cos(a) * r * 1.65,
                                                                                  y + math.sin(a) * r * 1.65)))
    return join(*parts)


def comment_box(x, y, w, h) -> skia.Path:
    return join(rect(x, y, w, h, 30), P((x - w / 2 + 80, y + h / 2), (x - w / 2 + 60, y + h / 2 + 70),
                                        (x - w / 2 + 160, y + h / 2)))


# ---------------------------------------------------------------- 开局：自测清单（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

BOX_X = 560
ROWS = [760, 960, 1160, 1360]
ITEMS = ["歇三个月不慌", "生病请假不慌", "不想要的加班能推掉", "周末能不看工作群"]

scene("先做个小测试", "小测试", (XL, 990, 0.75), bars=2)
L(paper(XL, 965, 1000, 1030), 0, 0.9, sfx="wood_high")
T("你能做到吗", XL, 575, 84, ACC, k0=1, k1=2.25, sfx="pop")
for n, yy in enumerate(ROWS):
    L(rect(BOX_X, yy, 100, 100, 10), 3 + n * 0.5, 3.45 + n * 0.5, BLACK, 9, sfx="wood_low" if n in (0, 2) else None)
L(underline(XL - 210, XL + 210, 630, 10, 36), 5, 5.8, ACC, 7, sfx="ding")

scene("不想干了，能歇一阵？", "小测试 · 第一、二题", (XL, 980, Z))
T(ITEMS[0], 1060, ROWS[0], 62, k0=0, sfx="pop")
T("？", BOX_X, ROWS[0] + 22, 76, BLUE, k0=2, k1=2.8, sfx="wood_high")
T(ITEMS[1], 1060, ROWS[1], 62, k0=3, sfx="pop")
T("？", BOX_X, ROWS[1] + 22, 76, BLUE, k0=5, k1=5.8, sfx="wood_high")
L(underline(1200, 1330, ROWS[0] + 42, 8, 30), 6, 6.7, RED, 7, sfx="ding")
L(underline(1200, 1330, ROWS[1] + 42, 8, 30), 7, 7.7, RED, 7)

scene("讨厌的活，能说不？", "小测试 · 第三、四题", (1000, 1000, Z))
T(ITEMS[2], 1060, ROWS[2], 60, k0=0, sfx="pop")
T("？", BOX_X, ROWS[2] + 22, 76, BLUE, k0=3, k1=3.8, sfx="wood_high")
T(ITEMS[3], 1060, ROWS[3], 60, k0=4, sfx="pop")
T("？", BOX_X, ROWS[3] + 22, 76, BLUE, k0=6, k1=6.8, sfx="wood_high")
L(oval(BOX_X, 1060, 170, 780), 7, 7.9, RED, 8, sfx="ding")

# ---------------------------------------------------------------- drop（场景 4）：闹钟被拎回小王手里

DESK = (2230, 1180)
CK0 = (2120, 1180 - 98, 80)             # 闹钟在老板桌上 (x, y, r)
XW = (3010, 1360, 0.85)                 # 小王：脚底与缩放
CK1 = (3010, 1360 - 290 * 0.85 - 150, 112)   # 举过头顶


def clock_fn(j):
    """闹钟：第 3–4 拍从老板桌飞到小王手里（越飞越大），第 5–6.5 拍指针转起来，最后停在小王定的时间。"""

    def fn(c, k, t):
        t_fly0, t_fly1 = b.t_of(j, 3), b.t_of(j, 4)
        t_spin0, t_spin1 = b.t_of(j, 5), b.t_of(j, 6.5)
        f = ease_in_out(clamp01((t - t_fly0) / (t_fly1 - t_fly0)))
        x = lerp(CK0[0], CK1[0], f)
        y = lerp(CK0[1], CK1[1], f) - 260 * 4 * f * (1 - f)
        r = lerp(CK0[2], CK1[2], f)
        spin = ease_out(clamp01((t - t_spin0) / (t_spin1 - t_spin0)))
        a = 50 + spin * (720 + 250)                      # 停在约 10:10 的位置
        body = alarm(x, y, r)
        if k < 1:                                        # 刚出现时随笔画出
            part, tip = partial(join(body, hands_ang(x, y, r, a)), k)
            _stroke(c, part, ACC, 9)
            return tip
        _stroke(c, body, ACC, 9)
        _stroke(c, hands_ang(x, y, r, a), RED, 9)
        if t < t_fly1:
            return (x, y - r * 1.2)
        return None

    return fn


scene("钱能买回时间", "钱能买回时间", (2650, 950, 0.75), shake=[0], flashes=[0])
T("时间，拎回来！", 2650, 480, 100, RED, k0=0, k1=1.0, sfx="kick")
L(join(desk(*DESK, 440), stick(2410, 1290, 0.7, "down", tie=True), face(2410, 1290, 0.7, "flat")), 1, 1.8,
  sfx="wood_low")
C(clock_fn(J()), 1.8, 2.0)
L(join(stick(XW[0], XW[1], XW[2], "up"), face(XW[0], XW[1], XW[2], "smile")), 2, 2.8, BLUE, 10, sfx="wood_high")
H(3, "tom")
H(4, "ding")
H(5, "shaker")
T("老板桌", DESK[0], DESK[1] + 170, 52, k0=6, k1=6.8, sfx="pop")
L(rays(*CK1), 7, 7.6, RED, 7, sfx="ding")
T("小王", XW[0], XW[1] + 60, 54, BLUE, k0=7.6, k1=8.0)

# ---------------------------------------------------------------- 书中观点（场景 5–9）

scene("翻开这本书", "金钱心理学 · 书中观点", (XR, R2, Z))
L(book(2400, 2470, 420, 280), 0, 0.9, sfx="wood_low")
T("金钱心理学", 2400, 2250, 72, GREEN, k0=1, k1=2.25, sfx="pop")
T("摩根 · 豪泽尔", 2400, 2720, 54, k0=3, k1=4.5, sfx="pop")
T("第 7 章", 2990, 2250, 60, BLUE, k0=5, k1=5.8, sfx="pop")
T("自由", 2990, 2370, 96, RED, k0=5.8, k1=6.4)
L(pig(2990, 2640, 0.85, "smile"), 7, 7.9, ACC, 9, sfx="wood_high")

scene("掌控时间，最值钱", "书中观点 · 第 7 章", (XL, R2, Z))
L(rect(XL, 2230, 1040, 290, 24), 0, 0.9, BLUE, 8, sfx="wood_low")
T("钱给的最高回报", XL, 2170, 64, k0=1, k1=2.75, sfx="pop")
T("能自己安排时间", XL, 2290, 80, RED, k0=3, k1=4.75, sfx="pop")
L(join(clock(660, 2700, 150), hands_at(660, 2700, 150, 10, 10)), 5, 5.9, ACC, 9, sfx="wood_high")
L(join(stick(1180, 2920, 0.75, "point"), face(1180, 2920, 0.75, "smile")), 6, 6.9, BLUE, 9, sfx="pop")
T("我定", 1180, 2560, 60, BLUE, k0=7, k1=7.8, sfx="ding")

BASE = 4230
scene("比收入更让人开心", "书中提到 · 坎贝尔的研究", (XL, R3, Z))
T("坎贝尔的研究：谁更让人开心", XL, 3460, 54, BLUE, k0=0, k1=2.0, sfx="pop")
L(P((380, BASE), (1520, BASE)), 2, 2.8, BLACK, 9, sfx="wood_low")
L(P((560, BASE), (560, BASE - 260), (780, BASE - 260), (780, BASE)), 3, 3.8, BLACK, 10, sfx="wood_high")
T("收入", 670, BASE + 80, 60, k0=3.8, k1=4.6)
L(P((1060, BASE), (1060, BASE - 560), (1280, BASE - 560), (1280, BASE)), 5, 5.8, GREEN, 10, sfx="wood_high")
T("能自己做主", 1170, BASE + 80, 60, GREEN, k0=5.8, k1=7.05)
L(rays(1170, BASE - 620, 70), 7, 7.5, RED, 7, sfx="ding")
T("（示意）", 1430, 3600, 48, k0=7.5, k1=8.0)

scene("问了很多老人", "书中提到 · 皮勒默的访谈", (XR, R3, Z))
T("皮勒默：访谈很多老人", XR, 3460, 58, BLUE, k0=0, k1=2.0, sfx="pop")
L(join(oldman(2330, 4380), oldman(2650, 4380), oldman(2970, 4380)), 2, 2.9, BLACK, 9, sfx="wood_high")
L(bubble(XR, 3800, 980, 300, -0.2), 3, 3.8, BLACK, 8, sfx="wood_low")
T("更拼命？", XR, 3730, 64, k0=4, k1=4.8, sfx="pop")
L(cross(XR, 3720, 70), 5, 5.6, RED, 11, sfx="rim")
T("朋友 · 家人 · 陪孩子", XR, 3870, 64, GREEN, k0=6, k1=8.0, sfx="ding")

BED = (2650, 5560)
scene("下班了，脑子还在上班", "书中观点 · 下班不下线", (XR, R4, Z))
L(join(bed(*BED, 720), lying(*BED, 1.0)), 0, 0.9, BLACK, 9, sfx="wood_low")
T("23:40", 2230, 4960, 72, RED, k0=1, k1=1.8, sfx="pop")
for n, (mx, my, s) in enumerate(((2470, 5220, "改个方案"), (2780, 5060, "在吗？"), (3060, 5240, "明早要"))):
    k = (2, 3.5, 5)[n]
    L(msg(mx, my), k, k + 0.5, BLACK, 7, sfx="pop" if n != 1 else None)
    T(s, mx, my + 16, 50, k0=k + 0.5, k1=k + 1.3)
T("睡不着", 2180, 5250, 56, BLUE, k0=7, k1=7.8, sfx="rim")

# ---------------------------------------------------------------- 按勾数解读（场景 10–11）

PIG = (XL, 5330, 1.3)


def pig_fn(j):
    """小猪罐：第 2 拍画出（冒汗），第 3、4、5 拍各进一枚硬币，每进一枚胖一圈；第三枚进去后笑了。"""

    def fn(c, k, t):
        n = sum(t >= b.t_of(j, kk) for kk in (3, 4, 5))
        s = PIG[2] * (1 + 0.07 * n)
        path = pig(PIG[0], PIG[1], s, "smile" if n >= 3 else "sweat")
        if k < 1:
            part, tip = partial(path, k)
            _stroke(c, part, ACC, 9)
            return tip
        _stroke(c, path, ACC, 9)
        return None

    return fn


def drop_fn(x, y0, y1):
    def fn(c, k, t):
        if k >= 1:
            return None
        y = lerp(y0, y1, k * k)
        _stroke(c, coin(x, y, 34), GREEN, 7)
        return None

    return fn


scene("打勾少，先攒应急钱", "按勾数看 · 打勾少", (XL, R4, Z))
T("0–1 个勾", XL, 4920, 84, RED, k0=0, k1=1.0, sfx="pop")
C(pig_fn(J()), 1, 1.9, sfx="wood_high")
for n in range(3):
    C(drop_fn(PIG[0], 5010, PIG[1] - 110 * PIG[2]), 2.5 + n, 3.0 + n)
    H(3 + n, "ding")
T("先攒几个月生活费", XL, 5760, 66, GREEN, k0=6, k1=8.0, sfx="pop")

scene("打勾多，用钱换时间", "按勾数看 · 打勾多", (XL, R5, Z))
T("3–4 个勾", XL, 6370, 84, GREEN, k0=0, k1=1.25, sfx="pop")
L(coin_stack(640, 6760, 3), 2, 2.9, GREEN, 9, sfx="wood_high")
L(arrow((800, 6700), (1060, 6700), 0.0, 40), 3, 3.7, BLACK, 9, sfx="pop")
L(join(alarm(1260, 6690, 120), hands_ang(1260, 6690, 120, 50)), 4, 4.9, ACC, 9, sfx="wood_high")
T("请人打扫一次", XL, 7000, 58, k0=5, k1=6.4, sfx="pop")
T("搬近点，少通勤", XL, 7120, 58, k0=6.5, k1=8.0)

# ---------------------------------------------------------------- 做法（场景 12–13）

scene("涨薪别全换成东西", "做法 · 涨薪分两路", (XR, R5, Z))
L(doc(2650, 6450, 220, 260, 4), 0, 0.9, BLACK, 9, sfx="wood_low")
T("涨薪了", 2950, 6420, 64, RED, k0=1, k1=1.8, sfx="pop")
L(arrow((2580, 6600), (2280, 6880), -0.1, 40), 2, 2.8, BLACK, 6, sfx="wood_high")
L(bag(2230, 7020, 0.9), 3, 3.8, BLACK, 8, sfx="pop")
T("东西", 2230, 7180, 58, k0=3.8, k1=4.6)
L(arrow((2720, 6600), (3020, 6880), 0.1, 56), 5, 5.8, GREEN, 18, sfx="wood_high")
L(join(clock(3040, 7010, 105), hands_at(3040, 7010, 105, 10, 10)), 6, 6.7, ACC, 9, sfx="ding")
T("时间", 3040, 7180, 64, GREEN, k0=6.7, k1=7.4)
L(check(3215, 6900, 40), 7.4, 7.9, GREEN, 9)

BEN = (2600, 8420)
scene("把时间还给自己", "做法 · 时间归自己", (XR, R6, Z))
L(bench(*BEN, 700), 0, 0.9, BLACK, 9, sfx="wood_low")
L(sitting(2380, BEN[1], 0.95), 1, 1.9, BLUE, 9, sfx="wood_high")
L(join(alarm(2510, BEN[1] - 120, 52), hands_ang(2510, BEN[1] - 120, 52, 50)), 2, 2.8, ACC, 7, sfx="ding")
L(pig(2830, BEN[1] - 132, 0.75, "smile"), 3, 3.9, ACC, 9, sfx="pop")
L(sun(3120, 7820, 60), 5, 5.8, ACC, 8, sfx="wood_high")
T("这段时间，归我", 2550, 7860, 70, GREEN, k0=6, k1=8.0, sfx="pop")

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：拉远看全板 → 推到评论区

FULL = (1800, 4500, 0.115)
COMMENT = (XL, R6, 0.8)
scene("你打了几个勾？", "评论区见", FULL, bars=4)
J_END = J()
b.move(J_END, 4, COMMENT)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
L(comment_box(XL, R6 - 20, 1200, 520), 5, 5.9, BLACK, 8)
T("评论区：你打了几个勾？", XL, R6 - 60, 66, RED, k0=6, k1=8.75, sfx="pop")
T("下一讲：开豪车的人，你记住他了吗？", XL, R6 + 90, 48, k0=10, k1=13.5, sfx="wood_high", gain=0.6)
L(underline(XL - 400, XL + 400, R6 + 140, 10, 36), 13.6, 14.2, BLACK, 6)
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(6, "freedom", "钱买自由", "钱最大的用处，是买回时间", ACC, b.shots,
                 [f"{BOOK}第 7 章“自由”（转述）",
                  "中译本：《金钱心理学》，李青宗译，民主与建设出版社 / 后浪 2023"],
                 "钱最大的用处|是买回【时间】", SQUARE_SHOT,
                 ["书中观点（转述）：Morgan Housel, The Psychology of Money (Harriman House, 2020)；中译本《金钱心理学》"
                  "（摩根·豪泽尔著，李青宗译，民主与建设出版社 / 后浪 2023）第 7 章“自由”——钱最大的内在价值，是让你能"
                  "掌控自己的时间；书中提到心理学家安格斯·坎贝尔的研究：比起收入，“觉得能掌控自己的生活”更能预测幸福感；"
                  "书中提到康奈尔大学卡尔·皮勒默访谈了大量老人，他们看重朋友、家人、陪孩子的时间，没人说该更拼命工作去买东西；"
                  "现在很多工作下了班脑子还在上班。上屏均为转述，不是逐字引文。",
                  "坎贝尔研究的柱状图只示意“能自己做主”高于“收入”，不是数值；皮勒默访谈人数、坎贝尔研究年份未核实，不上屏数字。",
                  "开局四题自测清单、按勾数的两种解读（打勾少先攒几个月生活费；打勾多用钱换时间，如请人打扫、搬近点少通勤）、"
                  "“涨薪分两路”与长椅画面，均为示意 / 据书中思路整理，不是投资或理财建议，不指向任何具体公司、平台或产品。",
                  "“23:40”、工作群消息、老板桌为现实场景示意；小王为示意人物，坎贝尔、皮勒默只写名字，不画肖像。"
                  "小猪罐为本系列视觉角色。"],
                 tags="#自由 #时间")
    return b.attach(ep)
