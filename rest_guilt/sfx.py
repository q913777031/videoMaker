"""七类打击乐音效的原创合成（48 kHz 浮点，确定性：固定随机种子）。

每个音色带起音 / 释放包络、20 Hz 高通去直流，峰值统一到 -6 dBFS，最终电平由 mix 按局部音乐电平决定。
"""

import numpy as np
from scipy import signal

SR = 48000
PEAK = 10 ** (-6 / 20)


def _t(d: float) -> np.ndarray:
    return np.arange(int(d * SR)) / SR


def _noise(n: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).standard_normal(n)


def _bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def _lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "lowpass", fs=SR, output="sos"), x)


def _hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "highpass", fs=SR, output="sos"), x)


def _sweep_sine(t, f0, f1, k):
    """频率从 f0 指数滑向 f1（时间常数 k 秒）的正弦，用于鼓皮音高下滑。"""
    f = f1 + (f0 - f1) * np.exp(-t / k)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def _finish(x: np.ndarray, attack: float = 0.002, release: float = 0.03) -> np.ndarray:
    x = _hp(x, 20)
    a, r = int(attack * SR), int(release * SR)
    if a:
        x[:a] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
    if r:
        x[-r:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    x = x - np.mean(x)
    return x / (np.max(np.abs(x)) + 1e-12) * PEAK


def low_drum() -> np.ndarray:
    t = _t(0.7)
    body = _sweep_sine(t, 120, 47, 0.045) * np.exp(-t / 0.22)
    click = _bp(_noise(len(t), 11), 900, 2600) * np.exp(-t / 0.006) * 0.35
    knock = np.sin(2 * np.pi * 310 * t) * np.exp(-t / 0.018) * 0.18
    return _finish(body + click + knock, 0.0015, 0.08)


def snare_rim() -> np.ndarray:
    t = _t(0.16)
    tone = (np.sin(2 * np.pi * 830 * t) + 0.6 * np.sin(2 * np.pi * 1710 * t + 0.5)) * np.exp(-t / 0.012)
    crack = _bp(_noise(len(t), 21), 2200, 6500) * np.exp(-t / 0.02) * 0.55
    return _finish(_lp(tone + crack, 9000), 0.0008, 0.03)


def woodblock() -> np.ndarray:
    t = _t(0.18)
    x = (np.sin(2 * np.pi * 1050 * t) * np.exp(-t / 0.035)
         + 0.45 * np.sin(2 * np.pi * 2730 * t) * np.exp(-t / 0.015)
         + 0.2 * _bp(_noise(len(t), 31), 1500, 4000) * np.exp(-t / 0.003))
    return _finish(x, 0.0008, 0.03)


def shaker(seed: int = 41) -> np.ndarray:
    t = _t(0.2)
    env = np.minimum(t / 0.018, 1) * np.exp(-np.maximum(t - 0.018, 0) / 0.05)
    env2 = np.exp(-np.maximum(t - 0.075, 0) / 0.035) * (t >= 0.075) * 0.55
    x = _lp(_bp(_noise(len(t), seed), 3500, 11000, 3), 8500) * (env + env2)
    return _finish(x, 0.004, 0.03)


def frame_drum() -> np.ndarray:
    t = _t(0.75)
    body = _sweep_sine(t, 165, 112, 0.06) * np.exp(-t / 0.28)
    mode2 = np.sin(2 * np.pi * 232 * t + 0.3) * np.exp(-t / 0.12) * 0.35
    palm = _lp(_noise(len(t), 51), 900) * np.exp(-t / 0.02) * 0.5
    return _finish(_lp(body + mode2 + palm, 4000), 0.002, 0.1)


def low_tom() -> np.ndarray:
    t = _t(0.7)
    body = _sweep_sine(t, 135, 86, 0.05) * np.exp(-t / 0.25)
    harm = _sweep_sine(t, 280, 190, 0.05) * np.exp(-t / 0.08) * 0.25
    stick = _bp(_noise(len(t), 61), 600, 1800) * np.exp(-t / 0.006) * 0.2
    return _finish(_lp(body + harm + stick, 3500), 0.0015, 0.1)


def bongo(high: bool) -> np.ndarray:
    f = 430 if high else 305
    t = _t(0.24)
    body = _sweep_sine(t, f * 1.12, f, 0.012) * np.exp(-t / (0.06 if high else 0.08))
    over = np.sin(2 * np.pi * f * 2.3 * t) * np.exp(-t / 0.02) * 0.25
    slap = _bp(_noise(len(t), 71 if high else 72), 1200, 3800) * np.exp(-t / 0.004) * 0.25
    return _finish(body + over + slap, 0.001, 0.04)


def cymbal(seed: int = 81) -> np.ndarray:
    """轻柔吊镲：非谐金属分音 + 噪声，40 ms 柔起音、约 2 秒自然衰减，8 kHz 以上柔化。"""
    t = _t(2.8)
    rng = np.random.default_rng(seed)
    parts = np.zeros(len(t))
    for f in rng.uniform(2400, 7800, 28):
        parts += np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / rng.uniform(0.6, 1.4))
    noise = _bp(_noise(len(t), seed + 1), 3000, 9000) * np.exp(-t / 0.9) * 6
    env = np.minimum(t / 0.04, 1)
    x = _lp(_hp((parts / 28 * 4 + noise * 0.15) * env, 1800), 8000, 3)
    return _finish(x, 0.04, 0.6)


def bank() -> dict[str, np.ndarray]:
    """全部音色，返回 名称 → (n, 2) 立体声数组；沙锤与吊镲左右声道用不同种子，其余居中。"""
    def mono(x):
        return np.stack([x, x], axis=1)
    return {
        "low_drum": mono(low_drum()),
        "snare_rim": mono(snare_rim()),
        "woodblock": mono(woodblock()),
        "shaker": np.stack([shaker(41), shaker(42)], axis=1),
        "frame_drum": mono(frame_drum()),
        "low_tom": mono(low_tom()),
        "bongo_hi": mono(bongo(True)),
        "bongo_lo": mono(bongo(False)),
        "cymbal": np.stack([cymbal(81), cymbal(91)], axis=1),
    }


def describe(x: np.ndarray) -> dict:
    """音色客观指标：时长、频谱质心、-20 dB 衰减时间、直流偏移，用于确认七类音色可区分。"""
    m = x.mean(axis=1)
    spec = np.abs(np.fft.rfft(m))
    f = np.fft.rfftfreq(len(m), 1 / SR)
    k = int(0.005 * SR)
    env = np.convolve(np.abs(m), np.ones(k) / k, mode="same")
    pk = int(np.argmax(env))
    below = np.nonzero(env[pk:] < env[pk] * 0.1)[0]
    return {"dur": len(m) / SR, "centroid_hz": float((spec * f).sum() / spec.sum()),
            "t20db_ms": float(below[0] / SR * 1000) if len(below) else len(m) / SR * 1000,
            "dc": float(np.mean(m)), "peak_dbfs": float(20 * np.log10(np.max(np.abs(x))))}
