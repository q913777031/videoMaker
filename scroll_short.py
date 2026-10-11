"""《为什么总想再刷一条？》黑金风格无声科普竖屏短视频。

完全无声：无旁白、无音乐、无音效，成片不含音频流；屏幕文字即完整叙事。
叙事线：开场钩子 → 示意循环 → 三节点历史时间轴 → 推荐反馈流程 → 有终点/持续加载对照
→ 给循环加暂停节点 → 收束 → 参考资料。
文案与分镜见 docs/scroll_short/，每条事实的出处见其中的 sources.md。

用法：
  python3 scroll_short.py [输出路径]          渲染成片（默认 out/scroll_short.mp4）与两张封面
  python3 scroll_short.py --still 秒 [...]    只渲染指定时刻的单帧 PNG，用于检查画面
依赖资源：python3 fetch_assets.py（只需其中的思源黑体）
"""

import functools
import math
import subprocess
import sys
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import skia

ROOT = Path(__file__).resolve().parent
FONT_DIR = ROOT / "assets" / "fonts"
W, H, FPS = 1080, 1920, 30
TOTAL = 96.0

BG = "#08090B"
GOLD = "#D8B46A"
LIGHT = "#E8DCC0"
DARK = "#75613C"
GOLD_HI = "#ECD08E"  # 金色字的轻微渐变上沿
GOLD_LO = "#C29A52"  # 金色字的轻微渐变下沿

# 安全区：避开右侧操作栏（约 190px）与底部说明区（约 340px）
CX = 480
LEFT, RIGHT = 72, 888
BOTTOM = 1580

WEIGHTS = {"r": "Regular", "m": "Medium", "b": "Bold", "k": "Black"}


# ---------------------------------------------------------------- 缓动与时间

def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def lerp(a: float, b: float, x: float) -> float:
    return a + (b - a) * x


def ease_out(x: float) -> float:
    return 1 - (1 - clamp01(x)) ** 3


def ease_in_out(x: float) -> float:
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def prog(t: float, start: float, dur: float = 0.4) -> float:
    return clamp01((t - start) / dur) if dur > 0 else float(t >= start)


def life(t: float, t0: float, t1: float | None = None, fin: float = 0.4, fout: float = 0.35) -> float:
    """元素透明度：t0 起淡入，t1 起淡出；只做单次渐变，不做明暗闪烁。"""
    a = ease_out(prog(t, t0, fin))
    if t1 is not None:
        a *= 1 - ease_in_out(prog(t, t1, fout))
    return a


# ---------------------------------------------------------------- 颜色与字体

@functools.lru_cache(maxsize=None)
def rgb(c: str) -> tuple:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def col(c: str, a: float = 1.0) -> int:
    r, g, b = rgb(c)
    return skia.Color(r, g, b, int(round(255 * clamp01(a))))


def mix(c1: str, c2: str, x: float) -> str:
    a, b = rgb(c1), rgb(c2)
    return "#%02X%02X%02X" % tuple(int(p + (q - p) * clamp01(x)) for p, q in zip(a, b))


@functools.lru_cache(maxsize=None)
def typeface(weight: str) -> skia.Typeface:
    path = FONT_DIR / f"NotoSansCJKsc-{WEIGHTS[weight]}.otf"
    tf = skia.Typeface.MakeFromFile(str(path))
    if tf is None:
        raise FileNotFoundError(f"font not found: {path} (run fetch_assets.py)")
    return tf


@functools.lru_cache(maxsize=2048)
def font(weight: str, size: float) -> skia.Font:
    f = skia.Font(typeface(weight), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def text_w(s: str, size: float, weight: str = "b") -> float:
    return font(weight, size).measureText(s.replace("【", "").replace("】", ""))


def paint(color: str, a: float = 1.0, stroke: float = 0.0, cap_round: bool = True) -> skia.Paint:
    p = skia.Paint(AntiAlias=True, Color=col(color, a))
    if stroke > 0:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap_round:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def text(c: skia.Canvas, s: str, x: float, y: float, size: float, weight: str = "b", color: str = LIGHT,
         a: float = 1.0, align: str = "center", hi: str = GOLD, gold: bool = False) -> float:
    """绘制单行文字，y 为视觉中线；【】包住的片段用金色 hi。gold=True 时整行用轻微金色渐变。
    返回行宽。"""
    if a <= 0 or not s:
        return 0.0
    segs, buf, on = [], "", False
    for ch in s:
        if ch in "【】":
            if buf:
                segs.append((buf, on))
            buf, on = "", ch == "【"
        else:
            buf += ch
    if buf:
        segs.append((buf, on))
    f = font(weight, size)
    w = sum(f.measureText(t) for t, _ in segs)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    base = y + size * 0.36
    for t, on in segs:
        if gold:
            p = skia.Paint(AntiAlias=True)
            p.setShader(skia.GradientShader.MakeLinear(
                [(0, y - size * 0.5), (0, y + size * 0.45)], [col(GOLD_HI, a), col(GOLD_LO, a)]))
        else:
            p = paint(hi if on else color, a)
        c.drawTextBlob(skia.TextBlob.MakeFromString(t, f), x0, base, p)
        x0 += f.measureText(t)
    return w


def lines(c: skia.Canvas, rows: list[str], x: float, y: float, size: float, lh: float, t: float, t0: float,
          t1: float | None = None, weight: str = "b", color: str = LIGHT, align: str = "center",
          stagger: float = 0.12, rise: float = 18, gold: bool = False):
    """多行文字逐行上浮淡入；t1 起整体淡出。"""
    for i, row in enumerate(rows):
        s = t0 + i * stagger
        a = life(t, s, t1)
        dy = (1 - ease_out(prog(t, s, 0.45))) * rise
        text(c, row, x, y + i * lh + dy, size, weight, color, a, align, gold=gold)


def punch(c: skia.Canvas, rows: list[str], x: float, y: float, size: float, lh: float, t: float, t0: float,
          t1: float | None = None, gold_rows: tuple = ()):
    """钩子大字：突然出现并从 1.08 倍收到原大（0.2 秒），停留后淡出；无闪烁。"""
    a = life(t, t0, t1, fin=0.08, fout=0.3)
    if a <= 0:
        return
    s = lerp(1.08, 1.0, ease_out(prog(t, t0, 0.22)))
    c.save()
    cy = y + (len(rows) - 1) * lh / 2
    c.translate(x, cy)
    c.scale(s, s)
    for i, row in enumerate(rows):
        text(c, row, 0, y + i * lh - cy, size, "k", LIGHT, a, gold=i in gold_rows)
    c.restore()


# ---------------------------------------------------------------- 图形元件

def rrect(c: skia.Canvas, cx: float, cy: float, w: float, h: float, r: float, fill: str | None = None,
          fa: float = 1.0, stroke: str | None = None, sa: float = 1.0, sw: float = 2.0):
    rect = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h), r, r)
    if fill and fa > 0:
        c.drawRRect(rect, paint(fill, fa))
    if stroke and sa > 0:
        c.drawRRect(rect, paint(stroke, sa, sw))


def arrow_head(c: skia.Canvas, x: float, y: float, ang: float, size: float, color: str, a: float):
    p = skia.Path()
    p.moveTo(x + math.cos(ang) * size, y + math.sin(ang) * size)
    p.lineTo(x + math.cos(ang + 2.5) * size * 0.8, y + math.sin(ang + 2.5) * size * 0.8)
    p.lineTo(x + math.cos(ang - 2.5) * size * 0.8, y + math.sin(ang - 2.5) * size * 0.8)
    p.close()
    c.drawPath(p, paint(color, a))


def polyline(c: skia.Canvas, pts: list[tuple], frac: float, color: str, a: float, width: float = 3,
             head: float = 0.0, dash: tuple | None = None):
    """按长度比例 frac 描出折线（路径描边动画）；head>0 时在笔尖画箭头。"""
    if frac <= 0 or a <= 0 or len(pts) < 2:
        return
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total, goal = sum(seg), sum(seg) * clamp01(frac)
    path, acc = skia.Path(), 0.0
    path.moveTo(*pts[0])
    end, ang = pts[0], 0.0
    for i, L in enumerate(seg):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        ang = math.atan2(y1 - y0, x1 - x0)
        if acc + L >= goal:
            k = (goal - acc) / L if L else 1
            end = (lerp(x0, x1, k), lerp(y0, y1, k))
            path.lineTo(*end)
            break
        path.lineTo(x1, y1)
        end, acc = (x1, y1), acc + L
    p = paint(color, a, width)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
    c.drawPath(path, p)
    if head > 0:
        arrow_head(c, end[0], end[1], ang, head, color, a)


def ellipse_pts(cx, cy, rx, ry, a0, a1, n=48) -> list[tuple]:
    return [(cx + rx * math.cos(math.radians(lerp(a0, a1, i / n))),
             cy + ry * math.sin(math.radians(lerp(a0, a1, i / n)))) for i in range(n + 1)]


def chapter(c: skia.Canvas, t: float, t0: float, t1: float, num: str, label: str):
    """左上角章节标：编号 + 名称 + 细金线。"""
    a = life(t, t0, t1)
    if a <= 0:
        return
    text(c, num, LEFT, 196, 34, "b", GOLD, a, "left")
    text(c, label, LEFT + 70, 196, 34, "m", DARK, a, "left")
    k = ease_out(prog(t, t0, 0.8))
    c.drawLine(LEFT, 236, LEFT + 220 * k, 236, paint(DARK, a, 2))


def tag(c: skia.Canvas, s: str, x: float, y: float, a: float, filled: bool = False, size: float = 34,
        align: str = "center"):
    """小标签：filled=True 实心金底（产品/技术），False 细线框（研究/示意）。"""
    if a <= 0:
        return
    w = text_w(s, size, "m") + size * 1.1
    cx = x if align == "center" else x + w / 2
    if filled:
        rrect(c, cx, y, w, size * 1.6, size * 0.8, fill=GOLD, fa=a)
        text(c, s, cx, y, size, "m", BG, a)
    else:
        rrect(c, cx, y, w, size * 1.6, size * 0.8, stroke=GOLD, sa=a * 0.9, sw=2)
        text(c, s, cx, y, size, "m", GOLD, a)


def source(c: skia.Canvas, rows: list[str], y: float, a: float):
    """画面底部的依据注释（小字，暗金）。"""
    for i, r in enumerate(rows):
        text(c, r, LEFT, y + i * 44, 30, "r", mix(DARK, LIGHT, 0.35), a, "left")


def pause_icon(c: skia.Canvas, x: float, y: float, r: float, a: float, filled: bool = True):
    if filled:
        c.drawCircle(x, y, r, paint(GOLD, a))
        fg = BG
    else:
        c.drawCircle(x, y, r, paint(GOLD, a, 3))
        fg = GOLD
    bw, bh = r * 0.22, r * 0.86
    for dx in (-r * 0.26, r * 0.26):
        rrect(c, x + dx, y, bw, bh, bw * 0.3, fill=fg, fa=a)


def shape(c: skia.Canvas, kind: str, x: float, y: float, s: float, color: str, a: float, stroke: float = 0):
    """内容卡片上的抽象主题符号：circle / tri / square。"""
    p = paint(color, a, stroke) if stroke else paint(color, a)
    if kind == "circle":
        c.drawCircle(x, y, s * 0.5, p)
    elif kind == "tri":
        path = skia.Path()
        path.moveTo(x, y - s * 0.52)
        path.lineTo(x + s * 0.55, y + s * 0.42)
        path.lineTo(x - s * 0.55, y + s * 0.42)
        path.close()
        c.drawPath(path, p)
    else:
        c.drawRect(skia.Rect.MakeXYWH(x - s * 0.42, y - s * 0.42, s * 0.84, s * 0.84), p)


def content_card(c: skia.Canvas, x: float, y: float, w: float, h: float, a: float, kind: str = "circle",
                 lit: float = 0.0, dim: float = 0.0):
    """抽象内容卡片：圆角框 + 主题符号 + 两条占位文字线。lit 提亮边框，dim 压暗。"""
    if a <= 0:
        return
    k = 1 - 0.65 * dim
    rrect(c, x, y, w, h, min(w, h) * 0.1, fill="#121317", fa=a * k,
          stroke=mix(DARK, GOLD, lit), sa=a * k, sw=2 + 2 * lit)
    shape(c, kind, x, y - h * 0.12, min(w, h) * 0.34, mix(DARK, GOLD, 0.5 + 0.5 * lit), a * k)
    for i, lw in enumerate((0.62, 0.42)):
        yy = y + h * (0.24 + 0.12 * i)
        c.drawLine(x - w * lw / 2, yy, x + w * lw / 2, yy, paint(DARK, a * k * 0.8, max(3, h * 0.025)))


# ---------------------------------------------------------------- 循环图（场景 2、3、7、9 共用）

LOOP_LABELS = ["看到内容", "产生反应", "继续滑动", "新内容出现"]
LOOP_ANG = [-90, 0, 90, 180]


def loop_geom(cx, cy, rx, ry):
    return [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))) for a in LOOP_ANG]


def draw_loop(c: skia.Canvas, cx: float, cy: float, rx: float, ry: float, scale: float, a: float,
              edge_frac: list[float], edge_lit: list[float], node_a: list[float], node_lit: list[float],
              pause: float = 0.0, flow_t: float | None = None, label_size: float = 50):
    """四节点行为循环图（示意）。edge_* / node_* 为每条边/每个节点的描边进度与点亮程度；
    pause>0 时在"继续滑动→新内容出现"之间插入暂停节点并截断该边；flow_t 给出时画沿环流动的光点。"""
    if a <= 0:
        return
    nodes = loop_geom(cx, cy, rx, ry)
    trims = [(26, 26), (28, 22), (26, 26), (22, 28)]
    for i in range(4):
        a0, a1 = LOOP_ANG[i] + trims[i][0], LOOP_ANG[i] + 90 - trims[i][1]
        lit = edge_lit[i]
        color = mix(DARK, GOLD, lit)
        if i == 2 and pause > 0:
            mid = 135
            gap = 13 * ease_out(pause)
            polyline(c, ellipse_pts(cx, cy, rx, ry, a0, mid - gap), edge_frac[i], color, a, 3 + 2 * lit)
            if edge_frac[i] >= 1:
                polyline(c, ellipse_pts(cx, cy, rx, ry, mid + gap, a1), 1, color, a, 3 + 2 * lit,
                         head=14 * scale)
            continue
        polyline(c, ellipse_pts(cx, cy, rx, ry, a0, a1), edge_frac[i], color, a, 3 + 2 * lit,
                 head=14 * scale)
    if flow_t is not None:
        for k in range(3):
            ang = math.radians(-90 + ((flow_t * 70 + k * 120) % 360))
            if pause > 0.5 and 120 < math.degrees(ang) % 360 < 150:
                continue
            c.drawCircle(cx + rx * math.cos(ang), cy + ry * math.sin(ang), 7 * scale, paint(GOLD, a * 0.9))
    pw, ph = 296 * scale, 100 * scale
    for i, (x, y) in enumerate(nodes):
        na = a * node_a[i]
        if na <= 0:
            continue
        lit = node_lit[i]
        rrect(c, x, y, pw, ph, ph / 2, fill=mix("#101114", "#2A2418", lit), fa=na,
              stroke=mix(DARK, GOLD, lit), sa=na, sw=2 + 1.5 * lit)
        text(c, LOOP_LABELS[i], x, y, label_size * scale, "b", mix(mix(DARK, LIGHT, 0.6), GOLD, lit), na)
    if pause > 0:
        px = cx + rx * math.cos(math.radians(135))
        py = cy + ry * math.sin(math.radians(135))
        s = ease_out(prog(pause, 0, 1)) * (1 + 0.15 * math.sin(math.pi * clamp01(pause)))
        c.drawCircle(px, py, 54 * scale * s, paint(BG, a))
        pause_icon(c, px, py, 44 * scale * s, a)


# ---------------------------------------------------------------- 场景

def s1_open(c: skia.Canvas, t: float):
    """0–6 秒：开场钩子。卡片滑走、下一张立刻进入，最后停在问号上。"""
    if t >= 6.2:
        return
    # 三张卡片依次上滑
    swaps = [1.7, 3.5]
    for i in range(3):
        enter = 0.0 if i == 0 else swaps[i - 1]
        leave = swaps[i] if i < 2 else 4.7
        if t < enter - 0.01:
            continue
        pin = ease_out(prog(t, enter, 0.45)) if i else 1.0
        pout = ease_in_out(prog(t, leave, 0.45))
        y = 1130 + (1 - pin) * 900 - pout * 1000
        a = (life(t, 0.0, None, 0.3) if i == 0 else 1.0) * (1 - clamp01(pout * 2.2))
        if i == 2:
            y = 1130 + (1 - pin) * 900
            a *= 1 - ease_in_out(prog(t, 4.7, 0.35))
        content_card(c, CX, y, 560, 720, a, ["circle", "tri", "square"][i], lit=0.3)
    # 上滑手势提示
    ga = life(t, 0.6, 4.5) * 0.85
    if ga > 0:
        gy = 1560 - 70 * ((t * 0.9) % 1)
        polyline(c, [(CX, 1600), (CX, gy - 40)], 1, DARK, ga, 3, head=12)
    punch(c, ["再刷一条。"], CX, 400, 120, 0, t, 0.25, 2.2)
    punch(c, ["为什么", "总有下一条？"], CX, 340, 108, 140, t, 2.35, 4.75, gold_rows=(1,))
    # 停在问号上
    qa = life(t, 4.85, 5.95, fin=0.1, fout=0.25)
    if qa > 0:
        s = lerp(1.12, 1.0, ease_out(prog(t, 4.85, 0.25)))
        c.save()
        c.translate(CX, 960)
        c.scale(s, s)
        text(c, "？", 0, 0, 420, "k", GOLD, qa, gold=True)
        c.restore()


def loop_state(t: float):
    """场景 2 中循环图随时间的构建状态。"""
    steps = [8.0, 10.8, 14.3, 16.8]
    edge_frac = [ease_in_out(prog(t, s, 0.8)) for s in steps]
    edge_lit = [life(t, s, steps[i + 1] if i < 3 else 20.0, 0.3, 0.5) for i, s in enumerate(steps)]
    node_a = [life(t, 6.4 + 0.25 * i, None, 0.4) for i in range(4)]
    node_lit = [0.0] * 4
    for i, s in enumerate(steps):
        on = life(t, s, steps[i + 1] if i < 3 else 20.0, 0.3, 0.5)
        node_lit[i] = max(node_lit[i], on)
        node_lit[(i + 1) % 4] = max(node_lit[(i + 1) % 4], life(t, s + 0.6, steps[i + 1] if i < 3 else 20.0, 0.3, 0.5))
    return edge_frac, edge_lit, node_a, node_lit


def s2_loop(c: skia.Canvas, t: float):
    """6–20 秒：示意循环图，逐边点亮，每次只解释一个关系。"""
    if not 5.9 <= t < 20.4:
        return
    chapter(c, t, 6.0, 19.8, "01", "一个示意循环")
    a = life(t, 6.0, 19.8, 0.4, 0.5)
    ef, el, na, nl = loop_state(t)
    draw_loop(c, CX, 1060, 255, 330, 1.0, a, ef, el, na, nl)
    # 环心：示意声明
    ca = life(t, 6.8, 19.8)
    tw = text_w("示意模型", 30, "m") + 33
    x0 = CX - (tw + 20 + text_w("帮助理解，非实验结论", 32, "r")) / 2
    tag(c, "示意模型", x0, 1490, ca, False, 30, "left")
    text(c, "帮助理解，非实验结论", x0 + tw + 20, 1490, 32, "r", mix(DARK, LIGHT, 0.5), ca, "left")
    # 每步一个关系
    lines(c, ["下一条【好不好看】，", "滑之前不知道"], CX, 400, 64, 92, t, 8.0, 10.6)
    lines(c, ["这份不确定，让人期待", "【“也许下一条更好”】"], CX, 400, 64, 92, t, 10.8, 14.1)
    lines(c, ["新内容几乎", "【零等待】出现"], CX, 400, 64, 92, t, 14.3, 16.6)
    lines(c, ["重复多了，滑动", "容易变成【习惯】"], CX, 400, 64, 92, t, 16.8, 19.8)
    source(c, ["理论框架：奖励预期与不确定性（Schultz 等，1997）"], 1556, life(t, 8.4, 14.1))
    source(c, ["依据：习惯研究综述（Wood & Rünger，2016）"], 1556, life(t, 17.2, 19.8))


def s3_hook2(c: skia.Canvas, t: float):
    """20–25 秒：第二个钩子；循环缩小并转化为横向时间轴。"""
    if not 19.8 <= t < 25.6:
        return
    punch(c, ["这种体验，", "有什么历史来由？"], CX, 360, 100, 130, t, 20.1, 24.7, gold_rows=(1,))
    k = ease_in_out(prog(t, 20.4, 1.6))
    # 循环节点收缩成点，滑到同一水平线
    loop_a = 1 - ease_in_out(prog(t, 20.4, 0.8))
    if loop_a > 0:
        draw_loop(c, CX, 1060, 255 * (1 - 0.5 * k), 330 * (1 - 0.5 * k), 1 - 0.6 * k, loop_a,
                  [1] * 4, [0] * 4, [1] * 4, [0] * 4)
    nodes = loop_geom(CX, 1060, 255, 330)
    targets = [(180, 980), (380, 980), (580, 980), (780, 980)]
    da = life(t, 20.4, 25.2, 0.3, 0.4)
    for (x0, y0), (x1, y1) in zip(nodes, targets):
        x, y = lerp(x0, x1, k), lerp(y0, y1, k)
        c.drawCircle(x, y, lerp(14, 10, k), paint(GOLD, da))
    lk = ease_in_out(prog(t, 21.8, 1.0))
    polyline(c, [(100, 980), (100 + 760 * lk, 980)], 1 if lk > 0 else 0, DARK, da, 3)


TL_Y = 700
TL_X = [200, 480, 760]
TL_NODES = [
    dict(t0=25.0, year="1992", tag="技术发展", filled=True,
         what=["“协同过滤”出现：", "用【他人的反馈】筛选信息"],
         rel=["推荐系统的早期源头之一"],
         src=["Goldberg 等，1992，Tapestry 系统"]),
    dict(t0=31.2, year="1997", tag="研究背景", filled=False,
         what=["猴子实验：多巴胺信号", "与【“预期落差”】有关"],
         rel=["更关乎预期，", "不是“快乐物质”"],
         src=["Schultz、Dayan、Montague，1997，Science", "动物实验，不能直接证明人刷视频的行为"]),
    dict(t0=37.6, year="2000s—2010s", tag="产品发展", filled=True,
         what=["无限滚动、自动播放", "在信息流中【逐渐普及】"],
         rel=["页面不再自然“到底”"],
         src=["例：YouTube 2015 年在网页端推出自动播放", "无限滚动的“发明者”说法有争议，此处不采用"]),
]


def s4_timeline(c: skia.Canvas, t: float):
    """25–43 秒：三节点历史时间轴；每个节点：时期 → 出现了什么 → 与本主题的关系。"""
    if not 24.6 <= t < 44.6:
        return
    chapter(c, t, 25.0, 43.8, "02", "历史背景")
    a = life(t, 24.6, 43.8, 0.4, 0.5)
    # 轴线：由场景 3 的水平线上移而来
    k = ease_in_out(prog(t, 24.6, 0.6))
    ay = lerp(980, TL_Y, k)
    polyline(c, [(100, ay), (860, ay)], 1, DARK, a, 3, head=12)
    for i, n in enumerate(TL_NODES):
        on = prog(t, n["t0"], 0.35)
        active = life(t, n["t0"], TL_NODES[i + 1]["t0"] if i < 2 else 43.8, 0.35, 0.35)
        x = TL_X[i]
        r = lerp(10, 10 + 8 * ease_out(on), 1) if on > 0 else 9
        c.drawCircle(x, ay, r, paint(GOLD if on > 0 else DARK, a))
        if active > 0:
            c.drawCircle(x, ay, r + 12, paint(GOLD, a * active * 0.8, 2))
        ya = a * life(t, n["t0"])
        ysize = 40 if len(n["year"]) <= 4 else 30
        text(c, n["year"], x, ay - 56, ysize, "b", mix(DARK, GOLD, 0.3 + 0.7 * active), ya)
        tagy = ay + 54
        sa = a * life(t, n["t0"] + 0.1) * (0.55 + 0.45 * active)
        if sa > 0:
            tw = text_w(n["tag"], 28, "m") + 26
            rrect(c, x, tagy, tw, 44, 22, fill=GOLD if n["filled"] else None, fa=sa,
                  stroke=None if n["filled"] else GOLD, sa=sa, sw=2)
            text(c, n["tag"], x, tagy, 28, "m", BG if n["filled"] else GOLD, sa)
        # 详情卡：局部放大
        da = a * active
        if da <= 0:
            continue
        slide = (1 - ease_out(prog(t, n["t0"], 0.5))) * 60
        c.save()
        c.translate(slide, 0)
        # 从轴上节点引出的细线
        polyline(c, [(x, ay + 82), (x, 860), (CX, 860)] if x != CX else [(x, ay + 82), (x, 860)],
                 ease_out(prog(t, n["t0"] + 0.1, 0.4)), DARK, da, 2)
        rrect(c, CX, 1145, 816, 550, 28, fill="#0E0F12", fa=da, stroke=DARK, sa=da, sw=2)
        text(c, n["year"], LEFT + 48, 960, 104 if len(n["year"]) <= 4 else 76, "k", GOLD, da, "left",
             gold=True)
        tag(c, n["tag"], RIGHT - 110, 960, da, n["filled"], 32, "center")
        c.restore()
        # 出现了什么 → 关系（分两拍）
        lines(c, n["what"], LEFT + 48, 1050, 54, 70, t, n["t0"] + 0.5, None, "b", LIGHT, "left")
        ra = life(t, n["t0"] + 2.2)
        if ra > 0:
            yy = 1050 + 70 * len(n["what"]) + 4
            c.drawLine(LEFT + 48, yy, LEFT + 48 + 120 * ease_out(prog(t, n["t0"] + 2.2, 0.4)), yy,
                       paint(GOLD, da * ra, 2))
            text(c, "与本主题的关系", LEFT + 48, yy + 40, 30, "m", DARK, da * ra, "left")
            for j, row in enumerate(n["rel"]):
                text(c, row, LEFT + 48, yy + 100 + j * 68, 52, "b", GOLD, da * life(t, n["t0"] + 2.4 + j * 0.15),
                     "left")
        source(c, n["src"], 1466, da * life(t, n["t0"] + 1.0))
    # 常驻声明：时间先后≠因果
    text(c, "时间先后只是背景，不代表已证实的因果", CX, 1572, 34, "m", mix(DARK, LIGHT, 0.5),
         a * life(t, 26.0))


def s5_hook3(c: skia.Canvas, t: float):
    """43–48 秒：第三个钩子；时间轴退场，内容卡片行入场，为推荐流程图铺垫。"""
    if not 43.8 <= t < 48.6:
        return
    punch(c, ["下一条为什么", "越来越合你的口味？"], CX, 380, 86, 120, t, 44.1, 47.7, gold_rows=(1,))
    kinds = ["circle", "tri", "square"]
    for i in range(3):
        st = 45.0 + 0.2 * i
        a = life(t, st, None, 0.4)
        y = 980 + (1 - ease_out(prog(t, st, 0.5))) * 120
        # 47.6 后移动到流程图第一行的位置
        m = ease_in_out(prog(t, 47.6, 0.8))
        y = lerp(y, 760, m)
        content_card(c, FLOW_X[i], y, lerp(240, 210, m), lerp(300, 170, m), a, kinds[i], lit=0.2)


FLOW_X = [210, 480, 750]


def s6_flow(c: skia.Canvas, t: float):
    """48–57 秒：推荐反馈流程（示意）：反馈 → 推荐系统 → 筛选 → 下一批。"""
    if not 48.3 <= t < 57.6:
        return
    chapter(c, t, 48.3, 56.9, "03", "推荐反馈")
    out = 56.9
    a = life(t, 48.3, out, 0.3, 0.5)
    lines(c, ["你的每个动作，", "都是一次【反馈】"], CX, 330, 64, 90, t, 48.4, out)
    tag(c, "示意流程", RIGHT - 70, 196, life(t, 48.6, out), False, 30)
    kinds = ["circle", "tri", "square"]
    chips = ["看完", "点赞", "很快划走"]
    for i in range(3):
        swiped = i == 2
        dim = 0.6 * ease_out(prog(t, 50.4, 0.4)) if swiped else 0.0
        content_card(c, FLOW_X[i], 620 + 140, 210, 170, a, kinds[i], lit=0.2 if swiped else 0.6 * life(t, 49.0 + 0.6 * i), dim=dim)
        ca = a * life(t, 49.0 + 0.6 * i)
        if ca > 0:
            cw = text_w(chips[i], 40, "b") + 44
            rrect(c, FLOW_X[i], 900, cw, 64, 32, fill="#1A1710", fa=ca, stroke=GOLD if not swiped else DARK,
                  sa=ca, sw=2)
            text(c, chips[i], FLOW_X[i], 900, 40, "b", GOLD if not swiped else mix(DARK, LIGHT, 0.4), ca)
        # 反馈箭头汇入推荐系统
        fa = ease_in_out(prog(t, 50.8 + 0.12 * i, 0.6))
        polyline(c, [(FLOW_X[i], 940), (FLOW_X[i], 975), (CX + (i - 1) * 90, 1010), (CX + (i - 1) * 90, 1030)],
                 fa, DARK if swiped else GOLD, a, 3, head=10)
    ba = a * life(t, 51.3)
    if ba > 0:
        pulse = 1 + 0.04 * math.sin(math.pi * clamp01((t - 51.6) / 0.6)) if t > 51.6 else 1
        c.save()
        c.translate(CX, 1090)
        c.scale(pulse, pulse)
        rrect(c, 0, 0, 380, 110, 22, fill="#1C1912", fa=ba, stroke=GOLD, sa=ba, sw=3)
        text(c, "推荐系统", 0, 0, 52, "b", GOLD, ba)
        c.restore()
        text(c, "调整下一批的排序", CX, 1170, 32, "m", mix(DARK, LIGHT, 0.5), ba * life(t, 51.8))
    # 候选内容经过筛选
    cand = ["circle", "square", "tri", "square", "circle", "tri"]
    xs = [140, 276, 412, 548, 684, 820]
    st = 52.6
    for j, kd in enumerate(cand):
        ca = a * life(t, st + 0.08 * j, None, 0.3)
        if ca <= 0:
            continue
        keep = kd != "square"
        m = ease_in_out(prog(t, 54.0 + 0.1 * j, 0.7))
        y = 1260
        if keep:
            y = lerp(1260, 1372, m)
            content_card(c, xs[j], y, 110, 96, ca, kd, lit=m)
        else:
            content_card(c, xs[j], y - 10 * m, 110, 96, ca * (1 - 0.65 * m), kd, dim=m)
    text(c, "候选内容", LEFT, 1196, 30, "m", DARK, a * life(t, st), "left")
    text(c, "↓ 更接近你反馈的排到前面", LEFT, 1462, 32, "m", GOLD, a * life(t, 54.8), "left")
    source(c, ["依据：TikTok 官方说明（2020）：看完较长视频是强信号；",
               "YouTube 论文（2016）：按预测观看时长排序。",
               "各平台的具体权重未公开。"], 1510, a * life(t, 49.5))
    # 次层：结论
    lines(c, ["系统据此调整下一批内容"], CX, 540, 52, 0, t, 52.8, out, "m", LIGHT)


def list_rows(c: skia.Canvas, x: float, top: float, w: float, h: float, offset: float, a: float, n: int,
              end_marker: bool, t: float):
    """手机框内的内容列表；offset 为滚动量。end_marker=True 时末尾画“到底了”。"""
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x - w / 2, top, w, h))
    rh = 150
    for i in range(n):
        y = top + 40 + i * rh - offset + rh / 2
        if y < top - rh or y > top + h + rh:
            continue
        rrect(c, x, y, w - 48, rh - 26, 14, fill="#121317", fa=a, stroke=DARK, sa=a * 0.8, sw=2)
        shape(c, ["circle", "tri", "square"][i % 3], x - w / 2 + 70, y, 46, DARK, a)
        c.drawLine(x - w / 2 + 116, y - 14, x + w / 2 - 50, y - 14, paint(DARK, a * 0.8, 6))
        c.drawLine(x - w / 2 + 116, y + 16, x + w / 2 - 110, y + 16, paint(DARK, a * 0.6, 6))
    if end_marker:
        y = top + 40 + n * rh - offset + 46
        text(c, "— 到底了 —", x, y, 38, "b", GOLD, a)
    c.restore()


def phone(c: skia.Canvas, x: float, top: float, w: float, h: float, a: float):
    rrect(c, x, top + h / 2, w + 16, h + 16, 40, stroke=mix(DARK, GOLD, 0.4), sa=a, sw=3)


def s6_compare(c: skia.Canvas, t: float):
    """57–65 秒：有明确终点的列表 vs 持续加载的列表，突出“停止节点”。"""
    if not 56.9 <= t < 65.6:
        return
    chapter(c, t, 57.0, 64.9, "03", "停止节点")
    out = 64.9
    a = life(t, 57.0, out, 0.4, 0.5)
    lines(c, ["区别在于：", "有没有【停止节点】"], CX, 330, 66, 92, t, 57.1, out)
    tag(c, "示意界面", RIGHT - 70, 196, life(t, 57.3, out), False, 30)
    top, ph, pw = 650, 720, 330
    lx, rx = 290, 676
    for x, lab in ((lx, "有终点的列表"), (rx, "持续加载的列表")):
        text(c, lab, x, 590, 44, "b", LIGHT, a * life(t, 57.5))
        phone(c, x, top, pw, ph, a * life(t, 57.5))
    la = a * life(t, 57.7)
    # 左：滚到底后停住
    off_l = 520 * ease_in_out(prog(t, 58.0, 2.2))
    list_rows(c, lx, top, pw, ph, off_l, la, 6, True, t)
    # 右：持续上滚，底部加载转圈
    off_r = 260 * max(0.0, t - 58.0)
    list_rows(c, rx, top, pw, ph, off_r, la, 6 + int(off_r / 150) + 4, False, t)
    sp = la * life(t, 58.2)
    if sp > 0:
        cy = top + ph - 40
        c.drawCircle(rx, cy, 30, paint("#08090B", sp))
        ang = (t * 360) % 360
        c.drawArc(skia.Rect.MakeXYWH(rx - 20, cy - 20, 40, 40), ang, 260, False, paint(GOLD, sp, 4))
    # 停止节点标注
    na = a * life(t, 60.4)
    if na > 0:
        endy = top + 40 + 6 * 150 - off_l + 46
        s = lerp(1.15, 1.0, ease_out(prog(t, 60.4, 0.3)))
        rrect(c, lx, endy, 280 * s, 76 * s, 38 * s, stroke=GOLD, sa=na, sw=3)
        text(c, "停止节点", lx, top + ph + 70, 48, "b", GOLD, na)
        polyline(c, [(lx, top + ph + 34), (lx, endy + 46)], ease_out(prog(t, 60.6, 0.4)), GOLD, na, 2, head=10)
    ra = a * life(t, 61.2)
    text(c, "没有自然终点", rx, top + ph + 70, 48, "b", mix(DARK, LIGHT, 0.6), ra)
    source(c, ["参考：Rixen 等（2023）无限滚动现场研究；",
               "欧盟委员会（2026）对无限滚动、自动播放等设计的初步认定"], 1520, a * life(t, 58.0))


def s7_hook4(c: skia.Canvas, t: float):
    """65–70 秒：第四个钩子；循环中出现清晰的暂停节点。"""
    if not 64.9 <= t < 70.6:
        return
    punch(c, ["怎样给自己", "一个停下来的机会？"], CX, 360, 86, 120, t, 65.1, 69.8, gold_rows=(1,))
    a = life(t, 65.6, 69.8, 0.5, 0.5)
    pause = prog(t, 67.6, 0.6)
    flow = None if t > 67.6 + 0.4 else t
    draw_loop(c, CX, 1110, 240, 300, 0.92, a, [1] * 4, [0.25] * 4, [1] * 4, [0.15] * 4,
              pause=pause if t >= 67.6 else 0.0, flow_t=flow)
    text(c, "暂停节点", CX - 240 * 0.707 - 66, 1110 + 300 * 0.707, 44, "b", GOLD, a * life(t, 68.1), "right")


METHOD_Y = [640, 1000, 1330]


def s8_method(c: skia.Canvas, t: float):
    """70–84 秒：方法。操作前 → 加一步（“如果—就”停止计划）→ 操作后。"""
    if not 69.9 <= t < 84.6:
        return
    chapter(c, t, 70.0, 83.9, "04", "一个可以试的方法")
    out = 83.9
    a = life(t, 70.0, out, 0.4, 0.5)
    lines(c, ["给循环加一个【停止节点】"], CX, 330, 62, 0, t, 70.1, 79.9)
    lines(c, ["补回消失的停止节点，", "也给【习惯】留个出口"], CX, 290, 56, 78, t, 80.2, out)
    # 三段式标签与连接箭头
    labels = ["操作前", "加一步", "操作后"]
    starts = [70.4, 73.4, 78.0]
    for i, (lab, st) in enumerate(zip(labels, starts)):
        tag(c, lab, LEFT, METHOD_Y[i] - 120 if i == 1 else METHOD_Y[i] - 92, a * life(t, st), i == 1, 34, "left")
    for i in range(2):
        y0 = [METHOD_Y[0] + 50, METHOD_Y[1] + 170][i]
        y1 = [METHOD_Y[1] - 160, METHOD_Y[2] - 130][i]
        polyline(c, [(CX, y0), (CX, y1)], ease_out(prog(t, starts[i + 1] - 0.3, 0.4)), DARK, a, 3, head=12)
    # 操作前：没有停顿的链条
    pa = a * life(t, 70.4)
    chain = ["滑动", "下一条", "滑动", "下一条", "…"]
    xs = [140, 300, 470, 630, 790]
    for j, (w_, x) in enumerate(zip(chain, xs)):
        ja = pa * life(t, 70.6 + 0.25 * j)
        text(c, w_, x, METHOD_Y[0], 48, "b", mix(DARK, LIGHT, 0.7), ja)
        if j < 4:
            polyline(c, [(x + text_w(w_, 48) / 2 + 10, METHOD_Y[0]), (xs[j + 1] - text_w(chain[j + 1], 48) / 2 - 14,
                                                                    METHOD_Y[0])],
                     ease_out(prog(t, 70.8 + 0.25 * j, 0.3)), DARK, ja, 3, head=9)
    # 加一步：如果—就 计划卡
    ka = a * life(t, 73.4)
    if ka > 0:
        rrect(c, CX, METHOD_Y[1], 816, 330, 26, fill="#16140F", fa=ka, stroke=GOLD, sa=ka, sw=3)
        text(c, "开刷前设个计时，并想好：", LEFT + 44, METHOD_Y[1] - 100, 46, "m", LIGHT, ka, "left")
        ia = ka * life(t, 74.4)
        text(c, "如果", LEFT + 44, METHOD_Y[1] - 6, 56, "k", GOLD, ia, "left")
        text(c, "提醒响了", LEFT + 44 + 132, METHOD_Y[1] - 6, 56, "b", LIGHT, ia, "left")
        ja = ka * life(t, 75.4)
        text(c, "就", LEFT + 44, METHOD_Y[1] + 92, 56, "k", GOLD, ja, "left")
        text(c, "先锁屏，再决定要不要继续", LEFT + 44 + 132, METHOD_Y[1] + 92, 52, "b", LIGHT, ja, "left")
    # 操作后：链条中出现暂停节点
    qa = a * life(t, 78.0)
    chain2 = [("滑动", 150), ("下一条", 330), ("", 520), ("自己决定", 740)]
    for j, (w_, x) in enumerate(chain2):
        ja = qa * life(t, 78.2 + 0.35 * j)
        if j == 2:
            pause_icon(c, x, METHOD_Y[2], 40 * lerp(1.2, 1.0, ease_out(prog(t, 78.9, 0.3))), ja)
        else:
            text(c, w_, x, METHOD_Y[2], 48, "b", GOLD if j == 3 else mix(DARK, LIGHT, 0.7), ja)
        if j < 3:
            x0 = x + (text_w(w_, 48) / 2 if w_ else 40) + 12
            nw, nx = chain2[j + 1]
            x1 = nx - (text_w(nw, 48) / 2 if nw else 40) - 14
            polyline(c, [(x0, METHOD_Y[2]), (x1, METHOD_Y[2])], ease_out(prog(t, 78.4 + 0.35 * j, 0.3)), DARK, ja,
                     3, head=9)
    text(c, "停一下", 520, METHOD_Y[2] + 72, 36, "m", GOLD, qa * life(t, 79.2))
    # 依据与边界
    source(c, ["“如果—就”计划有助于执行既定目标（元分析，",
               "Gollwitzer & Sheeran 2006）；打开应用前加一道确认，",
               "约 36% 的打开被放弃（Grüning 等 2023，280 人，6 周）"],
           1450, a * life(t, 75.0))
    lines(c, ["不保证对每个人有效，可以试一试"], CX, 452, 40, 0, t, 80.8, out, "m", mix(DARK, LIGHT, 0.7))


def s9_close(c: skia.Canvas, t: float):
    """84–89 秒：收束，回扣开场。"""
    if not 83.9 <= t < 89.6:
        return
    a = life(t, 84.0, 88.9, 0.5, 0.6)
    lines(c, ["再刷一条，没关系。"], CX, 520, 72, 0, t, 84.1, 88.9, "b", LIGHT)
    lines(c, ["停在哪里，", "可以由你决定。"], CX, 660, 92, 124, t, 85.0, 88.9, "k", LIGHT, gold=True)
    draw_loop(c, CX, 1190, 200, 220, 0.72, a * 0.9, [1] * 4, [0.2] * 4, [1] * 4, [0.1] * 4, pause=1.0)


REFS = [
    "Goldberg D, et al. (1992). Using collaborative filtering to weave an information tapestry. Commun. ACM, 35(12).",
    "Schultz W, Dayan P, Montague PR (1997). A neural substrate of prediction and reward. Science, 275.",
    "Wood W, Rünger D (2016). Psychology of habit. Annu. Rev. Psychol., 67.",
    "Covington P, Adams J, Sargin E (2016). Deep neural networks for YouTube recommendations. RecSys '16.",
    "TikTok Newsroom (2020). How TikTok recommends videos #ForYou.",
    "Rixen JO, et al. (2023). The loop and reasons to break it: infinite scrolling behaviour in social media apps. MobileHCI '23.",
    "European Commission (2026-02-06). Preliminary findings on TikTok's addictive design under the DSA.",
    "Gollwitzer PM, Sheeran P (2006). Implementation intentions and goal achievement. Adv. Exp. Soc. Psychol., 38.",
    "Grüning DJ, Riedel F, Lorenz-Spreen P (2023). Directing smartphone use through the self-nudge app one sec. PNAS, 120(8).",
    "CNET (2015). How to turn off YouTube's new autoplay feature.",
]


def wrap_words(s: str, size: float, max_w: float, weight: str = "r") -> list[str]:
    out, cur = [], ""
    for word in s.split(" "):
        trial = f"{cur} {word}".strip()
        if cur and text_w(trial, size, weight) > max_w:
            out.append(cur)
            cur = word
        else:
            cur = trial
    return out + [cur] if cur else out


def s10_refs(c: skia.Canvas, t: float):
    """89–96 秒：参考资料（不计入正文字数）。"""
    if t < 88.9:
        return
    a = life(t, 89.0, None, 0.6)
    text(c, "参考资料", LEFT, 210, 56, "k", GOLD, a, "left", gold=True)
    c.drawLine(LEFT, 262, LEFT + 160, 262, paint(DARK, a, 2))
    y = 330
    for i, ref in enumerate(REFS):
        ra = a * life(t, 89.2 + 0.06 * i)
        text(c, f"{i + 1:>2}", LEFT, y, 28, "b", GOLD, ra, "left")
        rows = wrap_words(ref, 28, RIGHT - LEFT - 52)
        for j, row in enumerate(rows):
            text(c, row, LEFT + 52, y + j * 38, 28, "r", LIGHT, ra, "left")
        y += 38 * len(rows) + 26
    text(c, "示意图仅帮助理解，不代表效果大小", LEFT, y + 30, 30, "m", DARK, a, "left")


SCENES = [s1_open, s2_loop, s3_hook2, s4_timeline, s5_hook3, s6_flow, s6_compare, s7_hook4, s8_method,
          s9_close, s10_refs]


def draw_frame(c: skia.Canvas, t: float):
    c.clear(col(BG))
    for s in SCENES:
        s(c, t)


# ---------------------------------------------------------------- 输出

_BUF: np.ndarray | None = None
_SURF: skia.Surface | None = None


def _render(frame: int) -> bytes:
    global _BUF, _SURF
    if _SURF is None:
        _BUF = np.zeros((H, W, 4), np.uint8)
        _SURF = skia.Surface(_BUF)
    draw_frame(_SURF.getCanvas(), frame / FPS)
    return _BUF.tobytes()


def still(t: float, path: str):
    buf = np.frombuffer(_render(int(round(t * FPS))), np.uint8).reshape(H, W, 4)
    skia.Image.fromarray(buf.copy()).save(path, skia.kPNG)


def render(out_path: str, workers: int = 4):
    """多进程逐帧渲染，经 FFmpeg 编码为不含音频流的 H.264 MP4。"""
    n = int(round(TOTAL * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        with get_context("fork").Pool(workers) as pool:
            for buf in pool.imap(_render, range(n), chunksize=8):
                proc.stdin.write(buf)
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")


# ---------------------------------------------------------------- 封面

def cover(path: str, w: int, h: int):
    """同风格封面：竖版 1080×1920，横版 1920×1080。"""
    arr = np.zeros((h, w, 4), np.uint8)
    surf = skia.Surface(arr)
    c = surf.getCanvas()
    c.clear(col(BG))
    if h > w:
        text(c, "为什么", LEFT, 420, 120, "k", LIGHT, 1, "left")
        text(c, "总想再刷一条？", LEFT, 570, 120, "k", LIGHT, 1, "left", gold=True)
        c.drawLine(LEFT, 680, LEFT + 220, 680, paint(GOLD, 1, 3))
        text(c, "四个问题，看懂“下一条”的来路", LEFT, 750, 46, "m", LIGHT, 0.85, "left")
        draw_loop(c, CX, 1150, 255, 270, 1.0, 1, [1] * 4, [0.35] * 4, [1] * 4, [0.2] * 4, pause=1.0)
        text(c, "无声科普 · 示意图解", LEFT, 1580, 34, "m", DARK, 1, "left")
    else:
        text(c, "为什么", 110, 380, 120, "k", LIGHT, 1, "left")
        text(c, "总想再刷一条？", 110, 530, 120, "k", LIGHT, 1, "left", gold=True)
        c.drawLine(110, 640, 330, 640, paint(GOLD, 1, 3))
        text(c, "四个问题，看懂“下一条”的来路", 110, 710, 46, "m", LIGHT, 0.85, "left")
        text(c, "无声科普 · 示意图解", 110, 940, 34, "m", DARK, 1, "left")
        draw_loop(c, 1440, 560, 230, 290, 0.95, 1, [1] * 4, [0.35] * 4, [1] * 4, [0.2] * 4, pause=1.0)
    skia.Image.fromarray(arr.copy()).save(path, skia.kPNG)


def main():
    args = sys.argv[1:]
    if args and args[0] == "--still":
        out = ROOT / "out" / "stills"
        out.mkdir(parents=True, exist_ok=True)
        for s in args[1:]:
            still(float(s), str(out / f"t{float(s):06.2f}.png"))
        return
    out_path = Path(args[0] if args else ROOT / "out" / "scroll_short.mp4")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cover(str(out_path.with_name("scroll_cover_vertical.png")), 1080, 1920)
    cover(str(out_path.with_name("scroll_cover_horizontal.png")), 1920, 1080)
    render(str(out_path))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
