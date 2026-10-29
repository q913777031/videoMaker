"""01 孤独是信号（白板手绘版）：一个人吃饭，心里为什么发空？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（2026-10 观众反馈“切太快看不清”后改为慢速讲解版）。
叙事：打工人切身问题开局（下班回出租屋、一个人吃外卖刷手机 → 心里发空）→
书中观点（亮书；饿、渴、疼都在提醒身体缺了什么，孤独也是这样一种信号，催人回到别人身边；它是进化留下来的：
祖先落单就危险，怕落单、赶紧回到人群的人更容易活下来；画成“饿 → 吃饭 / 渴 → 喝水 / 孤独 → 找人”一张图）→
身边的例子（午饭各吃各的、刚到新城市、爸妈在老家；最后连到同一个信号）→
具体做法（认出信号、别骂自己 / 当天联系一个人，说件具体的事 / 约顿饭）→ 评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, 2008；
中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, building, circle, cross, desk,
                               face, join, rect, scribble, stick, underline)

from .common import BOOK, episode

ACC = "#C2603A"
SQUARE_SHOT = 6                 # 场景 7：小人 + “饿 / 渴 / 孤独”信号图

b = Board(size=(3600, 10900))
OY = 0                          # 身边的例子起整体下移，避免上一块的字漏进页眉


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(jj, k0, k1, s, x, y + OY, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    if OY:
        path = skia.Path(path)
        path.offset(0, OY)
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


# ---------------------------------------------------------------- 本讲画法

def moon(x, y, r=90) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, 12), P((x - 12, y + h / 2 - 16), (x + 12, y + h / 2 - 16)))


def takeout(x, y, s=1.0) -> skia.Path:
    """外卖盒 + 一双筷子：(x, y) 为盒身中心。"""
    return join(P((x - 80 * s, y - 40 * s), (x - 60 * s, y + 50 * s), (x + 60 * s, y + 50 * s), (x + 80 * s, y - 40 * s),
                  close=True),
                P((x - 92 * s, y - 40 * s), (x - 70 * s, y - 62 * s), (x + 70 * s, y - 62 * s), (x + 92 * s, y - 40 * s)),
                P((x + 10 * s, y - 70 * s), (x + 110 * s, y - 160 * s)), P((x + 35 * s, y - 66 * s), (x + 130 * s, y - 145 * s)))


def heart(x, y, r=100) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def bowl(x, y, r=90, steam=True) -> skia.Path:
    """碗：(x, y) 为碗口中点。"""
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r * 0.9, 2 * r, 1.8 * r), 0, 180)
    parts = [p, P((x - r - 12, y), (x + r + 12, y)), P((x - r * 0.35, y + r * 0.95), (x + r * 0.35, y + r * 0.95))]
    if steam:
        for dx in (-r * 0.3, r * 0.3):
            st = skia.Path()
            st.moveTo(x + dx, y - 20)
            st.quadTo(x + dx - 20, y - 50, x + dx, y - 80)
            st.quadTo(x + dx + 20, y - 110, x + dx, y - 140)
            parts.append(st)
    return join(*parts)


def glass(x, y, s=1.0) -> skia.Path:
    return join(P((x - 45 * s, y - 70 * s), (x - 35 * s, y + 70 * s), (x + 35 * s, y + 70 * s), (x + 45 * s, y - 70 * s)),
                P((x - 41 * s, y - 25 * s), (x + 41 * s, y - 25 * s)))


def bolt(x, y, s=1.0) -> skia.Path:
    return P((x + 25 * s, y - 80 * s), (x - 30 * s, y + 5 * s), (x + 12 * s, y + 5 * s), (x - 22 * s, y + 80 * s))


def lamp(x, y, s=1.0) -> skia.Path:
    """信号灯：圆顶警示灯 + 底座 + 光芒 + 叹号。(x, y) 为灯罩中心。"""
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeXYWH(x - 55 * s, y - 60 * s, 110 * s, 120 * s), 180, 180)
    parts = [dome, P((x - 55 * s, y), (x - 55 * s, y + 30 * s)), P((x + 55 * s, y), (x + 55 * s, y + 30 * s)),
             rect(x, y + 45 * s, 150 * s, 30 * s, 8 * s),
             P((x, y - 38 * s), (x, y - 2 * s)), circle(x, y + 14 * s, 4 * s)]
    for dx, dy, ex, ey in ((0, -80, 0, -120), (-62, -58, -92, -88), (62, -58, 92, -88), (-80, -10, -120, -10),
                           (80, -10, 120, -10)):
        parts.append(P((x + dx * s, y + dy * s), (x + ex * s, y + ey * s)))
    return join(*parts)


def fire(x, y, s=1.0) -> skia.Path:
    """篝火：两根交叉的柴 + 火苗。(x, y) 为柴堆中心。"""
    fl = skia.Path()
    fl.moveTo(x, y - 170 * s)
    fl.quadTo(x + 85 * s, y - 70 * s, x + 35 * s, y)
    fl.lineTo(x - 35 * s, y)
    fl.quadTo(x - 85 * s, y - 70 * s, x, y - 170 * s)
    inner = skia.Path()
    inner.moveTo(x, y - 90 * s)
    inner.quadTo(x + 35 * s, y - 40 * s, x, y - 5 * s)
    inner.quadTo(x - 35 * s, y - 40 * s, x, y - 90 * s)
    return join(fl, inner, P((x - 100 * s, y + 35 * s), (x + 100 * s, y - 5 * s)),
                P((x - 100 * s, y - 5 * s), (x + 100 * s, y + 35 * s)))


def eyes(x, y, s=1.0) -> skia.Path:
    """暗处的一双眼睛（野兽）。"""
    parts = []
    for dx in (-45, 45):
        p = skia.Path()
        p.addOval(skia.Rect.MakeXYWH(x + (dx - 24) * s, y - 11 * s, 48 * s, 22 * s))
        parts += [p, circle(x + dx * s, y, 5 * s)]
    parts += [P((x - 75 * s, y - 40 * s), (x - 20 * s, y - 20 * s)), P((x + 75 * s, y - 40 * s), (x + 20 * s, y - 20 * s))]
    return join(*parts)


def suitcase(x, y, s=1.0) -> skia.Path:
    return join(rect(x, y, 120 * s, 100 * s, 12 * s),
                P((x - 25 * s, y - 50 * s), (x - 25 * s, y - 75 * s), (x + 25 * s, y - 75 * s), (x + 25 * s, y - 50 * s)),
                P((x - 60 * s, y), (x + 60 * s, y)))


def house(x, y, w=280, h=230) -> skia.Path:
    """平房：(x, y) 为地面中点。"""
    return join(P((x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)),
                P((x - w / 2 - 35, y - h), (x, y - h - 150), (x + w / 2 + 35, y - h)),
                P((x - 35, y), (x - 35, y - 110), (x + 35, y - 110), (x + 35, y)), rect(x + w / 4 + 10, y - h + 70, 60, 60, 4))


def contacts(x, y, w=230, n=3) -> skia.Path:
    parts = []
    for i in range(n):
        yy = y + i * 90
        parts += [circle(x - w / 2 + 50, yy, 22), P((x - w / 2 + 90, yy), (x + w / 2 - 30, yy))]
    return join(*parts)


def rays(x, y, w, h) -> skia.Path:
    """字周围的爆点短线。"""
    parts = []
    for dx, dy, ex, ey in ((-1, -1, -1.25, -1.5), (0, -1.15, 0, -1.6), (1, -1, 1.25, -1.5)):
        parts.append(P((x + dx * w / 2, y + dy * h / 2), (x + ex * w / 2, y + ey * h / 2)))
    return join(*parts)

# ---------------------------------------------------------------- 开局：一个人吃饭（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=(view[0], view[1] + OY, view[2]), bars=bars, **kw)


scene("下班回到出租屋", "灵魂拷问", (950, 850, 0.85), bars=2)
L(building(650, 1150), 0, 0.9, sfx="wood_high")
T("出租屋", 650, 1225, 54, k0=1, k1=1.8)
L(moon(1250, 500, 80), 2, 2.9, BLACK, 9, sfx="pop")
T("21:30", 1250, 680, 70, RED, k0=3, k1=4.2, sfx="pop")
L(stick(1080, 1250, 0.8, "down"), 5, 5.8, sfx="wood_high")
L(face(1080, 1250, 0.8, "flat"), 5.8, 6.0)

scene("吃着外卖，心里发空", "灵魂拷问", (2650, 850, 0.85), shake=[6], flashes=[6])
L(desk(2620, 1050, 420), 0, 0.9, sfx="wood_high")
L(takeout(2490, 1000), 1, 1.9, BLACK, 9, sfx="pop")
L(stick(2250, 1250, 0.8, "hold"), 2, 2.8, sfx="wood_high")
L(face(2250, 1250, 0.8, "flat"), 2.8, 3.0)
L(phone(2365, 1050), 3, 3.8, BLUE, 8, sfx="pop")
T("外卖 × 1", 2900, 640, 70, RED, k0=4, k1=5.2, sfx="pop")
T("心里为什么发空？", 2650, 440, 90, RED, k0=6, k1=8, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 3–7）

scene("饿渴疼，都在报信", "孤独是可耻的 · 书中观点", (1050, 3000, 0.9))
L(book(750, 3000, 420, 280), 0, 0.9, sfx="wood_low")
T("孤独是可耻的", 750, 2760, 72, GREEN, k0=1, k1=2.5, sfx="pop")
L(bowl(1300, 2800, 70), 3, 3.8, BLACK, 9, sfx="pop")
T("饿", 1480, 2810, 70, RED, k0=3.8, k1=4.1)
L(glass(1300, 3030, 0.9), 4.4, 5.2, BLACK, 9)
T("渴", 1480, 3030, 70, RED, k0=5.2, k1=5.5)
L(bolt(1300, 3260), 6, 6.8, RED, 10, sfx="rim")
T("疼", 1480, 3260, 70, RED, k0=6.8, k1=7.1)

scene("孤独也是信号", "书中观点 · 孤独是信号", (1050, 3200, 0.75), shake=[0], flashes=[0])
T("孤独 = 信号", 1000, 3430, 120, RED, k0=0, k1=1.8, sfx="kick")
L(rays(1000, 3430, 760, 150), 2, 2.8, RED, 8, sfx="pop")
L(underline(680, 1320, 3525), 3, 3.8, RED, 9, sfx="ding")
L(lamp(600, 3730, 0.9), 4, 4.9, RED, 9, sfx="wood_high")
T("催你回到别人身边", 1130, 3740, 70, k0=5, k1=7, sfx="pop")

VA = (2650, 3150, 0.75)
scene("几万年前，落单就危险", "书中观点 · 进化", VA)
T("几万年前", 2600, 2560, 70, k0=0, k1=1, sfx="pop")
L(fire(2550, 3250), 1, 1.9, BLACK, 9, sfx="wood_high")
L(join(stick(2330, 3400, 0.6, "down"), stick(2770, 3400, 0.6, "down")), 2, 2.9, BLACK, 8, sfx="pop")
L(stick(3120, 3400, 0.5, "shrug"), 3, 3.9, BLUE, 8, sfx="wood_high")
L(eyes(3110, 2940), 5, 5.8, BLACK, 7, sfx="pop")
T("危险", 3110, 3085, 64, RED, k0=6, k1=6.8, sfx="rim")

ME = (1750, 4450)               # 今天的“我们”
scene("怕落单，传到了今天", "书中观点 · 进化", (2520, 3800, 0.55))
L(arrow((3050, 3300), (2880, 3300), 0.25, 40), 0, 0.9, GREEN, 9, sfx="wood_high")
T("回到火边，活下来", 2550, 3620, 60, GREEN, k0=1, k1=3, sfx="pop")
L(arrow((2300, 3690), (1850, 4060), 0.1, 44), 3, 3.9, GREEN, 9, sfx="wood_high")
L(stick(*ME, 0.75, "down"), 4, 4.8, BLACK, 10, sfx="pop")
L(face(*ME, 0.75, "flat"), 4.8, 5.0)
T("今天的我们", ME[0], ME[1] + 60, 50, k0=6, k1=7.25, sfx="pop")

RX = 2450
ROWS = [("饿 → 吃饭", 3910, BLACK), ("渴 → 喝水", 4110, BLACK), ("孤独 → 找人", 4310, RED)]
scene("孤独了，就去找人", "书中观点 · 一张图", (2200, 4170, 0.8))
for n in range(3):
    T(ROWS[n][0], RX, ROWS[n][1], 72, ROWS[n][2], k0=n * 2, sfx="pop" if n < 2 else "tom")
L(heart(ME[0], 4320, 38), 6, 6.8, RED, 8, sfx="pop")
L(arrow((ME[0] + 80, 4320), (RX - 250, 4315), 0.05, 34), 7, 7.8, RED, 8, sfx="ding")

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

OY = 550
scene("想约饭，又不好意思", "例子 · 工位午饭", (840, 5300, 0.85))
L(join(desk(800, 5400, 320), desk(1270, 5400, 320)), 0, 0.9, sfx="wood_high")
L(join(takeout(690, 5350, 0.6), takeout(1160, 5350, 0.6)), 1, 1.9, BLACK, 8, sfx="pop")
L(join(stick(560, 5600, 0.6, "down"), stick(1035, 5600, 0.6, "down")), 2, 2.9, sfx="wood_high")
L(bubble(780, 5090, 280, 140, -1), 3, 3.8, BLACK, 8, sfx="pop")
T("一起吃？", 780, 5090, 54, k0=3.8, k1=4.8)
L(scribble(780, 5090, 280, 140, 7), 5, 5.8, RED, 7, sfx="pop")
T("算了", 1060, 5090, 56, BLUE, k0=6, k1=6.8, sfx="rim")

scene("刚到新城市，能约谁", "例子 · 新城市", (2760, 5300, 0.85))
L(join(building(2330, 5600, 200, 300), building(2540, 5600, 180, 400)), 0, 0.9, sfx="wood_high")
L(join(stick(2780, 5650, 0.7, "down"), suitcase(2900, 5600, 0.9)), 1, 1.9, BLUE, 9, sfx="pop")
T("新城市", 2600, 5000, 70, k0=2, k1=2.8, sfx="pop")
L(rect(3090, 5270, 230, 400, 24), 3, 3.8, BLACK, 9, sfx="wood_high")
L(contacts(3090, 5170), 4, 4.8, BLACK, 7, sfx="pop")
T("能约谁？", 3090, 4980, 56, RED, k0=5, k1=6, sfx="rim")

scene("都在叫你去找人", "例子 · 爸妈", (950, 6250, 0.85), shake=[6])
L(house(600, 6560), 0, 0.9, sfx="wood_high")
L(join(stick(850, 6600, 0.55, "down"), stick(960, 6600, 0.55, "down", hair=True)), 1, 1.9, BLACK, 8, sfx="pop")
L(phone(1180, 6460, 90, 150), 2, 2.8, BLUE, 8, sfx="pop")
L(bubble(1180, 6190, 260, 130, -1), 3, 3.8, BLACK, 8, sfx="pop")
T("吃了没", 1180, 6190, 52, k0=3.8, k1=4.6)
L(lamp(470, 5880, 0.8), 5, 5.8, RED, 9, sfx="ding")
T("都在叫你去找人", 1010, 5900, 80, RED, k0=6, k1=7.75, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

scene("认出信号，别骂自己", "第一步 · 认出信号", (950, 7750, 0.85))
T("① 认出信号", 950, 7400, 76, BLUE, k0=0, k1=1.5, sfx="pop")
L(lamp(640, 7720, 1.1), 2, 2.9, RED, 9, sfx="wood_high")
L(bubble(1150, 7640, 330, 140, -1), 3, 3.8, BLACK, 8, sfx="pop")
T("我想人了", 1150, 7640, 54, k0=3.8, k1=4.8)
T("矫情", 700, 8020, 60, k0=5, k1=5.8, sfx="pop")
L(cross(700, 8020, 70), 6, 6.8, RED, 12, sfx="rim")
T("正常", 1000, 8020, 60, GREEN, k0=7, k1=7.8, sfx="ding")

scene("联系一个人，说件具体事", "第二步 · 联系一个人", (2650, 7800, 0.85))
T("② 联系一个人", 2650, 7400, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(phone(2260, 7770, 160, 280), 2, 2.9, BLACK, 9, sfx="wood_high")
T("在吗？", 2780, 7900, 58, k0=3, k1=3.8, sfx="pop")
L(cross(2780, 7900, 60), 4, 4.8, RED, 10, sfx="rim")
L(bubble(2760, 7650, 430, 140, -1), 5, 5.8, BLUE, 8, sfx="pop")
T("那家面馆还开吗？", 2760, 7650, 46, k0=5.8, k1=7.8)

scene("约同事楼下吃碗面", "第三步 · 约顿饭", (2650, 8810, 0.85))
T("③ 约顿饭", 2650, 8350, 76, BLUE, k0=0, k1=1.25, sfx="pop")
L(stick(2350, 8950, 0.7, "point"), 2, 2.8, sfx="wood_high")
L(stick(2950, 8950, 0.7, "down"), 2.8, 3.6, BLUE, 9)
T("明天中午？", 2650, 8560, 54, k0=4, k1=5.25, sfx="pop")
L(bowl(2650, 8860, 80), 6, 6.8, BLACK, 9, sfx="wood_high")
T("12:10 楼下", 2650, 9030, 54, k0=6.8, k1=8)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

OVERALL = (1800, 5450 - 550, 0.18)      # 第 0–4 拍：全板（scene() 会加 OY）
scene("评论区聊聊", "评论区见", (1500, 9400, 0.8), bars=4)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你今天想联系谁？", 1500, 9320, 76, RED, k0=6, k1=8, sfx="pop")
T("下一讲：群里几百人，为什么还是孤单？", 1500, 9480, 46, k0=9, k1=13.5, sfx="wood_high")
b.hit(len(b.shots) - 1, 16, "kick", 0.55, "原曲最后一击")
FAR = (OVERALL[0], OVERALL[1] + OY, OVERALL[2])

_camera = wb.camera


def _end_camera(board, T):
    """片尾场景：第 0–4 拍从上一屏拉远到全板，第 4 拍起推到评论区（各 1.1 秒）；其余镜头照引擎默认。"""
    ep = board.ep
    j = len(b.shots) - 1
    if board is not b or ep is None or ep.shot_at(T) != j:
        return _camera(board, T)
    t4 = b.t_of(j, 4)
    a, z, t = (b.views[j - 1], FAR, T - ep.shots[j].t0) if T < t4 else (FAR, b.views[j], T - t4)
    k = wb.ease_in_out(wb.clamp01(t / 1.1))
    return (wb.lerp(a[0], z[0], k), wb.lerp(a[1], z[1], k),
            wb.math.exp(wb.lerp(wb.math.log(a[2]), wb.math.log(z[2]), k)), 0.0, 0.0)


wb.camera = _end_camera


def build():
    ep = episode(1, "signal", "孤独是信号", "一个人吃饭，心里为什么发空？", ACC, b.shots,
                 [f"{BOOK}第一部分 可耻的孤独、第二部分 从自私的基因到社会动物（转述）",
                  "中译本：焦梦津译，中国人民大学出版社 2009"],
                 "一个人吃饭|心里为什么【发空】", SQUARE_SHOT,
                 ["书中观点均为转述：孤独像饥饿、口渴、疼痛一样，是一种信号，提醒人去修复和别人的联系；这种感受是进化"
                  "留下来的——人类祖先离开群体就危险，对落单敏感、会赶紧回到群体的人更容易活下来。相关内容见第一部分"
                  "“可耻的孤独”与第二部分“从自私的基因到社会动物”。出处：John T. Cacioppo & William Patrick, "
                  "Loneliness: Human Nature and the Need for Social Connection (W. W. Norton, 2008)，中译本《孤独是可耻的》"
                  "（约翰·卡乔波、威廉·帕特里克著，焦梦津译，中国人民大学出版社 2009）。上屏均为转述，不是逐字引文；"
                  "书名中的“可耻”不用作对任何人的评价。",
                  "“几万年前”篝火、落单遇险的画面，以及“饿 → 吃饭 / 渴 → 喝水 / 孤独 → 找人”一图，为对书中观点的通俗化示意。",
                  "下班一个人吃外卖、工位各吃各的午饭、刚到新城市、爸妈在老家视频均为现实场景"
                  "示意，不指向任何具体公司或个人；时间、句数为示意，不是数据。",
                  "三步做法（认出信号、别骂自己；当天联系一个人并说件具体的事；约顿饭）为据书中思路整理的建议。"],
                 tags="#独处")
    return b.attach(ep)
