"""音频：Kokoro 离线 TTS、程序化音效、人声处理、闪避混音与响度标准化（配乐见 bgm.py）。

所有合成均为确定性计算（固定随机种子），同一输入每次生成完全相同的音频。
"""

import functools
import hashlib
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
ZIPVOICE = {"zv_yunxi": "zm_yunxi", "zv_009": "zm_009", "zv_001": "zf_001"}
PROMPT_TEXT = "其实每个人都可以重新开始，换一种方式，去过自己真正想要的生活。"


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
    """

    def __init__(self, voice: str = "zv_yunxi"):
        import sherpa_onnx

        self._prompt = None
        if voice in ZIPVOICE:
            d = str(MODEL_ROOT / ZV_DIR) + "/"
            if not Path(d + "decoder.int8.onnx").is_file():
                raise FileNotFoundError(f"TTS model not found: {d}decoder.int8.onnx")
            zv = sherpa_onnx.OfflineTtsZipvoiceModelConfig(
                tokens=d + "tokens.txt", encoder=d + "encoder.int8.onnx", decoder=d + "decoder.int8.onnx",
                vocoder=str(MODEL_ROOT / "vocos_24khz.onnx"), data_dir=d + "espeak-ng-data", lexicon=d + "lexicon.txt")
            self._tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
                model=sherpa_onnx.OfflineTtsModelConfig(zipvoice=zv, num_threads=4)))
            prompt = Narrator(ZIPVOICE[voice]).generate(PROMPT_TEXT, 1.0)
            self._prompt = signal.resample_poly(prompt, 24000, SR).astype(np.float32).tolist()
            self._key = f"{ZV_DIR}|{voice}"
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

    def generate(self, text: str, speed: float = 1.0) -> np.ndarray:
        """合成一句旁白；结果按 (音色, 语速, 文本) 缓存到 .cache/tts，改画面重渲染时无需重新合成。"""
        key = hashlib.sha1(f"{self._key}|{speed:.4f}|{text}".encode()).hexdigest()
        path = CACHE_DIR / f"{key}.npy"
        if path.exists():
            return np.load(path)
        if self._prompt is not None:
            a = self._tts.generate(text, PROMPT_TEXT, self._prompt, 24000, speed, 4)
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
