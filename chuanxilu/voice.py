"""本人克隆声旁白：CosyVoice 3 每句合成（念错的句子换种子重合成，最多 3 个候选） → 语音识别回写校验 → 选语调起伏最大的正确候选 → 统一音高。

python3 -m chuanxilu.voice ep01        # 合成并挑选，结果供 engine.audio.Narrator(VOICE) 读取
python3 -m chuanxilu.voice ep01 --report   # 只打印挑选结果

环境：CosyVoice 3 需要独立的 Python 3.10 虚拟环境（见 chuanxilu/README.md），路径由 COSY_PYTHON / COSYVOICE_DIR 指定。
录音放在 voices/<VOICE>/prompt.wav + prompt.txt（不入库）。
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

from engine import audio, gfx

from . import script

VOICE = "me_new"
INSTRUCT = ("You are a helpful assistant. 请用积极、充满好奇和热情的语气，语调起伏明显，"
            "像在给好朋友讲一个精彩的发现。<|endofprompt|>")
# 〔燃〕句（结尾鼓劲）用更有力的语气前缀；仍是零样本克隆，音色来自同一段录音，音高同样统一到录音原调
INSTRUCT_FIRE = ("You are a helpful assistant. 请用激昂有力、充满信心的语气，像在给好朋友打气，"
                 "句尾坚定上扬。<|endofprompt|>")
SEEDS, RETRY_SEEDS = (11,), (22, 33)
# 多音字：CosyVoice 3 支持用 [声母][韵母] 指定读音
PRON = {"种根": "[zh][òng]根", "种下": "[zh][òng]下", "空落落": "空[l][uò][l][uò]"}
COSY_PYTHON = os.environ.get("COSY_PYTHON", "/home/user/tts_eval/cv/bin/python")
ASR_DIR = audio.MODEL_ROOT / "sherpa-onnx-paraformer-zh-small-2024-03-09"
WORKER = Path(__file__).resolve().parent / "cosy_worker.py"


def voice_dir() -> Path:
    return audio.VOICE_DIR / VOICE


def write_config():
    """写 voices/<VOICE>/cosy.json，Narrator 据此进入 CosyVoice 缓存模式。"""
    (voice_dir() / "cosy.json").write_text(json.dumps({"engine": "cosyvoice3", "instruct": INSTRUCT},
                                                      ensure_ascii=False), encoding="utf-8")


def synth_text(text: str) -> str:
    for k, v in PRON.items():
        text = text.replace(k, v)
    return text


def _asr():
    import sherpa_onnx
    return sherpa_onnx.OfflineRecognizer.from_paraformer(paraformer=str(ASR_DIR / "model.int8.onnx"),
                                                         tokens=str(ASR_DIR / "tokens.txt"), num_threads=4)


def _pinyin(text: str) -> list[str]:
    from pypinyin import lazy_pinyin
    return lazy_pinyin(re.sub(r"[^一-鿿]", "", text))


def _cer(ref: list[str], hyp: list[str]) -> float:
    d = np.arange(len(hyp) + 1)
    for i, x in enumerate(ref, 1):
        prev, d[0] = d.copy(), i
        for j, y in enumerate(hyp, 1):
            d[j] = min(prev[j] + 1, d[j - 1] + 1, prev[j - 1] + (x != y))
    return float(d[-1]) / max(1, len(ref))


def _f0(y: np.ndarray, sr: int) -> np.ndarray:
    import librosa
    f0, voiced, _ = librosa.pyin(y, fmin=60, fmax=400, sr=sr, frame_length=1024)
    return f0[voiced & ~np.isnan(f0)]


def _load16k(path: Path) -> np.ndarray:
    import librosa
    return librosa.load(str(path), sr=16000)[0]


def run(ep: str, report_only: bool = False):
    """合成并挑选一讲的全部旁白句；有句子所有候选都念错时补一个种子再选，仍错则在报告中标出（不静默放过）。"""
    vd = voice_dir()
    if not (vd / "prompt.wav").is_file():
        raise FileNotFoundError(f"missing voice prompt: {vd}/prompt.wav")
    write_config()
    root = audio.cosy_dir(VOICE)
    raw = root / "raw"
    sents = {gfx.plain(s.text): s for sec in script.load(ep) for s in sec.sentences}
    jobs = []
    for t, sent in sents.items():
        fire = "燃" in sent.tags
        mkey = audio.cosy_key(t)
        jobs.append({"key": ("f" + mkey[1:]) if fire else mkey, "mkey": mkey, "text": t, "synth": synth_text(t),
                     "fire": fire})
    stats_path, meta_path = root / "stats.json", root / "meta.json"
    stats = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else {}
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    asr = None

    def synth(js, seeds):
        if report_only:
            return
        for fire, instruct in ((False, INSTRUCT), (True, INSTRUCT_FIRE)):
            group = [j for j in js if j["fire"] == fire]
            if not group:
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                json.dump(group, f, ensure_ascii=False)
            subprocess.run([COSY_PYTHON, str(WORKER), f.name, str(raw), str(vd), instruct,
                            ",".join(map(str, seeds))], check=True)

    def score(j):
        nonlocal asr
        rows = []
        for p in sorted(raw.glob(f"{j['key']}_*.wav")):
            if p.name not in stats:
                asr = asr or _asr()
                y = _load16k(p)
                s = asr.create_stream()
                s.accept_waveform(16000, y)
                asr.decode_stream(s)
                st = 12 * np.log2(_f0(y, 16000))
                stats[p.name] = dict(asr=s.result.text, cer=_cer(_pinyin(j["text"]), _pinyin(s.result.text)),
                                     range=float(np.percentile(st, 90) - np.percentile(st, 10)),
                                     median=float(np.median(2 ** (st / 12))))
            rows.append((p.name, stats[p.name]))
        return rows

    synth(jobs, SEEDS)
    for seed in RETRY_SEEDS:
        retry = [j for j in jobs if not any(r["cer"] == 0 for _, r in score(j))]
        synth(retry, (seed,))
    ref = float(np.median(_f0(_load16k(vd / "prompt.wav"), 16000)))
    bad = []
    for j in jobs:
        rows = score(j)
        if not rows:
            raise FileNotFoundError(f"no candidates for: {j['text']}")
        best = min(r["cer"] for _, r in rows)
        name, r = max([x for x in rows if x[1]["cer"] == best], key=lambda x: x[1]["range"])
        shift = float(np.clip(-0.7 * 12 * np.log2(r["median"] / ref), -2, 2))
        meta[j["mkey"]] = dict(text=j["text"], file=name, shift=round(shift, 3), cer=r["cer"], asr=r["asr"])
        if best > 0:
            bad.append((j["text"], r["asr"], best))
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(jobs)} lines, reference f0 {ref:.0f}Hz, {len(bad)} with pinyin mismatch")
    for text, hyp, e in bad:
        print(f"  [{e:.2f}] {text}\n         识别：{hyp}")


if __name__ == "__main__":
    run(sys.argv[1], "--report" in sys.argv)
