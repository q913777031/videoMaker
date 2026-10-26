"""旁白回听：用 SenseVoice 离线识别逐句转写 TTS 结果，与字幕文本逐字比对，列出可能读错的句子。"""

import difflib

import numpy as np
from scipy import signal

from engine import audio
from engine.gfx import plain

MODEL = audio.MODEL_ROOT / "sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17"


def _keep(s: str) -> str:
    return "".join(ch for ch in s if ch.isalnum())


def check(scenes, voice: str = "zv_yunxi", base_speed: float = 1.0) -> list[tuple[str, str, float]]:
    """返回 [(字幕文本, 识别文本, 相似度)]；相似度按去标点后的逐字比对计算。"""
    import sherpa_onnx

    rec = sherpa_onnx.OfflineRecognizer.from_sense_voice(
        model=str(MODEL / "model.int8.onnx"), tokens=str(MODEL / "tokens.txt"), language="zh", use_itn=True)
    narrator = audio.Narrator(voice)
    out = []
    for s in scenes:
        for ln in s.lines:
            x = narrator.generate(ln.spoken(), base_speed * ln.speed)
            st = rec.create_stream()
            st.accept_waveform(16000, signal.resample_poly(x, 160, 441).astype(np.float32))
            rec.decode_stream(st)
            got = st.result.text
            ref = plain(ln.text)
            out.append((ref, got, difflib.SequenceMatcher(None, _keep(ref), _keep(got)).ratio()))
    return out
