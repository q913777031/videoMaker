"""02 光环效应（白板手绘版）：先听到的那句，为什么最管用？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（形式 F 两人对比）：新来两个同事小A、小B → 小A 的介绍先说优点（聪明、勤奋、冲动、挑剔、固执、嫉妒），
小B 的介绍是同样六个词倒过来 → drop：拉远看两人，小A 头顶爱心、小B 头顶问号，“同样六个词”砸下 →
亮书（快快、慢慢出场，“光环效应”）→ 书中观点（快快手里只有一块拼图，剩下的自己补全：眼见即为事实）→
书中故事（作者批卷：先读的那篇带高后面的分，改成一题一题批、遮住分数）→
身边的例子（面试一进门就加分、周报先写什么、开会第一个开口的人定调）→
做法（开会前先各写各的 / 分项打分 / 重点放第一句）→ 拉远看全板 → 评论区互动 + 下一讲。
书中观点为转述：丹尼尔·卡尼曼《思考，快与慢》第7章“字母‘B’与数字‘13’”（A Machine for Jumping to Conclusions），
光环效应、Asch 的描述词实验、批卷、开会前先写下意见、“眼见即为事实”；中译本胡晓姣、李爱民、何梦莹译，中信出版社 2012。
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, cross,
                               doc, face, join, rect, scribble, stick)

from .common import BOOK, episode, kuai, man

ACC = "#3A6FC2"
SQUARE_SHOT = 3                 # 场景 4：小A（爱心）+ 小B（问号）+ 两张六词卡 + “同样六个词”

b = Board(size=(3600, 10000))
OY = 200                        # 各区块整体下移：顶部留白，后面几排再逐排加大间距，避免上一排的字露在页眉上方


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y + OY, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    path = skia.Path(path)
    path.offset(0, OY)
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=(view[0], view[1] + OY, view[2]), bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def heart(x, y, r=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def ellipse(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def piece(x, y, a=90) -> skia.Path:
    """拼图块：方块 + 右边、上边各一个凸起。(x, y) 为方块中心。"""
    return join(rect(x, y, a, a, 6), circle(x + a / 2 + a * 0.16, y, a * 0.18), circle(x, y - a / 2 - a * 0.16, a * 0.18))


def frame4(x, y, w, h) -> skia.Path:
    """2×2 拼图框。"""
    return join(rect(x, y, w, h, 8), P((x, y - h / 2), (x, y + h / 2)), P((x - w / 2, y), (x + w / 2, y)))


def head(x, y, r=70, mood="smile") -> skia.Path:
    """领导的大头：圆脸 + 眼睛 + 嘴 + 领带结。"""
    p = join(circle(x, y, r), circle(x - r * 0.35, y - r * 0.2, 5), circle(x + r * 0.35, y - r * 0.2, 5),
             P((x - 18, y + r + 6), (x, y + r + 40), (x + 18, y + r + 6), close=True))
    m = skia.Path()
    if mood == "smile":
        m.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.05, r * 0.9, r * 0.6), 20, 140)
    else:
        m.addArc(skia.Rect.MakeXYWH(x - r * 0.4, y + r * 0.3, r * 0.8, r * 0.5), 200, 140)
        m.moveTo(x - r * 0.6, y - r * 0.55)
        m.lineTo(x - r * 0.15, y - r * 0.4)
        m.moveTo(x + r * 0.6, y - r * 0.55)
        m.lineTo(x + r * 0.15, y - r * 0.4)
    return join(p, m)


def note(x, y, a=220) -> skia.Path:
    """便利贴：方块 + 三行字迹。"""
    parts = [rect(x, y, a, a, 8), P((x + a / 2 - 50, y + a / 2), (x + a / 2, y + a / 2 - 50))]
    for i in range(3):
        yy = y - a / 2 + 60 + i * 50
        parts.append(P((x - a / 2 + 30, yy), (x + a / 2 - 40 - 30 * (i % 2), yy)))
    return join(*parts)


# ---------------------------------------------------------------- 开局：两个新同事（场景 1–4）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

AX, BX, FY = 1500, 2100, 1650   # 小A、小B 的脚底
WORDS = ["聪明", "勤奋", "冲动", "挑剔", "固执", "嫉妒"]
GOOD = {"聪明", "勤奋"}
CA, CB, CY = 1050, 2550, 1300    # 两张词卡的中心

scene("新来两个同事", "两个新同事", (1800, 1400, 0.85), bars=2)
T("新来的同事", 1800, 1050, 72, BLUE, k0=0, k1=1.25, sfx="pop")
L(join(stick(AX, FY, 0.8, "down"), face(AX, FY, 0.8, "smile"), rect(AX, FY + 85, 150, 80, 12)), 2, 2.9,
  sfx="wood_high")
T("小A", AX, FY + 103, 52, k0=3, k1=3.8, sfx="pop")
L(join(stick(BX, FY, 0.8, "down"), face(BX, FY, 0.8, "smile"), rect(BX, FY + 85, 150, 80, 12)), 4, 4.9,
  sfx="wood_high")
T("小B", BX, FY + 103, 52, k0=5, k1=5.8, sfx="pop")


def word_card(cx, words, ring_color):
    L(rect(cx, CY, 260, 600, 16), 0, 0.9, BLACK, 8, sfx="wood_high")
    for n, w in enumerate(words):
        T(w, cx, CY - 225 + n * 88, 60, GREEN if w in GOOD else RED, k0=1 + n, k1=1.8 + n, sfx="pop")
    L(ellipse(cx, CY - 225, 200, 100), 7, 7.8, ring_color, 8, sfx="ding")


scene("先听到优点", "小A · 先听优点", (1350, 1350, 0.85))
word_card(CA, WORDS, GREEN)

scene("先听到缺点", "小B · 先听缺点", (2250, 1350, 0.85))
word_card(CB, WORDS[::-1], RED)

scene("同样的词，两种印象", "同样六个词", (1800, 1300, 0.58), shake=[0], flashes=[0])
T("同样六个词", 1800, 870, 130, RED, k0=0, k1=1.25, sfx="kick")
b.erase(J(), 1, 1.6, 1800, 1050 + OY, 460, 110)          # 擦掉场景 1 的“新来的同事”，给两人头顶留出地方
H(1, "shaker")
L(heart(AX, 1260, 70), 2, 2.9, RED, 10, sfx="ding")
T("？", BX, 1300, 180, RED, k0=4, k1=4.8, sfx="rim")
T("顺序反了，印象也反了", 1800, 1880, 84, k0=5, k1=7.25, sfx="pop")

# ---------------------------------------------------------------- 书中观点（场景 5–7）

scene("先来的定了调", "思考，快与慢 · 书中观点", (1300, 2900, 0.85))
L(book(950, 2850, 380, 260), 0, 0.9, sfx="wood_low")
T("思考，快与慢", 950, 2650, 60, GREEN, k0=1, k1=2.5, sfx="pop")
L(join(kuai(1450, 3150, 0.6), face(1450, 3150, 0.6, "smile")), 3, 3.9, RED, 9, sfx="wood_high")
L(join(man(1750, 3150, 0.6), face(1750, 3150, 0.6, "flat")), 4, 4.9, BLUE, 9, sfx="wood_high")
L(ellipse(950, 3110, 300, 56), 5, 5.8, ORANGE, 9, sfx="ding")
T("光环效应", 950, 3230, 90, RED, k0=6, k1=7, sfx="pop")

KX, KY = 2100, 3350             # 快快（拿着一块拼图）
FX, FYY = 2780, 2850            # 拼图框
scene("有一块就拼全图", "书中观点 · 眼见即为事实", (2500, 2900, 0.85))
L(join(kuai(KX, KY, 0.65), face(KX, KY, 0.65, "smile")), 0, 0.9, RED, 9, sfx="wood_high")
L(piece(KX, 2990, 80), 1, 1.8, BLUE, 9, sfx="pop")
L(join(frame4(FX, FYY, 500, 400), piece(FX - 125, FYY - 100, 80)), 2, 2.9, BLACK, 8, sfx="wood_low")
L(join(scribble(FX + 125, FYY - 100, 200, 150, 6), scribble(FX - 125, FYY + 100, 200, 150, 6),
       scribble(FX + 125, FYY + 100, 200, 150, 6)), 3, 3.9, RED, 6, sfx="shaker")
L(bubble(2150, 2640, 280, 130, -1), 4, 4.6, BLACK, 8, sfx="pop")
T("懂了！", 2150, 2660, 58, k0=4.6, k1=5.4)
T("眼见即为事实", FX, 3250, 64, RED, k0=6, k1=7.5, sfx="ding")

OY = 260
scene("作者批卷也中招", "书中故事 · 批卷", (2500, 4300, 0.85))
L(doc(2150, 4100, 280, 360, 4), 0, 0.9, sfx="wood_high")
T("高分", 2150, 3870, 60, RED, k0=1, k1=1.8, sfx="pop")
L(arrow((2320, 4100), (2680, 4100), 0.15, 40), 2, 2.9, BLACK, 8, sfx="wood_low")
L(doc(2850, 4100, 280, 360, 4), 3, 3.9, sfx="wood_high")
T("跟着高", 2850, 3870, 60, RED, k0=4, k1=4.8, sfx="pop")
L(cross(2500, 4060, 50), 5, 5.8, RED, 11, sfx="rim")
T("一题一题批", 2500, 4480, 70, BLUE, k0=6, k1=7.25, sfx="pop")
T("遮住分数", 2500, 4600, 70, BLUE, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

scene("一进门就加了分", "例子 · 面试", (1300, 4300, 0.85))
L(join(P((1000, 4560), (1600, 4560)), P((1040, 4560), (1040, 4700)), P((1560, 4560), (1560, 4700))), 0, 0.9,
  sfx="wood_high")
L(stick(900, 4700, 0.75, "down"), 1, 1.9, BLUE, 9, sfx="wood_high")
L(join(stick(1700, 4700, 0.75, "down"), face(1700, 4700, 0.75, "smile")), 2, 2.9, BLACK, 9, sfx="pop")
L(rect(1700, 4350, 150, 80, 12), 3, 3.4, RED, 7, sfx="pop")
T("名校", 1700, 4368, 54, RED, k0=3.4, k1=4.2)
L(doc(1200, 4000, 240, 300, 3), 4, 4.9, BLACK, 8, sfx="wood_low")
for n, yy in enumerate((3900, 4015, 4130)):
    L(check(1375, yy, 28), 5 + n, 5.6 + n, GREEN, 9, sfx="ding" if n == 2 else "pop")

OY = 320
scene("周报先写什么", "例子 · 周报", (1300, 5700, 0.85))
L(doc(1000, 5600, 300, 380, 5), 0, 0.9, sfx="wood_high")
T("先写成果", 1000, 5330, 56, GREEN, k0=1, k1=2, sfx="pop")
L(doc(1600, 5600, 300, 380, 5), 2, 2.9, sfx="wood_high")
T("先写问题", 1600, 5330, 56, RED, k0=3, k1=4, sfx="pop")
L(head(1000, 6000, 70, "smile"), 4, 4.9, BLACK, 8, sfx="pop")
L(head(1600, 6000, 70, "frown"), 5, 5.9, BLACK, 8, sfx="rim")
T("同一份周报", 1300, 6200, 60, k0=6, k1=7.25, sfx="ding")

scene("第一个开口的定调", "例子 · 开会", (2500, 5700, 0.85))
L(P((1950, 6060), (3050, 6060)), 0, 0.9, BLACK, 10, sfx="wood_high")
L(join(*(stick(x, 6150, 0.55, "down") for x in (2350, 2650, 2950))), 1, 1.9, BLACK, 8, sfx="wood_high")
L(stick(2050, 6150, 0.55, "point"), 2, 2.8, RED, 9, sfx="pop")
L(bubble(2250, 5700, 420, 130, -1), 3, 3.8, BLACK, 8, sfx="pop")
T("我觉得不行", 2250, 5718, 54, k0=3.8, k1=5.05)
for n, x in enumerate((2350, 2650, 2950)):
    T("对", x, 5915, 54, BLUE, k0=5 + n, k1=5.8 + n, sfx="pop" if n < 2 else "ding")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

OY = 470
scene("开会前，先各写各的", "做法一 · 先写再说", (2500, 7100, 0.85))
T("① 先写再说", 2500, 6720, 76, BLUE, k0=0, k1=1.5, sfx="pop")
for n, x in enumerate((2150, 2500, 2850)):
    L(note(x, 7050), 2 + n, 2.9 + n, ORANGE if n != 1 else BLACK, 8, sfx="wood_high" if n != 1 else "wood_low")
T("写完再一起看", 2500, 7400, 66, GREEN, k0=6, k1=7.5, sfx="ding")

scene("一项一项看", "做法二 · 分项打分", (1300, 7100, 0.85))
T("② 分项打分", 1300, 6720, 76, BLUE, k0=0, k1=1.5, sfx="pop")
GX = (970, 1190, 1410, 1630)
L(join(rect(1300, 7050, 880, 300, 12), P((850, 7000), (1740, 7000)),
       *(P((x, 6900), (x, 7200)) for x in (1080, 1300, 1520))), 2, 2.9, BLACK, 8, sfx="wood_high")
for n, w in enumerate(("沟通", "专业", "态度", "经验")):
    T(w, GX[n], 6968, 54, k0=3 + n, k1=3.8 + n, sfx="pop")
L(check(GX[0], 7100, 36), 7, 7.6, GREEN, 10, sfx="ding")

OY = 600
scene("重点放第一句", "做法三 · 重点放开头", (1300, 8500, 0.85))
T("③ 重点放开头", 1300, 8100, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(doc(1300, 8550, 420, 520, 5), 2, 2.9, sfx="wood_high")
L(rect(1297, 8340, 380, 70, 10), 3, 3.8, RED, 9, sfx="ding")
T("先写成果", 1690, 8220, 58, RED, k0=4, k1=5, sfx="pop")
L(arrow((1660, 8255), (1525, 8330), 0.1, 28), 5, 5.8, RED, 7, sfx="wood_low")
L(head(1700, 8650, 70, "smile"), 6, 6.9, BLACK, 8, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 4700, 0.105)
CMT = (2500, 8500, 0.85)
j_end = scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(j_end, 4, (CMT[0], CMT[1] + OY, CMT[2]), dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你被第一印象坑过吗？", 2500, 8250, 76, RED, k0=6, k1=8.5, sfx="pop")
L(join(kuai(2250, 8880, 0.6, "up"), face(2250, 8880, 0.6, "smile")), 9, 9.8, RED, 9, sfx="wood_high")
L(join(man(2750, 8880, 0.6), face(2750, 8880, 0.6, "smile")), 10, 10.8, BLUE, 9, sfx="wood_low")
T("下一讲：先报的数字，为什么能带偏你？", 2500, 8410, 46, k0=11, k1=15.5, sfx="pop")
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "halo", "光环效应", "先听到的那句，为什么最管用？", ACC, b.shots,
                 [f"{BOOK}第7章 字母“B”与数字“13”（A Machine for Jumping to Conclusions）（转述）",
                  "中译本：胡晓姣、李爱民、何梦莹译，中信出版社 2012"],
                 "先听到的那句|为什么最【管用】", SQUARE_SHOT,
                 ["书中观点均为转述：光环效应——先注意到的特点会给后面的信息上色。书中讲到 Asch 的实验：两个人的描述词"
                  "相同、顺序相反（聪明、勤奋、冲动、挑剔、固执、嫉妒），人们对先听到优点的那位印象更好。画面里的“小A”“小B”"
                  "替代书中的 Alan 与 Ben，六个词为中文转述（第 7 章）。",
                  "“眼见即为事实”：系统1 只拿手上已有的信息编出一个连贯的故事，不管缺了什么（第 7 章）。"
                  "快快手里一块拼图、其余格子自己补全的画面为通俗化示意。",
                  "作者批卷：卡尼曼发现先读的那篇文章会影响后面的打分，后来改成一题一题批、看不到前面的得分（第 7 章，据书中"
                  "内容转述）；试卷上的“高分”“跟着高”为示意，不是书中数据。",
                  "开会前每人先写下自己的看法，减少第一个发言的人定调，为书中建议（第 7 章）。",
                  "面试、周报、开会三个例子为现实场景示意，不指向任何具体公司或个人；“分项打分”“重点放开头”为据书中思路"
                  "整理的建议，评分栏目为示意。"],
                 tags="#第一印象 #职场")
    return b.attach(ep)
