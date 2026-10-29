"""02 感觉不看人数（白板手绘版）：群里几百人，为什么还是孤单？

节奏：21 个场景 × 2 小节（≈4.3 秒），每个场景前 6 拍画完、最后 2 拍停住让人看清（2026-10 观众反馈“切太快看不清”后改版）。
叙事：打工人切身问题开局（工作群几百人、消息刷不停、聚餐坐满一桌，回家心里还是空）→ 书中观点
（亮书《孤独是可耻的》、卡乔波；书里先问“人多就不孤单？”——对不上；孤独看的是心里的感觉、跟谁合得来，和人多人少、
独处多久是两回事；研究里孤单的人和不孤单的人，社交时间、长相、聪明程度差别都不大；画成“感觉 / 关系 / 人数 / 时长”
一张图）→ 身边的例子（工位挨着各刷各的手机、周末饭局散场更空、过年一大家子没人问累不累、一个人住每周和闺蜜长聊反倒
不孤单；最后连到“差在有没有深聊”）→ 具体做法（找一两个说得上话的人 / 把一次饭局换成一次深聊 / 点赞换成一句留言 /
定个固定时间打电话）→ 评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, W. W. Norton,
2008；中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009，第一部分）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, bubble, book, check, circle, clock, cross,
                               desk, face, hands_at, join, rect, stick, underline)

from .common import BOOK, episode

ACC = "#C0574A"
SQUARE_SHOT = 4                 # 场景 5：两个小人说得上话 + 红心“关系好不好”

b = Board(size=(3600, 10300))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


# ---------------------------------------------------------------- 本讲画法

def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, max(12, w * 0.1)), P((x - w * 0.12, y + h / 2 - h * 0.08), (x + w * 0.12, y + h / 2 - h * 0.08)))


def heart(x, y, r=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r)
    p.cubicTo(x - 1.7 * r, y - 0.1 * r, x - 0.7 * r, y - 1.3 * r, x, y - 0.45 * r)
    p.cubicTo(x + 0.7 * r, y - 1.3 * r, x + 1.7 * r, y - 0.1 * r, x, y + r)
    return p


def bust(x, y, r=40) -> skia.Path:
    """头 + 肩（围坐的人）：(x, y) 为头心。"""
    p = skia.Path()
    p.moveTo(x - 1.7 * r, y + 2.6 * r)
    p.quadTo(x - 1.6 * r, y + 1.2 * r, x, y + 1.15 * r)
    p.quadTo(x + 1.6 * r, y + 1.2 * r, x + 1.7 * r, y + 2.6 * r)
    return join(circle(x, y, r), p)


def oval(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def eq(x, y, w=70, neq=False, approx=False) -> skia.Path:
    """等号 / 不等号 / 约等号（画出来，手写字体没有这几个符号）。"""
    parts = []
    for dy in (-16, 16):
        if approx:
            q = skia.Path()
            q.moveTo(x - w / 2, y + dy + 4)
            q.quadTo(x - w / 4, y + dy - 18, x, y + dy)
            q.quadTo(x + w / 4, y + dy + 18, x + w / 2, y + dy - 4)
            parts.append(q)
        else:
            parts.append(P((x - w / 2, y + dy), (x + w / 2, y + dy)))
    if neq:
        parts.append(P((x + w * 0.25, y - 45), (x - w * 0.25, y + 45)))
    return join(*parts)


def cup(x, y, s=1.0) -> skia.Path:
    body = P((x - 40 * s, y - 50 * s), (x - 32 * s, y + 50 * s), (x + 32 * s, y + 50 * s), (x + 40 * s, y - 50 * s),
             close=True)
    handle = skia.Path()
    handle.addArc(skia.Rect.MakeXYWH(x + 20 * s, y - 30 * s, 40 * s, 46 * s), -90, 180)
    st = skia.Path()
    st.moveTo(x, y - 65 * s)
    st.quadTo(x - 15 * s, y - 85 * s, x, y - 100 * s)
    st.quadTo(x + 15 * s, y - 115 * s, x, y - 130 * s)
    return join(body, handle, st)


def calendar(x, y, w=300, h=260) -> skia.Path:
    parts = [rect(x, y, w, h, 14), P((x - w / 2, y - h / 2 + 60), (x + w / 2, y - h / 2 + 60)),
             P((x - w / 4, y - h / 2 - 25), (x - w / 4, y - h / 2 + 25)),
             P((x + w / 4, y - h / 2 - 25), (x + w / 4, y - h / 2 + 25))]
    for i in range(1, 3):
        yy = y - h / 2 + 60 + i * (h - 60) / 3
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
    for i in range(1, 4):
        xx = x - w / 2 + i * w / 4
        parts.append(P((xx, y - h / 2 + 60), (xx, y + h / 2)))
    return join(*parts)


def waves(x, y, n=3) -> skia.Path:
    """声波（打电话）：向右的三道弧。"""
    p = skia.Path()
    for i in range(n):
        r = 30 + i * 28
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -45, 90)
    return p


def room(x, y, w=600, h=500) -> skia.Path:
    """屋子：墙 + 屋顶 + 一扇窗。(x, y) 为墙体中心。"""
    return join(P((x - w / 2, y - h / 2), (x - w / 2, y + h / 2), (x + w / 2, y + h / 2), (x + w / 2, y - h / 2)),
                P((x - w / 2 - 40, y - h / 2 + 10), (x, y - h / 2 - 150), (x + w / 2 + 40, y - h / 2 + 10)),
                rect(x - w / 4, y - h / 6, 130, 110, 8), P((x - w / 4, y - h / 6 - 55), (x - w / 4, y - h / 6 + 55)))


# ---------------------------------------------------------------- 开局：人很多，心里空（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 各 3 小节（12 拍：第 0–8 拍逐步画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


scene("工作群几百人", "灵魂拷问", (950, 900, 0.85), bars=2)
L(phone(850, 900, 440, 700), 0, 1.0, BLACK, 10, sfx="wood_high")
T("工作群", 850, 630, 52, k0=1, sfx="pop")
T("498 人", 1330, 640, 70, RED, k0=2, sfx="pop")
L(join(*[bubble(x, y, 200, 70, -1 if x < 850 else 1) for x, y in ((750, 770), (950, 900), (750, 1030), (950, 1160))]),
  3, 4.2, BLUE, 7, sfx="pop")
T("99+", 1330, 900, 90, RED, k0=5, sfx="rim")

scene("人不少，咋还孤单？", "灵魂拷问", (2650, 1050, 0.85), shake=[5], flashes=[5])
T("坐满一桌", 2650, 560, 64, k0=0, sfx="pop")
L(oval(2650, 1010, 640, 200), 1, 2, BLACK, 9, sfx="wood_high")
L(join(*[bust(x, 790, 40) for x in (2450, 2650, 2850)], bust(2250, 1000, 40)), 2, 3, BLACK, 8, sfx="pop")
L(bust(3060, 1000, 40), 3, 3.8, BLUE, 8, sfx="pop")
L(face(3060, 1000 + 290 * 0.9, 0.9, "flat"), 3.8, 4.6, BLUE, 6)
T("几百人，还孤单", 2520, 1450, 80, k0=5, sfx="kick")
T("？", 2860, 1460, 110, RED, k0=6.8, k1=7.6)

# ---------------------------------------------------------------- 书中观点（场景 3–7）

scene("人多就不孤单？", "孤独是可耻的", (1050, 3200, 0.85))
L(book(750, 3050, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 750, 2810, 76, GREEN, k0=1, sfx="pop")
T("卡乔波", 750, 3280, 52, k0=3, sfx="pop")
T("人多", 720, 3500, 90, k0=4, sfx="pop")
L(eq(900, 3490, 70), 5, 5.8, BLACK, 9, sfx="wood_high")
T("不孤单？", 1140, 3500, 90, k0=6, sfx="pop")

scene("孤单看感觉，不看人数", "书中观点", (1050, 3520, 0.74), shake=[0], flashes=[0])
L(join(P((600, 3410), (1360, 3590)), P((1360, 3410), (600, 3590))), 0, 0.8, RED, 16, sfx="kick")
T("对不上", 1050, 3720, 110, RED, k0=1, sfx="tom")
L(underline(860, 1240, 3800, 10, 30), 2, 2.8, RED, 8, sfx="wood_high")
T("孤单看感觉", 1050, 3970, 100, k0=3, sfx="pop")
T("不看人数", 1050, 4120, 100, RED, k0=5, sfx="ding")

DX = 2680                         # 示意图中心
scene("看跟谁合得来", "书中观点 · 感觉与关系", (DX, 3190, 0.8))
L(heart(DX, 2700, 110), 0, 1.0, RED, 10, sfx="pop")
T("关系好不好", DX, 2930, 64, RED, k0=1, sfx="ding")
L(join(stick(2420, 3430, 0.65, "point"), stick(2940, 3430, 0.65, "up")), 3, 4, BLACK, 9, sfx="wood_high")
L(join(face(2420, 3430, 0.65, "smile"), face(2940, 3430, 0.65, "smile")), 4, 4.8, BLACK, 6)
L(join(arrow((2530, 3245), (2830, 3245), -0.1, 34), arrow((2830, 3295), (2530, 3295), -0.1, 34)), 5, 5.8, GREEN, 8,
  sfx="pop")
T("说得上话", DX, 3140, 58, GREEN, k0=6, sfx="pop")

scene("和人数时长无关", "书中观点 · 人数与独处", (DX, 4200, 1.1))
L(join(*[circle(2290 + c * 90, 4040 + r * 80, 26) for r in range(2) for c in range(3)]), 0, 0.9, BLACK, 7,
  sfx="pop")
T("人数", 2380, 4220, 56, k0=1, sfx="wood_high")
L(eq(2290, 4320, 60, neq=True), 2, 2.6, RED, 8, sfx="rim")
T("孤单", 2430, 4330, 56, RED, k0=2.6)
L(clock(2980, 4080, 80), 3.6, 4.4, BLACK, 9)
L(hands_at(2980, 4080, 80, 9, 0), 4.4, 4.9, RED, 9)
T("独处多久", 2980, 4220, 56, k0=5, sfx="pop")
L(eq(2890, 4320, 60, neq=True), 6, 6.6, RED, 8, sfx="rim")
T("孤单", 3030, 4330, 56, RED, k0=6.6)

scene("差在关系上", "书中观点 · 一张图", (1830, 3700, 0.4))
L(rect(DX, 3360, 780, 600, 30), 0, 1.0, RED, 10, sfx="wood_low")
L(check(3230, 3590, 50), 2, 2.8, GREEN, 11, sfx="ding")
L(join(cross(2380, 4040, 130), cross(2980, 4080, 130)), 3, 4, RED, 9, sfx="rim")
T("差在关系上", DX, 4700, 140, RED, k0=5, sfx="pop")

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

scene("同事挨着各刷手机", "例子 · 工位", (950, 5850, 0.85))
T("工位挨着", 950, 5440, 64, k0=0, sfx="pop")
L(join(desk(700, 5840, 300), desk(1200, 5840, 300)), 1, 2, BLACK, 9, sfx="wood_high")
L(join(stick(560, 5990, 0.7, "hold"), stick(1060, 5990, 0.7, "hold")), 2, 3, BLACK, 9, sfx="pop")
hy = 5990 - 290 * 0.7
L(join(phone(560 + 85, hy + 50, 50, 85), phone(1060 + 85, hy + 50, 50, 85)), 3, 4, BLUE, 7, sfx="pop")
L(join(face(560, 5990, 0.7, "flat"), face(1060, 5990, 0.7, "flat")), 4, 4.8, BLACK, 6)
T("午饭：各刷各的", 950, 5580, 60, RED, k0=5, sfx="rim")

scene("过年没人问你累不累", "例子 · 过年", (950, 7070, 0.9))
T("过年：十几口人", 950, 6550, 60, k0=0, sfx="pop")
L(join(*[stick(x, 7070, 0.5) for x in (600, 740, 880, 1020, 1160)], stick(1320, 7070, 0.5)), 2, 3, BLACK, 8,
  sfx="wood_high")
T("工资多少？", 680, 6720, 50, k0=3, k1=4, sfx="pop")
T("啥时结婚？", 1100, 6720, 50, k0=4, k1=5, sfx="pop")
L(face(1320, 7070, 0.5, "sad"), 5, 5.8, BLUE, 6)
T("没人问累不累", 950, 7180, 56, RED, k0=6, sfx="rim")

scene("独居不孤单，差在深聊", "例子 · 独居", (2650, 6700, 0.85))
T("一个人住", 2650, 6300, 60, k0=0, sfx="pop")
L(room(2480, 6720, 560, 440), 1, 2, BLACK, 9, sfx="wood_high")
L(join(stick(2560, 6920, 0.6, "hold", hair=True), face(2560, 6920, 0.6, "smile")), 2, 3, BLUE, 8, sfx="pop")
hy2 = 6920 - 290 * 0.6
L(join(phone(2560 + 70, hy2 + 40, 44, 76), waves(2680, hy2 + 30)), 3, 4, BLUE, 7, sfx="pop")
T("每周长聊", 3020, 6560, 54, k0=4, sfx="pop")
T("不孤单", 3020, 6860, 64, GREEN, k0=5, sfx="ding")
T("差在有没有深聊", 2560, 7130, 78, RED, k0=6, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

scene("找一两个聊得来的", "第一步 · 找人", (950, 8500, 0.85))
T("① 找一两个人", 950, 7950, 72, BLUE, k0=0, sfx="pop")
L(join(stick(830, 8500, 0.55), stick(1070, 8500, 0.55), face(830, 8500, 0.55, "smile"),
       face(1070, 8500, 0.55, "smile")), 2, 3, BLACK, 8, sfx="wood_high")
L(circle(950, 8390, 180), 3, 3.8, RED, 8, sfx="ding")
T("老同学", 600, 8300, 56, k0=4, sfx="pop")
T("前同事", 1300, 8300, 56, k0=5, sfx="pop")

scene("饭局换成深聊", "第二步 · 深聊", (2650, 8500, 0.85))
T("② 换成深聊", 2650, 7950, 72, BLUE, k0=0, sfx="pop")
L(join(oval(2400, 8400, 300, 100), *[circle(x, 8295, 30) for x in (2290, 2400, 2510)],
       *[circle(x, 8505, 30) for x in (2290, 2400, 2510)]), 2, 2.9, BLACK, 8, sfx="wood_low")
L(cross(2400, 8400, 140), 3, 3.8, RED, 11, sfx="rim")
L(join(stick(2830, 8590, 0.55), stick(3110, 8590, 0.55), cup(2970, 8480, 0.7)), 4, 5, BLUE, 8, sfx="wood_high")
L(bubble(2970, 8200, 380, 110, -1), 5, 5.8, BLACK, 8, sfx="pop")
T("最近在烦啥？", 2970, 8200, 48, k0=5.8)

scene("每周固定打电话", "第三步 · 固定", (2650, 9680, 0.9))
T("③ 定个时间", 2650, 9150, 72, BLUE, k0=0, sfx="pop")
L(calendar(2420, 9490, 300, 260), 2, 3, BLACK, 7, sfx="wood_high")
L(circle(2495, 9577, 34), 3, 3.8, RED, 8, sfx="ding")
L(join(phone(2930, 9470, 110, 190), waves(3010, 9400)), 4, 5, BLUE, 8, sfx="pop")
T("周日 20:00", 2900, 9680, 52, RED, k0=5, sfx="pop")
L(check(3130, 9675, 34), 7, 7.8, GREEN, 9, sfx="ding")

# ---------------------------------------------------------------- 收尾：看全板 → 评论区（场景 14，4 小节）

scene("评论区聊聊", "评论区见", (1800, 8700, 0.4), bars=4)
H(0, "cymbal", 0.5)
H(2, "ding")
T("你能深聊的有几个？", 1000, 9050, 110, RED, k0=5, sfx="pop")
T("下一讲：", 1000, 9230, 72, k0=8, sfx="wood_high")
T("一个人住久了，", 1000, 9370, 90, k0=9)
T("为什么总睡不好？", 1000, 9510, 90, k0=11)
b.hit(len(b.shots) - 1, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "quality", "感觉不看人数", "群里几百人，为什么还是孤单？", ACC, b.shots,
                 [f"{BOOK}第一部分 可耻的孤独（第 1–6 章，转述）",
                  "中译本：焦梦津译，中国人民大学出版社 2009；原书 W. W. Norton, 2008"],
                 "群里几百人|为什么还是【孤单】", 4,
                 ["书中观点均为转述：孤独看的是主观感受——和别人的关系质量、合不合心意，和身边人多人少、独处时间长短"
                  "不是一回事；作者团队的研究里，孤独的人和不孤独的人在外貌、聪明程度、社交时间上差别不大。出处：John T. "
                  "Cacioppo & William Patrick, Loneliness: Human Nature and the Need for Social Connection (W. W. Norton, "
                  "2008)，中译本《孤独是可耻的》（焦梦津译，中国人民大学出版社 2009），第一部分。上屏均为转述，不是逐字引文；"
                  "柱状图与“≈”只表示“差别不大”，不是研究数据。",
                  "工作群 498 人、消息 99+、聚餐、工位午饭、周末饭局、过年亲戚、独居女生每周和闺蜜长聊均为"
                  "现实场景示意，数字与时间为示意，不指向任何具体公司或个人。",
                  "四步做法（找一两个说得上话的人 / 把一次饭局换成一次深聊 / 点赞换成一句留言 / 定个固定时间打电话）为据书中"
                  "思路整理的建议，对应书末第 14 章 EASE 中“Selection：重质量不重数量”与“Extend yourself：先迈一小步”。"],
                 tags="#社交 #职场")
    return b.attach(ep)
