"""《丰田模式》01 停线：同一个问题，为什么总返工？（白板手绘 + AI 旁白，约 85 秒 + 频道片尾）

延续样片 v3 的风格与做法（用户确认“就这样，出第一讲”）：
- 12 屏，一屏一件事，每屏 ≥5.3 秒，旁白讲完、画完后停 ≥1.5 秒才切；切屏镜头移动 1.1 秒缓入缓出，切在实测半小节线上；
- 屏长按旁白实测时长自动排到半小节线；画面事件吸附到旁白关键词附近的实测拍点，配 engine/perc 打击乐，峰值对齐撞击帧；
- 拉绳 = 音乐 drop（实测第 32 拍）；角色延续：打工人小李、员工小王（黄安全帽蓝工装）、组长老张（红帽红袖章夹板）；
- 旁白音色见 fengtian/sample_v3.py 顶部 NARRATOR / GENERATE（音色 B：zv_yunjian）；配乐比人声低约 15 dB 并闪避，-14 LUFS。

叙事：痛点开场（小李返工第 3 遍）→ 丰田怎么做（小王发现毛病拉绳 → 黄灯 → 组长赶来 → 车走出工位前修不好才停线 → 红灯“停！”）
→ 为什么停线反而少返工（不停：带毛病的车一路往下装 → 最后拆开再装 = 返工；书中观点：当场亮出来、源头修好、不往下传）
→ 换到打工人（小李的方案带坑交出去，越挖越大又回来）→ 三条做法（示意）→ 评论区追问 + 下一讲预告。
出处与说明见 NOTES。
"""

import math

import numpy as np
import skia

from adler import core
from adler import kit as K
from engine import audio
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, cross,
                               desk, doc, join, rect, stick, face)

from .sample_v3 import GENERATE, NARRATOR

NO, KEY, CONCEPT = 1, "andon", "停线"
TITLE = "同一个问题，为什么总返工？"
ACC = "#C8102E"
YELLOW, HAT, SUIT, BOARD_C = "#E0A21B", "#F2B705", "#CFE0F5", "#C89B63"
TAGS = "#丰田模式 #精益管理 #读书 #打工人 #职场 #返工"
COVER_TITLE = "同一个问题|为什么总【返工】"
SQUARE_SHOT = 3                 # 横屏封面取景：第 4 屏（小王、老张、红灯、“停！”）
COVER_SHOT = 3
COMMA, PERIOD = 0.25, 0.45
B0 = 10                         # 第 1 屏起拍
DROP = 32
S = core.BEATS[B0]["t"] - 0.15
HOLD = 1.55                     # 旁白讲完后至少停留（秒）
MIN_BEATS = 10

core.SERIES.update(name="丰田模式", count="第一季", prefix="丰田")

# 旁白：(整句, 字幕)；字幕按逗号与句内逗号一一对应（None 表示与下一条合并显示）
LINES = [
    ("同一个问题，返工第三遍了。", ["同一个问题", "【返工】第三遍了"]),
    ("补了又坏，坏了又补。", ["补了又坏，坏了又补"]),
    ("丰田偏偏反着来：", ["丰田偏偏【反着来】"]),
    ("工人看到毛病，就拉一下绳。", ["工人看到毛病", "就【拉】一下绳"]),
    ("黄灯一亮，组长马上赶来。", ["黄灯一亮", "【组长】马上赶来"]),
    ("这辆车走出工位前修好，线照常走。", ["这辆车走出工位前修好", "线照常走"]),
    ("修不好，整条线才停下。", ["修不好", "整条线才【停下】"]),
    ("要是不停，带毛病的车接着往下走。", ["要是不停", "带毛病的车接着往下走"]),
    ("后面每个工位，都在它上面接着装零件。", ["后面每个工位", "都在它上面接着装零件"]),
    ("等到最后才发现，只能拆开再装一遍。", ["等到最后才发现", "只能拆开再装一遍"]),
    ("这就是返工。", ["这就是【返工】"]),
    ("问题当场亮出来，在源头修好，不往下传。", ["问题当场亮出来", "在【源头】修好", "不往下传"]),
    ("小李的方案里有个坑，他想先交了再说。", ["小李的方案里有个坑", "他想先交了再说"]),
    ("到了主管那、客户那，坑越挖越大，最后又回到他手上。", ["到了主管那、客户那", "坑越挖越大", "最后又回到他手上"]),
    ("第一，发现问题，当场喊停。", [None, "第一，发现问题", "当场【喊停】"]),
    ("拉上同事，一起看五分钟。", ["拉上同事", "一起看五分钟"]),
    ("第二，在源头修，别在后面打补丁。", [None, "第二，在【源头】修", "别在后面打补丁"]),
    ("第三，跟团队说好：喊停不挨骂。", ["第三", "跟团队说好：【喊停不挨骂】"]),
    ("你上次想喊停却没开口，是为什么？", ["你上次想喊停却没开口", "是为什么？"]),
    ("下一讲：活儿做得越多，为什么越乱？", ["下一讲：活儿做得越多", "为什么越乱？"]),
]
# 每屏：(旁白句序号, 页眉标签)
SCREENS = [
    ([0, 1], "打工人日常"), ([2, 3], "丰田模式 · 书中做法"), ([4], "丰田模式 · 书中做法"), ([5, 6], "丰田模式 · 书中做法"),
    ([7, 8], "为什么要停"), ([9, 10], "为什么要停"), ([11], "书中观点"), ([12, 13], "换到打工人"),
    ([14, 15], "做法一 · 示意"), ([16], "做法二 · 示意"), ([17], "做法三 · 示意"), ([18, 19], "评论区见"),
]

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way: 14 Management Principles from the World's Greatest Manufacturer "
    "(McGraw-Hill, 2004；第 2 版 2021)。中译本《丰田模式：精益制造的14项管理原则》，[美]杰弗瑞·莱克 著，机械工业出版社"
    "（珍藏版 2016 年 1 月；另有原书第 2 版）。译者未在网页上核实到，以版权页为准。",
    "本讲依据：第二部分“正确的流程方能产生正确的结果”之原则 5——建立立即暂停以解决问题、从一开始就重视质量的文化"
    "（英文版第 11 章 Principle 5: Build a Culture of Stopping to Fix Problems, to Get Quality Right the First Time），"
    "涉及自働化（jidoka）与安灯（andon）。上屏与旁白均为转述，不是逐字引文；未引用书中数字。",
    "安灯的流程（讲准的部分）：工人发现异常拉绳，先亮灯、叫组长来处理；车走到该工位尽头（定位停止点）前处理好，线照常走；"
    "处理不好，整条线才停下。旁白：“黄灯一亮，组长马上赶来；这辆车走出工位前修好，线照常走；修不好，整条线才停下。”"
    "参考：Lean Enterprise Institute 词条 Andon、Gemba Academy 对丰田肯塔基工厂的介绍、leanblog.org 对“一拉就全线停”误解的辨析。"
    "灯的颜色（先黄后红）为画面示意，各工厂做法不尽相同。",
    "“不停线 → 带毛病的车一路往下装 → 最后拆开再装 = 返工”“问题当场亮出来、在源头修好、不往下传”为对原则 5 的通俗化转述与示意。",
    "小李、小王、老张为虚构人物；“返工第三遍”“看五分钟”为示意，不是数据。三条做法（当场喊停拉人一起看 / 源头修别打补丁 / "
    "团队约定喊停不挨骂）为据书中思路整理的建议。",
    "下一讲拟题：02 拉动 · 只做下一步要的——“活儿做得越多，为什么越乱？”（原则 3：使用拉动式生产方式以避免生产过剩）。",
]

# ---------------------------------------------------------------- 旁白与排期


def stretch(x, text):
    """逗号处补停顿到约 COMMA 秒（预期位置 ±12% 内最安静的 30ms 切开）。返回 (音频, 各逗号后分句起点秒)。"""
    clauses = text.rstrip("。：？！").split("，")
    hz = [sum(1 for ch in cl if ch not in "。：？！、") for cl in clauses]
    total = sum(hz)
    hop = int(0.01 * audio.SR)
    starts, added, acc = [], 0, 0
    for ci in range(len(clauses) - 1):
        acc += hz[ci]
        n = len(x) // hop
        r = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1))
        r3 = np.convolve(r, np.ones(3) / 3, "same")
        orig_n = (len(x) - added) // hop
        center = int(acc / total * orig_n) + added // hop
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
    return x, [0.0] + starts


_nar = audio.Narrator(**NARRATOR)
RAW = [_nar.generate(t, **GENERATE) for t, _ in LINES]
CLIPS, CLAUSE_T = zip(*[stretch(x, t) for x, (t, _) in zip(RAW, LINES)])
DUR_L = [len(x) / audio.SR for x in CLIPS]


def _even_beat_at_or_after(T):
    i = int(np.searchsorted(core._BEAT_T, T - 1e-6))
    return i + (i % 2)


def _schedule():
    """屏起止拍与每句旁白起点（成片本地秒）。第 1、2 屏固定（拉绳对准 drop），其余按旁白长度排到半小节线。"""
    starts = [None] * len(LINES)
    bounds = [(B0, B0 + 12), (B0 + 12, B0 + 26)]
    loc = lambda T: T - S
    starts[0] = 0.25
    starts[1] = starts[0] + DUR_L[0] + PERIOD
    starts[2] = loc(core.bt(bounds[1][0])) + 0.45
    starts[3] = loc(core.BEATS[DROP]["t"]) - DUR_L[3] - 0.03
    b = bounds[1][1]
    for si in range(2, len(SCREENS)):
        lines = SCREENS[si][0]
        t = loc(core.bt(b)) + 0.3
        for li in lines:
            starts[li] = t
            t += DUR_L[li] + PERIOD
        end_voice = t - PERIOD
        hold = HOLD + (0.6 if si == len(SCREENS) - 1 else 0.0)
        e = max(b + MIN_BEATS, _even_beat_at_or_after(S + end_voice + hold))
        if e > core.N_BEATS - 1:
            e = core.N_BEATS - 1
        bounds.append((b, e))
        b = e
    return bounds, starts


BOUNDS, STARTS = _schedule()
END_LOCAL = min(core.bt(BOUNDS[-1][1]) - S, core.END - S - 0.05)
if BOUNDS[-1][1] >= core.N_BEATS - 1:                   # 末屏延到原曲最后一击之后的混响尾音里
    voice_end = STARTS[SCREENS[-1][0][-1]] + DUR_L[SCREENS[-1][0][-1]]
    END_LOCAL = min(core.END - S - 0.05, voice_end + 2.2)


def wt(li, ci=0, frac=0.0):
    """第 li 句第 ci 个分句（起点 + frac·该分句长度）的本地时间。"""
    ts = CLAUSE_T[li]
    a = ts[ci]
    z = ts[ci + 1] if ci + 1 < len(ts) else DUR_L[li]
    return STARTS[li] + a + (z - a) * frac


def kb(j, t_local, lo=0):
    """本屏内离本地时间 t_local 最近的整数拍（不早于 lo）。"""
    b0, b1 = BOUNDS[j]
    T = S + t_local
    i = int(np.argmin(np.abs(core._BEAT_T[b0:b1] - T)))
    return max(lo, i)


# ---------------------------------------------------------------- 白板布局

b = Board(size=(2400, 10600))
# 取景按 2:3 竖屏的白板舞台（872×900，见 fengtian/build.py）框住每屏全部内容（含标签、砸字、回弹余量）
VA = (1125, 810, 0.67)
VB = (1112, 1790, 0.63)
VB2 = (1292, 1800, 0.52)
VC = (1200, 3290, 0.53)
VD = (870, 4280, 0.84)
VE = (1160, 5700, 0.54)
VF1, VF2, VF3 = (1035, 6575, 0.71), (1078, 7590, 0.61), (1100, 8600, 0.76)
VG = (1150, 9785, 0.88)
# 屏 → 白板区块（镜头到位后只画本区块，避免相邻区块漏进舞台边缘）
GROUP = [0, 1, 1, 1, 2, 2, 3, 4, 5, 6, 7, 8]

LC, LR = (1350, 820), 230
WK = (1530, 2150, 0.9)
LD = (1850, 2150, 1.0)
CORD_X, RAIL_Y, HANDLE_Y = 1610, 1470, 1840
LAMP = (1000, 1565, 50)
BELT = (470, 1380, 2000)
ZONE = (620, 1045)                # 小王的工位（定位停止点在右端）
CAR_X = [650, 900, 1150]          # 刹停时三辆车的位置（中间那辆在工位尽头）
TIMER = (830, 1760, 46)


def tb(j, k):
    return b.t_of(j, k)


def beat_pos(T):
    bt_ = core._BEAT_T
    i = int(np.clip(np.searchsorted(bt_, T, side="right") - 1, 0, len(bt_) - 2))
    return i + (T - bt_[i]) / (bt_[i + 1] - bt_[i])


def pop_scale(dt, dur=0.32):
    return 0.0 if dt < 0 else ease_out_back(clamp01(dt / dur))


def slam_scale(dt):
    if dt < 0:
        return 0.0
    if dt < 0.1:
        return lerp(1.9, 1.0, ease_out(dt / 0.1))
    return 1.0 + 0.07 * math.exp(-(dt - 0.1) * 9) * math.sin((dt - 0.1) * 30)


def _line(c, a, z, color, w, alpha=1.0):
    c.drawLine(a[0], a[1], z[0], z[1], wb.marker(color, w, alpha))


def _reveal(c, x, top, h, p):
    c.clipRect(skia.Rect.MakeLTRB(x - 400, top - 10, x + 400, top + h * p))
    return (x + 70, top + h * p) if p < 1 else None


# ---------------------------------------------------------------- 角色（同 v3；工牌、袖章不再写小字，身份靠脚下标签）

def draw_worker(c, x, y, s, lh, rh, head_dx=0.0, alpha=1.0):
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    torso = skia.Rect.MakeLTRB(x - 42 * s, hy + 55 * s, x + 42 * s, y - 105 * s)
    c.drawRoundRect(torso, 18 * s, 18 * s, K.paint(SUIT, alpha))
    c.drawRoundRect(torso, 18 * s, 18 * s, wb.marker(BLUE, 8, alpha))
    for foot in ((x - 55 * s, y), (x + 55 * s, y)):
        _line(c, hip, foot, BLUE, 10, alpha)
    _line(c, sh, lh, BLUE, 10, alpha)
    _line(c, sh, rh, BLUE, 10, alpha)
    hx = x + head_dx
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    for dx in (-15, 15):
        c.drawCircle(hx + dx * s, hy - 4 * s, 4 * s, K.paint(BLACK, alpha))
    _line(c, (hx - 14 * s, hy + 20 * s), (hx + 14 * s, hy + 20 * s), BLACK, 6, alpha)
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeXYWH(hx - 50 * s, hy - 82 * s, 100 * s, 90 * s), 180, 180)
    dome.close()
    c.drawPath(dome, K.paint(HAT, alpha))
    c.drawPath(dome, wb.marker(BLACK, 7, alpha))
    _line(c, (hx - 66 * s, hy - 37 * s), (hx + 66 * s, hy - 37 * s), BLACK, 9, alpha)
    badge = skia.Rect.MakeXYWH(x - 26 * s, hy + 88 * s, 52 * s, 30 * s)
    c.drawRoundRect(badge, 5, 5, K.paint("#FFFFFF", alpha))
    c.drawRoundRect(badge, 5, 5, wb.marker(BLUE, 4, alpha))


def draw_leader(c, x, y, s, phase, run, head_dx=0.0, alpha=1.0):
    bob = -abs(math.sin(math.pi * phase)) * 16 * run
    y0 = y + bob
    hy = y0 - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y0 - 120 * s)
    sw = math.sin(2 * math.pi * phase) * run
    _line(c, (x, hy + 45 * s), hip, BLACK, 11, alpha)
    for sgn in (1, -1):
        stand = (x + sgn * 55 * s, y)
        runp = (x + sgn * 75 * s * sw, y0 - 22 * s * max(0.0, -sgn * sw))
        _line(c, hip, (lerp(stand[0], runp[0], run), lerp(stand[1], runp[1], run)), BLACK, 11, alpha)
    clip_c = (x - 80 * s, hy + 150 * s)
    _line(c, sh, (clip_c[0] + 10 * s, clip_c[1]), BLACK, 11, alpha)
    rh = (x + 70 * s - 30 * sw * s, hy + 170 * s - 25 * abs(sw) * s)
    _line(c, sh, rh, BLACK, 11, alpha)
    clip = skia.Rect.MakeXYWH(clip_c[0] - 40 * s, clip_c[1] - 55 * s, 80 * s, 105 * s)
    c.drawRoundRect(clip, 6, 6, K.paint(BOARD_C, alpha))
    c.drawRoundRect(clip, 6, 6, wb.marker(BLACK, 6, alpha))
    for i in range(3):
        yy = clip_c[1] - 20 * s + i * 22 * s
        _line(c, (clip_c[0] - 25 * s, yy), (clip_c[0] + 25 * s, yy), BLACK, 4, alpha)
    ax, ay = lerp(sh[0], rh[0], 0.4), lerp(sh[1], rh[1], 0.4)
    c.drawRoundRect(skia.Rect.MakeXYWH(ax - 30 * s, ay - 15 * s, 60 * s, 30 * s), 6, 6, K.paint(RED, alpha))
    hx = x + head_dx
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    for dx in (-15, 15):
        c.drawCircle(hx + dx * s, hy - 4 * s, 4 * s, K.paint(BLACK, alpha))
    m = skia.Path()
    m.addArc(skia.Rect.MakeXYWH(hx - 16 * s, hy + 12 * s, 32 * s, 18 * s), 200, 140)
    c.drawPath(m, wb.marker(BLACK, 6, alpha))
    cap = skia.Path()
    cap.addArc(skia.Rect.MakeXYWH(hx - 47 * s, hy - 70 * s, 94 * s, 70 * s), 180, 180)
    cap.close()
    c.drawPath(cap, K.paint(RED, alpha))
    c.drawPath(cap, wb.marker(BLACK, 6, alpha))
    _line(c, (hx - 10 * s, hy - 35 * s), (hx - 80 * s, hy - 30 * s), BLACK, 10, alpha)


def pop_text(s, x, y, size, color, j, k, font="hand"):
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k))
        if sc > 0:
            with K.at(c, x, y, 0, sc):
                K.text(c, s, 0, 0, size, font, color, clamp01(sc * 2))
        return None
    return fn


def slam_text(s, x, y, size, color, j, k, font="hand"):
    def fn(c, kk, T):
        sc = slam_scale(T - tb(j, k))
        if sc > 0:
            with K.at(c, x, y, 0, sc):
                K.text(c, s, 0, 0, size, font, color, clamp01((T - tb(j, k)) / 0.06))
        return None
    return fn


def pop_path(path, x, y, color, width, j, k, fill=None):
    """整块弹出的图形（以 (x, y) 为中心缩放回弹）。"""
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k))
        if sc > 0:
            with K.at(c, x, y, 0, sc):
                c.translate(-x, -y)
                if fill:
                    c.drawPath(path, K.paint(fill))
                c.drawPath(path, wb.marker(color, width))
        return None
    return fn


# ---------------------------------------------------------------- 屏 1：返工圈

T_CUT = None                      # 返工圈停转的时刻（第 6 屏“这就是返工”时剪断，见下）
SPIN0 = B0 + 4


def loop_fn(c, k, T):
    t0, t1 = tb(0, 2), tb(0, 2.9)
    p = clamp01((T - t0) / (t1 - t0))
    spin = 360 * (beat_pos(T) - SPIN0) / 4 if T > core.bt(SPIN0) else 0.0
    x, y = LC
    tip = None
    for i in range(2):
        a0 = -90 + i * 180 + spin + 12
        sweep = 150 * p
        pa = skia.Path()
        pa.addArc(skia.Rect.MakeXYWH(x - LR, y - LR, 2 * LR, 2 * LR), a0, sweep)
        c.drawPath(pa, wb.marker(RED, 12))
        ae = math.radians(a0 + sweep)
        ex, ey = x + LR * math.cos(ae), y + LR * math.sin(ae)
        if p >= 1:
            tx, ty = -math.sin(ae), math.cos(ae)
            for d in (0.55, -0.55):
                c.drawLine(ex, ey, ex - 46 * (tx * math.cos(d) - ty * math.sin(d)),
                           ey - 46 * (tx * math.sin(d) + ty * math.cos(d)), wb.marker(RED, 12))
        elif i == 1 or tip is None:
            tip = (ex, ey)
    if p >= 1 and T >= core.bt(SPIN0):
        dt = T - core.bt(SPIN0 + 4 * int((beat_pos(T) - SPIN0) // 4))
        if dt < 0.35:
            K.ripple(c, x, y - LR, dt, RED, 70, 6, 0.7, 0.35)
    return tip if p < 1 else None


# ---------------------------------------------------------------- 屏 2–4：流水线

def t_drop():
    return core.BEATS[DROP]["t"]


T_IN = None   # 车出现（屏 2 第 3 拍），在分镜里赋值
T_STOP = None  # 刹停（屏 4），在分镜里赋值


def car_path(x, y, s=1.0) -> skia.Path:
    return join(P((x - 85 * s, y - 20 * s), (x - 85 * s, y - 55 * s), (x - 45 * s, y - 60 * s), (x - 25 * s, y - 95 * s),
                  (x + 35 * s, y - 95 * s), (x + 55 * s, y - 60 * s), (x + 85 * s, y - 52 * s), (x + 85 * s, y - 20 * s),
                  close=True),
                circle(x - 48 * s, y - 16 * s, 17 * s), circle(x + 48 * s, y - 16 * s, 17 * s))


def car_offset(T):
    ts = T_STOP()
    if T < ts:
        v = 330.0 / (ts - T_IN())
        return -v * (ts - T)
    dt = T - ts
    return 16 * math.exp(-dt * 7) * math.sin(dt * 22)


def cars_fn(c, k, T):
    t_mark = tb(1, 7)
    a = ease_out(clamp01((T - T_IN()) / 0.3))
    x0, x1, y = BELT
    off = car_offset(T)
    dt = T - T_STOP()
    tilt = -4 * math.exp(-dt * 7) * math.sin(dt * 22) if dt >= 0 else 0.0
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y - 300, x1 + 120, y + 40))
    for i, xs in enumerate(CAR_X):
        with K.at(c, xs + off, y - 25, tilt):
            pth = car_path(0, 0)
            if i == 1 and T >= t_mark:
                m = ease_out(clamp01((T - t_mark) / 0.2))
                c.drawPath(pth, K.paint(RED, 0.2 * m))
                c.drawPath(pth, wb.marker(RED, 12, m))
            c.drawPath(pth, wb.marker(BLACK, 8, a))
    c.restore()
    if dt >= 0:
        h = 170 * ease_out(clamp01(dt / 0.12))
        c.drawLine(ZONE[1] + 100, y + 30, ZONE[1] + 100, y + 30 - h, wb.marker(RED, 16))
    return None


def pull_dy(T):
    return 60 * ease_in_out(clamp01((T - (t_drop() - 0.12)) / 0.12))


def worker_hands(T):
    x, y, s = WK
    hy = y - 290 * s
    lh_rest = (x - 70 * s, hy + 170 * s)
    rh_rest = (x + 70 * s, hy + 170 * s)
    car_mid = (CAR_X[1] + car_offset(T), BELT[2] - 80)
    t_pt, t_reach = tb(1, 7), tb(1, 9)
    k_pt = ease_out(clamp01((T - t_pt) / 0.18)) * (1 - ease_in_out(clamp01((T - t_reach) / 0.3)))
    d = (car_mid[0] - x, car_mid[1] - (hy + 80 * s))
    n = math.hypot(*d)
    point = (x + d[0] / n * 160 * s, hy + 80 * s + d[1] / n * 160 * s)
    lh = (lerp(lh_rest[0], point[0], k_pt), lerp(lh_rest[1], point[1], k_pt))
    handle = (CORD_X, HANDLE_Y + 30 + pull_dy(T))
    k_r = ease_out(clamp01((T - t_reach) / 0.25))
    rh = (lerp(rh_rest[0], handle[0], k_r), lerp(rh_rest[1], handle[1], k_r))
    return lh, rh


def worker_fn(c, k, T):
    x, y, s = WK
    t0 = tb(1, 5)
    p = clamp01((T - t0) / (tb(1, 5.8) - t0))
    c.save()
    tip = _reveal(c, x, y - 380 * s, 400 * s, p)
    lh, rh = worker_hands(T)
    dt = T - t_drop()
    shake = 6 * math.sin(dt * 40) * math.exp(-dt * 8) if dt > 0 else 0.0
    draw_worker(c, x, y, s, lh, rh, shake)
    c.restore()
    sc = pop_scale(T - tb(1, 6))
    if sc > 0:
        with K.at(c, x + 40, y - 290 * s - 150, 0, sc):
            c.drawCircle(0, 0, 46, K.paint("#FFFFFF"))
            c.drawCircle(0, 0, 46, wb.marker(RED, 7))
            c.drawLine(0, -26, 0, 8, wb.marker(RED, 12))
            c.drawCircle(0, 24, 6, K.paint(RED))
    return tip


def cord_fn(c, k, T):
    dy = pull_dy(T)
    yb = RAIL_Y + (HANDLE_Y + dy - RAIL_Y) * clamp01(k)
    slack = 22 * (1 - dy / 60)
    p = skia.Path()
    p.moveTo(CORD_X, RAIL_Y)
    p.quadTo(CORD_X + slack, (RAIL_Y + yb) / 2, CORD_X, yb)
    c.drawPath(p, wb.marker(ACC, 7))
    if k >= 1:
        c.drawPath(rect(CORD_X, HANDLE_Y + 25 + dy, 34, 56, 10), wb.marker(ACC, 9))
        return None
    return CORD_X, yb


LAMP_PULSE = []                   # 黄灯再闪一下的时刻（屏 3“黄灯一亮”）


def lamp_fn(c, k, T):
    if T < t_drop():
        return None
    red = T >= T_STOP()
    col = RED if red else YELLOW
    t_on = T_STOP() if red else t_drop()
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
    for tp in [t_on] + [f() for f in LAMP_PULSE]:
        if 0 <= T - tp < 0.6:
            K.ripple(c, x, y, T - tp, col, 230, 8, 0.8, 0.6)
    return None


LEAD_STEPS = [2010, 1930, LD[0]]
LEAD_K = 2                        # 屏 3 第几拍开始跑（等镜头移动完）


def leader_fn(c, k, T):
    x, y, s = LD
    bp = beat_pos(T) - (BOUNDS[2][0] + LEAD_K)
    if bp < 0:
        return None
    if bp < 2:
        i = int(math.floor(bp))
        f = bp - i
        xx = lerp(LEAD_STEPS[i], LEAD_STEPS[i + 1], ease_in_out(f))
        run, phase = 1.0, f
    else:
        settle = clamp01((bp - 2) / 0.5)
        xx, run, phase = x, 1 - settle, 0.5 * (1 - settle)
    hd = 0.0
    if T_SHAKE() <= T < T_SHAKE() + 0.8:
        dt = T - T_SHAKE()
        hd = 14 * math.sin(dt * 2 * math.pi * 3.2) * (1 - clamp01(dt / 0.8))
    draw_leader(c, xx, y, s, phase % 1.0, run, hd)
    if run > 0.05:
        for i in range(3):
            yy = y - 230 + i * 50
            c.drawLine(xx + 85, yy, xx + 85 + 55 * run - i * 12, yy, wb.marker(BLACK, 7, 0.7 * run))
    for i in range(3):
        dt = T - tb(2, LEAD_K + i)
        if 0 <= dt < 0.3:
            K.ripple(c, LEAD_STEPS[i], y + 4, dt, "#8A8F99", 60, 5, 0.6, 0.3)
    return None


T_SHAKE = None


def bubble_fn(j, k):
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k))
        if sc <= 0:
            return None
        with K.at(c, LD[0] - 20, 1640, 0, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(-85, -70, 170, 140), 40, 40, K.paint("#FFFFFF"))
            c.drawPath(bubble(0, 0, 170, 140, -1), wb.marker(BLACK, 7))
            K.text(c, "修", 0, 0, 96, "hand", BLACK)
        return None
    return fn


def timer_fn(j, k):
    """工位计时圈：车进工位就开始走，走满（车到工位尽头）那一刻刹停；最后一段变红。"""
    def fn(c, kk, T):
        t0 = tb(j, k)
        if T < t0:
            return None
        x, y, r = TIMER
        a = pop_scale(T - t0)
        f = clamp01((T - t0) / max(0.1, T_STOP() - t0))
        col = RED if f > 0.75 else YELLOW
        with K.at(c, x, y, 0, a):
            c.drawCircle(0, 0, r, K.paint("#FFFFFF"))
            c.drawCircle(0, 0, r, wb.marker(BLACK, 6))
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(-r + 10, -r + 10, 2 * r - 20, 2 * r - 20), -90, 360 * f)
            c.drawPath(arc, wb.marker(col, 12))
            ang = math.radians(-90 + 360 * f)
            c.drawLine(0, 0, (r - 14) * math.cos(ang), (r - 14) * math.sin(ang), wb.marker(BLACK, 5))
        return None
    return fn


def zone_path() -> skia.Path:
    x0, x1 = ZONE
    y = BELT[2]
    p = skia.Path()
    for xx in range(int(x0), int(x1), 50):
        p.moveTo(xx, y - 150)
        p.lineTo(min(xx + 28, x1), y - 150)
    return join(p, P((x0, y - 170), (x0, y + 60)), P((x1, y - 170), (x1, y + 60)))


# ---------------------------------------------------------------- 屏 5–6：不停线会怎样（四个工位）

ST_X = [600, 1000, 1400, 1800]
ST_Y = 3300
PARTS = [BLUE, GREEN, ORANGE]
FLOW = {}                         # 分镜里填：leave（离开工位 1）、arrive（到工位 2/3/4 的拍时刻函数）、scatter


def flow_car_fn(c, k, T):
    """带“!”的车从工位 1 往后走，每到一个工位加一块零件；最后拆开（零件飞散）。"""
    arr = [f() for f in FLOW["arrive"]]
    pos = ST_X[0]
    for i, ta in enumerate(arr):
        t0 = ta - 0.35
        if T >= t0:
            pos = lerp(ST_X[i], ST_X[i + 1], ease_in_out(clamp01((T - t0) / 0.35)))
    a = ease_out(clamp01((T - tb(*FLOW["in"])) / 0.25))
    with K.at(c, pos, ST_Y - 25, 0, 0.6 + 0.4 * pop_scale(T - tb(*FLOW["in"]))):
        pth = car_path(0, 0)
        c.drawPath(pth, K.paint(RED, 0.18 * a))
        c.drawPath(pth, wb.marker(RED, 10, a))
        c.drawLine(0, -175, 0, -125, wb.marker(RED, 12, a))
        c.drawCircle(0, -105, 7, K.paint(RED, a))
    ts = FLOW["scatter"]()
    for i, ta in enumerate(arr):
        if T < ta:
            continue
        sc = pop_scale(T - ta)
        bx, by = pos - 40 + i * 40, ST_Y - 130 - i * 8
        if T >= ts:                                    # 拆开：零件往外飞
            dt = T - ts
            ang = (-2.3, -1.57, -0.8)[i]
            bx += math.cos(ang) * 260 * ease_out(clamp01(dt / 0.5))
            by += math.sin(ang) * 260 * ease_out(clamp01(dt / 0.5)) + 300 * max(0, dt - 0.3) ** 2
        with K.at(c, bx, by, (i - 1) * 8, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(-30, -22, 60, 44), 6, 6, K.paint(K.tint(PARTS[i], 0.6)))
            c.drawRoundRect(skia.Rect.MakeXYWH(-30, -22, 60, 44), 6, 6, wb.marker(PARTS[i], 7))
    return None


def stations_path() -> skia.Path:
    parts = [rect((ST_X[0] + ST_X[-1]) / 2, ST_Y + 12, ST_X[-1] - ST_X[0] + 380, 40, 18)]
    for x in ST_X:
        parts.append(P((x - 190, ST_Y - 230), (x - 190, ST_Y + 70)))
    parts.append(P((ST_X[-1] + 190, ST_Y - 230), (ST_X[-1] + 190, ST_Y + 70)))
    return join(*parts)


# ---------------------------------------------------------------- 屏 7：书中观点图标

def lamp_icon(x, y, r=40) -> skia.Path:
    parts = [circle(x, y, r)]
    for i in range(6):
        a = -math.pi / 2 + (i - 2.5) * 0.45
        parts.append(P((x + math.cos(a) * (r + 12), y + math.sin(a) * (r + 12)),
                       (x + math.cos(a) * (r + 36), y + math.sin(a) * (r + 36))))
    return join(*parts)


def source_icon(x, y) -> skia.Path:
    """源头：一个水龙头 + 往下的水滴。"""
    drop = skia.Path()
    drop.moveTo(x + 40, y + 10)
    drop.quadTo(x + 70, y + 60, x + 40, y + 70)
    drop.quadTo(x + 10, y + 60, x + 40, y + 10)
    return join(P((x - 60, y - 40), (x + 50, y - 40), (x + 50, y - 10)), rect(x - 10, y - 60, 40, 30, 6), drop)


def nopass_icon(x, y) -> skia.Path:
    return join(P((x - 60, y), (x + 50, y)), P((x + 25, y - 25), (x + 55, y), (x + 25, y + 25)),
                circle(x, y, 62), P((x - 44, y - 44), (x + 44, y + 44)))


# ---------------------------------------------------------------- 屏 8：小李、主管、客户

PEOPLE = [(560, 5700, "小李"), (1150, 5700, "主管"), (1740, 5700, "客户")]
HOLES = {}                        # 分镜里填：每份方案上“坑”出现/变大的拍时刻


def hole_doc_fn(i):
    def fn(c, kk, T):
        x, y = PEOPLE[i][0] + 120, PEOPLE[i][1] - 260
        t_in = HOLES["doc"][i]()
        if T < t_in:
            return None
        sc = pop_scale(T - t_in)
        grow = [ease_out_back(clamp01((T - f()) / 0.3)) for f in HOLES["grow"]]
        r = 14 + (i * 10) * grow[0] + (i * 8 + 6) * grow[1]
        with K.at(c, x, y, 0, sc):
            c.drawPath(doc(0, 0, 130, 170, 3), K.paint("#FFFFFF"))
            c.drawPath(doc(0, 0, 130, 170, 3), wb.marker(BLACK, 7))
            c.drawOval(skia.Rect.MakeXYWH(-r, 30 - r * 0.55, 2 * r, 1.1 * r), K.paint("#3A3A44"))
        return None
    return fn


# ---------------------------------------------------------------- 分镜（屏 j 的拍号由旁白关键词吸附到实测拍点）

def scene(j, view):
    tag = SCREENS[j][1]
    jj = b.shot("", tag, view=view, bars=4)
    assert jj == j
    return j


# 屏 1：小李返工第 3 遍（同 v3）
j = scene(0, VA)
b.path(j, 0, 0.8, join(desk(780, 990, 380), stick(600, 1140, 0.85, "hold", tie=True, hair=True)), sfx="wood_high")
b.path(j, 0.8, 0.95, face(600, 1140, 0.85, "sad"))
b.custom(j, 1, 1.3, pop_text("小李 · 打工人", 720, 790, 54, BLACK, j, 1, "sans_medium"), sfx="pop")
b.path(j, 1.3, 1.9, doc(*LC, 150, 190), BLACK, 9)
b.custom(j, 2, 2.9, loop_fn, sfx="wood_high")
b.custom(j, 3, 3.3, slam_text("第3遍", LC[0], 520, 96, RED, j, 3), sfx="rim")
b.hit(j, 4, "shaker", 0.6, "返工圈开始按拍转")
b.custom(j, 6, 6.3, pop_text("补", 1030, 700, 80, GREEN, j, 6), sfx="pop")
b.path(j, 6.3, 6.8, check(1030, 830, 42), GREEN, 11)
b.custom(j, 7, 7.3, pop_text("坏", 1680, 700, 80, RED, j, 7), sfx="rim", gain=0.7)
b.path(j, 7.3, 7.8, cross(1680, 830, 38), RED, 11)
b.hit(j, 8, "wood_low", 0.8, "返工圈转满一圈")

# 屏 2：小王看到毛病，拉绳（drop）
KD = DROP - BOUNDS[1][0]
j = scene(1, VB)
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
x0, x1, by = BELT
b.path(j, 0, 0.7, book(540, 1310, 150, 100), GREEN, 7, sfx="wood_low")
b.text(j, 1, 1.8, "丰田模式", 760, 1310, 60, GREEN, sfx="pop")
b.path(j, 2, 2.8, join(rect((x0 + x1) / 2, by + 12, x1 - x0 + 40, 46, 20),
                       *[circle(xx, by + 12, 13) for xx in range(x0 + 40, x1, 110)]), sfx="wood_high")
T_IN = lambda: tb(1, 3)
b.custom(j, 3, 3.3, cars_fn, sfx="pop")
b.custom(j, 5, 5.8, worker_fn, sfx="wood_high")
b.text(j, 5.8, 5.95, "员工", WK[0], 2225, 80, BLUE)
b.text(j, 5.95, 6.0, "小王", WK[0], 2310, 62, BLUE)
b.hit(j, 6, "pop", 0.9, "小王头顶冒“!”")
b.hit(j, 7, "rim", 0.8, "小王指向那辆车，车身标红")
b.path(j, 8, 8.5, join(P((x0, RAIL_Y), (1760, RAIL_Y)), P((LAMP[0], RAIL_Y), (LAMP[0], LAMP[1] - LAMP[2])),
                       circle(*LAMP)), BLACK, 9, sfx="wood_high")
b.custom(j, 8.5, 8.9, cord_fn)
b.hit(j, 9, "shaker", 0.7, "小王伸手抓住安灯绳")
b.custom(j, KD, KD + 1, lamp_fn, sfx="kick", gain=0.9, )

# 屏 3：黄灯一亮，组长老张跑来
j = scene(2, VB2)
k_lamp = kb(j, wt(4, 0, 0.5), lo=1)
LAMP_PULSE.append(lambda: tb(2, k_lamp))
b.hit(j, k_lamp, "ding", 0.8, "黄灯再闪一下")
LEAD_K = max(k_lamp + 1, 2)
b.custom(j, LEAD_K, LEAD_K + 0.1, leader_fn, sfx="bongo_low", gain=0.9)
b.hit(j, LEAD_K + 1, "bongo_low", 0.9, "老张脚步")
b.hit(j, LEAD_K + 2, "bongo_low", 0.9, "老张脚步（站定）")
b.text(j, LEAD_K + 2.4, LEAD_K + 2.75, "组长", LD[0], 2225, 80, RED)
b.text(j, LEAD_K + 2.75, LEAD_K + 3.0, "老张", LD[0], 2310, 62, RED)

# 屏 4：车走出工位前修不好，才停线
j = scene(3, VB2)
b.path(j, 0, 0.8, zone_path(), BLUE, 7, sfx="wood_high")
b.text(j, 0.8, 1.3, "工位", (ZONE[0] + ZONE[1]) / 2, BELT[2] + 115, 70, BLUE)
k_t = kb(j, wt(5, 0, 0.55), lo=2)
b.custom(j, k_t, k_t + 0.3, timer_fn(j, k_t), sfx="pop")
k_fix = kb(j, wt(5, 0, 0.85), lo=k_t + 1)
b.custom(j, k_fix, k_fix + 0.3, bubble_fn(j, k_fix), sfx="pop")
k_x = kb(j, wt(6, 0, 0.4), lo=k_fix + 1)
b.path(j, k_x, k_x + 0.35, cross(LD[0] - 20, 1640, 75), RED, 13, sfx="rim")
T_SHAKE = lambda: tb(3, k_x)
k_stop = kb(j, wt(6, 1, 0.7), lo=k_x + 1)
T_STOP = lambda: tb(3, k_stop)
b.hit(j, k_stop, "tom", 0.9, "车辆刹停 + 停止线 + 红灯")
b.custom(j, k_stop + 1, k_stop + 1.3, slam_text("停！", 660, 1700, 150, RED, j, k_stop + 1), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_stop, 10.0), (k_stop + 1, 18.0)]

# 屏 5：不停线——带毛病的车一路往下走，每个工位都往上装零件
j = scene(4, VC)
b.path(j, 0, 0.9, stations_path(), BLACK, 8, sfx="wood_high")
for i, x in enumerate(ST_X):
    b.text(j, 0.9 + i * 0.1, 1.0 + i * 0.1, f"工位{i + 1}", x, ST_Y + 140, 76, BLUE)
b.custom(j, 1, 1.3, pop_text("要是不停", 640, 2950, 84, RED, j, 1, "hand"), sfx="rim", gain=0.6)
k_in = kb(j, wt(7, 1, 0.1), lo=2)
FLOW["in"] = (j, k_in)
b.custom(j, k_in, k_in + 0.3, flow_car_fn, sfx="pop")
k_a = kb(j, wt(8, 1, 0.1), lo=k_in + 2)
FLOW["arrive"] = [lambda i=i: tb(4, k_a + i) for i in range(3)]
for i in range(3):
    b.hit(j, k_a + i, ("wood_high", "wood_low", "bongo_high")[i], 0.8, f"到工位{i + 2}，装上一块零件")
FLOW["scatter"] = lambda: 1e9

# 屏 6：最后才发现，拆开再装一遍 = 返工
j = scene(5, VC)
k_find = kb(j, wt(9, 0, 0.6), lo=1)
b.custom(j, k_find, k_find + 0.3, pop_text("！", ST_X[-1] + 40, 2830, 160, RED, j, k_find), sfx="rim")
k_sc = kb(j, wt(9, 1, 0.3), lo=k_find + 1)
FLOW["scatter"] = lambda: tb(5, k_sc)
b.hit(j, k_sc, "clap", 0.9, "零件拆开飞散")
b.path(j, k_sc + 1, k_sc + 1.8, arrow((ST_X[-1], ST_Y + 230), (ST_X[0], ST_Y + 230), -0.18, 50), RED, 12,
       sfx="wood_high")
k_rw = kb(j, wt(10, 0, 0.7), lo=k_sc + 2)
b.custom(j, k_rw, k_rw + 0.3, slam_text("返工", (ST_X[0] + ST_X[-1]) / 2, ST_Y + 470, 130, RED, j, k_rw), sfx="kick",
         gain=0.8)
b.shots[j].shake = [(k_rw, 14.0)]

# 屏 7：书中观点——当场亮出来、在源头修好、不往下传
j = scene(6, VD)
b.path(j, 0, 0.6, book(470, 3950, 150, 100), GREEN, 7, sfx="wood_low")
b.text(j, 0.6, 1.2, "书中观点", 700, 3950, 54, GREEN)
ROWS = [(lamp_icon(560, 4160), "当场亮出来", YELLOW), (source_icon(560, 4380), "在源头修好", BLUE),
        (nopass_icon(560, 4600), "不往下传", RED)]
lo = 1
for ci, (icon, txt, col) in enumerate(ROWS):
    k = kb(j, wt(11, ci, 0.15), lo=lo)
    b.path(j, k, k + 0.6, icon, col, 9, sfx=("ding", "wood_high", "rim")[ci])
    b.text(j, k + 0.4, k + 0.4 + 0.18 * len(txt), txt, 1130, 4170 + ci * 220, 84, BLACK)
    lo = k + 1

# 屏 8：小李的方案带坑交出去，越挖越大又回来
j = scene(7, VE)
b.path(j, 0, 0.8, join(desk(PEOPLE[0][0] + 60, PEOPLE[0][1] - 150, 300),
                       stick(PEOPLE[0][0] - 90, PEOPLE[0][1], 0.8, "hold", tie=True, hair=True)), sfx="wood_high")
b.text(j, 0.8, 1.2, "小李", PEOPLE[0][0] - 90, PEOPLE[0][1] + 75, 72, BLACK)
k_hole = kb(j, wt(12, 0, 0.75), lo=1)
HOLES["doc"] = [lambda: tb(7, k_hole)]
b.custom(j, k_hole, k_hole + 0.3, hole_doc_fn(0), sfx="pop")
k_give = kb(j, wt(12, 1, 0.5), lo=k_hole + 1)
b.path(j, k_give, k_give + 0.6, arrow((720, 5380), (960, 5380), -0.2, 40), BLACK, 9, sfx="wood_high")
k_p1 = kb(j, wt(13, 0, 0.2), lo=k_give + 1)
k_p2 = kb(j, wt(13, 0, 0.7), lo=k_p1 + 1)
for i, kk in ((1, k_p1), (2, k_p2)):
    x, y, name = PEOPLE[i]
    b.path(j, kk, kk + 0.6, stick(x - 90, y, 0.8, "down", tie=(i == 1)), sfx="pop")
    b.text(j, kk + 0.6, kk + 0.9, name, x - 90, y + 75, 72, BLACK)
    HOLES["doc"].append(lambda kk=kk: tb(7, kk))
    b.custom(j, kk + 0.3, kk + 0.4, hole_doc_fn(i))
b.path(j, k_p2 - 0.4, k_p2 + 0.1, arrow((1310, 5380), (1550, 5380), -0.2, 40), BLACK, 9)
k_g1 = kb(j, wt(13, 1, 0.3), lo=k_p2 + 1)
HOLES["grow"] = [lambda: tb(7, k_g1), lambda: tb(7, k_g1 + 1)]
b.hit(j, k_g1, "rim", 0.7, "坑变大")
b.hit(j, k_g1 + 1, "rim", 0.8, "坑更大")
k_back = kb(j, wt(13, 2, 0.3), lo=k_g1 + 2)
b.path(j, k_back, k_back + 0.8, arrow((1700, 5850), (520, 5850), -0.12, 50), RED, 12)
b.custom(j, k_back, k_back + 0.3, slam_text("第3遍", 1110, 6010, 100, RED, j, k_back), sfx="kick", gain=0.75)

# 屏 9：第一，发现问题当场喊停，拉同事看五分钟
j = scene(8, VF1)
b.custom(j, 0, 0.3, pop_text("① 当场喊停", 1100, 6280, 90, BLUE, j, 0), sfx="pop")
b.path(j, 1, 1.8, join(desk(1020, 6720, 340), doc(1060, 6640, 110, 140, 3)), sfx="wood_high")
k_up = kb(j, wt(14, 2, 0.2), lo=2)
b.path(j, k_up, k_up + 0.7, stick(760, 6900, 0.85, "up", tie=True, hair=True), BLACK, 10, sfx="rim")
b.custom(j, k_up + 1, k_up + 1.3, pop_text("等一下！", 620, 6420, 70, RED, j, k_up + 1), sfx="pop")
k_mates = kb(j, wt(15, 0, 0.3), lo=k_up + 2)
b.path(j, k_mates, k_mates + 0.7, join(stick(1330, 6900, 0.8, "point"), stick(1530, 6900, 0.8, "down")), BLUE, 9,
       sfx="wood_high")
k_clock = kb(j, wt(15, 1, 0.6), lo=k_mates + 1)
b.path(j, k_clock, k_clock + 0.6, join(wb.clock(1500, 6420, 80), wb.hands_at(1500, 6420, 80, 12, 5)), BLACK, 8,
       sfx="ding")
b.text(j, k_clock + 0.6, k_clock + 1.0, "5分钟", 1500, 6560, 60, RED)

# 屏 10：第二，在源头修，别在后面打补丁
j = scene(9, VF2)
b.custom(j, 0, 0.3, pop_text("② 在源头修", 1150, 7280, 90, BLUE, j, 0), sfx="pop")
BOX = [(600, "方案"), (1100, "主管"), (1600, "客户")]
b.path(j, 1, 1.8, join(*[rect(x, 7650, 280, 180, 20) for x, _ in BOX], arrow((750, 7650), (950, 7650), 0, 36),
                       arrow((1250, 7650), (1450, 7650), 0, 36)), BLACK, 9, sfx="wood_high")
for x, name in BOX:
    b.text(j, 1.8, 2.0, name, x, 7650, 64, BLACK)
k_src = kb(j, wt(16, 1, 0.4), lo=2)
b.path(j, k_src, k_src + 0.6, circle(600, 7650, 190), RED, 11, sfx="rim")
b.text(j, k_src + 0.6, k_src + 1.0, "这里修", 600, 7900, 72, RED)
k_patch = kb(j, wt(16, 2, 0.5), lo=k_src + 1)
for i, x in enumerate((1100, 1600)):
    b.custom(j, k_patch, k_patch + 0.3, pop_path(join(rect(x + 90, 7580, 80, 60, 8), P((x + 60, 7580), (x + 120, 7580))),
                                                  x + 90, 7580, ORANGE, 6, j, k_patch, fill="#FBE3C8"),
             sfx="pop" if i == 0 else None)
b.path(j, k_patch + 1, k_patch + 1.4, join(cross(1190, 7580, 50), cross(1690, 7580, 50)), RED, 11, sfx="rim")

# 屏 11：第三，跟团队说好：喊停不挨骂
j = scene(10, VF3)
b.custom(j, 0, 0.3, pop_text("③ 说好规矩", 1100, 8280, 90, BLUE, j, 0), sfx="pop")
b.path(j, 1, 1.7, rect(1100, 8640, 760, 420, 30), BLACK, 9, sfx="wood_high")
b.text(j, 1.7, 2.3, "团队约定", 1100, 8510, 70, BLACK)
k_rule = kb(j, wt(17, 1, 0.55), lo=3)
b.text(j, k_rule, k_rule + 1.0, "喊停不挨骂", 1060, 8690, 92, RED, sfx="pop")
b.path(j, k_rule + 1, k_rule + 1.5, check(1400, 8690, 50), GREEN, 13, sfx="ding")
b.path(j, k_rule + 1.5, k_rule + 2.1, join(stick(640, 8960, 0.6, "point"), stick(1560, 8960, 0.6, "point")), BLACK, 8)

# 屏 12：评论区追问 + 下一讲
j = scene(11, VG)
b.path(j, 0, 0.8, bubble(1150, 9560, 900, 230, -1), BLACK, 9, sfx="wood_high")
k_q = kb(j, wt(18, 0, 0.3), lo=1)
b.text(j, k_q, k_q + 1.6, "你上次为啥没喊停？", 1150, 9560, 76, RED, sfx="pop")
k_c = kb(j, wt(18, 1, 0.9), lo=k_q + 2)
b.custom(j, k_c, k_c + 0.3, pop_text("评论区聊聊", 1150, 9800, 64, BLACK, j, k_c, "sans_medium"), sfx="ding")
k_n = kb(j, wt(19, 0, 0.2), lo=k_c + 1)
b.path(j, k_n, k_n + 0.6, rect(1150, 10020, 900, 200, 24), BLUE, 8, sfx="wood_high")
b.text(j, k_n + 0.5, k_n + 0.8, "下一讲", 1150, 9965, 46, BLUE)
b.text(j, k_n + 0.8, k_n + 2.2, "活儿做得越多，为什么越乱？", 1150, 10055, 62, BLACK)

# ---------------------------------------------------------------- 时间轴

ep = core.Episode(NO, KEY, CONCEPT, TITLE, ACC, b.shots, refs=[], publish_title=f"Vibe知识大赏｜{TITLE}",
                  hashtags=TAGS, cover_title=COVER_TITLE, cover_sub="丰田模式 · 停线", cover_shot=COVER_SHOT,
                  notes=NOTES)
for s, (k0, k1) in zip(b.shots, BOUNDS):
    s.b0, s.t0, s.t1 = k0, core.bt(k0), core.bt(k1)
b.shots[0].t0 = S
b.shots[-1].t1 = S + END_LOCAL
b.attach(ep)


def captions():
    caps = []
    for li, (text, pieces) in enumerate(LINES):
        pend = None
        for ci, cap in enumerate(pieces):
            t = STARTS[li] + CLAUSE_T[li][ci]
            if cap is None:
                pend = t if pend is None else pend
                continue
            caps.append([pend if pend is not None else t, None, cap])
            pend = None
    for i, cp in enumerate(caps):
        cp[1] = caps[i + 1][0] if i + 1 < len(caps) else None
    return caps


def build():
    return ep
