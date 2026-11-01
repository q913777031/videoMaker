"""丰田模式系列旁白：IndexTTS2 方案 2（音色取第 01 讲旁白，逐句文字情绪，强度 0.7）。

第 02 讲起各分镜模块统一调用 synthesize(LINES, LINE_MOOD, PINYIN)；参数与第 01 讲 NARRATOR 一致，缓存可互相命中。
"""
from engine import audio

VOICE = "ix2_cv3jian"
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


def synthesize(lines, mood, pinyin, log=None):
    """逐句合成 44.1kHz 单声道（首尾静音已裁）；lines 为 LINES 或整句列表，mood 每句一个情绪键。"""
    global _NAR
    texts = [ln[0] if isinstance(ln, tuple) else ln for ln in lines]
    assert len(mood) == len(texts), (len(mood), len(texts))
    if _NAR is None:
        _NAR = audio.Narrator(VOICE)
    out = []
    for i, (t, m) in enumerate(zip(texts, mood)):
        out.append(_NAR.generate(tts_text(t, pinyin), 1.0, 8, emo={"text": EMO[m], "alpha": ALPHA}))
        if log:
            print(f"  {i:02d} {len(out[-1]) / audio.SR:.1f}s {t}", file=log, flush=True)
    return out
