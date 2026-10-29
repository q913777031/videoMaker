"""07 人是社会动物（白板手绘版）：被同事晾在一边，为什么那么难受？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（2026-10 观众反馈“切换太快，来不及看”后改为慢速讲解版）。
叙事：打工人切身问题开局（中午同事约好去吃饭没叫你 → 下午在工作群里发了句话半天没人接 → 心里堵）→
书中观点（亮书《孤独是可耻的》；祖先靠抱团过日子，落单就危险，人是社会动物；书中讨论的“网络传球”实验：
三个人在屏幕上传球，渐渐不再传给其中一个人；被冷落的痛和身体疼痛在大脑里有重叠，这种疼提醒你回到人群）→
身边的例子（开会挨个夸人唯独跳过你、朋友聚会的照片才知道没叫你、年夜饭亲戚聊得热闹你插不上嘴：都是被晾）→
具体做法（认下难受别硬憋 / 找件事一起干 / 往好处猜，下回你来约）→ 拉远看全板 → 评论区互动。
书中观点为转述（Cacioppo & Patrick, Loneliness: Human Nature and the Need for Social Connection, 2008，
第二部分“从自私的基因到社会动物”，第 11 章“协作是人类进化的王道”等；书中讨论的艾森伯格等 2003 年“网络传球”实验；
中译本《孤独是可耻的》，焦梦津译，中国人民大学出版社 2009）；例子与做法为现实场景示意与据书中思路整理的建议。
"""

import math

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross,
                               desk, face, join, rect, stick, underline)
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, lerp

from .common import BOOK, episode

ACC = "#C0603A"
SQUARE_SHOT = 5

b = Board(size=(3600, 13000))


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None, j=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.5 拍）。"""
    jj = len(b.shots) - 1 if j is None else j
    k1 = k0 + max(0.5, 0.25 * len(s)) if k1 is None else k1
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


def fire(x, y, s=1.0) -> skia.Path:
    """篝火：两根交叉的柴 + 三簇火苗，(x, y) 为地面中点。"""
    logs = join(P((x - 110 * s, y), (x + 110 * s, y - 50 * s)), P((x + 110 * s, y), (x - 110 * s, y - 50 * s)))
    parts = [logs]
    for dx, h in ((-45, 150), (0, 220), (45, 140)):
        f = skia.Path()
        f.moveTo(x + (dx - 35) * s, y - 40 * s)
        f.quadTo(x + (dx - 45) * s, y - (40 + h * 0.6) * s, x + dx * s, y - (40 + h) * s)
        f.quadTo(x + (dx + 45) * s, y - (40 + h * 0.6) * s, x + (dx + 35) * s, y - 40 * s)
        parts.append(f)
    return join(*parts)


def brain(x, y, r=160) -> skia.Path:
    """大脑：起伏的轮廓 + 中线 + 几道褶。"""
    pts = []
    for i in range(48):
        a = i / 48 * 2 * math.pi
        rr = r * (1 + 0.07 * math.sin(a * 9))
        pts.append((x + rr * math.cos(a) * 1.2, y + rr * math.sin(a) * 0.82))
    out = P(*pts, close=True)
    mid = skia.Path()
    mid.moveTo(x, y - r * 0.78)
    mid.quadTo(x - 25, y, x, y + r * 0.78)
    folds = []
    for sx in (-1, 1):
        f = skia.Path()
        f.moveTo(x + sx * r * 0.25, y - r * 0.35)
        f.quadTo(x + sx * r * 0.7, y - r * 0.5, x + sx * r * 0.85, y - r * 0.1)
        folds.append(f)
        g = skia.Path()
        g.moveTo(x + sx * r * 0.3, y + r * 0.35)
        g.quadTo(x + sx * r * 0.6, y + r * 0.1, x + sx * r * 0.9, y + r * 0.3)
        folds.append(g)
    return join(out, mid, *folds)


def box(x, y, w=260, h=150) -> skia.Path:
    return join(rect(x, y, w, h, 8), P((x - w / 2, y - h / 2 + 40), (x + w / 2, y - h / 2 + 40)))


def spot_fn(x, y, r, color=RED, alpha=0.45):
    def fn(c, k, t):
        K.dot(c, x, y, r * k, color, alpha)
        return None

    return fn


def overlap_fn(c1, c2, color=RED, alpha=0.4):
    """两圆重叠部分慢慢填色。c1、c2 为 (x, y, r)。"""

    def fn(c, k, t):
        c.save()
        c.clipPath(circle(*c1), skia.ClipOp.kIntersect, True)
        c.drawPath(circle(*c2), K.paint(color, alpha * k))
        c.restore()
        return None

    return fn


# ---------------------------------------------------------------- 开局：被晾在一边（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍画完，最后 4 拍停住），场景 14 为 4 小节。

def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


scene("午饭没人叫我", "灵魂拷问", (1400, 900, 0.58), bars=2)
L(desk(950, 1100, 360), 0, 0.9, sfx="wood_high")
L(stick(1250, 1300, 0.75), 1, 1.9, sfx="pop")
for n, x in enumerate((1600, 1760, 1920)):
    L(stick(x, 1250, 0.6), 2 + n * 0.3, 2.3 + n * 0.3, sfx="wood_high" if n == 0 else None)
    L(face(x, 1250, 0.6, "smile"), 2.3 + n * 0.3, 2.4 + n * 0.3)
L(bubble(1760, 700, 440, 150, -1), 3, 3.4, BLACK, 8, sfx="pop")
T("走，吃饭去", 1760, 700, 60, k0=3.4)
T("没叫我", 1250, 880, 80, RED, k0=5, k1=5.75, sfx="rim")
L(face(1250, 1300, 0.75, "sad"), 5.75, 6.0, BLUE, 9)

scene("群里没人回，真难受", "灵魂拷问", (2800, 2000, 0.85))
L(phone(2750, 2020, 560, 760), 0, 1.0, BLACK, 9, sfx="wood_high")
T("工作群", 2750, 1730, 52, k0=1, k1=1.75)
L(bubble(2800, 1920, 440, 120, 1), 2, 2.4, BLUE, 8, sfx="pop")
T("方案改好了", 2800, 1920, 56, BLUE, k0=2.4)
T("……", 2750, 2130, 70, k0=4, k1=4.8, sfx="wood_high")
T("0 条回复", 2750, 2240, 60, RED, k0=5, k1=6.0, sfx="pop")
T("怎么这么难受？", 2750, 2500, 80, RED, k0=6, k1=7.75, sfx="rim")

# ---------------------------------------------------------------- 书中观点（场景 3–7）

GROUP = (1730, 1870, 2250, 2390)
scene("书里讲祖先靠抱团", "孤独是可耻的 · 书中观点", (1650, 3950, 0.58))
L(book(1100, 3650, 420, 280), 0, 1.0, sfx="wood_low")
T("孤独是可耻的", 1100, 3410, 76, GREEN, k0=1, k1=2.5, sfx="pop")
T("约翰 · 卡乔波", 1100, 3890, 50, k0=3, k1=4.25, sfx="pop")
L(fire(2060, 3950, 1.0), 4, 5.0, RED, 9, sfx="wood_high")
for n, x in enumerate(GROUP):
    L(stick(x, 4000, 0.55), 5 + n * 0.3, 5.4 + n * 0.3, sfx="pop" if n == 0 else None)
T("祖先", 2060, 3350, 70, k0=7, k1=7.5, sfx="pop")

scene("落单危险，人离不开人", "书中观点 · 社会动物", (2250, 3800, 0.7), shake=[0], flashes=[0])
T("危险！", 2680, 3400, 150, RED, k0=0, k1=0.75, sfx="kick")
L(stick(2720, 4000, 0.55), 1, 1.8, BLUE, 9, sfx="wood_high")
L(face(2720, 4000, 0.55, "sad"), 1.8, 2.0, BLUE, 8)
for n, (ex, ey) in enumerate(((2900, 3660), (2920, 3830))):
    b.custom(J(), 3 + n, 3.4 + n, spot_fn(ex - 22, ey, 12, RED, 1.0), sfx="tom")
    b.custom(J(), 3 + n, 3.4 + n, spot_fn(ex + 22, ey, 12, RED, 1.0))
T("人 = 社会动物", 2250, 4260, 84, RED, k0=5, k1=6.75, sfx="pop")
L(underline(1970, 2530, 4330), 7, 7.8, RED, 8, sfx="ding")

MON = (1050, 5050)
STK = {"A": (1050, 4910), "B": (760, 5300), "C": (1340, 5300)}
SS = 0.55
j_ball = scene("有个传球实验", "书中提到 · 网络传球", (1050, 5000, 0.85))
L(rect(*MON, 1100, 800, 30), 0, 1.0, BLACK, 9, sfx="wood_high")
T("网络传球游戏", 1050, 4570, 66, k0=1, k1=2.5, sfx="pop")
for n, key in enumerate("AB"):
    x, y = STK[key]
    L(stick(x, y, SS), 3 + n * 0.45, 3.45 + n * 0.45, BLACK, 9, sfx="pop" if n == 0 else None)
L(stick(*STK["C"], SS), 4, 4.8, BLUE, 9, sfx="wood_high")
T("你", 1200, 5390, 56, BLUE, k0=5, k1=5.5, sfx="pop")


def _hold(key):
    x, y = STK[key]
    hy = y - 290 * SS
    dx = {"A": 0, "B": 55, "C": -55}[key]
    return x + dx, hy + 130 * SS


# 每一传：(场景, 接住的拍, 从, 到)。接球落在整数拍，配音效。第 9 拍后再也不传给你。
PASSES = [(j_ball, 6, "A", "B"), (j_ball, 7, "B", "C"), (j_ball, 8, "C", "A"), (j_ball, 9, "A", "C"),
          (j_ball, 10, "C", "A"), (j_ball, 11, "A", "B"),
          (j_ball + 1, 0, "B", "A"), (j_ball + 1, 1, "A", "B"), (j_ball + 1, 2, "B", "A"), (j_ball + 1, 3, "A", "B"),
          (j_ball + 1, 4, "B", "A"), (j_ball + 1, 5, "A", "B")]
FLY = 0.32                      # 球在空中的秒数


def ball_fn(c, k, t):
    pos = _hold("A")
    for jj, kk, src, dst in PASSES:
        tc = b.t_of(jj, kk)
        ts = tc - FLY
        if t < ts:
            break
        (x0, y0), (x1, y1) = _hold(src), _hold(dst)
        if t >= tc:
            pos = (x1, y1)
            continue
        f = clamp01((t - ts) / FLY)
        pos = (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f - 150 * 4 * f * (1 - f))
        trail = skia.Path()
        trail.moveTo(x0, y0)
        for i in range(1, 13):
            g = f * i / 12
            trail.lineTo(x0 + (x1 - x0) * g, y0 + (y1 - y0) * g - 150 * 4 * g * (1 - g))
        c.drawPath(trail, K.paint(BLACK, 0.25, 5))
        break
    K.dot(c, pos[0], pos[1], 28, "#E07B24")
    c.drawCircle(pos[0], pos[1], 28, K.paint(BLACK, 1, 5))
    return None


b.custom(j_ball, 5.5, 5.7, ball_fn)
for n, (jj, kk, _, _) in enumerate(PASSES):
    if jj == j_ball:
        b.hit(jj, kk, "pop" if n % 2 == 0 else "wood_high", 0.7)

scene("渐渐不传给你了", "书中提到 · 网络传球", (1050, 5000, 0.85))
for n, (jj, kk, _, _) in enumerate(PASSES):
    if jj == J():
        H(kk, "pop" if n % 2 == 0 else "wood_high", 0.7)
T("没你的份", 1350, 4760, 56, RED, k0=3.2, k1=4.2)
L(face(*STK["C"], SS, "sad"), 6, 6.8, BLUE, 8, sfx="rim")
T("……", 1340, 5040, 60, BLUE, k0=7, k1=7.6)

BR = (2650, 5000)
V1, V2 = (2510, 5470, 200), (2790, 5470, 200)
scene("这种疼在喊你回人群", "书中观点 · 一张图", (2650, 5380, 0.8))
L(brain(*BR, 150), 0, 1.0, BLACK, 9, sfx="wood_high")
L(circle(*V1), 1, 1.8, BLUE, 9, sfx="pop")
T("被冷落", V1[0] - 80, V1[1], 52, BLUE, k0=1.8, k1=2.55)
L(circle(*V2), 3, 3.8, BLACK, 9, sfx="pop")
T("身体疼", V2[0] + 80, V2[1], 52, k0=3.8, k1=4.55)
b.custom(J(), 5, 5.8, overlap_fn(V1, V2), sfx="ding")
T("疼，在喊你回人群", 2650, 5880, 84, RED, k0=5.8, k1=7.3)
T("疼！", 3000, 4870, 70, RED, k0=7.3, k1=7.8)

# ---------------------------------------------------------------- 身边的例子（场景 8–10）

scene("开会唯独跳过你", "例子 · 开会", (880, 7650, 0.85))
L(stick(560, 7930, 0.75, "point", tie=True), 0, 1.0, sfx="wood_high")
for n, x in enumerate((870, 1070, 1270)):
    L(stick(x, 7930, 0.55, hair=n == 1), 1 + n * 0.3, 1.3 + n * 0.3, BLUE if n == 2 else BLACK, 9,
      sfx="pop" if n == 0 else None)
T("好！", 870, 7440, 64, RED, k0=2, k1=2.5, sfx="pop")
T("好！", 1070, 7440, 64, RED, k0=3, k1=3.5, sfx="pop")
L(arrow((900, 7360), (1300, 7360), -0.15, 36), 4, 4.8, RED, 8, sfx="wood_high")
L(face(1270, 7930, 0.55, "sad"), 5, 5.8, BLUE, 8, sfx="pop")
T("跳过", 1270, 7440, 64, BLUE, k0=6, k1=6.5, sfx="rim")

scene("聚会照片里没有我", "例子 · 聚会", (2720, 7650, 0.85))
L(phone(2500, 7620, 460, 640), 0, 1.0, BLACK, 9, sfx="wood_high")
L(rect(2500, 7560, 360, 300, 10), 1, 1.4, BLACK, 7, sfx="pop")
for n, x in enumerate((2400, 2500, 2600)):
    L(stick(x, 7680, 0.35, "up"), 1.4 + n * 0.3, 1.7 + n * 0.3, BLACK, 7)
T("周末聚会", 2500, 7360, 52, k0=3, k1=4.0, sfx="pop")
L(stick(3000, 7930, 0.6, "hold"), 4, 4.8, BLUE, 9, sfx="wood_high")
L(face(3000, 7930, 0.6, "sad"), 4.8, 5.0, BLUE, 8)
T("没叫我", 3000, 7400, 64, RED, k0=6, k1=6.75, sfx="rim")
T("？", 3170, 7540, 90, RED, k0=7, k1=7.5, sfx="pop")

scene("插不上嘴也是被晾", "例子 · 家庭", (880, 9050, 0.85), shake=[6])
L(join(P((520, 9175), (1060, 9175)), P((560, 9175), (560, 9280)), P((1020, 9175), (1020, 9280))), 0, 0.9, BLACK, 10,
  sfx="wood_high")
for n, x in enumerate((600, 780, 960)):
    L(stick(x, 9230, 0.5), 1 + n * 0.3, 1.3 + n * 0.3, BLACK, 9, sfx="pop" if n == 0 else None)
T("哈哈哈", 780, 8900, 60, k0=2, k1=2.75, sfx="pop")
L(stick(1300, 9230, 0.5), 3, 3.8, BLUE, 9, sfx="wood_high")
L(face(1300, 9230, 0.5, "flat"), 3.8, 4.0, BLUE, 8)
L(bubble(1340, 8900, 220, 110, -1), 4, 4.4, BLUE, 7, sfx="pop")
T("我…", 1340, 8900, 56, BLUE, k0=4.4, k1=4.9)
L(cross(1340, 8900, 60), 5, 5.5, RED, 10, sfx="rim")
T("都是被晾", 880, 9500, 100, RED, k0=6, k1=7.0, sfx="kick")

# ---------------------------------------------------------------- 具体做法（场景 11–13）

SOL = [(950, 10550), (2650, 10550), (2650, 11950)]
scene("先认下，别硬憋", "第一步 · 认下来", (950, 10600, 0.85))
L(rect(*SOL[0], 1200, 820, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("① 难受很正常", 950, 10250, 76, BLUE, k0=1, k1=2.5, sfx="pop")
L(stick(650, 10880, 0.65), 3, 3.8, sfx="pop")
L(face(650, 10880, 0.65, "sad"), 3.8, 4.0)
L(bubble(1080, 10450, 380, 120, -1), 4, 4.4, BLACK, 8, sfx="wood_high")
T("有点难受", 1080, 10450, 56, k0=4.4, k1=5.4)
T("跟朋友说一句", 1060, 10750, 56, GREEN, k0=6, k1=7.5, sfx="pop")
L(check(1260, 10870, 36), 7.5, 7.9, GREEN, 9)

scene("找件事一起干", "第二步 · 一起干", (2650, 10600, 0.85))
L(rect(*SOL[1], 1200, 820, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("② 找件事一起干", 2650, 10250, 72, BLUE, k0=1, k1=2.75, sfx="pop")
L(box(2650, 10460, 300, 140), 3, 3.8, BLACK, 9, sfx="wood_high")
L(stick(2520, 10730, 0.6, "up"), 4, 4.45, BLACK, 9, sfx="pop")
L(stick(2780, 10730, 0.6, "up"), 4.45, 4.9, BLUE, 9)
for n, w in enumerate(("周末打球", "一起拼饭")):
    T(w, 2420 + n * 460, 10850, 52, k0=5 + n, k1=6 + n, sfx="pop")
L(face(2520, 10730, 0.6, "smile"), 7, 7.4, BLACK, 8)
L(face(2780, 10730, 0.6, "smile"), 7.4, 7.8, BLUE, 8)

scene("往好处猜，下回你约", "第三步 · 往好处想", (2650, 12000, 0.85))
L(rect(*SOL[2], 1200, 820, 40), 0, 0.9, GREEN, 8, sfx="wood_high")
T("③ 往好处猜", 2650, 11650, 76, BLUE, k0=1, k1=2.25, sfx="pop")
L(stick(2350, 12280, 0.65), 3, 3.8, BLUE, 9, sfx="wood_high")
L(face(2350, 12280, 0.65, "smile"), 3.8, 4.0, BLUE, 8)
L(bubble(2820, 11870, 480, 130, -1), 4, 4.4, BLACK, 8, sfx="pop")
T("可能忘叫我了", 2820, 11870, 54, k0=4.4, k1=5.9)
T("明天一起吃？", 2760, 12100, 56, RED, k0=6, k1=7.5, sfx="pop")
L(check(3100, 12090, 40), 7.5, 7.9, GREEN, 10)

# ---------------------------------------------------------------- 收尾（场景 14，4 小节）：拉远看全板 → 推到评论区

FULL = (1800, 6600, 0.16)
scene("被晾过吗？评论区聊", "评论区见", (1500, 12700, 0.8), bars=4)
J_END = J()
H(0, "cymbal", 0.5)
H(2, "wood_high", 0.6)
H(4, "ding")
T("你被晾过吗？", 1500, 12620, 80, RED, k0=6, k1=7.5, sfx="pop")
T("下一讲：越孤单，为什么越爱跟猫说话？", 1500, 12780, 50, k0=9, k1=13.0, sfx="wood_high")
L(P((1050, 12830), (1950, 12830)), 13, 13.8, BLACK, 6)
b.hit(J_END, 16, "kick", 0.55, "原曲最后一击")


def _ease_view(v0, v1, f):
    return lerp(v0[0], v1[0], f), lerp(v0[1], v1[1], f), math.exp(lerp(math.log(v0[2]), math.log(v1[2]), f))


if not getattr(wb.camera, "_gudu07", False):
    _base_camera = wb.camera

    def _camera(board, T):
        """本讲片尾场景：第 0–2 拍拉远看全板，停到第 4 拍，第 4–6 拍推到评论区（其余镜头照引擎原样）。"""
        if board is b and board.ep is not None and board.ep.shot_at(T) == J_END:
            t0, t2, t4, t6 = (b.t_of(J_END, k) for k in (0, 2, 4, 6))
            prev, cur = b.views[J_END - 1], b.views[J_END]
            if T < t4:
                cx, cy, z = _ease_view(prev, FULL, ease_in_out(clamp01((T - t0) / (t2 - t0))))
            else:
                cx, cy, z = _ease_view(FULL, cur, ease_in_out(clamp01((T - t4) / (t6 - t4))))
            return cx, cy, z, 0.0, 0.0
        return _base_camera(board, T)

    _camera._gudu07 = True
    wb.camera = _camera


def build():
    ep = episode(7, "social", "人是社会动物", "被同事晾在一边，为什么那么难受？", ACC, b.shots,
                 [f"{BOOK}第二部分“从自私的基因到社会动物”、第 11 章“协作是人类进化的王道”（转述）",
                  "书中讨论的网络传球实验：Eisenberger, Lieberman & Williams (2003), Science",
                  "中译本：焦梦津译，中国人民大学出版社 2009"],
                 "被同事晾着|为什么【这么疼】", 6,
                 ["书中观点均为转述：人类祖先靠合作和群居活下来、繁荣起来，离群是危险的，人是社会动物（第二部分“从自私的基因到"
                  "社会动物”，第 7–11 章）；书中讨论了艾森伯格等人 2003 年的“网络传球”实验——受试者在电脑上和另外两名“玩家”"
                  "传球，渐渐不再收到球，被排斥时的大脑活动与身体疼痛相关的区域有重叠；被冷落的痛像信号，提醒人修复与他人的联系。"
                  "出处：John T. Cacioppo & William Patrick, Loneliness: Human Nature and the Need for Social Connection "
                  "(W. W. Norton, 2008)，中译本《孤独是可耻的》（焦梦津译，中国人民大学出版社 2009）。上屏均为转述，不是逐字引文。",
                  "午饭没被叫上、工作群没人回、开会被跳过、聚会照片、年夜饭插不上话均为现实场景示意，不指向任何具体"
                  "公司或个人；“0 条回复”为示意；传球画面、大脑与重叠图为对实验与结论的通俗化示意，不是实验数据。",
                  "三步做法（认下难受别硬憋、找件事一起干、往好处猜并主动约）为据书中思路（含第 14 章 EASE："
                  "先迈一小步、往好处预期别人）整理的建议。"],
                 tags="#职场 #人际关系")
    return b.attach(ep)
