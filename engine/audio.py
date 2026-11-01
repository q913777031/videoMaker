"""音频：Kokoro 离线 TTS、程序化音效、人声处理、闪避混音与响度标准化（配乐见 bgm.py）。

所有合成均为确定性计算（固定随机种子），同一输入每次生成完全相同的音频。
"""

import functools
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter1d

SR = 44100
ROOT = Path(__file__).resolve().parent.parent
MODEL_ROOT = ROOT / "models"
CACHE_DIR = ROOT / ".cache" / "tts"
V10 = ("kokoro-multi-lang-v1_0", "model.onnx")
V11 = ("kokoro-int8-multi-lang-v1_1", "model.int8.onnx")
# 音色 → (模型目录, 模型文件, speaker id)；id 来自模型元数据 speaker2id。
# v1.1 为中文专项训练版本，发音标准度明显优于 v1.0。
VOICES = {
    "zf_001": (*V11, 3), "zm_009": (*V11, 58),
    "zf_xiaobei": (*V10, 45), "zf_xiaoni": (*V10, 46), "zf_xiaoxiao": (*V10, 47), "zf_xiaoyi": (*V10, 48),
    "zm_yunjian": (*V10, 49), "zm_yunxi": (*V10, 50), "zm_yunxia": (*V10, 51), "zm_yunyang": (*V10, 52),
}
# ZipVoice 音色 → 用作音色提示的 Kokoro 音色
ZV_DIR = "sherpa-onnx-zipvoice-distill-int8-zh-en-emilia"
ZIPVOICE = {"zv_yunxi": "zm_yunxi", "zv_009": "zm_009", "zv_001": "zf_001",
            "zv_yunjian": "zm_yunjian", "zv_yunyang": "zm_yunyang", "zv_yunxia": "zm_yunxia",
            "zv_xiaoxiao": "zf_xiaoxiao", "zv_xiaoyi": "zf_xiaoyi"}
PROMPT_TEXT = "其实每个人都可以重新开始，换一种方式，去过自己真正想要的生活。"
# CosyVoice3 音色：cv3_<x> 零样本、cv3i_<x> 语气指令；提示音 = ZipVoice 音色 zv_<x> 念 CV3_PROMPT_TEXT（全程合成音，不涉及真人）。
# 模型跑在 models/venv_tts 的子进程里（见 engine/cosyvoice_worker.py 的准备步骤）。文本里可用 [sh][ǎo] 这样的拼音标注纠正多音字。
CV3_PROMPT_TEXT = "工厂里每天都会出点小问题，我们先把它记下来，再一个一个慢慢解决。"
CV3_INSTRUCT = "请用温暖、恳切、有感染力的语气讲解，像在提醒一个朋友，语调要有起伏。"
CV3_PYTHON = MODEL_ROOT / "venv_tts" / "bin" / "python"
# IndexTTS2 音色：ix2_<x>，模型跑在 models/venv_tts 的子进程里（见 engine/indextts_worker.py 的准备步骤）。
# 音色提示（speaker prompt）全程用本地合成音：
#   ix2_cv3jian —— 第 01 讲《丰田模式》现用 CosyVoice3 旁白（cv3i_yunjian、prompt_speed 0.95）里的两句，约 9 秒，
#                  音色与 ep01 一致；首次使用时从 .cache/tts 的合成结果拼出，并另存到 models/ix2_prompts/（CV3 权重已删，靠它留底）；
#   ix2_<z>     —— ZipVoice 音色 zv_<z>（如 ix2_yunjian）念 IX2_PROMPT_TEXT。
IX2_PROMPT_DIR = MODEL_ROOT / "ix2_prompts"
IX2_PROMPT_TEXT = "工厂里每天都会出点小问题。我们先把它记下来，再一个一个慢慢解决，这样大家后面都能轻松一点。"
IX2_CV3_LINES = {"cv3jian": ["说回我们自己，这种事是不是天天都有？", "报表里有个[sh][ù]对不上，你想着先混过去，到月底对账，全乱了。"]}
# 情绪向量各维：喜 怒 哀 惧 厌恶 低落 惊讶 平静（IndexTTS2 顺序）
IX2_EMOTIONS = ("happy", "angry", "sad", "afraid", "disgusted", "melancholic", "surprised", "calm")


# ---------------------------------------------------------------- 基础工具

def _t(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def _sos(kind: str, freq, order: int = 2):
    return signal.butter(order, freq, kind, fs=SR, output="sos")


def lowpass(x, f, order=2):
    return signal.sosfilt(_sos("lowpass", f, order), x)


def highpass(x, f, order=2):
    return signal.sosfilt(_sos("highpass", f, order), x)


def bandpass(x, lo, hi, order=2):
    return signal.sosfilt(_sos("bandpass", [lo, hi], order), x)


def _noise(n: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).standard_normal(n)


def hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def _fade(x: np.ndarray, fin: float = 0.005, fout: float = 0.02) -> np.ndarray:
    x = x.copy()
    a, b = min(len(x), int(fin * SR)), min(len(x), int(fout * SR))
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def _sweep_filter(x: np.ndarray, centers: np.ndarray, width: float = 0.45) -> np.ndarray:
    """STFT 域的时变带通：centers 给出每帧中心频率（对数高斯窗），用于呼啸、上升音效。"""
    f, tt, z = signal.stft(x, fs=SR, nperseg=1024)
    fc = np.interp(tt, np.linspace(0, tt[-1] if len(tt) > 1 else 1, len(centers)), centers)
    lf = np.log(np.maximum(f, 20))[:, None]
    z *= np.exp(-((lf - np.log(fc)[None, :]) ** 2) / (2 * width ** 2))
    _, y = signal.istft(z, fs=SR, nperseg=1024)
    return y[: len(x)]


def reverb_ir(rt: float = 2.2, seed: int = 11) -> np.ndarray:
    """指数衰减噪声构成的合成混响脉冲响应。"""
    t = _t(rt)
    ir = _noise(len(t), seed) * np.exp(-6.9 * t / rt)
    ir = lowpass(ir, 6000)
    ir[: int(0.012 * SR)] = 0
    return ir / np.sqrt(np.sum(ir ** 2))


def reverb(x: np.ndarray, wet: float, rt: float = 2.2) -> np.ndarray:
    """单声道输入 → 立体声输出的卷积混响（左右声道使用不同脉冲响应以获得空间感）。"""
    out = np.zeros((len(x), 2))
    for ch, seed in enumerate((11, 23)):
        out[:, ch] = x * (1 - wet) + signal.fftconvolve(x, reverb_ir(rt, seed))[: len(x)] * wet * 0.6
    return out


def pan(x: np.ndarray, p: float = 0.0) -> np.ndarray:
    """单声道等功率声像，p ∈ [-1, 1]。"""
    a = (p + 1) * math.pi / 4
    return np.stack([x * math.cos(a), x * math.sin(a)], axis=1)


def place(track: np.ndarray, clip: np.ndarray, start: float, gain: float = 1.0):
    """把片段叠加到轨道指定时刻（越界部分截断）。"""
    i = int(start * SR)
    if i >= len(track) or i + len(clip) <= 0:
        return
    j0 = max(0, -i)
    j1 = min(len(clip), len(track) - i)
    track[i + j0: i + j1] += clip[j0:j1] * gain


# ---------------------------------------------------------------- TTS

class Narrator:
    """离线中文旁白；generate 返回 44.1kHz 单声道、首尾静音已裁剪的音频。

    音色名以 zv_ 开头时使用 ZipVoice（零样本、韵律接近真人）：先用对应的 Kokoro 音色合成一句提示音，
    ZipVoice 只借用其音色，发音与语调由 ZipVoice 自己生成，因此不涉及任何真人声音。
    ZipVoice 的语速跟随提示音：prompt_speed < 1（如 0.8）时提示音念得慢，生成的旁白整体放慢、停顿更自然；
    默认 1.0 与旧版完全相同（含缓存键）。

    音色名以 cv3_ / cv3i_ 开头时使用 CosyVoice3（如 "cv3i_yunjian"）：提示音由 zv_<同名> 合成（prompt_speed 同上），
    cv3i_ 额外带语气指令（instruct，默认 CV3_INSTRUCT）。首次合成时启动一个常驻子进程加载模型（约 30 秒），
    CPU 上每 10 秒语音约需 2–3 分钟，结果同样按键缓存；合成带随机采样，固定种子后同一文本结果可复现。

    音色名以 ix2_ 开头时使用 IndexTTS2（如 "ix2_cv3jian"，提示音见 IX2_CV3_LINES / IX2_PROMPT_TEXT）。
    emo 设情绪（也可在 generate(emo=…) 里逐句覆盖）：
      None                                   —— 不加控制，情绪跟随音色提示；
      {"text": "语气温和，耐心讲解", "alpha": 0.7} —— 文字描述情绪（模型自带 Qwen 情绪模型换算成向量）；
      {"vector": {"calm": 0.7, "happy": 0.2}, "alpha": 0.7}（或 8 个数的列表，顺序见 IX2_EMOTIONS）—— 情绪向量；
      {"audio": "某段合成音.wav", "alpha": 0.7}    —— 情绪参考音频（不得用真人录音）；
      字符串等同 {"text": 字符串, "alpha": 0.7}。
    IndexTTS2 没有语速参数：语速跟随提示音（prompt_speed≠1 时用 ffmpeg atempo 先把提示音变速）；
    generate 的 speed≠1 时取同一句原速的结果做 atempo 变速（不重新采样）。文本里的 CosyVoice 式拼音标注 [d][āng] 自动换成 IndexTTS2 的 DANG1。
    首次合成时启动常驻子进程加载模型（约 80 秒、内存约 9GB），CPU 上每 10 秒语音约需 4 分钟；缓存键含
    后端|音色提示|情绪参数|语速|文本，固定种子可复现。
    """

    def __init__(self, voice: str = "zv_yunxi", prompt_speed: float = 1.0, instruct: str | None = None, emo=None):
        self._prompt = None
        self._cv3 = None
        self._ix2 = None
        if voice.startswith("ix2_"):
            if not CV3_PYTHON.is_file():
                raise FileNotFoundError(f"TTS venv not found: {CV3_PYTHON} (see engine/indextts_worker.py)")
            name = voice[4:]
            if name not in IX2_CV3_LINES and "zv_" + name not in ZIPVOICE:
                raise KeyError(f"unknown voice {voice}: no IndexTTS2 prompt for {name}")
            wav = self._ix2_prompt(name, prompt_speed)
            ph = hashlib.sha1(wav.read_bytes()).hexdigest()[:12]
            self._ix2 = dict(wav=str(wav), emo=_ix2_emo(emo), proc=None)
            self._key = f"ix2|{voice}|{ph}|p{prompt_speed:.3f}"
            return
        if voice.startswith(("cv3_", "cv3i_")):
            zv = "zv_" + voice.split("_", 1)[1]
            if zv not in ZIPVOICE:
                raise KeyError(f"unknown voice {voice}: no ZipVoice prompt {zv}")
            if not CV3_PYTHON.is_file():
                raise FileNotFoundError(f"CosyVoice3 venv not found: {CV3_PYTHON} (see engine/cosyvoice_worker.py)")
            mode = "ins" if voice.startswith("cv3i_") else "zs"
            ins = "You are a helpful assistant. " + (instruct or CV3_INSTRUCT) + "<|endofprompt|>"
            self._cv3 = dict(voice=zv, prompt_speed=prompt_speed, mode=mode, instruct=ins, proc=None, wav=None)
            self._key = f"cv3|{voice}|p{prompt_speed:.3f}" + (f"|{ins}" if mode == "ins" else "")
            return
        import sherpa_onnx

        if voice in ZIPVOICE:
            d = str(MODEL_ROOT / ZV_DIR) + "/"
            if not Path(d + "decoder.int8.onnx").is_file():
                raise FileNotFoundError(f"TTS model not found: {d}decoder.int8.onnx")
            zv = sherpa_onnx.OfflineTtsZipvoiceModelConfig(
                tokens=d + "tokens.txt", encoder=d + "encoder.int8.onnx", decoder=d + "decoder.int8.onnx",
                vocoder=str(MODEL_ROOT / "vocos_24khz.onnx"), data_dir=d + "espeak-ng-data", lexicon=d + "lexicon.txt")
            self._tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
                model=sherpa_onnx.OfflineTtsModelConfig(zipvoice=zv, num_threads=4)))
            prompt = Narrator(ZIPVOICE[voice]).generate(PROMPT_TEXT, prompt_speed)
            self._prompt = signal.resample_poly(prompt, 24000, SR).astype(np.float32).tolist()
            self._key = f"{ZV_DIR}|{voice}" + (f"|p{prompt_speed:.3f}" if prompt_speed != 1.0 else "")
            return
        sub, model, self._sid = VOICES[voice]
        d = str(MODEL_ROOT / sub) + "/"
        if not Path(d + model).is_file():
            raise FileNotFoundError(f"TTS model not found: {d}{model}")
        kokoro = sherpa_onnx.OfflineTtsKokoroModelConfig(
            model=d + model, voices=d + "voices.bin", tokens=d + "tokens.txt",
            lexicon=f"{d}lexicon-us-en.txt,{d}lexicon-zh.txt", data_dir=d + "espeak-ng-data",
            dict_dir=d + "dict")
        cfg = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(kokoro=kokoro, num_threads=4),
            rule_fsts=f"{d}date-zh.fst,{d}phone-zh.fst,{d}number-zh.fst", max_num_sentences=1)
        self._tts = sherpa_onnx.OfflineTts(cfg)
        self._key = f"{sub}|{self._sid}"

    def generate(self, text: str, speed: float = 1.0, num_steps: int = 4, emo=None) -> np.ndarray:
        """合成一句旁白；结果按 (音色, 语速, 文本[, 步数]) 缓存到 .cache/tts，改画面重渲染时无需重新合成。

        num_steps 为 ZipVoice 的去噪步数（默认 4；调高更慢、可能更自然），Kokoro 音色忽略此参数。
        默认步数的缓存键与旧版相同，已有缓存继续有效。emo 只对 ix2_ 音色有效（逐句覆盖构造时的情绪）。"""
        steps = f"|steps{num_steps}" if self._prompt is not None and num_steps != 4 else ""
        if self._ix2 is not None:                 # IndexTTS2：后端|音色提示|情绪参数|语速|文本（num_steps 不用）
            e = self._ix2["emo"] if emo is None else _ix2_emo(emo)
            raw = f"{self._key}|{json.dumps(e, sort_keys=True, ensure_ascii=False)}|{speed:.4f}|{text}"
        else:
            raw = f"{self._key}|{speed:.4f}|{text}{steps}"
        key = hashlib.sha1(raw.encode()).hexdigest()
        path = CACHE_DIR / f"{key}.npy"
        if path.exists():
            return np.load(path)
        if self._ix2 is not None:
            if abs(speed - 1.0) > 1e-6:           # 变速版 = 原速版（同一份采样结果）再 atempo，换语速不重新采样
                x, sr = _atempo(self.generate(text, 1.0, num_steps, emo), SR, speed), SR
            else:
                x, sr = self._ix2_generate(_ix2_pinyin(text), e, int(key[:8], 16))
            a = type("A", (), {"samples": x, "sample_rate": sr})
        elif self._cv3 is not None:
            x, sr = self._cv3_generate(text, speed, int(key[:8], 16))
            a = type("A", (), {"samples": x, "sample_rate": sr})
        elif self._prompt is not None:
            a = self._tts.generate(text, PROMPT_TEXT, self._prompt, 24000, speed, num_steps)
        else:
            a = self._tts.generate(text, sid=self._sid, speed=speed)
        x = np.asarray(a.samples, np.float64)
        if a.sample_rate != SR:
            g = math.gcd(SR, a.sample_rate)
            x = signal.resample_poly(x, SR // g, a.sample_rate // g)
        x = _trim(x)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        np.save(path, x)
        return x

    def _cv3_generate(self, text: str, speed: float, seed: int):
        """把一句交给 CosyVoice3 子进程；首次调用时合成提示音并启动子进程。"""
        import json
        import subprocess
        import tempfile

        import soundfile as sf

        c = self._cv3
        if c["proc"] is None:
            p = Narrator(c["voice"], prompt_speed=c["prompt_speed"]).generate(CV3_PROMPT_TEXT, 1.0, 8)
            c["tmp"] = tempfile.TemporaryDirectory()
            c["wav"] = str(Path(c["tmp"].name) / "prompt.wav")
            sf.write(c["wav"], signal.resample_poly(p, 160, 441).astype(np.float32), 16000)
            c["proc"] = subprocess.Popen([str(CV3_PYTHON), "-I", str(ROOT / "engine" / "cosyvoice_worker.py")],
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                         text=True, bufsize=1)
            self._cv3_reply()
        out = str(Path(c["tmp"].name) / "out.wav")
        q = dict(text=text, mode=c["mode"], prompt_wav=c["wav"], prompt_text=CV3_PROMPT_TEXT, instruct=c["instruct"],
                 speed=speed, seed=seed, out=out)
        c["proc"].stdin.write(json.dumps(q, ensure_ascii=False) + "\n")
        c["proc"].stdin.flush()
        r = self._cv3_reply()
        if not r.get("ok"):
            raise RuntimeError(f"CosyVoice3 failed: {r.get('err')}")
        x, sr = sf.read(out)
        return x, sr

    def _cv3_reply(self) -> dict:
        import json

        for line in self._cv3["proc"].stdout:
            line = line.strip()
            if line.startswith("{"):
                return json.loads(line)
        raise RuntimeError("CosyVoice3 worker exited")

    # ---------------------------------------------------------------- IndexTTS2
    @staticmethod
    def _ix2_prompt(name: str, prompt_speed: float) -> Path:
        """音色提示 wav（24kHz）：先找 models/ix2_prompts/<name>.wav，没有就用本地合成音拼出并存下。"""
        import soundfile as sf

        base = IX2_PROMPT_DIR / f"{name}.wav"
        if not base.is_file():
            if name in IX2_CV3_LINES:            # 只读缓存：CosyVoice3 权重已删，缓存缺失时直接报错
                cv = Narrator("cv3i_yunjian", prompt_speed=0.95)
                xs = []
                for t in IX2_CV3_LINES[name]:
                    k = hashlib.sha1(f"{cv._key}|{1.0:.4f}|{t}".encode()).hexdigest()
                    p = CACHE_DIR / f"{k}.npy"
                    if not p.is_file():
                        raise FileNotFoundError(f"CosyVoice3 cache missing for prompt line: {t} ({p})")
                    xs.append(np.load(p))
                y = np.concatenate([xs[0], np.zeros(int(0.5 * SR))] + xs[1:])
            else:
                y = Narrator("zv_" + name).generate(IX2_PROMPT_TEXT, 1.0, 8)
            y = y * (0.89 / max(1e-9, np.abs(y).max()))
            IX2_PROMPT_DIR.mkdir(parents=True, exist_ok=True)
            sf.write(base, signal.resample_poly(y, 240, 441).astype(np.float32), 24000)
        if abs(prompt_speed - 1.0) < 1e-6:
            return base
        out = IX2_PROMPT_DIR / f"{name}_p{prompt_speed:.3f}.wav"
        if not out.is_file():
            _atempo_file(base, out, prompt_speed)
        return out

    def _ix2_generate(self, text: str, emo: dict | None, seed: int):
        """把一句交给 IndexTTS2 子进程；首次调用时启动子进程。"""
        import json as _json
        import subprocess
        import tempfile

        import soundfile as sf

        c = self._ix2
        if c["proc"] is None:
            c["tmp"] = tempfile.TemporaryDirectory()
            c["proc"] = subprocess.Popen([str(CV3_PYTHON), "-I", str(ROOT / "engine" / "indextts_worker.py")],
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                         text=True, bufsize=1, cwd=c["tmp"].name)
            self._ix2_reply()
        out = str(Path(c["tmp"].name) / "out.wav")
        q = dict(text=text, spk_wav=c["wav"], seed=seed, out=out)
        if emo:
            q["emo_alpha"] = emo["alpha"]
            for k, qk in (("vector", "emo_vector"), ("text", "emo_text"), ("audio", "emo_wav")):
                if k in emo:
                    q[qk] = emo[k]
        c["proc"].stdin.write(_json.dumps(q, ensure_ascii=False) + "\n")
        c["proc"].stdin.flush()
        r = self._ix2_reply()
        if not r.get("ok"):
            raise RuntimeError(f"IndexTTS2 failed: {r.get('err')}")
        c["last"] = r
        x, sr = sf.read(out)
        return x, sr

    def _ix2_reply(self) -> dict:
        import json as _json

        for line in self._ix2["proc"].stdout:
            line = line.strip()
            if line.startswith("{"):
                return _json.loads(line)
        raise RuntimeError("IndexTTS2 worker exited")


def _ix2_emo(emo):
    """把 emo 参数整理成规范 dict（进缓存键）：{"alpha": a, "text"|"vector"|"audio": …}。"""
    if emo is None:
        return None
    if isinstance(emo, str):
        emo = {"text": emo}
    e = dict(emo)
    alpha = float(e.pop("alpha", 0.7))
    if "vector" in e:
        v = e["vector"]
        if isinstance(v, dict):
            bad = set(v) - set(IX2_EMOTIONS)
            if bad:
                raise KeyError(f"unknown emotions {bad}; use {IX2_EMOTIONS}")
            v = [float(v.get(k, 0.0)) for k in IX2_EMOTIONS]
        if len(v) != 8:
            raise ValueError("emotion vector needs 8 values")
        return {"alpha": round(alpha, 3), "vector": [round(float(x), 4) for x in v]}
    if "text" in e:
        return {"alpha": round(alpha, 3), "text": str(e["text"])}
    if "audio" in e:
        p = Path(e["audio"]).resolve()
        return {"alpha": round(alpha, 3), "audio": str(p), "sha": hashlib.sha1(p.read_bytes()).hexdigest()[:12]}
    raise ValueError(f"bad emo {emo!r}")


_TONES = {"ā": "a1", "á": "a2", "ǎ": "a3", "à": "a4", "ō": "o1", "ó": "o2", "ǒ": "o3", "ò": "o4",
          "ē": "e1", "é": "e2", "ě": "e3", "è": "e4", "ī": "i1", "í": "i2", "ǐ": "i3", "ì": "i4",
          "ū": "u1", "ú": "u2", "ǔ": "u3", "ù": "u4", "ǖ": "v1", "ǘ": "v2", "ǚ": "v3", "ǜ": "v4", "ü": "v"}


def _ix2_pinyin(text: str) -> str:
    """CosyVoice 式拼音标注 "[d][āng]场" → IndexTTS2 式 "DANG1场"（拼音大写 + 声调数字，替换掉那个字）。

    也可以直接在文本里写 IndexTTS2 式：把多音字换成大写拼音加声调（1–4，轻声 5），如 "先YING4付一下"。"""
    import re

    def conv(m):
        py = "".join(re.findall(r"\[([^\]]+)\]", m.group(0)))
        tone = "5"
        out = ""
        for ch in py:
            t = _TONES.get(ch)
            if t is None:
                out += ch
            else:
                out += t[0]
                if len(t) > 1:
                    tone = t[1]
        return out.upper() + tone

    return re.sub(r"(?:\[[a-zāáǎàōóǒòēéěèīíǐìūúǔùǖǘǚǜü]+\])+", conv, text)


def _atempo(x: np.ndarray, sr: int, tempo: float) -> np.ndarray:
    import tempfile

    import soundfile as sf

    with tempfile.TemporaryDirectory() as d:
        sf.write(f"{d}/a.wav", np.asarray(x, np.float32), sr)
        _atempo_file(f"{d}/a.wav", f"{d}/b.wav", tempo)
        y, _ = sf.read(f"{d}/b.wav")
    return np.asarray(y, np.float64)


def _atempo_file(src, dst, tempo: float):
    """ffmpeg atempo 变速不变调（tempo>1 变快）。"""
    import subprocess

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-filter:a", f"atempo={tempo:.4f}", str(dst)],
                   check=True)


def _trim(x: np.ndarray, thr_db: float = -38.0) -> np.ndarray:
    """按 10ms 帧能量裁掉首尾静音，前留 30ms、后留 80ms。"""
    hop = int(0.01 * SR)
    frames = len(x) // hop
    if frames == 0:
        return x
    rms = np.sqrt(np.mean(x[: frames * hop].reshape(frames, hop) ** 2, axis=1) + 1e-12)
    on = np.where(20 * np.log10(rms / rms.max()) > thr_db)[0]
    if len(on) == 0:
        return x
    a = max(0, on[0] * hop - int(0.03 * SR))
    b = min(len(x), (on[-1] + 1) * hop + int(0.08 * SR))
    return _fade(x[a:b], 0.005, 0.03)


def process_voice(x: np.ndarray) -> np.ndarray:
    """人声处理链：高通 → 低频温暖 + 临场感 EQ → 压缩 → 峰值归一化。"""
    y = highpass(x, 80)
    y = y + 0.18 * bandpass(y, 120, 300) + 0.25 * bandpass(y, 2500, 4500)
    hop = int(0.01 * SR)
    frames = int(np.ceil(len(y) / hop))
    pad = np.pad(y, (0, frames * hop - len(y)))
    rms = np.sqrt(np.mean(pad.reshape(frames, hop) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    thr, ratio = -24.0, 3.0
    gain_db = np.where(db > thr, (thr - db) * (1 - 1 / ratio), 0.0)
    gain_db = signal.lfilter([0.3], [1, -0.7], gain_db)
    gain = np.repeat(10 ** (gain_db / 20), hop)[: len(y)]
    y = y * gain
    return y / (np.max(np.abs(y)) + 1e-9) * 0.7


# ---------------------------------------------------------------- 音效

def _pop(base: float = 500) -> np.ndarray:
    t = _t(0.14)
    f = base + base * 1.4 * (1 - np.exp(-t * 60))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)
    return _fade(y * 0.8)


def _bell(freq: float = 1568, dur: float = 1.2, seed: int = 0) -> np.ndarray:
    t = _t(dur)
    y = sum(a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t * d)
            for r, a, d in ((1, 1, 3), (2.0, 0.45, 4.5), (2.76, 0.35, 6), (5.4, 0.18, 9)))
    return _fade(y * 0.5, 0.002, 0.1)


def _whoosh(dur: float = 0.5, seed: int = 1, up: bool = True) -> np.ndarray:
    n = int(dur * SR)
    x = _noise(n, seed)
    k = np.linspace(0, 1, 32)
    centers = 300 * (12 ** np.sin(np.pi * k)) if up else 4000 * (0.1 ** k)
    y = _sweep_filter(x, centers, 0.5)
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return _fade(y * env / (np.max(np.abs(y)) + 1e-9))


def _boom(dur: float = 1.4, seed: int = 2) -> np.ndarray:
    t = _t(dur)
    f = 45 + 70 * np.exp(-t * 18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    noise = lowpass(_noise(len(t), seed), 300) * np.exp(-t * 10) * 0.5
    y = np.tanh(2.2 * (sub + noise))
    return _fade(y * 0.9, 0.001, 0.2)


def _impact(seed: int = 3) -> np.ndarray:
    t = _t(2.8)
    y = np.zeros(len(t))
    b = _boom(2.0, seed)
    y[: len(b)] += b
    crash = highpass(_noise(len(t), seed + 1), 3000) * np.exp(-t * 2.4) * 0.35
    return _fade(y + crash, 0.001, 0.4)


def _riser(dur: float, seed: int = 4) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    k = np.linspace(0, 1, 48)
    noise = _sweep_filter(_noise(n, seed), 250 * (40 ** k), 0.35)
    noise /= np.max(np.abs(noise)) + 1e-9
    f = 180 * (8 ** (t / dur))
    trem = 1 + 0.35 * np.sin(2 * np.pi * np.cumsum(4 + 14 * t / dur) / SR)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * trem * 0.35
    env = (t / dur) ** 2.2
    return _fade((noise * 0.8 + tone) * env, 0.01, 0.03)


def _crack(seed: int = 5) -> np.ndarray:
    rng = np.random.default_rng(seed)
    y = np.zeros(int(0.45 * SR))
    for k in range(9):
        i = int(rng.uniform(0, 0.32) * SR)
        burst = highpass(_noise(int(0.006 * SR), seed + k), 1800) * rng.uniform(0.4, 1.0)
        y[i: i + len(burst)] += burst * np.exp(-np.arange(len(burst)) / (0.002 * SR))
    thud = _boom(0.4, seed)[: len(y)] * 0.4
    y[: len(thud)] += thud
    return _fade(y * 0.8)


def _heart(seed: int = 6) -> np.ndarray:
    y = np.zeros(int(0.9 * SR))
    for k, (start, a) in enumerate(((0.0, 1.0), (0.27, 0.75))):
        t = _t(0.25)
        f = 48 + 25 * np.exp(-t * 25)
        thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16) * a
        i = int(start * SR)
        y[i: i + len(thump)] += thump
    return _fade(np.tanh(1.8 * y))


def _glitch(seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    y = np.zeros(int(0.4 * SR))
    i = 0
    while i < len(y):
        seg = int(rng.uniform(0.012, 0.045) * SR)
        if rng.random() < 0.7:
            f = rng.uniform(150, 2400)
            t = np.arange(seg) / SR
            s = np.sign(np.sin(2 * np.pi * f * t)) * 0.35 if rng.random() < 0.5 else _noise(seg, int(rng.integers(1_000_000))) * 0.3
            y[i: i + seg] += s[: len(y) - i]
        i += seg
    return _fade(np.round(y * 8) / 8)


def _shimmer(seed: int = 8) -> np.ndarray:
    y = np.zeros(int(1.6 * SR))
    for k, m in enumerate((84, 88, 91, 96, 100)):
        b = _bell(hz(m), 1.0) * (0.6 - k * 0.07)
        place(y, b, k * 0.06)
    return y


def _down(seed: int = 9) -> np.ndarray:
    t = _t(0.55)
    f = 520 * (0.25 ** (t / 0.55))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3)
    y += 0.3 * np.sin(2 * np.pi * 2 * np.cumsum(f) / SR) * np.exp(-t * 5)
    return _fade(lowpass(y, 2500) * 0.7)


def _buzz(seed: int = 10) -> np.ndarray:
    t = _t(0.32)
    y = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5 + np.sign(np.sin(2 * np.pi * 116 * t)) * 0.3
    return _fade(lowpass(y, 1800) * np.exp(-t * 4) * 0.6)


def _type(dur: float = 0.8, seed: int = 12) -> np.ndarray:
    rng = np.random.default_rng(seed)
    y = np.zeros(int(dur * SR) + 2000)
    t = 0.0
    while t < dur:
        click = bandpass(_noise(int(0.004 * SR), int(rng.integers(1_000_000))), 2000, 6000)
        place(y, click * np.exp(-np.arange(len(click)) / 40.0), t, rng.uniform(0.4, 0.8))
        t += rng.uniform(0.05, 0.11)
    return y


@functools.lru_cache(maxsize=64)
def sfx(name: str, param: float = 0.0) -> np.ndarray:
    """按名称生成音效（单声道）；riser/type 的 param 为时长秒数。"""
    table = {
        "pop": lambda: _pop(500), "pop2": lambda: _pop(800), "ding": lambda: _bell(1568),
        "whoosh": lambda: _whoosh(0.5, 1, True), "swoosh": lambda: _whoosh(0.3, 2, False),
        "boom": lambda: _boom(), "impact": lambda: _impact(), "riser": lambda: _riser(param or 2.0),
        "crack": lambda: _crack(), "heart": lambda: _heart(), "glitch": lambda: _glitch(),
        "shimmer": lambda: _shimmer(), "down": lambda: _down(), "buzz": lambda: _buzz(),
        "type": lambda: _type(param or 0.8),
    }
    return table[name]()


# ---------------------------------------------------------------- 混音

def duck_envelope(voice: np.ndarray) -> np.ndarray:
    """由人声能量得到 [0, 1] 的闪避包络（含保持与平滑）。"""
    hop = int(0.02 * SR)
    frames = int(np.ceil(len(voice) / hop))
    pad = np.pad(voice, (0, frames * hop - len(voice)))
    rms = np.sqrt(np.mean(pad.reshape(frames, hop) ** 2, axis=1))
    env = np.clip(rms / 0.02, 0, 1)
    env = maximum_filter1d(env, size=10)
    env = signal.lfilter([0.25], [1, -0.75], env)
    return np.clip(np.repeat(env, hop)[: len(voice)], 0, 1)


def master(voice: np.ndarray, music: np.ndarray, sfx_track: np.ndarray, lufs: float = -14.0) -> np.ndarray:
    """人声 + 闪避后的配乐 + 音效混合，响度标准化到目标 LUFS，并软限幅到约 -3 dBFS（AAC 编码会抬高真峰值，需留余量）。"""
    import pyloudnorm

    n = min(len(voice), len(music), len(sfx_track))
    v = voice[:n]
    duck = duck_envelope(v)[:, None]
    mix_ = pan(v, 0) * 1.41 + music[:n] * (0.55 - 0.33 * duck) + sfx_track[:n] * (0.55 - 0.15 * duck)
    meter = pyloudnorm.Meter(SR)
    loud = meter.integrated_loudness(mix_)
    mix_ = mix_ * 10 ** ((lufs - loud) / 20)
    a = np.abs(mix_)
    knee, ceil = 0.55, 0.7
    over = a > knee
    mix_[over] = np.sign(mix_[over]) * (knee + (ceil - knee) * np.tanh((a[over] - knee) / (ceil - knee)))
    return mix_.astype(np.float32)
