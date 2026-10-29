"""05 孤独与自控（白板手绘版）：一个人的晚上，为什么管不住嘴？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。

叙事：打工人切身问题开局（加完班一个人到家 → 点夜宵 → 说好只刷一会儿 → 一抬头两点 → 计划又没做）→ 书中观点
（亮书《孤独是可耻的》、卡乔波；孤独削弱自我调节——管情绪、管嘴、坚持做事；被排斥实验里被冷落的人自控表现变差；
催眠让同一批人分别体验“孤单”和“有人陪”，孤单时更消极、更挑剔；画成“孤单 → 自控电量往下掉 → 夜宵 / 刷手机 /
计划泡汤”一张图）→ 身边的例子（新公司没饭搭子下午拖活、一个人办健身卡去两次就停、和家里吵完架狂下单、放假一个人
在家看什么都烦；最后连到“一孤单，就管不住”）→ 具体做法（别光怪意志力 / 找个搭子 / 晚上排上有人的事 / 想吃前先找人
聊几句）→ 评论区互动。
书中观点为转述（John T. Cacioppo & William Patrick, Loneliness: Human Nature and the Need for Social Connection,
W. W. Norton 2008；中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009，第一部分，主要见第 3 章“你的生活正在
失控”）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, cross,
                               doc, face, hands_at, join, rect, scribble, stick, underline)

from .common import BOOK, episode

ACC = "#6B5B95"
SQUARE_SHOT = 8

b = Board(size=(3600, 10400))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    k1 = k0 + max(0.5, 0.18 * len(s)) if k1 is None else k1
    b.text(len(b.shots) - 1, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


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


def sofa(x, y, w=420) -> skia.Path:
    """沙发（正视）：(x, y) 为坐垫中点。"""
    return join(rect(x, y - 110, w - 60, 160, 20), rect(x, y + 20, w, 100, 20), rect(x - w / 2 + 20, y - 20, 50, 200, 14),
                rect(x + w / 2 - 20, y - 20, 50, 200, 14), P((x - w / 2 + 30, y + 70), (x - w / 2 + 30, y + 120)),
                P((x + w / 2 - 30, y + 70), (x + w / 2 - 30, y + 120)))


def grid(x0, y, n=5, cw=180, ch=160) -> skia.Path:
    return join(*[rect(x0 + cw / 2 + i * cw, y, cw, ch, 6) for i in range(n)])


# ---------------------------------------------------------------- 开局：一个人的晚上（场景 1–3）
# 每个场景 2 小节（8 拍，≈4.3 秒）：第 0–6 拍画完，最后 2 拍停住让人看清。

def scene(text, tag, view, **kw):
    return b.shot(text, tag, view=view, bars=2, **kw)


scene("一个人到家，先点夜宵", "灵魂拷问", (950, 850, 0.85))
L(moon(480, 560, 80), 0, 0.6, BLACK, 9, sfx="wood_high")
T("22:30", 820, 560, 72, RED, k0=0.6, k1=1.0)
L(door(480, 1050), 1, 1.5, BLACK, 9, sfx="wood_low")
man(760, 1240, 0.85, "down", "flat", k0=1.6, k1=2.1)
L(rect(1180, 1030, 220, 360, 24), 2, 2.5, BLACK, 9, sfx="wood_high")
T("外卖", 1180, 960, 52, k0=2.5, k1=2.9)
L(bowl(1400, 1150, 0.7), 3, 3.7, BLACK, 8, sfx="pop")
T("炸鸡 + 奶茶", 1280, 720, 62, RED, k0=4, k1=4.9, sfx="pop")
L(check(1180, 1080, 45), 5, 5.3, GREEN, 11, sfx="ding")

scene("说好刷一会，刷到两点", "灵魂拷问", (950, 1950, 0.85))
man(720, 2150, 0.9, "hold", "smile", k0=0, sfx="wood_high")
L(phone(845, 1940), 0.75, 1.0, BLUE, 8)
L(clock(1300, 1520, 120), 1, 1.5, BLACK, 9, sfx="pop")
L(hands_at(1300, 1520, 120, 23, 0), 1.5, 1.7, BLACK, 10)
T("23:00", 1300, 1720, 56, k0=1.7, k1=1.95)
L(bubble(1240, 1980, 400, 130, -1), 2, 2.4, BLACK, 8, sfx="wood_high")
T("就刷 10 分钟", 1240, 1980, 52, k0=2.4, k1=3.0)
b.erase(len(b.shots) - 1, 3, 3.5, 1300, 1600, 320, 330)
H(3, "shaker")
L(clock(1300, 1520, 120), 4, 4.4, BLACK, 9, sfx="wood_high")
L(hands_at(1300, 1520, 120, 2, 0), 4.4, 4.6, RED, 12)
T("02:00", 1300, 1720, 64, RED, k0=5, k1=5.4, sfx="pop")
T("！", 1450, 1420, 100, RED, k0=5.4, k1=5.7)

scene("计划又没做，为啥？", "灵魂拷问", (2650, 1750, 0.85), shake=[4], flashes=[4])
L(doc(2480, 1760, 460, 620, 0), 0, 0.5, BLACK, 9, sfx="wood_high")
T("今晚计划", 2450, 1540, 58, k0=0.5, k1=0.9)
for n, w in enumerate(("跑步", "看书", "早睡")):
    T(w, 2400, 1680 + n * 140, 58, k0=0.6 + n * 0.12, k1=0.9 + n * 0.12)
    L(cross(2580, 1680 + n * 140, 36), 1 + n, 1.3 + n, RED, 10, sfx="rim")
man(2960, 2150, 0.8, "down", "sad", k0=3.3, k1=3.7)
T("？", 3060, 1620, 240, RED, k0=4, k1=4.4, sfx="kick")
T("为啥管不住自己？", 2650, 1300, 80, RED, k0=5, k1=5.9, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 4–9）

scene("有本书专讲这个", "孤独是可耻的", (1050, 2950, 0.85))
L(book(760, 3010, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 1050, 2620, 80, GREEN, k0=1.0, k1=2.0, sfx="pop")
T("约翰 · 卡乔波", 760, 3250, 50, k0=2.0, k1=2.9, sfx="pop")
T("第三章 · 失控", 1050, 2730, 46, k0=3, k1=3.8, sfx="pop")
man(1400, 3200, 0.65, "down", "sad", k0=4, sfx="wood_high")
T("孤单", 1400, 2860, 60, BLUE, k0=5, k1=5.4, sfx="pop")

scene("孤单时，自控会变弱", "书中观点 · 自控变弱", (1050, 3080, 0.85), shake=[0], flashes=[0])
T("自控变弱", 980, 3420, 150, RED, k0=0, k1=0.5, sfx="kick")
T("管情绪 · 管住嘴 · 坚持做事", 980, 3560, 44, k0=2, k1=3.8, sfx="tom")
L(arrow((590, 3330), (590, 3500), 0, 40), 4, 4.4, RED, 11, sfx="ding")

scene("先让一个人被冷落", "书中观点 · 被排斥实验", (2650, 3000, 0.85))
T("鲍迈斯特等人的实验", 2480, 2530, 50, k0=0, k1=1.0, sfx="pop")
for n, x in enumerate((2200, 2350, 2500)):
    man(x, 2960, 0.55, "down", "smile", k0=1 + n * 0.3, k1=1.25 + n * 0.3, sfx="wood_high" if n == 0 else None)
man(3060, 2960, 0.55, "down", "sad", k0=2, k1=2.4, color=RED, sfx="pop")
T("被冷落", 3060, 2700, 54, RED, k0=3, k1=3.5, sfx="rim")

scene("被冷落的，自控更差", "书中观点 · 自控变差", (2650, 3000, 0.85))
T("测：能撑多久", 2650, 3070, 52, k0=0, k1=0.8, sfx="pop")
L(P((2200, 3420), (3200, 3420)), 0.8, 1.0, BLACK, 8)
L(rect(2450, 3280, 140, 280, 8), 1, 1.5, BLUE, 9, sfx="wood_high")
T("被接纳", 2450, 3480, 46, BLUE, k0=1.5, k1=2.0)
L(rect(2850, 3365, 140, 110, 8), 2, 2.4, RED, 9, sfx="pop")
T("被冷落", 2850, 3480, 46, RED, k0=2.4, k1=2.9)
L(arrow((3130, 3170), (3130, 3300), 0, 32), 3, 3.3, RED, 9, sfx="rim")
T("更差", 3130, 3360, 56, RED, k0=4, k1=4.5, sfx="ding")

scene("同一批人，孤单更挑剔", "书中观点 · 催眠实验", (950, 4450, 0.85))
L(spiral(560, 3980, 100), 0, 0.7, BLUE, 8, sfx="wood_high")
T("催眠", 560, 4150, 56, BLUE, k0=0.7, k1=1.0)
T("同一批人", 1130, 3960, 60, k0=1, k1=1.7, sfx="pop")
L(arrow((1060, 4040), (700, 4290), 0.06, 36), 2, 2.3, GREEN, 8, sfx="wood_high")
L(arrow((1200, 4040), (1330, 4290), -0.06, 36), 2.3, 2.6, GREEN, 8)
man(600, 4680, 0.6, "down", "sad", k0=3, k1=3.4, sfx="pop")
T("孤单", 600, 4370, 54, BLUE, k0=3.55, k1=3.9)
T("更消极", 880, 4540, 50, RED, k0=4, k1=4.4, sfx="rim")
T("更挑剔", 880, 4630, 50, RED, k0=4.4, k1=4.8)
man(1250, 4680, 0.6, "down", "smile", k0=5, k1=5.3, sfx="ding")
man(1420, 4680, 0.6, "down", "smile", k0=5.3, k1=5.55)
T("有人陪", 1330, 4370, 54, GREEN, k0=5.6, k1=6.0)

BAT = (2950, 4070)
scene("孤单拖垮自控", "书中观点 · 一张图", (2650, 4450, 0.85))
man(2250, 4330, 0.6, "down", "sad", k0=0, sfx="wood_high")
T("孤单", 2250, 3990, 60, BLUE, k0=1, k1=1.4, sfx="pop")
L(arrow((2370, 4070), (2760, 4070), 0.05, 40), 2, 2.4, BLACK, 9, sfx="wood_high")
L(battery(*BAT), 2.4, 2.8, BLACK, 9)
T("自控", BAT[0], 3930, 60, k0=2.8, k1=3.0)
b.custom(len(b.shots) - 1, 3, 3.4, drain(*BAT), sfx="shaker")
for n, (x, w, k) in enumerate(((2450, "夜宵", 4), (2760, "刷手机", 4.5), (3120, "计划泡汤", 5))):
    L(arrow((BAT[0] - 40 + n * 40, 4150), (x, 4520), 0.04 * (1 - n), 30), k, k + 0.3, RED, 8,
      sfx=("pop", None, "rim")[n])
    T(w, x, 4590, 56, RED, k0=k + 0.3, k1=k + 0.6)
L(P((3240, 4660), (2380, 4660)), 5.6, 6.0, RED, 7)     # 从右往左画，手停在左边，不挡字

# ---------------------------------------------------------------- 身边的例子（场景 10–15）

CARDS = [(950, 5500), (2650, 5500), (950, 6450), (2650, 6450)]
scene("身边也常见", "身边的例子", (1800, 6150, 0.355))
T("身边的例子", 1800, 4920, 130, k0=0, k1=0.9, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 1 + n, 1.45 + n, GREEN, 8, sfx="wood_high")

scene("没饭搭子，下午就拖", "例子 · 职场", (950, 5500, 0.85))
T("12:00 午饭", 620, 5210, 58, RED, k0=0, k1=0.8, sfx="pop")
man(620, 5800, 0.7, "hold", "flat", k0=1, sfx="wood_high")
L(bowl(760, 5600, 0.45, False), 1.8, 2.0, BLACK, 7)
for n, x in enumerate((1150, 1290, 1430)):
    man(x, 5800, 0.55, "down", "smile", k0=2 + n * 0.3, k1=2.25 + n * 0.3, sfx="pop" if n == 0 else None)
T("一个人吃", 620, 5870, 46, k0=3, k1=3.5, sfx="rim")
L(doc(980, 5360, 120, 150, 3), 3.5, 3.9, BLACK, 8)
T("报告 0 字", 980, 5500, 46, RED, k0=4, k1=4.6, sfx="pop")
T("拖", 1380, 5350, 100, RED, k0=5, k1=5.4, sfx="rim")

scene("一个人健身，两次就停", "例子 · 健身", (2650, 5500, 0.85))
T("办了年卡", 2620, 5210, 58, k0=0, k1=0.7, sfx="pop")
L(dumbbell(2300, 5460, 0.9), 1, 1.6, BLACK, 9, sfx="wood_high")
man(2620, 5820, 0.75, "up", "smile", k0=2, sfx="pop")
T("一个人", 2620, 5890, 46, k0=3, k1=3.5, sfx="rim")
T("第 1 周：2 次", 3020, 5410, 48, k0=4, k1=4.3, sfx="pop")
T("第 2 周：0 次", 3020, 5520, 48, RED, k0=4.3, k1=4.6)
T("第 3 周：0 次", 3020, 5630, 48, RED, k0=4.6, k1=4.9)
L(cross(2300, 5460, 90), 5, 5.3, RED, 11, sfx="rim")

scene("吵完架，就狂下单", "例子 · 家庭", (950, 6450, 0.85))
man(500, 6760, 0.6, "point", "sad", k0=0, sfx="wood_high")
man(760, 6760, 0.6, "shrug", "sad", k0=1, sfx="pop")
T("吵", 630, 6270, 100, RED, k0=2, k1=2.3, sfx="rim")
L(arrow((880, 6500), (1030, 6500), 0, 30), 2.5, 2.8, BLACK, 8)
man(1140, 6800, 0.7, "hold", "flat", k0=3, sfx="wood_high")
L(phone(1237, 6637, 60, 100), 3.8, 4.0, BLUE, 7)
L(boxes(1420, 6800, 3), 4, 4.8, BLACK, 8, sfx="pop")
T("下单 ×8", 1250, 6280, 58, RED, k0=5, k1=5.5, sfx="pop")

scene("放假一个人，看啥都烦", "例子 · 放假", (2650, 6450, 0.85))
T("放假，室友都回家", 2650, 6200, 54, k0=0, k1=1.0, sfx="pop")
L(sofa(2450, 6680, 420), 1, 1.6, BLACK, 8, sfx="wood_high")
man(2450, 6730, 0.6, "down", "flat", k0=2, sfx="pop")
T("一天没说话", 2990, 6370, 50, BLUE, k0=3, k1=3.6, sfx="rim")
L(scribble(2450, 6290, 150, 70, 6), 3.6, 4.0, RED, 7)
T("剧太烂", 2990, 6500, 50, RED, k0=4, k1=4.4, sfx="pop")
T("外卖太慢", 2990, 6610, 50, RED, k0=4.5, k1=5.0)
T("群消息好吵", 2990, 6720, 50, RED, k0=5, k1=5.6, sfx="pop")

scene("一孤单，就管不住", "身边的例子", (1800, 6150, 0.355), shake=[4])
for n, (x, y) in enumerate(CARDS):
    T("一个人", x + 400, y - 345, 90, RED, k0=n, k1=n + 0.5, sfx="pop")
T("一孤单，就管不住", 1800, 7000, 100, RED, k0=4, k1=4.8, sfx="kick")
H(5, "ding")

# ---------------------------------------------------------------- 具体做法（场景 16–19）

R1, R2 = 7750, 8700
SOL = [(950, R1), (2650, R1), (950, R2), (2650, R2)]


def card(n, title, size=72):
    x, y = SOL[n]
    L(rect(x, y, 1200, 860, 40), 0, 0.5, GREEN, 8, sfx="wood_high")
    T(title, x, y - 290, size, BLUE, k0=1, k1=1.8, sfx="pop")


scene("先别怪意志力", "第一步 · 别光怪自己", (950, R1 + 240, 0.85))
card(0, "① 别光怪意志力")
T("意志力", 720, R1 - 80, 80, k0=2, k1=2.5, sfx="pop")
L(cross(720, R1 - 80, 80), 3, 3.3, RED, 11, sfx="rim")
T("今天跟人聊过天？", 1040, R1 + 60, 56, k0=3.3, k1=4.0)
man(1320, R1 + 400, 0.5, "shrug", "flat", k0=4, k1=4.4, sfx="wood_high")
T("没聊 → 先找人", 900, R1 + 230, 56, RED, k0=5, k1=5.6, sfx="pop")
L(underline(720, 1080, R1 + 285, 10, 30), 5.6, 5.9, RED, 7)

scene("吃饭健身，找个搭子", "第二步 · 找搭子", (2650, R1 + 240, 0.85))
card(1, "② 找个搭子")
man(2330, R1 + 360, 0.6, "down", "smile", k0=2, k1=2.35, sfx="wood_high")
man(2490, R1 + 360, 0.6, "down", "smile", k0=2.4, k1=2.75)
T("搭子", 2410, R1 + 60, 60, GREEN, k0=3, k1=3.4, sfx="pop")
L(bowl(2760, R1 - 60, 0.4, False), 3.5, 3.9, BLACK, 7)
T("饭搭子", 3000, R1 - 80, 56, k0=4, k1=4.5, sfx="pop")
L(dumbbell(2760, R1 + 180, 0.45), 4.5, 4.9, BLACK, 7)
T("健身搭子", 3020, R1 + 180, 56, k0=5, k1=5.6, sfx="pop")

scene("晚上排点有人的事", "第三步 · 排上人", (950, R2 + 240, 0.85))
card(2, "③ 晚上排上人")
L(grid(500, R2 - 30), 2, 2.6, BLACK, 8, sfx="wood_high")
T("一   二   三   四   五", 950, R2 - 160, 46, k0=2.6, k1=3.3)
L(circle(950, R2 - 30, 78), 3.5, 3.9, GREEN, 8)
T("羽毛球", 950, R2 - 30, 46, k0=4, k1=4.4, sfx="pop")
T("和同事", 950, R2 + 140, 46, k0=4.4, k1=4.8)
L(circle(1310, R2 - 30, 78), 5, 5.3, GREEN, 8, sfx="ding")
T("视频", 1310, R2 - 30, 46, k0=5.3, k1=5.6)
T("20:00", 1310, R2 + 140, 46, RED, k0=5.6, k1=6.0)

scene("想点夜宵，先找人聊", "第四步 · 先找人", (2650, R2 + 240, 0.85))
card(3, "④ 想吃前先找人")
L(phone(2330, R2 + 10, 170, 290), 2, 2.5, BLACK, 9, sfx="wood_high")
L(bubble(2800, R2 - 90, 380, 120, -1), 2.5, 2.9, BLACK, 8)
T("在干嘛？", 2800, R2 - 90, 52, k0=3, k1=3.5, sfx="pop")
L(bubble(2880, R2 + 90, 320, 110, 1), 3.6, 4.0, BLUE, 8)
T("刚下班！", 2880, R2 + 90, 50, BLUE, k0=4, k1=4.5, sfx="pop")
T("聊 10 分钟再说", 2650, R2 + 300, 52, k0=5, k1=5.7, sfx="pop")
L(check(2960, R2 + 300, 34), 5.7, 6.0, GREEN, 10)

# ---------------------------------------------------------------- 收尾（场景 20–21）

scene("先补人，再管嘴", "一句话", (1800, 4900, 0.23))
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")

scene("评论区聊聊", "评论区见", (1800, 10000, 0.8))
H(0, "cymbal", 0.5)
T("你一个人时最管不住啥？", 1800, 9920, 72, RED, k0=1, k1=2.6, sfx="pop")
T("下一讲：有人独处挺好，有人一天都熬不住？", 1800, 10070, 46, k0=3, k1=4.5, sfx="wood_high")
b.hit(len(b.shots) - 1, 8, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "control", "孤独与自控", "一个人的晚上，为什么管不住嘴？", ACC, b.shots,
                 [f"{BOOK}第一部分 · 第 3 章 你的生活正在失控（孤独削弱自我调节，转述）",
                  "中译本：焦梦津译，中国人民大学出版社 2009"],
                 "一个人的晚上|为什么【管不住嘴】", 8,
                 ["书中观点均为转述：孤独会削弱自我调节——管住情绪、管住嘴、坚持做事都会变难；书中提到鲍迈斯特（Baumeister）"
                  "等人的实验：让人感到被排斥后，自控表现变差；作者团队还用催眠让同一批人分别体验“孤独”和“有人陪”两种状态，"
                  "孤独时人更消极、更挑剔、社交表现更差。出处：John T. Cacioppo & William Patrick, Loneliness: Human Nature and "
                  "the Need for Social Connection (W. W. Norton, 2008)，中译本《孤独是可耻的》（焦梦津译，中国人民大学出版社 "
                  "2009），第一部分，主要见第 3 章“你的生活正在失控”。上屏均为转述，不是逐字引文。",
                  "实验画面（被接纳 / 被冷落的柱子、自控电量）为对书中结论的通俗化示意，柱高与电量不是实验数据，书中未给出的"
                  "数字一律未上屏。",
                  "深夜点夜宵刷手机、新公司没饭搭子、一个人办健身卡、和家里吵完架狂下单、放假一个人在家均为现实场景示意，不指向"
                  "任何具体公司或个人；时间、次数、单数为示意。",
                  "四步做法（别光怪意志力 / 找个搭子 / 晚上排上有人的事 / 想吃前先找人聊几句）为据书中思路整理的建议。"],
                 tags="#自律 #情绪")
    return b.attach(ep)
