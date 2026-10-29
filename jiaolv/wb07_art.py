"""07 艺术（白板手绘版）：为什么看部电影，心里就松了？

叙事：打工人切身问题开局（被领导骂了一整天、方案改到第 7 版 → 挤地铁回家 → 随手点开一部讲小人物的电影 →
主角也被人看低 → 看着看着哭了 → 哭完心里反倒松了，为什么？）→
书中观点（亮书《身份的焦虑》、德波顿，“解决方法”第二章“艺术”；小说、漫画、悲剧、喜剧一直在批评地位排位；
悲剧让人心疼摔下来的人，喜剧拿有权有势的人开涮，有些画家专画普通人家的厨房，让平常日子也有体面；画成一张图：
看故事 → 排位没那么硬 → 心里松）→
身边的例子（开会被点名，午休听段相声笑大老板；同学会比头衔，回家翻本写小面馆老板的小说；妈妈说“看看人家”，
一起看部老电影都哭了、话说开了；孩子考砸不吭声，画了张全家晚饭桌）→
具体做法（烦了挑讲普通人的片 / 看场喜剧笑笑大人物 / 拍一张身边的日常 / 记下戳你的那一句）→ 评论区互动。
书中观点为转述：Alain de Botton, Status Anxiety（Hamish Hamilton / Pantheon, 2004），第二部分“解决方法”第二章“艺术”；
中译本《身份的焦虑》（陈广兴、南治国译，上海译文出版社）。例子与做法为现实场景示意与据书中思路整理的建议，
不涉及任何真实影视作品、演员或画作。
"""

import math

import skia

from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross, doc,
                               face, join, rect, stick, underline)
from adler import kit as K

from .common import BOOK, episode

ACC = "#C8783A"
SQUARE_SHOT = 4

b = Board(size=(3600, 11700))
GOLD = "#E3A33B"


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.18 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    if k1 is None:
        k1 = k0 + max(0.5, 0.18 * len(s))
        if k1 > 3.85:                     # 镜头末尾写的字压缩到本镜内写完
            k1 = max(k0 + 0.35, 3.85)
    b.text(jj, k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def J():
    return len(b.shots) - 1


# ---------------------------------------------------------------- 本讲画法

def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12 if w < 200 else 40), P((x - w * 0.17, y + h / 2 - h * 0.13),
                                                           (x + w * 0.17, y + h / 2 - h * 0.13)))


def tv(x, y, w, h) -> skia.Path:
    """电视：屏幕 + 两条腿。"""
    return join(rect(x, y, w, h, 24), P((x - w * 0.3, y + h / 2), (x - w * 0.36, y + h / 2 + 50)),
                P((x + w * 0.3, y + h / 2), (x + w * 0.36, y + h / 2 + 50)))


def play(x, y, r=70) -> skia.Path:
    return P((x - r * 0.6, y - r), (x + r, y), (x - r * 0.6, y + r), close=True)


def train(x, y) -> skia.Path:
    """地铁车厢：车身 + 三扇窗 + 四个轮子。(x, y) 为车身中心。"""
    parts = [rect(x, y, 1100, 440, 50)]
    for dx in (-300, 0, 300):
        parts.append(rect(x + dx, y - 70, 210, 160, 14))
    for dx in (-380, -180, 180, 380):
        parts.append(circle(x + dx, y + 255, 32))
    parts.append(P((x - 550, y + 90), (x + 550, y + 90)))
    return join(*parts)


def ladder(x, top, bottom, w=240, step=130) -> skia.Path:
    parts = [P((x - w / 2, top), (x - w / 2, bottom)), P((x + w / 2, top), (x + w / 2, bottom))]
    yy = top + 70
    while yy < bottom:
        parts.append(P((x - w / 2, yy), (x + w / 2, yy)))
        yy += step
    return join(*parts)


def crown(x, y, w=110, h=70) -> skia.Path:
    """皇冠：(x, y) 为底边中点。"""
    return P((x - w / 2, y), (x - w / 2, y - h), (x - w / 4, y - h * 0.45), (x, y - h), (x + w / 4, y - h * 0.45),
             (x + w / 2, y - h), (x + w / 2, y), close=True)


def banana(x, y, s=1.0) -> skia.Path:
    """香蕉皮：中间一块 + 三瓣摊开。(x, y) 为地面中点。"""
    p = skia.Path()
    p.moveTo(x - 20 * s, y)
    p.quadTo(x, y - 40 * s, x + 20 * s, y)
    for dx, tx in ((-20, -75), (0, 5), (20, 80)):
        q = skia.Path()
        q.moveTo(x + dx * s, y - 12 * s)
        q.quadTo(x + (dx + tx) / 2 * s, y - 50 * s, x + tx * s, y - 4 * s)
        p.addPath(q)
    return p


def lying(x, y, s=1.0) -> skia.Path:
    """摔倒躺平的小人：(x, y) 为身体中点（地面上）。"""
    return join(circle(x - 150 * s, y - 40 * s, 40 * s), P((x - 105 * s, y - 30 * s), (x + 60 * s, y - 15 * s)),
                P((x + 60 * s, y - 15 * s), (x + 160 * s, y - 60 * s)), P((x + 60 * s, y - 15 * s), (x + 165 * s, y)),
                P((x - 40 * s, y - 25 * s), (x - 10 * s, y - 90 * s)), P((x - 40 * s, y - 25 * s), (x + 10 * s, y)))


def stove(x, y) -> skia.Path:
    """灶台 + 锅：(x, y) 为灶台中心。"""
    return join(rect(x, y, 320, 150, 10), P((x - 160, y - 30), (x + 160, y - 30)),
                P((x - 100, y - 75), (x - 80, y - 150), (x + 80, y - 150), (x + 100, y - 75)),
                P((x - 140, y - 140), (x + 140, y - 140)), circle(x - 90, y + 25, 18), circle(x + 90, y + 25, 18))


def window(x, y, w=200, h=160) -> skia.Path:
    return join(rect(x, y, w, h, 6), P((x, y - h / 2), (x, y + h / 2)), P((x - w / 2, y), (x + w / 2, y)))


def steam(x, y, n=3, gap=40, s=1.0) -> skia.Path:
    parts = []
    for i in range(n):
        dx = (i - (n - 1) / 2) * gap
        st = skia.Path()
        st.moveTo(x + dx, y)
        st.quadTo(x + dx - 20 * s, y - 30 * s, x + dx, y - 60 * s)
        st.quadTo(x + dx + 20 * s, y - 90 * s, x + dx, y - 120 * s)
        parts.append(st)
    return join(*parts)


def bowl(x, y, w=200) -> skia.Path:
    """一碗面：碗 + 面条 + 筷子。(x, y) 为碗口中点。"""
    body = skia.Path()
    body.moveTo(x - w / 2, y)
    body.quadTo(x, y + w * 0.75, x + w / 2, y)
    body.close()
    noodles = []
    for i in range(3):
        q = skia.Path()
        q.moveTo(x - w * 0.35, y - 6 - i * 10)
        q.quadTo(x - w * 0.1, y - 26 - i * 10, x + w * 0.05, y - 6 - i * 10)
        q.quadTo(x + w * 0.2, y + 12 - i * 10, x + w * 0.35, y - 6 - i * 10)
        noodles.append(q)
    sticks = join(P((x + w * 0.1, y - 30), (x + w * 0.55, y - 150)), P((x + w * 0.2, y - 25), (x + w * 0.65, y - 130)))
    return join(body, *noodles, sticks)


def pop_fn(draw, x, y, size, color):
    """弹出：0.35 拍内从 0 放大到 1.15 再回到 1。draw(c, x, y, size, color)。"""

    def fn(c, k, t):
        s = min(1.0, k / 0.35)
        s = s * (1.15 - 0.15 * s) if s < 1 else 1.0
        draw(c, x, y, size * s, color)
        return None

    return fn


def heart_fn(x, y, size, color=RED):
    return pop_fn(lambda c, xx, yy, s, col: K.heart(c, xx, yy, s, col), x, y, size, color)


def star_fn(x, y, size, color=GOLD):
    return pop_fn(lambda c, xx, yy, s, col: K.star(c, xx, yy, s, col), x, y, size, color)


def tear_fn(eyes, drop=90, r=9):
    """眼泪：从每只眼睛下方落下的蓝色泪滴。"""

    def fn(c, k, t):
        for ex, ey in eyes:
            yy = ey + 14 + drop * k
            p = skia.Path()
            p.moveTo(ex, yy - r * 2.2)
            p.quadTo(ex + r * 1.2, yy, ex, yy + r)
            p.quadTo(ex - r * 1.2, yy, ex, yy - r * 2.2)
            c.drawPath(p, K.paint(BLUE, 0.85))
        return None

    return fn


def eyes_of(x, y, s):
    hy = y - 290 * s
    return [(x - 15 * s, hy - 8 * s), (x + 15 * s, hy - 8 * s)]


# ---------------------------------------------------------------- 开局：被骂一天，回家看部电影哭了（镜头 1–6）

b.shot("被骂了一整天", "灵魂拷问", view=(950, 850, 0.85))
L(stick(620, 1150, 0.8, "point", tie=True), 0, 0.7, sfx="wood_high")
L(bubble(640, 720, 400, 130, -1), 1, 1.4, BLACK, 8, sfx="pop")
T("重做！", 640, 720, 66, RED, k0=1.4)
L(stick(1250, 1150, 0.75), 2, 2.5, BLUE, 9, sfx="wood_high")
L(face(1250, 1150, 0.75, "sad"), 2.5, 2.7, BLUE, 8)
T("第7版", 1250, 760, 64, RED, k0=3, sfx="pop")

b.shot("挤地铁回家", "灵魂拷问", view=(2650, 850, 0.85))
L(train(2650, 820), 0, 0.9, BLACK, 9, sfx="wood_high")
for n, dx in enumerate((-300, 300)):
    L(circle(2650 + dx, 760, 38), 1 + n * 0.2, 1.2 + n * 0.2, BLACK, 8, sfx="pop" if n == 0 else None)
T("22:30", 2650, 470, 66, RED, k0=2, sfx="pop")
L(circle(2650, 760, 38), 3, 3.2, BLUE, 8, sfx="rim")
L(face(2650, 760 + 290 * 0.85, 0.85, "sad"), 3.2, 3.4, BLUE, 7)
T("挤了一小时", 2650, 1190, 54, k0=3.4)

TVX, TVY = 850, 1680
ME = (1220, 2250, 0.55)
b.shot("随手点开部电影", "灵魂拷问", view=(950, 1850, 0.85))
L(tv(TVX, TVY, 760, 480), 0, 0.8, BLACK, 9, sfx="wood_high")
L(play(TVX, TVY), 1, 1.3, RED, 9, sfx="pop")
L(stick(*ME[:2], ME[2], "hold"), 2, 2.5, BLUE, 9, sfx="wood_high")
T("讲小人物的片", TVX, 2045, 54, k0=3, sfx="pop")

b.shot("主角也被人看低", "灵魂拷问", view=(950, 1850, 0.85))
b.erase(J(), 0, 0.4, TVX, TVY, 220, 220)
H(0, "shaker")
L(stick(700, 1880, 0.55, "point", tie=True), 1, 1.5, BLACK, 8, sfx="wood_high")
L(stick(1020, 1880, 0.4), 2, 2.4, BLACK, 8, sfx="pop")
L(face(1020, 1880, 0.4, "sad"), 3, 3.2, BLUE, 7, sfx="rim")

b.shot("看着看着就哭了", "灵魂拷问", view=(950, 1850, 0.85))
L(face(*ME[:2], ME[2], "sad"), 0, 0.3, BLUE, 8, sfx="pop")
b.custom(J(), 1, 1.8, tear_fn(eyes_of(*ME)), sfx="pop")
b.custom(J(), 2, 2.8, tear_fn(eyes_of(*ME)), sfx="pop")
T("哭了", 1440, 1990, 70, RED, k0=3, sfx="rim")

b.shot("哭完怎么松了？", "灵魂拷问", view=(1820, 1400, 0.38), flashes=[0])
T("？", 2650, 1800, 520, RED, k0=0, k1=0.6, sfx="kick")
T("哭完，心里反倒松了", 1800, 330, 100, k0=1.0, k1=2.4, sfx="pop")
H(3, "ding")

# ---------------------------------------------------------------- 书中观点（镜头 7–17）

b.shot("有本书讲过这个", "身份的焦虑", view=(1050, 2950, 0.9))
L(book(750, 2950, 420, 280), 0, 1.0, sfx="wood_low")
T("《身份的焦虑》", 750, 2710, 72, GREEN, k0=1.0, sfx="pop")
T("德波顿", 750, 3190, 54, k0=2.0, sfx="pop")
T("解法之二：艺术", 1380, 2950, 56, RED, k0=3.0, sfx="pop")

LAD = (3020, 2620, 3250)
b.shot("小说漫画悲喜剧", "书中观点 · 艺术", view=(2650, 2980, 0.85))
L(ladder(LAD[0], LAD[1], LAD[2]), 0, 0.8, BLACK, 9, sfx="wood_high")
L(stick(LAD[0], LAD[1], 0.45, tie=True), 1, 1.4, BLACK, 8, sfx="pop")
T("地位排行", LAD[0], 3330, 56, k0=1.4)
T("小说  漫画", 2300, 2800, 66, BLUE, k0=2, sfx="pop")
T("悲剧  喜剧", 2300, 2980, 66, BLUE, k0=3, sfx="pop")

b.shot("一直在批评排位", "书中观点 · 挑刺", view=(2650, 2980, 0.85), shake=[0], flashes=[0])
L(cross(LAD[0], 2930, 290), 0, 0.4, RED, 18, sfx="kick")
L(arrow((2470, 3050), (2860, 3150), -0.2, 40), 1, 1.4, GREEN, 9, sfx="wood_high")
T("都在挑刺", 2300, 3250, 72, RED, k0=2, sfx="pop")
H(3, "ding")

b.shot("悲剧写人摔下来", "书中观点 · 悲剧", view=(1050, 4300, 0.85))
T("悲剧", 1050, 3880, 76, BLUE, k0=0, sfx="pop")
L(join(P((520, 4150), (850, 4150), (850, 4700)), P((850, 4700), (1550, 4700))), 1, 1.6, BLACK, 9, sfx="wood_high")
L(arrow((800, 4080), (1150, 4560), -0.35, 44), 2, 2.5, RED, 9, sfx="rim")
L(lying(1250, 4700, 0.7), 3, 3.5, BLUE, 8, sfx="tom")
T("输了", 1300, 4520, 54, BLUE, k0=3.5)

b.shot("你会心疼他", "书中观点 · 悲剧", view=(1050, 4300, 0.85))
L(stick(620, 4700, 0.5, "hold"), 0, 0.5, BLACK, 9, sfx="wood_high")
L(face(620, 4700, 0.5, "sad"), 0.5, 0.6, BLACK, 7)
b.custom(J(), 1, 1.4, heart_fn(620, 4440, 90), sfx="pop")
T("跟我一样", 620, 4290, 54, RED, k0=2, sfx="pop")
T("心疼输了的人", 640, 4040, 56, RED, k0=3, sfx="ding")

BOSS = (2700, 4650, 0.9)
b.shot("喜剧专笑大人物", "书中观点 · 喜剧", view=(2650, 4300, 0.85))
T("喜剧", 2650, 3880, 76, BLUE, k0=0, sfx="pop")
L(stick(*BOSS[:2], BOSS[2], tie=True), 1, 1.6, BLACK, 10, sfx="wood_high")
L(crown(BOSS[0], BOSS[1] - 290 * BOSS[2] - 48), 2, 2.4, GOLD, 9, sfx="pop")
T("大老板", 3080, 4250, 60, k0=3, sfx="pop")

b.shot("台下笑成一片", "书中观点 · 喜剧", view=(2650, 4300, 0.85))
L(banana(BOSS[0] + 90, BOSS[1], 1.0), 0, 0.4, GOLD, 8, sfx="pop")
L(face(*BOSS[:2], BOSS[2], "sad"), 0.4, 0.6, BLACK, 8)
T("啪叽！", 3080, 4520, 70, RED, k0=1, sfx="rim")
for n, x in enumerate((2200, 2330, 2460)):
    L(stick(x, 4700, 0.35), 2 + n * 0.2, 2.3 + n * 0.2, BLACK, 7, sfx="wood_high" if n == 0 else None)
    L(face(x, 4700, 0.35, "smile"), 2.3 + n * 0.2, 2.4 + n * 0.2, BLACK, 6)
T("哈哈哈", 2330, 4440, 62, RED, k0=3, sfx="pop")

FR = (1050, 5600)
b.shot("有画家专画厨房", "书中观点 · 画", view=(1050, 5600, 0.85))
L(join(rect(*FR, 900, 640, 10), rect(*FR, 840, 580, 6)), 0, 0.8, BLACK, 9, sfx="wood_low")
L(stove(860, 5800), 1, 1.6, BLACK, 8, sfx="wood_high")
L(stick(1250, 5880, 0.55, "hold", hair=True), 2, 2.5, BLUE, 8, sfx="pop")
L(window(820, 5440), 3, 3.3, BLACK, 7, sfx="pop")
L(steam(860, 5640, 3, 45, 0.7), 3.3, 3.7, BLACK, 5)
T("一幅厨房的画", 1050, 5200, 56, k0=3.4)

b.shot("平常日子也体面", "书中观点 · 画", view=(1050, 5650, 0.85))
for n, (sx, sy) in enumerate(((610, 5300), (1490, 5300))):
    b.custom(J(), n * 0.2, n * 0.2 + 0.4, star_fn(sx, sy, 50), sfx="pop" if n == 0 else None)
T("平常日子", 1050, 6010, 64, k0=1, sfx="pop")
T("也有体面", 1050, 6110, 64, RED, k0=2, sfx="pop")
L(underline(900, 1200, 6160), 3, 3.4, RED, 7, sfx="ding")

b.shot("排位没那么硬", "书中观点 · 一张图", view=(2650, 5600, 0.85))
T("悲剧 → 心疼输家", 2650, 5300, 60, k0=0, sfx="pop")
T("喜剧 → 笑大人物", 2650, 5450, 60, k0=1, sfx="pop")
T("画 → 平常体面", 2650, 5600, 60, k0=2, sfx="pop")
T("排位松一松", 2650, 5850, 84, RED, k0=3, sfx="ding")

b.shot("故事替你松口气", "书中观点 · 一张图", view=(1800, 4700, 0.36))
L(join(arrow((1550, 4700), (2250, 5250), -0.15, 44), arrow((1600, 5600), (2200, 5600), 0.0, 44)), 0, 0.7, GREEN, 10,
  sfx="wood_high")
T("看故事 → 心里松", 1800, 6300, 120, RED, k0=1, k1=2.4, sfx="pop")
H(3, "ding")

# ---------------------------------------------------------------- 身边的例子（镜头 18–28）

CARDS = [(950, 7300), (2650, 7300), (950, 8200), (2650, 8200)]
b.shot("身边也常碰到", "身边的例子", view=(1800, 7750, 0.355))
T("身边的例子", 1800, 6750, 130, k0=0, sfx="pop")
for n, (x, y) in enumerate(CARDS):
    L(rect(x, y, 1200, 820, 40), 1.5 + n * 0.5, 1.95 + n * 0.5, GREEN, 8, sfx="wood_high" if n in (1, 3) else None)

b.shot("开会又被点名", "例子 · 职场", view=(950, 7300, 0.85))
L(stick(600, 7600, 0.7, "point", tie=True), 0, 0.6, sfx="wood_high")
L(bubble(680, 7120, 420, 120, -1), 1, 1.4, BLACK, 8, sfx="pop")
T("这都没做好", 680, 7120, 52, RED, k0=1.4)
L(stick(1250, 7600, 0.6), 2, 2.5, BLUE, 9, sfx="wood_high")
T("……", 1250, 7240, 66, BLUE, k0=3, sfx="rim")

b.shot("午休听段相声", "例子 · 职场", view=(950, 7300, 0.85))
b.erase(J(), 0, 0.5, 650, 7300, 620, 760)
H(0, "shaker")
L(phone(700, 7350, 260, 400), 1, 1.5, BLACK, 9, sfx="wood_high")
T("相声", 700, 7240, 56, k0=2, sfx="pop")
L(stick(700, 7480, 0.3, tie=True), 2.4, 2.7, BLACK, 6)
T("笑大老板", 700, 7630, 50, GREEN, k0=2.7)
L(face(1250, 7600, 0.6, "smile"), 3, 3.2, BLUE, 8, sfx="pop")
T("哈哈", 1250, 7100, 60, RED, k0=3.2)

b.shot("同学会比头衔", "例子 · 生活", view=(2650, 7300, 0.85))
L(stick(2300, 7600, 0.6, tie=True), 0, 0.5, BLACK, 9, sfx="wood_high")
T("总监", 2300, 7330, 56, k0=1, sfx="pop")
L(stick(2600, 7600, 0.6, tie=True), 1.4, 1.9, BLACK, 9)
T("经理", 2600, 7330, 56, k0=2, sfx="pop")
L(stick(3000, 7600, 0.6), 3, 3.4, BLUE, 9, sfx="wood_high")
T("我…", 3000, 7330, 56, BLUE, k0=3.4)

b.shot("回家翻本小说", "例子 · 生活", view=(2650, 7300, 0.85))
b.erase(J(), 0, 0.5, 2450, 7400, 580, 620)
H(0, "shaker")
L(book(2450, 7200, 360, 240), 1, 1.6, BLACK, 9, sfx="wood_low")
T("主角开小面馆", 2450, 7450, 52, k0=2, sfx="pop")
L(face(3000, 7600, 0.6, "smile"), 3, 3.2, BLUE, 8, sfx="pop")
T("日子也挺香", 2450, 7570, 52, GREEN, k0=3.2)

MOM = (600, 8500, 0.65)
ME3 = (1250, 8500, 0.6)
b.shot("妈说看看人家", "例子 · 家庭", view=(950, 8200, 0.85))
L(stick(*MOM[:2], MOM[2], hair=True), 0, 0.5, BLACK, 9, sfx="wood_high")
L(bubble(720, 7990, 400, 120, -1), 1, 1.4, BLACK, 8, sfx="pop")
T("看看人家", 720, 7990, 54, k0=1.4)
L(stick(*ME3[:2], ME3[2]), 2, 2.5, BLUE, 9, sfx="wood_high")
T("……", 1250, 8130, 66, BLUE, k0=3, sfx="rim")

b.shot("一起看部老电影", "例子 · 家庭", view=(950, 8200, 0.85))
b.erase(J(), 0, 0.5, 900, 8040, 920, 270)
H(0, "shaker")
L(tv(950, 8030, 420, 240), 1, 1.5, BLACK, 9, sfx="wood_high")
L(face(*MOM[:2], MOM[2], "sad"), 2, 2.2, BLACK, 7, sfx="pop")
L(face(*ME3[:2], ME3[2], "sad"), 2.2, 2.4, BLUE, 7)
b.custom(J(), 2.2, 3.0, tear_fn(eyes_of(*MOM) + eyes_of(*ME3)))
T("话说开了", 950, 8400, 54, GREEN, k0=3, sfx="ding")

KID = (3000, 8500, 0.5)
b.shot("孩子考砸了", "例子 · 孩子", view=(2650, 8200, 0.85))
L(doc(2330, 8040, 170, 210, 3), 0, 0.5, BLACK, 8, sfx="wood_high")
T("58", 2500, 7930, 72, RED, k0=1, sfx="pop")
L(stick(*KID[:2], KID[2]), 2, 2.4, BLUE, 8, sfx="wood_high")
T("不吭声", 3000, 8250, 50, BLUE, k0=3, sfx="rim")

b.shot("画了张晚饭桌", "例子 · 孩子", view=(2650, 8200, 0.85))
L(rect(2550, 8390, 440, 300, 8), 0, 0.4, BLACK, 8, sfx="pop")
L(join(P((2380, 8450), (2720, 8450)), P((2420, 8450), (2420, 8510)), P((2680, 8450), (2680, 8510)),
       circle(2440, 8395, 26), circle(2550, 8385, 30), circle(2660, 8400, 22),
       bowl(2550, 8445, 60)), 1, 1.7, BLUE, 6, sfx="wood_high")
T("我家晚饭", 2550, 8290, 46, k0=2, sfx="pop")
b.erase(J(), 2.4, 2.8, 3000, 8250, 240, 80)
L(face(*KID[:2], KID[2], "smile"), 3, 3.2, BLUE, 7, sfx="ding")
T("画得真好", 3000, 8250, 50, GREEN, k0=3.2)

b.shot("都被排位压着", "身边的例子", view=(1800, 7750, 0.355))
for n, (x, y) in enumerate(CARDS):
    T("被看低", x + 400, y - 320, 90, RED, k0=n, sfx="pop")

b.shot("故事帮你喘口气", "身边的例子", view=(1800, 7750, 0.355), shake=[0])
T("一个故事，松一口气", 1800, 8770, 140, RED, k0=0, k1=0.9, sfx="kick")
H(2, "ding")

# ---------------------------------------------------------------- 具体做法（镜头 29–41）

SOL = [(950, 9700), (2650, 9700), (950, 10600), (2650, 10600)]
b.shot("心里堵就这样做", "具体做法", view=(1800, 10150, 0.355))
T("心里堵，这样做", 1800, 9150, 130, k0=0, k1=1.4, sfx="pop")
for n, (x, y) in enumerate(SOL):
    L(rect(x, y, 1200, 820, 40), 2 + n * 0.4, 2.35 + n * 0.4, GREEN, 8, sfx="wood_high" if n == 0 else None)

b.shot("烦了挑小人物片", "第一步 · 挑片子", view=(950, 9700, 0.85))
T("① 挑讲小人物的片", 950, 9400, 66, BLUE, k0=0, sfx="pop")
L(join(rect(780, 9690, 240, 300, 10), rect(1120, 9690, 240, 300, 10)), 1, 1.6, BLACK, 8, sfx="wood_high")
T("小面馆", 780, 9610, 46, k0=2, sfx="pop")
L(stick(780, 9810, 0.33, "hold"), 2.4, 2.8, BLUE, 6)
T("修车铺", 1120, 9610, 46, k0=3, sfx="pop")
L(stick(1120, 9810, 0.33, "up"), 3.4, 3.8, BLUE, 6)

b.shot("看他怎么扛过来", "第一步 · 挑片子", view=(950, 9750, 0.85))
T("他也被看低过", 950, 9930, 50, k0=0, sfx="pop")
L(arrow((1230, 9915), (1230, 10030), 0.0, 24), 1, 1.3, RED, 7, sfx="wood_high")
T("最后扛过来了", 950, 10045, 50, GREEN, k0=2, sfx="pop")
L(check(1330, 10035, 34), 3, 3.3, GREEN, 9, sfx="ding")

BOSS2 = (2700, 9950, 0.6)
b.shot("看场喜剧笑笑", "第二步 · 看喜剧", view=(2650, 9700, 0.85))
T("② 看喜剧笑一笑", 2650, 9400, 66, BLUE, k0=0, sfx="pop")
L(stick(*BOSS2[:2], BOSS2[2], tie=True), 1, 1.5, BLACK, 9, sfx="wood_high")
L(crown(BOSS2[0], BOSS2[1] - 290 * BOSS2[2] - 32, 80, 50), 2, 2.4, GOLD, 8, sfx="pop")
T("大老板", 3060, 9700, 54, k0=3, sfx="pop")

b.shot("大人物也摔跤", "第二步 · 看喜剧", view=(2650, 9700, 0.85))
L(banana(BOSS2[0] + 70, BOSS2[1], 0.8), 0, 0.4, GOLD, 7, sfx="pop")
T("啪叽！", 3060, 9860, 60, RED, k0=1, sfx="rim")
L(face(*BOSS2[:2], BOSS2[2], "sad"), 2, 2.2, BLACK, 7, sfx="wood_high")
T("哈哈", 2300, 9600, 60, RED, k0=3, sfx="pop")

b.shot("笑完气就顺了", "第二步 · 看喜剧", view=(2650, 9700, 0.85))
L(stick(2300, 10050, 0.45), 0, 0.4, BLUE, 8, sfx="wood_high")
L(face(2300, 10050, 0.45, "smile"), 1, 1.2, BLUE, 7, sfx="pop")
T("气顺了", 2300, 9780, 56, GREEN, k0=2, sfx="pop")
L(underline(2160, 2440, 10085, 10, 30), 3, 3.4, RED, 6, sfx="ding")

PH = (950, 10650)
b.shot("拍张日常照片", "第三步 · 拍日常", view=(950, 10600, 0.85))
T("③ 拍张日常", 950, 10300, 66, BLUE, k0=0, sfx="pop")
L(phone(*PH, 340, 460), 1, 1.5, BLACK, 9, sfx="wood_high")
L(bowl(950, 10660, 200), 2, 2.6, BLACK, 7, sfx="pop")
L(steam(930, 10630, 3, 40, 0.6), 3, 3.4, BLACK, 5, sfx="pop")

b.shot("身边的小日子", "第三步 · 拍日常", view=(950, 10600, 0.85))
T("妈煮的面", 1360, 10480, 50, k0=0, sfx="pop")
T("楼下早点摊", 1360, 10620, 50, k0=1, sfx="pop")
T("下班的晚霞", 1360, 10760, 50, k0=2, sfx="pop")
b.custom(J(), 3, 3.4, heart_fn(560, 10600, 90), sfx="ding")

b.shot("平凡也挺好看", "第三步 · 拍日常", view=(950, 10600, 0.85))
L(rect(*PH, 440, 540, 6), 0, 0.6, GOLD, 9, sfx="wood_low")
for n, (sx, sy) in enumerate(((700, 10400), (1200, 10400))):
    b.custom(J(), 1 + n * 0.2, 1.4 + n * 0.2, star_fn(sx, sy, 40), sfx="pop" if n == 0 else None)
T("也挺好看", 950, 10970, 52, RED, k0=2, sfx="pop")
L(check(1180, 10965, 32), 3, 3.3, GREEN, 9, sfx="ding")

NOTE = (2480, 10650)
YOU4 = (3000, 10850, 0.55)
b.shot("记下戳你那句", "第四步 · 记一句", view=(2650, 10600, 0.85))
T("④ 记下那一句", 2650, 10300, 66, BLUE, k0=0, sfx="pop")
L(doc(*NOTE, 300, 380, 0), 1, 1.5, BLACK, 8, sfx="wood_high")
T("他跟我一样", NOTE[0], 10600, 46, RED, k0=2, sfx="pop")
L(stick(*YOU4[:2], YOU4[2], "hold"), 3, 3.5, BLUE, 8, sfx="pop")

b.shot("烦了翻出来看", "第四步 · 记一句", view=(2650, 10600, 0.85))
L(face(*YOU4[:2], YOU4[2], "smile"), 0, 0.2, BLUE, 7, sfx="pop")
T("下回烦了", NOTE[0], 10740, 46, k0=1, sfx="pop")
T("翻出来看", 2650, 10965, 52, GREEN, k0=2, sfx="pop")
L(check(2860, 10960, 32), 3, 3.3, GREEN, 9, sfx="ding")

b.shot("都是小事一件", "具体做法", view=(1800, 10150, 0.355))
for n, (x, y) in enumerate(SOL):
    L(check(x + 500, y - 300, 50), n, n + 0.3, GREEN, 10, sfx="ding" if n % 2 else "pop")

b.shot("烦了就看个故事", "一句话", view=(1800, 6300, 0.235))
H(0, "cymbal", 0.5)
H(2, "ding")

b.shot("评论区聊聊", "评论区见", view=(1800, 11400, 0.8))
T("哪部片让你哭过？", 1800, 11320, 80, RED, k0=0.5, k1=1.8)
T("下一讲：什么样才算混得好，谁说了算？", 1800, 11480, 50, k0=2.0, k1=3.2)
H(0, "cymbal", 0.5)
H(1, "pop")
H(2, "wood_high", 0.7)
b.hit(len(b.shots) - 1, 4, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(7, "art", "艺术", "为什么看部电影，心里就松了？", ACC, b.shots,
                 [f"{BOOK}第二部分“解决方法”第二章“艺术”（转述）",
                  "原书：Alain de Botton, Status Anxiety, Hamish Hamilton / Pantheon, 2004",
                  "中译本：《身份的焦虑》，陈广兴、南治国译，上海译文出版社"],
                 "看部小人物电影|心里就【松了】", 10,
                 ["书中观点均为转述：小说、讽刺漫画、悲剧、喜剧一直在批评地位体系；悲剧让人同情摔下来的失败者，"
                  "喜剧嘲笑有权有势的人；有些画家专画普通人的日常（如厨房、家务），让平凡生活显得有尊严"
                  "（第二部分“解决方法”第二章“艺术”）。出处：Alain de Botton, Status Anxiety (Hamish Hamilton / Pantheon, "
                  "2004)，中译本《身份的焦虑》（陈广兴、南治国译，上海译文出版社）。上屏均为转述，不是逐字引文。",
                  "被骂改方案、挤地铁、小人物电影、相声、同学会、小面馆小说、老电影、孩子画晚饭桌均为现实场景示意，"
                  "不指向任何具体公司、个人或真实影视作品、演员、画作；时间、版本号、分数为示意；梯子、皇冠、香蕉皮、"
                  "厨房画为对书中观点的通俗化示意。",
                  "四步做法（烦了挑讲普通人的片子、看喜剧笑笑大人物、拍一张身边的日常、记下戳你的那一句）为据书中思路整理的建议。"],
                 tags="#电影 #治愈")
    return b.attach(ep)
