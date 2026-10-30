"""02 五种想歪（白板手绘版）：这五种想法，你中了几个？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，最后 4 拍不出新笔画）。
叙事（E 自测清单）：开局白板正中只画一张空白的「想歪自测」卡，五个空方框，请观众对着打勾 →
亮书（书里列了十种想歪的套路，这讲先看前五种）→ 相机绕着自测卡转一圈，每格一种：
① 非黑即白（九十八分的卷子，被一处错整张涂黑，drop）、② 以偏概全（一个红叉复印成一排；信号词「总是 / 从来 / 永远」）、
③ 心理过滤（十张脸里一张哭脸被放大镜罩住）、④ 否定正面（表扬塞进碎纸机）、⑤ 妄下结论（读心术：同事没打招呼；
算命：还没进门就认定会砸）→ 回到正中的自测卡：填上五个名字、数勾，中了很正常，每格补一朵白云写换法 →
做法：心里一沉，对一对是哪格 → 拉远看全板（自测卡在中间，五种想歪围成一圈）→ 评论区 + 健康提醒。
构图与 01 讲不同：白板分成 3×3 九宫格，自测卡固定在中间格，八个讲解格绕着它顺时针排开，相邻场景只挪一格。
系列视觉角色：小周（戴工牌）+ 念头云（乌云带涂黑边、红字；白云蓝字为换法）。
书中观点为转述（戴维·伯恩斯《伯恩斯新情绪疗法》第 3 章“破解情绪：思维决定情绪”，十种认知扭曲的前五种；
中文叫法为通行译法，李亚萍译本原用词未核实）；例子、数字与换法为现实场景示意、据书中思路整理。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, cross, face, join, rect,
                               scribble, stick, underline)

from .common import BOOK, episode

ACC = "#5B5FB8"
SQUARE_SHOT = 3                 # 场景 4：小周 + 九十八分卷子被一处错涂黑 + 乌云「全砸了」

b = Board(size=(5400, 5900))

# 3×3 九宫格：列中心 x，行中心 y；自测卡在正中格
CX = (900, 2700, 4500)
CY = (1000, 2400, 3800)
Z = 0.8


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def cloud(x, y, w, h, n=9, tail=None) -> skia.Path:
    """念头云：椭圆上一圈鼓包；tail=(tx, ty) 时朝该点画两个小圆（从头顶冒出来）。"""
    rx, ry = w / 2, h / 2
    p = skia.Path()
    a0 = -math.pi / 2 + 0.2
    pts = [(x + rx * math.cos(a0 + 2 * math.pi * i / n), y + ry * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]
    p.moveTo(*pts[0])
    for i in range(n):
        am = a0 + 2 * math.pi * (i + 0.5) / n
        q = pts[(i + 1) % n]
        p.quadTo(x + rx * 1.32 * math.cos(am), y + ry * 1.32 * math.sin(am), *q)
    p.close()
    parts = [p]
    if tail:
        tx, ty = tail
        for f, r in ((0.45, 16), (0.78, 10)):
            sx, sy = x, y + ry * 1.05
            parts.append(circle(sx + (tx - sx) * f, sy + (ty - sy) * f, r))
    return join(*parts)


def dark(x, y, w, h, a=0.80, c=0.97, m=44) -> skia.Path:
    """乌云的涂黑边：沿云的内圈来回涂一圈锯齿。"""
    rx, ry = w / 2, h / 2
    p = skia.Path()
    for i in range(m + 1):
        ang = 2 * math.pi * i / m
        f = a if i % 2 == 0 else c
        pt = (x + rx * f * math.cos(ang), y + ry * f * math.sin(ang))
        p.moveTo(*pt) if i == 0 else p.lineTo(*pt)
    return p


def zhou(x, y, s=0.7, arms="down") -> skia.Path:
    """小周：简笔小人 + 工牌（挂绳 + 小卡片）。(x, y) 为脚底。"""
    hy = y - 290 * s
    badge = join(P((x - 20 * s, hy + 45 * s), (x, hy + 105 * s), (x + 20 * s, hy + 45 * s)),
                 rect(x, hy + 128 * s, 38 * s, 46 * s, 5 * s))
    return join(stick(x, y, s, arms), badge)


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def box(x, y, r=50) -> skia.Path:
    return rect(x, y, 2 * r, 2 * r, 10)


def mini_face(x, y, r=46, mood="smile") -> skia.Path:
    """圆脸：笑 / 哭（哭脸带一滴眼泪）。"""
    p = circle(x, y, r)
    p.addCircle(x - r * 0.35, y - r * 0.2, r * 0.08)
    p.addCircle(x + r * 0.35, y - r * 0.2, r * 0.08)
    if mood == "smile":
        p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.05, r * 0.9, r * 0.6), 20, 140)
    else:
        p.addArc(skia.Rect.MakeXYWH(x - r * 0.42, y + r * 0.25, r * 0.84, r * 0.55), 200, 140)
        p.moveTo(x - r * 0.35, y + r * 0.0)
        p.quadTo(x - r * 0.48, y + r * 0.22, x - r * 0.35, y + r * 0.3)
        p.quadTo(x - r * 0.22, y + r * 0.22, x - r * 0.35, y + r * 0.0)
    return p


def paper(x, y, w=380, h=470) -> skia.Path:
    """卷子：折角纸 + 下半截三行字。"""
    parts = [P((x - w / 2, y - h / 2), (x + w / 2 - 50, y - h / 2), (x + w / 2, y - h / 2 + 50), (x + w / 2, y + h / 2),
               (x - w / 2, y + h / 2), close=True), P((x + w / 2 - 50, y - h / 2), (x + w / 2 - 50, y - h / 2 + 50),
                                                      (x + w / 2, y - h / 2 + 50))]
    for i in range(3):
        yy = y + 90 + i * 55
        parts.append(P((x - w / 2 + 40, yy), (x + w / 2 - 40 - (i % 2) * 60, yy)))
    return join(*parts)


def star(x, y, r=40) -> skia.Path:
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return P(*pts, close=True)


def rays(x, y, r, n=6, ln=50) -> skia.Path:
    parts = []
    for i in range(n):
        a = -math.pi / 2 + (i - (n - 1) / 2) * 0.42
        parts.append(P((x + r * math.cos(a), y + r * math.sin(a)), (x + (r + ln) * math.cos(a), y + (r + ln) * math.sin(a))))
    return join(*parts)


def head(no_name, x, y):
    """讲解格的页首：一个方框 + 「① 非黑即白」（自测卡那一行的放大版）。返回方框中心。"""
    bx = x - 470
    L(box(bx, y), 0, 0.6, BLACK, 9, sfx="wood_high")
    T(no_name, bx + 80 + 35 * len(no_name), y, 70, BLUE, k0=0.6)
    return bx, y


# ---------------------------------------------------------------- 开局：一张空白自测卡（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

CARD = (CX[1], 2430)                    # 自测卡中心（正中格）
ROWS = [2120 + 180 * i for i in range(5)]
BOXX, NAMEX, WCX = 2170, 2460, 3110      # 方框 / 名字 / 白云 的 x
VC = (CX[1], 2500, 0.78)                # 自测卡视角

scene("对着打个勾", "想歪自测", VC, bars=2)
L(rect(CARD[0], CARD[1], 1240, 1060, 30), 0, 0.8, BLACK, 8, sfx="wood_low")
T("想歪自测", CARD[0], 1965, 76, RED, k0=1, k1=2, sfx="pop")
for n, ry in enumerate(ROWS):
    k = 2 + n * 0.75
    L(join(box(BOXX, ry), P((2240, ry + 36), (2860, ry + 36))), k, k + 0.7, BLACK, 8,
      sfx="wood_high" if abs(k - round(k)) < 1e-9 else None)

# 书：十种，先看五种（左上格）
scene("书里列了十种", "书中观点 · 十种想歪", (CX[0], CY[0], Z))
L(book(560, 1000, 380, 260), 0, 0.9, BLACK, 10, sfx="wood_low")
T("伯恩斯新情绪疗法", 560, 790, 56, GREEN, k0=1, k1=3, sfx="pop")
T("十种", 1180, 820, 150, RED, k0=3, k1=3.8, sfx="ding")
L(join(*[cloud(940 + 120 * i, 1060, 100, 70) for i in range(5)]), 4, 4.9, BLACK, 7, sfx="wood_high")
L(join(*[cloud(940 + 120 * i, 1210, 100, 70) for i in range(5)]), 5, 5.9, BLACK, 7, sfx="wood_high")
L(oval(1180, 1060, 680, 150), 6, 6.8, RED, 9, sfx="rim")
T("先看五种", 1180, 1370, 66, BLUE, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- ① 非黑即白（场景 3–4，上中格）

PX, PY = 2400, 1030                     # 卷子
ZX, ZY = 2950, 1400                     # 小周脚底
scene("一处错就全砸了", "① 非黑即白", (CX[1], CY[0], Z))
bx, by = head("① 非黑即白", CX[1], 640)
L(paper(PX, PY), 2, 2.8, BLACK, 9, sfx="wood_low")
T("98", PX - 20, PY - 90, 140, RED, k0=3, k1=3.8, sfx="pop")
L(zhou(ZX, ZY, 0.65), 4, 4.8, BLACK, 9, sfx="wood_high")
L(face(ZX, ZY, 0.65, "sad"), 4.8, 5.0)
L(cloud(ZX, 860, 340, 190, tail=(ZX - 10, 1180)), 5, 5.6, BLACK, 8, sfx="pop")
L(dark(ZX, 860, 340, 190), 5.6, 6.0, BLACK, 5)
T("全砸了", ZX, 860, 60, RED, k0=6, k1=6.8, sfx="pop")
L(check(bx, by, 40), 7, 7.6, RED, 11, sfx="ding")

# ★ drop：一处红叉，整张卷子被一层层涂黑
scene("一处错，全涂黑", "① 非黑即白", (2650, 1030, 0.85), shake=[0], flashes=[0])
L(cross(PX + 100, PY + 145, 42), 0, 0.6, RED, 14, sfx="kick")
for n in range(3):
    L(scribble(PX - 10, PY - 150 + 155 * n, 330, 140, 9), 1 + n, 1.9 + n, BLACK, 16, sfx="shaker" if n % 2 else "wood_high")
L(dark(ZX, 860, 400, 230, 0.86, 1.08, 52), 4, 4.8, BLACK, 7, sfx="tom")
T("要么满分，要么零分", PX, 1400, 72, RED, k0=5, k1=7.25, sfx="pop")

# ---------------------------------------------------------------- ② 以偏概全（场景 5–6，右上格 → 右中格）

scene("面试挂了一次", "② 以偏概全", (CX[2], CY[0], Z))
bx, by = head("② 以偏概全", CX[2], 640)
L(cross(4000, 980, 80), 2, 2.8, RED, 14, sfx="rim")
L(join(*[cross(4180 + 150 * i, 980, 42) for i in range(4)]), 3, 3.9, RED, 9, sfx="shaker")
L(zhou(4380, 1430, 0.6), 4, 4.8, BLACK, 9, sfx="wood_high")
L(face(4380, 1430, 0.6, "sad"), 4.8, 5.0)
L(cloud(4760, 1190, 400, 190, tail=(4430, 1230)), 5, 5.6, BLACK, 8, sfx="pop")
L(dark(4760, 1190, 400, 190), 5.6, 6.0, BLACK, 5)
T("总是这样", 4760, 1190, 60, RED, k0=6, k1=7)
L(check(bx, by, 40), 7, 7.6, RED, 11, sfx="ding")

scene("留意这几个词", "② 以偏概全 · 信号词", (CX[2], CY[1], Z))
T("信号词", CX[2], 2030, 72, k0=0, k1=0.8, sfx="pop")
for n, w in enumerate(("总是", "从来", "永远")):
    x = 4080 + 420 * n
    T(w, x, 2350, 110, RED, k0=1 + 2 * n, k1=1.8 + 2 * n, sfx="pop")
    L(oval(x, 2350, 310, 180), 2 + 2 * n, 2.8 + 2 * n, BLUE, 8, sfx="wood_high")
T("听到先停一下", CX[2], 2650, 66, BLUE, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- ③ 心理过滤（场景 7，右下格）

scene("只盯那条差评", "③ 心理过滤", (CX[2], 3850, Z))
bx, by = head("③ 心理过滤", CX[2], 3490)
L(join(*[mini_face(3960 + 130 * i, 3720) for i in range(5)]), 2, 2.9, BLACK, 7, sfx="wood_high")
L(join(*[mini_face(3960 + 130 * i, 3880, mood="cry" if i == 3 else "smile") for i in range(5)]), 3, 3.9, BLACK, 7,
  sfx="wood_high")
L(join(circle(4350, 3880, 82), P((4410, 3940), (4500, 4040))), 4, 4.8, RED, 11, sfx="ding")
L(join(mini_face(4860, 3820, 140, "cry"), P((4420, 3830), (4725, 3760)), P((4400, 3950), (4740, 3900))),
  5, 5.9, BLACK, 8, sfx="pop")
T("整晚想它", 4860, 4100, 64, RED, k0=6, k1=7, sfx="pop")
L(check(bx, by, 40), 7, 7.6, RED, 11, sfx="ding")

# ---------------------------------------------------------------- ④ 否定正面（场景 8，下中格）

scene("被夸了说运气好", "④ 否定正面", (CX[1], 3850, Z))
bx, by = head("④ 否定正面", CX[1], 3490)
L(join(rect(2400, 3740, 320, 200, 10), star(2400, 3715, 46), P((2300, 3800), (2500, 3800))), 2, 2.8, BLACK, 8,
  sfx="wood_high")
L(join(rect(2400, 3950, 380, 110, 14), P((2250, 3925), (2550, 3925)),
       *[P((2260 + 40 * i, 4010), (2260 + 40 * i, 4150 + (i % 3) * 25)) for i in range(8)]), 3, 3.9, BLACK, 8,
  sfx="shaker")
L(zhou(2950, 4280, 0.65), 4, 4.8, BLACK, 9, sfx="wood_high")
L(face(2950, 4280, 0.65, "flat"), 4.8, 5.0)
L(cloud(2980, 3790, 340, 180, tail=(2960, 4060)), 5, 5.6, BLACK, 8, sfx="pop")
L(dark(2980, 3790, 340, 180), 5.6, 6.0, BLACK, 5)
T("不算数", 2980, 3790, 60, RED, k0=6, k1=6.8)
L(check(bx, by, 40), 7, 7.6, RED, 11, sfx="ding")

# ---------------------------------------------------------------- ⑤ 妄下结论（场景 9–10，左下格 → 左中格）

scene("同事没打招呼", "⑤ 妄下结论 · 读心术", (CX[0], 3850, Z))
bx, by = head("⑤ 妄下结论", CX[0], 3490)
L(join(stick(450, 4270, 0.65, hair=True), P((540, 4000), (620, 4000)), P((550, 4060), (640, 4060))), 2, 2.8,
  BLACK, 9, sfx="wood_high")
L(zhou(1000, 4270, 0.65, "up"), 3, 3.8, BLACK, 9, sfx="wood_high")
L(face(1000, 4270, 0.65, "flat"), 3.8, 4.0)
L(cloud(1160, 3800, 400, 190, tail=(1010, 4040)), 4, 4.6, BLACK, 8, sfx="pop")
L(dark(1160, 3800, 400, 190), 4.6, 5.0, BLACK, 5)
T("他讨厌我", 1160, 3800, 58, RED, k0=5, k1=6, sfx="pop")
T("读心术", 600, 3730, 60, BLUE, k0=6, k1=6.8)
L(check(bx, by, 40), 7, 7.6, RED, 11, sfx="ding")

scene("还没开始就定了", "⑤ 妄下结论 · 算命", (CX[0], 2450, Z))
T("还有一种：算命", CX[0], 2080, 70, BLUE, k0=0, k1=1.75, sfx="pop")
L(join(circle(620, 2450, 180), P((520, 2625), (720, 2625), (770, 2700), (470, 2700), close=True)), 2, 2.9, BLACK, 10,
  sfx="wood_high")
T("肯定砸", 620, 2450, 56, RED, k0=3, k1=3.8, sfx="rim")
L(zhou(990, 2800, 0.62), 4, 4.8, BLACK, 9, sfx="wood_high")
L(face(990, 2800, 0.62, "sad"), 4.8, 5.0)
L(join(rect(1330, 2540, 230, 480, 8), circle(1410, 2560, 12)), 5, 5.8, BLACK, 9, sfx="wood_low")
T("汇报", 1330, 2420, 56, k0=6, k1=6.8, sfx="pop")
L(rays(620, 2450, 200, 5, 55), 7, 7.8, RED, 8, sfx="shaker")

# ---------------------------------------------------------------- 回到自测卡：数勾、换法、做法（场景 11–13，正中格）

NAMES = ("非黑即白", "以偏概全", "心理过滤", "否定正面", "妄下结论")
scene("中了很正常", "回到自测卡", VC)
for n, nm in enumerate(NAMES):
    T(nm, NAMEX, ROWS[n], 64, k0=n, k1=n + 1, sfx="pop")
T("中了几个？", CARD[0], 3070, 72, RED, k0=5, k1=6.25, sfx="kick")
T("查想法，不查病", CARD[0], 3180, 56, BLUE, k0=6.25, k1=8)
H(7, "ding")

FIX = ("改掉那一处", "这次没过", "也看看好评", "我也出了力", "去问一句")
scene("每种换个说法", "每格一朵白云", VC)
L(join(*[cloud(WCX, ry, 360, 140) for ry in ROWS]), 0, 0.9, BLUE, 7, sfx="wood_high")
for n, s in enumerate(FIX):
    k = 1 + 1.5 * n
    T(s, WCX, ROWS[n], 46, BLUE, k0=k, sfx="pop" if abs(k - round(k)) < 1e-9 else None)

scene("对一对是哪格", "做法 · 心里一沉时", (2520, 2520, 0.68))
L(zhou(1900, 3000, 0.7, "point"), 0, 0.8, BLACK, 9, sfx="wood_high")
L(face(1900, 3000, 0.7, "sad"), 0.8, 1.0)
L(cloud(1900, 2560, 300, 170, tail=(1900, 2760)), 1, 1.6, BLACK, 8, sfx="pop")
L(dark(1900, 2560, 300, 170), 1.6, 2.0, BLACK, 5)
T("又搞砸了", 1900, 2560, 50, RED, k0=2, k1=3, sfx="pop")
L(arrow((1990, 2440), (2110, 2160), -0.25, 34), 3, 3.8, RED, 8, sfx="wood_high")
L(oval(NAMEX, ROWS[0], 330, 110), 4, 4.8, RED, 9, sfx="ding")
L(check(BOXX, ROWS[0], 38), 5, 5.6, RED, 11, sfx="rim")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (CX[1], 2950, 0.19)
VE = (CX[1], 5250, Z)
scene("你中了几个", "评论区见", FAR, bars=4)
H(0, "cymbal", 0.5)
L(cloud(3050, 5640, 560, 190), 0.5, 1.3, BLUE, 8)
T("今天换掉一朵乌云", 3050, 5640, 46, BLUE, k0=1.3, k1=3.3)
T("一直低落、睡不好、不想活，去找医生聊聊", CX[1], 5430, 46, k0=1.5, k1=3.5)
H(2, "ding")
b.move(J(), 4, VE)
H(4, "wood_high", 0.6)
T("你中了几个？最常中哪个？", CX[1], 4900, 66, RED, k0=6, k1=9, sfx="pop")
T("下一讲：心里难受，就说明事情糟？", CX[1], 5080, 46, k0=9, k1=12.75, sfx="wood_high")
L(underline(2300, 3100, 4960, 10, 40), 13, 13.8, RED, 6, sfx="pop")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "trap", "五种想歪", "这五种想法，你中了几个？", ACC, b.shots,
                 [f"{BOOK}第 3 章“破解情绪：思维决定情绪”（十种认知扭曲的前五种，转述）",
                  "中译本：李亚萍译，中国城市出版社 2011；科学技术文献出版社 2014"],
                 "这五种想法|你中了【几个】", SQUARE_SHOT,
                 ["书中观点均为转述：书中第 3 章列出十种让心情变差的“认知扭曲”，本讲讲前五种——非黑即白（达不到满分就当零分）、"
                  "以偏概全（一次坏事看成没完没了，爱用“总是”“从来”）、心理过滤（只盯一个坏细节，整件事被染黑）、"
                  "否定正面（好事被说成不算数）、妄下结论（读心术：认定别人看不起你；算命：认定事情会搞砸）。"
                  "出处：David D. Burns, Feeling Good: The New Mood Therapy (William Morrow, 1980)，中译本《伯恩斯新情绪疗法》"
                  "（戴维·伯恩斯著，李亚萍译）。上屏叫法为通行译法与口语说法，李亚萍译本的原用词未核实；上屏均为转述，不是逐字引文。",
                  "卷子“98”分、面试挂一次、十张脸里一张哭脸（差评）、表扬进碎纸机、同事没打招呼、汇报前认定会砸均为现实场景示意，"
                  "不指向任何具体公司或个人；数字为示意，不是数据，也不是书中病例。",
                  "“想歪自测”清单只用来认出想法的套路，不打分、不做诊断；每格的“换法”（改掉那一处 / 这次没过 / 也看看好评 / "
                  "我也出了力 / 去问一句）与“心里一沉时对一对是哪格”为据书中思路整理的建议。",
                  "本片为读书分享，不能替代诊断和治疗；情绪持续低落或有轻生念头，请尽快联系医生、心理咨询师或当地心理援助热线。"],
                 tags="#认知扭曲")
    return b.attach(ep)
