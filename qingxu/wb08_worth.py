"""08 价值不看业绩（白板手绘版）：项目黄了，人就不值钱了？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事（形式 B：一个故事贯穿）：小周的一周，每块白板角上一页日历——
周一项目被砍，晚上觉得自己身上的价签一路跌价 → 周二工位上冒出乌云“我就是个失败的人”，贴名牌“乱贴标签” →
★drop：价签被一把撕掉，“人不带价签” → 亮书第 13 章“工作≠价值”；业绩和“我”绑在一起同起同落 →
周三给自己算账（项目没了还剩什么），晚上用三栏卡改那句话 → 周四见到退休的长辈；往下问一层，
挖出压在底下的那句“我得一直成功才算数”，把它放到石头上问“真的吗？” → 周五乌云变小，接着干下一个 →
做法：把“我……”换成“这件事……” → 拉远看这一周 → 评论区。
书中观点为转述（戴维·伯恩斯《伯恩斯新情绪疗法》第 13 章“工作≠价值”、第 10 章“抑郁症的根源”）；
故事、人物、时间线、价签数字均为示意，做法据书中思路整理。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, cross, desk, face,
                               join, marker, partial, rect, stick, underline)

from .common import BOOK, episode

ACC = "#B8862B"
SQUARE_SHOT = 3                 # 场景 4：小周 + 价签被撕掉、“人不带价签”

b = Board(size=(3600, 10700))
GREY = "#5A5A66"


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(len(b.shots) - 1, k0, k1, s, x, y, size, color, sfx=sfx)


def TL(s, x0, y, size=60, color=BLACK, k0=0.0, k1=None, sfx=None):
    """左对齐写字：x0 为左端。"""
    T(s, x0 + K.text_w(s, size, "hand") / 2, y, size, color, k0, k1, sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def C(k0, k1, fn, sfx=None):
    b.custom(len(b.shots) - 1, k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def badge(x, y, s=1.0) -> skia.Path:
    """小周的工牌：挂绳 + 卡片。(x, y) 为小人脚底。"""
    hy = y - 290 * s
    return join(P((x - 22 * s, hy + 42 * s), (x, hy + 112 * s), (x + 22 * s, hy + 42 * s)),
                rect(x, hy + 132 * s, 46 * s, 40 * s, 5 * s))


def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    return join(stick(x, y, s, arms), badge(x, y, s))


def cal(x, y) -> skia.Path:
    """台历一页：(x, y) 为纸面中心；日子写在 (x, y + 15)。"""
    return join(rect(x, y, 170, 150, 10), P((x - 85, y - 40), (x + 85, y - 40)),
                P((x - 45, y - 92), (x - 45, y - 58)), P((x + 45, y - 92), (x + 45, y - 58)))


def day(name, x, y, k0=0.0):
    """日历页 + 星期：描框 0.5 拍、写字 0.8 拍。"""
    L(cal(x, y), k0, k0 + 0.5, BLACK, 8, sfx="wood_high")
    T(name, x, y + 15, 56, RED, k0=k0 + 0.5, k1=k0 + 1.3)


def folder(x, y, w=420, h=300) -> skia.Path:
    top = y - h / 2
    return join(P((x - w / 2, top + 40), (x - w / 2, y + h / 2), (x + w / 2, y + h / 2), (x + w / 2, top + 40),
                  close=True),
                P((x - w / 2, top + 40), (x - w / 2, top), (x - w / 2 + w * 0.36, top), (x - w / 2 + w * 0.44, top + 40)))


def cloud(x, y, w, h, n=11) -> skia.Path:
    """念头云外轮廓：沿椭圆一圈小鼓包。"""
    p = skia.Path()
    pts = [(x + w / 2 * math.cos(2 * math.pi * i / n), y + h / 2 * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    p.moveTo(*pts[0])
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        cx, cy = x + w / 2 * 1.22 * math.cos(a), y + h / 2 * 1.3 * math.sin(a)
        p.quadTo(cx, cy, *pts[i + 1])
    return p


def darkedge(x, y, w, h, n=46) -> skia.Path:
    """乌云的涂黑边：贴着轮廓内侧来回涂一圈。"""
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        r = 0.84 if i % 2 else 0.99
        pts.append((x + w / 2 * r * math.cos(a), y + h / 2 * r * math.sin(a)))
    return P(*pts)


def dots(a, bb) -> skia.Path:
    """念头云连到小人头顶的两颗小圆点。"""
    (x0, y0), (x1, y1) = a, bb
    return join(circle(x0 + (x1 - x0) * 0.3, y0 + (y1 - y0) * 0.3, 20), circle(x0 + (x1 - x0) * 0.75, y0 + (y1 - y0) * 0.75, 12))


def tag_shape(x, y, w=200, h=260) -> skia.Path:
    """价签：尖头朝上，顶上一个穿绳孔。(x, y) 为价签中心。"""
    t = y - h / 2
    return join(P((x, t), (x + w / 2, t + 45), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2), (x - w / 2, t + 45),
                  close=True), circle(x, t + 30, 11))


def strike(x, y, w) -> skia.Path:
    return P((x - w / 2 - 14, y + 10), (x + w / 2 + 14, y - 14))


def pot_flower(x, y) -> skia.Path:
    """花盆 + 一朵花：(x, y) 为盆底中点。"""
    parts = [P((x - 75, y - 120), (x - 55, y), (x + 55, y), (x + 75, y - 120), close=True),
             P((x - 85, y - 120), (x + 85, y - 120)), P((x, y - 120), (x, y - 250)),
             P((x, y - 170), (x + 45, y - 200))]
    for i in range(5):
        a = 2 * math.pi * i / 5
        parts.append(circle(x + 30 * math.cos(a), y - 280 + 30 * math.sin(a), 22))
    parts.append(circle(x, y - 280, 14))
    return join(*parts)


def can(x, y) -> skia.Path:
    """洒水壶 + 几滴水：(x, y) 为壶身中心，壶嘴朝右下。"""
    hd = skia.Path()
    hd.addArc(skia.Rect.MakeXYWH(x - 95, y - 70, 70, 100), 90, 180)
    parts = [rect(x, y, 130, 100, 14), hd, P((x + 65, y + 10), (x + 150, y - 50)), P((x + 140, y - 62), (x + 165, y - 38))]
    for dx, dy in ((175, 0), (195, 50), (170, 95)):
        parts.append(P((x + dx, y + dy - 14), (x + dx - 5, y + dy + 14)))
    return join(*parts)


def glasses(x, y, s=1.0) -> skia.Path:
    hy = y - 290 * s
    return join(circle(x - 17 * s, hy - 7 * s, 13 * s), circle(x + 17 * s, hy - 7 * s, 13 * s),
                P((x - 4 * s, hy - 8 * s), (x + 4 * s, hy - 8 * s)))


def sparks(x, y, r) -> skia.Path:
    parts = []
    for a in (-150, -110, -70, -30, 10, 190):
        t = math.radians(a)
        parts.append(P((x + r * math.cos(t), y + r * math.sin(t)), (x + (r + 70) * math.cos(t), y + (r + 70) * math.sin(t))))
    return join(*parts)


def rock(x, y, w, h) -> skia.Path:
    return P((x - w * 0.5, y + h * 0.35), (x - w * 0.44, y - h * 0.3), (x - w * 0.24, y - h * 0.5), (x + w * 0.26, y - h * 0.48),
             (x + w * 0.47, y - h * 0.22), (x + w * 0.5, y + h * 0.38), (x + w * 0.36, y + h * 0.5), (x - w * 0.38, y + h * 0.5),
             close=True)


# ---------------------------------------------------------------- 周一：项目被砍（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("项目被砍了", "周一 · 项目被砍", (950, 900, 0.85), bars=2)
day("周一", 560, 540)
L(folder(1000, 870, 460, 320), 2, 2.8, BLACK, 10, sfx="wood_low")
T("三个月的项目", 1000, 1140, 60, k0=3, k1=4.5, sfx="pop")
L(cross(1000, 880, 170), 5, 5.7, RED, 14, sfx="rim")

ZH2 = (2380, 1300, 0.95)        # 周一晚上的小周（脚底, 比例）
scene("觉得自己也跌价", "周一晚上 · 跌价", (2650, 900, 0.85), shake=[6])
L(zhou(*ZH2), 0, 0.8, BLACK, 10, sfx="wood_low")
L(face(*ZH2, "sad"), 0.8, 0.9)
_hy2 = ZH2[1] - 290 * ZH2[2]
L(join(P((ZH2[0] + 8, _hy2 + 60), (2560, 1053)), tag_shape(2570, 1150, 200, 250)), 1, 1.7, BLACK, 9, sfx="wood_high")
T("100", 2570, 1185, 86, k0=2, k1=2.8, sfx="pop")
L(strike(2570, 1185, 140), 3, 3.4, RED, 9, sfx="rim")
T("50", 2850, 960, 96, k0=4, k1=4.8, sfx="pop")
L(strike(2850, 960, 100), 5, 5.4, RED, 9, sfx="rim")
L(arrow((2930, 1010), (3050, 1110), -0.15, 40), 6, 6.6, RED, 9, sfx="shaker")
T("1", 3080, 1220, 160, RED, k0=7, k1=7.8, sfx="tom")

# ---------------------------------------------------------------- 周二：乌云 + 撕价签（场景 3–4）

ZH3 = (2420, 2760, 0.9)
_hy3 = ZH3[1] - 290 * ZH3[2]
NECK3 = (ZH3[0] - 6, _hy3 + 56)
TAG3 = (2270, 2652, 130, 170)   # 价签中心与宽高

scene("工位上，一句话不想说", "周二 · 工位", (2650, 2300, 0.85))
day("周二", 2160, 1890)
L(join(zhou(*ZH3), desk(2810, 2600, 400)), 2, 2.8, BLACK, 10, sfx="wood_low")
L(face(*ZH3, "flat"), 2.8, 2.9)

J_TEAR = len(b.shots)           # 下一个场景（drop）第 0 拍撕掉价签


def tag_fn(c, k, t):
    """价签：周二随小周一起画出；drop 第 0 拍被一把撕成两半飞走，挂绳断开。"""
    x, y, w, h = TAG3
    hole = (x, y - h / 2 + 30)
    body = tag_shape(x, y, w, h)
    tear = b.t_of(J_TEAR, 0) if len(b.shots) > J_TEAR and b.ep is not None else 1e9
    if t < tear:
        string = P(NECK3, hole)
        part, tip = partial(join(string, body), k)
        c.drawPath(part, marker(BLACK, 8))
        if k > 0.6:
            K.text(c, "1", x, y + 22, 84, "hand", RED, clamp01((k - 0.6) / 0.4))
        return tip
    f = clamp01((t - tear) / 0.75)
    e = ease_in_out(f)
    c.drawPath(P(NECK3, (NECK3[0] - 40, NECK3[1] + 55 - 20 * e)), marker(BLACK, 8))   # 断掉的半截挂绳
    if f >= 1:
        return None
    zig = [(x, y - h / 2 - 10)]
    for i in range(1, 7):
        zig.append((x + (16 if i % 2 else -16), y - h / 2 + i * (h + 20) / 6))
    left = P(*zig, (x - w, y + h / 2 + 20), (x - w, y - h / 2 - 10), close=True)
    right = P(*zig, (x + w, y + h / 2 + 20), (x + w, y - h / 2 - 10), close=True)
    alpha = 1 - clamp01((f - 0.55) / 0.45)
    for side, clip in ((-1, left), (1, right)):
        dx = side * 420 * e
        dy = -260 * f + 520 * f * f
        c.save()
        c.translate(x + dx, y + dy)
        c.rotate(side * 75 * e)
        c.translate(-x, -y)
        c.clipPath(clip, skia.ClipOp.kIntersect, True)
        c.drawPath(body, marker(BLACK, 8, alpha))
        K.text(c, "1", x, y + 22, 84, "hand", RED, alpha)
        c.restore()
    if f < 0.45:                                       # 撕开那一下的爆线
        a = 1 - f / 0.45
        for ang in range(0, 360, 45):
            r0, r1 = 110 + 160 * f, 170 + 260 * f
            q = math.radians(ang)
            c.drawPath(P((x + r0 * math.cos(q), y + r0 * math.sin(q)), (x + r1 * math.cos(q), y + r1 * math.sin(q))),
                       marker(RED, 8, a))
    return None


C(2, 2.8, tag_fn)
CL3 = (2860, 2130, 640, 300)
L(join(cloud(*CL3), dots((2600, 2330), (2470, 2440))), 3, 3.8, BLACK, 9, sfx="pop")
T("我就是个", 2860, 2085, 62, RED, k0=4, k1=5, sfx="pop")
T("失败的人", 2860, 2175, 62, RED, k0=5, k1=6, sfx="pop")
L(darkedge(*CL3), 6, 6.5, GREY, 7, sfx="shaker")
L(rect(3060, 2350, 270, 86, 10), 6.5, 6.9, BLACK, 7)
T("乱贴标签", 3060, 2362, 52, k0=7, k1=8, sfx="tom")

scene("人身上没价签", "第一个转折 · 撕掉价签", (2650, 2450, 0.75), shake=[0], flashes=[0])
H(0, "kick", 0.95)
T("人不带价签", 2650, 2950, 110, RED, k0=2, k1=3.25, sfx="pop")
L(underline(2340, 2960, 3030), 4, 4.7, RED, 9, sfx="ding")
b.erase(len(b.shots) - 1, 5, 5.3, ZH3[0], _hy3 + 6, 52, 44)
H(5, "shaker")
L(face(*ZH3, "smile"), 6, 6.5, BLACK, 9, sfx="pop")
L(sparks(ZH3[0], _hy3, 70), 7, 7.7, ACC, 8, sfx="wood_high")

# ---------------------------------------------------------------- 书中观点（场景 5–6）

scene("书里有一整章", "书中观点 · 第十三章", (950, 2400, 0.85))
L(book(720, 2250, 440, 300), 0, 0.9, BLACK, 10, sfx="wood_low")
T("伯恩斯新情绪疗法", 950, 1990, 58, GREEN, k0=1, k1=3, sfx="pop")
T("第13章", 1260, 2250, 70, k0=3, k1=4, sfx="pop")
T("工作", 700, 2680, 104, k0=4, k1=4.8, sfx="pop")
L(join(P((880, 2655), (1020, 2655)), P((880, 2705), (1020, 2705))), 5, 5.5, BLACK, 12, sfx="wood_high")
L(P((1005, 2600), (895, 2760)), 6, 6.4, RED, 12, sfx="rim")
T("价值", 1200, 2680, 104, RED, k0=7, k1=7.8, sfx="pop")

OX, OY0 = 450, 4220             # 坐标轴原点
LINE = [(520, 3900), (760, 3640), (1000, 3570), (1180, 3880), (1360, 4100)]
scene("绑在一起，同起同落", "书中观点 · 绑在一起", (950, 3900, 0.85))
L(join(P((OX, 3440), (OX, OY0), (1400, OY0)), P((OX - 20, 3470), (OX, 3440), (OX + 20, 3470))), 0, 0.8, BLACK, 9,
  sfx="wood_high")
L(P(*LINE), 1, 1.9, BLUE, 11, sfx="wood_low")
T("业绩", 1000, 3490, 62, BLUE, k0=2, k1=2.8, sfx="pop")
L(P(*[(px, py + 85) for px, py in LINE]), 3, 3.9, RED, 11, sfx="wood_low")
T("我", 1450, 4185, 70, RED, k0=4, k1=4.8, sfx="pop")
L(join(*[P((px, py + 10), (px - 14, py + 30), (px + 14, py + 52), (px, py + 75)) for px, py in LINE[1:4]]), 5, 5.6, BLACK, 7,
  sfx="shaker")
T("业绩跌，我也跌", 950, 4330, 64, RED, k0=6, k1=7.75, sfx="tom")

# ---------------------------------------------------------------- 周三：算账 + 三栏卡（场景 7–8）

ZH7 = (2300, 4350, 0.85)
scene("项目没了，还剩什么", "周三 · 算算还剩什么", (2650, 3900, 0.85))
day("周三", 2170, 3480)
L(join(zhou(*ZH7, "hold"), rect(2830, 3950, 620, 560, 16)), 2, 2.9, BLACK, 10, sfx="wood_low")
L(face(*ZH7, "flat"), 2.9, 3.0)
TL("会写方案", 2640, 3790, 60, k0=3, k1=4, sfx="pop")
TL("同事愿意找我", 2640, 3960, 60, k0=4, k1=5.5, sfx="pop")
TL("周末陪爸妈", 2640, 4130, 60, k0=5.5, k1=6.75)
L(join(check(2585, 3790, 30), check(2585, 3960, 30), check(2585, 4130, 30)), 7, 7.8, GREEN, 10, sfx="ding")

CX8, CY8, CW8, CH8 = 2650, 5420, 1190, 640
COLS = [CX8 - CW8 / 3, CX8, CX8 + CW8 / 3]
scene("用三栏卡改一改", "周三晚上 · 三栏卡", (2650, 5400, 0.85))
L(join(rect(CX8, CY8, CW8, CH8, 18), P((CX8 - CW8 / 2, CY8 - CH8 / 2 + 110), (CX8 + CW8 / 2, CY8 - CH8 / 2 + 110)),
       P((CX8 - CW8 / 6, CY8 - CH8 / 2), (CX8 - CW8 / 6, CY8 + CH8 / 2)),
       P((CX8 + CW8 / 6, CY8 - CH8 / 2), (CX8 + CW8 / 6, CY8 + CH8 / 2))), 0, 0.9, BLACK, 9, sfx="wood_high")
for n, (s, k0) in enumerate((("想法", 1), ("哪种歪", 1.8), ("换个说法", 2.6))):
    T(s, COLS[n], CY8 - CH8 / 2 + 58, 50, k0=k0, k1=k0 + 0.8, sfx="pop" if n == 0 else None)
T("我是", COLS[0], CY8 - 10, 64, RED, k0=3.4, k1=4.2)
T("失败的人", COLS[0], CY8 + 85, 64, RED, k0=4.2, k1=5.0)
T("乱贴标签", COLS[1], CY8 + 40, 64, k0=5, k1=6, sfx="rim")
T("这个项目", COLS[2], CY8 - 10, 64, BLUE, k0=6, k1=7, sfx="pop")
T("失败了", COLS[2], CY8 + 85, 64, BLUE, k0=7, k1=7.8, sfx="ding")

# ---------------------------------------------------------------- 周四：退休的长辈 + 往下问（场景 9–11）

OLD = (800, 5800, 1.0)
ZH9 = (440, 5800, 0.7)
scene("没了工作也是他", "周四 · 楼下的长辈", (950, 5400, 0.85))
day("周四", 470, 4990)
L(join(stick(*OLD, "hold", hair=True), glasses(*OLD)), 2, 2.8, BLACK, 10, sfx="wood_low")
L(face(*OLD, "smile"), 2.8, 2.9)
L(can(990, 5605), 3, 3.8, BLUE, 9, sfx="wood_high")
L(pot_flower(1270, 5810), 4, 4.8, GREEN, 9, sfx="pop")
L(zhou(*ZH9), 5, 5.7, BLACK, 9, sfx="wood_low")
L(face(*ZH9, "flat"), 5.7, 5.8)
T("退休了", 1150, 5080, 66, k0=6, k1=6.8, sfx="pop")
T("日子照样过", 1150, 5190, 66, BLUE, k0=7, k1=8, sfx="pop")

scene("往下再问一层", "第二个转折 · 往下问", (950, 6800, 0.75))
T("项目黄了", 950, 6350, 72, k0=0, k1=1, sfx="pop")
L(arrow((950, 6410), (950, 6570), 0.0, 36), 1, 1.6, BLACK, 9, sfx="wood_low")
T("那又怎样？", 1270, 6490, 52, BLUE, k0=2, k1=3, sfx="pop")
T("我没用", 950, 6650, 84, RED, k0=3, k1=3.8, sfx="pop")
L(arrow((950, 6715), (950, 7090), 0.0, 40), 4, 4.6, BLACK, 9, sfx="wood_low")
T("再往下呢？", 1270, 6770, 52, BLUE, k0=5, k1=6, sfx="pop")
T("我得一直成功才算数", 950, 7160, 70, RED, k0=6, k1=8, sfx="tom")

ZH11 = (950, 7990, 0.8)
scene("这句，真的吗？", "第二个转折 · 压在底下", (950, 7560, 0.9))
L(rock(950, 7165, 780, 210), 0, 0.9, BLACK, 10, sfx="wood_low")
T("真的吗？", 950, 7440, 110, RED, k0=2, k1=3, sfx="pop")
T("？", 520, 7620, 110, BLUE, k0=4, k1=4.8, sfx="pop")
T("？", 1380, 7620, 110, BLUE, k0=5, k1=5.8, sfx="pop")
L(zhou(*ZH11, "shrug"), 6, 6.7, BLACK, 9, sfx="wood_high")
L(face(*ZH11, "flat"), 6.7, 6.8)
L(P((1180, 7062), (1150, 7120), (1200, 7170), (1160, 7230), (1190, 7268)), 7, 7.5, RED, 8, sfx="rim")

# ---------------------------------------------------------------- 周五：接着干（场景 12）

ZH12 = (2400, 7950, 0.9)
_hy12 = ZH12[1] - 290 * ZH12[2]
scene("接着干下一个", "周五 · 新项目", (2650, 7500, 0.85))
day("周五", 2170, 7080)
L(zhou(*ZH12, "point"), 2, 2.8, BLACK, 10, sfx="wood_low")
L(face(*ZH12, "smile"), 2.8, 2.9)
L(folder(2860, 7790, 380, 260), 3, 3.6, BLUE, 10, sfx="wood_high")
T("新项目", 2860, 7820, 58, BLUE, k0=3.6, k1=4.4)


def shrink_fn(c, k, t):
    """乌云冒出来，又一点点缩小，挪到角落。"""
    g = k / 0.2 if k < 0.2 else 1 - 0.62 * ease_in_out((k - 0.2) / 0.8)
    m = ease_in_out(clamp01((k - 0.2) / 0.8))
    x, y = 2440 - 220 * m, 7330 + 50 * m
    w, h = 520 * g, 230 * g
    if w < 4:
        return None
    c.drawPath(cloud(x, y, w, h), marker(BLACK, 9))
    c.drawPath(darkedge(x, y, w, h), marker(GREY, 7))
    K.text(c, "失败的人", x, y + 6 * g, 60 * g, "hand", RED)
    return None


C(5, 6, shrink_fn, sfx="shaker")
L(cloud(2930, 7300, 470, 210), 6, 6.7, BLUE, 9, sfx="pop")
T("接着干", 2930, 7310, 68, BLUE, k0=7, k1=7.8, sfx="pop")

# ---------------------------------------------------------------- 做法（场景 13）

S13 = 88
W13 = K.text_w("这件事失败了", S13, "hand")
X0_13 = 950 - W13 / 2
CH13 = W13 / 6                  # 每个字的宽度（等宽估计）
scene("把我换成这件事", "做法 · 换个主语", (950, 8900, 0.85))
T("换个主语说", 950, 8440, 72, BLUE, k0=0, k1=1.25, sfx="pop")
T("我失败了", 950, 8650, S13, k0=2, k1=3, sfx="pop")
L(cross(950 - K.text_w("我失败了", S13, "hand") / 2 + CH13 / 2, 8650, 46), 3, 3.4, RED, 10, sfx="rim")
L(arrow((950, 8720), (950, 8860), 0.0, 36), 4, 4.6, BLACK, 9, sfx="wood_low")
T("这件事失败了", 950, 8960, S13, BLUE, k0=5, k1=6.5, sfx="pop")
_e = skia.Path()
_e.addOval(skia.Rect.MakeXYWH(X0_13 - 26, 8960 - 72, CH13 * 3 + 52, 144))
L(_e, 7, 7.7, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看这一周，再推到评论区

FULL = (1800, 5300, 0.11)
END = (1800, 10000, 0.85)
J_END = scene("评论区聊聊", "评论区见", FULL, bars=4)
b.move(J_END, 4, END)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("把你和工作分开", 1800, 9700, 82, RED, k0=5, k1=6.75, sfx="pop")
T("你还剩什么？", 1800, 9815, 82, RED, k0=7, k1=8.5, sfx="pop")
T("下一讲：非要做到满分，才敢交？", 1800, 9990, 48, k0=9, k1=12, sfx="wood_high")
L(cloud(2080, 10220, 470, 150), 12, 12.6, BLUE, 8, sfx="ding")
T("今天换掉一朵乌云", 2080, 10228, 48, BLUE, k0=12.6, k1=14.4)
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(8, "worth", "价值不看业绩", "项目黄了，人就不值钱了？", ACC, b.shots,
                 [f"{BOOK}第四部分 第 13 章“工作≠价值”（转述）",
                  f"{BOOK}第四部分 第 10 章（往下追问、找出底下的假设，转述）",
                  "中译本：李亚萍译，中国城市出版社 2011；科学技术文献出版社 2014"],
                 "项目黄了|人就【不值钱】了", SQUARE_SHOT,
                 ["书中观点均为转述，不是逐字引文：第 13 章“工作≠价值”讨论把自我价值绑在成就和业绩上，事业一受挫人就"
                  "跟着垮；人的价值不靠业绩来挣。第 10 章讲对一个让人难受的想法一路追问“如果这是真的，对我意味着什么”，"
                  "能挖出底下压着的假设（本片写作“我得一直成功才算数”，为转述示意）。",
                  "小周一周的故事（周一项目被砍、周三算账、周五接着干）、价签上的 100 / 50 / 1、"
                  "跷跷板改画的“业绩和我同起同落”折线、价签被撕掉的画面，均为对书中观点的示意，不是书中案例或数据。",
                  "楼下退休的长辈为现实场景示意，不是书中人物；书中第 13 章的具体例子未引用。",
                  "“乱贴标签”与三栏卡（想法 / 哪种歪 / 换个说法）为通行译法和本系列口语叫法，李亚萍译本原用词未核实；"
                  "把“我失败了”换成“这件事失败了”为据书中第 13、10 章思路整理的做法。",
                  "不指向任何具体公司或个人。",
                  "本片为读书分享，不能替代诊断和治疗；情绪持续低落或有轻生念头，请尽快联系医生、心理咨询师或当地心理援助热线。"],
                 tags="#职场")
    return b.attach(ep)
