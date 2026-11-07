"""《丰田模式》每讲的开场钩子（第 0 屏，黄金 3 秒）：用本讲的痛点画面 + 一句配音开场，大字随配音逐字砸下，“丰田模式”是随后弹出的小字系列标识。

统一节奏（8 拍开场屏，约 4.4 秒；配音长时自动调整，见 prepare）：
  第 0–2 拍 画面动作（每拍一个，配打击乐）；第 3 拍起配音念大字（HOOK_TEXT，配音句默认就是大字，可在 HOOK_VOICE 改），
  每个字的落地时刻 = 该字在配音里的发声起点（fengtian.voice.syllable_onsets：谱通量起音 + CTC 识别逐字时刻）；
  配音一顿一顿地念（fengtian.voice.spread_line：在字界切开、字间插静音，相邻两字起点相隔约 0.34 秒，字多时缩到不低于 0.27，逗号处多停 0.15），
  每字从上方放大加速落下 → 落地压扁回弹 → 两侧尘土线，配一声打击乐（峰值对齐落地，tom，末字用 text_sfx）和轻震（末字重震）；
  末字落地后的拍上弹出系列小字，末字之后至少停 1.2 秒不出新笔画，再由本讲的转场进入第 1 屏。
  配音句长时首字提前到第 2 拍，仍放不下再把开场屏加长 2 拍（Lesson 构造时调用 prepare 决定，排期随之变化）。
接口：hook(H, j, cx, cy, acc)。H 要有 b（白板）、tb(j, k)（拍 → 绝对秒）、note(*字)（登记画面字给文案检查），
以及 HOOK（prepare 的结果）、tb_now(j, k)（finish 之前可用的 tb）、beat_at(j, T)（绝对秒 → 本屏小数拍）、
sfx_at(T, 名称, 增益, 说明)（不在拍上的音效）。common.Lesson 与 ep01_andon._Hook 都提供这些。
画面以 (cx, cy) 为中心，开场视角 (cx, cy - 40, 0.7)：可视约 x ±620、y cy-680…cy+600，内容留在 x ±560、y cy-620…cy+560。
颜色用白板墨色（BLACK / RED / BLUE / GREEN），深色底由 theme.Recolor 统一反色；大字用本讲主题色 acc（不换色）。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, box_path, draw_li, pop_scale, slam_scale, wobble
from whiteboard import engine as wb
from whiteboard.engine import P, check, circle, join, rect

SERIES_SUB = "丰田模式 · 精益制造的14项原则"
GRAY = "#6B6B6B"


# ---------------------------------------------------------------- 公共件

def _label(H, j, k, x, y):
    H.note(SERIES_SUB)

    def fn(c, kk, T):
        sc = pop_scale(T - H.tb(j, k))
        if sc > 0:
            with K.at(c, x, y, 0, sc):
                w = K.text_w(SERIES_SUB, 46, "sans_medium") + 60
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -38, w, 76), 38, 38, wb.marker(GRAY, 4, clamp01(sc * 2)))
                K.text(c, SERIES_SUB, 0, 0, 46, "sans_medium", GRAY, clamp01(sc * 2))
        return None
    return fn


INTRO_Z = 0.6                  # 开场屏缩放：舞台 872×900 px ≈ 板上 1453×1500
TEXT_DY = 430                  # 大字中心在钩子中心下方（板上单位）；舞台中部偏下，不压钩子画面
TEXT_DY2 = 380                 # 两行时整体上提，系列小字不进字幕条
TEXT_MAX = 340                 # 大字上限（板上单位，≈204px）
TEXT_W = 1250                  # 一行大字最宽（板上单位，≈750px）
ROWS = dict(reject=3, checklist=4)     # 字多的讲在第几个单位后换行（有空格的在空格处换行）


def intro_view(hx, hy):
    """钩子中心 (hx, hy) 时的开场视角：比原来（0.7、中心 hy-90）拉远并下移，画面缩小上移。"""
    return hx, hy + 60, INTRO_Z


def _rows(hook, text):
    """大字分行：[[(字, 音节数), …], …]。空格处换行；ROWS 里的讲在指定位置换行。"""
    toks = _units(text)
    rows, cur = [], []
    brk = ROWS.get(hook)
    for u in toks:
        if u[0] == " ":
            rows.append(cur)
            cur = []
            continue
        cur.append(u)
        if brk and len(cur) == brk and not rows:
            rows.append(cur)
            cur = []
    rows.append(cur)
    return [r for r in rows if r]


def _finish(H, j, cx, cy, text, acc, size=None, ty=None, shake=12.0, text_sfx="kick"):
    """大字随开场配音逐字砸下（落地 = 该字发声起点，每字一声打击乐 + 轻震，末字 text_sfx + shake 重震），
    之后在拍上弹出系列小字。配音与落地时刻由 prepare() 预先算好，放在 H.HOOK。
    大字统一放大（一行最多 TEXT_MAX、宽不超过 TEXT_W，字多自动缩或分两行），中心在钩子中心下方 TEXT_DY；
    size / ty 参数保留兼容，不再使用。"""
    b = H.b
    hv = H.HOOK
    if hv is None or hv["text"] != text:
        raise ValueError(f"开场大字“{text}”与 HOOK_TEXT 不一致：{hv and hv['text']}")
    H.note(text)
    rows = _rows(hv["hook"], text)
    gap = 0.06

    def row_w(r, s_):
        return sum(K.text_w(u, s_, "hand") for u, _ in r) + gap * s_ * (len(r) - 1)
    size = min([TEXT_MAX * (0.74 if len(rows) > 1 else 1.0)] + [TEXT_MAX * TEXT_W / row_w(r, TEXT_MAX) for r in rows])
    lh = size * 1.12
    y0 = cy + (TEXT_DY if len(rows) == 1 else TEXT_DY2) - lh * (len(rows) - 1) / 2
    chars = []
    for ri, r in enumerate(rows):
        x = cx - row_w(r, size) / 2
        for u, _ in r:
            w = K.text_w(u, size, "hand")
            chars.append((u, x + w / 2, y0 + ri * lh))
            x += w + gap * size
    t1 = H.tb_now(j, hv["k"])
    hv["start"] = t1 - hv["land"][0]                    # 配音起点（绝对秒）
    lands = [t1 + r for r in hv["rel"]]
    hv["lands"] = lands
    n = len(chars)
    for i, ((u, x_, y_), tl) in enumerate(zip(chars, lands)):
        last = i == n - 1
        k0 = H.beat_at(j, tl - FALL - 0.02)
        b.custom(j, k0, k0 + 0.3, _drop_char(u, x_, y_, size, acc, tl))
        H.sfx_at(tl, text_sfx if last else "tom", 0.85 if last else 0.75, f"砸字：{u}")
        b.shots[j].shake.append((H.beat_at(j, tl), shake if last else 7.0))
    yl = y0 + (len(rows) - 1) * lh + size * 0.55 + 50
    b.custom(j, hv["label_k"], hv["label_k"] + 0.3, _label(H, j, hv["label_k"], cx, yl), sfx="pop", gain=0.55)


FALL = 0.15                    # 砸落用时（秒）：从上方 1.5 倍大加速落下


def _drop_char(u, x, y, size, color, tl):
    """一个字砸下：tl 前 FALL 秒从上方放大加速落下，tl 落地（压扁 → 回弹），两侧扬起尘土线。"""
    base = y + size * 0.42

    def fn(c, kk, T):
        dt = T - tl
        if dt < -FALL:
            return None
        if dt < 0:
            p = (dt + FALL) / FALL
            yo, s, sx, sy, a = -380 * (1 - p * p), 1.6 - 0.6 * p * p, 1.0, 1.0, clamp01(p * 2.5)
        else:
            w = math.exp(-dt * 11) * math.cos(dt * 30)
            yo, s, sx, sy, a = 0.0, 1.0, 1 + 0.24 * w, 1 - 0.32 * w, 1.0
        c.save()
        c.translate(x, base + yo)
        c.scale(s * sx, s * sy)
        c.translate(0, -size * 0.42)
        K.text(c, u, 0, 0, size, "hand", color, a)
        c.restore()
        if 0 <= dt < 0.4:                              # 尘土：两侧各三道短线向外散开、变淡
            f = ease_out(clamp01(dt / 0.4))
            al = 1 - clamp01(dt / 0.4)
            hw = K.text_w(u, size, "hand") / 2
            for sg in (-1, 1):
                for q, (ang, ln) in enumerate(((8, 0.30), (28, 0.24), (50, 0.18))):
                    r0 = hw + 10 + f * size * 0.35
                    rad = math.radians(ang)
                    x0 = x + sg * r0 * math.cos(rad)
                    y0 = base - r0 * math.sin(rad) * 0.6
                    L_ = size * ln * (1 - 0.4 * f)
                    c.drawLine(x0, y0, x0 + sg * L_ * math.cos(rad), y0 - L_ * math.sin(rad) * 0.6,
                               wb.marker(GRAY, 9, 0.8 * al))
                c.drawCircle(x + sg * (hw + f * size * 0.5), base - 8 - f * 18, 7 + 10 * f, K.paint(GRAY, 0.35 * al))
        return None
    return fn


# ---------------------------------------------------------------- 开场配音：每讲大字（默认也是配音句）与排期

HOOK_TEXT = dict(stamp3="第三遍了", pile="越堆越乱", curve="忙一阵 闲一阵", bars="全卡在一半", checklist="做了100遍还漏",
                 sticky="又漏了一件", doorsign="问题还在", mole="又冒出来了", reject="一开会就被否",
                 treadmill="忙了一天 还在原地", clock8="白忙", desktop="找不到", mailfly="又手滑了", startlights="还没开始",
                 slides="结论呢？", qmarks="又错了", chain="掉链子", apps="又一个", alarm="先顾眼前")
HOOK_VOICE = {}                # 个别讲配音比大字长（如问句）时写在这里，大字须是配音的一段；默认配音 = 大字
HOOK_PINYIN = dict(checklist=[("还漏", "[h][ái]漏")])     # 多音字（合成时换成拼音标注；“还”曾被念成 huán）
BEAT = 0.533                   # 前奏段实测拍长（秒），排开场时估算用
HOLD_S = 1.2                   # 末字落地后至少停留


def _cn_num(n):
    d = "零一二三四五六七八九"
    if n < 10:
        return d[n]
    out, z = "", False
    for v, u in ((1000, "千"), (100, "百"), (10, "十"), (1, "")):
        q, n = divmod(n, v)
        if q:
            out += ("零" if z else "") + d[q] + u
            z = False
        elif out:
            z = True
    return out[:-1] if out.endswith("零") else out


def _is_han(ch):
    return "一" <= ch <= "鿿"


def _units(text):
    """大字拆成逐个砸下的单位 [(字, 音节数)]：汉字一个一单位，连续数字一单位（按读法计音节），
    标点并入前一个字，空格单独一项（音节 0，只占位）。"""
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isdigit():
            j_ = i
            while j_ < len(text) and text[j_].isdigit():
                j_ += 1
            out.append([text[i:j_], len(_cn_num(int(text[i:j_])))])
            i = j_
            continue
        if ch == " ":
            out.append([" ", 0])
        elif _is_han(ch) or not out or out[-1][0] == " ":
            out.append([ch, 1 if _is_han(ch) else 0])
        else:
            out[-1][0] += ch
        i += 1
    return [tuple(u) for u in out]


def voice_text(hook):
    t = HOOK_VOICE.get(hook) or HOOK_TEXT[hook]
    t = "".join(_cn_num(int(u)) if u.isdigit() else u for u, _ in _units(t)).replace(" ", "，")
    return t if t[-1] in "？！。" else t + "。"


def prepare(hook, draft=False, min_beats=8):
    """开场前准备：合成配音句（fengtian.voice.hook_line，逐字发声起点），定第一个字落在第几拍、开场屏几拍、系列小字哪拍弹出。
    规则：首字默认落在第 3 拍（前 3 拍是画面动作）；末字落地后要停 ≥HOLD_S 秒、小字弹出后再停 ≥2 拍，
    放不下时首字提前到第 2 拍，仍放不下再把开场屏加长 2 拍。返回 dict，放到 H.HOOK。"""
    from fengtian import voice
    text, vt = HOOK_TEXT[hook], voice_text(hook)
    clip, on, is_draft = voice.hook_line(vt, HOOK_PINYIN.get(hook, ()), draft=draft)
    clip, on = voice.spread_line(clip, vt, on, asr=not is_draft)          # 一顿一顿地念：字间插静音，相邻两字起点相隔约 0.34 秒
    toks = [u for u in _units(text) if u[0] != " "]
    spoken = "".join(_cn_num(int(u)) if u.isdigit() else "".join(ch for ch in u if _is_han(ch)) for u, _ in toks)
    vsy = "".join(ch for ch in vt if _is_han(ch))
    i0 = vsy.find(spoken)
    if i0 < 0 or len(on) != len(vsy):
        raise ValueError(f"大字“{text}”不是配音“{vt}”的一段")
    land, idx = [], i0
    for u, ns in toks:
        land.append(on[idx])
        idx += ns
    rel = [t - land[0] for t in land]
    for k, beats in ((3, 8), (2, 8), (2, 10), (1, 10), (1, 12)):
        if beats < min_beats:
            continue
        t_last = k * BEAT + rel[-1]
        label_k = math.ceil((t_last + 0.25) / BEAT - 1e-9)
        if beats * BEAT - t_last >= HOLD_S + 0.05 and beats - label_k >= 2:
            break
    return dict(hook=hook, text=text, voice=vt, clip=clip, on=on, land=land, rel=rel, k=k, beats=beats,
                label_k=label_k, draft=is_draft, dur=len(clip) / 44100)


def _stamp(H, j, k, s, x, y, size, rot, color=RED):
    H.note(s)
    w = K.text_w(s, size, "hand") + size * 0.8
    h = size * 1.45

    def fn(c, kk, T):
        dt = T - H.tb(j, k)
        sc = slam_scale(dt)
        if sc <= 0:
            return None
        a = clamp01(dt / 0.06)
        with K.at(c, x, y, rot, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 14, 14, K.paint("#FFFFFF", 0.8 * a))
            c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 14, 14, wb.marker(color, 10, a))
            c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 12, -h / 2 + 12, w - 24, h - 24), 8, 8, wb.marker(color, 4, a))
            K.text(c, s, 0, 0, size, "hand", color, a)
        return None
    return fn


def _doc_lines(x, y, w, h, n, top=0.22):
    parts = [rect(x, y, w, h, 18)]
    for i in range(n):
        yy = y - h / 2 + h * top + i * h * (0.7 / max(1, n))
        parts.append(P((x - w * 0.36, yy), (x + w * (0.36 if i % 3 != 2 else 0.12), yy)))
    return join(*parts)


# ---------------------------------------------------------------- 01 停线：同一份活被“返工”章盖了三遍

def stamp3(H, j, cx, cy, acc):
    b = H.b
    b.path(j, 0, 0.6, _doc_lines(cx, cy - 270, 540, 640, 7), BLACK, 10, sfx="wood_high")
    for k, (dx, dy, rot, size, sfx) in enumerate(((-120, -460, -14, 88, "rim"), (120, -280, 10, 92, "rim"))):
        b.custom(j, k + 1, k + 1.3, _stamp(H, j, k + 1, "返工", cx + dx, cy + dy, size, rot), sfx=sfx, gain=0.8)
    b.custom(j, 3, 3.3, _stamp(H, j, 3, "返工", cx - 10, cy - 90, 112, -5), sfx="tom", gain=0.8)
    _finish(H, j, cx, cy, "第三遍了", acc, size=150, ty=cy + 260, text_sfx="kick")


# ---------------------------------------------------------------- 02 拉动：活越堆越高，塌了

def pile(H, j, cx, cy, acc):
    b = H.b
    floor = cy + 40
    pieces = []                       # (宽, 高, 落下拍, 塌落方向, 塌落角)
    spec = [(420, 110, 0, -1, -70), (370, 105, 0, 1, 40), (390, 105, 1, -1, -35), (340, 100, 1, 1, 65),
            (360, 100, 2, -1, -55), (310, 95, 2, 1, 80)]
    y = floor
    for i, (w, h, k, d, ang) in enumerate(spec):
        pieces.append((w, h, k + (0.0 if i % 2 == 0 else 0.25), d, ang, y, (i * 37) % 23 - 11))
        y -= h
    b.path(j, 0, 0.5, P((cx - 520, floor), (cx + 520, floor)), BLACK, 9, sfx="wood_low")
    t_fall = lambda: H.tb(j, 3)

    def fn(c, kk, T):
        tf = t_fall()
        lean = 0.0
        for k_ in (1, 2):
            lean += wobble(T - H.tb(j, k_), 2.0 + k_ * 1.5, 16, 4)
        for i, (w, h, k, d, ang, yb, off) in enumerate(pieces):
            t0 = H.tb(j, k)
            dt = T - t0
            if dt < 0:
                continue
            drop = (1 - ease_out(clamp01(dt / 0.22))) * 420
            x, yy, rot = cx + off, yb - drop, lean * (i + 1) * 0.35
            if T > tf:
                f = ease_in_out(clamp01((T - tf) / 0.45))
                x += d * f * (160 + i * 60)
                yy = lerp(yy, floor - 40 - (i % 3) * 30, f)
                rot = lerp(rot, ang, f)
            with K.at(c, x, yy - h / 2, rot):
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 10, 10, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 10, 10, wb.marker(BLACK, 8))
                c.drawLine(-w * 0.32, 0, w * 0.2, 0, wb.marker(BLUE if i % 2 else RED, 8))
        if T > tf:
            dt = T - tf
            if dt < 0.5:
                for s_ in (-1, 1):
                    K.burst(c, cx + s_ * 300, floor - 20, dt, wb.BLACK, 30, 120, 6, 6, 0.7)
        return None
    b.custom(j, 0, 3.5, fn)
    b.hit(j, 1, "wood_high", 0.8, "又压上两份")
    b.hit(j, 2, "wood_high", 0.8, "再压三份，开始晃")
    b.custom(j, 3, 3.3, lambda c, k, T: None, sfx="tom", gain=0.8)
    _finish(H, j, cx, cy, "越堆越乱", acc, ty=cy + 270)


# ---------------------------------------------------------------- 03 均衡：忙闲曲线一笔划出

def curve(H, j, cx, cy, acc):
    b = H.b
    x0, x1, base = cx - 500, cx + 500, cy + 40
    b.path(j, 0, 0.5, join(P((x0, cy - 560), (x0, base), (x1, base)),
                           P((x1 - 30, base - 22), (x1, base), (x1 - 30, base + 22))), BLACK, 9, sfx="wood_low")
    pts = []
    for i in range(121):
        u = i / 120
        y = base - 60 - 230 * (1 + math.sin(u * math.pi * 4 - math.pi / 2)) * (0.75 + 0.25 * math.sin(u * 7))
        pts.append((x0 + 30 + u * 940, y))
    b.path(j, 1, 2.6, P(*pts), RED, 13, sfx="shaker", gain=0.7)
    hi = min(pts[:60], key=lambda p: p[1])
    lo = max(pts[40:90], key=lambda p: p[1])
    b.custom(j, 2, 2.3, _pop(H, j, 2, "忙死", hi[0], hi[1] - 70, 66, RED), sfx="pop")
    b.custom(j, 3, 3.3, _pop(H, j, 3, "闲死", lo[0], base + 70, 66, BLUE))
    _finish(H, j, cx, cy, "忙一阵 闲一阵", acc, size=112, ty=cy + 250)


def _pop(H, j, k, s, x, y, size, color, font="hand"):
    H.note(s)

    def fn(c, kk, T):
        sc = pop_scale(T - H.tb(j, k))
        if sc > 0:
            with K.at(c, x, y, 0, sc):
                K.text(c, s, 0, 0, size, font, color, clamp01(sc * 2))
        return None
    return fn


# ---------------------------------------------------------------- 04 单件流：十个进度条全卡在一半

def bars(H, j, cx, cy, acc):
    b = H.b
    n, x0, w, hgt, gap, top = 10, cx - 500, 780, 44, 72, cy - 640
    targets = [0.47, 0.52, 0.44, 0.55, 0.49, 0.5, 0.46, 0.53, 0.48, 0.51]
    outl = join(*[rect(x0 + w / 2, top + i * gap, w, hgt, 22) for i in range(n)])
    b.path(j, 0, 0.7, outl, BLACK, 7, sfx="wood_high")
    H.note(*[f"{int(t * 100)}%" for t in targets])

    def fn(c, kk, T):
        for i, tg in enumerate(targets):
            t0 = H.tb(j, 0.6 + i * 0.12)
            f = ease_out(clamp01((T - t0) / max(0.1, H.tb(j, 2.6) - t0)))
            p = tg * f
            if T > H.tb(j, 3):
                p += 0.006 * math.sin((T - H.tb(j, 3)) * 30 + i) * math.exp(-(T - H.tb(j, 3)) * 3)
            if p <= 0:
                continue
            y = top + i * gap
            c.drawRoundRect(skia.Rect.MakeXYWH(x0 + 6, y - hgt / 2 + 6, (w - 12) * p, hgt - 12), 16, 16,
                            K.paint(GREEN if T < H.tb(j, 3) else ORANGE))
            K.text(c, f"{int(round(p * 100))}%", x0 + w + 80, y, 48, "sans_medium", BLACK, clamp01((T - t0) / 0.2))
        tb3 = H.tb(j, 3)
        if T > tb3:
            a = clamp01((T - tb3) / 0.15)
            xm = x0 + w * 0.5
            c.drawLine(xm, top - 50, xm, top + (n - 1) * gap + 50, wb.marker(RED, 8, a))
        return None
    b.custom(j, 0.6, 2.6, fn)
    b.hit(j, 1, "shaker", 0.6, "进度条往前走")
    b.hit(j, 2, "wood_low", 0.8, "越走越慢")
    _finish(H, j, cx, cy, "全卡在一半", acc, size=136, ty=cy + 250, text_sfx="kick")


# ---------------------------------------------------------------- 05 标准化：清单第 100 遍，漏了一步

def checklist(H, j, cx, cy, acc):
    b = H.b
    x, top, w, h = cx - 40, cy - 640, 640, 700
    steps = ["写正文", "加附件", "抄送", "检查", "发送"]
    H.note(*steps, "发邮件 · 第100遍")
    clip = join(rect(x, top + h / 2, w, h, 26), rect(x, top + 10, 200, 56, 14))
    b.path(j, 0, 0.6, clip, BLACK, 9, sfx="wood_high")
    b.text(j, 0.4, 0.9, "发邮件 · 第100遍", x, top + 100, 54, BLACK, font="sans_medium")
    ys = [top + 210 + i * 104 for i in range(5)]
    boxes = join(*[rect(x - 220, y, 56, 56, 10) for y in ys])
    b.path(j, 0.6, 1.0, boxes, BLACK, 7)
    for y, s in zip(ys, steps):
        b.text(j, 0.7, 1.0, s, x + 20, y, 56, BLACK)
    for k, idx in ((1, (0,)), (2, (2, 3, 4))):
        for n, i in enumerate(idx):
            b.path(j, k + n * 0.18, k + n * 0.18 + 0.2, check(x - 220, ys[i], 30), GREEN, 10,
                   sfx="pop" if n == 0 else None, gain=0.6)
    ring = skia.Path()
    ring.addOval(skia.Rect.MakeXYWH(x - 300, ys[1] - 70, 460, 140))
    b.path(j, 3, 3.4, ring, RED, 11)
    b.custom(j, 3, 3.3, _pop(H, j, 3, "漏了", x + 330, ys[1], 80, RED))
    _finish(H, j, cx, cy, "做了100遍还漏", acc, size=108, ty=cy + 260)


# ---------------------------------------------------------------- 06 目视化：便利贴飘走了

def sticky(H, j, cx, cy, acc):
    b = H.b
    notes = [("周报", -260, -470, -6, 0), ("报销", 170, -500, 5, 1), ("交合同", -230, -170, 4, 1), ("回电话", 200, -160, -5, 2)]
    H.note(*[n[0] for n in notes])
    b.path(j, 0, 0.5, rect(cx - 20, cy - 330, 1000, 640, 20), BLACK, 8)

    def card(s, x, y, rot, k, fly):
        def fn(c, kk, T):
            sc = pop_scale(T - H.tb(j, k))
            if sc <= 0:
                return None
            xx, yy, rr, a = x, y, rot, 1.0
            if fly:
                t3 = H.tb(j, 3)
                if T > t3:
                    f = clamp01((T - t3) / 1.2)
                    e = ease_in_out(f)
                    xx += 420 * e + 40 * math.sin(f * 9)
                    yy -= 360 * e - 60 * math.sin(f * 5)
                    rr += 160 * e
                    a = 1 - clamp01((f - 0.55) / 0.45)
                    sc *= 1 - 0.3 * e
            with K.at(c, xx, yy, rr, sc):
                c.drawRect(skia.Rect.MakeXYWH(-130, -110, 260, 220), K.paint("#FFE58A", a))
                c.drawRect(skia.Rect.MakeXYWH(-130, -110, 260, 220), wb.marker(BLACK, 6, a))
                c.drawRect(skia.Rect.MakeXYWH(-50, -128, 100, 34), K.paint("#9FD3F0", 0.8 * a))
                K.text(c, s, 0, 10, 60, "hand", BLACK, a)
            return None
        return fn
    sfx = {0: "pop", 1: "pop", 2: "pop"}
    seen = set()
    for s, dx, dy, rot, k in notes:
        b.custom(j, k, k + 0.3, card(s, cx + dx, cy + dy, rot, k, s == "回电话"),
                 sfx=None if k in seen else sfx[k], gain=0.7)
        seen.add(k)

    def gust(c, kk, T):
        dt = T - H.tb(j, 3)
        if 0 <= dt < 0.8:
            a = 1 - dt / 0.8
            for i in range(3):
                yy = cy - 230 + i * 50
                c.drawLine(cx + 40 + dt * 300, yy, cx + 260 + dt * 400, yy - 40, wb.marker(BLUE, 6, a))
        return None
    b.custom(j, 3, 3.8, gust, sfx="shaker", gain=0.7)
    _finish(H, j, cx, cy, "又漏了一件", acc, ty=cy + 250, text_sfx="kick")


# ---------------------------------------------------------------- 07 现地现物：门牌翻到“第3次会”

def doorsign(H, j, cx, cy, acc):
    b = H.b
    dx, dy = cx, cy - 300
    door = join(rect(dx, dy, 520, 700, 14), circle(dx + 190, dy + 40, 18), P((dx - 300, dy + 350), (dx + 300, dy + 350)))
    b.path(j, 0, 0.7, door, BLACK, 9, sfx="wood_low")
    signs = ["第1次会", "第2次会", "第3次会"]
    H.note(*signs, "会议中")

    def fn(c, kk, T):
        idx, sy = 0, 1.0
        for k in (1, 2):
            t0 = H.tb(j, k)
            if T >= t0:
                f = clamp01((T - t0) / 0.28)
                if f < 0.5:
                    sy, idx = 1 - 2 * f, k - 1
                else:
                    sy, idx = 2 * f - 1, k
        last = H.tb(j, 2) if T > H.tb(j, 2) else H.tb(j, 1)
        sw = wobble(T - last - 0.28, 4, 14, 4)
        x, y = dx, dy - 150
        c.drawLine(x - 80, y - 120, x, y - 200, wb.marker(BLACK, 5))
        c.drawLine(x + 80, y - 120, x, y - 200, wb.marker(BLACK, 5))
        c.drawCircle(x, y - 200, 8, K.paint(BLACK))
        with K.at(c, x, y, sw, 1.0, max(0.02, sy)):
            c.drawRoundRect(skia.Rect.MakeXYWH(-190, -80, 380, 160), 14, 14, K.paint("#FFFFFF"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-190, -80, 380, 160), 14, 14, wb.marker(RED if idx == 2 else BLACK, 8))
            K.text(c, signs[idx], 0, 0, 74, "hand", RED if idx == 2 else BLACK)
        return None
    b.custom(j, 0.6, 0.9, fn)
    b.hit(j, 1, "wood_high", 0.8, "翻牌：第2次会")
    b.hit(j, 2, "rim", 0.8, "翻牌：第3次会")
    b.custom(j, 3, 3.3, _pop(H, j, 3, "会议中", dx, dy + 120, 56, GRAY, "sans_medium"))
    _finish(H, j, cx, cy, "问题还在", acc, ty=cy + 260)


# ---------------------------------------------------------------- 08 五问：打下去一个，又冒出一个

def mole(H, j, cx, cy, acc):
    b = H.b
    hy = cy - 60
    xs = [cx - 370, cx, cx + 370]
    holes = []
    for x in xs:
        o = skia.Path()
        o.addOval(skia.Rect.MakeXYWH(x - 160, hy - 40, 320, 80))
        holes.append(o)
    b.path(j, 0, 0.6, join(*holes), BLACK, 9, sfx="wood_low")
    H.note("问题")
    ups = [(0, 1, 2), (2, 2, 3), (1, 3, 99)]          # (洞, 冒头拍, 被打/缩回拍)

    def fn(c, kk, T):
        for hole, ku, kd in ups:
            tu, td = H.tb(j, ku), H.tb(j, kd) if kd < 99 else 1e9
            if T < tu:
                continue
            up = ease_out_back(clamp01((T - tu) / 0.25))
            if T > td:
                up *= 1 - ease_in_out(clamp01((T - td) / 0.18))
            if up <= 0.01:
                continue
            x = xs[hole]
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(x - 220, hy - 700, x + 220, hy))
            yy = hy + 60 - 330 * up
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 125, yy - 160, 250, 400), 120, 120, K.paint("#D9B38C"))
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 125, yy - 160, 250, 400), 120, 120, wb.marker(BLACK, 9))
            for ex in (-42, 42):
                c.drawCircle(x + ex, yy - 70, 12, K.paint(BLACK))
            c.drawCircle(x, yy - 30, 18, K.paint(BLACK))
            K.text(c, "问题", x, yy + 70, 66, "hand", RED)
            c.restore()
        c.drawPath(join(*holes), wb.marker(BLACK, 9))
        # 锤子：第 2 拍砸左边的洞
        t2 = H.tb(j, 2)
        if T > t2 - 0.3:
            f = clamp01((T - (t2 - 0.3)) / 0.3)
            ang = lerp(-60, 10, ease_in_out(f)) if T < t2 else 10 - 10 * ease_out(clamp01((T - t2) / 0.4))
            a = 1 - clamp01((T - t2 - 0.9) / 0.3)
            px, py = xs[0] + 300, hy - 90
            with K.at(c, px, py, ang):
                c.drawRoundRect(skia.Rect.MakeXYWH(-300, -16, 300, 32), 10, 10, K.paint("#C89B63", a))
                c.drawRoundRect(skia.Rect.MakeXYWH(-300, -16, 300, 32), 10, 10, wb.marker(BLACK, 6, a))
                c.drawRoundRect(skia.Rect.MakeXYWH(-360, -70, 120, 140), 16, 16, K.paint(RED, a))
                c.drawRoundRect(skia.Rect.MakeXYWH(-360, -70, 120, 140), 16, 16, wb.marker(BLACK, 7, a))
            if T > t2 and T - t2 < 0.4:
                K.burst(c, xs[0], hy - 160, T - t2, ORANGE, 50, 190, 8, 8, 0.9)
        return None
    b.custom(j, 0.6, 0.9, fn)
    b.hit(j, 1, "bongo_high", 0.8, "左边冒头")
    b.hit(j, 2, "rim", 0.9, "锤子砸下 + 右边冒头")
    b.custom(j, 3, 3.3, lambda c, k, T: None, sfx="bongo_low", gain=0.8)
    _finish(H, j, cx, cy, "又冒出来了", acc, size=136, ty=cy + 220)


# ---------------------------------------------------------------- 09 共识：方案被盖“否”

def reject(H, j, cx, cy, acc):
    b = H.b
    x, y = cx, cy - 330
    chart = join(P((x - 120, y + 120), (x - 120, y + 20)), P((x - 40, y + 120), (x - 40, y - 30)),
                 P((x + 40, y + 120), (x + 40, y + 50)), P((x + 120, y + 120), (x + 120, y - 70)))
    b.path(j, 0, 0.6, join(rect(x, y, 440, 560, 18), P((x - 160, y + 150), (x + 170, y + 150))), BLACK, 9,
           sfx="wood_high")
    b.text(j, 0.3, 0.7, "方案", x, y - 200, 76, BLACK)
    b.path(j, 0.6, 1.0, chart, BLUE, 16)
    H.note("挺好？")

    def heads(c, kk, T):
        for i, hx in enumerate((cx - 380, cx + 380)):
            sc = pop_scale(T - H.tb(j, 1) - i * 0.08)
            if sc <= 0:
                continue
            with K.at(c, hx, y + 60, 0, sc):
                c.drawCircle(0, 0, 70, K.paint("#FFFFFF"))
                c.drawCircle(0, 0, 70, wb.marker(BLACK, 8))
                for ex in (-24, 24):
                    c.drawCircle(ex, -10, 7, K.paint(BLACK))
                frown = T > H.tb(j, 2)
                m = skia.Path()
                if frown:
                    m.addArc(skia.Rect.MakeXYWH(-26, 22, 52, 32), 200, 140)
                else:
                    m.moveTo(-22, 30)
                    m.lineTo(22, 30)
                c.drawPath(m, wb.marker(BLACK, 6))
                c.drawLine(-60, 130, 60, 130, wb.marker(BLACK, 8))
                c.drawLine(0, 70, 0, 130, wb.marker(BLACK, 8))
        return None
    b.custom(j, 1, 1.3, heads, sfx="pop", gain=0.7)
    b.custom(j, 1.4, 1.7, _pop(H, j, 1.4, "挺好？", cx - 380, y - 70, 56, GRAY))
    b.custom(j, 2, 2.3, _stamp(H, j, 2, "否", x + 20, y + 10, 210, -12), sfx="kick", gain=0.8)
    b.shots[j].shake = [(2, 9.0)]
    _finish(H, j, cx, cy, "一开会就被否", acc)


# ---------------------------------------------------------------- 10 反省：跑步机上原地跑

def treadmill(H, j, cx, cy, acc):
    b = H.b
    by = cy + 20
    frame = join(P((cx - 420, by), (cx + 380, by)), P((cx - 420, by + 50), (cx + 380, by + 50)),
                 circle(cx - 420, by + 25, 25), circle(cx + 380, by + 25, 25),
                 P((cx + 330, by), (cx + 430, by - 520)), P((cx + 370, by - 520), (cx + 500, by - 520)))
    b.path(j, 0, 0.6, frame, BLACK, 9, sfx="wood_low")
    H.note("0米")

    def fn(c, kk, T):
        t1 = H.tb(j, 1)
        ph = max(0.0, T - t1) * 2.6
        # 履带上的刻线往后走
        for i in range(9):
            u = ((i / 9) - ph * 0.35) % 1
            xx = cx - 400 + u * 760
            c.drawLine(xx, by + 8, xx - 20, by + 42, wb.marker(BLACK, 4, 0.7))
        sc = pop_scale(T - t1)
        if sc <= 0:
            return None
        s = 1.0
        x, y0 = cx - 40, by - 6
        c.save()
        c.translate(x, y0)
        c.scale(1.3, 1.3)
        c.translate(-x, -y0)
        bob = -abs(math.sin(ph * math.pi)) * 22
        hy = y0 - 300 * s + bob
        hip = (x, y0 - 130 * s + bob)
        sw = math.sin(ph * math.pi)
        with K.at(c, x, y0, 0, sc):
            c.translate(-x, -y0)
            c.drawCircle(x + 14, hy, 44 * s, K.paint("#FFFFFF"))
            c.drawCircle(x + 14, hy, 44 * s, wb.marker(BLACK, 9))
            c.drawPath(P((x - 30, hy - 10), (x - 10, hy - 50), (x + 40, hy - 48), (x + 58, hy - 5)), wb.marker(BLACK, 7))
            for ex in (2, 30):
                c.drawCircle(x + ex, hy - 4, 4, K.paint(BLACK))
            c.drawLine(x + 2, hy + 22, x + 28, hy + 22, wb.marker(BLACK, 6))
            sh = (x + 6, hy + 75)
            c.drawLine(x + 10, hy + 44, hip[0], hip[1], wb.marker(BLACK, 10))
            for sg in (1, -1):
                k_ = sg * sw
                knee = (hip[0] + 55 * k_, hip[1] + 70)
                foot = (hip[0] + 95 * k_ - 20, y0 - 8 - 30 * max(0.0, -k_))
                c.drawPath(P(hip, knee, foot), wb.marker(BLACK, 10))
                elbow = (sh[0] - 50 * k_, sh[1] + 50)
                hand = (sh[0] - 20 * k_ + 30, sh[1] + 20)
                c.drawPath(P(sh, elbow, hand), wb.marker(BLACK, 10))
            t2 = H.tb(j, 2)
            if T > t2:
                for i, (dx_, dy_) in enumerate(((-70, -40), (80, -70))):
                    f = ((T - t2) * 1.4 + i * 0.5) % 1
                    c.drawCircle(x + 14 + dx_ * (1 + f * 0.4), hy + dy_ + f * 60, 10, K.paint(BLUE, 1 - f))
        c.restore()
        return None
    b.custom(j, 1, 1.3, fn, sfx="shaker", gain=0.6)

    def meter(c, kk, T):
        sc = pop_scale(T - H.tb(j, 2))
        if sc > 0:
            with K.at(c, cx + 430, by - 610, 6, sc):
                c.drawRoundRect(skia.Rect.MakeXYWH(-120, -60, 240, 120), 16, 16, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-120, -60, 240, 120), 16, 16, wb.marker(BLACK, 7))
                K.text(c, "0米", 0, 0, 76, "hand", RED)
        return None
    b.custom(j, 2, 2.3, meter, sfx="ding", gain=0.7)
    _finish(H, j, cx, cy, "忙了一天 还在原地", acc, size=104, ty=cy + 250)


# ---------------------------------------------------------------- 旧版：丰田模式四字（留作对照）

def title(H, j, cx, cy, acc):
    raise NotImplementedError("旧版四字开场在 common.Lesson.intro_title")


HOOKS = dict(stamp3=stamp3, pile=pile, curve=curve, bars=bars, checklist=checklist, sticky=sticky, doorsign=doorsign,
             mole=mole, reject=reject, treadmill=treadmill)


# ---------------------------------------------------------------- 11 浪费：表盘切成八块，一块块变灰

def clock8(H, j, cx, cy, acc):
    b = H.b
    x, y, r = cx - 40, cy - 290, 290
    H.note("浪费", "0")
    b.path(j, 0, 0.6, circle(x, y, r), BLACK, 11, sfx="wood_high")
    spokes = join(*[P((x, y), (x + r * math.cos(math.radians(-90 + 45 * i)), y + r * math.sin(math.radians(-90 + 45 * i))))
                    for i in range(8)])
    b.path(j, 0.3, 0.9, spokes, GRAY, 5)
    when = [1, 1, 1.25, 2, 2, 2.25, 3, 3]                 # 每块变灰的拍（第 1、2 拍各三块，第 3 拍最后两块）
    order = [0, 3, 6, 1, 4, 7, 2, 5]

    def fn(c, kk, T):
        for n, i in enumerate(order):
            dt = T - H.tb(j, when[n])
            if dt < 0:
                continue
            a = clamp01(dt / 0.12)
            sc = 1 + 0.12 * math.exp(-dt * 10)
            wedge = skia.Path()
            wedge.moveTo(x, y)
            wedge.arcTo(skia.Rect.MakeXYWH(x - r * sc + 10, y - r * sc + 10, 2 * r * sc - 20, 2 * r * sc - 20),
                        -90 + 45 * i, 45, False)
            wedge.close()
            c.drawPath(wedge, K.paint("#9AA0A8", 0.85 * a))
            c.drawPath(wedge, wb.marker(BLACK, 5, a))
        # 指针飞快地转
        ph = max(0.0, T - H.tb(j, 0)) * 300
        for ln, w, sp in ((r * 0.72, 12, 1.0), (r * 0.5, 16, 1 / 12)):
            ang = math.radians(-90 + ph * sp)
            c.drawLine(x, y, x + ln * math.cos(ang), y + ln * math.sin(ang), wb.marker(BLACK, w))
        c.drawCircle(x, y, 18, K.paint(BLACK))
        # 右上角计数器
        sc = pop_scale(T - H.tb(j, 2))
        if sc > 0:
            with K.at(c, cx + 420, cy - 560, 4, sc):
                c.drawRoundRect(skia.Rect.MakeXYWH(-110, -70, 220, 140), 18, 18, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-110, -70, 220, 140), 18, 18, wb.marker(BLACK, 7))
                K.text(c, "浪费", -40, 0, 46, "hand", GRAY)
                K.text(c, "0", 60, 0, 80, "hand", RED)
        return None
    b.custom(j, 0, 0.3, fn)
    b.hit(j, 1, "tom", 0.8, "三块变灰")
    b.hit(j, 2, "tom", 0.8, "又三块变灰 + 计数器")
    _finish(H, j, cx, cy, "白忙", acc, size=170, ty=cy + 230)


# ---------------------------------------------------------------- 12 整理整顿：电脑桌面图标堆满，弹出“最终版二”

def desktop(H, j, cx, cy, acc):
    b = H.b
    x, y, w, h = cx, cy - 300, 1000, 640
    b.path(j, 0, 0.6, join(rect(x, y, w, h, 22), P((x - 60, y + h / 2), (x - 90, y + h / 2 + 80)),
                           P((x + 60, y + h / 2), (x + 90, y + h / 2 + 80)),
                           P((x - 200, y + h / 2 + 80), (x + 200, y + h / 2 + 80))), BLACK, 10, sfx="wood_low")
    H.note("最终版二", "找不到")
    cols, rows = 9, 5
    cells = [(x - w / 2 + 70 + (i % cols) * 108, y - h / 2 + 75 + (i // cols) * 118) for i in range(cols * rows)]
    order = sorted(range(len(cells)), key=lambda i: (i * 7919) % 97)
    colors = ["#F2C14E", "#7FB2E5", "#F28C8C", "#8FD19E"]

    def fn(c, kk, T):
        n = 0
        for k_, upto in ((0.5, 8), (1, 22), (2, 45)):
            if T >= H.tb(j, k_):
                n = upto
        for m, i in enumerate(order[:n]):
            k_ = 0.5 if m < 8 else (1 if m < 22 else 2)
            sc = pop_scale(T - H.tb(j, k_) - (m % 7) * 0.03, 0.22)
            if sc <= 0:
                continue
            ix, iy = cells[i]
            with K.at(c, ix, iy, 0, sc):
                c.drawRoundRect(skia.Rect.MakeXYWH(-34, -40, 68, 60), 8, 8, K.paint(colors[i % 4]))
                c.drawRoundRect(skia.Rect.MakeXYWH(-34, -40, 68, 60), 8, 8, wb.marker(BLACK, 4))
                c.drawLine(-26, 36, 26, 36, wb.marker(GRAY, 5))
        # 鼠标乱窜
        t0 = H.tb(j, 1)
        if T > t0:
            u = (T - t0) * 2.2
            mx = x + 330 * math.sin(u * 2.3) * math.cos(u * 0.7)
            my = y + 200 * math.sin(u * 3.1 + 1)
            arrowp = P((mx, my), (mx, my + 56), (mx + 14, my + 42), (mx + 26, my + 66), (mx + 36, my + 60),
                       (mx + 24, my + 38), (mx + 42, my + 36), close=True)
            c.drawPath(arrowp, K.paint("#FFFFFF"))
            c.drawPath(arrowp, wb.marker(BLACK, 5))
        # 第 3 拍弹窗
        sc = slam_scale(T - H.tb(j, 3))
        if sc > 0:
            with K.at(c, x + 40, y - 20, -4, sc):
                c.drawRoundRect(skia.Rect.MakeXYWH(-250, -110, 500, 220), 16, 16, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-250, -110, 500, 220), 16, 16, wb.marker(RED, 8))
                c.drawRect(skia.Rect.MakeXYWH(-250, -110, 500, 50), K.paint(RED))
                K.text(c, "最终版二", 0, 30, 88, "hand", RED)
        return None
    b.custom(j, 0, 0.3, fn)
    b.hit(j, 1, "pop", 0.7, "一排排图标冒出来")
    b.hit(j, 2, "wood_high", 0.8, "图标堆满")
    b.custom(j, 3, 3.3, lambda c, k, T: None, sfx="rim", gain=0.8)
    _finish(H, j, cx, cy, "找不到", acc, size=160, ty=cy + 260)


# ---------------------------------------------------------------- 13 防错：邮件一封封飞出去，“附件呢？”

def mailfly(H, j, cx, cy, acc):
    b = H.b
    wx, wy = cx - 120, cy - 330
    b.path(j, 0, 0.5, join(rect(wx, wy, 760, 520, 18), P((wx - 380, wy - 180), (wx + 380, wy - 180))), BLACK, 9,
           sfx="wood_low")
    H.note("发送", "附件：无", "附件呢？")
    bx, by = wx + 230, wy + 170

    def env(c, x, y, rot, sc, a=1.0):
        with K.at(c, x, y, rot, sc):
            c.drawRect(skia.Rect.MakeXYWH(-90, -60, 180, 120), K.paint("#FFFFFF", a))
            c.drawRect(skia.Rect.MakeXYWH(-90, -60, 180, 120), wb.marker(BLUE, 6, a))
            c.drawPath(P((-90, -60), (0, 10), (90, -60)), wb.marker(BLUE, 6, a))

    def fn(c, kk, T):
        # 窗口里的几行字和空的回形针
        for i in range(3):
            c.drawLine(wx - 320, wy - 100 + i * 70, wx + (120 if i < 2 else -60), wy - 100 + i * 70, wb.marker(GRAY, 6))
        K.text(c, "附件：无", wx - 230, wy + 120, 44, "sans_medium", GRAY)
        clip = skia.Path()
        clip.addRoundRect(skia.Rect.MakeXYWH(wx - 340, wy + 95, 34, 64), 17, 17)
        p = K.paint(GRAY, 1, 5)
        p.setPathEffect(skia.DashPathEffect.Make([10, 8], 0))
        c.drawPath(clip, p)
        # 发送按钮：每拍按一下
        press = 0.0
        for k_ in (0, 1, 2):
            dt = T - H.tb(j, k_)
            if 0 <= dt < 0.25:
                press = 1 - dt / 0.25
        with K.at(c, bx, by, 0, 1 - 0.1 * press):
            c.drawRoundRect(skia.Rect.MakeXYWH(-110, -45, 220, 90), 45, 45, K.paint(BLUE))
            K.text(c, "发送", 0, 2, 50, "hand", "#FFFFFF")
        # 信封飞出
        for n, k_ in enumerate((0, 1, 2)):
            dt = T - H.tb(j, k_)
            if dt < 0 or dt > 1.4:
                continue
            f = ease_out(clamp01(dt / 1.0))
            ex = lerp(bx, cx + 420 - n * 60, f)
            ey = lerp(by, cy - 620 + n * 90, f) - math.sin(f * math.pi) * 120
            env(c, ex, ey, lerp(0, 25 + n * 10, f), lerp(0.5, 1.0, f), 1 - clamp01((dt - 1.0) / 0.4))
            if dt < 0.5:
                for i in range(3):
                    c.drawLine(ex - 120 - i * 10, ey + 40 + i * 25 - 40, ex - 220 - i * 10, ey + 60 + i * 25 - 40,
                               wb.marker(BLUE, 5, 1 - dt / 0.5))
        # 光标点在按钮上
        mx, my = bx + 40, by + 20 + 6 * press
        cur = P((mx, my), (mx, my + 56), (mx + 14, my + 42), (mx + 26, my + 66), (mx + 36, my + 60), (mx + 24, my + 38),
                (mx + 42, my + 36), close=True)
        c.drawPath(cur, K.paint("#FFFFFF"))
        c.drawPath(cur, wb.marker(BLACK, 5))
        # 第 3 拍：气泡“附件呢？”
        sc = pop_scale(T - H.tb(j, 3))
        if sc > 0:
            with K.at(c, cx + 330, cy + 10, 0, sc):
                c.drawRoundRect(skia.Rect.MakeXYWH(-200, -70, 400, 140), 40, 40, K.paint("#FFFFFF"))
                c.drawPath(wb.bubble(0, 0, 400, 140, -1), wb.marker(BLACK, 7))
                K.text(c, "附件呢？", 0, 0, 72, "hand", RED)
        return None
    b.custom(j, 0, 0.3, fn)
    b.hit(j, 1, "wood_high", 0.8, "又发出一封")
    b.hit(j, 2, "wood_high", 0.8, "再发一封")
    b.custom(j, 3, 3.3, lambda c, k, T: None, sfx="pop", gain=0.8)
    _finish(H, j, cx, cy, "又手滑了", acc, size=180, ty=cy + 250)


HOOKS.update(clock8=clock8, desktop=desktop, mailfly=mailfly)


# ---------------------------------------------------------------- 14 准备挪到前面：起跑灯一盏盏亮红，就是不变绿

def startlights(H, j, cx, cy, acc):
    b = H.b
    gy = cy - 450
    xs = [cx - 320, cx, cx + 320]
    labels = ["找文件", "倒水", "连网"]
    H.note(*labels)

    def icon(c, n, x, y):
        if n == 0:                                   # 文件夹
            c.drawPath(P((x - 90, y - 50), (x - 30, y - 50), (x - 10, y - 30), (x + 90, y - 30), (x + 90, y + 60),
                         (x - 90, y + 60), close=True), K.paint("#F2C14E"))
            c.drawPath(P((x - 90, y - 50), (x - 30, y - 50), (x - 10, y - 30), (x + 90, y - 30), (x + 90, y + 60),
                         (x - 90, y + 60), close=True), wb.marker(BLACK, 7))
        elif n == 1:                                 # 水杯
            c.drawPath(P((x - 55, y - 60), (x + 55, y - 60), (x + 42, y + 62), (x - 42, y + 62), close=True),
                       K.paint("#CFE3F8"))
            c.drawPath(P((x - 55, y - 60), (x + 55, y - 60), (x + 42, y + 62), (x - 42, y + 62), close=True),
                       wb.marker(BLACK, 7))
            c.drawLine(x - 48, y - 20, x + 48, y - 20, wb.marker(BLUE, 5))
        else:                                        # 网络信号 + 红斜杠
            for r in (30, 62, 94):
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(x - r, y + 50 - r, 2 * r, 2 * r), 225, 90)
                c.drawPath(arc, wb.marker(BLACK, 9))
            c.drawCircle(x, y + 50, 10, K.paint(BLACK))
            c.drawLine(x - 70, y + 60, x + 70, y - 60, wb.marker(RED, 10))

    def fn(c, kk, T):
        sc0 = pop_scale(T - H.tb(j, 0))
        if sc0 <= 0:
            return None
        with K.at(c, cx, gy, 0, sc0):
            c.translate(-cx, -gy)
            c.drawLine(cx - 520, gy - 170, cx + 520, gy - 170, wb.marker(BLACK, 14))
            for x in xs:
                c.drawLine(x, gy - 170, x, gy - 120, wb.marker(BLACK, 10))
                c.drawRoundRect(skia.Rect.MakeXYWH(x - 120, gy - 120, 240, 240), 34, 34, K.paint("#3B3F48"))
                c.drawRoundRect(skia.Rect.MakeXYWH(x - 120, gy - 120, 240, 240), 34, 34, wb.marker(BLACK, 8))
        for n, x in enumerate(xs):
            dt = T - H.tb(j, n)
            on = dt >= 0
            c.drawCircle(x, gy, 82, K.paint(RED if on else "#5A5F68"))
            c.drawCircle(x, gy, 82, wb.marker(BLACK, 6))
            if on:
                c.drawCircle(x, gy, 82 + 40 * math.exp(-dt * 6), K.paint(RED, 0.25 * math.exp(-dt * 3), blur=18))
                sc = pop_scale(dt)
                with K.at(c, x, cy - 180, wobble(dt, 6, 16, 5), sc):
                    c.translate(-x, -(cy - 180))
                    icon(c, n, x, cy - 180)
                    K.text(c, labels[n], x, cy - 40, 58, "hand", BLACK)
        return None
    b.custom(j, 0, 0.3, fn, sfx="tom", gain=0.8)
    b.hit(j, 1, "tom", 0.8, "第二盏红灯")
    b.hit(j, 2, "tom", 0.85, "第三盏红灯")
    _finish(H, j, cx, cy, "还没开始", acc, size=150, ty=cy + 250)


# ---------------------------------------------------------------- 15 一页纸：幻灯片一摞摞往上叠，30 页

def slides(H, j, cx, cy, acc):
    b = H.b
    px, py = cx - 70, cy - 120
    H.note("10页", "20页", "30页")
    b.path(j, 0, 0.4, P((cx - 500, py + 40), (cx + 380, py + 40)), BLACK, 9)

    def slide(c, x, y, n, a=1.0):
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 260, y - 150, 520, 150), 8, 8, K.paint("#FFFFFF", a))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 260, y - 150, 520, 150), 8, 8, wb.marker(BLACK, 5, a))
        col = (BLUE, RED, GREEN, ORANGE)[n % 4]
        for i in range(4):
            h = 20 + ((n * 7 + i * 13) % 5) * 18
            c.drawRect(skia.Rect.MakeXYWH(x - 220 + i * 46, y - 24 - h, 30, h), K.paint(col, a))
        for i in range(3):
            c.drawLine(x + 10, y - 115 + i * 34, x + 220 - (i % 2) * 60, y - 115 + i * 34, wb.marker(GRAY, 5, a))

    def fn(c, kk, T):
        n_on = 0
        for k_ in (0, 1, 2):
            if T >= H.tb(j, k_):
                n_on = (k_ + 1) * 10
        for n in range(n_on):
            k_ = n // 10
            dt = T - H.tb(j, k_) - (n % 10) * 0.035
            if dt < 0:
                continue
            drop = (1 - ease_out(clamp01(dt / 0.18))) * 300
            sway = wobble(T - H.tb(j, 2), 1.5, 14, 4) * (n / 30) if T > H.tb(j, 2) else 0.0
            x = px + ((n * 37) % 23 - 11) + sway * 8
            y = py + 40 - n * 17 - drop
            with K.at(c, x, y, ((n * 53) % 9 - 4) * 0.6 + sway):
                c.translate(-x, -y)
                slide(c, x, y, n)
        if n_on:
            k_ = n_on // 10 - 1
            sc = slam_scale(T - H.tb(j, k_))
            with K.at(c, cx + 400, cy - 640 + 60, 6, max(sc, 0.0)):
                c.drawRoundRect(skia.Rect.MakeXYWH(-120, -62, 240, 124), 18, 18, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-120, -62, 240, 124), 18, 18, wb.marker(RED, 7))
                K.text(c, f"{n_on}页", 0, 2, 72, "hand", RED)
        return None
    b.custom(j, 0, 0.3, fn, sfx="wood_high", gain=0.8)
    b.hit(j, 1, "wood_high", 0.8, "又叠上十页")
    b.hit(j, 2, "wood_low", 0.85, "叠到三十页，晃了晃")
    _finish(H, j, cx, cy, "结论呢？", acc, size=150, ty=cy + 250)


# ---------------------------------------------------------------- 16 教人：新人头顶的问号一个接一个

def qmarks(H, j, cx, cy, acc):
    from fengtian.scenekit import draw_zhou
    from fengtian.common import draw_li
    b = H.b
    fy = cy + 40
    lx, zx, s = cx - 260, cx + 230, 0.95
    H.note("第1遍", "第2遍", "第3遍", "？")
    spots = [(zx - 120, fy - 450), (zx + 60, fy - 520), (zx + 210, fy - 420)]

    def fn(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        t3 = H.tb(j, 3)
        palm = T >= t3
        hy = fy - 290 * s
        with K.at(c, cx, fy, 0, sc):
            c.translate(-cx, -fy)
            if palm:
                draw_li(c, lx, fy, s, "sad", rh=(lx + 10, hy - 20))
            else:
                n = sum(1 for k_ in (0, 1, 2) if T >= H.tb(j, k_))
                wav = math.sin((T - H.tb(j, 0)) * 14) * 30
                draw_li(c, lx, fy, s, "flat", rh=(lx + 120, hy + 40 + wav))
            draw_zhou(c, zx, fy, s, mood="o" if T >= H.tb(j, 1) else "flat")
        for n, (x, y) in enumerate(spots):
            dt = T - H.tb(j, n)
            if dt < 0:
                continue
            g = pop_scale(dt)
            with K.at(c, x, y, wobble(dt, 10, 14, 4) + (n - 1) * 10, g):
                K.text(c, "？", 0, 0, 120 + n * 20, "black", RED)
            bs = pop_scale(dt - 0.05)
            with K.at(c, lx - 30, fy - 520 - n * 0, 0, bs if n == sum(1 for k_ in (0, 1, 2) if T >= H.tb(j, k_)) - 1
                      else 0.0):
                c.drawRoundRect(skia.Rect.MakeXYWH(-120, -55, 240, 110), 40, 40, K.paint("#FFFFFF"))
                c.drawPath(wb.bubble(0, 0, 240, 110, 1), wb.marker(BLACK, 7))
                K.text(c, f"第{n + 1}遍", 0, 0, 58, "hand", BLACK)
        return None
    b.custom(j, 0, 0.3, fn, sfx="pop", gain=0.75)
    b.hit(j, 1, "pop", 0.8, "第二个问号")
    b.hit(j, 2, "bongo_low", 0.85, "第三个问号")
    _finish(H, j, cx, cy, "又错了", acc, size=160, ty=cy + 250)


HOOKS.update(startlights=startlights, slides=slides, qmarks=qmarks)


# ---------------------------------------------------------------- 17 合作伙伴：一条链子逐拍绷紧，第四拍断开一节

def chain(H, j, cx, cy, acc):
    from fengtian.scenekit import draw_wang
    b = H.b
    y = cy - 260
    lx, rx = cx - 430, cx + 430
    n = 11
    H.note()

    def link(c, x, y_, rot, color, w=10, alpha=1.0):
        with K.at(c, x, y_, rot):
            c.drawOval(skia.Rect.MakeXYWH(-46, -24, 92, 48), wb.marker(color, w, alpha))

    def fn(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        tight = sum(1 for k_ in (0, 1, 2) if T >= H.tb(j, k_))
        dt3 = T - H.tb(j, 3)
        broke = dt3 >= 0
        sag = (70, 30, 6, 0)[tight] if tight < 3 else 0
        pull = (0, 30, 60, 80)[tight]
        fall = ease_out(clamp01(dt3 / 0.35)) if broke else 0.0
        with K.at(c, cx, y, 0, sc):
            c.translate(-cx, -y)
            # 两端的人：左边小李往左拽，右边合作方往右拽；断开后两人往后一仰
            back = 40 * fall
            lxp, rxp = lx - pull * 0.5 - back, rx + pull * 0.5 + back
            hy = y + 260 - 290 * 0.8
            draw_li(c, lxp - 90, y + 260, 0.8, "o" if broke else ("sad" if tight >= 2 else "flat"),
                    rh=(lxp - 10, y), lh=(lxp - 30, y + 10))
            draw_wang(c, rxp + 90, y + 260, 0.8, lh=(rxp + 10, y), rh=(rxp + 30, y + 10), mood="o" if broke else "flat")
            mid = n // 2
            for i in range(n):
                u = i / (n - 1)
                x = lerp(lxp, rxp, u)
                yy = y + sag * math.sin(math.pi * u)
                rot = 0 if i % 2 == 0 else 0
                shake = wobble(T - H.tb(j, 2), 4, 40, 6) if tight >= 3 and not broke else 0.0
                if broke and i == mid:
                    # 断开的那一节：裂成两半飞开
                    for sgn in (-1, 1):
                        with K.at(c, x + sgn * 60 * fall, yy + 120 * fall * fall, sgn * 40 * fall):
                            arc = skia.Path()
                            arc.addArc(skia.Rect.MakeXYWH(-52, -28, 104, 56), 90 if sgn < 0 else 270, 180)
                            c.drawPath(arc, wb.marker(RED, 11))
                    continue
                dx = 0.0
                if broke:
                    dx = (-1 if i < mid else 1) * 70 * fall
                color = RED if (tight >= 2 and abs(i - mid) <= 1) else BLACK
                if i % 2:
                    c.drawRoundRect(skia.Rect.MakeXYWH(x - 50 + dx, yy - 9 + shake, 100, 18), 9, 9, K.paint(GRAY))
                    c.drawRoundRect(skia.Rect.MakeXYWH(x - 50 + dx, yy - 9 + shake, 100, 18), 9, 9, wb.marker(color, 7))
                else:
                    c.drawOval(skia.Rect.MakeXYWH(x - 52 + dx, yy - 28 + shake, 104, 56), wb.marker(color, 11))
            # 绷紧的受力线
            if tight >= 1 and not broke:
                for k_ in range(tight):
                    a = 0.5 + 0.25 * k_
                    for sgn in (-1, 1):
                        c.drawLine(cx + sgn * (140 + 30 * k_), y - 70 - 20 * k_, cx + sgn * (200 + 30 * k_),
                                   y - 110 - 20 * k_, wb.marker(GRAY, 6, a))
            if T >= H.tb(j, 2) and not broke:
                c.drawPath(P((cx - 14, y - 40), (cx + 6, y - 12), (cx - 8, y + 12), (cx + 12, y + 40)), wb.marker(RED, 6))
        if broke:
            for i in range(10):
                a = math.radians(i * 36 + 10)
                d = 60 + 220 * ease_out(clamp01(dt3 / 0.5))
                al = 1 - clamp01((dt3 - 0.3) / 0.5)
                if al > 0:
                    c.drawLine(cx + math.cos(a) * (d - 40), y + math.sin(a) * (d - 40), cx + math.cos(a) * d,
                               y + math.sin(a) * d, wb.marker(ORANGE, 7, al))
        return None
    b.custom(j, 0, 0.3, fn, sfx="wood_low", gain=0.75)
    b.hit(j, 1, "tom", 0.8, "链子拉紧")
    b.hit(j, 2, "rim", 0.85, "中间一节裂开")
    _finish(H, j, cx, cy, "掉链子", acc, size=170, ty=cy + 240)


# ---------------------------------------------------------------- 18 新工具：手机上应用图标一个个蹦出来，第四拍全部变灰

def apps(H, j, cx, cy, acc):
    b = H.b
    px, py = cx + 160, cy - 260
    pw, ph = 420, 720
    names = ["新系统", "协作", "助手"]
    H.note(*names)
    cols = ["#5B8DEF", "#F28C5B", "#7BC67E"]

    def icon(c, x, y, n, gray):
        col = "#9AA0A8" if gray else cols[n]
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 70, y - 70, 140, 140), 34, 34, K.paint(col))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 70, y - 70, 140, 140), 34, 34, wb.marker(BLACK, 6))
        if n == 0:
            c.drawRect(skia.Rect.MakeXYWH(x - 36, y - 30, 72, 56), wb.marker("#FFFFFF", 7))
            c.drawLine(x - 36, y - 10, x + 36, y - 10, wb.marker("#FFFFFF", 6))
        elif n == 1:
            c.drawCircle(x - 18, y - 6, 18, wb.marker("#FFFFFF", 7))
            c.drawCircle(x + 20, y + 8, 18, wb.marker("#FFFFFF", 7))
        else:
            c.drawPath(P((x, y - 38), (x + 12, y - 10), (x + 40, y), (x + 12, y + 10), (x, y + 38), (x - 12, y + 10),
                         (x - 40, y), (x - 12, y - 10), close=True), K.paint("#FFFFFF"))
        K.text(c, names[n], x, y + 110, 44, "hand", GRAY if gray else BLACK)

    def fn(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        gray = T >= H.tb(j, 3)
        with K.at(c, px, py, 0, sc):
            c.translate(-px, -py)
            c.drawRoundRect(skia.Rect.MakeXYWH(px - pw / 2, py - ph / 2, pw, ph), 50, 50, K.paint("#3B3F48"))
            c.drawRoundRect(skia.Rect.MakeXYWH(px - pw / 2, py - ph / 2, pw, ph), 50, 50, wb.marker(BLACK, 8))
            c.drawRoundRect(skia.Rect.MakeXYWH(px - pw / 2 + 22, py - ph / 2 + 60, pw - 44, ph - 120), 18, 18,
                            K.paint("#FFFFFF"))
            # 小李在手机左边，越来越累
            n_on = sum(1 for k_ in (0, 1, 2) if T >= H.tb(j, k_))
            draw_li(c, cx - 330, cy + 100, 0.95, "sad" if gray else ("o" if n_on >= 2 else "flat"),
                    rh=(px - pw / 2 - 20, py + 40 + 8 * math.sin(T * 9)), squash=0.92 if gray else 1.0)
        for n in range(3):
            dt = T - H.tb(j, n)
            if dt < 0:
                continue
            x, y = px, py - 230 + n * 220
            g = pop_scale(dt)
            hop = -60 * math.sin(math.pi * clamp01(dt / 0.3)) if dt < 0.3 else 0.0
            with K.at(c, x, y + hop, wobble(dt, 8, 18, 5), g):
                c.translate(-x, -y)
                icon(c, x, y - 30, n, gray)
        if gray:
            dt = T - H.tb(j, 3)
            for n in range(3):
                x, y = px + 110, py - 300 + n * 220
                g = pop_scale(dt - 0.04 * n)
                if g > 0:
                    with K.at(c, x, y, 0, g):
                        c.drawCircle(0, 0, 26, K.paint(RED))
                        K.text(c, "99", 0, 2, 26, "sans_medium", "#FFFFFF")
        return None
    b.custom(j, 0, 0.3, fn, sfx="pop", gain=0.75)
    b.hit(j, 1, "pop", 0.8, "第二个图标蹦出")
    b.hit(j, 2, "bongo_high", 0.85, "第三个图标蹦出")
    _finish(H, j, cx, cy, "又一个", acc, size=170, ty=cy + 260)


# ---------------------------------------------------------------- 19 长期：“考核”大闹钟追着小李跑，远处路标“以后”一闪

def alarm(H, j, cx, cy, acc):
    b = H.b
    gy = cy + 80
    H.note("考核", "以后")

    def clock(c, x, y, r, T, ring):
        c.drawCircle(x, y, r, K.paint("#FFFFFF"))
        c.drawCircle(x, y, r, wb.marker(BLACK, 10))
        for sgn in (-1, 1):
            bx, by = x + sgn * r * 0.62, y - r * 0.86
            c.drawCircle(bx, by, r * 0.26, K.paint("#F2C14E"))
            c.drawCircle(bx, by, r * 0.26, wb.marker(BLACK, 7))
            c.drawLine(x + sgn * r * 0.55, y + r * 0.8, x + sgn * r * 0.75, y + r * 1.08, wb.marker(BLACK, 10))
        a = T * 7
        c.drawLine(x, y, x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6, wb.marker(RED, 9))
        c.drawLine(x, y, x, y - r * 0.4, wb.marker(BLACK, 11))
        K.text(c, "考核", x, y + r * 0.45, r * 0.32, "hand", RED)
        if ring:
            for sgn in (-1, 1):
                for k_ in range(2):
                    rr = r * (1.25 + 0.18 * k_)
                    arc = skia.Path()
                    arc.addArc(skia.Rect.MakeXYWH(x - rr, y - rr, 2 * rr, 2 * rr), (-60 if sgn > 0 else 200) + 0, 40)
                    c.drawPath(arc, wb.marker(GRAY, 6))

    def fn(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        c.drawLine(cx - 600, gy, cx + 600, gy, wb.marker(GRAY, 6))
        steps = sum(1 for k_ in (0, 1, 2) if T >= H.tb(j, k_))
        t0 = H.tb(j, 0)
        # 每拍往右跑一步，闹钟紧跟
        x_li = cx - 40 + 90 * steps - 90 + 90 * ease_out(clamp01((T - H.tb(j, steps - 1)) / 0.25))
        ph = (T - t0) * 3.2
        bob = -abs(math.sin(ph * math.pi)) * 20
        with K.at(c, cx, gy, 0, sc):
            c.translate(-cx, -gy)
            draw_li(c, x_li, gy + bob, 0.85, "o", lh=(x_li - 80, gy - 200 + 30 * math.sin(ph * math.pi)),
                    rh=(x_li + 80, gy - 200 - 30 * math.sin(ph * math.pi)))
            for i in range(3):
                c.drawLine(x_li - 110 - i * 30, gy - 220 + i * 50, x_li - 170 - i * 30, gy - 220 + i * 50,
                           wb.marker(GRAY, 6, 0.7))
            xc = x_li - 330
            clock(c, xc, gy - 230 + wobble(T - t0, 10, 30, 0.0) * 0.5, 150, T, True)
        # 第 3 拍远处路标一闪
        dt = T - H.tb(j, 3)
        if dt >= 0:
            fl = 0.35 + 0.65 * abs(math.cos(dt * 9)) * math.exp(-dt * 2.5) if dt < 1.2 else 0.35
            sx, sy = cx + 470, gy
            c.drawLine(sx, sy, sx, sy - 260, wb.marker(GRAY, 9, fl))
            c.drawPath(P((sx - 80, sy - 360), (sx + 70, sy - 360), (sx + 110, sy - 310), (sx + 70, sy - 260),
                         (sx - 80, sy - 260), close=True), K.paint("#FFFFFF", fl))
            c.drawPath(P((sx - 80, sy - 360), (sx + 70, sy - 360), (sx + 110, sy - 310), (sx + 70, sy - 260),
                         (sx - 80, sy - 260), close=True), wb.marker(GREEN, 7, fl))
            K.text(c, "以后", sx, sy - 310, 56, "hand", GREEN, fl)
        return None
    b.custom(j, 0, 0.3, fn, sfx="tom", gain=0.8)
    b.hit(j, 1, "tom", 0.8, "又跑一步")
    b.hit(j, 2, "bongo_low", 0.85, "闹钟追上来")
    _finish(H, j, cx, cy, "先顾眼前", acc, size=150, ty=cy + 260)


HOOKS.update(chain=chain, apps=apps, alarm=alarm)
