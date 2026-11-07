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


def synthesize(lines, mood=None, pinyin=(), groups=None, log=None):
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
