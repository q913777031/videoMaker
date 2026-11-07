"""丰田模式系列旁白：IndexTTS2，音色取第 01 讲旁白（cv3jian），平淡叙述语气。

用户选定（试听 4 的方案 3）：全程固定一个平静情绪向量，同一屏的几句连起来一次合成，再按句切开，
句与句之间语调连贯、不会突然拔高。各分镜模块统一调用 synthesize(LINES, LINE_MOOD, PINYIN, groups)；
groups 是每屏的句序号列表（取自 SCREENS），不给则逐句合成。LINE_MOOD 保留在文案里，不再参与合成。
"""
import hashlib
import json
import math
import os

import numpy as np

from engine import audio

VOICE = "ix2_cv3jian"
CALM = {"vector": {"calm": 0.8, "happy": 0.1}, "alpha": 0.35}
# 旧方案（逐句文字情绪，强度 0.7）的情绪表：FT_DRAFT_TTS 草稿读旧缓存时还要用
ALPHA = 0.7
EMO = {"讲": "语气温和，像跟朋友聊天一样耐心讲解", "疼": "带着体谅和关心，有点心疼对方", "问": "略带惊讶，好奇地反问",
       "醒": "认真、关切地提醒", "安": "平静、温暖，让人安心", "奇": "带点好奇，像要讲一件有意思的事",
       "定": "认真、肯定地说明", "叹": "有点无奈，轻轻叹气", "近": "亲切地拉近距离，像聊家常",
       "励": "温和、鼓励地说", "条": "清楚、耐心地一条条说明", "笑": "轻松、温暖，带点笑意"}

_NAR = None


def tts_text(t, pinyin):
    for a, b in pinyin:
        t = t.replace(a, b)
    return t


def _han(s):
    return sum(1 for ch in s if "一" <= ch <= "鿿")


def _units(t):
    """估计一句的念读长度（单位≈一个字）：汉字 1，句内逗号等停顿 1.5，冒号（“下一讲：”）停得久、前后念得慢，算 5。"""
    body = t.rstrip("。？！：；")
    return _han(body) + 1.5 * sum(body.count(p) for p in "，、；") + 5.0 * body.count("：")


def split_group(x, texts):
    """一段连读音频按句切开：在所有静音段里挑 len(texts)-1 个切点，使切点贴近按念读长度估计的句界、且静音尽量长
    （动态规划整体求最优，不会因为某个句界附近有更长的句内停顿就整体错位）。找不到足够的静音段时抛 RuntimeError。"""
    hop = int(0.01 * audio.SR)
    n = len(x) // hop
    r = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1) + 1e-12)
    r3 = np.convolve(r, np.ones(3) / 3, "same")
    quiet = r3 < r.max() * 10 ** (-35 / 20)
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if i > 0 and j < n and j - i >= 4:          # 只取中间、至少 40ms 的静音
                runs.append((i, j))
            i = j
        else:
            i += 1
    m = len(texts) - 1
    if m == 0:
        return [audio._trim(x)]
    if len(runs) < m:
        raise RuntimeError(f"静音段不够：{texts[0]}")
    gap = 2.0                                          # 句与句之间的停顿，按两个字计
    u = [_units(t) for t in texts]
    tot = sum(u) + gap * m
    exp, acc = [], 0.0
    for k in range(m):
        acc += u[k]
        exp.append((acc + gap * 0.5) / tot * n)
        acc += gap
    sig = 0.07 * n

    def score(k, ri):
        a, b = runs[ri]
        d = ((a + b) / 2 - exp[k]) / sig
        return 1.5 * math.log(b - a) - d * d

    R = len(runs)
    best = [[-1e18] * R for _ in range(m)]
    prev = [[-1] * R for _ in range(m)]
    for ri in range(R):
        best[0][ri] = score(0, ri)
    for k in range(1, m):
        top, arg = -1e18, -1
        for ri in range(R):
            if ri - 1 >= 0 and best[k - 1][ri - 1] > top:
                top, arg = best[k - 1][ri - 1], ri - 1
            if arg >= 0:
                best[k][ri] = top + score(k, ri)
                prev[k][ri] = arg
    ri = max(range(R), key=lambda q: best[m - 1][q])
    if best[m - 1][ri] < -1e17:
        raise RuntimeError(f"找不到句界：{texts[0]}")
    picks = []
    for k in range(m - 1, -1, -1):
        picks.append(ri)
        ri = prev[k][ri]
    picks.reverse()
    cuts = [(runs[q][0] + runs[q][1]) // 2 for q in picks]
    cuts = _asr_refine(x, texts, cuts, runs, r3, hop) or cuts
    cuts = [0] + cuts + [n]
    return [audio._trim(x[a * hop: b * hop]) for a, b in zip(cuts, cuts[1:])]


# ---------------------------------------------------------------- 用语音识别核对句界（有 sherpa-onnx 与模型时）

ASR_MODEL = os.environ.get("FT_ASR_MODEL", "/tmp/claude-0/-home-user-videoMaker/c54877fb-ac6a-58c6-9cd0-0962ece50b52/"
                           "scratchpad/asr_dl/sherpa-onnx-paraformer-zh-small-2024-03-09")
_REC = None


def _asr(seg):
    global _REC
    import sherpa_onnx
    from scipy import signal
    if _REC is None:
        _REC = sherpa_onnx.OfflineRecognizer.from_paraformer(paraformer=f"{ASR_MODEL}/model.int8.onnx",
                                                            tokens=f"{ASR_MODEL}/tokens.txt", num_threads=2)
    st = _REC.create_stream()
    st.accept_waveform(16000, signal.resample_poly(seg, 160, 441).astype(np.float32))
    _REC.decode_stream(st)
    return st.result.text.replace(" ", "")


def _py_dist(ref, hyp):
    """无调拼音编辑距离（同音字不算错）。"""
    from pypinyin import lazy_pinyin
    a = lazy_pinyin("".join(ch for ch in ref if "一" <= ch <= "鿿"))
    b = lazy_pinyin("".join(ch for ch in hyp if "一" <= ch <= "鿿"))
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (ca != cb))
    return dp[-1]


def _asr_refine(x, texts, cuts, runs, r3, hop):
    """静音挑出的句界交给语音识别核对：前一段念的不是这句话（模型把两句连成一口气，停顿挪到了别处）时，
    在附近的静音段和音量低谷里找识别最对得上的切点。结果按音频内容缓存到 .cache/tts/split_*.json。
    没装 sherpa-onnx 或没有模型时返回 None（沿用静音切点）。"""
    h = hashlib.sha1(x.tobytes() + "|".join(texts).encode()).hexdigest()
    cf = audio.CACHE_DIR / f"split_{h}.json"
    if cf.exists():
        return json.loads(cf.read_text())
    if not os.path.isdir(ASR_MODEL):
        return None
    try:
        import sherpa_onnx  # noqa: F401
        import pypinyin  # noqa: F401
    except ImportError:
        return None
    n = len(r3)
    mins = [f for f in range(5, n - 5) if r3[f] == r3[f - 5: f + 6].min() and not any(a <= f < b for a, b in runs)]
    out, prev = [], 0
    for k, c0 in enumerate(cuts):
        seg_err = _py_dist(texts[k], _asr(x[prev * hop: c0 * hop]))
        if seg_err:
            nxt = cuts[k + 1] if k + 1 < len(cuts) else n
            cand = [(a + b) // 2 for a, b in runs] + mins
            cand = sorted({c for c in cand if prev + 20 < c < nxt - 20 and abs(c - c0) < 0.25 * n})
            best = (seg_err, 0, c0)
            for c in cand:
                e = _py_dist(texts[k], _asr(x[prev * hop: c * hop]))
                quiet = -max((b - a for a, b in runs if a <= c < b), default=0)
                if (e, quiet, abs(c - c0)) < (best[0], best[1], abs(best[2] - c0)):
                    best = (e, quiet, c)
            c0 = best[2]
        out.append(int(c0))
        prev = c0
    cf.write_text(json.dumps(out))
    return out


def synthesize(lines, mood=None, pinyin=(), groups=None, log=None, cached_only=False):
    """合成 44.1kHz 单声道逐句音频（首尾静音已裁），返回与 lines 等长的列表。

    groups：每屏的句序号列表；同屏几句连读一次合成后按句切开，切不开时该屏退回逐句合成。
    没被 groups 覆盖的句子逐句合成。mood 不参与合成（保留参数兼容旧调用）。
    """
    global _NAR
    texts = [ln[0] if isinstance(ln, tuple) else ln for ln in lines]
    if _NAR is None:
        _NAR = audio.Narrator(VOICE)
    covered = {i for g in (groups or []) for i in g}
    plan = [list(g) for g in (groups or []) if g] + [[i] for i in range(len(texts)) if i not in covered]
    out = [None] * len(texts)
    for g in plan:
        parts = None
        if cached_only:                                # 只读缓存（草稿排版）：整屏连读没缓存就留 None，不启动 IndexTTS2
            joined = "".join(tts_text(texts[i], pinyin) for i in g)
            if not _cache_path(_NAR, joined, CALM).exists():
                continue
        if len(g) > 1:
            x = _NAR.generate("".join(tts_text(texts[i], pinyin) for i in g), 1.0, 8, emo=CALM)
            try:
                parts = split_group(x, [texts[i] for i in g])
            except RuntimeError as e:
                if log:
                    print(f"  {g} 连读切分失败，改逐句：{e}", file=log, flush=True)
        if parts is None:
            parts = [_NAR.generate(tts_text(texts[i], pinyin), 1.0, 8, emo=CALM) for i in g]
        for i, p in zip(g, parts):
            out[i] = p
            if log:
                print(f"  {i:02d} {len(p) / audio.SR:.1f}s {texts[i]}", file=log, flush=True)
    return out


# ---------------------------------------------------------------- 开场钩子句：逐字发声起点（大字逐字砸下用）

HOOK_EMO = {"vector": {"calm": 0.6, "angry": 0.12, "surprised": 0.08}, "alpha": 0.4}   # 比正文略有力，强度低
CTC_MODEL = os.environ.get("FT_CTC_MODEL", "/tmp/claude-0/-home-user-videoMaker/c54877fb-ac6a-58c6-9cd0-0962ece50b52/"
                           "scratchpad/asr_ctc/sherpa-onnx-zipformer-ctc-zh-int8-2025-07-03")
_CTC = None


def _cache_path(nar, text, emo):
    e = audio._ix2_emo(emo)
    raw = f"{nar._key}|{json.dumps(e, sort_keys=True, ensure_ascii=False)}|{1.0:.4f}|{text}"
    return audio.CACHE_DIR / f"{hashlib.sha1(raw.encode()).hexdigest()}.npy"


def _draft_hook(n, seed=0):
    """占位：每字 0.2 秒低噪声 + 0.03 秒间隙（配音没合成时排版用），返回 (音频, 每字起点)。"""
    rng = np.random.default_rng(seed)
    syl, gap = int(0.2 * audio.SR), int(0.03 * audio.SR)
    x = np.zeros(int(0.03 * audio.SR) + n * (syl + gap) + int(0.08 * audio.SR))
    ons = []
    for i in range(n):
        a = int(0.03 * audio.SR) + i * (syl + gap)
        x[a: a + syl] = 0.05 * rng.standard_normal(syl) * np.hanning(syl)
        ons.append(a / audio.SR)
    return x, ons


def hook_line(text, pinyin=(), draft=False):
    """合成开场钩子句（同一音色、HOOK_EMO），返回 (音频, 每个汉字音节的发声起点秒, 是否占位)。

    draft=True 且没有缓存时不启动 IndexTTS2，返回占位音频（起点为估算）。"""
    global _NAR
    if _NAR is None:
        _NAR = audio.Narrator(VOICE)
    t = tts_text(text, pinyin)
    n = _han(text)
    if draft and not _cache_path(_NAR, t, HOOK_EMO).exists():
        x, ons = _draft_hook(n)
        return x, ons, True
    x = _NAR.generate(t, 1.0, 8, emo=HOOK_EMO)
    return x, syllable_onsets(x, n), False


def _ctc_starts(x):
    """CTC 识别（sherpa-onnx zipformer-ctc）给出的每个字的尖峰时刻；没有模型时返回 None。"""
    global _CTC
    if not os.path.isdir(CTC_MODEL):
        return None
    try:
        import sherpa_onnx
        from scipy import signal
    except ImportError:
        return None
    if _CTC is None:
        _CTC = sherpa_onnx.OfflineRecognizer.from_zipformer_ctc(model=f"{CTC_MODEL}/model.int8.onnx",
                                                               tokens=f"{CTC_MODEL}/tokens.txt", num_threads=2)
    st = _CTC.create_stream()
    st.accept_waveform(16000, signal.resample_poly(x, 160, 441).astype(np.float32))
    _CTC.decode_stream(st)
    r = st.result
    return [float(ts) for tok, ts in zip(r.tokens, r.timestamps) if tok.startswith("▁")]


def onset_strength(x, hop_s=0.005):
    """谱通量（80–8000Hz、32 个对数频带的正向变化之和，平滑约 15ms）与帧能量（dB）。返回 (时刻, 通量 0–1, 能量 dB)。"""
    from scipy import signal
    sr = audio.SR
    hop = int(hop_s * sr)
    f, t, Z = signal.stft(x, sr, nperseg=1024, noverlap=1024 - hop, boundary=None, padded=False)
    mag = np.abs(Z)
    edges = np.geomspace(80, 8000, 33)
    bands = np.stack([mag[(f >= a) & (f < b)].sum(0) for a, b in zip(edges, edges[1:])])
    lb = np.log1p(bands / (bands.max() + 1e-12) * 1000)
    flux = np.maximum(0, np.diff(lb, axis=1, prepend=lb[:, :1])).sum(0)
    k = np.exp(-0.5 * (np.arange(-6, 7) / 2.0) ** 2)
    flux = np.convolve(flux, k / k.sum(), "same")
    flux /= flux.max() + 1e-12
    e = 20 * np.log10(np.sqrt((mag ** 2).sum(0)) + 1e-9)
    t = t - 1024 / 2 / sr + hop / sr                  # 帧中心 → 帧右缘附近（起音出现的时刻）
    return np.maximum(t, 0), flux, e - e.max()


def syllable_onsets(x, n):
    """一句短话里 n 个音节（汉字）的发声起点（秒，相对音频开头）。

    做法：谱通量的局部峰为候选，CTC 识别的逐字尖峰时刻为先验（字数对不上时改用有声段内按字均分），
    动态规划按顺序挑 n 个候选（相邻 ≥70ms），使“峰高 − 偏离先验的惩罚”最大；第 1 个字固定为首个有声帧。
    结果按音频内容缓存到 .cache/tts/onset_*.json。"""
    h = hashlib.sha1(x.tobytes() + str(n).encode()).hexdigest()
    cf = audio.CACHE_DIR / f"onset_{h}.json"
    if cf.exists():
        return json.loads(cf.read_text())
    t, flux, e = onset_strength(x)
    voiced = np.where(e > -32)[0]
    a, z = t[voiced[0]], t[voiced[-1]]
    prior = _ctc_starts(x)
    src = "ctc"
    if prior is None or len(prior) != n:
        src = "均分"
        prior = [a + (z - a) * i / n for i in range(n)]
    prior[0] = a
    pk = [i for i in range(1, len(flux) - 1) if flux[i] >= flux[i - 1] and flux[i] > flux[i + 1] and flux[i] > 0.08
          and e[i] > -40]
    cand = sorted({float(t[i]) for i in pk} | {float(a)})
    hgt = {float(t[i]): float(flux[i]) for i in pk}
    hgt[float(a)] = 1.0
    sig = 0.07 if src == "ctc" else 0.12
    C = len(cand)

    def sc(k, ci):
        d = (cand[ci] - prior[k]) / sig
        return 2.0 * hgt[cand[ci]] - 0.5 * d * d

    best = np.full((n, C), -1e18)
    prev = np.full((n, C), -1, int)
    best[0] = [sc(0, ci) if cand[ci] == a else -1e18 for ci in range(C)]
    for k in range(1, n):
        for ci in range(C):
            ok = [cj for cj in range(ci) if cand[ci] - cand[cj] >= 0.07 and best[k - 1][cj] > -1e17]
            if ok:
                cj = max(ok, key=lambda q: best[k - 1][q])
                best[k][ci] = best[k - 1][cj] + sc(k, ci)
                prev[k][ci] = cj
    ci = int(np.argmax(best[n - 1]))
    if best[n - 1][ci] < -1e17:
        out = [float(p) for p in prior]
    else:
        out = []
        for k in range(n - 1, -1, -1):
            out.append(cand[ci])
            ci = prev[k][ci]
        out.reverse()
    out = [round(float(v), 4) for v in out]
    cf.write_text(json.dumps(out))
    return out


# ---------------------------------------------------------------- 开场句一顿一顿地念：在字界切开、字间插静音

SPREAD_GAP = 0.34              # 字与字发声起点的目标间隔（秒）；字多时缩小，整句起点跨度不超过 SPREAD_SPAN
SPREAD_MIN = 0.27
SPREAD_SPAN = 1.95
SPREAD_COMMA = 0.15            # 逗号处再多停


def _env_db(x, hop=0.005, win=0.02):
    h, w = int(hop * audio.SR), int(win * audio.SR)
    n = len(x) // h
    e = np.array([np.sqrt(np.mean(x[max(0, i * h - w // 2): i * h + w // 2] ** 2) + 1e-12) for i in range(n)])
    return 20 * np.log10(e / (e.max() + 1e-12) + 1e-9)


def _char_cuts(x, han, on, asr=True):
    """每两个字之间的切点（秒）：发声起点前后 [-0.12, +0.04] 秒内的音量低谷为候选，
    用语音识别核对“切点前念的是前几个字、切点后念的是后几个字”（无调拼音编辑距离），再加低谷深度与离起点远近打分。
    结果按音频内容缓存到 .cache/tts/cuts_*.json。"""
    h = hashlib.sha1(x.tobytes() + han.encode()).hexdigest()
    cf = audio.CACHE_DIR / f"cuts_{h}.json"
    if asr and cf.exists():
        return json.loads(cf.read_text())
    hop = 0.005
    e = _env_db(x, hop)
    use_asr = asr and os.path.isdir(ASR_MODEL)
    cuts = []
    for i in range(1, len(han)):
        lo = max(int((on[i] - 0.12) / hop), int((cuts[-1] if cuts else 0.0) / hop) + 12, 1)
        hi = min(int((on[i] + 0.04) / hop), len(e) - 2)
        if hi <= lo:
            cuts.append(round(max(on[i] - 0.02, (cuts[-1] if cuts else 0) + 0.06), 4))
            continue
        cand = [k for k in range(lo, hi + 1) if e[k] <= e[k - 1] and e[k] <= e[k + 1]] or [lo + int(np.argmin(e[lo:hi + 1]))]
        best = None
        for k in cand:
            t = k * hop
            s = -0.04 * (e[k] + 60) - 8 * abs(t - (on[i] - 0.02))
            if use_asr:
                n0 = int(t * audio.SR)
                s -= 1.5 * (_py_dist(han[:i], _asr(x[:n0])) + _py_dist(han[i:], _asr(x[n0:])))
            if best is None or s > best[0]:
                best = (s, t)
        cuts.append(round(best[1], 4))
    if asr:
        cf.write_text(json.dumps(cuts))
    return cuts


def spread_line(x, text, on, asr=True):
    """开场句改成一顿一顿地念：在字界切开（短淡入淡出防爆音），字与字之间插静音，
    使相邻两字发声起点相隔约 SPREAD_GAP 秒（逗号处多 SPREAD_COMMA）。返回 (新音频, 每字发声起点)。
    切点先由 _char_cuts 选，再逐个字界在候选低谷里微调：拼好整句交给语音识别，挑念得最对的（结果缓存）。"""
    han = "".join(ch for ch in text if _han(ch))
    n = len(han)
    if n < 2:
        return x, list(on)
    commas, c = set(), 0
    for ch in text:
        if _han(ch):
            c += 1
        elif ch in "，、" and 0 < c < n:
            commas.add(c)
    gap = min(SPREAD_GAP, max(SPREAD_MIN, (SPREAD_SPAN - SPREAD_COMMA * len(commas)) / (n - 1)))
    cuts = _char_cuts(x, han, on, asr)
    if not asr:                                    # 占位音频（草稿）：不核对
        return _assemble(x, cuts, on, gap, commas)
    h = hashlib.sha1(x.tobytes() + text.encode() + json.dumps(cuts).encode() + f"{gap}".encode()).hexdigest()
    cf = audio.CACHE_DIR / f"spread_{h}.json"
    if cf.exists():
        cuts = json.loads(cf.read_text())
    elif os.path.isdir(ASR_MODEL):
        hop = 0.005
        e = _env_db(x, hop)
        best = _py_dist(han, _asr(_assemble(x, cuts, on, gap, commas)[0]))
        for i in range(len(cuts)):
            if best == 0:
                break
            lo = max(int((cuts[i - 1] if i else 0.0) / hop) + 12, int((on[i + 1] - 0.14) / hop), 1)
            hi = min(int((cuts[i + 1] if i + 1 < len(cuts) else len(x) / audio.SR) / hop) - 12,
                     int((on[i + 1] + 0.06) / hop), len(e) - 2)
            for k in range(lo, hi + 1, 2):
                if not (e[k] <= e[k - 1] + 1.5 and e[k] <= e[k + 1] + 1.5):
                    continue
                trial = cuts[:i] + [round(k * hop, 4)] + cuts[i + 1:]
                d = _py_dist(han, _asr(_assemble(x, trial, on, gap, commas)[0]))
                if d < best:
                    best, cuts = d, trial
        cf.write_text(json.dumps(cuts))
    return _assemble(x, cuts, on, gap, commas)


def _assemble(x, cuts, on, gap, commas):
    n = len(cuts) + 1
    cuts = [0.0] + list(cuts) + [len(x) / audio.SR]
    sr = audio.SR
    fi, fo = int(0.004 * sr), int(0.012 * sr)
    segs, leads = [], []
    for i in range(n):
        a, z = int(cuts[i] * sr), int(cuts[i + 1] * sr)
        s = x[a:z].copy()
        if i and len(s) > fi:
            s[:fi] *= np.linspace(0, 1, fi)
        if i < n - 1 and len(s) > fo:
            s[-fo:] *= np.linspace(1, 0, fo)
        segs.append(s)
        leads.append(min(max(0.0, on[i] - cuts[i]), len(s) / sr))
    lands, pos = [], []
    for i in range(n):
        if i == 0:
            p, L = 0.0, leads[0]
        else:
            L = lands[-1] + gap + (SPREAD_COMMA if i in commas else 0.0)
            p = max(L - leads[i], pos[-1] + len(segs[i - 1]) / sr + 0.03)
            L = p + leads[i]
        pos.append(p)
        lands.append(L)
    out = np.zeros(int((pos[-1] + len(segs[-1]) / sr) * sr) + 1)
    for p, s in zip(pos, segs):
        k = int(round(p * sr))
        out[k: k + len(s)] += s
    return out, [round(float(v), 4) for v in lands]
