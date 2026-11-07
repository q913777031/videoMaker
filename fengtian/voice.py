"""丰田模式系列旁白：IndexTTS2，音色取第 01 讲旁白（cv3jian），平淡叙述语气。

用户选定（试听 4 的方案 3）：全程固定一个平静情绪向量，同一屏的几句连起来一次合成，再按句切开，
句与句之间语调连贯、不会突然拔高。各分镜模块统一调用 synthesize(LINES, LINE_MOOD, PINYIN, groups)；
groups 是每屏的句序号列表（取自 SCREENS），不给则逐句合成。LINE_MOOD 保留在文案里，不再参与合成。
"""
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


def split_group(x, texts):
    """一段连读音频按句切开：句界预期位置（按字数）±15% 内最长的静音段，从中间切。找不到句界时抛 RuntimeError。"""
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
            runs.append((i, j))
            i = j
        else:
            i += 1
    tot = sum(map(_han, texts))
    cuts, acc = [0], 0
    for t in texts[:-1]:
        acc += _han(t)
        c = acc / tot * n
        cand = [(b - a, a, b) for a, b in runs if abs((a + b) / 2 - c) < 0.15 * n and a > cuts[-1]]
        if not cand:
            raise RuntimeError(f"找不到句界：{t}")
        _, a, b = max(cand)
        cuts.append((a + b) // 2)
    cuts.append(n)
    return [audio._trim(x[a * hop: b * hop]) for a, b in zip(cuts, cuts[1:])]


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
