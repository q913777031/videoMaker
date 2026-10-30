"""02 注意力残留（白板手绘版）：回条消息，怎么半天回不了神？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（形式 C 复刻实验，开局让观众猜）：小周写方案写到一半，小红点叮一下 → 只回了一句“收到” → 回来接不上了 →
drop：小红点的影子粘在脑门上、消息残影飘在头顶，“残留”砸下 → 亮书，引出勒鲁瓦的研究 →
复刻实验（两组都做题 A；甲组做完，乙组做到一半被叫停；都去做题 B——先停住让观众猜谁差 → 揭晓：被打断的乙组更差，
头上还挂着 A 的残影）→ 书中观点（人到了 B，心还拴在 A）→ 回到小周（一天被叮成一段段灰色回神时间）→
做法（攒着一起回 / 做完一段再切）→ 评论区互动 + 下一讲。
书中观点为转述：卡尔·纽波特《深度工作》第一部分第1章（注意力残留，引管理学者苏菲·勒鲁瓦的研究）；
实验画面为对研究设计的简化示意，不写数字和人数；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_out
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, clock, doc,
                               face, hands_at, join, rect, stick)

from .common import BOOK, episode

ACC = "#6B5BB8"
SQUARE_SHOT = 8                 # 场景 9：两组小人 + 乙组头上 A 的残影 + 成绩条
COVER_SHOT = 3                  # 竖版封面：drop 那一屏（小周 + 残影 + “残留”）

b = Board(size=(3600, 5750))
GRAY = "#A3A8B0"
OY = 350                        # 场景 1–13 整体下移，顶部留给片尾评论区（评论区不压到“残留”一屏的字）


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(len(b.shots) - 1, k0, k1, s, x, y + OY, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    if OY:
        path = skia.Path(path)
        path.offset(0, OY)
    b.path(len(b.shots) - 1, k0, k1, path, color, width, sfx=sfx)


def C(k0, k1, fn, sfx=None):
    oy = OY

    def moved(c, k, t):
        c.save()
        c.translate(0, oy)
        fn(c, k, t)
        c.restore()
        return None

    b.custom(len(b.shots) - 1, k0, k1, moved, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(len(b.shots) - 1, k, sfx, gain)


def E(k0, k1, x, y, w, h):
    b.erase(len(b.shots) - 1, k0, k1, x, y + OY, w, h)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=(view[0], view[1] + OY, view[2]), bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def zhou(x, y, s=1.0, arms="down") -> skia.Path:
    """主角小周：火柴人 + 挂绳工牌。(x, y) 为脚底。"""
    hy = y - 290 * s
    return join(stick(x, y, s, arms),
                P((x - 18 * s, hy + 45 * s), (x, hy + 105 * s), (x + 18 * s, hy + 45 * s)),
                rect(x, hy + 128 * s, 36 * s, 44 * s, 5 * s))


def workdesk(x, y, w=680) -> skia.Path:
    """工位：桌面 + 两条腿 + 大显示器（显示器中心在桌面上方 200）。(x, y) 为桌面中点。"""
    mx, my = x + 100, y - 200
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 30, y), (x - w / 2 + 30, y + 110)),
                P((x + w / 2 - 30, y), (x + w / 2 - 30, y + 110)), rect(mx, my, 340, 230, 12),
                P((mx, my + 115), (mx, y - 20)), P((mx - 70, y - 20), (mx + 70, y - 20)))


def screen_lines(mx, my) -> skia.Path:
    """显示器上的文档：两行写满，第三行写到一半。"""
    return join(P((mx - 130, my - 50), (mx + 120, my - 50)), P((mx - 130, my), (mx + 100, my)),
                P((mx - 130, my + 50), (mx, my + 50)))


def tangle(x, y, w=180, h=90) -> skia.Path:
    """脑袋上方一团乱线。"""
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    for i in range(9):
        a = i * 1.9
        p.quadTo(x + math.cos(a) * w * 0.6, y + math.sin(a * 1.3) * h * 0.7,
                 x + math.cos(a + 1.1) * w * 0.45, y + math.sin(a + 0.8) * h * 0.5)
    return p


def dashed(a, b2, n=7) -> skia.Path:
    """虚线：n 段短线。"""
    (x0, y0), (x1, y1) = a, b2
    parts = []
    for i in range(n):
        f0, f1 = i / n, (i + 0.55) / n
        parts.append(P((x0 + (x1 - x0) * f0, y0 + (y1 - y0) * f0), (x0 + (x1 - x0) * f1, y0 + (y1 - y0) * f1)))
    return join(*parts)


def phone(x, y, w=180, h=320) -> skia.Path:
    return join(rect(x, y, w, h, 24), P((x - 22, y - h / 2 + 26), (x + 22, y - h / 2 + 26)))


def card(x, y, w=170, h=140) -> skia.Path:
    """一道题：题板 + 两行横线。题号另写在左上。"""
    return join(rect(x, y, w, h, 12), P((x - w / 2 + 70, y + 10), (x + w / 2 - 25, y + 10)),
                P((x - w / 2 + 70, y + 40), (x + w / 2 - 45, y + 40)))


def basket(x, y, w=360, h=220) -> skia.Path:
    top, bot = y - h / 2, y + h / 2
    parts = [P((x - w / 2, top), (x - w * 0.36, bot), (x + w * 0.36, bot), (x + w / 2, top), close=True)]
    for f in (1 / 3, 2 / 3):
        yy = top + h * f
        dx = w / 2 - (w / 2 - w * 0.36) * f
        parts.append(P((x - dx, yy), (x + dx, yy)))
    for f in (-0.2, 0.2):
        parts.append(P((x + w * f * 1.2, top), (x + w * f, bot)))
    return join(*parts)


def back(k):
    """带一点回弹的放大（0→1）。"""
    k = clamp01(k)
    return 1 + 2.7 * (k - 1) ** 3 + 1.7 * (k - 1) ** 2


def draw_dot(c, x, y, r, n="1", alpha=1.0, legs=True):
    """系列角色小红点：红色实心圆 + 白色数字 + 两条小短腿。"""
    if legs:
        for d in (-1, 1):
            c.drawPath(P((x + d * r * 0.35, y + r * 0.8), (x + d * r * 0.45, y + r * 1.55), (x + d * r * 0.8, y + r * 1.55)),
                       K.paint(BLACK, alpha, max(3.0, r * 0.15)))
    K.dot(c, x, y, r, RED, alpha)
    K.text(c, n, x, y + r * 0.04, r * 1.15, "black", "#FFFFFF", alpha)


def dot_fn(x, y, r=34, n="1", alpha=1.0, bob=True):
    """小红点蹦出来（回弹放大），落定后轻轻上下颠。"""
    def fn(c, k, t):
        s = back(k)
        yy = y + (math.sin(t * 5.5) * r * 0.12 if bob and k >= 1 else 0.0)
        c.save()
        c.translate(x, yy)
        c.scale(s, s)
        draw_dot(c, 0, 0, r, n, alpha)
        c.restore()
        return None

    return fn


def fall_fn(x0, y0, x1, y1, r=30):
    """小红点从上面掉进篮子。"""
    def fn(c, k, t):
        f = k * k
        draw_dot(c, x0 + (x1 - x0) * k, y0 + (y1 - y0) * f, r)
        return None

    return fn


def slam_fn(s, x, y, size, color=RED):
    """大字从大到小“砸”下来。"""
    def fn(c, k, t):
        sc = 1 + 1.3 * (1 - ease_out(k))
        c.save()
        c.translate(x, y)
        c.scale(sc, sc)
        K.text(c, s, 0, 0, size, "hand", color, min(1.0, 0.25 + k * 1.5))
        c.restore()
        return None

    return fn


def ghost_bubble_fn(x, y, w, h, s, color=BLUE):
    """半透明的消息残影，飘在头顶上下浮动。"""
    def fn(c, k, t):
        a = 0.42 * clamp01(k)
        yy = y + math.sin(t * 2.6) * 10 - 40 * (1 - ease_out(k))
        c.drawPath(bubble(x, yy, w, h, 1), K.paint(color, a, 7))
        K.text(c, s, x, yy, 56, "hand", color, a + 0.1)
        return None

    return fn


def ghost_card_fn(x, y, s="A"):
    """半透明的题 A 残影（虚线框），挂在乙组头上。"""
    def fn(c, k, t):
        a = 0.45 * clamp01(k)
        yy = y + math.sin(t * 2.6) * 8 - 30 * (1 - ease_out(k))
        K.rr_stroke(c, x, yy, 130, 90, 10, BLACK, 6, a, dash=(18, 12))
        K.text(c, s, x, yy, 60, "hand", BLACK, a)
        return None

    return fn


def cursor_fn(x, y, h=56):
    """文档光标一闪一闪。"""
    def fn(c, k, t):
        if math.sin(t * 6.5) > -0.2:
            c.drawPath(P((x, y - h / 2), (x, y + h / 2)), K.paint(BLUE, 1, 7))
        return None

    return fn


# ---------------------------------------------------------------- 开局：写到一半，叮一下（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

DX, DY = 900, 1700              # 工位桌面中点
MX, MY = DX + 100, DY - 200     # 显示器中心
ZH = (640, 1920)                # 小周脚底
ZS = 0.9
ZHY = ZH[1] - 290 * ZS          # 小周头心
DOT = (1240, 1420)              # 小红点从显示器右边蹦出来

scene("写到一半", "上班日常", (900, 1500, 0.85), bars=2)
L(workdesk(DX, DY), 0, 0.9, sfx="wood_high")
L(zhou(*ZH, ZS, "hold"), 1, 1.8, BLACK, 10, sfx="pop")
L(face(*ZH, ZS, "smile"), 1.8, 2.0)
L(screen_lines(MX, MY), 2, 2.8, BLUE, 8, sfx="wood_low")
C(4, 4.4, dot_fn(*DOT), sfx="ding")
T("叮！", 1290, 1290, 64, RED, k0=5, k1=5.8, sfx="rim")

scene("就回了一句", "上班日常", (1500, 1500, 0.85))
PX, PY = 1700, 1500
L(phone(PX, PY, 380, 600), 0, 0.9, BLACK, 10, sfx="wood_high")
L(bubble(PX - 40, 1350, 280, 100, -1), 1, 1.8, BLACK, 7, sfx="pop")
T("改到三点了", PX - 40, 1350, 46, k0=1.8, k1=3.0)
L(bubble(PX + 70, 1530, 200, 100, 1), 3, 3.7, BLUE, 7, sfx="pop")
T("收到", PX + 70, 1530, 52, BLUE, k0=3.7, k1=4.5)
L(join(clock(2010, 1330, 80), P((2010, 1250), (2010, 1222)), P((1985, 1222), (2035, 1222))), 5, 5.8, BLACK, 8,
  sfx="wood_low")
L(hands_at(2010, 1330, 80, 0, 5), 5.8, 6.0, RED, 7)
T("30 秒", 2010, 1470, 56, RED, k0=6, k1=7.25, sfx="rim")

scene("怎么接不上了", "上班日常", (850, 1550, 0.85))
E(0, 0.6, 1280, 1395, 180, 270)          # 回完了，小红点走了
H(0, "shaker", 0.7)
C(1, 1.2, cursor_fn(MX + 18, MY + 50), sfx="wood_low")
L(tangle(640, 1530, 170, 80), 2, 3, BLACK, 7, sfx="rim")
T("？？", 480, 1430, 64, RED, k0=4, k1=4.8, sfx="pop")
T("刚写到哪了？", 585, 1200, 60, k0=5, k1=6.5, sfx="pop")

# ---------------------------------------------------------------- drop：残留（场景 4）

scene("心还留在那", "注意力残留", (800, 1480, 0.85), shake=[0], flashes=[0])
E(0, 0.3, 585, 1320, 470, 520)           # 擦掉乱线和问号，换成残影
C(0, 0.35, slam_fn("残留", 900, 1140, 150), sfx="kick")
C(1, 1.8, ghost_bubble_fn(430, 1350, 240, 110, "收到"), sfx="shaker")
L(dashed((520, 1412), (615, 1612), 6), 3, 3.9, BLACK, 6, sfx="wood_low")
C(4, 4.4, dot_fn(695, 1618, 34, "1", 0.6), sfx="pop")
T("心还挂在消息上", 900, 1290, 56, RED, k0=5, k1=6.75, sfx="pop")

# ---------------------------------------------------------------- 亮书 + 复刻实验（场景 5–9）

scene("书里讲个研究", "书中研究", (1000, 2900, 0.85))
L(book(700, 2950, 420, 280), 0, 0.9, BLACK, 10, sfx="wood_low")
T("《深度工作》", 700, 2700, 64, GREEN, k0=1, k1=2.5, sfx="pop")
T("卡尔·纽波特", 700, 3170, 48, k0=3, k1=4.5, sfx="pop")
L(join(rect(1300, 2800, 420, 130, 14), P((1300, 2865), (1300, 3180)), P((1220, 3180), (1380, 3180))), 5, 5.9, BLUE,
  9, sfx="wood_high")
T("勒鲁瓦的研究", 1300, 2800, 54, BLUE, k0=6, k1=7.5, sfx="pop")

GL, GR = 630, 1370              # 甲组 / 乙组中心
FEET, SS = 4000, 0.55
CA, CB = 4240, 4620             # 题 A / 题 B 所在高度
VEXP = (1000, 4100, 0.85)

scene("两组先做题", "实验 · 都做题 A", VEXP)
L(P((1000, 3800), (1000, 4450)), 0, 0.8, GRAY, 7, sfx="wood_low")
L(join(stick(GL - 90, FEET, SS), stick(GL + 90, FEET, SS)), 1, 1.9, BLACK, 8, sfx="wood_high")
T("甲组", GL, 4070, 54, k0=2, k1=2.8, sfx="pop")
L(join(stick(GR - 90, FEET, SS), stick(GR + 90, FEET, SS)), 3, 3.9, BLACK, 8, sfx="wood_high")
T("乙组", GR, 4070, 54, k0=4, k1=4.8, sfx="pop")
L(join(card(GL, CA), card(GR, CA)), 5, 5.9, BLACK, 8, sfx="wood_low")
T("A", GL - 50, CA - 15, 60, BLUE, k0=6, k1=6.8, sfx="pop")
T("A", GR - 50, CA - 15, 60, BLUE, k0=6.8, k1=7.6)

scene("一组被打断", "实验 · 一组被叫停", VEXP)
L(check(GL + 40, CA - 10, 50), 0, 0.7, GREEN, 12, sfx="ding")
T("做完了", GL, 4370, 50, GREEN, k0=1, k1=1.8, sfx="pop")
L(circle(1560, CA, 55), 3, 3.7, RED, 9, sfx="rim")
T("停", 1560, CA, 64, RED, k0=3.7, k1=4.5)
L(P((GR - 70, CA + 75), (GR + 75, CA - 75)), 5, 5.6, RED, 12, sfx="tom")
T("做到一半", GR, 4370, 50, RED, k0=6, k1=7, sfx="pop")

VB = (1000, 4280, 0.8)
scene("你猜谁差", "实验 · 你来猜", VB)
L(join(arrow((GL, 4410), (GL, 4535), 0.0, 30), arrow((GR, 4410), (GR, 4535), 0.0, 30)), 0, 0.9, BLACK, 7,
  sfx="wood_low")
L(join(card(GL, CB), card(GR, CB)), 1, 1.9, BLACK, 8, sfx="wood_high")
T("B", GL - 50, CB - 15, 60, BLUE, k0=2, k1=2.8, sfx="pop")
T("B", GR - 50, CB - 15, 60, BLUE, k0=2.8, k1=3.6)
T("？", 1000, CB, 170, RED, k0=4, k1=4.8, sfx="tom")
T("谁做得更差？", 1000, 4810, 64, RED, k0=5, k1=6.5, sfx="pop")

scene("被打断的更差", "实验 · 揭晓", VB)
E(0, 0.5, 1000, CB, 220, 240)
E(0.3, 0.8, 1000, 4810, 520, 100)
H(0, "shaker", 0.7)
C(1, 1.8, ghost_card_fn(GR, 3745), sfx="pop")
L(P((GL - 170, 4800), (GL + 190, 4800)), 3, 3.9, GREEN, 36, sfx="wood_high")
L(P((GR - 170, 4800), (GR - 40, 4800)), 4, 4.6, RED, 36, sfx="wood_low")
T("更差", GR + 70, 4800, 60, RED, k0=5, k1=5.8, sfx="rim")

# ---------------------------------------------------------------- 书中观点 + 回到小周（场景 10–11）

scene("心有一半在后面", "书中观点 · 注意力残留", (2850, 4300, 0.85))
L(card(2450, 4450), 0, 0.9, BLACK, 8, sfx="wood_high")
T("A", 2400, 4435, 60, BLUE, k0=0.9, k1=1.7)
L(card(3260, 4450), 2, 2.9, BLACK, 8, sfx="wood_high")
T("B", 3210, 4435, 60, BLUE, k0=2.9, k1=3.7)
L(zhou(3050, 4720, 0.75, "point"), 4, 4.8, BLACK, 9, sfx="pop")
L(face(3050, 4720, 0.75, "flat"), 4.8, 5.0)
rope = skia.Path()
rope.moveTo(3016, 4490)
rope.cubicTo(2900, 4700, 2700, 4380, 2540, 4470)
L(join(rope, circle(2548, 4470, 14)), 5, 5.9, RED, 8, sfx="rim")
T("心还拴在 A 上", 2850, 4000, 70, RED, k0=6, k1=7.75, sfx="pop")

TLY = 3250
DOTS = [2420, 2640, 2860, 3080]
scene("一天全是灰", "回到小周", (2850, 3150, 0.85))
L(join(P((2300, TLY), (3420, TLY)), P((3390, TLY - 25), (3420, TLY), (3390, TLY + 25))), 0, 0.9, BLACK, 8,
  sfx="wood_low")
T("9:00", 2330, TLY + 90, 50, k0=1, k1=1.8, sfx="pop")
T("18:00", 3370, TLY + 90, 50, k0=1.8, k1=2.6)
for n, x in enumerate(DOTS):
    C(2 + n, 2.4 + n, dot_fn(x, TLY - 70, 30, "1", 1.0, False), sfx="ding")
    L(P((x + 30, TLY), (x + 190, TLY)), 2.2 + n, 2.95 + n, GRAY, 30)
T("灰的这段在回神", 2850, 2900, 66, k0=6, k1=7.75, sfx="pop")

# ---------------------------------------------------------------- 做法（场景 12–13）

scene("攒着一起回", "做法一 · 攒着回", (2850, 2000, 0.85))
L(basket(2600, 2280), 0, 0.9, BLACK, 9, sfx="wood_high")
for n, (sx, ex) in enumerate(((2420, 2530), (2600, 2610), (2780, 2690))):
    C(1 + n, 1.8 + n, fall_fn(sx, 1600, ex, 2150 - 10 * (n % 2)), sfx="pop")
L(join(clock(3200, 1880, 110), hands_at(3200, 1880, 110, 2, 0)), 4, 4.9, BLACK, 8, sfx="wood_low")
T("14:00 一起回", 3200, 2080, 56, BLUE, k0=5, k1=7.25, sfx="pop")

scene("做完一段再切", "做法二 · 做完一段", (2850, 850, 0.85))
L(doc(2620, 850, 380, 500, 5), 0, 0.9, BLACK, 9, sfx="wood_high")
T("这一节完", 2620, 1180, 56, GREEN, k0=2, k1=3, sfx="ding")
L(arrow((2840, 850), (3120, 850), 0.1, 36), 3, 3.9, BLACK, 8, sfx="wood_low")
L(phone(3250, 850), 4, 4.8, BLACK, 9, sfx="pop")
C(5, 5.4, dot_fn(3330, 700, 32), sfx="ding")
T("先写完这一节", 2850, 430, 70, BLUE, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

OY = 0                          # 片尾：评论区在白板顶部，坐标不下移
FAR = (1800, 2875, 0.17)
CMT = (1000, 560, 0.85)
j_end = scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(j_end, 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("被消息打断后", 1000, 420, 76, RED, k0=6, k1=7.5, sfx="pop")
T("你多久能回神？", 1000, 530, 76, RED, k0=7.5, k1=9.25)
T("下一讲：忙了一整天，干成了啥？", 1000, 690, 46, k0=10, k1=13.75, sfx="wood_high")
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(2, "residue", "注意力残留", "回条消息，怎么半天回不了神？", ACC, b.shots,
                 [f"{BOOK}第一部分 第1章“深度工作是有价值的”，注意力残留一节（转述）",
                  "书中引用：Sophie Leroy, Why is it so hard to do my work? The challenge of attention residue when "
                  "switching between work tasks, Organizational Behavior and Human Decision Processes, 2009",
                  "中译本：宋伟译，江西人民出版社 · 后浪 2017；民主与建设出版社 · 后浪 2023"],
                 "回条消息|怎么半天【回不了神】", COVER_SHOT,
                 ["书中观点均为转述：从任务 A 切到任务 B 时，注意力不会马上跟过去，会有一部分留在 A 上（注意力残留）；"
                  "A 没做完就被切走，残留更重，接下来做 B 的表现更差。书中引管理学者苏菲·勒鲁瓦的研究说明这一点。"
                  "见第一部分第1章（注意力残留）。上屏均为转述，不是逐字引文。",
                  "“甲组做完 A、乙组做到一半被叫停、再都去做 B”的实验画面，是对研究设计的简化示意；"
                  "成绩条只表示方向（被打断的一组更差），不是研究数据，画面里不写数字和人数。"
                  "“人到了 B，心还拴在 A”的绳子为通俗化比喻。",
                  "小周写方案时回一句“收到”、用时 30 秒、一天里一段段灰色回神时间，均为现实场景示意，"
                  "时间与次数为示意，不是数据；不指向任何具体公司或个人。",
                  "两条做法（消息攒着、下午两点一起回；手上的事做完一段再切）为据书中思路整理的建议，时间点为示意。"],
                 tags="#注意力")
    return b.attach(ep)
