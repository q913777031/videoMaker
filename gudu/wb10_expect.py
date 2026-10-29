"""10 挑人与往好处想（白板手绘版）：交朋友，该找谁、怎么想？（系列最后一讲）

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（2026-10 观众反馈“动画切换太快，来不及看”后改为慢速讲解版）。
叙事：打工人切身问题开局（手机里加了八百多个好友，周末想约人翻一圈没人可约；发了条消息两小时没回，心里就嘀咕
“他嫌我烦了吧”）→ 书中观点（亮书《孤独是可耻的》、卡乔波；书末四个字母 E A S E，上一讲讲了前两个，今天讲后两个：
S 挑人——找兴趣、想法相近、能长期来往的人，重质量不重数量；E 往好处想——孤单久了容易先把人往坏处猜，越猜越躲，
换个想法“他在忙吧”）→ 身边的例子（团建加了一圈好友、成朋友的是饭搭子；刚搬到新城市、跑步群每周都见；朋友半天没回、
原来在加班）→ 具体做法（列三个想常见的人、每月约一次 / 按兴趣找个局、固定去 / 没回消息先想三个好理由、明天再问一句）
→ 系列收尾：拉远看全板，评论区问题 + 这一季讲完了。
书中观点为转述（John T. Cacioppo & William Patrick, Loneliness: Human Nature and the Need for Social Connection, 2008；
中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009，第 14 章“个体困境的解药”）；例子与做法为现实场景示意与据书中思路整理的建议。

白板布局：3 列 × 4 行，每格 1200 × 1300，按蛇形走位（相邻场景相邻格），最后一屏拉远看全板，评论区写在白板最下方。
"""

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, building, check, circle, clock,
                               cross, face, hands_at, join, rect, scribble, stick, underline)

from .common import BOOK, episode

ACC = "#C2603A"
SQUARE_SHOT = 6
COVER_SHOT = 6

b = Board(size=(3600, 6200))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s.replace(" ", ""))) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def J():
    return len(b.shots) - 1


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    """一个场景：3 小节（12 拍，≈6.4 秒）第 0–8 拍画完、最后 4 拍停住；片头 2 小节第 0–6 拍画完；片尾 4 小节。"""
    return b.shot(text, tag, view=view, bars=bars, **kw)


def V(cell, z=0.85):
    x, y = cell
    return (x, y, z)


# 白板格子中心（列 x：600 / 1800 / 3000；行 y：700 / 2000 / 3300 / 4600）
C1, C2, C3 = (600, 700), (1800, 700), (3000, 700)
C4, C5, C6 = (3000, 2000), (1800, 2000), (600, 2000)
C8, C9, C10 = (600, 3300), (1800, 3300), (3000, 3300)
C11, C12, C13 = (3000, 4600), (1800, 4600), (600, 4600)


# ---------------------------------------------------------------- 本讲小画法

def phone(x, y, w=200, h=340):
    return join(rect(x, y, w, h, 30), P((x - 30, y + h / 2 - 30), (x + 30, y + h / 2 - 30)))


def contacts(x, y, n=4, gap=80, w=150):
    """手机里的好友列表：头像圈 + 名字横线。(x, y) 为第一行中点。"""
    parts = []
    for i in range(n):
        yy = y + i * gap
        parts.append(circle(x - w / 2, yy, 24))
        parts.append(P((x - w / 2 + 45, yy), (x + w / 2, yy)))
    return join(*parts)


def calendar(x, y, w=300, h=280):
    top = y - h / 2 + 70
    parts = [rect(x, y, w, h, 20), P((x - w / 2, top), (x + w / 2, top)),
             P((x - w / 4, y - h / 2 - 25), (x - w / 4, y - h / 2 + 25)),
             P((x + w / 4, y - h / 2 - 25), (x + w / 4, y - h / 2 + 25))]
    for r in range(2):
        for cc in range(3):
            parts.append(circle(x - w / 3 + cc * w / 3, top + (h - 70) * (0.3 + 0.4 * r), 10))
    return join(*parts)


# ---------------------------------------------------------------- 开局：好友一堆，没人可约（场景 1–2）

X, Y = C1
scene("好友一堆，没人可约", "灵魂拷问", V(C1), bars=2)
L(phone(X - 250, Y - 20, 300, 500), 0, 0.9, sfx="wood_high")
L(contacts(X - 230, Y - 170, 4, 90, 170), 1, 1.9, BLACK, 7, sfx="pop")
T("好友 873", X + 240, Y - 150, 80, k0=2, k1=2.9, sfx="pop")
T("周末约谁？", X + 240, Y + 20, 72, RED, k0=3, sfx="pop")
L(cross(X - 250, Y - 20, 170), 4, 4.8, RED, 14, sfx="rim")

X, Y = C2
scene("该找谁？该怎么想？", "灵魂拷问", V(C2))
L(bubble(X + 150, Y - 330, 560, 150, -1), 0, 0.9, sfx="wood_high")
T("周末有空吗？", X + 150, Y - 330, 56, k0=1, sfx="pop")
T("两小时没回", X + 150, Y - 170, 60, RED, k0=3, sfx="rim")
L(stick(X - 380, Y + 340, 0.75, "shrug"), 4, 4.8, sfx="wood_high")
L(face(X - 380, Y + 340, 0.75, "sad"), 4.8, 5.0)
T("嫌我烦了？", X - 380, Y - 10, 56, k0=5, k1=6, sfx="pop")
T("该找谁？怎么想？", X + 200, Y + 240, 80, RED, k0=6, k1=8, sfx="tom")

# ---------------------------------------------------------------- 书中观点（场景 3–7）

X, Y = C3
scene("书末给了四个字母", "孤独是可耻的 · 卡乔波", V(C3))
L(book(X - 230, Y - 30, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", X - 230, Y - 270, 72, GREEN, k0=1, sfx="pop")
T("卡乔波", X - 230, Y + 190, 60, k0=3, sfx="pop")
T("第十四章", X + 300, Y - 120, 64, k0=4, sfx="wood_high")
T("四个字母", X + 300, Y + 20, 64, RED, k0=5, sfx="ding")

X, Y = C4
scene("后两个：挑人，往好处想", "书中观点 · 后两个", V(C4), shake=[0], flashes=[0])
H(0, "kick", 1.0, "drop")
LX = [X - 390, X - 130, X + 130, X + 390]
for n, w in enumerate("EASE"):
    T(w, LX[n], Y - 120, 200, k0=n * 0.5, k1=n * 0.5 + 0.5)
L(join(check(LX[0], Y - 320, 36), check(LX[1], Y - 320, 36)), 2, 2.8, GREEN, 9, sfx="pop")
T("上一讲", (LX[0] + LX[1]) / 2, Y - 420, 50, GREEN, k0=3, sfx="wood_high")
L(rect((LX[2] + LX[3]) / 2, Y - 120, 540, 300, 40), 4, 4.9, RED, 12, sfx="tom")
T("挑人", LX[2], Y + 130, 64, RED, k0=5, sfx="pop")
T("往好处想", LX[3], Y + 240, 64, RED, k0=6, sfx="pop")

X, Y = C5
scene("挑想法相近的人", "书中观点 · 挑人", V(C5))
L(stick(X - 330, Y + 380, 0.75), 0, 0.8, sfx="wood_high")
L(face(X - 330, Y + 380, 0.75, "smile"), 0.8, 1.0)
L(stick(X + 330, Y + 380, 0.75), 1, 1.8, sfx="pop")
L(face(X + 330, Y + 380, 0.75, "smile"), 1.8, 2.0)
T("爬山 · 看球", X, Y + 170, 60, k0=2, sfx="pop")
T("想法相近", X, Y - 350, 76, RED, k0=4, sfx="pop")
L(underline(X - 150, X + 150, Y - 295, 8, 24), 5, 5.8, RED, 6, sfx="wood_high")
T("常来往，几个就够", X, Y - 180, 60, k0=6, k1=8, sfx="ding")

X, Y = C6
scene("越孤单，越往坏处猜", "书中观点 · 往坏处猜", V(C6))
L(stick(X - 260, Y + 380, 0.8, "shrug"), 0, 0.8, sfx="wood_high")
L(face(X - 260, Y + 380, 0.8, "sad"), 0.8, 1.0)
L(bubble(X + 170, Y - 300, 480, 150, -1), 1, 1.8, sfx="pop")
T("他烦我了？", X + 170, Y - 300, 56, k0=2, k1=3)
L(arrow((X + 230, Y - 200), (X + 250, Y - 70), 0.1, 30), 3, 3.8, RED, 8, sfx="wood_low")
T("躲远点", X + 250, Y + 10, 64, RED, k0=4, sfx="rim")
L(scribble(X - 260, Y + 60, 160, 60, 6), 5, 5.8, RED, 7, sfx="shaker")

scene("换个想法：他在忙", "书中观点 · 往好处想", V(C6))
L(cross(X + 170, Y - 300, 100), 0, 0.8, RED, 12, sfx="rim")
L(P((X + 140, Y + 10), (X + 360, Y + 10)), 1, 1.8, RED, 10, sfx="wood_low")
L(bubble(X + 200, Y + 250, 440, 150, -1), 2, 2.8, GREEN, 9, sfx="pop")
T("他在忙吧", X + 200, Y + 250, 56, GREEN, k0=3, k1=4)
L(check(X + 470, Y + 250, 32), 4, 4.8, GREEN, 9, sfx="ding")
L(underline(X + 90, X + 310, Y + 300, 6, 20), 5, 5.8, GREEN, 6, sfx="wood_high")

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

X, Y = C8
scene("成朋友的是饭搭子", "例子 · 团建", V(C8))
L(phone(X - 280, Y - 120, 240, 400), 0, 0.8, sfx="wood_high")
T("+20", X - 280, Y - 150, 80, GREEN, k0=1, sfx="pop")
T("团建加好友", X + 200, Y - 330, 60, k0=2, sfx="pop")
T("之后没下文", X + 200, Y - 220, 52, k0=3.3)
L(stick(X + 50, Y + 380, 0.5), 4.6, 5.4)
L(stick(X + 350, Y + 380, 0.5), 5, 5.8, sfx="wood_high")
T("饭搭子", X + 200, Y + 30, 64, RED, k0=6, sfx="pop")
L(check(X + 360, Y + 25, 28), 7, 7.8, GREEN, 8, sfx="ding")

X, Y = C9
scene("新城市，跑步群每周见", "例子 · 新城市", V(C9))
L(building(X - 330, Y + 320, 240, 340), 0, 0.9, sfx="wood_high")
L(stick(X - 60, Y + 380, 0.6), 1, 1.8, sfx="pop")
L(face(X - 60, Y + 380, 0.6, "flat"), 1.8, 2.0)
T("谁也不认识", X - 200, Y - 330, 56, k0=2, sfx="pop")
T("跑步群", X + 280, Y - 190, 64, k0=4, sfx="pop")
L(calendar(X + 280, Y + 50, 260, 220), 5, 5.8, BLACK, 8, sfx="wood_high")
T("每周六", X + 280, Y + 250, 56, RED, k0=6, sfx="pop")

X, Y = C10
scene("没回，原来在加班", "例子 · 没回消息", V(C10))
L(phone(X - 300, Y - 130, 220, 360), 0, 0.8, sfx="wood_high")
T("在吗？", X - 300, Y - 170, 50, k0=1, sfx="pop")
L(clock(X + 120, Y - 300, 90), 2, 2.8, sfx="wood_low")
L(hands_at(X + 120, Y - 300, 90, 3, 0), 2.8, 3.0, RED, 9)
T("三小时", X + 330, Y - 300, 56, RED, k0=3, sfx="pop")
L(bubble(X + 170, Y - 60, 460, 130, -1), 4, 4.8, GREEN, 8, sfx="pop")
T("刚下班才看到", X + 170, Y - 60, 46, GREEN, k0=4.8, k1=6.0)
T("朋友是处出来的", X, Y + 300, 76, RED, k0=6, k1=8, sfx="ding")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

X, Y = C11
scene("列三个人，每月一约", "第一步 · 列三个人", V(C11))
L(rect(X, Y, 1040, 820, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("① 列三个人", X, Y - 300, 76, BLUE, k0=1, sfx="pop")
T("老同学", X - 250, Y - 130, 56, k0=3, sfx="pop")
T("饭搭子", X - 250, Y - 20, 56, k0=4)
T("跑友", X - 250, Y + 90, 56, k0=5, sfx="pop")
L(calendar(X + 250, Y - 40, 260, 230), 6, 6.8, BLACK, 8, sfx="wood_high")
T("每月一次", X + 250, Y + 160, 52, RED, k0=7, k1=8, sfx="ding")

X, Y = C12
scene("找个局，固定去", "第二步 · 找个局", V(C12))
L(rect(X, Y, 1040, 820, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("② 按兴趣找局", X, Y - 300, 76, BLUE, k0=1, k1=2.4, sfx="pop")
T("羽毛球群", X - 250, Y - 110, 56, k0=2.5, k1=3.4)
T("读书会", X - 250, Y + 0, 56, k0=3.4, k1=4.0)
L(calendar(X + 250, Y - 60, 240, 220), 4, 4.8, BLACK, 8, sfx="wood_high")
T("每周四晚", X + 250, Y + 130, 52, RED, k0=5, k1=6, sfx="pop")
T("第三次就熟了", X, Y + 290, 60, k0=6, k1=7.5, sfx="ding")

X, Y = C13
scene("先想三个好理由", "第三步 · 往好处猜", V(C13))
L(rect(X, Y, 1040, 820, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("③ 往好处猜", X, Y - 300, 76, BLUE, k0=1, sfx="pop")
L(phone(X - 270, Y - 10, 210, 330), 2, 2.8, sfx="wood_low")
T("已读未回", X - 270, Y - 50, 44, k0=3, k1=4, sfx="pop")
T("开会呢", X + 200, Y - 140, 56, k0=4, sfx="pop")
T("在开车", X + 200, Y - 30, 56, k0=4.8)
T("没看到", X + 200, Y + 80, 56, k0=5.6)
T("明天再问问", X, Y + 270, 60, GREEN, k0=6.5, k1=7.8)

# ---------------------------------------------------------------- 收尾：拉远看全板，评论区（场景 14，4 小节）

scene("人挑对，心放宽", "评论区见", (1800, 3060, 0.157), bars=4)
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")
T("你这周最想约谁？", 1800, 5480, 300, RED, k0=5, k1=7, sfx="pop")
T("这一季讲完了，谢谢你一路看完", 1800, 5850, 200, k0=8, k1=11, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "expect", "挑人与往好处想", "交朋友，该找谁、怎么想？", ACC, b.shots,
                 [f"{BOOK}第 14 章“个体困境的解药”（转述）", "中译本：焦梦津译，中国人民大学出版社 2009"],
                 "交朋友|挑对人，【往好处想】", COVER_SHOT,
                 ["书中观点均为转述：书末（第 14 章）作者给出摆脱孤独的四步，取首字母记作 EASE：Extend yourself（先迈一小步）、"
                  "Action plan（有计划，从低风险的小场合开始）、Selection（挑人：找兴趣、价值观相近、能长期来往的人，重质量不重数量）、"
                  "Expect the best（往好处预期别人）；本讲讲后两步，前两步见第 9 讲。“孤单久了容易先把人往坏处想，于是更戒备、"
                  "更退缩”转述自书中关于孤独让人对社交威胁更警觉的论述。出处：John T. Cacioppo & William Patrick, Loneliness: "
                  "Human Nature and the Need for Social Connection (W. W. Norton, 2008)；中译本《孤独是可耻的》"
                  "（约翰·卡乔波、威廉·帕特里克著，焦梦津译，中国人民大学出版社 2009）。",
                  "开局（好友 873 个没人可约、两小时没回消息）、团建加好友与饭搭子、新城市跑步群、朋友加班晚回"
                  "均为现实场景示意，不指向任何具体公司或个人；列三个人、按兴趣找局、往好处猜三步为据书中思路整理的建议。"],
                 tags="#交朋友 #人际关系")
    return b.attach(ep)
