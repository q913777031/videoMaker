"""《丰田模式》样片：约 11 秒的开头钩子（白板手绘 + AI 旁白），给整季定调用，不接频道片尾。

结构：打工人痛点（同一个问题返工第三遍，补了又坏）→ 书中反常识做法（谁看到毛病谁就拉绳，整条线停下）
→ 结尾钩子追问（停线怎么反倒少返工？往下看）。
- 画面：whiteboard 引擎的 Board / 描线 / 相机，3 个镜头（2 + 2 + 1 小节），镜头边界都在实测半小节线上；
- 旁白：engine.audio.Narrator 本地 ZipVoice（zv_yunxi，语速 1.0），每句单独合成，字幕按句内字数比例逐条同步；
- 卡点：拉绳停线一刻 = 音乐 drop（实测第 32 拍），“拉绳”一句的句尾正好落在 drop；其余音效都在实测拍点上；
- 混音：music/bgm.m4a 压在人声下面（基础 -12 dB，旁白处再闪避约 -5 dB），整体 -14 LUFS，真峰值 ≤ -1 dBTP。

书中观点为转述：Jeffrey K. Liker, The Toyota Way（2004）原则 5“建立立即停止以解决问题、一开始就重视质量的文化”，
丰田生产线上工人发现问题可以拉安灯绳（andon cord），问题当场解决不了，整条线就停下。“返工第三遍”为打工人场景示意。

用法：python3 -m fengtian.sample [--sheet]     # 成片 out/fengtian/sample_10s.mp4；--sheet 只出关键帧
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
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d

from adler import core, fx
from adler import kit as K
from engine import audio, bgm, gfx, perc, wording
from engine.gfx import clamp01, ease_in_out, ease_out
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, GREEN, RED, Board, P, arrow, book, check, circle, cross, desk, doc, face,
                               join, rect)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "fengtian"
VOICE, SPEED = "zv_yunxi", 1.0
ACC = "#C8102E"
B0 = 18                              # 第一镜起始实测拍（半小节线）
S = core.BEATS[B0]["t"] - 0.1        # 成片 0 秒对应的配乐时刻（第一拍前留 0.1 秒）
DROP = 32                            # 音乐 drop 所在实测拍
MUSIC_DB, DUCK = -12.0, 0.45         # 配乐相对人声的基础电平；旁白处再乘 (1 - DUCK·包络)
SFX_DB = -9.0

core.SERIES.update(name="丰田模式", count="样片", prefix="丰田")

# 旁白：(整句, [(句内片段, 字幕)])；片段拼起来等于整句，字幕时间按片段字数比例落在整句音频上。
LINES = [
    ("同一个问题，返工第三遍了。", [("同一个问题，", "同一个问题"), ("返工第三遍了。", "【返工】第三遍了")]),
    ("补了又坏，坏了又补。", [("补了又坏，坏了又补。", "补了又坏，坏了又补")]),
    ("丰田偏偏反着来：", [("丰田偏偏反着来：", "丰田偏偏【反着来】")]),
    ("谁看到毛病，谁就拉绳，", [("谁看到毛病，", "谁看到毛病"), ("谁就拉绳，", "谁就【拉绳】")]),
    ("整条线停下。", [("整条线停下。", "整条线【停下】")]),
    ("停线，怎么反倒少返工？往下看。", [("停线，怎么反倒少返工？", "停线，怎么反倒【少返工】？"), ("往下看。", "往下看")]),
]

# ---------------------------------------------------------------- 白板分镜

b = Board(size=(2200, 3400))
VA = (1100, 800, 0.85)               # 痛点：工位 + 返工循环
VB = (1100, 1750, 0.8)               # 丰田：流水线 + 安灯绳
VC = (1150, 1180, 0.58)               # 结尾钩子：拉远，循环与停线同框

LC, LR = (1350, 820), 230            # 返工循环圈
WK = (1530, 2150, 0.9)               # 流水线工人（脚底, 缩放）
CORD_X, RAIL_Y, HANDLE_Y = 1600, 1470, 1850
LAMP = (1000, 1565, 50)
BELT = (470, 1380, 2000)             # 传送带 x0, x1, y


def car(x, y, s=1.0) -> skia.Path:
    """侧视小轿车：(x, y) 为车底中点。"""
    return join(P((x - 85 * s, y - 20 * s), (x - 85 * s, y - 55 * s), (x - 45 * s, y - 60 * s), (x - 25 * s, y - 95 * s),
                  (x + 35 * s, y - 95 * s), (x + 55 * s, y - 60 * s), (x + 85 * s, y - 52 * s), (x + 85 * s, y - 20 * s),
                  close=True),
                circle(x - 48 * s, y - 16 * s, 17 * s), circle(x + 48 * s, y - 16 * s, 17 * s))


def worker_body(x, y, s) -> skia.Path:
    """工人：头、身体、腿、左臂（右臂单独画，跟着安灯绳动）。"""
    hy = y - 290 * s
    sh = hy + 80 * s
    return join(circle(x, hy, 45 * s), P((x, hy + 45 * s), (x, y - 120 * s)),
                P((x - 55 * s, y), (x, y - 120 * s), (x + 55 * s, y)), P((x - 70 * s, hy + 170 * s), (x, sh)),
                rect(x, hy - 52 * s, 100 * s, 22 * s, 8 * s))          # 安全帽帽檐


def t_beat(j, k):
    return b.t_of(j, k)


def pull_dy(T):
    """安灯绳下拉量：drop 前 0.12 秒开始拉，drop 那一帧拉到底。"""
    t1 = core.BEATS[DROP]["t"]
    return 48 * ease_in_out(clamp01((T - (t1 - 0.12)) / 0.12))


def loop_fn(c, k, T):
    """返工循环：两段弧形箭头，第 2–2.9 拍描出，第 4 拍起转圈，被剪断那一拍停转并变淡。"""
    t0, t1 = t_beat(0, 2), t_beat(0, 2.9)
    ts, tc = t_beat(0, 4), t_beat(2, 3)
    p = clamp01((T - t0) / (t1 - t0))
    spin = 0.0
    if T > ts:
        dt = min(T, tc) - ts
        spin = 230 * (dt - 0.25 * (1 - math.exp(-dt / 0.25)))          # 起转有个缓冲
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
            tx, ty = -math.sin(ae), math.cos(ae)                          # 切线（顺时针方向）
            for d in (0.55, -0.55):
                hx = ex - 46 * (tx * math.cos(d) - ty * math.sin(d))
                hy = ey - 46 * (tx * math.sin(d) + ty * math.cos(d))
                c.drawLine(ex, ey, hx, hy, wb.marker(RED, 12, alpha))
        elif i == 1 or tip is None:
            tip = (ex, ey)
    return tip if p < 1 else None


def cars_fn(c, k, T):
    """传送带上的三辆车：第 2 拍出现并向右走，drop 那一帧（拉绳）停住；第二辆车第 4 拍冒出红色“!”。"""
    t_in, t_mark = t_beat(1, 2), t_beat(1, 4)
    t_stop = core.BEATS[DROP]["t"]
    a = ease_out(clamp01((T - t_in) / 0.3))
    v, span = 200.0, 960.0
    te = min(T, t_stop)
    x0, x1, y = BELT
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y - 360, x1, y + 40))
    for i in range(3):
        # 第二辆车在“!”出现时位于 x≈950
        cx = x0 + ((950 - x0) + (i - 1) * 320 + v * (te - t_mark)) % span
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
    """工人右臂：举手握住安灯绳把手，拉绳时跟着往下。"""
    x, y, s = WK
    hy = y - 290 * s
    sx, sy = x, hy + 80 * s
    hx, hyy = CORD_X, HANDLE_Y + 30 + pull_dy(T)
    p = clamp01(k * 1.0)
    c.drawLine(sx, sy, sx + (hx - sx) * p, sy + (hyy - sy) * p, wb.marker(BLACK, 10))
    return (sx + (hx - sx) * p, sy + (hyy - sy) * p) if p < 1 else None


def cord_fn(c, k, T):
    """安灯绳：从顶上的横杆垂到工人手边，末端是把手。"""
    dy = pull_dy(T)
    yb = RAIL_Y + (HANDLE_Y + dy - RAIL_Y) * clamp01(k)
    c.drawLine(CORD_X, RAIL_Y, CORD_X, yb, wb.marker(ACC, 7))
    if k >= 1:
        c.drawPath(rect(CORD_X, HANDLE_Y + 25 + dy, 34, 56, 10), wb.marker(ACC, 9))
        return None
    return CORD_X, yb


def lamp_fn(c, k, T):
    """安灯：拉绳那一帧亮红灯，之后一闪一闪。"""
    t_on = core.BEATS[DROP]["t"]
    if T < t_on:
        return None
    x, y, r = LAMP
    dt = T - t_on
    blink = 0.75 + 0.25 * math.cos(dt * 2 * math.pi / (core.BEATS[DROP + 1]["t"] - t_on))
    c.drawCircle(x, y, r * 3.2, K.paint(RED, 0.28 * blink, blur=40))
    c.drawCircle(x, y, r - 4, K.paint(RED, 0.9 * blink))
    for i in range(8):
        ang = i / 8 * 2 * math.pi
        L = 30 + 18 * ease_out(clamp01(dt / 0.25))
        c.drawLine(x + math.cos(ang) * (r + 18), y + math.sin(ang) * (r + 18),
                   x + math.cos(ang) * (r + 18 + L), y + math.sin(ang) * (r + 18 + L), wb.marker(RED, 7, blink))
    return None


def rays(x, y, w, h) -> skia.Path:
    parts = []
    for dx, dy, ex, ey in ((-1, -1, -1.3, -1.5), (0, -1.15, 0, -1.6), (1, -1, 1.3, -1.5)):
        parts.append(P((x + dx * w / 2, y + dy * h / 2), (x + ex * w / 2, y + ey * h / 2)))
    return join(*parts)


# 镜头 1（2 小节）：打工人痛点——工位上同一个问题返工第三遍，补了又坏
j = b.shot("", "打工人日常", view=VA, bars=2)
b.path(j, 0, 0.8, join(desk(780, 990, 380), wb.stick(600, 1140, 0.85, "hold")), sfx="wood_high")
b.path(j, 0.8, 0.95, face(600, 1140, 0.85, "sad"))
b.path(j, 1, 1.7, doc(*LC, 150, 190), BLACK, 9, sfx="pop")
b.custom(j, 2, 2.9, loop_fn, sfx="wood_high")
b.text(j, 3, 3.8, "第3遍", LC[0], 520, 92, RED, sfx="rim")
b.hit(j, 4, "shaker", 0.7, "返工圈开始转")
b.text(j, 5, 5.3, "补", 1030, 700, 76, GREEN, sfx="pop")
b.path(j, 5.3, 5.8, check(1030, 830, 42), GREEN, 11)
b.text(j, 6, 6.3, "坏", 1680, 700, 76, RED, sfx="pop")
b.path(j, 6.3, 6.8, cross(1680, 830, 38), RED, 11)

# 镜头 2（2 小节）：书中做法——谁看到毛病谁就拉绳，整条线停下（拉绳 = 音乐 drop）
j = b.shot("", "丰田模式 · 书中做法", view=VB, bars=2, shake=[(DROP - 26, 18.0)], flashes=[(DROP - 26, 0.5)])
b.path(j, 0, 0.8, book(640, 1325, 230, 150), GREEN, 9, sfx="wood_low")
b.text(j, 0.8, 1.6, "丰田模式", 1020, 1325, 84, GREEN)
x0, x1, by = BELT
b.path(j, 1, 1.8, join(rect((x0 + x1) / 2, by + 12, x1 - x0 + 40, 46, 20),
                       *[circle(xx, by + 12, 13) for xx in range(x0 + 40, x1, 110)]), sfx="wood_high")
b.custom(j, 2, 2.3, cars_fn, sfx="pop")
b.path(j, 3, 3.7, worker_body(*WK), sfx="wood_high")
b.path(j, 3.7, 3.85, face(WK[0], WK[1], WK[2], "flat"))
b.custom(j, 3.6, 3.95, arm_fn)
b.hit(j, 4, "rim", 0.8, "车上冒出红色“!”（毛病）")
b.path(j, 5, 5.5, join(P((x0, RAIL_Y), (1760, RAIL_Y)), P((LAMP[0], RAIL_Y), (LAMP[0], LAMP[1] - LAMP[2])),
                       circle(*LAMP)), BLACK, 9, sfx="wood_high")
b.custom(j, 5.5, 5.9, cord_fn)
b.custom(j, DROP - 26, DROP - 26 + 1, lamp_fn, sfx="kick", gain=0.9)        # drop：拉绳、红灯亮、整条线停
b.text(j, 7, 7.35, "停！", 640, 1740, 150, RED, sfx="ding")
b.path(j, 7.35, 7.8, rays(640, 1740, 260, 150), RED, 8)

# 镜头 3（1 小节）：结尾钩子——拉远，停线指向返工圈，红笔一刀剪断循环，留一个问号
j = b.shot("", "接下来", view=VC, bars=1, shake=[(3, 12.0)])
b.path(j, 0, 0.8, arrow((1680, 1430), (1530, 1040), 0.18, 44), GREEN, 11, sfx="wood_high")
b.text(j, 2, 2.3, "？", 1880, 1230, 280, RED, sfx="pop")
b.path(j, 3, 3.25, P((1080, 560), (1640, 1100)), RED, 22, sfx="frame", gain=0.9)
b.path(j, 4, 4.3, arrow((1880, 1420), (1880, 1640), 0.0, 48), RED, 12, sfx="pop", gain=0.6)

# ---------------------------------------------------------------- 时间轴（不走 Episode.build：样片只用配乐中间 5 小节）

ep = core.Episode(1, "sample", "停线", "丰田模式样片", ACC, b.shots, refs=[])
bb = B0
for s in b.shots:
    s.b0 = bb
    s.t0 = core.bt(bb)
    bb += 4 * s.bars
    s.t1 = core.bt(bb)
b.shots[0].t0 = S
b.attach(ep)


# ---------------------------------------------------------------- 旁白与字幕时间

def _weight(s):
    return sum(0.6 if ch in "，。：？！" else 1.0 for ch in s)


def narration():
    """合成每句旁白并排时间（成片本地秒）；返回 (旁白片段 [(本地起点, 音频)], 字幕 [(起, 止, 字幕)], 句表)。"""
    nar = audio.Narrator(VOICE)
    clips = [nar.generate(t, SPEED) for t, _ in LINES]
    d = [len(x) / audio.SR for x in clips]
    loc = lambda T: T - S
    sh = b.shots
    drop = loc(core.BEATS[DROP]["t"])
    starts = [0.15, None, loc(sh[1].t0) + 0.08, drop - d[3] - 0.02, drop + 0.08, loc(sh[2].t0) + 0.02]
    starts[1] = max(starts[0] + d[0] + 0.2, loc(core.bt(B0 + 5)) - 0.15)     # “补”“坏”落在第 5、6 拍
    for i in range(1, len(starts)):
        if starts[i] < starts[i - 1] + d[i - 1] + 0.08:
            raise ValueError(f"第 {i + 1} 句与上一句重叠：{starts[i]:.2f}s")
    caps, table = [], []
    for (text, pieces), st, du in zip(LINES, starts, d):
        if "".join(p for p, _ in pieces) != text:
            raise ValueError(f"字幕片段与旁白不一致：{text}")
        tot, acc = _weight(text), 0.0
        for p, cap in pieces:
            caps.append([st + du * acc / tot, None, cap])
            acc += _weight(p)
        table.append((text, st, du))
    for i, cp in enumerate(caps):
        cp[1] = caps[i + 1][0] if i + 1 < len(caps) else None
    return list(zip(starts, clips)), caps, table


# ---------------------------------------------------------------- 画面

CAPS: list = []
DUR = 0.0


def draw_caption(c, t):
    for t0, t1, cap in CAPS:
        if t0 <= t and (t1 is None or t < t1):
            break
    else:
        return
    k = clamp01((t - t0) / 0.18)
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


_DUMMY = skia.Surface(8, 8).getCanvas()


def idle_tip(T):
    """手的停放位置：最近画完的那一笔的终点。逐帧独立求值（多进程分块渲染时手不会跳到别处）。"""
    if b.t_of(2, 3.25) <= T < b.t_of(2, 4):
        return 2010, 1620              # 剪断之后手挪到右下角，让出问号
    best, tip = -1.0, None
    for it in b.items:
        if it["kind"] == "erase":
            continue
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
    """成片第 t 秒（本地时间）的画面；白板、相机、闪白都按配乐时刻 T = S + t 求值。"""
    T = S + t
    b._last_tip = idle_tip(T)
    ji = ep.shot_at(T)
    s = ep.shots[ji]
    g = core.G(c, ep, s, T - s.t0)
    wb.render_board(c, b, T)
    for kb, pk in s.flashes:
        a = fx.flash_alpha(g.since(kb), pk)
        if a > 0:
            c.drawPaint(K.paint("#FFFFFF", a))
    c.drawRect(skia.Rect.MakeLTRB(0, wb.CAP_TOP, core.W, wb.CAP_BOTTOM), K.paint("#FFFFFF", 0.82, blur=8))
    draw_caption(c, t)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, core.W, 318), K.paint("#FBFBF9", 1.0, blur=6))     # 页眉区不透出上一块白板
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
    """前视限幅：增益取窗口内最小值再平滑，样本峰值不超过 ceil_db。"""
    ceil = 10 ** (ceil_db / 20)
    peak = np.max(np.abs(x), axis=1)
    w = max(3, int(look * audio.SR))
    g = np.minimum(1.0, ceil / np.maximum(peak, 1e-9))
    g = minimum_filter1d(g, 2 * w + 1)
    g = uniform_filter1d(g, 2 * w + 1)
    g = np.minimum(g, minimum_filter1d(np.minimum(1.0, ceil / np.maximum(peak, 1e-9)), 3))
    return x * g[:, None]


def build_audio(voice_clips):
    n = int(DUR * audio.SR)
    v = np.zeros(n)
    for st, x in voice_clips:
        audio.place(v, x, st)
    v = audio.process_voice(v)
    voice = audio.pan(v, 0) * 1.41
    m0 = int(round(S * audio.SR))
    music = bgm.load()[m0: m0 + n].copy()
    fi, fo = int(0.08 * audio.SR), int(0.45 * audio.SR)
    music[:fi] *= np.linspace(0, 1, fi)[:, None]
    music[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    sfx = np.zeros((n, 2))
    events = []
    for k, s in enumerate(ep.shots):
        for beat, name, gain, note in s.all_hits():
            gi = s.b0 + int(round(beat))
            bt = core.BEATS[gi]
            name = core.resolve_sfx(name, bt)
            clip = perc.sound(name) * core.SFX_LEVEL.get(name, 0.3) * gain
            lead = perc.attack_ms(name) / 1000
            t = bt["t"] - S
            audio.place(sfx, audio.pan(clip, 0), t - lead)
            fr = int(round(t * core.FPS))
            events.append(dict(shot=k + 1, beat=gi, t=t, sfx=name, note=note, frame=fr,
                               frame_err=round(t * core.FPS - fr, 2)))
    lv = _lufs(voice)
    music *= 10 ** ((lv + MUSIC_DB - _lufs(music)) / 20)
    sfx *= 10 ** ((lv + SFX_DB - _lufs(sfx)) / 20)
    duck = audio.duck_envelope(v)
    music_d = music * (1 - DUCK * duck)[:, None]
    mix = voice + music_d + sfx
    gain = 10 ** ((-14.0 - _lufs(mix)) / 20)
    stems = {"voice": voice * gain, "music": music_d * gain, "sfx": sfx * gain}
    mix = limiter(mix * gain, -2.0)
    gain2 = 10 ** ((-14.0 - _lufs(mix)) / 20)            # 限幅后补回响度，再限一次
    mix = limiter(mix * gain2, -2.0)
    return mix.astype(np.float32), stems, duck, events


# ---------------------------------------------------------------- 检查

def wording_warnings():
    texts = [("旁白", t) for t, _ in LINES] + [("字幕", cap) for _, ps in LINES for _, cap in ps]
    texts += [(f"镜头{it['j'] + 1}白板字", it["s"]) for it in b.items if it["kind"] == "text"]
    texts += [(f"镜头{i + 1}标签", s.tag) for i, s in enumerate(b.shots)]
    out = []
    for where, s in texts:
        hits = wording.check(wording.gfx_plain(s))
        if hits:
            out.append(f"{where}“{s}”：{'、'.join(hits)}")
        if where == "字幕" and core.han(s) > 10:
            out.append(f"字幕“{s}”超过 10 字")
    return out


def main():
    global CAPS, DUR
    OUT.mkdir(parents=True, exist_ok=True)
    for w in wording_warnings():
        print("文案警告：", w, file=sys.stderr)
    clips, CAPS, table = narration()
    DUR = round(table[-1][1] + table[-1][2] + 0.3, 2)
    ep.total = DUR
    print(f"时长 {DUR:.2f}s，配乐 {S:.2f}–{S + DUR:.2f}s（drop {core.BEATS[DROP]['t'] - S:.2f}s）")
    for text, st, du in table:
        print(f"  旁白 {st:5.2f}–{st + du:5.2f}s  {text}")
    for t0, t1, cap in CAPS:
        print(f"  字幕 {t0:5.2f}–{(t1 if t1 is not None else DUR):5.2f}s  {cap}")
    if "--sheet" in sys.argv:
        for t in (1.9, 3.4, 6.2, 7.7, 8.4, 9.8, 10.5, DUR - 0.05):
            still(t, str(OUT / f"sheet_{t:05.2f}.png"))
        return
    mix, stems, duck, events = build_audio(clips)
    for e in events:
        print(f"  音效 {e['t']:5.2f}s 帧{e['frame']:3d}（偏差 {e['frame_err']:+.2f} 帧） 拍{e['beat']} {e['sfx']} {e['note']}")
    for k, x in stems.items():
        sf.write(OUT / f"sample_{k}.wav", x.astype(np.float32), audio.SR, subtype="PCM_16")
    # 人声段 / 非人声段的配乐与人声电平
    hop = int(0.05 * audio.SR)
    vr = np.sqrt(np.maximum(uniform_filter1d(stems["voice"][:, 0] ** 2, hop), 0))
    on = vr > 0.1 * vr.max()
    db = lambda x, m: 10 * np.log10(np.mean(x[m] ** 2) + 1e-12)
    print(f"  人声段：人声 {db(stems['voice'], on):.1f} dB，配乐 {db(stems['music'], on):.1f} dB；"
          f"无人声段配乐 {db(stems['music'], ~on):.1f} dB；人声 {_lufs(stems['voice']):.1f} LUFS，"
          f"配乐 {_lufs(stems['music']):.1f} LUFS，音效 {_lufs(stems['sfx']):.1f} LUFS")
    out = OUT / "sample_10s.mp4"
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
