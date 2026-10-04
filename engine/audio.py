"""音频：Kokoro 离线 TTS、程序化音效与配乐合成、人声处理、闪避混音与响度标准化。

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
    """Kokoro 离线中文旁白；generate 返回 44.1kHz 单声道、首尾静音已裁剪的音频。"""

    def __init__(self, voice: str = "zf_001"):
        import sherpa_onnx

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


# ---------------------------------------------------------------- 乐器

def _piano(freq: float, dur: float, vel: float = 0.6) -> np.ndarray:
    t = _t(dur + 1.6)
    y = np.zeros(len(t))
    for k, amp in enumerate((1, 0.55, 0.32, 0.18, 0.1, 0.06, 0.035), start=1):
        fk = freq * k * math.sqrt(1 + 0.0004 * k * k)
        if fk > 11000:
            break
        y += amp * np.sin(2 * np.pi * fk * t) * np.exp(-t * (1.1 + 0.8 * k + freq / 700))
    env = (1 - np.exp(-t * 500)) * np.where(t < dur, 1.0, np.exp(-(t - dur) * 5))
    return _fade(y * env * vel, 0.0, 0.05)


def _saw(f: float, t: np.ndarray, phase: float = 0.0) -> np.ndarray:
    return 2 * ((f * t + phase) % 1.0) - 1


def _pad(midis, dur: float, bright: float = 1400, vel: float = 0.18) -> np.ndarray:
    t = _t(dur + 1.0)
    y = np.zeros(len(t))
    for i, m in enumerate(midis):
        for j, d in enumerate((-0.09, 0.0, 0.09)):
            y += _saw(hz(m + d), t, (i * 0.37 + j * 0.21) % 1)
    y = lowpass(y, bright)
    env = np.minimum(1, t / 0.6) * np.where(t < dur, 1.0, np.exp(-(t - dur) * 4))
    return _fade(y * env * vel / len(midis), 0.0, 0.08)


def _pluck(freq: float, dur: float = 0.6, vel: float = 0.5) -> np.ndarray:
    t = _t(dur)
    y = sum(np.sin(2 * np.pi * freq * k * t) / k * np.exp(-t * (5 + 2.4 * k)) for k in range(1, 9))
    return _fade(y * vel, 0.002, 0.05)


def _bass(freq: float, dur: float, vel: float = 0.7) -> np.ndarray:
    t = _t(dur)
    y = np.tanh(1.6 * (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t)))
    return _fade(y * (1 - np.exp(-t * 300)) * np.exp(-t * 2.0) * vel, 0.002, 0.03)


def _kick() -> np.ndarray:
    t = _t(0.4)
    f = 48 + 110 * np.exp(-t * 32)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    y[: int(0.004 * SR)] += highpass(_noise(int(0.004 * SR), 31), 3000) * 0.3
    return _fade(np.tanh(1.5 * y) * 0.9, 0.0, 0.06)


def _clap() -> np.ndarray:
    t = _t(0.25)
    n = bandpass(_noise(len(t), 32), 900, 4200)
    env = np.exp(-t * 18)
    for d in (0.0, 0.011, 0.022):
        env += np.where(t >= d, np.exp(-(t - d) * 160), 0) * 0.8
    return _fade(n * env * 0.35, 0.0, 0.03)


def _hat(open_: bool = False) -> np.ndarray:
    t = _t(0.3 if open_ else 0.06)
    return _fade(highpass(_noise(len(t), 33 + open_), 7500) * np.exp(-t * (12 if open_ else 70)) * 0.25, 0.0, 0.01)


# ---------------------------------------------------------------- 配乐

SAD_CHORDS = [(45, (69, 72, 76)), (41, (65, 69, 72)), (48, (64, 67, 72)), (43, (62, 67, 71))]   # Am F C G
UP_CHORDS = [(36, (72, 76, 79)), (31, (71, 74, 79)), (33, (72, 76, 81)), (29, (72, 77, 81))]   # C G Am F
BREAK_CHORDS = [(29, (69, 72, 77)), (31, (71, 74, 79)), (33, (69, 72, 76)), (36, (67, 72, 76))]  # F G Am C


def _section_sad(dur: float) -> np.ndarray:
    """忧伤钢琴：72 BPM，Am-F-C-G 分解和弦 + 弦乐铺底，大混响。"""
    beat = 60 / 72
    bar = beat * 4
    n = int((dur + 3) * SR)
    piano = np.zeros(n)
    padt = np.zeros(n)
    rng = np.random.default_rng(41)
    for b in range(int(math.ceil(dur / bar))):
        root, chord = SAD_CHORDS[b % 4]
        t0 = b * bar
        place(piano, _piano(hz(root), bar * 0.95, 0.42), t0)
        place(piano, _piano(hz(root + 12), bar * 0.5, 0.18), t0 + beat * 2)
        for k, idx in enumerate((0, 1, 2, 1, 0, 1, 2, 1)):
            m = chord[idx] + (12 if (k == 4 and b % 2) else 0)
            place(piano, _piano(hz(m), beat * 0.9, 0.16 + 0.05 * rng.random()), t0 + k * beat / 2)
        if b >= 1:
            place(padt, _pad([m - 12 for m in chord], bar, 900, 0.12), t0)
    return reverb(piano, 0.35, 2.6) + reverb(padt, 0.25, 2.6) * 0.8


def _section_up(dur: float, drums: str = "full", chords=UP_CHORDS) -> np.ndarray:
    """明亮流行电子：100 BPM，四拍底鼓 + 拍手 + 踩镲 + 贝斯 + 琶音 pluck + 铺底，侧链压缩律动。"""
    beat = 0.6
    bar = beat * 4
    n = int((dur + 3) * SR)
    kick, clap = np.zeros(n), np.zeros(n)
    hats, bass = np.zeros((n, 2)), np.zeros(n)
    pl, padt = np.zeros((n, 2)), np.zeros(n)
    duck = np.ones(n)
    rel = 1 - 0.6 * np.exp(-_t(beat) * 9)
    for b in range(int(math.ceil(dur / bar))):
        root, chord = chords[b % 4]
        t0 = b * bar
        place(padt, _pad([m - 12 for m in chord], bar, 1800, 0.16), t0)
        for k in range(8):
            place(bass, _bass(hz(root), beat / 2 * 0.9, 0.5), t0 + k * beat / 2)
            m = (chord + (chord[0] + 12,))[(0, 1, 2, 3, 2, 1, 2, 3)[k]]
            place(pl, pan(_pluck(hz(m), 0.5, 0.22), -0.35 if k % 2 else 0.35), t0 + k * beat / 2)
        if drums == "none":
            continue
        for k in range(4):
            if drums == "full" or k in (0, 2):
                place(kick, _kick(), t0 + k * beat)
                i = int((t0 + k * beat) * SR)
                seg = duck[i: i + len(rel)]
                duck[i: i + len(rel)] = np.minimum(seg, rel[: len(seg)])
            if drums == "full" and k in (1, 3):
                place(clap, _clap(), t0 + k * beat)
            for h in range(2):
                op = drums == "full" and k == 3 and h == 1
                place(hats, pan(_hat(op), 0.3), t0 + k * beat + h * beat / 2, 0.8 if h else 0.5)
    sc = duck[:, None]
    music = reverb(padt * duck, 0.3, 2.0) + pl * sc + reverb(pl[:, 0] + pl[:, 1], 0.4, 1.8) * 0.25
    music += pan(bass * duck, 0) * 0.7 + pan(kick, 0) + reverb(clap, 0.25, 1.2) + hats
    return music


def compose(sections: list[tuple[float, float, str]], total: float) -> np.ndarray:
    """按段落表合成整轨配乐；sections 为 (开始秒, 结束秒, 风格)，风格：sad / up / break / outro / none（静音）。"""
    out = np.zeros((int(total * SR) + SR, 2))
    for start, end, style in sections:
        dur = end - start
        if dur <= 0 or style == "none":
            continue
        if style == "sad":
            seg = _section_sad(dur)
        elif style == "up":
            seg = _section_up(dur, "full")
        elif style == "break":
            seg = _section_up(dur, "none", BREAK_CHORDS) * 0.9
        else:
            seg = _section_up(dur, "light")
        keep = min(len(seg), int((dur + 0.6) * SR))
        seg = seg[:keep].copy()
        fin = int((0.8 if style == "sad" else 0.02) * SR)
        fout = int(0.6 * SR)
        seg[:fin] *= np.linspace(0, 1, fin)[:, None]
        seg[-fout:] *= np.linspace(1, 0, fout)[:, None]
        if style == "outro":
            tail = int(min(3.0, dur) * SR)
            body_end = int(dur * SR)
            seg[body_end - tail: body_end] *= np.linspace(1, 0, tail)[:, None]
            seg[body_end:] = 0
        i = int(start * SR)
        out[i: i + len(seg)] += seg[: len(out) - i]
    out = out[: int(total * SR)]
    return out / (np.max(np.abs(out)) + 1e-9) * 0.5


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
