"""七类打击乐音效的原创合成（固定随机种子，确定性输出，48 kHz 浮点）。

每个音色首尾带包络、去直流、尾长不超过约 1.6 秒，避免跨镜头拖尾。
"""

import numpy as np
from scipy import signal

from .config import SR


def _t(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def _sos(kind, f, order=2):
    return signal.butter(order, f, kind, fs=SR, output="sos")


def _noise(n: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).standard_normal(n)


def _finish(x: np.ndarray, fade_in: float = 0.0015, fade_out: float = 0.03, peak: float = 0.9) -> np.ndarray:
    """去直流、首尾淡入淡出并归一化峰值。"""
    x = signal.sosfilt(_sos("highpass", 25), x)
    a, b = int(fade_in * SR), int(fade_out * SR)
    x[:a] *= np.linspace(0, 1, a)
    x[-b:] *= np.linspace(1, 0, b) ** 2
    return x / (np.max(np.abs(x)) + 1e-12) * peak


def kick() -> np.ndarray:
    """低音鼓：短促低频正弦下滑 + 轻微中频敲击。"""
    t = _t(0.55)
    f = 46 + 70 * np.exp(-t * 32)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    click = signal.sosfilt(_sos("bandpass", [900, 2600]), _noise(len(t), 1)) * np.exp(-t * 180) * 0.35
    knock = np.sin(2 * np.pi * 210 * t) * np.exp(-t * 40) * 0.25
    return _finish(body + click + knock, fade_out=0.08)


def rim() -> np.ndarray:
    """军鼓边击：干燥短音，带通噪声 + 高频共振。"""
    t = _t(0.18)
    tone = np.sin(2 * np.pi * 1750 * t) * np.exp(-t * 90) + 0.6 * np.sin(2 * np.pi * 520 * t) * np.exp(-t * 70)
    nz = signal.sosfilt(_sos("bandpass", [1800, 6000]), _noise(len(t), 2)) * np.exp(-t * 120) * 0.8
    x = signal.sosfilt(_sos("lowpass", 7500), tone + nz)
    return _finish(x, fade_out=0.04)


def woodblock() -> np.ndarray:
    """木块：清脆木质音，两个非谐波模态快速衰减。"""
    t = _t(0.22)
    x = (np.sin(2 * np.pi * 1180 * t) * np.exp(-t * 48)
         + 0.45 * np.sin(2 * np.pi * 2770 * t) * np.exp(-t * 85)
         + 0.2 * signal.sosfilt(_sos("bandpass", [900, 3000]), _noise(len(t), 3)) * np.exp(-t * 400))
    return _finish(x, fade_out=0.05)


def shaker() -> np.ndarray:
    """沙锤：柔和带限噪声短脉冲（两次摇动，第二下更轻）。"""
    n = int(0.32 * SR)
    t = _t(0.32)
    env = np.exp(-((t - 0.035) / 0.022) ** 2) + 0.55 * np.exp(-((t - 0.16) / 0.03) ** 2)
    x = signal.sosfilt(_sos("bandpass", [3500, 9000], 3), _noise(n, 4)) * env
    x = signal.sosfilt(_sos("lowpass", 10000), x)
    return _finish(x, fade_in=0.004, fade_out=0.06, peak=0.55)


def framedrum() -> np.ndarray:
    """框鼓：较温暖的中低频，带一点皮面噪声与轻微音高下滑。"""
    t = _t(1.0)
    f = 92 + 18 * np.exp(-t * 20)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.8)
    over = 0.3 * np.sin(2 * np.pi * np.cumsum(f * 2.3) / SR) * np.exp(-t * 9)
    skin = signal.sosfilt(_sos("bandpass", [300, 1500]), _noise(len(t), 5)) * np.exp(-t * 30) * 0.3
    x = signal.sosfilt(_sos("lowpass", 3000), body + over + skin)
    return _finish(x, fade_in=0.003, fade_out=0.25)


def tom() -> np.ndarray:
    """低音通鼓：中低频，比框鼓更紧、更有音高。"""
    t = _t(0.8)
    f = 118 + 40 * np.exp(-t * 25)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    stick = signal.sosfilt(_sos("bandpass", [600, 2400]), _noise(len(t), 6)) * np.exp(-t * 150) * 0.3
    return _finish(body + stick, fade_out=0.2)


def _bongo(freq: float, seed: int) -> np.ndarray:
    t = _t(0.35)
    f = freq * (1 + 0.08 * np.exp(-t * 60))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)
    over = 0.35 * np.sin(2 * np.pi * np.cumsum(f * 1.59) / SR) * np.exp(-t * 30)
    slap = signal.sosfilt(_sos("bandpass", [1500, 5000]), _noise(len(t), seed)) * np.exp(-t * 260) * 0.35
    return _finish(body + over + slap, fade_out=0.08)


def bongo_lo() -> np.ndarray:
    """邦戈鼓低音。"""
    return _bongo(260, 7)


def bongo_hi() -> np.ndarray:
    """邦戈鼓高音（约高一个纯五度）。"""
    return _bongo(390, 8)


def cymbal() -> np.ndarray:
    """轻柔吊镲：慢起音的金属噪声 + 非谐波部分音，高频柔化，包络平滑。"""
    dur = 1.6
    t = _t(dur)
    rng = np.random.default_rng(9)
    partials = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * rng.uniform(0.3, 1.0)
                   for f in rng.uniform(3200, 8200, 24))
    nz = signal.sosfilt(_sos("bandpass", [2500, 9000]), _noise(len(t), 10))
    att = 1 - np.exp(-t / 0.035)
    env = att * np.exp(-t * 2.4)
    x = (0.5 * partials / 24 + nz * 0.9) * env
    x = signal.sosfilt(_sos("lowpass", 7000, 2), x)
    return _finish(x, fade_in=0.01, fade_out=0.5, peak=0.5)


BANK = {
    "kick": kick, "rim": rim, "woodblock": woodblock, "shaker": shaker,
    "framedrum": framedrum, "tom": tom, "bongo_lo": bongo_lo, "bongo_hi": bongo_hi, "cymbal": cymbal,
}

# 各音色在音效轨中的基础电平（线性），整体低于音乐；关键击打略高
LEVEL = {
    "kick": 0.55, "rim": 0.32, "woodblock": 0.30, "shaker": 0.20,
    "framedrum": 0.45, "tom": 0.42, "bongo_lo": 0.30, "bongo_hi": 0.28, "cymbal": 0.24,
}


def onset_offset(name: str) -> int:
    """音色的起音样本偏移（包络越过峰值 10% 的位置），用于把起音而非文件开头对齐到画面帧。"""
    x = np.abs(BANK[name]())
    return int(np.argmax(x > 0.1 * x.max()))


def render_track(events: list[tuple[float, str, float]], total: float) -> np.ndarray:
    """按 (起音秒, 音色, 增益) 生成立体声音效轨；起音（而非文件开头）对齐到给定时刻。"""
    n = int(round(total * SR))
    out = np.zeros((n, 2))
    pans = {"bongo_lo": -0.25, "bongo_hi": 0.25, "shaker": 0.15, "woodblock": -0.1}
    for t, name, gain in events:
        clip = BANK[name]() * LEVEL[name] * gain
        p = pans.get(name, 0.0)
        st = clip[:, None] * np.array([np.sqrt((1 - p) / 2), np.sqrt((1 + p) / 2)]) * np.sqrt(2)
        a = int(round(t * SR)) - onset_offset(name)
        b = min(n, a + len(st))
        if a < 0:
            st, a = st[-a:], 0
        out[a:b] += st[: b - a]
    return out
