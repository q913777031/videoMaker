"""《丰田模式》01 停线：同一个问题，为什么总返工？（白板手绘 + AI 旁白，竖屏 2:3，约 2 分多钟 + 频道片尾）

第二版（用户反馈：“修不好才停线”说法不准、语气平淡、结尾前要有身边的例子、要贴心、开头加“黄金 3 秒”）：
- 0–3 秒：“丰田模式”四个大字逐拍砸出（rim / clap / tom / kick + 震屏 + 闪白），副标弹出，镜头推到小李，旁白同时进；
- 丰田做法：小王发现毛病 → 拉绳（= 音乐 drop）→ 黄灯，组长赶来帮忙 → 工位里修好线照常走；修不完就整条线停下来先修好；
- 为什么停：停线亏？不停 → 带毛病的车一路往下装 → 最后拆开再装 = 返工 → 书中：宁可停一下，当场亮出来，源头修好；
- 身边的例子：一颗“小问题”雪球沿着之字形斜坡滚（对账 → 客户 → 牙疼），每站被糊住、盖住、越滚越大，
  “你怕麻烦，麻烦就会找上你”——小李背过身，大球咚地砸到他（强拍，重击 + 震屏 + 闪白）；
- 三条做法（示意）→ 贴心收尾：早点停，少返工，准点下班 → 评论区追问 + 下一讲预告。
节奏：一屏一件事，每屏 ≥5 秒，画完讲完停 ≥1.5 秒，切在实测半小节线上，切屏镜头移动 1.1 秒缓入缓出。
配乐：music/bgm.m4a 按实测拍点在小节线上循环延长（第 96–136 拍这一段，接缝 40ms 交叉淡化），拉绳仍对 drop，结尾落在原曲最后一击。
旁白：合成可插拔，见 NARRATOR / synthesize()。出处与说明见 NOTES。
"""

import importlib
import math

import numpy as np
import skia
from scipy import signal

from adler import core
from adler import kit as K
from engine import audio
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp
from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, ORANGE, RED, Board, P, arrow, book, bubble, check, circle, cross,
                               desk, doc, face, join, rect, stick)

# ---------------------------------------------------------------- 旁白合成（可插拔：换后端只改这里）
# backend="engine.audio"：本仓库 Narrator（ZipVoice / Kokoro）；其余值写成 "包.模块:函数"，
# 该函数签名 fn(text, **options) -> (samples: np.ndarray, sample_rate: int)，由 synthesize() 统一转成 44.1kHz、裁静音。
NARRATOR = {"backend": "engine.audio", "voice": "zv_yunjian", "prompt_speed": 0.95, "speed": 1.0, "num_steps": 8}


def synthesize(texts):
    """把每句旁白合成为 44.1kHz 单声道（首尾静音已裁剪）。"""
    cfg = dict(NARRATOR)
    be = cfg.pop("backend")
    if be == "engine.audio":
        nar = audio.Narrator(cfg["voice"], prompt_speed=cfg.get("prompt_speed", 1.0))
        return [nar.generate(t, cfg.get("speed", 1.0), cfg.get("num_steps", 4)) for t in texts]
    mod, fn = be.split(":")
    f = getattr(importlib.import_module(mod), fn)
    out = []
    for t in texts:
        x, sr = f(t, **cfg.get("options", {}))
        x = np.asarray(x, np.float64).reshape(-1)
        if sr != audio.SR:
            g = math.gcd(audio.SR, sr)
            x = signal.resample_poly(x, audio.SR // g, sr // g)
        out.append(audio._trim(x))
    return out


NO, KEY, CONCEPT = 1, "andon", "停线"
TITLE = "同一个问题，为什么总返工？"
ACC = "#C8102E"
YELLOW, HAT, SUIT, BOARD_C = "#E0A21B", "#F2B705", "#CFE0F5", "#C89B63"
TAGS = "#丰田模式 #精益管理 #读书 #打工人 #职场 #返工"
COVER_TITLE = "同一个问题|为什么总【返工】"
DROP = 32
COMMA = 0.25
HOLD = 1.55
MIN_BEATS = 10
INTRO_BEATS = 6                   # 四字逐拍落定（第 0–3 拍，1.75 秒落完）后整体停留约 1.6 秒，再用 1.3 秒缓推到小李
EXTRA_HOLD = {12: 1.0}            # “麻烦就会找上你”之后大球砸下（强拍），再多停一会儿

core.SERIES.update(name="丰田模式", count="第一季", prefix="丰田")

# 旁白：(整句, 字幕[按顺序拼起来等于整句（不计标点）；按字的位置换算出现时刻], 与同屏上一句的间隔秒)
LINES = [
    ("同一个问题，已经返工第三遍了。", ["同一个问题", "已经【返工】第三遍了"], 0.0),
    ("补了又坏，坏了又补，人都快麻了。", ["补了又坏，坏了又补", "人都快【麻了】"], 0.4),
    ("丰田的做法，正好反过来：", ["丰田的做法，正好【反过来】"], 0.0),
    ("工人一发现毛病，马上拉一下头顶的绳子。", ["工人一发现毛病", "马上【拉】一下头顶的绳子"], 0.25),
    ("黄灯一亮，组长立刻赶过来帮忙。", ["黄灯一亮", "【组长】立刻赶过来帮忙"], 0.0),
    ("如果在这个工位里能修好，生产线照常往前走；", ["如果在这个工位里", "能修好", "生产线照常往前走"], 0.0),
    ("要是修不完，就让整条线停下来，先把问题修好。", ["要是修不完", "就让整条线【停下来】", "先把问题【修好】"], 0.7),
    ("停线多亏啊，为什么还要停？", ["停线多亏啊", "为什么还要停？"], 0.0),
    ("因为不停的话，带毛病的车会继续往下走。", ["因为不停的话", "带毛病的车", "会继续往下走"], 0.0),
    ("后面每个工位，都在它上面接着装零件。", ["后面每个工位", "都在它上面接着装零件"], 0.45),
    ("等到最后才发现，只能拆开，重新装一遍。", ["等到最后才发现", "只能拆开，重新装一遍"], 0.0),
    ("这就是返工。", ["这就是【返工】"], 0.75),
    ("所以丰田宁可停一下，也要当场把问题摆出来，在源头修好。", ["所以丰田宁可停一下", "也要当场把问题摆出来", "在【源头】修好"], 0.0),
    ("我们身边，这种事天天都有。", ["我们身边", "这种事【天天都有】"], 0.0),
    ("报表里有个数对不上，先混过去，到月底对账就全乱了。", ["报表里有个数对不上", "先混过去", "到月底对账就【全乱了】"], 0.0),
    ("方案里有个漏洞，想着先交了再说，到了客户那里，漏洞越来越大。", ["方案里有个漏洞", "想着先交了再说", "到了客户那里", "漏洞【越来越大】"], 0.0),
    ("牙有点疼，先忍一忍，结果拖到要做根管。", ["牙有点疼，先忍一忍", "结果拖到要做【根管】"], 0.0),
    ("遇到问题先应付、先遮住，它就会一路往下走，越滚越大。", ["遇到问题先应付、先遮住", "它就会一路往下走", "【越滚越大】"], 0.0),
    ("你怕麻烦，麻烦就会找上你。", ["你怕麻烦", "麻烦就会【找上你】"], 0.8),
    ("所以，下次发现问题，先停一停。", ["所以，下次发现问题", "先【停一停】"], 0.0),
    ("第一，当场说出来，拉上同事一起看五分钟。", ["第一，当场说出来", "拉上同事一起看五分钟"], 0.6),
    ("第二，从源头上修，别在后面打补丁。", ["第二，从【源头】上修", "别在后面打补丁"], 0.0),
    ("第三，跟团队约好：喊停的人，不挨骂。", ["第三，跟团队约好", "喊停的人，【不挨骂】"], 0.0),
    ("早一点停下来，后面就少一点返工，你也能早点下班。", ["早一点停下来", "后面就少一点返工", "你也能【早点下班】"], 0.0),
    ("你手上有没有一个问题，一直想着以后再说？", ["你手上有没有一个问题", "一直想着以后再说？"], 0.0),
    ("写在评论区吧，别一个人扛着。", ["写在评论区吧", "别一个人扛着"], 0.6),
    ("下一讲：活儿越做越多，为什么反而越乱？", ["下一讲：活儿越做越多", "为什么反而越乱？"], 0.6),
]
# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1), ([2, 3], "丰田模式 · 书中做法", 2), ([4], "丰田模式 · 书中做法", 2),
    ([5, 6], "丰田模式 · 书中做法", 2), ([7], "为什么要停", 3), ([8, 9], "为什么要停", 4), ([10, 11], "为什么要停", 4),
    ([12], "书中观点", 5), ([13, 14], "身边的例子", 6), ([15], "身边的例子", 6), ([16], "身边的例子", 6),
    ([17, 18], "身边的例子", 6), ([19, 20], "做法一 · 示意", 7), ([21], "做法二 · 示意", 8), ([22], "做法三 · 示意", 9),
    ([23], "早点下班", 10), ([24, 25, 26], "评论区见", 11),
]
GROUP = [s[2] for s in SCREENS]
SQUARE_SHOT = COVER_SHOT = 4      # 封面取景：小王、老张、红灯、“停！”、修好的勾

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way: 14 Management Principles from the World's Greatest Manufacturer "
    "(McGraw-Hill, 2004；第 2 版 2021)。中译本《丰田模式：精益制造的14项管理原则》，[美]杰弗瑞·莱克 著，机械工业出版社"
    "（珍藏版 2016 年 1 月；另有原书第 2 版）。译者未在网页上核实到，以版权页为准。",
    "本讲依据：原则 5——建立立即暂停以解决问题、从一开始就重视质量的文化（英文版第 11 章 Principle 5: Build a Culture of "
    "Stopping to Fix Problems, to Get Quality Right the First Time），涉及自働化（jidoka）与安灯（andon）。上屏与旁白均为转述。",
    "安灯流程：工人发现异常拉绳，先亮灯叫组长来帮忙；能在这个工位（定位停止点之前）处理好，线照常走；处理不完，整条线停下来，"
    "先把问题修好再开。旁白据此表述。灯色先黄后红为画面示意。参考：Lean Enterprise Institute 词条 Andon、Gemba Academy "
    "对丰田肯塔基工厂的介绍、leanblog.org 对“一拉就全线停”误解的辨析。",
    "“不停线 → 带毛病的车一路往下装 → 最后拆开再装 = 返工”“宁可停一下，当场亮出来，源头修好”为对原则 5 的通俗化转述。",
    "身边的例子（对账、方案、牙疼）与三条做法为据书中思路整理的示意；牙疼只画简笔牙齿，不涉及医疗建议。"
    "小李、小王、老张为虚构人物；“第三遍”“五分钟”“18:00”为示意，不是数据。",
    "下一讲拟题：02 拉动 · 只做下一步要的——“活儿越做越多，为什么反而越乱？”（原则 3：使用拉动式生产方式以避免生产过剩）。",
]

# ---------------------------------------------------------------- 旁白：合成、补逗号停顿


def stretch(x, text, target=COMMA):
    """逗号处补停顿到约 COMMA 秒（预期位置 ±12% 内最安静的 30ms 切开）。返回 (音频, 各分句起点秒)。"""
    clauses = text.rstrip("。：？！；").split("，")
    hz = [sum(1 for ch in cl if ch not in "。：？！、；") for cl in clauses]
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
        add = int(max(0.0, target - have) * audio.SR)
        cut = i * hop
        f = int(0.008 * audio.SR)
        left, right = x[:cut].copy(), x[cut:].copy()
        left[-f:] *= np.linspace(1, 0, f)
        right[:f] *= np.linspace(0, 1, f)
        x = np.concatenate([left, np.zeros(add), right])
        added += add
        starts.append((cut + add) / audio.SR - min(0.05, have / 2))
    return x, [0.0] + starts


RAW = synthesize([t for t, _, _ in LINES])
NATURAL_COMMA = {0, 1, 2, 3}     # 开场四句卡在片头与 drop 之间，逗号用 ZipVoice 自然停顿（不额外补）
CLIPS, CLAUSE_T = zip(*[stretch(x, t, 0.0 if i in NATURAL_COMMA else COMMA)
                        for i, (x, (t, _, _)) in enumerate(zip(RAW, LINES))])
DUR_L = [len(x) / audio.SR for x in CLIPS]

# ---------------------------------------------------------------- 配乐延长：在小节线上循环第 96–136 拍（51.2–72.4 秒这一段）

ORIG_BEATS = [dict(bt_) for bt_ in core.DET["beats"]]
ORIG_T = np.array([bt_["t"] for bt_ in ORIG_BEATS])
LOOP_A, LOOP_B = 96, 136
LOOP_N = LOOP_B - LOOP_A
XFADE = 0.04


def _grid(K):
    """插入 K 拍（4 的倍数，整小节，循环第 LOOP_A–LOOP_B 拍）后的虚拟拍点时刻。"""
    L = ORIG_T[LOOP_B] - ORIG_T[LOOP_A]
    ins = (K // LOOP_N) * L + (ORIG_T[LOOP_A + K % LOOP_N] - ORIG_T[LOOP_A])
    seq, ts = [], []
    for o in range(LOOP_B):
        seq.append(o)
        ts.append(ORIG_T[o])
    for i in range(K):
        o = LOOP_A + i % LOOP_N
        seq.append(o)
        ts.append(ORIG_T[LOOP_B] + (i // LOOP_N) * L + ORIG_T[o] - ORIG_T[LOOP_A])
    for o in range(LOOP_B, len(ORIG_T)):
        seq.append(o)
        ts.append(ORIG_T[o] + ins)
    return seq, np.array(ts), ins


def _even_at_or_after(T_arr, t):
    i = int(np.searchsorted(T_arr, t - 1e-6))
    return i + (i % 2)


def _schedule(T_arr):
    """返回 (每屏 [起拍, 止拍), 每句起点（配乐绝对秒）)。第 2 屏让“拉一下绳”句尾落在 drop；第 1 屏、片头往前推。"""
    n = len(LINES)
    st = [None] * n
    need2 = 0.3 + DUR_L[2] + LINES[3][2] + DUR_L[3]
    s2 = DROP - 10
    while T_arr[DROP] - T_arr[s2] < need2:
        s2 -= 2
    st[2] = T_arr[s2] + 0.3
    st[3] = T_arr[DROP] - DUR_L[3] - 0.03
    s1 = s2 - MIN_BEATS
    while True:
        t0 = T_arr[s1] + 0.05                                 # 第 1 句在镜头从片头缓推向小李时进
        if t0 + DUR_L[0] + LINES[1][2] + DUR_L[1] + 1.5 <= T_arr[s2]:
            break
        s1 -= 2
    st[0] = T_arr[s1] + 0.05
    st[1] = st[0] + DUR_L[0] + LINES[1][2]
    s0 = s1 - INTRO_BEATS
    if s0 < 0:
        raise ValueError("片头前没有足够的拍")
    bounds = [(s0, s1), (s1, s2), (s2, DROP + 4)]          # 拉绳（drop）后再停 4 拍
    b = DROP + 4
    for si in range(3, len(SCREENS)):
        lines = SCREENS[si][0]
        if b >= len(T_arr) - 1:
            return None
        t = T_arr[b] + 0.3
        for k, li in enumerate(lines):
            if k:
                t += LINES[li][2]
            st[li] = t
            t += DUR_L[li]
        e = max(b + MIN_BEATS, _even_at_or_after(T_arr, t + HOLD + EXTRA_HOLD.get(si, 0.0)))
        bounds.append((b, e))
        b = e
    return bounds, st


for K_INS in range(0, 400, 4):
    SEQ, VT, INS = _grid(K_INS)
    res = _schedule(VT)
    if res is not None and res[0][-1][1] <= len(VT) - 1:
        BOUNDS_ABS, STARTS_ABS = res
        break
LAST = len(VT) - 1
BOUNDS_ABS[-1] = (BOUNDS_ABS[-1][0], LAST)                  # 末屏延到原曲最后一击

# 把引擎的拍点表换成延长后的（只影响本进程）
VBEATS = [dict(ORIG_BEATS[o], t=float(t)) for o, t in zip(SEQ, VT)]
core.BEATS = VBEATS
core._BEAT_T = VT
core.N_BEATS = len(VBEATS)
core.LAST_BAR = (core.N_BEATS - 1) // 4
core.MUSIC_END = VBEATS[core.LAST_BAR * 4]["t"] + 0.3
core.END = core.MUSIC_END + 2.9

B0 = BOUNDS_ABS[0][0]
S = core.bt(B0) - 0.15
BOUNDS = BOUNDS_ABS
STARTS = [t - S for t in STARTS_ABS]
_last_voice = STARTS[-1] + DUR_L[-1]
END_LOCAL = min(core.END - S - 0.05, max(core.bt(LAST) - S + 1.2, _last_voice + 2.0))
SEAMS = []                                                   # 接缝：(成片本地秒, 说明)


def music_track():
    """延长后的配乐：原曲（含最后一击后的混响尾音）按虚拟拍点拼接，接缝做 40ms 等功率交叉淡化。"""
    sr = audio.SR
    src = core_music_orig()
    L = ORIG_T[LOOP_B] - ORIG_T[LOOP_A]
    segs = [(0.0, 0.0, ORIG_T[LOOP_B])]
    out_t = ORIG_T[LOOP_B]
    for r in range(K_INS // LOOP_N):
        segs.append((out_t, ORIG_T[LOOP_A], L))
        out_t += L
    rem = K_INS % LOOP_N
    if rem:
        ln = ORIG_T[LOOP_A + rem] - ORIG_T[LOOP_A]
        segs.append((out_t, ORIG_T[LOOP_A], ln))
        out_t += ln
    segs.append((out_t, ORIG_T[LOOP_B], len(src) / sr - ORIG_T[LOOP_B]))
    n = int(round((out_t + len(src) / sr - ORIG_T[LOOP_B]) * sr))
    out = np.zeros((n, 2))
    for o, s_, ln in segs:
        i0, j0, m = int(round(o * sr)), int(round(s_ * sr)), int(round(ln * sr))
        m = min(m, len(src) - j0, n - i0)
        out[i0: i0 + m] = src[j0: j0 + m]
    h = int(XFADE * sr / 2)
    SEAMS.clear()
    for (o1, s1_, l1), (o2, s2_, _) in zip(segs, segs[1:]):
        j = int(round(o2 * sr))
        pe = int(round((s1_ + l1) * sr))
        ns = int(round(s2_ * sr))
        w = np.linspace(0, 1, 2 * h)[:, None]
        a = src[pe - h: pe + h]
        bb = src[ns - h: ns + h]
        if len(a) == 2 * h and len(bb) == 2 * h:
            out[j - h: j + h] = a * np.cos(w * np.pi / 2) + bb * np.sin(w * np.pi / 2)
        SEAMS.append((o2 - S, f"原曲 {s1_ + l1:.2f}s → {s2_:.2f}s"))
    return out


_MUSIC_ORIG = None


def core_music_orig():
    """原版 core.music_track()（用原始拍点表算尾音），只算一次。"""
    global _MUSIC_ORIG
    if _MUSIC_ORIG is None:
        saved = core.BEATS, core._BEAT_T, core.N_BEATS, core.LAST_BAR, core.MUSIC_END, core.END
        core.BEATS, core._BEAT_T, core.N_BEATS = ORIG_BEATS, ORIG_T, len(ORIG_BEATS)
        core.LAST_BAR = (core.N_BEATS - 1) // 4
        core.MUSIC_END = ORIG_BEATS[core.LAST_BAR * 4]["t"] + 0.3
        core.END = core.MUSIC_END + 2.9
        try:
            _MUSIC_ORIG = core.music_track()
        finally:
            core.BEATS, core._BEAT_T, core.N_BEATS, core.LAST_BAR, core.MUSIC_END, core.END = saved
    return _MUSIC_ORIG


def wt(li, ci=0, frac=0.0):
    ts = CLAUSE_T[li]
    a = ts[ci]
    z = ts[ci + 1] if ci + 1 < len(ts) else DUR_L[li]
    return STARTS[li] + a + (z - a) * frac


def kb(j, t_local, lo=0, strong=False):
    """本屏内离本地时间 t_local 最近的整数拍（不早于 lo；strong=True 时只取小节第一拍）。"""
    b0, b1 = BOUNDS[j]
    T = S + t_local
    cands = [i for i in range(max(lo, 0), b1 - b0) if not strong or core.BEATS[b0 + i]["bar_pos"] == 0]
    return min(cands, key=lambda i: abs(core.BEATS[b0 + i]["t"] - T))


# ---------------------------------------------------------------- 白板布局（取景按 872×900 的竖屏舞台框住每屏内容）

b = Board(size=(4800, 10600))
VI = (3300, 760, 0.7)
VA = (1125, 810, 0.67)
VB = (1112, 1790, 0.63)
VB2 = (1292, 1800, 0.52)
VQ = (3300, 1900, 0.8)
VC = (1200, 3290, 0.53)
VD = (870, 4280, 0.84)
VS1, VS2, VS3, VS4 = (1150, 4930, 0.72), (2250, 5190, 0.72), (3350, 5450, 0.72), (3790, 5640, 0.6)
VF1, VF2, VF3 = (1035, 6575, 0.71), (1078, 7590, 0.61), (1100, 8600, 0.76)
VH = (3300, 3300, 0.72)
VG = (1150, 9785, 0.88)

LC, LR = (1350, 820), 230
WK = (1530, 2150, 0.9)
LD = (1850, 2150, 1.0)
CORD_X, RAIL_Y, HANDLE_Y = 1610, 1470, 1840
LAMP = (1000, 1565, 50)
BELT = (470, 1380, 2000)
ZONE = (620, 1045)
CAR_X = [650, 900, 1150]
TIMER = (700, 1745, 46)


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


# ---------------------------------------------------------------- 角色

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


def draw_li(c, x, y, s, mood="flat", back=False, squash=1.0, bag=False, alpha=1.0):
    """打工人小李：头发 + 领带；back=True 时背过身（看不到脸）；squash<1 被压扁。"""
    c.save()
    c.translate(x, y)
    c.scale(1.0, squash)
    c.translate(-x, -y)
    path = stick(x, y, s, "down", tie=not back, hair=True)
    if bag:
        path = join(path, rect(x + 50 * s, y - 200 * s, 60 * s, 90 * s, 10 * s))
    c.drawPath(path, wb.marker(BLACK, 10, alpha))
    if back:
        hy = y - 290 * s
        c.drawPath(P((x - 40 * s, hy - 10 * s), (x - 20 * s, hy + 30 * s), (x + 20 * s, hy + 30 * s), (x + 40 * s, hy - 10 * s)),
                   wb.marker(BLACK, 7, alpha))
    else:
        c.drawPath(face(x, y, s, mood), wb.marker(BLACK, 7, alpha))
    c.restore()


# ---------------------------------------------------------------- 片头：丰田模式四个大字

INTRO_CH = "丰田模式"
INTRO_X = [2880, 3160, 3440, 3720]
INTRO_Y = 690


def intro_char(ch, x, j, k):
    """片头大字：落下（比砸字柔和：1.5 倍缩到 1，小回弹），落定后整体轻微呼吸。"""
    def fn(c, kk, T):
        dt = T - tb(j, k)
        if dt < 0:
            return None
        sc = lerp(1.5, 1.0, ease_out(clamp01(dt / 0.14))) if dt < 0.14 else \
            1.0 + 0.04 * math.exp(-(dt - 0.14) * 7) * math.sin((dt - 0.14) * 22)
        sc *= 1 + 0.012 * math.sin((T - tb(j, 4)) * 2.6) if T > tb(j, 4) else 1
        with K.at(c, x, INTRO_Y, 0, sc):
            K.text(c, ch, 0, 0, 250, "hand", RED, clamp01(dt / 0.08))
        return None
    return fn

# ---------------------------------------------------------------- 第 1 屏：返工圈

SPIN0 = None


def loop_fn(c, k, T):
    t0, t1 = tb(1, 2), tb(1, 2.9)
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


# ---------------------------------------------------------------- 第 2–4 屏：流水线

def t_drop():
    return core.BEATS[DROP]["t"]


T_IN = T_STOP = T_RED = T_FIXED = T_SHAKE = None


def car_path(x, y, s=1.0) -> skia.Path:
    return join(P((x - 85 * s, y - 20 * s), (x - 85 * s, y - 55 * s), (x - 45 * s, y - 60 * s), (x - 25 * s, y - 95 * s),
                  (x + 35 * s, y - 95 * s), (x + 55 * s, y - 60 * s), (x + 85 * s, y - 52 * s), (x + 85 * s, y - 20 * s),
                  close=True),
                circle(x - 48 * s, y - 16 * s, 17 * s), circle(x + 48 * s, y - 16 * s, 17 * s))


def car_offset(T):
    ts = T_STOP()
    if T < ts:
        return -330.0 / (ts - T_IN()) * (ts - T)
    dt = T - ts
    return 16 * math.exp(-dt * 7) * math.sin(dt * 22)


def cars_fn(c, k, T):
    t_mark = tb(2, 7)
    a = ease_out(clamp01((T - T_IN()) / 0.3))
    x0, x1, y = BELT
    off = car_offset(T)
    dt = T - T_STOP()
    tilt = -4 * math.exp(-dt * 7) * math.sin(dt * 22) if dt >= 0 else 0.0
    fixed = T >= T_FIXED()
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y - 300, x1 + 120, y + 40))
    for i, xs in enumerate(CAR_X):
        with K.at(c, xs + off, y - 25, tilt):
            pth = car_path(0, 0)
            if i == 1 and T >= t_mark:
                m = ease_out(clamp01((T - t_mark) / 0.2))
                col = GREEN if fixed else RED
                c.drawPath(pth, K.paint(col, 0.2 * m))
                c.drawPath(pth, wb.marker(col, 12, m))
            c.drawPath(pth, wb.marker(BLACK, 8, a))
    c.restore()
    if dt >= 0:
        h = 170 * ease_out(clamp01(dt / 0.12))
        c.drawLine(ZONE[1] + 100, y + 30, ZONE[1] + 100, y + 30 - h, wb.marker(RED, 16))
    if fixed:                                        # 修好：车上方一个大绿勾
        sc = pop_scale(T - T_FIXED())
        with K.at(c, CAR_X[1] + 40 + off, y - 255, 0, sc):
            c.drawPath(check(0, 0, 55), wb.marker(GREEN, 16))
    return None


def pull_dy(T):
    return 60 * ease_in_out(clamp01((T - (t_drop() - 0.12)) / 0.12))


def worker_hands(T):
    x, y, s = WK
    hy = y - 290 * s
    lh_rest = (x - 70 * s, hy + 170 * s)
    rh_rest = (x + 70 * s, hy + 170 * s)
    car_mid = (CAR_X[1] + car_offset(T), BELT[2] - 80)
    t_pt, t_reach = tb(2, 7), tb(2, 9)
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
    t0 = tb(2, 5)
    p = clamp01((T - t0) / (tb(2, 5.8) - t0))
    c.save()
    tip = _reveal(c, x, y - 380 * s, 400 * s, p)
    lh, rh = worker_hands(T)
    dt = T - t_drop()
    shake = 6 * math.sin(dt * 40) * math.exp(-dt * 8) if dt > 0 else 0.0
    draw_worker(c, x, y, s, lh, rh, shake)
    c.restore()
    sc = pop_scale(T - tb(2, 6))
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


LAMP_PULSE = []


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
LEAD_K = 2


def leader_fn(c, k, T):
    x, y, s = LD
    bp = beat_pos(T) - (BOUNDS[3][0] + LEAD_K)
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
    if T_SHAKE is not None and T_SHAKE() <= T < T_SHAKE() + 0.8:
        dt = T - T_SHAKE()
        hd = 14 * math.sin(dt * 2 * math.pi * 3.2) * (1 - clamp01(dt / 0.8))
    draw_leader(c, xx, y, s, phase % 1.0, run, hd)
    if run > 0.05:
        for i in range(3):
            yy = y - 230 + i * 50
            c.drawLine(xx + 85, yy, xx + 85 + 55 * run - i * 12, yy, wb.marker(BLACK, 7, 0.7 * run))
    for i in range(3):
        dt = T - tb(3, LEAD_K + i)
        if 0 <= dt < 0.3:
            K.ripple(c, LEAD_STEPS[i], y + 4, dt, "#8A8F99", 60, 5, 0.6, 0.3)
    return None


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
    """工位计时圈：车进工位开始走，走满（车到工位尽头）那一刻停线；“修不完”那一拍起变红。"""
    def fn(c, kk, T):
        t0 = tb(j, k)
        if T < t0:
            return None
        x, y, r = TIMER
        a = pop_scale(T - t0)
        f = clamp01((T - t0) / max(0.1, T_STOP() - t0))
        col = RED if T >= T_RED() else YELLOW
        with K.at(c, x, y, 0, a * (1 + 0.15 * math.exp(-(T - T_RED()) * 8) if T >= T_RED() else a)):
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


# ---------------------------------------------------------------- 第 6–7 屏：四个工位

ST_X = [600, 1000, 1400, 1800]
ST_Y = 3300
PARTS = [BLUE, GREEN, ORANGE]
FLOW = {}


def flow_car_fn(c, k, T):
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
        if T >= ts:
            dt = T - ts
            ang = (-2.3, -1.57, -0.8)[i]
            bx += math.cos(ang) * 230 * ease_out(clamp01(dt / 0.5))
            by += math.sin(ang) * 230 * ease_out(clamp01(dt / 0.5))
            sc *= 1 - clamp01((dt - 0.5) / 0.4)
            if sc <= 0:
                continue
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


# ---------------------------------------------------------------- 图标

def lamp_icon(x, y, r=40) -> skia.Path:
    parts = [circle(x, y, r)]
    for i in range(6):
        a = -math.pi / 2 + (i - 2.5) * 0.45
        parts.append(P((x + math.cos(a) * (r + 12), y + math.sin(a) * (r + 12)),
                       (x + math.cos(a) * (r + 36), y + math.sin(a) * (r + 36))))
    return join(*parts)


def source_icon(x, y) -> skia.Path:
    drop = skia.Path()
    drop.moveTo(x + 40, y + 10)
    drop.quadTo(x + 70, y + 60, x + 40, y + 70)
    drop.quadTo(x + 10, y + 60, x + 40, y + 10)
    return join(P((x - 60, y - 40), (x + 50, y - 40), (x + 50, y - 10)), rect(x - 10, y - 60, 40, 30, 6), drop)


def pause_icon(x, y) -> skia.Path:
    return join(circle(x, y, 55), rect(x - 18, y, 16, 56, 4), rect(x + 18, y, 16, 56, 4))


def coins(x, y) -> skia.Path:
    parts = []
    for i in range(4):
        e = skia.Path()
        e.addOval(skia.Rect.MakeXYWH(x - 80, y - i * 34 - 22, 160, 44))
        parts.append(e)
    return join(*parts)


def tooth(x, y, s=1.0) -> skia.Path:
    p = skia.Path()
    p.moveTo(x - 55 * s, y - 40 * s)
    p.cubicTo(x - 70 * s, y - 95 * s, x - 15 * s, y - 95 * s, x, y - 70 * s)
    p.cubicTo(x + 15 * s, y - 95 * s, x + 70 * s, y - 95 * s, x + 55 * s, y - 40 * s)
    p.cubicTo(x + 50 * s, y + 10 * s, x + 40 * s, y + 70 * s, x + 25 * s, y + 70 * s)
    p.cubicTo(x + 10 * s, y + 70 * s, x + 10 * s, y + 20 * s, x, y + 20 * s)
    p.cubicTo(x - 10 * s, y + 20 * s, x - 10 * s, y + 70 * s, x - 25 * s, y + 70 * s)
    p.cubicTo(x - 40 * s, y + 70 * s, x - 50 * s, y + 10 * s, x - 55 * s, y - 40 * s)
    return p


def sheet_icon(x, y) -> skia.Path:
    parts = [rect(x, y, 170, 130, 8)]
    for i in range(1, 3):
        parts.append(P((x - 85, y - 65 + i * 43), (x + 85, y - 65 + i * 43)))
    parts.append(P((x - 28, y - 65), (x - 28, y + 65)))
    return join(*parts)


# ---------------------------------------------------------------- 第 10–13 屏：雪球（一条宽的单向斜坡，三站各一屏）

SL0, SL1 = (450, 4980), (4300, 5910)
ST_SNOW = [1150, 2250, 3350]
END_X = 3880
LI = (4180, 5895, 0.8)            # 小李站在坡底右侧
SNOW = {}                          # 分镜里填：keys = [(时刻函数, 坡上横坐标, 半径)], patches, li, turn, hit


def slope_y(x):
    return SL0[1] + (x - SL0[0]) * (SL1[1] - SL0[1]) / (SL1[0] - SL0[0])


def slope_path() -> skia.Path:
    parts = [P(SL0, SL1)]
    for x in range(SL0[0] + 60, SL1[0], 120):                 # 坡下的短斜线（地面）
        parts.append(P((x, slope_y(x) + 8), (x - 40, slope_y(x - 40) + 48)))
    return join(*parts)


def ball_state(T):
    keys = [(f(), x, r) for f, x, r in SNOW["keys"]]
    if T < keys[0][0]:
        return None
    i = max(n for n, k_ in enumerate(keys) if k_[0] <= T)
    t, x, r = keys[i]
    if i + 1 < len(keys) and keys[i + 1][1] != x and T >= keys[i + 1][0] - 0.6:
        t2, x2, _ = keys[i + 1]
        x = lerp(x, x2, ease_in_out(clamp01((T - (t2 - 0.6)) / 0.6)))
    r0 = keys[i - 1][2] if i else 0.0
    rr = lerp(r0, r, pop_scale(T - t, 0.3))
    return x, slope_y(x) - rr, rr, x / max(rr, 1)


def ball_fn(c, k, T):
    st = ball_state(T)
    if st is None:
        return None
    x, y, r, roll = st
    hit = SNOW["hit"]()
    if T >= hit - 0.3:                          # 最后一扑：从坡底扑到小李身上
        f = ease_in_out(clamp01((T - (hit - 0.3)) / 0.3))
        x = lerp(x, LI[0] - 60, f)
        y = lerp(y, LI[1] - r * 0.95, f)
    c.drawCircle(x, y, r, K.paint("#E8E9EE"))
    with K.at(c, x, y, math.degrees(roll)):
        for i in range(3):
            c.drawArc(skia.Rect.MakeXYWH(-r * (0.8 - i * 0.2), -r * (0.8 - i * 0.2), r * (1.6 - i * 0.4), r * (1.6 - i * 0.4)),
                      30 + i * 70, 120, False, wb.marker("#9AA0AC", 5))
    c.drawCircle(x, y, r, wb.marker(BLACK, 9))
    patches = [(f_(), ang) for f_, ang in SNOW["patches"]]
    for tp, ang in patches:
        if T >= tp:
            sc = pop_scale(T - tp)
            with K.at(c, x + math.cos(ang) * r * 0.62, y + math.sin(ang) * r * 0.62, math.degrees(ang) + 20, sc):
                pw, ph = max(46.0, r * 0.62), max(30.0, r * 0.36)
                c.drawRoundRect(skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), 6, 6, K.paint("#F4D9A8"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), 6, 6, wb.marker(ORANGE, 5))
    K.text(c, "问题", x, y, max(56.0, r * 0.5), "hand", RED)       # 字画在补丁上面，不被遮住
    return None


def li_fn(c, k, T):
    x, y, s = LI
    t_in = SNOW["li"]()
    if T < t_in:
        return None
    sc = pop_scale(T - t_in)
    back = T >= SNOW["turn"]()
    hit = SNOW["hit"]()
    squash = 1.0
    if T >= hit:
        dt = T - hit
        squash = 0.55 + 0.08 * math.exp(-dt * 6) * math.sin(dt * 25)
    with K.at(c, x, y, 0, sc):
        c.translate(-x, -y)
        draw_li(c, x, y, s, "sad", back=back, squash=squash)
    if back and T < hit:
        bs = pop_scale(T - SNOW["turn"]())
        with K.at(c, x + 20, y - 420, 0, bs):
            c.drawRoundRect(skia.Rect.MakeXYWH(-130, -60, 260, 120), 40, 40, K.paint("#FFFFFF"))
            c.drawPath(bubble(0, 0, 260, 120, -1), wb.marker(BLACK, 7))
            K.text(c, "算了…", 0, 0, 76, "hand", BLACK)
    if T >= hit:
        dt = T - hit
        for i in range(4):
            a = i / 4 * 2 * math.pi + dt * 4
            K.star(c, x + math.cos(a) * 100, y - 150 + math.sin(a) * 34, 22, YELLOW, clamp01(1.5 - dt))
    return None


# ---------------------------------------------------------------- 第 17 屏：准点下班

def home_li_fn(j, k):
    def fn(c, kk, T):
        t0 = tb(j, k)
        if T < t0:
            return None
        f = ease_in_out(clamp01((T - t0) / 1.2))
        x = lerp(3080, 3330, f)
        bob = -abs(math.sin((T - t0) * 6)) * 12 * (1 - f)
        with K.at(c, x, 3620 + bob, 0, pop_scale(T - t0)):
            c.translate(-x, -3620)
            draw_li(c, x, 3620, 0.85, "smile", bag=True)
        return None
    return fn


# ---------------------------------------------------------------- 相机：切屏移动 1.3 秒缓入缓出（只影响本进程）

MOVE_S = 1.3


def camera(board, T):
    ep_ = board.ep
    j_ = ep_.shot_at(T)
    s_ = ep_.shots[j_]
    t_ = T - s_.t0
    cur = board.views[j_]
    prev = board.end_view(j_ - 1) if j_ > 0 else cur

    def mix(a, z, k):
        return lerp(a[0], z[0], k), lerp(a[1], z[1], k), math.exp(lerp(math.log(a[2]), math.log(z[2]), k))

    k = ease_in_out(clamp01(t_ / MOVE_S)) if prev != cur else 1.0
    view = mix(prev, cur, k)
    for kb_, target, dur in board.moves.get(j_, []):
        t0_ = board.t_of(j_, kb_)
        if T < t0_:
            break
        view = mix(view, target, ease_in_out(clamp01((T - t0_) / dur)))
    cx, cy, z = view
    z *= 1 + 0.012 * clamp01(t_ / max(0.1, s_.t1 - s_.t0))
    sx = sy = 0.0
    for it in s_.shake:
        kb_, amp = it if isinstance(it, tuple) else (it, 14.0)
        dt = T - core.bt(s_.b0 + kb_)
        if 0 <= dt < 0.3:
            a = amp * math.exp(-dt * 14)
            sx += a * math.sin(dt * 90)
            sy += a * math.cos(dt * 77)
    return cx, cy, z, sx, sy


wb.camera = camera

# ---------------------------------------------------------------- 分镜

def scene(j, view):
    jj = b.shot("", SCREENS[j][1], view=view, bars=4)
    assert jj == j
    return j


# 屏 0：黄金 3 秒——“丰田模式”四个大字逐拍砸下
j = scene(0, VI)
for i, (ch, x, sfx) in enumerate(zip(INTRO_CH, INTRO_X, ("rim", "clap", "tom", "kick"))):
    b.custom(j, i, i + 0.3, intro_char(ch, x, j, i), sfx=sfx, gain=(0.8, 0.8, 0.8, 0.7)[i])
b.shots[j].shake = [(3, 7.0)]                    # 第四字落定：轻震，不闪白
b.path(j, 3.4, 4.6, wb.underline(2780, 3820, 860, 16, 50), RED, 12)
b.custom(j, 4, 4.3, pop_text("精益制造的14项原则", 3300, 970, 66, BLACK, j, 4, "sans_medium"), sfx="pop", gain=0.6)

# 屏 1：小李返工第 3 遍
j = scene(1, VA)
SPIN0 = BOUNDS[1][0] + 4
b.path(j, 0, 0.8, join(desk(780, 990, 380), stick(600, 1140, 0.85, "hold", tie=True, hair=True)), sfx="wood_high")
b.path(j, 0.8, 0.95, face(600, 1140, 0.85, "sad"))
b.custom(j, 1, 1.3, pop_text("小李 · 打工人", 760, 775, 66, BLACK, j, 1, "sans_medium"), sfx="pop")
b.path(j, 1.3, 1.9, doc(*LC, 150, 190), BLACK, 9)
b.custom(j, 2, 2.9, loop_fn, sfx="wood_high")
b.custom(j, 3, 3.3, slam_text("第3遍", LC[0], 520, 96, RED, j, 3), sfx="rim")
b.hit(j, 4, "shaker", 0.6, "返工圈开始按拍转")
k_bu = kb(j, wt(1, 1, 0.1), lo=5)
b.custom(j, k_bu, k_bu + 0.3, pop_text("补", 1030, 700, 80, GREEN, j, k_bu), sfx="pop")
b.path(j, k_bu + 0.3, k_bu + 0.8, check(1030, 830, 42), GREEN, 11)
b.custom(j, k_bu + 1, k_bu + 1.3, pop_text("坏", 1680, 700, 80, RED, j, k_bu + 1), sfx="rim", gain=0.7)
b.path(j, k_bu + 1.3, k_bu + 1.8, cross(1680, 830, 38), RED, 11)
k_ma = kb(j, wt(1, 2, 0.6), lo=k_bu + 2)
b.custom(j, k_ma, k_ma + 0.3, pop_text("麻了", 590, 620, 76, BLUE, j, k_ma), sfx="pop", gain=0.6)

# 屏 2：小王看到毛病，拉绳（drop）
j = scene(2, VB)
KD = DROP - BOUNDS[2][0]
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
x0, x1, by = BELT
b.path(j, 0, 0.7, book(540, 1310, 150, 100), GREEN, 7, sfx="wood_low")
b.text(j, 1, 1.8, "丰田模式", 790, 1310, 76, GREEN, sfx="pop")
b.path(j, 2, 2.8, join(rect((x0 + x1) / 2, by + 12, x1 - x0 + 40, 46, 20),
                       *[circle(xx, by + 12, 13) for xx in range(x0 + 40, x1, 110)]), sfx="wood_high")
T_IN = lambda: tb(2, 3)
b.custom(j, 3, 3.3, cars_fn, sfx="pop")
b.custom(j, 5, 5.8, worker_fn, sfx="wood_high")
b.text(j, 5.8, 5.95, "员工", WK[0], 2230, 86, BLUE)
b.text(j, 5.95, 6.0, "小王", WK[0], 2325, 82, BLUE)
b.hit(j, 6, "pop", 0.9, "小王头顶冒“!”")
b.hit(j, 7, "rim", 0.8, "小王指向那辆车，车身标红")
b.path(j, 8, 8.5, join(P((x0, RAIL_Y), (1760, RAIL_Y)), P((LAMP[0], RAIL_Y), (LAMP[0], LAMP[1] - LAMP[2])),
                       circle(*LAMP)), BLACK, 9, sfx="wood_high")
b.custom(j, 8.5, 8.9, cord_fn)
b.hit(j, 9, "shaker", 0.7, "小王伸手抓住安灯绳")
b.custom(j, KD, KD + 1, lamp_fn, sfx="kick", gain=0.9)

# 屏 3：黄灯一亮，组长老张赶过来帮忙
j = scene(3, VB2)
k_lamp = kb(j, wt(4, 0, 0.5), lo=1)
LAMP_PULSE.append(lambda: tb(3, k_lamp))
b.hit(j, k_lamp, "ding", 0.8, "黄灯再闪一下")
LEAD_K = max(k_lamp + 1, 2)
b.custom(j, LEAD_K, LEAD_K + 0.1, leader_fn, sfx="bongo_low", gain=0.9)
b.hit(j, LEAD_K + 1, "bongo_low", 0.9, "老张脚步")
b.hit(j, LEAD_K + 2, "bongo_low", 0.9, "老张脚步（站定）")
b.text(j, LEAD_K + 2.4, LEAD_K + 2.75, "组长", LD[0] + 20, 2230, 86, RED)
b.text(j, LEAD_K + 2.75, LEAD_K + 3.0, "老张", LD[0] + 20, 2325, 82, RED)

# 屏 4：工位里修好线照常走；修不完就整条线停下来，先把它修好
j = scene(4, VB2)
b.path(j, 0, 0.8, zone_path(), BLUE, 7, sfx="wood_high")
b.text(j, 0.8, 1.3, "工位", (ZONE[0] + ZONE[1]) / 2, BELT[2] + 125, 86, BLUE)
k_t = kb(j, wt(5, 0, 0.5), lo=1)
b.custom(j, k_t, k_t + 0.3, timer_fn(j, k_t), sfx="pop")
k_fix = kb(j, wt(5, 0, 0.9), lo=k_t + 1)
b.custom(j, k_fix, k_fix + 0.3, bubble_fn(j, k_fix), sfx="pop")
k_go = kb(j, wt(5, 1, 0.3), lo=k_fix + 1)
b.path(j, k_go, k_go + 0.5, arrow((520, 2240), (980, 2240), 0, 34), GREEN, 9, sfx="wood_low")
k_red = kb(j, wt(6, 0, 0.3), lo=k_go + 1)
T_RED = lambda: tb(4, k_red)
b.hit(j, k_red, "rim", 0.9, "修不完：计时圈变红")
T_SHAKE = lambda: tb(4, k_red)
k_stop = kb(j, wt(6, 1, 0.75), lo=k_red + 1)
T_STOP = lambda: tb(4, k_stop)
b.hit(j, k_stop, "tom", 0.9, "整条线停下来：刹停 + 停止线 + 红灯")
b.custom(j, k_stop + 1, k_stop + 1.3, slam_text("停！", 1270, 1660, 140, RED, j, k_stop + 1), sfx="kick", gain=0.85)
b.shots[j].shake = [(k_stop, 10.0), (k_stop + 1, 18.0)]
k_ok = kb(j, wt(6, 2, 0.6), lo=k_stop + 2)
T_FIXED = lambda: tb(4, k_ok)
b.hit(j, k_ok, "ding", 0.9, "先把它修好：车变绿 + 大勾")

# 屏 5：停线多亏？为什么还要停？
j = scene(5, VQ)
b.path(j, 0, 0.8, coins(3000, 1980), YELLOW, 9, sfx="wood_high")
b.path(j, 0.8, 1.4, arrow((3150, 1800), (3150, 2050), 0, 40), RED, 10)
k_kui = kb(j, wt(7, 0, 0.7), lo=1)
b.custom(j, k_kui, k_kui + 0.3, slam_text("亏？", 3420, 1760, 150, RED, j, k_kui), sfx="rim")
k_why = kb(j, wt(7, 1, 0.5), lo=k_kui + 1)
b.custom(j, k_why, k_why + 0.3, pop_text("为什么还要停", 3300, 2200, 76, BLACK, j, k_why), sfx="pop")

# 屏 6：不停 → 带毛病的车一路往下装
j = scene(6, VC)
b.path(j, 0, 0.9, stations_path(), BLACK, 8, sfx="wood_high")
for i, x in enumerate(ST_X):
    b.text(j, 0.9 + i * 0.1, 1.0 + i * 0.1, f"工位{i + 1}", x, ST_Y + 150, 84, BLUE)
k_ns = kb(j, wt(8, 0, 0.4), lo=1)
b.custom(j, k_ns, k_ns + 0.3, pop_text("要是不停", 700, 2930, 92, RED, j, k_ns, "hand"), sfx="rim", gain=0.6)
k_in = kb(j, wt(8, 1, 0.1), lo=k_ns + 1)
FLOW["in"] = (j, k_in)
b.custom(j, k_in, k_in + 0.3, flow_car_fn, sfx="pop")
k_a = kb(j, wt(9, 1, 0.1), lo=k_in + 2)
FLOW["arrive"] = [lambda i=i: tb(6, k_a + i) for i in range(3)]
for i in range(3):
    b.hit(j, k_a + i, ("wood_high", "wood_low", "bongo_high")[i], 0.8, f"到工位{i + 2}，装上一块零件")
FLOW["scatter"] = lambda: 1e9

# 屏 7：最后才发现，拆开再装一遍 = 返工
j = scene(7, VC)
k_find = kb(j, wt(10, 0, 0.6), lo=1)
b.custom(j, k_find, k_find + 0.3, pop_text("！", ST_X[-1] + 40, 2830, 160, RED, j, k_find), sfx="rim")
k_sc = kb(j, wt(10, 2, 0.2), lo=k_find + 1)
FLOW["scatter"] = lambda: tb(7, k_sc)
b.hit(j, k_sc, "clap", 0.9, "零件拆开飞散")
b.path(j, k_sc + 1, k_sc + 1.8, arrow((ST_X[-1], ST_Y + 230), (ST_X[0], ST_Y + 230), -0.18, 50), RED, 12,
       sfx="wood_high")
k_rw = kb(j, wt(11, 0, 0.7), lo=k_sc + 2)
b.custom(j, k_rw, k_rw + 0.3, slam_text("返工", (ST_X[0] + ST_X[-1]) / 2, ST_Y + 470, 130, RED, j, k_rw), sfx="kick",
         gain=0.8)
b.shots[j].shake = [(k_rw, 14.0)]

# 屏 8：书中——宁可停一下，当场亮出来，源头修好
j = scene(8, VD)
b.path(j, 0, 0.6, book(470, 3950, 150, 100), GREEN, 7, sfx="wood_low")
b.text(j, 0.6, 1.2, "书中观点", 700, 3950, 54, GREEN)
ROWS = [(pause_icon(560, 4160), "宁可停一下", RED), (lamp_icon(560, 4380), "当场摆出来", YELLOW),
        (source_icon(560, 4600), "在源头修好", BLUE)]
lo = 1
for ci, (icon, txt, col) in enumerate(ROWS):
    k = kb(j, wt(12, ci, 0.3), lo=lo)
    b.path(j, k, k + 0.6, icon, col, 9, sfx=("rim", "ding", "wood_high")[ci])
    b.text(j, k + 0.4, k + 0.4 + 0.18 * len(txt), txt, 1130, 4170 + ci * 220, 84, BLACK)
    lo = k + 1

# 屏 9–12：雪球——报表、方案、牙疼三站各一屏，越滚越大，最后砸到小李
X1, X2, X3 = ST_SNOW
j = scene(9, VS1)
b.path(j, 0, 1.2, slope_path(), BLACK, 10, sfx="wood_high")
k_dd = kb(j, wt(13, 1, 0.5), lo=2)
b.custom(j, k_dd, k_dd + 0.3, pop_text("天天都有", X1, 4560, 100, RED, j, k_dd), sfx="pop", gain=0.7)
k_s1 = kb(j, wt(14, 0, 0.3), lo=k_dd + 1)
b.path(j, k_s1, k_s1 + 0.5, sheet_icon(X1 - 190, 4790), BLACK, 7, sfx="wood_low")
b.text(j, k_s1 + 0.5, k_s1 + 0.9, "报表", X1 + 110, 4790, 96, BLUE)
k_b1 = kb(j, wt(14, 0, 0.85), lo=k_s1 + 1)
k_p1 = kb(j, wt(14, 1, 0.5), lo=k_b1 + 1)
k_g1 = kb(j, wt(14, 2, 0.7), lo=k_p1 + 1)
b.custom(j, k_b1, k_b1 + 0.3, ball_fn, sfx="pop")
b.hit(j, k_p1, "clap", 0.6, "先混过去：贴一块补丁")
b.hit(j, k_g1, "tom", 0.7, "全乱了：球变大")

j = scene(10, VS2)
k_s2 = kb(j, wt(15, 0, 0.3), lo=3)
b.hit(j, k_s2, "bongo_low", 0.9, "雪球滚到第二站")
b.path(j, k_s2, k_s2 + 0.5, join(doc(X2 - 200, 4990, 120, 150, 3), circle(X2 - 200, 5030, 18)), BLACK, 7)
b.text(j, k_s2 + 0.5, k_s2 + 0.9, "方案", X2 + 90, 4990, 96, BLUE)
k_p2 = kb(j, wt(15, 1, 0.5), lo=k_s2 + 1)
b.hit(j, k_p2, "clap", 0.6, "先交了再说：再贴一块")
k_g2 = kb(j, wt(15, 3, 0.5), lo=k_p2 + 1)
b.custom(j, k_g2, k_g2 + 0.3, pop_text("漏洞", X2 + 90, 5110, 80, RED, j, k_g2), sfx="tom", gain=0.8)

j = scene(11, VS3)
k_s3 = kb(j, wt(16, 0, 0.3), lo=3)
b.hit(j, k_s3, "bongo_low", 0.9, "雪球滚到第三站")
b.path(j, k_s3, k_s3 + 0.6, tooth(X3 - 370, 5230, 1.0), BLACK, 8)
b.text(j, k_s3 + 0.6, k_s3 + 1.0, "牙疼", X3 - 30, 5230, 96, BLUE)
k_p3 = kb(j, wt(16, 0, 0.8), lo=k_s3 + 1)
b.hit(j, k_p3, "clap", 0.6, "先忍一忍：再贴一块")
k_g3 = kb(j, wt(16, 1, 0.6), lo=k_p3 + 1)
b.hit(j, k_g3, "tom", 0.85, "拖到要做根管：球变大")

j = scene(12, VS4)
b.custom(j, 2, 2.3, li_fn, sfx="wood_high")
b.text(j, 2.3, 2.6, "小李", LI[0], LI[1] + 85, 84, BLACK)
k_p4 = kb(j, wt(17, 0, 0.7), lo=3)
b.hit(j, k_p4, "clap", 0.7, "先应付、先遮住：再贴一块")
k_roll = kb(j, wt(17, 1, 0.4), lo=k_p4 + 1)
k_big = kb(j, wt(17, 2, 0.5), lo=k_roll + 1)
b.hit(j, k_roll, "bongo_low", 0.9, "一路往下走")
b.hit(j, k_big, "tom", 0.9, "越滚越大")
k_turn = kb(j, wt(18, 0, 0.5), lo=k_big + 1)
b.hit(j, k_turn, "rim", 0.7, "小李背过身：算了…")
k_hit = kb(j, wt(18, 1, 0.85), lo=k_turn + 1, strong=True)
b.hit(j, k_hit, "kick", 1.0, "麻烦找上门：大球咚地砸到小李（强拍）")
b.shots[j].shake = [(k_hit, 22.0)]
b.shots[j].flashes = [(k_hit, 0.35)]
SNOW["li"] = lambda: tb(12, 2)
SNOW["turn"] = lambda: tb(12, k_turn)
SNOW["hit"] = lambda: tb(12, k_hit)
SNOW["keys"] = [(lambda: tb(9, k_b1), X1, 42), (lambda: tb(9, k_g1), X1, 66),
                (lambda: tb(10, k_s2), X2, 82), (lambda: tb(10, k_g2), X2, 108),
                (lambda: tb(11, k_s3), X3, 124), (lambda: tb(11, k_g3), X3, 150),
                (lambda: tb(12, k_roll), 3620, 170), (lambda: tb(12, k_big), END_X, 205),
                (lambda: tb(12, k_hit), END_X, 225)]
SNOW["patches"] = [(lambda: tb(9, k_p1), -0.5), (lambda: tb(10, k_p2), 2.4), (lambda: tb(11, k_p3), 0.8),
                   (lambda: tb(12, k_p4), -2.5)]

# 屏 13：所以下次发现问题，先停一停。第一，当场说出来，拉上同事看五分钟
j = scene(13, VF1)
k_tt = kb(j, wt(19, 2, 0.3), lo=1)
b.custom(j, k_tt, k_tt + 0.3, pop_path(pause_icon(1440, 6235), 1440, 6235, RED, 10, j, k_tt, fill="#FFFFFF"), sfx="rim")
b.custom(j, k_tt, k_tt + 0.3, pop_text("先停一停", 1030, 6250, 84, RED, j, k_tt))
k_one = kb(j, wt(20, 1, 0.1), lo=k_tt + 1)
b.custom(j, k_one, k_one + 0.3, pop_text("① 当场说出来", 1000, 6420, 80, BLUE, j, k_one), sfx="pop")
b.path(j, k_one + 0.3, k_one + 0.9, join(desk(1020, 6720, 340), doc(1060, 6640, 110, 140, 3)))
b.path(j, k_one + 0.9, k_one + 1.5, stick(760, 6900, 0.85, "up", tie=True, hair=True), BLACK, 10)
k_mates = kb(j, wt(20, 2, 0.3), lo=k_one + 2)
b.path(j, k_mates, k_mates + 0.7, join(stick(1330, 6900, 0.8, "point"), stick(1530, 6900, 0.8, "down")), BLUE, 9,
       sfx="wood_high")
k_clock = kb(j, wt(20, 2, 0.85), lo=k_mates + 1)
b.path(j, k_clock, k_clock + 0.6, join(wb.clock(1450, 6400, 60), wb.hands_at(1450, 6400, 60, 12, 5)), BLACK, 8,
       sfx="ding")
b.text(j, k_clock + 0.6, k_clock + 1.0, "5分钟", 1450, 6530, 64, RED)

# 屏 14：第二，在源头修
j = scene(14, VF2)
b.custom(j, 0, 0.3, pop_text("② 在源头修", 1100, 7280, 90, BLUE, j, 0), sfx="pop")
BOX = [(600, "方案"), (1100, "主管"), (1600, "客户")]
b.path(j, 1, 1.8, join(*[rect(x, 7650, 280, 180, 20) for x, _ in BOX], arrow((750, 7650), (950, 7650), 0, 36),
                       arrow((1250, 7650), (1450, 7650), 0, 36)), BLACK, 9, sfx="wood_high")
for x, name in BOX:
    b.text(j, 1.8, 2.0, name, x, 7650, 74, BLACK)
k_src = kb(j, wt(21, 1, 0.4), lo=2)
b.path(j, k_src, k_src + 0.6, circle(600, 7650, 190), RED, 11, sfx="rim")
b.text(j, k_src + 0.6, k_src + 1.0, "这里修", 600, 7905, 80, RED)
k_patch = kb(j, wt(21, 2, 0.5), lo=k_src + 1)
for i, x in enumerate((1100, 1600)):
    b.custom(j, k_patch, k_patch + 0.3, pop_path(join(rect(x + 90, 7580, 80, 60, 8), P((x + 60, 7580), (x + 120, 7580))),
                                                  x + 90, 7580, ORANGE, 6, j, k_patch, fill="#FBE3C8"),
             sfx="pop" if i == 0 else None)
b.path(j, k_patch + 1, k_patch + 1.4, join(cross(1190, 7580, 50), cross(1690, 7580, 50)), RED, 11, sfx="rim")

# 屏 15：第三，喊停的人不挨骂
j = scene(15, VF3)
b.custom(j, 0, 0.3, pop_text("③ 说好规矩", 1100, 8280, 90, BLUE, j, 0), sfx="pop")
b.path(j, 1, 1.7, rect(1100, 8640, 760, 420, 30), BLACK, 9, sfx="wood_high")
b.text(j, 1.7, 2.3, "团队约定", 1100, 8510, 70, BLACK)
k_rule = kb(j, wt(22, 1, 0.6), lo=3)
b.text(j, k_rule, k_rule + 1.0, "喊停的人", 1100, 8640, 80, BLACK, sfx="pop")
k_nb = kb(j, wt(22, 2, 0.4), lo=k_rule + 1)
b.custom(j, k_nb, k_nb + 0.3, slam_text("不挨骂", 1060, 8760, 92, RED, j, k_nb), sfx="ding")
b.path(j, k_nb + 0.4, k_nb + 0.9, check(1330, 8760, 46), GREEN, 13)
b.path(j, 2.3, 2.9, join(stick(640, 8960, 0.6, "point"), stick(1560, 8960, 0.6, "point")), BLACK, 8)

# 屏 16：早一点停下来，少一点返工，早点下班
j = scene(16, VH)
k_c = kb(j, wt(23, 0, 0.5), lo=1)
b.path(j, k_c, k_c + 0.6, join(wb.clock(2950, 3080, 95), wb.hands_at(2950, 3080, 95, 6, 0)), BLACK, 9, sfx="ding")
b.text(j, k_c + 0.6, k_c + 1.1, "18:00", 2950, 3230, 64, RED)
k_rw2 = kb(j, wt(23, 1, 0.5), lo=k_c + 1)
b.custom(j, k_rw2, k_rw2 + 0.3, pop_text("返工 ↓", 3480, 3060, 76, GREEN, j, k_rw2), sfx="pop")
k_home = kb(j, wt(23, 2, 0.4), lo=k_rw2 + 1)
b.path(j, k_home - 0.8, k_home - 0.1, join(rect(3620, 3480, 200, 330, 10), circle(3680, 3480, 10)), BLACK, 8)
b.custom(j, k_home, k_home + 0.3, home_li_fn(j, k_home), sfx="wood_high")
b.custom(j, k_home + 1, k_home + 1.3, pop_text("准点下班", 3220, 3760, 70, BLUE, j, k_home + 1), sfx="ding", gain=0.7)

# 屏 17：评论区追问 + 下一讲
j = scene(17, VG)
b.path(j, 0, 0.8, bubble(1150, 9540, 960, 300, -1), BLACK, 9, sfx="wood_high")
k_q = kb(j, wt(24, 0, 0.2), lo=1)
b.text(j, k_q, k_q + 1.2, "你手上有没有一个问题", 1150, 9480, 72, RED, sfx="pop")
k_q2 = kb(j, wt(24, 1, 0.1), lo=k_q + 1)
b.text(j, k_q2, k_q2 + 1.0, "一直想着以后再说？", 1150, 9600, 72, RED)
k_cm = kb(j, wt(25, 0, 0.3), lo=k_q2 + 2)
b.custom(j, k_cm, k_cm + 0.3, pop_text("写在评论区，别一个人扛着", 1150, 9810, 58, BLACK, j, k_cm, "sans_medium"),
         sfx="ding")
k_n = kb(j, wt(26, 0, 0.2), lo=k_cm + 1)
b.path(j, k_n, k_n + 0.6, rect(1150, 10030, 980, 210, 24), BLUE, 8, sfx="wood_high")
b.text(j, k_n + 0.5, k_n + 0.8, "下一讲", 1150, 9965, 52, BLUE)
b.text(j, k_n + 0.8, k_n + 2.2, "活儿越做越多，为什么反而越乱？", 1150, 10065, 58, BLACK)

# ---------------------------------------------------------------- 时间轴

ep = core.Episode(NO, KEY, CONCEPT, TITLE, ACC, b.shots, refs=[], publish_title=f"Vibe知识大赏｜{TITLE}",
                  hashtags=TAGS, cover_title=COVER_TITLE, cover_sub="丰田模式 · 停线", cover_shot=COVER_SHOT,
                  notes=NOTES)
for s, (k0, k1) in zip(b.shots, BOUNDS):
    s.b0, s.t0, s.t1 = k0, core.bt(k0), core.bt(k1)
    s.bars = (k1 - k0) // 4 + 2          # 名义小节数盖住全部实测拍（Board.t_of 超出名义长度会外推）
b.shots[0].t0 = S
b.shots[-1].t1 = S + END_LOCAL
b.attach(ep)


_PUNCT = "，。：？！、；"


def char_time(li, idx):
    """第 li 句第 idx 个字（不计标点）的本地时刻：按分句起点与分句内字数比例换算。"""
    text = LINES[li][0].rstrip(_PUNCT)
    clauses = text.split("，")
    ts = CLAUSE_T[li]
    n = 0
    for ci, cl in enumerate(clauses):
        chars = [ch for ch in cl if ch not in _PUNCT]
        if idx < n + len(chars):
            a = ts[ci]
            z = (ts[ci + 1] - COMMA) if ci + 1 < len(ts) else DUR_L[li]
            return STARTS[li] + a + (z - a) * (idx - n) / max(1, len(chars))
        n += len(chars)
    return STARTS[li] + DUR_L[li]


def captions():
    caps = []
    for li, (text, pieces, _) in enumerate(LINES):
        plain = [ch for ch in text if ch not in _PUNCT]
        idx = 0
        for cap in pieces:
            body = [ch for ch in cap if ch not in _PUNCT + "【】"]
            if plain[idx: idx + len(body)] != body:
                raise ValueError(f"字幕与旁白不一致：{text} / {cap}")
            caps.append([char_time(li, idx), None, cap.rstrip("，。；：")])
            idx += len(body)
        if idx != len(plain):
            raise ValueError(f"字幕没有覆盖整句：{text}")
    for i, cp in enumerate(caps):
        cp[1] = caps[i + 1][0] if i + 1 < len(caps) else None
    return caps


def build():
    return ep
