"""本人克隆声旁白 + 角色配音：CosyVoice 3 每句合成（念错的句子换种子重合成，最多 3 个候选） → 语音识别回写校验
→ 在读对的候选里选语调起伏最接近自然水平的一个（避免个别字音调过重） → 统一到各自录音的原调。

角色台词在文案行尾标角色名（如〔慢｜王阳明〕），用 ROLES 里的音色；角色音色的提示音由离线合成音色生成，不克隆任何真人。

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
INSTRUCT = ("You are a helpful assistant. 请用亲切自然、有精神的语气，像跟好朋友聊天，"
            "每个字都轻松平稳，不要刻意加重字音。<|endofprompt|>")
# 〔燃〕句（结尾鼓劲）用更有力的语气前缀；仍是零样本克隆，音色来自同一段录音，音高同样统一到录音原调
INSTRUCT_FIRE = ("You are a helpful assistant. 请用激昂有力、充满信心的语气，像在给好朋友打气，"
                 "气息饱满但字音不要砸得太重。<|endofprompt|>")
# 角色 → (音色目录, 语气前缀)；voices/wym 的提示音由 Kokoro 合成音色 zm_yunyang 生成
ROLES = {"王阳明": ("wym", "You are a helpful assistant. 请用沉稳温和、略带笑意的中年男性语气，"
                         "慢慢地、像在跟学生谈心一样说。<|endofprompt|>")}
TARGET_RANGE = 4.5  # 句内音高起伏（第 10–90 百分位，半音）的自然水平
SEEDS, RETRY_SEEDS = (11,), (22, 33)
# 多音字：CosyVoice 3 支持用 [声母][韵母] 指定读音
PRON = {"种根": "[zh][òng]根", "种下": "[zh][òng]下", "空落落": "空[l][uò][l][uò]", "廷杖": "廷[zh][àng]"}
COSY_PYTHON = os.environ.get("COSY_PYTHON", "/home/user/tts_eval/cv/bin/python")
ASR_DIR = audio.MODEL_ROOT / "sherpa-onnx-paraformer-zh-small-2024-03-09"
WORKER = Path(__file__).resolve().parent / "cosy_worker.py"


def voice_dir(voice: str = VOICE) -> Path:
    return audio.VOICE_DIR / voice


def write_config(voice: str = VOICE, instruct: str = INSTRUCT):
    """写 voices/<音色>/cosy.json，Narrator 据此进入 CosyVoice 缓存模式（前缀变了，缓存目录随之更换）。"""
    (voice_dir(voice) / "cosy.json").write_text(json.dumps({"engine": "cosyvoice3", "instruct": instruct},
                                                           ensure_ascii=False), encoding="utf-8")


def role_voice(tags: set[str]) -> str | None:
    """句子标注里的角色名 → 角色音色；旁白句返回 None。"""
    for name, (v, _) in ROLES.items():
        if name in tags:
            return v
    return None


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
    """合成并挑选一讲的全部旁白与角色台词；所有候选都念错的句子在报告中标出（不静默放过）。"""
    groups = {VOICE: INSTRUCT} | {v: ins for v, ins in ROLES.values()}
    for v, ins in groups.items():
        if not (voice_dir(v) / "prompt.wav").is_file():
            raise FileNotFoundError(f"missing voice prompt: {voice_dir(v)}/prompt.wav")
        write_config(v, ins)
    jobs = []
    for sec in script.load(ep):
        for sent in sec.sentences:
            t = gfx.plain(sent.text)
            v = role_voice(sent.tags) or VOICE
            fire = "燃" in sent.tags and v == VOICE
            mkey = audio.cosy_key(t)
            jobs.append({"key": ("f" + mkey[1:]) if fire else mkey, "mkey": mkey, "text": t, "synth": synth_text(t),
                         "voice": v, "instruct": INSTRUCT_FIRE if fire else groups[v]})
    jobs = list({(j["voice"], j["mkey"]): j for j in jobs}.values())
    roots = {v: audio.cosy_dir(v) for v in groups}
    stats, metas = {}, {}
    for v, root in roots.items():
        sp, mp = root / "stats.json", root / "meta.json"
        stats[v] = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
        metas[v] = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
    asr = None
    ref_cache: dict[str, float] = {}

    def refs_f0(v: str) -> float:
        if v not in ref_cache:
            ref_cache[v] = float(np.median(_f0(_load16k(voice_dir(v) / "prompt.wav"), 16000)))
        return ref_cache[v]

    def synth(js, seeds):
        if report_only:
            return
        for (v, ins) in {(j["voice"], j["instruct"]) for j in js}:
            group = [j for j in js if j["voice"] == v and j["instruct"] == ins]
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                json.dump(group, f, ensure_ascii=False)
            subprocess.run([COSY_PYTHON, str(WORKER), f.name, str(roots[v] / "raw"), str(voice_dir(v)), ins,
                            ",".join(map(str, seeds))], check=True)

    def score(j):
        nonlocal asr
        st_v, rows = stats[j["voice"]], []
        for p in sorted((roots[j["voice"]] / "raw").glob(f"{j['key']}_*.wav")):
            if p.name not in st_v:
                asr = asr or _asr()
                y = _load16k(p)
                s_ = asr.create_stream()
                s_.accept_waveform(16000, y)
                asr.decode_stream(s_)
                f0 = _f0(y, 16000)
                if len(f0) < 10:
                    # 无浊音（静音或坏输出）：记为读错，交给换种子重合成
                    st_v[p.name] = dict(asr=s_.result.text, cer=1.0, range=0.0, median=refs_f0(j["voice"]))
                else:
                    st = 12 * np.log2(f0)
                    st_v[p.name] = dict(asr=s_.result.text, cer=_cer(_pinyin(j["text"]), _pinyin(s_.result.text)),
                                        range=float(np.percentile(st, 90) - np.percentile(st, 10)),
                                        median=float(np.median(f0)))
            rows.append((p.name, st_v[p.name]))
        return rows

    synth(jobs, SEEDS)
    for seed in RETRY_SEEDS:
        synth([j for j in jobs if not any(r["cer"] == 0 for _, r in score(j))], (seed,))
    refs = {v: refs_f0(v) for v in groups}
    bad = []
    for j in jobs:
        rows = score(j)
        if not rows:
            raise FileNotFoundError(f"no candidates for: {j['text']}")
        best = min(r["cer"] for _, r in rows)
        name, r = min([x for x in rows if x[1]["cer"] == best], key=lambda x: abs(x[1]["range"] - TARGET_RANGE))
        shift = float(np.clip(-0.7 * 12 * np.log2(r["median"] / refs[j["voice"]]), -2, 2))
        metas[j["voice"]][j["mkey"]] = dict(text=j["text"], file=name, shift=round(shift, 3), cer=r["cer"],
                                           asr=r["asr"])
        if best > 0:
            bad.append((j["voice"], j["text"], r["asr"], best))
    for v, root in roots.items():
        (root / "stats.json").write_text(json.dumps(stats[v], ensure_ascii=False, indent=1), encoding="utf-8")
        (root / "meta.json").write_text(json.dumps(metas[v], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(jobs)} lines, reference f0 " + ", ".join(f"{v} {f:.0f}Hz" for v, f in refs.items())
          + f", {len(bad)} with pinyin mismatch")
    for v, text, hyp, e in bad:
        print(f"  [{e:.2f}] ({v}) {text}\n         识别：{hyp}")


if __name__ == "__main__":
    run(sys.argv[1], "--report" in sys.argv)
