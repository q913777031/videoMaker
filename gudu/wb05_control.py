"""05 孤独与自控（白板手绘版）：一个人的晚上，为什么管不住嘴？

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
SQUARE_SHOT = 16

b = Board(size=(3600, 9600))


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


# ---------------------------------------------------------------- 开局：一个人的晚上（镜头 1–6）

b.shot("一个人回到家", "灵魂拷问", view=(950, 850, 0.85))
L(moon(600, 560, 90), 0, 0.6, BLACK, 9, sfx="wood_high")
man(880, 1250, 0.9, "down", "flat", k0=1, sfx="pop")
L(door(1330, 1060), 2, 2.6, BLACK, 9, sfx="wood_low")
T("22:30", 1330, 600, 72, RED, k0=3, sfx="pop")

b.shot("先点个夜宵", "灵魂拷问", view=(2650, 850, 0.85))
L(rect(2330, 900, 240, 420, 26), 0, 0.6, BLACK, 9, sfx="wood_high")
T("外卖", 2330, 820, 56, k0=0.6)
L(bowl(2860, 1000, 1.0), 1, 1.8, BLACK, 9, sfx="pop")
T("炸鸡 + 奶茶", 2700, 560, 66, RED, k0=2, sfx="pop")
L(check(2330, 980, 50), 3, 3.3, GREEN, 11, sfx="ding")

b.shot("说好只刷一会儿", "灵魂拷问", view=(950, 1750, 0.85))
man(720, 2150, 0.9, "hold", "smile", k0=0, sfx="wood_high")
L(phone(845, 1940), 0.75, 1.0, BLUE, 8)
L(clock(1300, 1520, 120), 1, 1.6, BLACK, 9, sfx="pop")
L(hands_at(1300, 1520, 120, 23, 0), 1.6, 1.8, BLACK, 10)
T("23:00", 1300, 1720, 56, k0=1.8, k1=2.0)
L(bubble(1240, 1980, 400, 130, -1), 2, 2.5, BLACK, 8, sfx="wood_high")
T("就刷 10 分钟", 1240, 1980, 52, k0=3, sfx="pop")

b.shot("一抬头两点了", "灵魂拷问", view=(950, 1750, 0.85))
b.erase(len(b.shots) - 1, 0, 0.6, 1300, 1600, 320, 330)
H(0, "shaker")
L(clock(1300, 1520, 120), 1, 1.5, BLACK, 9, sfx="wood_high")
L(hands_at(1300, 1520, 120, 2, 0), 1.5, 1.7, RED, 12)
T("02:00", 1300, 1720, 64, RED, k0=2, sfx="pop")
T("！", 1490, 1400, 100, RED, k0=3, sfx="rim")

b.shot("计划又没做", "灵魂拷问", view=(2650, 1750, 0.85))
L(doc(2480, 1760, 460, 620, 0), 0, 0.5, BLACK, 9, sfx="wood_high")
T("今晚计划", 2450, 1540, 58, k0=0.5)
for n, w in enumerate(("跑步", "看书", "早睡")):
    T(w, 2400, 1680 + n * 140, 58, k0=0.6 + n * 0.12, k1=0.9 + n * 0.12)
    L(cross(2580, 1680 + n * 140, 36), 1 + n, 1.3 + n, RED, 10, sfx="rim")
man(3060, 2150, 0.8, "down", "sad", k0=3.3, k1=3.7)

b.shot("为啥管不住自己？", "灵魂拷问", view=(1800, 1300, 0.42), flashes=[0])
T("？", 1800, 1300, 380, RED, k0=0, k1=0.6, sfx="kick")
T("又没管住", 1800, 2380, 110, k0=1.0, k1=2.0, sfx="pop")
H(2, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "孤独是可耻的", view=(1050, 2950, 0.85))
L(book(760, 3010, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 1050, 2620, 80, GREEN, k0=1.0, sfx="pop")
T("约翰 · 卡乔波", 760, 3250, 50, k0=2.0, sfx="pop")
H(3, "ding", 0.6)

b.shot("人孤单的时候", "书中观点 · 孤独", view=(1050, 2950, 0.85))
man(1400, 3200, 0.65, "down", "sad", k0=0, sfx="wood_high")
T("孤单", 1400, 2860, 60, BLUE, k0=1, sfx="pop")
T("第三章 · 失控", 1050, 2730, 46, k0=2, sfx="pop")

b.shot("自控会变弱", "书中观点 · 自控变弱", view=(1050, 3000, 0.85), shake=[0], flashes=[0])
T("自控变弱", 980, 3420, 150, RED, k0=0, k1=0.5, sfx="kick")
L(arrow((1460, 3290), (1460, 3490), 0, 44), 2, 2.4, RED, 11, sfx="ding")
H(3, "tom", 0.7)

b.shot("先让人被冷落", "书中观点 · 被排斥实验", view=(2650, 3000, 0.85))
T("鲍迈斯特等人的实验", 2480, 2530, 50, k0=0, sfx="pop")
for n, x in enumerate((2200, 2350, 2500)):
    man(x, 2960, 0.55, "down", "smile", k0=1 + n * 0.3, k1=1.25 + n * 0.3, sfx="wood_high" if n == 0 else None)
man(3060, 2960, 0.55, "down", "sad", k0=2, k1=2.4, color=RED, sfx="pop")
T("被冷落", 3060, 2700, 54, RED, k0=3, sfx="rim")

b.shot("再测他的自控", "书中观点 · 被排斥实验", view=(2650, 3000, 0.85))
T("测：能撑多久", 2650, 3070, 52, k0=0, sfx="pop")
L(P((2200, 3420), (3200, 3420)), 0.8, 1.0, BLACK, 8)
L(rect(2450, 3280, 140, 280, 8), 1, 1.5, BLUE, 9, sfx="wood_high")
T("被接纳", 2450, 3480, 46, BLUE, k0=2, sfx="pop")

b.shot("被冷落的更差", "书中观点 · 自控变差", view=(2650, 3000, 0.85))
L(rect(2850, 3365, 140, 110, 8), 0, 0.4, RED, 9, sfx="pop")
T("被冷落", 2850, 3480, 46, RED, k0=0.5)
L(arrow((3130, 3170), (3130, 3300), 0, 32), 1, 1.3, RED, 9, sfx="rim")
T("更差", 3130, 3360, 56, RED, k0=2, sfx="ding")

b.shot("还有个催眠实验", "书中观点 · 催眠实验", view=(950, 3950, 0.85))
L(spiral(560, 3700, 100), 0, 0.8, BLUE, 8, sfx="wood_high")
T("催眠", 560, 3870, 56, BLUE, k0=1, sfx="pop")
T("同一批人", 1130, 3680, 60, k0=2, sfx="pop")
L(arrow((1060, 3760), (700, 4010), 0.06, 36), 3, 3.4, GREEN, 8, sfx="wood_high")
L(arrow((1200, 3760), (1330, 4010), -0.06, 36), 3.4, 3.8, GREEN, 8)

b.shot("孤单时更挑剔", "书中观点 · 孤单时", view=(950, 3950, 0.85))
T("孤单", 600, 4090, 54, BLUE, k0=0, sfx="pop")
man(600, 4400, 0.6, "down", "sad", k0=1, sfx="wood_high")
T("更消极", 880, 4260, 50, RED, k0=2, sfx="pop")
T("更挑剔", 880, 4350, 50, RED, k0=3, sfx="rim")

b.shot("有人陪就好多了", "书中观点 · 有人陪", view=(950, 3950, 0.85))
T("有人陪", 1330, 4090, 54, GREEN, k0=0, sfx="pop")
man(1250, 4400, 0.6, "down", "smile", k0=1, k1=1.4, sfx="wood_high")
man(1420, 4400, 0.6, "down", "smile", k0=1.5, k1=1.9)
L(check(1500, 4085, 36), 2, 2.3, GREEN, 10, sfx="ding")
H(3, "pop", 0.6)

BAT = (2950, 3800)
b.shot("孤单拖垮自控", "书中观点 · 一张图", view=(2650, 3950, 0.85))
man(2250, 4060, 0.6, "down", "sad", k0=0, sfx="wood_high")
T("孤单", 2250, 3720, 60, BLUE, k0=1, sfx="pop")
L(arrow((2370, 3800), (2760, 3800), 0.05, 40), 2, 2.4, BLACK, 9, sfx="wood_high")
L(battery(*BAT), 2.4, 2.9, BLACK, 9)
T("自控", BAT[0], 3660, 60, k0=2.9, k1=3.0)
b.custom(len(b.shots) - 1, 3, 4, drain(*BAT), sfx="shaker")

b.shot("嘴就管不住了", "书中观点 · 一张图", view=(2650, 3950, 0.85))
for n, (x, w) in enumerate(((2450, "夜宵"), (2760, "刷手机"), (3120, "计划泡汤"))):
    L(arrow((BAT[0] - 40 + n * 40, 3880), (x, 4250), 0.04 * (1 - n), 30), n, n + 0.35, RED, 8,
      sfx=("pop", "pop", "rim")[n])
    T(w, x, 4320, 56, RED, k0=n + 0.4, k1=n + 0.9)
L(underline(2380, 3240, 4380, 10, 34), 3, 3.4, RED, 7, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 5300), (2650, 5300), (950, 6250), (2650, 6250)]
b.shot("身边也常见", "身边的例子", view=(1800, 5775, 0.355))
T("身边的例子", 1800, 4720, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 860, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("新公司没饭搭子", "例子 · 职场", view=(950, 5300, 0.85))
T("12:00 午饭", 620, 5010, 58, RED, k0=0, sfx="pop")
man(620, 5600, 0.7, "hold", "flat", k0=1, sfx="wood_high")
L(bowl(760, 5400, 0.45, False), 1.8, 2.0, BLACK, 7)
for n, x in enumerate((1150, 1290, 1430)):
    man(x, 5600, 0.55, "down", "smile", k0=2 + n * 0.3, k1=2.25 + n * 0.3, sfx="pop" if n == 0 else None)
T("一个人吃", 620, 5670, 46, k0=3, sfx="rim")

b.shot("下午活都拖着", "例子 · 职场", view=(950, 5300, 0.85))
L(doc(980, 5160, 120, 150, 3), 0, 0.4, BLACK, 8, sfx="wood_high")
T("报告 0 字", 980, 5300, 46, RED, k0=1, sfx="pop")
T("拖", 1380, 5150, 100, RED, k0=2, k1=2.4, sfx="rim")
H(3, "tom", 0.6)

b.shot("一个人去健身", "例子 · 生活", view=(2650, 5300, 0.85))
T("办了年卡", 2620, 5010, 58, k0=0, sfx="pop")
L(dumbbell(2300, 5260, 0.9), 1, 1.6, BLACK, 9, sfx="wood_high")
man(2620, 5620, 0.75, "up", "smile", k0=2, sfx="pop")
T("一个人", 2620, 5690, 46, k0=3, sfx="rim")

b.shot("去两次就停了", "例子 · 生活", view=(2650, 5300, 0.85))
T("第 1 周：2 次", 3020, 5210, 48, k0=0, sfx="pop")
T("第 2 周：0 次", 3020, 5320, 48, RED, k0=1, sfx="rim")
T("第 3 周：0 次", 3020, 5430, 48, RED, k0=2, sfx="rim")
L(cross(2300, 5260, 90), 3, 3.3, RED, 11, sfx="rim")

b.shot("和家里吵完架", "例子 · 家庭", view=(950, 6250, 0.85))
man(500, 6560, 0.6, "point", "sad", k0=0, sfx="wood_high")
man(760, 6560, 0.6, "shrug", "sad", k0=1, sfx="pop")
T("吵", 630, 6070, 100, RED, k0=2, k1=2.3, sfx="rim")
L(arrow((880, 6300), (1030, 6300), 0, 30), 3, 3.3, BLACK, 8, sfx="wood_high")

b.shot("下单停不下来", "例子 · 家庭", view=(950, 6250, 0.85))
man(1140, 6600, 0.7, "hold", "flat", k0=0, sfx="wood_high")
L(phone(1237, 6437, 60, 100), 0.7, 0.9, BLUE, 7)
L(boxes(1420, 6600, 3), 1, 1.8, BLACK, 8, sfx="pop")
T("下单 ×8", 1250, 6080, 58, RED, k0=2, sfx="pop")
H(3, "ding", 0.6)

b.shot("放假一个人在家", "例子 · 生活", view=(2650, 6250, 0.85))
T("放假，室友都回家", 2650, 6000, 54, k0=0, sfx="pop")
L(sofa(2450, 6480, 420), 1, 1.7, BLACK, 8, sfx="wood_high")
man(2450, 6530, 0.6, "down", "flat", k0=2, sfx="pop")
T("一天没说话", 2990, 6170, 50, BLUE, k0=3, sfx="rim")

b.shot("看什么都烦", "例子 · 生活", view=(2650, 6250, 0.85))
L(scribble(2450, 6090, 150, 70, 6), 0, 0.4, RED, 7, sfx="shaker")
T("剧太烂", 2990, 6300, 50, RED, k0=1, sfx="pop")
T("外卖太慢", 2990, 6410, 50, RED, k0=2, sfx="pop")
T("群消息好吵", 2990, 6520, 50, RED, k0=3, sfx="pop")

b.shot("都是一个人时", "身边的例子", view=(1800, 5775, 0.355))
for n, (x, y) in enumerate(CARDS):
    T("一个人", x + 400, y - 345, 90, RED, k0=n, sfx="pop")

b.shot("背后都是孤单", "身边的例子", view=(1800, 5775, 0.355), shake=[0])
T("一孤单，就管不住", 1800, 6820, 120, RED, k0=0, k1=0.8, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 7700), (2650, 7700), (950, 8650), (2650, 8650)]
b.shot("那该怎么办", "具体做法", view=(1800, 8175, 0.355))
T("晚上管住自己：四步", 1800, 7110, 120, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 860, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("别光怪意志力", "第一步 · 别光怪自己", view=(950, 7700, 0.85))
T("① 别光怪意志力", 950, 7400, 72, BLUE, k0=0, sfx="pop")
T("意志力", 720, 7620, 80, k0=1, sfx="pop")
L(cross(720, 7620, 80), 2, 2.3, RED, 11, sfx="rim")
H(3, "tom", 0.6)

b.shot("先问今天聊过没", "第一步 · 别光怪自己", view=(950, 7700, 0.85))
T("今天跟人聊过天？", 1040, 7760, 56, k0=0, sfx="pop")
man(1320, 8100, 0.5, "shrug", "flat", k0=1, sfx="wood_high")
T("没聊 → 先找人", 900, 7930, 56, RED, k0=2, sfx="pop")
L(underline(720, 1080, 7985, 10, 30), 3, 3.3, RED, 7, sfx="ding")

b.shot("找个搭子", "第二步 · 找搭子", view=(2650, 7700, 0.85))
T("② 找个搭子", 2650, 7400, 72, BLUE, k0=0, sfx="pop")
man(2330, 8060, 0.6, "down", "smile", k0=1, k1=1.4, sfx="wood_high")
man(2490, 8060, 0.6, "down", "smile", k0=1.5, k1=1.9)
T("搭子", 2410, 7760, 60, GREEN, k0=2, sfx="pop")
H(3, "ding", 0.6)

b.shot("午饭约个同事", "第二步 · 饭搭子", view=(2650, 7700, 0.85))
L(bowl(2760, 7640, 0.4, False), 0, 0.4, BLACK, 7, sfx="wood_high")
T("饭搭子", 2990, 7600, 56, k0=1, sfx="pop")
T("约同事吃午饭", 2950, 7720, 46, k0=2, sfx="pop")
L(check(3190, 7720, 32), 3, 3.3, GREEN, 10, sfx="ding")

b.shot("健身约上朋友", "第二步 · 健身搭子", view=(2650, 7700, 0.85))
L(dumbbell(2760, 7880, 0.45), 0, 0.4, BLACK, 7, sfx="wood_high")
T("健身搭子", 3020, 7880, 56, k0=1, sfx="pop")
T("每周二、四一起练", 2930, 8000, 46, k0=2, sfx="pop")
L(check(3200, 8000, 32), 3, 3.3, GREEN, 10, sfx="ding")

b.shot("晚上排点有人的事", "第三步 · 排上人", view=(950, 8650, 0.85))
T("③ 晚上排上人", 950, 8350, 72, BLUE, k0=0, sfx="pop")
L(grid(500, 8620), 1, 1.8, BLACK, 8, sfx="wood_high")
T("一   二   三   四   五", 950, 8490, 46, k0=2, k1=2.8, sfx="pop")

b.shot("周三去打球", "第三步 · 排上人", view=(950, 8650, 0.85))
L(circle(950, 8620, 78), 0, 0.4, GREEN, 8, sfx="pop")
T("羽毛球", 950, 8620, 46, k0=1, sfx="pop")
T("和同事", 950, 8790, 46, k0=2, sfx="pop")

b.shot("周五跟朋友视频", "第三步 · 排上人", view=(950, 8650, 0.85))
T("视频", 1310, 8620, 46, k0=0, sfx="pop")
T("20:00", 1310, 8790, 46, RED, k0=1, sfx="pop")
L(circle(1310, 8620, 78), 2, 2.4, GREEN, 8, sfx="ding")

b.shot("想点夜宵先发消息", "第四步 · 先找人", view=(2650, 8650, 0.85))
T("④ 想吃前先找人", 2650, 8350, 72, BLUE, k0=0, sfx="pop")
L(phone(2330, 8660, 170, 290), 1, 1.5, BLACK, 9, sfx="wood_high")
L(bubble(2800, 8560, 380, 120, -1), 2, 2.4, BLACK, 8, sfx="pop")
T("在干嘛？", 2800, 8560, 52, k0=3, sfx="pop")

b.shot("聊完再决定点不点", "第四步 · 先找人", view=(2650, 8650, 0.85))
L(bubble(2880, 8740, 320, 110, 1), 0, 0.4, BLUE, 8, sfx="pop")
T("刚下班！", 2880, 8740, 50, BLUE, k0=0.5)
T("聊 10 分钟再说", 2650, 8950, 52, k0=1, sfx="pop")
L(check(2960, 8950, 34), 2, 2.3, GREEN, 10, sfx="ding")

b.shot("照着试试", "具体做法", view=(1800, 8175, 0.355))
for n, (x, y) in enumerate(SOL):
    L(check(x + 500, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 else "pop")

b.shot("先补人，再管嘴", "一句话", view=(1800, 4300, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 9350, 0.8))
T("你一个人时最管不住啥？", 1800, 9270, 72, RED, k0=0.5, k1=1.8)
T("下一讲：有人独处挺好，有人一天都熬不住？", 1800, 9420, 46, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "control", "孤独与自控", "一个人的晚上，为什么管不住嘴？", ACC, b.shots,
                 [f"{BOOK}第一部分 · 第 3 章 你的生活正在失控（孤独削弱自我调节，转述）",
                  "中译本：焦梦津译，中国人民大学出版社 2009"],
                 "一个人的晚上|为什么【管不住嘴】", 16,
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
