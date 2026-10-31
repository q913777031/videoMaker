"""09 框架效应（白板手绘版）：同一件事，换个说法就变了？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（形式 H 对话改写，一屏一对）：同一份周报，进度九成 → 说法一“完成了九成”，老板笑 → 说法二“还有一成没做完”，
同一个老板皱眉 → drop：拉远看两句话，中间一个大等号砸下，“90% 完成 = 10% 没做” →
亮书（快快、慢慢出场，“框架效应”套进画框）→ 书中实验（同一个手术装进两个画框：存活率 90% / 死亡率 10%，
医生的选择跟着变；600 人点阵：“救活 200 人”与“400 人会死”，多数人的选择反过来；器官捐献表：默认已勾的
捐献人数条高、要自己勾的低）→ 职场原话改写（快快脱口“这事做不了”，慢慢改成“下周三能交，先砍掉这块”；
聊天框里“你怎么还没交”改成“周四前给我，好排下一步”）→ 做法（自己翻个面 / 先看默认项 / 说之前换位）→
拉远看全板 → 评论区互动 + 下一讲。
书中观点为转述：丹尼尔·卡尼曼《思考，快与慢》第34章“善用框架效应，让生活更美好”（Frames and Reality）；
中译本胡晓姣、李爱民、何梦莹译，中信出版社 2012。例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, cross,
                               doc, face, join, rect, stick)

from .common import BOOK, episode, kuai, man

ACC = "#2C8C9E"
SQUARE_SHOT = 3                 # 场景 4：员工 + 老板笑 / 皱眉两对，中间大等号，“90% 完成 = 10% 没做”

b = Board(size=(3600, 10300))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(fn, k0, k1, sfx=None):
    b.custom(J(), k0, k1, fn, sfx=sfx)


def H(k, sfx, gain=0.8):
    b.hit(J(), k, sfx, gain)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def head(x, y, r=80, mood="smile") -> skia.Path:
    """老板的大头：圆脸 + 眼睛 + 嘴 + 领带结；frown 时眉头往下压。"""
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


def pframe(x, y, w, h) -> skia.Path:
    """画框：外框 + 内框 + 四角斜线。"""
    g = 26
    return join(rect(x, y, w, h, 6), rect(x, y, w - 2 * g, h - 2 * g, 4),
                P((x - w / 2, y - h / 2), (x - w / 2 + g, y - h / 2 + g)),
                P((x + w / 2, y - h / 2), (x + w / 2 - g, y - h / 2 + g)),
                P((x - w / 2, y + h / 2), (x - w / 2 + g, y + h / 2 - g)),
                P((x + w / 2, y + h / 2), (x + w / 2 - g, y + h / 2 - g)))


def equals(x, y, w=240, gap=70) -> skia.Path:
    return join(P((x - w / 2, y - gap / 2), (x + w / 2, y - gap / 2)), P((x - w / 2, y + gap / 2), (x + w / 2, y + gap / 2)))


def rays(x, y, r0=170, r1=240, n=8) -> skia.Path:
    parts = []
    for i in range(n):
        a = i / n * 2 * math.pi + math.pi / n
        parts.append(P((x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))))
    return join(*parts)


def strike(x0, x1, y) -> skia.Path:
    """划掉一行字：一道略带起伏的横线。"""
    p = skia.Path()
    p.moveTo(x0, y + 6)
    p.quadTo((x0 + x1) / 2, y - 14, x1, y + 4)
    return p


def magnifier(x, y, r=90) -> skia.Path:
    d = r / math.sqrt(2)
    return join(circle(x, y, r), P((x + d, y + d), (x + d + 110, y + d + 110)))


def fill_fn(x0, y, w, h, color=GREEN, alpha=0.45):
    """进度条从左往右填满：x0 为左端，(w, h) 为填满后的尺寸。"""

    def fn(c, k, t):
        ww = w * wb.ease_out(k)
        if ww > 1:
            K.rr(c, x0 + ww / 2, y, ww, h, 8, color, alpha)
        return (x0 + ww, y) if k < 1 else None

    return fn


GX0, GY0, GD = 2031, 5051, 22   # 600 人点阵：30 列 × 20 行，左上角圆点与间距
GCOLS, GROWS = 30, 20


def dots_fn(color=BLACK, cols=range(GCOLS), r=6.5, alpha=1.0):
    """点阵逐列出现：cols 为要画的列；color 覆盖在原点阵上（用来把“救活的”“会死的”染色）。"""
    cols = list(cols)

    def fn(c, k, t):
        n = int(math.ceil(len(cols) * wb.clamp01(k)))
        for ci in cols[:n]:
            for ri in range(GROWS):
                K.dot(c, GX0 + ci * GD, GY0 + ri * GD, r, color, alpha)
        if k < 1 and n:
            return GX0 + cols[n - 1] * GD, GY0 + GROWS * GD + 20
        return None

    return fn


def bars_fn(items, base, w=170, alpha=0.4):
    """柱子从底线往上长：items 为 [(x, 高, 颜色)]。"""

    def fn(c, k, t):
        f = wb.ease_out(k)
        for x, h, col in items:
            hh = h * f
            if hh > 1:
                K.rr(c, x, base - hh / 2, w, hh, 6, col, alpha)
                c.drawPath(rect(x, base - hh / 2, w, hh, 6), wb.marker(col, 8))
        x, h, _ = items[0]
        return (x + w / 2, base - h * f) if k < 1 else None

    return fn


def flip_fn(x, y, w, h, front, back, size=64):
    """卡片翻面：前一半压扁显示正面，后一半展开显示反面。"""

    def fn(c, k, t):
        sx = math.cos(math.pi * wb.ease_in_out(k))
        a = abs(sx)
        if a < 0.03:
            return x, y - h / 2
        s, col = (front, GREEN) if sx > 0 else (back, RED)
        c.save()
        c.translate(x, y)
        c.scale(a, 1)
        c.drawPath(rect(0, 0, w, h, 16), wb.marker(BLACK, 9))
        K.text(c, s, 0, 20, size, "hand", col)
        c.restore()
        return (x + w / 2 * a, y - h / 2) if k < 1 else None

    return fn


# ---------------------------------------------------------------- 开局：同一份周报，两种说法（场景 1–4）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("同一份周报", "同一份周报", (1800, 900, 0.85), bars=2)
L(doc(1800, 760, 380, 440, 4), 0, 0.9, sfx="wood_high")
T("本周周报", 1800, 480, 64, BLUE, k0=1, k1=2, sfx="pop")
L(rect(1780, 1100, 500, 64, 12), 2, 2.7, BLACK, 8, sfx="wood_low")
C(fill_fn(1538, 1100, 434, 44), 3, 4.2, sfx="shaker")
T("90%", 2160, 1122, 70, RED, k0=4, k1=4.8, sfx="pop")

EY, BUB, BOSS = 2800, 2100, 2560     # 员工脚底、气泡、老板大头的纵坐标


def pair(cx, label, label_color, said, mood):
    """一对：员工说一句（气泡），老板的表情。cx 为这一对的中心。"""
    T(label, cx, 1880, 64, label_color, k0=0, k1=0.8, sfx="pop")
    L(join(stick(cx - 400, EY, 0.6, "point"), face(cx - 400, EY, 0.6, "smile")), 1, 1.8, BLACK, 9, sfx="wood_high")
    L(bubble(cx - 50, BUB, 600, 150, -1), 2, 2.5, BLACK, 8, sfx="pop")
    T(said, cx - 50, BUB + 20, 58, k0=2.5)
    L(head(cx + 250, BOSS, 85, mood), 4, 4.9, BLACK, 8, sfx="wood_low")


LX, RX = 1250, 2350             # 两对的中心

scene("这么说，老板笑了", "说法一 · 完成了九成", (LX, 2300, 0.85))
pair(LX, "说法一", GREEN, "完成了九成", "smile")
T("不错！", LX + 300, 2385, 64, GREEN, k0=6, k1=6.8, sfx="ding")

scene("那么说，老板皱眉", "说法二 · 还有一成没做", (RX, 2300, 0.85))
pair(RX, "说法二", RED, "还有一成没做完", "frown")
T("？", RX + 420, 2400, 110, RED, k0=6, k1=6.8, sfx="rim")

scene("说的是同一件事", "同一件事", (1800, 2600, 0.5), shake=[0], flashes=[0])
L(equals(1800, BUB + 10, 240, 74), 0, 0.6, RED, 26, sfx="kick")
L(rays(1800, BUB + 10, 175, 245), 2, 2.8, RED, 10, sfx="pop")
T("90% 完成 = 10% 没做", 1800, 3180, 130, RED, k0=4, k1=7, sfx="ding")
H(5, "tom")
L(join(P((1110, 3255), (1580, 3255)), P((2020, 3255), (2490, 3255))), 7, 7.9, BLACK, 9, sfx="wood_high")

# ---------------------------------------------------------------- 书中观点（场景 5–8）

scene("书里叫它框架效应", "思考，快与慢 · 书中观点", (1150, 4200, 0.85))
L(book(800, 3960, 320, 210), 0, 0.9, sfx="wood_low")
T("思考，快与慢", 800, 3790, 56, GREEN, k0=1, k1=2.5, sfx="pop")
L(join(kuai(1260, 4130, 0.5), face(1260, 4130, 0.5, "smile")), 3, 3.9, RED, 9, sfx="wood_high")
L(join(man(1530, 4130, 0.5), face(1530, 4130, 0.5, "flat")), 4, 4.9, BLUE, 9, sfx="wood_low")
T("框架效应", 1100, 4440, 100, RED, k0=5, k1=6, sfx="pop")
L(pframe(1100, 4410, 560, 200), 7, 7.9, ORANGE, 8, sfx="ding")

scene("换个框，医生也变", "书中实验 · 同一个手术", (2350, 4200, 0.85))
T("同一个手术", 2350, 3790, 66, k0=0, k1=1.25, sfx="pop")
L(pframe(2050, 4080, 500, 280), 2, 2.5, BLACK, 8, sfx="wood_high")
T("存活率90%", 2050, 4102, 62, GREEN, k0=2.5)
L(pframe(2650, 4080, 500, 280), 4, 4.5, BLACK, 8, sfx="wood_high")
T("死亡率10%", 2650, 4102, 62, RED, k0=4.5)
L(check(2050, 4370, 50), 6, 6.5, GREEN, 12, sfx="ding")
T("？", 2650, 4400, 100, RED, k0=7, k1=7.8, sfx="rim")

scene("救活，还是会死", "书中实验 · 救人方案", (2350, 5550, 0.85))
C(dots_fn(), 0, 1.4, sfx="shaker")
T("600人", 1895, 5282, 60, k0=1, k1=1.9, sfx="pop")
T("救活200人", 2060, 5650, 58, GREEN, k0=2, sfx="pop")
C(dots_fn(GREEN, range(10), 7), 2, 2.8)
T("400人会死", 2660, 5650, 58, RED, k0=4, sfx="pop")
C(dots_fn(RED, range(10, GCOLS), 7), 4, 5.2)
L(check(2060, 5820, 40), 6, 6.5, GREEN, 11, sfx="ding")
L(cross(2660, 5820, 36), 7, 7.6, RED, 11, sfx="rim")

FA, FB, FY = 850, 1450, 5250    # 两张登记表
BASE = 5850                     # 柱子底线
scene("默认勾上，人就多了", "书中例子 · 器官捐献", (1150, 5550, 0.85))
L(join(rect(FA, FY, 440, 200, 14), rect(FA - 140, FY, 60, 60, 6)), 0, 0.9, BLACK, 8, sfx="wood_high")
T("同意捐献", FA + 60, FY + 20, 56, k0=1, k1=2, sfx="pop")
L(check(FA - 140, FY - 4, 26), 2, 2.4, GREEN, 10, sfx="ding")
L(join(rect(FB, FY, 440, 200, 14), rect(FB - 140, FY, 60, 60, 6)), 3, 3.9, BLACK, 8, sfx="wood_high")
T("同意捐献", FB + 60, FY + 20, 56, k0=4, k1=5, sfx="pop")
L(P((620, BASE), (1680, BASE)), 6, 6.6, BLACK, 9, sfx="tom")
C(bars_fn([(FA, 400, GREEN), (FB, 90, BLACK)], BASE), 6.6, 7.8)
T("默认已勾", FA, FY - 150, 50, GREEN, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 原话改写（场景 9–10）

scene("做不了，换个说法", "改写一 · 做不了", (1150, 6900, 0.85))
L(join(kuai(700, 6800, 0.55, "up"), face(700, 6800, 0.55, "frown")), 0, 0.9, RED, 9, sfx="wood_high")
L(bubble(1250, 6520, 560, 140, -1), 1, 1.5, BLACK, 8, sfx="pop")
T("这事做不了", 1250, 6540, 60, k0=1.5)
L(strike(1080, 1420, 6530), 3, 3.6, RED, 11, sfx="rim")
L(join(man(700, 7350, 0.55), face(700, 7350, 0.55, "smile")), 4, 4.8, BLUE, 9, sfx="wood_low")
L(bubble(1250, 7080, 600, 230, -1), 5, 5.5, BLUE, 8, sfx="pop")
T("下周三能交", 1250, 7050, 60, BLUE, k0=5.5)
T("先砍掉这块", 1250, 7140, 60, BLUE, k0=6.75)

scene("催进度，换个说法", "改写二 · 催进度", (2450, 6900, 0.85))
L(rect(2450, 6900, 600, 1000, 44), 0, 0.9, BLACK, 9, sfx="wood_high")
L(bubble(2500, 6620, 480, 130, 1), 1, 1.4, BLACK, 8, sfx="pop")
T("你怎么还没交", 2500, 6640, 56, k0=1.4)
L(strike(2330, 2670, 6630), 3, 3.6, RED, 11, sfx="rim")
L(bubble(2450, 6960, 500, 230, 1), 4, 4.4, BLUE, 8, sfx="pop")
T("周四前给我", 2450, 6930, 58, BLUE, k0=4.4)
T("好排下一步", 2450, 7020, 58, BLUE, k0=5.65)
L(join(man(2930, 7380, 0.5), face(2930, 7380, 0.5, "smile")), 7, 7.8, BLUE, 9, sfx="wood_low")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

scene("听到一面，翻另一面", "做法一 · 自己翻个面", (1150, 8250, 0.85))
T("① 自己翻个面", 1150, 7830, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(rect(800, 8180, 380, 220, 16), 2, 2.6, BLACK, 9, sfx="wood_high")
T("90%成功", 800, 8200, 64, GREEN, k0=2.6)
L(arrow((1010, 8110), (1290, 8110), -0.35, 34), 4, 4.7, BLACK, 8, sfx="wood_low")
C(flip_fn(1500, 8180, 380, 220, "90%成功", "10%失败"), 5, 6.2, sfx="shaker")
T("两面都看", 1150, 8530, 70, GREEN, k0=7, k1=8, sfx="ding")

scene("默认勾的，先看看", "做法二 · 先看默认项", (2450, 8250, 0.85))
T("② 先看默认项", 2450, 7830, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(join(rect(2400, 8250, 680, 460, 20), P((2060, 8080), (2740, 8080)), P((2180, 8370), (2620, 8370)),
       P((2180, 8440), (2540, 8440))), 2, 2.9, BLACK, 8, sfx="wood_high")
L(join(rect(2170, 8215, 60, 60, 6), check(2170, 8211, 26)), 3, 3.5, BLACK, 9, sfx="pop")
T("自动续费", 2400, 8235, 60, k0=3.5)
L(magnifier(2170, 8215, 85), 5, 5.8, BLUE, 10, sfx="wood_low")
T("看清再点", 2400, 8600, 66, GREEN, k0=6, k1=7, sfx="ding")

scene("想想对方怎么听", "做法三 · 说之前换位", (1150, 9500, 0.85))
T("③ 说之前换位", 1150, 9080, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(join(kuai(760, 9820, 0.6, "point"), face(760, 9820, 0.6, "smile")), 2, 2.8, RED, 9, sfx="wood_high")
L(bubble(930, 9330, 360, 120, -1), 3, 3.4, BLACK, 8, sfx="pop")
T("这样不行", 930, 9350, 56, k0=3.4)
L(join(man(1500, 9820, 0.6), face(1500, 9820, 0.6, "flat")), 5, 5.8, BLUE, 9, sfx="wood_low")
L(arrow((860, 9900), (1420, 9900), 0.18, 34), 6, 6.8, ORANGE, 9, sfx="shaker")
T("他会怎么听？", 1440, 9420, 56, BLUE, k0=7, k1=8)

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5150, 0.095)
CMT = (2450, 9500, 0.85)
j_end = scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(j_end, 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你最近换过哪句话的说法？", 2450, 9100, 64, RED, k0=6, k1=9, sfx="pop")
L(join(kuai(2200, 9850, 0.6, "up"), face(2200, 9850, 0.6, "smile")), 9, 9.8, RED, 9, sfx="wood_high")
L(join(man(2700, 9850, 0.6), face(2700, 9850, 0.6, "smile")), 10, 10.8, BLUE, 9, sfx="wood_low")
T("下一讲：一段经历，只记住最高点和结尾？", 2450, 9250, 46, k0=11, k1=15.75, sfx="pop")
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(9, "frame", "框架效应", "同一件事，换个说法就变了？", ACC, b.shots,
                 [f"{BOOK}第34章 善用框架效应，让生活更美好（Frames and Reality）（转述）",
                  "中译本：胡晓姣、李爱民、何梦莹译，中信出版社 2012"],
                 "同一件事|换个【说法】就变了", SQUARE_SHOT,
                 ["书中观点均为转述：同一个手术结果，说成“一个月存活率 90%”比说成“一个月死亡率 10%”更让人愿意选手术，"
                  "医生也受这种说法影响（第 34 章）。画框里的“存活率90%”“死亡率10%”为书中数据的简写，省略了“一个月”；"
                  "对勾与问号为示意，不是书中数据。",
                  "亚洲疾病问题：600 人面临疫情，同一个方案说成“救活 200 人”或“400 人会死”，多数人的选择反过来"
                  "（第 34 章）。600、200、400 为书中数据；点阵、对勾与叉为示意。",
                  "器官捐献：默认同意的国家捐献率远高于需要自己勾选同意的国家（第 34 章）。两根柱子的高低为示意，"
                  "不是书中数据。",
                  "开局的周报（进度九成，“完成了九成”与“还有一成没做完”，老板笑与皱眉）为现实场景示意；"
                  "“90% 完成 = 10% 没做”为示意。",
                  "两句原话改写（“这事做不了”→“下周三能交，先砍掉这块”；“你怎么还没交”→“周四前给我，好排下一步”）"
                  "为职场场景示意，不指向任何具体公司或个人。",
                  "三条做法（自己翻个面、先看默认项、说之前换位）为据书中思路整理的建议；续费页为示意，不指向具体产品。"],
                 tags="#沟通 #表达")
    return b.attach(ep)
