"""阿德勒纸片风的光效与动效层：光晕、旋转光束、星光粒子、扫光、闪白、文字逐个弹出、滚动数字。

全部是纯绘制函数（不依赖时间轴）：调用方传入“距撞击拍的秒数 dt”与节拍脉冲值，
时间轴与音效由 adler.core 的 Pops / Glow / Rays / Spark / Counter 元素和 Shot 的 punch / flashes / shake 负责。
设计取向：光效只做强调，不盖过内容——光束与光晕用低透明度的强调色，粒子 1 秒内消失，闪白 0.18 秒内退完。
"""

import math

import numpy as np
import skia

from engine import gfx
from engine.gfx import clamp01, ease_out, ease_out_back, lerp

from . import kit as K


def _rgba(color, a: float) -> int:
    r, g, b = gfx.rgb(color)
    return skia.Color(int(r), int(g), int(b), int(255 * clamp01(a)))


def glow(c, x, y, r, color, alpha=0.5):
    """柔和径向光晕：中心 alpha，向外平滑衰减到透明。"""
    if alpha <= 0.003 or r <= 1:
        return
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y), r, [_rgba(color, alpha), _rgba(color, alpha * 0.35), _rgba(color, 0)],
                                        [0.0, 0.45, 1.0])
    p = skia.Paint(AntiAlias=True, Shader=sh)
    c.drawCircle(x, y, r, p)


def rays(c, x, y, r, color, t, n=14, alpha=0.3, spin=12.0, width=0.5, r0=0.0):
    """旋转光束：n 道楔形光，从中心向外淡出；t 为秒，spin 为每秒转动角度，width 为楔形占扇区的比例。"""
    if alpha <= 0.003:
        return
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y), r, [_rgba(color, alpha), _rgba(color, alpha * 0.5), _rgba(color, 0)],
                                        [0.0, 0.5, 1.0])
    p = skia.Paint(AntiAlias=True, Shader=sh)
    path = skia.Path()
    half = math.pi / n * width
    base = math.radians(t * spin)
    for i in range(n):
        a = base + i * math.tau / n
        path.moveTo(x + r0 * math.cos(a), y + r0 * math.sin(a))
        path.lineTo(x + r * math.cos(a - half), y + r * math.sin(a - half))
        path.lineTo(x + r * math.cos(a + half), y + r * math.sin(a + half))
        path.close()
    c.drawPath(path, p)


def sparkle(c, x, y, r, color, alpha=1.0, rot=0.0):
    """四角星光（十字闪光）。"""
    if alpha <= 0.003 or r <= 0.5:
        return
    K.star(c, x, y, r, color, alpha, 4, 0.22, rot)


def sparks(c, x, y, dt, colors, n=16, seed=5, reach=260, size=18, alpha=1.0, dur=0.9):
    """星光粒子爆散：撞击后 dt 秒，粒子向外减速飞出并闪烁，dur 秒内消失。"""
    if dt < 0 or dt > dur:
        return
    rng = np.random.default_rng(seed)
    k = ease_out(clamp01(dt / dur))
    for i in range(n):
        ang = i * math.tau / n + rng.uniform(-0.25, 0.25)
        d = reach * rng.uniform(0.55, 1.0) * k
        tw = 0.6 + 0.4 * math.sin(dt * 30 + i * 1.7)
        s = size * rng.uniform(0.6, 1.2) * (1 - 0.7 * k) * tw
        sparkle(c, x + d * math.cos(ang), y + d * math.sin(ang) + 60 * dt * dt, s, colors[i % len(colors)],
                alpha * (1 - clamp01((dt - dur * 0.45) / (dur * 0.55))), dt * 120 + i * 20)


def shine(c, bounds: skia.Rect, p: float, draw, color="#FFFFFF", alpha=0.85, band=0.22):
    """扫光：先 draw() 画出图形，再让一道斜向白光带从左到右扫过（只照亮已画出的像素），p 为扫光进度 0→1。"""
    if not 0 < p < 1:
        draw()
        return
    c.saveLayer(bounds, None)
    draw()
    w = bounds.width()
    cx = lerp(bounds.left() - w * band, bounds.right() + w * band, p)
    h = bounds.height()
    sh = skia.GradientShader.MakeLinear([skia.Point(cx - w * band, bounds.top() + h), skia.Point(cx + w * band, bounds.top())],
                                        [_rgba(color, 0), _rgba(color, alpha), _rgba(color, 0)], [0.0, 0.5, 1.0])
    paint = skia.Paint(AntiAlias=True, Shader=sh, BlendMode=skia.BlendMode.kSrcATop)
    c.drawRect(bounds, paint)
    c.restore()


def flash(c, a, color="#FFFFFF"):
    """全屏闪白（或强调色闪）。"""
    if a > 0.003:
        c.drawPaint(K.paint(color, a))


def flash_alpha(dt, peak=0.55, dur=0.18):
    """闪白透明度：撞击帧最亮，dur 秒内指数退完。"""
    if dt < 0 or dt > dur:
        return 0.0
    return peak * (1 - dt / dur) ** 2


def shake_offset(dt, amp=14.0, dur=0.28, seed=0):
    """镜头抖动偏移 (dx, dy)：撞击后 dur 秒内衰减。"""
    if dt < 0 or dt > dur:
        return 0.0, 0.0
    e = (1 - dt / dur) ** 2 * amp
    return e * math.sin(dt * 95 + seed), e * math.cos(dt * 77 + seed * 1.3)


# ---------------------------------------------------------------- 文字逐个弹出

def word_pop(dt, dur=0.32):
    """单个词的弹出姿态 (alpha, scale, rot)：撞击帧即可见，放大过冲后回弹落定。"""
    if dt < 0:
        return None
    k = clamp01(dt / dur)
    return clamp01(dt / 0.05), 0.35 + 0.65 * ease_out_back(k, 3.2), (1 - ease_out(k)) * 9


def word_box(word: str, size: float, font: str, hi: bool) -> tuple[float, float]:
    w = K.text_w(word, size, font)
    return (w + size * 0.7, size * 1.45) if hi else (w, size * 1.2)


def draw_word(c, word, x, y, size, font, color, hi_fill, hi_color, alpha, hi: bool, lift=1.0):
    """一个词：普通词为墨色粗字，高亮词为强调色纸片（白字）。"""
    if hi:
        w, h = word_box(word, size, font, True)
        K.card(c, x, y, w, h, hi_fill, alpha, r=h * 0.28, lift=lift)
        K.text(c, word, x, y, size, font, hi_color, alpha)
    else:
        K.text(c, word, x, y, size, font, color, alpha, shadow=(3, 5, 6, K.SHADOW))


def layout_words(words: list[tuple[str, bool]], size, font, layout, gap, maxw, breaks=()):
    """排版：row 为居中多行（breaks 中的词序号之前强制换行，超宽自动折行）；col 为每词一行。
    返回各词中心 (dx, dy)，以整体中心为原点。"""
    boxes = [word_box(w, size, font, h) for w, h in words]
    if layout == "col":
        hs = [b[1] for b in boxes]
        total = sum(hs) + gap * (len(hs) - 1)
        y, out = -total / 2, []
        for h in hs:
            out.append((0.0, y + h / 2))
            y += h + gap
        return out
    lines, cur, cw = [], [], 0.0
    for i, (w, h) in enumerate(boxes):
        add = w + (gap if cur else 0)
        if cur and (cw + add > maxw or i in breaks) and not (i not in breaks and _punct(words[i][0])):
            lines.append((cur, cw))
            cur, cw = [], 0.0
            add = w
        cur.append(i)
        cw += add
    if cur:
        lines.append((cur, cw))
    lh = max(b[1] for b in boxes) + gap * 0.6
    out = [(0.0, 0.0)] * len(words)
    y0 = -(len(lines) - 1) * lh / 2
    for li, (idx, cw) in enumerate(lines):
        x = -cw / 2
        for i in idx:
            out[i] = (x + boxes[i][0] / 2, y0 + li * lh)
            x += boxes[i][0] + gap
    return out


def _punct(w: str) -> bool:
    """纯标点的词（如单独的“？”）不单独换行，跟在上一个词后面。"""
    return bool(w) and all(ch in "？?！!，,。.、…：:" for ch in w)


def parse_words(words) -> tuple[list[tuple[str, bool]], set]:
    """词列表：字符串按空格分词、| 换行，词内【】部分拆成独立的高亮词（如“变【笨】吗”→ 变 / 笨 / 吗）；
    也可直接传列表。返回 (词列表, 换行位置集合)。"""
    if isinstance(words, str):
        words = words.replace("|", " | ").split()
    out, breaks = [], set()
    for w in words:
        if w == "|":
            breaks.add(len(out))
            continue
        for seg, hi in gfx.parse_marks(w):
            out.append((seg, hi))
    return out, breaks


# ---------------------------------------------------------------- 滚动数字

def counter_value(v0, v1, k):
    """滚动数字：先快后慢（ease_out），最后落在 v1。"""
    return lerp(v0, v1, ease_out(clamp01(k)) if k < 1 else 1.0)
