"""《越想赶紧解决，为什么越容易走错？》渲染器。

用法：
    python3 -m doubt.render out/doubt            # 成片 + 封面 + 时间轴核验
    python3 -m doubt.render out/doubt --frame 3  # 只出第 3 秒的单帧 PNG（调试）

规格：1080×1920、30 fps、恰好 1800 帧（60.000 秒）、H.264 yuv420p、不含音频轨道。
全部画面为时间 t 的纯函数，不使用随机数（噪声由固定相位的正弦叠加），可多进程逐帧并行渲染。
地图与路线是视觉比喻，不代表大脑结构，也不是研究数据。
"""

import math
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import skia

W, H, FPS, TOTAL = 1080, 1920, 30, 60.0
NFRAMES = int(round(TOTAL * FPS))

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"

BG = (0x07, 0x07, 0x08)
GOLD = (0xD6, 0xB6, 0x7E)        # 香槟金
GOLD_HI = (0xF2, 0xDC, 0xAE)
WHITE = (0xEE, 0xE9, 0xE0)       # 灰白
GRAY = (0x8C, 0x88, 0x80)
INK = (0x05, 0x05, 0x05)         # 剪影

# ---------------------------------------------------------------- 文案（最终主文案，【】为金色强调）

CARDS = [
    ["越想【赶紧解决】，", "为什么越容易【走错】？"],
    ["一群人迷路了。", "又累，又急，", "营地还没找到。"],
    ["他们最想要的，", "是【赶紧选一条路】。"],
    ["决定做了，", "大家【松了一口气】。"],
    ["可走了很久，", "才发现：【方向错了】。"],
    ["【急着结束不安】，", "不等于找到了答案。"],
    ["先把直觉，", "当成一个", "【需要验证的假设】。"],
    ["问自己：", "什么迹象说明", "【我可能错了】？"],
    ["【停下来核对】，", "有时也是在前进。"],
    ["你现在需要答案，", "还是需要【先看清问题】？"],
]
CARD_LEN = 6.0
FADE_IN, FADE_OUT = 0.35, 0.40
TAG = "根据播客故事改编 · 情境演绎"
TAG_SPAN = (6.0, 54.0)
SOURCE = "来源：Hidden Brain / Bobby Parmar"
SOURCE_IN = 54.3

TEXT_SIZE, TEXT_GAP, TEXT_CX, TEXT_CY = 80, 112, 500, 450
TAG_Y, SOURCE_Y = 700, 700
SAFE = (90, 230, 930, 1560)      # 主文字与关键人物须落在此框内（避开顶部状态区、右侧按钮列、底部标题区）


def card_window(i: int):
    """第 i 张卡的 (入场开始, 完全显示, 开始出场, 消失)。首卡首帧即完整显示，末卡停到片尾。"""
    s = i * CARD_LEN
    shown = s if i == 0 else s + FADE_IN
    out = TOTAL if i == len(CARDS) - 1 else s + CARD_LEN - FADE_OUT
    return s, shown, out, min(TOTAL, s + CARD_LEN)


# ---------------------------------------------------------------- 缓动与关键帧

def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def lerp(a, b, x):
    if isinstance(a, tuple):
        return tuple(lerp(p, q, x) for p, q in zip(a, b))
    return a + (b - a) * x


def kf(t, keys, fn=ease):
    """分段关键帧插值：keys 为按时间排序的 (时刻, 值)，区间内用 fn 缓动，两端保持。"""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            return lerp(v0, v1, fn((t - t0) / (t1 - t0)) if t1 > t0 else 1.0)
    return keys[-1][1]


def win(t, a, b, fi=0.3, fo=0.3):
    """[a, b] 区间的淡入淡出透明度。"""
    if t < a or t > b:
        return 0.0
    return min(clamp01((t - a) / fi) if fi else 1.0, clamp01((b - t) / fo) if fo else 1.0)


def col(rgb, a=1.0):
    return skia.ColorSetARGB(int(255 * clamp01(a)), *rgb)


def paint(rgb, a=1.0, stroke=None, cap=True, blur=0.0, dash=None):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
    return p


@lru_cache(maxsize=None)
def font(name: str, size: float):
    return skia.Font(skia.Typeface.MakeFromFile(str(FONT_DIR / name)), size)


SERIF = "NotoSerifCJKsc-Bold.otf"
SANS = "NotoSansCJKsc-Medium.otf"


def poly_path(pts):
    p = skia.Path()
    if len(pts):
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
    return p


# ---------------------------------------------------------------- 时间积分量（行走位移与步态相位）

def _speed(t):
    """世界横向滚动速度（像素/秒，正值=向右走）。"""
    return kf(t, [(15.6, 0), (16.6, 95), (18.5, 120), (24, 120), (26.5, 70), (27.6, 0),
                  (36.2, 0), (36.9, -110), (38.6, -110), (39.3, 0),
                  (48.3, 0), (48.9, -85), (50.6, -85), (51.2, 0)])


def _comp_walk(t):
    """S2 同伴入场时的行走强度。"""
    return kf(t, [(6.0, 0), (6.4, 1), (8.6, 0.8), (10.0, 0)])


_TS = np.arange(0, TOTAL + 1, 1 / 120)
_V = np.array([_speed(x) for x in _TS])
_SCROLL = np.concatenate([[0], np.cumsum((_V[1:] + _V[:-1]) / 2 / 120)])
_GAIT = np.concatenate([[0], np.cumsum(np.abs(_V[1:] + _V[:-1]) / 2 / 120)]) * 0.075
_CW = np.array([_comp_walk(x) for x in _TS])
_CGAIT = np.concatenate([[0], np.cumsum((_CW[1:] + _CW[:-1]) / 2 / 120)]) * 7.5


def scroll(t):
    return float(np.interp(t, _TS, _SCROLL))


def gait(t):
    return float(np.interp(t, _TS, _GAIT))


def walk_amp(t):
    return clamp01(abs(_speed(t)) / 90)


# ---------------------------------------------------------------- 地图（地图坐标：峰顶在右上，营地在湖边，下山方向在左下）

FORK = (500, 560)
LAKE = (600, 175)
CAMP = (705, 215)
VANTAGE = (455, 500)

A_PTS = [FORK, (545, 470), (600, 375), (650, 290), (690, 232)]
B_PTS = [FORK, (420, 625), (300, 665), (160, 720), (20, 815), (-120, 940), (-270, 1070)]
RIDGE_PTS = [(150, 640), (220, 560), (300, 505), (370, 470), (420, 455)]
RIVER_PTS = [(548, 185), (440, 235), (320, 320), (215, 450), (130, 610), (60, 800), (-30, 980), (-140, 1150)]
TRY1 = [VANTAGE, (400, 440), (330, 400)]
TRY2 = [VANTAGE, (470, 400), (470, 300), (455, 245)]
SAFE_PTS = [VANTAGE, (545, 445), (610, 350), (655, 285), (692, 232)]


def catmull(pts, n=40):
    pts = np.array(pts, float)
    P = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for s in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-2])
    return np.array(out)


class Route:
    def __init__(self, pts):
        self.p = catmull(pts)
        d = np.hypot(*np.diff(self.p, axis=0).T)
        self.cum = np.concatenate([[0], np.cumsum(d)]) / d.sum()

    def at(self, f):
        f = clamp01(f)
        return (float(np.interp(f, self.cum, self.p[:, 0])), float(np.interp(f, self.cum, self.p[:, 1])))

    def part(self, a, b):
        a, b = clamp01(a), clamp01(b)
        if b <= a:
            return []
        mid = [tuple(q) for q, c in zip(self.p, self.cum) if a < c < b]
        return [self.at(a)] + mid + [self.at(b)]


RA, RB, RIDGE, RIVER = Route(A_PTS), Route(B_PTS), Route(RIDGE_PTS), Route(RIVER_PTS)
RT1, RT2, RSAFE = Route(TRY1), Route(TRY2), Route(SAFE_PTS)


def _ring(cx, cy, r, k, ex=1.15, n=180):
    th = np.linspace(0, 2 * np.pi, n)
    rr = r * (1 + 0.07 * np.sin(3 * th + 1.3 * k) + 0.045 * np.sin(5 * th + 2.1 * k + 0.7)
              + 0.025 * np.sin(9 * th + 0.4 * k))
    return list(zip(cx + ex * rr * np.cos(th), cy + rr * np.sin(th)))


PEAK = (720, 40)
CONTOURS = [_ring(*PEAK, 80 + 85 * k, k) for k in range(16)]
FINE = [_ring(*PEAK, 122 + 85 * k, k + 0.5) for k in range(15)]
KNOLL = [_ring(*VANTAGE, 22 + 20 * k, k + 3, ex=1.3, n=90) for k in range(3)]


def map_state(t):
    """地图在 t 时刻的全部可视参数。"""
    s = {}
    s["center"] = kf(t, [(12, (450, 620)), (13, (480, 470)), (18, (480, 470)), (24, (420, 570)),
                         (26.5, (170, 610)), (36.4, (170, 610)), (38.6, (495, 535)), (42.2, (495, 535)),
                         (43.2, (470, 420)), (48.2, (470, 420)), (49.6, (430, 470)), (54, (430, 470)),
                         (55, (470, 520))])
    s["U"] = kf(t, [(12, 1100), (13, 1200), (18, 1200), (24, 1350), (26.5, 2050), (36.4, 2050),
                    (38.6, 640), (42.2, 640), (43.2, 1100), (48.2, 1100), (49.6, 1420), (54, 1420),
                    (55, 1150)])
    s["U"] *= 1 + 0.03 * math.sin(2 * math.pi * t / 9.0)      # 缓慢呼吸式推拉，避免长时间静帧
    s["clarity"] = kf(t, [(0, 0.12), (12.5, 0.12), (13.5, 0.22), (36.6, 0.22), (39, 0.85), (48.5, 0.85),
                          (50, 1.0)])
    s["fuzzy"] = kf(t, [(0, 1.0), (36.6, 1.0), (39, 0.0)])          # A/B 两条候选路线的模糊程度
    s["fuzzy_a"] = 1.0 - kf(t, [(15.5, 0), (16.5, 0.6), (36.6, 0.6), (37.6, 0)])   # 决定后 A 更淡
    s["lit"] = kf(t, [(18.0, 0), (18.8, 0.45), (27.2, 1.0), (36.0, 1.0), (37.6, 0)])
    s["mk"] = kf(t, [(18.3, 0), (27.5, 1.0), (36.0, 1.0), (37.6, 0)])
    s["arrow"] = win(t, 14.7, 48.0, 0.25, 0.5)
    s["arrow_dashed"] = kf(t, [(37.4, 0), (38.0, 1)])
    s["gap"] = win(t, 27.8, 36.0, 0.5, 0.3)
    s["label_route"] = win(t, 30.3, 36.0, 0.4, 0.3)
    s["magnifier"] = win(t, 38.4, 42.6, 0.4, 0.4)
    s["ridge"] = kf(t, [(42.6, 0), (43.6, 1)])
    s["river"] = kf(t, [(43.6, 0), (44.6, 1)])
    s["badge"] = win(t, 44.9, 48.3, 0.3, 0.3)
    s["vantage"] = kf(t, [(48.4, 0), (50.6, 1)])
    s["try1"] = kf(t, [(50.0, 0), (50.7, 1)])
    s["try2"] = kf(t, [(50.9, 0), (51.6, 1)])
    s["safe"] = kf(t, [(51.9, 0), (53.4, 1)])
    s["final"] = kf(t, [(54, 0), (55, 1)])                          # 结尾：路线全部回到"待选"状态
    return s


def draw_map(cv, rect, t, alpha=1.0):
    """把地图画进屏幕矩形 rect=(l,t,r,b)。"""
    st = map_state(t)
    l, tp, r, b = rect
    w = r - l
    sc = w / st["U"]
    cx, cy = st["center"]
    cv.save()
    rr = skia.RRect.MakeRectXY(skia.Rect(l, tp, r, b), 18, 18)
    cv.drawRRect(rr, paint((0x0F, 0x0E, 0x0C), alpha))
    cv.clipRRect(rr, True)
    cv.translate((l + r) / 2, (tp + b) / 2)
    cv.scale(sc, sc)
    cv.translate(-cx, -cy)
    px = 1 / sc                                   # 一个屏幕像素对应的地图单位
    c = st["clarity"]

    # 等高线：模糊期只剩粗略轮廓，放大后显露细节
    blur_c = (1 - c) * 6 * px
    for ring in CONTOURS:
        cv.drawPath(poly_path(ring), paint(GOLD, alpha * (0.10 + 0.30 * c), 1.6 * px, blur=blur_c))
    if c > 0.3:
        for ring in FINE:
            cv.drawPath(poly_path(ring), paint(GOLD, alpha * 0.16 * (c - 0.3) / 0.7, 1.0 * px))
    knoll_a = max(c - 0.3, 0) / 0.7
    for ring in KNOLL:
        cv.drawPath(poly_path(ring), paint(WHITE, alpha * 0.22 * knoll_a, 1.2 * px))

    # 湖与营地（营地始终可见，作为"目标"）
    lake = skia.Rect(LAKE[0] - 70, LAKE[1] - 34, LAKE[0] + 70, LAKE[1] + 34)
    cv.drawOval(lake, paint(WHITE, alpha * (0.10 + 0.10 * c)))
    cv.drawOval(lake, paint(WHITE, alpha * (0.25 + 0.3 * c), 1.5 * px))
    pulse = 0.5 + 0.5 * math.sin(t * 3.2)
    cv.drawCircle(*CAMP, 30 * px * (1 + 0.25 * pulse), paint(GOLD, alpha * 0.25, blur=10 * px))
    tent = skia.Path()
    tent.moveTo(CAMP[0] - 15 * px, CAMP[1] + 9 * px)
    tent.lineTo(CAMP[0], CAMP[1] - 15 * px)
    tent.lineTo(CAMP[0] + 15 * px, CAMP[1] + 9 * px)
    tent.close()
    cv.drawPath(tent, paint(GOLD_HI, alpha))
    _map_label(cv, "营地", (CAMP[0] + 22 * px, CAMP[1] + 9 * px), px, alpha * 0.9, WHITE)

    # 山脊与河流：与"下山就能到营地"的预期不一致的地形信息
    fin = st["final"]
    if st["ridge"] > 0:
        pts = RIDGE.part(0, st["ridge"])
        cv.drawPath(poly_path(pts), paint(WHITE, alpha * 0.85, 4 * px))
        n = int(st["ridge"] * 9)
        for i in range(1, n + 1):
            x, y = RIDGE.at(i / 10)
            tick = skia.Path()
            tick.moveTo(x - 9 * px, y + 4 * px)
            tick.lineTo(x, y - 12 * px)
            tick.lineTo(x + 9 * px, y + 4 * px)
            cv.drawPath(tick, paint(WHITE, alpha * 0.7, 2 * px))
        _map_label(cv, "山脊", (RIDGE_PTS[0][0] - 10 * px, RIDGE_PTS[0][1] + 34 * px), px,
                   alpha * clamp01(st["ridge"] * 2 - 1), WHITE)
    if st["river"] > 0:
        pts = RIVER.part(0, st["river"])
        cv.drawPath(poly_path(pts), paint(WHITE, alpha * 0.55, 5 * px))
        # 水流方向：从湖流向下游（离营地越来越远）
        for i in range(8):
            f = ((i + t * 0.35) / 8) % 1.0
            if f > st["river"]:
                continue
            (x, y), (x2, y2) = RIVER.at(f), RIVER.at(f + 0.01)
            a = math.atan2(y2 - y, x2 - x)
            ch = skia.Path()
            ch.moveTo(x - 10 * px * math.cos(a - 0.6), y - 10 * px * math.sin(a - 0.6))
            ch.lineTo(x, y)
            ch.lineTo(x - 10 * px * math.cos(a + 0.6), y - 10 * px * math.sin(a + 0.6))
            cv.drawPath(ch, paint(WHITE, alpha * 0.8, 2.2 * px))
        _map_label(cv, "河流", (RIVER.at(0.45)[0] - 90 * px, RIVER.at(0.45)[1]), px,
                   alpha * clamp01(st["river"] * 2 - 1), WHITE)

    # 两条候选路线：决定前模糊，结尾变清晰但不涂金（尚未选择）
    fz = st["fuzzy"]
    for route, extra in ((RA, st["fuzzy_a"]), (RB, 1.0)):
        a_ = alpha * (0.40 + 0.20 * (1 - fz)) * extra
        cv.drawPath(poly_path(route.part(0, 1)),
                    paint(WHITE, a_, 3 * px, blur=fz * 4 * px, dash=(14 * px, 12 * px)))

    # 金色路线：迅速亮起、一路延伸，随后退回岔路口
    if st["lit"] > 0:
        pts = RB.part(0, st["lit"])
        cv.drawPath(poly_path(pts), paint(GOLD, alpha * 0.45, 16 * px, blur=8 * px))
        cv.drawPath(poly_path(pts), paint(GOLD_HI, alpha, 5 * px))
        if st["label_route"] > 0:
            x, y = RB.at(0.55)
            _map_label(cv, "确定的路线", (x + 26 * px, y + 10 * px), px, alpha * st["label_route"], GOLD_HI)

    # 起点箭头：决定时是实线，回到岔路口后变成虚线（直觉降级为待验证的假设）
    if st["arrow"] > 0:
        _arrow(cv, RB, px, alpha * st["arrow"], st["arrow_dashed"])

    # 标记与营地之间的距离
    mk = RB.at(st["mk"])
    if st["gap"] > 0:
        cv.drawPath(poly_path([mk, CAMP]), paint(GRAY, alpha * st["gap"] * 0.9, 2.5 * px, dash=(10 * px, 10 * px)))

    # 回到高处、尝试不同选项、找到更安全的路径
    if st["try1"] > 0:
        _try_route(cv, RT1, st["try1"], px, alpha * (1 - fin))
    if st["try2"] > 0:
        _try_route(cv, RT2, st["try2"], px, alpha * (1 - fin))
    if st["safe"] > 0:
        pts = RSAFE.part(0, st["safe"])
        cv.drawPath(poly_path(pts), paint(GOLD, alpha * 0.4 * (1 - fin), 14 * px, blur=7 * px))
        cv.drawPath(poly_path(pts), paint(GOLD_HI, alpha * (1 - 0.65 * fin), 4.5 * px,
                                          dash=(16 * px, 8 * px) if fin > 0.5 else None))

    # 人物标记（小队）
    if t < 48.4:
        pos = mk
    else:
        pos = lerp(FORK, VANTAGE, st["vantage"])
        pos = lerp(pos, FORK, fin)
    for k, (dx, dy) in enumerate(((0, 0), (-16, 10), (-6, 22))):
        cv.drawCircle(pos[0] + dx * px, pos[1] + dy * px, (9 if k == 0 else 6) * px,
                      paint(GOLD_HI if k == 0 else WHITE, alpha * (1 if k == 0 else 0.6)))
    cv.drawCircle(*pos, 22 * px * (1 + 0.15 * pulse), paint(GOLD, alpha * 0.18, blur=8 * px))
    cv.restore()

    # 放大镜（屏幕空间，套在岔路口上）
    if st["magnifier"] > 0:
        sx = (l + r) / 2 + (FORK[0] - cx) * sc
        sy = (tp + b) / 2 + (FORK[1] - cy) * sc
        a = st["magnifier"]
        rad = 125 * (0.85 + 0.15 * a)
        cv.drawCircle(sx, sy, rad, paint(GOLD_HI, alpha * a * 0.9, 4))
        ang = math.radians(40)
        cv.drawLine(sx + rad * math.cos(ang), sy + rad * math.sin(ang),
                    sx + (rad + 70) * math.cos(ang), sy + (rad + 70) * math.sin(ang), paint(GOLD_HI, alpha * a * 0.9, 10))

    # "发现偏差"提示（屏幕空间）
    if st["badge"] > 0:
        a = st["badge"] * alpha
        bx, by = l + 70, tp + 40
        f = font(SANS, 34)
        tw = f.measureText("发现偏差")
        rrb = skia.RRect.MakeRectXY(skia.Rect(bx, by, bx + tw + 64, by + 58), 29, 29)
        cv.drawRRect(rrb, paint((0x1A, 0x17, 0x11), a))
        cv.drawRRect(rrb, paint(GOLD_HI, a, 2.5))
        cv.drawCircle(bx + 26, by + 29, 7, paint(GOLD_HI, a))
        cv.drawString("发现偏差", bx + 44, by + 41, f, paint(GOLD_HI, a))

    cv.drawRRect(rr, paint(GOLD, alpha * 0.55, 2))


def _map_label(cv, text, pos, px, a, rgb):
    if a <= 0:
        return
    cv.save()
    cv.translate(*pos)
    cv.scale(px, px)
    cv.drawString(text, 0, 0, font(SANS, 28), paint(rgb, a))
    cv.restore()


def _arrow(cv, route, px, a, dashed):
    pts = route.part(0, 0.13)
    p = paint(GOLD_HI, a, 7 * px, dash=(14 * px, 11 * px) if dashed > 0.5 else None)
    cv.drawPath(poly_path(pts), p)
    (x, y), (x0, y0) = pts[-1], pts[-3]
    ang = math.atan2(y - y0, x - x0)
    head = skia.Path()
    head.moveTo(x + 26 * px * math.cos(ang), y + 26 * px * math.sin(ang))
    head.lineTo(x + 18 * px * math.cos(ang + 2.4), y + 18 * px * math.sin(ang + 2.4))
    head.lineTo(x + 18 * px * math.cos(ang - 2.4), y + 18 * px * math.sin(ang - 2.4))
    head.close()
    if dashed > 0.5:
        cv.drawPath(head, paint(GOLD_HI, a, 3 * px))
    else:
        cv.drawPath(head, paint(GOLD_HI, a))


def _try_route(cv, route, f, px, a):
    """试探性的选项：虚线走到尽头被打叉（遇到山脊或河流）。"""
    cv.drawPath(poly_path(route.part(0, f)), paint(WHITE, a * 0.75, 3.5 * px, dash=(12 * px, 9 * px)))
    if f >= 1:
        x, y = route.at(1)
        s = 13 * px
        cv.drawLine(x - s, y - s, x + s, y + s, paint(WHITE, a * 0.9, 4 * px))
        cv.drawLine(x - s, y + s, x + s, y - s, paint(WHITE, a * 0.9, 4 * px))


# ---------------------------------------------------------------- 登山者剪影（全片同一造型）

def climber(cv, x, gy, h, facing, phase, amp, point=0.0, point_ang=0.0, hold=0.0, look=0.0,
            alpha=1.0, rim=GOLD, breath=0.0):
    """原创登山者剪影：鸭舌帽、背包与卷垫、登山杖。gy 为脚底 y，h 为身高像素。

    point：指路姿态权重；point_ang：手臂与水平线夹角（弧度，正值向上）；
    hold：低头看手中地图的权重；look：抬头/低头（正值抬头）。
    """
    if alpha <= 0:
        return
    cv.save()
    cv.translate(x, gy)
    cv.scale(facing * h, h)
    bob = -0.012 * amp * abs(math.cos(phase)) - 0.006 * (1 - amp) * math.sin(breath)
    hip = (0.0, -0.47 + bob)
    sh = (0.035, -0.775 + bob)

    def limb(p0, a0, l0, a1, l1):
        k = (p0[0] + l0 * math.sin(a0), p0[1] + l0 * math.cos(a0))
        e = (k[0] + l1 * math.sin(a1), k[1] + l1 * math.cos(a1))
        return [p0, k, e]

    legs = []
    for i in (0, 1):
        s = math.sin(phase + i * math.pi)
        th = amp * 0.42 * s + (0.05 if i else -0.05) * (1 - amp)
        knee_back = amp * 0.45 * max(0.0, math.cos(phase + i * math.pi))
        legs.append(limb(hip, th, 0.235, th - knee_back, 0.245))

    arms = []
    for i in (0, 1):
        s = math.sin(phase + i * math.pi)
        ua = -amp * 0.38 * s
        arms.append(limb(sh, ua, 0.2, ua + 0.45, 0.18))
    # 前臂姿态：指路 / 拿地图
    hand_pt = (sh[0] + 0.40 * math.cos(point_ang), sh[1] - 0.40 * math.sin(point_ang))
    point_arm = [sh, ((sh[0] + hand_pt[0]) / 2, (sh[1] + hand_pt[1]) / 2), hand_pt]
    hold_arm = [sh, (0.12, -0.60), (0.24, -0.66)]
    front = [tuple(lerp(lerp(arms[0][j], point_arm[j], point), hold_arm[j], hold)) for j in range(3)]
    back = [tuple(lerp(arms[1][j], [sh, (0.10, -0.60), (0.22, -0.64)][j], hold)) for j in range(3)]

    head_c = (0.065 + 0.015 * hold, -0.905 + bob + 0.02 * hold - 0.0 * look)
    tilt = -0.35 * hold + 0.25 * look

    def strokes(p, extra):
        for lg in legs:
            cv.drawPath(poly_path(lg), _wp(p, 0.078 + extra))
        cv.drawPath(poly_path(back), _wp(p, 0.06 + extra))
        cv.drawPath(poly_path([hip, sh]), _wp(p, 0.16 + extra))
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-0.175 - extra / 2, -0.81 + bob - extra / 2,
                                                     -0.035 + extra / 2, -0.50 + bob + extra / 2), 0.035, 0.035), _fp(p))
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-0.19 - extra / 2, -0.875 + bob - extra / 2,
                                                     -0.03 + extra / 2, -0.81 + bob + extra / 2), 0.03, 0.03), _fp(p))
        cv.drawCircle(*head_c, 0.072 + extra / 2, _fp(p))
        cv.save()
        cv.translate(*head_c)
        cv.rotate(math.degrees(-tilt))
        cv.drawPath(poly_path([(-0.06, -0.045), (0.14, -0.035)]), _wp(p, 0.03 + extra))
        cv.restore()
        cv.drawPath(poly_path(front), _wp(p, 0.06 + extra))
        # 登山杖（拿地图/指路时收起）
        stick = 1 - max(point, hold)
        if stick > 0.05:
            hx, hy = front[2]
            cv.drawPath(poly_path([(hx, hy), (hx + 0.13, 0.0)]), _wp(p, 0.018 + extra))
        if hold > 0.05:
            cv.drawRect(skia.Rect(0.17, -0.72, 0.31 + extra, -0.60 + extra), _fp(p))

    rim_p = skia.Paint(AntiAlias=True, Color=col(rim, alpha * 0.9))
    ink_p = skia.Paint(AntiAlias=True, Color=col(INK, alpha))
    strokes(rim_p, 5.0 / h)
    strokes(ink_p, 0.0)
    if hold > 0.05:   # 手中地图的金色细节
        cv.drawRect(skia.Rect(0.18, -0.71, 0.30, -0.61), paint(GOLD, alpha * hold * 0.8))
        cv.drawLine(0.20, -0.66, 0.28, -0.69, paint(GOLD_HI, alpha * hold, 0.008))
    cv.restore()


def _wp(p, w):
    q = skia.Paint(p)
    q.setStyle(skia.Paint.kStroke_Style)
    q.setStrokeWidth(w)
    q.setStrokeCap(skia.Paint.kRound_Cap)
    q.setStrokeJoin(skia.Paint.kRound_Join)
    return q


def _fp(p):
    q = skia.Paint(p)
    q.setStyle(skia.Paint.kFill_Style)
    return q


# ---------------------------------------------------------------- 山野场景

def _ridge_y(xs, seed, amp, base):
    return base - amp * (0.55 + 0.25 * np.sin(xs * 0.006 + seed) + 0.15 * np.sin(xs * 0.017 + 2 * seed)
                         + 0.07 * np.sin(xs * 0.041 + 3 * seed))


def draw_world(cv, t, comp):
    """comp=0：开场构图（全舞台、岔路口与地图牌）；comp=1：地图下方的窄条山野。"""
    top = lerp(760, 1262, comp)
    bot = 1580
    horizon = lerp(1235, 1395, comp)
    sc = scroll(t)
    up = kf(t, [(48.4, 0), (50.8, 1), (54, 1), (55, 0)])        # S9 登上高处：远山下沉、天际变亮
    horizon += 40 * up
    dusk = kf(t, [(0, 1.0), (24, 0.85), (30, 0.6), (42, 0.55), (50, 0.85), (55, 0.75)])

    cv.save()
    cv.clipRect(skia.Rect(0, top, W, bot))
    sky = skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, top), skia.Point(0, horizon)],
        [col(BG), col((int(0x2A * dusk + 6), int(0x25 * dusk + 6), int(0x1D * dusk + 6)))]))
    cv.drawRect(skia.Rect(0, top, W, horizon + 2), sky)
    glow = 0.25 * win(t, 18.4, 26.0, 1.0, 2.0) + 0.3 * up
    if glow > 0:
        cv.drawCircle(W * 0.5, horizon, 520, paint(GOLD, glow * 0.35, blur=160))

    xs = np.linspace(-20, W + 20, 120)
    hz = horizon - top
    if up > 0:      # 登高后才看得到的远处山脉
        far2 = _ridge_y(xs + sc * 0.05, 7.0, hz * 0.5, horizon)
        cv.drawPath(_fill_under(xs, far2, bot), paint((0x23, 0x20, 0x1B), up))
    for seed, amp, par, rgb in ((1.0, 0.62, 0.15, (0x1B, 0x19, 0x16)), (2.6, 0.38, 0.4, (0x12, 0x11, 0x10))):
        ys = _ridge_y(xs + sc * par, seed, hz * amp * (1 - 0.35 * up), horizon)
        cv.drawPath(_fill_under(xs, ys, bot), paint(rgb))

    tilt = math.tan(math.radians(kf(t, [(15.5, 0), (17.5, 4.0), (30, 4.0), (36, 0), (48.3, 0),
                                        (49.3, 6.0), (51, 6.0), (52, 0)])))
    gy0 = horizon + lerp(205, 72, comp) - 40 * up

    def gy(x):
        return gy0 + tilt * (x - 540)

    ground = skia.Path()
    ground.moveTo(-10, gy(-10))
    ground.lineTo(W + 10, gy(W + 10))
    ground.lineTo(W + 10, bot)
    ground.lineTo(-10, bot)
    ground.close()
    cv.drawPath(ground, paint((0x0A, 0x0A, 0x09)))
    cv.drawLine(-10, gy(-10), W + 10, gy(W + 10), paint(GOLD, 0.25, 2))
    # 地面碎石随行走滚动（提供速度感）
    for i in range(14):
        x = ((i * 97 - sc) % (W + 160)) - 80
        y = gy(x) + 14 + (i * 37 % 50) * (1 - comp * 0.6)
        cv.drawOval(skia.Rect(x - 9, y - 3, x + 9, y + 3), paint((0x2B, 0x28, 0x22), 0.9))

    # 开场构图：岔路、地图牌、右侧不断变暗的山路
    oc = 1 - comp
    if oc > 0:
        road = paint((0x2A, 0x26, 0x20), oc)
        p = skia.Path()
        p.moveTo(470, bot)
        p.lineTo(560, gy(560) + 8)
        p.lineTo(250, gy(250) - 2)
        p.lineTo(300, gy(300) - 2)
        p.lineTo(610, gy(610) + 8)
        p.lineTo(950, gy(950) - 6)
        p.lineTo(1040, gy(1040) - 6)
        p.lineTo(690, bot)
        p.close()
        cv.drawPath(p, road)
        dark = kf(t, [(0, 0.15), (12, 0.78)]) if t < 54 else kf(t, [(54, 0.78), (56, 0.55)])
        shade = skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [skia.Point(640, 0), skia.Point(1000, 0)], [col(BG, 0), col(BG, dark * oc)]))
        cv.drawRect(skia.Rect(640, top, W, bot), shade)
        cv.drawLine(285, gy(285), 285, 1160, paint((0x2E, 0x2A, 0x23), oc, 12))
    cv.restore()
    return gy


def _fill_under(xs, ys, bot):
    p = skia.Path()
    p.moveTo(float(xs[0]), bot)
    for x, y in zip(xs, ys):
        p.lineTo(float(x), float(y))
    p.lineTo(float(xs[-1]), bot)
    p.close()
    return p


# ---------------------------------------------------------------- 人物调度

def draw_people(cv, t, comp, gy):
    fig_h = lerp(300, 150, comp)
    g = gait(t)
    amp = walk_amp(t)
    v = _speed(t)

    # 领队（主角）
    lx = lerp(600, 590, comp)
    if t < 9.2:
        facing = 1
    elif t < 14.0:
        facing = -1
    elif t < 31.0:
        facing = 1
    elif t < 54.6:
        facing = -1 if (t < 39.5 or t > 48.0) else 1
        if 48.0 <= t < 51.4:
            facing = -1
        elif 51.4 <= t < 54.6:
            facing = 1
    else:
        facing = -1
    # 开场：手臂在两条路之间迟疑地抬起，指向变暗的山路
    p_open = kf(t, [(0, 0.45), (1.2, 0.35), (2.6, 0.55), (3.6, 0.45), (5.0, 0.75), (6.2, 0.75), (7.2, 0)])
    ang_open = math.radians(-8 + 6 * math.sin(t * 1.7))
    # 决定：指向下山方向
    p_dec = win(t, 14.2, 16.4, 0.4, 0.5)
    ang_dec = math.radians(-24)
    point = max(p_open, p_dec)
    ang = ang_open if p_open >= p_dec else ang_dec
    # 拿地图核对（S7 后段与 S8），S10 再次停下看地图
    hold = max(win(t, 39.4, 48.3, 0.5, 0.4), win(t, 51.8, 54.2, 0.4, 0.3))
    # S8：低头看图 ↔ 抬头看地形，来回核对
    look = 0.0
    if 42.0 < t < 48.3:
        look = 0.5 + 0.5 * math.sin((t - 42.0) * 2.0)
        hold *= 1 - 0.55 * look
    # S10：面向地图牌，一手微抬（在看，而不是出发）
    p_end = kf(t, [(55.2, 0), (56.4, 0.55)])
    if t > 55:
        point, ang = p_end, math.radians(18)
        hold = 0.0
        look = kf(t, [(55.2, 0), (56.4, 0.35)])
    walking_amp = amp if 15.6 < t < 52 else 0.0

    # 同伴：S2 从左侧走进，停在地图牌前；结尾淡出
    comp_a = kf(t, [(6.0, 0), (6.6, 0.85), (54.2, 0.85), (55.0, 0)])
    c_amp = _comp_walk(t) if t < 12 else walking_amp
    c_phase = float(np.interp(t, _TS, _CGAIT)) if t < 12 else g + 1.3
    cxs = [kf(t, [(6.0, -120), (10.0, 405)]), kf(t, [(6.0, -230), (10.0, 300)])]
    cxs = [lerp(x, x2, comp) for x, x2 in zip(cxs, (465, 365))]
    if t < 9.6:
        c_face = 1
    elif t < 15.3:
        c_face = -1
    else:
        c_face = 1 if (v >= 0 and not (31.0 < t < 48.0) and not (48.0 <= t < 51.4)) else -1
        if 39.5 <= t < 48.0:
            c_face = 1
    for i, x in enumerate(cxs):
        climber(cv, x, gy(x), fig_h * (0.95 - 0.04 * i), c_face, c_phase + i * 1.9, c_amp,
                alpha=comp_a, rim=GRAY, breath=t * 2.1 + i)
    climber(cv, lx, gy(lx), fig_h, facing, g, walking_amp, point=point, point_ang=ang,
            hold=hold, look=look, breath=t * 1.9)


# ---------------------------------------------------------------- 字幕

def draw_text(cv, t):
    for i, lines in enumerate(CARDS):
        s, shown, out, end = card_window(i)
        if not (s <= t < end or (i == len(CARDS) - 1 and t >= s)):
            continue
        a_in = 1.0 if i == 0 else ease_out((t - s) / FADE_IN)
        a_out = 1.0 if t < out else 1 - ease((t - out) / FADE_OUT)
        a = min(a_in, a_out)
        dy = (1 - a_in) * 22
        n = len(lines)
        f = font(SERIF, TEXT_SIZE)
        for k, line in enumerate(lines):
            cy = TEXT_CY + (k - (n - 1) / 2) * TEXT_GAP + dy
            segs, hl = [], False
            for part in line.replace("】", "【").split("【"):
                if part:
                    segs.append((part, hl))
                hl = not hl
            total = sum(f.measureText(p) for p, _ in segs)
            x = TEXT_CX - total / 2
            for p, is_hl in segs:
                cv.drawString(p, x, cy + TEXT_SIZE * 0.36, f, paint(GOLD_HI if is_hl else WHITE, a))
                x += f.measureText(p)

    ta = win(t, TAG_SPAN[0], TAG_SPAN[1], 0.3, 0.3)
    if ta > 0:
        f = font(SANS, 32)
        cv.drawLine(TEXT_CX - f.measureText(TAG) / 2 - 46, TAG_Y - 11, TEXT_CX - f.measureText(TAG) / 2 - 16,
                    TAG_Y - 11, paint(GOLD, ta, 2))
        cv.drawString(TAG, TEXT_CX - f.measureText(TAG) / 2, TAG_Y, f, paint(GRAY, ta))
    if t >= SOURCE_IN:
        a = ease_out((t - SOURCE_IN) / FADE_IN)
        f = font(SANS, 38)
        cv.drawString(SOURCE, TEXT_CX - f.measureText(SOURCE) / 2, SOURCE_Y, f, paint((0xCF, 0xC8, 0xBA), a))


# ---------------------------------------------------------------- 合成

BOARD = (95, 850, 475, 1165)
PANEL = (90, 770, 990, 1250)


def comp_at(t):
    return kf(t, [(12.0, 0), (13.0, 1), (54.0, 1), (55.0, 0)])


def render(t):
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cv.clear(col(BG))
    comp = comp_at(t)
    gy = draw_world(cv, t, comp)
    draw_map(cv, lerp(BOARD, PANEL, comp), t)
    draw_people(cv, t, comp, gy)
    # 舞台上下边缘渐隐到黑
    for y0, y1, a0, a1 in ((730, 830, 1, 0), (1500, 1590, 0, 1)):
        cv.drawRect(skia.Rect(0, y0, W, y1), skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [skia.Point(0, y0), skia.Point(0, y1)], [col(BG, a0), col(BG, a1)])))
    cv.drawRect(skia.Rect(0, 1590, W, H), paint(BG))
    draw_text(cv, t)
    return surf.makeImageSnapshot()


def frame_bytes(i):
    img = render(i / FPS)
    return img.toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()


def check_timeline():
    """阅读预算与时间轴核验：卡片连续、无重叠，稳定阅读时长满足 max(2, N/4.5) 与分镜下限。"""
    minimum = [5.0, 4.5, 4.0, 4.0, 4.5, 4.5, 5.0, 5.0, 4.5, 4.5]
    rows, ok = [], True
    for i, lines in enumerate(CARDS):
        s, shown, out, end = card_window(i)
        text = "".join(lines).replace("【", "").replace("】", "")
        n = sum(1 for ch in text if "一" <= ch <= "鿿")
        need = max(2.0, n / 4.5, minimum[i])
        stable = out - shown
        good = stable >= need and abs(end - (i + 1) * CARD_LEN) < 1e-9
        ok &= good
        rows.append(f"{s:5.1f}–{end:4.1f}s  N={n:2d}  稳定 {shown:5.2f}–{out:5.2f}s = {stable:.2f}s  "
                    f"需 ≥{need:.2f}s  {'通过' if good else '不足'}  {text}")
    src = TOTAL - (SOURCE_IN + FADE_IN)
    rows.append(f"来源字 稳定 {SOURCE_IN + FADE_IN:.2f}–60.00s = {src:.2f}s  需 ≥4.00s  {'通过' if src >= 4 else '不足'}")
    ok &= src >= 4
    ok &= card_window(0)[1] <= 0.3 and card_window(0)[2] >= 5.0
    # 文字宽度安全区检查
    f = font(SERIF, TEXT_SIZE)
    for lines in CARDS:
        n = len(lines)
        for k, line in enumerate(lines):
            w = f.measureText(line.replace("【", "").replace("】", ""))
            l, r = TEXT_CX - w / 2, TEXT_CX + w / 2
            cy = TEXT_CY + (k - (n - 1) / 2) * TEXT_GAP
            if l < SAFE[0] or r > SAFE[2] or cy - TEXT_SIZE / 2 < SAFE[1]:
                rows.append(f"越界：{line} ({l:.0f}–{r:.0f})")
                ok = False
    rows.append("全部通过" if ok else "存在问题")
    return ok, "\n".join(rows)


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "out/doubt")
    out.mkdir(parents=True, exist_ok=True)
    if "--frame" in sys.argv:
        t = float(sys.argv[sys.argv.index("--frame") + 1])
        render(t).save(str(out / f"frame_{t:05.2f}.png"), skia.kPNG)
        return
    ok, report = check_timeline()
    (out / "timeline_check.txt").write_text(report + "\n", encoding="utf-8")
    print(report)
    if not ok:
        sys.exit("时间轴核验未通过")
    render(3.0).save(str(out / "cover.png"), skia.kPNG)
    mp4 = out / "越想赶紧解决越容易走错.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", str(mp4)]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, buf in enumerate(pool.imap(frame_bytes, range(NFRAMES), chunksize=4)):
            enc.stdin.write(buf)
            if i % 150 == 0:
                print(f"帧 {i}/{NFRAMES}", flush=True)
    enc.stdin.close()
    if enc.wait() != 0:
        sys.exit("ffmpeg 编码失败")
    print(mp4)


if __name__ == "__main__":
    main()
