"""《丰田模式》样片 v2：慢速讲解版开头钩子（约 26 秒），音色 B（zv_yunjian），不接频道片尾。

用户反馈：语速和画面切换都要放慢，“不要还没看清就切换了”。照 CLAUDE.md「白板手绘节奏」放慢：
- 4 屏，一屏一件事：痛点（返工圈）→ 丰田做法（看到毛病就拉绳）→ 拉绳之后（组长赶来，修不好才停线）→ 结尾钩子追问；
- 每屏 5.9–7.4 秒，旁白讲完、画完后再停 1.5 秒以上才切；切屏镜头移动 1.1 秒缓入缓出，屏内不推拉；
- 元素约一拍一个逐个画出；切屏都在实测半小节线上；拉绳 = 音乐 drop（实测第 32 拍）。
- 旁白：ZipVoice zv_yunjian，提示语速 0.95、去噪 8 步，逗号处补到约 0.25 秒、句间约 0.5 秒，整体约 4 字/秒。
- 混音：配乐比人声低约 15 dB，旁白处再闪避；整体 -14 LUFS，真峰值 ≤ -1 dBTP。

书中观点为转述：Jeffrey K. Liker, The Toyota Way（2004）原则 5——发现问题就停下来解决，一次做对。
丰田生产线上工人发现异常可以拉安灯绳：先亮灯叫组长来处理，当场处理不好，整条线才停下。
“返工第三遍”为打工人场景示意，不是书中数据。

用法：python3 -m fengtian.sample_v2 [--sheet] [--asr 模型目录]   → out/fengtian/sample_v2.mp4
"""

import math
import subprocess
import sys
import tempfile
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import skia
import soundfile as sf
from scipy.ndimage import minimum_filter1d, uniform_filter1d

from adler import core, fx
from adler import kit as K
from engine import audio, bgm, gfx, perc, wording
from engine.gfx import clamp01, ease_in_out, ease_out
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, GREEN, RED, Board, P, arrow, book, check, circle, cross, desk, doc, face,
                               join, rect)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "fengtian"
VOICE, PROMPT_SPEED, STEPS = "zv_yunjian", 0.95, 8
COMMA, PERIOD = 0.25, 0.5
ACC = "#C8102E"
YELLOW = "#E0A21B"
SCREENS = [(10, 22), (22, 36), (36, 48), (48, 59)]   # 每屏 [起拍, 止拍)（实测拍序号，半小节线）
S = core.BEATS[SCREENS[0][0]]["t"] - 0.15            # 成片 0 秒对应的配乐时刻
DROP = 32                                            # 音乐 drop：拉绳
MUSIC_DB, DUCK, SFX_DB = -12.5, 0.45, -9.0

core.SERIES.update(name="丰田模式", count="样片", prefix="丰田")

# 旁白：(整句, [字幕...])；字幕按逗号切开，与句内逗号一一对应
LINES = [
    ("同一个问题，返工第三遍了。", ["同一个问题", "【返工】第三遍了"]),
    ("补了又坏，坏了又补。", None),
    ("丰田偏偏反着来：", ["丰田偏偏【反着来】"]),
    ("工人看到毛病，就拉一下绳。", ["工人看到毛病", "就【拉】一下绳"]),
    ("组长马上赶来，当场修不好，整条线就停下。", ["组长马上赶来", "当场修不好", "整条线就【停下】"]),
    ("停线这么狠，怎么反倒少返工？", ["停线这么狠", "怎么反倒【少返工】？"]),
    ("往下看。", ["往下看"]),
]
LINES[1] = (LINES[1][0], ["补了又坏，坏了又补"])     # 9 字一条，逗号处仍补停顿

# ---------------------------------------------------------------- 白板

b = Board(size=(2400, 3400))
VA = (1100, 800, 0.85)            # 屏 1：工位 + 返工圈
VB = (1100, 1750, 0.8)            # 屏 2：流水线 + 安灯绳
VB2 = (1300, 1830, 0.7)          # 屏 3：右移，组长赶来
VC = (1200, 1250, 0.55)           # 屏 4：拉远，返工圈与流水线同框

LC, LR = (1350, 820), 230
WK = (1530, 2150, 0.9)
LEAD = (1840, 2150, 0.9)
CORD_X, RAIL_Y, HANDLE_Y = 1600, 1470, 1850
LAMP = (1000, 1565, 50)
BELT = (470, 1380, 2000)


def car(x, y, s=1.0) -> skia.Path:
    return join(P((x - 85 * s, y - 20 * s), (x - 85 * s, y - 55 * s), (x - 45 * s, y - 60 * s), (x - 25 * s, y - 95 * s),
                  (x + 35 * s, y - 95 * s), (x + 55 * s, y - 60 * s), (x + 85 * s, y - 52 * s), (x + 85 * s, y - 20 * s),
                  close=True),
                circle(x - 48 * s, y - 16 * s, 17 * s), circle(x + 48 * s, y - 16 * s, 17 * s))


def worker_body(x, y, s) -> skia.Path:
    """工人：头、身体、腿、左臂、安全帽（右臂单独画，跟着安灯绳动）。"""
    hy = y - 290 * s
    sh = hy + 80 * s
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)),
                P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)), P((x - 70 * s, hy + 170 * s), (x, sh)),
                rect(x, hy - 52 * s, 100 * s, 22 * s, 8 * s))


def tb(j, k):
    return b.t_of(j, k)


def t_drop():
    return core.BEATS[DROP]["t"]


def t_stop():
    return tb(2, 7)


def pull_dy(T):
    return 48 * ease_in_out(clamp01((T - (t_drop() - 0.12)) / 0.12))


def loop_fn(c, k, T):
    """返工圈：第 2 拍描出，第 4 拍起慢慢转，屏 4 被剪断那一拍停转变淡。"""
    t0, t1 = tb(0, 2), tb(0, 2.9)
    ts, tc = tb(0, 4), tb(3, 5)
    p = clamp01((T - t0) / (t1 - t0))
    spin = 0.0
    if T > ts:
        dt = min(T, tc) - ts
        spin = 120 * (dt - 0.4 * (1 - math.exp(-dt / 0.4)))
    alpha = 1.0 - 0.55 * ease_out(clamp01((T - tc) / 0.25))
    x, y = LC
    tip = None
    for i in range(2):
        a0 = -90 + i * 180 + spin + 12
        sweep = 150 * p
        pa = skia.Path()
        pa.addArc(skia.Rect.MakeXYWH(x - LR, y - LR, 2 * LR, 2 * LR), a0, sweep)
        c.drawPath(pa, wb.marker(RED, 12, alpha))
        ae = math.radians(a0 + sweep)
        ex, ey = x + LR * math.cos(ae), y + LR * math.sin(ae)
        if p >= 1:
            tx, ty = -math.sin(ae), math.cos(ae)
            for d in (0.55, -0.55):
                hx = ex - 46 * (tx * math.cos(d) - ty * math.sin(d))
                hy = ey - 46 * (tx * math.sin(d) + ty * math.cos(d))
                c.drawLine(ex, ey, hx, hy, wb.marker(RED, 12, alpha))
        elif i == 1 or tip is None:
            tip = (ex, ey)
    return tip if p < 1 else None


def cars_fn(c, k, T):
    """传送带上三辆车慢慢向右走；第二辆车冒红“!”；整条线停下那一拍停住。"""
    t_in, t_mark = tb(1, 3), tb(1, 7)
    a = ease_out(clamp01((T - t_in) / 0.3))
    v, span = 60.0, 960.0
    te = min(T, t_stop())
    x0, x1, y = BELT
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y - 360, x1, y + 40))
    for i in range(3):
        cx = x0 + ((800 - x0) + (i - 1) * 320 + v * (te - t_mark)) % span
        if cx > x1 + 90:
            continue
        pth = car(cx, y - 25)
        c.drawPath(pth, wb.marker(BLACK, 8, a))
        if i == 1 and T >= t_mark:
            m = ease_out(clamp01((T - t_mark) / 0.2))
            c.drawPath(pth, K.paint(RED, 0.18 * m))
            with K.at(c, cx, y - 205 + 30 * (1 - m), 0, 0.6 + 0.4 * m):
                c.drawLine(0, -55, 0, 15, wb.marker(RED, 16, m))
                c.drawCircle(0, 48, 10, K.paint(RED, m))
    c.restore()
    return None


def arm_fn(c, k, T):
    x, y, s = WK
    hy = y - 290 * s
    sx, sy = x, hy + 80 * s
    hx, hyy = CORD_X, HANDLE_Y + 30 + pull_dy(T)
    p = clamp01(k)
    c.drawLine(sx, sy, sx + (hx - sx) * p, sy + (hyy - sy) * p, wb.marker(BLACK, 10))
    return (sx + (hx - sx) * p, sy + (hyy - sy) * p) if p < 1 else None


def cord_fn(c, k, T):
    dy = pull_dy(T)
    yb = RAIL_Y + (HANDLE_Y + dy - RAIL_Y) * clamp01(k)
    c.drawLine(CORD_X, RAIL_Y, CORD_X, yb, wb.marker(ACC, 7))
    if k >= 1:
        c.drawPath(rect(CORD_X, HANDLE_Y + 25 + dy, 34, 56, 10), wb.marker(ACC, 9))
        return None
    return CORD_X, yb


def lamp_fn(c, k, T):
    """安灯：拉绳那一帧亮黄灯（叫组长），整条线停下那一拍转红灯。"""
    if T < t_drop():
        return None
    red = T >= t_stop()
    col = RED if red else YELLOW
    t_on = t_stop() if red else t_drop()
    x, y, r = LAMP
    dt = T - t_on
    blink = 0.75 + 0.25 * math.cos((T - t_drop()) * 2 * math.pi / 1.07)
    c.drawCircle(x, y, r * 3.2, K.paint(col, 0.3 * blink, blur=40))
    c.drawCircle(x, y, r - 4, K.paint(col, 0.9 * blink))
    for i in range(8):
        ang = i / 8 * 2 * math.pi
        L = 30 + 18 * ease_out(clamp01(dt / 0.25))
        c.drawLine(x + math.cos(ang) * (r + 18), y + math.sin(ang) * (r + 18),
                   x + math.cos(ang) * (r + 18 + L), y + math.sin(ang) * (r + 18 + L), wb.marker(col, 7, blink))
    return None


def speed_lines(x, y) -> skia.Path:
    return join(*[P((x, y + i * 45), (x + 80 - i * 15, y + i * 45)) for i in range(3)])


x0, x1, by = BELT

# 屏 1（12 拍）：痛点——同一个问题返工第三遍，补了又坏
j = b.shot("", "打工人日常", view=VA, bars=4)
b.path(j, 0, 0.8, join(desk(780, 990, 380), wb.stick(600, 1140, 0.85, "hold")), sfx="wood_high")
b.path(j, 0.8, 0.95, face(600, 1140, 0.85, "sad"))
b.path(j, 1, 1.7, doc(*LC, 150, 190), BLACK, 9, sfx="pop")
b.custom(j, 2, 2.9, loop_fn, sfx="wood_high")
b.text(j, 3, 3.8, "第3遍", LC[0], 520, 92, RED, sfx="rim")
b.hit(j, 4, "shaker", 0.6, "返工圈开始转")
b.text(j, 6, 6.3, "补", 1030, 700, 76, GREEN, sfx="pop")
b.path(j, 6.3, 6.8, check(1030, 830, 42), GREEN, 11)
b.text(j, 7, 7.3, "坏", 1680, 700, 76, RED, sfx="pop")
b.path(j, 7.3, 7.8, cross(1680, 830, 38), RED, 11)

# 屏 2（14 拍）：丰田——工人看到毛病，就拉一下绳（拉绳 = drop，亮黄灯）
KD = DROP - SCREENS[1][0]
j = b.shot("", "丰田模式 · 书中做法", view=VB, bars=4, shake=[(KD, 16.0)], flashes=[(KD, 0.45)])
b.path(j, 0, 0.8, book(640, 1325, 230, 150), GREEN, 9, sfx="wood_low")
b.text(j, 1, 1.8, "丰田模式", 1020, 1325, 84, GREEN, sfx="pop")
b.path(j, 2, 2.8, join(rect((x0 + x1) / 2, by + 12, x1 - x0 + 40, 46, 20),
                       *[circle(xx, by + 12, 13) for xx in range(x0 + 40, x1, 110)]), sfx="wood_high")
b.custom(j, 3, 3.3, cars_fn, sfx="pop")
b.path(j, 5, 5.7, worker_body(*WK), sfx="wood_high")
b.path(j, 5.7, 5.85, face(WK[0], WK[1], WK[2], "flat"))
b.custom(j, 5.6, 5.95, arm_fn)
b.hit(j, 7, "rim", 0.8, "车上冒出红色“!”（毛病）")
b.path(j, 8, 8.5, join(P((x0, RAIL_Y), (1760, RAIL_Y)), P((LAMP[0], RAIL_Y), (LAMP[0], LAMP[1] - LAMP[2])),
                       circle(*LAMP)), BLACK, 9, sfx="wood_high")
b.custom(j, 8.5, 8.9, cord_fn)
b.custom(j, KD, KD + 1, lamp_fn, sfx="kick", gain=0.9)          # drop：拉绳，黄灯亮

# 屏 3（12 拍）：组长马上赶来，当场修不好，整条线就停下（转红灯）
j = b.shot("", "丰田模式 · 书中做法", view=VB2, bars=4, shake=[(7, 14.0)])
b.path(j, 0, 0.8, wb.stick(*LEAD, "hold"), sfx="wood_high")
b.path(j, 0.8, 0.95, face(*LEAD, "flat"))
b.text(j, 1, 1.5, "组长", LEAD[0], 1790, 64, BLACK, sfx="pop")
b.path(j, 2, 2.5, speed_lines(1950, 1960), BLACK, 8, sfx="wood_high")
b.text(j, 4, 4.4, "修", 1800, 1640, 120, BLACK, sfx="pop")
b.path(j, 5, 5.4, cross(1800, 1640, 80), RED, 13, sfx="rim")
b.text(j, 7, 7.4, "停！", 980, 1765, 150, RED, sfx="tom", gain=0.9)

# 屏 4（11 拍）：结尾钩子——拉远，停线指向返工圈，剪断循环，留问号
j = b.shot("", "接下来", view=VC, bars=4, shake=[(5, 12.0)])
b.path(j, 2, 2.8, arrow((1680, 1430), (1530, 1040), 0.18, 44), GREEN, 11, sfx="wood_high")
b.text(j, 3, 3.3, "？", 2060, 1180, 280, RED, sfx="pop")
b.path(j, 5, 5.25, P((1080, 560), (1640, 1100)), RED, 22, sfx="frame", gain=0.9)
b.path(j, 7, 7.3, arrow((2060, 1350), (2060, 1520), 0.0, 44), RED, 12, sfx="pop", gain=0.6)

# 时间轴：每屏按 SCREENS 的实测拍定起止（Board 镜头名义上 4 小节，只用于镜头移动 1.1 秒）
ep = core.Episode(1, "sample", "停线", "丰田模式样片", ACC, b.shots, refs=[])
for s, (k0, k1) in zip(b.shots, SCREENS):
    s.b0, s.t0, s.t1 = k0, core.bt(k0), core.bt(k1)
b.shots[0].t0 = S
b.attach(ep)
END = core.bt(SCREENS[-1][1]) - S


# ---------------------------------------------------------------- 旁白

def stretch(x, text):
    """逗号处补停顿到约 COMMA 秒：在预期位置 ±12% 内找最安静的 30ms 切开补静音。返回 (音频, 各逗号后新分句起点秒)。"""
    clauses = [c for c in text.rstrip("。：？！").split("，")]
    hz = [sum(1 for ch in cl if ch not in "。：？！【】") for cl in clauses]
    total_chars = sum(hz)
    hop = int(0.01 * audio.SR)
    starts, added, acc = [], 0, 0
    for ci in range(len(clauses) - 1):
        acc += hz[ci]
        frac = acc / total_chars
        n = len(x) // hop
        r = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1))
        r3 = np.convolve(r, np.ones(3) / 3, "same")
        orig_n = (len(x) - added) // hop
        center = int(frac * orig_n) + added // hop
        lo, hi = max(1, center - int(0.12 * orig_n)), min(n - 1, center + int(0.12 * orig_n))
        i = lo + int(np.argmin(r3[lo:hi]))
        quiet = r3 < r.max() * 10 ** (-32 / 20)
        a = i
        while a > 0 and quiet[a - 1]:
            a -= 1
        e = i
        while e < n and quiet[e]:
            e += 1
        have = (e - a) / 100 if quiet[i] else 0.0
        add = int(max(0.0, COMMA - have) * audio.SR)
        cut = i * hop
        f = int(0.008 * audio.SR)
        left, right = x[:cut].copy(), x[cut:].copy()
        left[-f:] *= np.linspace(1, 0, f)
        right[:f] *= np.linspace(0, 1, f)
        x = np.concatenate([left, np.zeros(add), right])
        added += add
        starts.append((cut + add) / audio.SR - min(0.05, have / 2))
    return x, starts


def narration():
    nar = audio.Narrator(VOICE, prompt_speed=PROMPT_SPEED)
    raw = [nar.generate(t, 1.0, STEPS) for t, _ in LINES]
    clips, inner = zip(*[stretch(x, t) for x, (t, _) in zip(raw, LINES)])
    d = [len(x) / audio.SR for x in clips]
    loc = lambda T: T - S
    st = [0.25, None, loc(b.shots[1].t0) + 0.45, loc(t_drop()) - d[3] - 0.03, loc(b.shots[2].t0) + 0.3,
          loc(b.shots[3].t0) + 0.3, None]
    st[1] = st[0] + d[0] + PERIOD
    st[6] = st[5] + d[5] + 0.4
    for i in range(1, len(st)):
        if st[i] < st[i - 1] + d[i - 1] + 0.3:
            raise ValueError(f"第 {i + 1} 句与上一句太近：{st[i]:.2f}s")
    caps, table = [], []
    for (text, pieces), s0, du, cuts in zip(LINES, st, d, inner):
        bounds = [s0] + ([s0 + c for c in cuts] if len(pieces) > 1 else [])
        if len(pieces) not in (1, len(cuts) + 1):
            raise ValueError(f"字幕条数与逗号不符：{text}")
        for bt_, cap in zip(bounds, pieces):
            caps.append([bt_, None, cap])
        table.append((text, s0, du))
    for i, cp in enumerate(caps):
        cp[1] = caps[i + 1][0] if i + 1 < len(caps) else None
    return list(zip(st, clips)), caps, table, raw


# ---------------------------------------------------------------- 画面

CAPS: list = []
DUR = END
_DUMMY = skia.Surface(8, 8).getCanvas()


def draw_caption(c, t):
    for t0, t1, cap in CAPS:
        if t0 <= t and (t1 is None or t < t1):
            break
    else:
        return
    k = clamp01((t - t0) / 0.2)
    size = 70
    segs = gfx.parse_marks(cap)
    total = sum(K.text_w(s, size, "serif") for s, _ in segs)
    x = core.W / 2 - total / 2
    y = core.CAP_Y + 8 * (1 - ease_out(k))
    for s, hi in segs:
        w = K.text_w(s, size, "serif")
        if hi:
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 6, y + size * 0.08, w + 12, size * 0.38), 8, 8,
                            K.paint(K.tint(ACC, 0.6), 0.85 * k))
        x += K.text(c, s, x, y, size, "serif", K.INK, k, "left")


def idle_tip(T):
    """手的停放位置：最近画完的那一笔的终点（逐帧独立求值，多进程渲染不跳手）。"""
    if tb(3, 5.25) <= T < tb(3, 7):
        return 2190, 1760              # 剪断之后手挪到右下角，让出问号
    best, tip = -1.0, None
    for it in b.items:
        t1 = b.t_of(it["j"], it["k1"])
        if t1 > T or t1 < best:
            continue
        if it["kind"] == "path":
            p = wb.partial(it["path"], 0.999)[1]
        elif it["kind"] == "text":
            p = (it["x"] + K.text_w(it["s"], it["size"], it["font"]) / 2, it["y"])
        else:
            p = it["fn"](_DUMMY, 0.999, t1 - 1e-3)
        if p is not None:
            best, tip = t1, p
    return tip


def frame(c, t):
    T = S + t
    b._last_tip = idle_tip(T)
    s = ep.shots[ep.shot_at(T)]
    g = core.G(c, ep, s, T - s.t0)
    wb.render_board(c, b, T)
    for kb, pk in s.flashes:
        a = fx.flash_alpha(g.since(kb), pk)
        if a > 0:
            c.drawPaint(K.paint("#FFFFFF", a))
    c.drawRect(skia.Rect.MakeLTRB(0, wb.CAP_TOP, core.W, wb.CAP_BOTTOM), K.paint("#FFFFFF", 0.82, blur=8))
    draw_caption(c, t)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, core.W, 318), K.paint("#FBFBF9", 1.0, blur=6))
    core.draw_header(c, ep, s, T, g)
    y, xa, xb = 300, 72, core.W - 72
    p = clamp01(t / DUR)
    K.seg(c, xa, y, xb, y, K.LINE, 4)
    K.seg(c, xa, y, xa + (xb - xa) * p, y, ACC, 4)


def _render(i):
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType,
                                                       skia.kPremul_AlphaType))
    frame(surf.getCanvas(), i / core.FPS)
    return surf.makeImageSnapshot().tobytes()


def still(t, path):
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType,
                                                       skia.kPremul_AlphaType))
    frame(surf.getCanvas(), t)
    surf.makeImageSnapshot().save(path, skia.kPNG)


# ---------------------------------------------------------------- 混音

def _lufs(x):
    import pyloudnorm
    return pyloudnorm.Meter(audio.SR).integrated_loudness(x)


def limiter(x, ceil_db=-2.0, look=0.004):
    ceil = 10 ** (ceil_db / 20)
    need = np.minimum(1.0, ceil / np.maximum(np.max(np.abs(x), axis=1), 1e-9))
    w = 2 * max(3, int(look * audio.SR)) + 1
    g = uniform_filter1d(minimum_filter1d(need, w), w)
    return x * np.minimum(g, minimum_filter1d(need, 3))[:, None]


def build_audio(voice_clips):
    n = int(DUR * audio.SR)
    v = np.zeros(n)
    for st, x in voice_clips:
        audio.place(v, x, st)
    v = audio.process_voice(v)
    voice = audio.pan(v, 0) * 1.41
    m0 = int(round(S * audio.SR))
    music = bgm.load()[m0: m0 + n].copy()
    fi, fo = int(0.3 * audio.SR), int(0.8 * audio.SR)
    music[:fi] *= np.linspace(0, 1, fi)[:, None]
    music[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    sfx = np.zeros((n, 2))
    events = []
    for k, s in enumerate(ep.shots):
        for beat, name, gain, note in s.all_hits():
            gi = s.b0 + int(round(beat))
            bt_ = core.BEATS[gi]
            name = core.resolve_sfx(name, bt_)
            clip = perc.sound(name) * core.SFX_LEVEL.get(name, 0.3) * gain
            t = bt_["t"] - S
            audio.place(sfx, audio.pan(clip, 0), t - perc.attack_ms(name) / 1000)
            fr = int(round(t * core.FPS))
            events.append(dict(shot=k + 1, beat=gi, t=t, sfx=name, note=note, frame=fr,
                               frame_err=round(t * core.FPS - fr, 2)))
    lv = _lufs(voice)
    music *= 10 ** ((lv + MUSIC_DB - _lufs(music)) / 20)
    sfx *= 10 ** ((lv + SFX_DB - _lufs(sfx)) / 20)
    music_d = music * (1 - DUCK * audio.duck_envelope(v))[:, None]
    mix = voice + music_d + sfx
    gain = 10 ** ((-14.0 - _lufs(mix)) / 20)
    stems = {"voice": voice * gain, "music": music_d * gain, "sfx": sfx * gain}
    mix = limiter(mix * gain)
    mix = limiter(mix * 10 ** ((-14.0 - _lufs(mix)) / 20))
    return mix.astype(np.float32), stems, events


# ---------------------------------------------------------------- 检查与输出

def wording_warnings():
    texts = [("旁白", t) for t, _ in LINES] + [("字幕", c) for _, ps in LINES for c in ps]
    texts += [(f"屏{it['j'] + 1}白板字", it["s"]) for it in b.items if it["kind"] == "text"]
    texts += [(f"屏{i + 1}标签", s.tag) for i, s in enumerate(b.shots)]
    out = []
    for where, s in texts:
        hits = wording.check(wording.gfx_plain(s))
        if hits:
            out.append(f"{where}“{s}”：{'、'.join(hits)}")
        if where == "字幕" and core.han(s) > 10:
            out.append(f"字幕“{s}”超过 10 字")
    return out


def screen_table(table):
    """每屏起止、最后一笔、最后一句结束、停住时长。"""
    rows = []
    for j, s in enumerate(b.shots):
        a, z = s.t0 - S, s.t1 - S
        if j == 0:
            a = 0.0
        last_stroke = max(b.t_of(it["j"], it["k1"]) - S for it in b.items
                          if it["j"] == j and it["kind"] in ("path", "text"))
        last_voice = max((st + du for _, st, du in table if a - 0.01 <= st < z), default=a)
        rows.append((j + 1, a, z, z - a, last_stroke, last_voice, z - max(last_stroke, last_voice)))
    return rows


def main():
    global CAPS
    OUT.mkdir(parents=True, exist_ok=True)
    for w in wording_warnings():
        print("文案警告：", w, file=sys.stderr)
    clips, CAPS, table, raw = narration()
    print(f"时长 {DUR:.2f}s，配乐 {S:.2f}–{S + DUR:.2f}s（drop 在 {t_drop() - S:.2f}s）")
    for text, st, du in table:
        hz = core.han(text)
        print(f"  旁白 {st:5.2f}–{st + du:5.2f}s  {du:.2f}s {hz / du:.2f}字/秒  {text}")
    for t0, t1, cap in CAPS:
        print(f"  字幕 {t0:5.2f}–{(t1 if t1 is not None else DUR):5.2f}s  {cap}")
    hz_all = sum(core.han(t) for t, _ in LINES)
    span = table[-1][1] + table[-1][2] - table[0][1]
    print(f"  整体语速：{hz_all} 字 / 首句起到末句止 {span:.2f}s = {hz_all / span:.2f} 字/秒；"
          f"纯语音 {hz_all / sum(len(x) for x in raw) * audio.SR:.2f} 字/秒")
    for r in screen_table(table):
        print(f"  屏{r[0]} {r[1]:5.2f}–{r[2]:5.2f}s 停留 {r[3]:.2f}s，最后一笔 {r[4]:.2f}s，旁白止 {r[5]:.2f}s，"
              f"画完讲完后停 {r[6]:.2f}s")
    if "--asr" in sys.argv:
        from fengtian.voice_audition import asr_check, edit
        res = asr_check(sys.argv[sys.argv.index("--asr") + 1], raw)
        for (t, _), a in zip(LINES, res):
            ref = "".join(ch for ch in t if ch not in "，。：？")
            print(f"  ASR {a}（原文 {ref}，差 {edit(ref, a)} 字）")
    if "--sheet" in sys.argv:
        for t in (4.8, 9.0, 12.5, 18.5, 22.0, 25.0):
            still(t, str(OUT / f"v2_sheet_{t:05.2f}.png"))
        return
    mix, stems, events = build_audio(clips)
    for e in events:
        print(f"  音效 {e['t']:5.2f}s 帧{e['frame']:3d}（偏差 {e['frame_err']:+.2f}） 拍{e['beat']} {e['sfx']} {e['note']}")
    for k, x in stems.items():
        sf.write(OUT / f"v2_{k}.wav", x.astype(np.float32), audio.SR, subtype="PCM_16")
    hop = int(0.05 * audio.SR)
    vr = np.sqrt(np.maximum(uniform_filter1d(stems["voice"][:, 0] ** 2, hop), 0))
    on = vr > 0.1 * vr.max()
    db = lambda x, m: 10 * np.log10(np.mean(x[m] ** 2) + 1e-12)
    print(f"  人声段：人声 {db(stems['voice'], on):.1f} dB，配乐 {db(stems['music'], on):.1f} dB；"
          f"无人声段配乐 {db(stems['music'], ~on):.1f} dB；积分响度 人声 {_lufs(stems['voice']):.1f} / "
          f"配乐 {_lufs(stems['music']):.1f} / 音效 {_lufs(stems['sfx']):.1f} LUFS")
    out = OUT / "sample_v2.mp4"
    n = int(round(DUR * core.FPS))
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "mix.wav")
        sf.write(wav, mix, audio.SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s",
               f"{core.W}x{core.H}", "-r", str(core.FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset",
               "medium", "-crf", "20", "-tune", "animation", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
               "-shortest", "-movflags", "+faststart", str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with get_context("fork").Pool(4) as pool:
            for buf in pool.imap(_render, range(n), chunksize=8):
                proc.stdin.write(buf)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
    print(out)


if __name__ == "__main__":
    main()
