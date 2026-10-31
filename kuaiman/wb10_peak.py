"""10 峰终定律（白板手绘版）：一段经历，只记住最高点和结尾？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版：3 小节场景第 0–8 拍画完，最后 4 拍停住）。
叙事（形式 I 曲线故事，两条疼痛曲线讲完一个道理）：两张病床、病人A 和病人B 做检查 →
A 的疼痛曲线约 8 分钟、在最疼时戛然而止 → B 的曲线约 24 分钟、同样有高峰、最后慢慢降下来 →
drop：拉远同框看两条曲线，“峰”和“终”亮红圈，“B 记得没那么糟”砸下 →
亮书（快快、慢慢出场，“峰终定律”）→ 书中观点（时长箭头被划掉：忽略时长）→
书中实验（冷水：60 秒 / 90 秒且最后 30 秒稍暖，多数人愿意再来长的那次）→
书中观点（体验的我一路走一路感受，记忆的我在终点拿相册记账）→
换到右列，用曲线看生活（旅行最后一天吵架、汇报结尾被问住）→
做法（好的放结尾：聚餐最后上甜品 / 难受的事收个缓尾 / 照片全删还去吗）→ 拉远看全板 → 评论区互动，这一季讲完。
白板分区：左列（场景 1–8，自上而下），右列（场景 9–14，自下而上），每行相隔 ≥1300，上一行的字不漏进页眉带。
书中观点为转述：丹尼尔·卡尼曼《思考，快与慢》第35章“体验效用与决策效用的不一致”（Two Selves）、
第36章“人生如戏”（Life as a Story）；中译本胡晓姣、李爱民、何梦莹译，中信出版社 2012。
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, cross,
                               face, join, rect, stick, underline)

from .common import BOOK, episode, kuai, man

ACC = "#8A5BB0"
SQUARE_SHOT = 3                 # 场景 4：两条疼痛曲线 + 峰 / 终红圈 + 病人A（皱眉）、病人B（平静）

b = Board(size=(3600, 9000))

# 白板分区：左列中心 XL（场景 1–8 自上而下），右列中心 XR（场景 9–14 自下而上）
XL, XR = 1150, 2650


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def ellipse(x, y, w, h) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h))
    return p


def bed(x, y, w=460) -> skia.Path:
    """病床（侧视）+ 平躺的病人：(x, y) 为床面中点，床头在左。"""
    l, r = x - w / 2, x + w / 2
    frame = join(P((l, y - 130), (l, y + 110)), P((l, y), (r, y)), P((l, y + 40), (r, y + 40)),
                 P((r, y - 40), (r, y + 110)), rect(l + 70, y - 22, 90, 36, 14))
    hx, hy = l + 80, y - 72
    body = join(circle(hx, hy, 36), P((hx + 36, y - 60), (r - 90, y - 60)),
                P((r - 90, y - 60), (r - 20, y - 70)), P((r - 90, y - 60), (r - 25, y - 45)),
                P((hx + 60, y - 60), (hx + 130, y - 95), (hx + 190, y - 60)))
    return join(frame, body)


def lying_face(x, y, w=460, mood="flat") -> skia.Path:
    """床上病人的五官（配合 bed）。"""
    hx, hy = x - w / 2 + 80, y - 72
    p = skia.Path()
    p.addCircle(hx - 12, hy - 8, 3.5)
    p.addCircle(hx + 12, hy - 8, 3.5)
    if mood == "sad":
        p.addArc(skia.Rect.MakeXYWH(hx - 14, hy + 8, 28, 20), 200, 140)
    else:
        p.moveTo(hx - 12, hy + 16)
        p.lineTo(hx + 12, hy + 16)
    return p


class Chart:
    """疼痛 / 心情坐标：x 轴按分钟（或天）等比，y 轴 0–10。(x0, base) 为原点。"""

    def __init__(self, x0, base, w, h, span):
        self.x0, self.base, self.w, self.h, self.span = x0, base, w, h, span

    def pt(self, t, v):
        return self.x0 + self.w * t / self.span, self.base - self.h * v / 10

    def axes(self) -> skia.Path:
        x0, y0, x1, y1 = self.x0, self.base, self.x0 + self.w + 30, self.base - self.h - 40
        return join(P((x0, y1), (x0, y0), (x1, y0)), P((x0 - 18, y1 + 30), (x0, y1), (x0 + 18, y1 + 30)),
                    P((x1 - 30, y0 - 18), (x1, y0), (x1 - 30, y0 + 18)))

    def curve(self, pts) -> skia.Path:
        """手绘感曲线：相邻点之间用二次曲线连到中点，过渡圆滑。"""
        q = [self.pt(t, v) for t, v in pts]
        p = skia.Path()
        p.moveTo(*q[0])
        for i in range(1, len(q) - 1):
            mx, my = (q[i][0] + q[i + 1][0]) / 2, (q[i][1] + q[i + 1][1]) / 2
            p.quadTo(q[i][0], q[i][1], mx, my)
        p.lineTo(*q[-1])
        return p

    def tick(self, t) -> skia.Path:
        x, _ = self.pt(t, 0)
        return P((x, self.base - 18), (x, self.base + 18))


def glow_fn(pts, r=78, color=RED):
    """drop 后峰 / 终两点的红色光晕：一拍一呼吸，持续到场景结束（动态项，不计入停留检查）。"""

    def fn(c, k, t):
        ph = 0.5 + 0.5 * math.sin(t * math.tau)
        for x, y in pts:
            c.drawCircle(x, y, r * (1.05 + 0.12 * ph), K.paint(color, 0.10 + 0.10 * ph, blur=26))
        return None

    return fn


def camera_body(x, y) -> skia.Path:
    return join(rect(x, y, 240, 160, 22), circle(x, y + 6, 50), circle(x, y + 6, 26),
                P((x - 80, y - 80), (x - 60, y - 112), (x - 10, y - 112), (x + 10, y - 80)), circle(x + 82, y - 48, 10))


def cake(x, y) -> skia.Path:
    """一块蛋糕 + 蜡烛：(x, y) 为底边中点。"""
    return join(P((x - 90, y), (x - 90, y - 90), (x + 90, y - 90), (x + 90, y), close=True),
                P((x - 90, y - 50), (x - 60, y - 36), (x - 30, y - 50), (x, y - 36), (x + 30, y - 50), (x + 60, y - 36),
                  (x + 90, y - 50)),
                P((x, y - 90), (x, y - 150)), P((x, y - 168), (x - 10, y - 152), (x, y - 145), (x + 10, y - 152),
                                                close=True))


def star(x, y, r=40) -> skia.Path:
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return P(*pts, close=True)


def basin(x, y) -> skia.Path:
    """水盆：(x, y) 为水面中点。"""
    return join(P((x - 210, y - 50), (x - 165, y + 190), (x + 165, y + 190), (x + 210, y - 50)),
                underline(x - 195, x + 195, y, 10, 39))


def hand_in(x, top, bottom) -> skia.Path:
    """伸进水里的手臂和手：从 top 伸到 bottom。"""
    return join(P((x - 34, top), (x - 34, bottom - 40)), P((x + 34, top), (x + 34, bottom - 40)),
                P((x - 34, bottom - 40), (x - 30, bottom - 8), (x - 10, bottom), (x + 10, bottom), (x + 30, bottom - 8),
                  (x + 34, bottom - 40)),
                P((x - 12, bottom - 4), (x - 12, bottom - 36)), P((x + 12, bottom - 4), (x + 12, bottom - 36)))


def album(x, y) -> skia.Path:
    return join(rect(x, y, 110, 84, 6), P((x, y - 42), (x, y + 42)), rect(x - 28, y - 6, 34, 30, 3),
                rect(x + 28, y - 6, 34, 30, 3))


def table(x, y, w=1000) -> skia.Path:
    return join(P((x - w / 2, y), (x + w / 2, y)), P((x - w / 2 + 50, y), (x - w / 2 + 50, y + 150)),
                P((x + w / 2 - 50, y), (x + w / 2 - 50, y + 150)))


# ---------------------------------------------------------------- 开局：两个病人，两条曲线（场景 1–4，左列）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

BA, BB, BY = XL - 330, XL + 330, 1000          # 两张病床的中点（床面高度 BY）

scene("两个病人做检查", "两个病人", (XL, 880, 0.85), bars=2)
L(join(bed(BA, BY), lying_face(BA, BY)), 0, 0.9, BLACK, 9, sfx="wood_high")
L(rect(BA, 760, 210, 90, 14), 1, 1.4, BLACK, 7, sfx="pop")
T("病人A", BA, 762, 56, k0=1.4, k1=2.2)
L(join(bed(BB, BY), lying_face(BB, BY)), 2, 2.9, BLACK, 9, sfx="wood_high")
L(rect(BB, 760, 210, 90, 14), 3, 3.4, BLACK, 7, sfx="pop")
T("病人B", BB, 762, 56, k0=3.4, k1=4.2)
T("做同一种检查", XL, 520, 76, ACC, k0=4, k1=5.5, sfx="pop")

# 两张图同一比例：横轴 24 分钟，纵轴疼痛 0–10；A 在上、B 在下，原点 x 对齐
X0, XW, HH = XL - 580, 1140, 450
CA = Chart(X0, 2200, XW, HH, 24)
CB = Chart(X0, 3350, XW, HH, 24)
PA = [(0, 0), (1, 2), (2, 4), (3, 3), (4, 5), (5, 6.5), (6, 5.5), (7, 7.5), (8, 8)]
PB_HEAD = PA
PB_TAIL = [(8, 8), (9, 6.5), (10, 7), (11, 5.5), (13, 4.5), (15, 4), (17, 3), (19, 2.5), (21, 1.8), (23, 1.2),
           (24, 1)]
A_END, B_PEAK, B_END = CA.pt(8, 8), CB.pt(8, 8), CB.pt(24, 1)


def chart_frame(ch, who):
    L(ch.axes(), 0, 0.9, BLACK, 8, sfx="wood_high")
    T("疼痛", ch.x0 + 95, ch.base - HH - 45, 54, k0=1, k1=1.6, sfx="pop")
    T("分钟", ch.x0 + XW - 20, ch.base + 62, 50, k0=1.6, k1=2.2)
    T(who, XL + 330, ch.base - HH - 45, 64, ACC, k0=2, k1=2.8, sfx="pop")


scene("第一个：短，疼着结束", "病人A · 短", (XL, 1980, 0.85))
chart_frame(CA, "病人A")
L(CA.curve(PA), 3, 4.8, ACC, 11, sfx="wood_low")
L(CA.tick(8), 5, 5.3, BLACK, 7, sfx="pop")
T("8分钟", CA.pt(8, 0)[0], CA.base + 62, 50, k0=5.3, k1=6)
L(circle(*A_END, 14), 6, 6.5, RED, 12, sfx="rim")
T("疼着结束", A_END[0] + 230, A_END[1] - 30, 62, RED, k0=7, k1=8, sfx="ding")

scene("第二个：长，慢慢收尾", "病人B · 长", (XL, 3130, 0.85))
chart_frame(CB, "病人B")
L(CB.curve(PB_HEAD), 3, 3.9, ACC, 11, sfx="wood_low")
L(CB.curve(PB_TAIL), 4, 5.8, ACC, 11, sfx="shaker")
L(CB.tick(24), 6, 6.3, BLACK, 7, sfx="pop")
T("24分钟", CB.pt(24, 0)[0] - 40, CB.base + 62, 50, k0=6.3, k1=7)
T("慢慢收尾", CB.pt(16, 0)[0], CB.pt(16, 6.6)[1], 62, BLUE, k0=7, k1=8, sfx="ding")

PA_X = XL + 820                 # drop 时同框才看得到的两位病人（曲线右侧）
j_drop = scene("长的那个，记得更好", "峰和终", (XL + 120, 2560, 0.53), shake=[0, 4], flashes=[0])
L(circle(*A_END, 70), 0, 0.8, RED, 12, sfx="kick")
L(circle(*B_PEAK, 70), 1, 1.8, RED, 12, sfx="ding")
L(circle(*B_END, 70), 2, 2.8, RED, 12, sfx="ding")
b.custom(j_drop, 3, 12, glow_fn([A_END, B_PEAK, B_END]))
T("峰也是终", A_END[0] + 250, A_END[1] - 10, 80, RED, k0=3, k1=4, sfx="pop")
T("峰", B_PEAK[0] + 130, B_PEAK[1] - 40, 80, RED, k0=3.4, k1=3.8)
T("终", B_END[0], B_END[1] - 125, 80, RED, k0=3.8, k1=4.2)
T("B 记得没那么糟", XL + 100, 2570, 104, RED, k0=4, k1=5.75, sfx="kick")
L(join(stick(PA_X, 2180, 0.62, "down"), face(PA_X, 2180, 0.62, "sad")), 6, 6.9, BLACK, 9, sfx="wood_high")
L(join(stick(PA_X, 3330, 0.62, "down"), face(PA_X, 3330, 0.62, "smile")), 7, 7.9, BLUE, 9, sfx="wood_low")

# ---------------------------------------------------------------- 书中观点（场景 5–8，左列）

scene("只记最高点和结尾", "思考，快与慢 · 书中观点", (XL, 4350, 0.85))
L(book(XL - 380, 4250, 380, 260), 0, 0.9, sfx="wood_low")
T("思考，快与慢", XL - 380, 4040, 60, GREEN, k0=1, k1=2.5, sfx="pop")
L(join(kuai(XL + 230, 4620, 0.6), face(XL + 230, 4620, 0.6, "smile")), 3, 3.9, RED, 9, sfx="wood_high")
L(join(man(XL + 520, 4620, 0.6), face(XL + 520, 4620, 0.6, "flat")), 4, 4.9, BLUE, 9, sfx="wood_high")
T("峰终定律", XL - 380, 4540, 90, RED, k0=5, k1=6, sfx="pop")
L(underline(XL - 570, XL - 190, 4610), 7, 7.8, ORANGE, 8, sfx="ding")

scene("多久，几乎不算", "书中观点 · 忽略时长", (XL, 5650, 0.85))
L(arrow((XL - 540, 5600), (XL + 540, 5600), 0.0, 50), 0, 0.9, BLACK, 10, sfx="wood_high")
T("时长", XL, 5500, 64, k0=1, k1=1.8, sfx="pop")
T("8分钟", XL - 420, 5700, 56, ACC, k0=2, k1=2.8, sfx="pop")
T("24分钟", XL + 400, 5700, 56, ACC, k0=3, k1=3.8, sfx="pop")
L(cross(XL, 5600, 110), 4, 4.9, RED, 12, sfx="rim")
T("忽略时长", XL, 5930, 96, RED, k0=5, k1=6, sfx="pop")
L(underline(XL - 200, XL + 200, 6000), 7, 7.8, RED, 8, sfx="ding")

WL, WR, WY = XL - 350, XL + 350, 6980             # 两盆冷水（水面高度 WY）
scene("多泡半分钟，更愿意", "书中实验 · 冷水", (XL, 6950, 0.85))
L(basin(WL, WY), 0, 0.9, BLUE, 9, sfx="wood_high")
L(hand_in(WL, 6640, 7080), 1, 1.9, BLACK, 9, sfx="wood_low")
T("60秒", WL, 6570, 60, BLUE, k0=2, k1=2.8, sfx="pop")
L(join(basin(WR, WY), hand_in(WR, 6640, 7080)), 3, 3.9, BLUE, 9, sfx="wood_high")
T("90秒", WR, 6570, 60, BLUE, k0=4, k1=4.8, sfx="pop")
T("最后30秒稍暖", WR, 7260, 50, ORANGE, k0=5, k1=6.5, sfx="pop")
L(check(WR - 210, 7385, 34), 6, 6.6, GREEN, 10, sfx="wood_high")
T("多数人选它", WR + 30, 7385, 58, GREEN, k0=7, k1=8, sfx="ding")

scene("过日子和记账的我", "书中观点 · 两个自我", (XL, 8250, 0.85))
L(underline(XL - 560, XL + 440, 8520, 12, 50), 0, 0.9, BLACK, 8, sfx="wood_high")
L(join(kuai(XL - 420, 8500, 0.55, "point"), face(XL - 420, 8500, 0.55, "smile")), 1, 1.9, RED, 9, sfx="pop")
T("好…累…疼…", XL - 40, 8330, 58, RED, k0=2, k1=3.25, sfx="pop")
L(join(man(XL + 400, 8500, 0.55, "hold"), face(XL + 400, 8500, 0.55, "flat"), album(XL + 490, 8370)), 4, 4.9,
  BLUE, 9, sfx="wood_low")
T("体验的我", XL - 420, 8620, 56, RED, k0=5, k1=6, sfx="pop")
T("记忆的我", XL + 400, 8620, 56, BLUE, k0=6, k1=7, sfx="pop")
L(ellipse(XL + 490, 8370, 170, 140), 7, 7.8, ORANGE, 8, sfx="ding")

# ---------------------------------------------------------------- 用曲线看生活（场景 9–10，右列，自下而上）

TR = Chart(XR - 580, 8450, 1100, 450, 5)          # 旅行：横轴 5 天，纵轴开心
scene("最后一天，毁了整趟", "例子 · 旅行", (XR, 8300, 0.85))
L(TR.axes(), 0, 0.9, BLACK, 8, sfx="wood_high")
T("开心", TR.x0 + 95, 7955, 54, k0=1, k1=1.6, sfx="pop")
T("天", TR.x0 + 1110, TR.base + 62, 50, k0=1.6, k1=2)
L(TR.curve([(0, 6), (0.6, 7.5), (1.2, 7), (2, 8.6), (2.8, 7.8), (3.5, 8.8), (4, 8.2)]), 2, 3.8, ACC, 11,
  sfx="wood_low")
L(P(TR.pt(4, 8.2), TR.pt(4.35, 4), TR.pt(4.8, 0.6)), 4, 4.6, RED, 12, sfx="rim")
T("最后一天", TR.pt(4.4, 0)[0], TR.base + 62, 50, RED, k0=5, k1=5.8, sfx="pop")
T("赶飞机，吵架", TR.pt(2.9, 0)[0], TR.pt(0, 1.6)[1], 58, RED, k0=6, k1=7.25, sfx="pop")
T("回想：这趟真糟", XR + 60, 7880, 62, BLUE, k0=7, k1=8, sfx="ding")

RP = Chart(XR - 580, 7100, 1100, 450, 10)         # 汇报：横轴 10 分钟，纵轴顺利
DIP = RP.pt(9.6, 2)
scene("汇报结尾，最被记住", "例子 · 汇报", (XR, 6950, 0.85))
L(RP.axes(), 0, 0.9, BLACK, 8, sfx="wood_high")
T("顺利", RP.x0 + 95, 6605, 54, k0=1, k1=1.6, sfx="pop")
T("分钟", RP.x0 + 1080, RP.base + 62, 50, k0=1.6, k1=2.2)
L(RP.curve([(0, 5), (1, 6.5), (2.5, 7), (4, 6.6), (5.5, 7.4), (7, 7), (8.6, 7.2)]), 2, 3.8, ACC, 11, sfx="wood_low")
L(RP.curve([(8.6, 7.2), (9.1, 5), (9.6, 2)]), 4, 4.5, RED, 12, sfx="rim")
L(bubble(DIP[0] - 260, 6620, 300, 110, 1), 5, 5.5, BLACK, 8, sfx="pop")
T("这个……", DIP[0] - 260, 6624, 54, k0=5.5, k1=6.3)
L(circle(*DIP, 64), 6, 6.8, RED, 11, sfx="ding")
T("大家只记得这下", XR, 7240, 62, k0=7, k1=8, sfx="pop")

# ---------------------------------------------------------------- 具体做法（场景 11–13，右列）

scene("好的留到最后", "做法一 · 好的放结尾", (XR, 5600, 0.85))
T("① 把好的放结尾", XR, 5230, 76, BLUE, k0=0, k1=1.75, sfx="pop")
L(table(XR, 5700, 1000), 2, 2.9, BLACK, 9, sfx="wood_high")
L(join(ellipse(XR - 380, 5672, 190, 44), ellipse(XR - 110, 5672, 190, 44),
       P((XR - 430, 5650), (XR - 380, 5620), (XR - 330, 5650)), P((XR - 160, 5650), (XR - 110, 5615), (XR - 60, 5650))),
  3, 3.9, BLACK, 8, sfx="pop")
L(cake(XR + 250, 5700), 4, 4.9, ORANGE, 9, sfx="wood_low")
L(star(XR + 250, 5440, 40), 5, 5.6, ORANGE, 8, sfx="ding")
T("最后上甜品", XR, 5975, 64, GREEN, k0=6, k1=7.25, sfx="pop")

SL = Chart(XR - 520, 4480, 1000, 400, 10)
SPK = SL.pt(5, 8.5)
scene("难受的事，收个缓尾", "做法二 · 收个缓尾", (XR, 4250, 0.85))
T("② 别在最难受时停", XR, 3870, 76, BLUE, k0=0, k1=2, sfx="pop")
L(SL.axes(), 2, 2.9, BLACK, 8, sfx="wood_high")
L(SL.curve([(0, 2), (1.5, 4), (3, 5.5), (4.2, 7.5), (5, 8.5)]), 3, 3.9, ACC, 11, sfx="wood_low")
L(SL.curve([(5, 8.5), (6, 6), (7.5, 4), (9, 2.6), (10, 2)]), 4, 5.5, GREEN, 11, sfx="shaker")
T("收尾聊两句轻松的", SL.pt(7.5, 0)[0] - 30, SL.pt(0, 7.6)[1], 54, GREEN, k0=6, k1=8, sfx="ding")

CX, DX = XR - 230, XR + 230
scene("照片全删，还去吗", "做法三 · 问问自己", (XR, 2900, 0.85))
T("③ 问问自己", XR, 2530, 76, BLUE, k0=0, k1=1.25, sfx="pop")
L(camera_body(CX, 2780), 2, 2.9, BLACK, 9, sfx="wood_high")
L(rect(DX, 2780, 260, 110, 20), 3, 3.4, RED, 9, sfx="rim")
T("全删", DX, 2782, 64, RED, k0=3.4, k1=4.2)
L(join(kuai(XR - 360, 3300, 0.55), face(XR - 360, 3300, 0.55, "flat")), 5, 5.9, RED, 9, sfx="wood_high")
L(join(man(XR + 360, 3300, 0.55), face(XR + 360, 3300, 0.55, "flat")), 6, 6.9, BLUE, 9, sfx="wood_low")
T("还去吗？", XR, 3160, 70, RED, k0=7, k1=8, sfx="ding")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 4600, 0.105)
CMT = (XR, 1550, 0.85)
j_end = scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(j_end, 4, CMT, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你记得最清的一段，结尾怎样？", XR, 1250, 74, RED, k0=6, k1=9, sfx="pop")
L(join(kuai(XR - 260, 1950, 0.6, "up"), face(XR - 260, 1950, 0.6, "smile")), 9, 9.8, RED, 9, sfx="wood_high")
L(join(man(XR + 260, 1950, 0.6), face(XR + 260, 1950, 0.6, "smile")), 10, 10.8, BLUE, 9, sfx="wood_low")
T("这一季讲完了", XR, 1430, 60, k0=11, k1=12.5, sfx="pop")
L(join(P((XR + 330, 1690), (XR + 360, 1710)), P((XR + 330, 1730), (XR + 362, 1745))), 13, 13.5, BLUE, 7,
  sfx="wood_low")
b.hit(j_end, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(10, "peak", "峰终定律", "一段经历，只记住最高点和结尾？", ACC, b.shots,
                 [f"{BOOK}第35章 体验效用与决策效用的不一致（Two Selves）（转述）",
                  f"{BOOK}第36章 人生如戏（Life as a Story）（转述）",
                  "中译本：胡晓姣、李爱民、何梦莹译，中信出版社 2012"],
                 "一段经历|只记住【最高点】和结尾", SQUARE_SHOT,
                 ["书中观点均为转述：结肠镜研究里，病人A 检查约 8 分钟、在最疼的时候结束，病人B 约 24 分钟、结尾较轻；"
                  "事后 B 对整个检查的回忆没那么糟。回忆主要看最痛的时刻和结尾，几乎不管持续多久，书中称为峰终定律与"
                  "忽略时长（第 35 章）。8 分钟、24 分钟为书中数据；两条曲线的起伏形状为示意，不是书中逐分钟的读数。",
                  "冷水实验：一次手泡冷水 60 秒；另一次 90 秒，最后 30 秒水温稍升，多数人选择重来长的那次（第 35 章）。"
                  "60 秒 / 90 秒 / 30 秒为书中数据，水盆与手的画面为示意。",
                  "人有体验的自我和记忆的自我，做决定的常是记忆的自我（第 35 章）；快快一路感受、慢慢拿相册记账的画面为"
                  "通俗化示意。书中还问：假如旅行结束后照片全删、记忆全忘，你还会选这趟旅行吗（第 36 章）。",
                  "旅行最后一天赶飞机吵架、汇报结尾被问住、聚餐最后上甜品均为现实场景示意，不指向任何具体公司或个人；"
                  "曲线、天数与分钟刻度为示意。",
                  "“把好的放结尾”“别在最难受时停、收个缓尾”“问问自己照片全删还去吗”为据书中思路整理的建议。"],
                 tags="#峰终定律 #幸福感")
    return b.attach(ep)
