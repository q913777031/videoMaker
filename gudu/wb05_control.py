"""05 孤独与自控（白板手绘版）：一个人的晚上，为什么管不住嘴？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（2026-10 观众反馈“动画切换太快，来不及看”后改为慢速讲解版）。

叙事：打工人切身问题开局（加完班一个人到家 → 点夜宵 → 说好只刷一会儿 → 一抬头两点）→ 书中观点
（亮书《孤独是可耻的》、卡乔波；孤独削弱自我调节——管情绪、管嘴、坚持做事；被排斥实验里被冷落的人自控表现变差；
催眠让同一批人分别体验“孤单”和“有人陪”，孤单时更消极、更挑剔；画成“孤单 → 自控电量往下掉 → 夜宵 / 刷手机 /
计划泡汤”一张图）→ 身边的例子（新公司没饭搭子下午拖活、一个人办健身卡去两次就停、和家里吵完架狂下单；最后连到
“一孤单，就管不住”）→ 具体做法（别光怪意志力 / 找个搭子 / 想吃前先找人聊几句）→ 评论区互动。
书中观点为转述（John T. Cacioppo & William Patrick, Loneliness: Human Nature and the Need for Social Connection,
W. W. Norton 2008；中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009，第一部分，主要见第 3 章“你的生活正在
失控”）；例子与做法为现实场景示意与据书中思路整理的建议。

白板布局：左栏自上而下（开局 → 书中观点），右栏自下而上（身边的例子 → 具体做法），相邻场景上下推拉，只在场景 8
横移一次；各块在原坐标里画好后整体平移到所在位置（scene(..., off=)）。
"""

import math

import skia

from adler import kit as K
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               doc, face, hands_at, join, rect, stick)

from .common import BOOK, episode

ACC = "#6B5B95"
SQUARE_SHOT = 6

b = Board(size=(3600, 8300))
OFF = [0, 0]      # 当前场景的整体平移量（块内坐标沿用原排版）


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.5 拍）。"""
    k1 = k0 + max(0.5, 0.25 * len(s)) if k1 is None else k1
    b.text(len(b.shots) - 1, k0, k1, s, x + OFF[0], y + OFF[1], size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    q = skia.Path(path)
    q.offset(OFF[0], OFF[1])
    b.path(len(b.shots) - 1, k0, k1, q, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def man(x, y, s, arms="down", mood="smile", k0=0.0, k1=None, color=BLACK, sfx=None):
    """小人 + 五官一起画：身体先描，五官随后。"""
    k1 = k0 + 0.6 if k1 is None else k1
    L(stick(x, y, s, arms), k0, k1, color, 9 if s >= 0.7 else 8, sfx=sfx)
    L(face(x, y, s, mood), k1, k1 + 0.15, color, 7)


# ---------------------------------------------------------------- 本讲画法

def moon(x, y, r=90) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12), P((x - 12, y + h / 2 - 16), (x + 12, y + h / 2 - 16)))


def door(x, y, w=200, h=380) -> skia.Path:
    """门：(x, y) 为门中心。"""
    return join(rect(x, y, w, h, 6), circle(x + w / 2 - 35, y + 10, 10))


def bowl(x, y, s=1.0, steam=True) -> skia.Path:
    """碗 + 筷子：(x, y) 为碗口中点。"""
    p = skia.Path()
    p.moveTo(x - 110 * s, y)
    p.lineTo(x + 110 * s, y)
    p.addArc(skia.Rect.MakeXYWH(x - 110 * s, y - 100 * s, 220 * s, 200 * s), 0, 180)
    parts = [p, P((x - 40 * s, y + 100 * s), (x + 40 * s, y + 100 * s)),
             P((x + 30 * s, y - 20 * s), (x + 150 * s, y - 150 * s)), P((x + 55 * s, y - 15 * s), (x + 170 * s, y - 130 * s))]
    if steam:
        for dx in (-40, 0):
            st = skia.Path()
            st.moveTo(x + dx * s, y - 25 * s)
            st.quadTo(x + (dx - 20) * s, y - 55 * s, x + dx * s, y - 85 * s)
            st.quadTo(x + (dx + 20) * s, y - 115 * s, x + dx * s, y - 145 * s)
            parts.append(st)
    return join(*parts)


def dumbbell(x, y, s=1.0) -> skia.Path:
    return join(P((x - 110 * s, y), (x + 110 * s, y)), rect(x - 110 * s, y, 40 * s, 130 * s, 8),
                rect(x + 110 * s, y, 40 * s, 130 * s, 8), rect(x - 150 * s, y, 30 * s, 90 * s, 6),
                rect(x + 150 * s, y, 30 * s, 90 * s, 6))


def spiral(x, y, r=100, turns=3.2) -> skia.Path:
    """催眠螺旋。"""
    p = skia.Path()
    n = 120
    for i in range(n + 1):
        a = i / n * turns * 2 * math.pi
        rr = r * i / n
        px, py = x + rr * math.cos(a), y + rr * math.sin(a)
        p.moveTo(px, py) if i == 0 else p.lineTo(px, py)
    return p


def battery(x, y, w=260, h=130) -> skia.Path:
    return join(rect(x, y, w, h, 18), rect(x + w / 2 + 16, y, 26, h * 0.4, 6))


def drain(x, y, w=260, h=130):
    """电量从满格掉到一格：颜色由绿转红。"""
    def fn(c, k, t):
        lv = 1 - 0.8 * k
        iw = (w - 36) * lv
        col = GREEN if lv > 0.5 else ("#E07B24" if lv > 0.3 else RED)
        K.rr(c, x - (w - 36) / 2 + iw / 2, y, iw, h - 36, 8, col)
        return None
    return fn


def boxes(x, y, n=3) -> skia.Path:
    """快递盒一摞：(x, y) 为底边中点。"""
    parts = []
    for i in range(n):
        cx, cy = x + (i % 2) * 30 - 15, y - 45 - i * 90
        parts += [rect(cx, cy, 150, 90, 6), P((cx - 25, cy - 45), (cx - 25, cy - 10)), P((cx + 25, cy - 45), (cx + 25, cy - 10))]
    return join(*parts)


# ---------------------------------------------------------------- 场景节奏
# 场景 1 = 2 小节（第 0–6 拍画完），场景 2–13 = 3 小节（12 拍：第 0–8 拍逐步画完，最后 4 拍停住），场景 14 = 4 小节。

def scene(text, tag, view, bars=3, off=(0, 0), **kw):
    """新场景：view 用块内原坐标给出，连同块内元素一起平移 off。"""
    OFF[:] = off
    return b.shot(text, tag, view=(view[0] + off[0], view[1] + off[1], view[2]), bars=bars, **kw)


# ---------------------------------------------------------------- 开局：一个人的晚上（场景 1–2）

scene("一个人到家，先点夜宵", "灵魂拷问", (1000, 950, 0.85), bars=2)
L(moon(480, 560, 80), 0, 0.8, BLACK, 9, sfx="wood_high")
T("22:30", 820, 560, 72, RED, k0=1, k1=1.8, sfx="pop")
L(door(480, 1050), 2, 2.8, BLACK, 9, sfx="wood_low")
man(760, 1240, 0.85, "down", "flat", k0=3, k1=3.7, sfx="wood_high")
L(rect(1180, 1030, 220, 360, 24), 4, 4.6, BLACK, 9, sfx="wood_high")
T("外卖", 1180, 960, 52, k0=4.6, k1=5.0)
T("炸鸡 + 奶茶", 1280, 720, 62, RED, k0=5, k1=6, sfx="pop")

scene("刷到两点，为啥停不下", "灵魂拷问", (950, 1950, 0.85))
man(720, 2150, 0.9, "hold", "smile", k0=0, k1=0.8, sfx="wood_high")
L(phone(845, 1940), 1, 1.8, BLUE, 8, sfx="pop")
L(bubble(1240, 1980, 400, 130, -1), 2, 2.8, BLACK, 8, sfx="wood_high")
T("就刷十分钟", 1240, 1980, 52, k0=2.8, k1=4.0)
L(clock(1300, 1520, 120), 4, 4.8, BLACK, 9, sfx="wood_high")
T("02:00", 1300, 1720, 64, RED, k0=5, k1=5.8, sfx="pop")
L(hands_at(1300, 1520, 120, 2, 0), 4.8, 5.0, RED, 12)
T("为啥管不住自己？", 900, 2340, 80, RED, k0=6, k1=8, sfx="rim")

# ---------------------------------------------------------------- 书中观点（场景 3–7）

scene("有本书专讲这个", "孤独是可耻的", (1050, 2950, 0.85), off=(0, 300))
L(book(760, 3010, 420, 280), 0, 0.9, sfx="wood_low")
T("孤独是可耻的", 1050, 2620, 80, GREEN, k0=1, k1=2.5, sfx="pop")
T("约翰 · 卡乔波", 760, 3250, 50, k0=3, k1=4.5, sfx="pop")
man(1400, 3200, 0.65, "down", "sad", k0=5, k1=5.7, sfx="wood_high")
T("孤单", 1400, 2860, 60, BLUE, k0=6, k1=6.6, sfx="pop")

scene("孤单时，自控会变弱", "书中观点 · 自控变弱", (1050, 3080, 0.85), off=(0, 300), shake=[0], flashes=[0])
T("自控变弱", 980, 3420, 150, RED, k0=0, k1=1, sfx="kick")
T("管情绪", 700, 3580, 56, k0=2, k1=2.8, sfx="tom")
T("管住嘴", 980, 3580, 56, k0=3, k1=3.8, sfx="tom")
T("坚持做事", 1260, 3580, 56, k0=4, k1=5, sfx="tom")
L(arrow((590, 3330), (590, 3500), 0, 40), 6, 6.8, RED, 11, sfx="ding")

# 被排斥实验：原排版在右栏 (2650, 3000)，挪到左栏
scene("被冷落的人，自控更差", "书中观点 · 被排斥实验", (2650, 3000, 0.85), off=(-1700, 1650))
T("鲍迈斯特等人的实验", 2650, 2530, 56, k0=0, k1=2, sfx="pop")
for n, x in enumerate((2200, 2350, 2500)):
    man(x, 2960, 0.55, "down", "smile", k0=2 + n * 0.45, k1=2.3 + n * 0.45, color=BLUE,
        sfx="wood_high" if n == 0 else None)
man(3060, 2960, 0.55, "down", "sad", k0=4, k1=4.6, color=RED, sfx="pop")
T("被冷落", 3060, 2700, 54, RED, k0=4.75, k1=5.5)
L(P((2200, 3420), (3200, 3420)), 5.6, 5.9, BLACK, 8)
L(rect(2450, 3280, 140, 280, 8), 6, 6.8, BLUE, 9, sfx="wood_high")
L(rect(2850, 3365, 140, 110, 8), 7, 7.5, RED, 9, sfx="rim")
T("更差", 2850, 3240, 56, RED, k0=7.5, k1=8.0)

scene("同一批人，孤单更挑剔", "书中观点 · 催眠实验", (950, 4450, 0.85), off=(0, 1350))
L(spiral(560, 3980, 100), 0, 0.7, BLUE, 8, sfx="wood_high")
T("催眠", 560, 4150, 56, BLUE, k0=0.7, k1=1.0)
T("同一批人", 1130, 3960, 60, k0=1, k1=2, sfx="pop")
L(join(arrow((1060, 4040), (700, 4290), 0.06, 36), arrow((1200, 4040), (1330, 4290), -0.06, 36)), 2, 2.8, GREEN, 8,
  sfx="wood_high")
man(600, 4680, 0.6, "down", "sad", k0=3, k1=3.6, sfx="pop")
T("孤单", 600, 4370, 54, BLUE, k0=3.75, k1=4.25)
T("更消极", 880, 4540, 50, RED, k0=4.25, k1=5.0)
T("更挑剔", 880, 4630, 50, RED, k0=5, k1=5.75, sfx="rim")
man(1250, 4680, 0.6, "down", "smile", k0=6, k1=6.3, sfx="ding")
man(1420, 4680, 0.6, "down", "smile", k0=6.3, k1=6.6)
T("有人陪", 1330, 4370, 54, GREEN, k0=6.8, k1=7.6)

# 一张图：原排版在右栏 (2650, 4450)，挪到左栏
BAT = (2950, 4070)
DX7, DY7 = -1700, 2400
scene("孤单拖垮自控", "书中观点 · 一张图", (2650, 4450, 0.85), off=(DX7, DY7))
man(2250, 4330, 0.6, "down", "sad", k0=0, k1=0.6, sfx="wood_high")
T("孤单", 2250, 3990, 60, BLUE, k0=1, k1=1.5, sfx="pop")
L(arrow((2370, 4070), (2760, 4070), 0.05, 40), 2, 2.6, BLACK, 9, sfx="wood_high")
L(battery(*BAT), 2.6, 3.4, BLACK, 9)
T("自控", BAT[0], 3930, 60, k0=3.4, k1=3.9)
b.custom(len(b.shots) - 1, 4, 4.6, drain(BAT[0] + DX7, BAT[1] + DY7), sfx="shaker")
for n, (x, w) in enumerate(((2450, "夜宵"), (2760, "刷手机"), (3120, "计划泡汤"))):
    k = 5 + n
    L(arrow((BAT[0] - 40 + n * 40, 4150), (x, 4520), 0.04 * (1 - n), 30), k, k + 0.3, RED, 8,
      sfx=("pop", "pop", "rim")[n])
    T(w, x, 4590, 56, RED, k0=k + 0.3, k1=min(8.0, k + 0.3 + 0.25 * len(w)))

# ---------------------------------------------------------------- 身边的例子（场景 8–10，右栏自下而上）

scene("没饭搭子，下午就拖", "例子 · 职场", (950, 5650, 0.85), off=(1700, 1050))
T("12:00 午饭", 620, 5210, 58, RED, k0=0, k1=1.5, sfx="pop")
man(620, 5800, 0.7, "hold", "flat", k0=2, k1=2.6, sfx="wood_high")
L(bowl(760, 5600, 0.45, False), 2.8, 3.5, BLACK, 7)
for n, x in enumerate((1150, 1290, 1430)):
    man(x, 5800, 0.55, "down", "smile", k0=4 + n * 0.3, k1=4.25 + n * 0.3, sfx="pop" if n == 0 else None)
L(doc(980, 5360, 120, 150, 3), 5.1, 5.9, BLACK, 8)
T("报告 0 字", 980, 5500, 46, RED, k0=6, k1=6.9, sfx="pop")
T("拖", 1380, 5350, 100, RED, k0=7, k1=7.6, sfx="rim")

scene("一个人健身，两次就停", "例子 · 健身", (2650, 5500, 0.85), off=(0, -50))
T("办了年卡", 2620, 5210, 58, k0=0, k1=1, sfx="pop")
L(dumbbell(2300, 5460, 0.9), 1, 1.8, BLACK, 9, sfx="wood_high")
man(2620, 5820, 0.75, "up", "smile", k0=2, k1=2.6, sfx="pop")
T("一个人", 2620, 5890, 46, k0=3, k1=3.75, sfx="rim")
T("第 1 周：2 次", 3020, 5410, 48, k0=4, k1=5, sfx="pop")
T("之后：0 次", 3020, 5530, 48, RED, k0=5, k1=5.9)
L(cross(2300, 5460, 90), 6, 6.6, RED, 11, sfx="rim")

scene("一孤单，就管不住", "例子 · 家庭", (950, 6550, 0.85), off=(1700, -2250), shake=[6])
man(500, 6760, 0.6, "point", "sad", k0=0, k1=0.6, sfx="wood_high")
man(760, 6760, 0.6, "shrug", "sad", k0=1, k1=1.6, sfx="pop")
T("吵", 630, 6270, 100, RED, k0=2, k1=2.5, sfx="rim")
L(arrow((880, 6500), (1030, 6500), 0, 30), 2.5, 2.9, BLACK, 8)
man(1140, 6800, 0.7, "hold", "flat", k0=3, k1=3.6, sfx="wood_high")
L(phone(1237, 6637, 60, 100), 3.75, 4.0, BLUE, 7)
L(boxes(1420, 6800, 3), 4, 4.8, BLACK, 8, sfx="pop")
T("下单 ×8", 1250, 6280, 58, RED, k0=5, k1=5.6, sfx="pop")
T("一孤单，就管不住", 950, 7020, 90, RED, k0=6, k1=8, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 11–13，右栏继续往上）


def card(x, y, title, size=72):
    L(rect(x, y, 1200, 860, 40), 0, 0.8, GREEN, 8, sfx="wood_high")
    T(title, x, y - 290, size, BLUE, k0=1, sfx="pop")


R1, R2 = 7750, 8700      # 原排版的两行卡片

scene("先别怪意志力", "第一步 · 别光怪自己", (950, R1 + 20, 0.85), off=(1700, 3400 - R1))
card(950, R1, "① 别光怪意志力")
man(1320, R1 + 400, 0.5, "shrug", "flat", k0=3, k1=3.6, sfx="wood_high")
T("今天跟人聊过天？", 1000, R1 + 60, 56, k0=4, k1=5.8, sfx="pop")
T("没聊 → 先找人", 900, R1 + 230, 64, RED, k0=6, k1=7.4, sfx="rim")

scene("吃饭健身，找个搭子", "第二步 · 找搭子", (2650, R1 + 20, 0.85), off=(0, 2300 - R1))
card(2650, R1, "② 找个搭子")
man(2330, R1 + 360, 0.6, "down", "smile", k0=3, k1=3.35, sfx="wood_high")
man(2490, R1 + 360, 0.6, "down", "smile", k0=3.5, k1=3.85)
L(bowl(2760, R1 - 60, 0.4, False), 4, 4.6, BLACK, 7, sfx="wood_high")
T("饭搭子", 3000, R1 - 80, 56, k0=5, k1=5.75, sfx="pop")
L(dumbbell(2760, R1 + 180, 0.45), 6, 6.6, BLACK, 7, sfx="wood_high")
T("健身搭子", 3020, R1 + 180, 56, k0=7, k1=8, sfx="pop")

scene("想点夜宵，先找人聊", "第三步 · 先找人", (2650, R2 + 20, 0.85), off=(0, 1200 - R2))
card(2650, R2, "③ 想吃前先找人")
L(phone(2330, R2 + 10, 170, 290), 3, 3.8, BLACK, 9, sfx="wood_high")
L(bubble(2800, R2 - 90, 380, 120, -1), 4, 4.5, BLACK, 8, sfx="wood_high")
T("在干嘛？", 2800, R2 - 90, 52, k0=4.5, k1=5.0)
L(bubble(2880, R2 + 90, 320, 110, 1), 5, 5.5, BLUE, 8, sfx="pop")
T("刚下班！", 2880, R2 + 90, 50, BLUE, k0=5.5, k1=6.0)
T("聊十分钟再说", 2650, R2 + 300, 52, k0=6, k1=7.5, sfx="pop")
L(check(2960, R2 + 300, 34), 7.5, 8.0, GREEN, 10)

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：拉远看全板，评论区写在板底

scene("评论区聊聊", "评论区见", (1800, 4200, 0.234), bars=4)
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")
T("你一个人时最管不住啥？", 1800, 7550, 230, RED, k0=5, k1=7.75, sfx="pop")
T("下一讲：有人独处挺好，有人一天都熬不住？", 1800, 7900, 140, k0=9, k1=12, sfx="wood_high")
b.hit(len(b.shots) - 1, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "control", "孤独与自控", "一个人的晚上，为什么管不住嘴？", ACC, b.shots,
                 [f"{BOOK}第一部分 · 第 3 章 你的生活正在失控（孤独削弱自我调节，转述）",
                  "中译本：焦梦津译，中国人民大学出版社 2009"],
                 "一个人的晚上|为什么【管不住嘴】", SQUARE_SHOT,
                 ["书中观点均为转述：孤独会削弱自我调节——管住情绪、管住嘴、坚持做事都会变难；书中提到鲍迈斯特（Baumeister）"
                  "等人的实验：让人感到被排斥后，自控表现变差；作者团队还用催眠让同一批人分别体验“孤独”和“有人陪”两种状态，"
                  "孤独时人更消极、更挑剔、社交表现更差。出处：John T. Cacioppo & William Patrick, Loneliness: Human Nature and "
                  "the Need for Social Connection (W. W. Norton, 2008)，中译本《孤独是可耻的》（焦梦津译，中国人民大学出版社 "
                  "2009），第一部分，主要见第 3 章“你的生活正在失控”。上屏均为转述，不是逐字引文。",
                  "实验画面（被接纳 / 被冷落的柱子、自控电量）为对书中结论的通俗化示意，柱高与电量不是实验数据，书中未给出的"
                  "数字一律未上屏。",
                  "深夜点夜宵刷手机、新公司没饭搭子、一个人办健身卡、和家里吵完架狂下单均为现实场景示意，不指向"
                  "任何具体公司或个人；时间、次数、单数为示意。",
                  "三步做法（别光怪意志力 / 找个搭子 / 想吃前先找人聊几句）为据书中思路整理的建议。"],
                 tags="#自律 #情绪")
    return b.attach(ep)
