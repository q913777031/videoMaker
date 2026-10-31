"""01 三重大脑（白板手绘版）：说好十一点睡，怎么又刷到一点？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版）。
叙事形式 B 一个故事贯穿：小林一个晚上的经历——十点到家，便签上写着“学一小时、十一点睡”→
一进门先瘫沙发、拿起手机（挂钟走到十点半）→ 一抬头凌晨一点，便签划红叉 →
drop：小林的脑袋“咔”地掀开，三兄弟同时弹出，年龄牌 100 / 55 / 1 砸下 →
亮书（《认知觉醒》+ 周岭，书旁一个舵写“01”）→ 三兄弟挂上名牌（本能脑 / 情绪脑 / 理智脑，宝宝抱着舵）→
每个转折谁抢了主意：老大一屁股坐上躺椅（能躺不坐）、老二举着手机冒爱心（马上要开心）、
宝宝伸手够舵被两只大手拨开（出现晚、细胞少、跑得慢）→ 先拿手机、后补理由“明天再学也一样” →
做法（进门先把手机放客厅充电；想拿手机先停几秒，宝宝第一次摸到舵、舵上第一道握痕）→
同一个十点分出两条路：刷到一点 / 十一点关灯 → 评论区互动。
书中观点为转述（周岭《认知觉醒》第一章第一节“大脑：重新认识你自己”）；
例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_out
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, circle, clock, cross, face,
                               hands_at, join, rect, stick)

from .common import BOOK, episode

ACC = "#3F6FB5"
SQUARE_SHOT = 5                 # 场景 6：脑袋剖面里三兄弟并排，年龄牌 100 / 55 / 1，宝宝抱舵

b = Board(size=(3600, 10700))
PAPER = "#FBFBF9"
OY = 0                          # 后面几排整体下移，免得上一排的字漏进屏幕顶端


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y + OY, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    if OY:
        path = skia.Path(path)
        path.offset(0, OY)
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def C(fn, k0, k1, sfx=None):
    oy = OY

    def shifted(c, k, t):
        c.save()
        c.translate(0, oy)
        tip = fn(c, k, t)
        c.restore()
        return (tip[0], tip[1] + oy) if tip else None

    b.custom(J(), k0, k1, shifted if oy else fn, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=(view[0], view[1] + OY, view[2]), bars=bars, **kw)


def ink(c, path, color, width):
    """和引擎描线同样的马克笔笔触（custom 动画里用）。"""
    c.drawPath(path, wb.marker(color, width))
    c.drawPath(path, K.paint(color, 0.22, width * 0.45, blur=1.2))


def moved(path, dx=0.0, dy=0.0, s=1.0, ax=0.0, ay=0.0, rot=0.0) -> skia.Path:
    """以 (ax, ay) 为锚点缩放、旋转后再平移的路径副本。"""
    p = skia.Path(path)
    m = skia.Matrix()
    m.setTranslate(-ax, -ay)
    m.postScale(s, s)
    m.postRotate(rot)
    m.postTranslate(ax + dx, ay + dy)
    p.transform(m)
    return p


def pop_s(k):
    """弹出：0 → 1.15 → 1。"""
    return ease_out(clamp01(k * 1.6)) * (1 + 0.15 * math.sin(math.pi * clamp01(k)))


# ---------------------------------------------------------------- 本讲画法

def note(x, y, w=380, h=200) -> skia.Path:
    """便签：卷角的方纸。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2),
                  (x - w / 2, y + h / 2), close=True),
                P((x + w / 2, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2 - 40), (x + w / 2 - 40, y + h / 2)))


def door(x, y, w=240, h=500) -> skia.Path:
    """门：(x, y) 为门中心。"""
    return join(rect(x, y, w, h, 6), circle(x + w / 2 - 34, y + 10, 12))


def sofa(x, y, s=1.0) -> skia.Path:
    """沙发：(x, y) 为地面中点。"""
    return join(rect(x, y - 270 * s, 640 * s, 150 * s, 24 * s), rect(x, y - 160 * s, 640 * s, 100 * s, 20 * s),
                rect(x - 345 * s, y - 190 * s, 70 * s, 180 * s, 26 * s), rect(x + 345 * s, y - 190 * s, 70 * s, 180 * s, 26 * s),
                P((x - 290 * s, y - 110 * s), (x - 290 * s, y)), P((x + 290 * s, y - 110 * s), (x + 290 * s, y)))


def slump(x, y) -> skia.Path:
    """瘫在沙发上举着手机的小林：(x, y) 为头顶附近的锚点（头在左扶手上）。"""
    hx, hy = x, y
    p = skia.Path()
    p.addCircle(hx - 14, hy - 4, 4)
    p.addCircle(hx + 12, hy - 10, 4)
    return join(circle(hx, hy, 40), p, P((hx - 6, hy + 18), (hx + 14, hy + 14)),
                P((hx + 38, hy + 22), (hx + 230, hy + 52)),
                P((hx + 230, hy + 52), (hx + 370, hy + 30), (hx + 500, hy + 60)),
                P((hx + 230, hy + 52), (hx + 380, hy + 62), (hx + 520, hy + 100)),
                P((hx + 90, hy + 34), (hx + 110, hy - 70), (hx + 70, hy - 130)))


def grandpa(x, y, s=1.0) -> skia.Path:
    """老大“本能脑”：驼背、白胡子、拄拐的老爷爷。(x, y) 为脚底。"""
    hy = y - 285 * s
    hook = skia.Path()
    hook.moveTo(x + 70 * s, hy + 150 * s)
    hook.quadTo(x + 72 * s, hy + 108 * s, x + 40 * s, hy + 118 * s)
    return join(circle(x - 10 * s, hy, 45 * s),
                P((x - 45 * s, hy + 18 * s), (x - 10 * s, hy + 78 * s), (x + 25 * s, hy + 18 * s)),
                P((x - 10 * s, hy + 45 * s), (x - 30 * s, hy + 120 * s), (x - 5 * s, y - 120 * s)),
                P((x - 55 * s, y), (x - 5 * s, y - 120 * s), (x + 45 * s, y)),
                P((x - 22 * s, hy + 95 * s), (x + 70 * s, hy + 160 * s)),
                P((x + 70 * s, y), (x + 70 * s, hy + 150 * s)), hook)


def uncle(x, y, s=1.0) -> skia.Path:
    """老二“情绪脑”：戴耳机、攥着手机的大叔。(x, y) 为脚底。"""
    hy = y - 290 * s
    band = skia.Path()
    band.addArc(skia.Rect.MakeXYWH(x - 58 * s, hy - 62 * s, 116 * s, 116 * s), 180, 180)
    return join(stick(x, y, s, "hold"), band, rect(x - 54 * s, hy, 22 * s, 44 * s, 8 * s),
                rect(x + 54 * s, hy, 22 * s, 44 * s, 8 * s))


def baby(x, y, s=1.0, arms="up") -> skia.Path:
    """老三“理智脑”：大头、戴围嘴的小宝宝。(x, y) 为脚底；arms：up（双手举过头）/ reach（右手往右上够）。"""
    hy = y - 150 * s
    r = 55 * s
    bib = skia.Path()
    bib.addArc(skia.Rect.MakeXYWH(x - 30 * s, hy + r - 22 * s, 60 * s, 50 * s), 0, 180)
    curl = skia.Path()
    curl.moveTo(x - 6 * s, hy - r)
    curl.quadTo(x + 4 * s, hy - r - 26 * s, x + 18 * s, hy - r - 12 * s)
    eyes = skia.Path()
    eyes.addCircle(x - 18 * s, hy - 4 * s, 3.5 * s)
    eyes.addCircle(x + 18 * s, hy - 4 * s, 3.5 * s)
    if arms == "reach":
        hands = join(P((x - 22 * s, hy + r + 12 * s), (x - 60 * s, hy + r + 60 * s)),
                     P((x + 22 * s, hy + r + 12 * s), (x + 110 * s, hy - 70 * s)))
    else:
        hands = join(P((x - 24 * s, hy + r + 8 * s), (x - 70 * s, hy - 50 * s)),
                     P((x + 24 * s, hy + r + 8 * s), (x + 70 * s, hy - 50 * s)))
    return join(circle(x, hy, r), curl, eyes, P((x - 8 * s, hy + 22 * s), (x + 8 * s, hy + 22 * s)), bib,
                P((x, hy + r), (x, y - 50 * s)), P((x - 34 * s, y), (x, y - 50 * s), (x + 34 * s, y)), hands)


def helm(x, y, r=90) -> skia.Path:
    """船舵：外圈 + 轴心 + 八根带把手的辐条。"""
    parts = [circle(x, y, r), circle(x, y, r * 0.3)]
    for i in range(8):
        a = i / 8 * 2 * math.pi + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        parts.append(P((x + ca * r * 0.3, y + sa * r * 0.3), (x + ca * r * 1.32, y + sa * r * 1.32)))
        parts.append(circle(x + ca * r * 1.36, y + sa * r * 1.36, r * 0.07))
    return join(*parts)


def heart(x, y, r=50) -> skia.Path:
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.7, y - r * 0.2, x - r * 0.65, y - r * 1.35, x, y - r * 0.45)
    p.cubicTo(x + r * 0.65, y - r * 1.35, x + r * 1.7, y - r * 0.2, x, y + r * 0.9)
    return p


def phone(x, y, w=70, h=120) -> skia.Path:
    return join(rect(x, y, w, h, max(6, w * 0.15)), P((x - w * 0.17, y + h / 2 - h * 0.1), (x + w * 0.17, y + h / 2 - h * 0.1)))


def recliner(x, y) -> skia.Path:
    """躺椅：(x, y) 为地面中点；右边靠着一根拐杖。"""
    hook = skia.Path()
    hook.moveTo(x + 400, y - 300)
    hook.quadTo(x + 404, y - 350, x + 360, y - 340)
    return join(P((x - 330, y - 450), (x - 190, y - 150), (x + 180, y - 150), (x + 330, y - 210)),
                P((x - 300, y - 460), (x - 360, y - 440)),
                P((x - 170, y - 150), (x - 230, y)), P((x + 160, y - 150), (x + 220, y)),
                P((x - 260, y), (x + 280, y)), P((x + 410, y), (x + 400, y - 300)), hook)


def lounger(x, y) -> skia.Path:
    """仰在躺椅上的老爷爷：(x, y) 为椅面中点（与 recliner 同一 x、地面 y-150）。"""
    hx, hy = x - 310, y - 330
    return join(circle(hx, hy, 45), P((hx - 30, hy + 22), (hx + 8, hy + 78), (hx + 40, hy + 18)),
                P((hx + 20, hy + 40), (x - 150, y - 30)), P((x - 150, y - 30), (x + 140, y - 40), (x + 300, y - 100)),
                P((hx + 60, hy + 110), (x - 120, y - 120), (x - 40, y - 90)))


def bighand(x, y, ang=0.0, s=1.0) -> skia.Path:
    """一只大手 + 袖子从画外伸进来：(x, y) 为手掌中心，ang 为手指朝向（度）。"""
    palm = rect(30, 0, 120, 92, 40)
    th = skia.Path()
    th.moveTo(0, -40)
    th.quadTo(20, -86, 54, -64)
    p = join(palm, th, P((60, -18), (88, -18)), P((60, 12), (88, 12)), rect(-46, 0, 30, 110, 8),
             P((-62, -48), (-460, -48)), P((-62, 48), (-460, 48)))
    m = skia.Matrix()
    m.setScale(s, s)
    m.postRotate(ang)
    m.postTranslate(x, y)
    p.transform(m)
    return p


def plug(x, y) -> skia.Path:
    """墙上插座：(x, y) 为面板中心。"""
    return join(rect(x, y, 70, 90, 10), P((x - 12, y - 14), (x - 12, y + 6)), P((x + 12, y - 14), (x + 12, y + 6)))


def bolt(x, y, s=1.0) -> skia.Path:
    return P((x + 25 * s, y - 80 * s), (x - 30 * s, y + 5 * s), (x + 12 * s, y + 5 * s), (x - 22 * s, y + 80 * s))


def hourglass(x, y, s=1.0) -> skia.Path:
    return join(P((x - 70 * s, y - 110 * s), (x + 70 * s, y - 110 * s)), P((x - 70 * s, y + 110 * s), (x + 70 * s, y + 110 * s)),
                P((x - 55 * s, y - 110 * s), (x - 8 * s, y), (x - 55 * s, y + 110 * s)),
                P((x + 55 * s, y - 110 * s), (x + 8 * s, y), (x + 55 * s, y + 110 * s)),
                P((x - 30 * s, y + 95 * s), (x, y + 60 * s), (x + 30 * s, y + 95 * s)))


def bed(x, y) -> skia.Path:
    """床 + 盖着被子睡着的小人：(x, y) 为地面中点。"""
    p = skia.Path()
    p.moveTo(x - 140, y - 150)
    p.quadTo(x + 40, y - 210, x + 220, y - 150)
    return join(P((x - 230, y), (x - 230, y - 230)), P((x + 230, y), (x + 230, y - 140)),
                P((x - 230, y - 100), (x + 230, y - 100)), circle(x - 170, y - 150, 32), p,
                P((x - 186, y - 154), (x - 170, y - 150)), P((x - 160, y - 154), (x - 148, y - 150)))


def moon(x, y, r=60) -> skia.Path:
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 60, 240)
    p.addArc(skia.Rect.MakeXYWH(x - r * 0.45, y - r * 0.95, 1.6 * r, 1.6 * r), 95, 170)
    return p


def plate_fn(x, y, label, color, w=124, h=66, size=54, fall=320, gain=1.0):
    """年龄牌从上方砸下、弹一下落定：白底圆角牌 + 数字。"""

    def fn(c, k, t):
        f = clamp01(k * 1.5)
        dy = -fall * (1 - f) ** 2 + (14 * math.sin(math.pi * clamp01((k - 0.66) / 0.34)) if k > 0.66 else 0)
        yy = y + dy * gain
        K.rr(c, x, yy, w, h, 12, PAPER)
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, yy - h / 2, w, h), 12, 12, wb.marker(color, 7))
        K.text(c, label, x, yy + 2, size, "hand", color)
        return (x + w / 2, yy) if k < 1 else None

    return fn


# ---------------------------------------------------------------- 墙上挂钟：一个指针动画管三屏

CLK = (1800, 620, 100)
_KEYS = []                      # (镜头, 拍, 钟点)：S1 十点 → S2 十点半 → S3 转到凌晨一点


def _hour_at(T):
    pts = [(b.t_of(j, k), h) for j, k, h in _KEYS]
    if T <= pts[0][0]:
        return pts[0][1]
    for (t0, h0), (t1, h1) in zip(pts, pts[1:]):
        if T < t1:
            return h0 + (h1 - h0) * wb.ease_in_out(clamp01((T - t0) / max(1e-3, t1 - t0)))
    return pts[-1][1]


def clock_hands(c, k, T):
    x, y, r = CLK
    h = _hour_at(T)
    ink(c, hands_at(x, y, r, int(h) % 12, (h - int(h)) * 60), BLACK, 9)
    return None


def spin_tip(c, k, T):
    """场景 3：手拨着分针转（只给笔尖位置，指针由 clock_hands 画）。"""
    x, y, r = CLK
    h = _hour_at(T)
    a = -math.pi / 2 + (h - int(h)) * 2 * math.pi
    return (x + math.cos(a) * r * 0.75, y + math.sin(a) * r * 0.75)


# ---------------------------------------------------------------- 一个晚上：十点到家 → 瘫沙发 → 凌晨一点（场景 1–3）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

scene("小林十点到家", "一个晚上", (1300, 950, 0.85), bars=2)
L(join(door(900, 1100), P((640, 1360), (1560, 1360))), 0, 0.8, sfx="wood_high")
L(stick(1250, 1360, 0.85, "down"), 1, 1.8, BLACK, 10, sfx="wood_low")
L(face(1250, 1360, 0.85, "smile"), 1.8, 2.0)
L(clock(*CLK), 2, 2.7, BLACK, 9, sfx="pop")
C(clock_hands, 2.7, 3.0)
_KEYS.append((J(), 2.7, 22.0))
L(note(1250, 820), 3, 3.7, BLACK, 8, sfx="wood_high")
T("学一小时", 1225, 785, 58, BLUE, k0=4, k1=4.9, sfx="pop")
T("十一点睡", 1225, 865, 58, BLUE, k0=5, k1=6.0, sfx="pop")

scene("先躺一会儿", "一个晚上", (2380, 950, 0.75))
L(sofa(2600, 1360), 0, 0.9, BLACK, 10, sfx="wood_low")
L(slump(2330, 1080), 1, 1.9, BLACK, 10, sfx="wood_high")
L(phone(2400, 900, 64, 104), 2, 2.7, BLUE, 8, sfx="pop")
L(bubble(2470, 640, 440, 140, -1), 4, 4.6, BLACK, 8, sfx="pop")
T("就躺五分钟", 2470, 640, 56, k0=4.6, k1=5.9)
_KEYS += [(J(), 6, 22.0), (J(), 7, 22.5)]
T("22:30", 1800, 790, 60, RED, k0=6, k1=7.25, sfx="shaker")

scene("刷着刷着一点了", "一个晚上", (1860, 950, 0.45))
_KEYS += [(J(), 0, 22.5), (J(), 1.8, 25.0)]
C(spin_tip, 0, 1.8, sfx="shaker")
T("凌晨 1:00", 1800, 905, 96, RED, k0=2, k1=3.5, sfx="pop")
L(cross(1250, 825, 120), 4, 4.7, RED, 14, sfx="rim")
T("？！", 2200, 900, 110, RED, k0=6, k1=6.8, sfx="tom")

# ---------------------------------------------------------------- 书中观点：脑子里住着三个人（场景 4–6）

HX, HY, HR = 1800, 2520, 380
CUT = HY - 220                                  # 头盖骨掀开的裂缝高度
CW = math.sqrt(HR ** 2 - (CUT - HY) ** 2)       # 裂缝处的半宽
FY = 2790                                       # 三兄弟脚底
BX = (1590, 1800, 2010)                         # 老大、老二、宝宝
BS = 0.7


def _zig():
    pts = []
    n = 8
    for i in range(n + 1):
        pts.append((HX - CW + 2 * CW * i / n, CUT + (16 if i % 2 else -16) * (0 < i < n)))
    return pts


def _head_parts():
    a = math.degrees(math.asin((CUT - HY) / HR))           # 右侧交点角（负值）
    low = skia.Path()
    low.addArc(skia.Rect.MakeXYWH(HX - HR, HY - HR, 2 * HR, 2 * HR), a, 180 - 2 * a)
    low.addPath(P(*_zig()))
    neck = join(P((HX - 70, HY + HR - 7), (HX - 70, HY + HR + 60), (HX - 400, HY + HR + 140), (HX - 440, HY + HR + 220)),
                P((HX + 70, HY + HR - 7), (HX + 70, HY + HR + 60), (HX + 400, HY + HR + 140), (HX + 440, HY + HR + 220)))
    cap = skia.Path()
    cap.addArc(skia.Rect.MakeXYWH(HX - HR, HY - HR, 2 * HR, 2 * HR), 180 - a, 180 + 2 * a)
    cap.addPath(P(*_zig()))
    return join(low, neck), cap


HEAD, CAP = _head_parts()


def head_fn(j):
    """场景 4：第 0 拍脑袋弹出来，第 1 拍头盖“咔”地掀开（往上抬、向左歪）。"""

    def fn(c, k, T):
        s = pop_s(clamp01((T - b.t_of(j, 0)) / max(1e-3, b.t_of(j, 0.6) - b.t_of(j, 0))))
        u = ease_out(clamp01((T - b.t_of(j, 1)) / max(1e-3, b.t_of(j, 1.5) - b.t_of(j, 1))))
        u = u * (1 + 0.25 * math.sin(math.pi * u))
        ink(c, moved(HEAD, s=s, ax=HX, ay=HY), BLACK, 11)
        ink(c, moved(CAP, dy=-45 * u, s=s, ax=HX - CW, ay=CUT, rot=-4 * u), BLACK, 11)
        return None

    return fn


BROS = join(grandpa(BX[0], FY, BS), uncle(BX[1], FY, BS))
BABY = baby(BX[2], FY, BS + 0.05)


def bros_fn(c, k, T):
    """三兄弟一起从脚底弹起来。"""
    s = pop_s(k)
    if s <= 0:
        return None
    ink(c, moved(grandpa(BX[0], FY, BS), s=s, ax=BX[0], ay=FY), BLACK, 8)
    ink(c, moved(uncle(BX[1], FY, BS), s=s, ax=BX[1], ay=FY), RED, 8)
    ink(c, moved(BABY, s=s, ax=BX[2], ay=FY), BLUE, 8)
    return None


PLY = (FY - 112, FY - 112, FY - 40)             # 年龄牌挂在胸前

scene("脑子里有三个人", "书中观点 · 三重大脑", (1800, 2540, 0.8), shake=[0], flashes=[0])
C(head_fn(J()), 0, 1.6, sfx="kick")
H(1, "tom")
C(bros_fn, 2, 2.6, sfx="pop")
C(plate_fn(BX[0] + 4, PLY[0], "100", BLACK), 3, 3.6, sfx="tom")
C(plate_fn(BX[1], PLY[1], "55", RED), 4, 4.6, sfx="tom")
C(plate_fn(BX[2], PLY[2], "1", BLUE, w=96, h=60), 5, 5.6, sfx="ding")

scene("有本书讲过", "认知觉醒 · 周岭", (2950, 2540, 0.85))
L(book(2850, 2520, 440, 300), 0, 0.9, BLACK, 10, sfx="wood_low")
T("认知觉醒", 2850, 2290, 76, GREEN, k0=1, k1=2, sfx="pop")
T("周岭 著", 2850, 2770, 56, k0=3, k1=3.9, sfx="pop")
L(helm(3330, 2500, 82), 4, 4.9, GREEN, 8, sfx="wood_high")
T("01", 3330, 2690, 64, GREEN, k0=5, k1=5.8, sfx="ding")

scene("三个脑，三个岁数", "书中观点 · 按年纪比", (1800, 2620, 0.95))
for n, (s, col) in enumerate((("本能脑", BLACK), ("情绪脑", RED), ("理智脑", BLUE))):
    T(s, BX[n], 2475, 50, col, k0=n, k1=n + 0.8, sfx="pop")
L(helm(BX[2], FY - 222, 34), 3, 3.8, GREEN, 6, sfx="wood_high")
T("书中比喻：按年纪算", HX, 2385, 46, k0=5, k1=7.25, sfx="pop")

# ---------------------------------------------------------------- 每个转折，谁抢了主意（场景 7–10）

scene("老大只想躺", "书中观点 · 本能脑", (950, 3950, 0.85))
L(recliner(880, 4250), 0, 0.9, BLACK, 10, sfx="wood_low")
L(lounger(880, 4100), 1, 1.9, BLACK, 10, sfx="wood_high")
C(plate_fn(820, 3905, "100", BLACK, fall=0), 2, 2.5, sfx="pop")
T("Zzz", 470, 3660, 70, BLUE, k0=3, k1=3.8, sfx="pop")
T("能躺不坐", 1060, 3530, 84, RED, k0=5, k1=6, sfx="pop")
T("书中：避难趋易", 950, 4400, 58, GREEN, k0=6, k1=7.75, sfx="ding")

scene("老二只想爽", "书中观点 · 情绪脑", (2650, 3950, 0.85))
L(uncle(2380, 4300, 1.0), 0, 0.9, RED, 10, sfx="wood_high")
L(phone(2530, 4085, 70, 120), 1, 1.6, BLUE, 8, sfx="pop")
C(plate_fn(2380, 4150, "55", RED, fall=0), 1.6, 2.0)
for n, (x, y, r) in enumerate(((2680, 3930, 38), (2840, 3800, 46), (3010, 3660, 54))):
    L(heart(x, y, r), 2 + n, 2.7 + n, RED, 8, sfx="pop" if n < 2 else "ding")
T("马上要开心", 2600, 3530, 76, RED, k0=5, k1=5.9, sfx="pop")
T("书中：急于求成", 2650, 4400, 58, GREEN, k0=6, k1=7.75, sfx="ding")

OY = 100
scene("宝宝说了不算", "书中观点 · 理智脑", (950, 5350, 0.85))
L(baby(760, 5720, 1.3, "reach"), 0, 0.9, BLUE, 10, sfx="wood_high")
L(helm(1150, 5130, 92), 1, 1.9, GREEN, 9, sfx="wood_low")
L(bighand(975, 5060, 25, 0.9), 2, 2.8, BLACK, 9, sfx="tom")
L(bighand(1330, 5060, 150, 0.9), 3, 3.8, RED, 9, sfx="tom")
T("够不着", 520, 5230, 60, BLUE, k0=4, k1=4.8, sfx="pop")
T("出现晚 · 细胞少 · 跑得慢", 950, 5840, 52, k0=5, k1=7.8, sfx="rim")

scene("先刷，再找理由", "书中观点 · 先冲动", (2650, 5350, 0.85))
L(phone(2300, 5420, 200, 330), 0, 0.9, BLUE, 10, sfx="pop")
L(circle(2300, 5070, 62), 1, 1.5, RED, 8, sfx="wood_high")
T("先", 2300, 5070, 72, RED, k0=1.4, k1=2.2)
L(arrow((2430, 5380), (2780, 5380), -0.2, 40), 2, 2.8, RED, 9, sfx="wood_low")
L(note(3020, 5420, 420, 260), 4, 4.7, BLACK, 8, sfx="pop")
T("明天再学", 3010, 5385, 60, k0=5, k1=6, sfx="pop")
T("也一样", 3010, 5470, 60, k0=6, k1=6.8)
L(circle(3020, 5140, 62), 7, 7.4, BLUE, 8, sfx="ding")
T("后", 3020, 5140, 72, BLUE, k0=7.2, k1=8.0)

# ---------------------------------------------------------------- 两个做法（场景 11–12）

OY = 200
scene("手机放客厅", "做法一 · 手机出卧室", (950, 6750, 0.85))
L(join(plug(430, 6830), P((480, 6960), (840, 6960)), P((520, 6960), (520, 7160)), P((800, 6960), (800, 7160))),
  0, 0.9, BLACK, 9, sfx="wood_low")
cable = skia.Path()
cable.moveTo(660, 6955)
cable.cubicTo(640, 7060, 470, 7000, 430, 6875)
L(join(phone(660, 6880, 80, 140), cable), 1, 1.8, BLUE, 8, sfx="pop")
L(bolt(660, 6870, 0.45), 2, 2.6, GREEN, 8, sfx="pop")
L(door(1290, 6910, 260, 500), 4, 4.8, BLACK, 10, sfx="wood_high")
T("卧室", 1270, 6770, 60, k0=5, k1=5.8, sfx="pop")
T("进门先放这儿", 900, 6420, 72, GREEN, k0=6, k1=7.5, sfx="ding")

scene("给宝宝留几秒", "做法二 · 先停几秒", (2650, 6750, 0.85))
HM = (2720, 6640, 96)
L(baby(2420, 7170, 1.3, "reach"), 0, 0.9, BLUE, 10, sfx="wood_high")
L(helm(*HM), 1, 1.9, GREEN, 9, sfx="wood_low")
L(bubble(2340, 6450, 440, 140, -1), 2, 2.6, BLACK, 8, sfx="pop")
T("现在要干啥？", 2340, 6450, 52, k0=2.6, k1=4.0)
L(hourglass(2990, 6960, 0.9), 4, 4.8, BLACK, 9, sfx="wood_high")
T("停几秒", 2990, 7170, 60, k0=5, k1=5.8, sfx="pop")
grip = skia.Path()
grip.addArc(skia.Rect.MakeXYWH(HM[0] - HM[2], HM[1] - HM[2], 2 * HM[2], 2 * HM[2]), 120, 34)
L(grip, 6, 6.5, RED, 22, sfx="ding")
T("握痕 +1", 2870, 6420, 54, GREEN, k0=6.6, k1=7.85)

# ---------------------------------------------------------------- 同一个十点，两条路（场景 13）

OY = 300
scene("十一点关灯", "另一种走法", (1800, 8150, 0.8))
L(join(clock(1340, 8150, 100), hands_at(1340, 8150, 100, 10, 0)), 0, 0.9, BLACK, 9, sfx="wood_low")
T("22:00", 1340, 8320, 56, k0=1, k1=2.25, sfx="pop")
L(join(arrow((1460, 8090), (1760, 7850), 0.15, 36), arrow((1460, 8210), (1760, 8450), -0.15, 36)),
  2, 2.9, BLACK, 9, sfx="wood_high")
L(sofa(2000, 7900, 0.55), 3, 3.8, RED, 9, sfx="wood_low")
T("1:00", 2340, 7800, 72, RED, k0=4, k1=5, sfx="rim")
L(bed(2000, 8640), 5, 5.9, BLUE, 9, sfx="wood_high")
T("23:00", 2340, 8520, 72, GREEN, k0=6, k1=7.25, sfx="ding")
L(moon(2330, 8370, 48), 7, 7.8, BLUE, 8, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FULL = (1800, 4560 - OY, 0.112)                 # 全板：上到挂钟、下到两条路（scene() 会加 OY）
END = (1800, 9520 + OY, 0.8)
scene("评论区聊聊", "评论区见", FULL, bars=4)
J_END = J()
b.move(J_END, 4, END, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
H(4, "wood_high", 0.6)
T("你家哪个脑最常抢主意？", 1800, 9420, 70, RED, k0=6, k1=8.75, sfx="pop")
for n, (lab, col) in enumerate((("100", BLACK), ("55", RED), ("1", BLUE))):
    C(plate_fn(1590 + 210 * n, 9570, lab, col, fall=0), 9 + n * 0.3, 9.4 + n * 0.3, sfx="pop" if n == 0 else None)
T("下一讲：事一多就慌，到底在慌啥？", 1800, 9720, 46, k0=10, k1=14, sfx="wood_high")
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(1, "brain", "三重大脑", "说好十一点睡，怎么又刷到一点？", ACC, b.shots,
                 [f"{BOOK}第一章第一节“大脑：重新认识你自己”（转述）"],
                 "说好十一点睡|怎么又刷到【一点】", SQUARE_SHOT,
                 ["书中观点均为转述（第一章第一节）：大脑分本能脑、情绪脑、理智脑；本能脑、情绪脑出现得早，理智脑出现得晚、"
                  "成熟晚、占的神经细胞少、处理得慢还费能量，所以多数决定由本能和情绪拿主意；人常常先有冲动，再替它找理由；"
                  "人的天性是避难趋易、急于求成。上屏均为转述，不是逐字引文。",
                  "“按年纪比”的 100 / 55 / 1 三块年龄牌据多篇读书笔记一致转述的书中比喻，原书措辞未核实，画面旁注“书中比喻”；"
                  "三兄弟（拄拐老爷爷、戴耳机大叔、抱舵宝宝）、脑袋掀开、两只大手拨开舵均为通俗化示意。",
                  "小林十点到家、便签“学一小时 / 十一点睡”、瘫沙发刷到凌晨一点、“明天再学也一样”均为现实场景示意，"
                  "时间为示意，不是数据；不指向任何具体公司或个人。",
                  "两条做法（进门先把手机放客厅充电；想拿手机时先停几秒，问自己现在要干啥）为据书中思路整理的建议；"
                  "“停几秒”不写成书中给定的秒数。"],
                 tags="#自律 #熬夜")
    return b.attach(ep)
