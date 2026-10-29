"""09 上瘾（白板手绘版）：为什么越熬夜越离不开咖啡？

叙事：打工人切身问题开局（熬到半夜 → 早上一杯咖啡 → 晚上又精神 → 第二天要两杯）→ 书中观点（亮书；系统陷阱之一
“上瘾”，也叫转嫁负担：外力压住症状，系统自己解决问题的本事萎缩，于是越来越离不开外力；外力可以是药、酒、一条规定；
画成“症状 / 外力 / 自己”一张图，对上咖啡和睡觉）→ 身边的例子（进度慢就加班、新人的活老员工顺手做了、心烦就刷手机、
作业全靠家长盯；最后连回咖啡）→ 具体做法（先找病根 / 补自己的本事 / 外力慢慢撤 / 撑过难受期）→ 评论区互动。
书中观点为转述（Meadows, Thinking in Systems, 2008，第五章 System Traps：Addiction / Shifting the Burden to
the Intervenor；中译本《系统之美》，邱昭良译，浙江人民出版社 2012）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, clock, cross, desk, doc,
                               face, hands_at, join, node, rect, scribble, stick, underline)

from .common import BOOK, episode

ACC = "#4F6D8F"
SQUARE_SHOT = 16

b = Board(size=(3600, 9000))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


# ---------------------------------------------------------------- 本讲画法

def moon(x, y, r=90) -> skia.Path:
    """月牙：外弧 + 内弧。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12), P((x - 12, y + h / 2 - 16), (x + 12, y + h / 2 - 16)))


def cup(x, y, s=1.0, steam=True) -> skia.Path:
    """咖啡杯：(x, y) 为杯身中心。"""
    body = P((x - 60 * s, y - 75 * s), (x - 48 * s, y + 75 * s), (x + 48 * s, y + 75 * s), (x + 60 * s, y - 75 * s),
             close=True)
    handle = skia.Path()
    handle.addArc(skia.Rect.MakeXYWH(x + 30 * s, y - 45 * s, 60 * s, 70 * s), -90, 180)
    parts = [body, handle, P((x - 57 * s, y - 45 * s), (x + 57 * s, y - 45 * s))]
    if steam:
        for dx in (-22, 22):
            st = skia.Path()
            st.moveTo(x + dx * s, y - 95 * s)
            st.quadTo(x + (dx - 22) * s, y - 125 * s, x + dx * s, y - 150 * s)
            st.quadTo(x + (dx + 22) * s, y - 175 * s, x + dx * s, y - 200 * s)
            parts.append(st)
    return join(*parts)


def bed(x, y, w=440) -> skia.Path:
    """床（侧视）：(x, y) 为床面中点。"""
    return join(P((x - w / 2, y - 120), (x - w / 2, y + 90)), P((x + w / 2, y - 40), (x + w / 2, y + 90)),
                P((x - w / 2, y + 40), (x + w / 2, y + 40)), rect(x - w / 2 + 80, y - 10, 110, 50, 20),
                P((x - w / 2 + 150, y + 10), (x - w / 2 + 170, y - 40), (x + w / 2, y - 40), (x + w / 2, y + 40)))


def pit(x, y, w=380, h=110) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    for i in range(5):
        xx = x - w * 0.3 + i * w * 0.15
        p.moveTo(xx, y + h * 0.05)
        p.lineTo(xx + 20, y + h * 0.3)
    return p


def smooth(*pts) -> skia.Path:
    """过各点的平滑曲线（中点二次贝塞尔）。"""
    p = skia.Path()
    p.moveTo(*pts[0])
    for i in range(1, len(pts) - 1):
        mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
        p.quadTo(pts[i][0], pts[i][1], mx, my)
    p.lineTo(*pts[-1])
    return p


def loop_arrow(x, y, r, head=40) -> skia.Path:
    """顺时针循环箭头（约 300 度）。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -60, 300)
    a = math.radians(240)
    ex, ey = x + r * math.cos(a), y + r * math.sin(a)
    tang = a + math.pi / 2
    for d in (0.5, -0.5):
        p.moveTo(ex, ey)
        p.lineTo(ex - head * math.cos(tang + d), ey - head * math.sin(tang + d))
    return p


# ---------------------------------------------------------------- 开局：越喝越多（镜头 1–6）

b.shot("又熬到半夜", "灵魂拷问", view=(950, 850, 0.85))
L(moon(600, 540, 90), 0, 0.6, BLACK, 9, sfx="wood_high")
L(stick(950, 1250, 0.9, "hold"), 1, 1.6, sfx="pop")
L(face(950, 1250, 0.9, "smile"), 1.6, 1.75)
L(phone(1075, 1040), 1.75, 2.0, BLUE, 8)
T("凌晨 1:30", 1300, 560, 70, RED, k0=2, sfx="pop")

b.shot("早上困得睁不开", "灵魂拷问", view=(2650, 850, 0.85))
L(clock(2250, 720, 140), 0, 0.7, sfx="wood_high")
L(hands_at(2250, 720, 140, 7, 0), 0.7, 0.9, RED, 12)
T("7:00", 2250, 930, 64, RED, k0=1, sfx="pop")
L(stick(2800, 1250, 0.9, "down"), 2, 2.6, sfx="wood_high")
L(face(2800, 1250, 0.9, "sad"), 2.6, 2.75)
T("Zzz", 3020, 840, 64, BLUE, k0=3, sfx="pop")

b.shot("先来一杯咖啡", "灵魂拷问", view=(2650, 850, 0.85))
L(cup(2470, 1170), 0, 0.8, BLACK, 9, sfx="pop")
T("1 杯", 2470, 1320, 56, k0=1, sfx="wood_high")
T("满血！", 2800, 640, 76, RED, k0=2, sfx="ding")

b.shot("晚上又精神了", "灵魂拷问", view=(950, 1750, 0.85))
L(moon(600, 1440, 90), 0, 0.6, BLACK, 9, sfx="wood_high")
L(stick(950, 2150, 0.9, "hold"), 1, 1.6, sfx="pop")
L(face(950, 2150, 0.9, "smile"), 1.6, 1.75)
L(phone(1075, 1940), 1.75, 2.0, BLUE, 8)
T("凌晨 2:00", 1300, 1460, 70, RED, k0=2, sfx="rim")

b.shot("第二天要两杯", "灵魂拷问", view=(2650, 1750, 0.85))
L(cup(2350, 1820), 0, 0.7, BLACK, 9, sfx="pop")
L(cup(2650, 1820), 1, 1.7, BLACK, 9, sfx="pop")
T("2 杯", 2500, 2020, 64, RED, k0=2, sfx="wood_high")
T("3 杯？", 3080, 1640, 64, RED, k0=3, sfx="rim")

b.shot("怎么越喝越多？", "灵魂拷问", view=(1800, 1300, 0.42), flashes=[0])
T("？", 1800, 1300, 380, RED, k0=0, k1=0.6, sfx="kick")
T("越喝越多", 1800, 2380, 110, k0=1.0, k1=2.0, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "系统之美", view=(1050, 3050, 0.9))
L(book(750, 3050, 420, 280), 0, 1.0, sfx="wood_low")
T("系统之美", 750, 2810, 80, GREEN, k0=1.0, sfx="pop")
T("德内拉 · 梅多斯", 750, 3280, 46, k0=2.0, sfx="pop")

b.shot("里面讲了个陷阱", "书中观点 · 系统陷阱", view=(1050, 3050, 0.9))
T("系统陷阱", 1360, 2840, 70, k0=0, sfx="pop")
L(pit(1360, 3150), 1, 1.7, BLACK, 9, sfx="wood_high")
L(stick(1360, 3170, 0.45, "up"), 2, 2.5, BLUE, 8, sfx="pop")
T("第五章", 1360, 2950, 46, k0=2.6)

b.shot("名字叫上瘾", "书中观点 · 上瘾", view=(1050, 3150, 0.9), shake=[0], flashes=[0])
T("上瘾", 1050, 3470, 200, RED, k0=0, k1=0.5, sfx="kick")
L(underline(840, 1260, 3590), 2, 2.5, RED, 9, sfx="ding")
H(3, "tom", 0.7)

DX = 2680                       # 示意图中心
SYM = (DX, 2800)
OUT = (2250, 3450)              # 外力
SELF = (3110, 3450)             # 自己

b.shot("麻烦冒出来了", "书中观点 · 上瘾", view=(DX, 3250, 0.8))
L(rect(*SYM, 360, 150, 24), 0, 0.6, BLACK, 9, sfx="wood_high")
T("症状：困", SYM[0], SYM[1], 66, k0=1, sfx="pop")
T("！", 2900, 2780, 90, RED, k0=2, sfx="rim")

b.shot("外力一压就好", "书中观点 · 外力", view=(DX, 3250, 0.8))
L(node(*OUT, 100), 0, 0.4, BLACK, 9, sfx="pop")
T("外力", OUT[0], OUT[1], 58, RED, k0=0.4)
L(arrow((2300, 3360), (2520, 2885), 0.08, 44), 1, 1.5, RED, 9, sfx="wood_high")
T("快", 2330, 3080, 64, RED, k0=2, sfx="pop")
H(3, "ding", 0.6)

b.shot("自己也能解决", "书中观点 · 自身能力", view=(DX, 3250, 0.8))
L(node(*SELF, 100), 0, 0.4, BLUE, 9, sfx="pop")
T("自己", SELF[0], SELF[1], 58, BLUE, k0=0.4)
L(arrow((3060, 3360), (2780, 2885), -0.08, 44), 1, 1.5, BLUE, 9, sfx="wood_high")
T("慢", 3030, 3080, 64, BLUE, k0=2, sfx="pop")

b.shot("外力越用越多", "书中观点 · 外力", view=(DX, 3250, 0.8))
L(arrow((2265, 3370), (2485, 2890), 0.08, 40), 0, 0.4, RED, 7, sfx="pop")
L(arrow((2335, 3350), (2555, 2885), 0.08, 40), 1, 1.4, RED, 7, sfx="pop")
T("×3", 2165, 3235, 60, RED, k0=2, sfx="wood_high")

b.shot("自己的本事退化", "书中观点 · 本事退化", view=(DX, 3250, 0.8))
L(arrow((2360, 3480), (3000, 3480), 0.12, 44), 0, 0.7, RED, 9, sfx="wood_high")
T("越用越弱", DX, 3640, 62, RED, k0=1, sfx="pop")
L(arrow((3262, 3380), (3262, 3540), 0, 34), 2, 2.3, RED, 9, sfx="rim")

b.shot("只能再加外力", "书中观点 · 越陷越深", view=(DX, 3250, 0.8), shake=[0])
L(loop_arrow(DX, 3200, 150), 0, 0.8, RED, 9, sfx="kick")
T("离不开", DX, 3200, 64, RED, k0=1, sfx="pop")
H(2, "ding", 0.6)

b.shot("咖啡就是外力", "书中观点 · 对上号", view=(DX, 3280, 0.8))
T("咖啡", OUT[0], 3615, 56, RED, k0=0, sfx="pop")
T("睡觉", SELF[0], 3615, 56, BLUE, k0=1, sfx="pop")
H(2, "ding", 0.6)

b.shot("药和规定也算", "书中观点 · 外力", view=(DX, 3300, 0.8))
T("药 · 酒 · 一条规定", DX, 3770, 52, k0=0, k1=1.2, sfx="pop")
L(underline(2440, 2920, 3815, 10, 30), 2, 2.5, RED, 7, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 4600), (2650, 4600), (950, 5550), (2650, 5550)]
b.shot("身边也常见", "身边的例子", view=(1800, 5080, 0.355))
T("身边的例子", 1800, 4060, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("进度慢，就加班", "例子 · 加班", view=(950, 4600, 0.85))
L(clock(520, 4420, 100), 0, 0.6, sfx="wood_high")
L(hands_at(520, 4420, 100, 10, 0), 0.6, 0.8, RED, 10)
L(desk(800, 4760), 1, 1.6, sfx="pop")
L(stick(1100, 4960, 0.75), 1.6, 2.0)
T("又加班", 1200, 4420, 70, RED, k0=2, sfx="pop")

b.shot("流程没人改", "例子 · 加班", view=(950, 4650, 0.85))
L(doc(1380, 4780, 150, 190), 0, 0.5, sfx="wood_high")
T("流程", 1380, 4630, 50, k0=0.6)
T("没动过", 1380, 4930, 50, RED, k0=1, sfx="pop")
T("下周：再加班", 950, 4260, 60, RED, k0=2, sfx="rim")

b.shot("新人的活顺手做了", "例子 · 帮着做", view=(2650, 4600, 0.85))
L(stick(2350, 4950, 0.8, "hold"), 0, 0.5, sfx="wood_high")
T("老员工", 2350, 4600, 50, k0=0.5)
L(stick(2950, 4950, 0.8, "shrug"), 1, 1.5, BLUE, sfx="pop")
T("新人", 2950, 4600, 50, BLUE, k0=1.5)
L(doc(2520, 4790, 110, 140, 3), 2, 2.4, sfx="pop")

b.shot("新人一直学不会", "例子 · 帮着做", view=(2650, 4600, 0.85))
T("3 个月还不会", 2650, 4330, 64, RED, k0=0, sfx="pop")
T("？", 3090, 4650, 80, RED, k0=1, sfx="rim")
L(doc(2560, 4750, 110, 140, 3), 2, 2.4, sfx="pop")

b.shot("心烦就刷手机", "例子 · 刷手机", view=(950, 5550, 0.85))
L(stick(800, 5900, 0.8, "hold"), 0, 0.5, sfx="wood_high")
L(phone(915, 5700), 1, 1.3, BLUE, 8, sfx="pop")
T("烦", 600, 5560, 70, RED, k0=2, sfx="pop")
for n in range(3):
    L(P((1000, 5650 + n * 40), (1080, 5650 + n * 40)), 3 + n * 0.2, 3.15 + n * 0.2, BLUE, 6,
      sfx="shaker" if n == 0 else None)

b.shot("越刷越静不下来", "例子 · 刷手机", view=(950, 5550, 0.85))
T("睡前 2 小时", 1200, 5300, 58, RED, k0=0, sfx="pop")
L(scribble(800, 5560, 240, 110, 7), 1, 1.5, RED, 7, sfx="shaker")
T("更烦", 1220, 5480, 64, RED, k0=2, sfx="rim")

b.shot("作业全靠家长盯", "例子 · 盯作业", view=(2650, 5550, 0.85))
L(stick(2420, 5950, 0.6), 0, 0.5, sfx="wood_high")
L(doc(2230, 5850, 110, 140, 3), 0.5, 0.8)
T("作业", 2230, 5730, 46, k0=0.8)
L(stick(2850, 5950, 0.85, "point"), 1, 1.6, BLUE, sfx="pop")
T("快写！", 2900, 5420, 64, RED, k0=2, sfx="pop")

b.shot("家长一走就不写", "例子 · 盯作业", view=(2650, 5550, 0.85))
b.erase(len(b.shots) - 1, 0, 0.8, 2880, 5680, 440, 600)
H(0, "shaker")
L(arrow((2780, 5850), (3200, 5850), 0.05, 40), 1, 1.4, GREEN, 8, sfx="wood_high")
T("玩去了", 2420, 5600, 54, RED, k0=2, sfx="pop")

b.shot("每件都靠外力", "身边的例子", view=(1800, 5080, 0.355))
for n, (x, y) in enumerate(CARDS):
    T("外力", x + 470, y - 345, 110, RED, k0=n, sfx="pop")

b.shot("跟咖啡一个样", "身边的例子", view=(1800, 5080, 0.355), shake=[0])
T("都跟咖啡一样", 1800, 6110, 125, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 6950), (2650, 6950), (950, 7900), (2650, 7900)]
b.shot("那该怎么戒", "具体做法", view=(1800, 7420, 0.355))
T("戒掉依赖四步", 1800, 6420, 130, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 860, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("先问困从哪来", "第一步 · 找病根", view=(950, 6950, 0.85))
T("① 先找病根", 950, 6650, 76, BLUE, k0=0, sfx="pop")
T("困", 680, 6960, 110, RED, k0=2, k1=2.4, sfx="pop")

b.shot("缺觉才是病根", "第一步 · 找病根", view=(950, 6950, 0.85))
L(arrow((1080, 6960), (790, 6960), 0, 40), 0, 0.5, BLACK, 9, sfx="wood_high")
T("缺觉", 1230, 6960, 90, k0=1, sfx="pop")
L(underline(1140, 1320, 7030, 10, 30), 2, 2.4, RED, 8, sfx="ding")

b.shot("补自己的本事", "第二步 · 补本事", view=(2650, 6950, 0.85))
T("② 补本事", 2650, 6650, 76, BLUE, k0=0, sfx="pop")
L(bed(2650, 6930), 1, 1.8, sfx="wood_high")
T("Zzz", 2950, 6780, 56, BLUE, k0=2, sfx="pop")

b.shot("手机放客厅充电", "第二步 · 补本事", view=(2650, 7000, 0.85))
T("23:00", 2330, 7170, 66, RED, k0=0, sfx="pop")
L(phone(3080, 7120), 1, 1.3, BLUE, 8, sfx="wood_high")
T("放客厅", 3080, 7235, 48, k0=1.4)
L(check(2700, 7160, 45), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("团队先补流程", "第二步 · 补本事", view=(2650, 7000, 0.85))
T("团队：改一处流程", 2560, 7320, 56, k0=0, k1=1.4, sfx="pop")
L(check(2850, 7315, 40), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("外力慢慢撤", "第三步 · 慢慢撤", view=(950, 7900, 0.85))
T("③ 外力慢慢撤", 950, 7590, 76, BLUE, k0=0, sfx="pop")
for n, x in enumerate((680, 950, 1220)):
    L(cup(x, 7860, 0.75, steam=False), 1 + n * 0.5, 1.4 + n * 0.5, BLACK, 8, sfx="pop" if n != 1 else None)

b.shot("每周少一杯", "第三步 · 慢慢撤", view=(950, 7900, 0.85))
L(cross(1220, 7860, 70), 0, 0.3, RED, 11, sfx="rim")
T("3 → 2 → 1 杯", 950, 8030, 62, RED, k0=1, sfx="pop")
L(cross(950, 7860, 70), 2, 2.3, RED, 11, sfx="rim")

b.shot("盯作业也慢慢撤", "第三步 · 慢慢撤", view=(950, 7950, 0.85))
T("陪着写 → 只检查", 900, 8180, 58, k0=0, k1=1.4, sfx="pop")
L(check(1220, 8175, 40), 2, 2.3, GREEN, 10, sfx="ding")

CURVE = [(2100, 7820), (2300, 7900), (2480, 8140), (2680, 8120), (2880, 7900), (3180, 7760)]
b.shot("撤的时候会难受", "第四步 · 撑过去", view=(2650, 7900, 0.85))
T("④ 撑过难受期", 2650, 7590, 76, BLUE, k0=0, sfx="pop")
L(smooth(*CURVE), 1, 1.8, BLACK, 9, sfx="wood_high")
T("难受", 2560, 8240, 56, RED, k0=2, sfx="rim")

b.shot("撑过去就轻松", "第四步 · 撑过去", view=(2650, 7900, 0.85))
L(stick(3180, 7740, 0.42, "up"), 0, 0.4, BLUE, 8, sfx="pop")
T("几天后", 3000, 8030, 56, GREEN, k0=1, sfx="pop")
H(2, "ding")

b.shot("照着做就行", "具体做法", view=(1800, 7420, 0.355))
for n, (x, y) in enumerate(SOL):
    L(check(x + 500, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 else "pop")

b.shot("先治本，再撤外力", "一句话", view=(1800, 4700, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 8740, 0.8))
T("你离不开的外力是啥？", 1800, 8660, 76, RED, k0=0.5, k1=1.8)
T("下一讲：想改变，该从哪里下手？", 1800, 8820, 46, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "addiction", "上瘾", "为什么越熬夜越离不开咖啡？", ACC, b.shots,
                 [f"{BOOK}第五章 · 系统陷阱：上瘾（转嫁负担，转述）", "中译本：邱昭良译，浙江人民出版社 2012"],
                 "越熬夜|越离不开【咖啡】", 16,
                 ["书中观点均为转述：第五章系统陷阱之“上瘾”（Addiction / Shifting the Burden to the Intervenor）——"
                  "用外部干预压住症状，系统自己解决问题的能力随之萎缩，于是需要越来越多的干预，越来越离不开它；干预可以是"
                  "一种药物，也可以是一项掩盖问题的政策。出路：一开始就别只治标；已经陷入时，加强系统自身的能力，再逐步撤掉"
                  "外部干预，撤的过程会难受。出处：Donella H. Meadows, Thinking in Systems: A Primer (2008)，中译本"
                  "《系统之美》（邱昭良译，浙江人民出版社 2012）。上屏均为转述，不是逐字引文。",
                  "熬夜喝咖啡、进度慢就加班、老员工顺手替新人做、心烦刷手机、作业全靠家长盯均为现实场景示意，不指向任何具体"
                  "公司或个人；“症状 / 外力 / 自己”图为对书中机制的通俗化示意；杯数、时间、难受期曲线为示意，不是数据。",
                  "四步做法（先找病根、补自己的本事、外力慢慢撤、撑过难受期）为据书中思路整理的建议。"],
                 tags="#熬夜 #习惯")
    return b.attach(ep)
